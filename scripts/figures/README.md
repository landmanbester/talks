# Deck figures from FITS

Every PNG in a deck's `images/` that came from a FITS image is declared in
`figures.yml` and rendered by `make_figures.py`. The FITS themselves live under
`fits_files/` and are gitignored; the spec is the tracked record of how each
figure was made, so a figure can be regenerated or corrected without anyone
having to remember which percentile was used.

## Running

Runs in the repo's uv environment (`uv sync` once; see `pyproject.toml`):

```bash
PY="uv run"

$PY scripts/figures/make_figures.py --list         # what is declared
$PY scripts/figures/make_figures.py --inspect      # what the FITS actually contain
$PY scripts/figures/make_figures.py                # render everything
$PY scripts/figures/make_figures.py sgra-full mosaic-compare
$PY scripts/figures/make_figures.py --dpi 220 sgra-full
```

`--inspect` is the one to run first after new data lands: it prints shape, pixel
scale, projection, BUNIT, restoring beam, reference frequency and the sky
bounding box of the pixels that are not blank. Region definitions in the spec
should be derived from those footprints rather than guessed.

## Files

| File | What it is |
|---|---|
| `skyfig.py` | Load / cut / scale / draw primitives. No knowledge of any particular deck. |
| `make_figures.py` | Reads the spec, resolves panels, writes PNGs. |
| `compare_regions.py` | Region-file-driven zoom comparison — see below. |
| `stamp_beam.py` | Write `BMAJ`/`BMIN`/`BPA` back into a header that lost them. |
| `psf_profile.py` | Azimuthal sidelobe profile of one or more PSFs. |
| `figures.yml` | The figures for `contributions/sgr-a-complex-uhf` (URSI J05). |
| `figures-j09.yml` | The figures for `contributions/pfb-imaging-galactic-centre` (URSI J09). |
| `regions/` | ds9 / CRTF region files naming what to zoom on. |
| `../../figures/scratch/` | Figures generated but not currently on a slide. Regenerable; see its README. |
| `reference/` | The five Africanus III paper scripts this was factored out of. Kept for provenance — not run. |

## A second spec — `figures-j09.yml`

`out_root` is a property of the spec, so a second deck needs a second file:

```bash
$PY scripts/figures/make_figures.py --spec scripts/figures/figures-j09.yml --list
$PY scripts/figures/make_figures.py --spec scripts/figures/figures-j09.yml gc-uhf-sara
```

Three things worth knowing before touching it, because none are obvious:

- **The J09 video is already recorded**, 66 frames with per-slide audio.
  Replacing an *image* is free — no slide, fragment or frame count changes, so
  the frames re-extract and re-mux against the same audio. Adding or removing a
  *slide* renumbers every audio file after it.
- **Full-bleed backgrounds want 16:9, not the slide's 3:2.** A
  `background-image` with `background-size: cover` fills the viewport, and both
  the browser and the extracted frames are 16:9; a 3:2 figure loses its top and
  bottom.
- **`GC_UHF_CLEAN` and `GC_UHF_SARA` are a blink comparison.** Same region, and
  `vmin`/`vmax` written out by hand rather than taken from percentiles, because
  `share_norm` only works within one figure and these are separate files. Change
  one, change the other. The crop is the largest box the image-space mosaic
  covers *completely*: with blank corners the eye reads the change in outline
  instead of the change in image quality.

`copy_to:` on a figure writes the same PNG into a second deck. `beams.png` uses
it — both talks make an argument from that picture, and each deck keeps its own
`images/`.

## Region zooms — `compare_regions.py`

For the super-resolution argument: the UHF intrinsic model resolves structure
that the L-band restored image, at a *higher* frequency and so a finer nominal
resolution, only just shows. One region is an anecdote, so the zoom targets come
from a ds9 `.reg` or CASA `.crtf` file — chosen in a viewer, not typed into a
script — and every region is rendered as a row.

