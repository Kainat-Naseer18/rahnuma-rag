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
- **Chosen:** TODO
- **Why these:** TODO
- **Result:** TODO (add numbers from results table)

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
