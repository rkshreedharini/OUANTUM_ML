import React, { useState } from 'react';
import { 
  Cpu, 
  Layers, 
  Play, 
  CheckCircle2, 
  Filter, 
  Sliders, 
  Activity 
} from 'lucide-react';
import { PointCloudContext3DViewer } from '../viewer/PointCloudContext3DViewer';
import { SegmentationStats } from '../../types/cloud2bim';

interface SemanticSegmentationPageProps {
  stats: SegmentationStats;
}

export const SemanticSegmentationPage: React.FC<SemanticSegmentationPageProps> = ({ stats }) => {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [voxelSize, setVoxelSize] = useState<number>(0.02);

  const handleRunSegmentation = async () => {
    setIsProcessing(true);
    try {
      await fetch('/api/context/segment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voxelSize })
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-amber-400" /> Point Transformer V3 / KPConv Semantic Segmentation
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Deep point neural network semantic classification mapping 3D points to standard IFC architectural classes.
          </p>
        </div>

        <button
          onClick={handleRunSegmentation}
          disabled={isProcessing}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />
          {isProcessing ? 'Segmenting Point Cloud...' : 'Run PTv3 Semantic Classification'}
        </button>
      </div>

      {/* 3D Visualizer & Parameters */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 h-[600px]">
          <PointCloudContext3DViewer colorMode="classification" />
        </div>

        <div className="space-y-5">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 font-mono text-xs">
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2 font-sans">
              <Activity className="w-4 h-4 text-amber-400" /> PTv3 Class Accuracy Metrics
            </h3>

            <div className="space-y-2 text-[11px]">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Mean mIoU:</span>
                <span className="text-emerald-400 font-bold">{stats.meanIoU}%</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Architecture:</span>
                <span className="text-amber-300 font-bold">{stats.modelName}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Voxel Grid Size:</span>
                <span className="text-cyan-400">{voxelSize * 100} cm</span>
              </div>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-amber-400" /> Voxel Grid Parameter
            </h3>

            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-400">
                <span>Voxel Downsampling:</span>
                <span className="font-mono text-amber-300 font-bold">{(voxelSize * 100).toFixed(1)} cm</span>
              </div>
              <input
                type="range"
                min="0.01"
                max="0.05"
                step="0.005"
                value={voxelSize}
                onChange={(e) => setVoxelSize(parseFloat(e.target.value))}
                className="w-full accent-amber-500 bg-slate-800 h-1 rounded cursor-pointer"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
