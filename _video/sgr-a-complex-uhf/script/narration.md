# Narration — High-Fidelity MeerKAT UHF Observations of the Sgr A Complex

URSI GASS 2026, Session J05. Target **13:30** against a hard 15:00 limit. The live slot is 25
minutes, so the video can sit close to the limit without crowding the questions.

One block per frame, in order. Record each as `audio/raw/slide-NN.wav` matching the frame
number. `(NNs)` is the budget, not a stopwatch — read at a natural pace and let the totals
sort themselves out; the build reports the real duration.

Pace assumed is ~140 wpm. Where a line reads awkwardly out loud, rewrite it — prose that looks
fine on the page often does not survive being spoken.

Nothing here goes near Ian's unpublished compact-source result. Frame 23 motivates the
compact-source question from the public GeV-excess literature only.

**Renumbered for the 76-frame deck.** Frames 1–25 are unchanged from the draft you edited.
After that the two slides that duplicated J09 are gone (`Every pointing that sees a pixel`,
`What that buys you`), the MAP section lost `What we could publish instead`, and a new
`Back to question 1` slide arrived. `_video/` still holds the old 82 frames — re-run
`extract_slides.py` before recording, or every block after 25 lands on the wrong picture.

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

## slide-28 — CLEAN can't forward model (16s)


And there is a reason we don't always do it this way. CLEAN does not minimise a stated
objective function, so a beam model is hard to put inside it. Forward modelling wants an
optimisation problem — which is what J09 is about.

## slide-29 — rephasing (14s)


There is a detail worth pointing out here. To jointly deconvolve all pointings, we need to rephase to a common phase centre. The primary beam does not come along.

## slide-30 — beam follows the dish (9s)


The beam is attached to where the dish is pointing, not to the phase centre.

## slide-31 — offset and distorted (13s)


So in the common frame, each pointing's beam sits at a different offset — and the projection
about the new centre distorts it, differently for each one.

## slide-32 — reprojected (9s)


Which means the beam has to be reprojected per pointing, not merely translated. This picture
turns up again in J09 this afternoon, doing a rather different job.

## slide-33 — PSF sidelobes (22s)


So what does that buy? Here is what it does to the point spread
function. Single pointing in green, joint in blue; RMS
sidelobe level as a function of radius drawn with the solid lines. The main lobes only differ by about four per cent, the sidelobes by a lot more than that. Sidelobe RMS reduces by up to a factor of four at
arcminute scales, dropping to just below two out to three degrees. This makes the problem much better conditioned.

## slide-34 — every pointing contributes (18s)


That's because every pointing that sees a pixel contributes to it, and since we interleaved them
in time, that union spans parallactic angle too. Roughly three times the imaging weight at the
field centre.

## slide-35 — Section: resolution is the hidden variable (6s)


Now the part that actually decides the science.

## slide-36 — alpha is a ratio (14s)


A spectral index is a ratio across the band. Which means the images going into it have to report the same thing — and by default they are not.

## slide-37 — common beam (10s)


Sensitivity and uv-coverage both change with frequency, so every sub-band has its own
resolution. You have to homogenize the resolution across frequency before comparing bands and physics forces us to degrade the resolution to that of the lowest sub-band.

## slide-38 — CLEAN's easy case (10s)


For a CLEAN model that is just a convolution, because the model is a set of delta functions.

## slide-39 — sparsity is harder (13s)


For a sparsity prior it is not, because that model has its own intrinsic resolution — which has
to be estimated before resolution can be homogenized.

## slide-40 — the cost of getting it wrong (19s)


Get this wrong and the derived spectral index is not reliable.

## slide-41 — CLEAN assumes zero (12s)


Let me be precise about the model resolution, because this is the methodological point. A CLEAN
model consisting of delta functions has zero intrinsic resolution by assumption. A sparsity prior's model does
not.

## slide-42 — non-zero (10s)


Its intrinsic resolution is non-zero, and it is set by the data and the prior together.

## slide-43 — varies across the band (10s)


It is also not constant across the band, because sensitivity and uv-coverage change.

## slide-44 — baked into alpha (10s)


Restore with a single beam and that variation is baked into every spectral index you derive.

## slide-45 — estimate then homogenise (10s)


So the restore step has to estimate the model resolution before it can homogenise anything.

## slide-46 — and it can't be exact (13s)


And it cannot do that exactly, because the model's intrinsic resolution is SNR-dependent — it
varies across the image as well as across the band. Homogenisation is an approximation. Hold
that thought.

## slide-47 — where we are looking (9s)


Is any of this visible? Here is the full mosaic, with the Radio Arc marked.

## slide-48 — the Radio Arc (21s)


The Radio Arc. Intrinsic model on the left, our UHF restored image in the middle at eight
and a half arcseconds, L band on the right at seven point six. The model separates
individual filament strands that blend together at the UHF restoring beam — and the L-band
image, which knows nothing about our model, shows the same strands.

