#!/usr/bin/env python3
"""Conditional direct-free margin and diagonal-convergence theorem ledger.

This module deliberately does not evaluate a new physical member, certify an
interval margin, or estimate a quadrature remainder.  It records the precise
open-domain hypotheses under which the direct-free complete-shell truncations
are eventually admissible for one fixed member and under which an adaptive,
member-by-member quadrature diagonal converges for the twenty action atoms and
their first variations.

The distinction is essential:

* the analytic admissibility domain is an open set of fields;
* the float64/TaylorDual3 guards in v5.6.7.1 are a smaller implementation
  domain, some parts of which depend on the chosen tangent;
* Q<=8 and G<=16 are finite resource guards, so the v5.6.7.1 finite-rule API
  cannot itself instantiate an infinite quadrature diagonal;
* conditional on the unaudited continuity of the forward decoder, all
  sufficiently late projections of one fixed analytically interior member are
  analytically admissible; this says nothing about eventual TD3/float64
  execution, early projections, or a truncation index/rate uniform on a
  Sobolev ball.

The positive decision keys below concern only this conditional mathematical
ledger, its byte-pinned guard inventory, and exact counterexamples to stronger
quantifiers.  Generic margins, quadrature, bridge, C1/N1, P4, B4 and B5 remain
fail-closed.  No artifact is written.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence, TypedDict


HERE = Path(__file__).resolve().parent
V5671_SOURCE = HERE / "derive_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
V5671_TEST = HERE / "test_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
V5671_SOURCE_SHA256 = "afe410507da533dfff9037b5bd730d90d5931f82aaeb8d4839a48f9a4d18e0c9"
V5671_TEST_SHA256 = "d7988e078fb81f9fa3001eaff2414962d45bfb240b024fbaacf8a9ab126b9694"
V567_EXACT_PRIMITIVES_SOURCE = (
    HERE / "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
)
V567_EXACT_PRIMITIVES_TEST = (
    HERE / "test_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
)
V567_EXACT_PRIMITIVES_SOURCE_SHA256 = (
    "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25"
)
V567_EXACT_PRIMITIVES_TEST_SHA256 = (
    "3fdcd09c3e575893dade6a396865a593349ebc62d28c07706d3f2b58a0caacd4"
)

SCHEMA = (
    "holo.one-omega-topological-so3-direct-free-pointwise-margin-"
    "diagonal-v5-6-7-3.v1"
)

CLASS_SIGNATURE_EIGENVALUE_MARGIN = 2.0e-2
CLASS_OMEGA_MINIMUM = 5.0e-1
CLASS_TIMELIKE_MARGIN = 2.0e-1
CLASS_ROTATION_CUT_LOCUS_MARGIN = 1.0

V5671_METRIC_SYMMETRY_ATOL = 2.0e-12
V5671_METRIC_RELATIVE_EIGENVALUE_FACTOR = 1.0e-10
V5671_METRIC_CONDITION_NUMBER_CAP = 1.0e10
V5671_NORMAL_AND_TIMELIKE_FLOOR = 1.0e-10
V5671_SO3_BODY_NORM_LIMIT = math.pi - 1.0
V5671_SO3_NONBODY_L1_LIMIT = 8.0
V5671_ALGEBRAIC_RESIDUAL_CAP = 2.0e-10
V5671_MAX_T4_ORDER_PER_AXIS = 8
V5671_MAX_GAUSS_ORDER = 16

TRUE_DECISION_KEYS = frozenset(
    {
        "v5_6_7_1_guard_catalog_byte_pinned_pass",
        "complete_full_t4_shell_weighted_radial_projection_lemma_ledger_pass",
        "conditional_fixed_member_eventual_open_admissibility_lemma_ledger_pass",
        "conditional_fixed_member_action_jvp_adaptive_diagonal_convergence_lemma_ledger_pass",
        "nonuniformity_alias_and_resource_counterexamples_exact_pass",
    }
)

FALSE_DECISION_KEYS = frozenset(
    {
        "margins_certified_pass",
        "finite_member_whole_domain_outward_rounded_margin_certificate_pass",
        "constructive_quadrature_remainder_certificate_pass",
        "quadrature_pass",
        "integrated_action_pass",
        "v5_6_7_1_runtime_eventual_acceptance_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_N_to_infinity_numerical_certificate_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "P4_full_same_action_pass",
        "B4_pass",
        "B5_pass",
    }
)

REQUIRED_SOURCE_FRAGMENTS = {
    "so3_body_limit_definition": "SO3_SERIES_BODY_NORM_LIMIT = math.pi - 1.0",
    "so3_nonbody_limit_definition": "SO3_SERIES_NONBODY_L1_LIMIT = 8.0",
    "so3_body_guard": "if z0 > SO3_SERIES_BODY_Z_LIMIT:",
    "so3_nonbody_guard": "if nonbody_l1 > SO3_SERIES_NONBODY_L1_LIMIT:",
    "metric_symmetry_guard": "if not np.allclose(body, body.T, atol=2.0e-12, rtol=0.0):",
    "metric_relative_eigenvalue_guard": (
        "float(np.min(np.abs(eigenvalues))) <= 1.0e-10 * scale"
    ),
    "metric_condition_guard": "if float(np.linalg.cond(body)) > 1.0e10:",
    "metric_determinant_guard": "if determinant.body >= 0.0:",
    "ghy_normal_guard": "if inverse[4][4].body <= 1.0e-10:",
    "interface_timelike_guard": "if tau_norm_squared.body >= -1.0e-10:",
    "skew_residual_guard": "if residual > 2.0e-10:",
    "frame_cancellation_guard": "if cancellation_residual > 2.0e-10:",
    "t4_resource_cap": "MAX_FINITE_T4_ORDER_PER_AXIS = 8",
    "gauss_resource_cap": "MAX_FINITE_RADIAL_ORDER = 16",
    "separate_domain_total": "S_total_formed_only_after_twenty_domain_integrals",
    "generic_integrated_false": '"integrated_action_pass": False',
    "generic_quadrature_false": '"quadrature_pass": False',
}

REQUIRED_EXACT_PRIMITIVES_FRAGMENTS = {
    "complete_real_fourier_generator": "def real_fourier_modes(N: int)",
    "radial_polynomial_generator": "def radial_profile_polynomials(K: int)",
    "radial_envelope": (
        "envelope = Poly([0.0, 0.0, 0.0, 64.0]) * Poly([1.0, -1.0]) ** 3"
    ),
    "mapped_legendre_basis": (
        "legendre = np.polynomial.legendre.Legendre.basis(j).convert(kind=Poly)"
    ),
    "mapped_legendre_composition": (
        "bumps.append(envelope * legendre(Poly([-1.0, 2.0])))"
    ),
}

ANALYTIC_MARGIN_OBLIGATIONS = frozenset(
    {
        "common_gamma_lorentzian_eigen_gap",
        "pulled_bulk_actual_plus_lorentzian_eigen_gap",
        "pulled_bulk_actual_minus_lorentzian_eigen_gap",
        "pulled_bulk_reference_plus_lorentzian_eigen_gap",
        "pulled_bulk_reference_minus_lorentzian_eigen_gap",
        "ghy_spacelike_normal_plus",
        "ghy_spacelike_normal_minus",
        "khronon_timelike",
        "frame_gram_leading_minor_1",
        "frame_gram_leading_minor_2",
        "frame_gram_leading_minor_3",
        "omega_plus",
        "omega_minus",
        "so3_chart_q",
        "so3_chart_r_plus",
        "so3_chart_r_minus",
    }
)

IMPLEMENTATION_MARGIN_OBLIGATIONS = frozenset(
    {
        "metric_relative_eigenvalue_all_operands",
        "metric_condition_number_all_operands",
        "metric_negative_determinant_all_operands",
        "metric_structural_symmetry_all_operands",
        "ghy_normal_guard_gap_plus",
        "ghy_normal_guard_gap_minus",
        "interface_timelike_guard_gap",
        "so3_body_q",
        "so3_body_r_plus",
        "so3_body_r_minus",
        "so3_nonbody_q_primal_spatial_eta",
        "so3_nonbody_r_plus_primal_spatial_eta",
        "so3_nonbody_r_minus_primal_spatial_eta",
        "skew_two_jet_residual",
        "common_frame_cancellation_two_jet_residual",
        "finite_float64_input_and_output",
    }
)

EXPECTED_ACTION_COMPONENTS = (
    "EH_bulk_plus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "GHY_minus",
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)

EVENTUAL_REQUIRED_UNCLOSED_HYPOTHESES = (
    "Gamma_is_C1_on_an_open_graded_Sobolev_neighborhood",
    "Gamma_maps_projection_convergence_to_the_consumed_C2_C3_jets",
)

DIAGONAL_REQUIRED_EXISTENCE_INPUTS = (
    {
        "id": "Gamma_projection_convergence",
        "statement": (
            "Gamma(u_n) converges to Gamma(u), and DGamma(u_n)a_n converges to "
            "DGamma(u)a, in every consumed jet topology"
        ),
    },
    {
        "id": "twenty_primal_integrands_L1_convergence",
        "statement": (
            "the twenty exact primal integrands converge in their separated-domain L1 norms"
        ),
    },
    {
        "id": "twenty_JVP_integrands_L1_convergence",
        "statement": (
            "the twenty exact JVP integrands converge in their separated-domain L1 norms"
        ),
    },
    {
        "id": "fixed_T4_integrand_periodic_quadrature_consistency",
        "statement": (
            "periodic tensor trapezoid rules converge for each already-fixed continuous T4 integrand"
        ),
    },
    {
        "id": "fixed_rho_integrand_Gauss_quadrature_consistency",
        "statement": (
            "positive Gauss-Legendre rules converge for each already-fixed continuous rho integrand"
        ),
    },
)

DIAGONAL_REQUIRED_STEP_IDS = (
    "fix_member_and_tangent",
    "choose_complete_shell_and_radial_approximants",
    "form_fixed_nth_primal_and_JVP_integrands",
    "choose_Qn_Gn_for_the_fixed_nth_integrands",
)


class ProjectionSobolevThreshold(TypedDict):
    parameter: str
    strict_relation: str
    bound: int
    literal: str


class ProjectionRegularityScope(TypedDict):
    C2_full_collar_fields: str
    C3_tangential_boundary_free_fields_only: list[str]
    C3_fields_are_rho_independent: bool
    C3_rho_derivative_or_full_collar_claimed: bool


class ProjectionContract(TypedDict):
    schema: str
    dimension: int
    sobolev_threshold: ProjectionSobolevThreshold
    radial_coefficient_weight_power: int
    rho_derivative_orders: list[int]
    regularity_scope: ProjectionRegularityScope

J3_REQUIRED_LAYER_SPECS = {
    "primal_spatial_coefficients": {
        "eta_power": 0,
        "spatial_total_degree_inclusive": [1, 3],
    },
    "eta_body_coefficient": {
        "eta_power": 1,
        "spatial_total_degree_inclusive": [0, 0],
    },
    "eta_spatial_coefficients": {
        "eta_power": 1,
        "spatial_total_degree_inclusive": [1, 3],
    },
}
J3_DEFINITION = (
    "sum of absolute values of every stored TD3 coefficient except the single "
    "(eta_power=0, spatial_multiindex=0) body coefficient"
)


class PointwiseMarginDiagonalLedgerError(RuntimeError):
    """Raised when a pinned inventory or fail-closed theorem ledger drifts."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strict_nonnegative_integer(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, not {type(value).__name__}")
    converted = int(value)
    if converted < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return converted


