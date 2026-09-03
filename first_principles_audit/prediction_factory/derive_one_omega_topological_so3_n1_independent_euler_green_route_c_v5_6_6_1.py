#!/usr/bin/env python3
"""Independent N=1 Euler--Green route for the literal v5.2 action.

This route reads only the C2 primitive bundle.  It owns its constant-mode
decoder and evaluates the analytic bulk Euler operators and interface Green
forms without importing either the Torch/AD or NumPy/FD5 action evaluators.
The N=1 result is deliberately a smoke theorem, not the complete multi-N gate.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
BUNDLE = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_4_c2_radial_primitive_bundle.json"
)
TEST = HERE / "test_one_omega_topological_so3_n1_independent_euler_green_route_c_v5_6_6_1.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_n1_independent_euler_green_route_c_v5_6_6_1.json"

BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
BUNDLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-4-c2-radial-primitive-bundle.v1"
)
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
SCHEMA = "holo.one-omega-topological-so3-n1-independent-euler-green-route-c-v5-6-6-1.v1"

SIDES = ("plus", "minus")
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
RADIAL_GAUSS_ORDER = 10
RADIAL_REFINEMENT_ORDERS = (8, 10, 12, 16, 20)
DECODER_JVP_STEP = 1.0e-4
LOCAL_EH_JET_STEP = 1.0e-4
STOKES_FINAL_COMPONENT_ABS_TOLERANCE = 5.0e-8
STOKES_FINAL_TOTAL_ABS_TOLERANCE = 5.0e-8

ACTION_COMPONENTS = (
    "EH_bulk_plus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "GHY_minus",
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)


class RouteCError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(blob).hexdigest()


def _decode_f64(record: Mapping[str, Any]) -> np.ndarray:
    if record.get("dtype") != "<f8" or record.get("encoding") != "base64":
        raise RouteCError("primitive array codec drift")
    raw = base64.b64decode(record["data"], validate=True)
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise RouteCError("primitive array digest mismatch")
    shape = tuple(int(item) for item in record["shape"])
    value = np.frombuffer(raw, dtype="<f8").copy()
    if value.size != math.prod(shape):
        raise RouteCError("primitive array shape mismatch")
    return value.reshape(shape)


def load_primitives() -> tuple[Mapping[str, Any], Mapping[str, Any], np.ndarray, np.ndarray]:
    observed = _sha256(BUNDLE)
    if observed != BUNDLE_SHA256:
        raise RouteCError(f"C2 primitive bundle drift: {observed}")
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise RouteCError("C2 primitive schema drift")
    material = {key: value for key, value in bundle.items() if key != "payload_sha256"}
    if _canonical_sha256(material) != bundle["payload_sha256"]:
        raise RouteCError("C2 primitive payload hash drift")
    action = bundle["action_contract"]
    if action["exact_action_sha256"] != LITERAL_V5_2_ACTION_SHA256:
        raise RouteCError("literal v5.2 action hash drift")
    member = next(item for item in bundle["primary_members"] if int(item["N"]) == 1)
    if int(member["K"]) != 1 or member["member_id"] != "N1.K1.seed20260902":
        raise RouteCError("unexpected N=1 member")
    curve = next(
        item
        for item in member["curves"]
        if item["name"] == "joint_all_primitive_classes_control_candidate"
    )
    free = _decode_f64(member["authoritative_free_central_f64le"])
    tangent = _decode_f64(curve["authoritative_free_tangent_f64le"])
    contract = bundle["pointwise_decoder_contract_by_N"]["1"]
    if free.shape != (int(contract["free_coordinate_dimension"]),):
        raise RouteCError("N=1 free-coordinate dimension drift")
    if tangent.shape != free.shape:
        raise RouteCError("N=1 tangent dimension drift")
    return bundle, member, free, tangent


def _block(free: np.ndarray, layout: Mapping[str, Any], name: str) -> np.ndarray:
    spec = layout[name]
    return free[int(spec["start"]):int(spec["stop"])].reshape(tuple(spec["shape"]))[0]


def _sym(vector: np.ndarray, dimension: int) -> np.ndarray:
    pairs = SYMMETRIC4 if dimension == 4 else SYMMETRIC5
    result = np.zeros((dimension, dimension), dtype=float)
    for position, (left, right) in enumerate(pairs):
        result[left, right] = vector[position]
        result[right, left] = vector[position]
    return result


def _sym_vector(matrix: np.ndarray) -> np.ndarray:
    return np.asarray([matrix[i, j] for i, j in SYMMETRIC5], dtype=float)


def _hat(vector: np.ndarray) -> np.ndarray:
    x, y, z = map(float, vector)
    return np.asarray(((0.0, -z, y), (z, 0.0, -x), (-y, x, 0.0)), dtype=float)


def _so3_exp(vector: np.ndarray) -> np.ndarray:
    angle = float(np.linalg.norm(vector))
    generator = _hat(vector)
    if angle < 1.0e-10:
        return np.eye(3) + generator + 0.5 * generator @ generator
    return (
        np.eye(3)
        + math.sin(angle) * generator / angle
        + (1.0 - math.cos(angle)) * (generator @ generator) / (angle * angle)
    )


def _constant_boundary_decode(
    free: np.ndarray, contract: Mapping[str, Any]
) -> Mapping[str, Any]:
    layout = contract["free_layout"]["blocks"]
    gamma = _sym(_block(free, layout, "common.gamma"), 4)
    log_omega = float(_block(free, layout, "common.log_Omega")[0])
    varphi_e0 = _block(free, layout, "common.varphi_E0")
    A_e0 = _block(free, layout, "common.A_E0")
    S = _so3_exp(_block(free, layout, "Q_frame.q"))
    varphi = S @ varphi_e0
    A_common = np.einsum("ij,mj->mi", S, A_e0)
    sides: dict[str, Any] = {}
    for side in SIDES:
        metric_free = _block(free, layout, f"{side}.metric_free")
        metric = np.empty((5, 5), dtype=float)
        metric[:4, :4] = gamma
        metric[:4, 4] = metric_free[:4]
        metric[4, :4] = metric_free[:4]
        metric[4, 4] = metric_free[4]
        R0 = _so3_exp(_block(free, layout, f"{side}.r_E0"))
        R = S @ R0
        phi_source = R.T @ varphi
        A_source = np.einsum("ij,mj->mi", R.T, A_common)
        A_full = np.empty((5, 3), dtype=float)
        A_full[:4] = A_source
        A_full[4] = _block(free, layout, f"{side}.A_perp")
        sides[side] = {
            "g_trace": metric,
            "log_Omega_trace": log_omega,
            "phi_trace": phi_source,
            "A_trace": A_full,
            "B_trace": _block(free, layout, f"{side}.B0_full"),
            "J1": _block(free, layout, f"{side}.boundary_jet_J1"),
            "C": _block(free, layout, f"{side}.interior_bump_C"),
            "R_source_to_Q": R,
            "Y": float(_block(free, layout, f"{side}.Y")[0]),
        }
    return {
        "gamma": gamma,
        "log_Omega": log_omega,
        "varphi": varphi,
        "A_Sigma": A_common,
        "S_Q": S,
        "sides": sides,
    }


def _radial_profiles(rho: np.ndarray) -> Mapping[str, np.ndarray]:
    r = np.asarray(rho, dtype=float)
    h0 = 1.0 - 10.0 * r**3 + 15.0 * r**4 - 6.0 * r**5
    h0_first = -30.0 * r**2 + 60.0 * r**3 - 30.0 * r**4
    h0_second = -60.0 * r + 180.0 * r**2 - 120.0 * r**3
    h1 = r * h0
    h1_first = h0 + r * h0_first
    h1_second = 2.0 * h0_first + r * h0_second
    s = r * (1.0 - r)
    s_first = 1.0 - 2.0 * r
    bump = 64.0 * s**3
    bump_first = 192.0 * s**2 * s_first
    bump_second = 384.0 * s * s_first**2 - 384.0 * s**2
    return {
        "h0": h0,
        "h0_first": h0_first,
        "h0_second": h0_second,
        "h1": h1,
        "h1_first": h1_first,
        "h1_second": h1_second,
        "bump": bump,
        "bump_first": bump_first,
        "bump_second": bump_second,
    }


def _constant_state(
    free: np.ndarray,
    contract: Mapping[str, Any],
    rho: np.ndarray,
    side: str,
) -> Mapping[str, np.ndarray]:
    boundary = _constant_boundary_decode(free, contract)
    item = boundary["sides"][side]
    profiles = _radial_profiles(rho)
    reference = np.zeros(64, dtype=float)
    reference[:15] = _sym_vector(REFERENCE_METRIC)
    X0 = np.zeros(64, dtype=float)
    X0[:15] = _sym_vector(item["g_trace"])
    X0[15] = item["log_Omega_trace"]
    X0[16:19] = item["phi_trace"]
    X0[19:34] = item["A_trace"].reshape(15)
    X0[34:64] = item["B_trace"].reshape(30)
    J1 = item["J1"]
    C = item["C"].reshape(64)
    value = (
        reference[None, :]
        + profiles["h0"][:, None] * (X0 - reference)[None, :]
        + profiles["h1"][:, None] * J1[None, :]
        + profiles["bump"][:, None] * C[None, :]
    )
    radial = (
        profiles["h0_first"][:, None] * (X0 - reference)[None, :]
        + profiles["h1_first"][:, None] * J1[None, :]
        + profiles["bump_first"][:, None] * C[None, :]
    )
    radial_second = (
        profiles["h0_second"][:, None] * (X0 - reference)[None, :]
        + profiles["h1_second"][:, None] * J1[None, :]
        + profiles["bump_second"][:, None] * C[None, :]
    )
    collar_sign = -1.0 if side == "plus" else 1.0
    first = np.zeros((rho.size, 5, 64), dtype=float)
    second = np.zeros((rho.size, 5, 5, 64), dtype=float)
    first[:, 4] = collar_sign * radial
    second[:, 4, 4] = radial_second
    log_omega = value[:, 15]
    dlog = first[:, :, 15]
    ddlog = second[:, :, :, 15]
    omega = np.exp(log_omega)
    d_omega = omega[:, None] * dlog
    dd_omega = omega[:, None, None] * (
        ddlog + np.einsum("rm,rn->rmn", dlog, dlog)
    )
    return {
        "g": np.stack([_sym(row, 5) for row in value[:, :15]]),
        "dg": np.stack(
            [[_sym(first[r, derivative, :15], 5) for derivative in range(5)] for r in range(rho.size)]
        ),
        "ddg": np.stack(
            [
                [
                    [_sym(second[r, left, right, :15], 5) for right in range(5)]
                    for left in range(5)
                ]
                for r in range(rho.size)
            ]
        ),
        "Omega": omega,
        "dOmega": d_omega,
        "ddOmega": dd_omega,
        "log_Omega": log_omega,
        "dlog_Omega": dlog,
        "ddlog_Omega": ddlog,
        "phi": value[:, 16:19],
        "dphi": first[:, :, 16:19],
        "ddphi": second[:, :, :, 16:19],
        "A": value[:, 19:34].reshape(rho.size, 5, 3),
        "dA": first[:, :, 19:34].reshape(rho.size, 5, 5, 3),
        "B": value[:, 34:64].reshape(rho.size, 10, 3),
        "dB": first[:, :, 34:64].reshape(rho.size, 5, 10, 3),
        "collar_sign": np.asarray(collar_sign),
    }


def _tree_fd5(
    free: np.ndarray,
    tangent: np.ndarray,
    function: Any,
    step: float = DECODER_JVP_STEP,
) -> Any:
    samples = {
        multiplier: function(free + multiplier * step * tangent)
        for multiplier in (-2, -1, 1, 2)
    }

    def combine(*values: Any) -> Any:
        first = values[0]
        if isinstance(first, dict):
            return {key: combine(*(value[key] for value in values)) for key in first}
        arrays = [np.asarray(value, dtype=float) for value in values]
        result = (arrays[0] - 8.0 * arrays[1] + 8.0 * arrays[2] - arrays[3]) / (
            12.0 * step
        )
        return result

    return combine(samples[-2], samples[-1], samples[1], samples[2])


def _geometry(
    metric: np.ndarray, metric_first: np.ndarray, metric_second: np.ndarray
) -> Mapping[str, np.ndarray | float]:
    inverse = np.linalg.inv(metric)
    dimension = metric.shape[0]
    connection = np.zeros((dimension, dimension, dimension), dtype=float)
    for upper in range(dimension):
        for left in range(dimension):
            for right in range(dimension):
                connection[upper, left, right] = 0.5 * sum(
                    inverse[upper, ell]
                    * (
                        metric_first[left, ell, right]
                        + metric_first[right, ell, left]
                        - metric_first[ell, left, right]
                    )
                    for ell in range(dimension)
                )
    inverse_first = np.stack(
        [-inverse @ metric_first[derivative] @ inverse for derivative in range(dimension)]
    )
    connection_first = np.zeros((dimension, dimension, dimension, dimension), dtype=float)
    for derivative in range(dimension):
        for upper in range(dimension):
            for left in range(dimension):
                for right in range(dimension):
                    total = 0.0
                    for ell in range(dimension):
                        base = (
                            metric_first[left, ell, right]
                            + metric_first[right, ell, left]
                            - metric_first[ell, left, right]
                        )
                        moved = (
                            metric_second[derivative, left, ell, right]
                            + metric_second[derivative, right, ell, left]
                            - metric_second[derivative, ell, left, right]
                        )
                        total += inverse_first[derivative, upper, ell] * base
                        total += inverse[upper, ell] * moved
                    connection_first[derivative, upper, left, right] = 0.5 * total
    ricci = np.zeros((dimension, dimension), dtype=float)
    for left in range(dimension):
        for right in range(dimension):
            derivative = sum(
                connection_first[k, k, left, right]
                - connection_first[right, k, left, k]
                for k in range(dimension)
            )
            quadratic = 0.0
            for k in range(dimension):
                for ell in range(dimension):
                    quadratic += (
                        connection[k, left, right] * connection[ell, k, ell]
                        - connection[k, left, ell] * connection[ell, right, k]
                    )
            ricci[left, right] = derivative + quadratic
    scalar = float(np.einsum("mn,mn->", inverse, ricci))
    return {
        "inverse": inverse,
        "inverse_first": inverse_first,
        "connection": connection,
        "ricci": ricci,
        "scalar": scalar,
    }


def _superpotential(omega: float, parameters: Mapping[str, float]) -> tuple[float, float, float]:
    M5 = float(parameters["M5_cubed"])
    G = float(parameters["compensator_metric_G"])
    k = float(parameters["k_infinity"])
    W = 3.0 * M5 * k * math.exp(-G * omega * omega / (6.0 * M5))
    first = -G * omega * W / (3.0 * M5)
    second = W * (G * G * omega * omega / (9.0 * M5 * M5) - G / (3.0 * M5))
    return W, first, second


def _curvature(A: np.ndarray, dA: np.ndarray) -> np.ndarray:
    result = np.zeros((5, 5, 3), dtype=float)
    for left in range(5):
        for right in range(left + 1, 5):
            value = dA[left, right] - dA[right, left] + np.cross(A[left], A[right])
            result[left, right] = value
            result[right, left] = -value
    return result


def _permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        int(sequence[i] > sequence[j])
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _bulk_euler_green_side(
    state: Mapping[str, np.ndarray],
    delta: Mapping[str, np.ndarray],
    boundary_state: Mapping[str, np.ndarray],
    boundary_delta: Mapping[str, np.ndarray],
    weights: np.ndarray,
    parameters: Mapping[str, float],
    side: str,
) -> tuple[dict[str, float], dict[str, Any]]:
    M5 = float(parameters["M5_cubed"])
    G = float(parameters["compensator_metric_G"])
    Z = float(parameters["material_Z5_per_side"])
    mass = float(parameters["material_mass_M"])
    kappa_bf = float(parameters["kappa_BF_inner_product"])
    scalar_integrands = {
        "EH": np.zeros(weights.size),
        "Omega_kinetic": np.zeros(weights.size),
        "Omega_potential": np.zeros(weights.size),
        "P_kinetic": np.zeros(weights.size),
        "full_V4": np.zeros(weights.size),
        "BF": np.zeros(weights.size),
    }
    pointwise_euler_norms: dict[str, list[float]] = {
        key: [] for key in scalar_integrands
    }
    for radial in range(weights.size):
        g = state["g"][radial]
        dg = state["dg"][radial]
        ddg = state["ddg"][radial]
        moved_g = delta["g"][radial]
        geometry = _geometry(g, dg, ddg)
        inverse = np.asarray(geometry["inverse"])
        connection = np.asarray(geometry["connection"])
        ricci = np.asarray(geometry["ricci"])
        scalar = float(geometry["scalar"])
        volume = math.sqrt(-float(np.linalg.det(g)))
        einstein_cov = ricci - 0.5 * g * scalar
        einstein_up = inverse @ einstein_cov @ inverse
        eh = -0.5 * M5 * volume * float(np.einsum("mn,mn->", einstein_up, moved_g))
        scalar_integrands["EH"][radial] = eh
        pointwise_euler_norms["EH"].append(float(np.linalg.norm(einstein_up)))

        omega = float(state["Omega"][radial])
        d_omega = state["dOmega"][radial]
        dd_omega = state["ddOmega"][radial]
        moved_omega = float(delta["Omega"][radial])
        raised_omega = inverse @ d_omega
        omega_norm = float(d_omega @ raised_omega)
        covariant_hessian = dd_omega.copy()
        for left in range(5):
            for right in range(5):
                covariant_hessian[left, right] -= float(connection[:, left, right] @ d_omega)
        box_omega = float(np.einsum("mn,mn->", inverse, covariant_hessian))
        omega_metric = volume * (
            -0.25 * G * inverse * omega_norm
            + 0.5 * G * np.outer(raised_omega, raised_omega)
        )
        scalar_integrands["Omega_kinetic"][radial] = (
            volume * G * box_omega * moved_omega
            + float(np.einsum("mn,mn->", omega_metric, moved_g))
        )
        pointwise_euler_norms["Omega_kinetic"].append(abs(G * box_omega))

        W, W_first, W_second = _superpotential(omega, parameters)
        potential = W_first * W_first / (2.0 * G) - 2.0 * W * W / (3.0 * M5)
        potential_first = W_first * W_second / G - 4.0 * W * W_first / (3.0 * M5)
        potential_metric = -0.5 * volume * potential * inverse
        scalar_integrands["Omega_potential"][radial] = (
            -volume * potential_first * moved_omega
            + float(np.einsum("mn,mn->", potential_metric, moved_g))
        )
        pointwise_euler_norms["Omega_potential"].append(abs(potential_first))

        phi = state["phi"][radial]
        dphi = state["dphi"][radial]
        ddphi = state["ddphi"][radial]
        A = state["A"][radial]
        dA = state["dA"][radial]
        dlog = state["dlog_Omega"][radial]
        ddlog = state["ddlog_Omega"][radial]
        P = np.empty((5, 3), dtype=float)
        dP = np.empty((5, 5, 3), dtype=float)
        for index in range(5):
            P[index] = dphi[index] + np.cross(A[index], phi) + 1.5 * phi * dlog[index]
        for derivative in range(5):
            for index in range(5):
                dP[derivative, index] = (
                    ddphi[derivative, index]
                    + np.cross(dA[derivative, index], phi)
                    + np.cross(A[index], dphi[derivative])
                    + 1.5
                    * (dphi[derivative] * dlog[index] + phi * ddlog[derivative, index])
                )
        P_up = np.einsum("mn,na->ma", inverse, P)
        inverse_first = np.asarray(geometry["inverse_first"])
        dP_up = np.empty((5, 5, 3), dtype=float)
        for derivative in range(5):
            dP_up[derivative] = (
                np.einsum("mn,na->ma", inverse_first[derivative], P)
                + np.einsum("mn,na->ma", inverse, dP[derivative])
            )
        divergence_P = sum(dP_up[index, index] for index in range(5))
        for index in range(5):
            for source in range(5):
                divergence_P += connection[index, index, source] * P_up[source]
            divergence_P += np.cross(A[index], P_up[index])
        c_dot_P = 1.5 * sum(dlog[index] * P_up[index] for index in range(5))
        E_phi = Z * (divergence_P - c_dot_P)
        J = np.asarray([float(phi @ P_up[index]) for index in range(5)])
        dJ = np.empty((5, 5), dtype=float)
        for derivative in range(5):
            for index in range(5):
                dJ[derivative, index] = float(
                    dphi[derivative] @ P_up[index] + phi @ dP_up[derivative, index]
                )
        divergence_J = sum(dJ[index, index] for index in range(5))
        for index in range(5):
            for source in range(5):
                divergence_J += connection[index, index, source] * J[source]
        E_omega_P = 1.5 * Z * divergence_J / omega
        E_A = np.stack([-Z * np.cross(phi, P_up[index]) for index in range(5)])
        P_norm = float(np.einsum("ma,ma->", P, P_up))
        P_metric = volume * (
            -0.25 * Z * inverse * P_norm
            + 0.5 * Z * np.einsum("ma,na->mn", P_up, P_up)
        )
        p_value = (
            volume * float(E_phi @ delta["phi"][radial])
            + volume * E_omega_P * moved_omega
            + volume * float(np.einsum("ma,ma->", E_A, delta["A"][radial]))
            + float(np.einsum("mn,mn->", P_metric, moved_g))
        )
        scalar_integrands["P_kinetic"][radial] = p_value
        pointwise_euler_norms["P_kinetic"].append(
            float(np.linalg.norm(E_phi)) + abs(E_omega_P) + float(np.linalg.norm(E_A))
        )

        norm_phi = float(np.linalg.norm(phi))
        argument = omega**1.5 * norm_phi
        V4 = argument**4 / (2.0 * math.sqrt(1.0 + argument**4))
        V4_first = argument**3 * (2.0 + argument**4) / (1.0 + argument**4) ** 1.5
        phi_hat = phi / norm_phi
        E_phi_V4 = -Z * mass**2 * omega**-3.5 * V4_first * phi_hat
        E_omega_V4 = Z * mass**2 * omega**-6.0 * (
            5.0 * V4 - 1.5 * argument * V4_first
        )
        V4_metric = -0.5 * volume * Z * mass**2 * omega**-5.0 * V4 * inverse
        scalar_integrands["full_V4"][radial] = (
            volume * float(E_phi_V4 @ delta["phi"][radial])
            + volume * E_omega_V4 * moved_omega
            + float(np.einsum("mn,mn->", V4_metric, moved_g))
        )
        pointwise_euler_norms["full_V4"].append(
            float(np.linalg.norm(E_phi_V4)) + abs(E_omega_V4)
        )

        curvature = _curvature(A, dA)
        E_B = np.zeros((10, 3), dtype=float)
        E_A_BF = np.zeros((5, 3), dtype=float)
        collar = float(state["collar_sign"])
        all_indices = set(range(5))
        for position, triple in enumerate(B_TRIPLES):
            pair = tuple(sorted(all_indices.difference(triple)))
            permutation = float(_permutation_sign(triple + pair))
            coefficient = collar * permutation
            B_value = state["B"][radial, position]
            E_B[position] = coefficient * curvature[pair[0], pair[1]]
            left, right = pair
            E_A_BF[left] += coefficient * np.cross(A[right], B_value)
            E_A_BF[right] += coefficient * np.cross(B_value, A[left])
            if left == 4:
                E_A_BF[right] -= coefficient * state["dB"][radial, 4, position]
            if right == 4:
                E_A_BF[left] += coefficient * state["dB"][radial, 4, position]
        bf_value = kappa_bf * (
            float(np.einsum("ma,ma->", E_A_BF, delta["A"][radial]))
            + float(np.einsum("ia,ia->", E_B, delta["B"][radial]))
        )
        scalar_integrands["BF"][radial] = bf_value
        pointwise_euler_norms["BF"].append(
            float(np.linalg.norm(E_A_BF)) + float(np.linalg.norm(E_B))
        )

    integrated = {
        key: TAU_VOLUME * float(np.dot(weights, values))
        for key, values in scalar_integrands.items()
    }

    g0 = boundary_state["g"][0]
    dg0 = boundary_state["dg"][0]
    geometry0 = _geometry(g0, dg0, boundary_state["ddg"][0])
    inverse0 = np.asarray(geometry0["inverse"])
    raw_normal = np.asarray((0.0, 0.0, 0.0, 0.0, 1.0))
    outward_sign = 1.0 if side == "plus" else -1.0
    normal_covector = outward_sign * raw_normal / math.sqrt(float(raw_normal @ inverse0 @ raw_normal))
    normal_vector = inverse0 @ normal_covector
    induced = g0[:4, :4]
    induced_inverse = np.linalg.inv(induced)
    measure = math.sqrt(-float(np.linalg.det(induced)))
    connection0 = np.asarray(geometry0["connection"])
    extrinsic = -np.einsum("p,pmn->mn", normal_covector, connection0[:, :4, :4])
    theta = float(np.einsum("mn,mn->", induced_inverse, extrinsic))
    pi_up = induced_inverse @ (extrinsic - theta * induced) @ induced_inverse
    brown_york = -0.5 * M5 * TAU_VOLUME * measure * float(
        np.einsum("mn,mn->", pi_up, boundary_delta["g"][0, :4, :4])
    )
    P0 = np.empty((5, 3), dtype=float)
    for index in range(5):
        P0[index] = (
            boundary_state["dphi"][0, index]
            + np.cross(boundary_state["A"][0, index], boundary_state["phi"][0])
            + 1.5
            * boundary_state["phi"][0]
            * boundary_state["dlog_Omega"][0, index]
        )
    nP = np.einsum("m,ma->a", normal_vector, P0)
    nOmega = float(normal_vector @ boundary_state["dOmega"][0])
    omega_green = -TAU_VOLUME * measure * G * nOmega * float(boundary_delta["Omega"][0])
    p_green = -TAU_VOLUME * measure * Z * (
        float(nP @ boundary_delta["phi"][0])
        + 1.5
        * float(boundary_state["phi"][0] @ nP)
        * float(boundary_delta["Omega"][0])
        / float(boundary_state["Omega"][0])
    )
    bf_green_density = 0.0
    all_indices = set(range(5))
    for position, triple in enumerate(B_TRIPLES):
        pair = tuple(sorted(all_indices.difference(triple)))
        left, right = pair
        permutation = float(_permutation_sign(triple + pair))
        B_value = boundary_state["B"][0, position]
        if left == 4:
            bf_green_density -= permutation * float(B_value @ boundary_delta["A"][0, right])
        if right == 4:
            bf_green_density += permutation * float(B_value @ boundary_delta["A"][0, left])
    bf_green = TAU_VOLUME * kappa_bf * bf_green_density
    greens = {
        "EH_plus_GHY_Brown_York": brown_york,
        "Omega_kinetic": omega_green,
        "P_kinetic": p_green,
        "BF": bf_green,
    }
    ledger = {
        key: {
            "bulk_Euler": integrated[key],
            "interface_Green": greens.get(key, 0.0),
            "outer_Green": 0.0,
            "pointwise_Euler_activity_Linf": max(pointwise_euler_norms[key]),
        }
        for key in integrated
    }
    return integrated, {
        "ledger": ledger,
        "brown_york_combined_boundary": brown_york,
        "normal_covector": normal_covector.tolist(),
        "interface_measure": measure,
        "extrinsic_trace": theta,
    }


def _direct_bulk_jet_variation_side(
    state: Mapping[str, np.ndarray],
    delta: Mapping[str, np.ndarray],
    weights: np.ndarray,
    parameters: Mapping[str, float],
) -> Mapping[str, float]:
    """Differentiate the local densities before any integration by parts."""

    M5 = float(parameters["M5_cubed"])
    G = float(parameters["compensator_metric_G"])
    Z = float(parameters["material_Z5_per_side"])
    mass = float(parameters["material_mass_M"])
    kappa_bf = float(parameters["kappa_BF_inner_product"])
    rows = {
        name: np.zeros(weights.size, dtype=float)
        for name in (
            "EH",
            "Omega_kinetic",
            "Omega_potential",
            "P_kinetic",
            "full_V4",
            "BF",
        )
    }
    for radial in range(weights.size):
        g = state["g"][radial]
        dg = state["dg"][radial]
        ddg = state["ddg"][radial]
        moved_g = delta["g"][radial]
        moved_dg = delta["dg"][radial]
        moved_ddg = delta["ddg"][radial]

        def eh_density(multiplier: float) -> float:
            candidate_g = g + multiplier * LOCAL_EH_JET_STEP * moved_g
            candidate_dg = dg + multiplier * LOCAL_EH_JET_STEP * moved_dg
            candidate_ddg = ddg + multiplier * LOCAL_EH_JET_STEP * moved_ddg
            geometry = _geometry(candidate_g, candidate_dg, candidate_ddg)
            volume = math.sqrt(-float(np.linalg.det(candidate_g)))
            return 0.5 * M5 * volume * float(geometry["scalar"])

        rows["EH"][radial] = (
            eh_density(-2.0)
            - 8.0 * eh_density(-1.0)
            + 8.0 * eh_density(1.0)
            - eh_density(2.0)
        ) / (12.0 * LOCAL_EH_JET_STEP)

        geometry = _geometry(g, dg, ddg)
        inverse = np.asarray(geometry["inverse"])
        volume = math.sqrt(-float(np.linalg.det(g)))
        omega = float(state["Omega"][radial])
        moved_omega = float(delta["Omega"][radial])
        d_omega = state["dOmega"][radial]
        moved_d_omega = delta["dOmega"][radial]
        raised_omega = inverse @ d_omega
        omega_norm = float(d_omega @ raised_omega)
        omega_metric = volume * (
            -0.25 * G * inverse * omega_norm
            + 0.5 * G * np.outer(raised_omega, raised_omega)
        )
        rows["Omega_kinetic"][radial] = (
            -G * volume * float(raised_omega @ moved_d_omega)
            + float(np.einsum("mn,mn->", omega_metric, moved_g))
        )

        W, W_first, W_second = _superpotential(omega, parameters)
        potential = W_first * W_first / (2.0 * G) - 2.0 * W * W / (3.0 * M5)
        potential_first = W_first * W_second / G - 4.0 * W * W_first / (3.0 * M5)
        potential_metric = -0.5 * volume * potential * inverse
        rows["Omega_potential"][radial] = (
            -volume * potential_first * moved_omega
            + float(np.einsum("mn,mn->", potential_metric, moved_g))
        )

        phi = state["phi"][radial]
        moved_phi = delta["phi"][radial]
        A = state["A"][radial]
        moved_A = delta["A"][radial]
        dphi = state["dphi"][radial]
        moved_dphi = delta["dphi"][radial]
        dlog = state["dlog_Omega"][radial]
        moved_dlog = delta["dlog_Omega"][radial]
        P = np.empty((5, 3), dtype=float)
        moved_P = np.empty((5, 3), dtype=float)
        for index in range(5):
            P[index] = dphi[index] + np.cross(A[index], phi) + 1.5 * phi * dlog[index]
            moved_P[index] = (
                moved_dphi[index]
                + np.cross(moved_A[index], phi)
                + np.cross(A[index], moved_phi)
                + 1.5 * (moved_phi * dlog[index] + phi * moved_dlog[index])
            )
        P_up = np.einsum("mn,na->ma", inverse, P)
        P_norm = float(np.einsum("ma,ma->", P, P_up))
        P_metric = volume * (
            -0.25 * Z * inverse * P_norm
            + 0.5 * Z * np.einsum("ma,na->mn", P_up, P_up)
        )
        rows["P_kinetic"][radial] = (
            -Z * volume * float(np.einsum("ma,ma->", P_up, moved_P))
            + float(np.einsum("mn,mn->", P_metric, moved_g))
        )

        norm_phi = float(np.linalg.norm(phi))
        argument = omega**1.5 * norm_phi
        V4 = argument**4 / (2.0 * math.sqrt(1.0 + argument**4))
        V4_first = argument**3 * (2.0 + argument**4) / (1.0 + argument**4) ** 1.5
        E_phi = -Z * mass**2 * omega**-3.5 * V4_first * phi / norm_phi
        E_omega = Z * mass**2 * omega**-6.0 * (
            5.0 * V4 - 1.5 * argument * V4_first
        )
        V4_metric = -0.5 * volume * Z * mass**2 * omega**-5.0 * V4 * inverse
        rows["full_V4"][radial] = (
            volume * float(E_phi @ moved_phi)
            + volume * E_omega * moved_omega
            + float(np.einsum("mn,mn->", V4_metric, moved_g))
        )

        curvature = _curvature(A, state["dA"][radial])
        moved_curvature = np.zeros((5, 5, 3), dtype=float)
        for left in range(5):
            for right in range(left + 1, 5):
                value = (
                    delta["dA"][radial, left, right]
                    - delta["dA"][radial, right, left]
                    + np.cross(moved_A[left], A[right])
                    + np.cross(A[left], moved_A[right])
                )
                moved_curvature[left, right] = value
                moved_curvature[right, left] = -value
        bf = 0.0
        all_indices = set(range(5))
        collar = float(state["collar_sign"])
        for position, triple in enumerate(B_TRIPLES):
            pair = tuple(sorted(all_indices.difference(triple)))
            coefficient = collar * float(_permutation_sign(triple + pair))
            bf += coefficient * (
                float(delta["B"][radial, position] @ curvature[pair[0], pair[1]])
                + float(state["B"][radial, position] @ moved_curvature[pair[0], pair[1]])
            )
        rows["BF"][radial] = kappa_bf * bf
    return {
        key: TAU_VOLUME * float(np.dot(weights, values)) for key, values in rows.items()
    }


def _ghy_value(
    free: np.ndarray,
    contract: Mapping[str, Any],
    parameters: Mapping[str, float],
    side: str,
) -> float:
    state = _constant_state(free, contract, np.asarray([0.0]), side)
    g = state["g"][0]
    geometry = _geometry(g, state["dg"][0], state["ddg"][0])
    inverse = np.asarray(geometry["inverse"])
    raw_normal = np.asarray((0.0, 0.0, 0.0, 0.0, 1.0))
    outward_sign = 1.0 if side == "plus" else -1.0
    normal = outward_sign * raw_normal / math.sqrt(float(raw_normal @ inverse @ raw_normal))
    induced = g[:4, :4]
    measure = math.sqrt(-float(np.linalg.det(induced)))
    connection = np.asarray(geometry["connection"])
    extrinsic = -np.einsum("p,pmn->mn", normal, connection[:, :4, :4])
    theta = float(np.einsum("mn,mn->", np.linalg.inv(induced), extrinsic))
    return TAU_VOLUME * float(parameters["M5_cubed"]) * measure * theta


def _interface_values(
    free: np.ndarray,
    contract: Mapping[str, Any],
    parameters: Mapping[str, float],
) -> Mapping[str, float]:
    boundary = _constant_boundary_decode(free, contract)
    gamma = boundary["gamma"]
    measure = math.sqrt(-float(np.linalg.det(gamma)))
    omega = math.exp(float(boundary["log_Omega"]))
    W, _first, _second = _superpotential(omega, parameters)
    beta = float(parameters["brane_beta"])
    kappa = float(parameters["Robin_kappa_hat"])
    result = {
        "GHY_plus": _ghy_value(free, contract, parameters, "plus"),
        "GHY_minus": _ghy_value(free, contract, parameters, "minus"),
        "wall": TAU_VOLUME
        * measure
        * (-(2.0 * W + 0.5 * beta * (omega - 1.0) ** 2)),
        "K_foliation": 0.0,
        "R": 0.0,
        "R_squared": 0.0,
        "a_squared": 0.0,
        "Robin": TAU_VOLUME
        * measure
        * (-0.5 * kappa * float(boundary["varphi"] @ boundary["varphi"])),
    }
    return result


def _evaluate_radial_order(
    free: np.ndarray,
    tangent: np.ndarray,
    contract: Mapping[str, Any],
    parameters: Mapping[str, float],
    radial_order: int,
) -> Mapping[str, Any]:
    radial_nodes_raw, radial_weights_raw = np.polynomial.legendre.leggauss(radial_order)
    rho = 0.5 * (radial_nodes_raw + 1.0)
    weights = 0.5 * radial_weights_raw
    boundary_rho = np.asarray([0.0])
    predicted: dict[str, float] = {}
    direct: dict[str, float] = {}
    side_ledgers: dict[str, Any] = {}
    outer_tangent_linf = 0.0
    for side in SIDES:
        state = _constant_state(free, contract, rho, side)
        delta = _tree_fd5(
            free, tangent, lambda value, s=side: _constant_state(value, contract, rho, s)
        )
        boundary_state = _constant_state(free, contract, boundary_rho, side)
        boundary_delta = _tree_fd5(
            free,
            tangent,
            lambda value, s=side: _constant_state(value, contract, boundary_rho, s),
        )
        outer_delta = _tree_fd5(
            free,
            tangent,
            lambda value, s=side: _constant_state(value, contract, np.asarray([1.0]), s),
        )
        for value in outer_delta.values():
            outer_tangent_linf = max(outer_tangent_linf, float(np.max(np.abs(value))))
        bulk, audit = _bulk_euler_green_side(
            state, delta, boundary_state, boundary_delta, weights, parameters, side
        )
        direct_bulk = _direct_bulk_jet_variation_side(state, delta, weights, parameters)
        side_ledgers[side] = audit
        for sector in (
            "Omega_kinetic",
            "Omega_potential",
            "P_kinetic",
            "full_V4",
            "BF",
        ):
            green = audit["ledger"][sector]["interface_Green"]
            predicted[f"{sector}_bulk_{side}"] = bulk[sector] + green
            direct[f"{sector}_bulk_{side}"] = direct_bulk[sector]
            audit["ledger"][sector]["direct_local_jet_variation"] = direct_bulk[sector]
            audit["ledger"][sector]["Stokes_residual_direct_minus_Euler_Green"] = (
                direct_bulk[sector] - predicted[f"{sector}_bulk_{side}"]
            )

    interface_derivative = _tree_fd5(
        free, tangent, lambda value: _interface_values(value, contract, parameters)
    )
    for side in SIDES:
        by = side_ledgers[side]["brown_york_combined_boundary"]
        ghy = float(interface_derivative[f"GHY_{side}"])
        predicted[f"GHY_{side}"] = ghy
        direct[f"GHY_{side}"] = ghy
        predicted[f"EH_bulk_{side}"] = (
            side_ledgers[side]["ledger"]["EH"]["bulk_Euler"] + by - ghy
        )
        direct_bulk_eh = _direct_bulk_jet_variation_side(
            _constant_state(free, contract, rho, side),
            _tree_fd5(
                free,
                tangent,
                lambda value, s=side: _constant_state(value, contract, rho, s),
            ),
            weights,
            parameters,
        )["EH"]
        direct[f"EH_bulk_{side}"] = direct_bulk_eh
        side_ledgers[side]["EH_GHY_split"] = {
            "EH_bulk_Euler": side_ledgers[side]["ledger"]["EH"]["bulk_Euler"],
            "combined_Brown_York_boundary": by,
            "independent_GHY_variation": ghy,
            "inferred_raw_EH_Green": by - ghy,
            "predicted_EH_variation": predicted[f"EH_bulk_{side}"],
            "predicted_GHY_variation": ghy,
            "direct_local_EH_jet_variation": direct_bulk_eh,
            "Stokes_residual_direct_EH_minus_Euler_Green": (
                direct_bulk_eh - predicted[f"EH_bulk_{side}"]
            ),
        }
    for name in ("wall", "K_foliation", "R", "R_squared", "a_squared", "Robin"):
        predicted[name] = float(interface_derivative[name])
        direct[name] = float(interface_derivative[name])
    if set(predicted) != set(ACTION_COMPONENTS):
        raise RouteCError("N=1 Euler-Green component coverage drift")
    if set(direct) != set(ACTION_COMPONENTS):
        raise RouteCError("N=1 direct local-jet component coverage drift")
    predicted["S_total"] = float(math.fsum(predicted.values()))
    direct["S_total"] = float(math.fsum(direct.values()))
    residual = {name: direct[name] - predicted[name] for name in direct}
    return {
        "radial_Gauss_order": radial_order,
        "predicted_Euler_Green_by_component": predicted,
        "direct_local_jet_JVP_by_component": direct,
        "Stokes_residual_direct_minus_Euler_Green": residual,
        "maximum_absolute_component_Stokes_residual": max(
            abs(value) for name, value in residual.items() if name != "S_total"
        ),
        "total_absolute_Stokes_residual": abs(residual["S_total"]),
        "side_ledgers": side_ledgers,
        "outer_boundary_tangent_Linf": outer_tangent_linf,
    }


def build_payload() -> Mapping[str, Any]:
    bundle, member, free, tangent = load_primitives()
    contract = bundle["pointwise_decoder_contract_by_N"]["1"]
    parameters = bundle["action_contract"]["coefficient_parameters"]
    refinement = [
        _evaluate_radial_order(free, tangent, contract, parameters, order)
        for order in RADIAL_REFINEMENT_ORDERS
    ]
    primary = next(
        row for row in refinement if row["radial_Gauss_order"] == RADIAL_GAUSS_ORDER
    )
    component_stokes = [
        float(row["maximum_absolute_component_Stokes_residual"]) for row in refinement
    ]
    total_stokes = [float(row["total_absolute_Stokes_residual"]) for row in refinement]
    monotone_component_contraction = all(
        right < left for left, right in zip(component_stokes, component_stokes[1:])
    )
    monotone_total_contraction = all(
        right < left for left, right in zip(total_stokes, total_stokes[1:])
    )
    n1_stokes_pass = (
        monotone_component_contraction
        and monotone_total_contraction
        and component_stokes[-1] <= STOKES_FINAL_COMPONENT_ABS_TOLERANCE
        and total_stokes[-1] <= STOKES_FINAL_TOTAL_ABS_TOLERANCE
    )

    boundary = _constant_boundary_decode(free, contract)
    rotations = {
        side: {
            "distance_from_identity_Frobenius": float(
                np.linalg.norm(boundary["sides"][side]["R_source_to_Q"] - np.eye(3))
            ),
            "determinant": float(np.linalg.det(boundary["sides"][side]["R_source_to_Q"])),
        }
        for side in SIDES
    }
    face_audit = {
        "tangential_T4_eight_faces": {
            f"x{axis}_{orientation}": 0.0
            for axis in range(4)
            for orientation in ("minus", "plus")
        },
        "reason": "N=1 is the exact constant Fourier mode, so each oriented periodic face flux is identically zero",
        "radial_outer_boundary_tangent_Linf": max(
            row["outer_boundary_tangent_Linf"] for row in refinement
        ),
        "radial_interface_fluxes_Q20": {
            side: {
                sector: refinement[-1]["side_ledgers"][side]["ledger"][sector][
                    "interface_Green"
                ]
                for sector in ("Omega_kinetic", "P_kinetic", "BF")
            }
            for side in SIDES
        },
    }
    return {
        "schema": SCHEMA,
        "classification": "theory_only;route_C;independent_analytic_Euler_Green;N1_constant_tangential_mode;C2_radial;raw;fail_closed",
        "decision": {
            "route_C_N1_independent_Euler_Green_raw_pass": n1_stokes_pass,
            "route_C_N2_N3_independent_Euler_Green_pass": False,
            "Euler_Green_independent_route_pass": False,
            "clean_room_full_mutant_campaign_pass": False,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "mathematical_contract": {
            "EH_GHY": "delta(S_EH+S_GHY)=-M5^3/2 int sqrt(-g) G^MN delta g_MN-M5^3/2 int_Sigma sqrt(-gamma) pi^mn delta gamma_mn",
            "Omega": "E_Omega=G box_g Omega with Green=-G int_Sigma sqrt(-gamma) n.dOmega deltaOmega",
            "matter": "E_phi=Z(D_M P^M-c_M P^M); E_Omega=(3Z/(2Omega)) div(phi.P); E_A=-Z phi cross P^M",
            "BF": "E_B=F and E_A is the oriented covariant divergence of B; the radial integration-by-parts term is retained explicitly",
            "interface_N1": "constant tangential mode has Kcal=Rcal=a=0; wall and Robin are algebraic weak Euler terms and Sigma=T4 has no corners",
        },
        "fixed_before_run": {
            "N": 1,
            "K": 1,
            "radial_Gauss_order": RADIAL_GAUSS_ORDER,
            "radial_refinement_orders": list(RADIAL_REFINEMENT_ORDERS),
            "tangential_rule": "Q1 exact constant Fourier mode",
            "decoder_JVP_step": DECODER_JVP_STEP,
            "local_EH_jet_step": LOCAL_EH_JET_STEP,
            "Stokes_final_component_abs_tolerance": STOKES_FINAL_COMPONENT_ABS_TOLERANCE,
            "Stokes_final_total_abs_tolerance": STOKES_FINAL_TOTAL_ABS_TOLERANCE,
        },
        "scientific": {
            "member_id": member["member_id"],
            "authoritative_free_central_sha256": member[
                "authoritative_free_central_f64le"
            ]["sha256"],
            "authoritative_free_tangent_sha256": next(
                curve
                for curve in member["curves"]
                if curve["name"] == "joint_all_primitive_classes_control_candidate"
            )["authoritative_free_tangent_f64le"]["sha256"],
            "predicted_Euler_Green_by_component": primary[
                "predicted_Euler_Green_by_component"
            ],
            "direct_local_jet_JVP_by_component": primary[
                "direct_local_jet_JVP_by_component"
            ],
            "Stokes_residual_direct_minus_Euler_Green": primary[
                "Stokes_residual_direct_minus_Euler_Green"
            ],
            "radial_refinement_records": refinement,
            "Stokes_convergence": {
                "maximum_component_residual_series": component_stokes,
                "total_residual_series": total_stokes,
                "monotone_component_contraction": monotone_component_contraction,
                "monotone_total_contraction": monotone_total_contraction,
                "pass": n1_stokes_pass,
            },
            "side_ledgers": primary["side_ledgers"],
            "nontrivial_R_controls": rotations,
            "outer_boundary_tangent_Linf": max(
                row["outer_boundary_tangent_Linf"] for row in refinement
            ),
            "corner_residual": 0.0,
            "face_audit": face_audit,
        },
        "independence_audit": {
            "project_action_or_Euler_modules_imported": [],
            "AD_or_FD_expected_values_read": False,
            "comparison_tolerances_read": False,
            "primitive_bundle_only_scientific_input": True,
            "action_formula_reconstructed_from_literal_hash": LITERAL_V5_2_ACTION_SHA256,
        },
        "source_pins": {
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
        },
        "open_obligations": {
            "multi_N": "extend the independent Euler-Green evaluator to the genuinely x-dependent N=2 and N=3 members",
            "comparison": "compare this raw route to the separately frozen v5.6.5.8 values in a distinct gate",
            "mutants": "execute the complete clean-room mutant campaign after multi-N Euler-Green closure",
            "continuum": "prove the uniform N-to-infinity bridge separately",
        },
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
        "evidence_boundary": "This is an independent analytic Euler-Green reconstruction for the finite N=1 constant tangential member only. It reads no AD/FD result and cannot promote the multi-N Euler-Green gate, C1/N1, B4, or B5.",
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
