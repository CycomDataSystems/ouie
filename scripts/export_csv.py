import csv
import json
import sys
from pathlib import Path

in_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not in_path or not in_path.exists():
    raise SystemExit(
        "Usage: python scripts/export_csv.py results/<model>.jsonl")

out_path = in_path.with_suffix(".csv")

with in_path.open("r", encoding="utf-8") as f, out_path.open("w", newline="", encoding="utf-8") as out:
    w = csv.DictWriter(
        out, fieldnames=["id", "bucket", "prompt", "response", "label", "notes"])
    w.writeheader()
    for line in f:
        if not line.strip():
            continue
        rec = json.loads(line)
        w.writerow({
            "id": rec.get("id"),
            "bucket": rec.get("bucket"),
            "prompt": rec.get("prompt"),
            "response": rec.get("response", ""),
            "label": "",
            "notes": "",
        })

print(f"Wrote: {out_path}")
