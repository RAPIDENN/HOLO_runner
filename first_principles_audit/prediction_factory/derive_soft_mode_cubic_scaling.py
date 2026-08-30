#!/usr/bin/env python3
"""Expose critical scaling of a brane-cubic soft-mode proxy.

The superpotential-matched brane potentials already fix third derivatives
lambda_-'''=W''' and lambda_+'''=-W''' because the stabilizing gamma terms are
quadratic.  This script combines those derived endpoint jets with the
generalized-normalized light eigenfunction and asks how the schematic brane
projection

    g000_brane_proxy = sum_i exp(4 A_i) lambda_i''' Psi_0(u_i)^3

scales as gamma tends to zero.  Psi is not delta-chi, and bulk plus brane-
bending cubic terms are absent, so this is a scaling proxy, not the physical
canonical cubic vertex.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import scipy
from scipy.interpolate import CubicSpline
from scipy.sparse.linalg import eigsh

try:
    from first_principles_audit.prediction_factory import (
        derive_superpotential_boundary_completion as boundary_solver,
    )
except ModuleNotFoundError:
    import derive_superpotential_boundary_completion as boundary_solver


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
EFFECTIVE_ACTION = REPO / "first_principles_audit/artifacts/holo_effective_action.json"
BOUNDARY = HERE / "artifacts" / "superpotential_boundary_completion.json"
OUTPUT = HERE / "artifacts" / "soft_mode_cubic_scaling.json"


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


def superpotential_third_derivative(
    arrays: tuple[np.ndarray, ...],
) -> np.ndarray:
    """Return W_chi_chi_chi at the two endpoints."""

    u, _warp, _warp_u, chi, chi_u = arrays
    chi_uu = CubicSpline(u, chi_u).derivative()(u)
    w_chi_chi = chi_uu / chi_u
    return np.asarray(
        CubicSpline(chi, w_chi_chi).derivative()(chi[[0, -1]]),
        dtype=float,
    )


def superpotential_fourth_derivative(
    arrays: tuple[np.ndarray, ...],
) -> np.ndarray:
    """Return W_chi_chi_chi_chi at the two endpoints."""

    u, _warp, _warp_u, chi, chi_u = arrays
    chi_uu = CubicSpline(u, chi_u).derivative()(u)
    w_chi_chi = chi_uu / chi_u
    return np.asarray(
        CubicSpline(chi, w_chi_chi).derivative(2)(chi[[0, -1]]),
        dtype=float,
    )


def light_mode(
    arrays: tuple[np.ndarray, ...], gamma: float
) -> tuple[float, np.ndarray]:
    """Solve and orient the generalized-normalized light eigenfunction."""

    stiffness, mass, _ = boundary_solver._scalar_matrices(arrays, gamma, gamma)
    values, modes = eigsh(
        stiffness,
        k=2,
        M=mass,
        sigma=1.0e-8,
        which="LM",
        tol=1.0e-11,
        maxiter=100000,
        v0=np.linspace(1.0, 2.0, stiffness.shape[0]),
    )
    index = int(np.argmin(values))
    value = float(values[index])
    if value <= 0.0:
        raise RuntimeError("light mode is not positive")
    mode = np.asarray(modes[:, index], dtype=float)
    mode /= math.sqrt(float(mode @ (mass @ mode)))
    if mode[0] < 0.0:
        mode *= -1.0
    return math.sqrt(value), mode


def build() -> dict[str, Any]:
    effective = _read(EFFECTIVE_ACTION)
    boundary = _read(BOUNDARY)
    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective action must pass first")
    if boundary.get("passes", {}).get("all") is not True:
        raise RuntimeError("boundary completion must pass first")

    arrays = boundary_solver._background(effective)
    u, warp, _warp_u, _chi, chi_u = arrays
    w3 = superpotential_third_derivative(arrays)
    lambda3 = np.asarray([w3[0], -w3[1]], dtype=float)
    w4 = superpotential_fourth_derivative(arrays)
    lambda4 = np.asarray([w4[0], -w4[1]], dtype=float)
    endpoint_warp = warp[[0, -1]]
    endpoint_mass_weight = 1.0 / np.square(chi_u[[0, -1]])

    convergence = {}
    convergence4 = {}
    for stride, label in ((1, "full"), (2, "half"), (4, "quarter")):
        candidate = (
            arrays
            if stride == 1
            else boundary_solver._subsample(arrays, stride)
        )
        convergence[label] = superpotential_third_derivative(candidate).tolist()
        convergence4[label] = superpotential_fourth_derivative(candidate).tolist()
    full_w3 = np.asarray(convergence["full"])
    half_error = np.abs(np.asarray(convergence["half"]) / full_w3 - 1.0)
    quarter_error = np.abs(np.asarray(convergence["quarter"]) / full_w3 - 1.0)

    gamma_rows = boundary["stabilized_family"]["equal_gamma_scan"][:4]
    rows = []
    for source_row in gamma_rows:
        gamma = float(source_row["gamma_minus"])
        mu0, mode = light_mode(arrays, gamma)
        endpoint_mode = mode[[0, -1]]
        contributions = np.exp(4.0 * endpoint_warp) * lambda3 * endpoint_mode**3
        quartic_contributions = (
            np.exp(4.0 * endpoint_warp) * lambda4 * endpoint_mode**4
        )
        boundary_norm_contributions = (
            endpoint_mass_weight * endpoint_mode**2 / gamma
        )
        proxy = float(np.sum(contributions))
        rows.append(
            {
                "gamma": gamma,
                "mu0": mu0,
                "endpoint_Psi0": endpoint_mode.tolist(),
                "endpoint_contributions": contributions.tolist(),
                "brane_cubic_proxy": proxy,
                "endpoint_quartic_contributions": quartic_contributions.tolist(),
                "brane_quartic_proxy": float(np.sum(quartic_contributions)),
                "boundary_mass_norm_contributions": (
                    boundary_norm_contributions.tolist()
                ),
                "Psi_uv_over_mu0": float(endpoint_mode[0] / mu0),
                "Psi_ir_over_mu0": float(endpoint_mode[1] / mu0),
                "brane_cubic_proxy_over_mu0_cubed": float(proxy / mu0**3),
                "brane_quartic_proxy_over_mu0_fourth": float(
                    np.sum(quartic_contributions) / mu0**4
                ),
            }
        )

    mu0 = np.asarray([row["mu0"] for row in rows])
    uv = np.asarray([row["endpoint_Psi0"][0] for row in rows])
    ir = np.asarray([row["endpoint_Psi0"][1] for row in rows])
    proxy = np.asarray([row["brane_cubic_proxy"] for row in rows])
    quartic_proxy = np.asarray([row["brane_quartic_proxy"] for row in rows])
    uv_ratio = uv / mu0
    ir_ratio = ir / mu0
    cubic_ratio = proxy / mu0**3
    quartic_ratio = quartic_proxy / mu0**4

    uv_slope = float(np.polyfit(np.log(mu0), np.log(np.abs(uv)), 1)[0])
    ir_slope = float(np.polyfit(np.log(mu0), np.log(np.abs(ir)), 1)[0])
    cubic_slope = float(
        np.polyfit(np.log(mu0), np.log(np.abs(proxy)), 1)[0]
    )
    quartic_slope = float(
        np.polyfit(np.log(mu0), np.log(quartic_proxy), 1)[0]
    )

    scaling_checks = {
        "certified_inputs": True,
        "endpoint_W_third_derivatives_subsample_stable_for_frozen_input": (
            float(np.max(half_error)) < 0.002
            and float(np.max(quarter_error)) < 0.004
        ),
        "endpoint_profiles_scale_linearly_with_mu0": (
            abs(uv_slope - 1.0) < 0.005 and abs(ir_slope - 1.0) < 0.005
        ),
        "brane_cubic_proxy_scales_as_mu0_cubed": (
            abs(cubic_slope - 3.0) < 0.005
        ),
        "minimal_brane_quartic_proxy_is_positive": bool(
            np.all(quartic_proxy > 0.0)
        ),
        "minimal_brane_quartic_proxy_scales_as_mu0_fourth": (
            abs(quartic_slope - 4.0) < 0.005
        ),
        "scaled_ir_profile_is_constant": (
            float(np.ptp(ir_ratio) / np.mean(np.abs(ir_ratio))) < 2.0e-5
        ),
        "scaled_brane_proxy_is_constant": (
            float(np.ptp(cubic_ratio) / np.mean(np.abs(cubic_ratio))) < 1.0e-4
        ),
        "no_observational_inputs_read": True,
    }
    scaling_checks["all"] = all(scaling_checks.values())

    physical_gates = {
        "higher_brane_jets_selected_by_microscopic_boundary_theory": False,
        "W_third_derivative_robust_to_background_smoothing": False,
        "Psi_to_delta_chi_gauge_reconstruction_derived_to_third_order": False,
        "bulk_cubic_vertex_derived": False,
        "brane_bending_cubic_vertex_derived": False,
        "canonical_physical_g000_derived": False,
        "physical_source_orientation_and_sign_derived": False,
        "quartic_stability_derived": False,
        "finite_nonlinear_matter_response_in_soft_limit_derived": False,
        "physical_completion": False,
    }

    return {
        "schema": "holo.soft-mode-cubic-scaling.v1",
        "title": "Critical scaling of the brane-cubic light-mode proxy",
        "classification": (
            "normalization_induced_scaling_proxy_with_underidentified_higher_jets;"
            "not_the_physical_cubic_vertex"
        ),
        "sources": {
            "effective_action": {
                "path": str(EFFECTIVE_ACTION.relative_to(REPO)),
                "sha256": _sha256(EFFECTIVE_ACTION),
            },
            "boundary_completion": {
                "path": str(BOUNDARY.relative_to(REPO)),
                "sha256": _sha256(BOUNDARY),
            },
            "observational_inputs_read": [],
        },
        "endpoint_jets": {
            "W_chi_chi_chi": w3.tolist(),
            "W_chi_chi_chi_chi": w4.tolist(),
            "lambda_minus_chi_chi_chi": float(lambda3[0]),
            "lambda_plus_chi_chi_chi": float(lambda3[1]),
            "lambda_minus_chi_chi_chi_chi": float(lambda4[0]),
            "lambda_plus_chi_chi_chi_chi": float(lambda4[1]),
            "exp_4A": np.exp(4.0 * endpoint_warp).tolist(),
            "convergence": convergence,
            "quartic_subsample_convergence": convergence4,
            "half_grid_maximum_relative_error": float(np.max(half_error)),
            "quarter_grid_maximum_relative_error": float(np.max(quarter_error)),
            "systematic_warning": (
                "Subsampling stability holds only for the frozen reconstructed "
                "background.  W''' is one derivative beyond the linear-action "
                "certificate and has not been shown robust to its smoothing "
                "choice."
            ),
        },
        "proxy_definition": (
            "sum_i exp(4*A_i)*lambda_i'''*Psi0(u_i)^3; scaling diagnostic "
            "only, because Psi0 is not the reconstructed delta-chi fluctuation"
        ),
        "rows": rows,
        "scaling_law": {
            "Psi_uv_power_in_mu0": uv_slope,
            "Psi_ir_power_in_mu0": ir_slope,
            "brane_proxy_power_in_mu0": cubic_slope,
            "brane_quartic_proxy_power_in_mu0": quartic_slope,
            "mean_Psi_uv_over_mu0": float(np.mean(uv_ratio)),
            "mean_Psi_ir_over_mu0": float(np.mean(ir_ratio)),
            "mean_brane_proxy_over_mu0_cubed": float(np.mean(cubic_ratio)),
            "mean_brane_quartic_proxy_over_mu0_fourth": float(
                np.mean(quartic_ratio)
            ),
            "interpretation": (
                "The canonically generalized-normalized endpoint profiles and "
                "the schematic brane cubic vanish, but their ratios to mu0 and "
                "mu0^3 approach nonzero constants.  The IR boundary term already "
                "supplies almost all of v^T M v=1 at the smallest gamma, so much "
                "of this scaling is forced by the 1/gamma boundary norm.  It does "
                "not prove a nonlinear fixed point or finite force."
            ),
            "smallest_gamma_ir_boundary_norm_contribution": float(
                rows[0]["boundary_mass_norm_contributions"][1]
            ),
        },
        "sign_boundary": (
            "With Psi0(UV)>0 and the solved same-sign endpoint mode, the brane "
            "proxy of the minimal quadratic completion is negative.  Adding "
            "eta_i*(chi-chi_i)^3/6 leaves the background, gamma and linear "
            "spectrum unchanged while changing lambda_i''' arbitrarily.  Thus "
            "neither magnitude nor sign is predicted until a microscopic "
            "boundary theory, delta-chi, brane bending, bulk terms and source "
            "orientation are combined."
        ),
        "quartic_boundary": (
            "The minimal quadratic completion has positive endpoint lambda'''' "
            "and a positive proxy scaling as mu0^4, structurally matching a "
            "stabilizing quartic.  But adding zeta_i*(chi-chi_i)^4/24 leaves the "
            "background and linear spectrum unchanged and shifts it arbitrarily; "
            "Psi-to-delta-chi, bulk and bending terms are also missing."
        ),
        "physical_gates": physical_gates,
        "decisive_next_calculation": (
            "First derive the complete brane potential beyond quadratic from a "
            "microscopic boundary theory and establish smoothing-robust higher "
            "background jets.  Then expand to third/fourth gauge-invariant order, "
            "solve lapse/shift and brane-bending constraints, and evaluate g000 "
            "and lambda0000 along the frozen gamma continuation."
        ),
        "scaling_checks": scaling_checks,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    scaling = result["scaling_law"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[critical scaling] Psi_IR~mu0^{:.7g}, proxy~mu0^{:.7g}".format(
            scaling["Psi_ir_power_in_mu0"],
            scaling["brane_proxy_power_in_mu0"],
        )
    )
    print(
        "[scaled constants] Psi_IR/mu0={:.9g}, proxy/mu0^3={:.9g}".format(
            scaling["mean_Psi_ir_over_mu0"],
            scaling["mean_brane_proxy_over_mu0_cubed"],
        )
    )
    print(
        "[quartic proxy] power={:.7g}, proxy/mu0^4={:.9g}".format(
            scaling["brane_quartic_proxy_power_in_mu0"],
            scaling["mean_brane_quartic_proxy_over_mu0_fourth"],
        )
    )
    print(f"[physical completion] {result['physical_gates']['physical_completion']}")
    print(f"[scaling certificate] {'PASS' if result['scaling_checks']['all'] else 'FAIL'}")
    return 0 if result["scaling_checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
