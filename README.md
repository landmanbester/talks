# Talks

Quarto revealjs presentations for technical talks at SARAO / Rhodes/ AIMS South Africa.
One directory per talk, a shared dark theme, and a root-level Quarto **website
project** that builds everything into a single browsable site.

Agent conventions (porting workflow, theme classes, Mermaid/Manim rules) live in
[AGENTS.md](AGENTS.md) — `CLAUDE.md` and `GEMINI.md` are symlinks to it.

## Layout

Talks come in two classes, and the class a deck lives in decides its
formatting and the agent rules that apply to it:

- **`lectures/`** — teaching material, revised and re-given. Undated
  (`date: today`), institutional logos only.
- **`contributions/`** — conference and workshop talks, each given once.
  Carries the event date, and event logos alongside the institutional ones.

Each talk is `<class>/<talk-slug>/index.qmd` with its `images/` beside it. The
full directory map, and where large data lives (`/data/talks/`, symlinked in),
is in [AGENTS.md](AGENTS.md) and the agent wiki under [`_wiki/`](_wiki/index.md).

Python tooling (the FITS figure pipeline) runs from a uv environment:
`uv sync`, then `uv run scripts/figures/make_figures.py --list`.

The large data has a copy on Google Drive, synced by hand (rclone remote
`talks-drive:`, set up once with `rclone config create talks-drive drive
scope=drive root_folder_id=<folder-id>`):

```bash
scripts/sync-data.sh status             # what differs
scripts/sync-data.sh push -n            # dry run; drop -n to upload changes
scripts/sync-data.sh pull               # on a fresh clone: fetch + symlink
```

**Push after every recording session** — the raw takes are the one thing in
this repo that cannot be regenerated. `scripts/backup-takes.sh` adds a second
local copy on the other disk.

## How the website project works

The root `_quarto.yml` makes this directory a Quarto project. Any `quarto`
command run anywhere inside it operates in project context:

- **All output goes to `_site/`** — including single-talk renders, which land in
  `_site/<class>/<talk-name>/`. Nothing renders in-place next to the `.qmd`.
- The root `index.qmd` is a **listing page** with one table per class: dated
  contributions sorted most-recent-first, then undated lectures sorted by
  title. Add a new talk directory under either class → it appears on the next
  render. No manual index editing.
- **Shared front matter is hoisted.** Theme, revealjs options, title
  background, and logos come from the class `_metadata.yml`, so a deck's own
  front matter carries only what is specific to it.
- Referenced resources (images, webm animations) are copied into `_site/`
  automatically.

## Everyday commands

```bash
# Edit loop: live preview of one talk (auto-reloads on save)
cd lectures/<talk-name>          # or contributions/<talk-name>
quarto preview index.qmd
# → serves at http://localhost:PORT/lectures/<talk-name>/  (note the prefix!)

# Build everything: listing page + all talks
quarto render            # from the repo root → _site/

# View the built site locally
quarto preview           # from the repo root
# or just open _site/index.html in a browser
```

To create a new talk, use the `quarto-revealjs` skill in your AI assistant, or
run the scaffold script directly with the required class argument:

```bash
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py lecture "Interferometry Basics"
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py contribution "KAT-7 Transient Search"
```

## Rendering to PDF

Three options, in order of preference (full details in
`.agents/skills/quarto-revealjs/references/pdf-export.md`):

**1. decktape — best fidelity to the HTML slides**

```bash
quarto render lectures/<talk-name>/index.qmd
npx decktape reveal --size 1600x900 _site/lectures/<talk-name>/index.html slides.pdf
```

**2. Browser print-to-PDF — no tooling needed**

Open the talk with `?print-pdf` appended, e.g.
`http://localhost:PORT/lectures/<talk-name>/?print-pdf`, then Ctrl+P → Save as PDF
(enable background graphics).

By default all fragments appear expanded on one page. For one page per
fragment step, add to the talk's YAML:

```yaml
format:
  revealjs:
    pdf-separate-fragments: true
```

**3. Self-contained HTML — often better than PDF for sharing**

Animations, videos, and progressive reveal survive; a PDF kills them. Add
`embed-resources: true` under `format: revealjs:` and the rendered
`index.html` becomes a single file you can email.

