"""What Is a Visibility? — what a correlator actually measures.

Sequel to ../two-element-interferometer/ (see scenes.md for the plan).

Render:
    ~/software/manim/.venv/bin/manim -qm visibility.py WhatIsAVisibility
"""

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # antenna p (right)
SIG_Q = "#d29922"   # antenna q (left)
GOOD = "#3fb950"    # product / stripes / result
BAD = "#f85149"     # mismatch
FRONT = "#c9d1d9"   # wavefronts / annotations
MUTED = "#8b949e"

config.background_color = BG

# ----- physical layout (screen units) -----
GROUND_Y = -1.0
O = np.array([0.0, GROUND_Y, 0.0])   # baseline midpoint = phase origin
B0 = 3.6                             # starting baseline (b = 3.6 lambda)
LAM = 1.0
C_VIS = 0.7
OMEGA = 2 * PI * C_VIS / LAM
K = 2 * PI / LAM
D0 = 5 * LAM
D_MAX = 4.6
SKY_TOP = 3.7
SRC_R = 4.0

# ----- oscilloscope panels -----
PANEL_W, PANEL_H = 3.2, 1.0
V_SCROLL = 0.75
AMP = 0.32
SCOPE_C = np.array([-5.05, -2.15, 0.0])
PROD_C = np.array([-1.45, -2.15, 0.0])

TH_MAX = 18 * DEGREES


def s_hat(theta):
    """Unit vector pointing from O toward the source."""
    return np.array([np.sin(theta), np.cos(theta), 0.0])


def voltage(a, theta, t):
    """Receiver voltage; gated to zero before the leading wavefront arrives."""
    proj = float(s_hat(theta) @ (a - O))
    lead = D0 - C_VIS * t
    if lead > proj:
        return 0.0
    ramp = np.clip((proj - lead) / (0.15 * LAM), 0.0, 1.0)
    return ramp * np.cos(K * proj + OMEGA * t)


