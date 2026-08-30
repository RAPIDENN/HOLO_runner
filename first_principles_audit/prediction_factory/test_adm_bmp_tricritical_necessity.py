#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_adm_bmp_tricritical_necessity as necessity,
)


class RealADMBMPTricriticalNecessityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = necessity.build()

    def test_uses_real_background_and_no_synthetic_fixture(self) -> None:
        self.assertEqual(self.result["actual_background"]["samples"], 1979)
        self.assertTrue(
            self.result["checks"]["synthetic_bent_geometry_not_imported"]
        )
        paths = str(self.result["inputs"]["files"])
        self.assertNotIn("bent_brane_geometry", paths)

    def test_symbolic_single_interval_action_cancels(self) -> None:
        symbolic = self.result["symbolic_static_ADM_reduction"]
        self.assertTrue(symbolic["bulk_density_equals_total_derivative"])
        self.assertTrue(symbolic["on_shell_action_cancels"])
        self.assertEqual(symbolic["on_shell_action_coefficient_sum"], "0")
        self.assertTrue(symbolic["lower_scalar_junction_zero"])
        self.assertTrue(symbolic["upper_scalar_junction_zero"])
        self.assertTrue(symbolic["lower_Israel_junction_zero"])
        self.assertTrue(symbolic["upper_Israel_junction_zero"])
        self.assertTrue(symbolic["Hamilton_Jacobi_square_completion_exact"])
        self.assertEqual(symbolic["zero_mode_bulk_equation_residuals"], ["0", "0"])

    def test_raw_real_action_cancels_and_mutation_fails(self) -> None:
        action = self.result["raw_actual_interval_action"]
        self.assertEqual(len(action["rows"]), len(necessity.PAIR_FRACTIONS))
        self.assertLess(
            action["maximum_relative_cancellation"],
            necessity.CRITERIA["raw_action_relative_max"],
        )
        self.assertGreater(
            action["minimum_wrong_sign_relative_residual"],
            necessity.CRITERIA["mutation_min_relative"],
        )

    def test_zero_modes_have_positive_finite_kinetic_gram(self) -> None:
        kernel = self.result["massless_kernel"]
        self.assertTrue(kernel["normalizable"])
        self.assertEqual(kernel["candidate_bulk_zero_mode_count"], 2)
        self.assertFalse(kernel["finite_endpoint_physical_mode_count_resolved"])
        self.assertGreater(
            min(kernel["Gram_eigenvalues"]),
            necessity.CRITERIA["zero_mode_gram_min_eigenvalue"],
        )
        self.assertEqual(
            kernel["single_interval_kinetic_metric"],
            "G_ab=6*I_ab/kappa5^2",
        )

    def test_conclusion_is_conditional_and_sextic_is_zero(self) -> None:
        theorem = self.result["flatness_theorem"]
        gate = self.result["tricritical_gate"]
        self.assertEqual(theorem["result"], "V_eff(R)=0 identically")
        self.assertTrue(gate["m2_zero"])
        self.assertTrue(gate["u4_zero"])
        self.assertFalse(gate["positive_q6"])
        self.assertTrue(
            gate["conditional_positive_q6_from_sixth_order_brane_detuning"]
        )
        self.assertFalse(gate["q2Y_derived"])
        self.assertFalse(gate["physical_tricritical_mechanism_complete"])
        self.assertFalse(
            self.result["scope_boundary"]["functional_BPS_branch_selected_by_bulk"]
        )
        self.assertFalse(
            self.result["scope_boundary"]["m2_u4_zero_from_bulk_alone"]
        )
        self.assertFalse(
            self.result["scope_boundary"]["unique_canonical_radion_selected"]
        )
        self.assertFalse(gate["unique_canonical_q_selected"])
        self.assertIn(
            "not a consequence", self.result["scope_boundary"]["therefore"]
        )

    def test_biscalar_moduli_gate_replaces_common_translation_claim(self) -> None:
        coordinate = self.result["correct_collective_coordinate"]
        self.assertIn("bi-scalar", coordinate["two_moduli_warning"])
        self.assertIn("finite-endpoint", coordinate["canonical_projection_gate"])
        self.assertNotIn("common endpoint translation is gauge", str(coordinate))

    def test_cubic_is_rejected_and_clean_sextic_is_only_a_candidate(self) -> None:
        candidate = self.result["localized_non_BPS_sextic_candidate"]
        self.assertIn("starts at q^3", candidate["cubic_warning"])
        self.assertIn("^6/6!", candidate["clean_local_deformation"])
        self.assertTrue(candidate["background_junctions_unchanged"])
        self.assertTrue(candidate["BPS_action_through_fifth_order_unchanged"])
        self.assertTrue(candidate["positive_g6_if_all_nonzero_rho_are_positive"])
        self.assertFalse(candidate["rho_i_selected_by_bulk"])
        self.assertFalse(candidate["full_S6_lapse_shift_bending_projection_executed"])
        self.assertFalse(candidate["q2Y_generated_by_pure_brane_potential"])
        self.assertGreater(candidate["endpoint_exp4A"]["lower"], 0.0)
        self.assertGreater(candidate["endpoint_exp4A"]["upper"], 0.0)

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if necessity.OUTPUT.exists():
            rendered = json.loads(necessity.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
