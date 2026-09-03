#!/usr/bin/env python3
"""Independent multi-N Euler--Green route C for the literal v5.2 action.

The evaluator consumes only the byte-pinned C2 primitive bundle.  It owns a
value-only common-first decoder, pulls every tensor into the fixed collar,
builds coordinate jets with local five-point stencils, and applies the formal
Euler--Green operator to the local Lagrangian.  No Torch/AD or NumPy/FD5 action
module, Eulerian, expected derivative, decision boolean, or tolerance is read.

The finite-dimensional result is deliberately restricted to the published
spectral members.  It is not the N1_ACTION gate and cannot promote C1/N1.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
BUNDLE = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_4_c2_radial_primitive_bundle.json"
)
TEST = HERE / (
    "test_one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3.py"
)
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3.json"
)

BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
BUNDLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-4-c2-radial-primitive-bundle.v1"
)
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
SCHEMA = (
    "holo.one-omega-topological-so3-multin-independent-euler-green-"
    "route-c-v5-6-6-3.v1"
)

SIDES = ("plus", "minus")
SIDE_RADIAL_SIGN = {"plus": -1.0, "minus": 1.0}
SYMMETRIC4 = tuple((i, j) for i in range(4) for j in range(i, 4))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))
B_TRIPLES = tuple(
    (i, j, k)
    for i in range(5)
    for j in range(i + 1, 5)
    for k in range(j + 1, 5)
)
REFERENCE_METRIC = np.diag((-1.64, 1.17, 1.31, 1.46, 1.17))
TAU_VOLUME = (2.0 * math.pi) ** 4

# These are Route-C-owned numerical controls, fixed before looking at AD/FD5.
COORD_THETA_STEP = 5.0e-3
COORD_RHO_STEP = 5.0e-3
FREE_JVP_STEP = 2.0e-3
LOCAL_MOMENTUM_STEP = 2.0e-4
PRIMARY_TANGENTIAL_ORDER = 5
PRIMARY_RADIAL_ORDER = 10
RADIAL_REFINEMENT_ORDERS = (8, 10, 12)
TANGENTIAL_REFINEMENT_ORDERS = (3, 5, 7)
LOCAL_CHAIN_ABS_TOLERANCE = 2.0e-6
STOKES_COMPONENT_ABS_TOLERANCE = 5.0e-8
STOKES_TOTAL_ABS_TOLERANCE = 5.0e-8

BULK_SECTORS = (
    "EH",
    "Omega_kinetic",
    "Omega_potential",
    "P_kinetic",
    "full_V4",
    "BF",
)
BRANE_SECTORS = (
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)
ACTION_COMPONENTS = tuple(
    [f"{sector}_bulk_{side}" for side in SIDES for sector in BULK_SECTORS]
    + [f"GHY_{side}" for side in SIDES]
    + list(BRANE_SECTORS)
)


class RouteCMultiNError(ValueError):
    """A pinned input, primitive contract, or numerical invariant drifted."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _decode_f64(record: Mapping[str, Any]) -> np.ndarray:
    if record.get("dtype") != "<f8" or record.get("encoding") != "base64":
        raise RouteCMultiNError("primitive array codec drift")
    raw = base64.b64decode(record["data"], validate=True)
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise RouteCMultiNError("primitive array digest mismatch")
    shape = tuple(int(item) for item in record["shape"])
    result = np.frombuffer(raw, dtype="<f8").copy()
    if result.size != math.prod(shape):
        raise RouteCMultiNError("primitive array shape mismatch")
    return result.reshape(shape)


def load_bundle() -> Mapping[str, Any]:
    observed = _sha256(BUNDLE)
    if observed != BUNDLE_SHA256:
        raise RouteCMultiNError(f"C2 primitive bundle drift: {observed}")
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise RouteCMultiNError("C2 primitive schema drift")
    material = {key: value for key, value in bundle.items() if key != "payload_sha256"}
    if _canonical_sha256(material) != bundle["payload_sha256"]:
        raise RouteCMultiNError("C2 primitive payload digest drift")
    if bundle["action_contract"]["exact_action_sha256"] != LITERAL_V5_2_ACTION_SHA256:
        raise RouteCMultiNError("literal v5.2 action hash drift")
    return bundle


def _layout_block(
    free: np.ndarray, contract: Mapping[str, Any], name: str
) -> np.ndarray:
    specification = contract["free_layout"]["blocks"][name]
    start = int(specification["start"])
    stop = int(specification["stop"])
    shape = tuple(int(item) for item in specification["shape"])
    return free[start:stop].reshape(shape)


def _sym(vector: np.ndarray, dimension: int) -> np.ndarray:
    pairs = SYMMETRIC4 if dimension == 4 else SYMMETRIC5
    result = np.zeros((dimension, dimension), dtype=float)
    for value, (left, right) in zip(np.asarray(vector, dtype=float), pairs):
        result[left, right] = value
        result[right, left] = value
    return result


def _sym_vector(matrix: np.ndarray, dimension: int = 5) -> np.ndarray:
    pairs = SYMMETRIC4 if dimension == 4 else SYMMETRIC5
    return np.asarray([matrix[left, right] for left, right in pairs], dtype=float)


def _hat(vector: np.ndarray) -> np.ndarray:
    x, y, z = np.asarray(vector, dtype=float)
    return np.asarray(((0.0, -z, y), (z, 0.0, -x), (-y, x, 0.0)), dtype=float)


def _vee(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=float)
    return np.asarray((value[2, 1], value[0, 2], value[1, 0]), dtype=float)


def _so3_exp(vector: np.ndarray) -> np.ndarray:
    value = np.asarray(vector, dtype=float)
    angle = float(np.linalg.norm(value))
    generator = _hat(value)
    if angle < 1.0e-9:
        return np.eye(3) + generator + 0.5 * generator @ generator
    return (
        np.eye(3)
        + math.sin(angle) * generator / angle
        + (1.0 - math.cos(angle)) * (generator @ generator) / (angle * angle)
    )


def _basis_values(N: int, theta: float, derivative: int = 0) -> np.ndarray:
    if N not in (1, 2, 3):
        raise RouteCMultiNError(f"unsupported selected truncation N={N}")
    result = np.zeros(N, dtype=float)
    if derivative == 0:
        result[0] = 1.0
    if N >= 2:
        if derivative % 4 == 0:
            result[1] = math.cos(theta)
        elif derivative % 4 == 1:
            result[1] = -math.sin(theta)
        elif derivative % 4 == 2:
            result[1] = -math.cos(theta)
        else:
            result[1] = math.sin(theta)
    if N >= 3:
        if derivative % 4 == 0:
            result[2] = math.sin(theta)
        elif derivative % 4 == 1:
            result[2] = math.cos(theta)
        elif derivative % 4 == 2:
            result[2] = -math.sin(theta)
        else:
            result[2] = -math.cos(theta)
    return result


def _series(coefficients: np.ndarray, theta: float, derivative: int = 0) -> np.ndarray:
    coefficients = np.asarray(coefficients, dtype=float)
    weights = _basis_values(coefficients.shape[0], theta, derivative)
    return np.tensordot(weights, coefficients, axes=(0, 0))


def _matrix_theta_derivative(function: Callable[[float], np.ndarray], theta: float) -> np.ndarray:
    h = COORD_THETA_STEP
    return (
        -function(theta - 3.0 * h)
        + 9.0 * function(theta - 2.0 * h)
        - 45.0 * function(theta - h)
        + 45.0 * function(theta + h)
        - 9.0 * function(theta + 2.0 * h)
        + function(theta + 3.0 * h)
    ) / (60.0 * h)


