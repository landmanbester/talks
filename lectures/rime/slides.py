"""manim-slides versions of the RIME lecture's explainers, for stepping on the clicker.

The scenes live in _animations/ and are imported unchanged apart from
`standalone = False`, which drops their title and closing cards. Every
caption marks a narrative beat, so the only change is a pause before each new
caption. While a wave is flowing (WhatCanHappenToAWiggle, JourneyOfAWave), the pause is a loop of
whole wave periods that holds until the next click; the other scenes are
static between beats and simply hold their last frame.

Render (from this directory), then lay the segments out as slides:
    ~/software/manim/.venv/bin/manim-slides render -qm slides.py \
        RimeDiagramSlides WiggleSlides JourneySlides OneNumberToABoxSlides \
        TransferSlides RimeTartSlides
    python3 ../../scripts/manim_slides_qmd.py RimeDiagramSlides rime-diagram
    python3 ../../scripts/manim_slides_qmd.py WiggleSlides wiggle
    python3 ../../scripts/manim_slides_qmd.py JourneySlides journey
    python3 ../../scripts/manim_slides_qmd.py OneNumberToABoxSlides one-number-to-a-box
    python3 ../../scripts/manim_slides_qmd.py TransferSlides transfer
    python3 ../../scripts/manim_slides_qmd.py RimeTartSlides rime-tart
"""

import sys
from pathlib import Path

ANIM = Path(__file__).resolve().parents[2] / "_animations"
sys.path[:0] = [str(ANIM / "rime-interferometer"),
                str(ANIM / "polarisation-ellipse"),
                str(ANIM / "journey-of-a-wave"),
                str(ANIM / "calibrator-transfer")]

from manim_slides import Slide  # noqa: E402

import journey  # noqa: E402
import polarisation_ellipse  # noqa: E402
import rime_interferometer  # noqa: E402
import transfer  # noqa: E402


class Beats:
    """Pause before every caption; loop the hold while a wave flows.

    `hold` is a whole number of wave periods, so a loop cycles seamlessly.
    Scenes without a wave clock (no `rate`) just hold their last frame.
    The segment before a loop has to run straight into it; manim_slides_qmd.py
    sets that when laying out the slides.
    """

    standalone = False
    hold = 0.0

    def caption(self, text, *args, **kwargs):
        self.beat()
        return super().caption(text, *args, **kwargs)

    def beat(self):
        if not getattr(self, "_started", False):
            # the first caption opens the scene: nothing to pause on yet
            self._started = True
            return
        rate = getattr(self, "rate", None)
        if rate is None or rate.get_value() == 0:
            self.next_slide()
        else:
            self.next_slide(loop=True)
            self.wait(self.hold)
            self.next_slide()


class RimeDiagramSlides(Beats, Slide, rime_interferometer.RimeOnTheInterferometer):
    pass


class RimeTartSlides(Beats, Slide, rime_interferometer.RimeForTart):
    pass


class WiggleSlides(Beats, Slide, polarisation_ellipse.WhatCanHappenToAWiggle):
    hold = polarisation_ellipse.HOLD   # 3 wave periods = 6 s


class JourneySlides(Beats, Slide, journey.JourneyOfAWave):
    hold = journey.HOLD   # 3 wave periods = 6 s


class OneNumberToABoxSlides(Beats, Slide, rime_interferometer.OneNumberToABox):
    pass


class TransferSlides(Beats, Slide, transfer.CalibratorTransfer):
    pass
