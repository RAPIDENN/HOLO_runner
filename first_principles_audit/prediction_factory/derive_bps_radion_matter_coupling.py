#!/usr/bin/env python3
"""Test the matter coupling of the real Einstein--dilaton BPS radion.

The functional-BPS branch contains a static modulus: keep the lower endpoint
``u_-`` fixed and slide the upper endpoint ``R`` along the same first-order
flow.  At zero four-dimensional derivatives the coefficient of the 4D Ricci
scalar is

    F(R) = integral_{u_-}^{R} exp(2 A(u)) du.

Consequently the Einstein metric is ``g_E = F(R)/F(R0) g_4`` and minimally
localized matter sees

    gamma_i = A_i(R)^2 g_E,
    A_i(R)^2 = exp(2 A(y_i(R))) F(R0)/F(R).

This certificate evaluates that exact matter metric on the real 1,979-point
reconstructed background along a declared one-dimensional separation slice.
It asks the decisive structural question before attempting a mixed S4
calculation: is the normalized Jordan curvature selector
``C_i=A_i(R0)^2/A_i(R)^2`` stationary on this slice?  If it is not, a regular
canonical reparametrization of this slice cannot make its leading matter
response even in the radion.

The calculation does not identify the full constraint-reduced quasistatic
coefficient with ``C_i``.  It instead supplies a necessary no-odd-coupling
test.  Failure rules out deriving a leading pure q^2 Y vertex on the declared
minimal separation slice, while avoiding the stronger and unjustified claims
that a complete qY coefficient or a unique one-field truncation has already
been computed.  A general scalar BPS two-brane system can have two moduli; the
orthogonal mode must be fixed before a unique canonical q exists.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import cumulative_trapezoid


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
EFFECTIVE_ACTION = (
    REPO / "first_principles_audit/artifacts/holo_effective_action.json"
)
BPS_CERTIFICATE = HERE / "artifacts/adm_bmp_tricritical_necessity.json"
OUTPUT = HERE / "artifacts/bps_radion_matter_coupling.json"

CRITERIA = {
    "background_samples": 1979,
    "einstein_frame_identity_max_abs": 5.0e-15,
    "local_fit_first_derivative_relative_max": 1.0e-5,
    "local_fit_quadratic_coefficient_relative_max": 2.0e-5,
    "linear_selector_derivative_abs_min": 1.0e-8,
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


def _relative_error(measured: float, expected: float) -> float:
    return abs(measured - expected) / max(abs(expected), 1.0e-300)


def _endpoint_polynomial_coefficients(
    u: np.ndarray, values: np.ndarray, points: int = 12
) -> tuple[float, float]:
    """Independently fit C=1+c1*dR+c2*dR^2+... at the upper endpoint."""

    offset = u[-points:] - u[-1]
    coefficients = np.polynomial.polynomial.polyfit(
        offset, values[-points:], deg=5
    )
    return float(coefficients[1]), float(coefficients[2])


def build() -> dict[str, Any]:
    effective = _read(EFFECTIVE_ACTION)
    bps = _read(BPS_CERTIFICATE)
    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action background is not certified")
    if bps.get("checks", {}).get("all") is not True:
        raise RuntimeError("real-background BPS certificate must pass first")

    u = np.asarray(effective["u"], dtype=float)
    warp = np.asarray(effective["A"], dtype=float)
    warp_u = np.asarray(effective["A_u"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)
    arrays = (u, warp, warp_u, chi_u)
    if not (
        u.size == CRITERIA["background_samples"]
        and all(array.shape == u.shape for array in arrays)
        and all(np.all(np.isfinite(array)) for array in arrays)
        and np.all(np.diff(u) > 0.0)
        and np.all(warp_u < 0.0)
        and np.all(chi_u > 0.0)
    ):
        raise ValueError("invalid reconstructed Einstein--dilaton background")

    exp_2A = np.exp(2.0 * warp)
    planck_integral = cumulative_trapezoid(exp_2A, u, initial=0.0)
    F0 = float(planck_integral[-1])
    if not F0 > 0.0:
        raise RuntimeError("four-dimensional Planck integral is not positive")

    # Weyl factor g_4=(F0/F) g_E.  The first node has F=0 and is only the
    # degenerate zero-length interval, so frame identities are tested for R>u_-.
    valid = planck_integral > 0.0
    einstein_weyl_squared = np.full_like(planck_integral, np.nan)
    einstein_weyl_squared[valid] = F0 / planck_integral[valid]
    einstein_coefficient = (
        planck_integral[valid] * einstein_weyl_squared[valid] / F0
    )
    einstein_identity_error = float(
        np.max(np.abs(einstein_coefficient - 1.0))
    )

    # Normalize the Jordan curvature selector at the reference endpoint.  A
    # constant normalization is immaterial for the stationarity test.
    lower_selector = planck_integral / F0
    upper_selector = lower_selector * np.exp(-2.0 * (warp - warp[-1]))

    endpoint_ratio = float(exp_2A[-1] / F0)
    lower_endpoint_ratio = float(exp_2A[0] / F0)
    endpoint_A_u = float(warp_u[-1])
    lower_endpoint_A_u = float(warp_u[0])
    endpoint_A_uu = float(-chi_u[-1] ** 2 / 6.0)

    # C_-=F/F0.
    lower_c1 = endpoint_ratio
    lower_c2 = endpoint_A_u * endpoint_ratio

    # C_+=(F/F0) exp[-2(A(R)-A(R0))].  Coefficients refer to
    # C=1+c1*dR+c2*dR^2+O(dR^3), where R is the dimensionless domain-wall
    # coordinate.  Their magnitudes acquire powers of ell^-1 in physical units.
    upper_log_c1 = endpoint_ratio - 2.0 * endpoint_A_u
    upper_log_c2_derivative = (
        2.0 * endpoint_A_u * endpoint_ratio
        - endpoint_ratio**2
        - 2.0 * endpoint_A_uu
    )
    upper_c1 = upper_log_c1
    upper_c2 = 0.5 * (
        upper_log_c1**2 + upper_log_c2_derivative
    )

    lower_fit_c1, lower_fit_c2 = _endpoint_polynomial_coefficients(
        u, lower_selector
    )
    upper_fit_c1, upper_fit_c2 = _endpoint_polynomial_coefficients(
        u, upper_selector
    )
    fit_errors = {
        "lower_first_relative": _relative_error(lower_fit_c1, lower_c1),
        "lower_quadratic_relative": _relative_error(lower_fit_c2, lower_c2),
        "upper_first_relative": _relative_error(upper_fit_c1, upper_c1),
        "upper_quadratic_relative": _relative_error(upper_fit_c2, upper_c2),
    }

    # delta S_m=sqrt(-gamma) alpha_i T_i delta R.  Here alpha_i is the
    # derivative of ln(A_i), not of its square.
    lower_trace_alpha = -0.5 * endpoint_ratio
    upper_trace_alpha = endpoint_A_u - 0.5 * endpoint_ratio

    # Coordinate gradients in the complete two-endpoint chart (Y_-,Y_+).
    # These do not yet canonically normalize the two moduli, but they expose
    # exactly which tangent selection would be required to remove the odd
    # matter response.  A tangent is normalized only by
    # d(Y_+-Y_-)=1; this is not a kinetic normalization.
    selector_gradients = np.asarray(
        [
            [-lower_endpoint_ratio - 2.0 * lower_endpoint_A_u, endpoint_ratio],
            [-lower_endpoint_ratio, endpoint_ratio - 2.0 * endpoint_A_u],
        ],
        dtype=float,
    )
    gradient_determinant = float(np.linalg.det(selector_gradients))
    orthogonal_separation_tangents = []
    orthogonality_residuals = []
    for gradient in selector_gradients:
        tangent_lower = float(-gradient[1] / np.sum(gradient))
        tangent = np.asarray([tangent_lower, tangent_lower + 1.0])
        orthogonal_separation_tangents.append(tangent.tolist())
        orthogonality_residuals.append(float(gradient @ tangent))

    ratio_along_grid = np.full_like(planck_integral, np.nan)
    ratio_along_grid[valid] = exp_2A[valid] / planck_integral[valid]
    lower_log_selector_derivative = ratio_along_grid[valid]
    upper_log_selector_derivative = (
        ratio_along_grid[valid] - 2.0 * warp_u[valid]
    )

    first_derivatives = (lower_c1, upper_c1)
    checks = {
        "certified_real_background_used": u.size
        == CRITERIA["background_samples"],
        "conditional_functional_BPS_branch_used": bps["flatness_theorem"][
            "result"
        ]
        == "V_eff(R)=0 identically",
        "einstein_frame_planck_coefficient_is_constant": einstein_identity_error
        < CRITERIA["einstein_frame_identity_max_abs"],
        "lower_selector_is_strictly_monotone": bool(
            np.all(np.diff(lower_selector) > 0.0)
        ),
        "upper_selector_is_strictly_monotone": bool(
            np.all(np.diff(upper_selector) > 0.0)
        ),
        "analytic_first_derivatives_match_local_fit": bool(
            max(
                fit_errors["lower_first_relative"],
                fit_errors["upper_first_relative"],
            )
            < CRITERIA["local_fit_first_derivative_relative_max"]
        ),
        "analytic_quadratic_coefficients_match_local_fit": bool(
            max(
                fit_errors["lower_quadratic_relative"],
                fit_errors["upper_quadratic_relative"],
            )
            < CRITERIA["local_fit_quadratic_coefficient_relative_max"]
        ),
        "minimal_lower_matter_has_nonzero_linear_response": abs(lower_c1)
        > CRITERIA["linear_selector_derivative_abs_min"],
        "minimal_upper_matter_has_nonzero_linear_response": abs(upper_c1)
        > CRITERIA["linear_selector_derivative_abs_min"],
        "linear_trace_vertex_nonzero_on_both_endpoints": bool(
            lower_trace_alpha != 0.0 and upper_trace_alpha != 0.0
        ),
        "two_endpoint_matter_gradients_are_independent": bool(
            abs(gradient_determinant) > 1.0e-8
        ),
        "candidate_single_brane_orthogonal_tangents_close": bool(
            max(abs(value) for value in orthogonality_residuals) < 1.0e-12
        ),
        "no_observational_tables_read": True,
    }
    checks["all"] = all(checks.values())

    return {
        "schema": "holo.bps-radion-matter-coupling.v1",
        "title": "Real-background BPS radion induced-matter metric test",
        "classification": (
            "declared_separation_slice_has_odd_minimal_matter_response;"
            "leading_pure_q2Y_not_derived"
        ),
        "fixed_reduction": {
            "declared_moduli_slice": (
                "lower endpoint u_- fixed; upper endpoint R slides along the "
                "same functional-BPS Einstein--dilaton flow"
            ),
            "four_dimensional_curvature_coefficient": (
                "F(R)=integral_[u_-,R] exp(2A(u)) du"
            ),
            "einstein_frame_map": "g_E=[F(R)/F(R0)]*g_4",
            "induced_matter_metric": (
                "gamma_i=A_i(R)^2*g_E; A_i^2=exp(2A(y_i))*F(R0)/F(R)"
            ),
            "normalized_jordan_selector": (
                "C_i(R)=A_i(R0)^2/A_i(R)^2; C_i(R0)=1"
            ),
            "endpoint_positions": {"lower": "y_-=u_-", "upper": "y_+=R"},
        },
        "analytic_stationarity_theorem": {
            "definitions": "E=exp(2A(R))>0; F>0; A'(R)<0",
            "lower": "C_-=F/F0, so C_-'=E/F0>0",
            "upper": (
                "C_+=(F/F0) exp[-2(A-A0)], so "
                "d_R ln C_+=E/F-2A'>0"
            ),
            "consequence": (
                "Neither minimally induced endpoint matter metric has an "
                "extremum anywhere on the certified monotone branch."
            ),
            "regular_canonical_reparametrization": (
                "dC/dq=(dC/dR)(dR/dq); finite nonzero dR/dq cannot turn "
                "the nonzero first derivative into C_Y'(0)=0 on this slice"
            ),
        },
        "full_moduli_space_gate": {
            "candidate_bulk_zero_modes": bps["massless_kernel"][
                "candidate_bulk_zero_mode_count"
            ],
            "general_functional_BPS_system_may_be_biscalar": True,
            "finite_endpoint_moduli_metric_derived_here": False,
            "orthogonal_modulus_fixed_or_stabilized": False,
            "unique_canonical_q_selected": False,
            "required_projection": (
                "derive the finite-endpoint positive moduli metric G_ab, fix or "
                "stabilize the orthogonal direction, and test "
                "e_q^a*partial_a ln(A_m)=0 for the retained canonical tangent"
            ),
            "coordinate_gradients_d_ln_C_d_Yminus_d_Yplus": {
                "lower_matter": selector_gradients[0].tolist(),
                "upper_matter": selector_gradients[1].tolist(),
                "determinant": gradient_determinant,
            },
            "candidate_tangents_with_d_separation_equal_one": {
                "lower_matter_stationary": orthogonal_separation_tangents[0],
                "upper_matter_stationary": orthogonal_separation_tangents[1],
                "orthogonality_residuals": orthogonality_residuals,
                "selected_by_current_action": False,
                "canonically_normalized": False,
            },
            "simultaneous_stationarity": (
                "The two matter gradients have nonzero determinant, so no "
                "nonzero tangent makes both endpoint metrics stationary."
            ),
            "logical_scope": (
                "The nonzero result is a counterexample to geometric necessity "
                "and a no-go for the declared separation slice; it is not a "
                "no-go for every deliberately selected tangent in a two-"
                "dimensional moduli space."
            ),
        },
        "actual_background": {
            "samples": int(u.size),
            "u_domain": [float(u[0]), float(u[-1])],
            "F_R0": F0,
            "exp_2A_endpoints": [float(exp_2A[0]), float(exp_2A[-1])],
            "A_u_upper": endpoint_A_u,
            "A_uu_upper_from_flow": endpoint_A_uu,
            "E_over_F_upper": endpoint_ratio,
            "E_over_F_lower": lower_endpoint_ratio,
            "minimum_lower_log_selector_derivative": float(
                np.min(lower_log_selector_derivative)
            ),
            "minimum_upper_log_selector_derivative": float(
                np.min(upper_log_selector_derivative)
            ),
        },
        "endpoint_expansions_in_delta_R": {
            "convention": "C_i=1+c1*delta_R+c2*delta_R^2+O(delta_R^3)",
            "lower": {
                "c1": lower_c1,
                "c2": lower_c2,
                "local_fit_c1": lower_fit_c1,
                "local_fit_c2": lower_fit_c2,
            },
            "upper": {
                "c1": upper_c1,
                "c2": upper_c2,
                "local_fit_c1": upper_fit_c1,
                "local_fit_c2": upper_fit_c2,
            },
            "warning": (
                "Because c1 is nonzero and the canonical map q(R) is not yet "
                "fixed, c2 is a delta_R diagnostic, not the physical q^2Y "
                "coefficient. The nonzero-c1 verdict is invariant."
            ),
        },
        "linear_matter_vertex": {
            "variation": (
                "delta S_m=int sqrt(-gamma_i)*alpha_i*T_i*delta R; "
                "alpha_i=d_R ln A_i"
            ),
            "alpha_lower_per_dimensionless_R": lower_trace_alpha,
            "alpha_upper_per_dimensionless_R": upper_trace_alpha,
            "physical_units": "alpha_physical=alpha_dimensionless/ell",
            "massive_matter_trace": "nonzero linear radion coupling",
            "four_dimensional_conformal_radiation": (
                "T=0 is an exception and cannot source the requested massive-"
                "matter force"
            ),
        },
        "q2Y_gate": {
            "necessary_even_matter_metric_condition": "C_Y'(0)=0",
            "declared_separation_slice_minimal_lower_brane_passes": False,
            "declared_separation_slice_minimal_upper_brane_passes": False,
            "some_unselected_two_modulus_tangent_can_kill_one_first_jet": True,
            "same_nonzero_tangent_can_kill_both_endpoint_first_jets": False,
            "q_to_minus_q_symmetry_derived": False,
            "pure_leading_q2Y_from_minimal_endpoint_matter": False,
            "full_constraint_reduced_qY_coefficient_computed": False,
            "q2Y_derived": False,
            "decision": (
                "Stop before interpreting C_Y'' as the desired vertex: the "
                "minimally induced matter metric already contains a nonzero "
                "odd response along the declared separation slice."
            ),
        },
        "what_would_be_new_physics": {
            "upper_local_conformal_tuning": (
                "For gamma_m=B(chi_+)^2*gamma_+, stationarity requires "
                "d_R ln B^(-2)=2A'-E/F, equivalently cancellation of the "
                "displayed upper selector derivative. This function is not "
                "selected by the present bulk action."
            ),
            "lower_brane_obstruction": (
                "A local function of chi_- is constant while only the upper "
                "endpoint slides, so it cannot cancel F'(R)/F(R)."
            ),
            "symmetry_route": (
                "An exact brane-exchange or q->-q symmetry could forbid the "
                "odd term, but the certified branch is monotone and its two "
                "endpoints are not exchange symmetric."
            ),
            "projection_route": (
                "In a multi-modulus theory an even candidate direction must "
                "satisfy e_q^a*partial_a ln(A_m)=0 and every orthogonal mode "
                "must be stabilized. The present geometry does not select "
                "such a tangent."
            ),
            "sextic_detuning_relation": (
                "The rho_i*X_i^6 deformation leaves the background and its "
                "first five jets unchanged, so it cannot cancel this linear "
                "matter response."
            ),
        },
        "negative_control": {
            "omission": "drop the Einstein-frame factor F(R0)/F(R)",
            "false_result": (
                "matter on the fixed lower brane then appears independent of R"
            ),
            "why_invalid": (
                "the four-dimensional Ricci coefficient remains F(R), so the "
                "putative metric is not in Einstein frame"
            ),
            "missed_log_derivative": endpoint_ratio,
        },
        "checks": checks,
        "criteria": CRITERIA,
        "fit_errors": fit_errors,
        "inputs": {
            "observational_tables_read": [],
            "files": {
                "effective_action": {
                    "path": str(EFFECTIVE_ACTION.relative_to(REPO)),
                    "sha256": _sha256(EFFECTIVE_ACTION),
                },
                "BPS_certificate": {
                    "path": str(BPS_CERTIFICATE.relative_to(REPO)),
                    "sha256": _sha256(BPS_CERTIFICATE),
                },
            },
        },
        "evidence_boundary": (
            "This is an exact static-moduli induced-metric result inside the "
            "conditional functional-BPS branch, evaluated on the real ED "
            "background. It rules out a leading purely even radion coupling "
            "for minimally localized endpoint matter along the declared "
            "separation slice and shows that geometry does not force "
            "C_Y'(0)=0. It does not select the canonical tangent in the full "
            "possibly bi-scalar moduli space, compute the full lapse/shift-"
            "reduced qY coefficient, select a nonminimal matter metric, or "
            "establish an observed force."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        failed = [key for key, value in result["checks"].items() if not value]
        raise SystemExit(f"BPS radion matter-metric certificate failed: {failed}")
    _write(OUTPUT, result)
    expansions = result["endpoint_expansions_in_delta_R"]
    print(f"[artifact] {OUTPUT}")
    print(f"[real background samples] {result['actual_background']['samples']}")
    print(
        "[selector c1] lower={:.12g} upper={:.12g}".format(
            expansions["lower"]["c1"], expansions["upper"]["c1"]
        )
    )
    print("[minimal endpoint matter C_Y'(0)=0] False")
    print("[q2Y derived] False")
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
