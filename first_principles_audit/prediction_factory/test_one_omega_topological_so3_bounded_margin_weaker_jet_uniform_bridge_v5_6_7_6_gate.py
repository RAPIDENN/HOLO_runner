#!/usr/bin/env python3
"""Independent tests for the scoped v5.6.7.6 exact-formula bridge."""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE
    / "derive_one_omega_topological_so3_bounded_margin_weaker_jet_uniform_bridge_v5_6_7_6_gate.py"
)
SPEC = importlib.util.spec_from_file_location("v5676_weaker_jet_bridge", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


EXPECTED_TRUE = {
    "complete_shell_H19_4_to_H9_2_uniform_rate_pass",
    "weighted_radial_p4_C2_tail_and_C0_3_8_equicontinuity_pass",
    "tensor_trapezoid_gauss_bernstein_exact_bound_pass",
}

EXPECTED_FALSE = {
    "margins_certified_pass",
    "integrated_action_pass",
    "quadrature_pass",
    "v5_6_7_1_runtime_eventual_acceptance_pass",
    "twenty_real_formula_paths_and_sixteen_margin_inventory_ast_bound_pass",
    "uniform_twenty_primal_jvp_holder_lemma_pass",
    "bounded_margin_ball_weaker_jet_exact_formula_uniform_bridge_pass",
    "uniform_N_to_infinity_bridge_pass",
    "uniform_N_to_infinity_numerical_certificate_pass",
    "same_functional_symbolic_identity_pass",
    "all_N_q_zero_factorization_pass",
    "continuum_action_representative_independence_theorem_pass",
    "global_smooth_physical_gauge_quotient_manifold_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "C1_N1_promotion_authorized",
    "P4_full_same_action_pass",
    "B4_pass",
    "B5_pass",
}

EXPECTED_COMPONENTS = (
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

EXPECTED_MARGINS = {
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

EXPECTED_CALL_EDGES = {
    "decode_common_first_boundary_td3": {
        "_spectral_td3",
        "so3_exp",
        "_inverse_td3",
        "_matmul",
        "_vee_checked_td3",
    },
    "_collar_ambient_x64": {"_load_pinned_upstream", "RhoJet2"},
    "_pullback_x64_and_reference15": {"_sym_matrix", "_matmul", "_det3"},
    "rhojet2_local_two_jet": {"_dual_value"},
    "_bulk_component_densities_td3": {
        "td3_metric_geometry",
        "td3_cross",
        "_regular_v4_td3",
    },
    "_relative_bulk_densities_td3": {
        "_bulk_component_densities_td3",
        "_x64_local_primitives",
    },
    "_ghy_density_td3": {"_x64_local_primitives", "td3_metric_geometry"},
    "_foliation_geometry_td3": {"td3_metric_geometry"},
    "_interface_component_densities_td3": {
        "_foliation_geometry_td3",
        "_dual_value",
    },
    "_bulk_components_from_boundary_td3": {
        "_collar_ambient_x64",
        "_pullback_x64_and_reference15",
        "_relative_bulk_densities_td3",
    },
    "_boundary_components_from_boundary_td3": {
        "_collar_ambient_x64",
        "_pullback_x64_and_reference15",
        "_ghy_density_td3",
        "_interface_component_densities_td3",
    },
    "_local_density_td3": {
        "decode_common_first_boundary_td3",
        "_bulk_components_from_boundary_td3",
        "_boundary_components_from_boundary_td3",
    },
    "integrated_action_values_and_eta_jvps": {
        "finite_full_t4_rho_quadrature",
        "decode_common_first_boundary_td3",
        "_bulk_components_from_boundary_td3",
        "_boundary_components_from_boundary_td3",
    },
}

EXPECTED_PINS = {
    "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py": (
        "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25"
    ),
    "test_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py": (
        "3fdcd09c3e575893dade6a396865a593349ebc62d28c07706d3f2b58a0caacd4"
    ),
    "derive_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py": (
        "afe410507da533dfff9037b5bd730d90d5931f82aaeb8d4839a48f9a4d18e0c9"
    ),
    "test_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py": (
        "d7988e078fb81f9fa3001eaff2414962d45bfb240b024fbaacf8a9ab126b9694"
    ),
    "derive_one_omega_topological_so3_direct_free_pointwise_margin_diagonal_v5_6_7_3_gate.py": (
        "e85d247bfbc766ff59105469626b0191adb6aaeda9799c84dca3fdeca4e3271a"
    ),
    "test_one_omega_topological_so3_direct_free_pointwise_margin_diagonal_v5_6_7_3_gate.py": (
        "1d7687ed37c9a10454d221440184080412ede621f8301aa940b1ed76d3c05fdd"
    ),
}


def _assignment_literal(tree: ast.AST, name: str):
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == name for target in targets):
            continue
        value = node.value
        assert value is not None
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
        ):
            value = value.args[0]
        return ast.literal_eval(value)
    raise AssertionError(f"literal assignment {name} not found")


def _functions(tree: ast.AST) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _calls(node: ast.AST) -> set[str]:
    result: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        if isinstance(child.func, ast.Name):
            result.add(child.func.id)
        elif isinstance(child.func, ast.Attribute):
            result.add(child.func.attr)
    return result


def _return_keys(node: ast.AST) -> set[str]:
    result: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Return) and isinstance(child.value, ast.Dict):
            for key in child.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    result.add(key.value)
    return result


