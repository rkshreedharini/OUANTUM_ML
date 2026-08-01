"""Internal schema + splits -> Ultralytics YOLO directory layout.

Produces:
  <out>/images/{train,val,test}/<uid>.png
  <out>/labels/{train,val,test}/<uid>.txt   (YOLO: `cls cx cy w h`)
  <out>/data.yaml                            (Ultralytics dataset config)

UNIQUE FILE IDS -- this is why `_uid()` exists. In CubiCasa5k every plan's
image is literally named `F1_scaled.png`; the folder is the only thing that
distinguishes them:

    cubicasa_raw/cubicasa5k/high_quality/13671/F1_scaled.png
    cubicasa_raw/cubicasa5k/high_quality/3588/F1_scaled.png

Naming labels after the image basename would collapse all 5,000 plans onto one
file called `F1_scaled.txt`, each overwriting the last, and you'd train on a
dataset of one image while everything reported success. So the uid is derived
from the whole relative path, not the basename. Verified on real data.

Image copying uses the dataset's own recorded path when it exists (adapters
that store a real path, e.g. CubiCasa), and falls back to
`images_src_dir/basename` for flat datasets (e.g. COCO).
"""

import json
import os
import re
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Dataset  # noqa: E402
import taxonomy  # noqa: E402

_SAFE = re.compile(r"[^A-Za-z0-9]+")


def _uid(file_name, seen=None):
    """Stable, unique, filesystem-safe id from a full relative path."""
    stem, _ext = os.path.splitext(file_name)
    uid = _SAFE.sub("_", stem).strip("_")
    # keep it a sane length while staying unique
    if len(uid) > 120:
        uid = uid[:60] + "_" + uid[-55:]
    if seen is not None:
        base, n = uid, 1
        while uid in seen:
            n += 1
            uid = f"{base}_{n}"
        seen.add(uid)
    return uid


def export(ds: Dataset, splits, out_dir, images_src_dir=None, copy_images=False):
    by_name = {im.file_name: im for im in ds.images}
    for sub in ("train", "val", "test"):
        os.makedirs(os.path.join(out_dir, "labels", sub), exist_ok=True)
        os.makedirs(os.path.join(out_dir, "images", sub), exist_ok=True)

    written = {"train": 0, "val": 0, "test": 0}
    copied = {"train": 0, "val": 0, "test": 0}
    missing_images = []
    seen = set()

    for sub in ("train", "val", "test"):
        for name in splits.get(sub, []):
            im = by_name.get(name)
            if im is None:
                continue
            uid = _uid(name, seen)

            with open(os.path.join(out_dir, "labels", sub, uid + ".txt"), "w") as f:
                for b in im.boxes:
                    cid = taxonomy.CLASS_TO_ID[b.cls]
                    f.write(f"{cid} {b.cx:.6f} {b.cy:.6f} {b.w:.6f} {b.h:.6f}\n")
            written[sub] += 1

            if copy_images:
                # 1) the dataset's own path (CubiCasa stores a real one)
                src = name if os.path.exists(name) else None
                # 2) fall back to a flat image dir + basename (COCO-style)
                if src is None and images_src_dir:
                    cand = os.path.join(images_src_dir, os.path.basename(name))
                    if os.path.exists(cand):
                        src = cand
                if src:
                    ext = os.path.splitext(src)[1] or ".png"
                    shutil.copy2(src, os.path.join(out_dir, "images", sub, uid + ext))
                    copied[sub] += 1
                else:
                    missing_images.append(name)

    data_yaml = os.path.join(out_dir, "data.yaml")
    with open(data_yaml, "w") as f:
        f.write(f"path: {os.path.abspath(out_dir)}\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n")
        f.write("test: images/test\n")
        f.write(f"nc: {taxonomy.NUM_CLASSES}\n")
        f.write("names:\n")
        for i, nm in enumerate(taxonomy.CLASSES):
            f.write(f"  {i}: {nm}\n")

    if copy_images:
        print(f"images copied: {copied}")
        if missing_images:
            print(f"!! {len(missing_images)} images NOT found -- training will skip these.")
            for m in missing_images[:5]:
                print("   missing:", m)
    # a label file with no matching image is silently ignored by Ultralytics,
    # so surface any mismatch loudly rather than training on a fraction
    return written, data_yaml


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("internal_json")
    p.add_argument("splits_json")
    p.add_argument("--out", default="yolo_dataset")
    p.add_argument("--images", default=None)
    p.add_argument("--copy-images", action="store_true")
    args = p.parse_args()
    ds = Dataset.from_dict(json.load(open(args.internal_json)))
    splits = json.load(open(args.splits_json))
    written, data_yaml = export(ds, splits, args.out, args.images, args.copy_images)
    print("label files written:", written)
    print("data.yaml:", data_yaml)
