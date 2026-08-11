# Talks

Quarto revealjs presentations for technical talks at SARAO / Rhodes/ AIMS South Africa.
One directory per talk, a shared dark theme, and a root-level Quarto **website
project** that builds everything into a single browsable site.

Agent conventions (porting workflow, theme classes, Mermaid/Manim rules) live in
[AGENTS.md](AGENTS.md) — `CLAUDE.md` is a symlink to it.

## Layout

Talks come in two classes, and the class a deck lives in decides its
formatting and the agent rules that apply to it:

- **`lectures/`** — teaching material, revised and re-given. Undated
  (`date: today`), institutional logos only.
- **`contributions/`** — conference and workshop talks, each given once.
  Carries the event date, and event logos alongside the institutional ones.

```
talks/
├── _quarto.yml            # Website project config — renders index.qmd + */*/index.qmd
├── index.qmd              # Listing page: one table per class
├── templates/
│   ├── dark-academic.scss # Shared theme (canonical copy; the skill symlinks to it)
│   ├── lectures.scss      # Lecture-specific layer on top of the shared theme
│   ├── contributions.scss # Contribution-specific layer
│   └── title-slide.html   # Title-slide partial; renders the logo strip
├── assets/logos/          # Shared logos + meerkat-milkyway.jpg title background
├── scripts/
│   └── shoot-decks.sh     # Render + screenshot every deck (verification harness)
├── reference_pdfs/        # Canva PDF exports to port from (gitignored)
├── .claude/skills/        # quarto-revealjs + manim skills for Claude Code
├── _animations/           # Standalone manim explainer videos (one dir per video:
│   └── <video-name>/      #   scenes.md plan + script; renders land in media/, gitignored)
├── lectures/
│   ├── AGENTS.md          # Lecture rules (CLAUDE.md symlinks to it)
│   ├── _metadata.yml      # Shared front matter for every lecture
│   └── <talk-name>/
│       ├── index.qmd      # The presentation (always index.qmd)
│       ├── custom.css     # Scrollbar fix (required — `css:` is hoisted)
│       └── images/        # Talk-specific images
├── contributions/
│   ├── AGENTS.md          # Contribution rules (CLAUDE.md symlinks to it)
│   ├── _metadata.yml      # Shared front matter for every contribution
│   └── <talk-name>/       # Same shape as a lecture
└── _site/                 # Rendered site (gitignored — never edit by hand)
```

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
  background, and `css:` come from the class `_metadata.yml`, so a deck's own
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

To create a new talk, use the `quarto-revealjs` skill in Claude Code
(`/quarto-revealjs`), or run the scaffold script directly with the required
class argument:

```bash
python .claude/skills/quarto-revealjs/scripts/scaffold_talk.py lecture "Interferometry Basics"
python .claude/skills/quarto-revealjs/scripts/scaffold_talk.py contribution "KAT-7 Transient Search"
```

## Rendering to PDF

Three options, in order of preference (full details in
`.claude/skills/quarto-revealjs/references/pdf-export.md`):

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

## Manim animations

Manim (Community Edition) lives in a uv-managed venv at `~/software/manim/.venv`.
Either activate it (`source ~/software/manim/.venv/bin/activate`) or call the
binary directly — all examples below use the direct path.

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

`media/` is gitignored — only scripts and `scenes.md` plans are committed, so
re-running the render command above regenerates any video from scratch.
Quality flags: `-ql` 480p15 · `-qm` 720p30 · `-qh` 1080p60 · `-qk` 4K60.

Three helper scripts in `_animations/` wrap the repeatable parts:

```bash
# new episode: directory + scenes.md skeleton + series-boilerplate script
python _animations/scaffold_video.py deconvolution Deconvolution "Deconvolution"

# dev render + spot-check frames extracted to /tmp/manim-frames/<Scene>/
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

```bash
# 1. Render scene with transparent background to .mov
~/software/manim/.venv/bin/manim -t -qm script.py SceneName

# 2. Convert to WebM with working VP9 alpha (direct webm export is buggy)
ffmpeg -y -i media/videos/script/720p30/SceneName.mov \
  -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 \
  -b:v 2M images/animation.webm
```

Embed in the `.qmd` with `{{< video images/animation.webm >}}`.

## Publishing (when ready)

Once the repo has a GitHub remote:

```bash
quarto publish gh-pages
```

This pushes `_site/` to GitHub Pages — a permanent, shareable archive of every
talk at one URL.
