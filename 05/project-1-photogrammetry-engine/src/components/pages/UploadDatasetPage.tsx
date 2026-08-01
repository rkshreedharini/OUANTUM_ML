import React, { useState } from 'react';
import { 
  Upload, 
  Camera, 
  Trash2, 
  Play, 
  Check, 
  Sliders, 
  MapPin, 
  Image as ImageIcon 
} from 'lucide-react';
import { PhotogrammetryImage, NavTab } from '../../types/photogrammetry';
import { MOCK_IMAGES } from '../../data/mockPhotogrammetryData';

interface UploadDatasetPageProps {
  setActiveTab: (tab: NavTab) => void;
}

export const UploadDatasetPage: React.FC<UploadDatasetPageProps> = ({ setActiveTab }) => {
  const [images, setImages] = useState<PhotogrammetryImage[]>(MOCK_IMAGES);
  const [selectedImage, setSelectedImage] = useState<PhotogrammetryImage | null>(MOCK_IMAGES[0]);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [preset, setPreset] = useState<'high_quality' | 'fast'>('high_quality');

  const handleSimulateUpload = () => {
    const newImg: PhotogrammetryImage = {
      id: `img-${Date.now()}`,
      name: `DRONE_CAPTURE_${images.length + 1}.JPG`,
      url: 'https://images.unsplash.com/photo-1508873696983-2df515122519?auto=format&fit=crop&w=800&q=80',
      size: '16.4 MB',
      resolution: '5472 x 3648 (20 MP)',
      exif: {
        camera: 'DJI FC6310 (Phantom 4 Pro V2)',
        focalLength: '8.8 mm',
        iso: 100,
        aperture: 'f/4.0',
        shutterSpeed: '1/1000s',
        gps: { lat: 37.7754, lng: -122.4187, alt: 53.1 }
      },
      keypointsCount: 37800,
      qualityScore: 97,
      status: 'matched'
    };
    setImages([newImg, ...images]);
    setSelectedImage(newImg);
  };

  const handleRunFeatureExtractor = async () => {
    setIsProcessing(true);
    try {
      const res = await fetch('/api/photogrammetry/reconstruct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset })
      });
      const data = await res.json();
      console.log('COLMAP Reconstruct Response:', data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsProcessing(false);
      setActiveTab('sfm_mvs');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Banner */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            <Upload className="w-5 h-5 text-cyan-400" /> Photogrammetry Photo Ingestion Workbench
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Load drone or smartphone photos for SIFT feature extraction, EXIF focal length auto-calibration, and COLMAP SfM feature matching.
          </p>
        </div>

        <button
          onClick={handleRunFeatureExtractor}
          disabled={isProcessing || images.length === 0}
          className="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />
          {isProcessing ? 'Processing SIFT Matching...' : 'Run COLMAP Feature Matching'}
        </button>
      </div>

      {/* Upload Dropzone */}
      <div
        onClick={handleSimulateUpload}
        className="p-8 rounded-2xl border-2 border-dashed border-slate-800 hover:border-cyan-500/50 bg-slate-900/60 hover:bg-slate-900 transition-all text-center flex flex-col items-center justify-center space-y-3 cursor-pointer group"
      >
        <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform">
          <Upload className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-200">Click or Drag & Drop Site Photos Here</h3>
          <p className="text-xs text-slate-400 mt-0.5">Supports RAW, JPG, PNG, TIFF from UAV Drones, DSLR, or Mobile Scanners</p>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-slate-500 font-mono">
          <span>• Min 70% Overlap</span>
          <span>• EXIF Auto-Calibration</span>
          <span>• Max 100MB / Image</span>
        </div>
      </div>

      {/* Images & EXIF Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Image Grid */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <ImageIcon className="w-4 h-4 text-cyan-400" /> Loaded Photos ({images.length})
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {images.map((img) => (
              <div
                key={img.id}
                onClick={() => setSelectedImage(img)}
                className={`p-2.5 rounded-xl bg-slate-900 border transition-all cursor-pointer ${
                  selectedImage?.id === img.id
                    ? 'border-cyan-400 ring-2 ring-cyan-500/20 shadow-xl'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="aspect-video rounded-lg overflow-hidden relative mb-2 bg-slate-950">
                  <img src={img.url} alt={img.name} className="w-full h-full object-cover" />
                  <div className="absolute top-1.5 right-1.5 px-2 py-0.5 rounded bg-slate-950/80 text-[10px] text-cyan-300 font-mono font-bold backdrop-blur">
                    Q: {img.qualityScore}%
                  </div>
                </div>

                <p className="text-xs font-semibold text-slate-200 truncate">{img.name}</p>
                <div className="flex justify-between text-[10px] text-slate-400 font-mono mt-1">
                  <span>{img.size}</span>
                  <span className="text-cyan-400 font-bold">{img.keypointsCount} keypts</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Col: Selected Image EXIF Metadata */}
        <div className="space-y-5">
          {selectedImage && (
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                <Camera className="w-4 h-4 text-cyan-400" /> EXIF & Camera Calibration
              </h3>

              <div className="aspect-video rounded-xl overflow-hidden border border-slate-800">
                <img src={selectedImage.url} alt={selectedImage.name} className="w-full h-full object-cover" />
              </div>

              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Camera Model:</span>
                  <span className="text-cyan-400 font-bold">{selectedImage.exif.camera}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Focal Length:</span>
                  <span className="text-slate-200">{selectedImage.exif.focalLength}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Aperture / Speed:</span>
                  <span className="text-slate-200">{selectedImage.exif.aperture} • {selectedImage.exif.shutterSpeed}</span>
                </div>
                {selectedImage.exif.gps && (
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400 flex items-center gap-1"><MapPin className="w-3 h-3 text-rose-400" /> GPS Coordinates:</span>
                    <span className="text-slate-200">{selectedImage.exif.gps.lat}, {selectedImage.exif.gps.lng}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
