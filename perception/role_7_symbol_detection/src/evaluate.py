"""Evaluation, calibration fitting, and threshold derivation.

*** Needs trained weights (GPU). *** Produces, all logged to MLflow:
  - per-class mAP@0.5           <- Role 7's named deliverable
  - confusion matrix + val plots (Ultralytics)
  - calibration.json            <- Platt params per class + ECE before/after
  - thresholds.json             <- per-class F-beta cutoffs on CALIBRATED conf

Order matters: calibrate FIRST, then pick thresholds on the calibrated scores.
Thresholds chosen on raw scores would be meaningless once inference calibrates.

Usage:
    python src/evaluate.py --config configs/base.yaml --data yolo_dataset/data.yaml \
        --weights runs/yolo-yolo11m/weights/best.pt --out eval_out
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy          # noqa: E402
import thresholds as th  # noqa: E402
import calibration       # noqa: E402


def _iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    ua = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / ua if ua > 0 else 0.0


def collect_scores(model, data_yaml, split="val", iou_thr=0.5):
    """Match predictions to GT on the val split -> per-class (score, is_tp)
    lists + GT counts. Greedy highest-score-first matching, one GT per pred."""
    import yaml
    cfg = yaml.safe_load(open(data_yaml))
    base = cfg["path"]
    img_dir = os.path.join(base, "images", split)
    lbl_dir = os.path.join(base, "labels", split)

    per_class_scored = {c: [] for c in taxonomy.CLASSES}
    per_class_gt = {c: 0 for c in taxonomy.CLASSES}

    for fn in sorted(os.listdir(img_dir)):
        stem = os.path.splitext(fn)[0]
        gts = []
        lp = os.path.join(lbl_dir, stem + ".txt")
        if os.path.exists(lp):
            for line in open(lp):
                parts = line.split()
                if len(parts) != 5:
                    continue
                cid = int(float(parts[0]))
                cx, cy, w, h = map(float, parts[1:])
                gts.append((cid, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)))
        for cid, _ in gts:
            per_class_gt[taxonomy.ID_TO_CLASS[cid]] += 1

        res = model.predict(os.path.join(img_dir, fn), conf=0.001, verbose=False)[0]
        preds = []
        for b in res.boxes:
            cx, cy, w, h = b.xywhn[0].tolist()
            preds.append((int(b.cls), float(b.conf),
                          (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)))
        preds.sort(key=lambda p: -p[1])

        used = set()
        for cid, score, box in preds:
            match = None
            for j, (gcid, gbox) in enumerate(gts):
                if j in used or gcid != cid:
                    continue
                if _iou(box, gbox) >= iou_thr:
                    match = j
                    break
            if match is not None:
                used.add(match)
            per_class_scored[taxonomy.ID_TO_CLASS[cid]].append((score, match is not None))

    return per_class_scored, per_class_gt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/base.yaml")
    ap.add_argument("--data", required=True)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--out", default="eval_out")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    import yaml
    import mlflow
    from ultralytics import YOLO
    cfg = yaml.safe_load(open(args.config))

    mlflow.set_tracking_uri(cfg["mlflow"]["tracking_uri"])
    mlflow.set_experiment(cfg["mlflow"]["experiment"])
    model = YOLO(args.weights)

    with mlflow.start_run(run_name="eval"):
        # ---- 1. per-class mAP@0.5 (the named deliverable) ----
        metrics = model.val(data=args.data, split="val", plots=True)
        print(f"{'class':<10}{'mAP@0.5':>10}")
        print(f"{'ALL':<10}{metrics.box.map50:>10.4f}")
        mlflow.log_metric("mAP50_all", float(metrics.box.map50))
        mlflow.log_metric("mAP50_95_all", float(metrics.box.map))
        for i, cls in enumerate(taxonomy.CLASSES):
            try:
                m = float(metrics.box.maps[i])
                print(f"{cls:<10}{m:>10.4f}")
                mlflow.log_metric(f"mAP50_{cls}", m)
            except Exception:
                pass

        # ---- 2. calibrate BEFORE thresholding ----
        scored, gt = collect_scores(model, args.data)
        calib = calibration.fit_all(scored)
        calibration.save(calib, os.path.join(args.out, "calibration.json"))
        print("\n--- calibration (contract: confidence must be calibrated) ---")
        calibration.print_table(calib)
        for cls in taxonomy.CLASSES:
            mlflow.log_metric(f"ece_before_{cls}", calib[cls]["ece_before"])
            mlflow.log_metric(f"ece_after_{cls}", calib[cls]["ece_after"])
        json.dump({c: calibration.reliability_table(
                       scored[c],
                       transform=lambda s, c=c: calibration.calibrate(s, c, calib))
                   for c in taxonomy.CLASSES},
                  open(os.path.join(args.out, "reliability.json"), "w"), indent=2)

        # ---- 3. thresholds on CALIBRATED confidence ----
        cal_scored = {c: [(calibration.calibrate(s, c, calib), t) for s, t in scored[c]]
                      for c in taxonomy.CLASSES}
        thc = cfg["thresholds"]
        detail, flat = th.compute_all(cal_scored, gt, beta_map=thc["beta"],
                                      floor=thc["floor"], ceil=thc["ceil"])
        th.save(flat, detail, args.out)
        print("\n--- per-class thresholds (F-beta on calibrated confidence) ---")
        th.print_table(detail)
        for cls in taxonomy.CLASSES:
            mlflow.log_metric(f"threshold_{cls}", detail[cls]["thr"])
            mlflow.log_metric(f"precision_{cls}", detail[cls]["precision"])
            mlflow.log_metric(f"recall_{cls}", detail[cls]["recall"])

        for f in ("thresholds.json", "thresholds_detail.json", "calibration.json",
                  "reliability.json"):
            p = os.path.join(args.out, f)
            if os.path.exists(p):
                mlflow.log_artifact(p)
        save_dir = str(getattr(metrics, "save_dir", "") or "")
        if save_dir and os.path.isdir(save_dir):
            mlflow.log_artifacts(save_dir, artifact_path="val_plots")

        print("\nwrote calibration.json + thresholds.json to", args.out)


if __name__ == "__main__":
    main()
