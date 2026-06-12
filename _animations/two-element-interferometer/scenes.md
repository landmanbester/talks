# The Two-Element Interferometer: Why Timing Is Everything

## Overview
- **Topic**: How a two-element radio interferometer works — geometric delay, out-of-phase voltages, and delay compensation ("phasing up") before correlation
- **Hook**: "These two dishes are 100 metres apart. Together they can see detail that would otherwise need a dish 100 metres wide. The trick? Nanosecond timing."
- **Target Audience**: Physics/astronomy students; knows what a sinusoid and a phase offset are; no interferometry background assumed
- **Estimated Length**: ~3 minutes
- **Key Insight**: An off-zenith source reaches the two antennas at *different times*, so their voltage outputs are out of phase — and by deliberately delaying the near antenna's signal by exactly the geometric delay τ = b·sin(θ)/c, the signals snap back into alignment, making two small dishes listen as one

## Narrative Arc
We start with the comfortable case — a source straight overhead lights up both antennas in unison. Tilting the source breaks that symmetry: one antenna hears the wave first, and the voltage traces visibly slide apart. A simple right triangle explains exactly how much, and adding that path length back as an electronic delay restores the lock — the moment the array becomes a single instrument.

---

## Scene 1: Two Dishes, One Wave (The Zenith Case)
**Duration**: ~30 seconds
**Purpose**: Establish the visual machinery (antennas, wavefronts, scrolling voltage traces) in the simplest configuration, where everything is in phase

### Visual Elements
- Dark background; horizontal ground line near the bottom
- Two stylized antennas (simple parabolic-arc dishes or V shapes) labelled $p$ and $q$, separated by baseline $b$ (a labelled double-arrow along the ground between them)
- A star/source glyph at the top of frame, at zenith
- Plane wavefronts: 4–6 parallel lines perpendicular to the propagation direction, marching downward continuously (spacing = wavelength λ)
- Two small oscilloscope panels, one beneath/beside each antenna, with sinusoidal voltage traces scrolling out of them (right-to-left, like a chart recorder)
- Antenna-p trace in **blue**, antenna-q trace in **amber**

### Content
Title card fades ("The Two-Element Interferometer"), then the scene builds: ground, antennas, source at zenith. Wavefronts begin to march down. The first wiggle emerges from each scope at the exact moment the leading wavefront reaches the dishes — the wiggle *visibly emanates from the arrival event*. Because the source is at zenith, both traces start simultaneously and stay identical and locked in phase. Briefly overlay the two traces in a third panel to show perfect agreement. (An earlier draft added a glow pulse on each antenna at every crest crossing; at the chosen wave frequency it read as arbitrary flicker, so it was cut — the trace onset carries the arrival event on its own.)

### Narration Notes
"Here are two radio dishes, separated by a baseline b. A distant source straight overhead sends down plane waves — and because the wavefronts are parallel to the ground, they strike both antennas at the same instant. The voltages coming out of the two receivers are perfectly in step."

### Technical Notes
- **One master clock**: a single `ValueTracker` `t` drives *everything* — wavefront positions AND voltage phases — so arrival events and trace wiggles are physically consistent. This is the core machinery reused by every scene.
- Wavefronts: `always_redraw` group of `Line`s at positions `(n·λ − c_vis·t) mod (N·λ)` along the propagation direction; fade lines as they pass the ground
- Voltage traces: `always_redraw` `FunctionGraph` of `cos(2πν(t − x/v_scroll − τ_arrival))` clipped to the panel, with a `Rectangle` clip or restricted x-range; trace flat (zero) for times before first arrival
- Choose a slow visual frequency: wave period ~1.5 s of screen time so phase relationships are readable
- ~~Antenna pulse on crest crossing~~ — implemented, then removed: strobing at the wave frequency looked like random blinking rather than a readable arrival cue

---

## Scene 2: Tilt the Source (The Sweep)
**Duration**: ~45 seconds
**Purpose**: The core phenomenon — continuously sweep θ off zenith and watch the voltage traces slide out of phase in real time

### Visual Elements
- Same scene as Scene 1, now with an angle indicator: dashed zenith line, arc + label θ between zenith and the source direction
- Source glyph slides along an arc; wavefronts tilt with it (always perpendicular to the line of sight)
- Live readouts in a corner: `θ = 23°` and `Δφ = 2πν·b·sinθ/c` (a phase-offset dial or growing arc between the two traces)
- The overlay panel from Scene 1 stays visible: blue and amber traces visibly drifting apart

### Content
The source begins to slide away from zenith — slowly, continuously, driven by a θ `ValueTracker` from 0° to ~30°. The wavefront family tilts. Now each wavefront strikes antenna $p$ (the one nearer the source) *first*. The traces, locked at zenith, slide apart; the phase-offset readout grows from zero. **Pause the sweep at the angle where the extra path is exactly λ/2**: the overlay panel shows the two sinusoids in perfect anti-phase — blue crest on amber trough. Hold for a beat (this is the dramatic low point: "add these and they cancel completely"). Resume to the final angle (~30°) and freeze.

