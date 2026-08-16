#!/usr/bin/env python3
"""Azimuthal sidelobe profile of one or more PSFs.

The claim a mosaicking slide has to support is about *sidelobes*, and a PSF
image does not show them: the main lobes of two PSFs from the same array look
identical at any stretch that keeps the core visible, and at a stretch that
shows the far sidelobes the core saturates and the eye has nothing to compare.
The information is in how |PSF| falls with radius, which is a line plot.

For each logarithmic annulus this measures

    RMS |PSF|   -- how much spurious flux a source at that radius contributes
    max |PSF|   -- the worst case, which is what sets the dynamic range

and integrates the sidelobe power beyond the main lobe into a single number.

    PY=~/software/pfb-imaging/.venv/bin/python
    $PY scripts/figures/psf_profile.py \
        'Single pointing=fits_files/GC/norephase_..._psf_time0_mfs.fits' \
        'Joint / OTF=fits_files/GC/withbeam_..._psf_time0_mfs.fits' \
        -o contributions/sgr-a-complex-uhf/images/psf-sidelobes.png

Profiles are cached next to the FITS as `<stem>.psfprof.npz`, because a
15680^2 PSF takes a couple of minutes to walk and the plot always needs
several attempts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from astropy.io import fits

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skyfig  # noqa: E402
from skyfig import FS, THEME  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


def profile(path: Path, rmax_deg: float, nbins: int, chunk: int = 512,
            refresh: bool = False) -> dict:
    """Radial |PSF| statistics, accumulated a block of rows at a time.

    Streaming rather than loading the array: a 15680^2 float32 PSF is ~1 GB on
    disk and 2 GB promoted to float64, and two of them at once is enough to
    start swapping. Accumulating count/sum/sumsq/max per bin gives exact
    answers with bounded memory.

    Decimating first would be the easy alternative and it would be wrong -- a
    block mean lowers every peak, so the max-sidelobe curve, which is the one
    that matters for dynamic range, would come out systematically low.
    """
    cache = path.with_suffix(".psfprof.npz")
    if cache.is_file() and not refresh:
        z = np.load(cache, allow_pickle=True)
        if z["rmax"] == rmax_deg and z["nbins"] == nbins:
            return {k: z[k] for k in z.files}

    with fits.open(path, memmap=True) as hdul:
        h = hdul[0].header
        d = hdul[0].data
        while d.ndim > 2:
            d = d[0]
        ny, nx = d.shape
        pix = abs(float(h["CDELT1"]))                      # deg per pixel

        # Both PSFs peak at the exact centre pixel, which is what makes them
        # comparable despite different phase centres and image sizes. Verify
        # rather than assume: an off-centre peak silently turns every radius
        # into a different quantity.
        yc, xc = ny // 2, nx // 2
        core = np.asarray(d[yc - 2:yc + 3, xc - 2:xc + 3], dtype=np.float64)
        if not np.isclose(core[2, 2], np.nanmax(core)):
            die(f"{path.name}: peak is not at the centre pixel ({xc}, {yc})")

        edges = np.concatenate([[0.0], np.geomspace(pix, rmax_deg, nbins)])
        n = np.zeros(nbins + 1)
        ssq = np.zeros(nbins + 1)
        mx = np.zeros(nbins + 1)
        x = (np.arange(nx) - xc) * pix

        for y0 in range(0, ny, chunk):
            y1 = min(y0 + chunk, ny)
            blk = np.asarray(d[y0:y1], dtype=np.float64)
            yy = (np.arange(y0, y1) - yc) * pix
            r = np.hypot(yy[:, None], x[None, :]).ravel()
            a = np.abs(blk.ravel())
            k = np.digitize(r, edges) - 1
            keep = (k >= 0) & (k <= nbins) & np.isfinite(a)
            k, a = k[keep], a[keep]
            n += np.bincount(k, minlength=nbins + 1)
            ssq += np.bincount(k, weights=a * a, minlength=nbins + 1)
            # np.maximum.at is correct but very slow on millions of elements;
            # sorting once per block and slicing is ~50x faster here.
            order = np.argsort(k, kind="stable")
            ks, asort = k[order], a[order]
            bounds = np.searchsorted(ks, np.arange(nbins + 2))
            for b in range(nbins + 1):
                if bounds[b + 1] > bounds[b]:
                    m = asort[bounds[b]:bounds[b + 1]].max()
                    if m > mx[b]:
                        mx[b] = m

    with np.errstate(invalid="ignore", divide="ignore"):
        rms = np.sqrt(ssq / n)
    centres = np.sqrt(edges[:-1] * np.maximum(edges[1:], 1e-12))
    centres[0] = edges[1] / 2

    out = dict(r=centres[:nbins], rms=rms[:nbins], mx=mx[:nbins], n=n[:nbins],
               ssq=ssq[:nbins], pix=np.array(pix),
               bmaj=np.array(float(h.get("BMAJ", 0)) * 3600),
               bmin=np.array(float(h.get("BMIN", 0)) * 3600),
               wsum=np.array(float(h.get("WSUM", np.nan))),
               rmax=np.array(rmax_deg), nbins=np.array(nbins))
    np.savez(cache, **out)
    return out


def sidelobe_power(p: dict, inner_deg: float) -> float:
    """Total |PSF|^2 outside `inner_deg` -- one number for the whole pattern."""
    sel = p["r"] > inner_deg
    return float(np.nansum(p["ssq"][sel]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("psfs", nargs="+", metavar="LABEL=PATH")
    ap.add_argument("-o", "--output",
                    default="contributions/sgr-a-complex-uhf/images/psf-sidelobes.png")
    ap.add_argument("--rmax", type=float, default=3.0, help="max radius, degrees")
    ap.add_argument("--rmin-arcmin", type=float, default=0.5,
                    help="left edge of the plot; below this is main lobe")
    ap.add_argument("--nbins", type=int, default=90)
    ap.add_argument("--inner", type=float, default=0.01,
                    help="inner radius for integrated sidelobe power, degrees")
    ap.add_argument("--theme", default="dark", choices=sorted(THEME))
    ap.add_argument("--figsize", type=float, nargs=2, default=(9.5, 6.6))
    ap.add_argument("--dpi", type=int, default=170)
    ap.add_argument("--show-max", action="store_true", default=True)
    ap.add_argument("--refresh", action="store_true", help="ignore cached profiles")
    args = ap.parse_args()

    items = []
    for spec in args.psfs:
        label, _, path = spec.partition("=")
        if not path:
            label, path = Path(spec).stem, spec
        p = Path(path)
        if not p.is_absolute():
            p = REPO / path
        if not p.is_file():
            die(f"no such PSF: {p}")
        items.append((label, p))

    theme = THEME[args.theme]
    import matplotlib.pyplot as plt

    profs = []
    for label, path in items:
        print(f"{label}: {path.name}")
        pr = profile(path, args.rmax, args.nbins, refresh=args.refresh)
        print(f"   beam {pr['bmaj']:.2f}\" x {pr['bmin']:.2f}\"   "
              f"wsum {float(pr['wsum']):.4g}   "
              f"sidelobe power beyond {args.inner:g} deg = "
              f"{sidelobe_power(pr, args.inner):.4g}")
        profs.append((label, pr))

    fig = skyfig.new_figure(args.figsize, theme)
    gs = fig.add_gridspec(2, 1, height_ratios=[2.4, 1], hspace=0.08)
    ax = fig.add_subplot(gs[0])
    axr = fig.add_subplot(gs[1], sharex=ax)

    colours = theme["series"]
    rmin = args.rmin_arcmin
    for i, (label, p) in enumerate(profs):
        c = colours[i % len(colours)]
        r = p["r"] * 60.0
        sel = (r >= rmin) & np.isfinite(p["rms"]) & (p["rms"] > 0)
        ax.plot(r[sel], p["rms"][sel], color=c, lw=2.0, label=f"{label} — RMS")
        if args.show_max:
            ax.plot(r[sel], p["mx"][sel], color=c, lw=1.1, ls=":", alpha=0.85,
                    label=f"{label} — worst case")

    # Ratio of the first curve to each of the others: the improvement factor,
    # which is the number the slide is actually claiming.
    base = profs[0][1]
    for i, (label, p) in enumerate(profs[1:], start=1):
        c = colours[i % len(colours)]
        r = p["r"] * 60.0
        n = min(len(base["rms"]), len(p["rms"]))
        with np.errstate(invalid="ignore", divide="ignore"):
            ratio = base["rms"][:n] / p["rms"][:n]
        sel = (r[:n] >= rmin) & np.isfinite(ratio)
        axr.plot(r[:n][sel], ratio[sel], color=c, lw=2.0)
    axr.axhline(1.0, color=theme["muted"], lw=1.0, ls="--", alpha=0.8)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylabel("|PSF|", color=theme["fg"], fontsize=FS["label"])
    axr.set_xscale("log")
    axr.set_xlabel("radius from PSF peak  (arcmin)", color=theme["fg"], fontsize=FS["label"])
    axr.set_ylabel("improvement", color=theme["fg"], fontsize=FS["label"] - 3)
    axr.set_ylim(bottom=0)

    for a in (ax, axr):
        a.set_facecolor("none")
        a.tick_params(colors=theme["muted"], labelsize=FS["tick"], which="both")
        for side, spine in a.spines.items():
            spine.set_visible(side in ("bottom", "left"))
            spine.set_edgecolor(theme["muted"])
        a.grid(color=theme["grid"], alpha=0.12, lw=0.6, which="major")
    plt.setp(ax.get_xticklabels(), visible=False)

    leg = ax.legend(loc="upper right", frameon=False, fontsize=FS["legend"], ncol=1)
    for t in leg.get_texts():
        t.set_color(theme["fg"])

    if len(profs) == 2:
        a = sidelobe_power(profs[0][1], args.inner)
        b = sidelobe_power(profs[1][1], args.inner)
        ax.text(0.025, 0.04,
                f"integrated sidelobe power beyond {args.inner * 60:.0f}′\n"
                f"reduced by {a / b:.1f}×",
                transform=ax.transAxes, ha="left", va="bottom",
                color=theme["fg"], fontsize=FS["annot"], linespacing=1.5,
                bbox=dict(boxstyle="round,pad=0.4", fc=theme["bg"], ec="none",
                          alpha=0.65))

    out = Path(args.output)
    if not out.is_absolute():
        out = REPO / out
    p = skyfig.save(fig, out, dpi=args.dpi, transparent=True, theme=theme)
    rel = p.relative_to(REPO) if p.is_relative_to(REPO) else p
    print(f"\nwrote {rel}  ({p.stat().st_size / 1e3:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
