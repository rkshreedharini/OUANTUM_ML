# BIM-Vision — Perception Pod, Role 7: Symbol/Object Detection

YOLOv11 detector for **door, window, stair, fixture** on architectural floor
plans, with a contract-compliant handoff to the Context Engine.

**Status: deliverable met.** Trained on CubiCasa5k (Phase 0 public dataset,
1,200 plans, yolo11s @ imgsz 1024, 50 epochs):

| metric | value |
|---|---|
| **mAP@0.5 (all classes)** | **0.88** |
| door recall / precision | 0.87 / 0.81 |
| window recall / precision | 0.92 / 0.83 |
| stair recall / precision | 0.83 / 0.91 |
| fixture recall / precision | 0.77 / 0.92 |
| per-class mAP@0.5:0.95 | 0.64 – 0.73 |
| calibration (ECE after Platt) | ≤ 0.012 all classes |

Note the deliberate asymmetry: doors/windows tuned for **recall** (a missed
opening becomes a solid wall in the IFC), fixtures for **precision** (false
ones are pure noise) — per the assignment's "weight doors/windows above
furniture." All metrics tracked in MLflow every run.

**Position in the system:** Perception pod (Roles 5–9). Upstream: Data &
Annotation pod. Downstream: **Context & Geometry pod** (the Context Engine).
Interface spec: `docs/CONTRACT.md`.

---

## When the real dataset arrives, one command changes

```bash
python src/ingest.py --input <their_folder> --out yolo_dataset
```

`ingest.py` auto-detects the annotation format and normalizes into one internal
schema. Supported and tested:

| format | detected by | adapter |
|---|---|---|
| **CubiCasa5k** | `model.svg` present | `adapters/cubicasa.py` |
| **Label Studio** | JSON export | `adapters/labelstudio.py` — built against the D&A pod's actual config; handles polygon AND rectangle doors/windows |
| **COCO** | json with `annotations`+`categories` | `adapters/coco.py` |
| **YOLO** | `data.yaml` or `labels/*.txt` | `adapters/yolo.py` |
| **Pascal VOC** | `*.xml` | `adapters/voc.py` |

Category names resolve in three tiers — exact (`class_map`), keyword
(`sliding_door`→door, `washingmachine`→fixture), or unmapped (reported, never
silently dropped). A new format is one adapter file; nothing downstream changes.

---

## Three data bugs this pipeline caught (and how)

All three were found by **drawing the ground-truth boxes on real plans and
looking** before spending GPU time — that check is now a mandatory notebook cell.

1. **SVG arc parsing.** Door swings are arcs; naive number-pairing reads arc
   radii/flags as coordinates. Door boxes measured 34% of image area instead of
   0.4%. Fixed with a real path parser (`src/svgpath.py`).
2. **SVG transforms ignored.** Groups position content via
   `transform="translate/rotate/matrix"`. Ignoring them displaced whole label
   clusters off the drawing — round-2 door recall was 0.02 because the model was
   taught that blank paper is a door. Fixed with full transform-stack
   composition in the adapter.
3. **PNG frame ≠ SVG canvas.** On 272/300 plans the SVG width/height attributes
   describe content extent, not the image frame; coordinates live in PNG pixel
   space. Normalizing by SVG dims stretched labels downward. Fixed by reading
   the PNG's IHDR header and normalizing by real pixel size.

Result of the fixes alone (same model, same data volume, same epochs):
**mAP@0.5 went 0.21 → 0.88.**

## Design decisions

**4 flat training classes** — fine labels (`double_door`, `toilet`) kept per-box
as `subtype` for provenance, not trained on. **Per-class F-beta thresholds** on
the val PR curve (beta 2.0 doors/windows, 1.0 stair, 0.5 fixture). **Calibrated
confidence** — per-class Platt scaling; the frozen schema demands "calibrated,
not raw softmax" and the Context Engine gates human review on this number.
**imgsz 1024** — window symbols are ~0.1% of image area; at 640 they vanish.
**No millimetres emitted** — scale is the Context Engine's job via Role 8's
signals; we emit `units: normalized_xywh`, `scale_resolved: false`.

## Layout

```
configs/base.yaml           every knob (classes, class_map, hyperparams, thresholds)
docs/CONTRACT.md            ★ Perception -> Context Engine interface spec
src/taxonomy.py             the 4 classes — single source of truth
src/schema.py               internal annotation format
src/classmap.py             category-name resolution (exact/keyword/unmapped)
src/svgpath.py              correct SVG path parsing (arcs, beziers)
src/adapters/               cubicasa, labelstudio, coco, yolo, voc + auto-detect
src/ingest.py               ONE command: any dataset -> training-ready
src/prep/                   balance report, stratified split, YOLO export
src/train.py                config-driven fine-tune, MLflow            [GPU]
src/calibration.py          Platt scaling + ECE / reliability tables
src/thresholds.py           F-beta per-class threshold selection
src/evaluate.py             per-class metrics, calibration, thresholds [GPU]
src/infer.py                new plan -> Context Engine handoff JSON    [GPU]
tests/test_contract.py      21 assertions: handoff matches frozen schema (CPU)
run_cpu_pipeline.py         end-to-end CPU smoke test (no torch/GPU/internet)
notebooks/BIM_Vision_Role7_Round3.ipynb   full Colab run incl. visual label check
```

## Quick start

```bash
pip install pyyaml
python run_cpu_pipeline.py     # full prep chain on synthetic data (CPU only)
python tests/test_contract.py  # 21 contract assertions
```

Full training: open `notebooks/BIM_Vision_Role7_Round3.ipynb` in Colab with a
T4 GPU and run top to bottom. **Do not skip the visual label-check cell.**

## Open items

1. **Data & Annotation pod:** first real annotation export pending; their schema
   currently lacks Stair/Fixture classes and has a polygon-vs-rectangle
   inconsistency for doors/windows (raised with the pod — adapter handles both).
2. **Leakage guard:** split is by image; set `split.group_key` to a building id
   if several drawings share a building.
3. **Metric naming:** per-class values logged as `mAP50_<cls>` are Ultralytics'
   `maps` (mAP@0.5:0.95); overall `mAP50_all` is true mAP@0.5.
4. Scale-up options: full 5k plans / yolo11m / RT-DETR comparison as GPU budget allows.
