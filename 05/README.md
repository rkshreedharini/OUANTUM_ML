# BIM-Vision AI • Reality Capture Pod Deliverables & Deployment Guide

This repository contains the complete deliverables for the **Reality Capture Pod** of **BIM-Vision AI**, split into two independent projects aligned with the team workplan:

1. **[Project 1: Photogrammetry & 3D Gaussian Splatting Engine](./project-1-photogrammetry-engine)** (Role 16 - Photogrammetry Engineer)
2. **[Project 2: Point-Cloud-to-Context & Cloud2BIM Engine](./project-2-pointcloud-context-engine)** (Role 17 - Point-Cloud-to-Context Engineer)

---

## 📐 Project Architecture & Role Matrix

| Project Directory | Assignment Role | Primary Core Engine | Key Output Deliverables | Port |
| :--- | :--- | :--- | :--- | :--- |
| **`project-1-photogrammetry-engine/`** | Role 16: Photogrammetry Engineer | COLMAP (SfM + MVS) & `gsplat`/`Nerfstudio` | Metrically accurate PLY point cloud & 3D Gaussian Splat model (Visualization mode) | `3000` |
| **`project-2-pointcloud-context-engine/`** | Role 17: Point-Cloud-to-Context Engineer | Point Transformer V3 / KPConv & Open3D RANSAC | Parametric IFC4 / IFC2x3 entities with `source_type = point_cloud` metadata | `3001` |

---

## 🛠️ Global Prerequisites

Before deploying either project, ensure your environment meets the following requirements:

- **Node.js**: `v18.x` or higher (LTS recommended)
- **Package Manager**: `npm` v9+ or `bun` / `yarn`
- **Python**: `v3.10` or higher (with `pip`, `venv`, PyTorch, Open3D, `IfcOpenShell`)
- **GPU Driver** (Optional for ML & 3DGS training): NVIDIA CUDA 11.8+ / 12.x
- **COLMAP Binary** (For Project 1 SfM processing): CUDA-enabled COLMAP build

---

## 🚀 Quick Local Deployment Guide

### Deploying Project 1: Photogrammetry Engine

```bash
# 1. Navigate to Project 1 directory
cd project-1-photogrammetry-engine

# 2. Install Node dependencies
npm install

# 3. Configure Environment Variables
cp .env.example .env
```

Edit `.env` and set your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=3000
COLMAP_PATH=colmap
NERFSTUDIO_PATH=ns-train
```

#### Run in Development Mode:
```bash
# Launches Vite dev server & Express backend API on http://localhost:3000
npm run dev
```

#### Run Express Backend Engine Directly:
```bash
npm run server
```

---

### Deploying Project 2: Point-Cloud-to-Context Engine

```bash
# 1. Navigate to Project 2 directory
cd project-2-pointcloud-context-engine

# 2. Install Node dependencies
npm install

# 3. Configure Environment Variables
cp .env.example .env
```

Edit `.env` and set your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=3001
PTv3_WEIGHTS_PATH=./weights/ptv3_scannet.pth
IFCOPENSHELL_SCHEMA=IFC4
```

#### Run in Development Mode:
```bash
# Launches Vite dev server & Express backend API on http://localhost:3001
npm run dev
```

#### Run Express Backend Engine Directly:
```bash
npm run server
```

---

## 🏭 Production Build & Deployment

To build single production bundles with bundled Vite static assets served directly via Express:

### Project 1 Production Deployment
```bash
cd project-1-photogrammetry-engine

# Build TypeScript & Vite assets into dist/
npm run build

# Start production Express server
NODE_ENV=production npm run start
```

### Project 2 Production Deployment
```bash
cd project-2-pointcloud-context-engine

# Build TypeScript & Vite assets into dist/
npm run build

# Start production Express server
NODE_ENV=production npm run start
```

---

## 🐳 Docker Containerization Deployment

Both projects can be containerized using Docker and launched simultaneously using Docker Compose.

### Dockerfile for Project 1 (`project-1-photogrammetry-engine/Dockerfile`)
```dockerfile
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/server.ts ./
COPY --from=builder /app/.env ./
EXPOSE 3000
CMD ["npx", "tsx", "server.ts"]
```

### Dockerfile for Project 2 (`project-2-pointcloud-context-engine/Dockerfile`)
```dockerfile
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/server.ts ./
COPY --from=builder /app/.env ./
EXPOSE 3001
CMD ["npx", "tsx", "server.ts"]
```

### Docker Compose Orchestration (`docker-compose.yml`)
Save the following `docker-compose.yml` in the root directory:

```yaml
version: '3.8'

services:
  photogrammetry-engine:
    build:
      context: ./project-1-photogrammetry-engine
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: unless-stopped

  context-engine:
    build:
      context: ./project-2-pointcloud-context-engine
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - PORT=3001
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: unless-stopped
```

#### Launch Services via Docker Compose:
```bash
GEMINI_API_KEY="your_gemini_api_key" docker-compose up -d --build
```

---

## ☁️ Cloud Deployment Guidelines (GCP / AWS / Render)

### 1. Google Cloud Run / AWS ECS
- Build container image per project using the Dockerfiles above.
- Deploy image to Cloud Run / ECS setting memory limit to minimum 4GB.
- Inject `GEMINI_API_KEY` as a Secret Manager environment variable.

### 2. Vercel / Railway / Render
- Set Root Directory to `project-1-photogrammetry-engine` or `project-2-pointcloud-context-engine`.
- Build Command: `npm run build`
- Start Command: `npm run start`

---

## 🔍 API Verification & Health Check

After deployment, verify server health and Gemini 3.6 Flash integration:

### Project 1 Verification:
```bash
curl http://localhost:3000/api/health
```
Expected output:
```json
{
  "status": "ok",
  "module": "Project 1: Photogrammetry & 3D Gaussian Splatting Engine",
  "role": "Role 16 - Photogrammetry Engineer",
  "version": "1.0.0"
}
```

### Project 2 Verification:
```bash
curl http://localhost:3001/api/health
```
Expected output:
```json
{
  "status": "ok",
  "module": "Project 2: Point-Cloud-to-Context Extraction Engine",
  "role": "Role 17 - Point-Cloud-to-Context Engineer",
  "version": "1.0.0"
}
```

---

## 📑 Deliverable Verification Checklist

- [x] **Project 1**: Role 16 Photogrammetry COLMAP SfM/MVS + 3DGS pipeline built.
- [x] **Project 1**: Enforced 3DGS visualization-only guardrails.
- [x] **Project 2**: Role 17 PTv3 / KPConv semantic classification pipeline built.
- [x] **Project 2**: Cloud2BIM RANSAC plane fitting with `source_type = point_cloud` metadata.
- [x] **Project 2**: IfcOpenShell IFC4 / IFC2x3 standard file exporter (LOD 100-400).
- [x] **AI Engine**: `@google/genai` v2.4.0 with model `gemini-3.6-flash` integrated into both Express backends.
