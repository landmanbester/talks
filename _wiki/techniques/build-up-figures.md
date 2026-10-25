---
type: Technique
title: Build-up figures
description: Annotations appearing one click at a time on a photo or diagram, as transparent PNG frames in an r-stack.
tags: [figures, fragments, canva]
timestamp: 2026-10-25
---

# Build-up figures

For annotations appearing one click at a time on a photo or diagram (as Canva builds do): don't
position HTML over the image. Draw each step as a **transparent PNG on the same canvas, each a
superset of the one before**, from a deck-local `make_figures.py` (`uv run <deck>/make_figures.py`),
and stack them in `::: {.r-stack}` with `.fragment` on all but the first (pair with
`fragment-index` on text in another column). Draw in the theme palette and verify each step
composited on `#0d1117`.

Pattern: `lectures/visibility-space` (resolution, sensitivity, how to make an interferometer).
