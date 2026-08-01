"""Class-balance + data-quality report over a schema.Dataset.

Reports per-class instance counts and share, and fires warnings for:
  - sparse classes (< MIN_INSTANCES) -> poor mAP expected
  - tiny objects (median box area below TINY_AREA_FRAC) -> raise imgsz

Pure stdlib. Runs on CPU.
"""

import json
import os
import sys
from collections import Counter
from statistics import median

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Dataset  # noqa: E402
import taxonomy  # noqa: E402

MIN_INSTANCES = 200       # below this, expect unstable / poor per-class mAP
TINY_AREA_FRAC = 0.005    # median box area (fraction of image) below this = tiny


def build_report(ds: Dataset):
    counts = Counter()
    areas = {c: [] for c in taxonomy.CLASSES}
    for im in ds.images:
        for b in im.boxes:
            counts[b.cls] += 1
            areas[b.cls].append(b.area())

    total = sum(counts.values()) or 1
    rows = []
    warnings = []
    for c in taxonomy.CLASSES:
        n = counts[c]
        share = 100.0 * n / total
        med_area = median(areas[c]) if areas[c] else 0.0
        row = {"cls": c, "count": n, "share_pct": round(share, 1),
               "median_area_pct": round(100.0 * med_area, 3)}
        rows.append(row)
        if 0 < n < MIN_INSTANCES:
            warnings.append(f"{c}: only {n} instances (<{MIN_INSTANCES}) -- poor mAP expected")
        if n == 0:
            warnings.append(f"{c}: ZERO instances -- class present in taxonomy but absent from data")
        if areas[c] and med_area < TINY_AREA_FRAC:
            warnings.append(f"{c}: median object area {100*med_area:.3f}% of image -- tiny; use imgsz>=1024")

    return {"rows": rows, "total": total, "warnings": warnings}


def print_report(report, unmapped=None):
    print(f"{'class':<10}{'count':>7}{'share':>8}{'med_area':>10}")
    for r in report["rows"]:
        flag = ""
        if r["count"] and r["count"] < MIN_INSTANCES:
            flag = "  <- sparse"
        elif r["median_area_pct"] and r["median_area_pct"] < 100 * TINY_AREA_FRAC:
            flag = "  <- tiny objects, raise imgsz"
        print(f"{r['cls']:<10}{r['count']:>7}{r['share_pct']:>7}%{r['median_area_pct']:>9}%{flag}")
    if unmapped:
        um = ", ".join(f"{k} ({v})" for k, v in unmapped.items())
        print(f"unmapped: {um}  <- reported, not silently dropped")
    if report["warnings"]:
        print("\nwarnings:")
        for w in report["warnings"]:
            print("  ! " + w)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("internal_json")
    p.add_argument("--out", default=None, help="optional JSON output path")
    args = p.parse_args()
    ds = Dataset.from_dict(json.load(open(args.internal_json)))
    rep = build_report(ds)
    print_report(rep)
    if args.out:
        json.dump(rep, open(args.out, "w"), indent=2)
