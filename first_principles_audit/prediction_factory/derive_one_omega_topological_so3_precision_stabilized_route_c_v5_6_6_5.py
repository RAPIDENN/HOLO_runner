#!/usr/bin/env python3
"""Precision-stabilized coordinate jets for the independent Route C.

The v5.6.6.4 campaign is intentionally retained as a red, sub-resolved
receipt.  This additive correction changes neither the literal v5.2 action nor
the primitive spectral family.  It evaluates the same fixed-collar pullback in
``numpy.longdouble`` and uses an explicit nine-point, eighth-order coordinate
stencil before handing the resulting jets to Route C's literal local density.

This module is a numerical correction layer, not a new action route and not a
C1/N1 promotion.  It imports no Torch/AD or NumPy/FD5 action evaluator.
"""

from __future__ import annotations

import itertools
import hashlib
import json
import math
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3
    as route_c,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
PREVIOUS_SOURCE = HERE / (
    "derive_one_omega_topological_so3_multidirection_convergence_"
    "route_c_v5_6_6_4.py"
)
PREVIOUS_TEST = HERE / (
    "test_one_omega_topological_so3_multidirection_convergence_"
    "route_c_v5_6_6_4.py"
)
PREVIOUS_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_multidirection_convergence_"
    "route_c_v5_6_6_4.json"
)
TEST = HERE / (
    "test_one_omega_topological_so3_precision_stabilized_"
    "route_c_v5_6_6_5.py"
)
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_precision_stabilized_"
    "route_c_v5_6_6_5.json"
)
PREVIOUS_SOURCE_SHA256 = "2d9b7f4cbda863f4468247c8a607d22a272cf740bfb99c51bfbe63497a349cca"
PREVIOUS_TEST_SHA256 = "58cc63875586a39796acbb86542fd4b7baf8f46e0520a0a268c6ba4c5995996c"
PREVIOUS_ARTIFACT_SHA256 = "23579f90fc535a71d088e992a4f6f49aea515a8ab9c7b04bb6b7cc89bff9ddb8"
SCHEMA = (
    "holo.one-omega-topological-so3-precision-stabilized-"
    "route-c-v5-6-6-5.v1"
)

LD = np.longdouble
STABLE_THETA_STEP = LD("0.03")
STABLE_RHO_STEP = LD("0.03")
RADIAL_ORDERS = (12, 14, 16)
TANGENTIAL_ORDERS = (11, 13, 15)
RADIAL_ATOL = 5.0e-3
RADIAL_RTOL = 5.0e-7
TANGENTIAL_ATOL = 5.0e-8
TANGENTIAL_RTOL = 5.0e-10

# Centered nine-point coefficients.  The first and second derivatives are
# exact through polynomial degree eight and have O(h^8) truncation error.
FIRST_WEIGHTS = {
    -4: LD(1) / LD(280),
    -3: -LD(4) / LD(105),
    -2: LD(1) / LD(5),
    -1: -LD(4) / LD(5),
    1: LD(4) / LD(5),
    2: -LD(1) / LD(5),
    3: LD(4) / LD(105),
    4: -LD(1) / LD(280),
}
SECOND_WEIGHTS = {
    -4: -LD(1) / LD(560),
    -3: LD(8) / LD(315),
    -2: -LD(1) / LD(5),
    -1: LD(8) / LD(5),
    0: -LD(205) / LD(72),
    1: LD(8) / LD(5),
    2: -LD(1) / LD(5),
    3: LD(8) / LD(315),
    4: -LD(1) / LD(560),
}


class RouteCPrecisionError(ValueError):
    """A stabilized-jet invariant or selected primitive contract drifted."""


def _sym_ld(vector: np.ndarray, dimension: int) -> np.ndarray:
    pairs = route_c.SYMMETRIC4 if dimension == 4 else route_c.SYMMETRIC5
    result = np.zeros((dimension, dimension), dtype=LD)
    for value, (left, right) in zip(np.asarray(vector, dtype=LD), pairs):
        result[left, right] = value
        result[right, left] = value
    return result


def _sym_vector_ld(matrix: np.ndarray, dimension: int = 5) -> np.ndarray:
    pairs = route_c.SYMMETRIC4 if dimension == 4 else route_c.SYMMETRIC5
    value = np.asarray(matrix, dtype=LD)
    return np.asarray([value[left, right] for left, right in pairs], dtype=LD)


