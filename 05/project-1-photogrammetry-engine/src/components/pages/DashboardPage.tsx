import React from 'react';
import { 
  Camera, 
  Cpu, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight,
  Activity,
  Layers,
  ShieldCheck,
  Clock
} from 'lucide-react';
import { NavTab, ColmapStats, GaussianSplatStats } from '../../types/photogrammetry';
import { MOCK_ACTIVITY_LOGS } from '../../data/mockPhotogrammetryData';

interface DashboardPageProps {
  setActiveTab: (tab: NavTab) => void;
  colmapStats: ColmapStats;
  splatStats: GaussianSplatStats;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ setActiveTab, colmapStats, splatStats }) => {
  return (
    <div className="p-6 space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-mono font-bold">
            Role 16: Photogrammetry Engineer
          </span>
          <h2 className="text-xl font-extrabold text-slate-100 mt-2">
            Structure-from-Motion & 3D Gaussian Splatting Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Metrically accurate COLMAP SfM/MVS point cloud generation paired with gsplat / Nerfstudio 3D Gaussian Splatting for photorealistic client visualization.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('upload')}
            className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all active:scale-95"
          >
            <Camera className="w-4 h-4" /> Load Photo Dataset
          </button>
          <button
            onClick={() => setActiveTab('sfm_mvs')}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 flex items-center gap-2 transition-all"
          >
            Run COLMAP Pipeline <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Images */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Drone / Site Photos</span>
            <Camera className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100 font-mono">{colmapStats.totalImages} Frames</div>
          <p className="text-[11px] text-emerald-400 font-semibold">100% EXIF Georeferenced</p>
        </div>

        {/* COLMAP Dense Points */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">COLMAP Dense Points</span>
            <Layers className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100 font-mono">{(colmapStats.densePointsCount / 1e6).toFixed(2)}M Pts</div>
          <p className="text-[11px] text-slate-400 font-mono">RMS Residual: <span className="text-emerald-400 font-bold">{colmapStats.sparseRmseMm} mm</span></p>
        </div>

        {/* 3D Gaussian Splats */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">3D Gaussian Splats</span>
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100 font-mono">{(splatStats.numGaussians / 1e6).toFixed(2)}M Splats</div>
          <p className="text-[11px] text-amber-300 font-mono">PSNR: {splatStats.psnrDb} dB • {splatStats.renderFps} FPS</p>
        </div>

        {/* Pipeline Status */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Pipeline Status</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-xl font-extrabold text-emerald-400 font-mono flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" /> CONVERGED
          </div>
          <p className="text-[11px] text-slate-400">All 48 Cameras Calibrated</p>
        </div>
      </div>

      {/* Main Grid: Pipeline Summary & Activity Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline Features Overview */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" /> Module Capabilities & Deliverables
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold">
                01
              </div>
              <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
                COLMAP SfM / MVS Pipeline
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Extracts SIFT keypoints, matches feature descriptors, performs bundle adjustment, and computes dense PatchMatch point clouds with sub-millimeter RMS residuals (1.84 mm).
              </p>
              <button
                onClick={() => setActiveTab('sfm_mvs')}
                className="text-xs text-cyan-400 hover:underline font-semibold flex items-center gap-1 pt-1"
              >
                Inspect Point Cloud <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center font-bold">
                02
              </div>
              <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
                3D Gaussian Splatting Engine
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generates photorealistic rendering scenes via <code>gsplat</code> & <code>Nerfstudio</code>. Explicitly bounded for client visualization demos only, maintaining strict separation from dimensional truth.
              </p>
              <button
                onClick={() => setActiveTab('gaussian_splat')}
                className="text-xs text-amber-400 hover:underline font-semibold flex items-center gap-1 pt-1"
              >
                Launch Splatting Engine <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Activity Logs Column */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" /> Pipeline Activity Log
          </h3>

          <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            {MOCK_ACTIVITY_LOGS.map((log) => (
              <div key={log.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <div className="flex justify-between items-center text-[10px] font-mono">
                  <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-semibold">{log.stage}</span>
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
