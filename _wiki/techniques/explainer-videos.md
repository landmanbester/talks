---
type: Technique
title: Standalone explainer videos (_animations/)
description: The manim explainer series: layout, scaffold, series conventions, master-clock architecture, render helpers.
tags: [manim, animations]
timestamp: 2026-10-25
---

# Standalone explainer videos (`_animations/`)

Plan with the `manim-composer` skill before writing code; implement with `manimce-best-practices`.
Interpreter: see [Python environment](../infrastructure/python-env.md).

One directory per video: a `scenes.md` plan plus a single script with one `Scene` class. Only those
two files are committed. Scaffold a new episode with the series boilerplate (palette, master clock,
caption helper, title/closing cards):

```bash
python _animations/scaffold_video.py <slug> <SceneClassName> "<Title>" --subtitle "..."
```

Series conventions (`two-element-interferometer` → `what-is-a-visibility` → `aperture-synthesis` →
`uvw-and-lmn`): dark-academic palette (bg `#0d1117`, blue `#58a6ff` antenna p, amber `#d29922`
antenna q / sky brightness, green `#3fb950` measurements/results, red `#f85149` mismatch), `Text`
captions at the top edge (font 27), a title card, and a closing card teasing the next episode.

- **Master-clock architecture**: one `ValueTracker` clock advanced by a dt-updater scaled by a
  `rate` tracker; every moving element is an `always_redraw` reading the same trackers, so
  consistency holds by construction instead of choreography
- Prefer computing real data in updaters over staging effects — the aperture-synthesis
  reconstruction is a genuine masked-FFT inverse (`ImageMobject` from a uint8 array)

## Rendering

Render opaque (no `-t`): `-ql` (480p15) for the dev loop, `-qh` (1080p60) for the final. Output
lands in `media/videos/<script-stem>/<quality>/<Scene>.mp4`. Use the helpers rather than
hand-rolled commands:

```bash
_animations/preview.sh <script.py> <Scene>              # -ql render + 10 frames to Read
_animations/preview.sh --no-render <script.py> <Scene> 35 60   # frames at given times
_animations/final.sh <script.py> <Scene>                # -qh, clears partials, checks duration
```

`final.sh` warns if the duration drifts more than 5 s from the dev render; run it in the
background for 3D or long scenes. Check every scene's key beat at `-ql` before the final run. If
rendering by hand, see the render pitfalls in [manim gotchas](../gotchas/manim.md).

To show an explainer inside a deck one beat per click: [manim-slides stepping](manim-slides-stepping.md).
