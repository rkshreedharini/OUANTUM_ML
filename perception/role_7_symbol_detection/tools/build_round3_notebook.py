"""Generates BIM_Vision_Role7_Round3.ipynb. Run: python tools/build_round3_notebook.py

Round 3 = round 2 + the transform fix (v7) + a MANDATORY visual label check
between ingest and training. Lesson learned: round 2 burned 2 GPU-hours on
displaced labels no one had looked at. Now the notebook shows you the boxes
and stops; training is a separate cell you run after eyeballing them.
"""
import json, os

def md(*l): return {"cell_type": "markdown", "metadata": {}, "source": [x + "\n" for x in l]}
def code(*l): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": [x + "\n" for x in l]}

cells = [
  md("# Role 7 — Round 3 (transform-fixed labels)",
     "**Before running: Runtime → Change runtime type → T4 GPU → Save.**",
     "",
     "Run cells top to bottom. One file-pick (`bim-vision-detection-v7.zip`).",
     "**Cell 5 shows the ground-truth boxes drawn on real plans — LOOK at them",
     "before running the training cell.** Boxes on doors/windows = proceed.",
     "Boxes floating in margins = stop and tell Claude."),

  code("# 1. GPU + deps",
       "import torch",
       "assert torch.cuda.is_available(), 'NO GPU: Runtime > Change runtime type > T4 GPU'",
       "print('GPU:', torch.cuda.get_device_name(0))",
       "!pip -q install pyyaml ultralytics mlflow"),

  code("# 2. pipeline code (pick bim-vision-detection-v7.zip)",
       "import os",
       "os.chdir('/content')",
       "from google.colab import files",
       "up = files.upload()",
       "os.system(f'rm -rf bim-vision-detection && unzip -oq \"{next(iter(up))}\"')",
       "os.chdir('/content/bim-vision-detection')",
       "print(sorted(os.listdir('.')))"),

  code("# 3. CubiCasa5k (resumable; ~35 min on a fresh session)",
       "assert os.system('wget -cq -O cubicasa5k.zip \"https://zenodo.org/records/2613548/files/cubicasa5k.zip?download=1\"') == 0, 'download failed - re-run this cell'",
       "if not os.path.isdir('cubicasa_raw'):",
       "    assert os.system('unzip -q cubicasa5k.zip -d cubicasa_raw') == 0",
       "print('dataset ready')"),

  code("# 4. ingest 1200 plans with TRANSFORM-AWARE adapter",
       "assert os.system('python src/ingest.py --input cubicasa_raw --out yolo_dataset --limit 1200') == 0"),

  code("# 5. *** VISUAL LABEL CHECK -- LOOK BEFORE TRAINING ***",
       "import matplotlib.pyplot as plt, matplotlib.patches as mpatches",
       "from PIL import Image as PILImage",
       "img_dir, lbl_dir = 'yolo_dataset/images/train', 'yolo_dataset/labels/train'",
       "colors = {0:'red',1:'blue',2:'green',3:'orange'}",
       "files_ = sorted(os.listdir(img_dir))[:4]",
       "fig, axes = plt.subplots(1, 4, figsize=(32, 8))",
       "for ax, fn in zip(axes, files_):",
       "    im = PILImage.open(os.path.join(img_dir, fn)); W, H = im.size",
       "    ax.imshow(im)",
       "    for line in open(os.path.join(lbl_dir, os.path.splitext(fn)[0] + '.txt')):",
       "        c, cx, cy, w, h = map(float, line.split())",
       "        ax.add_patch(mpatches.Rectangle(((cx-w/2)*W, (cy-h/2)*H), w*W, h*H,",
       "                     fill=False, edgecolor=colors[int(c)], linewidth=1.5))",
       "    ax.set_title(fn[:35]); ax.axis('off')",
       "plt.tight_layout(); plt.show()",
       "print('red=door blue=window green=stair orange=fixture')",
       "print('Boxes ON the symbols? -> run the next cell. Floating in margins? -> STOP, tell Claude.')"),

  code("# 6. train: 50 epochs, yolo11s, imgsz 1024 (~1.5-2 h)  -- run AFTER checking cell 5",
       "import yaml",
       "cfg = yaml.safe_load(open('configs/base.yaml'))",
       "cfg['model'].update(arch='yolo11s', pretrained='yolo11s.pt')",
       "cfg['train'].update(epochs=50, batch=8, patience=15)",
       "yaml.safe_dump(cfg, open('configs/round3.yaml', 'w'), sort_keys=False)",
       "assert os.system('python src/train.py --config configs/round3.yaml --data yolo_dataset/data.yaml') == 0"),

  code("# 7. evaluate + calibrate + thresholds + handoff + bundle",
       "import glob, json",
       "cands = glob.glob('runs/**/best.pt', recursive=True)",
       "W = max(cands, key=os.path.getmtime)",
       "print('weights:', W)",
       "assert os.system(f'python src/evaluate.py --config configs/round3.yaml --data yolo_dataset/data.yaml --weights {W} --out eval_out') == 0",
       "img = 'yolo_dataset/images/test/' + sorted(os.listdir('yolo_dataset/images/test'))[0]",
       "os.system(f'python src/infer.py --weights {W} --thresholds eval_out/thresholds.json --calibration eval_out/calibration.json --image {img} --out handoff.json')",
       "os.system(f'zip -qj role7_round3_results.zip eval_out/*.json handoff.json {W} configs/round3.yaml')",
       "print('thresholds:', json.load(open('eval_out/thresholds.json')))",
       "from google.colab import files",
       "files.download('role7_round3_results.zip')"),
]

nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"},
                   "language_info": {"name": "python"}, "accelerator": "GPU"},
      "nbformat": 4, "nbformat_minor": 5}
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "notebooks", "BIM_Vision_Role7_Round3.ipynb")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
print("wrote", out, "-", len(cells), "cells")
