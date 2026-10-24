# Talks — Agent Context

> Single source of truth for AI coding agents. `CLAUDE.md` and `GEMINI.md` are symlinks to this file.
> `README.md` is the human-facing guide; this file holds the rules.

## Project overview

Quarto revealjs presentations for technical talks at SARAO / Rhodes / AIMS South Africa. Decks are
written fresh or ported from Canva (PDF export) or Beamer, then refined until the slides look right.

Prioritize semantic structure, reproducible visualizations, and clean Markdown over pixel-perfect
mimicry of the original deck. Never recreate Canva's visual layouts with custom HTML/JS positioning hacks.

## Skills

Task-specific instructions live in `.agents/skills/<name>/SKILL.md`. Claude Code discovers them
automatically via the `.claude/skills` symlink; **other agents must read the `SKILL.md` themselves**
before starting the matching task — the file is the instruction set, not background reading.

| Task | Read |
|---|---|
| Create, port, render, or debug a deck | `.agents/skills/quarto-revealjs/SKILL.md` |
| Record / assemble a talk video from a deck | `.agents/skills/quarto-talk-video/SKILL.md` |
| Plan an explainer animation (before any code) | `.agents/skills/manim-composer/SKILL.md` |
| Write ManimCE code | `.agents/skills/manimce-best-practices/SKILL.md` |

Paths in a `SKILL.md` are relative to that skill's own directory, not to the repo root — the repo
also has a top-level `scripts/`, so always invoke a skill's helper by its full path
(`.agents/skills/quarto-talk-video/scripts/build_video.sh`).

Where a skill and this file disagree, this file wins.

## Directory structure

Talks are split into two classes. **The class a deck lives in decides its formatting and which
rules apply** — each class directory carries its own `AGENTS.md`, loaded automatically when working
in that subtree. Read it before authoring.

- **`lectures/`** — teaching material, revised and re-given. Undated (`date: today`).
- **`contributions/`** — conference and workshop talks, each given once. Hard-coded event date.

```
talks/
├── AGENTS.md                # This file (CLAUDE.md / GEMINI.md symlink here)
├── _quarto.yml              # Website project: renders */*/index.qmd into _site/
├── index.qmd                # Listing page: one table per class
├── pyproject.toml, uv.lock  # Python env for the repo's tooling (`uv sync`)
├── templates/
│   ├── dark-academic.scss   # Shared dark theme (canonical copy)
│   ├── lectures.scss        # Lecture layer on top of the shared theme
│   ├── contributions.scss   # Contribution layer
│   └── title-slide.html     # Title-slide partial: event line + logo strip
├── assets/logos/            # Shared logos + meerkat-milkyway.jpg title background
├── lectures/ , contributions/
│   ├── AGENTS.md            # Class rules (CLAUDE.md / GEMINI.md symlink here)
│   ├── _metadata.yml        # Front matter shared by every deck in the class
│   └── <talk-slug>/
│       ├── index.qmd        # The presentation (always index.qmd)
│       ├── images/          # Figures for this talk
│       ├── videos/          # Embedded clips (manim webm, footage)
│       └── custom.css       # Optional deck-local CSS — declare it (see below)
├── scripts/
│   ├── check_slides.py      # Measure every slide for overflow (verification harness)
│   ├── shoot-decks.sh       # Render + screenshot every deck's title slide
│   ├── sync-data.sh         # /data/talks/ ⇄ Google Drive (see Large data)
│   ├── backup-takes.sh      # Mirror raw narration takes to the other disk
│   └── figures/             # FITS → slide-ready PNGs from a YAML spec (own README)
├── figures/scratch/         # Generated figures not currently on a slide
├── fits_files → /data/…     # FITS feeding scripts/figures/ (gitignored)
├── reference_pdfs/          # Canva PDF exports to port from (gitignored)
├── _animations/<video>/     # Standalone manim explainer: scenes.md + one script
├── _video/<talk-slug>/      # Talk-video build: spec.json + script/ tracked, rest gitignored
├── docs/superpowers/        # Design specs and plans for past repo-wide changes
└── .agents/skills/          # Agent skills (.claude/skills symlinks here)
```

The leading underscore on `_animations/` and `_video/` keeps Quarto's site render out of them.
For the same reason **never prefix a talk directory with `_`** — the deck silently will not render.

### Large data

The machine's main drive is small; large files live on `/data/talks/` and are symlinked into the
repo at the paths above, so scripts see ordinary paths:

| Repo path | What |
|---|---|
| `fits_files` | FITS images for `scripts/figures/` |
| `_video/<slug>/audio` | Narration takes and every processed stage |
| `_animations/<video>/media`, `<deck>/media` | manim render output and caches |

