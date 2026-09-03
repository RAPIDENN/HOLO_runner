#!/usr/bin/env python3
"""Full five-dimensional SO(3) gauge-Ward gate for the pinned v5.2 action.

This additive v5.5.3 receipt does not consume the preliminary two-dimensional
v5.5.1 result.  It evaluates two non-Abelian five-dimensional bulks, the full
v5.2 interface action on a four-dimensional common boundary, and the boundary
Green identity.  Diffeomorphism/khronon and BV--BFV completion remain separate
fail-closed questions.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.json"
)
TEST = HERE / "test_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.py"
V5_2 = HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
V5_5_2 = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.json"
)

SCHEMA = "holo.one-omega-topological-so3-full-action-gauge-noether-v5-5-3-gate.v1"
EXPECTED_V5_2_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
EXPECTED_V5_2_SHA256 = (
    "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b"
)
EXPECTED_V5_5_2_SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-gate.v1"
EXPECTED_V5_5_2_SHA256 = (
    "4e068475ae316684cebd0f68e10d183fff7c0d90c46b155f2dfc8be4b3b0d6e8"
)

DIM5 = 5
DIM4 = 4
GRID5 = 7
GRID4 = 7
SHAPE5 = (GRID5,) * DIM5
SHAPE4 = (GRID4,) * DIM4
VOL5 = (2.0 * math.pi) ** DIM5
VOL4 = (2.0 * math.pi) ** DIM4
ETA5 = np.asarray([-1.0, 1.0, 1.0, 1.0, 1.0])
ETA4 = np.asarray([-1.0, 1.0, 1.0, 1.0])
TOP5 = tuple(range(DIM5))
TOP4 = tuple(range(DIM4))

EXPECTED_ACTIONS = {
    "BF": "S_BF=sum_eps int_Meps <B_eps wedge F[A_eps]>, <X,Y>=-tr_3(XY)/2",
    "GHY": "S_GHY=M5^3*sum_eps int_Sigma sqrt(-gamma)*Theta_eps for outward normals",
    "Robin_intrinsic": "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)",
    "bulk_gauged": "S_bulk_gauged=sum_eps int_Meps sqrt(-g_eps)*[M5^3*R_eps/2-G*(nabla Omega_eps)^2/2-U(Omega_eps)-Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2-Z5*M^2*Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)]",
    "bulk_potential": "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
    "foliation_lower": "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-B4_bar*Rcal^2/(16*k_infinity^2)]",
    "full_V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
    "gauged_conformal_derivative": "P_eps_M=D_(A_eps,M)phi_eps+3*phi_eps*partial_M log(Omega_eps)/2",
    "removed_terms": "S_X=0 and every bulk screen-clock term=0",
    "superpotential": "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]",
    "total": "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF",
    "wall_background": "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2]",
}

EXPECTED_COEFFICIENTS = {
    "B4_bar": 0.8,
    "M4_bulk_squared_selected_one_Omega_wall_value": 1.107013790800849,
    "M5_cubed": 1.0,
    "Robin_kappa_hat": 1.0,
    "Robin_kappa_in_Mb_units": 0.5,
    "Robin_y": 1.7320508075688772,
    "Robin_y_squared": 3.0,
    "brane_Mb_squared": 2.0,
    "brane_beta": 2.0,
    "compensator_metric_G": 1.2,
    "eta": 3.107013790800849,
    "k_BF_trace_equivalent": -0.5,
    "k_infinity": 1.0,
    "kappa_BF_inner_product": 1.0,
    "lambda_K": -0.5535068954004245,
    "material_Z5_per_side": 1.0,
    "material_mass_M": 1.0,
    "xi": 1.0,
}

FAIL_CLOSED_KEYS = (
    "diffeomorphism_khronon_full_Ward_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "unrestricted_large_gauge_sector_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "N4_JUNCTION_BENDING_pass",
    "P4_full_same_action_pass",
    "v5_6_promotion_authorized",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
)


class FullActionWardV553Error(ValueError):
    """A source pin or an executable Ward check failed closed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise FullActionWardV553Error(f"cannot hash {path}: {exc}") from exc


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _load_sources() -> tuple[dict[str, Any], dict[str, Any]]:
    if _sha256(V5_2) != EXPECTED_V5_2_SHA256:
        raise FullActionWardV553Error("v5.2 artifact byte hash mismatch")
    if _sha256(V5_5_2) != EXPECTED_V5_5_2_SHA256:
        raise FullActionWardV553Error("v5.5.2 artifact byte hash mismatch")
    try:
        v52 = json.loads(V5_2.read_text(encoding="utf-8"))
        v552 = json.loads(V5_5_2.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FullActionWardV553Error("cannot load pinned sources") from exc
    if v52.get("schema") != EXPECTED_V5_2_SCHEMA:
        raise FullActionWardV553Error("v5.2 schema mismatch")
    if v552.get("schema") != EXPECTED_V5_5_2_SCHEMA:
        raise FullActionWardV553Error("v5.5.2 schema mismatch")
    charter = v52.get("exact_classical_charter", {})
    if charter.get("exact_action") != EXPECTED_ACTIONS:
        raise FullActionWardV553Error("v5.2 literal action ledger mismatch")
    coefficients = charter.get("coefficient_policy", {}).get("parameters")
    if coefficients != EXPECTED_COEFFICIENTS:
        raise FullActionWardV553Error("v5.2 coefficient ledger mismatch")
    decision52 = v52.get("decision", {})
    if (
        decision52.get("exact_single_classical_action_candidate_charter_pass") is not True
        or decision52.get("C1_ACTION_pass") is not False
        or decision52.get("N1_ACTION_pass") is not False
    ):
        raise FullActionWardV553Error("v5.2 decision boundary mismatch")
    slots = v552.get("formula_ledger", {}).get("literal_variational_coordinates", {})
    adm = v552.get("certificates", {}).get("ADM_Jacobian", {})
    israel = v552.get("certificates", {}).get("Israel_Brown_York_reconstruction", {})
    matter = v552.get("certificates", {}).get("matter_shift_and_Robin", {})
    decision552 = v552.get("decision", {})
    if (
        slots.get("omega") != "omega=δOmegaSigma"
        or slots.get("v") != "v_i=δpsi_i"
        or slots.get("b_shift") != "b_shift^i=δβ^i"
        or adm.get("Jacobian_rank") != 10
        or decision552.get("induced_ADM_bidirectional_Jacobian_pass") is not True
        or decision552.get("single_Israel_Brown_York_tensor_reconstruction_pass") is not True
        or decision552.get("bulk_matter_shift_momentum_witness_pass") is not True
        or float(israel.get("projection_reconstruction_error", math.inf)) > 1.0e-10
        or float(matter.get("T_ui_norm", 0.0)) <= 1.0e-3
        or decision552.get("C1_ACTION_pass") is not False
        or decision552.get("N1_ACTION_pass") is not False
    ):
        raise FullActionWardV553Error("v5.5.2 ADM control contract mismatch")
    return v52, v552


V5_2_PAYLOAD, V5_5_2_PAYLOAD = _load_sources()
M5 = EXPECTED_COEFFICIENTS["M5_cubed"]
G_OMEGA = EXPECTED_COEFFICIENTS["compensator_metric_G"]
Z5 = EXPECTED_COEFFICIENTS["material_Z5_per_side"]
MATERIAL_M = EXPECTED_COEFFICIENTS["material_mass_M"]
K_INFINITY = EXPECTED_COEFFICIENTS["k_infinity"]
MB2 = EXPECTED_COEFFICIENTS["brane_Mb_squared"]
LAMBDA_K = EXPECTED_COEFFICIENTS["lambda_K"]
XI = EXPECTED_COEFFICIENTS["xi"]
ETA = EXPECTED_COEFFICIENTS["eta"]
B4_BAR = EXPECTED_COEFFICIENTS["B4_bar"]
ROBIN_KAPPA = EXPECTED_COEFFICIENTS["Robin_kappa_hat"]
ROBIN_Y = EXPECTED_COEFFICIENTS["Robin_y"]
BRANE_BETA = EXPECTED_COEFFICIENTS["brane_beta"]


def _coords(dim: int, size: int) -> tuple[np.ndarray, ...]:
    line = np.linspace(0.0, 2.0 * math.pi, size, endpoint=False)
    return tuple(np.meshgrid(*([line] * dim), indexing="ij"))


def _d(value: np.ndarray, axis: int) -> np.ndarray:
    modes = np.fft.fftfreq(value.shape[axis], d=1.0 / value.shape[axis])
    shape = [1] * value.ndim
    shape[axis] = value.shape[axis]
    transformed = np.fft.fft(value, axis=axis)
    return np.fft.ifft(1j * modes.reshape(shape) * transformed, axis=axis).real


def _integral5(value: np.ndarray) -> float:
    return VOL5 * float(np.mean(value))


def _integral4(value: np.ndarray) -> float:
    return VOL4 * float(np.mean(value))


def _l2(value: np.ndarray) -> float:
    array = np.asarray(value)
    if array.ndim and array.shape[-1] == 3:
        return float(np.sqrt(np.mean(np.sum(array**2, axis=-1))))
    return float(np.sqrt(np.mean(array**2)))


def _linf(value: np.ndarray) -> float:
    return float(np.max(np.abs(value)))


def _wave(coords: tuple[np.ndarray, ...], phase: float, scale: float) -> np.ndarray:
    value = np.zeros_like(coords[0])
    for axis, coordinate in enumerate(coords):
        value += scale * (0.55 + 0.08 * axis) * np.sin(
            coordinate + phase * (axis + 1)
        )
    value += 0.31 * scale * np.cos(coords[0] + coords[-1] + 0.7 * phase)
    value += 0.23 * scale * np.sin(coords[1] - coords[-2] + 0.4 * phase)
    return value


def _permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _tuples(degree: int, dim: int = DIM5) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.combinations(range(dim), degree))


def _covariant_component(
    value: np.ndarray, connection: np.ndarray, axis: int
) -> np.ndarray:
    return _d(value, axis) + np.cross(connection[..., axis, :], value)


def _curvature(connection: np.ndarray) -> dict[tuple[int, ...], np.ndarray]:
    return {
        (m, n): _d(connection[..., n, :], m)
        - _d(connection[..., m, :], n)
        + np.cross(connection[..., m, :], connection[..., n, :])
        for m, n in _tuples(2)
    }


def _covariant_exterior(
    form: Mapping[tuple[int, ...], np.ndarray],
    degree: int,
    connection: np.ndarray,
    dim: int = DIM5,
) -> dict[tuple[int, ...], np.ndarray]:
    output: dict[tuple[int, ...], np.ndarray] = {}
    for target in _tuples(degree + 1, dim):
        value = np.zeros_like(next(iter(form.values())))
        for position, axis in enumerate(target):
            source = target[:position] + target[position + 1 :]
            value += (-1) ** position * _covariant_component(
                form[source], connection, axis
            )
        output[target] = value
    return output


def _ordinary_exterior_scalar_form(
    form: Mapping[tuple[int, ...], np.ndarray], degree: int, dim: int
) -> dict[tuple[int, ...], np.ndarray]:
    output: dict[tuple[int, ...], np.ndarray] = {}
    for target in _tuples(degree + 1, dim):
        value = np.zeros_like(next(iter(form.values())))
        for position, axis in enumerate(target):
            source = target[:position] + target[position + 1 :]
            value += (-1) ** position * _d(form[source], axis)
        output[target] = value
    return output


