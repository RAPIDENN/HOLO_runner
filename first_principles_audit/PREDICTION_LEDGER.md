# Prediction ledger after the first-principles audit

The word “prediction” is reserved here for a quantity fixed before comparison
with the datum used to test it.  A reproducible fit, dictionary, inverse
reconstruction, or arithmetic conversion is listed separately.

## Current adjudication

| Result | Status | Quantitative reading |
|---|---|---|
| Neumann scalar zero mode | Derived within the conditional compact branch, but excluded if massless and unscreened | `beta_0=0.0542901`, `alpha_0=2 beta_0^2=0.00589483`, `gamma=0.988279`; the force is about 472 times the conservative Cassini 2-sigma scalar allowance. |
| Six positive compact modes | Conditional correlated template, not yet a viable model on its own | `sum alpha_n=7.20230e-5`; mass ratios `1:1.686942:2.334807:2.985996:3.651009:4.327036`; every range scales with the still-free `ell`. |
| Positive Robin boundary family | Operator-derived phase map, not a selected boundary theory | IR stiffness alone gives `mu_0<=0.00274497647`; UV stiffness creates an avoided crossing and transfers the UV residue between poles. Exactly `d(mu_n^2)/db_UV=f_n(UV)^2=3 beta_n^2/I_g`. |
| Conditional functional-BPS branes | Exact flat bi-scalar branch; even selector jets exist but the physical tangent is unselected | On the reconstructed 1979-point flow, `lambda_-=W` and `lambda_+=-W` cancel bulk, GHY and brane terms for every endpoint pair (maximum raw relative residual `1.51e-8`), hence `m^2=u^4=q^6=0`. The finite-endpoint map is invertible and the Planck-normalized kinetic metric has eigenvalues `(0.125269, 2.00317)`: both endpoint moduli are physical. The lower-fixed separation slice has nonzero selector slopes `0.0197499449` and `4.24994900`. Covariantly, either single-brane selector has a stationary tangent with curvature `-0.330977` or `-0.257821`, but there is no common tangent and neither BPS nor positive local diagonal `p=2`/`p=6` terms select one. Minimal scalar matter uses the inverse selector and, after separating its standard `-Y`, gives correctly signed candidates `-0.165489 q^2Y` and `-0.128911 q^2Y`. The constitutive `Y`, tangent and normalization remain unselected, so the physical vertex is unproved. A sixth-order detuning gives positive `q^6` only conditionally and is new brane physics. |
| Fixed warped-volume selector | Target-independent near-alignment, rejected as the minimal completion | The `F=constant` Planck-normalized unit tangent is `0.0686272` degrees from the lower-brane silent kernel but leaves residual `9.69442e-4`; the upper angle is `86.1253` degrees. Exact lower alignment is equivalent to `A'_-=0` or `W_-=0`, whose linearized location lies just outside the certified interval. In that formal limit the actual `F` level curve has `C=1+0.00227481 q^2+...`, so minimal `-Y/C` leaves `+0.00227481 q^2Y`, opposite to the requested sign. Choosing `s=C-1` would fix the sign but is another nonminimal operator. The repository contains no global-`F` constraint. |
| Stiff-boundary force | Current action-derived dimensionless candidate, not a detection | Seven positive modes have `sum alpha_n=0.106765079`, giving at most `1.106765` times baryonic acceleration or `1.052029` times circular speed. `ell` and the physical boundary selection remain unfixed. |
| Coordinate-correct Eq. 39 | Derived bulk-Maxwell measure; historical numerical projection rejected | In domain-wall `u`, `K_u=1/Delta u=0.507421595`; after `du=e^A dz_c`, `K_zc=e^A/Delta u`. The old mislabeled-grid kernel differs from the correct `u` density by as much as `0.395739`. |
| Scalar--photon double comb | Conditional action-derived fingerprint for a bulk photon | Photon masses start `mu_gamma={0,0.652597,1.301427,1.939255}`; scalar `d_gamma,n` is fixed by the lapse overlap. Photon and scalar towers share the same unfixed `ell`. |
| Stored scalar ratio `1.5454665` | Operator diagnostic | Agrees with the broad 1999 value `1.54(11)`, but is 10.1% below the modern continuum SU(3) ratio `1.7195(160)`. |
| `sigma=0.203 GeV^2`, `m0=1.60 GeV` | External endpoint conversion | Uses the ED endpoint plus chosen `alpha'` and `c=3.55`; no Wilson area law determines either number. |
| Corrected 5D Ricci quantity | Derived dimensionless geometry | `R5_hat=-8A_uu-20A_u^2`; it agrees with the Einstein-trace and conformal-coordinate calculations. It fixes mode/curvature ratios, not seconds or amplitudes. |
| Historical LOCK5 | Circular calibration | Uses `1.6664` and `2.1590 mHz` to infer `xi` and then reconstructs `2.1590 mHz`; it also mixes bulk `R5` with terrestrial matter `R4`. |
| Historical SPARC calibration | Rejected input contract | The old 150/175 and 149/175 counts used unsigned, unit-weight baryonic quadrature and remain only as provenance. |
| Repaired SPARC audit and finite-disk scan | Current stiff force tested and found insufficient | All 3391 points use signed gas with disk `M/L=0.5` and bulge `M/L=0.7`. The stiff force gives `chi2/point=371.58`, versus RAR `36.75`, old P6 `414.20`, and baryons `414.23`. A single global `ell` scan runs to its `1e5 kpc` upper boundary under resolution and tail variations, so disk cancellation identifies no finite-scale rescue. Public SPARC lacks gas and vertical density maps for a unique 3D convolution. P6/P5 remain genealogy. |
| Force-residual bridge | Exact empirical diagnostic, not a force prediction | `Delta nu=nu_RAR-(1+sum alpha_stiff)` crosses zero at `gbar=6.25719e-10 m/s^2` and grows toward low acceleration. A fixed positive Yukawa comb has the wrong bounded trend; a new common state-dependent source/coupling is required. |
| Universal signed residual collector | Train-frozen empirical target, not action-derived | One global `g_dagger=1.14414e-10 m/s^2` and no per-galaxy parameters give test `chi2/point=36.75`. The required multiplier spans `1.00033--23.9192` across the sampled galactic domain, while the positive stiff comb is capped at `1.106765`. Neither `R>=0.6 kpc` nor `ell=600 kpc` rescues the stiff force (`390.85` and `371.72`). |
| Nonlinear collector action and HOLO gate | Local mathematical target; current regular linearized HOLO embedding excluded | The reconstructed `F(X)` is single-valued and locally elliptic for nonzero field, with deep limit `(2/3)X^(3/2)` and Newtonian limit `X`, but it is degenerately elliptic at zero. Numerical inversion closes to `3.46e-10` and a spherical Plummer PDE check to `1.26e-5`. The current canonical HOLO response scales as `M`, while the target scales as `sqrt(M)`; regular Yukawa modes and endpoint potentials cannot bridge that mismatch. This does not exclude a new nonperturbative or derivative sector. |
| Axisymmetric collector gate | Controls pass; physical SPARC PDE blocked | The cylindrical Plummer control converges at second order (`L2=2.21e-3`, coarse/fine `4.00`), but a flattened algebraic field has normalized curl `0.0211`. The 175 local tables do not identify `rho(R,z)`, gas surface density, component thicknesses, or boundary data. The `36.75` score is retained as a non-PDE algebraic diagnostic, not a force validation. |
| QCD--galaxy scale consistency | Conditional single-scale no-go, not a measurement | The legacy `1.600006 GeV` proxy implies `ell=3.58248e-17 m`; the saturated SPARC boundary is `1e5 kpc`. Their ratio is `8.61325e40`. The galactic boundary would mean `f0=4.49168e-18 Hz` and `T0=7.05484 Gyr`, but no finite scale was measured. |
| P7 breathing response | Derived conditional space-time transfer, not a detection | The stiff seven-mode force is recovered exactly at `Omega=0`. Below `Omega_n=c mu_n/ell` the response is evanescent; above it an outgoing massive wave has `v_g/c=sqrt(1-(Omega_n/Omega)^2)`. Ratios are `1:4.214303:5.939951:7.533412:9.447842:11.514983:13.636417`. A clock, source occupation, coherence, boundary selection and detector remain unfixed. |
| BOSS DR12 | External comparison with no preference | `chi2_dict=2.266`, `chi2_LCDM=2.443`; the difference is negligible. |
| Suppression near redshift one | Dictionary prediction | Approximately `-12%` at the edge of the mapped trace; it is not generated by the new universal matter coupling, which has the opposite attractive sign. |
| Historical UV/NIST clock arm | Null/poor fit with a coordinate-mixed kernel | Pearson `r=-0.0554`, `chi2/n=22.59`; this does not test the new coordinate-correct bulk-photon response. |