## slide-49 — Section: does the science hold up (6s)


So does any of this survive contact with the science?

## slide-50 — two estimates (18s)


Here are two independent estimates of the same quantity. An in-band fit across 544 to 1087
megahertz, against a two-band ratio from 797 megahertz to 1.28 gigahertz. Both primary-beam
corrected, both carrying the same mask.

## slide-51 — they agree (13s)


Pixel by pixel they agree to a median offset of minus zero point zero three, with a scatter of
zero point three five, over a hundred and fifty-eight thousand pixels.

## slide-52 — what that means (13s)


Nothing forces that to happen. That they agree tells us the resolution handling is not
introducing a systematic at any level we can detect.

## slide-53 — the distribution (14s)


The distributions land in the same place too — both peak around minus zero point nine. Ordinary
non-thermal emission, reached two independent ways.

## slide-54 — the maps (16s)


And the maps themselves. In-band left, two-band right — same colour scale and same mask, so a
difference in colour is a real disagreement. Thermal sources near zero, filaments and diffuse
medium steeper.

## slide-55 — back to question 1 (14s)

So, back to the first question. Three non-thermal filament systems — the Radio Arc, the Snake
and the Cane — measured on the filaments themselves, because a box around one is mostly
background.

## slide-56 — looks like three populations (11s)

Taken as they come their medians run from minus zero point two five to minus one point one,
which certainly looks like three different populations.

## slide-57 — matched in brightness (16s)

But alpha flattens with brightness inside every one of them, by about as much as they differ
from each other. Match them in brightness and the Arc and the Snake agree to within zero point
zero six.

## slide-58 — only the Cane (9s)

Only the Cane stays steeper — by about zero point three, in every bin where we can make the
comparison.

## slide-59 — alpha against its error (15s)


And this is the caution behind all of it — the in-band spectral index against its own fitted
uncertainty. Binned by that uncertainty, the median alpha runs from minus zero point five five
where it is well constrained to minus one point three where it is not.

## slide-60 — a 0.75 swing (10s)


That is a swing of three quarters, driven entirely by how well each pixel was constrained.

## slide-61 — no error map, no interpretation (12s)


Which means any weakly constrained subsample will look like a steep-spectrum population. A
spectral index map without its error map is not interpretable.

## slide-62 — Section: what is the resolution of a MAP image (7s)


Which brings me to the thing I actually want to leave you with.

## slide-63 — K (18s)


For a quadratic regulariser the MAP estimate is just a linear filter applied to the truth. Let's
call it K. The H inside is the likelihood Hessian — the operator J09 spends its whole talk
making cheap.

## slide-64 — rows of K (12s)


Row j of K is the effective point spread function at pixel j — the average of the sky that
pixel actually reports.

## slide-65 — SNR- and brightness-dependent (18s)


The inverse noise covariance sits inside K, so resolution is a function of local
signal-to-noise, not an instrumental constant. For an L1 or learned prior it depends on source
brightness too.

## slide-66 — assert, not measure (10s)


So the restoring beam asserts a resolution. It does not measure one.

## slide-67 — four other fields (16s)


This is not a new problem, and it is not our problem. Geophysics has called it an averaging
kernel since 1968. Seismic tomography, the model resolution matrix. Atmospheric sounding,
emission tomography — all of them report it.

## slide-68 — why we got away with it (19s)


Radio interferometry is the outlier. We hid it behind the restoring beam — not because CLEAN is
linear, it is not, but because a delta-function model lets us assert zero intrinsic resolution
and then never check. That assertion is already doubtful for multi-scale CLEAN.

## slide-69 — affordable today (14s)


And probing it is affordable — K applied to a probe is one extra solve. Well within reach
today, and we are simply not doing it.

## slide-70 — Section: in summary (5s)


To summarise.

## slide-71 — the band (10s)


The Galactic Centre at UHF carries the steep-spectrum and absorption diagnostics, and it has
been under-observed.

## slide-72 — mosaicking (13s)


Joint mosaicking is a modelling choice. The beam is direction-dependent as well as
time-dependent, and after rephasing it has to be reprojected, not merely shifted.

## slide-73 — the PSF (9s)


Measured on the point spread function, that is sidelobes down fourfold at arcminute scales.

## slide-74 — resolution propagates (18s)


Resolution is the variable that propagates into spectral index — a beam-area ratio of one point
six three is a shift of one point oh three. Control for it and two of our three filaments
agree.

## slide-75 — the closing claim (12s)


And the restoring beam is an assertion, not a measurement. Other fields have been reporting
theirs for fifty years.

## slide-76 — come to J09 (11s)


And please do come to J09 after lunch. That is the other half of this — and what it would
actually take to report K instead of a beam.

## slide-77 — Thanks (14s)


Thank you. The imaging was done with `pfb-imaging`, which is on GitHub under ratt-ru. Happy to
take questions.
