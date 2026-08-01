"""Single source of truth for the detection class taxonomy.

Role 7 trains on 4 flat classes. Finer labels (e.g. `toilet`, `double_door`)
are preserved on each box as `subtype` metadata but are NOT trained on --
splitting fixtures into sparse subclasses tanks mAP for no downstream benefit,
while discarding the label would waste annotation work.
"""

# Training classes, in fixed index order. Index == YOLO class id.
CLASSES = ["door", "window", "stair", "fixture"]

CLASS_TO_ID = {name: i for i, name in enumerate(CLASSES)}
ID_TO_CLASS = {i: name for i, name in enumerate(CLASSES)}

NUM_CLASSES = len(CLASSES)

# Structural importance -> drives the per-class F-beta used for thresholding.
# beta > 1 favours recall, beta < 1 favours precision. See thresholds.py.
CLASS_BETA = {
    "door": 2.0,    # a missed doorway becomes a solid wall in the IFC; nothing flags it
    "window": 2.0,  # same structural consequence as doors
    "stair": 1.0,   # balanced
    "fixture": 0.5, # nothing downstream consumes fixtures; false ones are pure noise
}

# Downstream routing hint for the Role 9 handoff. Openings get projected onto
# wall centerlines; symbols are informational only.
OPENING_CLASSES = {"door", "window"}
SYMBOL_CLASSES = {"stair", "fixture"}


def validate():
    """Fail fast if the taxonomy tables ever drift out of sync."""
    assert set(CLASS_BETA) == set(CLASSES), "CLASS_BETA keys must match CLASSES"
    assert OPENING_CLASSES | SYMBOL_CLASSES == set(CLASSES), "routing must cover all classes"
    assert OPENING_CLASSES & SYMBOL_CLASSES == set(), "a class cannot be both opening and symbol"
    return True


if __name__ == "__main__":
    validate()
    print("taxonomy OK:", CLASSES)
