---
type: Technique
title: Stepping an animation on the clicker (manim-slides)
description: Play an _animations/ explainer inside a deck one beat per click: slides.py wrapper, seamless hold loops, generated slides, click cue.
tags: [manim, manim-slides, video]
timestamp: 2026-10-26
---

# Stepping an animation on the clicker (manim-slides)

An `_animations/` explainer can play inside a deck one beat per click, without forking its script.
[manim-slides](https://manim-slides.eyllanesc.io) splits a render into segments at each
`self.next_slide()`; `scripts/manim_slides_qmd.py` turns the segments into one Quarto slide each.
Reference: `lectures/visibility-space` (all three series videos). Prefer this to embedding one long
clip for any explainer the presenter talks over.

1. **Wrap, don't fork.** A deck-local `slides.py` puts `_animations/<video>/` on `sys.path`,
   imports the scene and subclasses it with `Slide`. A mixin overrides the scene's `caption()` to
   call `next_slide()` first — every caption is a narrative beat, so the pauses fall where the
   narration does. Copy `lectures/visibility-space/slides.py`. The wave scenes have `caption()`,
   `rate` and `t_now()`; a scene with no `rate` (aperture-synthesis, the `lectures/rime` scenes)
   is static, so every pause is a frozen hold. Check what `caption()` does: in some scenes it only
   *builds* the Text and the scene plays it later, so the pause lands just before that play.
   Title/closing cards that don't fit a deck: gate them on a `standalone = True` class attribute
   in the scene and set it `False` in the wrapper (the standalone video is unchanged); skip a
   whole unwanted opening beat by overriding that method with `pass` in the wrapper. In a
   print-to-PDF of the deck every segment slide is black (background videos at frame 0) — that
   is not an empty segment.
2. **Holds loop seamlessly.** While the wave machinery is running (`rate > 0`), a pause is a loop of
   exactly **7 wave periods** (λ/c = 1/0.7 s, so 10 s = 300 frames at 30 fps) — wavefronts and
   traces cycle without a jump. A frozen scene (`rate == 0`) just holds its last frame. Before the
   leading wavefront has reached every antenna nothing is periodic yet, so a beat that falls there
   is skipped (`steady` on the subclass).
3. **Render** from the deck directory, with `media` and `slides` symlinked into
   `/data/talks/<class>/<slug>/` first ([large data](../infrastructure/large-data.md)):
   ```bash
   ~/software/manim/.venv/bin/manim-slides render -qm slides.py SceneSlides
   python3 ../../scripts/manim_slides_qmd.py SceneSlides <name>
   ```
   `-qm` (720p30) is plenty for a slide and keeps a video near 10 MB. `videos/` must already be a
   symlink into `/data/talks/` (segments are not tracked); afterwards run
   `scripts/publish-videos.sh` so the site build has them ([publish](../tools/publish.md)).
   The script copies them to `videos/<name>/NN.mp4` and writes `_<name>.qmd`; pull it into
   `index.qmd` with `{{< include _<name>.qmd >}}`. Never edit `_<name>.qmd` — re-run the script.
4. **What the generated slides do**: headless `.plain-figure` slides with the segment as
   `background-video` (`contain`, muted), `transition="none"` and `background-transition="none"`
   so the cuts are invisible. A play-once segment holds its last frame until the click; a loop
   repeats until the click; a segment followed by a loop gets `data-autoslide` (its duration) so
   it runs straight into the hold.
5. **Click cue.** Copy `segment-cue.html` and its CSS block from `lectures/visibility-space`, and
   add `include-after-body: segment-cue.html` to the deck's front matter: a small green dot pulses
   in the top-right corner whenever a segment is waiting for the click (during a loop, or once a
   play-once segment ends), and never on autoslide segments. Deck-local by choice; moving it into
   `templates/` is a shared-theme change — ask first.
6. **Verify**: `check_slides.py`, then click through in a browser — confirm each autoslide segment
   lands in its loop and the cue comes on only while waiting.
