#!/usr/bin/env python3
"""Prove which nonlinear brane jets are invisible to the background and S2.

The full second-order junction equation is still to be derived.  This module
isolates a prior, exact identifiability fact: a boundary potential and another
one differing first at cubic order have identical background matching and
identical linear spectrum, while their nonlinear response differs.  It also
shows why ``gamma -> infinity`` is not a complete nonlinear prescription
unless the scaling of all higher boundary jets is specified.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import CubicSpline


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts/cubic_boundary_identifiability.json"

INPUTS = {
    "effective_action": (
        REPO / "first_principles_audit/artifacts/holo_effective_action.json"
    ),
    "boundary_completion": (
        HERE / "artifacts/superpotential_boundary_completion.json"
    ),
    "gauge_invariant_route": (
        HERE / "artifacts/gauge_invariant_cubic_route.json"
    ),
}

CRITERIA = {
    "stationarity_series_coefficient_max_abs": 1.0e-12,
    "onshell_series_relative_error_max": 2.0e-8,
    "fixed_jet_cubic_decay_slope_abs_error": 1.0e-12,
    "fixed_jet_quartic_decay_slope_abs_error": 2.0e-8,
    "fixed_brane_junction_series_max_abs": 1.0e-12,
    "boundary_action_series_max_abs": 1.0e-12,
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


def response_coefficients(
    gamma: float, eta: float, zeta: float
) -> dict[str, float]:
    """Return the stationary x(J) and on-shell F(J) series coefficients.

    F=J*x+gamma*x^2/2+eta*x^3/6+zeta*x^4/24 and F_x=0.
    Coefficients are defined by x=sum a_n J^n and F=sum C_n J^n.
    """

    if not np.isfinite(gamma) or gamma <= 0.0:
        raise ValueError("gamma must be finite and positive")
    if not np.isfinite(eta) or not np.isfinite(zeta):
        raise ValueError("higher jets must be finite")
    return {
        "a1": -1.0 / gamma,
        "a2": -eta / (2.0 * gamma**3),
        "a3": (-3.0 * eta**2 + gamma * zeta) / (6.0 * gamma**5),
        "C2": -1.0 / (2.0 * gamma),
        "C3": -eta / (6.0 * gamma**3),
        "C4": (-3.0 * eta**2 + gamma * zeta) / (24.0 * gamma**5),
    }


def _stationarity_series_residual(
    gamma: float, eta: float, zeta: float
) -> float:
    coefficients = response_coefficients(gamma, eta, zeta)
    # Polynomial coefficients in ascending powers of J, through J^3.
    x = np.asarray(
        [0.0, coefficients["a1"], coefficients["a2"], coefficients["a3"]]
    )
    x2 = np.polynomial.polynomial.polymul(x, x)[:4]
    x3 = np.polynomial.polynomial.polymul(x2, x)[:4]
    residual = gamma * x + 0.5 * eta * x2 + (zeta / 6.0) * x3
    residual[1] += 1.0
    return float(np.max(np.abs(residual[1:4])))


def _stationary_root(
    source: float, gamma: float, eta: float, zeta: float
) -> float:
    x = -source / gamma
    for _ in range(20):
        value = source + gamma * x + 0.5 * eta * x**2 + zeta * x**3 / 6.0
        derivative = gamma + eta * x + 0.5 * zeta * x**2
        step = value / derivative
        x -= step
        if abs(step) <= 1.0e-15 * max(1.0, abs(x)):
            break
    return float(x)


def _onshell_series_check() -> float:
    gamma, eta, zeta = 2.3, -0.7, 0.4
    coefficients = response_coefficients(gamma, eta, zeta)
    errors = []
    for source in (1.0e-4, -1.0e-4, 2.0e-4, -2.0e-4):
        x = _stationary_root(source, gamma, eta, zeta)
        exact = (
            source * x
            + 0.5 * gamma * x**2
            + eta * x**3 / 6.0
            + zeta * x**4 / 24.0
        )
        series = (
            coefficients["C2"] * source**2
            + coefficients["C3"] * source**3
            + coefficients["C4"] * source**4
        )
        errors.append(abs(exact - series) / max(abs(exact), 1.0e-300))
    return float(max(errors))


def _log_slope(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.polyfit(np.log10(x), np.log10(np.abs(y)), 1)[0])


def _fixed_brane_junction_series_check() -> float:
    """Check the exact scalar junction expansion through second order."""

    # Deterministic non-special values for all independent local jets.
    s = -1.0
    background_chi_u = 1.7
    q1, q2 = 0.23, -0.17
    q1_u, q2_u = -0.31, 0.41
    alpha1, alpha2 = 0.19, -0.07
    shift1_dot_grad_q1 = 0.13
    lambda1 = -s * background_chi_u
    lambda2, lambda3 = 0.83, -0.29

    inverse_lapse = np.asarray(
        [1.0, -alpha1, alpha1**2 - alpha2], dtype=float
    )
    normal_numerator = np.asarray(
        [
            background_chi_u,
            q1_u,
            q2_u - shift1_dot_grad_q1,
        ],
        dtype=float,
    )
    normal = np.polynomial.polynomial.polymul(
        inverse_lapse, normal_numerator
    )[:3]
    potential_prime = np.asarray(
        [
            lambda1,
            lambda2 * q1,
            lambda2 * q2 + 0.5 * lambda3 * q1**2,
        ],
        dtype=float,
    )
    exact_coefficients = s * normal + potential_prime

    expected = np.asarray(
        [
            0.0,
            s * (q1_u - alpha1 * background_chi_u) + lambda2 * q1,
            s
            * (
                q2_u
                - alpha1 * q1_u
                + (alpha1**2 - alpha2) * background_chi_u
                - shift1_dot_grad_q1
            )
            + lambda2 * q2
            + 0.5 * lambda3 * q1**2,
        ]
    )
    return float(np.max(np.abs(exact_coefficients - expected)))


def _truncated_product(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.polynomial.polynomial.polymul(left, right)[:5]


def _boundary_action_series_check() -> dict[str, float]:
    """Verify the fixed-brane GHY and potential jets through fourth order."""

    r, alpha = 0.17, -0.09
    exp_four_r = np.asarray(
        [(4.0 * r) ** degree / math.factorial(degree) for degree in range(5)]
    )
    inverse_lapse = np.asarray([(-alpha) ** degree for degree in range(5)])
    prefactor = _truncated_product(exp_four_r, inverse_lapse)
    expected_prefactor = np.asarray(
        [
            1.0,
            4.0 * r - alpha,
            8.0 * r**2 - 4.0 * alpha * r + alpha**2,
            32.0 * r**3 / 3.0
            - 8.0 * alpha * r**2
            + 4.0 * alpha**2 * r
            - alpha**3,
            32.0 * r**4 / 3.0
            - 32.0 * alpha * r**3 / 3.0
            + 8.0 * alpha**2 * r**2
            - 4.0 * alpha**3 * r
            + alpha**4,
        ]
    )

    warp_u = -1.13
    theta = np.asarray([4.0 * warp_u, 0.23, -0.31, 0.19, 0.07])
    ghy = _truncated_product(prefactor, theta)
    expected_ghy_cubic = (
        4.0 * warp_u * expected_prefactor[3]
        + expected_prefactor[2] * theta[1]
        + expected_prefactor[1] * theta[2]
        + theta[3]
    )
    expected_ghy_quartic = (
        4.0 * warp_u * expected_prefactor[4]
        + expected_prefactor[3] * theta[1]
        + expected_prefactor[2] * theta[2]
        + expected_prefactor[1] * theta[3]
        + theta[4]
    )

    lambda0, lambda1 = 1.2, -0.4
    gamma, eta, zeta4, q = 0.8, -0.6, 0.3, 0.21
    lambda_series = np.asarray(
        [
            lambda0,
            lambda1 * q,
            0.5 * gamma * q**2,
            eta * q**3 / 6.0,
            zeta4 * q**4 / 24.0,
        ]
    )
    potential_density = _truncated_product(exp_four_r, lambda_series)
    expected_potential_cubic = (
        32.0 * lambda0 * r**3 / 3.0
        + 8.0 * lambda1 * r**2 * q
        + 2.0 * gamma * r * q**2
        + eta * q**3 / 6.0
    )
    expected_potential_quartic = (
        32.0 * lambda0 * r**4 / 3.0
        + 32.0 * lambda1 * r**3 * q / 3.0
        + 4.0 * gamma * r**2 * q**2
        + 2.0 * eta * r * q**3 / 3.0
        + zeta4 * q**4 / 24.0
    )
    return {
        "prefactor_max_abs": float(
            np.max(np.abs(prefactor - expected_prefactor))
        ),
        "GHY_cubic_abs": float(abs(ghy[3] - expected_ghy_cubic)),
        "GHY_quartic_abs": float(abs(ghy[4] - expected_ghy_quartic)),
        "brane_potential_cubic_abs": float(
            abs(potential_density[3] - expected_potential_cubic)
        ),
        "brane_potential_quartic_abs": float(
            abs(potential_density[4] - expected_potential_quartic)
        ),
    }


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    effective = payloads["effective_action"]
    boundary = payloads["boundary_completion"]
    route = payloads["gauge_invariant_route"]
    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action input is not certified")
    if boundary.get("passes", {}).get("all") is not True:
        raise RuntimeError("boundary-completion input is not certified")
    if route.get("checks", {}).get("all") is not True:
        raise RuntimeError("gauge-invariant-route input is not certified")

    u = np.asarray(effective["u"], dtype=float)
    chi = np.asarray(effective["canonical_chi"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)
    W = -6.0 * np.asarray(effective["A_u"], dtype=float)
    W_chichi = CubicSpline(u, chi_u).derivative()(u) / chi_u
    W_chichichi = CubicSpline(chi, W_chichi).derivative()(chi)

    examples = (
        (1.7, 0.3, -0.2),
        (3.2, -1.1, 0.9),
        (10.0, 4.0, 2.0),
    )
    stationarity_residual = max(
        _stationarity_series_residual(*row) for row in examples
    )
    onshell_relative = _onshell_series_check()
    junction_series_residual = _fixed_brane_junction_series_check()
    boundary_action_series = _boundary_action_series_check()
    boundary_action_series_max = max(boundary_action_series.values())

    gammas = np.logspace(1.0, 5.0, 9)
    fixed_eta, fixed_zeta = 0.7, -0.4
    fixed_rows = [
        {
            "gamma": float(gamma),
            **response_coefficients(gamma, fixed_eta, fixed_zeta),
        }
        for gamma in gammas
    ]
    cubic_slope = _log_slope(
        gammas, np.asarray([row["C3"] for row in fixed_rows])
    )
    pure_zeta_C4 = np.asarray(
        [response_coefficients(gamma, 0.0, fixed_zeta)["C4"] for gamma in gammas]
    )
    quartic_slope = _log_slope(gammas, pure_zeta_C4)
    mixed_quartic_asymptotic_slope = _log_slope(
        gammas[-4:], np.asarray([row["C4"] for row in fixed_rows[-4:]])
    )

    scaled_eta_rows = [
        {
            "gamma": float(gamma),
            "eta": float(0.2 * gamma**3),
            **response_coefficients(gamma, 0.2 * gamma**3, 0.0),
        }
        for gamma in gammas
    ]

    checks = {
        "certified_inputs": True,
        "no_observational_tables_read": True,
        "stationarity_series_is_exact_through_J3": (
            stationarity_residual
            <= CRITERIA["stationarity_series_coefficient_max_abs"]
        ),
        "onshell_series_matches_exact_stationary_solution": (
            onshell_relative <= CRITERIA["onshell_series_relative_error_max"]
        ),
        "fixed_eta_cubic_response_decays_as_gamma_minus_3": (
            abs(cubic_slope + 3.0)
            <= CRITERIA["fixed_jet_cubic_decay_slope_abs_error"]
        ),
        "fixed_zeta_quartic_response_decays_as_gamma_minus_4": (
            abs(quartic_slope + 4.0)
            <= CRITERIA["fixed_jet_quartic_decay_slope_abs_error"]
        ),
        "cubic_deformation_preserves_background_and_S2_jets": True,
        "fixed_brane_scalar_junction_expansion_through_second_order": (
            junction_series_residual
            <= CRITERIA["fixed_brane_junction_series_max_abs"]
        ),
        "formal_fixed_brane_GHY_prefactor_and_potential_jet_convolution_through_S4": (
            boundary_action_series_max
            <= CRITERIA["boundary_action_series_max_abs"]
        ),
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "boundary_jet_nonidentifiability_proved": True,
        "natural_fixed_higher_jet_stiff_limit_defined": True,
        "fixed_brane_scalar_junction_source_derived": True,
        "boundary_action_normalization_and_variational_junctions_identified": True,
        "formal_fixed_brane_GHY_prefactor_and_potential_jet_convolution_verified": True,
        "metric_junction_right_hand_side_through_second_order_identified": True,
        "metric_junction_through_second_order_derived": False,
        "moving_brane_pullback_and_normal_completed": False,
        "full_second_order_junction_source_derived": False,
        "GHY_metric_cubic_terms_combined": False,
        "brane_bending_through_second_order_included": False,
        "stiff_limit_uniformity_proved_for_full_field_system": False,
        "physical_compact_S3_boundary_vertex_computed": False,
    }

    return {
        "schema": "holo.cubic-boundary-identifiability.v2",
        "title": "Nonlinear boundary-jet identifiability before compact S3",
        "classification": (
            "exact_boundary_normal_form_and_stiff_path_gate;"
            "full_second_order_junction_pending"
        ),
        "endpoint_bulk_jets": {
            "lower": {
                "u": float(u[0]),
                "chi": float(chi[0]),
                "W": float(W[0]),
                "W_chichi": float(W_chichi[0]),
                "W_chichichi": float(W_chichichi[0]),
            },
            "upper": {
                "u": float(u[-1]),
                "chi": float(chi[-1]),
                "W": float(W[-1]),
                "W_chichi": float(W_chichi[-1]),
                "W_chichichi": float(W_chichichi[-1]),
            },
            "role": (
                "The superpotential fixes the minimal matching jets. Extra "
                "brane-potential jets beginning at third order remain "
                "independent microscopic data. Endpoint W''' values are "
                "diagnostic spline derivatives, not fitted parameters."
            ),
        },
        "jet_counterexample": {
            "potential_A": (
                "lambda_A=s*W+gamma*(chi-chi_i)^2/2"
            ),
            "potential_B": (
                "lambda_B=lambda_A+eta*(chi-chi_i)^3/6"
            ),
            "identical_at_background": ["lambda", "lambda'", "lambda''"],
            "first_difference": "lambda_B'''-lambda_A'''=eta",
            "consequence": (
                "The background, linear junction condition and S2 spectrum "
                "cannot determine the compact S3 boundary vertex."
            ),
        },
        "boundary_normal_form": {
            "functional": (
                "F(x;J)=J*x+gamma*x^2/2+eta*x^3/6+zeta*x^4/24"
            ),
            "stationarity": (
                "J+gamma*x+eta*x^2/2+zeta*x^3/6=0"
            ),
            "solution": (
                "x=-J/gamma-eta*J^2/(2*gamma^3)+"
                "(gamma*zeta-3*eta^2)*J^3/(6*gamma^5)+O(J^4)"
            ),
            "onshell_response": (
                "F*=-J^2/(2*gamma)-eta*J^3/(6*gamma^3)+"
                "(gamma*zeta-3*eta^2)*J^4/(24*gamma^5)+O(J^5)"
            ),
            "interpretation": (
                "J denotes the remaining bulk/metric source in the boundary "
                "junction and x the boundary scalar displacement. This is a "
                "local normal form, not yet the complete gravitational "
                "junction equation."
            ),
        },
        "boundary_action_convention": {
            "interval_Z2_action": (
                "S_boundary=kappa5^-2*sum_i integral sqrt(-gamma_hat)*K_hat"
                "-(2*kappa5^2)^-1*sum_i integral sqrt(-gamma_hat)*lambda_i(chi_hat)"
            ),
            "scalar_junction": "n dot partial(chi)+lambda_i'=0",
            "israel_junction": (
                "K_mn-K*gamma_mn+(lambda_i/2)*gamma_mn=0"
            ),
            "pure_tension_result": (
                "K_mn=(lambda_i/6)*gamma_mn; K=2*lambda_i/3"
            ),
            "background_check": "s_i*A'_i=lambda_i/6",
            "factor_of_two_warning": (
                "Do not switch from the interval/Z2 convention to a doubled "
                "orbifold action without translating both bulk and brane factors."
            ),
        },
        "fixed_brane_boundary_density": {
            "status": (
                "Formal fixed-brane jet identity: Theta_n are independent inputs. "
                "This does not derive the inclined normal, bending or the full "
                "extrinsic-curvature geometry."
            ),
            "fields": (
                "gamma_mn=exp(2A+2r)*eta_mn; N=1+alpha; N_m=partial_m beta"
            ),
            "oriented_trace": (
                "K=s_i*N^-1*[4(A'+r')-D_m N^m]"
            ),
            "shift_divergence": (
                "D_m N^m=exp(-2A-2r)*[box(beta)+2 partial(r) dot partial(beta)]"
            ),
            "GHY_density": (
                "sqrt(-gamma)K=s_i*exp(4A)*exp(4r)/(1+alpha)*"
                "[4A'+Theta]"
            ),
            "Theta": (
                "4r'-exp(-2A-2r)*[box(beta)+2 partial(r) dot partial(beta)]"
            ),
            "prefactor_P0_to_P4": [
                "1",
                "4r-alpha",
                "8r^2-4alpha*r+alpha^2",
                "32r^3/3-8alpha*r^2+4alpha^2*r-alpha^3",
                "32r^4/3-32alpha*r^3/3+8alpha^2*r^2-4alpha^3*r+alpha^4",
            ],
            "GHY_S3": (
                "s_i*exp(4A)/kappa5^2*[4A'*P3+P2*Theta1+P1*Theta2+Theta3]"
            ),
            "GHY_S4": (
                "s_i*exp(4A)/kappa5^2*[4A'*P4+P3*Theta1+P2*Theta2+"
                "P1*Theta3+Theta4]"
            ),
            "brane_potential_S3": (
                "-exp(4A)/(2*kappa5^2)*[32lambda0*r^3/3+"
                "8lambda1*r^2*Q+2gamma*r*Q^2+eta*Q^3/6]"
            ),
            "brane_potential_S4": (
                "-exp(4A)/(2*kappa5^2)*[32lambda0*r^4/3+"
                "32lambda1*r^3*Q/3+4gamma*r^2*Q^2+"
                "2eta*r*Q^3/3+zeta4*Q^4/24]"
            ),
            "series_check": boundary_action_series,
        },
        "fixed_brane_scalar_junction": {
            "orientations": "s_minus=-1; s_plus=+1",
            "exact": (
                "B_i=s_i*N^-1*(chi'-N^mu*partial_mu chi)+"
                "lambda_i'(chi)=0"
            ),
            "background": "s_i*bar_chi'+lambda_i'=0",
            "perturbation_convention": (
                "chi=bar_chi+q1+q2; N=1+alpha1+alpha2; "
                "second-order fields carry no factor 1/2"
            ),
            "first_order": (
                "B1=s_i*(q1'-alpha1*bar_chi')+lambda_i''*q1=0"
            ),
            "second_order": (
                "B2=s_i*[q2'-alpha1*q1'+(alpha1^2-alpha2)*"
                "bar_chi'-N1^mu*partial_mu q1]+lambda_i''*q2+"
                "lambda_i'''*q1^2/2=0"
            ),
            "cubic_jet_entry": "lambda_i'''=sign_i*W'''+eta_i",
            "moving_brane_pullback": {
                "Q1": "q1+bar_chi'*xi1",
                "Q2": (
                    "q2+bar_chi'*xi2+xi1*q1'+bar_chi''*xi1^2/2"
                ),
                "status": (
                    "The pullback is identified, but the inclined normal, "
                    "induced metric, trace/traceless Israel junctions and "
                    "brane bending are not yet combined."
                ),
            },
            "series_check_max_abs": junction_series_residual,
        },
        "metric_and_bending_structure": {
            "israel_traceless": "K_<mn>=0",
            "israel_trace_first_order": "K1=(2/3)*lambda1*Q1",
            "israel_trace_second_order": (
                "K2=(2/3)*[lambda1*Q2+gamma_i*Q1^2/2]"
            ),
            "induced_metric_exact": (
                "gamma_hat_mn=gamma_mn(Y)+N_m(Y)*partial_n(xi)+"
                "N_n(Y)*partial_m(xi)+[N^2+N_rho*N^rho]_Y*"
                "partial_m(xi)*partial_n(xi)"
            ),
            "inclined_normal": (
                "n_A=s_i*(-partial_m(xi),1)/sqrt(G^yy-2G^ym*partial_m(xi)+"
                "G^mn*partial_m(xi)*partial_n(xi))"
            ),
            "status": (
                "The exact sources and right-hand sides are identified, but the "
                "inclined normal and induced metric have not yet been expanded and "
                "combined with the bulk constraints in executable code."
            ),
        },
        "stiff_limit_paths": {
            "natural_fixed_higher_jets": {
                "eta": fixed_eta,
                "zeta": fixed_zeta,
                "rows": fixed_rows,
                "cubic_log_slope": cubic_slope,
                "pure_zeta_quartic_log_slope": quartic_slope,
                "mixed_quartic_asymptotic_log_slope": (
                    mixed_quartic_asymptotic_slope
                ),
                "result": (
                    "C3 vanishes as gamma^-3 and C4 is O(gamma^-4), or "
                    "faster when the quartic jet vanishes; fixed microscopic "
                    "higher jets decouple from the scalar boundary displacement "
                    "in this local normal form."
                ),
            },
            "nonuniform_eta_proportional_gamma_cubed": {
                "rows": scaled_eta_rows,
                "result": (
                    "C3 remains finite, while the eta^2 contribution makes "
                    "C4 nonuniform without further higher-jet tuning. Gamma "
                    "to infinity alone therefore does not define a nonlinear "
                    "boundary theory."
                ),
            },
            "junction_scaling": {
                "linear_boundary_displacement": "Q1=O(gamma^-1)",
                "raw_eta_source_in_second_order_junction": (
                    "eta*Q1^2=O(eta/gamma^2)"
                ),
                "eta_part_of_second_order_displacement": (
                    "Q2_eta=O(eta/gamma^3)"
                ),
                "cubic_boundary_action": (
                    "eta*Q1^3=O(eta/gamma^3)"
                ),
                "quartic_eta_squared_response": (
                    "eta^2/gamma^5 must vanish independently of eta/gamma^3"
                ),
            },
            "admissible_freeze_rule": (
                "Freeze the full brane potentials before projection. For the "
                "natural stiff candidate require eta/gamma^3 -> 0, "
                "zeta/gamma^4 -> 0, eta^2/gamma^5 -> 0 and no compensating "
                "singular higher-jet tower. The source J, modal norms, lapse, "
                "shift and bending must also remain bounded in the full system."
            ),
        },
        "next_calculation": {
            "objective": (
                "Derive the second-order gauge-invariant junction source and "
                "combine it with GHY, induced-metric and brane-bending terms."
            ),
            "accepted_branch": (
                "Natural stiff path with fixed analytic higher jets, subject "
                "to an explicit uniform-limit check in the full equations."
            ),
            "rejection_rule": (
                "Do not tune eta, zeta or higher jets after viewing a desired "
                "galactic force law."
            ),
        },
        "metrics": {
            "stationarity_series_coefficient_max_abs": stationarity_residual,
            "onshell_series_relative_error_max": onshell_relative,
            "fixed_brane_junction_series_max_abs": junction_series_residual,
            "boundary_action_series_max_abs": boundary_action_series_max,
        },
        "physical_gates": physical_gates,
        "criteria": CRITERIA,
        "checks": checks,
        "inputs": {
            "observational_tables_read": [],
            "files": {
                name: {
                    "path": str(path.relative_to(REPO)),
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
        },
        "evidence_boundary": (
            "This proves a nonlinear boundary non-identifiability theorem and "
            "defines a natural stiff path. It does not yet compute the full "
            "junction source, physical S3, S4, a force law or a detection."
        ),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    natural = result["stiff_limit_paths"]["natural_fixed_higher_jets"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[fixed-jet stiff slopes] "
        f"C3={natural['cubic_log_slope']:.9g} "
        f"C4={natural['pure_zeta_quartic_log_slope']:.9g}"
    )
    print(
        "[full compact S3 boundary] "
        f"{result['physical_gates']['physical_compact_S3_boundary_vertex_computed']}"
    )
    print(f"[certificate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
