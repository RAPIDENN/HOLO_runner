#!/usr/bin/env python3
"""Independent full-5D matrix/form red-team for the v5.5.3 gauge gate.

This module does not import numerical or algebraic helpers from the primary.
It evaluates the literal v5.2 action on two five-dimensional half-space cells,
uses genuine 1/2/3/4/5-form incidence, and derives the internal SO(3) Euler
operators before testing their off-shell Ward identity.  The four-dimensional
Robin solder/frame cancellation is differentiated from its action.  This is
not a diffeomorphism--khronon Ward proof and cannot promote C1 or N1.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
from itertools import combinations
import json
import math
import platform
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate.json"
)
TEST = (
    HERE
    / "test_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate.py"
)
PRIMARY_GENERATOR = (
    HERE / "derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.py"
)
PRIMARY_TEST = (
    HERE / "test_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.py"
)
PRIMARY_ARTIFACT = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.json"
)
V5_2_ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
ADM_GENERATOR = HERE / "derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py"
ADM_TEST = HERE / "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py"
ADM_ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.json"
ADM_REDTEAM_GENERATOR = HERE / "derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.py"
ADM_REDTEAM_TEST = HERE / "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.py"
ADM_REDTEAM_ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.json"

EXPECTED_PRIMARY_GENERATOR_SHA256 = "3d9a57482d3a80832427d4d3e9e645e09d78166c3070de49de9f9cb89cbfd692"
EXPECTED_PRIMARY_TEST_SHA256 = "9d88139a02ca6c708a921a51e27287480db65c81e0c6b008d5717f3775c99e34"
EXPECTED_PRIMARY_ARTIFACT_SHA256 = "0bae4d93de669a95becb3742e4e2f8ad2f99517e9b6efa7a7cfc518b9c6d832d"
EXPECTED_V5_2_SHA256 = "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b"
EXPECTED_ADM_GENERATOR_SHA256 = "00f8fa443bda37711d2456cb5e55c8a5c349d1c7f814a44c63203e3c02836e1e"
EXPECTED_ADM_TEST_SHA256 = "4547d1e7f361b2c9b931dba3a9a5a5829d2a2563ab4a0c9c54a154f9292f7aca"
EXPECTED_ADM_ARTIFACT_SHA256 = "4e068475ae316684cebd0f68e10d183fff7c0d90c46b155f2dfc8be4b3b0d6e8"
EXPECTED_ADM_REDTEAM_GENERATOR_SHA256 = "470d3c8b2bc7429ad77083c39f9112cc1908501b176d72f3b464b2f37f62696d"
EXPECTED_ADM_REDTEAM_TEST_SHA256 = "6b373b7cccac70316ca52172fe65cfad991f90d0ad160afa4cdb2994e67e6f4f"
EXPECTED_ADM_REDTEAM_ARTIFACT_SHA256 = "4c94c2abeb24fb3444be4f79c93aa383659feac9e706eea7fe4fe2aac85bc7f6"

EXPECTED_PRIMARY_SCHEMA = "holo.one-omega-topological-so3-full-action-gauge-noether-v5-5-3-gate.v1"
EXPECTED_V5_2_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
EXPECTED_ADM_SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-gate.v1"
EXPECTED_ADM_REDTEAM_SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-redteam.v1"
SCHEMA = "holo.one-omega-topological-so3-full-action-gauge-noether-v5-5-3-redteam-gate.v1"

DIM = 5
DERIVATIVE_STEP = 5.0e-4
ACTION_STEP = 2.0e-6
ARBITRARY_VARIATION_SCALE = 2.0
FORM_INDICES = {degree: tuple(combinations(range(DIM), degree)) for degree in range(DIM + 1)}
FORM_POSITIONS = {
    degree: {indices: position for position, indices in enumerate(rows)}
    for degree, rows in FORM_INDICES.items()
}
FULL_INDEX = tuple(range(DIM))

ALLOWED_TRUE_PASS_KEYS = {
    "primary_v5_5_3_hash_and_convention_bound_pass",
    "ADM_v5_5_2_control_hash_bound_pass",
    "full_5D_internal_SO3_gauge_Noether_independent_pass",
}
FAIL_CLOSED_KEYS = (
    "full_diffeomorphism_khronon_Ward_pass",
    "complete_all_field_Euler_variation_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "regulated_interface_charge_completion_pass",
    "complete_v5_2_all_field_normal_embedding_pass",
    "full_off_shell_Green_theorem_accepted",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "N4_JUNCTION_BENDING_pass",
    "P4_full_same_action_pass",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
)


class FullActionGaugeV553RedteamError(ValueError):
    """A frozen input or independent full-dimensional oracle failed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise FullActionGaugeV553RedteamError(f"cannot hash {path}: {exc}") from exc


def _read_json(
    path: Path,
    expected_hash: str,
    expected_schema: str,
    *,
    require_canonical: bool = True,
) -> dict[str, Any]:
    if _sha256(path) != expected_hash:
        raise FullActionGaugeV553RedteamError(f"byte hash mismatch for {path.name}")
    try:
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FullActionGaugeV553RedteamError(f"cannot read {path}: {exc}") from exc
    canonical = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    if type(payload) is not dict or payload.get("schema") != expected_schema:
        raise FullActionGaugeV553RedteamError(f"schema mismatch for {path.name}")
    if require_canonical and raw != canonical:
        raise FullActionGaugeV553RedteamError(f"noncanonical artifact: {path.name}")
    return payload


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


V5_2 = _read_json(V5_2_ARTIFACT, EXPECTED_V5_2_SHA256, EXPECTED_V5_2_SCHEMA)
ADM = _read_json(
    ADM_ARTIFACT,
    EXPECTED_ADM_ARTIFACT_SHA256,
    EXPECTED_ADM_SCHEMA,
    require_canonical=False,
)
ADM_REDTEAM = _read_json(
    ADM_REDTEAM_ARTIFACT,
    EXPECTED_ADM_REDTEAM_ARTIFACT_SHA256,
    EXPECTED_ADM_REDTEAM_SCHEMA,
    require_canonical=False,
)
PARAMETERS = V5_2["exact_classical_charter"]["coefficient_policy"]["parameters"]
M5_CUBED = float(PARAMETERS["M5_cubed"])
G_COMP = float(PARAMETERS["compensator_metric_G"])
K_INFINITY = float(PARAMETERS["k_infinity"])
Z5 = float(PARAMETERS["material_Z5_per_side"])
MATERIAL_M = float(PARAMETERS["material_mass_M"])
MB2 = float(PARAMETERS["brane_Mb_squared"])
LAMBDA_K = float(PARAMETERS["lambda_K"])
XI = float(PARAMETERS["xi"])
ETA = float(PARAMETERS["eta"])
B4_BAR = float(PARAMETERS["B4_bar"])
BETA = float(PARAMETERS["brane_beta"])
KAPPA = float(PARAMETERS["Robin_kappa_hat"])
ROBIN_Y = float(PARAMETERS["Robin_y"])


def _load_primary() -> dict[str, Any]:
    return _read_json(PRIMARY_ARTIFACT, EXPECTED_PRIMARY_ARTIFACT_SHA256, EXPECTED_PRIMARY_SCHEMA)


def _hat(vector: np.ndarray) -> np.ndarray:
    value = np.asarray(vector)
    result = np.zeros(value.shape[:-1] + (3, 3), dtype=np.result_type(value, float))
    result[..., 0, 1] = -value[..., 2]
    result[..., 0, 2] = value[..., 1]
    result[..., 1, 0] = value[..., 2]
    result[..., 1, 2] = -value[..., 0]
    result[..., 2, 0] = -value[..., 1]
    result[..., 2, 1] = value[..., 0]
    return result


def _generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return tuple(_hat(np.eye(3)[index]) for index in range(3))  # type: ignore[return-value]


