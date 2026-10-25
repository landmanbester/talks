---
type: Infrastructure
title: Python environment
description: uv env for repo tooling; manim and manim-slides from ~/software/manim/.venv until pycairo headers exist.
tags: [python, uv, manim]
timestamp: 2026-10-25
---

# Python environment

`uv sync` builds `.venv/` from `pyproject.toml` with what `scripts/figures/` needs; run tools with
`uv run scripts/figures/make_figures.py …`. `check_slides.py` is stdlib-only;
the talk-video scripts need only numpy (so `uv run` them, or any python3 with numpy).

manim is the opt-in `manim` dependency group (with `manim-slides`), because pycairo needs system
headers this machine does not have yet (`sudo apt install libcairo2-dev libpango1.0-dev && uv sync
--group manim`). Until then manim runs from `~/software/manim/.venv/bin/manim`; `manim-slides` is
installed in the same venv (`~/software/manim/.venv/bin/manim-slides`). The series was rendered on
manim 0.20 — bump deliberately, and re-check a scene.