```bash
$PY scripts/figures/compare_regions.py scripts/figures/regions/superres.reg --list

# the deck figure: model vs L-band, five regions
$PY scripts/figures/compare_regions.py scripts/figures/regions/superres.reg \
    --image 'joint_model:label=UHF intrinsic model (SARA):smooth=2.5' \
    --image 'lband:label=L-band restored' \
    -o contributions/sgr-a-complex-uhf/images/superres-zooms.png

# the stronger three-panel version, one PNG per region
$PY scripts/figures/compare_regions.py scripts/figures/regions/superres.crtf --per-region \
    --image 'joint_model:label=UHF intrinsic model:smooth=2.5' \
    --image 'joint:label=UHF restored:beam=8.55x7.76@160' \
    --image 'lband:label=L-band restored' \
    -o contributions/sgr-a-complex-uhf/images
```

Rectangles, circles, ellipses and polygons all reduce to a box; points take
`--default-size`. Per-image options are appended to the key with colons:
`smooth=<arcsec>`, `beam=<b>x<b>@<pa>`, `label=`, plus `stretch`, `pmin`,
`pmax`, `cmap`.

- **`smooth`** convolves before display. A model image is a set of delta
  functions and shows nothing raw; a light Gaussian well below the restoring
  beam is how a model is normally made legible. State the kernel when the figure
  is used.
- **`beam`** stamps a restoring beam on an image whose header lost it, so the
  ellipse gets drawn. The script warns for every image with no beam — on a
  super-resolution figure the claim *is* "structure finer than the beam", and
  without the ellipse there is nothing for a reader to measure against.
- Each panel is scaled independently. A shared scale would be meaningless: the
  model is Jy/pixel and the restored images are Jy/beam.
- RA is labelled on **every** row, because rows are unrelated sky positions
  rather than a shared axis.

Editing a `.reg` by hand, note that the ds9 reader treats a semicolon as a
statement separator even inside a comment and tries to parse what follows.

## Writing a figure

```yaml
figures:
  mosaic-compare:
    out: mosaic-compare.png     # relative to out_root
    region: overlap             # a named region, or an inline {center, width, height}
    figsize: [14, 6.4]
    share_norm: true            # one colour scale across all panels
    panels:
      - image: imspace          # a named image
        title: "Image-space mosaic"
        stretch: log            # linear | log | sqrt | asinh | power
        pmin: 30                # percentile limits, nan-aware
        pmax: 99.8
      - image: joint
        title: "Joint / OTF mosaic"
```

Any panel can be masked by a companion map. Written for `alpha_err`, since a
fitted spectral index comes with a per-pixel uncertainty and cutting on that is
a far better mask than cutting on brightness, which is only a proxy for it:

```yaml
      - image: alpha
        mask_by: {image: alpha_err, below: 0.2}   # or a list of conditions
```

A `plot: density` panel hexbins two maps against each other, with a 1:1 line and
the median offset and 16–84 scatter printed on it. This is the panel that
answers "do these agree": two maps can have *identical* histograms and still
disagree at every pixel, and only a per-pixel plot can tell the difference.
Both sides must be on the same grid — a shape mismatch is an error, not
something to broadcast around.

```yaml
      - plot: density
        range: [-2.5, 0.75]
        xlabel: "in-band α"
        ylabel: "two-band α"
        x: {image: alpha, mask_by: {image: alpha_err, below: 0.2}}
        y: {op: spix, images: [joint, lband], mask_below: 0.0015}
```

A panel draws either a named image, a two-image operation, or the distribution
of one:

```yaml
      - op: spix
        images: [joint, lband]
        mask_below: 0.0015
        plot: histogram         # distribution instead of a map
        bins: 140
        range: [-2.5, 1.0]
        cuts: [0.0015, 0.01, 0.05]   # overlaid, cut on the FIRST image
        highlight: [-1.0, -0.7]      # shaded reference band
        xlabel: "spectral index  α"
```

A `plot: histogram` panel histograms the array the map panel would have drawn —
same region, same mask, same beam correction — rather than recomputing, so the
two cannot describe different populations. `cuts` are thresholds on the first
operand, because a spectral index carries no signal-to-noise of its own: faint
pixels are a ratio of two small numbers, and left unseparated they broaden and
shift the peak. Median (dashed line) and binned peak are printed per series.

To overlay *different* estimates rather than cuts of one, give the panel a
`series:` list. Each entry is a full panel spec, resolved independently, so each
keeps its own valid mask — which is correct, since forcing two estimates onto a
common mask silently discards the disagreement you are looking for:

```yaml
      - plot: histogram
        series:
          - {image: alpha, mask_by: {image: alpha_err, below: 0.2},
             label: "in-band"}
          - {op: spix, images: [joint, lband], mask_below: 0.0015,
             label: "two-band"}
```

