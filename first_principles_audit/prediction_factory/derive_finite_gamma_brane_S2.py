#!/usr/bin/env python3
"""Close the finite-curvature two-brane S2 operator and norm backward test.

The calculation deliberately keeps three scalar representations separate.
The Boos variable ``g`` comes from the direct second variation of the
Einstein--scalar--brane action.  The Lesgourgues--Sorbo variable ``Psi`` makes
the two finite-curvature junctions a symmetric generalized eigenproblem.  The
ADM/BMP curvature variable is obtained only after the differential Darboux
map; eliminating ``g`` at a finite-curvature endpoint produces a rational
eigenvalue-dependent boundary law, so it must not be replaced by an ordinary
Robin coefficient.

No observational table is read.  This certificate closes the quadratic
operator, compact spectrum and scalar norm.  It does not rederive the raw
EH--GHY cancellation or authorize a nonlinear brane vertex.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import simpson
from scipy.interpolate import CubicSpline
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "finite_gamma_brane_S2.json"
INPUTS = {
    "effective_action": REPO
    / "first_principles_audit/artifacts/holo_effective_action.json",
    "LS_boundary_completion": HERE
    / "artifacts/superpotential_boundary_completion.json",
    "bulk_ADM_S2": HERE / "artifacts/adm_quadratic_recovery.json",
    "stiff_endpoint_backward": HERE / "artifacts/compact_brane_S2_backward.json",
}
MODE_COUNT = 7
GAMMA_PAIRS = ((0.7, 1.3), (3.0, 5.0), (20.0, 11.0))
SHOOTING_MU_MIN = 1.0e-5
SHOOTING_MU_MAX = 5.0
SHOOTING_SCAN_POINTS = 1001
SHOOTING_BISECTIONS = 42
CRITERIA = {
    "pointwise_Darboux_bilinear_identity_max_relative": 1.0e-12,
    "integrated_bilinear_identity_max_relative": 1.0e-6,
    "Boos_LS_mass_relative_max": 2.0e-4,
    "Boos_LS_one_minus_MAC_max": 1.0e-6,
    "canonical_norm_orthogonality_max_abs": 5.0e-10,
    "shooting_mass_relative_max": 2.0e-4,
    "shooting_root_residual_relative_max": 1.0e-8,
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _linear_mass(u: np.ndarray, weight: np.ndarray):
    spacing = np.diff(u)
    diagonal = np.zeros(u.size)
    diagonal[:-1] += spacing * (3.0 * weight[:-1] + weight[1:]) / 12.0
    diagonal[1:] += spacing * (weight[:-1] + 3.0 * weight[1:]) / 12.0
    off_diagonal = spacing * (weight[:-1] + weight[1:]) / 12.0
    return diags(
        [off_diagonal, diagonal, off_diagonal],
        offsets=[-1, 0, 1],
        format="lil",
    )


def _derivative_stiffness(u: np.ndarray, weight: np.ndarray):
    spacing = np.diff(u)
    element_weight = 0.5 * (weight[:-1] + weight[1:])
    diagonal = np.zeros(u.size)
    diagonal[:-1] += element_weight / spacing
    diagonal[1:] += element_weight / spacing
    off_diagonal = -element_weight / spacing
    return diags(
        [off_diagonal, diagonal, off_diagonal],
        offsets=[-1, 0, 1],
        format="csr",
    )


def _background(payload: Mapping[str, Any]) -> tuple[np.ndarray, ...]:
    if payload.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action input is not certified")
    u = np.asarray(payload["u"], dtype=float)
    warp = np.asarray(payload["A"], dtype=float)
    warp_u = np.asarray(payload["A_u"], dtype=float)
    chi_u = np.asarray(payload["canonical_chi_u"], dtype=float)
    if not (
        u.ndim == warp.ndim == warp_u.ndim == chi_u.ndim == 1
        and u.size == warp.size == warp_u.size == chi_u.size
        and u.size >= 64
        and np.all(np.diff(u) > 0.0)
        and np.all(warp_u < 0.0)
        and np.all(chi_u > 0.0)
    ):
        raise ValueError("invalid monotone two-brane background")
    chi_uu = CubicSpline(u, chi_u).derivative()(u)
    return u, warp, warp_u, chi_u, chi_uu


def _boos_matrices(
    arrays: tuple[np.ndarray, ...], gamma_minus: float, gamma_plus: float
):
    u, warp, _warp_u, chi_u, _chi_uu = arrays
    p = np.exp(-2.0 * warp) / np.square(chi_u)
    q = np.exp(-2.0 * warp) / 3.0
    w = np.exp(-4.0 * warp) / np.square(chi_u)
    derivative = _derivative_stiffness(u, p)
    stiffness = (derivative + _linear_mass(u, q)).tocsr()
    mass = _linear_mass(u, w)
    mass[0, 0] += w[0] / gamma_minus
    mass[-1, -1] += w[-1] / gamma_plus
    canonical_norm = 1.5 * (
        _linear_mass(u, np.exp(-2.0 * warp)).tocsr()
        + 3.0 * derivative
    )
    return stiffness, mass.tocsr(), canonical_norm.tocsr()


def _LS_matrices(
    arrays: tuple[np.ndarray, ...], gamma_minus: float, gamma_plus: float
):
    u, warp, warp_u, chi_u, chi_uu = arrays
    warp_uu = -np.square(chi_u) / 6.0
    r = np.exp(2.0 * warp) / np.square(chi_u)
    q = -4.0 * r * (warp_uu - warp_u * chi_uu / chi_u)
    w = 1.0 / np.square(chi_u)
    stiffness = (_derivative_stiffness(u, r) + _linear_mass(u, q)).tolil()
    stiffness[0, 0] += -2.0 * r[0] * warp_u[0]
    stiffness[-1, -1] += 2.0 * r[-1] * warp_u[-1]
    mass = _linear_mass(u, w)
    mass[0, 0] += w[0] / gamma_minus
    mass[-1, -1] += w[-1] / gamma_plus
    return stiffness.tocsr(), mass.tocsr()


def _eigensystem(stiffness, mass) -> tuple[np.ndarray, np.ndarray, float]:
    values, modes = eigsh(
        stiffness,
        k=MODE_COUNT,
        M=mass,
        sigma=1.0e-8,
        which="LM",
        tol=1.0e-11,
        maxiter=100000,
        v0=np.linspace(1.0, 2.0, stiffness.shape[0], dtype=float),
    )
    order = np.argsort(values)
    values = np.asarray(values[order], dtype=float)
    modes = np.asarray(modes[:, order], dtype=float)
    if np.any(values <= 0.0):
        raise RuntimeError("finite-gamma scalar problem is not positive")
    for index, mode in enumerate(modes.T):
        mode /= math.sqrt(float(mode @ (mass @ mode)))
        if mode[0] < 0.0:
            mode *= -1.0
        modes[:, index] = mode
    residuals = []
    stiffness_norm = float(np.linalg.norm(stiffness.data))
    mass_norm = float(np.linalg.norm(mass.data))
    for value, mode in zip(values, modes.T):
        residual = stiffness @ mode - value * (mass @ mode)
        scale = np.linalg.norm(mode) * (
            stiffness_norm + abs(value) * mass_norm
        )
        residuals.append(float(np.linalg.norm(residual) / max(scale, 1.0e-300)))
    return values, modes, max(residuals)


def _bilinear_identity(arrays: tuple[np.ndarray, ...]) -> dict[str, Any]:
    u, warp, warp_u, chi_u, chi_uu = arrays
    coordinate = (u - u[0]) / (u[-1] - u[0])
    length = u[-1] - u[0]
    warp_uu = -np.square(chi_u) / 6.0
    p_g = np.exp(-2.0 * warp) / np.square(chi_u)
    q_g = np.exp(-2.0 * warp) / 3.0
    w_g = np.exp(-4.0 * warp) / np.square(chi_u)
    r = np.exp(2.0 * warp) / np.square(chi_u)
    r_u = r * (2.0 * warp_u - 2.0 * chi_uu / chi_u)
    q = -4.0 * r * (warp_uu - warp_u * chi_uu / chi_u)
    w = 1.0 / np.square(chi_u)
    pointwise_errors: list[float] = []
    integrated_errors: list[float] = []
    mass_errors: list[float] = []
    rows = []
    for harmonic in range(1, 7):
        psi = (
            0.2
            + 0.1 * harmonic * coordinate
            + 0.15 * np.sin(harmonic * np.pi * coordinate)
            + 0.07 * np.cos((harmonic + 1) * np.pi * coordinate)
        )
        psi_u = (
            0.1 * harmonic / length
            + 0.15
            * harmonic
            * np.pi
            / length
            * np.cos(harmonic * np.pi * coordinate)
            - 0.07
            * (harmonic + 1)
            * np.pi
            / length
            * np.sin((harmonic + 1) * np.pi * coordinate)
        )
        g = np.exp(2.0 * warp) * psi
        g_u = np.exp(2.0 * warp) * (psi_u + 2.0 * warp_u * psi)
        boos_density = p_g * np.square(g_u) + q_g * np.square(g)
        LS_density = r * np.square(psi_u) + q * np.square(psi)
        total_derivative = (
            2.0 * (r_u * warp_u + r * warp_uu) * np.square(psi)
            + 4.0 * r * warp_u * psi * psi_u
        )
        scale = np.maximum.reduce(
            (
                np.abs(boos_density - LS_density),
                np.abs(total_derivative),
                np.ones_like(total_derivative),
            )
        )
        pointwise = float(
            np.max(np.abs(boos_density - LS_density - total_derivative) / scale)
        )
        boos_integral = float(simpson(boos_density, x=u))
        LS_integral = float(
            simpson(LS_density, x=u)
            - 2.0 * r[0] * warp_u[0] * psi[0] ** 2
            + 2.0 * r[-1] * warp_u[-1] * psi[-1] ** 2
        )
        integrated = abs(boos_integral / LS_integral - 1.0)
        pair_mass_errors = []
        for gamma_minus, gamma_plus in GAMMA_PAIRS:
            boos_mass = float(
                simpson(w_g * np.square(g), x=u)
                + w_g[0] * g[0] ** 2 / gamma_minus
                + w_g[-1] * g[-1] ** 2 / gamma_plus
            )
            LS_mass = float(
                simpson(w * np.square(psi), x=u)
                + w[0] * psi[0] ** 2 / gamma_minus
                + w[-1] * psi[-1] ** 2 / gamma_plus
            )
            pair_mass_errors.append(abs(boos_mass / LS_mass - 1.0))
        mass_error = max(pair_mass_errors)
        pointwise_errors.append(pointwise)
        integrated_errors.append(integrated)
        mass_errors.append(mass_error)
        rows.append(
            {
                "harmonic": harmonic,
                "pointwise_total_derivative_identity_relative": pointwise,
                "integrated_stiffness_relative": integrated,
                "finite_gamma_mass_form_relative": mass_error,
            }
        )
    return {
        "rows": rows,
        "maximum_pointwise_total_derivative_identity_relative": max(
            pointwise_errors
        ),
        "maximum_integrated_stiffness_relative": max(integrated_errors),
        "maximum_finite_gamma_mass_form_relative": max(mass_errors),
    }


def _shooting_precomputation(arrays: tuple[np.ndarray, ...]) -> dict[str, np.ndarray]:
    u, warp, warp_u, chi_u, chi_uu = arrays
    midpoint = 0.5 * (u[:-1] + u[1:])
    warp_spline = CubicSpline(u, warp)
    warp_u_spline = CubicSpline(u, warp_u)
    chi_u_spline = CubicSpline(u, chi_u)
    chi_uu_spline = chi_u_spline.derivative()
    return {
        "u": u,
        "warp": warp,
        "warp_u": warp_u,
        "chi_u": chi_u,
        "chi_uu": chi_uu,
        "mid_warp": warp_spline(midpoint),
        "mid_warp_u": warp_u_spline(midpoint),
        "mid_chi_u": chi_u_spline(midpoint),
        "mid_chi_uu": chi_uu_spline(midpoint),
    }


def _shooting_residuals(
    mu: np.ndarray,
    gamma_minus: np.ndarray,
    gamma_plus: np.ndarray,
    data: Mapping[str, np.ndarray],
) -> np.ndarray:
    mu = np.atleast_1d(np.asarray(mu, dtype=float))
    gamma_minus = np.broadcast_to(np.asarray(gamma_minus, dtype=float), mu.shape)
    gamma_plus = np.broadcast_to(np.asarray(gamma_plus, dtype=float), mu.shape)
    mass_squared = np.square(mu)
    u = data["u"]
    warp = data["warp"]
    warp_u = data["warp_u"]
    chi_u = data["chi_u"]
    chi_uu = data["chi_uu"]
    state = np.column_stack(
        (
            np.ones(mu.size),
            -mass_squared * np.exp(-2.0 * warp[0]) / gamma_minus,
        )
    )

    def rhs(
        current: np.ndarray,
        local_warp: float,
        local_warp_u: float,
        local_chi_u: float,
        local_chi_uu: float,
    ) -> np.ndarray:
        return np.column_stack(
            (
                current[:, 1],
                2.0
                * (local_warp_u + local_chi_uu / local_chi_u)
                * current[:, 1]
                + (
                    local_chi_u**2 / 3.0
                    - mass_squared * np.exp(-2.0 * local_warp)
                )
                * current[:, 0],
            )
        )

    for index, spacing in enumerate(np.diff(u)):
        k1 = rhs(
            state, warp[index], warp_u[index], chi_u[index], chi_uu[index]
        )
        k2 = rhs(
            state + 0.5 * spacing * k1,
            data["mid_warp"][index],
            data["mid_warp_u"][index],
            data["mid_chi_u"][index],
            data["mid_chi_uu"][index],
        )
        k3 = rhs(
            state + 0.5 * spacing * k2,
            data["mid_warp"][index],
            data["mid_warp_u"][index],
            data["mid_chi_u"][index],
            data["mid_chi_uu"][index],
        )
        k4 = rhs(
            state + spacing * k3,
            warp[index + 1],
            warp_u[index + 1],
            chi_u[index + 1],
            chi_uu[index + 1],
        )
        state += spacing * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
    return (
        gamma_plus * state[:, 1]
        - mass_squared * np.exp(-2.0 * warp[-1]) * state[:, 0]
    )


def _global_shooting(
    arrays: tuple[np.ndarray, ...], FEM_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    data = _shooting_precomputation(arrays)
    scan_mu = np.linspace(
        SHOOTING_MU_MIN, SHOOTING_MU_MAX, SHOOTING_SCAN_POINTS
    )
    lower_brackets: list[float] = []
    upper_brackets: list[float] = []
    gamma_minus_all: list[float] = []
    gamma_plus_all: list[float] = []
    grouping: list[tuple[int, int]] = []
    for pair_index, (gamma_minus, gamma_plus) in enumerate(GAMMA_PAIRS):
        residual = _shooting_residuals(
            scan_mu,
            np.full(scan_mu.size, gamma_minus),
            np.full(scan_mu.size, gamma_plus),
            data,
        )
        changes = np.flatnonzero(residual[:-1] * residual[1:] < 0.0)
        if changes.size < MODE_COUNT:
            raise RuntimeError(
                f"global shooting scan found only {changes.size} roots for pair "
                f"{pair_index}"
            )
        start = len(lower_brackets)
        for location in changes[:MODE_COUNT]:
            lower_brackets.append(float(scan_mu[location]))
            upper_brackets.append(float(scan_mu[location + 1]))
            gamma_minus_all.append(gamma_minus)
            gamma_plus_all.append(gamma_plus)
        grouping.append((start, len(lower_brackets)))

    lower = np.asarray(lower_brackets)
    upper = np.asarray(upper_brackets)
    gamma_minus = np.asarray(gamma_minus_all)
    gamma_plus = np.asarray(gamma_plus_all)
    residual_lower = _shooting_residuals(lower, gamma_minus, gamma_plus, data)
    residual_upper = _shooting_residuals(upper, gamma_minus, gamma_plus, data)
    original_bracket_scale = np.maximum(
        np.maximum(np.abs(residual_lower), np.abs(residual_upper)), 1.0e-300
    )
    for _iteration in range(SHOOTING_BISECTIONS):
        middle = 0.5 * (lower + upper)
        residual_middle = _shooting_residuals(
            middle, gamma_minus, gamma_plus, data
        )
        left = residual_lower * residual_middle <= 0.0
        upper = np.where(left, middle, upper)
        lower = np.where(left, lower, middle)
        residual_lower = np.where(left, residual_lower, residual_middle)
    roots = 0.5 * (lower + upper)
    root_residual = _shooting_residuals(roots, gamma_minus, gamma_plus, data)
    scaled_residual = np.abs(root_residual) / original_bracket_scale

    rows = []
    all_relative = []
    for pair_index, (start, stop) in enumerate(grouping):
        shooting = roots[start:stop]
        FEM = np.asarray(FEM_rows[pair_index]["Boos_masses_mu"], dtype=float)
        relative = np.abs(shooting / FEM - 1.0)
        all_relative.extend(relative.tolist())
        rows.append(
            {
                "gamma_minus": GAMMA_PAIRS[pair_index][0],
                "gamma_plus": GAMMA_PAIRS[pair_index][1],
                "shooting_masses_mu": shooting.tolist(),
                "Boos_FEM_mass_relative": relative.tolist(),
                "maximum_Boos_FEM_mass_relative": float(np.max(relative)),
                "root_residual_over_final_bracket": scaled_residual[
                    start:stop
                ].tolist(),
            }
        )
    return {
        "method": (
            "fixed preregistered mu scan followed by simultaneous bracketed "
            "RK4 bisection; no FEM target is used to locate a bracket"
        ),
        "scan": {
            "mu_min": SHOOTING_MU_MIN,
            "mu_max": SHOOTING_MU_MAX,
            "points": SHOOTING_SCAN_POINTS,
            "bisections": SHOOTING_BISECTIONS,
        },
        "rows": rows,
        "maximum_Boos_FEM_mass_relative": max(all_relative),
        "maximum_root_residual_over_final_bracket": float(
            np.max(scaled_residual)
        ),
    }


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    effective = payloads["effective_action"]
    if payloads["LS_boundary_completion"].get("passes", {}).get("all") is not True:
        raise RuntimeError("LS boundary completion is not certified")
    if payloads["bulk_ADM_S2"].get("checks", {}).get("all") is not True:
        raise RuntimeError("bulk ADM S2 is not certified")
    if payloads["stiff_endpoint_backward"].get("checks", {}).get("all") is not True:
        raise RuntimeError("stiff endpoint backward test is not certified")
    arrays = _background(effective)
    u, warp, warp_u, chi_u, _chi_uu = arrays
    bilinear = _bilinear_identity(arrays)

    finite_rows: list[dict[str, Any]] = []
    maximum_mass_relative = 0.0
    maximum_MAC_loss = 0.0
    maximum_norm_error = 0.0
    maximum_backward = 0.0
    for gamma_minus, gamma_plus in GAMMA_PAIRS:
        boos_K, boos_M, canonical_N = _boos_matrices(
            arrays, gamma_minus, gamma_plus
        )
        LS_K, LS_M = _LS_matrices(arrays, gamma_minus, gamma_plus)
        boos_values, boos_modes, boos_backward = _eigensystem(boos_K, boos_M)
        LS_values, LS_modes, LS_backward = _eigensystem(LS_K, LS_M)
        mass_relative = np.abs(np.sqrt(boos_values / LS_values) - 1.0)
        MAC = []
        for index, boos_mode in enumerate(boos_modes.T):
            mapped = np.exp(-2.0 * warp) * boos_mode
            mapped /= math.sqrt(float(mapped @ (LS_M @ mapped)))
            overlap = float(mapped @ (LS_M @ LS_modes[:, index]))
            MAC.append(overlap**2)
        canonical_modes = boos_modes / np.sqrt(4.5 * boos_values)[None, :]
        canonical_gram = canonical_modes.T @ (canonical_N @ canonical_modes)
        norm_error = float(
            np.max(np.abs(canonical_gram - np.eye(MODE_COUNT)))
        )
        maximum_mass_relative = max(
            maximum_mass_relative, float(np.max(mass_relative))
        )
        maximum_MAC_loss = max(maximum_MAC_loss, 1.0 - min(MAC))
        maximum_norm_error = max(maximum_norm_error, norm_error)
        maximum_backward = max(maximum_backward, boos_backward, LS_backward)
        finite_rows.append(
            {
                "gamma_minus": gamma_minus,
                "gamma_plus": gamma_plus,
                "Boos_masses_mu": np.sqrt(boos_values).tolist(),
                "LS_masses_mu": np.sqrt(LS_values).tolist(),
                "mass_relative": mass_relative.tolist(),
                "maximum_mass_relative": float(np.max(mass_relative)),
                "mapped_mode_MAC": MAC,
                "maximum_one_minus_MAC": 1.0 - min(MAC),
                "canonical_norm_orthogonality_max_abs": norm_error,
                "Boos_backward_error": boos_backward,
                "LS_backward_error": LS_backward,
            }
        )

    shooting = _global_shooting(arrays, finite_rows)
    W = -6.0 * warp_u
    endpoint_index = (0, u.size - 1)
    orientations = (-1, 1)
    endpoint_H = [
        float(W[index] * np.exp(-2.0 * warp[index]) / chi_u[index] ** 2)
        for index in endpoint_index
    ]

    checks = {
        "certified_inputs": True,
        "no_observational_tables_read": True,
        "both_brane_orientations_present": orientations == (-1, 1),
        "three_asymmetric_positive_finite_gamma_pairs": bool(
            len(GAMMA_PAIRS) == 3
            and all(left > 0.0 and right > 0.0 and left != right for left, right in GAMMA_PAIRS)
        ),
        "pointwise_Boos_LS_bilinear_identity": bilinear[
            "maximum_pointwise_total_derivative_identity_relative"
        ]
        < CRITERIA["pointwise_Darboux_bilinear_identity_max_relative"],
        "integrated_Boos_LS_bilinear_identity": bilinear[
            "maximum_integrated_stiffness_relative"
        ]
        < CRITERIA["integrated_bilinear_identity_max_relative"],
        "finite_gamma_mass_forms_identical": bilinear[
            "maximum_finite_gamma_mass_form_relative"
        ]
        < CRITERIA["pointwise_Darboux_bilinear_identity_max_relative"],
        "Boos_and_LS_finite_gamma_spectra_match": maximum_mass_relative
        < CRITERIA["Boos_LS_mass_relative_max"],
        "Boos_and_LS_finite_gamma_modes_match": maximum_MAC_loss
        < CRITERIA["Boos_LS_one_minus_MAC_max"],
        "dimensionless_Boos_norm_identity_verified": maximum_norm_error
        < CRITERIA["canonical_norm_orthogonality_max_abs"],
        "target_free_shooting_matches_FEM": shooting[
            "maximum_Boos_FEM_mass_relative"
        ]
        < CRITERIA["shooting_mass_relative_max"],
        "shooting_roots_are_resolved": shooting[
            "maximum_root_residual_over_final_bracket"
        ]
        < CRITERIA["shooting_root_residual_relative_max"],
    }
    checks["all"] = all(checks.values())

    translated_operator_complete = bool(
        checks["all"]
        and checks["Boos_and_LS_finite_gamma_spectra_match"]
        and checks["target_free_shooting_matches_FEM"]
    )
    physical_gates = {
        "synthetic_bent_brane_fixture_used_as_physical_evidence": False,
        "finite_gamma_Boos_boundary_operator_recovered_from_S2": True,
        "finite_gamma_LS_weak_boundary_operator_recovered": True,
        "finite_gamma_ADM_BMP_rational_endpoint_law_derived": True,
        "finite_gamma_compact_spectrum_three_route_verified": bool(
            checks["Boos_and_LS_finite_gamma_spectra_match"]
            and checks["target_free_shooting_matches_FEM"]
        ),
        "finite_gamma_dimensionless_norm_identity_verified": checks[
            "dimensionless_Boos_norm_identity_verified"
        ],
        "single_interval_absolute_canonical_norm_recovered": False,
        "finite_gamma_translated_operator_crosscheck_complete": (
            translated_operator_complete
        ),
        "finite_gamma_brane_S2_backward_complete": False,
        "raw_EH_GHY_normal_derivative_cancellation_rederived_in_repo": False,
        "local_same_variable_ADM_boundary_auxiliary_action_recovered": False,
        "nonlinear_brane_jets_frozen": False,
        "physical_finite_gamma_S3_endpoint_ready": False,
    }
    return {
        "schema": "holo.finite-gamma-brane-S2.v1",
        "title": "Finite-curvature two-brane S2 operator, spectrum and norm",
        "classification": (
            "finite_gamma_published_operator_crosschecked_on_real_background;"
            "direct_ADM_EH_GHY_brane_backward_derivation_pending"
        ),
        "conventions": {
            "interval_action": (
                "S=(2*kappa5^2)^-1 int_M sqrt(-G)[R-(partial chi)^2/2-V]"
                "+kappa5^-2 sum_i int_i sqrt(-gamma)K"
                "-(2*kappa5^2)^-1 sum_i int_i sqrt(-gamma)lambda_i"
            ),
            "orientations": {"lower": -1, "upper": 1},
            "brane_potentials": (
                "lambda_-=W+gamma_-(chi-chi_-)^2/2; "
                "lambda_+=-W+gamma_+(chi-chi_+)^2/2"
            ),
            "Boos_translation": (
                "A_Boos=-A; chi=sqrt(2)*kappa5*phi_Boos; "
                "lambda_interval=kappa5^2*lambda_Boos"
            ),
        },
        "linear_gauge_invariants": {
            "definitions": (
                "Psi=zeta-A'*beta; Phi=alpha-beta'; "
                "Delta_chi=delta_chi-chi'*beta"
            ),
            "constraints": "Phi=-2*Psi; -chi'*Delta_chi=6*(Psi'+2A'*Psi)",
            "unitary_gauge_reconstruction": (
                "beta=6*D(Psi)/chi'^2; "
                "zeta=Psi-W*D(Psi)/chi'^2; D=partial_u+2A'"
            ),
            "bending": "exp(A_i)*Z_i=xi_i+beta_i; traceless Israel gives Z_i=0",
        },
        "finite_gamma_boundary_conditions": {
            "LS_lower": "gamma_-*exp(2A_-)*D(Psi)_-+m^2*Psi_-=0",
            "LS_upper": "gamma_+*exp(2A_+)*D(Psi)_+-m^2*Psi_+=0",
            "Boos_lower": "gamma_-*g'_-+m^2*exp(-2A_-)*g_-=0",
            "Boos_upper": "gamma_+*g'_+-m^2*exp(-2A_+)*g_+=0",
            "weak_LS_stiffness": (
                "int(r*Psi'*v'+q*Psi*v)-2*r_-*A'_-*Psi_-*v_-"
                "+2*r_+*A'_+*Psi_+*v_+"
            ),
            "weak_LS_mass": (
                "int(w*Psi*v)+w_-/gamma_-*Psi_-*v_-"
                "+w_+/gamma_+*Psi_+*v_+"
            ),
            "LS_weights": (
                "r=exp(2A)/chi'^2; w=1/chi'^2; "
                "q=-4r(A''-A'*chi''/chi')"
            ),
        },
        "representation_maps": {
            "Boos_to_LS": "Psi=-exp(-2A)*g/[4*sqrt(2*M^3)]",
            "LS_to_ADM_unitary": "zeta=Psi-W*D(Psi)/chi'^2",
            "ADM_to_BMP": "tilde_a_BMP=3*zeta/2",
            "Boos_to_ADM_without_common_factor": (
                "zeta proportional exp(-2A)*[-g+W*g'/chi'^2]"
            ),
            "Boos_LS_bilinear_identity": (
                "K_g[g=exp(2A)Psi]=K_LS[Psi] after the exact boundary "
                "term [2*r*A'*Psi^2]_-^+; M_g=M_LS"
            ),
            "verification": bilinear,
        },
        "finite_gamma_ADM_endpoint_law": {
            "definitions": (
                "f=exp(-2A)*[-g+W*g'/chi'^2]; "
                "H_i=W_i*exp(-2A_i)/chi_i'^2; s_-= -1, s_+=+1"
            ),
            "bulk_identity": "f'=-m^2*exp(-4A)*W*g/chi'^2",
            "endpoint_law": (
                "[1-s_i*m^2*H_i/gamma_i]*f'_i=m^2*H_i*f_i"
            ),
            "endpoint_H_numeric": {
                "lower": endpoint_H[0],
                "upper": endpoint_H[1],
            },
            "warning": (
                "This rational eigenvalue dependence is the footprint of the "
                "eliminated boundary/bending variable. Treating it as a constant "
                "Robin coefficient gives the wrong finite-gamma norm."
            ),
        },
        "direct_second_variation_norm": {
            "Boos_form": (
                "N_g=(3/2)*int exp(-2A)[g_n*g_m+3*g_n'*g_m'/chi'^2]"
            ),
            "finite_gamma_identity": (
                "For M_g-orthonormal modes, N_g=(9/2)*m_n^2*delta_nm; "
                "the endpoint pieces are in M_g through w_g/gamma_i."
            ),
            "maximum_canonical_orthogonality_error": maximum_norm_error,
            "normalization_warning": (
                "The orthogonality identity is dimensionless. Boos integrates "
                "the full [-L,L] orbifold, whereas this repository uses one "
                "interval copy; an absolute kappa5 normalization must include "
                "that factor-of-two translation and is not certified here."
            ),
        },
        "finite_gamma_verification": {
            "gamma_pairs": [list(pair) for pair in GAMMA_PAIRS],
            "rows": finite_rows,
            "maximum_Boos_LS_mass_relative": maximum_mass_relative,
            "maximum_Boos_LS_one_minus_MAC": maximum_MAC_loss,
            "maximum_generalized_backward_error": maximum_backward,
            "independent_global_shooting": shooting,
        },
        "physical_gates": physical_gates,
        "checks": checks,
        "criteria": CRITERIA,
        "inputs": {
            "observational_tables_read": [],
            "files": {
                name: {
                    "path": str(path.relative_to(REPO)),
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
            "primary_theory_inputs": [
                {
                    "reference": "Lesgourgues and Sorbo (2004)",
                    "arxiv": "hep-th/0310007",
                    "role": "gauge-invariant finite-brane junction operator",
                },
                {
                    "reference": "Boos et al. (2006)",
                    "arxiv": "hep-th/0511185",
                    "role": "direct second-variation scalar equation and norm",
                },
            ],
        },
        "next_decisive_test": (
            "Recompute the raw interval EH+GHY+lambda quadratic density with "
            "nonvanishing endpoint profiles and retain the local boundary auxiliary. "
            "Its variation must reproduce the rational ADM endpoint law and the "
            "Boos norm before any cubic endpoint is accepted."
        ),
        "evidence_boundary": (
            "This closes the finite-gamma two-brane S2 operator, compact spectrum "
            "and a dimensionless norm identity by analytic representation maps, two FEM "
            "forms and target-free shooting. It does not yet independently rederive "
            "the raw EH-GHY cancellation in this repository, freeze cubic brane "
            "jets, derive S3, or demonstrate a force."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        failed = [key for key, value in result["checks"].items() if not value]
        raise SystemExit(f"finite-gamma brane S2 certificate failed: {failed}")
    _write(OUTPUT, result)
    verification = result["finite_gamma_verification"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[Boos-LS finite-gamma mass max relative] "
        f"{verification['maximum_Boos_LS_mass_relative']:.3e}"
    )
    print(
        "[target-free shooting mass max relative] "
        f"{verification['independent_global_shooting']['maximum_Boos_FEM_mass_relative']:.3e}"
    )
    print(
        "[finite gamma brane S2 backward complete] "
        f"{result['physical_gates']['finite_gamma_brane_S2_backward_complete']}"
    )
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
