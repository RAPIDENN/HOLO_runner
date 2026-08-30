# First-principles Einstein--dilaton audit

This directory is a clean derivation and adjudication layer for the HOLO
Einstein--dilaton programme.  It does not treat an existing manuscript, kernel,
or frozen JSON value as an answer key.

The workflow has three deliberately separated stages:

1. **Derive and seal.**  Start from the declared five-dimensional action, fix
   the gauge and signs, derive the field equations, and generate an exact
   reference solution.  Acceptance criteria are fixed in
   [`PREREGISTRATION.md`](PREREGISTRATION.md) before comparison.
2. **Compare.**  Evaluate the frozen HOLO trace and analytic reconstruction
   against the sealed equations.  Existing values are inputs to be tested, not
   targets to reproduce.
3. **Adjudicate independently.**  Check the result with a second formulation:
   an exact superpotential flow, a separate numerical integrator, and the
   domain-wall/conformal-coordinate transformation.

The intended output is not a blanket pass/fail for HOLO.  Every claim is
classified as one of:

- `derived`: follows from the declared action and stated assumptions;
- `numerical`: a reproducible consequence of a derived system;
- `phenomenological`: a declared readout or calibrated mapping;
- `unsupported`: the present evidence does not establish the claim;
- `inconsistent`: incompatible equations, conventions, or provenance were
  found.

Run the audit from the `HOLO_runner` root:

```bash
python3 first_principles_audit/derive_and_audit.py
python3 -m unittest first_principles_audit.test_derive_and_audit -v
```

Generated machine-readable results are written to
`first_principles_audit/artifacts/ed_audit.json`.

The scientific interpretation is developed in
[`MANUSCRIPT.md`](MANUSCRIPT.md).  It reports the exact solution as a positive
result while keeping the existing cross-domain readouts as explicitly
phenomenological material rather than promoting them to consequences of the
five-dimensional action.

The follow-up [`EFFECTIVE_RECONSTRUCTION.md`](EFFECTIVE_RECONSTRUCTION.md)
does not replace the HOLO geometry.  It preserves its warp and scalar profiles
and reconstructs the positive non-canonical kinetic function and potential
that make those profiles a solution on the frozen radial interval:

```bash
python3 first_principles_audit/reconstruct_holo_effective_action.py
python3 -m unittest first_principles_audit.test_effective_reconstruction -v
```

The next blind stage derives the healthy gauge-invariant scalar carrier and
separates it from the boundary and matter coefficients that the geometry does
not fix.  Its gates are frozen in
[`INTERFACE_PREREGISTRATION.md`](INTERFACE_PREREGISTRATION.md), and the 4D
interface equations and evidence boundary are documented in
[`INTERFACE_ACTION.md`](INTERFACE_ACTION.md):

```bash
python3 first_principles_audit/derive_interface_action.py
python3 -m unittest first_principles_audit.test_interface_action -v
```

The upstream and historical repositories are classified in
[`REPOSITORY_PROVENANCE_AUDIT.md`](REPOSITORY_PROVENANCE_AUDIT.md).  In
particular, exact trace reproduction, the inverse effective completion,
historical fitted couplings, and the independent lattice-gauge engine are kept
as four distinct evidence layers.

One explicitly conditional physical realization is then frozen in
[`MINIMAL_PROBE_COMPLETION.md`](MINIMAL_PROBE_COMPLETION.md).  It treats the
finite radial domain as a compact interval, normalizes the gravity--scalar
trace modes, and derives their probe-matter coupling without importing the
historical SPARC-fitted DOF1 parameters:

```bash
python3 first_principles_audit/derive_minimal_probe_completion.py
python3 -m unittest first_principles_audit.test_minimal_probe_completion -v
```

The spectrum and UV coupling are then recomputed by an independent continuous
ODE shooting method that does not import or reuse the finite-element matrices:

```bash
python3 first_principles_audit/verify_minimal_probe_completion_shooting.py
python3 -m unittest first_principles_audit.test_minimal_probe_completion_shooting -v
```

The Ricci/Wilson provenance layer and the usable, scale-free part of a material
transducer are audited separately.  This stage corrects the derivative used by
the historical 5D curvature artefact, identifies the historical Wilson value
as an endpoint proxy rather than an area-law measurement, and derives the
correlated Yukawa acceleration/tidal templates without choosing a target
frequency or detector:

```bash
python3 first_principles_audit/audit_ricci_wilson_interface.py
python3 first_principles_audit/derive_material_transducer.py
python3 -m unittest \
  first_principles_audit.test_ricci_wilson_interface \
  first_principles_audit.test_material_transducer -v
```

The equations, physical-branch fork, and non-double-counting rule are recorded
in [`RICCI_WILSON_MATERIAL_INTERFACE.md`](RICCI_WILSON_MATERIAL_INTERFACE.md).
The resulting separation between excluded, conditional, diagnostic, and
genuinely forward targets is summarized in
[`PREDICTION_LEDGER.md`](PREDICTION_LEDGER.md).

The executable follow-up is the
[`prediction_factory/`](prediction_factory/) directory.  It adds a complete
boundary-condition branch audit, an independent shooting check of the
ultralight ND mode, a frozen dimensionless material fingerprint, an
action-level completion of the historical Eq. 39 electromagnetic kernel, a
fail-closed Wilson-loop pipeline, a microscopic superpotential boundary audit,
a canonically normalized seven-mode stiff force, a repaired SPARC baryonic-
input audit and geometry-matched finite-disk scan (P6/P5 are genealogy only),
a universal signed-residual collector that rejects both interpretations of the
old `600` threshold while remaining explicitly empirical,
a locally elliptic but zero-field-degenerate nonlinear action reconstruction,
an executable no-go gate for embedding it in the current regular linearized
HOLO sector, a real-background BPS moduli/matter-metric certificate resolving
two physical endpoint moduli and their covariant selector jets (while no
physical tangent or `q^2Y` matter operator is selected), a fixed-warped-volume
candidate that nearly aligns one tangent but fails exact alignment and the
minimal matter-sign test, and
axisymmetric controls that fail closed on missing 3D SPARC
source and boundary data,
a P7 space--time breathing response that recovers the stiff force at zero frequency,
and a published-DESI marginal diagnostic.  P7 derives the correlated scalar
thresholds, evanescent-to-propagating transition and causal timing without
assigning an observational frequency, source occupation or detector signal. Their
physical dependencies and missing
links are collected in
[`MASTER_PREDICTION_REGISTRY.md`](prediction_factory/MASTER_PREDICTION_REGISTRY.md).
