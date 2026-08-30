#!/usr/bin/env python3
"""Apply the stiff scalar comb to SPARC with an axisymmetric disk operator.

The public SPARC mass-model tables provide Newtonian component rotation
curves, but not the gas surface-density map or a three-dimensional baryonic
density for every galaxy.  Consequently the unique extended-source Yukawa
convolution is not identifiable from those tables alone.  This certificate
performs the strongest controlled check available from the public curves: it
interprets the repaired ``Vbar**2`` profile as the radial field of an
effective razor-thin axisymmetric disk and applies the Yukawa transfer in
Hankel space.

For a thin disk, with ``a(R)=R*g_N(R)=Vbar**2(R)``, the order-one Hankel
transform is multiplied by

    T(k;m) = k / sqrt(k**2 + m**2)

for each Yukawa mode.  The complete stiff candidate therefore has spectral
transfer ``1 + sum(alpha_n*T(k;mu_n/ell))``.  A single global ``ell`` is
selected on the frozen training galaxies; there are no per-galaxy force
parameters.  Validation and test galaxies are evaluated without refitting.

This is a retrospective feasibility/shape test, not a detection.  Finite
radial coverage requires explicit inner and outer extrapolations, which are
varied below as a sensitivity check.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import scipy
from scipy.fft import fht, fhtoffset, ifht
from scipy.interpolate import PchipInterpolator

try:
    from first_principles_audit.prediction_factory import sparc_crossval as legacy
    from first_principles_audit.prediction_factory import sparc_physical_audit as audit
except ModuleNotFoundError:  # direct execution from this directory
    import sparc_crossval as legacy
    import sparc_physical_audit as audit


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "sparc_finite_disk_yukawa.json"
SPLIT_PATH = HERE / "sparc_split_v1.json"
STIFF_PATH = HERE / "artifacts" / "stiff_boundary_force.json"
ELL_GRID_KPC = np.logspace(-3.0, 5.0, 81)


@dataclass(frozen=True)
class DiskOperatorConfig:
    name: str
    samples: int = 1024
    padding_factor: float = 1.0e3
    inner_v2_power: float = 2.0
    outer_v2_power: float = -1.0

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "name": self.name,
            "samples": self.samples,
            "padding_factor": self.padding_factor,
            "inner_v2_power": self.inner_v2_power,
            "outer_v2_power": self.outer_v2_power,
        }


BASELINE = DiskOperatorConfig("baseline")
SENSITIVITY_CONFIGS = (
    DiskOperatorConfig("high_resolution", samples=2048, padding_factor=1.0e4),
    DiskOperatorConfig("shallower_outer_tail", outer_v2_power=-0.5),
    DiskOperatorConfig("steeper_outer_tail", outer_v2_power=-1.5),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _validate_config(config: DiskOperatorConfig) -> None:
    if config.samples < 128 or config.samples % 2:
        raise ValueError("FFTLog samples must be an even integer >=128")
    if not math.isfinite(config.padding_factor) or config.padding_factor <= 10.0:
        raise ValueError("padding_factor must be finite and greater than ten")
    if not all(
        math.isfinite(value)
        for value in (config.inner_v2_power, config.outer_v2_power)
    ):
        raise ValueError("extrapolation powers must be finite")


def extended_v2_profile(
    radius_kpc: np.ndarray,
    v2_kms2: np.ndarray,
    config: DiskOperatorConfig = BASELINE,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a positive, padded log-grid representation of ``Vbar**2``."""

    _validate_config(config)
    radius = np.asarray(radius_kpc, dtype=float)
    v2 = np.asarray(v2_kms2, dtype=float)
    if not (
        radius.ndim == v2.ndim == 1
        and radius.size == v2.size >= 3
        and np.all(np.isfinite(radius))
        and np.all(np.isfinite(v2))
        and np.all(radius > 0.0)
        and np.all(np.diff(radius) > 0.0)
        and np.all(v2 >= 0.0)
    ):
        raise ValueError("invalid radial Vbar-squared profile")

    grid = np.geomspace(
        radius[0] / config.padding_factor,
        radius[-1] * config.padding_factor,
        config.samples,
    )
    log_grid = np.log(grid)
    log_radius = np.log(radius)
    values = np.empty_like(grid)
    interior = (grid >= radius[0]) & (grid <= radius[-1])
    interpolator = PchipInterpolator(log_radius, v2, extrapolate=False)
    values[interior] = interpolator(log_grid[interior])
    lower = grid < radius[0]
    upper = grid > radius[-1]
    values[lower] = v2[0] * np.power(
        grid[lower] / radius[0], config.inner_v2_power
    )
    values[upper] = v2[-1] * np.power(
        grid[upper] / radius[-1], config.outer_v2_power
    )
    # PCHIP may undershoot by roundoff near a tabulated zero.  The repaired
    # baryonic contract defines the inward profile as max(Vbar2, 0).
    return grid, np.maximum(values, 0.0)


