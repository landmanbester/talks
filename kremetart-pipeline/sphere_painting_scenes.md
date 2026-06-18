# Painting the whole sphere — slide clip plan

A short, transparent webm embedded on the **"Painting the whole sphere"** slide of
the KREMETART talk. One continuous `ThreeDScene`, no title/closing cards (the slide
already carries the heading and bullets). Composites onto the slide's dark
`#0d1117` background.

## Overview
- **Topic**: how a global network of zenith-pointing TART stations paints the whole
  celestial sphere *in real time* — each station's instantaneous, primary-beam-tapered
  footprint sweeps across the fixed equatorial sky as the Earth turns, and coverage
  accumulates.
- **Hook**: one station's footprint sweeps out only a *band* — so how does the network
  cover the whole sphere?
- **Audience**: collaborators / supervisors (the talk's group-update audience). No
  narration; the slide bullets carry the words. Captions in the clip are minimal.
- **Estimated length**: ~15 s (target window 12–18 s).
- **Key insight**: this is a **streaming** instrument. The sky is fixed (the equatorial
  grid of the previous slide); the stations' footprints *move*. The primary beam is the
  soft, bright-at-zenith / zero-at-horizon weight of each live footprint. Sweep over a
  sidereal day → each station paints a band; several stations → the whole sphere.

## Narrative arc
A dark, **fixed** celestial sphere appears. A southern station's footprint — a big soft
spotlight, bright at its zenith and fading to its horizon — switches on and **sweeps**
around the sky at the sidereal rate, leaving a glowing painted trail behind it. After
one turn it has painted a band but the far-north cap is still dark. Northern and mid
stations switch on and their footprints sweep too; the dark cap fills, overlaps brighten
and colour-blend. The clip ends with all footprints live and sweeping over a fully
painted sphere — the steady-state streaming network.

## The schematic physics (qualitatively correct)
- A zenith-pointing station at geographic latitude $\varphi$ has its zenith at
  **declination $\delta=\varphi$**, and its zenith **right ascension = local sidereal
  time**, which advances $360°$ per sidereal day. So the footprint **sweeps around the
  $\delta=\varphi$ circle** at a constant rate; different longitudes only set the
  starting RA (a phase offset).
- The **instantaneous footprint** is the visible hemisphere: a cap of angular radius
  $90°$ centred on the moving zenith, with the **primary beam** as a soft taper — full
  at the centre (zenith), fading to ~0 at the rim ($90°$, the horizon). Weight model:
  `w = max(0, cos(θ_zenith))^p`, `p≈1.5`, where `θ_zenith` is the angle from the
  current zenith.
- **Accumulated coverage** at a sky point = the best (max) footprint weight it has
  received so far. A point is painted to `w(|δ−φ|)` once the sweep's closest approach
  in RA has passed it; the polar cap with `|δ−φ| > 90°` is **never** reached by that
  station.
- Three illustrative stations (labels illustrative of a *future* network, not literal
  site claims), staggered in start-RA so their spotlights are visually separated:
  - **Southern** `≈ −45°` — **blue** `#58a6ff` (nod to TART's NZ origin). Alone, leaves
    `δ > +45°` dark.
  - **Northern** `≈ +45°` — **green** `#3fb950`. Fills the northern cap; overlaps the
    south in the mid-declinations.
  - **Mid** `≈ 0°` — **amber** `#d29922`. Thickens the overlap; "network" richness.

## Visual elements
- **Celestial sphere (FIXED)**: unit `Sphere`/`Surface`, very low-opacity dark fill,
  plus a faint graticule (a few declination circles + meridians, thin
  `#30363d`/`#8b949e`, equator subtly emphasised). It does **not** rotate — it is the
  fixed sky. Depth/parallax comes from a slow **camera** orbit only.
- **Live footprint (per active station)**: the bright soft spotlight — the dot
  cloud (below) re-coloured at full opacity within the current cap, brightest at the
  moving zenith. Optionally a small bright zenith marker + short label (`46°S`, `0°`,
  `46°N`) in the station colour, riding the zenith.
- **Accumulated paint**: a cloud of small `Dot3D`s sampled on a longitude×latitude grid
  (≈ 48 × 28). Per station, each dot stores its accumulated weight; the dot's drawn
  colour/opacity is the blend of station contributions (live cap brightest, trail
  dimmer but persistent). Overlap regions show layered colours → brighter, mixed.
- **Captions** (optional, minimal): top-edge `Text`, font 27, `#e6edf3`, ≤ 2 short
  phrases ("one station sweeps a band", "the network fills the sphere"); easy to drop to
  zero to avoid clashing with the slide's bullets.

## Beats (one continuous scene, driven by the master clock)
1. **Establish (~0–2 s)** — fade in the dark fixed sphere + graticule. Camera at
   `phi≈68°` so the north polar cap (top) is in view; begin a slow continuous camera
   orbit (theta) that runs the whole clip.
2. **One station streaming (~2–7 s)** — southern (blue) footprint switches on at the
   front and **sweeps** ~one full turn around `δ=−45°`, painting a glowing trail. The
   north cap (`δ>+45°`, top of the sphere) stays **dark** — the visible gap. *Caption
   (opt.): "One TART sweeps out a band as the sky streams past."*
3. **Network switches on (~7–12 s)** — northern (green) then mid (amber) footprints
   switch on (staggered start RAs) and sweep too. The dark north cap fills; the
   mid-declination overlaps brighten and colour-blend. *Caption (opt.): "More stations —
   the gaps fill in."*
4. **Steady-state (~12–15 s)** — all three footprints live and sweeping over the fully
   painted sphere; camera completes its orbit to show seamless, soft-edged coverage from
   all sides. Markers may fade so the painted sphere + moving spotlights are the final
   image. *Caption (opt.): "Together: the whole sphere, in real time."*

(Stagger is for narrative; if a cleaner loop is wanted, start all three together and let
the sweep complete an integer number of turns.)

## Consistency checklist (the rendered frames MUST show)
- [ ] The celestial sphere itself is **fixed** (graticule does not rotate); only the
      **camera** orbits and the **footprints** sweep.
- [ ] Each footprint sweeps in **RA at a constant rate** around its own declination
      circle (constant `δ`, advancing RA).
- [ ] The **live** footprint is clearly **brighter** than the painted **trail** behind it.
- [ ] After beat 2, a **visibly dark** north polar cap (`δ>+45°`) remains, and it is
      **in view** (camera `phi` shows the top).
- [ ] After beat 3, **no dark gap remains** — the whole sphere is covered.
- [ ] Footprint edges are **soft** (opacity gradient to zero at the rim), never hard —
      the "primary beam, not a hard horizon cut" point.
- [ ] Overlap regions are **brighter / colour-mixed** than single-station regions.

## Colour palette
- Background: transparent (composites on slide `#0d1117`).
- Southern: `#58a6ff` (blue). Northern: `#3fb950` (green). Mid: `#d29922` (amber).
- Graticule: `#30363d` lines, equator `#8b949e`. Captions/labels: `#e6edf3`.

## Technical notes (ManimCE, `ThreeDScene`)
- **Master clock**: one `ValueTracker` `clock` advanced by a `dt`-updater (scaled by a
  `rate` tracker); `clock` represents sidereal phase (turns). Every moving element reads
  it: each station's zenith RA `= RA0_s + 360°·clock`, and the accumulated paint is a
  function of `clock`. This is the `_animations/` master-clock pattern — consistency by
  construction (footprint position vs painted trail can't drift apart).
- **Accumulated paint**: maintain a persistent `paint[n_stations, n_points]` numpy array;
  in the dot-cloud `always_redraw`, compute each active station's instantaneous weight
  for the current zenith and `paint = np.maximum(paint, w_instant)`, then map to dot
  colours/opacities (live cap = max(w_instant) bright, trail = stored paint). Mirrors the
  genuine-data-in-updater approach of the aperture-synthesis episode. (Frame-order
  dependent, which is fine for a forward render; an analytic `reach-phase` form is the
  resumable alternative if needed.)
- `always_redraw` mobjects only render after an explicit `self.add(...)` — add the cloud.
- Use `Group` (not `VGroup`) if the cloud is ever mixed with an `ImageMobject`.
- **Camera orbits, sphere does not**: drive the camera with
  `begin_ambient_camera_rotation(rate=…)` (or a clock-linked theta); never rotate the
  sphere mobject. Keep `phi≈68°` so the north cap stays visible for the gap beat.
- Fixed captions/labels: `add_fixed_in_frame_mobjects(c)` then `remove`, then animate
  `FadeIn` (the `uvw-and-lmn` recipe). Zenith labels that should face the camera go
  through `add_fixed_orientation_mobjects`.
- Depth sorting can dim a translucent sphere's far side over the dots — brighten the dots
  and re-`add` the sphere fill if it washes out; use `.set_stroke(opacity=…)` for the
  graticule lines.
- Keep the dot grid modest (≈ 48×28) for render time; `Dot3D` radius small.
- Render transparent then convert (repo workflow): `manim -t -qm sphere_painting.py
  SpherePainting` → `.mov`, then `ffmpeg … -c:v libvpx-vp9 -pix_fmt yuva420p
  -auto-alt-ref 0 -b:v 2M videos/sphere-painting.webm`.
- Verify with `_animations/preview.sh sphere_painting.py SpherePainting` (frame sheet) at
  `-ql`, iterate against the consistency checklist, then a final `-qh` render before the
  webm convert. 3D + dot clouds can be slow — background the final render.

## Integration into the slide
Replace the fan-in Mermaid diagram on the "Painting the whole sphere" slide with
`{{< video videos/sphere-painting.webm >}}` (autoplay, muted, loop), keeping the three
bullets and the status note. Fall back to keeping the Mermaid diagram if the clip isn't
ready by talk time.

## Files
- `sphere_painting.py` — standalone script, one `SpherePainting(ThreeDScene)`.
- `videos/sphere-painting.webm` — committed final render (embedded).
- `media/` — manim intermediates (gitignored).
