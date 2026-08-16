"""Primitives for turning FITS sky images into slide-ready figures.

The scripts in `reference/` are the ancestors of this module: five near-identical
files from the Africanus III paper, each one a flat script that opens a FITS
file, hand-computes cutout indices, builds a norm, and draws a panel -- then
repeats all four steps verbatim three more times. Every fix had to be applied
n times, and the copies had already drifted apart by the time they were kept.

What is here is the same four steps factored once:

    load  -> SkyImage.open       squeeze degenerate axes, take the celestial WCS
    cut   -> SkyImage.cutout     Cutout2D, so the edge cases are astropy's
    scale -> make_norm           nan-aware percentiles, symmetric option
    draw  -> Panel.draw          one panel, with the dark-deck styling applied

`make_figures.py` drives it from a YAML spec so a figure is data, not code.

Two things this adds that the paper scripts had no need for:

* **Dark styling.** Paper figures are black-on-white serif. Dropped onto a
  #0d1117 slide they read as a bright rectangle with a glowing frame. Every
  figure here is drawn transparent with light text, so it sits on the slide
  instead of on top of it.
* **Decimation.** These mosaics are up to 11491 x 11817. Handing that to
  `imshow` for a 1500 px figure wastes minutes and memory to throw 98% of it
  away. `max_pixels` block-averages first.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
from astropy.visualization import (
    AsinhStretch,
    ImageNormalize,
    LinearStretch,
    LogStretch,
    PowerStretch,
    SqrtStretch,
)
from astropy.wcs import WCS
import astropy.units as u

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

# Palette lifted from templates/dark-academic.scss so figures and slides agree.
THEME = {
    "dark": {
        "bg": "#0d1117",
        "fg": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#7ee787",
        "grid": "#e6edf3",
        "blank": "#0d1117",   # colour painted under NaNs
        "series": ["#7ee787", "#58a6ff", "#d29922", "#f85149", "#bc8cff"],
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "muted": "#444444",
        "accent": "#006400",
        "grid": "#000000",
        "blank": "#ffffff",
        "series": ["#1b7837", "#2166ac", "#b8860b", "#b2182b", "#762a83"],
    },
}

# A figure written at 9x6 inches and dropped onto a 1050x700 slide at
# height="380" is displayed at roughly a third of its rendered size, so a 12pt
# axis label arrives on screen at about 4pt. These are the sizes that survive
# that reduction and read from the back of a hall.
FS = {
    "label": 20,       # axis labels on the analysis plots
    "tick": 16,
    "legend": 16,
    "annot": 17,       # the stats box
    "title": 20,
    "wcs_label": 15,   # sky panels are usually shown larger, so less scaling
    "wcs_tick": 13,
}

STRETCHES = {
    "linear": LinearStretch,
    "log": LogStretch,
    "sqrt": SqrtStretch,
    "asinh": AsinhStretch,
    "power": PowerStretch,
}


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

@dataclass
class SkyImage:
    """A 2-D sky image and the celestial WCS that goes with it."""

    data: np.ndarray
    wcs: WCS
    header: fits.Header
    path: Path | None = None
    label: str | None = None

    @classmethod
    def open(cls, path, hdu: int = 0, blank_zeros: bool = False,
             label: str | None = None) -> "SkyImage":
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"no such FITS file: {path}")
        with fits.open(path, memmap=True) as hdul:
            header = hdul[hdu].header.copy()
            wcs = WCS(header)
            data = hdul[hdu].data
            if data is None:
                raise ValueError(f"{path}[{hdu}] has no data")

            # `.celestial` picks the sky axes out of an (RA, Dec, FREQ, STOKES)
            # cube in one call. The paper scripts did `wcs.dropaxis(2)` twice,
            # which silently produces the wrong WCS the moment the axis order
            # differs -- and MFS images from different imagers do differ.
            wcs = wcs.celestial

            # Degenerate FREQ/STOKES axes are length 1, so squeeze is safe. A
            # genuine cube is not: take the first plane and say so, rather than
            # letting imshow fail three frames later with a shape error.
            arr = np.squeeze(np.asarray(data))
            while arr.ndim > 2:
                if arr.shape[0] != 1:
                    print(f"  note: {path.name} has a non-degenerate leading "
                          f"axis of length {arr.shape[0]}; using plane 0")
                arr = arr[0]
            if arr.ndim != 2:
                raise ValueError(f"{path}: expected a 2-D image, got {arr.shape}")

            # Materialise inside the `with`. `arr` is a view on the memmap, and
            # touching a memmap after its HDUList is closed is undefined -- it
            # reads correctly often enough to pass a smoke test and segfault
            # later on a bigger file.
            arr = arr.astype(np.float64, copy=True)

        # WSClean and friends occasionally write CRVAL1 outside [0, 360). The
        # paper scripts patched this per-file with `wcs.wcs.crval[0] += 360`,
        # which is the same fix applied by hand only where someone noticed.
        if wcs.wcs.crval[0] < 0:
            wcs.wcs.crval[0] += 360.0
        elif wcs.wcs.crval[0] >= 360.0:
            wcs.wcs.crval[0] -= 360.0

        if blank_zeros:
            # Mosaics are zero-filled outside the primary-beam cutoff. Left as
            # zeros they anchor the percentiles and paint a hard black frame
            # around the field; as NaN they simply do not draw.
            arr[arr == 0.0] = np.nan

        return cls(arr, wcs, header, path=path, label=label)

    # -- metadata -----------------------------------------------------------

    @property
    def pixel_scale(self) -> float:
        """Arcsec per pixel, from the WCS rather than from CDELT."""
        return float(np.abs(self.wcs.pixel_scale_matrix[0, 0]) * 3600.0)

    @property
    def beam(self) -> tuple[float, float, float] | None:
        """(BMAJ, BMIN) in arcsec and BPA in degrees, or None if unrecorded."""
        h = self.header
        if "BMAJ" in h and "BMIN" in h:
            return float(h["BMAJ"]) * 3600, float(h["BMIN"]) * 3600, float(h.get("BPA", 0.0))
        return None

    @property
    def bunit(self) -> str:
        return str(self.header.get("BUNIT", "")).strip()

    def center(self) -> SkyCoord:
        ny, nx = self.data.shape
        return self.wcs.pixel_to_world(nx / 2, ny / 2)

    def footprint(self) -> dict:
        """Sky bounding box of the pixels that actually carry data.

        Corner positions go through `wcs_pix2world`, not `wcs.pixel_to_world`:
        the high-level call returns a wrong position for the specific argument
        pair `(0, 0)` -- scalar Python zeros -- while being correct for every
        other pixel and for `([0], [0])`. Corner 0 is exactly the one a
        footprint wants, so the quirk lands squarely on this calculation.
        """
        finite = np.isfinite(self.data)
        if not finite.any():
            raise ValueError(f"{self.path}: no finite pixels")
        ys, xs = np.where(finite.any(axis=1))[0], np.where(finite.any(axis=0))[0]
        y0, y1, x0, x1 = ys[0], ys[-1], xs[0], xs[-1]
        corners = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1],
                            [(x0 + x1) / 2, (y0 + y1) / 2]], dtype=float)
        sky = self.wcs.wcs_pix2world(corners, 0)
        ra, dec = sky[:4, 0], sky[:4, 1]
        cra, cdec = sky[4]
        return {
            "center": (float(cra), float(cdec)),
            "ra_range": (float(ra.min()), float(ra.max())),
            "dec_range": (float(dec.min()), float(dec.max())),
            "width": float((ra.max() - ra.min()) * np.cos(np.deg2rad(cdec))),
            "height": float(dec.max() - dec.min()),
        }

    def describe(self) -> str:
        ny, nx = self.data.shape
        p = self.pixel_scale
        return (f"{nx}x{ny}  {p:.2f}\"/pix  "
                f"{nx * p / 3600:.2f}x{ny * p / 3600:.2f} deg  "
                f"{self.header.get('CTYPE1', '?')}")

    # -- transforms ---------------------------------------------------------

    def cutout(self, center=None, width=None, height=None) -> "SkyImage":
        """Sub-image around `center` spanning width x height degrees.

        `center` is a SkyCoord, an (ra_deg, dec_deg) pair, a sexagesimal string,
        or None for the image centre. Cutout2D handles partial overlap and
        rewrites the WCS; the hand-rolled index arithmetic it replaces relied on
        CDELT1 being negative and swapped x_min/x_max to compensate.
        """
        if width is None and height is None:
            return self
        c = as_skycoord(center) if center is not None else self.center()
        h = height if height is not None else width
        w = width if width is not None else height
        cut = Cutout2D(self.data, c, (h * u.deg, w * u.deg), wcs=self.wcs,
                       mode="partial", fill_value=np.nan, copy=True)
        return SkyImage(cut.data, cut.wcs, self.header, self.path, self.label)

    def decimate(self, max_pixels: int) -> "SkyImage":
        """Block-average down to at most `max_pixels` on the long axis.

        Block mean rather than striding: striding drops point sources entirely
        whenever the stride steps over them, which on this field silently
        deletes the compact emission the figure exists to show.
        """
        ny, nx = self.data.shape
        n = int(np.ceil(max(ny, nx) / max_pixels))
        if n <= 1:
            return self
        ty, tx = (ny // n) * n, (nx // n) * n
        blocks = self.data[:ty, :tx].reshape(ty // n, n, tx // n, n)
        # An all-NaN block is ordinary here -- it is sky outside the mosaic
        # footprint -- and nanmean warns on every one of them.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            small = np.nanmean(blocks, axis=(1, 3))
        wcs = self.wcs.slice((slice(0, ty), slice(0, tx)))[::n, ::n]
        return SkyImage(small, wcs, self.header, self.path, self.label)

    def reproject_onto(self, other: "SkyImage") -> "SkyImage":
        """Resample onto another image's grid, for differencing.

        Needed here rather than optional: the joint mosaic is RA---SIN at
        2.31"/pix and the image-space mosaics are RA---TAN at 1.70" and 0.99".
        Subtracting those arrays directly compares unrelated sky positions.
        """
        from reproject import reproject_interp

        arr, _ = reproject_interp((self.data, self.wcs), other.wcs,
                                  shape_out=other.data.shape)
        return SkyImage(arr, other.wcs, self.header, self.path, self.label)


def as_skycoord(value) -> SkyCoord:
    """Accept a SkyCoord, an (ra_deg, dec_deg) pair, or a sexagesimal string."""
    if isinstance(value, SkyCoord):
        return value
    if isinstance(value, str):
        return SkyCoord(value, unit=(u.hourangle, u.deg))
    ra, dec = value
    return SkyCoord(float(ra), float(dec), unit="deg")


# --------------------------------------------------------------------------
# scaling
# --------------------------------------------------------------------------

def make_norm(data: np.ndarray, stretch: str = "linear", vmin=None, vmax=None,
              pmin: float | None = None, pmax: float | None = 99.5,
              symmetric: bool = False, a: float | None = None) -> ImageNormalize:
    """Build an ImageNormalize, taking limits from percentiles by default.

    All percentiles are nan-aware. The paper scripts used bare `np.percentile`
    on arrays that are a third NaN outside the mosaic footprint, which returns
    NaN for every limit and hands imshow a norm that renders nothing.
    """
    finite = data[np.isfinite(data)]
    if finite.size == 0:
        raise ValueError("image is entirely blank -- nothing to scale")

    if vmax is None:
        vmax = float(np.percentile(finite, pmax)) if pmax is not None else float(finite.max())
    if vmin is None:
        if symmetric:
            vmin = -abs(vmax)
        elif pmin is not None:
            vmin = float(np.percentile(finite, pmin))
        else:
            vmin = float(finite.min())
    if symmetric:
        m = max(abs(vmin), abs(vmax))
        vmin, vmax = -m, m

    cls = STRETCHES.get(stretch)
    if cls is None:
        raise ValueError(f"unknown stretch {stretch!r}; have {sorted(STRETCHES)}")
    kwargs = {}
    if a is not None and stretch in ("log", "asinh", "power"):
        kwargs["a" if stretch != "power" else "a"] = a

    # A log stretch maps [vmin, vmax] onto [0, 1] before stretching, so vmin
    # need not be positive -- but vmin == vmax collapses it to a divide by zero.
    if vmax <= vmin:
        vmax = vmin + (abs(vmin) or 1.0) * 1e-6
    return ImageNormalize(vmin=vmin, vmax=vmax, stretch=cls(**kwargs))


# --------------------------------------------------------------------------
# drawing
# --------------------------------------------------------------------------

@dataclass
class Panel:
    """One image panel: what to draw and which decorations to hang on it."""

    image: SkyImage
    cmap: str = "inferno"
    norm: ImageNormalize | None = None
    title: str | None = None
    show_ra: bool = True
    show_dec: bool = True
    grid: bool = True
    beam: bool = True
    colorbar: bool = False
    cbar_label: str | None = None
    frame: bool = True
    annotations: list = field(default_factory=list)

    def draw(self, fig, subplot_spec, theme: dict):
        """`subplot_spec` is an (nrows, ncols, index) triple.

        It has to be unpacked: matplotlib reads a single 3-tuple argument as
        Bbox bounds, so passing it whole fails inside Bbox.from_bounds with a
        message that says nothing about subplots.
        """
        img = self.image
        ax = fig.add_subplot(*subplot_spec, projection=img.wcs)

        cmap = plt.get_cmap(self.cmap).copy()
        cmap.set_bad(theme["blank"], alpha=0.0)   # blanked sky shows the slide

        norm = self.norm if self.norm is not None else make_norm(img.data)
        im = ax.imshow(img.data, cmap=cmap, norm=norm, origin="lower",
                       interpolation="nearest")

        style_wcsaxes(ax, theme, show_ra=self.show_ra, show_dec=self.show_dec,
                      grid=self.grid, frame=self.frame)

        if self.title:
            ax.text(0.03, 0.97, self.title, transform=ax.transAxes,
                    ha="left", va="top", color=theme["fg"], fontsize=FS["title"],
                    fontweight="600",
                    bbox=dict(boxstyle="round,pad=0.35", fc=theme["bg"],
                              ec="none", alpha=0.65))

        if self.beam and img.beam is not None:
            draw_beam(ax, img, theme)

        for ann in self.annotations:
            draw_annotation(ax, img, ann, theme)

        if self.colorbar:
            cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
            cb.ax.tick_params(colors=theme["muted"], labelsize=FS["wcs_tick"])
            cb.outline.set_edgecolor(theme["muted"])
            label = self.cbar_label if self.cbar_label is not None else img.bunit
            if label:
                cb.set_label(label, color=theme["fg"], fontsize=FS["wcs_label"])

        return ax, im


def style_wcsaxes(ax, theme: dict, show_ra=True, show_dec=True, grid=True,
                  frame=True):
    """Apply the dark-deck styling to a WCSAxes.

    Tick labels, axis labels, spines and the coordinate grid each carry their
    own colour on a WCSAxes and none of them follow rcParams, so a figure styled
    only through rcParams comes out with black ticks on a transparent
    background -- invisible on the slide, and invisible in a light-background
    preview too, which is how it survives review.
    """
    ax.set_facecolor("none")
    ra, dec = ax.coords[0], ax.coords[1]

    # Pin each axis label to its own edge. Setting "bl" on both -- the obvious
    # loop over ax.coords -- draws RA and Dec on the bottom *and* the left, so
    # the two labels sit on top of each other and neither is readable.
    ra.set_ticks_position("b")
    ra.set_axislabel_position("b")
    dec.set_ticks_position("l")
    dec.set_axislabel_position("l")
    for s in (ra, dec):
        s.set_ticklabel(color=theme["muted"], size=FS["wcs_tick"])
        s.set_ticks(color=theme["muted"])

    if grid:
        ax.coords.grid(color=theme["grid"], alpha=0.18, linestyle="solid",
                       linewidth=0.6)

    if show_ra:
        ra.set_axislabel("Right Ascension (J2000)", color=theme["fg"], size=FS["wcs_label"])
    else:
        ra.set_ticklabel_visible(False)
        ra.set_axislabel("")
    if show_dec:
        dec.set_axislabel("Declination (J2000)", color=theme["fg"], size=FS["wcs_label"])
    else:
        dec.set_ticklabel_visible(False)
        dec.set_axislabel("")

    if frame:
        for spine in ax.spines.values():
            spine.set_edgecolor(theme["muted"])
            spine.set_linewidth(0.8)
    else:
        # Full-bleed background slides: no frame, no ticks, nothing but sky.
        for spine in ax.spines.values():
            spine.set_visible(False)
        for s in (ra, dec):
            s.set_ticks_visible(False)
            s.set_ticklabel_visible(False)


def draw_beam(ax, img: SkyImage, theme: dict, corner=(0.055, 0.055)):
    """Restoring beam ellipse, bottom-left, in pixels on the current cutout."""
    bmaj, bmin, bpa = img.beam
    px = img.pixel_scale
    ny, nx = img.data.shape
    x = corner[0] * nx
    y = corner[1] * ny
    # BPA is measured from north through east; matplotlib measures anticlockwise
    # from the x axis, and with RA increasing to the left that is BPA + 90.
    e = Ellipse((x, y), width=bmin / px, height=bmaj / px, angle=bpa + 90.0,
                facecolor=theme["fg"], edgecolor=theme["fg"], alpha=0.85, lw=1.0)
    ax.add_patch(e)


def draw_region_boxes(ax, img: SkyImage, boxes, theme: dict, color=None,
                      label: bool = True, fontsize: int | None = None):
    """Outline the regions a later slide zooms into, on the wide view.

    A zoom panel on its own leaves the audience to guess where in the field it
    came from, and on a five-degree mosaic of the Galactic Centre that guess is
    not available to anyone who has not spent a year with the image. Drawing the
    boxes on the overview first is what makes the zooms readable.

    `boxes` are compare_regions.Box instances -- centre as a SkyCoord, width and
    height in degrees.
    """
    from matplotlib.patches import Rectangle

    color = color or theme["accent"]
    fs = fontsize if fontsize is not None else FS["wcs_label"]
    px = img.pixel_scale / 3600.0                       # degrees per pixel
    for b in boxes:
        x, y = img.wcs.world_to_pixel(b.center)
        if not (np.isfinite(x) and np.isfinite(y)):
            continue
        w, h = b.width / px, b.height / px
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fill=False,
                               edgecolor=color, lw=1.8, zorder=6))
        if label and b.label:
            ax.text(x, y + h / 2 + 8, b.label, ha="center", va="bottom",
                    color=color, fontsize=fs, fontweight="600", zorder=7,
                    bbox=dict(boxstyle="round,pad=0.25", fc=theme["bg"],
                              ec="none", alpha=0.6))


def draw_annotation(ax, img: SkyImage, ann: dict, theme: dict):
    """Label a sky position: {position, text, [color], [marker], [offset]}."""
    c = as_skycoord(ann["position"])
    x, y = img.wcs.world_to_pixel(c)
    if not (np.isfinite(x) and np.isfinite(y)):
        return
    color = ann.get("color", theme["accent"])
    if ann.get("marker", True):
        ax.plot(x, y, marker=ann.get("marker_style", "o"), ms=ann.get("size", 7),
                mfc="none", mec=color, mew=1.4)
    dx, dy = ann.get("offset", (12, 12))
    ax.annotate(ann.get("text", ""), (x, y), textcoords="offset points",
                xytext=(dx, dy), color=color, fontsize=ann.get("fontsize", 11),
                fontweight="600")


def draw_histogram(fig, subplot_spec, opts: dict, theme: dict, series: list):
    """Distributions of one or more derived maps -- spectral indices, differences.

    `series` is a list of (label, values array). The arrays arrive already
    computed rather than being re-derived here, so a histogram is always of
    exactly the pixels its map shows: same region, same mask, same beam
    correction. Recomputing is how a histogram ends up quietly describing a
    different population from the image beside it.

    Overlaying series is the point when the question is whether two independent
    estimates of the same quantity agree -- an in-band fit against a two-band
    ratio, say. Each keeps its own pixel population, which is correct: they do
    not have the same valid mask and forcing them onto one would silently
    discard the disagreement being looked for.
    """
    ax = fig.add_subplot(*subplot_spec)
    ax.set_facecolor("none")

    if not series:
        raise ValueError("no series to histogram")
    pooled = np.concatenate([v[np.isfinite(v)].ravel() for _, v in series])
    if pooled.size == 0:
        raise ValueError("nothing finite to histogram")

    lo, hi = opts.get("range", (None, None))
    if lo is None:
        lo = float(np.percentile(pooled, 0.5))
    if hi is None:
        hi = float(np.percentile(pooled, 99.5))
    bins = np.linspace(float(lo), float(hi), int(opts.get("bins", 120)) + 1)
    centres = 0.5 * (bins[1:] + bins[:-1])

    band = opts.get("highlight")
    if band:
        ax.axvspan(float(band[0]), float(band[1]), color=theme["fg"], alpha=0.08,
                   zorder=0, lw=0)

    colours = theme["series"]
    stats = []
    for i, (label, values) in enumerate(series):
        v = values[np.isfinite(values)].ravel()
        if v.size < 10:
            continue
        colour = colours[i % len(colours)]
        counts, _ = np.histogram(v, bins=bins, density=True)
        # Pixel counts belong in the legend when the question is "over how much
        # sky", and are noise when the point is the shape of the distribution.
        # On a slide they roughly double the legend's width for a number nobody
        # reads from the back of the room, so they are opt-out.
        text = f"{label}   n={v.size:,}" if opts.get("legend_counts", True) else label
        ax.step(centres, counts, where="mid", color=colour, lw=1.8, label=text)
        ax.fill_between(centres, counts, step="mid", color=colour, alpha=0.13, lw=0)

        med = float(np.median(v))
        # Peak of the binned distribution, which is what the eye reads off the
        # plot -- not the same number as the median on a skewed distribution,
        # and on these maps they differ by a few tenths.
        mode = float(centres[int(np.argmax(counts))])
        ax.axvline(med, color=colour, ls="--", lw=1.1, alpha=0.75)
        stats.append((label, v.size, med, mode))

    ax.set_xlim(bins[0], bins[-1])
    ax.set_ylim(bottom=0)
    ax.set_xlabel(opts.get("xlabel", ""), color=theme["fg"], fontsize=FS["label"])
    ax.set_ylabel(opts.get("ylabel", "density"), color=theme["fg"], fontsize=FS["label"])
    ax.tick_params(colors=theme["muted"], labelsize=FS["tick"])
    for side, spine in ax.spines.items():
        spine.set_visible(side in ("bottom", "left"))
        spine.set_edgecolor(theme["muted"])
    ax.grid(color=theme["grid"], alpha=0.12, lw=0.6)

    leg = ax.legend(loc=opts.get("legend_loc", "upper left"), frameon=False,
                    fontsize=opts.get("legend_fontsize", FS["legend"]),
                    labelspacing=0.35, handlelength=1.4, borderpad=0.2)
    for text in leg.get_texts():
        text.set_color(theme["fg"])

    if opts.get("title"):
        ax.set_title(opts["title"], color=theme["fg"], fontsize=FS["title"],
                     fontweight="600", loc="left")

    return ax, stats


def draw_density(fig, subplot_spec, x: np.ndarray, y: np.ndarray, opts: dict,
                 theme: dict):
    """Pixel-by-pixel density of one estimate against another.

    A pair of histograms shows that two estimates cover the same range. It
    cannot show whether they agree *pixel by pixel* -- two maps with identical
    distributions can disagree everywhere. This can, and it is the plot that
    answers "systematically compare".

    Both arrays must be on the same grid; the caller is responsible for that,
    and a shape mismatch is an error rather than something to broadcast around.
    """
    if x.shape != y.shape:
        raise ValueError(f"density needs matching grids, got {x.shape} and {y.shape}")

    ax = fig.add_subplot(*subplot_spec)
    ax.set_facecolor("none")

    good = np.isfinite(x) & np.isfinite(y)
    xv, yv = x[good].ravel(), y[good].ravel()
    if xv.size < 10:
        raise ValueError("density: fewer than 10 pixels valid in both maps")

    lo, hi = opts.get("range", (None, None))
    if lo is None:
        lo = float(np.percentile(xv, 1))
    if hi is None:
        hi = float(np.percentile(xv, 99))

    # The axes share a range only when both sides are the same quantity.
    # Plotting a spectral index against its own uncertainty on a square axis,
    # with a 1:1 line and a "median offset", is three statements that are each
    # meaningless. Supplying `yrange` declares the two axes different and turns
    # all three off.
    yr = opts.get("yrange")
    comparison = yr is None
    ylo, yhi = (lo, hi) if comparison else (float(yr[0]), float(yr[1]))

    from matplotlib.colors import LogNorm
    hb = ax.hexbin(xv, yv, gridsize=int(opts.get("gridsize", 90)),
                   extent=(lo, hi, ylo, yhi), cmap=opts.get("cmap", "magma"),
                   norm=LogNorm(), mincnt=1, linewidths=0)

    if opts.get("identity", comparison):
        # Accent rather than fg: a white 1:1 line vanishes into the light end of
        # every sequential colormap, which is exactly where the ridge is.
        ax.plot([lo, hi], [lo, hi], color=theme["accent"], lw=1.4, ls="--",
                alpha=0.9, zorder=5, label="1:1")

    stats = (xv.size, float("nan"), float("nan"))
    if opts.get("stats", comparison):
        # Median offset and scatter, which is the number a reader wants and
        # cannot read off a hexbin. Median rather than mean: the tails on these
        # maps are unconstrained fits, not physics.
        d = yv - xv
        med = float(np.median(d))
        scat = float(np.diff(np.percentile(d, [16, 84]))[0] / 2)
        stats = (xv.size, med, scat)
        txt = f"n = {xv.size:,}\nmedian Δ = {med:+.2f}\nscatter = {scat:.2f}"
    else:
        txt = f"n = {xv.size:,}"
    ax.text(0.035, 0.965, txt, transform=ax.transAxes, ha="left", va="top",
            color=theme["fg"], fontsize=FS["annot"], linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.4", fc=theme["bg"], ec="none", alpha=0.65))

    # Running median of y in bins of x -- on a plot where the two axes are
    # different quantities, the trend is the result and a hexbin alone hides it
    # under the density of the faint end.
    if opts.get("running_median"):
        edges = np.linspace(lo, hi, int(opts.get("running_bins", 24)) + 1)
        idx = np.digitize(xv, edges) - 1
        bx, by = [], []
        for k in range(len(edges) - 1):
            sel = idx == k
            if sel.sum() >= 50:
                bx.append(0.5 * (edges[k] + edges[k + 1]))
                by.append(float(np.median(yv[sel])))
        if bx:
            ax.plot(bx, by, color=theme["accent"], lw=2.0, zorder=6,
                    label="running median")

    ax.set_xlim(lo, hi)
    ax.set_ylim(ylo, yhi)
    if comparison:
        ax.set_aspect("equal")
    ax.set_xlabel(opts.get("xlabel", ""), color=theme["fg"], fontsize=FS["label"])
    ax.set_ylabel(opts.get("ylabel", ""), color=theme["fg"], fontsize=FS["label"])
    ax.tick_params(colors=theme["muted"], labelsize=FS["tick"])
    for side, spine in ax.spines.items():
        spine.set_visible(side in ("bottom", "left"))
        spine.set_edgecolor(theme["muted"])
    ax.grid(color=theme["grid"], alpha=0.12, lw=0.6)
    if opts.get("title"):
        ax.set_title(opts["title"], color=theme["fg"], fontsize=13,
                     fontweight="600", loc="left")

    if opts.get("colorbar", True):
        cb = fig.colorbar(hb, ax=ax, fraction=0.046, pad=0.02)
        cb.ax.tick_params(colors=theme["muted"], labelsize=FS["tick"])
        cb.outline.set_edgecolor(theme["muted"])
        cb.set_label("pixels per bin", color=theme["fg"], fontsize=FS["label"])

    return ax, stats


def new_figure(figsize, theme: dict):
    fig = plt.figure(figsize=figsize)
    fig.patch.set_alpha(0.0)
    return fig


def save(fig, out_path, dpi: int = 150, transparent: bool = True,
         theme: dict | None = None, pad: float = 0.02):
    """Write the PNG, making the parent directory if needed.

    Transparent by default so the figure inherits whatever the slide is doing --
    including the full-bleed background slides, where an opaque #0d1117 margin
    would show as a rectangle over the image.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", pad_inches=pad,
                transparent=transparent,
                facecolor="none" if transparent else theme["bg"])
    plt.close(fig)
    return out_path