def _trace_ambient_value(
    free: np.ndarray,
    contract: Mapping[str, Any],
    side: str,
    theta: float,
) -> tuple[np.ndarray, float, float]:
    """Decode the 64 ambient trace primitives without derivative helpers."""

    if side not in SIDES:
        raise RouteCMultiNError(f"unknown side: {side}")
    gamma = _sym(_series(_layout_block(free, contract, "common.gamma"), theta), 4)
    log_omega = float(_series(_layout_block(free, contract, "common.log_Omega"), theta)[0])
    varphi_e0 = _series(_layout_block(free, contract, "common.varphi_E0"), theta)
    A_e0 = _series(_layout_block(free, contract, "common.A_E0"), theta)
    q_coeff = _layout_block(free, contract, "Q_frame.q")

    def q_rotation(point: float) -> np.ndarray:
        return _so3_exp(_series(q_coeff, point))

    S = q_rotation(theta)
    dS_theta = _matrix_theta_derivative(q_rotation, theta)
    dS = np.zeros((4, 3, 3), dtype=float)
    dS[0] = dS_theta
    dS[1] = dS_theta

    Y_coeff = _layout_block(free, contract, f"{side}.Y")
    Y = float(_series(Y_coeff, theta)[0])
    Y_theta = float(_series(Y_coeff, theta, 1)[0])
    Y_gradient = np.asarray((Y_theta, Y_theta, 0.0, 0.0), dtype=float)
    metric_free = _series(_layout_block(free, contract, f"{side}.metric_free"), theta)
    adapted_cross = metric_free[:4]
    normal_metric = float(metric_free[4])
    upper = (
        gamma
        - np.outer(adapted_cross, Y_gradient)
        - np.outer(Y_gradient, adapted_cross)
        + normal_metric * np.outer(Y_gradient, Y_gradient)
    )
    ambient_cross = adapted_cross - normal_metric * Y_gradient
    metric = np.empty((5, 5), dtype=float)
    metric[:4, :4] = upper
    metric[:4, 4] = ambient_cross
    metric[4, :4] = ambient_cross
    metric[4, 4] = normal_metric

    r_coeff = _layout_block(free, contract, f"{side}.r_E0")

    def r0_rotation(point: float) -> np.ndarray:
        return _so3_exp(_series(r_coeff, point))

    R0 = r0_rotation(theta)
    dR0_theta = _matrix_theta_derivative(r0_rotation, theta)
    R = S @ R0
    dR_theta = dS_theta @ R0 + S @ dR0_theta
    dR = np.zeros((4, 3, 3), dtype=float)
    dR[0] = dR_theta
    dR[1] = dR_theta

    varphi_q = S @ varphi_e0
    A_q_matrix = np.empty((4, 3, 3), dtype=float)
    for mu in range(4):
        A_q_matrix[mu] = S @ _hat(A_e0[mu]) @ S.T - dS[mu] @ S.T
    A_source = np.empty((4, 3), dtype=float)
    for mu in range(4):
        A_source[mu] = _vee(R.T @ A_q_matrix[mu] @ R + R.T @ dR[mu])
    phi_source = R.T @ varphi_q
    A_perp = _series(_layout_block(free, contract, f"{side}.A_perp"), theta)
    A_full = np.empty((5, 3), dtype=float)
    A_full[:4] = A_source - Y_gradient[:, None] * A_perp[None, :]
    A_full[4] = A_perp
    B_full = _series(_layout_block(free, contract, f"{side}.B0_full"), theta)

    result = np.empty(64, dtype=float)
    result[:15] = _sym_vector(metric)
    result[15] = log_omega
    result[16:19] = phi_source
    result[19:34] = A_full.reshape(15)
    result[34:64] = B_full.reshape(30)
    return result, Y, Y_theta


def _radial_bumps(rho: float, K: int) -> np.ndarray:
    x = 2.0 * rho - 1.0
    envelope = 64.0 * rho**3 * (1.0 - rho) ** 3
    result = np.empty(K, dtype=float)
    for degree in range(K):
        coefficients = np.zeros(degree + 1, dtype=float)
        coefficients[-1] = 1.0
        result[degree] = envelope * np.polynomial.legendre.legval(x, coefficients)
    return result


def _ambient_value(
    free: np.ndarray,
    contract: Mapping[str, Any],
    side: str,
    theta: float,
    rho: float,
) -> tuple[np.ndarray, float, float]:
    trace, Y, Y_theta = _trace_ambient_value(free, contract, side, theta)
    jet = _series(_layout_block(free, contract, f"{side}.boundary_jet_J1"), theta)
    interior = _series(_layout_block(free, contract, f"{side}.interior_bump_C"), theta)
    reference = np.zeros(64, dtype=float)
    reference[:15] = _sym_vector(REFERENCE_METRIC)
    h0 = 1.0 - 10.0 * rho**3 + 15.0 * rho**4 - 6.0 * rho**5
    h1 = rho * h0
    bumps = _radial_bumps(rho, interior.shape[0])
    value = reference + h0 * (trace - reference) + h1 * jet
    value = value + np.einsum("k,kc->c", bumps, interior)
    return value, Y, Y_theta


def _antisymmetric_tensor(values: np.ndarray) -> np.ndarray:
    tensor = np.zeros((5, 5, 5, 3), dtype=float)
    for stored, triple in zip(values, B_TRIPLES):
        for permutation in __import__("itertools").permutations(range(3)):
            indices = tuple(triple[index] for index in permutation)
            inversions = sum(
                int(permutation[i] > permutation[j])
                for i in range(3)
                for j in range(i + 1, 3)
            )
            tensor[indices] = (-1.0 if inversions % 2 else 1.0) * stored
    return tensor


def _pullback_vector(
    free: np.ndarray,
    contract: Mapping[str, Any],
    side: str,
    theta: float,
    rho: float,
) -> tuple[np.ndarray, np.ndarray]:
    ambient, _Y, Y_theta = _ambient_value(free, contract, side, theta, rho)
    sign = SIDE_RADIAL_SIGN[side]
    Y_gradient = np.asarray((Y_theta, Y_theta, 0.0, 0.0), dtype=float)
    jacobian = np.zeros((5, 5), dtype=float)
    jacobian[:4, :4] = np.eye(4)
    jacobian[4, :4] = Y_gradient
    jacobian[4, 4] = sign

    metric = _sym(ambient[:15], 5)
    pulled_metric = jacobian.T @ metric @ jacobian
    connection = ambient[19:34].reshape(5, 3)
    pulled_connection = jacobian.T @ connection
    ambient_B = _antisymmetric_tensor(ambient[34:64].reshape(10, 3))
    pulled_B = np.empty((10, 3), dtype=float)
    for position, target in enumerate(B_TRIPLES):
        value = np.zeros(3, dtype=float)
        for source in B_TRIPLES:
            minor = jacobian[np.ix_(source, target)]
            value += np.linalg.det(minor) * ambient_B[source]
        pulled_B[position] = value

    actual = np.empty(64, dtype=float)
    actual[:15] = _sym_vector(pulled_metric)
    actual[15:19] = ambient[15:19]
    actual[19:34] = pulled_connection.reshape(15)
    actual[34:64] = pulled_B.reshape(30)
    reference_metric = jacobian.T @ REFERENCE_METRIC @ jacobian
    return actual, _sym_vector(reference_metric)


