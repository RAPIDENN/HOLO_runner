#!/usr/bin/env python3
"""Verify bent-brane geometry and radial gauge straightening through S2.

The calculation uses a synthetic analytic five-dimensional metric and scalar,
not the observational sector.  It evaluates the exact induced metric, unit
normal, extrinsic curvature, scalar junction and Israel tensor on a moving
brane, then performs the coordinate change that straightens the same brane.
Agreement is required at both endpoint orientations and through second order
in the perturbation parameter.  This closes the geometric covariance subgate,
not the full finite-gamma endpoint action or spectrum.
"""

from __future__ import annotations

import json
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "bent_brane_geometry_S2.json"
DIM = 5
SLICE_DIM = 4
X_INDEX = 1
U_INDEX = 4
ETA4 = np.diag([-1.0, 1.0, 1.0, 1.0])
COMPLEX_STEP = 1.0e-30
PROBE_X = 0.73
EPSILON_VALUES = np.asarray([-0.02, -0.01, 0.0, 0.01, 0.02])
JET_SWEEP = (
    ("soft_eta_zero", 0.25, 0.0),
    ("reference_eta_negative", 1.37, -0.43),
    ("stiff_eta_positive", 4.20, 0.90),
)


@dataclass(frozen=True)
class BraneSpec:
    """Fixed endpoint data; the potential does not follow a trial normal sign."""

    label: str
    jet_case: str
    endpoint_u: float
    outward_orientation: float
    lambda0: float
    lambda1: float
    gamma: float
    eta: float


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _warp(u: complex | float) -> complex | float:
    return -0.21 - 0.83 * u - 0.035 * u**2


def _warp_u(u: complex | float) -> complex | float:
    return -0.83 - 0.07 * u


def _chi_background(u: complex | float) -> complex | float:
    return 0.14 + 0.71 * u + 0.045 * u**2


def _chi_background_u(u: complex | float) -> complex | float:
    return 0.71 + 0.09 * u


def _brane_spec(
    label: str,
    jet_case: str,
    endpoint_u: float,
    outward_orientation: float,
    gamma: float,
    eta: float,
) -> BraneSpec:
    """Construct a physical endpoint potential for its fixed outward normal."""

    return BraneSpec(
        label=label,
        jet_case=jet_case,
        endpoint_u=endpoint_u,
        outward_orientation=outward_orientation,
        lambda0=(
            6.0 * outward_orientation * float(_warp_u(endpoint_u))
        ),
        lambda1=(
            -outward_orientation * float(_chi_background_u(endpoint_u))
        ),
        gamma=gamma,
        eta=eta,
    )


def _brane_specs() -> list[BraneSpec]:
    endpoints = (("lower", 0.17, -1.0), ("upper", 1.13, 1.0))
    return [
        _brane_spec(label, jet_case, endpoint_u, orientation, gamma, eta)
        for label, endpoint_u, orientation in endpoints
        for jet_case, gamma, eta in JET_SWEEP
    ]


def _bending(x: complex | float) -> complex | float:
    return 0.18 * np.cos(x) + 0.025 * np.sin(2.0 * x)


def _bending_x(x: complex | float) -> complex | float:
    return -0.18 * np.sin(x) + 0.05 * np.cos(2.0 * x)


def _bending_xx(x: complex | float) -> complex | float:
    return -0.18 * np.cos(x) - 0.10 * np.sin(2.0 * x)


def _metric_scalar_perturbation(
    x: complex | float, u: complex | float
) -> tuple[complex | float, complex | float, complex | float]:
    curvature = 0.08 * np.cos(x) + 0.03 * u * np.sin(x)
    lapse = 0.05 * np.sin(2.0 * x) - 0.02 * u * np.cos(x)
    scalar = 0.06 * np.cos(x) + 0.04 * u * np.sin(2.0 * x)
    return curvature, lapse, scalar


