## SPARC Verification Clarification (superseded historical check)

This note explains why the old artefact was reproduced; it does not validate
that artefact's physical baryonic model.  A later physical-input audit found
that the pipeline itself was wrong: SPARC requires signed gas plus the declared
stellar mass-to-light factors,
`Vbar^2 = Vgas*abs(Vgas) + 0.5*Vdisk^2 + 0.7*Vbulge^2`.  The old unit-weight
unsigned quadrature is retained only for byte-level historical provenance.
See `first_principles_audit/prediction_factory/sparc_physical_audit.json`.

- The initial 7-galaxy mismatch was **not** caused by using a different dataset, altered data, or post-preprint tuning. The current public SPARC catalogue is used unchanged.
- Root cause: a definition mismatch for the baryonic velocity `v_bar`.
  - Pipeline (preprint artefacts): `v_bar = sqrt(v_gas^2 + v_disk^2 + v_bulge^2)` using the raw SPARC component values (which may be negative by convention).
  - Previous verifier: applied per-component clamping (`max(component, 0)`) before squaring, which underestimates `v_bar` and therefore lowers χ² for some galaxies.
- Impacted galaxies (traceability): DDO064, UGC04305, F574-2, UGC08837, F583-1, UGC04278, UGC01281.
- Historical resolution: the verifier was aligned with the pipeline definition
  so the old output could be reproduced.  That reproducibility pass must not be
interpreted as physical validation.  The repaired audit now uses the
canonically normalized seven-mode stiff-boundary force as the current
candidate.  It gives test `chi2/point=371.58`, compared with `414.23` for
baryons and `36.75` for the empirical RAR.  An effective thin-disk Hankel scan
with one global `ell` runs to its `1e5 kpc` upper boundary under all declared
sensitivity checks, so no finite scale is identified.  Public SPARC tables do
not contain the gas surface-density or vertical-density maps needed for a
unique 3D convolution.  P6 and P5 remain rejected numerical genealogy.
An explicit follow-up also rejects both possible readings of the old `600`
statement: `R>=0.6 kpc` leaves the stiff score at `390.85`, and `ell=600 kpc`
leaves it at `371.72`.  A universal train-frozen signed collector reaches
`36.75` with no per-galaxy parameters, but it is the empirical RAR target that
a new action sector must derive, not confirmation of the present force.  The
current regular linearized HOLO sector cannot supply its half-power source
scaling through the existing Yukawa tower or endpoint potentials.  A
cylindrical finite-volume control converges on a spherical benchmark, but the
flattened algebraic shortcut develops curl; the local SPARC tables do not
identify the 3D density and boundary data required for the genuine nonlinear
PDE.  Therefore the `36.75` value remains a non-PDE algebraic diagnostic.
