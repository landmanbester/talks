# Talks — Agent Context

> Single source of truth for AI coding agents. `CLAUDE.md` and `GEMINI.md` are symlinks to this file.

## Project overview

This directory contains Quarto revealjs presentations for technical talks at SARAO / AIMS South Africa. The workflow is: port presentations from Canva (PDF export) or Beamer into Quarto revealjs, then refine until the slides look right.

Prioritize semantic structure, reproducible visualizations, and clean Markdown over pixel-perfect mimicry of the original deck. Never recreate Canva's visual layouts with custom HTML/JS positioning hacks.

## Directory structure

Talks are split into two classes. **The class a deck lives in decides its
formatting and which rules apply** — each class directory carries its own
`AGENTS.md`, loaded automatically when working in that subtree.

- **`lectures/`** — teaching material, revised and re-given. Undated.
- **`contributions/`** — conference and workshop talks, each given once, dated.

```
talks/
├── AGENTS.md / CLAUDE.md / GEMINI.md (symlinks)  # Shared conventions (this file)
├── _quarto.yml                     # Website project: renders */*/index.qmd into _site/
├── index.qmd                       # Listing page: one table per class
├── .agents/skills/                 # Agent skills (.claude/skills symlinks here)
│   ├── quarto-revealjs/            # Scaffolding + porting skill (references, examples, scripts)
│   ├── manim-composer/             # Plan 3b1b-style animations (use BEFORE writing manim code)
│   └── manimce-best-practices/     # ManimCE implementation reference
├── templates/
│   ├── dark-academic.scss          # Shared dark theme (canonical copy)
│   ├── lectures.scss               # Lecture layer on top of the shared theme
│   ├── contributions.scss          # Contribution layer
│   └── title-slide.html            # Title-slide partial; renders the logo strip
├── assets/
│   └── logos/                      # Shared logos + meerkat-milkyway.jpg title background
├── scripts/
│   └── shoot-decks.sh              # Render + screenshot every deck (verification harness)
├── reference_pdfs/                 # Canva PDF exports to port from (gitignored)
├── _animations/
│   └── video-name/                 # Standalone manim explainer video: scenes.md plan +
│                                   #   one script; media/ output gitignored; the leading
│                                   #   underscore keeps Quarto's site render away
├── lectures/
│   ├── AGENTS.md / CLAUDE.md / GEMINI.md  # Lecture-specific rules — read before authoring
│   ├── _metadata.yml               # Shared front matter for every lecture
│   └── talk-name/
│       ├── index.qmd               # The presentation (always index.qmd)
│       ├── custom.css              # Scrollbar fix — REQUIRED, `css:` is hoisted
│       ├── images/                 # Images for this talk (copy shared assets here)
│       └── videos/                 # Manim renders (webm)
├── contributions/
│   ├── AGENTS.md / CLAUDE.md / GEMINI.md  # Contribution-specific rules
│   ├── _metadata.yml               # Shared front matter for every contribution
│   └── talk-name/                  # Same shape as a lecture
└── ...
```

## Workflow: PDF → Quarto

### 1. Scaffold and port

Follow the [`quarto-revealjs`](.agents/skills/quarto-revealjs/SKILL.md) skill to scaffold and port presentations.

Scaffolding takes a required class argument:

```bash
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py lecture "Interferometry Basics"
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py contribution "KAT-7 Transient Search"
```

