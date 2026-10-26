"""The RIME on a two-element interferometer — what each term means.

Episode of the interferometry explainer series (see scenes.md for the plan).
Two scenes share one diagram: the terms of the scalar measurement equation
fly onto the parts of the interferometer they describe (RimeOnTheInterferometer),
and the same picture comes back at the end of the RIME lecture to show what
is left to solve for TART (RimeForTart).

Render (from this directory):
    ../preview.sh rime_interferometer.py RimeOnTheInterferometer
    ../final.sh rime_interferometer.py RimeOnTheInterferometer
    ../preview.sh rime_interferometer.py OneNumberToABox     # G (one number) to J (a 2x2 box)
"""

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # instrument: antennas, gains
SIG_Q = "#d29922"   # sky brightness
GOOD = "#3fb950"    # measurements / known
BAD = "#f85149"     # mismatch / warnings
FRONT = "#c9d1d9"   # annotations / text
MUTED = "#8b949e"

config.background_color = BG

# ----- diagram layout (screen units) -----
STAR = np.array([-3.5, 2.55, 0])
DISH_P = np.array([-5.6, 0.35, 0])      # base of antenna p
DISH_Q = np.array([-1.4, 0.35, 0])
AMP_Y = -0.75                           # amplifier centre
WIRE_Y = -2.1                           # wires into the correlator
CORR = np.array([-3.5, WIRE_Y, 0])
COIL_X = (-5.3, -4.5)                  # delay line on p's wire
EQ_POS = np.array([3.7, 0.6, 0])

# where each term lands on the diagram
SPOT_V = np.array([-3.5, -3.4, 0])
SPOT_B = STAR + np.array([0.65, 0.0, 0])
SPOT_GP = np.array([DISH_P[0] - 0.8, AMP_Y, 0])
SPOT_GQ = np.array([DISH_Q[0] + 0.85, AMP_Y, 0])
SPOT_K = np.array([np.mean(COIL_X), WIRE_Y - 0.5, 0])

EXTRA_STARS = [(-6.5, 2.15, 0.12), (-5.1, 2.95, 0.09), (-2.1, 3.0, 0.1),
               (-0.6, 2.2, 0.13), (-5.8, 1.75, 0.08)]

EQ_ONE = [r"V_{pq}", r"=", r"G_p", r"B", r"G_q^*", r"K_{pq}"]
EQ_SUM = [r"V_{pq}", r"=", r"\sum_s", r"G_p", r"B_s", r"G_q^*", r"K_{pq,s}"]
TERM_COLORS = {r"V_{pq}": GOOD, r"G_p": SIG_P, r"G_q^*": SIG_P,
               r"B": SIG_Q, r"B_s": SIG_Q, r"K_{pq}": FRONT,
               r"K_{pq,s}": FRONT}


def make_antenna(pos, color, scale=1.35):
    dish = ArcBetweenPoints(pos + np.array([-0.42, 0.55, 0]),
                            pos + np.array([0.42, 0.55, 0]),
                            angle=-PI / 2.2, color=color, stroke_width=5)
    stand = Line(pos, pos + 0.42 * UP, color=color, stroke_width=5)
    feed = Dot(pos + 0.42 * UP, radius=0.05, color=color)
    return VGroup(dish, stand, feed).scale(scale, about_point=pos)


def make_star(pos, r=0.22, color=SIG_Q):
    return Star(5, outer_radius=r, inner_radius=0.42 * r, color=color,
                fill_opacity=1, stroke_width=0).move_to(pos)


def make_satellite(pos, s=1.0):
    body = Square(0.2 * s, color=FRONT, fill_opacity=1, stroke_width=0)
    wing = Rectangle(width=0.32 * s, height=0.13 * s, color=SIG_P,
                     fill_opacity=0.9, stroke_width=1.5, stroke_color=FRONT)
    left = wing.copy().next_to(body, LEFT, buff=0.04 * s)
    right = wing.copy().next_to(body, RIGHT, buff=0.04 * s)
    return VGroup(left, right, body).rotate(25 * DEGREES).move_to(pos)