def test_decision_allowlists_are_test_local_and_fail_closed() -> None:
    decision = gate.build_report()["decision"]
    assert {key for key, value in decision.items() if value} == EXPECTED_TRUE
    assert {key for key, value in decision.items() if not value} == EXPECTED_FALSE
    assert set(decision) == EXPECTED_TRUE | EXPECTED_FALSE
    assert gate.TRUE_DECISION_KEYS == EXPECTED_TRUE
    assert gate.FALSE_DECISION_KEYS == EXPECTED_FALSE


def test_every_stable_input_is_byte_pinned_with_test_local_hashes() -> None:
    report = gate.build_report()["source_pins"]
    assert report["pass"] is True
    assert report["expected"] == EXPECTED_PINS
    for name, expected in EXPECTED_PINS.items():
        path = HERE / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        assert report["observed"][name] == expected
        assert report["matches"][name] is True


def test_real_twenty_route_call_graph_and_domains_are_independently_parsed() -> None:
    text = gate.V5671_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(text)
    functions = _functions(tree)
    for function_name, required in EXPECTED_CALL_EDGES.items():
        assert function_name in functions
        assert required <= _calls(functions[function_name])

    sides = tuple(_assignment_literal(tree, "SIDES"))
    bulk = tuple(_assignment_literal(tree, "BULK_SECTORS"))
    interface = tuple(_assignment_literal(tree, "INTERFACE_SECTORS"))
    components = tuple(
        name
        for side in sides
        for name in tuple(f"{sector}_bulk_{side}" for sector in bulk)
        + (f"GHY_{side}",)
    ) + interface
    assert components == EXPECTED_COMPONENTS
    assert _return_keys(functions["_bulk_component_densities_td3"]) == {
        "EH",
        "Omega_kinetic",
        "Omega_potential",
        "P_kinetic",
        "full_V4",
        "BF",
    }
    assert _return_keys(functions["_interface_component_densities_td3"]) == {
        "wall",
        "K_foliation",
        "R",
        "R_squared",
        "a_squared",
        "Robin",
    }
    assert "for name in BOUNDARY_COMPONENTS:" in text
    assert "for rho, radial_weight in zip(rho_nodes, rho_weights):" in text
    assert "for name in BULK_COMPONENTS:" in text
    assert "combined_weight = float(tangential_weight) * float(radial_weight)" in text
    assert '"S_total_formed_only_after_twenty_domain_integrals": True' in text

    inventory = gate.build_report()["real_formula_AST_inventory"]
    # These checks are useful diagnostics, but do not form a typed expression
    # IR and therefore cannot discharge a formula or Holder theorem.
    assert inventory["shallow_lexical_inventory_pass"] is True
    assert inventory["pass"] is False
    assert inventory["component_order"] == list(EXPECTED_COMPONENTS)
    assert inventory["component_count"] == 20
    assert inventory["runtime_resource_caps"] == {"Q": 8, "G": 16}
    assert inventory["consumed_source_subscript_keys"] == {
        "bulk_primitives": [
            "A",
            "B",
            "d_A",
            "d_g",
            "d_log_Omega",
            "d_phi",
            "dd_g",
            "g",
            "log_Omega",
            "phi",
        ],
        "GHY_primitives": ["d_g", "g"],
        "interface_common": ["E_Q", "T", "gamma", "log_Omega", "varphi"],
    }
    transitive = inventory["transitive_source_diagnostic"]
    assert transitive["reachable_local_function_count"] == 67
    assert transitive["adjacency_sha256"] == (
        "a4d322b8d66da0d6199cc8ab094073e604a5ac3000bb664e06c912de86f99ced"
    )
    assert transitive["regular_v4_reachable"] is True
    assert transitive["standalone_typed_expression_IR_emitted"] is False
    assert transitive["decoder_projection_continuity_discharged"] is False
    assert transitive["inverse_root_guard_bijection_discharged"] is False
    assert transitive["pass"] is False


