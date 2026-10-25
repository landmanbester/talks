---
type: Technique
title: Embedding video in a slide
description: Shortcode vs raw <video>; the muted-autoplay exception and its two pandoc/Quarto traps.
tags: [video, html, gotcha]
timestamp: 2026-10-25
---

# Embedding video in a slide

Use `{{< video videos/clip.webm >}}`, not a raw `<video>` tag.

**Exception — a clip that must autoplay muted.** Browsers only honour `muted`/`autoplay` reliably
as parse-time attributes, which the shortcode cannot emit. `contributions/kremetart-pipeline` does
this twice: a full-bleed background (`.bg-fill`) and an inline looping manim clip. A raw tag must:

1. **Name the file in a `<source src>` child** — Quarto does not copy a file referenced only by
   `<video src>`, so it is missing from `_site/`
2. **Sit in a ```` ```{=html} ```` block when inside a fenced div** — otherwise pandoc leaves the
   closing `:::` as literal text and the div swallows the following slides

````markdown
::: {.r-stack}
```{=html}
<video width="78%" autoplay loop muted playsinline data-autoplay>
<source src="videos/sphere-painting.webm" type="video/webm">
</video>
```
:::
````

Related: [manim slide clips](manim-slide-clips.md) (making the webm),
[manim-slides stepping](manim-slides-stepping.md) (an explainer stepped on the clicker instead of
one long clip).
