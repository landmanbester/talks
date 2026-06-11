# Talks — Agent Context

> Single source of truth for AI coding agents. `CLAUDE.md` is a symlink to this file.

## Project overview

This directory contains Quarto revealjs presentations for technical talks at SARAO / AIMS South Africa. The workflow is: port presentations from Canva (PDF export) or Beamer into Quarto revealjs, then refine until the slides look right.

Prioritize semantic structure, reproducible visualizations, and clean Markdown over pixel-perfect mimicry of the original deck. Never recreate Canva's visual layouts with custom HTML/JS positioning hacks.

## Directory structure

```
talks/
├── AGENTS.md / CLAUDE.md (symlink)
├── _quarto.yml                     # Website project: renders all talks + listing into _site/
├── index.qmd                       # Listing page of all talks
├── .claude/skills/
│   ├── quarto-revealjs/            # Scaffolding + porting skill (references, examples, scripts)
│   ├── manim-composer/             # Plan 3b1b-style animations (use BEFORE writing manim code)
│   └── manimce-best-practices/     # ManimCE implementation reference
├── templates/
│   └── dark-academic.scss          # Shared dark theme for all talks (canonical copy)
├── assets/
│   └── logos/                      # Shared logos + meerkat-milkyway.jpg title background
├── reference_pdfs/                 # Canva PDF exports to port from (gitignored)
├── talk-name/
│   ├── index.qmd                   # The presentation (always index.qmd)
│   ├── custom.css                  # Per-talk CSS overrides (scrollbar fix)
│   ├── images/                     # Images for this talk (copy shared assets here)
│   └── videos/                     # Manim renders (webm)
└── ...
```

## Workflow: PDF → Quarto

### 1. Scaffold and port

Use the `quarto-revealjs` skill to scaffold and port:

```
/quarto-revealjs
```

