# Narration — High-Fidelity MeerKAT UHF Observations of the Sgr A Complex

URSI GASS 2026, Session J05. Target **13:30** against a hard 15:00 limit.

One block per frame, in order. Record each as `audio/raw/slide-NN.wav` matching the frame
number. `(NNs)` is the budget, not a stopwatch — read at a natural pace and let the totals
sort themselves out; the build reports the real duration.

Pace assumed is ~140 wpm. Where a line reads awkwardly out loud, rewrite it — prose that looks
fine on the page often does not survive being spoken.

**This is a first draft for you to edit.** Two things to know before you start:

- 83 frames is a lot for 15 minutes. This draft comes in close to the limit, so the blocks are
  tighter than the pfb-imaging ones. If a block feels rushed, that slide is a cut candidate.
- Nothing here goes near Ian's unpublished compact-source result. Frame 23 motivates the
  compact-source question from the public GeV-excess literature only.

---

## slide-01 — Title (18s)

Hello. I'm Landman Bester, from SARAO and Rhodes University. This talk is about high-fidelity
imaging of the Galactic Centre at UHF band — and about the one number that quietly decides
whether you can believe a spectral index.

## slide-02 — Cold open, image only (6s)

Let me start with the picture.

## slide-03 — 544–1087 MHz (11s)

This is the Sgr A complex at UHF band — 544 to 1087 megahertz, about five square degrees, from
three MeerKAT pointings imaged jointly.

## slide-04 — least-explored view (10s)

It is also the least-explored view of this field. Almost everything published here is at L band
or above.

## slide-05 — Section: the band, and the field (5s)

So: why this band, and why this field.

## slide-06 — steep-spectrum sensitivity (9s)

UHF buys four things. Sensitivity to steep-spectrum emission — the emission that has faded out
of reach by the time you get to 1.28 gigahertz.

## slide-07 — diffuse plasma (9s)

Diffuse plasma that higher frequencies either resolve out or never detect at all.

## slide-08 — free-free absorption (12s)

Free-free absorption becomes a usable diagnostic rather than a nuisance, because thermal gas
turns optically thick against the Galactic Centre in this band.

## slide-09 — lever arm (11s)

And an octave of frequency lever arm, 544 to 1087 — roughly double that if you tie it to
existing L-band data.

## slide-10 — simultaneously measurable (8s)

This band is the one place where several of those effects are measurable at the same time.

## slide-11 — three 8-hour pointings (10s)

The observation is three eight-hour pointings, interleaved in time, covering about five square
degrees.

## slide-12 — imaged jointly (10s)

The full band, imaged jointly with `pfb-imaging` under a sparsity-promoting prior — SARA.

## slide-13 — restored resolution (10s)

Restored to eight and a half by seven point eight arcseconds, homogenised across the band. Hold
on to that word "homogenised" — most of this talk is about it.

## slide-14 — the beam varies (12s)

Two facts about the primary beam. It varies strongly across the mosaic, and it changes size by
nearly a factor of two across the band.

## slide-15 — usually nuisances (8s)

Both are normally treated as calibration nuisances. They are the whole story for what follows.

## slide-16 — bright and saturating (9s)

As for the field: Sgr A-star, Sgr A East, the Radio Arc — bright, compact, and saturating.

## slide-17 — filaments (8s)

Filamentary structure on every scale from arcseconds to degrees.

## slide-18 — diffuse emission (8s)

Genuinely diffuse emission underneath all of it.

## slide-19 — dynamic range (9s)

And dynamic range spanning several orders of magnitude across a single field.

## slide-20 — point-source prior (10s)

Which is to say a point-source prior is a poor description of very nearly everything in this
image.

## slide-21 — question 1, filaments (12s)

Three open questions. First: do the non-thermal filaments share a common spectral index, or is
that population heterogeneous?

## slide-22 — question 2, bubble base (11s)

Second: what is the spectrum at the base of the bubbles, where the energetics are actually set?

## slide-23 — question 3, compact sources (14s)

Third: is there a distinct population of compact steep-spectrum sources here? That one matters
because of the gamma-ray excess towards the Galactic Centre, and whether its origin is a
population of millisecond pulsars.

## slide-24 — all spectral index questions (10s)

All three are spectral-index questions. So everything that follows is about whether we can
measure a spectral index here that we are willing to believe.

## slide-25 — Section: mosaicking is a modelling choice (5s)

Start with how the mosaic gets made.

## slide-26 — two ways (18s)

There are two ways. In image space you deconvolve each pointing independently, primary-beam
correct, and take a weighted average. Jointly — or on the fly — the beam sits inside the
measurement operator, and you do one deconvolution over all the data.

