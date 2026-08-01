"""Internal annotation format -- the one shape everything downstream speaks.

Every adapter (COCO, Label Studio, whatever Role 3 ships) converts INTO this.
Split / balance / export / eval never touch a vendor format directly, so when
the real annotation export arrives you write exactly one adapter file.

A box is normalized: cx, cy, w, h are all fractions of image size in [0, 1]
(YOLO convention). `cls` is a training class name from taxonomy.CLASSES.
`subtype` is the finer original label, kept for provenance, never trained on.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Box:
    cls: str              # training class (must be in taxonomy.CLASSES)
    cx: float             # center x, fraction of width  [0,1]
    cy: float             # center y, fraction of height [0,1]
    w: float              # width,  fraction of width    [0,1]
    h: float              # height, fraction of height   [0,1]
    subtype: Optional[str] = None  # original fine label, e.g. "double_door"

    def area(self) -> float:
        return self.w * self.h

    def valid(self) -> bool:
        return (0 <= self.cx <= 1 and 0 <= self.cy <= 1
                and 0 < self.w <= 1 and 0 < self.h <= 1)


@dataclass
class Image:
    file_name: str
    width: int
    height: int
    boxes: List[Box] = field(default_factory=list)


@dataclass
class Dataset:
    images: List[Image] = field(default_factory=list)

    def to_dict(self):
        return {"images": [asdict(im) for im in self.images]}

    @staticmethod
    def from_dict(d):
        ds = Dataset()
        for im in d["images"]:
            boxes = [Box(**b) for b in im.get("boxes", [])]
            ds.images.append(Image(file_name=im["file_name"], width=im["width"],
                                   height=im["height"], boxes=boxes))
        return ds
