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
python3 first_principles_audit/prediction_factory/derive_superpotential_boundary_completion.py
python3 first_principles_audit/prediction_factory/verify_superpotential_boundary_shooting.py
python3 first_principles_audit/prediction_factory/derive_stiff_boundary_force.py
python3 first_principles_audit/prediction_factory/derive_breathing_response.py
python3 first_principles_audit/prediction_factory/derive_sparc_finite_disk_yukawa.py
python3 first_principles_audit/prediction_factory/sparc_physical_audit.py
python3 first_principles_audit/prediction_factory/derive_force_residual_bridge.py
python3 first_principles_audit/prediction_factory/derive_universal_residual_collector.py
python3 first_principles_audit/prediction_factory/derive_nonlinear_collector_action.py
python3 first_principles_audit/prediction_factory/derive_holo_collector_embedding_gate.py
python3 first_principles_audit/prediction_factory/derive_axisymmetric_collector_prototype.py
python3 first_principles_audit/prediction_factory/derive_scale_consistency.py
python3 first_principles_audit/prediction_factory/derive_em_spectral_fingerprint.py
python3 first_principles_audit/prediction_factory/evaluate_desi_dr1_growth.py
python3 -m first_principles_audit.prediction_factory.derive_adm_bmp_tricritical_necessity
python3 -m first_principles_audit.prediction_factory.derive_bps_radion_matter_coupling
python3 -m first_principles_audit.prediction_factory.derive_bps_biscalar_matter_geometry
python3 -m first_principles_audit.prediction_factory.derive_bps_volume_constraint_selector
python3 -m first_principles_audit.prediction_factory.derive_c1_bk_derivative_gate
python3 -m first_principles_audit.prediction_factory.derive_c2_critical_continuum_gate
python3 -m first_principles_audit.prediction_factory.derive_c3_geometric_transition_gate
python3 -m first_principles_audit.prediction_factory.derive_c2_band_edge_continuum
python3 -m first_principles_audit.prediction_factory.derive_dirac_critical_bath_gate
python3 -m first_principles_audit.prediction_factory.derive_dirac_bath_red_team_map
python3 first_principles_audit/prediction_factory/build_master_prediction_registry.py
```

## Minimal microscopic-mechanism ladder

`artifacts/minimal_mechanism_campaign.json` is the fail-closed C1 -> C2 -> C3
campaign. Its step records, theory inputs, gate artifacts and test sources are
content-addressed. Its declared input set contains no observational table; it
authorizes no parameter fit or physical action and cannot promote a new force,
lensing result or publication. This provenance statement covers the declared
repository paths; it is not presented as a recursive audit of every historical
ancestor.

The present result is `C1=failed`, `C2=failed`, `C3=blocked`. None of the three
steps is labelled target-blind: C1 tests the known Berezhiani--Khoury candidate,
C2 knows its acceptance target, and C3 knows the required mechanism structure.
C1 rejects that candidate as a completion of the current HOLO action. C2 rejects
only the frozen compact seven-pole model, not every possible critical continuum.
C3 remains open because nine of ten microscopic action, constraint, source and
branch-selection requirements are missing. The content hashes preserve the
reconstruction, but the record times and initial dirty-worktree state are
explicitly declared metadata, not independently authenticated history. When
Git metadata is available, validation additionally requires the declared
baseline commit to exist and be an ancestor of the inspected `HEAD`.

Three one-shot, history-free and tool-free Skai review requests were attempted.
All ended in provider errors, so the campaign records them as inconclusive
non-evidence; no Skai answer is invented or used to decide a physics gate.
The legacy private request identifiers contain the word `BLIND`; that label is
not a blinding claim. Private request/response records remain outside the
repository. Validate the versioned campaign with:

```bash
python3 first_principles_audit/prediction_factory/validate_mechanism_campaign.py \
  first_principles_audit/prediction_factory/artifacts/minimal_mechanism_campaign.json
python3 -m unittest \
  first_principles_audit.prediction_factory.test_mechanism_campaign \
  first_principles_audit.prediction_factory.test_minimal_mechanism_campaign
