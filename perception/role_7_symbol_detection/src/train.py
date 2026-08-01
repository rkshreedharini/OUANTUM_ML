"""Config-driven YOLOv11 fine-tuning with MLflow tracking.

*** GPU REQUIRED for the training loop. *** Everything upstream (adapter,
balance, split, export) runs on CPU; only this step needs a GPU. Run it on the
GPU machine / Colab. It is resumable and logs every run to MLflow from the
start (not bolted on at the end).

Usage:
    python src/train.py --config configs/base.yaml --data yolo_dataset/data.yaml
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_config(path):
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/base.yaml")
    ap.add_argument("--data", required=True, help="path to data.yaml from export_yolo")
    ap.add_argument("--rtdetr", action="store_true", help="train RT-DETR instead of YOLO")
    args = ap.parse_args()

    cfg = load_config(args.config)

    # Imports deferred so the rest of the pipeline never needs torch installed.
    import mlflow
    from ultralytics import YOLO, RTDETR

    mlflow.set_tracking_uri(cfg["mlflow"]["tracking_uri"])
    mlflow.set_experiment(cfg["mlflow"]["experiment"])

    if args.rtdetr:
        arch = cfg["rtdetr"]["arch"]
        model = RTDETR(arch + ".pt")
        run_name = f"rtdetr-{arch}"
    else:
        model = YOLO(cfg["model"]["pretrained"])
        run_name = f"yolo-{cfg['model']['arch']}"

    aug = cfg["train"]["augment"]
    with mlflow.start_run(run_name=run_name):
        # log hyperparameters up front
        mlflow.log_params({
            "arch": run_name, "imgsz": cfg["model"]["imgsz"],
            "epochs": cfg["train"]["epochs"], "batch": cfg["train"]["batch"],
            "lr0": cfg["train"]["lr0"], "seed": cfg["seed"],
        })

        results = model.train(
            data=args.data,
            epochs=cfg["train"]["epochs"],
            imgsz=cfg["model"]["imgsz"],
            batch=cfg["train"]["batch"],
            patience=cfg["train"]["patience"],
            optimizer=cfg["train"]["optimizer"],
            lr0=cfg["train"]["lr0"],
            seed=cfg["seed"],
            project="runs", name=run_name, exist_ok=True, resume=False,
            **aug,
        )

        # per-class + overall metrics
        try:
            metrics = model.val(data=args.data, split="val")
            mlflow.log_metric("mAP50", float(metrics.box.map50))
            mlflow.log_metric("mAP50_95", float(metrics.box.map))
            import taxonomy
            for i, cls in enumerate(taxonomy.CLASSES):
                try:
                    mlflow.log_metric(f"mAP50_{cls}", float(metrics.box.maps[i]))
                except Exception:
                    pass
        except Exception as e:
            print("val metric logging skipped:", e)

        best = os.path.join("runs", run_name, "weights", "best.pt")
        if os.path.exists(best):
            mlflow.log_artifact(best)
        print("best weights:", best)


if __name__ == "__main__":
    main()
