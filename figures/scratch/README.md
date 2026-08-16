# Parked figures

Figures that were generated for a deck and are not currently placed on a slide.
Kept rather than deleted because the argument they support may come back, and
because they are useful to have open during questions.

Nothing here is precious. Every one is declared in `scripts/figures/figures.yml`
or produced by a documented command, so it regenerates in seconds:

```bash
PY=~/software/pfb-imaging/.venv/bin/python
$PY scripts/figures/make_figures.py --list
$PY scripts/figures/make_figures.py sgra-full
```

Note the spec's `out_root` points at the deck's own `images/` directory, so a
regenerated figure lands there and not here. Move it back if it is still not
being used.

## What is here, and why it left the deck

From `contributions/sgr-a-complex-uhf`, after the deck was restructured around
resolution rather than around a joint-vs-image-space comparison:

| File | Why it is parked |
|---|---|
| `sgra-full.png` | Superseded by `superres-overview`, which shows the same mosaic with the zoom regions drawn on |
| `superres-zooms.png` | Five-region, two-panel version; superseded by the per-region three-panel slides |
| `superres-zooms-3panel.png` | Two-region stacked version; same |
| `lband-context.png` | Real L-band mosaic, never placed on a slide |
| `joint-model.png` | Never placed |
| `mosaic-difference.png` | Image-space minus joint. Not usable as evidence as it stands: the two differ in deconvolution algorithm (MS-CLEAN vs SARA) as well as mosaicking scheme, and the image-space mosaic still has no restoring beam in its header |
| `beam-bias.png` | The α histogram with and without the beam-area correction. Its slide was cut as too obvious for a J05 audience — the result is still real and still quoted on the homogenisation slide |
| `uhf-lband-spix.png` | Superseded by `spix-inband-map`, which shows it beside the in-band fit |
| `uhf-lband-spix-hist.png` | Superseded by `spix-hist-compare`, which overlays the in-band distribution |
| `mosaic-compare.png` | Its slide (`What that buys you`) was cut because J09 makes the same CLEAN-vs-SARA comparison the same day, across three full-bleed slides and 60 s of narration. Carries the same confound as `mosaic-difference` above: algorithm and mosaicking scheme change together, so it cannot attribute the difference to either. Slide source kept in `contributions/sgr-a-complex-uhf/parked-slides.md` |

Deleted rather than parked, at the same time: seven synthetic placeholders from
the original scaffold (`psf-compare`, `spix-compare`, `spix-difference`,
`filament-spix`, `bubble-base`, `uhf-lband-spectrum`, `uv-coverage-compare`).
They were never real data — they stood in for sub-band PSF and spectral-index
comparisons that the available products cannot support.

`filament-spix` has since come back as a real figure — three non-thermal
filament systems on the in-band α map — and lives in the deck's `images/`.
Nothing here is that file.

Slides are parked separately from figures, in
`contributions/sgr-a-complex-uhf/parked-slides.md`: the markdown source of every
cut slide, with the reason and where it sat.
