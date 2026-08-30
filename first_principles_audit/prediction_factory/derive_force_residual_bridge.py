#!/usr/bin/env python3
"""Map the differential from the stiff HOLO force to the SPARC target.

The origin is the observation-free stiff-boundary force.  The destination is
the train-fitted empirical RAR already reported by the SPARC audit.  Their
difference and logarithmic derivative expose which radial/acceleration shape
is missing.  The exact bridge is diagnostic: because it uses the empirical
destination, it is not promoted as a new HOLO prediction.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
STIFF_RELATIVE = Path(
    "first_principles_audit/prediction_factory/artifacts/stiff_boundary_force.json"
)
SPARC_RELATIVE = Path(
    "first_principles_audit/prediction_factory/sparc_physical_audit.json"
)
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "force_residual_bridge.json"

GBAR_GRID_M_S2 = np.logspace(-14.0, -8.0, 241)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def rar_nu(gbar_m_s2: np.ndarray, g_dagger_m_s2: float) -> np.ndarray:
    gbar = np.asarray(gbar_m_s2, dtype=float)
    if not (
        np.all(np.isfinite(gbar))
        and np.all(gbar > 0.0)
        and math.isfinite(g_dagger_m_s2)
        and g_dagger_m_s2 > 0.0
    ):
        raise ValueError("accelerations must be positive and finite")
    root = np.sqrt(gbar / g_dagger_m_s2)
    return 1.0 / (-np.expm1(-root))


def rar_nu_log_gbar_derivative(
    gbar_m_s2: np.ndarray, g_dagger_m_s2: float
) -> np.ndarray:
    gbar = np.asarray(gbar_m_s2, dtype=float)
    root = np.sqrt(gbar / g_dagger_m_s2)
    exponential = np.exp(-root)
    return -0.5 * root * exponential / np.square(1.0 - exponential)


def point_yukawa_boost_and_log_radius_derivative(
    x_r_over_ell: np.ndarray, masses_mu: np.ndarray, alpha: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x_r_over_ell, dtype=float)
    masses = np.asarray(masses_mu, dtype=float)
    strengths = np.asarray(alpha, dtype=float)
    if not (
        x.ndim == masses.ndim == strengths.ndim == 1
        and masses.size == strengths.size > 0
        and np.all(x >= 0.0)
        and np.all(masses > 0.0)
        and np.all(strengths > 0.0)
    ):
        raise ValueError("invalid Yukawa comb")
    mode_x = np.outer(x, masses)
    boost = np.sum(
        strengths[None, :] * (1.0 + mode_x) * np.exp(-mode_x), axis=1
    )
    derivative = -np.sum(
        strengths[None, :] * np.square(mode_x) * np.exp(-mode_x), axis=1
    )
    return boost, derivative


def build() -> dict[str, Any]:
    stiff_path = REPO / STIFF_RELATIVE
    sparc_path = REPO / SPARC_RELATIVE
    stiff = _read(stiff_path)
    sparc = _read(sparc_path)
    if stiff.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff force input is not certified")
    if sparc.get("passes", {}).get("all") is not True:
        raise RuntimeError("SPARC audit input is not certified")

    force = stiff["spectrum_and_force"]
    alpha_sum = float(force["sum_alpha_short_distance"])
    masses = np.asarray(force["masses_mu"], dtype=float)
    alpha = np.asarray(force["alpha_uv_2_beta_squared"], dtype=float)
    g_dagger = float(sparc["frozen_train_fits"]["rar"]["g_dagger_m_s2"])

    destination_nu = rar_nu(GBAR_GRID_M_S2, g_dagger)
    destination_derivative = rar_nu_log_gbar_derivative(
        GBAR_GRID_M_S2, g_dagger
    )
    origin_nu = np.full_like(destination_nu, 1.0 + alpha_sum)
    missing_nu = destination_nu - origin_nu

    # nu_RAR-1=alpha has a closed-form crossing.
    crossing_root = math.log((1.0 + alpha_sum) / alpha_sum)
    crossing_gbar = g_dagger * crossing_root * crossing_root

    x = np.logspace(-3.0, 3.0, 241)
    point_boost, point_derivative = point_yukawa_boost_and_log_radius_derivative(
        x, masses, alpha
    )
    anchors = []
    for acceleration in (1.0e-13, 1.0e-12, 1.0e-11, 1.0e-10, 1.0e-9):
        destination = float(rar_nu(np.asarray([acceleration]), g_dagger)[0])
        derivative = float(
            rar_nu_log_gbar_derivative(np.asarray([acceleration]), g_dagger)[0]
        )
        anchors.append(
            {
                "gbar_m_s2": acceleration,
                "origin_multiplier": 1.0 + alpha_sum,
                "destination_multiplier": destination,
                "missing_multiplier": destination - 1.0 - alpha_sum,
                "d_missing_multiplier_d_ln_gbar": derivative,
            }
        )

    passes = {
        "input_certificates_pass": True,
        "stiff_origin_observation_free": stiff["observational_inputs_read"] == [],
        "rar_destination_declared_empirical": (
            sparc["classification"]
            == "retrospective_input_repair_not_holo_confirmation"
        ),
        "analytic_derivative_matches_finite_difference": bool(
            np.max(
                np.abs(
                    np.gradient(destination_nu, np.log(GBAR_GRID_M_S2))
                    - destination_derivative
                )[2:-2]
            )
            < 2.0e-2
        ),
        "point_yukawa_boost_never_exceeds_short_range_sum": bool(
            np.all(point_boost <= alpha_sum * (1.0 + 1.0e-13))
        ),
        "point_yukawa_radial_slope_non_positive": bool(
            np.all(point_derivative <= 0.0)
        ),
        "missing_response_changes_sign": bool(
            np.min(missing_nu) < 0.0 < np.max(missing_nu)
        ),
        "crossing_inside_grid": bool(
            GBAR_GRID_M_S2[0] < crossing_gbar < GBAR_GRID_M_S2[-1]
        ),
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.force-residual-bridge.v1",
        "title": "Origin-to-destination force differential",
        "classification": "empirical_inverse_diagnostic_not_prediction",
        "inputs": {
            "origin_stiff_force": {
                "path": STIFF_RELATIVE.as_posix(),
                "sha256": _sha256(stiff_path),
            },
            "destination_sparc_audit": {
                "path": SPARC_RELATIVE.as_posix(),
                "sha256": _sha256(sparc_path),
                "fit_scope": "RAR scale fitted on frozen training galaxies",
            },
        },
        "map_definition": {
            "origin": "g_HOLO=(1+sum_alpha_stiff) g_bar in the long-range limit",
            "destination": (
                "g_RAR=g_bar/[1-exp(-sqrt(g_bar/g_dagger))]"
            ),
            "differential": "Delta_g=g_destination-g_origin",
            "dimensionless_differential": (
                "Delta_nu=nu_RAR-(1+sum_alpha_stiff)"
            ),
            "transient_derivative": (
                "d Delta_nu/d ln(g_bar)="
                "-[sqrt(g_bar/g_dagger)/2] exp(-sqrt(g_bar/g_dagger))/"
                "[1-exp(-sqrt(g_bar/g_dagger))]^2"
            ),
            "homotopy": "g(s)=g_origin+s Delta_g, 0<=s<=1",
            "homotopy_tangent": "partial g/partial s=Delta_g",
        },
        "parameters": {
            "sum_alpha_stiff": alpha_sum,
            "rar_g_dagger_m_s2_train_only": g_dagger,
            "zero_differential_crossing_gbar_m_s2": crossing_gbar,
        },
        "diagnosis": {
            "high_acceleration_side": (
                "the stiff candidate over-supplies the empirical correction"
            ),
            "low_acceleration_side": (
                "the stiff candidate under-supplies an increasingly large correction"
            ),
            "amplitude_only_sufficient": False,
            "fixed_linear_point_yukawa_scale_only_sufficient": False,
            "mathematical_reason": (
                "a fixed positive Yukawa comb is bounded by sum(alpha) and its "
                "boost decreases with radius, whereas the empirical missing "
                "multiplier grows as g_bar falls"
            ),
            "what_a_complete_theory_must_generate": (
                "an acceleration- or environment-dependent source/coupling, a new "
                "source component, or disk nonlocality strong enough to reverse "
                "the fixed point-source trend"
            ),
        },
        "anchors": anchors,
        "curves": {
            "gbar_m_s2": GBAR_GRID_M_S2.tolist(),
            "origin_multiplier": origin_nu.tolist(),
            "destination_multiplier": destination_nu.tolist(),
            "missing_multiplier": missing_nu.tolist(),
            "d_missing_multiplier_d_ln_gbar": destination_derivative.tolist(),
            "point_yukawa_x_r_over_ell": x.tolist(),
            "point_yukawa_boost": point_boost.tolist(),
            "d_point_yukawa_boost_d_ln_r": point_derivative.tolist(),
        },
        "next_falsifiable_step": {
            "derive_not_fit": (
                "derive the missing state dependence from a microscopic source or "
                "boundary sector before reopening validation/test galaxies"
            ),
            "disk_check": (
                "perform the finite-range axisymmetric Yukawa convolution because "
                "disk cancellation can differ from the point-source monotonicity"
            ),
            "promotion_gate": (
                "freeze the derived bridge on training information and require "
                "improvement on untouched galaxies without per-galaxy parameters"
            ),
        },
        "passes": passes,
        "evidence_boundary": (
            "The exact origin-to-destination differential is mathematically valid "
            "and identifies the missing shape. Because the destination is empirical, "
            "adding this differential back would reproduce it by construction and is "
            "not evidence for a new force."
        ),
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(f"[force residual bridge] {OUTPUT}")
    print(
        "[zero-gap acceleration] {:.9g} m/s^2".format(
            result["parameters"]["zero_differential_crossing_gbar_m_s2"]
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
