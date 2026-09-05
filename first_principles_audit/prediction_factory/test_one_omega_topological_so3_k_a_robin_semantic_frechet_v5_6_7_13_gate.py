#!/usr/bin/env python3
"""Independent tests for the narrow v5.6.7.13 K/a/Robin raw gate."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "derive_one_omega_topological_so3_k_a_robin_semantic_frechet_v5_6_7_13_gate.py"

EXPECTED_SCHEMA = "holo.one-omega-topological-so3-k-a-robin-semantic-frechet-v5-6-7-13.v1"
EXPECTED_SEMANTIC_SHA256 = "8020baa5a3dad7c2cf17ea49ed7053603a0a10b0a47b65cda030f83f1bef2123"
EXPECTED_HASHES = {
    "component_ASTS_sha256": "00fd2501d34305fd49f02da61d15b109d7c74a4b0449fa89b76838b06da8668e",
    "raw_rows_sha256": "5457e0486676ac265b640dcd2e9162a37d7ef023e366f634dae865601cbfa580",
    "coefficient_DAG_sha256": "e1574b8e7343082c161234147e437220f516392e7c175bce618fa0da433c1579",
}
EXPECTED_ROW_COUNTS = {"K_foliation": 64, "a_squared": 64, "Robin": 68}
EXPECTED_CORE_MUTANTS = {
    "correlated_wrong_inverse_sign",
    "correlated_wrong_volume_half",
    "correlated_wrong_fractional_power_sign",
    "correlated_hidden_offdiagonal_term",
    "serializer_leaf_relabel_after_repin",
    "wrong_christoffel_last_sign",
    "wrong_K_lambda_sign",
    "wrong_a_prefactor_half",
    "wrong_Robin_cross_sign",
    "wrong_Robin_prefactor_sign",
    "omit_Robin_varphi",
    "frechet_times_finite_gamma_factor",
    "frechet_times_parameter_y_alias_factor",
    "frechet_times_tau_varphi_double_zero_factor",
    "component_form_redistribution_preserving_aggregate",
}
EXPECTED_FINITE_LOCUS_EXPLOITS = {
    "frechet_times_finite_gamma_factor",
    "frechet_times_parameter_y_alias_factor",
    "frechet_times_tau_varphi_double_zero_factor",
    "component_form_redistribution_preserving_aggregate",
    "orientation_odd_double_zero",
}
EXPECTED_SCHEMA_MUTANTS = {
    "unknown_opcode_rejected_after_rehash",
    "extra_node_field_rejected_after_rehash",
    "bad_opcode_arity_rejected_after_rehash",
    "extra_row_field_rejected",
    "slot_field_mismatch_rejected",
    "noncanonical_tensor_indices_rejected",
    "noncontiguous_component_ordinal_rejected",
    "literal_source_span_drift_rejected",
    "component_root_and_span_swap_rejected_after_repin",
    "within_component_root_swap_rejected",
    "global_component_interleave_rejected",
    "swap_exported_variation_labels_after_repin_rejected",
}
EXPECTED_TRUE_DECISIONS = {
    "fixed_domain_K_a_Robin_semantic_completion_pinned_pass",
    "K_a_Robin_raw_Frechet_exact_under_displayed_completion_pass",
    "strict_RawFrechetRowV1_export_pass",
}


def _load() -> object:
    spec = importlib.util.spec_from_file_location("kar_v56713_under_test", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import v5.6.7.13 source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GATE = _load()
REPORT = GATE.build_report()


class KARRawFrechetGateTests(unittest.TestCase):
    def test_report_schema_and_every_narrow_check_close(self) -> None:
        self.assertEqual(REPORT["schema"], EXPECTED_SCHEMA)
        self.assertIs(REPORT["checks"]["all"], True)
        self.assertTrue(all(REPORT["checks"].values()))

    def test_only_the_three_narrow_decisions_are_true(self) -> None:
        true_keys = {key for key, value in REPORT["decision"].items() if value is True}
        self.assertEqual(true_keys, EXPECTED_TRUE_DECISIONS)
        self.assertIs(REPORT["decision"]["C1_ACTION_pass"], False)
        self.assertIs(REPORT["decision"]["N1_ACTION_pass"], False)
        self.assertIs(REPORT["decision"]["publication_authorized"], False)

    def test_dependency_bytes_and_commit_lineage_are_exact(self) -> None:
        observed = REPORT["lineage"]["observed_source_test_sha256"]
        self.assertEqual(observed, GATE.PINNED_INPUTS)
        self.assertEqual(
            REPORT["lineage"]["declared_commits"]["S10_exact_eleven_rows"],
            "e8f831ddb383598c9b74b1606c87674bbd476617",
        )
        self.assertIn("not imported as raw rows", REPORT["lineage"]["S8_role"])

    def test_completion_is_live_pinned_and_unambiguously_raw(self) -> None:
        self.assertEqual(REPORT["semantic_completion_sha256"], EXPECTED_SEMANTIC_SHA256)
        self.assertEqual(REPORT["semantic_completion"]["stage"], "raw_Frechet_before_formal_adjoint")
        self.assertIn("formal adjoint and integration by parts", REPORT["semantic_completion"]["excluded"])
        self.assertEqual(REPORT["scope"]["included_components"], ["K_foliation", "a_squared", "Robin"])

    def test_aggregate_hashes_match_independent_test_constants(self) -> None:
        self.assertEqual(REPORT["aggregate_hashes"], EXPECTED_HASHES)
        self.assertEqual(GATE.EXPECTED_COMPONENT_ASTS_SHA256, EXPECTED_HASHES["component_ASTS_sha256"])
        self.assertEqual(GATE.EXPECTED_RAW_ROWS_SHA256, EXPECTED_HASHES["raw_rows_sha256"])
        self.assertEqual(GATE.EXPECTED_COEFFICIENT_DAG_SHA256, EXPECTED_HASHES["coefficient_DAG_sha256"])

    def test_rows_are_separate_by_component_and_have_expected_field_orders(self) -> None:
        rows = REPORT["RawFrechetRowV1"]
        counts = {name: sum(row["component"] == name for row in rows) for name in EXPECTED_ROW_COUNTS}
        self.assertEqual(counts, EXPECTED_ROW_COUNTS)
        self.assertEqual(REPORT["component_certificate"]["K_foliation"]["slots"], ["H", "tau"])
        self.assertEqual(REPORT["component_certificate"]["a_squared"]["slots"], ["H", "tau"])
        self.assertEqual(REPORT["component_certificate"]["Robin"]["slots"], ["H", "tau", "v"])
        self.assertTrue(all(row["domain"] == "Sigma" for row in rows))
        roots = {name: {row["coefficient_root_sha256"] for row in rows if row["component"] == name} for name in EXPECTED_ROW_COUNTS}
        self.assertTrue(all(roots[left].isdisjoint(roots[right]) for left in roots for right in roots if left < right))

    def test_every_source_span_round_trips_to_the_literal_action(self) -> None:
        action, _ = GATE.certify_dependencies()
        for row in REPORT["RawFrechetRowV1"]:
            span = row["source_span"]
            self.assertEqual(action[span["action_key"]][span["start"] : span["end"]], span["text"])
        self.assertIn("lambda_K*Kcal^2", next(row for row in REPORT["RawFrechetRowV1"] if row["component"] == "K_foliation")["source_span"]["text"])
        self.assertEqual(next(row for row in REPORT["RawFrechetRowV1"] if row["component"] == "a_squared")["source_span"]["text"], "eta*a_mu*a^mu")

    def test_strict_schema_revalidates_full_DAG_and_rows(self) -> None:
        action, _ = GATE.certify_dependencies()
        rows = REPORT["RawFrechetRowV1"]
        dag = REPORT["coefficient_DAG"]
        self.assertEqual(len(dag), 59665)
        self.assertTrue(GATE.validate_raw_rows(rows, dag, action))
        self.assertTrue(GATE.validate_coefficient_dag(dag, [row["coefficient_root_sha256"] for row in rows]))

    def test_every_exported_root_decodes_to_its_original_symbolic_form(self) -> None:
        action, _ = GATE.certify_dependencies()
        program = GATE.build_component_program(action)
        forms = {name: GATE.frechet(expr) for name, expr in program.components.items()}
        independent_program = GATE.independent_literal_component_program(action)
        independent_forms = {
            name: GATE.reverse_context_frechet(expr)
            for name, expr in independent_program.components.items()
        }
        self.assertTrue(
            GATE.validate_expr_row_dag_binding(
                forms,
                REPORT["RawFrechetRowV1"],
                REPORT["coefficient_DAG"],
                independent_forms,
            )
        )
        self.assertIs(
            REPORT["checks"][
                "every_Expr_row_root_decodes_back_to_the_same_symbolic_coefficient"
            ],
            True,
        )

    def test_complete_symbolic_forms_match_independent_literal_context_route(self) -> None:
        certificate = REPORT["exact_symbolic_semantic_certificate"]
        self.assertIs(certificate["pass"], True)
        self.assertIs(certificate["component_roots_bound_to_literal_program"], True)
        self.assertIs(
            certificate["all_component_variation_keys_and_coefficients_exact"],
            True,
        )
        self.assertIn("universal identity", certificate["epistemic_scope"])
        self.assertIn("not inferred from numerical witnesses", certificate["epistemic_scope"])
        self.assertIs(certificate["local_calculus_rules"]["pass"], True)
        self.assertTrue(
            all(certificate["local_calculus_rules"]["coordinate_partial_rows"].values())
        )
        for name, expected_count in EXPECTED_ROW_COUNTS.items():
            row = certificate["component_rows"][name]
            self.assertIs(row["pass"], True)
            self.assertEqual(row["coefficient_count"], expected_count)
            self.assertEqual(
                row["primary_root_expr_sha256"],
                row["independent_literal_root_expr_sha256"],
            )

        for function in (
            GATE.reverse_context_frechet,
            GATE._independent_literal_component_program_cached,
        ):
            tree = ast.parse(inspect.getsource(function))
            calls = {
                node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            self.assertTrue(
                calls.isdisjoint(
                    {
                        "frechet",
                        "export_raw_rows",
                        "export_coefficient_dag",
                        "build_component_program",
                    }
                )
            )

    def test_independent_oracle_checks_every_basis_coefficient_twice(self) -> None:
        oracle = REPORT["independent_exact_oracle"]
        self.assertEqual(oracle["variation_basis_size"], 68)
        self.assertEqual(oracle["total_frechet_comparisons"], 408)
        self.assertIs(oracle["all_primal_components_match"], True)
        self.assertIs(oracle["all_basis_Frechet_coefficients_match"], True)
        self.assertIs(oracle["all_rational_congruence_witnesses_verified"], True)
        self.assertEqual(oracle["mismatch_examples"], [])
        self.assertEqual([row["mismatches"] for row in oracle["witnesses"]], [0, 0])
        self.assertTrue(all(row["rational_congruence_geometry_pass"] for row in oracle["witnesses"]))
        self.assertIn("finite exact evaluation", oracle["epistemic_scope"])
        self.assertIn("not a universal identity by sampling", oracle["epistemic_scope"])

    def test_test_local_exact_primal_values_prevent_producer_repinning(self) -> None:
        expected = {
            1: {
                "K_foliation": [40325205763902394512593044695862453040833351777, 987475306242820960395909887255012966400000000],
                "a_squared": [234827973018831785315747526394287145360265521, 17273620517367130502552359543819468800000000],
                "Robin": [-367358490532105791947813068044094749560508721, 58960624699279805448712053909570453504000000],
            },
            2: {
                "K_foliation": [18524139297215609906472168987066892129019569450873, 4618354975051955023999981516365810892800000000],
                "a_squared": [704007802628784250296697650907222974043780519777, 101792313735839008692244490564797464576000000],
                "Robin": [-696758112520824230309356524144460919781805496161, 303084265095066744404034303476132955448934400],
            },
        }
        for seed, target in expected.items():
            observed = GATE.independent_dual_components(GATE._fraction_witness(seed), {})
            self.assertEqual(
                {name: [value.primal.numerator, value.primal.denominator] for name, value in observed.items()},
                target,
            )

    def test_test_local_exact_directional_values_cover_all_three_slots(self) -> None:
        cases = {
            GATE._variation_key("H", (), (0, 0)): {
                "K_foliation": [-5024145296821344632416046667969230373789340417062349236649, 10836051583272900872080065663785876942676295680000000000],
                "a_squared": [-42516144465763647058960085996447856009394700324722931449, 189551922739467653739009894993338955265474560000000000],
                "Robin": [50673709677642760341630068652303797754712176064039974649, 647003896284049591429153774910596967306153164800000000],
            },
            GATE._variation_key("tau", (1, 2), ()): {
                "K_foliation": [2322822442091966066532317419, 457144391653515845959680000],
                "a_squared": [-2290658047170588457205976079, 279884321420519905689600000],
                "Robin": [2416970850101443897196760079, 955338483782041278087168000],
            },
            GATE._variation_key("v", (), (3,)): {
                "K_foliation": [0, 1],
                "a_squared": [0, 1],
                "Robin": [-27758890119273022442059189, 4975721269698131656704000],
            },
        }
        witness = GATE._fraction_witness(1)
        for key, target in cases.items():
            observed = GATE.independent_dual_components(witness, GATE._basis_tangent(key))
            self.assertEqual(
                {name: [value.tangent.numerator, value.tangent.denominator] for name, value in observed.items()},
                target,
            )

    def test_correlated_rule_mutants_fail_after_internal_hash_repin(self) -> None:
        campaign = REPORT["correlated_repin_mutation_campaign"]
        self.assertEqual(set(campaign), EXPECTED_CORE_MUTANTS)
        for name, row in campaign.items():
            with self.subTest(name=name):
                self.assertIs(row["internal_hashes_repinned"], True)
                self.assertIs(row["ready_after_repin"], False)
                self.assertTrue(
                    not row["exact_symbolic_semantic_pass"]
                    or not row["Expr_row_DAG_structural_binding_pass"]
                    or not row["primal_oracle_pass"]
                    or not row["Frechet_oracle_pass"]
                )
        for name in {
            "correlated_wrong_inverse_sign",
            "correlated_wrong_volume_half",
            "correlated_wrong_fractional_power_sign",
        }:
            self.assertIs(campaign[name]["primal_oracle_pass"], True)
            self.assertIs(campaign[name]["Frechet_oracle_pass"], False)

    def test_formula_sign_and_prefactor_mutants_fail_primal_oracle(self) -> None:
        campaign = REPORT["correlated_repin_mutation_campaign"]
        for name in EXPECTED_CORE_MUTANTS - {
            "correlated_wrong_inverse_sign",
            "correlated_wrong_volume_half",
            "correlated_wrong_fractional_power_sign",
            "serializer_leaf_relabel_after_repin",
            "frechet_times_finite_gamma_factor",
            "frechet_times_parameter_y_alias_factor",
            "frechet_times_tau_varphi_double_zero_factor",
            "component_form_redistribution_preserving_aggregate",
        }:
            with self.subTest(name=name):
                self.assertIs(campaign[name]["primal_oracle_pass"], False)
                self.assertIs(campaign[name]["Frechet_oracle_pass"], False)

    def test_five_finite_locus_exploits_pass_samples_but_fail_symbolically(self) -> None:
        certificate = REPORT["mandatory_finite_locus_exploit_certificate"]
        self.assertIs(certificate["pass"], True)
        self.assertEqual(set(certificate["rows"]), EXPECTED_FINITE_LOCUS_EXPLOITS)
        self.assertIn("finite exact regressions", certificate["witness_role"])
        for name, row in certificate["rows"].items():
            with self.subTest(name=name):
                self.assertIs(row["internal_hashes_repinned"], True)
                self.assertIs(row["finite_witness_oracle_pass"], True)
                self.assertIs(row["exact_symbolic_semantic_pass"], False)
                self.assertIs(row["independent_route_binding_pass"], False)
                self.assertIs(row["strict_schema_pass"], True)
                self.assertIs(row["ready_after_repin"], False)
        redistribution = certificate["rows"][
            "component_form_redistribution_preserving_aggregate"
        ]
        self.assertIs(
            redistribution["aggregate_form_preserved_vs_unmutated"], True
        )

    def test_hidden_offdiagonal_and_serializer_relabel_exploits_are_rejected(self) -> None:
        campaign = REPORT["correlated_repin_mutation_campaign"]
        hidden = campaign["correlated_hidden_offdiagonal_term"]
        self.assertIs(hidden["internal_hashes_repinned"], True)
        self.assertIs(hidden["primal_oracle_pass"], False)
        self.assertIs(hidden["Frechet_oracle_pass"], False)
        self.assertIs(hidden["ready_after_repin"], False)
        serializer = campaign["serializer_leaf_relabel_after_repin"]
        self.assertIs(serializer["internal_hashes_repinned"], True)
        self.assertIs(serializer["Expr_row_DAG_structural_binding_pass"], False)
        self.assertIs(serializer["Frechet_oracle_pass"], False)
        self.assertIs(serializer["ready_after_repin"], False)

    def test_exhaustive_node_and_row_schema_mutants_are_rejected(self) -> None:
        campaign = REPORT["strict_schema_mutation_campaign"]
        self.assertEqual(set(campaign), EXPECTED_SCHEMA_MUTANTS)
        self.assertTrue(all(campaign.values()))

    def test_even_densities_do_not_fabricate_an_orientation_choice(self) -> None:
        orientation = REPORT["orientation_invariance"]
        self.assertIs(orientation["universal_symbolic_invariance"], True)
        self.assertIs(orientation["exact_rational_invariance"], True)
        self.assertIs(orientation["finite_witness_regression_only"], True)
        self.assertIs(orientation["orientation_parity_calculus"]["pass"], True)
        self.assertTrue(
            all(
                row["pass"]
                for row in orientation["symbolic_component_bindings"].values()
            )
        )
        self.assertIs(orientation["orientation_selected_by_this_gate"], False)
        self.assertTrue(all(row["witness_pass"] for row in orientation["witnesses"]))
        self.assertTrue(
            all(
                row["all_AST_basis_coefficients_plus_equal_minus"]
                and row["both_AST_basis_routes_match_independent_oracles"]
                for row in orientation["witnesses"]
            )
        )
        self.assertIs(REPORT["decision"]["time_orientation_selected_by_K_a_Robin_even_densities_pass"], False)

    def test_orientation_odd_builder_mutant_is_rejected(self) -> None:
        attack = REPORT["orientation_odd_mutation_probe"]
        self.assertEqual(attack["mutation"], "orientation_odd_hidden_term")
        self.assertIs(attack["exact_rational_invariance"], False)
        self.assertIs(attack["universal_symbolic_invariance"], False)
        self.assertTrue(any(not row["witness_pass"] for row in attack["witnesses"]))

    def test_orientation_odd_double_zero_is_rejected_before_finite_witnesses(self) -> None:
        attack = REPORT["orientation_odd_double_zero_mutation_probe"]
        self.assertEqual(attack["mutation"], "orientation_odd_double_zero")
        self.assertIs(attack["exact_rational_invariance"], True)
        self.assertIs(attack["universal_symbolic_invariance"], False)
        self.assertTrue(all(row["witness_pass"] for row in attack["witnesses"]))
        self.assertIs(
            attack["symbolic_component_bindings"]["K_foliation"]["pass"],
            False,
        )
        pipeline = attack["repinned_export_pipeline"]
        self.assertIs(pipeline["all_internal_hashes_repinned"], True)
        self.assertIs(pipeline["all_strict_schema_pass"], True)
        self.assertIs(pipeline["finite_witness_oracle_pass"], True)
        self.assertIs(pipeline["all_independent_row_DAG_bindings_pass"], False)
        self.assertIs(pipeline["ready_after_repin"], False)
        for sign, row in pipeline["orientation_signs"].items():
            with self.subTest(sign=sign):
                self.assertEqual(row["row_count"], 196)
                self.assertGreater(row["DAG_node_count"], 0)
                self.assertEqual(row["observed_hashes"], row["repinned_hashes"])
                self.assertTrue(all(row["pin_checks"].values()))
                self.assertIs(row["strict_schema_pass"], True)
        self.assertIs(
            pipeline["orientation_signs"]["u_sign_minus"][
                "independent_row_DAG_binding_pass"
            ],
            True,
        )
        self.assertIs(
            pipeline["orientation_signs"]["u_sign_plus"][
                "independent_row_DAG_binding_pass"
            ],
            False,
        )

    def test_varphi_completion_does_not_claim_horizontal_or_groupoid_assembly(self) -> None:
        completion = REPORT["semantic_completion"]
        self.assertIn("independent contravariant coordinate components", completion["independent_coordinate_jets"]["varphi_H^m"])
        self.assertIs(REPORT["decision"]["horizontal_varphi_H_constraint_preservation_pass"], False)
        self.assertIs(REPORT["decision"]["frame_and_SO3_groupoid_Robin_variation_pass"], False)
        self.assertIs(REPORT["decision"]["bulk_GHY_interface_assembly_pass"], False)

    def test_no_artifact_is_declared_and_report_is_strict_json(self) -> None:
        self.assertFalse(hasattr(GATE, "OUTPUT"))
        encoded = json.dumps(GATE._jsonable(REPORT), sort_keys=True, allow_nan=False)
        self.assertIn(EXPECTED_SCHEMA, encoded)
        self.assertNotIn("NaN", encoded)

    def test_source_has_no_artifact_writer_or_promoted_claim_assignment(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("write_text(", source)
        self.assertNotIn("open(OUTPUT", source)
        self.assertIn('"C1_ACTION_pass": False', source)
        self.assertIn('"N1_ACTION_pass": False', source)
        self.assertIn('"publication_authorized": False', source)

    def test_source_digest_is_reportable_but_not_self_pinned(self) -> None:
        digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        self.assertEqual(len(digest), 64)
        self.assertNotIn(digest, SOURCE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
