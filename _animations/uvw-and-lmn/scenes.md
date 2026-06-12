# Where uvw and lmn Live

Fourth installment, between `../aperture-synthesis/` and a future deconvolution video.
Goal: a fairly non-technical audience leaves knowing what the letters in
`V_pq = ∬ I(l,m) e^{-2πi(ul+vm+w(n-1))} dl dm / n` actually *are*, before deconvolution.

## Overview
- **Topic**: the uvw and lmn coordinate systems
- **Hook**: they are the two ends of the same line of sight
- **Key Insight**:
  - **(u,v,w)** = the array, as the source sees it: baselines projected flat onto the
    source's sky (u,v) plus the hidden component along the sight-line (w)
  - **(l,m,n)** = the sky, as the array sees it: stars dropped onto a flat map around
    the pointing centre (l,m) plus the dome's sag along the sight-line (n)
- **Estimated Length**: ~2:20
- **Style**: first `ThreeDScene` of the series; one 3D set (ground + antennas + dome +
  line of sight), camera does the teaching. Exactly one equation in the whole video.

## Narrative Arc
Everything is measured relative to one arrow: the phase centre s₀ (the direction the
delays of video 1 are tuned to). Ride up that arrow and look back down — the baselines
collapse into their projections: that picture is (u,v), and the part you can't see is w;
the Earth turning sweeps the projection along an ellipse (video 3's tracks, explained).
Come back down and look up — stars live on a dome, but a computer wants a flat map:
each star drops perpendicularly onto the tangent screen, its address is (l,m), and the
dome sags away from the screen by 1−n. The two screens pair up letter by letter in the
phase; for a small patch n ≈ 1 and the w-term dies, leaving the flat-sky Fourier world
of videos 2–3.

---

## Scene 1: One Special Direction (~20 s)
Title card ("Where uvw and lmn Live — the two viewpoints of an interferometer").
Build the 3D set at an oblique camera angle: ground grid, four antennas (pair p/q
highlighted in series colors), faint celestial dome, yellow star at the phase centre,
arrow s₀ from the array to it. Caption: every coordinate is measured relative to this
arrow.

## Scene 2: The Source's-Eye View — uvw (~45 s)
A green-tinted screen ⊥ s₀ appears high up ("the source's sky — really light-years
away"). The p–q baseline projects along s₀ onto it (dashed rays, projected dots, green
projected baseline). Decompose b on the ground: a leg along s₀ (w) + the perpendicular
rest (u,v). **Camera flies up the line of sight and looks back down**: antennas land
exactly on their projections — all the source can see is (u,v); w hides along the
sight-line. Earth turns (rotate array about vertical): the projected endpoints trace
ellipses on the screen — video 3's uv tracks. Camera returns; screen fades.

## Scene 3: The Array's-Eye View — lmn (~45 s)
Look up instead: stars on the dome (three near the phase centre, one far out). An
amber-tinted screen tangent to the dome at s₀, with l and m arrows. Each star drops a
plumb line parallel to s₀ onto the screen: its map address (l,m). The far star's plumb
line is long — the dome *sags* away from the flat screen, and n records it (n = 1 at
centre, smaller further out). Fixed-frame inset: the flat map peeled off into 2D, then
the video-3 truth-sky thumbnail — "the I(l,m) we imaged last time lives exactly here."

## Scene 4: The Letters Pair Up (~25 s)
World fades; the talk's equation appears with two-tone coloring: green measurement
letters (V_pq, u, v, w), amber sky letters (I(l,m), l, m, n). Caption: u pairs with l,
v with m, w with n−1 — one frame, two viewpoints. Then the small-patch move:
`\underbrace{w(n-1)}_{≈0}` mutes the w-term → a clean 2-D Fourier transform.

## Scene 5: Closing (~15 s)
Card: "uvw — the array, as the source sees it." / "lmn — the sky, as the array sees it."
Tease: "next: deconvolution — undoing the dirty beam."

---

## Technical Notes
- Frame: ŵ = s₀ = (sin 25°, 0, cos 25°); û = ẑ×ŵ normalized = (0,1,0); v̂ = ŵ×û.
  Direction cosines are exact: ŝ = lû + mv̂ + nŵ with n = √(1−l²−m²); star at R·ŝ,
  map point at R(lû + mv̂ + ŵ), so the plumb line is parallel to s₀ with length R(1−n).
- uvw screen ⊥ ŵ at distance 4.6 (beyond the dome, R = 3.4) — deliberately a
  *different* screen from the lmn tangent screen (they are Fourier duals, not the same
  plane); green vs amber tint and separate scenes keep them distinct.
- Projection for uvw: a ↦ a + (d − a·ŵ)ŵ; rotation via a ValueTracker and
  `always_redraw` so rays/projections/traces stay consistent; `TracedPath` ellipses.
- Look-down-the-LOS camera: phi = 25°, theta calibrated empirically so antennas land
  on their projections (verified by screenshot).
- Captions/equations are fixed-in-frame; 3D labels use fixed-orientation mobjects.
- Sky thumbnail reuses video 3's `make_sky`/`colorize` (copied, scripts stay standalone).

## Color Palette (series)
green `#3fb950` = measurement side (uvw, screens, projected baselines) ·
amber `#d29922` = sky side (lmn, stars' map, I(l,m)) · blue `#58a6ff` antenna p ·
amber antenna q · `#c9d1d9` text · `#8b949e` muted · bg `#0d1117`.

## Consistency checklist
- In the look-down shot, each antenna sits exactly on its projected dot
- Ellipse traces match video 3's track shapes (rotation about the vertical, tilt 25°)
- Far star: longer plumb line than near stars; n readout smaller
- p is nearer the source along ŵ than q (continuity with video 1: p hears first)
