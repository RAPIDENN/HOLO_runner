#!/usr/bin/env python3
"""Tests for the conditional v5.6.7.3 margin/diagonal theorem ledger."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE
    / "derive_one_omega_topological_so3_direct_free_pointwise_margin_diagonal_v5_6_7_3_gate.py"
)
SPEC = importlib.util.spec_from_file_location("v5673_margin_diagonal", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def test_report_has_exact_true_false_allowlists() -> None:
    report = gate.build_report()
    decision = report["decision"]
    assert {key for key, value in decision.items() if value} == set(gate.TRUE_DECISION_KEYS)
    assert {key for key, value in decision.items() if not value} == set(gate.FALSE_DECISION_KEYS)
    assert len(decision) == len(gate.TRUE_DECISION_KEYS) + len(gate.FALSE_DECISION_KEYS)


def test_v5671_source_and_test_are_byte_pinned_and_every_guard_fragment_is_present() -> None:
    report = gate.build_report()["source_pins_and_guard_catalog"]
    assert report["pass"] is True
    assert report["source_observed_sha256"] == gate.V5671_SOURCE_SHA256
    assert report["test_observed_sha256"] == gate.V5671_TEST_SHA256
    assert all(report["required_source_fragment_matches"].values())
    assert (
        report["exact_primitives_source_observed_sha256"]
        == gate.V567_EXACT_PRIMITIVES_SOURCE_SHA256
    )
    assert (
        report["exact_primitives_test_observed_sha256"]
        == gate.V567_EXACT_PRIMITIVES_TEST_SHA256
    )
    assert all(report["required_exact_primitives_fragment_matches"].values())
    assert report["J3_catalog_structural_match"] is True
    assert hashlib.sha256(gate.V5671_SOURCE.read_bytes()).hexdigest() == gate.V5671_SOURCE_SHA256
    assert hashlib.sha256(gate.V5671_TEST.read_bytes()).hexdigest() == gate.V5671_TEST_SHA256


def test_guard_catalog_separates_analytic_class_runtime_and_discrete_resources() -> None:
    catalog = gate.guard_catalog()
    assert set(catalog) == {
        "analytic_open_margins",
        "historical_class_thresholds",
        "v5_6_7_1_runtime_open_gaps",
        "v5_6_7_1_discrete_resource_domain",
        "analytic_obligation_ids",
        "implementation_obligation_ids",
    }
    assert catalog["historical_class_thresholds"] == {
        "signature_min_abs_eigenvalue": 0.02,
        "Omega_minimum": 0.5,
        "negative_timelike_norm_clearance": 0.2,
        "each_of_q_r_plus_r_minus_cut_locus_clearance": 1.0,
    }
    resources = catalog["v5_6_7_1_discrete_resource_domain"]
    assert resources["tangential_order_per_axis"] == [1, 8]
    assert resources["gauss_legendre_order"] == [1, 16]
    assert "cannot instantiate" in resources["meaning"]
    charts = catalog["analytic_open_margins"]["SO3_charts_if_required"]
    assert set(charts) == {"q", "r_plus", "r_minus", "meaning"}
    assert "globally smooth" in charts["meaning"]
    runtime = catalog["v5_6_7_1_runtime_open_gaps"]
    j3 = runtime["so3_nonbody_each_exp"]
    assert gate._j3_catalog_accepts(j3)
    assert j3["maximum_nonbody_coefficient_keys_per_component"] == 69
    assert j3["maximum_nonbody_coefficient_keys_per_rotation_vector"] == 207
    assert "ghy_normal" in runtime
    assert "timelike" in runtime


def test_complete_shell_size_is_full_t4_and_rejects_malformed_radii() -> None:
    assert [gate.complete_shell_size(radius) for radius in range(4)] == [1, 81, 625, 2401]
    for malformed in (-1, True, 1.0, 1.5, "not-an-integer"):
        try:
            gate.complete_shell_size(malformed)
        except ValueError:
            pass
        else:
            raise AssertionError(f"malformed shell radius accepted: {malformed!r}")


def test_weighted_radial_bounds_and_gauss_constant_are_exact() -> None:
    assert gate.radial_basis_derivative_bounds(0) == (1, 12, 120)
    assert gate.radial_basis_derivative_bounds(3) == (1, 24, 408)
    assert gate.gauss_legendre_unit_interval_error_constant(1) == Fraction(1, 24)
    assert gate.gauss_legendre_unit_interval_error_constant(2) == Fraction(1, 4320)
    derivation = gate._radial_bound_derivation_ledger()
    assert derivation["pass"] is True
    assert derivation["definitions"] == {
        "x": "2rho-1",
        "w": "1-x^2",
        "b_j": "w^3 P_j(x)",
    }
    assert derivation["derived_sup_bounds"] == {
        "rho_order_0": "1",
        "rho_order_1": "12+4j",
        "rho_order_2": "120+80j+4j(j+1)",
    }
    assert derivation["weighted_Cauchy_Schwarz"]["coefficient_weight_power"] == 4
    assert (
        derivation["weighted_Cauchy_Schwarz"]["tail_exponent_formula"]
        == "2*m-2*weight_power"
    )
    assert derivation["weighted_Cauchy_Schwarz"][
        "squared_tail_asymptotic_exponents"
    ] == {"rho_order_0": -8, "rho_order_1": -6, "rho_order_2": -4}
    assert derivation["weighted_Cauchy_Schwarz"]["all_three_series_summable"] is True


def test_projection_lemma_is_strong_only_pointwise() -> None:
    ledger = gate.build_report()["complete_shell_and_radial_projection_lemma"]
    assert ledger["pass"] is True
    assert ledger["complete_shell"]["arbitrary_even_prefix_allowed"] is False
    assert ledger["complete_shell"]["H_t_operator_norm"] == 1
    assert ledger["exact_primitives_definition_pin_consumed"]["pass"] is True
    assert "no operator-norm convergence" in ledger["conclusion"]
    regularity = ledger["regularity_scope"]
    assert regularity["C3_tangential_boundary_free_fields_only"] == [
        "Y",
        "q",
        "r_plus",
        "r_minus",
    ]
    assert regularity["C3_fields_are_rho_independent"] is True
    assert regularity["C3_rho_derivative_or_full_collar_claimed"] is False
    assert all(
        exponent < -1
        for exponent in ledger["radial_basis_bounds"]["cauchy_schwarz_tail_exponents"].values()
    )


def test_projection_contract_kills_threshold_weight_and_C3_promotion_mutants() -> None:
    canonical = gate._canonical_projection_contract()
    assert gate._projection_contract_accepts(canonical)
    assert gate._projection_lemma_ledger(canonical)["pass"] is True

    s_gt_zero = gate._canonical_projection_contract()
    s_gt_zero["sobolev_threshold"] = {
        "parameter": "s",
        "strict_relation": ">",
        "bound": 0,
        "literal": "s>0",
    }
    assert not gate._projection_contract_accepts(s_gt_zero)
    assert gate._projection_lemma_ledger(s_gt_zero)["pass"] is False

    weight_zero = gate._canonical_projection_contract()
    weight_zero["radial_coefficient_weight_power"] = 0
    weight_zero_ledger = gate._projection_lemma_ledger(weight_zero)
    assert not gate._projection_contract_accepts(weight_zero)
    assert weight_zero_ledger["pass"] is False
    assert weight_zero_ledger["radial_basis_bounds"]["derivation"][
        "weighted_Cauchy_Schwarz"
    ]["squared_tail_asymptotic_exponents"] == {
        "rho_order_0": 0,
        "rho_order_1": 2,
        "rho_order_2": 4,
    }

    c3_full_collar = gate._canonical_projection_contract()
    c3_full_collar["regularity_scope"] = {
        **c3_full_collar["regularity_scope"],
        "C3_rho_derivative_or_full_collar_claimed": True,
    }
    assert not gate._projection_contract_accepts(c3_full_collar)
    assert gate._projection_lemma_ledger(c3_full_collar)["pass"] is False


def test_eventual_margin_quantifiers_are_fixed_member_and_tail_only() -> None:
    ledger = gate.build_report()["fixed_member_eventual_open_margin_lemma"]
    quantifiers = ledger["quantifiers"]
    assert ledger["pass"] is True
    contract = ledger["theorem_contract"]
    assert gate._eventual_margin_contract_accepts(contract)
    assert contract["sobolev_threshold"]["literal"] == "s>4"
    assert contract["scope"] == "analytic-only"
    assert contract["eventual_tail_order"]["order_literal"] == "n>=n0"
    assert (
        contract["eventual_tail_order"]["member_dependent_literal"]
        == "n>=n0(u)"
    )
    assert contract["runtime_eventual_promoted"] is False
    assert quantifiers["fixed_first"] == ["u"]
    assert quantifiers["exists_after_fixing_member"] == "n0(u)"
    assert quantifiers["early_truncations_claimed_admissible"] is False
    assert quantifiers["uniform_n0_over_balls_claimed"] is False
    assert quantifiers["uniform_rate_claimed"] is False
    assert "U_{epsilon/2}" in ledger["family_correction"]
    assert set(ledger["analytic_margin_obligations_only"]) == (
        gate.ANALYTIC_MARGIN_OBLIGATIONS
    )
    assert "TD3/float64" in ledger["runtime_nonconclusion"]
    assert ledger["unclosed_hypotheses"] and not any(ledger["unclosed_hypotheses"].values())
    assert {"so3_chart_q", "so3_chart_r_plus", "so3_chart_r_minus"} <= set(
        ledger["analytic_margin_obligations_only"]
    )


def test_exact_counterexamples_block_every_stronger_quantifier() -> None:
    ledger = gate.build_report()["exact_counterexamples"]
    assert ledger["pass"] is True
    witnesses = ledger["witnesses"]
    assert witnesses["early_projection_can_leave_open_margin"][
        "full_metric_positive_spatial_eigenvalue_minimum"
    ] == "7/50"
    assert witnesses["early_projection_can_leave_open_margin"][
        "P1_spatial_eigenvalue_at_pi"
    ] == "-1/5"
    shear = witnesses["pullback_shear_preserves_inertia_not_condition_guard"]
    assert shear["J"] == [[1, 0], [1000, 1]]
    assert shear["G_equals_J_transpose_reference_J"] == [
        [1000**2 - 1, 1000],
        [1000, 1],
    ]
    assert shear["det_G"] == -1
    assert math.isclose(
        shear["kappa_abs"], shear["lambda_plus"] ** 2, rel_tol=2.0e-16
    )
    assert shear["kappa_abs"] > shear["derived_kappa_abs_strict_lower_bound"]
    assert shear["kappa_abs"] > shear["v5_6_7_1_cap"]
    assert all(shear["derivation_checks"].values())
    assert witnesses["arbitrary_Qn_alias"]["detected"] is True
    assert witnesses["Q_to_2Q_refinement_can_share_alias"]["detected"] is True
    assert witnesses["fixed_resource_caps_preclude_infinite_diagonal"]["detected"] is True


def test_alias_witness_uses_exact_integer_turns() -> None:
    for order in (1, 2, 7, 31):
        assert gate._periodic_alias_exact(order, order)
        assert gate._periodic_alias_exact(2 * order, order)
        assert gate._periodic_alias_exact(2 * order, 2 * order)
    assert gate._periodic_alias_exact(3, 8) is False
    for malformed in ((True, 4), (4, False), (1.0, 4), (4, 2.0), (0, 4), (4, 0)):
        try:
            gate._periodic_alias_exact(*malformed)
        except ValueError:
            pass
        else:
            raise AssertionError(f"malformed alias arguments accepted: {malformed!r}")


def test_diagonal_selects_orders_after_member_and_budgets_twenty_atoms() -> None:
    ledger = gate.build_report()["fixed_member_action_jvp_diagonal_convergence_lemma"]
    assert ledger["pass"] is True
    assert ledger["quantifier_order"][2].startswith("form the fixed nth exact")
    assert ledger["quantifier_order"][3].startswith("only then choose")
    contract = ledger["theorem_contract"]
    assert gate._diagonal_convergence_contract_accepts(contract)
    assert len(ledger["existence_and_convergence_inputs"]) == 5
    assert [item["id"] for item in ledger["existence_and_convergence_inputs"]] == [
        item["id"] for item in gate.DIAGONAL_REQUIRED_EXISTENCE_INPUTS
    ]
    assert contract["quantifier_step_ids"].index(
        "form_fixed_nth_primal_and_JVP_integrands"
    ) < contract["quantifier_step_ids"].index(
        "choose_Qn_Gn_for_the_fixed_nth_integrands"
    )
    assert ledger["integrand_count"] == {"primal_atoms": 20, "jvp_atoms": 20}
    assert ledger["error_choice"]["each_primal_atom"] == "2^(-n)/20"
    assert ledger["error_choice"]["total_primal_quadrature_error_at_most"] == "2^(-n)"
    assert ledger["arbitrary_cofinal_Q_G_sufficient_for_changing_integrands"] is False
    assert ledger["constructive_rule_selection_claimed"] is False
    assert ledger["uniform_on_balls_claimed"] is False
    assert ledger["unclosed_hypotheses"] and not any(ledger["unclosed_hypotheses"].values())
    remainder = ledger["optional_computable_remainder_formula_not_certified_here"]
    assert remainder["L_x_definition"].endswith("Euclidean norm ||grad_x f||_2")
    assert "center" in remainder["periodic_cell_convention"]
    assert "2pi/Q" in remainder["periodic_cell_convention"]
    assert ledger["domain_separation"]["S_total"] == "formed only after the twenty separate integrals"


def test_every_required_mutant_is_effective() -> None:
    campaign = gate.build_report()["effective_mutants"]
    assert campaign["pass"] is True
    assert campaign["all_mutants_effective"] is True
    assert set(campaign["mutant_detected"]) == {
        "drop_pulled_reference_plus",
        "drop_ghy_normal_minus",
        "drop_frame_gram_pivot_2",
        "drop_q_chart",
        "drop_r_plus_chart",
        "drop_r_minus_chart",
        "drop_runtime_ghy_normal_minus",
        "drop_runtime_timelike_gap",
        "drop_eta_from_J3",
        "weaken_projection_sobolev_threshold_s_gt_4_to_s_gt_0",
        "weaken_projection_radial_weight_power_4_to_0",
        "promote_projection_C3_to_rho_full_collar",
        "weaken_sobolev_threshold_s_gt_4_to_s_gt_0",
        "reverse_eventual_tail_n_ge_n0_to_n_le_n0",
        "runtime_eventual_promoted",
        "drop_Gamma_projection_convergence",
        "drop_diagonal_Gamma_projection_convergence_input",
        "drop_twenty_primal_integrands_L1_convergence",
        "drop_twenty_JVP_integrands_L1_convergence",
        "choose_Q_G_before_fixed_nth_integrand",
        "drop_one_of_twenty_action_components",
        "repeat_boundary_with_radial_measure",
    }
    assert all(campaign["mutant_detected"].values())
    assert campaign["analytic_margin_mutants_pass"] is True
    assert campaign["projection_contract_mutants_pass"] is True
    assert campaign["runtime_catalog_mutants_pass"] is True
    assert campaign["eventual_theorem_contract_mutants_pass"] is True
    assert campaign["diagonal_theorem_contract_mutants_pass"] is True
    assert campaign["action_contract_mutants_pass"] is True


def test_theorem_contracts_fail_closed_on_every_no_go_mutation() -> None:
    eventual = gate._canonical_eventual_margin_contract()
    assert gate._eventual_margin_contract_accepts(eventual)

    s_gt_zero = gate._canonical_eventual_margin_contract()
    s_gt_zero["sobolev_threshold"] = {
        "parameter": "s",
        "strict_relation": ">",
        "bound": 0,
        "literal": "s>0",
    }
    assert not gate._eventual_margin_contract_accepts(s_gt_zero)
    assert gate._eventual_margin_lemma_ledger(s_gt_zero)["pass"] is False

    reversed_tail = gate._canonical_eventual_margin_contract()
    reversed_tail["eventual_tail_order"] = {
        "index": "n",
        "relation": "<=",
        "threshold": "n0(u)",
        "order_literal": "n<=n0",
        "member_dependent_literal": "n<=n0(u)",
    }
    assert not gate._eventual_margin_contract_accepts(reversed_tail)
    assert gate._eventual_margin_lemma_ledger(reversed_tail)["pass"] is False

    runtime_promoted = gate._canonical_eventual_margin_contract()
    runtime_promoted["runtime_eventual_promoted"] = True
    assert not gate._eventual_margin_contract_accepts(runtime_promoted)
    assert gate._eventual_margin_lemma_ledger(runtime_promoted)["pass"] is False

    no_Gamma_convergence = gate._canonical_eventual_margin_contract()
    no_Gamma_convergence["required_unclosed_hypotheses"].remove(
        "Gamma_maps_projection_convergence_to_the_consumed_C2_C3_jets"
    )
    assert not gate._eventual_margin_contract_accepts(no_Gamma_convergence)
    assert gate._eventual_margin_lemma_ledger(no_Gamma_convergence)["pass"] is False

    diagonal = gate._canonical_diagonal_convergence_contract()
    assert gate._diagonal_convergence_contract_accepts(diagonal)

    no_diagonal_Gamma_convergence = gate._canonical_diagonal_convergence_contract()
    no_diagonal_Gamma_convergence["existence_and_convergence_inputs"] = [
        item
        for item in no_diagonal_Gamma_convergence[
            "existence_and_convergence_inputs"
        ]
        if item["id"] != "Gamma_projection_convergence"
    ]
    assert not gate._diagonal_convergence_contract_accepts(
        no_diagonal_Gamma_convergence
    )
    assert (
        gate._diagonal_convergence_lemma_ledger(no_diagonal_Gamma_convergence)[
            "pass"
        ]
        is False
    )

    no_primal_L1 = gate._canonical_diagonal_convergence_contract()
    no_primal_L1["existence_and_convergence_inputs"] = [
        item
        for item in no_primal_L1["existence_and_convergence_inputs"]
        if item["id"] != "twenty_primal_integrands_L1_convergence"
    ]
    assert not gate._diagonal_convergence_contract_accepts(no_primal_L1)
    assert gate._diagonal_convergence_lemma_ledger(no_primal_L1)["pass"] is False

    rules_before_integrands = gate._canonical_diagonal_convergence_contract()
    rules_before_integrands["quantifier_step_ids"] = [
        "fix_member_and_tangent",
        "choose_complete_shell_and_radial_approximants",
        "choose_Qn_Gn_for_the_fixed_nth_integrands",
        "form_fixed_nth_primal_and_JVP_integrands",
    ]
    assert not gate._diagonal_convergence_contract_accepts(rules_before_integrands)
    assert gate._diagonal_convergence_lemma_ledger(rules_before_integrands)["pass"] is False


def test_inventory_validators_fail_closed_on_omissions_and_reordering() -> None:
    analytic_margins = sorted(gate.ANALYTIC_MARGIN_OBLIGATIONS)
    runtime_guards = sorted(gate.IMPLEMENTATION_MARGIN_OBLIGATIONS)
    assert gate._analytic_margin_inventory_accepts(analytic_margins)
    assert not gate._analytic_margin_inventory_accepts(analytic_margins[:-1])
    assert gate._runtime_guard_inventory_accepts(runtime_guards)
    assert not gate._runtime_guard_inventory_accepts(runtime_guards[:-1])
    assert gate._component_inventory_accepts(gate.EXPECTED_ACTION_COMPONENTS)
    assert not gate._component_inventory_accepts(gate.EXPECTED_ACTION_COMPONENTS[::-1])
    j3_catalog = gate.guard_catalog()["v5_6_7_1_runtime_open_gaps"][
        "so3_nonbody_each_exp"
    ]
    assert gate._j3_catalog_accepts(j3_catalog)
    assert not gate._j3_catalog_accepts(
        {**j3_catalog, "required_layers": {"primal_spatial_coefficients": {}}}
    )
    assert gate._domain_contract_accepts(
        {
            "bulk": "T4 x rho",
            "boundary": "T4 only",
            "total": "after twenty separate integrals",
        }
    )
    assert not gate._domain_contract_accepts(
        {
            "bulk": "T4 x rho",
            "boundary": "T4 x rho",
            "total": "after twenty separate integrals",
        }
    )


def test_no_numerical_certificate_or_promotion_is_claimed() -> None:
    report = gate.build_report()
    certificates = report["computable_finite_certificates"]
    assert certificates and not any(certificates.values())
    for key in gate.FALSE_DECISION_KEYS:
        assert report["decision"][key] is False
    assert "not proof-assistant derivations" in report["scope"]
    assert "No artifact" in report["scope"]


def test_module_is_stdlib_only_and_contains_no_file_write_path() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    assert imported_roots <= {
        "__future__",
        "hashlib",
        "json",
        "math",
        "fractions",
        "pathlib",
        "typing",
    }
    assert ".write_text(" not in source
    assert ".write_bytes(" not in source
    assert "open(" not in source


def test_main_prints_the_same_json_report_without_writing_artifacts() -> None:
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)],
        check=True,
        capture_output=True,
        text=True,
    )
    observed = json.loads(completed.stdout)
    expected = gate.build_report()
    assert observed == expected
    json.dumps(expected, allow_nan=False)
