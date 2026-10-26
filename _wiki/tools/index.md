---
type: Index
title: Tools
description: Scripts and commands: render/preview/screenshot, publish, check_slides, talk videos, manim_slides_qmd, figures.
tags: [index]
timestamp: 2026-10-25
---

# Tools

- [render.md](render.md) — `quarto preview`/`render`, PDF export, headless screenshot of a slide, `#/H/V` anchors
- [publish.md](publish.md) — GitHub Actions publish on push to `main`; deck videos via `scripts/publish-videos.sh` and the `site-videos` release; Pages limits
- [check-slides.md](check-slides.md) — `scripts/check_slides.py`: CLIPPED vs tight, probe behaviour, 0px slides, fix-by-cause table
- [talk-videos.md](talk-videos.md) — deck + narration → MP4 (`quarto-talk-video` skill)
- `scripts/manim_slides_qmd.py` — documented in [manim-slides stepping](../techniques/manim-slides-stepping.md)
- `scripts/figures/` — FITS → slide-ready PNGs from a YAML spec; has its own README
- `scripts/sync-data.sh`, `scripts/backup-takes.sh` — see [large data](../infrastructure/large-data.md)
