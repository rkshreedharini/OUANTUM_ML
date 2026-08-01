# Role 5 — Wall/Room Segmentation Baseline

Semantic segmentation baseline for architectural floor plans: classifies each
pixel into wall / room / background categories, producing the wall and room
geometry the Context Engine needs to place openings on.

## Model

| setting | value |
|---|---|
| architecture | DeepLabV3+ (`segmentation-models-pytorch`) |
| encoder | ResNet-50 |
| classes | 5 |
| epochs | 15 |
| batch size | 4 |
| learning rate | 1e-4 |
| metric | IoU (torchmetrics) |
| dataset | CubiCasa5K (`high_quality_architectural`) |

Trained on GPU (Kaggle/Colab). `predictions.png` shows the qualitative result:
input image / ground-truth mask / predicted mask for four validation samples.

## Contents

```
train_segmentation.py   training script (exported from the training notebook)
masks.zip               3,725 rasterized ground-truth masks generated from the
                        CubiCasa5K SVG annotations (unzip to ./masks/)
predictions.png         qualitative results — image vs ground truth vs prediction
```

## Trained weights

`best_model.pth` is **107 MB**, which exceeds GitHub's 100 MB per-file hard
limit, so it is not committed here. To obtain it:

- request the file from the Role 5 owner, or
- re-run `train_segmentation.py` (~15 epochs on a T4), or
- have it attached to a GitHub Release, which permits files up to 2 GB.

## Reproducing

```bash
pip install segmentation-models-pytorch albumentations opencv-python torchmetrics cairosvg
unzip masks.zip
python train_segmentation.py
```

The script expects CubiCasa5K under the dataset path defined near the top of the
file; adjust that path for your environment (it currently points at the Kaggle
working directory used for the original run).

## Notes

`train_segmentation.py` is the linear export of an exploratory training
notebook, so it retains the environment-setup and path-discovery cells from the
original session. The training logic starts at the dataset/model definition.

## Position in the pipeline

Upstream: Data & Annotation pod (CubiCasa5K + client drawings).
Downstream: the **Context Engine**, which skeletonizes these masks into wall
centerlines and then attaches Role 7's detected door/window openings to them.
Role 6 builds the production dual-branch model once this baseline plateaus.
