# Observational prediction factory

This directory freezes a leakage-aware observational protocol without fitting
or changing the HOLO model.  It deliberately separates three things that were
previously easy to conflate:

1. an arithmetic reproduction of a published local artefact;
2. an evaluation on data that have already influenced or been inspected by the
   pipeline; and
3. a genuinely untouched confirmatory holdout.

The current result is fail-closed: **no observational channel in this checkout
is presently a clean confirmatory holdout**.  SPARC, BOSS, and the historical
NIST comparison remain useful audit receipts.  The local DESI residual is a
model-derived residual, not an official observed data vector.

## Run

From the repository root:

```bash
python3 first_principles_audit/prediction_factory/prediction_factory.py
python3 first_principles_audit/prediction_factory/prediction_factory.py --check
python3 first_principles_audit/prediction_factory/test_prediction_factory.py -v
```

The builder uses only the Python standard library.  It writes three versioned
documents:

- `observational_inventory.json`: local files, hashes, data content, redaction,
  and calibration exposure;
- `sparc_split_v1.json`: deterministic galaxy-level 122/26/27
  train/validation/test assignment; and
- `prediction_manifest.json`: readiness, reason codes, metrics, baselines, and
  the next admissible test for each prediction.

## Local inventory and admissible use

| Channel | Local observational content | Present use |
|---|---|---|
| SPARC | 175 per-galaxy derived score rows; no point-level curves/covariance | descriptive all-data-fit audit only |
| BOSS DR12 | three observed `fσ8` values and full 3x3 covariance | historical external comparison; already inspected |
| DESI | constructed residual and response/inversion artefacts | not an observational evaluation |
| NIST clocks | predicted series and summary metrics; observed/residual series redacted | historical null/poor-fit audit only |

The SPARC split is useful for rebuilding the analysis honestly, but it cannot
retroactively blind outcomes already used to optimize five global parameters.
After a train-only refit and one validation pass, its test group is an honest
development estimate; a new external galaxy catalogue is still required for a
strict confirmation.

For growth, the barrier is by **survey release**, not by correlated redshift
row.  BOSS DR12 and inspected DESI Year 1 material are development context.  A
later official likelihood that has not been used to alter this protocol is the
prospective test.

For clocks, samples from the same time series must never be randomly
interleaved across train and test.  The split unit is an independent acquisition
session/day/site/species.  New session IDs are assigned by a frozen SHA-256 rule
to 50% calibration, 25% validation, and 25% test; every channel from one session
stays in the same bucket.  The two historical NIST channels have already been
used and therefore cannot be recycled as confirmation, regardless of their hash
bucket.

## Fair scoring

Galaxy models receive the same masks, covariance, baryonic inputs, and nuisance
policy.  The primary score is held-out predictive log likelihood; the old
velocity-weighted ranking loss is descriptive only.  Baselines include
baryons-only Newton, a train-frozen canonical RAR/MOND law, and a predictive
abundance-matched CDM model.  A nuisance-profiled comparison is secondary and
must give every model the same prior budget.

Growth uses the official full-shape likelihood or `rᵀ C⁻¹ r`, with identical
fiducial/AP conventions and scale cuts for HOLO and matched ΛCDM.  Clock tests
use independent-session predictive likelihood or a preregistered matched
filter with colored-noise covariance, injection recovery, environmental vetoes,
and a trials correction whenever signal parameters are scanned.

The brane-localized metric-only branch predicts no direct classical
scalar--Maxwell vertex.  The distinct bulk-photon branch now has a derived
trace-lapse vertex and a photon KK tower, but still no dimensional clock signal
until the boundary branch, `ell`, source and atomic coefficients are fixed.

## Executable physical-link graph

[`MASTER_PREDICTION_REGISTRY.md`](MASTER_PREDICTION_REGISTRY.md) is the single
human-readable map of derived, conditional, phenomenological, and blocked
links.  The adjacent JSON contains the exact values and hashes.  Rebuild it
after regenerating any component:

