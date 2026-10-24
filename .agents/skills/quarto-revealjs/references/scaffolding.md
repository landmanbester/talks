# Scaffolding a New Talk

The repo root's `AGENTS.md` is authoritative for layout and conventions; this
page covers only the scaffold script and what it produces.

## Using the Scaffold Script

Talks belong to one of two classes, and the class is a **required** first
argument. It decides where the directory lands and which rules apply. Run it
from the repo root:

```bash
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py lecture "Interferometry Basics" --institute "NASSP"
# → lectures/interferometry-basics/

python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py contribution "KAT-7 Transient Search"
# → contributions/kat-7-transient-search/
```

| Class | Directory | Dates |
|---|---|---|
| `lecture` | `lectures/<slug>/` | inherits `date: today`; never hard-coded |
| `contribution` | `contributions/<slug>/` | stub `date:` for the event date, plus `event:` and `location:` |

This creates `index.qmd` and an empty `images/`. Nothing else is needed:
theme, revealjs options, title background, and logos all come from the class
`_metadata.yml`.

`--institute` is the course or host institution for a lecture, and your own
affiliation for a contribution (where the venue is `event:` instead).

None of the generated fields are enforced. A deck with only a `title:` renders
and inherits the full class theme; the contribution stubs are prompts, not
requirements.

Do not prefix a talk directory with `_` — Quarto skips underscore-prefixed
directories and the deck will silently not render.

### What the scaffold generates

A lecture's `index.qmd`:

```markdown
---
title: "Interferometry Basics"
institute: "NASSP"
---

## Introduction

<!-- Replace with your opening content -->

---

## Main Content

$$
y = Rx + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \Sigma)
$$

. . .

This appears on click.

---

## Thanks! {background-color="#0d1117" .closing-slide}

::: {.contact}
landman.bester@gmail.com
:::
```

Put the slide attributes on the `## Thanks!` heading itself. Do NOT use an
empty `## {background-color=...}` slide with a `## Thanks!` heading nested
inside a `.closing-slide` div — pandoc splits the inner heading into its own
slide, leaving a stray empty slide before it.

### Adding to the thin front matter

Only what is specific to the deck goes in its own front matter. Common
additions, which merge with the inherited `format: revealjs:` block:

```yaml
format:
  revealjs:
    css: custom.css            # deck-local CSS in a file beside index.qmd
    include-in-header:
      text: |
        <script>
        MathJax = { TeX: { Macros: {
          bm: ["{\\boldsymbol{#1}}", 1],
          Fourier: "{\\mathcal{F}}"
        } } };
        </script>
    title-slide-attributes:    # a different title background
      data-background-image: images/other.jpg
      data-background-opacity: "0.5"
```

Do not add `footer:` — the repo omits footers.

## Rendering a Specific Talk

```bash
cd lectures/interferometry-basics && quarto preview index.qmd
# or, from the root
quarto render lectures/interferometry-basics/index.qmd   # → _site/lectures/interferometry-basics/
```
