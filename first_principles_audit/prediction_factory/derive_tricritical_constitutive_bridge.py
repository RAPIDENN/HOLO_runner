#!/usr/bin/env python3
"""Test a classical tricritical route to the deep constitutive operator.

Let the nonnegative selector be the squared amplitude of a collective field,
s=q^2.  The auxiliary density

    L_aux = -s*Y + W(s),
    W(s)=m2*s + u4*s^2/2 + s^3/3,

has the nonzero stationary branch Y=m2+u4*s+s^2.  At the tricritical point
m2=u4=0 it gives s=sqrt(Y) and

    P(Y)=s*Y-W(s)=2*Y^(3/2)/3.

This is an exact classical mechanism for the desired exponent.  It is not a
derivation from the current bulk: the q^2*Y vertex, the vanishing relevant
couplings, a positive sextic coefficient, a saturation completion and the
auxiliary/local character of q all remain physical gates.
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
EFFECTIVE_ACTION = REPO / "first_principles_audit/artifacts/holo_effective_action.json"
INTERFACE = REPO / "first_principles_audit/artifacts/interface_action_derivation.json"
ENVELOPE = HERE / "artifacts" / "collector_legendre_envelope.json"
SOFT_SCALING = HERE / "artifacts" / "soft_mode_cubic_scaling.json"
OUTPUT = HERE / "artifacts" / "tricritical_constitutive_bridge.json"


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


def stationary_selector(
    gradient_y: np.ndarray, *, mass2: float = 0.0, quartic: float = 0.0
) -> np.ndarray:
    """Return the nonzero q^2 branch, or zero below its threshold."""

    y = np.asarray(gradient_y, dtype=float)
    if np.any(~np.isfinite(y)) or np.any(y < 0.0):
        raise ValueError("Y must be finite and nonnegative")
    if not np.isfinite(mass2) or not np.isfinite(quartic) or quartic < 0.0:
        raise ValueError("finite mass2 and nonnegative quartic required")
    discriminant = quartic * quartic + 4.0 * (y - mass2)
    selector = np.zeros_like(y)
    active = discriminant > quartic * quartic
    selector[active] = 0.5 * (
        -quartic + np.sqrt(discriminant[active])
    )
    return selector


def dual_density(
    gradient_y: np.ndarray, *, mass2: float = 0.0, quartic: float = 0.0
) -> tuple[np.ndarray, np.ndarray]:
    """Return selector s and the stationary P=sY-W(s)."""

    y = np.asarray(gradient_y, dtype=float)
    s = stationary_selector(y, mass2=mass2, quartic=quartic)
    potential = mass2 * s + 0.5 * quartic * s * s + s**3 / 3.0
    return s, s * y - potential


def _log_slope(x: np.ndarray, y: np.ndarray) -> float:
    positive = (x > 0.0) & (y > 0.0)
    return float(np.polyfit(np.log(x[positive]), np.log(y[positive]), 1)[0])


def build() -> dict[str, Any]:
    effective = _read(EFFECTIVE_ACTION)
    interface = _read(INTERFACE)
    envelope = _read(ENVELOPE)
    soft = _read(SOFT_SCALING)
    if effective["summary"]["passes"]["all"] is not True:
        raise RuntimeError("effective action must be certified")
    if interface["passes"]["all"] is not True:
        raise RuntimeError("interface must be certified")
    if envelope["passes"]["all"] is not True:
        raise RuntimeError("collector envelope must be certified")
    if soft["scaling_checks"]["all"] is not True:
        raise RuntimeError("soft-mode scaling proxy must be certified")

    y = np.logspace(-12.0, -3.0, 512)
    selector, density = dual_density(y)
    selector_error = float(np.max(np.abs(selector / np.sqrt(y) - 1.0)))
    density_error = float(
        np.max(np.abs(density / ((2.0 / 3.0) * y**1.5) - 1.0))
    )
    density_slope = _log_slope(y, density)

    quartic = 0.2
    _, quartic_density = dual_density(y, quartic=quartic)
    contaminated = y < 1.0e-7
    quartic_deep_slope = _log_slope(
        y[contaminated], quartic_density[contaminated]
    )
    threshold_mass2 = 1.0e-6
    threshold_selector, _ = dual_density(y, mass2=threshold_mass2)
    threshold_is_inactive = bool(np.all(threshold_selector[y <= threshold_mass2] == 0.0))

    # The curvature of L_aux with respect to q on the tricritical branch is
    # 8Y.  A canonical q kinetic term would therefore have a correlation
    # length proportional to Y^(-1/2), invalidating uniform local elimination.
    auxiliary_curvature = 8.0 * y
    correlation_length_proxy = 1.0 / np.sqrt(auxiliary_curvature)
    correlation_power = _log_slope(y, correlation_length_proxy)

    checks = {
        "certified_inputs": True,
        "tricritical_selector_is_sqrt_y": selector_error < 2.0e-15,
        "tricritical_dual_is_two_thirds_y_three_halves": density_error < 3.0e-15,
        "tricritical_log_slope_is_three_halves": abs(density_slope - 1.5) < 2.0e-12,
        "positive_quartic_restores_analytic_y_squared": abs(quartic_deep_slope - 2.0) < 2.0e-3,
        "positive_mass_creates_a_threshold": threshold_is_inactive,
        "dynamical_amplitude_correlation_length_diverges": abs(correlation_power + 0.5) < 2.0e-12,
        "no_observational_tables_read": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "collective_amplitude_q_identified_in_bulk_spectrum": False,
        "q_squared_times_Y_vertex_derived_from_constraint_action": False,
        "quadratic_relevant_coupling_m2_vanishes_without_data_tuning": False,
        "quartic_relevant_coupling_u4_vanishes_without_data_tuning": False,
        "positive_sextic_normalization_derived": False,
        "q_is_auxiliary_or_gradient_terms_are_controlled": False,
        "all_order_saturation_to_selector_below_one_derived": False,
        "a0_matter_normalization_slip_and_lensing_derived": False,
        "physical_completion": False,
    }

    return {
        "schema": "holo.tricritical-constitutive-bridge.v1",
        "title": "Tricritical collective-amplitude bridge to P(Y)",
        "classification": (
            "exact_classical_deep_exponent_mechanism;"
            "tricritical_bulk_realization_not_derived"
        ),
        "sources": {
            "effective_action": {
                "path": str(EFFECTIVE_ACTION.relative_to(REPO)),
                "sha256": _sha256(EFFECTIVE_ACTION),
            },
            "interface": {
                "path": str(INTERFACE.relative_to(REPO)),
                "sha256": _sha256(INTERFACE),
            },
            "collector_envelope": {
                "path": str(ENVELOPE.relative_to(REPO)),
                "sha256": _sha256(ENVELOPE),
            },
            "soft_scaling": {
                "path": str(SOFT_SCALING.relative_to(REPO)),
                "sha256": _sha256(SOFT_SCALING),
            },
            "observational_inputs_read": [],
        },
        "exact_mechanism": {
            "selector": "s=q^2>=0",
            "auxiliary_density": "L_aux=-s*Y+W(s)",
            "potential": "W(s)=m2*s+u4*s^2/2+s^3/3",
            "stationarity": "Y=m2+u4*s+s^2",
            "tricritical_point": "m2=u4=0",
            "tricritical_solution": "s=sqrt(Y)",
            "deep_operator": "P(Y)=s*Y-W(s)=2*Y^(3/2)/3",
            "q_form": "L_aux=-q^2*Y+m2*q^2+u4*q^4/2+q^6/3",
            "stationary_q_hessian": "d2L_aux/dq2=8*Y at m2=u4=0",
        },
        "old_vs_new": {
            "previous_fixed_poles": {
                "carrier": "finite set of canonical modes with positive fixed masses",
                "operator": "quadratic Green functions and additive Yukawa exchange",
                "source_mass_exponent": 1.0,
                "failure": "no finite source-independent pole sum changes M into sqrt(M)",
            },
            "new_collective_coordinate": {
                "carrier": "nonnegative squared amplitude s=q^2",
                "operator": "stationary nonlinear constitutive response",
                "source_mass_exponent_in_deep_spherical_limit": 0.5,
                "gain": "the half-power follows classically at a tricritical sextic point",
            },
        },
        "relevant_deformation_tests": {
            "quartic_test_value": quartic,
            "quartic_contaminated_deep_P_power": quartic_deep_slope,
            "mass_threshold_test_value": threshold_mass2,
            "mass_threshold_branch_inactive_below_threshold": threshold_is_inactive,
            "interpretation": (
                "Any positive u4 changes the asymptotic P power from 3/2 to 2; "
                "any positive m2 removes the branch below Y=m2. Both relevant "
                "couplings must therefore vanish by a microscopic mechanism, "
                "not by fitting the exposed galaxy target."
            ),
        },
        "locality_obstruction": {
            "correlation_length_proxy": "xi_q=(8*Y)^(-1/2)",
            "measured_power_in_Y": correlation_power,
            "interpretation": (
                "The exact algebraic saddle becomes gapless as Y tends to zero. "
                "A canonically propagating q cannot be integrated out uniformly "
                "as a local auxiliary field; q must be a genuine constrained "
                "variable or its gradient sector must scale away consistently."
            ),
        },
        "current_bulk_boundary": {
            "positive_canonical_carrier": bool(
                interface["carrier_metrics"]["p_min"] > 0.0
                and interface["carrier_metrics"]["w_min"] > 0.0
            ),
            "known_interface_order": interface["conditional_4d_interface"]["ln_A_m"],
            "higher_brane_jets_selected": soft["physical_gates"][
                "higher_brane_jets_selected_by_microscopic_boundary_theory"
            ],
            "conclusion": (
                "The current artefacts fix a healthy quadratic propagating carrier "
                "and only the linear matter coefficient. They do not fix the q^2Y "
                "vertex or the tricritical cancellations."
            ),
        },
        "physical_gates": physical_gates,
        "decisive_next_calculation": (
            "Perform the gauge-invariant cubic-through-sextic reduction including "
            "lapse, shift, brane bending and the matter metric. Project it onto the "
            "soft collective coordinate and test prospectively whether m2=u4=0, "
            "the q^6 coefficient is positive and q^2Y is nonzero."
        ),
        "diagnostics": {
            "samples": int(y.size),
            "selector_max_relative_error": selector_error,
            "deep_density_max_relative_error": density_error,
            "deep_density_log_slope": density_slope,
            "minimum_auxiliary_curvature": float(np.min(auxiliary_curvature)),
            "maximum_correlation_length_proxy": float(
                np.max(correlation_length_proxy)
            ),
        },
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
        "[tricritical] P(Y) power={:.12g}; quartic-contaminated power={:.12g}".format(
            result["diagnostics"]["deep_density_log_slope"],
            result["relevant_deformation_tests"][
                "quartic_contaminated_deep_P_power"
            ],
        )
    )
    print(f"[physical completion] {result['physical_gates']['physical_completion']}")
    print(f"[algebra certificate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