def complete_shell_size(shell_radius: int) -> int:
    """Number of real modes in the complete |k|_infinity<=L shell on T4."""

    radius = _strict_nonnegative_integer("shell_radius", shell_radius)
    return (2 * radius + 1) ** 4


def radial_basis_derivative_bounds(index: int) -> tuple[int, int, int]:
    """Declared sup bounds for b_j and its first two rho derivatives."""

    j = _strict_nonnegative_integer("index", index)
    return 1, 12 + 4 * j, 120 + 80 * j + 4 * j * (j + 1)


def gauss_legendre_unit_interval_error_constant(order: int) -> Fraction:
    """Peano coefficient for an order-G Gauss rule on [0,1]."""

    g = _strict_nonnegative_integer("order", order)
    if g == 0:
        raise ValueError("order must be positive")
    numerator = math.factorial(g) ** 4
    denominator = (2 * g + 1) * math.factorial(2 * g) ** 3
    return Fraction(numerator, denominator)


def guard_catalog() -> dict[str, Any]:
    """Return analytic, historical-class, implementation and resource layers."""

    return {
        "analytic_open_margins": {
            "lorentzian_and_inverse": (
                "inf_D min(-lambda_1(g),lambda_2(g))-0.02 > 0 for common gamma and "
                "each actual/reference pulled bulk metric, eigenvalues ordered increasingly"
            ),
            "consumed_metric_restrictions": (
                "the two full GHY metrics are the rho=0 restrictions of the actual pulled "
                "bulk metrics; both induced GHY metrics and the interface metric are the "
                "common gamma by the common-first pullback identities"
            ),
            "ghy_normal": "inf_T4 (g_pulled^{-1})^{rho rho} > 0 on each rho=0 boundary",
            "timelike_khronon": "inf_T4 [-gamma^{-1}(d tau,d tau)]-0.2 > 0",
            "frame": (
                "inf_T4 det(H[0:k,0:k]) > 0 for k=1,2,3, where H is the Gram matrix "
                "of the three projected coordinate-spatial candidates"
            ),
            "Omega": "inf_{T4 x [0,1]} Omega_side-0.5 > 0 on both sides",
            "SO3_charts_if_required": {
                "q": "inf_T4 [pi-|q|]-1.0 > 0",
                "r_plus": "inf_T4 [pi-|r_plus|]-1.0 > 0",
                "r_minus": "inf_T4 [pi-|r_minus|]-1.0 > 0",
                "meaning": (
                    "three separate v5.6.6.8 logarithm-chart conditions; exp itself is "
                    "globally smooth and does not require them"
                ),
            },
            "pullback_invertibility": (
                "the fixed collar Jacobian is triangular with determinant +/-1; this is "
                "a structural identity, not a sampled margin"
            ),
            "regular_V4": "1+Omega^6 |phi|^4 >= 1, so no phi-norm denominator margin exists",
        },
        "historical_class_thresholds": {
            "signature_min_abs_eigenvalue": CLASS_SIGNATURE_EIGENVALUE_MARGIN,
            "Omega_minimum": CLASS_OMEGA_MINIMUM,
            "negative_timelike_norm_clearance": CLASS_TIMELIKE_MARGIN,
            "each_of_q_r_plus_r_minus_cut_locus_clearance": (
                CLASS_ROTATION_CUT_LOCUS_MARGIN
            ),
        },
        "v5_6_7_1_runtime_open_gaps": {
            "metric_symmetry": f"{V5671_METRIC_SYMMETRY_ATOL} - max_abs(g-g^T)",
            "metric_relative_eigenvalue": (
                "min_abs(lambda) - 1e-10 max(1,max_abs(lambda))"
            ),
            "metric_condition_number": "1e10-cond_2(g)",
            "metric_determinant": "-det(g)",
            "ghy_normal": "(g^{-1})^{rho rho}-1e-10",
            "timelike": "-gamma^{-1}(d tau,d tau)-1e-10",
            "so3_body_each_exp": "(pi-1)^2-|rotation_vector|^2",
            "so3_nonbody_each_exp": {
                "gap": "8-J3(rotation_vector;tangent)",
                "J3_definition": J3_DEFINITION,
                "fields": ["q", "r_plus", "r_minus"],
                "cap": V5671_SO3_NONBODY_L1_LIMIT,
                "excluded_keys": ["primal_body_coefficient_only"],
                "required_layers": J3_REQUIRED_LAYER_SPECS,
                "maximum_nonbody_coefficient_keys_per_component": 69,
                "maximum_nonbody_coefficient_keys_per_rotation_vector": 207,
                "geometric_admissibility_condition": False,
                "tangent_and_representation_dependent": True,
            },
            "skew_and_frame_cancellation": "2e-10-max_abs_two_jet_residual",
            "finite_arithmetic": "every float64 input, intermediate and output must remain finite",
        },
        "v5_6_7_1_discrete_resource_domain": {
            "N": "positive integer",
            "K": "positive integer",
            "tangential_order_per_axis": [1, V5671_MAX_T4_ORDER_PER_AXIS],
            "gauss_legendre_order": [1, V5671_MAX_GAUSS_ORDER],
            "tangential_nodes": "Q^4",
            "bulk_nodes_per_side": "Q^4 G",
            "meaning": (
                "implementation guards only; a fixed upper cap cannot instantiate an asymptotic diagonal"
            ),
        },
        "analytic_obligation_ids": sorted(ANALYTIC_MARGIN_OBLIGATIONS),
        "implementation_obligation_ids": sorted(IMPLEMENTATION_MARGIN_OBLIGATIONS),
    }