def _old_metric(coords: np.ndarray, epsilon: float | complex) -> np.ndarray:
    x, u = coords[X_INDEX], coords[U_INDEX]
    curvature, lapse, _scalar = _metric_scalar_perturbation(x, u)
    conformal = np.exp(2.0 * (_warp(u) + epsilon * curvature))
    radial_lapse = 1.0 + epsilon * lapse
    dtype = np.result_type(coords.dtype, epsilon)
    metric = np.zeros((DIM, DIM), dtype=dtype)
    metric[:SLICE_DIM, :SLICE_DIM] = conformal * ETA4
    metric[U_INDEX, U_INDEX] = radial_lapse**2
    return metric


def _old_scalar(coords: np.ndarray, epsilon: float | complex) -> complex | float:
    x, u = coords[X_INDEX], coords[U_INDEX]
    _curvature, _lapse, scalar = _metric_scalar_perturbation(x, u)
    return _chi_background(u) + epsilon * scalar


def _old_from_straight(
    straight_coords: np.ndarray, epsilon: float | complex
) -> tuple[np.ndarray, np.ndarray]:
    dtype = np.result_type(straight_coords.dtype, epsilon)
    old = np.asarray(straight_coords, dtype=dtype).copy()
    x = straight_coords[X_INDEX]
    old[U_INDEX] = straight_coords[U_INDEX] + epsilon * _bending(x)
    jacobian = np.eye(DIM, dtype=dtype)
    jacobian[U_INDEX, X_INDEX] = epsilon * _bending_x(x)
    return old, jacobian


def _straight_metric(coords: np.ndarray, epsilon: float | complex) -> np.ndarray:
    old, jacobian = _old_from_straight(coords, epsilon)
    return jacobian.T @ _old_metric(old, epsilon) @ jacobian


def _straight_scalar(coords: np.ndarray, epsilon: float | complex) -> complex | float:
    old, _jacobian = _old_from_straight(coords, epsilon)
    return _old_scalar(old, epsilon)


def _complex_derivatives(
    function: Callable[[np.ndarray, float | complex], np.ndarray | complex | float],
    coords: np.ndarray,
    epsilon: float,
) -> np.ndarray:
    values = []
    for axis in range(DIM):
        shifted = coords.astype(complex)
        shifted[axis] += 1j * COMPLEX_STEP
        values.append(np.imag(function(shifted, epsilon)) / COMPLEX_STEP)
    return np.asarray(values)


def _christoffel(
    metric_function: Callable[[np.ndarray, float | complex], np.ndarray],
    coords: np.ndarray,
    epsilon: float,
) -> tuple[np.ndarray, np.ndarray]:
    metric = np.asarray(metric_function(coords, epsilon), dtype=float)
    inverse = np.linalg.inv(metric)
    derivative = _complex_derivatives(metric_function, coords, epsilon)
    connection = np.zeros((DIM, DIM, DIM), dtype=float)
    for upper in range(DIM):
        for left in range(DIM):
            for right in range(DIM):
                connection[upper, left, right] = 0.5 * sum(
                    inverse[upper, lower]
                    * (
                        derivative[left, lower, right]
                        + derivative[right, lower, left]
                        - derivative[lower, left, right]
                    )
                    for lower in range(DIM)
                )
    return metric, connection


def _lambda_data(chi: float, brane: BraneSpec) -> tuple[float, float]:
    reference = float(_chi_background(brane.endpoint_u))
    delta = chi - reference
    value = (
        brane.lambda0
        + brane.lambda1 * delta
        + 0.5 * brane.gamma * delta**2
        + brane.eta * delta**3 / 6.0
    )
    derivative = (
        brane.lambda1
        + brane.gamma * delta
        + 0.5 * brane.eta * delta**2
    )
    return value, derivative


