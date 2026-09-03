#!/usr/bin/env python3
"""Independent red-team for the selected-family v5.5.4 interface Ward gate.

The primary implementation is consumed only as three byte-hashed artifacts.
No primary Python helper or runtime object is imported.  This file rebuilds a
different four-dimensional family and checks the same literal v5.2 intrinsic
interface action using finite action differences, a separate forward-mode JVP
density and an independently assembled eight-face Stokes density.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import torch
from torch.func import jacrev, jvp, vmap


torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass
torch.set_default_dtype(torch.float64)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
V5_2 = HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
V5_5_2 = HERE / "artifacts" / "one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.json"
V5_5_2_REDTEAM = HERE / "artifacts" / "one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.json"
PRIMARY_V5_5_4_GENERATOR = HERE / "derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.py"
PRIMARY_V5_5_4_TEST = HERE / "test_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.py"
PRIMARY_V5_5_4_ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.json"
OUTPUT = HERE / "artifacts" / "one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam.json"
TEST = HERE / "test_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam.py"

SCHEMA = "holo.one-omega-topological-so3-interface-diffeomorphism-khronon-v5-5-4-redteam.v1"
EXPECTED_V5_2_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
EXPECTED_V5_5_2_SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-gate.v1"
EXPECTED_V5_5_2_REDTEAM_SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-redteam.v1"
EXPECTED_PRIMARY_V5_5_4_SCHEMA = "holo.one-omega-topological-so3-interface-diffeomorphism-khronon-v5-5-4-gate.v1"
EXPECTED_V5_2_SHA256 = "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b"
EXPECTED_V5_5_2_SHA256 = "4e068475ae316684cebd0f68e10d183fff7c0d90c46b155f2dfc8be4b3b0d6e8"
EXPECTED_V5_5_2_REDTEAM_SHA256 = "4c94c2abeb24fb3444be4f79c93aa383659feac9e706eea7fe4fe2aac85bc7f6"

EXPECTED_PRIMARY_V5_5_4_GENERATOR_SHA256 = "299d07965f0a6feb4f9f577664a7c13f09107fefe85ac80ac6efdf5b0e22c024"
EXPECTED_PRIMARY_V5_5_4_TEST_SHA256 = "2c37ccd958c9bee99d8d3a5b28bd345a22b90786d1b36b33cf01c23477c877c6"
EXPECTED_PRIMARY_V5_5_4_ARTIFACT_SHA256 = "d5e60c535cdfb19aeee7d8007e3c39afcff699e34128ca1a016d4ba4469cd23c"

EXPECTED_ACTIONS = {
    "bulk_gauged": (
        "S_bulk_gauged=sum_eps int_Meps sqrt(-g_eps)*[M5^3*R_eps/2-"
        "G*(nabla Omega_eps)^2/2-U(Omega_eps)-Z5*delta_ab*P_eps_M^a*"
        "P_eps^(b M)/2-Z5*M^2*Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)]"
    ),
    "foliation_lower": (
        "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-"
        "lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
        "B4_bar*Rcal^2/(16*k_infinity^2)]"
    ),
    "wall_background": (
        "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+"
        "beta*(Omega_Sigma-1)^2/2]"
    ),
    "Robin_intrinsic": (
        "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*"
        "h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)"
    ),
    "full_V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
    "gauged_conformal_derivative": (
        "P_eps_M=D_(A_eps,M)phi_eps+3*phi_eps*partial_M log(Omega_eps)/2"
    ),
}
EXPECTED_CONTROL_LITERALS = {
    "associated_trace": "j_eps(Y_eps^*phi_eps)=varphi_H in H_(gamma,T)",
    "induced_metric": "gamma_mu_nu=Y_eps^*g_eps and is common on both sides",
    "scalar_pullback": "delta(Y^*f)=Y^*(delta f+Lie_xi f)",
    "reference_domain": (
        "M_eps are fixed reference half-spaces; moving physical domains are pulled "
        "back in full by Y_eps, so the material variations include Lie_xi once and "
        "no separate i_xi L_5 term is added"
    ),
}
EXPECTED_COEFFICIENTS = {
    "brane_Mb_squared": 2.0,
    "lambda_K": -0.5535068954004245,
    "xi": 1.0,
    "eta": 3.107013790800849,
    "B4_bar": 0.8,
    "k_infinity": 1.0,
    "M5_cubed": 1.0,
    "compensator_metric_G": 1.2,
    "brane_beta": 2.0,
    "Robin_kappa_hat": 1.0,
    "Robin_y": math.sqrt(3.0),
    "material_Z5_per_side": 1.0,
    "material_mass_M": 1.0,
}

MB2 = EXPECTED_COEFFICIENTS["brane_Mb_squared"]
LAMBDA_K = EXPECTED_COEFFICIENTS["lambda_K"]
XI_R = EXPECTED_COEFFICIENTS["xi"]
ETA = EXPECTED_COEFFICIENTS["eta"]
B4_BAR = EXPECTED_COEFFICIENTS["B4_bar"]
K_INFINITY = EXPECTED_COEFFICIENTS["k_infinity"]
M5 = EXPECTED_COEFFICIENTS["M5_cubed"]
G_OMEGA = EXPECTED_COEFFICIENTS["compensator_metric_G"]
BETA = EXPECTED_COEFFICIENTS["brane_beta"]
KAPPA = EXPECTED_COEFFICIENTS["Robin_kappa_hat"]
ROBIN_Y = EXPECTED_COEFFICIENTS["Robin_y"]
Z5 = EXPECTED_COEFFICIENTS["material_Z5_per_side"]
MATERIAL_M = EXPECTED_COEFFICIENTS["material_mass_M"]
DOMAIN = 0.68

COMPONENT_LABELS = tuple(
    [f"gamma_{mu}{nu}" for mu, nu in (
        (0, 0), (0, 1), (0, 2), (0, 3), (1, 1),
        (1, 2), (1, 3), (2, 2), (2, 3), (3, 3),
    )]
    + ["T", "Omega"]
    + [f"psi_{mu}" for mu in range(4)]
)
COMPONENT_COUNT = len(COMPONENT_LABELS)
COMPONENT_ACTION_JVP_TOLERANCE = 2.0e-6
COMPONENT_LOCAL_ACTIVITY_FLOOR = 1.0e-8
MUTANT_RESIDUAL_FLOOR = 1.0e-6

FAIL_CLOSED_KEYS = (
    "full_bulk_diffeomorphism_Ward_pass",
    "complete_moving_embedding_Ward_pass",
    "complete_all_field_Euler_variation_pass",
    "complete_v5_2_all_field_normal_embedding_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "full_off_shell_Green_theorem_accepted",
    "continuum_all_configurations_theorem_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "unrestricted_large_gauge_sector_pass",
    "v5_6_promotion_authorized",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "N4_JUNCTION_BENDING_pass",
    "P4_full_same_action_pass",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
)

ALLOWED_TRUE_PASS_KEYS = {
    "primary_v5_5_4_three_file_hash_binding_pass",
    "independent_interface_diffeomorphism_khronon_redteam_pass",
    "two_compact_xi_and_density_divergence_pass",
    "real_local_JVP_10_gamma_T_Omega_4_psi_pass",
    "independent_action_JVP_Stokes_density_assemblies_pass",
    "executed_mutation_re_evaluation_pass",
    "independent_R_groupoid_pullback_T_ui_V4_controls_pass",
    "local_density_Ward_equals_divergence_redteam_pass",
    "runtime_boundary_Stokes_flux_zero_redteam_pass",
    "compact_xi_weak_Ward_zero_by_local_Stokes_redteam_pass",
    "independent_finite_action_Euler_route_pass",
    "off_shell_mutation_suite_pass",
    "independent_redteam_checks_pass",
}


class InterfaceWardV554RedteamError(ValueError):
    """A lineage pin or independent red-team check failed closed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise InterfaceWardV554RedteamError(f"cannot hash {path}: {exc}") from exc


