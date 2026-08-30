#!/usr/bin/env python3
"""Differentiate the gap between a gapped 3D collector and the exact target.

For the exposed collector selector s=mu=1-exp(-t),

    X_target(s) = [-log(1-s)]^4 / s^2.

If a three-dimensional occupied mode supplies a shell density s^2, the energy
per shell required by the target is epsilon_req=X_target/s^2.  The gapped
breathing dispersion supplies epsilon_gap=sqrt(1+s^2).  Their positive
difference defines the exact interaction/saturation residual that a
microscopic completion would still need to derive.

This is inverse design against an exposed empirical target, not a new HOLO
prediction.  It translates the missing force shape into a local shell-cost
function that can be compared with cubic, quartic and resummed HOLO vertices.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import scipy
from scipy.integrate import cumulative_trapezoid

try:
    from first_principles_audit.prediction_factory import (
        derive_nonlinear_collector_action as action,
        derive_phase_space_collector_bridge as phase_space,
    )
except ModuleNotFoundError:
    import derive_nonlinear_collector_action as action
    import derive_phase_space_collector_bridge as phase_space


HERE = Path(__file__).resolve().parent
ACTION = HERE / "artifacts" / "nonlinear_collector_action.json"
PHASE_SPACE = HERE / "artifacts" / "phase_space_collector_bridge.json"
OUTPUT = HERE / "artifacts" / "collector_shell_residual.json"


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


def required_shell_cost(selector: np.ndarray) -> np.ndarray:
    """Return epsilon_req(s)=[-log(1-s)/s]^4 on 0<s<1."""

    s = np.asarray(selector, dtype=float)
    if np.any(~np.isfinite(s)) or np.any(s <= 0.0) or np.any(s >= 1.0):
        raise ValueError("selector must lie strictly in (0,1)")
    return np.power(-np.log1p(-s) / s, 4)


def build() -> dict[str, Any]:
    action_artifact = _read(ACTION)
    phase_artifact = _read(PHASE_SPACE)
    if action_artifact["passes"]["all"] is not True:
        raise RuntimeError("collector action must pass first")
    if phase_artifact["algebra_checks"]["all"] is not True:
        raise RuntimeError("phase-space bridge algebra must pass first")

    _, arrays = action.reconstruct_action_table(samples=16384)
    t = arrays["t"]
    s = arrays["mu"]
    X = arrays["X"]
    F = arrays["F"]
    open_domain = s < 1.0 - 1.0e-12
    t = t[open_domain]
    s = s[open_domain]
    X = X[open_domain]
    F = F[open_domain]

    epsilon_required = required_shell_cost(s)
    epsilon_gap = np.sqrt(1.0 + s * s)
    epsilon_interaction = epsilon_required - epsilon_gap
    interaction_derivative_s = s * s * epsilon_interaction
    interaction_derivative_t = interaction_derivative_s * np.exp(-t)
    # epsilon_interaction=2s+O(s^2), hence W_int=s^4/2+O(s^5).
    interaction_W = 0.5 * s[0] ** 4 + cumulative_trapezoid(
        interaction_derivative_t, t, initial=0.0
    )
    _, gap_W, _ = phase_space.gapped_three_dimensional_dual(s)
    decomposed_W = gap_W + interaction_W
    reconstructed_F = s * X - decomposed_W
    relative_F_error = np.abs(reconstructed_F - F) / np.maximum(
        np.abs(F), 1.0e-300
    )

    deep = slice(0, 400)
    deep_interaction_coefficient = float(
        np.median(interaction_W[deep] / s[deep] ** 4)
    )
    deep_epsilon_slope = float(
        np.polyfit(
            np.log(s[deep]),
            np.log(epsilon_interaction[deep]),
            1,
        )[0]
    )
    high = t > 10.0
    high_log_barrier_ratio = float(
        np.median(epsilon_interaction[high] / t[high] ** 4)
    )
    saturation_transport_residual = float(
        np.max(np.abs(np.exp(-t) - (1.0 - s)))
    )

    resolved_log = s < 1.0 - 1.0e-8
    checks = {
        "source_certificates_pass": True,
        "required_shell_cost_identity": bool(
            np.max(
                np.abs(epsilon_required[resolved_log] - X[resolved_log] / s[resolved_log] ** 2)
                / epsilon_required[resolved_log]
            )
            < 2.0e-9
        ),
        "interaction_shell_cost_positive": bool(
            np.min(epsilon_interaction) > 0.0
        ),
        "interaction_potential_monotone": bool(
            np.all(np.diff(interaction_W) > 0.0)
        ),
        "deep_interaction_starts_quartic": (
            abs(deep_epsilon_slope - 1.0) < 5.0e-4
            and abs(deep_interaction_coefficient - 0.5) < 5.0e-4
        ),
        "high_selector_cost_has_log_four_barrier": (
            abs(high_log_barrier_ratio - 1.0) < 0.08
        ),
        "selector_is_exact_first_order_saturation_solution": (
            saturation_transport_residual < 2.0e-16
        ),
        "decomposition_recovers_target_action": (
            float(np.max(relative_F_error)) < 3.0e-6
        ),
        "no_observational_table_read": True,
    }
    checks["all"] = all(checks.values())

    anchor_indices = np.unique(np.linspace(0, s.size - 1, 40, dtype=int))
    return {
        "schema": "holo.collector-shell-residual.v1",
        "title": "Shell-by-shell residual between gapped occupation and collector target",
        "classification": (
            "exact_inverse_design_of_exposed_target;not_a_microscopic_prediction"
        ),
        "sources": {
            "collector_action": {
                "path": str(ACTION.relative_to(HERE.parents[1])),
                "sha256": _sha256(ACTION),
            },
            "phase_space_bridge": {
                "path": str(PHASE_SPACE.relative_to(HERE.parents[1])),
                "sha256": _sha256(PHASE_SPACE),
            },
            "observational_inputs_read": [],
        },
        "derivation": {
            "target_selector": "s=mu=1-exp(-t)",
            "target_conjugate_gradient": "X(s)=[-log(1-s)]^4/s^2",
            "three_dimensional_shell_density": "rho_shell(s)=s^2",
            "required_energy_per_shell": (
                "epsilon_req=X/rho_shell=[-log(1-s)/s]^4"
            ),
            "gapped_energy_per_shell": "epsilon_gap=sqrt(1+s^2)",
            "missing_energy_per_shell": "epsilon_int=epsilon_req-epsilon_gap>0",
            "interaction_potential": "W_int'=s^2*epsilon_int",
            "decomposition": "W_target=W_gap+W_int",
        },
        "asymptotics": {
            "deep": (
                "epsilon_gap=1+s^2/2+...; epsilon_int=2s+...; "
                "W_gap=s^3/3+...; W_int=s^4/2+..."
            ),
            "newtonian_selector_limit": (
                "epsilon_int~[-log(1-s)]^4 as s->1; the missing interaction "
                "must create a divergent selector-saturation slope"
            ),
            "measured_deep_epsilon_power": deep_epsilon_slope,
            "measured_deep_Wint_quartic_coefficient": (
                deep_interaction_coefficient
            ),
            "measured_high_barrier_over_t_four": high_log_barrier_ratio,
            "normalization_dependency": (
                "For a physical gapped-sector prefactor A3, the residual begins "
                "W_int=(1-A3)*s^3/3+s^4/2+... .  Thus the statement that the "
                "first missing term is quartic is conditional on the normalized "
                "inverse-design choice A3=1; A3 is not derived by HOLO.  A "
                "nontrivial physical selector map can also change later "
                "coefficients.  Positivity is conditional too: as s tends to "
                "zero the residual shell cost tends to 1-A3."
            ),
        },
        "transport_equivalence": {
            "equation": "ds/dt=1-s with s(0)=0",
            "solution": "s=1-exp(-t)",
            "optical_reading": (
                "s is mathematically identical to the captured fraction after "
                "dimensionless optical depth t; equivalently it is the "
                "probability of at least one event in a Poisson process"
            ),
            "collector_parameter": "t=sqrt(g_N/a0)",
            "maximum_analytic_transport_residual": (
                saturation_transport_residual
            ),
            "evidence_boundary": (
                "This is an exact reformulation of the exposed interpolation "
                "law, not evidence that breathing quanta physically absorb."
            ),
        },
        "diagnostics": {
            "samples": int(s.size),
            "minimum_missing_shell_cost": float(np.min(epsilon_interaction)),
            "maximum_missing_shell_cost": float(np.max(epsilon_interaction)),
            "maximum_target_F_relative_error": float(np.max(relative_F_error)),
        },
        "anchors": [
            {
                "s": float(s[index]),
                "X": float(X[index]),
                "epsilon_required": float(epsilon_required[index]),
                "epsilon_gap": float(epsilon_gap[index]),
                "epsilon_interaction": float(epsilon_interaction[index]),
                "W_gap": float(gap_W[index]),
                "W_interaction": float(interaction_W[index]),
            }
            for index in anchor_indices
        ],
        "physical_gates": {
            "stationary_occupation_derived": False,
            "physical_selector_s_equals_mu_equals_kmax_over_m_derived": False,
            "holo_transport_equation_ds_dt_equals_one_minus_s_derived": False,
            "optical_depth_t_squared_equals_gN_over_a0_derived": False,
            "s_times_X_coupling_derived": False,
            "positive_quartic_from_holo_vertex_derived": False,
            "nonpolynomial_saturation_barrier_from_holo_derived": False,
            "a0_and_normalization_derived": False,
            "physical_completion": False,
        },
        "decisive_use": (
            "Compare the gauge-invariant cubic, quartic and higher soft-mode "
            "vertices against W_int after independently deriving the selector "
            "normalization A3.  Conditional on A3=1, the first new target is a "
            "positive +s^4/2 term.  A finite polynomial is insufficient near "
            "s=1, where the selector slope must diverge."
        ),
        "checks": checks,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    asymptotics = result["asymptotics"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[deep missing interaction] W_int~{:.9g}*s^4".format(
            asymptotics["measured_deep_Wint_quartic_coefficient"]
        )
    )
    print(
        "[target recovery] max relative F error="
        f"{result['diagnostics']['maximum_target_F_relative_error']:.6g}"
    )
    print(f"[physical completion] {result['physical_gates']['physical_completion']}")
    print(f"[inverse-design certificate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
