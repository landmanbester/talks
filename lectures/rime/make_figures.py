"""Figures for the RIME lecture.

- kgb-0..2.png: what delay, bandpass and gain errors look like in the data,
  one panel per click (a build-up: each frame a superset of the one before)
- calibration-before-after.png: a simulated MeerKAT-like snapshot of a few
  point sources, imaged with the gains left in and with them corrected

    uv run lectures/rime/make_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import PowerNorm  # noqa: E402

HERE = Path(__file__).resolve().parent
IMG = HERE / "images"

# dark-academic palette
BG = "#0d1117"
FG = "#c9d1d9"
MUTED = "#8b949e"
BLUE = "#58a6ff"
AMBER = "#d29922"
GREEN = "#3fb950"
RED = "#f85149"

plt.rcParams.update({
    "mathtext.fontset": "cm",
    "font.size": 15,
    "text.color": FG,
    "axes.labelcolor": FG,
    "axes.edgecolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
})


def style(ax, title, xlabel, ylabel):
    ax.set_facecolor("none")
    ax.set_title(title, color=FG, fontsize=19, pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def kgb():
    rng = np.random.default_rng(3)
    nu = np.linspace(0, 1, 160)
    t = np.linspace(0, 1, 160)

    def panel(ax, which):
        if which == 0:
            phase = np.angle(np.exp(2j * np.pi * 3.2 * nu + 0.4j))
            ax.plot(nu, phase + 0.12 * rng.standard_normal(nu.size), ".",
                    color=BLUE, ms=4)
            ax.set_ylim(-3.6, 3.6)
            style(ax, "Delay (K)", "frequency", "phase")
            ax.text(0.5, -0.32, "a slope across frequency\n(wraps around)",
                    transform=ax.transAxes, ha="center", va="top", color=MUTED)
        elif which == 1:
            edge = 1 / (1 + np.exp(-(nu - 0.06) / 0.015)) / (
                1 + np.exp((nu - 0.94) / 0.015))
            amp = edge * (1 + 0.07 * np.sin(2 * np.pi * 7 * nu) + 0.05 * nu)
            ax.plot(nu, amp + 0.015 * rng.standard_normal(nu.size), ".",
                    color=BLUE, ms=4)
            ax.set_ylim(-0.05, 1.3)
            style(ax, "Bandpass (B)", "frequency", "amplitude")
            ax.text(0.5, -0.32, "a fixed shape across frequency",
                    transform=ax.transAxes, ha="center", va="top", color=MUTED)
        else:
            ph = 0.9 * np.sin(2 * np.pi * 0.8 * t + 0.3) + 0.35 * np.sin(
                2 * np.pi * 3.1 * t)
            ax.plot(t, ph + 0.08 * rng.standard_normal(t.size), ".",
                    color=BLUE, ms=4)
            ax.set_ylim(-2, 2)
            style(ax, "Gain (G)", "time", "phase")
            ax.text(0.5, -0.32, "a slow drift in time",
                    transform=ax.transAxes, ha="center", va="top", color=MUTED)

    for n in range(3):
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), dpi=130)
        fig.subplots_adjust(left=0.04, right=0.98, bottom=0.3, top=0.86,
                            wspace=0.25)
        for i, ax in enumerate(axes):
            if i <= n:
                panel(ax, i)
            else:
                ax.axis("off")
        fig.savefig(IMG / f"kgb-{n}.png", transparent=True)
        plt.close(fig)
        print(f"wrote kgb-{n}.png")


def simulate_before_after():
    rng = np.random.default_rng(11)
    lam = 0.21                                   # 1.4 GHz
    lat, dec = np.radians(-30.7), np.radians(-45.0)
    n_ant = 64
    r = 4000 * rng.random(n_ant) ** 2            # dense core, sparse arms
    th = 2 * np.pi * rng.random(n_ant)
    east, north = r * np.cos(th), r * np.sin(th)
    p, q = np.triu_indices(n_ant, 1)
    ha = np.radians(np.linspace(-45, 45, 90))    # 6 hours

    X = -(north[q] - north[p])[None, :] * np.sin(lat)
    Y = (east[q] - east[p])[None, :]
    Z = (north[q] - north[p])[None, :] * np.cos(lat)
    H = ha[:, None]
    u = (np.sin(H) * X + np.cos(H) * Y) / lam
    v = (-np.sin(dec) * np.cos(H) * X + np.sin(dec) * np.sin(H) * Y
         + np.cos(dec) * Z) / lam

    npix, cell = 256, np.radians(2.5 / 3600)
    src = [(0, 0, 1.0), (30, 18, 0.35), (-40, 22, 0.25), (15, -45, 0.2),
           (-25, -30, 0.15), (50, -15, 0.1), (-55, -50, 0.12)]
    vis = np.zeros(u.shape, complex)
    for x, y, s in src:
        l, m = x * cell, y * cell
        vis += s * np.exp(-2j * np.pi * (u * l + v * m))

    # antenna-based gain errors: a fixed phase offset per antenna plus a
    # random-walk drift (atmosphere), and ~20% amplitude errors
    offset = np.radians(70) * rng.standard_normal(n_ant)[None, :]
    drift = np.cumsum(np.radians(6) * rng.standard_normal((ha.size, n_ant)),
                      axis=0)
    phase = offset + drift
    amp = 1 + 0.2 * rng.standard_normal(n_ant)[None, :]
    g = amp * np.exp(1j * phase)
    corrupted = g[:, p] * vis * np.conj(g[:, q])

    def image(data):
        grid = np.zeros((npix, npix), complex)
        wts = np.zeros((npix, npix))
        du = 1 / (npix * cell)
        for uu, vv, dd in ((u, v, data), (-u, -v, np.conj(data))):
            iu = np.round(uu / du).astype(int) + npix // 2
            iv = np.round(vv / du).astype(int) + npix // 2
            ok = (iu >= 0) & (iu < npix) & (iv >= 0) & (iv < npix)
            np.add.at(grid, (iv[ok], iu[ok]), dd[ok])
            np.add.at(wts, (iv[ok], iu[ok]), 1)
        grid[wts > 0] /= wts[wts > 0]               # uniform weighting
        img = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(grid))).real
        psf = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(
            (wts > 0).astype(float)))).real
        return img / psf.max()

    before, after = image(corrupted), image(vis)
    vmax = after.max()
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.4), dpi=130)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.02, top=0.9,
                        wspace=0.04)
    for ax, im, title, col in ((axes[0], before, "Gains left in", RED),
                               (axes[1], after, "Gains corrected", GREEN)):
        c = slice(npix // 2 - 72, npix // 2 + 72)
        # square-root stretch, same scale for both: shows where the flux went
        ax.imshow(np.clip(im[c, c], 0, None), origin="lower", cmap="inferno",
                  norm=PowerNorm(0.5, vmin=0, vmax=0.6 * vmax),
                  interpolation="bicubic")
        ax.set_title(title, color=col, fontsize=22, pad=10)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor(MUTED)
    fig.savefig(IMG / "calibration-before-after.png", transparent=True)
    plt.close(fig)
    print("wrote calibration-before-after.png")


if __name__ == "__main__":
    kgb()
    simulate_before_after()
