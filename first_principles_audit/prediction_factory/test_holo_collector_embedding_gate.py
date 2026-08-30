#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import derive_holo_collector_embedding_gate as gate
except ModuleNotFoundError:
    import derive_holo_collector_embedding_gate as gate


class HoloCollectorEmbeddingGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    def test_current_yukawa_tower_is_linear_in_source_mass(self) -> None:
        certificate = self.result["source_scaling_certificate"]
        self.assertEqual(certificate["current_fixed_radius_mass_exponent"], 1.0)
        self.assertLess(certificate["current_numerical_exponent_max_abs_error"], 1.0e-11)

    def test_collector_tends_to_half_power(self) -> None:
        exponent = gate.collector_source_exponent(np.array([1.0e-16, 1.0e-12, 1.0e12]))
        self.assertAlmostEqual(exponent[0], 0.5, delta=1.0e-8)
        self.assertAlmostEqual(exponent[1], 0.5, delta=1.0e-6)
        self.assertAlmostEqual(exponent[2], 1.0, delta=1.0e-12)

    def test_fixed_linear_modes_cannot_embed_deep_collector(self) -> None:
        self.assertTrue(self.result["passes"]["audit_complete"])
        self.assertFalse(
            self.result["passes"]["linearized_current_sector_can_embed_collector"]
        )
        self.assertIn("conditional_no_go", self.result["classification"])
        self.assertIn("full_nonlinear_holo_completion_unresolved", self.result["classification"])
        operator = self.result["operator_certificate"]
        self.assertGreater(operator["current_positive_quadratic_carrier"]["p_min"], 0.0)
        self.assertGreater(operator["current_positive_quadratic_carrier"]["w_min"], 0.0)
        self.assertFalse(
            operator["current_boundary_operator_inventory"]
            ["derivative_kinetic_operator_present"]
        )

    def test_gate_does_not_read_observational_tables(self) -> None:
        self.assertEqual(self.result["scope"]["observational_inputs_read_by_this_gate"], [])
        self.assertIn(
            "exposed_empirical_target_read_for_comparison_only",
            self.result["scope"],
        )

    def test_theory_change_is_not_promoted_to_prediction(self) -> None:
        self.assertIn("new theory input", self.result["theory_change_boundary"])
        self.assertGreaterEqual(len(self.result["minimal_missing_physics"]), 4)
        self.assertGreaterEqual(len(self.result["evidence_partition"]["blocked"]), 4)
        self.assertIn("strongly coupled", self.result["candidate_extension_warning"])


if __name__ == "__main__":
    unittest.main()
