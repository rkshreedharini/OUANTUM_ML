# Project 2: Point-Cloud-to-Context & Cloud2BIM Engine

**Pod**: Reality Capture (Optional Module)  
**Role**: Role 17 - Point-Cloud-to-Context Engineer  
**Tech Stack**: Node.js, Express v4 (`tsx`, `esbuild`), `@google/genai` (v2.4.0 using `gemini-3.6-flash`), TypeScript (~5.8), React 18, Vite, Three.js, Open3D, Point Transformer V3 / KPConv, `IfcOpenShell`.

---

## 🎯 Overview & Responsibilities
This repository contains the standalone **Point-Cloud-to-BuildingContext** extraction engine for **BIM-Vision AI**.

### Core Responsibilities
1. **Point Semantic Segmentation (PTv3 / KPConv)**:
   - Deep point neural network inference classifying 3D point clouds into architectural categories (`IfcWallStandardCase`, `IfcSlab`, `IfcColumn`, `IfcBeam`, `IfcWindow`, `IfcDoor`, `IfcDuctSegment`, `IfcPipeSegment`).
2. **Cloud2BIM Planar Region & Primitive Extraction**:
   - Open3D RANSAC plane surface equation fitting (`distanceThreshold = 2.0 cm`).
   - Volumetric primitive bounding box calculation.
   - **Mandatory Schema Integration**: Every extracted primitive is automatically assigned metadata attribute `source_type = "point_cloud"`.
3. **IfcOpenShell Standard IFC Exporter**:
   - Automatic generation of valid ISO 10303-21 standard IFC files (IFC4 and IFC2x3 schemas).
   - Support for Levels of Development from LOD 100 to LOD 400.
4. **Gemini 3.6 Flash AI Assistance**:
   - Integrated via `@google/genai` v2.4.0.
   - Geometry boundary analysis, plane fitting residual inspection, and IFC class verification.

---

## 📁 Repository Structure
```text
project-2-pointcloud-context-engine/
├── server.ts                         # Express app & Gemini AI API endpoints
├── pipeline/
│   ├── semantic_segmentation.py      # Python Point Transformer V3 / KPConv wrapper
│   ├── cloud2bim_planar_fit.py       # Python Open3D RANSAC plane fitting & primitive extractor
│   └── ifc_exporter.py               # Python IfcOpenShell IFC file generator
├── src/
│   ├── App.tsx                       # Main React web portal
│   ├── components/
│   │   ├── layout/                   # Header & Sidebar navigation
│   │   ├── viewer/
│   │   │   └── PointCloudContext3DViewer.tsx # 3D WebGL semantic class & IFC wireframe visualizer
│   │   └── pages/                    # Workbench pages (Dashboard, PTv3, RANSAC, Primitives, IFC Export, AI)
│   ├── data/                         # Mock point cloud & Cloud2BIM dataset
│   └── types/                        # TypeScript type definitions
├── .env                              # API secrets (GEMINI_API_KEY)
├── package.json                      # Node dependencies & scripts
├── tsconfig.json                     # TypeScript configuration
└── vite.config.ts                    # Vite dev server configuration
```

---

## 🚀 API Endpoints

- `GET /api/health`: Health status.
- `POST /api/context/segment`: Run PTv3 / KPConv point semantic classification.
- `POST /api/context/ransac-fit`: Execute Cloud2BIM planar surface RANSAC fitting.
- `POST /api/context/extract-ifc-primitives`: Generate IFC-shaped primitives with `source_type = point_cloud`.
- `POST /api/context/export-ifc`: Convert primitives into valid IFC4 / IFC2x3 standard file string.
- `POST /api/gemini/analyze`: Gemini 3.6 Flash automated context geometry & planarity quality report.
- `POST /api/gemini/chat`: Interactive Cloud2BIM AI assistant chat.

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Set Environment Variables
Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
PORT=3001
```

### 3. Run the Development Server
```bash
npm run dev
```
Open `http://localhost:3001` in your browser.

### 4. Run the Express Backend Directly
```bash
npm run server
```
