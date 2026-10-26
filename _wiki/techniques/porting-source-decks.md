---
type: Technique
title: Getting content out of Google Slides and Canva
description: Export a source deck's text, page renders and original images (Google Slides via rclone PPTX/PDF, Canva via the connector) before porting.
tags: [porting, canva, google-slides, images]
timestamp: 2026-10-26
---

# Getting content out of Google Slides and Canva

Port from the source's **text and original images**, never from cut-outs of screenshots. Keep the
exports on `/data/talks/reference/<source>/` (not in the repo); copy only the images a deck uses
into its `images/`. Reference: `lectures/rime` (two Google Slides decks plus a Canva build).

## Google Slides

1. **Text**: the Google Drive connector's `read_file_content` on the file ID gives every slide's
   text. Equations are embedded objects and do not come through.
2. **Exports**: the `talks-drive:` rclone remote can export by file ID, wherever the file lives.
   One format per call (a comma list exports only the first):
   ```bash
   rclone backend copyid talks-drive: <file-id> <dir>/ --drive-export-formats pptx
   rclone backend copyid talks-drive: <file-id> <dir>/ --drive-export-formats pdf
   ```
3. **Images**: a PPTX is a zip; `ppt/media/` holds every image at its original resolution.
   `python3 -I scripts/pptx_media.py deck.pptx 58,72` says which media file is on which slide (the
   `slideN.xml` names are not the presentation order).
4. **Looking at slides**: `pdftoppm -r 60 -f A -l B` on the PDF, then `montage` six to a sheet —
   one image read per six slides. Speaker notes (`ppt/notesSlides/`) may be empty; slides built
   from animations or embedded video can export blank — check the page render.

## Canva

1. **Text first**: `read-design` with `design_content` and `presenter_notes` for the pages you
   want (cheap). Thumbnails are expensive; pages that are all graphics return almost no text.
2. **Page images**: `export-design` with `type: png`, `pages: [...]`, `width: 1600` returns
   signed download URLs — `curl` them into `/data/talks/reference/canva-<id>/` and contact-sheet
   them. This gives whole pages (good for reading a build, or for a page-sized image); it does not
   separate a page's individual image assets.
3. Record the design ID on the deck's wiki page so later passes can go straight back to it.

Then build the slides natively — [build-up figures](build-up-figures.md) for click-by-click
annotation, manim for anything that moves ([stepping](manim-slides-stepping.md)).