### Narration Notes
"But real sources aren't at zenith. Watch what happens as the source moves. The tilted wavefront now reaches this antenna first — the other has to wait. And that wait shows up directly in the voltages: the two signals drift out of phase. At this particular angle, they're perfectly opposed — combine them naively and they'd cancel to nothing. Two dishes, hearing the same wave, disagreeing completely."

### Technical Notes
- θ `ValueTracker`; propagation direction $\hat{s} = (\sin θ, -\cos θ)$; everything (`wavefronts`, arrival times, trace phases) derived from θ and the master clock
- Arrival-time offset: $τ_g(θ) = b\sinθ/c_{vis}$ in screen units; antenna q's trace phase is `2πν(t − τ_g)`
- Rate function for the sweep: `rate_functions.ease_in_out_sine`, with a `Wait` inserted at the anti-phase angle — compute that angle from b and λ in advance (`sinθ = λ/(2b)` scaled to screen units; pick b and λ so it lands around 15–20°)
- The phase dial: `always_redraw` `Arc` of angle Δφ between two reference ticks, turning from green (0) through amber to red (π)

---

## Scene 3: The Right Triangle (Where the Delay Comes From)
**Duration**: ~35 seconds
**Purpose**: Derive τ = b·sin(θ)/c geometrically — make the delay quantitative and inevitable

### Visual Elements
- Frozen geometry from the end of Scene 2 (θ ≈ 30°); wavefronts paused or slowed to a crawl; oscilloscope panels dimmed to de-emphasize
- One wavefront highlighted at the moment it touches antenna $p$
- A bright segment from that wavefront down to antenna $q$ along the propagation direction — the **extra path**, drawn in accent green
- Right triangle: baseline $b$ as hypotenuse (ground), extra path $b\sinθ$ as one side, right-angle marker at the foot of the perpendicular, θ marked inside the triangle (with a brief flash of the equal angle at zenith to justify it)
- Equations appearing beside the triangle:
  - $\ell = b\sin θ$
  - $τ_g = \dfrac{b\sin θ}{c}$
  - $Δφ = 2πν\, τ_g$

### Content
Freeze the action. Highlight the wavefront at the instant it kisses antenna $p$: antenna $q$ is still waiting. Draw the perpendicular distance the wavefront must still travel — the extra path ℓ. Construct the right triangle on the baseline, animate the angle-chasing flash showing the angle inside the triangle equals θ, then write ℓ = b sin θ. Convert distance to time (divide by c) and time to phase (multiply by 2πν), transforming each equation into the next (`TransformMatchingTex`). End with the three-line result boxed.

### Narration Notes
"How big is the wait? Freeze the moment the wavefront touches the first antenna. The second antenna sits this extra distance behind — and a little geometry shows that distance is just b sin θ. Divide by the speed of light and you get the geometric delay: a few hundred nanoseconds for a hundred-metre baseline. Tiny — but at radio frequencies, hundreds of full cycles."

### Technical Notes
- `DashedLine` for the perpendicular drop, `RightAngle` mobject for the marker, `Angle` for θ
- `TransformMatchingTex` for the ℓ → τ → Δφ chain; keep colors consistent (b in white, sinθ term in green matching the extra-path segment, c in muted gray)
- Dim the oscilloscope panels with `.set_opacity(0.3)` rather than removing them — they return in Scene 4

---

## Scene 4: Phasing Up (Delay Compensation)
**Duration**: ~45 seconds
**Purpose**: The payoff — insert a compensating delay into the near antenna's signal path and watch the sinusoids slide back into lock

### Visual Elements
- Signal paths drawn from each antenna down to a **correlator block** below the ground line (a box labelled with × and ⟨ · ⟩ — multiply and average; shown but not yet active)
- In antenna $p$'s path: a **delay line** — a coiled/serpentine cable segment that visibly *grows* as delay is added, labelled $τ$
- The overlay panel front and centre: blue and amber traces, currently out of phase
- A live "alignment" indicator: the product or overlap glow between the traces

### Content
Restore full brightness. Route both voltage streams down toward the correlator — but stop at its door: "before we combine them, we must undo the geometry." A delay line appears in the path of antenna $p$ (the one the wave hit *first* — make this point explicitly: we delay the early signal to wait for the late one). The coil grows from zero; as it grows, the blue trace slides continuously to the right in the overlay panel. Crests sweep past troughs, the phase dial unwinds from red back through amber toward green — and at exactly τ = b sin θ/c the traces lock. Snap-flash: the two sinusoids rendered overlapping as one bright white curve. The correlator block lights up green. Boxed text: **phased up**.

### Narration Notes
"Here's the fix — and it's beautifully simple. The first antenna heard the wave early, so we make its signal *wait*: an electronic delay, exactly b sin θ over c. Watch the blue trace slide… and lock. The two antennas, metres apart on the ground, are now listening in perfect unison — as if they were one dish. Only now do we let the correlator combine them."

