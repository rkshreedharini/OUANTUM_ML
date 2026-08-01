# QUANTUM_ML — BIM-Vision

Machine learning pipeline that turns architectural floor plans into structured
3D building models (IFC). Plans are read by perception models, fused into one
validated building description by the Context Engine, and then converted into
geometry and visualization.

## Pipeline

```
floor plan / CAD / scan
          │
          ▼
   ┌─────────────┐
   │ PERCEPTION  │  segmentation · symbol detection · OCR+scale · raster→vector
   └──────┬──────┘
          ▼
   ┌──────────────────┐
   │ CONTEXT ENGINE   │  fuse → resolve scale → validate → human review → FREEZE
   └──────┬───────────┘
          ▼
   ┌──────────────────┐
   │ 3D / BIM / IFC   │  extrusion · openings · storeys · IFC authoring
   └──────────────────┘
```

The Context Engine is the one contract every downstream stage consumes. No
perception module writes geometry or resolves scale directly.

## Contents

| Directory | Pod | Description |
|---|---|---|
| [`perception/`](perception) | Perception | Roles 5, 7, 8, 9 — wall/room segmentation, symbol detection, OCR + scale detection, raster-to-vector. See its [README](perception/README.md). |
| [`Context_and_Geometry_Assignment/`](Context_and_Geometry_Assignment) | Context & Geometry | Context Engine: fusion, scale resolution, validation gates, review queue, and geometry/IFC generation. |
| [`05/`](05) | — | Additional assignment material. |

Data & Annotation pod work (dataset curation, Label Studio tooling, active
learning loop) lives in its own repository.

## Setup

Each module manages its own dependencies. Install from the `requirements.txt`
inside the relevant directory.

## Note on large files

GitHub rejects any single file over 100 MB. Trained model weights exceeding that
limit are not committed; each module's README states how to obtain or regenerate
them.
