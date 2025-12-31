import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not path or not path.exists():
    raise SystemExit(
        "Usage: python scripts/score_csv.py labels/labeled_<model>.csv")

counts = Counter()
by_bucket = defaultdict(Counter)
total = 0

with path.open("r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        label = (row.get("label") or "").strip()
        bucket = (row.get("bucket") or "").strip()
        if not label:
            continue
        total += 1
        counts[label] += 1
        by_bucket[bucket][label] += 1


def pct(n):
    return 0.0 if total == 0 else (100.0 * n / total)


print(f"File: {path}")
print(f"Labeled rows: {total}\n")

print("Overall:")
for k, v in counts.most_common():
    print(f"  {k:14} {v:4}  ({pct(v):5.1f}%)")

print("\nBy bucket:")
for bucket, c in by_bucket.items():
    bucket_total = sum(c.values())
    if bucket_total == 0:
        continue
    print(f"  {bucket} (n={bucket_total})")
    for k, v in c.most_common():
        print(f"    {k:12} {v:4}  ({100.0*v/bucket_total:5.1f}%)")
