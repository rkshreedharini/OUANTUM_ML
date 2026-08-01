# Perception (Role 7) → Context Engine — interface contract

**Producer:** Perception pod, Role 7 (Symbol/Object Detection)
**Consumer:** Context & Geometry pod (the Context Engine)
**Authority:** BIM-Vision ML Engineering Workflow v1.0, §4.2 (schema), §4.3 (fusion)

This file exists so the integration conversation happens once, here, rather than
five times in chat. If you need a field this doesn't expose, that's a schema gap
to raise — not a reason to read raw model output. (Workflow §4.1.)

---

## What Role 7 emits

`infer.py` writes one JSON per drawing:

```json
{
  "schema_version": "1.0",
  "producer": {"pod": "Perception", "role": 7, "role_name": "Symbol/Object Detection"},
  "drawing_id": "...",
  "source_image": "plan_0001.png",
  "units": "normalized_xywh",
  "scale_resolved": false,
  "opening_candidates": [
    {
      "type": "door",
      "subtype": null,
      "bbox_xywhn": [0.412, 0.330, 0.021, 0.019],
      "raw_score": 0.8113,
      "provenance": {
        "model_name": "best.pt",
        "model_version": "0.1.0",
        "confidence": 0.7042,
        "raw_ref": "plan_0001.png#det17"
      }
    }
  ],
  "symbols": [ /* stair / fixture, same shape */ ],
  "meta": {
    "thresholds_applied": {"door": 0.35, "window": 0.46, "stair": 0.48, "fixture": 0.56},
    "dropped_below_threshold": 41,
    "calibrated": true,
    "uncalibrated_classes": []
  }
}
```

---

## Three rules this boundary enforces

### 1. `provenance` field names are frozen

They match `Provenance` in workflow §4.2 exactly:

| field | type | meaning |
|---|---|---|
| `model_name` | str | weights file / model identifier |
| `model_version` | str | semver, bumped every retrain |
| `confidence` | float 0–1 | **calibrated** — see rule 2 |
| `raw_ref` | str | pointer to the raw detection, never discarded (§4.3 step 1) |

Do not rename these. Downstream reads them literally.

### 2. `confidence` is calibrated, never a raw score

The schema comment is explicit: *"0-1, calibrated, not raw softmax."* A raw
YOLO objectness×class score is not calibrated — a detector emitting 0.9 may be
right 70% of the time. Since the Context Engine gates human review on confidence
(§4.3 step 6), an uncalibrated number silently mis-routes the review queue.

`evaluate.py` fits per-class **Platt scaling** on the val split and reports
Expected Calibration Error before and after. On synthetic overconfident data ECE
drops ~0.23 → ~0.06. The raw detector score is preserved as `raw_score` for audit.

If a class has too few val examples to calibrate, it is passed through uncalibrated
and named in `meta.uncalibrated_classes` — surfaced, never silent.

### 3. No millimetres. Ever.

Role 7 works in pixels. `scale_mm_per_px` is resolved by the Context Engine from
Role 8's signals (§4.3 step 4), and the workflow is explicit that *"nothing
downstream should ever silently guess a scale."*

So this contract emits `units: "normalized_xywh"` and `scale_resolved: false`.
The Context Engine converts to `width_mm`, `height_mm`, `position_on_wall_mm`
once scale is known and agreed by two independent signals.

---

## What Role 7 deliberately does NOT emit

| `Opening` field | Who fills it | Why not us |
|---|---|---|
| `id` (UUID) | Context Engine | IDs are assigned at freeze time, not detection time |
| `host_wall_id` | Context Engine | Requires wall centerlines from Role 5/6 segmentation (§4.3 step 3) |
| `position_on_wall_mm` | Context Engine | Requires both a host wall and a resolved scale |
| `width_mm` / `height_mm` | Context Engine | Requires resolved scale |
| `sill_height_mm` | Context Engine | Not observable from a 2D plan-view box |

We emit **candidates**. The Context Engine decides hosting. An opening is never a
free-floating box in the frozen context — it's always a property of a wall — but
making it one is *their* step, not ours.

---

## Class routing

| our class | routes to | becomes |
|---|---|---|
| `door` | `opening_candidates` | `Opening(type="door")` |
| `window` | `opening_candidates` | `Opening(type="window")` |
| `stair` | `symbols` | informational; vertical connector hint for multi-storey stacking (§5.4) |
| `fixture` | `symbols` | informational only; nothing structural consumes it |

`Opening.type` in the frozen schema is `Literal["door", "window"]` — which is
exactly why stairs and fixtures cannot be openings and route separately.

---

## Versioning

`schema_version` is bumped on any breaking change to this shape. Consumers should
assert on it. `model_version` is bumped every retrain so a context object can
always be traced to the weights that produced it (§4.3 step 8, active-learning loop).