def _hat_ld(vector: np.ndarray) -> np.ndarray:
    x, y, z = np.asarray(vector, dtype=LD)
    return np.asarray(
        ((LD(0), -z, y), (z, LD(0), -x), (-y, x, LD(0))), dtype=LD
    )


def _vee_ld(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=LD)
    return np.asarray((value[2, 1], value[0, 2], value[1, 0]), dtype=LD)


def _basis_values_ld(N: int, theta: LD, derivative: int = 0) -> np.ndarray:
    if N not in (1, 2, 3):
        raise RouteCPrecisionError(f"unsupported selected truncation N={N}")
    result = np.zeros(N, dtype=LD)
    if derivative == 0:
        result[0] = LD(1)
    if N >= 2:
        cycle = derivative % 4
        result[1] = (
            np.cos(theta)
            if cycle == 0
            else -np.sin(theta)
            if cycle == 1
            else -np.cos(theta)
            if cycle == 2
            else np.sin(theta)
        )
    if N >= 3:
        cycle = derivative % 4
        result[2] = (
            np.sin(theta)
            if cycle == 0
            else np.cos(theta)
            if cycle == 1
            else -np.sin(theta)
            if cycle == 2
            else -np.cos(theta)
        )
    return result


def _series_ld(
    coefficients: np.ndarray, theta: float | LD, derivative: int = 0
) -> np.ndarray:
    values = np.asarray(coefficients, dtype=LD)
    weights = _basis_values_ld(values.shape[0], LD(theta), derivative)
    return np.tensordot(weights, values, axes=(0, 0))


def _so3_exp_ld(vector: np.ndarray) -> np.ndarray:
    value = np.asarray(vector, dtype=LD)
    angle = np.sqrt(np.sum(value * value, dtype=LD))
    generator = _hat_ld(value)
    identity = np.eye(3, dtype=LD)
    if angle < LD("1e-12"):
        return identity + generator + LD("0.5") * generator @ generator
    return (
        identity
        + np.sin(angle) * generator / angle
        + (LD(1) - np.cos(angle)) * (generator @ generator) / (angle * angle)
    )


def _matrix_theta_derivative_ld(
    function: Callable[[LD], np.ndarray], theta: float | LD
) -> np.ndarray:
    total: np.ndarray | None = None
    center = LD(theta)
    for offset, coefficient in FIRST_WEIGHTS.items():
        sample = np.asarray(
            function(center + LD(offset) * STABLE_THETA_STEP), dtype=LD
        )
        total = coefficient * sample if total is None else total + coefficient * sample
    if total is None:
        raise RouteCPrecisionError("empty coordinate stencil")
    return total / STABLE_THETA_STEP


