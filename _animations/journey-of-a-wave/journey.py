"""The Journey of a Wave — every effect on the way is a Jones matrix.

Episode of the interferometry explainer series (see scenes.md for the plan).

Render (from this directory):
    ../preview.sh journey.py JourneyOfAWave        # dev loop: -ql + frame sheet
    ../final.sh journey.py JourneyOfAWave          # final: 1080p60 + duration check
"""

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # instrument
SIG_Q = "#d29922"   # sky signal
GOOD = "#3fb950"    # measurements / results
BAD = "#f85149"     # mismatch / warnings
FRONT = "#c9d1d9"   # annotations / text
MUTED = "#8b949e"

config.background_color = BG

# ----- the wave -----
T = 2.0                       # wave period (s); hold loops are 3 periods
OMEGA = 2 * PI / T
LAM = 1.0                     # ribbon wavelength on screen
C_RIB = LAM / T               # ribbon phase speed: periodic in T by construction
HOLD = 3 * T

# ----- layout -----
PATH_Y = -1.0
X_SRC, X_CLOUD, X_DISH, X_RX, X_OUT = -6.3, -3.3, 0.35, 3.7, 6.4
PANEL_Y = 1.55
PANEL_X = [-5.0, -1.45, 2.0, 5.35]
PANEL_R = 0.95                # half-size of a panel
SCALE = 0.8                   # screen units per unit field
CHAIN_POS = np.array([0.0, -2.75, 0])


def rot(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], complex)


# Each stage, in the order the wave meets it. Chosen so every panel changes
# visibly: a rotation, a lag, a shrink, then a stretch with a phase offset
# between x and y (an ellipse).
E0 = np.array([np.cos(30 * DEGREES), np.sin(30 * DEGREES)], complex)
K = np.exp(-0.6j) * np.eye(2)                         # free space: a delay
Z = np.exp(-1.3j) * np.eye(2)                         # ionosphere: more delay
F = rot(40 * DEGREES)                                 # Faraday rotation
P = rot(-25 * DEGREES)                                # parallactic angle
E = 0.7 * np.eye(2)                                   # primary beam
D = np.array([[1, 0.3j], [0.3j, 1]])                  # leakage
G = np.diag([1.35, 0.8 * np.exp(-0.6j)])              # receiver gains

STATES = [K @ E0, F @ Z @ K @ E0, E @ P @ F @ Z @ K @ E0,
          G @ D @ E @ P @ F @ Z @ K @ E0]
PANEL_LABELS = ["from the source", "after the ionosphere",
                "after the dish", "at the receiver"]
CHAIN = [r"\mathbf{J}", r"=", "G", "D", "E", "P", "F", "Z", "K"]
STAGE_COLORS = {"K": FRONT, "Z": SIG_P, "F": SIG_P, "P": FRONT,
                "E": FRONT, "D": SIG_P, "G": SIG_P}


def field(v, t):
    """Instantaneous field vector (screen units) of complex state v."""
    e = np.real(v * np.exp(-1j * OMEGA * t))
    return SCALE * np.array([e[0], e[1], 0.0])