## slide-27 — different problems (9s)

That is not a workflow preference. The two are solving genuinely different problems.

## slide-28 — rephasing (14s)

And there is a detail here that is easy to miss. To deconvolve every pointing together, the data
first have to be rephased to a common phase centre. The primary beam does not come along.

## slide-29 — beam follows the dish (9s)

The beam is attached to where the dish is pointing, not to the phase centre.

## slide-30 — offset and distorted (13s)

So in the common frame, each pointing's beam sits at a different offset — and the projection
about the new centre distorts it, differently for each one.

## slide-31 — reprojected (9s)

Which means the beam has to be reprojected per pointing, not merely translated.

## slide-32 — one pointing's coverage (10s)

Now, what does joint deconvolution actually buy. Image-space mosaicking gives you one pointing's
uv-coverage per sky position.

## slide-33 — the union (12s)

Joint gives you the coherent union of every pointing that sees that position, weighted by the
primary beam.

## slide-34 — parallactic angle (11s)

And because the pointings are interleaved in time, that union spans parallactic angle as well as
position.

## slide-35 — more samples per position (8s)

More samples per sky position — not merely more sky.

## slide-36 — four times the weight (10s)

At the field centre that is about four times the imaging weight, out of the same observation.

## slide-37 — PSF sidelobes (22s)

Here is what it does to the point spread function. Single pointing in green, joint in blue; RMS
sidelobe level solid, worst case dotted. The main lobes differ by four per cent, so on an image
they look identical. The sidelobes do not. Sidelobe RMS is down by a factor of four at
arcminute scales, and about one point seven out to three degrees.

## slide-38 — mosaic comparison (16s)

And in the image. Same sky, same colour scale. On the left, each pointing deconvolved
independently with multi-scale CLEAN and then averaged — you can still see the individual
pointing footprints in the product. On the right, one SARA deconvolution over all three.

## slide-39 — CLEAN can't forward model (18s)

One honest note on that comparison: it changes the deconvolution algorithm as well as the
mosaicking scheme. That is not entirely accidental. CLEAN does not minimise a stated objective,
so there is no natural place to put a beam model inside it.

## slide-40 — Section: resolution is the hidden variable (6s)

Now the part that actually decides the science.

## slide-41 — alpha is a ratio (14s)

A spectral index is a ratio across the band. Which means the two images going into it have to be
reporting the same thing — and by default they are not.

## slide-42 — common beam (10s)

Sensitivity and uv-coverage both change with frequency, so every sub-band has its own
resolution. You have to restore them all to a common beam.

## slide-43 — CLEAN's easy case (10s)

For a CLEAN model that is just a convolution, because the model is a set of delta functions.

## slide-44 — sparsity is harder (13s)

For a sparsity prior it is not, because that model has its own intrinsic resolution — which has
to be estimated first, and then corrected for.

## slide-45 — the cost of getting it wrong (19s)

And get this wrong by a constant factor and every spectral index shifts. For our two bands, a
beam-area ratio of one point six three moves alpha by one point zero three. That is the
difference between an impossible number and an ordinary one.

## slide-46 — CLEAN assumes zero (12s)

Let me be precise about the model resolution, because this is the methodological point. A CLEAN
model is delta functions: intrinsic resolution zero, by assumption. A sparsity prior's model is
not.

## slide-47 — non-zero (10s)

Its intrinsic resolution is non-zero, and it is set by the data and the prior together.

## slide-48 — varies across the band (10s)

It is also not constant across the band, because sensitivity and uv-coverage change.

## slide-49 — baked into alpha (10s)

Restore with a single beam and that variation is baked into every spectral index you derive.

## slide-50 — estimate then homogenise (10s)

So the restore step has to estimate the model resolution before it can homogenise anything.

## slide-51 — and it can't be exact (13s)

And it cannot do that exactly, because the model's intrinsic resolution is SNR-dependent — it
varies across the image as well as across the band. Homogenisation is an approximation. Hold
that thought.

## slide-52 — where we are looking (12s)

Is any of this visible? Here is the full mosaic with two regions marked — Sgr B2 and Sgr C.

## slide-53 — Sgr B2 (16s)

Sgr B2. Intrinsic model on the left, our UHF restored image in the middle at eight and a half
arcseconds, L band on the right at seven point six. The model separates clumps that both
restored images blend together.

## slide-54 — Sgr C (16s)

Sgr C, the same three. The filament crossing the shell stays thin in the model and widens in
both restored images — including the L-band one, which has the finer nominal resolution.

## slide-55 — Section: does the science hold up (6s)

So does any of this survive contact with the science?

