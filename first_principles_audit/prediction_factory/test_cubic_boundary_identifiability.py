#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_cubic_boundary_identifiability as boundary,
)


class CubicBoundaryIdentifiabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = boundary.build()

    def test_stationary_normal_form_series(self) -> None:
        row = boundary.response_coefficients(2.0, 3.0, 5.0)
        self.assertAlmostEqual(row["a1"], -0.5)
        self.assertAlmostEqual(row["a2"], -3.0 / 16.0)
        self.assertAlmostEqual(row["C3"], -3.0 / 48.0)
        self.assertTrue(self.result["checks"]["all"])

    def test_cubic_jet_is_invisible_to_background_and_S2(self) -> None:
        counterexample = self.result["jet_counterexample"]
        self.assertEqual(
            counterexample["identical_at_background"],
            ["lambda", "lambda'", "lambda''"],
        )
        self.assertIn("cannot determine", counterexample["consequence"])

    def test_natural_and_nonuniform_stiff_paths_are_distinguished(self) -> None:
        paths = self.result["stiff_limit_paths"]
        natural = paths["natural_fixed_higher_jets"]
        self.assertAlmostEqual(natural["cubic_log_slope"], -3.0, places=12)
        self.assertAlmostEqual(
            natural["pure_zeta_quartic_log_slope"], -4.0, places=12
        )
        nonuniform = paths["nonuniform_eta_proportional_gamma_cubed"]
        c3 = [row["C3"] for row in nonuniform["rows"]]
        self.assertLess(max(c3) - min(c3), 1.0e-14)
        self.assertIn("does not define", nonuniform["result"])

    def test_physical_boundary_vertex_remains_fail_closed(self) -> None:
        gates = self.result["physical_gates"]
        self.assertTrue(gates["boundary_jet_nonidentifiability_proved"])
        self.assertTrue(gates["fixed_brane_scalar_junction_source_derived"])
        self.assertFalse(gates["metric_junction_through_second_order_derived"])
        self.assertFalse(gates["moving_brane_pullback_and_normal_completed"])
        self.assertFalse(gates["full_second_order_junction_source_derived"])
        self.assertFalse(gates["physical_compact_S3_boundary_vertex_computed"])
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])

    def test_fixed_brane_scalar_junction_is_expanded_exactly(self) -> None:
        junction = self.result["fixed_brane_scalar_junction"]
        self.assertIn("N^-1", junction["exact"])
        self.assertIn("lambda_i'''*q1^2/2", junction["second_order"])
        self.assertLess(junction["series_check_max_abs"], 1.0e-12)
        scaling = self.result["stiff_limit_paths"]["junction_scaling"]
        self.assertIn("eta/gamma^3", scaling["cubic_boundary_action"])
        self.assertIn("eta^2/gamma^5", scaling["quartic_eta_squared_response"])

    def test_fixed_brane_action_is_expanded_through_quartic_order(self) -> None:
        action = self.result["boundary_action_convention"]
        self.assertIn("lambda_i/2", action["israel_junction"])
        density = self.result["fixed_brane_boundary_density"]
        self.assertIn("P3", density["GHY_S3"])
        self.assertIn("zeta4*Q^4", density["brane_potential_S4"])
        self.assertLess(max(density["series_check"].values()), 1.0e-12)
        gates = self.result["physical_gates"]
        self.assertTrue(
            gates[
                "formal_fixed_brane_GHY_prefactor_and_potential_jet_convolution_verified"
            ]
        )
        self.assertIn("Formal", density["status"])
        self.assertFalse(gates["full_second_order_junction_source_derived"])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if boundary.OUTPUT.exists():
            rendered = json.loads(boundary.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