def test_all_sixteen_analytic_margins_are_independently_parsed() -> None:
    tree = ast.parse(gate.V5673_SOURCE.read_text(encoding="utf-8"))
    margins = set(_assignment_literal(tree, "ANALYTIC_MARGIN_OBLIGATIONS"))
    assert margins == EXPECTED_MARGINS
    inventory = gate.build_report()["real_formula_AST_inventory"]
    assert set(inventory["analytic_margin_ids"]) == EXPECTED_MARGINS
    assert inventory["analytic_margin_count"] == 16


def test_complete_shell_and_weaker_sobolev_exponents_are_exact() -> None:
    s = Fraction(19, 4)
    s0 = Fraction(9, 2)
    alpha = Fraction(1, 4)
    assert s - s0 == Fraction(1, 4)
    assert -(s - s0) / 2 == Fraction(-1, 8)
    assert -(s - s0) == Fraction(-1, 4)
    assert s0 > 2 + alpha + Fraction(4, 2)
    assert s0 + 1 > 3 + alpha + Fraction(4, 2)
    assert [gate.complete_shell_size(L) for L in range(4)] == [1, 81, 625, 2401]
    ledger = gate.build_report()["fourier_complete_shell_lemma"]
    assert ledger["pass"] is True
    assert ledger["weight_exponent"] == {"numerator": -1, "denominator": 8}
    assert ledger["asymptotic_L_exponent"] == {"numerator": -1, "denominator": 4}
    assert ledger["enhanced_fields"] == [
        "plus.Y",
        "minus.Y",
        "Q_frame.q",
        "plus.r_E0",
        "minus.r_E0",
    ]
    for malformed in (-1, True, 1.0, "1"):
        try:
            gate.complete_shell_size(malformed)
        except ValueError:
            pass
        else:
            raise AssertionError(f"malformed shell radius accepted: {malformed!r}")


