"""One command to turn ANY dataset into a training-ready YOLO dataset.

    python src/ingest.py --input PATH [--images DIR] [--out yolo_dataset] [--limit N]

PATH may be a CubiCasa5k dir, a COCO json, a YOLO dir, or a VOC dir -- the
format is auto-detected. Steps: detect -> adapt -> resolution report ->
balance report -> stratified split -> YOLO export (copying images).

This is the front door for the real dataset when it arrives from Data &
Annotation: no code change, just point --input at it.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from adapters.auto import detect_format, load_any            # noqa: E402
import classmap                                              # noqa: E402
from prep.balance_report import build_report, print_report   # noqa: E402
from prep.split import split, _split_counts                  # noqa: E402
from prep.export_yolo import export                          # noqa: E402


def _source_names(ds):
    """Distinct raw category labels seen, taken from box.subtype."""
    return {b.subtype for im in ds.images for b in im.boxes if b.subtype}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CubiCasa dir / COCO json / YOLO dir / VOC dir")
    ap.add_argument("--config", default=os.path.join(os.path.dirname(HERE), "configs", "base.yaml"))
    ap.add_argument("--images", default=None, help="flat image dir (COCO-style datasets)")
    ap.add_argument("--out", default="yolo_dataset")
    ap.add_argument("--limit", type=int, default=None, help="cap source files (subset runs)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--no-images", action="store_true", help="labels only, skip image copy")
    args = ap.parse_args()

    import yaml
    cfg = yaml.safe_load(open(args.config))
    class_map = cfg.get("class_map")
    ratios = tuple(cfg["split"]["ratios"])
    seed = args.seed if args.seed is not None else cfg["seed"]

    fmt, target = detect_format(args.input)
    print(f"detected format: {fmt}  ({target})")
    if args.limit:
        print(f"limit: first {args.limit} source files")

    fmt, ds, unmapped = load_any(args.input, class_map, limit=args.limit)
    n_boxes = sum(len(i.boxes) for i in ds.images)
    print(f"loaded {len(ds.images)} images, {n_boxes} boxes\n")
    if n_boxes == 0:
        print("!! ZERO boxes parsed. Stopping -- check the adapter before continuing.")
        sys.exit(1)

    print("--- category resolution (confirm keyword guesses) ---")
    classmap.print_resolution_report(
        classmap.build_resolution_report(_source_names(ds), class_map))

    print("\n--- class balance ---")
    print_report(build_report(ds), unmapped)

    print("\n--- split ---")
    sp = split(ds, ratios=ratios, seed=seed)
    splits = {k: [im.file_name for im in v] for k, v in sp.items()}
    for name in ("train", "val", "test"):
        print(f"{name:<6} {len(sp[name]):>5} imgs  {_split_counts(sp[name])}")

    print("\n--- export ---")
    written, data_yaml = export(ds, splits, args.out, args.images,
                                copy_images=not args.no_images)
    print("label files:", written)
    print("data.yaml:", data_yaml)
    print(f"\nReady. Train with:\n  python src/train.py --config {args.config} --data {data_yaml}")


if __name__ == "__main__":
    main()
