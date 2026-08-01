"""Generate a synthetic COCO instances file so the whole CPU pipeline runs
before any real annotation data exists.

Class frequencies are deliberately skewed to mimic real floor plans: doors and
windows dominate, stairs are sparse. Fixtures are emitted as realistic FINE
labels (toilet/sink/bathtub) so the adapter's subtype-mapping path
(fine label -> 'fixture') gets exercised, and two 'nuisance' categories
(dimension_line, north_arrow) are NOT in the class map -- so the unmapped
reporting path gets exercised too. Doors/windows are made tiny to trigger the
tiny-object warning. Pure stdlib.
"""

import json
import random
import argparse

# name -> (approx weight, tiny?)
SPEC = [
    ("door", 30, True),
    ("double_door", 15, True),    # -> door via class_map
    ("window", 34, True),
    ("toilet", 6, False),         # -> fixture
    ("sink", 6, False),           # -> fixture
    ("bathtub", 4, False),        # -> fixture
    ("stair", 5, False),
    ("dimension_line", 0, False), # nuisance, unmapped
    ("north_arrow", 0, False),    # nuisance, unmapped
]


def make(out_path, n_images=120, boxes_per_image=15, seed=7):
    rng = random.Random(seed)
    categories = [{"id": i + 1, "name": name} for i, (name, _, _) in enumerate(SPEC)]
    name_to_id = {c["name"]: c["id"] for c in categories}
    tiny = {name for name, _, t in SPEC if t}

    weighted = []
    for name, weight, _ in SPEC:
        weighted += [name] * weight
    # a handful of nuisance boxes regardless of weight
    weighted += ["dimension_line"] * 6 + ["north_arrow"] * 5

    images, annotations = [], []
    ann_id = 1
    for i in range(n_images):
        W, H = 2000, 1500
        images.append({"id": i, "file_name": f"plan_{i:04d}.png", "width": W, "height": H})
        for _ in range(rng.randint(boxes_per_image - 4, boxes_per_image + 4)):
            name = rng.choice(weighted)
            if name in tiny:
                w, h = rng.randint(20, 45), rng.randint(20, 45)      # ~0.05% of image
            else:
                w, h = rng.randint(80, 220), rng.randint(80, 220)
            x = rng.randint(0, W - w)
            y = rng.randint(0, H - h)
            annotations.append({
                "id": ann_id, "image_id": i, "category_id": name_to_id[name],
                "bbox": [x, y, w, h], "area": w * h, "iscrowd": 0,
            })
            ann_id += 1

    coco = {"images": images, "annotations": annotations, "categories": categories}
    with open(out_path, "w") as f:
        json.dump(coco, f)
    print(f"wrote {out_path}: {len(images)} images, {len(annotations)} boxes")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="fake_coco.json")
    p.add_argument("--n", type=int, default=120)
    args = p.parse_args()
    make(args.out, n_images=args.n)