def _guard_catalog_pin_ledger() -> dict[str, Any]:
    source_sha = _sha256(V5671_SOURCE)
    test_sha = _sha256(V5671_TEST)
    source_text = V5671_SOURCE.read_text(encoding="utf-8")
    exact_primitives_source_sha = _sha256(V567_EXACT_PRIMITIVES_SOURCE)
    exact_primitives_test_sha = _sha256(V567_EXACT_PRIMITIVES_TEST)
    exact_primitives_text = V567_EXACT_PRIMITIVES_SOURCE.read_text(encoding="utf-8")
    fragment_results = {
        name: fragment in source_text for name, fragment in REQUIRED_SOURCE_FRAGMENTS.items()
    }
    exact_primitives_fragment_results = {
        name: fragment in exact_primitives_text
        for name, fragment in REQUIRED_EXACT_PRIMITIVES_FRAGMENTS.items()
    }
    catalog = guard_catalog()
    j3_catalog_match = _j3_catalog_accepts(
        catalog["v5_6_7_1_runtime_open_gaps"]["so3_nonbody_each_exp"]
    )
    return {
        "source_path": V5671_SOURCE.name,
        "source_expected_sha256": V5671_SOURCE_SHA256,
        "source_observed_sha256": source_sha,
        "test_path": V5671_TEST.name,
        "test_expected_sha256": V5671_TEST_SHA256,
        "test_observed_sha256": test_sha,
        "required_source_fragment_matches": fragment_results,
        "exact_primitives_source_path": V567_EXACT_PRIMITIVES_SOURCE.name,
        "exact_primitives_source_expected_sha256": V567_EXACT_PRIMITIVES_SOURCE_SHA256,
        "exact_primitives_source_observed_sha256": exact_primitives_source_sha,
        "exact_primitives_test_path": V567_EXACT_PRIMITIVES_TEST.name,
        "exact_primitives_test_expected_sha256": V567_EXACT_PRIMITIVES_TEST_SHA256,
        "exact_primitives_test_observed_sha256": exact_primitives_test_sha,
        "required_exact_primitives_fragment_matches": exact_primitives_fragment_results,
        "J3_catalog_structural_match": j3_catalog_match,
        "guard_catalog": catalog,
        "pass": bool(
            source_sha == V5671_SOURCE_SHA256
            and test_sha == V5671_TEST_SHA256
            and all(fragment_results.values())
            and exact_primitives_source_sha == V567_EXACT_PRIMITIVES_SOURCE_SHA256
            and exact_primitives_test_sha == V567_EXACT_PRIMITIVES_TEST_SHA256
            and all(exact_primitives_fragment_results.values())
            and j3_catalog_match
        ),
    }


def _canonical_projection_contract() -> ProjectionContract:
    return {
        "schema": "full-T4-weighted-radial-projection-contract.v1",
        "dimension": 4,
        "sobolev_threshold": {
            "parameter": "s",
            "strict_relation": ">",
            "bound": 4,
            "literal": "s>4",
        },
        "radial_coefficient_weight_power": 4,
        "rho_derivative_orders": [0, 1, 2],
        "regularity_scope": {
            "C2_full_collar_fields": (
                "all decoded physical collar fields consumed by the action"
            ),
            "C3_tangential_boundary_free_fields_only": [
                "Y",
                "q",
                "r_plus",
                "r_minus",
            ],
            "C3_fields_are_rho_independent": True,
            "C3_rho_derivative_or_full_collar_claimed": False,
        },
    }


def _projection_contract_accepts(contract: Mapping[str, Any]) -> bool:
    """Validate every analytic parameter consumed by the projection ledger."""

    if not isinstance(contract, Mapping) or set(contract) != {
        "schema",
        "dimension",
        "sobolev_threshold",
        "radial_coefficient_weight_power",
        "rho_derivative_orders",
        "regularity_scope",
    }:
        return False
    threshold = contract.get("sobolev_threshold")
    regularity = contract.get("regularity_scope")
    if not isinstance(threshold, Mapping) or not isinstance(regularity, Mapping):
        return False
    dimension = contract.get("dimension")
    weight_power = contract.get("radial_coefficient_weight_power")
    derivative_orders = contract.get("rho_derivative_orders")
    return bool(
        contract.get("schema") == "full-T4-weighted-radial-projection-contract.v1"
        and not isinstance(dimension, bool)
        and isinstance(dimension, int)
        and dimension == 4
        and set(threshold) == {"parameter", "strict_relation", "bound", "literal"}
        and threshold.get("parameter") == "s"
        and threshold.get("strict_relation") == ">"
        and not isinstance(threshold.get("bound"), bool)
        and isinstance(threshold.get("bound"), int)
        and threshold.get("bound") == 4
        and threshold.get("literal") == "s>4"
        and not isinstance(weight_power, bool)
        and isinstance(weight_power, int)
        and weight_power == 4
        and derivative_orders == [0, 1, 2]
        and all(
            not isinstance(order, bool) and isinstance(order, int)
            for order in derivative_orders
        )
        and set(regularity)
        == {
            "C2_full_collar_fields",
            "C3_tangential_boundary_free_fields_only",
            "C3_fields_are_rho_independent",
            "C3_rho_derivative_or_full_collar_claimed",
        }
        and regularity.get("C2_full_collar_fields")
        == "all decoded physical collar fields consumed by the action"
        and regularity.get("C3_tangential_boundary_free_fields_only")
        == ["Y", "q", "r_plus", "r_minus"]
        and regularity.get("C3_fields_are_rho_independent") is True
        and regularity.get("C3_rho_derivative_or_full_collar_claimed") is False
    )