def _wedge_dot_top(
    left: Mapping[tuple[int, ...], np.ndarray],
    right: Mapping[tuple[int, ...], np.ndarray],
    dim: int,
) -> np.ndarray:
    result = np.zeros_like(next(iter(left.values()))[..., 0])
    full = tuple(range(dim))
    for left_indices, left_value in left.items():
        right_indices = tuple(axis for axis in full if axis not in left_indices)
        if right_indices not in right:
            continue
        sign = _permutation_sign(left_indices + right_indices)
        result += sign * np.sum(left_value * right[right_indices], axis=-1)
    return result


def _wedge_cross_top(
    left: Mapping[tuple[int, ...], np.ndarray],
    right: Mapping[tuple[int, ...], np.ndarray],
    dim: int,
) -> np.ndarray:
    result = np.zeros_like(next(iter(left.values())))
    full = tuple(range(dim))
    for left_indices, left_value in left.items():
        right_indices = tuple(axis for axis in full if axis not in left_indices)
        if right_indices not in right:
            continue
        sign = _permutation_sign(left_indices + right_indices)
        result += sign * np.cross(left_value, right[right_indices])
    return result


def _one_form(array: np.ndarray) -> dict[tuple[int, ...], np.ndarray]:
    return {(axis,): array[..., axis, :] for axis in range(array.shape[-2])}


def _form_add(
    left: Mapping[tuple[int, ...], np.ndarray],
    right: Mapping[tuple[int, ...], np.ndarray],
) -> dict[tuple[int, ...], np.ndarray]:
    return {key: left[key] + right[key] for key in left}


def _hat(vector: np.ndarray) -> np.ndarray:
    output = np.zeros(vector.shape[:-1] + (3, 3), dtype=float)
    x, y, z = (vector[..., index] for index in range(3))
    output[..., 0, 1] = -z
    output[..., 0, 2] = y
    output[..., 1, 0] = z
    output[..., 1, 2] = -x
    output[..., 2, 0] = -y
    output[..., 2, 1] = x
    return output


def _v4(value: np.ndarray) -> np.ndarray:
    return value**4 / (2.0 * np.sqrt(1.0 + value**4))


def _v4_prime(value: np.ndarray) -> np.ndarray:
    return value**3 * (2.0 + value**4) / (1.0 + value**4) ** 1.5


def _superpotential(omega: np.ndarray) -> np.ndarray:
    return 3.0 * M5 * K_INFINITY * np.exp(-G_OMEGA * omega**2 / (6.0 * M5))


def _bulk_potential(omega: np.ndarray) -> np.ndarray:
    w = _superpotential(omega)
    w_prime = -G_OMEGA * omega * w / (3.0 * M5)
    return w_prime**2 / (2.0 * G_OMEGA) - 2.0 * w**2 / (3.0 * M5)


def _bulk_configuration(side: int) -> dict[str, Any]:
    if side not in (1, -1):
        raise ValueError("side must be +1 or -1")
    coordinates = _coords(DIM5, GRID5)
    tangential = coordinates[:DIM4]
    normal = coordinates[4]
    sigma_boundary = _wave(tangential, 0.31, 0.018)
    omega_boundary = 1.24 + _wave(tangential, 0.63, 0.025)
    vanishing_normal = np.sin(normal) * (
        0.014 * side + _wave(tangential, 0.41 + 0.17 * side, 0.003)
    ) + 0.004 * (1.0 - np.cos(normal))
    sigma = sigma_boundary + vanishing_normal
    omega = omega_boundary + np.sin(normal) * (
        0.035 * side + _wave(tangential, 0.72 + 0.11 * side, 0.006)
    ) + 0.012 * (1.0 - np.cos(normal))

    connection = np.empty(SHAPE5 + (DIM5, 3), dtype=float)
    for spacetime in range(DIM5):
        for internal in range(3):
            boundary = _wave(
                tangential,
                0.19 + 0.23 * spacetime + 0.37 * internal,
                0.055 + 0.004 * spacetime,
            )
            normal_profile = np.sin(normal) * _wave(
                tangential,
                0.47 + 0.13 * spacetime + 0.29 * internal,
                0.012,
            )
            connection[..., spacetime, internal] = (
                boundary
                + side * normal_profile
                + 0.009 * (internal + 1) * (1.0 - np.cos(normal))
            )

    phi = np.empty(SHAPE5 + (3,), dtype=float)
    phi_bases = (0.36, -0.24, 0.29)
    for internal in range(3):
        phi[..., internal] = (
            phi_bases[internal]
            + _wave(tangential, 0.28 + 0.43 * internal, 0.045)
            + side
            * np.sin(normal)
            * _wave(tangential, 0.61 + 0.31 * internal, 0.014)
            + 0.008 * (internal + 1) * (1.0 - np.cos(normal))
        )

    b_form: dict[tuple[int, ...], np.ndarray] = {}
    for component, indices in enumerate(_tuples(3)):
        value = np.empty(SHAPE5 + (3,), dtype=float)
        for internal in range(3):
            boundary = _wave(
                tangential,
                0.16 + 0.21 * component + 0.33 * internal,
                0.043,
            ) + 0.025 * (internal - 1)
            normal_profile = np.sin(normal) * _wave(
                tangential,
                0.37 + 0.17 * component + 0.26 * internal,
                0.011,
            )
            value[..., internal] = (
                boundary
                + side * normal_profile
                + 0.006 * (component + 1) * (1.0 - np.cos(normal))
            )
        b_form[indices] = value
    configuration = {
        "side": side,
        "coordinates": coordinates,
        "sigma": sigma,
        "Omega": omega,
        "A": connection,
        "B": b_form,
        "phi": phi,
    }
    configuration["_geometry"] = _conformal_bulk_geometry(configuration)
    return configuration


def _conformal_bulk_geometry(configuration: Mapping[str, Any]) -> dict[str, Any]:
    sigma = np.asarray(configuration["sigma"])
    omega = np.asarray(configuration["Omega"])
    exp_minus_two = np.exp(-2.0 * sigma)
    sqrt_minus_g = np.exp(5.0 * sigma)
    sigma_gradient = np.stack([_d(sigma, axis) for axis in range(DIM5)], axis=-1)
    sigma_box = sum(
        ETA5[axis] * _d(_d(sigma, axis), axis) for axis in range(DIM5)
    )
    sigma_gradient_squared = np.sum(
        exp_minus_two[..., None] * ETA5 * sigma_gradient**2, axis=-1
    )
    scalar_curvature = exp_minus_two * (
        -8.0 * sigma_box
        - 12.0 * np.sum(ETA5 * sigma_gradient**2, axis=-1)
    )
    inverse_diagonal = exp_minus_two[..., None] * ETA5
    omega_gradient = np.stack([_d(omega, axis) for axis in range(DIM5)], axis=-1)
    omega_gradient_squared = np.sum(
        inverse_diagonal * omega_gradient**2, axis=-1
    )
    return {
        "sqrt_minus_g": sqrt_minus_g,
        "inverse_diagonal": inverse_diagonal,
        "scalar_curvature": scalar_curvature,
        "sigma_gradient_squared": sigma_gradient_squared,
        "Omega_gradient": omega_gradient,
        "Omega_gradient_squared": omega_gradient_squared,
    }


def _radial_potential_euler(omega: np.ndarray, phi: np.ndarray) -> np.ndarray:
    rho = np.linalg.norm(phi, axis=-1)
    s = omega**1.5 * rho
    output = np.zeros_like(phi)
    nonzero = rho > 0.0
    coefficient = np.zeros_like(rho)
    coefficient[nonzero] = (
        -Z5
        * MATERIAL_M**2
        * omega[nonzero] ** -3.5
        * _v4_prime(s[nonzero])
        / rho[nonzero]
    )
    output[nonzero] = coefficient[nonzero, None] * phi[nonzero]
    return output


def _vector_current_to_four_form(
    current_contravariant: np.ndarray, sqrt_minus_g: np.ndarray
) -> dict[tuple[int, ...], np.ndarray]:
    output: dict[tuple[int, ...], np.ndarray] = {}
    full = tuple(range(DIM5))
    for axis in range(DIM5):
        complement = tuple(value for value in full if value != axis)
        sign = _permutation_sign((axis,) + complement)
        output[complement] = (
            sign * sqrt_minus_g[..., None] * current_contravariant[..., axis, :]
        )
    return output


def _bulk_runtime(configuration: Mapping[str, Any]) -> dict[str, Any]:
    connection = np.asarray(configuration["A"])
    b_form = configuration["B"]
    phi = np.asarray(configuration["phi"])
    omega = np.asarray(configuration["Omega"])
    geometry = configuration.get("_geometry")
    if geometry is None:
        geometry = _conformal_bulk_geometry(configuration)
    curvature = _curvature(connection)
    c_covariant = np.stack(
        [1.5 * _d(np.log(omega), axis) for axis in range(DIM5)], axis=-1
    )
    p_covariant = np.empty(SHAPE5 + (DIM5, 3), dtype=float)
    for axis in range(DIM5):
        p_covariant[..., axis, :] = (
            _d(phi, axis)
            + np.cross(connection[..., axis, :], phi)
            + c_covariant[..., axis, None] * phi
        )
    p_contravariant = (
        geometry["inverse_diagonal"][..., :, None] * p_covariant
    )
    current_contravariant = Z5 * np.cross(p_contravariant, phi[..., None, :])
    current_four_form = _vector_current_to_four_form(
        current_contravariant, geometry["sqrt_minus_g"]
    )
    db = _covariant_exterior(b_form, 3, connection)
    e_a = _form_add(db, current_four_form)

    weighted_p = geometry["sqrt_minus_g"][..., None, None] * p_contravariant
    divergence_density = np.zeros_like(phi)
    for axis in range(DIM5):
        divergence_density += _d(weighted_p[..., axis, :], axis)
        divergence_density += np.cross(
            connection[..., axis, :], weighted_p[..., axis, :]
        )
    divergence = divergence_density / geometry["sqrt_minus_g"][..., None]
    c_dot_p = np.sum(
        c_covariant[..., :, None] * p_contravariant, axis=-2
    )
    e_phi_kinetic = Z5 * (divergence - c_dot_p)
    e_phi_potential = _radial_potential_euler(omega, phi)
    e_phi = e_phi_kinetic + e_phi_potential
    return {
        "geometry": geometry,
        "F": curvature,
        "c": c_covariant,
        "P_covariant": p_covariant,
        "P_contravariant": p_contravariant,
        "J_vector": current_contravariant,
        "J_four_form": current_four_form,
        "DB": db,
        "E_A": e_a,
        "E_B": curvature,
        "E_phi_kinetic": e_phi_kinetic,
        "E_phi_potential": e_phi_potential,
        "E_phi": e_phi,
    }