def test_radial_tail_markov_split_and_endpoint_are_exact() -> None:
    assert gate.exact_legendre_coefficients(3) == (
        Fraction(0),
        Fraction(-3, 2),
        Fraction(0),
        Fraction(5, 2),
    )
    assert gate.exact_radial_basis_coefficients(0) == tuple(
        Fraction(value) for value in (1, 0, -3, 0, 3, 0, -1)
    )
    # Regression for the NumPy power-basis endpoint failure found at K=24.
    # This is the separate exact all-j path, so the first three endpoint jets
    # vanish identically rather than producing the observed ~-219 artifact.
    assert gate.exact_radial_basis_jet(23, Fraction(1)) == (
        Fraction(0),
        Fraction(0),
        Fraction(0),
    )
    assert gate.exact_radial_family_fingerprint(12) == (
        "00b9c0d7c37f022c8d3669b6771424e46e7818cdb90c48f6e722717a7290cfce"
    )
    assert gate.radial_basis_derivative_bounds(0) == (1, 12, 120)
    assert gate.radial_basis_derivative_bounds(3) == (1, 24, 408)
    ledger = gate.build_report()["weighted_radial_lemma"]
    assert ledger["pass"] is True
    assert ledger["squared_summand_exponents"] == {"0": -8, "1": -6, "2": -4}
    assert ledger["tail_norm_exponents"]["2"] == {"numerator": -3, "denominator": 2}
    assert ledger["worst_C2_constant_numerator"] == 416
    assert ledger["worst_C2_constant_squared_denominator"] == 3
    assert ledger["markov"]["coarse_growth_constant"] == 8 * 6**6 == 373248
    assert ledger["basis_role"] == (
        "exact ideal family, not the NumPy power-basis runtime generator"
    )
    assert ledger["exact_engine"] == {
        "coefficient_field": "Q (fractions only)",
        "legendre_recurrence": (
            "P_0=1; P_1=x; P_(j+1)=((2j+1)xP_j-jP_(j-1))/(j+1)"
        ),
        "envelope_in_x": "(1-x^2)^3",
        "rho_chain_rule": "d_rho^m=2^m d_x^m for m=0,1,2",
        "arbitrary_nonnegative_index_accepted": True,
        "prefix_0_through_12_sha256": (
            "00b9c0d7c37f022c8d3669b6771424e46e7818cdb90c48f6e722717a7290cfce"
        ),
        "j23_rho1_jet_0_through_2": [[0, 1], [0, 1], [0, 1]],
    }
    assert ledger["pinned_numpy_generator"] == {
        "used_by_ideal_lemma": False,
        "upstream_validation_scope": "K<=8 only",
        "all_j_runtime_certified": False,
        "known_failure": "K=24,j=23,rho=1 may evaluate b_23 near -219 in float64",
    }
    assert ledger["exact_coarse_inequality_identities"] == {
        "208j2_minus_B2": {
            "coefficients": [-120, -84, 204],
            "factorization": "12(j-1)(17j+10), j>=1",
        },
        "240_jplus1_squared_minus_2B2": [0, 312, 232],
        "twice_1plusj2_minus_jplus1_squared": [1, -2, 1],
        "six_jplus1_minus_jplus6": [0, 5],
    }

    split = ledger["endpoint_split"]
    assert split["index"] == "J=ceil(delta^(-1/4)); low 0<=j<J; high j>=J"
    assert split["split_power"] == {"numerator": 1, "denominator": 4}
    assert split["low_squared_delta_exponent"] == {"numerator": 3, "denominator": 4}
    assert split["high_squared_delta_exponent"] == {"numerator": 3, "denominator": 4}
    assert split["holder_exponent"] == {"numerator": 3, "denominator": 8}
    expected_constant_squared = Fraction(512 * (8 * 6**6) ** 2) + Fraction(16 * 240**2, 3)
    assert split["holder_constant_squared"] == {
        "numerator": expected_constant_squared.numerator,
        "denominator": expected_constant_squared.denominator,
    }
    # Termwise interpolation at beta=3/8 has harmonic exponent -1;
    # only the low/high split proves the endpoint.
    assert -4 + 8 * Fraction(3, 8) == -1
    assert ledger["termwise_interpolation_endpoint_series_exponent"] == {
        "numerator": -1,
        "denominator": 1,
    }
    assert ledger["termwise_interpolation_is_not_endpoint_proof"] is True


def test_float_power_basis_failure_is_recorded_but_not_used_by_ideal_lemma() -> None:
    runtime_spec = importlib.util.spec_from_file_location(
        "v567_float_radial_runtime", gate.V567_SOURCE
    )
    assert runtime_spec is not None and runtime_spec.loader is not None
    runtime = importlib.util.module_from_spec(runtime_spec)
    runtime_spec.loader.exec_module(runtime)
    observed = float(runtime.radial_profiles(1.0, 24)["bumps"][0, 23])
    assert abs(observed) > 100.0
    assert gate.exact_radial_basis_jet(23, Fraction(1))[0] == 0
    decision = gate.build_report()["decision"]
    assert decision[
        "weighted_radial_p4_C2_tail_and_C0_3_8_equicontinuity_pass"
    ] is True
    assert decision["v5_6_7_1_runtime_eventual_acceptance_pass"] is False


