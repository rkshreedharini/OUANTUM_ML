import React, { useState } from 'react';
import { 
  Cpu, 
  Layers, 
  Play, 
  Activity, 
  Download, 
  CheckCircle2,
  Sliders,
  Sparkles
} from 'lucide-react';
import { SplatPointCloudViewer } from '../viewer/SplatPointCloudViewer';
import { ColmapStats } from '../../types/photogrammetry';

interface SfmMvsPipelinePageProps {
  stats: ColmapStats;
}

export const SfmMvsPipelinePage: React.FC<SfmMvsPipelinePageProps> = ({ stats }) => {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [patchMatchRadius, setPatchMatchRadius] = useState<number>(5);

  const handleRunCOLMAP = async () => {
    setIsProcessing(true);
    try {
      await fetch('/api/photogrammetry/reconstruct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quality: 'high' })
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" /> COLMAP Structure-from-Motion (SfM) & PatchMatch MVS Workbench
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Metrically accurate sparse keypoints & PatchMatch MVS dense point cloud reconstruction with calibrated camera poses.
          </p>
        </div>

        <button
          onClick={handleRunCOLMAP}
          disabled={isProcessing}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />
          {isProcessing ? 'Reconstructing Dense Cloud...' : 'Run PatchMatch Dense MVS'}
        </button>
      </div>

      {/* Main Grid: 3D Stage & Control Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 3D Canvas Stage */}
        <div className="lg:col-span-3 h-[600px]">
          <SplatPointCloudViewer renderingMode="metric_cloud" />
        </div>

        {/* Telemetry & Controls Panel */}
        <div className="space-y-5">
          {/* Telemetry Stats */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 font-mono text-xs">
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2 font-sans">
              <Activity className="w-4 h-4 text-cyan-400" /> COLMAP Telemetry
            </h3>

            <div className="space-y-2 text-[11px]">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Cameras Calibrated:</span>
                <span className="text-emerald-400 font-bold">{stats.registeredCameras} / {stats.totalImages}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Sparse Keypoints:</span>
                <span className="text-cyan-400 font-bold">{(stats.sparsePointsCount / 1000).toFixed(1)}k pts</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Dense MVS Points:</span>
                <span className="text-slate-100 font-bold">{(stats.densePointsCount / 1e6).toFixed(2)}M pts</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Mean RMS Residual:</span>
                <span className="text-emerald-400 font-bold">{stats.sparseRmseMm} mm</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Reconstruction Time:</span>
                <span className="text-slate-300">{stats.reconstructionTimeSec} s</span>
              </div>
            </div>

            <button className="w-full mt-2 py-2 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-colors">
              <Download className="w-3.5 h-3.5" /> Export PLY / LAS Point Cloud
            </button>
          </div>

          {/* PatchMatch Parameters */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-cyan-400" /> PatchMatch Parameters
            </h3>

            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-400">
                <span>Window Radius:</span>
                <span className="font-mono text-cyan-400 font-bold">{patchMatchRadius} px</span>
              </div>
              <input
                type="range"
                min="3"
                max="15"
                step="2"
                value={patchMatchRadius}
                onChange={(e) => setPatchMatchRadius(parseInt(e.target.value))}
                className="w-full accent-cyan-500 bg-slate-800 h-1 rounded cursor-pointer"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
