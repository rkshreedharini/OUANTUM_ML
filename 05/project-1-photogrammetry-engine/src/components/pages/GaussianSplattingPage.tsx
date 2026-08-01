import React, { useState } from 'react';
import { 
  Sparkles, 
  Play, 
  ShieldAlert, 
  Sliders, 
  Activity, 
  CheckCircle2,
  Download
} from 'lucide-react';
import { SplatPointCloudViewer } from '../viewer/SplatPointCloudViewer';
import { GaussianSplatStats } from '../../types/photogrammetry';

interface GaussianSplattingPageProps {
  stats: GaussianSplatStats;
}

export const GaussianSplattingPage: React.FC<GaussianSplattingPageProps> = ({ stats }) => {
  const [isTraining, setIsTraining] = useState<boolean>(false);
  const [targetIterations, setTargetIterations] = useState<number>(30000);
  const [shDegree, setShDegree] = useState<number>(3);

  const handleTrainSplatting = async () => {
    setIsTraining(true);
    try {
      await fetch('/api/photogrammetry/splat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ iterations: targetIterations })
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Banner */}
      <div className="p-5 rounded-2xl bg-amber-950/30 border border-amber-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-mono font-bold flex items-center gap-1.5 w-fit">
            <ShieldAlert className="w-3.5 h-3.5" /> Photoreal Client Demo Engine (Visualization Only)
          </span>
          <h2 className="text-lg font-extrabold text-slate-100 mt-2 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-400" /> 3D Gaussian Splatting (gsplat / Nerfstudio) Trainer
          </h2>
          <p className="text-xs text-amber-200/80 mt-1 max-w-3xl">
            Train 3D Gaussian representations for real-time photorealistic walkthroughs. Splats are optimized strictly for visual fidelity and must never be used to derive dimensional measurements.
          </p>
        </div>

        <button
          onClick={handleTrainSplatting}
          disabled={isTraining}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${isTraining ? 'animate-spin' : ''}`} />
          {isTraining ? 'Optimizing 1.5M Gaussians...' : 'Train 3D Gaussian Splat Model'}
        </button>
      </div>

      {/* Main Workbench Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 3D Viewer Canvas */}
        <div className="lg:col-span-3 h-[600px]">
          <SplatPointCloudViewer renderingMode="gaussian_splat" />
        </div>

        {/* Hyperparameters & Metrics Panel */}
        <div className="space-y-5">
          {/* Metrics */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 font-mono text-xs">
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2 font-sans">
              <Activity className="w-4 h-4 text-amber-400" /> Splat Model Quality Metrics
            </h3>

            <div className="space-y-2 text-[11px]">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Total Gaussians:</span>
                <span className="text-amber-300 font-bold">{(stats.numGaussians / 1e6).toFixed(2)}M</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">PSNR Quality:</span>
                <span className="text-emerald-400 font-bold">{stats.psnrDb} dB</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">SSIM Index:</span>
                <span className="text-cyan-400 font-bold">{stats.ssim}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Rendering Frame Rate:</span>
                <span className="text-amber-400 font-bold">{stats.renderFps} FPS</span>
              </div>
            </div>

            <button className="w-full mt-2 py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-colors">
              <Download className="w-3.5 h-3.5" /> Download .splat Model File
            </button>
          </div>

          {/* Hyperparameter Controls */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-amber-400" /> Training Parameters
            </h3>

            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-400">
                <span>Iterations:</span>
                <span className="font-mono text-amber-300 font-bold">{targetIterations.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="7000"
                max="30000"
                step="1000"
                value={targetIterations}
                onChange={(e) => setTargetIterations(parseInt(e.target.value))}
                className="w-full accent-amber-500 bg-slate-800 h-1 rounded cursor-pointer"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-400">
                <span>Spherical Harmonics Degree:</span>
                <span className="font-mono text-amber-300 font-bold">Degree {shDegree}</span>
              </div>
              <div className="grid grid-cols-4 gap-1.5 font-mono">
                {[0, 1, 2, 3].map((deg) => (
                  <button
                    key={deg}
                    onClick={() => setShDegree(deg)}
                    className={`py-1 rounded border text-[11px] font-bold ${
                      shDegree === deg
                        ? 'bg-amber-500/20 border-amber-400 text-amber-300'
                        : 'bg-slate-950 border-slate-800 text-slate-400'
                    }`}
                  >
                    L{deg}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