A panel drawing a map instead:

```yaml
      - op: difference          # a - b, b reprojected onto a's grid
        images: [imspace, joint]
        symmetric: true
      - op: spix                # log(Sa/Sb) / log(fa/fb)
        images: [joint, lband]
        mask_below: 0.0015
```

Figure-level keys `grid`, `frame`, `beam` and `colorbar` set the default for
every panel; a panel can override any of them. `frame: false` strips ticks,
spines and labels, which is what a full-bleed background slide wants.

Output is transparent PNG with light text, so a figure sits on the slide
background rather than on a white card. Nothing here needs to change for the
`light` theme beyond `theme: light` at the top of the spec.

## Restoring a lost beam — `stamp_beam.py`

```bash
$PY scripts/figures/stamp_beam.py fits_files/GC/L_band_..._sara.fits \
    --bmaj 0.002111010951921344 --bmin 0.001486398930691199 --bpa 5.3e-07 \
    --source "the input images that went into the montage mosaic"
```

Degrees by default so a value pasted out of an input header goes straight in;
`--arcsec` if not. The edit is header-only and in place, refuses to overwrite an
existing beam without `--force`, records provenance as `HISTORY` so a
hand-restored beam is later distinguishable from an imager-written one, and
hashes the data array before and after — a header that outgrows its
2880-byte block moves every byte of a 1 GB file, and that is worth confirming
rather than assuming. `--dry-run` reports without writing.

## PSF sidelobes — `psf_profile.py`

```bash
$PY scripts/figures/psf_profile.py \
    'Single pointing=fits_files/GC/norephase_withbeam_newfout_I_psf_time0_mfs.fits' \
    'Joint / OTF=fits_files/GC/withbeam_newfout_gcx17fix_I_psf_time0_mfs.fits' \
    -o contributions/sgr-a-complex-uhf/images/psf-sidelobes.png
```

A PSF *image* cannot carry a sidelobe comparison: at a stretch that keeps the
core visible the two main lobes look identical, and at a stretch that shows the
far sidelobes the core saturates. The information is in how |PSF| falls with
radius, so this measures RMS and worst-case |PSF| per logarithmic annulus and
integrates the sidelobe power beyond the main lobe into one number.

- Walks the array a block of rows at a time. A 15680² PSF is ~1 GB on disk and
  2 GB as float64; two at once starts swapping. Decimating first would be the
  easy alternative and would be wrong — a block mean lowers every peak, so the
  worst-case curve would come out systematically low.
- Profiles cache to `<stem>.psfprof.npz` beside the FITS (`--refresh` to redo).
  The walk takes a couple of minutes and the plot always needs several goes.
- Asserts the PSF peaks at the centre pixel rather than assuming it. That is
  what makes two PSFs with different phase centres and different image sizes
  comparable, and an off-centre peak would silently turn every radius into a
  different quantity.

## Things that bite

- **`share_norm` is the point of a comparison figure.** Two panels on
  independent percentile scales look similar no matter how far apart the data
  are, and nothing in the rendered figure says so.
- **Blank sky.** Joint mosaics are zero-filled outside the primary-beam cutoff;
  set `blank_zeros: true` on those images or the zeros anchor the percentiles
  and paint a hard frame around the field. Image-space mosaics already use NaN.
- **Projections differ.** The joint mosaic is `RA---SIN` at 2.31"/pix, the
  image-space mosaics are `RA---TAN` at 1.70" and 0.99". Any `difference` or
  `spix` panel reprojects for you; do not subtract the arrays by hand.
- **`wcs.pixel_to_world(0, 0)`** — scalar Python zeros for both arguments —
  returns a wrong position for at least some sliced WCSs in astropy 7.2, while
  `([0], [0])` and every other pixel are correct. `SkyImage.footprint` goes
  through `wcs_pix2world` to avoid it. Worth knowing before writing a corner
  calculation.

## Open questions about the GC data

Recorded here because they limit what the figures can honestly claim, not
because the tooling has a problem with them.

