"""End-to-end CPU smoke test: proves the whole non-GPU pipeline runs before any
real data or GPU exists. Generates synthetic COCO, converts to internal format,
prints the balance report, splits, exports YOLO labels + data.yaml, and derives
per-class thresholds from synthetic PR data.

    python run_cpu_pipeline.py

No torch, no ultralytics, no internet required.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from adapters.coco import load_coco          # noqa: E402
from prep.balance_report import build_report, print_report  # noqa: E402
from prep.split import split, _split_counts  # noqa: E402
from prep.export_yolo import export          # noqa: E402
import thresholds as th                      # noqa: E402
import taxonomy                              # noqa: E402

sys.path.insert(0, os.path.join(HERE, "tools"))
from make_fake_coco import make              # noqa: E402

WORK = os.path.join(HERE, "_cpu_run")
os.makedirs(WORK, exist_ok=True)


def load_class_map():
    import yaml
    cfg = yaml.safe_load(open(os.path.join(HERE, "configs", "base.yaml")))
    return cfg["class_map"]


def main():
    taxonomy.validate()
    print("=" * 60, "\n1. generate synthetic COCO\n" + "=" * 60)
    coco_path = os.path.join(WORK, "fake_coco.json")
    make(coco_path, n_images=120)

    print("\n" + "=" * 60, "\n2. COCO -> internal (adapter)\n" + "=" * 60)
    class_map = load_class_map()
    ds, unmapped = load_coco(coco_path, class_map)
    print(f"images: {len(ds.images)}, boxes: {sum(len(im.boxes) for im in ds.images)}")

    print("\n" + "=" * 60, "\n3. class-balance report\n" + "=" * 60)
    rep = build_report(ds)
    print_report(rep, unmapped)

    print("\n" + "=" * 60, "\n4. stratified split (rarest-first)\n" + "=" * 60)
    sp = split(ds, ratios=(0.8, 0.1, 0.1), seed=42)
    splits_names = {k: [im.file_name for im in v] for k, v in sp.items()}
    for name in ("train", "val", "test"):
        print(f"{name:<6} {len(sp[name]):>4} images  per-class: {_split_counts(sp[name])}")

    print("\n" + "=" * 60, "\n5. export YOLO labels + data.yaml\n" + "=" * 60)
    written, data_yaml = export(ds, splits_names, os.path.join(WORK, "yolo_dataset"))
    print("label files written:", written)
    print("data.yaml at:", data_yaml)
    print("--- data.yaml ---")
    print(open(data_yaml).read())

    print("=" * 60, "\n6. per-class thresholds (F-beta) on synthetic PR\n" + "=" * 60)
    import random
    rng = random.Random(0)
    scored, gt = {}, {}
    for cls in taxonomy.CLASSES:
        n = 300
        gt[cls] = n
        s = [(min(1.0, rng.gauss(0.7, 0.15)), True) for _ in range(n)]
        s += [(max(0.0, rng.gauss(0.4, 0.15)), False) for _ in range(int(n * 0.6))]
        scored[cls] = s
    detail, flat = th.compute_all(scored, gt)
    th.print_table(detail)
    th.save(flat, detail, WORK)
    print("\nthresholds.json ->", flat)
    print("\nALL CPU STAGES PASSED. GPU is required only for train/eval/infer.")


if __name__ == "__main__":
    main()
