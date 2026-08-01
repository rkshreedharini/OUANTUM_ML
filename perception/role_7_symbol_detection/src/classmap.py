"""Robust category-name -> training-class resolution.

Resolves in three tiers and REPORTS how each name was mapped, so nothing is
silently dropped and nothing is silently guessed:

  1. exact    -- name is a key in the explicit class_map (highest trust)
  2. keyword  -- name contains a known keyword for a class. Best-effort;
                 surfaced for confirmation.
  3. unmapped -- no match. Counted and reported, never trained on.

TWO KINDS OF KEYWORD, and the distinction matters:

  KEYWORDS      matched as a SUBSTRING. Safe for long, distinctive words
                ('bath' must match inside 'bathtub', 'furniture' inside
                'FixedFurniture').

  WORD_KEYWORDS matched only at WORD BOUNDARIES. Short abbreviations like 'wc'
                are dangerous as substrings -- 'wc' appears inside
                'ResizeSWControl', an Illustrator selection handle, which
                produced 1,536 phantom 'fixture' boxes on real CubiCasa5k data
                before this split existed. Verified against 300 real plans.

Keyword lists cover the CubiCasa5k vocabulary (Phase-0 dataset, workflow S9),
where doors are 'Door Swing Beside', fixtures are 'FixedFurniture Closet', and
stairs are 'Steps' or 'Stairs'. Extend as real category names appear.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402

# Substring-matched. Only put words here that are long/distinctive enough that
# an accidental substring hit is implausible.
KEYWORDS = {
    "door":   ["door", "doorway", "entrance", "gate"],
    "window": ["window", "glazing", "casement", "skylight"],
    "stair":  ["stair", "staircase", "step", "escalator"],
    "fixture": [
        # sanitary
        "toilet", "sink", "basin", "bath", "tub", "shower", "jacuzzi",
        "bidet", "urinal",
        # appliances
        "washingmachine", "washing", "dishwasher", "dryer", "stove", "oven",
        "cooktop", "fridge", "refrigerator", "freezer", "appliance",
        # built-ins / furniture (CubiCasa: 'FixedFurniture <Type>')
        "furniture", "chimney", "fireplace", "sauna", "closet", "wardrobe",
        "cabinet", "counter", "fixture", "sofa", "desk", "table", "chair",
        "shelf",
    ],
}

# Word-boundary matched. Short/ambiguous tokens that would false-positive as
# substrings. See the ResizeSWControl case in the module docstring.
WORD_KEYWORDS = {
    "fixture": ["wc", "bed", "hob"],
}


def _word_hit(kw, low):
    return re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", low) is not None


def resolve(name, explicit_map=None):
    """Return (train_cls_or_None, how) where how in {'exact','keyword','unmapped'}."""
    explicit_map = explicit_map or {}
    if name in explicit_map:
        tc = explicit_map[name]
        if tc not in taxonomy.CLASS_TO_ID:
            raise ValueError(f"class_map maps {name!r} to unknown class {tc!r}")
        return tc, "exact"
    if name is None:
        return None, "unmapped"
    low = str(name).lower()
    for cls in taxonomy.CLASSES:            # taxonomy order keeps this deterministic
        for kw in KEYWORDS[cls]:
            if kw in low:
                return cls, "keyword"
        for kw in WORD_KEYWORDS.get(cls, []):
            if _word_hit(kw, low):
                return cls, "keyword"
    return None, "unmapped"


def build_resolution_report(names, explicit_map=None):
    """Given the category names in a dataset, report how each resolves."""
    exact, keyword, unmapped = {}, {}, []
    for name in sorted(set(n for n in names if n is not None)):
        tc, how = resolve(name, explicit_map)
        if how == "exact":
            exact[name] = tc
        elif how == "keyword":
            keyword[name] = tc
        else:
            unmapped.append(name)
    return {"exact": exact, "keyword": keyword, "unmapped": unmapped}


def print_resolution_report(rep):
    print("category -> class resolution:")
    if rep["exact"]:
        print("  exact (from class_map):")
        for k, v in rep["exact"].items():
            print(f"    {k} -> {v}")
    if rep["keyword"]:
        print("  keyword-guessed (CONFIRM these before training):")
        for k, v in rep["keyword"].items():
            print(f"    {k} -> {v}   [add to class_map to lock in]")
    if rep["unmapped"]:
        print("  unmapped (ignored, not trained on):")
        for k in rep["unmapped"]:
            print(f"    {k}")


if __name__ == "__main__":
    # Regression check: the real CubiCasa names that broke this before.
    cases = [
        ("Door Swing Beside", "door"), ("Doors", "door"), ("Door Slide Beside", "door"),
        ("Window Regular", "window"), ("Window Sauna", "window"),
        ("Steps", "stair"), ("Stairs", "stair"),
        ("FixedFurniture Closet", "fixture"), ("FixedFurnitureSet", "fixture"),
        ("WC-toilet", "fixture"), ("washingmachine", "fixture"),
        # these MUST NOT resolve -- Illustrator UI handles
        ("ResizeSWControl", None), ("ResizeWControl", None), ("ResizeNWControl", None),
        ("SelectionControls", None), ("rotateControl", None),
        ("DimensionMark", None), ("BoundaryPolygon", None), ("Threshold", None),
    ]
    bad = 0
    for name, want in cases:
        got, _ = resolve(name, None)
        ok = got == want
        bad += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name!r:28} -> {got}  (want {want})")
    print("\nALL RESOLUTION TESTS PASSED" if not bad else f"\n{bad} FAILED")
