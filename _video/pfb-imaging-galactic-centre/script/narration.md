# Narration — Scalable Statistical Inference for Wide-Field Radio Interferometry

URSI GASS 2026, Session J09. Target **13:30** against a hard 15:00 limit.

One block per frame, in order. Record each as `audio/raw/slide-NN.wav` matching the frame
number. `(NNs)` is the budget, not a stopwatch — read at a natural pace and let the totals
sort themselves out; the build reports the real duration.

Pace assumed is ~140 wpm, slower than conversation, because this is equation-heavy material.
Where a line reads awkwardly out loud, rewrite it — prose that looks fine on the page often
does not survive being spoken.

---

## slide-01 — Title (22s)

Hello. I'm Landman Bester, from SARAO and Rhodes University. This talk is about making
statistically principled imaging affordable at survey scale — and about a package called
`pfb-imaging` that we've applied to MeerKAT UHF observations of the Galactic Centre.

## slide-02 — Three MeerKAT UHF-band pointings (8s)

Let me start with the picture, because the rest of the talk is really an explanation of how
we got here.

## slide-03 — Galactic Centre teaser (14s)

This is roughly five square degrees of the Galactic Centre, at UHF band. Three separate
MeerKAT pointings. Filaments, shells, compact sources, and diffuse emission spanning a very
large dynamic range.

## slide-04 — teaser caption (8s)

The three pointings were not imaged separately. 
They were reconstructed jointly, under a single sparsity-promoting prior. 
We used the Sparsity Averaging and Reweighting Analysis framework incorporated into pfb-imaging,
but I am hoping to convince you that the prior is not the point here.

## slide-05 — The adoption gap (8s)

To explain why that matters, I want to start with a gap between what the imaging literature
knows and what we actually run.

## slide-06 — CLEAN: point-source prior (12s)

CLEAN is very good at what it was designed for. It carries a point-source prior, matched to
the emission that dominated the fields it was built on.

## slide-07 — CLEAN: cheap iterations (11s)

Its iterations are cheap, because the minor cycle never touches the data — it works entirely
in image space.

## slide-08 — CLEAN: operational knowledge (10s)

And it comes with fifty years of accumulated operational knowledge about how to drive it.

## slide-09 — CLEAN is not wrong (12s)

I want to be clear about this: half this room ran CLEAN this week. Nothing that follows is an
argument that it is wrong.

## slide-10 — The sky is not a collection of points (18s)

But the sky is not a collection of points. On the left is ESO 137-006 reconstructed with
uSARA; on the right, the same field with multi-scale CLEAN. A simplistic prior does not
produce a realistic image of complex diffuse structure — you can see it in the texture.

## slide-11 — The literature already has answers (14s)

The literature has known this for a long time. Maximum entropy since the eighties. Sparsity
and compressed sensing from around 2009. Bayesian field inference — RESOLVE, and algorithm I am very fond of — from 2013.
Plug-and-play and learned priors are gaining traction.

## slide-12 — each replaces the prior (12s)

Every one of these replaces the point-source prior with something better matched to complex,
extended emission. Not point sources mind you, we'll get back to that.

## slide-13 — none are routinely deployed (12s)

To my knowledge, none of them are routinely deployed on survey-scale data. That is the gap pfb-imaging aims to
address.

## slide-14 — Two walls (16s)

There are two barriers to making this practical. The first is data volume — terabytes per observation, where out-of-core and distributed processing is becoming the norm, not the hard case. The second is
implementation burden: bespoke code, maintained by a small group specialising in algorithm
development, and inherited by nobody.

## slide-15 — the obstacle is not the mathematics (10s)

Notice that neither wall is mathematical. The obstacle has not been the maths.

## slide-16 — Imaging as inference (7s)

So let me set the problem up as inference, and then attack both walls directly.

## slide-17 — the measurement equation (12s)

The measurement equation. Visibilities `y` are a linear operator `R` applied to the sky `x`,
plus noise, which we take to be Gaussian with covariance Sigma.

## slide-18 — y (10s)

`y` is the visibilities — for a MeerKAT observation, of order ten to the ten of them.

## slide-19 — R (12s)

`R` is the measurement operator. It carries the sampling, the weighting, the w-term, and the
primary beam — everything the instrument does to the sky.

## slide-20 — x (10s)

