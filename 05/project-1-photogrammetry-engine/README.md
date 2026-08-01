# Project 1: Photogrammetry & 3D Gaussian Splatting Engine

**Pod**: Reality Capture (Optional Module)  
**Role**: Role 16 - Photogrammetry Engineer  
**Tech Stack**: Node.js, Express v4 (`tsx`, `esbuild`), `@google/genai` (v2.4.0 using `gemini-3.6-flash`), TypeScript (~5.8), React 18, Vite, Three.js, COLMAP (SfM + MVS), `gsplat` / `Nerfstudio`.

---

## 🎯 Overview & Responsibilities
This repository contains the standalone photogrammetry and photoreal rendering engine for **BIM-Vision AI**.

### Core Responsibilities
1. **Structure-from-Motion (SfM) + Multi-View Stereo (MVS)**:
   - SIFT keypoint extraction and guided feature matching.
   - Camera calibration and pose estimation via COLMAP incremental mapper.
   - PatchMatch dense MVS point cloud reconstruction with calibrated metric scale (1.84 mm RMS residual).
   - Point cloud filtering and PLY / LAS export.
2. **3D Gaussian Splatting (3DGS) Photoreal Visualization Engine**:
   - `gsplat` / `Nerfstudio` pipeline integration.
   - Spherical Harmonics degree 0-3 optimization.
   - Real-time WebGL canvas viewer with dual rendering mode.
   - **Dimensional Guardrail**: 3D Gaussian Splatting is strictly enforced as a visualization-only layer for client demos. It is never used as a source of metric or dimensional truth.
3. **Gemini 3.6 Flash AI Assistance**:
   - Integrated via `@google/genai` v2.4.0.
   - Camera calibration diagnostics, feature overlap calculation, and SIFT parameter tuning.

---

## 📁 Repository Structure
```text
project-1-photogrammetry-engine/
├── server.ts                         # Express app & Gemini AI API endpoints
├── pipeline/
│   ├── colmap_sfm_mvs.py             # Python COLMAP SfM & MVS pipeline wrapper
│   └── gaussian_splatting.py         # Python 3D Gaussian Splatting trainer wrapper
├── src/
│   ├── App.tsx                       # Main React web portal
│   ├── components/
│   │   ├── layout/                   # Header & Sidebar navigation
│   │   ├── viewer/
│   │   │   └── SplatPointCloudViewer.tsx # Dual-mode Three.js WebGL 3D visualizer
│   │   └── pages/                    # Workbench pages (Dashboard, Photo Ingestion, SfM/MVS, 3DGS, AI Diagnostics)
│   ├── data/                         # Mock photogrammetry dataset & stats
│   └── types/                        # TypeScript type definitions
├── .env                              # API secrets (GEMINI_API_KEY)
├── package.json                      # Node dependencies & scripts
├── tsconfig.json                     # TypeScript configuration
└── vite.config.ts                    # Vite dev server configuration
```

---

## 🚀 API Endpoints

- `GET /api/health`: Health status.
- `POST /api/photogrammetry/upload`: Ingest drone/phone photos and EXIF data.
- `POST /api/photogrammetry/reconstruct`: Execute COLMAP SfM keypoint matching & MVS dense point cloud generation.
- `POST /api/photogrammetry/splat`: Train 3D Gaussian Splat model (`gsplat` / `Nerfstudio`).
- `POST /api/gemini/analyze`: Gemini 3.6 Flash automated photo calibration & overlap quality report.
- `POST /api/gemini/chat`: Interactive photogrammetry assistant chat.

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
PORT=3000
```

### 3. Run the Development Server
```bash
npm run dev
```
Open `http://localhost:3000` in your browser.

### 4. Run the Express Backend Directly
```bash
npm run server
```