def stiff_disk_velocity_curves(
    galaxy: legacy.Galaxy,
    ell_kpc: np.ndarray,
    masses_mu: np.ndarray,
    strengths_alpha: np.ndarray,
    config: DiskOperatorConfig = BASELINE,
) -> tuple[np.ndarray, dict[str, float]]:
    """Return geometry-matched stiff predictions for all requested scales."""

    ell = np.asarray(ell_kpc, dtype=float)
    masses = np.asarray(masses_mu, dtype=float)
    strengths = np.asarray(strengths_alpha, dtype=float)
    if not (
        ell.ndim == masses.ndim == strengths.ndim == 1
        and ell.size > 0
        and masses.size == strengths.size > 0
        and np.all(np.isfinite(ell))
        and np.all(ell > 0.0)
        and np.all(np.isfinite(masses))
        and np.all(masses > 0.0)
        and np.all(np.isfinite(strengths))
        and np.all(strengths > 0.0)
    ):
        raise ValueError("invalid scale or stiff mode table")

    observed_radius = np.asarray(galaxy.radius_kpc, dtype=float)
    observed_v2 = np.square(np.asarray(galaxy.v_bary_kms, dtype=float))
    radius, v2 = extended_v2_profile(observed_radius, observed_v2, config)
    log_radius = np.log(radius)
    dln = float(log_radius[1] - log_radius[0])
    offset = float(fhtoffset(dln, mu=1.0, initial=0.0, bias=0.0))
    wave_number = np.exp(offset) / radius[::-1]
    transformed = fht(v2, dln, mu=1.0, offset=offset, bias=0.0)

    mass_kpc_inverse = masses[None, :, None] / ell[:, None, None]
    k = wave_number[None, None, :]
    yukawa_transfer = np.sum(
        strengths[None, :, None]
        * k
        / np.sqrt(np.square(k) + np.square(mass_kpc_inverse)),
        axis=1,
    )
    correction_v2_grid = ifht(
        transformed[None, :] * yukawa_transfer,
        dln,
        mu=1.0,
        offset=offset,
        bias=0.0,
    )
    correction_v2 = np.asarray(
        PchipInterpolator(
            log_radius, correction_v2_grid, axis=-1, extrapolate=False
        )(np.log(observed_radius))
    )
    identity_grid = ifht(
        transformed, dln, mu=1.0, offset=offset, bias=0.0
    )
    identity_observed = np.asarray(
        PchipInterpolator(
            log_radius, identity_grid, extrapolate=False
        )(np.log(observed_radius))
    )
    positive_source = observed_v2 > 0.0
    interpolation_calibration = np.ones_like(observed_v2)
    interpolation_calibration[positive_source] = (
        observed_v2[positive_source] / identity_observed[positive_source]
    )
    correction_v2[:, positive_source] *= interpolation_calibration[
        None, positive_source
    ]
    # Keep the tabulated Newtonian term exact and interpolate only the Yukawa
    # correction.  This prevents the dense-grid interpolation itself from
    # changing the published baryonic curve.
    prediction_v2 = observed_v2[None, :] + correction_v2

    identity_error = float(
        np.max(np.abs(identity_grid - v2)) / max(float(np.max(v2)), 1.0e-12)
    )
    minimum_total_v2 = float(np.min(prediction_v2))
    negative_at_positive_source = int(
        np.sum((prediction_v2 < -1.0e-8) & (observed_v2[None, :] > 0.0))
    )
    curves = np.sqrt(np.maximum(prediction_v2, 0.0))
    return curves, {
        "maximum_fractional_newtonian_identity_error": identity_error,
        "minimum_predicted_v2_km2_s2": minimum_total_v2,
        "negative_predictions_at_positive_source_points": (
            negative_at_positive_source
        ),
        "maximum_fractional_interpolation_calibration": float(
            np.max(np.abs(interpolation_calibration - 1.0))
        ),
    }


