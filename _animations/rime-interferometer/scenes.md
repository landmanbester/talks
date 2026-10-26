# The Measurement Equation — what each term means

Episode of the interferometry explainer series. Built for the RIME lecture
(`lectures/rime`), where it opens the lecture and, as `RimeForTart`, closes it.
Adapted from the Canva build in "Old Aperture synthesis, visibilities and
imaging" (`DAF75-Z8qDM`, slides 71–80).

## Overview
- **Topic**: the scalar RIME, term by term, on the two-element interferometer
- **Hook**: every symbol in the equation is a part of the picture you already know
- **Target Audience**: same as the rest of the series (non-technical)
- **Estimated Length**: ~45 s (+ ~30 s for the TART scene)
- **Key Insight**: V = G B G* K — the sky, wrapped in what each antenna does to it;
  calibration finds the G's, imaging finds the B's

## Narrative Arc
Draw the interferometer, write the equation, then fly each term onto the part it
describes. A real sky has many sources, so add them up. End on the inverse
problem. The TART scene returns to the same picture: satellites at known
positions (B known), known geometry (K known), single-polarisation antennas (each
G one complex number) — 24 unknowns against 276 visibilities.

---

## RimeOnTheInterferometer (one beat per caption)
1. "A two-element interferometer" — star, rays, dishes, amplifiers, delay line,
   correlator (× and ⟨⟩), output arrow
2. "One equation says what comes out" — V_pq = G_p B G_q* K_pq on the right
3. V → correlator output (green)
4. B → star (amber)
5. G_p, G_q* → amplifiers (blue)
6. K → delay line (white: known geometry)
7. "A real sky has many sources — add them all up" — more stars; equation
   becomes Σ_s G_p B_s G_q* K_pq,s
8. "Calibration finds the G's. Imaging finds the B's." — boxes + labels

## RimeForTart
1. "Back to our picture" — full labelled diagram and summed equation
2. Stars → GPS satellites; ✓ under B_s
3. ✓ under K
4. Gain dials beside each amplifier: one complex number (length = how much
   louder, angle = how much later), animated
5. "24 antennas ⇒ 276 visibilities ⇒ only 24 unknown gains"

## Color Palette (series)
`#0d1117` bg · blue `#58a6ff` instrument/gains · amber `#d29922` sky ·
green `#3fb950` measurement / known · `#c9d1d9` text · `#8b949e` muted.

## Consistency checklist
- G_q carries the conjugate (the Canva original drops it)
- TART: 24 antennas, 24·23/2 = 276 baselines