## slide-56 — two estimates (16s)

Here are two independent estimates of the same quantity. An in-band fit across 544 to 1087
megahertz on the intrinsic cube, against a two-band ratio from 797 megahertz to 1.28 gigahertz
on the apparent restored images. Different lever arms, different resolutions.

## slide-57 — they agree (11s)

Pixel by pixel, they agree to a median offset of plus zero point zero one, with 0.29 scatter,
over a hundred and eighteen thousand pixels.

## slide-58 — what that means (13s)

Nothing forces that. That they do agree says the resolution handling — homogenisation across the
band, and the beam correction between bands — is not introducing a systematic at any level we
can detect.

## slide-59 — the distribution (15s)

The distributions land in the same place too: a peak around minus zero point nine. Ordinary
non-thermal emission, reached by two independent routes.

## slide-60 — the maps (14s)

And these are the maps themselves. In-band fit on the left, two-band ratio on the right, same
colour scale. Thermal sources near zero, the filaments and the diffuse medium steeper.

## slide-61 — alpha against its error (15s)

Now the caution. This is the in-band spectral index plotted against its own fitted uncertainty.
Binned by that uncertainty, the median alpha runs from minus zero point five five at the
well-constrained end to minus one point three at the poorly constrained end.

## slide-62 — a 0.75 swing (10s)

That is a swing of three quarters, driven entirely by how well each pixel was constrained.

## slide-63 — no error map, no interpretation (12s)

Which means any weakly constrained subsample will look like a steep-spectrum population. A
spectral index map without its error map is not interpretable.

## slide-64 — Section: what is the resolution of a MAP image (7s)

Which brings me to the thing I actually want to leave you with.

## slide-65 — R (16s)

For a quadratic regulariser, the maximum a posteriori estimate is a linear filter applied to the
truth. Call that filter R.

## slide-66 — rows of R (12s)

Row j of R is the effective point spread function at pixel j — the average of the sky that
pixel actually reports.

## slide-67 — SNR-dependent (12s)

The inverse noise covariance sits inside R, which makes resolution a function of local
signal-to-noise rather than an instrumental constant.

## slide-68 — brightness-dependent (12s)

And for an L1, total-variation or learned prior, R depends on source brightness as well. The
resolution field changes with the object you are imaging.

## slide-69 — assert, not measure (10s)

So the restoring beam asserts a resolution. It does not measure one.

## slide-70 — four other fields (16s)

This is not a new problem, and it is not our problem. Geophysics has called it an averaging
kernel since 1968. Seismic tomography, the model resolution matrix. Atmospheric sounding,
emission tomography — all of them report it.

## slide-71 — why we got away with it (19s)

Radio interferometry is the outlier. We hid it behind the restoring beam — not because CLEAN is
linear, it is not, but because a delta-function model lets us assert zero intrinsic resolution
and then never check. That assertion is already doubtful for multi-scale CLEAN.

## slide-72 — publish a resolution field (15s)

So what could we publish instead. A resolution field rather than a beam. Probing R is one
Jacobian-vector product through the solver's fixed point; the diagonal is about ten Hutchinson
probes.

## slide-73 — fix it by construction (13s)

Or where the science product is a per-pixel fit, fix the resolution by construction — forfeit
super-resolution and gain a defined estimand.

## slide-74 — move the model forward (14s)

Or better, move the science model into the forward problem, and fit spectra against the
visibilities, so the regulariser and the physical model are the same object.

## slide-75 — affordable today (10s)

The cost is one extra solve per probe. That is affordable today, and we are not doing it.

## slide-76 — Section: in summary (5s)

To summarise.

## slide-77 — the band (10s)

The Galactic Centre at UHF carries the steep-spectrum and absorption diagnostics, and it has
been under-observed.

## slide-78 — mosaicking (13s)

Joint mosaicking is a modelling choice. The beam is direction-dependent as well as
time-dependent, and after rephasing it has to be reprojected, not merely shifted.

## slide-79 — the PSF (9s)

Measured on the point spread function, that is sidelobes down fourfold at arcminute scales.

## slide-80 — resolution propagates (12s)

Resolution is the variable that propagates into spectral index. A beam-area ratio of one point
six three is a shift of one point zero three.

## slide-81 — it works (10s)

Handle it explicitly and two independent estimates agree to a hundredth.

## slide-82 — the closing claim (12s)

And the restoring beam is an assertion, not a measurement. Other fields have been reporting
theirs for fifty years.

## slide-83 — Thanks (14s)

Thank you. The imaging was done with `pfb-imaging`, which is on GitHub under ratt-ru, and which
is the subject of a separate talk in J09. Happy to take questions.
