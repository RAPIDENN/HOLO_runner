## Reproducibility Notes

- SPARC dataset: The preprint used an earlier snapshot of SPARC (175 galaxies) that is not available on this machine. The current repo uses the public SPARC dataset converted from the original `*_rotmod.dat` files to CSV (under `data/external/SPARC/sparc_175` in the source projects).
- Artefacts:
  - `data/internal/sparc_p5_current.json` — regenerated with SPARC-current, same pipeline/parameters as the preprint.
  - `data/internal/sparc_p5_preprint_frozen.json` — legacy artefact from the preprint snapshot.
- Expected differences: the historical verifier reproduces its frozen artefact,
  but those HOLO/Newton counts are no longer current scientific results.  The
  physical-input audit recomputes signed gas and stellar mass-to-light factors.
  The current seven-mode stiff-boundary force is evaluated both in its exact
  long-range limit and with an effective axisymmetric finite-disk Hankel scan;
  the latter selects only the upper `ell` boundary.  P6 and P5 are retained as
  historical numerical genealogy, not as the current physical curve.
  The nonlinear collector is now separately gated: its local action is
  zero-field-degenerate, the current regular linearized HOLO sector fails the
  `M` versus `sqrt(M)` embedding test, and a physical axisymmetric SPARC solve
  is blocked because the local tables do not identify the required 3D density,
  thicknesses, and PDE boundary conditions.
- `run_repro.py` defaults to SPARC-current; use `--mode preprint` to verify against the frozen preprint artefact.
- SPARC verification note: the earlier 7-galaxy mismatch concerned historical
  byte-level reproduction.  The pipeline's unit-weight unsigned baryonic
  construction was subsequently found to be physically wrong; see
  `docs/SPARC_VERIFICATION_NOTE.md` and the repaired audit for details.