def _brane_invariants(
    *,
    chart: str,
    brane: BraneSpec,
    x_value: float,
    epsilon: float,
    normal_orientation: float | None = None,
) -> dict[str, np.ndarray | float]:
    endpoint_u = brane.endpoint_u
    orientation = (
        brane.outward_orientation
        if normal_orientation is None
        else normal_orientation
    )
    tangential = np.asarray([0.13, x_value, -0.17, 0.09], dtype=float)
    if chart == "bent":
        coords = np.append(tangential, endpoint_u + epsilon * _bending(x_value))
        metric_function = _old_metric
        scalar_function = _old_scalar
        tangent = np.zeros((SLICE_DIM, DIM), dtype=float)
        tangent[:, :SLICE_DIM] = np.eye(SLICE_DIM)
        tangent[X_INDEX, U_INDEX] = epsilon * _bending_x(x_value)
        second = np.zeros((SLICE_DIM, SLICE_DIM, DIM), dtype=float)
        second[X_INDEX, X_INDEX, U_INDEX] = epsilon * _bending_xx(x_value)
        level_gradient = np.zeros(DIM, dtype=float)
        level_gradient[X_INDEX] = -epsilon * _bending_x(x_value)
        level_gradient[U_INDEX] = 1.0
    elif chart == "straight":
        coords = np.append(tangential, endpoint_u)
        metric_function = _straight_metric
        scalar_function = _straight_scalar
        tangent = np.zeros((SLICE_DIM, DIM), dtype=float)
        tangent[:, :SLICE_DIM] = np.eye(SLICE_DIM)
        second = np.zeros((SLICE_DIM, SLICE_DIM, DIM), dtype=float)
        level_gradient = np.zeros(DIM, dtype=float)
        level_gradient[U_INDEX] = 1.0
    else:
        raise ValueError("chart must be bent or straight")

    metric, connection = _christoffel(metric_function, coords, epsilon)
    inverse_metric = np.linalg.inv(metric)
    norm_squared = float(level_gradient @ inverse_metric @ level_gradient)
    normal_covector = orientation * level_gradient / np.sqrt(norm_squared)
    normal_vector = inverse_metric @ normal_covector
    induced = tangent @ metric @ tangent.T
    induced_inverse = np.linalg.inv(induced)
    extrinsic = np.zeros((SLICE_DIM, SLICE_DIM), dtype=float)
    for mu in range(SLICE_DIM):
        for nu in range(SLICE_DIM):
            acceleration = second[mu, nu].copy()
            acceleration += np.einsum(
                "abc,b,c->a", connection, tangent[mu], tangent[nu]
            )
            extrinsic[mu, nu] = -float(normal_covector @ acceleration)
    extrinsic_trace = float(np.trace(induced_inverse @ extrinsic))

    scalar_value = float(scalar_function(coords, epsilon))
    scalar_gradient = np.asarray(
        _complex_derivatives(scalar_function, coords, epsilon), dtype=float
    )
    lambda_value, lambda_prime = _lambda_data(scalar_value, brane)
    scalar_junction = float(normal_vector @ scalar_gradient + lambda_prime)
    israel = (
        extrinsic
        - extrinsic_trace * induced
        + 0.5 * lambda_value * induced
    )
    tangent_normal = tangent @ normal_covector
    return {
        "induced": induced,
        "normal_covector": normal_covector,
        "normal_norm": float(normal_covector @ inverse_metric @ normal_covector),
        "tangent_normal": tangent_normal,
        "extrinsic": extrinsic,
        "extrinsic_trace": extrinsic_trace,
        "scalar_junction": scalar_junction,
        "israel": israel,
    }


def _flatten_invariants(values: Mapping[str, np.ndarray | float]) -> np.ndarray:
    return np.concatenate(
        (
            np.ravel(values["induced"]),
            np.ravel(values["extrinsic"]),
            np.asarray([values["extrinsic_trace"]], dtype=float),
            np.asarray([values["scalar_junction"]], dtype=float),
            np.ravel(values["israel"]),
        )
    )


