---
type: Log
title: Wiki change log
description: Chronological record of changes to the wiki and the rules it holds.
tags: [log]
timestamp: 2026-10-25
---

# Change log

Newest first. One line per change: date, page(s), what and why.

- 2026-10-26 — tools/publish, gotchas/index: first CI run hung on Mermaid (runner Chrome sandbox under
  Ubuntu 24.04 AppArmor); workflow installs chrome-headless-shell, lifts the restriction, 20-min timeout.
- 2026-10-26 — tools/publish (new), tools/render, infrastructure/large-data, infrastructure/repo-map,
  conventions/front-matter, techniques/manim-slides-stepping, techniques/manim-slide-clips, AGENTS.md:
  deck `videos/` moved to `/data/talks/` and untracked (history grew a full copy per re-render).
  The site now publishes via GitHub Actions on push to `main`; videos reach the runner through the
  `site-videos` release (`scripts/publish-videos.sh`). `quarto publish gh-pages` retired.
- 2026-10-26 — decks/visibility-space, techniques/manim-slides-stepping: the deck now steps all
  three series explainers; the aperture-synthesis one replaces the static "Filling Visibility
  Space" slide. Its scene gained `standalone = True` (title/closing cards; the wrapper turns them
  off), and `Beats` now treats a scene without a `rate` clock as static (frozen holds).
  gotchas/manim, gotchas/index: a pause before a caption can land after a section-ending fade.
- 2026-10-26 — decks/rime (new), techniques/porting-source-decks (new), techniques/manim-slides-stepping:
  RIME lecture. Google Slides export via `rclone backend copyid` (PPTX + PDF), `scripts/pptx_media.py`
  to map media to slides; Canva page PNGs via `export-design` work. `slides.py` Beats holds without a
  wave clock; `standalone` gates title/closing cards.
- 2026-10-25 — conventions/slide-patterns, gotchas/index: no `$…$` in slide titles (raw TeX shows in
  the menu and reports; idea from epilliat's quarto-presentations skill). Fixed the three titles in
  deconvolution and sgr-a-complex-uhf. Removed the unused manimgl-best-practices skill (the repo
  uses ManimCE only).
- 2026-10-25 — conventions/mermaid: clarified that quotes as label delimiters are fine. Also fixed
  the quarto-revealjs skill where it contradicted the wiki (MathJax 3 macro example, Mermaid
  without `fig-height`, per-deck `mermaid-format`).
- 2026-10-25 — infrastructure/repo-map (new), conventions/front-matter, conventions/mermaid:
  before/after agent test found the annotated directory tree and the theme/title-background file
  names had been dropped in the migration; restored. Mermaid page now links the palette.
- 2026-10-25 — all pages: wiki created from the monolithic `AGENTS.md` (453 lines, ~8k tokens per
  turn), which now only routes and holds the always-on rules. Content moved, not rewritten.
- 2026-10-25 — techniques/manim-slides-stepping, interactive-figures-ojs, build-up-figures,
  tools/check-slides: added with the Visibility Space lecture (merge `d42e14f`).
