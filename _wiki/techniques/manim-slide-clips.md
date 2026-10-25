---
type: Technique
title: Manim slide clips (transparent webm)
description: Render a transparent manim clip for a slide: two-step render because manim's webm loses alpha.
tags: [manim, video]
timestamp: 2026-10-25
---

# Manim slide clips (transparent webm)

Plan with the `manim-composer` skill before writing code; implement with `manimce-best-practices`.
Interpreter: see [Python environment](../infrastructure/python-env.md).

The script lives beside the deck's `index.qmd` (with its `scenes.md` plan if it has one); the clip
goes in the deck's `videos/`. Render in two steps — manim's direct `--format=webm` does not encode
VP9 alpha properly:

```bash
manim -t -qm script.py SceneName          # -t transparent; -qh for the final
ffmpeg -y -i media/videos/script/720p30/SceneName.mov \
  -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 -b:v 2M videos/clip.webm
```

`-auto-alt-ref 0` is required for the alpha channel. Symlink the deck's `media/` to `/data/talks/`
before a long render (see [large data](../infrastructure/large-data.md)). Embedding it:
[embedding video](embedding-video.md). Render pitfalls: [manim gotchas](../gotchas/manim.md).