def _trace_ambient_value_ld(
    free: np.ndarray,
    contract: Mapping[str, Any],
    side: str,
    theta: float | LD,
) -> tuple[np.ndarray, LD, LD]:
    if side not in route_c.SIDES:
        raise RouteCPrecisionError(f"unknown side: {side}")
    free_ld = np.asarray(free, dtype=LD)
    theta_ld = LD(theta)
    gamma = _sym_ld(
        _series_ld(route_c._layout_block(free_ld, contract, "common.gamma"), theta_ld),
        4,
    )
    log_omega = LD(
        _series_ld(
            route_c._layout_block(free_ld, contract, "common.log_Omega"), theta_ld
        )[0]
    )
    varphi_e0 = _series_ld(
        route_c._layout_block(free_ld, contract, "common.varphi_E0"), theta_ld
    )
    A_e0 = _series_ld(
        route_c._layout_block(free_ld, contract, "common.A_E0"), theta_ld
    )
    q_coeff = route_c._layout_block(free_ld, contract, "Q_frame.q")

    def q_rotation(point: LD) -> np.ndarray:
        return _so3_exp_ld(_series_ld(q_coeff, point))

    S = q_rotation(theta_ld)
    dS_theta = _matrix_theta_derivative_ld(q_rotation, theta_ld)
    dS = np.zeros((4, 3, 3), dtype=LD)
    dS[0] = dS_theta
    dS[1] = dS_theta

    Y_coeff = route_c._layout_block(free_ld, contract, f"{side}.Y")
    Y = LD(_series_ld(Y_coeff, theta_ld)[0])
    Y_theta = LD(_series_ld(Y_coeff, theta_ld, 1)[0])
    Y_gradient = np.asarray((Y_theta, Y_theta, LD(0), LD(0)), dtype=LD)
    metric_free = _series_ld(
        route_c._layout_block(free_ld, contract, f"{side}.metric_free"), theta_ld
    )
    adapted_cross = metric_free[:4]
    normal_metric = LD(metric_free[4])
    upper = (
        gamma
        - np.outer(adapted_cross, Y_gradient)
        - np.outer(Y_gradient, adapted_cross)
        + normal_metric * np.outer(Y_gradient, Y_gradient)
    )
    ambient_cross = adapted_cross - normal_metric * Y_gradient
    metric = np.empty((5, 5), dtype=LD)
    metric[:4, :4] = upper
    metric[:4, 4] = ambient_cross
    metric[4, :4] = ambient_cross
    metric[4, 4] = normal_metric

    r_coeff = route_c._layout_block(free_ld, contract, f"{side}.r_E0")

    def r0_rotation(point: LD) -> np.ndarray:
        return _so3_exp_ld(_series_ld(r_coeff, point))

    R0 = r0_rotation(theta_ld)
    dR0_theta = _matrix_theta_derivative_ld(r0_rotation, theta_ld)
    R = S @ R0
    dR_theta = dS_theta @ R0 + S @ dR0_theta
    dR = np.zeros((4, 3, 3), dtype=LD)
    dR[0] = dR_theta
    dR[1] = dR_theta

    varphi_q = S @ varphi_e0
    A_q_matrix = np.empty((4, 3, 3), dtype=LD)
    for mu in range(4):
        A_q_matrix[mu] = S @ _hat_ld(A_e0[mu]) @ S.T - dS[mu] @ S.T
    A_source = np.empty((4, 3), dtype=LD)
    for mu in range(4):
        A_source[mu] = _vee_ld(R.T @ A_q_matrix[mu] @ R + R.T @ dR[mu])
    phi_source = R.T @ varphi_q
    A_perp = _series_ld(
        route_c._layout_block(free_ld, contract, f"{side}.A_perp"), theta_ld
    )
    A_full = np.empty((5, 3), dtype=LD)
    A_full[:4] = A_source - Y_gradient[:, None] * A_perp[None, :]
    A_full[4] = A_perp
    B_full = _series_ld(
        route_c._layout_block(free_ld, contract, f"{side}.B0_full"), theta_ld
    )

    result = np.empty(64, dtype=LD)
    result[:15] = _sym_vector_ld(metric)
    result[15] = log_omega
    result[16:19] = phi_source
    result[19:34] = A_full.reshape(15)
    result[34:64] = B_full.reshape(30)
    return result, Y, Y_theta


def _radial_bumps_ld(rho: float | LD, K: int) -> np.ndarray:
    value = LD(rho)
    x = LD(2) * value - LD(1)
    envelope = LD(64) * value**3 * (LD(1) - value) ** 3
    legendre = (LD(1), x, (LD(3) * x * x - LD(1)) / LD(2))
    if K > len(legendre):
        raise RouteCPrecisionError(f"unsupported selected radial order K={K}")
    return np.asarray([envelope * legendre[index] for index in range(K)], dtype=LD)


def _ambient_value_ld(
    free: np.ndarray,
    contract: Mapping[str, Any],
    side: str,
    theta: float | LD,
    rho: float | LD,
) -> tuple[np.ndarray, LD, LD]:
    trace, Y, Y_theta = _trace_ambient_value_ld(free, contract, side, theta)
    free_ld = np.asarray(free, dtype=LD)
    theta_ld = LD(theta)
    rho_ld = LD(rho)
    jet = _series_ld(
        route_c._layout_block(free_ld, contract, f"{side}.boundary_jet_J1"),
        theta_ld,
    )
    interior = _series_ld(
        route_c._layout_block(free_ld, contract, f"{side}.interior_bump_C"),
        theta_ld,
    )
    reference = np.zeros(64, dtype=LD)
    reference[:15] = _sym_vector_ld(
        np.asarray(route_c.REFERENCE_METRIC, dtype=LD)
    )
    h0 = (
        LD(1)
        - LD(10) * rho_ld**3
        + LD(15) * rho_ld**4
        - LD(6) * rho_ld**5
    )
    h1 = rho_ld * h0
    bumps = _radial_bumps_ld(rho_ld, interior.shape[0])
    value = reference + h0 * (trace - reference) + h1 * jet
    value = value + np.sum(bumps[:, None] * interior, axis=0, dtype=LD)
    return value, Y, Y_theta