Put new large inputs or outputs under `/data/talks/` and symlink them in the same way. `/tmp` is
RAM on this machine — scratch output bigger than a few screenshots goes in `/data/tmp/`. The
`.gitignore` patterns for these have **no trailing slash** on purpose — `dir/` only matches real
directories, not symlinks.

`/data/talks/` has a Google Drive copy, kept in step by hand with `scripts/sync-data.sh` (rclone
remote `talks-drive:`; the folder ID lives in the rclone config, not here). Transfers are by MD5,
so an unchanged file never moves:

```bash
scripts/sync-data.sh status       # what differs
scripts/sync-data.sh push -n      # dry run, then without -n: local → Drive
scripts/sync-data.sh pull         # fresh clone / other machine: fetch, then symlink into the repo
```

Push mirrors, but anything it would delete or overwrite on Drive is moved to `_deleted/<time>/`
there instead. Pull only fetches files missing locally. manim `media/` is not synced.

**`_video/<slug>/audio/raw/` is the only irreplaceable thing in the repo** — every other stage and
artifact is rebuilt from tracked source. After any recording session run `scripts/sync-data.sh
push` and `scripts/backup-takes.sh` (a second local copy in `~/backups/talks-takes`, on the other
disk).

### Python environment

`uv sync` builds `.venv/` from `pyproject.toml` with what `scripts/figures/` needs; run tools with
`uv run scripts/figures/make_figures.py …`. `check_slides.py` is stdlib-only;
the talk-video scripts need only numpy (so `uv run` them, or any python3 with numpy).

manim is the opt-in `manim` dependency group, because pycairo needs system headers this machine
does not have yet (`sudo apt install libcairo2-dev libpango1.0-dev && uv sync --group manim`).
Until then manim runs from `~/software/manim/.venv/bin/manim`.

## Authoring conventions

Front matter shared by a class — theme, revealjs options, title background, logos — is hoisted into
`<class>/_metadata.yml`. A deck's own front matter carries only what is specific to it; the class
`AGENTS.md` lists what that is. Relative paths in `_metadata.yml` resolve from the *document*
(hence `../../templates/…`); `/`-prefixed paths resolve from the project root and Quarto rewrites
them per deck.

**Nothing in front matter is enforced** — a deck with only a `title:` must render and the site must
build. Never add schema checks or validation.

Create a deck with the scaffold script; the class argument is required:

```bash
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py lecture "Interferometry Basics"
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py contribution "KAT-7 Transient Search"
```

- **Directory naming** — descriptive slugs without dates (`stimela-fundamentals/`)
- **No footer** — omit `footer:`; it takes up too much space on dense slides
- **Deck-local CSS** — put it in `custom.css` beside `index.qmd` and declare it in the deck's own
  front matter (`format: revealjs: css: custom.css`). Nothing is hoisted, so a deck without
  extra styling needs no file. Classes several decks want belong in the theme — ask first
- **MathJax macros** use MathJax 2 syntax: `TeX: { Macros: {} }` (uppercase — not
  `tex: { macros: }`), injected via `include-in-header`
- **Unsupported LaTeX**: the bundled MathJax cannot load `\cancel` (renders red or
  `[Math Processing Error]`) and has no mathtools commands like `\xleftrightarrow`. Substitutes:
  `\underbrace{w_{pq}(n-1)}_{\approx\, 0}` for striking out a term,
  `\overset{\mathcal{F}}{\longleftrightarrow}` for a labelled arrow
- **No inline HTML for layout** — no `<style>` tags, flexbox hacks, or JS positioning. Use fenced divs:
  ```markdown
  :::: {.columns}
  ::: {.column width="50%"}
  Left
  :::
  ::: {.column width="50%"}
  Right
  :::
  ::::
  ```
- **Full-slide graphics**: `## Slide Title {background-image="images/asset.png"}`
- **Clickable screenshots**: `![alt](images/screenshot.png){fig-link="https://url.com"}`. A
  standalone image (the only content on a slide) loses its link — use `[![alt](img.png)](url)`
- **Executable code**: when demonstrating software, prefer Python blocks with `#| echo: true`,
  `#| eval: false` over static text
- **Fragments**: `. . .` pauses work only at **top level** — inside `:::` divs they render as three
  literal dots. Inside divs use `{.incremental}` lists or `{.fragment}` divs. Use these built-in
  mechanisms; no custom CSS animations
- **Syncing fragments across columns**: fragments fire in DOM order, so the left column always goes
  first. Set `fragment-index` explicitly, e.g. `::: {.fragment fragment-index=2}` — works on images
  too: `![](img.png){.fragment fragment-index=1}`
