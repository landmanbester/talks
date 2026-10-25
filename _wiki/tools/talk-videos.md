---
type: Tool
title: Talk videos (deck + narration → MP4)
description: Pointer to the quarto-talk-video skill and its build directory.
tags: [video, narration]
timestamp: 2026-10-25
---

# Talk videos

A deck plus per-slide narration becomes a conference-compliant MP4 via the
`quarto-talk-video` skill (`.agents/skills/quarto-talk-video/SKILL.md`). **Read it before touching
ffmpeg** — its scripts encode the compliance checks (duration limits, codec, submission filename)
and hard-fail on the silent failure modes. Audio is recorded per slide, so a fluffed line costs one
re-read, not the whole take. Build dir is `_video/<talk-slug>/` (`spec.json` + `script/` tracked,
rest gitignored). Captions are built from the narration script; whisper (not installed) is only
needed if the delivery departed from it.

Raw takes are irreplaceable — after a recording session, see [large data](../infrastructure/large-data.md).
