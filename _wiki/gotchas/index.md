---
type: Index
title: Gotchas
description: Traps already hit in this repo, by symptom, with the page that holds the fix.
tags: [index, gotcha]
timestamp: 2026-10-26
---

# Gotchas — by symptom

| Symptom | Fix lives in |
|---|---|
| `. . .` renders as three literal dots | [slide-patterns](../conventions/slide-patterns.md) — only works at top level |
| Left column's fragment always fires first | [slide-patterns](../conventions/slide-patterns.md) — `fragment-index` |
| Title shows garbled TeX in the menu or reports (`σσ\sigma`, `A(t)A(t)A(t)`) | [slide-patterns](../conventions/slide-patterns.md) — no `$…$` in titles |
| A stray empty slide before "Thanks!" | [slide-patterns](../conventions/slide-patterns.md) — closing slide |
| Clickable image loses its link | [slide-patterns](../conventions/slide-patterns.md) — `[![alt](img)](url)` |
| Deck silently missing from the site | [front-matter](../conventions/front-matter.md) — `_`-prefixed directory |
| `\cancel` red / `[Math Processing Error]`, `\xleftrightarrow` missing | [math](../conventions/math.md) |
| Macros ignored | [math](../conventions/math.md) — MathJax 2 `TeX: { Macros: }` |
| Mermaid pushes content off the slide / scrollbar / parse error | [mermaid](../conventions/mermaid.md) |
| Raw `<video>` file missing from `_site/` | [embedding-video](../techniques/embedding-video.md) — `<source>` child |
| Literal `:::` on a slide, following slides swallowed | [embedding-video](../techniques/embedding-video.md) — `{=html}` block |
| OJS deck hangs when opened as a file / headless | [interactive-figures-ojs](../techniques/interactive-figures-ojs.md) — HTTP only |
| Copy buttons on every OJS cell | [interactive-figures-ojs](../techniques/interactive-figures-ojs.md) — `code-copy: false` |
| check_slides: "measured 0px" | [check-slides](../tools/check-slides.md) |
| Transparent webm has no alpha | [manim-slide-clips](../techniques/manim-slide-clips.md) — two-step render, `-auto-alt-ref 0` |
| Short mp4 / `InvalidDataError` after a killed render | [manim](manim.md) |
| `always_redraw` mobject invisible, `Group` vs `VGroup`, curve looks closed | [manim](manim.md) |
| A stepped manim segment holds on a frame with no caption | [manim](manim.md) — pause before the section-ending fade |
| Published deck has blank/black video slides, or the publish workflow fails with "missing …/videos/…" | [publish](../tools/publish.md) — run `scripts/publish-videos.sh` before pushing |
| `.gitignore` pattern doesn't match a `/data` symlink | [large-data](../infrastructure/large-data.md) — no trailing slash |
