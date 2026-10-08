"""Evaluate only the saved multilingual-e5-small baseline using NumPy search."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import re
import time

import numpy as np

from embed import MODEL, REVISION, ROOT, encode_texts


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def read_questions(path):
    questions = []
    answerable = True
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('## Refusal'):
            answerable = False
        if re.match(r'^\| Q\d+ \|', line):
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if len(cells) != 5:
                raise ValueError('Expected five question table columns')
            qid, language, question, expected, source = cells
            questions.append(dict(question_id=qid, language=language, question=question,
                                  answerable=answerable, expected=expected, source_target=source))
    if not questions or len({q['question_id'] for q in questions}) != len(questions):
        raise ValueError('Missing or duplicate questions')
    return questions


def load_artifacts(folder, corpus):
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    raw = (folder / 'chunks.jsonl').read_bytes()
    if raw != corpus.read_bytes() or sha256(raw) != manifest['input_sha256']:
        raise ValueError('Corpus checksum mismatch; regenerate embeddings with src/embed.py')
    if (manifest['model'], manifest['revision']) != (MODEL, REVISION):
        raise ValueError('Expected the existing pinned multilingual-e5-small baseline')
    if not manifest['normalized'] or manifest['query_prefix'] != 'query: ' or manifest['passage_prefix'] != 'passage: ':
        raise ValueError('Invalid embedding normalization/prefix metadata')
    chunks = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    vectors = np.load(folder / 'vectors.npy', allow_pickle=False)
    if vectors.shape != (len(chunks), manifest['dimension']) or len(chunks) != manifest['count']:
        raise ValueError('Vector/metadata shape mismatch')
    if len(chunks) < 10 or len({c['chunk_id'] for c in chunks}) != len(chunks):
        raise ValueError('Need at least 10 unique chunks')
    if not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5):
        raise ValueError('Saved vectors must be finite and normalized')
    return manifest, chunks, vectors


def validate_labels(path, questions, chunks, corpus_hash, question_hash):
    """Accept only explicitly reviewed labels tied to these exact inputs."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if data['corpus_sha256'] != corpus_hash or data['questions_sha256'] != question_hash:
        raise ValueError('Relevance labels refer to different corpus/questions')
    question_map = {q['question_id']: q for q in questions}
    chunk_ids = {c['chunk_id'] for c in chunks}
    labels = {}
    for qid, entry in data['labels'].items():
        if qid not in question_map or not question_map[qid]['answerable']:
            raise ValueError(f'Invalid answerable question label: {qid}')
        if entry.get('reviewed') is not True:
            continue
        ids = entry.get('relevant_chunk_ids', [])
        if not ids or len(ids) != len(set(ids)) or not set(ids) <= chunk_ids:
            raise ValueError(f'Missing/unknown/duplicate relevant chunk IDs for {qid}')
        labels[qid] = set(ids)
    return labels


def metrics(records):
    if not records:
        return dict(count=0, hit_at_1=None, hit_at_5=None, hit_at_10=None, mrr_at_10=None)
    ranks = [r['first_relevant_rank'] for r in records]
    return dict(count=len(records), **{
        f'hit_at_{k}': sum(rank is not None and rank <= k for rank in ranks) / len(ranks)
        for k in (1, 5, 10)},
        mrr_at_10=sum(1 / rank if rank is not None else 0 for rank in ranks) / len(ranks))


def latency_stats(samples):
    return dict(samples=len(samples), mean_ms=float(np.mean(samples)),
                p50_ms=float(np.percentile(samples, 50)), p95_ms=float(np.percentile(samples, 95)))


