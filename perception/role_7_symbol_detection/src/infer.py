"""Inference + Perception -> Context Engine handoff (Role 7 output boundary).

*** Needs trained weights (GPU-produced). *** The handoff-shaping logic
(`filter_and_shape`) is pure stdlib and testable without torch.

THREE CONTRACT RULES THIS FILE ENFORCES (workflow doc S4.2 / S4.3):

1. `provenance` uses the EXACT frozen field names -- model_name, model_version,
   confidence, raw_ref. Downstream reads this literally; renaming breaks them.

2. `confidence` is CALIBRATED (Platt-scaled on val), never the raw detector
   score. The Context Engine's confidence gating assumes the number means what
   it says. Raw score is kept alongside as `raw_score` for audit.

3. NO MILLIMETRES. Role 7 works in pixels. Scale (mm-per-px) is resolved by the
   Context Engine from Role 8's signals (S4.3 step 4), and "nothing downstream
   should ever silently guess a scale." So we emit normalized boxes and set
   `scale_resolved: false`. The Context Engine converts to width_mm /
   position_on_wall_mm once scale is known.

Likewise we do NOT emit host_wall_id or position_on_wall_mm: attaching an
opening to a wall centerline is the Context Engine's job (S4.3 step 3). We emit
*candidates*; it decides hosting.

Usage:
    python src/infer.py --weights best.pt --thresholds eval_out/thresholds.json \
        --calibration eval_out/calibration.json --image plan.png --out handoff.json
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy      # noqa: E402
import calibration   # noqa: E402

HANDOFF_SCHEMA_VERSION = "1.0"


def filter_and_shape(detections, thresholds, model_name, model_version,
                     calib=None, drawing_id=None, source_image=None):
    """
    detections: [{cls, raw_score, bbox_xywhn, subtype, raw_ref}, ...]
    thresholds: {cls: cutoff}          -- applied to the CALIBRATED confidence
    calib:      per-class Platt params from calibration.fit_all (or None)

    Returns the Perception->Context handoff dict.
    """
    openings, symbols, dropped = [], [], 0
    uncalibrated_classes = set()

    for d in detections:
        cls = d["cls"]
        raw = float(d["raw_score"])
        if calib:
            conf = calibration.calibrate(raw, cls, calib)
            if calib.get(cls, {}).get("degenerate", True):
                uncalibrated_classes.add(cls)
        else:
            conf = raw
            uncalibrated_classes.add(cls)

        cutoff = thresholds.get(cls, 0.5)
        if conf < cutoff:
            dropped += 1
            continue

        rec = {
            "type": cls,
            "subtype": d.get("subtype"),
            "bbox_xywhn": [round(float(v), 6) for v in d["bbox_xywhn"]],
            "raw_score": round(raw, 4),
            "provenance": {                       # EXACT contract field names
                "model_name": model_name,
                "model_version": model_version,
                "confidence": round(float(conf), 4),   # calibrated
                "raw_ref": d.get("raw_ref"),
            },
        }
        # door/window -> Opening candidates; stair/fixture -> informational
        (openings if cls in taxonomy.OPENING_CLASSES else symbols).append(rec)

    return {
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "producer": {"pod": "Perception", "role": 7,
                     "role_name": "Symbol/Object Detection"},
        "drawing_id": drawing_id,
        "source_image": source_image,
        # units contract: normalized [0,1] xywh in IMAGE space. NOT millimetres.
        "units": "normalized_xywh",
        "scale_resolved": False,
        "scale_note": ("Role 7 does not resolve scale. Context Engine converts to "
                       "mm using Role 8's scale signals (workflow S4.3 step 4)."),
        "opening_candidates": openings,   # -> Context Engine attaches host_wall_id
        "symbols": symbols,               # stair/fixture, informational
        "meta": {
            "model_name": model_name,
            "model_version": model_version,
            "thresholds_applied": thresholds,
            "dropped_below_threshold": dropped,
            "calibrated": bool(calib) and not uncalibrated_classes,
            "uncalibrated_classes": sorted(uncalibrated_classes),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--thresholds", required=True)
    ap.add_argument("--calibration", default=None, help="calibration.json from evaluate.py")
    ap.add_argument("--image", required=True)
    ap.add_argument("--imgsz", type=int, default=1024)
    ap.add_argument("--out", default="handoff.json")
    ap.add_argument("--model-version", default="0.1.0")
    ap.add_argument("--drawing-id", default=None)
    args = ap.parse_args()

    thresholds = json.load(open(args.thresholds))
    calib = calibration.load(args.calibration) if args.calibration else None
    if calib is None:
        print("WARNING: no --calibration given; provenance.confidence will be the "
              "RAW score, which violates the 'calibrated, not raw softmax' contract. "
              "Run evaluate.py first.")

    from ultralytics import YOLO
    model = YOLO(args.weights)
    res = model.predict(args.image, imgsz=args.imgsz, conf=0.001, verbose=False)[0]

    dets = []
    for i, b in enumerate(res.boxes):
        cid = int(b.cls)
        dets.append({
            "cls": taxonomy.ID_TO_CLASS[cid],
            "raw_score": float(b.conf),
            "bbox_xywhn": b.xywhn[0].tolist(),
            "subtype": None,   # fine label is not recoverable from a 4-class head
            "raw_ref": f"{os.path.basename(args.image)}#det{i}",
        })

    handoff = filter_and_shape(
        dets, thresholds, os.path.basename(args.weights), args.model_version,
        calib=calib, drawing_id=args.drawing_id,
        source_image=os.path.basename(args.image))
    json.dump(handoff, open(args.out, "w"), indent=2)
    print(f"wrote {args.out}: {len(handoff['opening_candidates'])} opening candidates, "
          f"{len(handoff['symbols'])} symbols, "
          f"{handoff['meta']['dropped_below_threshold']} dropped, "
          f"calibrated={handoff['meta']['calibrated']}")


if __name__ == "__main__":
    main()
