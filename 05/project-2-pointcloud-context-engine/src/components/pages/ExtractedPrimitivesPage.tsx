import React from 'react';
import { Box, ArrowRight, CheckCircle2 } from 'lucide-react';
import { IfcPrimitive, NavTab } from '../../types/cloud2bim';

interface ExtractedPrimitivesPageProps {
  primitives: IfcPrimitive[];
  setActiveTab: (tab: NavTab) => void;
}

export const ExtractedPrimitivesPage: React.FC<ExtractedPrimitivesPageProps> = ({ primitives, setActiveTab }) => {
  return (
    <div className="p-6 space-y-6">
      {/* Banner */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            <Box className="w-5 h-5 text-amber-400" /> Extracted Parametric IFC Entities
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Volumetric primitives output directly from point cloud RANSAC fitting with metadata attribute <code>source_type = point_cloud</code>.
          </p>
        </div>

        <button
          onClick={() => setActiveTab('ifc_export')}
          className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all active:scale-95"
        >
          Proceed to IFC Export <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Table */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] font-mono">
              <th className="pb-3 font-semibold">Entity Name</th>
              <th className="pb-3 font-semibold">IFC Type</th>
              <th className="pb-3 font-semibold">Source Type Tag</th>
              <th className="pb-3 font-semibold">Dimensions (L x W x H)</th>
              <th className="pb-3 font-semibold">Position (XYZ)</th>
              <th className="pb-3 font-semibold">LOD</th>
              <th className="pb-3 font-semibold">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {primitives.map((elem) => (
              <tr key={elem.id} className="hover:bg-slate-950/50 transition-colors">
                <td className="py-3 font-sans font-semibold text-slate-200">{elem.name}</td>
                <td className="py-3 text-cyan-400 font-semibold">{elem.ifcType}</td>
                <td className="py-3">
                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px] font-bold">
                    {elem.source_type}
                  </span>
                </td>
                <td className="py-3 text-slate-300">{elem.dimensions.length} x {elem.dimensions.width} x {elem.dimensions.height} m</td>
                <td className="py-3 text-slate-400">[{elem.position.x}, {elem.position.y}, {elem.position.z}]</td>
                <td className="py-3 text-amber-300">{elem.lod}</td>
                <td className="py-3">
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">
                    {elem.confidence}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