class WhatIsAVisibility(Scene):
    def construct(self):
        self.setup_trackers()
        self.build_apparatus()
        self.scene1_correlate()
        self.scene2_fringe()
        self.scene3_stripes()
        self.scene4_extended()
        self.scene5_fourier()

    # ------------------------------------------------------------------
    # trackers & machinery
    # ------------------------------------------------------------------
    def setup_trackers(self):
        self.clock = ValueTracker(20.0)     # wave already streaming (recap)
        self.rate = ValueTracker(0.0)
        self.theta = ValueTracker(0.0)      # source direction (phase centre = 0)
        self.b_tr = ValueTracker(B0)        # baseline length
        self.sig = ValueTracker(0.004)      # source width (in l = sin theta)
        self.front_op = ValueTracker(0.0)
        self.stripe_op = ValueTracker(0.0)
        self.clock.add_updater(
            lambda m, dt: m.increment_value(dt * self.rate.get_value())
        )
        self.add(self.clock)

    def t_now(self):
        return self.clock.get_value()

    def th_now(self):
        return self.theta.get_value()

    def u_now(self):
        return self.b_tr.get_value() / LAM

    def a_p(self):
        return O + np.array([+self.b_tr.get_value() / 2, 0, 0])

    def a_q(self):
        return O + np.array([-self.b_tr.get_value() / 2, 0, 0])

    def resp(self, l):
        """Normalized correlator output for a Gaussian source centred at l."""
        u, s = self.u_now(), self.sig.get_value()
        return np.exp(-2 * (PI * u * s) ** 2) * np.cos(2 * PI * u * l)

    # -- wavefronts (same machinery as video 1) -----------------------------
    def make_wavefronts(self):
        t, th = self.t_now(), self.th_now()
        master = self.front_op.get_value()
        sh = s_hat(th)
        perp = np.array([sh[1], -sh[0], 0.0])
        out = VGroup()
        if master < 1e-3:
            out.add(VMobject())
            return out
        n_lo = max(5, int(np.ceil((C_VIS * t + 0.05) / LAM)))
        n_hi = int(np.floor((C_VIS * t + D_MAX) / LAM))
        for n in range(n_lo, n_hi + 1):
            d = n * LAM - C_VIS * t
            c = O + d * sh
            p1, p2 = c + 3.1 * perp, c - 3.1 * perp
            seg = self.clip_segment(p1, p2)
            if seg is None:
                continue
            fade = np.clip(d / 0.6, 0, 1) * np.clip((D_MAX - d) / 0.4, 0, 1)
            out.add(
                Line(*seg, color=FRONT, stroke_width=2.5)
                .set_opacity(0.55 * fade * master)
            )
        if len(out) == 0:
            out.add(VMobject())
        return out

    @staticmethod
    def clip_segment(p1, p2):
        lo, hi = GROUND_Y + 0.05, SKY_TOP
        pts = []
        for a, b in ((p1, p2), (p2, p1)):
            p = a.copy()
            if p[1] < lo or p[1] > hi:
                if abs(b[1] - a[1]) < 1e-9:
                    return None
                bound = lo if p[1] < lo else hi
                f = (bound - a[1]) / (b[1] - a[1])
                if not 0 <= f <= 1:
                    return None
                p = a + f * (b - a)
            pts.append(p)
        if np.linalg.norm(pts[1] - pts[0]) < 0.05:
            return None
        return pts

    # -- apparatus ----------------------------------------------------------
    @staticmethod
    def make_antenna(pos, color):
        dish = ArcBetweenPoints(
            pos + np.array([-0.42, 0.55, 0]),
            pos + np.array([0.42, 0.55, 0]),
            angle=-PI / 2.2, color=color, stroke_width=5,
        )
        stand = Line(pos, pos + 0.42 * UP, color=color, stroke_width=5)
        feed = Dot(pos + 0.42 * UP, radius=0.05, color=color)
        return VGroup(dish, stand, feed)

    def make_panel(self, center, label, color, tag_right=False):
        box = RoundedRectangle(
            width=PANEL_W, height=PANEL_H, corner_radius=0.12,
            stroke_color=MUTED, stroke_width=2, fill_color=BG, fill_opacity=0.85,
        ).move_to(center)
        mid = DashedLine(
            box.get_left() + 0.08 * RIGHT, box.get_right() + 0.08 * LEFT,
            stroke_width=1, color=MUTED, dash_length=0.08,
        ).set_opacity(0.4)
        tag = MathTex(label, font_size=30, color=color).next_to(box, UP, buff=0.08)
        if tag_right:
            tag.align_to(box, RIGHT).shift(0.15 * LEFT)
        else:
            tag.align_to(box, LEFT).shift(0.15 * RIGHT)
        return VGroup(box, mid, tag)

    def make_trace(self, panel_box, a_func, color, n=110):
        t, th = self.t_now(), self.th_now()
        a = a_func()
        xr = panel_box.get_right()[0] - 0.10
        xl = panel_box.get_left()[0] + 0.10
        yc = panel_box.get_center()[1]
        xs = np.linspace(xl, xr, n)
        pts = [
            np.array([x, yc + AMP * voltage(a, th, t - (xr - x) / V_SCROLL), 0])
            for x in xs
        ]
        trace = VMobject(stroke_color=color, stroke_width=3)
        trace.set_points_as_corners(pts)
        return trace

    def make_ptrace(self, panel_box, n=110):
        """Product trace V_p * V_q at the same scrolled times."""
        t, th = self.t_now(), self.th_now()
        ap, aq = self.a_p(), self.a_q()
        xr = panel_box.get_right()[0] - 0.10
        xl = panel_box.get_left()[0] + 0.10
        yc = panel_box.get_center()[1]
        xs = np.linspace(xl, xr, n)
        pts = []
        for x in xs:
            ts = t - (xr - x) / V_SCROLL
            v = voltage(ap, th, ts) * voltage(aq, th, ts)
            pts.append(np.array([x, yc + 0.30 * v, 0]))
        trace = VMobject(stroke_color=GOOD, stroke_width=3)
        trace.set_points_as_corners(pts)
        return trace

    def make_stripes(self):
        """The fringe pattern painted on the sky: radial ticks, opacity = response."""
        op = self.stripe_op.get_value()
        out = VGroup()
        if op < 1e-3:
            out.add(VMobject())
            return out
        u = self.u_now()
        for th in np.linspace(-42 * DEGREES, 42 * DEGREES, 141):
            r = (1 + np.cos(2 * PI * u * np.sin(th))) / 2
            sh = s_hat(th)
            out.add(
                Line(O + 3.5 * sh, O + 3.95 * sh, color=GOOD, stroke_width=3)
                .set_opacity(0.7 * r ** 1.5 * op)
            )
        return out

    def make_source(self):
        """Point star for tiny sigma; a Gaussian blob of dots once extended."""
        thc, s = self.th_now(), self.sig.get_value()
        if s < 0.008:
            pos = O + SRC_R * s_hat(thc)
            star = Star(n=6, outer_radius=0.16, inner_radius=0.07,
                        color=YELLOW, fill_opacity=1).move_to(pos)
            halo = Dot(pos, radius=0.3, color=YELLOW).set_opacity(0.25)
            return VGroup(halo, star)
        out = VGroup()
        lc = np.sin(thc)
        for dl in np.linspace(-2.5 * s, 2.5 * s, 25):
            l = np.clip(lc + dl, -0.99, 0.99)
            w = np.exp(-dl ** 2 / (2 * s ** 2))
            out.add(
                Dot(O + SRC_R * s_hat(np.arcsin(l)), radius=0.11,
                    color=YELLOW).set_opacity(0.75 * w)
            )
        return out

    def build_apparatus(self):
        self.ground = Line(
            [-6.8, GROUND_Y, 0], [6.8, GROUND_Y, 0], color=MUTED, stroke_width=3
        )
        self.ant_p = always_redraw(
            lambda: self.make_antenna(self.a_p(), SIG_P)
        )
        self.ant_q = always_redraw(
            lambda: self.make_antenna(self.a_q(), SIG_Q)
        )
        self.lbl_p = always_redraw(
            lambda: MathTex("p", font_size=38, color=SIG_P).move_to(
                self.a_p() + 0.35 * DOWN
            )
        )
        self.lbl_q = always_redraw(
            lambda: MathTex("q", font_size=38, color=SIG_Q).move_to(
                self.a_q() + 0.35 * DOWN
            )
        )
        self.base_arrow = always_redraw(
            lambda: DoubleArrow(
                self.a_q() + 0.75 * DOWN, self.a_p() + 0.75 * DOWN, buff=0.5,
                color=FRONT, stroke_width=2.5, tip_length=0.15,
            )
        )
        self.base_lbl = always_redraw(
            lambda: MathTex("b", font_size=34, color=FRONT).move_to(
                O + 1.05 * DOWN
            )
        )

        self.source = always_redraw(self.make_source)
        self.fronts = always_redraw(self.make_wavefronts)
        self.stripes = always_redraw(self.make_stripes)

        # phase centre marker (zenith)
        self.zenith = DashedLine(O, O + 3.4 * UP, color=MUTED,
                                 stroke_width=2, dash_length=0.12).set_opacity(0.6)
        self.s0_lbl = MathTex("s_0", font_size=30, color=MUTED).move_to(
            O + 3.4 * UP + 0.3 * RIGHT
        )

        # scope panel (both traces) and product panel
        self.pan_s = self.make_panel(SCOPE_C, r"V_p,\;V_q", FRONT)
        self.pan_x = self.make_panel(PROD_C, r"V_p \times V_q", GOOD,
                                     tag_right=True)
        self.tr_p = always_redraw(
            lambda: self.make_trace(self.pan_s[0], self.a_p, SIG_P)
        )
        self.tr_q = always_redraw(
            lambda: self.make_trace(self.pan_s[0], self.a_q, SIG_Q)
        )
        self.tr_x = always_redraw(lambda: self.make_ptrace(self.pan_x[0]))

        # x node between the panels
        self.xnode = VGroup(
            Circle(radius=0.17, stroke_color=GOOD, stroke_width=2.5,
                   fill_color=BG, fill_opacity=1),
            MathTex(r"\times", font_size=28, color=GOOD),
        ).move_to([(SCOPE_C[0] + PROD_C[0]) / 2, SCOPE_C[1], 0])

        # feed -> scope connector stubs
        self.wire_p = always_redraw(
            lambda: Line(self.a_p(), self.pan_s[0].get_corner(UR) + 0.1 * DL,
                         color=MUTED, stroke_width=2).set_opacity(0.5)
        )
        self.wire_q = always_redraw(
            lambda: Line(self.a_q(), self.pan_s[0].get_corner(UL) + 0.1 * DR,
                         color=MUTED, stroke_width=2).set_opacity(0.5)
        )

        # averaged output readout under the product panel
        self.avg = VGroup(
            MathTex(r"\langle V_p V_q \rangle = ", font_size=32, color=GOOD),
            DecimalNumber(1.0, num_decimal_places=2, font_size=32, color=GOOD),
        ).arrange(RIGHT, buff=0.08).next_to(self.pan_x[0], DOWN, buff=0.22)
        self.avg[1].add_updater(
            lambda m: m.set_value(self.resp(np.sin(self.th_now())))
        )

        # fringe plot (right-bottom)
        self.axes = Axes(
            x_range=[-0.34, 0.34, 0.17], y_range=[-1.2, 1.2, 1.0],
            x_length=5.4, y_length=2.1,
            axis_config={"color": MUTED, "stroke_width": 2,
                         "include_ticks": False, "include_tip": False},
        ).move_to([3.85, -2.45, 0])
        self.ax_xlbl = MathTex(r"\sin\theta", font_size=26, color=MUTED).next_to(
            self.axes.x_axis.get_end(), DOWN, buff=0.10
        )

        def plot_pt():
            return self.axes.c2p(np.sin(self.th_now()),
                                 self.resp(np.sin(self.th_now())))

        self.plot_pt = plot_pt
        self.dot = always_redraw(
            lambda: Dot(plot_pt(), radius=0.07, color=GOOD)
        )

        # theta readout, top-left
        self.readout = VGroup(
            MathTex(r"\theta = ", font_size=32, color=FRONT),
            DecimalNumber(0, num_decimal_places=1, unit=r"^{\circ}",
                          font_size=32, color=FRONT),
        ).arrange(RIGHT, buff=0.08).to_corner(UL, buff=0.45)
        self.readout[1].add_updater(
            lambda m: m.set_value(self.th_now() / DEGREES)
        )

    def caption(self, text, color=FRONT, **kwargs):
        return Text(text, font_size=27, color=color, **kwargs).to_edge(
            UP, buff=0.25
        )

    # ------------------------------------------------------------------
    # Scene 1: multiply and average
    # ------------------------------------------------------------------
    def scene1_correlate(self):
        title = Text("What Is a Visibility?", font_size=44, color=FRONT)
        sub = Text("what a correlator actually measures", font_size=28,
                   color=MUTED).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

        # quick recap build: world + streaming wave
        self.play(
            Create(self.ground),
            FadeIn(self.ant_p), FadeIn(self.ant_q),
            FadeIn(self.lbl_p), FadeIn(self.lbl_q),
            run_time=1.2,
        )
        self.play(GrowFromCenter(self.base_arrow), FadeIn(self.base_lbl),
                  FadeIn(self.zenith), FadeIn(self.s0_lbl), run_time=0.9)
        self.add(self.source)
        self.add(self.fronts)
        self.bring_to_front(self.ant_p, self.ant_q, self.source)
        self.front_op.set_value(1.0)
        self.play(self.rate.animate.set_value(1), run_time=0.3)

        cap = self.caption("last time: delays compensated, two voltages in step")
        self.play(FadeIn(cap), run_time=0.7)
        self.play(FadeIn(self.pan_s), FadeIn(self.wire_p), FadeIn(self.wire_q),
                  FadeOut(self.base_arrow), FadeOut(self.base_lbl), run_time=0.9)
        self.add(self.tr_q, self.tr_p)
        self.play(FadeIn(self.readout), run_time=0.5)
        self.wait(2.5)

        # multiply...
        cap2 = self.caption("the correlator multiplies them, sample by sample")
        self.play(FadeOut(cap), FadeIn(cap2), FadeIn(self.xnode),
                  FadeIn(self.pan_x), run_time=0.9)
        self.add(self.tr_x)
        self.wait(3.0)

        # ...and average
        cap3 = self.caption("...and averages: two streams become one number")
        self.play(FadeOut(cap2), FadeIn(cap3), FadeIn(self.avg), run_time=0.9)
        self.wait(2.5)

        # that number becomes a point on a plot
        self.play(Create(self.axes), FadeIn(self.ax_xlbl), run_time=1.0)
        self.add(self.dot)
        self.path = TracedPath(self.plot_pt, stroke_color=FRONT, stroke_width=3)
        self.add(self.path)
        self.bring_to_front(self.dot)
        self.wait(1.5)
        self.play(FadeOut(cap3), run_time=0.5)

    # ------------------------------------------------------------------
    # Scene 2: the fringe
    # ------------------------------------------------------------------
    def scene2_fringe(self):
        cap = self.caption("hold the delay fixed — and let the sky drift")
        self.play(FadeIn(cap), run_time=0.7)

        u = self.u_now()
        th_null = float(np.arcsin(1 / (4 * u)))     # quarter fringe
        th_anti = float(np.arcsin(1 / (2 * u)))     # b sin(theta) = lambda/2

        self.play(self.theta.animate.set_value(th_null),
                  run_time=4.0, rate_func=rate_functions.ease_in_out_sine)
        cap2 = self.caption("a quarter fringe off: the average cancels to zero")
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.7)
        self.wait(2.0)

        self.play(FadeOut(cap2), run_time=0.5)
        self.play(self.theta.animate.set_value(th_anti),
                  run_time=3.5, rate_func=rate_functions.ease_in_out_sine)
        cap3 = self.caption("the anti-phase angle from last time — output fully negative",
                            color=BAD)
        self.play(FadeIn(cap3), run_time=0.7)
        self.wait(2.2)

        cap4 = self.caption("keep drifting: the output oscillates — this is the fringe")
        self.play(FadeOut(cap3), FadeIn(cap4), run_time=0.7)
        self.play(self.theta.animate.set_value(TH_MAX),
                  run_time=5.0, rate_func=rate_functions.ease_in_out_sine)
        fr_lbl = Text("the fringe", font_size=26, color=GOOD,
                      slant=ITALIC).next_to(self.axes, DOWN, buff=0.12)
        self.play(FadeIn(fr_lbl, scale=1.2), run_time=0.8)
        self.wait(1.8)
        self.play(FadeOut(cap4), run_time=0.5)
        self.fr_lbl = fr_lbl

    # ------------------------------------------------------------------
    # Scene 3: fringes painted on the sky
    # ------------------------------------------------------------------
    def scene3_stripes(self):
        cap = self.caption("the interferometer sees the sky through this pattern")
        self.play(FadeIn(cap),
                  self.stripe_op.animate.set_value(1.0), run_time=1.5)
        self.add(self.stripes)
        self.bring_to_front(self.source)
        sp_lbl = MathTex(r"\Delta\theta \approx \lambda / b", font_size=32,
                         color=GOOD).to_corner(UR, buff=0.45)
        self.play(FadeIn(sp_lbl), run_time=0.7)
        self.wait(1.5)

        cap2 = self.caption("bright stripe: signals agree — dark stripe: they cancel")
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.7)
        self.play(self.theta.animate.set_value(-TH_MAX),
                  run_time=8.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.0)
        self.play(FadeOut(cap2), run_time=0.5)
        self.sp_lbl = sp_lbl

    # ------------------------------------------------------------------
    # Scene 4: extended sources wash the fringe out
    # ------------------------------------------------------------------
    def scene4_extended(self):
        # recentre, retire the time-domain machinery (incoherent sources ahead)
        cap = self.caption("but real sources aren't points...")
        self.play(FadeIn(cap),
                  self.theta.animate.set_value(0.0), run_time=2.0)
        self.remove(self.tr_p, self.tr_q, self.tr_x, self.path)
        self.play(
            FadeOut(self.pan_s), FadeOut(self.pan_x), FadeOut(self.xnode),
            FadeOut(self.avg), FadeOut(self.wire_p), FadeOut(self.wire_q),
            FadeOut(self.fr_lbl),
            self.front_op.animate.set_value(0.0),
            run_time=1.2,
        )

        # live theoretical fringe: redrawn as sigma and b change
        self.curve = always_redraw(
            lambda: self.axes.plot(self.resp, x_range=[-0.33, 0.33, 0.004],
                                   color=GOOD, stroke_width=3)
        )
        self.add(self.curve)
        self.bring_to_front(self.dot)
        vis = VGroup(
            MathTex(r"|V_{pq}| = ", font_size=34, color=GOOD),
            DecimalNumber(1.0, num_decimal_places=2, font_size=34, color=GOOD),
        ).arrange(RIGHT, buff=0.08).to_corner(UR, buff=0.45).shift(0.7 * DOWN)
        vis[1].add_updater(
            lambda m: m.set_value(
                np.exp(-2 * (PI * self.u_now() * self.sig.get_value()) ** 2)
            )
        )
        self.play(FadeIn(vis), FadeOut(self.sp_lbl), run_time=0.8)

        # grow the source
        cap2 = self.caption("let the source grow wider than a stripe...")
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.7)
        self.play(self.sig.animate.set_value(0.05), run_time=3.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)
        cap3 = self.caption("it covers a crest and a trough at once — the fringe washes out")
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.7)
        self.play(self.sig.animate.set_value(0.10), run_time=4.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.5)

        # same source, longer baseline
        cap4 = self.caption("same source, longer baseline: finer stripes, weaker fringe")
        self.play(FadeOut(cap3), FadeIn(cap4),
                  self.sig.animate.set_value(0.05), run_time=1.5)
        self.play(FadeIn(self.base_arrow), FadeIn(self.base_lbl), run_time=0.6)
        self.play(self.b_tr.animate.set_value(9.0), run_time=6.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.0)

        box = SurroundingRectangle(vis, color=GOOD, buff=0.12, stroke_width=2.5)
        cap5 = self.caption("fringe contrast = |V| — the visibility amplitude")
        self.play(FadeOut(cap4), FadeIn(cap5), Create(box), run_time=0.9)
        self.wait(2.5)
        self.play(FadeOut(cap5), run_time=0.5)
        self.vis = vis
        self.vis_box = box

    # ------------------------------------------------------------------
    # Scene 5: one Fourier component
    # ------------------------------------------------------------------
    def scene5_fourier(self):
        # clear the stage
        self.remove(self.source, self.fronts, self.stripes, self.dot,
                    self.curve, self.ant_p, self.ant_q, self.lbl_p, self.lbl_q,
                    self.base_arrow, self.base_lbl, self.wire_p, self.wire_q)
        keep = VGroup(self.ground, self.zenith, self.s0_lbl, self.axes,
                      self.ax_xlbl, self.readout,
                      self.vis, self.vis_box)
        self.play(FadeOut(keep), run_time=1.0)

        # the integral picture: brightness x stripes -> shaded overlap
        ax = Axes(
            x_range=[-1, 1, 0.5], y_range=[-1.1, 1.1, 1],
            x_length=8.0, y_length=3.0,
            axis_config={"color": MUTED, "stroke_width": 2,
                         "include_ticks": False, "include_tip": False},
        ).move_to([0, 1.2, 0])
        ilbl = MathTex("l", font_size=28, color=MUTED).next_to(
            ax.x_axis.get_end(), UR, buff=0.08
        )

        def bright(l):
            return 0.95 * np.exp(-((l - 0.18) ** 2) / (2 * 0.22 ** 2))

        def stripes_f(l):
            return np.cos(2 * PI * 3 * l)

        sky = ax.plot(bright, color=SIG_Q, stroke_width=4)
        sky_lbl = MathTex("I(l)", font_size=34, color=SIG_Q).next_to(
            ax.c2p(0.18, 0.95), UP, buff=0.15
        )
        strp = ax.plot(stripes_f, x_range=[-1, 1, 0.002], color=MUTED,
                       stroke_width=2).set_stroke(opacity=0.7)
        prod = ax.plot(lambda l: bright(l) * stripes_f(l),
                       x_range=[-1, 1, 0.002], color=GOOD, stroke_width=3)
        area = ax.get_area(prod, x_range=[-1, 1], color=GOOD, opacity=0.25)

        cap = self.caption("one baseline asks one question of the sky")
        self.play(FadeIn(cap), Create(ax), FadeIn(ilbl), run_time=1.0)
        self.play(Create(sky), FadeIn(sky_lbl), run_time=1.0)
        self.play(Create(strp), run_time=1.0)
        self.wait(0.8)
        cap2 = self.caption("how much does the brightness overlap this one stripe pattern?")
        self.play(FadeOut(cap), FadeIn(cap2),
                  Create(prod), FadeIn(area), run_time=1.4)
        self.wait(1.5)

        eq = MathTex(
            r"V_{pq}", "=", r"\int", "I(l)",
            r"\, e^{-2\pi\imath\,(b/\lambda)\, l}", r"\, dl",
            font_size=44,
        ).move_to([0, -1.4, 0])
        eq[0].set_color(GOOD)
        eq[3].set_color(SIG_Q)
        bullets = VGroup(
            MathTex(r"|V_{pq}| \;\text{--- fringe contrast}",
                    font_size=30, color=FRONT),
            MathTex(r"\arg V_{pq} \;\text{--- fringe offset}",
                    font_size=30, color=FRONT),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to([0, -2.55, 0])
        cap3 = self.caption("that answer is the visibility")
        self.play(FadeOut(cap2), FadeIn(cap3), Write(eq), run_time=1.5)
        self.wait(1.0)
        self.play(FadeIn(bullets), run_time=0.9)
        self.wait(3.0)

        # closing card
        self.play(FadeOut(VGroup(ax, ilbl, sky, sky_lbl, strp, prod, area,
                                 eq, bullets, cap3)), run_time=1.0)
        line1 = Text("A visibility is one Fourier component", font_size=40,
                     color=FRONT)
        line2 = Text("of the sky.", font_size=40, color=FRONT)
        msg = VGroup(line1, line2).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        tease = Text("next: many baselines — aperture synthesis",
                     font_size=26, color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.0)
        self.play(FadeIn(tease), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(tease), run_time=1.0)
        self.wait(0.5)
