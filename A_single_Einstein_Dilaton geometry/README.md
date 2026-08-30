# Verification bundle: A single Einstein–Dilaton geometry (QCD, SPARC, growth)

This folder contains **machine-readable verification artifacts** (JSON) supporting the numerical values quoted in the preprint.

Repository: https://github.com/RAPIDENN/HOLO_runner

Zenodo record (DOI): https://doi.org/10.5281/zenodo.18224589
Local PDF: `A_single_Einstein-Dilaton_geometry.pdf`

## What is included (paper-aligned)

## Preprint

- `A_single_Einstein-Dilaton_geometry.pdf` — manuscript PDF (paper-aligned; verification lives in the JSON artifacts below).

## Figures (exactly those used by the PDF)

All figures are copied verbatim from the paper build directory and correspond 1:1 to `\includegraphics{...}` entries in the LaTeX.

- `figures/glueball_ratio.png`
- `figures/fig_sparc_physical_audit.png`
- `figures/fig_nonlinear_collector_action.png`
- `figures/multiarm_svd_diagnostic.png`
- `figures/fig_spectroscopy.pdf`
- `figures/fig_single_arm_modal_responses.pdf`
- `figures/bulk_clock_5d.png`
- `figures/nist_baseline_vs_uv.png`
- `figures/fig_effective_reconstruction.png`
- `figures/fig_minimal_probe_completion.png`
- `figures/fig_ricci_material_audit.png`
- `figures/fig_prediction_factory.png`
- `figures/fig_em_double_comb.png`

## Historical instrument-closure artefacts

This bundle includes the frozen historical artefacts audited by the paper.  The
legacy Ricci series used a mislabeled radial derivative, and the laboratory
kernel mixed the domain-wall trace coordinate with the conformal Maxwell
density.  It is retained for provenance and superseded by the coordinate-correct
bulk-photon certificate:

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
- `artifacts/yang_mills_scale_report.json` — Einstein-frame IR-endpoint proxy and implied absolute glueball mass after external choices of α′ and scalar conversion factor; it is not a measured Wilson area law.
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
- Verifies the arithmetic of the historical **IR-endpoint scale proxy** and its implied absolute mass conversion.
- Uses σ_proxy = exp(2A(z_end)) / (2π α′), with external α′; no rectangular Wilson loop or world-sheet calculation is contained in the artefact.

## Verification (local)

From the repo root `HOLO_runner/`:

```bash
python3 tools/verify_bulk_clock_5d.py
python3 tools/verify_uv_screened_nist_channel.py
python3 first_principles_audit/audit_ricci_wilson_interface.py
python3 first_principles_audit/derive_material_transducer.py
python3 first_principles_audit/prediction_factory/derive_boundary_branches.py
python3 first_principles_audit/prediction_factory/verify_nd_ultralight_shooting.py
python3 first_principles_audit/prediction_factory/derive_em_kernel_completion.py
python3 first_principles_audit/prediction_factory/derive_robin_boundary_family.py
python3 first_principles_audit/prediction_factory/derive_em_spectral_fingerprint.py
python3 first_principles_audit/prediction_factory/evaluate_desi_dr1_growth.py
python3 first_principles_audit/prediction_factory/derive_sparc_finite_disk_yukawa.py
python3 first_principles_audit/prediction_factory/sparc_physical_audit.py
python3 first_principles_audit/prediction_factory/derive_force_residual_bridge.py
python3 first_principles_audit/prediction_factory/derive_universal_residual_collector.py
python3 first_principles_audit/prediction_factory/derive_nonlinear_collector_action.py
python3 first_principles_audit/prediction_factory/derive_holo_collector_embedding_gate.py
python3 first_principles_audit/prediction_factory/derive_axisymmetric_collector_prototype.py
python3 first_principles_audit/prediction_factory/derive_scale_consistency.py
python3 first_principles_audit/prediction_factory/build_master_prediction_registry.py
```

The prediction factory is indexed by
[`MASTER_PREDICTION_REGISTRY.md`](../first_principles_audit/prediction_factory/MASTER_PREDICTION_REGISTRY.md).
It includes the four endpoint branches, the positive Robin phase map, the
scale-free material fingerprint, the coordinate-correct Eq. 39 completion, the
conditional scalar--photon double comb and photon KK tower, the fail-closed
Wilson-loop input audit, the repaired SPARC physical-input audit, and the DESI
DR1 marginal diagnostic.  The current action-derived galaxy candidate is the
seven-mode stiff-boundary force; P6 and P5 are retained only as genealogy.  Its
finite-disk scan reaches the long-range boundary, and neither `R>=0.6 kpc` nor
`ell=600 kpc` rescues it.  The universal signed collector identifies the
missing response without per-galaxy parameters, but is the empirical RAR
target rather than a HOLO prediction.  The current canonical linearized sector
fails the `M` versus `sqrt(M)` embedding gate, while a cylindrical control shows
that the flattened algebraic shortcut has curl and is not an AQUAL solution.
The physical SPARC PDE remains blocked by non-unique 3D source and boundary
inputs.  None is labelled a new detection or a clean confirmatory holdout.

## JSON sanitized
