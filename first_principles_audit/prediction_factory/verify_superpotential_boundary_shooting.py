#!/usr/bin/env python3
"""Independently verify the stiff two-brane scalar spectrum by shooting."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BACKGROUND_RELATIVE = Path(
    "first_principles_audit/artifacts/holo_effective_action.json"
)
FEM_RELATIVE = Path(
    "first_principles_audit/prediction_factory/artifacts/"
    "superpotential_boundary_completion.json"
)
OUTPUT = HERE / "artifacts" / "superpotential_boundary_shooting.json"

BRACKET_FRACTION = 0.02
MASS_RELATIVE_TOLERANCE = 3.0e-4
ROOT_RESIDUAL_OVER_BRACKET_MAX = 1.0e-7


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


class StiffShootingProblem:
    def __init__(self, payload: dict[str, Any]):
        if payload.get("summary", {}).get("passes", {}).get("all") is not True:
            raise RuntimeError("effective-action background is not certified")
        self.u = np.asarray(payload["u"], dtype=float)
        self.warp = CubicSpline(self.u, np.asarray(payload["A"], dtype=float))
        self.warp_u = CubicSpline(
            self.u, np.asarray(payload["A_u"], dtype=float)
        )
        self.chi_u = CubicSpline(
            self.u, np.asarray(payload["canonical_chi_u"], dtype=float)
        )
        self.chi_uu = self.chi_u.derivative()

    def residual(self, mu_squared: float) -> float:
        if not math.isfinite(mu_squared) or mu_squared <= 0.0:
            raise ValueError("mu_squared must be positive and finite")
        lower = float(self.u[0])
        upper = float(self.u[-1])
        initial = [1.0, -2.0 * float(self.warp_u(lower))]

        def ode(position: float, state: np.ndarray) -> list[float]:
            warp = float(self.warp(position))
            warp_u = float(self.warp_u(position))
            chi_u = float(self.chi_u(position))
            chi_uu_over_u = float(self.chi_uu(position)) / chi_u
            warp_uu = -chi_u * chi_u / 6.0
            first_coefficient = 2.0 * warp_u - 2.0 * chi_uu_over_u
            zeroth_coefficient = (
                mu_squared * math.exp(-2.0 * warp)
                + 4.0 * (warp_uu - warp_u * chi_uu_over_u)
            )
            return [
                float(state[1]),
                -first_coefficient * float(state[1])
                - zeroth_coefficient * float(state[0]),
            ]

        solution = solve_ivp(
            ode,
            (lower, upper),
            initial,
            method="DOP853",
            rtol=2.0e-12,
            atol=2.0e-13,
            t_eval=[upper],
        )
        if not solution.success or solution.y.shape != (2, 1):
            raise RuntimeError("shooting integration failed")
        psi, psi_u = solution.y[:, -1]
        return float(psi_u + 2.0 * self.warp_u(upper) * psi)


def build() -> dict[str, Any]:
    background_path = REPO / BACKGROUND_RELATIVE
    fem_path = REPO / FEM_RELATIVE
    background = _read(background_path)
    fem = _read(fem_path)
    if fem.get("passes", {}).get("all") is not True:
        raise RuntimeError("FEM boundary certificate is not certified")
    targets = fem["stiff_candidate"]["spectrum"]["mass_squared_mu2"]
    problem = StiffShootingProblem(background)

    modes = []
    for index, target in enumerate(targets):
        target = float(target)
        lower = target * (1.0 - BRACKET_FRACTION)
        upper = target * (1.0 + BRACKET_FRACTION)
        residual_lower = problem.residual(lower)
        residual_upper = problem.residual(upper)
        if residual_lower * residual_upper >= 0.0:
            raise RuntimeError(f"mode {index} is not bracketed independently")
        root = float(
            brentq(
                problem.residual,
                lower,
                upper,
                xtol=1.0e-14,
                rtol=1.0e-14,
                maxiter=100,
            )
        )
        root_residual = abs(problem.residual(root))
        residual_scale = max(abs(residual_lower), abs(residual_upper))
        root_residual_over_bracket = root_residual / residual_scale
        fem_mass = math.sqrt(target)
        shooting_mass = math.sqrt(root)
        relative = abs(shooting_mass / fem_mass - 1.0)
        modes.append(
            {
                "index": index,
                "fem_mu": fem_mass,
                "shooting_mu": shooting_mass,
                "mass_relative_difference": relative,
                "root_residual_abs": root_residual,
                "root_residual_over_bracket": root_residual_over_bracket,
                "bracket_mu_squared": [lower, upper],
                "bracket_residual": [residual_lower, residual_upper],
            }
        )

    maximum_relative = max(row["mass_relative_difference"] for row in modes)
    maximum_residual = max(row["root_residual_abs"] for row in modes)
    maximum_scaled_residual = max(
        row["root_residual_over_bracket"] for row in modes
    )
    passes = {
        "background_input_certified": True,
        "fem_input_certified": True,
        "observational_blinding": True,
        "all_modes_bracketed": len(modes) == len(targets),
        "mass_agreement": maximum_relative <= MASS_RELATIVE_TOLERANCE,
        "root_residuals_bounded": (
            maximum_scaled_residual <= ROOT_RESIDUAL_OVER_BRACKET_MAX
        ),
    }
    passes["all"] = all(passes.values())
    return {
        "schema": "holo.superpotential-boundary-shooting.v1",
        "title": "Independent stiff-boundary scalar shooting verification",
        "classification": "independent_numerical_verification_not_detection",
        "inputs": {
            "background": {
                "path": BACKGROUND_RELATIVE.as_posix(),
                "sha256": _sha256(background_path),
            },
            "fem_target": {
                "path": FEM_RELATIVE.as_posix(),
                "sha256": _sha256(fem_path),
            },
        },
        "observational_inputs_read": [],
        "method": {
            "bulk_equation": (
                "Psi_uu+(2A_u-2chi_uu/chi_u)Psi_u+"
                "[mu^2 exp(-2A)+4(A_uu-A_u chi_uu/chi_u)]Psi=0"
            ),
            "stiff_boundaries": "Psi_u+2 A_u Psi=0 at UV and IR",
            "integrator": "DOP853 adaptive shooting",
            "root_solver": "Brent bracketed root",
            "independence": (
                "no finite-element matrices or eigenvectors are reused"
            ),
        },
        "criteria": {
            "bracket_fraction": BRACKET_FRACTION,
            "mass_relative_tolerance": MASS_RELATIVE_TOLERANCE,
            "root_residual_over_bracket_max": (
                ROOT_RESIDUAL_OVER_BRACKET_MAX
            ),
        },
        "modes": modes,
        "maximum_mass_relative_difference": maximum_relative,
        "maximum_root_residual_abs": maximum_residual,
        "maximum_root_residual_over_bracket": maximum_scaled_residual,
        "passes": passes,
        "evidence_boundary": (
            "Agreement verifies the stiff-limit dimensionless mass comb by a "
            "second numerical method. It does not select the stiff limit, fix "
            "a physical scale, derive force residues, or constitute detection."
        ),
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(f"[stiff shooting] {OUTPUT}")
    print(
        "[maximum mass difference] {:.6g}".format(
            result["maximum_mass_relative_difference"]
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
