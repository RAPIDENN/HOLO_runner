#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_bps_radion_matter_coupling as coupling,
)


class BPSRadionMatterCouplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = coupling.build()

    def test_real_background_and_bps_branch_are_used(self) -> None:
        self.assertEqual(self.result["actual_background"]["samples"], 1979)
        self.assertTrue(
            self.result["checks"]["conditional_functional_BPS_branch_used"]
        )
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])
        self.assertTrue(
            self.result["full_moduli_space_gate"][
                "general_functional_BPS_system_may_be_biscalar"
            ]
        )
        self.assertFalse(
            self.result["full_moduli_space_gate"]["unique_canonical_q_selected"]
        )

    def test_einstein_frame_reduction_keeps_planck_coefficient_fixed(self) -> None:
        reduction = self.result["fixed_reduction"]
        self.assertIn("integral_[u_-,R]", reduction["four_dimensional_curvature_coefficient"])
        self.assertEqual(
            reduction["einstein_frame_map"], "g_E=[F(R)/F(R0)]*g_4"
        )
        self.assertTrue(
            self.result["checks"][
                "einstein_frame_planck_coefficient_is_constant"
            ]
        )

    def test_both_minimal_endpoint_selectors_have_linear_terms(self) -> None:
        expansions = self.result["endpoint_expansions_in_delta_R"]
        self.assertGreater(expansions["lower"]["c1"], 0.0)
        self.assertGreater(expansions["upper"]["c1"], 0.0)
        self.assertAlmostEqual(expansions["lower"]["c1"], 0.0197499449254)
        self.assertAlmostEqual(expansions["upper"]["c1"], 4.24994900419)
        self.assertTrue(
            self.result["checks"][
                "minimal_lower_matter_has_nonzero_linear_response"
            ]
        )
        self.assertTrue(
            self.result["checks"][
                "minimal_upper_matter_has_nonzero_linear_response"
            ]
        )

    def test_stationarity_failure_is_global_on_monotone_branch(self) -> None:
        background = self.result["actual_background"]
        self.assertGreater(
            background["minimum_lower_log_selector_derivative"], 0.0
        )
        self.assertGreater(
            background["minimum_upper_log_selector_derivative"], 0.0
        )
        self.assertTrue(
            self.result["checks"]["lower_selector_is_strictly_monotone"]
        )
        self.assertTrue(
            self.result["checks"]["upper_selector_is_strictly_monotone"]
        )

    def test_analytic_expansion_has_independent_local_fit(self) -> None:
        self.assertTrue(
            self.result["checks"][
                "analytic_first_derivatives_match_local_fit"
            ]
        )
        self.assertTrue(
            self.result["checks"][
                "analytic_quadratic_coefficients_match_local_fit"
            ]
        )

    def test_minimal_matter_fails_the_q2Y_gate_without_overclaiming_qY(self) -> None:
        gate = self.result["q2Y_gate"]
        self.assertFalse(
            gate["declared_separation_slice_minimal_lower_brane_passes"]
        )
        self.assertFalse(
            gate["declared_separation_slice_minimal_upper_brane_passes"]
        )
        self.assertTrue(
            gate["some_unselected_two_modulus_tangent_can_kill_one_first_jet"]
        )
        self.assertFalse(
            gate["same_nonzero_tangent_can_kill_both_endpoint_first_jets"]
        )
        self.assertFalse(gate["q_to_minus_q_symmetry_derived"])
        self.assertFalse(gate["pure_leading_q2Y_from_minimal_endpoint_matter"])
        self.assertFalse(gate["full_constraint_reduced_qY_coefficient_computed"])
        self.assertFalse(gate["q2Y_derived"])
        self.assertIn(
            "declared separation slice",
            self.result["full_moduli_space_gate"]["logical_scope"],
        )

    def test_two_modulus_tangent_is_exposed_but_not_selected(self) -> None:
        gate = self.result["full_moduli_space_gate"]
        gradients = gate["coordinate_gradients_d_ln_C_d_Yminus_d_Yplus"]
        self.assertNotEqual(gradients["determinant"], 0.0)
        tangents = gate["candidate_tangents_with_d_separation_equal_one"]
        self.assertFalse(tangents["selected_by_current_action"])
        self.assertFalse(tangents["canonically_normalized"])
        self.assertLess(
            max(abs(value) for value in tangents["orthogonality_residuals"]),
            1.0e-12,
        )

    def test_no_weyl_rescaling_is_explicitly_rejected(self) -> None:
        control = self.result["negative_control"]
        self.assertIn("appears independent", control["false_result"])
        self.assertIn("not in Einstein frame", control["why_invalid"])
        self.assertGreater(control["missed_log_derivative"], 0.0)

    def test_sextic_detuning_does_not_fix_linear_matter_response(self) -> None:
        statement = self.result["what_would_be_new_physics"][
            "sextic_detuning_relation"
        ]
        self.assertIn("cannot cancel", statement)

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if coupling.OUTPUT.exists():
            rendered = json.loads(coupling.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