def _endpoint_check(brane: BraneSpec) -> dict[str, Any]:
    bent_rows = []
    straight_rows = []
    pointwise_errors = []
    geometry_errors = []
    normal_transform_errors = []
    for epsilon in EPSILON_VALUES:
        bent = _brane_invariants(
            chart="bent",
            brane=brane,
            x_value=PROBE_X,
            epsilon=float(epsilon),
        )
        straight = _brane_invariants(
            chart="straight",
            brane=brane,
            x_value=PROBE_X,
            epsilon=float(epsilon),
        )
        bent_flat = _flatten_invariants(bent)
        straight_flat = _flatten_invariants(straight)
        scale = np.maximum(np.maximum(np.abs(bent_flat), np.abs(straight_flat)), 1.0)
        pointwise_errors.append(float(np.max(np.abs(bent_flat - straight_flat) / scale)))
        straight_coords = np.asarray(
            [0.13, PROBE_X, -0.17, 0.09, brane.endpoint_u], dtype=float
        )
        _old, jacobian = _old_from_straight(straight_coords, float(epsilon))
        transformed_normal = jacobian.T @ np.asarray(bent["normal_covector"])
        normal_scale = max(
            float(np.max(np.abs(transformed_normal))),
            float(np.max(np.abs(straight["normal_covector"]))),
            1.0,
        )
        normal_transform_errors.append(
            float(
                np.max(
                    np.abs(
                        transformed_normal
                        - np.asarray(straight["normal_covector"])
                    )
                )
                / normal_scale
            )
        )
        geometry_errors.extend(
            [
                abs(float(bent["normal_norm"]) - 1.0),
                float(np.max(np.abs(bent["tangent_normal"]))),
                abs(float(straight["normal_norm"]) - 1.0),
                float(np.max(np.abs(straight["tangent_normal"]))),
            ]
        )
        bent_rows.append(bent_flat)
        straight_rows.append(straight_flat)

    vandermonde = np.vander(EPSILON_VALUES, N=5, increasing=True)
    bent_coefficients = np.linalg.solve(vandermonde, np.asarray(bent_rows))
    straight_coefficients = np.linalg.solve(vandermonde, np.asarray(straight_rows))
    coefficient_scale = np.maximum(
        np.maximum(
            np.abs(bent_coefficients[:3]), np.abs(straight_coefficients[:3])
        ),
        1.0,
    )
    coefficient_error = float(
        np.max(
            np.abs(bent_coefficients[:3] - straight_coefficients[:3])
            / coefficient_scale
        )
    )
    background_bent = _brane_invariants(
        chart="bent",
        brane=brane,
        x_value=PROBE_X,
        epsilon=0.0,
    )
    background_junction = max(
        abs(float(background_bent["scalar_junction"])),
        float(np.max(np.abs(background_bent["israel"]))),
    )
    expected_extrinsic = (
        brane.outward_orientation
        * float(_warp_u(brane.endpoint_u))
        * np.asarray(background_bent["induced"])
    )
    background_extrinsic_oracle = max(
        float(
            np.max(
                np.abs(
                    np.asarray(background_bent["extrinsic"])
                    - expected_extrinsic
                )
            )
        ),
        abs(
            float(background_bent["extrinsic_trace"])
            - 4.0
            * brane.outward_orientation
            * float(_warp_u(brane.endpoint_u))
        ),
    )
    wrong_orientation = _brane_invariants(
        chart="bent",
        brane=brane,
        normal_orientation=-brane.outward_orientation,
        x_value=PROBE_X,
        epsilon=0.0,
    )
    wrong_orientation_junction = min(
        abs(float(wrong_orientation["scalar_junction"])),
        float(np.max(np.abs(wrong_orientation["israel"]))),
    )
    return {
        "label": brane.label,
        "jet_case": brane.jet_case,
        "endpoint_u": brane.endpoint_u,
        "orientation": int(brane.outward_orientation),
        "lambda0": brane.lambda0,
        "lambda1": brane.lambda1,
        "gamma": brane.gamma,
        "eta": brane.eta,
        "epsilon_values": EPSILON_VALUES.tolist(),
        "pointwise_chart_max_relative": max(pointwise_errors),
        "coefficient_O0_O1_O2_chart_max_relative": coefficient_error,
        "normal_covector_transform_max_relative": max(
            normal_transform_errors
        ),
        "normalization_and_orthogonality_max_abs": max(geometry_errors),
        "background_junction_max_abs": background_junction,
        "background_extrinsic_oracle_max_abs": background_extrinsic_oracle,
        "wrong_orientation_junction_min_abs": wrong_orientation_junction,
        "nontrivial_O1_coefficient_max_abs": float(
            np.max(np.abs(bent_coefficients[1]))
        ),
        "nontrivial_O2_coefficient_max_abs": float(
            np.max(np.abs(bent_coefficients[2]))
        ),
    }


