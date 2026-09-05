#!/usr/bin/env python3
"""Independent tests for the narrow v5.6.7.11 EH/GHY formal AST gate."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import copy
import hashlib
import json

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_eh_ghy_semantic_frechet_v5_6_7_11_gate
    as gate,
)


SEMANTIC_HASH = "d933f3bd85d3495271877491016b50e739958ce73d2daf8083b42897a1dc84dc"
PROGRAM_HASH = "c1dcf794b0e18c0326791980ba7cbd65d413f0311bc311347d594bcee8881b75"
DERIVATIVE_HASH = "991e3a3d4fef746c10f17b39c8634d6bc10a820029d35a72b704fa3ef256fa07"
ROWS_HASH = "02db8501f63ef50451c094bdb1b3984e31f0b405fbe9dae637f0348d22742059"
V52_HASH = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BROWN_TARGET_HASH = "6ae45e806c9bb02e49d1f1d86b3044da81d7ed27caf0574c82fad8e4cc24093a"


@pytest.fixture(scope="session")
def report() -> dict:
    return gate.build_report()


def _ops(value: object):
    if isinstance(value, dict):
        if "op" in value:
            yield value["op"]
        for child in value.values():
            yield from _ops(child)


def _nodes(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _ops(child)


def test_ready_byte_pins_and_literal_four_component_scope(report: dict) -> None:
    assert report["status"] == "READY"
    assert report["checks"]["all"] is True
    dependency = report["dependency_certificate"]
    assert dependency["pass"] is True
    assert dependency["exact_action_sha256"] == V52_HASH
    assert {
        name: row["sha256"] for name, row in dependency["files"].items()
    } == gate.PINNED_INPUTS
    literal = report["literal_component_certificate"]
    assert literal["pass"] is True
    assert tuple(literal["components"]) == gate.COMPONENTS
    assert literal["EH_capture"] == {"M5_power": 3, "denominator": 2}
    assert literal["GHY_capture"] == {"M5_power": 3, "denominator": 1}


def test_semantic_completion_is_exactly_pinned_and_not_a_hidden_claim(report: dict) -> None:
    completion = report["semantic_completion"]
    assert report["semantic_completion_sha256"] == SEMANTIC_HASH
    assert report["expected_semantic_completion_sha256"] == SEMANTIC_HASH
    assert gate._canonical_sha256(completion) == SEMANTIC_HASH
    assert completion["coordinate_gravity"]["Riemann"].startswith(
        "R^R_SMN=partial_M Gamma^R_NS-partial_N Gamma^R_MS"
    )
    embedding = completion["embedding_and_normal"]
    assert embedding["cofactor"].startswith("nu_A=(1/4!)")
    assert embedding["unit_normal"] == "n_A=s_out*nu_A/sqrt(g^{BC}nu_B nu_C)"
    assert "n^A partial_A r_eps<0" in embedding["outward_selector"]
    assert "OUTWARD_SIGN" in embedding["outward_selector_type"]
    assert embedding["extrinsic_trace"] == "Theta=-gamma^{mn} n_R Q_mn^R"
    assert "finite" in completion["differentiation"][
        "finite_local_denotation_bridge"
    ]
    assert "do not establish a universal" in completion["differentiation"][
        "finite_local_denotation_bridge"
    ]
    symbolic = completion["differentiation"]["symbolic_whole_summand_replay"]
    assert "indeterminates" in symbolic
    assert "every outer factor" in symbolic
    assert all(value is False for value in completion["scope_limits"].values())


def test_semantic_completion_hash_is_recomputed_after_runtime_tamper() -> None:
    original = gate.SEMANTIC_COMPLETION["embedding_and_normal"]["extrinsic_trace"]
    try:
        gate.SEMANTIC_COMPLETION["embedding_and_normal"]["extrinsic_trace"] = (
            "Theta=+gamma^{mn} n_R Q_mn^R"
        )
        _, action, green = gate.certify_v52_dependency()
        core = gate._build_core(gate.parse_charter(action), green, None)
        assert core["required_checks"]["semantic_completion_pin"] is False
        assert core["normal_theta"]["pass"] is False
        assert core["semantic_completion_sha256"] == gate._canonical_sha256(
            core["semantic_completion"]
        )
        assert core["semantic_completion_sha256"] != SEMANTIC_HASH
    finally:
        gate.SEMANTIC_COMPLETION["embedding_and_normal"]["extrinsic_trace"] = original


def test_typed_gravity_AST_has_declared_primitives_and_is_pinned(report: dict) -> None:
    assert report["gravity_action_AST_sha256"] == PROGRAM_HASH
    assert report["expected_gravity_action_AST_sha256"] == PROGRAM_HASH
    manifest = report["gravity_action_AST"]
    assert tuple(manifest["components"]) == gate.COMPONENTS
    assert gate._canonical_sha256(manifest) == PROGRAM_HASH
    transparent = report["transparent_AST_certificate"]
    assert transparent["pass"] is True
    assert transparent["unknown_operators"] == []
    assert transparent["unexpected_primitive_fields"] == []
    assert transparent["forbidden_tokens"] == []
    assert transparent["coefficient_projection_atoms"]
    assert transparent["projection_free_claim"] is False
    assert transparent["every_primitive_has_independent_executable_coordinate_denotation"] is False
    serialized = json.dumps(manifest, sort_keys=True)
    assert "Brown_York" not in serialized
    assert "opaque" not in serialized and "placeholder" not in serialized
    assert "metric_jet_0_at_moving_Y" in serialized
    assert "metric_jet_1_at_moving_Y" in serialized


def test_literal_exterior_M5_polynomial_is_exact_and_independent(report: dict) -> None:
    oracle = report["exact_small_oracles"]["literal_exterior_M5_polynomial"]
    assert oracle["pass"] is True
    assert oracle["comparison_ring"] == "Q[M5] with M5 an indeterminate"
    assert oracle["separation"] == (
        "does not call Program builder, AD, row exporter, or symbolic replay"
    )
    expected = {
        "EH_bulk_plus": ((3, (1, 2)),),
        "GHY_plus": ((3, (1, 1)),),
        "EH_bulk_minus": ((3, (1, 2)),),
        "GHY_minus": ((3, (1, 1)),),
    }
    assert oracle["expected_by_component"] == expected
    for component, surface in oracle["components"].items():
        assert surface["pass"] is True
        assert surface["records"]
        assert all(row["observed_Q_M5"] == expected[component] for row in surface["records"])
        assert all(row["expected_Q_M5"] == expected[component] for row in surface["records"])
        assert all(row["scale_depth"] == 1 for row in surface["records"])


def test_cofactor_normal_and_theta_sign_are_structural_not_side_aliases(report: dict) -> None:
    certificate = report["cofactor_outward_normal_Theta_certificate"]
    assert certificate["pass"] is True
    assert certificate["Theta_formula"] == "Theta=-gamma^{mn} n_R Q_mn^R"
    for side in ("plus", "minus"):
        row = certificate["sides"][side]
        assert row["pass"] is True
        assert row["cofactor_present"] is True
        assert row["unit_normal_denominator_present"] is True
        assert row["outward_selector_slot"] == f"s_out_{side}"
        assert row["orientation_slot_not_negated_by_side_name"] is True
        assert row["Theta_is_minus_n_dot_Q"] is True
        assert f"M_{side}={{r_{side}>=0}}" in row["outward_constraint"]


def test_two_traversal_formal_Frechet_consistency_and_row_hashes(report: dict) -> None:
    derivative = report["exact_raw_Frechet_certificate"]
    assert derivative["pass"] is True
    assert derivative["traversal_and_row_consistency_pass"] is True
    assert derivative["inverse_volume_local_denotation_bridge_pass"] is True
    assert derivative["symbolic_whole_summand_replay_pass"] is True
    assert derivative["comparison_mode"] == (
        "exact canonical AST equality of two traversals over one primitive registry"
    )
    assert derivative["independent_coordinate_denotation_proved"] is False
    assert derivative["forward_equals_reverse_by_component"] == {
        name: True for name in gate.COMPONENTS
    }
    assert all(derivative["every_summand_linear_in_one_tangent_jet"].values())
    assert derivative["derivatives_sha256"] == DERIVATIVE_HASH
    assert derivative["FrechetRowV1_rows_sha256"] == ROWS_HASH
    assert derivative["row_count"] == 90
    assert derivative["role_inventory"] == ["bulk_metric", "embedding_map"]
    assert derivative["ordered_derivative_word_inventory"] == [
        [], [0], [0, 1]
    ]


def test_FrechetRowV1_component_roles_words_and_source_spans(report: dict) -> None:
    rows = report["exact_raw_Frechet_certificate"]["FrechetRowV1_rows"]
    assert Counter(row["component"] for row in rows) == {
        "EH_bulk_plus": 16,
        "GHY_plus": 29,
        "EH_bulk_minus": 16,
        "GHY_minus": 29,
    }
    _, action, _ = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    collection = report["exact_raw_Frechet_certificate"][
        "FrechetRowV1_collection_certificate"
    ]
    assert collection == {
        "pass": True,
        "expected_component_counts": gate.EXPECTED_COMPONENT_ROW_COUNTS,
        "observed_component_counts": gate.EXPECTED_COMPONENT_ROW_COUNTS,
        "canonical_component_order": list(gate.COMPONENTS),
        "ordinals_contiguous_and_unique": True,
        "parsed_action_sha256": V52_HASH,
        "side_consistency_checked": True,
        "source_spans_bound_to_parsed_action": True,
    }
    for row in rows:
        assert row["schema"] == "FrechetRowV1"
        assert row["derivative"]["kind"] == "partial"
        assert row["coefficient_ast_sha256"] == gate._canonical_sha256(
            row["coefficient_ast"]
        )
        assert "variation" not in set(_ops(row["coefficient_ast"]))
        assert set(row["coefficient_ast"]["type"]) == {
            "name", "dimension", "form_degree", "bundle", "variance",
            "density_weight", "symmetry", "fiber_dimension",
        }
        assert row["coefficient_ast"]["type"]["fiber_dimension"] == 1
        word = row["derivative"]["word"]
        assert word == list(range(len(word)))
        binders = row["derivative"].get("binders", [])
        assert len(binders) == len(word)
        assert [binder["id"] for binder in binders] == word
        assert all(binder["scope"] == "row" for binder in binders)
        slots = [
            node for node in _nodes(row["coefficient_ast"])
            if node.get("op") == "linear_slot"
        ]
        assert len(slots) == 1
        assert slots[0]["external_derivative_word"] == word
        assert slots[0]["type"]["fiber_dimension"] == 1
        for node in _nodes(row["coefficient_ast"]):
            if node.get("op") != "jet":
                continue
            node_word = node["derivative"]["word"]
            assert node_word == list(range(len(node_word)))
            assert all(
                binder["scope"] == "node"
                for binder in node["derivative"].get("binders", [])
            )
        assert row["source_spans"]
        assert row["source_spans"] == gate._source_spans(row["component"], parsed)
        assert gate.validate_frechet_row(row, parsed) is True
        for span in row["source_spans"]:
            source = gate.parse_charter(
                gate.certify_v52_dependency()[1]
            ).action[span["action_key"]]
            assert span["start"] == 0 and span["end"] == len(source)
            assert span["sha256"] == hashlib.sha256(source.encode()).hexdigest()
        if row["component"].startswith("EH_"):
            assert row["role"] == "bulk_metric"
            assert row["domain"] in {"M_plus", "M_minus"}
        else:
            assert row["domain"] == "Sigma"

    serialized_coefficients = json.dumps(
        [row["coefficient_ast"] for row in rows], sort_keys=True
    )
    assert '"symbol": "g_plus"' in serialized_coefficients
    assert '"word": [0, 1]' in serialized_coefficients
    assert '"symbol": "Y_minus"' in serialized_coefficients

    for side in ("plus", "minus"):
        eh = [row for row in rows if row["component"] == f"EH_bulk_{side}"]
        ghy = [row for row in rows if row["component"] == f"GHY_{side}"]
        assert {tuple(row["derivative"]["word"]) for row in eh} == {
            (), (0,), (0, 1)
        }
        assert Counter(row["role"] for row in ghy) == {
            "bulk_metric": 5,
            "embedding_map": 24,
        }
        assert (0, 1) in {
            tuple(row["derivative"]["word"]) for row in ghy
        }


def test_neutral_row_registry_binds_variation_bundle_not_integration_domain(
    report: dict,
) -> None:
    derivative = report["exact_raw_Frechet_certificate"]
    neutral = derivative["neutral_FrechetRowV1_validation"]
    assert neutral["pass"] is True
    assert neutral["validated_row_count"] == 90
    assert neutral["component_whitelist_used"] is False
    assert neutral["binder_source"] == "variation_bundle_plus_ordered_word"
    assert neutral["S10_validator_used"] is False
    assert neutral["S10_validator_interoperability_proved"] is False
    assert neutral["shared_density_metadata"] == {
        "bulk_coordinate_density": {
            "name": "bulk_coordinate_density", "dimension": 5,
            "form_degree": 5, "bundle": "trivial", "variance": [],
            "density_weight": 1, "symmetry": "alternating",
            "fiber_dimension": 1,
        },
        "interface_coordinate_density": {
            "name": "interface_coordinate_density", "dimension": 4,
            "form_degree": 4, "bundle": "trivial", "variance": [],
            "density_weight": 1, "symmetry": "alternating",
            "fiber_dimension": 1,
        },
    }

    rows = derivative["FrechetRowV1_rows"]
    expected_slot_names = {
        "H": ("bulk_metric", "bulk_metric_first_jet", "bulk_metric_second_jet"),
        "xi": ("embedding_map", "embedding_first_jet", "embedding_second_jet"),
    }
    for row in rows:
        variation = row["variation_component"]
        stem, side = variation.rsplit("_", 1)
        word = row["derivative"]["word"]
        slot = next(
            node for node in _nodes(row["coefficient_ast"])
            if node.get("op") == "linear_slot"
        )
        assert slot["type"]["name"] == expected_slot_names[stem][len(word)]
        expected_namespace = (
            f"M_{side}.coordinate" if stem == "H" else "Sigma.coordinate"
        )
        expected_dimension = 5 if stem == "H" else 4
        assert all(
            (binder["namespace"], binder["dimension"])
            == (expected_namespace, expected_dimension)
            for binder in row["derivative"].get("binders", [])
        )
        assert gate.validate_neutral_frechet_row(row) is True

    ghy_h1 = next(
        row for row in rows
        if row["component"] == "GHY_plus"
        and row["variation_component"] == "H_plus"
        and row["derivative"]["word"] == [0]
    )
    assert ghy_h1["domain"] == "Sigma"
    assert ghy_h1["derivative"]["binders"] == [{
        "id": 0, "namespace": "M_plus.coordinate", "dimension": 5,
        "variance": "down", "scope": "row", "alpha_normalized": True,
    }]
    renamed_ghy_h1 = copy.deepcopy(ghy_h1)
    renamed_ghy_h1["derivative"]["word"] = [7]
    renamed_ghy_h1["derivative"]["binders"][0].update(
        {"id": 7, "alpha_normalized": False}
    )
    renamed_slot = next(
        node for node in _nodes(renamed_ghy_h1["coefficient_ast"])
        if node.get("op") == "linear_slot"
    )
    renamed_slot["external_derivative_word"] = [7]
    renamed_ghy_h1["coefficient_ast_sha256"] = gate._canonical_sha256(
        renamed_ghy_h1["coefficient_ast"]
    )
    assert gate.canonicalize_frechet_row_binders(renamed_ghy_h1) == ghy_h1
    corrupt = copy.deepcopy(ghy_h1)
    corrupt["derivative"]["binders"][0].update(
        {"namespace": "Sigma.coordinate", "dimension": 4}
    )
    with pytest.raises(gate.GravityFrechetError, match="binder"):
        gate.validate_neutral_frechet_row(corrupt)

    xi2 = next(
        row for row in rows
        if row["variation_component"] == "xi_plus"
        and row["derivative"]["word"] == [0, 1]
    )
    mistyped_xi2 = copy.deepcopy(xi2)
    xi2_slot = next(
        node for node in _nodes(mistyped_xi2["coefficient_ast"])
        if node.get("op") == "linear_slot"
    )
    xi2_slot["type"] = gate._compat_type(gate.ACCELERATION5)
    mistyped_xi2["coefficient_ast_sha256"] = gate._canonical_sha256(
        mistyped_xi2["coefficient_ast"]
    )
    with pytest.raises(gate.GravityFrechetError, match="linear slot type"):
        gate.validate_neutral_frechet_row(mistyped_xi2)

    foreign_component = copy.deepcopy(ghy_h1)
    foreign_component["component"] = "neutral_consumer_component"
    assert gate.validate_neutral_frechet_row(foreign_component) is True
    with pytest.raises(gate.GravityFrechetError, match="component drift"):
        gate.validate_frechet_row(foreign_component)


def test_exact_inverse_connection_moving_cofactor_and_theta_oracles(report: dict) -> None:
    oracles = report["exact_small_oracles"]
    assert oracles["consumed_AST"] == {
        "program_sha256": report["gravity_action_AST_sha256"],
        "derivatives_sha256": report["exact_raw_Frechet_certificate"][
            "derivatives_sha256"
        ],
    }
    factors = oracles["literal_action_prefactors"]
    assert factors["pass"] is True
    assert factors["observed"] == {
        "EH_bulk_plus": Fraction(1, 2), "GHY_plus": Fraction(1),
        "EH_bulk_minus": Fraction(1, 2), "GHY_minus": Fraction(1),
    }
    q = oracles["covariant_acceleration_composition"]
    assert q["pass"] is True
    assert all(row["root_operation"] == "covariant_acceleration" for row in q["sides"].values())
    assert all(row["second_jet_type"] == "embedding_second_jet" for row in q["sides"].values())
    assert oracles["derivative_primitive_inventory"]["pass"] is True
    assert "covariant_acceleration" in oracles["derivative_primitive_inventory"]["observed"]
    inverse = oracles["inverse_and_volume"]
    assert inverse["delta_g_inverse"] == (
        (Fraction(-1), Fraction(2)),
        (Fraction(2), Fraction(-3)),
    )
    assert inverse["delta_sqrt_minus_det"] == 1
    bridge = oracles["derivative_AST_inverse_volume_bridge"]
    assert bridge["pass"] is True
    assert bridge["independent_expected"] == {
        "method": (
            "direct exact 5x5/4x4 Gauss-Jordan inverse, determinant, matrix "
            "multiplication, pullback, and first-jet contraction; no forward/reverse "
            "AD rule or attacked AST supplies expectations"
        ),
        "inverse_formula": "-base_inverse*tangent*base_inverse",
        "volume_formula": "sqrt(-det(base))*trace(base_inverse*tangent)/2",
        "GHY_ordinal_tangent_map": {
            "volume": {
                "0": "pullback(H,E,E)",
                "1": "pullback(partial_g.xi,E,E)",
                "2": "pullback(g(Y),Dxi,E)",
                "3": "pullback(g(Y),E,Dxi)",
            },
            "inverse": {
                "12,23": "H(Y)",
                "13,24": "partial_g.xi",
                "25": "pullback(H,E,E)",
                "26": "pullback(partial_g.xi,E,E)",
                "27": "pullback(g(Y),Dxi,E)",
                "28": "pullback(g(Y),E,Dxi)",
            },
        },
    }
    assert bridge["declared_dimensions"] == {"bulk": 5, "interface": 4}
    assert bridge["finite_witness_count"] == 2
    witnesses = bridge["finite_exact_rational_witnesses"]
    assert [row["bulk_dimension"] for row in witnesses] == [5, 5]
    assert [row["interface_dimension"] for row in witnesses] == [4, 4]
    assert [row["parameters"]["M5"] for row in witnesses] == [2, 3]
    assert [row["parameters"]["s_out_plus"] for row in witnesses] == [1, -1]
    assert [row["parameters"]["s_out_minus"] for row in witnesses] == [-1, 1]
    assert bridge["expected_local_primitive_counts"] == {
        "inverse": 32,
        "volume": 14,
        "by_component": {
            "EH_bulk_plus": {"inverse": 8, "volume": 3},
            "GHY_plus": {"inverse": 8, "volume": 4},
            "EH_bulk_minus": {"inverse": 8, "volume": 3},
            "GHY_minus": {"inverse": 8, "volume": 4},
        },
    }
    assert bridge["consumed_derivatives_sha256"] == DERIVATIVE_HASH
    assert bridge["consumed_FrechetRowV1_sha256"] == ROWS_HASH
    assert bridge["coverage_agrees_across_routes_and_rows"] is True
    assert bridge["denotational_values_agree_across_routes_and_rows"] is True
    parameter_surface = bridge["parameter_assignment_surface"]
    assert parameter_surface["pass"] is True
    assert parameter_surface["route_and_row_values_agree"] is True
    assert parameter_surface["expected_symbols_exact_per_component_and_ordinal"] is True
    assert parameter_surface[
        "every_assignment_covers_M5_and_both_outward_signs_nonzero"
    ] is True
    for route, surface in bridge["surfaces"].items():
        assert surface["pass"] is True
        assert surface["inverse_count"] == 32
        assert surface["volume_count"] == 14
        assert set(surface["components"]) == set(gate.COMPONENTS)
        for component, component_surface in surface["components"].items():
            expected = bridge["expected_local_primitive_counts"]["by_component"][component]
            assert component_surface["pass"] is True
            assert component_surface["coverage_exact"] is True
            assert component_surface["no_duplicate_ordinal_paths"] is True
            assert component_surface["values_exact"] is True
            assert component_surface["inverse_count"] == expected["inverse"]
            assert component_surface["volume_count"] == expected["volume"]
            assert component_surface["records"]
            assert all(record["route"] == route for record in component_surface["records"])
            assert all(record["component"] == component for record in component_surface["records"])
            assert all(record["values_exact"] for record in component_surface["records"])
            assert all(
                record["value_by_witness"] == record["expected_value_by_witness"]
                for record in component_surface["records"]
            )
            assert component_surface["observed_coverage"] == [
                {
                    "kind": record["kind"],
                    "summand_ordinal": record["summand_ordinal"],
                    "path": record["path"],
                }
                for record in component_surface["records"]
            ]
    symbolic = oracles["symbolic_whole_summand_replay"]
    assert symbolic["pass"] is True
    assert symbolic["whole_summand_count"] == 90
    assert symbolic["parameter_indeterminates"] == [
        "M5", "s_out_plus", "s_out_minus"
    ]
    assert symbolic["parameter_normal_form"].startswith("exact multivariate Q")
    assert "typed free symbols" in symbolic["tensor_primitive_semantics"]
    assert "does not call forward_nilpotent_dual" in symbolic["expected_route"]
    for component, component_surface in symbolic["components"].items():
        assert component in gate.COMPONENTS
        assert component_surface["pass"] is True
        assert component_surface["count_exact"] is True
        assert all(
            row["producer_reverse_row_denotational_equal"]
            and row["independent_replay_equal"]
            and row["error"] is None
            for row in component_surface["records"]
        )
    assert oracles["Christoffel_1d"]["value"] == Fraction(7, 8)
    cofactor = oracles["cofactor_outward"]
    assert cofactor["identity_embedding_cofactor"] == (0, 0, 0, 0, 1)
    assert cofactor["selected_normal"] == (0, 0, 0, 0, -1)
    assert cofactor["n_dot_dr"] == -1
    moving = oracles["moving_pulljet"]
    assert moving["delta_g_at_Y"] == 21
    assert moving["delta_g1_at_Y"] == 27
    assert oracles["flat_graph_Theta_sign"]["delta_Theta_for_s_out_plus_one"] == 2
    assert (
        oracles["warped_Brown_York_nonzero_diagnostic"]
        ["Brown_York_pi_coefficient_times_gamma_inverse"]
        == Fraction(-9, 2)
    )


def test_fixed_embedding_subcertificate_is_post_derivative_and_fail_closed(report: dict) -> None:
    brown = report["fixed_embedding_xi_zero_Brown_York_subcertificate"]
    derivative = report["exact_raw_Frechet_certificate"]
    assert brown["pass"] is False
    assert brown["constructed_after_both_raw_derivatives"] is True
    assert brown["input_derivatives_sha256"] == derivative["derivatives_sha256"]
    assert brown["input_FrechetRowV1_sha256"] == derivative["FrechetRowV1_rows_sha256"]
    assert brown["projection"].startswith("xi_plus=xi_minus=0")
    assert (brown["raw_row_count"], brown["discarded_xi_row_count"], brown["fixed_embedding_row_count"]) == (90, 48, 42)
    assert brown["constructor_contains_Brown_York_target"] is False
    assert brown["constructor_contains_v5_2_target_text"] is False
    assert brown["v5_2_target_diagnostic_sha256"] == BROWN_TARGET_HASH
    assert brown["Palatini_boundary_current_derived_from_EH_rows"] is False
    assert brown["oriented_Stokes_map_from_Meps_to_Sigma_implemented"] is False
    assert brown["normal_derivative_cancellation_exact"] is False
    assert brown["Brown_York_remainder_exact"] is False


def test_all_mandatory_mutants_are_rejected_on_real_failure_surfaces(report: dict) -> None:
    certificate = report["mandatory_mutant_certificate"]
    assert certificate["pass"] is True
    assert tuple(certificate["required_inventory"]) == gate.MANDATORY_MUTANTS
    assert set(certificate["rows"]) == set(gate.MANDATORY_MUTANTS)
    assert all(row["killed"] for row in certificate["rows"].values())
    assert all(row["failed_required_checks"] for row in certificate["rows"].values())
    assert all(
        row["required_semantic_failure_observed"]
        for row in certificate["rows"].values()
    )
    assert certificate["rows"]["semantic_completion_post_cache_tamper"][
        "required_semantic_failure_surface"
    ] == "semantic_completion_pin"
    m5_alias = certificate["rows"]["primal_read_once_M5_alias"]
    assert m5_alias["required_semantic_failure_surface"] == (
        "literal_exterior_M5_polynomial_exact"
    )
    assert "literal_exterior_M5_polynomial_exact" in m5_alias[
        "failed_required_checks"
    ]
    for name in ("wrong_EH_half", "wrong_GHY_half"):
        assert "AST_literal_EH_GHY_prefactors_exact" in certificate["rows"][name][
            "failed_required_checks"
        ]
    assert "AST_Q_is_D2Y_plus_GammaYY_exact" in certificate["rows"]["omit_Y2"][
        "failed_required_checks"
    ]
    assert certificate["rows"]["wrong_inverse_sign"]["dual_equals_reverse"] is False
    assert certificate["rows"]["wrong_volume_half"]["dual_equals_reverse"] is False
    for name in (
        "correlated_wrong_inverse_sign",
        "correlated_wrong_volume_half",
        "correlated_inverse_operand_doubled",
        "correlated_dimension_trace_identity_factor",
        "correlated_inverse_operand_scaled_by_M5",
        "correlated_evaluation_embedding_scaled_by_M5",
        "row_evaluation_embedding_scaled_by_M5",
    ):
        row = certificate["rows"][name]
        assert row["dual_equals_reverse"] is True
        assert row["required_semantic_failure_surface"] == "exact_small_oracles"
        assert "exact_small_oracles" in row["failed_required_checks"]
    for name in (
        "finite_alias_inverse_operand_lost_prefactor",
        "lost_inverse_summand_M5_cubed_prefactor",
    ):
        row = certificate["rows"][name]
        assert row["dual_equals_reverse"] is True
        assert row["FrechetRowV1_schema_and_binder_pass"] is True
        assert row["required_semantic_failure_surface"] == (
            "symbolic_whole_summand_replay_exact"
        )
        assert "symbolic_whole_summand_replay_exact" in row[
            "failed_required_checks"
        ]
    assert "cofactor_unit_outward_normal_and_Theta_minus_nQ" in certificate["rows"]["wrong_Theta_sign"]["failed_required_checks"]
    assert "declared_denotational_primitive_inventory" in certificate["rows"]["inject_Brown_York_target"]["failed_required_checks"]
    assert "ordered_holonomic_tangent_words" in certificate["rows"]["collapse_mixed"]["failed_required_checks"]
    for name in (
        "binder_wrong_dimension",
        "binder_wrong_namespace",
        "binder_GHY_H_uses_integration_domain",
        "xi_D2_slot_mistyped_as_acceleration",
        "binder_free_word",
        "binder_illegal_capture",
        "binder_not_alpha_normalized",
        "row_unknown_rehashed_opcode",
        "row_extra_rehashed_metadata",
        "row_GHY_outward_selector_to_M5",
    ):
        assert certificate["rows"][name]["dual_equals_reverse"] is True
        assert certificate["rows"][name]["FrechetRowV1_schema_and_binder_pass"] is False
        assert "FrechetRowV1_schema_scope_capture_validation" in certificate["rows"][name]["failed_required_checks"]
    for name in (
        "fake_source_span_rehashed",
        "row_ordinal_999",
        "row_duplicate_ordinal",
        "row_plus_variation_to_minus",
        "row_plus_jet_to_minus",
        "row_GHY_outward_selector_to_M5",
        "integral_duplicate_minus_into_plus",
    ):
        row = certificate["rows"][name]
        assert row["dual_equals_reverse"] is True
        assert row["FrechetRowV1_component_collection_pass"] is False
        assert row["required_semantic_failure_surface"] == (
            "FrechetRowV1_component_collection_exact"
        )
        assert "FrechetRowV1_component_collection_exact" in row[
            "failed_required_checks"
        ]


@pytest.mark.parametrize(
    "mutation",
    ("correlated_wrong_inverse_sign", "correlated_wrong_volume_half"),
)
def test_correlated_primitive_mutation_survives_route_equality_but_not_independent_bridge_after_repin(
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    _, action, green = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    mutated = gate._build_core(parsed, green, mutation)
    assert mutated["derivative"]["raw_dual_equals_reverse_pass"] is True
    assert mutated["oracles"]["derivative_AST_inverse_volume_bridge"]["pass"] is False
    monkeypatch.setattr(
        gate,
        "EXPECTED_DERIVATIVES_SHA256",
        mutated["derivative"]["derivatives_sha256"],
    )
    monkeypatch.setattr(
        gate,
        "EXPECTED_FRECHET_ROWS_SHA256",
        mutated["derivative"]["FrechetRowV1_rows_sha256"],
    )
    repinned = gate._build_core(parsed, green, mutation)
    assert repinned["required_checks"]["semantic_derivative_pin"] is True
    assert repinned["required_checks"]["FrechetRowV1_export_pin"] is True
    assert repinned["required_checks"]["nilpotent_dual_equals_reverse_Frechet_exact"] is True
    assert repinned["required_checks"]["exact_small_oracles"] is False
    assert repinned["ready"] is False
    public = gate.build_report(mutation)
    assert public["exact_raw_Frechet_certificate"][
        "traversal_and_row_consistency_pass"
    ] is True
    assert public["exact_raw_Frechet_certificate"][
        "inverse_volume_local_denotation_bridge_pass"
    ] is False
    assert public["exact_raw_Frechet_certificate"]["pass"] is False
    assert public["decision"][
        "EH_plus_minus_GHY_plus_minus_raw_formal_AST_Frechet_pass"
    ] is False


def test_recursive_inverse_bridge_consumes_the_actual_metric_operand() -> None:
    witness = gate._local_denotation_witnesses()[0]
    metric = gate.field("probe_g", gate.METRIC5)
    tangent = gate.variation("probe_H", gate.METRIC5)
    inverse = gate.inverse_metric(metric)
    correct = gate.negate(
        gate.multilinear("inverse_sandwich_5", inverse, tangent, inverse)
    )
    doubled_left = gate.negate(
        gate.multilinear(
            "inverse_sandwich_5",
            gate.inverse_metric(gate.add(metric, metric)),
            tangent,
            inverse,
        )
    )
    expected = gate._independent_local_expected_value(
        "EH_bulk_plus", "inverse", 5, witness
    )
    assert gate._expr_probe_inverse(correct, witness) == expected
    assert gate._expr_probe_inverse(doubled_left, witness) == gate._matrix_scale(
        Fraction(1, 2), expected
    )
    assert gate._expr_probe_inverse(doubled_left, witness) != expected


def test_declared_dimension_trace_distinguishes_bulk_five_from_induced_four() -> None:
    witness = gate._local_denotation_witnesses()[0]
    bulk_metric = gate.field("probe_g", gate.METRIC5)
    bulk_trace = gate.multilinear(
        "metric_trace_5", gate.inverse_metric(bulk_metric), bulk_metric
    )
    induced_metric = gate.multilinear(
        "pullback_metric",
        gate.evaluate_jet(
            bulk_metric,
            gate.field("probe_g1", gate.METRIC1JET5),
            gate.field("probe_Y", gate.MAP5),
            0,
        ),
        gate.field("probe_Y1", gate.MAP1),
        gate.field("probe_Y1", gate.MAP1),
    )
    induced_trace = gate.multilinear(
        "metric_trace_4", gate.inverse_metric(induced_metric), induced_metric
    )
    assert gate._expr_probe_scalar(bulk_trace, witness) == 5
    assert gate._expr_probe_scalar(induced_trace, witness) == 4


def test_correlated_inverse_operand_mutation_fails_bridge_after_full_repin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, action, green = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    mutation = "correlated_inverse_operand_doubled"
    mutated = gate._build_core(parsed, green, mutation)
    assert mutated["derivative"]["raw_dual_equals_reverse_pass"] is True
    bridge = mutated["oracles"]["derivative_AST_inverse_volume_bridge"]
    assert bridge["pass"] is False
    assert any(
        not component["values_exact"]
        for surface in bridge["surfaces"].values()
        for component in surface["components"].values()
    )
    monkeypatch.setattr(
        gate,
        "EXPECTED_DERIVATIVES_SHA256",
        mutated["derivative"]["derivatives_sha256"],
    )
    monkeypatch.setattr(
        gate,
        "EXPECTED_FRECHET_ROWS_SHA256",
        mutated["derivative"]["FrechetRowV1_rows_sha256"],
    )
    repinned = gate._build_core(parsed, green, mutation)
    assert repinned["required_checks"]["semantic_derivative_pin"] is True
    assert repinned["required_checks"]["FrechetRowV1_export_pin"] is True
    assert repinned["required_checks"][
        "nilpotent_dual_equals_reverse_Frechet_exact"
    ] is True
    assert repinned["required_checks"]["exact_small_oracles"] is False
    assert repinned["ready"] is False


@pytest.mark.parametrize(
    "mutation",
    (
        "correlated_dimension_trace_identity_factor",
        "correlated_inverse_operand_scaled_by_M5",
        "correlated_evaluation_embedding_scaled_by_M5",
    ),
)
def test_fifth_audit_correlated_attacks_fail_exact_5d_4d_bridge_after_repin(
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    _, action, green = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    mutated = gate._build_core(parsed, green, mutation)
    derivative = mutated["derivative"]
    bridge = mutated["oracles"]["derivative_AST_inverse_volume_bridge"]
    assert derivative["raw_dual_equals_reverse_pass"] is True
    assert derivative["FrechetRowV1_schema_and_binder_pass"] is True
    assert derivative["FrechetRowV1_component_collection_pass"] is True
    assert bridge["pass"] is False
    assert any(
        not component["values_exact"]
        for surface in bridge["surfaces"].values()
        for component in surface["components"].values()
    )
    monkeypatch.setattr(
        gate, "EXPECTED_DERIVATIVES_SHA256", derivative["derivatives_sha256"]
    )
    monkeypatch.setattr(
        gate, "EXPECTED_FRECHET_ROWS_SHA256", derivative["FrechetRowV1_rows_sha256"]
    )
    repinned = gate._build_core(parsed, green, mutation)
    assert repinned["required_checks"]["semantic_derivative_pin"] is True
    assert repinned["required_checks"]["FrechetRowV1_export_pin"] is True
    assert repinned["required_checks"][
        "nilpotent_dual_equals_reverse_Frechet_exact"
    ] is True
    assert repinned["required_checks"]["exact_small_oracles"] is False
    assert repinned["ready"] is False


def test_row_only_evaluation_point_attack_breaks_denotational_route_equality_after_repin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, action, green = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    mutation = "row_evaluation_embedding_scaled_by_M5"
    mutated = gate._build_core(parsed, green, mutation)
    derivative = mutated["derivative"]
    bridge = mutated["oracles"]["derivative_AST_inverse_volume_bridge"]
    assert derivative["raw_dual_equals_reverse_pass"] is True
    assert derivative["FrechetRowV1_schema_and_binder_pass"] is True
    assert derivative["FrechetRowV1_component_collection_pass"] is True
    assert bridge["pass"] is False
    assert bridge["denotational_values_agree_across_routes_and_rows"] is False
    assert bridge["parameter_assignment_surface"]["route_and_row_values_agree"] is False
    monkeypatch.setattr(
        gate, "EXPECTED_DERIVATIVES_SHA256", derivative["derivatives_sha256"]
    )
    monkeypatch.setattr(
        gate, "EXPECTED_FRECHET_ROWS_SHA256", derivative["FrechetRowV1_rows_sha256"]
    )
    repinned = gate._build_core(parsed, green, mutation)
    assert repinned["required_checks"]["semantic_derivative_pin"] is True
    assert repinned["required_checks"]["FrechetRowV1_export_pin"] is True
    assert repinned["required_checks"]["exact_small_oracles"] is False
    assert repinned["ready"] is False


def test_finite_alias_is_exactly_one_at_witnesses_but_nonconstant_symbolically() -> None:
    alias = gate._finite_alias_polynomial()
    polynomial = gate._expr_parameter_polynomial(alias)
    assert gate._polynomial_normal_form(polynomial) == (
        ((0, 0, 0), (7, 1)),
        ((1, 0, 0), (-5, 1)),
        ((2, 0, 0), (1, 1)),
    )
    assert [
        gate._expr_probe_scalar(alias, witness)
        for witness in gate._local_denotation_witnesses()
    ] == [1, 1]


def test_read_once_primal_M5_alias_fails_literal_polynomial_after_full_repin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, action, green = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    mutation = "primal_read_once_M5_alias"
    mutated = gate._build_core(parsed, green, mutation)
    derivative = mutated["derivative"]
    exact = mutated["oracles"]["literal_exterior_M5_polynomial"]

    alias = gate._read_once_M5_cubed_alias()
    assert [
        gate._expr_probe_scalar(alias, witness)
        for witness in gate._local_denotation_witnesses()
    ] == [8, 27]
    assert gate._strict_exterior_M5_polynomial(alias) != {3: Fraction(1)}
    assert mutated["program_sha256"] == (
        "60ac9dc363f65d26e136c1d31588438371f4b2cbd60003f8b94ee4f789488870"
    )
    assert derivative["derivatives_sha256"] == (
        "a7506d8ae0359b91910cbd486c3e5a277a5eaa1e677aca8fabd15a997d408708"
    )
    assert derivative["FrechetRowV1_rows_sha256"] == (
        "49db65aeaf90578c3b48511a22944a812f8c87b0c77e5a94f8d1abf76c73df0a"
    )
    assert mutated["oracles"]["literal_action_prefactors"]["pass"] is True
    assert mutated["oracles"]["derivative_AST_inverse_volume_bridge"][
        "parameter_assignment_surface"
    ]["pass"] is True
    assert mutated["oracles"]["symbolic_whole_summand_replay"]["pass"] is True
    assert derivative["row_count"] == 90
    assert exact["pass"] is False
    assert all(
        not row["pass"]
        for surface in exact["components"].values()
        for row in surface["records"]
    )

    monkeypatch.setattr(gate, "EXPECTED_PROGRAM_SHA256", mutated["program_sha256"])
    monkeypatch.setattr(
        gate, "EXPECTED_DERIVATIVES_SHA256", derivative["derivatives_sha256"]
    )
    monkeypatch.setattr(
        gate,
        "EXPECTED_FRECHET_ROWS_SHA256",
        derivative["FrechetRowV1_rows_sha256"],
    )
    repinned = gate._build_core(parsed, green, mutation)
    assert repinned["required_checks"]["typed_action_AST_pin"] is True
    assert repinned["required_checks"]["semantic_derivative_pin"] is True
    assert repinned["required_checks"]["FrechetRowV1_export_pin"] is True
    assert repinned["required_checks"][
        "nilpotent_dual_equals_reverse_Frechet_exact"
    ] is True
    assert repinned["required_checks"][
        "literal_exterior_M5_polynomial_exact"
    ] is False
    assert repinned["ready"] is False


@pytest.mark.parametrize(
    ("mutation", "finite_bridge_pass"),
    (
        ("finite_alias_inverse_operand_lost_prefactor", True),
        ("lost_inverse_summand_M5_cubed_prefactor", False),
    ),
)
def test_whole_summand_symbolic_replay_kills_lost_prefactor_after_full_repin(
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
    finite_bridge_pass: bool,
) -> None:
    _, action, green = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    mutated = gate._build_core(parsed, green, mutation)
    derivative = mutated["derivative"]
    finite_bridge = mutated["oracles"]["derivative_AST_inverse_volume_bridge"]
    symbolic = mutated["oracles"]["symbolic_whole_summand_replay"]
    assert derivative["raw_dual_equals_reverse_pass"] is True
    assert derivative["FrechetRowV1_schema_and_binder_pass"] is True
    assert derivative["FrechetRowV1_component_collection_pass"] is True
    assert finite_bridge["pass"] is finite_bridge_pass
    assert symbolic["pass"] is False
    assert symbolic["whole_summand_count"] == 90
    for component in gate.COMPONENTS:
        failed_ordinals = {
            row["summand_ordinal"]
            for row in symbolic["components"][component]["records"]
            if not row["independent_replay_equal"]
        }
        expected = {
            ordinal
            for kind, ordinal, _ in gate._expected_local_coverage(component)
            if kind == "inverse"
        }
        assert failed_ordinals == expected
    monkeypatch.setattr(
        gate, "EXPECTED_DERIVATIVES_SHA256", derivative["derivatives_sha256"]
    )
    monkeypatch.setattr(
        gate, "EXPECTED_FRECHET_ROWS_SHA256", derivative["FrechetRowV1_rows_sha256"]
    )
    repinned = gate._build_core(parsed, green, mutation)
    assert repinned["required_checks"]["semantic_derivative_pin"] is True
    assert repinned["required_checks"]["FrechetRowV1_export_pin"] is True
    assert repinned["required_checks"][
        "nilpotent_dual_equals_reverse_Frechet_exact"
    ] is True
    assert repinned["required_checks"][
        "symbolic_whole_summand_replay_exact"
    ] is False
    assert repinned["ready"] is False
    public = gate.build_report(mutation)
    assert public["status"] == "NOT_READY"
    assert public["exact_raw_Frechet_certificate"][
        "symbolic_whole_summand_replay_pass"
    ] is False
    assert public["exact_raw_Frechet_certificate"]["pass"] is False


def test_outward_selector_has_distinct_type_and_exact_row_inventory(
    report: dict,
) -> None:
    rows = report["exact_raw_Frechet_certificate"]["FrechetRowV1_rows"]
    for row in rows:
        side = row["component"].rsplit("_", 1)[1]
        selectors = [
            node
            for node in _nodes(row["coefficient_ast"])
            if node.get("op") == "param"
            and node.get("type") == gate._compat_type(gate.OUTWARD_SIGN)
        ]
        expected = [] if row["component"].startswith("EH_") else [f"s_out_{side}"]
        assert [node["symbol"] for node in selectors] == expected

    attacked = copy.deepcopy(next(row for row in rows if row["component"] == "GHY_plus"))
    selector = next(
        node
        for node in _nodes(attacked["coefficient_ast"])
        if node.get("op") == "param" and node.get("symbol") == "s_out_plus"
    )
    selector["symbol"] = "M5"
    attacked["coefficient_ast_sha256"] = gate._canonical_sha256(
        attacked["coefficient_ast"]
    )
    for validator in (gate.validate_neutral_frechet_row, gate.validate_frechet_row):
        with pytest.raises(gate.GravityFrechetError, match="parameter leaf signature"):
            validator(attacked)

    retagged = copy.deepcopy(attacked)
    retagged_selector = next(
        node
        for node in _nodes(retagged["coefficient_ast"])
        if node.get("op") == "param" and node.get("symbol") == "M5"
        and node.get("type") == gate._compat_type(gate.OUTWARD_SIGN)
    )
    retagged_selector["type"] = gate._compat_type(gate.SCALAR0)
    retagged["coefficient_ast_sha256"] = gate._canonical_sha256(
        retagged["coefficient_ast"]
    )
    assert gate.validate_neutral_frechet_row(retagged) is True
    with pytest.raises(gate.GravityFrechetError, match="outward selector inventory"):
        gate.validate_frechet_row(retagged)


def test_outward_selector_to_M5_integral_mutant_stays_false_after_row_repin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, action, green = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    mutation = "row_GHY_outward_selector_to_M5"
    mutated = gate._build_core(parsed, green, mutation)
    assert mutated["derivative"]["raw_dual_equals_reverse_pass"] is True
    assert mutated["derivative"]["FrechetRowV1_schema_and_binder_pass"] is False
    assert mutated["derivative"]["FrechetRowV1_component_collection_pass"] is False
    monkeypatch.setattr(
        gate,
        "EXPECTED_FRECHET_ROWS_SHA256",
        mutated["derivative"]["FrechetRowV1_rows_sha256"],
    )
    repinned = gate._build_core(parsed, green, mutation)
    assert repinned["required_checks"]["FrechetRowV1_export_pin"] is True
    assert repinned["required_checks"][
        "FrechetRowV1_schema_scope_capture_validation"
    ] is False
    assert repinned["required_checks"][
        "FrechetRowV1_component_collection_exact"
    ] is False
    assert repinned["ready"] is False


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ("unknown", "unknown coefficient AST opcode"),
        ("extra", "opcode field inventory drift"),
    ),
)
def test_rehashed_unknown_opcode_and_extra_metadata_fail_neutral_and_local_validation(
    report: dict,
    mutation: str,
    message: str,
) -> None:
    row = copy.deepcopy(report["exact_raw_Frechet_certificate"]["FrechetRowV1_rows"][0])
    if mutation == "unknown":
        row["coefficient_ast"]["op"] = "unknown_rehashed_opcode"
    else:
        row["coefficient_ast"]["forged_metadata"] = "ignored_by_permissive_validator"
    row["coefficient_ast_sha256"] = gate._canonical_sha256(row["coefficient_ast"])
    for validator in (gate.validate_neutral_frechet_row, gate.validate_frechet_row):
        with pytest.raises(gate.GravityFrechetError, match=message):
            validator(row)


def test_row_derivative_and_source_span_field_inventories_are_exhaustive(report: dict) -> None:
    baseline = report["exact_raw_Frechet_certificate"]["FrechetRowV1_rows"][0]

    extra_row = copy.deepcopy(baseline)
    extra_row["forged_metadata"] = True
    with pytest.raises(gate.GravityFrechetError, match="row field inventory"):
        gate.validate_neutral_frechet_row(extra_row)

    extra_derivative = copy.deepcopy(baseline)
    extra_derivative["derivative"]["forged_metadata"] = True
    with pytest.raises(gate.GravityFrechetError, match="derivative kind drift"):
        gate.validate_neutral_frechet_row(extra_derivative)

    extra_span = copy.deepcopy(baseline)
    extra_span["source_spans"][0]["forged_metadata"] = True
    with pytest.raises(gate.GravityFrechetError, match="source span field inventory"):
        gate.validate_neutral_frechet_row(extra_span)

    bad_component = copy.deepcopy(baseline)
    bad_component["component"] = ["EH_bulk_plus"]
    with pytest.raises(gate.GravityFrechetError, match="component is not a nonempty string"):
        gate.validate_neutral_frechet_row(bad_component)

    bad_ordinal = copy.deepcopy(baseline)
    bad_ordinal["summand_ordinal"] = True
    with pytest.raises(gate.GravityFrechetError, match="summand ordinal drift"):
        gate.validate_neutral_frechet_row(bad_ordinal)


def test_fake_rehashed_source_span_passes_shape_but_not_parsed_action_binding(
    report: dict,
) -> None:
    row = copy.deepcopy(report["exact_raw_Frechet_certificate"]["FrechetRowV1_rows"][0])
    _, action, _ = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    span = row["source_spans"][1]
    fake_text = parsed.action[span["action_key"]][:-1]
    span["end"] = len(fake_text)
    span["sha256"] = hashlib.sha256(fake_text.encode()).hexdigest()
    assert gate.validate_neutral_frechet_row(row) is True
    with pytest.raises(gate.GravityFrechetError, match="parsed action bytes"):
        gate.validate_frechet_row(row, parsed)


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ("row_ordinal_999", "canonical contiguous ordinals"),
        ("row_duplicate_ordinal", "ordinal duplicated"),
    ),
)
def test_complete_collection_rejects_noncanonical_or_duplicate_ordinals(
    report: dict,
    mutation: str,
    message: str,
) -> None:
    rows = copy.deepcopy(report["exact_raw_Frechet_certificate"]["FrechetRowV1_rows"])
    if mutation == "row_ordinal_999":
        rows[0]["summand_ordinal"] = 999
    else:
        rows[1]["summand_ordinal"] = rows[0]["summand_ordinal"]
    _, action, _ = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    assert all(gate.validate_frechet_row(row, parsed) for row in rows)
    with pytest.raises(gate.GravityFrechetError, match=message):
        gate.frechet_row_collection_certificate(rows, parsed)


def test_component_side_binds_variation_and_every_background_jet(report: dict) -> None:
    rows = report["exact_raw_Frechet_certificate"]["FrechetRowV1_rows"]
    _, action, _ = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    baseline = next(
        row
        for row in rows
        if row["component"] == "EH_bulk_plus"
        and row["variation_component"] == "H_plus"
        and row["derivative"]["word"] == []
    )

    wrong_variation = copy.deepcopy(baseline)
    wrong_variation["variation_component"] = "H_minus"
    assert gate.validate_neutral_frechet_row(wrong_variation) is True
    with pytest.raises(gate.GravityFrechetError, match="variation component side"):
        gate.validate_frechet_row(wrong_variation, parsed)

    wrong_jet = copy.deepcopy(baseline)
    jet = next(
        node
        for node in _nodes(wrong_jet["coefficient_ast"])
        if node.get("op") == "jet"
        and node.get("symbol") == "g_plus"
        and node.get("derivative", {}).get("word") == []
    )
    jet["symbol"] = "g_minus"
    wrong_jet["coefficient_ast_sha256"] = gate._canonical_sha256(
        wrong_jet["coefficient_ast"]
    )
    assert gate.validate_neutral_frechet_row(wrong_jet) is True
    with pytest.raises(gate.GravityFrechetError, match="jet symbol side"):
        gate.validate_frechet_row(wrong_jet, parsed)


def test_integral_minus_into_plus_duplication_stays_not_ready_after_repin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, action, green = gate.certify_v52_dependency()
    parsed = gate.parse_charter(action)
    mutation = "integral_duplicate_minus_into_plus"
    mutated = gate._build_core(parsed, green, mutation)
    assert mutated["derivative"]["derivatives_sha256"] == (
        "cf60f4936de2a04e90f3c71aab0583faaf56861c7b66f3dc4d96cdbe4c03a4e5"
    )
    assert mutated["derivative"]["FrechetRowV1_rows_sha256"] == (
        "2008e7ab20a0cebead5e3244388a187d64839ba51e51504d1f58b395bd09ca6e"
    )
    assert mutated["derivative"]["raw_dual_equals_reverse_pass"] is True
    bridge = mutated["oracles"]["derivative_AST_inverse_volume_bridge"]
    assert bridge["pass"] is False
    assert bridge["parameter_assignment_surface"][
        "expected_symbols_exact_per_component_and_ordinal"
    ] is False
    assert mutated["derivative"]["FrechetRowV1_component_collection_pass"] is False
    monkeypatch.setattr(
        gate,
        "EXPECTED_DERIVATIVES_SHA256",
        mutated["derivative"]["derivatives_sha256"],
    )
    monkeypatch.setattr(
        gate,
        "EXPECTED_FRECHET_ROWS_SHA256",
        mutated["derivative"]["FrechetRowV1_rows_sha256"],
    )
    repinned = gate._build_core(parsed, green, mutation)
    assert repinned["required_checks"]["semantic_derivative_pin"] is True
    assert repinned["required_checks"]["FrechetRowV1_export_pin"] is True
    assert repinned["required_checks"][
        "nilpotent_dual_equals_reverse_Frechet_exact"
    ] is True
    assert repinned["required_checks"][
        "FrechetRowV1_component_collection_exact"
    ] is False
    assert repinned["ready"] is False


def test_two_index_binder_alpha_renaming_is_invariant_and_capture_safe(report: dict) -> None:
    derivative = report["exact_raw_Frechet_certificate"]
    assert derivative["FrechetRowV1_validation"] == {
        "pass": True,
        "validated_row_count": 90,
        "errors": [],
    }
    assert derivative["binder_alpha_renaming_oracle"]["pass"] is True
    assert derivative["binder_alpha_renaming_oracle"]["renamed_ids"] == [7, 9]
    row = copy.deepcopy(
        next(
            item
            for item in derivative["FrechetRowV1_rows"]
            if item["derivative"]["word"] == [0, 1]
        )
    )
    renamed = copy.deepcopy(row)
    renamed["derivative"]["word"] = [7, 9]
    for identifier, binder in zip((7, 9), renamed["derivative"]["binders"], strict=True):
        binder["id"] = identifier
        binder["alpha_normalized"] = False
    slot = next(
        node
        for node in _nodes(renamed["coefficient_ast"])
        if node.get("op") == "linear_slot"
    )
    slot["external_derivative_word"] = [7, 9]
    renamed["coefficient_ast_sha256"] = gate._canonical_sha256(
        renamed["coefficient_ast"]
    )
    assert gate.canonicalize_frechet_row_binders(renamed) == row

    captured = copy.deepcopy(row)
    captured["coefficient_ast"]["external_derivative_word"] = [0, 1]
    captured["coefficient_ast_sha256"] = gate._canonical_sha256(
        captured["coefficient_ast"]
    )
    with pytest.raises(gate.GravityFrechetError, match="captured"):
        gate.validate_frechet_row(captured)


def test_decision_frontier_keeps_every_downstream_claim_false(report: dict) -> None:
    decision = report["decision"]
    assert {key for key, value in decision.items() if value} == {
        "literal_v5_2_EH_plus_minus_GHY_plus_minus_byte_bound_pass",
        "gravity_semantic_completion_pinned_pass",
        "typed_gravity_action_AST_with_declared_primitives_pass",
        "cofactor_normal_outward_and_Theta_equals_minus_n_dot_Q_pass",
        "EH_plus_minus_GHY_plus_minus_raw_formal_AST_Frechet_pass",
        "nilpotent_dual_equals_reverse_Frechet_exact_pass",
        "FrechetRowV1_four_component_export_pass",
    }
    assert decision["self_contained_gravity_action_AST_pass"] is False
    assert decision["EH_plus_minus_GHY_plus_minus_raw_semantic_Frechet_pass"] is False
    assert decision["independent_coordinate_Frechet_denotation_pass"] is False
    assert decision["S10_component_validator_interoperability_pass"] is False
    assert decision["fixed_embedding_xi_zero_normal_derivative_cancellation_pass"] is False
    assert decision["fixed_embedding_xi_zero_Brown_York_pairing_exact_pass"] is False
    assert decision["moving_embedding_shape_equation_pass"] is False
    assert decision["two_sided_EH_GHY_full_Green_pairing_exact_pass"] is False
    assert decision["all_twenty_components_semantic_Frechet_pass"] is False
    assert decision["C1_same_action_certificate_pass"] is False
    assert decision["N1_nonlinear_gravity_certificate_pass"] is False
    assert decision["promotion_or_publication_authorized"] is False
    assert report["evidence_boundary"]["artifact_written"] is False
    assert report["evidence_boundary"]["finite_exact_witnesses_used"] is True
    assert report["evidence_boundary"]["sampled_identity_used"] is False
    assert report["evidence_boundary"][
        "finite_witnesses_are_not_a_universal_identity"
    ] is True
    assert "independent symbolic whole-summand" in report["evidence_boundary"][
        "formal_identity_basis"
    ]
    assert report["evidence_boundary"]["numerical_tolerance_used"] is False


def test_type_checker_and_unknown_mutation_fail_closed() -> None:
    with pytest.raises(gate.GravityFrechetError, match="type mismatch"):
        gate.multilinear(
            "Christoffel_5",
            gate.field("bad", gate.METRIC5),
            gate.field("g1", gate.METRIC1JET5),
        )
    with pytest.raises(gate.GravityFrechetError, match="covariant_acceleration type mismatch"):
        gate.covariant_acceleration(
            gate.field("not_D2Y", gate.ACCELERATION5),
            gate.field("GammaYY", gate.ACCELERATION5),
        )
    with pytest.raises(gate.GravityFrechetError, match="unknown mutation"):
        dependency, action, green = gate.certify_v52_dependency()
        del dependency
        gate._build_core(gate.parse_charter(action), green, "not_registered")
