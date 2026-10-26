# Calibrator Transfer — solving for the gains, and what it costs

Episode of the interferometry explainer series, built for the RIME lecture
(`lectures/rime`). Animates Oleg Smirnov's "Calibration & Calibrators" timeline
slide, with his error terms (σ_sol, σ_var, σ_xfer) as three knobs instead of formulas.

## Overview
- **Topic**: 1GC / reference calibration — solve on a calibrator, interpolate onto the target
- **Hook**: the gain drifts; we only get to look at it now and then
- **Target Audience**: same as the rest of the series (non-technical)
- **Estimated Length**: ~45 s
- **Key Insight**: what the interpolated solutions miss is the calibration error;
  it grows with a fainter calibrator, less frequent visits, and a calibrator
  further from the target

## Beats (one per caption)
1. The gain drifts with time — the true gain-phase curve (blue)
2. Calibrator scans (green bands) between target scans (amber)
3. Solutions on each calibrator scan (green dots with error bars)
4. Transfer: join the dots
5. The error: red fill between truth and interpolation, rms readout
6. Fainter calibrator — solution noise 4° → 15°
7. Less often — visits every 1.5 h → 4 h
8. Further away — the calibrator's own gain curve (ghost) departs from the target's
9. Bright, nearby, often — everything restored

## Technical Notes
- No wave clock: static between beats, so deck holds are plain freezes
- Fixed noise draw per visit, so the knobs change the picture smoothly
- The readout's digit count changes: add it, never animate it in