```

The paper build regenerates the three theory gates and then validates this
content-addressed campaign. It intentionally does not regenerate the campaign
or its private Skai records; any changed gate hash must stop the build and start
a new recorded campaign rather than silently refreshing the old receipts.

## Post-campaign spectral branch and adversarial map

The frozen campaign is unchanged. A subsequent outside-scope C2 test now makes
the continuum fork explicit. A stable z=2 band edge derives the exact
three-halves pressure exponent but has the wrong AQUAL variational sign, so
`c2_band_edge_continuum.json` kills that candidate. A filled negative-energy
Clifford bath avoids the sign obstruction. Its uniform-static determinant gives

```text
mu(x) = 1 + x - sqrt(1 + x^2),    a0 = Lambda/y,
```

with the required deep limit, positive off-origin elliptic factors and a finite
band Newtonian limit. This is a static spectral construction. The onsite
continuum is still an infinite internal fibre, not an exhibited finite local
3+1 QFT, and it produces a nonanalytic temporal kernel. Its curve shares the
exposed target's asymptotes but is not the exact SPARC-training interpolation.

`dirac_bath_red_team_map.json` records 17 attacks across six trust boundaries.
Algebra and uniform-static spectral response pass at L0-L1. Finite regulation,
causal covariant dynamics, the current compact HOLO origin and matter/lensing
remain blocked at L2-L5. The artifact authorizes no physical force, detection,
lensing claim or publication. Reproduce the branch and tests with:

```bash
python3 -m first_principles_audit.prediction_factory.derive_c2_band_edge_continuum
python3 -m first_principles_audit.prediction_factory.derive_dirac_critical_bath_gate
python3 -m first_principles_audit.prediction_factory.derive_dirac_bath_red_team_map
python3 -m unittest \
  first_principles_audit.prediction_factory.test_c2_band_edge_continuum \
  first_principles_audit.prediction_factory.test_dirac_critical_bath_gate \
  first_principles_audit.prediction_factory.test_dirac_bath_red_team_map
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

The microscopic junction audit and real-background ADM/GHY reduction show that
functional superpotential matching has an exactly flat moduli potential:
`m^2=u^4=0`, but also `q^6=0`.  The finite-endpoint reduction resolves two
physical moduli with Planck-normalized kinetic eigenvalues
`(0.125269, 2.00317)`, so the theory has not selected a unique canonical `q`. Along
the explicit lower-fixed separation slice, minimally induced matter gives
normalized selector slopes `0.0197499449` and `4.24994900` on the two branes,
not zero.  It therefore fails the necessary even-coupling gate for leading
pure `q^2Y` on that slice.  Covariantly, an orthogonal tangent exists for either
matter brane separately and has selector curvature `-0.330977` or `-0.257821`.
No tangent is silent for both branes, and neither BPS nor positive local
diagonal quadratic/sextic terms select one.  Moreover minimal scalar matter
weights the Einstein-frame kinetic term by the inverse selector.  After its
standard `-Y` term is separated, the candidate coefficients are correctly
signed, `-0.165489 q^2Y` and `-0.128911 q^2Y`; identifying the constitutive
`Y`, selecting the tangent and fixing its normalization remain open.
The branch is compatible with, not selected by, the bulk.  A localized
sixth-order brane detuning is a clean conditional route to positive `q^6`; a
cubic brane jet is not, and the sixth-order coefficient is not fixed by the
bulk.  The closest target-independent selector tested is `F=constant`: its
unit tangent is only `0.0686272` degrees from the lower-brane silent kernel,
but its residual is nonzero.  Exact alignment requires `A'_-=0`, outside the
certified interval; on the true `F` level curve, minimal `-Y/C` then gives
`+0.00227481 q^2Y`, the wrong sign.  The shifted choice `s=C-1` repairs the
sign only by adding a new nonminimal operator.  No global-`F` constraint is in
the current action.  The separate declared stiff stabilized limit has seven
positive, canonically normalized residues with `sum(alpha)=0.106765079`; an
independent shooting calculation verifies its masses.  P7 restores the time
derivative of this force.  For `nu=Omega*ell/c`, a mode is evanescent below
`nu=mu_n` and becomes an outgoing massive wave above it.  The stiff force is
recovered exactly at `Omega=0`; the seven threshold ratios are
`1:4.214303:5.939951:7.533412:9.447842:11.514983:13.636417`.  An independently identified
`f0` would imply `ell=mu0*c/(2*pi*f0)`, but the artifact intentionally reads no
historical frequency or observation.  Source amplitude, coherence, damping,
causal distance, boundary action and detector response remain required.

