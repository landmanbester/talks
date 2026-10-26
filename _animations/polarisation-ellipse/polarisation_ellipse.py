"""What Can Happen to a Wiggle — delay, twist, shrink, and the polarisation ellipse.

Episode of the interferometry explainer series (see scenes.md for the plan).

Render (from this directory):
    ../preview.sh polarisation_ellipse.py WhatCanHappenToAWiggle   # dev loop: -ql + frame sheet
    ../final.sh polarisation_ellipse.py WhatCanHappenToAWiggle     # final: 1080p60 + duration check
"""

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # instrument
SIG_Q = "#d29922"   # sky signal: the wave
GOOD = "#3fb950"    # measurements / results
BAD = "#f85149"     # mismatch / warnings
FRONT = "#c9d1d9"   # annotations / text
MUTED = "#8b949e"

config.background_color = BG

# ----- the wave -----
T = 2.0                       # wave period (s); deck holds loop 3 periods
OMEGA = 2 * PI / T
HOLD = 3 * T
THETA0 = -15 * DEGREES        # starting direction of the wiggle

# ----- layout -----
PC = np.array([-3.4, 0.75, 0])  # panel centre
SCALE = 1.35                    # screen units per unit field
BOX = 1.75                      # panel half-size
GAP = 0.3                       # panel edge to the start of a trace
SPEED = 1.5                     # trace scroll speed (screen units / s)
Y_TRACE_X0 = PC[0] + BOX + GAP  # y wiggle: starts right of the panel ...
Y_TRACE_X1 = 6.6                # ... and scrolls right
X_TRACE_Y0 = PC[1] - BOX - GAP  # x wiggle: starts below the panel ...
X_TRACE_Y1 = -3.85              # ... and scrolls down
CARD_POS = np.array([3.0, -2.15, 0])


def rot(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], complex)


def state(phi=0.0, theta=0.0, amp=1.0, delta=0.0):
    """Polarisation state after the four moves, in the order the journey
    meets them: delay both (phi), twist (theta), shrink (amp), and delay y
    more than x (delta). Multiplying by e^{+i phi} is a true delay for the
    field Re(v e^{-i omega t})."""
    e0 = np.array([np.cos(THETA0), np.sin(THETA0)], complex)
    v = amp * np.exp(1j * phi) * (rot(theta) @ e0)
    return np.array([v[0], v[1] * np.exp(1j * delta)])


def field(v, t):
    return np.real(v * np.exp(-1j * OMEGA * t))


