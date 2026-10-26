# The Journey of a Wave — every effect on the way is a Jones matrix

Episode of the interferometry explainer series, built for the RIME lecture
(`lectures/rime`). Turns Oleg Smirnov's Jones-calculus slides (plane waves,
Jones chains, the Jones zoo) into one picture with no matrix algebra.

## Overview
- **Topic**: polarisation and the Jones chain J = G D E P F Z K
- **Hook**: watch the wiggle of one wave change at every stage of its journey
- **Target Audience**: same as the rest of the series (non-technical)
- **Estimated Length**: ~60 s standalone; in the deck each hold loops 3 wave periods
- **Key Insight**: every effect between source and receiver changes the
  polarisation in a linear way — a 2×2 Jones matrix — and the effects chain up,
  in order

## Narrative Arc
A source emits a linearly polarised wave (panel: the field vector oscillating).
Its path crosses space (K, a delay), the ionosphere (Z delay, F Faraday rotation),
the dish (P parallactic rotation, E beam attenuation) and the receiver (D leakage,
G gains). A panel after each zone shows the real polarisation state computed from
the actual matrices: rotated, lagging, shrunk, then elliptical. Letters drop from
each zone into the chain, which grows leftwards. Closing beat: order matters.

## Beats (one per caption)
1. Light wiggles in a direction — source panel, e = (e_x, e_y)
2. Every effect on the way changes the wiggle — path, cloud, dish, receiver
3. Space only delays it (K)
4. Ionosphere: Z and F — panel 2 (rotated, lagging)
5. Dish: P and E — panel 3 (rotated back, smaller)
6. Receiver: D and G — panel 4 (an ellipse), output v
7. "Each effect is a 2×2 Jones matrix" — J = G D E P F Z K, v = J e
8. Order matters — rotate-then-squash vs squash-then-rotate

## Technical Notes
- Master clock; wave period T = 2 s; the ribbon's phase speed is λ/T so every
  moving part is periodic in T. Deck holds loop 3T = 6 s
- Panel states are STATES[i] = (product of the stage matrices so far) · E0

## Consistency checklist
- Panel 2 is panel 1 rotated by F (40°) and lagging by Z
- Panel 4 is elliptical (G has a phase difference between x and y; D is imaginary)