def _antisymmetric_tensor_ld(values: np.ndarray) -> np.ndarray:
    tensor = np.zeros((5, 5, 5, 3), dtype=LD)
    for stored, triple in zip(np.asarray(values, dtype=LD), route_c.B_TRIPLES):
        for permutation in itertools.permutations(range(3)):
            indices = tuple(triple[index] for index in permutation)
            inversions = sum(
                int(permutation[i] > permutation[j])
                for i in range(3)
                for j in range(i + 1, 3)
            )
            tensor[indices] = (LD(-1) if inversions % 2 else LD(1)) * stored
    return tensor


def _determinant3_ld(matrix: np.ndarray) -> LD:
    value = np.asarray(matrix, dtype=LD)
    return LD(
        value[0, 0]
        * (value[1, 1] * value[2, 2] - value[1, 2] * value[2, 1])
        - value[0, 1]
        * (value[1, 0] * value[2, 2] - value[1, 2] * value[2, 0])
        + value[0, 2]
        * (value[1, 0] * value[2, 1] - value[1, 1] * value[2, 0])
    )


def _pullback_vector_ld(
    free: np.ndarray,
    contract: Mapping[str, Any],
    side: str,
    theta: float | LD,
    rho: float | LD,
) -> tuple[np.ndarray, np.ndarray]:
    ambient, _Y, Y_theta = _ambient_value_ld(free, contract, side, theta, rho)
    sign = LD(route_c.SIDE_RADIAL_SIGN[side])
    Y_gradient = np.asarray((Y_theta, Y_theta, LD(0), LD(0)), dtype=LD)
    jacobian = np.zeros((5, 5), dtype=LD)
    jacobian[:4, :4] = np.eye(4, dtype=LD)
    jacobian[4, :4] = Y_gradient
    jacobian[4, 4] = sign

    metric = _sym_ld(ambient[:15], 5)
    pulled_metric = jacobian.T @ metric @ jacobian
    connection = ambient[19:34].reshape(5, 3)
    pulled_connection = jacobian.T @ connection
    ambient_B = _antisymmetric_tensor_ld(ambient[34:64].reshape(10, 3))
    pulled_B = np.empty((10, 3), dtype=LD)
    for position, target in enumerate(route_c.B_TRIPLES):
        value = np.zeros(3, dtype=LD)
        for source in route_c.B_TRIPLES:
            minor = jacobian[np.ix_(source, target)]
            value += _determinant3_ld(minor) * ambient_B[source]
        pulled_B[position] = value

    actual = np.empty(64, dtype=LD)
    actual[:15] = _sym_vector_ld(pulled_metric)
    actual[15:19] = ambient[15:19]
    actual[19:34] = pulled_connection.reshape(15)
    actual[34:64] = pulled_B.reshape(30)
    reference_metric = (
        jacobian.T @ np.asarray(route_c.REFERENCE_METRIC, dtype=LD) @ jacobian
    )
    return actual, _sym_vector_ld(reference_metric)


def _weighted_sum(
    sample: Callable[[int, int], tuple[np.ndarray, np.ndarray]],
    terms: list[tuple[LD, tuple[int, int]]],
    position: int,
) -> np.ndarray:
    result: np.ndarray | None = None
    for coefficient, key in terms:
        value = np.asarray(sample(*key)[position], dtype=LD)
        result = coefficient * value if result is None else result + coefficient * value
    if result is None:
        raise RouteCPrecisionError("empty stabilized stencil")
    return result


