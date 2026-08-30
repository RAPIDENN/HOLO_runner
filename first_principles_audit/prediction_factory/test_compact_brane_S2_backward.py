#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_compact_brane_S2_backward as brane,
)


class CompactBraneS2BackwardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = brane.build()

    def test_background_scalar_and_Israel_junctions_are_recovered(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        self.assertLess(
            self.result["covariant_boundary_action"][
                "background_junction_max_abs"
            ],
            1.0e-12,
        )

    def test_all_seven_transformed_modes_satisfy_endpoint_problem(self) -> None:
        verification = self.result["verification"]
        self.assertEqual(len(verification["mode_rows"]), 7)
        self.assertLess(verification["maximum_weak_residual"], 1.0e-12)
        self.assertLess(
            verification["maximum_partner_rayleigh_mass_relative"], 1.0e-4
        )
        self.assertLess(
            verification["maximum_independent_Boos_LS_mass_relative"], 1.0e-4
        )

    def test_stiff_pins_bending_but_finite_gamma_does_not(self) -> None:
        gates = self.result["physical_gates"]
        self.assertTrue(gates["stiff_linear_bending_pinned_in_unitary_gauge"])
        self.assertTrue(gates["stiff_Darboux_endpoint_operator_recovered"])
        self.assertFalse(gates["finite_gamma_ADM_S2_with_bending_recovered"])
        self.assertFalse(gates["physical_finite_gamma_S3_endpoint_ready"])
        self.assertIn(
            "cannot be used", self.result["stiff_bending_reduction"]["finite_gamma_warning"]
        )

    def test_partner_form_is_not_misreported_as_positivity_proof(self) -> None:
        endpoint = self.result["Darboux_endpoint_derivation"][
            "endpoint_mass_coefficients"
        ]
        self.assertLess(endpoint["lower_numeric"], 0.0)
        self.assertGreater(endpoint["upper_numeric"], 0.0)
        self.assertIn("not by itself", endpoint["warning"])

    def test_no_observational_or_cubic_claim(self) -> None:
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])
        self.assertIn("does not derive", self.result["evidence_boundary"])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if brane.OUTPUT.exists():
            rendered = json.loads(brane.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