Primary comparison sources: [Cassini](https://doi.org/10.1038/nature01997),
[modern SU(3) glueball continuum calculation](https://arxiv.org/abs/2007.06422),
[Morningstar--Peardon](https://arxiv.org/abs/hep-lat/9901004),
[MICROSCOPE final result](https://doi.org/10.1103/PhysRevLett.129.121102),
and [short-range torsion balance](https://arxiv.org/abs/2002.11761).

## Constraint windows for the compact benchmark

These are point-source recasts, not a global fifth-force likelihood.

- Keeping the exact massless zero mode is not viable without a prospectively
  derived screening mechanism.
- If a new boundary action lifts only that mode, a simple Cassini/LLR recast
  requires roughly `m_0 > 1.33e-14 eV`, or a range below `1.48e7 m`.
- Displaying only the six current positive modes gives a Cassini+LLR envelope
  `ell <~ 2.16e7 m`.  This is diagnostic because a real boundary change can
  alter their masses and couplings as well as the zero mode.
- A conservative short-range benchmark `ell <= 35 micrometre` gives
  `lambda_1 <= 38.3 micrometre` and `m_1 >= 5.15 meV`; the total strength
  `7.2e-5` is far below current unit-strength torsion-balance sensitivity there.

Universal induced-metric coupling preserves weak equivalence for ideal test
bodies.  In the separately declared bulk-photon branch, the scalar lapse now
fixes `d_gamma,n`; it must not be replaced by `beta_n`.  QCD and fermion-mass
coefficients remain unfixed, and the brane-localized Maxwell branch retains the
classical Weyl-invariant null.

## What would be genuinely disruptive

### Near term: correlated scalar--photon double comb

Freeze an explicit boundary/junction action before opening limits, recompute
the entire scalar spectrum, and test a modulated source with a mechanical arm,
a differential-clock arm, and a Coulomb-law arm.  A single `ell` must predict
the scalar falloffs, the photon KK falloffs and all cross-sector mass ratios.
Reserve source distances and one detector species as holdouts.  A recovered
double comb would be much more distinctive than one fitted fifth force.

### Near term: causal breathing comb

Freeze a boundary action and identify one mode frequency from an independent
clock or driven source.  P7 then fixes all other thresholds, relative periods,
static ranges and massive-wave group delays.  The acquisition must last long
enough to resolve the comb and must use independent detectors; coherence
between deliberately phase-linked channels is a control, not evidence.

### Near to medium term: real QCD closure

Implement rectangular 4D SU(3) Wilson loops, a static potential, Creutz/Cornell
cross-checks, volume and lattice-spacing scans, and continuum extrapolation.
Independently freeze a string-frame holographic completion and predict the full
set `0++* / 0++`, `2++ / 0++`, `0-+ / 0++`, and `m/sqrt(sigma)`.  Agreement
without channel-specific retuning would be a real cross-method result.

### Medium term: physical branch matching

A UV completion would have to derive `ell*sqrt(sigma)` or `alpha'/ell^2`.
Only then could the same numerical background connect a QCD Wilson scale and a
compact material range without identifying an RG coordinate with a physical
dimension by hand.

### Longer term: dimensional clocks and gravitational radiation

Fix `ell`, the scalar source/occupation, photon localization and atomic
sensitivity coefficients prospectively.  Then the derived `d_gamma,n` becomes
a dimensional differential-clock template.  A full four-dimensional
cosmological reduction and QCD/fermion anomaly coefficients are still required
for composition dependence or scalar breathing/dipole radiation.

## Three-rung rule

1. Derive and freeze the action, boundary sector, scale rule, and observable
   before reading the target data.
2. Recompute with an independent method: coordinate identity, shooting versus
   finite elements, lattice estimator cross-check, or full elastic FEM versus
   modal transfer.
3. Test a held-out dataset or experimental arm; preserve a null or exclusion
   rather than tuning the interface after seeing it.
