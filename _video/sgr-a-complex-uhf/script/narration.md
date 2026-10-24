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

**Renumbered for the 61-frame deck.** Frames 1–25 are unchanged from the draft you edited.
After that the two slides that duplicated J09 are gone (`Every pointing that sees a pixel`,
`What that buys you`), the MAP section lost `What we could publish instead`, and a new
`Back to question 1` slide arrived, and the two resolution slides merged into one. Frames are
re-extracted and every block maps to the frame of the same number.

---

## slide-01 — Title (18s)



Hello. I'm Landman Bester, from SARAO and Rhodes University. 
This talk is about high-fidelity imaging of the Galactic Centre at UHF band — and about what the spectral index maps can tell us.
I'll start with a disclaimer - I am an algorithm developer more than an astronomer.
What I'm about to present was born out of a curiosity about how better algorithms, imaging algorithms in particular, can improve the science we derive from the data we have.
All the results I'm about to present are preliminary, this is an ongoing project.

## slide-02 — Cold open, image only (6s)

Let me start with the picture.

## slide-03 — 544–1087 MHz (11s)

This is the Sgr A complex at UHF band — obtained by jointly imaging three 8 hour MeerKAT pointings.

## slide-04 — least-explored view (10s)

It is probably the least-explored view of this field.

## slide-05 — Section: the band, and the field (5s)

So: why this band, and why this field.

## slide-06 — steep-spectrum sensitivity (9s)

UHF buys four things.
Sensitivity to steep-spectrum emission that has faded out of reach of higher frequencies.

## slide-07 — diffuse plasma (9s)

Diffuse plasma that higher frequencies either resolve out or never detect at all.

## slide-08 — free-free absorption (12s)

Free-free absorption becomes a usable diagnostic in this band, rather than a nuisance.

## slide-09 — lever arm (11s)

And an octave of frequency lever arm, from about 500 to 1000 MHz — roughly double that if you tie it to existing L-band data.

## slide-10 — simultaneously measurable (8s)

This band is the one place where several of those effects are measurable at the same time.

## slide-11 — three 8-hour pointings (10s)

The observation consists of three eight-hour pointings, interleaved in time, covering about five square degrees.

## slide-12 — imaged jointly (10s)

We image the full band jointly with `pfb-imaging`, under a sparsity-promoting prior known as Sparsity Averaging and Reweighting Analysis, or SARA, with an additional correlation along the frequency axis imposed.
Please come see my J09 talk later today for more about the algorithmic details.

## slide-13 — restored resolution (10s)

I'll mainly show restored images with resolution homogenised across the band.

## slide-14 — the beam varies (12s)

The primary varies strongly across the mosaic, and it changes size by nearly a factor of two across the band.

## slide-15 — usually nuisances (8s)

Jointly imaging the three fields allows us to correct for the primary beam in a more systematic way. 
It's a big part of the story that follows.
I won't delve into the technical details here, please come see my J09 talk later today if you are interested.

## slide-16 — bright and saturating (9s)

This field is one of the toughest there is.
It hosts Sgr A-star, Sgr A East, the Radio Arc, among others.

## slide-17 — filaments (8s)

It contains filamentary structure on every scale from arcseconds to degrees.

## slide-18 — diffuse emission (8s)

With genuinely diffuse emission underneath all of it.
Which quietly drops below the noise at the top end of the band.

## slide-19 — dynamic range (9s)

Add dynamic range spanning several orders of magnitude across a single field...

## slide-20 — point-source prior (10s)

And you have a field for which a point-source prior is a very poor description of nearly everything in it.

## slide-21 — question 1, filaments (12s)

I know of at least three open questions about this field.
First: do the non-thermal filaments share a common spectral index, or is that population heterogeneous?

## slide-22 — question 2, bubble base (11s)

Second: Does the spectral index steepen from the base of the bubbles outwards, as synchrotron ageing requires?

## slide-23 — question 3, compact sources (14s)

Third: is there a distinct population of compact steep-spectrum sources here?
Answers to these questions will genuinely broaden our understanding of what is going on in our own galaxy.

