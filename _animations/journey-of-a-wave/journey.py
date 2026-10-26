"""The Journey of a Wave — every effect on the way is a Jones matrix.

Episode of the interferometry explainer series (see scenes.md for the plan).
Follows "What Can Happen to a Wiggle" (_animations/polarisation-ellipse) and
uses its four moves: delay, twist, shrink, uneven delay.

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
LAM = 2.0                     # wavelength of the travelling pattern on screen
HOLD = 3 * T

# ----- layout -----
PATH_Y = -1.05
X_SRC, X_CLOUD, X_DISH, X_RX, X_OUT = -6.3, -2.9, 0.0, 3.1, 6.2
SPACE = (-5.9, -4.0)          # where each effect builds up along the path
CLOUD = (-3.9, -1.9)
DISH = (-0.45, 0.45)
RX_D = (2.3, 3.1)             # feed: leakage
RX_G = (3.1, 3.9)             # electronics: gains
RX_HALF = 0.85                # receiver box half-width
FRONT_START = -5.95

PANEL_C = np.array([0.0, 1.6, 0])
PANEL_R = 1.15                # half-size of the panel
SCALE = 1.0                   # panel screen units per unit field
CARD_POS = np.array([3.3, 1.6, 0])
NOTE_POS = np.array([-4.0, 1.6, 0])
GLYPH_DX = 0.4                # spacing of the wiggle strip
GLYPH_S = 0.23                # strip screen units per unit field
ZOOM_Y = 1.15                 # the magnified strip above the cloud (F beat)
ZOOM_X = np.linspace(-6.0, -2.2, 6)
ZOOM_S = 0.36
CHAIN_POS = np.array([0.0, -2.8, 0])

# ----- the stages, in the order the wave meets them -----
THETA0 = -20 * DEGREES        # the source: linear polarisation
PHI_K = 70 * DEGREES          # space: delay
PHI_Z = 60 * DEGREES          # ionosphere: more delay
ANG_F = 50 * DEGREES          # ionosphere: Faraday twist (builds up through the cloud)
ANG_P = 20 * DEGREES          # dish: parallactic twist, same way, so nothing cancels
AMP_E = 0.7                   # dish: primary beam
LEAK_D = 0.3                  # feed: leakage, a quarter wave out of step
GAIN_G = (1.15, 0.85)         # electronics: x and y amplified differently ...
DELAY_G = 60 * DEGREES        # ... and y delayed more than x

CHAIN = [r"\mathbf{J}", r"=", "G", "D", "E", "P", "F", "Z", "K"]
STAGE_COLORS = {"K": FRONT, "Z": SIG_P, "F": SIG_P, "P": FRONT,
                "E": FRONT, "D": SIG_P, "G": SIG_P}


def rot(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], complex)


def ramp(x, zone):
    a, b = zone
    s = np.clip((x - a) / (b - a), 0.0, 1.0)
    return s * s * (3 - 2 * s)          # smooth in and out


def jones_upto(x, f_on=1.0, e_on=1.0, g_on=1.0):
    """The Jones chain from the source to position x along the path.

    Each effect builds up across its zone; the *_on switches let a second
    effect in the same place (F after Z, E after P, G after D) be shown on
    its own beat. Multiplying by e^{+i phi} is a true delay for the field
    Re(v e^{-i omega t})."""
    k = np.exp(1j * PHI_K * ramp(x, SPACE)) * np.eye(2)
    c = ramp(x, CLOUD)
    z = np.exp(1j * PHI_Z * c) * np.eye(2)
    f = rot(ANG_F * c * f_on)
    d_ = ramp(x, DISH)
    p = rot(ANG_P * d_)
    e = (1 - (1 - AMP_E) * d_ * e_on) * np.eye(2)
    l = LEAK_D * ramp(x, RX_D)
    d = np.array([[1, 1j * l], [1j * l, 1]])
    g_ = ramp(x, RX_G) * g_on
    g = np.diag([1 + (GAIN_G[0] - 1) * g_,
                 (1 + (GAIN_G[1] - 1) * g_) * np.exp(1j * DELAY_G * g_)])
    return g @ d @ e @ p @ f @ z @ k


E0 = np.array([np.cos(THETA0), np.sin(THETA0)], complex)


def field(v, t):
    return np.real(v * np.exp(-1j * OMEGA * t))


class JourneyOfAWave(Scene):
    standalone = True   # title / closing cards (the deck wrapper turns them off)

    def construct(self):
        self.setup_trackers()
        self.cap = None
        self.card = None
        if self.standalone:
            self.scene_title()
        self.beat_source()
        self.beat_path()
        self.beat_space()
        self.beat_ionosphere_delay()
        self.beat_faraday()
        self.beat_parallactic()
        self.beat_beam()
        self.beat_leakage()
        self.beat_gains()
        self.beat_why_receiver()
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
        self.front = ValueTracker(FRONT_START)   # how far the wave has got
        self.f_on = ValueTracker(0.0)
        self.e_on = ValueTracker(0.0)
        self.g_on = ValueTracker(0.0)
        self.ghost = None                         # state before the current step
        self.ghost_on = ValueTracker(0.0)

    def t_now(self):
        return self.clock.get_value()

    def switches(self):
        return dict(f_on=self.f_on.get_value(), e_on=self.e_on.get_value(),
                    g_on=self.g_on.get_value())

    def v_at(self, x):
        return jones_upto(x, **self.switches()) @ E0

    def v_front(self):
        return self.v_at(self.front.get_value())

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

    # -- the wiggle strip along the path ----------------------------------
    def glyph_xs(self):
        xs = np.arange(FRONT_START, X_OUT + 0.01, GLYPH_DX)
        keep = [x for x in xs
                if abs(x - X_DISH) > 0.3 and abs(x - X_RX) > RX_HALF + 0.15]
        return np.array(keep)

    def make_strip(self):
        xs = self.glyph_xs()
        k = 2 * PI / LAM

        def draw():
            t = self.t_now()
            x1 = self.front.get_value()
            out = VGroup()
            for x in xs[xs <= x1 + 1e-6]:
                v = self.v_at(x)
                col = GOOD if x > X_RX else SIG_Q
                c = np.array([x, PATH_Y, 0])
                pts = [c + GLYPH_S * np.r_[field(v, s), 0]
                       for s in np.linspace(0, T, 24)]
                shape = VMobject().set_points_as_corners(pts).set_stroke(
                    col, 2.2, opacity=0.75)
                # the travelling pattern: phase advances along the path
                tip = c + GLYPH_S * np.r_[field(v * np.exp(1j * k * x), t), 0]
                out.add(shape, Dot(tip, radius=0.05, color=col))
            return out
        return always_redraw(draw)

    # -- the panel: the wiggle at the wavefront ----------------------------
    def loop_curve(self, v, n=90):
        pts = [PANEL_C + SCALE * np.r_[field(v, s), 0]
               for s in np.linspace(0, T, n)]
        return VMobject().set_points_as_corners(pts)

    def make_panel(self):
        box = RoundedRectangle(width=2 * PANEL_R, height=2 * PANEL_R,
                               corner_radius=0.12, stroke_color=MUTED,
                               stroke_width=2).move_to(PANEL_C)
        axes = VGroup(
            Line(PANEL_C + 0.85 * PANEL_R * LEFT, PANEL_C + 0.85 * PANEL_R * RIGHT),
            Line(PANEL_C + 0.85 * PANEL_R * DOWN, PANEL_C + 0.85 * PANEL_R * UP),
        ).set_stroke(MUTED, 1, opacity=0.5)
        label = Text("the wiggle at the wavefront", font_size=20,
                     color=MUTED).next_to(box, UP, buff=0.12)
        return VGroup(box, axes, label)

    def make_live(self):
        def draw():
            v = self.v_front()
            col = GOOD if self.front.get_value() > X_RX else SIG_Q
            tip = PANEL_C + SCALE * np.r_[field(v, self.t_now()), 0]
            return VGroup(self.loop_curve(v).set_stroke(col, 2.5, opacity=0.55),
                          Line(PANEL_C, tip, stroke_width=5, color=col),
                          Dot(tip, radius=0.07, color=col))
        return always_redraw(draw)

    def make_ghost(self):
        def draw():
            op = self.ghost_on.get_value()
            if self.ghost is None or op == 0:
                return VGroup()
            tip = PANEL_C + SCALE * np.r_[field(self.ghost, self.t_now()), 0]
            ring = Circle(radius=0.1).move_to(tip).set_stroke(
                FRONT, 2.2, opacity=0.85 * op)
            return VGroup(self.loop_curve(self.ghost).set_stroke(
                MUTED, 2, opacity=0.5 * op), ring)
        return always_redraw(draw)

    def make_link(self):
        """A faint line from the wavefront up to the panel."""
        def draw():
            x = self.front.get_value()
            return DashedLine([x, PATH_Y + 0.3, 0],
                              PANEL_C + PANEL_R * DOWN + 0.05 * DOWN,
                              dash_length=0.08, stroke_width=1.5,
                              color=MUTED).set_opacity(0.45)
        return always_redraw(draw)

    def snapshot_ghost(self):
        self.ghost = self.v_front()
        self.ghost_on.set_value(1.0)

    def move_card(self, word, sub, color=FRONT):
        w = Text(word, font_size=36, color=color, weight=BOLD)
        s = Text(sub, font_size=21, color=MUTED)
        return VGroup(w, s).arrange(DOWN, buff=0.12).move_to(CARD_POS)

    def show_card(self, card):
        if self.card is not None:
            self.play(FadeOut(self.card), run_time=0.3)
        self.play(FadeIn(card, shift=0.15 * UP), run_time=0.5)
        self.card = card

    def make_zoom(self):
        """The wiggle at six depths through the cloud, magnified above it."""
        depths = np.linspace(CLOUD[0], CLOUD[1], len(ZOOM_X))
        cross = VGroup(*[VGroup(
            Line([x - 0.42, ZOOM_Y, 0], [x + 0.42, ZOOM_Y, 0]),
            Line([x, ZOOM_Y - 0.42, 0], [x, ZOOM_Y + 0.42, 0]))
            for x in ZOOM_X]).set_stroke(MUTED, 1, opacity=0.35)
        note = Text("the deeper in, the more it twists",
                    font_size=21, color=MUTED).move_to(
            [np.mean(ZOOM_X), ZOOM_Y + 0.7, 0])
        arrow = Arrow([ZOOM_X[0], ZOOM_Y - 0.62, 0], [ZOOM_X[-1], ZOOM_Y - 0.62, 0],
                      buff=0, stroke_width=2, color=MUTED,
                      max_tip_length_to_length_ratio=0.04)
        ends = VGroup(
            Text("in", font_size=18, color=MUTED).next_to(arrow, LEFT, 0.12),
            Text("out", font_size=18, color=MUTED).next_to(arrow, RIGHT, 0.12))

        def draw():
            t = self.t_now()
            out = VGroup()
            for x, depth in zip(ZOOM_X, depths):
                v = self.v_at(depth)
                c = np.array([x, ZOOM_Y, 0])
                pts = [c + ZOOM_S * np.r_[field(v, s), 0]
                       for s in np.linspace(0, T, 40)]
                tip = c + ZOOM_S * np.r_[field(v, t), 0]
                out.add(VMobject().set_points_as_corners(pts).set_stroke(
                            SIG_Q, 2.5, opacity=0.8),
                        Line(c, tip, stroke_width=3.5, color=SIG_Q),
                        Dot(tip, radius=0.05, color=SIG_Q))
            return out
        return VGroup(cross, note, arrow, ends), always_redraw(draw)

    # -- scenery -----------------------------------------------------------
    def make_cloud(self):
        parts = [(0, 0, 0.62), (-0.6, -0.1, 0.45), (0.6, -0.1, 0.48),
                 (-0.25, 0.35, 0.42), (0.35, 0.33, 0.4)]
        return VGroup(*[
            Circle(radius=r, stroke_width=0, fill_color=SIG_P,
                   fill_opacity=0.14).move_to([X_CLOUD + x, PATH_Y + y, 0])
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
        box = RoundedRectangle(width=2 * RX_HALF, height=0.9, corner_radius=0.1,
                               color=FRONT, stroke_width=3).move_to(
            [X_RX, PATH_Y, 0])
        tri = Triangle(color=FRONT, stroke_width=3).scale(0.25).rotate(-PI / 2)
        return VGroup(box, tri.move_to(box))

    def stage_letters(self, letters, x):
        """Letter tags above a zone, and the same letters into the chain."""
        tags = VGroup(*[MathTex(l, font_size=40, color=STAGE_COLORS[l])
                        for l in letters]).arrange(RIGHT, buff=0.25)
        tags.move_to([x, PATH_Y + 0.95, 0])
        self.tags.update({l: t for l, t in zip(letters, tags)})
        anims = [TransformFromCopy(tag, self.chain[CHAIN.index(l)])
                 for l, tag in zip(letters, tags)]
        self.play(FadeIn(tags, shift=0.2 * DOWN), run_time=0.5)
        self.play(*anims, run_time=0.9)

    def add_tag(self, letter, x):
        """A second letter joins a zone that already has one."""
        old = [t for l, t in self.tags.items() if abs(t.get_x() - x) < 0.6]
        tag = MathTex(letter, font_size=40, color=STAGE_COLORS[letter])
        row = VGroup(*old, tag.copy())
        target = row.copy().arrange(RIGHT, buff=0.25).move_to(
            [x, PATH_Y + 0.95, 0])
        tag.move_to(target[-1])
        self.play(*[o.animate.move_to(tg) for o, tg in zip(old, target)],
                  FadeIn(tag, shift=0.2 * DOWN), run_time=0.5)
        self.tags[letter] = tag
        self.play(TransformFromCopy(tag, self.chain[CHAIN.index(letter)]),
                  run_time=0.9)

    def travel(self, x, run_time=2.5):
        self.play(self.front.animate.set_value(x), run_time=run_time,
                  rate_func=linear)

    # -- beats -------------------------------------------------------------
    def scene_title(self):
        title = Text("The Journey of a Wave", font_size=44, color=FRONT)
        sub = Text("every effect on the way is a Jones matrix", font_size=28,
                   color=MUTED).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

    def beat_source(self):
        self.tags = {}
        self.show_caption("Follow one wave from a source to a receiver")
        star = Star(5, outer_radius=0.3, inner_radius=0.13, color=SIG_Q,
                    fill_opacity=1, stroke_width=0).move_to([X_SRC, PATH_Y, 0])
        self.panel = self.make_panel()
        self.live = self.make_live()
        self.ghost_mob = self.make_ghost()
        self.strip = self.make_strip()
        self.link = self.make_link()
        self.add(self.live, self.ghost_mob, self.strip, self.link)
        self.play(FadeIn(star, scale=0.5), FadeIn(self.panel),
                  FadeIn(self.live), FadeIn(self.strip), FadeIn(self.link),
                  run_time=0.9)
        self.play(self.rate.animate.set_value(1), run_time=0.3)
        e = MathTex(r"\mathbf{e} = \begin{bmatrix} e_x \\ e_y \end{bmatrix}",
                    font_size=38, color=SIG_Q)
        note = Text("the x wiggle and the y wiggle", font_size=21,
                    color=MUTED).next_to(e, DOWN, buff=0.2)
        self.e_note = VGroup(e, note).move_to(NOTE_POS)
        self.play(Write(e), FadeIn(note), run_time=1.0)
        self.wait(T)

    def beat_path(self):
        self.show_caption("Every effect on the way changes the wiggle")
        line = DashedLine([X_SRC + 0.3, PATH_Y, 0], [X_OUT, PATH_Y, 0],
                          color=MUTED, stroke_width=1.5, dash_length=0.1
                          ).set_opacity(0.35)
        names = VGroup(*[
            Text(t, font_size=20, color=MUTED).move_to([x, PATH_Y - 1.0, 0])
            for t, x in [("space", np.mean(SPACE)), ("ionosphere", X_CLOUD),
                         ("dish", X_DISH), ("receiver", X_RX)]])
        self.chain = MathTex(*CHAIN, font_size=54, color=FRONT).move_to(
            CHAIN_POS)
        for i, tex in enumerate(CHAIN):
            if tex in STAGE_COLORS:
                self.chain[i].set_color(STAGE_COLORS[tex])
        self.play(Create(line), run_time=0.7)
        self.play(FadeIn(self.make_cloud()), FadeIn(self.make_dish()),
                  FadeIn(self.make_receiver()), FadeIn(names), run_time=1.0)
        self.wait(T)

    def beat_space(self):
        self.show_caption("Travelling through space only delays it (K)")
        self.play(FadeOut(self.e_note), run_time=0.4)
        self.snapshot_ghost()
        self.show_card(self.move_card("delay", "same line, later"))
        self.travel(SPACE[1] + 0.05)
        self.stage_letters(["K"], np.mean(SPACE))
        self.wait(T)

    def beat_ionosphere_delay(self):
        self.show_caption("The ionosphere delays it a little more (Z)")
        self.snapshot_ghost()
        self.show_card(self.move_card("delay", "same line, later"))
        self.travel(CLOUD[1] + 0.05)
        self.stage_letters(["Z"], X_CLOUD)
        self.wait(T)

    def beat_faraday(self):
        self.show_caption("The Earth's magnetic field in the ionosphere "
                          "twists it (F)")
        self.snapshot_ghost()
        self.show_card(self.move_card("twist", "Faraday rotation"))
        static, live = self.make_zoom()
        self.zoom = VGroup(static, live)
        self.add(live)
        self.play(FadeIn(static), FadeIn(live), run_time=0.8)
        # the twist builds up with depth: deeper glyphs turn further
        self.play(self.f_on.animate.set_value(1), run_time=3.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.add_tag("F", X_CLOUD)
        self.wait(T)

    def beat_parallactic(self):
        self.show_caption("The dish turns as it tracks the sky: "
                          "another twist (P)")
        self.play(FadeOut(self.zoom), run_time=0.5)
        self.zoom[1].clear_updaters()
        self.remove(self.zoom[1])
        self.snapshot_ghost()
        self.show_card(self.move_card("twist", "parallactic angle"))
        self.travel(DISH[1] + 0.05)
        self.stage_letters(["P"], X_DISH)
        self.wait(T)

    def beat_beam(self):
        self.show_caption("The beam sees off-centre sources more weakly (E)")
        self.snapshot_ghost()
        self.show_card(self.move_card("shrink", "primary beam"))
        self.play(self.e_on.animate.set_value(1), run_time=2.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.add_tag("E", X_DISH)
        self.wait(T)

    def beat_leakage(self):
        self.show_caption("The feed leaks a little x into y, out of step (D)")
        self.snapshot_ghost()
        self.show_card(self.move_card("leak", "the line starts to open",
                                      color=GOOD))
        self.travel(X_OUT, run_time=3.0)
        self.stage_letters(["D"], X_RX)
        self.wait(T)

    def beat_gains(self):
        self.show_caption("The electronics amplify and delay x and y "
                          "differently (G)")
        self.snapshot_ghost()
        self.show_card(self.move_card("uneven delay", "an ellipse", color=GOOD))
        self.play(self.g_on.animate.set_value(1), run_time=2.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.add_tag("G", X_RX)
        v = MathTex(r"\mathbf{v}", font_size=40, color=GOOD).move_to(
            [X_OUT + 0.05, PATH_Y + 0.45, 0])
        self.play(FadeIn(v), run_time=0.5)
        self.wait(T)

    def beat_why_receiver(self):
        self.show_caption("Only D and G treat x and y differently: "
                          "that is why the ellipse appears here")
        self.play(FadeOut(self.ghost_mob), run_time=0.4)
        self.ghost_on.set_value(0)
        lines = [l for l in self.tags if l not in "DG"]
        self.play(*[self.tags[l].animate.set_opacity(0.3) for l in lines],
                  *[Indicate(self.tags[l], color=GOOD, scale_factor=1.3)
                    for l in "DG"], run_time=1.2)
        self.play(*[self.tags[l].animate.set_opacity(1) for l in lines],
                  run_time=0.6)
        self.wait(T)

    def beat_chain(self):
        self.show_caption("Each effect is a 2×2 Jones matrix: chain them all")
        self.play(FadeOut(self.card), run_time=0.4)
        self.card = None
        self.play(FadeIn(self.chain[0]), FadeIn(self.chain[1]), run_time=0.8)
        rhs = MathTex(r"\mathbf{v} = \mathbf{J}\,\mathbf{e}", font_size=48,
                      color=FRONT).next_to(self.chain, RIGHT, buff=1.2)
        rhs[0][0].set_color(GOOD)
        rhs[0][-1].set_color(SIG_Q)
        mat = MathTex(r"\begin{bmatrix} j_{11} & j_{12} \\ j_{21} & j_{22}"
                      r"\end{bmatrix}", font_size=36, color=MUTED).next_to(
            self.chain, LEFT, buff=1.2)
        self.play(Write(rhs), FadeIn(mat), run_time=1.2)
        self.wait(T)

    def beat_order(self):
        self.show_caption("Order matters: rotate-then-squash is not squash-then-rotate")
        everything = [m for m in self.mobjects if m is not self.clock
                      and m is not self.cap]
        self.play(*[FadeOut(m) for m in everything], run_time=0.8)
        self.play(self.rate.animate.set_value(0), run_time=0.1)
        for m in (self.live, self.ghost_mob, self.strip, self.link):
            m.clear_updaters()
            self.remove(m)

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
