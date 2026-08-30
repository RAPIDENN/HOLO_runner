#!/usr/bin/env python3
"""Certify the gauge-invariant route from the existing S2 carrier to S3.

This calculation maps the conventions of Bianchi, Mueck and Prisco
(hep-th/0310129) to the canonical Einstein--dilaton action used in this
repository.  It verifies pointwise that their self-adjoint active-scalar
operator is the already-certified compact trace-carrier operator.  It then
records exactly which part of the cubic calculation is available and which
compact-boundary terms still have to be derived before a physical modal
coupling can be reported.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import CubicSpline

from first_principles_audit.derive_minimal_probe_completion import (
    _fem_matrices,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "gauge_invariant_cubic_route.json"

INPUTS = {
    "effective_action": (
        REPO / "first_principles_audit/artifacts/holo_effective_action.json"
    ),
    "compact_carrier": (
        REPO / "first_principles_audit/artifacts/minimal_probe_completion.json"
    ),
    "cubic_inventory": HERE / "artifacts/bulk_cubic_vertex_inventory.json",
    "boundary_completion": (
        HERE / "artifacts/superpotential_boundary_completion.json"
    ),
    "stiff_force": HERE / "artifacts/stiff_boundary_force.json",
}

CRITERIA = {
    "canonical_speed_identity_max_relative": 1.0e-12,
    "epsilon_identity_max_relative": 1.0e-12,
    "weight_factorization_max_relative": 1.0e-12,
    "integrating_factor_log_derivative_max_relative": 1.0e-3,
    "bmp_gram_max_abs": 1.0e-12,
    "spectrum_max_relative": 1.0e-10,
    "stiff_map_strong_equation_rms_relative": 5.0e-4,
    "stiff_map_strong_equation_peak_relative": 2.5e-3,
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


def _max_relative(left: np.ndarray, right: np.ndarray) -> float:
    scale = np.maximum(np.maximum(np.abs(left), np.abs(right)), 1.0e-300)
    return float(np.max(np.abs(left - right) / scale))


def _stiff_to_bmp_mode_check(
    u: np.ndarray,
    A: np.ndarray,
    chi_u: np.ndarray,
    W_holo: np.ndarray,
    rho_bmp: np.ndarray,
    stiff: dict[str, Any],
) -> dict[str, Any]:
    """Map the Boos scalar g to BMP tilde-a and check its bulk equation.

    A common normalization 3/(8*sqrt(2*M^3)) is omitted because it cancels
    from the homogeneous equation and will be restored by the already
    certified Boos quadratic normalization at modal projection time.
    """

    masses_squared = np.asarray(
        stiff["spectrum_and_force"]["mass_squared_mu2"], dtype=float
    )
    g_modes = np.asarray(stiff["profiles"]["h_n"], dtype=float)
    if g_modes.shape != (masses_squared.size, u.size):
        raise RuntimeError("unexpected stiff-mode array shape")

    rho_log_derivative = np.gradient(np.log(rho_bmp), u, edge_order=2)
    transformed = []
    rows = []
    interior = slice(10, -10)
    for index, (mass_squared, g_mode) in enumerate(
        zip(masses_squared, g_modes)
    ):
        g_spline = CubicSpline(u, g_mode)
        g_u = g_spline(u, 1)
        tilde_a_shape = np.exp(-2.0 * A) * (
            -g_mode + W_holo * g_u / np.square(chi_u)
        )
        transformed.append(tilde_a_shape)

        tilde_spline = CubicSpline(u, tilde_a_shape)
        second = tilde_spline(u, 2)
        first = tilde_spline(u, 1)
        mass_term = mass_squared * np.exp(-2.0 * A) * tilde_a_shape
        residual = second + rho_log_derivative * first + mass_term
        scale = np.abs(second) + np.abs(rho_log_derivative * first) + np.abs(
            mass_term
        )
        rms_relative = float(
            np.sqrt(np.mean(np.square(residual[interior])))
            / max(np.sqrt(np.mean(np.square(scale[interior]))), 1.0e-300)
        )
        peak_relative = float(
            np.max(np.abs(residual[interior]))
            / max(np.max(scale[interior]), 1.0e-300)
        )
        rows.append(
            {
                "mode": index,
                "mass_squared_mu2": float(mass_squared),
                "rms_relative": rms_relative,
                "peak_relative": peak_relative,
            }
        )

    return {
        "formula_without_common_normalization": (
            "tilde_a_n=exp(-2A)*[-g_n+W_H*g_n'/chi'^2]"
        ),
        "omitted_common_normalization": "3/(8*sqrt(2*M^3))",
        "profiles": transformed,
        "mode_checks": rows,
        "maximum_rms_relative": max(row["rms_relative"] for row in rows),
        "maximum_peak_relative": max(row["peak_relative"] for row in rows),
        "interior_nodes_excluded_per_endpoint": 10,
    }


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    effective = payloads["effective_action"]
    carrier = payloads["compact_carrier"]
    inventory = payloads["cubic_inventory"]
    boundary = payloads["boundary_completion"]
    stiff = payloads["stiff_force"]

    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action input is not certified")
    if carrier.get("passes", {}).get("all") is not True:
        raise RuntimeError("compact-carrier input is not certified")
    if inventory.get("checks", {}).get("all") is not True:
        raise RuntimeError("cubic-inventory input is not certified")
    if boundary.get("passes", {}).get("all") is not True:
        raise RuntimeError("boundary-completion input is not certified")
    if stiff.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff-force input is not certified")

    u = np.asarray(effective["u"], dtype=float)
    A = np.asarray(effective["A"], dtype=float)
    A_u = np.asarray(effective["A_u"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)
    phi_u = np.asarray(effective["phi_u"], dtype=float)
    kinetic = np.asarray(effective["kinetic_K_of_phi"], dtype=float)

    carrier_u = np.asarray(carrier["profiles"]["u"], dtype=float)
    if not np.array_equal(u, carrier_u):
        raise RuntimeError("effective-action and carrier grids differ")

    # Repository convention: A'=-W_H/6, chi'=W_H,chi.
    W_holo = -6.0 * A_u
    W_holo_chi = chi_u
    A_uu = -np.square(chi_u) / 6.0
    epsilon_geometry = -A_uu / np.square(A_u)
    epsilon_superpotential = 6.0 * np.square(chi_u / W_holo)
    p_holo = np.exp(4.0 * A) * epsilon_geometry
    w_holo = np.exp(2.0 * A) * epsilon_geometry

    # BMP convention map: phi_BMP=chi/2 and W_BMP=W_H/4.  Therefore
    # W_BMP,phi/W_BMP=2 W_H,chi/W_H.
    ratio_bmp = 2.0 * W_holo_chi / W_holo
    rho_bmp = np.exp(4.0 * A) * np.square(ratio_bmp)
    mass_weight_bmp = rho_bmp * np.exp(-2.0 * A)

    canonical_speed_relative = _max_relative(
        np.square(chi_u), kinetic * np.square(phi_u)
    )
    epsilon_relative = _max_relative(
        epsilon_geometry, epsilon_superpotential
    )
    p_factor_relative = _max_relative(rho_bmp, (2.0 / 3.0) * p_holo)
    w_factor_relative = _max_relative(
        mass_weight_bmp, (2.0 / 3.0) * w_holo
    )

    # Independent finite-difference check of the BMP integrating-factor
    # identity rho'/rho = 2(W_phiphi-W_phi^2/W-4W/3), after mapping.
    W_holo_chichi = np.gradient(chi_u, u, edge_order=2) / chi_u
    d2_first_derivative_coefficient = 2.0 * (
        W_holo_chichi
        - np.square(chi_u) / W_holo
        - W_holo / 3.0
    )
    rho_log_derivative = np.gradient(np.log(rho_bmp), u, edge_order=2)
    integrating_factor_relative = _max_relative(
        d2_first_derivative_coefficient, rho_log_derivative
    )

    # The stored f_n are w_H-orthonormal.  Since w_BMP=(2/3)w_H,
    # their BMP Gram matrix must be (2/3) times the identity and the
    # generalized eigenvalues must be unchanged.
    modes = np.asarray(carrier["profiles"]["f_n"], dtype=float).T
    stiffness_bmp, mass_bmp = _fem_matrices(
        u, rho_bmp, mass_weight_bmp
    )
    gram_bmp = modes.T @ (mass_bmp @ modes)
    expected_gram = (2.0 / 3.0) * np.eye(modes.shape[1])
    gram_max_abs = float(np.max(np.abs(gram_bmp - expected_gram)))

    stored_mass_squared = np.asarray(
        carrier["dimensionless_spectrum"]["mass_squared"], dtype=float
    )
    rayleigh = np.asarray(
        [
            float(mode @ (stiffness_bmp @ mode))
            / float(mode @ (mass_bmp @ mode))
            for mode in modes.T
        ]
    )
    spectrum_relative = _max_relative(
        rayleigh[1:], stored_mass_squared[1:]
    )
    stiff_map = _stiff_to_bmp_mode_check(
        u, A, chi_u, W_holo, rho_bmp, stiff
    )

    checks = {
        "certified_inputs": True,
        "no_observational_tables_read": True,
        "canonical_speed_identity": (
            canonical_speed_relative
            <= CRITERIA["canonical_speed_identity_max_relative"]
        ),
        "epsilon_superpotential_identity": (
            epsilon_relative <= CRITERIA["epsilon_identity_max_relative"]
        ),
        "bmp_stiffness_weight_equals_two_thirds_p": (
            p_factor_relative
            <= CRITERIA["weight_factorization_max_relative"]
        ),
        "bmp_mass_weight_equals_two_thirds_w": (
            w_factor_relative
            <= CRITERIA["weight_factorization_max_relative"]
        ),
        "bmp_integrating_factor_identity": (
            integrating_factor_relative
            <= CRITERIA[
                "integrating_factor_log_derivative_max_relative"
            ]
        ),
        "stored_modes_have_bmp_gram_two_thirds_identity": (
            gram_max_abs <= CRITERIA["bmp_gram_max_abs"]
        ),
        "stored_spectrum_is_unchanged": (
            spectrum_relative <= CRITERIA["spectrum_max_relative"]
        ),
        "stiff_modes_map_to_bmp_bulk_equation": (
            stiff_map["maximum_rms_relative"]
            <= CRITERIA["stiff_map_strong_equation_rms_relative"]
            and stiff_map["maximum_peak_relative"]
            <= CRITERIA["stiff_map_strong_equation_peak_relative"]
        ),
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "same_local_S2_operator_identified": checks["all"],
        "bmp_linear_comoving_identity_identified": True,
        "repository_trace_to_bmp_absolute_normalization_identified": False,
        "linear_stiff_to_gauge_invariant_mode_map_identified": True,
        "stiff_mode_map_strong_equation_verified": checks[
            "stiff_modes_map_to_bmp_bulk_equation"
        ],
        "bmp_holographic_three_point_kernel_identified": True,
        "compact_bulk_S3_action_derived": False,
        "compact_endpoint_terms_derived": False,
        "compact_GHY_or_junction_cubic_completion_derived": False,
        "field_redefinition_boundary_cancellation_verified": False,
        "physical_compact_modal_couplings_computed": False,
        "direct_S4_contact_derived": False,
    }
    physical_gates["physical_S3_complete"] = all(
        (
            physical_gates["same_local_S2_operator_identified"],
            physical_gates["bmp_linear_comoving_identity_identified"],
            physical_gates[
                "repository_trace_to_bmp_absolute_normalization_identified"
            ],
            physical_gates[
                "linear_stiff_to_gauge_invariant_mode_map_identified"
            ],
            physical_gates["stiff_mode_map_strong_equation_verified"],
            physical_gates["bmp_holographic_three_point_kernel_identified"],
            physical_gates["compact_bulk_S3_action_derived"],
            physical_gates["compact_endpoint_terms_derived"],
            physical_gates[
                "compact_GHY_or_junction_cubic_completion_derived"
            ],
            physical_gates[
                "field_redefinition_boundary_cancellation_verified"
            ],
            physical_gates["physical_compact_modal_couplings_computed"],
        )
    )

    return {
        "schema": "holo.gauge-invariant-cubic-route.v1",
        "title": "Gauge-invariant S2-to-S3 route for the HOLO scalar carrier",
        "classification": (
            "exact_local_operator_match_and_primary_S3_kernel_identified;"
            "compact_boundary_completion_pending"
        ),
        "primary_derivation": {
            "authors": "Massimo Bianchi, Wolfgang Mueck, Maurizio Prisco",
            "title": "New Results on Holographic Three-Point Functions",
            "arxiv": "hep-th/0310129v3",
            "doi": "10.1088/1126-6708/2003/11/052",
            "url": "https://arxiv.org/abs/hep-th/0310129",
            "used_equations": {
                "background": "Eq. (2.5)",
                "gauge_invariants": "Eqs. (3.9)-(3.13)",
                "constraint_solution": "Eq. (4.6)",
                "active_scalar_equation": "Eqs. (4.7)-(4.9)",
                "bose_symmetric_cubic_kernel": "Eq. (5.19)",
                "integrating_factor_identity": "Eq. (5.18)",
            },
            "scope": (
                "Einstein equations through second perturbative order, "
                "which determine the tree-level active-scalar three-point "
                "vertex. The paper does not derive the direct quartic S4 "
                "contact required here."
            ),
        },
        "convention_map": {
            "repository_action": (
                "S5=(2*kappa5^2)^(-1) integral sqrt(-G) "
                "[R-(partial chi)^2/2-V_H(chi)]"
            ),
            "field": "phi_BMP=chi/2",
            "superpotential": "W_BMP=W_H/4",
            "potential": "V_BMP=V_H/4",
            "repository_background": (
                "chi'=W_H,chi; A'=-W_H/6; "
                "V_H=W_H,chi^2/2-W_H^2/3"
            ),
            "bmp_ratio": "W_BMP,phi/W_BMP=2*W_H,chi/W_H",
            "bmp_D2_in_repository_variables": (
                "D2=[d_u+2*(W_H,chichi-W_H,chi^2/W_H-W_H/3)]d_u"
            ),
        },
        "quadratic_operator_match": {
            "samples": int(u.size),
            "domain": [float(u[0]), float(u[-1])],
            "repository_equation": "-(p*f')'=mu^2*w*f",
            "bmp_self_adjoint_equation": (
                "-(rho_BMP*f')'=mu^2*rho_BMP*exp(-2A)*f"
            ),
            "exact_weight_relations": {
                "rho_BMP": "(2/3)*p",
                "rho_BMP_exp_minus_2A": "(2/3)*w",
            },
            "metrics": {
                "canonical_speed_identity_max_relative": (
                    canonical_speed_relative
                ),
                "epsilon_identity_max_relative": epsilon_relative,
                "stiffness_weight_factorization_max_relative": (
                    p_factor_relative
                ),
                "mass_weight_factorization_max_relative": w_factor_relative,
                "integrating_factor_log_derivative_max_relative": (
                    integrating_factor_relative
                ),
                "bmp_gram_minus_two_thirds_identity_max_abs": gram_max_abs,
                "rayleigh_spectrum_max_relative": spectrum_relative,
            },
            "mode_count": int(modes.shape[1]),
            "mass_squared": stored_mass_squared.tolist(),
        },
        "linear_mode_map": {
            "bmp_invariant": "tilde_a=(W_BMP/W_BMP,phi)*a",
            "bmp_a": "a=varphi+W_BMP,phi*h/(4*W_BMP)+O(fields^2)",
            "comoving_gauge": (
                "varphi=0 implies tilde_a=h_BMP/4 at linear order"
            ),
            "repository_trace": (
                "delta_g_mu_nu=(h_R/4)*gbar_mu_nu and "
                "h_R(x,u)=sum_n q_n(x) f_n(u)"
            ),
            "normalization_distinction": (
                "BMP decomposes h^i_j with delta^i_j*h_BMP/3 in d=4, "
                "whereas the repository benchmark labels the isotropic "
                "relative trace h_R. For the isotropic representative, "
                "H_BMP=0, h_BMP=3*h_R/4 and tilde_a=3*h_R/16, not "
                "h_R/4. The constant leaves the local operator and spectrum "
                "unchanged but must be restored before absolute couplings."
            ),
            "consequence": (
                "The certified Neumann f_n are a direct control of the local "
                "BMP operator, but they belong to the earlier conditional "
                "trace benchmark, are not the microscopic stabilized "
                "two-brane modes, and do not yet supply BMP's absolute "
                "normalization."
            ),
            "stiff_branch": {
                "boos_variable": (
                    "g=exp(2A)*h_44 in the repository warp convention"
                ),
                "derivation": (
                    "Use the Boos gauge relations h_mu_nu=-eta_mu_nu*g/2 "
                    "and delta_chi=3*exp(-2A)*g'/(2*sqrt(2*M^3)*chi'), "
                    "then insert them into the BMP invariant tilde_a."
                ),
                "map": stiff_map["formula_without_common_normalization"],
                "common_normalization": stiff_map[
                    "omitted_common_normalization"
                ],
                "strong_equation_check": {
                    "maximum_rms_relative": stiff_map[
                        "maximum_rms_relative"
                    ],
                    "maximum_peak_relative": stiff_map[
                        "maximum_peak_relative"
                    ],
                    "mode_checks": stiff_map["mode_checks"],
                },
                "consequence": (
                    "The seven stiff g_n profiles are not inserted raw. After "
                    "this first-principles linear transform they are valid "
                    "external tilde-a profiles for the BMP bulk S3 source."
                ),
            },
        },
        "cubic_calculation": {
            "available_bulk_result": (
                "BMP Eq. (5.19) gives an explicitly Bose-symmetric radial "
                "holographic three-point kernel X_123 built from W, A, "
                "external momenta and radial derivatives of three linear "
                "profiles. It is an independent bulk EOM/correlator oracle, "
                "not by itself the compact cubic action."
            ),
            "why_it_is_not_yet_a_physical_compact_coupling": (
                "Eq. (5.19) follows after a field redefinition and radial "
                "integration by parts. BMP verify cancellation of the induced "
                "boundary pieces for holographic GPPZ asymptotics. This "
                "repository instead selected two finite Neumann endpoints, "
                "so its GHY/junction and field-redefinition endpoint terms "
                "must be derived and combined before reporting c_abc."
            ),
            "correct_execution_order": [
                "evaluate the unreduced quadratic source J_tilde_a using BMP Eqs. (4.6)-(4.9) on the certified f_n",
                "use the transformed stiff tilde-a_n profiles, not raw g_n or the conditional Neumann f_n, for the physical stiff candidate",
                "derive the finite-endpoint cubic GHY or junction completion selected by the stiff compact branch",
                "verify the endpoint cancellation associated with the BMP field redefinition and integration by parts",
                "recover the certified S2 normalization in the same variables",
                "project the complete bulk-plus-boundary source to obtain c_abc with nested mode and grid convergence",
                "derive S4 independently before assigning the sign of the total Y^2 coefficient",
            ],
            "direct_S4_requirement": (
                "C_Y2_total=C_Y2_direct_S4-0.5*c^T*M^(-2)*c; "
                "the primary S3 derivation fixes only the exchange term."
            ),
            "boundary_identifiability": (
                "The background fixes each brane potential and its first "
                "derivative; S2 fixes or selects a second-derivative branch. "
                "A cubic deformation eta_i*(chi-chi_i)^3/6 leaves all those "
                "data unchanged but alters finite-gamma S3. Setting eta_i=0 "
                "or taking a controlled stiff limit is an additional "
                "microscopic choice, not information encoded by the bulk "
                "background."
            ),
        },
        "silicon_execution_contract": {
            "role_of_i5": (
                "Run the already-defined deterministic grid and modal "
                "projection with bounded arrays and independent residuals."
            ),
            "not_a_derivation": (
                "Neither i5 geometry nor a runner label supplies missing "
                "boundary terms, a gauge map, or S4."
            ),
            "launch_gate": (
                "Do not launch hardware runners until the local bulk-plus-"
                "boundary reference calculation passes and its exact input "
                "hashes are frozen."
            ),
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
        },
        "evidence_boundary": (
            "This certificate establishes an exact local S2 operator match "
            "and identifies a primary gauge-invariant holographic three-point "
            "kernel. It is not a compact S3 action, a computed compact cubic "
            "coupling, a quartic completion, a force law, or observational "
            "evidence for a new interaction."
        ),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    metrics = result["quadratic_operator_match"]["metrics"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[S2 operator match] max weight relative error "
        f"{max(metrics['stiffness_weight_factorization_max_relative'], metrics['mass_weight_factorization_max_relative']):.3e}"
    )
    print(
        "[physical compact S3 complete] "
        f"{result['physical_gates']['physical_S3_complete']}"
    )
    print(f"[certificate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
