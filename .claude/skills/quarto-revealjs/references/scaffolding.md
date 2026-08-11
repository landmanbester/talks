# Scaffolding a New Talk

## Quick Start (Single Talk)

For a standalone presentation, create this minimal structure:

```
my-talk/
├── index.qmd
├── images/
└── custom.scss      # optional, for theme overrides
```

The `.qmd` file is self-contained — all configuration goes in its YAML front matter.

## Multi-Talk Collection

For a collection of talks sharing a theme and branding (e.g., all SARAO/AI4RI talks):

```
talks/
├── _quarto.yml              # Shared project config
├── templates/
│   ├── dark-academic.scss   # Shared theme
│   └── macros.html          # Shared LaTeX macros
├── assets/
│   ├── logos/
│   │   ├── sarao-nrf.png
│   │   └── aims.png
│   └── images/              # Shared images
├── covariance-toeplitz/
│   ├── index.qmd
│   └── images/
├── learned-denoisers/
│   ├── index.qmd
│   └── images/
└── ...
```

### Shared `_quarto.yml`

```yaml
project:
  type: default

format:
  revealjs:
    theme: [dark, templates/dark-academic.scss]
    slide-number: true
    code-line-numbers: false
    code-copy: true
    highlight-style: monokai
    logo: assets/logos/sarao-nrf.png
    width: 1920
    height: 1080
    center: true
    transition: slide
    include-in-header: templates/macros.html
```

Individual talks inherit these defaults and override as needed in their own front matter.

### Shared LaTeX macros (`templates/macros.html`)

```html
<script>
MathJax = {
  TeX: {
    Macros: {
      bm: ["{\\boldsymbol{#1}}", 1],
      R: "{\\mathbb{R}}",
      C: "{\\mathbb{C}}",
      E: "{\\mathbb{E}}",
      Fourier: "{\\mathcal{F}}",
      Prob: "{\\mathbb{P}}",
      Normal: ["{\\mathcal{N}\\left(#1, #2\\right)}", 2],
      diag: "{\\operatorname{diag}}",
      tr: "{\\operatorname{tr}}",
      argmin: "{\\operatorname{arg\\,min}}",
      argmax: "{\\operatorname{arg\\,max}}"
    }
  }
};
</script>
```

## Using the Scaffold Script

Talks belong to one of two classes, and the class is a **required** first
argument. It decides where the directory lands and which rules apply:

```bash
python scaffold_talk.py lecture "Interferometry Basics" --institute "NASSP"
# → lectures/interferometry-basics/

python scaffold_talk.py contribution "KAT-7 Transient Search"
# → contributions/kat-7-transient-search/
```

| Class | Directory | Dates |
|---|---|---|
| `lecture` | `lectures/<slug>/` | inherits `date: today`; never hard-coded |
| `contribution` | `contributions/<slug>/` | stub `date:` for the event date, plus `event:` and `location:` |

This creates:
- `index.qmd` with **thin** front matter — theme, revealjs options, title
  background, logos, and `css:` all come from the class `_metadata.yml`, so the
  deck carries only what is specific to it
- `images/` directory
- `custom.css` with the code block scrollbar fix — **required**, since `css:`
  is hoisted and a deck without this file fails to render

`--institute` is the course or host institution for a lecture, and your own
affiliation for a contribution (where the venue is `event:` instead).

None of the generated fields are enforced. A deck with only a `title:` renders
and inherits the full class theme; the contribution stubs are prompts, not
requirements.

Do not prefix a talk directory with `_` — Quarto skips underscore-prefixed
directories and the deck will silently not render.

### What the scaffold generates

The generated `index.qmd` includes:

```yaml
---
title: "Talk Title"
author: "Author Name"
date: today
institute: "AI4RI"
format:
  revealjs:
    theme: [dark, ../templates/dark-academic.scss]
    slide-number: true
    code-line-numbers: false
    code-copy: true
    highlight-style: monokai
    center: true
    transition: slide
    mermaid-format: svg
    css: custom.css
    title-slide-attributes:
      data-background-image: images/meerkat-milkyway.jpg
      data-background-opacity: "0.5"
---

## Introduction

Content here.

---

## Thanks! {background-color="#0d1117" .closing-slide}

::: {.contact}
author@email.com
:::
```

Put the slide attributes on the `## Thanks!` heading itself. Do NOT use an empty `## {background-color=...}` slide with a `## Thanks!` heading nested inside a `.closing-slide` div — pandoc splits the inner heading into its own slide, leaving a stray empty slide before it.

### Title slide background

Copy the standard background image into each talk's `images/` directory:

```bash
cp ../assets/logos/meerkat-milkyway.jpg images/
```

The scaffold creates `custom.css` automatically. It overrides a cosmetic Quarto bug where `.reveal div.sourceCode { overflow: auto; }` adds a horizontal scrollbar to code blocks even when code fits. The fix must be in a separately-loaded CSS file (not `include-in-header`), because Quarto's injected stylesheet applies after `<head>` content.

### No footer by default

Footers take up too much space on dense slides. Omit `footer:` unless the event requires it (can be added per-talk in the YAML front matter).

## Git Setup

Add to `.gitignore`:
```
# Rendered outputs
*_files/
*.html
!templates/*.html

# Quarto cache
.quarto/
_freeze/

# OS files
.DS_Store
```

## Rendering a Specific Talk

```bash
# From the talk directory
cd talks/covariance-toeplitz
quarto render index.qmd

# Or from the project root
quarto render talks/covariance-toeplitz/index.qmd
```
