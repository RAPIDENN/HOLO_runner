#!/usr/bin/env python3
"""Audit a *candidate* fixed-warped-volume selector on the real BPS branch.

The existing two-modulus certificate defines

    F(y) = integral_[u_-,u_+] exp(2A) du,
    C_i = (F/F0) exp[-2(A_i-A_i0)].

This module asks a deliberately conditional question: if new physics imposed
``delta F=0``, which Khat-unit tangent would remain, and how closely would it
agree with ``ker dC_i``?  No top-form, Lagrange multiplier, or other global-F
constraint exists in the current repository theory.  None is invented here.
Consequently the calculation is a geometric candidate certificate, not an
action derivation, a force prediction, or a physical q^2 Y vertex.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np

try:
    from first_principles_audit.prediction_factory import (
        derive_bps_biscalar_matter_geometry as biscalar,
    )
except ModuleNotFoundError:
    import derive_bps_biscalar_matter_geometry as biscalar


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts/bps_volume_constraint_selector.json"

CRITERIA = {
    "volume_tangent_residual_max": 1.0e-14,
    "metric_unit_residual_max": 1.0e-13,
    "selector_residual_identity_max": 1.0e-12,
    "angle_identity_max": 1.0e-12,
    "alignment_determinant_identity_max": 1.0e-12,
    "lower_near_alignment_angle_degrees_max": 0.1,
    "upper_misalignment_angle_degrees_min": 80.0,
    "alignment_limit_metric_min_eigenvalue": 1.0e-6,
    "alignment_limit_curvature_negative_max": -1.0e-8,
    "level_set_curvature_positive_min": 1.0e-8,
    "level_set_curvature_identity_max": 1.0e-12,
    "level_set_kinematic_residual_max": 1.0e-12,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _unit_kernel_tangent(metric: np.ndarray, covector: np.ndarray) -> np.ndarray:
    """Return the positively oriented unit tangent spanning a 2D kernel."""

    metric = np.asarray(metric, dtype=float)
    covector = np.asarray(covector, dtype=float)
    if metric.shape != (2, 2) or covector.shape != (2,):
        raise ValueError("a two-dimensional metric and covector are required")
    if not np.all(np.isfinite(metric)) or not np.all(np.isfinite(covector)):
        raise ValueError("metric and covector must be finite")
    if np.min(np.linalg.eigvalsh(metric)) <= 0.0:
        raise ValueError("Khat must be positive definite")
    raw = np.asarray([covector[1], -covector[0]], dtype=float)
    norm_squared = float(raw @ metric @ raw)
    if norm_squared <= 0.0:
        raise ValueError("kernel tangent has nonpositive Khat norm")
    return raw / math.sqrt(norm_squared)


def _kernel_comparison(
    metric: np.ndarray,
    reference_unit_tangent: np.ndarray,
    selector_covector: np.ndarray,
) -> dict[str, Any]:
    """Compare two one-dimensional kernels using the Khat geometry."""

    metric = np.asarray(metric, dtype=float)
    tangent = np.asarray(reference_unit_tangent, dtype=float)
    selector = np.asarray(selector_covector, dtype=float)
    inverse = np.linalg.inv(metric)
    selector_dual_norm = float(math.sqrt(selector @ inverse @ selector))
    if selector_dual_norm <= 0.0:
        raise ValueError("selector covector has zero dual norm")
    selector_tangent = _unit_kernel_tangent(metric, selector)
    directional_residual = float(selector @ tangent)
    sine = float(abs(directional_residual) / selector_dual_norm)
    cosine = float(abs(tangent @ metric @ selector_tangent))
    sine = min(1.0, max(0.0, sine))
    cosine = min(1.0, max(0.0, cosine))
    angle = float(math.atan2(sine, cosine))
    return {
        "selector_dual_norm": selector_dual_norm,
        "selector_Khat_unit_kernel_tangent": selector_tangent.tolist(),
        "directional_residual_C_a_vF_a": directional_residual,
        "covariant_misalignment_sine": sine,
        "covariant_kernel_line_cosine_abs": cosine,
        "covariant_kernel_angle_radians": angle,
        "covariant_kernel_angle_degrees": float(math.degrees(angle)),
        "angle_Pythagorean_residual": float(abs(sine**2 + cosine**2 - 1.0)),
    }


def _level_set_acceleration(
    metric: np.ndarray,
    metric_derivative: np.ndarray,
    level_gradient: np.ndarray,
    level_hessian: np.ndarray,
    unit_tangent: np.ndarray,
) -> dict[str, Any]:
    """Coordinate acceleration of the Khat-arclength curve F=constant."""

    metric = np.asarray(metric, dtype=float)
    derivative = np.asarray(metric_derivative, dtype=float)
    gradient = np.asarray(level_gradient, dtype=float)
    hessian = np.asarray(level_hessian, dtype=float)
    tangent = np.asarray(unit_tangent, dtype=float)
    if derivative.shape != (2, 2, 2) or hessian.shape != (2, 2):
        raise ValueError("two-dimensional metric and level-set jets required")
    metric_rate = float(np.einsum("cab,c,a,b", derivative, tangent, tangent, tangent))
    equations = np.vstack((gradient, metric @ tangent))
    rhs = np.asarray(
        [-float(tangent @ hessian @ tangent), -0.5 * metric_rate]
    )
    if abs(float(np.linalg.det(equations))) <= 1.0e-14:
        raise ValueError("level-set acceleration equations are singular")
    acceleration = np.linalg.solve(equations, rhs)
    return {
        "coordinate_acceleration_d2y_dqbar2": acceleration.tolist(),
        "F_second_derivative_residual": float(
            abs(gradient @ acceleration + tangent @ hessian @ tangent)
        ),
        "Khat_unit_speed_derivative_residual": float(
            abs(2.0 * (metric @ tangent) @ acceleration + metric_rate)
        ),
    }


def _formal_alignment_limit(
    upstream: Mapping[str, Any], label: str
) -> dict[str, Any]:
    """Set one endpoint A' to zero in the local jets, without inventing a model."""

    if label not in {"lower", "upper"}:
        raise ValueError("label must be 'lower' or 'upper'")
    background = upstream["actual_background"]
    Em, Ep = map(float, background["exp_2A_endpoints"])
    F = float(background["F0"])
    H = list(map(float, background["A_u_endpoints"]))
    Bm, Bp = map(float, background["A_uu_endpoints_from_flow"])
    index = 0 if label == "lower" else 1
    H[index] = 0.0

    interval_gram = 6.0 * biscalar._closed_endpoint_gram_I(
        Em, Ep, H[0], H[1], F
    )
    interval_derivative = 6.0 * biscalar._endpoint_gram_derivatives_I(
        Em, Ep, H[0], H[1], Bm, Bp, F
    )
    inverse_F_log_derivative = np.asarray([Em / F, -Ep / F])
    metric = interval_gram / F
    metric_derivative = np.asarray(
        [
            (
                interval_derivative[coordinate]
                + inverse_F_log_derivative[coordinate] * interval_gram
            )
            / F
            for coordinate in range(2)
        ]
    )
    eigenvalues = np.linalg.eigvalsh(metric)
    if np.min(eigenvalues) <= 0.0:
        return {
            "endpoint": label,
            "admissible_positive_Khat_fixed_jet_limit": False,
            "Khat_eigenvalues": eigenvalues.tolist(),
            "construction": "set A'_i=0 while holding E, F, A'' and the opposite endpoint jets fixed",
        }

    connection = biscalar._christoffel(metric, metric_derivative)
    jet = biscalar._selector_jets(
        Em, Ep, H[0], H[1], Bm, Bp, F
    )[label]
    gradient = np.asarray(jet["gradient"], dtype=float)
    coordinate_hessian = np.asarray(jet["coordinate_hessian"], dtype=float)
    covariant_hessian = coordinate_hessian - np.einsum(
        "cab,c->ab", connection, gradient
    )
    normal = np.asarray([-Em, Ep], dtype=float)
    tangent = _unit_kernel_tangent(metric, normal)
    comparison = _kernel_comparison(metric, tangent, gradient)
    ambient_curvature = float(tangent @ covariant_hessian @ tangent)
    ambient_half_curvature = 0.5 * ambient_curvature

    # A physical holonomic F constraint would follow the level curve, not the
    # ambient geodesic.  Its coordinate acceleration is fixed by dF/dq=0 and
    # Khat-unit speed.  At A'_i=0 the acceleration-dependent A'_i*y_i'' term
    # drops out and the selector identity becomes
    # d2C/dq2|F=-2 A''_i (v_F^i)^2=chi_i'^2(v_F^i)^2/3 > 0.
    F_hessian = np.diag([-2.0 * H[0] * Em, 2.0 * H[1] * Ep])
    level_acceleration = _level_set_acceleration(
        metric, metric_derivative, normal, F_hessian, tangent
    )
    coordinate_acceleration = np.asarray(
        level_acceleration["coordinate_acceleration_d2y_dqbar2"]
    )
    covariant_acceleration = coordinate_acceleration + np.einsum(
        "abc,b,c->a", connection, tangent, tangent
    )
    level_set_curvature = float(
        tangent @ coordinate_hessian @ tangent
        + gradient @ coordinate_acceleration
    )
    endpoint_A_uu = (Bm, Bp)[index]
    level_set_identity = float(-2.0 * endpoint_A_uu * tangent[index] ** 2)
    level_set_half_curvature = 0.5 * level_set_curvature
    level_acceleration.update(
        {
            "covariant_acceleration": covariant_acceleration.tolist(),
            "Khat_tangent_projection_residual": float(
                abs(tangent @ metric @ covariant_acceleration)
            ),
            "ambient_Hessian_plus_extrinsic_term": float(
                ambient_curvature + gradient @ covariant_acceleration
            ),
        }
    )

    return {
        "endpoint": label,
        "construction": (
            "formal local endpoint-jet limit A'_i->0, holding E, F, A'', "
            "and the opposite endpoint jets fixed; this is not a solved "
            "global extension"
        ),
        "admissible_positive_Khat_fixed_jet_limit": True,
        "Khat_equals_6I_over_F": metric.tolist(),
        "Khat_eigenvalues": eigenvalues.tolist(),
        "dC_equals_dF_over_F": gradient.tolist(),
        "Khat_unit_volume_tangent": tangent.tolist(),
        "selector_residual": comparison["directional_residual_C_a_vF_a"],
        "covariant_nabla_a_nabla_b_C": covariant_hessian.tolist(),
        "F_level_set_curve": {
            "priority": "relevant kinematics if a holonomic F=F0 constraint were derived",
            "extrinsic_acceleration": level_acceleration,
            "selector_second_derivative": level_set_curvature,
            "identity": "d2C_i/dqbar2|F=-2A''_i(v_F^i)^2=chi_i'^2(v_F^i)^2/3",
            "identity_value": level_set_identity,
            "identity_absolute_error": float(
                abs(level_set_curvature - level_set_identity)
            ),
            "expansions": {
                "coordinate": "qbar is Khat arclength on the local F level curve",
                "C": {
                    "series": "C=1+(kappa_F/2)qbar^2+O(qbar^3)",
                    "qbar_squared_coefficient": level_set_half_curvature,
                    "sign": (
                        "positive"
                        if level_set_half_curvature > 0.0
                        else "nonpositive"
                    ),
                },
                "one_minus_C": {
                    "series": "1-C=-(kappa_F/2)qbar^2+O(qbar^3)",
                    "qbar_squared_coefficient": -level_set_half_curvature,
                    "sign": (
                        "negative"
                        if -level_set_half_curvature < 0.0
                        else "nonnegative"
                    ),
                },
                "minus_Y_over_C": {
                    "series": "-Y/C=-Y+(kappa_F/2)qbar^2*Y+O(qbar^3 Y)",
                    "qbar_squared_Y_coefficient": level_set_half_curvature,
                    "sign": (
                        "positive"
                        if level_set_half_curvature > 0.0
                        else "nonpositive"
                    ),
                    "matches_requested_negative_qbar_squared_Y_sign": False,
                },
                "shifted_selector_s_equals_C_minus_1": {
                    "s_qbar_squared_coefficient": level_set_half_curvature,
                    "minus_sY_qbar_squared_Y_coefficient": (
                        -level_set_half_curvature
                    ),
                    "minus_sY_sign": "negative",
                    "matches_requested_sign_conditionally": True,
                    "selected_by_current_minimal_matter_action": False,
                    "status": (
                        "additional nonminimal operator choice; it does not follow "
                        "from -Y/C or from fixing F alone"
                    ),
                },
                "physical_q2Y_vertex_derived": False,
            },
        },
        "ambient_Khat_geodesic_diagnostic": {
            "covariant_selector_curvature": ambient_curvature,
            "scope": (
                "ambient geodesic only; it is not the trajectory of a holonomic "
                "F=constant constraint"
            ),
            "Riemann_normal_expansions": {
            "coordinate": "qbar is Khat-unit and geodesic at the reference point",
            "C": {
                "series": "C=1+(kappa_C/2)qbar^2+O(qbar^3)",
                "qbar_squared_coefficient": ambient_half_curvature,
                "sign": (
                    "negative" if ambient_half_curvature < 0.0 else "nonnegative"
                ),
            },
            "one_minus_C": {
                "series": "1-C=-(kappa_C/2)qbar^2+O(qbar^3)",
                "qbar_squared_coefficient": -ambient_half_curvature,
                "sign": (
                    "positive" if -ambient_half_curvature > 0.0 else "nonpositive"
                ),
            },
            "minus_Y_over_C": {
                "series": "-Y/C=-Y+(kappa_C/2)qbar^2*Y+O(qbar^3 Y)",
                "qbar_squared_Y_coefficient": ambient_half_curvature,
                "sign": (
                    "negative" if ambient_half_curvature < 0.0 else "nonnegative"
                ),
            },
            "minus_C_times_Y_diagnostic": {
                "series": "-C*Y=-Y-(kappa_C/2)qbar^2*Y+O(qbar^3 Y)",
                "qbar_squared_Y_coefficient": -ambient_half_curvature,
                "sign": (
                    "positive" if -ambient_half_curvature > 0.0 else "nonpositive"
                ),
            },
            "physical_q2Y_vertex_derived": False,
            },
        },
        "curvature_scope": (
            "The F-level-set second derivative is the relevant conditional "
            "kinematics. Even it is not a physical vertex until a constraint "
            "action and the complete reduced matter action are derived."
        ),
    }


