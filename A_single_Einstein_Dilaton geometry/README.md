# Verification bundle: A single Einstein–Dilaton geometry (QCD, SPARC, growth)

This folder contains **machine-readable verification artifacts** (JSON) supporting the numerical values quoted in the preprint.

Repository: https://github.com/RAPIDENN/HOLO_runner

Zenodo record (DOI): https://doi.org/10.5281/zenodo.18086173  
Local PDF: `A_single_Einstein-Dilaton_geometry.pdf`

## What is included

## Preprint

- `A_single_Einstein-Dilaton_geometry.pdf` — manuscript PDF (scientific document; verification lives in the JSON artifacts below).

## Instrument closure (bulk clock + UV-screened lab channel)

This bundle also includes the frozen ``instrument closure'' additions:

- 5D Ricci bulk clock artifact:
  - `artifacts/ed_bulk_clock.json`
  - Figure: `figures/bulk_clock_5d.png`
- Frozen time-mapping dictionary artifact:
  - `artifacts/tau_from_dictionary.json`
- UV-screened EM/lab readout artifacts (verification only):
  - `artifacts/k_em_uv_projector.json`
  - `artifacts/em_uv_projected.json`
  - `artifacts/nist_comparison_naive.json`
  - `artifacts/nist_comparison_uv.json`
  - Figure: `figures/nist_baseline_vs_uv.png`

The key point is separation: bulk eigenmodes are geometric observables, while laboratory clocks are tested as UV-projected drift/readout series.

## Artifacts

- `artifacts/invariant_flux_spectrum_u.json` — gauge-invariant scalar 0⁺⁺ spectrum readout (u coordinate); includes the reported ratio m₁/m₀.
- `artifacts/growth_report.json` — linear-growth readout fσ8(z) computed from the frozen ED trace and matched ΛCDM reference.
- `artifacts/growth_validation_boss_dr12.json` — BOSS DR12 covariance-weighted χ² comparison vs ΛCDM.
- `artifacts/yang_mills_scale_report.json` — Wilson-loop string-tension estimate and implied absolute glueball mass scale under a universal α′.



### `artifacts/invariant_flux_spectrum_u.json`
- Verifies the **gauge-invariant scalar 0⁺⁺ spectrum readout** on the frozen background.
- Contains `ratio_m1_over_m0` used in the text/figure.

### `artifacts/growth_report.json`
- Verifies the **linear growth** reconstruction and the fσ8(z) series used for plotting.
- Includes `z_max_used` and confirms the plotted domain was fully covered by the trace.

### `artifacts/growth_validation_boss_dr12.json`
- Verifies the **BOSS DR12** covariance-weighted χ² calculation for the quoted redshifts.

### `artifacts/yang_mills_scale_report.json`
- Verifies the **Wilson-loop string-tension estimate** from the IR warp factor and the implied absolute mass scale.
- Uses the convention stated in the preprint: σ_eff = exp(2A(z_*)) / (2π α′).

## Manifest

See `MANIFEST.md` for an explicit list of the figures and artifacts included in this folder.

## Verification (local)

From the repo root `HOLO_runner/`:

```bash
python3 tools/verify_bulk_clock_5d.py
python3 tools/verify_uv_screened_nist_channel.py
```

## JSON sanitized
