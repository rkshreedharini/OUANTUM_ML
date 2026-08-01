import React, { useState } from 'react';
import { FileCode2, Download, Check, Sparkles } from 'lucide-react';
import { IfcPrimitive } from '../../types/cloud2bim';

interface IfcExportPageProps {
  primitives: IfcPrimitive[];
}

export const IfcExportPage: React.FC<IfcExportPageProps> = ({ primitives }) => {
  const [schema, setSchema] = useState<'IFC4' | 'IFC2x3'>('IFC4');
  const [lod, setLod] = useState<'LOD 100' | 'LOD 200' | 'LOD 300' | 'LOD 350' | 'LOD 400'>('LOD 350');
  const [ifcContent, setIfcContent] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const handleGenerateIfc = async () => {
    setIsGenerating(true);
    try {
      const res = await fetch('/api/context/export-ifc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schema, lod })
      });
      const data = await res.json();
      setIfcContent(data.ifcContent);
    } catch (e) {
      console.error(e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadFile = () => {
    if (!ifcContent) return;
    const blob = new Blob([ifcContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `BIM_VISION_CLOUD2BIM_${schema}_${lod.replace(' ', '')}.ifc`;
    link.click();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Banner */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            <FileCode2 className="w-5 h-5 text-amber-400" /> IfcOpenShell Standard File Exporter
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Export extracted point cloud entities into valid ISO 10303-21 standard IFC files with frozen Context & Geometry schema compatibility.
          </p>
        </div>

        <button
          onClick={handleGenerateIfc}
          disabled={isGenerating}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
        >
          <FileCode2 className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
          {isGenerating ? 'Synthesizing IFC File...' : 'Generate Standard IFC File'}
        </button>
      </div>

      {/* Exporter Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Schema Options */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">IFC Schema Standard</h3>
          <div className="grid grid-cols-2 gap-2 text-xs font-bold">
            {(['IFC4', 'IFC2x3'] as const).map((s) => (
              <button
                key={s}
                onClick={() => setSchema(s)}
                className={`p-3 rounded-xl border text-center transition-all ${
                  schema === s ? 'bg-amber-500/15 border-amber-400 text-amber-300' : 'bg-slate-950/60 border-slate-800 text-slate-400'
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider pt-2">LOD Specification</h3>
          <div className="grid grid-cols-2 gap-2 text-xs font-bold">
            {(['LOD 200', 'LOD 300', 'LOD 350', 'LOD 400'] as const).map((l) => (
              <button
                key={l}
                onClick={() => setLod(l)}
                className={`p-2.5 rounded-xl border text-center transition-all ${
                  lod === l ? 'bg-amber-500/15 border-amber-400 text-amber-300' : 'bg-slate-950/60 border-slate-800 text-slate-400'
                }`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>

        {/* Code Preview */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col h-[400px]">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">IFC File Preview</h3>
            {ifcContent && (
              <button
                onClick={handleDownloadFile}
                className="px-4 py-1.5 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all shadow"
              >
                <Download className="w-3.5 h-3.5" /> Download .ifc File
              </button>
            )}
          </div>

          <div className="flex-1 p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-y-auto whitespace-pre leading-relaxed">
            {ifcContent ? ifcContent : 'Click "Generate Standard IFC File" to compile ISO-10303-21 text stream.'}
          </div>
        </div>
      </div>
    </div>
  );
};
