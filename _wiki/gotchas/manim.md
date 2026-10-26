---
type: Gotcha
title: Manim gotchas (hit in this repo)
description: ManimCE API traps and manual-render pitfalls: killed renders, piped exit codes, duration drift, ThreeDScene.
tags: [manim, gotcha]
timestamp: 2026-10-26
---

# Manim gotchas (hit in this repo)

## Rendering by hand

- Piping manim (e.g. `| tail`) masks its exit code — run it bare
- A killed render leaves a truncated segment in `partial_movie_files/` that poisons later runs
  (short mp4 or `InvalidDataError`; `--flush_cache` does NOT fix it) — delete that quality's
  `partial_movie_files/` before a final render (`_animations/final.sh` clears partials itself)
- Always ffprobe the final duration: 15 vs 60 fps renders drift ~1s; a broken stitch loses tens

## Stepping with manim-slides

- Pausing "before each caption" holds on a captionless frame when a section ends by fading its
  caption out on its own (`self.play(FadeOut(cap))`) before the next section starts. Move that
  pause to just before the fade: `ApertureSynthesisSlides` in `lectures/visibility-space/slides.py`
  overrides `play()` to beat before an all-`FadeOut` play that removes the current caption, then
  skips the next caption's pause. Check the last frame of every segment (ffmpeg `-sseof -0.1`)

- A step video stops on its last frame and needs a click to continue (just before the green cue
  dot appears), on some slides only. reveal.js's `autoSlideStoppable` defaults to true: any key
  or click while an autoslide timer runs pauses autoslide **for the rest of the deck**, and the
  only resumes are the A key or the playback control (hidden in these decks). So one click during
  any step segment strands every later step-into-loop hand-off. Fix: `auto-slide-stoppable: false`
  under `format: revealjs:` in every deck with stepped segments. Testing with `Reveal.slide()`
  from a script never shows it — reproduce with real key presses

## ManimCE API

- `always_redraw` mobjects only render after an explicit `self.add(...)` — invisible, no error
- Rate functions are namespaced: `rate_func=rate_functions.ease_in_out_sine`
- `.set_opacity()` on a plotted curve also sets fill, visually closing the path — use
  `.set_stroke(opacity=...)` on line-like mobjects
- Mixing `ImageMobject` with vector mobjects needs `Group`, not `VGroup`
- Swap a caption out *before* animating to a state it doesn't describe — a lingering caption over a
  sweep reads as wrong physics
- `ThreeDScene` (see `_animations/uvw-and-lmn/`):
  - Fixed captions: `self.add_fixed_in_frame_mobjects(c)`, `self.remove(c)`, then `FadeIn(c)`;
    camera-facing 3D labels go through `add_fixed_orientation_mobjects` the same way
  - "Look along an axis" shots suffer perspective parallax — pass a large `focal_distance` (e.g. 60)
    to `move_camera` for that shot, restore after
  - Depth sorting draws a translucent `Surface`'s fill over floor-level VMobjects — brighten the
    floor mobject and re-`add` it
  - `theta` is the camera's azimuth: to look down `(sin φ, 0, cos φ)` use `phi=φ, theta=0` — and
    verify the alignment with a screenshot rather than trusting the convention
