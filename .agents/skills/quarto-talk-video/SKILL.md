---
name: quarto-talk-video
description: Turn a Quarto revealjs deck plus recorded voice-over into a conference-compliant MP4. Use this skill whenever the user wants to produce, edit, re-record, assemble, normalize, or validate a pre-recorded talk video from slides — including phrases like "record my talk", "voice over my slides", "make the conference video", "the video is too long", "check my mp4 meets the submission spec", or any mention of a deck plus narration. Also use it for per-slide re-records, silence trimming, loudness normalization, duration/filesize compliance, caption generation, and submission filename construction. Prefer this skill over ad-hoc ffmpeg invocations, since it encodes the compliance checks that ad-hoc commands miss.
---

# Quarto talk → conference MP4

Builds a narrated video from a Quarto revealjs deck using per-slide audio, then validates it
against a conference submission spec. Per-slide audio is the default because it makes re-recording
a single slide cheap — the usual failure mode with one-take screen capture is that a fluff at
minute 11 costs the whole take.

## Non-negotiables

Read the submission spec **into `spec.json` before building anything**, then never deviate from it.
Default spec (URSI GASS 2026 pre-recorded talk):

```json
{
  "max_duration_s": 900,
  "max_size_bytes": 2147483648,
  "container": "mp4",
  "video_codec": "h264",
  "audio_codec": "aac",
  "filename_pattern": "ID{abstract_id}_{session}_{surname}.mp4"
}
```

`max_duration_s` is a **hard reject**, not a guideline. Target 13:30 so that a late re-record of
one slide cannot push the total over. 2 GB over 15 min is ~19 Mbps, which static slides will never
approach — size is a non-issue here, so optimise for legibility, not bitrate.

## Workflow

Work in a scratch dir per talk: `build/<talk-slug>/`. Never write into the deck's source tree.

### 1. Deck → slide images

Ensure the deck's front matter has fragment-aware printing, otherwise fragments collapse onto one
frame and the narration desyncs:

```yaml
format:
  revealjs:
    pdf-separate-fragments: true
```

```bash
quarto render talk.qmd --to revealjs
scripts/extract_slides.sh talk.html build/talk-slug 1920x1080
```

This drives decktape's `--screenshots` mode, which writes PNGs at an exact requested size. Do not
route through PDF and `pdftoppm` unless screenshots fail — the PDF path yields frames a few pixels
off the target, which then need padding before muxing.

Note decktape's version subcommand is `decktape version`, not `--version`.

Then **check the frame count matches the expected slide count** and eyeball 2–3 frames with the
`view` tool. decktape truncating at a broken slide is the single most common failure here, and it
is silent — invisible until the finished video comes out short.

Fallback if `--screenshots` produces nothing, then pad any off-size frame rather than stretching it
(a stretched plot axis is obvious and bad):

```bash
npx -y decktape reveal "file://$PWD/talk.html?print-pdf" build/talk.pdf -s 1920x1080
pdftoppm -png -r 150 build/talk.pdf build/slide
ffmpeg -i slide-07.png -vf "scale=1920:1080:force_original_aspect_ratio=decrease,\
pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=white" slide-07.png
```

### 2. Narration script

Pull speaker notes from the `.qmd` — `::: {.notes}` blocks — into `script/slide-NN.md`, one file
per slide, and show them to the user for editing before any recording happens. Notes written as
prompts-to-self are not readable prose; expect to rewrite them.

Annotate each with a target duration and keep a running total against `max_duration_s`. Reading
pace is ~140 wpm for technical material with equations — slower than conversational speech. Flag
any slide budgeted over 90 s: that is a slide that needs splitting, not a slide that needs faster
talking.

### 3. Record

The user records `audio/slide-NN.wav` themselves (mono, 48 kHz, 24-bit). Do not offer TTS unless
asked — iterating on synthetic prosody costs more than a re-read, and a live audience can tell.

After each batch, trim only the head and tail silence — the dead space around hitting
record/stop. Use `scripts/trim_silence.sh`, which is plain ffmpeg and needs no extra tooling:

```bash
scripts/trim_silence.sh audio/raw audio/trimmed
```

Do **not** reach for a general silence-cutting tool (auto-editor and friends) on this material by
default. They excise mid-take pauses too, and in equation-heavy narration those pauses are load-
bearing — the audience needs them to read the maths. Head/tail trimming is all that's wanted.

### 4. Normalize

Two-pass EBU R128 via `scripts/normalize_audio.sh` — single-pass `loudnorm` uses a dynamic
estimate and will pump between slides recorded in different sessions, which is exactly the
situation here.

```bash
scripts/normalize_audio.sh audio/trimmed audio/normalized
```

### 5. Mux

```bash
scripts/build_video.sh build/talk-slug        # expects slide-*.png + audio/normalized/slide-*.wav
```

Slide count and audio count must match exactly; the script hard-fails otherwise rather than
silently zipping the shorter list. Note the concat demuxer drops the final image unless it is
listed twice — the script handles this, but preserve it in any hand-rolled variant.

### 6. Validate, then name

```bash
scripts/validate_video.sh build/talk-slug/talk.mp4 spec.json
```

Only rename to the submission filename **after** validation passes, so a non-compliant file can
never be confused for a finished one. Sanitize the session name: no spaces, no `/`, ASCII only.

```bash
cp build/talk-slug/talk.mp4 "out/ID1234_SessionJ01_Bester.mp4"
```

Confirm the abstract ID and exact session identifier with the user — do not infer them from the
deck title. A wrong ID is a rejected submission with no chance to fix it after the deadline.

### 7. Captions (do this — it's cheap)

```bash
whisper build/talk-slug/talk.mp4 --model medium --output_format srt --output_dir out/
```

Then skim the SRT for domain terms: Whisper reliably mangles MeerKAT, uv-coverage, Stokes,
deconvolution, and most author surnames. Fix those before shipping. Submit as a sidecar file if
the portal accepts one; do not burn subtitles in unless required.

## If the video is over length

In this order, stopping as soon as it fits:

1. Re-trim with a tighter pad: `scripts/trim_silence.sh audio/raw audio/trimmed 0.10` and re-check.
2. Cut whole slides. Ask the user which are expendable — never choose silently.
3. Re-record the 2–3 longest slides against a tightened script.

Do **not** speed up the video to fit. It is audible, it reads as panic, and it wrecks equation-heavy
slides where the audience needs dwell time.

## Re-recording one slide

The whole point of the per-slide layout. Replace `audio/slide-07.wav`, re-run steps 4–6. Never
rebuild from the deck unless the slide content itself changed.

## Fallback: live screen capture

Use only if the deck depends on live behaviour that a static frame cannot carry — embedded video,
iframes, animated fragments, live code. Record in sections with OBS (1920x1080, 30 fps), trim each,
then concat. Encode every section to identical parameters or `-c copy` concat will fail:

```
1920x1080, 30 fps, yuv420p, libx264, AAC 48 kHz stereo
```

Steps 4, 6, and 7 apply unchanged to captured sections.
