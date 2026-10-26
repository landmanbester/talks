#!/usr/bin/env python3
"""List the images on each slide of a PPTX export, in presentation order.

The slideN.xml file names inside a PPTX are not the presentation order (slides
moved in Google Slides keep their old numbers); presentation.xml is. Use this
to find which ppt/media/ file is on the slide you want to reuse.

    python3 -I scripts/pptx_media.py deck.pptx            # every slide
    python3 -I scripts/pptx_media.py deck.pptx 58,59,72   # just these

Stdlib only.
"""

import re
import sys
import zipfile
from pathlib import PurePosixPath


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    z = zipfile.ZipFile(sys.argv[1])
    pres = z.read("ppt/presentation.xml").decode()
    rels = z.read("ppt/_rels/presentation.xml.rels").decode()
    target = {}
    for rel in re.findall(r"<Relationship [^>]*>", rels):
        rid = re.search(r'Id="([^"]+)"', rel).group(1)
        target[rid] = re.search(r'Target="([^"]+)"', rel).group(1)
    order = [target[r] for r in re.findall(r'<p:sldId [^>]*r:id="([^"]+)"', pres)]
    pages = (range(1, len(order) + 1) if len(sys.argv) < 3
             else [int(p) for p in sys.argv[2].split(",")])
    for p in pages:
        name = PurePosixPath(order[p - 1]).name
        srels = z.read(f"ppt/slides/_rels/{name}.rels").decode()
        media = re.findall(r'Target="\.\./media/([^"]+)"', srels)
        print(f"{p:3d}  {name:14s} {' '.join(media)}")


if __name__ == "__main__":
    main()