def test_contract_has_exact_quantifier_order_and_only_formula_target() -> None:
    report = gate.build_report()
    contract = report["theorem_contract"]
    assert contract["status"] == "specification_only_not_discharged"
    assert contract["source_space"]["ordinary_fields"] == "H^(19/4)(T4)"
    assert contract["source_space"]["enhanced_space"] == "H^(23/4)(T4)"
    assert contract["source_space"]["tangent_norm_bound"] == "||a||<=M"
    assert contract["ball"]["quantifiers"] == "for every M>=1 and 0<epsilon<=1"
    assert contract["ball"]["whole_noncompact_domain_uniformity_claimed"] is False
    assert contract["eventual_margins"] == {
        "exists": "n0(M,epsilon)",
        "definition": (
            "least n>=1 with C_margin(M,epsilon)"
            "([1+(n+1)^2]^(-1/8)+(416/sqrt(3))n^(-3/2))<=epsilon/2"
        ),
        "order": "for every n>=n0 and every (u,a) in B_(M,epsilon)",
        "projected_margin": ">=epsilon/2",
        "early_n_claimed": False,
    }
    assert contract["diagonal"] == {
        "L_n": "n",
        "K_n": "n",
        "N_n": "(2n+1)^4",
        "Q_n": "n",
        "G_n": "n",
        "n_domain": "positive integers",
    }
    target = contract["target_identity"]
    assert target["proposed_not_proved"] == (
        "the exact real integral of the same twenty formula paths"
    )
    assert target["literal_S_rel_symbolic_identity_claimed"] is False
    assert target["q_zero_continuum_factorization_claimed"] is False
    assert target["physical_gauge_quotient_claimed"] is False
    assert target["float64_runtime_sequence_claimed"] is False
    lemma = report["analytic_holder_and_eventual_margin_lemma"]
    assert lemma["pass"] is False
    assert "for every M>=1" in lemma["quantifiers"]
    assert lemma["n0_definition"] == contract["eventual_margins"]["definition"]
    assert "not uniform" in lemma["noncompact_exhaustion"]
    assert lemma["unclosed_obligations"] == [
        "emit all twenty primal formulas and JVPs as a closed typed pure IR",
        "bind every transitive helper and consumed jet leaf with derivative order",
        "prove decoder and projection continuity into that complete leaf schema",
        "bind every inverse, reciprocal and positive root to one of sixteen margins or structural positivity",
        "derive uniform first/second IR derivative bounds before differentiating under integrals",
    ]


def test_trapezoid_bernstein_gauss_and_total_rate_are_exact() -> None:
    ledger = gate.build_report()["quadrature_and_total_rate_lemma"]
    assert ledger["pass"] is True
    assert ledger["periodic_voronoi_cell_radius_in_dimension_four"] == "2pi/Q"
    assert ledger["trapezoid_per_atom"] == "V H (2pi/Q)^(1/4)"
    gauss = ledger["gauss"]
    assert gauss["polynomial_exactness_degree"] == "2G-1"
    assert gauss["degree_offset_from_2G"] == -1
    assert gauss["integral_plus_rule_factor"] == 2
    assert gauss["asymptotic_G_exponent"] == {"numerator": -1, "denominator": 8}
    assert ledger["S_total_bound"] == (
        "20 V C Delta_n + 20 V H (2pi/n)^(1/4) + "
        "24 V H [1/(2 sqrt(2n-1))]^(1/4)"
    )
    assert ledger["overall_n_exponent"] == {"numerator": -1, "denominator": 8}
    assert ledger["overall_bound"] == "D(M,epsilon)n^(-1/8), n>=n0(M,epsilon)"


def test_every_contract_mutant_is_effective_and_expected() -> None:
    campaign = gate.build_report()["effective_contract_mutants"]
    expected = {
        "same_norm_target",
        "critical_s0_four",
        "alpha_one_half_endpoint",
        "omit_q_enhanced_regularity",
        "radial_weight_three",
        "omit_tangent_bound",
        "omit_one_margin",
        "merge_bulk_boundary_domains",
        "gauss_degree_2G",
        "fixed_quadrature",
        "N_n_equals_n",
        "claim_literal_S_rel_identity",
        "claim_q_continuum",
        "claim_float64_sequence",
    }
    assert set(campaign["mutants"]) == expected
    assert campaign["all_mutants_effective"] is True
    assert all(row == {"accepted": False, "detected": True} for row in campaign["mutants"].values())

    canonical = copy.deepcopy(gate.build_report()["theorem_contract"])
    assert gate._theorem_contract_accepts(canonical)
    canonical["diagonal"]["N_n"] = "n"
    assert not gate._theorem_contract_accepts(canonical)


