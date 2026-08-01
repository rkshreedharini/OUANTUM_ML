"""Per-class confidence thresholds via F-beta maximisation.

NOT a single global threshold. Each class gets its own cutoff chosen to
maximise F-beta on the validation precision-recall curve, with beta set per
class by structural importance (taxonomy.CLASS_BETA):

  door, window  beta=2.0  favour recall  -- a missed opening becomes a solid
                                            wall downstream and nothing flags it;
                                            a false one dies in the review queue.
  stair         beta=1.0  balanced
  fixture       beta=0.5  favour precision -- nothing downstream consumes
                                            fixtures, so false ones are pure noise.

Input is a per-class list of (confidence, is_true_positive) pairs plus the
number of ground-truth instances for that class (needed for recall). This is
model-agnostic: `evaluate.py` produces these from val predictions; the pure
selection logic below has no torch dependency and is unit-testable on CPU.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402


def _pr_at_threshold(scored, n_gt, thr):
    tp = sum(1 for conf, is_tp in scored if conf >= thr and is_tp)
    fp = sum(1 for conf, is_tp in scored if conf >= thr and not is_tp)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / n_gt if n_gt else 0.0
    return precision, recall


def fbeta(precision, recall, beta):
    b2 = beta * beta
    denom = b2 * precision + recall
    if denom == 0:
        return 0.0
    return (1 + b2) * precision * recall / denom


def best_threshold(scored, n_gt, beta, floor=0.05, ceil=0.90, steps=91):
    """Sweep candidate thresholds, return the one maximising F-beta (clamped)."""
    best = {"thr": floor, "fbeta": -1.0, "precision": 0.0, "recall": 0.0}
    for i in range(steps):
        thr = floor + (ceil - floor) * i / (steps - 1)
        p, r = _pr_at_threshold(scored, n_gt, thr)
        fb = fbeta(p, r, beta)
        if fb > best["fbeta"]:
            best = {"thr": round(thr, 3), "fbeta": round(fb, 4),
                    "precision": round(p, 4), "recall": round(r, 4)}
    return best


def compute_all(per_class_scored, per_class_gt, beta_map=None, floor=0.05, ceil=0.90):
    """
    per_class_scored: {cls: [(conf, is_tp), ...]}
    per_class_gt:     {cls: n_ground_truth}
    Returns: {cls: best_threshold_dict} plus a flat {cls: thr} for thresholds.json
    """
    beta_map = beta_map or taxonomy.CLASS_BETA
    detail, flat = {}, {}
    for cls in taxonomy.CLASSES:
        scored = per_class_scored.get(cls, [])
        n_gt = per_class_gt.get(cls, 0)
        beta = beta_map[cls]
        b = best_threshold(scored, n_gt, beta, floor, ceil)
        b["beta"] = beta
        detail[cls] = b
        flat[cls] = b["thr"]
    return detail, flat


def save(flat, detail, out_dir="."):
    json.dump(flat, open(os.path.join(out_dir, "thresholds.json"), "w"), indent=2)
    json.dump(detail, open(os.path.join(out_dir, "thresholds_detail.json"), "w"), indent=2)


def print_table(detail):
    print(f"{'class':<10}{'beta':>5}{'thr':>7}{'prec':>7}{'recall':>8}{'Fb':>7}")
    for cls in taxonomy.CLASSES:
        d = detail[cls]
        print(f"{cls:<10}{d['beta']:>5}{d['thr']:>7}{d['precision']:>7}{d['recall']:>8}{d['fbeta']:>7}")


if __name__ == "__main__":
    # Demo on synthetic PR data so the asymmetry is visible without a trained model.
    import random
    rng = random.Random(0)
    scored, gt = {}, {}
    for cls in taxonomy.CLASSES:
        n = 300
        gt[cls] = n
        s = []
        for _ in range(n):                         # true positives: high-ish conf
            s.append((min(1.0, rng.gauss(0.7, 0.15)), True))
        for _ in range(int(n * 0.6)):              # false positives: lower conf
            s.append((max(0.0, rng.gauss(0.4, 0.15)), False))
        scored[cls] = s
    detail, flat = compute_all(scored, gt)
    print_table(detail)
    print("\nflat thresholds.json ->", flat)
