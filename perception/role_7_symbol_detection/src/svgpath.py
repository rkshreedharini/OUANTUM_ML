"""Correct SVG path 'd' parsing for bounding-box extraction.

WHY THIS EXISTS. The naive approach -- regex every number out of a `d` string
and pair them as (x, y) -- is wrong, and wrong in a way that silently destroys
a dataset rather than raising.

An SVG arc command is:

    A rx ry x-axis-rotation large-arc-flag sweep-flag x y

Seven numbers, of which ONLY THE LAST TWO are a coordinate. Naive pairing reads
the radii and the flags as points. On CubiCasa5k this inflated every
arc-drawn element enormously: `Door Swing Beside` (a door with a swing arc)
measured a median 34% of image area, versus 0.083% for `Door None Beside`,
which has no arc. Doors are the highest-value class in this project, so the
corruption landed exactly where it hurt most.

This module walks the path properly: it tracks the current point, honours
relative (lowercase) commands, and consumes the correct argument count per
command, emitting only real coordinates.

Bezier control points ARE included. They are not on the curve, but the curve is
guaranteed to lie inside their convex hull, so the resulting bbox is a correct
(slightly loose) bound rather than a wrong one. Arc endpoints are exact; the
arc bulge is not modelled, which can under-cover a wide arc slightly -- an
acceptable trade for a box detector, and far better than the alternative.

Pure stdlib.
"""

import re

# argument count per command, lowercase key
ARGC = {"m": 2, "l": 2, "h": 1, "v": 1, "c": 6, "s": 4,
        "q": 4, "t": 2, "a": 7, "z": 0}

_TOKEN = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")


def path_points(d):
    """Return [(x, y), ...] of real coordinates referenced by a path 'd'."""
    if not d:
        return []
    toks = _TOKEN.finditer(d)
    pts = []
    cx = cy = 0.0          # current point
    sx = sy = 0.0          # subpath start (for Z)
    cmd = None
    buf = []

    def flush():
        """Consume buffered numbers for the pending command."""
        nonlocal cx, cy, sx, sy, buf
        if cmd is None:
            buf = []
            return
        low = cmd.lower()
        rel = cmd.islower()
        n = ARGC[low]
        if n == 0:
            cx, cy = sx, sy
            buf = []
            return
        i = 0
        first = True
        while i + n <= len(buf):
            a = buf[i:i + n]
            if low == "m":
                x, y = (cx + a[0], cy + a[1]) if rel else (a[0], a[1])
                cx, cy = x, y
                if first:
                    sx, sy = cx, cy
                pts.append((cx, cy))
            elif low == "l" or low == "t":
                x, y = (cx + a[0], cy + a[1]) if rel else (a[0], a[1])
                cx, cy = x, y
                pts.append((cx, cy))
            elif low == "h":
                cx = cx + a[0] if rel else a[0]
                pts.append((cx, cy))
            elif low == "v":
                cy = cy + a[0] if rel else a[0]
                pts.append((cx, cy))
            elif low == "c":
                if rel:
                    p = [(cx + a[0], cy + a[1]), (cx + a[2], cy + a[3]), (cx + a[4], cy + a[5])]
                else:
                    p = [(a[0], a[1]), (a[2], a[3]), (a[4], a[5])]
                pts.extend(p)
                cx, cy = p[-1]
            elif low == "s" or low == "q":
                if rel:
                    p = [(cx + a[0], cy + a[1]), (cx + a[2], cy + a[3])]
                else:
                    p = [(a[0], a[1]), (a[2], a[3])]
                pts.extend(p)
                cx, cy = p[-1]
            elif low == "a":
                # a[0..4] = rx, ry, rotation, large-arc-flag, sweep-flag -> NOT points
                x, y = (cx + a[5], cy + a[6]) if rel else (a[5], a[6])
                cx, cy = x, y
                pts.append((cx, cy))
            i += n
            first = False
            # after an explicit moveto, repeated pairs are implicit linetos
            if low == "m":
                low = "l"
                n = 2
        buf = []

    for m in toks:
        t = m.group()
        if t[0].isalpha():
            flush()
            cmd = t
            if cmd.lower() == "z":
                flush()
                cmd = None
        else:
            buf.append(float(t))
    flush()
    return pts


def points_attr(points):
    """Parse a polygon/polyline `points` attribute -- plain coordinate pairs."""
    if not points:
        return []
    nums = [float(n) for n in re.findall(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?", points)]
    return list(zip(nums[0::2], nums[1::2]))


if __name__ == "__main__":
    # The exact failure mode this module exists to prevent.
    d = "M 100 100 A 45 45 0 0 1 130 130 L 130 100 Z"
    naive = list(zip(*[iter([float(n) for n in re.findall(r"-?\d*\.?\d+", d)])] * 2))
    good = path_points(d)
    nx = [p[0] for p in naive]; ny = [p[1] for p in naive]
    gx = [p[0] for p in good]; gy = [p[1] for p in good]
    print("path:", d)
    print(f"  naive pairing -> {len(naive)} pts, bbox x[{min(nx)},{max(nx)}] y[{min(ny)},{max(ny)}]")
    print(f"  correct       -> {len(good)} pts, bbox x[{min(gx)},{max(gx)}] y[{min(gy)},{max(gy)}]")
    assert min(gx) >= 100 and max(gx) <= 130, "arc endpoints wrong"
    assert min(nx) < 100, "naive should have been wrong (sanity of the demo)"
    print("\nPASS: arc flags/radii are no longer read as coordinates")
