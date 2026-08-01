import { IfcPrimitive, SegmentationStats, RansacStats, ActivityLog } from '../types/cloud2bim';

export const MOCK_PRIMITIVES: IfcPrimitive[] = [
  {
    id: 'elem-wall-north',
    name: 'Exterior Shear Wall North',
    ifcType: 'IfcWallStandardCase',
    source_type: 'point_cloud',
    confidence: 99.2,
    dimensions: { length: 12.5, width: 0.3, height: 3.8 },
    position: { x: 0.0, y: 1.9, z: -4.8 },
    rotation: { x: 0, y: 0, z: 0 },
    planeEquation: [0.0, 0.0, 1.0, 4.8],
    lod: 'LOD 350',
    material: 'Reinforced Concrete (C35/45)',
    propertySets: {
      Pset_WallCommon: { IsExternal: true, LoadBearing: true, ThermalTransmittance: 0.28 },
      Pset_StructuralAnalysis: { MetricThicknessMm: 300 }
    },
    status: 'fitted'
  },
  {
    id: 'elem-col-se',
    name: 'Structural Column SE',
    ifcType: 'IfcColumn',
    source_type: 'point_cloud',
    confidence: 98.4,
    dimensions: { length: 0.45, width: 0.45, height: 3.8 },
    position: { x: 5.0, y: 1.9, z: 3.0 },
    rotation: { x: 0, y: 0, z: 0 },
    planeEquation: [1.0, 0.0, 0.0, -5.0],
    lod: 'LOD 350',
    material: 'RC Grade C40',
    propertySets: {
      Pset_ColumnCommon: { LoadBearing: true, Slope: 0.0 }
    },
    status: 'fitted'
  },
  {
    id: 'elem-col-sw',
    name: 'Structural Column SW',
    ifcType: 'IfcColumn',
    source_type: 'point_cloud',
    confidence: 97.9,
    dimensions: { length: 0.45, width: 0.45, height: 3.8 },
    position: { x: -5.0, y: 1.9, z: 3.0 },
    rotation: { x: 0, y: 0, z: 0 },
    planeEquation: [-1.0, 0.0, 0.0, -5.0],
    lod: 'LOD 350',
    material: 'RC Grade C40',
    propertySets: {
      Pset_ColumnCommon: { LoadBearing: true }
    },
    status: 'fitted'
  },
  {
    id: 'elem-slab-floor',
    name: 'Ground Floor Slab',
    ifcType: 'IfcSlab',
    source_type: 'point_cloud',
    confidence: 99.6,
    dimensions: { length: 14.0, width: 10.0, height: 0.25 },
    position: { x: 0.0, y: -0.125, z: 0.0 },
    rotation: { x: 0, y: 0, z: 0 },
    planeEquation: [0.0, 1.0, 0.0, 0.0],
    lod: 'LOD 350',
    material: 'Cast-in-place Concrete',
    propertySets: {
      Pset_SlabCommon: { Compartmentation: true, AcousticRating: '55dB' }
    },
    status: 'fitted'
  },
  {
    id: 'elem-duct-main',
    name: 'HVAC Main Supply Duct',
    ifcType: 'IfcDuctSegment',
    source_type: 'point_cloud',
    confidence: 93.1,
    dimensions: { length: 9.5, width: 0.6, height: 0.4 },
    position: { x: 0.0, y: 3.2, z: 0.0 },
    rotation: { x: 0, y: 0, z: 0 },
    lod: 'LOD 300',
    material: 'Galvanized Sheet Steel',
    propertySets: {
      Pset_DuctSegmentTypeCommon: { PressureRating: 1500 }
    },
    status: 'fitted'
  }
];

export const MOCK_SEGMENTATION_STATS: SegmentationStats = {
  totalPoints: 8450200,
  segmentedPoints: 8450200,
  meanIoU: 89.4,
  modelName: 'Point Transformer V3',
  voxelSizeMeters: 0.02,
  classCounts: {
    'IfcWallStandardCase': 3211000,
    'IfcSlab': 2535000,
    'IfcColumn': 1267000,
    'IfcDuctSegment': 845000,
    'IfcWindow': 592200
  }
};

export const MOCK_RANSAC_STATS: RansacStats = {
  distanceThresholdM: 0.02,
  minInlierPoints: 500,
  fittedPlanesCount: 24,
  extractedPrimitivesCount: 5,
  meanResidualErrorMm: 2.1
};

export const MOCK_ACTIVITY_LOGS: ActivityLog[] = [
  {
    id: 'log-01',
    timestamp: '00:28:10',
    stage: 'PTv3 Segmenter',
    message: 'Point Transformer V3 inferred 8.45M points across 5 semantic classes (Mean mIoU = 89.4%).',
    type: 'success'
  },
  {
    id: 'log-02',
    timestamp: '00:28:35',
    stage: 'Cloud2BIM RANSAC',
    message: 'Fitted 24 planar region equations using Open3D RANSAC (distance threshold = 2.0 cm).',
    type: 'success'
  },
  {
    id: 'log-03',
    timestamp: '00:28:50',
    stage: 'IFC Primitive Synthesizer',
    message: 'Constructed 5 volumetric IFC entities. Added source_type = point_cloud metadata attribute.',
    type: 'success'
  },
  {
    id: 'log-04',
    timestamp: '00:29:15',
    stage: 'IfcOpenShell',
    message: 'Generated IFC4 file (LOD 350) compatible with Context & Geometry frozen schema.',
    type: 'info'
  }
];