And `x` is the sky we actually want.

## slide-21 — ill-posed (13s)

This problem is ill-posed. There are far more unknowns than the data constrain, so Bayesian
modelling is not an optional refinement here — it is what makes the problem well-defined.

## slide-22 — Maximum a posteriori (15s)

Take the maximum a posteriori estimate, and the problem splits cleanly into two terms: minus
log-likelihood, which I'll call `f`, plus minus log-prior, which I'll call `r`.

## slide-23 — the table (14s)

These two terms have very different characters. `f` is data fidelity, fixed by the
instrument, and smooth. `r` is the prior — chosen by us, and possibly non-smooth. That
asymmetry is the whole design.

## slide-24 — the likelihood (10s)

For completeness, `f` is the standard Gaussian likelihood, weighted by the noise covariance —
which, because of calibration errors and RFI, we do not know exactly in practice. This is where robust
statistical modelling can help.

## slide-25 — Prior should be a user choice (11s)

The prior should be a user choice. Different fields genuinely require different choices of
`r`.

## slide-26 — the proximal operator (15s)

Non-smoothness is not an obstacle, because a non-smooth prior is handled through its proximal
operator — the argmin of the prior plus a quadratic proximity term. That gives us a uniform
interface to priors that have no gradient.

## slide-27 — pfb hosts priors (11s)

So `pfb-imaging` does not impose a prior. It hosts them.

## slide-28 — CLEAN is recoverable (10s)

And CLEAN itself is recoverable in this framework: a sparsity prior with a particular
minor-cycle solver.

## slide-29 — Standing on the PyData stack (15s)

That mostly handles the maths. For the implementation wall, we lean heavily in the PyData community.
For example, we are trying to move away from bespoke formats like measurement sets to rely on industry standards such as xarray and zarr, specifically through xarray-ms and the MSv4 standard that is being developed.
For distribution and scheduling, we lean on packages like Ray and Dask.
`pfb-imaging` supplies the operators and solvers required to solve the inverse problem. 
And post-processing is handled with `spimple`, a package I don't have time to delve into.

## slide-30 — Africanus philosophy (12s)

This is the Africanus philosophy. The scheduler, the storage format, and the array semantics
are inherited, not re-invented.

## slide-31 — what's left is the algorithm (10s)

The maintenance burden moves to the (much larger) PyData ecosystem. What's left for us to write is the algorithms.

## slide-32 — Making general priors affordable (7s)

Which leaves cost. This is the part that actually blocks adoption.

## slide-33 — forward-backward (13s)

Forward–backward splitting on `f` plus `r`: take a gradient step on the likelihood, then
apply the proximal operator of the prior.

## slide-34 — the gradient (14s)

Write out the gradient and you get `H x` minus `d`, where `H` is the Hessian — R-dagger,
noise-weighted, R — and `d` is the dirty image.

## slide-35 — the cost (13s)

Applying `H` naively means a degrid and a grid over every visibility, on every single
iteration. At ten-to-the-ten visibilities, that is the end of the conversation.

## slide-36 — the real barrier (10s)

This — not the prior — is the barrier to adopting more sophisticated methods.

## slide-37 — CLEAN's approximation (16s)

CLEAN's minor cycle is cheap precisely because it never applies `H` exactly. It assumes `H`
acting on `x` is approximately the PSF convolved with `x` — a convolution, which you evaluate
by FFT at image cost rather than data cost.

## slide-38 — major cycles (14s)

The approximation isn't perfect, which is why major cycles exist: to compute the exact
residual periodically. But notice the trick is not tied to the point-source prior at all. It
is a statement about the Hessian `H`.

## slide-39 — Borrow the trick, keep the prior (17s)

So borrow the trick and keep whatever prior you want. Major cycles stay exact, at data cost,
and there are few of them. Minor cycles are approximate, at FFT cost, and there are many.

## slide-40 — the preconditioner (11s)

`H`-tilde is the fast, invertible approximation to the Hessian — a preconditioner.

## slide-41 — the result (11s)

The result is an arbitrary prior iterating at CLEAN-like cost: a generalised, forward-modelling based
minor cycle.

## slide-42 — MeerKAT UHF — the Galactic Centre (7s)

So let's go back to the Galactic Centre and see what that buys.

## slide-43 — The observation (16s)

