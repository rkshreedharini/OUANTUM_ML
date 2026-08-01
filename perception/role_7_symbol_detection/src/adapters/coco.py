"""COCO -> internal schema adapter.

Reads a standard COCO instances JSON. Category names resolve to training classes
via classmap.resolve (exact class_map first, then keyword fallback), so an
unfamiliar category in a newly uploaded dataset still gets a best-effort mapping
that is reported for confirmation rather than silently dropped. The original
COCO name is preserved on each box as `subtype`.

Pure stdlib -- runs on CPU with no torch/ultralytics installed.
"""

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Dataset, Image, Box  # noqa: E402
import classmap  # noqa: E402


def load_coco(coco_json_path, class_map=None):
    """
    class_map: optional {COCO name -> training class}. Names not in it fall back
               to keyword resolution. Returns (Dataset, unmapped_counter).
    """
    with open(coco_json_path) as f:
        coco = json.load(f)

    cat_by_id = {c["id"]: c["name"] for c in coco["categories"]}
    img_by_id = {im["id"]: im for im in coco["images"]}

    ds = Dataset()
    images_index = {}
    for im in coco["images"]:
        obj = Image(file_name=im["file_name"], width=im["width"], height=im["height"])
        images_index[im["id"]] = obj
        ds.images.append(obj)

    unmapped = Counter()
    for ann in coco["annotations"]:
        coco_name = cat_by_id[ann["category_id"]]
        train_cls, how = classmap.resolve(coco_name, class_map)
        if train_cls is None:
            unmapped[coco_name] += 1
            continue

        im = img_by_id[ann["image_id"]]
        W, H = im["width"], im["height"]
        x, y, w, h = ann["bbox"]  # COCO bbox = [x_min, y_min, w, h] in pixels
        box = Box(cls=train_cls, cx=(x + w / 2) / W, cy=(y + h / 2) / H,
                  w=w / W, h=h / H, subtype=coco_name)
        if box.valid():
            images_index[ann["image_id"]].boxes.append(box)

    return ds, unmapped


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("coco_json")
    p.add_argument("--class-map", default=None, help="JSON dict: COCO name -> training class")
    p.add_argument("--out", default="internal.json")
    args = p.parse_args()
    cmap = json.load(open(args.class_map)) if args.class_map else None
    ds, unmapped = load_coco(args.coco_json, cmap)
    json.dump(ds.to_dict(), open(args.out, "w"))
    print(f"wrote {args.out}: {len(ds.images)} images")
    if unmapped:
        print("unmapped:", dict(unmapped.most_common()))