- **Progressive image swap**: stack images in `::: {.r-stack}` with `.fragment` on all but the
  first; pair with `fragment-index` on bullets to swap the image as each bullet appears
- **Dense slides**: `{.smaller}` on the heading. Never a wrapping `{style="font-size:…"}` div — it
  breaks `. . .` pauses
- **Closing slide**: `## Thanks! {background-color="#0d1117" .closing-slide}` with a `::: {.contact}`
  div. Do NOT nest a `## Thanks!` heading inside a `.closing-slide` div on an empty `##` slide —
  pandoc splits it into its own slide, leaving a stray empty one before it
- **Embedded video**: `{{< video videos/clip.webm >}}`, not a raw `<video>` tag. The exception is a
  clip that must autoplay muted — browsers only honour `muted`/`autoplay` reliably as parse-time
  attributes, which the shortcode cannot emit. `contributions/kremetart-pipeline` does this twice:
  a full-bleed background (`.bg-fill`) and an inline looping manim clip

### Theme classes (`dark-academic.scss`)

| Class | Use |
|---|---|
| `.highlight-box` | Key equations, definitions (blue border) |
| `.result-box` | Important results, theorems (green border) |
| `.muted` | Secondary notes, small print |
| `.small` | Explicit small text (0.7em) |
| `.closing-slide` | The final "Thanks!" slide |
| `.contact` | Monospace contact line on closing slide |
| `.overlay-caption` | Caption pill over a full-bleed background; tune `font-size` per deck |
| `.bottom-caption-slide` on heading | Full-bleed slide: hides the empty `##`, pins captions to the bottom |
| `.plain-figure` on heading | Hides the empty `##` so a figure gets the whole slide |
| `{.smaller}` on heading | Reduce entire slide font to ~70% |
| `{.incremental}` on list | Reveal list items one by one |

### Mermaid diagrams

Translate pipelines, architectures, and systems into Mermaid. Unstyled Mermaid looks bare on dark
slides — always style it. `mermaid-format: svg` is inherited from `_metadata.yml` (the default `js`
format overrides custom themes).

- Configure with a **YAML config block inside the cell** (not `%%{init:...}%%`), `theme: base`, and
  `themeVariables` matching the dark-academic palette
- **Always set both `%%| fig-width:` and `%%| fig-height:`** — without a height the SVG container
  reserves far more vertical space than the diagram needs and pushes content off the slide (a 4-node
  `flowchart LR` wants `fig-width: 9`, `fig-height: 1.8`). Too wide a `fig-width` adds a scrollbar
- The first line after the config declares the diagram type (`flowchart TD`, `sequenceDiagram`)
- **No quotation marks or parentheses** inside node labels — they break the parser
- `<br />` for line breaks in labels (not `\n`); `&nbsp;` padding for wider nodes
- Start labels with a Unicode emoji for meaning (`📡 Array`, `📦 CABS`, `⚙️ Stimela`)

## Render, inspect, fix

The repo root is a Quarto website project. All output, including single-deck renders, goes to
`_site/<class>/<talk-slug>/` (gitignored).

```bash
cd lectures/<talk-slug> && quarto preview index.qmd   # edit loop; serves /lectures/<talk-slug>/
quarto render                                         # from the root: listing + every deck
quarto publish gh-pages                               # publish _site/ to GitHub Pages
```

PDF export (decktape, print-to-PDF, self-contained HTML):
`.agents/skills/quarto-revealjs/references/pdf-export.md`.

### Screenshot a slide

With the preview server running, note its port:

```bash
google-chrome --headless=new --screenshot=/tmp/slide.png --window-size=1600,900 \
  --virtual-time-budget=5000 "http://localhost:PORT/lectures/<talk-slug>/#/slide-anchor"
```

- The anchor is the slide heading lowercased and hyphenated (`#/the-proximal-operator`)
- Slides nested under a `#` section use `#/H/V` (both 0-indexed): `#/2/3` is the 4th slide of the
  3rd section
- A URL cannot set fragment state — headless screenshots show the pre-fragment state. Hidden
  fragments still occupy layout space (`visibility: hidden`), so vertical positions are final
- For the fully-revealed state use `scripts/check_slides.py --shots`. Never hand-edit
  `fragments: false` into front matter — an interrupted run leaves the deck broken

### Find overflow

Measure it rather than eyeballing screenshots:

```bash
scripts/check_slides.py                    # render, then check every deck
scripts/check_slides.py --no-render deconvolution
scripts/check_slides.py --no-render --shots /data/tmp/shots deconvolution   # + every slide, revealed
```

- **CLIPPED** (exit 1) — taller than ~778px, cut off on screen. Fix it.
- **tight** — over the 700px design height but still visible inside reveal's 10% margin. A
  judgement call; it reads as cramped. `--strict` fails on these too.

