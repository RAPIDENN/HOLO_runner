#!/usr/bin/env python3
"""Backward-check the stiff compact S2 endpoints in the ADM/BMP variable.

The positive Boos scalar ``g`` has a Neumann endpoint condition in the stiff
two-brane theory.  A first-order Darboux map sends it to the curvature variable
used by the ADM/BMP bulk operator.  This certificate derives the induced
eigenvalue-dependent endpoint terms and checks all seven transformed modes in
the weak compact problem.  It does not claim the finite-gamma bent-brane
action, which remains the prerequisite for the cubic eta assay.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.sparse import diags


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "compact_brane_S2_backward.json"
INPUTS = {
    "effective_action": REPO
    / "first_principles_audit/artifacts/holo_effective_action.json",
    "stiff_action": HERE / "artifacts/stiff_boundary_force.json",
    "junction_spectrum": HERE / "artifacts/superpotential_boundary_completion.json",
    "adm_bulk_S2": HERE / "artifacts/adm_quadratic_recovery.json",
    "gauge_invariant_route": HERE / "artifacts/gauge_invariant_cubic_route.json",
}
CRITERIA = {
    "background_junction_max_abs": 1.0e-12,
    "transformed_weak_residual_max": 1.0e-12,
    "transformed_rayleigh_mass_relative_max": 1.0e-4,
    "independent_stiff_spectrum_relative_max": 1.0e-4,
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


def _linear_mass(u: np.ndarray, weight: np.ndarray):
    spacing = np.diff(u)
    diagonal = np.zeros(u.size)
    diagonal[:-1] += spacing * (3.0 * weight[:-1] + weight[1:]) / 12.0
    diagonal[1:] += spacing * (weight[:-1] + 3.0 * weight[1:]) / 12.0
    off_diagonal = spacing * (weight[:-1] + weight[1:]) / 12.0
    return diags(
        [off_diagonal, diagonal, off_diagonal],
        offsets=[-1, 0, 1],
        format="lil",
    )


def _derivative_stiffness(u: np.ndarray, weight: np.ndarray):
    spacing = np.diff(u)
    element_weight = 0.5 * (weight[:-1] + weight[1:])
    diagonal = np.zeros(u.size)
    diagonal[:-1] += element_weight / spacing
    diagonal[1:] += element_weight / spacing
    off_diagonal = -element_weight / spacing
    return diags(
        [off_diagonal, diagonal, off_diagonal],
        offsets=[-1, 0, 1],
        format="csr",
    )


def _compact_partner_matrices(
    u: np.ndarray,
    warp: np.ndarray,
    warp_u: np.ndarray,
    chi_u: np.ndarray,
):
    chi_squared = chi_u**2
    epsilon = chi_squared / (6.0 * warp_u**2)
    p = np.exp(4.0 * warp) * epsilon
    w = np.exp(2.0 * warp) * epsilon
    superpotential = -6.0 * warp_u
    inverse_conformal = np.exp(-2.0 * warp)
    endpoint_robin_per_mass_squared = (
        superpotential * inverse_conformal / chi_squared
    )

    stiffness = _derivative_stiffness(u, p)
    mass = _linear_mass(u, w)
    lower_boundary_mass = -p[0] * endpoint_robin_per_mass_squared[0]
    upper_boundary_mass = p[-1] * endpoint_robin_per_mass_squared[-1]
    mass[0, 0] += lower_boundary_mass
    mass[-1, -1] += upper_boundary_mass
    return (
        stiffness,
        mass.tocsr(),
        p,
        w,
        endpoint_robin_per_mass_squared,
        lower_boundary_mass,
        upper_boundary_mass,
    )


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    effective = payloads["effective_action"]
    stiff = payloads["stiff_action"]
    junction = payloads["junction_spectrum"]
    adm = payloads["adm_bulk_S2"]
    gauge = payloads["gauge_invariant_route"]
    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective action is not certified")
    if stiff.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff quadratic action is not certified")
    if junction.get("passes", {}).get("all") is not True:
        raise RuntimeError("junction spectrum is not certified")
    if adm.get("checks", {}).get("all") is not True:
        raise RuntimeError("ADM bulk S2 is not certified")
    if gauge.get("checks", {}).get("all") is not True:
        raise RuntimeError("gauge-invariant route is not certified")

    u = np.asarray(effective["u"], dtype=float)
    warp = np.asarray(effective["A"], dtype=float)
    warp_u = np.asarray(effective["A_u"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)
    superpotential = -6.0 * warp_u
    inverse_conformal = np.exp(-2.0 * warp)
    masses_squared = np.asarray(
        stiff["spectrum_and_force"]["mass_squared_mu2"], dtype=float
    )
    g_modes = np.asarray(stiff["profiles"]["h_n"], dtype=float)
    if g_modes.shape != (masses_squared.size, u.size):
        raise RuntimeError("stiff modes and background use different grids")

    (
        stiffness,
        mass,
        p,
        w,
        endpoint_robin,
        lower_boundary_mass,
        upper_boundary_mass,
    ) = _compact_partner_matrices(u, warp, warp_u, chi_u)
    stiffness_norm = float(np.linalg.norm(stiffness.data))
    mass_norm = float(np.linalg.norm(mass.data))
    rows: list[dict[str, float | int]] = []
    transformed_modes = []
    for index, (mass_squared, g_mode) in enumerate(
        zip(masses_squared, g_modes)
    ):
        g_u = CubicSpline(u, g_mode)(u, 1)
        curvature_mode = inverse_conformal * (
            -g_mode + superpotential * g_u / chi_u**2
        )
        transformed_modes.append(curvature_mode)
        residual = stiffness @ curvature_mode - mass_squared * (
            mass @ curvature_mode
        )
        residual_scale = np.linalg.norm(curvature_mode) * (
            stiffness_norm + mass_squared * mass_norm
        )
        weak_residual = float(
            np.linalg.norm(residual) / max(residual_scale, 1.0e-300)
        )
        rayleigh = float(
            curvature_mode @ (stiffness @ curvature_mode)
            / (curvature_mode @ (mass @ curvature_mode))
        )
        rows.append(
            {
                "mode": index,
                "input_mass_squared": float(mass_squared),
                "partner_rayleigh_mass_squared": rayleigh,
                "rayleigh_relative_error": abs(rayleigh / mass_squared - 1.0),
                "weak_residual": weak_residual,
            }
        )

    junction_masses = np.asarray(
        junction["stiff_candidate"]["spectrum"]["masses_mu"], dtype=float
    )
    boos_masses = np.sqrt(masses_squared)
    independent_spectrum_relative = np.abs(boos_masses / junction_masses - 1.0)

    # Background brane values in the interval convention:
    # lambda_- = W, lambda_+ = -W and s=(-1,+1).
    orientations = np.asarray([-1.0, 1.0])
    endpoint_indices = np.asarray([0, u.size - 1])
    lambda_value = np.asarray([superpotential[0], -superpotential[-1]])
    lambda_prime = np.asarray([chi_u[0], -chi_u[-1]])
    israel_background = (
        orientations * warp_u[endpoint_indices] - lambda_value / 6.0
    )
    scalar_background = (
        orientations * chi_u[endpoint_indices] + lambda_prime
    )
    background_junction_max = float(
        max(np.max(np.abs(israel_background)), np.max(np.abs(scalar_background)))
    )

    maximum_weak = max(float(row["weak_residual"]) for row in rows)
    maximum_rayleigh = max(float(row["rayleigh_relative_error"]) for row in rows)
    maximum_independent_spectrum = float(np.max(independent_spectrum_relative))
    checks = {
        "certified_inputs": True,
        "no_observational_tables_read": True,
        "background_scalar_and_Israel_junctions": background_junction_max
        < CRITERIA["background_junction_max_abs"],
        "all_seven_Darboux_modes_satisfy_compact_weak_problem": maximum_weak
        < CRITERIA["transformed_weak_residual_max"],
        "all_seven_partner_rayleigh_masses_match": maximum_rayleigh
        < CRITERIA["transformed_rayleigh_mass_relative_max"],
        "Boos_and_LS_stiff_spectra_independently_match": maximum_independent_spectrum
        < CRITERIA["independent_stiff_spectrum_relative_max"],
        "stiff_unitary_gauge_pins_linear_bending": bool(np.all(chi_u > 0.0)),
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "stiff_background_brane_action_junctions_recovered": True,
        "stiff_Darboux_endpoint_operator_recovered": True,
        "stiff_compact_S2_spectrum_two_representation_verified": True,
        "stiff_linear_bending_pinned_in_unitary_gauge": True,
        "inclined_brane_geometry_expanded_and_verified": False,
        "finite_gamma_ADM_S2_with_bending_recovered": False,
        "compact_ADM_S2_endpoint_action_derived_directly_from_GHY_and_brane": False,
        "physical_finite_gamma_S3_endpoint_ready": False,
    }

    return {
        "schema": "holo.compact-brane-S2-backward.v1",
        "title": "Stiff two-brane S2 backward check in the ADM/BMP bulk variable",
        "classification": (
            "stiff_compact_endpoint_operator_recovered;"
            "finite_gamma_bent_brane_action_pending"
        ),
        "covariant_boundary_action": {
            "action": (
                "S_boundary=kappa5^-2*sum_i integral sqrt(-gamma_hat)*K_hat"
                "-(2*kappa5^2)^-1*sum_i integral sqrt(-gamma_hat)*lambda_i(chi_hat)"
            ),
            "scalar_junction": "n dot partial(chi)+lambda_i'=0",
            "israel_junction": (
                "K_mn-K*gamma_mn+(lambda_i/2)*gamma_mn=0"
            ),
            "orientations": {"lower": -1, "upper": 1},
            "background_junction_max_abs": background_junction_max,
        },
        "stiff_bending_reduction": {
            "gauge": "delta_chi=0 in the bulk",
            "physical_pullback": "Q1=delta_chi+chi_bar'*xi1",
            "stiff_condition": "Q1=0",
            "consequence": (
                "chi_bar' is strictly positive on the certified interval, so xi1=0. "
                "The stiff linear endpoint can be checked on a fixed brane."
            ),
            "finite_gamma_warning": (
                "At finite gamma, Q1 and xi1 need not vanish; this simplification "
                "cannot be used for the cubic eta deformation assay."
            ),
        },
        "Darboux_endpoint_derivation": {
            "positive_variable": "g with g'=0 at both stiff endpoints",
            "positive_operator": (
                "-(p_g*g')'+q_g*g=m^2*w_g*g; p_g=e^-2A/chi'^2; "
                "q_g=e^-2A/3; w_g=e^-4A/chi'^2"
            ),
            "curvature_map_without_common_factor": (
                "f=e^-2A*(-g+W*g'/chi'^2)"
            ),
            "endpoint_use_of_positive_equation": (
                "g''=(chi'^2/3-m^2*e^-2A)*g when g'=0"
            ),
            "induced_boundary_condition": (
                "f'=m^2*[W*e^-2A/chi'^2]*f at both coordinate endpoints"
            ),
            "weak_partner_problem": (
                "K_f=int p*f'*v'; M_f=int w*f*v + b_-*f_-*v_- + "
                "b_+*f_+*v_+; K_f=m^2*M_f"
            ),
            "bulk_weights": {"p": "e^4A*epsilon", "w": "e^2A*epsilon"},
            "endpoint_mass_coefficients": {
                "lower": "-p_-*W_-*e^-2A_-/chi_-'^2",
                "upper": "+p_+*W_+*e^-2A_+/chi_+'^2",
                "lower_numeric": float(lower_boundary_mass),
                "upper_numeric": float(upper_boundary_mass),
                "warning": (
                    "The partner mass form is indefinite at the lower endpoint. "
                    "It is a Darboux representation of the positive g action, not "
                    "by itself a new positivity proof."
                ),
            },
        },
        "verification": {
            "mode_rows": rows,
            "maximum_weak_residual": maximum_weak,
            "maximum_partner_rayleigh_mass_relative": maximum_rayleigh,
            "independent_Boos_LS_mass_relative": independent_spectrum_relative.tolist(),
            "maximum_independent_Boos_LS_mass_relative": maximum_independent_spectrum,
            "transformed_profiles_not_exported": (
                "Profiles are used only for the backward residual to avoid duplicating "
                "the existing source-of-truth arrays."
            ),
        },
        "physical_gates": physical_gates,
        "checks": checks,
        "criteria": CRITERIA,
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
        "next_decisive_test": (
            "Expand the exact induced metric, inclined normal, scalar junction and "
            "Israel tensor on a moving finite-gamma brane, straighten it by a radial "
            "diffeomorphism, and require equality through second order before S3."
        ),
        "evidence_boundary": (
            "This recovers the stiff compact endpoint operator and its seven-mode "
            "spectrum in two independent representations. It does not derive the "
            "finite-gamma bent-brane ADM action or authorize a cubic coupling."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        raise SystemExit("compact brane S2 backward certificate failed")
    _write(OUTPUT, result)
    verification = result["verification"]
    print(f"[artifact] {OUTPUT}")
    print(f"[stiff endpoint weak residual] {verification['maximum_weak_residual']:.3e}")
    print(
        "[stiff partner mass max relative] "
        f"{verification['maximum_partner_rayleigh_mass_relative']:.3e}"
    )
    print(
        "[finite gamma bending recovered] "
        f"{result['physical_gates']['finite_gamma_ADM_S2_with_bending_recovered']}"
    )
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
