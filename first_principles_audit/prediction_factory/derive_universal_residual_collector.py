#!/usr/bin/env python3
"""Certify the universal response required by the SPARC residual.

The action-derived stiff Yukawa comb is a linear, positive response whose
long-range acceleration multiplier is bounded by ``1 + sum(alpha)``.  Changing
its one global length changes where that bounded response turns on, but cannot
create the growing low-acceleration boost seen in the SPARC radial-acceleration
relation (RAR).

This script translates the residual into the minimal *universal* matched
response

    Delta g(g_bar) = [nu_RAR(g_bar) - (1 + sum(alpha))] g_bar,

where the single RAR acceleration scale is fitted on the frozen training
galaxies.  Validation and test galaxies are never used to fit it.  The result
has no per-galaxy parameter and is evaluated both above 0.6 kpc in observed
radius and at a 600 kpc Yukawa length, resolving two distinct readings of the
historical ``600`` statement.

The response is an empirical target for a future nonlinear action completion,
not a derivation from the present Einstein--dilaton action and not evidence for
one force law at laboratory, QCD, galactic, and cosmological scales.
"""

from __future__ import annotations

import json
import math
import platform
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import scipy

try:
    from first_principles_audit.prediction_factory import sparc_crossval as legacy
    from first_principles_audit.prediction_factory import sparc_physical_audit as audit
    from first_principles_audit.prediction_factory import derive_sparc_finite_disk_yukawa as disk
except ModuleNotFoundError:  # direct execution from this directory
    import sparc_crossval as legacy
    import sparc_physical_audit as audit
    import derive_sparc_finite_disk_yukawa as disk


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "universal_residual_collector.json"
RADIUS_THRESHOLDS_KPC = (0.0, 0.6, 1.0, 3.0, 6.0, 10.0)
RANGE_AUDIT_KPC = np.asarray((0.6, 600.0, 1.0e5), dtype=float)


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def collector_nu(gbar_si: np.ndarray, g_dagger_si: float) -> np.ndarray:
    """Return the train-frozen RAR multiplier g_target/g_bar."""

    gbar = np.asarray(gbar_si, dtype=float)
    if not math.isfinite(g_dagger_si) or g_dagger_si <= 0.0:
        raise ValueError("g_dagger must be finite and positive")
    if np.any(~np.isfinite(gbar)) or np.any(gbar < 0.0):
        raise ValueError("gbar must be finite and non-negative")
    result = np.ones_like(gbar)
    positive = gbar > 0.0
    if np.any(positive):
        x = np.sqrt(gbar[positive] / g_dagger_si)
        result[positive] = 1.0 / (-np.expm1(-x))
    return result


def _gbar(galaxy: legacy.Galaxy) -> np.ndarray:
    radius_metres = galaxy.radius_kpc * legacy.KPC_METRES
    return np.square(galaxy.v_bary_kms) * 1.0e6 / radius_metres


def predict_collector(
    galaxy: legacy.Galaxy, g_dagger_si: float
) -> np.ndarray:
    gbar = _gbar(galaxy)
    gtarget = gbar * collector_nu(gbar, g_dagger_si)
    radius_metres = galaxy.radius_kpc * legacy.KPC_METRES
    return np.sqrt(np.maximum(gtarget * radius_metres, 0.0)) / 1000.0


def _masked_metrics(
    galaxies: Sequence[legacy.Galaxy],
    predictor: Callable[[legacy.Galaxy], np.ndarray],
    minimum_radius_kpc: float,
) -> dict[str, float | int]:
    chi2 = 0.0
    points = 0
    fractional: list[float] = []
    galaxies_used = 0
    for galaxy in galaxies:
        mask = galaxy.radius_kpc >= minimum_radius_kpc
        if not np.any(mask):
            continue
        prediction = np.asarray(predictor(galaxy), dtype=float)
        residual = (
            prediction[mask] - galaxy.v_obs_kms[mask]
        ) / galaxy.sigma_v_kms[mask]
        chi2 += float(np.sum(np.square(residual)))
        points += int(np.sum(mask))
        galaxies_used += 1
        fractional.extend(
            np.abs(prediction[mask] - galaxy.v_obs_kms[mask])
            / galaxy.v_obs_kms[mask]
        )
    if points == 0:
        raise ValueError("radius mask selected no SPARC points")
    return {
        "minimum_radius_kpc": minimum_radius_kpc,
        "galaxies": galaxies_used,
        "velocity_points": points,
        "chi2_per_point": chi2 / points,
        "median_absolute_fractional_velocity_error": float(
            np.median(fractional)
        ),
    }