def _read(path: Path, expected_hash: str, expected_schema: str) -> dict[str, Any]:
    if expected_hash.startswith("PENDING_"):
        raise InterfaceWardV554RedteamError("primary v5.5.4 hashes are pending")
    if _sha256(path) != expected_hash:
        raise InterfaceWardV554RedteamError(f"lineage hash mismatch: {path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InterfaceWardV554RedteamError(f"cannot parse {path}") from exc
    if payload.get("schema") != expected_schema:
        raise InterfaceWardV554RedteamError(f"lineage schema mismatch: {path.name}")
    return payload


def load_lineage() -> dict[str, Any]:
    v52 = _read(V5_2, EXPECTED_V5_2_SHA256, EXPECTED_V5_2_SCHEMA)
    v552 = _read(V5_5_2, EXPECTED_V5_5_2_SHA256, EXPECTED_V5_5_2_SCHEMA)
    v552_red = _read(
        V5_5_2_REDTEAM,
        EXPECTED_V5_5_2_REDTEAM_SHA256,
        EXPECTED_V5_5_2_REDTEAM_SCHEMA,
    )
    primary = _read(
        PRIMARY_V5_5_4_ARTIFACT,
        EXPECTED_PRIMARY_V5_5_4_ARTIFACT_SHA256,
        EXPECTED_PRIMARY_V5_5_4_SCHEMA,
    )
    if _sha256(PRIMARY_V5_5_4_GENERATOR) != EXPECTED_PRIMARY_V5_5_4_GENERATOR_SHA256:
        raise InterfaceWardV554RedteamError("primary v5.5.4 generator hash mismatch")
    if _sha256(PRIMARY_V5_5_4_TEST) != EXPECTED_PRIMARY_V5_5_4_TEST_SHA256:
        raise InterfaceWardV554RedteamError("primary v5.5.4 test hash mismatch")
    if (
        primary.get("provenance", {}).get("generator_sha256")
        != EXPECTED_PRIMARY_V5_5_4_GENERATOR_SHA256
        or primary.get("provenance", {}).get("test_sha256")
        != EXPECTED_PRIMARY_V5_5_4_TEST_SHA256
        or primary.get("earlier_gate_helpers_imported") != []
    ):
        raise InterfaceWardV554RedteamError("primary v5.5.4 provenance contract mismatch")
    actions = v52.get("exact_classical_charter", {}).get("exact_action", {})
    coefficients = (
        v52.get("exact_classical_charter", {})
        .get("coefficient_policy", {})
        .get("parameters", {})
    )
    for key, expected in EXPECTED_ACTIONS.items():
        if actions.get(key) != expected:
            raise InterfaceWardV554RedteamError(f"v5.2 action drift: {key}")
    definitions = v52.get("exact_classical_charter", {}).get("definitions", {})
    pullback = v52.get("moving_pullback_certificate", {})
    topology = v52.get("exact_classical_charter", {}).get("topology", {})
    actual_control_literals = {
        "associated_trace": definitions.get("associated_trace"),
        "induced_metric": definitions.get("induced_metric"),
        "scalar_pullback": pullback.get("scalar_pullback"),
        "reference_domain": topology.get("reference_domain_formulation"),
    }
    if actual_control_literals != EXPECTED_CONTROL_LITERALS:
        raise InterfaceWardV554RedteamError("v5.2 pullback/groupoid literal drift")
    for key, expected in EXPECTED_COEFFICIENTS.items():
        if float(coefficients.get(key, float("nan"))) != expected:
            raise InterfaceWardV554RedteamError(f"v5.2 coefficient drift: {key}")
    # Deliberately return structural lineage only.  Decision dictionaries and
    # pass flags from upstream receipts are neither exposed nor consumed by the
    # independent calculation or by `_decision` below.
    return {
        "v5_2_schema": v52["schema"],
        "v5_5_2_schema": v552["schema"],
        "v5_5_2_redteam_schema": v552_red["schema"],
        "primary_schema": primary["schema"],
        "primary_generator_sha256": primary["provenance"]["generator_sha256"],
        "primary_test_sha256": primary["provenance"]["test_sha256"],
    }


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


_PAIRS = (
    (0, 0), (0, 1), (0, 2), (0, 3), (1, 1),
    (1, 2), (1, 3), (2, 2), (2, 3), (3, 3),
)
_K = torch.tensor(
    [
        [0.46, -0.31, 0.27, 0.39],
        [-0.28, 0.51, 0.34, -0.22],
        [0.37, 0.24, -0.49, 0.33],
        [0.29, -0.44, 0.31, 0.48],
        [-0.41, 0.32, 0.45, 0.26],
        [0.35, 0.47, -0.23, -0.38],
        [-0.33, 0.29, 0.52, 0.21],
        [0.49, -0.26, -0.36, 0.42],
        [0.22, 0.38, 0.43, -0.47],
        [-0.45, -0.34, 0.25, 0.50],
    ]
)
_PHASE = torch.linspace(-0.52, 0.73, 10)


def _gamma0(x: torch.Tensor) -> torch.Tensor:
    base = torch.tensor([-1.37, 0.0, 0.0, 0.0, 1.18, 0.0, 0.0, 1.04, 0.0, 1.25])
    amplitude = torch.tensor([0.021, 0.012, 0.014, 0.011, 0.025, 0.013, 0.010, 0.023, 0.012, 0.027])
    values = base + amplitude * (
        torch.cos(_K @ x + _PHASE)
        + 0.19 * torch.sin(torch.flip(_K, dims=(1,)) @ x - 0.6 * _PHASE)
        + 0.025 * torch.prod(1.0 + 0.22 * x)
    )
    lookup = {pair: values[index] for index, pair in enumerate(_PAIRS)}
    return torch.stack(
        [
            torch.stack([lookup[(min(mu, nu), max(mu, nu))] for nu in range(4)])
            for mu in range(4)
        ]
    )


def _t0(x: torch.Tensor) -> torch.Tensor:
    return (
        x[0]
        + 0.031 * torch.cos(0.43 * x[0] - 0.37 * x[1] + 0.29 * x[2] + 0.34 * x[3])
        + 0.012 * torch.sin(0.28 * x[0] + 0.41 * x[1] - 0.35 * x[2] + 0.46 * x[3])
        + 0.004 * torch.prod(1.0 + 0.18 * x)
    )


def _omega0(x: torch.Tensor) -> torch.Tensor:
    return (
        1.21
        + 0.044 * torch.cos(0.39 * x[0] + 0.48 * x[1] - 0.33 * x[2] + 0.42 * x[3])
        + 0.016 * torch.sin(0.52 * x[0] - 0.27 * x[1] + 0.37 * x[2] + 0.31 * x[3])
        + 0.006 * torch.prod(1.0 + 0.16 * x)
    )


def _psi0(x: torch.Tensor) -> torch.Tensor:
    return torch.stack(
        [
            0.10 * (mu + 1)
            + 0.039 * torch.cos(_K[mu + 2] @ x + 0.17 * mu)
            + 0.024 * torch.sin(_K[mu + 5] @ x - 0.21 * mu)
            + 0.004 * (mu + 1) * torch.prod(1.0 + 0.12 * x)
            for mu in range(4)
        ]
    )


def _bump(x: torch.Tensor) -> torch.Tensor:
    ratio2 = (x / DOMAIN) ** 2
    inside = ratio2 < 1.0
    denominator = torch.where(inside, 1.0 - ratio2, torch.ones_like(ratio2))
    factors = torch.where(
        inside,
        torch.exp(1.0 - 1.0 / denominator),
        torch.zeros_like(ratio2),
    )
    return torch.prod(factors)


def _xi(x: torch.Tensor, variant: int) -> torch.Tensor:
    bump = _bump(x)
    if variant == 0:
        raw = torch.stack(
            (
                0.24 + torch.cos(0.41 * x[0] - 0.33 * x[1] + 0.29 * x[2] + 0.22 * x[3]),
                -0.18 + torch.sin(0.26 * x[0] + 0.47 * x[1] - 0.31 * x[2] + 0.36 * x[3]),
                0.16 + torch.cos(-0.35 * x[0] + 0.28 * x[1] + 0.44 * x[2] - 0.25 * x[3]),
                -0.20 + torch.sin(0.38 * x[0] - 0.24 * x[1] + 0.32 * x[2] + 0.45 * x[3]),
            )
        )
        return 0.27 * bump * raw
    raw = torch.stack(
        (
            -0.19 + torch.sin(0.36 * x[0] + 0.27 * x[1] - 0.45 * x[2] + 0.31 * x[3]),
            0.22 + torch.cos(-0.29 * x[0] + 0.42 * x[1] + 0.24 * x[2] - 0.37 * x[3]),
            -0.15 + torch.sin(0.47 * x[0] - 0.21 * x[1] + 0.34 * x[2] + 0.39 * x[3]),
            0.17 + torch.cos(0.25 * x[0] + 0.35 * x[1] - 0.28 * x[2] + 0.43 * x[3]),
        )
    )
    return 0.25 * bump * raw


def _lie_slots(x: torch.Tensor, variant: int, *, scalarized_psi: bool = False) -> tuple[torch.Tensor, ...]:
    gamma = _gamma0(x)
    psi = _psi0(x)
    xi = _xi(x, variant)
    d_gamma = jacrev(_gamma0)(x)
    d_t = jacrev(_t0)(x)
    d_omega = jacrev(_omega0)(x)
    d_psi = jacrev(_psi0)(x)
    d_xi = jacrev(lambda z: _xi(z, variant))(x)
    l_gamma = torch.einsum("r,mnr->mn", xi, d_gamma)
    l_gamma = l_gamma + torch.einsum("rn,rm->mn", gamma, d_xi)
    l_gamma = l_gamma + torch.einsum("mr,rn->mn", gamma, d_xi)
    l_t = xi @ d_t
    l_omega = xi @ d_omega
    l_psi = torch.einsum("r,mr->m", xi, d_psi)
    if not scalarized_psi:
        l_psi = l_psi + torch.einsum("r,rm->m", psi, d_xi)
    return l_gamma, l_t, l_omega, l_psi


def _component_direction(slot: str) -> torch.Tensor:
    """Return the explicit sixteen-component tangent used by one Ward slot."""

    direction = torch.zeros(COMPONENT_COUNT)
    if slot == "metric_stress":
        direction[:10] = 1.0
    elif slot == "khronon_T":
        direction[10] = 1.0
    elif slot == "Omega":
        direction[11] = 1.0
    elif slot == "psi_covector":
        direction[12:] = 1.0
    elif slot == "all":
        direction[:] = 1.0
    else:
        raise InterfaceWardV554RedteamError(f"unknown component slot: {slot}")
    return direction


def _fields(x: torch.Tensor, epsilon: torch.Tensor, variant: int, *, scalarized_psi: bool = False) -> tuple[torch.Tensor, ...]:
    slots = _lie_slots(x, variant, scalarized_psi=scalarized_psi)
    pair_position = {pair: index for index, pair in enumerate(_PAIRS)}
    delta_gamma = torch.stack(
        [
            torch.stack(
                [
                    epsilon[pair_position[(min(mu, nu), max(mu, nu))]]
                    * slots[0][mu, nu]
                    for nu in range(4)
                ]
            )
            for mu in range(4)
        ]
    )
    delta_psi = torch.stack(
        [epsilon[12 + mu] * slots[3][mu] for mu in range(4)]
    )
    return (
        _gamma0(x) + delta_gamma,
        _t0(x) + epsilon[10] * slots[1],
        _omega0(x) + epsilon[11] * slots[2],
        _psi0(x) + delta_psi,
    )


def _christoffel(x: torch.Tensor, epsilon: torch.Tensor, variant: int, *, scalarized_psi: bool = False) -> torch.Tensor:
    gamma = _fields(x, epsilon, variant, scalarized_psi=scalarized_psi)[0]
    inverse = torch.linalg.inv(gamma)
    derivative = jacrev(
        lambda z: _fields(z, epsilon, variant, scalarized_psi=scalarized_psi)[0]
    )(x)
    lowered = torch.stack(
        [
            torch.stack(
                [
                    torch.stack(
                        [
                            derivative[sigma, nu, mu]
                            + derivative[sigma, mu, nu]
                            - derivative[mu, nu, sigma]
                            for nu in range(4)
                        ]
                    )
                    for mu in range(4)
                ]
            )
            for sigma in range(4)
        ]
    )
    return 0.5 * torch.einsum("rs,smn->rmn", inverse, lowered)


def _u_covector(x: torch.Tensor, epsilon: torch.Tensor, variant: int, *, scalarized_psi: bool = False) -> torch.Tensor:
    gamma, _, _, _ = _fields(x, epsilon, variant, scalarized_psi=scalarized_psi)
    inverse = torch.linalg.inv(gamma)
    d_t = jacrev(
        lambda z: _fields(z, epsilon, variant, scalarized_psi=scalarized_psi)[1]
    )(x)
    norm = d_t @ inverse @ d_t
    return -d_t / torch.sqrt(-norm)


def _density_point(
    x: torch.Tensor,
    epsilon: torch.Tensor,
    variant: int,
    *,
    scalarized_psi: bool = False,
    omit_wall_density_weight: bool = False,
) -> torch.Tensor:
    gamma, _, omega, psi = _fields(
        x, epsilon, variant, scalarized_psi=scalarized_psi
    )
    inverse = torch.linalg.inv(gamma)
    determinant = torch.linalg.det(gamma)
    sqrt_gamma = torch.sqrt(-determinant)
    christoffel = _christoffel(
        x, epsilon, variant, scalarized_psi=scalarized_psi
    )
    d_christoffel = jacrev(
        lambda z: _christoffel(
            z, epsilon, variant, scalarized_psi=scalarized_psi
        )
    )(x)
    ricci_rows = []
    for mu in range(4):
        entries = []
        for nu in range(4):
            derivative = sum(
                d_christoffel[rho, mu, nu, rho]
                - d_christoffel[rho, mu, rho, nu]
                for rho in range(4)
            )
            quadratic = sum(
                christoffel[rho, rho, lam] * christoffel[lam, mu, nu]
                - christoffel[rho, nu, lam] * christoffel[lam, mu, rho]
                for rho in range(4)
                for lam in range(4)
            )
            entries.append(derivative + quadratic)
        ricci_rows.append(torch.stack(entries))
    ricci = torch.stack(ricci_rows)
    scalar_r = torch.einsum("mn,mn->", inverse, ricci)

    u_cov = _u_covector(
        x, epsilon, variant, scalarized_psi=scalarized_psi
    )
    u_up = inverse @ u_cov
    h_contra = inverse + torch.outer(u_up, u_up)
    projector = torch.eye(4) + torch.outer(u_cov, u_up)
    d_u = jacrev(
        lambda z: _u_covector(
            z, epsilon, variant, scalarized_psi=scalarized_psi
        )
    )(x)
    nabla_u = d_u.T - torch.einsum("rmn,r->mn", christoffel, u_cov)
    k_cov = torch.einsum("ma,nb,ab->mn", projector, projector, nabla_u)
    k_trace = torch.einsum("mn,mn->", h_contra, k_cov)
    k_squared = torch.einsum("ma,nb,mn,ab->", h_contra, h_contra, k_cov, k_cov)
    a_cov = torch.einsum("n,nm->m", u_up, nabla_u)
    a_squared = a_cov @ h_contra @ a_cov
    ricci_uu = u_up @ ricci @ u_up
    r_cal = scalar_r + 2.0 * ricci_uu + k_trace * k_trace - k_squared
    foliation = 0.5 * MB2 * (
        k_squared
        - LAMBDA_K * k_trace * k_trace
        + XI_R * r_cal
        + ETA * a_squared
        - B4_BAR * r_cal * r_cal / (16.0 * K_INFINITY**2)
    )
    w = 3.0 * M5 * K_INFINITY * torch.exp(
        -G_OMEGA * omega * omega / (6.0 * M5)
    )
    wall = -(2.0 * w + 0.5 * BETA * (omega - 1.0) ** 2)
    robin_cov = psi - ROBIN_Y * a_cov
    robin = -0.5 * KAPPA * (robin_cov @ h_contra @ robin_cov)
    if omit_wall_density_weight:
        return sqrt_gamma * (foliation + robin) + wall
    return sqrt_gamma * (foliation + wall + robin)


def _rebuilt_neutral_primitives(
    x: torch.Tensor,
    epsilon: torch.Tensor,
    variant: int,
    *,
    scalarized_psi: bool = False,
) -> dict[str, torch.Tensor]:
    """Geometry-only primitives shared by separately assembled audit routes."""

    gamma, _, omega, psi = _fields(
        x, epsilon, variant, scalarized_psi=scalarized_psi
    )
    inverse = torch.linalg.inv(gamma)
    sqrt_gamma = torch.sqrt(-torch.linalg.det(gamma))
    christoffel = _christoffel(
        x, epsilon, variant, scalarized_psi=scalarized_psi
    )
    d_christoffel = jacrev(
        lambda z: _christoffel(
            z, epsilon, variant, scalarized_psi=scalarized_psi
        )
    )(x)
    ricci = torch.stack(
        [
            torch.stack(
                [
                    sum(
                        d_christoffel[rho, mu, nu, rho]
                        - d_christoffel[rho, mu, rho, nu]
                        for rho in range(4)
                    )
                    + sum(
                        christoffel[rho, rho, lam] * christoffel[lam, mu, nu]
                        - christoffel[rho, nu, lam] * christoffel[lam, mu, rho]
                        for rho in range(4)
                        for lam in range(4)
                    )
                    for nu in range(4)
                ]
            )
            for mu in range(4)
        ]
    )
    scalar_r = torch.einsum("mn,mn->", inverse, ricci)
    u_cov = _u_covector(
        x, epsilon, variant, scalarized_psi=scalarized_psi
    )
    u_up = inverse @ u_cov
    h_contra = inverse + torch.outer(u_up, u_up)
    projector = torch.eye(4) + torch.outer(u_cov, u_up)
    d_u = jacrev(
        lambda z: _u_covector(
            z, epsilon, variant, scalarized_psi=scalarized_psi
        )
    )(x)
    nabla_u = d_u.T - torch.einsum("rmn,r->mn", christoffel, u_cov)
    k_cov = torch.einsum("ma,nb,ab->mn", projector, projector, nabla_u)
    k_trace = torch.einsum("mn,mn->", h_contra, k_cov)
    k_squared = torch.einsum(
        "ma,nb,mn,ab->", h_contra, h_contra, k_cov, k_cov
    )
    a_cov = torch.einsum("n,nm->m", u_up, nabla_u)
    a_squared = a_cov @ h_contra @ a_cov
    r_cal = (
        scalar_r
        + 2.0 * (u_up @ ricci @ u_up)
        + k_trace * k_trace
        - k_squared
    )
    return {
        "sqrt_gamma": sqrt_gamma,
        "omega": omega,
        "psi": psi,
        "h_contra": h_contra,
        "a_cov": a_cov,
        "a_squared": a_squared,
        "k_trace": k_trace,
        "k_squared": k_squared,
        "Rcal": r_cal,
    }


def _jvp_density_point(
    x: torch.Tensor,
    epsilon: torch.Tensor,
    variant: int,
    *,
    scalarized_psi: bool = False,
) -> torch.Tensor:
    """Local-JVP density, assembled separately from the action evaluator."""

    row = _rebuilt_neutral_primitives(
        x, epsilon, variant, scalarized_psi=scalarized_psi
    )
    r_cal = row["Rcal"]
    foliation = (MB2 / 2.0) * (
        row["k_squared"]
        - LAMBDA_K * row["k_trace"] ** 2
        + XI_R * r_cal
        + ETA * row["a_squared"]
        - B4_BAR * r_cal**2 / (16.0 * K_INFINITY**2)
    )
    omega = row["omega"]
    superpotential = 3.0 * M5 * K_INFINITY * torch.exp(
        -G_OMEGA * omega**2 / (6.0 * M5)
    )
    wall = -2.0 * superpotential - 0.5 * BETA * (omega - 1.0) ** 2
    robin_vector = row["psi"] - ROBIN_Y * row["a_cov"]
    robin = -(KAPPA / 2.0) * (
        robin_vector @ row["h_contra"] @ robin_vector
    )
    return row["sqrt_gamma"] * foliation + row["sqrt_gamma"] * wall + row[
        "sqrt_gamma"
    ] * robin


def _stokes_density_point(
    x: torch.Tensor,
    epsilon: torch.Tensor,
    variant: int,
) -> torch.Tensor:
    """Boundary density with an independent literal sector assembly."""

    row = _rebuilt_neutral_primitives(x, epsilon, variant)
    omega = row["omega"]
    r_cal = row["Rcal"]
    wall_sector = -(
        6.0
        * M5
        * K_INFINITY
        * torch.exp(-G_OMEGA * omega**2 / (6.0 * M5))
        + 0.5 * BETA * (omega - 1.0) ** 2
    )
    q_cov = row["psi"] - ROBIN_Y * row["a_cov"]
    robin_sector = -0.5 * KAPPA * torch.einsum(
        "m,mn,n->", q_cov, row["h_contra"], q_cov
    )
    foliation_sector = 0.5 * MB2 * (
        row["k_squared"]
        - LAMBDA_K * row["k_trace"] * row["k_trace"]
        + XI_R * r_cal
        + ETA * row["a_squared"]
        - (B4_BAR / (16.0 * K_INFINITY**2)) * r_cal * r_cal
    )
    return row["sqrt_gamma"] * (
        wall_sector + robin_sector + foliation_sector
    )


def _quadrature(order: int) -> tuple[torch.Tensor, torch.Tensor]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    nodes = DOMAIN * nodes
    weights = DOMAIN * weights
    meshes = np.meshgrid(nodes, nodes, nodes, nodes, indexing="ij")
    weight_meshes = np.meshgrid(weights, weights, weights, weights, indexing="ij")
    points = torch.as_tensor(np.stack([mesh.reshape(-1) for mesh in meshes], axis=1))
    combined = torch.as_tensor(
        np.prod(np.stack(weight_meshes, axis=-1), axis=-1).reshape(-1)
    )
    return points, combined


def _density_batch(
    points: torch.Tensor,
    epsilon: torch.Tensor,
    variant: int,
    *,
    scalarized_psi: bool = False,
    omit_wall_density_weight: bool = False,
) -> torch.Tensor:
    return vmap(
        lambda point: _density_point(
            point,
            epsilon,
            variant,
            scalarized_psi=scalarized_psi,
            omit_wall_density_weight=omit_wall_density_weight,
        )
    )(points)


def _jvp_density_batch(
    points: torch.Tensor,
    epsilon: torch.Tensor,
    variant: int,
) -> torch.Tensor:
    return vmap(
        lambda point: _jvp_density_point(point, epsilon, variant)
    )(points)


def _stokes_density_batch(
    points: torch.Tensor,
    epsilon: torch.Tensor,
    variant: int,
) -> torch.Tensor:
    return vmap(
        lambda point: _stokes_density_point(point, epsilon, variant)
    )(points)


def _action(
    points: torch.Tensor,
    weights: torch.Tensor,
    epsilon: torch.Tensor,
    variant: int,
    *,
    scalarized_psi: bool = False,
    omit_wall_density_weight: bool = False,
) -> torch.Tensor:
    return weights @ _density_batch(
        points,
        epsilon,
        variant,
        scalarized_psi=scalarized_psi,
        omit_wall_density_weight=omit_wall_density_weight,
    )


def _stokes_boundary_certificate(face_order: int, variant: int) -> dict[str, Any]:
    """Independently integrate xi^mu*density over all eight oriented faces."""

    nodes, weights = np.polynomial.legendre.leggauss(face_order)
    nodes = DOMAIN * nodes
    weights = DOMAIN * weights
    meshes = np.meshgrid(nodes, nodes, nodes, indexing="ij")
    weight_meshes = np.meshgrid(weights, weights, weights, indexing="ij")
    tangential = np.stack([mesh.reshape(-1) for mesh in meshes], axis=1)
    face_weights = torch.as_tensor(
        np.prod(np.stack(weight_meshes, axis=-1), axis=-1).reshape(-1)
    )
    zero = torch.zeros(COMPONENT_COUNT)
    faces: list[dict[str, Any]] = []
    total_flux = 0.0
    maximum_xi = 0.0
    maximum_density = 0.0
    maximum_flux_density = 0.0
    for axis in range(4):
        tangential_axes = [index for index in range(4) if index != axis]
        for sign in (-1.0, 1.0):
            face_points = np.zeros((face_order**3, 4), dtype=float)
            face_points[:, axis] = sign * DOMAIN
            face_points[:, tangential_axes] = tangential
            points = torch.as_tensor(face_points)
            xis = vmap(lambda point: _xi(point, variant))(points).detach()
            densities = _stokes_density_batch(points, zero, variant).detach()
            oriented_flux_density = sign * xis[:, axis] * densities
            integrated_flux = float(face_weights @ oriented_flux_density)
            xi_max = float(torch.max(torch.abs(xis)))
            density_max = float(torch.max(torch.abs(densities)))
            flux_density_max = float(torch.max(torch.abs(oriented_flux_density)))
            total_flux += integrated_flux
            maximum_xi = max(maximum_xi, xi_max)
            maximum_density = max(maximum_density, density_max)
            maximum_flux_density = max(maximum_flux_density, flux_density_max)
            faces.append(
                {
                    "axis": axis,
                    "sign": int(sign),
                    "point_count": face_order**3,
                    "xi_max": xi_max,
                    "action_density_max": density_max,
                    "oriented_flux_density_max": flux_density_max,
                    "integrated_oriented_flux": integrated_flux,
                }
            )
    return {
        "Stokes_convention": (
            "int_M partial_mu(xi^mu density)="
            "sum_faces int sign_mu xi^mu density"
        ),
        "face_quadrature_order": face_order,
        "face_count": len(faces),
        "faces": faces,
        "maximum_boundary_xi": maximum_xi,
        "maximum_boundary_action_density": maximum_density,
        "maximum_boundary_flux_density": maximum_flux_density,
        "total_oriented_boundary_flux": total_flux,
        "total_oriented_boundary_flux_absolute": abs(total_flux),
        "boundary_zero_obtained_from_runtime_fields": bool(
            maximum_xi == 0.0
            and maximum_flux_density == 0.0
            and maximum_density > 0.0
        ),
    }


def _central_action_direction(
    points: torch.Tensor,
    weights: torch.Tensor,
    direction: torch.Tensor,
    variant: int,
    step: float,
    *,
    scalarized_psi: bool = False,
    omit_wall_density_weight: bool = False,
) -> torch.Tensor:
    return (
        _action(
            points,
            weights,
            step * direction,
            variant,
            scalarized_psi=scalarized_psi,
            omit_wall_density_weight=omit_wall_density_weight,
        )
        - _action(
            points,
            weights,
            -step * direction,
            variant,
            scalarized_psi=scalarized_psi,
            omit_wall_density_weight=omit_wall_density_weight,
        )
    ) / (2.0 * step)


def _local_density_and_divergence(
    point: torch.Tensor,
    variant: int,
    step: float,
    *,
    omit_density_jacobian: bool = False,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    zero = torch.zeros(COMPONENT_COUNT)
    ones = torch.ones(COMPONENT_COUNT)
    base, varied = jvp(
        lambda epsilon: _jvp_density_point(point, epsilon, variant),
        (zero,),
        (ones,),
    )
    base_function = lambda x: _jvp_density_point(x, zero, variant)
    gradient = jacrev(base_function)(point)
    xi = _xi(point, variant)
    d_xi = jacrev(lambda x: _xi(x, variant))(point)
    transport = xi @ gradient
    jacobian_term = base * torch.trace(d_xi)
    divergence = transport if omit_density_jacobian else transport + jacobian_term
    return varied, divergence, transport, jacobian_term


def _component_jvp_rows(
    points: torch.Tensor,
    weights: torch.Tensor,
    variant: int,
    step: float,
) -> list[dict[str, Any]]:
    """Signed local JVP and independent finite-action value for all 16 slots."""

    zero = torch.zeros(COMPONENT_COUNT)
    basis = torch.eye(COMPONENT_COUNT)
    rows: list[dict[str, Any]] = []
    for index, label in enumerate(COMPONENT_LABELS):
        direction = basis[index]
        _, local_value = jvp(
            lambda epsilon: _jvp_density_batch(points, epsilon, variant),
            (zero,),
            (direction,),
        )
        action_value = _central_action_direction(
            points, weights, direction, variant, step
        )
        integrated_jvp = weights @ local_value
        raw = local_value.detach()
        rows.append(
            {
                "component": label,
                "signed_finite_action_derivative": float(action_value),
                "signed_integrated_local_JVP": float(integrated_jvp.detach()),
                "action_vs_JVP_absolute_error": abs(
                    float(action_value - integrated_jvp.detach())
                ),
                "signed_local_JVP_values": [float(value) for value in raw],
                "local_JVP_min": float(torch.min(raw)),
                "local_JVP_max": float(torch.max(raw)),
                "local_JVP_RMS": float(torch.sqrt(torch.mean(raw**2))),
            }
        )
    return rows


def _probe(order: int, variant: int) -> dict[str, Any]:
    points, weights = _quadrature(order)
    fine = 2.0e-5
    coarse = 4.0e-5
    slots: dict[str, float] = {}
    convergence: dict[str, float] = {}
    slot_names = ("metric_stress", "khronon_T", "Omega", "psi_covector")
    for name in slot_names:
        direction = _component_direction(name)
        fine_value = _central_action_direction(
            points, weights, direction, variant, fine
        )
        coarse_value = _central_action_direction(
            points, weights, direction, variant, coarse
        )
        slots[name] = float(fine_value)
        convergence[name] = abs(float(fine_value - coarse_value))
    all_direction = _component_direction("all")
    direct_all = _central_action_direction(
        points, weights, all_direction, variant, fine
    )
    direct_all_coarse = _central_action_direction(
        points, weights, all_direction, variant, coarse
    )
    local_rows = vmap(
        lambda point: torch.stack(
            _local_density_and_divergence(point, variant, fine)
        )
    )(points)
    omit_jacobian_rows = vmap(
        lambda point: torch.stack(
            _local_density_and_divergence(
                point, variant, fine, omit_density_jacobian=True
            )
        )
    )(points)
    local_variation = local_rows[:, 0]
    divergence = local_rows[:, 1]
    transport = local_rows[:, 2]
    jacobian_term = local_rows[:, 3]
    local_residual = local_variation - divergence
    integrated_divergence = weights @ divergence
    scalarized = _central_action_direction(
        points,
        weights,
        all_direction,
        variant,
        fine,
        scalarized_psi=True,
    )
    bad_weight = _central_action_direction(
        points,
        weights,
        all_direction,
        variant,
        fine,
        omit_wall_density_weight=True,
    )
    weak_sum = sum(slots.values())
    component_rows = _component_jvp_rows(points, weights, variant, fine)
    zero_components = torch.zeros(COMPONENT_COUNT)
    _, joint_local_jvp = jvp(
        lambda epsilon: _jvp_density_batch(points, epsilon, variant),
        (zero_components,),
        (_component_direction("all"),),
    )
    summed_component_jvp = torch.stack(
        [
            torch.as_tensor(row["signed_local_JVP_values"])
            for row in component_rows
        ]
    ).sum(dim=0)
    action_density_values = _density_batch(points, zero_components, variant).detach()
    jvp_density_values = _jvp_density_batch(points, zero_components, variant).detach()
    stokes_density_values = _stokes_density_batch(
        points, zero_components, variant
    ).detach()
    reference_divergence = float(integrated_divergence.detach())
    executed_mutants: dict[str, dict[str, float | str]] = {}
    for name in slot_names:
        slot_direction = _component_direction(name)
        for operation, mutant_direction in (
            ("omit", all_direction - slot_direction),
            ("flip_sign", all_direction - 2.0 * slot_direction),
        ):
            mutant_value = _central_action_direction(
                points, weights, mutant_direction, variant, fine
            )
            key = f"{operation}_{name}"
            executed_mutants[key] = {
                "route": "re-evaluated finite action with mutated Lie direction",
                "signed_mutant_action_derivative": float(mutant_value),
                "signed_reference_local_divergence": reference_divergence,
                "mutant_residual": abs(float(mutant_value) - reference_divergence),
            }
    executed_mutants["scalarize_psi_covector"] = {
        "route": "re-evaluated action with covector Jacobian leg removed",
        "signed_mutant_action_derivative": float(scalarized),
        "signed_reference_local_divergence": reference_divergence,
        "mutant_residual": abs(float(scalarized) - reference_divergence),
    }
    executed_mutants["omit_density_Jacobian"] = {
        "route": "re-evaluated local identity without density*partial_mu_xi^mu",
        "signed_mutant_action_derivative": float(weights @ local_variation),
        "signed_reference_local_divergence": float(weights @ omit_jacobian_rows[:, 1]),
        "mutant_residual": float(
            torch.sqrt(
                torch.mean(
                    (omit_jacobian_rows[:, 0] - omit_jacobian_rows[:, 1]) ** 2
                )
            )
        ),
    }
    executed_mutants["omit_sqrt_gamma_from_wall"] = {
        "route": "re-evaluated finite action with wall density weight removed",
        "signed_mutant_action_derivative": float(bad_weight),
        "signed_reference_local_divergence": reference_divergence,
        "mutant_residual": abs(float(bad_weight) - reference_divergence),
    }
    forced_t_on_shell = _central_action_direction(
        points,
        weights,
        all_direction - _component_direction("khronon_T"),
        variant,
        fine,
    )
    executed_mutants["force_khronon_E_T_on_shell"] = {
        "route": "re-evaluated finite action with the T Lie direction omitted",
        "signed_mutant_action_derivative": float(forced_t_on_shell),
        "signed_reference_local_divergence": reference_divergence,
        "mutant_residual": abs(float(forced_t_on_shell) - reference_divergence),
    }
    return {
        "quadrature_order": order,
        "point_count": order**4,
        "xi_variant": variant,
        "finite_difference_Euler_slot_pairings": slots,
        "signed_component_action_and_local_JVP": component_rows,
        "component_action_JVP_tolerance": COMPONENT_ACTION_JVP_TOLERANCE,
        "maximum_component_action_vs_JVP_error": max(
            row["action_vs_JVP_absolute_error"] for row in component_rows
        ),
        "minimum_component_local_JVP_RMS": min(
            row["local_JVP_RMS"] for row in component_rows
        ),
        "component_JVP_additivity": {
            "signed_joint_local_JVP_values": [
                float(value) for value in joint_local_jvp.detach()
            ],
            "signed_sum_of_16_local_JVP_values": [
                float(value) for value in summed_component_jvp
            ],
            "pointwise_Linf_error": float(
                torch.max(
                    torch.abs(joint_local_jvp.detach() - summed_component_jvp)
                )
            ),
        },
        "independent_density_route_comparison": {
            "action_vs_JVP_Linf": float(
                torch.max(torch.abs(action_density_values - jvp_density_values))
            ),
            "action_vs_Stokes_Linf": float(
                torch.max(torch.abs(action_density_values - stokes_density_values))
            ),
            "signed_action_density_values": [
                float(value) for value in action_density_values
            ],
            "signed_JVP_density_values": [
                float(value) for value in jvp_density_values
            ],
            "signed_Stokes_density_values": [
                float(value) for value in stokes_density_values
            ],
        },
        "slot_step_convergence": convergence,
        "minimum_absolute_slot_pairing": min(abs(value) for value in slots.values()),
        "underresolved_Gauss_volume_weak_Euler_sum": weak_sum,
        "underresolved_Gauss_volume_weak_absolute_value": abs(weak_sum),
        "underresolved_Gauss_volume_used_as_zero_gate": False,
        "direct_all_field_derivative": float(direct_all),
        "direct_all_vs_slot_sum_error": abs(float(direct_all) - weak_sum),
        "direct_all_step_convergence": abs(float(direct_all - direct_all_coarse)),
        "integrated_coordinate_divergence": float(integrated_divergence),
        "weak_sum_vs_divergence_error": abs(weak_sum - float(integrated_divergence)),
        "local_density_covariance_L2": float(torch.sqrt(torch.mean(local_residual**2))),
        "local_density_covariance_Linf": float(torch.max(torch.abs(local_residual))),
        "density_variation_RMS": float(torch.sqrt(torch.mean(local_variation**2))),
        "transport_RMS": float(torch.sqrt(torch.mean(transport**2))),
        "density_Jacobian_term_RMS": float(torch.sqrt(torch.mean(jacobian_term**2))),
        "xi_RMS": float(torch.sqrt(torch.mean(vmap(lambda x: _xi(x, variant))(points) ** 2))),
        "executed_mutants": executed_mutants,
        "mutant_witnesses": {
            name: float(row["mutant_residual"])
            for name, row in executed_mutants.items()
        },
    }


def _hat3(vector: torch.Tensor) -> torch.Tensor:
    x, y, z = vector
    zero = torch.zeros((), dtype=vector.dtype)
    return torch.stack(
        (
            torch.stack((zero, -z, y)),
            torch.stack((z, zero, -x)),
            torch.stack((-y, x, zero)),
        )
    )


def _groupoid_frozen_R_control() -> dict[str, Any]:
    """Derive delta R=-R hat(lambda) from varphi_H=R phi."""

    phi = torch.tensor([0.37, -0.24, 0.19])
    gauge_parameter = torch.tensor([0.31, -0.18, 0.27])
    r_groupoid = torch.matrix_exp(_hat3(torch.tensor([0.22, -0.16, 0.11])))
    generator = _hat3(gauge_parameter)
    step = 2.0e-5

    def trace(epsilon: float, *, frozen_r: bool) -> torch.Tensor:
        source_rotation = torch.matrix_exp(epsilon * generator)
        moved_phi = source_rotation @ phi
        moved_r = (
            r_groupoid
            if frozen_r
            else r_groupoid @ torch.matrix_exp(-epsilon * generator)
        )
        return moved_r @ moved_phi

    nominal = (trace(step, frozen_r=False) - trace(-step, frozen_r=False)) / (
        2.0 * step
    )
    frozen = (trace(step, frozen_r=True) - trace(-step, frozen_r=True)) / (
        2.0 * step
    )
    return {
        "literal_origin": "varphi_H=j(Y^*phi) and equivariance of the groupoid representative",
        "derived_groupoid_variation": "delta R_groupoid=-R_groupoid hat(lambda)",
        "R_is_groupoid_data_not_an_independent_bifundamental_field": True,
        "signed_nominal_delta_varphi_H": nominal.tolist(),
        "signed_frozen_R_delta_varphi_H": frozen.tolist(),
        "nominal_invariance_error": float(torch.linalg.vector_norm(nominal)),
        "frozen_R_mutant_witness": float(torch.linalg.vector_norm(frozen)),
        "R_orthogonality_error": float(
            torch.linalg.matrix_norm(r_groupoid.T @ r_groupoid - torch.eye(3))
        ),
        "R_determinant_error": abs(float(torch.linalg.det(r_groupoid)) - 1.0),
    }


def _induced_pullback_control() -> dict[str, Any]:
    """Re-evaluate a genuine 4D-to-5D induced metric pullback."""

    point = torch.tensor([0.12, -0.17, 0.09, 0.21])

    def embedding(x: torch.Tensor) -> torch.Tensor:
        normal = 0.13 * torch.sin(
            0.37 * x[0] - 0.29 * x[1] + 0.41 * x[2] + 0.33 * x[3]
        )
        return torch.cat((x, normal.reshape(1)))

    def displacement(x: torch.Tensor) -> torch.Tensor:
        tangential = _xi(x, 0)
        normal = 0.19 * _bump(x) * (
            1.0 + 0.17 * torch.cos(0.31 * x[0] + 0.26 * x[3])
        )
        return torch.cat((tangential, normal.reshape(1)))

    def bulk_metric(y: torch.Tensor) -> torch.Tensor:
        diagonal = torch.stack(
            (
                -1.42 - 0.021 * torch.cos(0.31 * y[0] + 0.22 * y[4]),
                1.19 + 0.024 * torch.sin(0.27 * y[1] - 0.18 * y[4]),
                1.11 + 0.019 * torch.cos(0.23 * y[2] + 0.29 * y[4]),
                1.27 + 0.022 * torch.sin(0.25 * y[3] - 0.21 * y[4]),
                1.08 + 0.017 * torch.cos(0.28 * y[0] + 0.24 * y[4]),
            )
        )
        metric = torch.diag(diagonal)
        mixing = 0.012 * torch.sin(0.21 * y[1] + 0.17 * y[4])
        basis_14 = torch.zeros((5, 5))
        basis_14[1, 4] = 1.0
        basis_14[4, 1] = 1.0
        return metric + mixing * basis_14

    y0 = embedding(point)
    zeta = displacement(point)
    jacobian0 = jacrev(embedding)(point)
    delta_jacobian = jacrev(displacement)(point)
    step = 2.0e-5

    def pulled(epsilon: float, *, broken: bool) -> torch.Tensor:
        moved_embedding = lambda x: embedding(x) + epsilon * displacement(x)
        moved_y = moved_embedding(point)
        ambient_metric = bulk_metric(moved_y)
        if broken:
            return jacobian0.T @ ambient_metric @ jacobian0
        jacobian = jacrev(moved_embedding)(point)
        return jacobian.T @ ambient_metric @ jacobian

    nominal = (pulled(step, broken=False) - pulled(-step, broken=False)) / (
        2.0 * step
    )
    broken = (pulled(step, broken=True) - pulled(-step, broken=True)) / (
        2.0 * step
    )
    metric0 = bulk_metric(y0)
    metric_derivative = jacrev(bulk_metric)(y0)
    transported_metric = torch.einsum("c,abc->ab", zeta, metric_derivative)
    expected = (
        delta_jacobian.T @ metric0 @ jacobian0
        + jacobian0.T @ metric0 @ delta_jacobian
        + jacobian0.T @ transported_metric @ jacobian0
    )
    nominal_residual = nominal - expected
    broken_residual = broken - expected
    return {
        "literal_origin": "gamma_mu_nu=Y^*g_MN for Y:Sigma_4->M_5",
        "ambient_dimension": 5,
        "interface_dimension": 4,
        "pullback_formula": "Y_epsilon^*g=J_epsilon^T g(Y_epsilon) J_epsilon",
        "broken_mutant": "move g(Y_epsilon) but freeze both induced Jacobian legs",
        "normal_embedding_displacement": float(zeta[4]),
        "symmetric_components": [f"gamma_{mu}{nu}" for mu, nu in _PAIRS],
        "signed_finite_pullback_derivative": [
            float(nominal[mu, nu]) for mu, nu in _PAIRS
        ],
        "signed_Lie_derivative_prediction": [
            float(expected[mu, nu]) for mu, nu in _PAIRS
        ],
        "signed_broken_pullback_derivative": [
            float(broken[mu, nu]) for mu, nu in _PAIRS
        ],
        "nominal_pullback_max_error": float(torch.max(torch.abs(nominal_residual))),
        "broken_pullback_mutant_witness": float(
            torch.linalg.matrix_norm(broken_residual)
        ),
    }


def _adm_metric_rebuilt(
    lapse: float, shift: np.ndarray, spatial_metric: np.ndarray
) -> np.ndarray:
    metric = np.zeros((4, 4), dtype=float)
    metric[1:, 1:] = spatial_metric
    metric[0, 1:] = spatial_metric @ shift
    metric[1:, 0] = metric[0, 1:]
    metric[0, 0] = -lapse**2 + float(shift @ spatial_metric @ shift)
    return metric


def _v4_numpy(argument: float) -> float:
    return argument**4 / (2.0 * math.sqrt(1.0 + argument**4))


def _matter_T_ui_control() -> dict[str, Any]:
    """Rebuild the v5.2 matter shift derivative and execute its omission."""

    lapse = 1.31
    shift = np.asarray([0.21, -0.14, 0.09], dtype=float)
    spatial_metric = np.asarray(
        [[1.36, 0.12, -0.07], [0.12, 1.17, 0.08], [-0.07, 0.08, 1.02]],
        dtype=float,
    )
    p_cov = np.asarray(
        [
            [0.73, -0.32, 0.25],
            [0.39, 0.24, -0.28],
            [-0.26, 0.49, 0.17],
            [0.34, -0.22, 0.46],
        ],
        dtype=float,
    )
    p_normal = np.asarray([0.19, -0.13, 0.08], dtype=float)
    phi = np.asarray([0.33, -0.21, 0.17], dtype=float)
    omega = 1.22

    def material_potential() -> float:
        rho = float(np.linalg.norm(phi))
        return Z5 * MATERIAL_M**2 * omega**-5.0 * _v4_numpy(
            omega**1.5 * rho
        )

    def matter_action(varied_shift: np.ndarray) -> float:
        inverse_h = np.linalg.inv(spatial_metric)
        p_u = (
            p_cov[0] - np.einsum("i,ia->a", varied_shift, p_cov[1:])
        ) / lapse
        spatial_norm = float(
            np.einsum("ij,ia,ja->", inverse_h, p_cov[1:], p_cov[1:])
        )
        lagrangian = (
            0.5 * Z5 * float(p_u @ p_u)
            - 0.5 * Z5 * spatial_norm
            - 0.5 * Z5 * float(p_normal @ p_normal)
            - material_potential()
        )
        return lapse * math.sqrt(float(np.linalg.det(spatial_metric))) * lagrangian

    step = 2.0e-6
    numerical = []
    for index in range(3):
        basis = np.eye(3)[index]
        numerical.append(
            (
                matter_action(shift + step * basis)
                - matter_action(shift - step * basis)
            )
            / (2.0 * step)
        )
    numerical = np.asarray(numerical) / (
        lapse * math.sqrt(float(np.linalg.det(spatial_metric)))
    )

    gamma = _adm_metric_rebuilt(lapse, shift, spatial_metric)
    gamma_inverse = np.linalg.inv(gamma)
    p_up = gamma_inverse @ p_cov
    p_squared = float(np.einsum("mn,ma,na->", gamma_inverse, p_cov, p_cov))
    p_squared += float(p_normal @ p_normal)
    matter_lagrangian = -0.5 * Z5 * p_squared - material_potential()
    stress = Z5 * np.einsum("ma,na->mn", p_up, p_up)
    stress += matter_lagrangian * gamma_inverse
    u_cov = np.asarray([-lapse, 0.0, 0.0, 0.0])
    t_ui = np.asarray(u_cov @ stress @ gamma[:, 1:], dtype=float)
    prediction = -t_ui / lapse
    omitted_prediction = np.zeros(3, dtype=float)
    flipped_prediction = t_ui / lapse
    return {
        "literal_origin": "bulk_gauged matter action and E_shift_i^matter=-T_ui/N",
        "signed_T_ui_components": t_ui.tolist(),
        "signed_covariant_shift_prediction": prediction.tolist(),
        "signed_finite_action_shift_derivative": numerical.tolist(),
        "signed_omit_T_ui_equation_prediction": omitted_prediction.tolist(),
        "signed_flip_T_ui_sign_prediction": flipped_prediction.tolist(),
        "nominal_shift_max_error": float(np.max(np.abs(numerical - prediction))),
        "T_ui_activity_norm": float(np.linalg.norm(t_ui)),
        "minimum_absolute_T_ui_component": float(np.min(np.abs(t_ui))),
        "omit_T_ui_matter_mutant_witness": float(
            np.linalg.norm(numerical - omitted_prediction)
        ),
        "flip_T_ui_sign_mutant_witness": float(
            np.linalg.norm(numerical - flipped_prediction)
        ),
        "full_radial_V4_potential_value": material_potential(),
    }


def _anisotropic_V4_control() -> dict[str, Any]:
    """Execute radial full-V4 and anisotropic-potential gauge variations."""

    phi = torch.tensor([0.36, -0.23, 0.18])
    omega = torch.tensor(1.19)
    generator = _hat3(torch.tensor([0.29, -0.17, 0.26]))
    identity_metric = torch.eye(3)
    anisotropic_metric = torch.diag(torch.tensor([1.0, 1.43, 0.71]))
    step = 2.0e-5

    def potential(epsilon: float, metric: torch.Tensor) -> torch.Tensor:
        moved_phi = torch.matrix_exp(epsilon * generator) @ phi
        rho = torch.sqrt(moved_phi @ metric @ moved_phi)
        argument = omega**1.5 * rho
        v4 = argument**4 / (2.0 * torch.sqrt(1.0 + argument**4))
        return -Z5 * MATERIAL_M**2 * omega**-5.0 * v4

    radial = (potential(step, identity_metric) - potential(-step, identity_metric)) / (
        2.0 * step
    )
    anisotropic = (
        potential(step, anisotropic_metric)
        - potential(-step, anisotropic_metric)
    ) / (2.0 * step)
    return {
        "literal_origin": "-Z5*M^2*Omega^-5*V4(Omega^(3/2)*|phi|)",
        "V4_formula": "r^4/(2*sqrt(1+r^4))",
        "signed_radial_gauge_derivative": float(radial),
        "signed_anisotropic_gauge_derivative": float(anisotropic),
        "radial_potential_activity": abs(float(potential(0.0, identity_metric))),
        "anisotropic_V4_mutant_witness": abs(float(anisotropic)),
        "anisotropic_metric_diagonal": [1.0, 1.43, 0.71],
    }


def _independent_control_reconstructions() -> dict[str, Any]:
    return {
        "R_groupoid_frozen": _groupoid_frozen_R_control(),
        "induced_pullback_broken": _induced_pullback_control(),
        "matter_T_ui_omitted": _matter_T_ui_control(),
        "full_V4_anisotropic": _anisotropic_V4_control(),
        "tolerances": {
            "R_groupoid_nominal_max": 2.0e-10,
            "induced_pullback_nominal_max": 2.0e-9,
            "matter_shift_nominal_max": 2.0e-8,
            "radial_V4_gauge_derivative_max": 2.0e-10,
            "required_mutant_minimum": MUTANT_RESIDUAL_FLOOR,
        },
        "gate_helpers_imported": [],
        "upstream_decision_booleans_used_as_oracle": False,
    }


def _activity() -> dict[str, Any]:
    points, _ = _quadrature(2)
    derivatives = {
        "gamma": vmap(jacrev(_gamma0))(points),
        "T": vmap(jacrev(_t0))(points),
        "Omega": vmap(jacrev(_omega0))(points),
        "psi": vmap(jacrev(_psi0))(points),
    }
    rows = {
        key: [
            float(torch.sqrt(torch.mean(value[..., axis] ** 2)))
            for axis in range(4)
        ]
        for key, value in derivatives.items()
    }
    face_points = []
    for axis in range(4):
        for sign in (-1.0, 1.0):
            point = torch.tensor([0.11, -0.13, 0.09, -0.08])
            point[axis] = sign * DOMAIN
            face_points.append(point)
    face = torch.stack(face_points)
    boundary_max = max(
        float(torch.max(torch.abs(vmap(lambda x: _xi(x, variant))(face))))
        for variant in (0, 1)
    )
    return {
        "coordinate_derivative_RMS": rows,
        "minimum_coordinate_activity": min(value for row in rows.values() for value in row),
        "boundary_xi_exact_max": boundary_max,
        "all_four_coordinates_active": all(
            len(row) == 4 and min(row) > 1.0e-8 for row in rows.values()
        ),
    }


def independent_runtime() -> dict[str, Any]:
    probes = [_probe(3, variant) for variant in (0, 1)]
    activity = _activity()
    controls = _independent_control_reconstructions()
    stokes = {
        f"xi_variant_{variant}": _stokes_boundary_certificate(2, variant)
        for variant in (0, 1)
    }
    coordinate_volume = (2.0 * DOMAIN) ** 4
    stokes_weak_bounds = {
        name: (
            row["total_oriented_boundary_flux_absolute"]
            + coordinate_volume * probes[index]["local_density_covariance_Linf"]
        )
        for index, (name, row) in enumerate(stokes.items())
    }
    volume_diagnostics = {
        f"xi_variant_{index}": {
            "quadrature_orders_evaluated": [probe["quadrature_order"]],
            "weak_Euler_sum": probe["underresolved_Gauss_volume_weak_Euler_sum"],
            "integrated_coordinate_divergence": probe[
                "integrated_coordinate_divergence"
            ],
            "weak_sum_vs_divergence_error": probe[
                "weak_sum_vs_divergence_error"
            ],
            "convergence_to_zero_tested": False,
            "certified": False,
            "used_by_selected_family_decision": False,
        }
        for index, probe in enumerate(probes)
    }
    all_mutants = {
        f"probe{index}_{name}": value
        for index, probe in enumerate(probes)
        for name, value in probe["mutant_witnesses"].items()
    }
    control_mutants = {
        "R_groupoid_frozen": controls["R_groupoid_frozen"][
            "frozen_R_mutant_witness"
        ],
        "induced_pullback_broken": controls["induced_pullback_broken"][
            "broken_pullback_mutant_witness"
        ],
        "omit_T_ui_matter": controls["matter_T_ui_omitted"][
            "omit_T_ui_matter_mutant_witness"
        ],
        "flip_T_ui_matter_sign": controls["matter_T_ui_omitted"][
            "flip_T_ui_sign_mutant_witness"
        ],
        "anisotropic_full_V4": controls["full_V4_anisotropic"][
            "anisotropic_V4_mutant_witness"
        ],
    }
    all_mutants.update(
        {f"independent_control_{name}": value for name, value in control_mutants.items()}
    )
    closure_errors = [
        value
        for probe in probes
        for value in (
            probe["direct_all_vs_slot_sum_error"],
            probe["direct_all_step_convergence"],
            max(probe["slot_step_convergence"].values()),
            probe["weak_sum_vs_divergence_error"],
            probe["local_density_covariance_L2"],
            probe["local_density_covariance_Linf"],
            probe["maximum_component_action_vs_JVP_error"],
            probe["independent_density_route_comparison"]["action_vs_JVP_Linf"],
            probe["independent_density_route_comparison"]["action_vs_Stokes_Linf"],
        )
    ]
    closure_errors.extend(
        row["total_oriented_boundary_flux_absolute"] for row in stokes.values()
    )
    closure_errors.extend(
        (
            controls["R_groupoid_frozen"]["nominal_invariance_error"],
            controls["induced_pullback_broken"]["nominal_pullback_max_error"],
            controls["matter_T_ui_omitted"]["nominal_shift_max_error"],
            abs(
                controls["full_V4_anisotropic"][
                    "signed_radial_gauge_derivative"
                ]
            ),
        )
    )
    nominal = max(closure_errors)
    return {
        "implementation_route": {
            "coordinate_jets": "torch reverse-mode jacrev of a distinct analytic field family",
            "Euler_pairings": "centered finite differences of the independently integrated action",
            "local_JVP": "torch.func.jvp of a separately assembled local density for 10+1+1+4 signed components",
            "divergence": "coordinate gradient of the separate JVP density plus density*partial.xi",
            "boundary_Stokes": "separately assembled density and Gauss integration of xi^mu*density on all eight oriented faces",
            "shared_internal_primitives": "neutral metric/khronon composites only",
            "primary_helpers_or_runtime_imported": [],
            "same_field_family_as_primary": False,
        },
        "action_scope": (
            "literal v5.2 S_fol_lower+S_wall0+S_R_intrinsic plus independent "
            "literal controls for groupoid trace, induced pullback, bulk T_ui and full V4"
        ),
        "geometry_route": "Rcal=R4+2 Ricci(u,u)+K^2-K_mn K^mn (Ricci contraction, not primary projected Riemann route)",
        "activity": activity,
        "compact_xi_probes": probes,
        "compact_Stokes_boundary_flux": stokes,
        "selected_family_Stokes_weak_residual_bounds": stokes_weak_bounds,
        "underresolved_Gauss_volume_diagnostics": volume_diagnostics,
        "compact_divergence_quadrature_convergence": {
            "orders_evaluated": [3],
            "convergence_to_zero_tested": False,
            "certified": False,
            "used_by_selected_family_decision": False,
        },
        "independent_control_reconstructions": controls,
        "required_independent_control_mutants": control_mutants,
        "published_tolerances": {
            "component_action_vs_JVP_max": COMPONENT_ACTION_JVP_TOLERANCE,
            "component_local_JVP_RMS_min": COMPONENT_LOCAL_ACTIVITY_FLOOR,
            "local_density_L2_max": 5.0e-7,
            "local_density_Linf_max": 5.0e-6,
            "density_route_Linf_max": 2.0e-10,
            "mutant_residual_min": MUTANT_RESIDUAL_FLOOR,
            **controls["tolerances"],
        },
        "mutant_witnesses": all_mutants,
        "minimum_mutant_witness": min(all_mutants.values()),
        "maximum_nominal_closure_error": nominal,
        "mutant_to_nominal_ratio": min(all_mutants.values()) / max(nominal, 1.0e-300),
        "continuum_limit_statement": (
            "The selected check combines pointwise automatic local density covariance "
            "with an independently evaluated compact-support boundary Stokes flux. "
            "The order-3 Gauss volume sums are retained as under-resolved diagnostics, "
            "are not required to vanish, and do not certify quadrature convergence."
        ),
    }


def formula_ledger() -> dict[str, Any]:
    return {
        "literal_action": EXPECTED_ACTIONS,
        "control_literals": EXPECTED_CONTROL_LITERALS,
        "fields": "10 symmetric gamma_mn components, T, Omega and 4 psi_m components",
        "signed_component_order": list(COMPONENT_LABELS),
        "diffeomorphism": {
            "delta_gamma": "L_xi gamma",
            "delta_T": "xi^m partial_m T",
            "delta_Omega": "xi^m partial_m Omega",
            "delta_psi": "xi^m partial_m psi_n+psi_m partial_n xi^m",
        },
        "weak_Ward": (
            "deltaS_gamma+deltaS_T+deltaS_Omega+deltaS_psi="
            "int partial_m(xi^m density)=int_boundary n_m xi^m density=0"
        ),
        "local_density_divergence": "delta_xi density=xi^m partial_m density+density partial_m xi^m",
        "boundary_Stokes": (
            "sum over eight oriented faces int sign_m xi^m density; compact xi is "
            "evaluated at the faces rather than replaced by a stored zero"
        ),
        "independent_routes": {
            "action": "centered finite differences of the integrated action density",
            "local": "torch.func.jvp of a separately assembled local density",
            "Stokes": "third literal density assembly evaluated on eight oriented faces",
        },
        "mandatory_executed_controls": {
            "R_groupoid_frozen": "varphi_H=R phi with delta R=-R hat(lambda)",
            "induced_pullback_broken": "gamma=J^T g(Y) J versus g(Y) without Jacobian legs",
            "omit_T_ui_matter": "E_shift_i^matter=-T_ui/N from bulk_gauged",
            "anisotropic_full_V4": "radial |phi| versus sqrt(phi^T G_aniso phi)",
        },
        "published_tolerances": {
            "component_action_vs_JVP_max": COMPONENT_ACTION_JVP_TOLERANCE,
            "component_local_activity_min": COMPONENT_LOCAL_ACTIVITY_FLOOR,
            "required_mutant_minimum": MUTANT_RESIDUAL_FLOOR,
        },
        "underresolved_volume_separation": (
            "the order-3 Gauss volume sum tests equality of two routes at identical "
            "nodes but is not accepted as a zero integral or convergence theorem"
        ),
        "scope": (
            "selected intrinsic interface family plus isolated mandatory literal controls; "
            "no full bulk Ward or moving-normal embedding theorem"
        ),
    }


def _decision(runtime: Mapping[str, Any]) -> dict[str, Any]:
    probes = runtime["compact_xi_probes"]
    stokes = runtime["compact_Stokes_boundary_flux"]
    stokes_bounds = runtime["selected_family_Stokes_weak_residual_bounds"]
    controls = runtime["independent_control_reconstructions"]
    control_tolerances = controls["tolerances"]
    local_density_closed = bool(
        len(probes) == 2
        and all(probe["weak_sum_vs_divergence_error"] < 5.0e-7 for probe in probes)
        and all(probe["local_density_covariance_L2"] < 5.0e-7 for probe in probes)
        and all(probe["local_density_covariance_Linf"] < 5.0e-6 for probe in probes)
    )
    stokes_boundary_closed = bool(
        len(stokes) == 2
        and all(row["face_count"] == 8 for row in stokes.values())
        and all(
            row["boundary_zero_obtained_from_runtime_fields"] is True
            for row in stokes.values()
        )
        and all(row["maximum_boundary_xi"] < 2.0e-15 for row in stokes.values())
        and all(
            row["maximum_boundary_action_density"] > 1.0e-3
            for row in stokes.values()
        )
        and all(
            row["maximum_boundary_flux_density"] < 2.0e-14
            for row in stokes.values()
        )
        and all(
            row["total_oriented_boundary_flux_absolute"] < 2.0e-14
            for row in stokes.values()
        )
    )
    local_stokes_closed = bool(
        local_density_closed
        and stokes_boundary_closed
        and len(stokes_bounds) == 2
        and max(stokes_bounds.values()) < 2.0e-5
    )
    component_jvp_closed = bool(
        len(probes) == 2
        and all(
            [row["component"] for row in probe["signed_component_action_and_local_JVP"]]
            == list(COMPONENT_LABELS)
            for probe in probes
        )
        and all(
            len(row["signed_local_JVP_values"]) == probe["point_count"]
            for probe in probes
            for row in probe["signed_component_action_and_local_JVP"]
        )
        and all(
            probe["maximum_component_action_vs_JVP_error"]
            < COMPONENT_ACTION_JVP_TOLERANCE
            for probe in probes
        )
        and all(
            probe["minimum_component_local_JVP_RMS"]
            > COMPONENT_LOCAL_ACTIVITY_FLOOR
            for probe in probes
        )
        and all(
            probe["component_JVP_additivity"]["pointwise_Linf_error"] < 2.0e-10
            for probe in probes
        )
    )
    density_routes_closed = bool(
        all(
            probe["independent_density_route_comparison"]["action_vs_JVP_Linf"]
            < 2.0e-10
            and probe["independent_density_route_comparison"][
                "action_vs_Stokes_Linf"
            ]
            < 2.0e-10
            for probe in probes
        )
    )
    required_probe_mutants = {
        "scalarize_psi_covector",
        "omit_density_Jacobian",
        "omit_sqrt_gamma_from_wall",
        "force_khronon_E_T_on_shell",
        *{
            f"{operation}_{slot}"
            for operation in ("omit", "flip_sign")
            for slot in ("metric_stress", "khronon_T", "Omega", "psi_covector")
        },
    }
    executed_mutants_closed = bool(
        all(set(probe["executed_mutants"]) == required_probe_mutants for probe in probes)
        and all(
            row["mutant_residual"] > MUTANT_RESIDUAL_FLOOR
            and "re-evaluated" in row["route"]
            for probe in probes
            for row in probe["executed_mutants"].values()
        )
    )
    independent_controls_closed = bool(
        controls["gate_helpers_imported"] == []
        and controls["upstream_decision_booleans_used_as_oracle"] is False
        and controls["R_groupoid_frozen"]["nominal_invariance_error"]
        < control_tolerances["R_groupoid_nominal_max"]
        and controls["R_groupoid_frozen"]["R_orthogonality_error"] < 2.0e-12
        and controls["R_groupoid_frozen"]["R_determinant_error"] < 2.0e-12
        and controls["R_groupoid_frozen"]["frozen_R_mutant_witness"]
        > control_tolerances["required_mutant_minimum"]
        and controls["induced_pullback_broken"]["nominal_pullback_max_error"]
        < control_tolerances["induced_pullback_nominal_max"]
        and controls["induced_pullback_broken"]["broken_pullback_mutant_witness"]
        > control_tolerances["required_mutant_minimum"]
        and controls["matter_T_ui_omitted"]["nominal_shift_max_error"]
        < control_tolerances["matter_shift_nominal_max"]
        and controls["matter_T_ui_omitted"]["T_ui_activity_norm"] > 1.0e-3
        and controls["matter_T_ui_omitted"]["minimum_absolute_T_ui_component"]
        > 1.0e-4
        and controls["matter_T_ui_omitted"]["full_radial_V4_potential_value"]
        > 1.0e-6
        and controls["matter_T_ui_omitted"]["omit_T_ui_matter_mutant_witness"]
        > control_tolerances["required_mutant_minimum"]
        and controls["matter_T_ui_omitted"]["flip_T_ui_sign_mutant_witness"]
        > control_tolerances["required_mutant_minimum"]
        and abs(
            controls["full_V4_anisotropic"]["signed_radial_gauge_derivative"]
        )
        < control_tolerances["radial_V4_gauge_derivative_max"]
        and controls["full_V4_anisotropic"]["radial_potential_activity"] > 1.0e-6
        and controls["full_V4_anisotropic"]["anisotropic_V4_mutant_witness"]
        > control_tolerances["required_mutant_minimum"]
        and min(runtime["required_independent_control_mutants"].values())
        > control_tolerances["required_mutant_minimum"]
    )
    selected = bool(
        len(probes) == 2
        and runtime["activity"]["all_four_coordinates_active"] is True
        and runtime["activity"]["minimum_coordinate_activity"] > 1.0e-5
        and runtime["activity"]["boundary_xi_exact_max"] == 0.0
        and all(probe["minimum_absolute_slot_pairing"] > 1.0e-7 for probe in probes)
        and all(probe["direct_all_vs_slot_sum_error"] < 5.0e-7 for probe in probes)
        and all(probe["direct_all_step_convergence"] < 5.0e-7 for probe in probes)
        and all(max(probe["slot_step_convergence"].values()) < 5.0e-7 for probe in probes)
        and local_density_closed
        and component_jvp_closed
        and density_routes_closed
        and executed_mutants_closed
        and independent_controls_closed
        and stokes_boundary_closed
        and local_stokes_closed
        and runtime["minimum_mutant_witness"] > 1.0e-6
        and runtime["mutant_to_nominal_ratio"] > 10.0
    )
    decision: dict[str, Any] = {
        "primary_v5_5_4_three_file_hash_binding_pass": True,
        "independent_interface_diffeomorphism_khronon_redteam_pass": selected,
        "two_compact_xi_and_density_divergence_pass": local_density_closed,
        "real_local_JVP_10_gamma_T_Omega_4_psi_pass": component_jvp_closed,
        "independent_action_JVP_Stokes_density_assemblies_pass": density_routes_closed,
        "executed_mutation_re_evaluation_pass": executed_mutants_closed,
        "independent_R_groupoid_pullback_T_ui_V4_controls_pass": independent_controls_closed,
        "local_density_Ward_equals_divergence_redteam_pass": local_density_closed,
        "runtime_boundary_Stokes_flux_zero_redteam_pass": stokes_boundary_closed,
        "compact_xi_weak_Ward_zero_by_local_Stokes_redteam_pass": local_stokes_closed,
        "underresolved_Gauss_volume_Ward_diagnostic_pass": False,
        "compact_divergence_quadrature_convergence_pass": False,
        "independent_finite_action_Euler_route_pass": selected,
        "off_shell_mutation_suite_pass": selected,
        "independent_redteam_checks_pass": selected,
    }
    for key in FAIL_CLOSED_KEYS:
        decision[key] = False
    return decision


def build_payload() -> dict[str, Any]:
    load_lineage()
    runtime = independent_runtime()
    decision = _decision(runtime)
    if decision["independent_redteam_checks_pass"] is not True:
        raise InterfaceWardV554RedteamError("independent v5.5.4 Ward red-team failed")
    if any(decision[key] is not False for key in FAIL_CLOSED_KEYS):
        raise InterfaceWardV554RedteamError("red-team downstream boundary promoted")
    true_pass_keys = {
        key
        for key, value in decision.items()
        if key.endswith("_pass") and value is True
    }
    if true_pass_keys != ALLOWED_TRUE_PASS_KEYS:
        raise InterfaceWardV554RedteamError("red-team true-pass allowlist drift")
    return {
        "schema": SCHEMA,
        "claim": (
            "Independent selected-family interface diffeomorphism/khronon Ward reproduction "
            "from signed sixteen-component action/JVP data, a separately assembled "
            "boundary Stokes flux and executed R/pullback/T_ui/V4 mutants; the "
            "under-resolved volume quadrature, full bulk, moving embedding, C1 and N1 "
            "remain fail-closed."
        ),
        "lineage": {
            "v5_2_artifact_sha256": EXPECTED_V5_2_SHA256,
            "v5_5_2_artifact_sha256": EXPECTED_V5_5_2_SHA256,
            "v5_5_2_redteam_artifact_sha256": EXPECTED_V5_5_2_REDTEAM_SHA256,
            "primary_v5_5_4": {
                "artifact_sha256": EXPECTED_PRIMARY_V5_5_4_ARTIFACT_SHA256,
                "generator_sha256": EXPECTED_PRIMARY_V5_5_4_GENERATOR_SHA256,
                "test_sha256": EXPECTED_PRIMARY_V5_5_4_TEST_SHA256,
            },
        },
        "primary_helpers_or_runtime_imported": [],
        "formula_ledger": formula_ledger(),
        "runtime": runtime,
        "decision": decision,
        "provenance": {
            "generator": str(Path(__file__).resolve().relative_to(REPO)),
            "generator_sha256": _sha256(Path(__file__).resolve()),
            "test": str(TEST.relative_to(REPO)),
            "test_sha256": _sha256(TEST),
            "torch": torch.__version__,
            "dtype": str(torch.get_default_dtype()),
            "threads": torch.get_num_threads(),
        },
    }


def main() -> int:
    payload = build_payload()
    _write(OUTPUT, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
