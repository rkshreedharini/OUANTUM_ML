# OCR + Scale Detection Module for BIM Vision

## Project Overview
This project extracts textual information from architectural floor plan images using computer vision and deterministic NLP, converting raw blueprints into structured JSON metadata for downstream BIM (Building Information Modeling) pipelines.

## Key Features
- **Multi-Angle OCR**: Uses EasyOCR with automatic rotation fallbacks ($0^\circ, 90^\circ, 180^\circ, 270^\circ$) to capture sideways room labels and vertical dimension lines.
- **Image Preprocessing**: Applies CLAHE contrast enhancement and cubic upscaling to boost text detection on thin, faint CAD lines.
- **Room Label Extraction**: Detects room names with substring deduplication to prevent redundant overlapping labels (e.g., suppressing `"DIN"` when `"DINING ROOM"` is present).
- **Deterministic Dimension Normalization**: Regex-based dimension parser that normalizes imperial/metric inputs and applies strict aspect-ratio/bounds filtering ($5\text{ft} \le \text{side} \le 35\text{ft}$) to eliminate line graphics noise.
- **Scale Signal Detection**: Identifies plan scale patterns (`SCALE: 1/4" = 1'-0"`, `1:100`).
- **DXF Geometry Extraction & Merging**: Integrates CAD line geometry with extracted OCR metadata.
- **Structured JSON Export**: Generates standardized JSON outputs adhering to BIM schema requirements.

## Technologies Used
- **Python 3.x**
- **EasyOCR** (Text Recognition)
- **OpenCV & NumPy** (Image Preprocessing & Transformations)
- **ezdxf** (DXF CAD Geometry Parsing)
- **Regular Expressions (`re`)** (Deterministic Unit & Pattern Normalization)

## Folder Structure

```text
OCR_Project/
│── datasets/          # Input floor plan images and DXF CAD files
│── output/            # Generated JSON and TXT metadata outputs
│── config.py          # Central project configuration and dataset paths
│── main.py            # Primary batch inference execution script
│── ocr_engine.py      # Preprocessing & EasyOCR multi-angle extraction engine
│── parser.py          # Deterministic room, dimension, and scale parsing logic
│── dxf_reader.py      # DXF CAD line and vector geometry parser
│── merge_data.py      # Integrates OCR text metadata with DXF vector geometry
│── requirements.txt   # Project dependencies