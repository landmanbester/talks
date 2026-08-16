# What is the resolution of a MAP image?
### Concluding slides — URSI GASS

---

## Slide 1 — We report images without reporting what a pixel means

For a quadratic regulariser, the MAP estimate is a **linear filter applied to the truth**:

$$
\hat{x} \;=\; \underbrace{\left(A^H N^{-1} A + \lambda L\right)^{-1} A^H N^{-1} A}_{\displaystyle R}\; x_{\rm true} \;+\; \text{noise term}
$$

- Row $j$ of $R$ is the **effective PSF at pixel $j$** — the average of the sky that $\hat{x}_j$ actually reports.
- $R = I$ only where the data term dominates. Elsewhere the prior sets the width.
- $N^{-1}$ sits inside $R$ $\Rightarrow$ **resolution is a function of local SNR**, not an instrumental constant.
- For non-quadratic priors ($\ell_1$, TV, learned denoisers) $R$ is the Jacobian of the solver map linearised about the solution — it depends on **source brightness**, so the resolution field changes with the object being imaged.

> The restoring beam *asserts* a resolution. It does not *measure* one.

*Presenter note: this is the punchline of the whole talk — the point estimate is not a sufficient statistic, and the thing it is missing is not just error bars, it is the definition of the quantity being estimated.*

---

## Slide 2 — Why this breaks downstream science

Two failure modes, both of which look like astrophysics:

**Spatially varying $R$.** Hotspots are super-resolved, low-brightness lobe edges are prior-smoothed. Spectral index maps then acquire structure that tracks brightness contours — reported in the literature as "steepening towards the edges."

**Frequency-varying $R$.** SNR per channel varies with intrinsic spectrum, primary beam, and RFI flagging. So $R = R(\nu)$ *even in a jointly deconvolved cube.* Convolving to a nominal common beam imposes a floor; it does not remove the variation underneath it.

For spectral ageing this is fatal in a specific way: the observable is curvature in $\log I$ vs $\log \nu$, and a frequency-dependent averaging kernel produces exactly that curvature. **The systematic is degenerate with the signal.**

And the standard downstream $\chi^2$ compounds it: pixels are correlated by $R$, the correlation length is unknown, so parameter uncertainties on $(\alpha_{\rm inj}, \nu_b)$ are not merely wrong — they are wrong by an unquantified factor.

---

## Slide 3 — This is a solved problem in four other fields

| Field | Name for $R$ | Canonical reference |
|---|---|---|
| Geophysics / normal modes | Averaging (resolving) kernel | Backus & Gilbert 1968, 1970 |
| Seismic tomography | Model resolution matrix $G^\dagger G$ | Menke 1989; Nolet 2008 |
| Atmospheric sounding | Averaging kernel matrix | Rodgers 2000 |
| Emission tomography (PET/SPECT) | Local impulse response | Fessler & Rogers 1996 |
| CMB | Window function | Tegmark 1997 |
| Statistics | Smoother / hat matrix | Hastie & Tibshirani 1990 |

Radio interferometry is the outlier: we hid the issue behind the restoring beam, and it worked for as long as deconvolution was effectively linear and images were noise-limited.

**Two results worth importing verbatim:**

1. **Backus–Gilbert trade-off curve.** Do not report *a* model. Sweep the regularisation and report resolution width against variance at each location. The curve is the result; picking a point on it is a choice that must be declared.
2. **Fessler's uniform-resolution penalties.** In penalised-likelihood PET the resolution is object- and count-dependent — the *same* pathology. The fix is to design the penalty so that $R$ is approximately shift-invariant by construction, accepting worse variance in exchange for an interpretable image. Directly transferable to imaging where the science product is a per-pixel fit.

---

## Slide 4 — And one cautionary result

**Checkerboard / spike tests are known to be misleading** (Lévêque, Rivera & Wittlinger 1993).

- Recovery of a pattern at one spatial wavelength says little about recovery at others.
- For non-linear inversions the *amplitude* of the injected pattern changes the answer.
- Column $j$ of $R$ ("where does a spike smear to") $\neq$ row $j$ ("what average do I report") unless $R$ is symmetric — and it generally is not.

This is a direct warning about how we currently validate deconvolution algorithms in radio astronomy: single-point-source and single-scale simulation tests measure a corner of $R$ and are extrapolated to the whole operator.

---

## Slide 5 — What we can actually compute

$R$ is $N^2$ and cannot be formed. It can be **probed**, cheaply, with modern autodiff:

- **$R v$ for a chosen probe** — one JVP through the solver's fixed point. A probe at pixel $p$ returns the local averaging kernel; a handful of locations per channel gives the resolution field.
- **$\mathrm{diag}(R)$** — Hutchinson stochastic estimation, $\mathcal{O}(10)$ probes.
- **Lanczos / bidiagonalisation approximations** — Zhang & Thurber 2007, developed for exactly this scaling problem.
- **$\mathrm{tr}(R)$ = effective degrees of freedom** — gives a defensible parameter count for model comparison in the spectral fit, which is otherwise ill-defined under correlated pixels.

Cost: $\mathcal{O}(\text{one extra solve})$ per probe. This is affordable today and we are not doing it.

---

## Slide 6 — Recommendations

