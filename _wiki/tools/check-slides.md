---
type: Tool
title: check_slides.py — find overflow
description: Measure every slide's height: CLIPPED vs tight thresholds, how the probe works, 0px slides, fixes by cause.
tags: [verification, overflow, check_slides]
timestamp: 2026-10-25
---

# `scripts/check_slides.py` — find overflow

Measure overflow rather than eyeballing screenshots, and do so before calling a deck done:

```bash
scripts/check_slides.py                    # render, then check every deck
scripts/check_slides.py --no-render deconvolution
scripts/check_slides.py --no-render --shots /data/tmp/shots deconvolution   # + every slide, revealed
```

- **CLIPPED** (exit 1) — taller than ~778px, cut off on screen. Fix it.
- **tight** — over the 700px design height but still visible inside reveal's 10% margin. A
  judgement call; it reads as cramped. `--strict` fails on these too.

Deck sources are never modified — the probe runs on a throwaway copy inside `_site/`, loaded over
a local HTTP server (OJS refuses `file://`). That copy drops background videos and `data-autoslide`
(neither affects layout; dozens of preloaded segments exhaust the time budget, and autoslide would
move the deck under the probe). A slide with no visible content — a manim-slides segment — measures
0px and is accepted; any other 0px slide means the page never laid out, and the run fails.

## Fix overflow

| Cause of overflow | Fix |
|---|---|
| Too much text / too many equations | `{.smaller}` on the heading |
| Two independent blocks of content | `:::: {.columns}` |
| Genuinely too much content | Split the slide (contributions: cut, don't shrink) |
| Long callout at the bottom | Shorten, move to a column, or its own slide |
| Mermaid diagram | Set `%%| fig-height:` ([mermaid](../conventions/mermaid.md)) |
| Tall image in a column | `{height="500"}` instead of `width="100%"` |

Never fix it with a wrapping `{style="font-size:…"}` div — it breaks `. . .` pauses.
