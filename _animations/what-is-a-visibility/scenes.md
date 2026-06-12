# What Is a Visibility?

Sequel to `../two-element-interferometer/` — picks up at that video's tease:
"next: what the correlator measures — the fringe."

## Overview
- **Topic**: the complex visibility — what a correlator output actually is
- **Hook**: we phased the two signals up… now what number comes out, and what does it mean?
- **Target Audience**: same as video 1 (students meeting radio interferometry)
- **Estimated Length**: ~2:15
- **Key Insight**: one baseline measures **one Fourier component of the sky** — the
  fringe amplitude is `|V|` (contrast), the fringe offset is `arg V`
- **Notation**: matches the aperture-synthesis talk: `V_pq = ∫ I(l) e^{-2πi (b/λ) l} dl`

## Narrative Arc
Multiply-and-average turns two voltage streams into a single number. Hold the delay
fixed at the phase centre and let the sky drift: that number oscillates — the fringe.
Flip perspective: the interferometer sees the sky through a sinusoidal stripe pattern.
A source wider than the stripes covers crests and troughs at once, so the fringe washes
out — fringe contrast *is* the visibility amplitude, and that is exactly a Fourier
component of the brightness.

Continuity with video 1: same apparatus, palette, master-clock machinery; the
anti-phase angle (b·sinθ = λ/2, the "8° moment") reappears as the fringe's negative peak.
Phase centre is **zenith** (τ = 0), so no delay coil is needed.

---

## Scene 1: Multiply and Average (~30 s incl. title)
Title card ("What Is a Visibility? — what a correlator actually measures").
Quick recap build: ground, dishes p/q, baseline arrow, source at zenith, wavefronts,
one scope panel with both traces in step. New: a `×` node feeds a green **product
trace** (cos², all positive bumps), then `⟨·⟩` collapses it to a number ≈ 1.00.
That number becomes the first point on an output-vs-direction plot (axes fade in,
dot at l = 0, r = 1).

**Technical**: same `voltage()` / master-clock; product trace is an `always_redraw`
over the same scrolled times; the plot dot rides `axes.c2p(sinθ, r(sinθ))` with a
`TracedPath`.

## Scene 2: The Fringe (~25 s)
Caption: "hold the delay fixed — and let the sky drift." θ sweeps 0 → 18°; the traces
slide apart and the traced dot draws a cosine: r = cos(2π·(b/λ)·sinθ). Pause at the
first null (θ ≈ 4.0°, quarter fringe) and at the anti-phase peak (θ ≈ 8.0° — explicit
callback to video 1), then continue. Label the curve **"the fringe"**.

## Scene 3: Fringes on the Sky (~18 s)
Flip perspective: fade in a stripe pattern painted on the sky arc — radial ticks whose
opacity follows (1 + cos(2π(b/λ) sinθ))/2. The drifting star moves through bright and
dark zones exactly in step with the plot dot. Caption: "the interferometer sees the sky
through this pattern — spacing λ/b."

## Scene 4: Extended Sources Wash Out (~30 s)
Scope + product panels fade (single-trace story breaks for incoherent sources); the
traced curve is replaced by a live `always_redraw` theoretical fringe
A(σ)·cos(2π u l). The point source grows into a Gaussian blob (width tracker σ):
it now covers a crest *and* a trough at once → the live curve flattens,
A = exp(−2(πuσ)²). `|V|` readout drops from 1.00 toward 0. Then **b grows** 3.6 → 9
(antennas slide apart, stripes tighten, curve compresses *and* flattens further):
"a longer baseline resolves out the same source." Caption: **fringe contrast = |V|,
the visibility amplitude**; the fringe offset would be its phase.

## Scene 5: One Fourier Component (~25 s)
Apparatus fades. Mini-diagram: brightness I(l) (gold blob) × cosine stripes (muted)
→ green shaded product. Equation (talk notation):
`V_pq = ∫ I(l) e^{−2πi (b/λ) l} dl`
Bullets: |V_pq| — fringe contrast; arg V_pq — fringe offset.
Closing card: **"A visibility is one Fourier component of the sky."**
Tease: "next: many baselines — aperture synthesis."

---

## Color Palette (same as video 1)
`#0d1117` bg · blue `#58a6ff` p / signal · amber `#d29922` q · green `#3fb950`
product / stripes / result · red `#f85149` mismatch · `#c9d1d9` fronts/text.

## Implementation Order
1. Port machinery from `interferometer.py` (clock, fronts, traces) with **dynamic
   antenna positions** driven by a baseline `ValueTracker`.
2. Scene 2's drift + traced fringe (the core coupling) before anything else.
3. Stripes (scene 3), σ/b washout (scene 4), then the static scene 5 diagram.

## Consistency checklist
- Fringe nulls/peaks line up: plot dot peak ↔ star centred on a bright stripe
- Anti-phase peak at the same b·sinθ = λ/2 angle as video 1 (θ ≈ 8.0° at b = 3.6λ)
- When b doubles, stripe spacing halves and the live curve gains the same factor in cycles
- Removed glow pulses (video 1 lesson): no per-crest blinking anywhere
