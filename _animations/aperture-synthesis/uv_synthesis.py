"""Aperture Synthesis — many dishes, one giant eye.

Third installment (see scenes.md). The reconstruction panel is a genuine
masked-FFT inverse of the truth sky, driven by the same trackers that draw
the uv-plane, so the two can never disagree.

Render:
    ~/software/manim/.venv/bin/manim -qm uv_synthesis.py ApertureSynthesis
"""

from itertools import combinations

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # antennas
SIG_Q = "#d29922"   # sky / brightness
GOOD = "#3fb950"    # uv samples / tracks
BAD = "#f85149"
FRONT = "#c9d1d9"
MUTED = "#8b949e"

config.background_color = BG

# ----- panels -----
AC = np.array([-3.45, -0.35, 0.0])   # array / sky / reconstruction panel centre
UC = np.array([3.45, -0.35, 0.0])    # uv-plane panel centre
HALF = 2.1                           # half panel side (panels are 4.2 x 4.2)
ASC = 1.55                           # array units -> screen units
USC = 0.95                           # uv units -> screen units

# ----- antennas (array units; dense-ish core + outliers) -----
ANTS = [
    (0.0, 0.0), (0.55, 0.18), (0.15, 0.6), (-0.5, 0.4),
    (-0.28, -0.52), (0.95, -0.55), (-1.05, -0.75),
]
PAIRS = list(combinations(range(len(ANTS)), 2))
LONG_PAIR = (5, 6)                   # the long baseline used for the stripes beat

SIND = 0.7                           # sin(declination) -> ellipse axis ratio
H_FULL = 1.3                         # hour-angle sweep (rad)

# ----- imaging grid -----
NPIX = 128
CTR = NPIX // 2
S_UV = 22.0                          # uv units -> mask pixels


def make_sky():
    y, x = np.mgrid[0:NPIX, 0:NPIX].astype(float)

    def g(cx, cy, sig, amp):
        return amp * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sig ** 2))

    return (g(78, 58, 9, 0.55)        # diffuse blob
            + g(46, 50, 1.4, 1.0)     # point source
            + g(58, 88, 2.6, 0.85)    # close double...
            + g(68, 93, 2.6, 0.7))


SKY = make_sky()
F0 = np.fft.fftshift(np.fft.fft2(SKY))

_BGV = np.array([13.0, 17.0, 23.0])
_AMB = np.array([210.0, 153.0, 34.0])
_WHT = np.array([255.0, 244.0, 220.0])


def colorize(x):
    """Two-stop colormap bg -> amber -> warm white for x in [0, 1]."""
    t = np.clip(x, 0, 1)[..., None]
    lo = _BGV + (_AMB - _BGV) * np.clip(t, 0, 0.6) / 0.6
    hi = _AMB + (_WHT - _AMB) * (np.clip(t, 0.6, 1) - 0.6) / 0.4
    return np.where(t < 0.6, lo, hi).astype(np.uint8)


def baseline(i, j):
    return np.array(ANTS[j]) - np.array(ANTS[i])


def uv_of(b, h, s=1.0, sign=1):
    u = s * sign * (b[0] * np.cos(h) - b[1] * np.sin(h))
    v = s * sign * SIND * (b[0] * np.sin(h) + b[1] * np.cos(h))
    return u, v