class WhatCanHappenToAWiggle(Scene):
    standalone = True   # title / closing cards (the deck wrapper turns them off)

    def construct(self):
        self.setup_trackers()
        self.cap = None
        if self.standalone:
            self.scene_title()
        self.beat_wiggle()
        self.beat_components()
        self.beat_delay()
        self.beat_twist()
        self.beat_shrink()
        self.beat_uneven()
        self.beat_circle()
        self.beat_summary()
        if self.standalone:
            self.scene_close()
        else:
            self.wait(0.5)

    # ------------------------------------------------------------------
    def setup_trackers(self):
        self.clock = ValueTracker(0.0)
        self.rate = ValueTracker(0.0)      # 0 = frozen, 1 = real time
        self.clock.add_updater(
            lambda m, dt: m.increment_value(dt * self.rate.get_value())
        )
        self.add(self.clock)
        self.phi = ValueTracker(0.0)
        self.theta = ValueTracker(0.0)
        self.amp = ValueTracker(1.0)
        self.delta = ValueTracker(0.0)
        self.ghost = None                  # snapshot of the state before a move
        self.ghost_on = ValueTracker(0.0)  # ghost opacity

    def t_now(self):
        return self.clock.get_value()

    def params(self):
        return dict(phi=self.phi.get_value(), theta=self.theta.get_value(),
                    amp=self.amp.get_value(), delta=self.delta.get_value())

    def v_now(self):
        return state(**self.params())

    def v_ghost(self):
        return state(**self.ghost)

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

    # -- pieces ---------------------------------------------------------
    def tip(self, v, t):
        e = field(v, t)
        return PC + SCALE * np.array([e[0], e[1], 0])

    def loop_curve(self, v, centre=PC, scale=SCALE, n=90):
        pts = []
        for t in np.linspace(0, T, n):
            e = field(v, t)
            pts.append(centre + scale * np.array([e[0], e[1], 0]))
        return VMobject().set_points_as_corners(pts)

    def make_panel(self):
        box = RoundedRectangle(width=2 * BOX, height=2 * BOX,
                               corner_radius=0.15, stroke_color=MUTED,
                               stroke_width=2).move_to(PC)
        ax_x = Line(PC + 0.9 * BOX * LEFT, PC + 0.9 * BOX * RIGHT)
        ax_y = Line(PC + 0.9 * BOX * DOWN, PC + 0.9 * BOX * UP)
        axes = VGroup(ax_x, ax_y).set_stroke(MUTED, 1.2, opacity=0.5)
        lx = Text("x", font_size=22, color=MUTED).next_to(
            ax_x.get_end(), DOWN + LEFT, buff=0.06)
        ly = Text("y", font_size=22, color=MUTED).next_to(ax_y, UP, 0.06)
        return VGroup(box, axes, lx, ly)

    def make_live(self):
        """The tip trace, arrow and dot of the current state."""
        def draw():
            v = self.v_now()
            t = self.t_now()
            trace = self.loop_curve(v).set_stroke(SIG_Q, 2.5, opacity=0.55)
            p = self.tip(v, t)
            return VGroup(trace, Line(PC, p, stroke_width=5, color=SIG_Q),
                          Dot(p, radius=0.08, color=SIG_Q))
        return always_redraw(draw)

    def make_ghost(self):
        """The state before the current move: a faint trace and dot."""
        def draw():
            op = self.ghost_on.get_value()
            if self.ghost is None or op == 0:
                return VGroup()
            v = self.v_ghost()
            trace = self.loop_curve(v).set_stroke(MUTED, 2, opacity=0.5 * op)
            # a ring, drawn over the live state, so it stays visible when the
            # two lie on the same line (the delay move)
            ring = Circle(radius=0.12).move_to(self.tip(v, self.t_now()))
            ring.set_stroke(FRONT, 2.5, opacity=0.85 * op)
            return VGroup(trace, ring)
        return always_redraw(draw)

    def y_trace_pts(self, v, t):
        ds = np.linspace(0, Y_TRACE_X1 - Y_TRACE_X0, 160)
        return [np.array([Y_TRACE_X0 + d,
                          PC[1] + SCALE * field(v, t - d / SPEED)[1], 0])
                for d in ds]

    def x_trace_pts(self, v, t):
        ds = np.linspace(0, X_TRACE_Y0 - X_TRACE_Y1, 100)
        return [np.array([PC[0] + SCALE * field(v, t - d / SPEED)[0],
                          X_TRACE_Y0 - d, 0]) for d in ds]

    def make_traces(self):
        """The y wiggle (right) and x wiggle (below), joined to the tip."""
        def draw():
            v = self.v_now()
            t = self.t_now()
            out = VGroup()
            op = self.ghost_on.get_value()
            if self.ghost is not None and op > 0:
                g = self.v_ghost()
                for pts in (self.y_trace_pts(g, t), self.x_trace_pts(g, t)):
                    out.add(VMobject().set_points_as_corners(pts).set_stroke(
                        MUTED, 2, opacity=0.5 * op))
            yp = self.y_trace_pts(v, t)
            xp = self.x_trace_pts(v, t)
            for pts in (yp, xp):
                out.add(VMobject().set_points_as_corners(pts).set_stroke(
                    FRONT, 3))
            p = self.tip(v, t)
            out.add(DashedLine(p, yp[0], dash_length=0.08, stroke_width=1.5,
                               color=SIG_Q).set_opacity(0.7))
            out.add(DashedLine(p, xp[0], dash_length=0.08, stroke_width=1.5,
                               color=SIG_Q).set_opacity(0.7))
            out.add(Dot(yp[0], radius=0.06, color=FRONT),
                    Dot(xp[0], radius=0.06, color=FRONT))
            return out
        return always_redraw(draw)

    def trace_guides(self):
        gy = Line([Y_TRACE_X0, PC[1], 0], [Y_TRACE_X1, PC[1], 0])
        gx = Line([PC[0], X_TRACE_Y0, 0], [PC[0], X_TRACE_Y1, 0])
        guides = VGroup(gy, gx).set_stroke(MUTED, 1, opacity=0.4)
        ly = Text("y wiggle", font_size=22, color=MUTED).next_to(
            gy.get_end(), UP, buff=0.1).shift(0.5 * LEFT + 1.25 * UP)
        lx = Text("x wiggle", font_size=22, color=MUTED).next_to(
            gx.get_end(), RIGHT, buff=0.15).shift(1.3 * RIGHT + 0.25 * UP)
        return VGroup(guides, ly, lx)

    def move_card(self, word, letters, color=FRONT, extra=None):
        w = Text(word, font_size=40, color=color, weight=BOLD)
        l = Text(letters, font_size=24, color=MUTED)
        g = VGroup(w, l).arrange(DOWN, buff=0.15)
        if extra is not None:
            g.add(Text(extra, font_size=22, color=color).next_to(l, DOWN, 0.15))
        return g.move_to(CARD_POS)

    def show_card(self, card):
        old = getattr(self, "card", None)
        anims = [FadeIn(card, shift=0.15 * UP)]
        if old is not None:
            anims.append(FadeOut(old))
        self.play(*anims, run_time=0.6)
        self.card = card

    def snapshot_ghost(self):
        self.ghost = self.params()
        self.ghost_on.set_value(1.0)

    # -- beats ----------------------------------------------------------
    def scene_title(self):
        title = Text("What Can Happen to a Wiggle", font_size=44, color=FRONT)
        sub = Text("delay, twist, shrink — and the polarisation ellipse",
                   font_size=28, color=MUTED).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

    def beat_wiggle(self):
        self.show_caption("Light wiggles: the tip of its field traces out a shape")
        self.panel = self.make_panel()
        self.live = self.make_live()
        self.ghost_mob = self.make_ghost()
        self.add(self.live, self.ghost_mob)
        self.play(FadeIn(self.panel), FadeIn(self.live), run_time=0.8)
        self.play(self.rate.animate.set_value(1), run_time=0.3)
        self.wait(2 * T)

    def beat_components(self):
        self.show_caption("Split it into an x wiggle and a y wiggle: "
                          "in step, they make a line")
        self.guides = self.trace_guides()
        self.traces = self.make_traces()
        self.add(self.traces)
        self.play(FadeIn(self.guides), FadeIn(self.traces), run_time=1.0)
        self.wait(2 * T)

    def beat_delay(self):
        self.show_caption("Delay both wiggles equally: the same line, just later")
        self.snapshot_ghost()
        self.show_card(self.move_card("delay", "space K · ionosphere Z"))
        self.play(self.phi.animate.set_value(80 * DEGREES), run_time=2.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(T)

    def beat_twist(self):
        self.show_caption("Twist it: the line turns")
        self.snapshot_ghost()
        self.show_card(self.move_card("twist", "Faraday F · parallactic P"))
        self.play(self.theta.animate.set_value(60 * DEGREES), run_time=2.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(T)

    def beat_shrink(self):
        self.show_caption("Shrink it: the line gets smaller")
        self.snapshot_ghost()
        self.show_card(self.move_card("shrink", "primary beam E"))
        self.play(self.amp.animate.set_value(0.7), run_time=2.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(T)

    def beat_uneven(self):
        self.show_caption("Delay y more than x: the line opens into an ellipse")
        self.snapshot_ghost()
        self.show_card(self.move_card("uneven delay", "leakage D · gains G",
                                      color=GOOD,
                                      extra="the polarisation ellipse"))
        self.play(self.delta.animate.set_value(55 * DEGREES), run_time=3.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(T)

    def beat_circle(self):
        self.show_caption("A quarter-wave difference makes a circle")
        self.snapshot_ghost()
        self.play(self.delta.animate.set_value(90 * DEGREES), run_time=2.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(T)

    def beat_summary(self):
        self.show_caption("Only an uneven delay changes the shape")
        old = [self.panel, self.live, self.ghost_mob, self.traces,
               self.guides, self.card]
        self.play(*[FadeOut(m) for m in old], run_time=0.8)
        self.remove(self.live, self.ghost_mob, self.traces)

        r, s = 1.35, 1.05
        steps = [
            ("delay", "same shape, later", dict(), dict(phi=80 * DEGREES),
             SIG_Q),
            ("twist", "same shape, turned", dict(), dict(theta=60 * DEGREES),
             SIG_Q),
            ("shrink", "same shape, smaller", dict(theta=60 * DEGREES),
             dict(theta=60 * DEGREES, amp=0.7), SIG_Q),
            ("uneven delay", "a new shape", dict(theta=60 * DEGREES, amp=0.7),
             dict(theta=60 * DEGREES, amp=0.7, delta=70 * DEGREES), GOOD),
        ]
        xs = [-4.95, -1.65, 1.65, 4.95]
        minis = []
        for (word, sub, before, after, col), x in zip(steps, xs):
            c = np.array([x, 0.6, 0])
            box = RoundedRectangle(width=2 * r, height=2 * r, corner_radius=0.12,
                                   stroke_color=col if col == GOOD else MUTED,
                                   stroke_width=2).move_to(c)
            vb, va = state(**before), state(**after)
            ghost = self.loop_curve(vb, c, s).set_stroke(MUTED, 2, opacity=0.5)
            after_c = self.loop_curve(va, c, s).set_stroke(col, 2.5, opacity=0.6)

            def dots(vb=vb, va=va, c=c, col=col):
                t = self.t_now()
                pb = c + s * np.r_[field(vb, t), 0]
                pa = c + s * np.r_[field(va, t), 0]
                return VGroup(Circle(radius=0.1).move_to(pb).set_stroke(
                                  FRONT, 2, opacity=0.8),
                              Line(c, pa, stroke_width=4, color=col),
                              Dot(pa, radius=0.065, color=col))
            live = always_redraw(dots)
            w = Text(word, font_size=28, color=col if col == GOOD else FRONT,
                     weight=BOLD).next_to(box, DOWN, buff=0.3)
            t2 = Text(sub, font_size=21, color=MUTED).next_to(w, DOWN, 0.12)
            static = VGroup(box, ghost, after_c, w, t2)
            self.add(live)
            minis.append((static, live))
        self.play(LaggedStart(*[AnimationGroup(FadeIn(st), FadeIn(lv))
                                for st, lv in minis], lag_ratio=0.35),
                  run_time=2.4)
        self.minis = VGroup(*[VGroup(st, lv) for st, lv in minis])
        self.wait(2 * T)

    def scene_close(self):
        line1 = Text("Delay, twist and shrink keep a line a line —",
                     font_size=36, color=FRONT)
        line2 = Text("only an uneven delay makes an ellipse.", font_size=36,
                     color=FRONT)
        msg = VGroup(line1, line2).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        tease = Text("next: the journey of a wave", font_size=26,
                     color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.play(FadeOut(Group(*[m for m in self.mobjects
                                  if m is not self.clock])), run_time=0.8)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.0)
        self.play(FadeIn(tease), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(tease), run_time=1.0)
        self.wait(0.5)