def test_source_and_margin_mutations_break_the_independent_AST_inventory(
    tmp_path: Path,
) -> None:
    original_action_path = gate.V5671_SOURCE
    original_margin_path = gate.V5673_SOURCE
    try:
        action_text = original_action_path.read_text(encoding="utf-8")
        needle = "bulk = _relative_bulk_densities_td3(pulled, reference15, side=side)"
        assert action_text.count(needle) == 1
        mutant_action = tmp_path / original_action_path.name
        mutant_action.write_text(
            action_text.replace(
                needle,
                "bulk = _ghy_density_td3(pulled, side=side)",
            ),
            encoding="utf-8",
        )
        gate.V5671_SOURCE = mutant_action
        assert gate._real_formula_ast_inventory()["shallow_lexical_inventory_pass"] is False

        gate.V5671_SOURCE = original_action_path
        margin_text = original_margin_path.read_text(encoding="utf-8")
        margin_needle = '"so3_chart_r_minus",'
        assert margin_text.count(margin_needle) >= 1
        mutant_margin = tmp_path / original_margin_path.name
        mutant_margin.write_text(
            margin_text.replace(margin_needle, "", 1), encoding="utf-8"
        )
        gate.V5673_SOURCE = mutant_margin
        mutated_inventory = gate._real_formula_ast_inventory()
        assert mutated_inventory["shallow_lexical_inventory_pass"] is False
        assert mutated_inventory["analytic_margin_count"] == 15
    finally:
        gate.V5671_SOURCE = original_action_path
        gate.V5673_SOURCE = original_margin_path


def test_nested_formula_mutants_stay_fail_closed_even_after_sha_repin(
    tmp_path: Path,
) -> None:
    original_path = gate.V5671_SOURCE
    original_pins = gate.SOURCE_PINS
    source = original_path.read_text(encoding="utf-8")
    return_needle = (
        "return radial_fourth / (2.0 * (1.0 + radial_fourth).sqrt())"
    )
    call_needle = "V4 = _regular_v4_td3(Omega, phi)"
    assert source.count(return_needle) == 1
    assert source.count(call_needle) == 1

    variants = {
        "nested_abs_body": (
            source.replace(return_needle, "return abs(phi[0].body)", 1),
            "abs_body",
        ),
        "nested_branch": (
            source.replace(
                return_needle,
                "return radial_fourth if phi else radial_fourth / 2.0",
                1,
            ),
            "branch",
        ),
        "drop_nested_helper": (
            source.replace(call_needle, "V4 = phi[0]", 1),
            "drop_helper",
        ),
    }

    try:
        for identifier, (mutated_source, kind) in variants.items():
            directory = tmp_path / identifier
            directory.mkdir()
            mutant_path = directory / original_path.name
            mutant_path.write_text(mutated_source, encoding="utf-8")
            repinned = dict(original_pins)
            repinned[original_path.name] = hashlib.sha256(
                mutant_path.read_bytes()
            ).hexdigest()
            gate.V5671_SOURCE = mutant_path
            gate.SOURCE_PINS = repinned
            report = gate.build_report()
            assert report["source_pins"]["pass"] is True
            for key in (
                "twenty_real_formula_paths_and_sixteen_margin_inventory_ast_bound_pass",
                "uniform_twenty_primal_jvp_holder_lemma_pass",
                "bounded_margin_ball_weaker_jet_exact_formula_uniform_bridge_pass",
            ):
                assert report["decision"][key] is False

            diagnostic = report["real_formula_AST_inventory"][
                "transitive_source_diagnostic"
            ]
            if kind == "abs_body":
                row = diagnostic["functions_with_non_pure_python_features"][
                    "_regular_v4_td3"
                ]
                assert row["body_attribute_count"] == 1
                assert row["forbidden_builtin_calls"] == ["abs"]
                # This mutant preserves the old hand-picked edge inventory;
                # precisely that old inventory was not a semantic proof.
                assert report["real_formula_AST_inventory"][
                    "shallow_lexical_inventory_pass"
                ] is True
            elif kind == "branch":
                row = diagnostic["functions_with_non_pure_python_features"][
                    "_regular_v4_td3"
                ]
                assert row["branch_node_count"] == 1
            else:
                assert diagnostic["regular_v4_reachable"] is False
                assert report["real_formula_AST_inventory"][
                    "shallow_lexical_inventory_pass"
                ] is False
    finally:
        gate.V5671_SOURCE = original_path
        gate.SOURCE_PINS = original_pins