def _scalar_junction_coefficients(brane: BraneSpec) -> np.ndarray:
    rows = [
        float(
            _brane_invariants(
                chart="bent",
                brane=brane,
                x_value=PROBE_X,
                epsilon=float(epsilon),
            )["scalar_junction"]
        )
        for epsilon in EPSILON_VALUES
    ]
    vandermonde = np.vander(EPSILON_VALUES, N=5, increasing=True)
    return np.linalg.solve(vandermonde, np.asarray(rows))


def _jet_sensitivity_check(
    label: str, endpoint_u: float, orientation: float
) -> dict[str, Any]:
    gamma_low = _brane_spec(
        label, "gamma_low", endpoint_u, orientation, 0.41, 0.27
    )
    gamma_high = _brane_spec(
        label, "gamma_high", endpoint_u, orientation, 2.31, 0.27
    )
    eta_zero = _brane_spec(
        label, "eta_zero", endpoint_u, orientation, 1.19, 0.0
    )
    eta_nonzero = _brane_spec(
        label, "eta_nonzero", endpoint_u, orientation, 1.19, 0.83
    )
    gamma_low_coefficients = _scalar_junction_coefficients(gamma_low)
    gamma_high_coefficients = _scalar_junction_coefficients(gamma_high)
    eta_zero_coefficients = _scalar_junction_coefficients(eta_zero)
    eta_nonzero_coefficients = _scalar_junction_coefficients(eta_nonzero)

    _curvature, _lapse, scalar = _metric_scalar_perturbation(
        PROBE_X, endpoint_u
    )
    q1 = float(
        _chi_background_u(endpoint_u) * _bending(PROBE_X) + scalar
    )
    measured_dB1_dgamma = float(
        (gamma_high_coefficients[1] - gamma_low_coefficients[1])
        / (gamma_high.gamma - gamma_low.gamma)
    )
    measured_dB2_deta = float(
        (eta_nonzero_coefficients[2] - eta_zero_coefficients[2])
        / (eta_nonzero.eta - eta_zero.eta)
    )
    expected_dB2_deta = 0.5 * q1**2
    return {
        "label": label,
        "endpoint_u": endpoint_u,
        "orientation": int(orientation),
        "Q1": q1,
        "measured_dB1_dgamma": measured_dB1_dgamma,
        "expected_dB1_dgamma": q1,
        "dB1_dgamma_error_abs": abs(measured_dB1_dgamma - q1),
        "measured_dB2_deta": measured_dB2_deta,
        "expected_dB2_deta": expected_dB2_deta,
        "dB2_deta_error_abs": abs(
            measured_dB2_deta - expected_dB2_deta
        ),
    }


