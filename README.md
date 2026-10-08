# Rahnuma: Urdu–English RAG Assistant for Pakistani Income Tax Guidance

Ask about income tax in Urdu, English, or Roman Urdu. Get a cited answer from FBR web pages, or an honest "not found."

**Live demo:** TODO (link after deployment)
**Status:** In progress, target completion Oct 31, 2026

> **Disclaimer:** This tool gives information from FBR web pages accessed on 10/7/2026 - date. It is not tax advice. Check FBR or a qualified tax professional for your situation.

## Why this project

Most RAG demos work only in English. Many Pakistani taxpayers search in Urdu or Roman Urdu, while official guidance is often written in formal English or in rough Urdu translation. This project tests how well retrieval works across those languages, and whether the assistant stays honest when the answer isn't in the sources.

## What it does

- Answers questions in Urdu, English, and Roman Urdu
- Shows the source passage and page link for every answer
- Refuses to answer when the sources don't contain the answer
- Covers concepts and procedures (definitions, registration, filing, deadlines, refunds, appeals)
- Does **not** answer questions that depend on current tax rates or amounts

## Architecture

TODO: add a diagram (draw.io or Excalidraw export).

Pipeline: scrape FBR pages → clean and normalize → chunk by section → embed + BM25 index → hybrid retrieval → rerank → grounded answer with citations → refusal check → Gradio UI.

## Data

- Source: official FBR English and Urdu income tax pages (list in `data/pages.csv`)
- Pages: TODO pairs, TODO chunks (English: TODO, Urdu: TODO)
- Accessed: TODO date
- Known issues: some pages cite the Companies Ordinance 1984 (since replaced) and use older tax-year examples. The Urdu and English versions are not always perfectly aligned. Answers should be treated as based on the page text, not as current law.

## Evaluation

- Question set: 20 drafts in `eval/questions_draft.md`: 16 answerable and 4 unanswerable, across English, Urdu, and Roman Urdu.
- Baseline evaluation: saved `intfloat/multilingual-e5-small` vectors, NumPy dot-product search over all 131 chunks, no answer generation. Corpus checksums and row alignment are verified before reuse. Questions use the same pinned revision, `query: ` prefix, normalization, and token-limit checks.

From the repository root in PowerShell, run:

```powershell
.\venv\Scripts\python.exe .\src\evaluate.py --repeats 3
```

Results are under `eval/results/multilingual-e5-small/`: answerable and
unanswerable top-10 retrieval outputs (IDs, scores, URLs), `summary.json`,
`summary.md`, and manual-labeling candidates/template. No model download is
needed with the existing pinned local cache.

### Results

| Question language | Answerable questions | Hit@1 | Hit@5 | Hit@10 | MRR@10 |
| --- | --- | --- | --- | --- | --- |
| Overall | 16 | N/A | N/A | N/A | N/A |
| English | 6 | N/A | N/A | N/A | N/A |
| Urdu | 5 | N/A | N/A | N/A | N/A |
| Roman Urdu | 5 | N/A | N/A | N/A | N/A |

No finalized relevance labels exist for Q01–Q16; source-section references are
review candidates, not accepted chunk IDs. Metrics are unavailable until manual
labeling. Review `manual_labeling_needed.jsonl`, including equivalent evidence in
both corpus languages. Copy `relevance_labels_template.json` from the results
folder to `eval/relevance_labels.json`, enter reviewed relevant chunk IDs, set
`reviewed` to true, and rerun evaluation. Labels must match the corpus/question
checksums. Q06 needs both password and PIN evidence; Hit/MRR measure any relevant
hit rather than complete evidence coverage. Unanswerable questions never enter
these metrics.

## Failure analysis

TODO: list the main failure causes with counts (spelling variants, Roman Urdu transliteration, chunk boundaries, translation mismatches, model weakness on Urdu), what you fixed, and what remains.

## Design decisions

See [`docs/decisions.md`](docs/decisions.md) for the reasoning behind each design choice (data source, chunking, embedding models, retrieval, reranking, refusal logic, and deployment).

## Cost and latency

Measured E5 baseline CPU query encoding plus full NumPy search: p50 **44.53 ms**,
p95 **69.41 ms**, mean **47.63 ms** across 60 samples (20 questions × 3 passes,
batch size 1, after 3 warm-up queries). Model loading and output serialization
are excluded. These are local measurements, not a service latency guarantee.
Per-language timings and environment details are saved in the evaluation summary.
No answer generation or API cost was evaluated.

## Tech stack

Python, requests + BeautifulSoup, sentence-transformers, TODO embedding models, Qdrant, rank-bm25, TODO reranker, Ragas, FastAPI, Gradio, Docker

## Run locally

    git clone https://github.com/YOUR-USERNAME/rahnuma-rag.git
    cd rahnuma-rag
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env     # add your API key
    python src/download.py
    python src/extract.py
    python src/chunk.py
    TODO: commands to build the index and start the app

## Repository structure

Create multilingual embeddings with `python src/embed.py` after chunking.
The first run downloads `intfloat/multilingual-e5-small` into `.cache/models`.
Outputs in `data/embeddings/multilingual-e5-small/` are `vectors.npy` (normalized
float32 vectors), an aligned copy of `chunks.jsonl`, and `manifest.json` with
model revision, dimensions, token limits, and input checksum. Both downloaded
models and generated embeddings are ignored by Git.

For retrieval, load the same model/revision and encode questions using
`encode_texts(model, questions, "query")` from `src/embed.py`. Rank normalized
passage vectors by their dot product with the normalized query vector. Use the
matching metadata row for citations. English and Urdu share the vector space;
Roman Urdu retrieval quality still needs evaluation. The script rejects inputs
above the model's token limit instead of silently truncating them.

Chunk extracted pages with `python src/chunk.py`. This writes UTF-8
`data/processed/chunks.jsonl`, one JSON object per chunk. Use `text` for embeddings
and keyword search, and `content` for the source passage. Each record includes
`chunk_id`, language, page title, section heading, source URL, access date, and
character offsets within its section. Sections stay separate and split at up to
1,200 characters including the title and heading. To change the limit, run
`python src/chunk.py --max-chars 1600`.

Run chunking checks with `python -m unittest discover -s src -p test_chunk.py`.

    data/        page list, download log, processed chunks
    src/         download, extract, chunk, retrieval, generation, app
    eval/        question set and results
    notebooks/   failure analysis
    docs/        design decisions

## Limitations

- Based on a small set of FBR pages, not the full tax law
- Content may be outdated or inconsistent between languages
- Not tested on questions about rates, amounts, or individual circumstances
- Roman Urdu has no standard spelling, so retrieval varies

## Future work

Graph RAG over tax concepts, agentic retrieval for multi-step questions, fine-tuned embeddings on Urdu tax text, more document sources.

## Data and licensing

Source pages belong to the Federal Board of Revenue, Government of Pakistan. See FBR's Terms of Use. This project is for educational and portfolio purposes.
