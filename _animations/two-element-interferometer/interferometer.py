"""The Two-Element Interferometer: Why Timing Is Everything.

Standalone educational animation (see scenes.md for the full plan).

Render:
    ~/software/manim/.venv/bin/manim -qm interferometer.py TwoElementInterferometer
"""

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # antenna p (right, nearer the source)
SIG_Q = "#d29922"   # antenna q (left)
GOOD = "#3fb950"    # extra path / lock / success
BAD = "#f85149"     # anti-phase / mismatch
FRONT = "#c9d1d9"   # wavefronts / annotations
MUTED = "#8b949e"

config.background_color = BG

# ----- physical layout (screen units) -----
GROUND_Y = -1.0
O = np.array([0.0, GROUND_Y, 0.0])   # baseline midpoint = phase origin
B = 3.6                              # baseline length
LAM = 1.0                            # wavelength on screen (b = 3.6 lambda)
C_VIS = 0.7                          # wave speed (period ~1.43 s)
OMEGA = 2 * PI * C_VIS / LAM
K = 2 * PI / LAM
D0 = 5 * LAM                         # leading crest starts this far from O
D_MAX = 4.6                          # crests drawn for 0 < d < D_MAX
SKY_TOP = 3.7
SRC_R = 4.0                          # source glyph distance from O

A_P = O + np.array([+B / 2, 0, 0])
A_Q = O + np.array([-B / 2, 0, 0])

# ----- oscilloscope panels -----
PANEL_W, PANEL_H = 3.2, 1.0
PANEL_Y = -2.35
V_SCROLL = 0.75                      # trace scroll speed (units/s)
AMP = 0.32

THETA_FINAL = 30 * DEGREES


def s_hat(theta):
    """Unit vector pointing from O toward the source."""
    return np.array([np.sin(theta), np.cos(theta), 0.0])


def antenna_proj(a, theta):
    """Distance of antenna a from O along the source direction."""
    return float(s_hat(theta) @ (a - O))


def voltage(a, theta, t, tau=0.0):
    """Receiver voltage; gated to zero before the leading wavefront arrives."""
    t_eff = t - tau
    proj = antenna_proj(a, theta)
    lead = D0 - C_VIS * t_eff        # leading-crest distance at the delayed time
    if lead > proj:                  # wave hasn't reached this antenna yet
        return 0.0
    ramp = np.clip((proj - lead) / (0.15 * LAM), 0.0, 1.0)
    return ramp * np.cos(K * proj + OMEGA * t_eff)


