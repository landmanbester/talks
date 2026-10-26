---
type: Infrastructure
title: Repository map
description: Annotated directory tree of the talks repo — what lives where.
tags: [structure, layout]
timestamp: 2026-10-25
---

# Repository map

```
talks/
├── AGENTS.md                # Agent entry point (CLAUDE.md / GEMINI.md symlink here)
├── _quarto.yml              # Website project: renders */*/index.qmd into _site/
├── index.qmd                # Listing page: one table per class
├── pyproject.toml, uv.lock  # Python env for the repo's tooling (`uv sync`)
├── templates/
│   ├── dark-academic.scss   # Shared dark theme (canonical copy)
│   ├── lectures.scss        # Lecture layer on top of the shared theme
│   ├── contributions.scss   # Contribution layer
│   └── title-slide.html     # Title-slide partial: event line + logo strip
├── assets/logos/            # Shared logos + meerkat-milkyway.jpg title background
├── lectures/ , contributions/
│   ├── AGENTS.md            # Class rules (CLAUDE.md / GEMINI.md symlink here)
│   ├── _metadata.yml        # Front matter shared by every deck in the class
│   └── <talk-slug>/
│       ├── index.qmd        # The presentation (always index.qmd)
│       ├── images/          # Figures for this talk
│       ├── videos → /data/… # Embedded clips + manim-slides segments (gitignored; published via release)
│       ├── custom.css       # Optional deck-local CSS — declare it (conventions/front-matter.md)
│       ├── make_figures.py  # Optional: generates images/ (build-up overlays, plots)
│       └── slides.py        # Optional: manim-slides wrappers for _animations/ scenes
├── scripts/
│   ├── check_slides.py      # Measure every slide for overflow (verification harness)
│   ├── manim_slides_qmd.py  # manim-slides render → one Quarto slide per segment
│   ├── shoot-decks.sh       # Render + screenshot every deck's title slide
│   ├── sync-data.sh         # /data/talks/ ⇄ Google Drive (see Large data)
│   ├── publish-videos.sh    # Deck videos → `site-videos` release for the publish workflow
│   ├── backup-takes.sh      # Mirror raw narration takes to the other disk
│   └── figures/             # FITS → slide-ready PNGs from a YAML spec (own README)
├── figures/scratch/         # Generated figures not currently on a slide
├── fits_files → /data/…     # FITS feeding scripts/figures/ (gitignored)
├── reference_pdfs/          # Canva PDF exports to port from (gitignored)
├── _animations/<video>/     # Standalone manim explainer: scenes.md + one script
├── _video/<talk-slug>/      # Talk-video build: spec.json + script/ tracked, rest gitignored
├── _wiki/                   # Agent knowledge base (this wiki)
├── .github/workflows/publish.yml  # Push to main → render → GitHub Pages
├── docs/superpowers/        # Design specs and plans for past repo-wide changes
└── .agents/skills/          # Agent skills (.claude/skills symlinks here)
```

The leading underscore on `_animations/` and `_video/` keeps Quarto's site render out of them.
For the same reason **never prefix a talk directory with `_`** — the deck silently will not render.