The skill contains:
- **references/** — theme guide, scaffolding conventions, porting guide, PDF export
- **examples/** — reference presentations to follow for style and structure
- **scripts/** — `scaffold_talk.py` for creating a new talk directory

### Authoring conventions

- **Directory naming** — descriptive slugs without dates (e.g. `stimela-fundamentals/`, not `2025-10-01-stimela-fundamentals/`). Never prefix with `_` — Quarto skips underscore-prefixed directories and the deck silently will not render
- **Class rules live with the class** — `lectures/AGENTS.md` and `contributions/AGENTS.md` carry the front-matter, style, logo, and citation rules for their subtree, and load automatically when working there. **Dates differ between the two**: lectures use `date: today` and never hard-code; contributions hard-code the event date. Read the class file before authoring
- **Shared front matter is hoisted** — theme, revealjs options, title background, logos, and `css:` come from the class `_metadata.yml`. A deck's own front matter carries only what is specific to it. Relative paths in `_metadata.yml` resolve from the *document*, so the theme path is `../../templates/dark-academic.scss`
- **No footer** — omit `footer:` entirely; it takes up too much space on dense slides
- **Standard title background**: copy `../assets/logos/meerkat-milkyway.jpg` to `images/` and set `data-background-image: images/meerkat-milkyway.jpg` with `data-background-opacity: "0.5"` in `title-slide-attributes`
- MathJax macros use MathJax 2 syntax: `TeX: { Macros: {} }` (uppercase, not `tex: { macros: }`)
- **Unsupported LaTeX commands**: Quarto's bundled MathJax cannot load `\cancel` (the `cancel.js` extension fails — renders red `\cancel` or `[Math Processing Error]`) and has no mathtools commands like `\xleftrightarrow`. Substitutes that work: `\underbrace{w_{pq}(n-1)}_{\approx\, 0}` for striking out a term, `\overset{\mathcal{F}}{\longleftrightarrow}` for a labelled arrow
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
- **Fragments**: pauses (`. . .`) must be at **top level** — they break silently inside `:::` divs (render as three literal white dots on the slide). Inside divs, use `{.incremental}` for lists or wrap content in `{.fragment}` divs. Use these built-in mechanisms; no custom CSS animations
- **Syncing fragments across columns**: fragments fire in DOM order, so a fragment in the left column always fires before one in the right. Use explicit `fragment-index` to control order, e.g. `::: {.fragment fragment-index=2}` — works on image attributes too: `![](img.png){.fragment fragment-index=1}`
- **Progressive image swap**: stack images in `::: {.r-stack}` with `.fragment` on all but the first; pair with `fragment-index` on text bullets to swap the image as each bullet appears
- **Closing slide**: use `## Thanks! {background-color="#0d1117" .closing-slide}` with a `::: {.contact}` div. Do NOT nest a `## Thanks!` heading inside a `.closing-slide` div on an empty `##` slide — pandoc splits the inner heading into its own slide, leaving a stray empty slide before it
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
- **Checking the fully-revealed state**: temporarily add `fragments: false` under `revealjs:` in the YAML, render, screenshot every slide (all fragments visible), then **remove the option and re-render**. This is the only reliable way to catch overflow that only appears after the last fragment click. Verify restoration with `grep -c 'class="fragment"' _site/<talk>/index.html` (should be > 0)
- Hidden fragments still occupy layout space (reveal.js uses `visibility: hidden`), so vertical positions in a pre-fragment screenshot match the final layout — only the text is invisible
- Inspect `/tmp/slide.png` with your image viewer or file viewing tool to see the rendered result

### 4. Fix overflow

Common causes of content falling off the bottom of the slide:

| Problem | Fix |
|---|---|
| Too much text / too many equations | Add `{.smaller}` to the `## Heading` |
| Two independent blocks of content | Two-column layout with `:::: {.columns}` |
| Slide genuinely has too much content | Split into two slides |
| Long callout at the bottom | Shorten, or move to a column, or its own slide |
| Mermaid diagram pushes content off the slide | Set `%%| fig-height:` on the cell — without it the SVG container reserves a huge vertical block even for a short diagram |
| Tall image in a column | Constrain with `{height="500"}` instead of `width="100%"` |

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
- **Always set `%%| fig-height:` too** — without it the SVG container reserves far more vertical space than the diagram needs and pushes following content off the slide (e.g. a 4-node `flowchart LR` wants `fig-width: 9`, `fig-height: 1.8`). Too large a `fig-width` overflows horizontally and produces a scrollbar under the diagram
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

There are two distinct products: **transparent clips embedded in talk slides**
and **standalone explainer videos** under `_animations/` (opaque, mp4).

### Workflow: slide clips (transparent webm)

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

### Workflow: standalone explainer videos (`_animations/`)

One directory per video: a `scenes.md` plan (write it with the `manim-composer`
skill BEFORE any code) plus a single standalone script with one `Scene` class.
Only those two files are committed — `media/` and `__pycache__/` are gitignored,
so every video is regenerable from its script.

Scaffold a new episode (creates the directory, a `scenes.md` skeleton, and a
script pre-loaded with the series boilerplate — palette, master clock, caption
helper, title/closing cards):

```bash
python _animations/scaffold_video.py <slug> <SceneClassName> "<Title>" --subtitle "..."
```

- Render opaque (no `-t`): `-ql` (480p15) for the dev loop, `-qh` (1080p60) for
  the final. Output: `media/videos/<script-stem>/<quality>/<SceneName>.mp4`
- The existing series (`two-element-interferometer` → `what-is-a-visibility` →
  `aperture-synthesis` → `uvw-and-lmn`) shares conventions new episodes should
  follow: dark-academic palette (bg `#0d1117`, blue `#58a6ff` antenna p, amber
  `#d29922` antenna q / sky brightness, green `#3fb950` measurements/results,
  red `#f85149` mismatch), `Text` captions at the top edge (font 27), a title
  card, and a closing card with a "next: ..." tease into the following episode
- **Master-clock architecture** for physics animations: one `ValueTracker`
  clock advanced by a dt-updater scaled by a `rate` tracker; every moving
  element is an `always_redraw` reading the same trackers. Consistency (wave
  crests vs trace phases, uv coverage vs reconstructed image) then holds by
  construction instead of choreography
- Prefer computing real data in updaters over staging effects — e.g. the
  aperture-synthesis reconstruction is a genuine masked-FFT inverse
  (`ImageMobject` from a uint8 numpy array inside `always_redraw`)

### Verifying renders (the dev loop)

Two helper scripts in `_animations/` wrap the repeatable parts — prefer them
over hand-rolled manim/ffmpeg invocations:

```bash
# dev render + frame sheet: renders -ql, extracts 10 evenly spaced frames
# (or the timestamps you pass), prints their paths — Read them, fix, repeat
_animations/preview.sh <script.py> <SceneName>
_animations/preview.sh --no-render <script.py> <SceneName> 35 60   # reuse last render

# final render: clears stale partials first, renders -qh with a real exit
# code, ffprobe-checks duration against the dev render (warns on >5s drift)
_animations/final.sh <script.py> <SceneName>      # background this for 3D/long scenes
```

Check every scene's key beat at `-ql` before the final run. Knowledge baked
into the scripts (still true when running manim by hand):

- Piping manim (e.g. `| tail`) masks its exit code — run it bare
- A killed render leaves a truncated segment in `partial_movie_files/` that
  poisons later runs (silently short mp4 or `InvalidDataError`;
  `--flush_cache` does NOT fix it) — delete that quality's
  `partial_movie_files/` before a final render
- Always ffprobe the final duration; frame-rate rounding gives ~1s drift
  between 15fps and 60fps renders of the same scene, a broken stitch loses
  tens of seconds

### ManimCE gotchas (hit in this repo)

- `always_redraw` mobjects only render after an explicit `self.add(...)` —
  easy to construct one and forget to add it (invisible, no error)
- Rate functions are namespaced: `rate_func=rate_functions.ease_in_out_sine`
- `.set_opacity()` on a plotted curve also sets fill opacity, visually closing
  the path — use `.set_stroke(opacity=...)` on line-like mobjects
- Mixing `ImageMobject` with vector mobjects needs `Group`, not `VGroup`
- Swap a caption out *before* animating to the state it doesn't describe —
  a lingering caption over a sweep reads as wrong physics
- `ThreeDScene` (see `_animations/uvw-and-lmn/`):
  - Fixed captions: `self.add_fixed_in_frame_mobjects(c)` then `self.remove(c)`
    then animate `FadeIn(c)` normally; 3D labels that should face the camera go
    through `add_fixed_orientation_mobjects` the same way
  - "Look along an axis" shots suffer perspective parallax (a point and its
    projection along the view axis don't coincide on screen) — pass a large
    `focal_distance` (e.g. 60) to `move_camera` for that shot, restore after
  - Depth sorting draws a translucent `Surface`'s fill over floor-level
    VMobjects, dimming them badly — brighten the floor mobject and re-`add` it
  - Camera angles: `theta` is the camera's azimuth; to look down direction
    `(sin φ, 0, cos φ)` use `phi=φ, theta=0` — and verify the alignment with a
    screenshot rather than trusting the convention

## Boundaries

- **Every deck needs a `custom.css`** — `css: custom.css` is hoisted into both class `_metadata.yml` files, so a deck without that file fails to render. The scaffold script creates it; hand-made directories need it too
- **Nothing in front matter is enforced** — a deck with only a `title:` must render and the site must build. Never add schema checks or validation
- **Ask first** before cross-cutting structural changes: editing the shared theme (`templates/dark-academic.scss`), adding new shared CSS/SCSS files, or repository-wide refactors
- **Never** run destructive commands (`rm -rf`, history rewrites) without explicit approval
