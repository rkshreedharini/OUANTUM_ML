"""Pascal VOC XML -> internal schema adapter.

Handles a folder of VOC-style .xml annotations (one per image), each with
<size> and <object><name>/<bndbox>. Names resolve through classmap. Uses only
the stdlib XML parser.
"""

import os
import sys
import glob
import xml.etree.ElementTree as ET
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Dataset, Image, Box  # noqa: E402
import classmap  # noqa: E402


def load_voc(xml_dir, class_map=None):
    ds = Dataset()
    unmapped = Counter()
    for xf in sorted(glob.glob(os.path.join(xml_dir, "**", "*.xml"), recursive=True)):
        root = ET.parse(xf).getroot()
        size = root.find("size")
        W = int(size.findtext("width")) if size is not None else 0
        H = int(size.findtext("height")) if size is not None else 0
        fn = root.findtext("filename") or (os.path.splitext(os.path.basename(xf))[0] + ".png")
        img = Image(file_name=fn, width=W, height=H)
        for obj in root.findall("object"):
            name = obj.findtext("name")
            train_cls, how = classmap.resolve(name, class_map)
            if train_cls is None:
                unmapped[name] += 1
                continue
            bb = obj.find("bndbox")
            xmin, ymin = float(bb.findtext("xmin")), float(bb.findtext("ymin"))
            xmax, ymax = float(bb.findtext("xmax")), float(bb.findtext("ymax"))
            if not (W and H):
                continue
            box = Box(cls=train_cls, cx=(xmin + xmax) / 2 / W, cy=(ymin + ymax) / 2 / H,
                      w=(xmax - xmin) / W, h=(ymax - ymin) / H, subtype=name)
            if box.valid():
                img.boxes.append(box)
        ds.images.append(img)
    return ds, unmapped


if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("xml_dir")
    p.add_argument("--out", default="internal.json")
    args = p.parse_args()
    ds, unmapped = load_voc(args.xml_dir)
    json.dump(ds.to_dict(), open(args.out, "w"))
    print(f"wrote {args.out}: {len(ds.images)} images; unmapped={dict(unmapped)}")
