import React, { useState } from 'react';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { DashboardPage } from './components/pages/DashboardPage';
import { UploadDatasetPage } from './components/pages/UploadDatasetPage';
import { SfmMvsPipelinePage } from './components/pages/SfmMvsPipelinePage';
import { GaussianSplattingPage } from './components/pages/GaussianSplattingPage';
import { AiPhotogrammetryPage } from './components/pages/AiPhotogrammetryPage';
import { SettingsPage } from './components/pages/SettingsPage';
import { NavTab } from './types/photogrammetry';
import { MOCK_COLMAP_STATS, MOCK_SPLAT_STATS } from './data/mockPhotogrammetryData';

export default function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('dashboard');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header serverStatus="connected" />

      <div className="flex flex-1 relative">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 overflow-y-auto">
          {activeTab === 'dashboard' && (
            <DashboardPage
              setActiveTab={setActiveTab}
              colmapStats={MOCK_COLMAP_STATS}
              splatStats={MOCK_SPLAT_STATS}
            />
          )}
          {activeTab === 'upload' && <UploadDatasetPage setActiveTab={setActiveTab} />}
          {activeTab === 'sfm_mvs' && <SfmMvsPipelinePage stats={MOCK_COLMAP_STATS} />}
          {activeTab === 'gaussian_splatting' && <GaussianSplattingPage stats={MOCK_SPLAT_STATS} />}
          {activeTab === 'ai_diagnostics' && <AiPhotogrammetryPage />}
          {activeTab === 'settings' && <SettingsPage />}
        </main>
      </div>
    </div>
  );
}
