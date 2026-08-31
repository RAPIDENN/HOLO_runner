#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_c3_geometric_transition_gate as gate,
)


class C3GeometricTransitionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    @staticmethod
    def _hypotheses(
        value: bool, *, competing_gap: bool | None = None
    ) -> dict[str, bool]:
        payload = {key: value for key in gate.LOCAL_THEOREM_HYPOTHESES}
        payload[gate.GLOBAL_EXTENSION_HYPOTHESIS] = (
            value if competing_gap is None else competing_gap
        )
        return payload

    def test_all_existing_precursors_are_certified(self) -> None:
        self.assertTrue(all(self.result["precursor_certificates"].values()))
        self.assertTrue(
            self.result["checks"]["all_upstream_mathematical_certificates_pass"]
        )

    def test_missing_inputs_block_c3_without_killing_it(self) -> None:
        decision = self.result["decision"]
        self.assertEqual(decision["input_status"], "INPUT_INCOMPLETE")
        self.assertEqual(decision["status"], "BLOCKED_C3")
        self.assertFalse(decision["kill_triggered"])
        self.assertFalse(decision["candidate_passed"])
        self.assertFalse(self.result["input_completeness"]["all"])
        self.assertGreater(len(decision["missing_requirement_ids"]), 0)

    def test_required_missing_action_constraint_and_matter_inputs_are_explicit(
        self,
    ) -> None:
        missing = set(self.result["input_completeness"]["missing_requirement_ids"])
        self.assertTrue(
            {
                "R2_complete_boundary_action_and_jets_frozen",
                "R3_eh_ghy_boundary_variation_complete",
                "R4_nonlinear_junctions_with_bending_complete",
                "R5_nonlinear_lapse_shift_and_dirac_system_complete",
                "R6_matter_action_localization_and_source_frozen",
            }.issubset(missing)
        )

    def test_analytic_theorem_applies_only_when_every_local_hypothesis_holds(
        self,
    ) -> None:
        complete = gate.analytic_branch_theorem(self._hypotheses(True))
        self.assertEqual(complete["local_status"], "APPLIES")
        self.assertTrue(complete["local_unique_analytic_stationary_branch"])
        self.assertTrue(complete["local_onshell_map_is_analytic"])
        self.assertTrue(complete["first_order_crossing_excluded"])
        self.assertFalse(complete["physical_no_go_claimed"])

        missing_rank = self._hypotheses(True)
        missing_rank["dirac_rank_constant"] = False
        incomplete = gate.analytic_branch_theorem(missing_rank)
        self.assertEqual(incomplete["local_status"], "NOT_APPLICABLE")
        self.assertFalse(incomplete["local_onshell_map_is_analytic"])
        self.assertFalse(incomplete["first_order_crossing_excluded"])

    def test_local_ift_does_not_exclude_a_distinct_first_order_branch(self) -> None:
        local_only = gate.analytic_branch_theorem(
            self._hypotheses(True, competing_gap=False)
        )
        self.assertEqual(local_only["local_status"], "APPLIES")
        self.assertTrue(local_only["local_onshell_map_is_analytic"])
        self.assertEqual(local_only["selected_ground_state_status"], "UNDECIDED")
        self.assertFalse(local_only["first_order_crossing_excluded"])

    def test_theorem_interface_rejects_missing_or_non_boolean_hypotheses(self) -> None:
        incomplete = self._hypotheses(True)
        incomplete.pop("dirac_rank_constant")
        with self.assertRaises(ValueError):
            gate.analytic_branch_theorem(incomplete)
        malformed = self._hypotheses(True)
        malformed["dirac_rank_constant"] = 1  # type: ignore[assignment]
        with self.assertRaises(TypeError):
            gate.analytic_branch_theorem(malformed)

    def test_schur_control_separates_invertible_and_singular_auxiliaries(self) -> None:
        regular = gate.schur_gap_certificate(
            np.asarray([[3.0, 0.2], [0.2, 2.0]]),
            np.asarray([[2.0]]),
            np.asarray([[0.5], [0.25]]),
        )
        self.assertTrue(regular["auxiliary_invertible"])
        self.assertTrue(regular["reduced_positive_gap"])
        self.assertGreater(regular["reduced_gap"], 0.0)
        self.assertFalse(regular["constant_rank_in_neighborhood_certified"])

        singular = gate.schur_gap_certificate(
            np.eye(2), np.asarray([[0.0]]), np.zeros((2, 1))
        )
        self.assertEqual(singular["status"], "NOT_APPLICABLE_AUXILIARY_SINGULAR")
        self.assertFalse(singular["auxiliary_invertible"])
        self.assertIsNone(singular["reduced_hessian"])
        for certificate in (regular, singular):
            self.assertEqual(certificate["scope"], "algebraic_auxiliaries_only")
            self.assertFalse(
                certificate["adm_lapse_shift_or_boundary_value_problem_certified"]
            )

    def test_baseline_positive_s2_is_not_reused_as_candidate_gap(self) -> None:
        requirement = self.result["required_inputs"][
            "R9_candidate_spectrum_symbol_and_free_energy_gap_complete"
        ]
        self.assertFalse(requirement["present"])
        self.assertIn("cannot be reused", requirement["consequence_if_missing"])
        adjudication = self.result["candidate_spectral_adjudication"]
        self.assertFalse(adjudication["calculation_complete"])
        self.assertFalse(
            adjudication["exactly_one_physical_critical_collective"]["evaluated"]
        )
        self.assertFalse(
            adjudication["uniform_positive_gap_on_noncollective_complement"][
                "evaluated"
            ]
        )
        self.assertFalse(
            adjudication["full_linearized_operator_isomorphism"]["certified"]
        )

    def test_frozen_inputs_do_not_auto_certify_functional_analysis(self) -> None:
        adjudication = self.result["functional_analytic_adjudication"]
        for key in (
            "maps_analytic_between_fixed_banach_spaces",
            "gauge_fixed_boundary_value_problem_complete",
            "dirac_rank_constant",
            "algebraic_auxiliary_jacobian_invertible_or_absent",
        ):
            self.assertFalse(adjudication[key]["evaluated"])
            self.assertFalse(adjudication[key]["certified"])
        certified = self.result["analytic_branch_theorem"]["certified_hypotheses"]
        self.assertFalse(certified["maps_analytic_between_fixed_banach_spaces"])
        self.assertFalse(certified["gauge_fixed_boundary_value_problem_complete"])

    def test_kill_criteria_are_declared_but_not_evaluated(self) -> None:
        criteria = self.result["kill_criteria"]
        self.assertGreaterEqual(len(criteria), 8)
        self.assertEqual(
            len({criterion["id"] for criterion in criteria}), len(criteria)
        )
        for criterion in criteria:
            self.assertFalse(criterion["evaluated"])
            self.assertEqual(criterion["result"], "NOT_EVALUATED_INPUT_INCOMPLETE")

        by_id = {criterion["id"]: criterion for criterion in criteria}
        self.assertIn(
            "Dirac rank changes", by_id["K4_gauge_or_constraint_artifact"]["kill_if"]
        )
        gap_gate = by_id["K8_noncollective_gap_or_cutoff_failure"]["kill_if"]
        self.assertIn("tower accumulates at zero", gap_gate)
        self.assertIn("EFT cutoff", gap_gate)

    def test_campaign_projection_keeps_ready_step_checks_pending(self) -> None:
        projection = self.result["campaign_step_projection"]
        self.assertEqual(projection["step_id"], "C3")
        self.assertEqual(projection["family"], "geometric_brane_transition")
        self.assertEqual(projection["status"], "ready")
        self.assertIn("not a standalone", projection["projection_scope"])
        self.assertEqual(
            tuple(row["id"] for row in projection["checks"]),
            gate.C3_CAMPAIGN_CHECK_IDS,
        )
        self.assertTrue(all(row["status"] == "pending" for row in projection["checks"]))
        self.assertTrue(all(row["evidence_refs"] == [] for row in projection["checks"]))

    def test_certificate_reads_no_observational_data(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["checks"]["no_observational_data_read"])
        for receipt in self.result["sources"]["artifacts"].values():
            self.assertEqual(len(receipt["sha256"]), 64)
            self.assertFalse(receipt["path"].startswith("/"))

    def test_generated_artifact_matches_fresh_builder(self) -> None:
        stored = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.result)


if __name__ == "__main__":
    unittest.main()