def _radial_bound_derivation_ledger(
    projection_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Record and arithmetically cross-check the weighted Legendre derivation."""

    contract = (
        _canonical_projection_contract()
        if projection_contract is None
        else projection_contract
    )
    raw_weight_power = contract.get("radial_coefficient_weight_power")
    weight_power = (
        raw_weight_power
        if isinstance(raw_weight_power, int) and not isinstance(raw_weight_power, bool)
        else 0
    )
    raw_derivative_orders = contract.get("rho_derivative_orders")
    derivative_orders = (
        raw_derivative_orders
        if isinstance(raw_derivative_orders, list)
        and all(
            isinstance(order, int) and not isinstance(order, bool)
            for order in raw_derivative_orders
        )
        else []
    )

    # With x=2 rho-1, 64[rho(1-rho)]^3=(1-x^2)^3=w^3.
    # d_x(w^3)=-6xw^2 and d_x^2(w^3)=-6w^2+24x^2w.
    first_constant = 2 * 6
    first_linear_j = 2 * 2
    # Before the Legendre equation, the P' coefficient in d_x^2(w^3 P)
    # is -12 x w^2.  Since w P''=2xP'-j(j+1)P, the w^3 P'' term
    # changes it to -10 x w^2.  |w P'|<=2j and |xw|<=1 then give 20j.
    second_dx_p_prime_coefficient = -12 + 2
    second_constant = 4 * (6 + 24)
    second_linear_j = 4 * (abs(second_dx_p_prime_coefficient) * 2)
    second_quadratic_factor = 4
    derived_bound_formula = {
        "rho_order_0": "1",
        "rho_order_1": f"{first_constant}+{first_linear_j}j",
        "rho_order_2": (
            f"{second_constant}+{second_linear_j}j+"
            f"{second_quadratic_factor}j(j+1)"
        ),
    }
    tail_exponents = {
        f"rho_order_{rho_order}": 2 * rho_order - 2 * weight_power
        for rho_order in derivative_orders
    }
    return {
        "pinned_profile_identity": (
            "b_j(rho)=64[rho(1-rho)]^3 P_j(2rho-1)=(1-x^2)^3 P_j(x), "
            "x=2rho-1"
        ),
        "definitions": {"x": "2rho-1", "w": "1-x^2", "b_j": "w^3 P_j(x)"},
        "weighted_legendre_identities": [
            "w P_j'=j(P_{j-1}-x P_j) for j>=1; j=0 is handled directly",
            "w P_j''=2x P_j'-j(j+1)P_j",
            "|P_j|<=1 and |w P_j'|<=2j on [-1,1]",
        ],
        "product_rule": {
            "d_x_b": "-6xw^2 P_j+w^3 P_j'",
            "d_x_2_b_before_legendre": (
                "(-6w^2+24x^2w)P_j-12xw^2P_j'+w^3P_j''"
            ),
            "d_x_2_b_after_legendre": (
                "(-6w^2+24x^2w-j(j+1)w^2)P_j-10xw^2P_j'"
            ),
            "rho_chain_rule": "d_rho=2d_x and d_rho^2=4d_x^2",
        },
        "derived_sup_bounds": derived_bound_formula,
        "weighted_Cauchy_Schwarz": {
            "coefficient_weight": f"(1+j^2)^{weight_power}",
            "coefficient_weight_power": weight_power,
            "tail_exponent_formula": "2*m-2*weight_power",
            "squared_tail_asymptotic_exponents": tail_exponents,
            "all_three_series_summable": all(
                exponent < -1 for exponent in tail_exponents.values()
            ),
        },
        "pass": bool(
            _projection_contract_accepts(contract)
            and second_dx_p_prime_coefficient == -10
            and derived_bound_formula
            == {
                "rho_order_0": "1",
                "rho_order_1": "12+4j",
                "rho_order_2": "120+80j+4j(j+1)",
            }
            and radial_basis_derivative_bounds(0) == (1, 12, 120)
            and radial_basis_derivative_bounds(3) == (1, 24, 408)
            and tail_exponents
            == {
                f"rho_order_{order}": 2 * order - 2 * weight_power
                for order in derivative_orders
            }
            and all(exponent < -1 for exponent in tail_exponents.values())
        ),
    }


def _projection_lemma_ledger(
    projection_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    contract = (
        _canonical_projection_contract()
        if projection_contract is None
        else projection_contract
    )
    shell_examples = {str(radius): complete_shell_size(radius) for radius in range(3)}
    radial_derivation = _radial_bound_derivation_ledger(contract)
    threshold = contract.get("sobolev_threshold", {})
    if not isinstance(threshold, Mapping):
        threshold = {}
    regularity_contract = contract.get("regularity_scope", {})
    regularity_scope = (
        dict(regularity_contract)
        if isinstance(regularity_contract, Mapping)
        else {}
    )
    weight_power = radial_derivation["weighted_Cauchy_Schwarz"][
        "coefficient_weight_power"
    ]
    exact_primitives_definition_pin_pass = bool(
        _sha256(V567_EXACT_PRIMITIVES_SOURCE)
        == V567_EXACT_PRIMITIVES_SOURCE_SHA256
    )
    radial_growth_squared_exponents = dict(
        radial_derivation["weighted_Cauchy_Schwarz"][
            "squared_tail_asymptotic_exponents"
        ]
    )
    return {
        "projection_contract": dict(contract),
        "dimension": contract.get("dimension"),
        "sobolev_exponent": threshold.get("literal"),
        "derivative_consumed_free_fields": {
            "H_s_plus_1": ["Y", "q_Q", "r_plus", "r_minus"],
            "H_s": "remaining common-first fields, with the graded target used after differentiation",
        },
        "complete_shell": {
            "wavevectors": "all k in Z^4 with |k|_infinity<=L",
            "real_mode_count": "N_L=(2L+1)^4",
            "examples": shell_examples,
            "arbitrary_even_prefix_allowed": False,
            "commutes_with_tangential_derivatives": True,
            "H_t_operator_norm": 1,
        },
        "weighted_radial_space": (
            f"sum_j (1+j^2)^{weight_power} ||C_j||_{{H^s}}^2 < infinity"
        ),
        "exact_primitives_definition_pin_consumed": {
            "source": V567_EXACT_PRIMITIVES_SOURCE.name,
            "sha256": V567_EXACT_PRIMITIVES_SOURCE_SHA256,
            "pass": exact_primitives_definition_pin_pass,
        },
        "radial_basis_bounds": {
            "b_j": "1",
            "d_rho_b_j": "12+4j",
            "d_rho_2_b_j": "120+80j+4j(j+1)",
            "cauchy_schwarz_tail_exponents": radial_growth_squared_exponents,
            "derivation": radial_derivation,
        },
        "regularity_scope": regularity_scope,
        "conclusion": (
            "P_L P_K converges strongly for each fixed free datum, in C2 after Sobolev "
            "embedding on the collar; C3 is only tangential on the rho-independent boundary "
            "free fields Y,q,r_plus,r_minus, with no C3 rho/full-collar claim; no "
            "operator-norm convergence on a Sobolev ball"
        ),
        "pass": bool(
            _projection_contract_accepts(contract)
            and shell_examples == {"0": 1, "1": 81, "2": 625}
            and exact_primitives_definition_pin_pass
            and radial_derivation["pass"]
            and all(exponent < -1 for exponent in radial_growth_squared_exponents.values())
            and radial_basis_derivative_bounds(0) == (1, 12, 120)
            and regularity_scope == contract.get("regularity_scope")
        ),
    }


def _analytic_margin_inventory_accepts(obligations: Sequence[str]) -> bool:
    return frozenset(obligations) == ANALYTIC_MARGIN_OBLIGATIONS


def _runtime_guard_inventory_accepts(obligations: Sequence[str]) -> bool:
    return frozenset(obligations) == IMPLEMENTATION_MARGIN_OBLIGATIONS


def _canonical_eventual_margin_contract() -> dict[str, Any]:
    """Exact conditional-theorem schema; none of its hypotheses is promoted."""

    return {
        "schema": "fixed-member-eventual-analytic-margin-contract.v1",
        "sobolev_threshold": {
            "parameter": "s",
            "strict_relation": ">",
            "bound": 4,
            "literal": "s>4",
        },
        "scope": "analytic-only",
        "fixed_member": "u",
        "eventual_tail_order": {
            "index": "n",
            "relation": ">=",
            "threshold": "n0(u)",
            "order_literal": "n>=n0",
            "member_dependent_literal": "n>=n0(u)",
        },
        "required_unclosed_hypotheses": list(
            EVENTUAL_REQUIRED_UNCLOSED_HYPOTHESES
        ),
        "runtime_eventual_promoted": False,
    }


def _eventual_margin_contract_accepts(contract: Mapping[str, Any]) -> bool:
    """Fail closed unless the analytic-only fixed-member implication is exact."""

    if not isinstance(contract, Mapping) or set(contract) != {
        "schema",
        "sobolev_threshold",
        "scope",
        "fixed_member",
        "eventual_tail_order",
        "required_unclosed_hypotheses",
        "runtime_eventual_promoted",
    }:
        return False
    threshold = contract.get("sobolev_threshold")
    tail = contract.get("eventual_tail_order")
    if not isinstance(threshold, Mapping) or not isinstance(tail, Mapping):
        return False
    bound = threshold.get("bound")
    return bool(
        contract.get("schema")
        == "fixed-member-eventual-analytic-margin-contract.v1"
        and set(threshold) == {"parameter", "strict_relation", "bound", "literal"}
        and threshold.get("parameter") == "s"
        and threshold.get("strict_relation") == ">"
        and not isinstance(bound, bool)
        and isinstance(bound, int)
        and bound == 4
        and threshold.get("literal") == "s>4"
        and contract.get("scope") == "analytic-only"
        and contract.get("fixed_member") == "u"
        and set(tail)
        == {
            "index",
            "relation",
            "threshold",
            "order_literal",
            "member_dependent_literal",
        }
        and tail.get("index") == "n"
        and tail.get("relation") == ">="
        and tail.get("threshold") == "n0(u)"
        and tail.get("order_literal") == "n>=n0"
        and tail.get("member_dependent_literal") == "n>=n0(u)"
        and contract.get("required_unclosed_hypotheses")
        == list(EVENTUAL_REQUIRED_UNCLOSED_HYPOTHESES)
        and contract.get("runtime_eventual_promoted") is False
    )


def _eventual_margin_lemma_ledger(
    theorem_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    contract = (
        _canonical_eventual_margin_contract()
        if theorem_contract is None
        else theorem_contract
    )
    perturbation_steps = {
        "lorentzian": "Weyl eigenvalue perturbation",
        "inverse": "resolvent identity on the fixed positive eigenvalue gap",
        "normal_and_timelike": "uniform convergence of metric inverse and contracted covectors",
        "frame": "continuity of the three Gram leading determinants",
        "Omega": "uniform convergence and positivity of the fixed member",
        "three_separate_SO3_charts": (
            "apply the reverse triangle inequality independently to q, r_plus and r_minus"
        ),
    }
    obligations = sorted(ANALYTIC_MARGIN_OBLIGATIONS)
    tail_contract = contract.get("eventual_tail_order", {})
    if not isinstance(tail_contract, Mapping):
        tail_contract = {}
    tail_literal = tail_contract.get(
        "member_dependent_literal", "invalid-tail-order"
    )
    return {
        "logical_status": (
            "conditional implication only; this module checks the quantifier structure "
            "and does not discharge the decoder-continuity hypotheses"
        ),
        "theorem_contract": dict(contract),
        "quantifiers": {
            "fixed_first": [contract.get("fixed_member")],
            "assumption": "m_analytic(u)>0 for every analytic open margin",
            "exists_after_fixing_member": tail_contract.get("threshold"),
            "tail_statement": (
                f"for every {tail_literal}, m_analytic(u_n)>=m_analytic(u)/2"
            ),
            "early_truncations_claimed_admissible": False,
            "uniform_n0_over_balls_claimed": False,
            "uniform_rate_claimed": False,
        },
        "free_approximants": "u_n=P_{L_n}P_{K_n}u",
        "complete_shell_subsequence": "N_n=(2L_n+1)^4 with L_n,K_n tending to infinity",
        "m_analytic_definition": (
            "the minimum of all listed analytic slacks: Lorentzian eigen clearance "
            "above 0.02, Omega clearance above 0.5, timelike clearance above 0.2, "
            "each separate q/r_plus/r_minus chart clearance above 1.0, and the "
            "zero-threshold GHY-normal and frame-Gram clearances"
        ),
        "proof_steps": perturbation_steps,
        "analytic_margin_obligations_only": obligations,
        "unclosed_hypotheses": {
            "Gamma_is_C1_on_an_open_graded_Sobolev_neighborhood": False,
            "Gamma_maps_projection_convergence_to_the_consumed_C2_C3_jets": False,
        },
        "runtime_nonconclusion": (
            "no eventual acceptance by the v5.6.7.1 TD3/float64 evaluator is claimed; "
            "its condition-number, series, coefficient-l1, residual and finite-arithmetic "
            "guards remain a separate member-and-tangent-dependent catalog"
        ),
        "family_correction": (
            "a projected member need not remain in U_epsilon at small n; the theorem only "
            "places the fixed-member tail in U_{epsilon/2}"
        ),
        "pass": bool(
            _eventual_margin_contract_accepts(contract)
            and _analytic_margin_inventory_accepts(obligations)
            and set(perturbation_steps)
            == {
                "lorentzian",
                "inverse",
                "normal_and_timelike",
                "frame",
                "Omega",
                "three_separate_SO3_charts",
            }
        ),
    }


def _canonical_diagonal_convergence_contract() -> dict[str, Any]:
    return {
        "schema": "fixed-member-action-JVP-adaptive-diagonal-contract.v1",
        "existence_and_convergence_inputs": [
            dict(item) for item in DIAGONAL_REQUIRED_EXISTENCE_INPUTS
        ],
        "quantifier_step_ids": list(DIAGONAL_REQUIRED_STEP_IDS),
        "order_literal": (
            "fix the nth primal/JVP integrands before choosing Q_n,G_n"
        ),
    }


def _diagonal_convergence_contract_accepts(contract: Mapping[str, Any]) -> bool:
    """Consume all five inputs and the member-adapted order, fail closed."""

    if not isinstance(contract, Mapping) or set(contract) != {
        "schema",
        "existence_and_convergence_inputs",
        "quantifier_step_ids",
        "order_literal",
    }:
        return False
    inputs = contract.get("existence_and_convergence_inputs")
    step_ids = contract.get("quantifier_step_ids")
    if not isinstance(inputs, list) or not isinstance(step_ids, list):
        return False
    if len(inputs) != 5 or any(not isinstance(item, Mapping) for item in inputs):
        return False
    expected_inputs = [dict(item) for item in DIAGONAL_REQUIRED_EXISTENCE_INPUTS]
    if inputs != expected_inputs or step_ids != list(DIAGONAL_REQUIRED_STEP_IDS):
        return False
    form_index = step_ids.index("form_fixed_nth_primal_and_JVP_integrands")
    choose_index = step_ids.index("choose_Qn_Gn_for_the_fixed_nth_integrands")
    return bool(
        contract.get("schema")
        == "fixed-member-action-JVP-adaptive-diagonal-contract.v1"
        and contract.get("order_literal")
        == "fix the nth primal/JVP integrands before choosing Q_n,G_n"
        and form_index < choose_index
    )


def _diagonal_convergence_lemma_ledger(
    theorem_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    contract = (
        _canonical_diagonal_convergence_contract()
        if theorem_contract is None
        else theorem_contract
    )
    epsilon_n = "2^(-n)"
    per_atom_budget = "2^(-n)/20"
    gauss_g1 = gauss_legendre_unit_interval_error_constant(1)
    unclosed_hypotheses = {
        "Gamma_is_C1_on_the_declared_open_graded_Sobolev_set": False,
        "DGamma_is_continuous_in_base_point_and_tangent": False,
        "all_twenty_primal_integrand_maps_are_continuous_on_the_margin_set": False,
        "all_twenty_JVP_integrand_maps_are_continuous_on_the_margin_set": False,
    }
    return {
        "logical_status": (
            "conditional implication only; TRUE records the implication and quantifier order, "
            "not that its four analytic hypotheses have been audited"
        ),
        "theorem_contract": dict(contract),
        "quantifier_order": [
            "fix admissible X=Gamma(u) and tangent dX=DGamma(u)a",
            "choose complete-shell/radial approximants u_n,a_n",
            "form the fixed nth exact continuous primal and JVP integrands",
            "only then choose Q_n,G_n>=n for those integrands",
        ],
        "integrand_count": {"primal_atoms": 20, "jvp_atoms": 20},
        "domain_separation": {
            "twelve_bulk_atoms": "T4 x [0,1], tensor periodic trapezoid x Gauss-Legendre",
            "two_GHY_and_six_interface_atoms": "T4 only, periodic trapezoid",
            "S_total": "formed only after the twenty separate integrals",
        },
        "error_choice": {
            "epsilon_n": epsilon_n,
            "each_primal_atom": per_atom_budget,
            "each_jvp_atom": per_atom_budget,
            "total_primal_quadrature_error_at_most": epsilon_n,
            "total_jvp_quadrature_error_at_most": epsilon_n,
        },
        "existence_and_convergence_inputs": contract.get(
            "existence_and_convergence_inputs"
        ),
        "closure_step": (
            "apply the triangle inequality between quadrature_n, exact action/JVP at "
            "X_n, and exact action/JVP at X"
        ),
        "unclosed_hypotheses": unclosed_hypotheses,
        "optional_computable_remainder_formula_not_certified_here": {
            "T4_lipschitz_term": "Vol(T4) 2pi L_x/Q",
            "L_x_definition": "sup over the domain of the Euclidean norm ||grad_x f||_2",
            "periodic_cell_convention": (
                "center the half-open periodic cell of side h=2pi/Q at each grid node; "
                "in four dimensions every point in its cell is at Euclidean distance "
                "at most sqrt(4)h/2=h=2pi/Q"
            ),
            "rho_gauss_term": "Vol(T4) C_G sup|partial_rho^(2G) f|",
            "C_G": "(G!)^4/((2G+1)((2G)!)^3) on [0,1]",
            "C_1": {"numerator": gauss_g1.numerator, "denominator": gauss_g1.denominator},
            "requires_outward_rounded_derivative_bounds": True,
        },
        "conclusion": (
            "there exists a member-adapted diagonal with quadrature action and JVP "
            "converging pointwise in X"
        ),
        "arbitrary_cofinal_Q_G_sufficient_for_changing_integrands": False,
        "constructive_rule_selection_claimed": False,
        "uniform_on_balls_claimed": False,
        "pass": bool(
            _diagonal_convergence_contract_accepts(contract)
            and gauss_g1 == Fraction(1, 24)
            and len(unclosed_hypotheses) == 4
            and not any(unclosed_hypotheses.values())
        ),
    }


def _periodic_alias_exact(frequency: int, order: int) -> bool:
    """Exact integer-turn test for cos(frequency*x) on the order-point grid."""

    frequency = _strict_nonnegative_integer("frequency", frequency)
    order = _strict_nonnegative_integer("order", order)
    if frequency == 0 or order == 0:
        raise ValueError("frequency and order must be positive")
    return all((frequency * j) % order == 0 for j in range(order))


def _transpose_2x2(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("matrix must be 2x2")
    return [[matrix[column][row] for column in range(2)] for row in range(2)]


def _matmul_2x2(
    left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]
) -> list[list[float]]:
    if (
        len(left) != 2
        or len(right) != 2
        or any(len(row) != 2 for row in left)
        or any(len(row) != 2 for row in right)
    ):
        raise ValueError("both matrices must be 2x2")
    return [
        [sum(left[row][k] * right[k][column] for k in range(2)) for column in range(2)]
        for row in range(2)
    ]


def _determinant_2x2(matrix: Sequence[Sequence[float]]) -> float:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("matrix must be 2x2")
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def _pullback_shear_condition_witness(shear: int) -> dict[str, Any]:
    """Derive, rather than assume, the indefinite spectral-condition blow-up."""

    s = _strict_nonnegative_integer("shear", shear)
    if s == 0:
        raise ValueError("shear must be positive")
    jacobian = [[1, 0], [s, 1]]
    minkowski = [[-1, 0], [0, 1]]
    pulled_metric = _matmul_2x2(
        _matmul_2x2(_transpose_2x2(jacobian), minkowski), jacobian
    )
    determinant = _determinant_2x2(pulled_metric)
    trace = pulled_metric[0][0] + pulled_metric[1][1]
    discriminant = trace * trace - 4 * determinant
    lambda_plus = (trace + math.sqrt(discriminant)) / 2
    # det(G)=-1 gives lambda_minus=-1/lambda_plus without cancellation.
    lambda_minus = determinant / lambda_plus
    kappa_abs = lambda_plus / abs(lambda_minus)
    derived_lower_bound = s**4
    derivation_checks = {
        "J_has_required_shear_form": jacobian == [[1, 0], [s, 1]],
        "G_equals_JT_diag_minus1_plus1_J": pulled_metric
        == [[s * s - 1, s], [s, 1]],
        "det_G_equals_minus_one": determinant == -1,
        "trace_G_equals_s_squared": trace == s * s,
        "discriminant_equals_s_fourth_plus_four": discriminant == s**4 + 4,
        "sqrt_discriminant_strictly_exceeds_s_squared": (
            math.sqrt(discriminant) > s * s
        ),
        "lambda_plus_strictly_exceeds_s_squared": lambda_plus > s * s,
        "lambda_product_equals_det_via_stable_definition": math.isclose(
            lambda_plus * lambda_minus,
            determinant,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ),
        "kappa_abs_equals_lambda_plus_squared": math.isclose(
            kappa_abs,
            lambda_plus * lambda_plus,
            rel_tol=2.0e-16,
            abs_tol=0.0,
        ),
        "kappa_abs_strictly_exceeds_s_fourth": kappa_abs > derived_lower_bound,
    }
    return {
        "shear": s,
        "J": jacobian,
        "reference_metric": minkowski,
        "G_equals_J_transpose_reference_J": pulled_metric,
        "det_G": determinant,
        "trace_G": trace,
        "characteristic_discriminant": discriminant,
        "lambda_plus": lambda_plus,
        "lambda_minus_from_det_over_lambda_plus": lambda_minus,
        "kappa_abs": kappa_abs,
        "derived_kappa_abs_strict_lower_bound": derived_lower_bound,
        "derivation": (
            "det(G)=-1 and lambda_plus=(s^2+sqrt(s^4+4))/2>s^2; hence "
            "|lambda_minus|=1/lambda_plus and kappa_abs=lambda_plus^2>s^4"
        ),
        "derivation_checks": derivation_checks,
        "detected": all(derivation_checks.values()),
    }


def _counterexample_ledger() -> dict[str, Any]:
    # f(c)=1+6c/5+cos(2x)/2 = c^2+6c/5+1/2, c=cos(x).
    # Its exact minimum is attained at c=-3/5.
    full_positive_minimum = Fraction(7, 50)
    shell_one_value_at_pi = Fraction(-1, 5)

    shear = 1000
    shear_witness = _pullback_shear_condition_witness(shear)
    alias_order = 7
    tangent_base_j3 = 1
    tangent_scaled_j3 = 9
    witnesses = {
        "early_projection_can_leave_open_margin": {
            "full_metric_positive_spatial_eigenvalue_minimum": str(full_positive_minimum),
            "P1_spatial_eigenvalue_at_pi": str(shell_one_value_at_pi),
            "detected": full_positive_minimum > 0 and shell_one_value_at_pi < 0,
        },
        "bounded_family_has_no_uniform_margin": {
            "family": "diag(-1,1/m,1,1), m positive integer",
            "entrywise_uniform_bound": 1,
            "margin_infimum": 0,
            "detected": True,
        },
        "sobolev_ball_has_no_uniform_projection_tail": {
            "witness": "a unit H^s Fourier mode supported beyond the current complete shell",
            "projection_error_Hs": 1,
            "detected": True,
        },
        "pullback_shear_preserves_inertia_not_condition_guard": {
            **shear_witness,
            "v5_6_7_1_cap": int(V5671_METRIC_CONDITION_NUMBER_CAP),
            "detected": bool(
                shear_witness["detected"]
                and shear_witness["kappa_abs"] > V5671_METRIC_CONDITION_NUMBER_CAP
            ),
        },
        "so3_exp_domain_is_larger_than_v5_6_7_1_series_guard": {
            "witness_rotation_norm": 3.0,
            "v5_6_7_1_norm_limit": V5671_SO3_BODY_NORM_LIMIT,
            "matrix_exponential_exists_for_every_finite_rotation_vector": True,
            "detected": 3.0 > V5671_SO3_BODY_NORM_LIMIT,
        },
        "nonbody_guard_depends_on_tangent_scaling": {
            "J3_before_scaling": tangent_base_j3,
            "J3_after_scaling": tangent_scaled_j3,
            "guard_cap": int(V5671_SO3_NONBODY_L1_LIMIT),
            "mathematical_JVP_remains_linear": True,
            "detected": (
                tangent_base_j3 <= V5671_SO3_NONBODY_L1_LIMIT
                and tangent_scaled_j3 > V5671_SO3_NONBODY_L1_LIMIT
            ),
        },
        "arbitrary_Qn_alias": {
            "function": "cos(Q*x0)",
            "exact_integral": 0,
            "all_Q_grid_samples": 1,
            "detected": _periodic_alias_exact(alias_order, alias_order),
        },
        "Q_to_2Q_refinement_can_share_alias": {
            "function": "cos(2Q*x0)",
            "exact_integral": 0,
            "Q_and_2Q_grid_samples": 1,
            "detected": (
                _periodic_alias_exact(2 * alias_order, alias_order)
                and _periodic_alias_exact(2 * alias_order, 2 * alias_order)
            ),
        },
        "fixed_resource_caps_preclude_infinite_diagonal": {
            "Q_cap_contradicted_by_Q_n_at_least_n_from_n": V5671_MAX_T4_ORDER_PER_AXIS + 1,
            "G_cap_contradicted_by_G_n_at_least_n_from_n": V5671_MAX_GAUSS_ORDER + 1,
            "detected": True,
        },
    }
    return {
        "witnesses": witnesses,
        "pass": all(bool(record["detected"]) for record in witnesses.values()),
    }


def _component_inventory_accepts(components: Sequence[str]) -> bool:
    return tuple(components) == EXPECTED_ACTION_COMPONENTS


def _j3_catalog_accepts(catalog: Mapping[str, Any]) -> bool:
    required_layers = catalog.get("required_layers")
    expanded_regions: set[tuple[int, int]] = set()
    layer_names_ok = isinstance(required_layers, Mapping) and set(required_layers) == {
        "primal_spatial_coefficients",
        "eta_body_coefficient",
        "eta_spatial_coefficients",
    }
    if layer_names_ok:
        for specification in required_layers.values():
            if not isinstance(specification, Mapping):
                return False
            eta_power = specification.get("eta_power")
            degree_interval = specification.get("spatial_total_degree_inclusive")
            if (
                isinstance(eta_power, bool)
                or not isinstance(eta_power, int)
                or eta_power not in (0, 1)
                or not isinstance(degree_interval, list)
                or len(degree_interval) != 2
                or any(isinstance(value, bool) or not isinstance(value, int) for value in degree_interval)
            ):
                return False
            start, stop = degree_interval
            if not 0 <= start <= stop <= 3:
                return False
            for degree in range(start, stop + 1):
                region = (eta_power, degree)
                if region in expanded_regions:
                    return False
                expanded_regions.add(region)
    expected_regions = {(0, degree) for degree in range(1, 4)} | {
        (1, degree) for degree in range(4)
    }
    multiindices_through_degree_three = math.comb(4 + 3, 3)
    nonbody_keys_per_component = 2 * multiindices_through_degree_three - 1
    return bool(
        catalog.get("gap") == "8-J3(rotation_vector;tangent)"
        and catalog.get("J3_definition") == J3_DEFINITION
        and catalog.get("fields") == ["q", "r_plus", "r_minus"]
        and catalog.get("cap") == V5671_SO3_NONBODY_L1_LIMIT
        and catalog.get("excluded_keys") == ["primal_body_coefficient_only"]
        and layer_names_ok
        and expanded_regions == expected_regions
        and catalog.get("maximum_nonbody_coefficient_keys_per_component")
        == nonbody_keys_per_component
        and catalog.get("maximum_nonbody_coefficient_keys_per_rotation_vector")
        == 3 * nonbody_keys_per_component
        and catalog.get("geometric_admissibility_condition") is False
        and catalog.get("tangent_and_representation_dependent") is True
    )


def _domain_contract_accepts(contract: Mapping[str, str]) -> bool:
    return dict(contract) == {
        "bulk": "T4 x rho",
        "boundary": "T4 only",
        "total": "after twenty separate integrals",
    }


def _mutant_campaign() -> dict[str, Any]:
    weakened_projection_sobolev = _canonical_projection_contract()
    weakened_projection_sobolev["sobolev_threshold"] = {
        "parameter": "s",
        "strict_relation": ">",
        "bound": 0,
        "literal": "s>0",
    }
    unweighted_projection = _canonical_projection_contract()
    unweighted_projection["radial_coefficient_weight_power"] = 0
    promoted_c3_projection = _canonical_projection_contract()
    promoted_c3_projection["regularity_scope"] = {
        **promoted_c3_projection["regularity_scope"],
        "C3_rho_derivative_or_full_collar_claimed": True,
    }
    projection_contract_mutants = {
        "weaken_projection_sobolev_threshold_s_gt_4_to_s_gt_0": (
            weakened_projection_sobolev
        ),
        "weaken_projection_radial_weight_power_4_to_0": unweighted_projection,
        "promote_projection_C3_to_rho_full_collar": promoted_c3_projection,
    }
    projection_detected = {
        name: bool(
            not _projection_contract_accepts(mutant)
            and _projection_lemma_ledger(mutant)["pass"] is False
        )
        for name, mutant in projection_contract_mutants.items()
    }
    analytic_margin_mutants = {
        "drop_pulled_reference_plus": ANALYTIC_MARGIN_OBLIGATIONS
        - {"pulled_bulk_reference_plus_lorentzian_eigen_gap"},
        "drop_ghy_normal_minus": ANALYTIC_MARGIN_OBLIGATIONS
        - {"ghy_spacelike_normal_minus"},
        "drop_frame_gram_pivot_2": ANALYTIC_MARGIN_OBLIGATIONS
        - {"frame_gram_leading_minor_2"},
        "drop_q_chart": ANALYTIC_MARGIN_OBLIGATIONS - {"so3_chart_q"},
        "drop_r_plus_chart": ANALYTIC_MARGIN_OBLIGATIONS - {"so3_chart_r_plus"},
        "drop_r_minus_chart": ANALYTIC_MARGIN_OBLIGATIONS - {"so3_chart_r_minus"},
    }
    runtime_guard_mutants = {
        "drop_runtime_ghy_normal_minus": IMPLEMENTATION_MARGIN_OBLIGATIONS
        - {"ghy_normal_guard_gap_minus"},
        "drop_runtime_timelike_gap": IMPLEMENTATION_MARGIN_OBLIGATIONS
        - {"interface_timelike_guard_gap"},
    }
    analytic_detected = {
        name: not _analytic_margin_inventory_accepts(sorted(mutant))
        for name, mutant in analytic_margin_mutants.items()
    }
    runtime_detected = {
        name: not _runtime_guard_inventory_accepts(sorted(mutant))
        for name, mutant in runtime_guard_mutants.items()
    }
    real_j3_catalog = guard_catalog()["v5_6_7_1_runtime_open_gaps"][
        "so3_nonbody_each_exp"
    ]
    mutated_j3_catalog = {
        **real_j3_catalog,
        "required_layers": {
            "primal_spatial_coefficients": J3_REQUIRED_LAYER_SPECS[
                "primal_spatial_coefficients"
            ]
        },
    }
    runtime_detected["drop_eta_from_J3"] = bool(
        _j3_catalog_accepts(real_j3_catalog)
        and not _j3_catalog_accepts(mutated_j3_catalog)
    )

    weakened_sobolev_contract = _canonical_eventual_margin_contract()
    weakened_sobolev_contract["sobolev_threshold"] = {
        "parameter": "s",
        "strict_relation": ">",
        "bound": 0,
        "literal": "s>0",
    }
    reversed_tail_contract = _canonical_eventual_margin_contract()
    reversed_tail_contract["eventual_tail_order"] = {
        "index": "n",
        "relation": "<=",
        "threshold": "n0(u)",
        "order_literal": "n<=n0",
        "member_dependent_literal": "n<=n0(u)",
    }
    runtime_promoted_contract = _canonical_eventual_margin_contract()
    runtime_promoted_contract["runtime_eventual_promoted"] = True
    dropped_Gamma_contract = _canonical_eventual_margin_contract()
    dropped_Gamma_contract["required_unclosed_hypotheses"] = [
        hypothesis
        for hypothesis in EVENTUAL_REQUIRED_UNCLOSED_HYPOTHESES
        if hypothesis
        != "Gamma_maps_projection_convergence_to_the_consumed_C2_C3_jets"
    ]
    eventual_theorem_contract_mutants = {
        "weaken_sobolev_threshold_s_gt_4_to_s_gt_0": weakened_sobolev_contract,
        "reverse_eventual_tail_n_ge_n0_to_n_le_n0": reversed_tail_contract,
        "runtime_eventual_promoted": runtime_promoted_contract,
        "drop_Gamma_projection_convergence": dropped_Gamma_contract,
    }
    eventual_theorem_detected = {
        name: not _eventual_margin_contract_accepts(mutant)
        for name, mutant in eventual_theorem_contract_mutants.items()
    }

    dropped_primal_L1_contract = _canonical_diagonal_convergence_contract()
    dropped_primal_L1_contract["existence_and_convergence_inputs"] = [
        item
        for item in dropped_primal_L1_contract["existence_and_convergence_inputs"]
        if item["id"] != "twenty_primal_integrands_L1_convergence"
    ]
    dropped_JVP_L1_contract = _canonical_diagonal_convergence_contract()
    dropped_JVP_L1_contract["existence_and_convergence_inputs"] = [
        item
        for item in dropped_JVP_L1_contract["existence_and_convergence_inputs"]
        if item["id"] != "twenty_JVP_integrands_L1_convergence"
    ]
    dropped_diagonal_Gamma_contract = _canonical_diagonal_convergence_contract()
    dropped_diagonal_Gamma_contract["existence_and_convergence_inputs"] = [
        item
        for item in dropped_diagonal_Gamma_contract[
            "existence_and_convergence_inputs"
        ]
        if item["id"] != "Gamma_projection_convergence"
    ]
    choose_rule_too_early_contract = _canonical_diagonal_convergence_contract()
    choose_rule_too_early_contract["quantifier_step_ids"] = [
        "fix_member_and_tangent",
        "choose_complete_shell_and_radial_approximants",
        "choose_Qn_Gn_for_the_fixed_nth_integrands",
        "form_fixed_nth_primal_and_JVP_integrands",
    ]
    diagonal_theorem_contract_mutants = {
        "drop_diagonal_Gamma_projection_convergence_input": (
            dropped_diagonal_Gamma_contract
        ),
        "drop_twenty_primal_integrands_L1_convergence": dropped_primal_L1_contract,
        "drop_twenty_JVP_integrands_L1_convergence": dropped_JVP_L1_contract,
        "choose_Q_G_before_fixed_nth_integrand": choose_rule_too_early_contract,
    }
    diagonal_theorem_detected = {
        name: not _diagonal_convergence_contract_accepts(mutant)
        for name, mutant in diagonal_theorem_contract_mutants.items()
    }
    action_detected = {
        "drop_one_of_twenty_action_components": not _component_inventory_accepts(
            EXPECTED_ACTION_COMPONENTS[:-1]
        ),
        "repeat_boundary_with_radial_measure": not _domain_contract_accepts(
            {
                "bulk": "T4 x rho",
                "boundary": "T4 x rho",
                "total": "after twenty separate integrals",
            }
        ),
    }
    detected = {
        **projection_detected,
        **analytic_detected,
        **runtime_detected,
        **eventual_theorem_detected,
        **diagonal_theorem_detected,
        **action_detected,
    }
    return {
        "projection_contract_mutant_detected": projection_detected,
        "analytic_margin_mutant_detected": analytic_detected,
        "runtime_catalog_mutant_detected": runtime_detected,
        "eventual_theorem_contract_mutant_detected": eventual_theorem_detected,
        "diagonal_theorem_contract_mutant_detected": diagonal_theorem_detected,
        "action_contract_mutant_detected": action_detected,
        "projection_contract_mutants_pass": all(projection_detected.values()),
        "analytic_margin_mutants_pass": all(analytic_detected.values()),
        "runtime_catalog_mutants_pass": all(runtime_detected.values()),
        "eventual_theorem_contract_mutants_pass": all(
            eventual_theorem_detected.values()
        ),
        "diagonal_theorem_contract_mutants_pass": all(
            diagonal_theorem_detected.values()
        ),
        "action_contract_mutants_pass": all(action_detected.values()),
        "mutant_detected": detected,
        "all_mutants_effective": all(detected.values()),
        "pass": all(detected.values()),
    }


def build_report() -> dict[str, Any]:
    pins = _guard_catalog_pin_ledger()
    projection = _projection_lemma_ledger()
    eventual = _eventual_margin_lemma_ledger()
    diagonal = _diagonal_convergence_lemma_ledger()
    counterexamples = _counterexample_ledger()
    mutants = _mutant_campaign()

    decision: dict[str, bool] = {
        "v5_6_7_1_guard_catalog_byte_pinned_pass": bool(pins["pass"]),
        "complete_full_t4_shell_weighted_radial_projection_lemma_ledger_pass": bool(
            projection["pass"] and mutants["projection_contract_mutants_pass"]
        ),
        "conditional_fixed_member_eventual_open_admissibility_lemma_ledger_pass": bool(
            eventual["pass"]
            and mutants["analytic_margin_mutants_pass"]
            and mutants["eventual_theorem_contract_mutants_pass"]
        ),
        "conditional_fixed_member_action_jvp_adaptive_diagonal_convergence_lemma_ledger_pass": bool(
            diagonal["pass"]
            and mutants["action_contract_mutants_pass"]
            and mutants["diagonal_theorem_contract_mutants_pass"]
        ),
        "nonuniformity_alias_and_resource_counterexamples_exact_pass": bool(
            counterexamples["pass"] and mutants["pass"]
        ),
        "margins_certified_pass": False,
        "finite_member_whole_domain_outward_rounded_margin_certificate_pass": False,
        "constructive_quadrature_remainder_certificate_pass": False,
        "quadrature_pass": False,
        "integrated_action_pass": False,
        "v5_6_7_1_runtime_eventual_acceptance_pass": False,
        "uniform_N_to_infinity_bridge_pass": False,
        "uniform_N_to_infinity_numerical_certificate_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "P4_full_same_action_pass": False,
        "B4_pass": False,
        "B5_pass": False,
    }
    observed_true = frozenset(key for key, value in decision.items() if value)
    observed_false = frozenset(key for key, value in decision.items() if not value)
    if observed_true != TRUE_DECISION_KEYS or observed_false != FALSE_DECISION_KEYS:
        raise PointwiseMarginDiagonalLedgerError(
            "decision allowlist drift or a conditional theorem prerequisite failed"
        )

    return {
        "schema": SCHEMA,
        "claim": (
            "Byte-pinned v5.6.7.1 guard inventory plus a conditional fixed-member "
            "eventual-margin and member-adapted diagonal convergence theorem ledger"
        ),
        "source_pins_and_guard_catalog": pins,
        "complete_shell_and_radial_projection_lemma": projection,
        "fixed_member_eventual_open_margin_lemma": eventual,
        "fixed_member_action_jvp_diagonal_convergence_lemma": diagonal,
        "exact_counterexamples": counterexamples,
        "effective_mutants": mutants,
        "computable_finite_certificates": {
            "whole_domain_interval_margin_engine_implemented": False,
            "outward_rounded_metric_inverse_and_eigenvalue_bounds_implemented": False,
            "outward_rounded_integrand_derivative_bounds_implemented": False,
            "constructive_Q_G_selector_implemented": False,
            "v5_6_7_1_same_grid_float64_receipt_reclassified_as_remainder_bound": False,
        },
        "open_obligations": [
            "audit Gamma as a C1 map on the declared graded Sobolev open set",
            "audit continuity of DGamma in both its base point and tangent",
            "audit continuity of all twenty primal integrand maps on the analytic margin set",
            "audit continuity of all twenty JVP integrand maps on the analytic margin set",
            "prove that the chosen target X satisfies every strict analytic class margin",
            "supply an outward-rounded whole-domain finite-member margin certificate",
            "supply certified derivative/modulus bounds and a constructive quadrature remainder",
            "replace the fixed Q<=8,G<=16 finite allocator by a resource-bounded growing or streaming rule",
            "complete the remaining fixed-background, Green, moving-embedding and noncompact obligations",
        ],
        "decision": decision,
        "scope": (
            "The lemmas are conditional mathematical ledgers relative to standard Fourier projection, "
            "Sobolev embedding, Weyl/inverse perturbation, smooth composition, periodic Riemann-sum and "
            "positive Gauss-Legendre consistency results. They are not proof-assistant derivations. The "
            "analytic eventual index depends on the fixed member; the quadrature orders may depend on "
            "the fixed member and tangent. Gamma C1, DGamma continuity, and continuity of the twenty "
            "primal/JVP integrand maps are explicit undischarged hypotheses. No eventual float64 "
            "acceptance, early-truncation, uniform-on-balls, interval-margin, constructive-remainder, "
            "unconditional continuum-action, bridge, C1/N1, P4, B4 or B5 conclusion is made. The "
            "v5.6.7.1 resource guards cannot realize the asymptotic diagonal. No artifact or roadmap "
            "file is written."
        ),
    }


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
