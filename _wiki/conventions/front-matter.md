---
type: Convention
title: Front matter, scaffolding and deck layout
description: Class split, hoisted front matter, scaffold script, naming, deck-local CSS.
tags: [authoring, front-matter]
timestamp: 2026-10-25
---

# Front matter, scaffolding and deck layout

Talks are split into two classes. **The class a deck lives in decides its formatting and which
rules apply** — each class directory carries its own `AGENTS.md`, loaded automatically when working
in that subtree. Read it before authoring.

- **`lectures/`** — teaching material, revised and re-given. Undated (`date: today`).
- **`contributions/`** — conference and workshop talks, each given once. Hard-coded event date.

Front matter shared by a class — theme, revealjs options, title background, logos — is hoisted into
`<class>/_metadata.yml`. A deck's own front matter carries only what is specific to it; the class
`AGENTS.md` lists what that is. Relative paths in `_metadata.yml` resolve from the *document*
(hence `../../templates/…`); `/`-prefixed paths resolve from the project root and Quarto rewrites
them per deck.

**Nothing in front matter is enforced** — a deck with only a `title:` must render and the site must
build. Never add schema checks or validation.

## Scaffold a deck

The class argument is required:

```bash
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py lecture "Interferometry Basics"
python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py contribution "KAT-7 Transient Search"
```

## Deck directory

```
<class>/<talk-slug>/
├── index.qmd        # The presentation (always index.qmd)
├── images/          # Figures for this talk
├── videos/          # Embedded clips (manim webm, footage, manim-slides segments)
├── custom.css       # Optional deck-local CSS — declare it (see below)
├── make_figures.py  # Optional: generates images/ (see techniques/build-up-figures.md)
└── slides.py        # Optional: manim-slides wrappers (see techniques/manim-slides-stepping.md)
```

- **Directory naming** — descriptive slugs without dates (`stimela-fundamentals/`)
- **Never prefix a talk directory with `_`** — Quarto's site render skips it; the deck silently
  will not render (the same underscore keeps `_animations/`, `_video/` and `_wiki/` out)
- **No footer** — omit `footer:`; it takes up too much space on dense slides
- **Deck-local CSS** — put it in `custom.css` beside `index.qmd` and declare it in the deck's own
  front matter (`format: revealjs: css: custom.css`). Nothing is hoisted, so a deck without
  extra styling needs no file. Classes several decks want belong in the theme — ask first
  (see [theme classes](theme-classes.md))
