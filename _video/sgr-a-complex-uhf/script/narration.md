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
whether you can believe a spectral index. I'll start with a disclaimer - I am an algorithm
developer more than an astronomer. What I'm about to present was born out of a curiosity about
how better algorithms, imaging algorithms in particular, can improve the science we derive
from the data we have. 

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

We image the full band jointly with `pfb-imaging`, under a sparsity-promoting prior — SARA — with an additional correlation along the frequency axis imposed. Please come see my J09 talk later today for more about the algorithmic details. 

## slide-13 — restored resolution (10s)

I'll mainly show restored images with resolution homogenised across the band. Hold on to that word "homogenised" — most of this talk is about it.

## slide-14 — the beam varies (12s)

Two facts about the primary beam. It varies strongly across the mosaic, and it changes size by
nearly a factor of two across the band.

## slide-15 — usually nuisances (8s)

Both are normally treated as nuisances that can be corrected for during image post-processing. They are a big part of the story that follows.

## slide-16 — bright and saturating (9s)

This field is one of the toughest there is. It hosts Sgr A-star, Sgr A East, the Radio Arc, among others.

## slide-17 — filaments (8s)

It contains filamentary structure on every scale from arcseconds to degrees.

## slide-18 — diffuse emission (8s)

Genuinely diffuse emission underneath all of it.
Which quietly drops below the noise at the top end of the band.

## slide-19 — dynamic range (9s)

Add dynamic range spanning several orders of magnitude across a single field...

## slide-20 — point-source prior (10s)

And you have a field for which a point-source prior is a very poor description of nearly everything in it.

## slide-21 — question 1, filaments (12s)

I know of at least three open questions. First: do the non-thermal filaments share a common spectral index, or is
that population heterogeneous?

## slide-22 — question 2, bubble base (11s)

Second: Does $\alpha$ steepen from the base of the bubbles outwards, as synchrotron ageing requires? Spoiler alert, the data are not yet conclusive about this.

## slide-23 — question 3, compact sources (14s)

Third: is there a distinct population of compact steep-spectrum sources here? That one matters
because of the gamma-ray excess towards the Galactic Centre, and whether its origin is a
population of millisecond pulsars.

## slide-24 — all spectral index questions (10s)

All three are spectral-index questions. So everything that follows is about whether we can
measure a spectral index here that we are willing to believe. (Another spoiler alert).

## slide-25 — Section: mosaicking is a modelling choice (5s)

Let's start with how the mosaic gets made.

## slide-26 — two ways (18s)

There are two ways to build a mosaic.
The usual way is to deconvolve each pointing independently, primary-beam
correct, and use a weighted average to stitch the images together. Or you can do it jointly, in visibilty space, by incorporating the beam into the
measurement operator. That way it's one deconvolution over all the data simultaneously.

## slide-27 — different problems (9s)

That is not a workflow preference. The two are solving genuinely different problems. The latter is harder in many ways, but I'm going to try and convince you that it is worth it.

## slide-28 — rephasing (14s)

There is a detail worth pointing out here. To jointly deconvolve all pointings, we need to rephase to a common phase centre. The primary beam does not come along.

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

At the field centre that is roughly three times the imaging weight, out of the same observation.

## slide-37 — PSF sidelobes (22s)

Here is what it does to the point spread function. Single pointing in green, joint in blue; RMS
sidelobe level as a function of radius drawn with the solid lines. The main lobes only differ by about four per cent, the sidelobes by a lot more than that. Sidelobe RMS reduces by up to a factor of four at
arcminute scales, dropping to just below two out to three degrees. This makes the problem much better conditioned.

## slide-38 — mosaic comparison (16s)

What does that do for imaging? Here's the same data images in two different ways. It's the same sky and colour scale. On the left, each pointing deconvolved
independently with multi-scale CLEAN and then stitched in image space. On the right, one SARA deconvolution over all three. I hope we can agree that the latter is the more faithful of the two.

## slide-39 — CLEAN can't forward model (18s)

One honest note on that comparison: both the deconvolution algorithm and the
mosaicking scheme is different in this comparison. That is not entirely accidental. CLEAN does not minimise a stated objective function, and that makes it harder to incorporate the beam model.

## slide-40 — Section: resolution is the hidden variable (6s)

Now the part that actually decides the science.

## slide-41 — alpha is a ratio (14s)

A spectral index is a ratio across the band. Which means the images going into it have to report the same thing — and by default they are not.

## slide-42 — common beam (10s)

Sensitivity and uv-coverage both change with frequency, so every sub-band has its own
resolution. You have to homogenize the resolution across frequency before comparing bands and physics forces us to degrade the resolution to that of the lowest sub-band.

## slide-43 — CLEAN's easy case (10s)

For a CLEAN model that is just a convolution, because the model is a set of delta functions.

## slide-44 — sparsity is harder (13s)

For a sparsity prior it is not, because that model has its own intrinsic resolution — which has
to be estimated before resolution can be homogenized.

## slide-45 — the cost of getting it wrong (19s)

Get this wrong and the derived spectral index is not reliable. 

## slide-46 — CLEAN assumes zero (12s)

Let me be precise about the model resolution, because this is the methodological point. A CLEAN
model consisting of delta functions has zero intrinsic resolution by assumption. A sparsity prior's model does
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
