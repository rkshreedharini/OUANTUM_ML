import { PhotogrammetryImage, ColmapStats, GaussianSplatStats, ActivityLog } from '../types/photogrammetry';

export const MOCK_IMAGES: PhotogrammetryImage[] = [
  {
    id: 'img-001',
    name: 'DJI_20260725_001.JPG',
    url: 'https://images.unsplash.com/photo-1541888946425-d0fbb186a5b3?auto=format&fit=crop&w=800&q=80',
    size: '14.8 MB',
    resolution: '5472 x 3648 (20 MP)',
    exif: {
      camera: 'DJI FC6310 (Phantom 4 Pro V2)',
      focalLength: '8.8 mm (24mm equiv)',
      iso: 100,
      aperture: 'f/4.0',
      shutterSpeed: '1/1000s',
      gps: { lat: 37.7749, lng: -122.4194, alt: 52.4 }
    },
    keypointsCount: 38420,
    qualityScore: 98,
    status: 'matched'
  },
  {
    id: 'img-002',
    name: 'DJI_20260725_002.JPG',
    url: 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80',
    size: '15.1 MB',
    resolution: '5472 x 3648 (20 MP)',
    exif: {
      camera: 'DJI FC6310 (Phantom 4 Pro V2)',
      focalLength: '8.8 mm (24mm equiv)',
      iso: 100,
      aperture: 'f/4.0',
      shutterSpeed: '1/1000s',
      gps: { lat: 37.7751, lng: -122.4192, alt: 52.6 }
    },
    keypointsCount: 36150,
    qualityScore: 96,
    status: 'matched'
  },
  {
    id: 'img-003',
    name: 'SITE_CANON_EOS_048.CR3',
    url: 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=800&q=80',
    size: '28.4 MB',
    resolution: '6720 x 4480 (30 MP)',
    exif: {
      camera: 'Canon EOS R5',
      focalLength: '35.0 mm',
      iso: 200,
      aperture: 'f/5.6',
      shutterSpeed: '1/500s',
      gps: { lat: 37.7753, lng: -122.4189, alt: 14.2 }
    },
    keypointsCount: 44100,
    qualityScore: 99,
    status: 'matched'
  },
  {
    id: 'img-004',
    name: 'SITE_IPHONE_SCAN_102.HEIC',
    url: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
    size: '8.2 MB',
    resolution: '4032 x 3024 (12 MP)',
    exif: {
      camera: 'iPhone 15 Pro LiDAR',
      focalLength: '6.86 mm',
      iso: 80,
      aperture: 'f/1.78',
      shutterSpeed: '1/1200s',
      gps: { lat: 37.7748, lng: -122.4195, alt: 12.1 }
    },
    keypointsCount: 28900,
    qualityScore: 94,
    status: 'matched'
  }
];

export const MOCK_COLMAP_STATS: ColmapStats = {
  totalImages: 48,
  registeredCameras: 48,
  matchedPairsCount: 1128,
  sparsePointsCount: 124500,
  sparseRmseMm: 1.84,
  densePointsCount: 8450200,
  denseDensityPtsPerM3: 450000,
  reconstructionTimeSec: 142.5
};

export const MOCK_SPLAT_STATS: GaussianSplatStats = {
  numGaussians: 1520000,
  iterationsCompleted: 30000,
  targetIterations: 30000,
  psnrDb: 34.25,
  ssim: 0.945,
  lpips: 0.048,
  renderFps: 95.4,
  shDegree: 3,
  guardrailAcknowledged: true
};

export const MOCK_ACTIVITY_LOGS: ActivityLog[] = [
  {
    id: 'log-01',
    timestamp: '00:24:10',
    stage: 'SIFT Extractor',
    message: 'Extracted 1,732,800 SIFT keypoints across 48 UAV site images.',
    type: 'success'
  },
  {
    id: 'log-02',
    timestamp: '00:24:18',
    stage: 'COLMAP Mapper',
    message: 'Bundle Adjustment converged: Mean Reprojection Residual = 0.42 px (1.84 mm RMS error).',
    type: 'success'
  },
  {
    id: 'log-03',
    timestamp: '00:24:45',
    stage: 'PatchMatch MVS',
    message: 'Dense Point Cloud fused: 8,450,200 points created with RGB & normal vectors.',
    type: 'info'
  },
  {
    id: 'log-04',
    timestamp: '00:25:02',
    stage: '3DGS Trainer',
    message: '3D Gaussian Splatting trained: 1.52M Gaussians at 34.25 dB PSNR (Visualization Only Mode).',
    type: 'success'
  }
];