def _nine_point_jet_ld(
    function: Callable[[LD, LD], tuple[np.ndarray, np.ndarray]],
    theta: float | LD,
    rho: float | LD,
) -> Mapping[str, np.ndarray]:
    center_theta = LD(theta)
    center_rho = LD(rho)
    cache: dict[tuple[int, int], tuple[np.ndarray, np.ndarray]] = {}

    def sample(i: int, j: int) -> tuple[np.ndarray, np.ndarray]:
        key = (i, j)
        if key not in cache:
            cache[key] = function(
                center_theta + LD(i) * STABLE_THETA_STEP,
                center_rho + LD(j) * STABLE_RHO_STEP,
            )
        return cache[key]

    theta_first = [(coefficient, (offset, 0)) for offset, coefficient in FIRST_WEIGHTS.items()]
    rho_first = [(coefficient, (0, offset)) for offset, coefficient in FIRST_WEIGHTS.items()]
    theta_second = [(coefficient, (offset, 0)) for offset, coefficient in SECOND_WEIGHTS.items()]
    rho_second = [(coefficient, (0, offset)) for offset, coefficient in SECOND_WEIGHTS.items()]
    mixed = [
        (left_weight * right_weight, (left, right))
        for left, left_weight in FIRST_WEIGHTS.items()
        for right, right_weight in FIRST_WEIGHTS.items()
    ]
    result: dict[str, np.ndarray] = {}
    for part, position in (("actual", 0), ("reference_metric", 1)):
        result[f"{part}_q"] = np.asarray(sample(0, 0)[position], dtype=LD)
        result[f"{part}_qt"] = _weighted_sum(sample, theta_first, position) / STABLE_THETA_STEP
        result[f"{part}_qr"] = _weighted_sum(sample, rho_first, position) / STABLE_RHO_STEP
        result[f"{part}_qtt"] = _weighted_sum(sample, theta_second, position) / (
            STABLE_THETA_STEP**2
        )
        result[f"{part}_qrr"] = _weighted_sum(sample, rho_second, position) / (
            STABLE_RHO_STEP**2
        )
        result[f"{part}_qtr"] = _weighted_sum(sample, mixed, position) / (
            STABLE_THETA_STEP * STABLE_RHO_STEP
        )
    return result


def stable_bulk_jet(
    free: np.ndarray,
    contract: Mapping[str, Any],
    side: str,
    theta: float,
    rho: float,
) -> Mapping[str, np.ndarray]:
    raw = _nine_point_jet_ld(
        lambda moved_theta, moved_rho: _pullback_vector_ld(
            np.asarray(free, dtype=LD),
            contract,
            side,
            moved_theta,
            moved_rho,
        ),
        LD(theta),
        LD(rho),
    )
    return {
        suffix: np.concatenate(
            (raw[f"actual_{suffix}"], raw[f"reference_metric_{suffix}"])
        )
        for suffix in ("q", "qt", "qr", "qtt", "qtr", "qrr")
    }


@contextmanager
def stabilized_route_c_bulk_jet() -> Iterator[None]:
    """Temporarily inject the stabilized primitive-to-jet map into Route C."""

    original = route_c._bulk_jet
    route_c._bulk_jet = stable_bulk_jet
    try:
        yield
    finally:
        route_c._bulk_jet = original


def evaluate_direct_member_stable(
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    *,
    curve_name: str = "joint_all_primitive_classes_control_candidate",
    tangential_order: int = route_c.PRIMARY_TANGENTIAL_ORDER,
    radial_order: int = route_c.PRIMARY_RADIAL_ORDER,
    free_step: float = route_c.FREE_JVP_STEP,
) -> Mapping[str, Any]:
    with stabilized_route_c_bulk_jet():
        return route_c.evaluate_direct_member(
            bundle,
            member,
            curve_name=curve_name,
            tangential_order=tangential_order,
            radial_order=radial_order,
            free_step=free_step,
        )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_previous_red_receipt() -> Mapping[str, Any]:
    observed = {
        "source": _sha256(PREVIOUS_SOURCE),
        "test": _sha256(PREVIOUS_TEST),
        "artifact": _sha256(PREVIOUS_ARTIFACT),
    }
    expected = {
        "source": PREVIOUS_SOURCE_SHA256,
        "test": PREVIOUS_TEST_SHA256,
        "artifact": PREVIOUS_ARTIFACT_SHA256,
    }
    if observed != expected:
        raise RouteCPrecisionError(f"v5.6.6.4 red lineage drift: {observed}")
    payload = json.loads(PREVIOUS_ARTIFACT.read_text(encoding="utf-8"))
    decision = payload["decision"]
    if decision["route_C_all_four_directions_multi_N_pass"] is not True:
        raise RouteCPrecisionError("v5.6.6.4 four-direction lemma is not green")
    if decision["route_C_h_and_quadrature_convergence_pass"] is not False:
        raise RouteCPrecisionError("v5.6.6.4 no longer preserves the red refinement")
    if decision["restricted_spectral_family_Euler_Green_certificate_pass"] is not False:
        raise RouteCPrecisionError("v5.6.6.4 must remain fail-closed")
    return payload


