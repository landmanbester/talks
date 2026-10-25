"""manim-slides versions of the two series explainers, for stepping on the clicker.

The scenes themselves live in _animations/ and are imported unchanged: every
caption marks a narrative beat, so the only change is a pause before each new
caption. While the wave is streaming, the pause is a 10 s loop (7 wave periods,
so the wavefronts and traces cycle seamlessly) that holds until the next click.

Render (from this directory), then lay the segments out as slides:
    ~/software/manim/.venv/bin/manim-slides render -qm slides.py \
        TwoElementInterferometerSlides WhatIsAVisibilitySlides
    python3 ../../scripts/manim_slides_qmd.py TwoElementInterferometerSlides two-element
    python3 ../../scripts/manim_slides_qmd.py WhatIsAVisibilitySlides visibility
"""

import sys
from pathlib import Path

ANIM = Path(__file__).resolve().parents[2] / "_animations"
sys.path[:0] = [str(ANIM / "two-element-interferometer"),
                str(ANIM / "what-is-a-visibility")]

from manim_slides import Slide  # noqa: E402

import interferometer  # noqa: E402
import visibility  # noqa: E402

HOLD = 7 * interferometer.LAM / interferometer.C_VIS   # 10 s; same in both


class Beats:
    """Pause before every caption; loop the hold while the wave flows.

    `steady` is the clock time after which every moving part is periodic (the
    leading wavefront has reached both antennas). Before then a loop would jump,
    so a beat that falls mid-arrival is skipped rather than frozen.

    The segment before a loop has to run straight into it; manim-slides can only
    flag that when the segment starts, before we know, so manim_slides_qmd.py
    sets it when laying out the slides.
    """

    steady = 0.0

    def caption(self, text, *args, **kwargs):
        self.beat()
        return super().caption(text, *args, **kwargs)

    def beat(self):
        if self.rate.get_value() == 0:
            self.next_slide()
        elif self.t_now() > self.steady:
            self.next_slide(loop=True)
            self.wait(HOLD)
            self.next_slide()
        # else: wave still arriving, keep playing through to the next beat


class TwoElementInterferometerSlides(Beats, Slide,
                                     interferometer.TwoElementInterferometer):
    # the far antenna is reached at (D0 + B/2) / C_VIS ≈ 9.7 s
    steady = (interferometer.D0 + interferometer.B / 2) / interferometer.C_VIS


class WhatIsAVisibilitySlides(Beats, Slide, visibility.WhatIsAVisibility):
    steady = 0.0   # the clock starts at 20 s: the wave is already streaming
