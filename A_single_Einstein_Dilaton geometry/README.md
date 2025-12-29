# Verification bundle: A single Einstein–Dilaton geometry (QCD, SPARC, growth)

This folder contains **machine-readable verification artifacts** (JSON) supporting the numerical values quoted in the preprint.

Repository: https://github.com/RAPIDENN/HOLO_runner

Zenodo record (DOI): https://doi.org/10.5281/zenodo.18086173  
Local PDF: `A_single_Einstein-Dilaton_geometry.pdf`

## What is included

## Preprint

- `A_single_Einstein-Dilaton_geometry.pdf` — manuscript PDF (scientific document; verification lives in the JSON artifacts below).

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

## JSON sanitized 
