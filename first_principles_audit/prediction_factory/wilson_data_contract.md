# Genuine Wilson-loop data contract

`wilson_loop_analyzer.py` accepts only stored four-dimensional SU(3) link
matrices.  An average plaquette, a plaquette--plaquette correlator, or an
Einstein--dilaton endpoint value is not sufficient to reconstruct a rectangular
Wilson loop.

## Canonical NPZ

The preferred input is an `.npz` file with:

- `links`: complex array shaped
  `[Ncfg,Lx,Ly,Lz,Lt,4,3,3]`, or one configuration shaped
  `[Lx,Ly,Lz,Lt,4,3,3]`;
- `schema="holo.su3-link-ensemble.v1"`;
- `axis_order="config,x,y,z,t,mu,row,col"` (omit `config,` for a single
  configuration);
- `gauge_group="SU(3)"`;
- `boundary_conditions="periodic"`;
- `time_direction=3`;
- for a possible `sigma*a^2` interpretation: `ensemble_id`, `gauge_action`,
  `beta`, `thermalization_sweeps`, and
  `saved_configuration_stride_sweeps`.

`links_real` plus `links_imag` may replace the complex `links` array.  JSON
uses the same metadata and requires the split real/imaginary representation.
An `.npy` array requires a sibling `.npy.meta.json` or `.meta.json` carrying
the metadata above.

Every matrix is checked for finiteness, unitarity, and determinant one.  Inputs
with unknown axis order, boundary conditions, group, or temporal direction are
rejected rather than guessed.

## Outputs and scale boundary

For each stored configuration the analyzer averages

`W(R,T) = Re Tr P product_C U / 3`

over origins and three spatial orientations.  Ensemble means, the effective
potential `aV_eff=log(W(R,T)/W(R,T+1))`, and Creutz ratios are evaluated after
blocking.  Jackknife errors are propagated through the logarithms and ratios.

An estimate labelled `sigma*a^2` is allowed only for an explicitly requested
large-loop window with at least three positive Creutz cells, four jackknife
blocks, complete ensemble provenance, and a stable window.  It remains a
finite-volume, finite-spacing result.  Multiple volumes and bare couplings are
needed for a continuum result.

Conversion uses

`sigma[GeV^2] = (sigma*a^2) * (a^{-1}[GeV])^2`.

The inverse lattice spacing is an independent scale-setting input.  The file
`instrument_closure/2026-01-04/wilson_loop_sigma_from_ed_trace.json` is an ED
endpoint proxy and is explicitly excluded.  A lattice spacing is also not a
physical compactification length: identifying an `ell` requires an additional
theory relation such as `ell*sqrt(sigma)` or `a/ell`.

## Current repository result

Run from the repository root:

```bash
python3 first_principles_audit/prediction_factory/wilson_loop_analyzer.py
```

With the current HK-core and HOLO artifacts this intentionally exits with code
`2` after writing `wilson_data_manifest.json`: the discovered JSON files contain
only observable summaries or the excluded endpoint proxy, not link matrices.
