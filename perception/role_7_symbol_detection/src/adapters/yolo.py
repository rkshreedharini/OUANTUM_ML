"""YOLO dataset -> internal schema adapter.

Handles the case where the uploaded sample is ALREADY in YOLO format: a
directory with a data.yaml (giving class names + image/label folders) or a
plain images/ + labels/ pair. Label lines are `cls cx cy w h` (normalized).
Class names come from data.yaml `names`; they resolve through classmap so they
still land on our 4 training classes.

Needs Pillow only if image sizes must be read; YOLO labels are already
normalized so we don't actually need the images to build the internal dataset.
Pure stdlib otherwise.
"""

import os
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Dataset, Image, Box  # noqa: E402
import classmap  # noqa: E402
from collections import Counter  # noqa: E402


def _read_names(root):
    for cand in ("data.yaml", "dataset.yaml", "data.yml"):
        p = os.path.join(root, cand)
        if os.path.exists(p):
            import yaml
            d = yaml.safe_load(open(p))
            names = d.get("names")
            if isinstance(names, dict):
                return {int(k): v for k, v in names.items()}
            if isinstance(names, list):
                return {i: n for i, n in enumerate(names)}
    return None


def load_yolo(root, class_map=None, names=None):
    """
    root: dataset dir. names: optional {id: name}; else read from data.yaml.
    Returns (Dataset, unmapped_counter).
    """
    names = names or _read_names(root)
    if names is None:
        raise ValueError(f"No data.yaml/names found under {root}; pass names={{id:name}} explicitly.")

    label_files = glob.glob(os.path.join(root, "**", "labels", "**", "*.txt"), recursive=True)
    label_files += glob.glob(os.path.join(root, "labels", "*.txt"))
    label_files = sorted(set(label_files))

    ds = Dataset()
    unmapped = Counter()
    for lf in label_files:
        stem = os.path.splitext(os.path.basename(lf))[0]
        # width/height unknown & unneeded (coords already normalized); store 0
        img = Image(file_name=stem + ".png", width=0, height=0)
        for line in open(lf):
            parts = line.split()
            if len(parts) != 5:
                continue
            cid, cx, cy, w, h = int(float(parts[0])), *map(float, parts[1:])
            src_name = names.get(cid, str(cid))
            train_cls, how = classmap.resolve(src_name, class_map)
            if train_cls is None:
                unmapped[src_name] += 1
                continue
            box = Box(cls=train_cls, cx=cx, cy=cy, w=w, h=h, subtype=src_name)
            if box.valid():
                img.boxes.append(box)
        ds.images.append(img)
    return ds, unmapped


if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("root")
    p.add_argument("--out", default="internal.json")
    args = p.parse_args()
    ds, unmapped = load_yolo(args.root)
    json.dump(ds.to_dict(), open(args.out, "w"))
    print(f"wrote {args.out}: {len(ds.images)} images; unmapped={dict(unmapped)}")