def main():
    from sentence_transformers import SentenceTransformer
    import sentence_transformers
    import torch

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--embeddings', type=Path, default=ROOT / 'data/embeddings/multilingual-e5-small')
    parser.add_argument('--corpus', type=Path, default=ROOT / 'data/processed/chunks.jsonl')
    parser.add_argument('--questions', type=Path, default=ROOT / 'eval/questions_draft.md')
    parser.add_argument('--labels', type=Path, default=ROOT / 'eval/relevance_labels.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'eval/results/multilingual-e5-small')
    parser.add_argument('--repeats', type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be positive')
    manifest, chunks, vectors = load_artifacts(args.embeddings, args.corpus)
    questions = read_questions(args.questions)
    question_hash = sha256(args.questions.read_bytes())
    labels = validate_labels(args.labels, questions, chunks, manifest['input_sha256'], question_hash)
    # The exact pinned snapshot is already cached: do not download or load another model.
    snapshot = ROOT / '.cache/models/models--intfloat--multilingual-e5-small/snapshots' / manifest['revision']
    model = SentenceTransformer(str(snapshot), device='cpu', local_files_only=True)
    if model.max_seq_length != manifest['max_sequence_length']:
        raise ValueError('Model token limit differs from manifest')
    passage_lengths = [len(ids) for ids in model.tokenizer(
        ['passage: ' + c['text'] for c in chunks], truncation=False)['input_ids']]
    query_lengths = [len(ids) for ids in model.tokenizer(
        ['query: ' + q['question'] for q in questions], truncation=False)['input_ids']]
    if max(passage_lengths + query_lengths) > model.max_seq_length:
        raise ValueError('Corpus or questions exceed token limit')
    # Warm three single-query encode+search calls; no model-loading time is measured.
    for q in questions[:3]:
        v, _ = encode_texts(model, [q['question']], 'query', show_progress=False)
        np.argsort(-(vectors @ v[0]), kind='stable')[:10]
    outputs = {}
    times = {q['question_id']: [] for q in questions}
    # Repeat full passes to avoid timing consecutive copies of only one question.
    for _ in range(args.repeats):
        for q in questions:
            started = time.perf_counter()
            query_vectors, _ = encode_texts(model, [q['question']], 'query', show_progress=False)
            scores = vectors @ query_vectors[0]
            top = np.argsort(-scores, kind='stable')[:10]
            elapsed = (time.perf_counter() - started) * 1000
            times[q['question_id']].append(elapsed)
            outputs[q['question_id']] = [dict(rank=rank, chunk_id=chunks[i]['chunk_id'],
                                                  score=float(scores[i]), url=chunks[i]['url'])
                                               for rank, i in enumerate(top, 1)]
    records, manual = [], []
    for q, tokens in zip(questions, query_lengths):
        qid = q['question_id']
        hits = outputs[qid]
        relevant = labels.get(qid)
        first_rank = next((h['rank'] for h in hits if h['chunk_id'] in relevant), None) if relevant else None
        records.append(dict(**q, query_tokens=tokens, top_10=hits,
                            label_status='validated' if relevant else ('missing' if q['answerable'] else 'excluded'),
                            relevant_chunk_ids=sorted(relevant) if relevant else None,
                            first_relevant_rank=first_rank, latency_ms=times[qid]))
        if q['answerable'] and not relevant:
            # Source references are candidates only, never inferred relevance labels.
            refs = re.findall(r'`([^`]+)`;\s*([^;]+)', q['source_target'])
            candidates = [c for c in chunks if any(c['file'] == f and c['heading'] == h.strip() for f, h in refs)]
            manual.append(dict(question_id=qid, language=q['language'], question=q['question'],
                               expected=q['expected'], source_target=q['source_target'],
                               source_reference_candidates=[dict(chunk_id=c['chunk_id'], url=c['url'],
                                                                 heading=c['heading'], content=c['content']) for c in candidates]))
    answerable = [r for r in records if r['answerable']]
    complete = all(r['label_status'] == 'validated' for r in answerable)
    scored = [r for r in answerable if r['label_status'] == 'validated']
    summary = dict(model=MODEL, revision=manifest['revision'], embeddings_reused=True,
                   corpus_sha256=manifest['input_sha256'], questions_sha256=question_hash,
                   vectors_sha256=sha256((args.embeddings / 'vectors.npy').read_bytes()),
                   labels_sha256=sha256(args.labels.read_bytes()) if args.labels.exists() else None,
                   chunk_count=len(chunks), question_counts=dict(Counter(r['language'] for r in records)),
                   answerable_count=len(answerable), unanswerable_count=len(records)-len(answerable),
                   validated_label_count=len(scored), missing_label_ids=[r['question_id'] for r in manual],
                   metric_status='complete' if complete else 'unavailable: manual relevance labels missing',
                   overall=metrics(answerable) if complete else metrics([]),
                   by_language={lang: metrics([r for r in answerable if r['language'] == lang])
                                if complete else metrics([]) for lang in sorted({r['language'] for r in answerable})},
                   labeled_subset_only=dict(overall=metrics(scored), by_language={
                       lang: metrics([r for r in scored if r['language'] == lang])
                       for lang in sorted({r['language'] for r in answerable})}),
                   metric_definition='Hit@k: any labeled relevant chunk in top k; MRR@10: reciprocal first relevant rank, else zero. Unanswerable excluded. Q06 requires both source topics for full evidence coverage; Hit/MRR measure any hit only.',
                   token_checks=dict(limit=model.max_seq_length, max_passage_tokens=max(passage_lengths), max_query_tokens=max(query_lengths)),
                   latency=dict(device='cpu', warmup_queries=3, repeats=args.repeats, batch_size=1,
                                scope='query prefix, tokenization/limit validation, normalized encoding, vector validation, full NumPy dot product and top-10 sort; excludes model loading, passage checks, serialization',
                                all_questions=latency_stats([t for r in records for t in r['latency_ms']]),
                                by_language={lang: latency_stats([t for r in records if r['language'] == lang for t in r['latency_ms']])
                                             for lang in sorted({r['language'] for r in records})}),
                   environment=dict(python=platform.python_version(), platform=platform.platform(),
                                    numpy=np.__version__, sentence_transformers=sentence_transformers.__version__,
                                    torch=torch.__version__, torch_threads=torch.get_num_threads()))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, items in [('answerable_retrieval.jsonl', answerable),
                        ('unanswerable_retrieval.jsonl', [r for r in records if not r['answerable']]),
                        ('manual_labeling_needed.jsonl', manual)]:
        (args.output / name).write_text(''.join(json.dumps(item, ensure_ascii=False) + '\n' for item in items), encoding='utf-8')
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    template = dict(corpus_sha256=manifest['input_sha256'], questions_sha256=question_hash,
                    labels={q['question_id']: dict(reviewed=False, relevant_chunk_ids=[])
                            for q in questions if q['answerable']})
    (args.output / 'relevance_labels_template.json').write_text(json.dumps(template, indent=2), encoding='utf-8')
    report = [f'# {MODEL} evaluation', '',
              f"Reused {len(chunks)} saved vectors; {len(answerable)} answerable and {len(records)-len(answerable)} unanswerable questions.",
              f"Relevance labels validated: {len(scored)}/{len(answerable)}. Status: {summary['metric_status']}.", '',
              '| Question language | Answerable questions | Hit@1 | Hit@5 | Hit@10 | MRR@10 |',
              '| --- | --- | --- | --- | --- | --- |']
    for lang in ['Overall'] + sorted(summary['by_language']):
        group = answerable if lang == 'Overall' else [r for r in answerable if r['language'] == lang]
        m = summary['overall'] if lang == 'Overall' else summary['by_language'][lang]
        values = ['N/A' if m[key] is None else f'{m[key]:.4f}' for key in ['hit_at_1', 'hit_at_5', 'hit_at_10', 'mrr_at_10']]
        report.append(f"| {lang} | {len(group)} | " + ' | '.join(values) + ' |')
    latency = summary['latency']['all_questions']
    report.extend(['', f"Warmed CPU query encoding plus NumPy search: p50 {latency['p50_ms']:.2f} ms; p95 {latency['p95_ms']:.2f} ms ({latency['samples']} samples). Model loading excluded.",
                   '', 'Unanswerable retrieval is saved separately and excluded from relevance metrics.', '',
                   'For missing labels, review `manual_labeling_needed.jsonl` against the corpus. Source-reference candidates are not accepted labels. Review other chunks, including the other language, for equivalent evidence. For Q06 review both password and PIN passages.',
                   'Copy `relevance_labels_template.json` to `eval/relevance_labels.json`, enter relevant chunk IDs, and set `reviewed` to true only after manual review. Re-run the same evaluation command. Do not label by retrieval rank.',
                   '', 'Hit@k and MRR@10 count the first hit among any relevant chunk; they do not measure complete multi-passage evidence coverage.'])
    (args.output / 'summary.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