def _comparison(
    left: Mapping[str, float],
    right: Mapping[str, float],
    *,
    atol: float,
    rtol: float,
) -> Mapping[str, Any]:
    if set(left) != set(right):
        raise RouteCPrecisionError("component key drift in stabilized refinement")
    rows: dict[str, Any] = {}
    all_pass = True
    for name in sorted(left):
        left_value = float(left[name])
        right_value = float(right[name])
        difference = abs(left_value - right_value)
        scale = max(abs(left_value), abs(right_value))
        tolerance = atol + rtol * scale
        passed = difference <= tolerance
        rows[name] = {
            "left": left_value,
            "right": right_value,
            "raw_residual": left_value - right_value,
            "absolute_difference": difference,
            "normalized_difference": difference / max(1.0, scale),
            "fixed_tolerance": tolerance,
            "difference_over_tolerance": difference / tolerance,
            "pass": passed,
        }
        all_pass = all_pass and passed
    return {
        "absolute_tolerance": atol,
        "relative_tolerance": rtol,
        "rows": rows,
        "key_aligned_L2_difference": float(
            np.linalg.norm(
                np.asarray(
                    [float(left[name]) - float(right[name]) for name in sorted(left)]
                )
            )
        ),
        "maximum_difference_over_tolerance": max(
            row["difference_over_tolerance"] for row in rows.values()
        ),
        "pass": all_pass,
    }


def _member_refinement(
    bundle: Mapping[str, Any], member: Mapping[str, Any]
) -> Mapping[str, Any]:
    cache: dict[tuple[int, int], Mapping[str, float]] = {}

    def evaluate(tangential_order: int, radial_order: int) -> Mapping[str, float]:
        key = (tangential_order, radial_order)
        if key not in cache:
            record = evaluate_direct_member_stable(
                bundle,
                member,
                tangential_order=tangential_order,
                radial_order=radial_order,
            )
            cache[key] = record["direct_local_free_JVP_by_component"]
            print(
                "completed precision-stabilized "
                f"N={int(member['N'])} K={int(member['K'])} "
                f"Qtheta={tangential_order} Qrho={radial_order}",
                flush=True,
            )
        return cache[key]

    radial = {
        str(order): evaluate(TANGENTIAL_ORDERS[1], order)
        for order in RADIAL_ORDERS
    }
    tangential = {
        str(order): evaluate(order, RADIAL_ORDERS[1])
        for order in TANGENTIAL_ORDERS
    }
    radial_final = _comparison(
        radial["14"], radial["16"], atol=RADIAL_ATOL, rtol=RADIAL_RTOL
    )
    tangential_final = _comparison(
        tangential["13"],
        tangential["15"],
        atol=TANGENTIAL_ATOL,
        rtol=TANGENTIAL_RTOL,
    )
    return {
        "N": int(member["N"]),
        "K": int(member["K"]),
        "member_id": member["member_id"],
        "authoritative_free_central_sha256": member[
            "authoritative_free_central_f64le"
        ]["sha256"],
        "radial": {
            "fixed_tangential_order": TANGENTIAL_ORDERS[1],
            "records_by_order": radial,
            "Q14_vs_Q16": radial_final,
        },
        "tangential": {
            "fixed_radial_order": RADIAL_ORDERS[1],
            "records_by_order": tangential,
            "Q13_vs_Q15": tangential_final,
        },
        "member_precision_stabilized_convergence_pass": bool(
            radial_final["pass"] and tangential_final["pass"]
        ),
    }


