---
type: Deck
title: Visibility Space (lecture)
description: East Africa TART training lecture; reference implementation for manim-slides stepping, OJS and build-up figures.
tags: [decks, lecture]
timestamp: 2026-10-26
---

# Visibility Space: spatial filtering and the two-element interferometer

`lectures/visibility-space/` — East Africa TART Training. Audience is largely non-technical:
light on math. TART itself was introduced in an earlier session, so this lecture has no TART
material.

- **Source**: built from `lectures/aperture-synthesis-imaging` material plus the build-up in Canva
  `DAHMUzASEpo` pages 8–22 (photo `images/gbt-current.png` supplied by the user)
- **Reference implementation** for: [manim-slides stepping](../techniques/manim-slides-stepping.md)
  (`slides.py`, `_two-element.qmd`, `_visibility.qmd`, `_aperture-synthesis.qmd`, `segment-cue.html`),
  [interactive figures](../techniques/interactive-figures-ojs.md) (fringe explorer),
  [build-up figures](../techniques/build-up-figures.md) (`make_figures.py`: dish, Rayleigh, interferometer)
- **Steps all three series explainers**: two-element-interferometer and what-is-a-visibility
  (wave clock, seamless 10 s hold loops) and aperture-synthesis (static, frozen holds). The
  aperture-synthesis wrapper skips scene 1 (title card + 1-D to 2-D equation recap, too much math
  for this audience; the "One Pair, One Point" slide says it in words) and, via `standalone = False`,
  the closing card, so the clip ends on the dirty image and "What the Holes Cost Us" follows it
- `images/uv-snapshot.png`, `uv-tracks.png`, `uv-freq.png` are no longer used (the animation
  replaced the "Filling Visibility Space" slide)
