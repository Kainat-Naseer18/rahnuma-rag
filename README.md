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

- Question set: TODO questions (Urdu, English, Roman Urdu; includes unanswerable questions), written and checked by hand
- Metrics: hit@1/5/10, MRR, faithfulness (Ragas), refusal accuracy, latency, cost per query

### Results

| Experiment | hit@5 Urdu | hit@5 English | hit@5 Roman Urdu | MRR |
|---|---|---|---|---|
| Baseline (Model A) | TODO | TODO | TODO | TODO |
| Model B | TODO | TODO | TODO | TODO |
| Model C | TODO | TODO | TODO | TODO |
| + Hybrid search | TODO | TODO | TODO | TODO |
| + Reranker | TODO | TODO | TODO | TODO |

## Failure analysis

TODO: list the main failure causes with counts (spelling variants, Roman Urdu transliteration, chunk boundaries, translation mismatches, model weakness on Urdu), what you fixed, and what remains.

## Design decisions

See [`docs/decisions.md`](docs/decisions.md) for the reasoning behind each design choice (data source, chunking, embedding models, retrieval, reranking, refusal logic, and deployment).

## Cost and latency

TODO: p50/p95 latency per query, average cost per query, which LLM was used.

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