def build(
    upstream_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    upstream = (
        biscalar.build() if upstream_result is None else dict(upstream_result)
    )
    if upstream.get("checks", {}).get("all") is not True:
        raise RuntimeError("real BPS biscalar geometry must pass first")
    if upstream.get("schema") != "holo.bps-biscalar-matter-geometry.v1":
        raise RuntimeError("unexpected BPS biscalar geometry schema")
    if (
        upstream.get("physical_gates", {}).get("physical_q2Y_selector_derived")
        is not False
    ):
        raise RuntimeError("upstream physical q2Y gate must remain explicitly closed")

    background = upstream["actual_background"]
    Em, Ep = map(float, background["exp_2A_endpoints"])
    Hm, Hp = map(float, background["A_u_endpoints"])
    Bm, _ = map(float, background["A_uu_endpoints_from_flow"])
    u_minus, u_plus = map(float, background["domain"])
    F = float(background["F0"])
    metric = np.asarray(
        upstream["moduli_metric"]["Khat_equals_6I_over_F"], dtype=float
    )
    if Em <= 0.0 or Ep <= 0.0 or F <= 0.0:
        raise ValueError("positive endpoint warp factors and F are required")

    normal = np.asarray([-Em, Ep], dtype=float)
    tangent = _unit_kernel_tangent(metric, normal)
    volume_residual = float(normal @ tangent)
    unit_residual = float(abs(tangent @ metric @ tangent - 1.0))
    expected_upstream_normal = np.asarray(
        upstream["moduli_metric"]["Planck_normalized_action_derivation"][
            "endpoint_derivative_of_F"
        ],
        dtype=float,
    )

    selector_results: dict[str, Any] = {}
    maximum_residual_identity_error = 0.0
    maximum_angle_identity_error = 0.0
    maximum_determinant_identity_error = 0.0
    for label, index, H, other_E in (
        ("lower", 0, Hm, Ep),
        ("upper", 1, Hp, Em),
    ):
        gradient = np.asarray(upstream["selectors"][label]["C_a"], dtype=float)
        comparison = _kernel_comparison(metric, tangent, gradient)
        expected_residual = float(-2.0 * H * tangent[index])
        residual_error = float(
            abs(comparison["directional_residual_C_a_vF_a"] - expected_residual)
        )
        determinant = float(np.linalg.det(np.vstack((normal, gradient))))
        expected_determinant = float(2.0 * other_E * H)
        determinant_error = float(abs(determinant - expected_determinant))
        W = float(-6.0 * H)
        stored_tangent = np.asarray(
            upstream["selectors"][label][
                "invariants_in_Khat_equals_6I_over_F_units"
            ]["unit_silent_tangent"],
            dtype=float,
        )
        stored_line_cosine = float(abs(stored_tangent @ metric @ np.asarray(
            comparison["selector_Khat_unit_kernel_tangent"]
        )))
        maximum_residual_identity_error = max(
            maximum_residual_identity_error, residual_error
        )
        maximum_angle_identity_error = max(
            maximum_angle_identity_error,
            comparison["angle_Pythagorean_residual"],
            abs(stored_line_cosine - 1.0),
        )
        maximum_determinant_identity_error = max(
            maximum_determinant_identity_error, determinant_error
        )
        selector_results[label] = {
            "C_a": gradient.tolist(),
            **comparison,
            "residual_identity": "C_i,a v_F^a=-2 A'_i v_F^i",
            "residual_identity_expected": expected_residual,
            "residual_identity_absolute_error": residual_error,
            "covector_determinant_det_dF_dC": determinant,
            "determinant_identity": (
                "2 E_+ A'_-=-E_+ W_-/3"
                if label == "lower"
                else "2 E_- A'_+=-E_- W_+/3"
            ),
            "determinant_identity_expected": expected_determinant,
            "determinant_identity_absolute_error": determinant_error,
            "A_u_at_endpoint": H,
            "W_at_endpoint_equals_minus_6_A_u": W,
            "exactly_aligned_on_current_background": H == 0.0,
        }

    alignment_limit = _formal_alignment_limit(upstream, "lower")
    extrapolated_delta = float(-Hm / Bm)
    extrapolated_root = float(u_minus + extrapolated_delta)
    extrapolation = {
        "method": "first-order endpoint Taylor hypothesis A'(u)=A'_--+A''_--*(u-u_-)",
        "A_u_lower": Hm,
        "A_uu_lower_from_flow": Bm,
        "delta_u_root_equals_minus_A_u_over_A_uu": extrapolated_delta,
        "estimated_u_at_A_u_zero": extrapolated_root,
        "distance_below_certified_lower_endpoint": float(u_minus - extrapolated_root),
        "certified_domain": [u_minus, u_plus],
        "inside_certified_domain": bool(u_minus <= extrapolated_root <= u_plus),
        "linearized_A_u_at_estimated_root": float(Hm + Bm * extrapolated_delta),
        "Taylor_remainder_bounded_from_current_artifact": False,
        "outside_interval_background_evaluated": False,
        "zero_confirmed": False,
        "status": "hypothesis_outside_certified_interval",
    }

    lower_angle = selector_results["lower"]["covariant_kernel_angle_degrees"]
    upper_angle = selector_results["upper"]["covariant_kernel_angle_degrees"]
    ambient_limit_curvature = alignment_limit.get(
        "ambient_Khat_geodesic_diagnostic", {}
    ).get("covariant_selector_curvature", math.nan)
    level_set_limit_curvature = alignment_limit.get(
        "F_level_set_curve", {}
    ).get("selector_second_derivative", math.nan)
    level_set_identity_error = alignment_limit.get(
        "F_level_set_curve", {}
    ).get("identity_absolute_error", math.inf)
    level_set_kinematic_residual = max(
        alignment_limit.get("F_level_set_curve", {})
        .get("extrinsic_acceleration", {})
        .get(key, math.inf)
        for key in (
            "F_second_derivative_residual",
            "Khat_unit_speed_derivative_residual",
            "Khat_tangent_projection_residual",
        )
    )
    checks = {
        "upstream_real_BPS_biscalar_certificate_passes": True,
        "dF_endpoint_formula_matches_upstream": bool(
            np.array_equal(normal, expected_upstream_normal)
        ),
        "volume_tangent_annihilates_dF": abs(volume_residual)
        < CRITERIA["volume_tangent_residual_max"],
        "volume_tangent_is_Khat_unit": unit_residual
        < CRITERIA["metric_unit_residual_max"],
        "selector_residual_identities_close": maximum_residual_identity_error
        < CRITERIA["selector_residual_identity_max"],
        "covariant_angle_identities_close": maximum_angle_identity_error
        < CRITERIA["angle_identity_max"],
        "alignment_determinant_identities_close": (
            maximum_determinant_identity_error
            < CRITERIA["alignment_determinant_identity_max"]
        ),
        "lower_endpoint_is_near_but_not_exactly_aligned": bool(
            0.0 < lower_angle
            < CRITERIA["lower_near_alignment_angle_degrees_max"]
            and Hm != 0.0
        ),
        "upper_endpoint_is_strongly_misaligned": upper_angle
        > CRITERIA["upper_misalignment_angle_degrees_min"],
        "lower_linearized_zero_is_outside_certified_interval": bool(
            extrapolated_root < u_minus and not extrapolation["zero_confirmed"]
        ),
        "lower_fixed_jet_alignment_limit_keeps_positive_Khat": bool(
            alignment_limit["admissible_positive_Khat_fixed_jet_limit"]
            and min(alignment_limit["Khat_eigenvalues"])
            > CRITERIA["alignment_limit_metric_min_eigenvalue"]
        ),
        "lower_ambient_geodesic_curvature_is_negative": bool(
            np.isfinite(ambient_limit_curvature)
            and ambient_limit_curvature
            < CRITERIA["alignment_limit_curvature_negative_max"]
        ),
        "lower_F_level_set_selector_curvature_is_positive": bool(
            np.isfinite(level_set_limit_curvature)
            and level_set_limit_curvature
            > CRITERIA["level_set_curvature_positive_min"]
        ),
        "lower_F_level_set_curvature_identity_closes": (
            level_set_identity_error
            < CRITERIA["level_set_curvature_identity_max"]
        ),
        "lower_F_level_set_extrinsic_kinematics_close": (
            level_set_kinematic_residual
            < CRITERIA["level_set_kinematic_residual_max"]
        ),
        "ambient_and_F_level_set_curvatures_have_opposite_sign": bool(
            ambient_limit_curvature < 0.0 < level_set_limit_curvature
        ),
        "no_observational_tables_read": True,
        "physical_q2Y_gate_remains_closed": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "warped_volume_F_exists_as_geometric_functional": True,
        "top_form_present_in_current_repository_theory": False,
        "global_F_constraint_present_in_current_repository_action": False,
        "constraint_equation_and_backreaction_derived": False,
        "F_constraint_physically_selects_ker_dF": False,
        "lower_alignment_exact_on_certified_background": False,
        "extrapolated_A_u_zero_confirmed_outside_interval": False,
        "nonlinear_constraint_surface_reduced_action_derived": False,
        "matter_Y_convention_and_base_term_fixed": False,
        "minimal_minus_Y_over_C_has_requested_negative_q2Y_sign": False,
        "shifted_s_equals_C_minus_1_operator_selected_by_current_action": False,
        "physical_q2Y_vertex_derived": False,
        "force_law_derived_or_observed": False,
        "candidate_is_physical_completion": False,
    }

    return {
        "schema": "holo.bps-volume-constraint-selector.v1",
        "title": "Conditional fixed-warped-volume selector geometry",
        "classification": (
            "lower_volume_tangent_nearly_matches_single_brane_selector_kernel;"
            "formal_F_level_curve_has_wrong_minimal_matter_sign;"
            "global_constraint_is_new_physics_not_present;physical_q2Y_false"
        ),
        "current_theory_vs_new_extension": {
            "current_theory": (
                "The real functional-BPS branch supplies F, two endpoint moduli, "
                "Khat, and C_i. It supplies no top-form or global equation fixing F."
            ),
            "new_extension_hypothesis": (
                "An unspecified new global mechanism could impose F=F0 and retain "
                "ker dF. This certificate neither writes nor endorses such an action."
            ),
            "top_form_action_written_here": False,
            "stress_energy_or_backreaction_computed_here": False,
            "force_claim": False,
        },
        "coordinates": {
            "endpoint_moduli": ["u_minus", "u_plus"],
            "warped_volume": "F=int_[u_minus,u_plus] exp(2A(u)) du",
            "normal_covector": "n_F=dF=(-E_-,E_+), E_i=exp(2A_i)>0",
            "metric": "Khat_ab=6I_ab/F",
        },
        "actual_background": {
            "samples": background["samples"],
            "domain": [u_minus, u_plus],
            "F0": F,
            "E_endpoints": [Em, Ep],
            "A_u_endpoints": [Hm, Hp],
            "W_endpoints_equals_minus_6_A_u": [-6.0 * Hm, -6.0 * Hp],
        },
        "volume_constraint_candidate": {
            "normal_covector_nF_equals_dF": normal.tolist(),
            "raw_kernel_tangent": [Ep, Em],
            "Khat_unit_kernel_tangent_vF": tangent.tolist(),
            "dF_vF_residual": volume_residual,
            "Khat_unit_residual": unit_residual,
            "physical_selection_by_current_action": False,
        },
        "selector_kernel_comparison": selector_results,
        "exact_alignment_theorem": {
            "selector_gradient": "dC_i=dF/F-2A'_i dy^i at C_i=1",
            "lower_determinant": "det(dF,dC_-)=2E_+ A'_-=-E_+ W_-/3",
            "upper_determinant": "det(dF,dC_+)=2E_- A'_+=-E_- W_+/3",
            "positive_endpoint_factors": "E_->0 and E_+>0",
            "if_and_only_if": "ker(dF)=ker(dC_i) iff A'_i=0 iff W_i=0",
            "BPS_flow_convention": "A'=-W/6",
            "current_lower_endpoint_satisfies_exact_condition": False,
            "current_upper_endpoint_satisfies_exact_condition": False,
        },
        "lower_exact_alignment_fixed_jet_diagnostic": alignment_limit,
        "lower_A_u_zero_local_extrapolation": extrapolation,
        "candidate_verdict": (
            "Fixing F would nearly align the lower selector at first order on "
            "the current background. In the formal exact-alignment limit, however, "
            "the F-level curve has positive C curvature, so minimal -Y/C gives a "
            "positive qbar^2 Y coefficient rather than the requested negative one. "
            "The shifted selector s=C-1 would give -sY the requested sign, but that "
            "is an additional nonminimal operator choice, not a consequence of "
            "-Y/C or of the F constraint. Thus fixing F alone is insufficient and "
            "no force completion follows."
        ),
        "physical_gates": physical_gates,
        "falsifiers": [
            {
                "id": "F1_endpoint_derivative",
                "test": "finite endpoint variations of F must approach (-E_-,E_+)",
                "failure": "dF disagrees with the endpoint fundamental theorem",
            },
            {
                "id": "F2_alignment_identity",
                "test": "det(dF,dC_i) must equal 2 E_other A'_i",
                "failure": "the claimed iff alignment condition fails",
            },
            {
                "id": "F3_outside_interval_zero",
                "test": (
                    "extend the same certified solution below u_- and evaluate A' "
                    "near the Taylor estimate"
                ),
                "failure": (
                    "no A'=0 crossing exists there or higher endpoint jets move it "
                    "outside the stated local regime"
                ),
            },
            {
                "id": "F4_constraint_dynamics",
                "test": (
                    "supply a complete global-constraint action and solve its "
                    "background, perturbations, stress tensor, and reduced kinetic term"
                ),
                "failure": (
                    "backreaction changes the background/Khat or the retained tangent, "
                    "or introduces a ghost/nonlocal inconsistency"
                ),
            },
            {
                "id": "F5_physical_matter_vertex",
                "test": (
                    "perform the full lapse/shift/bending and matter reduction with "
                    "a fixed Y convention and canonical normalization"
                ),
                "failure": (
                    "a qbar*Y term survives, the base -Y term is uncontrolled, or the "
                    "qbar^2*Y sign differs from the conditional level-set diagnostic"
                ),
            },
        ],
        "checks": checks,
        "criteria": CRITERIA,
        "inputs": {
            "observational_tables_read": [],
            "imported_builder": {
                "path": str(Path(biscalar.__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(biscalar.__file__).resolve()),
                "schema": upstream["schema"],
            },
            "upstream_files": upstream["inputs"]["files"],
        },
        "evidence_boundary": (
            "This proves endpoint-calculus identities and quantifies a conditional "
            "Khat-unit volume tangent on the certified real BPS background. The "
            "constraint mechanism, the extrapolated A'=0 point, a reduced action, "
            "a physical q^2Y vertex, and any force remain unproved."
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
        raise SystemExit(f"BPS volume-constraint candidate failed: {failed}")
    _write(OUTPUT, result)
    lower = result["selector_kernel_comparison"]["lower"]
    upper = result["selector_kernel_comparison"]["upper"]
    limit = result["lower_exact_alignment_fixed_jet_diagnostic"]
    print(f"[artifact] {OUTPUT}")
    print(f"[v_F] {result['volume_constraint_candidate']['Khat_unit_kernel_tangent_vF']}")
    print(
        "[lower] C.v={:.12g} angle={:.9g} deg".format(
            lower["directional_residual_C_a_vF_a"],
            lower["covariant_kernel_angle_degrees"],
        )
    )
    print(
        "[upper] C.v={:.12g} angle={:.9g} deg".format(
            upper["directional_residual_C_a_vF_a"],
            upper["covariant_kernel_angle_degrees"],
        )
    )
    print(
        "[formal lower A'=0 F-level curvature] {:.12g}".format(
            limit["F_level_set_curve"]["selector_second_derivative"]
        )
    )
    print(
        "[ambient geodesic diagnostic] {:.12g}".format(
            limit["ambient_Khat_geodesic_diagnostic"][
                "covariant_selector_curvature"
            ]
        )
    )
    print("[global F constraint present] False")
    print("[physical q2Y derived] False")
    print("[certificate] PASS (conditional geometry only)")


if __name__ == "__main__":
    main()