### Technical Notes
- Delay `ValueTracker` `τ_inst` from 0 → τ_g; antenna p's displayed trace phase becomes `2πν(t − τ_inst)` so the slide is continuous and driven, not a jump-cut
- The coil: `ParametricFunction` serpentine whose number of loops scales with `τ_inst` (or a `Line` path with `always_redraw` zigzag) — keep it cartoonish, it's a metaphor
- Lock moment: when `|τ_inst − τ_g|` crosses zero, `ReplacementTransform` the two traces into a single white curve + `Flash`; use `rate_functions.ease_out_quad` so the approach decelerates into the lock (satisfying snap)
- Correlator block: `RoundedRectangle` + `MathTex(r"\times \;\rightarrow\; \langle \,\cdot\, \rangle")`, border turns from gray to green on lock

---

## Scene 5: Tracking the Sky (Coda)
**Duration**: ~25 seconds
**Purpose**: Generalize — the delay isn't set once; it tracks the source continuously. Tease the next chapter (correlation & fringes)

### Visual Elements
- Full scene with everything live: tilting wavefronts, voltage traces, delay coil, green-locked correlator
- θ sweeps again (e.g. 30° → 10° → 25°, as if the Earth is rotating under the source), but now the delay coil **grows and shrinks automatically in sync**, and the traces *stay locked* throughout — phase dial pinned green
- Closing text card: "Delay tracking — the first thing every interferometer does." then "Next: what the correlator measures — the fringe."

### Content
One continuous shot: the source drifts across the sky and the compensating delay visibly tracks it, the coil breathing in and out while the overlaid traces never separate. This is the inverted replay of Scene 2 — same sweep, but now the system is smart. Fade the apparatus, leave the closing text.

### Narration Notes
"And since the sky rotates, this delay is recomputed continuously — the hardware tracks the source across the sky, keeping the array phased at all times. What the correlator does with these locked signals — and why the answer is a Fourier component of the sky — is the next story."

### Technical Notes
- Trivial once Scene 4's machinery exists: tie `τ_inst` to `τ_g(θ)` with an updater (`τ_inst.add_updater(lambda m: m.set_value(b*sin(θ.get_value())/c_vis))`)
- Reuse Scene 2's sweep code with a different θ schedule

---

## Transitions & Flow
- Scenes 1→2→3→4→5 are one continuous world — no hard cuts; the camera and apparatus persist. Scene boundaries are narrative beats, not visual resets
- Recurring motif: the **master clock** drives wavefront positions and trace phases together, so wave geometry and voltage phase stay visibly consistent in every scene
- The **phase dial** (green→red arc) is the running scoreboard: born in Scene 2, peaks red, unwound in Scene 4, pinned green in Scene 5
- Render as a single Scene class (or a sequence of classes sharing a builder function for the apparatus) — a continuous master clock makes one class simpler

## Color Palette (matched to dark-academic talk theme)
- Background: `#0d1117` (matches the talk theme — clips can later be reused on slides)
- Antenna-p signal: `#58a6ff` (blue)
- Antenna-q signal: `#d29922` (amber)
- Extra path / lock / success: `#3fb950` (green)
- Anti-phase / mismatch warnings, phase-dial hot end: `#f85149` (red)
- Wavefronts: soft white `#c9d1d9` at ~50% opacity
- Annotations/equations: `#c9d1d9`

## Mathematical Content
- $τ_g = \dfrac{b \sin θ}{c}$ — geometric delay (the centerpiece)
- $\ell = b \sin θ$ — extra path length
- $Δφ = 2πν τ_g = \dfrac{2πν\, b \sin θ}{c}$ — phase offset
- $V_p(t) = \cos(2πν t)$, $\quad V_q(t) = \cos\!\big(2πν (t - τ_g)\big)$ — receiver voltages
- Labels: $b$, $θ$, $λ$, correlator $\times \rightarrow \langle\,\cdot\,\rangle$

## Implementation Order
1. **Core machinery first** (used by everything): master clock `ValueTracker`, parameterized wavefront family in direction θ, the two scrolling voltage traces phase-locked to the clock. Get Scene 2's sweep working before anything else — if the wavefront-tilt ↔ trace-phase coupling looks right, the whole video works
2. Scene 1 (zenith special case of the machinery + titles)
3. Scene 3 (static geometry + `TransformMatchingTex` — independent of the hard parts)
4. Scene 4 (delay tracker + coil + lock moment)
5. Scene 5 (one updater + replayed sweep)
6. Polish pass: pacing waits, Flash timing, phase-dial styling

## Physical-Consistency Checklist (the thing that makes or breaks this video)
- [ ] Wavefront spacing on screen = λ, and the trace period = λ/c_vis in clock time — crests hitting an antenna must coincide exactly with crests appearing in its trace
- [ ] At the anti-phase pause in Scene 2, the on-screen extra path is visibly λ/2 (half a wavefront gap)
- [ ] Choose b ≈ 3λ on screen so the sweep to 30° spans ~1.5 cycles of phase — enough to see drift, not so much it strobes
- [ ] Delay slide in Scene 4 moves the blue trace in the *correct* direction (delaying p shifts its trace later in time)