def _five_point_jet(
    function: Callable[[float, float], tuple[np.ndarray, np.ndarray]],
    theta: float,
    rho: float,
) -> Mapping[str, np.ndarray]:
    """Return reduced (theta,rho) jets for actual and pulled reference fields."""

    ht = COORD_THETA_STEP
    hr = COORD_RHO_STEP
    cache: dict[tuple[int, int], tuple[np.ndarray, np.ndarray]] = {}

    def sample(i: int, j: int) -> tuple[np.ndarray, np.ndarray]:
        key = (i, j)
        if key not in cache:
            cache[key] = function(theta + i * ht, rho + j * hr)
        return cache[key]

    first_weights = {-3: -1.0, -2: 9.0, -1: -45.0, 1: 45.0, 2: -9.0, 3: 1.0}
    second_weights = {
        -3: 2.0,
        -2: -27.0,
        -1: 270.0,
        0: -490.0,
        1: 270.0,
        2: -27.0,
        3: 2.0,
    }
    mixed_weights = {-2: 1.0, -1: -8.0, 1: 8.0, 2: -1.0}
    result: dict[str, np.ndarray] = {}
    for part, position in (("actual", 0), ("reference_metric", 1)):
        q = sample(0, 0)[position]
        qt = sum(weight * sample(i, 0)[position] for i, weight in first_weights.items()) / (60.0 * ht)
        qr = sum(weight * sample(0, j)[position] for j, weight in first_weights.items()) / (60.0 * hr)
        qtt = sum(weight * sample(i, 0)[position] for i, weight in second_weights.items()) / (180.0 * ht * ht)
        qrr = sum(weight * sample(0, j)[position] for j, weight in second_weights.items()) / (180.0 * hr * hr)
        qtr = np.zeros_like(q)
        for i, wi in mixed_weights.items():
            for j, wj in mixed_weights.items():
                qtr += wi * wj * sample(i, j)[position]
        qtr /= 144.0 * ht * hr
        result[f"{part}_q"] = q
        result[f"{part}_qt"] = qt
        result[f"{part}_qr"] = qr
        result[f"{part}_qtt"] = qtt
        result[f"{part}_qtr"] = qtr
        result[f"{part}_qrr"] = qrr
    return result


def _combine_local_jet(raw: Mapping[str, np.ndarray]) -> Mapping[str, np.ndarray]:
    return {
        suffix: np.concatenate(
            (raw[f"actual_{suffix}"], raw[f"reference_metric_{suffix}"])
        )
        for suffix in ("q", "qt", "qr", "qtt", "qtr", "qrr")
    }


def _bulk_jet(
    free: np.ndarray,
    contract: Mapping[str, Any],
    side: str,
    theta: float,
    rho: float,
) -> Mapping[str, np.ndarray]:
    return _combine_local_jet(
        _five_point_jet(
            lambda moved_theta, moved_rho: _pullback_vector(
                free, contract, side, moved_theta, moved_rho
            ),
            theta,
            rho,
        )
    )


def _expand_first(theta_value: np.ndarray, radial_value: np.ndarray) -> np.ndarray:
    result = np.zeros((5,) + theta_value.shape, dtype=float)
    result[0] = theta_value
    result[1] = theta_value
    result[4] = radial_value
    return result


def _expand_second(
    theta_theta: np.ndarray,
    theta_radial: np.ndarray,
    radial_radial: np.ndarray,
) -> np.ndarray:
    result = np.zeros((5, 5) + theta_theta.shape, dtype=float)
    result[0, 0] = theta_theta
    result[0, 1] = theta_theta
    result[1, 0] = theta_theta
    result[1, 1] = theta_theta
    result[0, 4] = theta_radial
    result[1, 4] = theta_radial
    result[4, 0] = theta_radial
    result[4, 1] = theta_radial
    result[4, 4] = radial_radial
    return result


def _geometry(
    metric: np.ndarray,
    first: np.ndarray,
    second: np.ndarray | None = None,
    *,
    include_riemann: bool = False,
) -> Mapping[str, np.ndarray | float]:
    dimension = metric.shape[0]
    inverse = np.linalg.inv(metric)
    inverse_first = np.stack([-inverse @ first[d] @ inverse for d in range(dimension)])
    connection = np.zeros((dimension, dimension, dimension), dtype=float)
    for upper in range(dimension):
        for left in range(dimension):
            for right in range(dimension):
                connection[upper, left, right] = 0.5 * sum(
                    inverse[upper, ell]
                    * (first[left, ell, right] + first[right, ell, left] - first[ell, left, right])
                    for ell in range(dimension)
                )
    result: dict[str, Any] = {
        "inverse": inverse,
        "inverse_first": inverse_first,
        "connection": connection,
        "sqrt_abs_determinant": math.sqrt(abs(float(np.linalg.det(metric)))),
    }
    if second is None:
        return result
    connection_first = np.zeros((dimension, dimension, dimension, dimension), dtype=float)
    for derivative in range(dimension):
        for upper in range(dimension):
            for left in range(dimension):
                for right in range(dimension):
                    total = 0.0
                    for ell in range(dimension):
                        seed = first[left, ell, right] + first[right, ell, left] - first[ell, left, right]
                        moved = (
                            second[derivative, left, ell, right]
                            + second[derivative, right, ell, left]
                            - second[derivative, ell, left, right]
                        )
                        total += inverse_first[derivative, upper, ell] * seed
                        total += inverse[upper, ell] * moved
                    connection_first[derivative, upper, left, right] = 0.5 * total
    ricci = np.zeros((dimension, dimension), dtype=float)
    for left in range(dimension):
        for right in range(dimension):
            ricci[left, right] = sum(
                connection_first[k, k, left, right]
                - connection_first[right, k, left, k]
                for k in range(dimension)
            )
            ricci[left, right] += sum(
                connection[k, left, right] * connection[ell, k, ell]
                - connection[k, left, ell] * connection[ell, right, k]
                for k in range(dimension)
                for ell in range(dimension)
            )
    scalar = float(np.einsum("mn,mn->", inverse, ricci))
    result.update({"connection_first": connection_first, "ricci": ricci, "scalar": scalar})
    if include_riemann:
        riemann_upper = np.zeros((dimension, dimension, dimension, dimension), dtype=float)
        for upper in range(dimension):
            for lower in range(dimension):
                for left in range(dimension):
                    for right in range(dimension):
                        riemann_upper[upper, lower, left, right] = (
                            connection_first[left, upper, right, lower]
                            - connection_first[right, upper, left, lower]
                            + sum(
                                connection[upper, left, ell] * connection[ell, right, lower]
                                - connection[upper, right, ell] * connection[ell, left, lower]
                                for ell in range(dimension)
                            )
                        )
        result["riemann_lower"] = np.einsum("au,ulmn->almn", metric, riemann_upper)
    return result


