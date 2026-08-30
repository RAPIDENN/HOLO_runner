#!/usr/bin/env python3
"""Explore a positive phase-space origin for the collector's cubic dual.

The conventional soft-mode determinant has the required cubic exponent but
the wrong sign.  A distinct collective possibility is suggested by the
existing four-dimensional breathing dispersion: every gapped mode has a
three-dimensional continuum of spatial momenta.  If a positive local
occupation fills low-momentum states up to s=k_max/m, its positive energy is

    W_d(s) = integral_0^s u^(d-1) sqrt(1+u^2) du
           = s^d/d + higher powers.

Its Legendre envelope gives F_d(X)=(d-1)/d X^(d/(d-1)).  Dimension d=3 is
special: F=2 X^(3/2)/3 and the spherical AQUAL field scales as sqrt(M)/r.

The cubic is the rest-energy-weighted state count in the low-momentum limit
of the certified breathing dispersion.  This is still a generated microscopic
hypothesis, not a derivation of the ensemble, conjugate variable, occupation,
coupling, a0, the high-acceleration branch or lensing from the current action.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
BREATHING = HERE / "artifacts" / "breathing_response.json"
SOFT_MODE = HERE / "artifacts" / "soft_mode_cubic_bridge.json"
ENVELOPE = HERE / "artifacts" / "collector_legendre_envelope.json"
OUTPUT = HERE / "artifacts" / "phase_space_collector_bridge.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def dimension_row(dimension: int) -> dict[str, float | int]:
    if dimension <= 1:
        raise ValueError("phase-space dimension must exceed one")
    d = float(dimension)
    return {
        "dimension": dimension,
        "dual_power_in_s": d,
        "primal_power_in_X": d / (d - 1.0),
        "primal_coefficient": (d - 1.0) / d,
        "mu_power_in_x": 2.0 / (d - 1.0),
        "spherical_mass_power": (d - 1.0) / (d + 1.0),
        "spherical_radius_power": -2.0 * (d - 1.0) / (d + 1.0),
        "spherical_a0_power": 2.0 / (d + 1.0),
    }


def legendre_phase_space(
    query_x: np.ndarray, states: np.ndarray, dimension: int, block_size: int = 32
) -> tuple[np.ndarray, np.ndarray]:
    """Numerically select sup_s[sX-s^d/d] on a finite selector grid."""

    X = np.asarray(query_x, dtype=float)
    s = np.asarray(states, dtype=float)
    if dimension <= 1 or np.any(X <= 0.0) or np.any(s <= 0.0):
        raise ValueError("positive X and s with dimension>1 are required")
    if block_size < 1:
        raise ValueError("block_size must be positive")
    values = np.empty_like(X)
    selectors = np.empty_like(X)
    dual = s**dimension / dimension
    for start in range(0, X.size, block_size):
        stop = min(start + block_size, X.size)
        branches = X[start:stop, None] * s[None, :] - dual[None, :]
        selected = np.argmax(branches, axis=1)
        values[start:stop] = branches[np.arange(stop - start), selected]
        selectors[start:stop] = s[selected]
    return values, selectors


def gapped_three_dimensional_dual(
    selector: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return X=W'(s), W and F=sX-W for a unit-gap 3D mode."""

    s = np.asarray(selector, dtype=float)
    if np.any(~np.isfinite(s)) or np.any(s <= 0.0):
        raise ValueError("selector must be finite and positive")
    W = np.empty_like(s)
    small = s < 1.0e-2
    W[small] = (
        s[small] ** 3 / 3.0
        + s[small] ** 5 / 10.0
        - s[small] ** 7 / 56.0
        + s[small] ** 9 / 144.0
    )
    sl = s[~small]
    W[~small] = (
        sl * np.sqrt(1.0 + sl * sl) * (2.0 * sl * sl + 1.0)
        - np.arcsinh(sl)
    ) / 8.0
    X = s * s * np.sqrt(1.0 + s * s)
    F = s * X - W
    return X, W, F


