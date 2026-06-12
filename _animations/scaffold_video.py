#!/usr/bin/env python3
"""Scaffold a new explainer-video episode under _animations/.

Creates <slug>/scenes.md (plan skeleton — flesh it out with the
manim-composer skill BEFORE writing code) and <slug>/<module>.py with the
series boilerplate: palette, master-clock trackers, caption helper, title
card, and closing card with the "next: ..." tease.

Usage:
    python scaffold_video.py <slug> <SceneClassName> "<Title>" \
        [--subtitle "..."] [--root DIR]

Example:
    python scaffold_video.py deconvolution Deconvolution \
        "Deconvolution" --subtitle "undoing the dirty beam"
"""

import argparse
import re
import sys
from pathlib import Path

SCENES_TEMPLATE = '''# {title}

Episode of the interferometry explainer series (see sibling directories).

## Overview
- **Topic**:
- **Hook**:
- **Target Audience**: same as the rest of the series
- **Estimated Length**: ~2 min
- **Key Insight**:

## Narrative Arc
<!-- 2-3 sentences: the journey from question to insight. Which beat from the
previous episode does this pick up, and what does the closing tease set up? -->

---

## Scene 1: Title (~5 s)
Title card: "{title}" / "{subtitle}".

## Scene 2: ...
**Purpose**:
### Visual Elements
### Content
### Technical Notes

## Scene N: Closing (~15 s)
Closing card + tease for the next episode.

---

## Color Palette (series)
`#0d1117` bg · blue `#58a6ff` · amber `#d29922` (sky/brightness) ·
green `#3fb950` (measurements/results) · red `#f85149` (mismatch) ·
`#c9d1d9` text · `#8b949e` muted.

## Implementation Order
1. Core tracker-driven machinery first; get the central coupling right
   before polish.

## Consistency checklist
<!-- physically-verifiable facts the rendered frames must show -->
-
'''

SCRIPT_TEMPLATE = '''"""{title} — {subtitle}.

Episode of the interferometry explainer series (see scenes.md for the plan).

Render (from this directory):
    ../preview.sh {module}.py {cls}        # dev loop: -ql + frame sheet
    ../final.sh {module}.py {cls}          # final: 1080p60 + duration check
"""

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # antenna p / primary
SIG_Q = "#d29922"   # antenna q / sky brightness
GOOD = "#3fb950"    # measurements / results
BAD = "#f85149"     # mismatch / warnings
FRONT = "#c9d1d9"   # annotations / text
MUTED = "#8b949e"

config.background_color = BG


class {cls}(Scene):
    def construct(self):
        self.setup_trackers()
        self.scene1_title()
        # one method per scenes.md beat goes here
        self.scene_close()

    # ------------------------------------------------------------------
    # one master clock drives every moving element (see AGENTS.md):
    # always_redraw mobjects read the trackers, so physics stays
    # consistent by construction. Remember: always_redraw mobjects are
    # invisible until self.add(...)ed.
    # ------------------------------------------------------------------
    def setup_trackers(self):
        self.clock = ValueTracker(0.0)
        self.rate = ValueTracker(0.0)      # 0 = frozen, 1 = real time
        self.clock.add_updater(
            lambda m, dt: m.increment_value(dt * self.rate.get_value())
        )
        self.add(self.clock)

    def t_now(self):
        return self.clock.get_value()

    def caption(self, text, color=FRONT, **kwargs):
        return Text(text, font_size=27, color=color, **kwargs).to_edge(
            UP, buff=0.25
        )

    # ------------------------------------------------------------------
    # Scene 1: title card
    # ------------------------------------------------------------------
    def scene1_title(self):
        title = Text("{title}", font_size=44, color=FRONT)
        sub = Text("{subtitle}", font_size=28, color=MUTED).next_to(
            title, DOWN, buff=0.3
        )
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

    # ------------------------------------------------------------------
    # Closing card
    # ------------------------------------------------------------------
    def scene_close(self):
        line1 = Text("CLOSING LINE 1 —", font_size=40, color=FRONT)
        line2 = Text("closing line 2.", font_size=40, color=FRONT)
        msg = VGroup(line1, line2).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        tease = Text("next: TEASE FOR THE FOLLOWING EPISODE",
                     font_size=26, color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.0)
        self.play(FadeIn(tease), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(tease), run_time=1.0)
        self.wait(0.5)
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug", help="directory name, e.g. deconvolution")
    ap.add_argument("cls", help="Scene class name, e.g. Deconvolution")
    ap.add_argument("title", help="video title for the title card")
    ap.add_argument("--subtitle", default="SUBTITLE TBD")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent),
                    help="parent directory (default: _animations/)")
    args = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.slug):
        sys.exit(f"slug must be a lowercase hyphenated name: {args.slug!r}")
    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", args.cls):
        sys.exit(f"class name must be CamelCase: {args.cls!r}")

    target = Path(args.root) / args.slug
    if target.exists():
        sys.exit(f"refusing to overwrite existing {target}")
    module = args.slug.replace("-", "_")

    target.mkdir(parents=True)
    (target / "scenes.md").write_text(SCENES_TEMPLATE.format(
        title=args.title, subtitle=args.subtitle))
    (target / f"{module}.py").write_text(SCRIPT_TEMPLATE.format(
        title=args.title, subtitle=args.subtitle, module=module,
        cls=args.cls))

    print(f"created {target}/")
    print(f"  scenes.md          <- plan here first (manim-composer skill)")
    print(f"  {module}.py        <- scene class {args.cls}")
    print(f"render: cd {target} && ../preview.sh {module}.py {args.cls}")


if __name__ == "__main__":
    main()
