"""Create normalized multilingual E5 embeddings and aligned citation metadata."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL = "intfloat/multilingual-e5-small"
REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"


def encode_texts(model, texts, kind, batch_size=16, show_progress=True):
    if kind not in ("query", "passage"):
        raise ValueError("kind must be query or passage")
    inputs = [f"{kind}: {text}" for text in texts]
    lengths = [len(ids) for ids in model.tokenizer(inputs, truncation=False)["input_ids"]]
    oversized = [i for i, length in enumerate(lengths) if length > model.max_seq_length]
    if oversized:
        raise ValueError(f"Inputs {oversized} exceed {model.max_seq_length} tokens; "
                         "re-run chunk.py with a smaller --max-chars. No text was silently truncated.")
    vectors = model.encode(inputs, batch_size=batch_size, normalize_embeddings=True,
                           convert_to_numpy=True, show_progress_bar=show_progress)
    vectors = np.asarray(vectors, dtype=np.float32)
    if not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5):
        raise ValueError("Embeddings must be finite unit vectors")
    return vectors, lengths


def main():
    from sentence_transformers import SentenceTransformer

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/processed/chunks.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "data/embeddings/multilingual-e5-small")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--check-query", action="append", default=[],
                        help="Optional retrieval smoke test; may be repeated")
    args = parser.parse_args()
    raw = args.input.read_bytes()
    chunks = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if not chunks or len({c['chunk_id'] for c in chunks}) != len(chunks):
        raise ValueError("Input must contain chunks with unique IDs")
    model = SentenceTransformer(MODEL, revision=REVISION, device=args.device,
                                cache_folder=str(ROOT / ".cache/models"))
    vectors, lengths = encode_texts(model, [c['text'] for c in chunks], "passage", args.batch_size)
    args.output.mkdir(parents=True, exist_ok=True)
    np.save(args.output / "vectors.npy", vectors, allow_pickle=False)
    (args.output / "chunks.jsonl").write_bytes(raw)
    manifest = dict(model=MODEL, revision=REVISION,
                    dimension=int(vectors.shape[1]), count=len(chunks), normalized=True,
                    passage_prefix="passage: ", query_prefix="query: ",
                    max_sequence_length=model.max_seq_length, largest_input_tokens=max(lengths),
                    input_sha256=hashlib.sha256(raw).hexdigest(),
                    row_mapping="vectors.npy row i corresponds to chunks.jsonl record i")
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved {vectors.shape} embeddings to {args.output}")
    if args.check_query:
        queries, _ = encode_texts(model, args.check_query, "query", args.batch_size)
        for query, vector in zip(args.check_query, queries):
            top = np.argsort(-(vectors @ vector))[:3]
            print(json.dumps({"query": query, "top_chunks": [chunks[i]['chunk_id'] for i in top]}))


if __name__ == "__main__":
    main()