def test_leaf_guard_and_radial_exponent_mutants_die_fail_closed(
    tmp_path: Path,
) -> None:
    original_action_path = gate.V5671_SOURCE
    original_margin_path = gate.V5673_SOURCE
    original_pins = gate.SOURCE_PINS
    original_weight = gate.RADIAL_WEIGHT_POWER
    try:
        action = original_action_path.read_text(encoding="utf-8")
        leaf_needle = 'dphi = primitives["d_phi"]'
        assert action.count(leaf_needle) == 1
        leaf_directory = tmp_path / "leaf"
        leaf_directory.mkdir()
        leaf_mutant = leaf_directory / original_action_path.name
        leaf_mutant.write_text(
            action.replace(leaf_needle, 'dphi = primitives["phi"]', 1),
            encoding="utf-8",
        )
        repinned = dict(original_pins)
        repinned[original_action_path.name] = hashlib.sha256(
            leaf_mutant.read_bytes()
        ).hexdigest()
        gate.V5671_SOURCE = leaf_mutant
        gate.SOURCE_PINS = repinned
        leaf_report = gate.build_report()
        assert leaf_report["source_pins"]["pass"] is True
        assert leaf_report["real_formula_AST_inventory"][
            "shallow_lexical_inventory_pass"
        ] is False
        assert leaf_report["decision"][
            "twenty_real_formula_paths_and_sixteen_margin_inventory_ast_bound_pass"
        ] is False

        gate.V5671_SOURCE = original_action_path
        gate.SOURCE_PINS = original_pins
        margins = original_margin_path.read_text(encoding="utf-8")
        guard_needle = '"so3_chart_r_minus",'
        assert margins.count(guard_needle) >= 1
        guard_directory = tmp_path / "guard"
        guard_directory.mkdir()
        guard_mutant = guard_directory / original_margin_path.name
        guard_mutant.write_text(
            margins.replace(guard_needle, "", 1), encoding="utf-8"
        )
        gate.V5673_SOURCE = guard_mutant
        guard_report = gate.build_report()
        assert guard_report["real_formula_AST_inventory"][
            "analytic_margin_count"
        ] == 15
        assert guard_report["decision"][
            "uniform_twenty_primal_jvp_holder_lemma_pass"
        ] is False

        gate.V5673_SOURCE = original_margin_path
        gate.RADIAL_WEIGHT_POWER = 3
        try:
            gate.build_report()
        except gate.WeakerJetUniformBridgeError as error:
            assert "scoped theorem did not discharge" in str(error)
        else:
            raise AssertionError("radial weight exponent mutant survived")
    finally:
        gate.V5671_SOURCE = original_action_path
        gate.V5673_SOURCE = original_margin_path
        gate.SOURCE_PINS = original_pins
        gate.RADIAL_WEIGHT_POWER = original_weight


def test_no_q_gate_or_sampled_same_functional_is_a_positive_dependency() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    assert not any("v5_6_7_4" in name for name in imports)
    assert "q_frame_section_factorization_v5_6_7_4" not in source
    assert "route_c_same_functional_pointwise_v5_6_6_15" not in source
    inventory = gate.build_report()["real_formula_AST_inventory"]
    assert inventory["v5_6_7_4_consumed_as_positive_pin"] is False


def test_scientific_decision_path_has_no_float_literals_or_numerical_library() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    float_literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    ]
    assert float_literals == []
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert {"numpy", "scipy", "torch", "sympy", "decimal"}.isdisjoint(imported_roots)


def test_exact_same_norm_no_go_blocks_stronger_quantifier() -> None:
    no_go = gate.build_report()["exact_same_norm_no_go"]
    assert no_go["pass"] is True
    assert no_go["projection"] == "P_L f_L=0"
    assert no_go["same_norm_error"] == "||(I-P_L)f_L||_Hs=1"
    assert "margin" in no_go["margin_ball_compatibility"]
    assert "impossible" in no_go["conclusion"]


def test_report_is_json_serializable_and_cli_is_stable() -> None:
    expected = gate.build_report()
    encoded = json.dumps(expected, sort_keys=True, allow_nan=False)
    assert json.loads(encoded) == expected
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)],
        cwd=HERE,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(completed.stdout) == expected
