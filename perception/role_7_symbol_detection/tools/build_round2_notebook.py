"""Generates BIM_Vision_Role7_Round2.ipynb -- the run-everything notebook.
Run: python tools/build_round2_notebook.py"""
import json, os

def md(*l): return {"cell_type": "markdown", "metadata": {}, "source": [x + "\n" for x in l]}
def code(*l): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": [x + "\n" for x in l]}

cells = [
  md("# Role 7 — Round 2: full training run",
     "**Before running: Runtime → Change runtime type → T4 GPU → Save.**",
     "",
     "Then **Runtime → Run all**. One file-pick when prompted (`bim-vision-detection-v6.zip`),",
     "everything else is automatic. Total ~2–3 hours: ~35 min download, ~1.5–2 h training.",
     "Keep the tab open. At the end `role7_round2_results.zip` downloads itself."),

  code("# 1. GPU + deps",
       "import torch",
       "assert torch.cuda.is_available(), 'NO GPU: Runtime > Change runtime type > T4 GPU, then Run all again'",
       "print('GPU:', torch.cuda.get_device_name(0))",
       "!pip -q install pyyaml ultralytics mlflow"),

  code("# 2. pipeline code (pick bim-vision-detection-v6.zip)",
       "import os",
       "os.chdir('/content')",
       "from google.colab import files",
       "up = files.upload()",
       "os.system(f'rm -rf bim-vision-detection && unzip -oq \"{next(iter(up))}\"')",
       "os.chdir('/content/bim-vision-detection')",
       "print(sorted(os.listdir('.')))"),

  code("# 3. clone Data & Annotation pod repo -- print what's ACTUALLY in it",
       "os.system('rm -rf /content/BIM_Vision && git -C /content clone -q https://github.com/Jerlin-Ishabel/BIM_Vision.git')",
       "print('=== datasets/ ==='); os.system('find /content/BIM_Vision/datasets -type f | head -20')",
       "print('=== annotations/exports/ ==='); os.system('ls -la /content/BIM_Vision/annotations/exports/ 2>/dev/null')",
       "print('=== annotations/labels/ ==='); os.system('ls -la /content/BIM_Vision/annotations/labels/ 2>/dev/null')",
       "# if they shipped a real Label Studio export, ingest-report it (too few images to train on alone)",
       "import glob, subprocess, sys",
       "exports = glob.glob('/content/BIM_Vision/annotations/exports/*.json')",
       "if exports:",
       "    print(f'\\nFound {len(exports)} export(s) -- parsing with the labelstudio adapter:')",
       "    for e in exports:",
       "        subprocess.run([sys.executable, 'src/adapters/labelstudio.py', e, '--out', '/tmp/ls_internal.json'])",
       "else:",
       "    print('\\nNo annotation exports in their repo yet -- training on CubiCasa5k as planned.')"),

  code("# 4. CubiCasa5k (resumable; ~35 min)",
       "import os",
       "assert os.system('wget -cq -O cubicasa5k.zip \"https://zenodo.org/records/2613548/files/cubicasa5k.zip?download=1\"') == 0, 'download failed - re-run this cell'",
       "if not os.path.isdir('cubicasa_raw'):",
       "    assert os.system('unzip -q cubicasa5k.zip -d cubicasa_raw') == 0",
       "print('dataset ready')"),

  code("# 5. ingest 1200 plans (dedupe active in v6)",
       "assert os.system('python src/ingest.py --input cubicasa_raw --out yolo_dataset --limit 1200') == 0"),

  code("# 6. train: 50 epochs, yolo11s, imgsz 1024  (~1.5-2 h on T4)",
       "import yaml",
       "cfg = yaml.safe_load(open('configs/base.yaml'))",
       "cfg['model'].update(arch='yolo11s', pretrained='yolo11s.pt')",
       "cfg['train'].update(epochs=50, batch=8, patience=15)",
       "yaml.safe_dump(cfg, open('configs/round2.yaml', 'w'), sort_keys=False)",
       "assert os.system('python src/train.py --config configs/round2.yaml --data yolo_dataset/data.yaml') == 0, 'training failed - run the command manually with 2>&1|tail -40 to see why'"),

  code("# 7. locate weights robustly (Ultralytics nests run dirs unpredictably)",
       "import glob, os",
       "cands = glob.glob('runs/**/best.pt', recursive=True)",
       "assert cands, 'no best.pt found under runs/'",
       "W = max(cands, key=os.path.getmtime)",
       "print('weights:', W)"),

  code("# 8. evaluate + calibrate + thresholds (the deliverable numbers)",
       "assert os.system(f'python src/evaluate.py --config configs/round2.yaml --data yolo_dataset/data.yaml --weights {W} --out eval_out') == 0",
       "import json",
       "print('\\nthresholds:', json.load(open('eval_out/thresholds.json')))"),

  code("# 9. handoff demo + results bundle (auto-downloads)",
       "img = 'yolo_dataset/images/test/' + sorted(os.listdir('yolo_dataset/images/test'))[0]",
       "os.system(f'python src/infer.py --weights {W} --thresholds eval_out/thresholds.json --calibration eval_out/calibration.json --image {img} --out handoff.json')",
       "os.system(f'zip -qj role7_round2_results.zip eval_out/*.json handoff.json {W} configs/round2.yaml')",
       "import json",
       "h = json.load(open('handoff.json'))",
       "print('handoff:', len(h['opening_candidates']), 'openings,', len(h['symbols']), 'symbols, calibrated =', h['meta']['calibrated'])",
       "from google.colab import files",
       "files.download('role7_round2_results.zip')",
       "print('\\nROUND 2 COMPLETE -- send the mAP table + this zip to Claude')"),
]

nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"},
                   "language_info": {"name": "python"}, "accelerator": "GPU"},
      "nbformat": 4, "nbformat_minor": 5}
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "notebooks", "BIM_Vision_Role7_Round2.ipynb")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
print("wrote", out, "-", len(cells), "cells")