def build() -> dict[str, Any]:
    endpoints = [_endpoint_check(brane) for brane in _brane_specs()]
    sensitivities = [
        _jet_sensitivity_check("lower", 0.17, -1.0),
        _jet_sensitivity_check("upper", 1.13, 1.0),
    ]
    bending_probe = {
        "xi": float(_bending(PROBE_X)),
        "xi_x": float(_bending_x(PROBE_X)),
        "xi_xx": float(_bending_xx(PROBE_X)),
    }
    maxima = {
        "pointwise_chart_max_relative": max(
            row["pointwise_chart_max_relative"] for row in endpoints
        ),
        "coefficient_O0_O1_O2_chart_max_relative": max(
            row["coefficient_O0_O1_O2_chart_max_relative"] for row in endpoints
        ),
        "normalization_and_orthogonality_max_abs": max(
            row["normalization_and_orthogonality_max_abs"] for row in endpoints
        ),
        "normal_covector_transform_max_relative": max(
            row["normal_covector_transform_max_relative"] for row in endpoints
        ),
        "background_junction_max_abs": max(
            row["background_junction_max_abs"] for row in endpoints
        ),
        "background_extrinsic_oracle_max_abs": max(
            row["background_extrinsic_oracle_max_abs"] for row in endpoints
        ),
        "jet_sensitivity_max_abs": max(
            max(
                row["dB1_dgamma_error_abs"],
                row["dB2_deta_error_abs"],
            )
            for row in sensitivities
        ),
    }
    minimum_wrong_orientation_signal = min(
        row["wrong_orientation_junction_min_abs"] for row in endpoints
    )
    minimum_O1_signal = min(
        row["nontrivial_O1_coefficient_max_abs"] for row in endpoints
    )
    minimum_O2_signal = min(
        row["nontrivial_O2_coefficient_max_abs"] for row in endpoints
    )
    gamma_values = [row[1] for row in JET_SWEEP]
    eta_values = [row[2] for row in JET_SWEEP]
    checks = {
        "no_observational_inputs": True,
        "fixed_lower_and_upper_outward_orientations": {
            (row["label"], row["orientation"]) for row in endpoints
        }
        == {("lower", -1), ("upper", 1)},
        "wrong_orientation_is_detected_with_fixed_potential": (
            minimum_wrong_orientation_signal > 1.0e-3
        ),
        "multiple_positive_gamma_values_exercised": (
            len(set(gamma_values)) >= 3
            and all(np.isfinite(gamma_values))
            and all(gamma > 0.0 for gamma in gamma_values)
        ),
        "zero_and_nonzero_eta_values_exercised": (
            any(eta == 0.0 for eta in eta_values)
            and any(eta != 0.0 for eta in eta_values)
            and all(np.isfinite(eta_values))
        ),
        "bending_value_gradient_and_hessian_are_nonzero": all(
            abs(value) > 1.0e-3 for value in bending_probe.values()
        ),
        "first_and_second_order_responses_are_nonzero": (
            minimum_O1_signal > 1.0e-3 and minimum_O2_signal > 1.0e-4
        ),
        "unit_normal_and_tangent_orthogonality": maxima[
            "normalization_and_orthogonality_max_abs"
        ]
        < 1.0e-12,
        "normal_covector_transforms_between_charts": maxima[
            "normal_covector_transform_max_relative"
        ]
        < 1.0e-12,
        "bent_and_straight_charts_agree_pointwise": maxima[
            "pointwise_chart_max_relative"
        ]
        < 1.0e-11,
        "bent_and_straight_coefficients_agree_through_O2": maxima[
            "coefficient_O0_O1_O2_chart_max_relative"
        ]
        < 1.0e-9,
        "background_scalar_and_Israel_junctions": maxima[
            "background_junction_max_abs"
        ]
        < 1.0e-12,
        "background_extrinsic_curvature_matches_analytic_oracle": maxima[
            "background_extrinsic_oracle_max_abs"
        ]
        < 1.0e-12,
        "brane_jet_sensitivity_identities": maxima[
            "jet_sensitivity_max_abs"
        ]
        < 1.0e-9,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "exact_bent_induced_metric_implemented": (
            checks["bent_and_straight_charts_agree_pointwise"]
            and checks["first_and_second_order_responses_are_nonzero"]
        ),
        "exact_inclined_unit_normal_implemented": (
            checks["unit_normal_and_tangent_orthogonality"]
            and checks["normal_covector_transforms_between_charts"]
            and checks["bending_value_gradient_and_hessian_are_nonzero"]
        ),
        "exact_bent_extrinsic_curvature_implemented": (
            checks["bent_and_straight_charts_agree_pointwise"]
            and checks[
                "background_extrinsic_curvature_matches_analytic_oracle"
            ]
        ),
        "radial_gauge_straightening_verified_through_O2": (
            checks["bent_and_straight_coefficients_agree_through_O2"]
            and checks["bending_value_gradient_and_hessian_are_nonzero"]
        ),
        "background_scalar_and_Israel_junctions_recovered": checks[
            "background_scalar_and_Israel_junctions"
        ],
        "total_action_variation_reproduces_linear_junctions": False,
        "EH_GHY_normal_derivative_cancellation_verified": False,
        "nonvanishing_endpoint_profile_action_tested": False,
        "finite_gamma_compact_ADM_S2_spectrum_recovered": False,
        "finite_gamma_compact_ADM_S2_norm_recovered": False,
    }
    physical_gates["finite_gamma_bent_brane_S2_complete"] = all(
        physical_gates.values()
    )

    return {
        "schema": "holo.bent-brane-geometry-S2.v2",
        "title": "Bent-brane covariance and junction geometry through second order",
        "classification": (
            "restricted_bent_geometry_covariance_verified;"
            "total_boundary_action_S2_pending"
        ),
        "geometry": {
            "embedding": "X^A=(x^mu,u_i+epsilon*xi(x))",
            "straightening": "v=u-epsilon*xi(x)",
            "induced_metric": (
                "gamma_hat_mn=G_AB*partial_m X^A*partial_n X^B"
            ),
            "normal": (
                "n_A=s*d_A[u-u_i-epsilon*xi]/sqrt(G^BC*d_BF*d_CF)"
            ),
            "extrinsic_curvature": (
                "K_mn=-n_A*(partial_m partial_n X^A+Gamma^A_BC*"
                "partial_m X^B*partial_n X^C)"
            ),
            "scalar_junction": "B=n^A*partial_A chi+lambda'(chi_hat)",
            "israel_tensor": (
                "I_mn=K_mn-K*gamma_hat_mn+(lambda/2)*gamma_hat_mn"
            ),
            "brane_jet_sweep": [
                {"case": case, "gamma": gamma, "eta": eta}
                for case, gamma, eta in JET_SWEEP
            ],
            "fixed_endpoint_potentials": (
                "lambda0 and lambda1 belong to each BraneSpec and are not "
                "recomputed when a trial normal orientation is supplied"
            ),
        },
        "verification": {
            "endpoints": endpoints,
            "jet_sensitivities": sensitivities,
            "bending_probe": bending_probe,
            "minimum_wrong_orientation_junction_abs": (
                minimum_wrong_orientation_signal
            ),
            "minimum_nontrivial_O1_coefficient_abs": minimum_O1_signal,
            "minimum_nontrivial_O2_coefficient_abs": minimum_O2_signal,
            "maxima": maxima,
        },
        "physical_gates": physical_gates,
        "checks": checks,
        "inputs": {
            "observational_tables_read": [],
            "synthetic_geometry_only": True,
        },
        "next_decisive_test": (
            "Vary the complete EH+GHY+lambda action on nonvanishing endpoint "
            "profiles, recover the linear scalar and Israel junction operators, "
            "then reproduce the finite-gamma spectrum and quadratic norm."
        ),
        "evidence_boundary": (
            "This verifies a restricted synthetic one-spatial-direction geometry, "
            "fixed endpoint orientations, brane-jet entry and gauge straightening "
            "through O(epsilon^2). It does not yet verify the full scalar ADM "
            "sector, total action variation, compact spectrum, norm or cubic endpoint."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        raise SystemExit("bent-brane geometry certificate failed")
    _write(OUTPUT, result)
    maxima = result["verification"]["maxima"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[bent-straight O2 max relative] "
        f"{maxima['coefficient_O0_O1_O2_chart_max_relative']:.3e}"
    )
    print(
        "[finite gamma brane S2 complete] "
        f"{result['physical_gates']['finite_gamma_bent_brane_S2_complete']}"
    )
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
