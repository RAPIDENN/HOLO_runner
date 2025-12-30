# Manifest (verification bundle map)

This document maps the included manuscript PDF to the machine-readable artifacts and figures shipped in this folder.

All paths are relative to `A_single_Einstein_Dilaton geometry/`.

## Manuscript

- `A_single_Einstein-Dilaton_geometry.pdf`

## Figures

- `figures/bulk_clock_5d.png` (5D Ricci bulk clock: `A(z)`, `R5(z)`, `dt_phys/dt_ref`)
- `figures/nist_baseline_vs_uv.png` (NIST comparison: naive vs UV-screened channel)

## Machine-readable artifacts (JSON)

Core (QCD / SPARC / growth):
- `artifacts/invariant_flux_spectrum_u.json`
- `artifacts/covariant_invariance_proof.json`
- `artifacts/sparc_forward_eval.json`
- `artifacts/growth_report.json`
- `artifacts/growth_validation_boss_dr12.json`
- `artifacts/yang_mills_scale_report.json`

Bulk clock + time mapping (instrument closure):
- `artifacts/ed_bulk_clock.json`
- `artifacts/tau_from_dictionary.json`

Laboratory UV-screened readout (verification; no code):
- `artifacts/k_em_uv_projector.json`
- `artifacts/em_uv_projected.json`
- `artifacts/nist_comparison_naive.json`
- `artifacts/nist_comparison_uv.json`

## Verification scripts (local)

From the repo root `HOLO_runner/`:

- `python3 tools/verify_bulk_clock_5d.py`
- `python3 tools/verify_uv_screened_nist_channel.py`