Deck sources are never modified — the probe runs on a throwaway copy inside `_site/`.

| Cause of overflow | Fix |
|---|---|
| Too much text / too many equations | `{.smaller}` on the heading |
| Two independent blocks of content | `:::: {.columns}` |
| Genuinely too much content | Split the slide (contributions: cut, don't shrink) |
| Long callout at the bottom | Shorten, move to a column, or its own slide |
| Mermaid diagram | Set `%%| fig-height:` |
| Tall image in a column | `{height="500"}` instead of `width="100%"` |

## Talk videos

A deck plus per-slide narration becomes a conference-compliant MP4 via the
[`quarto-talk-video`](.agents/skills/quarto-talk-video/SKILL.md) skill. **Read it before touching
ffmpeg** — its scripts encode the compliance checks (duration limits, codec, submission filename)
and hard-fail on the silent failure modes. Audio is recorded per slide, so a fluffed line costs one
re-read, not the whole take. Build dir is `_video/<talk-slug>/`. Captions are built
from the narration script; whisper (not installed) is only needed if the delivery departed from it.

## Manim animations

Two products: **transparent clips embedded in slides** and **standalone explainer videos** under
`_animations/`. Plan with `manim-composer` before writing code; implement with
`manimce-best-practices`. Interpreter: see [Python environment](#python-environment).

### Slide clips (transparent webm)

The script lives beside the deck's `index.qmd` (with its `scenes.md` plan if it has one); the clip
goes in the deck's `videos/`. Render in two steps — manim's direct `--format=webm` does not encode
VP9 alpha properly:

```bash
manim -t -qm script.py SceneName          # -t transparent; -qh for the final
ffmpeg -y -i media/videos/script/720p30/SceneName.mov \
  -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 -b:v 2M videos/clip.webm
```

`-auto-alt-ref 0` is required for the alpha channel. Symlink the deck's `media/` to `/data/talks/`
before a long render (see [Large data](#large-data)).

### Standalone explainer videos (`_animations/`)

One directory per video: a `scenes.md` plan plus a single script with one `Scene` class. Only those
two files are committed. Scaffold a new episode with the series boilerplate (palette, master clock,
caption helper, title/closing cards):

```bash
python _animations/scaffold_video.py <slug> <SceneClassName> "<Title>" --subtitle "..."
```

Series conventions (`two-element-interferometer` → `what-is-a-visibility` → `aperture-synthesis` →
`uvw-and-lmn`): dark-academic palette (bg `#0d1117`, blue `#58a6ff` antenna p, amber `#d29922`
antenna q / sky brightness, green `#3fb950` measurements/results, red `#f85149` mismatch), `Text`
captions at the top edge (font 27), a title card, and a closing card teasing the next episode.

- **Master-clock architecture**: one `ValueTracker` clock advanced by a dt-updater scaled by a
  `rate` tracker; every moving element is an `always_redraw` reading the same trackers, so
  consistency holds by construction instead of choreography
- Prefer computing real data in updaters over staging effects — the aperture-synthesis
  reconstruction is a genuine masked-FFT inverse (`ImageMobject` from a uint8 array)

Render opaque (no `-t`): `-ql` (480p15) for the dev loop, `-qh` (1080p60) for the final. Output
lands in `media/videos/<script-stem>/<quality>/<Scene>.mp4`. Use the helpers rather than
hand-rolled commands:

```bash
_animations/preview.sh <script.py> <Scene>              # -ql render + 10 frames to Read
_animations/preview.sh --no-render <script.py> <Scene> 35 60   # frames at given times
_animations/final.sh <script.py> <Scene>                # -qh, clears partials, checks duration
```

`final.sh` warns if the duration drifts more than 5 s from the dev render; run it in the
background for 3D or long scenes.

Check every scene's key beat at `-ql` before the final run. If rendering by hand:

- Piping manim (e.g. `| tail`) masks its exit code — run it bare
- A killed render leaves a truncated segment in `partial_movie_files/` that poisons later runs
  (short mp4 or `InvalidDataError`; `--flush_cache` does NOT fix it) — delete that quality's
  `partial_movie_files/` before a final render
- Always ffprobe the final duration: 15 vs 60 fps renders drift ~1s; a broken stitch loses tens

### ManimCE gotchas (hit in this repo)

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

## Boundaries

- **Ask first** before cross-cutting structural changes: editing the shared theme
  (`templates/dark-academic.scss`), adding shared CSS/SCSS files, or repository-wide refactors
- **Never** run destructive commands (`rm -rf`, history rewrites) without explicit approval — and
  never delete anything under `_video/*/audio/raw/`
