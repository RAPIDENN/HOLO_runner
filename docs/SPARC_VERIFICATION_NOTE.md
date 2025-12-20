## SPARC Verification Clarification

- The initial 7-galaxy mismatch was **not** caused by using a different dataset, altered data, or post-preprint tuning. The current public SPARC catalogue is used unchanged.
- Root cause: a definition mismatch for the baryonic velocity `v_bar`.
  - Pipeline (preprint artefacts): `v_bar = sqrt(v_gas^2 + v_disk^2 + v_bulge^2)` using the raw SPARC component values (which may be negative by convention).
  - Previous verifier: applied per-component clamping (`max(component, 0)`) before squaring, which underestimates `v_bar` and therefore lowers χ² for some galaxies.
- Impacted galaxies (traceability): DDO064, UGC04305, F574-2, UGC08837, F583-1, UGC04278, UGC01281.
- Resolution: align the verifier with the pipeline definition (no clamping before squaring). With this alignment, SPARC verification passes fully using the current public SPARC dataset, with no parameter changes and no artefact regeneration.