def _range_audit(
    galaxies: Sequence[legacy.Galaxy],
    masses: np.ndarray,
    strengths: np.ndarray,
) -> dict[str, Any]:
    curves: dict[str, np.ndarray] = {}
    for galaxy in galaxies:
        curves[galaxy.name] = disk.stiff_disk_velocity_curves(
            galaxy, RANGE_AUDIT_KPC, masses, strengths, disk.BASELINE
        )[0]
    rows = []
    for index, ell_kpc in enumerate(RANGE_AUDIT_KPC):
        metrics = audit._model_metrics(
            galaxies, lambda galaxy, i=index: curves[galaxy.name][i]
        )[0]
        rows.append({"ell_kpc": float(ell_kpc), **metrics})
    return {
        "interpretation": (
            "This varies the global Yukawa length; it is distinct from cutting "
            "the observed rotation-curve points by their galactocentric radius."
        ),
        "test": rows,
    }


def _acceleration_inventory(
    groups: Mapping[str, Sequence[legacy.Galaxy]],
    g_dagger_si: float,
    rigid_nu: float,
) -> dict[str, Any]:
    by_group: dict[str, Any] = {}
    all_gbar: list[float] = []
    all_radius: list[float] = []
    for name, galaxies in groups.items():
        values = np.concatenate([_gbar(galaxy) for galaxy in galaxies])
        radii = np.concatenate([galaxy.radius_kpc for galaxy in galaxies])
        positive = values[values > 0.0]
        nu = collector_nu(positive, g_dagger_si)
        all_gbar.extend(positive.tolist())
        all_radius.extend(radii.tolist())
        by_group[name] = {
            "positive_velocity_points": int(positive.size),
            "gbar_min_m_s2": float(np.min(positive)),
            "gbar_max_m_s2": float(np.max(positive)),
            "radius_min_kpc": float(np.min(radii)),
            "radius_max_kpc": float(np.max(radii)),
            "collector_nu_min": float(np.min(nu)),
            "collector_nu_max": float(np.max(nu)),
            "fraction_requiring_more_than_rigid_ceiling": float(
                np.mean(nu > rigid_nu)
            ),
        }
    values = np.asarray(all_gbar)
    radii = np.asarray(all_radius)
    nu = collector_nu(values, g_dagger_si)
    return {
        "by_split": by_group,
        "all_catalogue": {
            "positive_velocity_points": int(values.size),
            "gbar_min_m_s2": float(np.min(values)),
            "gbar_max_m_s2": float(np.max(values)),
            "radius_min_kpc": float(np.min(radii)),
            "radius_max_kpc": float(np.max(radii)),
            "collector_nu_min": float(np.min(nu)),
            "collector_nu_max": float(np.max(nu)),
            "fraction_requiring_more_than_rigid_ceiling": float(
                np.mean(nu > rigid_nu)
            ),
            "fraction_requiring_screening_below_rigid_ceiling": float(
                np.mean(nu < rigid_nu)
            ),
        },
    }


