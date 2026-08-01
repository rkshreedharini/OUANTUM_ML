import React from 'react';
import { 
  Layers, 
  Cpu, 
  Box, 
  FileCode2, 
  ArrowRight, 
  CheckCircle2, 
  Activity,
  Sparkles,
  Clock
} from 'lucide-react';
import { NavTab, SegmentationStats, RansacStats } from '../../types/cloud2bim';
import { MOCK_ACTIVITY_LOGS } from '../../data/mockCloud2BimData';

interface DashboardPageProps {
  setActiveTab: (tab: NavTab) => void;
  segmentationStats: SegmentationStats;
  ransacStats: RansacStats;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ setActiveTab, segmentationStats, ransacStats }) => {
  return (
    <div className="p-6 space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-mono font-bold">
            Role 17: Point-Cloud-to-Context Engineer
          </span>
          <h2 className="text-xl font-extrabold text-slate-100 mt-2">
            Point-Cloud-to-BuildingContext & Cloud2BIM Extraction Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Converts unstructured point cloud data into parametric IFC entities using Point Transformer V3 / KPConv semantic classification and Open3D RANSAC planar surface fitting.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('cloud2bim')}
            className="px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all active:scale-95"
          >
            <Layers className="w-4 h-4" /> Run Cloud2BIM RANSAC
          </button>
          <button
            onClick={() => setActiveTab('ifc_export')}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 flex items-center gap-2 transition-all"
          >
            Export IFC4 <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Points */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Input Point Cloud</span>
            <Cpu className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100 font-mono">{(segmentationStats.totalPoints / 1e6).toFixed(2)}M Pts</div>
          <p className="text-[11px] text-emerald-400 font-semibold">Mean mIoU: {segmentationStats.meanIoU}%</p>
        </div>

        {/* RANSAC Fitted Planes */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">RANSAC Planes</span>
            <Layers className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100 font-mono">{ransacStats.fittedPlanesCount} Planes</div>
          <p className="text-[11px] text-slate-400 font-mono">Residual Error: <span className="text-cyan-400 font-bold">{ransacStats.meanResidualErrorMm} mm</span></p>
        </div>

        {/* Extracted IFC Entities */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">IFC Primitives</span>
            <Box className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100 font-mono">{ransacStats.extractedPrimitivesCount} Entities</div>
          <p className="text-[11px] text-emerald-400 font-mono font-bold">source_type = point_cloud</p>
        </div>

        {/* IFC Schema Compatibility */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">IFC Schema</span>
            <FileCode2 className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl font-extrabold text-amber-400 font-mono flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-amber-400" /> IFC4 (LOD 350)
          </div>
          <p className="text-[11px] text-slate-400">IfcOpenShell Ready</p>
        </div>
      </div>

      {/* Main Grid: Pipeline Summary & Activity Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Capabilities Overview */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-amber-400" /> Module Architecture & Deliverables
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center font-bold">
                01
              </div>
              <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
                Point Transformer V3 Semantic Segmentation
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Classifies point cloud points into structural categories (walls, slabs, columns, beams, openings, MEP ducts/pipes).
              </p>
              <button
                onClick={() => setActiveTab('semantic_segmentation')}
                className="text-xs text-amber-400 hover:underline font-semibold flex items-center gap-1 pt-1"
              >
                View Point Classes <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold">
                02
              </div>
              <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
                Cloud2BIM Planar Extraction Engine
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Fits Open3D RANSAC 3D plane equations, calculates bounding dimensions, and outputs parametric IFC primitives tagged with <code>source_type = point_cloud</code>.
              </p>
              <button
                onClick={() => setActiveTab('primitives')}
                className="text-xs text-cyan-400 hover:underline font-semibold flex items-center gap-1 pt-1"
              >
                Inspect IFC Primitives <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Logs */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-400" /> Pipeline Activity Log
          </h3>

          <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            {MOCK_ACTIVITY_LOGS.map((log) => (
              <div key={log.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <div className="flex justify-between items-center text-[10px] font-mono">
                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-semibold">{log.stage}</span>
                  <span className="text-slate-500">{log.timestamp}</span>
                </div>
                <p className="text-xs text-slate-300 leading-normal">{log.message}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
