# Talks

Quarto revealjs presentations for technical talks at SARAO / AIMS South Africa.
One directory per talk, a shared dark theme, and a root-level Quarto **website
project** that builds everything into a single browsable site.

Agent conventions (porting workflow, theme classes, Mermaid/Manim rules) live in
[AGENTS.md](AGENTS.md) — `CLAUDE.md` is a symlink to it.

## Layout

```
talks/
├── _quarto.yml            # Website project config — renders index.qmd + */index.qmd
├── index.qmd              # Listing page: auto-generated table of all talks
├── templates/
│   └── dark-academic.scss # Shared theme (canonical copy; the skill symlinks to it)
├── assets/logos/          # Shared logos + meerkat-milkyway.jpg title background
├── reference_pdfs/        # Canva PDF exports to port from (gitignored)
├── .claude/skills/        # quarto-revealjs + manim skills for Claude Code
├── <talk-name>/
│   ├── index.qmd          # The presentation (always index.qmd)
│   ├── custom.css         # Scrollbar fix
│   └── images/            # Talk-specific images
└── _site/                 # Rendered site (gitignored — never edit by hand)
```

## How the website project works

The root `_quarto.yml` makes this directory a Quarto project. Any `quarto`
command run anywhere inside it operates in project context:

- **All output goes to `_site/`** — including single-talk renders, which land in
  `_site/<talk-name>/`. Nothing renders in-place next to the `.qmd` anymore.
- The root `index.qmd` is a **listing page**: it reads `title` and `institute`
  from each talk's front matter and builds the table automatically. Add a new
  talk directory → it appears on the next render. No manual index editing.
- Referenced resources (images, webm animations) are copied into `_site/`
  automatically.

## Everyday commands

```bash
# Edit loop: live preview of one talk (auto-reloads on save)
cd <talk-name>
quarto preview index.qmd
# → serves at http://localhost:PORT/<talk-name>/  (note the prefix!)

# Build everything: listing page + all talks
quarto render            # from the repo root → _site/

# View the built site locally
quarto preview           # from the repo root
# or just open _site/index.html in a browser
```

To create a new talk, use the `quarto-revealjs` skill in Claude Code
(`/quarto-revealjs`) — it scaffolds the directory, theme reference, custom.css,
and title-slide background.

## Rendering to PDF

Three options, in order of preference (full details in
`.claude/skills/quarto-revealjs/references/pdf-export.md`):

**1. decktape — best fidelity to the HTML slides**

```bash
quarto render <talk-name>/index.qmd
npx decktape reveal --size 1600x900 _site/<talk-name>/index.html slides.pdf
```

**2. Browser print-to-PDF — no tooling needed**

Open the talk with `?print-pdf` appended, e.g.
`http://localhost:PORT/<talk-name>/?print-pdf`, then Ctrl+P → Save as PDF
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

Manim (Community Edition) lives in a uv-managed venv at `~/software/manim/.venv`:

```bash
source ~/software/manim/.venv/bin/activate

# 1. Render scene with transparent background to .mov
manim -t -qm script.py SceneName          # -qh for the final render

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
