#!/usr/bin/env python3
"""Additive v5.5.2 certificate for the induced-metric/ADM chain rule.

This gate is deliberately self-contained.  It does not import a frozen v5.5
or v5.6 helper and it does not promote C1, N1, or B4.  Its job is narrower:
show, on a genuinely off-shell Lorentzian jet, that one real local action has
the same first variation when differentiated in ADM variables and when
differentiated in the ten covariant metric components; reconstruct the unique
stress/junction tensor; and connect that result to an induced bending family.

The executed action contains the covariant SO(3)-matter kinetic term and the
wall/Robin terms relevant to the missing shift witness.  It is not a new
certificate for all derivative terms of the frozen v5.2 action.  In
particular, the complete normal equation also needs the two-sided bulk trace
momenta for every pulled-back field, so that larger claim remains fail closed.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
V5_2_PATH = HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
OUTPUT = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.json"
)
TEST = HERE / "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py"
SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-gate.v1"
EXPECTED_V5_2_SHA256 = (
    "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b"
)
EXPECTED_V5_2_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
EXPECTED_V5_2_COEFFICIENTS = {
    "M5_cubed": 1.0,
    "compensator_metric_G": 1.2,
    "material_Z5_per_side": 1.0,
    "material_mass_M": 1.0,
    "k_infinity": 1.0,
    "brane_beta": 2.0,
    "Robin_kappa_hat": 1.0,
    "Robin_y": math.sqrt(3.0),
}
EXPECTED_V5_2_ACTIONS = {
    "bulk_gauged": (
        "S_bulk_gauged=sum_eps int_Meps sqrt(-g_eps)*[M5^3*R_eps/2-"
        "G*(nabla Omega_eps)^2/2-U(Omega_eps)-"
        "Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2-"
        "Z5*M^2*Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)]"
    ),
    "wall_background": (
        "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+"
        "beta*(Omega_Sigma-1)^2/2]"
    ),
    "Robin_intrinsic": (
        "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*"
        "h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)"
    ),
}
EXPECTED_FORMULA_LEDGER_SHA256 = (
    "e7c699c75e5507865d5db555c7a9094eb6d610988592abd935586beff5134a16"
)

SYM4 = (
    (0, 0), (0, 1), (0, 2), (0, 3), (1, 1),
    (1, 2), (1, 3), (2, 2), (2, 3), (3, 3),
)
SYM3 = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
SLOT_NAMES = (
    "n", "b_shift^1", "b_shift^2", "b_shift^3", "q_11",
    "q_12", "q_13", "q_22", "q_23", "q_33",
)

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
ALLOWED_TRUE_PASS_KEYS = {
    "literal_slot_coordinate_contract_pass",
    "induced_ADM_bidirectional_Jacobian_pass",
    "one_action_independent_gamma_ADM_chain_pass",
    "single_Israel_Brown_York_tensor_reconstruction_pass",
    "metric_bending_normal_subsector_pass",
    "bulk_matter_shift_momentum_witness_pass",
    "wall_Robin_no_direct_shift_pass",
    "psi_varphi_total_chain_pass",
    "off_shell_mutation_suite_pass",
    "candidate_checks_pass",
}


class ADMChainV552Error(ValueError):
    """The additive ADM/induced-metric certificate is malformed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ADMChainV552Error(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def _load_v5_2(
    path: Path = V5_2_PATH,
    expected_sha256: str = EXPECTED_V5_2_SHA256,
) -> tuple[dict[str, Any], dict[str, float], dict[str, str]]:
    """Load and independently validate only the v5.2 data used here."""

    if _sha256(path) != expected_sha256:
        raise ADMChainV552Error("v5.2 artifact byte hash mismatch")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ADMChainV552Error(f"cannot read v5.2 artifact: {exc}") from exc
    if type(payload) is not dict or payload.get("schema") != EXPECTED_V5_2_SCHEMA:
        raise ADMChainV552Error("v5.2 artifact schema mismatch")
    try:
        coefficient_raw = payload["exact_classical_charter"]["coefficient_policy"][
            "parameters"
        ]
        action_raw = payload["exact_classical_charter"]["exact_action"]
        coefficients = {
            key: float(coefficient_raw[key]) for key in EXPECTED_V5_2_COEFFICIENTS
        }
        actions = {key: str(action_raw[key]) for key in EXPECTED_V5_2_ACTIONS}
    except (KeyError, TypeError, ValueError) as exc:
        raise ADMChainV552Error("v5.2 coefficient/action contract missing") from exc
    if coefficients != EXPECTED_V5_2_COEFFICIENTS:
        raise ADMChainV552Error("v5.2 coefficient contract mismatch")
    if actions != EXPECTED_V5_2_ACTIONS:
        raise ADMChainV552Error("v5.2 literal action contract mismatch")
    return payload, coefficients, actions


V5_2, V5_2_COEFF, V5_2_ACTION = _load_v5_2()


def _five_point(function: Callable[[float], float], step: float = 2.0e-5) -> float:
    """Fourth-order centred first derivative, with no shared analytic helper."""

    return float(
        (
            function(-2.0 * step)
            - 8.0 * function(-step)
            + 8.0 * function(step)
            - function(2.0 * step)
        )
        / (12.0 * step)
    )


def _five_point_matrix(
    function: Callable[[float], np.ndarray], step: float = 2.0e-5
) -> np.ndarray:
    return (
        function(-2.0 * step)
        - 8.0 * function(-step)
        + 8.0 * function(step)
        - function(2.0 * step)
    ) / (12.0 * step)


def _sym_matrix(vector: np.ndarray, pairs: tuple[tuple[int, int], ...], n: int) -> np.ndarray:
    matrix = np.zeros((n, n), dtype=float)
    for value, (i, j) in zip(np.asarray(vector, dtype=float), pairs, strict=True):
        matrix[i, j] = value
        matrix[j, i] = value
    return matrix


def _sym_vector(matrix: np.ndarray, pairs: tuple[tuple[int, int], ...]) -> np.ndarray:
    return np.asarray([float(matrix[i, j]) for i, j in pairs], dtype=float)


def sample_jet() -> dict[str, Any]:
    """A deterministic, curved-coordinate, non-static, genuinely off-shell jet."""

    return {
        "N": 1.37,
        "beta": np.asarray([0.23, -0.17, 0.11], dtype=float),
        "h": np.asarray(
            [[1.42, 0.13, -0.08], [0.13, 1.18, 0.09], [-0.08, 0.09, 0.96]],
            dtype=float,
        ),
        "p_cov": np.asarray(
            [
                [0.80, -0.35, 0.27],
                [0.41, 0.22, -0.31],
                [-0.29, 0.53, 0.18],
                [0.37, -0.26, 0.49],
            ],
            dtype=float,
        ),
        "p_normal": np.asarray([0.21, -0.16, 0.09], dtype=float),
        "phi": np.asarray([0.31, -0.22, 0.18], dtype=float),
        "psi": np.asarray([0.34, -0.28, 0.19], dtype=float),
        "a": np.asarray([0.07, 0.11, -0.09], dtype=float),
        "Omega": 1.24,
        "Z": V5_2_COEFF["material_Z5_per_side"],
        "kappa": V5_2_COEFF["Robin_kappa_hat"],
        "robin_y": V5_2_COEFF["Robin_y"],
    }


def adm_metric(N: float, beta: np.ndarray, h: np.ndarray) -> np.ndarray:
    """gamma_{mu nu} in the (-,+,+,+) ADM chart."""

    gamma = np.zeros((4, 4), dtype=float)
    gamma[1:, 1:] = h
    gamma[0, 1:] = h @ beta
    gamma[1:, 0] = gamma[0, 1:]
    gamma[0, 0] = -N * N + float(beta @ h @ beta)
    return gamma


def decompose_adm(gamma: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    """Algebraic inverse gamma -> (N,beta,h), not an independent metric model."""

    h = np.asarray(gamma[1:, 1:], dtype=float)
    beta = np.linalg.solve(h, np.asarray(gamma[0, 1:], dtype=float))
    lapse_squared = -float(gamma[0, 0]) + float(beta @ h @ beta)
    if lapse_squared <= 0.0 or np.min(np.linalg.eigvalsh(h)) <= 0.0:
        raise ADMChainV552Error("metric left the Lorentzian ADM chart")
    return math.sqrt(lapse_squared), beta, h


def adm_variation(
    N: float,
    beta: np.ndarray,
    h: np.ndarray,
    n: float,
    b_shift: np.ndarray,
    q: np.ndarray,
) -> np.ndarray:
    """Exact tangent H=d gamma for n=dN/N, b=d beta, q=d h."""

    H = np.zeros((4, 4), dtype=float)
    H[1:, 1:] = q
    H[0, 1:] = q @ beta + h @ b_shift
    H[1:, 0] = H[0, 1:]
    H[0, 0] = (
        -2.0 * N * N * n
        + float(beta @ q @ beta)
        + 2.0 * float(beta @ h @ b_shift)
    )
    return H


def inverse_adm_variation(
    N: float, beta: np.ndarray, h: np.ndarray, H: np.ndarray
) -> tuple[float, np.ndarray, np.ndarray]:
    """Exact inverse tangent (n,b,q) from a symmetric H_{mu nu}."""

    q = np.asarray(H[1:, 1:], dtype=float)
    b_shift = np.linalg.solve(h, np.asarray(H[0, 1:], dtype=float) - q @ beta)
    n = (
        -float(H[0, 0])
        + float(beta @ q @ beta)
        + 2.0 * float(beta @ h @ b_shift)
    ) / (2.0 * N * N)
    return n, b_shift, q


def adm_jacobian(N: float, beta: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Ten-by-ten Jacobian d gamma_sym / d(n,b_shift,q)."""

    columns: list[np.ndarray] = []
    for k in range(10):
        n = 1.0 if k == 0 else 0.0
        b_shift = np.zeros(3, dtype=float)
        if 1 <= k <= 3:
            b_shift[k - 1] = 1.0
        q = np.zeros((3, 3), dtype=float)
        if k >= 4:
            i, j = SYM3[k - 4]
            q[i, j] = 1.0
            q[j, i] = 1.0
        columns.append(_sym_vector(adm_variation(N, beta, h, n, b_shift, q), SYM4))
    return np.column_stack(columns)


def _superpotential(Omega: float) -> float:
    M5_cubed = V5_2_COEFF["M5_cubed"]
    k_infinity = V5_2_COEFF["k_infinity"]
    G = V5_2_COEFF["compensator_metric_G"]
    return 3.0 * M5_cubed * k_infinity * math.exp(
        -G * Omega * Omega / (6.0 * M5_cubed)
    )


def _bulk_potential(Omega: float, data: Mapping[str, Any]) -> float:
    """Literal U(Omega)+Z M^2 Omega^-5 V4(Omega^(3/2)|phi|)."""

    M5_cubed = V5_2_COEFF["M5_cubed"]
    G = V5_2_COEFF["compensator_metric_G"]
    Z = V5_2_COEFF["material_Z5_per_side"]
    mass = V5_2_COEFF["material_mass_M"]
    W = _superpotential(Omega)
    dW = -(G * Omega / (3.0 * M5_cubed)) * W
    U = dW * dW / (2.0 * G) - 2.0 * W * W / (3.0 * M5_cubed)
    rho = float(np.linalg.norm(np.asarray(data["phi"])))
    s = Omega**1.5 * rho
    V4 = s**4 / (2.0 * math.sqrt(1.0 + s**4))
    return U + Z * mass * mass * Omega**-5.0 * V4


def _wall(Omega: float) -> float:
    beta_wall = V5_2_COEFF["brane_beta"]
    return 2.0 * _superpotential(Omega) + 0.5 * beta_wall * (Omega - 1.0) ** 2


def action_adm(
    N: float,
    beta: np.ndarray,
    h: np.ndarray,
    Omega: float,
    psi: np.ndarray,
    data: Mapping[str, Any],
    *,
    matter: bool = True,
    wall_robin: bool = True,
) -> float:
    """The selected real action density written directly in ADM variables."""

    h_inverse = np.linalg.inv(h)
    volume = N * math.sqrt(float(np.linalg.det(h)))
    lagrangian = 0.0
    if matter:
        p_cov = np.asarray(data["p_cov"])
        p_normal = np.asarray(data["p_normal"])
        p_u = (p_cov[0] - np.einsum("i,ia->a", beta, p_cov[1:])) / N
        spatial_norm = float(np.einsum("ij,ia,ja->", h_inverse, p_cov[1:], p_cov[1:]))
        lagrangian += (
            0.5 * float(data["Z"]) * float(p_u @ p_u)
            - 0.5 * float(data["Z"]) * spatial_norm
            - 0.5 * float(data["Z"]) * float(p_normal @ p_normal)
            - _bulk_potential(Omega, data)
        )
    if wall_robin:
        r = np.asarray(psi) - float(data["robin_y"]) * np.asarray(data["a"])
        lagrangian += -_wall(Omega) - 0.5 * float(data["kappa"]) * float(r @ h_inverse @ r)
    return volume * lagrangian


def action_gamma(
    gamma: np.ndarray,
    Omega: float,
    psi: np.ndarray,
    data: Mapping[str, Any],
    *,
    matter: bool = True,
    wall_robin: bool = True,
) -> float:
    """The same action, independently written in ten gamma components."""

    determinant = float(np.linalg.det(gamma))
    if determinant >= 0.0:
        raise ADMChainV552Error("covariant route left Lorentzian signature")
    volume = math.sqrt(-determinant)
    gamma_inverse = np.linalg.inv(gamma)
    lagrangian = 0.0
    if matter:
        p_cov = np.asarray(data["p_cov"])
        p_normal = np.asarray(data["p_normal"])
        covariant_norm = float(np.einsum("mn,ma,na->", gamma_inverse, p_cov, p_cov))
        lagrangian += (
            -0.5 * float(data["Z"]) *
            (covariant_norm + float(p_normal @ p_normal))
            - _bulk_potential(Omega, data)
        )
    if wall_robin:
        _, _, h = decompose_adm(gamma)
        r = np.asarray(psi) - float(data["robin_y"]) * np.asarray(data["a"])
        lagrangian += -_wall(Omega) - 0.5 * float(data["kappa"]) * float(
            r @ np.linalg.inv(h) @ r
        )
    return volume * lagrangian


def _gamma_gradient(
    gamma: np.ndarray,
    Omega: float,
    psi: np.ndarray,
    data: Mapping[str, Any],
    *,
    matter: bool = True,
    wall_robin: bool = True,
) -> np.ndarray:
    derivatives = []
    for pair in SYM4:
        basis = np.zeros((4, 4), dtype=float)
        i, j = pair
        basis[i, j] = 1.0
        basis[j, i] = 1.0
        derivatives.append(
            _five_point(
                lambda epsilon, basis=basis: action_gamma(
                    gamma + epsilon * basis,
                    Omega,
                    psi,
                    data,
                    matter=matter,
                    wall_robin=wall_robin,
                )
            )
        )
    return np.asarray(derivatives, dtype=float)


def _tau_from_gamma_gradient(gradient: np.ndarray, volume: float) -> np.ndarray:
    tau = np.zeros((4, 4), dtype=float)
    for derivative, (i, j) in zip(gradient, SYM4, strict=True):
        value = (2.0 if i == j else 1.0) * float(derivative) / volume
        tau[i, j] = value
        tau[j, i] = value
    return tau


def _gamma_gradient_from_tau(tau: np.ndarray, volume: float) -> np.ndarray:
    return np.asarray(
        [
            (0.5 * volume if i == j else volume) * float(tau[i, j])
            for i, j in SYM4
        ],
        dtype=float,
    )


def _adm_gradient(
    data: Mapping[str, Any],
    *,
    fixed_varphi: np.ndarray | None = None,
    matter: bool = True,
    wall_robin: bool = True,
) -> np.ndarray:
    N = float(data["N"])
    beta = np.asarray(data["beta"])
    h = np.asarray(data["h"])
    Omega = float(data["Omega"])
    psi = np.asarray(data["psi"])
    derivatives: list[float] = []
    for k in range(10):
        direction = np.zeros(10, dtype=float)
        direction[k] = 1.0

        def varied(epsilon: float) -> float:
            varied_N = N * math.exp(epsilon * direction[0])
            varied_beta = beta + epsilon * direction[1:4]
            varied_h = h + epsilon * _sym_matrix(direction[4:], SYM3, 3)
            varied_psi = psi if fixed_varphi is None else varied_h @ fixed_varphi
            return action_adm(
                varied_N,
                varied_beta,
                varied_h,
                Omega,
                varied_psi,
                data,
                matter=matter,
                wall_robin=wall_robin,
            )

        derivatives.append(_five_point(varied))
    return np.asarray(derivatives, dtype=float)


def _adm_euler_from_gradient(gradient: np.ndarray, volume: float) -> dict[str, np.ndarray | float]:
    E_h = np.zeros((3, 3), dtype=float)
    for derivative, (i, j) in zip(gradient[4:], SYM3, strict=True):
        value = float(derivative) / (volume * (2.0 if i != j else 1.0))
        E_h[i, j] = value
        E_h[j, i] = value
    return {
        "E_N": float(gradient[0]) / volume,
        "E_shift": np.asarray(gradient[1:4], dtype=float) / volume,
        "E_h": E_h,
    }


def _metric_projections(
    tensor: np.ndarray, N: float, beta: np.ndarray, gamma: np.ndarray
) -> dict[str, np.ndarray | float]:
    """Projections dual to exactly the declared ADM tangent coordinates."""

    u_cov = np.asarray([-N, 0.0, 0.0, 0.0], dtype=float)
    spatial_metric_covectors = gamma[:, 1:]
    theta = np.vstack([beta, np.eye(3)])
    return {
        "uu": float(u_cov @ tensor @ u_cov),
        "ui": np.asarray(u_cov @ tensor @ spatial_metric_covectors, dtype=float),
        "spatial": np.asarray(theta.T @ tensor @ theta, dtype=float),
    }


def _tensor_from_adm_projections(
    uu: float,
    ui: np.ndarray,
    spatial: np.ndarray,
    N: float,
    beta: np.ndarray,
    h: np.ndarray,
    *,
    jacobian_override: np.ndarray | None = None,
) -> np.ndarray:
    """Unique tensor reconstruction through the full-rank chain Jacobian."""

    volume = N * math.sqrt(float(np.linalg.det(h)))
    E_N = -float(uu)
    E_shift = -np.asarray(ui, dtype=float) / N
    E_h = 0.5 * np.asarray(spatial, dtype=float)
    slot_gradient = np.zeros(10, dtype=float)
    slot_gradient[0] = volume * E_N
    slot_gradient[1:4] = volume * E_shift
    for k, (i, j) in enumerate(SYM3, start=4):
        slot_gradient[k] = volume * E_h[i, j] * (2.0 if i != j else 1.0)
    jacobian = (
        adm_jacobian(N, beta, h)
        if jacobian_override is None
        else np.asarray(jacobian_override, dtype=float)
    )
    gamma_gradient = np.linalg.solve(jacobian.T, slot_gradient)
    return _tau_from_gamma_gradient(gamma_gradient, volume)


def formula_ledger() -> dict[str, Any]:
    """Human-readable formulas whose digest is bound to every receipt."""

    return {
        "v5_2_source_binding": {
            "artifact_sha256": EXPECTED_V5_2_SHA256,
            "schema": EXPECTED_V5_2_SCHEMA,
            "loaded_coefficients": dict(V5_2_COEFF),
            "literal_bulk_gauged": V5_2_ACTION["bulk_gauged"],
            "literal_wall_background": V5_2_ACTION["wall_background"],
            "literal_Robin_intrinsic": V5_2_ACTION["Robin_intrinsic"],
        },
        "literal_variational_coordinates": {
            "n": "n=δN/N",
            "b_shift": "b_shift^i=δβ^i",
            "q": "q_ij=δh_ij",
            "omega": "omega=δOmegaSigma",
            "v": "v_i=δpsi_i",
            "BF_trace_not_shift": "b_BF=iota^*B; b_BF is not b_shift",
            "primary_matter_coordinate": "psi_i fixed independently of h_ij",
        },
        "induced_metric_and_ADM_chart": {
            "induced": "gamma_mn=(Y^*g)_mn=g_AB(Y) partial_m Y^A partial_n Y^B",
            "gamma_00": "gamma_00=-N^2+h_ij beta^i beta^j",
            "gamma_0i": "gamma_0i=h_ij beta^j",
            "gamma_ij": "gamma_ij=h_ij",
            "H_00": "H_00=-2N^2 n+q_ij beta^i beta^j+2h_ij beta^i b_shift^j",
            "H_0i": "H_0i=q_ij beta^j+h_ij b_shift^j",
            "H_ij": "H_ij=q_ij",
            "inverse": (
                "q_ij=H_ij; b_shift^i=h^ij(H_0j-q_jk beta^k); "
                "n=(-H_00+q_ij beta^i beta^j+2h_ij beta^i b_shift^j)/(2N^2)"
            ),
        },
        "one_real_local_action": {
            "covariant": (
                "S_loc=sqrt(-gamma)[-Z/2(gamma^mn p_m·p_n+|P_perp|^2)"
                "-U(Omega)-Z M^2 Omega^-5 V4(Omega^(3/2)|phi|)-V_Sigma(Omega)"
                "-kappa/2 r_i h^ij r_j], r_i=psi_i-y a_i"
            ),
            "ADM": (
                "S_loc=N sqrt(h)[Z/2 |(p_0-beta^i p_i)/N|^2"
                "-Z/2(h^ij p_i·p_j+|P_perp|^2)-U(Omega)"
                "-Z M^2 Omega^-5 V4-V_Sigma-kappa r^2/2]"
            ),
            "bulk_identification": (
                "p_mu=Y^*P_mu and P_perp=n^M P_M are one Gaussian-normal jet of "
                "the literal v5.2 term -Z P_M·P^M/2; phi is fixed in metric variations"
            ),
            "literal_wall": (
                "V_Sigma=2W+beta(Omega-1)^2/2, W=3 exp[-1.2 Omega^2/6], beta=2"
            ),
            "chain": (
                "E_N n+E_shift_i b_shift^i+E_h^ij q_ij"
                "=(1/2) tau^mn H_mn"
            ),
            "projections": (
                "tau_uu=-E_N; tau_ui=-N E_shift_i; "
                "tau_spatial^ij=2E_h^ij"
            ),
        },
        "stress_and_junction": {
            "matter_stress": (
                "T^mn=Z p^m·p^n+[-Z p^2/2-U] gamma^mn; "
                "E_shift_i^matter=-T_ui/N"
            ),
            "Brown_York": "pi^mn=Theta^mn-Theta gamma^mn",
            "junction_tensor": "I^mn=M pi^mn-tau^mn",
            "normal_metric_equation": "E_Yperp(metric)=I^mn Theta_mn=0",
        },
        "bending": {
            "general": "H=Y^*δg+2D_(mu xi_parallel_nu)+2 f Theta_mn",
            "metric_Green_sign": (
                "delta S_metric=-(sqrt(-gamma)/2) I^mn H_mn; "
                "pure normal=-sqrt(-gamma) f I^mn Theta_mn"
            ),
            "trace_augmented_selected_scope": (
                "E_Yperp(selected)=I:Theta-E_Omega d_perp Omega-E_psi^i d_perp psi_i"
            ),
        },
        "psi_varphi_coordinate_change": {
            "definition": "psi_i=h_ij varphi^j",
            "chain": (
                "E_h|varphi=E_h|psi+E_psi^(i varphi^j); "
                "the added term vanishes when the full Robin coefficient E_psi=0"
            ),
        },
        "scope_boundary": {
            "proved": (
                "ten-component algebraic chain, selected local matter/wall/Robin action, "
                "unique tensor reconstruction, and induced metric bending sub-sector"
            ),
            "not_proved": (
                "complete v5.2 derivative action, two-sided momenta of every pulled-back "
                "field, C1, N1, N4, B4, B5, or a full Green theorem"
            ),
        },
    }


def jacobian_certificate(mutant: str | None = None) -> dict[str, Any]:
    data = sample_jet()
    N, beta, h = float(data["N"]), np.asarray(data["beta"]), np.asarray(data["h"])
    gamma = adm_metric(N, beta, h)
    ambient_metric = np.zeros((5, 5), dtype=float)
    ambient_metric[:4, :4] = gamma
    ambient_metric[4, 4] = 1.0
    reference_embedding_tangent = np.zeros((5, 4), dtype=float)
    reference_embedding_tangent[:4, :] = np.eye(4)
    induced_gamma = reference_embedding_tangent.T @ ambient_metric @ reference_embedding_tangent
    induced_reference_error = float(np.max(np.abs(induced_gamma - gamma)))
    recovered_N, recovered_beta, recovered_h = decompose_adm(gamma)
    J = adm_jacobian(N, beta, h)
    if mutant == "lapse_sign":
        J = J.copy()
        J[:, 0] *= -1.0
    elif mutant == "omit_q_beta":
        J = J.copy()
        for column in range(4, 10):
            J[1:4, column] = 0.0
            J[0, column] = 0.0
    elif mutant == "independent_metrics":
        J = np.eye(10)

    directions = np.asarray(
        [
            [0.17, -0.11, 0.08, 0.13, 0.21, -0.07, 0.04, -0.16, 0.09, 0.12],
            [-0.09, 0.19, -0.14, 0.06, -0.08, 0.15, -0.12, 0.11, 0.05, -0.17],
            [0.23, 0.04, 0.10, -0.18, 0.07, 0.03, 0.16, -0.05, -0.13, 0.20],
        ],
        dtype=float,
    )
    inverse_errors = []
    solve_errors = []
    for direction in directions:
        q = _sym_matrix(direction[4:], SYM3, 3)
        H = adm_variation(N, beta, h, direction[0], direction[1:4], q)
        n_back, b_back, q_back = inverse_adm_variation(N, beta, h, H)
        direct_back = np.concatenate([[n_back], b_back, _sym_vector(q_back, SYM3)])
        inverse_errors.append(float(np.max(np.abs(direct_back - direction))))
        solve_errors.append(
            float(np.max(np.abs(np.linalg.solve(J, _sym_vector(H, SYM4)) - direction)))
        )
    return {
        "gamma_equals_Y_star_g_realized_at_reference_embedding": bool(
            induced_reference_error < 2.0e-15
        ),
        "induced_reference_metric_error": induced_reference_error,
        "ADM_recomposition_error": float(
            max(
                abs(recovered_N - N),
                np.max(np.abs(recovered_beta - beta)),
                np.max(np.abs(recovered_h - h)),
            )
        ),
        "Jacobian_shape": list(J.shape),
        "Jacobian_rank": int(np.linalg.matrix_rank(J)),
        "Jacobian_determinant": float(np.linalg.det(J)),
        "Jacobian_condition_number": float(np.linalg.cond(J)),
        "analytic_inverse_max_error": max(inverse_errors),
        "linear_solve_inverse_max_error": max(solve_errors),
        "nonzero_beta_norm": float(np.linalg.norm(beta)),
        "off_diagonal_h_norm": float(np.linalg.norm(h - np.diag(np.diag(h)))),
        "mutant": mutant,
    }


def action_chain_certificate(mutant: str | None = None) -> dict[str, Any]:
    data = sample_jet()
    N, beta, h = float(data["N"]), np.asarray(data["beta"]), np.asarray(data["h"])
    Omega, psi = float(data["Omega"]), np.asarray(data["psi"])
    gamma = adm_metric(N, beta, h)
    volume = N * math.sqrt(float(np.linalg.det(h)))
    J = adm_jacobian(N, beta, h)
    adm_gradient = _adm_gradient(data)
    gamma_gradient = _gamma_gradient(gamma, Omega, psi, data)
    if mutant == "gamma_overall_sign":
        gamma_gradient = -gamma_gradient
    elif mutant == "omit_shift_slot":
        adm_gradient = adm_gradient.copy()
        adm_gradient[1:4] = 0.0
    elif mutant == "independent_metrics":
        J = np.eye(10)
    elif mutant == "off_diagonal_double_count":
        gamma_gradient = gamma_gradient.copy()
        for k, (i, j) in enumerate(SYM4):
            if i != j:
                gamma_gradient[k] *= 2.0

    tau = _tau_from_gamma_gradient(gamma_gradient, volume)
    euler = _adm_euler_from_gradient(adm_gradient, volume)
    chain_error = float(np.max(np.abs(adm_gradient - J.T @ gamma_gradient)))

    directions = np.asarray(
        [
            [0.13, -0.09, 0.16, 0.07, 0.11, -0.12, 0.06, -0.08, 0.15, 0.04],
            [-0.21, 0.14, -0.05, 0.18, -0.09, 0.07, 0.12, 0.17, -0.03, -0.10],
            [0.08, 0.22, -0.17, -0.11, 0.19, 0.05, -0.14, 0.06, 0.09, -0.16],
        ],
        dtype=float,
    )
    pairing_errors = []
    for direction in directions:
        q = _sym_matrix(direction[4:], SYM3, 3)
        H = adm_variation(N, beta, h, direction[0], direction[1:4], q)
        left = volume * (
            float(euler["E_N"]) * direction[0]
            + float(np.asarray(euler["E_shift"]) @ direction[1:4])
            + float(np.sum(np.asarray(euler["E_h"]) * q))
        )
        right = 0.5 * volume * float(np.sum(tau * H))
        pairing_errors.append(abs(left - right))

    projections = _metric_projections(tau, N, beta, gamma)
    projection_error = max(
        abs(float(projections["uu"]) + float(euler["E_N"])),
        float(
            np.max(
                np.abs(
                    np.asarray(projections["ui"]) + N * np.asarray(euler["E_shift"])
                )
            )
        ),
        float(
            np.max(
                np.abs(
                    np.asarray(projections["spatial"]) - 2.0 * np.asarray(euler["E_h"])
                )
            )
        ),
    )

    omega_derivative = _five_point(
        lambda epsilon: action_adm(N, beta, h, Omega + epsilon, psi, data)
    ) / volume
    v_derivative = np.asarray(
        [
            _five_point(
                lambda epsilon, i=i: action_adm(
                    N, beta, h, Omega, psi + epsilon * np.eye(3)[i], data
                )
            )
            / volume
            for i in range(3)
        ],
        dtype=float,
    )
    return {
        "single_action_ADM_value": action_adm(N, beta, h, Omega, psi, data),
        "single_action_gamma_value": action_gamma(gamma, Omega, psi, data),
        "action_representation_error": abs(
            action_adm(N, beta, h, Omega, psi, data)
            - action_gamma(gamma, Omega, psi, data)
        ),
        "ADM_vs_gamma_chain_max_error": chain_error,
        "random_direction_pairing_max_error": max(pairing_errors),
        "projection_formula_max_error": projection_error,
        "minimum_absolute_ADM_slot_derivative": float(np.min(np.abs(adm_gradient))),
        "tau_Frobenius_norm": float(np.linalg.norm(tau)),
        "E_N": float(euler["E_N"]),
        "E_shift": np.asarray(euler["E_shift"]).tolist(),
        "E_h": np.asarray(euler["E_h"]).tolist(),
        "E_Omega": float(omega_derivative),
        "E_psi": v_derivative.tolist(),
        "tau": tau.tolist(),
        "mutant": mutant,
    }


def matter_shift_certificate(mutant: str | None = None) -> dict[str, Any]:
    data = sample_jet()
    N, beta, h = float(data["N"]), np.asarray(data["beta"]), np.asarray(data["h"])
    Omega, psi = float(data["Omega"]), np.asarray(data["psi"])
    gamma = adm_metric(N, beta, h)
    volume = N * math.sqrt(float(np.linalg.det(h)))
    p_cov = np.asarray(data["p_cov"])
    p_normal = np.asarray(data["p_normal"])
    gamma_inverse = np.linalg.inv(gamma)
    p_up = gamma_inverse @ p_cov
    p_squared = (
        float(np.einsum("mn,ma,na->", gamma_inverse, p_cov, p_cov))
        + float(p_normal @ p_normal)
    )
    matter_lagrangian = (
        -0.5 * float(data["Z"]) * p_squared
        - _bulk_potential(float(data["Omega"]), data)
    )
    stress = float(data["Z"]) * np.einsum("ma,na->mn", p_up, p_up)
    stress += matter_lagrangian * gamma_inverse
    u_cov = np.asarray([-N, 0.0, 0.0, 0.0])
    T_ui = np.asarray(u_cov @ stress @ gamma[:, 1:], dtype=float)
    expected_shift = -T_ui / N
    if mutant == "flip_momentum_sign":
        expected_shift = T_ui / N
    elif mutant == "omit_matter_current":
        expected_shift = np.zeros(3, dtype=float)

    numerical_shift = np.asarray(
        [
            _five_point(
                lambda epsilon, i=i: action_adm(
                    N,
                    beta + epsilon * np.eye(3)[i],
                    h,
                    Omega,
                    psi,
                    data,
                    matter=True,
                    wall_robin=False,
                )
            )
            / volume
            for i in range(3)
        ],
        dtype=float,
    )

    direct_wall_robin_shift = np.asarray(
        [
            _five_point(
                lambda epsilon, i=i: action_adm(
                    N,
                    beta + epsilon * np.eye(3)[i],
                    h,
                    Omega,
                    psi,
                    data,
                    matter=False,
                    wall_robin=True,
                )
            )
            / volume
            for i in range(3)
        ],
        dtype=float,
    )
    r = psi - float(data["robin_y"]) * np.asarray(data["a"])
    fake_coefficient = 0.37
    fake_robin_shift = fake_coefficient * r
    if mutant == "fake_Robin_shift_current":
        direct_wall_robin_shift = fake_robin_shift
    return {
        "p_u_norm": float(
            np.linalg.norm((p_cov[0] - np.einsum("i,ia->a", beta, p_cov[1:])) / N)
        ),
        "spatial_gradient_min_norm": float(
            min(np.linalg.norm(p_cov[i]) for i in range(1, 4))
        ),
        "T_ui": T_ui.tolist(),
        "T_ui_norm": float(np.linalg.norm(T_ui)),
        "numerical_E_shift_matter": numerical_shift.tolist(),
        "covariant_momentum_prediction": expected_shift.tolist(),
        "matter_shift_error": float(np.max(np.abs(numerical_shift - expected_shift))),
        "wall_Robin_direct_shift_norm": float(np.linalg.norm(direct_wall_robin_shift)),
        "fake_Robin_shift_current_witness": float(np.linalg.norm(fake_robin_shift)),
        "mutant": mutant,
    }


def psi_varphi_chain_certificate(mutant: str | None = None) -> dict[str, Any]:
    data = sample_jet()
    N, h = float(data["N"]), np.asarray(data["h"])
    volume = N * math.sqrt(float(np.linalg.det(h)))
    psi = np.asarray(data["psi"])
    varphi = np.linalg.solve(h, psi)
    gradient_psi = _adm_gradient(data)
    gradient_varphi = _adm_gradient(data, fixed_varphi=varphi)
    E_h_psi = np.asarray(_adm_euler_from_gradient(gradient_psi, volume)["E_h"])
    E_h_varphi = np.asarray(_adm_euler_from_gradient(gradient_varphi, volume)["E_h"])
    E_psi = np.asarray(
        [
            _five_point(
                lambda epsilon, i=i: action_adm(
                    float(data["N"]),
                    np.asarray(data["beta"]),
                    h,
                    float(data["Omega"]),
                    psi + epsilon * np.eye(3)[i],
                    data,
                )
            )
            / volume
            for i in range(3)
        ]
    )
    coordinate_term = 0.5 * (np.outer(E_psi, varphi) + np.outer(varphi, E_psi))
    if mutant == "omit_coordinate_term":
        coordinate_term = np.zeros((3, 3), dtype=float)
    elif mutant == "flip_coordinate_term":
        coordinate_term = -coordinate_term

    r = psi - float(data["robin_y"]) * np.asarray(data["a"])
    robin_surface_coefficient = -float(data["kappa"]) * np.linalg.solve(h, r)
    bulk_trace_momentum_on_shell = -robin_surface_coefficient
    full_robin_coefficient = bulk_trace_momentum_on_shell + robin_surface_coefficient
    off_shell_full_coefficient = full_robin_coefficient + np.asarray([0.13, -0.07, 0.09])
    on_shell_cross = 0.5 * (
        np.outer(full_robin_coefficient, varphi)
        + np.outer(varphi, full_robin_coefficient)
    )
    off_shell_cross = 0.5 * (
        np.outer(off_shell_full_coefficient, varphi)
        + np.outer(varphi, off_shell_full_coefficient)
    )
    return {
        "primary_coordinate": "psi_i",
        "varphi_definition": "varphi^i=h^ij psi_j",
        "E_psi": E_psi.tolist(),
        "coordinate_cross_term": coordinate_term.tolist(),
        "fixed_varphi_minus_fixed_psi_metric_error": float(
            np.max(np.abs(E_h_varphi - E_h_psi - coordinate_term))
        ),
        "coordinate_cross_term_norm": float(np.linalg.norm(
            0.5 * (np.outer(E_psi, varphi) + np.outer(varphi, E_psi))
        )),
        "Robin_surface_coefficient_match_error": float(
            np.max(np.abs(E_psi - robin_surface_coefficient))
        ),
        "full_Robin_on_shell_coefficient_norm": float(np.linalg.norm(full_robin_coefficient)),
        "on_shell_coordinate_cross_norm": float(np.linalg.norm(on_shell_cross)),
        "off_shell_coordinate_cross_norm": float(np.linalg.norm(off_shell_cross)),
        "mutant": mutant,
    }


def israel_reconstruction_certificate(mutant: str | None = None) -> dict[str, Any]:
    data = sample_jet()
    N, beta, h = float(data["N"]), np.asarray(data["beta"]), np.asarray(data["h"])
    gamma = adm_metric(N, beta, h)
    volume = N * math.sqrt(float(np.linalg.det(h)))
    gamma_gradient = _gamma_gradient(gamma, float(data["Omega"]), np.asarray(data["psi"]), data)
    tau = _tau_from_gamma_gradient(gamma_gradient, volume)
    Theta = np.asarray(
        [
            [0.12, 0.03, -0.02, 0.04],
            [0.03, -0.08, 0.025, -0.015],
            [-0.02, 0.025, 0.07, 0.018],
            [0.04, -0.015, 0.018, -0.05],
        ],
        dtype=float,
    )
    gamma_inverse = np.linalg.inv(gamma)
    Theta_trace = float(np.sum(gamma_inverse * Theta))
    Theta_up = gamma_inverse @ Theta @ gamma_inverse
    pi = Theta_up - Theta_trace * gamma_inverse
    wrong_pi = -pi
    M = 1.70
    junction = M * pi - tau

    target = junction
    projections = _metric_projections(target, N, beta, gamma)
    uu = float(projections["uu"])
    ui = np.asarray(projections["ui"])
    spatial = np.asarray(projections["spatial"])
    if mutant == "flip_tensor_sign":
        uu, ui, spatial = -uu, -ui, -spatial
    elif mutant == "omit_lapse_slot":
        uu = 0.0
    elif mutant == "omit_shift_slot":
        ui = np.zeros(3, dtype=float)
    elif mutant == "omit_spatial_slot":
        spatial = np.zeros((3, 3), dtype=float)
    elif mutant == "Brown_York_sign":
        target = M * wrong_pi - tau

    reconstructed = _tensor_from_adm_projections(
        uu,
        ui,
        spatial,
        N,
        beta,
        h,
        jacobian_override=np.eye(10) if mutant == "independent_Jacobian" else None,
    )
    return {
        "Brown_York_convention": "pi^mn=Theta^mn-Theta gamma^mn",
        "junction_convention": "I^mn=M pi^mn-tau^mn",
        "Theta_trace": Theta_trace,
        "Brown_York_norm": float(np.linalg.norm(pi)),
        "junction_tensor_norm": float(np.linalg.norm(junction)),
        "projection_reconstruction_error": float(np.max(np.abs(reconstructed - target))),
        "Brown_York_wrong_sign_witness": float(np.linalg.norm(M * (wrong_pi - pi))),
        "Jacobian_rank_used_for_uniqueness": int(np.linalg.matrix_rank(adm_jacobian(N, beta, h))),
        "tau": tau.tolist(),
        "Theta": Theta.tolist(),
        "pi": pi.tolist(),
        "junction": junction.tolist(),
        "mutant": mutant,
    }


def bending_certificate(mutant: str | None = None) -> dict[str, Any]:
    """Induced family with all three H terms; normal equation run separately."""

    data = sample_jet()
    N, beta, h = float(data["N"]), np.asarray(data["beta"]), np.asarray(data["h"])
    gamma0 = adm_metric(N, beta, h)
    volume = N * math.sqrt(float(np.linalg.det(h)))
    Theta = np.asarray(
        [
            [0.12, 0.03, -0.02, 0.04],
            [0.03, -0.08, 0.025, -0.015],
            [-0.02, 0.025, 0.07, 0.018],
            [0.04, -0.015, 0.018, -0.05],
        ]
    )
    delta_g = np.asarray(
        [
            [0.09, -0.04, 0.025, 0.03],
            [-0.04, 0.06, -0.018, 0.022],
            [0.025, -0.018, -0.05, 0.017],
            [0.03, 0.022, 0.017, 0.04],
        ]
    )
    D_xi = np.asarray(
        [
            [0.025, -0.014, 0.009, 0.006],
            [0.017, -0.021, 0.012, -0.008],
            [-0.011, 0.015, 0.019, 0.010],
            [0.008, -0.006, 0.013, -0.016],
        ]
    )
    f_bend = 0.37

    def induced(s: float) -> np.ndarray:
        tangent = np.eye(4) + s * D_xi
        ambient_tangent_metric = gamma0 + s * delta_g + 2.0 * (s * f_bend) * Theta
        return tangent.T @ ambient_tangent_metric @ tangent

    numerical_H = _five_point_matrix(induced)
    term_delta_g = delta_g
    term_xi = D_xi.T @ gamma0 + gamma0 @ D_xi
    term_normal = 2.0 * f_bend * Theta
    analytic_H = term_delta_g + term_xi + term_normal
    if mutant == "omit_Y_star_delta_g":
        analytic_H = term_xi + term_normal
    elif mutant == "omit_tangential_transport":
        analytic_H = term_delta_g + term_normal
    elif mutant == "omit_normal_bending":
        analytic_H = term_delta_g + term_xi
    elif mutant == "flip_normal_sign":
        analytic_H = term_delta_g + term_xi - term_normal

    n, b_shift, q = inverse_adm_variation(N, beta, h, numerical_H)
    reconstructed_H = adm_variation(N, beta, h, n, b_shift, q)

    gamma_gradient = _gamma_gradient(
        gamma0, float(data["Omega"]), np.asarray(data["psi"]), data
    )
    tau = _tau_from_gamma_gradient(gamma_gradient, volume)
    gamma_inverse = np.linalg.inv(gamma0)
    Theta_trace = float(np.sum(gamma_inverse * Theta))
    pi = gamma_inverse @ Theta @ gamma_inverse - Theta_trace * gamma_inverse
    junction = 1.70 * pi - tau
    metric_normal_residual = float(np.sum(junction * Theta))
    H_normal = 2.0 * f_bend * Theta
    metric_Green_direct = -0.5 * volume * float(np.sum(junction * H_normal))
    metric_Green_from_normal_equation = -volume * f_bend * metric_normal_residual
    if mutant == "normal_equation_sign":
        metric_Green_from_normal_equation *= -1.0

    chain = action_chain_certificate()
    E_Omega = float(chain["E_Omega"])
    E_psi = np.asarray(chain["E_psi"])
    d_perp_Omega = 0.18
    d_perp_psi = np.asarray([0.09, -0.06, 0.07])
    selected_augmented_residual = (
        metric_normal_residual
        - E_Omega * d_perp_Omega
        - float(E_psi @ d_perp_psi)
    )
    selected_augmented_Green = -volume * f_bend * selected_augmented_residual
    direct_selected_Green = metric_Green_direct + volume * f_bend * (
        E_Omega * d_perp_Omega + float(E_psi @ d_perp_psi)
    )
    return {
        "ambient_dimension": 5,
        "embedding": "Y_s(sigma)=(sigma+s xi(sigma), r=s f_bend)",
        "ambient_metric": "g_ab(s,r)=gamma0_ab+s delta_g_ab+2r Theta_ab; g_rr=1",
        "H_formula": "H=Y^*δg+2D_(mu xi_parallel_nu)+2 f_bend Theta_mn",
        "H_formula_max_error": float(np.max(np.abs(numerical_H - analytic_H))),
        "Y_star_delta_g_norm": float(np.linalg.norm(term_delta_g)),
        "tangential_transport_norm": float(np.linalg.norm(term_xi)),
        "normal_bending_norm": float(np.linalg.norm(term_normal)),
        "H_to_ADM_to_H_error": float(np.max(np.abs(numerical_H - reconstructed_H))),
        "recovered_n": float(n),
        "recovered_b_shift_norm": float(np.linalg.norm(b_shift)),
        "recovered_q_norm": float(np.linalg.norm(q)),
        "metric_normal_residual_I_Theta": metric_normal_residual,
        "metric_normal_residual_absolute_value": abs(metric_normal_residual),
        "metric_Green_normal_error": abs(
            metric_Green_direct - metric_Green_from_normal_equation
        ),
        "selected_trace_augmented_residual": selected_augmented_residual,
        "selected_trace_augmented_Green_error": abs(
            direct_selected_Green - selected_augmented_Green
        ),
        "complete_v5_2_all_field_normal_embedding_claimed": False,
        "missing_for_complete_normal": (
            "two-sided bulk normal momenta and transport laws for Omega, phi, A, B, T, "
            "plus the derivative EH/GHY and regulated corner Green coefficients"
        ),
        "mutant": mutant,
    }


def _mutation_witnesses() -> dict[str, float]:
    nominal_J = jacobian_certificate()
    nominal_chain = action_chain_certificate()
    nominal_matter = matter_shift_certificate()
    nominal_psi = psi_varphi_chain_certificate()
    nominal_israel = israel_reconstruction_certificate()
    nominal_bending = bending_certificate()
    witnesses: dict[str, float] = {}
    for mutant in ("lapse_sign", "omit_q_beta", "independent_metrics"):
        row = jacobian_certificate(mutant)
        witnesses[f"Jacobian_{mutant}"] = max(
            row["linear_solve_inverse_max_error"],
            abs(row["Jacobian_determinant"] - nominal_J["Jacobian_determinant"]),
        )
    for mutant in (
        "gamma_overall_sign", "omit_shift_slot", "independent_metrics",
        "off_diagonal_double_count",
    ):
        row = action_chain_certificate(mutant)
        witnesses[f"chain_{mutant}"] = max(
            row["ADM_vs_gamma_chain_max_error"], row["random_direction_pairing_max_error"]
        )
    for mutant in ("flip_momentum_sign", "omit_matter_current"):
        row = matter_shift_certificate(mutant)
        witnesses[f"matter_{mutant}"] = row["matter_shift_error"]
    witnesses["Robin_fake_shift_current"] = matter_shift_certificate(
        "fake_Robin_shift_current"
    )["wall_Robin_direct_shift_norm"]
    for mutant in ("omit_coordinate_term", "flip_coordinate_term"):
        witnesses[f"psi_varphi_{mutant}"] = psi_varphi_chain_certificate(mutant)[
            "fixed_varphi_minus_fixed_psi_metric_error"
        ]
    for mutant in (
        "flip_tensor_sign", "omit_lapse_slot", "omit_shift_slot", "omit_spatial_slot",
        "Brown_York_sign", "independent_Jacobian",
    ):
        witnesses[f"Israel_{mutant}"] = israel_reconstruction_certificate(mutant)[
            "projection_reconstruction_error"
        ]
    for mutant in (
        "omit_Y_star_delta_g", "omit_tangential_transport", "omit_normal_bending",
        "flip_normal_sign", "normal_equation_sign",
    ):
        row = bending_certificate(mutant)
        witnesses[f"bending_{mutant}"] = max(
            row["H_formula_max_error"], row["metric_Green_normal_error"]
        )
    # Explicitly retain nominal activity in the receipt: mutants may not hide
    # behind a zero equation or a static/diagonal background.
    witnesses["nominal_shift_activity"] = float(np.linalg.norm(nominal_chain["E_shift"]))
    witnesses["nominal_matter_T_ui_activity"] = nominal_matter["T_ui_norm"]
    witnesses["nominal_coordinate_cross_activity"] = nominal_psi[
        "coordinate_cross_term_norm"
    ]
    witnesses["nominal_junction_activity"] = nominal_israel["junction_tensor_norm"]
    witnesses["nominal_normal_equation_activity"] = nominal_bending[
        "metric_normal_residual_absolute_value"
    ]
    return witnesses


def _decision(
    jacobian: Mapping[str, Any],
    chain: Mapping[str, Any],
    matter: Mapping[str, Any],
    psi_chain: Mapping[str, Any],
    israel: Mapping[str, Any],
    bending: Mapping[str, Any],
    witnesses: Mapping[str, float],
) -> dict[str, bool]:
    literal = formula_ledger()["literal_variational_coordinates"]
    literal_contract = bool(
        literal.get("n") == "n=δN/N"
        and literal.get("b_shift") == "b_shift^i=δβ^i"
        and literal.get("q") == "q_ij=δh_ij"
        and literal.get("omega") == "omega=δOmegaSigma"
        and literal.get("v") == "v_i=δpsi_i"
        and literal.get("BF_trace_not_shift")
        == "b_BF=iota^*B; b_BF is not b_shift"
    )
    decision = {
        "literal_slot_coordinate_contract_pass": literal_contract,
        "induced_ADM_bidirectional_Jacobian_pass": bool(
            jacobian["Jacobian_rank"] == 10
            and jacobian["gamma_equals_Y_star_g_realized_at_reference_embedding"] is True
            and jacobian["induced_reference_metric_error"] < 2.0e-15
            and jacobian["ADM_recomposition_error"] < 2.0e-14
            and jacobian["analytic_inverse_max_error"] < 2.0e-14
            and jacobian["linear_solve_inverse_max_error"] < 2.0e-13
        ),
        "one_action_independent_gamma_ADM_chain_pass": bool(
            chain["action_representation_error"] < 2.0e-13
            and chain["ADM_vs_gamma_chain_max_error"] < 2.0e-8
            and chain["random_direction_pairing_max_error"] < 2.0e-8
            and chain["projection_formula_max_error"] < 2.0e-8
            and chain["minimum_absolute_ADM_slot_derivative"] > 1.0e-4
        ),
        "single_Israel_Brown_York_tensor_reconstruction_pass": bool(
            israel["Jacobian_rank_used_for_uniqueness"] == 10
            and israel["projection_reconstruction_error"] < 2.0e-12
            and israel["Brown_York_wrong_sign_witness"] > 1.0e-3
        ),
        "metric_bending_normal_subsector_pass": bool(
            bending["H_formula_max_error"] < 2.0e-10
            and bending["H_to_ADM_to_H_error"] < 1.0e-10
            and bending["metric_Green_normal_error"] < 2.0e-14
            and bending["selected_trace_augmented_Green_error"] < 2.0e-14
            and bending["metric_normal_residual_absolute_value"] > 1.0e-4
            and bending["complete_v5_2_all_field_normal_embedding_claimed"] is False
        ),
        "bulk_matter_shift_momentum_witness_pass": bool(
            matter["T_ui_norm"] > 1.0e-3
            and matter["matter_shift_error"] < 2.0e-9
        ),
        "wall_Robin_no_direct_shift_pass": bool(
            matter["wall_Robin_direct_shift_norm"] < 2.0e-10
            and matter["fake_Robin_shift_current_witness"] > 1.0e-3
        ),
        "psi_varphi_total_chain_pass": bool(
            psi_chain["fixed_varphi_minus_fixed_psi_metric_error"] < 2.0e-9
            and psi_chain["coordinate_cross_term_norm"] > 1.0e-4
            and psi_chain["Robin_surface_coefficient_match_error"] < 2.0e-9
            and psi_chain["full_Robin_on_shell_coefficient_norm"] < 1.0e-14
            and psi_chain["on_shell_coordinate_cross_norm"] < 1.0e-14
            and psi_chain["off_shell_coordinate_cross_norm"] > 1.0e-4
        ),
        "off_shell_mutation_suite_pass": bool(
            min(float(value) for value in witnesses.values()) > 1.0e-5
        ),
    }
    decision["candidate_checks_pass"] = all(decision.values())
    for key in FAIL_CLOSED_KEYS:
        decision[key] = False
    true_pass_keys = {
        key for key, value in decision.items() if key.endswith("_pass") and value is True
    }
    if not true_pass_keys <= ALLOWED_TRUE_PASS_KEYS:
        raise ADMChainV552Error("unexpected true pass key")
    if any(decision[key] is not False for key in FAIL_CLOSED_KEYS):
        raise ADMChainV552Error("fail-closed boundary changed")
    return decision


def build_payload() -> dict[str, Any]:
    _, live_coefficients, live_actions = _load_v5_2()
    if live_coefficients != V5_2_COEFF or live_actions != V5_2_ACTION:
        raise ADMChainV552Error("v5.2 runtime binding differs from loaded action data")
    ledger = formula_ledger()
    digest = _canonical_sha256(ledger)
    if digest != EXPECTED_FORMULA_LEDGER_SHA256:
        raise ADMChainV552Error("formula ledger digest mismatch")
    jacobian = jacobian_certificate()
    chain = action_chain_certificate()
    matter = matter_shift_certificate()
    psi_chain = psi_varphi_chain_certificate()
    israel = israel_reconstruction_certificate()
    bending = bending_certificate()
    witnesses = _mutation_witnesses()
    decision = _decision(jacobian, chain, matter, psi_chain, israel, bending, witnesses)
    return {
        "schema": SCHEMA,
        "claim": (
            "Additive, self-contained algebraic induced-metric/ADM chain certificate on "
            "one off-shell local action; it is not a C1/N1/B4 promotion."
        ),
        "v5_2_source_binding": {
            "path": str(V5_2_PATH.resolve().relative_to(HERE.parents[1])),
            "sha256": EXPECTED_V5_2_SHA256,
            "schema": EXPECTED_V5_2_SCHEMA,
            "coefficients_used": dict(live_coefficients),
            "literal_actions_used": dict(live_actions),
        },
        "frozen_gate_helpers_imported": [],
        "formula_ledger_sha256": digest,
        "formula_ledger": ledger,
        "certificates": {
            "ADM_Jacobian": jacobian,
            "one_action_two_routes": chain,
            "matter_shift_and_Robin": matter,
            "psi_varphi_coordinate_chain": psi_chain,
            "Israel_Brown_York_reconstruction": israel,
            "induced_bending": bending,
            "mutation_witnesses": witnesses,
        },
        "decision": decision,
        "provenance": {
            "generator": str(Path(__file__).resolve().relative_to(HERE.parents[1])),
            "generator_sha256": _sha256(Path(__file__)),
            "test": str(TEST.resolve().relative_to(HERE.parents[1])),
            "test_sha256": _sha256(TEST),
            "numerical_library": f"numpy-{np.__version__}",
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
