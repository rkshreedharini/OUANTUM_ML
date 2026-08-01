"""Contract tests -- assert the handoff matches the FROZEN BuildingContext
schema field-for-field. These run on CPU with no torch and no weights.

Run:  python tests/test_contract.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import taxonomy       # noqa: E402
import calibration    # noqa: E402
from infer import filter_and_shape  # noqa: E402

# exact field names from workflow doc S4.2 class Provenance
REQUIRED_PROVENANCE_FIELDS = {"model_name", "model_version", "confidence", "raw_ref"}
FORBIDDEN_MM_KEYS = {"width_mm", "height_mm", "position_on_wall_mm",
                     "sill_height_mm", "host_wall_id"}

failures = []


def check(cond, msg):
    if cond:
        print(f"  PASS  {msg}")
    else:
        print(f"  FAIL  {msg}")
        failures.append(msg)


def fake_detections():
    dets = []
    for i, cls in enumerate(taxonomy.CLASSES):
        for k in range(3):
            dets.append({
                "cls": cls,
                "raw_score": 0.55 + 0.1 * k,
                "bbox_xywhn": [0.4, 0.3, 0.02, 0.02],
                "subtype": "double_door" if cls == "door" else None,
                "raw_ref": f"plan.png#det{i}{k}",
            })
    return dets


def main():
    # build a real calibrator so the calibrated path is exercised
    import random
    rng = random.Random(0)
    scored = {c: [(min(0.999, abs(rng.gauss(0.85, 0.1))), True) for _ in range(200)]
                 + [(min(0.999, abs(rng.gauss(0.7, 0.15))), False) for _ in range(150)]
              for c in taxonomy.CLASSES}
    calib = calibration.fit_all(scored)

    thresholds = {"door": 0.30, "window": 0.30, "stair": 0.30, "fixture": 0.30}
    h = filter_and_shape(fake_detections(), thresholds, "best.pt", "0.1.0",
                         calib=calib, drawing_id="dwg-1", source_image="plan.png")

    print("\n[1] top-level shape")
    for k in ("schema_version", "producer", "units", "scale_resolved",
              "opening_candidates", "symbols", "meta"):
        check(k in h, f"has '{k}'")

    print("\n[2] no-millimetres rule (scale is the Context Engine's job)")
    check(h["units"] == "normalized_xywh", "units == normalized_xywh")
    check(h["scale_resolved"] is False, "scale_resolved is False")
    all_recs = h["opening_candidates"] + h["symbols"]
    leaked = {k for r in all_recs for k in r} & FORBIDDEN_MM_KEYS
    check(not leaked, f"no mm/host fields leaked (found: {leaked or 'none'})")

    print("\n[3] provenance field names match frozen schema")
    check(bool(all_recs), "produced at least one detection")
    for r in all_recs:
        p = r["provenance"]
        missing = REQUIRED_PROVENANCE_FIELDS - set(p)
        extra = set(p) - REQUIRED_PROVENANCE_FIELDS
        check(not missing, f"provenance has all required fields (missing: {missing or 'none'})")
        check(not extra, f"provenance has no extra fields (extra: {extra or 'none'})")
        break  # shape is uniform

    print("\n[4] confidence is calibrated, not the raw score")
    check(h["meta"]["calibrated"] is True, "meta.calibrated is True")
    differs = any(abs(r["provenance"]["confidence"] - r["raw_score"]) > 1e-6 for r in all_recs)
    check(differs, "calibrated confidence differs from raw_score")
    check(all(0.0 <= r["provenance"]["confidence"] <= 1.0 for r in all_recs),
          "all confidences in [0,1]")
    check(all("raw_score" in r for r in all_recs), "raw_score preserved for audit")

    print("\n[5] class routing: only door/window may be opening candidates")
    op_types = {r["type"] for r in h["opening_candidates"]}
    sym_types = {r["type"] for r in h["symbols"]}
    check(op_types <= {"door", "window"}, f"opening_candidates types {op_types} subset of door/window")
    check(sym_types <= {"stair", "fixture"}, f"symbols types {sym_types} subset of stair/fixture")
    check(op_types | sym_types == set(taxonomy.CLASSES), "every class routed somewhere")

    print("\n[6] thresholds actually drop things")
    h2 = filter_and_shape(fake_detections(), {c: 0.99 for c in taxonomy.CLASSES},
                          "best.pt", "0.1.0", calib=calib)
    check(h2["meta"]["dropped_below_threshold"] == 12, "high thresholds drop all 12 detections")
    check(not h2["opening_candidates"] and not h2["symbols"], "nothing survives a 0.99 cutoff")

    print("\n[7] uncalibrated path is surfaced, not silent")
    h3 = filter_and_shape(fake_detections(), thresholds, "best.pt", "0.1.0", calib=None)
    check(h3["meta"]["calibrated"] is False, "meta.calibrated False when no calibrator")
    check(set(h3["meta"]["uncalibrated_classes"]) == set(taxonomy.CLASSES),
          "all classes listed as uncalibrated")

    print("\n" + "=" * 52)
    if failures:
        print(f"{len(failures)} CONTRACT TEST(S) FAILED")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("ALL CONTRACT TESTS PASSED")


if __name__ == "__main__":
    main()