def make_coil():
    x0, x1 = COIL_X
    xs = np.linspace(x0, x1, 120)
    pts = [np.array([x, WIRE_Y + 0.16 * np.sin((x - x0) / (x1 - x0) * 6 * PI), 0])
           for x in xs]
    coil = VMobject(stroke_color=FRONT, stroke_width=3)
    coil.set_points_as_corners(pts)
    return coil


def make_equation(parts, font_size=60):
    eq = MathTex(*parts, font_size=font_size, color=FRONT, arg_separator=r"\,")
    if eq.width > 6.3:
        eq.scale_to_fit_width(6.3)
    return eq.move_to(EQ_POS)


class RimeDiagram:
    """Shared pieces: the interferometer drawing, the equation and labels."""

    standalone = True   # title / closing cards (the deck wrapper turns them off)

    def caption(self, text, color=FRONT, **kwargs):
        return Text(text, font_size=27, color=color, **kwargs).to_edge(
            UP, buff=0.25
        )

    def show_caption(self, text, **kwargs):
        cap = self.caption(text, **kwargs)
        old = getattr(self, "cap", None)
        if old is not None:
            self.play(FadeOut(old), run_time=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        self.cap = cap
        return cap

    def build_diagram(self):
        ant_p = make_antenna(DISH_P, SIG_P)
        ant_q = make_antenna(DISH_Q, SIG_P)
        feed_p = DISH_P + 1.35 * 0.42 * UP
        feed_q = DISH_Q + 1.35 * 0.42 * UP
        star = make_star(STAR)
        rays = VGroup(*[
            DashedLine(STAR, f + 0.35 * UP, color=SIG_Q, stroke_width=2,
                       dash_length=0.12).set_opacity(0.7)
            for f in (feed_p, feed_q)
        ])

        def amp(x):
            tri = Triangle(color=FRONT, stroke_width=3).scale(0.28)
            return tri.rotate(PI).move_to([x, AMP_Y, 0])

        amp_p, amp_q = amp(DISH_P[0]), amp(DISH_Q[0])
        w = dict(color=MUTED, stroke_width=3)
        wires = VGroup(
            Line(DISH_P, amp_p.get_top(), **w),
            Line(DISH_Q, amp_q.get_top(), **w),
            Line(amp_p.get_bottom(), [DISH_P[0], WIRE_Y, 0], **w),
            Line([DISH_P[0], WIRE_Y, 0], [COIL_X[0], WIRE_Y, 0], **w),
            Line([COIL_X[1], WIRE_Y, 0], CORR + 0.8 * LEFT, **w),
            Line(amp_q.get_bottom(), [DISH_Q[0], WIRE_Y, 0], **w),
            Line([DISH_Q[0], WIRE_Y, 0], CORR + 0.8 * RIGHT, **w),
        )
        coil = make_coil()
        box = RoundedRectangle(width=1.6, height=0.8, corner_radius=0.12,
                               color=FRONT, stroke_width=3).move_to(CORR)
        ops = MathTex(r"\times", r"\langle\;\rangle", font_size=40,
                      color=FRONT).arrange(RIGHT, buff=0.3).move_to(CORR)
        out = Arrow(CORR + 0.4 * DOWN, CORR + 1.0 * DOWN, buff=0,
                    color=GOOD, stroke_width=4, max_tip_length_to_length_ratio=0.3)
        self.d = dict(star=star, rays=rays, ant_p=ant_p, ant_q=ant_q,
                      amp_p=amp_p, amp_q=amp_q, wires=wires, coil=coil,
                      box=box, ops=ops, out=out)
        return self.d

    def diagram_group(self):
        return VGroup(*self.d.values())

    def spot(self, tex):
        return {r"V_{pq}": SPOT_V, r"B": SPOT_B, r"B_s": SPOT_B,
                r"G_p": SPOT_GP, r"G_q^*": SPOT_GQ, r"K_{pq}": SPOT_K,
                r"K_{pq,s}": SPOT_K}[tex]

    def make_label(self, tex):
        return MathTex(tex, font_size=48,
                       color=TERM_COLORS[tex]).move_to(self.spot(tex))

    def title_card(self, title, sub):
        t = Text(title, font_size=44, color=FRONT)
        s = Text(sub, font_size=28, color=MUTED).next_to(t, DOWN, buff=0.3)
        self.play(FadeIn(t, shift=0.3 * UP), FadeIn(s), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(t), FadeOut(s), run_time=0.8)

    def closing_card(self, line1, line2, tease):
        l1 = Text(line1, font_size=40, color=FRONT)
        l2 = Text(line2, font_size=40, color=FRONT)
        msg = VGroup(l1, l2).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        te = Text(tease, font_size=26, color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.0)
        self.play(FadeIn(te), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(te), run_time=1.0)
        self.wait(0.5)


class RimeOnTheInterferometer(RimeDiagram, Scene):
    def construct(self):
        self.cap = None
        if self.standalone:
            self.title_card("The Measurement Equation",
                            "what each term means")
        self.beat_diagram()
        self.beat_equation()
        self.beat_terms()
        self.beat_many_sources()
        self.beat_inverse()
        if self.standalone:
            self.closing_card("Calibration finds the G's —",
                              "imaging finds the B's.",
                              "next: what is hiding inside G?")
        else:
            self.wait(0.5)

    def beat_diagram(self):
        d = self.build_diagram()
        self.show_caption("A two-element interferometer")
        self.play(FadeIn(d["star"], scale=0.5), run_time=0.6)
        self.play(Create(d["rays"]), FadeIn(d["ant_p"]), FadeIn(d["ant_q"]),
                  run_time=1.2)
        self.play(Create(d["wires"]), FadeIn(d["amp_p"]), FadeIn(d["amp_q"]),
                  Create(d["coil"]), run_time=1.4)
        self.play(Create(d["box"]), Write(d["ops"]), run_time=1.0)
        self.play(GrowArrow(d["out"]), run_time=0.6)
        self.wait(0.5)

    def beat_equation(self):
        self.show_caption("One equation says what comes out")
        self.eq = make_equation(EQ_ONE)
        self.play(Write(self.eq), run_time=1.6)
        self.wait(0.5)

    def fly(self, idx, extra=()):
        term = self.eq[idx]
        tex = EQ_ONE[idx]
        color = TERM_COLORS[tex]
        label = self.make_label(tex)
        self.play(term.animate.set_color(color), run_time=0.4)
        self.play(TransformFromCopy(term, label), *extra, run_time=1.3)
        self.labels[tex] = label

    def beat_terms(self):
        self.labels = {}
        d = self.d
        self.show_caption("V: the visibility — what the correlator gives us")
        self.fly(0, extra=[Indicate(d["box"], color=GOOD)])
        self.wait(0.5)

        self.show_caption("B: the brightness of the source — what we want to know")
        self.fly(3, extra=[Indicate(d["star"], color=SIG_Q, scale_factor=1.6)])
        self.wait(0.5)

        self.show_caption("G: what each antenna and its electronics do to the signal")
        self.fly(2, extra=[Indicate(d["amp_p"], color=SIG_P)])
        self.fly(4, extra=[Indicate(d["amp_q"], color=SIG_P)])
        self.wait(0.5)

        self.show_caption("K: the delay between the two antennas — pure geometry")
        self.fly(5, extra=[Indicate(d["coil"], color=FRONT)])
        self.wait(0.5)

    def beat_many_sources(self):
        self.show_caption("A real sky has many sources — add them all up")
        stars = VGroup(*[make_star((x, y, 0), r) for x, y, r in EXTRA_STARS])
        eq2 = make_equation(EQ_SUM)
        for i, tex in enumerate(EQ_SUM):
            if tex in TERM_COLORS:
                eq2[i].set_color(TERM_COLORS[tex])
        lab_b = self.make_label(r"B_s")
        lab_k = self.make_label(r"K_{pq,s}")
        self.play(LaggedStart(*[FadeIn(s, scale=0.3) for s in stars],
                              lag_ratio=0.2), run_time=1.4)
        self.play(TransformMatchingTex(self.eq, eq2),
                  Transform(self.labels[r"B"], lab_b),
                  Transform(self.labels[r"K_{pq}"], lab_k), run_time=1.5)
        self.eq = eq2
        self.extra_stars = stars
        self.wait(0.5)

    def beat_inverse(self):
        self.show_caption("Calibration finds the G's. Imaging finds the B's.")
        eq = self.eq
        box_g = VGroup(SurroundingRectangle(eq[3], color=SIG_P, buff=0.05),
                       SurroundingRectangle(eq[5], color=SIG_P, buff=0.05))
        box_b = SurroundingRectangle(eq[4], color=SIG_Q, buff=0.05)
        cal = Text("calibration", font_size=28, color=SIG_P).next_to(
            eq, DOWN, buff=0.6).set_x(box_g.get_x())
        img = Text("imaging", font_size=28, color=SIG_Q).next_to(
            eq, UP, buff=0.6).set_x(box_b.get_x())
        self.play(Create(box_g), FadeIn(cal, shift=0.2 * UP), run_time=1.0)
        self.play(Create(box_b), FadeIn(img, shift=0.2 * DOWN), run_time=1.0)
        self.wait(1.0)


class RimeForTart(RimeDiagram, Scene):
    """The same picture, at the end of the lecture: what TART solves for."""

    def construct(self):
        self.cap = None
        if self.standalone:
            self.title_card("The Measurement Equation for TART",
                            "what is left to solve for")
        self.beat_recap()
        self.beat_satellites()
        self.beat_geometry()
        self.beat_gains()
        self.beat_count()
        if self.standalone:
            self.closing_card("For TART, calibration means",
                              "one complex number per antenna.",
                              "")
        else:
            self.wait(0.5)

    def beat_recap(self):
        d = self.build_diagram()
        self.eq = make_equation(EQ_SUM)
        self.labels = {}
        for i, tex in enumerate(EQ_SUM):
            if tex in TERM_COLORS:
                self.eq[i].set_color(TERM_COLORS[tex])
                self.labels[tex] = self.make_label(tex)
        self.stars = VGroup(d["star"], *[make_star((x, y, 0), r)
                                         for x, y, r in EXTRA_STARS])
        d.pop("star")
        self.show_caption("Back to our picture")
        self.play(FadeIn(self.diagram_group()), FadeIn(self.stars),
                  FadeIn(self.eq), *[FadeIn(l) for l in self.labels.values()],
                  run_time=1.5)
        self.wait(0.5)

    def check(self, term):
        return MathTex(r"\checkmark", font_size=40, color=GOOD).next_to(
            term, DOWN, buff=0.25)

    def beat_satellites(self):
        self.show_caption("TART's sky: GPS satellites at known positions")
        sats = VGroup(*[make_satellite(s.get_center(), 1.2 if i == 0 else 0.9)
                        for i, s in enumerate(self.stars)])
        self.play(LaggedStart(*[ReplacementTransform(s, t)
                                for s, t in zip(self.stars, sats)],
                              lag_ratio=0.15), run_time=1.6)
        self.ck_b = self.check(self.eq[4])
        self.play(FadeIn(self.ck_b, scale=0.5), run_time=0.6)
        self.sats = sats
        self.wait(0.5)

    def beat_geometry(self):
        self.show_caption("K: known from where the antennas are")
        self.ck_k = self.check(self.eq[6])
        self.play(Indicate(self.labels[r"K_{pq,s}"], color=GOOD),
                  FadeIn(self.ck_k, scale=0.5), run_time=1.0)
        self.wait(0.5)

    def make_dial(self, centre, amp, phase):
        circ = Circle(radius=0.45, color=MUTED, stroke_width=2).move_to(centre)
        tip = centre + amp * 0.45 * np.array([np.cos(phase), np.sin(phase), 0])
        arr = Arrow(centre, tip, buff=0, color=SIG_P, stroke_width=4,
                    max_tip_length_to_length_ratio=0.3)
        return VGroup(circ, arr)

    def beat_gains(self):
        self.show_caption("One receiver per antenna, one polarisation")
        lp, lq = self.labels[r"G_p"], self.labels[r"G_q^*"]
        cp = lp.get_center() + 1.15 * DOWN
        cq = lq.get_center() + 1.15 * DOWN
        self.amp_p = ValueTracker(0.8)
        self.ph_p = ValueTracker(40 * DEGREES)
        self.amp_q = ValueTracker(0.9)
        self.ph_q = ValueTracker(-30 * DEGREES)
        dial_p = always_redraw(lambda: self.make_dial(
            cp, self.amp_p.get_value(), self.ph_p.get_value()))
        dial_q = always_redraw(lambda: self.make_dial(
            cq, self.amp_q.get_value(), self.ph_q.get_value()))
        self.add(dial_p, dial_q)
        self.play(FadeIn(dial_p), FadeIn(dial_q), run_time=0.8)
        self.wait(0.3)

        self.show_caption("…so each G is one complex number: how much louder, how much later")
        self.play(self.amp_p.animate.set_value(1.0),
                  self.amp_q.animate.set_value(0.6), run_time=1.2)
        self.play(self.ph_p.animate.set_value(110 * DEGREES),
                  self.ph_q.animate.set_value(15 * DEGREES), run_time=1.4)
        self.wait(0.5)

    def beat_count(self):
        self.show_caption("Calibration: solve for one complex number per antenna")
        eq = self.eq
        box_g = VGroup(SurroundingRectangle(eq[3], color=SIG_P, buff=0.05),
                       SurroundingRectangle(eq[5], color=SIG_P, buff=0.05))
        rows = VGroup(
            Tex(r"24 antennas", font_size=36, color=FRONT),
            Tex(r"$\Rightarrow$ 276 visibilities $V_{pq}$", font_size=36,
                color=GOOD),
            Tex(r"$\Rightarrow$ only 24 unknown gains $G_p$", font_size=36,
                color=SIG_P),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(
            eq, DOWN, buff=1.0).align_to(eq, LEFT).shift(0.3 * RIGHT)
        self.play(Create(box_g), run_time=0.8)
        for r in rows:
            self.play(FadeIn(r, shift=0.2 * RIGHT), run_time=0.7)
        self.wait(1.0)


def cell_grid(color, entries=("xx", "xy", "yx", "yy"), size=0.85):
    """A 2x2 box, the shape of the visibility matrix: one cell per pairing."""
    cells = VGroup()
    for i, e in enumerate(entries):
        r, c = divmod(i, 2)
        sq = RoundedRectangle(width=size - 0.06, height=size - 0.06,
                              corner_radius=0.05, stroke_color=color,
                              stroke_width=2.5).move_to([c * size, -r * size, 0])
        lab = Text(e, font_size=26, color=color).move_to(sq)
        cells.add(VGroup(sq, lab))
    return cells.move_to(ORIGIN)


class OneNumberToABox(RimeDiagram, Scene):
    """From the scalar equation to the RIME: with two wiggles per antenna,
    every number in G_p B G_q* grows into a 2x2 box, and G is renamed J."""

    def construct(self):
        self.cap = None
        if self.standalone:
            self.title_card("One Number Becomes a Box",
                            "from the scalar equation to the RIME")
        self.beat_scalar()
        self.beat_boxes()
        self.beat_rename()
        self.beat_rime()
        if self.standalone:
            self.closing_card("Same equation —",
                              "bigger pieces.",
                              "next: peeling the onion")
        else:
            self.wait(0.5)

    def beat_scalar(self):
        self.show_caption("One wiggle per antenna: every term is one number")
        parts = [r"V_{pq}", r"=", r"G_p", r"B", r"G_q^*"]
        eq = MathTex(*parts, font_size=72, color=FRONT,
                     arg_separator=r"\quad").move_to(0.6 * UP)
        for i, tex in enumerate(parts):
            if tex in TERM_COLORS:
                eq[i].set_color(TERM_COLORS[tex])
        words = ["measured", None, "antenna p", "sky", "antenna q"]
        labels = VGroup(*[
            Text(w, font_size=22, color=MUTED).next_to(eq[i], DOWN, buff=0.45)
            for i, w in enumerate(words) if w])
        self.play(Write(eq), run_time=1.2)
        self.play(FadeIn(labels, lag_ratio=0.2), run_time=0.8)
        self.scalar, self.scalar_labels = eq, labels
        self.wait(1.0)

    def beat_boxes(self):
        self.show_caption("Two wiggles per antenna (x and y): "
                          "each number grows into a 2×2 box")
        cols = [GOOD, SIG_P, SIG_Q, SIG_P]
        grids = [cell_grid(c) for c in cols]
        syms = [r"\mathbf{V}_{pq}", r"\mathbf{J}_p", r"\mathbf{B}",
                r"\mathbf{J}_q^H"]
        row = VGroup(grids[0], MathTex("=", font_size=60, color=FRONT),
                     *grids[1:]).arrange(RIGHT, buff=0.7).move_to(0.7 * UP)
        names = VGroup(*[MathTex(s, font_size=56, color=c).next_to(
            g, DOWN, buff=0.35) for s, c, g in zip(syms, cols, grids)])
        self.play(FadeOut(self.scalar_labels), run_time=0.4)
        src = [self.scalar[i] for i in (0, 2, 3, 4)]
        self.play(*[ReplacementTransform(s, g) for s, g in zip(src, grids)],
                  ReplacementTransform(self.scalar[1], row[1]), run_time=1.6)
        self.play(FadeIn(names, shift=0.15 * UP, lag_ratio=0.2), run_time=1.0)
        self.row, self.names = row, names
        self.wait(1.0)

    def beat_rename(self):
        self.show_caption("G was shorthand for the whole journey: "
                          "its full name is J")
        jp = self.names[1]
        chain = MathTex(r"\mathbf{J} = G\,D\,E\,P\,F\,Z\,K", font_size=44,
                        color=SIG_P).move_to(2.4 * DOWN)
        note = Text("from here on, G means just the electronics",
                    font_size=22, color=MUTED).next_to(chain, DOWN, buff=0.25)
        self.play(Indicate(jp, color=SIG_P, scale_factor=1.25),
                  Indicate(self.names[3], color=SIG_P, scale_factor=1.25),
                  run_time=1.0)
        self.play(FadeIn(chain, shift=0.2 * UP), run_time=0.8)
        self.play(FadeIn(note), run_time=0.6)
        self.rename = VGroup(chain, note)
        self.wait(1.0)

    def beat_rime(self):
        self.show_caption("The RIME: the same shape as before, "
                          "with boxes instead of numbers")
        old = MathTex(r"V_{pq}", r"=", r"G_p", r"B", r"G_q^*", font_size=44,
                      color=MUTED, arg_separator=r"\,").move_to(1.7 * UP)
        rime = MathTex(r"\mathbf{V}_{pq}", r"=", r"\mathbf{J}_p", r"\mathbf{B}",
                       r"\mathbf{J}_q^H", font_size=84, color=FRONT,
                       arg_separator=r"\,").move_to(0.1 * DOWN)
        for i, c in zip((0, 2, 3, 4), (GOOD, SIG_P, SIG_Q, SIG_P)):
            rime[i].set_color(c)
        self.play(FadeOut(self.row), FadeOut(self.rename), run_time=0.6)
        self.play(*[ReplacementTransform(n, rime[i])
                    for n, i in zip(self.names, (0, 2, 3, 4))],
                  FadeIn(rime[1]), run_time=1.4)
        self.play(FadeIn(old, shift=0.2 * DOWN), run_time=0.8)
        self.wait(1.5)
