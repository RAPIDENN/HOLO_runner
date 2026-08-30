#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_gauge_invariant_cubic_route as route,
)


class GaugeInvariantCubicRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = route.build()

    def test_bmp_operator_is_the_certified_S2_operator(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        match = self.result["quadratic_operator_match"]
        self.assertEqual(match["samples"], 1979)
        self.assertEqual(match["exact_weight_relations"]["rho_BMP"], "(2/3)*p")
        metrics = match["metrics"]
        self.assertLess(
            metrics["stiffness_weight_factorization_max_relative"], 1.0e-12
        )
        self.assertLess(
            metrics["mass_weight_factorization_max_relative"], 1.0e-12
        )
        self.assertLess(metrics["rayleigh_spectrum_max_relative"], 1.0e-10)

    def test_convention_map_reproduces_repository_background(self) -> None:
        mapping = self.result["convention_map"]
        self.assertEqual(mapping["field"], "phi_BMP=chi/2")
        self.assertEqual(mapping["superpotential"], "W_BMP=W_H/4")
        self.assertIn("A'=-W_H/6", mapping["repository_background"])

    def test_linear_external_profiles_are_identified_without_mixing_branches(self) -> None:
        mapping = self.result["linear_mode_map"]
        self.assertIn("tilde_a=h_BMP/4", mapping["comoving_gauge"])
        self.assertIn("H_BMP=0", mapping["normalization_distinction"])
        self.assertIn("tilde_a=3*h_R/16", mapping["normalization_distinction"])
        self.assertIn("not the microscopic", mapping["consequence"])
        stiff = mapping["stiff_branch"]
        self.assertIn("exp(-2A)", stiff["map"])
        self.assertIn("not inserted raw", stiff["consequence"])
        self.assertLess(
            stiff["strong_equation_check"]["maximum_rms_relative"], 5.0e-4
        )
        self.assertLess(
            stiff["strong_equation_check"]["maximum_peak_relative"], 2.5e-3
        )

    def test_primary_S3_kernel_does_not_hide_boundary_or_S4_gaps(self) -> None:
        calculation = self.result["cubic_calculation"]
        self.assertIn("Eq. (5.19)", calculation["available_bulk_result"])
        self.assertIn("finite Neumann endpoints", calculation["why_it_is_not_yet_a_physical_compact_coupling"])
        self.assertIn("direct_S4", calculation["direct_S4_requirement"])
        gates = self.result["physical_gates"]
        self.assertTrue(gates["bmp_linear_comoving_identity_identified"])
        self.assertFalse(
            gates["repository_trace_to_bmp_absolute_normalization_identified"]
        )
        self.assertTrue(gates["bmp_holographic_three_point_kernel_identified"])
        self.assertFalse(gates["compact_bulk_S3_action_derived"])
        self.assertFalse(gates["compact_endpoint_terms_derived"])
        self.assertFalse(gates["direct_S4_contact_derived"])
        self.assertFalse(gates["physical_S3_complete"])
        self.assertTrue(gates["linear_stiff_to_gauge_invariant_mode_map_identified"])
        self.assertIn("cubic deformation", calculation["boundary_identifiability"])

    def test_i5_is_an_executor_not_a_missing_derivation(self) -> None:
        contract = self.result["silicon_execution_contract"]
        self.assertIn("not launch", contract["launch_gate"])
        self.assertIn("Neither i5 geometry", contract["not_a_derivation"])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if route.OUTPUT.exists():
            rendered = json.loads(route.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
