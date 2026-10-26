---
type: Tool
title: Render, preview, publish and screenshot
description: Quarto website render/preview commands, pointer to publishing, PDF export pointer, and headless screenshots of a slide.
tags: [quarto, render, screenshots]
timestamp: 2026-10-25
---

# Render, preview, publish and screenshot

The repo root is a Quarto website project (`_quarto.yml` renders `*/*/index.qmd` into `_site/`;
`index.qmd` is the listing page, one table per class). All output, including single-deck renders,
goes to `_site/<class>/<talk-slug>/` (gitignored).

```bash
cd lectures/<talk-slug> && quarto preview index.qmd   # edit loop; serves /lectures/<talk-slug>/
quarto render                                         # from the root: listing + every deck
```

Publishing is a GitHub Actions workflow on push to `main`, not `quarto publish` — see
[publish](publish.md).

PDF export (decktape, print-to-PDF, self-contained HTML):
`.agents/skills/quarto-revealjs/references/pdf-export.md`. `scripts/shoot-decks.sh` renders and
screenshots every deck's title slide.

## Screenshot a slide

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
- For the fully-revealed state use `scripts/check_slides.py --shots` ([check_slides](check-slides.md)).
  Never hand-edit `fragments: false` into front matter — an interrupted run leaves the deck broken
- Decks with `{ojs}` cells only work over HTTP, never `file://` ([OJS](../techniques/interactive-figures-ojs.md))
