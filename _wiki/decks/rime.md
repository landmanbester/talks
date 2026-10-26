---
type: Deck
title: The RIME (lecture)
description: East Africa TART training lecture on the measurement equation and calibration; adapted from Oleg Smirnov's decks; three new manim explainers.
tags: [decks, lecture]
timestamp: 2026-10-26
---

# The RIME: the radio interferometer measurement equation, and calibration

`lectures/rime/` — East Africa TART Training, the lecture after
[Visibility Space](visibility-space.md). One hour; non-technical audience: pictures, not proofs.
Given on behalf of Oleg Smirnov, who may reuse anything made for it — so the animations are
standalone explainers in `_animations/` as well as stepped segments.

- **Sources**:
  - Oleg Smirnov's Google Slides: "Interferometry — TART Madagascar" (2026, the base) and
    "Imaging/RIME/Calibration — TART BIUST" (2025: direction-dependent effects, VLA beam). Copies
    on the user's Drive; exports in `/data/talks/reference/smirnov/{madagascar-2026,biust-2025}/`
  - Canva `DAF75-Z8qDM` ("Old Aperture synthesis, visibilities and imaging") pages 71–80: the RIME
    terms placed on the two-element interferometer — rebuilt as `_animations/rime-interferometer`.
    Page PNGs in `/data/talks/reference/canva-DAF75-Z8qDM/`
- **Arc**: why an equation → the scalar RIME on the interferometer (animation) → what is inside G:
  the Jones chain (animation) → J_p B J_q^H, the onion, KGB, direction-dependent effects →
  calibration: KGB panels, calibrators, transfer (animation), selfcal → "let's break it down":
  the same picture for TART (one complex number per antenna; GPS satellites as known sky)
- **Animations** (`slides.py` wraps all three; see [stepping](../techniques/manim-slides-stepping.md)):
  `rime-interferometer` (two scenes: `RimeOnTheInterferometer`, `RimeForTart`),
  `journey-of-a-wave` (wave clock; 6 s hold loops), `calibrator-transfer` (static holds)
- **Figures**: `make_figures.py` — KGB build-up panels, and a simulated before/after-calibration
  image (64-antenna MeerKAT-like array, antenna phase offsets + random-walk drift)
- **Cut on purpose**: Stokes formulas, brightness-matrix derivation, Mueller calculus, all-sky
  integrals and W-term, fringe stopping, Oleg's σ formulas (they became the transfer animation's knobs)
- **Overlap**: `lectures/aperture-synthesis-imaging` has a Calibration section (RIME, calibration vs
  imaging, calibrators) — when it is adapted for this training, cut it to a back-reference
