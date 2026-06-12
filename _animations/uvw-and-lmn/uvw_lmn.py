"""Where uvw and lmn Live — the two viewpoints of an interferometer.

Fourth installment (see scenes.md). First ThreeDScene of the series: one 3D
set (ground + antennas + dome + line of sight) and the camera does the
teaching.

Render:
    ~/software/manim/.venv/bin/manim -qm uvw_lmn.py UVWAndLMN
"""

import numpy as np
from manim import *

# ----- palette (matches dark-academic talk theme) -----
BG = "#0d1117"
SIG_P = "#58a6ff"   # antenna p
SIG_Q = "#d29922"   # antenna q / sky side (lmn)
GOOD = "#3fb950"    # measurement side (uvw)
BAD = "#f85149"
FRONT = "#c9d1d9"
MUTED = "#8b949e"
GRAY_ANT = "#6e7681"

config.background_color = BG

# ----- geometry -----
PHI0 = 25 * DEGREES                      # phase centre tilt from vertical
W_HAT = np.array([np.sin(PHI0), 0.0, np.cos(PHI0)])   # toward the source
U_HAT = np.array([0.0, 1.0, 0.0])                      # "east" on the screens
V_HAT = np.cross(W_HAT, U_HAT)                         # completes the frame

R_DOME = 3.4                             # celestial dome radius
D_SCR = 4.6                              # uvw screen distance (beyond dome)
C_SCR = D_SCR * W_HAT                    # uvw screen centre
C_TAN = R_DOME * W_HAT                   # lmn tangent point on the dome

P_BASE = np.array([1.5, 0.6, 0.0])       # p is nearer the source along w
Q_BASE = np.array([-1.1, 1.0, 0.0])
OTHERS = [np.array([0.2, -1.2, 0.0]), np.array([-0.7, -0.35, 0.0])]

NEAR_LM = [(0.10, 0.04), (-0.09, 0.16), (0.04, -0.12)]
FAR_LM = (0.52, 0.30)


def rotz(p, ang):
    c, s = np.cos(ang), np.sin(ang)
    return np.array([c * p[0] - s * p[1], s * p[0] + c * p[1], p[2]])


def proj_screen(a):
    """Project a point along w-hat onto the uvw screen."""
    return a + (D_SCR - float(a @ W_HAT)) * W_HAT


def sky_dir(l, m):
    n = np.sqrt(1 - l ** 2 - m ** 2)
    return l * U_HAT + m * V_HAT + n * W_HAT


def map_point(l, m):
    """Orthographic drop of a star onto the tangent screen."""
    return R_DOME * (l * U_HAT + m * V_HAT + W_HAT)


def make_sky_img():
    """Video 3's truth sky (copied so the script stays standalone)."""
    y, x = np.mgrid[0:128, 0:128].astype(float)

    def g(cx, cy, sig, amp):
        return amp * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sig ** 2))

    sky = (g(78, 58, 9, 0.55) + g(46, 50, 1.4, 1.0)
           + g(58, 88, 2.6, 0.85) + g(68, 93, 2.6, 0.7))
    t = np.clip((sky / sky.max()) ** 0.7, 0, 1)[..., None]
    bgv = np.array([13.0, 17.0, 23.0])
    amb = np.array([210.0, 153.0, 34.0])
    wht = np.array([255.0, 244.0, 220.0])
    lo = bgv + (amb - bgv) * np.clip(t, 0, 0.6) / 0.6
    hi = amb + (wht - amb) * (np.clip(t, 0.6, 1) - 0.6) / 0.4
    return np.where(t < 0.6, lo, hi).astype(np.uint8)


