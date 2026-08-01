"""Train/val/test split, stratified by rarest class first.

Stratifying detection data perfectly is impossible (an image holds many
classes), so we approximate: assign each image the label of its RAREST present
class, then split within each of those buckets. This keeps sparse classes
(stairs) proportionally represented in val/test instead of landing entirely in
one split by luck.

LEAKAGE NOTE: this splits by image. If several drawings come from the same
building, boxes leak between train and val. When Role 3 confirms a building id
per image, switch `group_key` to that id and split by group. The hook is here.

Pure stdlib. Deterministic given seed.
"""

import json
import os
import sys
import random
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Dataset  # noqa: E402
import taxonomy  # noqa: E402


def _rarity_order(ds):
    counts = Counter()
    for im in ds.images:
        for b in im.boxes:
            counts[b.cls] += 1
    # rarest class first
    return [c for c, _ in sorted(counts.items(), key=lambda kv: kv[1])]


def _bucket_of(image, rarity):
    present = {b.cls for b in image.boxes}
    for c in rarity:            # rarest first
        if c in present:
            return c
    return "__empty__"


def split(ds, ratios=(0.8, 0.1, 0.1), seed=42, group_key=None):
    assert abs(sum(ratios) - 1.0) < 1e-6, "ratios must sum to 1"
    rng = random.Random(seed)
    rarity = _rarity_order(ds)

    # group_key(image) -> group id. Default: each image is its own group.
    if group_key is None:
        group_key = lambda im: im.file_name  # noqa: E731

    # collect groups, tag each group by the rarest class it contains
    groups = defaultdict(list)
    for im in ds.images:
        groups[group_key(im)].append(im)

    buckets = defaultdict(list)
    for gid, imgs in groups.items():
        present = {b.cls for im in imgs for b in im.boxes}
        tag = "__empty__"
        for c in rarity:
            if c in present:
                tag = c
                break
        buckets[tag].append(gid)

    train, val, test = [], [], []
    for tag, gids in buckets.items():
        rng.shuffle(gids)
        n = len(gids)
        n_tr = int(round(n * ratios[0]))
        n_va = int(round(n * ratios[1]))
        for gid in gids[:n_tr]:
            train += groups[gid]
        for gid in gids[n_tr:n_tr + n_va]:
            val += groups[gid]
        for gid in gids[n_tr + n_va:]:
            test += groups[gid]

    return {"train": train, "val": val, "test": test}


def _split_counts(images):
    c = Counter()
    for im in images:
        for b in im.boxes:
            c[b.cls] += 1
    return {cl: c[cl] for cl in taxonomy.CLASSES}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("internal_json")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="splits.json")
    args = p.parse_args()
    ds = Dataset.from_dict(json.load(open(args.internal_json)))
    sp = split(ds, seed=args.seed)
    out = {k: [im.file_name for im in v] for k, v in sp.items()}
    json.dump(out, open(args.out, "w"), indent=2)
    for name in ("train", "val", "test"):
        print(f"{name:<6} {len(sp[name]):>4} images  per-class: {_split_counts(sp[name])}")
    print(f"wrote {args.out}")