def _scan_config(
    groups: Mapping[str, Sequence[legacy.Galaxy]],
    masses: np.ndarray,
    strengths: np.ndarray,
    config: DiskOperatorConfig,
) -> tuple[dict[str, Any], dict[str, dict[str, np.ndarray]]]:
    cache: dict[str, dict[str, np.ndarray]] = {}
    train_chi2 = np.zeros(ELL_GRID_KPC.size)
    train_points = 0
    max_identity_error = 0.0
    minimum_v2 = math.inf
    negative_at_positive_source = 0
    max_interpolation_calibration = 0.0
    for group, galaxies in groups.items():
        cache[group] = {}
        for galaxy in galaxies:
            curves, diagnostics = stiff_disk_velocity_curves(
                galaxy, ELL_GRID_KPC, masses, strengths, config
            )
            cache[group][galaxy.name] = curves
            max_identity_error = max(
                max_identity_error,
                diagnostics["maximum_fractional_newtonian_identity_error"],
            )
            minimum_v2 = min(
                minimum_v2, diagnostics["minimum_predicted_v2_km2_s2"]
            )
            negative_at_positive_source += diagnostics[
                "negative_predictions_at_positive_source_points"
            ]
            max_interpolation_calibration = max(
                max_interpolation_calibration,
                diagnostics["maximum_fractional_interpolation_calibration"],
            )
            if group == "train":
                train_chi2 += np.sum(
                    np.square(
                        (curves - galaxy.v_obs_kms[None, :])
                        / galaxy.sigma_v_kms[None, :]
                    ),
                    axis=1,
                )
                train_points += galaxy.points

    best_index = int(np.argmin(train_chi2))
    finite_differences = np.diff(train_chi2)
    report = {
        "config": config.as_dict(),
        "train_velocity_points": train_points,
        "ell_grid_kpc": ELL_GRID_KPC.tolist(),
        "train_chi2_per_point": (train_chi2 / train_points).tolist(),
        "best_grid_index": best_index,
        "best_ell_kpc": float(ELL_GRID_KPC[best_index]),
        "best_at_upper_boundary": best_index == ELL_GRID_KPC.size - 1,
        "train_objective_nonincreasing_with_ell": bool(
            np.all(finite_differences <= 1.0e-9 * np.maximum(train_chi2[:-1], 1.0))
        ),
        "maximum_fractional_newtonian_identity_error": max_identity_error,
        "minimum_predicted_v2_km2_s2": minimum_v2,
        "negative_predictions_at_positive_source_points": (
            negative_at_positive_source
        ),
        "maximum_fractional_interpolation_calibration": (
            max_interpolation_calibration
        ),
    }
    return report, cache


def _metrics_for_frozen_index(
    galaxies: Sequence[legacy.Galaxy],
    cache: Mapping[str, np.ndarray],
    index: int,
) -> dict[str, float | int]:
    return audit._model_metrics(
        galaxies, lambda galaxy: cache[galaxy.name][index]
    )[0]


def _bulgeless_names(data_dir: Path) -> set[str]:
    names: set[str] = set()
    for path in sorted(data_dir.glob("*_rotmod.csv")):
        _, _, bulge = audit._component_arrays(path)
        if np.all(bulge == 0.0):
            names.add(path.name.removesuffix("_rotmod.csv"))
    return names


