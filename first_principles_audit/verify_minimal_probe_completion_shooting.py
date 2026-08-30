#!/usr/bin/env python3
"""Independently verify the compact-interval spectrum by ODE shooting.

This verifier deliberately does not import the FEM implementation in
``derive_minimal_probe_completion.py``.  It reconstructs the Sturm--Liouville
carrier from the certified effective-action arrays, integrates the first-order
flux system, and finds Neumann eigenvalues from sign changes of the right-end
flux.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq


HERE = Path(__file__).resolve().parent
PRIMARY_PATH = HERE / "artifacts" / "minimal_probe_completion.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "minimal_probe_completion_shooting_verification.json"
)

POSITIVE_MODE_COUNT = 6
SEARCH_LAMBDA_MIN = 1.0e-7
SEARCH_LAMBDA_MAX = 20.0
SEARCH_GRID_POINTS = 201
ODE_RTOL = 1.0e-10
ODE_ATOL = 1.0e-12
ROOT_XTOL = 2.0e-11
ROOT_RTOL = 2.0e-11

# These comparison thresholds are fixed in this verifier, not copied from the
# primary FEM certificate.  They are looser than the ODE integration settings
# and tight enough to expose a discretization, boundary-condition, or
# normalization mismatch.
CRITERIA = {
    "positive_mode_count": POSITIVE_MODE_COUNT,
    "mass_relative_error_max": 1.0e-4,
    "uv_coupling_relative_error_max": 1.5e-4,
    "zero_mode_uv_coupling_relative_error_max": 1.0e-10,
    "right_neumann_relative_flux_max": 1.0e-8,
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _effective_path(primary: dict[str, Any], primary_path: Path) -> Path:
    path = Path(primary["input"]["path"])
    if path.is_absolute():
        return path
    return (primary_path.parent / path).resolve()


def _reconstruct_carrier(
    effective: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    u = np.asarray(effective["u"], dtype=float)
    A = np.asarray(effective["A"], dtype=float)
    A_u = np.asarray(effective["A_u"], dtype=float)
    phi_u = np.asarray(effective["phi_u"], dtype=float)
    kinetic = np.asarray(effective["kinetic_K_of_phi"], dtype=float)
    if not all(array.shape == u.shape for array in (A, A_u, phi_u, kinetic)):
        raise ValueError("Effective-action carrier arrays have unequal lengths")
    if not np.all(np.diff(u) > 0.0):
        raise ValueError("Radial grid is not strictly increasing")

    A_uu = -kinetic * np.square(phi_u) / 6.0
    epsilon_ed = -A_uu / np.square(A_u)
    p_weight = np.exp(4.0 * A) * epsilon_ed
    w_weight = np.exp(2.0 * A) * epsilon_ed
    if not (
        np.all(np.isfinite(p_weight))
        and np.all(np.isfinite(w_weight))
        and np.all(p_weight > 0.0)
        and np.all(w_weight > 0.0)
    ):
        raise ValueError("Reconstructed Sturm--Liouville carrier is not positive")
    return u, A, p_weight, w_weight


def _make_shooter(
    u: np.ndarray, p_weight: np.ndarray, w_weight: np.ndarray
) -> Callable[[float, np.ndarray | None], Any]:
    # Interpolating log(p) and log(w) keeps the continuous shooting carrier
    # positive without sharing the FEM code's element averaging.
    log_p = PchipInterpolator(u, np.log(p_weight), extrapolate=False)
    log_w = PchipInterpolator(u, np.log(w_weight), extrapolate=False)

    def shoot(eigenvalue: float, sample_grid: np.ndarray | None = None):
        def rhs(position: float, state: np.ndarray) -> np.ndarray:
            p_here = np.exp(log_p(position))
            w_here = np.exp(log_w(position))
            # state=(f, j), j=p f'; hence f'=j/p and j'=-lambda w f.
            return np.asarray(
                (state[1] / p_here, -eigenvalue * w_here * state[0]),
                dtype=float,
            )

        solution = solve_ivp(
            rhs,
            (float(u[0]), float(u[-1])),
            (1.0, 0.0),
            method="DOP853",
            rtol=ODE_RTOL,
            atol=ODE_ATOL,
            t_eval=sample_grid,
        )
        if not solution.success:
            raise RuntimeError(
                f"Shooting integration failed at lambda={eigenvalue}: "
                f"{solution.message}"
            )
        return solution

    return shoot


def _find_positive_roots(
    shoot: Callable[[float, np.ndarray | None], Any],
) -> tuple[list[float], list[list[float]]]:
    scan = np.linspace(
        SEARCH_LAMBDA_MIN, SEARCH_LAMBDA_MAX, SEARCH_GRID_POINTS
    )

    def residual(eigenvalue: float) -> float:
        return float(shoot(eigenvalue, None).y[1, -1])

    values = np.asarray([residual(value) for value in scan])
    brackets: list[tuple[float, float]] = []
    for left, right, f_left, f_right in zip(
        scan[:-1], scan[1:], values[:-1], values[1:]
    ):
        if f_left * f_right < 0.0:
            brackets.append((float(left), float(right)))

    roots = [
        float(
            brentq(
                residual,
                left,
                right,
                xtol=ROOT_XTOL,
                rtol=ROOT_RTOL,
            )
        )
        for left, right in brackets
    ]
    return roots, [[left, right] for left, right in brackets]


def _node_count(profile: np.ndarray) -> int:
    # Roots cannot coincide systematically with this unrelated sampled grid;
    # the tiny threshold only removes round-off zeros before counting signs.
    scale = max(float(np.max(np.abs(profile))), 1.0)
    signs = np.sign(profile[np.abs(profile) > 1.0e-13 * scale])
    return int(np.count_nonzero(signs[:-1] * signs[1:] < 0.0))


def verify(primary_path: Path = PRIMARY_PATH) -> dict[str, Any]:
    primary_path = Path(primary_path).resolve()
    primary = _read_json(primary_path)
    effective_path = _effective_path(primary, primary_path)
    effective = _read_json(effective_path)

    if not primary["passes"]["all"]:
        raise RuntimeError("Primary compact-interval certificate does not pass")
    if not effective["summary"]["passes"]["all"]:
        raise RuntimeError("Effective-action input certificate does not pass")

    u, A, p_weight, w_weight = _reconstruct_carrier(effective)
    shoot = _make_shooter(u, p_weight, w_weight)
    roots, brackets = _find_positive_roots(shoot)

    target_masses = np.asarray(
        primary["dimensionless_spectrum"]["masses_mu"][1:], dtype=float
    )[:POSITIVE_MODE_COUNT]
    target_beta = np.asarray(
        primary["uv_probe_couplings_beta_n"][1:], dtype=float
    )[:POSITIVE_MODE_COUNT]
    if target_masses.size != POSITIVE_MODE_COUNT:
        raise ValueError("Primary artifact lacks six positive target modes")
    if len(roots) != POSITIVE_MODE_COUNT:
        raise RuntimeError(
            f"Fixed shooting window found {len(roots)} roots, expected "
            f"{POSITIVE_MODE_COUNT}: {roots}"
        )

    I_g = float(np.trapezoid(np.exp(2.0 * A), u))
    modes: list[dict[str, Any]] = []
    shooting_masses: list[float] = []
    shooting_beta: list[float] = []
    node_counts: list[int] = []
    boundary_residuals: list[float] = []
    for index, eigenvalue in enumerate(roots, start=1):
        solution = shoot(eigenvalue, u)
        profile = np.asarray(solution.y[0], dtype=float)
        flux = np.asarray(solution.y[1], dtype=float)
        norm = float(np.sqrt(np.trapezoid(w_weight * np.square(profile), u)))
        profile /= norm
        flux /= norm

        mass = float(np.sqrt(eigenvalue))
        beta_uv = float(np.sqrt(I_g / 3.0) * profile[0])
        nodes = _node_count(profile)
        flux_scale = float(
            eigenvalue * np.trapezoid(np.abs(w_weight * profile), u)
        )
        relative_flux = float(abs(flux[-1]) / max(flux_scale, 1.0e-300))
        mass_error = float(abs(mass / target_masses[index - 1] - 1.0))
        beta_error = float(abs(beta_uv / target_beta[index - 1] - 1.0))

        shooting_masses.append(mass)
        shooting_beta.append(beta_uv)
        node_counts.append(nodes)
        boundary_residuals.append(relative_flux)
        modes.append(
            {
                "mode_index": index,
                "eigenvalue_lambda": eigenvalue,
                "mass_mu": mass,
                "node_count": nodes,
                "uv_coupling_beta": beta_uv,
                "right_flux": float(flux[-1]),
                "right_neumann_relative_flux": relative_flux,
                "target_mass_mu": float(target_masses[index - 1]),
                "mass_relative_error": mass_error,
                "target_uv_coupling_beta": float(target_beta[index - 1]),
                "uv_coupling_relative_error": beta_error,
            }
        )

    shooting_masses_array = np.asarray(shooting_masses)
    shooting_beta_array = np.asarray(shooting_beta)
    mass_errors = np.abs(shooting_masses_array / target_masses - 1.0)
    beta_errors = np.abs(shooting_beta_array / target_beta - 1.0)

    I_w = float(np.trapezoid(w_weight, u))
    zero_beta = float(np.sqrt(I_g / (3.0 * I_w)))
    target_zero_beta = float(primary["uv_probe_couplings_beta_n"][0])
    zero_beta_error = float(abs(zero_beta / target_zero_beta - 1.0))

    observations = list(primary.get("observational_inputs_read", []))
    passes = {
        "primary_certificate": True,
        "effective_action_certificate": True,
        "observational_blinding": observations == [],
        "positive_reconstructed_carrier": bool(
            np.all(p_weight > 0.0) and np.all(w_weight > 0.0)
        ),
        "fixed_window_mode_count": len(roots)
        == CRITERIA["positive_mode_count"],
        "strictly_increasing_eigenvalues": bool(np.all(np.diff(roots) > 0.0)),
        "sturm_node_sequence": node_counts
        == list(range(1, POSITIVE_MODE_COUNT + 1)),
        "right_neumann_boundary": max(boundary_residuals)
        <= CRITERIA["right_neumann_relative_flux_max"],
        "positive_masses_match": float(np.max(mass_errors))
        <= CRITERIA["mass_relative_error_max"],
        "positive_uv_couplings_match": float(np.max(beta_errors))
        <= CRITERIA["uv_coupling_relative_error_max"],
        "zero_mode_uv_coupling_match": zero_beta_error
        <= CRITERIA["zero_mode_uv_coupling_relative_error_max"],
    }
    passes["all"] = all(passes.values())

    return {
        "title": "Independent Neumann spectrum verification by ODE shooting",
        "classification": "independent_numerical_verification_not_detection",
        "inputs": {
            "primary_artifact": str(primary_path),
            "primary_artifact_sha256": _sha256(primary_path),
            "effective_action_artifact": str(effective_path),
            "effective_action_artifact_sha256": _sha256(effective_path),
            "samples": int(u.size),
            "domain": [float(u[0]), float(u[-1])],
        },
        "observational_inputs_read": [],
        "target_observational_inputs_declared": observations,
        "method": {
            "operator": "-(p f')'=lambda w f",
            "state": "(f,j) with j=p f'",
            "left_boundary": "f(u_min)=1, j(u_min)=0",
            "right_boundary": "j(u_max)=0",
            "carrier_reconstruction": (
                "A_uu=-K(phi) phi_u^2/6; epsilon=-A_uu/A_u^2; "
                "p=exp(4A) epsilon; w=exp(2A) epsilon"
            ),
            "interpolation": "shape-preserving cubic interpolation of log(p), log(w)",
            "integrator": "scipy solve_ivp DOP853",
            "root_finder": "independent fixed-window sign scan plus Brent bracketing",
            "normalization": "integral w f_n^2 du = 1 by trapezoidal quadrature",
            "primary_solver_reused": False,
            "fem_matrix_reused": False,
        },
        "numerical_settings": {
            "search_lambda": [SEARCH_LAMBDA_MIN, SEARCH_LAMBDA_MAX],
            "search_grid_points": SEARCH_GRID_POINTS,
            "ode_rtol": ODE_RTOL,
            "ode_atol": ODE_ATOL,
            "root_xtol": ROOT_XTOL,
            "root_rtol": ROOT_RTOL,
        },
        "reconstructed_carrier_ranges": {
            "p": [float(np.min(p_weight)), float(np.max(p_weight))],
            "w": [float(np.min(w_weight)), float(np.max(w_weight))],
        },
        "root_brackets": brackets,
        "modes": modes,
        "summary": {
            "positive_modes_checked": len(modes),
            "shooting_masses_mu": shooting_masses,
            "shooting_uv_couplings_beta_n": shooting_beta,
            "node_counts": node_counts,
            "mass_relative_error_max": float(np.max(mass_errors)),
            "uv_coupling_relative_error_max": float(np.max(beta_errors)),
            "right_neumann_relative_flux_max": max(boundary_residuals),
            "zero_mode_beta_shooting_normalization": zero_beta,
            "zero_mode_beta_target": target_zero_beta,
            "zero_mode_beta_relative_error": zero_beta_error,
        },
        "criteria": CRITERIA,
        "passes": passes,
        "evidence_boundary": (
            "This independently checks the declared Neumann compact-interval "
            "eigenproblem and UV normalization against the primary FEM result. "
            "It does not select the boundary completion, fix ell, read "
            "observations, or establish a detected interaction."
        ),
    }


def main() -> int:
    result = verify()
    _write_json(OUTPUT_PATH, result)
    summary = result["summary"]
    print(f"[shooting verification] {OUTPUT_PATH}")
    print(f"[observational inputs] {len(result['observational_inputs_read'])}")
    print(
        "[six positive modes] max mass rel={:.3e}  max beta rel={:.3e}".format(
            summary["mass_relative_error_max"],
            summary["uv_coupling_relative_error_max"],
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
