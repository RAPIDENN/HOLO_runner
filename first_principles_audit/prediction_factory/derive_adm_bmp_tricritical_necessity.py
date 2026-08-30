#!/usr/bin/env python3
"""Decide what the real Einstein--dilaton/BPS brane geometry forces.

This certificate uses the reconstructed 1,979-point Einstein--dilaton
background and the *functional* minimal brane ansatz

    lambda_i(chi) = -s_i W(chi),   s_-=-1, s_+=+1.

It never imports the synthetic bent-brane covariance fixture.  The static
ADM action is reduced on the first-order flow and checked directly against
the raw reconstructed bulk density.  The result is deliberately conditional:
the BPS brane ansatz has an exactly flat radion potential, whereas the bulk
background by itself fixes only lambda_i and lambda_i' at each endpoint and
does not select that ansatz.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import sympy as sp
from scipy.integrate import cumulative_trapezoid, simpson


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "adm_bmp_tricritical_necessity.json"
INPUTS = {
    "effective_action": REPO
    / "first_principles_audit/artifacts/holo_effective_action.json",
    "conditional_brane_family": HERE
    / "artifacts/superpotential_boundary_completion.json",
}
PAIR_FRACTIONS = (
    (0.00, 1.00),
    (0.025, 0.25),
    (0.05, 0.50),
    (0.20, 0.90),
    (0.45, 0.96),
)
CRITERIA = {
    "potential_identity_max_abs": 2.0e-12,
    "junction_max_abs": 2.0e-12,
    "raw_action_relative_max": 3.0e-8,
    "zero_mode_gram_min_eigenvalue": 1.0e-8,
    "mutation_min_relative": 1.0e-4,
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


def _background(payload: Mapping[str, Any]) -> tuple[np.ndarray, ...]:
    if payload.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action input is not certified")
    arrays = tuple(
        np.asarray(payload[key], dtype=float)
        for key in (
            "u",
            "A",
            "A_u",
            "canonical_chi",
            "canonical_chi_u",
            "potential_V_of_phi",
        )
    )
    u, warp, warp_u, chi, chi_u, _potential = arrays
    if not (
        u.size == 1979
        and all(array.shape == u.shape for array in arrays)
        and all(np.all(np.isfinite(array)) for array in arrays)
        and np.all(np.diff(u) > 0.0)
        and np.all(np.diff(chi) > 0.0)
        and np.all(warp_u < 0.0)
        and np.all(chi_u > 0.0)
    ):
        raise ValueError("invalid reconstructed Einstein--dilaton background")
    return arrays


def _symbolic_reduction() -> dict[str, Any]:
    """Reduce the interval action without choosing a numerical W."""

    W, W_chi = sp.symbols("W W_chi", real=True)
    A_u = -W / 6
    chi_u = W_chi
    A_uu = -(W_chi**2) / 6
    potential = W_chi**2 / 2 - W**2 / 3
    ricci = -8 * A_uu - 20 * A_u**2
    bulk_local = sp.simplify(ricci - chi_u**2 / 2 - potential)
    total_derivative_local = sp.simplify(
        (4 * A_u * W + W_chi * chi_u) / 3
    )

    # With Delta=[exp(4A)W]_-^+, these are the three coefficients of
    # Delta/kappa_5^2 for a single interval copy.
    bulk_coefficient = sp.Rational(1, 6)
    ghy_coefficient = -sp.Rational(2, 3)
    brane_coefficient = sp.Rational(1, 2)

    lower_scalar = sp.simplify(-chi_u + W_chi)
    upper_scalar = sp.simplify(chi_u - W_chi)
    lower_israel = sp.simplify(-A_u - W / 6)
    upper_israel = sp.simplify(A_u - (-W) / 6)
    action_sum = sp.simplify(
        bulk_coefficient + ghy_coefficient + brane_coefficient
    )

    hamiltonian = 12 * A_u**2 - chi_u**2 / 2 - potential
    square_completion = sp.simplify(
        12 * (A_u + W / 6) ** 2
        - (chi_u - W_chi) ** 2 / 2
        - (4 * A_u * W + W_chi * chi_u)
    )

    # Verify the two analytic zero-mode solutions without differentiating a
    # fitted spline.  a=A', b=A'', c=A''', E=exp(-2A), J'=exp(2A)=1/E.
    a, b, c, d, E, J = sp.symbols("a b c d E J", nonzero=True)

    def radial_derivative(expression: sp.Expr) -> sp.Expr:
        return sp.expand(
            sp.diff(expression, a) * b
            + sp.diff(expression, b) * c
            + sp.diff(expression, c) * d
            + sp.diff(expression, E) * (-2 * a * E)
            + sp.diff(expression, J) / E
        )

    chi_uu_over_chi_u = c / (2 * b)
    zero_mode_residuals = []
    for psi in (a * E, 1 - 2 * a * E * J):
        psi_u = radial_derivative(psi)
        psi_uu = radial_derivative(psi_u)
        residual = sp.simplify(
            psi_uu
            + (2 * a - 2 * chi_uu_over_chi_u) * psi_u
            + 4 * (b - a * chi_uu_over_chi_u) * psi
        )
        zero_mode_residuals.append(str(residual))

    return {
        "bulk_density_equals_total_derivative": bool(
            sp.simplify(bulk_local - total_derivative_local) == 0
        ),
        "lower_scalar_junction_zero": bool(lower_scalar == 0),
        "upper_scalar_junction_zero": bool(upper_scalar == 0),
        "lower_Israel_junction_zero": bool(lower_israel == 0),
        "upper_Israel_junction_zero": bool(upper_israel == 0),
        "on_shell_action_coefficient_sum": str(action_sum),
        "on_shell_action_cancels": bool(action_sum == 0),
        "Hamilton_Jacobi_square_completion_exact": bool(
            sp.simplify(hamiltonian - square_completion) == 0
        ),
        "zero_mode_bulk_equation_residuals": zero_mode_residuals,
        "two_zero_mode_bulk_solutions_exact": zero_mode_residuals == ["0", "0"],
        "pieces_in_units_of_Delta_over_kappa5_squared": {
            "bulk": str(bulk_coefficient),
            "GHY": str(ghy_coefficient),
            "branes": str(brane_coefficient),
        },
        "bulk_local_density": str(bulk_local),
        "one_third_exp_minus_4A_d_exp4AW": str(total_derivative_local),
    }


def _actual_background_checks(arrays: tuple[np.ndarray, ...]) -> dict[str, Any]:
    u, warp, warp_u, chi, chi_u, potential = arrays
    superpotential = -6.0 * warp_u
    potential_from_W = 0.5 * np.square(chi_u) - np.square(superpotential) / 3.0
    potential_residual = potential - potential_from_W
    orientations = np.asarray([-1.0, 1.0])
    endpoint_indices = np.asarray([0, u.size - 1])
    lambda_value = -orientations * superpotential[endpoint_indices]
    lambda_prime = -orientations * chi_u[endpoint_indices]
    scalar_junction = orientations * chi_u[endpoint_indices] + lambda_prime
    israel_junction = (
        orientations * warp_u[endpoint_indices] - lambda_value / 6.0
    )
    return {
        "samples": int(u.size),
        "u_domain": [float(u[0]), float(u[-1])],
        "chi_domain": [float(chi[0]), float(chi[-1])],
        "W_endpoints": superpotential[endpoint_indices].tolist(),
        "potential_identity_max_abs": float(
            np.max(np.abs(potential_residual))
        ),
        "scalar_junction_residuals": scalar_junction.tolist(),
        "Israel_junction_residuals": israel_junction.tolist(),
        "junction_max_abs": float(
            max(
                np.max(np.abs(scalar_junction)),
                np.max(np.abs(israel_junction)),
            )
        ),
    }


def _raw_interval_action_checks(
    arrays: tuple[np.ndarray, ...],
) -> dict[str, Any]:
    """Integrate the unsimplified bulk density on several real subintervals."""

    u, warp, warp_u, _chi, chi_u, potential = arrays
    superpotential = -6.0 * warp_u
    warp_uu = -np.square(chi_u) / 6.0
    ricci = -8.0 * warp_uu - 20.0 * np.square(warp_u)
    raw_bulk_density = np.exp(4.0 * warp) * (
        ricci - 0.5 * np.square(chi_u) - potential
    )
    rows = []
    maximum_relative = 0.0
    minimum_mutation_relative = float("inf")
    for lower_fraction, upper_fraction in PAIR_FRACTIONS:
        lower = int(round(lower_fraction * (u.size - 1)))
        upper = int(round(upper_fraction * (u.size - 1)))
        if upper - lower < 4:
            raise RuntimeError("action-control subinterval is too short")
        bulk = 0.5 * float(
            simpson(raw_bulk_density[lower : upper + 1], x=u[lower : upper + 1])
        )
        endpoint_B = np.exp(4.0 * warp) * superpotential
        delta = float(endpoint_B[upper] - endpoint_B[lower])
        ghy = -2.0 * delta / 3.0
        branes = delta / 2.0
        total = bulk + ghy + branes
        scale = max(abs(bulk), abs(ghy), abs(branes), 1.0e-300)
        relative = abs(total) / scale

        # Wrong upper-brane sign: lambda_+=+W instead of -W.  It must not
        # accidentally pass the cancellation test.
        mutated_branes = -0.5 * (
            endpoint_B[lower] + endpoint_B[upper]
        )
        mutated_total = bulk + ghy + mutated_branes
        mutation_relative = abs(mutated_total) / scale
        maximum_relative = max(maximum_relative, relative)
        minimum_mutation_relative = min(
            minimum_mutation_relative, mutation_relative
        )
        rows.append(
            {
                "indices": [lower, upper],
                "proper_static_separation": float(u[upper] - u[lower]),
                "Delta_exp4A_W": delta,
                "S_bulk_times_kappa5_squared": bulk,
                "S_GHY_times_kappa5_squared": ghy,
                "S_brane_times_kappa5_squared": branes,
                "S_total_times_kappa5_squared": total,
                "relative_cancellation": relative,
                "wrong_upper_brane_sign_relative_residual": mutation_relative,
            }
        )
    return {
        "method": (
            "Simpson integration of raw reconstructed R-chi_u^2/2-V, "
            "combined with independently evaluated GHY and brane endpoints"
        ),
        "rows": rows,
        "maximum_relative_cancellation": maximum_relative,
        "minimum_wrong_sign_relative_residual": minimum_mutation_relative,
    }


def _zero_mode_norm(arrays: tuple[np.ndarray, ...]) -> dict[str, Any]:
    """Check that the two analytic m2=0 bulk solutions are normalizable."""

    u, warp, warp_u, _chi, chi_u, _potential = arrays
    exp_minus_2A = np.exp(-2.0 * warp)
    J = cumulative_trapezoid(np.exp(2.0 * warp), u, initial=0.0)
    psi_1 = warp_u * exp_minus_2A
    psi_2 = 1.0 - 2.0 * warp_u * exp_minus_2A * J
    warp_uu = -np.square(chi_u) / 6.0
    D_psi_1 = warp_uu * exp_minus_2A
    D_psi_2 = -2.0 * warp_uu * exp_minus_2A * J
    modes = (psi_1, psi_2)
    D_modes = (D_psi_1, D_psi_2)
    gram = np.empty((2, 2), dtype=float)
    for row in range(2):
        for column in range(2):
            integrand = np.exp(2.0 * warp) * (
                modes[row] * modes[column]
                + 3.0
                * D_modes[row]
                * D_modes[column]
                / np.square(chi_u)
            )
            gram[row, column] = float(simpson(integrand, x=u))
    eigenvalues = np.linalg.eigvalsh(gram)
    return {
        "basis": {
            "psi_1": "A'*exp(-2A)",
            "psi_2": "1-2*A'*exp(-2A)*integral(exp(2A)du)",
            "Q_1": "chi'*exp(-2A)",
            "Q_2": "-2*chi'*exp(-2A)*integral(exp(2A)du)",
        },
        "dimensionless_Gram_I": gram.tolist(),
        "Gram_eigenvalues": eigenvalues.tolist(),
        "normalizable": bool(np.min(eigenvalues) > 0.0),
        "candidate_bulk_zero_mode_count": 2,
        "finite_endpoint_physical_mode_count_resolved": False,
        "single_interval_kinetic_metric": "G_ab=6*I_ab/kappa5^2",
    }


def build() -> dict[str, Any]:
    effective = _read(INPUTS["effective_action"])
    brane_family = _read(INPUTS["conditional_brane_family"])
    if brane_family.get("passes", {}).get("all") is not True:
        raise RuntimeError("conditional brane-family input is not certified")
    arrays = _background(effective)
    symbolic = _symbolic_reduction()
    actual = _actual_background_checks(arrays)
    action = _raw_interval_action_checks(arrays)
    zero_modes = _zero_mode_norm(arrays)
    endpoint_warp_weights = np.exp(4.0 * arrays[1][[0, -1]])

    checks = {
        "real_reconstructed_background_used": actual["samples"] == 1979,
        "synthetic_bent_geometry_not_imported": all(
            "bent_brane_geometry" not in str(path) for path in INPUTS.values()
        ),
        "symbolic_bulk_reduction_exact": symbolic[
            "bulk_density_equals_total_derivative"
        ],
        "symbolic_junctions_exact": all(
            symbolic[key]
            for key in (
                "lower_scalar_junction_zero",
                "upper_scalar_junction_zero",
                "lower_Israel_junction_zero",
                "upper_Israel_junction_zero",
            )
        ),
        "symbolic_on_shell_action_cancels": symbolic[
            "on_shell_action_cancels"
        ],
        "Hamilton_Jacobi_square_completion_exact": symbolic[
            "Hamilton_Jacobi_square_completion_exact"
        ],
        "analytic_zero_mode_bulk_basis_exact": symbolic[
            "two_zero_mode_bulk_solutions_exact"
        ],
        "actual_W_potential_identity": actual["potential_identity_max_abs"]
        < CRITERIA["potential_identity_max_abs"],
        "actual_endpoint_junctions": actual["junction_max_abs"]
        < CRITERIA["junction_max_abs"],
        "raw_actual_action_cancels_on_multiple_intervals": action[
            "maximum_relative_cancellation"
        ]
        < CRITERIA["raw_action_relative_max"],
        "wrong_brane_sign_is_detected": bool(
            action["minimum_wrong_sign_relative_residual"]
            > CRITERIA["mutation_min_relative"]
        ),
        "zero_mode_basis_has_positive_finite_norm": bool(
            min(zero_modes["Gram_eigenvalues"])
            > CRITERIA["zero_mode_gram_min_eigenvalue"]
        ),
        "no_observational_tables_read": True,
    }
    checks["all"] = all(checks.values())

    return {
        "schema": "holo.adm-bmp-tricritical-necessity.v2",
        "title": "Real-background ADM/BMP BPS-radion flatness test",
        "classification": (
            "m2_and_u4_zero_in_conditional_functional_BPS_brane_branch;"
            "bulk_alone_does_not_select_that_branch;positive_sextic_absent"
        ),
        "fixed_action": {
            "interval": (
                "S=(2*kappa5^2)^-1 int sqrt(-G)[R-(partial chi)^2/2-V]"
                "+kappa5^-2 sum_i int sqrt(-gamma)K"
                "-(2*kappa5^2)^-1 sum_i int sqrt(-gamma)lambda_i"
            ),
            "flow": "A'=-W/6; chi'=W_chi; V=W_chi^2/2-W^2/3",
            "orientations": {"lower": -1, "upper": 1},
            "functional_BPS_branes": "lambda_i(chi)=-s_i*W(chi)",
            "explicit_branes": {"lower": "lambda_-=W", "upper": "lambda_+=-W"},
        },
        "correct_collective_coordinate": {
            "relative_separation": "R(x)=integral_from_Yminus_to_Yplus N(x,u) du",
            "linear_invariant": (
                "delta R=xi_+-xi_-+integral(alpha du); relative proper "
                "separation is gauge invariant"
            ),
            "two_moduli_warning": (
                "For a general Einstein--dilaton functional-BPS interval, the "
                "two boundary scalar values can define a bi-scalar moduli "
                "space. A common coordinate translation is a diffeomorphism "
                "only when the full fields are pulled back with it; changing "
                "both physical boundary scalar values is not thereby gauge."
            ),
            "canonical_projection_gate": (
                "The two exact positive-norm bulk zero-mode candidates must be "
                "combined with the finite-endpoint junctions and any "
                "stabilization before a unique canonical tangent q is named. "
                "It is not automatically the lowest finite-gamma KK eigenvector."
            ),
        },
        "linear_ADM_BMP_dictionary": {
            "gauge_invariants": (
                "Psi=zeta-A'*beta; Phi=alpha-beta'; "
                "Delta_chi=delta_chi-chi'*beta"
            ),
            "constraints": "Phi=-2*Psi; -chi'*Delta_chi=6*(partial_u+2A')Psi",
            "unitary_reconstruction": (
                "beta=6*D(Psi)/chi'^2; zeta=Psi-W*D(Psi)/chi'^2"
            ),
            "BMP": "tilde_a_BMP=3*zeta/2",
            "boundary_role": (
                "brane bending must be retained until delta R is formed; it "
                "cannot be certified by a synthetic covariance fixture"
            ),
        },
        "symbolic_static_ADM_reduction": symbolic,
        "actual_background": actual,
        "raw_actual_interval_action": action,
        "massless_kernel": zero_modes,
        "flatness_theorem": {
            "hypothesis": (
                "lambda_i=-s_i W holds as a functional identity along the "
                "whole monotone flow, with no localized detuning"
            ),
            "endpoint_sliding": (
                "both scalar and Israel junctions hold at every point of the "
                "flow, so every allowed interbrane separation is a solution"
            ),
            "on_shell_pieces": (
                "for Delta=[exp(4A)W]_-^+: S_bulk=Delta/(6kappa5^2), "
                "S_GHY=-2Delta/(3kappa5^2), S_brane=Delta/(2kappa5^2)"
            ),
            "result": "V_eff(R)=0 identically",
            "canonical_consequence": (
                "along every regular canonical direction in the flat moduli "
                "sector, m2=V_eff''=0 and u4=V_eff''''=0"
            ),
            "stronger_consequence": "V_eff^(n)=0 for every n, including q6=0",
        },
        "localized_non_BPS_sextic_candidate": {
            "gauge_invariant_brane_pullback": (
                "After all orthogonal moduli are fixed, "
                "X_i=delta_chi_i+chi'_i*xi_i=Z_i*q+B_i*q^2+... for the retained "
                "regular canonically normalized direction q"
            ),
            "cubic_warning": (
                "Delta_i=eta_i*X_i^3/3! starts at q^3. Integrating a massive "
                "mode sourced by q^2*h generically also induces a negative "
                "order-eta_i^2 q^4 exchange term; it is not a q^6 completion."
            ),
            "clean_local_deformation": (
                "lambda_i=-s_i*W+rho_i*(chi-chi_i_star)^6/6!"
            ),
            "four_dimensional_Einstein_frame_leading_term": (
                "V_E(q)=g6*q^6+O(q^7), with "
                "g6=sum_i exp(4A_i)*rho_i*Z_i^6/(1440*kappa5^2), up to the "
                "positive background Weyl normalization"
            ),
            "endpoint_exp4A": {
                "lower": float(endpoint_warp_weights[0]),
                "upper": float(endpoint_warp_weights[1]),
            },
            "background_junctions_unchanged": True,
            "BPS_action_through_fifth_order_unchanged": True,
            "heavy_mode_backreaction_starts_in_potential_at_order_q10": True,
            "positive_g6_if_all_nonzero_rho_are_positive": True,
            "rho_i_selected_by_bulk": False,
            "full_S6_lapse_shift_bending_projection_executed": False,
            "q2Y_generated_by_pure_brane_potential": False,
            "status": (
                "valid leading-order local brane candidate, not a bulk prediction "
                "or a completed matter-coupled force derivation"
            ),
        },
        "scope_boundary": {
            "functional_BPS_branch_selected_by_bulk": False,
            "m2_u4_zero_from_bulk_alone": False,
            "unique_canonical_radion_selected": False,
            "full_BPS_moduli_dimension_resolved_from_finite_endpoints": False,
            "bulk_background_fixes": (
                "only lambda_i and lambda_i' at the two background endpoints"
            ),
            "bulk_background_does_not_fix": (
                "the functional brane potentials or their second and higher jets"
            ),
            "therefore": (
                "m2=u4=0 is necessary inside the declared functional BPS brane "
                "branch, but is not a consequence of the reconstructed bulk alone"
            ),
            "finite_gamma_family": (
                "adding gamma_i*(chi-chi_i*)^2/2 changes the brane theory, "
                "pins the endpoints and removes the flat radion"
            ),
        },
        "tricritical_gate": {
            "m2_zero": True,
            "u4_zero": True,
            "positive_q6": False,
            "conditional_positive_q6_from_sixth_order_brane_detuning": True,
            "q2Y_derived": False,
            "unique_canonical_q_selected": False,
            "physical_tricritical_mechanism_complete": False,
            "decision": (
                "The minimal BPS branch proves both requested zeros but is too "
                "flat to generate the required stabilizing sextic."
            ),
        },
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
        },
        "next_decisive_test": (
            "Either derive a microscopic principle selecting lambda_i=-s_iW "
            "plus a first nonzero stable sixth-order deformation, or accept that "
            "the present bulk supplies a flat moduli sector rather than the "
            "tricritical q^6 selector. Fix the finite-endpoint moduli metric and "
            "canonical tangent before deriving q^2Y with the matter metric and "
            "constraints."
        ),
        "evidence_boundary": (
            "This is an exact classical potential-sector result for the conditional "
            "functional BPS brane action on the real reconstructed background. It "
            "does not claim that the bulk uniquely selects those branes, that q6 is "
            "positive, or that a physical force has been derived."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "sympy": sp.__version__,
        },
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        failed = [key for key, value in result["checks"].items() if not value]
        raise SystemExit(f"real BPS-radion certificate failed: {failed}")
    _write(OUTPUT, result)
    raw = result["raw_actual_interval_action"]
    gram = result["massless_kernel"]
    print(f"[artifact] {OUTPUT}")
    print(f"[real background samples] {result['actual_background']['samples']}")
    print(
        "[raw action max relative cancellation] "
        f"{raw['maximum_relative_cancellation']:.6g}"
    )
    print(f"[zero-mode Gram eigenvalues] {gram['Gram_eigenvalues']}")
    print("[BPS branch] m2=0, u4=0, q6=0")
    print("[bulk-alone selection] False")
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
