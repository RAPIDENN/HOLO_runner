#!/usr/bin/env python3
"""Adversarial tests for the exact geometric v5.2 naturality certificate."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_geometric_bulk_diffeomorphism_naturality_v5_6_7_2_gate
    as gate,
)


@pytest.fixture(scope="session")
def report() -> dict:
    return gate.build_report()


def test_exact_upstream_byte_pins_and_literal_action_hash(report: dict) -> None:
    pins = report["source_pins"]
    for name, expected in gate.EXPECTED_SHA256.items():
        assert pins[name]["sha256"] == expected
    assert pins["v5_2_artifact"]["schema"] == gate.V52_SCHEMA
    assert pins["v5_6_1_artifact"]["schema"] == gate.V561_SCHEMA
    assert (
        pins["v5_2_artifact"]["canonical_exact_action_sha256"]
        == gate.V52_EXACT_ACTION_SHA256
    )
    assert tuple(pins["v5_2_artifact"]["interface_configuration"]) == (
        gate.EXPECTED_INTERFACE_CONFIGURATION
    )
    assert pins["v5_2_artifact"]["connection_trace_definition"] == (
        gate.EXPECTED_CONNECTION_TRACE_DEFINITION
    )
    assert pins["v5_2_artifact"]["pinned_BF_incidence_not_yet_consumed"] == (
        gate.EXPECTED_BF_INCIDENCE
    )
    assert pins["v5_6_1_historical_target_false"] is True
    assert "complete 5D metric, scalar, BF and matter" in pins[
        "v5_6_1_literal_open_obligation"
    ]


def test_literal_inventory_is_exactly_twenty_typed_top_forms(report: dict) -> None:
    inventory = report["literal_action_inventory"]
    assert inventory["pass"] is True
    assert inventory["component_count"] == 20
    assert tuple(inventory["component_order"]) == gate.COMPONENT_NAMES
    assert inventory["all_exact_action_keys_consumed"] is True
    assert inventory[
        "coherent_coefficients_and_signs_bound_by_byte_pin_not_by_naturality"
    ] is True
    assert len(inventory["rows"]) == len(gate.COMPONENT_NAMES)
    for row in inventory["rows"]:
        expected = gate.FORM5 if "_bulk_" in row["component"] else gate.FORM4
        assert row["root_type"] == gate.asdict(expected)
        assert row["source_keys"]
        assert row["required_fragments"]
        assert row["semantic_operator_signature"]
        assert row["naturality_axioms_used"]


def test_same_type_semantic_operator_swaps_are_rejected() -> None:
    _pins, v52, _v561 = gate._load_pinned_contracts()
    exact_action = v52["exact_classical_charter"]["exact_action"]
    bindings = gate.literal_component_bindings()
    baseline = gate.build_component_expressions("baseline")
    for left, right in (
        ("EH_bulk_plus", "Omega_kinetic_bulk_plus"),
        ("wall", "R_squared"),
        ("Robin", "K_foliation"),
    ):
        swapped = dict(baseline)
        swapped[left], swapped[right] = swapped[right], swapped[left]
        with pytest.raises(gate.NaturalityCertificateError):
            gate._validate_literal_inventory(exact_action, bindings, swapped)


def test_complete_domain_pullback_words_reduce_exactly(report: dict) -> None:
    ledger = report["complete_domain_pullback"]
    assert ledger["pass"] is True
    assert ledger[
        "complete_maps_are_auxiliary_domain_identifications_not_new_dynamical_fields"
    ] is True
    assert len(ledger["rows"]) == 2
    for row in ledger["rows"]:
        side = row["side"]
        assert row["expanded_pullback_word"] == [
            f"F_{side}",
            f"Phi_{side}^-1",
            f"Phi_{side}",
        ]
        assert row["reduced_pullback_word"] == [f"F_{side}"]
        assert row["baseline_pullback_word"] == [f"F_{side}"]
        assert row["exact_match"] is True
        assert row["reduction_steps"] == [
            {
                "rule": "adjacent_inverse_cancellation",
                "cancelled": [f"Phi_{side}^-1", f"Phi_{side}"],
                "remaining_prefix": [f"F_{side}"],
            }
        ]


def test_every_literal_component_has_a_real_normalization_trace(report: dict) -> None:
    finite = report["finite_naturality"]
    assert finite["pass"] is True
    assert finite["term_count"] == 20
    assert finite["no_absolute_noncompact_action_value_asserted"] is True
    assert tuple(row["component"] for row in finite["rows"]) == gate.COMPONENT_NAMES
    for row in finite["rows"]:
        assert row["exact_match"] is True
        assert row["transformed_expression"] != row["baseline_expression"]
        assert (
            row["normalized_transformed_expression"] == row["baseline_expression"]
        )
        pullback_rows = [
            item
            for item in row["transformed_reduction_trace"]
            if item["kind"] in {
                "pullback_word",
                "soldered_pullback_and_groupoid_words",
            }
        ]
        assert pullback_rows
        assert any(
            item.get("steps") or item.get("pullback_steps")
            for item in pullback_rows
        )


def test_two_side_raw_pullback_words_reduce_without_claiming_full_matching(
    report: dict,
) -> None:
    matching = report["two_side_raw_spacetime_pullback_words"]
    assert matching["pass"] is True
    assert len(matching["rows"]) == 4
    assert tuple(
        row["pinned_matching_premise"] for row in matching["rows"]
    ) == gate.EXPECTED_INTERFACE_CONFIGURATION
    for row in matching["rows"]:
        assert row["raw_side_pullback_words_reduce_exactly"] is True
        assert len(row["sides"]) == 2
        assert all(side["transformed_reduces_to_baseline"] for side in row["sides"])
    assert matching["scope"] == "raw spacetime pullback words only"
    assert matching["full_v5_2_groupoid_configuration_domain_transport_proved"] is False
    connection = next(row for row in matching["rows"] if row["field"] == "A")
    assert connection["affine_connection_trace_transport_status"] == (
        "checked_by_separate_exact_affine_ledger"
    )
    assert report["theorem_domain"]["interface_matching"] == list(
        gate.EXPECTED_INTERFACE_CONFIGURATION
    )


def test_typed_kernel_rejects_ill_typed_map_and_wrong_B_degree() -> None:
    complete_map, _phi, inverse = gate._side_maps("plus")
    with pytest.raises(gate.NaturalityCertificateError):
        gate.compose(complete_map, inverse)
    with pytest.raises(gate.NaturalityCertificateError):
        gate.construct(
            "invariant_B_wedge_F",
            gate.PulledField("B_degree_2", gate.ADJOINT2_5, ("F_plus",)),
            gate.PulledField("F_A", gate.ADJOINT2_5, ("F_plus",)),
        )


def test_operator_axioms_are_closed_and_not_term_specific(report: dict) -> None:
    kernel = report["proof_kernel"]
    assert kernel["status"] == "exact relative to the enumerated differential-geometric axioms"
    assert kernel["operator_count"] == len(gate.OPERATOR_SPECS)
    assert set(kernel["axioms"]) == gate.EXPECTED_KERNEL_AXIOMS
    assert set(kernel["expected_allowed_axioms"]) == gate.EXPECTED_KERNEL_AXIOMS
    assert kernel["exact_allowed_axiom_set_match"] is True
    assert set(kernel["consumed_axioms"]) == gate.EXPECTED_KERNEL_AXIOMS
    assert kernel["unused_allowed_axioms"] == []
    assert kernel["consumed_unexpected_axioms"] == []
    assert kernel["every_allowed_axiom_consumed_exactly"] is True
    assert gate._consumed_kernel_axioms(
        gate.build_component_expressions("finite")
    ) == gate.EXPECTED_KERNEL_AXIOMS
    assert {
        spec.naturality_axiom for spec in gate.OPERATOR_SPECS.values()
    }.issubset(set(kernel["axioms"]))
    assert set(kernel["operators"]).isdisjoint(gate.COMPONENT_NAMES)


def test_groupoid_word_is_exact_and_effective_mutants_fail(report: dict) -> None:
    groupoid = report["finite_associated_matter_solder_groupoid"]
    assert groupoid["pass"] is True
    assert groupoid["scope"] == "associated matter solder E R phi only"
    assert groupoid["affine_connection_trace_transport_claimed"] is False
    assert groupoid["source_component"] == "Robin"
    assert groupoid["source_node_kind"] == "SolderedMatter"
    assert groupoid["source_node_binding_exact"] is True
    assert groupoid["transformed_word"] == [
        "E",
        "gQ^-1",
        "gQ",
        "R",
        "gP^-1",
        "gP",
        "phi",
    ]
    assert groupoid["transformed_word"] == groupoid["expected_transformed_word"]
    assert groupoid["reduced_word"] == ["E", "R", "phi"]
    assert groupoid["reduced_word"] == groupoid["baseline_word"]
    assert groupoid["baseline_word"] == groupoid["expected_baseline_word"]
    omitted = gate._groupoid_ledger("baseline")
    assert omitted["pass"] is False
    assert omitted["source_node_binding_exact"] is False
    mutants = report["effective_mutants"]
    assert mutants["pass"] is True
    assert mutants["mutant_count"] >= 21
    assert all(row["killed"] for row in mutants["rows"].values())
    assert "Robin" in mutants["rows"]["frozen_frame"]["mismatched_components"]
    assert "Robin" in mutants["rows"]["missing_source_inverse"][
        "mismatched_components"
    ]
    assert mutants["rows"]["BF_field_pullback_omitted"]["mismatched_components"] == [
        "BF_bulk_plus"
    ]
    assert set(
        mutants["rows"]["GHY_outward_normal_frozen"]["mismatched_components"]
    ) == {"GHY_plus", "GHY_minus"}
    for name in (
        "semantic_operator_swap_EH_bulk_plus_with_Omega_kinetic_bulk_plus",
        "semantic_operator_swap_wall_with_R_squared",
        "semantic_operator_swap_Robin_with_K_foliation",
    ):
        assert mutants["rows"][name]["killed"] is True
    assert mutants["rows"]["semantic_leaf_Omega_to_unrelated_scalar"][
        "killed"
    ] is True
    assert mutants["rows"]["semantic_leaf_varphi_H_to_unrelated_vector"][
        "killed"
    ] is True
    assert mutants["rows"]["missing_chain_rule_axiom"]["killed"] is True
    assert mutants["rows"]["finite_groupoid_transport_omitted"]["killed"] is True


def test_groupoid_ledger_reads_the_actual_Robin_soldered_node(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = gate._soldered_matter

    def omit_finite_transport(
        mode: str,
        groupoid_mode: str,
    ) -> gate.SolderedMatter:
        node = original(mode, groupoid_mode)
        if mode == "finite" and groupoid_mode == "finite":
            return gate.SolderedMatter(
                node.name,
                node.type_tag,
                node.pullback_factors,
                ("E", "R", "phi"),
            )
        return node

    monkeypatch.setattr(gate, "_soldered_matter", omit_finite_transport)
    ledger = gate._groupoid_ledger()
    assert ledger["transformed_word"] == ["E", "R", "phi"]
    assert ledger["source_node_binding_exact"] is False
    assert ledger["pass"] is False
    with pytest.raises(gate.NaturalityCertificateError):
        gate.build_report()


def test_affine_connection_trace_is_exact_on_both_real_A_routes(
    report: dict,
) -> None:
    affine = report["finite_affine_connection_trace_transport"]
    assert affine["pass"] is True
    assert affine["pinned_connection_trace_definition"] == (
        gate.EXPECTED_CONNECTION_TRACE_DEFINITION
    )
    assert affine["pinned_common_interface_configuration"] == (
        gate.EXPECTED_INTERFACE_CONFIGURATION[3]
    )
    assert "one shared q" in affine["formal_domain"]["group_maps"]
    assert affine["formal_domain"]["coefficient_ring"] == "exact integers"
    assert affine["formal_domain"]["word_product"] == (
        "associative and noncommutative"
    )
    assert affine["target_gauge_atoms_by_side"] == ["q", "q"]
    assert affine["same_literal_q_and_dq_used_on_both_sides"] is True
    assert affine["two_transformed_interface_traces_remain_equal"] is True
    assert affine["common_transformed_A_Sigma_terms"] == [
        {"coefficient": -1, "word": ["d_q", "q^-1"]},
        {"coefficient": 1, "word": ["q", "A_Sigma", "q^-1"]},
    ]
    assert set(affine["consumed_kernel_rules"]) == (
        gate.EXPECTED_AFFINE_KERNEL_RULES
    )
    assert affine["every_affine_kernel_rule_consumed_exactly"] is True
    assert affine["BF_incidence_or_Green_identity_claimed"] is False

    assert len(affine["binding_rows"]) == 2
    for binding in affine["binding_rows"]:
        side = binding["side"]
        assert binding["pass"] is True
        assert binding["connection_atom"] == f"A_{side}"
        assert binding["source_gauge_atom"] == f"p_{side}"
        assert binding["transition_atom"] == f"r_{side}"
        assert binding["target_gauge_atom"] == "q"
        assert binding["exactly_two_action_component_routes"] is True
        assert binding["two_semantic_routes_not_two_AST_visits"] is True
        assert binding[
            "same_structural_A_e_symbol_type_pullback_on_both_routes"
        ] is True
        routes = binding["actual_action_component_routes"]
        assert [row["component"] for row in routes] == [
            f"P_kinetic_bulk_{side}",
            f"BF_bulk_{side}",
        ]
        assert [row["raw_AST_connection_occurrence_count"] for row in routes] == [
            2,
            1,
        ]
        assert [
            row["distinct_structural_connection_node_count"] for row in routes
        ] == [1, 1]
        assert all(
            row["all_occurrences_are_the_same_expected_A_e"]
            and row[
                "one_structural_A_e_symbol_type_pullback_on_this_route"
            ]
            and row["structural_multiplicity_is_exact"]
            for row in routes
        )

    assert len(affine["side_polynomial_identities"]) == 2
    for row in affine["side_polynomial_identities"]:
        side = row["side"]
        assert row["pass"] is True
        assert row["r_prime_word"] == ["q", f"r_{side}", f"p_{side}^-1"]
        assert row["r_prime_inverse_word"] == [
            f"p_{side}",
            f"r_{side}^-1",
            "q^-1",
        ]
        assert row["r_prime_inverse_word"] == row[
            "expected_r_prime_inverse_word"
        ]
        assert [
            item["Leibniz_slot"] for item in row["d_r_prime_Leibniz_trace"]
        ] == [0, 1, 2]
        inverse_row = row["d_r_prime_Leibniz_trace"][2]
        assert inverse_row["group_atom"] == f"p_{side}^-1"
        assert inverse_row["atom_derivative_terms"] == [
            {
                "coefficient": -1,
                "word": [f"p_{side}^-1", f"d_p_{side}", f"p_{side}^-1"],
            }
        ]
        assert row["source_dp_cancels_exactly"] is True
        assert row["source_dp_cancellation_terms"] == []
        assert row["source_trace_matches_bound_Trans_r_A"] is True
        assert row["common_interface_substitution"] == (
            "Trans_r_e(A_e)->A_Sigma"
        )
        assert row["common_interface_substitution_applied"] is True
        assert row["residual_terms"] == []
        assert row["polynomial_identity_exact"] is True
        assert row["lhs_terms"] == row["rhs_terms"]
        assert row["lhs_terms"] == row["expected_normal_form_terms"]
        distribution = row["distributive_expansion_witness"]
        assert distribution["lhs_conjugation_of_sum_terms"] == distribution[
            "lhs_sum_of_conjugated_terms"
        ]
        assert distribution["rhs_conjugation_of_sum_terms"] == distribution[
            "rhs_sum_of_conjugated_terms"
        ]
        assert all(row["kernel_rule_checks"].values())

    with pytest.raises(gate.NaturalityCertificateError):
        gate._affine_side_identity(affine["binding_rows"][0], "unknown_mutant")
    _pins, v52, _v561 = gate._load_pinned_contracts()
    with pytest.raises(gate.NaturalityCertificateError):
        gate._affine_connection_trace_ledger(
            v52,
            gate._interface_raw_pullback_ledger(),
            side_mutations={"detached_side": "exact"},
        )
    with pytest.raises(gate.NaturalityCertificateError):
        gate._affine_connection_trace_ledger(
            v52,
            gate._interface_raw_pullback_ledger(),
            target_gauges={"detached_side": "q"},
        )


def test_affine_mutants_are_effective_and_binding_is_not_detached(
    report: dict,
) -> None:
    mutants = report["affine_connection_trace_effective_mutants"]
    assert mutants["pass"] is True
    assert mutants["mutant_count"] == 16
    assert all(row["killed"] for row in mutants["rows"].values())
    for name in (
        "missing_source_affine_term",
        "wrong_source_affine_sign",
        "missing_target_affine_term",
        "wrong_target_affine_sign",
        "wrong_inverse_derivative_sign",
        "wrong_inverse_derivative_order",
        "omit_p_Leibniz_term",
        "omit_r_Leibniz_term",
        "omit_q_Leibniz_term",
        "wrong_r_prime_inverse_order",
        "frozen_r_transport",
        "r_factor_omitted_from_transport",
        "source_inverse_omitted_from_r_transport",
    ):
        assert mutants["rows"][name]["residual_terms"]
    split = mutants["rows"]["split_target_q_between_sides"]
    assert split["target_gauge_atoms"] == ["q_plus", "q_minus"]
    detached = mutants["rows"][
        "detached_hard_coded_ledger_from_BF_connection_route"
    ]["detached_route"]
    assert detached["all_occurrences_are_the_same_expected_A_e"] is False
    duplicated = mutants["rows"][
        "duplicated_A_occurrence_on_P_kinetic_route"
    ]["duplicated_route"]
    assert duplicated["raw_AST_connection_occurrence_count"] == 3
    assert duplicated["structural_multiplicity_is_exact"] is False
    assert duplicated["all_occurrences_are_the_same_expected_A_e"] is True
    assert duplicated["distinct_structural_connection_node_count"] == 1
    assert duplicated[
        "one_structural_A_e_symbol_type_pullback_on_this_route"
    ] is True


def test_Cartan_signs_reduce_as_exact_integer_combinations(report: dict) -> None:
    cartan = report["formal_local_compact_support_chain_rule_corollary"][
        "Cartan_bulk_sign_ledger"
    ]
    assert cartan["pass"] is True
    assert cartan["residuals"] == {
        "connection": [],
        "associated_scalar": [],
        "adjoint_three_form": [],
    }
    for mutant in ("connection_sign", "matter_sign", "omit_D_iB"):
        mutated = gate._cartan_ledger(mutant)
        assert mutated["pass"] is False
        assert any(mutated["residuals"].values())


def test_local_DS_is_only_the_formal_compact_support_chain_rule_corollary(
    report: dict,
) -> None:
    corollary = report["formal_local_compact_support_chain_rule_corollary"]
    assert corollary["pass"] is True
    assert corollary["prerequisites"] == {
        "byte_pins_and_canonical_v5_2_action": True,
        "literal_twenty_component_inventory": True,
        "complete_domain_pullback": True,
        "two_side_raw_spacetime_pullback_words_reduce_exactly": True,
        "twenty_component_finite_naturality": True,
        "finite_associated_matter_solder_covariance": True,
    }
    assert corollary["prerequisite_names_match"] is True
    assert set(corollary["required_chain_rule_axioms"]) == (
        gate.FORMAL_LOCAL_REQUIRED_AXIOMS
    )
    assert corollary["missing_required_chain_rule_axioms"] == []
    assert corollary["unexpected_kernel_axioms"] == []
    assert corollary["exact_allowed_kernel_axiom_set_match"] is True
    assert set(corollary["consumed_kernel_axioms"]) == (
        gate.EXPECTED_KERNEL_AXIOMS
    )
    assert corollary["unused_allowed_kernel_axioms"] == []
    assert corollary["consumed_unexpected_kernel_axioms"] == []
    assert corollary["every_allowed_kernel_axiom_consumed_exactly"] is True
    assert corollary["Euler_equations_imposed"] is False
    assert corollary["local_Green_or_stratified_Ward_identity_claimed"] is False
    assert "D_local S_v5.2" in corollary["formal_chain_rule_identity"]
    flow = corollary["flow_generators_derived_from_finite_map_words"]
    assert flow["pass"] is True
    for row in flow["rows"]:
        assert row["complete_map_generator_coefficient"] == -1
        assert row["physical_field_Lie_generator_coefficient"] == 1
        assert row["pulled_field_total_generator_coefficient"] == 0
    all_true = {name: True for name in gate.FORMAL_LOCAL_PREREQUISITES}
    assert gate._formal_local_chain_rule_ledger(
        all_true, flow_mode="wrong_inverse_complete_map"
    )["pass"] is False
    assert gate._formal_local_chain_rule_ledger({})["pass"] is False
    assert gate._formal_local_chain_rule_ledger({"arbitrary": True})["pass"] is False
    one_false = dict(all_true)
    one_false["byte_pins_and_canonical_v5_2_action"] = False
    assert gate._formal_local_chain_rule_ledger(one_false)["pass"] is False
    missing_chain_rule = tuple(
        axiom
        for axiom in gate.KERNEL_AXIOMS
        if axiom != "chain_rule_for_smooth_local_functionals"
    )
    assert gate._formal_local_chain_rule_ledger(
        all_true, available_axioms=missing_chain_rule
    )["pass"] is False
    assert gate._formal_local_chain_rule_ledger(
        all_true, available_axioms=gate.KERNEL_AXIOMS + ("magic_axiom",)
    )["pass"] is False
    assert gate._formal_local_chain_rule_ledger(
        all_true,
        consumed_axioms=tuple(
            gate.EXPECTED_KERNEL_AXIOMS - {"curvature_is_natural"}
        ),
    )["pass"] is False
    assert gate._formal_local_chain_rule_ledger(
        all_true,
        consumed_axioms=tuple(gate.EXPECTED_KERNEL_AXIOMS)
        + ("magic_axiom",),
    )["pass"] is False


def test_transformed_pair_does_not_promote_frozen_background_gauge(report: dict) -> None:
    exclusion = report["excluded_fixed_background_relative_contract"]
    assert exclusion["transformed_pair"]["pair_covariance_exact"] is True
    assert exclusion["frozen_external_background"]["full_gauge_identity"] is False
    witness = exclusion["normal_interface_flux_counterexample"]
    assert witness["nonzero_under_the_stated_assumptions"] is True
    assert witness["unconditional_nonzero_claimed"] is False
    assert witness["conditional_nonzero_assumptions"] == [
        "c != 0",
        "f(0) != 0",
        "Vol(Sigma) != 0",
    ]
    assert exclusion["normal_interface_flux_counterexample"]["uncancelled_flux"] == (
        "c f(0) Vol(Sigma)"
    )


def test_only_finite_covariance_and_formal_local_corollary_are_promoted(
    report: dict,
) -> None:
    decision = report["decision"]
    assert set(decision) == gate.TRUE_DECISION_KEYS | gate.FALSE_DECISION_KEYS
    assert {key for key, value in decision.items() if value} == gate.TRUE_DECISION_KEYS
    assert {key for key, value in decision.items() if not value} == gate.FALSE_DECISION_KEYS
    assert decision[
        "finite_typed_geometric_S_v5_2_action_expression_covariance_exact_pass"
    ] is True
    assert decision[
        "formal_local_compact_support_chain_rule_corollary_DS_G_zero_exact_pass"
    ] is True
    assert decision[
        "finite_full_affine_connection_trace_transport_exact_pass"
    ] is True
    assert report["theorem_domain"][
        "full_affine_connection_trace_transport_in_this_certificate"
    ] is True
    for key in (
        "fixed_reference_S_rel_diffeomorphism_Ward_pass",
        "oriented_BF_incidence_cancellation_exact_pass",
        "literal_bulk_interface_Green_ledger_pass",
        "differentiated_smooth_compact_support_bulk_Ward_identity_exact_pass",
        "full_bulk_diffeomorphism_Ward_pass",
        "complete_moving_embedding_Ward_pass",
        "complete_v5_2_all_field_normal_embedding_pass",
        "full_off_shell_Green_theorem_accepted",
        "global_noncompact_action_finite_pass",
        "continuum_all_configurations_theorem_pass",
        "full_classical_variational_principle_selected_sector_pass",
        "numerical_sample_constitutes_naturality_proof_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "P4_full_same_action_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False
    opens = report["open_local_Ward_obligations"]
    assert set(opens) == {
        "oriented_BF_incidence",
        "literal_bulk_interface_Green_ledger",
        "Noether_current_definition",
    }
    assert "does not close" in report["explicit_exclusions"]["promotion"]


def test_source_is_stdlib_only_and_has_no_numerical_or_relative_action_dependency() -> None:
    path = Path(gate.__file__)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[str] = []
    called_attributes: list[str] = []
    assigned_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            called_attributes.append(node.func.attr)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            assigned_names.extend(
                target.id for target in targets if isinstance(target, ast.Name)
            )
    assert set(imports).issubset(
        {"__future__", "dataclasses", "hashlib", "json", "pathlib", "typing"}
    )
    assert not any(name in imports for name in ("numpy", "torch", "sympy", "mpmath"))
    assert "route_c_full_t4_dual_local_action_v5_6_7_1" not in source
    assert not any(name in called_attributes for name in ("write_text", "write_bytes"))
    assert not any("TOLERANCE" in name.upper() for name in assigned_names)


def test_report_is_deterministic_JSON_and_writes_no_artifact(report: dict) -> None:
    again = gate.build_report()
    assert again == report
    encoded = json.dumps(report, sort_keys=True, allow_nan=False)
    assert encoded
    assert not hasattr(gate, "OUTPUT")