1. **RESOLVED — the L-band beam is back.** Montage does not propagate
   `BMAJ`/`BMIN`/`BPA` through a mosaic, which is how `imspace` and `lband`
   arrived without them. The L-band values were recovered from the images that
   went into the mosaic and written back with `stamp_beam.py`:

   ```
   BMAJ = 0.002111010951921344   # 7.5996"
   BMIN = 0.001486398930691199   # 5.3510"
   BPA  = 5.29693843382383E-07
   ```

   Against the joint mosaic's 8.55" x 7.76" that is a **beam-area ratio of
   1.630**, which by itself biases a UHF→L spectral index by −1.03.
   `imspace` still has no beam; recover it the same way when the number turns
   up.

2. **The two-point spectral index was too steep, and the beam was why.**
   Median α(UHF→L), before and after the beam-area correction:

   | above | raw | corrected |
   |---|---|---|
   | 50 mJy/beam | −1.55 | **−0.53** |
   | 10 mJy/beam | −1.65 | **−0.63** |
   | 2 mJy/beam | −2.05 | **−1.02** |

   The corrected values are ordinary non-thermal indices. `spix` panels now
   apply the correction automatically whenever both images declare a beam, and
   print what they removed.

   The distribution (`uhf-lband-spix-hist`) peaks where it should:

   | UHF brightness | n | median | peak |
   |---|---|---|---|
   | > 1.5 mJy/beam | 137,820 | −0.75 | **−0.79** |
   | > 10 mJy/beam | 53,319 | −0.64 | −0.64 |
   | > 50 mJy/beam | 6,363 | −0.52 | −0.59 |

   Note α is *not* a fit — with two frequencies it is the closed form
   `ln(S₁/S₂) / ln(ν₁/ν₂)` evaluated per pixel. Nothing is being minimised, and
   there is no residual to inspect. A per-sub-band cube would make it a fit and
   would come with one.

   The brightest cut is the flattest, which is the expected direction: the
   bright pixels are Sgr A, the Radio Arc and the thermal sources rather than
   the diffuse non-thermal medium.

3. **The in-band fit and the two-band ratio agree.** `spifit` (spimple) fitted
   544–1087 MHz on the *intrinsic* cube: `alpha`, `alpha_err`, `I0`, `I0_err`,
   on the same 7840² `RA---SIN` grid as `joint`, pixel for pixel, at
   11.74" x 10.77" — coarser than the MFS image because an in-band fit works at
   the resolution of the lowest sub-band. It self-blanks: only 5.5% of the
   field is fitted at all.

   | estimate | n | median | peak |
   |---|---|---|---|
   | in-band, all fitted | 402,630 | −0.98 | −0.91 |
   | in-band, α_err < 0.2 | 238,005 | −0.86 | −0.91 |
   | two-band (UHF→L) | 137,820 | −0.75 | −0.79 |

   Those medians differ by up to 0.23, but that is a population difference, not
   a disagreement — the three cover different pixels. On the 118,085 pixels
   where both are valid, `spix-inband-vs-twoband` gives a **median offset of
   +0.01 with 0.29 scatter**. Two independent estimates, different frequency
   levers, different resolutions, one apparent and one intrinsic, agreeing to a
   hundredth in the median.

   That is also an independent check on the beam-area correction in (2):
   without it the two-band side would sit 1.03 low and this plot would show it.

   Sensitivity to the *frequencies*, for comparison: `ln(797/1284) = −0.476`,
   so a 10% error in either reference frequency moves α by about 20% — a few
   hundredths. The beam was a factor-of-three effect. Frequencies are worth
   getting right but will not rescue or ruin this map on their own.

3. **The joint mosaic is still brighter than the image-space one.** `imspace /
   joint` has median 0.57 above 50 mJy/beam, 0.40 above 10, 0.21 above 2. The
   gradient with brightness is plausibly real — SARA recovering diffuse
   emission MS-CLEAN misses — but the constant part cannot be judged until
   `imspace` has a beam, since a beam-area ratio would produce exactly that.

4. **There are no sub-band cubes**, only MFS images, so the per-sub-band PSF and
   spectral-index comparisons the deck is built around cannot be made from what
   is on disk yet. `uhf-lband-spix` is a two-point stand-in.

5. **`imspace` is MS-CLEAN and `joint` is SARA**, so `mosaic-compare` and
   `mosaic-difference` vary the deconvolution algorithm as well as the
   mosaicking scheme. An image-space SARA mosaic would isolate the variable the
   talk is actually about.
