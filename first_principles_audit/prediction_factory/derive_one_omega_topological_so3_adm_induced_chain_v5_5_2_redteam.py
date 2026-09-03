#!/usr/bin/env python3
"""Independent red-team of the additive v5.5.2 induced-ADM certificate.

This implementation deliberately imports no helper from the primary v5.5.2
gate or from the frozen v5.5/v5.6 gates.  It uses a different off-shell jet,
a nontrivial five-dimensional pullback, a complex-step differentiation route
for the action, and a separately differentiated inverse ADM chart.

The proved scope is only the selected local matter/wall/Robin action and its
metric normal subsector.  The all-field normal embedding equation, C1, N1,
N4, B4, and B5 remain fail closed.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
PRIMARY_GENERATOR = (
    HERE / "derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py"
)
PRIMARY_TEST = (
    HERE / "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py"
)
PRIMARY_ARTIFACT = (
    HERE / "artifacts" / "one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.json"
)
OUTPUT = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.json"
)
TEST = HERE / "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.py"

SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-redteam.v1"
PRIMARY_SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-gate.v1"
EXPECTED_PRIMARY_GENERATOR_SHA256 = (
    "00f8fa443bda37711d2456cb5e55c8a5c349d1c7f814a44c63203e3c02836e1e"
)
EXPECTED_PRIMARY_TEST_SHA256 = (
    "4547d1e7f361b2c9b931dba3a9a5a5829d2a2563ab4a0c9c54a154f9292f7aca"
)
EXPECTED_PRIMARY_ARTIFACT_SHA256 = (
    "4e068475ae316684cebd0f68e10d183fff7c0d90c46b155f2dfc8be4b3b0d6e8"
)
EXPECTED_V5_2_SHA256 = (
    "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b"
)

SYM4 = (
    (0, 0), (0, 1), (0, 2), (0, 3), (1, 1),
    (1, 2), (1, 3), (2, 2), (2, 3), (3, 3),
)
SYM3 = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))

FAIL_CLOSED_KEYS = (
    "complete_v5_2_all_field_normal_embedding_pass",
    "full_off_shell_Green_theorem_accepted",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "N4_JUNCTION_BENDING_pass",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
)


class ADMInducedV552RedteamError(ValueError):
    """The independent v5.5.2 audit is malformed or no longer reproducible."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ADMInducedV552RedteamError(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def _load_primary() -> dict[str, Any]:
    """Pin the primary by bytes without importing or executing its code."""

    actual = {
        "generator": _sha256(PRIMARY_GENERATOR),
        "test": _sha256(PRIMARY_TEST),
        "artifact": _sha256(PRIMARY_ARTIFACT),
    }
    expected = {
        "generator": EXPECTED_PRIMARY_GENERATOR_SHA256,
        "test": EXPECTED_PRIMARY_TEST_SHA256,
        "artifact": EXPECTED_PRIMARY_ARTIFACT_SHA256,
    }
    if actual != expected:
        raise ADMInducedV552RedteamError("primary v5.5.2 byte hash mismatch")
    try:
        payload = json.loads(PRIMARY_ARTIFACT.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ADMInducedV552RedteamError(f"cannot read primary artifact: {exc}") from exc
    if type(payload) is not dict or payload.get("schema") != PRIMARY_SCHEMA:
        raise ADMInducedV552RedteamError("primary v5.5.2 schema mismatch")
    provenance = payload.get("provenance", {})
    if provenance.get("generator_sha256") != expected["generator"]:
        raise ADMInducedV552RedteamError("primary generator provenance mismatch")
    if provenance.get("test_sha256") != expected["test"]:
        raise ADMInducedV552RedteamError("primary test provenance mismatch")
    pinned_v5_2 = payload.get("v5_2_source_binding", {})
    if pinned_v5_2.get("sha256") != EXPECTED_V5_2_SHA256:
        raise ADMInducedV552RedteamError("primary v5.2 lineage mismatch")
    decision = payload.get("decision", {})
    if decision.get("candidate_checks_pass") is not True:
        raise ADMInducedV552RedteamError("primary candidate is not green")
    for key in FAIL_CLOSED_KEYS:
        if decision.get(key) is not False:
            raise ADMInducedV552RedteamError(f"primary fail-closed boundary changed: {key}")
    if payload.get("frozen_gate_helpers_imported") != []:
        raise ADMInducedV552RedteamError("primary claims a frozen helper import")
    return payload


def sample_jet() -> dict[str, Any]:
    """A second, deterministic, non-diagonal, genuinely off-shell local jet."""

    return {
        "N": 1.29,
        "beta": np.asarray([-0.19, 0.14, 0.21]),
        "h": np.asarray(
            [[1.31, -0.12, 0.07], [-0.12, 1.09, 0.11], [0.07, 0.11, 1.24]]
        ),
        "p_cov": np.asarray(
            [
                [0.73, -0.44, 0.31],
                [-0.36, 0.57, 0.22],
                [0.48, 0.19, -0.41],
                [0.27, -0.33, 0.52],
            ]
        ),
        "p_normal": np.asarray([-0.18, 0.12, 0.23]),
        "Omega": 1.17,
        "psi": np.asarray([-0.29, 0.38, 0.24]),
        "a": np.asarray([0.08, -0.06, 0.13]),
        "Z": 1.0,
        "U": 0.31,
        "kappa": 1.0,
        "robin_y": math.sqrt(3.0),
    }


def _sym_basis(pair: tuple[int, int], size: int) -> np.ndarray:
    basis = np.zeros((size, size), dtype=float)
    i, j = pair
    basis[i, j] = 1.0
    basis[j, i] = 1.0
    return basis


def _sym_vector(matrix: np.ndarray, pairs: tuple[tuple[int, int], ...]) -> np.ndarray:
    return np.asarray([matrix[i, j] for i, j in pairs])


def _sym_matrix(vector: np.ndarray, pairs: tuple[tuple[int, int], ...], size: int) -> np.ndarray:
    matrix = np.zeros((size, size), dtype=np.asarray(vector).dtype)
    for value, (i, j) in zip(vector, pairs, strict=True):
        matrix[i, j] = value
        matrix[j, i] = value
    return matrix


def _complex_derivative(function: Callable[[complex], complex], step: float = 1.0e-27) -> float:
    return float(np.imag(function(1j * step)) / step)


def _five_point_vector(
    function: Callable[[float], np.ndarray], step: float = 2.0e-5
) -> np.ndarray:
    return (
        function(-2.0 * step)
        - 8.0 * function(-step)
        + 8.0 * function(step)
        - function(2.0 * step)
    ) / (12.0 * step)


def metric_from_adm(N: complex, beta: np.ndarray, h: np.ndarray) -> np.ndarray:
    dtype = np.result_type(N, beta, h)
    gamma = np.zeros((4, 4), dtype=dtype)
    gamma[1:, 1:] = h
    gamma[0, 1:] = h @ beta
    gamma[1:, 0] = gamma[0, 1:]
    gamma[0, 0] = -N * N + beta @ h @ beta
    return gamma


def adm_from_metric(gamma: np.ndarray) -> tuple[complex, np.ndarray, np.ndarray]:
    h = np.asarray(gamma[1:, 1:])
    beta = np.linalg.solve(h, np.asarray(gamma[0, 1:]))
    N = np.sqrt(-gamma[0, 0] + beta @ h @ beta)
    return N, beta, h


def tangent_metric(
    N: float, beta: np.ndarray, h: np.ndarray,
    n: float, b_shift: np.ndarray, q: np.ndarray,
) -> np.ndarray:
    H = np.zeros((4, 4), dtype=float)
    H[1:, 1:] = q
    H[0, 1:] = q @ beta + h @ b_shift
    H[1:, 0] = H[0, 1:]
    H[0, 0] = (
        -2.0 * N * N * n + beta @ q @ beta + 2.0 * beta @ h @ b_shift
    )
    return H


def inverse_tangent_metric(
    N: float, beta: np.ndarray, h: np.ndarray, H: np.ndarray,
) -> np.ndarray:
    q = np.asarray(H[1:, 1:])
    b_shift = np.linalg.solve(h, H[0, 1:] - q @ beta)
    n = (-H[0, 0] + beta @ q @ beta + 2.0 * beta @ h @ b_shift) / (
        2.0 * N * N
    )
    return np.concatenate(([n], b_shift, _sym_vector(q, SYM3)))


def _nonlinear_metric_along(data: Mapping[str, Any], direction: np.ndarray, s: complex) -> np.ndarray:
    N = data["N"] * np.exp(s * direction[0])
    beta = np.asarray(data["beta"]) + s * direction[1:4]
    h = np.asarray(data["h"]) + s * _sym_matrix(direction[4:], SYM3, 3)
    return metric_from_adm(N, beta, h)


def _direct_jacobian(data: Mapping[str, Any]) -> np.ndarray:
    columns = []
    for index in range(10):
        direction = np.zeros(10)
        direction[index] = 1.0
        columns.append(
            _sym_vector(
                np.imag(_nonlinear_metric_along(data, direction, 1j * 1.0e-27))
                / 1.0e-27,
                SYM4,
            )
        )
    return np.column_stack(columns)


def _inverse_jacobian(data: Mapping[str, Any], gamma: np.ndarray) -> np.ndarray:
    N0 = float(data["N"])
    beta0 = np.asarray(data["beta"])
    h0 = np.asarray(data["h"])

    def inverse_coordinates(varied: np.ndarray) -> np.ndarray:
        N, beta, h = adm_from_metric(varied)
        return np.concatenate(
            ([np.log(N / N0)], beta - beta0, _sym_vector(h - h0, SYM3))
        )

    columns = []
    for pair in SYM4:
        basis = _sym_basis(pair, 4)
        columns.append(
            _five_point_vector(lambda epsilon, B=basis: inverse_coordinates(gamma + epsilon * B))
        )
    return np.column_stack(columns)


def action_gamma(
    gamma: np.ndarray, Omega: complex, psi: np.ndarray, data: Mapping[str, Any],
    *, matter: bool = True, wall_robin: bool = True,
) -> complex:
    """Covariant route, written independently of the ADM action below."""

    gamma = np.asarray(gamma)
    inverse = np.linalg.inv(gamma)
    volume = np.sqrt(-np.linalg.det(gamma))
    lagrangian: complex = 0.0
    if matter:
        p = np.asarray(data["p_cov"])
        normal = np.asarray(data["p_normal"])
        contracted = np.einsum("mn,ma,na->", inverse, p, p)
        lagrangian += (
            -0.5 * data["Z"] * (contracted + normal @ normal) - data["U"]
        )
    if wall_robin:
        # Duplicated literally here so the two action representations do not
        # share a wall or Robin helper.
        W = 3.0 * np.exp(-1.2 * Omega * Omega / 6.0)
        V_sigma = 2.0 * W + (Omega - 1.0) ** 2
        h_inverse = np.linalg.inv(gamma[1:, 1:])
        r = np.asarray(psi) - data["robin_y"] * np.asarray(data["a"])
        lagrangian += -V_sigma - 0.5 * data["kappa"] * (r @ h_inverse @ r)
    return volume * lagrangian


def action_adm(
    N: complex, beta: np.ndarray, h: np.ndarray, Omega: complex,
    psi: np.ndarray, data: Mapping[str, Any],
    *, matter: bool = True, wall_robin: bool = True,
) -> complex:
    """Direct ADM route, intentionally not factored through action_gamma."""

    h = np.asarray(h)
    h_inverse = np.linalg.inv(h)
    volume = N * np.sqrt(np.linalg.det(h))
    lagrangian: complex = 0.0
    if matter:
        p = np.asarray(data["p_cov"])
        normal = np.asarray(data["p_normal"])
        p_u = (p[0] - np.einsum("i,ia->a", beta, p[1:])) / N
        spatial = np.einsum("ij,ia,ja->", h_inverse, p[1:], p[1:])
        lagrangian += (
            0.5 * data["Z"] * (p_u @ p_u)
            - 0.5 * data["Z"] * (spatial + normal @ normal)
            - data["U"]
        )
    if wall_robin:
        # This is a second literal implementation, not a call into the
        # covariant route or the primary gate.
        W_adm = 3.0 * np.exp(-1.2 * Omega * Omega / 6.0)
        wall_adm = 2.0 * W_adm + (Omega - 1.0) ** 2
        robin = np.asarray(psi) - data["robin_y"] * np.asarray(data["a"])
        lagrangian += -wall_adm - 0.5 * data["kappa"] * (
            robin @ h_inverse @ robin
        )
    return volume * lagrangian


def _gamma_gradient(data: Mapping[str, Any], *, matter: bool = True, wall_robin: bool = True) -> np.ndarray:
    gamma = metric_from_adm(data["N"], data["beta"], data["h"])
    values = []
    for pair in SYM4:
        basis = _sym_basis(pair, 4)
        values.append(
            _complex_derivative(
                lambda epsilon, B=basis: action_gamma(
                    gamma + epsilon * B, data["Omega"], data["psi"], data,
                    matter=matter, wall_robin=wall_robin,
                )
            )
        )
    return np.asarray(values)


def _adm_gradient(
    data: Mapping[str, Any], *, matter: bool = True, wall_robin: bool = True,
    fixed_varphi: np.ndarray | None = None,
) -> np.ndarray:
    values = []
    for index in range(10):
        direction = np.zeros(10)
        direction[index] = 1.0

        def varied(epsilon: complex) -> complex:
            N = data["N"] * np.exp(epsilon * direction[0])
            beta = np.asarray(data["beta"]) + epsilon * direction[1:4]
            h = np.asarray(data["h"]) + epsilon * _sym_matrix(direction[4:], SYM3, 3)
            psi = np.asarray(data["psi"]) if fixed_varphi is None else h @ fixed_varphi
            return action_adm(
                N, beta, h, data["Omega"], psi, data,
                matter=matter, wall_robin=wall_robin,
            )

        values.append(_complex_derivative(varied))
    return np.asarray(values)


def _tensor_from_gamma_gradient(gradient: np.ndarray, volume: float) -> np.ndarray:
    tensor = np.zeros((4, 4))
    for derivative, (i, j) in zip(gradient, SYM4, strict=True):
        tensor[i, j] = tensor[j, i] = derivative / volume * (2.0 if i == j else 1.0)
    return tensor


def _euler_from_adm_gradient(gradient: np.ndarray, volume: float) -> dict[str, Any]:
    E_h = np.zeros((3, 3))
    for derivative, (i, j) in zip(gradient[4:], SYM3, strict=True):
        E_h[i, j] = E_h[j, i] = derivative / volume / (2.0 if i != j else 1.0)
    return {
        "E_N": gradient[0] / volume,
        "E_shift": gradient[1:4] / volume,
        "E_h": E_h,
    }


def _dual_projections(tensor: np.ndarray, N: float, beta: np.ndarray, gamma: np.ndarray) -> dict[str, Any]:
    u_cov = np.asarray([-N, 0.0, 0.0, 0.0])
    slice_covectors = gamma[:, 1:]
    theta = np.vstack((beta, np.eye(3)))
    return {
        "uu": float(u_cov @ tensor @ u_cov),
        "ui": np.asarray(u_cov @ tensor @ slice_covectors),
        "spatial": np.asarray(theta.T @ tensor @ theta),
    }


def coordinate_ledger() -> dict[str, Any]:
    return {
        "n": "n=δN/N",
        "b_shift": "b_shift^i=δβ^i",
        "q": "q_ij=δh_ij",
        "omega": "omega=δOmegaSigma",
        "v": "v_i=δpsi_i",
        "metric_status": "(N,beta,h)=ADM(Y^*g,T), not autonomous fields",
        "primary_Robin_coordinate": "psi_i is fixed independently of h_ij",
        "BF_trace_disambiguation": "b_BF=iota^*B is not b_shift",
        "chain_identity": (
            "E_N n+E_shift_i b_shift^i+E_h^ij q_ij=(1/2)tau^mn H_mn"
        ),
    }


def induced_jacobian_certificate() -> dict[str, Any]:
    data = sample_jet()
    gamma = metric_from_adm(data["N"], data["beta"], data["h"])

    # A nontrivial immersion: E=[I;w].  The top block of the ambient metric
    # is chosen as gamma-w⊗w, so E^T g E=gamma without using an identity-only
    # reference embedding.
    w = np.asarray([0.08, -0.05, 0.06, 0.04])
    tangent = np.vstack((np.eye(4), w))
    ambient = np.zeros((5, 5))
    ambient[:4, :4] = gamma - np.outer(w, w)
    ambient[4, 4] = 1.0
    pulled_back = tangent.T @ ambient @ tangent

    J = _direct_jacobian(data)
    K = _inverse_jacobian(data, gamma)
    analytic_columns = []
    inverse_errors = []
    probes = np.asarray(
        [
            [0.11, -0.16, 0.07, 0.13, 0.18, -0.09, 0.05, -0.12, 0.08, 0.14],
            [-0.17, 0.10, 0.15, -0.06, -0.11, 0.04, 0.19, 0.07, -0.13, 0.09],
            [0.06, 0.21, -0.14, 0.12, 0.09, 0.16, -0.08, -0.05, 0.11, -0.18],
        ]
    )
    for index in range(10):
        direction = np.zeros(10)
        direction[index] = 1.0
        analytic_columns.append(
            _sym_vector(
                tangent_metric(
                    data["N"], data["beta"], data["h"], direction[0],
                    direction[1:4], _sym_matrix(direction[4:], SYM3, 3),
                ),
                SYM4,
            )
        )
    analytic_J = np.column_stack(analytic_columns)
    for probe in probes:
        H = tangent_metric(
            data["N"], data["beta"], data["h"], probe[0], probe[1:4],
            _sym_matrix(probe[4:], SYM3, 3),
        )
        inverse_errors.append(
            float(np.max(np.abs(inverse_tangent_metric(
                data["N"], data["beta"], data["h"], H,
            ) - probe)))
        )
    return {
        "ambient_dimension": 5,
        "embedding_tangent_last_row_norm": float(np.linalg.norm(w)),
        "ambient_metric_inertia": {
            "negative": int(np.sum(np.linalg.eigvalsh(ambient) < 0.0)),
            "positive": int(np.sum(np.linalg.eigvalsh(ambient) > 0.0)),
        },
        "Y_star_g_error": float(np.max(np.abs(pulled_back - gamma))),
        "ADM_roundtrip_error": float(np.max(np.abs(
            metric_from_adm(*adm_from_metric(gamma)) - gamma
        ))),
        "Jacobian_rank": int(np.linalg.matrix_rank(J)),
        "Jacobian_determinant": float(np.linalg.det(J)),
        "Jacobian_condition_number": float(np.linalg.cond(J)),
        "complex_step_vs_closed_tangent_error": float(np.max(np.abs(J - analytic_J))),
        "inverse_chart_left_error": float(np.max(np.abs(K @ J - np.eye(10)))),
        "inverse_chart_right_error": float(np.max(np.abs(J @ K - np.eye(10)))),
        "closed_inverse_probe_max_error": max(inverse_errors),
        "nonzero_shift_norm": float(np.linalg.norm(data["beta"])),
        "offdiagonal_metric_norm": float(np.linalg.norm(
            data["h"] - np.diag(np.diag(data["h"]))
        )),
    }


def action_chain_certificate() -> dict[str, Any]:
    data = sample_jet()
    gamma = metric_from_adm(data["N"], data["beta"], data["h"])
    volume = data["N"] * math.sqrt(float(np.linalg.det(data["h"])))
    J = _direct_jacobian(data)
    gamma_gradient = _gamma_gradient(data)
    adm_gradient = _adm_gradient(data)
    tau = _tensor_from_gamma_gradient(gamma_gradient, volume)
    euler = _euler_from_adm_gradient(adm_gradient, volume)
    projections = _dual_projections(tau, data["N"], data["beta"], gamma)

    directions = np.asarray(
        [
            [0.14, -0.08, 0.17, 0.05, 0.12, -0.10, 0.04, -0.07, 0.13, 0.09],
            [-0.20, 0.12, -0.04, 0.19, -0.08, 0.06, 0.11, 0.15, -0.02, -0.13],
            [0.07, 0.18, -0.15, -0.10, 0.17, 0.03, -0.12, 0.08, 0.10, -0.14],
        ]
    )
    pairing_errors = []
    for direction in directions:
        q = _sym_matrix(direction[4:], SYM3, 3)
        H = tangent_metric(
            data["N"], data["beta"], data["h"], direction[0], direction[1:4], q
        )
        left = volume * (
            euler["E_N"] * direction[0]
            + euler["E_shift"] @ direction[1:4]
            + np.sum(euler["E_h"] * q)
        )
        right = 0.5 * volume * np.sum(tau * H)
        pairing_errors.append(abs(left - right))

    projection_errors = [
        abs(projections["uu"] + euler["E_N"]),
        np.max(np.abs(projections["ui"] + data["N"] * euler["E_shift"])),
        np.max(np.abs(projections["spatial"] - 2.0 * euler["E_h"])),
    ]
    E_Omega = _complex_derivative(
        lambda epsilon: action_adm(
            data["N"], data["beta"], data["h"], data["Omega"] + epsilon,
            data["psi"], data,
        )
    ) / volume
    E_psi = np.asarray([
        _complex_derivative(
            lambda epsilon, i=i: action_adm(
                data["N"], data["beta"], data["h"], data["Omega"],
                data["psi"] + epsilon * np.eye(3)[i], data,
            )
        ) / volume
        for i in range(3)
    ])
    return {
        "gamma_action_value": float(np.real(action_gamma(
            gamma, data["Omega"], data["psi"], data
        ))),
        "ADM_action_value": float(np.real(action_adm(
            data["N"], data["beta"], data["h"], data["Omega"], data["psi"], data
        ))),
        "action_representation_error": float(abs(
            action_gamma(gamma, data["Omega"], data["psi"], data)
            - action_adm(data["N"], data["beta"], data["h"], data["Omega"], data["psi"], data)
        )),
        "ADM_vs_gamma_gradient_chain_error": float(np.max(np.abs(
            adm_gradient - J.T @ gamma_gradient
        ))),
        "directional_pairing_max_error": float(max(pairing_errors)),
        "projection_1_plus_3_plus_6_max_error": float(max(projection_errors)),
        "minimum_active_ADM_gradient": float(np.min(np.abs(adm_gradient))),
        "tau_norm": float(np.linalg.norm(tau)),
        "E_N": float(euler["E_N"]),
        "E_shift": euler["E_shift"].tolist(),
        "E_h": euler["E_h"].tolist(),
        "E_Omega": float(E_Omega),
        "E_psi": E_psi.tolist(),
        "tau": tau.tolist(),
        "genuinely_off_shell": bool(
            np.min(np.abs(adm_gradient)) > 1.0e-4
            and abs(E_Omega) > 1.0e-4
            and np.min(np.abs(E_psi)) > 1.0e-4
        ),
    }


def matter_shift_certificate() -> dict[str, Any]:
    data = sample_jet()
    gamma = metric_from_adm(data["N"], data["beta"], data["h"])
    inverse = np.linalg.inv(gamma)
    volume = data["N"] * math.sqrt(float(np.linalg.det(data["h"])))
    p = data["p_cov"]
    p_up = inverse @ p
    p_squared = np.einsum("mn,ma,na->", inverse, p, p) + data["p_normal"] @ data["p_normal"]
    L_matter = -0.5 * data["Z"] * p_squared - data["U"]
    T = data["Z"] * np.einsum("ma,na->mn", p_up, p_up) + L_matter * inverse
    u_cov = np.asarray([-data["N"], 0.0, 0.0, 0.0])
    T_ui = u_cov @ T @ gamma[:, 1:]
    expected = -T_ui / data["N"]
    numerical = _adm_gradient(data, matter=True, wall_robin=False)[1:4] / volume
    wall_numerical = _adm_gradient(data, matter=False, wall_robin=True)[1:4] / volume
    r = data["psi"] - data["robin_y"] * data["a"]
    fake = 0.41 * np.linalg.solve(data["h"], r)
    return {
        "T_ui_components": T_ui.tolist(),
        "T_ui_norm": float(np.linalg.norm(T_ui)),
        "minimum_absolute_T_ui_component": float(np.min(np.abs(T_ui))),
        "numerical_bulk_matter_E_shift": numerical.tolist(),
        "minus_T_ui_over_N_prediction": expected.tolist(),
        "matter_shift_error": float(np.max(np.abs(numerical - expected))),
        "omit_matter_current_witness": float(np.linalg.norm(numerical)),
        "flip_matter_current_sign_witness": float(np.linalg.norm(numerical + expected)),
        "wall_Robin_direct_shift_components": wall_numerical.tolist(),
        "wall_Robin_direct_shift_norm": float(np.linalg.norm(wall_numerical)),
        "fake_wall_Robin_shift_current": fake.tolist(),
        "fake_wall_Robin_shift_current_witness": float(np.linalg.norm(fake)),
    }


def psi_coordinate_certificate() -> dict[str, Any]:
    """Observe the coordinate term from two action derivatives; do not assume it."""

    data = sample_jet()
    volume = data["N"] * math.sqrt(float(np.linalg.det(data["h"])))
    varphi = np.linalg.solve(data["h"], data["psi"])
    fixed_psi = _euler_from_adm_gradient(_adm_gradient(data), volume)["E_h"]
    fixed_varphi = _euler_from_adm_gradient(
        _adm_gradient(data, fixed_varphi=varphi), volume
    )["E_h"]
    E_psi = np.asarray([
        _complex_derivative(
            lambda epsilon, i=i: action_adm(
                data["N"], data["beta"], data["h"], data["Omega"],
                data["psi"] + epsilon * np.eye(3)[i], data,
            )
        ) / volume
        for i in range(3)
    ])
    observed = fixed_varphi - fixed_psi
    independently_predicted = 0.5 * (
        np.outer(E_psi, varphi) + np.outer(varphi, E_psi)
    )
    return {
        "fixed_coordinate": "psi_i",
        "varphi_defined_afterwards_as": "varphi^i=h^ij psi_j",
        "E_psi_from_action": E_psi.tolist(),
        "observed_fixed_varphi_minus_fixed_psi": observed.tolist(),
        "independent_coordinate_prediction": independently_predicted.tolist(),
        "coordinate_chain_error": float(np.max(np.abs(
            observed - independently_predicted
        ))),
        "coordinate_term_norm": float(np.linalg.norm(observed)),
        "omit_coordinate_term_witness": float(np.linalg.norm(observed)),
        "flip_coordinate_term_witness": float(np.linalg.norm(
            observed + independently_predicted
        )),
    }


def _reconstruct_tensor_from_projections(
    uu: float, ui: np.ndarray, spatial: np.ndarray,
    data: Mapping[str, Any], J: np.ndarray,
) -> np.ndarray:
    volume = data["N"] * math.sqrt(float(np.linalg.det(data["h"])))
    E_N = -uu
    E_shift = -np.asarray(ui) / data["N"]
    E_h = 0.5 * np.asarray(spatial)
    slots = np.zeros(10)
    slots[0] = volume * E_N
    slots[1:4] = volume * E_shift
    for index, (i, j) in enumerate(SYM3, start=4):
        slots[index] = volume * E_h[i, j] * (2.0 if i != j else 1.0)
    gamma_gradient = np.linalg.solve(J.T, slots)
    return _tensor_from_gamma_gradient(gamma_gradient, volume)


def israel_certificate() -> dict[str, Any]:
    data = sample_jet()
    gamma = metric_from_adm(data["N"], data["beta"], data["h"])
    volume = data["N"] * math.sqrt(float(np.linalg.det(data["h"])))
    tau = _tensor_from_gamma_gradient(_gamma_gradient(data), volume)
    inverse = np.linalg.inv(gamma)
    Theta = np.asarray(
        [
            [0.09, -0.028, 0.037, -0.016],
            [-0.028, -0.061, 0.021, 0.014],
            [0.037, 0.021, 0.074, -0.023],
            [-0.016, 0.014, -0.023, -0.047],
        ]
    )
    trace = np.sum(inverse * Theta)
    pi = inverse @ Theta @ inverse - trace * inverse
    M = 1.63
    junction = M * pi - tau
    projections = _dual_projections(junction, data["N"], data["beta"], gamma)
    J = _direct_jacobian(data)
    reconstructed = _reconstruct_tensor_from_projections(
        projections["uu"], projections["ui"], projections["spatial"], data, J
    )
    slot_mutants = {}
    for name, values in {
        "omit_1_lapse_projection": (0.0, projections["ui"], projections["spatial"]),
        "omit_3_shift_projections": (projections["uu"], np.zeros(3), projections["spatial"]),
        "omit_6_spatial_projections": (projections["uu"], projections["ui"], np.zeros((3, 3))),
        "flip_all_projection_signs": (-projections["uu"], -projections["ui"], -projections["spatial"]),
    }.items():
        wrong = _reconstruct_tensor_from_projections(*values, data, J)
        slot_mutants[name] = float(np.linalg.norm(wrong - junction))
    autonomous = _reconstruct_tensor_from_projections(
        projections["uu"], projections["ui"], projections["spatial"], data, np.eye(10)
    )
    wrong_pi_junction = -M * pi - tau
    return {
        "Brown_York_convention": "pi^mn=Theta^mn-Theta gamma^mn",
        "junction_convention": "I^mn=M pi^mn-tau^mn",
        "Jacobian_rank": int(np.linalg.matrix_rank(J)),
        "tau_norm": float(np.linalg.norm(tau)),
        "Brown_York_norm": float(np.linalg.norm(pi)),
        "junction_norm": float(np.linalg.norm(junction)),
        "projection_component_count": 10,
        "projection_reconstruction_error": float(np.max(np.abs(
            reconstructed - junction
        ))),
        "slot_mutant_witnesses": slot_mutants,
        "autonomous_metric_mutant_witness": float(np.linalg.norm(
            autonomous - junction
        )),
        "Brown_York_sign_mutant_witness": float(np.linalg.norm(
            wrong_pi_junction - junction
        )),
        "Theta": Theta.tolist(),
        "tau": tau.tolist(),
        "pi": pi.tolist(),
        "junction": junction.tolist(),
    }


def normal_embedding_certificate() -> dict[str, Any]:
    data = sample_jet()
    gamma = metric_from_adm(data["N"], data["beta"], data["h"])
    volume = data["N"] * math.sqrt(float(np.linalg.det(data["h"])))
    israel = israel_certificate()
    Theta = np.asarray(israel["Theta"])
    junction = np.asarray(israel["junction"])
    f = -0.36
    curvature2 = np.asarray(
        [
            [0.04, 0.01, -0.008, 0.006],
            [0.01, -0.02, 0.007, 0.003],
            [-0.008, 0.007, 0.03, -0.005],
            [0.006, 0.003, -0.005, -0.01],
        ]
    )

    def induced_metric(s: float) -> np.ndarray:
        r = s * f
        # Gaussian-normal ambient family and Y_s=(sigma,r=s f).
        return gamma + 2.0 * r * Theta + r * r * curvature2

    H_numerical = _five_point_vector(induced_metric)
    H_expected = 2.0 * f * Theta
    normal_residual = float(np.sum(junction * Theta))
    direct_pairing = -0.5 * volume * float(np.sum(junction * H_numerical))
    normal_pairing = -volume * f * normal_residual
    return {
        "embedding_family": "Y_s(sigma)=(sigma,r=s f) in Gaussian-normal ambient metric",
        "normal_metric_identity": "H_mn=2 f Theta_mn",
        "f_bend": f,
        "H_identity_error": float(np.max(np.abs(H_numerical - H_expected))),
        "H_norm": float(np.linalg.norm(H_numerical)),
        "I_contract_Theta": normal_residual,
        "I_contract_Theta_absolute": abs(normal_residual),
        "direct_metric_Green_pairing": direct_pairing,
        "normal_equation_pairing": normal_pairing,
        "normal_pairing_error": abs(direct_pairing - normal_pairing),
        "omit_normal_bending_witness": float(np.linalg.norm(H_numerical)),
        "flip_normal_bending_sign_witness": float(np.linalg.norm(
            H_numerical + H_expected
        )),
        "full_all_field_normal_embedding_claimed": False,
        "still_missing_for_full_all_field_normal_embedding": (
            "two-sided normal momenta and transport of Omega, phi, A, B, T, "
            "plus derivative EH/GHY and corner Green data"
        ),
    }


def mutation_certificate() -> dict[str, float]:
    data = sample_jet()
    J = _direct_jacobian(data)
    gamma_gradient = _gamma_gradient(data)
    adm_gradient = _adm_gradient(data)
    wrong_lapse = J.copy()
    wrong_lapse[:, 0] *= -1.0
    omit_q_beta = J.copy()
    # q columns must feed H_00 and H_0i when beta is nonzero.
    omit_q_beta[0:4, 4:] = 0.0
    offdiag_wrong = gamma_gradient.copy()
    for index, (i, j) in enumerate(SYM4):
        if i != j:
            offdiag_wrong[index] *= 2.0
    matter = matter_shift_certificate()
    psi = psi_coordinate_certificate()
    israel = israel_certificate()
    normal = normal_embedding_certificate()
    witnesses = {
        "Jacobian_flip_lapse_sign": float(np.linalg.norm(J - wrong_lapse)),
        "Jacobian_omit_q_beta_terms": float(np.linalg.norm(J - omit_q_beta)),
        "Jacobian_autonomize_gamma_and_ADM": float(np.linalg.norm(J - np.eye(10))),
        "chain_flip_gamma_route_sign": float(np.linalg.norm(
            adm_gradient + J.T @ gamma_gradient
        )),
        "chain_omit_shift_slot": float(np.linalg.norm(
            np.concatenate((adm_gradient[:1], np.zeros(3), adm_gradient[4:]))
            - J.T @ gamma_gradient
        )),
        "chain_omit_metric_slots": float(np.linalg.norm(
            np.concatenate((adm_gradient[:4], np.zeros(6))) - J.T @ gamma_gradient
        )),
        "chain_double_offdiagonal_gamma_slots": float(np.linalg.norm(
            adm_gradient - J.T @ offdiag_wrong
        )),
        "matter_omit_T_ui": matter["omit_matter_current_witness"],
        "matter_flip_T_ui_sign": matter["flip_matter_current_sign_witness"],
        "Robin_fake_shift_current": matter["fake_wall_Robin_shift_current_witness"],
        "psi_omit_coordinate_term": psi["omit_coordinate_term_witness"],
        "psi_flip_coordinate_term": psi["flip_coordinate_term_witness"],
        "Israel_autonomous_metric": israel["autonomous_metric_mutant_witness"],
        "Israel_Brown_York_sign": israel["Brown_York_sign_mutant_witness"],
        "normal_omit_2fTheta": normal["omit_normal_bending_witness"],
        "normal_flip_2fTheta_sign": normal["flip_normal_bending_sign_witness"],
    }
    witnesses.update({f"Israel_{key}": value for key, value in israel["slot_mutant_witnesses"].items()})
    return witnesses


def _decision(
    lineage: Mapping[str, Any], jacobian: Mapping[str, Any], chain: Mapping[str, Any],
    matter: Mapping[str, Any], psi: Mapping[str, Any], israel: Mapping[str, Any],
    normal: Mapping[str, Any], mutants: Mapping[str, float],
) -> dict[str, bool]:
    ledger = coordinate_ledger()
    decision = {
        "independent_primary_lineage_pass": bool(
            lineage.get("schema") == PRIMARY_SCHEMA
            and lineage.get("decision", {}).get("candidate_checks_pass") is True
        ),
        "explicit_coordinate_contract_pass": bool(
            ledger["n"] == "n=δN/N"
            and ledger["b_shift"] == "b_shift^i=δβ^i"
            and ledger["q"] == "q_ij=δh_ij"
            and ledger["omega"] == "omega=δOmegaSigma"
            and ledger["v"] == "v_i=δpsi_i"
            and "not autonomous" in ledger["metric_status"]
        ),
        "nontrivial_induced_pullback_pass": bool(
            jacobian["embedding_tangent_last_row_norm"] > 1.0e-2
            and jacobian["ambient_metric_inertia"] == {"negative": 1, "positive": 4}
            and jacobian["Y_star_g_error"] < 2.0e-14
            and jacobian["ADM_roundtrip_error"] < 2.0e-14
        ),
        "bidirectional_ADM_Jacobian_rank10_pass": bool(
            jacobian["Jacobian_rank"] == 10
            and jacobian["complex_step_vs_closed_tangent_error"] < 2.0e-13
            and jacobian["inverse_chart_left_error"] < 2.0e-9
            and jacobian["inverse_chart_right_error"] < 2.0e-9
            and jacobian["closed_inverse_probe_max_error"] < 2.0e-14
        ),
        "independent_action_routes_chain_pass": bool(
            chain["action_representation_error"] < 2.0e-13
            and chain["ADM_vs_gamma_gradient_chain_error"] < 2.0e-10
            and chain["directional_pairing_max_error"] < 2.0e-10
            and chain["projection_1_plus_3_plus_6_max_error"] < 2.0e-10
            and chain["minimum_active_ADM_gradient"] > 1.0e-4
            and chain["genuinely_off_shell"] is True
        ),
        "unique_Israel_Brown_York_reconstruction_pass": bool(
            israel["Jacobian_rank"] == 10
            and israel["projection_component_count"] == 10
            and israel["projection_reconstruction_error"] < 2.0e-10
            and israel["junction_norm"] > 1.0e-3
        ),
        "normal_embedding_metric_pairing_pass": bool(
            normal["H_identity_error"] < 2.0e-11
            and normal["normal_pairing_error"] < 2.0e-11
            and normal["I_contract_Theta_absolute"] > 1.0e-4
            and normal["full_all_field_normal_embedding_claimed"] is False
        ),
        "matter_shift_T_ui_visible_pass": bool(
            matter["minimum_absolute_T_ui_component"] > 1.0e-3
            and matter["matter_shift_error"] < 2.0e-10
        ),
        "wall_Robin_shift_neutral_pass": bool(
            matter["wall_Robin_direct_shift_norm"] < 2.0e-13
            and matter["fake_wall_Robin_shift_current_witness"] > 1.0e-3
        ),
        "psi_coordinate_chain_observed_pass": bool(
            psi["fixed_coordinate"] == "psi_i"
            and psi["coordinate_chain_error"] < 2.0e-10
            and psi["coordinate_term_norm"] > 1.0e-4
        ),
        "off_shell_independent_mutants_pass": bool(
            len(mutants) >= 20 and min(mutants.values()) > 1.0e-5
        ),
    }
    decision["independent_redteam_checks_pass"] = all(decision.values())
    for key in FAIL_CLOSED_KEYS:
        decision[key] = False
    return decision


def build_payload() -> dict[str, Any]:
    primary = _load_primary()
    jacobian = induced_jacobian_certificate()
    chain = action_chain_certificate()
    matter = matter_shift_certificate()
    psi = psi_coordinate_certificate()
    israel = israel_certificate()
    normal = normal_embedding_certificate()
    mutants = mutation_certificate()
    decision = _decision(primary, jacobian, chain, matter, psi, israel, normal, mutants)
    if decision["independent_redteam_checks_pass"] is not True:
        raise ADMInducedV552RedteamError("independent red-team checks did not all pass")
    if any(decision[key] is not False for key in FAIL_CLOSED_KEYS):
        raise ADMInducedV552RedteamError("red-team fail-closed boundary changed")
    ledger = coordinate_ledger()
    return {
        "schema": SCHEMA,
        "claim": (
            "Independent reproduction of the selected local induced-ADM chain; "
            "not an all-field normal theorem and not a C1/N1/B4 promotion."
        ),
        "primary_helpers_imported": [],
        "coordinate_ledger_sha256": _canonical_sha256(ledger),
        "coordinate_ledger": ledger,
        "pinned_primary_v5_5_2": {
            "schema": PRIMARY_SCHEMA,
            "generator_sha256": EXPECTED_PRIMARY_GENERATOR_SHA256,
            "test_sha256": EXPECTED_PRIMARY_TEST_SHA256,
            "artifact_sha256": EXPECTED_PRIMARY_ARTIFACT_SHA256,
            "v5_2_artifact_sha256": EXPECTED_V5_2_SHA256,
        },
        "certificates": {
            "nontrivial_induced_pullback_and_ADM_Jacobian": jacobian,
            "one_action_two_independent_routes": chain,
            "bulk_matter_shift_and_wall_Robin": matter,
            "psi_coordinate_observation": psi,
            "single_Israel_Brown_York_tensor": israel,
            "normal_embedding_metric_subsector": normal,
            "independent_mutant_witnesses": mutants,
        },
        "decision": decision,
        "scope_boundary": {
            "proved": (
                "selected local SO(3)-matter/wall/Robin metric action, induced ADM "
                "chain, unique 1+3+6 junction tensor, and metric normal pairing"
            ),
            "still_red": (
                "complete v5.2 derivative action and all pulled-back field normal "
                "momenta; C1, N1, N4, B4, and B5"
            ),
        },
        "provenance": {
            "generator": str(Path(__file__).resolve().relative_to(HERE.parents[1])),
            "generator_sha256": _sha256(Path(__file__).resolve()),
            "test": str(TEST.resolve().relative_to(HERE.parents[1])),
            "test_sha256": _sha256(TEST),
            "numpy": np.__version__,
            "deterministic_seed_used": False,
        },
    }


def main() -> int:
    payload = build_payload()
    _write(OUTPUT, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
