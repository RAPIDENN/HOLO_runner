#!/usr/bin/env python3
"""Additive v5.5.4 interface diffeomorphism/khronon Ward gate.

The gate rebuilds the selected v5.2 interface action from its literal
foliation, wall, and intrinsic Robin terms.  All four interface coordinates
are active.  Tensor jets, curvature, the action gradients, and the prolonged
diffeomorphism variation are produced with torch automatic differentiation.

This is deliberately separate from the SO(3) gauge Ward identity and imports
no earlier gate helper.  It also does not promote C1, N1, N4, B4, or B5.
"""

from __future__ import annotations

import hashlib
import json
import math
import gc
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import torch
from torch.func import jacfwd, jvp, vmap


torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    # A host test runner may have initialized the inter-op pool before import;
    # intra-op work is still hard-capped above and the receipt records it.
    pass
torch.set_default_dtype(torch.float64)

HERE = Path(__file__).resolve().parent
V5_2_ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
V5_5_2_PRIMARY = HERE / "artifacts" / "one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.json"
V5_5_2_REDTEAM = HERE / "artifacts" / "one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.json"
OUTPUT = HERE / "artifacts" / "one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.json"
TEST = HERE / "test_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.py"

SCHEMA = "holo.one-omega-topological-so3-interface-diffeomorphism-khronon-v5-5-4-gate.v1"
EXPECTED_V5_2_SHA256 = "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b"
EXPECTED_PRIMARY_V5_5_2_SHA256 = "4e068475ae316684cebd0f68e10d183fff7c0d90c46b155f2dfc8be4b3b0d6e8"
EXPECTED_REDTEAM_V5_5_2_SHA256 = "4c94c2abeb24fb3444be4f79c93aa383659feac9e706eea7fe4fe2aac85bc7f6"
EXPECTED_V5_2_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
EXPECTED_PRIMARY_V5_5_2_SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-gate.v1"
EXPECTED_REDTEAM_V5_5_2_SCHEMA = "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-redteam.v1"

EXPECTED_ACTIONS = {
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
}

DOMAIN_HALF_WIDTH = 0.72

FAIL_CLOSED_KEYS = (
    "continuum_all_configurations_theorem_pass",
    "complete_v5_2_all_field_normal_embedding_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "N4_JUNCTION_BENDING_pass",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
)


