# Verification bundle (Preprint v3): A single Einstein–Dilaton geometry (QCD, SPARC, growth)

This folder contains **machine-readable verification artifacts** (JSON) supporting the numerical values quoted in the preprint.

Repository: https://github.com/RAPIDENN/HOLO_runner

Zenodo record (DOI): https://doi.org/10.5281/zenodo.18141795 (v3)
Local PDF (v3): `A_single_Einstein-Dilaton_geometry.pdf`

## What is included (v3, paper-aligned)

## Preprint

- `A_single_Einstein-Dilaton_geometry.pdf` — manuscript PDF (paper-aligned “v3”; verification lives in the JSON artifacts below).

## Figures (exactly those used by the PDF)

All figures are copied verbatim from the paper build directory and correspond 1:1 to `\includegraphics{...}` entries in the LaTeX.

- `figures/glueball_ratio.png`
- `figures/sparc_rotation_curves_forward.png`
- `figures/multiarm_svd_diagnostic.png`
- `figures/fig_spectroscopy.pdf`
- `figures/fig_single_arm_modal_responses.pdf`
- `figures/bulk_clock_5d.png`
- `figures/nist_baseline_vs_uv.png`

## Instrument closure (bulk clock + UV-screened lab channel)

This bundle includes the frozen instrument-closure artifacts used by the paper:

- `artifacts/ed_bulk_clock.json`
- `artifacts/tau_from_dictionary.json`
- `artifacts/k_em_uv_projector.json`
- `artifacts/em_uv_projected.json`
- `artifacts/nist_comparison_naive.json`
- `artifacts/nist_comparison_uv.json`

### Third-party data policy (NIST)

The NIST comparison JSONs intentionally **do not** ship the observed time series values.

- Removed fields: `series.y_obs` and `series.resid`
- Retained: predicted series (`y_pred`) and summary metrics

This keeps the manuscript figure as published while avoiding redistribution of third-party observational samples.

## Artifacts

- `artifacts/invariant_flux_spectrum_u.json` — gauge-invariant scalar 0⁺⁺ spectrum readout (u coordinate); includes the reported ratio m₁/m₀.
- `artifacts/growth_report.json` — linear-growth readout fσ8(z) computed from the frozen ED trace and matched ΛCDM reference.
- `artifacts/growth_validation_boss_dr12.json` — BOSS DR12 covariance-weighted χ² comparison vs ΛCDM.
- `artifacts/yang_mills_scale_report.json` — Wilson-loop string-tension estimate and implied absolute glueball mass scale under a universal α′.
- `artifacts/desi_residual.json` — versioned residual vector Δfσ8(z_bins) used by the paper.
- `artifacts/bulk_eigenmodes_derived.json` — certified bulk eigenmode basis (ψₙ on the solver grid).
- `artifacts/reconstructed_mode_delta_G_desi_nontoy.json` — non-toy bounded single-arm reconstruction artifact underlying the dynamic spectroscopy figure.
- `artifacts/multi_arm_response_bundle_v2.json` — multi-arm response bundle (diagnostic aggregation; no inversion).
- `artifacts/multiarm_svd_diagnostic.json` — multi-arm SVD diagnostic output (diagnostic only).
- `artifacts/response_operator_R_*_nontoy.json` — frozen non-toy single-arm response operators (G/S/D/ζ/L) used by the diagnostics and reconstructions.



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

## Verification (local)

From the repo root `HOLO_runner/`:

```bash
python3 tools/verify_bulk_clock_5d.py
python3 tools/verify_uv_screened_nist_channel.py
```

## JSON sanitized
