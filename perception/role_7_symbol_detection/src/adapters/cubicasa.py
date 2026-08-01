"""CubiCasa5k -> internal schema adapter.  (v3 -- transform-aware)

CubiCasa5k: 5,000 annotated floor plans (workflow doc S9), one folder per
apartment holding model.svg + F1_scaled.png.

THREE HARD-WON LESSONS ENCODED HERE, all found on the real data:

1. ARC PARSING (src/svgpath.py). Door swings are SVG arcs; regex-pairing every
   number in a path `d` reads arc radii/flags as coordinates. Doors measured
   34% of image area instead of 0.4%.

2. TRANSFORMS ARE NOT OPTIONAL. Groups carry transform="translate/matrix/..."
   attributes; element coordinates are in LOCAL space. Ignoring transforms put
   whole clusters of boxes in the top-left corner of the image, off the
   drawing. The model then learned that blank paper is a fixture -- round-2
   training produced door recall of 0.02 because most door labels were
   displaced. This version composes the full transform stack from the SVG root
   down and maps every point to absolute coordinates.

3. NESTING POLICY: innermost-wins. A FixedFurnitureSet contains individual
   FixedFurniture members; emitting the set AND its members double-labels the
   region (and a set-sized box is useless for detection). If a resolving group
   contains resolving descendants, we skip the parent and keep the leaves.
   Identical nested duplicates (Door inside Door) collapse via exact dedupe.

Pure stdlib.
"""

import os
import re
import sys
import glob
import math
import struct
import xml.etree.ElementTree as ET
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Dataset, Image, Box  # noqa: E402
import classmap  # noqa: E402
import svgpath   # noqa: E402

IGNORE_PREFIXES = (
    "wall", "space", "railing", "background",
    "selectioncontrols", "resize", "rotatecontrol", "removecontrol",
    "copypastecontrol", "translatecontrol",
    "dimensionmark", "dimension", "textlabel", "name", "direction", "visual",
    "boundarypolygon", "innerpolygon", "overlaypolygon", "walkinline",
    "electricitysign", "heatersign", "threshold", "spacedimensionslabel",
    "indicator", "model", "floorplan", "floorscompose", "composeelement",
    "floor", "lines", "column", "handle",
    "glass", "panel", "panelarea", "faucet", "outerdrain", "innerdrain",
    "outercircle", "innercircle", "firebox", "pipe", "tap",
    "flight", "winding", "roundedwinding", "landing",
)

_NUM = re.compile(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?")
_XFORM = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)")

# ---------- 2x3 affine transforms: (a, b, c, d, e, f) ----------
# x' = a*x + c*y + e ;  y' = b*x + d*y + f   (SVG convention)
IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _mat_mul(m1, m2):
    """Compose: apply m2 first, then m1 (SVG parent-then-child order is
    parent_matrix * child_matrix)."""
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def _mat_apply(m, x, y):
    a, b, c, d, e, f = m
    return a * x + c * y + e, b * x + d * y + f


def parse_transform(s):
    """Parse an SVG transform attribute into one composed matrix."""
    m = IDENTITY
    if not s:
        return m
    for name, args in _XFORM.findall(s):
        nums = [float(n) for n in _NUM.findall(args)]
        if name == "matrix" and len(nums) == 6:
            t = tuple(nums)
        elif name == "translate":
            tx = nums[0] if nums else 0.0
            ty = nums[1] if len(nums) > 1 else 0.0
            t = (1, 0, 0, 1, tx, ty)
        elif name == "scale":
            sx = nums[0] if nums else 1.0
            sy = nums[1] if len(nums) > 1 else sx
            t = (sx, 0, 0, sy, 0, 0)
        elif name == "rotate":
            ang = math.radians(nums[0]) if nums else 0.0
            ca, sa = math.cos(ang), math.sin(ang)
            if len(nums) >= 3:
                cx, cy = nums[1], nums[2]
                t = _mat_mul(_mat_mul((1, 0, 0, 1, cx, cy),
                                      (ca, sa, -sa, ca, 0, 0)),
                             (1, 0, 0, 1, -cx, -cy))
            else:
                t = (ca, sa, -sa, ca, 0, 0)
        elif name == "skewX":
            t = (1, 0, math.tan(math.radians(nums[0])), 1, 0, 0) if nums else IDENTITY
        elif name == "skewY":
            t = (1, math.tan(math.radians(nums[0])), 0, 1, 0, 0) if nums else IDENTITY
        else:
            t = IDENTITY
        m = _mat_mul(m, t)
    return m


