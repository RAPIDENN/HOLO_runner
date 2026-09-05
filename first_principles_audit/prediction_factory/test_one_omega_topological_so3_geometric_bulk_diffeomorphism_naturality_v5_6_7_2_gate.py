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
    assert pins["v5_2_artifact"]["pinned_BF_incidence_contract"] == (
        gate.EXPECTED_BF_INCIDENCE
    )
    assert pins["v5_2_artifact"]["BF_action_literal"] == (
        gate.EXPECTED_BF_ACTION_LITERAL
    )
    assert pins["v5_2_artifact"]["adjoint_form_trace_definition"] == (
        gate.EXPECTED_ADJOINT_FORM_TRACE_DEFINITION
    )
    assert pins["v5_2_artifact"]["BF_Green_form"] == gate.EXPECTED_BF_GREEN_FORM
    assert pins["v5_2_artifact"]["BF_natural_interface_equation"] == (
        gate.EXPECTED_BF_NATURAL_INTERFACE_EQUATION
    )
    assert pins["v5_2_artifact"]["BF_bulk_equation_A"] == (
        gate.EXPECTED_BF_BULK_EQUATION_A
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


def test_oriented_BF_incidence_is_aggregated_off_shell_not_cancelled(
    report: dict,
) -> None:
    ledger = report["oriented_BF_incidence_aggregation"]
    assert ledger["pass"] is True
    assert ledger["pinned_literals"] == {
        "BF_action": gate.EXPECTED_BF_ACTION_LITERAL,
        "adjoint_form_trace": gate.EXPECTED_ADJOINT_FORM_TRACE_DEFINITION,
        "common_interface_variations": gate.EXPECTED_COMMON_INTERFACE_VARIATIONS,
        "Green_form": gate.EXPECTED_BF_GREEN_FORM,
        "natural_B_flux_equation": gate.EXPECTED_BF_INCIDENCE,
        "natural_interface_BF_flux": gate.EXPECTED_BF_NATURAL_INTERFACE_EQUATION,
    }
    assert ledger["literal_BF_component_bindings_exact"] is True
    assert len(ledger["actual_BF_action_route_bindings"]) == 2
    for row in ledger["actual_BF_action_route_bindings"]:
        side = row["side"]
        assert row["pass"] is True
        assert row["component"] == f"BF_bulk_{side}"
        assert row["root_operator"] == "invariant_B_wedge_F"
        assert row["B_occurrence_count"] == 1
        assert row["A_occurrence_count"] == 1
        assert row["B_symbols"] == [f"B_{side}"]
        assert row["A_symbols"] == [f"A_{side}"]
        assert row["expected_B_symbol_type_pullback"]["symbol"] == f"B_{side}"
        assert row["expected_A_symbol_type_pullback"]["symbol"] == f"A_{side}"
    assert ledger["all_BF_boundary_atoms_derived_from_typed_trace_rows"] is True
    trace_rows = ledger["typed_B_and_affine_target_trace_binding_rows"]
    assert len(trace_rows) == 2
    for row in trace_rows:
        side = row["side"]
        assert row["pass"] is True
        assert row["mutation"] == "exact"
        assert row["source_B_node_from_actual_BF_action"]["symbol"] == f"B_{side}"
        assert row["adjoint_trace_input_node"] == row[
            "source_B_node_from_actual_BF_action"
        ]
        assert row["adjoint_trace_transition_atom_from_affine_binding"] == f"r_{side}"
        assert row["adjoint_trace_output_atom"] == f"b_{side}"
        assert row["source_B_node_bound_to_adjoint_trace"] is True
        assert row["source_A_node_from_actual_BF_action"]["symbol"] == f"A_{side}"
        assert row["affine_source_connection_atom"] == f"A_{side}"
        assert row["affine_common_target_atom"] == "A_Sigma"
        assert row[
            "boundary_variation_atom_derived_from_affine_target"
        ] == "Delta_A_Sigma"
        assert row[
            "source_A_node_bound_through_affine_trace_to_variation"
        ] is True
        assert row["affine_common_target_terms"]
    assert ledger["orientation_sign_rows"] == [
        {
            "side": "plus",
            "s_epsilon": 1,
            "boundary_variation_atom": "Delta_A_Sigma",
        },
        {
            "side": "minus",
            "s_epsilon": -1,
            "boundary_variation_atom": "Delta_A_Sigma",
        },
    ]
    assert ledger["oriented_flux_terms"] == [
        ("b_minus", -1),
        ("b_plus", 1),
    ]
    assert ledger["expected_b_plus_minus_b_minus_terms"] == ledger[
        "oriented_flux_terms"
    ]
    assert ledger["common_Delta_A_Sigma_factored"] is True
    assert ledger["oriented_boundary_integrand_terms"] == [
        ("b_minus_wedge_Delta_A_Sigma", 1),
        ("b_plus_wedge_Delta_A_Sigma", -1),
    ]
    assert ledger["expected_boundary_integrand_terms"] == ledger[
        "oriented_boundary_integrand_terms"
    ]
    assert ledger["off_shell_oriented_flux_is_nonzero"] is True
    assert ledger["off_shell_cancellation_claimed"] is False
    assert ledger["natural_interface_equation_quotient_rule_consumed"] is True
    assert ledger["flux_terms_mod_natural_interface_equation"] == []
    assert ledger["on_shell_cancellation_only"] is True
    assert ledger["full_Green_or_Ward_identity_claimed"] is False
    assert ledger[
        "decision_also_requires_separate_affine_connection_trace_pass"
    ] is True


def test_BF_incidence_mutants_and_literal_drift_are_fail_closed(
    report: dict,
) -> None:
    mutants = report["oriented_BF_incidence_effective_mutants"]
    assert mutants["pass"] is True
    assert mutants["mutant_count"] == 9
    assert all(row["killed"] for row in mutants["rows"].values())
    assert set(mutants["rows"]) == {
        "same_orientation_sign",
        "reversed_orientation_signs",
        "minus_side_omitted",
        "split_Delta_A_between_sides",
        "wrong_global_boundary_sign",
        "detached_B_from_actual_BF_route",
        "detached_A_from_actual_BF_route",
        "detached_b_trace",
        "detached_affine_target",
    }
    assert mutants["rows"]["detached_b_trace"]["plus_trace_binding"][
        "source_B_node_bound_to_adjoint_trace"
    ] is False
    assert mutants["rows"]["detached_affine_target"]["plus_trace_binding"][
        "source_A_node_bound_through_affine_trace_to_variation"
    ] is False

    _pins, v52, _v561 = gate._load_pinned_contracts()
    baseline = gate._bf_incidence_aggregation_ledger(v52)
    assert baseline["pass"] is True
    mutation_paths = (
        ("exact_classical_charter", "exact_action", "BF"),
        ("exact_classical_charter", "definitions", "adjoint_form_trace"),
        ("exact_classical_charter", "interface_domain", "natural_B_flux_equation"),
        ("Green_form_certificate", "Green_form"),
        ("Green_form_certificate", "natural_interface_equations", "BF_flux"),
    )
    for path in mutation_paths:
        mutated = json.loads(json.dumps(v52))
        target = mutated
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = "mutated"
        assert gate._bf_incidence_aggregation_ledger(mutated)["pass"] is False
    mutated = json.loads(json.dumps(v52))
    mutated["exact_classical_charter"]["interface_domain"]["variations"][0] = (
        "split variations"
    )
    assert gate._bf_incidence_aggregation_ledger(mutated)["pass"] is False

    with pytest.raises(gate.NaturalityCertificateError):
        gate._bf_incidence_aggregation_ledger(
            v52,
            orientation_signs={"plus": 1},
        )
    with pytest.raises(gate.NaturalityCertificateError):
        gate._bf_incidence_aggregation_ledger(
            v52,
            orientation_signs={"plus": 1, "minus": False},
        )
    with pytest.raises(gate.NaturalityCertificateError):
        gate._bf_incidence_aggregation_ledger(
            v52,
            variation_atoms={"plus": "Delta_A_Sigma", "detached": "Delta_A_Sigma"},
        )
    with pytest.raises(gate.NaturalityCertificateError):
        gate._bf_incidence_aggregation_ledger(v52, boundary_prefactor=True)


def test_literal_Green_ledger_consumes_20_components_in_18_real_AST_rows(
    report: dict,
) -> None:
    ledger = report["literal_bulk_interface_Green_ledger"]
    assert ledger["pass"] is True
    assert ledger["row_count"] == ledger["expected_row_count"] == 18
    assert ledger["component_count_with_multiplicity"] == 20
    assert ledger["expected_component_count"] == len(gate.COMPONENT_NAMES) == 20
    assert ledger["actual_component_keys_are_exactly_COMPONENT_NAMES"] is True
    assert set(ledger["actual_component_keys"]) == set(gate.COMPONENT_NAMES)
    assert ledger["exact_twenty_component_multiset"] is True
    assert ledger["component_multiplicities"] == {
        component: 1 for component in gate.COMPONENT_NAMES
    }
    assert ledger["observed_row_layout"] == ledger["expected_row_layout"]
    assert ledger["candidate_rows_derived_from_AST_not_expected_layout"] is True
    assert ledger["AST_classification_issues"] == []
    assert len(ledger["AST_derived_component_classifications"]) == 20
    assert tuple(
        (row["name"], tuple(row["components"])) for row in ledger["rows"]
    ) == gate.EXPECTED_GREEN_ROW_LAYOUT
    assert ledger["literal_and_geometric_axiom_contract"][
        "all_literal_and_geometric_axiom_pins_exact"
    ] is True
    assert ledger["literal_and_geometric_axiom_contract"][
        "Green_form_text_used_as_proof_target"
    ] is False
    for row in ledger["rows"]:
        assert row["pass"] is True
        assert row["row_layout_exact"] is True
        assert row["component_names_match_expression_bindings"] is True
        assert row["bulk_euler_pairing_exact"] is True
        assert row["bulk_euler_terms_exact"] is True
        assert row["row_family_and_side_match_AST_classifications"] is True
        assert row["derivation_kind_matches_independent_target"] is True
        assert row["local_d5_divergence_recorded_exactly_for_bulk_row"] is True
        assert row["intrinsic_delta_exact_and_unexpanded"] is True
        assert row["source_literal_keys"]
        assert row["component_bindings"]
        for binding in row["component_bindings"]:
            assert binding[
                "structurally_equal_to_real_component_expression"
            ] is True
            assert binding["full_AST_fingerprint_exact"] is True
            assert binding[
                "AST_family_and_side_match_independent_component_target"
            ] is True
            assert binding["observed_full_AST_fingerprint_sha256"] == binding[
                "independent_expected_full_AST_fingerprint_sha256"
            ]
            assert binding["semantic_signature_exact"] is True
            assert binding["leaf_multiset_exact"] is True
            assert binding["observed_leaf_multiset"] == binding[
                "expected_leaf_multiset"
            ]
            assert binding["exact_symbolic_weight"] is True
            assert binding["observed_weight"] == binding["expected_weight"]
            assert binding["observed_weight"]["uses_floating_point"] is False

    for side in gate.SIDES:
        eh = next(row for row in ledger["rows"] if row["name"] == f"EH_GHY_{side}")
        assert eh["components"] == [f"EH_bulk_{side}", f"GHY_{side}"]
        assert eh["derivation_kind"] == "explicit_geometric_EH_plus_GHY_axiom"
        assert eh["local_divergence"] == f"d_5(theta_EH_GHY_{side})"
    p_plus = next(row for row in ledger["rows"] if row["name"] == "P_kinetic_plus")
    leafs = p_plus["component_bindings"][0]["observed_leaf_multiset"]
    assert leafs == [["A", 2], ["Omega", 2], ["g", 2], ["phi", 4]]


def test_Green_candidate_layout_and_fingerprints_are_independent_of_the_oracle() -> None:
    baseline = gate.build_component_expressions("baseline")
    layout, classifications, issues = gate._derive_green_candidate_layout_from_AST(
        baseline
    )
    assert layout == gate.EXPECTED_GREEN_ROW_LAYOUT
    assert len(classifications) == len(gate.COMPONENT_NAMES)
    assert issues == ()
    assert set(gate.EXPECTED_GREEN_EXPRESSION_FINGERPRINTS) == set(
        gate.COMPONENT_NAMES
    )

    _pins, v52, _v561 = gate._load_pinned_contracts()
    extra = dict(baseline)
    extra["EXTRA_COMPONENT"] = baseline["wall"]
    extra_result = gate._literal_green_ledger(v52, components=extra)
    assert extra_result["pass"] is False
    assert extra_result[
        "actual_component_keys_are_exactly_COMPONENT_NAMES"
    ] is False
    assert len(extra_result["actual_component_keys"]) == 21

    ghost = dict(baseline)
    ghost["EH_bulk_plus"] = gate._append_AST_ghost_to_first_pullback(
        ghost["EH_bulk_plus"]
    )
    ghost_result = gate._literal_green_ledger(v52, components=ghost)
    assert ghost_result["pass"] is False
    ghost_binding = next(
        binding
        for row in ghost_result["rows"]
        for binding in row["component_bindings"]
        if binding["component"] == "EH_bulk_plus"
    )
    assert ghost_binding["semantic_signature_exact"] is True
    assert ghost_binding["leaf_multiset_exact"] is True
    assert ghost_binding["full_AST_fingerprint_exact"] is False
    assert "AST_GHOST" in str(ghost_binding["full_AST_fingerprint_payload"])

    swapped = gate._literal_green_ledger(v52, mutation="shared_layout_swap")
    assert swapped["pass"] is False
    assert swapped["actual_component_keys_are_exactly_COMPONENT_NAMES"] is True
    assert swapped["observed_row_layout"] != swapped["expected_row_layout"]


def test_Green_kinetic_currents_are_derived_by_exact_product_rule_and_IBP(
    report: dict,
) -> None:
    ledger = report["literal_bulk_interface_Green_ledger"]
    assert ledger[
        "Omega_and_matter_momenta_derived_not_copied_from_Green_string"
    ] is True
    assert ledger["derived_boundary_equals_independent_target"] is True
    assert ledger["derived_integrated_boundary_terms"] == ledger[
        "independent_expected_integrated_boundary_terms"
    ]
    for side in gate.SIDES:
        normalized = ledger["kinetic_product_rule_IBP_normalizer"][side]
        assert normalized["pass"] is True
        assert normalized["quadratic_first_variation_multiplicity"] == 2
        assert normalized["source_action_weights"]["Omega_kinetic"] == {
            "numerator": -1,
            "denominator": 2,
            "powers": [["G", 1]],
            "numerator_parameters": ["G"],
            "denominator_parameters": [],
            "uses_floating_point": False,
        }
        assert normalized["source_action_weights"]["P_kinetic"] == {
            "numerator": -1,
            "denominator": 2,
            "powers": [["Z", 1]],
            "numerator_parameters": ["Z"],
            "denominator_parameters": [],
            "uses_floating_point": False,
        }
        assert normalized["raw_Omega_gradient_coefficient"]["numerator"] == -1
        assert normalized["raw_Omega_gradient_coefficient"]["powers"] == [["G", 1]]
        assert normalized["raw_P_pairing_coefficient"]["numerator"] == -1
        assert normalized["raw_P_pairing_coefficient"]["powers"] == [["Z", 1]]
        assert normalized["conformal_product_coefficient"] == {
            "numerator": 3,
            "denominator": 2,
            "powers": [["Omega_Sigma", -1]],
            "numerator_parameters": [],
            "denominator_parameters": ["Omega_Sigma"],
            "uses_floating_point": False,
        }
        assert normalized["derived_integrated_boundary_terms"] == normalized[
            "independent_expected_boundary_terms"
        ]
        assert normalized["Pi_Omega_formula"] == (
            f"G*n_{side}.nabla_Omega_{side}+3*Z*<phi_{side},n_{side}.P_{side}>/"
            "(2*Omega_Sigma)"
        )
        assert normalized["Pi_phi_formula"] == f"Z*j_{side}(n_{side}.P_{side})"
        assert normalized["Delta_P_program_matches_independent_target"] is True
        assert normalized["Delta_P_all_five_terms_consumed_once"] is True
        assert len(normalized["Delta_P_product_rule"]) == 5
        assert normalized["Delta_P_consumed_term_ids"] == [
            "covariant_Delta_phi",
            "conformal_Delta_phi_dOmega",
            "conformal_phi_dDeltaOmega",
            "conformal_log_variation",
            "connection_representation",
        ]
        assert {
            term["term_id"] for term in normalized["Delta_P_product_rule"]
        } == set(normalized["Delta_P_consumed_term_ids"])
        assert normalized["observed_Delta_P_term_signatures"] == normalized[
            "independent_expected_Delta_P_term_signatures"
        ]


def test_Delta_P_algebraic_terms_are_consumed_even_when_the_current_is_unchanged() -> None:
    for mutation in (
        "DeltaP_omit_Delta_phi_dOmega",
        "DeltaP_corrupt_Delta_phi_dOmega",
        "DeltaP_omit_Omega_minus2",
        "DeltaP_corrupt_Omega_minus2",
        "DeltaP_omit_representation_DeltaA_phi",
        "DeltaP_corrupt_representation_DeltaA_phi",
    ):
        normalized = gate._kinetic_boundary_current_normalizer("plus", mutation)
        assert normalized["pass"] is False
        assert normalized["Delta_P_program_matches_independent_target"] is False
        assert (
            normalized["Delta_P_all_five_terms_consumed_once"] is False
            or normalized["observed_Delta_P_term_signatures"]
            != normalized["independent_expected_Delta_P_term_signatures"]
        )
    for mutation in (
        "DeltaP_corrupt_Delta_phi_dOmega",
        "DeltaP_corrupt_Omega_minus2",
        "DeltaP_corrupt_representation_DeltaA_phi",
    ):
        normalized = gate._kinetic_boundary_current_normalizer("plus", mutation)
        assert normalized["derived_integrated_boundary_terms"] == normalized[
            "independent_expected_boundary_terms"
        ]


def test_Green_potentials_have_no_current_and_intrinsic_deltas_stay_unexpanded(
    report: dict,
) -> None:
    ledger = report["literal_bulk_interface_Green_ledger"]
    assert ledger["potential_and_full_V4_have_no_boundary_current"] is True
    assert ledger["six_intrinsic_variations_exact_and_unexpanded"] is True
    assert ledger["local_d4_intrinsic_expansion_performed"] is False
    assert ledger["intrinsic_trace_leaf_map"] == {
        "g_plus": "gamma",
        "Omega_plus": "Omega_Sigma",
        "varphi_H_soldered_leaf": "varphi_H",
        "T_on_abstract_Sigma": "T_Sigma",
    }
    intrinsic = {
        row["name"]: row for row in ledger["rows"] if row["name"] in gate.INTERFACE_SECTORS
    }
    assert tuple(intrinsic) == gate.INTERFACE_SECTORS
    assert all(
        row["derivation_kind"] == "exact_unexpanded_intrinsic_delta_axiom"
        and row["integrated_boundary_terms"] == []
        and row["intrinsic_delta"].startswith("delta(S_")
        for row in intrinsic.values()
    )
    r_squared = intrinsic["R_squared"]["component_bindings"][0]["observed_weight"]
    assert r_squared["numerator"] == -1
    assert r_squared["denominator"] == 32
    assert r_squared["powers"] == [
        ["B4_bar", 1],
        ["Mb", 2],
        ["k_infinity", -2],
    ]

    _pins, v52, _v561 = gate._load_pinned_contracts()
    corrupted = gate._literal_green_ledger(
        v52, mutation="intrinsic_producer_corruption"
    )
    assert corrupted["pass"] is False
    corrupted_r = next(row for row in corrupted["rows"] if row["name"] == "R")
    assert corrupted_r["intrinsic_delta"] == "delta(S_WRONG_R)"
    assert corrupted_r["intrinsic_delta_exact_and_unexpanded"] is False
    assert gate.EXPECTED_INTRINSIC_DELTAS["R"] == "delta(S_R)"


def test_Green_BF_row_reuses_offshell_incidence_without_cancelling_it(
    report: dict,
) -> None:
    ledger = report["literal_bulk_interface_Green_ledger"]
    assert ledger["BF_prerequisite_reused_exactly"] is True
    assert ledger["BF_off_shell_oriented_flux_nonzero"] is True
    assert ledger["BF_off_shell_cancellation_claimed"] is False
    assert report["oriented_BF_incidence_aggregation"]["pass"] is True
    assert report["oriented_BF_incidence_aggregation"][
        "off_shell_cancellation_claimed"
    ] is False
    bf_rows = [row for row in ledger["rows"] if row["name"].startswith("BF_")]
    assert len(bf_rows) == 2
    assert {row["derivation_kind"] for row in bf_rows} == {
        "reused_oriented_BF_incidence_prerequisite"
    }
    contract = ledger["literal_and_geometric_axiom_contract"]
    assert contract["observed"]["BF_bulk_equation_A"] == (
        gate.EXPECTED_BF_BULK_EQUATION_A
    )
    for side in gate.SIDES:
        normalized = ledger["BF_graded_bulk_variation_normalizer"][side]
        assert normalized["pass"] is True
        assert normalized["B_form_degree"] == 3
        assert "+<D_A B wedge Delta_A>-d<B wedge Delta_A>" in normalized[
            "graded_product_rule"
        ]
        assert normalized["derived_bulk_euler_terms"] == normalized[
            "independent_expected_bulk_euler_terms"
        ]
        d_ab = next(
            term
            for term in normalized["derived_bulk_euler_terms"]
            if term["factor"] == f"D_A_{side} B_{side}"
        )
        assert d_ab["coefficient"]["numerator"] == 1
        assert normalized["derived_local_boundary_divergence_term"] == normalized[
            "independent_expected_local_boundary_divergence_term"
        ]
        assert normalized["derived_local_boundary_divergence_term"][0][
            "coefficient"
        ]["numerator"] == -1
    _pins, v52, _v561 = gate._load_pinned_contracts()
    for mutation in (
        "BF_wrong_bulk_DAB_sign",
        "BF_omit_DAB",
        "BF_internal_boundary_minus_to_plus",
    ):
        mutated = gate._literal_green_ledger(v52, mutation=mutation)
        assert mutated["pass"] is False
        assert any(
            not row["bulk_euler_terms_exact"]
            or not row["local_d5_divergence_recorded_exactly_for_bulk_row"]
            for row in mutated["rows"]
            if row["name"].startswith("BF_")
        )


def test_Green_mutants_cover_structure_signs_currents_intrinsics_and_drift(
    report: dict,
) -> None:
    mutants = report["literal_bulk_interface_Green_effective_mutants"]
    expected = set(gate.GREEN_LEDGER_MUTATIONS) | {
        "drift_bulk_action_literal",
        "drift_EH_GHY_axiom_literal",
        "drift_momentum_literal",
        "drift_common_variation_literal",
        "drift_BF_bulk_equation_A_literal",
    }
    assert mutants["pass"] is True
    assert mutants["mutant_count"] == len(expected) == 50
    assert set(mutants["rows"]) == expected
    assert all(row["killed"] for row in mutants["rows"].values())
    for required in (
        "component_omitted",
        "component_duplicated",
        "component_swapped",
        "component_detached",
        "shared_layout_swap",
        "extra_component",
        "AST_GHOST_pullback",
        "GHY_omitted",
        "GHY_wrong_sign",
        "GHY_inward_normal",
        "Pi_Omega_kinetic_wrong_sign",
        "Pi_Omega_P_wrong_sign",
        "Pi_phi_wrong_sign",
        "P_three_halves_omitted",
        "P_three_halves_wrong",
        "DeltaP_omit_Delta_phi_dOmega",
        "DeltaP_corrupt_Delta_phi_dOmega",
        "DeltaP_omit_Omega_minus2",
        "DeltaP_corrupt_Omega_minus2",
        "DeltaP_omit_representation_DeltaA_phi",
        "DeltaP_corrupt_representation_DeltaA_phi",
        "split_common_variations",
        "Pi_phi_detached",
        "Pi_phi_unsoldered",
        "spurious_Omega_potential_current",
        "spurious_V4_current",
        "R_squared_denominator_16",
        "local_divergence_omitted",
        "BF_offshell_cancelled",
        "BF_wrong_bulk_DAB_sign",
        "BF_omit_DAB",
        "BF_internal_boundary_minus_to_plus",
        "intrinsic_producer_corruption",
    ):
        assert mutants["rows"][required]["killed"] is True
    for intrinsic in gate.INTERFACE_SECTORS:
        assert mutants["rows"][f"intrinsic_wrong_sign_{intrinsic}"]["killed"] is True
        assert mutants["rows"][f"intrinsic_omitted_{intrinsic}"]["killed"] is True


def test_Green_normalizer_and_mutation_API_are_fail_closed() -> None:
    with pytest.raises(gate.NaturalityCertificateError):
        gate.ExactCoefficient(1.0, 1, ())
    with pytest.raises(gate.NaturalityCertificateError):
        gate.ExactCoefficient(2, 4, ())
    with pytest.raises(gate.NaturalityCertificateError):
        gate.ExactCoefficient.from_parts(True)
    with pytest.raises(gate.NaturalityCertificateError):
        gate.ExactCoefficient.from_parts(1, 0)
    with pytest.raises(gate.NaturalityCertificateError):
        gate.ExactCoefficient.from_parts(1, 1, (("G", False),))
    with pytest.raises(gate.NaturalityCertificateError):
        gate._kinetic_boundary_current_normalizer("detached")
    _pins, v52, _v561 = gate._load_pinned_contracts()
    with pytest.raises(gate.NaturalityCertificateError):
        gate._literal_green_ledger(v52, mutation="unknown")
    for mutation in gate.GREEN_LEDGER_MUTATIONS:
        assert gate._literal_green_ledger(v52, mutation=mutation)["pass"] is False


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


def test_scoped_Green_ledger_is_promoted_but_every_wider_Ward_key_stays_false(
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
    assert decision["oriented_BF_incidence_aggregation_exact_pass"] is True
    assert decision["literal_bulk_interface_Green_ledger_pass"] is True
    assert report["theorem_domain"][
        "full_affine_connection_trace_transport_in_this_certificate"
    ] is True
    for key in (
        "fixed_reference_S_rel_diffeomorphism_Ward_pass",
        "oriented_BF_incidence_cancellation_exact_pass",
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
        "differentiated_local_Ward_identity",
        "Noether_current_definition",
        "moving_embedding_and_intrinsic_d4_expansion",
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