def build() -> dict[str, Any]:
    data_dir = legacy.default_sparc_dir()
    groups, split = audit.load_groups(
        data_dir, SPLIT_PATH, legacy.default_trace_path()
    )
    stiff = _read(STIFF_PATH)
    if stiff.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff boundary force certificate does not pass")
    if stiff.get("observational_inputs_read") != []:
        raise RuntimeError("stiff boundary force must be observation-free")
    force = stiff["spectrum_and_force"]
    masses = np.asarray(force["masses_mu"], dtype=float)
    strengths = np.asarray(force["alpha_uv_2_beta_squared"], dtype=float)

    baseline, baseline_cache = _scan_config(
        groups, masses, strengths, BASELINE
    )
    best_index = int(baseline["best_grid_index"])
    baseline_metrics = {
        group: _metrics_for_frozen_index(
            galaxies, baseline_cache[group], best_index
        )
        for group, galaxies in groups.items()
    }

    sensitivity = []
    for config in SENSITIVITY_CONFIGS:
        scan, _ = _scan_config(groups, masses, strengths, config)
        # The curve arrays are deliberately not serialized.
        sensitivity.append(scan)

    alpha_sum = float(np.sum(strengths))
    exact_long_range_metrics = {
        group: audit._model_metrics(
            galaxies,
            lambda galaxy: audit.predict_p6_long_range_envelope(
                galaxy, alpha_sum
            ),
        )[0]
        for group, galaxies in groups.items()
    }
    newton_metrics = {
        group: audit._model_metrics(galaxies, legacy.predict_newton)[0]
        for group, galaxies in groups.items()
    }

    bulgeless = _bulgeless_names(data_dir)
    bulgeless_metrics: dict[str, Any] = {}
    for group, galaxies in groups.items():
        selected = [galaxy for galaxy in galaxies if galaxy.name in bulgeless]
        bulgeless_metrics[group] = {
            "galaxies": len(selected),
            "finite_disk": _metrics_for_frozen_index(
                selected, baseline_cache[group], best_index
            ),
            "exact_long_range": audit._model_metrics(
                selected,
                lambda galaxy: audit.predict_p6_long_range_envelope(
                    galaxy, alpha_sum
                ),
            )[0],
        }

    all_sensitivity_upper = all(
        item["best_at_upper_boundary"] for item in sensitivity
    )
    passes = {
        "stiff_input_certified_and_observation_free": True,
        "single_global_scale_no_per_galaxy_force_parameters": True,
        "validation_and_test_not_used_for_scale_selection": True,
        "fftlog_newtonian_identity_below_1e_6": (
            baseline["maximum_fractional_newtonian_identity_error"] < 1.0e-6
        ),
        "no_negative_predictions_at_positive_source_points": (
            baseline["negative_predictions_at_positive_source_points"] == 0
        ),
        "baseline_best_scale_is_upper_grid_boundary": baseline[
            "best_at_upper_boundary"
        ],
        "baseline_train_score_nonincreasing_with_scale": baseline[
            "train_objective_nonincreasing_with_ell"
        ],
        "boundary_sensitivity_does_not_create_finite_optimum": (
            all_sensitivity_upper
        ),
        "finite_disk_test_does_not_reach_empirical_rar": (
            baseline_metrics["test"]["chi2_per_point"] > 10.0
        ),
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.sparc-finite-disk-yukawa.v1",
        "title": "Geometry-matched finite-range stiff Yukawa check",
        "classification": (
            "retrospective_effective_disk_feasibility_test_not_detection"
        ),
        "claim_boundary": (
            "This applies the action-derived stiff spectrum and residues to an "
            "effective razor-thin disk reconstructed from the public Newtonian "
            "baryonic curve. The public tables do not contain the gas surface-"
            "density map or full 3D baryonic density, so they do not identify a "
            "unique extended-source Yukawa convolution."
        ),
        "source_inventory": {
            "official_page": "https://astroweb.cwru.edu/SPARC/",
            "official_mass_model_archive": (
                "https://astroweb.cwru.edu/SPARC/Rotmod_LTG.zip"
            ),
            "archive_columns": [
                "Rad",
                "Vobs",
                "errV",
                "Vgas",
                "Vdisk",
                "Vbul",
                "SBdisk",
                "SBbul",
            ],
            "gas_surface_density_column_present": False,
            "vertical_density_profile_present": False,
            "local_catalogue_files": 175,
            "local_catalogue_aggregate_sha256": (
                legacy.aggregate_dataset_sha256(data_dir)[0]
            ),
        },
        "inputs": {
            "stiff_force_path": (
                "first_principles_audit/prediction_factory/artifacts/"
                "stiff_boundary_force.json"
            ),
            "stiff_force_sha256": _sha256(STIFF_PATH),
            "split_path": (
                "first_principles_audit/prediction_factory/sparc_split_v1.json"
            ),
            "split_sha256": _sha256(SPLIT_PATH),
            "stiff_masses_mu": masses.tolist(),
            "stiff_strengths_alpha": strengths.tolist(),
            "sum_alpha": alpha_sum,
            "observational_inputs_used_to_derive_force": [],
        },
        "operator": {
            "geometry": "effective axisymmetric razor-thin disk",
            "source_profile": "a(R)=R*gbar(R)=Vbar(R)^2",
            "transform_order": 1,
            "mode_transfer": "T(k;m)=k/sqrt(k^2+m^2)",
            "total_transfer": "1+sum_n alpha_n*T(k;mu_n/ell)",
            "inverse_problem": (
                "the supplied finite radial curve is continued with declared "
                "inner and outer power laws before FFTLog"
            ),
            "motion_status": (
                "quasi-static rotation-curve test; no radiative or retarded "
                "time dependence is inferred"
            ),
        },
        "protocol": {
            "split_counts": {key: len(value) for key, value in split.items()},
            "scale_grid_kpc": ELL_GRID_KPC.tolist(),
            "scale_selection": (
                "one global ell minimizes summed train chi2 on the fixed grid"
            ),
            "validation_and_test": "evaluated at frozen train-selected ell",
            "per_galaxy_force_parameters": False,
            "catalogue_status": (
                "retrospective: catalogue outcomes were exposed before this test"
            ),
        },
        "baseline_scan": baseline,
        "sensitivity_scans": sensitivity,
        "metrics": {
            "finite_disk_at_train_selected_scale": baseline_metrics,
            "exact_long_range_limit": exact_long_range_metrics,
            "newtonian": newton_metrics,
            "bulgeless_subset": bulgeless_metrics,
        },
        "adjudication": {
            "finite_scale_identified": False,
            "reason": (
                "training chi2 improves toward the largest ell and every declared "
                "boundary sensitivity repeats the upper-grid optimum; the scan "
                "therefore selects the already computed long-range limit rather "
                "than a finite interaction scale"
            ),
            "disk_cancellation_rescues_stiff_candidate": False,
            "geometry_matched_operator_built": True,
            "unique_physical_convolution_built": False,
            "missing_data_for_unique_convolution": [
                "gas surface-density profile for each galaxy",
                "vertical density model or declared razor-thin physical assumption",
                "radial source continuation outside the published samples",
            ],
            "what_the_residual_can_do": (
                "define a matched-filter target for a microscopic missing sector"
            ),
            "what_the_residual_cannot_do": (
                "be added object by object and then counted as evidence for a force"
            ),
            "next_gate": (
                "derive a common state-dependent source/coupling and freeze it "
                "before evaluating an independent galaxy sample"
            ),
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "passes": passes,
    }


def main() -> int:
    report = build()
    _write(OUTPUT, report)
    scan = report["baseline_scan"]
    test = report["metrics"]["finite_disk_at_train_selected_scale"]["test"]
    print(f"[finite disk artifact] {OUTPUT}")
    print(
        "[train-selected ell] {:.6g} kpc{}".format(
            scan["best_ell_kpc"],
            " (upper boundary)" if scan["best_at_upper_boundary"] else "",
        )
    )
    print(f"[test chi2/point] {test['chi2_per_point']:.9f}")
    print(f"[certificate] {'PASS' if report['passes']['all'] else 'FAIL'}")
    return 0 if report["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