def build() -> dict[str, Any]:
    breathing = _read(BREATHING)
    soft = _read(SOFT_MODE)
    envelope = _read(ENVELOPE)
    if breathing["passes"]["all"] is not True:
        raise RuntimeError("breathing response must pass first")
    if soft["certificate_checks"]["all"] is not True:
        raise RuntimeError("soft-mode exponent bridge must pass first")
    if envelope["passes"]["all"] is not True:
        raise RuntimeError("collector envelope must pass first")

    dimensions = [dimension_row(d) for d in range(2, 7)]
    d3 = next(row for row in dimensions if row["dimension"] == 3)
    query_s = np.geomspace(1.0e-5, 0.2, 512)
    query_X = np.square(query_s)
    states = np.geomspace(5.0e-6, 0.3, 32768)
    numerical_F, numerical_s = legendre_phase_space(query_X, states, 3)
    exact_F = (2.0 / 3.0) * query_X ** 1.5
    envelope_relative_error = float(
        np.max(np.abs(numerical_F - exact_F) / exact_F)
    )
    selector_relative_error = float(
        np.max(np.abs(numerical_s - query_s) / query_s)
    )

    breathing_equation = breathing["equations"]["four_dimensional_mode"]
    target_slope = float(envelope["diagnostics"]["deep_dual_log_slope"])
    target_coefficient = float(
        envelope["diagnostics"]["deep_dual_cubic_coefficient"]
    )
    determinant_sign = float(
        soft["three_dimensional_determinant"][
            "numerical_coefficient_of_m_cubed"
        ]
    )
    deep_s = np.geomspace(1.0e-6, 1.0e-2, 512)
    deep_X, gapped_W, gapped_F = gapped_three_dimensional_dual(deep_s)
    gapped_W_slope = float(
        np.polyfit(np.log(deep_s), np.log(gapped_W), 1)[0]
    )
    gapped_F_slope = float(
        np.polyfit(np.log(deep_X), np.log(gapped_F), 1)[0]
    )
    gapped_W_coefficient = float(
        np.median(gapped_W[:128] / deep_s[:128] ** 3)
    )
    gapped_F_coefficient = float(
        np.median(gapped_F[:128] / deep_X[:128] ** 1.5)
    )
    ultraviolet_s = np.geomspace(1.0e2, 1.0e4, 256)
    ultraviolet_X, _, ultraviolet_F = gapped_three_dimensional_dual(
        ultraviolet_s
    )
    ultraviolet_F_slope = float(
        np.polyfit(np.log(ultraviolet_X), np.log(ultraviolet_F), 1)[0]
    )

    algebra_checks = {
        "certified_inputs": True,
        "four_dimensional_mode_has_three_spatial_momenta": (
            "nabla^2" in breathing_equation
        ),
        "dimension_three_gives_cubic_positive_dual": (
            d3["dual_power_in_s"] == 3.0
            and d3["primal_coefficient"] == 2.0 / 3.0
        ),
        "dimension_three_gives_three_halves_primal": (
            d3["primal_power_in_X"] == 1.5
        ),
        "dimension_three_gives_sqrt_mass": (
            d3["spherical_mass_power"] == 0.5
        ),
        "dimension_three_gives_inverse_radius": (
            d3["spherical_radius_power"] == -1.0
        ),
        "numerical_envelope_matches_exact": envelope_relative_error < 1.0e-6,
        "numerical_selector_matches_exact": selector_relative_error < 3.0e-4,
        "matches_exposed_deep_dual": (
            abs(target_slope - 3.0) < 0.003
            and abs(target_coefficient - 1.0 / 3.0) < 0.002
        ),
        "kept_distinct_from_wrong_sign_vacuum_determinant": determinant_sign < 0.0,
        "gapped_low_momentum_energy_has_positive_cubic_dual": (
            abs(gapped_W_slope - 3.0) < 2.0e-5
            and abs(gapped_W_coefficient - 1.0 / 3.0) < 1.0e-9
        ),
        "gapped_legendre_action_has_three_halves_limit": (
            abs(gapped_F_slope - 1.5) < 2.0e-5
            and abs(gapped_F_coefficient - 2.0 / 3.0) < 1.0e-9
        ),
        "unsaturated_ultraviolet_is_not_mislabelled_newtonian": (
            abs(ultraviolet_F_slope - 4.0 / 3.0) < 2.0e-4
        ),
        "no_observational_tables_read": True,
    }
    algebra_checks["all"] = all(algebra_checks.values())

    physical_gates = {
        "positive_local_occupation_derived": False,
        "stationary_flat_occupation_distribution_derived": False,
        "gapped_low_momentum_window_selected_without_target": False,
        "occupation_cutoff_is_collector_selector_derived": False,
        "local_s_times_X_coupling_derived": False,
        "analytic_linear_X_term_absent_or_cancelled": False,
        "finite_matter_coupling_in_critical_limit_derived": False,
        "a0_and_normalization_derived": False,
        "newtonian_high_acceleration_completion_derived": False,
        "metric_lensing_completion_derived": False,
        "physical_completion": False,
    }

    return {
        "schema": "holo.phase-space-collector-bridge.v1",
        "title": "Three-dimensional phase-space collector hypothesis",
        "classification": (
            "generated_gapped_occupation_ansatz_with_derived_deep_exponent;"
            "not_a_force_derivation"
        ),
        "sources": {
            "breathing_response": {
                "path": str(BREATHING.relative_to(HERE.parents[1])),
                "sha256": _sha256(BREATHING),
            },
            "soft_mode_bridge": {
                "path": str(SOFT_MODE.relative_to(HERE.parents[1])),
                "sha256": _sha256(SOFT_MODE),
            },
            "collector_envelope": {
                "path": str(ENVELOPE.relative_to(HERE.parents[1])),
                "sha256": _sha256(ENVELOPE),
            },
            "observational_inputs_read": [],
        },
        "generated_idea": {
            "carrier": "gapped HOLO breathing mode with k in three spatial dimensions",
            "collector": "positive local occupation of low-momentum modes inside k/m<=s",
            "dual_potential": (
                "W_3(s)=integral_0^s u^2 sqrt(1+u^2)du="
                "s^3/3+O(s^5)"
            ),
            "selector_equation": "X=W_d'(s)=s^(d-1)",
            "primal_action": "F_d(X)=(d-1)X^(d/(d-1))/d",
            "dimension_three_result": (
                "for s<<1: W=s^3/3+O(s^5), X=s^2+O(s^4), "
                "F=2X^(3/2)/3+O(X^(5/2))"
            ),
            "spherical_result": (
                "mu(g/a0)g=g_N gives g=sqrt(G*M*a0)/r only for d=3"
            ),
            "sign_advantage": (
                "occupied positive-energy gapped modes give positive W; unlike "
                "the isolated bosonic vacuum determinant, the low-momentum "
                "coefficient has the sign required by convex W"
            ),
            "energy_weight_warning": (
                "The cubic follows only in the gapped low-momentum window where "
                "omega(k)=m+O(k^2/m).  A gapless or high-momentum population gives "
                "s^4, and a physical stationary bosonic occupation distribution "
                "has not yet been derived."
            ),
            "normalization_warning": (
                "Angular phase-space volume, (2*pi)^-3, degeneracy, occupation "
                "and the momentum scale multiply W by A3.  A3=1 is a normalized "
                "algebraic comparison, not a derived physical coefficient."
            ),
            "conjugate_warning": (
                "For N=s^3/3 the thermodynamic conjugate is dW/dN, whereas "
                "the collector construction uses X=dW/ds.  The required s*X "
                "coupling and ensemble are not derived.  At chemical potential "
                "equal to the gap, the rest-energy cubic cancels and the next "
                "term scales as s^5."
            ),
        },
        "dimension_matrix": dimensions,
        "dimension_convention": (
            "d labels the candidate phase-space dimension while Gauss law is "
            "kept in the observed three spatial dimensions.  For a separate "
            "physical dimension D, the radius exponent is "
            "-(D-1)(d-1)/(d+1)."
        ),
        "gapped_dispersion_check": {
            "dispersion": "omega/m=sqrt(1+(k/m)^2)",
            "dual": "W=int_0^s u^2 sqrt(1+u^2)du",
            "deep_W_log_slope_vs_s": gapped_W_slope,
            "deep_W_cubic_coefficient": gapped_W_coefficient,
            "deep_F_log_slope_vs_X": gapped_F_slope,
            "deep_F_three_halves_coefficient": gapped_F_coefficient,
            "high_X_F_log_slope": ultraviolet_F_slope,
            "high_X_adjudication": (
                "The unsaturated relativistic occupation tends to F~X^(4/3), "
                "not Newtonian F~X; a separate selector saturation is required."
            ),
        },
        "numerical_check": {
            "selector_points": int(states.size),
            "query_points": int(query_X.size),
            "maximum_F_relative_error": envelope_relative_error,
            "maximum_selector_relative_error": selector_relative_error,
            "maximum_branch_block_mib": 32 * states.size * 8 / 1024**2,
            "exposed_dual_log_slope": target_slope,
            "exposed_dual_cubic_coefficient": target_coefficient,
        },
        "evidence_boundary": (
            "The 3D momentum continuum and its relativistic dispersion exist in "
            "the certified breathing equation.  Filling that continuum with a "
            "positive stationary bosonic occupation, identifying its momentum "
            "radius with s, its normalization and coupling s to X are generated "
            "hypotheses, not current consequences of the five-dimensional action."
        ),
        "physical_gates": physical_gates,
        "decisive_next_test": (
            "Derive a kinetic/transport equation for breathing-mode occupation "
            "from cubic and quartic HOLO overlaps.  Its stationary free energy "
            "must create the gapped low-k occupation, retain finite matter "
            "coupling, eliminate the linear X term, saturate to the Newtonian "
            "branch and fix a0 without observational input."
        ),
        "algebra_checks": algebra_checks,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    d3 = next(row for row in result["dimension_matrix"] if row["dimension"] == 3)
    print(f"[artifact] {OUTPUT}")
    print(
        "[d=3] F power={:.6g}, mass power={:.6g}, radius power={:.6g}".format(
            d3["primal_power_in_X"],
            d3["spherical_mass_power"],
            d3["spherical_radius_power"],
        )
    )
    print(f"[physical completion] {result['physical_gates']['physical_completion']}")
    print(f"[algebra] {'PASS' if result['algebra_checks']['all'] else 'FAIL'}")
    return 0 if result["algebra_checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