def _bulk_action_sectors(
    configuration: Mapping[str, Any], *, anisotropic_potential: bool = False
) -> dict[str, float]:
    runtime = _bulk_runtime(configuration)
    geometry = runtime["geometry"]
    omega = np.asarray(configuration["Omega"])
    phi = np.asarray(configuration["phi"])
    rho = np.linalg.norm(phi, axis=-1)
    s = omega**1.5 * rho
    kinetic_contraction = np.sum(
        runtime["P_covariant"] * runtime["P_contravariant"], axis=(-2, -1)
    )
    potential_shape = _v4(s)
    if anisotropic_potential:
        potential_shape = potential_shape + 0.23 * phi[..., 0] * phi[..., 1]
    sectors = {
        "Einstein_Hilbert": _integral5(
            geometry["sqrt_minus_g"] * M5 * geometry["scalar_curvature"] / 2.0
        ),
        "Omega_kinetic": _integral5(
            -geometry["sqrt_minus_g"]
            * G_OMEGA
            * geometry["Omega_gradient_squared"]
            / 2.0
        ),
        "Omega_superpotential": _integral5(
            -geometry["sqrt_minus_g"] * _bulk_potential(omega)
        ),
        "matter_kinetic": _integral5(
            -geometry["sqrt_minus_g"] * Z5 * kinetic_contraction / 2.0
        ),
        "matter_full_V4": _integral5(
            -geometry["sqrt_minus_g"]
            * Z5
            * MATERIAL_M**2
            * omega**-5.0
            * potential_shape
        ),
        "BF": _integral5(_wedge_dot_top(configuration["B"], runtime["F"], DIM5)),
    }
    sectors["total"] = sum(sectors.values())
    return sectors


def _bulk_action(
    configuration: Mapping[str, Any], *, anisotropic_potential: bool = False
) -> float:
    return _bulk_action_sectors(
        configuration, anisotropic_potential=anisotropic_potential
    )["total"]


def _variation(seed: float) -> dict[str, Any]:
    coordinates = _coords(DIM5, GRID5)
    delta_a = np.empty(SHAPE5 + (DIM5, 3), dtype=float)
    for spacetime in range(DIM5):
        for internal in range(3):
            delta_a[..., spacetime, internal] = _wave(
                coordinates,
                seed + 0.19 * spacetime + 0.27 * internal,
                0.018,
            )
    delta_b: dict[tuple[int, ...], np.ndarray] = {}
    for component, indices in enumerate(_tuples(3)):
        value = np.empty(SHAPE5 + (3,), dtype=float)
        for internal in range(3):
            value[..., internal] = _wave(
                coordinates,
                seed + 0.13 * component + 0.31 * internal,
                0.016,
            )
        delta_b[indices] = value
    delta_phi = np.stack(
        [
            _wave(coordinates, seed + 0.41 * internal, 0.017)
            for internal in range(3)
        ],
        axis=-1,
    )
    return {"A": delta_a, "B": delta_b, "phi": delta_phi}


def _scaled_configuration(
    configuration: Mapping[str, Any],
    variation: Mapping[str, Any],
    scale: float,
    active: tuple[str, ...],
) -> dict[str, Any]:
    output = dict(configuration)
    output["A"] = np.asarray(configuration["A"]) + (
        scale * np.asarray(variation["A"]) if "A" in active else 0.0
    )
    output["phi"] = np.asarray(configuration["phi"]) + (
        scale * np.asarray(variation["phi"]) if "phi" in active else 0.0
    )
    output["B"] = {
        key: value + (scale * variation["B"][key] if "B" in active else 0.0)
        for key, value in configuration["B"].items()
    }
    return output


def _central_action_derivative(
    configuration: Mapping[str, Any],
    variation: Mapping[str, Any],
    active: tuple[str, ...],
    *,
    anisotropic_potential: bool = False,
    step: float = 2.0e-5,
) -> float:
    # A symmetric two-point route is deliberately used here: it is independent
    # of the analytic Euler implementation while keeping the 6^5 audit light.
    plus = _bulk_action(
        _scaled_configuration(configuration, variation, step, active),
        anisotropic_potential=anisotropic_potential,
    )
    minus = _bulk_action(
        _scaled_configuration(configuration, variation, -step, active),
        anisotropic_potential=anisotropic_potential,
    )
    return (plus - minus) / (2.0 * step)


def _euler_pairing(
    configuration: Mapping[str, Any],
    runtime: Mapping[str, Any],
    variation: Mapping[str, Any],
    active: tuple[str, ...],
    *,
    e_a_override: Mapping[tuple[int, ...], np.ndarray] | None = None,
    e_b_override: Mapping[tuple[int, ...], np.ndarray] | None = None,
    e_phi_override: np.ndarray | None = None,
) -> float:
    density = np.zeros(SHAPE5, dtype=float)
    if "A" in active:
        density += _wedge_dot_top(
            _one_form(variation["A"]),
            runtime["E_A"] if e_a_override is None else e_a_override,
            DIM5,
        )
    if "B" in active:
        density += _wedge_dot_top(
            variation["B"],
            runtime["E_B"] if e_b_override is None else e_b_override,
            DIM5,
        )
    if "phi" in active:
        e_phi = runtime["E_phi"] if e_phi_override is None else e_phi_override
        density += runtime["geometry"]["sqrt_minus_g"] * np.sum(
            e_phi * variation["phi"], axis=-1
        )
    return _integral5(density)


def _interface_primitives(
    plus: Mapping[str, Any], minus: Mapping[str, Any]
) -> dict[str, Any]:
    coordinates = _coords(DIM4, GRID4)
    theta = _wave(coordinates, 0.52, 0.018)
    phi_trace = np.asarray(plus["phi"])[..., 0, :]
    if np.max(np.abs(phi_trace - np.asarray(minus["phi"])[..., 0, :])) > 1.0e-12:
        raise FullActionWardV553Error("bulk phi traces are not common")
    sigma = np.asarray(plus["sigma"])[..., 0]
    omega = np.asarray(plus["Omega"])[..., 0]
    if (
        np.max(np.abs(sigma - np.asarray(minus["sigma"])[..., 0])) > 1.0e-12
        or np.max(np.abs(omega - np.asarray(minus["Omega"])[..., 0])) > 1.0e-12
    ):
        raise FullActionWardV553Error("bulk metric/Omega traces are not common")
    angle_x = _wave(coordinates, 0.23, 0.050)
    angle_y = _wave(coordinates, 0.71, 0.040)
    angle_z = _wave(coordinates, 1.09, 0.045)
    cx, sx = np.cos(angle_x), np.sin(angle_x)
    cy, sy = np.cos(angle_y), np.sin(angle_y)
    cz, sz = np.cos(angle_z), np.sin(angle_z)
    rx = np.zeros(SHAPE4 + (3, 3))
    ry = np.zeros_like(rx)
    rz = np.zeros_like(rx)
    rx[..., 0, 0] = 1.0
    rx[..., 1, 1] = cx
    rx[..., 1, 2] = -sx
    rx[..., 2, 1] = sx
    rx[..., 2, 2] = cx
    ry[..., 0, 0] = cy
    ry[..., 0, 2] = sy
    ry[..., 1, 1] = 1.0
    ry[..., 2, 0] = -sy
    ry[..., 2, 2] = cy
    rz[..., 0, 0] = cz
    rz[..., 0, 1] = -sz
    rz[..., 1, 0] = sz
    rz[..., 1, 1] = cz
    rz[..., 2, 2] = 1.0
    groupoid_r = np.einsum("...ij,...jk,...kl->...il", rz, ry, rx)
    return {
        "coordinates": coordinates,
        "sigma": sigma,
        "sigma_normal_plus": _d(np.asarray(plus["sigma"]), 4)[..., 0],
        "sigma_normal_minus": _d(np.asarray(minus["sigma"]), 4)[..., 0],
        "Omega": omega,
        "theta": theta,
        "phi_source": phi_trace,
        "R_groupoid": groupoid_r,
        "A_source": np.asarray(plus["A"])[..., 0, :DIM4, :],
        "B_source_plus": {
            key: value[..., 0, :]
            for key, value in plus["B"].items()
            if all(axis < DIM4 for axis in key)
        },
        "B_source_minus": {
            key: value[..., 0, :]
            for key, value in minus["B"].items()
            if all(axis < DIM4 for axis in key)
        },
    }


