# Aperture Synthesis

Third installment, after `../two-element-interferometer/` and `../what-is-a-visibility/`.
Picks up at video 2's tease: "next: many baselines — aperture synthesis."

## Overview
- **Topic**: uv-coverage and synthesis imaging — how many baselines become an image
- **Hook**: one baseline asks one question of the sky… how many questions make a picture?
- **Target Audience**: same as videos 1–2
- **Estimated Length**: ~2:20
- **Key Insight**: every antenna pair samples one point of the sky's 2-D Fourier plane;
  N antennas + Earth rotation + bandwidth fill that plane, and an inverse transform of
  the samples *is* the image (the dirty image, blurred by the unsampled holes)
- **Notation**: matches the talk: `V_pq = ∫ I(l,m) e^{-2πi(ul+vm)} dl dm`, `(u,v) = b_pq/λ`,
  and the talk's slogan "more antennas + earth rotation + frequency coverage = fewer holes"

## Narrative Arc
Generalize video 2's 1-D integral to the 2-D sky: a baseline is now a *vector*, one
point (u,v) and its conjugate. Pairs multiply combinatorially; the Earth turning sweeps
each point along an elliptical arc; observing across a band scales arcs radially.
The payoff is a *live reconstruction*: inverse-transform exactly the sampled Fourier
components and watch a patch of sky emerge — stripes (one baseline, video-2 callback) →
crude snapshot (21 baselines) → recognizable image (tracks + bandwidth) — ending honestly
on the dirty image and a deconvolution tease.

This video drops the side-view wave machinery entirely: top-down array panel (left) and
uv-plane panel (right), then sky/reconstruction panels. Same palette; sky/brightness is
amber (like I(l) in video 2), measurements are green.

---

## Scene 1: From a Line to a Plane (~22 s)
Title card ("Aperture Synthesis — many dishes, one giant eye"). Recap equation from
video 2, then `TransformMatchingTex` into the 2-D version with `(u,v) = b_pq/λ`:
the sky is two-dimensional, so spatial frequencies live in a **plane**.

## Scene 2: Every Pair Is a Baseline (~28 s)
Two panels fade in: the array seen from above (left), the uv-plane (right). Two
antennas → one baseline vector → one green point and its mirror image. Add antennas
one at a time to 7: chords multiply, uv points pop in pairs; a live counter shows
N antennas → N(N−1)/2 baselines. Caption: "seven dishes already ask 21 questions at once."

## Scene 3: Try to Make a Picture (~30 s)
Reveal a small patch of sky (amber: a point source, a close double, a diffuse blob) in
the left panel, then shrink it to an inset — "what can the samples reconstruct?"
A reconstruction panel takes its place, computed as a *real masked-FFT inverse* of the
truth image:
- **one baseline** (others dimmed in the uv panel): the reconstruction is pure stripes —
  the corrugation from video 2, now in 2-D
- **all 21 baselines, one instant**: a crude, ringing snapshot

## Scene 4: Let the Earth Do the Work (~30 s)
Hour-angle tracker sweeps ~5 h: every uv point traces an elliptical arc (tracks drawn
live), and the reconstruction sharpens in lockstep. Then bandwidth: arcs fan out
radially ((u,v) ∝ ν), filling more of the plane, image improves again.
Caption echoes the talk: "more antennas + earth rotation + frequency = fewer holes."

## Scene 5: The Dirty Image (~25 s)
Hold the final side-by-side: inset truth vs reconstruction. Caption: the holes never
sampled blur and ripple every source — this is the **dirty image**, the sky convolved
with the dirty beam. Closing card: "Aperture synthesis — many dishes, hours, and
bandwidth: one giant virtual aperture." Tease: "next: from dirty images to the sky —
deconvolution."

---

## Technical Notes
- **Real imaging, not staged**: truth sky is a 128×128 numpy array; `F0 = fftshift(fft2(sky))`
  computed once; the uv mask is gridded from the *same* tracker-driven baseline/hour-angle/
  bandwidth state that draws the uv panel; reconstruction = `ifft2(ifftshift(F0·mask)).real`,
  clipped ≥ 0, normalized, colorized, shown via an `always_redraw` ImageMobject. The uv
  panel and the image can never disagree.
- Ellipse tracks: u = s(bₓcos H − b_y sin H), v = s·sinδ(bₓsin H + b_y cos H), δ = 45°-ish
  (sinδ = 0.7); bandwidth = three radial scalings s ∈ {1−0.08f, 1, 1+0.08f} with f: 0→1.
- 7 fixed antenna positions (dense-ish core + outliers, MeerKAT-flavoured).
- Amber two-stop colormap (bg → amber → warm white) for truth and reconstruction.
- Mixing ImageMobjects with VMobjects: use `Group`, not `VGroup`.

## Color Palette (same series)
`#0d1117` bg · blue `#58a6ff` antennas · amber `#d29922` sky/brightness ·
green `#3fb950` uv samples/tracks · `#c9d1d9` text · `#8b949e` muted.

## Consistency checklist
- Single-baseline reconstruction = stripes perpendicular-ish to that baseline (video-2 callback)
- uv points always come in conjugate pairs; tracks are ellipses centred on the origin
- Image sharpens monotonically as coverage grows; never sharper than the truth
- Counter matches visible chords: N(N−1)/2
