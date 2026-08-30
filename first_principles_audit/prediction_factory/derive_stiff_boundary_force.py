#!/usr/bin/env python3
"""Normalize the stiff stabilized radion and derive its matter force residues.

This uses the second-variation scalar action and matter vertex of Boos et al.
(hep-th/0511185), translated to the reconstructed Einstein--dilaton
conventions.  No residue from the earlier trace-only NN benchmark is reused.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BACKGROUND_RELATIVE = Path(
    "first_principles_audit/artifacts/holo_effective_action.json"
)
BOUNDARY_RELATIVE = Path(
    "first_principles_audit/prediction_factory/artifacts/"
    "superpotential_boundary_completion.json"
)
OUTPUT = HERE / "artifacts" / "stiff_boundary_force.json"

MODE_COUNT = 7
ANCHOR_X = (0.0, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0)
MASS_HALF_GRID_RELATIVE_MAX = 1.5e-4
MASS_QUARTER_GRID_RELATIVE_MAX = 7.0e-4
BETA_HALF_GRID_RELATIVE_MAX = 1.0e-4
BETA_QUARTER_GRID_RELATIVE_MAX = 4.0e-4
BOUNDARY_MASS_RELATIVE_MAX = 1.0e-4
BACKWARD_ERROR_MAX = 1.0e-12


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
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
        format="csr",
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


def _arrays(payload: dict[str, Any], stride: int = 1) -> tuple[np.ndarray, ...]:
    if payload.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action input is not certified")
    u = np.asarray(payload["u"], dtype=float)
    warp = np.asarray(payload["A"], dtype=float)
    chi_u = np.asarray(payload["canonical_chi_u"], dtype=float)
    if not (
        u.ndim == warp.ndim == chi_u.ndim == 1
        and u.size == warp.size == chi_u.size
        and u.size >= 64
        and np.all(np.diff(u) > 0.0)
        and np.all(np.isfinite(warp))
        and np.all(chi_u > 0.0)
    ):
        raise ValueError("invalid canonical background arrays")
    indices = np.arange(0, u.size, stride, dtype=int)
    if indices[-1] != u.size - 1:
        indices = np.append(indices, u.size - 1)
    return u[indices], warp[indices], chi_u[indices]


def solve(payload: dict[str, Any], stride: int = 1) -> dict[str, Any]:
    u, warp, chi_u = _arrays(payload, stride)
    derivative_weight = np.exp(-2.0 * warp) / np.square(chi_u)
    potential_weight = np.exp(-2.0 * warp) / 3.0
    eigen_weight = np.exp(-4.0 * warp) / np.square(chi_u)

    derivative = _derivative_stiffness(u, derivative_weight)
    stiffness = derivative + _linear_mass(u, potential_weight)
    mass = _linear_mass(u, eigen_weight)
    normalization = 1.5 * (
        _linear_mass(u, np.exp(-2.0 * warp)) + 3.0 * derivative
    )

    values, modes = eigsh(
        stiffness,
        k=MODE_COUNT,
        M=mass,
        sigma=1.0e-8,
        which="LM",
        tol=1.0e-11,
        maxiter=100000,
        v0=np.linspace(1.0, 2.0, u.size, dtype=float),
    )
    order = np.argsort(values)
    values = np.asarray(values[order], dtype=float)
    modes = np.asarray(modes[:, order], dtype=float)
    if np.any(values <= 0.0):
        raise RuntimeError("stiff scalar force operator is not positive")

    residuals = []
    stiffness_norm = float(np.linalg.norm(stiffness.data))
    mass_norm = float(np.linalg.norm(mass.data))
    for index, (value, mode) in enumerate(zip(values, modes.T)):
        mode /= math.sqrt(float(mode @ (normalization @ mode)))
        if mode[0] < 0.0:
            mode *= -1.0
        residual = stiffness @ mode - value * (mass @ mode)
        scale = np.linalg.norm(mode) * (
            stiffness_norm + abs(value) * mass_norm
        )
        residuals.append(float(np.linalg.norm(residual) / max(scale, 1.0e-300)))
        modes[:, index] = mode

    gram = modes.T @ (normalization @ modes)
    integral_g = float(np.trapezoid(np.exp(2.0 * warp), u))
    beta = math.sqrt(integral_g / 8.0) * modes[0, :]
    alpha = 2.0 * np.square(beta)
    masses = np.sqrt(values)
    return {
        "samples": int(u.size),
        "masses_mu": masses.tolist(),
        "mass_squared_mu2": values.tolist(),
        "uv_mode_value_h_n": modes[0, :].tolist(),
        "ir_mode_value_h_n": modes[-1, :].tolist(),
        "beta_uv": beta.tolist(),
        "alpha_uv_2_beta_squared": alpha.tolist(),
        "I_g": integral_g,
        "normalization_orthogonality_max_abs": float(
            np.max(np.abs(gram - np.eye(MODE_COUNT)))
        ),
        "normwise_backward_error_max": max(residuals),
        "profiles": {"u": u.tolist(), "h_n": modes.T.tolist()},
    }


def _without_profiles(solution: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in solution.items() if key != "profiles"}


def _force_ratio(masses: np.ndarray, alpha: np.ndarray, x: float) -> float:
    return float(np.sum(alpha * (1.0 + masses * x) * np.exp(-masses * x)))


def build() -> dict[str, Any]:
    background_path = REPO / BACKGROUND_RELATIVE
    boundary_path = REPO / BOUNDARY_RELATIVE
    background = _read(background_path)
    boundary = _read(boundary_path)
    if boundary.get("passes", {}).get("all") is not True:
        raise RuntimeError("boundary completion is not certified")
    if boundary["stiff_candidate"]["definition"] != "gamma_-,gamma_+ -> infinity":
        raise RuntimeError("unexpected boundary candidate")

    full = solve(background)
    half = solve(background, 2)
    quarter = solve(background, 4)
    masses = np.asarray(full["masses_mu"])
    beta = np.asarray(full["beta_uv"])
    alpha = np.asarray(full["alpha_uv_2_beta_squared"])
    boundary_masses = np.asarray(
        boundary["stiff_candidate"]["spectrum"]["masses_mu"]
    )

    half_mass_relative = np.abs(
        np.asarray(half["masses_mu"]) / masses - 1.0
    )
    quarter_mass_relative = np.abs(
        np.asarray(quarter["masses_mu"]) / masses - 1.0
    )
    half_beta_relative = np.abs(np.asarray(half["beta_uv"]) / beta - 1.0)
    quarter_beta_relative = np.abs(
        np.asarray(quarter["beta_uv"]) / beta - 1.0
    )
    boundary_mass_relative = np.abs(masses / boundary_masses - 1.0)
    anchor_response = [
        {"x_r_over_ell": x, "scalar_acceleration_over_newton": _force_ratio(masses, alpha, x)}
        for x in ANCHOR_X
    ]

    passes = {
        "certified_inputs": True,
        "observational_blinding": True,
        "positive_ordered_spectrum": bool(
            np.all(masses > 0.0) and np.all(np.diff(masses) > 0.0)
        ),
        "positive_force_residues": bool(np.all(alpha > 0.0)),
        "boos_and_junction_mass_agreement": bool(
            np.max(boundary_mass_relative) <= BOUNDARY_MASS_RELATIVE_MAX
        ),
        "half_grid_mass_convergence": bool(
            np.max(half_mass_relative) <= MASS_HALF_GRID_RELATIVE_MAX
        ),
        "quarter_grid_mass_convergence": bool(
            np.max(quarter_mass_relative) <= MASS_QUARTER_GRID_RELATIVE_MAX
        ),
        "half_grid_beta_convergence": bool(
            np.max(half_beta_relative) <= BETA_HALF_GRID_RELATIVE_MAX
        ),
        "quarter_grid_beta_convergence": bool(
            np.max(quarter_beta_relative) <= BETA_QUARTER_GRID_RELATIVE_MAX
        ),
        "normalization_orthonormal": bool(
            full["normalization_orthogonality_max_abs"] <= 1.0e-10
        ),
        "backward_error_bounded": bool(
            full["normwise_backward_error_max"] <= BACKWARD_ERROR_MAX
        ),
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.stiff-boundary-force.v1",
        "title": "Canonically normalized stiff-boundary scalar force",
        "classification": "prospective_stiff_boundary_force_not_detection",
        "inputs": {
            "background": {
                "path": BACKGROUND_RELATIVE.as_posix(),
                "sha256": _sha256(background_path),
            },
            "boundary_completion": {
                "path": BOUNDARY_RELATIVE.as_posix(),
                "sha256": _sha256(boundary_path),
            },
        },
        "observational_inputs_read": [],
        "historical_trace_residues_reused": [],
        "primary_theory_input": {
            "reference": "Boos, Mikhailov, Smolyakov and Volobuev (2006)",
            "arxiv": "hep-th/0511185",
            "role": "second-variation scalar normalization and brane matter vertex",
        },
        "translated_problem": {
            "boos_scalar": (
                "g=e^{-2 A_B} h_44 with A_B=-A; stiff boundaries g_u=0"
            ),
            "operator": (
                "-d_u[p_g d_u h_n]+q_g h_n=mu_n^2 w_g h_n; "
                "p_g=exp(-2A)/chi_u^2; q_g=exp(-2A)/3; "
                "w_g=exp(-4A)/chi_u^2"
            ),
            "canonical_normalization": (
                "(3/2) int du exp(-2A) [h_n h_m+"
                "3 h_n' h_m'/chi_u^2]=delta_nm"
            ),
            "tensor_relative_coupling": (
                "alpha_n=[h_n(UV)/(2 psi_0(UV))]^2; "
                "psi_0(UV)=1/sqrt(I_g)"
            ),
            "scalar_tensor_convention": (
                "alpha_n=2 beta_n^2=I_g h_n(UV)^2/4"
            ),
        },
        "spectrum_and_force": {
            **_without_profiles(full),
            "sum_alpha_short_distance": float(np.sum(alpha)),
            "maximum_baryonic_acceleration_multiplier": float(1.0 + np.sum(alpha)),
            "maximum_circular_speed_multiplier": float(math.sqrt(1.0 + np.sum(alpha))),
            "physical_scale_rule": "m_n=mu_n/ell; ell remains independent",
            "static_force": (
                "a_scalar/a_Newton=sum_n alpha_n(1+mu_n*x)exp(-mu_n*x)"
            ),
            "anchor_response": anchor_response,
        },
        "convergence": {
            "half_grid": {
                **_without_profiles(half),
                "mass_relative_to_full": half_mass_relative.tolist(),
                "beta_relative_to_full": half_beta_relative.tolist(),
                "maximum_mass_relative": float(np.max(half_mass_relative)),
                "maximum_beta_relative": float(np.max(half_beta_relative)),
            },
            "quarter_grid": {
                **_without_profiles(quarter),
                "mass_relative_to_full": quarter_mass_relative.tolist(),
                "beta_relative_to_full": quarter_beta_relative.tolist(),
                "maximum_mass_relative": float(np.max(quarter_mass_relative)),
                "maximum_beta_relative": float(np.max(quarter_beta_relative)),
            },
            "junction_representation_mass_relative": boundary_mass_relative.tolist(),
            "maximum_junction_representation_mass_relative": float(
                np.max(boundary_mass_relative)
            ),
        },
        "profiles": full["profiles"],
        "passes": passes,
        "evidence_boundary": (
            "This derives the stiff-limit dimensionless force residues from the "
            "coupled scalar-metric action. The stiff limit is a declared candidate, "
            "not selected by the bulk; ell and any observational detection remain "
            "unfixed."
        ),
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    force = result["spectrum_and_force"]
    print(f"[stiff boundary force] {OUTPUT}")
    print(
        "[short-distance scalar fraction] {:.9g}".format(
            force["sum_alpha_short_distance"]
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