# ---------- geometry ----------

def _strip_ns(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def _element_points(el):
    t = _strip_ns(el.tag)
    if t == "rect":
        try:
            x, y = float(el.get("x", 0)), float(el.get("y", 0))
            w, h = float(el.get("width", 0)), float(el.get("height", 0))
            return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        except (TypeError, ValueError):
            return []
    if t == "circle":
        try:
            cx, cy, r = float(el.get("cx", 0)), float(el.get("cy", 0)), float(el.get("r", 0))
            return [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)]
        except (TypeError, ValueError):
            return []
    if t == "ellipse":
        try:
            cx, cy = float(el.get("cx", 0)), float(el.get("cy", 0))
            rx, ry = float(el.get("rx", 0)), float(el.get("ry", 0))
            return [(cx - rx, cy - ry), (cx + rx, cy - ry), (cx + rx, cy + ry), (cx - rx, cy + ry)]
        except (TypeError, ValueError):
            return []
    if t in ("polygon", "polyline"):
        return svgpath.points_attr(el.get("points"))
    if t == "path":
        return svgpath.path_points(el.get("d"))
    if t == "line":
        try:
            return [(float(el.get("x1", 0)), float(el.get("y1", 0))),
                    (float(el.get("x2", 0)), float(el.get("y2", 0)))]
        except (TypeError, ValueError):
            return []
    return []


def _collect_abs_points(el, xf, out):
    """All geometry points in el's subtree, mapped to absolute coords."""
    xf = _mat_mul(xf, parse_transform(el.get("transform")))
    for x, y in _element_points(el):
        out.append(_mat_apply(xf, x, y))
    for child in el:
        _collect_abs_points(child, xf, out)


def _source_label(class_attr):
    toks = [t for t in class_attr.replace(",", " ").split() if t]
    if not toks:
        return None
    if toks[0].lower() == "icon" and len(toks) > 1:
        return toks[1].lower()
    return toks[0].lower()


def _resolves(el, class_map):
    cls_attr = el.get("class") or ""
    if not cls_attr:
        return None, None
    label = _source_label(cls_attr)
    if not label or label.startswith(IGNORE_PREFIXES):
        return None, cls_attr
    tc, _ = classmap.resolve(label, class_map)
    return tc, cls_attr


def _has_resolving_descendant(el, class_map):
    for child in el:
        if _strip_ns(child.tag) == "g":
            tc, _ = _resolves(child, class_map)
            if tc is not None:
                return True
        if _has_resolving_descendant(child, class_map):
            return True
    return False


def _png_size(path):
    """Read PNG pixel dimensions from the IHDR header. Pure stdlib.

    WHY THE PNG AND NOT THE SVG ATTRIBUTES: measured on 300 real plans, 272
    had an SVG width/height that mismatched the PNG's aspect -- the SVG attrs
    describe the annotated content's extent, while the coordinates are in the
    PNG's pixel space. Normalizing by SVG dims displaced boxes on ~90% of the
    dataset (downward-shifted labels, round-3 visual check)."""
    try:
        with open(path, "rb") as f:
            head = f.read(24)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            return None, None
        w, h = struct.unpack(">II", head[16:24])
        return int(w), int(h)
    except Exception:
        return None, None


def _svg_size(root):
    def _f(v):
        if not v:
            return None
        m = _NUM.search(v)
        return float(m.group()) if m else None
    W, H = _f(root.get("width")), _f(root.get("height"))
    if not (W and H):
        vb = root.get("viewBox")
        if vb:
            nums = [float(n) for n in _NUM.findall(vb)]
            if len(nums) == 4:
                W, H = nums[2], nums[3]
    return W, H


# ---------- main walk ----------

