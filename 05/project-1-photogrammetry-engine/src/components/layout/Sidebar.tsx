import React from 'react';
import { 
  LayoutDashboard, 
  Upload, 
  Cpu, 
  Sparkles, 
  Bot, 
  Settings,
  ShieldAlert
} from 'lucide-react';
import { NavTab } from '../../types/photogrammetry';

interface SidebarProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems: { id: NavTab; label: string; icon: any; badge?: string }[] = [
    { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutDashboard },
    { id: 'upload', label: 'Photo Dataset', icon: Upload, badge: '48 Photos' },
    { id: 'sfm_mvs', label: 'COLMAP SfM / MVS', icon: Cpu, badge: 'Metric Cloud' },
    { id: 'gaussian_splatting', label: '3D Gaussian Splatting', icon: Sparkles, badge: 'Photoreal' },
    { id: 'ai_diagnostics', label: 'Gemini AI Assistant', icon: Bot },
    { id: 'settings', label: 'Engine Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900/95 border-r border-slate-800/80 flex flex-col justify-between p-4 sticky top-16 h-[calc(100vh-4rem)] z-20">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">
          Photogrammetry Pipeline
        </div>

        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-300 border border-cyan-500/30 shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
                }`}
              >
                <div className="flex items-center space-x-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-2 py-0.5 rounded-md font-mono ${
                    isActive ? 'bg-cyan-500/20 text-cyan-300' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Mandatory Guardrail Banner */}
      <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-300 space-y-1.5 text-[11px]">
        <div className="flex items-center gap-1.5 font-bold">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
          <span>Dimensional Guardrail</span>
        </div>
        <p className="text-[10px] text-amber-200/80 leading-relaxed">
          3D Gaussian Splatting is strictly for photoreal client demos. Dimensional truth is derived <strong>only</strong> from COLMAP dense point clouds.
        </p>
      </div>
    </aside>
  );
};