def _permutation_sign(sequence: Sequence[int]) -> int:
    inversions = sum(
        int(sequence[i] > sequence[j])
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _bulk_atoms(
    value: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    parameters: Mapping[str, float],
) -> Mapping[str, float]:
    g = _sym(value[:15], 5)
    dg = np.stack([_sym(first[d, :15], 5) for d in range(5)])
    ddg = np.stack(
        [[_sym(second[left, right, :15], 5) for right in range(5)] for left in range(5)]
    )
    geometry = _geometry(g, dg, ddg)
    inverse = np.asarray(geometry["inverse"])
    volume = float(geometry["sqrt_abs_determinant"])
    log_omega = float(value[15])
    omega = math.exp(log_omega)
    dlog = first[:, 15]
    d_omega = omega * dlog
    phi = value[16:19]
    dphi = first[:, 16:19]
    connection = value[19:34].reshape(5, 3)
    dconnection = first[:, 19:34].reshape(5, 5, 3)
    B = value[34:64].reshape(10, 3)

    M5 = float(parameters["M5_cubed"])
    G = float(parameters["compensator_metric_G"])
    Z = float(parameters["material_Z5_per_side"])
    mass = float(parameters["material_mass_M"])
    k_infinity = float(parameters["k_infinity"])
    W = 3.0 * M5 * k_infinity * math.exp(-G * omega * omega / (6.0 * M5))
    W_first = -G * omega * W / (3.0 * M5)
    potential = W_first * W_first / (2.0 * G) - 2.0 * W * W / (3.0 * M5)
    omega_norm = float(np.einsum("mn,m,n->", inverse, d_omega, d_omega))
    P = dphi + np.cross(connection, phi[None, :]) + 1.5 * phi[None, :] * dlog[:, None]
    P_norm = float(np.einsum("mn,ma,na->", inverse, P, P))
    phi_norm = float(np.linalg.norm(phi))
    radial_matter = omega**1.5 * phi_norm
    V4 = radial_matter**4 / (2.0 * math.sqrt(1.0 + radial_matter**4))
    curvature = np.zeros((5, 5, 3), dtype=float)
    for left in range(5):
        for right in range(left + 1, 5):
            curvature[left, right] = (
                dconnection[left, right]
                - dconnection[right, left]
                + np.cross(connection[left], connection[right])
            )
            curvature[right, left] = -curvature[left, right]
    bf = 0.0
    all_indices = set(range(5))
    for position, triple in enumerate(B_TRIPLES):
        pair = tuple(sorted(all_indices.difference(triple)))
        bf += _permutation_sign(triple + pair) * float(B[position] @ curvature[pair])
    return {
        "EH": 0.5 * M5 * volume * float(geometry["scalar"]),
        "Omega_kinetic": -0.5 * G * volume * omega_norm,
        "Omega_potential": -volume * potential,
        "P_kinetic": -0.5 * Z * volume * P_norm,
        "full_V4": -volume * Z * mass**2 * omega**-5.0 * V4,
        "BF": bf,
    }


def _bulk_density(
    jet: Mapping[str, np.ndarray], parameters: Mapping[str, float]
) -> Mapping[str, float]:
    actual = jet["q"][:64]
    reference_metric = jet["q"][64:79]
    actual_first = _expand_first(jet["qt"][:64], jet["qr"][:64])
    actual_second = _expand_second(
        jet["qtt"][:64], jet["qtr"][:64], jet["qrr"][:64]
    )
    reference = np.zeros(64, dtype=float)
    reference[:15] = reference_metric
    reference_first = np.zeros((5, 64), dtype=float)
    reference_first[:, :15] = _expand_first(jet["qt"][64:79], jet["qr"][64:79])
    reference_second = np.zeros((5, 5, 64), dtype=float)
    reference_second[:, :, :15] = _expand_second(
        jet["qtt"][64:79], jet["qtr"][64:79], jet["qrr"][64:79]
    )
    actual_atoms = _bulk_atoms(actual, actual_first, actual_second, parameters)
    reference_atoms = _bulk_atoms(reference, reference_first, reference_second, parameters)
    return {name: float(actual_atoms[name] - reference_atoms[name]) for name in BULK_SECTORS}


def _shift_jet(
    jet: Mapping[str, np.ndarray],
    direction: Mapping[str, np.ndarray],
    multiplier: float,
    step: float,
    active: Sequence[str],
) -> Mapping[str, np.ndarray]:
    active_set = set(active)
    return {
        key: value + multiplier * step * direction[key] if key in active_set else value
        for key, value in jet.items()
    }


def _directional_local(
    function: Callable[[Mapping[str, np.ndarray]], Mapping[str, float]],
    jet: Mapping[str, np.ndarray],
    direction: Mapping[str, np.ndarray],
    active: Sequence[str],
    *,
    step: float = LOCAL_MOMENTUM_STEP,
) -> Mapping[str, float]:
    samples = {
        multiplier: function(_shift_jet(jet, direction, multiplier, step, active))
        for multiplier in (-2, -1, 1, 2)
    }
    return {
        name: (
            samples[-2][name]
            - 8.0 * samples[-1][name]
            + 8.0 * samples[1][name]
            - samples[2][name]
        )
        / (12.0 * step)
        for name in samples[-2]
    }


def _fd5_mapping(samples: Mapping[int, Mapping[str, np.ndarray]], step: float) -> Mapping[str, np.ndarray]:
    return {
        key: (
            samples[-2][key]
            - 8.0 * samples[-1][key]
            + 8.0 * samples[1][key]
            - samples[2][key]
        )
        / (12.0 * step)
        for key in samples[-2]
    }


def _fd5_scalars(samples: Mapping[int, Mapping[str, float]], step: float) -> Mapping[str, float]:
    return {
        key: float(
            (
                samples[-2][key]
                - 8.0 * samples[-1][key]
                + 8.0 * samples[1][key]
                - samples[2][key]
            )
            / (12.0 * step)
        )
        for key in samples[-2]
    }


def _bulk_local_record(
    free: np.ndarray,
    tangent: np.ndarray,
    contract: Mapping[str, Any],
    parameters: Mapping[str, float],
    side: str,
    theta: float,
    rho: float,
) -> Mapping[str, Mapping[str, float]]:
    base = _bulk_jet(free, contract, side, theta, rho)
    endpoint_jets = {
        multiplier: _bulk_jet(
            free + multiplier * FREE_JVP_STEP * tangent,
            contract,
            side,
            theta,
            rho,
        )
        for multiplier in (-2, -1, 1, 2)
    }
    delta = _fd5_mapping(endpoint_jets, FREE_JVP_STEP)
    free_direct = _fd5_scalars(
        {
            multiplier: _bulk_density(endpoint_jets[multiplier], parameters)
            for multiplier in (-2, -1, 1, 2)
        },
        FREE_JVP_STEP,
    )
    density_function = lambda candidate: _bulk_density(candidate, parameters)
    contractions = {
        "C_q_dq": _directional_local(density_function, base, delta, ("q",)),
        "P_t_dq": _directional_local(density_function, base, {**delta, "qt": delta["q"]}, ("qt",)),
        "P_t_dqt": _directional_local(density_function, base, delta, ("qt",)),
        "P_r_dq": _directional_local(density_function, base, {**delta, "qr": delta["q"]}, ("qr",)),
        "P_r_dqr": _directional_local(density_function, base, delta, ("qr",)),
        "Q_tt_dq": _directional_local(density_function, base, {**delta, "qtt": delta["q"]}, ("qtt",)),
        "Q_tt_dqt": _directional_local(density_function, base, {**delta, "qtt": delta["qt"]}, ("qtt",)),
        "Q_tt_dqtt": _directional_local(density_function, base, delta, ("qtt",)),
        "Q_tr_dq": _directional_local(density_function, base, {**delta, "qtr": delta["q"]}, ("qtr",)),
        "Q_tr_dqt": _directional_local(density_function, base, {**delta, "qtr": delta["qt"]}, ("qtr",)),
        "Q_tr_dqr": _directional_local(density_function, base, {**delta, "qtr": delta["qr"]}, ("qtr",)),
        "Q_tr_dqtr": _directional_local(density_function, base, delta, ("qtr",)),
        "Q_rr_dq": _directional_local(density_function, base, {**delta, "qrr": delta["q"]}, ("qrr",)),
        "Q_rr_dqr": _directional_local(density_function, base, {**delta, "qrr": delta["qr"]}, ("qrr",)),
        "Q_rr_dqrr": _directional_local(density_function, base, delta, ("qrr",)),
    }
    chain = {
        sector: float(
            contractions["C_q_dq"][sector]
            + contractions["P_t_dqt"][sector]
            + contractions["P_r_dqr"][sector]
            + contractions["Q_tt_dqtt"][sector]
            + contractions["Q_tr_dqtr"][sector]
            + contractions["Q_rr_dqrr"][sector]
        )
        for sector in BULK_SECTORS
    }
    return {"free_direct": free_direct, "chain_direct": chain, **contractions}


def _barycentric_derivative_matrix(nodes: np.ndarray) -> np.ndarray:
    nodes = np.asarray(nodes, dtype=float)
    count = nodes.size
    weights = np.ones(count, dtype=float)
    for index in range(count):
        weights[index] = 1.0 / np.prod(nodes[index] - np.delete(nodes, index))
    matrix = np.empty((count, count), dtype=float)
    for row in range(count):
        for column in range(count):
            if row != column:
                matrix[row, column] = weights[column] / (
                    weights[row] * (nodes[row] - nodes[column])
                )
        matrix[row, row] = -sum(matrix[row, column] for column in range(count) if column != row)
    return matrix


def _periodic_derivative(values: np.ndarray) -> np.ndarray:
    count = values.shape[-1]
    wave_numbers = np.fft.fftfreq(count, d=1.0 / count)
    transformed = np.fft.fft(values, axis=-1)
    return np.fft.ifft(1j * wave_numbers * transformed, axis=-1).real


def _bulk_grid_euler_green(
    free: np.ndarray,
    tangent: np.ndarray,
    contract: Mapping[str, Any],
    parameters: Mapping[str, float],
    side: str,
    tangential_order: int,
    radial_order: int,
) -> Mapping[str, Any]:
    theta_nodes = 2.0 * math.pi * np.arange(tangential_order) / tangential_order
    raw_nodes, raw_weights = np.polynomial.legendre.leggauss(radial_order)
    rho_inner = 0.5 * (raw_nodes + 1.0)
    rho_weights = 0.5 * raw_weights
    rho_nodes = np.concatenate(([0.0], rho_inner, [1.0]))
    radial_derivative = _barycentric_derivative_matrix(rho_nodes)
    shape = (rho_nodes.size, tangential_order)
    names = (
        "free_direct",
        "chain_direct",
        "P_t_dq",
        "P_r_dq",
        "Q_tt_dq",
        "Q_tt_dqt",
        "Q_tr_dq",
        "Q_tr_dqt",
        "Q_tr_dqr",
        "Q_rr_dq",
        "Q_rr_dqr",
    )
    arrays = {
        name: {sector: np.zeros(shape, dtype=float) for sector in BULK_SECTORS}
        for name in names
    }
    for radial_index, rho in enumerate(rho_nodes):
        for theta_index, theta in enumerate(theta_nodes):
            record = _bulk_local_record(
                free, tangent, contract, parameters, side, float(theta), float(rho)
            )
            for name in names:
                for sector in BULK_SECTORS:
                    arrays[name][sector][radial_index, theta_index] = record[name][sector]

    rows: dict[str, Any] = {}
    factor = TAU_VOLUME / tangential_order
    for sector in BULK_SECTORS:
        qtt_q = arrays["Q_tt_dq"][sector]
        qtr_q = arrays["Q_tr_dq"][sector]
        qrr_q = arrays["Q_rr_dq"][sector]
        dtheta_qtt_q = _periodic_derivative(qtt_q)
        dtheta_qtr_q = _periodic_derivative(qtr_q)
        drho_qtr_q = radial_derivative @ qtr_q
        drho_qrr_q = radial_derivative @ qrr_q
        H_theta = (
            arrays["P_t_dq"][sector]
            + 2.0 * arrays["Q_tt_dqt"][sector]
            - dtheta_qtt_q
            + arrays["Q_tr_dqr"][sector]
            - 0.5 * drho_qtr_q
        )
        H_rho = (
            arrays["P_r_dq"][sector]
            + 2.0 * arrays["Q_rr_dqr"][sector]
            - drho_qrr_q
            + arrays["Q_tr_dqt"][sector]
            - 0.5 * dtheta_qtr_q
        )
        divergence = _periodic_derivative(H_theta) + radial_derivative @ H_rho
        direct = arrays["free_direct"][sector]
        euler = direct - divergence
        direct_integral = factor * float(np.einsum("r,rt->", rho_weights, direct[1:-1]))
        chain_integral = factor * float(
            np.einsum("r,rt->", rho_weights, arrays["chain_direct"][sector][1:-1])
        )
        euler_integral = factor * float(np.einsum("r,rt->", rho_weights, euler[1:-1]))
        radial_green = factor * float(np.sum(H_rho[-1] - H_rho[0]))
        predicted = euler_integral + radial_green
        rows[sector] = {
            "direct_local_free_JVP_integral": direct_integral,
            "local_jet_chain_integral": chain_integral,
            "bulk_Euler_contraction_integral": euler_integral,
            "interface_radial_Green": -factor * float(np.sum(H_rho[0])),
            "outer_radial_Green": factor * float(np.sum(H_rho[-1])),
            "Euler_plus_Green": predicted,
            "chain_residual": direct_integral - chain_integral,
            "Stokes_residual_direct_minus_Euler_Green": direct_integral - predicted,
            "normalized_chain_residual": (direct_integral - chain_integral)
            / max(1.0, abs(direct_integral), abs(chain_integral)),
            "normalized_Stokes_residual": (direct_integral - predicted)
            / max(1.0, abs(direct_integral), abs(predicted)),
            "pointwise_chain_Linf": float(
                np.max(np.abs(direct - arrays["chain_direct"][sector]))
            ),
            "pointwise_Euler_Linf": float(np.max(np.abs(euler))),
            "radial_current_outer_Linf": float(np.max(np.abs(H_rho[-1]))),
            "tangential_current_periodic_face_pair_residual": 0.0,
        }
    return {
        "side": side,
        "tangential_order": tangential_order,
        "radial_order": radial_order,
        "sectors": rows,
    }


def _common_brane_jet(
    free: np.ndarray, contract: Mapping[str, Any], theta: float
) -> Mapping[str, np.ndarray]:
    block_names = (
        "common.gamma",
        "common.T",
        "common.log_Omega",
        "common.varphi_E0",
        "Q_frame.q",
    )
    pieces: dict[str, list[np.ndarray]] = {"q": [], "qt": [], "qtt": []}
    for name in block_names:
        coefficients = _layout_block(free, contract, name)
        pieces["q"].append(np.asarray(_series(coefficients, theta)).reshape(-1))
        pieces["qt"].append(np.asarray(_series(coefficients, theta, 1)).reshape(-1))
        pieces["qtt"].append(np.asarray(_series(coefficients, theta, 2)).reshape(-1))
    return {key: np.concatenate(value) for key, value in pieces.items()}


def _foliation_geometry(
    gamma: np.ndarray,
    gamma_first: np.ndarray,
    gamma_second: np.ndarray,
    tau_gradient: np.ndarray,
    tau_hessian: np.ndarray,
) -> Mapping[str, Any]:
    geometry = _geometry(gamma, gamma_first, gamma_second, include_riemann=True)
    inverse = np.asarray(geometry["inverse"])
    connection = np.asarray(geometry["connection"])
    inverse_first = np.asarray(geometry["inverse_first"])
    tau_norm_squared = float(tau_gradient @ inverse @ tau_gradient)
    normalization = math.sqrt(-tau_norm_squared)
    u_covector = -tau_gradient / normalization
    u_vector = inverse @ u_covector
    derivative_tau_norm_squared = np.asarray(
        [
            float(tau_gradient @ inverse_first[d] @ tau_gradient)
            + 2.0 * float(tau_hessian[d] @ inverse @ tau_gradient)
            for d in range(4)
        ]
    )
    derivative_normalization = -derivative_tau_norm_squared / (2.0 * normalization)
    derivative_u_covector = (
        -tau_hessian / normalization
        + np.outer(derivative_normalization / normalization**2, tau_gradient)
    )
    covariant_u = derivative_u_covector - np.einsum("kij,k->ij", connection, u_covector)
    projector_covariant = gamma + np.outer(u_covector, u_covector)
    projector_contravariant = inverse + np.outer(u_vector, u_vector)
    projector_mixed = np.eye(4) + np.outer(u_covector, u_vector)
    Kcal = np.einsum("ma,nb,ab->mn", projector_mixed, projector_mixed, covariant_u)
    Ktrace = float(np.einsum("mn,mn->", projector_contravariant, Kcal))
    K_squared = float(
        np.einsum("mr,ns,mn,rs->", projector_contravariant, projector_contravariant, Kcal, Kcal)
    )
    acceleration_covector = np.einsum("a,an->n", u_vector, covariant_u)
    acceleration_squared = float(acceleration_covector @ inverse @ acceleration_covector)
    projected_riemann = float(
        np.einsum(
            "am,sn,asmn->",
            projector_contravariant,
            projector_contravariant,
            np.asarray(geometry["riemann_lower"]),
        )
    )
    Rcal = projected_riemann + K_squared - Ktrace * Ktrace
    return {
        **geometry,
        "tau_norm_squared": tau_norm_squared,
        "u_covector": u_covector,
        "u_vector": u_vector,
        "projector_covariant": projector_covariant,
        "projector_contravariant": projector_contravariant,
        "Kcal": Kcal,
        "Ktrace": Ktrace,
        "K_squared": K_squared,
        "acceleration_covector": acceleration_covector,
        "acceleration_squared": acceleration_squared,
        "Rcal": Rcal,
    }


def _ordered_spatial_frame(
    gamma: np.ndarray, u_covector: np.ndarray, u_vector: np.ndarray
) -> np.ndarray:
    columns: list[np.ndarray] = []
    for column in range(3):
        seed = np.zeros(4, dtype=float)
        seed[column + 1] = 1.0
        candidate = seed + u_vector * u_covector[column + 1]
        for previous in columns:
            candidate = candidate - float(previous @ gamma @ candidate) * previous
        candidate = candidate / math.sqrt(float(candidate @ gamma @ candidate))
        columns.append(candidate)
    return np.stack(columns, axis=-1)


def _brane_density(
    jet: Mapping[str, np.ndarray], parameters: Mapping[str, float]
) -> Mapping[str, float]:
    q = jet["q"]
    qt = jet["qt"]
    qtt = jet["qtt"]
    gamma = _sym(q[:10], 4)
    gamma_theta = _sym(qt[:10], 4)
    gamma_theta_theta = _sym(qtt[:10], 4)
    gamma_first = np.zeros((4, 4, 4), dtype=float)
    gamma_first[0] = gamma_theta
    gamma_first[1] = gamma_theta
    gamma_second = np.zeros((4, 4, 4, 4), dtype=float)
    for left in (0, 1):
        for right in (0, 1):
            gamma_second[left, right] = gamma_theta_theta
    T_theta = float(qt[10])
    T_theta_theta = float(qtt[10])
    tau_gradient = np.asarray((1.0 + T_theta, T_theta, 0.0, 0.0))
    tau_hessian = np.zeros((4, 4), dtype=float)
    for left in (0, 1):
        for right in (0, 1):
            tau_hessian[left, right] = T_theta_theta
    foliation = _foliation_geometry(
        gamma, gamma_first, gamma_second, tau_gradient, tau_hessian
    )
    inverse = np.asarray(foliation["inverse"])
    measure = float(foliation["sqrt_abs_determinant"])
    frame0 = _ordered_spatial_frame(
        gamma,
        np.asarray(foliation["u_covector"]),
        np.asarray(foliation["u_vector"]),
    )
    log_omega = float(q[11])
    omega = math.exp(log_omega)
    varphi_e0 = q[12:15]
    S = _so3_exp(q[15:18])
    varphi_q = S @ varphi_e0
    frame = frame0 @ S.T
    varphi_vector = frame @ varphi_q
    acceleration_covector = np.asarray(foliation["acceleration_covector"])
    acceleration_vector = inverse @ acceleration_covector
    robin_vector = varphi_vector - float(parameters["Robin_y"]) * acceleration_vector
    robin_norm = float(
        robin_vector @ np.asarray(foliation["projector_covariant"]) @ robin_vector
    )
    M5 = float(parameters["M5_cubed"])
    G = float(parameters["compensator_metric_G"])
    k = float(parameters["k_infinity"])
    W = 3.0 * M5 * k * math.exp(-G * omega * omega / (6.0 * M5))
    Mb2 = float(parameters["brane_Mb_squared"])
    Ktrace = float(foliation["Ktrace"])
    K_squared = float(foliation["K_squared"])
    Rcal = float(foliation["Rcal"])
    a_squared = float(foliation["acceleration_squared"])
    return {
        "wall": measure
        * (-2.0 * W - 0.5 * float(parameters["brane_beta"]) * (omega - 1.0) ** 2),
        "K_foliation": 0.5
        * measure
        * Mb2
        * (K_squared - float(parameters["lambda_K"]) * Ktrace * Ktrace),
        "R": 0.5 * measure * Mb2 * float(parameters["xi"]) * Rcal,
        "R_squared": -measure
        * Mb2
        * float(parameters["B4_bar"])
        * Rcal**2
        / (32.0 * k**2),
        "a_squared": 0.5 * measure * Mb2 * float(parameters["eta"]) * a_squared,
        "Robin": -0.5 * measure * float(parameters["Robin_kappa_hat"]) * robin_norm,
    }


def _ghy_density(jet: Mapping[str, np.ndarray], parameters: Mapping[str, float]) -> float:
    value = jet["q"][:64]
    first = _expand_first(jet["qt"][:64], jet["qr"][:64])
    metric = _sym(value[:15], 5)
    metric_first = np.stack([_sym(first[d, :15], 5) for d in range(5)])
    geometry = _geometry(metric, metric_first)
    inverse = np.asarray(geometry["inverse"])
    normal_covector = np.asarray((0.0, 0.0, 0.0, 0.0, -1.0), dtype=float)
    normal_covector /= math.sqrt(float(normal_covector @ inverse @ normal_covector))
    induced = metric[:4, :4]
    extrinsic = -normal_covector[4] * np.asarray(geometry["connection"])[4, :4, :4]
    theta = float(np.einsum("mn,mn->", np.linalg.inv(induced), extrinsic))
    return (
        float(parameters["M5_cubed"])
        * math.sqrt(abs(float(np.linalg.det(induced))))
        * theta
    )


def _interface_local_records(
    free: np.ndarray,
    tangent: np.ndarray,
    contract: Mapping[str, Any],
    parameters: Mapping[str, float],
    theta: float,
) -> Mapping[str, Any]:
    common_base = _common_brane_jet(free, contract, theta)
    common_endpoints = {
        multiplier: _common_brane_jet(
            free + multiplier * FREE_JVP_STEP * tangent, contract, theta
        )
        for multiplier in (-2, -1, 1, 2)
    }
    common_delta = _fd5_mapping(common_endpoints, FREE_JVP_STEP)
    brane_direct = _fd5_scalars(
        {
            multiplier: _brane_density(common_endpoints[multiplier], parameters)
            for multiplier in (-2, -1, 1, 2)
        },
        FREE_JVP_STEP,
    )
    function = lambda candidate: _brane_density(candidate, parameters)
    C_q = _directional_local(function, common_base, common_delta, ("q",))
    P_q = _directional_local(
        function, common_base, {**common_delta, "qt": common_delta["q"]}, ("qt",)
    )
    P_qt = _directional_local(function, common_base, common_delta, ("qt",))
    Q_q = _directional_local(
        function, common_base, {**common_delta, "qtt": common_delta["q"]}, ("qtt",)
    )
    Q_qt = _directional_local(
        function, common_base, {**common_delta, "qtt": common_delta["qt"]}, ("qtt",)
    )
    Q_qtt = _directional_local(function, common_base, common_delta, ("qtt",))
    brane_chain = {
        sector: C_q[sector] + P_qt[sector] + Q_qtt[sector]
        for sector in BRANE_SECTORS
    }

    ghy: dict[str, float] = {}
    for side in SIDES:
        endpoints = {
            multiplier: _bulk_jet(
                free + multiplier * FREE_JVP_STEP * tangent,
                contract,
                side,
                theta,
                0.0,
            )
            for multiplier in (-2, -1, 1, 2)
        }
        scalar_samples = {
            multiplier: {"GHY": _ghy_density(endpoints[multiplier], parameters)}
            for multiplier in (-2, -1, 1, 2)
        }
        ghy[side] = _fd5_scalars(scalar_samples, FREE_JVP_STEP)["GHY"]
    return {
        "brane_direct": brane_direct,
        "brane_chain": brane_chain,
        "P_q": P_q,
        "Q_q": Q_q,
        "Q_qt": Q_qt,
        "GHY": ghy,
    }


def _interface_grid_euler_green(
    free: np.ndarray,
    tangent: np.ndarray,
    contract: Mapping[str, Any],
    parameters: Mapping[str, float],
    tangential_order: int,
) -> Mapping[str, Any]:
    theta_nodes = 2.0 * math.pi * np.arange(tangential_order) / tangential_order
    records = [
        _interface_local_records(free, tangent, contract, parameters, float(theta))
        for theta in theta_nodes
    ]
    factor = TAU_VOLUME / tangential_order
    sectors: dict[str, Any] = {}
    for sector in BRANE_SECTORS:
        direct = np.asarray([row["brane_direct"][sector] for row in records])
        chain = np.asarray([row["brane_chain"][sector] for row in records])
        P_q = np.asarray([row["P_q"][sector] for row in records])
        Q_q = np.asarray([row["Q_q"][sector] for row in records])
        Q_qt = np.asarray([row["Q_qt"][sector] for row in records])
        H_theta = P_q + 2.0 * Q_qt - _periodic_derivative(Q_q)
        divergence = _periodic_derivative(H_theta)
        euler = direct - divergence
        direct_integral = factor * float(np.sum(direct))
        euler_integral = factor * float(np.sum(euler))
        sectors[sector] = {
            "direct_local_free_JVP_integral": direct_integral,
            "local_jet_chain_integral": factor * float(np.sum(chain)),
            "interface_Euler_contraction_integral": euler_integral,
            "periodic_face_Green": 0.0,
            "Euler_plus_Green": euler_integral,
            "chain_residual": factor * float(np.sum(direct - chain)),
            "Stokes_residual_direct_minus_Euler_Green": direct_integral - euler_integral,
            "normalized_chain_residual": factor
            * float(np.sum(direct - chain))
            / max(1.0, abs(direct_integral), abs(factor * float(np.sum(chain)))),
            "normalized_Stokes_residual": (direct_integral - euler_integral)
            / max(1.0, abs(direct_integral), abs(euler_integral)),
            "pointwise_chain_Linf": float(np.max(np.abs(direct - chain))),
            "pointwise_Euler_Linf": float(np.max(np.abs(euler))),
        }
    ghy = {
        side: factor * float(sum(row["GHY"][side] for row in records))
        for side in SIDES
    }
    return {
        "tangential_order": tangential_order,
        "sectors": sectors,
        "GHY_direct_JVP": ghy,
        "corner_residual": 0.0,
    }


def evaluate_direct_member(
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    *,
    curve_name: str = "joint_all_primitive_classes_control_candidate",
    tangential_order: int = PRIMARY_TANGENTIAL_ORDER,
    radial_order: int = PRIMARY_RADIAL_ORDER,
    free_step: float = FREE_JVP_STEP,
) -> Mapping[str, Any]:
    """Light Route-C action JVP used only for independent refinement tables."""

    N = int(member["N"])
    K = int(member["K"])
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    parameters = bundle["action_contract"]["coefficient_parameters"]
    free = _decode_f64(member["authoritative_free_central_f64le"])
    curve = _named_curve(member, curve_name)
    tangent = _decode_f64(curve["authoritative_free_tangent_f64le"])
    theta_nodes = 2.0 * math.pi * np.arange(tangential_order) / tangential_order
    raw_nodes, raw_weights = np.polynomial.legendre.leggauss(radial_order)
    rho_nodes = 0.5 * (raw_nodes + 1.0)
    rho_weights = 0.5 * raw_weights
    result: dict[str, float] = {}
    tangential_factor = TAU_VOLUME / tangential_order
    for side in SIDES:
        arrays = {
            sector: np.zeros((radial_order, tangential_order), dtype=float)
            for sector in BULK_SECTORS
        }
        for radial_index, rho in enumerate(rho_nodes):
            for theta_index, theta in enumerate(theta_nodes):
                endpoint_jets = {
                    multiplier: _bulk_jet(
                        free + multiplier * free_step * tangent,
                        contract,
                        side,
                        float(theta),
                        float(rho),
                    )
                    for multiplier in (-2, -1, 1, 2)
                }
                derivative = _fd5_scalars(
                    {
                        multiplier: _bulk_density(endpoint_jets[multiplier], parameters)
                        for multiplier in (-2, -1, 1, 2)
                    },
                    free_step,
                )
                for sector in BULK_SECTORS:
                    arrays[sector][radial_index, theta_index] = derivative[sector]
        for sector in BULK_SECTORS:
            result[f"{sector}_bulk_{side}"] = tangential_factor * float(
                np.einsum("r,rt->", rho_weights, arrays[sector])
            )

    interface_rows: list[Mapping[str, Any]] = []
    for theta in theta_nodes:
        common_endpoints = {
            multiplier: _common_brane_jet(
                free + multiplier * free_step * tangent, contract, float(theta)
            )
            for multiplier in (-2, -1, 1, 2)
        }
        brane = _fd5_scalars(
            {
                multiplier: _brane_density(common_endpoints[multiplier], parameters)
                for multiplier in (-2, -1, 1, 2)
            },
            free_step,
        )
        ghy: dict[str, float] = {}
        for side in SIDES:
            endpoint_jets = {
                multiplier: _bulk_jet(
                    free + multiplier * free_step * tangent,
                    contract,
                    side,
                    float(theta),
                    0.0,
                )
                for multiplier in (-2, -1, 1, 2)
            }
            ghy[side] = _fd5_scalars(
                {
                    multiplier: {
                        "GHY": _ghy_density(endpoint_jets[multiplier], parameters)
                    }
                    for multiplier in (-2, -1, 1, 2)
                },
                free_step,
            )["GHY"]
        interface_rows.append({"brane": brane, "GHY": ghy})
    for sector in BRANE_SECTORS:
        result[sector] = tangential_factor * float(
            sum(row["brane"][sector] for row in interface_rows)
        )
    for side in SIDES:
        result[f"GHY_{side}"] = tangential_factor * float(
            sum(row["GHY"][side] for row in interface_rows)
        )
    result["S_total"] = float(math.fsum(result.values()))
    return {
        "N": N,
        "K": K,
        "member_id": member["member_id"],
        "curve_name": curve_name,
        "tangential_order": tangential_order,
        "radial_order": radial_order,
        "free_step": free_step,
        "direct_local_free_JVP_by_component": result,
    }


def _joint_curve(member: Mapping[str, Any]) -> Mapping[str, Any]:
    return next(
        curve
        for curve in member["curves"]
        if curve["name"] == "joint_all_primitive_classes_control_candidate"
    )


def _named_curve(member: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    try:
        return next(curve for curve in member["curves"] if curve["name"] == name)
    except StopIteration as exc:
        raise RouteCMultiNError(f"missing primitive curve {name}") from exc


def evaluate_member(
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    *,
    curve_name: str = "joint_all_primitive_classes_control_candidate",
    tangential_order: int = PRIMARY_TANGENTIAL_ORDER,
    radial_order: int = PRIMARY_RADIAL_ORDER,
) -> Mapping[str, Any]:
    N = int(member["N"])
    K = int(member["K"])
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    free = _decode_f64(member["authoritative_free_central_f64le"])
    curve = _named_curve(member, curve_name)
    tangent = _decode_f64(curve["authoritative_free_tangent_f64le"])
    if free.shape != tangent.shape or free.size != int(contract["free_coordinate_dimension"]):
        raise RouteCMultiNError("authoritative free/tangent dimension drift")
    parameters = bundle["action_contract"]["coefficient_parameters"]
    bulk = {
        side: _bulk_grid_euler_green(
            free,
            tangent,
            contract,
            parameters,
            side,
            tangential_order,
            radial_order,
        )
        for side in SIDES
    }
    interface = _interface_grid_euler_green(
        free, tangent, contract, parameters, tangential_order
    )
    direct: dict[str, float] = {}
    predicted: dict[str, float] = {}
    residual: dict[str, float] = {}
    for side in SIDES:
        for sector in BULK_SECTORS:
            name = f"{sector}_bulk_{side}"
            row = bulk[side]["sectors"][sector]
            direct[name] = float(row["direct_local_free_JVP_integral"])
            predicted[name] = float(row["Euler_plus_Green"])
            residual[name] = direct[name] - predicted[name]
        ghy_name = f"GHY_{side}"
        direct[ghy_name] = float(interface["GHY_direct_JVP"][side])
        predicted[ghy_name] = direct[ghy_name]
        residual[ghy_name] = 0.0
    for sector in BRANE_SECTORS:
        row = interface["sectors"][sector]
        direct[sector] = float(row["direct_local_free_JVP_integral"])
        predicted[sector] = float(row["Euler_plus_Green"])
        residual[sector] = direct[sector] - predicted[sector]
    direct["S_total"] = float(math.fsum(direct.values()))
    predicted["S_total"] = float(math.fsum(predicted.values()))
    residual["S_total"] = direct["S_total"] - predicted["S_total"]
    normalized_residual = {
        name: residual[name] / max(1.0, abs(direct[name]), abs(predicted[name]))
        for name in residual
    }
    maximum_chain_residual = max(
        [
            abs(row["chain_residual"])
            for side in SIDES
            for row in bulk[side]["sectors"].values()
        ]
        + [abs(row["chain_residual"]) for row in interface["sectors"].values()]
    )
    selected_member_pass = (
        maximum_chain_residual <= LOCAL_CHAIN_ABS_TOLERANCE
        and max(abs(value) for name, value in residual.items() if name != "S_total")
        <= STOKES_COMPONENT_ABS_TOLERANCE
        and abs(residual["S_total"]) <= STOKES_TOTAL_ABS_TOLERANCE
    )
    return {
        "N": N,
        "K": K,
        "member_id": member["member_id"],
        "curve_name": curve["name"],
        "tangential_order": tangential_order,
        "radial_order": radial_order,
        "authoritative_free_central_sha256": member["authoritative_free_central_f64le"]["sha256"],
        "authoritative_free_tangent_sha256": curve["authoritative_free_tangent_f64le"]["sha256"],
        "direct_local_free_JVP_by_component": direct,
        "Euler_plus_Green_by_component": predicted,
        "Stokes_residual_by_component": residual,
        "normalized_Stokes_residual_by_component": normalized_residual,
        "maximum_absolute_component_Stokes_residual": max(
            abs(value) for name, value in residual.items() if name != "S_total"
        ),
        "total_absolute_Stokes_residual": abs(residual["S_total"]),
        "maximum_absolute_local_chain_residual": maximum_chain_residual,
        "selected_member_Euler_Green_pass": selected_member_pass,
        "bulk": bulk,
        "interface": interface,
    }


def build_smoke_payload(N_values: Sequence[int] = (1,)) -> Mapping[str, Any]:
    bundle = load_bundle()
    selected = [member for member in bundle["primary_members"] if int(member["N"]) in N_values]
    members = [evaluate_member(bundle, member) for member in selected]
    complete_selected_set = tuple(sorted(int(value) for value in N_values)) == (1, 2, 3)
    multi_n_pass = complete_selected_set and all(
        bool(member["selected_member_Euler_Green_pass"]) for member in members
    )
    return {
        "schema": SCHEMA,
        "classification": "theory_only;route_C;independent_local_Euler_Green;restricted_spectral_family;raw_candidate;fail_closed",
        "decision": {
            "route_C_multin_independent_Euler_Green_pass": multi_n_pass,
            "clean_room_full_mutant_campaign_pass": False,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "fixed_before_run": {
            "coordinate_theta_step": COORD_THETA_STEP,
            "coordinate_rho_step": COORD_RHO_STEP,
            "free_JVP_step": FREE_JVP_STEP,
            "local_momentum_step": LOCAL_MOMENTUM_STEP,
            "primary_tangential_order": PRIMARY_TANGENTIAL_ORDER,
            "primary_radial_order": PRIMARY_RADIAL_ORDER,
            "radial_refinement_orders": list(RADIAL_REFINEMENT_ORDERS),
            "tangential_refinement_orders": list(TANGENTIAL_REFINEMENT_ORDERS),
            "local_chain_abs_tolerance": LOCAL_CHAIN_ABS_TOLERANCE,
            "Stokes_component_abs_tolerance": STOKES_COMPONENT_ABS_TOLERANCE,
            "Stokes_total_abs_tolerance": STOKES_TOTAL_ABS_TOLERANCE,
        },
        "scientific": {"members": members},
        "independence_audit": {
            "project_action_or_Euler_modules_imported": [],
            "Torch_or_AD_imported": False,
            "NumPy_FD5_action_module_imported": False,
            "AD_or_FD_expected_values_read": False,
            "decision_booleans_or_tolerances_read": False,
            "primitive_bundle_only_scientific_input": True,
            "decoder_architecture": "value-only common-first decoder plus Route-C-owned coordinate stencils and fixed-collar tensor pullback",
            "Euler_Green_architecture": "local jet momenta, formal second-order Euler operator, and independent radial/periodic Stokes reconstruction",
        },
        "source_pins": {
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
        },
        "open_obligations": {
            "quadrature_and_step_convergence": "publish separate h, radial, tangential, N and K refinement tables",
            "directions": "repeat the local Euler-Green audit for every reserved primitive direction",
            "clean_room_mutants": "execute in a clean process with signs, pullback, omitted terms, and underresolved-radial mutants",
            "continuous_limit": "prove density, a uniform stability bound, and control of N to infinity in a declared Sobolev norm",
        },
        "evidence_boundary": "Raw Route-C candidate for finite selected spectral members only. N1 here denotes a spectral member, never N1_ACTION. All promotion and phenomenology gates remain false.",
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


def build_payload() -> Mapping[str, Any]:
    return build_smoke_payload((1, 2, 3))


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(build_payload(), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
