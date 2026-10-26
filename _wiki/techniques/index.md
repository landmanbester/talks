---
type: Index
title: Techniques
description: How to do specific things in a deck: video, build-ups, interactive figures, manim clips and explainers.
tags: [index]
timestamp: 2026-10-26
---

# Techniques

- [embedding-video.md](embedding-video.md) — shortcode vs raw `<video>`; muted autoplay needs `<source>` + `{=html}`
- [build-up-figures.md](build-up-figures.md) — annotations one click at a time: transparent PNG frames from `make_figures.py`
- [interactive-figures-ojs.md](interactive-figures-ojs.md) — `{ojs}` sliders and plots; HTTP only; `code-copy: false`
- [manim-slides-stepping.md](manim-slides-stepping.md) — explainer stepped on the clicker: `slides.py`, 10 s hold loops, `manim_slides_qmd.py`, click cue
- [manim-slide-clips.md](manim-slide-clips.md) — transparent webm clip for a slide (two-step render)
- [explainer-videos.md](explainer-videos.md) — `_animations/` series: scaffold, conventions, master clock, preview/final helpers
- [porting-source-decks.md](porting-source-decks.md) — text, page renders and original images out of Google Slides (rclone PPTX/PDF) and Canva (connector PNG export)