A little bit more about the observation.
Like I said, it's MeerKAT at UHF band.
Three pointings, reconstructed jointly.
Roughly a terabyte of data before averaging.
At a field of view of five square degrees, and a Nyquist over-sampling factor of about two,
that translates to a ten-thousand by ten-thousand pixel cube which we imaged in eight bands.
It takes the SARA algorithm about fifty hours to solution.
That's completely unsupervised, no manual masking or anything like that.

## slide-44 — the hard case (10s)

Complex extended emission at high dynamic range — precisely the case a point-source prior
handles worst.

## slide-45 — What forward modelling buys (14s)

Forward modelling also lets us put instrumental effects where they belong: inside the
measurement operator. Here, the inhomogeneous primary beams across the three pointings enter
`R` and are handled in a statistically robust way.

## slide-46 — one sky model (10s)

Jointly means one sky model, one prior, and all of the data at once.

## slide-47 — consistent deconvolution (10s)

Deconvolution is therefore consistent across the pointing boundaries.

## slide-48 — no stitching artefacts (9s)

There are no stitching artefacts to explain away, because nothing was stitched.

## slide-49 — uv-coverage (9s)

The combined uv-coverage is better than any single pointing, which buys resolution.

## slide-50 — the beam enters R (10s)

And the primary beam enters the measurement operator, rather than arriving as a post-hoc
correction.

## slide-51 — CLEAN result (20s)

Here is the field mosaicked in the conventional way, with a multi-scale CLEAN prior. It is a
perfectly respectable image — look at the diffuse emission and the background texture. But the negative
bowls are telling us that we are deconvolution limited.

## slide-52 — SARA result (22s)

And here is the same data, reconstructed jointly under the SARA prior. The filamentary
structure is sharper, the diffuse emission is smoother, the background is markedly cleaner,
and the negative bowls are gone. That strongly supports the argument that they are deconvolution
artifacts in the MSClean images.

## slide-53 — Intrinsic model (18s)

And this is the intrinsic model — the actual quantity being inferred, before any restoring
beam is applied. This is what the prior is acting on. It's not perfect, we don't have uncertainty estimates for it yet,
but we are working on that.

## slide-54 — Caveat: computational cost (13s)

Now the caveats, honestly. It costs more compute than CLEAN-based methods. The cost is
dominated by image-space operations — FFTs and wavelet transforms — rather than by the data.

## slide-55 — Caveat: convergence (13s)

Runtime is sensitive to convergence criteria. The sub-iterative solvers need careful tuning,
and that tuning may well be observation-dependent.

## slide-56 — Caveat: point sources (13s)

And point-source fidelity. These priors mostly target extended emission, and they are often
sub-optimal for point sources — which is exactly where CLEAN is strong.

## slide-57 — Where this leaves us (6s)

So where does that leave us?

## slide-58 — Principled (13s)

Principled: imaging is posed as MAP estimation, so the prior is an explicit, swappable choice
rather than an emergent property of a loop.

## slide-59 — Maintainable (12s)

Maintainable: the machinery is inherited from the PyData community, which is far larger than
ours and maintains it for us.

## slide-60 — Affordable (12s)

And affordable: preconditioning gives general priors CLEAN-like iteration cost, and reduces
the number of major cycles we need.

## slide-61 — MeerKAT+ (16s)

What's next. MeerKAT Plus brings dishes with different primary beams, and those
inhomogeneous beams can be handled by splitting the data into baseline groups —
MeerKAT–MeerKAT, MeerKAT–MeerKAT-Plus, and Plus–Plus — which is very close to what
on-the-fly mosaicing already does.

## slide-62 — Acceleration (10s)

Image-space operations — the FFTs especially — accelerate very well on GPUs.

## slide-63 — Better priors (11s)

Learned priors such as AIRI could converge in fewer iterations, and may improve point-source
reconstruction.

## slide-64 — Multi-SPW and field (10s)

Imaging all the Galactic Centre data simultaneously, for a high-fidelity reconstruction over
the full bandwidth.

## slide-65 — Polarisation (9s)

And polarisation imaging, which is coming soon.

## slide-66 — Thanks (15s)

Thank you. The code is on GitHub under ratt-ru/pfb-imaging, and there's an Africanus
paper on the arXiv if you want the detail on the underlying stack. Happy to take
questions.