```bash
python3 first_principles_audit/prediction_factory/derive_boundary_branches.py
python3 first_principles_audit/prediction_factory/verify_nd_ultralight_shooting.py
python3 first_principles_audit/prediction_factory/material_prediction_factory.py
python3 first_principles_audit/prediction_factory/derive_em_kernel_completion.py
python3 first_principles_audit/prediction_factory/derive_robin_boundary_family.py
python3 first_principles_audit/prediction_factory/derive_em_spectral_fingerprint.py
python3 first_principles_audit/prediction_factory/evaluate_desi_dr1_growth.py
python3 first_principles_audit/prediction_factory/build_master_prediction_registry.py
```

The current branch audit finds that changing only the IR Neumann condition to
Dirichlet does not cleanly remove the excluded massless mode: it produces an
independently verified UV-coupled ultralight mode with
`mu=0.0027447613` and `beta_UV=0.0542909541`.  Dirichlet data on the UV matter
face instead make an exact point probe decouple.  These are conditional
alternatives, not permission to choose a boundary after seeing data.

The electromagnetic completion proves that the functional Eq. 39 form follows
if the photon is a five-dimensional bulk field.  For

```text
S_gamma = -(4 g5^2)^-1 integral sqrt(-g) Z(chi) F_MN F^MN
```

the normalized zero-mode weight is
`K_gamma = exp(A) Z(chi) |f_gamma|^2 / integral exp(A) Z(chi) |f_gamma|^2`.
That is the density in the *constructed conformal coordinate*.  The historical
1999-point numerical artifact instead used the raw trace coordinate later
identified as domain-wall `u`; for `Z=1` the correct `u`-density is uniform.
Its maximum discrepancy from the historical kernel is `0.395739`, so the old
UV projection is rejected rather than relabelled.

The almost-radial scalar constraint then supplies the missing bulk-photon
vertex:

```text
A_u h_uu = (d_u h)/4
d_gamma,n(c) = sqrt(I_g/3)
               * integral exp(c chi) f_n'/A_u du
               / integral exp(c chi) du
```

At the minimal point `Z=1`, no coefficient is fitted.  The positive NN values
begin `3.94563, -2.52337, 2.90124`, while the independent photon tower begins
`mu_gamma = 0, 0.652597, 1.301427, 1.939255`.  Photon and scalar masses share
the same unfixed `ell`, creating a cross-sector double-comb template.  Finite
elements, grid convergence, a determinant check, Hellmann--Feynman differences
and independent shooting all pass.  This is conditional model output, not a
clock detection.

The positive Robin endpoint family adds a second non-arbitrary result.  IR
stiffness alone cannot raise the lightest scalar above
`mu=0.00274497647`; UV stiffness can raise it but drives an avoided crossing
where the UV residue moves between poles.  Across the family,

```text
d(mu_n^2)/d b_UV = f_n(UV)^2 = 3 beta_n(UV)^2/I_g.
```

The identity is numerically verified, but the microscopic endpoint
coefficients remain theory inputs and are not selected from observations.

## Retrospective and external checks generated now

- The SPARC galaxy-level 122/26/27 refit improves on baryons-only Newton in
  22/27 test galaxies, but its cluster-bootstrap improvement crosses zero.
  More importantly, it is much worse than a one-global-parameter RAR baseline:
  P5 `chi2/point=203.26` versus RAR `60.99`, and P5 wins only 8/27.  The P5
  optimizer also exhausted its budget and reached four preregistered bounds.
  This is retrospective development evidence, not confirmation.
- A four-bin marginal diagnostic using published DESI DR1 ShapeFit entries
  gives diagonal `chi2=2.6917` for the frozen dictionary curve and `2.4189`
  for matched LCDM.  The small `delta chi2=+0.2729` gives no preference for
  HOLO and is not a substitute for the official correlated likelihood.
- The Wilson-loop analyser is implemented and tested, but fails closed because
  the available lattice summaries do not contain gauge-link configurations.
  Plaquettes and the ED endpoint proxy are not promoted to rectangular Wilson
  loops or a string tension.