## Narrated talk videos

Turning a deck into a pre-recorded conference submission: render the slides to
PNG frames, record one audio take per frame, mux. Everything lives in
`_video/<talk-slug>/`, mirroring the deck's own directory name.

Audio is recorded **per frame**, not as one continuous take. That is the whole
design: fluffing a line at minute eleven then costs one re-read rather than the
entire recording, and swapping a figure later costs no re-recording at all.

```
_video/<talk-slug>/
├── spec.json            # submission spec — tracked
├── script/narration.md  # one block per frame — tracked
├── frames.json          # frame → slide + fragment map — tracked
├── slide-01.png …       # extracted frames        — gitignored
├── audio/{raw,declicked,declicked-trimmed,declicked-normalized}/
├── talk.mp4             # muxed output            — gitignored
└── out/                 # submission-named mp4 + captions
```

Only the three small files are tracked, so the video is regenerable from source
while the multi-gigabyte artefacts stay out of git.

Full reference, including the failure modes each script guards against:
[`.agents/skills/quarto-talk-video/SKILL.md`](.agents/skills/quarto-talk-video/SKILL.md).

Every command below runs from the repo root. Set these two once per shell:

```bash
SKILL=.agents/skills/quarto-talk-video/scripts
D=_video/<talk-slug>            # e.g. _video/sgr-a-complex-uhf
```

### 1. Deck → PNG frames

Render the site first — the extractor reads the built HTML, not the `.qmd`:

```bash
quarto render                                  # → _site/
$SKILL/extract_slides.py \
    _site/contributions/<talk-slug>/index.html $D 1920x1080
```

You get **one frame per fragment step**, matching the live talk: arriving at a
slide is one frame and each reveal is another, so a slide with three fragments
yields four frames. Pass `--per-slide` for one fully-revealed frame per slide
instead — far less recording, at the cost of the progressive reveal.

It also writes `frames.json`, which maps every frame to its slide heading and
fragment step. That file is the running order for the narration.

Two things worth knowing:

- **Decks with full-bleed background images need a longer timeout.** The
  default is not enough to load several 1920×1080 PNGs, and Chrome gives up
  with `error: chrome timed out`. Add `--timeout 120000`.
- **Check the frame count against the deck** before going further. The script
  hard-fails on byte-identical consecutive frames and off-size PNGs, but it
  cannot tell you that you meant to have one fewer slide.

### 2. Narration, before any recording

`record_narration.py` reads `script/narration.md` and shows you one block at a
time, so the script has to exist and has to line up with the frames. One block
per frame, in `frames.json` order:

```markdown
## slide-07 — CLEAN: cheap iterations (11s)

Its iterations are cheap, because the minor cycle never touches the data.
```

Check it rather than counting by eye:

```bash
$SKILL/check_script.py $D/script/narration.md $D/spec.json --frames $D/frames.json
```

It reports spoken time at 140 wpm, flags blocks whose text overruns their own
budget, and — the one that matters — verifies **every frame has a block**. A
missing block means every take after it lands on the wrong picture.

On duration: the 140 wpm estimate covers the words only. Inter-frame gaps add
roughly **0.7 s per frame** on top, measured on a finished talk here (66 frames,
estimated 12:06.9, delivered 12:52.8). Budget the real number:

```
real ≈ spoken@140wpm + 0.7 s × frames
```

### 3. Record

```bash
$SKILL/record_narration.py $D --level     # check the mic first
$SKILL/record_narration.py $D             # record / resume at the first gap
$SKILL/record_narration.py $D --status    # what is done
```

Takes are written to `audio/raw/slide-NN.wav` under the frame number they
belong to, recorded via a temp file so a bad take never destroys a good one.
The recorder resumes at the first unrecorded frame, so it is safe to stop and
come back — use `--from N` to restart somewhere specific.

Across a multi-session recording, two things actually matter:

- **Never clip.** Aim for peaks around −6 to −12 dBFS. Loudness differences
  between sessions are fixed in step 4; a clipped take is not fixable.
- **Keep mic distance and room constant.** Loudness gets normalized, timbre and
  room tone do not, and one slide recorded closer to the mic stands out.

Leave a beat of silence at each end and don't clip your own first word — the
trim in step 4 removes it.

