"""Calibrator Transfer — solving for the gains, and what it costs.

Episode of the interferometry explainer series (see scenes.md for the plan).

Render (from this directory):
    ../preview.sh transfer.py CalibratorTransfer   # dev loop: -ql + frame sheet
    ../final.sh transfer.py CalibratorTransfer     # final: 1080p60 + duration check
"""

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # instrument: the gain
SIG_Q = "#d29922"   # sky: target scans
GOOD = "#3fb950"    # measurements: calibrator solutions
BAD = "#f85149"     # calibration error
FRONT = "#c9d1d9"   # annotations / text
MUTED = "#8b949e"

config.background_color = BG

T_END = 12.0          # hours
SCAN = 0.3            # calibrator scan length (h)
TS = np.linspace(0, T_END, 240)
RNG = np.random.default_rng(7)
NOISE = RNG.standard_normal(64)   # one fixed draw per calibrator visit


def gain(t):
    """Gain phase (deg) towards the target: slow drift plus faster wiggles."""
    t = np.asarray(t)
    return (32 * np.sin(2 * PI * t / 9 + 0.5) + 14 * np.sin(2 * PI * t / 3.1 + 1)
            + 7 * np.sin(2 * PI * t / 1.3 + 2))


def offset(t):
    """How the gain towards a distant calibrator differs (another sky path)."""
    t = np.asarray(t)
    return 22 * np.sin(2 * PI * t / 4.3 + 2.2) + 9 * np.sin(2 * PI * t / 1.7)