def _walk(el, xf, W, H, img, class_map, unmapped, stats, seen):
    xf_here = _mat_mul(xf, parse_transform(el.get("transform")))
    for child in el:
        if _strip_ns(child.tag) != "g":
            continue
        tc, cls_attr = _resolves(child, class_map)
        if tc is None:
            # Not a detection target -- but ALWAYS keep walking. Real CubiCasa
            # SVGs wrap all content in <g class="Model v1-1"> / <g class=
            # "Floorplan Floor-1">, both on the ignore list; refusing to
            # descend through them yields ZERO boxes on the entire dataset
            # (found the hard way in round 3).
            if cls_attr is not None:
                label = _source_label(cls_attr)
                if label and not label.startswith(IGNORE_PREFIXES):
                    unmapped[cls_attr] += 1
                else:
                    stats["ignored"] += 1
            _walk(child, xf_here, W, H, img, class_map, unmapped, stats, seen)
            continue

        # innermost-wins: a Set containing resolving members yields the members
        if _has_resolving_descendant(child, class_map):
            stats["container_skipped"] += 1
            _walk(child, xf_here, W, H, img, class_map, unmapped, stats, seen)
            continue

        pts = []
        _collect_abs_points(child, xf_here, pts)
        if not pts:
            stats["group_without_geometry"] += 1
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        # clamp to the image frame: annotations may extend slightly past the
        # PNG edge (content extent vs frame); clip instead of discarding
        x1, y1 = max(0.0, min(xs)), max(0.0, min(ys))
        x2, y2 = min(W, max(xs)), min(H, max(ys))
        bw, bh = x2 - x1, y2 - y1
        if bw <= 0 or bh <= 0:
            stats["degenerate_box"] += 1
            continue
        box = Box(cls=tc, cx=(x1 + x2) / 2 / W, cy=(y1 + y2) / 2 / H,
                  w=bw / W, h=bh / H, subtype=cls_attr)
        if not box.valid():
            stats["out_of_bounds_box"] += 1
            continue
        key = (tc, round(box.cx, 5), round(box.cy, 5), round(box.w, 5), round(box.h, 5))
        if key in seen:
            stats["duplicate_box_skipped"] += 1
            continue
        seen.add(key)
        img.boxes.append(box)
        stats[f"box_{tc}"] += 1


def load_cubicasa(root, class_map=None, audit=False, limit=None):
    svgs = sorted(glob.glob(os.path.join(root, "**", "model.svg"), recursive=True))
    if not svgs:
        svgs = sorted(glob.glob(os.path.join(root, "**", "*.svg"), recursive=True))
    if limit:
        svgs = svgs[:limit]

    ds = Dataset()
    unmapped = Counter()
    stats = Counter()

    for svg_path in svgs:
        try:
            rt = ET.parse(svg_path).getroot()
        except ET.ParseError:
            stats["unparseable_svg"] += 1
            continue
        W, H = _svg_size(rt)
        if not (W and H):
            stats["missing_size"] += 1
            continue

        folder = os.path.dirname(svg_path)
        png = None
        for cand in ("F1_scaled.png", "F1_original.png"):
            if os.path.exists(os.path.join(folder, cand)):
                png = cand
                break
        if png is None:
            stats["no_image"] += 1
            continue

        # normalize by the PNG's REAL pixel size (SVG coords live in PNG
        # pixel space; the SVG width/height attrs are just the content extent
        # -- mismatched on ~90% of plans). SVG dims only as fallback.
        png_path = os.path.join(folder, png)
        PW, PH = _png_size(png_path)
        if PW and PH:
            if abs(PW - W) > 2 or abs(PH - H) > 2:
                stats["svg_png_dim_mismatch"] += 1
            W, H = float(PW), float(PH)
        else:
            stats["png_header_unreadable"] += 1

        img = Image(file_name=png_path, width=int(W), height=int(H))
        _walk(rt, IDENTITY, W, H, img, class_map, unmapped, stats, set())
        ds.images.append(img)
        stats["images"] += 1

    if audit:
        print(f"--- CubiCasa audit ({len(svgs)} svg files) ---")
        for k, v in sorted(stats.items()):
            print(f"  {k}: {v}")
        if unmapped:
            print("  unmapped (top 15):", dict(unmapped.most_common(15)))
        if sum(v for k, v in stats.items() if k.startswith("box_")) == 0:
            print("  !! ZERO boxes parsed -- inspect one model.svg before training.")
    return ds, unmapped


if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("root")
    p.add_argument("--out", default="internal.json")
    p.add_argument("--audit", action="store_true")
    p.add_argument("--limit", type=int, default=None)
    args = p.parse_args()
    ds, unmapped = load_cubicasa(args.root, audit=args.audit, limit=args.limit)
    json.dump(ds.to_dict(), open(args.out, "w"))
    print(f"wrote {args.out}: {len(ds.images)} images, "
          f"{sum(len(i.boxes) for i in ds.images)} boxes")
