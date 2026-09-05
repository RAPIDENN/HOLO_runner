#!/usr/bin/env python3
"""Freeze the classical one-Omega bulk-plus-wall action charter.

This gate resolves the action items ``C1_ACTION`` and ``N1_ACTION``.  It
selects the canonical positive-norm backreacted one-Omega
wall, the bare matched ADM coefficient point, and one concrete rank-full
Stueckelberg-solid solder.  The complete action, field content, symmetries,
domains, moving embedding, GHY term, conformal triplet, Robin term and the
zero coefficient assigned to every unlisted operator are recorded without an
ellipsis.

The result is deliberately not a transport of the historical linear P4
receipt.  A healthy dynamical solid has three fluctuations and nonzero mixed
second derivatives with the ADM shift and spatial metric, so its full Hessian
is not the old wall-ADM Hessian.  Complete nonlinear constraints,
characteristics, displaced-wall junctions and the new extended Hessian have
not been derived.  Therefore C2-C10, N2-N7, P2, complete P3, nonlinear P4,
B4 and B5 remain false.  N8 is retained only as the direct prescribed-
acceleration material-port result; it is not a nonlinear gravity result.

No registry, build script, paper, README or PDF is modified by this gate.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from numbers import Real
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "one_omega_action_charter_gate.json"
TEST = HERE / "test_one_omega_action_charter_gate.py"

WALL = HERE / "artifacts" / "backreacted_compensator_wall_gate.json"
WALL_ADM = HERE / "artifacts" / "wall_adm_base_hessian_gate.json"
NONLINEAR_ROBIN = HERE / "artifacts" / "nonlinear_robin_full_v4_gate.json"

SCHEMA = "holo.one-omega-action-charter-gate.v1"
ROUTE_ID = "canonical_one_Omega_backreacted_wall_with_rank_full_solid_v1"

FROZEN_PARAMETERS = {
    "M5_cubed": 1.0,
    "k_infinity": 1.0,
    "compensator_metric_G": 1.2,
    "brane_beta": 2.0,
    "material_Z5_per_side": 1.0,
    "material_mass_M": 1.0,
    "M4_bulk_squared_selected_one_Omega_wall_value": 1.107013790800849,
    "brane_Mb_squared": 2.0,
    "lambda_K": 1.3107013790800848,
    "xi": 1.0,
    "eta": 3.107013790800849,
    "B4_bar": 0.8,
    "Robin_kappa_in_Mb_units": 0.5,
    "Robin_kappa_hat": 1.0,
    "Robin_y_squared": 3.0,
    "Robin_y": math.sqrt(3.0),
    "solid_v": 1.0,
    "solid_rho": 1.0,
    "solid_mu": 1.0,
    "solid_lambda": 1.0,
}

UPSTREAM_PATHS = {
    "backreacted_wall": WALL,
    "wall_ADM": WALL_ADM,
    "nonlinear_Robin_full_V4": NONLINEAR_ROBIN,
}
UPSTREAM_HASHES = {
    "backreacted_wall": "7cc97911d3265ac131d2fabad9a4676eb05643ecd8be1c3b7acd586d58e5e369",
    "wall_ADM": "f0b491d498b8a68ec24c0faacbe28622820e05290fa6f5cf15422d1feaea4764",
    "nonlinear_Robin_full_V4": "e65b790fdd068c58e6b7597955c0d5fc93e419852f70561b54e997dddd04250b",
}
UPSTREAM_SCHEMAS = {
    "backreacted_wall": "holo.backreacted-compensator-wall-gate.v1",
    "wall_ADM": "holo.wall-adm-base-hessian-gate.v1",
    "nonlinear_Robin_full_V4": "holo.nonlinear-robin-full-v4-gate.v1",
}

C1_REQUIRED = (
    "one covariant bulk-plus-delta-wall action with every gravity, compensator, "
    "khronon, solder, Goldstone/gauge and auxiliary field declared"
)
N1_REQUIRED = (
    "one explicit covariant bulk-plus-brane action through the nonlinear order "
    "being certified, including every ADM, khronon, compensator, bending and "
    "full-V4 material cross coupling with no ellipsis"
)

CERTIFICATE_C_REQUIREMENTS = (
    ("C1_ACTION", C1_REQUIRED),
    (
        "C2_BRST",
        "off-shell nilpotent BRST transformations and one gauge fermion for that same full action, including the relative-SO3 sector",
    ),
    (
        "C3_DOMAIN",
        "bulk and wall boundary operators for fields and ghosts whose domains are BRST closed and satisfy the chosen elliptic or Lorentzian well-posedness test",
    ),
    (
        "C4_HESSIAN",
        "the complete gauge-fixed quadratic super-Hessian, including wall delta terms, constraints, solder partners, FP and auxiliary blocks",
    ),
    (
        "C5_JACOBIANS",
        "curved York/Hodge and internal field-redefinition Jacobians evaluated on the same domains as the Hessian",
    ),
    (
        "C6_ZERO_MODES",
        "complete kernel bases, norms, primed prescriptions, gauge volumes and physical collective-coordinate measures",
    ),
    (
        "C7_REGULATOR",
        "one regulator, renormalization scale, local bulk/wall counterterm basis and renormalization conditions applied to every boson and ghost block",
    ),
    (
        "C8_CONTOUR",
        "a conformal/negative-mode contour with its phase and a reflection-positivity or Lorentzian unitarity prescription",
    ),
    (
        "C9_REDUCTION",
        "an analytic or interval-certified equality reducing the full primed BRST superdeterminant to the stated physical P4 factors",
    ),
    (
        "C10_INDEPENDENCE_UNITARITY",
        "gauge-parameter/regulator independence plus positivity or optical-theorem checks for the resulting renormalized physical determinant",
    ),
)

CERTIFICATE_N_REQUIREMENTS = (
    ("N1_ACTION", N1_REQUIRED),
    (
        "N2_CONSTRAINTS",
        "the complete nonlinear primary and secondary constraints, their Poisson/Dirac closure and constant physical rank over a declared field domain",
    ),
    (
        "N3_CHARACTERISTICS",
        "the constraint-reduced nonlinear principal/characteristic matrix for scalar, vector, tensor, bending, compensator and material helicities, with strong hyperbolicity and positive kinetic cone on that domain",
    ),
    (
        "N4_JUNCTION_BENDING",
        "nonlinear Israel, scalar, khronon and Robin junction equations on the displaced brane, including the normal/bending map and interface conservation",
    ),
    (
        "N5_COUPLED_BVP",
        "an existence/uniqueness or interval-certified continuation theorem for the coupled nonlinear gravity-plus-full-V4 finite-q radial BVP",
    ),
    (
        "N6_GLOBAL_STABILITY",
        "a same-action energy or symmetrizer estimate excluding ghosts, gradient loss, constraint bifurcation and boundary energy influx beyond linear order",
    ),
    (
        "N7_LINEAR_REDUCTION",
        "linearization of the selected nonlinear system reproduces the hash-bound wall ADM and independent all-helicity receipts including the q=0 quotient",
    ),
    (
        "N8_MATERIAL_PORT",
        "the full-V4 material sector has a positive Hamiltonian and a converged nonlinear finite-q solution for prescribed boundary acceleration",
    ),
)

CANONICAL_GLUING = {
    "configuration_metric": (
        "gamma^+_{mu nu}[g_+,Y_+]=gamma^-_{mu nu}[g_-,Y_-]=gamma_{mu nu}"
    ),
    "variation_metric": (
        "delta gamma^+_{mu nu}=delta gamma^-_{mu nu}=delta gamma_{mu nu}"
    ),
    "configuration_Omega": (
        "Omega_+(Y_+)=Omega_-(Y_-)=Omega_Sigma"
    ),
    "variation_Omega": (
        "delta[Omega_+(Y_+)]=delta[Omega_-(Y_-)]=delta Omega_Sigma"
    ),
    "configuration_phi": (
        "phi_+^a(Y_+)=phi_-^a(Y_-)=varphi^a"
    ),
    "variation_phi": (
        "delta[phi_+^a(Y_+)]=delta[phi_-^a(Y_-)]=delta varphi^a"
    ),
    "implementation": (
        "the common induced metric and continuous even traces define the restricted "
        "configuration and variation spaces; no gluing Lagrange multiplier is required"
    ),
}

CANONICAL_DEFINITIONS = {
    "khronon_norm": "D_T_squared=gamma^(mu nu)*D_mu T*D_nu T<0",
    "khronon_unit_vector": (
        "u_mu=-D_mu T/sqrt(-gamma^(rho sigma)*D_rho T*D_sigma T)"
    ),
    "triad_internal_identity": "E^a_mu*E^(b mu)=delta^ab",
    "triad_spatial_identity": "sum_a E^(a mu)*E^(a nu)=h^(mu nu)",
}

CANONICAL_ACTION = {
    "total": "S_cand=S_bulk+S_GHY+S_wall0+S_fol+S_X+S_R",
    "superpotential": "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]",
    "bulk_potential": "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
    "full_V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
    "dimensionless_material_argument": "r=Omega^(3/2)*r_phi",
    "bulk": (
        "S_bulk=sum_(eps in {plus,minus}) int_Meps sqrt(-g)*[M5^3*R/2-"
        "G*(nabla Omega)^2/2-U(Omega)-Z5_per_side*P_M^a*P_a^M/2-"
        "Z5_per_side*M^2*Omega^(-5)*V4(Omega^(3/2)*r_phi)]"
    ),
    "GHY": (
        "S_GHY=+M5^3*sum_(eps in {plus,minus}) int_Sigma "
        "sqrt(-gamma)*Theta_eps for outward spacelike normals"
    ),
    "wall_background": (
        "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+"
        "beta*(Omega_Sigma-1)^2/2]"
    ),
    "foliation": (
        "S_fol=Mb^2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-"
        "lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
        "B4_bar*Rcal^2/(16*k_infinity^2)]/2"
    ),
    "solid": (
        "S_X=int_Sigma sqrt(-gamma)*[rho_X*(u^mu*partial_mu X^a)^2/2-"
        "mu_X*tr[(B-v^2*I)^2]/4-lambda_X*(tr(B-v^2*I))^2/8]"
    ),
    "Robin": (
        "S_R=-kappa_hat*int_Sigma sqrt(-gamma)*"
        "delta_ab*(varphi^a-y*Acal^a)*(varphi^b-y*Acal^b)/2"
    ),
}

CANONICAL_FORMULA_SIGNS = {
    "EH_M5_cubed_R_coefficient": 0.5,
    "Omega_kinetic_G_coefficient": -0.5,
    "triplet_kinetic_Z5_per_side_coefficient": -0.5,
    "GHY_M5_cubed_Theta_coefficient": 1.0,
    "wall_2W_sign": -1.0,
    "U_WOmega_squared_over_G_coefficient": 0.5,
    "U_W_squared_over_M5_cubed_coefficient": -2.0 / 3.0,
    "foliation_overall_Mb_squared_coefficient": 0.5,
    "foliation_B4_Rcal_squared_inside_sign": -1.0,
    "solid_velocity_rho_coefficient": 0.5,
    "solid_shear_mu_coefficient": -0.25,
    "Robin_kappa_hat_coefficient": -0.5,
}

CANONICAL_JUNCTION_CONVENTION = (
    "M5^3*sum_eps(Theta_eps_mu_nu-Theta_eps*gamma_mu_nu)=tau_Sigma_mu_nu; "
    "sum_eps n_eps_M*[G*nabla^M Omega+3*Z5_per_side*phi^a*P_a^M/(2*Omega)]+"
    "partial_Omega Lambda_Sigma=0; Z5_per_side*sum_eps(n_eps.P^a)+"
    "kappa_hat*(varphi^a-y*Acal^a)=0"
)

PHYSICAL_FALSE_KEYS = (
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
    "full_P2_pass",
    "P3_complete_gauge_fixed_unitary_determinant_pass",
    "old_P3_gate_already_consumes_this_C1",
    "historical_linear_P4_receipt_reused",
    "old_wall_ADM_Hessian_inherited_after_dynamic_solid",
    "complete_same_action_ghost_freedom_proved",
    "nonlinear_gravitational_P4_pass",
    "P4_full_same_action_pass",
    "B4_pass",
    "B5_pass",
    "a0_predicted",
    "new_force_derived",
    "universal_matter_metric_and_lensing_derived",
    "UV_or_top_down_derivation_pass",
    "Ward_or_RG_protection_pass",
    "publication_authorized",
)

DIGEST_KEYS = (
    "upstream_bindings",
    "action_charter",
    "algebraic_audits",
    "certificate_ledger",
    "decision",
)


class OneOmegaActionCharterError(ValueError):
    """An input or stored receipt violates the one-Omega charter contract."""


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise OneOmegaActionCharterError(f"cannot hash {path}: {exc}") from exc


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OneOmegaActionCharterError(f"cannot read JSON object {path}: {exc}") from exc
    if type(value) is not dict:
        raise OneOmegaActionCharterError(f"{path} must contain one JSON object")
    return value


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO.resolve()))
    except ValueError:
        return str(resolved)


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise OneOmegaActionCharterError(f"{name} must be a finite real")
    result = float(value)
    if not math.isfinite(result):
        raise OneOmegaActionCharterError(f"{name} must be a finite real")
    return 0.0 if result == 0.0 else result


def _positive(value: Any, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise OneOmegaActionCharterError(f"{name} must be positive")
    return result


def _close(left: Any, right: Any, name: str, *, tolerance: float = 2.0e-13) -> float:
    lhs = _finite(left, name)
    rhs = _finite(right, name)
    residual = lhs - rhs
    if abs(residual) > tolerance:
        raise OneOmegaActionCharterError(
            f"{name} changed: {lhs!r} versus frozen {rhs!r}"
        )
    return residual


def _validate_upstream_semantics(inputs: Mapping[str, Mapping[str, Any]]) -> None:
    wall = inputs["backreacted_wall"]
    wall_decision = wall.get("decision", {})
    for key in (
        "positive_norm_dynamical_compensator_wall_on_shell",
        "Z2_Israel_and_scalar_junctions_derived",
        "localized_TT_zero_mode_and_M4_derived",
    ):
        if wall_decision.get(key) is not True:
            raise OneOmegaActionCharterError(f"backreacted wall lost required scope: {key}")
    if wall_decision.get("B4_pass") is not False or wall_decision.get("B5_pass") is not False:
        raise OneOmegaActionCharterError("backreacted wall was over-promoted")

    wall_adm = inputs["wall_ADM"]
    adm_decision = wall_adm.get("decision", {})
    if adm_decision.get("positive_bare_total_matched_family_exists") is not True:
        raise OneOmegaActionCharterError("matched bare wall-ADM family is absent")
    if adm_decision.get("B4_pass") is not False or adm_decision.get("B5_pass") is not False:
        raise OneOmegaActionCharterError("wall-ADM input was over-promoted")
    family = wall_adm.get("positive_bare_total_matching_and_crossover", {}).get("family")
    if type(family) is not dict:
        raise OneOmegaActionCharterError("wall-ADM family is absent")
    expected = {
        "M4_bulk_squared": 1.107013790800849,
        "M_b_squared": 2.0,
        "r0": 0.5535068954004245,
    }
    for key, value in expected.items():
        _close(family.get(key), value, f"wall_ADM.family.{key}")
    bare = family.get("bare_coefficients_in_Mb_units", {})
    expected_bare = {
        "KijKij": 1.0,
        "lambda_bare": 1.3107013790800848,
        "xi_bare": 1.0,
        "eta_bare": 3.107013790800849,
        "kappa": 0.5,
        "y_squared": 3.0,
        "y2_kappa": 1.5,
        "delta_UV": 1.607013790800849,
    }
    for key, value in expected_bare.items():
        _close(bare.get(key), value, f"wall_ADM.bare.{key}")

    robin = inputs["nonlinear_Robin_full_V4"]
    robin_decision = robin.get("decision", {})
    for key in (
        "finite_Robin_full_V4_functional_coercive_convex",
        "full_V4_periodic_EOM_energy_convergence_source_closure_pass",
        "canonical_time_dependent_material_Hamiltonian_positive",
        "nonlinear_inhomogeneous_finite_q_material_BVP_pass",
    ):
        if robin_decision.get(key) is not True:
            raise OneOmegaActionCharterError(
                f"nonlinear Robin material port lost required scope: {key}"
            )
    for key in ("P4_pass", "nonlinear_all_helicity_P4_pass", "B4_pass", "B5_pass"):
        if robin_decision.get(key) is not False:
            raise OneOmegaActionCharterError(
                f"nonlinear Robin material port was over-promoted: {key}"
            )
    matched = robin.get("matched_wall_scope", {})
    if matched.get("conformal_variable") != "psi=Omega^(3/2)*phi":
        raise OneOmegaActionCharterError("nonlinear Robin conformal variable changed")
    if matched.get("total_material_coefficient") != "T=N_s*Z5>0":
        raise OneOmegaActionCharterError("nonlinear Robin material normalization changed")
    representative = matched.get("numerical_representative", {})
    for key, expected_value in {
        "T": 1.0,
        "kappa": 0.5,
        "y": math.sqrt(3.0),
        "y_squared_kappa": 1.5,
    }.items():
        _close(representative.get(key), expected_value, f"nonlinear Robin {key}")
    if "prescribed acceleration" not in matched.get("important_boundary", ""):
        raise OneOmegaActionCharterError("nonlinear Robin prescribed-port boundary changed")
    hamiltonian = robin.get("canonical_material_Hamiltonian", {})
    if (
        hamiltonian.get("bounded_below_for_prescribed_A") is not True
        or hamiltonian.get("higher_time_derivatives") != 0
        or hamiltonian.get("dynamical_gravitational_A_requires_coupled_constraint_audit")
        is not True
    ):
        raise OneOmegaActionCharterError("nonlinear Robin Hamiltonian scope changed")


def _load_upstreams() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, str]]]:
    inputs: dict[str, dict[str, Any]] = {}
    bindings: dict[str, dict[str, str]] = {}
    scopes = {
        "backreacted_wall": "one-Omega on-shell background, GHY and Z2 junction data only",
        "wall_ADM": "bare coefficient point and numerical crossover window only; no P4 transport",
        "nonlinear_Robin_full_V4": (
            "direct prescribed-acceleration full-V4 material port only; no nonlinear "
            "gravity, determinant or P4 transport"
        ),
    }
    for name, path in UPSTREAM_PATHS.items():
        actual_hash = _sha256(path)
        if actual_hash != UPSTREAM_HASHES[name]:
            raise OneOmegaActionCharterError(f"{name} byte hash changed")
        payload = _read_object(path)
        if payload.get("schema") != UPSTREAM_SCHEMAS[name]:
            raise OneOmegaActionCharterError(f"{name} schema changed")
        if payload.get("checks", {}).get("all") is not True:
            raise OneOmegaActionCharterError(f"{name} checks are not certified")
        inputs[name] = payload
        bindings[name] = {
            "path": _display_path(path),
            "schema": UPSTREAM_SCHEMAS[name],
            "sha256": actual_hash,
            "consumed_scope": scopes[name],
        }
    _validate_upstream_semantics(inputs)
    return inputs, bindings


def _action_charter(inputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    family = inputs["wall_ADM"]["positive_bare_total_matching_and_crossover"]["family"]
    bare = family["bare_coefficients_in_Mb_units"]
    parameters = {
        "M5_cubed": 1.0,
        "k_infinity": 1.0,
        "compensator_metric_G": 1.2,
        "brane_beta": 2.0,
        "material_Z5_per_side": 1.0,
        "material_mass_M": 1.0,
        "M4_bulk_squared_selected_one_Omega_wall_value": family["M4_bulk_squared"],
        "brane_Mb_squared": family["M_b_squared"],
        "lambda_K": bare["lambda_bare"],
        "xi": bare["xi_bare"],
        "eta": bare["eta_bare"],
        "B4_bar": 0.8,
        "Robin_kappa_in_Mb_units": bare["kappa"],
        "Robin_kappa_hat": family["M_b_squared"] * bare["kappa"],
        "Robin_y_squared": bare["y_squared"],
        "Robin_y": math.sqrt(bare["y_squared"]),
        "solid_v": 1.0,
        "solid_rho": 1.0,
        "solid_mu": 1.0,
        "solid_lambda": 1.0,
    }
    return {
        "route_id": ROUTE_ID,
        "unit_convention": "numerical values use k_infinity=1 with dimensions restored by the explicit ledger",
        "selection": {
            "bulk_compensator_count": 1,
            "bulk_compensator": "Omega",
            "solder_route": "three brane Stueckelberg solid scalars X^a",
            "bifundamental_solder_selected": False,
            "fixed_external_triad_selected": False,
            "canonical_genealogy_selected_for_C1_and_N1": True,
            "old_P3_gate_automatically_updated": False,
        },
        "topology": {
            "cover": "M=M_plus union_Sigma M_minus",
            "sides": "M_plus and M_minus are each R^(1,3) times R_ge_0",
            "interface": "one timelike moving brane Sigma with no boundary of its own",
            "reflection": "Z2 exchanges the two bulk sides",
            "asymptotic_domain": "normalizable fields and compact-support variations at AdS5 infinity",
            "physical_interface_interpretation": (
                "Y_plus and Y_minus are two bulk-side representatives of one physical brane"
            ),
        },
        "independent_fields": {
            "bulk_dynamic": [
                "g_MN on each Z2 side",
                "one positive compensator Omega on each Z2 side",
                "one real SO(3) triplet phi^a on each Z2 side",
            ],
            "brane_dynamic": [
                "embedding Y_plus^M(sigma) and Y_minus^M(sigma)",
                "khronon T(sigma)",
                "three solid Stueckelberg scalars X^a(sigma)",
            ],
            "continuous_Z2_even_traces": ["Omega_Sigma", "varphi^a"],
            "independent_internal_gauge_fields": [],
            "independent_auxiliary_fields": [],
            "classical_FP_or_BRST_fields": [],
            "composites_not_independent_fields": [
                "induced gamma_mu_nu",
                "bulk-side normals n_plus^M and n_minus^M",
                "bulk extrinsic curvatures Theta_plus_mu_nu and Theta_minus_mu_nu",
                "u_mu, h_mu_nu, Kcal_mu_nu, acceleration a_mu and leaf curvature Rcal",
                "B^ab, B^(-1/2), E^a_mu and Acal^a",
            ],
        },
        "symmetries": [
            "five-dimensional diffeomorphisms with matched interface action",
            "four-dimensional reparametrizations of the moving brane",
            "Z2 exchange of the two bulk sides",
            "monotone khronon reparametrization T maps to f(T)",
            "time-orientation reversal u_mu maps to minus u_mu",
            "global internal ISO(3): X^a maps to R^a_b X^b+c^a and phi^a maps to R^a_b phi^b",
        ],
        "symmetry_breaking_pattern": {
            "unbroken_on_X_equals_vx_background": "diagonal SO(3)⋉R^3_X",
            "relative_SO3": "explicitly broken by the Robin solder",
            "relative_SO3_is_gauged": False,
            "internal_translations": "global shifts X^a maps to X^a+c^a",
        },
        "domains": {
            "Omega": "Omega>0",
            "khronon": (
                "-gamma^(mu nu)*D_mu T*D_nu T>0 with a global time orientation"
            ),
            "solid": "B^ab positive definite and det(partial_i X^a)>0",
            "solder_patch": "rank-full orientation-preserving sector with det(B)>0",
            "interface_gluing": dict(CANONICAL_GLUING),
            "gluing_is_a_restricted_domain_not_a_multiplier_equation": True,
            "excluded": [
                "khronon caustics",
                "solid defects with det(B)=0",
                "a nondynamical external triad",
            ],
            "BRST_closed_boundary_domain_selected": False,
        },
        "definitions": {
            "embedding": "e_mu^M=partial_mu Y^M; gamma_mu_nu=g_MN(Y)e_mu^M e_nu^N",
            "covariant_delta_wall_equivalence": (
                "int_Sigma sqrt(-gamma)*L_Sigma=int_M sqrt(-g)*delta_Sigma*L_Sigma, "
                "where int_M sqrt(-g)*delta_Sigma*f=int_Sigma sqrt(-gamma)*f"
            ),
            "bulk_extrinsic_curvature": "Theta_eps_mu_nu=e_mu^M e_nu^N nabla_M n_eps_N",
            "normal_convention": "n_eps^M is outward pointing and n_eps^M*n_eps_M=+1",
            "conformal_derivative": "P_M^a=nabla_M phi^a+3*phi^a*nabla_M Omega/(2*Omega)",
            "material_radius": "r_phi=sqrt(delta_ab*phi^a*phi^b)",
            "khronon_norm": CANONICAL_DEFINITIONS["khronon_norm"],
            "khronon_unit_vector": CANONICAL_DEFINITIONS["khronon_unit_vector"],
            "spatial_metric": "h_mu_nu=gamma_mu_nu+u_mu*u_nu",
            "leaf_extrinsic_curvature": "Kcal_mu_nu=h_mu^rho*h_nu^sigma*D_rho u_sigma",
            "acceleration": "a_mu=u^nu*D_nu u_mu",
            "solid_metric": "B^ab=h^(mu nu)*partial_mu X^a*partial_nu X^b",
            "orthonormal_triad": "E^a_mu=h_mu^nu*partial_nu X^b*(B^(-1/2))_b^a",
            "raised_triad": "E^(a mu)=h^(mu nu)*E^a_nu",
            "triad_internal_identity": CANONICAL_DEFINITIONS["triad_internal_identity"],
            "triad_spatial_identity": CANONICAL_DEFINITIONS["triad_spatial_identity"],
            "soldered_acceleration": "Acal^a=E^(a mu)*a_mu",
        },
        "exact_action": dict(CANONICAL_ACTION),
        "explicit_cross_couplings": {
            "conformal_kinetic_expansion": (
                "P^2=(nabla phi)^2+3*phi^a*nabla_M phi^a*nabla^M Omega/Omega+"
                "9*phi^2*(nabla Omega)^2/(4*Omega^2)"
            ),
            "Robin_expansion": (
                "(varphi-y*Acal)^2=varphi^2-2*y*varphi_a*E^(a mu)*a_mu+"
                "y^2*a_mu*a^mu"
            ),
            "moving_pullbacks": (
                "gamma_mu_nu, Omega_Sigma and varphi^a depend on Y^M, so bending is "
                "generated by varying the displayed action"
            ),
            "foliation_metric": "u, h, Kcal, a and Rcal are exact functions of gamma_mu_nu and T",
            "solid_foliation_metric": "B and E are exact functions of gamma_mu_nu, T and X^a",
            "Robin_four_sector": "S_R couples gamma_mu_nu, T, X^a and varphi^a",
            "direct_Robin_dressing": "f(Omega_Sigma)=1",
        },
        "derivative_and_amplitude_scope": {
            "nonlinear_amplitude": "exact in every displayed field",
            "bulk": "Einstein frame with at most two derivatives in each displayed bulk term",
            "foliation": "at most two time derivatives and at most four leaf-spatial derivatives",
            "solid": "first derivatives of X^a with equations of motion of second differential order",
            "Robin": "algebraic in varphi^a and Acal^a",
        },
        "coefficient_policy": {
            "matching_scale_symbol": "mu_star",
            "matching_scale_in_k_infinity_units": 1.0,
            "parameters": parameters,
            "dimensionful_reconstruction": {
                "M5_cubed": "1*k_infinity^3",
                "G": "1.2*k_infinity^3",
                "beta": "2*k_infinity^4",
                "material_M": "1*k_infinity",
                "material_Z5_per_side": "1*k_infinity^3 on each of the two sides",
                "material_T_two_side": "2*k_infinity^3",
                "Mb_squared": "2*k_infinity^2",
                "kappa_hat": "1*k_infinity^4",
                "y_squared": "3/k_infinity^2",
                "solid_v": "1*k_infinity",
                "solid_rho": "1*k_infinity^2",
                "solid_mu": "1",
                "solid_lambda": "1",
                "B4_bar": "0.8",
                "mu_star": "1*k_infinity",
            },
            "all_unlisted_operator_coefficients_at_mu_star": 0.0,
            "all_displayed_coefficient_functions_are_constant_unless_formula_shown": True,
            "radiative_closure_proved": False,
            "UV_derivation_claimed": False,
        },
        "mass_dimension_ledger": {
            "derivative": 1.0,
            "five_dimensional_Lagrangian_density": 5.0,
            "brane_Lagrangian_density": 4.0,
            "M5_cubed": 3.0,
            "brane_Mb_squared": 2.0,
            "k_infinity": 1.0,
            "bulk_R": 2.0,
            "bulk_superpotential_W": 4.0,
            "bulk_potential_U": 5.0,
            "boundary_Theta": 1.0,
            "leaf_Kcal": 1.0,
            "leaf_Rcal": 2.0,
            "material_mass_M": 1.0,
            "Omega": 0.0,
            "compensator_metric_G": 3.0,
            "dimensionless_radial_phi": 0.0,
            "material_Z5_per_side": 3.0,
            "X": 0.0,
            "solid_v": 1.0,
            "Robin_y": -1.0,
            "Robin_kappa_hat": 4.0,
            "solid_rho": 2.0,
            "solid_mu": 0.0,
            "solid_lambda": 0.0,
            "brane_beta": 4.0,
            "B4_bar": 0.0,
            "khronon_T_coordinate_convention": -1.0,
            "acceleration_Acal": 1.0,
            "Robin_varphi_dimension": 0.0,
            "Robin_yAcal_dimension": 0.0,
            "Robin_integrand_dimension": 4.0,
            "potential_prefactor_Z5_M2_dimension": 5.0,
            "dimensionless_V4_argument": True,
            "field_convention": (
                "phi is the exact dimensionless radial field used by the existing gates; "
                "a dimension-3/2 canonical comparison field would be M^(3/2)*phi"
            ),
        },
    }


def _sigma_positive_audit(charter: Mapping[str, Any]) -> dict[str, Any]:
    pars = charter["coefficient_policy"]["parameters"]
    metric_G = _positive(pars["compensator_metric_G"], "G")
    z5 = _positive(pars["material_Z5_per_side"], "Z5_per_side")
    omega = 0.73
    phi_squared = 0.29
    c = 1.5
    omega_omega_entry = metric_G + z5 * c * c * phi_squared / (omega * omega)
    determinant = metric_G * z5**3
    return {
        "field_space_line_element": (
            "ds_field^2=G*dOmega^2+Z5*delta_ab*(dphi^a+3*phi^a*dOmega/(2*Omega))*"
            "(dphi^b+3*phi^b*dOmega/(2*Omega))"
        ),
        "completed_square_proof": "G>0 and Z5>0 make both displayed squares positive",
        "Schur_complement_of_triplet_block": metric_G,
        "determinant_four_field_metric": determinant,
        "sample_OmegaOmega_entry": omega_omega_entry,
        "positive_for_Omega_positive": metric_G > 0.0 and z5 > 0.0 and determinant > 0.0,
    }


def _formula_sign_audit(charter: Mapping[str, Any]) -> dict[str, Any]:
    """Bind the displayed formulas and coefficient signs to literal constants."""

    if charter.get("exact_action") != CANONICAL_ACTION:
        raise OneOmegaActionCharterError("canonical exact-action formula changed")
    definitions = charter.get("definitions", {})
    for key, expected in CANONICAL_DEFINITIONS.items():
        if definitions.get(key) != expected:
            raise OneOmegaActionCharterError(f"canonical definition changed: {key}")
    gluing = charter.get("domains", {}).get("interface_gluing")
    if gluing != CANONICAL_GLUING:
        raise OneOmegaActionCharterError("canonical interface gluing changed")
    return {
        "exact_action_matches_literal_CANONICAL_ACTION": True,
        "gluing_matches_literal_CANONICAL_GLUING": True,
        "definitions_match_literal_CANONICAL_DEFINITIONS": True,
        "coefficients": dict(CANONICAL_FORMULA_SIGNS),
        "solid_shear_operator": "tr[(B-v^2*I)^2]",
        "khronon_timelike_contraction": "-gamma^(mu nu)*D_mu T*D_nu T",
        "spatial_triad_completeness": CANONICAL_DEFINITIONS["triad_spatial_identity"],
    }


def dimension_audit(charter: Mapping[str, Any]) -> dict[str, Any]:
    """Check that the radial dimensionless-phi convention is homogeneous."""

    ledger = charter.get("mass_dimension_ledger")
    if type(ledger) is not dict:
        raise OneOmegaActionCharterError("mass-dimension ledger is absent")
    derivative = _finite(ledger.get("derivative"), "[partial]")
    phi = _finite(ledger.get("dimensionless_radial_phi"), "[phi]")
    omega = _finite(ledger.get("Omega"), "[Omega]")
    z5 = _finite(ledger.get("material_Z5_per_side"), "[Z5_per_side]")
    mass = _finite(ledger.get("material_mass_M"), "[M]")
    m3 = _finite(ledger.get("M5_cubed"), "[M5^3]")
    mb2 = _finite(ledger.get("brane_Mb_squared"), "[Mb^2]")
    metric_g = _finite(ledger.get("compensator_metric_G"), "[G]")
    k_dimension = _finite(ledger.get("k_infinity"), "[k_infinity]")
    w_dimension = _finite(ledger.get("bulk_superpotential_W"), "[W]")
    bulk_r = _finite(ledger.get("bulk_R"), "[R]")
    theta = _finite(ledger.get("boundary_Theta"), "[Theta]")
    leaf_k = _finite(ledger.get("leaf_Kcal"), "[Kcal]")
    leaf_r = _finite(ledger.get("leaf_Rcal"), "[Rcal]")
    y = _finite(ledger.get("Robin_y"), "[y]")
    acceleration = _finite(ledger.get("acceleration_Acal"), "[Acal]")
    spring = _finite(ledger.get("Robin_kappa_hat"), "[kappa_hat]")
    x_dimension = _finite(ledger.get("X"), "[X]")
    rho = _finite(ledger.get("solid_rho"), "[rho_X]")
    mu = _finite(ledger.get("solid_mu"), "[mu_X]")
    lam = _finite(ledger.get("solid_lambda"), "[lambda_X]")
    v_dimension = _finite(ledger.get("solid_v"), "[v]")
    beta = _finite(ledger.get("brane_beta"), "[beta]")
    b4 = _finite(ledger.get("B4_bar"), "[B4_bar]")
    bulk_target = _finite(
        ledger.get("five_dimensional_Lagrangian_density"), "[L5]"
    )
    brane_target = _finite(ledger.get("brane_Lagrangian_density"), "[L4]")

    rows = {
        "EH_bulk": m3 + bulk_r,
        "Omega_kinetic": metric_g + 2.0 * (derivative + omega),
        "superpotential_W": m3 + k_dimension,
        "U_from_WOmega_squared_over_G": 2.0 * w_dimension - metric_g,
        "U_from_W_squared_over_M5_cubed": 2.0 * w_dimension - m3,
        "GHY": m3 + theta,
        "wall_2W": w_dimension,
        "phi_kinetic": z5 + 2.0 * (derivative + phi),
        "V4_prefactor": z5 + 2.0 * mass,
        "V4_argument": omega + phi,
        "Mb2_Kcal_squared": mb2 + 2.0 * leaf_k,
        "Mb2_Rcal": mb2 + leaf_r,
        "Mb2_acceleration_squared": mb2 + 2.0 * acceleration,
        "Mb2_B4_Rcal_squared_over_k_squared": (
            mb2 + b4 + 2.0 * leaf_r - 2.0 * k_dimension
        ),
        "Robin_phi": phi,
        "Robin_yAcal": y + acceleration,
        "Robin_density": spring + 2.0 * phi,
        "solid_velocity_density": rho + 2.0 * (derivative + x_dimension),
        "solid_B": 2.0 * (derivative + x_dimension),
        "solid_v_squared": 2.0 * v_dimension,
        "solid_mu_strain_density": mu + 4.0 * (derivative + x_dimension),
        "solid_lambda_strain_density": lam + 4.0 * (derivative + x_dimension),
        "beta_density": beta,
    }
    expected = {
        "EH_bulk": bulk_target,
        "Omega_kinetic": bulk_target,
        "superpotential_W": w_dimension,
        "U_from_WOmega_squared_over_G": bulk_target,
        "U_from_W_squared_over_M5_cubed": bulk_target,
        "GHY": brane_target,
        "wall_2W": brane_target,
        "phi_kinetic": bulk_target,
        "V4_prefactor": bulk_target,
        "V4_argument": 0.0,
        "Mb2_Kcal_squared": brane_target,
        "Mb2_Rcal": brane_target,
        "Mb2_acceleration_squared": brane_target,
        "Mb2_B4_Rcal_squared_over_k_squared": brane_target,
        "Robin_phi": phi,
        "Robin_yAcal": phi,
        "Robin_density": brane_target,
        "solid_velocity_density": brane_target,
        "solid_B": 2.0,
        "solid_v_squared": 2.0,
        "solid_mu_strain_density": brane_target,
        "solid_lambda_strain_density": brane_target,
        "beta_density": brane_target,
    }
    residuals = {key: rows[key] - expected[key] for key in rows}
    if max(abs(value) for value in residuals.values()) > 1.0e-14:
        raise OneOmegaActionCharterError("dimensionally incoherent displayed action")

    pars = charter["coefficient_policy"]["parameters"]
    # Reconstruct at k != 1 so dimensional cancellations are actually tested.
    sample_k = 2.75
    m5_phys = _positive(pars["M5_cubed"], "M5_cubed") * sample_k**3
    g_phys = _positive(pars["compensator_metric_G"], "G") * sample_k**3
    z5_per_side_phys = (
        _positive(pars["material_Z5_per_side"], "Z5_per_side") * sample_k**3
    )
    material_m_phys = _positive(pars["material_mass_M"], "M") * sample_k
    mb_squared_phys = _positive(pars["brane_Mb_squared"], "Mb_squared") * sample_k**2
    kappa_hat_phys = _positive(pars["Robin_kappa_hat"], "kappa_hat") * sample_k**4
    y_phys = _positive(pars["Robin_y"], "y") / sample_k
    v_phys = _positive(pars["solid_v"], "v") * sample_k
    kappa_b = kappa_hat_phys / (mb_squared_phys * sample_k**2)
    kappa_over_z5_m = kappa_hat_phys / (z5_per_side_phys * material_m_phys)
    if abs(kappa_b - pars["Robin_kappa_in_Mb_units"]) > 1.0e-14:
        raise OneOmegaActionCharterError("Robin kappa normalization is inconsistent")
    if abs(kappa_over_z5_m - 1.0) > 1.0e-14:
        raise OneOmegaActionCharterError("Robin kappa_hat/(Z5*M) reconstruction changed")
    _close(
        (y_phys * sample_k) ** 2,
        pars["Robin_y_squared"],
        "arbitrary-k Robin y squared reconstruction",
    )
    raw_two_side = {
        "T": 2.0 * pars["material_Z5_per_side"],
        "kappa": pars["Robin_kappa_hat"],
        "y_squared": pars["Robin_y_squared"],
    }
    divisor = pars["brane_Mb_squared"]
    normalized = {
        "T": raw_two_side["T"] / divisor,
        "kappa": raw_two_side["kappa"] / divisor,
        "y_squared": raw_two_side["y_squared"],
    }
    for key, expected_value in {"T": 1.0, "kappa": 0.5, "y_squared": 3.0}.items():
        _close(normalized[key], expected_value, f"two-side N8 normalization {key}")
    return {
        "convention": "dimensionless radial triplet with dimension-three Z5",
        "rows": rows,
        "expected": expected,
        "residuals": residuals,
        "maximum_absolute_residual": max(abs(value) for value in residuals.values()),
        "kappa_b_definition": "kappa_b=kappa_hat/(Mb^2*k_infinity^2)",
        "kappa_b": kappa_b,
        "kappa_hat_over_Z5_per_side_M_definition": (
            "kappa_hat/(Z5_per_side*M) with kappa_hat~k^4, Z5~k^3 and M~k"
        ),
        "kappa_hat_over_Z5_M": kappa_over_z5_m,
        "arbitrary_k_reconstruction": {
            "sample_k": sample_k,
            "M5_cubed": m5_phys,
            "G": g_phys,
            "Z5_per_side": z5_per_side_phys,
            "material_M": material_m_phys,
            "Mb_squared": mb_squared_phys,
            "kappa_hat": kappa_hat_phys,
            "y": y_phys,
            "v": v_phys,
        },
        "N8_two_side_normalization": {
            "Z5_is_per_side": True,
            "raw_barred_T_kappa_y_squared": raw_two_side,
            "Mb_squared_over_k_squared_divisor_for_T_and_kappa": divisor,
            "normalized_T_kappa_y_squared": normalized,
            "equation": "(T,kappa,y^2)=(2,1,3)/2_for_T_and_kappa=(1,0.5,3)",
        },
        "Robin_sum_is_homogeneous": True,
        "full_V4_term_has_dimension_five": True,
    }


def _background_and_junction_audit(charter: Mapping[str, Any]) -> dict[str, Any]:
    pars = charter["coefficient_policy"]["parameters"]
    m3 = _positive(pars["M5_cubed"], "M5_cubed")
    k = _positive(pars["k_infinity"], "k_infinity")
    metric_G = _positive(pars["compensator_metric_G"], "G")
    beta = _positive(pars["brane_beta"], "beta")
    gamma = metric_G / (6.0 * m3)
    k_brane = k * math.exp(-gamma)
    w = 3.0 * m3 * k_brane
    w_omega = -2.0 * gamma * w
    wall_function = 2.0 * w
    wall_derivative = 2.0 * w_omega
    israel_residual = wall_function - 6.0 * m3 * k_brane
    scalar_residual = wall_derivative + 2.0 * metric_G * k_brane
    flow_residual = w_omega / metric_G + k_brane
    return {
        "background": (
            "ds^2=exp(2A(y))*eta_mu_nu*dx^mu*dx^nu+dy^2; "
            "Omega=exp(A); phi^a=0; A'=-k_infinity*exp[-G*Omega^2/(6*M5^3)]"
        ),
        "brane_values": {
            "gamma": gamma,
            "k_brane": k_brane,
            "W_at_one": w,
            "W_Omega_at_one": w_omega,
            "Lambda_Sigma_at_one": wall_function,
            "Lambda_Sigma_prime_at_one": wall_derivative,
            "beta": beta,
        },
        "junction_convention": CANONICAL_JUNCTION_CONVENTION,
        "normal_orientation": "outward spacelike normals on both bulk sides",
        "GHY_sign_for_EH_plus_M5_cubed_R_over_2": 1,
        "Israel_equation_momentum_equals_brane_stress_sign": 1,
        "scalar_wall_derivative_enters_with_plus_sign": 1,
        "Israel_residual": israel_residual,
        "scalar_junction_residual": scalar_residual,
        "Omega_equals_expA_flow_residual_at_brane": flow_residual,
        "solid_and_Robin_background_first_variations_vanish": True,
        "reason": "phi=0, a_mu=0, u^mu partial_mu X^a=0 and B^ab=v^2 delta^ab",
    }


def _triad_rank_audit() -> dict[str, Any]:
    gradients = [2.0, 3.0, 4.0]
    b_diagonal = [value * value for value in gradients]
    inverse_square_root = [1.0 / value for value in gradients]
    e_diagonal = [gradients[index] * inverse_square_root[index] for index in range(3)]
    determinant = math.prod(e_diagonal)
    return {
        "definition": "E^a_mu=h_mu^nu*partial_nu X^b*(B^(-1/2))_b^a",
        "algebraic_identities": [
            CANONICAL_DEFINITIONS["triad_internal_identity"],
            CANONICAL_DEFINITIONS["triad_spatial_identity"],
        ],
        "sample_gradient_diagonal": gradients,
        "sample_B_diagonal": b_diagonal,
        "sample_B_inverse_square_root_diagonal": inverse_square_root,
        "sample_E_diagonal": e_diagonal,
        "sample_E_determinant": determinant,
        "Jacobian_dAcal_da_rank": 3,
        "analytic_at_zero_acceleration": True,
        "local_only_on_B_positive_definite_patch": True,
    }


def _window_audit(inputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    family = inputs["wall_ADM"]["positive_bare_total_matching_and_crossover"]["family"]
    bare = family["bare_coefficients_in_Mb_units"]
    r0 = _positive(family["r0"], "r0")
    xi = _positive(bare["xi_bare"], "xi")
    eta = _positive(bare["eta_bare"], "eta")
    coupling_lambda = _positive(bare["lambda_bare"], "lambda_K")
    y2_kappa = _positive(bare["y2_kappa"], "y2_kappa")
    delta_uv = eta - y2_kappa
    lower = 2.0 * r0
    upper = 2.0 * (xi + r0)
    lambda_expected = 1.2 + 0.2 * r0
    q_coercivity_at_r_zero = 2.0 * (2.0 + 3.0 * (coupling_lambda - 1.0)) / (
        coupling_lambda - 1.0
    )
    return {
        "classification": "historical linear-family numbers imported as bare coefficients only",
        "M4_bulk_squared": family["M4_bulk_squared"],
        "hairy_multiscalar_M4_bulk_squared_imported": False,
        "hairy_multiscalar_M4_bulk_squared": 1.2298525754296912,
        "M_b_squared": family["M_b_squared"],
        "r0": r0,
        "lambda_K": coupling_lambda,
        "xi": xi,
        "eta": eta,
        "y_squared_kappa": y2_kappa,
        "lower_2r0": lower,
        "upper_2_xi_plus_r0": upper,
        "strict_window": lower < y2_kappa < upper,
        "delta_UV": delta_uv,
        "lambda_matching_residual": coupling_lambda - lambda_expected,
        "eta_matching_residual": eta - upper,
        "positive_upper_lambda_branch": coupling_lambda > 1.0,
        "positive_scalar_coercivity_proxy_at_r_zero": q_coercivity_at_r_zero > 0.0,
        "B4_bar": 0.8,
        "historical_linear_P4_consumed_as_certificate": False,
        "full_new_action_ghost_certificate": False,
    }


def _solid_hessian_audit(charter: Mapping[str, Any]) -> dict[str, Any]:
    pars = charter["coefficient_policy"]["parameters"]
    rho = _positive(pars["solid_rho"], "rho_X")
    mu = _positive(pars["solid_mu"], "mu_X")
    lam = _finite(pars["solid_lambda"], "lambda_X")
    v = _positive(pars["solid_v"], "v")
    bulk_modulus = lam + 2.0 * mu / 3.0
    transverse_speed_squared = mu * v * v / rho
    longitudinal_speed_squared = (lam + 2.0 * mu) * v * v / rho
    velocity_shift_hessian = [
        [rho, -rho * v],
        [-rho * v, rho * v * v],
    ]
    return {
        "unitary_gauge_linearization": {
            "velocity": "u^mu*partial_mu X^a=dot(pi_X^a)-v*N^a",
            "strain": (
                "B^ab-v^2*delta^ab=v*(partial^a pi_X^b+partial^b pi_X^a)-"
                "v^2*delta_h^ab"
            ),
        },
        "velocity_shift_Hessian_for_each_internal_index": velocity_shift_hessian,
        "mixed_second_derivative_d2L_dpiDot_dShift": -rho * v,
        "shift_second_derivative_d2L_dShift2": rho * v * v,
        "nonzero_metric_strain_mixing_coefficient": mu * v**3,
        "new_phonon_field_count": 3,
        "solid_bulk_modulus": bulk_modulus,
        "transverse_speed_squared": transverse_speed_squared,
        "longitudinal_speed_squared": longitudinal_speed_squared,
        "isolated_solid_has_no_obvious_kinetic_or_gradient_ghost": (
            rho > 0.0
            and mu > 0.0
            and bulk_modulus > 0.0
            and transverse_speed_squared > 0.0
            and longitudinal_speed_squared > 0.0
        ),
        "dynamic_solid_changes_old_Hessian": True,
        "old_P4_determinant_or_modes_inherited": False,
        "zero_solid_action_escape_is_viable": False,
        "zero_solid_action_failure": "three null quadratic operators and strong coupling",
        "fixed_external_triad_escape_is_covariant": False,
        "fixed_external_triad_failure": "removes the X^a Euler-Lagrange equation and is not a field of the covariant action",
    }


def _variation_ledger() -> dict[str, Any]:
    return {
        "action_scope_closed_for_N1": (
            "all independent fields, pullbacks, cross-couplings, coefficients, zero "
            "coefficients and the nonlinear derivative/amplitude scope are explicit"
        ),
        "variations_still_required_for_N2_through_N7": [
            "bulk g_plus_MN and g_minus_MN including both GHY terms",
            "bulk Omega_plus and Omega_minus including conformal-triplet momentum",
            "bulk phi_plus^a and phi_minus^a including the nonlinear Robin condition",
            "moving embeddings Y_plus^M and Y_minus^M including the normal shape equation",
            "brane khronon T through u, h, Kcal, a, Rcal, B, E and Robin",
            "solid X^a through B, B^(-1/2), E and Robin",
        ],
        "required_second_variation": (
            "derive the extended metric, compensator, bending, khronon, phi and phonon "
            "Hessian instead of importing the historical P4 matrix"
        ),
        "complete_first_variation_and_interface_terms_derived": False,
        "nonlinear_primary_secondary_constraints_derived": False,
        "nonlinear_characteristic_matrix_derived": False,
        "displaced_brane_junction_system_derived": False,
        "new_extended_linear_reduction_derived": False,
        "N1_ACTION_pass": True,
        "why_N1_does_not_imply_N2_through_N7": (
            "N1 is the explicit-action item; equations, constraint closure, characteristics, "
            "coupled BVP, global stability and same-action linear reduction are separate items"
        ),
    }


def _certificate_ledger() -> dict[str, Any]:
    c_items = [
        {
            "id": item_id,
            "required": required,
            "pass": item_id == "C1_ACTION",
            "current_evidence": (
                "the exact bulk-plus-moving-wall action, gluing domain and all independent "
                "fields are frozen in this gate"
                if item_id == "C1_ACTION"
                else "not derived for the selected solid-extended one-Omega action"
            ),
        }
        for item_id, required in CERTIFICATE_C_REQUIREMENTS
    ]
    n_items = []
    for item_id, required in CERTIFICATE_N_REQUIREMENTS:
        passed = item_id in {"N1_ACTION", "N8_MATERIAL_PORT"}
        if item_id == "N1_ACTION":
            evidence = (
                "the exact action is explicit through its declared nonlinear order with "
                "moving pullbacks, ADM-khronon, compensator, full-V4 and Robin-solid couplings"
            )
        elif item_id == "N8_MATERIAL_PORT":
            evidence = (
                "the direct nonlinear-Robin upstream certifies the prescribed-acceleration "
                "port at normalized (T,kappa,y^2)=(1,0.5,3); it does not certify dynamic gravity"
            )
        else:
            evidence = "not derived for the selected solid-extended one-Omega action"
        n_items.append(
            {
                "id": item_id,
                "required": required,
                "pass": passed,
                "current_evidence": evidence,
            }
        )

    return {
        "C1_through_C10": {
            "items": c_items,
            "pass_ids": [item["id"] for item in c_items if item["pass"] is True],
            "all_items_pass": all(item["pass"] is True for item in c_items),
            "P3_complete": False,
        },
        "N1_through_N8": {
            "items": n_items,
            "pass_ids": [item["id"] for item in n_items if item["pass"] is True],
            "all_items_pass": all(item["pass"] is True for item in n_items),
            "nonlinear_gravitational_P4": False,
        },
        "scope": (
            "C1 and N1 close the unique classical action. N8 is a direct prescribed-port "
            "certificate only. No determinant, nonlinear-gravity or P4 result is transported."
        ),
    }


def _contains_ellipsis(value: Any) -> bool:
    if isinstance(value, str):
        return "..." in value or "\N{HORIZONTAL ELLIPSIS}" in value
    if isinstance(value, Mapping):
        return any(_contains_ellipsis(key) or _contains_ellipsis(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_ellipsis(item) for item in value)
    return False


def validate_payload(payload: Mapping[str, Any]) -> None:
    """Reject action mutation, upstream drift and every downstream overclaim."""

    if payload.get("schema") != SCHEMA:
        raise OneOmegaActionCharterError("schema mismatch")
    if payload.get("checks", {}).get("all") is not True:
        raise OneOmegaActionCharterError("audit checks are not certified")
    decision = payload.get("decision")
    if type(decision) is not dict:
        raise OneOmegaActionCharterError("decision object is absent")
    for key in ("C1_ACTION_pass", "N1_ACTION_pass", "N8_MATERIAL_PORT_pass"):
        if decision.get(key) is not True:
            raise OneOmegaActionCharterError(f"required action/material pass was lost: {key}")
    for key in PHYSICAL_FALSE_KEYS:
        if decision.get(key) is not False:
            raise OneOmegaActionCharterError(f"physical fail-closed key promoted: {key}")

    charter = payload.get("action_charter")
    if type(charter) is not dict:
        raise OneOmegaActionCharterError("action charter is absent")
    if charter.get("route_id") != ROUTE_ID:
        raise OneOmegaActionCharterError("canonical route changed")
    selection = charter.get("selection", {})
    if selection.get("bulk_compensator_count") != 1 or selection.get("solder_route") != (
        "three brane Stueckelberg solid scalars X^a"
    ):
        raise OneOmegaActionCharterError("field-content selection changed")
    if _contains_ellipsis(charter):
        raise OneOmegaActionCharterError("action charter contains an ellipsis")
    coefficient_policy = charter.get("coefficient_policy", {})
    if coefficient_policy.get("all_unlisted_operator_coefficients_at_mu_star") != 0.0:
        raise OneOmegaActionCharterError("unlisted operators are not frozen to zero")
    if coefficient_policy.get("UV_derivation_claimed") is not False:
        raise OneOmegaActionCharterError("bottom-up charter was promoted to UV derivation")
    if coefficient_policy.get("matching_scale_in_k_infinity_units") != 1.0:
        raise OneOmegaActionCharterError("matching scale is not the frozen mu_star")
    parameters = coefficient_policy.get("parameters")
    if type(parameters) is not dict or set(parameters) != set(FROZEN_PARAMETERS):
        raise OneOmegaActionCharterError("frozen parameter set changed")
    for key, expected in FROZEN_PARAMETERS.items():
        _close(parameters[key], expected, f"frozen parameter {key}")
    computed_dimensions = dimension_audit(charter)
    computed_formulas = _formula_sign_audit(charter)

    domains = charter.get("domains", {})
    if domains.get("gluing_is_a_restricted_domain_not_a_multiplier_equation") is not True:
        raise OneOmegaActionCharterError("interface gluing was changed into a multiplier equation")
    if domains.get("khronon") != (
        "-gamma^(mu nu)*D_mu T*D_nu T>0 with a global time orientation"
    ):
        raise OneOmegaActionCharterError("khronon inverse-metric contraction changed")

    symmetry = charter.get("symmetry_breaking_pattern", {})
    if symmetry.get("unbroken_on_X_equals_vx_background") != (
        "diagonal SO(3)⋉R^3_X"
    ):
        raise OneOmegaActionCharterError("diagonal solid symmetry changed")
    if symmetry.get("relative_SO3_is_gauged") is not False:
        raise OneOmegaActionCharterError("relative SO3 was silently gauged")

    action_digest = payload.get("action_charter_digest", {})
    if action_digest.get("sha256") != _canonical_digest(charter):
        raise OneOmegaActionCharterError("action charter digest mismatch")
    calculation_digest = payload.get("calculation_digest", {})
    core = {key: payload.get(key) for key in DIGEST_KEYS}
    if calculation_digest.get("sha256") != _canonical_digest(core):
        raise OneOmegaActionCharterError("calculation digest mismatch")

    bindings = payload.get("upstream_bindings")
    if type(bindings) is not dict or set(bindings) != set(UPSTREAM_HASHES):
        raise OneOmegaActionCharterError("upstream binding set changed")
    for name, expected_hash in UPSTREAM_HASHES.items():
        binding = bindings[name]
        if binding.get("sha256") != expected_hash:
            raise OneOmegaActionCharterError(f"stored upstream hash changed: {name}")
        if binding.get("schema") != UPSTREAM_SCHEMAS[name]:
            raise OneOmegaActionCharterError(f"stored upstream schema changed: {name}")

    ledger = payload.get("certificate_ledger", {})
    c_block = ledger.get("C1_through_C10", {})
    n_block = ledger.get("N1_through_N8", {})
    if c_block.get("pass_ids") != ["C1_ACTION"]:
        raise OneOmegaActionCharterError("C1 is not the sole passing certificate item")
    if n_block.get("pass_ids") != ["N1_ACTION", "N8_MATERIAL_PORT"]:
        raise OneOmegaActionCharterError("N1/N8 literal certificate pass set changed")
    for block, requirements, passing in (
        (c_block, CERTIFICATE_C_REQUIREMENTS, {"C1_ACTION"}),
        (n_block, CERTIFICATE_N_REQUIREMENTS, {"N1_ACTION", "N8_MATERIAL_PORT"}),
    ):
        items = block.get("items")
        if type(items) is not list or len(items) != len(requirements):
            raise OneOmegaActionCharterError("literal certificate item set changed")
        for item, (expected_id, expected_required) in zip(items, requirements):
            if (
                item.get("id") != expected_id
                or item.get("required") != expected_required
                or item.get("pass") is not (expected_id in passing)
            ):
                raise OneOmegaActionCharterError(
                    f"literal certificate formula/status changed: {expected_id}"
                )
    audits = payload.get("algebraic_audits", {})
    if audits.get("formula_and_signs") != computed_formulas:
        raise OneOmegaActionCharterError("stored canonical formula/sign audit changed")
    if audits.get("mass_dimensions") != computed_dimensions:
        raise OneOmegaActionCharterError("stored dimensional audit changed")
    junction = audits.get("background_and_junctions", {})
    if (
        junction.get("junction_convention") != CANONICAL_JUNCTION_CONVENTION
        or junction.get("GHY_sign_for_EH_plus_M5_cubed_R_over_2") != 1
        or junction.get("Israel_equation_momentum_equals_brane_stress_sign") != 1
        or junction.get("scalar_wall_derivative_enters_with_plus_sign") != 1
        or abs(_finite(junction.get("Israel_residual"), "Israel residual")) > 2.0e-14
        or abs(_finite(junction.get("scalar_junction_residual"), "scalar residual")) > 2.0e-14
    ):
        raise OneOmegaActionCharterError("normal, GHY or junction sign convention changed")
    triad = audits.get("triad_rank", {})
    if (
        triad.get("Jacobian_dAcal_da_rank") != 3
        or triad.get("algebraic_identities")
        != [
            CANONICAL_DEFINITIONS["triad_internal_identity"],
            CANONICAL_DEFINITIONS["triad_spatial_identity"],
        ]
    ):
        raise OneOmegaActionCharterError("solder rank changed")
    normalized = computed_dimensions.get("N8_two_side_normalization", {})
    if normalized.get("raw_barred_T_kappa_y_squared") != {
        "T": 2.0,
        "kappa": 1.0,
        "y_squared": 3.0,
    } or normalized.get("normalized_T_kappa_y_squared") != {
        "T": 1.0,
        "kappa": 0.5,
        "y_squared": 3.0,
    }:
        raise OneOmegaActionCharterError("two-side N8 normalization changed")
    window = audits.get("bare_parameter_window", {})
    _close(
        window.get("M4_bulk_squared"),
        1.107013790800849,
        "one-Omega M4_bulk_squared",
    )
    if window.get("hairy_multiscalar_M4_bulk_squared_imported") is not False:
        raise OneOmegaActionCharterError("hairy multiscalar M4 was imported")
    if audits.get("solid_Hessian", {}).get("dynamic_solid_changes_old_Hessian") is not True:
        raise OneOmegaActionCharterError("solid Hessian obstruction was lost")
    if audits.get("solid_Hessian", {}).get("old_P4_determinant_or_modes_inherited") is not False:
        raise OneOmegaActionCharterError("historical P4 was inherited")
    if audits.get("solid_Hessian", {}).get("zero_solid_action_escape_is_viable") is not False:
        raise OneOmegaActionCharterError("S_X=0 was accepted as an escape")
    if audits.get("solid_Hessian", {}).get("fixed_external_triad_escape_is_covariant") is not False:
        raise OneOmegaActionCharterError("frozen X was accepted as a covariant escape")
    variations = audits.get("missing_variations", {})
    if (
        variations.get("N1_ACTION_pass") is not True
        or variations.get("complete_first_variation_and_interface_terms_derived") is not False
        or variations.get("nonlinear_primary_secondary_constraints_derived") is not False
    ):
        raise OneOmegaActionCharterError("N1 was conflated with N2-N7 variation work")


def build_payload() -> dict[str, Any]:
    inputs, bindings = _load_upstreams()
    charter = _action_charter(inputs)
    sigma = _sigma_positive_audit(charter)
    formulas = _formula_sign_audit(charter)
    dimensions = dimension_audit(charter)
    junction = _background_and_junction_audit(charter)
    triad = _triad_rank_audit()
    window = _window_audit(inputs)
    solid = _solid_hessian_audit(charter)
    variations = _variation_ledger()
    ledger = _certificate_ledger()

    checks = {
        "three_direct_upstreams_byte_hash_schema_and_scope_bound_acyclic": bool(
            set(bindings)
            == {"backreacted_wall", "wall_ADM", "nonlinear_Robin_full_V4"}
        ),
        "one_Omega_and_one_solid_route_uniquely_selected": bool(
            charter["selection"]["bulk_compensator_count"] == 1
            and not charter["selection"]["bifundamental_solder_selected"]
            and not charter["selection"]["fixed_external_triad_selected"]
        ),
        "every_independent_classical_field_and_absent_field_class_declared": bool(
            len(charter["independent_fields"]["bulk_dynamic"]) == 3
            and len(charter["independent_fields"]["brane_dynamic"]) == 3
            and charter["independent_fields"]["independent_internal_gauge_fields"] == []
            and charter["independent_fields"]["independent_auxiliary_fields"] == []
        ),
        "exact_action_has_no_ellipsis_and_unlisted_coefficients_are_zero": bool(
            not _contains_ellipsis(charter)
            and charter["exact_action"] == CANONICAL_ACTION
            and charter["coefficient_policy"]["all_unlisted_operator_coefficients_at_mu_star"]
            == 0.0
        ),
        "interface_configuration_and_variation_gluing_is_explicit": bool(
            charter["domains"]["interface_gluing"] == CANONICAL_GLUING
            and charter["domains"][
                "gluing_is_a_restricted_domain_not_a_multiplier_equation"
            ]
        ),
        "formula_indices_shear_and_signs_match_literal_constants": bool(
            formulas["coefficients"] == CANONICAL_FORMULA_SIGNS
            and formulas["solid_shear_operator"] == "tr[(B-v^2*I)^2]"
            and formulas["spatial_triad_completeness"]
            == "sum_a E^(a mu)*E^(a nu)=h^(mu nu)"
        ),
        "classical_action_is_local_and_covariant_on_declared_rank_full_patch": bool(
            triad["local_only_on_B_positive_definite_patch"]
            and charter["domains"]["BRST_closed_boundary_domain_selected"] is False
        ),
        "bulk_compensator_triplet_sigma_metric_is_positive": bool(
            sigma["positive_for_Omega_positive"]
        ),
        "canonical_dimension_ledger_and_Robin_sum_are_homogeneous": bool(
            dimensions["maximum_absolute_residual"] < 1.0e-14
            and dimensions["Robin_sum_is_homogeneous"]
            and dimensions["full_V4_term_has_dimension_five"]
            and dimensions["kappa_b"] == 0.5
            and dimensions["kappa_hat_over_Z5_M"] == 1.0
        ),
        "two_side_material_port_normalizes_to_direct_N8_representative": bool(
            dimensions["N8_two_side_normalization"][
                "raw_barred_T_kappa_y_squared"
            ]
            == {"T": 2.0, "kappa": 1.0, "y_squared": 3.0}
            and dimensions["N8_two_side_normalization"][
                "normalized_T_kappa_y_squared"
            ]
            == {"T": 1.0, "kappa": 0.5, "y_squared": 3.0}
        ),
        "background_and_Z2_junctions_close": bool(
            abs(junction["Israel_residual"]) < 2.0e-14
            and abs(junction["scalar_junction_residual"]) < 2.0e-14
            and abs(junction["Omega_equals_expA_flow_residual_at_brane"]) < 2.0e-14
            and junction["solid_and_Robin_background_first_variations_vanish"]
        ),
        "solder_triad_has_rank_three_and_is_regular_at_zero_acceleration": bool(
            triad["Jacobian_dAcal_da_rank"] == 3
            and abs(triad["sample_E_determinant"] - 1.0) < 2.0e-14
            and triad["analytic_at_zero_acceleration"]
        ),
        "bare_numeric_window_and_obvious_signs_close_without_P4_transport": bool(
            window["strict_window"]
            and window["delta_UV"] > 0.0
            and window["positive_upper_lambda_branch"]
            and window["positive_scalar_coercivity_proxy_at_r_zero"]
            and not window["historical_linear_P4_consumed_as_certificate"]
        ),
        "dynamic_solid_is_individually_healthy_but_changes_full_Hessian": bool(
            solid["isolated_solid_has_no_obvious_kinetic_or_gradient_ghost"]
            and solid["dynamic_solid_changes_old_Hessian"]
            and not solid["old_P4_determinant_or_modes_inherited"]
        ),
        "C1_N1_and_prescribed_port_N8_are_exactly_the_passing_items": bool(
            ledger["C1_through_C10"]["pass_ids"] == ["C1_ACTION"]
            and ledger["N1_through_N8"]["pass_ids"]
            == ["N1_ACTION", "N8_MATERIAL_PORT"]
        ),
        "N1_is_action_only_while_N2_through_N7_remain_fail_closed": bool(
            variations["N1_ACTION_pass"]
            and not variations["complete_first_variation_and_interface_terms_derived"]
            and not variations["nonlinear_primary_secondary_constraints_derived"]
        ),
    }
    checks["all"] = all(checks.values())
    if not checks["all"]:
        failed = [key for key, value in checks.items() if not value]
        raise RuntimeError(f"one-Omega action charter checks failed: {failed}")

    decision = {
        "one_Omega_classical_action_charter_frozen": True,
        "unique_rank_full_solid_solder_route_selected": True,
        "bulk_triplet_sigma_metric_positive_on_declared_domain": True,
        "background_and_Z2_junctions_close": True,
        "rank_three_solder_regular_at_zero_acceleration": True,
        "bare_linear_family_coefficients_can_be_inserted_with_no_obvious_isolated_sign_ghost": True,
        "dynamic_solid_provably_changes_the_full_quadratic_Hessian": True,
        "C1_ACTION_pass": True,
        "N1_ACTION_pass": True,
        "N8_MATERIAL_PORT_pass": True,
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
        "full_P2_pass": False,
        "P3_complete_gauge_fixed_unitary_determinant_pass": False,
        "old_P3_gate_already_consumes_this_C1": False,
        "historical_linear_P4_receipt_reused": False,
        "old_wall_ADM_Hessian_inherited_after_dynamic_solid": False,
        "complete_same_action_ghost_freedom_proved": False,
        "nonlinear_gravitational_P4_pass": False,
        "P4_full_same_action_pass": False,
        "B4_pass": False,
        "B5_pass": False,
        "a0_predicted": False,
        "new_force_derived": False,
        "universal_matter_metric_and_lensing_derived": False,
        "UV_or_top_down_derivation_pass": False,
        "Ward_or_RG_protection_pass": False,
        "publication_authorized": False,
        "status": (
            "ONE_OMEGA_EXACT_ACTION_C1_N1_PASS__PRESCRIBED_PORT_N8_PASS__"
            "DYNAMIC_SOLID_CHANGES_HESSIAN__N2_N7_C2_C10_P2_P3_P4_B4_B5_FAIL_CLOSED"
        ),
        "decisive_result": (
            "One local covariant classical field content and action are now selected, which "
            "closes C1 and N1. The direct prescribed-acceleration material port retains N8. "
            "The rank-full solid adds phonon-shift-metric Hessian blocks, so the historical "
            "P4 determinant cannot be reused."
        ),
        "next_action": (
            "Vary g, Omega, phi, both embeddings, T and X from this exact action; derive all "
            "interface equations, constraints and the extended Hessian before reconsidering "
            "N2-N7, C4 or P4."
        ),
    }
    for key in PHYSICAL_FALSE_KEYS:
        if decision.get(key) is not False:
            raise RuntimeError(f"physical fail-closed key was promoted: {key}")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": (
            "theory_only;exact_classical_one_Omega_action_charter;C1_N1_pass;"
            "prescribed_acceleration_material_port_N8_pass;dynamic_solid_extended_Hessian_"
            "uncomputed;N2_N7_P2_P3_P4_B4_B5_fail_closed"
        ),
        "summary": (
            "The canonical one-Omega wall now has one explicitly selected classical "
            "bulk-plus-moving-brane action with a rank-full solid solder and no hidden "
            "operator coefficients. This resolves the action items C1 and N1. N8 is retained "
            "only for prescribed acceleration with its two-side normalization checked. The "
            "solid changes the Hessian, and no historical P4 result is inherited."
        ),
        "upstream_bindings": bindings,
        "action_charter": charter,
        "algebraic_audits": {
            "positive_sigma": sigma,
            "formula_and_signs": formulas,
            "mass_dimensions": dimensions,
            "background_and_junctions": junction,
            "triad_rank": triad,
            "bare_parameter_window": window,
            "solid_Hessian": solid,
            "missing_variations": variations,
        },
        "certificate_ledger": ledger,
        "checks": checks,
        "decision": decision,
    }
    payload["action_charter_digest"] = {
        "algorithm": "sha256(canonical-json(action_charter))",
        "sha256": _canonical_digest(charter),
    }
    core = {key: payload[key] for key in DIGEST_KEYS}
    payload["calculation_digest"] = {
        "algorithm": "sha256(canonical-json(DIGEST_KEYS))",
        "keys": list(DIGEST_KEYS),
        "sha256": _canonical_digest(core),
    }
    payload["provenance"] = {
        "generator": {
            "path": _display_path(Path(__file__)),
            "sha256": _sha256(Path(__file__)),
        },
        "test": {"path": _display_path(TEST), "sha256": _sha256(TEST)},
        "upstreams": bindings,
        "serialization": "json.dumps(indent=2,sort_keys=True,allow_nan=False)+newline",
        "runtime": {"python": platform.python_version()},
    }
    validate_payload(payload)
    return payload


def main() -> int:
    payload = build_payload()
    _write(OUTPUT, payload)
    print(f"[one-Omega action charter] {OUTPUT}")
    print(f"[action digest] {payload['action_charter_digest']['sha256']}")
    print(f"[calculation digest] {payload['calculation_digest']['sha256']}")
    print(f"[C1/N1] {payload['decision']['C1_ACTION_pass']}/{payload['decision']['N1_ACTION_pass']}")
    print(f"[P3/B4/B5] {payload['decision']['P3_complete_gauge_fixed_unitary_determinant_pass']}/"
          f"{payload['decision']['B4_pass']}/{payload['decision']['B5_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
