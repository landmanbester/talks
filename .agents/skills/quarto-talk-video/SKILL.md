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

Work in a build dir per talk at the repo root — `_video/<slug>/`, mirroring `_animations/`. Never
write into the deck's source tree. The leading underscore keeps Quarto's site render out of it.
All paths below are relative to the repo root; `<slug>` matches the deck's directory name.

```
_video/<slug>/
├── spec.json          # submission spec — tracked
├── script/narration.md # narration, one block per frame — tracked
├── frames.json        # frame → slide/fragment map — tracked
├── slide-NN.png       # extracted frames — gitignored
│                      #   (top level, not a subdir: build_video.sh globs slide-*.png here)
├── talk.mp4           # muxed output   — gitignored
├── audio/{raw,trimmed,normalized}/  # WAVs — gitignored
└── out/               # submission-named mp4 + captions — gitignored
```

Tracking the spec and the narration keeps the video regenerable from source, exactly like
`_animations/` keeps `scenes.md` plus the script and throws away `media/`.

### 1. Deck → slide images

```bash
quarto render                     # renders the whole site into _site/
.agents/skills/quarto-talk-video/scripts/extract_slides.py \
    _site/<class>/<slug>/index.html _video/<slug> 1920x1080
```

One frame per **fragment step**, matching the live talk: arriving at a slide is one frame and each
fragment reveal is another. Add `--per-slide` for one fully-revealed frame per slide instead —
far less recording, at the cost of the progressive reveal. A slide whose entire body is fragmented
has its nothing-revealed frame skipped, since that renders as a heading over a blank slide; pass
`--keep-empty-intro` to keep those.

The script also writes `frames.json`, mapping every frame to its slide heading and fragment
step. That is the running order for the narration.

**Do not use decktape.** It cannot do per-fragment frames here anyway, and it is broken in this
environment twice over: puppeteer's `page.pdf()` dies with `Attempted to use detached Frame`
against current Chrome, and on Ubuntu 24.04+ its bundled Chromium cannot even start, because
`apparmor_restrict_unprivileged_userns=1` blocks the sandbox (`credentials.cc … Permission
denied`). Both are fixed by not involving puppeteer: the script drives the system Chrome with
`--no-sandbox`.

Two failure modes the script now checks for you, because both are silent:

- **Byte-identical consecutive frames** — a state that never rendered. The script hashes every
  frame and hard-fails. Causes seen: sharing one Chrome `--user-data-dir` across invocations (the
  second Chrome hits the singleton lock and shoots stale page state), and reveal's ~200 ms
  fragment fade landing mid-transition when the screenshot fires, which renders a slide blank but
  for its heading. The probe disables all transitions to remove the second.
- **Off-size frames** — every PNG is ffprobed against the requested size.

Still **eyeball 2–3 frames** and confirm the count is what you expect.

### 2. Narration script

Write `_video/<slug>/script/narration.md` — **one file**, one block per frame, in `frames.json`
order. One file rather than one per frame because it is edited in a single pass and read in
order; the frame number in each heading is what maps it to `audio/raw/slide-NN.wav`.

```markdown
## slide-07 — CLEAN: cheap iterations (11s)

Its iterations are cheap, because the minor cycle never touches the data.
```

Seed from the deck's `::: {.notes}` blocks if it has any — many decks have none, in which case
write from the slide content. Either way expect to rewrite: notes written as prompts-to-self are
not speakable prose. **Show the draft to the user and get it edited before any recording happens.**

Then check it, rather than adding up budgets by eye:

```bash
.agents/skills/quarto-talk-video/scripts/check_script.py \
    _video/<slug>/script/narration.md _video/<slug>/spec.json \
    --frames _video/<slug>/frames.json
```

It reports spoken time at 140 wpm (right for equation-heavy material — slower than
conversational), flags blocks whose text does not match their own budget, verifies every frame has
a block, and exits 1 if the total breaks `max_duration_s`.

Aim to come in **under** target: the estimate counts words only, and 60+ inter-frame pauses add up.
Any block budgeted over 90 s is a slide that needs splitting, not faster talking.

### 3. Record

The user records `_video/<slug>/audio/raw/slide-NN.wav` themselves, one per frame (mono, 48 kHz,
24-bit). Do not offer TTS unless asked — iterating on synthetic prosody costs more than a re-read,
and a live audience can tell.

Drive it with the recorder rather than hand-rolled ffmpeg calls, which is where takes get saved
under the wrong number and silently desync every later frame:

```bash
.agents/skills/quarto-talk-video/scripts/record_narration.py _video/<slug> --level  # check mic
.agents/skills/quarto-talk-video/scripts/record_narration.py _video/<slug>          # resume
.agents/skills/quarto-talk-video/scripts/record_narration.py _video/<slug> --status
.agents/skills/quarto-talk-video/scripts/record_narration.py _video/<slug> --only 7 # redo one
```

It shows each block, records to a temp file so a bad take never destroys a good one, reports
duration against budget and peak dBFS after every take, and resumes at the first unrecorded frame.
Prefers `pw-record` when PipeWire is running, else `arecord`.

What actually matters across a multi-session recording:

- **Never clip.** Aim for peaks around −6 to −12 dBFS. Two-pass loudnorm at step 4 fixes level
  differences between sessions; nothing fixes a clipped take.
- **Keep mic distance and room constant** between sessions. Loudness is normalized, timbre and
  room tone are not — a slide recorded at a different distance stands out mid-talk.
- Leave a beat of silence at each end and don't clip your own first word; step 3's trim removes it.

