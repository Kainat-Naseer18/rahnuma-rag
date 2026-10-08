"""Build citation-ready chunks from extracted pages (no model required)."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def split_body(body, limit):
    """Yield contiguous slices, preferring line, sentence, then word boundaries."""
    start = 0
    while start < len(body):
        end = min(start + limit, len(body))
        if end < len(body):
            window = body[start:end]
            # Avoid tiny chunks when the only boundary is near the start.
            for pattern in (r"\n", r"[.!?\u06d4\u061f](?:\s+|$)", r"\s+"):
                boundaries = [m.end() for m in re.finditer(pattern, window)
                              if m.end() >= limit // 2]
                if boundaries:
                    end = start + boundaries[-1]
                    break
        yield start, end, body[start:end]
        start = end


def chunk_pages(pages, max_chars=1200):
    """Keep sections separate; max_chars includes the repeated title/heading."""
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    chunks = []
    for page in pages:
        if not page.get("ok", True):
            continue
        for section_index, section in enumerate(page["sections"]):
            body = "\n".join(line.strip() for line in section["lines"] if line.strip())
            if not body:
                continue
            title, heading = page["title"], section["heading"]
            prefix = title + ("\n" + heading if heading != title else "") + "\n\n"
            budget = max_chars - len(prefix)
            if budget < 1:
                raise ValueError(f"Title/heading exceeds chunk size: {page['file']}, section {section_index}")
            for part, (start, end, content) in enumerate(split_body(body, budget)):
                chunks.append({
                    "chunk_id": f"{page['pair_id']}_{page['lang']}_s{section_index:03d}_c{part:03d}",
                    "pair_id": page["pair_id"],
                    "lang": page["lang"],
                    "title": title,
                    "heading": heading,
                    "url": page["url"],
                    "file": page["file"],
                    "accessed": page.get("accessed"),
                    "section_index": section_index,
                    "chunk_index": part,
                    "start_char": start,
                    "end_char": end,
                    "content": content,
                    "text": prefix + content,
                })
    ids = [chunk["chunk_id"] for chunk in chunks]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate chunk IDs: check page pair_id/lang values")
    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data/processed/pages.json")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/processed/chunks.jsonl")
    parser.add_argument("--max-chars", type=int, default=1200)
    args = parser.parse_args()
    pages = json.loads(args.input.read_text(encoding="utf-8"))
    chunks = chunk_pages(pages, args.max_chars)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for chunk in chunks:
            stream.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"Saved {len(chunks)} chunks to {args.output}")
    print("Chunks by language:", dict(Counter(c["lang"] for c in chunks)))
    print("Largest chunk:", max((len(c["text"]) for c in chunks), default=0), "characters")


if __name__ == "__main__":
    main()
