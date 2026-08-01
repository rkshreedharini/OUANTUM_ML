import React, { useState } from 'react';
import { Settings, Save, Server, Cpu, Sparkles, Check } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [apiKey, setApiKey] = useState<string>('GEMINI_API_KEY_CONFIGURED');
  const [weightsPath, setWeightsPath] = useState<string>('./weights/ptv3_scannet.pth');
  const [schema, setSchema] = useState<string>('IFC4');
  const [saved, setSaved] = useState<boolean>(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            <Settings className="w-5 h-5 text-amber-400" /> Context Engine Settings
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure PTv3 model weights, Open3D RANSAC defaults, IfcOpenShell schema, and Gemini API keys.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-lg flex items-center gap-2 transition-all"
        >
          {saved ? <Check className="w-4 h-4 text-slate-950" /> : <Save className="w-4 h-4" />}
          {saved ? 'Saved Config' : 'Save Settings'}
        </button>
      </div>

      <div className="space-y-5">
        {/* Gemini AI */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" /> Gemini API Secrets (@google/genai v2.4.0)
          </h3>
          <div className="space-y-1 text-xs">
            <label className="text-slate-400">GEMINI_API_KEY</label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono focus:outline-none focus:border-amber-400"
            />
          </div>
        </div>

        {/* Weights Path */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <Cpu className="w-4 h-4 text-amber-400" /> Point Transformer V3 Weights Path
          </h3>
          <div className="space-y-1 text-xs">
            <label className="text-slate-400">PyTorch Checkpoint File (.pth)</label>
            <input
              type="text"
              value={weightsPath}
              onChange={(e) => setWeightsPath(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono focus:outline-none focus:border-amber-400"
            />
          </div>
        </div>

        {/* IFC Schema */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" /> Default IFC Schema
          </h3>
          <div className="space-y-1 text-xs">
            <label className="text-slate-400">Schema Version</label>
            <input
              type="text"
              value={schema}
              onChange={(e) => setSchema(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono focus:outline-none focus:border-cyan-400"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
