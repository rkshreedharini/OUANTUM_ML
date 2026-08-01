import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { 
  Layers, 
  Box, 
  Eye, 
  Sliders, 
  RefreshCw, 
  Sparkles,
  CheckCircle2
} from 'lucide-react';
import { IfcPrimitive } from '../../types/cloud2bim';

interface PointCloudContext3DViewerProps {
  colorMode?: 'classification' | 'elevation' | 'rgb';
  primitives?: IfcPrimitive[];
  heightCutoff?: number;
}

export const PointCloudContext3DViewer: React.FC<PointCloudContext3DViewerProps> = ({
  colorMode: initialColorMode = 'classification',
  primitives = [],
  heightCutoff: initialCutoff = 100
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [colorMode, setColorMode] = useState<'classification' | 'elevation' | 'rgb'>(initialColorMode);
  const [showWireframes, setShowWireframes] = useState<boolean>(true);
  const [showFrustums, setShowFrustums] = useState<boolean>(true);
  const [pointSize, setPointSize] = useState<number>(3.5);
  const [heightCutoff, setHeightCutoff] = useState<number>(initialCutoff);

  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const pointsMeshRef = useRef<THREE.Points | null>(null);
  const bimGroupRef = useRef<THREE.Group | null>(null);
  const frustumGroupRef = useRef<THREE.Group | null>(null);

  const isDraggingRef = useRef<boolean>(false);
  const previousMousePositionRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const cameraRotationRef = useRef<{ theta: number; phi: number; distance: number }>({
    theta: Math.PI / 4,
    phi: Math.PI / 3,
    distance: 14
  });

  useEffect(() => {
    if (!canvasRef.current || !containerRef.current) return;

    const width = containerRef.current.clientWidth || 800;
    const height = containerRef.current.clientHeight || 500;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0f1d);
    sceneRef.current = scene;

    const gridHelper = new THREE.GridHelper(20, 20, 0x1e293b, 0x0f172a);
    scene.add(gridHelper);

    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
    cameraRef.current = camera;
    updateCameraPosition();

    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current,
      antialias: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    rendererRef.current = renderer;

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xf59e0b, 1.2);
    dirLight.position.set(10, 20, 15);
    scene.add(dirLight);

    buildPointCloudMesh();
    buildBimBoxes();
    buildFrustums();

    let animId: number;
    const render = () => {
      animId = requestAnimationFrame(render);
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };
    render();

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width: newW, height: newH } = entry.contentRect;
        if (newW > 0 && newH > 0 && cameraRef.current && rendererRef.current) {
          cameraRef.current.aspect = newW / newH;
          cameraRef.current.updateProjectionMatrix();
          rendererRef.current.setSize(newW, newH);
        }
      }
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      cancelAnimationFrame(animId);
      resizeObserver.disconnect();
      renderer.dispose();
    };
  }, []);

  const updateCameraPosition = () => {
    if (!cameraRef.current) return;
    const { theta, phi, distance } = cameraRotationRef.current;
    const x = distance * Math.sin(phi) * Math.cos(theta);
    const y = distance * Math.cos(phi);
    const z = distance * Math.sin(phi) * Math.sin(theta);
    cameraRef.current.position.set(x, Math.max(0.5, y), z);
    cameraRef.current.lookAt(0, 1.5, 0);
  };

  const buildPointCloudMesh = () => {
    if (!sceneRef.current) return;
    if (pointsMeshRef.current) sceneRef.current.remove(pointsMeshRef.current);

    const totalPoints = 32000;
    const cutoffY = (heightCutoff / 100) * 4.2;

    const positions = new Float32Array(totalPoints * 3);
    const colors = new Float32Array(totalPoints * 3);

    const classColors: Record<string, [number, number, number]> = {
      'IfcWallStandardCase': [0.9, 0.3, 0.3], // Red Wall
      'IfcColumn': [0.2, 0.8, 0.4],           // Green Column
      'IfcSlab': [0.3, 0.5, 0.9],             // Blue Slab
      'IfcDuctSegment': [0.95, 0.8, 0.2]      // Gold Duct
    };

    const classes = ['IfcWallStandardCase', 'IfcColumn', 'IfcSlab', 'IfcDuctSegment'];

    for (let i = 0; i < totalPoints; i++) {
      const rx = (Math.random() - 0.5) * 12;
      const ry = Math.random() * 4.0;
      const rz = (Math.random() - 0.5) * 10;

      if (ry > cutoffY) {
        positions[i * 3] = 0; positions[i * 3 + 1] = -100; positions[i * 3 + 2] = 0;
        continue;
      }

      positions[i * 3] = rx;
      positions[i * 3 + 1] = ry;
      positions[i * 3 + 2] = rz;

      const chosenClass = classes[i % classes.length];
      const rgb = classColors[chosenClass];
      colors[i * 3] = rgb[0];
      colors[i * 3 + 1] = rgb[1];
      colors[i * 3 + 2] = rgb[2];
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: pointSize * 0.02,
      vertexColors: true,
      transparent: true,
      opacity: 0.95
    });

    const pointsMesh = new THREE.Points(geometry, material);
    sceneRef.current.add(pointsMesh);
    pointsMeshRef.current = pointsMesh;
  };

  const buildBimBoxes = () => {
    if (!sceneRef.current) return;
    if (bimGroupRef.current) sceneRef.current.remove(bimGroupRef.current);

    const group = new THREE.Group();
    const boxes = [
      { name: 'Exterior Wall North', dims: [12.5, 3.8, 0.3], pos: [0, 1.9, -4.8], color: 0xef4444 },
      { name: 'Structural Column SE', dims: [0.45, 3.8, 0.45], pos: [5.0, 1.9, 3.0], color: 0x22c55e },
      { name: 'Structural Column SW', dims: [0.45, 3.8, 0.45], pos: [-5.0, 1.9, 3.0], color: 0x22c55e },
      { name: 'HVAC Duct', dims: [9.5, 0.4, 0.6], pos: [0, 3.2, 0], color: 0xeab308 }
    ];

    boxes.forEach(b => {
      const geom = new THREE.BoxGeometry(b.dims[0], b.dims[1], b.dims[2]);
      const edges = new THREE.EdgesGeometry(geom);
      const line = new THREE.LineSegments(
        edges,
        new THREE.LineBasicMaterial({ color: b.color, linewidth: 2 })
      );
      line.position.set(b.pos[0], b.pos[1], b.pos[2]);
      group.add(line);
    });

    group.visible = showWireframes;
    sceneRef.current.add(group);
    bimGroupRef.current = group;
  };

  const buildFrustums = () => {
    if (!sceneRef.current) return;
    if (frustumGroupRef.current) sceneRef.current.remove(frustumGroupRef.current);

    const group = new THREE.Group();
    const numCameras = 12;
    const radius = 8.5;

    for (let i = 0; i < numCameras; i++) {
      const angle = (i / numCameras) * Math.PI * 2;
      const cone = new THREE.Mesh(
        new THREE.ConeGeometry(0.3, 0.5, 4),
        new THREE.MeshBasicMaterial({ color: 0xf59e0b, wireframe: true })
      );
      cone.position.set(Math.cos(angle) * radius, 4.2 + Math.sin(i) * 0.8, Math.sin(angle) * radius);
      cone.lookAt(0, 1.5, 0);
      cone.rotateX(Math.PI / 2);
      group.add(cone);
    }

    group.visible = showFrustums;
    sceneRef.current.add(group);
    frustumGroupRef.current = group;
  };

  useEffect(() => { buildPointCloudMesh(); }, [colorMode, pointSize, heightCutoff]);
  useEffect(() => { if (bimGroupRef.current) bimGroupRef.current.visible = showWireframes; }, [showWireframes]);
  useEffect(() => { if (frustumGroupRef.current) frustumGroupRef.current.visible = showFrustums; }, [showFrustums]);

  const handleMouseDown = (e: React.MouseEvent) => {
    isDraggingRef.current = true;
    previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    const deltaX = e.clientX - previousMousePositionRef.current.x;
    const deltaY = e.clientY - previousMousePositionRef.current.y;
    cameraRotationRef.current.theta -= deltaX * 0.008;
    cameraRotationRef.current.phi = Math.max(0.1, Math.min(Math.PI / 2 - 0.05, cameraRotationRef.current.phi - deltaY * 0.008));
    updateCameraPosition();
    previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => { isDraggingRef.current = false; };
  const handleWheel = (e: React.WheelEvent) => {
    cameraRotationRef.current.distance = Math.max(3, Math.min(30, cameraRotationRef.current.distance + e.deltaY * 0.01));
    updateCameraPosition();
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/95 border border-slate-800 rounded-2xl overflow-hidden relative shadow-2xl">
      {/* Viewer Toolbar */}
      <div className="p-3 bg-slate-950/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs z-10">
        <div className="flex items-center space-x-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 font-bold px-2 uppercase">Semantic Shader</span>
          <button
            onClick={() => setColorMode('classification')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              colorMode === 'classification'
                ? 'bg-amber-500 text-slate-950 shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            PTv3 IFC Classes
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowWireframes(!showWireframes)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs transition-all ${
              showWireframes ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-slate-900 text-slate-400 border-slate-800'
            }`}
          >
            <Box className="w-3.5 h-3.5" /> Extracted IFC Wireframes ({showWireframes ? 'On' : 'Off'})
          </button>
          <button
            onClick={() => {
              cameraRotationRef.current = { theta: Math.PI / 4, phi: Math.PI / 3, distance: 14 };
              updateCameraPosition();
            }}
            className="p-1.5 text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-800 rounded-lg"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 3D Canvas */}
      <div
        ref={containerRef}
        className="flex-1 w-full min-h-[440px] relative cursor-grab active:cursor-grabbing select-none overflow-hidden"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
        <canvas ref={canvasRef} className="w-full h-full block" />

        {/* Controls Overlay */}
        <div className="absolute top-4 right-4 p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-3 backdrop-blur-md w-52 shadow-xl">
          <div className="font-semibold text-slate-200 text-[11px] uppercase tracking-wider flex items-center gap-1.5">
            <Sliders className="w-3 h-3 text-amber-400" /> Height Section Slice
          </div>
          <div className="space-y-1">
            <div className="flex justify-between text-[11px] text-slate-400">
              <span>Section Cutoff</span>
              <span className="font-mono text-amber-300 font-bold">{heightCutoff}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="100"
              step="5"
              value={heightCutoff}
              onChange={(e) => setHeightCutoff(parseInt(e.target.value))}
              className="w-full accent-amber-500 bg-slate-800 h-1 rounded cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* Telemetry Bar */}
      <div className="p-2.5 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400 px-4 font-mono">
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
          Semantic Classification: <span className="text-slate-200 font-bold">PTv3 (5 Classes Active)</span>
        </span>
        <span className="text-slate-500">Drag to Orbit • Scroll to Zoom</span>
      </div>
    </div>
  );
};
