# Reproducibility (Verification Only)

This pack provides verification of the preprint results via public data
and frozen artefacts. It does **not** regenerate the solver output.

## Observational inputs
- SPARC 175 galaxy rotation curves (public `*_rotmod.csv` files).
- Bullet Cluster observational summary.
- Planck 2018 cosmological parameters (used via frozen summary JSON).

## Frozen artefacts
Located in `data/internal/` and `figures/`.
- SPARC summaries (current & legacy): `sparc_p5_current.json`, `sparc_p5_preprint_frozen.json`, `sparc_predictive.json`, `ed_fixed_ic_sparc_eval.json`
- Early SPARC mismatches were resolved by aligning the verification metric with the pipeline definition of baryonic velocity.
- Ricci lock: `lock5_ricci_results.json`
- Bullet Cluster: `bullet_cluster_ed.json`
- Additional tables: `ed_vs_mond_eval.json`
- Figures: see `repro/traceability_table.md`

## Verification scripts
Located in `tools/`:
- `verify_sparc_metrics.py` (requires `--sparc-dir`) – recomputes Newton baseline from public CSVs and checks the frozen JSON.
- `verify_lock5_ricci.py` – checks the Ricci lock summary JSON.
- `verify_cosmo_summary.py` – checks cosmology robustness JSON.
- `verify_bullet_cluster.py` – checks Bullet Cluster JSON + figure.

The entry point `run_repro.py` runs all verifications.

## Traceability
See `repro/traceability_table.md` for the mapping from paper sections/figures to the artefacts provided here.
