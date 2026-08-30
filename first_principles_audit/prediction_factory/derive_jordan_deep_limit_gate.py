#!/usr/bin/env python3
"""Test the deep-collector branch of the direct Jordan selector embedding.

The exposed collector uses s=1-exp(-t), with t=sqrt(g_N/a0), so s tends to
zero in the isolated deep-field limit.  If the same s is identified with
A_m^-2 in the certified scalar--matter interface, then the Jordan tensor
coefficient M_Pl^2*s and the inverse conformal map both become singular.

This does not reject a nonlinear derivative/constitutive scalar sector.  It
rejects promoting the collector selector directly to the *entire* Jordan
Planck coefficient while claiming a regular relativistic completion.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
EMBEDDING = HERE / "artifacts" / "jordan_selector_embedding.json"
ENVELOPE = HERE / "artifacts" / "collector_legendre_envelope.json"
OUTPUT = HERE / "artifacts" / "jordan_deep_limit_gate.json"


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


def target_frame_path(t: np.ndarray, beta: float) -> dict[str, np.ndarray]:
    """Map the exact collector selector onto an exponential matter frame."""

    t = np.asarray(t, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t <= 0.0):
        raise ValueError("t must be positive and finite")
    if not np.isfinite(beta) or beta == 0.0:
        raise ValueError("beta must be nonzero and finite")
    selector = -np.expm1(-t)
    physical_acceleration = t * t / selector
    gradient_invariant = physical_acceleration * physical_acceleration
    conformal = 1.0 / np.sqrt(selector)
    phi_over_mpl = -np.log(selector) / (2.0 * beta)
    tensor_kinetic_ratio = selector
    return {
        "s": selector,
        "x": physical_acceleration,
        "X": gradient_invariant,
        "A_m": conformal,
        "phi_over_mpl": phi_over_mpl,
        "M_J_squared_over_M_Pl_squared": tensor_kinetic_ratio,
    }


def build() -> dict[str, Any]:
    embedding = _read(EMBEDDING)
    envelope = _read(ENVELOPE)
    if embedding["checks"]["all"] is not True:
        raise RuntimeError("Jordan embedding identities must pass first")
    if envelope["passes"]["all"] is not True:
        raise RuntimeError("collector envelope must pass first")

    beta = float(embedding["numerical_identity_check"]["test_beta"])
    t = np.logspace(-11.0, -4.0, 512)
    frame = target_frame_path(t, beta)
    log_t = np.log(t)
    selector_power = float(np.polyfit(log_t, np.log(frame["s"]), 1)[0])
    conformal_power = float(np.polyfit(log_t, np.log(frame["A_m"]), 1)[0])
    field_log_slope = float(
        np.polyfit(log_t, frame["phi_over_mpl"], 1)[0]
    )
    x_power = float(np.polyfit(log_t, np.log(frame["x"]), 1)[0])
    max_deep_s_over_t_error = float(
        np.max(np.abs(frame["s"] / t - 1.0))
    )

    brans_dicke_omega = 1.0 / (4.0 * beta * beta) - 1.5
    einstein_health_combination = 2.0 * brans_dicke_omega + 3.0

    checks = {
        "certified_inputs": True,
        "collector_deep_selector_scales_as_t": abs(selector_power - 1.0) < 2.0e-5,
        "collector_deep_acceleration_scales_as_t": abs(x_power - 1.0) < 2.0e-5,
        "conformal_factor_diverges_as_t_minus_half": abs(conformal_power + 0.5) < 2.0e-5,
        "canonical_field_runs_logarithmically": abs(
            field_log_slope + 1.0 / (2.0 * beta)
        )
        < 2.0e-5,
        "deep_series_resolved": max_deep_s_over_t_error < 6.0e-5,
        "einstein_frame_scalar_is_not_a_ghost": einstein_health_combination > 0.0,
        "no_observational_tables_read": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "direct_selector_keeps_nonzero_jordan_tensor_kinetic_term": False,
        "deep_limit_frame_map_is_nonsingular": False,
        "finite_field_excursion_reaches_s_zero": False,
        "constraint_reduction_yields_local_aqual_operator": False,
        "simple_negative_jordan_potential_is_stable": False,
        "direct_s_as_full_planck_coefficient_completion": False,
    }

    return {
        "schema": "holo.jordan-deep-limit-gate.v1",
        "title": "Deep-limit gate for the direct Jordan gravitational selector",
        "classification": (
            "exact_asymptotic_obstruction_to_direct_sR_identification;"
            "derivative_constitutive_route_remains_open"
        ),
        "sources": {
            "jordan_embedding": {
                "path": str(EMBEDDING.relative_to(REPO)),
                "sha256": _sha256(EMBEDDING),
            },
            "collector_envelope": {
                "path": str(ENVELOPE.relative_to(REPO)),
                "sha256": _sha256(ENVELOPE),
            },
            "observational_inputs_read": [],
        },
        "exact_path": {
            "collector_parameter": "t=sqrt(g_N/a0)",
            "selector": "s=1-exp(-t)",
            "physical_acceleration": "x=g/a0=t^2/s",
            "frame_map": "A_m=s^(-1/2), phi/M_Pl=-log(s)/(2*beta)",
            "jordan_tensor_coefficient": "M_J^2/M_Pl^2=s",
            "deep_limit": (
                "t->0: s~t, x~t, A_m~t^(-1/2), phi/M_Pl~"
                "-log(t)/(2*beta), and M_J^2/M_Pl^2->0"
            ),
        },
        "diagnostics": {
            "beta": beta,
            "samples": int(t.size),
            "selector_power_in_t": selector_power,
            "acceleration_power_in_t": x_power,
            "conformal_power_in_t": conformal_power,
            "field_slope_vs_log_t": field_log_slope,
            "maximum_deep_s_over_t_error": max_deep_s_over_t_error,
            "brans_dicke_omega_for_exponential_map": brans_dicke_omega,
            "two_omega_plus_three": einstein_health_combination,
        },
        "failure_of_early_linearization": {
            "expansion": "s=1-2*beta*phi/M_Pl+O(phi^2)",
            "domain": "valid only near a finite s=1 background",
            "consequence": (
                "With a regular invertible quadratic operator the response is "
                "analytic in source strength, so the leading force is linear "
                "in M (massless or Yukawa), not proportional to sqrt(M)."
            ),
            "why_the_target_disappeared": (
                "The required branch is an order-one run from s=1 toward a "
                "degenerate s=0 endpoint. Taylor expanding first removes that "
                "branch before solving the gravitational constraints."
            ),
        },
        "architecture_implication": {
            "rejected_direct_reading": (
                "Do not equate the collector susceptibility with the entire "
                "Jordan-frame Planck coefficient of the current one-scalar action."
            ),
            "surviving_route": (
                "Keep a nondegenerate Einstein-Hilbert tensor term and derive a "
                "separate nonlinear derivative/constitutive scalar or collective "
                "sector whose auxiliary selector multiplies its quasistatic "
                "gradient invariant. Couple that sector to matter through the "
                "certified A_m interface and derive slip and lensing separately."
            ),
        },
        "physical_gates": physical_gates,
        "checks": checks,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(
        "[deep path] s~t^{:.8f}, A_m~t^{:.8f}".format(
            result["diagnostics"]["selector_power_in_t"],
            result["diagnostics"]["conformal_power_in_t"],
        )
    )
    print(
        "[direct sR completion] "
        f"{result['physical_gates']['direct_s_as_full_planck_coefficient_completion']}"
    )
    print(f"[asymptotic gate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
