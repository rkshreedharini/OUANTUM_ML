"""Label Studio -> internal schema adapter.

Built against the Data & Annotation pod's ACTUAL setup
(github.com/Jerlin-Ishabel/BIM_Vision, inspected 2026-07):

  - label_studio/config.xml uses <PolygonLabels> for Room, Wall, Door, Window.
    So their exports carry doors/windows as POLYGONS; we take each polygon's
    axis-aligned bbox.
  - Their schema DOC (annotations/schemas/annotation_schema.json) says Door and
    Window are Rectangles. The doc and the config contradict each other, so
    this adapter accepts BOTH result types: `polygonlabels` and
    `rectanglelabels`. Whichever way the pod resolves the inconsistency, the
    adapter keeps working.
  - Their schema has NO Stair and NO Fixture. Those classes simply won't
    appear from this source until the pod adds them -- flagged in the balance
    report as zero-count, not silently hidden.

Supported export shapes (both standard Label Studio JSON):
  - full export:  [{"data": {"image": ...}, "annotations": [{"result": [...]}]}]
  - JSON-MIN:     [{"image": ..., "label": [...]}]  (best-effort)

Coordinate convention: Label Studio emits polygon points and rectangle x/y/
width/height as PERCENTAGES of image size (0-100). We normalize to [0,1].

Room/Wall polygons are ignored here -- walls belong to Roles 5/6, rooms to the
Context Engine. Relationship entries (`type: "relation"`) are skipped; door->
wall attachment is the Context Engine's job (workflow S4.3 step 3).

Pure stdlib.
"""

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Dataset, Image, Box  # noqa: E402
import classmap  # noqa: E402

# Deliberately ignored, not 'unmapped': owned by other roles. Walls belong to
# Roles 5/6 (segmentation), rooms to the Context Engine, corners to Role 9.
IGNORED_LABELS = {"room", "wall", "corner"}


def _bbox_from_result(res):
    """Return (x_min, y_min, w, h) in percent units, or None."""
    v = res.get("value", {})
    rtype = res.get("type", "")
    if rtype == "rectanglelabels" or ("x" in v and "width" in v):
        try:
            return float(v["x"]), float(v["y"]), float(v["width"]), float(v["height"])
        except (KeyError, TypeError, ValueError):
            return None
    if rtype == "polygonlabels" or "points" in v:
        pts = v.get("points") or []
        if len(pts) < 3:
            return None
        try:
            xs = [float(p[0]) for p in pts]
            ys = [float(p[1]) for p in pts]
        except (TypeError, ValueError, IndexError):
            return None
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    return None


def _labels_from_result(res):
    v = res.get("value", {})
    return v.get("polygonlabels") or v.get("rectanglelabels") or v.get("labels") or []


def load_labelstudio(export_path, class_map=None):
    """export_path: a Label Studio JSON export file (full or JSON-MIN).
    Returns (Dataset, unmapped_counter)."""
    with open(export_path) as f:
        tasks = json.load(f)
    if isinstance(tasks, dict):
        tasks = tasks.get("tasks") or [tasks]

    ds = Dataset()
    unmapped = Counter()

    for task in tasks:
        # image reference: full export nests it under 'data'
        data = task.get("data", task)
        image_ref = data.get("image") or data.get("img") or ""
        img = Image(file_name=image_ref, width=0, height=0)

        # collect result lists from every annotation on the task
        results = []
        for ann in task.get("annotations", []) or []:
            results += ann.get("result", []) or []
        for pred in task.get("predictions", []) or []:  # tolerate pre-annotations
            results += pred.get("result", []) or []
        if not results and "label" in task:              # JSON-MIN
            results = [{"type": "polygonlabels",
                        "value": {"points": r.get("points", []),
                                  "polygonlabels": [r.get("polygonlabels", [None])[0]]}}
                       if "points" in r else
                       {"type": "rectanglelabels", "value": r}
                       for r in task.get("label", [])]

        for res in results:
            if res.get("type") == "relation":
                continue  # door->wall hosting is the Context Engine's job
            labels = _labels_from_result(res)
            if not labels:
                continue
            raw_label = str(labels[0])
            if raw_label.lower() in IGNORED_LABELS:
                continue  # other roles' targets, skipped by design
            train_cls, _how = classmap.resolve(raw_label, class_map)
            if train_cls is None:
                unmapped[raw_label] += 1
                continue
            bb = _bbox_from_result(res)
            if bb is None:
                continue
            x, y, w, h = bb
            # percent (0-100) -> normalized (0-1)
            ow = res.get("original_width")
            oh = res.get("original_height")
            if ow and img.width == 0:
                img.width, img.height = int(ow), int(oh or 0)
            box = Box(cls=train_cls,
                      cx=(x + w / 2) / 100.0, cy=(y + h / 2) / 100.0,
                      w=w / 100.0, h=h / 100.0, subtype=raw_label)
            if box.valid():
                img.boxes.append(box)

        ds.images.append(img)

    return ds, unmapped


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("export_json")
    p.add_argument("--out", default="internal.json")
    args = p.parse_args()
    ds, unmapped = load_labelstudio(args.export_json)
    json.dump(ds.to_dict(), open(args.out, "w"))
    print(f"wrote {args.out}: {len(ds.images)} images, "
          f"{sum(len(i.boxes) for i in ds.images)} boxes; unmapped={dict(unmapped)}")
