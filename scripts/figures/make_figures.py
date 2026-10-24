#!/usr/bin/env python3
"""Render the deck figures declared in a YAML spec.

    scripts/figures/make_figures.py --list
    scripts/figures/make_figures.py                       # everything
    scripts/figures/make_figures.py sgra-full spix-compare
    scripts/figures/make_figures.py --spec other.yml --dpi 220

A figure is a spec entry, not a script. The point is that "same cutout, same
colour scale, two imaging runs side by side" -- the comparison this talk turns
on -- is one `share_norm: true` rather than four hand-kept-in-sync copies of a
percentile calculation. When the copies drift, the comparison silently stops
being a comparison, and nothing in the figure says so.

Run it in the repo's uv environment (pyproject.toml):

    uv run scripts/figures/make_figures.py
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skyfig  # noqa: E402
from skyfig import Panel, SkyImage, THEME, make_norm  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


# --------------------------------------------------------------------------
# spec handling
# --------------------------------------------------------------------------

class Spec:
    def __init__(self, path: Path):
        self.path = path
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        self.data_root = (REPO / doc.get("data_root", ".")).resolve()
        self.out_root = (REPO / doc.get("out_root", ".")).resolve()
        self.theme = THEME[doc.get("theme", "dark")]
        self.dpi = int(doc.get("dpi", 150))
        self.max_pixels = int(doc.get("max_pixels", 2000))
        self.images = doc.get("images", {})
        self.regions = doc.get("regions", {})
        self.figures = doc.get("figures", {})
        self._cache: dict[str, SkyImage] = {}

    def image(self, key: str) -> SkyImage:
        """Load an image by spec key, once per run."""
        if key in self._cache:
            return self._cache[key]
        entry = self.images.get(key)
        if entry is None:
            die(f"unknown image {key!r}; spec defines {sorted(self.images)}")
        path = self.data_root / entry["file"]
        img = SkyImage.open(path, hdu=entry.get("hdu", 0),
                            blank_zeros=entry.get("blank_zeros", False),
                            label=entry.get("label", key))
        self._cache[key] = img
        return img

    def freq(self, key: str) -> float:
        """Reference frequency in Hz -- from the spec, else from the header."""
        entry = self.images.get(key, {})
        if "freq_hz" in entry:
            return float(entry["freq_hz"])
        h = self.image(key).header
        for k in ("RESTFRQ", "CRVAL3"):
            if k in h and float(h[k]) > 1e6:
                return float(h[k])
        die(f"no frequency for image {key!r}: set freq_hz in the spec")

    def region(self, name):
        if name is None:
            return {}
        if isinstance(name, dict):
            return name
        r = self.regions.get(name)
        if r is None:
            die(f"unknown region {name!r}; spec defines {sorted(self.regions)}")
        return r


# --------------------------------------------------------------------------
# panel data: either a named image, or something derived from two of them
# --------------------------------------------------------------------------

def resolve_panel_image(spec: Spec, p: dict, region: dict,
                        max_pixels: int) -> tuple[SkyImage, dict]:
    """The (cut, decimated) SkyImage a panel draws, plus its operands.

    The operands come back so a histogram panel can cut on the brightness of
    the image the map was derived from, without reloading and re-aligning it --
    which would be a second chance to get the region, mask or grid subtly
    different from the map it is supposed to describe.
    """
    op = p.get("op")
    if op is None:
        img = smooth_image(prepare(spec.image(p["image"]), region, max_pixels), p)
        return apply_mask_by(spec, img, p, region, max_pixels), {"a": img}

    if op == "mean":
        # Any number of images on a common grid. Written for the mean
        # sensitivity pattern -- three primary beams averaged is the mosaic's
        # actual response, and it is not the same picture as any one of them.
        first = prepare(spec.image(p["images"][0]), region, max_pixels)
        stack = [first.data] + [spec.image(k).reproject_onto(first).data
                                for k in p["images"][1:]]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            out = np.nanmean(np.stack(stack), axis=0)
        img = SkyImage(out, first.wcs, first.header, first.path, p.get("title"))
        return apply_mask_by(spec, smooth_image(img, p), p, region, max_pixels), {"a": first}

    if op in ("difference", "ratio", "spix"):
        a = prepare(spec.image(p["images"][0]), region, max_pixels)
        b = spec.image(p["images"][1])
        # Reproject onto a's grid *after* a is cut down, so we resample the
        # region being shown rather than the whole 5-degree mosaic.
        b = b.reproject_onto(a)
    else:
        die(f"unknown panel op {op!r}")

    with np.errstate(divide="ignore", invalid="ignore"):
        if op == "difference":
            out = a.data - b.data
        elif op == "ratio":
            out = a.data / b.data
        else:
            fa, fb = spec.freq(p["images"][0]), spec.freq(p["images"][1])
            if abs(np.log(fa / fb)) < 1e-6:
                die("spix needs two different frequencies")
            # Only positive brightness has a defined spectral index; negatives
            # are deconvolution residual and would otherwise come back as NaN
            # scattered through the map, which reads as a real structure.
            lo = p.get("mask_below")
            da = np.where(a.data > 0, a.data, np.nan)
            db = np.where(b.data > 0, b.data, np.nan)
            # Beam-correct *before* masking. `mask_below` is a brightness in Jy
            # per beam of the first image; applying that same number to both in
            # Jy/beam is a different surface-brightness cut in each whenever the
            # beams differ, and here the L-band beam is 1.63x smaller in area,
            # so the cut is 1.63x stricter at the high frequency. That
            # preferentially throws away pixels that are faint at L band --
            # which is to say the steep-spectrum ones -- so the mask selects on
            # the quantity being measured. Measured on this field it biases the
            # surviving median alpha by +0.08.
            da, db, scale_a = beam_correct(a, b, da, db, p, fa, fb)
            if lo is not None:
                cut = float(lo) / scale_a
                da = np.where(da > cut, da, np.nan)
                db = np.where(db > cut, db, np.nan)
            out = np.log(da / db) / np.log(fa / fb)

    img = SkyImage(out, a.wcs, a.header, a.path, p.get("title"))
    return apply_mask_by(spec, img, p, region, max_pixels), {"a": a, "b": b}


def smooth_image(img: SkyImage, p: dict) -> SkyImage:
    """Convolve with a Gaussian of `smooth` arcsec FWHM, if asked.

    A sparsity-prior model is close to a set of spikes on a pixel grid.
    Block-averaging it down for display turns those into single bright pixels
    scattered on black, which reads as noise rather than as the structure the
    model actually carries. A light convolution -- stated in the caption --
    is how a model is normally made legible.
    """
    fwhm = p.get("smooth")
    if not fwhm:
        return img
    from astropy.convolution import Gaussian2DKernel, convolve_fft

    sigma_pix = float(fwhm) / (2.0 * np.sqrt(2.0 * np.log(2.0))) / img.pixel_scale
    if sigma_pix < 0.3:
        return img
    out = convolve_fft(img.data, Gaussian2DKernel(sigma_pix),
                       nan_treatment="interpolate", preserve_nan=True,
                       allow_huge=True, normalize_kernel=True)
    return SkyImage(out, img.wcs, img.header, img.path, img.label)


def apply_mask_by(spec: Spec, img: SkyImage, p: dict, region: dict,
                  max_pixels: int) -> SkyImage:
    """Blank pixels where a companion map fails a threshold.

    Written for `alpha_err`: a fitted spectral index has a per-pixel
    uncertainty, and cutting on it is a far better mask than cutting on
    brightness, which is only a proxy for it. Takes one condition or a list.

        mask_by: {image: alpha_err, below: 0.2}
    """
    conds = p.get("mask_by")
    if not conds:
        return img
    if isinstance(conds, dict):
        conds = [conds]

    data = img.data
    for cond in conds:
        m = prepare(spec.image(cond["image"]), region, max_pixels)
        if m.data.shape != data.shape:
            m = m.reproject_onto(img)
        keep = np.isfinite(m.data)
        if "below" in cond:
            keep &= m.data < float(cond["below"])
        if "above" in cond:
            keep &= m.data > float(cond["above"])
        # Count what survives, not what the condition passes. The two differ
        # whenever the map already carries a mask of its own, and reporting the
        # condition's own count there gives percentages over 100.
        before = int(np.isfinite(data).sum())
        data = np.where(keep, data, np.nan)
        after = int(np.isfinite(data).sum())
        print(f"  mask_by {cond['image']}: {after:,} of {before:,} "
              f"finite pixels kept ({100 * after / max(before, 1):.1f}%)")
    return SkyImage(data, img.wcs, img.header, img.path, img.label)


def beam_correct(a: SkyImage, b: SkyImage, da, db, p: dict, fa: float, fb: float):
    """Put two Jy/beam images on a common surface-brightness scale.

    A spectral index is a ratio, so any constant factor between the two images
    lands on it directly: a beam-area ratio r biases alpha by
    log(r)/log(fa/fb). Here that is log(1.63)/log(797/1284) = -1.03, which is
    the difference between the -1.55 these images give raw and the -0.53 they
    give corrected -- the difference between "impossibly steep" and "ordinary
    non-thermal". It is not a detail, so it is on by default whenever both
    images declare a beam, and switched off only by saying so.

    Dividing by beam area converts Jy/beam to Jy/arcsec^2, which is exact for
    emission well resolved by *both* beams and wrong for anything approaching
    unresolved. The rigorous alternative is to convolve the sharper image to
    the broader beam before dividing; this is the cheap correction, and the
    figure should say which it used.

    Returns the two arrays and the scale applied to the first, so a caller can
    convert a Jy/beam threshold into the same units the arrays are now in.
    """
    want = p.get("beam_area_correct")
    ba, bb = a.beam, b.beam
    if want is False:
        return da, db, 1.0
    if ba is None or bb is None:
        if want:
            die("beam_area_correct needs a beam on both images; "
                "stamp one with scripts/figures/stamp_beam.py")
        print("  note: no beam on one or both images -- NO beam-area correction "
              "applied. Any beam mismatch appears as a spectral index offset.")
        return da, db, 1.0

    # Gaussian solid angle is proportional to bmaj*bmin; the constant cancels.
    area_a, area_b = ba[0] * ba[1], bb[0] * bb[1]
    ratio = area_a / area_b
    if abs(np.log(ratio)) < 1e-3:
        return da, db, 1.0
    offset = np.log(ratio) / np.log(fa / fb)
    print(f"  beam-area correction: {ba[0]:.2f}\"x{ba[1]:.2f}\" vs "
          f"{bb[0]:.2f}\"x{bb[1]:.2f}\", ratio {ratio:.3f} "
          f"-> removes an alpha offset of {offset:+.2f}")
    return da / area_a, db / area_b, area_a


def prepare(img: SkyImage, region: dict, max_pixels: int) -> SkyImage:
    img = img.cutout(center=region.get("center"),
                     width=region.get("width"),
                     height=region.get("height"))
    return img.decimate(max_pixels)


def histogram_series(spec: Spec, p: dict, img: SkyImage, operands: dict,
                     region: dict, max_pixels: int) -> list:
    """(label, values) pairs for a histogram panel.

    Three ways to get them, in order of precedence:

    * `series:` -- a list of full panel specs, each resolved independently.
      This is how two different estimates of the same quantity get compared.
    * `cuts:` -- thresholds on the first operand, splitting one array by
      brightness. A spectral index carries no signal-to-noise of its own, so
      faint pixels are a ratio of two small numbers; unseparated they broaden
      and shift the peak.
    * neither -- one series, every valid pixel.
    """
    if p.get("series"):
        out = []
        for s in p["series"]:
            simg, _ = resolve_panel_image(spec, s, region, max_pixels)
            out.append((s.get("label", s.get("image", s.get("op", "?"))), simg.data))
        return out

    cuts, ref = p.get("cuts"), operands.get("a")
    if cuts and ref is not None:
        unit = p.get("cut_unit", "mJy/beam")
        scale = 1e3 if unit.startswith("mJy") else 1.0
        return [(f"> {c * scale:g} {unit}",
                 np.where(np.isfinite(ref.data) & (ref.data > float(c)),
                          img.data, np.nan))
                for c in cuts]

    return [(p.get("label", "all pixels"), img.data)]


def norm_for(p: dict, img: SkyImage):
    return make_norm(
        img.data,
        stretch=p.get("stretch", "linear"),
        vmin=p.get("vmin"), vmax=p.get("vmax"),
        pmin=p.get("pmin"), pmax=p.get("pmax", 99.5),
        symmetric=p.get("symmetric", False),
        a=p.get("a"),
    )


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def render(spec: Spec, name: str, fig_spec: dict, dpi: int | None) -> Path:
    panels_spec = fig_spec.get("panels")
    if not panels_spec:
        die(f"figure {name!r} declares no panels")

    region = spec.region(fig_spec.get("region"))
    max_pixels = int(fig_spec.get("max_pixels", spec.max_pixels))

    is_hist = [p.get("plot") == "histogram" for p in panels_spec]
    is_dens = [p.get("plot") == "density" for p in panels_spec]

    # A density panel names its axes as `x:`/`y:` sub-specs, and a histogram
    # with `series:` names each series the same way. Neither has an image of its
    # own, so there is nothing to resolve up front for them.
    defers = [d or (h and bool(p.get("series")))
              for p, h, d in zip(panels_spec, is_hist, is_dens)]
    # A panel may override the figure's region. That turns one figure into a
    # row of zooms on unrelated sky positions -- several filaments on the same
    # colour scale, say -- which is the only honest way to ask whether a
    # population shares a property.
    regions = [spec.region(p["region"]) if p.get("region") else region
               for p in panels_spec]
    resolved = [(None, {}) if skip else resolve_panel_image(spec, p, rg, max_pixels)
                for p, rg, skip in zip(panels_spec, regions, defers)]
    images = [r[0] for r in resolved]
    operands = [r[1] for r in resolved]

    # A shared colour scale is the whole content of a comparison figure: two
    # panels on independent percentile scales look similar no matter how far
    # apart the data are.
    if fig_spec.get("share_norm"):
        src = fig_spec.get("norm_from", 0)
        i = src if isinstance(src, int) else [p.get("image") for p in panels_spec].index(src)
        shared = norm_for(panels_spec[i], images[i])
        norms = [shared] * len(images)
    else:
        norms = [None if (h or d) else norm_for(p, im)
                 for p, im, h, d in zip(panels_spec, images, is_hist, is_dens)]
    norms = [None if im is None else n for im, n in zip(images, norms)]

    n = len(panels_spec)
    rows, cols = fig_spec.get("layout", (1, n) if n <= 4 else (2, (n + 1) // 2))
    figsize = fig_spec.get("figsize", (5.5 * cols, 5.0 * rows))

    fig = skyfig.new_figure(figsize, spec.theme)
    axes = []
    for k, (p, img, norm) in enumerate(zip(panels_spec, images, norms)):
        r, c = divmod(k, cols)

        if is_hist[k]:
            series = histogram_series(spec, p, img, operands[k], regions[k], max_pixels)
            _, stats = skyfig.draw_histogram(fig, (rows, cols, k + 1), p,
                                             spec.theme, series)
            for label, n, med, mode in stats:
                print(f"  {label:<26} n={n:>9,}  median {med:+.2f}  peak {mode:+.2f}")
            continue

        if p.get("plot") == "density":
            xs, _ = resolve_panel_image(spec, p["x"], regions[k], max_pixels)
            ys, _ = resolve_panel_image(spec, p["y"], regions[k], max_pixels)
            _, (n, med, scat) = skyfig.draw_density(
                fig, (rows, cols, k + 1), xs.data, ys.data, p, spec.theme)
            print(f"  density: n={n:,}  median offset {med:+.2f}  scatter {scat:.2f}")
            continue

        panel = Panel(
            image=img,
            cmap=p.get("cmap", "inferno"),
            norm=norm,
            title=p.get("title"),
            # Only the outer edge of the grid carries coordinates -- interior
            # duplicates cost space that the figure needs for the sky.
            show_ra=p.get("show_ra", r == rows - 1),
            show_dec=p.get("show_dec", c == 0),
            grid=p.get("grid", fig_spec.get("grid", True)),
            beam=p.get("beam", fig_spec.get("beam", True)),
            colorbar=p.get("colorbar", fig_spec.get("colorbar", False)),
            cbar_label=p.get("cbar_label"),
            frame=p.get("frame", fig_spec.get("frame", True)),
            annotations=p.get("annotations", []),
            contours=p.get("contours"),
            contour_color=p.get("contour_color", "#ffffff"),
        )
        ax, _ = panel.draw(fig, (rows, cols, k + 1), spec.theme)

        # Outline the regions a later slide zooms into. Imported here rather
        # than at module scope: compare_regions imports this module, so a
        # top-level import would be circular.
        overlay = p.get("overlay_regions", fig_spec.get("overlay_regions"))
        if overlay:
            from compare_regions import read_boxes
            boxes = read_boxes(REPO / overlay, None, 2.0, 1.0)
            skyfig.draw_region_boxes(ax, img, boxes, spec.theme)

        axes.append(ax)

    fig.subplots_adjust(**fig_spec.get("adjust", {"hspace": 0.03, "wspace": 0.03}))

    out = spec.out_root / fig_spec.get("out", f"{name}.png")
    written = skyfig.save(fig, out, dpi=dpi or int(fig_spec.get("dpi", spec.dpi)),
                          transparent=fig_spec.get("transparent", True),
                          theme=spec.theme)

    # Two decks occasionally want the identical figure, and each deck keeps its
    # own images/ directory. Copying beats duplicating sixty lines of spec into
    # a second file, where the two would drift apart the first time either is
    # touched. Paths are repo-relative.
    for extra in fig_spec.get("copy_to", []) or []:
        dest = REPO / extra
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(written, dest)
        print(f"  also wrote {extra}")
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="figures to render (default: all)")
    ap.add_argument("--spec", type=Path,
                    default=Path(__file__).resolve().parent / "figures.yml")
    ap.add_argument("--list", action="store_true", help="list figures and exit")
    ap.add_argument("--inspect", action="store_true",
                    help="print what each declared image actually contains")
    ap.add_argument("--dpi", type=int, help="override the spec's dpi")
    args = ap.parse_args()

    if not args.spec.is_file():
        die(f"no such spec: {args.spec}")
    spec = Spec(args.spec)

    if args.list:
        for name, f in spec.figures.items():
            print(f"  {name:<22} -> {f.get('out', name + '.png')}"
                  f"   ({len(f.get('panels', []))} panel(s))")
        return 0

    if args.inspect:
        for key in spec.images:
            try:
                img = spec.image(key)
                print(f"  {key:<12} {img.describe()}")
                b = img.beam
                print(f"  {'':<12} bunit={img.bunit or '-'}  "
                      f"beam={f'{b[0]:.2f}x{b[1]:.2f}@{b[2]:.0f}' if b else '-'}  "
                      f"freq={spec.freq(key) / 1e6:.1f} MHz")
                fp = img.footprint()
                print(f"  {'':<12} data footprint: centre "
                      f"[{fp['center'][0]:.4f}, {fp['center'][1]:.4f}]  "
                      f"{fp['width']:.2f} x {fp['height']:.2f} deg  "
                      f"RA [{fp['ra_range'][0]:.3f}, {fp['ra_range'][1]:.3f}]  "
                      f"Dec [{fp['dec_range'][0]:.3f}, {fp['dec_range'][1]:.3f}]")
            except SystemExit:
                raise
            except Exception as e:
                print(f"  {key:<12} FAILED: {e}")
        return 0

    names = args.names or list(spec.figures)
    unknown = [n for n in names if n not in spec.figures]
    if unknown:
        die(f"unknown figure(s): {', '.join(unknown)}\n"
            f"       have: {', '.join(spec.figures)}")

    for name in names:
        t0 = time.time()
        print(f"{name} ...", flush=True)
        out = render(spec, name, spec.figures[name], args.dpi)
        rel = out.relative_to(REPO) if out.is_relative_to(REPO) else out
        print(f"  wrote {rel}  ({out.stat().st_size / 1e3:.0f} kB, "
              f"{time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