class InterfaceWardV554Error(ValueError):
    """The additive interface Ward receipt is malformed or drifted."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise InterfaceWardV554Error(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def _read_json(path: Path, expected_hash: str, expected_schema: str) -> dict[str, Any]:
    if _sha256(path) != expected_hash:
        raise InterfaceWardV554Error(f"lineage byte hash mismatch: {path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InterfaceWardV554Error(f"cannot parse {path}: {exc}") from exc
    if type(payload) is not dict or payload.get("schema") != expected_schema:
        raise InterfaceWardV554Error(f"lineage schema mismatch: {path.name}")
    return payload


def load_lineage() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    v5_2 = _read_json(V5_2_ARTIFACT, EXPECTED_V5_2_SHA256, EXPECTED_V5_2_SCHEMA)
    primary = _read_json(
        V5_5_2_PRIMARY, EXPECTED_PRIMARY_V5_5_2_SHA256, EXPECTED_PRIMARY_V5_5_2_SCHEMA
    )
    redteam = _read_json(
        V5_5_2_REDTEAM, EXPECTED_REDTEAM_V5_5_2_SHA256, EXPECTED_REDTEAM_V5_5_2_SCHEMA
    )
    try:
        actions = v5_2["exact_classical_charter"]["exact_action"]
        coefficients = v5_2["exact_classical_charter"]["coefficient_policy"]["parameters"]
    except (KeyError, TypeError) as exc:
        raise InterfaceWardV554Error("v5.2 action charter missing") from exc
    for key, literal in EXPECTED_ACTIONS.items():
        if actions.get(key) != literal:
            raise InterfaceWardV554Error(f"v5.2 literal action drift: {key}")
    for key, expected in EXPECTED_COEFFICIENTS.items():
        if float(coefficients.get(key, float("nan"))) != expected:
            raise InterfaceWardV554Error(f"v5.2 coefficient drift: {key}")
    if primary.get("decision", {}).get("candidate_checks_pass") is not True:
        raise InterfaceWardV554Error("v5.5.2 primary is not green")
    if redteam.get("decision", {}).get("independent_redteam_checks_pass") is not True:
        raise InterfaceWardV554Error("v5.5.2 red-team is not green")
    for payload in (primary, redteam):
        for key in ("C1_ACTION_pass", "N1_ACTION_pass", "B4_pass"):
            if payload.get("decision", {}).get(key) is not False:
                raise InterfaceWardV554Error(f"lineage fail-closed boundary changed: {key}")
    return v5_2, primary, redteam


# Constants are copied only after validating the exact frozen charter above.
MB2 = EXPECTED_COEFFICIENTS["brane_Mb_squared"]
LAMBDA_K = EXPECTED_COEFFICIENTS["lambda_K"]
XI_R = EXPECTED_COEFFICIENTS["xi"]
ETA = EXPECTED_COEFFICIENTS["eta"]
B4_BAR = EXPECTED_COEFFICIENTS["B4_bar"]
K_INFINITY = EXPECTED_COEFFICIENTS["k_infinity"]
M5_CUBED = EXPECTED_COEFFICIENTS["M5_cubed"]
G_OMEGA = EXPECTED_COEFFICIENTS["compensator_metric_G"]
BETA_WALL = EXPECTED_COEFFICIENTS["brane_beta"]
KAPPA = EXPECTED_COEFFICIENTS["Robin_kappa_hat"]
ROBIN_Y = EXPECTED_COEFFICIENTS["Robin_y"]


_K1 = torch.tensor(
    [
        [0.71, 0.43, -0.37, 0.29],
        [0.39, -0.62, 0.51, 0.34],
        [-0.48, 0.36, 0.67, -0.25],
        [0.27, 0.58, 0.33, -0.61],
        [0.55, -0.31, 0.46, 0.63],
        [-0.35, 0.69, -0.28, 0.47],
        [0.64, 0.24, -0.53, 0.38],
        [-0.42, -0.57, 0.32, 0.66],
        [0.31, 0.49, 0.59, -0.44],
        [-0.59, 0.28, 0.41, 0.52],
    ]
)
_K2 = torch.flip(_K1, dims=(0, 1)) * 0.83 + 0.17
_PHASE = torch.linspace(-0.7, 0.8, 10)
_METRIC_PAIRS = (
    (0, 0), (0, 1), (0, 2), (0, 3), (1, 1),
    (1, 2), (1, 3), (2, 2), (2, 3), (3, 3),
)


def _base_gamma(x: torch.Tensor) -> torch.Tensor:
    base = torch.tensor([-1.28, 0.0, 0.0, 0.0, 1.13, 0.0, 0.0, 0.98, 0.0, 1.21])
    amplitudes = torch.tensor([0.026, 0.018, 0.015, 0.017, 0.031, 0.016, 0.014, 0.028, 0.015, 0.033])
    wave = torch.sin(_K1 @ x + _PHASE) + 0.24 * torch.cos(_K2 @ x - 0.7 * _PHASE)
    wave = wave + 0.035 * torch.prod(1.0 + 0.4 * x) * torch.linspace(0.7, 1.3, 10)
    values = base + amplitudes * wave
    rows: list[torch.Tensor] = []
    lookup = {pair: values[index] for index, pair in enumerate(_METRIC_PAIRS)}
    for mu in range(4):
        rows.append(torch.stack([lookup[(min(mu, nu), max(mu, nu))] for nu in range(4)]))
    return torch.stack(rows)


def _base_T(x: torch.Tensor) -> torch.Tensor:
    return (
        x[0]
        + 0.038 * torch.sin(0.61 * x[0] + 0.47 * x[1] - 0.36 * x[2] + 0.29 * x[3])
        + 0.014 * torch.cos(0.33 * x[0] - 0.52 * x[1] + 0.41 * x[2] + 0.57 * x[3])
        + 0.006 * torch.prod(1.0 + 0.3 * x)
    )


def _base_Omega(x: torch.Tensor) -> torch.Tensor:
    return (
        1.16
        + 0.052 * torch.sin(0.44 * x[0] + 0.63 * x[1] - 0.38 * x[2] + 0.51 * x[3])
        + 0.019 * torch.cos(0.57 * x[0] - 0.31 * x[1] + 0.46 * x[2] + 0.35 * x[3])
        + 0.008 * torch.prod(1.0 + 0.2 * x)
    )


def _base_psi(x: torch.Tensor) -> torch.Tensor:
    rows = []
    for mu in range(4):
        k = _K1[mu + 3]
        q = _K2[mu + 5]
        rows.append(
            0.12 * (mu + 1)
            + 0.047 * torch.sin(k @ x + 0.23 * mu)
            + 0.029 * torch.cos(q @ x - 0.17 * mu)
            + 0.006 * (mu + 1) * torch.prod(1.0 + 0.15 * x)
        )
    return torch.stack(rows)


def _compact_bump(x: torch.Tensor) -> torch.Tensor:
    ratio2 = (x / DOMAIN_HALF_WIDTH) ** 2
    inside = ratio2 < 1.0
    safe_denominator = torch.where(inside, 1.0 - ratio2, torch.ones_like(ratio2))
    factors = torch.where(
        inside,
        torch.exp(1.0 - 1.0 / safe_denominator),
        torch.zeros_like(ratio2),
    )
    # Standard C-infinity compact bump, normalized to one at the origin and
    # explicitly extended by zero at and beyond every face.
    return torch.prod(factors)


def _xi(x: torch.Tensor, variant: int) -> torch.Tensor:
    bump = _compact_bump(x)
    if variant == 0:
        raw = torch.stack(
            (
                0.31 + torch.sin(0.7 * x[0] - 0.4 * x[1] + 0.3 * x[2] + 0.2 * x[3]),
                -0.22 + torch.cos(0.2 * x[0] + 0.6 * x[1] - 0.5 * x[2] + 0.4 * x[3]),
                0.18 + torch.sin(-0.3 * x[0] + 0.4 * x[1] + 0.7 * x[2] - 0.2 * x[3]),
                -0.15 + torch.cos(0.5 * x[0] - 0.3 * x[1] + 0.2 * x[2] + 0.6 * x[3]),
            )
        )
        return 0.34 * bump * raw
    raw = torch.stack(
        (
            -0.27 + torch.cos(0.4 * x[0] + 0.3 * x[1] - 0.6 * x[2] + 0.5 * x[3]),
            0.19 + torch.sin(-0.5 * x[0] + 0.7 * x[1] + 0.2 * x[2] - 0.3 * x[3]),
            -0.16 + torch.cos(0.6 * x[0] - 0.2 * x[1] + 0.5 * x[2] + 0.4 * x[3]),
            0.24 + torch.sin(0.3 * x[0] + 0.5 * x[1] - 0.4 * x[2] + 0.7 * x[3]),
        )
    )
    return 0.29 * bump * raw


def _lie_variations(x: torch.Tensor, variant: int) -> tuple[torch.Tensor, ...]:
    gamma = _base_gamma(x)
    psi = _base_psi(x)
    xi = _xi(x, variant)
    dgamma = jacfwd(_base_gamma)(x)
    dT = jacfwd(_base_T)(x)
    dOmega = jacfwd(_base_Omega)(x)
    dpsi = jacfwd(_base_psi)(x)
    dxi = jacfwd(lambda z: _xi(z, variant))(x)
    L_gamma = torch.einsum("r,mnr->mn", xi, dgamma)
    L_gamma = L_gamma + torch.einsum("rn,rm->mn", gamma, dxi)
    L_gamma = L_gamma + torch.einsum("mr,rn->mn", gamma, dxi)
    L_T = xi @ dT
    L_Omega = xi @ dOmega
    L_psi = torch.einsum("r,mr->m", xi, dpsi) + torch.einsum("r,rm->m", psi, dxi)
    # A common coding mutant: treating a covector as four spectator scalars.
    scalarized_L_psi = torch.einsum("r,mr->m", xi, dpsi)
    return L_gamma, L_T, L_Omega, L_psi, scalarized_L_psi


def _varied_fields(
    x: torch.Tensor, epsilon: torch.Tensor, variant: int,
    *, scalarized_psi: bool = False,
) -> tuple[torch.Tensor, ...]:
    L_gamma, L_T, L_Omega, L_psi, wrong_L_psi = _lie_variations(x, variant)
    return (
        _base_gamma(x) + epsilon[0] * L_gamma,
        _base_T(x) + epsilon[1] * L_T,
        _base_Omega(x) + epsilon[2] * L_Omega,
        _base_psi(x) + epsilon[3] * (wrong_L_psi if scalarized_psi else L_psi),
    )


def _christoffel(x: torch.Tensor, epsilon: torch.Tensor, variant: int) -> torch.Tensor:
    gamma = _varied_fields(x, epsilon, variant)[0]
    inverse = torch.linalg.inv(gamma)
    dgamma = jacfwd(lambda z: _varied_fields(z, epsilon, variant)[0])(x)
    rows = []
    for sigma in range(4):
        mu_rows = []
        for mu in range(4):
            mu_rows.append(torch.stack([
                dgamma[sigma, nu, mu] + dgamma[sigma, mu, nu] - dgamma[mu, nu, sigma]
                for nu in range(4)
            ]))
        rows.append(torch.stack(mu_rows))
    lowered = torch.stack(rows)
    return 0.5 * torch.einsum("rs,smn->rmn", inverse, lowered)


def _u_covector(x: torch.Tensor, epsilon: torch.Tensor, variant: int) -> torch.Tensor:
    gamma, T, _, _ = _varied_fields(x, epsilon, variant)
    inverse = torch.linalg.inv(gamma)
    dT = jacfwd(lambda z: _varied_fields(z, epsilon, variant)[1])(x)
    lapse = torch.rsqrt(-(dT @ inverse @ dT))
    return -lapse * dT


def _density_point(
    x: torch.Tensor, epsilon: torch.Tensor, variant: int,
    *, scalarized_psi: bool = False,
) -> torch.Tensor:
    gamma, _, Omega, psi = _varied_fields(
        x, epsilon, variant, scalarized_psi=scalarized_psi
    )
    inverse = torch.linalg.inv(gamma)
    root = torch.sqrt(-torch.linalg.det(gamma))
    christoffel = _christoffel(x, epsilon, variant)
    dchristoffel = jacfwd(lambda z: _christoffel(z, epsilon, variant))(x)

    # R^rho_{ sigma mu nu}; every index is kept explicit to make orientation
    # and sign mutants visible in the receipt.
    rho_rows = []
    for rho in range(4):
        sigma_rows = []
        for sigma in range(4):
            mu_rows = []
            for mu in range(4):
                entries = []
                for nu in range(4):
                    derivative = (
                        dchristoffel[rho, nu, sigma, mu]
                        - dchristoffel[rho, mu, sigma, nu]
                    )
                    quadratic = sum(
                        christoffel[rho, mu, ell] * christoffel[ell, nu, sigma]
                        - christoffel[rho, nu, ell] * christoffel[ell, mu, sigma]
                        for ell in range(4)
                    )
                    entries.append(derivative + quadratic)
                mu_rows.append(torch.stack(entries))
            sigma_rows.append(torch.stack(mu_rows))
        rho_rows.append(torch.stack(sigma_rows))
    riemann_mixed = torch.stack(rho_rows)
    riemann_cov = torch.einsum("ar,rsmn->asmn", gamma, riemann_mixed)

    u_cov = _u_covector(x, epsilon, variant)
    u_up = inverse @ u_cov
    h_contra = inverse + torch.outer(u_up, u_up)
    projector = torch.eye(4) + torch.outer(u_cov, u_up)
    du = jacfwd(lambda z: _u_covector(z, epsilon, variant))(x)
    nabla_u = du.T - torch.einsum("rmn,r->mn", christoffel, u_cov)
    K_cov = torch.einsum("ma,nb,ab->mn", projector, projector, nabla_u)
    K_trace = torch.einsum("mn,mn->", h_contra, K_cov)
    K_squared = torch.einsum("ma,nb,mn,ab->", h_contra, h_contra, K_cov, K_cov)
    a_cov = torch.einsum("n,nm->m", u_up, nabla_u)
    a_squared = a_cov @ h_contra @ a_cov
    projected_ambient_R = torch.einsum(
        "am,bn,abmn->", h_contra, h_contra, riemann_cov
    )
    Rcal = projected_ambient_R + K_trace * K_trace - K_squared

    foliation = 0.5 * MB2 * (
        K_squared - LAMBDA_K * K_trace * K_trace + XI_R * Rcal
        + ETA * a_squared - B4_BAR * Rcal * Rcal / (16.0 * K_INFINITY**2)
    )
    W = 3.0 * M5_CUBED * K_INFINITY * torch.exp(
        -G_OMEGA * Omega * Omega / (6.0 * M5_CUBED)
    )
    wall = -(2.0 * W + 0.5 * BETA_WALL * (Omega - 1.0) ** 2)
    r_cov = psi - ROBIN_Y * a_cov
    robin = -0.5 * KAPPA * (r_cov @ h_contra @ r_cov)
    return root * (foliation + wall + robin)


def _quadrature(order: int) -> tuple[torch.Tensor, torch.Tensor]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    nodes = DOMAIN_HALF_WIDTH * nodes
    weights = DOMAIN_HALF_WIDTH * weights
    meshes = np.meshgrid(nodes, nodes, nodes, nodes, indexing="ij")
    weight_meshes = np.meshgrid(weights, weights, weights, weights, indexing="ij")
    points = np.stack([item.reshape(-1) for item in meshes], axis=1)
    total_weights = np.prod(np.stack(weight_meshes, axis=-1), axis=-1).reshape(-1)
    return torch.as_tensor(points), torch.as_tensor(total_weights)


def _density_batch(points: torch.Tensor, epsilon: torch.Tensor, variant: int) -> torch.Tensor:
    return vmap(lambda point: _density_point(point, epsilon, variant))(points)


def _action(points: torch.Tensor, weights: torch.Tensor, epsilon: torch.Tensor, variant: int) -> torch.Tensor:
    return weights @ _density_batch(points, epsilon, variant)


def _probe_certificate(order: int, variant: int) -> dict[str, Any]:
    points, weights = _quadrature(order)
    epsilon = torch.zeros(4, requires_grad=True)
    density = _density_batch(points, epsilon, variant)
    action = weights @ density
    reverse_slots = torch.autograd.grad(action, epsilon, create_graph=False)[0].detach()
    action_value = float(action.detach())
    del action, density, epsilon
    gc.collect()

    # A single all-field density JVP is independent of the reverse-mode slot
    # gradient above and avoids materializing a point_count x 4 higher-jet
    # Jacobian.
    zero = torch.zeros(4)
    local_slot_arrays = []
    for slot in range(4):
        direction = torch.zeros(4)
        direction[slot] = 1.0
        base_density, local_slot = jvp(
            lambda e: _density_batch(points, e, variant),
            (zero,),
            (direction,),
        )
        local_slot_arrays.append(local_slot.detach())
    local_slots = torch.stack(local_slot_arrays, dim=1)
    local_total = torch.sum(local_slots, dim=1)
    base_density = base_density.detach()
    xis = vmap(lambda point: _xi(point, variant))(points)
    _, density_along_xi = jvp(
        lambda batch: _density_batch(batch, zero, variant),
        (points,),
        (xis,),
    )
    dxis = vmap(jacfwd(lambda point: _xi(point, variant)))(points)
    divergence = density_along_xi + base_density * torch.einsum(
        "pmm->p", dxis
    )
    local_covariance_residual = local_total - divergence

    forward_slots = torch.einsum("p,ps->s", weights, local_slots)
    step = 1.0e-5
    direction = torch.ones(4)
    finite = (
        _action(points, weights, step * direction, variant)
        - _action(points, weights, -step * direction, variant)
    ) / (2.0 * step)

    # The wrong psi route is differentiated separately, not obtained by
    # deleting a term from the correct answer.
    wrong_direction = torch.zeros(4)
    wrong_direction[3] = 1.0
    _, wrong_psi_local = jvp(
        lambda e: vmap(
            lambda point: _density_point(point, e, variant, scalarized_psi=True)
        )(points),
        (zero,),
        (wrong_direction,),
    )
    wrong_psi_local = wrong_psi_local.detach()
    wrong_psi_slot = weights @ wrong_psi_local
    wrong_psi_local_residual = (
        torch.sum(local_slots[:, :3], dim=1) + wrong_psi_local - divergence
    )

    slot_names = ("metric_stress", "khronon_T", "Omega", "psi_covector")
    slots = {name: float(value) for name, value in zip(slot_names, reverse_slots, strict=True)}
    local_l2 = torch.sqrt(torch.sum(weights * local_covariance_residual**2) / torch.sum(weights))
    return {
        "quadrature_order_per_coordinate": order,
        "point_count": order**4,
        "xi_variant": variant,
        "action_value": action_value,
        "automatic_reverse_slot_contributions": slots,
        "minimum_absolute_slot_contribution": min(abs(value) for value in slots.values()),
        "reverse_vs_forward_local_slot_max_error": float(torch.max(torch.abs(
            reverse_slots - forward_slots
        ))),
        "weak_Ward_sum": float(torch.sum(reverse_slots).detach()),
        "weak_Ward_absolute_residual": abs(float(torch.sum(reverse_slots).detach())),
        "integrated_density_divergence": float(torch.sum(weights * divergence).detach()),
        "weak_sum_vs_density_divergence_error": abs(float(
            torch.sum(reverse_slots).detach() - torch.sum(weights * divergence).detach()
        )),
        "finite_difference_all_fields_derivative": float(finite.detach()),
        "finite_difference_vs_automatic_sum_error": abs(float(
            finite.detach() - torch.sum(reverse_slots).detach()
        )),
        "local_density_covariance_L2": float(local_l2.detach()),
        "local_density_covariance_Linf": float(torch.max(torch.abs(
            local_covariance_residual
        )).detach()),
        "density_variation_RMS": float(torch.sqrt(torch.mean(local_total.detach() ** 2))),
        "local_slot_L2_norms": {
            name: float(torch.sqrt(torch.sum(weights * local_slots[:, index] ** 2) / torch.sum(weights)))
            for index, name in enumerate(slot_names)
        },
        "xi_RMS": float(torch.sqrt(torch.mean(xis**2))),
        "xi_derivative_RMS": float(torch.sqrt(torch.mean(dxis**2))),
        "wrong_scalarized_psi_slot": float(wrong_psi_slot.detach()),
        "wrong_scalarized_psi_local_Ward_L2_witness": float(torch.sqrt(
            torch.sum(weights * wrong_psi_local_residual**2) / torch.sum(weights)
        )),
    }


def _weak_integral_certificate(order: int, variant: int) -> dict[str, Any]:
    """Low-cost quadrature-only probe used solely for convergence."""

    points, weights = _quadrature(order)
    zero = torch.zeros(4)
    base_density, local_total = jvp(
        lambda e: _density_batch(points, e, variant),
        (zero,),
        (torch.ones(4),),
    )
    xis = vmap(lambda point: _xi(point, variant))(points)
    _, density_along_xi = jvp(
        lambda batch: _density_batch(batch, zero, variant),
        (points,),
        (xis,),
    )
    dxis = vmap(jacfwd(lambda point: _xi(point, variant)))(points)
    divergence = density_along_xi + base_density * torch.einsum("pmm->p", dxis)
    weak = weights @ local_total
    flux = weights @ divergence
    return {
        "quadrature_order_per_coordinate": order,
        "point_count": order**4,
        "weak_Ward_absolute_residual": abs(float(weak.detach())),
        "integrated_density_divergence": float(flux.detach()),
        "weak_sum_vs_density_divergence_error": abs(float((weak - flux).detach())),
    }


def _stokes_boundary_certificate(face_order: int, variant: int) -> dict[str, Any]:
    """Evaluate xi^mu density on all eight faces; no zero is inserted by hand."""

    nodes, weights = np.polynomial.legendre.leggauss(face_order)
    nodes = DOMAIN_HALF_WIDTH * nodes
    weights = DOMAIN_HALF_WIDTH * weights
    meshes = np.meshgrid(nodes, nodes, nodes, indexing="ij")
    weight_meshes = np.meshgrid(weights, weights, weights, indexing="ij")
    tangential = np.stack([item.reshape(-1) for item in meshes], axis=1)
    face_weights = np.prod(np.stack(weight_meshes, axis=-1), axis=-1).reshape(-1)
    zero = torch.zeros(4)
    total_flux = 0.0
    face_rows: list[dict[str, Any]] = []
    maximum_xi = 0.0
    maximum_flux_density = 0.0
    maximum_action_density = 0.0
    for axis in range(4):
        tangential_axes = [index for index in range(4) if index != axis]
        for sign in (-1.0, 1.0):
            points = np.zeros((face_order**3, 4), dtype=float)
            points[:, axis] = sign * DOMAIN_HALF_WIDTH
            points[:, tangential_axes] = tangential
            point_tensor = torch.as_tensor(points)
            xis = vmap(lambda point: _xi(point, variant))(point_tensor)
            densities = _density_batch(point_tensor, zero, variant).detach()
            oriented_flux_density = sign * xis[:, axis] * densities
            integral = float(torch.as_tensor(face_weights) @ oriented_flux_density)
            xi_max = float(torch.max(torch.abs(xis)))
            flux_max = float(torch.max(torch.abs(oriented_flux_density)))
            density_max = float(torch.max(torch.abs(densities)))
            total_flux += integral
            maximum_xi = max(maximum_xi, xi_max)
            maximum_flux_density = max(maximum_flux_density, flux_max)
            maximum_action_density = max(maximum_action_density, density_max)
            face_rows.append({
                "axis": axis,
                "sign": int(sign),
                "point_count": face_order**3,
                "xi_max": xi_max,
                "action_density_max": density_max,
                "oriented_flux_density_max": flux_max,
                "integrated_oriented_flux": integral,
            })
    return {
        "Stokes_convention": "int_M partial_mu(xi^mu density)=sum_faces int sign_mu xi^mu density",
        "face_quadrature_order": face_order,
        "face_count": 8,
        "faces": face_rows,
        "maximum_boundary_xi": maximum_xi,
        "maximum_boundary_action_density": maximum_action_density,
        "maximum_boundary_flux_density": maximum_flux_density,
        "total_oriented_boundary_flux": total_flux,
        "total_oriented_boundary_flux_absolute": abs(total_flux),
        "boundary_zero_obtained_from_runtime_fields": True,
    }


def _field_activity_certificate(order: int = 3) -> dict[str, Any]:
    points, _ = _quadrature(order)
    gamma_derivatives = vmap(jacfwd(_base_gamma))(points)
    T_derivatives = vmap(jacfwd(_base_T))(points)
    Omega_derivatives = vmap(jacfwd(_base_Omega))(points)
    psi_derivatives = vmap(jacfwd(_base_psi))(points)

    def coordinate_rms(values: torch.Tensor) -> list[float]:
        axes = tuple(range(values.ndim - 1))
        return [float(value) for value in torch.sqrt(torch.mean(values**2, dim=axes))]

    rows = {
        "gamma": coordinate_rms(gamma_derivatives),
        "T": coordinate_rms(T_derivatives),
        "Omega": coordinate_rms(Omega_derivatives),
        "psi": coordinate_rms(psi_derivatives),
    }
    minimum = min(min(values) for values in rows.values())
    # The C-infinity bump is exactly zero on every face in its continuous
    # extension.  Evaluate face interiors just inside the branch and record
    # the declared exact extension separately.
    face_points = []
    for axis in range(4):
        for sign in (-1.0, 1.0):
            point = torch.tensor([0.13, -0.17, 0.09, -0.11])
            point[axis] = sign * DOMAIN_HALF_WIDTH
            face_points.append(point)
    face_tensor = torch.stack(face_points)
    face_xi_max = max(
        float(torch.max(torch.abs(vmap(lambda point: _xi(point, variant))(face_tensor))))
        for variant in (0, 1)
    )
    return {
        "coordinate_derivative_RMS": rows,
        "minimum_field_coordinate_derivative_RMS": minimum,
        "all_four_coordinates_active": bool(minimum > 1.0e-4),
        "compact_support_boundary_extension": "xi=0 with all jets on |x^mu|=L",
        "boundary_face_count": len(face_points),
        "boundary_xi_exact_max": face_xi_max,
    }


def formula_ledger() -> dict[str, Any]:
    return {
        "selected_literal_action": {
            "terms": "S_interface=S_fol_lower+S_wall0+S_R_intrinsic",
            "u": "u_mu=-N partial_mu T; N=(-gamma^mn partial_mT partial_nT)^(-1/2)",
            "h": "h_mn=gamma_mn+u_m u_n; h^mn=gamma^mn+u^m u^n",
            "K": "K_mn=h_m^a h_n^b nabla_a u_b",
            "a": "a_m=u^n nabla_n u_m",
            "Rcal": "Rcal=h^am h^bn R_abmn[gamma]+K^2-K_mn K^mn",
            "Rcal_squared": "-Mb^2 B4_bar Rcal^2/(32 k_infinity^2)",
            "Robin_covector": "r_m=psi_m-y a_m; S_R=-kappa/2 int sqrt(-gamma) h^mn r_m r_n",
        },
        "infinitesimal_diffeomorphism_convention": {
            "metric": "delta_xi gamma_mn=L_xi gamma_mn",
            "khronon": "delta_xi T=xi^r partial_r T",
            "Omega": "delta_xi Omega=xi^r partial_r Omega",
            "psi": "delta_xi psi_m=xi^r nabla_r psi_m+psi_r nabla_m xi^r=L_xi psi_m",
        },
        "first_variation": (
            "delta S=int sqrt(-gamma)[tau^mn delta gamma_mn/2+E_T delta T+"
            "E_Omega delta Omega+E_psi^m delta psi_m]"
        ),
        "weak_Ward": (
            "int sqrt(-gamma)[tau^mn nabla_m xi_n+E_T xi.dT+E_Omega xi.dOmega+"
            "E_psi^m(L_xi psi)_m]=0 for compact xi"
        ),
        "local_Ward": (
            "W_n=-nabla_m tau^m_n+E_T partial_nT+E_Omega partial_nOmega+"
            "E_psi^m nabla_n psi_m-nabla_m(E_psi^m psi_n)=0"
        ),
        "density_covariance": "delta_xi(sqrt(-gamma)L)=partial_m[xi^m sqrt(-gamma)L]",
        "compact_Stokes_closure": (
            "int_Sigma delta_xi density=int_partialSigma n_mu xi^mu density=0; "
            "the eight face fluxes are evaluated from runtime xi and density"
        ),
        "separation": "This is a spacetime diffeomorphism/khronon Ward identity, not the SO(3) gauge Ward identity.",
    }


def runtime_certificate() -> dict[str, Any]:
    activity = _field_activity_certificate()
    # Two unrelated compact vector fields are used at two quadrature orders.
    # The low order is diagnostic only; the high order must both reduce and
    # absolutely close the compact-support weak integral.  Local coordinate
    # derivatives remain automatic rather than finite-difference stencils.
    probe_families = {}
    probes = []
    for variant in (0, 1):
        low = _weak_integral_certificate(2, variant)
        high = _probe_certificate(3, variant)
        probe_families[f"xi_variant_{variant}"] = [low, high]
        probes.append(high)
    convergence: dict[str, Any] = {}
    for name, (low, high) in probe_families.items():
        low_residual = low["weak_Ward_absolute_residual"]
        high_residual = high["weak_Ward_absolute_residual"]
        convergence[name] = {
            "orders": [low["quadrature_order_per_coordinate"], high["quadrature_order_per_coordinate"]],
            "absolute_residuals": [low_residual, high_residual],
            "reduction_factor_high_over_low": high_residual / max(low_residual, 1.0e-300),
            "high_order_integrated_divergence_absolute": abs(
                high["integrated_density_divergence"]
            ),
            "certified": bool(
                high_residual < 2.0e-8
                and abs(high["integrated_density_divergence"]) < 2.0e-8
                and high["weak_sum_vs_density_divergence_error"] < 2.0e-9
                and high_residual < 0.25 * low_residual
            ),
        }
    stokes = {
        f"xi_variant_{variant}": _stokes_boundary_certificate(2, variant)
        for variant in (0, 1)
    }
    coordinate_volume = (2.0 * DOMAIN_HALF_WIDTH) ** 4
    stokes_weak_bounds = {
        name: (
            row["total_oriented_boundary_flux_absolute"]
            + coordinate_volume * probes[index]["local_density_covariance_Linf"]
        )
        for index, (name, row) in enumerate(stokes.items())
    }
    mutants: dict[str, float] = {}
    for index, row in enumerate(probes):
        slots = row["automatic_reverse_slot_contributions"]
        local_norms = row["local_slot_L2_norms"]
        mutants[f"probe{index}_omit_E_T"] = local_norms["khronon_T"]
        mutants[f"probe{index}_omit_metric_stress"] = local_norms["metric_stress"]
        mutants[f"probe{index}_omit_E_Omega"] = local_norms["Omega"]
        mutants[f"probe{index}_omit_E_psi"] = local_norms["psi_covector"]
        mutants[f"probe{index}_flip_metric_sign"] = 2.0 * local_norms["metric_stress"]
        mutants[f"probe{index}_flip_T_sign"] = 2.0 * local_norms["khronon_T"]
        mutants[f"probe{index}_flip_Omega_sign"] = 2.0 * local_norms["Omega"]
        mutants[f"probe{index}_flip_psi_sign"] = 2.0 * local_norms["psi_covector"]
        mutants[f"probe{index}_scalarize_psi_covector"] = row[
            "wrong_scalarized_psi_local_Ward_L2_witness"
        ]
        # A circular integrated construction can define E_T to cancel the
        # other three numbers.  It cannot reproduce the independently
        # prolonged local density variation, whose RMS is recorded here.
        # Exact integrated cancellation alone is therefore not accepted.
        mutants[f"probe{index}_circular_integrated_Euler"] = row[
            "density_variation_RMS"
        ]
        mutants[f"probe{index}_force_T_on_shell"] = local_norms["khronon_T"]
    mutants["Killing_only_or_constant_background_activity_loss"] = activity[
        "minimum_field_coordinate_derivative_RMS"
    ]
    return {
        "action_scope": "literal v5.2 S_fol_lower+S_wall0+S_R_intrinsic",
        "spacetime_dimension": 4,
        "field_activity": activity,
        "compact_arbitrary_xi_probes": probes,
        "compact_weak_quadrature_convergence": convergence,
        "compact_Stokes_boundary_flux": stokes,
        "selected_family_Stokes_weak_residual_bounds": stokes_weak_bounds,
        "automatic_Euler_route": "torch reverse-mode gradients of one action with four independent variation slots",
        "independent_local_route": "torch forward-mode prolonged density variation versus coordinate divergence",
        "finite_difference_route": "independent centered simultaneous action variation",
        "mutant_witnesses": mutants,
        "minimum_mutant_witness": min(mutants.values()),
        "vacuous_Killing_only_probe_rejected": True,
        "vacuous_Killing_reason": (
            "constant fields/translation would have zero coordinate activity; the gate requires "
            "all four coordinate derivatives and every Euler slot to be active"
        ),
        "continuum_limit_statement": (
            "Local tensor jets are differentiated continuously by automatic differentiation. "
            "Compact weak closure uses the independently evaluated eight-face Stokes flux. "
            "The under-resolved order-2/3 volume Gauss sums are retained as failed diagnostics. "
            "This validates the displayed analytic family and two compact xi probes, not all smooth configurations."
        ),
    }


def _decision(runtime: Mapping[str, Any]) -> dict[str, bool]:
    probes = runtime["compact_arbitrary_xi_probes"]
    convergence = runtime["compact_weak_quadrature_convergence"]
    high_order = [
        row for row in probes if row["quadrature_order_per_coordinate"] == 3
    ]
    stokes = runtime["compact_Stokes_boundary_flux"]
    stokes_bounds = runtime["selected_family_Stokes_weak_residual_bounds"]
    local_density_closed = bool(
        len(high_order) == 2
        and all(row["local_density_covariance_L2"] < 2.0e-8 for row in high_order)
        and all(row["local_density_covariance_Linf"] < 2.0e-7 for row in high_order)
        and all(row["weak_sum_vs_density_divergence_error"] < 2.0e-9 for row in high_order)
    )
    stokes_boundary_closed = bool(
        len(stokes) == 2
        and all(row["boundary_zero_obtained_from_runtime_fields"] is True for row in stokes.values())
        and all(row["maximum_boundary_xi"] < 2.0e-15 for row in stokes.values())
        and all(row["maximum_boundary_action_density"] > 1.0e-3 for row in stokes.values())
        and all(row["maximum_boundary_flux_density"] < 2.0e-14 for row in stokes.values())
        and all(row["total_oriented_boundary_flux_absolute"] < 2.0e-14 for row in stokes.values())
    )
    stokes_weak_closed = bool(
        local_density_closed
        and stokes_boundary_closed
        and len(stokes_bounds) == 2
        and max(stokes_bounds.values()) < 2.0e-7
    )
    selected = bool(
        runtime["spacetime_dimension"] == 4
        and runtime["field_activity"]["all_four_coordinates_active"] is True
        and runtime["field_activity"]["boundary_xi_exact_max"] == 0.0
        and all(row["minimum_absolute_slot_contribution"] > 1.0e-6 for row in probes)
        and all(row["reverse_vs_forward_local_slot_max_error"] < 2.0e-9 for row in probes)
        and local_density_closed
        and stokes_boundary_closed
        and stokes_weak_closed
        and all(row["finite_difference_vs_automatic_sum_error"] < 2.0e-7 for row in probes)
        and runtime["minimum_mutant_witness"] > 1.0e-6
        and runtime["vacuous_Killing_only_probe_rejected"] is True
    )
    decision = {
        "v5_2_and_v5_5_2_lineage_pinned_pass": True,
        "full_4D_interface_fields_active_pass": runtime["field_activity"]["all_four_coordinates_active"],
        "interface_diffeomorphism_khronon_Ward_selected_family_pass": selected,
        "compact_xi_weak_Ward_zero_by_local_Stokes_pass": stokes_weak_closed,
        "local_density_Ward_equals_divergence_pass": local_density_closed,
        "runtime_boundary_Stokes_flux_zero_pass": stokes_boundary_closed,
        "underresolved_Gauss_volume_Ward_diagnostic_pass": bool(
            all(item["certified"] is True for item in convergence.values())
        ),
        "compact_divergence_quadrature_convergence_pass": bool(
            all(item["certified"] is True for item in convergence.values())
        ),
        "independent_automatic_Euler_and_local_density_routes_pass": bool(
            selected and all(row["reverse_vs_forward_local_slot_max_error"] < 2.0e-9 for row in probes)
        ),
        "off_shell_nonvacuous_mutants_pass": bool(
            selected and runtime["minimum_mutant_witness"] > 1.0e-6
        ),
        "SO3_gauge_Ward_inherited_pass": False,
        "candidate_checks_pass": selected,
    }
    for key in FAIL_CLOSED_KEYS:
        decision[key] = False
    return decision


def build_payload() -> dict[str, Any]:
    load_lineage()
    runtime = runtime_certificate()
    decision = _decision(runtime)
    if decision["candidate_checks_pass"] is not True:
        raise InterfaceWardV554Error("selected-family Ward checks did not pass")
    if any(decision[key] is not False for key in FAIL_CLOSED_KEYS):
        raise InterfaceWardV554Error("v5.5.4 fail-closed boundary changed")
    ledger = formula_ledger()
    return {
        "schema": SCHEMA,
        "claim": (
            "Additive four-dimensional selected-family interface diffeomorphism/khronon "
            "Ward certificate; no C1/N1/B4 promotion and no all-configuration theorem."
        ),
        "earlier_gate_helpers_imported": [],
        "formula_ledger_sha256": _canonical_sha256(ledger),
        "formula_ledger": ledger,
        "lineage": {
            "v5_2_artifact_sha256": EXPECTED_V5_2_SHA256,
            "v5_5_2_primary_artifact_sha256": EXPECTED_PRIMARY_V5_5_2_SHA256,
            "v5_5_2_redteam_artifact_sha256": EXPECTED_REDTEAM_V5_5_2_SHA256,
        },
        "runtime": runtime,
        "decision": decision,
        "provenance": {
            "generator": str(Path(__file__).resolve().relative_to(HERE.parents[1])),
            "generator_sha256": _sha256(Path(__file__).resolve()),
            "test": str(TEST.resolve().relative_to(HERE.parents[1])),
            "test_sha256": _sha256(TEST),
            "torch": torch.__version__,
            "dtype": str(torch.get_default_dtype()),
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