## Retrospective and external checks generated now

- The SPARC audit now recomputes all 3391 velocity points with signed gas,
  disk `M/L=0.5`, and bulge `M/L=0.7`.  On the frozen 27-galaxy test split,
  the train-frozen empirical RAR gives `chi2/point=36.75` and 14.5% median
  absolute velocity error.  The current stiff force gives `371.58`, compared
  with old P6 at `414.20` and baryons at `414.23`.  An axisymmetric effective-
  disk Hankel scan with one global `ell` improves monotonically to its `1e5`
  kpc upper boundary under resolution and radial-tail variations, so it finds
  no finite-scale rescue.  Public SPARC does not provide the gas surface-
  density or vertical-density maps needed for a unique 3D convolution.  The
  residual crosses zero at `gbar=6.25719e-10 m/s^2` and requires a new common
  state-dependent source or coupling; it is not fitted galaxy by galaxy.
  `derive_universal_residual_collector.py` resolves the old `600` ambiguity:
  the stiff force scores `390.85` after the `R>=0.6 kpc` cut and `371.72` at
  `ell=600 kpc`, so neither is a success.  Its one-parameter, no-per-galaxy
  signed collector scores `36.75`, but is explicitly the empirical RAR target
  for a future nonlinear or separate ultralight action sector.  The
  repaired legacy P5 refit gives `290.98`, reaches all five bounds, and remains
  rejected genealogy.  RAR is an empirical target, not a HOLO prediction.
  A separate scale-consistency certificate shows that forcing one `ell` to
  represent both the legacy `1.600006 GeV` QCD proxy and the saturated SPARC
  boundary creates an `8.61325e40` mismatch.  The boundary would correspond to
  `f0=4.49168e-18 Hz` and `T0=7.05484 Gyr`, but it is not a measured clock.
  The earlier `203.26/60.99` comparison is kept
  only as provenance of the invalid unsigned, unit-weight input contract.
- `derive_nonlinear_collector_action.py` reconstructs the minimal
  nonrelativistic scalar action whose spherical equation reproduces the
  universal collector.  It verifies single-valuedness, local ellipticity for
  nonzero field, degeneracy at zero field, deep and Newtonian limits, and shows
  that the transition radius obeys
  `r_M=sqrt(GM/a0)`: `0.6 kpc` and `600 kpc` correspond to `2.955e8` and
  `2.955e14 Msun`, not one universal cutoff.  This is an empirical action
  target, not a microscopic or relativistic HOLO completion.
- `derive_holo_collector_embedding_gate.py` proves a conditional no-go for the
  present regular linearized sector: its canonical Yukawa response scales as
  `M` and starts with `F~X`, whereas the target scales as `sqrt(M)` and needs
  `F~X^(3/2)`.  New derivative or nonperturbative sectors remain open and must
  derive `a0` independently.
- `derive_axisymmetric_collector_prototype.py` verifies second-order
  cylindrical convergence on a Plummer control and detects the curl obstruction
  of the algebraic closure for flattened sources.  It blocks the physical SPARC
  PDE because the local tables do not identify `rho(R,z)`, thicknesses, or
  boundary conditions; `Vobs` enters only the final non-PDE diagnostic score.
- A four-bin marginal diagnostic using published DESI DR1 ShapeFit entries
  gives diagonal `chi2=2.6917` for the frozen dictionary curve and `2.4189`
  for matched LCDM.  The small `delta chi2=+0.2729` gives no preference for
  HOLO and is not a substitute for the official correlated likelihood.
- The Wilson-loop analyser is implemented and tested, but fails closed because
  the available lattice summaries do not contain gauge-link configurations.
  Plaquettes and the ED endpoint proxy are not promoted to rectangular Wilson
  loops or a string tension.
