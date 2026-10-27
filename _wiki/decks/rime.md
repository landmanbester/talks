---
type: Deck
title: The RIME (lecture)
description: East Africa TART training lecture on the measurement equation and calibration; adapted from Oleg Smirnov's decks; four manim explainers.
tags: [decks, lecture]
timestamp: 2026-10-27
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
  → fixed vs steerable: three slides contrasting ground-fixed arrays (TART) with tracking dishes
  (MeerKAT): what each sees, which RIME terms change (E, P, ionosphere, pointing), and how each
  gets its calibrators
- **Animations** (`slides.py` wraps them all; see [stepping](../techniques/manim-slides-stepping.md)):
  `rime-interferometer` (three scenes: `RimeOnTheInterferometer`, `OneNumberToABox` — scalar G
  grows into the 2×2 J — and `RimeForTart`), `polarisation-ellipse` (`WhatCanHappenToAWiggle`:
  the four moves — delay, twist, shrink, uneven delay — and the polarisation ellipse; wave clock),
  `journey-of-a-wave` (reuses those moves stage by stage; one effect per click; wave clock),
  `calibrator-transfer` (static holds). Wave-clock scenes hold on 6 s loops
- **Notation**: the intro's scalar G is "everything on the way"; "G Is a Whole Journey" and the
  `OneNumberToABox` clip rename it J, after which G means only the electronics (as in the
  Jones chain J = G D E P F Z K). Keep that order if the arc changes, or G means two things
- **Why the ellipse appears only at the receiver**: only D and G treat x and y differently;
  K/Z delay both equally, F/P rotate, E scales. The primer sets this up, the journey pays it off
- **Figures**: `make_figures.py` — KGB build-up panels, and a simulated before/after-calibration
  image (64-antenna MeerKAT-like array, antenna phase offsets + random-walk drift)
- **Cut on purpose**: Stokes formulas, brightness-matrix derivation, Mueller calculus, all-sky
  integrals and W-term, fringe stopping, Oleg's σ formulas (they became the transfer animation's knobs)
- **Overlap**: `lectures/aperture-synthesis-imaging` has a Calibration section (RIME, calibration vs
  imaging, calibrators) — when it is adapted for this training, cut it to a back-reference
