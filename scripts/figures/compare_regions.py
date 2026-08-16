#!/usr/bin/env python3
"""Zoom on the same sky regions in two or more images, side by side.

Built for one specific argument: the UHF intrinsic model resolves structure
that the L-band restored image -- at a *higher* frequency, and so a finer
nominal resolution -- only just shows. If that holds at several independent
high-SNR locations, the model is carrying information below the restoring beam,
which is the claim. One region is an anecdote; a region file is the argument.

Regions come from a ds9 `.reg` or CASA `.crtf` file, so the choice of what to
zoom on stays a scientific decision made in a viewer, not a set of magic numbers
in a script. Rectangles, circles, ellipses and polygons all reduce to a box;
points take `--default-size`.

    PY=~/software/pfb-imaging/.venv/bin/python

    # the default pairing: UHF intrinsic model vs L-band restored
    $PY scripts/figures/compare_regions.py regions/superres.reg

    # three panels, model lightly smoothed, L-band beam supplied by hand
    $PY scripts/figures/compare_regions.py regions/superres.reg \
        --image 'joint_model:label=UHF intrinsic model:smooth=3' \
        --image 'joint:label=UHF restored (8.6")' \
        --image 'lband:label=L-band restored:beam=6.0x5.5@160' \
        -o contributions/sgr-a-complex-uhf/images/superres-zooms.png

Image keys are whatever `figures.yml` defines; a path to a FITS file also works.
Per-image options are appended to the key with colons:

    smooth=<arcsec>   convolve with a Gaussian of this FWHM before display
    beam=<b>x<b>@<pa> restoring beam in arcsec/deg, for images whose header has
                      none -- drawn bottom-left, so a reader can see for
                      themselves what counts as unresolved
    label=<text>      panel heading (default: the label from figures.yml)
    stretch, pmin, pmax, cmap   as in figures.yml

Each panel is scaled independently. A shared colour scale would be meaningless
here: the model is Jy/pixel and the restored images are Jy/beam.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from astropy.convolution import Gaussian2DKernel, convolve_fft
from astropy.coordinates import SkyCoord
import astropy.units as u

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skyfig  # noqa: E402
from skyfig import FS, Panel, SkyImage, THEME, make_norm  # noqa: E402
from make_figures import REPO, Spec  # noqa: E402

FWHM_TO_SIGMA = 1.0 / (2.0 * np.sqrt(2.0 * np.log(2.0)))


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


# --------------------------------------------------------------------------
# regions
# --------------------------------------------------------------------------

class Box:
    """A region reduced to what a cutout needs: centre, size, name."""

    __slots__ = ("center", "width", "height", "label")

    def __init__(self, center: SkyCoord, width: float, height: float, label: str):
        self.center, self.width, self.height, self.label = center, width, height, label

    def __repr__(self):
        return (f"{self.label}: {self.center.ra.deg:.4f} {self.center.dec.deg:.4f} "
                f"{self.width * 60:.2f}' x {self.height * 60:.2f}'")


def read_boxes(path: Path, fmt: str | None, default_size: float,
               pad: float) -> list[Box]:
    from regions import Regions

    if not path.is_file():
        die(f"no such region file: {path}")
    try:
        regs = Regions.read(str(path), format=fmt) if fmt else Regions.read(str(path))
    except Exception as e:
        die(f"could not read {path}: {e}\n"
            f"       pass --format ds9 or --format crtf if auto-detection failed")

    boxes: list[Box] = []
    for i, r in enumerate(regs, 1):
        c = getattr(r, "center", None)
        if c is None or not isinstance(c, SkyCoord):
            # A pixel-coordinate region has no sky centre and cannot be applied
            # to a second image on a different grid, which is the whole job.
            print(f"  skipping region {i} ({type(r).__name__}): not in sky coordinates")
            continue

        w = h = None
        if hasattr(r, "width") and hasattr(r, "height"):
            w = _deg(r.width)
            h = _deg(r.height)
        elif hasattr(r, "radius"):
            w = h = 2.0 * _deg(r.radius)
        elif hasattr(r, "outer_radius"):
            w = h = 2.0 * _deg(r.outer_radius)
        elif hasattr(r, "vertices"):
            v = r.vertices
            dec0 = float(np.mean(v.dec.deg))
            w = float(v.ra.deg.ptp()) * np.cos(np.deg2rad(dec0))
            h = float(v.dec.deg.ptp())
            c = SkyCoord(float(np.mean(v.ra.deg)), dec0, unit="deg")
        if not w or not h:
            w = h = default_size / 60.0

        meta = {**getattr(r, "meta", {}), **getattr(r, "visual", {})}
        label = meta.get("text") or meta.get("label") or f"region {i}"

        boxes.append(Box(c, w * pad, h * pad, str(label)))

    if not boxes:
        die(f"{path} yielded no usable sky regions")
    return boxes


def _deg(q) -> float:
    """Angle as degrees, whether it arrived as a Quantity or a bare number."""
    if isinstance(q, u.Quantity):
        return float(q.to(u.deg).value)
    return float(q)


# --------------------------------------------------------------------------
# per-image options
# --------------------------------------------------------------------------

def parse_image_arg(arg: str) -> tuple[str, dict]:
    """`key:opt=value:opt=value` -> (key, options).

    Split on colons that are followed by `word=`, so a label may contain one --
    `label=17h45m:the Arc` is a reasonable thing to write and should not be read
    as an option named `the Arc`.
    """
    import re

    parts = re.split(r":(?=[A-Za-z_]+=)", arg)
    key, opts = parts[0], {}
    for p in parts[1:]:
        k, _, v = p.partition("=")
        opts[k.strip()] = v.strip()
    return key, opts


def parse_beam(text: str) -> tuple[float, float, float]:
    """`8.55x7.76@160` in arcsec, arcsec, degrees."""
    try:
        axes, _, pa = text.partition("@")
        bmaj, _, bmin = axes.lower().partition("x")
        return float(bmaj), float(bmin), float(pa or 0.0)
    except ValueError:
        die(f"could not parse beam {text!r}; expected e.g. 8.55x7.76@160")


def load_image(spec: Spec, key: str, opts: dict) -> SkyImage:
    """A key from the spec, or a path to a FITS file."""
    if key in spec.images:
        img = spec.image(key)
    else:
        p = Path(key)
        if not p.is_absolute():
            p = (REPO / key) if (REPO / key).is_file() else (spec.data_root / key)
        img = SkyImage.open(p, blank_zeros=opts.get("blank_zeros", "").lower() == "true",
                            label=p.stem)

    if "beam" in opts:
        # Two of these mosaics reached us without BMAJ/BMIN. Stamping the beam
        # on the copy lets the figure show what "unresolved" looks like, which
        # is the only reason a reader can judge a super-resolution claim.
        bmaj, bmin, bpa = parse_beam(opts["beam"])
        img = SkyImage(img.data, img.wcs, img.header.copy(), img.path, img.label)
        img.header["BMAJ"] = bmaj / 3600.0
        img.header["BMIN"] = bmin / 3600.0
        img.header["BPA"] = bpa
    return img


def smooth(img: SkyImage, fwhm_arcsec: float) -> SkyImage:
    """Convolve with a Gaussian of the given FWHM.

    A model image is a set of delta functions on a pixel grid; displayed raw it
    is a field of single-pixel spikes and shows nothing about structure. A light
    convolution -- well below the restoring beam -- is how a model is normally
    made legible, and keeps the point intact so long as the kernel is stated.

    `convolve_fft` with `nan_treatment='interpolate'` so blanked sky does not
    eat a kernel-width border of every region.
    """
    sigma_pix = fwhm_arcsec * FWHM_TO_SIGMA / img.pixel_scale
    if sigma_pix < 0.3:
        return img
    kernel = Gaussian2DKernel(sigma_pix)
    out = convolve_fft(img.data, kernel, nan_treatment="interpolate",
                       preserve_nan=True, allow_huge=True, normalize_kernel=True)
    return SkyImage(out, img.wcs, img.header, img.path, img.label)


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def render(spec: Spec, boxes: list[Box], images: list[tuple[str, dict]],
           args) -> list[Path]:
    theme = THEME[args.theme]
    loaded = [(key, opts, load_image(spec, key, opts)) for key, opts in images]

    written: list[Path] = []
    missing_beam: set[str] = set()
    groups = [[b] for b in boxes] if args.per_region else [boxes]

    for gi, group in enumerate(groups):
        nrows, ncols = len(group), len(loaded)
        figsize = args.figsize or (4.6 * ncols, 4.8 * nrows)
        fig = skyfig.new_figure(figsize, theme)

        for ri, box in enumerate(group):
            for ci, (key, opts, img) in enumerate(loaded):
                cut = img.cutout(box.center, box.width, box.height)
                if not np.isfinite(cut.data).any():
                    print(f"  {box.label}: no data in {key} -- panel left blank")
                if "smooth" in opts:
                    cut = smooth(cut, float(opts["smooth"]))
                cut = cut.decimate(args.max_pixels)

                title = None
                if ri == 0:
                    title = opts.get("label") or img.label or key

                try:
                    norm = make_norm(
                        cut.data,
                        stretch=opts.get("stretch", args.stretch),
                        pmin=float(opts["pmin"]) if "pmin" in opts else args.pmin,
                        pmax=float(opts["pmax"]) if "pmax" in opts else args.pmax,
                    )
                except ValueError:
                    norm = None

                if img.beam is None:
                    missing_beam.add(opts.get("label") or key)

                panel = Panel(
                    image=cut,
                    cmap=opts.get("cmap", args.cmap),
                    norm=norm,
                    title=title,
                    # RA on every row, not just the bottom one. Rows are
                    # unrelated sky positions rather than a shared axis, so
                    # bottom-row-only labels would read as applying to the whole
                    # column and be wrong for every row above it. Dec is per-row
                    # already, and only the left panel needs it.
                    show_ra=True,
                    show_dec=(ci == 0),
                    grid=not args.no_grid,
                    beam=True,
                )
                ax, _ = panel.draw(fig, (nrows, ncols, ri * ncols + ci + 1), theme)

                if ci == 0 and nrows > 1:
                    # Region name down the left-hand side, so a reader can tie a
                    # row back to the region file it came from. With a single
                    # row the slide heading already names it, and the label just
                    # repeats the title in a second place.
                    ax.text(-0.14, 0.5, box.label, transform=ax.transAxes,
                            rotation=90, ha="center", va="center",
                            color=theme["accent"], fontsize=FS["title"], fontweight="600")

        # Room for a set of RA labels under every row.
        fig.subplots_adjust(hspace=0.28, wspace=0.06)

        out = Path(args.output)
        if args.per_region:
            stem = slug(group[0].label)
            out = out / f"{args.prefix}{stem}.png" if out.is_dir() or not out.suffix \
                else out.with_name(f"{out.stem}-{stem}{out.suffix}")
        elif out.is_dir() or not out.suffix:
            out = out / f"{args.prefix}zooms.png"
        if not out.is_absolute():
            out = REPO / out

        written.append(skyfig.save(fig, out, dpi=args.dpi, transparent=True,
                                   theme=theme))

    if missing_beam:
        # Worth saying out loud on a super-resolution figure specifically: the
        # claim is "structure finer than the beam", and without a beam drawn on
        # the panel the reader has nothing to measure that against.
        print(f"  note: no restoring beam in the header of "
              f"{', '.join(sorted(missing_beam))} -- no beam ellipse drawn. "
              f"Supply one with e.g. --image 'lband:beam=6.0x5.5@160'.")
    return written


def slug(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in text.strip()]
    s = "".join(keep)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "region"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("regions", type=Path, help="ds9 .reg or CASA .crtf file")
    ap.add_argument("--format", choices=["ds9", "crtf", "fits"],
                    help="override region-format auto-detection")
    ap.add_argument("--image", action="append", dest="images", metavar="KEY[:opt=val]",
                    help="repeatable; defaults to joint_model then lband")
    ap.add_argument("--spec", type=Path,
                    default=Path(__file__).resolve().parent / "figures.yml")
    ap.add_argument("-o", "--output", default="contributions/sgr-a-complex-uhf/images",
                    help="file, or directory when --per-region")
    ap.add_argument("--prefix", default="superres-", help="filename prefix")
    ap.add_argument("--per-region", action="store_true",
                    help="one PNG per region instead of one stacked figure")
    ap.add_argument("--default-size", type=float, default=2.0,
                    help="arcmin box for regions with no size (points)")
    ap.add_argument("--pad", type=float, default=1.0,
                    help="scale every region box by this factor")
    ap.add_argument("--stretch", default="log")
    ap.add_argument("--pmin", type=float, default=40.0)
    ap.add_argument("--pmax", type=float, default=99.8)
    ap.add_argument("--cmap", default="inferno")
    ap.add_argument("--theme", default="dark", choices=sorted(THEME))
    ap.add_argument("--max-pixels", type=int, default=900)
    ap.add_argument("--figsize", type=float, nargs=2)
    ap.add_argument("--dpi", type=int, default=170)
    ap.add_argument("--no-grid", action="store_true")
    ap.add_argument("--list", action="store_true", help="print the regions and exit")
    args = ap.parse_args()

    if not args.spec.is_file():
        die(f"no such spec: {args.spec}")
    spec = Spec(args.spec)

    boxes = read_boxes(args.regions, args.format, args.default_size, args.pad)
    if args.list:
        for b in boxes:
            print(f"  {b}")
        return 0

    images = [parse_image_arg(a) for a in (args.images or ["joint_model", "lband"])]

    print(f"{len(boxes)} region(s) x {len(images)} image(s)")
    for p in render(spec, boxes, images, args):
        rel = p.relative_to(REPO) if p.is_relative_to(REPO) else p
        print(f"  wrote {rel}  ({p.stat().st_size / 1e3:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
