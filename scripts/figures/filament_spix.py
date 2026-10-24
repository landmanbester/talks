#!/usr/bin/env python3
"""Do the non-thermal filaments share a spectral index? Figure and answer.

    PY="uv run"   # repo env, see pyproject.toml
    $PY scripts/figures/filament_spix.py                     # figure + table
    $PY scripts/figures/filament_spix.py --table-only

A separate script rather than a `figures.yml` entry because the figure *is* an
analysis: the numbers quoted on the slide come out of the same run that draws
it, so the two cannot drift apart. Regions come from the spec (`fil_arc`,
`fil_snake`, `fil_cane`) so there is still one definition of where each system
is.

Three things it does that a whole-box median gets wrong, all of which changed
the answer:

1. **Measure the filaments, not the boxes.** A box around a filament is mostly
   diffuse background, and around the Radio Arc that background includes
   thermal emission from the Sickle. Whole-box medians gave -0.58 / -0.87 /
   -1.22, which is largely a statement about three different backgrounds. A
   ridge filter on I0 picks the filaments out; on those pixels the raw medians
   are -0.25 / -0.70 / -1.11.

2. **Match in surface brightness before comparing.** Alpha flattens with
   brightness inside *every* system here, by about as much as the systems
   differ from each other -- the same estimator systematic the previous slide
   measures. Comparing unmatched populations therefore compares brightness
   distributions, not spectra. It is what made an earlier version of this slide
   claim the ordering "reverses" when matched; it does not, and it never did.

3. **Count beams, not pixels.** The in-band fit is at 11.74" x 10.77" on a
   2.31" grid, so a pixel is 1/27th of an independent sample. Errors quoted per
   pixel are ~5x too small and turn every difference into a detection.

What survives all three: the Radio Arc and the Snake agree to within 0.06 where
their brightnesses overlap, and the Cane is steeper than both by ~0.3 at better
than 5 sigma, with a comparable fitted uncertainty. So the population is mostly
homogeneous with one genuine outlier -- not the three-way spread the raw
numbers suggest.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skyfig  # noqa: E402
from skyfig import FS, SkyImage, THEME  # noqa: E402
from make_figures import REPO, Spec  # noqa: E402

# Gaussian beam solid angle over pixel area: 1.133 * bmaj * bmin / pix^2.
# 11.74" x 10.77" restored, 2.31"/pixel.
PIX_PER_BEAM = 1.133 * 11.74 * 10.77 / (2.31 ** 2)

SYSTEMS = [("Radio Arc", "fil_arc"), ("The Snake", "fil_snake"), ("The Cane", "fil_cane")]

# Factor-1.6 bins. Wide enough to hold a few tens of beams, narrow enough that
# the brightness trend inside one bin is small against the differences between
# systems.
EDGES = np.array([3, 5, 8, 13, 21, 34, 55, 90, 150]) * 1e-3

MIN_BEAMS = 8       # below this a median is not worth plotting
RIDGE_PCT = 90      # keep the top decile of ridge response


def ridge_mask(i0: np.ndarray, alpha: np.ndarray, aerr: np.ndarray) -> np.ndarray:
    """Pixels on a filament, well enough constrained to carry a spectral index.

    `sato` on log brightness: the filter responds to tube-like structure, and
    working in log stops the Arc's bright core dominating the response so
    completely that the fainter strands never clear the threshold. Sigmas of
    2-5 pixels match the 10-25 arcsec transverse widths these filaments have.
    """
    from skimage.filters import sato

    good = (np.isfinite(alpha) & (alpha != 0) & np.isfinite(aerr) & (aerr < 0.2)
            & np.isfinite(i0) & (i0 > 0))
    filled = np.where(np.isfinite(i0), i0, 0.0)
    tube = sato(np.log10(np.clip(filled, 1e-5, None)), sigmas=[2, 3, 4, 5],
                black_ridges=False)
    if not good.any():
        return good
    return good & (tube > np.percentile(tube[good], RIDGE_PCT))


def collect(spec: Spec) -> dict:
    alpha_i = spec.image("alpha")
    aerr_i = spec.image("alpha_err")
    i0_i = spec.image("i0")
    out = {}
    for name, key in SYSTEMS:
        r = spec.region(key)
        a = alpha_i.cutout(r["center"], r["width"], r["height"]).data
        e = aerr_i.cutout(r["center"], r["width"], r["height"]).data
        i = i0_i.cutout(r["center"], r["width"], r["height"]).data
        m = ridge_mask(i, a, e)
        out[name] = dict(alpha=a, aerr=e, i0=i, mask=m)
    return out


def binned(d: dict) -> list:
    """(centre, median, standard error, n_pixels) per brightness bin."""
    rows = []
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        m = d["mask"] & (d["i0"] >= lo) & (d["i0"] < hi)
        n = int(m.sum())
        if n / PIX_PER_BEAM < MIN_BEAMS:
            continue
        v = d["alpha"][m]
        # 1.2533 sigma/sqrt(N) is the large-sample standard error of a median.
        se = 1.2533 * float(np.std(v)) / np.sqrt(n / PIX_PER_BEAM)
        rows.append((float(np.sqrt(lo * hi)), float(np.median(v)), se, n))
    return rows


def report(data: dict) -> None:
    print(f"\nindependent samples = pixels / {PIX_PER_BEAM:.1f}   "
          f"(11.74\" x 10.77\" beam on a 2.31\" grid)\n")
    for name, _ in SYSTEMS:
        d = data[name]
        v = d["alpha"][d["mask"]]
        print(f"{name:11s} ridge pixels {d['mask'].sum():>7,}   "
              f"raw median {np.median(v):+.2f}")

    print(f"\n{'I0 (mJy/beam)':>14s} " + "".join(f"{n:>24s}" for n, _ in SYSTEMS))
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        cells = []
        for name, _ in SYSTEMS:
            d = data[name]
            m = d["mask"] & (d["i0"] >= lo) & (d["i0"] < hi)
            n = int(m.sum())
            if n / PIX_PER_BEAM < MIN_BEAMS:
                cells.append(f"{'--':>24s}")
                continue
            v = d["alpha"][m]
            se = 1.2533 * float(np.std(v)) / np.sqrt(n / PIX_PER_BEAM)
            cells.append(f"{np.median(v):+.2f} ± {se:.2f} ({n / PIX_PER_BEAM:>4.0f} bm)".rjust(24))
        print(f"{lo * 1e3:5.0f}-{hi * 1e3:<8.0f} " + "".join(cells))

    print("\npairwise, where both are populated:")
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        vals = {}
        for name, _ in SYSTEMS:
            d = data[name]
            m = d["mask"] & (d["i0"] >= lo) & (d["i0"] < hi)
            if int(m.sum()) / PIX_PER_BEAM < MIN_BEAMS:
                continue
            v = d["alpha"][m]
            vals[name] = (float(np.median(v)),
                          1.2533 * float(np.std(v)) / np.sqrt(int(m.sum()) / PIX_PER_BEAM))
        names = list(vals)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                (m1, s1), (m2, s2) = vals[names[i]], vals[names[j]]
                d_, s_ = m1 - m2, float(np.hypot(s1, s2))
                print(f"  {lo * 1e3:3.0f}-{hi * 1e3:<3.0f} mJy  {names[i]:10s} − "
                      f"{names[j]:10s} = {d_:+.2f} ± {s_:.2f}  ({abs(d_) / s_:4.1f}σ)")


def draw(data: dict, out: Path, dpi: int) -> Path:
    theme = THEME["dark"]
    fig = plt.figure(figsize=(13.5, 9.0))
    fig.patch.set_alpha(0.0)
    gs = fig.add_gridspec(2, 3, height_ratios=[0.78, 1.22], hspace=0.06, wspace=0.02)

    for k, (name, _) in enumerate(SYSTEMS):
        d = data[name]
        ax = fig.add_subplot(gs[0, k])
        ax.set_facecolor("none")
        shown = np.where(d["mask"], d["alpha"], np.nan)
        cmap = plt.get_cmap("Spectral_r").copy()
        cmap.set_bad(theme["blank"], alpha=0.0)
        im = ax.imshow(shown, origin="lower", cmap=cmap, vmin=-2.0, vmax=0.5,
                       interpolation="nearest")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.text(0.03, 0.97, name, transform=ax.transAxes, ha="left", va="top",
                color=theme["fg"], fontsize=FS["title"], fontweight="600",
                bbox=dict(boxstyle="round,pad=0.3", fc=theme["bg"], ec="none", alpha=0.7))
        if k == 2:
            cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
            cb.ax.tick_params(colors=theme["muted"], labelsize=FS["wcs_tick"])
            cb.outline.set_edgecolor(theme["muted"])
            cb.set_label("in-band α", color=theme["fg"], fontsize=FS["wcs_label"])

    ax = fig.add_subplot(gs[1, :])
    ax.set_facecolor("none")
    for k, (name, _) in enumerate(SYSTEMS):
        rows = binned(data[name])
        if not rows:
            continue
        x = [r[0] * 1e3 for r in rows]
        y = [r[1] for r in rows]
        e = [r[2] for r in rows]
        ax.errorbar(x, y, yerr=e, marker="o", ms=7, lw=2.0, capsize=4,
                    color=theme["series"][k], label=name)
    ax.set_xscale("log")
    ax.set_xlabel("surface brightness on the filament   I₀ at 797 MHz  (mJy/beam)",
                  color=theme["fg"], fontsize=FS["label"])
    ax.set_ylabel("median α", color=theme["fg"], fontsize=FS["label"])
    ax.tick_params(colors=theme["muted"], labelsize=FS["tick"])
    for side, s in ax.spines.items():
        s.set_visible(side in ("bottom", "left"))
        s.set_edgecolor(theme["muted"])
    ax.grid(color=theme["grid"], alpha=0.12, lw=0.6)
    # A log axis defaults to labelling every minor decade division, which at
    # this size is a wall of digits under the plot. Six round numbers is enough
    # to read a factor-of-two difference off the x axis from the back.
    from matplotlib.ticker import FixedLocator, NullFormatter, ScalarFormatter
    ax.xaxis.set_major_locator(FixedLocator([3, 5, 10, 20, 50, 100]))
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(2.7, 160)
    leg = ax.legend(loc="lower right", frameon=False, fontsize=FS["legend"],
                    labelspacing=0.3, handlelength=1.6)
    for t in leg.get_texts():
        t.set_color(theme["fg"])

    return skyfig.save(fig, out, dpi=dpi, transparent=True, theme=theme)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path,
                    default=Path(__file__).resolve().parent / "figures.yml")
    ap.add_argument("-o", "--output",
                    default="contributions/sgr-a-complex-uhf/images/filament-spix.png")
    ap.add_argument("--dpi", type=int, default=160)
    ap.add_argument("--table-only", action="store_true")
    args = ap.parse_args()

    spec = Spec(args.spec)
    data = collect(spec)
    report(data)
    if args.table_only:
        return 0
    out = Path(args.output)
    p = draw(data, out if out.is_absolute() else REPO / out, args.dpi)
    print(f"\n  wrote {p.relative_to(REPO)}  ({p.stat().st_size / 1e3:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
