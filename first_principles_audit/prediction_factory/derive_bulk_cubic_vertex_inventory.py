#!/usr/bin/env python3
"""Audit the first cubic bulk vertex needed by a constitutive response.

The calculation is intentionally prior to a full ADM reduction.  It derives
the universal metric variation of the canonical scalar kinetic density,
checks it numerically on the reconstructed domain-wall background, and records
why the currently stored gauge-invariant quadratic profiles cannot yet be
inserted as cubic fields.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "bulk_cubic_vertex_inventory.json"

INPUTS = {
    "effective_action": REPO
    / "first_principles_audit/artifacts/holo_effective_action.json",
    "interface": REPO
    / "first_principles_audit/artifacts/interface_action_derivation.json",
    "stiff_force": HERE / "artifacts" / "stiff_boundary_force.json",
}


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


def densitized_inverse(metric: np.ndarray) -> np.ndarray:
    determinant = float(np.linalg.det(metric))
    if not determinant < 0.0:
        raise ValueError("metric must be Lorentzian with negative determinant")
    return math.sqrt(-determinant) * np.linalg.inv(metric)


def analytic_first_variation(
    metric: np.ndarray, perturbation: np.ndarray
) -> np.ndarray:
    inverse = np.linalg.inv(metric)
    trace = float(np.trace(inverse @ perturbation))
    raised = inverse @ perturbation @ inverse
    return math.sqrt(-float(np.linalg.det(metric))) * (
        0.5 * trace * inverse - raised
    )


def _variation_check(warp: float) -> dict[str, float]:
    conformal = math.exp(2.0 * warp)
    metric = np.diag([-conformal, conformal, conformal, conformal, 1.0])
    rng = np.random.default_rng(20260830)
    raw = rng.normal(size=(5, 5))
    perturbation = 0.5 * (raw + raw.T)
    perturbation /= np.linalg.norm(perturbation)
    analytic = analytic_first_variation(metric, perturbation)

    errors: list[float] = []
    steps = (2.0e-4, 1.0e-4, 5.0e-5)
    for step in steps:
        numeric = (
            densitized_inverse(metric + step * perturbation)
            - densitized_inverse(metric - step * perturbation)
        ) / (2.0 * step)
        errors.append(
            float(
                np.linalg.norm(numeric - analytic)
                / max(np.linalg.norm(analytic), 1.0e-300)
            )
        )
    return {
        "largest_step_relative_error": errors[0],
        "smallest_step_relative_error": errors[-1],
        "central_difference_error_ratio": errors[0] / errors[-1],
    }


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    effective = payloads["effective_action"]
    interface = payloads["interface"]
    stiff = payloads["stiff_force"]

    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action input is not certified")
    if interface.get("passes", {}).get("all") is not True:
        raise RuntimeError("interface input is not certified")
    if stiff.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff-force input is not certified")

    warp = np.asarray(effective["A"], dtype=float)
    variation = _variation_check(float(warp[warp.size // 2]))
    masses = np.asarray(
        stiff["spectrum_and_force"]["masses_mu"], dtype=float
    )
    heavy_inverse_mass_squared_moment = float(
        np.sum(1.0 / np.square(masses[1:]))
    )

    checks = {
        "certified_inputs": True,
        "no_observational_tables_read": True,
        "densitized_inverse_first_variation_verified": (
            variation["smallest_step_relative_error"] < 2.0e-8
            and variation["central_difference_error_ratio"] > 10.0
        ),
        "seven_stiff_masses_are_positive": bool(
            masses.size == 7 and np.all(masses > 0.0)
        ),
        "heavy_inverse_mass_squared_moment_is_positive": (
            heavy_inverse_mass_squared_moment > 0.0
        ),
        "fixed_metric_scalar_derivative_cubic_is_zero": True,
        "potential_cubic_is_derivative_free": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "adm_cubic_action_derived": False,
        "lapse_and_shift_solved_through_second_order": False,
        "brane_bending_and_boundary_cubic_terms_included": False,
        "nonlinear_map_from_stored_h_to_metric_and_delta_chi_derived": False,
        "quadratic_action_recovered_from_same_adm_variables": False,
        "physical_overlap_coefficients_c_a_computed": False,
        "direct_quartic_contact_operator_computed": False,
        "absolute_ell_and_kappa5_normalization_fixed": False,
        "modal_and_grid_convergence_of_C_Y2_passed": False,
    }
    physical_gates["physical_cubic_vertex_complete"] = all(
        physical_gates.values()
    )

    return {
        "schema": "holo.bulk-cubic-vertex-inventory.v1",
        "title": "First cubic vertex inventory for the HOLO constitutive sector",
        "classification": (
            "universal_raw_metric_scalar_vertex_derived;"
            "gauge_invariant_modal_coefficient_not_yet_computable"
        ),
        "action_convention": {
            "bulk": (
                "S5=(2*kappa5^2)^(-1)*integral sqrt(-G)*"
                "[R-(partial chi)^2/2-V(chi)]"
            ),
            "metric_split": "G_AB=Gbar_AB+h_AB; h=Gbar^AB*h_AB",
            "scalar_split": "chi=chibar+varphi",
        },
        "exact_first_variation": {
            "identity": (
                "delta[sqrt(-G) G^AB]=sqrt(-Gbar)*"
                "[h*Gbar^AB/2-h^AB]"
            ),
            "raw_derivative_cubic": (
                "S3_kin=-(4*kappa5^2)^(-1)*integral sqrt(-Gbar)*"
                "[h*Gbar^AB/2-h^AB]*partial_A(varphi)*partial_B(varphi)"
            ),
            "fixed_metric_result": (
                "Setting h_AB=0 removes every derivative cubic from the canonical "
                "scalar kinetic term exactly."
            ),
            "potential_cubic": (
                "S3_pot=-(12*kappa5^2)^(-1)*integral sqrt(-Gbar)*"
                "V'''(chibar)*varphi^3; it can generate sigma_a*pi^2 but not sigma_a*Y."
            ),
            "numerical_identity_check": variation,
        },
        "modal_reduction": {
            "desired_reduced_vertex": "sum_a c_a*sigma_a*Y",
            "heavy_mode_count": int(masses.size - 1),
            "heavy_masses_mu": masses[1:].tolist(),
            "unit_overlap_spectral_moment_sum_mu_inverse_squared": (
                heavy_inverse_mass_squared_moment
            ),
            "low_energy_result_if_c_a_were_known": (
                "For L=-P-0.5*sigma*K*sigma+c*sigma*Y: "
                "Delta L_exchange=+0.5*Y*c^T*K^(-1)*c*Y and "
                "Delta P_exchange=-0.5*Y*c^T*K^(-1)*c*Y"
            ),
            "total_quartic_coefficient": (
                "C_Y2_total=C_Y2_direct_S4-0.5*c^T*M^(-2)*c; its sign "
                "cannot be known from S3 alone"
            ),
            "locality_window": f"p*ell << mu_1={masses[1]:.12g}",
            "normalization_warning": (
                "The inverse-mass moment assumes unit overlaps and is not a physical "
                "coefficient. The c_a carry the ADM kernels and absolute normalization."
            ),
        },
        "projection_obstruction": {
            "stored_profiles": (
                "seven normalized quadratic profiles h_n(u) representing the "
                "reduced Boos scalar g=exp(-2*A_B)*h_44 on the stiff branch"
            ),
            "why_direct_insertion_is_invalid": (
                "The repository does not store the nonlinear reconstruction of "
                "h_AB, delta_chi, lapse, shift and brane bending in terms of h_n. "
                "Using h_n as any one raw perturbation would mix gauges and invent c_a."
            ),
            "required_reduction_order": [
                "choose one ADM gauge on the monotonic chi background",
                "expand Einstein-Hilbert, scalar and boundary actions to cubic order",
                "solve lapse and shift constraints consistently",
                "recover the certified quadratic operator and normalization",
                "project the remaining cubic action onto the same h_n basis",
            ],
        },
        "physical_gates": physical_gates,
        "checks": checks,
        "inputs": {
            "observational_tables_read": [],
            "files": {
                name: {
                    "path": str(path.relative_to(REPO)),
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
        },
        "next_output_contract": {
            "current_status": (
                "BLOCKED_MISSING_PHYSICAL_GAUGE_INVARIANT_CUBIC_VERTEX"
            ),
            "whitelist": [
                "holo_effective_action.json",
                "superpotential_boundary_completion.json",
                "stiff_boundary_force.json",
                "future gauge-invariant ADM cubic reduction with empty observational inputs",
            ],
            "forbidden_inputs": ["SPARC", "collector", "RAR", "a0", "galaxy scores"],
            "nested_mode_counts": {
                "N3": "light mode plus 2 heavy modes",
                "N5": "light mode plus 4 heavy modes",
                "N7": "light mode plus 6 heavy modes",
            },
            "grid_strides": {"coarse": 4, "medium": 2, "fine": 1},
            "calculation_rule": (
                "Use the same seven-mode solve and nested prefixes; compute "
                "E_N=0.5*c^T*solve(M2,c), never an explicit inverse. E_N is "
                "positive in Delta L and negative in Delta P; combine it with "
                "the independently derived direct S4 contact."
            ),
            "pre_registered_gates": {
                "quadratic_gram_max_abs": 1.0e-9,
                "quadratic_backward_residual_max": 1.0e-11,
                "mode_matching_MAC_min": 0.999,
                "constraint_residual_max": 1.0e-8,
                "pure_gauge_overlap_fraction_max": 1.0e-7,
                "integration_by_parts_relative_error_max": 1.0e-5,
                "mixed_derivative_vertex_relative_error_max": 1.0e-4,
                "fine_medium_c_and_C_relative_change_max": 0.02,
                "fine_coarse_c_and_C_relative_change_max": 0.05,
                "C7_minus_C5_over_C7_max": 0.05,
                "solve_vs_diagonalization_relative_error_max": 1.0e-10,
                "phase_flip_C_relative_error_max": 1.0e-12,
                "local_kernel_at_p_over_m1_0p1_relative_error_max": 0.01,
                "peak_arrays_mib_max": 8.0,
            },
            "classification_if_all_gates_pass": (
                "finite_gapped_S3_exchange_generates_analytic_Y2_with_negative_"
                "P_sign;total_Y2_sign_requires_direct_S4;not_Y_three_halves"
            ),
            "required_arrays": [
                "u",
                "c_a by mode",
                "integrand decomposition by ADM kernel",
                "S3 exchange E_N on 3, 5 and 7 mode truncations",
                "direct S4 contact and total C_Y2 separately",
                "full, half and quarter grid comparisons",
            ],
            "decisive_gate": (
                "No constitutive bulk claim is allowed until the same ADM reducer "
                "reproduces S2 before reporting S3."
            ),
        },
        "software": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    moment = result["modal_reduction"][
        "unit_overlap_spectral_moment_sum_mu_inverse_squared"
    ]
    print(f"[artifact] {OUTPUT}")
    print(f"[raw cubic identity] {'PASS' if result['checks']['all'] else 'FAIL'}")
    print(f"[unit-overlap heavy moment] {moment:.12g}")
    print(
        "[physical cubic completion] "
        f"{result['physical_gates']['physical_cubic_vertex_complete']}"
    )
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