class UVWAndLMN(ThreeDScene):
    def construct(self):
        self.rot = ValueTracker(0.0)
        self.scene1_direction()
        self.scene2_uvw()
        self.scene3_lmn()
        self.scene4_pairing()
        self.scene5_close()

    # ------------------------------------------------------------------
    # fixed-frame / fixed-orientation helpers
    # ------------------------------------------------------------------
    def caption(self, text, color=FRONT):
        c = Text(text, font_size=27, color=color).to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(c)
        self.remove(c)
        return c

    def label3d(self, tex, pos, color=FRONT, fs=34):
        t = MathTex(tex, font_size=fs, color=color).move_to(pos)
        self.add_fixed_orientation_mobjects(t)
        self.remove(t)
        return t

    def p_now(self):
        return rotz(P_BASE, self.rot.get_value())

    def q_now(self):
        return rotz(Q_BASE, self.rot.get_value())

    # ------------------------------------------------------------------
    # Scene 1: one special direction
    # ------------------------------------------------------------------
    def scene1_direction(self):
        title = Text("Where uvw and lmn Live", font_size=44, color=FRONT)
        sub = Text("the two viewpoints of an interferometer", font_size=28,
                   color=MUTED).next_to(title, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(title, sub)
        self.remove(title, sub)
        self.play(FadeIn(title, shift=0.3 * UP), FadeIn(sub), run_time=1.2)
        self.wait(1.8)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES,
                                    zoom=0.8, frame_center=[0.4, 0.2, 1.7])

        # ground grid
        grid = VGroup()
        for t in np.arange(-2.4, 2.5, 0.8):
            grid.add(Line([t, -2.4, 0], [t, 2.4, 0]))
            grid.add(Line([-2.4, t, 0], [2.4, t, 0]))
        grid.set_stroke(MUTED, 1, opacity=0.3)
        self.grid = grid

        # antennas (p/q highlighted; whole array rides the rotation tracker)
        self.ant_p = always_redraw(
            lambda: Dot3D(self.p_now(), radius=0.10, color=SIG_P)
        )
        self.ant_q = always_redraw(
            lambda: Dot3D(self.q_now(), radius=0.10, color=SIG_Q)
        )
        self.ant_o = always_redraw(lambda: VGroup(*[
            Dot3D(rotz(a, self.rot.get_value()), radius=0.08, color=GRAY_ANT)
            for a in OTHERS
        ]))
        self.lbl_p = self.label3d("p", P_BASE + [0.0, 0.32, 0.12], SIG_P)
        self.lbl_q = self.label3d("q", Q_BASE + [0.0, 0.32, 0.12], SIG_Q)
        self.lbl_p.add_updater(
            lambda m: m.move_to(self.p_now() + [0.0, 0.32, 0.12])
        )
        self.lbl_q.add_updater(
            lambda m: m.move_to(self.q_now() + [0.0, 0.32, 0.12])
        )

        # celestial dome (faint) + the target star at the phase centre
        dome = Surface(
            lambda t, p: R_DOME * np.array([
                np.cos(t) * np.sin(p), np.sin(t) * np.sin(p), np.cos(p)
            ]),
            u_range=[0, TAU], v_range=[0.02, PI / 2 - 0.02],
            resolution=(24, 8),
        )
        dome.set_fill(FRONT, opacity=0.03)
        dome.set_stroke(MUTED, 0.5, opacity=0.16)
        self.dome = dome

        self.star0 = VGroup(
            Dot3D(C_TAN, radius=0.20, color=YELLOW).set_opacity(0.25),
            Dot3D(C_TAN, radius=0.09, color=YELLOW),
        )
        self.s0_arrow = Arrow3D([0, 0, 0], 2.6 * W_HAT, color=FRONT,
                                thickness=0.012, base_radius=0.05)
        self.s0_lbl = self.label3d("s_0", 2.45 * W_HAT + 0.42 * V_HAT, FRONT)

        cap = self.caption("a radio array on the ground, pointed at a patch of sky")
        self.play(FadeIn(cap), Create(grid), FadeIn(self.dome), run_time=1.4)
        self.add(self.ant_p, self.ant_q, self.ant_o)
        self.play(FadeIn(self.lbl_p), FadeIn(self.lbl_q),
                  FadeIn(self.star0), run_time=0.9)
        self.wait(1.0)
        cap2 = self.caption("one special arrow: the direction you point — the phase centre")
        self.play(FadeOut(cap), FadeIn(cap2),
                  Create(self.s0_arrow), FadeIn(self.s0_lbl), run_time=1.2)
        self.wait(1.2)
        cap3 = self.caption("every coordinate that follows is measured relative to this arrow")
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.8)
        self.wait(2.0)
        self.play(FadeOut(cap3), run_time=0.5)

    # ------------------------------------------------------------------
    # Scene 2: the source's-eye view (uvw)
    # ------------------------------------------------------------------
    def scene2_uvw(self):
        # the source's screen, far beyond the dome
        scr = Polygon(
            *[C_SCR + a * 1.9 * U_HAT + b * 1.9 * V_HAT
              for a, b in [(1, 1), (-1, 1), (-1, -1), (1, -1)]],
            stroke_color=GOOD, stroke_width=2,
            fill_color=GOOD, fill_opacity=0.06,
        )
        u_arrow = Arrow(C_SCR, C_SCR + 1.35 * U_HAT, buff=0,
                        color=GOOD, stroke_width=3, max_tip_length_to_length_ratio=0.12)
        v_arrow = Arrow(C_SCR, C_SCR + 1.35 * V_HAT, buff=0,
                        color=GOOD, stroke_width=3, max_tip_length_to_length_ratio=0.12)
        u_lbl = self.label3d("u", C_SCR + 1.6 * U_HAT, GOOD, fs=30)
        v_lbl = self.label3d("v", C_SCR + 1.6 * V_HAT, GOOD, fs=30)

        cap = self.caption("the source looks back down at us — this is its sky")
        self.play(FadeIn(cap), FadeIn(scr), GrowArrow(u_arrow),
                  GrowArrow(v_arrow), FadeIn(u_lbl), FadeIn(v_lbl),
                  FadeOut(self.star0), run_time=1.4)
        self.wait(1.5)

        # baseline + projection rays + projected baseline (tracker-driven)
        bl = always_redraw(lambda: Line(self.p_now(), self.q_now(),
                                        color=FRONT, stroke_width=3.5))
        ray_p = always_redraw(lambda: DashedLine(
            self.p_now(), proj_screen(self.p_now()),
            dash_length=0.14, color=SIG_P, stroke_width=1.6).set_opacity(0.55))
        ray_q = always_redraw(lambda: DashedLine(
            self.q_now(), proj_screen(self.q_now()),
            dash_length=0.14, color=SIG_Q, stroke_width=1.6).set_opacity(0.55))
        pp = always_redraw(lambda: Dot3D(proj_screen(self.p_now()),
                                         radius=0.07, color=SIG_P))
        pq = always_redraw(lambda: Dot3D(proj_screen(self.q_now()),
                                         radius=0.07, color=SIG_Q))
        pbl = always_redraw(lambda: Line(
            proj_screen(self.p_now()), proj_screen(self.q_now()),
            color=GOOD, stroke_width=4.5))

        cap2 = self.caption("slide our baseline up the sight-line onto that screen")
        self.play(FadeOut(cap), FadeIn(cap2), Create(bl), run_time=0.9)
        self.add(ray_p, ray_q)
        self.play(FadeIn(pp), FadeIn(pq), run_time=0.9)
        self.add(pbl)
        self.wait(1.5)

        # decomposition on the ground: w along the sight-line, (u,v) the rest
        w_val = float((P_BASE - Q_BASE) @ W_HAT)
        knee = Q_BASE + w_val * W_HAT
        w_leg = DashedLine(Q_BASE, knee, dash_length=0.12,
                           color=GOOD, stroke_width=3)
        uv_leg = Line(knee, P_BASE, color=GOOD, stroke_width=3)
        w_lbl = self.label3d("w", Q_BASE + 0.7 * w_val * W_HAT
                             - 0.55 * U_HAT, GOOD, fs=30)
        uv_lbl = self.label3d("(u,v)", 0.5 * (knee + P_BASE)
                              - 0.6 * V_HAT, GOOD, fs=28)
        cap3 = self.caption("part of the baseline points at the source: that part is w")
        self.play(FadeOut(cap2), FadeIn(cap3),
                  Create(w_leg), FadeIn(w_lbl), run_time=1.2)
        self.wait(1.2)
        cap4 = self.caption("the rest lies flat on the screen: that part is (u, v)")
        self.play(FadeOut(cap3), FadeIn(cap4),
                  Create(uv_leg), FadeIn(uv_lbl), run_time=1.2)
        self.wait(1.8)

        # ride up the line of sight and look back down
        cap5 = self.caption("now ride up the arrow and look back down...")
        self.play(FadeOut(cap4), FadeIn(cap5),
                  FadeOut(w_leg), FadeOut(uv_leg),
                  FadeOut(w_lbl), FadeOut(uv_lbl), run_time=0.9)
        self.move_camera(phi=PHI0, theta=0 * DEGREES, zoom=0.85,
                         frame_center=[1.2, 0, 2.6], focal_distance=60,
                         run_time=4.5)
        cap6 = self.caption("the baseline lands exactly on its shadow: all the source sees is (u, v)")
        self.play(FadeOut(cap5), FadeIn(cap6), run_time=0.8)
        self.wait(2.0)
        cap7 = self.caption("w hides along the sight-line — invisible from up here")
        self.play(FadeOut(cap6), FadeIn(cap7), run_time=0.8)
        self.wait(2.0)

        # the Earth turns: projected endpoints trace video 3's ellipses
        tr_p = TracedPath(lambda: proj_screen(self.p_now()),
                          stroke_color=GOOD, stroke_width=2.5)
        tr_q = TracedPath(lambda: proj_screen(self.q_now()),
                          stroke_color=GOOD, stroke_width=2.5)
        self.add(tr_p, tr_q)
        cap8 = self.caption("and as the Earth turns, the shadow sweeps an arc...")
        self.play(FadeOut(cap7), FadeIn(cap8), run_time=0.8)
        self.play(self.rot.animate.set_value(2.6), run_time=8.0,
                  rate_func=rate_functions.ease_in_out_sine)
        cap9 = self.caption("...the uv tracks of last time, seen for what they are")
        self.play(FadeOut(cap8), FadeIn(cap9), run_time=0.8)
        self.wait(2.0)

        # back down to the ground view
        self.play(FadeOut(cap9), run_time=0.5)
        self.move_camera(phi=65 * DEGREES, theta=-50 * DEGREES, zoom=0.8,
                         frame_center=[0.4, 0.2, 1.7], focal_distance=20,
                         run_time=3.0)
        self.remove(tr_p, tr_q, ray_p, ray_q, pp, pq, pbl, bl)
        self.play(FadeOut(scr), FadeOut(u_arrow), FadeOut(v_arrow),
                  FadeOut(u_lbl), FadeOut(v_lbl), run_time=0.9)

    # ------------------------------------------------------------------
    # Scene 3: the array's-eye view (lmn)
    # ------------------------------------------------------------------
    def scene3_lmn(self):
        # the dome's fill depth-sorts above the floor: brighten + re-add
        self.grid.set_stroke(MUTED, 1, opacity=0.55)
        self.add(self.grid)
        cap = self.caption("now the other viewpoint: stand at a dish and look up")
        self.play(FadeIn(cap), FadeIn(self.star0), run_time=0.9)

        stars = VGroup(*[
            Dot3D(R_DOME * sky_dir(l, m), radius=0.08, color=YELLOW)
            for (l, m) in NEAR_LM + [FAR_LM]
        ])
        self.play(LaggedStart(*[FadeIn(s, scale=2) for s in stars],
                              lag_ratio=0.2), run_time=1.2)
        self.wait(0.8)

        # the flat map: tangent screen at the phase centre
        scr = Polygon(
            *[C_TAN + a * 1.7 * U_HAT + b * 1.7 * V_HAT
              for a, b in [(1, 1), (-1, 1), (-1, -1), (1, -1)]],
            stroke_color=SIG_Q, stroke_width=2,
            fill_color=SIG_Q, fill_opacity=0.06,
        )
        l_arrow = Arrow(C_TAN, C_TAN + 1.25 * U_HAT, buff=0, color=SIG_Q,
                        stroke_width=3, max_tip_length_to_length_ratio=0.12)
        m_arrow = Arrow(C_TAN, C_TAN + 1.25 * V_HAT, buff=0, color=SIG_Q,
                        stroke_width=3, max_tip_length_to_length_ratio=0.12)
        l_lbl = self.label3d("l", C_TAN + 1.48 * U_HAT, SIG_Q, fs=30)
        m_lbl = self.label3d("m", C_TAN + 1.48 * V_HAT, SIG_Q, fs=30)
        cap2 = self.caption("stars live on a dome — but a computer wants a flat map")
        self.play(FadeOut(cap), FadeIn(cap2), FadeIn(scr),
                  GrowArrow(l_arrow), GrowArrow(m_arrow),
                  FadeIn(l_lbl), FadeIn(m_lbl), run_time=1.4)
        self.wait(1.5)

        # plumb lines: each star drops onto its map address
        plumbs = VGroup()
        mdots = VGroup()
        for (l, m) in NEAR_LM + [FAR_LM]:
            s_pos = R_DOME * sky_dir(l, m)
            t_pos = map_point(l, m)
            plumbs.add(DashedLine(s_pos, t_pos, dash_length=0.1,
                                  color=FRONT, stroke_width=1.8).set_opacity(0.7))
            mdots.add(Dot3D(t_pos, radius=0.06, color=SIG_Q))
        cap3 = self.caption("drop each star straight onto the map: its address is (l, m)")
        self.play(FadeOut(cap2), FadeIn(cap3),
                  LaggedStart(*[Create(p) for p in plumbs], lag_ratio=0.2),
                  LaggedStart(*[FadeIn(d, scale=2) for d in mdots],
                              lag_ratio=0.2),
                  run_time=2.0)
        self.wait(1.8)

        # the sag: n
        far_plumb = plumbs[-1]
        lf, mf = FAR_LM
        n_lbl = self.label3d("1-n",
                             0.5 * (R_DOME * sky_dir(lf, mf) + map_point(lf, mf))
                             + 0.45 * U_HAT - 0.35 * V_HAT, BAD, fs=28)
        cap4 = self.caption("far from centre the dome sags below the map — n keeps the score")
        self.play(FadeOut(cap3), FadeIn(cap4),
                  far_plumb.animate.set_opacity(1.0).set_color(BAD)
                  .set_stroke(width=3.5),
                  FadeIn(n_lbl), run_time=1.2)
        self.wait(2.2)

        # peel the map off into 2D (fixed-frame inset)
        inset_sc = 2.1
        ibox = Square(2.55, stroke_color=SIG_Q, stroke_width=2).move_to(
            [4.7, -1.9, 0])
        idots = VGroup(*[
            Dot([4.7 + l * inset_sc, -1.9 + m * inset_sc, 0],
                radius=0.05, color=SIG_Q)
            for (l, m) in NEAR_LM + [FAR_LM]
        ])
        itag = Text("the flat map", font_size=20, color=SIG_Q).next_to(
            ibox, UP, buff=0.1)
        self.add_fixed_in_frame_mobjects(ibox, idots, itag)
        self.remove(ibox, idots, itag)
        cap5 = self.caption("peel the map off — this flat picture is all the computer keeps")
        self.play(FadeOut(cap4), FadeIn(cap5), Create(ibox),
                  FadeIn(idots), FadeIn(itag), run_time=1.4)
        self.wait(1.8)

        img = ImageMobject(make_sky_img()).set(height=2.45).move_to(
            [4.7, -1.9, 0])
        self.add_fixed_in_frame_mobjects(img)
        self.remove(img)
        cap6 = self.caption("the sky maps of last time — I(l, m) — live exactly here")
        self.play(FadeOut(cap5), FadeIn(cap6), FadeOut(idots),
                  FadeIn(img), run_time=1.2)
        self.wait(2.5)

        self.play(FadeOut(cap6), run_time=0.5)
        self.s3_world = VGroup(stars, scr, l_arrow, m_arrow, l_lbl, m_lbl,
                               plumbs, mdots, n_lbl)
        self.s3_fixed = Group(ibox, img, itag)

    # ------------------------------------------------------------------
    # Scene 4: the letters pair up
    # ------------------------------------------------------------------
    def scene4_pairing(self):
        # clear the 3D world
        self.lbl_p.clear_updaters()
        self.lbl_q.clear_updaters()
        self.remove(self.ant_p, self.ant_q, self.ant_o)
        self.play(FadeOut(Group(
            self.grid, self.dome, self.star0, self.s0_arrow, self.s0_lbl,
            self.lbl_p, self.lbl_q, self.s3_world, self.s3_fixed,
        )), run_time=1.2)

        parts = [r"V_{pq}", "=", r"\iint", r"I(l,m)",
                 r"\, e^{-2\pi\imath (", "u", "l", "+", "v", "m", "+",
                 r"w(n-1)", r")}", r"\,\frac{dl\,dm}{n}"]
        eq = MathTex(*parts, font_size=46)
        eq.set_color(FRONT)
        for k in (0, 5, 8, 11):
            eq[k].set_color(GOOD)
        for k in (3, 6, 9):
            eq[k].set_color(SIG_Q)
        eq[11].set_color_by_gradient(GOOD, SIG_Q)
        eq.move_to(0.5 * UP)
        self.add_fixed_in_frame_mobjects(eq)
        self.remove(eq)

        key = VGroup(
            Text("green: the baseline, as the source sees it (u, v, w)",
                 font_size=24, color=GOOD),
            Text("amber: the sky, as the array sees it (l, m, n)",
                 font_size=24, color=SIG_Q),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(1.9 * DOWN)
        self.add_fixed_in_frame_mobjects(key)
        self.remove(key)

        cap = self.caption("the two viewpoints meet in one equation")
        self.play(FadeIn(cap), Write(eq), run_time=1.6)
        self.wait(0.8)
        self.play(FadeIn(key), run_time=0.9)
        self.wait(2.2)

        cap2 = self.caption("each baseline letter is paired with its sky letter")
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.8)
        for k in (5, 8, 11):
            self.play(Indicate(eq[k], scale_factor=1.35, color=None),
                      Indicate(eq[k + 1] if k != 11 else eq[k],
                               scale_factor=1.35, color=None),
                      run_time=0.7)
        self.wait(1.2)

        # the small-patch move: w(n-1) ~ 0
        brace = Brace(eq[11], DOWN, buff=0.1, color=MUTED)
        approx = MathTex(r"\approx 0", font_size=32, color=MUTED).next_to(
            brace, DOWN, buff=0.08)
        self.add_fixed_in_frame_mobjects(brace, approx)
        self.remove(brace, approx)
        cap3 = self.caption("point well and keep the patch small: n ≈ 1, and the w-term dies")
        self.play(FadeOut(cap2), FadeIn(cap3), FadeIn(brace), FadeIn(approx),
                  eq[11].animate.set_color(MUTED), run_time=1.2)
        self.wait(2.0)
        cap4 = self.caption("what is left is the clean 2-D Fourier pair of the last two videos")
        self.play(FadeOut(cap3), FadeIn(cap4), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(cap4), FadeOut(eq), FadeOut(key),
                  FadeOut(brace), FadeOut(approx), run_time=0.9)

    # ------------------------------------------------------------------
    # Scene 5: closing
    # ------------------------------------------------------------------
    def scene5_close(self):
        line1 = Text("uvw — the array, as the source sees it.",
                     font_size=38, color=GOOD)
        line2 = Text("lmn — the sky, as the array sees it.",
                     font_size=38, color=SIG_Q)
        msg = VGroup(line1, line2).arrange(DOWN, buff=0.35).move_to(0.4 * UP)
        tease = Text("next: deconvolution — undoing the dirty beam",
                     font_size=26, color=MUTED).next_to(msg, DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(msg, tease)
        self.remove(msg, tease)
        self.play(FadeIn(msg, shift=0.3 * UP), run_time=1.2)
        self.wait(1.2)
        self.play(FadeIn(tease), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(msg), FadeOut(tease), run_time=1.0)
        self.wait(0.5)