def build() -> dict[str, Any]:
    groups, split = audit.load_groups(
        legacy.default_sparc_dir(), disk.SPLIT_PATH, legacy.default_trace_path()
    )
    stiff_document = disk._read(disk.STIFF_PATH)
    if stiff_document.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff force certificate must pass")
    force = stiff_document["spectrum_and_force"]
    masses = np.asarray(force["masses_mu"], dtype=float)
    strengths = np.asarray(force["alpha_uv_2_beta_squared"], dtype=float)
    alpha_sum = float(np.sum(strengths))
    rigid_nu = 1.0 + alpha_sum

    g_dagger_si, optimizer = legacy.fit_rar(groups["train"])
    collector_metrics = {
        name: audit._model_metrics(
            galaxies,
            lambda galaxy: predict_collector(galaxy, g_dagger_si),
        )[0]
        for name, galaxies in groups.items()
    }
    stiff_metrics = {
        name: audit._model_metrics(
            galaxies,
            lambda galaxy: audit.predict_p6_long_range_envelope(
                galaxy, alpha_sum
            ),
        )[0]
        for name, galaxies in groups.items()
    }
    radius_audit = []
    for threshold in RADIUS_THRESHOLDS_KPC:
        radius_audit.append(
            {
                "minimum_radius_kpc": threshold,
                "collector": _masked_metrics(
                    groups["test"],
                    lambda galaxy: predict_collector(galaxy, g_dagger_si),
                    threshold,
                ),
                "stiff_long_range": _masked_metrics(
                    groups["test"],
                    lambda galaxy: audit.predict_p6_long_range_envelope(
                        galaxy, alpha_sum
                    ),
                    threshold,
                ),
            }
        )
    range_audit = _range_audit(groups["test"], masses, strengths)
    inventory = _acceleration_inventory(groups, g_dagger_si, rigid_nu)
    crossing = g_dagger_si * math.log(1.0 + 1.0 / alpha_sum) ** 2

    passes = {
        "one_global_train_fitted_acceleration_scale": (
            math.isfinite(g_dagger_si) and g_dagger_si > 0.0
        ),
        "no_per_galaxy_parameters": True,
        "validation_and_test_not_used_for_fit": True,
        "rigid_positive_yukawa_has_finite_ceiling": rigid_nu < 1.2,
        "catalogue_requires_boost_above_rigid_ceiling": (
            inventory["all_catalogue"][
                "fraction_requiring_more_than_rigid_ceiling"
            ]
            > 0.5
        ),
        "catalogue_also_requires_high_acceleration_screening": (
            inventory["all_catalogue"][
                "fraction_requiring_screening_below_rigid_ceiling"
            ]
            > 0.0
        ),
        "collector_beats_stiff_on_frozen_test": (
            collector_metrics["test"]["chi2_per_point"]
            < stiff_metrics["test"]["chi2_per_point"]
        ),
        "collector_beats_stiff_above_0p6_kpc": (
            radius_audit[1]["collector"]["chi2_per_point"]
            < radius_audit[1]["stiff_long_range"]["chi2_per_point"]
        ),
        "six_hundred_kpc_range_does_not_rescue_rigid_force": (
            range_audit["test"][1]["chi2_per_point"] > 10.0
        ),
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.universal-residual-collector.v1",
        "title": "Universal signed residual response required by SPARC",
        "classification": (
            "retrospective_train_frozen_empirical_target_not_action_derivation"
        ),
        "claim_boundary": (
            "The collector is the train-frozen empirical response that a new "
            "common galactic sector would have to derive. It is not obtained "
            "from the present Einstein-dilaton action, does not prove a new "
            "force, and is not licensed outside the sampled galactic "
            "acceleration and radius domain."
        ),
        "mathematics": {
            "collector_multiplier": (
                "nu_col(gbar)=[1-exp(-sqrt(gbar/g_dagger))]^-1"
            ),
            "signed_residual": (
                "Delta_g=[nu_col(gbar)-(1+sum_alpha_stiff)]*gbar"
            ),
            "low_acceleration_limit": (
                "g_collector~sqrt(gbar*g_dagger); nu_collector diverges "
                "as sqrt(g_dagger/gbar)"
            ),
            "rigid_yukawa_bound": (
                "1<=nu_positive_linear_Yukawa<=1+sum_alpha_stiff"
            ),
            "meaning": (
                "A length-only positive linear Yukawa filter cannot supply the "
                "required acceleration-dependent growth. The missing operator "
                "must be nonlinear/state-dependent or contain a distinct "
                "infrared sector, and it must screen as well as enhance."
            ),
        },
        "frozen_inputs": {
            "split_path": str(disk.SPLIT_PATH.relative_to(HERE.parents[1])),
            "split_counts_galaxies": {
                name: len(names) for name, names in split.items()
            },
            "fit_split": "train",
            "evaluation_splits": ["validation", "test"],
            "stiff_force_path": str(disk.STIFF_PATH.relative_to(HERE.parents[1])),
            "sum_alpha_stiff": alpha_sum,
            "rigid_long_range_nu_ceiling": rigid_nu,
        },
        "train_fit": {
            "g_dagger_m_s2": g_dagger_si,
            "optimizer": optimizer,
            "per_galaxy_parameters": 0,
        },
        "signed_response": {
            "stiff_collector_crossing_gbar_m_s2": crossing,
            "below_crossing": "positive residual enhancement required",
            "above_crossing": "negative residual screening of stiff correction required",
        },
        "acceleration_domain": inventory,
        "metrics": {
            "collector": collector_metrics,
            "stiff_long_range": stiff_metrics,
        },
        "six_hundred_disambiguation": {
            "observed_radius_thresholds_test": radius_audit,
            "global_yukawa_range_test": range_audit,
            "adjudication": (
                "Neither retaining only R>=0.6 kpc nor setting ell=600 kpc "
                "makes the rigid stiff force agree with SPARC. These are "
                "different hypotheses and both fail in the frozen test set."
            ),
        },
        "scope": {
            "supported": (
                "universal empirical response over the SPARC galactic "
                "acceleration/radius domain represented by the frozen splits"
            ),
            "not_supported": [
                "one force valid at every physical length scale",
                "laboratory or Solar-System phenomenology",
                "QCD matching",
                "cosmological perturbations",
                "a unique three-dimensional disk solution",
            ],
            "next_derivation_gate": (
                "derive a common nonlinear or separate ultralight action sector "
                "whose field equation produces the signed response without "
                "using SPARC observations as its source"
            ),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "passes": passes,
    }


def main() -> None:
    result = build()
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(
        "[600 audit] R>=0.6 kpc stiff chi2/point="
        f"{result['six_hundred_disambiguation']['observed_radius_thresholds_test'][1]['stiff_long_range']['chi2_per_point']:.6f}; "
        "ell=600 kpc stiff chi2/point="
        f"{result['six_hundred_disambiguation']['global_yukawa_range_test']['test'][1]['chi2_per_point']:.6f}"
    )
    print(
        "[collector test] chi2/point="
        f"{result['metrics']['collector']['test']['chi2_per_point']:.6f}"
    )
    if not result["passes"]["all"]:
        raise SystemExit("universal residual collector certificate failed")


if __name__ == "__main__":
    main()
