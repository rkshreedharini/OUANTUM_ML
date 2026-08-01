"""Confidence calibration -- required by the BuildingContext contract.

The frozen schema (workflow doc S4.2) specifies:

    class Provenance(BaseModel):
        confidence: float    # 0-1, CALIBRATED, not raw softmax

A raw YOLO objectness*class score is NOT calibrated: a detector that outputs
0.9 is typically right far less (or more) than 90% of the time. Emitting raw
scores as `confidence` would break the Context Engine's confidence gating
(S4.3 step 6), because its thresholds assume the number means what it says.

This module fits **Platt scaling** -- a 1-D logistic on the val-set
(score, is_true_positive) pairs -- per class, and reports Expected Calibration
Error before/after so the improvement is measurable rather than asserted.

Pure stdlib (no sklearn/torch), so it runs anywhere the rest of the CPU
pipeline runs and is unit-testable without a GPU.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402


def _sigmoid(z):
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)


def fit_platt(scored, lr=0.5, iters=2000, l2=1e-4):
    """Fit p = sigmoid(a*s + b) to [(score, is_tp), ...] by gradient descent.

    Uses the Platt-recommended smoothed targets to avoid overfitting when one
    outcome dominates. Returns (a, b).
    """
    n_pos = sum(1 for _, t in scored if t)
    n_neg = len(scored) - n_pos
    if not scored or n_pos == 0 or n_neg == 0:
        return 1.0, 0.0  # degenerate -> identity-ish, caller should note this
    hi = (n_pos + 1.0) / (n_pos + 2.0)
    lo = 1.0 / (n_neg + 2.0)

    a, b = 1.0, 0.0
    m = len(scored)
    for _ in range(iters):
        ga = gb = 0.0
        for s, t in scored:
            target = hi if t else lo
            p = _sigmoid(a * s + b)
            err = p - target
            ga += err * s
            gb += err
        ga = ga / m + l2 * a
        gb = gb / m
        a -= lr * ga
        b -= lr * gb
    return a, b


def apply_platt(score, a, b):
    return _sigmoid(a * score + b)


def expected_calibration_error(scored, n_bins=10, transform=None):
    """ECE: mean |confidence - accuracy| across equal-width confidence bins.
    Lower is better; 0 means the number means exactly what it says."""
    if not scored:
        return 0.0
    bins = [[] for _ in range(n_bins)]
    for s, t in scored:
        p = transform(s) if transform else s
        p = min(max(p, 0.0), 1.0)
        idx = min(int(p * n_bins), n_bins - 1)
        bins[idx].append((p, t))
    total = len(scored)
    ece = 0.0
    for b in bins:
        if not b:
            continue
        conf = sum(p for p, _ in b) / len(b)
        acc = sum(1 for _, t in b if t) / len(b)
        ece += (len(b) / total) * abs(conf - acc)
    return ece


def reliability_table(scored, n_bins=10, transform=None):
    """Per-bin (confidence, accuracy, count) -- the data behind a reliability
    diagram. Useful to log as an MLflow artifact."""
    bins = [[] for _ in range(n_bins)]
    for s, t in scored:
        p = transform(s) if transform else s
        p = min(max(p, 0.0), 1.0)
        bins[min(int(p * n_bins), n_bins - 1)].append((p, t))
    rows = []
    for i, b in enumerate(bins):
        if not b:
            rows.append({"bin": i, "conf": None, "acc": None, "n": 0})
            continue
        rows.append({"bin": i,
                     "conf": round(sum(p for p, _ in b) / len(b), 4),
                     "acc": round(sum(1 for _, t in b if t) / len(b), 4),
                     "n": len(b)})
    return rows


def fit_all(per_class_scored):
    """Fit a calibrator per class. Returns {cls: {a, b, ece_before, ece_after, n}}."""
    out = {}
    for cls in taxonomy.CLASSES:
        scored = per_class_scored.get(cls, [])
        a, b = fit_platt(scored)
        before = expected_calibration_error(scored)
        after = expected_calibration_error(scored, transform=lambda s: apply_platt(s, a, b))
        out[cls] = {"a": round(a, 6), "b": round(b, 6),
                    "ece_before": round(before, 4), "ece_after": round(after, 4),
                    "n": len(scored),
                    "degenerate": not scored or all(t for _, t in scored) or not any(t for _, t in scored)}
    return out


def save(calib, path):
    json.dump(calib, open(path, "w"), indent=2)


def load(path):
    return json.load(open(path))


def calibrate(score, cls, calib):
    """Apply the per-class calibrator to a raw detector score."""
    c = calib.get(cls)
    if not c or c.get("degenerate"):
        return score  # no trustworthy calibrator -> pass through, flagged upstream
    return apply_platt(score, c["a"], c["b"])


def print_table(calib):
    print(f"{'class':<10}{'n':>6}{'ECE before':>12}{'ECE after':>11}")
    for cls in taxonomy.CLASSES:
        c = calib[cls]
        flag = "  (degenerate -- passthrough)" if c["degenerate"] else ""
        print(f"{cls:<10}{c['n']:>6}{c['ece_before']:>12}{c['ece_after']:>11}{flag}")


if __name__ == "__main__":
    # Demo: a deliberately OVERCONFIDENT detector -- raw scores skew high
    # regardless of correctness, which is exactly what calibration must fix.
    import random
    rng = random.Random(0)
    scored = {}
    for cls in taxonomy.CLASSES:
        s = []
        for _ in range(400):
            s.append((min(0.999, abs(rng.gauss(0.85, 0.10))), True))
        for _ in range(300):
            s.append((min(0.999, abs(rng.gauss(0.75, 0.15))), False))
        scored[cls] = s
    calib = fit_all(scored)
    print_table(calib)
    print("\nreliability (door, after calibration):")
    a, b = calib["door"]["a"], calib["door"]["b"]
    for r in reliability_table(scored["door"], transform=lambda s: apply_platt(s, a, b)):
        if r["n"]:
            print(f"  bin {r['bin']}: conf={r['conf']}  acc={r['acc']}  n={r['n']}")
