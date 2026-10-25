---
name: quarto-revealjs
description: "Use this skill whenever creating, editing, building, or porting a presentation using Quarto revealjs. This includes: creating slide decks with LaTeX math, code snippets, diagrams, or technical content; porting presentations from Canva, PowerPoint, Google Slides, or PDF to Quarto; scaffolding a new talk project; rendering to HTML or PDF; customizing themes with SCSS; or working with .qmd files for presentations. Trigger whenever the user mentions 'Quarto', 'revealjs', 'qmd slides', 'technical presentation', 'lecture slides', or asks to create a presentation that involves code and/or math. Also trigger when converting or porting an existing presentation to a markdown-based format."
---

# Quarto Revealjs Presentation Skill

Create polished, technical presentations using Quarto's revealjs format. Optimized for talks that mix LaTeX math, syntax-highlighted code, diagrams, and progressive reveal — the kind of presentations common in scientific computing, signal processing, and machine learning.

## Quick Reference

| Task | Action |
|------|--------|
| Scaffold a new talk | Read [references/scaffolding.md](references/scaffolding.md), run the scaffold script |
| Create/edit slides | Follow the patterns below, consult [references/revealjs-options.md](references/revealjs-options.md) |
| Port from Canva/PDF | Read [references/porting-guide.md](references/porting-guide.md) |
| Build-up figure, interactive (OJS) figure, or manim animation stepped on the clicker | Repo `AGENTS.md`: "Build-up figures", "Interactive figures", "Stepping an animation on the clicker" |
| Customize theme | Edit the SCSS file — see [templates/](templates/) |
| Render to HTML | `quarto render index.qmd` |
| Export to PDF | Read [references/pdf-export.md](references/pdf-export.md) |
| General Quarto authoring | Cross-references, citations, tables, figures, callouts, shortcodes, layout, extensions, YAML config |

---

## Core Workflow

### 1. Project Setup

In this repo every talk is `lectures/<slug>/index.qmd` or
`contributions/<slug>/index.qmd`, with an `images/` directory beside it. Create
one with the scaffold script (see references/scaffolding.md). Shared front
matter comes from the class `_metadata.yml`, so a deck's YAML stays thin.

### 2. Writing Slides

Slides are plain markdown in a `.qmd` file with YAML front matter. The minimal structure:

```yaml
---
title: "Talk Title"
author: "Author Name"
date: "2025-03-11"
format:
  revealjs:
    theme: dark
    slide-number: true
    code-line-numbers: false
---

## First Slide Title

Content here.

---

## Second Slide Title

More content.
```

**Slide boundaries**: Use `## Heading` for titled slides or `---` for untitled slides. A `# Heading` creates a section title slide.

### 3. Key Content Patterns

Read [references/common-patterns.md](references/common-patterns.md) for the full catalog. The essentials:

**LaTeX math** — works natively, no plugins:
```markdown
Inline: $T_{i,j} = T_{i-1,j-1}$

Display:
$$P(s) = \int K(r) \exp(-2\pi \imath s \cdot r) \, dr$$
```

**Code blocks** — syntax highlighted by default:
````markdown
```python
import jax.numpy as jnp
from jax import vmap

def toeplitz_matvec(c, x):
    N = len(x)
    c_embed = jnp.concatenate([c, jnp.zeros(1), jnp.flip(c[1:])])
    return jnp.fft.irfft(jnp.fft.rfft(c_embed) * jnp.fft.rfft(x, 2*N-1))[:N]
```
````

**Executable code** (requires Jupyter kernel):
````markdown
```{python}
#| echo: true
#| output-location: fragment
import numpy as np
print(f"FFT of delta: {np.fft.fft([1,0,0,0])}")
```
````

**Progressive reveal** (content appears on click):
```markdown
## Slide Title

First point visible immediately.

. . .

This appears on first click.

. . .

This appears on second click.
```

**Incremental lists**:
```markdown
::: {.incremental}
- First item
- Second item
- Third item
:::
```

**Fragments with custom animations**:
```markdown
::: {.fragment .fade-in}
Content fades in on click.
:::

::: {.fragment .highlight-red}
This text turns red on click.
:::
```

**Two-column layout**:
```markdown
:::: {.columns}
::: {.column width="50%"}
Left column content

$$C = \sum_{k=0}^{N-1} c_k P^k$$
:::

::: {.column width="50%"}
Right column content

$$\boldsymbol{c} = [c_0, \cdots, c_{N-1}]$$
:::
::::
```