class ApertureSynthesis(Scene):
    def construct(self):
        self.setup_trackers()
        self.scene1_plane()
        self.scene2_pairs()
        self.scene3_snapshot()
        self.scene4_rotation()
        self.scene5_dirty()

    # ------------------------------------------------------------------
    # trackers & shared machinery
    # ------------------------------------------------------------------
    def setup_trackers(self):
        self.H = ValueTracker(0.0)        # hour angle swept so far
        self.fr = ValueTracker(0.0)       # fractional bandwidth knob (0..1)
        self.one_bl = ValueTracker(0.0)   # 1 -> image from LONG_PAIR only

    def active_pairs(self):
        if self.one_bl.get_value() > 0.5:
            return [LONG_PAIR]
        return PAIRS

    def scalings(self):
        off = 0.08 * self.fr.get_value()
        return [1.0 - off, 1.0, 1.0 + off]

    def build_mask(self):
        h_max = self.H.get_value()
        hs = np.linspace(0.0, h_max, max(2, int(h_max / 0.025) + 1))
        mask = np.zeros((NPIX, NPIX))
        for (i, j) in self.active_pairs():
            b = baseline(i, j)
            for s in self.scalings():
                for h in hs:
                    for sign in (1, -1):
                        u, v = uv_of(b, h, s, sign)
                        iu = int(round(CTR + u * S_UV))
                        iv = int(round(CTR + v * S_UV))
                        if 0 <= iu < NPIX and 0 <= iv < NPIX:
                            mask[iv, iu] = 1.0
        return mask

    def make_recon(self):
        d = np.fft.ifft2(np.fft.ifftshift(F0 * self.build_mask())).real
        pos = np.clip(d, 0, None)
        m = pos.max()
        img = ImageMobject(colorize((pos / m) ** 0.7 if m > 0 else pos))
        img.set(height=2 * HALF).move_to(AC)
        return img

    def uv_pt(self, b, h, s=1.0, sign=1):
        u, v = uv_of(b, h, s, sign)
        return UC + np.array([u * USC, v * USC, 0.0])

    def make_tracks(self):
        """Arcs swept so far in the uv-plane + leading dots; tracker-driven."""
        h_max = self.H.get_value()
        out = VGroup()
        for (i, j) in PAIRS:
            b = baseline(i, j)
            for sign in (1, -1):
                for s in self.scalings():
                    if h_max > 1e-3:
                        out.add(
                            ParametricFunction(
                                lambda h, b=b, s=s, sign=sign:
                                    self.uv_pt(b, h, s, sign),
                                t_range=[0.0, h_max, h_max / 30],
                                stroke_color=GOOD, stroke_width=2,
                            ).set_stroke(opacity=0.55)
                        )
                    out.add(
                        Dot(self.uv_pt(b, h_max, s, sign), radius=0.035,
                            color=GOOD)
                    )
        return out

    @staticmethod
    def panel_frame(center, title):
        box = Rectangle(width=2 * HALF, height=2 * HALF, stroke_color=MUTED,
                        stroke_width=2).move_to(center)
        tag = Text(title, font_size=22, color=MUTED).next_to(box, UP, buff=0.12)
        return box, tag

    def ant_pos(self, k):
        return AC + np.array([ANTS[k][0] * ASC, ANTS[k][1] * ASC, 0.0])

    def caption(self, text, color=FRONT, **kwargs):
        return Text(text, font_size=27, color=color, **kwargs).to_edge(
            UP, buff=0.25
        )

    def counter_tex(self, n):
        nb = n * (n - 1) // 2
        return Text(f"{n} antennas   →   {nb} baseline{'s' if nb > 1 else ''}",
                    font_size=24, color=FRONT).next_to(
            [AC[0], AC[1] - HALF, 0], DOWN, buff=0.3
        )

    # ------------------------------------------------------------------
    # Scene 1: from a line to a plane
    # ------------------------------------------------------------------
    def scene1_plane(self):
        title = Text("Aperture Synthesis", font_size=44, color=FRONT)
        sub = Text("many dishes, one giant eye", font_size=28,
                   color=MUTED).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

        cap = self.caption("last time: one baseline measures one Fourier component")
        eq1 = MathTex(
            r"V_{pq}", "=", r"\int", "I(l)",
            r"\, e^{-2\pi\imath\,(b/\lambda)\, l}", r"\, dl",
            font_size=46,
        ).move_to(0.6 * UP)
        eq1[0].set_color(GOOD)
        eq1[3].set_color(SIG_Q)
        self.play(FadeIn(cap), Write(eq1), run_time=1.4)
        self.wait(2.0)

        cap2 = self.caption("but the sky is two-dimensional — frequencies live in a plane")
        eq2 = MathTex(
            r"V_{pq}", "=", r"\iint", "I(l,m)",
            r"\, e^{-2\pi\imath\,(u l + v m)}", r"\, dl\, dm",
            font_size=46,
        ).move_to(0.6 * UP)
        eq2[0].set_color(GOOD)
        eq2[3].set_color(SIG_Q)
        uv_def = MathTex(r"(u, v) = \vec{b}_{pq} / \lambda", font_size=40,
                         color=FRONT).next_to(eq2, DOWN, buff=0.6)
        self.play(FadeOut(cap), FadeIn(cap2),
                  TransformMatchingTex(eq1, eq2), run_time=1.4)
        self.wait(1.0)
        self.play(Write(uv_def), run_time=1.0)
        self.wait(2.2)
        self.play(FadeOut(cap2), FadeOut(eq2), FadeOut(uv_def), run_time=0.8)

    # ------------------------------------------------------------------
    # Scene 2: every pair is a baseline
    # ------------------------------------------------------------------
    def scene2_pairs(self):
        self.abox, self.atag = self.panel_frame(AC, "the array, from above")
        self.ubox, self.utag = self.panel_frame(UC, "the uv-plane")
        uv_axes = VGroup(
            Line(UC + HALF * 0.92 * LEFT, UC + HALF * 0.92 * RIGHT,
                 color=MUTED, stroke_width=1.2),
            Line(UC + HALF * 0.92 * DOWN, UC + HALF * 0.92 * UP,
                 color=MUTED, stroke_width=1.2),
            MathTex("u", font_size=26, color=MUTED).move_to(
                UC + np.array([HALF * 0.92 - 0.15, -0.18, 0])),
            MathTex("v", font_size=26, color=MUTED).move_to(
                UC + np.array([0.18, HALF * 0.92 + 0.0, 0])),
        ).set_opacity(0.6)
        self.uv_axes = uv_axes
        self.play(Create(self.abox), Create(self.ubox),
                  FadeIn(self.atag), FadeIn(self.utag), FadeIn(uv_axes),
                  run_time=1.2)

        # first two antennas -> one baseline -> one conjugate pair of points
        self.ant_dots = [Dot(self.ant_pos(k), radius=0.07, color=SIG_P)
                         for k in range(len(ANTS))]
        self.chords = {}
        self.uvdots = {}

        cap = self.caption("two antennas: one baseline vector")
        self.play(FadeIn(cap), FadeIn(self.ant_dots[0]),
                  FadeIn(self.ant_dots[1]), run_time=0.8)
        ch = Line(self.ant_pos(0), self.ant_pos(1), color=MUTED,
                  stroke_width=1.6).set_opacity(0.5)
        self.chords[(0, 1)] = ch
        self.play(Create(ch), run_time=0.6)

        b = baseline(0, 1)
        dots = VGroup(Dot(self.uv_pt(b, 0), radius=0.05, color=GOOD),
                      Dot(self.uv_pt(b, 0, sign=-1), radius=0.05, color=GOOD))
        self.uvdots[(0, 1)] = dots
        cap2 = self.caption("one point in the uv-plane — and its mirror twin")
        self.play(FadeOut(cap), FadeIn(cap2), FadeIn(dots, scale=2),
                  run_time=0.9)
        counter = self.counter_tex(2)
        self.play(FadeIn(counter), run_time=0.5)
        self.wait(1.5)

        cap3 = self.caption("every pair of dishes is a baseline — add more")
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.7)
        for k in range(2, len(ANTS)):
            new_chords = VGroup()
            new_dots = VGroup()
            for i in range(k):
                ch = Line(self.ant_pos(i), self.ant_pos(k), color=MUTED,
                          stroke_width=1.6).set_opacity(0.5)
                self.chords[(i, k)] = ch
                new_chords.add(ch)
                b = baseline(i, k)
                dd = VGroup(
                    Dot(self.uv_pt(b, 0), radius=0.05, color=GOOD),
                    Dot(self.uv_pt(b, 0, sign=-1), radius=0.05, color=GOOD),
                )
                self.uvdots[(i, k)] = dd
                new_dots.add(dd)
            self.play(
                FadeIn(self.ant_dots[k]),
                LaggedStart(*[Create(c) for c in new_chords], lag_ratio=0.15),
                LaggedStart(*[FadeIn(d, scale=2) for d in new_dots],
                            lag_ratio=0.15),
                Transform(counter, self.counter_tex(k + 1)),
                run_time=1.1,
            )
        self.counter = counter
        self.wait(1.0)
        cap4 = self.caption("seven dishes already ask 21 questions of the sky at once")
        self.play(FadeOut(cap3), FadeIn(cap4), run_time=0.7)
        self.wait(2.0)
        self.play(FadeOut(cap4), run_time=0.5)

    # ------------------------------------------------------------------
    # Scene 3: try to make a picture (snapshot)
    # ------------------------------------------------------------------
    def scene3_snapshot(self):
        # reveal the truth sky where the array panel was
        truth = ImageMobject(colorize((SKY / SKY.max()) ** 0.7))
        truth.set(height=2 * HALF).move_to(AC)
        tlbl = Text("a patch of sky", font_size=22, color=SIG_Q).next_to(
            truth, UP, buff=0.12
        )
        cap = self.caption("here is what's really up there")
        array_stuff = VGroup(*self.ant_dots, *self.chords.values(),
                             self.atag, self.counter)
        self.play(FadeOut(array_stuff), run_time=0.6)
        self.play(FadeIn(cap), FadeIn(truth), FadeIn(tlbl), run_time=1.0)
        self.wait(2.2)

        # shrink the truth to an inset; reconstruction takes its place
        cap2 = self.caption("what can 21 samples reconstruct?")
        inset_box = Rectangle(width=1.62, height=1.62, stroke_color=MUTED,
                              stroke_width=1.5).move_to([-6.2, 2.7, 0])
        tlbl_small = Text("the sky", font_size=18, color=SIG_Q).next_to(
            inset_box, DOWN, buff=0.08
        )
        self.play(
            FadeOut(cap), FadeIn(cap2),
            truth.animate.set(height=1.6).move_to([-6.2, 2.7, 0]),
            Transform(tlbl, tlbl_small),
            run_time=1.2,
        )
        self.add(inset_box)
        self.truth, self.tlbl, self.inset_box = truth, tlbl, inset_box

        rlbl = Text("reconstruction", font_size=22, color=GOOD).next_to(
            [AC[0], AC[1] - HALF, 0], DOWN, buff=0.3
        )
        self.rlbl = rlbl

        # one baseline first: pure stripes (the video-2 callback)
        self.one_bl.set_value(1.0)
        self.recon = always_redraw(self.make_recon)
        dim = [d for p, d in self.uvdots.items() if p != LONG_PAIR]
        ring = VGroup(*[
            Circle(radius=0.13, stroke_color=FRONT, stroke_width=2).move_to(
                self.uvdots[LONG_PAIR][k].get_center())
            for k in (0, 1)
        ])
        cap3 = self.caption("one baseline alone: just its stripe pattern, again")
        self.play(FadeOut(cap2), FadeIn(cap3),
                  *[d.animate.set_opacity(0.18) for d in dim],
                  Create(ring), run_time=1.0)
        self.add(self.recon)
        self.bring_to_front(self.abox)
        self.play(FadeIn(rlbl), run_time=0.6)
        self.wait(2.8)

        # all 21 at once: a crude snapshot
        cap4 = self.caption("all 21 at once: a crude, ringing snapshot")
        self.play(FadeOut(cap3), FadeIn(cap4), FadeOut(ring),
                  *[d.animate.set_opacity(1.0) for d in dim],
                  self.one_bl.animate.set_value(0.0), run_time=1.0)
        self.wait(3.0)
        self.play(FadeOut(cap4), run_time=0.5)

    # ------------------------------------------------------------------
    # Scene 4: let the Earth do the work
    # ------------------------------------------------------------------
    def scene4_rotation(self):
        # swap the static uv dots for tracker-driven tracks (same positions)
        tracks = always_redraw(self.make_tracks)
        self.add(tracks)
        self.remove(*self.uvdots.values())
        self.tracks = tracks

        hread = VGroup(
            Text("observing time: ", font_size=24, color=FRONT),
            DecimalNumber(0, num_decimal_places=1, unit=r"\,\text{h}",
                          font_size=28, color=FRONT),
        ).arrange(RIGHT, buff=0.1).to_corner(UR, buff=0.4).shift(0.75 * DOWN)
        hread[1].add_updater(
            lambda m: m.set_value(self.H.get_value() * 12 / PI)
        )

        cap = self.caption("now let the Earth turn the array under the sky")
        self.play(FadeIn(cap), FadeIn(hread), run_time=0.8)
        self.play(self.H.animate.set_value(H_FULL), run_time=9.0,
                  rate_func=rate_functions.ease_in_out_sine)
        cap2 = self.caption("every baseline sweeps an arc — the plane fills in")
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.7)
        self.wait(2.0)

        cap3 = self.caption("observe across a band of frequencies: (u,v) scales with ν")
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.7)
        self.play(self.fr.animate.set_value(1.0), run_time=4.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.5)
        cap4 = self.caption("more antennas + earth rotation + frequency = fewer holes")
        self.play(FadeOut(cap3), FadeIn(cap4), run_time=0.7)
        self.wait(2.5)
        self.play(FadeOut(cap4), FadeOut(hread), run_time=0.6)
        self.hread = hread

    # ------------------------------------------------------------------
    # Scene 5: the dirty image
    # ------------------------------------------------------------------
    def scene5_dirty(self):
        cap = self.caption("close — but the holes we never sampled still ripple the image")
        self.play(FadeIn(cap), run_time=0.8)
        self.wait(1.5)
        dirty = Text("the dirty image", font_size=26, color=SIG_Q,
                     slant=ITALIC).next_to(
            [AC[0], AC[1] - HALF, 0], DOWN, buff=0.3
        )
        self.play(FadeOut(self.rlbl), FadeIn(dirty), run_time=0.8)
        self.wait(2.5)

        # closing card
        self.play(FadeOut(cap), run_time=0.5)
        self.remove(self.recon, self.tracks)
        self.play(FadeOut(Group(
            self.truth, self.tlbl, self.inset_box, dirty,
            self.abox, self.ubox, self.utag, self.uv_axes,
        )), run_time=1.0)

        line1 = Text("Aperture synthesis —", font_size=40, color=FRONT)
        line2 = Text("many dishes, hours, and bandwidth: one giant eye.",
                     font_size=36, color=FRONT)
        msg = VGroup(line1, line2).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        tease = Text("next: from dirty images to the sky — deconvolution",
                     font_size=26, color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.0)
        self.play(FadeIn(tease), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(tease), run_time=1.0)
        self.wait(0.5)
