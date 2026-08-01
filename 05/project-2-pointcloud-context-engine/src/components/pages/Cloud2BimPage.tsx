import React, { useState } from 'react';
import { 
  Layers, 
  Play, 
  Sliders, 
  Layers3, 
  CheckCircle2,
  ArrowRight
} from 'lucide-react';
import { NavTab, RansacStats } from '../../types/cloud2bim';

interface Cloud2BimPageProps {
  setActiveTab: (tab: NavTab) => void;
  stats: RansacStats;
}

export const Cloud2BimPage: React.FC<Cloud2BimPageProps> = ({ setActiveTab, stats }) => {
  const [selectedLod, setSelectedLod] = useState<'LOD 100' | 'LOD 200' | 'LOD 300' | 'LOD 350' | 'LOD 400'>('LOD 350');
  const [distanceThreshold, setDistanceThreshold] = useState<number>(0.02);
  const [minPoints, setMinPoints] = useState<number>(500);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleRunRansac = async () => {
    setIsProcessing(true);
    try {
      await fetch('/api/context/ransac-fit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ distanceThreshold, minPoints, lod: selectedLod })
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsProcessing(false);
      setActiveTab('primitives');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Banner */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-amber-400" /> Cloud2BIM Surface Fitting Pipeline
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Convert 3D point cloud clusters into parametric IFC primitives using Open3D RANSAC plane segmentation.
          </p>
        </div>

        <button
          onClick={handleRunRansac}
          disabled={isProcessing}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />
          {isProcessing ? 'Fitting Geometry Planes...' : 'Run RANSAC & Build IFC Entities'}
        </button>
      </div>

      {/* Main Parameters */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LOD Selection Card */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <Layers3 className="w-4 h-4 text-amber-400" /> Level of Development (LOD)
          </h3>

          <div className="grid grid-cols-2 gap-2 text-xs">
            {[
              { lod: 'LOD 100', desc: 'Conceptual Box' },
              { lod: 'LOD 200', desc: 'Approximate Geometry' },
              { lod: 'LOD 300', desc: 'Precise Geometry' },
              { lod: 'LOD 350', desc: 'As-Built + Rebar / Assemblies' }
            ].map((item) => (
              <button
                key={item.lod}
                onClick={() => setSelectedLod(item.lod as any)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  selectedLod === item.lod
                    ? 'bg-amber-500/15 border-amber-400 text-amber-300 font-bold'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <div className="font-mono text-xs">{item.lod}</div>
                <div className="text-[10px] opacity-75 mt-0.5">{item.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* RANSAC Geometry Parameters */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-amber-400" /> Open3D RANSAC Surface Fitting Parameters
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-400">
                <span>Distance Threshold (Inlier Tolerance)</span>
                <span className="font-mono text-amber-300 font-bold">{(distanceThreshold * 100).toFixed(1)} cm</span>
              </div>
              <input
                type="range"
                min="0.005"
                max="0.05"
                step="0.005"
                value={distanceThreshold}
                onChange={(e) => setDistanceThreshold(parseFloat(e.target.value))}
                className="w-full accent-amber-500 bg-slate-800 h-1 rounded cursor-pointer"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-400">
                <span>Minimum Inliers per Plane</span>
                <span className="font-mono text-amber-300 font-bold">{minPoints} pts</span>
              </div>
              <input
                type="range"
                min="100"
                max="2000"
                step="100"
                value={minPoints}
                onChange={(e) => setMinPoints(parseInt(e.target.value))}
                className="w-full accent-amber-500 bg-slate-800 h-1 rounded cursor-pointer"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
