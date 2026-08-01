import React, { useState } from 'react';
import { 
  Bot, 
  Sparkles, 
  Send, 
  Camera, 
  CheckCircle2, 
  Activity,
  Layers,
  Cpu
} from 'lucide-react';

export const AiPhotogrammetryPage: React.FC = () => {
  const [prompt, setPrompt] = useState<string>('');
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; content: string }[]>([
    {
      role: 'ai',
      content: `Hello! I am your Photogrammetry & 3D Gaussian Splatting AI Assistant powered by Gemini 3.6 Flash (@google/genai v2.4.0). I can help verify camera EXIF calibration, calculate photo overlap coverage, optimize SIFT feature matching parameters, and configure gsplat / Nerfstudio training for client demos.`
    }
  ]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);

  const handleSendMessage = async () => {
    if (!prompt.trim()) return;
    const userMsg = prompt;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setPrompt('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/gemini/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'ai', content: data.reply }]);
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'ai', content: `Error: ${e.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunAiAnalysis = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/gemini/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: "Analyze current UAV photogrammetry camera alignment and COLMAP reprojection residuals.",
          context: "Drone capture of site building with 48 photos"
        })
      });
      const data = await res.json();
      setAnalysisResult(data.analysis);
    } catch (e: any) {
      setAnalysisResult(`Analysis Error: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header Banner */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" /> Gemini 3.6 Flash Photogrammetry Diagnostics
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated SIFT keypoint density verification, camera overlap diagnostics, and reprojection error evaluation using @google/genai SDK v2.4.0.
          </p>
        </div>

        <button
          onClick={handleRunAiAnalysis}
          disabled={isLoading}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
        >
          <Sparkles className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          {isLoading ? 'Running Gemini AI Analysis...' : 'Run Automated AI Quality Inspection'}
        </button>
      </div>

      {/* Main Grid: Analysis Report & AI Assistant Chat */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Col: AI Inspection Report */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 flex flex-col h-[560px]">
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" /> Automated Quality Inspection Report
          </h3>

          <div className="flex-1 p-4 rounded-xl bg-slate-950 border border-slate-800/80 overflow-y-auto font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
            {analysisResult ? (
              analysisResult
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 text-center space-y-2 font-sans">
                <Camera className="w-8 h-8 text-slate-600" />
                <p className="text-xs">Click "Run Automated AI Quality Inspection" to analyze SIFT keypoint distribution and camera overlap parameters.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Gemini Interactive Chat */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col h-[560px]">
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2 mb-4">
            <Bot className="w-4 h-4 text-cyan-400" /> Photogrammetry AI Assistant
          </h3>

          {/* Messages list */}
          <div className="flex-1 p-4 rounded-xl bg-slate-950 border border-slate-800/80 overflow-y-auto space-y-3 mb-4 text-xs">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`p-3 rounded-xl max-w-[85%] ${
                  msg.role === 'user'
                    ? 'ml-auto bg-cyan-500/15 border border-cyan-400/30 text-cyan-200'
                    : 'mr-auto bg-slate-900 border border-slate-800 text-slate-200'
                }`}
              >
                <div className="font-bold text-[10px] uppercase font-mono mb-1 text-slate-400">
                  {msg.role === 'user' ? 'You' : 'Gemini 3.6 Flash'}
                </div>
                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              </div>
            ))}
          </div>

          {/* Prompt input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask about COLMAP parameters, SIFT matching, or 3DGS training..."
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-cyan-400"
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !prompt.trim()}
              className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
