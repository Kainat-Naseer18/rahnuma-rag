# Design Decisions

A log of the choices made in this project and why. Newest entries at the bottom.
Each entry: what I chose, what else I considered, why, and how I'll know if it was right.

## 1. Data source: FBR web pages instead of PDFs
- **Chosen:** FBR English and Urdu income tax web pages
- **Considered:** SECP Section 42 guide (PDF), other PDFs
- **Why:** Web pages give clean Unicode Urdu with no OCR, and the pages exist in both languages.
- **Trade-offs:** Small corpus, some outdated content, translation quality varies.
- **Revisit if:** TODO

## 2. Chunking strategy
- **Chosen:** One chunk per page section, split at 1,200 characters if longer, including the prepended page title and heading in that limit. Prefer line, sentence, then word boundaries. No overlap; chunks never cross sections.
- **Considered:** Fixed-size chunks
- **Why:** Sections match how questions are asked, and headings add context.
- **Result:** 131 chunks from 68 pages (66 English, 65 Urdu); largest chunk is 1,191 characters. Counts can change when sources are re-extracted. Character limits are not tokenizer limits; check the chosen embedding model's token limit before indexing.

## 3. Embedding models compared
- **Chosen:** `intfloat/multilingual-e5-small` as the first baseline; no comparison completed yet.
- **Why these:** Multilingual retrieval model with 384-dimensional embeddings, suitable as a local CPU baseline. Follow the model card's `passage: ` and `query: ` prefixes, including for non-English text: https://huggingface.co/intfloat/multilingual-e5-small
- **Implementation:** Normalize vectors for cosine/dot-product retrieval; keep citation metadata aligned by row and record the model revision and input checksum. Check token limits before encoding.
- **Result:** Generated 131 normalized float32 vectors, each with 384 dimensions. Largest input is 331 tokens (limit 512), so no chunks were truncated. Password-reset smoke queries in English, Urdu, and Roman Urdu each retrieved page 10 first. Full retrieval evaluation remains pending.
- **Baseline evaluation (2026-10-09):** Reused saved vectors after verifying corpus checksum, shape, normalization, unique chunk IDs, and aligned metadata. Encoded 20 questions with the same pinned revision and `query: ` prefix; largest question is 37 tokens (512-token limit). Searched all 131 chunks by NumPy dot product. Saved top-10 IDs, scores, and source URLs for 16 answerable questions and separately for 4 unanswerable questions under `eval/results/multilingual-e5-small/`.
- **Label audit:** Q01–Q16 have source-section references but no finalized relevance labels. Hit@1/5/10 and MRR@10 are unavailable overall and by language until manual chunk-level labeling; no labels were inferred from reference sections or retrieval rankings. Candidate source passages and a checksum-bound label template are saved for review. Q06 requires reviewing both password and PIN evidence; any-hit metrics do not measure full evidence coverage.
- **Measured latency:** Warmed CPU encoding plus full search/sort, batch size 1, 3 warm-up queries, 3 passes over 20 questions (60 samples): p50 44.53 ms, p95 69.41 ms, mean 47.63 ms. Excludes model loading and serialization. Run `.\venv\Scripts\python.exe .\src\evaluate.py --repeats 3` from the project root to reproduce the procedure; timings will vary.

## 4. Vector store
- **Chosen:** TODO (Qdrant or pgvector)
- **Why:** TODO

## 5. Hybrid search and fusion
- **Chosen:** TODO
- **Result:** TODO (change in hit@5)

## 6. Reranker
- **Chosen:** TODO
- **Result:** TODO (change in hit@5, added latency)

## 7. Refusal logic
- **Chosen:** TODO (score threshold, LLM check)
- **Result:** TODO (refusal precision and recall)

## 8. LLM for answer generation
- **Chosen:** TODO
- **Why:** TODO (Urdu quality, cost, latency)

## 9. Deployment
- **Chosen:** TODO
- **Why:** TODO