### 4. Clean up the takes

Three passes, each writing a new directory so the originals survive:

```bash
$SKILL/declick_takes.py   $D/audio/raw       $D/audio/declicked --dry-run   # report first
$SKILL/declick_takes.py   $D/audio/raw       $D/audio/declicked
$SKILL/trim_silence.sh    $D/audio/declicked $D/audio/declicked-trimmed
$SKILL/normalize_audio.sh $D/audio/declicked-trimmed $D/audio/declicked-normalized
```

**Declick before trimming.** Starting and stopping with a keypress puts the key
click *inside* the take, and silence trimming will not remove it — a click is
loud, so it is the trim's stopping point rather than something the trim cuts,
and normalization then lifts it toward full scale. Measured on a real recording
here it reached −3 dBFS in the finished mux, louder than the narration.

Skip the declick pass if you recorded hands-free; then trim `audio/raw` into
`audio/trimmed` and normalize into `audio/normalized`, which is what
`build_video.sh` defaults to.

### 5. Build and validate

```bash
$SKILL/build_video.sh   $D $D/talk.mp4 audio/declicked-normalized
$SKILL/validate_video.sh $D/talk.mp4 $D/spec.json
```

The third argument is the audio directory relative to the build dir; it
defaults to `audio/normalized`, so pass it whenever you used the declick chain.
Slide count and audio count must match exactly — the script hard-fails rather
than silently zipping the shorter list.

Rename to the submission filename **only after** validation passes, so a
non-compliant file can never be mistaken for a finished one:

```bash
mkdir -p $D/out
cp $D/talk.mp4 "$D/out/ID2664_J09_Bester.mp4"
```

Confirm the abstract ID and the exact session identifier with the organisers —
do not infer them from the deck title. A wrong ID is a rejected submission.

### 6. Captions

```bash
$SKILL/captions_from_script.py $D
```

Built from the narration and the per-slide audio durations, not from ASR: when
the talk was read per-slide the script *is* the transcript, so this needs no
model and cannot mangle a domain term. Output is `out/talk.srt`; submit it as a
sidecar rather than burning it in.

### Re-recording one slide

The point of the per-slide layout. Nothing else has to be touched:

```bash
$SKILL/record_narration.py $D --only 37          # or --only 37 38 39

$SKILL/declick_takes.py   $D/audio/raw       $D/audio/declicked
$SKILL/trim_silence.sh    $D/audio/declicked $D/audio/declicked-trimmed
$SKILL/normalize_audio.sh $D/audio/declicked-trimmed $D/audio/declicked-normalized

$SKILL/build_video.sh $D $D/talk.mp4 audio/declicked-normalized
$SKILL/validate_video.sh $D/talk.mp4 $D/spec.json
$SKILL/captions_from_script.py $D
```

The cleanup passes are cheap and rerunning them over the whole directory keeps
normalization consistent across the set — which is the point of the two-pass
loudness measurement. Do **not** normalize one file on its own.

**The one rule: this is only safe while the frame count is unchanged.** Frames
are numbered, and audio is matched to them by number alone. So:

| What changed | What to do |
|---|---|
| Wording of a take | `--only N`, then the block above. Nothing else moves. |
| A figure, colour scale, or caption on a slide | Re-render, re-extract frames, rebuild. **No re-recording** — the frame count is identical, so every take still lines up. |
| Text that adds or removes a fragment | Every later frame shifts by one. Re-extract, renumber `narration.md` to match, and re-record only the frames whose *content* changed — but rename the existing `audio/raw/slide-NN.wav` files to their new numbers first. |
| A slide added, removed, or reordered | Same as above, and there is no shortcut. Re-extract, fix the narration numbering, shift the audio filenames, re-record the genuinely new blocks. |

After any of the last three, re-run `check_script.py --frames` before rebuilding
— it is the only thing that will tell you the script and the frames disagree.

### If it comes out too long

In this order, stopping as soon as it fits:

1. Re-trim with a tighter pad: `trim_silence.sh $D/audio/declicked $D/audio/declicked-trimmed 0.10`.
2. Cut whole slides, and thin the narration to match.
3. Re-record the two or three longest blocks against a tightened script.

