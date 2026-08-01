export type NavTab = 
  | 'dashboard' 
  | 'upload' 
  | 'sfm_mvs' 
  | 'gaussian_splatting' 
  | 'ai_diagnostics' 
  | 'settings';

export interface PhotogrammetryImage {
  id: string;
  name: string;
  url: string;
  size: string;
  resolution: string;
  exif: {
    camera: string;
    focalLength: string;
    iso: number;
    aperture: string;
    shutterSpeed: string;
    gps?: { lat: number; lng: number; alt: number };
  };
  keypointsCount: number;
  qualityScore: number; // 0 - 100
  status: 'indexed' | 'matched' | 'failed';
}

export interface CameraPose {
  id: string;
  imageId: string;
  position: { x: number; y: number; z: number };
  rotation: { x: number; y: number; z: number; w: number };
  reprojectionErrorPx: number;
  inlierRatio: number;
}

export interface ColmapStats {
  totalImages: number;
  registeredCameras: number;
  matchedPairsCount: number;
  sparsePointsCount: number;
  sparseRmseMm: number;
  densePointsCount: number;
  denseDensityPtsPerM3: number;
  reconstructionTimeSec: number;
}

export interface GaussianSplatStats {
  numGaussians: number;
  iterationsCompleted: number;
  targetIterations: number;
  psnrDb: number;
  ssim: number;
  lpips: number;
  renderFps: number;
  shDegree: number;
  guardrailAcknowledged: boolean;
}

export interface ActivityLog {
  id: string;
  timestamp: string;
  stage: 'SIFT Extractor' | 'COLMAP Mapper' | 'PatchMatch MVS' | '3DGS Trainer' | 'Gemini AI';
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}
