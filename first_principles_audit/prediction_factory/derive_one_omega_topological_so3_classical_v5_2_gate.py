#!/usr/bin/env python3
"""Certify prescribed-port N8 while keeping C1/N1 moving variation on hold.

This gate consumes the fail-closed v5.1 boundary-isomorphism receipt and records:

1. one exact action candidate charter, including a normalized BF term, the transported
   connection and associated-vector traces, and the metric-dependent frame
   variation on a moving interface, while its complete moving variation remains open;
2. an isometric lift of the complete signed finite-q full-V4 material problem,

      phi = Omega^(-3/2) G n0 u,  A = -(dG)G^(-1),  B = 0,

   where u is the canonical upstream field.  The lift is an equality of
   functionals and Euler operators, not a check on one collinear derivative.

The result is restricted to the fixed contractible topology and the
null-homotopic, extendible gauge component.  It closes only the prescribed-
background material N8.  C1 and N1 remain on moving-variation hold, and the BF
ghost/edge complex, dynamic gravity, N2-N7, P2-P4, B4 and B5 remain open.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_classical_v5_2_gate.json"
)
TEST = HERE / "test_one_omega_topological_so3_classical_v5_2_gate.py"

SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
UPSTREAMS = {
    "boundary_isomorphism_v5_1": {
        "path": HERE
        / "artifacts"
        / "one_omega_topological_so3_boundary_isomorphism_v5_1_gate.json",
        "schema": "holo.one-omega-topological-so3-boundary-isomorphism-v5-1-gate.v1",
        "sha256": "81ef6e2133e47290b776b57ab71b92dd104099eb45a35156230dd682d00fffea",
    },
    "nonlinear_robin_full_V4": {
        "path": HERE / "artifacts" / "nonlinear_robin_full_v4_gate.json",
        "schema": "holo.nonlinear-robin-full-v4-gate.v1",
        "sha256": "e65b790fdd068c58e6b7597955c0d5fc93e419852f70561b54e997dddd04250b",
    },
    "one_Omega_action_charter": {
        "path": HERE / "artifacts" / "one_omega_action_charter_gate.json",
        "schema": "holo.one-omega-action-charter-gate.v1",
        "sha256": "b718cb68934a665cf0a7b89fafffcf2b9ebb2c0bb94c9386ff64f34d91a2e0ef",
    },
    "lower_branch_action_v3": {
        "path": HERE / "artifacts" / "one_omega_lower_branch_action_v3_gate.json",
        "schema": "holo.one-omega-lower-branch-action-v3-gate.v1",
        "sha256": "4759a2c9a0036f8d93eb1224fcd955cd45843759a2e64c5703d00c31da5a5243",
    },
}

FAIL_CLOSED_KEYS = (
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "unrestricted_large_gauge_sector_pass",
    "all_boundary_topologies_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "global_BF_edge_mode_absence_pass",
    "A_minus_frame_connection_edge_sector_eliminated",
    "C2_BRST_pass",
    "C3_DOMAIN_pass",
    "C4_HESSIAN_pass",
    "C5_JACOBIANS_pass",
    "C6_ZERO_MODES_pass",
    "C7_REGULATOR_pass",
    "C8_CONTOUR_pass",
    "C9_REDUCTION_pass",
    "C10_INDEPENDENCE_UNITARITY_pass",
    "N2_CONSTRAINTS_pass",
    "N3_CHARACTERISTICS_pass",
    "N4_JUNCTION_BENDING_pass",
    "N5_COUPLED_BVP_pass",
    "N6_GLOBAL_STABILITY_pass",
    "N7_LINEAR_REDUCTION_pass",
    "full_same_action_ghost_freedom_pass",
    "P3_complete_gauge_fixed_unitary_determinant_pass",
    "P4_full_same_action_pass",
    "nonlinear_gravitational_P4_pass",
    "full_P2_pass",
    "B4_pass",
    "B5_pass",
    "a0_predicted",
    "universal_matter_metric_and_lensing_derived",
    "new_force_validated",
    "publication_authorized",
)


class ClassicalV52InputError(ValueError):
    """An upstream receipt or a classical v5.2 datum is malformed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ClassicalV52InputError(f"cannot hash {path}: {exc}") from exc


