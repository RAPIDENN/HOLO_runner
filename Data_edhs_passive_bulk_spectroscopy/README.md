# EDHS passive bulk spectroscopy (operator-level) — frozen artifacts

This folder is a **frozen artefact pack** for a numerical note on passive operator-level spectroscopy of a trace-defined Einstein–Dilaton background.

## Contents

- `edhs_passive_bulk_spectroscopy_preprint.pdf` — the preprint PDF.
- `figures/` — frozen figures referenced by the PDF (S1–S8) plus NIST clock validation figures.
- `artifacts/` — supplementary JSON datasets referenced by the PDF.
- Zenodo DOI (this version): [10.5281/zenodo.18109545](https://doi.org/10.5281/zenodo.18109545)

## Figure inventory (frozen)

Supplementary figures (S1–S8):

- `figures/figS1_phaseA_transfer_linear.png`
- `figures/figS2_phaseA_transfer_log.png`
- `figures/figS3_emergent_geometry_profiles.png`
- `figures/figS4_emergent_geometry_weights.png`
- `figures/figS5_constraint_residual.png`
- `figures/figS6_phase_space_phi_vs_A.png`
- `figures/figS7_phaseB_phi0_dphi0_geometry_map.png`
- `figures/figS8_toroidal_screening.png`

Operator-level instrumental validation (NIST clock antenna readout):

- `figures/y_antenna_timeseries_nist_yb.png`
- `figures/y_antenna_fft_nist_yb.png`
- `figures/y_antenna_timeseries_nist_10ghz.png`
- `figures/y_antenna_fft_nist_10ghz.png`

## Dataset inventory (frozen)

- Dataset S1 (JSON): `artifacts/spectrum_response.json`
- Dataset S2 (JSON): `artifacts/datasetS2_phaseB_phi0_dphi0_geometry_map.json`

## Notes

- Only **observables and frozen outputs** are included here (plots + JSON). No internal repository paths, command lines, or solver implementation details are included.
- The datasets are intended to support independent inspection (e.g., reproducing plots from the provided JSON), not to distribute the underlying kernel/solver.