class JourneyOfAWave(Scene):
    standalone = True   # title / closing cards (the deck wrapper turns them off)

    def construct(self):
        self.setup_trackers()
        self.cap = None
        if self.standalone:
            self.scene_title()
        self.beat_polarisation()
        self.beat_path()
        self.beat_space()
        self.beat_ionosphere()
        self.beat_dish()
        self.beat_receiver()
        self.beat_chain()
        self.beat_order()
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
        self.front = ValueTracker(X_SRC + 0.3)   # how far the ribbon has got

    def t_now(self):
        return self.clock.get_value()

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
    def make_panel(self, i, color=SIG_Q):
        c = np.array([PANEL_X[i], PANEL_Y, 0])
        v = STATES[i]
        box = RoundedRectangle(width=2 * PANEL_R, height=2 * PANEL_R,
                               corner_radius=0.12, stroke_color=MUTED,
                               stroke_width=2).move_to(c)
        axes = VGroup(
            Line(c + 0.8 * PANEL_R * LEFT, c + 0.8 * PANEL_R * RIGHT),
            Line(c + 0.8 * PANEL_R * DOWN, c + 0.8 * PANEL_R * UP),
        ).set_stroke(MUTED, 1, opacity=0.5)
        ts = np.linspace(0, T, 80)
        trace = VMobject().set_points_as_corners(
            [c + field(v, t) for t in ts]).set_stroke(color, 2, opacity=0.45)
        label = Text(PANEL_LABELS[i], font_size=20, color=MUTED).next_to(
            box, UP, buff=0.12)

        def arrow():
            tip = c + field(v, self.t_now())
            g = VGroup(Line(c, tip, stroke_width=5, color=color),
                       Dot(tip, radius=0.06, color=color))
            return g

        live = always_redraw(arrow)
        return VGroup(box, axes, trace, label), live

    def show_panel(self, i, color=SIG_Q):
        static, live = self.make_panel(i, color)
        self.add(live)
        self.play(FadeIn(static), FadeIn(live), run_time=0.8)
        self.panels.append(VGroup(static, live))

    def make_ribbon(self):
        def ribbon():
            x1 = self.front.get_value()
            xs = np.linspace(X_SRC + 0.3, max(x1, X_SRC + 0.31), 300)
            t = self.t_now()
            amp = np.where(xs < X_DISH, 0.14, 0.1)
            ys = PATH_Y + amp * np.sin(2 * PI * (xs - C_RIB * t) / LAM)
            m = VMobject().set_points_smoothly(
                [np.array([x, y, 0]) for x, y in zip(xs, ys)])
            return m.set_stroke(SIG_Q, 3, opacity=0.9)
        return always_redraw(ribbon)

    def make_cloud(self):
        parts = [(0, 0, 0.55), (-0.5, -0.1, 0.4), (0.5, -0.1, 0.42),
                 (-0.2, 0.3, 0.38), (0.3, 0.3, 0.35)]
        return VGroup(*[
            Circle(radius=r, stroke_width=0, fill_color=SIG_P,
                   fill_opacity=0.28).move_to([X_CLOUD + x, PATH_Y + y, 0])
            for x, y, r in parts])

    def make_dish(self):
        top = np.array([X_DISH, PATH_Y + 0.75, 0])
        bot = np.array([X_DISH, PATH_Y - 0.75, 0])
        dish = ArcBetweenPoints(top, bot, angle=-PI / 2.5, color=SIG_P,
                                stroke_width=6)
        feed = Dot([X_DISH - 0.55, PATH_Y, 0], radius=0.07, color=SIG_P)
        struts = VGroup(Line(top, feed.get_center()),
                        Line(bot, feed.get_center())).set_stroke(SIG_P, 2)
        return VGroup(dish, struts, feed)

    def make_receiver(self):
        box = RoundedRectangle(width=1.3, height=0.9, corner_radius=0.1,
                               color=FRONT, stroke_width=3).move_to(
            [X_RX, PATH_Y, 0])
        tri = Triangle(color=FRONT, stroke_width=3).scale(0.25).rotate(-PI / 2)
        return VGroup(box, tri.move_to(box))

    # -- beats ----------------------------------------------------------
    def scene_title(self):
        title = Text("The Journey of a Wave", font_size=44, color=FRONT)
        sub = Text("every effect on the way is a Jones matrix", font_size=28,
                   color=MUTED).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

    def beat_polarisation(self):
        self.panels = []
        self.show_caption("Light wiggles in a direction: its polarisation")
        star = Star(5, outer_radius=0.3, inner_radius=0.13, color=SIG_Q,
                    fill_opacity=1, stroke_width=0).move_to([X_SRC, PATH_Y, 0])
        self.star = star
        self.play(FadeIn(star, scale=0.5), run_time=0.6)
        self.play(self.rate.animate.set_value(1), run_time=0.3)
        self.show_panel(0)
        e = MathTex(r"\mathbf{e} = \begin{bmatrix} e_x \\ e_y \end{bmatrix}",
                    font_size=36, color=SIG_Q).next_to(
            self.panels[0], DOWN, buff=0.35)
        note = Text("two numbers: the wiggle along x and along y",
                    font_size=22, color=MUTED).next_to(e, RIGHT, buff=0.4)
        self.e_note = VGroup(e, note)
        self.play(Write(e), FadeIn(note), run_time=1.2)
        self.wait(T)

    def beat_path(self):
        self.show_caption("Every effect on the way changes the wiggle")
        self.play(FadeOut(self.e_note), run_time=0.5)
        line = DashedLine([X_SRC + 0.3, PATH_Y, 0], [X_OUT - 0.3, PATH_Y, 0],
                          color=MUTED, stroke_width=2, dash_length=0.1
                          ).set_opacity(0.5)
        self.cloud = self.make_cloud()
        self.dish = self.make_dish()
        self.rx = self.make_receiver()
        names = VGroup(*[
            Text(t, font_size=20, color=MUTED).move_to([x, PATH_Y - 1.05, 0])
            for t, x in [("space", (X_SRC + X_CLOUD) / 2),
                         ("ionosphere", X_CLOUD), ("dish", X_DISH),
                         ("receiver", X_RX)]])
        self.play(Create(line), run_time=0.8)
        self.play(FadeIn(self.cloud), FadeIn(self.dish), FadeIn(self.rx),
                  FadeIn(names), run_time=1.0)
        self.ribbon = self.make_ribbon()
        self.add(self.ribbon)
        self.chain = MathTex(*CHAIN, font_size=54, color=FRONT).move_to(
            CHAIN_POS)
        for i, tex in enumerate(CHAIN):
            if tex in STAGE_COLORS:
                self.chain[i].set_color(STAGE_COLORS[tex])
        self.wait(T)

    def stage_letters(self, letters, x):
        """Letter tags above a zone, and the same letters into the chain."""
        tags = VGroup(*[MathTex(l, font_size=40, color=STAGE_COLORS[l])
                        for l in letters]).arrange(RIGHT, buff=0.25).move_to(
            [x, PATH_Y + 0.95, 0])
        anims = []
        for l, tag in zip(letters, tags):
            target = self.chain[CHAIN.index(l)]
            anims.append(TransformFromCopy(tag, target))
        self.play(FadeIn(tags, shift=0.2 * DOWN), run_time=0.6)
        self.play(*anims, run_time=1.0)

    def beat_space(self):
        self.show_caption("Travelling through space only delays it  (K)")
        self.play(self.front.animate.set_value(X_CLOUD - 0.7), run_time=2.0,
                  rate_func=linear)
        self.stage_letters(["K"], (X_SRC + X_CLOUD) / 2)
        self.wait(T)

    def beat_ionosphere(self):
        self.show_caption("The ionosphere delays it more (Z) and twists it (F)")
        self.play(self.front.animate.set_value(X_DISH - 0.6), run_time=2.0,
                  rate_func=linear)
        self.show_panel(1)
        self.stage_letters(["Z", "F"], X_CLOUD)
        self.wait(T)

    def beat_dish(self):
        self.show_caption("The dish turns against the sky (P), and its beam "
                          "favours some directions (E)")
        self.play(self.front.animate.set_value(X_RX - 0.65), run_time=2.0,
                  rate_func=linear)
        self.show_panel(2)
        self.stage_letters(["P", "E"], X_DISH)
        self.wait(T)

    def beat_receiver(self):
        self.show_caption("The receiver leaks a little x into y (D), and "
                          "amplifies each differently (G)")
        self.play(self.front.animate.set_value(X_OUT - 0.3), run_time=1.6,
                  rate_func=linear)
        self.show_panel(3, color=GOOD)
        self.stage_letters(["D", "G"], X_RX)
        v = MathTex(r"\mathbf{v}", font_size=40, color=GOOD).move_to(
            [X_OUT + 0.05, PATH_Y + 0.45, 0])
        self.play(FadeIn(v), run_time=0.5)
        self.v_tag = v
        self.wait(T)

    def beat_chain(self):
        self.show_caption("Each effect is a 2×2 Jones matrix: chain them all")
        self.play(FadeIn(self.chain[0]), FadeIn(self.chain[1]), run_time=0.8)
        rhs = MathTex(r"\mathbf{v} = \mathbf{J}\,\mathbf{e}", font_size=48,
                      color=FRONT).next_to(self.chain, RIGHT, buff=1.2)
        rhs[0][0].set_color(GOOD)
        rhs[0][-1].set_color(SIG_Q)
        mat = MathTex(r"\begin{bmatrix} j_{11} & j_{12} \\ j_{21} & j_{22}"
                      r"\end{bmatrix}", font_size=36, color=MUTED).next_to(
            self.chain, LEFT, buff=1.2)
        self.play(Write(rhs), FadeIn(mat), run_time=1.2)
        self.chain_extra = VGroup(rhs, mat)
        self.wait(T)

    def beat_order(self):
        self.show_caption("Order matters: rotate-then-squash is not squash-then-rotate")
        everything = [m for m in self.mobjects if m is not self.clock
                      and m is not self.cap]
        self.play(*[FadeOut(m) for m in everything], run_time=0.8)
        self.play(self.rate.animate.set_value(0), run_time=0.1)
        self.clear_updaters_on_panels()

        def demo(y, first, second, labels):
            start = Square(1.2, color=SIG_Q, fill_opacity=0.25).move_to(
                [-4.5, y, 0])
            mark = Dot(start.get_corner(UR), color=SIG_Q, radius=0.08)
            a = VGroup(start, mark)
            b = a.copy().move_to([-0.5, y, 0])
            c = a.copy().move_to([3.8, y, 0])
            ar1 = Arrow([-3.5, y, 0], [-1.6, y, 0], color=MUTED, buff=0)
            ar2 = Arrow([0.6, y, 0], [2.5, y, 0], color=MUTED, buff=0)
            t1 = Text(labels[0], font_size=22, color=MUTED).next_to(ar1, UP, 0.1)
            t2 = Text(labels[1], font_size=22, color=MUTED).next_to(ar2, UP, 0.1)
            return a, b, c, VGroup(ar1, ar2, t1, t2), first, second

        def squash(m):
            return m.stretch(0.45, 1)

        def turn(m):
            return m.rotate(40 * DEGREES)

        rows = [demo(1.2, turn, squash, ("rotate", "squash")),
                demo(-1.8, squash, turn, ("squash", "rotate"))]
        for a, b, c, deco, f1, f2 in rows:
            self.play(FadeIn(a), FadeIn(deco), run_time=0.6)
            b2 = f1(b.copy())
            self.play(TransformFromCopy(a, b2), run_time=0.9)
            c2 = f2(f1(c.copy()))
            self.play(TransformFromCopy(b2, c2), run_time=0.9)
        neq = MathTex(r"\neq", font_size=72, color=BAD).move_to([3.8, -0.3, 0])
        self.play(FadeIn(neq, scale=0.5), run_time=0.6)
        self.wait(1.0)

    def clear_updaters_on_panels(self):
        for p in self.panels:
            p[1].clear_updaters()
        self.ribbon.clear_updaters()

    def scene_close(self):
        line1 = Text("Every effect on the way is a Jones matrix —",
                     font_size=36, color=FRONT)
        line2 = Text("the RIME keeps track of them all.", font_size=36,
                     color=FRONT)
        msg = VGroup(line1, line2).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        tease = Text("next: two antennas, one equation", font_size=26,
                     color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.play(FadeOut(Group(*[m for m in self.mobjects
                                  if m is not self.clock])), run_time=0.8)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.0)
        self.play(FadeIn(tease), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(tease), run_time=1.0)
        self.wait(0.5)