**Declick before trimming** if the takes were started and stopped with a keypress. The key is
*inside* the take — a 10–30 ms transient at the very end of nearly every file, occasionally at the
start. Silence trimming will not remove it: a click is loud, so it is the trim's stopping point
rather than something the trim removes, and normalization then lifts it toward full scale. Measured
on a real 66-take recording, the click reached **−3 dBFS** in the finished mux, louder than the
narration.

```bash
.agents/skills/quarto-talk-video/scripts/declick_takes.py \
    _video/<slug>/audio/raw _video/<slug>/audio/declicked --dry-run   # report first
.agents/skills/quarto-talk-video/scripts/declick_takes.py \
    _video/<slug>/audio/raw _video/<slug>/audio/declicked
```

It cuts the last run above each file's own noise floor only when it is short (≤120 ms), isolated
(≥80 ms of silence before it) and touching the file edge, and it refuses the cut if what it would
remove contains anything sustained. Level alone cannot be the test — click and speech peaks overlap
almost exactly; duration and isolation are what separate them. Removing the click also lets the
trim finally reach the trailing silence behind it, which is worth ~20 s over a 66-slide talk.

Feed the declicked directory to the trim, and pass the matching audio dir on to the build:

```bash
.agents/skills/quarto-talk-video/scripts/build_video.sh _video/<slug> \
    _video/<slug>/talk-declicked.mp4 audio/declicked-normalized
```

After each batch, trim only the head and tail silence — the dead space around hitting
record/stop. Use `trim_silence.sh`, which is plain ffmpeg and needs no extra tooling:

```bash
.agents/skills/quarto-talk-video/scripts/trim_silence.sh _video/<slug>/audio/raw _video/<slug>/audio/trimmed
```

Do **not** reach for a general silence-cutting tool (auto-editor and friends) on this material by
default. They excise mid-take pauses too, and in equation-heavy narration those pauses are load-
bearing — the audience needs them to read the maths. Head/tail trimming is all that's wanted.

### 4. Normalize

Two-pass EBU R128 via `normalize_audio.sh` — single-pass `loudnorm` uses a dynamic
estimate and will pump between slides recorded in different sessions, which is exactly the
situation here.

```bash
.agents/skills/quarto-talk-video/scripts/normalize_audio.sh _video/<slug>/audio/trimmed _video/<slug>/audio/normalized
```

### 5. Mux

```bash
.agents/skills/quarto-talk-video/scripts/build_video.sh _video/<slug>        # expects slide-*.png + audio/normalized/slide-*.wav
```

Slide count and audio count must match exactly; the script hard-fails otherwise rather than
silently zipping the shorter list. Note the concat demuxer drops the final image unless it is
listed twice — the script handles this, but preserve it in any hand-rolled variant.

### 6. Validate, then name

```bash
.agents/skills/quarto-talk-video/scripts/validate_video.sh _video/<slug>/talk.mp4 _video/<slug>/spec.json
```

Only rename to the submission filename **after** validation passes, so a non-compliant file can
never be confused for a finished one. Sanitize the session name: no spaces, no `/`, ASCII only.

```bash
cp _video/<slug>/talk.mp4 "_video/<slug>/out/ID1234_SessionJ01_Bester.mp4"
```

Confirm the abstract ID and exact session identifier with the user — do not infer them from the
deck title. A wrong ID is a rejected submission with no chance to fix it after the deadline.

### 7. Captions (do this — it's cheap)

Build them from the narration script, not from the audio:

```bash
.agents/skills/quarto-talk-video/scripts/captions_from_script.py _video/<slug>
```

The script *is* the transcript when the talk was read per-slide, so this needs no ASR and no
install, and it cannot mangle a domain term. Cue times come from each slide's audio duration, so
every cue is exact at its slide boundary; within a slide the split is proportional to text length,
which bounds drift by one slide and resets it at the next. Output is `out/talk.srt`.

Use whisper instead only if the delivery departed substantially from the script:

```bash
whisper _video/<slug>/talk.mp4 --model medium --output_format srt --output_dir _video/<slug>/out/
```

Then skim the SRT for domain terms: Whisper reliably mangles MeerKAT, uv-coverage, Stokes,
deconvolution, and most author surnames. Fix those before shipping.

Either way, submit as a sidecar file if the portal accepts one; do not burn subtitles in unless
required. To eyeball alignment, burn one frame — and pass `-copyts`, or `-ss` rebases the
timestamps to zero and the filter renders no caption at all, which looks like a broken SRT:

```bash
ffmpeg -ss 380 -copyts -i _video/<slug>/talk.mp4 \
  -vf "subtitles=_video/<slug>/out/talk.srt" -frames:v 1 /tmp/caption_check.png
```

## If the video is over length

In this order, stopping as soon as it fits:

1. Re-trim with a tighter pad: `.agents/skills/quarto-talk-video/scripts/trim_silence.sh _video/<slug>/audio/raw _video/<slug>/audio/trimmed 0.10` and re-check.
2. Cut whole slides. Ask the user which are expendable — never choose silently.
3. Re-record the 2–3 longest slides against a tightened script.

Do **not** speed up the video to fit. It is audible, it reads as panic, and it wrecks equation-heavy
slides where the audience needs dwell time.

## Re-recording one slide

The whole point of the per-slide layout. Replace `_video/<slug>/audio/raw/slide-07.wav`, re-run steps 4–6. Never
rebuild from the deck unless the slide content itself changed.

## Fallback: live screen capture

Use only if the deck depends on live behaviour that a static frame cannot carry — embedded video,
iframes, animated fragments, live code. Record in sections with OBS (1920x1080, 30 fps), trim each,
then concat. Encode every section to identical parameters or `-c copy` concat will fail:

```
1920x1080, 30 fps, yuv420p, libx264, AAC 48 kHz stereo
```

Steps 4, 6, and 7 apply unchanged to captured sections.