## slide-24 — all spectral index questions (10s)

All three are spectral-index questions.
So everything that follows is about whether we can measure a spectral index that we are willing to believe.

## slide-25 — Section: mosaicking is a modelling choice (5s)

Let's start with how the mosaic gets made.

## slide-26 — two ways (18s)

There are two ways to build a mosaic.
The usual way is to deconvolve each pointing independently, primary-beam correct, and use a weighted average to stitch the images together.
Alternatively, you can do it jointly, in visibility space, by incorporating the primary beam into the measurement operator.
That way it's one deconvolution over all the data simultaneously.

## slide-27 — different problems (9s)

That is not a workflow preference.
The two are solving genuinely different problems.
The latter is harder in many ways, but I'm going to try and convince you that it's worth it.

## slide-28 — CLEAN can't forward model (16s)

Worth stating upfront, since it does not minimize a formal objective function, the beam model is awkward to incorporate into CLEAN.
Forward modelling wants an optimisation problem and that's what makes the latter approach feasible.
This is what my J09 talk is about.

## slide-29 — rephasing (14s)

The detail worth pointing out here is that, to jointly deconvolve all pointings, we need to rephase to a common phase centre.
The primary beam does not come along.

## slide-30 — beam follows the dish (9s)

The beam is attached to where the dish is pointing, not to the phase centre.

## slide-31 — offset and distorted (13s)

So in the common frame, each pointing's beam sits at a different offset — and the projection about the new centre distorts it, differently for each one.

## slide-32 — reprojected (9s)

Which means the beam has to be reprojected per pointing, it's not merely translated.

## slide-33 — PSF sidelobes (22s)

So what does joint imaging buy?
Well, here is what it does to the point spread function.
Single pointing is shown in green, joint in blue.
The RMS sidelobe level as a function of radius from the center is drawn with the solid lines.
The main lobes only differ by about four per cent, the sidelobes by a lot more than that.
Sidelobe RMS reduces by up to a factor of four at arcminute scales, dropping to just below two out to three degrees.
This makes the problem much better conditioned.

## slide-34 — every pointing contributes (18s)

That's because every pointing that sees a pixel contributes to it, and since we interleaved them in time, that union spans parallactic angle too.
It results in roughly three times the imaging weight at the field centre.

## slide-35 — Section: Science is predicated on knowing the resolution (6s)

Now the part that's actually relevant for the science viz. resolution.


## slide-36 — alpha is a ratio (19s)

A spectral index is a ratio across the band.
So every sub-band contributing to its estimation has to report the same thing — and by default they do not.
Sensitivity and uv-coverage both change with frequency, so each sub-band has its own resolution.

## slide-37 — common beam (11s)

So we homogenize the resolution across frequency before comparing anything, and physics forces us to degrade to the resolution of the lowest sub-band.

## slide-38 — CLEAN's easy case (9s)

For a CLEAN model that is just a convolution: a set of delta functions has zero intrinsic resolution by assumption.

## slide-39 — sparsity is harder (19s)

A sparsity prior's model does not.
Its intrinsic resolution is non-zero, it is set by the data and the prior together.
So the restore step technically has to estimate it before it can homogenise anything.

## slide-40 — an approximation (14s)

Get this wrong and the derived spectral index is not reliable.
And we cannot do it exactly, because resolution is also SNR-dependent.
So, homogenisation is an approximation.

## slide-41 — where we are looking (9s)

Is any of this visible?
Here is the full mosaic with the radio arc highlighted.
Noise is amplified as the sensitivity pattern drops off so we discard the extreme edges of the field. 

## slide-42 — the Radio Arc (21s)

Zooming into the highlighted box containing the radio arc, we see this. 
The intrinsic model is shown on the left, our UHF restored image in the middle and L band on the right. 
The model separates individual filament strands that blend together at the UHF restoring beam.
But these strands are also visible in the L-band restored image, which suggests that they are real.

## slide-43 — Section: does the science hold up (6s)

Does this enable better science?
I would say yes but we could do a lot better.
Let me try to explain why.

