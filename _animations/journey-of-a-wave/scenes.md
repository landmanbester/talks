# The Journey of a Wave — every effect on the way is a Jones matrix

Episode of the interferometry explainer series, built for the RIME lecture
(`lectures/rime`). Turns Oleg Smirnov's Jones-calculus slides (plane waves,
Jones chains, the Jones zoo) into one picture with no matrix algebra. Plays
right after *What Can Happen to a Wiggle* (`_animations/polarisation-ellipse`)
and reuses its four moves: delay, twist, shrink, uneven delay.

## Overview
- **Topic**: polarisation and the Jones chain J = G D E P F Z K
- **Hook**: follow one wave from the source to the receiver; why does it only
  go elliptical at the very end?
- **Target Audience**: same as the rest of the series (non-technical)
- **Estimated Length**: ~95 s standalone; in the deck each hold loops 3 wave periods
- **Key Insight**: every effect on the way is one of the four moves, so each is
  a 2×2 Jones matrix, and they chain up in order. Only D and G treat x and y
  differently, which is why the line only opens into an ellipse at the receiver

## Narrative Arc
A source emits a linearly polarised wave. A strip of small wiggles along the
path shows the polarisation everywhere the wave has been (their oscillating
dots also make the travelling wave); one large panel shows the wiggle at the
wavefront, with a faint ghost of the state before each step and a move card
naming it. Stages: space (K), ionosphere (Z, F), dish (P, E), receiver (D, G).
One effect per click: where two share a place, the wavefront passes with the
first, then the second is switched on in place. Letters drop from each zone
into the chain, which grows leftwards. Closing beats: why the ellipse appears
only at the receiver, the chain as a Jones matrix, and "order matters".

## Beats (one per caption)
1. Follow one wave from a source to a receiver: e = (e_x, e_y)
2. Every effect on the way changes the wiggle: space, cloud, dish, receiver
3. Space only delays it (K): **delay**, the ghost ring runs ahead on the same line
4. The ionosphere delays it a little more (Z): **delay**
5. The Earth's magnetic field in the ionosphere twists it (F): **twist**. A
   magnified row of six wiggles above the cloud, from entrance to exit, turns
   progressively as the field switches on: the deeper in, the more twist
6. The dish turns as it tracks the sky: another twist (P), the same way as F
7. The beam sees off-centre sources more weakly (E): **shrink**
8. The feed leaks a little x into y, out of step (D): **leak**, the line starts to open
9. The electronics amplify and delay x and y differently (G): **uneven delay**, an ellipse; output v
10. Only D and G treat x and y differently: that is why the ellipse appears here
11. Each effect is a 2×2 Jones matrix: J = G D E P F Z K, v = J e
12. Order matters: rotate-then-squash is not squash-then-rotate

## Technical Notes
- Master clock; wave period T = 2 s; strip pattern wavelength 2 screen units;
  every moving part depends on (x, t) only through periodic functions of t, so
  the deck's 3T holds loop seamlessly
- `jones_upto(x, f_on, e_on, g_on)`: the chain from the source to x, each
  effect ramped smoothly across its zone; the switches show F, E and G on their
  own beats. The panel shows `jones_upto(front) @ E0`; the ghost is a snapshot
  at the start of each beat. Multiplying by e^{+iφ} is a true delay for the
  field Re(v e^{−iωt})
- Stage values: e0 at −20°; K 70° delay; Z 60° delay; F +50° twist (builds up
  through the cloud); P +20° twist (same way, so nothing cancels: the wave
  ends at 50°); E ×0.7; D leakage 0.3i; G gains 1.15 / 0.85 with y delayed 60°
- `standalone` gates the title and closing cards (the deck wrapper turns them off)

## Consistency checklist
- Before the receiver every wiggle in the strip and the panel is a straight line
- In beat 3 the panel trace does not change; the live dot trails the ghost ring
- In beat 5 the six magnified wiggles turn by increasing amounts left to right;
  the strip glyphs past the cloud all turn by the full 50°
- In beat 6 the line turns further the same way (to 50°), not back
- Strip wiggles past the dish are smaller (E)
- After D the panel shows a thin ellipse; after G a clear one; wiggles past the
  receiver are green ellipses
