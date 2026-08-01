import React from 'react';
import { Camera, Sparkles, Server, CheckCircle2 } from 'lucide-react';

interface HeaderProps {
  serverStatus: 'connected' | 'disconnected' | 'connecting';
}

export const Header: React.FC<HeaderProps> = ({ serverStatus }) => {
  return (
    <header className="h-16 bg-slate-900/90 border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-30 backdrop-blur-md">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-0.5 shadow-lg shadow-cyan-500/20">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <Camera className="w-5 h-5 text-cyan-400" />
          </div>
        </div>
        <div>
          <h1 className="text-base font-extrabold text-slate-100 flex items-center gap-2">
            BIM-Vision AI <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[10px] font-mono tracking-wide uppercase">Role 16 • Photogrammetry Pod</span>
          </h1>
          <p className="text-[11px] text-slate-400">COLMAP SfM / MVS Point Cloud & 3D Gaussian Splatting Engine</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Status indicator */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono">
          <Server className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Express Backend:</span>
          <span className="flex items-center gap-1.5 font-bold text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Active (PORT 3000)
          </span>
        </div>

        <div className="px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] font-semibold flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          Gemini 3.6 Flash
        </div>
      </div>
    </header>
  );
};
