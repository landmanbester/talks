"""Painting the whole sphere — KREMETART slide clip.

A fixed celestial sphere (the equatorial grid) painted in real time by the
sweeping, primary-beam-tapered footprints of several zenith-pointing TART
stations. One southern station sweeps out a band and leaves the north cap dark;
northern and mid stations switch on and fill it. Master clock = sidereal phase.

Render (transparent), then convert to VP9-alpha webm:
    ~/software/manim/.venv/bin/manim -t -qm sphere_painting.py SpherePainting
    ffmpeg -y -i media/videos/sphere_painting/720p30/SpherePainting.mov \
      -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 -b:v 2M \
      videos/sphere-painting.webm
"""

import numpy as np
from manim import *

# ----- palette (dark-academic talk theme) -----
BG = "#0d1117"
BLUE = "#58a6ff"    # southern station
GREEN = "#3fb950"   # northern station
AMBER = "#d29922"   # mid station
MUTED = "#8b949e"
GRID = "#30363d"
FRONT = "#c9d1d9"

config.background_color = BG

R = 2.2          # sphere radius
EXP = 1.5        # primary-beam taper exponent

# stations: (dec_deg, ra0_deg, colour, on_clock turns, label)
# Two stations at opposite mid-latitudes: one paints the south and leaves a
# north cap, the other fills it; their overlap band reads as multi-station cover.
STATIONS = [
    (-55, 0, BLUE, 0.0, "55S"),
    (+55, 150, GREEN, 1.0, "55N"),
]


def uvec(dec, ra):
    cd = np.cos(dec)
    return np.array([cd * np.cos(ra), cd * np.sin(ra), np.sin(dec)])


def sphere_func(u, v):
    return R * np.array([np.sin(v) * np.cos(u),
                         np.sin(v) * np.sin(u),
                         np.cos(v)])


class SpherePainting(ThreeDScene):
    def construct(self):
        self.clock = ValueTracker(0.0)

        st_dec = np.array([s[0] * DEGREES for s in STATIONS])
        st_ra0 = np.array([s[1] * DEGREES for s in STATIONS])
        st_on = np.array([s[3] for s in STATIONS])
        st_rgb = np.array([ManimColor(s[2]).to_rgb() for s in STATIONS])
        S = len(STATIONS)

        # the fixed celestial sphere — faint mesh = graticule + body
        surf = Surface(sphere_func, u_range=[0, TAU], v_range=[0.08, PI - 0.08],
                       resolution=(44, 22))
        surf.set_fill(BLUE, opacity=0.0)
        surf.set_stroke(GRID, width=0.5, opacity=0.18)
        faces = surf.submobjects
        dirs = np.array([f.get_center() / np.linalg.norm(f.get_center())
                         for f in faces])
        Nf = len(faces)
        paint = np.zeros((S, Nf))

        def update_fill(_m):
            t = self.clock.get_value()
            drawn = np.zeros((S, Nf))
            for s in range(S):
                if t < st_on[s]:
                    continue
                z = uvec(st_dec[s], st_ra0[s] + TAU * t)
                w = np.clip(dirs @ z, 0.0, None) ** EXP
                paint[s] = np.maximum(paint[s], w)
                drawn[s] = 0.45 * paint[s] + 0.85 * w   # dim trail, bright live head
            # additive light: overlaps brighten and shift hue, each station keeps its colour
            lin = (drawn[:, :, None] * st_rgb[:, None, :]).sum(0)   # (Nf, 3)
            inten = lin.max(axis=1)                                 # brightness proxy
            rgb = np.clip(lin / np.maximum(inten, 1e-6)[:, None], 0.0, 1.0)
            op = np.clip(inten * 0.95, 0.0, 0.9)
            for i, face in enumerate(faces):
                face.set_fill(rgb_to_color(rgb[i]), opacity=float(op[i]))

        # sweeping zenith markers (one per station, shown once active)
        def zen_dot(s):
            t = self.clock.get_value()
            pos = R * uvec(st_dec[s], st_ra0[s] + TAU * t)
            if t < st_on[s]:
                return Dot3D(pos, radius=0.001).set_opacity(0.0)
            return Dot3D(pos, radius=0.075, color=STATIONS[s][2])

        markers = [always_redraw(lambda s=s: zen_dot(s)) for s in range(S)]

        self.set_camera_orientation(phi=70 * DEGREES, theta=-55 * DEGREES,
                                    zoom=0.95)

        # --- intro: the fixed sphere appears ---
        self.play(FadeIn(surf), run_time=1.3)
        surf.add_updater(update_fill)
        for m in markers:
            self.add(m)
        self.begin_ambient_camera_rotation(rate=0.05)

        cap = self.caption("One TART sweeps the sky as it streams past")
        self.play(FadeIn(cap), run_time=0.5)

        # --- one station sweeps a band ---
        self.play(self.clock.animate.set_value(1.0),
                  rate_func=linear, run_time=4.6)

        cap2 = self.caption("More stations fill what one cannot reach")
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.5)

        # --- the network switches on and fills the gap ---
        self.play(self.clock.animate.set_value(2.3),
                  rate_func=linear, run_time=5.6)

        cap3 = self.caption("Together: the whole sphere, in real time")
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.5)

        # --- steady state ---
        self.play(self.clock.animate.set_value(2.75),
                  rate_func=linear, run_time=2.0)
        self.wait(0.4)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(cap3), run_time=0.6)

    def caption(self, text, color=FRONT):
        c = Text(text, font_size=27, color=color).to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(c)
        self.remove(c)
        return c
