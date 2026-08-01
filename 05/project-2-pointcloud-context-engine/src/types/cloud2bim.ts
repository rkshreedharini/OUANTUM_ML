export type NavTab = 
  | 'dashboard' 
  | 'semantic_segmentation' 
  | 'cloud2bim' 
  | 'primitives' 
  | 'ifc_export' 
  | 'ai_analysis' 
  | 'settings';

export type IfcType = 
  | 'IfcWallStandardCase' 
  | 'IfcColumn' 
  | 'IfcBeam' 
  | 'IfcSlab' 
  | 'IfcWindow' 
  | 'IfcDoor' 
  | 'IfcPipeSegment' 
  | 'IfcDuctSegment';

export interface PointCloudPoint {
  x: number;
  y: number;
  z: number;
  r: number;
  g: number;
  b: number;
  classification: string;
  confidence: number;
}

export interface IfcPrimitive {
  id: string;
  name: string;
  ifcType: IfcType;
  source_type: 'point_cloud'; // Mandatory schema field
  confidence: number; // 0 - 100%
  dimensions: { length: number; width: number; height: number }; // meters
  position: { x: number; y: number; z: number };
  rotation: { x: number; y: number; z: number };
  planeEquation?: [number, number, number, number]; // [a, b, c, d]
  lod: 'LOD 100' | 'LOD 200' | 'LOD 300' | 'LOD 350' | 'LOD 400';
  material: string;
  propertySets: Record<string, Record<string, string | number | boolean>>;
  status: 'segmented' | 'fitted' | 'validated' | 'exported';
}

export interface SegmentationStats {
  totalPoints: number;
  segmentedPoints: number;
  meanIoU: number;
  modelName: 'Point Transformer V3' | 'KPConv';
  voxelSizeMeters: number;
  classCounts: Record<string, number>;
}

export interface RansacStats {
  distanceThresholdM: number;
  minInlierPoints: number;
  fittedPlanesCount: number;
  extractedPrimitivesCount: number;
  meanResidualErrorMm: number;
}

export interface ActivityLog {
  id: string;
  timestamp: string;
  stage: 'PTv3 Segmenter' | 'Cloud2BIM RANSAC' | 'IFC Primitive Synthesizer' | 'IfcOpenShell' | 'Gemini AI';
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}
