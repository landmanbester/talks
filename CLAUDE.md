# Talks — Claude Code Context

## Project overview

This directory contains Quarto revealjs presentations for technical talks at SARAO / AIMS South Africa. The workflow is: port presentations from Canva (PDF export) into Quarto revealjs, then refine until the slides look right.

## Directory structure

```
talks/
├── CLAUDE.md
├── templates/
│   └── dark-academic.scss          # Shared dark theme for all talks
├── assets/
│   └── logos/
│       ├── sarao-nrf.png           # Shared logos
│       ├── aims.png
│       └── meerkat-milkyway.jpg    # Standard title slide background
├── YYYY-MM-DD-talk-name/
│   ├── index.qmd                   # The presentation
│   ├── custom.css                  # Optional per-talk CSS overrides
│   └── images/                     # Images for this talk (copy shared assets here)
└── ...
```

## Workflow: PDF → Quarto

### 1. Scaffold and port

Use the `quarto-revealjs` skill to scaffold and port:

```
/quarto-revealjs
```

The skill contains:
- **references/** — theme guide, scaffolding conventions, CSS classes available in `dark-academic.scss`
- **examples/** — reference presentations to follow for style and structure
- **scripts/** — `scaffold_talk.py` for creating a new talk directory

Key conventions:
- Theme path from a talk: `../templates/dark-academic.scss`
- **No footer** — omit `footer:` entirely; it takes up too much space on dense slides
- **Standard title background**: copy `../assets/logos/meerkat-milkyway.jpg` to `images/` and set `data-background-image: images/meerkat-milkyway.jpg` with `data-background-opacity: "0.5"` in `title-slide-attributes`
- MathJax macros use MathJax 2 syntax: `TeX: { Macros: {} }` (uppercase, not `tex: { macros: }`)
- Fragment pauses (`. . .`) must be at **top level** — they break silently inside `:::` divs (renders as literal dots). Inside divs, use `{.incremental}` for lists or wrap content in `{.fragment}` divs instead
- Dense slides: use `{.smaller}` on the heading (not a wrapping div) to reduce font without breaking fragments
- **Mermaid diagrams**: set `mermaid-format: svg` in the YAML front matter (under `revealjs:`) — the default `js` format overrides custom themes. Use YAML config blocks inside Mermaid cells (not the older `%%{init:...}%%` syntax) with `theme: base` and custom `themeVariables` for full control over colors matching the dark-academic palette. Use `%%|` cell options for sizing (e.g. `%%| fig-width: 4.5`). Use emoji prefixes in labels for semantic meaning (e.g. `📦 CABS`, `⚙️ Stimela`). Use `<br />` for line breaks in labels (not `\n`). Add `&nbsp;` padding in labels for wider nodes. Do NOT use quotation marks or parentheses inside node labels. Plain unstyled Mermaid looks too bare on dark slides
- **Code block scrollbars**: Quarto injects `.reveal div.sourceCode { overflow: auto; }` which causes a cosmetic horizontal scrollbar even when code fits. Fix with a `custom.css` file containing `.reveal div.sourceCode { overflow-x: hidden !important; }`, referenced via `css: custom.css` in the YAML `revealjs:` block

### 2. Render

```bash
cd talks/YYYY-MM-DD-talk-name
quarto preview index.qmd
```

### 3. Inspect with headless Chrome

With the preview server running (note the port from the `quarto preview` output), take a screenshot of any slide to see exactly what renders:

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

Avoid wrapping content in arbitrary `{style="font-size:..."}` divs — this breaks `{. . .}` fragment pauses.

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

## Manim animations

For complex math/physics visualizations that go beyond static slides, use standalone Python scripts with the `manim` library (3Blue1Brown community).

### Environment

Manim is installed in a virtualenv at `~/software/manim/.venv`. Activate it before rendering:
```bash
source ~/software/manim/.venv/bin/activate
```

### Workflow

1. **Write** a standalone `.py` script (not an inline code block)
2. **Render** to `.mov` with transparent background (two-step process):
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
