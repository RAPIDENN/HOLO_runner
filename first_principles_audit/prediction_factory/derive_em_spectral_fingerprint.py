#!/usr/bin/env python3
"""Derive the conditional electromagnetic double-comb fingerprint.

This calculation adds no observed series and fits no coupling.  It combines:

* the physical scalar-lapse constraint in the almost-radial gauge;
* every already-catalogued scalar boundary branch;
* a minimal bulk Maxwell field with Z=1 and Neumann photon data; and
* the independent Kaluza--Klein tower of that photon.

The output is dimensionless.  A physical length, source and atomic response
are deliberately left outside the certificate.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import root_scalar

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from first_principles_audit.derive_minimal_probe_completion import (
    _fem_matrices,
    _solve_modes,
)
from first_principles_audit.prediction_factory.derive_boundary_branches import (
    BRANCHES,
    _carrier,
    _solve,
)


EFFECTIVE = Path("first_principles_audit/artifacts/holo_effective_action.json")
BOUNDARIES = Path(
    "first_principles_audit/prediction_factory/artifacts/"
    "boundary_branch_catalogue.json"
)
EM_KERNEL = Path(
    "first_principles_audit/prediction_factory/em_kernel_completion.json"
)
OUTPUT = HERE / "em_spectral_fingerprint.json"

SCALAR_MODE_COUNT = 6
PHOTON_MODE_COUNT = 7  # one exact zero plus six positive modes
ANCHOR_X = (0.5, 1.0, 2.0, 5.0, 10.0)
FD_C_STEP = 1.0e-5
HF_FD_C_STEP = 3.0e-3
CRITERIA = {
    "scalar_d_half_grid_relative_max": 8.0e-4,
    "scalar_d_quarter_grid_relative_max": 4.0e-3,
    "c_derivative_finite_difference_relative_max": 1.0e-7,
    "photon_half_grid_mass_relative_max": 2.0e-4,
    "photon_quarter_grid_mass_relative_max": 8.0e-4,
    "photon_quarter_grid_residue_relative_max": 2.5e-3,
    "photon_shooting_mass_relative_max": 2.0e-5,
    "photon_hf_finite_difference_relative_max": 5.0e-6,
    "determinant_vertex_absolute_error_max": 2.0e-8,
}


def _read(relative: Path) -> dict[str, Any]:
    return json.loads((REPO / relative).read_text(encoding="utf-8"))


def _sha256(relative: Path) -> str:
    return hashlib.sha256((REPO / relative).read_bytes()).hexdigest()


def _indices(size: int, stride: int) -> np.ndarray:
    values = np.arange(0, size, stride, dtype=int)
    if values[-1] != size - 1:
        values = np.append(values, size - 1)
    return values


def _element_response_integrals(
    u: np.ndarray,
    warp_u: np.ndarray,
    chi: np.ndarray,
    profile: np.ndarray,
) -> tuple[float, float, float, float]:
    """Return N(0), N'(0), D(0), D'(0) for the lapse overlap.

    Profiles are P1 finite-element functions, so their derivative is constant
    on each cell.  Endpoint-averaging the smooth factors retains that element
    structure and makes the convergence audit explicit.
    """

    if not (
        u.size == warp_u.size == chi.size == profile.size
        and np.all(np.diff(u) > 0.0)
        and np.all(np.isfinite(warp_u))
        and np.all(warp_u != 0.0)
    ):
        raise ValueError("invalid scalar-response arrays")
    delta_profile = np.diff(profile)
    inv_warp = 1.0 / warp_u
    numerator = float(
        np.sum(delta_profile * 0.5 * (inv_warp[:-1] + inv_warp[1:]))
    )
    numerator_prime = float(
        np.sum(
            delta_profile
            * 0.5
            * (
                chi[:-1] * inv_warp[:-1]
                + chi[1:] * inv_warp[1:]
            )
        )
    )
    denominator = float(u[-1] - u[0])
    denominator_prime = float(np.trapezoid(chi, u))
    return numerator, numerator_prime, denominator, denominator_prime


def scalar_photon_coefficient(
    u: np.ndarray,
    warp_u: np.ndarray,
    chi: np.ndarray,
    profile: np.ndarray,
    root_ig_over_3: float,
    c_gamma: float = 0.0,
) -> float:
    """Evaluate d_gamma,n(c) for Z=exp(c chi) on a P1 scalar profile."""

    if not math.isfinite(c_gamma):
        raise ValueError("c_gamma must be finite")
    z_function = np.exp(c_gamma * (chi - float(np.mean(chi))))
    if not np.all(np.isfinite(z_function)) or np.any(z_function <= 0.0):
        raise ValueError("Z=exp(c chi) is not positive and finite")
    delta_profile = np.diff(profile)
    factor = z_function / warp_u
    numerator = float(
        np.sum(delta_profile * 0.5 * (factor[:-1] + factor[1:]))
    )
    denominator = float(np.trapezoid(z_function, u))
    return root_ig_over_3 * numerator / denominator


def scalar_photon_coefficient_and_slope(
    u: np.ndarray,
    warp_u: np.ndarray,
    chi: np.ndarray,
    profile: np.ndarray,
    root_ig_over_3: float,
) -> tuple[float, float]:
    numerator, numerator_prime, denominator, denominator_prime = (
        _element_response_integrals(u, warp_u, chi, profile)
    )
    value = root_ig_over_3 * numerator / denominator
    slope = root_ig_over_3 * (
        numerator_prime / denominator
        - numerator * denominator_prime / denominator**2
    )
    return value, slope


def _maxwell_prefactor(
    epsilon: float, trace_h: float, radial_h: float
) -> float:
    """Coefficient of one F_12 component in a Euclidean signature check."""

    metric = np.diag(
        [1.0 + epsilon * radial_h]
        + [1.0 + epsilon * trace_h / 4.0] * 4
    )
    determinant = float(np.linalg.det(metric))
    if determinant <= 0.0:
        raise ValueError("perturbed metric is not positive in determinant check")
    inverse = np.linalg.inv(metric)
    return math.sqrt(determinant) * inverse[1, 1] * inverse[2, 2]


def _determinant_vertex_certificate() -> dict[str, float | bool]:
    step = 1.0e-6
    trace_h = 0.73
    radial_h = -0.41
    derivative = (
        _maxwell_prefactor(step, trace_h, radial_h)
        - _maxwell_prefactor(-step, trace_h, radial_h)
    ) / (2.0 * step)
    pure_trace = (
        _maxwell_prefactor(step, trace_h, 0.0)
        - _maxwell_prefactor(-step, trace_h, 0.0)
    ) / (2.0 * step)
    expected = radial_h / 2.0
    error = abs(derivative - expected)
    return {
        "finite_difference_derivative": derivative,
        "expected_radial_lapse_derivative": expected,
        "absolute_error": error,
        "pure_four_dimensional_trace_derivative": pure_trace,
        "passes": bool(
            error <= CRITERIA["determinant_vertex_absolute_error_max"]
            and abs(pure_trace)
            <= CRITERIA["determinant_vertex_absolute_error_max"]
        ),
    }


def _subsampled_scalar_solution(
    effective: dict[str, Any],
    stride: int,
    left: str,
    right: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    u, warp_a, p_weight, w_weight = _carrier(effective)
    idx = _indices(u.size, stride)
    solution = _solve(
        u[idx],
        warp_a[idx],
        p_weight[idx],
        w_weight[idx],
        left,
        right,
    )
    return (
        u[idx],
        np.asarray(effective["A_u"], dtype=float)[idx],
        np.asarray(effective["canonical_chi"], dtype=float)[idx],
        solution,
    )


def _scalar_branches(
    effective: dict[str, Any], boundary: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, float]]:
    u = np.asarray(effective["u"], dtype=float)
    warp_a = np.asarray(effective["A"], dtype=float)
    warp_u = np.asarray(effective["A_u"], dtype=float)
    chi = np.asarray(effective["canonical_chi"], dtype=float)
    _, _, _, scalar_weight = _carrier(effective)
    ig = float(np.trapezoid(np.exp(2.0 * warp_a), u))
    root = math.sqrt(ig / 3.0)
    all_d_half_errors: list[float] = []
    all_d_quarter_errors: list[float] = []
    all_fd_errors: list[float] = []
    branches: dict[str, Any] = {}

    for code, (left, right) in BRANCHES.items():
        stored = boundary["branches"][code]
        modes: list[dict[str, float | int]] = []
        full_d: list[float] = []
        full_slope: list[float] = []
        profiles = [np.asarray(values, dtype=float) for values in stored["profiles"]]
        for index, (mu, beta, profile) in enumerate(
            zip(
                stored["masses_mu"],
                stored["uv_probe_couplings_beta_n"],
                profiles,
            )
        ):
            value, slope = scalar_photon_coefficient_and_slope(
                u, warp_u, chi, profile, root
            )
            finite_difference = (
                scalar_photon_coefficient(
                    u, warp_u, chi, profile, root, FD_C_STEP
                )
                - scalar_photon_coefficient(
                    u, warp_u, chi, profile, root, -FD_C_STEP
                )
            ) / (2.0 * FD_C_STEP)
            fd_relative = abs(finite_difference - slope) / max(abs(slope), 1.0e-14)
            all_fd_errors.append(fd_relative)
            alpha_mechanical = 2.0 * float(beta) ** 2
            source_to_alpha = 2.0 * float(beta) * value
            modes.append(
                {
                    "mode_index": index,
                    "mu_scalar": float(mu),
                    "beta_uv": float(beta),
                    "d_gamma_at_c0": value,
                    "partial_c_d_gamma_at_c0": slope,
                    "partial_c_finite_difference_relative_error": fd_relative,
                    "mechanical_yukawa_alpha": alpha_mechanical,
                    "source_to_delta_ln_alpha_per_U": source_to_alpha,
                }
            )
            full_d.append(value)
            full_slope.append(slope)

        convergence: dict[str, Any] = {}
        for stride, label, collector in (
            (2, "half_grid", all_d_half_errors),
            (4, "quarter_grid", all_d_quarter_errors),
        ):
            u_s, au_s, chi_s, solution = _subsampled_scalar_solution(
                effective, stride, left, right
            )
            a_s = np.asarray(effective["A"], dtype=float)[
                _indices(u.size, stride)
            ]
            ig_s = float(np.trapezoid(np.exp(2.0 * a_s), u_s))
            root_s = math.sqrt(ig_s / 3.0)
            values = [
                scalar_photon_coefficient_and_slope(
                    u_s, au_s, chi_s, np.asarray(profile), root_s
                )[0]
                for profile in solution["profiles"]
            ]
            relative = np.abs(
                np.asarray(values) / np.asarray(full_d) - 1.0
            )
            collector.extend(relative.tolist())
            convergence[label] = {
                "samples": int(u_s.size),
                "d_gamma_at_c0": values,
                "relative_to_full": relative.tolist(),
                "max_relative": float(np.max(relative)),
            }

        # The NN zero mode is stored separately by the branch catalogue.  Its
        # constant profile gives exactly zero photon coupling but nonzero
        # universal matter coupling.
        if code == "NN":
            _, mass_matrix = _fem_matrices(
                u,
                np.ones_like(u),
                scalar_weight,
            )
            # Only the P1 mass integration is relevant to the constant mode.
            ones = np.ones(u.size)
            iw = float(ones @ (mass_matrix @ ones))
            beta_zero = math.sqrt(ig / (3.0 * iw))
            modes.insert(
                0,
                {
                    "mode_index": 0,
                    "mu_scalar": 0.0,
                    "beta_uv": beta_zero,
                    "d_gamma_at_c0": 0.0,
                    "partial_c_d_gamma_at_c0": 0.0,
                    "partial_c_finite_difference_relative_error": 0.0,
                    "mechanical_yukawa_alpha": 2.0 * beta_zero**2,
                    "source_to_delta_ln_alpha_per_U": 0.0,
                },
            )
            for row in modes[1:]:
                row["mode_index"] = int(row["mode_index"]) + 1

        transfers: list[dict[str, float]] = []
        for x in ANCHOR_X:
            mechanical = sum(
                float(row["mechanical_yukawa_alpha"])
                * math.exp(-float(row["mu_scalar"]) * x)
                for row in modes
            )
            electromagnetic = sum(
                float(row["source_to_delta_ln_alpha_per_U"])
                * math.exp(-float(row["mu_scalar"]) * x)
                for row in modes
            )
            transfers.append(
                {
                    "x_r_over_ell": x,
                    "mechanical_delta_V_over_Newton": mechanical,
                    "delta_ln_alpha_per_Newtonian_U": electromagnetic,
                }
            )

        branches[code] = {
            "scalar_boundary_conditions": {
                "uv": left,
                "ir": right,
            },
            "physical_branch_selected": False,
            "uv_point_matter_decouples": stored["uv_point_probe_decouples"],
            "adjudication": stored["adjudication"],
            "modes": modes,
            "transfer_anchors": transfers,
            "convergence": convergence,
        }

    return branches, {
        "d_half_grid_relative_max": max(all_d_half_errors),
        "d_quarter_grid_relative_max": max(all_d_quarter_errors),
        "c_derivative_finite_difference_relative_max": max(all_fd_errors),
    }


def _photon_solution(
    u: np.ndarray, warp_a: np.ndarray, chi: np.ndarray, c_gamma: float
) -> dict[str, Any]:
    z_function = np.exp(c_gamma * (chi - float(np.mean(chi))))
    return _solve_modes(
        u,
        np.exp(2.0 * warp_a) * z_function,
        z_function,
        count=PHOTON_MODE_COUNT,
    )


def _shoot_photon_masses(
    u: np.ndarray, warp_a: np.ndarray, fem_masses: np.ndarray
) -> list[float]:
    spline_a = CubicSpline(u, warp_a)

    def residual(lam: float) -> float:
        def rhs(position: float, state: np.ndarray) -> list[float]:
            return [
                float(state[1] / math.exp(2.0 * float(spline_a(position)))),
                float(-lam * state[0]),
            ]

        solution = solve_ivp(
            rhs,
            (float(u[0]), float(u[-1])),
            [1.0, 0.0],
            rtol=2.0e-10,
            atol=2.0e-12,
            method="DOP853",
        )
        if not solution.success:
            raise RuntimeError("independent photon shooting integration failed")
        return float(solution.y[1, -1])

    masses: list[float] = []
    for mass in fem_masses[:3]:
        lam = float(mass**2)
        root = root_scalar(
            residual,
            bracket=(0.9 * lam, 1.1 * lam),
            xtol=1.0e-12,
            rtol=1.0e-12,
        )
        if not root.converged:
            raise RuntimeError("independent photon shooting root did not converge")
        masses.append(math.sqrt(root.root))
    return masses


def _photon_tower(effective: dict[str, Any]) -> tuple[dict[str, Any], dict[str, float]]:
    u = np.asarray(effective["u"], dtype=float)
    warp_a = np.asarray(effective["A"], dtype=float)
    chi = np.asarray(effective["canonical_chi"], dtype=float)
    full = _photon_solution(u, warp_a, chi, 0.0)
    masses = np.asarray(full["masses"], dtype=float)
    profiles = np.asarray(full["modes"], dtype=float)
    residue_ratios = np.square(profiles[0, :] / profiles[0, 0])

    stiffness_prime, mass_prime = _fem_matrices(
        u, chi * np.exp(2.0 * warp_a), chi
    )
    slopes: list[float] = [0.0]
    for index in range(1, PHOTON_MODE_COUNT):
        vector = profiles[:, index]
        eigenvalue = float(full["eigenvalues"][index])
        eigenvalue_slope = float(
            vector @ (stiffness_prime @ vector)
            - eigenvalue * vector @ (mass_prime @ vector)
        )
        slopes.append(eigenvalue_slope / (2.0 * eigenvalue))

    plus = _photon_solution(u, warp_a, chi, HF_FD_C_STEP)
    minus = _photon_solution(u, warp_a, chi, -HF_FD_C_STEP)
    finite_slopes = np.zeros(PHOTON_MODE_COUNT)
    finite_slopes[1:] = (
        np.log(np.asarray(plus["masses"])[1:])
        - np.log(np.asarray(minus["masses"])[1:])
    ) / (2.0 * HF_FD_C_STEP)
    hf_relative = np.abs(
        finite_slopes[1:] / np.asarray(slopes[1:]) - 1.0
    )

    convergence: dict[str, Any] = {}
    mass_errors: dict[int, np.ndarray] = {}
    residue_errors: dict[int, np.ndarray] = {}
    for stride, label in ((2, "half_grid"), (4, "quarter_grid")):
        idx = _indices(u.size, stride)
        solution = _photon_solution(u[idx], warp_a[idx], chi[idx], 0.0)
        sub_masses = np.asarray(solution["masses"])
        sub_profiles = np.asarray(solution["modes"])
        sub_residues = np.square(sub_profiles[0, :] / sub_profiles[0, 0])
        mass_relative = np.abs(sub_masses[1:] / masses[1:] - 1.0)
        residue_relative = np.abs(sub_residues[1:] / residue_ratios[1:] - 1.0)
        mass_errors[stride] = mass_relative
        residue_errors[stride] = residue_relative
        convergence[label] = {
            "samples": int(idx.size),
            "positive_masses_mu_gamma": sub_masses[1:].tolist(),
            "mass_relative_to_full": mass_relative.tolist(),
            "uv_residue_relative_to_full": residue_relative.tolist(),
        }

    shooting_masses = np.asarray(
        _shoot_photon_masses(u, warp_a, masses[1:]), dtype=float
    )
    shooting_relative = np.abs(shooting_masses / masses[1:4] - 1.0)

    modes = []
    for index in range(PHOTON_MODE_COUNT):
        modes.append(
            {
                "mode_index": index,
                "mu_gamma": float(masses[index]),
                "mass_rule": "m_gamma,n=mu_gamma,n/ell",
                "uv_charge_coupling_squared_relative_to_zero_mode": float(
                    residue_ratios[index]
                ),
                "partial_c_ln_mu_at_c0": float(slopes[index]),
            }
        )

    return {
        "boundary_conditions": "Neumann--Neumann photon data",
        "zero_mode": "exactly massless and flat for every positive Z(chi)",
        "modes": modes,
        "coulomb_template": (
            "V_Q(r)=V_Coulomb(r)[1+sum_(n>0) eta_n exp(-mu_gamma,n r/ell)]"
        ),
        "hellmann_feynman_identity": (
            "partial_c lambda_n=int du chi[exp(2A)(f_n')^2-lambda_n f_n^2]"
        ),
        "hellmann_feynman_finite_difference_relative_errors": hf_relative.tolist(),
        "independent_shooting": {
            "primary_fem_reused": False,
            "fem_masses_first_three": masses[1:4].tolist(),
            "shooting_masses_first_three": shooting_masses.tolist(),
            "relative_errors": shooting_relative.tolist(),
        },
        "convergence": convergence,
    }, {
        "half_grid_mass_relative_max": float(np.max(mass_errors[2])),
        "quarter_grid_mass_relative_max": float(np.max(mass_errors[4])),
        "quarter_grid_residue_relative_max": float(np.max(residue_errors[4])),
        "shooting_mass_relative_max": float(np.max(shooting_relative)),
        "hf_finite_difference_relative_max": float(np.max(hf_relative)),
    }


def build() -> dict[str, Any]:
    effective = _read(EFFECTIVE)
    boundary = _read(BOUNDARIES)
    em_kernel = _read(EM_KERNEL)
    if not effective["summary"]["passes"]["all"]:
        raise RuntimeError("effective action input failed")
    if not boundary["passes"]["all"]:
        raise RuntimeError("boundary catalogue input failed")
    if not all(em_kernel["passes"].values()):
        raise RuntimeError("coordinate-correct EM kernel input failed")

    scalar_branches, scalar_metrics = _scalar_branches(effective, boundary)
    photon_tower, photon_metrics = _photon_tower(effective)
    determinant = _determinant_vertex_certificate()
    photon_first = photon_tower["modes"][1]["mu_gamma"]
    for branch in scalar_branches.values():
        branch["photon_first_to_scalar_mass_ratios"] = [
            (
                None
                if float(row["mu_scalar"]) == 0.0
                else float(photon_first / float(row["mu_scalar"]))
            )
            for row in branch["modes"]
        ]

    passes = {
        "effective_action_input_certified": True,
        "boundary_catalogue_input_certified": True,
        "coordinate_correct_kernel_input_certified": True,
        "determinant_vertex": determinant["passes"],
        "scalar_d_half_grid_convergence": scalar_metrics[
            "d_half_grid_relative_max"
        ]
        <= CRITERIA["scalar_d_half_grid_relative_max"],
        "scalar_d_quarter_grid_convergence": scalar_metrics[
            "d_quarter_grid_relative_max"
        ]
        <= CRITERIA["scalar_d_quarter_grid_relative_max"],
        "scalar_c_derivative_finite_difference": scalar_metrics[
            "c_derivative_finite_difference_relative_max"
        ]
        <= CRITERIA["c_derivative_finite_difference_relative_max"],
        "photon_half_grid_mass_convergence": photon_metrics[
            "half_grid_mass_relative_max"
        ]
        <= CRITERIA["photon_half_grid_mass_relative_max"],
        "photon_quarter_grid_mass_convergence": photon_metrics[
            "quarter_grid_mass_relative_max"
        ]
        <= CRITERIA["photon_quarter_grid_mass_relative_max"],
        "photon_quarter_grid_residue_convergence": photon_metrics[
            "quarter_grid_residue_relative_max"
        ]
        <= CRITERIA["photon_quarter_grid_residue_relative_max"],
        "photon_independent_shooting": photon_metrics[
            "shooting_mass_relative_max"
        ]
        <= CRITERIA["photon_shooting_mass_relative_max"],
        "photon_hellmann_feynman_finite_difference": photon_metrics[
            "hf_finite_difference_relative_max"
        ]
        <= CRITERIA["photon_hf_finite_difference_relative_max"],
        "no_observational_inputs": True,
        "no_c_gamma_fit": True,
        "no_ell_assignment": True,
        "no_branch_selected": all(
            not row["physical_branch_selected"]
            for row in scalar_branches.values()
        ),
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.em-spectral-fingerprint.v1",
        "title": "Conditional scalar--photon double-comb fingerprint",
        "classification": "action_derived_conditional_template_not_detection",
        "inputs": {
            "effective_action": {"path": str(EFFECTIVE), "sha256": _sha256(EFFECTIVE)},
            "boundary_catalogue": {
                "path": str(BOUNDARIES),
                "sha256": _sha256(BOUNDARIES),
            },
            "coordinate_correct_em_kernel": {
                "path": str(EM_KERNEL),
                "sha256": _sha256(EM_KERNEL),
            },
        },
        "observational_inputs_read": [],
        "assumptions": [
            "the certified interval is a physical compact interval",
            "the photon propagates in the five-dimensional bulk",
            "the photon has Neumann-compatible boundary data and no brane kinetic terms",
            "the reported central fingerprint uses Z(chi)=1",
            "scalar endpoints are comoving in the almost-radial gauge",
            "matter sources are localized at the UV endpoint",
            "a conserved four-dimensional electric current couples minimally "
            "to the bulk photon at the UV endpoint",
            "no brane bending, endpoint displacement or backreaction",
        ],
        "derivation": {
            "constraint": "A_u h_uu=(d_u h)/4",
            "maxwell_linear_factor": "N=h_uu/2=(d_u h)/(8 A_u)",
            "scalar_photon_coefficient": (
                "d_gamma,n(c)=sqrt(I_g/3)<f_n'/A_u>_(Z=exp(c chi))"
            ),
            "slope_per_unfitted_c_gamma": (
                "partial_c d|_0=sqrt(I_g/3) Cov_u(chi,f_n'/A_u)"
            ),
            "source_to_alpha": (
                "delta ln alpha/U=sum_n 2 beta_n d_gamma,n exp(-mu_n r/ell), "
                "U=G M/r"
            ),
            "clock_ratio": (
                "delta ln(nu_A/nu_B)=Delta K_alpha delta ln alpha only after "
                "an atomic sensitivity Delta K_alpha is supplied"
            ),
        },
        "determinant_vertex_check": determinant,
        "scalar_boundary_branches": scalar_branches,
        "bulk_photon_tower": photon_tower,
        "brane_photon_branch": {
            "classical_trace_vertex": 0.0,
            "bulk_photon_KK_tower": None,
            "reason": (
                "four-dimensional Maxwell Weyl invariance cancels the conformal "
                "trace and there is no radial lapse integral"
            ),
        },
        "scale_rule": {
            "ell": None,
            "scalar_masses": "m_scalar,n=mu_scalar,n/ell",
            "photon_masses": "m_gamma,n=mu_gamma,n/ell",
            "cross_sector_mass_ratios": "mu_gamma,n/mu_scalar,m are ell-independent",
        },
        "metrics": {"scalar": scalar_metrics, "photon": photon_metrics},
        "criteria": CRITERIA,
        "passes": passes,
        "evidence_boundary": (
            "This is a parameter-free central fingerprint only inside the declared "
            "bulk-photon compactification. It neither selects the scalar boundary "
            "action nor supplies ell, a source amplitude, an atomic coefficient, "
            "or evidence for an observed interaction."
        ),
    }


def main() -> int:
    result = build()
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    photon = result["bulk_photon_tower"]["modes"]
    nn = result["scalar_boundary_branches"]["NN"]["modes"]
    print(f"[EM spectral fingerprint] {OUTPUT}")
    print(
        "[photon comb] "
        + ", ".join(f"{row['mu_gamma']:.7g}" for row in photon[:4])
    )
    print(
        "[NN d_gamma positive tower] "
        + ", ".join(f"{row['d_gamma_at_c0']:.7g}" for row in nn[1:])
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
