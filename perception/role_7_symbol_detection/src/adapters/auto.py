"""Auto-detect annotation format from an uploaded path, then dispatch.

Detection rules (first match wins):
  - dir containing model.svg                          -> CUBICASA
  - a .json with 'annotations' + 'categories'         -> COCO
  - a dir containing such a .json                     -> COCO
  - a dir with data.yaml / labels/*.txt               -> YOLO
  - a dir with *.xml                                  -> VOC

Returns (format_name, Dataset, unmapped_counter). This is what lets the
pipeline take 'any dataset you upload': point it at the folder and it works
out the rest. Ambiguous input raises with a clear message rather than guessing.
"""

import os
import sys
import glob
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from adapters.coco import load_coco          # noqa: E402
from adapters.yolo import load_yolo          # noqa: E402
from adapters.voc import load_voc            # noqa: E402
from adapters.cubicasa import load_cubicasa  # noqa: E402


def _looks_like_coco(path):
    try:
        d = json.load(open(path))
        return isinstance(d, dict) and "annotations" in d and "categories" in d
    except Exception:
        return False


def detect_format(path):
    if os.path.isfile(path) and path.endswith(".json") and _looks_like_coco(path):
        return "coco", path
    if os.path.isdir(path):
        # CubiCasa first: its folders also contain PNGs that could confuse others
        if glob.glob(os.path.join(path, "**", "model.svg"), recursive=True):
            return "cubicasa", path
        for jf in glob.glob(os.path.join(path, "**", "*.json"), recursive=True):
            if _looks_like_coco(jf):
                return "coco", jf
        if (glob.glob(os.path.join(path, "**", "data.yaml"), recursive=True)
                or glob.glob(os.path.join(path, "**", "labels", "*.txt"), recursive=True)
                or glob.glob(os.path.join(path, "labels", "*.txt"))):
            return "yolo", path
        if glob.glob(os.path.join(path, "**", "*.xml"), recursive=True):
            return "voc", path
        if glob.glob(os.path.join(path, "**", "*.svg"), recursive=True):
            return "cubicasa", path
    raise ValueError(
        f"Could not detect annotation format at {path!r}. Expected a COCO .json, "
        f"a YOLO dir (data.yaml or labels/*.txt), a VOC dir (*.xml), or a "
        f"CubiCasa5k dir (model.svg). If it's a new format, add one adapter in "
        f"src/adapters/ -- everything downstream stays the same."
    )


def load_any(path, class_map=None, limit=None):
    """limit: cap the number of source files parsed (CubiCasa only, for subsets)."""
    fmt, target = detect_format(path)
    if fmt == "coco":
        ds, unmapped = load_coco(target, class_map)
    elif fmt == "yolo":
        ds, unmapped = load_yolo(target, class_map)
    elif fmt == "voc":
        ds, unmapped = load_voc(target, class_map)
    elif fmt == "cubicasa":
        ds, unmapped = load_cubicasa(target, class_map, limit=limit)
    else:
        raise AssertionError(fmt)
    return fmt, ds, unmapped
