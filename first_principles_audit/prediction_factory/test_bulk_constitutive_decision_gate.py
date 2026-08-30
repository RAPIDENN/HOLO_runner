#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_bulk_constitutive_decision_gate as gate,
)


class BulkConstitutiveDecisionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    def test_algebra_passes_but_physical_completion_does_not(self) -> None:
        self.assertTrue(self.result["algebra_checks"]["all"])
        self.assertFalse(self.result["physical_gates"]["physical_completion"])
        self.assertIn("not_yet_derived", self.result["classification"])

    def test_old_and_new_mass_exponents_are_distinguished(self) -> None:
        comparison = self.result["old_vs_this"]
        self.assertEqual(comparison["old_fixed_poles"]["source_mass_exponent"], 1.0)
        self.assertEqual(
            comparison["this_critical_constitutive_response"][
                "source_mass_exponent"
            ],
            0.5,
        )
        self.assertLess(
            comparison["old_fixed_poles"]["three_halves_crossover_width_dex"],
            1.0,
        )

    def test_minimal_covariant_completion_exposes_characteristic_gate(self) -> None:
        audit = self.result["principal_symbol_audit"]
        self.assertAlmostEqual(
            audit["radial_over_transverse_characteristic_ratio"], 2.0
        )
        self.assertIn("degenerate", audit["vacuum_limit"])
        self.assertFalse(
            self.result["physical_gates"][
                "healthy_causal_covariant_completion_derived"
            ]
        )

    def test_conformal_acceleration_is_not_a_lensing_derivation(self) -> None:
        audit = self.result["matter_and_lensing_audit"]
        self.assertIn("Phi_J+Psi_J=Phi_E+Psi_E", audit["linear_conformal_map"])
        self.assertFalse(
            self.result["physical_gates"]["metric_slip_and_lensing_derived"]
        )

    def test_raw_cubic_progress_is_not_a_modal_coefficient_claim(self) -> None:
        progress = self.result["microscopic_progress"]
        self.assertIn("partial_A(varphi)", progress["raw_metric_scalar_derivative_vertex"])
        self.assertEqual(progress["fixed_metric_scalar_derivative_cubic"], "exactly zero")
        self.assertGreater(progress["heavy_unit_overlap_inverse_mass_squared_moment"], 0.0)
        self.assertFalse(progress["physical_c_a_computed"])
        self.assertFalse(progress["direct_S4_contact_computed"])
        self.assertIn("Delta P_exchange=-0.5", progress["gapped_exchange_contribution_to_P"])
        self.assertIn("C_Y2_direct_S4-0.5", progress["total_Y2_coefficient"])
        self.assertIn("mix gauges", progress["current_boundary"])

    def test_prospective_test_is_blind_and_fail_closed(self) -> None:
        prospective = self.result["prospective_bulk_test"]
        joined = " ".join(prospective["pre_registered_acceptance_conditions"])
        self.assertIn("Pi(g)/g^2", joined)
        self.assertIn("two source geometries", joined)
        self.assertFalse(prospective["can_run_with_current_frozen_inputs"])
        self.assertIn("inverse design", prospective["fail_closed_rule"])
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if gate.OUTPUT.exists():
            rendered = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
