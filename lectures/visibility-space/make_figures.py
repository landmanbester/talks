"""Build-up figures for the resolution / sensitivity / interferometer slides.

Each build is a sequence of transparent PNGs on the same canvas, each a superset
of the one before, for a `::: {.r-stack}` with `.fragment` on all but the first.
The layout follows the Canva deck (slides 8-22); the GBT photo is
images/gbt-current.png and the two MeerKAT thumbnails are cut from
images/interferometer-schematic.png (that is where the p and q come from).

    uv run lectures/visibility-space/make_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Ellipse, FancyArrowPatch, PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from PIL import Image  # noqa: E402
from scipy.special import j1  # noqa: E402

HERE = Path(__file__).resolve().parent
IMG = HERE / "images"

# dark-academic palette
BG = "#0d1117"
FG = "#c9d1d9"
BLUE = "#58a6ff"
AMBER = "#d29922"
GREEN = "#3fb950"

plt.rcParams["mathtext.fontset"] = "cm"

PHOTO = np.asarray(Image.open(IMG / "gbt-current.png").convert("RGBA"))
PH, PW = PHOTO.shape[:2]                     # 972 x 750


def canvas(w, h, scale=2):
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100 * scale)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(IMG / name, transparent=True)
    plt.close(fig)
    print("wrote", name)


def arrow(ax, p0, p1, color, both=False, lw=3, scale=28):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<|-|>" if both else "-|>",
                                 mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------- the dish
# Geometry in gbt-current.png pixels. The rim runs from lower left to upper
# right; the face is foreshortened, so the true diameter is the major axis.
RIM_C = (305, 568)
RIM_ANGLE = -44.7                            # degrees, data coords (y down)
RIM_A, RIM_B = 380, 106                      # semi-axes
U = np.array([np.cos(np.radians(RIM_ANGLE)), np.sin(np.radians(RIM_ANGLE))])
N = np.array([-U[1], U[0]])                  # toward the lower right


def dish(steps):
    """The photo plus the requested overlays: 'rim', 'D', 'receiver'."""
    fig, ax = canvas(PW, PH)
    ax.imshow(PHOTO, extent=(0, PW, PH, 0))
    if "rim" in steps:
        ax.add_patch(Ellipse(RIM_C, 2 * RIM_A, 2 * RIM_B, angle=RIM_ANGLE,
                             fill=False, ec=AMBER, lw=5))
    if "D" in steps:
        c = np.array(RIM_C)
        arrow(ax, c - RIM_A * U, c + RIM_A * U, BG, both=True, lw=4)   # rim to rim
        ax.text(*(c - 55 * N), r"$D$", color=BG, fontsize=44,
                ha="center", va="center")
    if "receiver" in steps:
        ax.add_patch(Ellipse((222, 110), 205, 100, angle=26.6,
                             fill=False, ec=AMBER, lw=5))
    return fig


# --------------------------------------------------- the interferometer
# Canvas = interferometer-schematic.png (2040 x 1688): the photo fills the top
# left, the second dish and the correlator sit off it to the right.
SCH = np.asarray(Image.open(IMG / "interferometer-schematic.png").convert("RGBA"))
SW, SH = 2040, 1688
S = 1170 / PW                                # photo scale on this canvas
DISH_P = (288, 1440, 712, 1672)              # x0, y0, x1, y1 in the schematic
DISH_Q = (1213, 1067, 1648, 1312)


def thumb(ax, box):
    x0, y0, x1, y1 = box
    ax.imshow(SCH[y0:y1, x0:x1], extent=(x0, x1, y1, y0), zorder=3)


def interferometer(step):
    fig, ax = canvas(SW, SH, scale=1)
    ax.imshow(PHOTO, extent=(0, PW * S, PH * S, 0))
    if step >= 1:
        # light from the source direction, collected by two pieces of the
        # aperture -- each now a small dish of its own
        arrow(ax, (546, 948), (22, 405), BG, lw=4, scale=40)
        ax.text(30, 330, r"$s_0$", color=BG, fontsize=72)
        for (a, b) in [((898, 515), (1428, 1067)), ((887, 627), (1318, 1067)),
                       ((232, 1300), (370, 1440)), ((298, 1270), (470, 1440))]:
            ax.plot(*zip(a, b), color=AMBER, lw=4)
        thumb(ax, DISH_P)
        thumb(ax, DISH_Q)
    if step >= 2:
        arrow(ax, (440, 1478), (1066, 730), BG, both=True, lw=4, scale=40)
        ax.text(690, 1255, r"$b_{pq}$", color=BG, fontsize=64)
    if step >= 3:
        ax.text(985, 1400, r"$\Delta\theta \approx \dfrac{\lambda}{b_{pq}}$",
                color=BG, fontsize=58, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=BG, lw=3))
    if step >= 4:
        # both signals run to the correlator, which outputs the visibility
        knot = (1566, 1499)
        for verts in [[(712, 1620), (1000, 1560), (1300, 1680), knot],
                      [(1468, 1312), (1468, 1420), (1520, 1499), knot]]:
            ax.add_patch(PathPatch(MPath(verts, [MPath.MOVETO] + [MPath.CURVE4] * 3),
                                   fc="none", ec=FG, lw=4))
        ax.plot(*knot, marker="D", ms=26, mfc=BG, mec=FG, mew=4, zorder=4)
        x = np.linspace(knot[0] + 30, 1860, 400)
        ax.plot(x, knot[1] + 16 * np.sin((x - x[0]) / 13), color=GREEN, lw=5)
        ax.text(1875, knot[1] + 15, r"$V_{pq}$", color=GREEN, fontsize=72,
                va="center")
    return fig


# --------------------------------------------------------- resolution
def airy(theta):
    """Airy pattern; theta in units of lambda/D (first null at 1.22)."""
    x = np.pi * np.where(theta == 0, 1e-9, theta)
    return (2 * j1(x) / x) ** 2


def rayleigh():
    cases = [(0.5, "too close"), (1.22, "just resolved"), (2.5, "resolved")]
    fig, axes = plt.subplots(2, 3, figsize=(13, 6.2), dpi=200,
                             gridspec_kw=dict(height_ratios=[1.15, 1]))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.03,
                        hspace=0.12, wspace=0.08)
    t = np.linspace(-4, 4, 1200)
    yy, xx = np.mgrid[-3:3:300j, -4:4:400j]
    for k, (sep, title) in enumerate(cases):
        ax = axes[0, k]
        a, b = airy(t + sep / 2), airy(t - sep / 2)
        ax.fill_between(t, a + b, color=FG, alpha=0.12, lw=0)
        ax.plot(t, a + b, color=FG, lw=1.5)
        ax.plot(t, a, color=BLUE, lw=2.5)
        ax.plot(t, b, color=AMBER, lw=2.5)
        ax.set_xlim(-4, 4)
        ax.set_ylim(0, 2.05)
        ax.axis("off")
        ax.set_title(title, color=FG, fontsize=30, pad=6)
        img = (airy(np.hypot(xx + sep / 2, yy)) + airy(np.hypot(xx - sep / 2, yy)))
        axes[1, k].imshow(np.sqrt(img), cmap="inferno", aspect="equal")
        axes[1, k].axis("off")
    fig.savefig(IMG / "rayleigh.png", transparent=True)
    plt.close(fig)
    print("wrote rayleigh.png")


if __name__ == "__main__":
    save(dish([]), "dish-0.png")
    save(dish(["rim"]), "dish-1.png")
    save(dish(["rim", "D"]), "dish-2.png")
    save(dish(["receiver"]), "dish-3.png")
    save(dish(["receiver", "rim"]), "dish-4.png")
    for s in range(5):
        save(interferometer(s), f"interferometer-{s}.png")
    rayleigh()