class CalibratorTransfer(Scene):
    standalone = True   # title / closing cards (the deck wrapper turns them off)

    def construct(self):
        self.cap = None
        self.sigma = ValueTracker(4.0)      # solution noise (deg): faint calibrator
        self.cadence = ValueTracker(1.5)    # hours between calibrator visits
        self.sep = ValueTracker(0.0)        # 0 = calibrator next to target
        if self.standalone:
            self.scene_title()
        self.beat_drift()
        self.beat_calibrator()
        self.beat_solve()
        self.beat_transfer()
        self.beat_error()
        self.beat_faint()
        self.beat_cadence()
        self.beat_distance()
        self.beat_wrap()
        if self.standalone:
            self.scene_close()
        else:
            self.wait(0.5)

    # ------------------------------------------------------------------
    def caption(self, text, color=FRONT, **kwargs):
        return Text(text, font_size=27, color=color, **kwargs).to_edge(
            UP, buff=0.25
        )

    def show_caption(self, text, **kwargs):
        cap = self.caption(text, **kwargs)
        if self.cap is not None:
            self.play(FadeOut(self.cap), run_time=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        self.cap = cap

    def scene_title(self):
        title = Text("Calibrator Transfer", font_size=44, color=FRONT)
        sub = Text("solving for the gains, and what it costs", font_size=28,
                   color=MUTED).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

    # -- model ------------------------------------------------------------
    def scans(self):
        """Start times of the calibrator scans."""
        cad = self.cadence.get_value()
        n = int(np.floor((T_END - SCAN) / cad + 1e-9)) + 1
        starts = np.arange(n) * cad
        # always finish on a calibrator, as a real schedule would
        if T_END - SCAN - starts[-1] > 0.5 * cad:
            starts = np.append(starts, T_END - SCAN)
        return starts

    def solutions(self):
        tc = self.scans() + SCAN / 2
        cal = gain(tc) + self.sep.get_value() * offset(tc)
        sol = cal + self.sigma.get_value() * NOISE[:len(tc)]
        return tc, sol

    def interp(self, ts):
        tc, sol = self.solutions()
        return np.interp(ts, tc, sol)

    def rms_error(self):
        starts = self.scans()
        on_target = np.ones_like(TS, dtype=bool)
        for s in starts:
            on_target &= ~((TS >= s) & (TS <= s + SCAN))
        d = (gain(TS) - self.interp(TS))[on_target]
        return float(np.sqrt(np.mean(d ** 2)))

    # -- drawing ----------------------------------------------------------
    def curve(self, ys, color, width=3, opacity=1.0):
        pts = [self.ax.c2p(t, y) for t, y in zip(TS, ys)]
        return VMobject().set_points_as_corners(pts).set_stroke(
            color, width, opacity=opacity)

    def make_bands(self):
        def bands():
            g = VGroup()
            starts = self.scans()
            y0, y1 = -90, 90
            edges = [0.0]
            for s in starts:
                g.add(Polygon(self.ax.c2p(s, y0), self.ax.c2p(s + SCAN, y0),
                              self.ax.c2p(s + SCAN, y1), self.ax.c2p(s, y1),
                              stroke_width=0, fill_color=GOOD, fill_opacity=0.22))
            for a, b in zip(starts[:-1] + SCAN, starts[1:]):
                g.add(Polygon(self.ax.c2p(a, y0), self.ax.c2p(b, y0),
                              self.ax.c2p(b, y1), self.ax.c2p(a, y1),
                              stroke_width=0, fill_color=SIG_Q, fill_opacity=0.07))
            return g
        return always_redraw(bands)

    def make_points(self):
        def pts():
            tc, sol = self.solutions()
            s = self.sigma.get_value()
            g = VGroup()
            for t, y in zip(tc, sol):
                g.add(Line(self.ax.c2p(t, y - s), self.ax.c2p(t, y + s),
                           color=GOOD, stroke_width=3))
                g.add(Dot(self.ax.c2p(t, y), radius=0.07, color=GOOD))
            return g
        return always_redraw(pts)

    def make_interp(self):
        def line():
            tc, sol = self.solutions()
            pts = [self.ax.c2p(t, y) for t, y in zip(tc, sol)]
            return VMobject().set_points_as_corners(pts).set_stroke(GOOD, 3)
        return always_redraw(line)

    def make_error(self):
        def fill():
            up = [self.ax.c2p(t, y) for t, y in zip(TS, gain(TS))]
            dn = [self.ax.c2p(t, y) for t, y in zip(TS[::-1], self.interp(TS[::-1]))]
            return Polygon(*up, *dn, stroke_width=0, fill_color=BAD,
                           fill_opacity=0.35)
        return always_redraw(fill)

    def make_readout(self):
        label = Text("calibration error:", font_size=24, color=BAD)
        num = DecimalNumber(0, num_decimal_places=0, font_size=30, color=BAD,
                            unit=r"^\circ")
        grp = VGroup(label, num).arrange(RIGHT, buff=0.2).to_corner(
            UR, buff=0.5).shift(0.55 * DOWN)
        num.add_updater(lambda m: m.set_value(self.rms_error()))
        return grp

    # -- beats ------------------------------------------------------------
    def beat_drift(self):
        self.show_caption("An antenna's gain drifts with time")
        self.ax = Axes(x_range=[0, T_END, 2], y_range=[-90, 90, 45],
                       x_length=11.5, y_length=4.8, tips=False,
                       axis_config=dict(color=MUTED, stroke_width=2,
                                        include_ticks=False)).shift(0.6 * DOWN)
        xl = Text("time", font_size=22, color=MUTED).next_to(
            self.ax.c2p(T_END, -90), DOWN, buff=0.12).align_to(
            self.ax.x_axis, RIGHT)
        yl = Text("gain phase", font_size=22, color=MUTED).rotate(PI / 2).next_to(
            self.ax.y_axis, LEFT, buff=0.15)
        self.true = self.curve(gain(TS), SIG_P, width=4)
        tl = Text("the truth (we never see it directly)", font_size=22,
                  color=SIG_P).next_to(self.ax.c2p(0.3, 62), RIGHT, buff=0)
        self.play(Create(self.ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        self.play(Create(self.true), FadeIn(tl), run_time=2.0)
        self.truth_label = tl
        self.wait(0.5)

    def beat_calibrator(self):
        self.show_caption("Between target scans, visit a calibrator: a bright "
                          "source we know")
        self.bands = self.make_bands()
        self.add(self.bands)
        key = VGroup(
            Square(0.25, stroke_width=0, fill_color=GOOD, fill_opacity=0.5),
            Text("calibrator", font_size=22, color=GOOD),
            Square(0.25, stroke_width=0, fill_color=SIG_Q, fill_opacity=0.3),
            Text("target", font_size=22, color=SIG_Q),
        ).arrange(RIGHT, buff=0.15)
        key[2].shift(0.3 * RIGHT)
        key[3].shift(0.3 * RIGHT)
        key.next_to(self.ax, DOWN, buff=0.35)
        self.play(FadeIn(self.bands), FadeIn(key), FadeOut(self.truth_label),
                  run_time=1.0)
        self.wait(0.5)

    def beat_solve(self):
        self.show_caption("On the calibrator we know the sky, so we can "
                          "solve for the gain")
        self.points = self.make_points()
        self.add(self.points)
        self.play(FadeIn(self.points, lag_ratio=0.2), run_time=1.5)
        self.wait(0.5)

    def beat_transfer(self):
        self.show_caption("Transfer: join the dots across the target scans")
        self.line = self.make_interp()
        self.add(self.line)
        self.play(Create(self.line), run_time=1.6)
        self.wait(0.5)

    def beat_error(self):
        self.show_caption("What the dots miss is our calibration error")
        self.err = self.make_error()
        self.readout = self.make_readout()
        self.add(self.err)
        # the number changes digit count as it updates: add it, don't animate it
        self.play(FadeIn(self.err), FadeIn(self.readout[0]), run_time=1.0)
        self.add(self.readout[1])
        self.wait(0.5)

    def beat_faint(self):
        self.show_caption("A fainter calibrator gives noisier solutions")
        self.play(self.sigma.animate.set_value(15), run_time=2.0)
        self.wait(0.8)

    def beat_cadence(self):
        self.show_caption("Visit less often, and the gain drifts in between")
        self.play(self.sigma.animate.set_value(4), run_time=1.0)
        self.play(self.cadence.animate.set_value(4.0), run_time=2.5,
                  rate_func=linear)
        self.wait(0.8)

    def beat_distance(self):
        self.show_caption("A calibrator far from the target sees a "
                          "different patch of sky")
        self.play(self.cadence.animate.set_value(1.5), run_time=1.5,
                  rate_func=linear)
        ghost = always_redraw(lambda: self.curve(
            gain(TS) + self.sep.get_value() * offset(TS), GOOD, width=2,
            opacity=0.6 * self.sep.get_value()))
        self.add(ghost)
        gl = Text("the gain towards the calibrator", font_size=22, color=GOOD
                  ).next_to(self.ax.c2p(0.3, -78), RIGHT, buff=0)
        self.play(self.sep.animate.set_value(1.0), FadeIn(gl), run_time=2.0)
        self.wait(0.8)
        self.ghost = VGroup(ghost, gl)

    def beat_wrap(self):
        self.show_caption("Good calibration: bright, nearby, and often")
        self.play(self.sep.animate.set_value(0.0), FadeOut(self.ghost[1]),
                  run_time=1.5)
        self.remove(self.ghost[0])
        self.wait(1.0)

    def scene_close(self):
        line1 = Text("Calibrators pin down the gains —", font_size=40,
                     color=FRONT)
        line2 = Text("everything in between is a guess.", font_size=40,
                     color=FRONT)
        msg = VGroup(line1, line2).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        tease = Text("next: self-calibration", font_size=26,
                     color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.0)
        self.play(FadeIn(tease), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(tease), run_time=1.0)
        self.wait(0.5)
