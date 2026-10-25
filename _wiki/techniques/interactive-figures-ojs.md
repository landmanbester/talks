---
type: Technique
title: Interactive figures (Observable JS)
description: Sliders driving a live plot with Quarto's built-in {ojs} cells; layout, styling, and the file:// trap.
tags: [ojs, interactive, gotcha]
timestamp: 2026-10-25
---

# Interactive figures (Observable JS)

For a figure the audience should *play with* (sliders driving a live plot), use Quarto's built-in
`{ojs}` cells with Observable Plot and Inputs — no extension, no build step. Reference:
`lectures/visibility-space`, "Try It: The Fringe Explorer". It re-implements the physics in a few
lines of JS; it does not embed a manim video (for that, see [manim-slides stepping](manim-slides-stepping.md)).

- `//| echo: false` on every cell, and set `code-copy: false` in the deck's front matter — the
  inherited `code-copy: true` puts a copy button on every OJS cell
- One slider per `.column` in a `:::::{.columns .ojs-controls}` row, with deck CSS hiding the
  number box and putting the label above (`--label-width: auto`); the default inline label wraps
  and the number box is white-on-white on the dark theme
- Plots: `style: {background: "transparent", color: "#c9d1d9"}` and explicit `width`/`height` in
  slide pixels (the slide is 1050 wide); marks in the palette. Check the slide with
  `check_slides.py` — OJS output is measured after it renders
- **OJS only runs over HTTP.** Opened as `file://`, Quarto's OJS bootstrap raises an `alert()`;
  in headless Chrome that modal blocks until timeout. Use `quarto preview` or a server on `_site/`
- Colour legends: classes in `custom.css` (`[gold]{.key-source}`), not inline `style=` spans