def build_payload() -> Mapping[str, Any]:
    if not np.finfo(LD).eps < np.finfo(np.float64).eps:
        raise RouteCPrecisionError("numpy.longdouble is not extended on this runtime")
    previous = _read_previous_red_receipt()
    bundle = route_c.load_bundle()
    members = [_member_refinement(bundle, member) for member in bundle["primary_members"]]
    stabilized_convergence = all(
        bool(member["member_precision_stabilized_convergence_pass"])
        for member in members
    )
    previous_directions = bool(
        previous["decision"]["route_C_all_four_directions_multi_N_pass"]
    )
    return {
        "schema": SCHEMA,
        "classification": "theory_only;route_C;precision_stabilized;longdouble;stencil9_order8;multi_N;restricted_spectral_family;fail_closed",
        "decision": {
            "v5_6_6_4_red_subresolved_receipt_preserved": True,
            "route_C_all_four_directions_multi_N_pass_from_pinned_v5_6_6_4": previous_directions,
            "precision_stabilized_radial_and_tangential_convergence_pass": stabilized_convergence,
            "restricted_spectral_family_precision_correction_pass": previous_directions
            and stabilized_convergence,
            "AD_FD5_Route_C_three_way_comparison_pass": False,
            "independent_clean_process_redteam_pass": False,
            "full_mutant_campaign_pass": False,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "fixed_before_acceptance_run": {
            "coordinate_derivative": {
                "dtype": str(np.dtype(LD)),
                "mantissa_bits": int(np.finfo(LD).nmant),
                "machine_epsilon": float(np.finfo(LD).eps),
                "theta_step": float(STABLE_THETA_STEP),
                "rho_step": float(STABLE_RHO_STEP),
                "stencil_points": 9,
                "formal_order": 8,
                "mixed_derivative_is_tensor_product_of_first_derivative_stencil": True,
            },
            "radial_orders": list(RADIAL_ORDERS),
            "tangential_orders": list(TANGENTIAL_ORDERS),
            "radial_atol": RADIAL_ATOL,
            "radial_rtol": RADIAL_RTOL,
            "tangential_atol": TANGENTIAL_ATOL,
            "tangential_rtol": TANGENTIAL_RTOL,
        },
        "scientific": {
            "members": members,
            "previous_red_witness": {
                "artifact_sha256": PREVIOUS_ARTIFACT_SHA256,
                "N1_radial_Q10_Q12_pass": previous["scientific"][
                    "member_campaigns"
                ][0]["refinement"]["radial"]["Q10_vs_Q12"]["pass"],
                "N2_tangential_Q5_Q7_pass": previous["scientific"][
                    "member_campaigns"
                ][1]["refinement"]["tangential"]["Q5_vs_Q7"]["pass"],
                "N3_tangential_Q5_Q7_pass": previous["scientific"][
                    "member_campaigns"
                ][2]["refinement"]["tangential"]["Q5_vs_Q7"]["pass"],
            },
        },
        "independence_audit": {
            "Torch_or_AD_action_imported": False,
            "NumPy_FD5_action_route_imported": False,
            "literal_v5_2_action_changed": False,
            "primitive_family_changed": False,
            "same_route_C_local_density_consumed": True,
            "only_primitive_to_coordinate_jet_map_stabilized": True,
        },
        "source_pins": {
            "v5_6_6_4_source_sha256": PREVIOUS_SOURCE_SHA256,
            "v5_6_6_4_test_sha256": PREVIOUS_TEST_SHA256,
            "v5_6_6_4_red_artifact_sha256": PREVIOUS_ARTIFACT_SHA256,
            "route_C_v5_6_6_3_source_sha256": _sha256(Path(route_c.__file__)),
            "primitive_bundle_sha256": route_c.BUNDLE_SHA256,
            "literal_v5_2_action_sha256": route_c.LITERAL_V5_2_ACTION_SHA256,
        },
        "open_obligations": {
            "three_way_comparison": "compare Route C, Torch AD, and independent NumPy FD5 at identical finite quadrature and component conventions",
            "clean_room_and_mutants": "required after the three-way comparison; this correction is not a red-team",
            "uniform_continuum_bridge": "finite N=1,2,3 remains a restricted numerical certificate and does not imply density or uniform stability",
        },
        "evidence_boundary": "This additive gate repairs coordinate-jet precision and finite radial/tangential convergence while preserving v5.6.6.4 as a red sub-resolution witness. It does not promote C1_ACTION or N1_ACTION, does not open B4/B5, and proves no N-to-infinity limit.",
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST) if TEST.exists() else None,
            },
        },
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(build_payload(), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
