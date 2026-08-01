import React, { useState } from 'react';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { DashboardPage } from './components/pages/DashboardPage';
import { SemanticSegmentationPage } from './components/pages/SemanticSegmentationPage';
import { Cloud2BimPage } from './components/pages/Cloud2BimPage';
import { ExtractedPrimitivesPage } from './components/pages/ExtractedPrimitivesPage';
import { IfcExportPage } from './components/pages/IfcExportPage';
import { AiContextAnalysisPage } from './components/pages/AiContextAnalysisPage';
import { SettingsPage } from './components/pages/SettingsPage';
import { NavTab } from './types/cloud2bim';
import { MOCK_PRIMITIVES, MOCK_SEGMENTATION_STATS, MOCK_RANSAC_STATS } from './data/mockCloud2BimData';

export default function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('dashboard');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header />

      <div className="flex flex-1 relative">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 overflow-y-auto">
          {activeTab === 'dashboard' && (
            <DashboardPage
              setActiveTab={setActiveTab}
              segmentationStats={MOCK_SEGMENTATION_STATS}
              ransacStats={MOCK_RANSAC_STATS}
            />
          )}
          {activeTab === 'semantic_segmentation' && (
            <SemanticSegmentationPage stats={MOCK_SEGMENTATION_STATS} />
          )}
          {activeTab === 'cloud2bim' && (
            <Cloud2BimPage setActiveTab={setActiveTab} stats={MOCK_RANSAC_STATS} />
          )}
          {activeTab === 'primitives' && (
            <ExtractedPrimitivesPage primitives={MOCK_PRIMITIVES} setActiveTab={setActiveTab} />
          )}
          {activeTab === 'ifc_export' && (
            <IfcExportPage primitives={MOCK_PRIMITIVES} />
          )}
          {activeTab === 'ai_analysis' && <AiContextAnalysisPage />}
          {activeTab === 'settings' && <SettingsPage />}
        </main>
      </div>
    </div>
  );
}