class TwoElementInterferometer(Scene):
    def construct(self):
        self.setup_trackers()
        self.build_apparatus()
        self.scene1_zenith()
        self.scene2_sweep()
        self.scene3_triangle()
        self.scene4_phase_up()
        self.scene5_tracking()

    # ------------------------------------------------------------------
    # trackers & machinery
    # ------------------------------------------------------------------
    def setup_trackers(self):
        self.clock = ValueTracker(0.0)      # master clock (s of wave time)
        self.rate = ValueTracker(0.0)       # time-flow rate (0 = frozen)
        self.theta = ValueTracker(0.0)
        self.tau = ValueTracker(0.0)        # instrumental delay on p
        self.front_op = ValueTracker(0.0)   # wavefront master opacity
        self.clock.add_updater(
            lambda m, dt: m.increment_value(dt * self.rate.get_value())
        )
        self.add(self.clock)

    def t_now(self):
        return self.clock.get_value()

    def th_now(self):
        return self.theta.get_value()

    # -- wavefronts --------------------------------------------------------
    def make_wavefronts(self):
        t, th = self.t_now(), self.th_now()
        master = self.front_op.get_value()
        sh = s_hat(th)
        perp = np.array([sh[1], -sh[0], 0.0])
        out = VGroup()
        if master < 1e-3:
            out.add(VMobject())  # never empty (avoids zero-size group issues)
            return out
        n_lo = max(5, int(np.ceil((C_VIS * t + 0.05) / LAM)))
        n_hi = int(np.floor((C_VIS * t + D_MAX) / LAM))
        half = 3.1
        for n in range(n_lo, n_hi + 1):
            d = n * LAM - C_VIS * t
            c = O + d * sh
            p1, p2 = c + half * perp, c - half * perp
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
        """Clip a wavefront segment to the sky region (above ground, below top)."""
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
            angle=-PI / 2.2,
            color=color,
            stroke_width=5,
        )
        stand = Line(pos, pos + 0.42 * UP, color=color, stroke_width=5)
        feed = Dot(pos + 0.42 * UP, radius=0.05, color=color)
        return VGroup(dish, stand, feed)

    def make_panel(self, center, label, color):
        box = RoundedRectangle(
            width=PANEL_W, height=PANEL_H, corner_radius=0.12,
            stroke_color=MUTED, stroke_width=2, fill_color=BG, fill_opacity=0.85,
        ).move_to(center)
        mid = DashedLine(
            box.get_left() + 0.08 * RIGHT, box.get_right() + 0.08 * LEFT,
            stroke_width=1, color=MUTED, dash_length=0.08,
        ).set_opacity(0.4)
        tag = MathTex(label, font_size=30, color=color).next_to(
            box, UP, buff=0.08
        ).align_to(box, LEFT).shift(0.15 * RIGHT)
        return VGroup(box, mid, tag)

    def make_trace(self, panel_box, antenna, color, delayed=False, n=110):
        """Scrolling voltage trace: newest sample at the right edge."""
        t, th = self.t_now(), self.th_now()
        tau = self.tau.get_value() if delayed else 0.0
        xr = panel_box.get_right()[0] - 0.10
        xl = panel_box.get_left()[0] + 0.10
        yc = panel_box.get_center()[1]
        xs = np.linspace(xl, xr, n)
        pts = [
            np.array([x, yc + AMP * voltage(antenna, th, t - (xr - x) / V_SCROLL, tau), 0])
            for x in xs
        ]
        trace = VMobject(stroke_color=color, stroke_width=3)
        trace.set_points_as_corners(pts)
        return trace

    def make_phase_dial(self, center):
        """Two-hand phase clock: amber hand fixed up, blue hand offset by dphi."""
        dphi = K * B * np.sin(self.th_now()) - OMEGA * self.tau.get_value()
        w = np.arctan2(np.sin(dphi), np.cos(dphi))          # wrap to [-pi, pi]
        heat = abs(w) / PI
        ring = Circle(radius=0.42, stroke_width=3).move_to(center)
        ring.set_stroke(interpolate_color(ManimColor(GOOD), ManimColor(BAD), heat))
        hq = Line(center, center + 0.34 * UP, color=SIG_Q, stroke_width=4)
        dir_p = np.array([np.sin(-w), np.cos(-w), 0.0])
        hp = Line(center, center + 0.34 * dir_p, color=SIG_P, stroke_width=4)
        return VGroup(ring, hq, hp)

    def build_apparatus(self):
        self.ground = Line(
            [-6.8, GROUND_Y, 0], [6.8, GROUND_Y, 0], color=MUTED, stroke_width=3
        )
        self.ant_p = self.make_antenna(A_P, SIG_P)
        self.ant_q = self.make_antenna(A_Q, SIG_Q)
        self.lbl_p = MathTex("p", font_size=38, color=SIG_P).next_to(
            self.ant_p, DOWN, buff=0.12
        )
        self.lbl_q = MathTex("q", font_size=38, color=SIG_Q).next_to(
            self.ant_q, DOWN, buff=0.12
        )
        self.base_arrow = DoubleArrow(
            A_Q + 0.5 * DOWN, A_P + 0.5 * DOWN, buff=0.5,
            color=FRONT, stroke_width=2.5, tip_length=0.15,
        ).shift(0.05 * DOWN)
        self.base_lbl = MathTex("b", font_size=34, color=FRONT).next_to(
            self.base_arrow, DOWN, buff=0.08
        )

        # source glyph rides the theta tracker
        def src():
            pos = O + SRC_R * s_hat(self.th_now())
            star = Star(n=6, outer_radius=0.16, inner_radius=0.07,
                        color=YELLOW, fill_opacity=1).move_to(pos)
            halo = Dot(pos, radius=0.3, color=YELLOW).set_opacity(0.25)
            return VGroup(halo, star)

        self.source = always_redraw(src)
        self.fronts = always_redraw(self.make_wavefronts)

        # panels: q left, overlay centre, p right
        self.pan_q = self.make_panel([-4.5, PANEL_Y, 0], r"V_q(t)", SIG_Q)
        self.pan_p = self.make_panel([4.5, PANEL_Y, 0], r"V_p(t)", SIG_P)
        self.pan_o = self.make_panel([0, PANEL_Y, 0], r"\mathrm{both}", FRONT)

        self.tr_q = always_redraw(
            lambda: self.make_trace(self.pan_q[0], A_Q, SIG_Q)
        )
        self.tr_p = always_redraw(
            lambda: self.make_trace(self.pan_p[0], A_P, SIG_P)
        )
        self.tr_oq = always_redraw(
            lambda: self.make_trace(self.pan_o[0], A_Q, SIG_Q)
        )
        self.tr_op = always_redraw(
            lambda: self.make_trace(self.pan_o[0], A_P, SIG_P, delayed=True)
        )

        # feed -> panel connector stubs
        self.wire_q = Line(A_Q, [-4.5 + PANEL_W / 2 - 0.1, PANEL_Y + PANEL_H / 2, 0],
                           color=MUTED, stroke_width=2).set_opacity(0.5)
        self.wire_p = Line(A_P, [4.5 - PANEL_W / 2 + 0.1, PANEL_Y + PANEL_H / 2, 0],
                           color=MUTED, stroke_width=2).set_opacity(0.5)

        self.dial = always_redraw(lambda: self.make_phase_dial([0, PANEL_Y - 1.05, 0]))
        self.dial_lbl = MathTex(r"\Delta\phi", font_size=30, color=FRONT).next_to(
            [0.55, PANEL_Y - 1.05, 0], RIGHT, buff=0.05
        )

        # zenith line + theta arc + readout
        self.zenith = DashedLine(O, O + 3.4 * UP, color=MUTED,
                                 stroke_width=2, dash_length=0.12).set_opacity(0.6)

        def th_arc():
            th = self.th_now()
            if th < 0.02:
                return VMobject()
            arc = Arc(radius=1.3, start_angle=PI / 2 - th, angle=th,
                      arc_center=O, color=FRONT, stroke_width=2.5)
            lab = MathTex(r"\theta", font_size=34, color=FRONT).move_to(
                O + 1.62 * s_hat(th / 2)
            )
            return VGroup(arc, lab)

        self.theta_arc = always_redraw(th_arc)

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

    def let_time_flow(self, duration):
        """Let the wave machinery run in real time."""
        self.play(self.rate.animate.set_value(1), run_time=0.0001)
        self.wait(duration)

    # ------------------------------------------------------------------
    # Scene 1: two dishes, one wave (zenith)
    # ------------------------------------------------------------------
    def scene1_zenith(self):
        title = Text("The Two-Element Interferometer",
                     font_size=44, color=FRONT)
        sub = Text("why timing is everything", font_size=28,
                   color=MUTED).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

        # build the world
        self.play(
            Create(self.ground),
            FadeIn(self.ant_p), FadeIn(self.ant_q),
            FadeIn(self.lbl_p), FadeIn(self.lbl_q),
            run_time=1.2,
        )
        self.play(GrowFromCenter(self.base_arrow), FadeIn(self.base_lbl),
                  run_time=0.8)
        self.add(self.source)
        self.play(FadeIn(self.zenith), run_time=0.8)
        self.wait(0.4)

        cap = self.caption("a distant source, straight overhead")
        self.play(FadeIn(cap), run_time=0.6)

        # panels + traces (flat until the wave arrives)
        self.play(
            FadeIn(self.pan_q), FadeIn(self.pan_p),
            FadeIn(self.wire_q), FadeIn(self.wire_p),
            run_time=0.9,
        )
        self.add(self.fronts)
        self.add(self.tr_q, self.tr_p)
        self.add(self.theta_arc)
        self.bring_to_front(self.ant_p, self.ant_q, self.source)

        # release the wave
        self.front_op.set_value(1.0)
        self.play(self.rate.animate.set_value(1), run_time=0.3)
        # leading crest needs D0/C_VIS ~ 7.1 s to reach the ground
        self.wait(5.0)
        cap2 = self.caption("the wavefronts strike both antennas at the same instant")
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.7)
        self.wait(4.5)

        # overlay panel: perfect agreement (baseline arrow has done its job)
        self.play(FadeIn(self.pan_o), FadeOut(self.base_arrow),
                  FadeOut(self.base_lbl), run_time=0.7)
        self.add(self.tr_oq, self.tr_op)
        self.play(FadeIn(self.dial), FadeIn(self.dial_lbl), FadeIn(self.readout),
                  run_time=0.7)
        cap3 = self.caption("the two voltages are perfectly in step")
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.7)
        self.wait(3.5)
        self.play(FadeOut(cap3), run_time=0.5)
        self.cap_prev = None

    # ------------------------------------------------------------------
    # Scene 2: tilt the source (the sweep)
    # ------------------------------------------------------------------
    def scene2_sweep(self):
        cap = self.caption("but real sources aren't at zenith...")
        self.play(FadeIn(cap), run_time=0.7)
        self.wait(1.2)

        # anti-phase angle: b sin(theta) = lambda/2
        th_anti = float(np.arcsin(0.5 * LAM / B))
        self.play(self.theta.animate.set_value(th_anti),
                  run_time=6.0, rate_func=rate_functions.ease_in_out_sine)

        cap2 = self.caption("at this angle the signals are perfectly opposed",
                            color=BAD)
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.7)
        box = SurroundingRectangle(self.pan_o, color=BAD, buff=0.06,
                                   stroke_width=2.5)
        self.play(Create(box), run_time=0.6)
        self.wait(3.0)
        self.play(FadeOut(box), FadeOut(cap2), run_time=0.6)

        cap3 = self.caption("one antenna hears the wave first — the other has to wait")
        self.play(FadeIn(cap3), run_time=0.7)
        self.play(self.theta.animate.set_value(THETA_FINAL),
                  run_time=7.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(2.5)
        self.play(FadeOut(cap3), run_time=0.5)

    # ------------------------------------------------------------------
    # Scene 3: the right triangle
    # ------------------------------------------------------------------
    def scene3_triangle(self):
        # freeze the world
        self.play(self.rate.animate.set_value(0.04), run_time=1.2)
        cap = self.caption("freeze the moment a wavefront touches antenna p")
        self.play(FadeIn(cap), run_time=0.7)

        th = self.th_now()
        sh = s_hat(th)
        perp = np.array([sh[1], -sh[0], 0.0])

        # wavefront through p at the instant of contact (extends up-left, in sky)
        wf_p = Line(A_P - 2.8 * perp, A_P + 0.12 * perp,
                    color=SIG_P, stroke_width=3.5).set_opacity(0.9)
        self.play(Create(wf_p), run_time=1.0)
        self.wait(0.8)

        # extra path: q -> foot of perpendicular on that wavefront
        ell = B * np.sin(th)
        F = A_Q + ell * sh
        extra = Line(A_Q, F, color=GOOD, stroke_width=5)
        cap2 = self.caption("antenna q sits this extra distance behind")
        self.play(FadeOut(cap), FadeIn(cap2), Create(extra), run_time=1.2)

        tri = Polygon(A_Q, A_P, F, stroke_color=FRONT, stroke_width=2,
                      fill_color=FRONT, fill_opacity=0.07)
        ra = RightAngle(Line(F, A_Q), Line(F, A_P), length=0.22,
                        color=FRONT, stroke_width=2)
        ang = Angle(Line(A_P, F), Line(A_P, A_Q), radius=0.55,
                    color=FRONT, stroke_width=2.5)
        bis = (Line(A_P, A_Q).get_unit_vector()
               + Line(A_P, F).get_unit_vector())
        bis = bis / np.linalg.norm(bis)
        ang_lbl = MathTex(r"\theta", font_size=30, color=FRONT).move_to(
            A_P + 0.85 * bis
        )
        self.play(FadeIn(tri), Create(ra), Create(ang), FadeIn(ang_lbl),
                  run_time=1.2)

        n_perp = np.array([-sh[1], sh[0], 0.0])   # perp to extra path, up-left
        ell_lbl = MathTex(r"\ell", font_size=34, color=GOOD).move_to(
            A_Q + 0.7 * ell * sh + 0.32 * n_perp
        )
        self.play(FadeIn(ell_lbl), run_time=0.6)
        self.wait(0.8)

        # equation chain, top-left under the readout
        eq1 = MathTex(r"\ell", "=", r"b\sin\theta",
                      font_size=40).set_color(FRONT)
        eq1[0].set_color(GOOD)
        eq2 = MathTex(r"\tau_g", "=", r"\frac{b\sin\theta}{c}",
                      font_size=40).set_color(FRONT)
        eq2[0].set_color(GOOD)
        eq3 = MathTex(r"\Delta\phi", "=", r"2\pi\nu\,\tau_g",
                      font_size=40).set_color(FRONT)
        eq3[0].set_color(GOOD)
        eqs = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        eqs.to_corner(UL, buff=0.45).shift(0.8 * DOWN)

        cap3 = self.caption("a little geometry gives the geometric delay")
        self.play(FadeOut(cap2), FadeIn(cap3), Write(eq1), run_time=1.2)
        self.wait(1.2)
        self.play(TransformMatchingTex(eq1.copy(), eq2), run_time=1.2)
        self.wait(1.2)
        self.play(TransformMatchingTex(eq2.copy(), eq3), run_time=1.2)
        rb = SurroundingRectangle(eq2, color=GOOD, buff=0.12, stroke_width=2.5)
        self.play(Create(rb), run_time=0.7)
        self.wait(2.2)

        self.tri_stuff = VGroup(wf_p, extra, tri, ra, ang, ang_lbl, ell_lbl)
        self.eq_stuff = VGroup(eq1, eq2, eq3, rb)
        self.play(FadeOut(cap3), FadeOut(self.tri_stuff), run_time=0.8)

    # ------------------------------------------------------------------
    # Scene 4: phasing up (delay compensation)
    # ------------------------------------------------------------------
    def make_coil(self):
        """Serpentine delay line in p's wire; loops grow with tau."""
        tau = self.tau.get_value()
        c = np.array([2.9, PANEL_Y - 1.05, 0.0])
        n_half = 2 + int(tau / 0.35)
        amp = 0.13 + 0.12 * np.clip(tau / 2.0, 0, 1)
        w = 1.5
        xs = np.linspace(c[0] - w / 2, c[0] + w / 2, 24 * n_half)
        pts = [
            np.array([x, c[1] + amp * np.sin((x - xs[0]) / w * PI * n_half), 0])
            for x in xs
        ]
        coil = VMobject(stroke_color=SIG_P, stroke_width=3)
        coil.set_points_as_corners(pts)
        return coil

    def scene4_phase_up(self):
        # resume time
        self.play(self.rate.animate.set_value(1), run_time=1.0)

        cap = self.caption("before combining the signals, undo the geometry")
        self.play(FadeIn(cap), run_time=0.7)

        # correlator block + feed wires
        corr = RoundedRectangle(width=1.7, height=0.75, corner_radius=0.1,
                                stroke_color=MUTED, stroke_width=2.5,
                                fill_color=BG, fill_opacity=0.9)
        corr.move_to([0, PANEL_Y - 1.05, 0]).shift(3.2 * LEFT)
        corr_lbl = MathTex(r"\times \;\to\; \langle\,\cdot\,\rangle",
                           font_size=30, color=FRONT).move_to(corr)
        corr_tag = Text("correlator", font_size=20, color=MUTED).next_to(
            corr, LEFT, buff=0.18
        )
        wq = Line(self.pan_q[0].get_bottom(), corr.get_top() + 0.2 * LEFT,
                  color=SIG_Q, stroke_width=2.5).set_opacity(0.7)
        wp1 = Line(self.pan_p[0].get_bottom(), [3.65, PANEL_Y - 1.05, 0],
                   color=SIG_P, stroke_width=2.5).set_opacity(0.7)
        wp2 = Line([2.15, PANEL_Y - 1.05, 0], corr.get_right(),
                   color=SIG_P, stroke_width=2.5).set_opacity(0.7)
        self.play(FadeIn(corr), FadeIn(corr_lbl), FadeIn(corr_tag),
                  Create(wq), Create(wp1), Create(wp2), run_time=1.3)

        # the delay line appears in p's path (p heard the wave first)
        coil = always_redraw(self.make_coil)
        tau_lbl = VGroup(
            MathTex(r"\tau = ", font_size=30, color=SIG_P),
            DecimalNumber(0, num_decimal_places=2, font_size=30, color=SIG_P),
        ).arrange(RIGHT, buff=0.06).move_to([4.95, PANEL_Y - 1.25, 0])
        tau_lbl[1].add_updater(lambda m: m.set_value(self.tau.get_value()))
        cap2 = self.caption("p heard the wave early — so make its signal wait")
        self.play(FadeOut(cap), FadeIn(cap2), FadeIn(coil), FadeIn(tau_lbl),
                  run_time=1.0)
        self.wait(1.0)

        # grow the delay to exactly tau_g; blue trace slides into lock
        tau_g = B * np.sin(THETA_FINAL) / C_VIS
        cap3 = self.caption("add exactly  b sin(θ) / c  of delay...")
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.7)
        self.play(self.tau.animate.set_value(tau_g),
                  run_time=6.0, rate_func=rate_functions.ease_out_quad)

        # lock!
        flash_box = SurroundingRectangle(self.pan_o, color=GOOD, buff=0.06,
                                         stroke_width=3)
        locked = Text("phased up", font_size=30, color=GOOD, weight=BOLD)
        locked.next_to(self.pan_o, UP, buff=0.45)
        self.play(
            Create(flash_box),
            Flash(self.pan_o[0].get_center(), color=GOOD, flash_radius=0.9,
                  line_length=0.25, num_lines=14),
            FadeIn(locked, scale=1.3),
            corr.animate.set_stroke(GOOD),
            run_time=1.0,
        )
        cap4 = self.caption("two dishes, listening as one")
        self.play(FadeOut(cap3), FadeIn(cap4), run_time=0.7)
        self.wait(3.0)
        self.play(FadeOut(cap4), FadeOut(locked), FadeOut(flash_box),
                  FadeOut(self.eq_stuff), run_time=0.8)
        self.s4 = VGroup(corr, corr_lbl, corr_tag, wq, wp1, wp2, tau_lbl)
        self.coil = coil

    # ------------------------------------------------------------------
    # Scene 5: tracking the sky (coda)
    # ------------------------------------------------------------------
    def scene5_tracking(self):
        cap = self.caption("the sky rotates — so the delay tracks it, continuously")
        self.play(FadeIn(cap), run_time=0.8)

        # slave the delay to the geometry: stays locked forever
        self.tau.add_updater(
            lambda m: m.set_value(B * np.sin(self.th_now()) / C_VIS)
        )
        self.play(self.theta.animate.set_value(10 * DEGREES),
                  run_time=5.0, rate_func=rate_functions.ease_in_out_sine)
        self.play(self.theta.animate.set_value(25 * DEGREES),
                  run_time=5.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.0)

        # closing card
        everything = VGroup(
            self.ground, self.ant_p, self.ant_q, self.lbl_p, self.lbl_q,
            self.zenith,
            self.pan_q, self.pan_p, self.pan_o, self.wire_q, self.wire_p,
            self.dial_lbl, self.readout, self.s4,
        )
        self.play(FadeOut(cap), run_time=0.5)
        self.remove(self.source, self.fronts,
                    self.tr_q, self.tr_p, self.tr_oq, self.tr_op,
                    self.dial, self.theta_arc, self.coil)
        self.play(FadeOut(everything), run_time=1.2)

        line1 = Text("Delay tracking —", font_size=40, color=FRONT)
        line2 = Text("the first thing every interferometer does.",
                     font_size=40, color=FRONT)
        msg = VGroup(line1, line2).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        tease = Text("next: what the correlator measures — the fringe",
                     font_size=26, color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.0)
        self.play(FadeIn(tease), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(tease), run_time=1.0)
        self.wait(0.5)
