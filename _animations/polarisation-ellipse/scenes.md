# What Can Happen to a Wiggle — delay, twist, shrink, and the polarisation ellipse

Episode of the interferometry explainer series, built for the RIME lecture
(`lectures/rime`), where it plays just before *The Journey of a Wave*. It gives
the audience the four moves that every Jones term is made of, so that the
journey reads as "delay, delay, twist, twist, shrink, ellipse" rather than as
a list of letters.

## Overview
- **Topic**: what a 2×2 Jones matrix can do to a polarised wave, without matrices
- **Hook**: the tip of the electric field traces a shape. Which effects change
  that shape, and which only move it around?
- **Target Audience**: non-technical (same as the rest of the series)
- **Estimated Length**: ~70 s standalone; in the deck each hold loops 3 periods
- **Key Insight**: delaying both wiggles equally, twisting, and shrinking all
  keep a line a line. Only an *uneven* delay between the x and y wiggles opens
  the line into an ellipse (a quarter wave makes a circle). This is why the
  journey only goes elliptical at the receiver: D and G are the only terms
  that treat x and y differently

## Narrative Arc
One panel shows the tip of the field vector; beside and below it, the y and x
wiggles are drawn as scrolling traces, joined to the tip by projection lines
(the classic Lissajous construction). The panel is put through four moves, one
per click, each leaving a faint ghost of the state before it. A summary row of
four mini-panels closes the scene.

## Beats (one per caption)
1. **The wiggle**: "Light wiggles: the tip of its field traces out a shape".
   The panel, a live arrow and a line-shaped trace (linear polarisation at −15°)
2. **x and y**: "Split it into an x wiggle and a y wiggle: in step, a line".
   The x trace (downwards) and y trace (to the right) grow out, with dashed
   projection lines to the tip
3. **Delay**: "Delay both wiggles equally: the same line, just later". Ghost
   of the previous state appears; the common phase φ ramps 0 → 80°. The live
   dot lags the ghost dot on the same line; both traces shift by the same
   amount. Move card: **delay** · K, Z
4. **Twist**: "Twist it: the line turns". θ 0 → 60° (the line ends at 45°,
   so x and y are equal). Move card: **twist** · F, P
5. **Shrink**: "Shrink it: the line gets smaller". Amplitude 1 → 0.7. Move
   card: **shrink** · E
6. **Uneven delay**: "Delay y more than x: the line opens into an ellipse".
   δ (the extra delay of y) 0 → 55°. The y trace slides relative to the x
   trace. Move card: **uneven delay** · D, G, plus the label "the polarisation
   ellipse"
7. **Circle**: "A quarter-wave difference makes a circle". δ → 90°
8. **Summary**: "Only an uneven delay changes the shape". Four mini-panels in
   a row, each showing a ghost of the state before and the state after, with
   its word and letters; the fourth one is green

## Technical Notes
- Master clock (`clock`, `rate`); wave period T = 2 s; HOLD = 3T. The traces
  scroll at a fixed speed and depend only on t − d/speed, so every moving part
  is periodic in T and the deck's hold loops are seamless
- State: v = diag(1, e^{iδ}) · a · e^{iφ} · R(θ) · e0, with e0 = (cos −15°,
  sin −15°). Field e(t) = Re(v e^{−iωt}), so multiplying by e^{+iφ} is a true
  *delay* (live(t) = ghost(t − φ/ω))
- Ghost: a snapshot dict of (φ, θ, a, δ) taken at the start of each move
- `standalone` gates the title and closing cards (the deck wrapper turns them off)

## Consistency checklist
- In beats 1–5 the tip trace is a straight line (δ = 0)
- In beat 3 the ghost and live traces coincide in the panel; the live dot
  trails the ghost dot along the line; both x and y traces shift by the same
  amount
- In beat 4 the line ends at 45°: the x and y traces have equal heights
- In beat 6 the x and y traces peak at different times; the panel shows an
  ellipse
- In beat 7 the ellipse is a circle (|e_x| = |e_y|, δ = 90°)
- Projection lines meet the traces at their "now" ends

## Closing card
"Delay, twist and shrink keep a line a line — only an uneven delay makes an
ellipse." Tease: "next: the journey of a wave".