## slide-44 — two estimates (18s)

Here we compare two independent estimates of the spectral index populations.
One comes from an in-band fit to the UHF mosaic, imaged in 8 sub-bands.
The other from a two-band ratio between the UHF and L band mosaics, imaged separately.
Both primary-beam corrected and carrying the same mask.
Perfect agreement between the two maps would put every dot on this image on the diagonal line.

## slide-45 — they agree (13s)

We find that there is good agreement between the two estimates, especially in high SNR regions.
However, the agreement is not perfect. 

## slide-46 — what that means (13s)

Nothing forces that to happen.
But the level of agreement, as indicated by the high density of points that fall near the diagonal, is reassuring since the two approaches have different systematics.

## slide-47 — the distribution (14s)

The distributions land in the same place too — both peak around where one would expect for non-thermal emission, reached two independent ways.
We also observe that lowering the SNR threshold to fit mode components systematically shifts the mode of the distribution downwards.
Since that includes some of the bubbles into the fit, it suggests that they do have steeper spectra.
But this conclusion is tentative at best, it's not that visible by looking at the actual maps.

## slide-48 — the maps (16s)

Here they are.
In-band left, two-band right — same colour scale, so a difference in colour is a real disagreement.
Both made with an SNR cut of 5-sigma across all bands.
The fact that more components survive the SNR cut in the in-band image could be a result of better imaging, but we have to keep in mind that SNR drops towards the top of the band, so a hard cut across all frequencies can also explain the difference in the masks.

## slide-49 — What you ca't see in either map (11s)

And this is the caution behind all of it — the in-band spectral index against its own fitted uncertainty.
Binned by that uncertainty, the median alpha runs from -0.5 where it is well constrained to -1.3 where it is not.

## slide-50 — sweep in alpha (11s)

This shows that steep spectrum sources are generally not as well described by a spectral index model.

## slide-51 — weakly constrained steep spectrum sources (16s)
And that a weakly constrained sub-sample can masquerade as a steep-spectrum population.
We should therefore be careful about drawing conclusions about the nature of the radio bubbles from spectral index maps alone.
A more sophisticated analysis is required here.


## slide-52 — back to opening questions (14s)

So then, back to my opening questions.

## slide-53 — Q1 filaments (14s)

The only one with a convincing answer is the first.
Isolating three non-thermal filament systems — known as the Radio Arc, the Snake and the Cane — shown in the top panel, they certainly look rather inhomogeneous.

## slide-54 — Matched surface brightness (14s)
But alpha flattens with brightness inside every one of them, by about as much as they differ from each other.
When matched in surface brightness, the Arc and the Snake agree quite well.
But the cane consistently appears steeper.
I must admit that I am not really sure if this tells us anything useful.


## slide-55 — Inconclusive (7s)
The second question, whether spectral index steepens towards the edge of the bubbles, is harder to answer.
Despite the fact there is evidence for this in the maps, I would say this is still inconclusive.
Additional UHF observations of the galactic center would help though.
And I'm hoping to get my hands on some of those.


## slide-56 — Third question (18s)
The third question, whether there is a distinct population of steep spectrum sources towards the galactic center, is even harder to answer.
We currently see no evidence for this but it can't be ruled out.
The plan going forward is to extend this study by jointly imaging over a wider frequency range and applying a more sophisticated analysis.


## slide-57 — Section: in summary (5s)

To summarise.
Additional UHF observations of the GC can help answer some hard questions about our own galaxy. 

## slide-58 — pfb-imaging (10s)
pfb-imaging facilitates joint mosaicing with more sophisticated algorithms to help extract more science close to the noise.

## slide-59 — Imaging all the data is hard (13s)
But imaging all the data jointly is hard.
And it's not just a big data problem, that one is mostly under control.
Optimal prior specification, uncertainty quantification, calibration model etc. are still open questions. 

## slide-60 — J09 (9s)
I'll talk a bit more about how we got the big data problem under control in the J09 session later today if you are interested.

## slide-61 — Thanks (14s)

Thanks for your attention.
