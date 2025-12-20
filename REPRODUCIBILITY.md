## Reproducibility Notes

- SPARC dataset: The preprint used an earlier snapshot of SPARC (175 galaxies) that is not available on this machine. The current repo uses the public SPARC dataset converted from the original `*_rotmod.dat` files to CSV (under `data/external/SPARC/sparc_175` in the source projects).
- Artefacts:
  - `data/internal/sparc_p5_current.json` — regenerated with SPARC-current, same pipeline/parameters as the preprint.
  - `data/internal/sparc_p5_preprint_frozen.json` — legacy artefact from the preprint snapshot.
- Expected differences: With SPARC-current, 7/175 galaxies show small χ² shifts versus the preprint snapshot, but overall HOLO > Newton counts and conclusions are unchanged.
- `run_repro.py` defaults to SPARC-current; use `--mode preprint` to verify against the frozen preprint artefact.
- SPARC verification note: the earlier 7-galaxy mismatch was due to a baryonic-velocity definition mismatch (pipeline uses raw components squared; the verifier previously clamped each component before squaring). The verifier is now aligned; see `docs/SPARC_VERIFICATION_NOTE.md` for details.
