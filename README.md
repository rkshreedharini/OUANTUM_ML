# Fusion Engineer Module

## Overview

This module is responsible for converting detected wall masks into a structured building context for BIM integration.

### Features

- Skeletonization of wall masks
- Wall centerline extraction
- Orthogonal wall snapping
- OCR room label assignment
- Door/window projection onto nearest wall
- Scale estimation
- Unified building context generation

## Folder Structure

```
bim/
└── context/
    ├── fusion.py
    ├── scale.py
    └── schema.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Run Demo

```bash
python main.py
```

## Output

The pipeline returns a building context dictionary containing:

- centerlines
- room_labels
- openings
- scale