def _interface_geometry(primitives: Mapping[str, Any]) -> dict[str, Any]:
    sigma = np.asarray(primitives["sigma"])
    theta = np.asarray(primitives["theta"])
    exp_two = np.exp(2.0 * sigma)
    exp_minus_two = np.exp(-2.0 * sigma)
    sqrt_minus_gamma = np.exp(4.0 * sigma)
    gamma_cov = np.zeros(SHAPE4 + (DIM4, DIM4))
    gamma_inverse = np.zeros_like(gamma_cov)
    for axis in range(DIM4):
        gamma_cov[..., axis, axis] = exp_two * ETA4[axis]
        gamma_inverse[..., axis, axis] = exp_minus_two * ETA4[axis]

    sigma_gradient = np.stack([_d(sigma, axis) for axis in range(DIM4)], axis=-1)
    christoffel = np.zeros(SHAPE4 + (DIM4, DIM4, DIM4))
    for rho in range(DIM4):
        for mu in range(DIM4):
            for nu in range(DIM4):
                value = np.zeros(SHAPE4)
                if rho == mu:
                    value += sigma_gradient[..., nu]
                if rho == nu:
                    value += sigma_gradient[..., mu]
                if mu == nu:
                    value -= ETA4[mu] * ETA4[rho] * sigma_gradient[..., rho]
                christoffel[..., rho, mu, nu] = value

    t_cov = np.stack([_d(theta, axis) for axis in range(DIM4)], axis=-1)
    t_cov[..., 0] += 1.0
    t_norm = np.einsum("...mn,...m,...n->...", gamma_inverse, t_cov, t_cov)
    if np.max(t_norm) >= -0.2:
        raise FullActionWardV553Error("interface khronon gradient is not timelike")
    lapse_t = (-t_norm) ** -0.5
    u_cov = -lapse_t[..., None] * t_cov
    u_contra = np.einsum("...mn,...n->...m", gamma_inverse, u_cov)
    h_cov = gamma_cov + np.einsum("...m,...n->...mn", u_cov, u_cov)
    h_contra = gamma_inverse + np.einsum("...m,...n->...mn", u_contra, u_contra)
    projector = np.eye(DIM4) + np.einsum("...m,...a->...ma", u_cov, u_contra)

    nabla_u = np.empty(SHAPE4 + (DIM4, DIM4))
    for alpha in range(DIM4):
        for beta in range(DIM4):
            nabla_u[..., alpha, beta] = _d(u_cov[..., beta], alpha) - np.sum(
                christoffel[..., :, alpha, beta] * u_cov, axis=-1
            )
    k_tensor = np.einsum(
        "...ma,...nb,...ab->...mn", projector, projector, nabla_u
    )
    k_trace = np.einsum("...mn,...mn->...", h_contra, k_tensor)
    k_squared = np.einsum(
        "...ma,...nb,...mn,...ab->...", h_contra, h_contra, k_tensor, k_tensor
    )
    acceleration_cov = np.einsum("...a,...am->...m", u_contra, nabla_u)
    acceleration_contra = np.einsum(
        "...mn,...n->...m", gamma_inverse, acceleration_cov
    )
    acceleration_squared = np.einsum(
        "...mn,...m,...n->...", gamma_inverse, acceleration_cov, acceleration_cov
    )

    sigma_hessian = np.empty(SHAPE4 + (DIM4, DIM4))
    for mu in range(DIM4):
        for nu in range(DIM4):
            sigma_hessian[..., mu, nu] = _d(sigma_gradient[..., nu], mu)
    sigma_box_flat = sum(
        ETA4[axis] * sigma_hessian[..., axis, axis] for axis in range(DIM4)
    )
    sigma_gradient_flat = np.sum(ETA4 * sigma_gradient**2, axis=-1)
    ricci = np.empty(SHAPE4 + (DIM4, DIM4))
    for mu in range(DIM4):
        for nu in range(DIM4):
            ricci[..., mu, nu] = -2.0 * (
                sigma_hessian[..., mu, nu]
                - sigma_gradient[..., mu] * sigma_gradient[..., nu]
            )
            if mu == nu:
                ricci[..., mu, nu] -= ETA4[mu] * (
                    sigma_box_flat + 2.0 * sigma_gradient_flat
                )
    scalar_curvature_4 = exp_minus_two * (
        -6.0 * sigma_box_flat - 6.0 * sigma_gradient_flat
    )
    ricci_uu = np.einsum("...mn,...m,...n->...", ricci, u_contra, u_contra)
    scalar_curvature_3 = (
        scalar_curvature_4 + 2.0 * ricci_uu + k_trace**2 - k_squared
    )

    candidates = np.empty(SHAPE4 + (DIM4, 3))
    for spatial in range(3):
        coordinate_axis = spatial + 1
        candidates[..., :, spatial] = (
            np.eye(DIM4)[:, coordinate_axis]
            + u_contra * u_cov[..., coordinate_axis, None]
        )

    def inner(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        return np.einsum("...mn,...m,...n->...", gamma_cov, left, right)

    frame = np.empty_like(candidates)
    first = candidates[..., :, 0]
    frame[..., :, 0] = first / np.sqrt(inner(first, first))[..., None]
    second = candidates[..., :, 1] - frame[..., :, 0] * inner(
        frame[..., :, 0], candidates[..., :, 1]
    )[..., None]
    frame[..., :, 1] = second / np.sqrt(inner(second, second))[..., None]
    third = candidates[..., :, 2]
    for previous in range(2):
        third = third - frame[..., :, previous] * inner(
            frame[..., :, previous], third
        )[..., None]
    frame[..., :, 2] = third / np.sqrt(inner(third, third))[..., None]
    frame_gram = np.einsum("...mn,...ma,...nb->...ab", gamma_cov, frame, frame)
    return {
        "sqrt_minus_gamma": sqrt_minus_gamma,
        "gamma_cov": gamma_cov,
        "gamma_inverse": gamma_inverse,
        "u_cov": u_cov,
        "u_contra": u_contra,
        "h_cov": h_cov,
        "h_contra": h_contra,
        "K": k_tensor,
        "K_trace": k_trace,
        "K_squared": k_squared,
        "a_cov": acceleration_cov,
        "a_contra": acceleration_contra,
        "a_squared": acceleration_squared,
        "R4": scalar_curvature_4,
        "R3": scalar_curvature_3,
        "frame": frame,
        "frame_orthonormality_error": float(
            np.max(np.abs(frame_gram - np.eye(3)))
        ),
        "khronon_norm_error": float(
            np.max(np.abs(np.einsum("...m,...m->...", u_cov, u_contra) + 1.0))
        ),
    }


def _groupoid_traces(
    primitives: Mapping[str, Any],
    *,
    connection: np.ndarray | None = None,
    phi: np.ndarray | None = None,
    b_form: Mapping[tuple[int, ...], np.ndarray] | None = None,
    groupoid_r: np.ndarray | None = None,
) -> dict[str, Any]:
    source_a = np.asarray(primitives["A_source"] if connection is None else connection)
    source_phi = np.asarray(primitives["phi_source"] if phi is None else phi)
    source_b = primitives["B_source_plus"] if b_form is None else b_form
    r_matrix = np.asarray(primitives["R_groupoid"] if groupoid_r is None else groupoid_r)
    r_inverse = np.swapaxes(r_matrix, -1, -2)
    a_sigma = np.empty(SHAPE4 + (DIM4, 3, 3))
    for axis in range(DIM4):
        source_matrix = _hat(source_a[..., axis, :])
        a_sigma[..., axis, :, :] = (
            np.einsum("...ij,...jk,...lk->...il", r_matrix, source_matrix, r_matrix)
            - np.einsum("...ij,...kj->...ik", _d(r_matrix, axis), r_matrix)
        )
    varphi = np.einsum("...ij,...j->...i", r_matrix, source_phi)
    b_sigma = {
        indices: np.einsum("...ij,...j->...i", r_matrix, value)
        for indices, value in source_b.items()
    }
    return {
        "A_Sigma": a_sigma,
        "varphi": varphi,
        "b": b_sigma,
        "R_inverse": r_inverse,
    }


def _interface_action_sectors(
    primitives: Mapping[str, Any],
    geometry: Mapping[str, Any],
    *,
    frame: np.ndarray | None = None,
    varphi: np.ndarray | None = None,
) -> dict[str, float]:
    sqrt_gamma = geometry["sqrt_minus_gamma"]
    sigma = np.asarray(primitives["sigma"])
    omega = np.asarray(primitives["Omega"])
    selected_frame = geometry["frame"] if frame is None else frame
    selected_varphi = (
        _groupoid_traces(primitives)["varphi"] if varphi is None else varphi
    )
    theta_plus = -4.0 * np.exp(-sigma) * primitives["sigma_normal_plus"]
    theta_minus = -4.0 * np.exp(-sigma) * primitives["sigma_normal_minus"]
    varphi_h = np.einsum("...ma,...a->...m", selected_frame, selected_varphi)
    robin_vector = varphi_h - ROBIN_Y * geometry["a_contra"]
    robin_norm = np.einsum(
        "...mn,...m,...n->...", geometry["h_cov"], robin_vector, robin_vector
    )
    foliation_density = (
        geometry["K_squared"]
        - LAMBDA_K * geometry["K_trace"] ** 2
        + XI * geometry["R3"]
        + ETA * geometry["a_squared"]
        - B4_BAR * geometry["R3"] ** 2 / (16.0 * K_INFINITY**2)
    )
    sectors = {
        "GHY": _integral4(sqrt_gamma * M5 * (theta_plus + theta_minus)),
        "wall_background": _integral4(
            -sqrt_gamma
            * (2.0 * _superpotential(omega) + BRANE_BETA * (omega - 1.0) ** 2 / 2.0)
        ),
        "foliation_lower": _integral4(sqrt_gamma * MB2 * foliation_density / 2.0),
        "Robin_intrinsic": _integral4(
            -sqrt_gamma * ROBIN_KAPPA * robin_norm / 2.0
        ),
    }
    sectors["total"] = sum(sectors.values())
    return sectors


def _compact_lambda5(coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    bump = np.ones(SHAPE5)
    for coordinate in coordinates:
        bump *= np.where(np.sin(coordinate) > 0.0, np.sin(coordinate) ** 4, 0.0)
    return np.stack(
        (
            0.42 * bump * (1.0 + 0.18 * np.sin(coordinates[1])),
            -0.35 * bump * (1.0 + 0.16 * np.cos(coordinates[2])),
            0.31 * bump * (1.0 + 0.14 * np.sin(coordinates[3] + coordinates[4])),
        ),
        axis=-1,
    )


def _lambda4(coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    return np.stack(
        (
            0.23 + _wave(coordinates, 0.29, 0.035),
            -0.17 + _wave(coordinates, 0.67, 0.031),
            0.19 + _wave(coordinates, 1.03, 0.029),
        ),
        axis=-1,
    )


def _gauge_variation5(
    configuration: Mapping[str, Any], gauge_parameter: np.ndarray
) -> dict[str, Any]:
    connection = np.asarray(configuration["A"])
    delta_a = np.empty_like(connection)
    for axis in range(DIM5):
        delta_a[..., axis, :] = -_covariant_component(
            gauge_parameter, connection, axis
        )
    return {
        "A": delta_a,
        "B": {
            key: np.cross(gauge_parameter, value)
            for key, value in configuration["B"].items()
        },
        "phi": np.cross(gauge_parameter, configuration["phi"]),
    }


def _ward_terms(
    configuration: Mapping[str, Any], runtime: Mapping[str, Any]
) -> dict[str, np.ndarray]:
    d_e_a = _covariant_exterior(runtime["E_A"], 4, configuration["A"])[TOP5]
    b_cross_e_b = _wedge_cross_top(configuration["B"], runtime["E_B"], DIM5)
    matter = runtime["geometry"]["sqrt_minus_g"][..., None] * np.cross(
        configuration["phi"], runtime["E_phi"]
    )
    return {
        "D_A_E_A": d_e_a,
        "B_cross_E_B": b_cross_e_b,
        "phi_cross_E_phi_volume": matter,
        "W": d_e_a + b_cross_e_b + matter,
    }


def _ordinary_d_four_form(
    form: Mapping[tuple[int, ...], np.ndarray]
) -> np.ndarray:
    result = np.zeros_like(next(iter(form.values())))
    for position, axis in enumerate(TOP5):
        source = TOP5[:position] + TOP5[position + 1 :]
        result += (-1) ** position * _d(form[source], axis)
    return result


def _bulk_side_certificate(
    configuration: Mapping[str, Any], variation: Mapping[str, Any]
) -> dict[str, Any]:
    runtime = _bulk_runtime(configuration)
    ward = _ward_terms(configuration, runtime)
    d_squared_b = _covariant_exterior(
        runtime["DB"], 4, configuration["A"]
    )[TOP5]
    f_cross_b = _wedge_cross_top(runtime["F"], configuration["B"], DIM5)
    d_squared_b_residual = d_squared_b - f_cross_b
    bianchi = _covariant_exterior(runtime["F"], 2, configuration["A"])
    ordinary_bianchi = _ordinary_exterior_scalar_form(runtime["F"], 2, DIM5)
    d_current = _covariant_exterior(
        runtime["J_four_form"], 4, configuration["A"]
    )[TOP5]
    matter_moment = runtime["geometry"]["sqrt_minus_g"][..., None] * np.cross(
        configuration["phi"], runtime["E_phi"]
    )
    matter_reduction = d_current + matter_moment
    action_routes: dict[str, Any] = {}
    active_sets = {
        "A_only": ("A",),
        "B_only": ("B",),
        "phi_only": ("phi",),
        "A_B_phi": ("A", "B", "phi"),
    }
    for name, active in active_sets.items():
        direct_coarse = _central_action_derivative(
            configuration, variation, active, step=4.0e-5
        )
        direct = _central_action_derivative(
            configuration, variation, active, step=2.0e-5
        )
        euler = _euler_pairing(configuration, runtime, variation, active)
        action_routes[name] = {
            "direct_action_derivative": direct,
            "coarse_step_action_derivative": direct_coarse,
            "coarse_step": 4.0e-5,
            "fine_step": 2.0e-5,
            "step_convergence_difference": abs(direct - direct_coarse),
            "Euler_pairing": euler,
            "absolute_error": abs(direct - euler),
            "active_magnitude": max(abs(direct), abs(euler)),
        }

    omit_c_ephi = runtime["E_phi"] + Z5 * np.sum(
        runtime["c"][..., :, None] * runtime["P_contravariant"], axis=-2
    )
    zero_ephi = np.zeros_like(runtime["E_phi"])
    zero_ea = {key: np.zeros_like(value) for key, value in runtime["E_A"].items()}
    zero_eb = {key: np.zeros_like(value) for key, value in runtime["E_B"].items()}
    direct_all = action_routes["A_B_phi"]["direct_action_derivative"]

    p_without_c_covariant = np.empty_like(runtime["P_covariant"])
    for axis in range(DIM5):
        p_without_c_covariant[..., axis, :] = (
            _d(configuration["phi"], axis)
            + np.cross(
                configuration["A"][..., axis, :], configuration["phi"]
            )
        )
    p_without_c_contravariant = (
        runtime["geometry"]["inverse_diagonal"][..., :, None]
        * p_without_c_covariant
    )
    j_without_c_vector = Z5 * np.cross(
        p_without_c_contravariant, configuration["phi"][..., None, :]
    )
    j_without_c_form = _vector_current_to_four_form(
        j_without_c_vector, runtime["geometry"]["sqrt_minus_g"]
    )
    weighted_p_without_c = (
        runtime["geometry"]["sqrt_minus_g"][..., None, None]
        * p_without_c_contravariant
    )
    divergence_without_c_density = np.zeros_like(configuration["phi"])
    for axis in range(DIM5):
        divergence_without_c_density += _d(
            weighted_p_without_c[..., axis, :], axis
        )
        divergence_without_c_density += np.cross(
            configuration["A"][..., axis, :],
            weighted_p_without_c[..., axis, :],
        )
    e_phi_without_c_in_p = (
        Z5
        * divergence_without_c_density
        / runtime["geometry"]["sqrt_minus_g"][..., None]
        + runtime["E_phi_potential"]
    )
    e_a_without_c_in_p = _form_add(runtime["DB"], j_without_c_form)
    omit_c_from_p_pairing = _euler_pairing(
        configuration,
        runtime,
        variation,
        ("A", "B", "phi"),
        e_a_override=e_a_without_c_in_p,
        e_phi_override=e_phi_without_c_in_p,
    )
    circular_pairing = _euler_pairing(
        configuration,
        runtime,
        variation,
        ("A", "B", "phi"),
        e_a_override=zero_ea,
        e_b_override=zero_eb,
        e_phi_override=zero_ephi,
    )
    forced_d_ea = -(
        ward["B_cross_E_B"] + ward["phi_cross_E_phi_volume"]
    )
    circular_forced_w = (
        forced_d_ea
        + ward["B_cross_E_B"]
        + ward["phi_cross_E_phi_volume"]
    )
    actual_d_zero_ea = _covariant_exterior(
        zero_ea, 4, configuration["A"]
    )[TOP5]

    omit_bf_pairing = _euler_pairing(
        configuration,
        runtime,
        variation,
        ("A", "B", "phi"),
        e_a_override=runtime["J_four_form"],
        e_b_override=zero_eb,
    )
    omit_potential_pairing = _euler_pairing(
        configuration,
        runtime,
        variation,
        ("A", "B", "phi"),
        e_phi_override=runtime["E_phi_kinetic"],
    )

    e_a_without_j = runtime["DB"]
    d_ea_without_j = _covariant_exterior(
        e_a_without_j, 4, configuration["A"]
    )[TOP5]
    d_ea_ordinary = _ordinary_d_four_form(runtime["E_A"])
    matter_without_c = runtime["geometry"]["sqrt_minus_g"][..., None] * np.cross(
        configuration["phi"], omit_c_ephi
    )
    mutants = {
        "omit_BF_from_Euler_action_mismatch": abs(direct_all - omit_bf_pairing),
        "omit_E_B_from_W": _l2(
            ward["D_A_E_A"] + ward["phi_cross_E_phi_volume"]
        ),
        "omit_J_from_E_A": _l2(
            d_ea_without_j
            + ward["B_cross_E_B"]
            + ward["phi_cross_E_phi_volume"]
        ),
        "omit_material_E_phi": _l2(
            ward["D_A_E_A"] + ward["B_cross_E_B"]
        ),
        "omit_c_M_P_M_in_E_phi": _l2(
            ward["D_A_E_A"] + ward["B_cross_E_B"] + matter_without_c
        ),
        "omit_c_phi_from_P_action_mismatch": abs(
            direct_all - omit_c_from_p_pairing
        ),
        "flip_J_A_sign": _l2(-d_current + matter_moment),
        "flip_D_A_E_A_sign": _l2(
            -ward["D_A_E_A"]
            + ward["B_cross_E_B"]
            + ward["phi_cross_E_phi_volume"]
        ),
        "flip_E_B_sign": _l2(
            ward["D_A_E_A"]
            - ward["B_cross_E_B"]
            + ward["phi_cross_E_phi_volume"]
        ),
        "abelianize_D_A_and_curvature_terms": _l2(
            d_ea_ordinary + ward["phi_cross_E_phi_volume"]
        ),
        "omit_radial_V4_from_Euler_action_mismatch": abs(
            direct_all - omit_potential_pairing
        ),
    }
    radial_moment = np.cross(
        configuration["phi"], runtime["E_phi_potential"]
    )
    omega = configuration["Omega"]
    phi = configuration["phi"]
    anisotropic_ephi = np.zeros_like(phi)
    anisotropic_ephi[..., 0] = (
        -Z5 * MATERIAL_M**2 * omega**-5.0 * 0.23 * phi[..., 1]
    )
    anisotropic_ephi[..., 1] = (
        -Z5 * MATERIAL_M**2 * omega**-5.0 * 0.23 * phi[..., 0]
    )
    anisotropic_moment = np.cross(phi, anisotropic_ephi)

    euler_norms = {
        "E_A": float(
            np.sqrt(np.mean([_l2(value) ** 2 for value in runtime["E_A"].values()]))
        ),
        "E_B": float(
            np.sqrt(np.mean([_l2(value) ** 2 for value in runtime["E_B"].values()]))
        ),
        "E_phi": _l2(runtime["E_phi"]),
    }
    form_activity: dict[str, list[float]] = {}
    representative_fields = {
        "metric_sigma": configuration["sigma"][..., None],
        "Omega": configuration["Omega"][..., None],
        "A": configuration["A"].reshape(SHAPE5 + (-1,)),
        "B": np.concatenate(
            [value for value in configuration["B"].values()], axis=-1
        ),
        "phi": configuration["phi"],
    }
    for name, value in representative_fields.items():
        form_activity[name] = [_l2(_d(value, axis)) for axis in range(DIM5)]

    return {
        "side": "+" if configuration["side"] == 1 else "-",
        "action_sectors": _bulk_action_sectors(configuration),
        "action_to_Euler": action_routes,
        "off_shell_Euler_norms": euler_norms,
        "Ward": {
            "L2_residual": _l2(ward["W"]),
            "Linf_residual": _linf(ward["W"]),
            "term_L2_norms": {
                key: _l2(ward[key])
                for key in (
                    "D_A_E_A",
                    "B_cross_E_B",
                    "phi_cross_E_phi_volume",
                )
            },
            "per_generator": {
                f"W_{internal + 1}": {
                    "L2": _l2(ward["W"][..., internal]),
                    "Linf": _linf(ward["W"][..., internal]),
                }
                for internal in range(3)
            },
        },
        "separated_structural_identities": {
            "D_A_squared_B": {
                "identity": "D_A^2 B=[F,B]:=F cross-wedge B=-B cross-wedge F",
                "L2_residual": _l2(d_squared_b_residual),
                "Linf_residual": _linf(d_squared_b_residual),
                "D_A_squared_B_L2": _l2(d_squared_b),
                "F_cross_B_L2": _l2(f_cross_b),
                "flip_curvature_commutator_sign_mutant_L2": _l2(
                    d_squared_b + f_cross_b
                ),
            },
            "D_A_F_Bianchi": {
                "identity": "D_A F=0 as an adjoint-valued 3-form in five dimensions",
                "component_count": len(bianchi),
                "L2_residual": float(
                    np.sqrt(np.mean([_l2(value) ** 2 for value in bianchi.values()]))
                ),
                "Linf_residual": max(_linf(value) for value in bianchi.values()),
                "ordinary_d_instead_of_D_A_mutant_L2": float(
                    np.sqrt(
                        np.mean([_l2(value) ** 2 for value in ordinary_bianchi.values()])
                    )
                ),
            },
            "material_current": {
                "identity": "D_A J_A+sqrt(-g) phi cross E_phi d5x=0",
                "L2_residual": _l2(matter_reduction),
                "Linf_residual": _linf(matter_reduction),
                "D_A_J_A_L2": _l2(d_current),
                "matter_moment_L2": _l2(matter_moment),
                "per_generator": {
                    f"W_material_{internal + 1}": {
                        "L2": _l2(matter_reduction[..., internal]),
                        "Linf": _linf(matter_reduction[..., internal]),
                    }
                    for internal in range(3)
                },
                "flip_J_A_sign_mutant_L2": _l2(-d_current + matter_moment),
            },
        },
        "five_coordinate_activity": form_activity,
        "matter": {
            "Omega_minimum": float(np.min(omega)),
            "Omega_maximum": float(np.max(omega)),
            "c_covector_L2": _l2(runtime["c"]),
            "P_covector_L2": _l2(runtime["P_covariant"].reshape(SHAPE5 + (-1, 3))),
            "radial_V4_E_phi_L2": _l2(runtime["E_phi_potential"]),
            "radial_V4_moment_L2": _l2(radial_moment),
            "rho_zero_extension_Linf": _linf(
                _radial_potential_euler(omega, np.zeros_like(phi))
            ),
            "anisotropic_V4_mutant_E_phi_L2": _l2(anisotropic_ephi),
            "anisotropic_V4_mutant_moment_L2": _l2(anisotropic_moment),
        },
        "mutant_witnesses": mutants,
        "circular_Euler_detector": {
            "forced_W_L2": _l2(circular_forced_w),
            "actual_D_of_zero_E_A_vs_forced_D_L2": _l2(
                actual_d_zero_ea - forced_d_ea
            ),
            "action_to_circular_Euler_mismatch": abs(
                direct_all - circular_pairing
            ),
        },
    }


def _compact_gauge_certificate(
    plus: Mapping[str, Any], minus: Mapping[str, Any]
) -> dict[str, Any]:
    sides = []
    for number, configuration in enumerate((plus, minus)):
        gauge_parameter = _compact_lambda5(configuration["coordinates"])
        variation = _gauge_variation5(configuration, gauge_parameter)
        runtime = _bulk_runtime(configuration)
        direct = _central_action_derivative(
            configuration, variation, ("A", "B", "phi")
        )
        euler = _euler_pairing(
            configuration, runtime, variation, ("A", "B", "phi")
        )
        boundary_trace = []
        for axis in range(DIM5):
            boundary_trace.extend(
                (
                    np.take(gauge_parameter, 0, axis=axis).ravel(),
                    np.take(gauge_parameter, -1, axis=axis).ravel(),
                )
            )
        mutant_direct = _central_action_derivative(
            configuration,
            variation,
            ("A", "B", "phi"),
            anisotropic_potential=True,
        )
        sides.append(
            {
                "side": "+" if number == 0 else "-",
                "support_fraction": float(
                    np.mean(np.linalg.norm(gauge_parameter, axis=-1) > 0.0)
                ),
                "boundary_trace_max": float(
                    max(np.max(np.abs(values)) for values in boundary_trace)
                ),
                "three_generator_L2": [
                    _l2(gauge_parameter[..., internal]) for internal in range(3)
                ],
                "direct_full_action_derivative": direct,
                "Euler_pairing": euler,
                "direct_vs_Euler_error": abs(direct - euler),
                "anisotropic_V4_mutant_direct_gauge_derivative": mutant_direct,
            }
        )
    return {"compact_lambda_is_first": True, "sides": sides}


def _source_groupoid_direction(
    primitives: Mapping[str, Any], gauge_parameter: np.ndarray
) -> dict[str, Any]:
    source_a = primitives["A_source"]
    delta_a = np.empty_like(source_a)
    for axis in range(DIM4):
        delta_a[..., axis, :] = -(
            _d(gauge_parameter, axis)
            + np.cross(source_a[..., axis, :], gauge_parameter)
        )
    return {
        "A": delta_a,
        "B": {
            key: np.cross(gauge_parameter, value)
            for key, value in primitives["B_source_plus"].items()
        },
        "phi": np.cross(gauge_parameter, primitives["phi_source"]),
        "R": -np.einsum(
            "...ij,...jk->...ik", primitives["R_groupoid"], _hat(gauge_parameter)
        ),
    }


def _interface_robin_data(
    primitives: Mapping[str, Any],
    geometry: Mapping[str, Any],
    frame: np.ndarray,
    varphi: np.ndarray,
) -> dict[str, np.ndarray]:
    varphi_h = np.einsum("...ma,...a->...m", frame, varphi)
    robin_vector = varphi_h - ROBIN_Y * geometry["a_contra"]
    h_times_r = np.einsum("...mn,...n->...m", geometry["h_cov"], robin_vector)
    e_varphi = -(
        ROBIN_KAPPA
        * geometry["sqrt_minus_gamma"][..., None]
        * np.einsum("...ma,...m->...a", frame, h_times_r)
    )
    e_frame = -(
        ROBIN_KAPPA
        * geometry["sqrt_minus_gamma"][..., None, None]
        * h_times_r[..., :, None]
        * varphi[..., None, :]
    )
    return {
        "r": robin_vector,
        "E_varphi": e_varphi,
        "E_frame": e_frame,
    }


def _central_interface_direction(
    primitives: Mapping[str, Any],
    geometry: Mapping[str, Any],
    frame: np.ndarray,
    varphi: np.ndarray,
    delta_frame: np.ndarray,
    delta_varphi: np.ndarray,
) -> float:
    step = 2.0e-5

    def action(scale: float) -> float:
        return _interface_action_sectors(
            primitives,
            geometry,
            frame=frame + scale * delta_frame,
            varphi=varphi + scale * delta_varphi,
        )["total"]

    return (action(step) - action(-step)) / (2.0 * step)


def _interface_gauge_certificate(
    primitives: Mapping[str, Any], geometry: Mapping[str, Any]
) -> dict[str, Any]:
    gauge_parameter = _lambda4(primitives["coordinates"])
    groupoid = _groupoid_traces(primitives)
    direction = _source_groupoid_direction(primitives, gauge_parameter)
    step = 2.0e-5

    def traces(scale: float, include_r: bool = True) -> dict[str, Any]:
        return _groupoid_traces(
            primitives,
            connection=primitives["A_source"] + scale * direction["A"],
            phi=primitives["phi_source"] + scale * direction["phi"],
            b_form={
                key: primitives["B_source_plus"][key] + scale * direction["B"][key]
                for key in primitives["B_source_plus"]
            },
            groupoid_r=(
                primitives["R_groupoid"] + scale * direction["R"]
                if include_r
                else primitives["R_groupoid"]
            ),
        )

    traces_plus = traces(step)
    traces_minus = traces(-step)
    trace_derivatives = {
        "varphi": (traces_plus["varphi"] - traces_minus["varphi"]) / (2.0 * step),
        "A_Sigma": (traces_plus["A_Sigma"] - traces_minus["A_Sigma"])
        / (2.0 * step),
        "b": {
            key: (traces_plus["b"][key] - traces_minus["b"][key])
            / (2.0 * step)
            for key in traces_plus["b"]
        },
    }
    trace_l2 = {
        "delta_varphi": _l2(trace_derivatives["varphi"]),
        "delta_A_Sigma": _l2(trace_derivatives["A_Sigma"].reshape(SHAPE4 + (-1,))),
        "delta_b": float(
            np.sqrt(np.mean([_l2(value) ** 2 for value in trace_derivatives["b"].values()]))
        ),
    }
    mutant_plus = traces(step, include_r=False)
    mutant_minus = traces(-step, include_r=False)
    mutant_varphi_direction = (
        mutant_plus["varphi"] - mutant_minus["varphi"]
    ) / (2.0 * step)

    frame = geometry["frame"]
    varphi = groupoid["varphi"]
    robin = _interface_robin_data(primitives, geometry, frame, varphi)
    source_delta_varphi = np.einsum(
        "...ij,...j->...i", direction["R"], primitives["phi_source"]
    ) + np.einsum(
        "...ij,...j->...i", primitives["R_groupoid"], direction["phi"]
    )
    source_robin_pairing = _integral4(
        np.sum(robin["E_varphi"] * source_delta_varphi, axis=-1)
    )
    source_mutant_pairing = _integral4(
        np.sum(robin["E_varphi"] * mutant_varphi_direction, axis=-1)
    )
    source_direct = _central_interface_direction(
        primitives,
        geometry,
        frame,
        varphi,
        np.zeros_like(frame),
        source_delta_varphi,
    )
    source_mutant_direct = _central_interface_direction(
        primitives,
        geometry,
        frame,
        varphi,
        np.zeros_like(frame),
        mutant_varphi_direction,
    )

    q_parameter = np.stack(
        (
            _wave(primitives["coordinates"], 0.35, 0.025),
            _wave(primitives["coordinates"], 0.79, 0.027),
            _wave(primitives["coordinates"], 1.17, 0.023),
        ),
        axis=-1,
    )
    delta_varphi_q = np.cross(q_parameter, varphi)
    delta_frame_q = np.cross(q_parameter[..., None, :], frame)
    q_pairing = _integral4(
        np.sum(robin["E_varphi"] * delta_varphi_q, axis=-1)
        + np.sum(robin["E_frame"] * delta_frame_q, axis=(-2, -1))
    )
    q_direct = _central_interface_direction(
        primitives,
        geometry,
        frame,
        varphi,
        delta_frame_q,
        delta_varphi_q,
    )
    q_frame_fixed_mutant = _central_interface_direction(
        primitives,
        geometry,
        frame,
        varphi,
        np.zeros_like(frame),
        delta_varphi_q,
    )
    sectors = _interface_action_sectors(primitives, geometry)
    sector_activity = {key: abs(value) for key, value in sectors.items() if key != "total"}
    return {
        "all_literal_interface_terms": {
            "terms": ["GHY", "wall_background", "foliation_lower", "Robin_intrinsic"],
            "action_values": sectors,
            "minimum_sector_activity": min(sector_activity.values()),
            "gauge_neutral_without_internal_indices": [
                "GHY",
                "wall_background",
                "foliation_lower",
            ],
            "Robin_uses": "h_mu_nu*(e_Q_a^mu varphi^a-y a^mu)*(e_Q_b^nu varphi^b-y a^nu)",
            "frame_orthonormality_error": geometry["frame_orthonormality_error"],
            "khronon_unit_norm_error": geometry["khronon_norm_error"],
        },
        "source_P_gauge_groupoid": {
            "convention": {
                "delta_A": "-D_A lambda",
                "delta_phi": "lambda cross phi",
                "delta_B": "lambda cross B",
                "delta_R": "-R hat(lambda), with Q fixed",
                "varphi": "R phi",
                "A_Sigma": "R A R^-1-dR R^-1",
                "b": "R B",
            },
            "trace_derivative_L2": trace_l2,
            "Robin_direct_derivative": source_direct,
            "Robin_Euler_pairing": source_robin_pairing,
            "omit_delta_R_mutant_direct_derivative": source_mutant_direct,
            "omit_delta_R_mutant_Euler_pairing": source_mutant_pairing,
        },
        "target_Q_frame_Ward": {
            "delta_varphi": "q cross varphi",
            "delta_frame": "q cross e_Q on its internal index",
            "direct_derivative": q_direct,
            "Euler_pairing": q_pairing,
            "frame_fixed_mutant_direct_derivative": q_frame_fixed_mutant,
        },
    }


def _vee(matrix: np.ndarray) -> np.ndarray:
    return np.stack(
        (
            0.5 * (matrix[..., 2, 1] - matrix[..., 1, 2]),
            0.5 * (matrix[..., 0, 2] - matrix[..., 2, 0]),
            0.5 * (matrix[..., 1, 0] - matrix[..., 0, 1]),
        ),
        axis=-1,
    )


def _boundary_green_and_bfv_certificate(
    plus: Mapping[str, Any],
    minus: Mapping[str, Any],
    primitives: Mapping[str, Any],
) -> dict[str, Any]:
    runtime = _bulk_runtime(plus)
    gauge_parameter = _lambda4(primitives["coordinates"])
    source_a = primitives["A_source"]
    d_lambda: dict[tuple[int, ...], np.ndarray] = {}
    for axis in range(DIM4):
        d_lambda[(axis,)] = _d(gauge_parameter, axis) + np.cross(
            source_a[..., axis, :], gauge_parameter
        )
    b_trace = primitives["B_source_plus"]
    theta_bf = _wedge_dot_top(b_trace, d_lambda, DIM4)
    e_a_trace = runtime["E_A"][TOP4][..., 0, :]
    j_trace = runtime["J_four_form"][TOP4][..., 0, :]
    theta_matter = np.sum(gauge_parameter * j_trace, axis=-1)
    theta_total = theta_bf + theta_matter
    lambda_e_a = np.sum(gauge_parameter * e_a_trace, axis=-1)
    charge = {
        indices: np.sum(value * gauge_parameter, axis=-1)
        for indices, value in b_trace.items()
    }
    d_charge = _ordinary_exterior_scalar_form(charge, 3, DIM4)[TOP4]
    exact_rhs = -d_charge
    green_residual = theta_total - lambda_e_a - exact_rhs
    omit_theta_matter = theta_bf - lambda_e_a - exact_rhs
    omit_current_in_ea = theta_total - np.sum(
        gauge_parameter * (e_a_trace - j_trace), axis=-1
    ) - exact_rhs

    groupoid_plus = _groupoid_traces(primitives)
    groupoid_minus = _groupoid_traces(
        primitives, b_form=primitives["B_source_minus"]
    )
    gluing_defect = {
        key: groupoid_plus["b"][key] - groupoid_minus["b"][key]
        for key in groupoid_plus["b"]
    }
    a_sigma_vector = _vee(groupoid_plus["A_Sigma"])
    target_parameter = np.stack(
        (
            0.21 + _wave(primitives["coordinates"], 0.22, 0.024),
            -0.16 + _wave(primitives["coordinates"], 0.64, 0.022),
            0.18 + _wave(primitives["coordinates"], 1.02, 0.020),
        ),
        axis=-1,
    )
    delta_a_sigma = {
        (axis,): -(
            _d(target_parameter, axis)
            + np.cross(a_sigma_vector[..., axis, :], target_parameter)
        )
        for axis in range(DIM4)
    }
    glued_bfv_density = -_wedge_dot_top(gluing_defect, delta_a_sigma, DIM4)
    unglued_defect = {
        key: value
        + np.stack(
            [
                _wave(
                    primitives["coordinates"],
                    0.31 + 0.27 * component + 0.19 * internal,
                    0.018,
                )
                for internal in range(3)
            ],
            axis=-1,
        )
        for component, (key, value) in enumerate(gluing_defect.items())
    }
    unglued_bfv_density = -_wedge_dot_top(
        unglued_defect, delta_a_sigma, DIM4
    )
    defect_l2 = float(
        np.sqrt(np.mean([_l2(value) ** 2 for value in gluing_defect.values()]))
    )
    unglued_l2 = float(
        np.sqrt(np.mean([_l2(value) ** 2 for value in unglued_defect.values()]))
    )
    return {
        "boundary_Green_identity": {
            "formula": "Theta_gauge-<lambda,E_A>=-d_boundary<B lambda>",
            "Theta_BF_L2": _l2(theta_bf),
            "Theta_matter_current_L2": _l2(theta_matter),
            "E_A_material_current_trace_L2": _l2(j_trace),
            "lambda_E_A_L2": _l2(lambda_e_a),
            "charge_3form_L2": float(
                np.sqrt(np.mean([_l2(value) ** 2 for value in charge.values()]))
            ),
            "exact_4form_L2": _l2(exact_rhs),
            "exact_4form_integral": _integral4(exact_rhs),
            "identity_L2_residual": _l2(green_residual),
            "identity_Linf_residual": _linf(green_residual),
            "omit_matter_from_Theta_mutant_L2": _l2(omit_theta_matter),
            "omit_material_J_from_E_A_mutant_L2": _l2(omit_current_in_ea),
        },
        "interface_lambda_and_BFV": {
            "lambda_interface_L2": _l2(gauge_parameter),
            "oriented_signs": {"plus": 1, "minus": -1},
            "selected_local_trace_gluing_defect_L2": defect_l2,
            "selected_glued_BFV_residual_L2": _l2(glued_bfv_density),
            "selected_glued_BFV_residual_integral": _integral4(glued_bfv_density),
            "unglued_defect_L2": unglued_l2,
            "unglued_BFV_residual_L2": _l2(unglued_bfv_density),
            "unglued_BFV_residual_integral": _integral4(unglued_bfv_density),
            "selected_local_gluing_demonstrated": True,
            "global_or_large_gauge_gluing_claimed": False,
            "complete_BV_BFV_boundary_complex_claimed": False,
        },
    }


def _roll_bulk_configuration(
    configuration: Mapping[str, Any], axis: int
) -> dict[str, Any]:
    output = dict(configuration)
    output["sigma"] = np.roll(configuration["sigma"], 1, axis=axis)
    output["Omega"] = np.roll(configuration["Omega"], 1, axis=axis)
    output["A"] = np.roll(configuration["A"], 1, axis=axis)
    output["phi"] = np.roll(configuration["phi"], 1, axis=axis)
    output["B"] = {
        key: np.roll(value, 1, axis=axis) for key, value in configuration["B"].items()
    }
    output.pop("_geometry", None)
    return output


def _translation_naturality_certificate(
    plus: Mapping[str, Any], minus: Mapping[str, Any]
) -> dict[str, Any]:
    bulk_differences: dict[str, list[float]] = {}
    for label, configuration in (("plus", plus), ("minus", minus)):
        reference = _bulk_action(configuration)
        bulk_differences[label] = [
            abs(_bulk_action(_roll_bulk_configuration(configuration, axis)) - reference)
            for axis in range(DIM5)
        ]
    return {
        "independent_restricted_test": "constant periodic translations recomputed from the full 5D action",
        "bulk_translation_action_differences": bulk_differences,
        "maximum_bulk_translation_action_difference": max(
            value for rows in bulk_differences.values() for value in rows
        ),
        "full_diffeomorphism_khronon_Ward_completed": False,
        "missing_for_full_diffeomorphism_khronon_Ward": [
            "arbitrary local five-dimensional xi with independent metric Euler and GHY cancellation",
            "moving two-sided embeddings and all normal pullback momenta on one common family",
            "direct khronon T Euler variation of foliation and Robin terms beyond constant translations",
            "regulated corners and the relative BF BV-BFV edge complex",
        ],
    }


@lru_cache(maxsize=1)
def full_action_certificate() -> dict[str, Any]:
    plus = _bulk_configuration(1)
    minus = _bulk_configuration(-1)
    plus_certificate = _bulk_side_certificate(plus, _variation(0.37))
    minus_certificate = _bulk_side_certificate(minus, _variation(0.91))
    compact = _compact_gauge_certificate(plus, minus)
    primitives = _interface_primitives(plus, minus)
    geometry = _interface_geometry(primitives)
    interface = _interface_gauge_certificate(primitives, geometry)
    boundary = _boundary_green_and_bfv_certificate(
        plus, minus, primitives
    )
    translation = _translation_naturality_certificate(plus, minus)
    return {
        "form_degree_contract": {
            "ambient_dimension": 5,
            "bulk_grid_shape": [GRID5] * DIM5,
            "interface_grid_shape": [GRID4] * DIM4,
            "spectral_grid_policy": (
                "odd N=7 avoids a Nyquist singleton; all primitive waves use modes <=1, "
                "while non-polynomial composite aliasing is retained as a measured Ward residual"
            ),
            "dealiasing_claimed": False,
            "active_coordinates": ["x0", "x1", "x2", "x3", "x4"],
            "internal_generators": 3,
            "A": {"degree": 1, "independent_components": len(_tuples(1))},
            "B": {"degree": 3, "independent_components": len(_tuples(3))},
            "F_and_E_B": {"degree": 2, "independent_components": len(_tuples(2))},
            "D_B_J_and_E_A": {"degree": 4, "independent_components": len(_tuples(4))},
            "W": {"degree": 5, "independent_components": len(_tuples(5))},
            "metric_signature": [-1, 1, 1, 1, 1],
            "dimensional_reduction_or_spectator_ansatz_used": False,
        },
        "bulk_sides": {"plus": plus_certificate, "minus": minus_certificate},
        "compact_lambda_first": compact,
        "interface_4D": interface,
        "boundary_Green_and_BFV": boundary,
        "diffeomorphism_khronon_attempt": translation,
    }


def _v5_5_2_control_receipt() -> dict[str, Any]:
    slots = V5_5_2_PAYLOAD["formula_ledger"]["literal_variational_coordinates"]
    certificates = V5_5_2_PAYLOAD["certificates"]
    decision = V5_5_2_PAYLOAD["decision"]
    return {
        "path": str(V5_5_2.relative_to(REPO)),
        "sha256": EXPECTED_V5_5_2_SHA256,
        "schema": EXPECTED_V5_5_2_SCHEMA,
        "literal_slots": {
            "omega": slots["omega"],
            "v": slots["v"],
            "b_shift": slots["b_shift"],
        },
        "ADM_Jacobian_rank": certificates["ADM_Jacobian"]["Jacobian_rank"],
        "Israel_projection_reconstruction_error": certificates[
            "Israel_Brown_York_reconstruction"
        ]["projection_reconstruction_error"],
        "matter_T_ui_norm": certificates["matter_shift_and_Robin"]["T_ui_norm"],
        "imported_control_flags": {
            "induced_ADM_bidirectional_Jacobian_pass": decision[
                "induced_ADM_bidirectional_Jacobian_pass"
            ],
            "literal_slot_coordinate_contract_pass": decision[
                "literal_slot_coordinate_contract_pass"
            ],
            "single_Israel_Brown_York_tensor_reconstruction_pass": decision[
                "single_Israel_Brown_York_tensor_reconstruction_pass"
            ],
            "bulk_matter_shift_momentum_witness_pass": decision[
                "bulk_matter_shift_momentum_witness_pass"
            ],
        },
        "scope": "ADM/Israel/T_ui controls only; no inherited Ward boolean",
    }


def build_payload() -> dict[str, Any]:
    _load_sources()
    certificate = full_action_certificate()
    sides = certificate["bulk_sides"]
    compact_sides = certificate["compact_lambda_first"]["sides"]
    interface = certificate["interface_4D"]
    boundary = certificate["boundary_Green_and_BFV"]
    translation = certificate["diffeomorphism_khronon_attempt"]
    form_contract = certificate["form_degree_contract"]

    action_rows = [
        row
        for side in sides.values()
        for row in side["action_to_Euler"].values()
    ]
    ward_rows = [side["Ward"] for side in sides.values()]
    structural_rows = [
        side["separated_structural_identities"] for side in sides.values()
    ]
    structural_residuals = [
        value
        for row in structural_rows
        for value in (
            row["D_A_squared_B"]["L2_residual"],
            row["D_A_F_Bianchi"]["L2_residual"],
            row["material_current"]["L2_residual"],
        )
    ]
    structural_mutants = [
        value
        for row in structural_rows
        for value in (
            row["D_A_squared_B"][
                "flip_curvature_commutator_sign_mutant_L2"
            ],
            row["D_A_F_Bianchi"][
                "ordinary_d_instead_of_D_A_mutant_L2"
            ],
            row["material_current"]["flip_J_A_sign_mutant_L2"],
        )
    ]
    matter_rows = [side["matter"] for side in sides.values()]
    mutant_values = [
        value
        for side in sides.values()
        for value in side["mutant_witnesses"].values()
    ]
    activity_values = [
        value
        for side in sides.values()
        for field in side["five_coordinate_activity"].values()
        for value in field
    ]
    circular_rows = [side["circular_Euler_detector"] for side in sides.values()]
    source_groupoid = interface["source_P_gauge_groupoid"]
    target_frame = interface["target_Q_frame_Ward"]
    green = boundary["boundary_Green_identity"]
    bfv = boundary["interface_lambda_and_BFV"]

    checks = {
        "v5_2_full_literal_action_and_coefficients_are_hash_pinned": (
            _sha256(V5_2) == EXPECTED_V5_2_SHA256
            and V5_2_PAYLOAD["exact_classical_charter"]["exact_action"]
            == EXPECTED_ACTIONS
            and V5_2_PAYLOAD["exact_classical_charter"]["coefficient_policy"][
                "parameters"
            ]
            == EXPECTED_COEFFICIENTS
        ),
        "v5_5_2_ADM_controls_are_hash_pinned_not_Ward_inherited": (
            _sha256(V5_5_2) == EXPECTED_V5_5_2_SHA256
            and _v5_5_2_control_receipt()["ADM_Jacobian_rank"] == 10
            and _v5_5_2_control_receipt()["matter_T_ui_norm"] > 1.0e-3
            and all(
                _v5_5_2_control_receipt()["imported_control_flags"].values()
            )
        ),
        "real_5D_exterior_form_degrees_and_all_coordinates_are_active": (
            form_contract["ambient_dimension"] == 5
            and form_contract["A"]["independent_components"] == 5
            and form_contract["B"]["independent_components"] == 10
            and form_contract["F_and_E_B"]["independent_components"] == 10
            and form_contract["D_B_J_and_E_A"]["independent_components"] == 5
            and form_contract["W"]["independent_components"] == 1
            and form_contract["dimensional_reduction_or_spectator_ansatz_used"]
            is False
            and min(activity_values) > 1.0e-4
        ),
        "every_literal_bulk_sector_is_nonzero_on_both_sides": all(
            abs(value) > 1.0e-5
            for side in sides.values()
            for key, value in side["action_sectors"].items()
            if key != "total"
        ),
        "full_action_variation_matches_independent_Euler_forms": (
            max(row["absolute_error"] for row in action_rows) < 2.0e-6
            and max(row["step_convergence_difference"] for row in action_rows)
            < 2.0e-5
            and min(row["active_magnitude"] for row in action_rows) > 1.0e-4
        ),
        "bulk_SO3_Ward_closes_off_shell_on_both_sides": (
            max(row["L2_residual"] for row in ward_rows) < 5.0e-4
            and max(row["Linf_residual"] for row in ward_rows) < 2.0e-3
            and min(
                value
                for row in ward_rows
                for value in row["term_L2_norms"].values()
            )
            > 1.0e-4
            and min(
                value
                for side in sides.values()
                for value in side["off_shell_Euler_norms"].values()
            )
            > 1.0e-4
        ),
        "curvature_Bianchi_and_material_reductions_close_separately": all(
            row["D_A_squared_B"]["L2_residual"] < 5.0e-4
            and row["D_A_squared_B"]["Linf_residual"] < 2.0e-3
            and row["D_A_squared_B"]["D_A_squared_B_L2"] > 1.0e-4
            and row["D_A_squared_B"]["F_cross_B_L2"] > 1.0e-4
            and row["D_A_squared_B"][
                "flip_curvature_commutator_sign_mutant_L2"
            ]
            > 1.0e-4
            and row["D_A_F_Bianchi"]["component_count"] == 10
            and row["D_A_F_Bianchi"]["L2_residual"] < 5.0e-4
            and row["D_A_F_Bianchi"]["Linf_residual"] < 2.0e-3
            and row["D_A_F_Bianchi"][
                "ordinary_d_instead_of_D_A_mutant_L2"
            ]
            > 1.0e-4
            and row["material_current"]["L2_residual"] < 5.0e-4
            and row["material_current"]["Linf_residual"] < 2.0e-3
            and row["material_current"]["D_A_J_A_L2"] > 1.0e-4
            and row["material_current"]["matter_moment_L2"] > 1.0e-4
            and len(row["material_current"]["per_generator"]) == 3
            and max(
                norm
                for generator in row["material_current"]["per_generator"].values()
                for norm in generator.values()
            )
            < 2.0e-3
            and row["material_current"]["flip_J_A_sign_mutant_L2"] > 1.0e-4
            for row in structural_rows
        ),
        "separated_identity_mutants_exceed_numerical_residuals": (
            min(structural_mutants) > 1.0e-4
            and min(structural_mutants) / max(structural_residuals) > 10.0
        ),
        "Omega_c_and_full_radial_V4_are_active_and_covariant": (
            min(row["Omega_minimum"] for row in matter_rows) > 0.0
            and min(row["c_covector_L2"] for row in matter_rows) > 1.0e-4
            and min(row["P_covector_L2"] for row in matter_rows) > 1.0e-4
            and min(row["radial_V4_E_phi_L2"] for row in matter_rows) > 1.0e-4
            and max(row["radial_V4_moment_L2"] for row in matter_rows) < 1.0e-12
            and max(row["rho_zero_extension_Linf"] for row in matter_rows) == 0.0
            and min(
                row["anisotropic_V4_mutant_moment_L2"] for row in matter_rows
            )
            > 1.0e-4
        ),
        "all_bulk_mutants_are_killed": (
            min(mutant_values) > 1.0e-4
            and min(mutant_values)
            / max(row["L2_residual"] for row in ward_rows)
            > 10.0
        ),
        "circular_W_oracle_is_rejected_by_action_variation": all(
            row["forced_W_L2"] < 1.0e-15
            and row["actual_D_of_zero_E_A_vs_forced_D_L2"] > 1.0e-4
            and row["action_to_circular_Euler_mismatch"] > 1.0e-4
            for row in circular_rows
        ),
        "compact_lambda_is_tested_first_and_bad_V4_breaks_it": all(
            0.0 < row["support_fraction"] < 0.5
            and row["boundary_trace_max"] < 1.0e-14
            and min(row["three_generator_L2"]) > 1.0e-5
            and abs(row["direct_full_action_derivative"]) < 2.0e-6
            and abs(row["Euler_pairing"]) < 2.0e-6
            and row["direct_vs_Euler_error"] < 2.0e-6
            and abs(row["anisotropic_V4_mutant_direct_gauge_derivative"])
            > 1.0e-4
            for row in compact_sides
        ),
        "all_v5_2_interface_terms_and_source_groupoid_Ward_execute": (
            interface["all_literal_interface_terms"]["terms"]
            == ["GHY", "wall_background", "foliation_lower", "Robin_intrinsic"]
            and interface["all_literal_interface_terms"]["minimum_sector_activity"]
            > 1.0e-5
            and interface["all_literal_interface_terms"][
                "frame_orthonormality_error"
            ]
            < 1.0e-10
            and max(source_groupoid["trace_derivative_L2"].values()) < 5.0e-5
            and abs(source_groupoid["Robin_direct_derivative"]) < 2.0e-7
            and abs(source_groupoid["Robin_Euler_pairing"]) < 2.0e-7
            and abs(source_groupoid["omit_delta_R_mutant_direct_derivative"])
            > 1.0e-4
            and abs(source_groupoid["omit_delta_R_mutant_Euler_pairing"])
            > 1.0e-4
        ),
        "target_Q_frame_and_varphi_Robin_Ward_executes": (
            abs(target_frame["direct_derivative"]) < 2.0e-7
            and abs(target_frame["Euler_pairing"]) < 2.0e-7
            and abs(target_frame["frame_fixed_mutant_direct_derivative"])
            > 1.0e-4
        ),
        "boundary_Green_charge_exact_and_material_current_close": (
            green["Theta_BF_L2"] > 1.0e-4
            and green["Theta_matter_current_L2"] > 1.0e-4
            and green["E_A_material_current_trace_L2"] > 1.0e-4
            and green["charge_3form_L2"] > 1.0e-4
            and green["exact_4form_L2"] > 1.0e-4
            and green["identity_L2_residual"] < 2.0e-10
            and green["identity_Linf_residual"] < 2.0e-9
            and green["omit_matter_from_Theta_mutant_L2"] > 1.0e-4
            and green["omit_material_J_from_E_A_mutant_L2"] > 1.0e-4
        ),
        "local_interface_gluing_closes_but_unglued_BFV_residual_is_explicit": (
            bfv["lambda_interface_L2"] > 1.0e-4
            and bfv["selected_local_trace_gluing_defect_L2"] < 1.0e-12
            and bfv["selected_glued_BFV_residual_L2"] < 1.0e-12
            and bfv["unglued_defect_L2"] > 1.0e-4
            and bfv["unglued_BFV_residual_L2"] > 1.0e-4
            and bfv["global_or_large_gauge_gluing_claimed"] is False
            and bfv["complete_BV_BFV_boundary_complex_claimed"] is False
        ),
        "restricted_translation_attempt_is_not_promoted_to_full_diffeomorphism": (
            translation["maximum_bulk_translation_action_difference"] < 1.0e-8
            and translation["full_diffeomorphism_khronon_Ward_completed"] is False
            and len(translation["missing_for_full_diffeomorphism_khronon_Ward"])
            >= 4
        ),
    }
    internal_keys = [
        key
        for key in checks
        if key
        != "restricted_translation_attempt_is_not_promoted_to_full_diffeomorphism"
    ]
    checks["all_internal_gauge_Ward_checks"] = all(checks[key] for key in internal_keys)
    checks["all_primary_scope_checks"] = all(checks.values())

    decision = {
        "bulk_full_v5_2_internal_SO3_Ward_pass": checks[
            "bulk_SO3_Ward_closes_off_shell_on_both_sides"
        ],
        "interface_full_v5_2_internal_SO3_Ward_selected_sector_pass": (
            checks["all_v5_2_interface_terms_and_source_groupoid_Ward_execute"]
            and checks["target_Q_frame_and_varphi_Robin_Ward_executes"]
        ),
        "boundary_Green_local_exact_identity_pass": checks[
            "boundary_Green_charge_exact_and_material_current_close"
        ],
        "internal_SO3_full_action_selected_trivial_sector_Ward_pass": checks[
            "all_internal_gauge_Ward_checks"
        ],
        "diffeomorphism_khronon_full_Ward_pass": False,
        "complete_BV_BFV_boundary_complex_pass": False,
        "unrestricted_large_gauge_sector_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "N4_JUNCTION_BENDING_pass": False,
        "P4_full_same_action_pass": False,
        "v5_6_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
        "publication_authorized": False,
        "status": (
            "FULL_5D_V5_2_INTERNAL_SO3_WARD_SELECTED_TRIVIAL_SECTOR_PRIMARY_PASS__"
            "DIFF_KHRONON_BV_BFV_C1_N1_N4_P4_V56_B4_B5_FAIL_CLOSED"
        ),
    }
    if checks["all_primary_scope_checks"] is not True:
        failed = [key for key, value in checks.items() if not value]
        raise FullActionWardV553Error(f"primary v5.5.3 checks failed: {failed}")
    if decision["internal_SO3_full_action_selected_trivial_sector_Ward_pass"] is not True:
        raise FullActionWardV553Error("internal full-action Ward flag did not close")
    if any(decision[key] is not False for key in FAIL_CLOSED_KEYS):
        raise FullActionWardV553Error("a downstream decision was promoted")

    return {
        "schema": SCHEMA,
        "title": "One-Omega topological SO(3) full-action gauge-Noether v5.5.3 gate",
        "classification": (
            "theory_only;full_5D_internal_gauge_Ward;selected_trivial_null_homotopic_sector;"
            "primary_not_independently_audited"
        ),
        "evidence_boundary": (
            "This gate independently executes the internal SO(3) Ward identity of the full "
            "five-dimensional v5.2 bulk action, its four-dimensional literal interface terms, "
            "and the local boundary Green exact form. The v5.5.1 two-dimensional receipt is "
            "preliminary and is neither consumed nor promoted. Arbitrary diffeomorphism/khronon "
            "Ward, large gauges, global gluing, BV-BFV, C1, N1, N4, P4, v5.6, B4 and B5 remain open."
        ),
        "pinned_v5_2": {
            "path": str(V5_2.relative_to(REPO)),
            "sha256": EXPECTED_V5_2_SHA256,
            "schema": EXPECTED_V5_2_SCHEMA,
            "literal_actions": EXPECTED_ACTIONS,
            "coefficients": EXPECTED_COEFFICIENTS,
        },
        "pinned_v5_5_2_ADM_controls": _v5_5_2_control_receipt(),
        "v5_5_1_preliminary_receipt": {
            "consumed": False,
            "promotable_by_this_gate": False,
            "reason": "the prior receipt is dimensionally reduced and cannot source this 5D result",
        },
        "equation_ledger": {
            "bulk_action": EXPECTED_ACTIONS["bulk_gauged"],
            "BF_action": EXPECTED_ACTIONS["BF"],
            "Euler_degrees": "E_B=F is a 2-form; E_A=D_A B+J_A is a 4-form; E_phi is a 0-form",
            "matter": (
                "P_M=D_M phi+c_M phi, c_M=3 partial_M log(Omega)/2; "
                "E_phi=Z[D_M P^M-c_M P^M]-Z M^2 Omega^(-7/2)V4'(s)phi/|phi|"
            ),
            "Ward_5form": "W=D_A E_A+B cross-wedge E_B+sqrt(-g) phi cross E_phi d5x=0",
            "curvature_on_B": "D_A^2 B=[F,B]=F cross-wedge B=-B cross-wedge F",
            "Bianchi": "D_A F=0 as a five-dimensional adjoint-valued 3-form",
            "material_reduction": "D_A J_A+sqrt(-g) phi cross E_phi d5x=0 componentwise",
            "boundary_Green": "Theta_gauge-<lambda,E_A>=-d_boundary<B lambda>",
            "source_groupoid": (
                "delta A=-D lambda, delta phi=lambda cross phi, delta B=lambda cross B, "
                "delta R=-R hat(lambda); varphi=R phi, A_Sigma=R A R^-1-dR R^-1, b=R B"
            ),
        },
        "certificate": certificate,
        "checks": checks,
        "decision": decision,
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST),
            },
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    payload = build_payload()
    _write(OUTPUT, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
