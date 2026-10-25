---
type: Convention
title: Slide patterns
description: Layout, fragments, images, notes, closing slide: how to express common slide needs in native Quarto.
tags: [authoring, fragments, layout]
timestamp: 2026-10-25
---

# Slide patterns

Prioritize semantic structure and clean Markdown over pixel-perfect mimicry of the source deck.

- **No inline HTML for layout** — no `<style>` tags, flexbox hacks, or JS positioning. Use fenced divs:
  ```markdown
  :::: {.columns}
  ::: {.column width="50%"}
  Left
  :::
  ::: {.column width="50%"}
  Right
  :::
  ::::
  ```
  Documented exceptions: a raw `<video>` for muted autoplay ([embedding video](../techniques/embedding-video.md)),
  `{ojs}` cells ([interactive figures](../techniques/interactive-figures-ojs.md)), and the manim-slides
  click cue ([manim-slides stepping](../techniques/manim-slides-stepping.md))
- **Full-slide graphics**: `## Slide Title {background-image="images/asset.png"}`
- **Clickable screenshots**: `![alt](images/screenshot.png){fig-link="https://url.com"}`. A
  standalone image (the only content on a slide) loses its link — use `[![alt](img.png)](url)`
- **Executable code**: when demonstrating software, prefer Python blocks with `#| echo: true`,
  `#| eval: false` over static text
- **Fragments**: `. . .` pauses work only at **top level** — inside `:::` divs they render as three
  literal dots. Inside divs use `{.incremental}` lists or `{.fragment}` divs. Use these built-in
  mechanisms; no custom CSS animations
- **Syncing fragments across columns**: fragments fire in DOM order, so the left column always goes
  first. Set `fragment-index` explicitly, e.g. `::: {.fragment fragment-index=2}` — works on images
  too: `![](img.png){.fragment fragment-index=1}`
- **Progressive image swap**: stack images in `::: {.r-stack}` with `.fragment` on all but the
  first; pair with `fragment-index` on bullets to swap the image as each bullet appears. For
  annotations building up on one image, see [build-up figures](../techniques/build-up-figures.md)
- **Words for the presenter go in notes**: "one click per idea", "another animation", reminders —
  never on a slide. Put them in `::: {.notes}` (presenter view, `S`)
- **No `$…$` math in slide titles** — the menu, the site listing, the overflow report and the
  talk-video frame list all show a title's raw text, so `## Calibrating $\sigma$` reads as
  "Calibrating σσ\sigma". Use Unicode (`## Calibrating σ`, `R²`, `β`) or Markdown emphasis
  (`## *A*(*t*) is not just…`) instead
- **Dense slides**: `{.smaller}` on the heading. Never a wrapping `{style="font-size:…"}` div — it
  breaks `. . .` pauses
- **Closing slide**: `## Thanks! {background-color="#0d1117" .closing-slide}` with a `::: {.contact}`
  div. Do NOT nest a `## Thanks!` heading inside a `.closing-slide` div on an empty `##` slide —
  pandoc splits it into its own slide, leaving a stray empty one before it
- **Video**: see [embedding video](../techniques/embedding-video.md); explainer animations the
  presenter talks over: [manim-slides stepping](../techniques/manim-slides-stepping.md)
