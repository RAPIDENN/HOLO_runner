#!/usr/bin/env python3
"""Independently verify the UV-Neumann/IR-Dirichlet ultralight mode.

This verifier reconstructs the continuous carrier and integrates its flux
system.  It imports no FEM matrix or eigensolver from the branch catalogue.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq


HERE = Path(__file__).resolve().parent
EFFECTIVE_PATH = HERE.parent / "artifacts" / "holo_effective_action.json"
CATALOGUE_PATH = HERE / "artifacts" / "boundary_branch_catalogue.json"
OUTPUT_PATH = HERE / "artifacts" / "nd_ultralight_shooting.json"

SCAN = np.geomspace(1.0e-10, 1.0e-1, 121)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, Any]:
    effective = _read(EFFECTIVE_PATH)
    catalogue = _read(CATALOGUE_PATH)
    if not effective["summary"]["passes"]["all"]:
        raise RuntimeError("Effective-action certificate does not pass")
    if not catalogue["passes"]["all"]:
        raise RuntimeError("Boundary catalogue does not pass")

    u = np.asarray(effective["u"], dtype=float)
    A = np.asarray(effective["A"], dtype=float)
    A_u = np.asarray(effective["A_u"], dtype=float)
    phi_u = np.asarray(effective["phi_u"], dtype=float)
    kinetic = np.asarray(effective["kinetic_K_of_phi"], dtype=float)
    A_uu = -kinetic * np.square(phi_u) / 6.0
    epsilon = -A_uu / np.square(A_u)
    p = np.exp(4.0 * A) * epsilon
    w = np.exp(2.0 * A) * epsilon
    log_p = PchipInterpolator(u, np.log(p), extrapolate=False)
    log_w = PchipInterpolator(u, np.log(w), extrapolate=False)

    def shoot(eigenvalue: float, sample: bool = False):
        def rhs(position: float, state: np.ndarray) -> np.ndarray:
            p_here = float(np.exp(log_p(position)))
            w_here = float(np.exp(log_w(position)))
            return np.asarray(
                [state[1] / p_here, -eigenvalue * w_here * state[0]]
            )

        solution = solve_ivp(
            rhs,
            (float(u[0]), float(u[-1])),
            (1.0, 0.0),
            method="DOP853",
            rtol=3.0e-10,
            atol=1.0e-12,
            t_eval=u if sample else None,
        )
        if not solution.success:
            raise RuntimeError(solution.message)
        return solution

    residuals = np.asarray(
        [float(shoot(value).y[0, -1]) for value in SCAN], dtype=float
    )
    brackets = [
        (float(left), float(right))
        for left, right, f_left, f_right in zip(
            SCAN[:-1], SCAN[1:], residuals[:-1], residuals[1:]
        )
        if f_left * f_right < 0.0
    ]
    if len(brackets) != 1:
        raise RuntimeError(
            f"Expected exactly one ND root below lambda=0.1, found {brackets}"
        )
    eigenvalue = float(
        brentq(
            lambda value: float(shoot(value).y[0, -1]),
            *brackets[0],
            xtol=2.0e-12,
            rtol=2.0e-12,
        )
    )
    solution = shoot(eigenvalue, sample=True)
    profile = np.asarray(solution.y[0], dtype=float)
    flux = np.asarray(solution.y[1], dtype=float)
    norm = float(np.sqrt(np.trapezoid(w * np.square(profile), u)))
    profile /= norm
    flux /= norm
    I_g = float(np.trapezoid(np.exp(2.0 * A), u))
    beta_uv = float(np.sqrt(I_g / 3.0) * profile[0])
    mass_mu = float(np.sqrt(eigenvalue))

    target = catalogue["branches"]["ND"]
    target_mass = float(target["masses_mu"][0])
    target_beta = float(target["uv_probe_couplings_beta_n"][0])
    mass_error = float(abs(mass_mu / target_mass - 1.0))
    beta_error = float(abs(beta_uv / target_beta - 1.0))
    dirichlet_residual = float(abs(profile[-1]) / np.max(np.abs(profile)))
    left_flux_scale = float(
        eigenvalue * np.trapezoid(np.abs(w * profile), u)
    )
    neumann_residual = float(abs(flux[0]) / max(left_flux_scale, 1.0e-300))
    passes = {
        "effective_action_certified": True,
        "catalogue_certified": True,
        "fixed_window_has_one_root": len(brackets) == 1,
        "mass_matches_fem": mass_error < 2.0e-4,
        "uv_coupling_matches_fem": beta_error < 2.0e-4,
        "left_neumann": neumann_residual < 1.0e-10,
        "right_dirichlet": dirichlet_residual < 1.0e-8,
        "ultralight": mass_mu < 0.01,
        "no_observational_inputs": True,
    }
    passes["all"] = all(passes.values())
    return {
        "title": "Independent ND ultralight verification by continuous shooting",
        "classification": "independent_numerical_verification_not_detection",
        "inputs": {
            "effective_action_sha256": _sha256(EFFECTIVE_PATH),
            "branch_catalogue_sha256": _sha256(CATALOGUE_PATH),
        },
        "observational_inputs_read": [],
        "method": {
            "state": "(f,j), j=p f'",
            "left_boundary": "f(u_min)=1, j(u_min)=0",
            "right_boundary": "f(u_max)=0",
            "interpolation": "PCHIP interpolation of log(p) and log(w)",
            "integration": "DOP853",
            "root_window_lambda": [float(SCAN[0]), float(SCAN[-1])],
            "primary_fem_matrices_reused": False,
        },
        "root_bracket": list(brackets[0]),
        "eigenvalue_lambda": eigenvalue,
        "mass_mu": mass_mu,
        "uv_coupling_beta": beta_uv,
        "target_fem_mass_mu": target_mass,
        "target_fem_beta_uv": target_beta,
        "mass_relative_error": mass_error,
        "beta_relative_error": beta_error,
        "boundary_residuals": {
            "left_neumann_relative_flux": neumann_residual,
            "right_dirichlet_relative_value": dirichlet_residual,
        },
        "passes": passes,
        "evidence_boundary": (
            "This confirms that the hard IR wall creates an ultralight mode "
            "in the declared conditional compact branch. It does not select "
            "that branch, fix ell, or establish an observed interaction."
        ),
    }


def main() -> int:
    result = verify()
    _write(OUTPUT_PATH, result)
    print(f"[ND shooting] {OUTPUT_PATH}")
    print(
        "[root] lambda={:.12g} mu={:.12g} beta_uv={:.12g}".format(
            result["eigenvalue_lambda"],
            result["mass_mu"],
            result["uv_coupling_beta"],
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