The skill contains:
- **references/** — theme guide, scaffolding conventions, porting guide, PDF export
- **examples/** — reference presentations to follow for style and structure
- **scripts/** — `scaffold_talk.py` for creating a new talk directory

### Authoring conventions

- **Directory naming** — descriptive slugs without dates (e.g. `stimela-fundamentals/`, not `2025-10-01-stimela-fundamentals/`)
- **Dynamic date** — always `date: today` in YAML front matter. Never hard-code dates
- Theme path from a talk: `../templates/dark-academic.scss`
- **No footer** — omit `footer:` entirely; it takes up too much space on dense slides
- **Standard title background**: copy `../assets/logos/meerkat-milkyway.jpg` to `images/` and set `data-background-image: images/meerkat-milkyway.jpg` with `data-background-opacity: "0.5"` in `title-slide-attributes`
- MathJax macros use MathJax 2 syntax: `TeX: { Macros: {} }` (uppercase, not `tex: { macros: }`)
- **No inline HTML for layout** — no `<style>` tags, no flexbox hacks, no JS positioning. Use Quarto's native fenced divs:
  ```markdown
  :::: {.columns}
  ::: {.column width="50%"}
  Left content
  :::
  ::: {.column width="50%"}
  Right content
  :::
  ::::
  ```
- **Full-slide graphics**: slide header attributes — `## Slide Title {background-image="images/asset.png"}`
- **Clickable screenshots**: `![alt](images/screenshot.png){fig-link="https://url.com"}`
- **Executable code**: when demonstrating software, prefer executable Python blocks (`#| echo: true`, `#| eval: false`) over static text
- **Fragments**: pauses (`. . .`) must be at **top level** — they break silently inside `:::` divs (render as literal dots). Inside divs, use `{.incremental}` for lists or wrap content in `{.fragment}` divs. Use these built-in mechanisms; no custom CSS animations
- Dense slides: use `{.smaller}` on the heading (not a wrapping div) to reduce font without breaking fragments
- **Code block scrollbars**: Quarto injects `.reveal div.sourceCode { overflow: auto; }` which causes a cosmetic horizontal scrollbar even when code fits. Fix with a `custom.css` containing `.reveal div.sourceCode { overflow-x: hidden !important; }`, referenced via `css: custom.css` in the YAML `revealjs:` block

### 2. Render and preview

The repo root is a Quarto website project (`_quarto.yml`): the root `index.qmd` is a listing page linking to every talk, and rendering outputs to `_site/` (gitignored).

```bash
# Single talk, live preview (the usual edit loop)
cd talks/talk-name
quarto preview index.qmd

# Everything: listing page + all talks → _site/
cd talks
quarto render
```

Because the talks live inside a project, all output (including single-file renders) goes to `_site/<talk-name>/`, and preview URLs are prefixed with the talk directory (e.g. `http://localhost:PORT/talk-name/#/slide-anchor`). To publish the whole collection to GitHub Pages once a remote exists: `quarto publish gh-pages`.

For PDF export, see the skill's `references/pdf-export.md`.

### 3. Inspect with headless Chrome

With the preview server running (note the port from the `quarto preview` output), screenshot any slide to see exactly what renders:

```bash
google-chrome --headless=new \
  --screenshot=/tmp/slide.png \
  --window-size=1600,900 \
  --virtual-time-budget=5000 \
  "http://localhost:PORT/#/slide-anchor"
```

- Use the slide heading text as the anchor, lowercased and hyphenated (e.g. `#/the-proximal-operator`)
- For nested slides (slides under a `#` section): use `#/H/V` where H = horizontal section index (0-indexed), V = vertical slide within that section (0-indexed). Example: `#/2/3` = 4th slide in the 3rd horizontal section
- Fragment state cannot be controlled via URL — headless screenshots always show the pre-fragment (initial) state
- Read `/tmp/slide.png` with the Read tool to see the rendered result

### 4. Fix overflow

Common causes of content falling off the bottom of the slide:

| Problem | Fix |
|---|---|
| Too much text / too many equations | Add `{.smaller}` to the `## Heading` |
| Two independent blocks of content | Two-column layout with `:::: {.columns}` |
| Slide genuinely has too much content | Split into two slides |
| Long callout at the bottom | Shorten, or move to a column, or its own slide |

Avoid wrapping content in arbitrary `{style="font-size:..."}` divs — this breaks `. . .` fragment pauses.

## Theme classes (dark-academic.scss)

| Class | Use |
|---|---|
| `.highlight-box` | Key equations, definitions (blue border) |
| `.result-box` | Important results, theorems (green border) |
| `.muted` | Secondary notes, small print |
| `.small` | Explicit small text (0.7em) |
| `.closing-slide` | The final "Thanks!" slide |
| `.contact` | Monospace contact line on closing slide |
| `{.smaller}` on heading | Reduce entire slide font to ~70% |
| `{.incremental}` on list | Reveal list items one by one |

## Mermaid diagrams

Translate pipelines, architectures, and systems into Mermaid code blocks. Plain unstyled Mermaid looks too bare on dark slides — always style.

- Set `mermaid-format: svg` in the YAML front matter (under `revealjs:`) — the default `js` format overrides custom themes
- Use **YAML config blocks inside the Mermaid cell** (NOT the older `%%{init:...}%%` directive syntax) with `theme: base` and custom `themeVariables` for full control over colors matching the dark-academic palette
- Use `%%|` cell options for sizing (e.g. `%%| fig-width: 4.5`)
- The first line after config must declare the diagram type (e.g. `flowchart TD`, `sequenceDiagram`)
- **Forbidden characters**: no quotation marks or parentheses inside node labels — they break the parser
- Use `<br />` for line breaks in labels (not `\n`)
- Start node labels with a Unicode emoji for semantic meaning (e.g. `📡 Array`, `📦 CABS`, `⚙️ Stimela`)
- Add `&nbsp;` padding in labels for wider nodes

## Manim animations

For complex math/physics visualizations beyond static slides, use standalone Python scripts with the `manim` library (Manim Community Edition).

Two skills support this: `manim-composer` (plan the animation scene-by-scene BEFORE writing code) and `manimce-best-practices` (implementation reference).

### Environment

Manim lives in a uv-managed environment at `~/software/manim/.venv`. Either activate it or call the binary directly:

```bash
source ~/software/manim/.venv/bin/activate
# or, without activation:
~/software/manim/.venv/bin/manim -t -qm script.py SceneName
```

### Workflow

1. **Write** a standalone `.py` script (not an inline code block)
2. **Render** to `.mov` with transparent background, then convert (two-step process):
   ```bash
   # Step 1: Render to .mov (reliable alpha via ARGB)
   manim -t -qm script.py SceneName

   # Step 2: Convert to WebM with proper VP9 alpha
   ffmpeg -y -i media/videos/script/720p30/SceneName.mov \
     -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 \
     -b:v 2M images/animation.webm
   ```
   - `-t` = transparent background (alpha channel)
   - `-qm` = medium quality (720p30, good for development; use `-qh` for final render)
   - Do NOT use `manim -t --format=webm` directly — it has a bug where VP9 alpha is not properly encoded
   - The `-auto-alt-ref 0` flag is required for VP9 alpha to work
3. **Embed** in `.qmd` using the native Quarto video shortcode:
   ```markdown
   {{< video images/animation.webm >}}
   ```
   Do NOT use raw `<video>` HTML tags.

## Boundaries

- **Ask first** before cross-cutting structural changes: editing the shared theme (`templates/dark-academic.scss`), adding new shared CSS/SCSS files, or repository-wide refactors
- **Never** run destructive commands (`rm -rf`, history rewrites) without explicit approval
