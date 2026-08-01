# Perception Pod

Perception modules for the BIM-Vision pipeline. Each module reads architectural
floor plans and produces structured output for the **Context Engine**, which
fuses everything into one validated building description before any 3D geometry
is generated.

## Roles

| Directory | Role | Description |
|---|---|---|
| [`role_5_segmentation/`](role_5_segmentation) | Role 5 — Wall/room segmentation | DeepLabV3+ / ResNet-50 semantic segmentation baseline on CubiCasa5K. Training script, ground-truth masks, qualitative results. |
| [`role_7_symbol_detection/`](role_7_symbol_detection) | Role 7 — Symbol detection | YOLOv11 detector for door/window/stair/fixture. **mAP@0.5 = 0.88.** Five dataset adapters, per-class calibrated thresholds, contract-compliant handoff. |
| [`role_8_ocr/`](role_8_ocr) | Role 8 — OCR + scale detection | Multi-angle EasyOCR with CLAHE preprocessing, deterministic room/dimension/scale parsing, DXF geometry merge, structured JSON export. |
| [`role_9_raster_to_vector/`](role_9_raster_to_vector) | Role 9 — Raster to vector | Classical and learned raster-to-vector backends behind a shared interface. |

Role 6 (segmentation upgrade — dual-branch multi-attention) begins once Role 5's
baseline plateaus.

## How the modules fit together

```
floor plan image
      │
      ├─► Role 5  segmentation  ──► wall / room masks ───┐
      ├─► Role 7  detection     ──► door / window boxes ─┤
      ├─► Role 8  OCR + scale   ──► labels, dimensions ──┼──► CONTEXT ENGINE ──► 3D / IFC
      └─► Role 9  raster→vector ──► clean polygons ──────┘     (fuse, validate,
                                                                freeze)
```

Each module emits raw perception output only. Fusion, scale resolution, and
validation belong to the Context Engine — **no perception module resolves scale
or writes geometry directly.**

## Setup

Each module has its own dependencies; install from the `requirements.txt` inside
the relevant directory.

## Large files

Trained weights above GitHub's 100 MB per-file limit are not committed. Role 5's
`best_model.pth` (107 MB) is available on request or reproducible from its
training script.