1. **Publish a resolution field, not a beam.** Per frequency. If $R$ varies across the band, the spectral fit is not trustworthy and that should be visible in the paper.
2. **Where the science is a per-pixel fit, fix the resolution by construction.** Parameterise $x = k \ast s$ with $k$ a fixed kernel and solve for $s$. Forfeit super-resolution; gain a defined estimand.
3. **Better: move the science model into the forward problem.** Fit $(\alpha_{\rm inj}, \nu_b)$ against visibilities. Then the regulariser and the physical model are the same object, and there is no double-counting of the spectral prior.
4. **Better still: stop producing point estimates.** Posterior samples make the question disappear — you never have to declare what a pixel means, because the uncertainty carries it. `resolve` / NIFTy, and the convex-optimisation UQ of Cai, Pereyra & McEwen, are existence proofs at survey scale.
5. **Validate against $R$, not against spikes.** Injection tests spanning the angular scales and brightnesses of the target, with the recovered-vs-true bias reported as a curve.

> The MAP estimate is a filtered version of the sky with an unreported, spatially and spectrally varying filter. Every science product we derive from one inherits that filter. Other fields have been reporting theirs for fifty years.

---

## References

**Averaging kernels and resolution matrices**
- Backus, G. & Gilbert, F. 1968, *The resolving power of gross Earth data*, Geophys. J. R. Astron. Soc., 16, 169
- Backus, G. & Gilbert, F. 1970, *Uniqueness in the inversion of inaccurate gross Earth data*, Phil. Trans. R. Soc. A, 266, 123
- Menke, W. 1989, *Geophysical Data Analysis: Discrete Inverse Theory*, Academic Press
- Nolet, G. 2008, *A Breviary of Seismic Tomography*, CUP
- Zhang, H. & Thurber, C. 2007, *Estimating the model resolution matrix for large seismic tomography problems based on Lanczos bidiagonalization with partial reorthogonalization*, Geophys. J. Int., 170, 337
- Lévêque, J.-J., Rivera, L. & Wittlinger, G. 1993, *On the use of the checker-board test to assess the resolution of tomographic inversions*, Geophys. J. Int., 115, 313

**Atmospheric retrieval (most readable Bayesian derivation)**
- Rodgers, C. D. 2000, *Inverse Methods for Atmospheric Sounding: Theory and Practice*, World Scientific — Ch. 3 on averaging kernels and degrees of freedom for signal

**Medical imaging — SNR/object-dependent resolution in penalised likelihood**
- Fessler, J. A. & Rogers, W. L. 1996, *Spatial resolution properties of penalized-likelihood image reconstruction: space-invariant tomographs*, IEEE Trans. Med. Imag., 15, 346
- Stayman, J. W. & Fessler, J. A. 2000, *Regularization for uniform spatial resolution properties in penalized-likelihood image reconstruction*, IEEE Trans. Med. Imag., 19, 601
- Nuyts, J. & Fessler, J. A. 2003, *A penalized-likelihood image reconstruction method for emission tomography, compared to postsmoothed maximum-likelihood with matched spatial resolution*, IEEE Trans. Med. Imag., 22, 1042
- Qi, J. & Leahy, R. M. 2000, *Resolution and noise properties of MAP reconstruction for fully 3-D PET*, IEEE Trans. Med. Imag., 19, 493

**Statistics**
- Hastie, T. & Tibshirani, R. 1990, *Generalized Additive Models*, Chapman & Hall — trace of the smoother matrix as effective degrees of freedom
- Hastie, T., Tibshirani, R. & Friedman, J. 2009, *The Elements of Statistical Learning*, 2nd ed., §5.4

**Radio interferometry — the issue, mostly implicit**
- Narayan, R. & Nityananda, R. 1986, *Maximum entropy image restoration in astronomy*, ARA&A, 24, 127
- Briggs, D. 1995, PhD thesis, NMIMT — weighting, and the resolution/sensitivity trade-off
- Rau, U. & Cornwell, T. J. 2011, *A multi-scale multi-frequency deconvolution algorithm for synthesis imaging in wide-band radio interferometry*, A&A, 532, A71
- Honma, M. et al. 2014, *Imaging black holes with sparse modeling*, PASJ, 66, 95 — super-resolution claims, i.e. $R \neq$ instrumental beam
- Akiyama, K. et al. 2017, ApJ, 838, 1 — sparse imaging resolution properties

**Radio interferometry — posterior approaches**
- Junklewitz, H. et al. 2016, *RESOLVE: A new algorithm for aperture synthesis imaging of extended emission in radio astronomy*, A&A, 586, A76
- Arras, P. et al. 2021, *Comparison of classical and Bayesian imaging in radio interferometry*, A&A, 646, A84
- Arras, P. et al. 2022, *Variable structures in M87\* from space, time and frequency resolved interferometry*, Nature Astronomy, 6, 259
- Cai, X., Pereyra, M. & McEwen, J. D. 2018, *Uncertainty quantification for radio interferometric imaging: I. Proximal MCMC methods* / *II. MAP estimation*, MNRAS, 480, 4154 / 4170
- Repetti, A., Pereyra, M. & Wiaux, Y. 2019, *Scalable Bayesian uncertainty quantification by local hypothesis testing*, SIAM J. Imaging Sci., 12, 87

**Spectral ageing (the downstream victim)**
- Harwood, J. J. et al. 2013, MNRAS, 435, 3353 — BRATS, and the common-beam / matched-$uv$ prescription
- Quici, B. et al. 2022, PASA, 39, e042 — `synchrofit`

---

*Note: please verify volume/page numbers against ADS before the slides go final — several of the medical-imaging and geophysics citations are from memory.*