def _inner(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return -0.5 * np.trace(left @ right, axis1=-2, axis2=-1)


def _mu(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """hat(left x right), expressed without a cross-product helper."""

    return right[..., :, None] * left[..., None, :] - left[..., :, None] * right[..., None, :]


def _broadcast_coordinates(coordinates: tuple[np.ndarray, ...]) -> tuple[np.ndarray, ...]:
    if len(coordinates) != DIM:
        raise FullActionGaugeV553RedteamError("the bulk oracle requires exactly five coordinates")
    return tuple(np.broadcast_arrays(*coordinates))


def _partial(
    function: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
    axis: int,
) -> np.ndarray:
    h = DERIVATIVE_STEP
    values = []
    for shift in (-2.0, -1.0, 1.0, 2.0):
        moved = list(coordinates)
        moved[axis] = moved[axis] + shift * h
        values.append(function(tuple(moved)))
    return (values[0] - 8.0 * values[1] + 8.0 * values[2] - values[3]) / (12.0 * h)


def _wedge_sign(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    inversions = sum(1 for i in left for j in right if i > j)
    return -1 if inversions % 2 else 1


def _wedge_matrix(left: np.ndarray, p: int, right: np.ndarray, q: int) -> np.ndarray:
    shape = np.broadcast_shapes(left.shape[:-3], right.shape[:-3])
    result = np.zeros(shape + (len(FORM_INDICES[p + q]), 3, 3), dtype=float)
    for left_position, left_index in enumerate(FORM_INDICES[p]):
        for right_position, right_index in enumerate(FORM_INDICES[q]):
            if set(left_index).intersection(right_index):
                continue
            total_index = tuple(sorted(left_index + right_index))
            position = FORM_POSITIONS[p + q][total_index]
            result[..., position, :, :] += (
                _wedge_sign(left_index, right_index)
                * left[..., left_position, :, :]
                @ right[..., right_position, :, :]
            )
    return result


def _wedge_pair(left: np.ndarray, p: int, right: np.ndarray, q: int) -> np.ndarray:
    if p + q != DIM:
        raise FullActionGaugeV553RedteamError("paired wedge must be a five-form")
    result = np.zeros(np.broadcast_shapes(left.shape[:-3], right.shape[:-3]), dtype=float)
    for left_position, left_index in enumerate(FORM_INDICES[p]):
        right_index = tuple(index for index in FULL_INDEX if index not in left_index)
        right_position = FORM_POSITIONS[q][right_index]
        result += _wedge_sign(left_index, right_index) * _inner(
            left[..., left_position, :, :], right[..., right_position, :, :]
        )
    return result


def _exterior_derivative(
    function: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    degree: int,
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    shape = function(coordinates).shape[:-3]
    result = np.zeros(shape + (len(FORM_INDICES[degree + 1]), 3, 3), dtype=float)
    for output_position, output_index in enumerate(FORM_INDICES[degree + 1]):
        for slot, derivative_axis in enumerate(output_index):
            source_index = output_index[:slot] + output_index[slot + 1 :]
            source_position = FORM_POSITIONS[degree][source_index]
            result[..., output_position, :, :] += (-1.0) ** slot * _partial(
                lambda moved, source_position=source_position: function(moved)[
                    ..., source_position, :, :
                ],
                coordinates,
                derivative_axis,
            )
    return result


def _covariant_form_derivative(
    function: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    degree: int,
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    value = function(coordinates)
    a_value = connection(coordinates)
    return (
        _exterior_derivative(function, degree, coordinates)
        + _wedge_matrix(a_value, 1, value, degree)
        - (-1.0) ** degree * _wedge_matrix(value, degree, a_value, 1)
    )


def _form_bracket(left: np.ndarray, p: int, right: np.ndarray, q: int) -> np.ndarray:
    return _wedge_matrix(left, p, right, q) - (-1.0) ** (p * q) * _wedge_matrix(
        right, q, left, p
    )


def _form_l2(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.sum(np.asarray(value) ** 2, axis=(-3, -2, -1)) / 2.0)))


def _vector_l2(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.sum(np.asarray(value) ** 2, axis=-1))))


def _phase(coordinates: tuple[np.ndarray, ...], seed: int) -> np.ndarray:
    # ``seed`` selects phases and a small bounded frequency family; it must not
    # scale the frequency without bound.  The former seed*axis rule produced
    # frequencies near 30 radians per cell in the variation probes, so the
    # nominal Gauss 2/3/4 sequence was not in its asymptotic regime.  These
    # modes remain genuinely dependent on every one of the five coordinates,
    # while all products entering the action are resolved by that frozen
    # quadrature ladder.
    offset = 0.173 * seed
    return offset + sum(
        (
            0.31
            + 0.07 * (axis + 1)
            + 0.009 * ((seed + axis) % 5)
        )
        * coordinate
        for axis, coordinate in enumerate(coordinates)
    )


def _connection(side: int, coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    coordinates = _broadcast_coordinates(coordinates)
    shape = coordinates[0].shape
    result = np.zeros(shape + (DIM, 3, 3), dtype=float)
    normal = coordinates[4]
    for index in range(DIM):
        components = []
        for internal in range(3):
            seed = 3 * index + internal
            components.append(
                0.035 * (index + 1) * (internal - 1)
                + 0.075 * np.sin(_phase(coordinates, seed) + 0.2 * internal)
                + 0.042 * np.cos(_phase(coordinates, seed + 2) - 0.17 * index)
                + side * normal * 0.018 * np.sin(_phase(coordinates, seed + 5))
            )
        result[..., index, :, :] = _hat(np.stack(components, axis=-1))
    return result


def _b_field(side: int, coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    coordinates = _broadcast_coordinates(coordinates)
    shape = coordinates[0].shape
    result = np.zeros(shape + (len(FORM_INDICES[3]), 3, 3), dtype=float)
    normal = coordinates[4]
    for position, indices in enumerate(FORM_INDICES[3]):
        components = []
        for internal in range(3):
            seed = 7 + 3 * position + internal
            components.append(
                0.055 * (internal + 1)
                + 0.065 * np.sin(_phase(coordinates, seed) + 0.11 * sum(indices))
                + 0.031 * np.cos(_phase(coordinates, seed + 4))
                + side * (0.012 * (position + 1) + normal * 0.014)
            )
        result[..., position, :, :] = _hat(np.stack(components, axis=-1))
    return result


def _phi_field(side: int, coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    coordinates = _broadcast_coordinates(coordinates)
    normal = coordinates[4]
    return np.stack(
        [
            0.31
            - 0.12 * internal
            + 0.085 * np.sin(_phase(coordinates, 21 + internal))
            + 0.047 * np.cos(_phase(coordinates, 26 + internal))
            + side * normal * 0.022 * np.sin(_phase(coordinates, 31 + internal))
            for internal in range(3)
        ],
        axis=-1,
    )


def _omega_field(side: int, coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    coordinates = _broadcast_coordinates(coordinates)
    normal = coordinates[4]
    return (
        1.24
        + 0.055 * np.sin(_phase(coordinates, 2))
        + 0.038 * np.cos(_phase(coordinates, 5))
        + side * normal * 0.018 * np.sin(_phase(coordinates, 9))
    )


def _sigma_field(side: int, coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    coordinates = _broadcast_coordinates(coordinates)
    normal = coordinates[4]
    tangential = coordinates[:4] + (np.zeros_like(normal),)
    return (
        0.075 * np.sin(_phase(tangential, 1))
        + 0.042 * np.cos(_phase(tangential, 4))
        + normal * (0.055 + side * 0.021 * np.sin(_phase(tangential, 7)))
        + 0.014 * normal**2
    )


def _base_connection(side: int) -> Callable[[tuple[np.ndarray, ...]], np.ndarray]:
    return lambda coordinates: _connection(side, coordinates)


def _base_b(side: int) -> Callable[[tuple[np.ndarray, ...]], np.ndarray]:
    return lambda coordinates: _b_field(side, coordinates)


def _base_phi(side: int) -> Callable[[tuple[np.ndarray, ...]], np.ndarray]:
    return lambda coordinates: _phi_field(side, coordinates)


def _metric_data(side: int, coordinates: tuple[np.ndarray, ...]) -> tuple[np.ndarray, np.ndarray]:
    sigma = _sigma_field(side, coordinates)
    signs = np.asarray([-1.0, 1.0, 1.0, 1.0, 1.0])
    inverse_diagonal = np.exp(-2.0 * sigma)[..., None] * signs
    volume = np.exp(5.0 * sigma)
    return volume, inverse_diagonal


def _c_form(side: int, coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    omega_function = lambda moved: np.log(_omega_field(side, moved))
    return np.stack(
        [1.5 * _partial(omega_function, coordinates, axis) for axis in range(DIM)],
        axis=-1,
    )


def _v4(value: np.ndarray) -> np.ndarray:
    return value**4 / (2.0 * np.sqrt(1.0 + value**4))


def _v4_prime(value: np.ndarray) -> np.ndarray:
    return value**3 * (2.0 + value**4) / (1.0 + value**4) ** 1.5


def _curvature(
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    value = connection(coordinates)
    return _exterior_derivative(connection, 1, coordinates) + _wedge_matrix(
        value, 1, value, 1
    )


def _covariant_vector_component(
    vector: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
    axis: int,
) -> np.ndarray:
    return _partial(vector, coordinates, axis) + np.einsum(
        "...ij,...j->...i",
        connection(coordinates)[..., axis, :, :],
        vector(coordinates),
    )


def _p_lower(
    side: int,
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    phi: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    phi_value = phi(coordinates)
    c_value = _c_form(side, coordinates)
    return np.stack(
        [
            _covariant_vector_component(phi, connection, coordinates, axis)
            + c_value[..., axis, None] * phi_value
            for axis in range(DIM)
        ],
        axis=-2,
    )


def _p_upper(
    side: int,
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    phi: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    _, inverse_diagonal = _metric_data(side, coordinates)
    return inverse_diagonal[..., :, None] * _p_lower(side, connection, phi, coordinates)


def _matter_current_four_form(
    side: int,
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    phi: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    volume, _ = _metric_data(side, coordinates)
    phi_value = phi(coordinates)
    p_upper = _p_upper(side, connection, phi, coordinates)
    shape = phi_value.shape[:-1]
    result = np.zeros(shape + (len(FORM_INDICES[4]), 3, 3), dtype=float)
    for axis in range(DIM):
        complement = tuple(index for index in range(DIM) if index != axis)
        position = FORM_POSITIONS[4][complement]
        result[..., position, :, :] = (
            (-1.0) ** axis
            * volume[..., None, None]
            * Z5
            * _mu(p_upper[..., axis, :], phi_value)
        )
    return result


def _radial_potential_euler(
    side: int,
    phi_value: np.ndarray,
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    omega = _omega_field(side, coordinates)
    rho = np.linalg.norm(phi_value, axis=-1)
    argument = omega**1.5 * rho
    coefficient = np.divide(
        -Z5 * MATERIAL_M**2 * omega**-3.5 * _v4_prime(argument),
        rho,
        out=np.zeros_like(rho),
        where=rho > 0.0,
    )
    return coefficient[..., None] * phi_value


def _matter_euler_phi(
    side: int,
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    phi: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    volume, inverse_diagonal = _metric_data(side, coordinates)
    p_lower = _p_lower(side, connection, phi, coordinates)
    p_upper = inverse_diagonal[..., :, None] * p_lower
    c_value = _c_form(side, coordinates)
    divergence_density = np.zeros_like(phi(coordinates))

    for axis in range(DIM):
        def density_vector(
            moved: tuple[np.ndarray, ...],
            axis: int = axis,
        ) -> np.ndarray:
            moved_volume, moved_inverse = _metric_data(side, moved)
            moved_p = _p_lower(side, connection, phi, moved)
            return moved_volume[..., None] * moved_inverse[..., axis, None] * moved_p[..., axis, :]

        density_value = density_vector(coordinates)
        divergence_density += _partial(density_vector, coordinates, axis) + np.einsum(
            "...ij,...j->...i",
            connection(coordinates)[..., axis, :, :],
            density_value,
        )

    kinetic = Z5 * (
        divergence_density / volume[..., None]
        - np.sum(c_value[..., :, None] * p_upper, axis=-2)
    )
    potential = _radial_potential_euler(side, phi(coordinates), coordinates)
    return kinetic + potential, kinetic, potential


def _euler_A(
    side: int,
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    b_field: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    phi: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    db = _covariant_form_derivative(b_field, 3, connection, coordinates)
    current = _matter_current_four_form(side, connection, phi, coordinates)
    return db + current, db, current


def _full_euler_certificate_at(
    side: int,
    coordinates: tuple[np.ndarray, ...],
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray] | None = None,
    b_field: Callable[[tuple[np.ndarray, ...]], np.ndarray] | None = None,
    phi: Callable[[tuple[np.ndarray, ...]], np.ndarray] | None = None,
) -> dict[str, np.ndarray]:
    connection = _base_connection(side) if connection is None else connection
    b_field = _base_b(side) if b_field is None else b_field
    phi = _base_phi(side) if phi is None else phi
    curvature = _curvature(connection, coordinates)
    e_a, db, current = _euler_A(side, connection, b_field, phi, coordinates)
    e_phi, e_phi_kinetic, e_phi_potential = _matter_euler_phi(
        side, connection, phi, coordinates
    )
    volume, _ = _metric_data(side, coordinates)
    return {
        "E_A": e_a,
        "D_A_B": db,
        "matter_current_four_form": current,
        "E_B": curvature,
        "E_phi": e_phi,
        "E_phi_top": volume[..., None] * e_phi,
        "E_phi_kinetic": e_phi_kinetic,
        "E_phi_potential": e_phi_potential,
        "P_lower": _p_lower(side, connection, phi, coordinates),
        "P_upper": _p_upper(side, connection, phi, coordinates),
    }


def _full_W(
    side: int,
    coordinates: tuple[np.ndarray, ...],
) -> dict[str, np.ndarray]:
    connection = _base_connection(side)
    b_field = _base_b(side)
    phi = _base_phi(side)

    def e_a_function(moved: tuple[np.ndarray, ...]) -> np.ndarray:
        return _euler_A(side, connection, b_field, phi, moved)[0]

    euler = _full_euler_certificate_at(side, coordinates)
    d_e_a = _covariant_form_derivative(e_a_function, 4, connection, coordinates)
    b_bracket_f = _form_bracket(
        b_field(coordinates), 3, euler["E_B"], 2
    )
    matter_moment = _mu(phi(coordinates), euler["E_phi_top"])[..., None, :, :]
    return {
        **euler,
        "D_A_E_A": d_e_a,
        "B_bracket_E_B": b_bracket_f,
        "mu_phi_E_phi": matter_moment,
        "W": d_e_a + b_bracket_f + matter_moment,
    }


def _charged_bulk_density(
    side: int,
    coordinates: tuple[np.ndarray, ...],
    connection: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    b_field: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    phi: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    potential_metric: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    curvature = _curvature(connection, coordinates)
    bf_density = _wedge_pair(b_field(coordinates), 3, curvature, 2)
    volume, inverse_diagonal = _metric_data(side, coordinates)
    p_lower = _p_lower(side, connection, phi, coordinates)
    kinetic_contraction = np.sum(
        inverse_diagonal[..., :, None] * p_lower**2, axis=(-2, -1)
    )
    phi_value = phi(coordinates)
    if potential_metric is None:
        rho = np.linalg.norm(phi_value, axis=-1)
    else:
        rho = np.sqrt(
            np.einsum("...i,ij,...j->...", phi_value, potential_metric, phi_value)
        )
    omega = _omega_field(side, coordinates)
    matter_density = volume * (
        -0.5 * Z5 * kinetic_contraction
        - Z5 * MATERIAL_M**2 * omega**-5.0 * _v4(omega**1.5 * rho)
    )
    return bf_density + matter_density, bf_density, matter_density


def _superpotential(omega: np.ndarray) -> np.ndarray:
    return 3.0 * M5_CUBED * K_INFINITY * np.exp(
        -G_COMP * omega**2 / (6.0 * M5_CUBED)
    )


def _bulk_potential(omega: np.ndarray) -> np.ndarray:
    superpotential = _superpotential(omega)
    derivative = -G_COMP * omega * superpotential / (3.0 * M5_CUBED)
    return derivative**2 / (2.0 * G_COMP) - 2.0 * superpotential**2 / (3.0 * M5_CUBED)


def _conformal_ricci_scalar(side: int, coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    sigma_function = lambda moved: _sigma_field(side, moved)
    signs = np.asarray([-1.0, 1.0, 1.0, 1.0, 1.0])
    first = [_partial(sigma_function, coordinates, axis) for axis in range(DIM)]
    second = [
        _partial(
            lambda moved, axis=axis: _partial(sigma_function, moved, axis),
            coordinates,
            axis,
        )
        for axis in range(DIM)
    ]
    box_sigma = sum(signs[axis] * second[axis] for axis in range(DIM))
    gradient_square = sum(signs[axis] * first[axis] ** 2 for axis in range(DIM))
    sigma = sigma_function(coordinates)
    return np.exp(-2.0 * sigma) * (-8.0 * box_sigma - 12.0 * gradient_square)


def _neutral_bulk_density(
    side: int,
    coordinates: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    volume, inverse_diagonal = _metric_data(side, coordinates)
    omega = _omega_field(side, coordinates)
    omega_derivatives = np.stack(
        [
            _partial(lambda moved: _omega_field(side, moved), coordinates, axis)
            for axis in range(DIM)
        ],
        axis=-1,
    )
    omega_kinetic = np.sum(inverse_diagonal * omega_derivatives**2, axis=-1)
    eh = volume * M5_CUBED * _conformal_ricci_scalar(side, coordinates) / 2.0
    scalar = volume * (-0.5 * G_COMP * omega_kinetic - _bulk_potential(omega))
    return eh + scalar, eh, scalar


def _gauss_grid(
    dimensions: int,
    count: int,
    bounds: tuple[tuple[float, float], ...] | None = None,
) -> tuple[tuple[np.ndarray, ...], np.ndarray]:
    bounds = tuple((0.0, 1.0) for _ in range(dimensions)) if bounds is None else bounds
    base_nodes, base_weights = np.polynomial.legendre.leggauss(count)
    nodes = []
    weights = []
    for left, right in bounds:
        nodes.append(0.5 * (right - left) * base_nodes + 0.5 * (left + right))
        weights.append(0.5 * (right - left) * base_weights)
    coordinate_mesh = tuple(np.meshgrid(*nodes, indexing="ij"))
    weight_mesh = np.meshgrid(*weights, indexing="ij")
    total_weight = np.ones_like(weight_mesh[0])
    for value in weight_mesh:
        total_weight *= value
    return coordinate_mesh, total_weight


def _integrate(
    function: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    dimensions: int,
    count: int,
    bounds: tuple[tuple[float, float], ...] | None = None,
) -> float:
    coordinates, weights = _gauss_grid(dimensions, count, bounds)
    return float(np.sum(weights * function(coordinates)))


def _interface_coordinates(
    tangential: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, ...]:
    if len(tangential) != 4:
        raise FullActionGaugeV553RedteamError("Sigma requires four coordinates")
    tangential = tuple(np.broadcast_arrays(*tangential))
    return tangential + (np.zeros_like(tangential[0]),)


def _interface_sigma(tangential: tuple[np.ndarray, ...]) -> np.ndarray:
    return _sigma_field(1, _interface_coordinates(tangential))


def _interface_frame(tangential: tuple[np.ndarray, ...]) -> np.ndarray:
    sigma = _interface_sigma(tangential)
    identity = np.eye(3)
    return np.exp(-sigma)[..., None, None] * identity


def _interface_acceleration(tangential: tuple[np.ndarray, ...]) -> np.ndarray:
    bulk_coordinates = _interface_coordinates(tangential)
    sigma = _interface_sigma(tangential)
    derivatives = np.stack(
        [
            _partial(lambda moved: _sigma_field(1, moved), bulk_coordinates, axis)
            for axis in (1, 2, 3)
        ],
        axis=-1,
    )
    return np.exp(-2.0 * sigma)[..., None] * derivatives


def _interface_phi_internal(tangential: tuple[np.ndarray, ...]) -> np.ndarray:
    return _phi_field(1, _interface_coordinates(tangential))


def _robin_density_from(
    tangential: tuple[np.ndarray, ...],
    phi_internal: np.ndarray,
    frame: np.ndarray,
) -> np.ndarray:
    sigma = _interface_sigma(tangential)
    varphi_h = np.einsum("...ia,...a->...i", frame, phi_internal)
    residual = varphi_h - ROBIN_Y * _interface_acceleration(tangential)
    spatial_metric_factor = np.exp(2.0 * sigma)
    volume = np.exp(4.0 * sigma)
    return -0.5 * KAPPA * volume * spatial_metric_factor * np.sum(
        residual**2, axis=-1
    )


def _robin_density(tangential: tuple[np.ndarray, ...]) -> np.ndarray:
    return _robin_density_from(
        tangential,
        _interface_phi_internal(tangential),
        _interface_frame(tangential),
    )


def _interface_neutral_densities(
    tangential: tuple[np.ndarray, ...],
) -> dict[str, np.ndarray]:
    coordinates = _interface_coordinates(tangential)
    sigma = _interface_sigma(tangential)
    volume = np.exp(4.0 * sigma)
    omega = _omega_field(1, coordinates)
    ghy = np.zeros_like(sigma)
    for side in (-1, 1):
        normal_sigma = _partial(lambda moved, side=side: _sigma_field(side, moved), coordinates, 4)
        theta = -4.0 * np.exp(-sigma) * normal_sigma
        ghy += M5_CUBED * volume * theta
    wall = -volume * (
        2.0 * _superpotential(omega) + 0.5 * BETA * (omega - 1.0) ** 2
    )
    sigma_time = _partial(lambda moved: _sigma_field(1, moved), coordinates, 0)
    spatial_first = [
        _partial(lambda moved: _sigma_field(1, moved), coordinates, axis)
        for axis in (1, 2, 3)
    ]
    spatial_second = [
        _partial(
            lambda moved, axis=axis: _partial(
                lambda nested: _sigma_field(1, nested), moved, axis
            ),
            coordinates,
            axis,
        )
        for axis in (1, 2, 3)
    ]
    k_square = 9.0 * np.exp(-2.0 * sigma) * sigma_time**2
    kij_square = 3.0 * np.exp(-2.0 * sigma) * sigma_time**2
    a_square = np.exp(-2.0 * sigma) * sum(value**2 for value in spatial_first)
    r_three = np.exp(-2.0 * sigma) * (
        -4.0 * sum(spatial_second) - 2.0 * sum(value**2 for value in spatial_first)
    )
    foliation = 0.5 * MB2 * volume * (
        kij_square
        - LAMBDA_K * k_square
        + XI * r_three
        + ETA * a_square
        - B4_BAR * r_three**2 / (16.0 * K_INFINITY**2)
    )
    return {
        "GHY": ghy,
        "wall_background": wall,
        "foliation_lower": foliation,
        "Robin_intrinsic": _robin_density(tangential),
    }


def _bulk_action_parts(
    states: Mapping[int, tuple[
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
    ]] | None = None,
    *,
    count: int = 5,
    potential_metric: np.ndarray | None = None,
) -> dict[str, float]:
    totals = {"BF": 0.0, "matter": 0.0, "EH": 0.0, "Omega_and_U": 0.0}
    coordinates, weights = _gauss_grid(DIM, count)
    for side in (-1, 1):
        connection, b_field, phi = (
            (_base_connection(side), _base_b(side), _base_phi(side))
            if states is None
            else states[side]
        )

        _, bf_density, matter_density = _charged_bulk_density(
            side,
            coordinates,
            connection,
            b_field,
            phi,
            potential_metric,
        )
        _, eh_density, scalar_density = _neutral_bulk_density(side, coordinates)
        # The pieces share one five-dimensional grid evaluation, but remain
        # independently integrated so an omitted sector cannot hide in a sum.
        totals["BF"] += float(np.sum(weights * bf_density))
        totals["matter"] += float(np.sum(weights * matter_density))
        totals["EH"] += float(np.sum(weights * eh_density))
        totals["Omega_and_U"] += float(np.sum(weights * scalar_density))
    return totals


def _charged_action_parts(
    states: Mapping[int, tuple[
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
    ]] | None = None,
    *,
    count: int,
    potential_metric: np.ndarray | None = None,
) -> dict[str, float]:
    """Evaluate only the internally charged pieces on one shared 5D grid."""

    coordinates, weights = _gauss_grid(DIM, count)
    totals = {"BF": 0.0, "matter": 0.0}
    for side in (-1, 1):
        connection, b_field, phi = (
            (_base_connection(side), _base_b(side), _base_phi(side))
            if states is None
            else states[side]
        )
        _, bf_density, matter_density = _charged_bulk_density(
            side,
            coordinates,
            connection,
            b_field,
            phi,
            potential_metric,
        )
        totals["BF"] += float(np.sum(weights * bf_density))
        totals["matter"] += float(np.sum(weights * matter_density))
    return totals


def _interface_action_parts(count: int = 6) -> dict[str, float]:
    coordinates, weights = _gauss_grid(4, count)
    densities = _interface_neutral_densities(coordinates)
    return {
        name: float(np.sum(weights * value)) for name, value in densities.items()
    }


def _full_action_value(
    states: Mapping[int, tuple[
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
        Callable[[tuple[np.ndarray, ...]], np.ndarray],
    ]] | None = None,
    *,
    count: int = 5,
    potential_metric: np.ndarray | None = None,
) -> tuple[float, dict[str, float]]:
    pieces = _bulk_action_parts(states, count=count, potential_metric=potential_metric)
    pieces.update(_interface_action_parts(max(5, count)))
    return float(sum(pieces.values())), pieces


def _variation_envelope(coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    result = np.ones_like(coordinates[0])
    for coordinate in coordinates:
        # A degree-two face-vanishing factor is enough to remove the Green
        # boundary term.  The previous degree-four factor unnecessarily
        # under-resolved a five-dimensional total derivative at low order.
        result *= 4.0 * coordinate * (1.0 - coordinate)
    return result


def _arbitrary_variation(
    side: int,
    coordinates: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    coordinates = _broadcast_coordinates(coordinates)
    # Explicitly amplify the off-shell probe, not the acceptance tolerance.
    # Multiplication by a constant preserves all ten zero boundary traces and
    # the same resolved Gauss convergence family.
    envelope = ARBITRARY_VARIATION_SCALE * _variation_envelope(coordinates)
    shape = envelope.shape
    delta_a = np.zeros(shape + (DIM, 3, 3), dtype=float)
    delta_b = np.zeros(shape + (len(FORM_INDICES[3]), 3, 3), dtype=float)
    for index in range(DIM):
        vector = np.stack(
            [
                envelope
                * (0.035 + 0.009 * internal)
                * np.sin(_phase(coordinates, 70 + 3 * index + internal))
                for internal in range(3)
            ],
            axis=-1,
        )
        delta_a[..., index, :, :] = _hat(vector)
    for position in range(len(FORM_INDICES[3])):
        vector = np.stack(
            [
                envelope
                * (0.028 + 0.006 * internal)
                * np.cos(_phase(coordinates, 110 + 3 * position + internal))
                for internal in range(3)
            ],
            axis=-1,
        )
        delta_b[..., position, :, :] = _hat(vector)
    delta_phi = np.stack(
        [
            envelope
            * (0.041 + 0.007 * internal)
            * np.cos(_phase(coordinates, 150 + internal) + 0.1 * side)
            for internal in range(3)
        ],
        axis=-1,
    )
    return delta_a, delta_b, delta_phi


def _arbitrarily_moved_states(
    epsilon: float,
) -> dict[int, tuple[
    Callable[[tuple[np.ndarray, ...]], np.ndarray],
    Callable[[tuple[np.ndarray, ...]], np.ndarray],
    Callable[[tuple[np.ndarray, ...]], np.ndarray],
]]:
    states = {}
    for side in (-1, 1):
        base_a, base_b, base_phi = _base_connection(side), _base_b(side), _base_phi(side)
        states[side] = (
            lambda coordinates, side=side, base_a=base_a: base_a(coordinates)
            + epsilon * _arbitrary_variation(side, coordinates)[0],
            lambda coordinates, side=side, base_b=base_b: base_b(coordinates)
            + epsilon * _arbitrary_variation(side, coordinates)[1],
            lambda coordinates, side=side, base_phi=base_phi: base_phi(coordinates)
            + epsilon * _arbitrary_variation(side, coordinates)[2],
        )
    return states


def _euler_pairing_arbitrary(count: int = 6) -> float:
    total = 0.0
    coordinates, weights = _gauss_grid(DIM, count)
    for side in (-1, 1):
        def density(coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
            euler = _full_euler_certificate_at(side, coordinates)
            delta_a, delta_b, delta_phi = _arbitrary_variation(side, coordinates)
            return (
                _wedge_pair(euler["E_A"], 4, delta_a, 1)
                + _wedge_pair(delta_b, 3, euler["E_B"], 2)
                + np.sum(euler["E_phi_top"] * delta_phi, axis=-1)
            )

        total += float(np.sum(weights * density(coordinates)))
    return total


def _action_euler_at_order(count: int) -> dict[str, float]:
    actions = []
    for sign in (1.0, -1.0):
        rows = _charged_action_parts(
            _arbitrarily_moved_states(sign * ACTION_STEP), count=count
        )
        actions.append(rows["BF"] + rows["matter"])
    direct = (actions[0] - actions[1]) / (2.0 * ACTION_STEP)
    euler = _euler_pairing_arbitrary(count)

    def wrong_pairing(coordinates: tuple[np.ndarray, ...], side: int) -> np.ndarray:
        euler_row = _full_euler_certificate_at(side, coordinates)
        delta_a, delta_b, delta_phi = _arbitrary_variation(side, coordinates)
        wrong_e_a = euler_row["D_A_B"] - euler_row["matter_current_four_form"]
        return (
            _wedge_pair(wrong_e_a, 4, delta_a, 1)
            + _wedge_pair(delta_b, 3, euler_row["E_B"], 2)
            + np.sum(euler_row["E_phi_top"] * delta_phi, axis=-1)
        )

    wrong = sum(
        _integrate(
            lambda coordinates, side=side: wrong_pairing(coordinates, side),
            DIM,
            count,
        )
        for side in (-1, 1)
    )
    return {
        "direct_full_action_derivative": direct,
        "charged_Euler_pairing": euler,
        "absolute_error": abs(direct - euler),
        "active_derivative_magnitude": abs(direct),
        "flip_matter_source_sign_witness": abs(direct - wrong),
    }


def _action_to_euler_certificate() -> dict[str, Any]:
    # Three actual tensor-product Gauss rules certify convergence.  Acceptance
    # uses the highest order and requires decreasing error; no tolerance is
    # relaxed to accommodate under-integration.
    convergence = {
        str(count): _action_euler_at_order(count) for count in (2, 3, 4)
    }
    selected = dict(convergence["4"])
    base_total, base_pieces = _full_action_value(count=4)
    selected.update(
        {
            "arbitrary_variation_scale": ARBITRARY_VARIATION_SCALE,
            "full_v5_2_action_value": base_total,
            "active_action_pieces": base_pieces,
            "neutral_piece_central_derivative_max": 0.0,
            "quadrature_convergence": convergence,
            "successive_absolute_errors": [
                convergence[str(count)]["absolute_error"] for count in (2, 3, 4)
            ],
            "tensor_product_node_counts": {
                str(count): count**DIM for count in (2, 3, 4)
            },
            "successive_error_ratios": [
                convergence["2"]["absolute_error"]
                / max(convergence["3"]["absolute_error"], 1.0e-30),
                convergence["3"]["absolute_error"]
                / max(convergence["4"]["absolute_error"], 1.0e-30),
            ],
        }
    )
    return selected


def _compact_factor(coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    result = np.ones_like(coordinates[0])
    for coordinate in coordinates:
        inside = (coordinate > 0.0) & (coordinate < 1.0)
        factor = np.zeros_like(coordinate)
        factor[inside] = 16.0 * coordinate[inside] ** 2 * (1.0 - coordinate[inside]) ** 2
        result *= factor
    return result


def _compact_lambda_vector(coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
    coordinates = _broadcast_coordinates(coordinates)
    factor = _compact_factor(coordinates)
    return np.stack(
        (
            factor * (0.22 + 0.035 * coordinates[0]),
            factor * (-0.17 + 0.031 * coordinates[2]),
            factor * (0.14 + 0.027 * coordinates[1] - 0.019 * coordinates[3]),
        ),
        axis=-1,
    )


def _lambda_form(
    vector_function: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    return _hat(vector_function(coordinates))[..., None, :, :]


def _gauge_direction(
    side: int,
    vector_function: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    coordinates: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    connection, b_field, phi = _base_connection(side), _base_b(side), _base_phi(side)
    lambda_function = lambda moved: _lambda_form(vector_function, moved)
    d_lambda = _covariant_form_derivative(lambda_function, 0, connection, coordinates)
    lambda_matrix = lambda_function(coordinates)[..., 0, :, :]
    b_value = b_field(coordinates)
    delta_b = (
        lambda_matrix[..., None, :, :] @ b_value
        - b_value @ lambda_matrix[..., None, :, :]
    )
    delta_phi = np.einsum("...ij,...j->...i", lambda_matrix, phi(coordinates))
    return -d_lambda, delta_b, delta_phi


def _gauge_moved_states(
    epsilon: float,
    vector_function: Callable[[tuple[np.ndarray, ...]], np.ndarray],
) -> dict[int, tuple[
    Callable[[tuple[np.ndarray, ...]], np.ndarray],
    Callable[[tuple[np.ndarray, ...]], np.ndarray],
    Callable[[tuple[np.ndarray, ...]], np.ndarray],
]]:
    states = {}
    for side in (-1, 1):
        base_a, base_b, base_phi = _base_connection(side), _base_b(side), _base_phi(side)
        states[side] = (
            lambda coordinates, side=side, base_a=base_a: base_a(coordinates)
            + epsilon * _gauge_direction(side, vector_function, coordinates)[0],
            lambda coordinates, side=side, base_b=base_b: base_b(coordinates)
            + epsilon * _gauge_direction(side, vector_function, coordinates)[1],
            lambda coordinates, side=side, base_phi=base_phi: base_phi(coordinates)
            + epsilon * _gauge_direction(side, vector_function, coordinates)[2],
        )
    return states


def _gauge_euler_pairing(
    vector_function: Callable[[tuple[np.ndarray, ...]], np.ndarray],
    count: int,
) -> float:
    total = 0.0
    coordinates, weights = _gauss_grid(DIM, count)
    for side in (-1, 1):
        def density(coordinates: tuple[np.ndarray, ...]) -> np.ndarray:
            euler = _full_euler_certificate_at(side, coordinates)
            delta_a, delta_b, delta_phi = _gauge_direction(side, vector_function, coordinates)
            return (
                _wedge_pair(euler["E_A"], 4, delta_a, 1)
                + _wedge_pair(delta_b, 3, euler["E_B"], 2)
                + np.sum(euler["E_phi_top"] * delta_phi, axis=-1)
            )

        total += float(np.sum(weights * density(coordinates)))
    return total


def _compact_lambda_certificate() -> dict[str, Any]:
    actions = []
    for sign in (1.0, -1.0):
        pieces = _charged_action_parts(
            _gauge_moved_states(sign * ACTION_STEP, _compact_lambda_vector),
            count=4,
        )
        actions.append(pieces["BF"] + pieces["matter"])
    direct = (actions[0] - actions[1]) / (2.0 * ACTION_STEP)
    euler = _gauge_euler_pairing(_compact_lambda_vector, 4)
    sample, _ = _gauss_grid(DIM, 3)
    lambda_value = _compact_lambda_vector(sample)
    boundary_samples = []
    line = np.linspace(0.0, 1.0, 5)
    base_mesh = np.meshgrid(line, line, line, line, indexing="ij")
    for axis in range(DIM):
        for face in (0.0, 1.0):
            values = list(base_mesh)
            values.insert(axis, np.full_like(base_mesh[0], face))
            boundary_samples.append(_compact_lambda_vector(tuple(values)))

    per_generator = {}
    for index in range(3):
        def one_generator(
            coordinates: tuple[np.ndarray, ...],
            index: int = index,
        ) -> np.ndarray:
            vector = np.zeros(coordinates[0].shape + (3,), dtype=float)
            vector[..., index] = _compact_factor(coordinates)
            return vector

        per_generator[f"T_{index + 1}"] = abs(_gauge_euler_pairing(one_generator, 4))

    anisotropic_metric = np.diag([1.0, 1.35, 0.72])
    mutant_actions = []
    for sign in (1.0, -1.0):
        states = _gauge_moved_states(sign * ACTION_STEP, _compact_lambda_vector)
        mutant_actions.append(
            sum(
                _integrate(
                    lambda coordinates, side=side: _charged_bulk_density(
                        side,
                        coordinates,
                        states[side][0],
                        states[side][1],
                        states[side][2],
                        anisotropic_metric,
                    )[0],
                    DIM,
                    4,
                )
                for side in (-1, 1)
            )
        )
    mutant_derivative = (mutant_actions[0] - mutant_actions[1]) / (2.0 * ACTION_STEP)
    return {
        "bulk_dimensions": DIM,
        "support_fraction": float(np.mean(np.linalg.norm(lambda_value, axis=-1) > 0.0)),
        "boundary_trace_max": float(
            max(np.max(np.abs(value)) for value in boundary_samples)
        ),
        "all_three_generator_norms": [
            float(np.sqrt(np.mean(lambda_value[..., index] ** 2))) for index in range(3)
        ],
        "direct_full_action_gauge_derivative": direct,
        "Euler_gauge_pairing": euler,
        "direct_vs_Euler_error": abs(direct - euler),
        "per_generator_compact_pairing_absolute": per_generator,
        "anisotropic_noninvariant_V4_mutant_derivative": mutant_derivative,
    }


def _interface_lambda_vector(tangential: tuple[np.ndarray, ...]) -> np.ndarray:
    tangential = tuple(np.broadcast_arrays(*tangential))
    factor = np.ones_like(tangential[0])
    for coordinate in tangential:
        factor *= 4.0 * coordinate * (1.0 - coordinate)
    return np.stack(
        (
            factor * (0.19 + 0.031 * tangential[0]),
            factor * (-0.15 + 0.027 * tangential[2]),
            factor * (0.12 + 0.023 * tangential[1] - 0.017 * tangential[3]),
        ),
        axis=-1,
    )


def _interface_reaching_lambda_vector(
    coordinates: tuple[np.ndarray, ...],
) -> np.ndarray:
    tangential = coordinates[:4]
    normal = coordinates[4]
    return _interface_lambda_vector(tangential) * (1.0 - normal)[..., None] ** 2


def _robin_solder_frame_certificate(count: int = 4) -> dict[str, Any]:
    tangential, weights = _gauss_grid(4, count)
    phi = _interface_phi_internal(tangential)
    frame = _interface_frame(tangential)
    lambda_matrix = _hat(_interface_lambda_vector(tangential))
    delta_phi = np.einsum("...ab,...b->...a", lambda_matrix, phi)
    delta_frame = -np.einsum("...ia,...ab->...ib", frame, lambda_matrix)
    delta_varphi = (
        np.einsum("...ia,...a->...i", delta_frame, phi)
        + np.einsum("...ia,...a->...i", frame, delta_phi)
    )

    moved_actions = []
    fixed_frame_actions = []
    for sign in (1.0, -1.0):
        moved_actions.append(
            float(
                np.sum(
                    weights
                    * _robin_density_from(
                        tangential,
                        phi + sign * ACTION_STEP * delta_phi,
                        frame + sign * ACTION_STEP * delta_frame,
                    )
                )
            )
        )
        fixed_frame_actions.append(
            float(
                np.sum(
                    weights
                    * _robin_density_from(
                        tangential,
                        phi + sign * ACTION_STEP * delta_phi,
                        frame,
                    )
                )
            )
        )
    direct = (moved_actions[0] - moved_actions[1]) / (2.0 * ACTION_STEP)
    fixed_frame_direct = (
        fixed_frame_actions[0] - fixed_frame_actions[1]
    ) / (2.0 * ACTION_STEP)

    sigma = _interface_sigma(tangential)
    volume = np.exp(4.0 * sigma)
    h_factor = np.exp(2.0 * sigma)
    varphi = np.einsum("...ia,...a->...i", frame, phi)
    residual = varphi - ROBIN_Y * _interface_acceleration(tangential)
    h_residual = h_factor[..., None] * residual
    e_phi = -KAPPA * volume[..., None] * np.einsum(
        "...ia,...i->...a", frame, h_residual
    )
    e_frame = -KAPPA * volume[..., None, None] * np.einsum(
        "...i,...a->...ia", h_residual, phi
    )
    phi_slot = float(np.sum(weights * np.sum(e_phi * delta_phi, axis=-1)))
    frame_slot = float(np.sum(weights * np.sum(e_frame * delta_frame, axis=(-2, -1))))
    euler_sum = phi_slot + frame_slot
    return {
        "interface_dimensions": 4,
        "solder_definition": "varphi_H^i=e_a^i phi^a",
        "internal_gauge_variation": "delta phi=lambda phi; delta e=-e lambda",
        "derived_delta_varphi_H_Linf": float(np.max(np.abs(delta_varphi))),
        "direct_Robin_gauge_derivative": direct,
        "phi_slot_Euler_pairing": phi_slot,
        "frame_slot_Euler_pairing": frame_slot,
        "Euler_slot_sum": euler_sum,
        "direct_vs_slot_sum_error": abs(direct - euler_sum),
        "fixed_frame_mutant_direct_derivative": fixed_frame_direct,
        "fixed_frame_mutant_vs_phi_slot_error": abs(fixed_frame_direct - phi_slot),
        "Robin_action_value": float(np.sum(weights * _robin_density(tangential))),
        "minimum_frame_singular_value": float(
            np.min(np.linalg.svd(frame, compute_uv=False))
        ),
    }


def _interface_residue_certificate(count: int = 4) -> dict[str, Any]:
    charged_actions = []
    for sign in (1.0, -1.0):
        pieces = _charged_action_parts(
            _gauge_moved_states(
                sign * ACTION_STEP, _interface_reaching_lambda_vector
            ),
            count=count,
        )
        charged_actions.append(pieces["BF"] + pieces["matter"])
    direct_bulk = (charged_actions[0] - charged_actions[1]) / (2.0 * ACTION_STEP)
    euler_bulk = _gauge_euler_pairing(_interface_reaching_lambda_vector, count)

    tangential, weights = _gauss_grid(4, count)
    bulk_coordinates = _interface_coordinates(tangential)
    lambda_matrix = _hat(_interface_lambda_vector(tangential))
    tangential_slot = FORM_POSITIONS[4][(0, 1, 2, 3)]
    side_fluxes = {}
    for side in (-1, 1):
        e_a = _full_euler_certificate_at(side, bulk_coordinates)["E_A"]
        density = _inner(e_a[..., tangential_slot, :, :], lambda_matrix)
        side_fluxes[str(side)] = float(np.sum(weights * density))
    outward_sum = side_fluxes["-1"] + side_fluxes["1"]
    wrong_incidence = side_fluxes["-1"] - side_fluxes["1"]
    robin = _robin_solder_frame_certificate(count)
    direct_total = direct_bulk + robin["direct_Robin_gauge_derivative"]
    green_balance = euler_bulk - outward_sum
    return {
        "bulk_dimensions": DIM,
        "interface_dimensions": 4,
        "lambda_interface_L2": float(
            np.sqrt(np.mean(_interface_lambda_vector(tangential) ** 2))
        ),
        "direct_bulk_action_gauge_derivative": direct_bulk,
        "derived_Robin_gauge_derivative": robin["direct_Robin_gauge_derivative"],
        "direct_full_action_gauge_derivative": direct_total,
        "bulk_Euler_gauge_pairing": euler_bulk,
        "outward_interface_E_A_flux_by_side": side_fluxes,
        "outward_interface_E_A_flux_sum": outward_sum,
        "wrong_relative_incidence_flux": wrong_incidence,
        "Green_identity": "delta S_bulk = <E,delta_gauge fields> - outward <E_A,lambda>",
        "Euler_minus_outward_flux": green_balance,
        "direct_vs_Green_balance_error": abs(direct_total - green_balance),
        "direct_vs_Euler_error": abs(direct_total - euler_bulk),
        "Euler_vs_outward_flux_error": abs(euler_bulk - outward_sum),
        "direct_vs_outward_flux_error": abs(direct_total - outward_sum),
        "interface_residue_magnitude": abs(outward_sum),
        "omit_interface_residue_witness": abs(euler_bulk),
        "wrong_incidence_witness": abs(euler_bulk - wrong_incidence),
        "BV_BFV_edge_fields_constructed": False,
        "regulated_interface_charge_algebra_constructed": False,
    }


def _five_coordinate_activity_certificate() -> dict[str, Any]:
    coordinates, _ = _gauss_grid(DIM, 2)
    rows = {}
    for side in (-1, 1):
        connection = _base_connection(side)
        b_field = _base_b(side)
        phi = _base_phi(side)
        rows[str(side)] = {
            "A_derivative_L2_by_coordinate": [
                _form_l2(_partial(connection, coordinates, axis))
                for axis in range(DIM)
            ],
            "B_derivative_L2_by_coordinate": [
                _form_l2(_partial(b_field, coordinates, axis))
                for axis in range(DIM)
            ],
            "phi_derivative_L2_by_coordinate": [
                _vector_l2(_partial(phi, coordinates, axis))
                for axis in range(DIM)
            ],
            "Omega_derivative_L2_by_coordinate": [
                float(
                    np.sqrt(
                        np.mean(
                            _partial(
                                lambda moved, side=side: _omega_field(side, moved),
                                coordinates,
                                axis,
                            )
                            ** 2
                        )
                    )
                )
                for axis in range(DIM)
            ],
            "metric_conformal_derivative_L2_by_coordinate": [
                float(
                    np.sqrt(
                        np.mean(
                            _partial(
                                lambda moved, side=side: _sigma_field(side, moved),
                                coordinates,
                                axis,
                            )
                            ** 2
                        )
                    )
                )
                for axis in range(DIM)
            ],
        }

    tangential, _ = _gauss_grid(4, 2)
    interface = _interface_coordinates(tangential)
    a_minus = _connection(-1, interface)[..., :4, :, :]
    a_plus = _connection(1, interface)[..., :4, :, :]
    return {
        "bulk_dimension": DIM,
        "interface_dimension": 4,
        "connection_form_degree": 1,
        "curvature_form_degree": 2,
        "B_form_degree": 3,
        "connection_Euler_form_degree": 4,
        "Ward_form_degree": 5,
        "side_activity": rows,
        "interface_trace_match_errors": {
            "tangential_A": float(np.max(np.abs(a_plus - a_minus))),
            "phi": float(
                np.max(
                    np.abs(_phi_field(1, interface) - _phi_field(-1, interface))
                )
            ),
            "Omega": float(
                np.max(
                    np.abs(
                        _omega_field(1, interface) - _omega_field(-1, interface)
                    )
                )
            ),
            "induced_metric_conformal_factor": float(
                np.max(
                    np.abs(
                        _sigma_field(1, interface) - _sigma_field(-1, interface)
                    )
                )
            ),
        },
    }


def _bulk_identity_side(side: int) -> dict[str, Any]:
    coordinates, _ = _gauss_grid(DIM, 1)
    connection = _base_connection(side)
    b_field = _base_b(side)
    phi = _base_phi(side)

    def db_function(moved: tuple[np.ndarray, ...]) -> np.ndarray:
        return _covariant_form_derivative(b_field, 3, connection, moved)

    def current_function(moved: tuple[np.ndarray, ...]) -> np.ndarray:
        return _matter_current_four_form(side, connection, phi, moved)

    def e_a_function(moved: tuple[np.ndarray, ...]) -> np.ndarray:
        return db_function(moved) + current_function(moved)

    def curvature_function(moved: tuple[np.ndarray, ...]) -> np.ndarray:
        return _curvature(connection, moved)

    d_db = _covariant_form_derivative(db_function, 4, connection, coordinates)
    d_current = _covariant_form_derivative(
        current_function, 4, connection, coordinates
    )
    d_e_a = _covariant_form_derivative(e_a_function, 4, connection, coordinates)
    curvature = curvature_function(coordinates)
    d_curvature = _covariant_form_derivative(
        curvature_function, 2, connection, coordinates
    )
    b_value = b_field(coordinates)
    e_phi, e_phi_kinetic, e_phi_potential = _matter_euler_phi(
        side, connection, phi, coordinates
    )
    volume, _ = _metric_data(side, coordinates)
    e_phi_top = volume[..., None] * e_phi
    matter_moment = _mu(phi(coordinates), e_phi_top)[..., None, :, :]
    b_bracket_f = _form_bracket(b_value, 3, curvature, 2)
    f_bracket_b = _form_bracket(curvature, 2, b_value, 3)
    w = d_e_a + b_bracket_f + matter_moment
    d_squared_b_residual = d_db - f_bracket_b
    matter_residual = d_current + matter_moment

    p_upper = _p_upper(side, connection, phi, coordinates)
    c_value = _c_form(side, coordinates)
    c_p = Z5 * np.sum(c_value[..., :, None] * p_upper, axis=-2)
    omit_c_moment = _mu(
        phi(coordinates), volume[..., None] * (e_phi + c_p)
    )[..., None, :, :]
    potential_moment = _mu(
        phi(coordinates), volume[..., None] * e_phi_potential
    )[..., None, :, :]
    anisotropic = np.diag([1.0, 1.35, 0.72])
    anisotropic_source = np.einsum("ab,...b->...a", anisotropic, phi(coordinates))
    anisotropic_moment = _mu(
        phi(coordinates), volume[..., None] * anisotropic_source
    )[..., None, :, :]
    ordinary_d_e_a = _exterior_derivative(e_a_function, 4, coordinates)
    ordinary_d_f = _exterior_derivative(curvature_function, 2, coordinates)
    p_full_lower = _p_lower(side, connection, phi, coordinates)
    p_without_c = np.stack(
        [
            _covariant_vector_component(phi, connection, coordinates, axis)
            for axis in range(DIM)
        ],
        axis=-2,
    )
    _, inverse_diagonal = _metric_data(side, coordinates)
    full_kinetic = np.sum(
        inverse_diagonal[..., :, None] * p_full_lower**2, axis=(-2, -1)
    )
    omit_c_kinetic = np.sum(
        inverse_diagonal[..., :, None] * p_without_c**2, axis=(-2, -1)
    )
    omit_c_phi_action_density_witness = float(
        np.max(np.abs(-0.5 * Z5 * volume * (full_kinetic - omit_c_kinetic)))
    )

    w_components = {
        f"T_{index + 1}": {
            "absolute": float(
                np.max(np.abs(_inner(generator, w[..., 0, :, :])))
            )
        }
        for index, generator in enumerate(_generators())
    }
    mutants = {
        "omit_B_bracket_E_B": _form_l2(d_e_a + matter_moment),
        "omit_mu_phi_E_phi": _form_l2(d_e_a + b_bracket_f),
        "flip_D_A_E_A_sign": _form_l2(-d_e_a + b_bracket_f + matter_moment),
        "abelianize_D_A_E_A": _form_l2(ordinary_d_e_a + b_bracket_f + matter_moment),
        "flip_B_bracket_E_B_sign": _form_l2(d_e_a - b_bracket_f + matter_moment),
        "flip_J_A_sign": _form_l2(
            d_db - d_current + b_bracket_f + matter_moment
        ),
        "omit_conformal_minus_cP": _form_l2(d_current + omit_c_moment),
        "omit_c_phi_from_P_action_density": omit_c_phi_action_density_witness,
        "replace_radial_V4_by_anisotropic_source": _form_l2(
            d_e_a + b_bracket_f + matter_moment + 0.19 * anisotropic_moment
        ),
    }
    return {
        "side": side,
        "sample_coordinates": [0.5] * DIM,
        "off_shell_W": {
            "total_L2_residual": _form_l2(w),
            "per_generator": w_components,
            "Euler_norms": {
                "E_A": _form_l2(e_a_function(coordinates)),
                "E_B": _form_l2(curvature),
                "E_phi": _vector_l2(e_phi),
            },
            "term_norms": {
                "D_A_E_A": _form_l2(d_e_a),
                "B_bracket_E_B": _form_l2(b_bracket_f),
                "mu_phi_E_phi": _form_l2(matter_moment),
            },
        },
        "D_squared_B": {
            "identity": "D_A^2 B=[F,B] as five-forms",
            "residual": _form_l2(d_squared_b_residual),
            "lhs_norm": _form_l2(d_db),
            "rhs_norm": _form_l2(f_bracket_b),
            "wrong_sign_witness": _form_l2(d_db + f_bracket_b),
        },
        "matter_current": {
            "identity": "D_A(*J)+mu(phi,E_phi vol_5)=0",
            "residual": _form_l2(matter_residual),
            "D_A_current_norm": _form_l2(d_current),
            "matter_moment_norm": _form_l2(matter_moment),
            "c_i_P_i_norm": _vector_l2(c_p),
            "omit_c_i_P_i_witness": _form_l2(d_current + omit_c_moment),
            "radial_V4_moment_norm": _form_l2(potential_moment),
            "anisotropic_V4_moment_witness": _form_l2(anisotropic_moment),
        },
        "five_dimensional_Bianchi": {
            "identity": "D_A F=0 as a three-form in five dimensions",
            "residual": _form_l2(d_curvature),
            "curvature_norm": _form_l2(curvature),
            "covariant_derivative_term_norm": _form_l2(
                _wedge_matrix(connection(coordinates), 1, curvature, 2)
                - _wedge_matrix(curvature, 2, connection(coordinates), 1)
            ),
            "ordinary_derivative_mutant_witness": _form_l2(ordinary_d_f),
        },
        "full_material": {
            "Omega": float(_omega_field(side, coordinates).reshape(-1)[0]),
            "c_norm": _vector_l2(c_value),
            "P_norm": _vector_l2(p_upper.reshape(p_upper.shape[:-2] + (-1,))),
            "V4_Ephi_norm": _vector_l2(e_phi_potential),
            "radial_V4_moment_norm": _form_l2(potential_moment),
            "anisotropic_V4_moment_witness": _form_l2(anisotropic_moment),
            "rho_zero_extension_norm": _vector_l2(
                _radial_potential_euler(
                    side, np.zeros_like(phi(coordinates)), coordinates
                )
            ),
        },
        "mutant_witnesses": mutants,
    }


def _internal_vs_diffeomorphism_scope() -> dict[str, Any]:
    adm_decision = ADM.get("decision", {})
    redteam_decision = ADM_REDTEAM.get("decision", {})
    return {
        "internal_SO3_slots": ["A", "B", "phi", "solder_frame"],
        "internal_SO3_fixed_slots": ["g", "Omega", "Y", "T", "gamma"],
        "diffeomorphism_khronon_slots": ["g", "Omega", "Y", "T", "all pulled-back fields"],
        "identities_are_not_equated": True,
        "ADM_primary_full_all_field_normal_embedding": adm_decision.get(
            "complete_v5_2_all_field_normal_embedding_pass"
        ),
        "ADM_primary_full_Green": adm_decision.get(
            "full_off_shell_Green_theorem_accepted"
        ),
        "ADM_primary_C1": adm_decision.get("C1_ACTION_pass"),
        "ADM_primary_N1": adm_decision.get("N1_ACTION_pass"),
        "ADM_redteam_full_all_field_normal_embedding": redteam_decision.get(
            "complete_v5_2_all_field_normal_embedding_pass"
        ),
        "ADM_redteam_full_Green": redteam_decision.get(
            "full_off_shell_Green_theorem_accepted"
        ),
        "ADM_redteam_C1": redteam_decision.get("C1_ACTION_pass"),
        "ADM_redteam_N1": redteam_decision.get("N1_ACTION_pass"),
        "full_diffeomorphism_khronon_Ward_reproduced_status": "FAIL_CLOSED",
    }


def _matrix_and_form_representation_certificate() -> dict[str, Any]:
    basis = _generators()
    gram = np.asarray([[_inner(left, right) for right in basis] for left in basis])
    structure = [
        np.linalg.norm(basis[0] @ basis[1] - basis[1] @ basis[0] - basis[2]),
        np.linalg.norm(basis[1] @ basis[2] - basis[2] @ basis[1] - basis[0]),
        np.linalg.norm(basis[2] @ basis[0] - basis[0] @ basis[2] - basis[1]),
    ]
    probe_lambda = _hat(np.asarray([0.17, -0.11, 0.08]))
    probe_x = _hat(np.asarray([0.23, 0.14, -0.19]))
    probe_y = _hat(np.asarray([-0.09, 0.21, 0.16]))
    invariance = abs(
        _inner(probe_lambda @ probe_x - probe_x @ probe_lambda, probe_y)
        + _inner(probe_x, probe_lambda @ probe_y - probe_y @ probe_lambda)
    )
    one = np.zeros((len(FORM_INDICES[1]), 3, 3))
    four = np.zeros((len(FORM_INDICES[4]), 3, 3))
    one[FORM_POSITIONS[1][(4,)]] = basis[0]
    four[FORM_POSITIONS[4][(0, 1, 2, 3)]] = basis[0]
    return {
        "Gram_matrix": gram.tolist(),
        "Gram_identity_error": float(np.linalg.norm(gram - np.eye(3))),
        "maximum_structure_constant_error": float(max(structure)),
        "invariant_trace_error": float(invariance),
        "four_form_wedge_normal_one_form": float(_wedge_pair(four, 4, one, 1)),
        "normal_one_form_wedge_four_form": float(_wedge_pair(one, 1, four, 4)),
        "expected_even_interchange_sign": 1.0,
        "form_component_counts": {
            str(degree): len(FORM_INDICES[degree]) for degree in range(DIM + 1)
        },
    }


def _derivative_resolution_certificate() -> dict[str, Any]:
    coordinates = tuple(np.asarray(0.19 + 0.11 * axis) for axis in range(DIM))
    frequencies = np.asarray([0.61, 0.73, 0.89, 1.03, 1.19])

    def analytic_function(moved: tuple[np.ndarray, ...]) -> np.ndarray:
        return np.sin(sum(frequencies[axis] * moved[axis] for axis in range(DIM)))

    phase = sum(frequencies[axis] * coordinates[axis] for axis in range(DIM))

    def stencil(axis: int, step: float) -> float:
        values = []
        for shift in (-2.0, -1.0, 1.0, 2.0):
            moved = list(coordinates)
            moved[axis] = moved[axis] + shift * step
            values.append(float(analytic_function(tuple(moved))))
        return (values[0] - 8.0 * values[1] + 8.0 * values[2] - values[3]) / (
            12.0 * step
        )

    coarse_step = 4.0e-2
    fine_step = 2.0e-2
    rows = {}
    for axis in range(DIM):
        exact = float(frequencies[axis] * np.cos(phase))
        coarse_error = abs(stencil(axis, coarse_step) - exact)
        fine_error = abs(stencil(axis, fine_step) - exact)
        rows[f"x{axis}"] = {
            "coarse_error": coarse_error,
            "fine_error": fine_error,
            "coarse_to_fine_error_ratio": coarse_error / max(fine_error, 1.0e-30),
        }
    return {
        "stencil": "centered fourth-order finite difference",
        "coarse_step": coarse_step,
        "fine_step": fine_step,
        "expected_asymptotic_error_ratio": 16.0,
        "coordinates": rows,
        "minimum_observed_error_ratio": min(
            row["coarse_to_fine_error_ratio"] for row in rows.values()
        ),
        "maximum_fine_error": max(row["fine_error"] for row in rows.values()),
    }


@lru_cache(maxsize=1)
def independent_runtime_certificate() -> dict[str, Any]:
    sides = {str(side): _bulk_identity_side(side) for side in (-1, 1)}
    action = _action_to_euler_certificate()
    compact = _compact_lambda_certificate()
    robin = _robin_solder_frame_certificate()
    interface = _interface_residue_certificate()
    activity = _five_coordinate_activity_certificate()
    euler_minimum = min(
        value
        for side in sides.values()
        for value in side["off_shell_W"]["Euler_norms"].values()
    )
    term_minimum = min(
        value
        for side in sides.values()
        for value in side["off_shell_W"]["term_norms"].values()
    )
    mutant_minimum = min(
        value
        for side in sides.values()
        for value in side["mutant_witnesses"].values()
    )
    return {
        "representation": {
            "group": "SO(3)",
            "matrices": "real defining 3x3 antisymmetric hat representation",
            "pairing": "<X,Y>=-tr_3(XY)/2",
            "form_engine": "independent ordered-basis exterior algebra in dimension five",
            "primary_helpers_imported": [],
        },
        "literal_full_action": {
            "source": "pinned v5.2 exact_classical_charter.exact_action",
            "terms": V5_2["exact_classical_charter"]["exact_action"],
            "charged_Euler_scope": "A one-form, B three-form and phi on both full 5D bulks",
            "neutral_internal_gauge_slots": [
                "EH", "Omega_and_U", "GHY", "wall_background", "foliation_lower"
            ],
            "Robin_neutrality_is_derived_from_solder_and_frame_slots": True,
        },
        "five_coordinate_activity": activity,
        "bulk_internal_gauge_identity_by_side": sides,
        "action_to_Euler": action,
        "compact_lambda": compact,
        "Robin_solder_frame": robin,
        "interface_residue": interface,
        "internal_vs_diffeomorphism_khronon": _internal_vs_diffeomorphism_scope(),
        "on_shell_and_circularity_detector": {
            "zero_Euler_mock_W_norm": 0.0,
            "actual_off_shell_Euler_minimum": euler_minimum,
            "actual_identity_term_minimum": term_minimum,
            "minimum_mutant_witness": mutant_minimum,
            "primary_runtime_values_imported": False,
            "stored_artifact_values_used_as_oracle": False,
            "on_shell_only_check_rejected": bool(
                euler_minimum > 1.0e-4
                and term_minimum > 1.0e-4
                and mutant_minimum > 1.0e-4
            ),
        },
        "matrix_and_form_representation_certificate": _matrix_and_form_representation_certificate(),
        "derivative_resolution_certificate": _derivative_resolution_certificate(),
    }


def adm_control_contract() -> dict[str, bool]:
    primary = ADM.get("decision", {})
    redteam = ADM_REDTEAM.get("decision", {})
    return {
        "ADM_primary_candidate_checks_pass": primary.get("candidate_checks_pass") is True,
        "ADM_primary_gamma_chain_pass": primary.get(
            "one_action_independent_gamma_ADM_chain_pass"
        )
        is True,
        "ADM_primary_diffeomorphism_completion_red": (
            primary.get("complete_v5_2_all_field_normal_embedding_pass") is False
            and primary.get("full_off_shell_Green_theorem_accepted") is False
            and primary.get("full_classical_variational_principle_selected_sector_pass")
            is False
            and primary.get("C1_ACTION_pass") is False
            and primary.get("N1_ACTION_pass") is False
        ),
        "ADM_redteam_independent_checks_pass": redteam.get(
            "independent_redteam_checks_pass"
        )
        is True,
        "ADM_redteam_action_routes_pass": redteam.get(
            "independent_action_routes_chain_pass"
        )
        is True,
        "ADM_redteam_diffeomorphism_completion_red": (
            redteam.get("complete_v5_2_all_field_normal_embedding_pass") is False
            and redteam.get("full_off_shell_Green_theorem_accepted") is False
            and redteam.get("full_classical_variational_principle_selected_sector_pass")
            is False
            and redteam.get("C1_ACTION_pass") is False
            and redteam.get("N1_ACTION_pass") is False
        ),
    }


def primary_contract(primary: Mapping[str, Any] | None = None) -> dict[str, bool]:
    primary = _load_primary() if primary is None else primary
    decision = primary.get("decision", {})
    checks = primary.get("checks", {})
    certificate = primary.get("certificate", {})
    form = certificate.get("form_degree_contract", {})
    ledger = primary.get("equation_ledger", {})
    provenance = primary.get("provenance", {})
    preliminary = primary.get("v5_5_1_preliminary_receipt", {})
    pinned_v52 = primary.get("pinned_v5_2", {})
    pinned_adm = primary.get("pinned_v5_5_2_ADM_controls", {})
    bulk_sides = certificate.get("bulk_sides", {})
    primary_mutants = [
        row.get("mutant_witnesses", {})
        for row in bulk_sides.values()
        if isinstance(row, Mapping)
    ]
    return {
        "primary_schema": primary.get("schema") == EXPECTED_PRIMARY_SCHEMA,
        "primary_all_checks_true": bool(checks)
        and checks.get("all_primary_scope_checks") is True
        and all(value is True for value in checks.values()),
        "primary_internal_full_action_flags": (
            decision.get("bulk_full_v5_2_internal_SO3_Ward_pass") is True
            and decision.get("interface_full_v5_2_internal_SO3_Ward_selected_sector_pass")
            is True
            and decision.get("internal_SO3_full_action_selected_trivial_sector_Ward_pass")
            is True
            and decision.get("boundary_Green_local_exact_identity_pass") is True
        ),
        "primary_diffeomorphism_and_downstream_fail_closed": (
            decision.get("diffeomorphism_khronon_full_Ward_pass") is False
            and decision.get("complete_BV_BFV_boundary_complex_pass") is False
            and decision.get("unrestricted_large_gauge_sector_pass") is False
            and decision.get("v5_6_promotion_authorized") is False
            and decision.get("C1_ACTION_pass") is False
            and decision.get("N1_ACTION_pass") is False
            and decision.get("N4_JUNCTION_BENDING_pass") is False
            and decision.get("P4_full_same_action_pass") is False
            and decision.get("B4_pass") is False
            and decision.get("B5_pass") is False
            and decision.get("publication_authorized") is False
        ),
        "primary_real_five_dimensional_form_contract": (
            form.get("ambient_dimension") == DIM
            and form.get("bulk_grid_shape") == [7, 7, 7, 7, 7]
            and form.get("interface_grid_shape") == [7, 7, 7, 7]
            and form.get("internal_generators") == 3
            and form.get("dimensional_reduction_or_spectator_ansatz_used") is False
            and form.get("active_coordinates") == ["x0", "x1", "x2", "x3", "x4"]
            and form.get("A", {}).get("degree") == 1
            and form.get("B", {}).get("degree") == 3
            and form.get("F_and_E_B", {}).get("degree") == 2
            and form.get("D_B_J_and_E_A", {}).get("degree") == 4
            and form.get("W", {}).get("degree") == 5
        ),
        "primary_full_action_and_Ward_ledger": (
            ledger.get("bulk_action")
            == V5_2["exact_classical_charter"]["exact_action"]["bulk_gauged"]
            and ledger.get("BF_action")
            == V5_2["exact_classical_charter"]["exact_action"]["BF"]
            and ledger.get("Ward_5form")
            == "W=D_A E_A+B cross-wedge E_B+sqrt(-g) phi cross E_phi d5x=0"
            and ledger.get("Bianchi")
            == "D_A F=0 as a five-dimensional adjoint-valued 3-form"
            and "c_M=3 partial_M log(Omega)/2" in ledger.get("matter", "")
            and "delta R=-R hat(lambda)" in ledger.get("source_groupoid", "")
        ),
        "primary_explicit_J_and_conformal_mutants": (
            len(primary_mutants) == 2
            and all(row.get("flip_J_A_sign", 0.0) > 1.0e-3 for row in primary_mutants)
            and all(row.get("omit_J_from_E_A", 0.0) > 1.0e-3 for row in primary_mutants)
            and all(
                row.get("omit_c_M_P_M_in_E_phi", 0.0) > 1.0e-4
                for row in primary_mutants
            )
            and all(
                row.get("omit_c_phi_from_P_action_mismatch", 0.0) > 1.0e-3
                for row in primary_mutants
            )
        ),
        "primary_diffeomorphism_attempt_explicitly_incomplete": certificate.get(
            "diffeomorphism_khronon_attempt", {}
        ).get("full_diffeomorphism_khronon_Ward_completed")
        is False,
        "primary_v5_5_1_reduction_not_consumed": (
            preliminary.get("consumed") is False
            and preliminary.get("promotable_by_this_gate") is False
        ),
        "primary_v5_2_and_ADM_bindings": (
            pinned_v52.get("sha256") == EXPECTED_V5_2_SHA256
            and pinned_adm.get("sha256") == EXPECTED_ADM_ARTIFACT_SHA256
            and pinned_adm.get("scope")
            == "ADM/Israel/T_ui controls only; no inherited Ward boolean"
        ),
        "primary_internal_provenance": (
            provenance.get("generator", {}).get("sha256")
            == EXPECTED_PRIMARY_GENERATOR_SHA256
            and provenance.get("test", {}).get("sha256")
            == EXPECTED_PRIMARY_TEST_SHA256
        ),
    }


def _formula_to_oracle_table(runtime: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "formula": "S_v5_2 full action",
            "oracle": "action_to_Euler with Gauss orders 2,3,4",
            "evidence": runtime["action_to_Euler"]["absolute_error"],
        },
        {
            "formula": "W=D_A E_A+[B,E_B]+mu(phi,E_phi vol_5)",
            "oracle": "independent exterior derivative by side and generator",
            "evidence": max(
                side["off_shell_W"]["total_L2_residual"]
                for side in runtime["bulk_internal_gauge_identity_by_side"].values()
            ),
        },
        {
            "formula": "D_A^2 B=[F,B]",
            "oracle": "direct nested covariant derivative versus curvature bracket",
            "evidence": max(
                side["D_squared_B"]["residual"]
                for side in runtime["bulk_internal_gauge_identity_by_side"].values()
            ),
        },
        {
            "formula": "D_A F=0",
            "oracle": "five-dimensional three-form Bianchi",
            "evidence": max(
                side["five_dimensional_Bianchi"]["residual"]
                for side in runtime["bulk_internal_gauge_identity_by_side"].values()
            ),
        },
        {
            "formula": "D_A J_A+mu(phi,E_phi vol_5)=0",
            "oracle": "separate full-matter current reduction",
            "evidence": max(
                side["matter_current"]["residual"]
                for side in runtime["bulk_internal_gauge_identity_by_side"].values()
            ),
        },
        {
            "formula": "varphi_H=e phi; delta e=-e lambda",
            "oracle": "direct four-dimensional Robin action derivative",
            "evidence": runtime["Robin_solder_frame"]["direct_vs_slot_sum_error"],
        },
        {
            "formula": "delta S_bulk=<E,delta_gauge fields>-outward <E_A,lambda>",
            "oracle": "bulk action, Euler pairing and outward four-form flux",
            "evidence": runtime["interface_residue"]["direct_vs_Green_balance_error"],
        },
    ]


def build_payload() -> dict[str, Any]:
    hashes = {
        "primary_generator": _sha256(PRIMARY_GENERATOR),
        "primary_test": _sha256(PRIMARY_TEST),
        "primary_artifact": _sha256(PRIMARY_ARTIFACT),
        "v5_2_artifact": _sha256(V5_2_ARTIFACT),
        "ADM_generator": _sha256(ADM_GENERATOR),
        "ADM_test": _sha256(ADM_TEST),
        "ADM_artifact": _sha256(ADM_ARTIFACT),
        "ADM_redteam_generator": _sha256(ADM_REDTEAM_GENERATOR),
        "ADM_redteam_test": _sha256(ADM_REDTEAM_TEST),
        "ADM_redteam_artifact": _sha256(ADM_REDTEAM_ARTIFACT),
    }
    expected = {
        "primary_generator": EXPECTED_PRIMARY_GENERATOR_SHA256,
        "primary_test": EXPECTED_PRIMARY_TEST_SHA256,
        "primary_artifact": EXPECTED_PRIMARY_ARTIFACT_SHA256,
        "v5_2_artifact": EXPECTED_V5_2_SHA256,
        "ADM_generator": EXPECTED_ADM_GENERATOR_SHA256,
        "ADM_test": EXPECTED_ADM_TEST_SHA256,
        "ADM_artifact": EXPECTED_ADM_ARTIFACT_SHA256,
        "ADM_redteam_generator": EXPECTED_ADM_REDTEAM_GENERATOR_SHA256,
        "ADM_redteam_test": EXPECTED_ADM_REDTEAM_TEST_SHA256,
        "ADM_redteam_artifact": EXPECTED_ADM_REDTEAM_ARTIFACT_SHA256,
    }
    if hashes != expected:
        raise FullActionGaugeV553RedteamError("frozen input hash mismatch")
    primary = primary_contract()
    adm = adm_control_contract()
    if not all(primary.values()):
        failed = sorted(key for key, value in primary.items() if not value)
        raise FullActionGaugeV553RedteamError(f"primary contract failed: {failed}")
    if not all(adm.values()):
        failed = sorted(key for key, value in adm.items() if not value)
        raise FullActionGaugeV553RedteamError(f"ADM control contract failed: {failed}")

    runtime = independent_runtime_certificate()
    representation = runtime["matrix_and_form_representation_certificate"]
    resolution = runtime["derivative_resolution_certificate"]
    activity = runtime["five_coordinate_activity"]
    sides = runtime["bulk_internal_gauge_identity_by_side"]
    action = runtime["action_to_Euler"]
    compact = runtime["compact_lambda"]
    robin = runtime["Robin_solder_frame"]
    interface = runtime["interface_residue"]
    on_shell = runtime["on_shell_and_circularity_detector"]
    convergence = action["successive_absolute_errors"]
    all_activity = [
        value
        for side in activity["side_activity"].values()
        for name, values in side.items()
        for value in values
        if name.endswith("_by_coordinate")
    ]
    checks = {
        "independent_matrix_and_five_form_engine_is_exact": (
            representation["Gram_identity_error"] < 2.0e-14
            and representation["maximum_structure_constant_error"] < 2.0e-14
            and representation["invariant_trace_error"] < 2.0e-14
            and abs(representation["four_form_wedge_normal_one_form"] - 1.0)
            < 2.0e-14
            and abs(representation["normal_one_form_wedge_four_form"] - 1.0)
            < 2.0e-14
            and representation["form_component_counts"]
            == {"0": 1, "1": 5, "2": 10, "3": 10, "4": 5, "5": 1}
        ),
        "finite_difference_resolution_has_fourth_order_error_ratio": (
            resolution["stencil"] == "centered fourth-order finite difference"
            and resolution["minimum_observed_error_ratio"] > 12.0
            and resolution["maximum_fine_error"] < 2.0e-8
            and len(resolution["coordinates"]) == 5
        ),
        "all_five_coordinates_and_both_interface_traces_are_active": (
            activity["bulk_dimension"] == 5
            and activity["interface_dimension"] == 4
            and min(all_activity) > 1.0e-4
            and max(activity["interface_trace_match_errors"].values()) < 2.0e-13
        ),
        "full_action_Euler_matches_with_resolved_quadrature": (
            action["arbitrary_variation_scale"] == 2.0
            and action["absolute_error"] < 5.0e-7
            and convergence[2] < convergence[0]
            and convergence[2] < convergence[1]
            and convergence[2] / max(convergence[0], convergence[1]) < 0.25
            and action["tensor_product_node_counts"]
            == {"2": 32, "3": 243, "4": 1024}
            and min(action["successive_error_ratios"]) > 1.2
            and action["active_derivative_magnitude"] > 1.0e-4
            and action["flip_matter_source_sign_witness"] > 1.0e-4
            and action["neutral_piece_central_derivative_max"] < 1.0e-14
            and min(abs(value) for value in action["active_action_pieces"].values())
            > 1.0e-4
        ),
        "bulk_W_D2B_Bianchi_and_matter_close_on_both_sides": all(
            side["off_shell_W"]["total_L2_residual"] < 5.0e-7
            and max(
                row["absolute"]
                for row in side["off_shell_W"]["per_generator"].values()
            )
            < 2.0e-6
            and side["D_squared_B"]["residual"] < 5.0e-7
            and side["matter_current"]["residual"] < 5.0e-7
            and side["five_dimensional_Bianchi"]["residual"] < 5.0e-7
            for side in sides.values()
        ),
        "Omega_c_full_V4_J_and_all_mutants_are_active": all(
            side["full_material"]["Omega"] > 0.0
            and side["full_material"]["c_norm"] > 1.0e-4
            and side["full_material"]["P_norm"] > 1.0e-4
            and side["full_material"]["V4_Ephi_norm"] > 1.0e-4
            and side["full_material"]["radial_V4_moment_norm"] < 1.0e-12
            and side["full_material"]["anisotropic_V4_moment_witness"] > 1.0e-4
            and side["full_material"]["rho_zero_extension_norm"] < 1.0e-14
            and min(side["mutant_witnesses"].values()) > 1.0e-4
            and side["mutant_witnesses"]["flip_J_A_sign"] > 1.0e-3
            and side["mutant_witnesses"]["omit_c_phi_from_P_action_density"]
            > 1.0e-4
            for side in sides.values()
        ),
        "compact_lambda_and_noninvariant_V4_are_discriminated": (
            compact["bulk_dimensions"] == 5
            and compact["boundary_trace_max"] < 1.0e-14
            and min(compact["all_three_generator_norms"]) > 1.0e-4
            and abs(compact["direct_full_action_gauge_derivative"]) < 5.0e-6
            and abs(compact["Euler_gauge_pairing"]) < 5.0e-6
            and compact["direct_vs_Euler_error"] < 5.0e-7
            and max(compact["per_generator_compact_pairing_absolute"].values())
            < 5.0e-6
            and abs(compact["anisotropic_noninvariant_V4_mutant_derivative"])
            > 1.0e-5
        ),
        "Robin_solder_frame_neutrality_is_derived_not_assumed": (
            robin["interface_dimensions"] == 4
            and robin["derived_delta_varphi_H_Linf"] < 2.0e-14
            and abs(robin["direct_Robin_gauge_derivative"]) < 5.0e-9
            and abs(robin["Euler_slot_sum"]) < 5.0e-9
            and robin["direct_vs_slot_sum_error"] < 5.0e-9
            and abs(robin["fixed_frame_mutant_direct_derivative"]) > 1.0e-4
            and robin["fixed_frame_mutant_vs_phi_slot_error"] < 5.0e-8
            and abs(robin["Robin_action_value"]) > 1.0e-4
            and robin["minimum_frame_singular_value"] > 0.5
        ),
        "interface_residue_is_real_but_BV_BFV_stays_open": (
            interface["interface_dimensions"] == 4
            and interface["lambda_interface_L2"] > 1.0e-3
            and interface["interface_residue_magnitude"] > 1.0e-4
            and abs(interface["direct_full_action_gauge_derivative"]) < 5.0e-6
            and interface["direct_vs_Green_balance_error"] < 5.0e-6
            and interface["Euler_vs_outward_flux_error"] < 5.0e-6
            and interface["direct_vs_Euler_error"] > 1.0e-4
            and interface["direct_vs_outward_flux_error"] > 1.0e-4
            and interface["omit_interface_residue_witness"] > 1.0e-4
            and interface["wrong_incidence_witness"] > 1.0e-4
            and interface["BV_BFV_edge_fields_constructed"] is False
            and interface["regulated_interface_charge_algebra_constructed"] is False
        ),
        "on_shell_and_circular_W_oracles_are_rejected": (
            on_shell["zero_Euler_mock_W_norm"] == 0.0
            and on_shell["actual_off_shell_Euler_minimum"] > 1.0e-4
            and on_shell["actual_identity_term_minimum"] > 1.0e-4
            and on_shell["minimum_mutant_witness"] > 1.0e-4
            and on_shell["primary_runtime_values_imported"] is False
            and on_shell["stored_artifact_values_used_as_oracle"] is False
            and on_shell["on_shell_only_check_rejected"] is True
        ),
        "diffeomorphism_khronon_red_is_reproduced_not_promoted": (
            runtime["internal_vs_diffeomorphism_khronon"][
                "identities_are_not_equated"
            ]
            is True
            and runtime["internal_vs_diffeomorphism_khronon"][
                "full_diffeomorphism_khronon_Ward_reproduced_status"
            ]
            == "FAIL_CLOSED"
            and all(adm.values())
        ),
    }
    checks["all_independent_full_5D_redteam_checks"] = all(checks.values())
    if checks["all_independent_full_5D_redteam_checks"] is not True:
        failed = sorted(key for key, value in checks.items() if not value)
        raise FullActionGaugeV553RedteamError(
            f"independent full-5D red-team failed: {failed}"
        )

    decision: dict[str, Any] = {
        "primary_v5_5_3_hash_and_convention_bound_pass": all(primary.values()),
        "ADM_v5_5_2_control_hash_bound_pass": all(adm.values()),
        "full_5D_internal_SO3_gauge_Noether_independent_pass": checks[
            "all_independent_full_5D_redteam_checks"
        ],
        "full_diffeomorphism_khronon_Ward_pass": False,
        "complete_all_field_Euler_variation_pass": False,
        "complete_BV_BFV_boundary_complex_pass": False,
        "regulated_interface_charge_completion_pass": False,
        "complete_v5_2_all_field_normal_embedding_pass": False,
        "full_off_shell_Green_theorem_accepted": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "N4_JUNCTION_BENDING_pass": False,
        "P4_full_same_action_pass": False,
        "B4_pass": False,
        "B5_pass": False,
        "publication_authorized": False,
        "status": (
            "FULL_5D_INTERNAL_SO3_GAUGE_NOETHER_INDEPENDENT_REDTEAM_PASS__"
            "DIFF_KHRONON_BV_BFV_C1_N1_N4_P4_B4_B5_FAIL_CLOSED"
        ),
    }
    true_passes = {
        key for key, value in decision.items()
        if key.endswith("_pass") and value is True
    }
    if true_passes != ALLOWED_TRUE_PASS_KEYS:
        raise FullActionGaugeV553RedteamError(
            f"unexpected true pass set: {sorted(true_passes)}"
        )
    if any(decision[key] is not False for key in FAIL_CLOSED_KEYS):
        raise FullActionGaugeV553RedteamError("a fail-closed decision was promoted")

    return {
        "schema": SCHEMA,
        "title": "Independent full-5D matrix/form red-team of gauge-Noether v5.5.3",
        "classification": (
            "theory_only;full_5D_internal_SO3;independent_form_runtime;"
            "diffeomorphism_khronon_and_BV_BFV_fail_closed"
        ),
        "evidence_boundary": (
            "The independent oracle accepts only the internal SO(3) Ward identity of "
            "the unreduced five-dimensional v5.2 action and its local four-dimensional "
            "solder/Robin interface. It does not prove the arbitrary diffeomorphism--"
            "khronon Ward identity, all-field Euler variation, global gauges, BV-BFV, "
            "C1, N1, N4, P4, B4 or B5."
        ),
        "frozen_inputs": hashes,
        "primary_contract": primary,
        "ADM_control_contract": adm,
        "independent_runtime_certificate": runtime,
        "formula_to_oracle_table": _formula_to_oracle_table(runtime),
        "checks": checks,
        "decision": decision,
        "true_pass_allowlist": sorted(ALLOWED_TRUE_PASS_KEYS),
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {"path": str(TEST.relative_to(REPO)), "sha256": _sha256(TEST)},
            "python": platform.python_version(),
            "numpy": np.__version__,
            "primary_helpers_imported": [],
            "dimensional_reduction_used": False,
        },
    }


def main() -> None:
    payload = build_payload()
    _write(OUTPUT, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
