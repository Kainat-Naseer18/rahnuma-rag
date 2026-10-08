import csv, time, json
from pathlib import Path
from datetime import date
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (student research project: rahnuma-rag)"}
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(open("data/pages.csv", encoding="utf-8-sig")))
log = []

for r in rows:
    name = f"{r['pair_id']}_{r['lang']}.html"
    try:
        resp = requests.get(r["url"], headers=HEADERS, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        (RAW / name).write_text(resp.text, encoding="utf-8")
        log.append({**r, "file": name, "accessed": str(date.today()), "ok": True})
        print("saved", name, len(resp.text))
    except Exception as e:
        log.append({**r, "file": name, "ok": False, "error": str(e)})
        print("FAILED", name, e)
    time.sleep(1.5)

json.dump(log, open("data/download_log.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("done:", sum(1 for x in log if x["ok"]), "ok,", sum(1 for x in log if not x["ok"]), "failed")