**Speaker notes** (visible in presenter view, press `S`):
```markdown
::: {.notes}
Remember to explain the connection between
circulant embedding and the FFT here.
:::
```

**Images with captions and sizing**:
```markdown
![Roots of unity on the complex plane](images/roots-of-unity.png){width=60% fig-align="center"}
```

**Embedded videos**:
```markdown
{{< video https://www.youtube.com/watch?v=spUNpyF58BY width="80%" >}}
```

**Callout boxes** (for exercises, warnings, notes):
```markdown
::: {.callout-note}
## Exercise
Show that the eigenvalues of a circulant matrix are given by the
Fourier transform of its first row or column.
:::
```

### 4. Rendering

```bash
# Render to HTML (default)
quarto render index.qmd

# Render and preview with live reload
quarto preview index.qmd

# Render to PDF (requires chromium or tinytex)
quarto render index.qmd --to pdf
```

### 5. The SCSS Theme

The skill includes a dark theme template at `templates/dark-academic.scss`. To use it, either copy it into the talk directory or reference it via relative path:

```yaml
format:
  revealjs:
    theme: [dark, path/to/dark-academic.scss]
```

The theme provides:
- Dark background with high-contrast text (good for projectors)
- Styled math blocks with subtle background
- Code blocks with distinct background and border
- Colored callout boxes for exercises and notes
- `.highlight-box`, `.result-box`, `.muted`, `.closing-slide`, `.contact` classes
- Responsive font sizing

See the SCSS file itself for all customizable variables.

---

## Important Rendering Notes

- Quarto must be installed (`quarto --version` to check). If not available in the environment, create the .qmd file and the user can render locally.
- For executable Python code blocks, Jupyter must be installed in the environment.
- LaTeX math rendering uses MathJax (in HTML) or KaTeX — no LaTeX installation needed for HTML output.
- PDF export from revealjs uses a headless browser. Alternative: use `format: beamer` for native LaTeX PDF slides.
- Always test-render with `quarto render` before delivering to catch YAML or math errors.

---

## Key Conventions

- **No footer** — omit `footer:` from YAML; it takes up too much space on dense slides
- **Title background and code-block scrollbar fix** — both inherited (class `_metadata.yml` and the theme); a deck does nothing for either
- **Fragment pauses** — `. . .` only works at **top level**; inside `:::` divs it renders as literal dots. Use `{.incremental}` for lists or `{.fragment}` divs for other content inside columns/divs
- **MathJax macros** — use MathJax 2 syntax: `TeX: { Macros: {} }` (uppercase), not `tex: { macros: {} }`
- **Mermaid diagrams** — use `mermaid-format: svg` in the YAML front matter (under `revealjs:`) to ensure custom theming works (the default `js` format overrides custom themes). Use YAML config blocks inside Mermaid cells (not the older `%%{init:...}%%` syntax) for theming — set `theme: base` with custom `themeVariables` for full control over colors. Use `%%|` cell options for sizing (e.g. `%%| fig-width: 4.5`). Use Unicode emoji prefixes in labels for semantic meaning (e.g. `📦 CABS`, `⚙️ Stimela`). Use `<br />` for line breaks in labels (not `\n`). Do NOT use quotation marks or parentheses inside node labels — they break the Mermaid parser. Use dashed arrows `<-.->` for bidirectional connections. Never use Mermaid's default harsh black lines — always apply a curated palette via `themeVariables`
- **Dense slides** — use `{.smaller}` on the `## Heading` (not a wrapping div) to reduce font without breaking fragments
- **fig-link bug** — `fig-link` is a known Quarto bug for standalone images in revealjs (images that are the only content on a slide). The link gets stripped. Workaround: use markdown linked images `[![alt](img.png)](url)` or ensure there is other text on the slide
- **No inline HTML for layouts** — never use raw HTML `{=html}` blocks, inline style tags, CSS flexbox, or JavaScript for element positioning. Always use Quarto's native constructs (fenced divs, Mermaid blocks). See the project's AGENTS.md for presentation engineering standards, including its documented exceptions (`{=html}` for autoplaying video, `{ojs}` cells, the manim-slides click cue)
- **General Quarto authoring** — for cross-references, citations, tables, figures, callouts, shortcodes, layout, extensions, and YAML config, follow standard Quarto authoring conventions. This skill focuses specifically on revealjs presentation conventions
- **AGENTS.md** — the project has an AGENTS.md file that defines presentation engineering standards. This skill should complement (not contradict) those standards