Do **not** speed up the video. It is audible, it reads as panic, and it wrecks
equation-heavy slides where the audience needs dwell time.

## Manim animations

Manim (Community Edition) currently lives in a uv-managed venv at
`~/software/manim/.venv`; all examples below call that binary directly. Once
the cairo headers are installed (`sudo apt install libcairo2-dev
libpango1.0-dev`), `uv sync --group manim` puts it in the repo's own
environment and `uv run manim …` replaces the long path.

There are two distinct workflows:

### 1. Standalone explainer videos (`_animations/`)

Each video is one directory containing a `scenes.md` plan and a single script
with one `Scene` class. Rendering is a two-speed loop — low quality while
iterating, high quality once the script is final:

```bash
cd _animations/uvw-and-lmn

# Dev loop: 480p / 15 fps, renders in ~a minute
~/software/manim/.venv/bin/manim -ql uvw_lmn.py UVWAndLMN

# Final: 1080p / 60 fps (3D scenes take considerably longer)
~/software/manim/.venv/bin/manim -qh uvw_lmn.py UVWAndLMN
```

The last argument is the **scene class name** inside the script. Output lands in
`media/videos/<script-stem>/<quality>/<SceneName>.mp4` next to the script, e.g.
the final render above produces

```
_animations/uvw-and-lmn/media/videos/uvw_lmn/1080p60/UVWAndLMN.mp4
```

`media/` is gitignored (and on this machine a symlink into `/data/talks/`) —
only scripts and `scenes.md` plans are committed, so re-running the render
command above regenerates any video from scratch.
Quality flags: `-ql` 480p15 · `-qm` 720p30 · `-qh` 1080p60 · `-qk` 4K60.

Three helper scripts in `_animations/` wrap the repeatable parts:

```bash
# new episode: directory + scenes.md skeleton + series-boilerplate script
python _animations/scaffold_video.py deconvolution Deconvolution "Deconvolution"

# dev render + spot-check frames extracted to /data/tmp/manim-frames/<Scene>/
_animations/preview.sh uvw_lmn.py UVWAndLMN

# final render with stale-partials cleanup and a duration sanity check
_animations/final.sh uvw_lmn.py UVWAndLMN
```
A render that was killed partway leaves `partial_movie_files/` behind, and a
truncated segment in there poisons later runs — manim either stitches a short,
broken mp4 or dies with `InvalidDataError` (`--flush_cache` does *not* clear
the bad segment). `final.sh` guards against this automatically; if rendering
by hand, delete that quality's partials and re-run:

```bash
rm -rf media/videos/uvw_lmn/1080p60/partial_movie_files
~/software/manim/.venv/bin/manim -qh uvw_lmn.py UVWAndLMN
```

Sanity-check the result with
`ffprobe -v error -show_entries format=duration -of csv=p=0 <file>.mp4` —
the duration should match what the dev render reported.

### 2. Transparent clips embedded in talk slides

The script lives beside the deck's `index.qmd`; the clip goes in its `videos/`
(a symlink into `/data/talks/` — see Publishing for how videos reach the site).

```bash
# 1. Render scene with transparent background to .mov
~/software/manim/.venv/bin/manim -t -qm script.py SceneName

# 2. Convert to WebM with working VP9 alpha (direct webm export is buggy)
ffmpeg -y -i media/videos/script/720p30/SceneName.mov \
  -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 \
  -b:v 2M videos/clip.webm
```

Embed in the `.qmd` with `{{< video videos/clip.webm >}}`.

## Publishing

Every push to `main` runs `.github/workflows/publish.yml`, which renders the
whole site and deploys it to GitHub Pages at
<https://landmanbester.github.io/talks/> — one shareable URL per deck
(e.g. `…/talks/lectures/visibility-space/`). It can also be run by hand from the
repo's Actions tab.

Videos are not in git. Each deck's `videos/` is a symlink into `/data/talks/`,
and the workflow downloads them from the `site-videos` release. When you add or
re-render a video, upload the set **before** pushing:

```bash
scripts/publish-videos.sh       # tar every */*/videos and upload to the release
git push origin main            # the workflow renders and deploys
```

The workflow fails (rather than publishing a broken deck) if a deck references
a video that is not in the release. One-time setup: Settings → Pages → Source:
"GitHub Actions".