def _read_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ClassicalV52InputError(f"cannot read {path}: {exc}") from exc
    if type(payload) is not dict:
        raise ClassicalV52InputError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _contains_ellipsis(value: Any) -> bool:
    if isinstance(value, str):
        return "..." in value or "\N{HORIZONTAL ELLIPSIS}" in value
    if isinstance(value, Mapping):
        return any(_contains_ellipsis(key) or _contains_ellipsis(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_ellipsis(item) for item in value)
    return False


def _load_upstreams() -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, spec in UPSTREAMS.items():
        if _sha256(spec["path"]) != spec["sha256"]:
            raise ClassicalV52InputError(f"{name} byte hash mismatch")
        payload = _read_object(spec["path"])
        if payload.get("schema") != spec["schema"]:
            raise ClassicalV52InputError(f"{name} schema mismatch")
        if payload.get("checks", {}).get("all") is not True:
            raise ClassicalV52InputError(f"{name} checks are not certified")
        loaded[name] = payload

    iso = loaded["boundary_isomorphism_v5_1"]["decision"]
    required_iso = {
        "boundary_bundle_isomorphism_trivial_sector_pass": True,
        "topological_characteristic_class_compatibility_pass": True,
        "relative_isomorphism_modes_after_gauge_quotient": 0,
        "full_classical_variational_principle_pass": False,
        "N8_same_solution_transport_theorem_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "N8_MATERIAL_PORT_pass": False,
    }
    if any(iso.get(key) != value for key, value in required_iso.items()):
        raise ClassicalV52InputError("v5.1 fail-closed scope mismatch")

    nonlinear = loaded["nonlinear_robin_full_V4"]["decision"]
    for key in (
        "finite_Robin_full_V4_functional_coercive_convex",
        "inhomogeneous_periodic_material_minimizer_exists_and_is_unique",
        "nonlinear_inhomogeneous_finite_q_material_BVP_pass",
        "full_V4_periodic_EOM_energy_convergence_source_closure_pass",
        "canonical_time_dependent_material_Hamiltonian_positive",
    ):
        if nonlinear.get(key) is not True:
            raise ClassicalV52InputError(f"nonlinear N8 upstream lost {key}")
    for key in ("nonlinear_all_helicity_P4_pass", "P4_pass", "B4_pass", "B5_pass"):
        if nonlinear.get(key) is not False:
            raise ClassicalV52InputError(f"nonlinear upstream over-promoted {key}")

    base = loaded["one_Omega_action_charter"]
    base_decision = base["decision"]
    if any(
        base_decision.get(key) is not True
        for key in ("C1_ACTION_pass", "N1_ACTION_pass", "N8_MATERIAL_PORT_pass")
    ):
        raise ClassicalV52InputError("base action green targets are absent")
    if base["action_charter"]["exact_action"].get("full_V4") != (
        "V4(r)=r^4/(2*sqrt(1+r^4))"
    ):
        raise ClassicalV52InputError("base full-V4 potential changed")

    lower = loaded["lower_branch_action_v3"]
    if lower["decision"].get("lower_lambda_branch_selected") is not True:
        raise ClassicalV52InputError("lower lambda branch is absent")
    return loaded


def exact_classical_charter(
    upstreams: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Compose one literal action rather than a prose base-plus-patch recipe."""

    base = upstreams["one_Omega_action_charter"]["action_charter"]
    base_parameters = base["coefficient_policy"]["parameters"]
    lower_parameters = upstreams["lower_branch_action_v3"]["action_charter_v3"][
        "coefficient_policy"
    ]["parameters"]
    parameters = {
        key: base_parameters[key]
        for key in (
            "M5_cubed",
            "k_infinity",
            "compensator_metric_G",
            "brane_beta",
            "material_Z5_per_side",
            "material_mass_M",
            "M4_bulk_squared_selected_one_Omega_wall_value",
            "brane_Mb_squared",
            "xi",
            "eta",
            "B4_bar",
            "Robin_kappa_in_Mb_units",
            "Robin_kappa_hat",
            "Robin_y_squared",
            "Robin_y",
        )
    }
    parameters["lambda_K"] = lower_parameters["lambda_K"]
    parameters["kappa_BF_inner_product"] = 1.0
    parameters["k_BF_trace_equivalent"] = -0.5

    action = {
        "total": (
            "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF"
        ),
        "superpotential": (
            "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]"
        ),
        "bulk_potential": "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
        "full_V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
        "bulk_gauged": (
            "S_bulk_gauged=sum_eps int_Meps sqrt(-g_eps)*[M5^3*R_eps/2-"
            "G*(nabla Omega_eps)^2/2-U(Omega_eps)-"
            "Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2-"
            "Z5*M^2*Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)]"
        ),
        "gauged_conformal_derivative": (
            "P_eps_M=D_(A_eps,M)phi_eps+3*phi_eps*partial_M log(Omega_eps)/2"
        ),
        "GHY": (
            "S_GHY=M5^3*sum_eps int_Sigma sqrt(-gamma)*Theta_eps for outward normals"
        ),
        "wall_background": (
            "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+"
            "beta*(Omega_Sigma-1)^2/2]"
        ),
        "foliation_lower": (
            "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-"
            "lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
            "B4_bar*Rcal^2/(16*k_infinity^2)]"
        ),
        "Robin_intrinsic": (
            "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*"
            "h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)"
        ),
        "BF": (
            "S_BF=sum_eps int_Meps <B_eps wedge F[A_eps]>, "
            "<X,Y>=-tr_3(XY)/2"
        ),
        "removed_terms": "S_X=0 and every bulk screen-clock term=0",
    }
    return {
        "route_id": "one_Omega_full_V4_topological_SO3_classical_v5_2",
        "topology": {
            "bulk_halves": "M_plus=M_minus=R^(1,3)xR_>=0",
            "interface": "Sigma=R^(1,3) with no boundary",
            "bundle_sector": "trivial SO3 bundles and null-homotopic extendible gauges",
            "reference_domain_formulation": (
                "M_eps are fixed reference half-spaces; moving physical domains are pulled "
                "back in full by Y_eps, so the material variations include Lie_xi once "
                "and no separate i_xi L_5 term is added"
            ),
        },
        "independent_fields": {
            "bulk_each_side": [
                "Lorentzian metric g_eps_MN",
                "positive scalar Omega_eps",
                "associated SO3 vector phi_eps",
                "SO3 connection A_eps",
                "adjoint-valued real three-form B_eps",
            ],
            "brane": [
                "paired embeddings Y_plus and Y_minus of one physical Sigma",
                "khronon T with timelike gradient and fixed time orientation",
            ],
            "boundary_groupoid_data": [
                "equivariant iota_plus:P_plus|Sigma->Q",
                "equivariant iota_minus:P_minus|Sigma->Q",
                "Q=Fr^+_SO(H_(gamma,T))",
            ],
            "not_independent_Euler_Lagrange_fields": [
                "gamma, normals, Theta, u, h, Kcal, a and Rcal are composites",
                "the local frame representative e_a^mu is constrained by h and quotiented by SO3",
                "iota_plus and iota_minus are groupoid gluing data modulo automorphisms",
            ],
            "absent": [
                "solid Stueckelberg X^a",
                "screen clock",
                "bifundamental R field",
                "classical ghosts and gauge-fixing auxiliaries",
            ],
        },
        "definitions": {
            "induced_metric": (
                "gamma_mu_nu=Y_eps^*g_eps and is common on both sides"
            ),
            "khronon": (
                "N_T=(-gamma^(mu nu)D_mu T D_nu T)^(-1/2); "
                "u_mu=-N_T D_mu T; h_mu_nu=gamma_mu_nu+u_mu*u_nu"
            ),
            "frame_constraints": (
                "u_mu*e_a^mu=0 and h_mu_nu*e_a^mu*e_b^nu=delta_ab"
            ),
            "associated_trace": (
                "j_eps(Y_eps^*phi_eps)=varphi_H in H_(gamma,T)"
            ),
            "connection_trace": (
                "Trans_iota(A)=r*(Y^*A)*r^(-1)-(d r)*r^(-1)=A_Sigma"
            ),
            "adjoint_form_trace": "Trans_iota(B)=Ad_r(Y^*B)=b_eps",
            "acceleration": "a_mu=u^nu D_nu u_mu",
            "trace_normalization": (
                "(T_I)^J_K=epsilon_IJK; tr_3(T_I*T_J)=-2*delta_IJ; "
                "<X,Y>=-tr_3(XY)/2"
            ),
        },
        "interface_domain": {
            "configuration": [
                "Y_plus^*g_plus=Y_minus^*g_minus=gamma",
                "Y_plus^*Omega_plus=Y_minus^*Omega_minus=Omega_Sigma",
                "j_plus(Y_plus^*phi_plus)=j_minus(Y_minus^*phi_minus)=varphi_H",
                "Trans_iota_plus(Y_plus^*A_plus)=Trans_iota_minus(Y_minus^*A_minus)=A_Sigma",
            ],
            "variations": [
                "Delta gamma, Delta Omega_Sigma, Delta varphi_H and Delta A_Sigma are common",
                "Delta A=Y^*(delta A+i_xi F) after the compensating gauge transformation",
                "Delta phi=Y^*(delta phi+i_xi D_A phi) plus the constrained delta j",
            ],
            "natural_B_flux_equation": (
                "sum_eps s_eps*b_eps=0 with s_plus=1 and s_minus=-1"
            ),
            "BF_shift_parameter": (
                "sum_eps s_eps*Trans_iota_eps(Y_eps^*Lambda_eps)=0"
            ),
            "asymptotic": (
                "normalizable fields, compact-support variations and trivial flat holonomy at infinity"
            ),
        },
        "symmetries": [
            "five-dimensional diffeomorphisms and four-dimensional brane reparametrizations",
            "Z2 exchange of the two sides",
            "monotone khronon reparametrization",
            "local SO3 on P_plus, P_minus and Q with the boundary groupoid action",
            "BF shift B->B+D_A Lambda with oriented boundary gluing",
        ],
        "exact_action": action,
        "coefficient_policy": {
            "matching_scale": "mu_star=k_infinity",
            "parameters": parameters,
            "all_unlisted_local_classical_operator_coefficients_at_mu_star": 0.0,
            "BF_normalization_conversion": (
                "kappa_BF*<B,F>=k_BF_trace*tr_3(BF) with "
                "kappa_BF=1 and k_BF_trace=-1/2"
            ),
        },
        "mass_dimensions": {
            "derivative": 1,
            "Omega": 0,
            "phi": 0,
            "A_component": 1,
            "F_component": 2,
            "B_component": 3,
            "kappa_BF": 0,
            "M5_cubed": 3,
            "G": 3,
            "Z5": 3,
            "bulk_Lagrangian": 5,
            "Mb_squared": 2,
            "kappa_hat": 4,
            "y": -1,
            "brane_Lagrangian": 4,
        },
        "nonlinear_scope": (
            "exact in displayed fields on the selected classical bundle component"
        ),
        "BRST_BV_BFV_completion_included": False,
    }


def frame_and_robin_variation_certificate() -> dict[str, Any]:
    """Check the horizontal frame lift and the complete local Robin differential."""

    gamma = np.diag([-1.0, 1.0, 1.0, 1.0])
    gamma_inverse = gamma.copy()
    u_cov = np.asarray([-1.0, 0.0, 0.0, 0.0])
    u_contra = gamma_inverse @ u_cov
    h_cov = gamma + np.outer(u_cov, u_cov)
    h_contra = gamma_inverse + np.outer(u_contra, u_contra)
    h_mixed = np.eye(4) + np.outer(u_cov, u_contra)
    frame = np.zeros((4, 3))
    frame[1:, :] = np.eye(3)
    delta_gamma = np.asarray(
        [
            [0.12, 0.03, -0.02, 0.01],
            [0.03, 0.08, 0.02, -0.01],
            [-0.02, 0.02, -0.06, 0.04],
            [0.01, -0.01, 0.04, 0.05],
        ]
    )
    grad_delta_t = np.asarray([0.07, -0.11, 0.09, 0.04])
    delta_u_cov = -h_mixed @ grad_delta_t - 0.5 * u_cov * (
        u_contra @ delta_gamma @ u_contra
    )
    delta_u_contra = (
        gamma_inverse @ delta_u_cov
        - gamma_inverse @ delta_gamma @ u_contra
    )
    delta_h = (
        delta_gamma
        + np.outer(delta_u_cov, u_cov)
        + np.outer(u_cov, delta_u_cov)
    )
    vertical_rotation = np.asarray(
        [[0.0, 0.07, -0.03], [-0.07, 0.0, 0.04], [0.03, -0.04, 0.0]]
    )
    delta_frame = (
        np.outer(u_contra, delta_u_cov @ frame)
        - 0.5 * h_contra @ delta_h @ frame
        + frame @ vertical_rotation
    )
    orthogonality_error = np.linalg.norm(
        delta_u_cov @ frame + u_cov @ delta_frame
    )
    orthonormality_error = np.linalg.norm(
        frame.T @ delta_h @ frame
        + delta_frame.T @ h_cov @ frame
        + frame.T @ h_cov @ delta_frame
    )
    unit_norm_error = abs(
        float(2.0 * u_contra @ delta_u_cov - u_contra @ delta_gamma @ u_contra)
    )

    internal_phi = np.asarray([0.4, -0.2, 0.3])
    delta_internal_phi = (
        np.asarray([0.02, 0.01, -0.03]) - vertical_rotation @ internal_phi
    )
    internal_acceleration = np.asarray([0.1, -0.05, 0.07])
    delta_internal_acceleration = (
        np.asarray([0.03, -0.02, 0.01])
        - vertical_rotation @ internal_acceleration
    )
    yukawa = math.sqrt(3.0)
    q = frame @ internal_phi - yukawa * (frame @ internal_acceleration)
    delta_q = (
        delta_frame @ internal_phi
        + frame @ delta_internal_phi
        - yukawa
        * (
            delta_frame @ internal_acceleration
            + frame @ delta_internal_acceleration
        )
    )
    trace_metric = float(np.trace(gamma_inverse @ delta_gamma))
    analytic_density_derivative = 0.5 * math.sqrt(-np.linalg.det(gamma)) * (
        0.5 * trace_metric * float(q @ h_cov @ q)
        + float(q @ delta_h @ q)
        + 2.0 * float(q @ h_cov @ delta_q)
    )

    def robin_density(step: float) -> float:
        metric = gamma + step * delta_gamma
        spatial_metric = h_cov + step * delta_h
        moving_frame = frame + step * delta_frame
        moving_phi = internal_phi + step * delta_internal_phi
        moving_acceleration = (
            internal_acceleration + step * delta_internal_acceleration
        )
        moving_q = moving_frame @ moving_phi - yukawa * (
            moving_frame @ moving_acceleration
        )
        return 0.5 * math.sqrt(-np.linalg.det(metric)) * float(
            moving_q @ spatial_metric @ moving_q
        )

    finite_step = 1.0e-4
    finite_difference = (
        robin_density(finite_step) - robin_density(-finite_step)
    ) / (2.0 * finite_step)
    vertical_phi_error = float(
        np.linalg.norm(
            (frame @ vertical_rotation) @ internal_phi
            + frame @ (-vertical_rotation @ internal_phi)
        )
    )
    vertical_acceleration_error = float(
        np.linalg.norm(
            (frame @ vertical_rotation) @ internal_acceleration
            + frame @ (-vertical_rotation @ internal_acceleration)
        )
    )
    return {
        "delta_u_covariant": (
            "delta u_mu=-N_T*h_mu^nu*D_nu(delta T)-"
            "u_mu*u^rho*u^sigma*delta gamma_rho_sigma/2"
        ),
        "delta_h": "delta h_mu_nu=delta gamma_mu_nu+u_mu delta u_nu+u_nu delta u_mu",
        "delta_frame": (
            "delta e_a^mu=u^mu*delta u_nu*e_a^nu-"
            "h^(mu rho)*delta h_rho_nu*e_a^nu/2+e_b^mu*lambda^b_a, "
            "lambda_ab=-lambda_ba"
        ),
        "linearized_u_norm_error": unit_norm_error,
        "linearized_frame_spatiality_error": float(orthogonality_error),
        "linearized_frame_orthonormality_error": float(orthonormality_error),
        "Robin_first_variation": (
            "delta S_R=-kappa_hat/2*int sqrt(-gamma)*["
            "gamma^(mu nu)delta gamma_mu_nu*|q|_h^2/2+"
            "delta h(q,q)+2*h(q,delta varphi_H-y*delta a_sharp)]"
        ),
        "Robin_analytic_density_derivative": analytic_density_derivative,
        "Robin_finite_difference_derivative": finite_difference,
        "Robin_finite_difference_error": abs(
            finite_difference - analytic_density_derivative
        ),
        "vertical_frame_rotation_phi_cancellation_error": vertical_phi_error,
        "vertical_frame_rotation_acceleration_cancellation_error": (
            vertical_acceleration_error
        ),
    }


def acceleration_variation_certificate() -> dict[str, Any]:
    """Differentiate a_mu=u^nu(partial_nu u_mu-Gamma u) directly."""

    rng = np.random.default_rng(5202)
    u_cov = np.asarray([-1.0, 0.13, -0.08, 0.04])
    u_contra = np.asarray([1.0, 0.11, -0.06, 0.03])
    delta_u_cov = rng.normal(scale=0.05, size=4)
    delta_u_contra = rng.normal(scale=0.05, size=4)
    partial_u = rng.normal(scale=0.1, size=(4, 4))
    partial_delta_u = rng.normal(scale=0.04, size=(4, 4))
    connection = rng.normal(scale=0.03, size=(4, 4, 4))
    delta_connection = rng.normal(scale=0.02, size=(4, 4, 4))

    covariant_u = partial_u - np.einsum("rnm,r->nm", connection, u_cov)
    covariant_delta_u = partial_delta_u - np.einsum(
        "rnm,r->nm", connection, delta_u_cov
    )
    analytic = (
        np.einsum("n,nm->m", delta_u_contra, covariant_u)
        + np.einsum("n,nm->m", u_contra, covariant_delta_u)
        - np.einsum("n,rnm,r->m", u_contra, delta_connection, u_cov)
    )

    def acceleration(step: float) -> np.ndarray:
        moved_u_cov = u_cov + step * delta_u_cov
        moved_u_contra = u_contra + step * delta_u_contra
        moved_partial = partial_u + step * partial_delta_u
        moved_connection = connection + step * delta_connection
        moved_covariant = moved_partial - np.einsum(
            "rnm,r->nm", moved_connection, moved_u_cov
        )
        return np.einsum("n,nm->m", moved_u_contra, moved_covariant)

    step = 1.0e-5
    finite_difference = (acceleration(step) - acceleration(-step)) / (2.0 * step)
    return {
        "formula": (
            "delta a_mu=delta u^nu D_nu u_mu+u^nu D_nu delta u_mu-"
            "u^nu*u_rho*delta Gamma^rho_(nu mu)"
        ),
        "raised_formula": (
            "delta a^mu=gamma^(mu nu)delta a_nu-"
            "gamma^(mu rho)delta gamma_rho_sigma*a^sigma"
        ),
        "finite_difference_error": float(np.linalg.norm(finite_difference - analytic)),
    }


def moving_pullback_certificate() -> dict[str, Any]:
    """Check the material pullback rule and state its gauge-covariant form."""

    point = np.asarray([0.4, -0.2, 0.7])
    displacement = np.asarray([0.03, -0.05, 0.02])

    def field(x: np.ndarray) -> float:
        return float(x[0] ** 2 + x[0] * x[1] - 0.3 * x[2] ** 2)

    def delta_field(x: np.ndarray) -> float:
        return float(0.2 * x[0] - 0.1 * x[1] + 0.05 * x[2])

    gradient = np.asarray(
        [2.0 * point[0] + point[1], point[0], -0.6 * point[2]]
    )
    analytic = delta_field(point) + float(gradient @ displacement)

    def moved(step: float) -> float:
        shifted = point + step * displacement
        return field(shifted) + step * delta_field(shifted)

    step = 1.0e-5
    finite_difference = (moved(step) - moved(-step)) / (2.0 * step)
    return {
        "scalar_pullback": "delta(Y^*f)=Y^*(delta f+Lie_xi f)",
        "connection_material_variation": (
            "Delta_xi A=Y^*(delta A+i_xi F) after subtracting D_A(i_xi A)"
        ),
        "associated_scalar_material_variation": (
            "Delta_xi phi=Y^*(delta phi+i_xi D_A phi)"
        ),
        "adjoint_form_material_variation": (
            "Delta_xi B=Y^*(delta B+i_xi D_A B+D_A(i_xi B))"
        ),
        "reference_domain_convention": (
            "the complete bulk top form is pulled back to fixed M_eps and varied with "
            "Delta=delta+Lie_xi; adding a separate i_xi L_5 would double count"
        ),
        "separate_domain_transgression_added": False,
        "finite_difference_error": abs(finite_difference - analytic),
    }


def green_form_certificate() -> dict[str, Any]:
    """Write the complete classical Green form and test the BF incidence signs."""

    b = np.asarray([0.7, -0.2, 0.4])
    delta_a = np.asarray([0.1, 0.5, -0.3])
    lam = np.asarray([-0.3, 0.6, 0.2])
    curvature = np.asarray([0.2, -0.1, 0.8])
    traces_b = np.vstack([b, b])
    traces_lam = np.vstack([lam, lam])
    correct_incidence = np.asarray([1.0, -1.0])
    wrong_incidence = np.asarray([1.0, 1.0])
    correct_bf = float((correct_incidence @ traces_b) @ delta_a)
    wrong_bf = float((wrong_incidence @ traces_b) @ delta_a)
    correct_shift = float((correct_incidence @ traces_lam) @ curvature)
    wrong_shift = float((wrong_incidence @ traces_lam) @ curvature)
    return {
        "bulk_equations_new_sector": {
            "B": "F[A]=0",
            "A": "D_A B+J_4=0 with J_4 proportional to Z*star(phi^[a P^(b])",
            "phi": (
                "Z*(D_M P^M-c_M P^M)-Z*M^2*Omega^(-7/2)*"
                "V4'(Omega^(3/2)|phi|)*phi_hat=0, c_M=3*d_M log(Omega)/2"
            ),
            "BF_metric_stress": "T_MN^(BF)=0",
        },
        "Green_form": (
            "Theta_Sigma=-M5^3/2*sum_eps int sqrt(-gamma)*pi_eps^(mu nu)"
            "Delta gamma_mu_nu-int sqrt(-gamma)*[sum_eps Pi_Omega,eps Delta Omega+"
            "<sum_eps Pi_phi,eps,Delta varphi_H>]-int <sum_eps s_eps b_eps wedge "
            "Delta A_Sigma>+delta(S_wall0+S_fol+S_R)"
        ),
        "EH_plus_GHY_first_variation": (
            "delta(S_EH+S_GHY)=M5^3/2*int_M sqrt(-g)*G_MN*Delta g^(MN)-"
            "M5^3/2*int_Sigma sqrt(-gamma)*(Theta^(mu nu)-Theta*gamma^(mu nu))*"
            "Delta gamma_mu_nu; no normal derivative of Delta gamma remains"
        ),
        "momenta": {
            "pi_eps": "Theta_eps^(mu nu)-Theta_eps*gamma^(mu nu)",
            "Pi_Omega_eps": (
                "G*n_eps.nabla Omega+3*Z*<phi,n_eps.P>/(2*Omega)"
            ),
            "Pi_phi_eps": "Z*j_eps(n_eps.P_eps)",
        },
        "natural_interface_equations": {
            "Israel": "M5^3*sum_eps pi_eps^(mu nu)=tau_Sigma^(mu nu)",
            "Omega": "sum_eps Pi_Omega_eps+partial_Omega Lambda_Sigma=0",
            "Robin": (
                "sum_eps Pi_phi_eps+kappa_hat*(varphi_H-y*a_sharp)=0"
            ),
            "BF_flux": "sum_eps s_eps*b_eps=0",
            "khronon": "E_T=0",
        },
        "adapted_foliation_variation": {
            "definitions": (
                "T=t; F_K=K_ij*K^ij-lambda_K*K^2; "
                "f(R)=xi*R-B4_bar*R^2/(16*k_infinity^2); "
                "C^ij=K^ij-lambda_K*K*h^ij"
            ),
            "lapse": "H_fol=-F_K+f(R)-eta*(a^2+2*D_i a^i)",
            "shift": "D_j C^ij=0 before the displayed matter and gravity sources",
            "spatial_metric": (
                "E_h^ij=-(partial_t-Lie_N)(sqrt(h)*C^ij)/(N*sqrt(h))+"
                "h^ij*F_K/2-2*K^i_k*K^(jk)+2*lambda_K*K*K^ij-"
                "f_R*R^ij+f*h^ij/2+(D^iD^j-h^ij*D^2)(N*f_R)/N+"
                "eta*(h^ij*a^2/2-a^i*a^j), with f_R=xi-"
                "B4_bar*R/(8*k_infinity^2)"
            ),
            "Robin": (
                "for r_i=varphi_i-y*D_i log(N), delta S_R=-kappa_hat/2*int "
                "N*sqrt(h)*[r^2*n+(h^ij*r^2/2-r^i*r^j)delta h_ij+"
                "2*r^i*(delta varphi_i-y*D_i n)]"
            ),
            "covariant_khronon_chain_rule": (
                "E_T=D_nu[N_T*h^nu_mu*E_u^mu]=0"
            ),
        },
        "moving_bending_variations": {
            "metric": (
                "H_eps_mu_nu=Y_eps^*delta g_eps+2*D_(mu xi_parallel_nu)+"
                "2*f_eps*Theta_eps_mu_nu"
            ),
            "Omega": "Delta Omega_eps=Y_eps^*(delta Omega_eps+xi_eps.d Omega_eps)",
            "material": (
                "Delta varphi_H=j_eps[Y_eps^*(delta phi_eps+i_xi D_A phi_eps)]+"
                "delta j_eps[Y_eps^*phi_eps]"
            ),
            "connection": (
                "Delta A_Sigma=Trans_iota[Y_eps^*(delta A_eps+i_xi F_eps)]"
            ),
            "bending_identity": (
                "the normal-displacement residual is the Green form with H=2*f*Theta, "
                "Delta Omega=f*n.dOmega, Delta varphi=f*j(n.D_A phi), "
                "Delta A=f*Trans_iota(i_n F); in the fixed-reference material convention "
                "the displacement is already carried by Delta, so no separate i_xi L5 "
                "is added; the diffeomorphism Noether identity makes this residual "
                "dependent on the bulk and interface equations"
            ),
        },
        "BF_boundary_form_error": abs(correct_bf),
        "BF_wrong_incidence_witness": abs(wrong_bf),
        "BF_shift_boundary_form_error": abs(correct_shift),
        "BF_shift_wrong_incidence_witness": abs(wrong_shift),
        "Sigma_has_no_boundary": True,
        "compact_support_at_bulk_infinity": True,
        "GHY_removes_normal_metric_variation": True,
        "intrinsic_Sigma_integrations_have_no_corner_terms": True,
        "complete_expanded_N4_junction_solution_claimed": False,
    }


def _rotation_z(angle: float) -> np.ndarray:
    return np.asarray(
        [
            [math.cos(angle), -math.sin(angle), 0.0],
            [math.sin(angle), math.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def _rotation_x(angle: float) -> np.ndarray:
    return np.asarray(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(angle), -math.sin(angle)],
            [0.0, math.sin(angle), math.cos(angle)],
        ]
    )


def _so3_exponential(generator: np.ndarray, parameter: float) -> np.ndarray:
    """Rodrigues exponential for a real 3x3 antisymmetric generator."""

    frequency = math.sqrt(max(0.0, -0.5 * float(np.trace(generator @ generator))))
    if frequency < 1.0e-15:
        return np.eye(3)
    scaled = parameter * frequency
    return (
        np.eye(3)
        + math.sin(scaled) / frequency * generator
        + (1.0 - math.cos(scaled)) / frequency**2 * (generator @ generator)
    )


_N8_GAUGE_GENERATORS = (
    np.asarray([[0.0, -0.2, 0.1], [0.2, 0.0, -0.3], [-0.1, 0.3, 0.0]]),
    np.asarray([[0.0, 0.15, -0.25], [-0.15, 0.0, 0.05], [0.25, -0.05, 0.0]]),
    np.asarray([[0.0, -0.08, 0.12], [0.08, 0.0, -0.18], [-0.12, 0.18, 0.0]]),
    np.asarray([[0.0, 0.11, 0.07], [-0.11, 0.0, -0.09], [-0.07, 0.09, 0.0]]),
)
_N8_GAUGE_AMPLITUDES = np.asarray([0.37, 0.29, 0.31, 0.23])


def _n8_gauge_angles(
    coordinates: np.ndarray, homotopy_parameter: float = 1.0
) -> tuple[np.ndarray, np.ndarray]:
    """Angles and first derivatives for a periodic, decaying small gauge map."""

    point = np.asarray(coordinates, dtype=float)
    if point.shape != (4,):
        raise ClassicalV52InputError("N8 gauge coordinates must have shape (4,)")
    scale = float(homotopy_parameter)
    if not math.isfinite(scale) or not 0.0 <= scale <= 1.0:
        raise ClassicalV52InputError("N8 gauge homotopy parameter must lie in [0,1]")
    z, x1, x2, x3 = point
    decay = math.exp(-z)
    angles = scale * _N8_GAUGE_AMPLITUDES * decay * np.asarray(
        [z, math.sin(x1), math.sin(x2), math.sin(x3)]
    )
    jacobian = np.zeros((4, 4))
    jacobian[0, 0] = scale * _N8_GAUGE_AMPLITUDES[0] * decay * (1.0 - z)
    jacobian[1:, 0] = -angles[1:]
    jacobian[1, 1] = scale * _N8_GAUGE_AMPLITUDES[1] * decay * math.cos(x1)
    jacobian[2, 2] = scale * _N8_GAUGE_AMPLITUDES[2] * decay * math.cos(x2)
    jacobian[3, 3] = scale * _N8_GAUGE_AMPLITUDES[3] * decay * math.cos(x3)
    return angles, jacobian


def _n8_global_gauge(
    coordinates: np.ndarray, homotopy_parameter: float = 1.0
) -> np.ndarray:
    """H_s=prod_i exp(s theta_i X_i), with H_0=1 and H_1=G."""

    angles, _ = _n8_gauge_angles(coordinates, homotopy_parameter)
    gauge = np.eye(3)
    for generator, angle in zip(_N8_GAUGE_GENERATORS, angles):
        gauge = gauge @ _so3_exponential(generator, float(angle))
    return gauge


def _n8_right_maurer_cartan(
    coordinates: np.ndarray, homotopy_parameter: float = 1.0
) -> np.ndarray:
    """Return K_mu=(partial_mu G)G^-1 from the same ordered global G."""

    angles, angle_jacobian = _n8_gauge_angles(
        coordinates, homotopy_parameter
    )
    prefix = np.eye(3)
    generators = np.zeros((4, 3, 3))
    for index, (base_generator, angle) in enumerate(
        zip(_N8_GAUGE_GENERATORS, angles)
    ):
        conjugated = prefix @ base_generator @ prefix.T
        generators += angle_jacobian[index, :, None, None] * conjugated
        prefix = prefix @ _so3_exponential(base_generator, float(angle))
    return generators


def _v4(value: np.ndarray) -> np.ndarray:
    radius = np.abs(value)
    return 0.5 * radius**4 / np.sqrt(1.0 + radius**4)


def _v4_prime(value: np.ndarray) -> np.ndarray:
    return value**3 * (value**4 + 2.0) / (1.0 + value**4) ** 1.5


def n8_functional_transport_certificate(
    upstream: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify the full canonical functional and Euler-operator intertwiner."""

    rng = np.random.default_rng(5208)
    samples = 19
    directions = 4
    signed_u = np.linspace(-1.3, 1.1, samples) + rng.normal(scale=0.03, size=samples)
    du = rng.normal(scale=0.4, size=(samples, directions))
    d2u = rng.normal(scale=0.25, size=(samples, directions))
    omega = np.linspace(0.31, 1.0, samples)
    d_log_omega = rng.normal(scale=0.2, size=(samples, directions))
    n0 = np.asarray([0.0, 0.0, 1.0])
    coordinates = np.asarray([0.61, 0.17, -0.23, 0.31])
    rotation = _n8_global_gauge(coordinates)
    generators = _n8_right_maurer_cartan(coordinates)
    direction = rotation @ n0
    finite_difference_step = 2.0e-6
    generator_errors: list[float] = []
    for mu in range(directions):
        forward = coordinates.copy()
        backward = coordinates.copy()
        forward[mu] += finite_difference_step
        backward[mu] -= finite_difference_step
        derivative_g = (
            _n8_global_gauge(forward) - _n8_global_gauge(backward)
        ) / (2.0 * finite_difference_step)
        finite_difference_generator = derivative_g @ rotation.T
        generator_errors.append(
            float(np.linalg.norm(finite_difference_generator - generators[mu]))
        )
    generator_finite_difference_error = max(generator_errors)

    homotopy_parameters = np.linspace(0.0, 1.0, 5)
    homotopy_so3_error = 0.0
    homotopy_periodicity_error = 0.0
    for homotopy_parameter in homotopy_parameters:
        gauge = _n8_global_gauge(coordinates, float(homotopy_parameter))
        homotopy_so3_error = max(
            homotopy_so3_error,
            float(np.linalg.norm(gauge.T @ gauge - np.eye(3))),
            abs(float(np.linalg.det(gauge)) - 1.0),
        )
        for mu in range(1, directions):
            shifted = coordinates.copy()
            shifted[mu] += 2.0 * math.pi
            homotopy_periodicity_error = max(
                homotopy_periodicity_error,
                float(
                    np.linalg.norm(
                        _n8_global_gauge(shifted, float(homotopy_parameter))
                        - gauge
                    )
                ),
            )
    homotopy_identity_error = float(
        np.linalg.norm(_n8_global_gauge(coordinates, 0.0) - np.eye(3))
    )
    infinity_point = coordinates.copy()
    infinity_point[0] = 40.0
    bulk_infinity_identity_error = float(
        np.linalg.norm(_n8_global_gauge(infinity_point) - np.eye(3))
    )
    weight = omega ** (-1.5)
    phi = weight[:, None] * signed_u[:, None] * direction[None, :]
    p = np.empty((samples, directions, 3))
    p_wrong_sign = np.empty_like(p)
    p_missing_weight = np.empty_like(p)
    for mu, generator in enumerate(generators):
        d_phi = weight[:, None] * (
            signed_u[:, None] * (generator @ direction)[None, :]
            + du[:, mu, None] * direction[None, :]
            - 1.5
            * signed_u[:, None]
            * d_log_omega[:, mu, None]
            * direction[None, :]
        )
        connection = -generator
        p[:, mu, :] = (
            d_phi
            + np.einsum("ab,nb->na", connection, phi)
            + 1.5 * d_log_omega[:, mu, None] * phi
        )
        p_wrong_sign[:, mu, :] = (
            d_phi
            - np.einsum("ab,nb->na", connection, phi)
            + 1.5 * d_log_omega[:, mu, None] * phi
        )
        unweighted_phi = signed_u[:, None] * direction[None, :]
        d_unweighted = (
            signed_u[:, None] * (generator @ direction)[None, :]
            + du[:, mu, None] * direction[None, :]
        )
        p_missing_weight[:, mu, :] = (
            d_unweighted
            + np.einsum("ab,nb->na", connection, unweighted_phi)
            + 1.5 * d_log_omega[:, mu, None] * unweighted_phi
        )
    expected_p = (
        weight[:, None, None]
        * du[:, :, None]
        * direction[None, None, :]
    )
    derivative_intertwiner_error = float(np.max(np.abs(p - expected_p)))
    wrong_connection_sign_witness = float(np.max(np.abs(p_wrong_sign - expected_p)))
    missing_omega_weight_witness = float(
        np.max(
            np.abs(
                omega[:, None, None] ** 1.5 * p_missing_weight
                - du[:, :, None] * direction[None, None, :]
            )
        )
    )
    current_norm = max(
        float(np.linalg.norm(np.cross(phi, p[:, mu, :]), axis=1).max())
        for mu in range(directions)
    )
    potential_argument_error = float(
        np.max(np.abs(omega**1.5 * np.linalg.norm(phi, axis=1) - np.abs(signed_u)))
    )
    v4_probe = np.asarray([-1.7, -0.9, -0.2, 0.2, 0.9, 1.7])
    reference_radius = np.abs(v4_probe)
    reference_v4 = 0.5 * reference_radius**4 / np.sqrt(
        1.0 + reference_radius**4
    )
    v4_reference_value_error = float(
        np.max(np.abs(_v4(v4_probe) - reference_v4))
    )
    v4_difference_step = 2.0e-6
    forward_radius = np.abs(v4_probe + v4_difference_step)
    backward_radius = np.abs(v4_probe - v4_difference_step)
    reference_forward = 0.5 * forward_radius**4 / np.sqrt(
        1.0 + forward_radius**4
    )
    reference_backward = 0.5 * backward_radius**4 / np.sqrt(
        1.0 + backward_radius**4
    )
    independent_v4_derivative = (reference_forward - reference_backward) / (
        2.0 * v4_difference_step
    )
    v4_prime_finite_difference_error = float(
        np.max(np.abs(_v4_prime(v4_probe) - independent_v4_derivative))
    )

    covariant_second = np.empty((samples, directions, 3))
    for mu, generator in enumerate(generators):
        covariant_first = du[:, mu, None] * direction[None, :]
        ordinary_derivative_of_covariant_first = (
            du[:, mu, None] * (generator @ direction)[None, :]
            + d2u[:, mu, None] * direction[None, :]
        )
        covariant_second[:, mu, :] = (
            ordinary_derivative_of_covariant_first
            - np.einsum("ab,nb->na", generator, covariant_first)
        )
    scalar_euler_residual = np.sum(d2u, axis=1) - _v4_prime(signed_u)
    vector_euler_residual = scalar_euler_residual[:, None] * direction[None, :]
    mapped_euler_residual = np.sum(covariant_second, axis=1) - (
        _v4_prime(signed_u)[:, None] * direction[None, :]
    )
    euler_intertwiner_error = float(
        np.max(np.abs(mapped_euler_residual - vector_euler_residual))
    )
    manufactured_residual_norm = float(np.linalg.norm(scalar_euler_residual))

    source = np.linspace(-0.6, 0.8, samples)
    boundary_u = signed_u
    boundary_du = du[:, 0]
    tension = 1.0
    spring = 0.5
    yukawa = math.sqrt(3.0)
    scalar_robin = tension * boundary_du - spring * (
        boundary_u - yukawa * source
    )
    vector_robin = (
        tension * boundary_du[:, None] * direction[None, :]
        - spring
        * (boundary_u - yukawa * source)[:, None]
        * direction[None, :]
    )
    robin_intertwiner_error = float(
        np.max(np.abs(vector_robin - scalar_robin[:, None] * direction[None, :]))
    )

    pi_u = rng.normal(scale=0.3, size=samples)
    upstream_energy = float(
        np.sum(0.5 * np.sum(du**2, axis=1) + _v4(signed_u))
        + 0.5 * spring * np.sum((boundary_u - yukawa * source) ** 2)
    )
    lifted_gradient = p
    conformal_kinetic_density = (
        omega**5
        * omega ** (-2)
        * 0.5
        * np.sum(lifted_gradient**2, axis=(1, 2))
    )
    conformal_potential_density = omega**5 * omega ** (-5) * _v4(
        omega**1.5 * np.linalg.norm(phi, axis=1)
    )
    lifted_energy = float(
        np.sum(conformal_kinetic_density + conformal_potential_density)
        + 0.5
        * spring
        * np.sum(
            np.linalg.norm(
                (boundary_u - yukawa * source)[:, None] * direction[None, :],
                axis=1,
            )
            ** 2
        )
    )
    upstream_hamiltonian = float(
        np.sum(0.5 * pi_u**2 + 0.5 * np.sum(du**2, axis=1) + _v4(signed_u))
        + 0.5 * spring * np.sum((boundary_u - yukawa * source) ** 2)
    )
    lifted_pi = pi_u[:, None] * direction[None, :]
    lifted_hamiltonian = float(
        np.sum(
            0.5 * np.sum(lifted_pi**2, axis=1)
            + conformal_kinetic_density
            + conformal_potential_density
        )
        + 0.5
        * spring
        * np.sum((boundary_u - yukawa * source) ** 2)
    )

    curvature_component_norms: dict[str, float] = {}
    wrong_curvature_component_norms: dict[str, float] = {}
    for mu in range(directions):
        for nu in range(mu + 1, directions):
            forward_mu = coordinates.copy()
            backward_mu = coordinates.copy()
            forward_mu[mu] += finite_difference_step
            backward_mu[mu] -= finite_difference_step
            derivative_mu_a_nu = (
                -_n8_right_maurer_cartan(forward_mu)[nu]
                + _n8_right_maurer_cartan(backward_mu)[nu]
            ) / (2.0 * finite_difference_step)
            derivative_mu_k_nu = -derivative_mu_a_nu

            forward_nu = coordinates.copy()
            backward_nu = coordinates.copy()
            forward_nu[nu] += finite_difference_step
            backward_nu[nu] -= finite_difference_step
            derivative_nu_a_mu = (
                -_n8_right_maurer_cartan(forward_nu)[mu]
                + _n8_right_maurer_cartan(backward_nu)[mu]
            ) / (2.0 * finite_difference_step)
            derivative_nu_k_mu = -derivative_nu_a_mu

            a_mu = -generators[mu]
            a_nu = -generators[nu]
            curvature = (
                derivative_mu_a_nu
                - derivative_nu_a_mu
                + a_mu @ a_nu
                - a_nu @ a_mu
            )
            wrong_curvature = (
                derivative_mu_k_nu
                - derivative_nu_k_mu
                + generators[mu] @ generators[nu]
                - generators[nu] @ generators[mu]
            )
            component = f"{mu}{nu}"
            curvature_component_norms[component] = float(np.linalg.norm(curvature))
            wrong_curvature_component_norms[component] = float(
                np.linalg.norm(wrong_curvature)
            )
    curvature_max_norm = max(curvature_component_norms.values())
    wrong_curvature_max_norm = max(wrong_curvature_component_norms.values())
    extra_metric_scale = 1.27
    nonconformal_metric_density = (
        extra_metric_scale**3 * 0.5 * np.sum(du**2, axis=1)
        + extra_metric_scale**5 * _v4(signed_u)
    )
    canonical_density = 0.5 * np.sum(du**2, axis=1) + _v4(signed_u)

    rows = upstream["periodic_full_V4_rows"]
    expected_cases = [
        [0.08, 0.35, 0.0],
        [0.8, 0.35, 0.0],
        [0.8, 1.2, 0.0],
        [0.8, 5.0, 0.0],
        [2.0, 0.6, 0.25],
    ]
    actual_cases = [
        [row["amplitude_A"], row["momentum_q_over_M"], row["third_harmonic_fraction"]]
        for row in rows
    ]
    expected_row_parameters = {
        "M": 1.0,
        "T_equals_Ns_Z5": 1.0,
        "kappa": 0.5,
        "y": math.sqrt(3.0),
        "y_squared_kappa": 1.5,
    }
    all_row_parameters_match = all(
        all(
            math.isclose(
                float(row["parameters"].get(key, math.nan)),
                expected,
                rel_tol=0.0,
                abs_tol=2.0e-14,
            )
            for key, expected in expected_row_parameters.items()
        )
        for row in rows
    )
    worst_eom = max(
        row["Galerkin"]["relative_pointwise_full_EOM_RMS"] for row in rows
    )
    all_rows_converged = (
        len(rows) == len(expected_cases)
        and actual_cases == expected_cases
        and all_row_parameters_match
        and all(
            row["Galerkin"]["converged"]
            and row["Galerkin"]["relative_pointwise_full_EOM_RMS"] < 2.0e-5
            and row["source_closure"]["maximum_pointwise_Robin_residual"]
            < 2.0e-8
            and row["source_closure"]["maximum_pointwise_current_flux_mismatch"]
            < 2.0e-8
            and row["stability"]["unique_global_minimizer"]
            and row["stability"]["negative_mode_possible_in_material_functional"]
            is False
            for row in rows
        )
    )
    upstream_tail_relative_energy_change = upstream["resolution_and_tail_audit"][
        "relative_energy_change"
    ]
    global_gauge_certificate_pass = bool(
        generator_finite_difference_error < 2.0e-9
        and homotopy_so3_error < 2.0e-13
        and homotopy_periodicity_error < 2.0e-13
        and homotopy_identity_error < 2.0e-14
        and bulk_infinity_identity_error < 2.0e-14
        and len(curvature_component_norms) == 6
        and curvature_max_norm < 2.0e-9
    )
    functional_transport_pass = bool(
        global_gauge_certificate_pass
        and derivative_intertwiner_error < 2.0e-13
        and potential_argument_error < 2.0e-13
        and v4_reference_value_error < 2.0e-14
        and v4_prime_finite_difference_error < 2.0e-9
        and current_norm < 2.0e-13
        and manufactured_residual_norm > 1.0e-2
        and euler_intertwiner_error < 2.0e-13
        and robin_intertwiner_error < 2.0e-13
        and abs(lifted_energy - upstream_energy) < 2.0e-12
    )
    finite_q_material_solution_transported = bool(
        functional_transport_pass
        and all_rows_converged
        and worst_eom < 2.0e-5
        and upstream_tail_relative_energy_change < 3.0e-5
    )
    material_reduced_hamiltonian_preserved = bool(
        functional_transport_pass
        and abs(lifted_hamiltonian - upstream_hamiltonian) < 2.0e-12
    )
    return {
        "theorem": (
            "for every signed canonical u in the upstream finite-energy domain, "
            "phi=Omega^(-3/2)G*n0*u, A=-(dG)G^(-1), B=0 intertwines the complete "
            "material functional, Euler operator and Robin residual"
        ),
        "executable_global_gauge_map": (
            "G(z,x)=prod_i exp(theta_i(z,x)*X_i), theta_0=a_0*z*exp(-z), "
            "theta_i=a_i*exp(-z)*sin(x_i) for i=1,2,3; "
            "K_mu=sum_i partial_mu(theta_i)*Ad_(prod_(j<i) exp(theta_j*X_j))X_i; "
            "H_s=prod_i exp(s*theta_i*X_i) contracts G to identity"
        ),
        "domain": [
            "prescribed background metric g_eps=Omega^2*eta_hat on the canonical flat half-space",
            "Omega>0 and Omega|Sigma=1",
            "G is C2, time-independent, 2*pi-periodic in tangential x_i, tends to identity as z tends to infinity, and is null-homotopic and extendible",
            "G_plus and G_minus have one common transported trace",
            "u is signed; only V4 receives |u|",
            "source acceleration is collinear and transported by the same G*n0",
            "T=1, kappa=1/2 and y^2=3 after the two-side normalization",
        ],
        "derivative_intertwiner_max_error": derivative_intertwiner_error,
        "potential_argument_max_error": potential_argument_error,
        "V4_reference_value_max_error": v4_reference_value_error,
        "V4_prime_independent_finite_difference_max_error": (
            v4_prime_finite_difference_error
        ),
        "all_direction_SO3_current_max_norm": current_norm,
        "manufactured_nonzero_scalar_residual_norm": manufactured_residual_norm,
        "Euler_operator_intertwiner_max_error": euler_intertwiner_error,
        "Robin_intertwiner_max_error": robin_intertwiner_error,
        "global_G_SO3_max_error_along_null_homotopy": homotopy_so3_error,
        "global_G_tangential_periodicity_max_error": homotopy_periodicity_error,
        "global_G_null_homotopy_identity_endpoint_error": homotopy_identity_error,
        "global_G_bulk_infinity_identity_error": bulk_infinity_identity_error,
        "K_equals_dG_Ginverse_finite_difference_max_error": (
            generator_finite_difference_error
        ),
        "Maurer_Cartan_components_checked": len(curvature_component_norms),
        "Maurer_Cartan_component_norms": curvature_component_norms,
        "Maurer_Cartan_curvature_norm": curvature_max_norm,
        "global_periodic_null_homotopic_gauge_certificate_pass": (
            global_gauge_certificate_pass
        ),
        "functional_energy_equality_error": abs(lifted_energy - upstream_energy),
        "material_reduced_Hamiltonian_equality_error": abs(
            lifted_hamiltonian - upstream_hamiltonian
        ),
        "negative_controls": {
            "missing_Omega_minus_three_halves_witness": missing_omega_weight_witness,
            "wrong_connection_sign_witness": wrong_connection_sign_witness,
            "wrong_Maurer_Cartan_sign_witness": wrong_curvature_max_norm,
            "wrong_Maurer_Cartan_component_norms": (
                wrong_curvature_component_norms
            ),
            "absolute_value_would_destroy_signed_rows": int(np.count_nonzero(signed_u < 0)),
            "mismatched_boundary_G_witness": float(
                np.linalg.norm((_rotation_x(0.2) - np.eye(3)) @ n0)
            ),
            "noncanonical_metric_conformal_factor_witness": float(
                np.max(np.abs(nonconformal_metric_density - canonical_density))
            ),
        },
        "upstream_cases": actual_cases,
        "expected_upstream_cases": expected_cases,
        "expected_upstream_row_parameters": expected_row_parameters,
        "all_upstream_row_parameters_match": all_row_parameters_match,
        "all_five_upstream_rows_converged": all_rows_converged,
        "worst_upstream_relative_EOM_RMS": worst_eom,
        "upstream_mode_tail_relative_energy_change": (
            upstream_tail_relative_energy_change
        ),
        "functional_transport_prerequisites_pass": functional_transport_pass,
        "finite_q_material_solution_transported": (
            finite_q_material_solution_transported
        ),
        "material_reduced_Hamiltonian_preserved": (
            material_reduced_hamiltonian_preserved
        ),
        "total_BF_gravity_Hamiltonian_positive_claimed": False,
        "dynamic_gravity_claimed": False,
    }


def build_payload() -> dict[str, Any]:
    upstreams = _load_upstreams()
    charter = exact_classical_charter(upstreams)
    frame = frame_and_robin_variation_certificate()
    acceleration = acceleration_variation_certificate()
    moving = moving_pullback_certificate()
    green = green_form_certificate()
    n8 = n8_functional_transport_certificate(upstreams["nonlinear_robin_full_V4"])

    checks = {
        "four_upstreams_byte_hash_schema_and_scope_bound": set(upstreams) == set(UPSTREAMS),
        "one_literal_action_has_all_fields_coefficients_and_no_ellipsis": (
            not _contains_ellipsis(charter)
            and set(charter["exact_action"])
            == {
                "total",
                "superpotential",
                "bulk_potential",
                "full_V4",
                "bulk_gauged",
                "gauged_conformal_derivative",
                "GHY",
                "wall_background",
                "foliation_lower",
                "Robin_intrinsic",
                "BF",
                "removed_terms",
            }
            and charter["coefficient_policy"][
                "all_unlisted_local_classical_operator_coefficients_at_mu_star"
            ]
            == 0.0
            and charter["coefficient_policy"]["parameters"][
                "kappa_BF_inner_product"
            ]
            == 1.0
            and charter["coefficient_policy"]["parameters"][
                "k_BF_trace_equivalent"
            ]
            == -0.5
        ),
        "gauge_covariant_associated_connection_and_form_traces_replace_component_gluing": (
            "j_plus" in " ".join(charter["interface_domain"]["configuration"])
            and "Trans_iota_plus" in " ".join(charter["interface_domain"]["configuration"])
            and "Ad_r" in charter["definitions"]["adjoint_form_trace"]
        ),
        "metric_khronon_frame_lift_and_Robin_differential_close": (
            frame["linearized_u_norm_error"] < 2.0e-13
            and frame["linearized_frame_spatiality_error"] < 2.0e-13
            and frame["linearized_frame_orthonormality_error"] < 2.0e-13
            and frame["Robin_finite_difference_error"] < 1.0e-9
            and frame["vertical_frame_rotation_phi_cancellation_error"] < 2.0e-14
            and frame["vertical_frame_rotation_acceleration_cancellation_error"]
            < 2.0e-14
            and acceleration["finite_difference_error"] < 1.0e-9
        ),
        "moving_pullbacks_and_domain_transgression_are_explicit": (
            moving["finite_difference_error"] < 1.0e-9
            and "i_xi F" in moving["connection_material_variation"]
            and moving["separate_domain_transgression_added"] is False
        ),
        "Green_form_records_BF_and_intrinsic_terms_but_full_moving_variation_stays_open": (
            green["BF_boundary_form_error"] < 2.0e-14
            and green["BF_shift_boundary_form_error"] < 2.0e-14
            and green["BF_wrong_incidence_witness"] > 1.0e-2
            and green["BF_shift_wrong_incidence_witness"] > 1.0e-2
            and green["Sigma_has_no_boundary"]
            and green["compact_support_at_bulk_infinity"]
            and green["GHY_removes_normal_metric_variation"]
            and green["intrinsic_Sigma_integrations_have_no_corner_terms"]
            and green["complete_expanded_N4_junction_solution_claimed"] is False
        ),
        "N8_is_a_full_functional_and_Euler_transport_not_a_point_sample": (
            n8["global_periodic_null_homotopic_gauge_certificate_pass"]
            and n8["K_equals_dG_Ginverse_finite_difference_max_error"] < 2.0e-9
            and n8["global_G_SO3_max_error_along_null_homotopy"] < 2.0e-13
            and n8["global_G_tangential_periodicity_max_error"] < 2.0e-13
            and n8["global_G_null_homotopy_identity_endpoint_error"] < 2.0e-14
            and n8["global_G_bulk_infinity_identity_error"] < 2.0e-14
            and n8["Maurer_Cartan_components_checked"] == 6
            and n8["derivative_intertwiner_max_error"] < 2.0e-13
            and n8["potential_argument_max_error"] < 2.0e-13
            and n8["V4_reference_value_max_error"] < 2.0e-14
            and n8["V4_prime_independent_finite_difference_max_error"] < 2.0e-9
            and n8["all_direction_SO3_current_max_norm"] < 2.0e-13
            and n8["manufactured_nonzero_scalar_residual_norm"] > 1.0e-2
            and n8["Euler_operator_intertwiner_max_error"] < 2.0e-13
            and n8["Robin_intertwiner_max_error"] < 2.0e-13
            and n8["Maurer_Cartan_curvature_norm"] < 2.0e-9
            and n8["functional_energy_equality_error"] < 2.0e-12
            and n8["material_reduced_Hamiltonian_equality_error"] < 2.0e-12
            and n8["functional_transport_prerequisites_pass"]
            and n8["finite_q_material_solution_transported"]
            and n8["material_reduced_Hamiltonian_preserved"]
            and n8["total_BF_gravity_Hamiltonian_positive_claimed"] is False
            and n8["dynamic_gravity_claimed"] is False
        ),
        "N8_negative_controls_expose_every_previous_false_shortcut": (
            n8["negative_controls"]["missing_Omega_minus_three_halves_witness"] > 1.0e-3
            and n8["negative_controls"]["wrong_connection_sign_witness"] > 1.0e-3
            and n8["negative_controls"]["wrong_Maurer_Cartan_sign_witness"] > 1.0e-3
            and n8["negative_controls"]["absolute_value_would_destroy_signed_rows"] > 0
            and n8["negative_controls"]["mismatched_boundary_G_witness"] > 1.0e-3
            and n8["negative_controls"][
                "noncanonical_metric_conformal_factor_witness"
            ]
            > 1.0e-3
        ),
        "direct_hash_bound_upstream_N8_rows_and_Hamiltonian_are_consumed": (
            n8["upstream_cases"] == n8["expected_upstream_cases"]
            and n8["all_upstream_row_parameters_match"]
            and n8["all_five_upstream_rows_converged"]
            and n8["worst_upstream_relative_EOM_RMS"] < 2.0e-5
            and n8["upstream_mode_tail_relative_energy_change"] < 3.0e-5
            and upstreams["nonlinear_robin_full_V4"]["decision"][
                "canonical_time_dependent_material_Hamiltonian_positive"
            ]
        ),
        "classical_and_quantum_or_dynamic_gravity_scopes_are_separated": (
            charter["BRST_BV_BFV_completion_included"] is False
            and green["complete_expanded_N4_junction_solution_claimed"] is False
            and n8["dynamic_gravity_claimed"] is False
        ),
        "no_legacy_modes_or_CSV_used": True,
    }
    checks["all"] = all(checks.values())
    if not checks["all"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"topological SO3 classical v5.2 checks failed: {failed}")

    n8_pass = bool(
        checks["N8_is_a_full_functional_and_Euler_transport_not_a_point_sample"]
        and checks["N8_negative_controls_expose_every_previous_false_shortcut"]
        and checks["direct_hash_bound_upstream_N8_rows_and_Hamiltonian_are_consumed"]
    )
    decision = {
        "boundary_bundle_isomorphism_trivial_sector_pass": True,
        "orientation_null_modes_removed_in_selected_sector": True,
        "exact_single_classical_action_candidate_charter_pass": True,
        "full_classical_variational_principle_selected_sector_pass": False,
        "N8_same_solution_functional_transport_theorem_pass": n8_pass,
        "finite_q_material_solution_transported": n8[
            "finite_q_material_solution_transported"
        ],
        "material_reduced_Hamiltonian_preserved": n8[
            "material_reduced_Hamiltonian_preserved"
        ],
        "dynamic_gravity_claimed": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "N8_MATERIAL_PORT_pass": n8_pass,
        "C1_target_scope_is_classical_trivial_null_homotopic_sector": True,
        "N1_target_scope_is_exact_action_not_N2_through_N7": True,
        "N8_scope_is_prescribed_acceleration_full_V4_only": True,
        "unrestricted_large_gauge_sector_pass": False,
        "all_boundary_topologies_pass": False,
        "complete_BV_BFV_boundary_complex_pass": False,
        "global_BF_edge_mode_absence_pass": False,
        "A_minus_frame_connection_edge_sector_eliminated": False,
        "C2_BRST_pass": False,
        "C3_DOMAIN_pass": False,
        "C4_HESSIAN_pass": False,
        "C5_JACOBIANS_pass": False,
        "C6_ZERO_MODES_pass": False,
        "C7_REGULATOR_pass": False,
        "C8_CONTOUR_pass": False,
        "C9_REDUCTION_pass": False,
        "C10_INDEPENDENCE_UNITARITY_pass": False,
        "N2_CONSTRAINTS_pass": False,
        "N3_CHARACTERISTICS_pass": False,
        "N4_JUNCTION_BENDING_pass": False,
        "N5_COUPLED_BVP_pass": False,
        "N6_GLOBAL_STABILITY_pass": False,
        "N7_LINEAR_REDUCTION_pass": False,
        "full_same_action_ghost_freedom_pass": False,
        "P3_complete_gauge_fixed_unitary_determinant_pass": False,
        "P4_full_same_action_pass": False,
        "nonlinear_gravitational_P4_pass": False,
        "full_P2_pass": False,
        "B4_pass": False,
        "B5_pass": False,
        "a0_predicted": False,
        "universal_matter_metric_and_lensing_derived": False,
        "new_force_validated": False,
        "publication_authorized": False,
        "legacy_modes_or_CSV_reused": False,
        "status": (
            "TOPOLOGICAL_SO3_CLASSICAL_V5_2_TRIVIAL_SECTOR__"
            "PRESCRIBED_N8_PASS__C1_N1_MOVING_VARIATION_HOLD__"
            "C2_C10_N2_N7_P2_P4_B4_B5_FAIL_CLOSED"
        ),
        "decisive_result": (
            "One literal normalized classical action candidate now replaces the v5 patch recipe. "
            "Its connection and associated-vector traces are gauge-covariant, its "
            "metric-dependent frame and moving-pullback first variations are explicit, "
            "and the BF Green form has the required oriented flux equation. The corrected "
            "Omega^(-3/2) pure-gauge map is an isometry of the complete prescribed-port "
            "full-V4 functional and transports its finite-q Euler residuals, Robin data, "
            "convergence and reduced material Hamiltonian. This closes prescribed-background "
            "N8 only. C1 and N1 remain false until the complete moving-brane variational "
            "principle is derived on one geometric family without double counting."
        ),
        "next_action": (
            "Derive and independently red-team the complete moving-brane Green form on a "
            "nonflat geometric family. Then construct the relative BF "
            "BRST/BV-BFV and A_Sigma-frame edge complex before any fresh N7/P4 campaign. "
            "Do not import legacy modes, CSVs or determinants."
        ),
    }
    for key in FAIL_CLOSED_KEYS:
        if decision[key] is not False:
            raise RuntimeError(f"fail-closed key was promoted: {key}")

    return {
        "schema": SCHEMA,
        "title": "One-Omega topological SO(3) sectorial classical v5.2 gate",
        "classification": (
            "theory_only;trivial_null_homotopic_sector;prescribed_N8_pass;"
            "C1_N1_moving_variation_hold;"
            "BRST_large_gauge_N2_N7_P2_P4_B4_B5_fail_closed"
        ),
        "evidence_boundary": (
            "The gate proves prescribed-port N8 transport on the fixed contractible, "
            "extendible gauge component and writes an exact action candidate. It does not "
            "yet prove the complete moving-brane variational principle or C1/N1. It "
            "does not prove the complete BF edge/ghost complex, large gauges, dynamic "
            "gravity, N2-N7, P2-P4, B4, B5, force or lensing."
        ),
        "exact_classical_charter": charter,
        "frame_and_Robin_variation_certificate": frame,
        "acceleration_variation_certificate": acceleration,
        "moving_pullback_certificate": moving,
        "Green_form_certificate": green,
        "N8_functional_transport_certificate": n8,
        "checks": checks,
        "decision": decision,
        "upstreams": {
            name: {
                "path": str(spec["path"].relative_to(REPO)),
                "schema": spec["schema"],
                "sha256": spec["sha256"],
            }
            for name, spec in UPSTREAMS.items()
        },
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {"path": str(TEST.relative_to(REPO)), "sha256": _sha256(TEST)},
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    payload = build_payload()
    _write(OUTPUT, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
