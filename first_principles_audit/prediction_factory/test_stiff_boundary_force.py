#!/usr/bin/env python3
"""Regression tests for the canonically normalized stiff scalar force."""

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory.derive_stiff_boundary_force import (
    OUTPUT,
    build,
)


class StiffBoundaryForceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_blind_certificate_and_independent_residues(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertEqual(self.result["historical_trace_residues_reused"], [])
        self.assertIn("not_detection", self.result["classification"])

    def test_stiff_masses_and_force_residues(self) -> None:
        force = self.result["spectrum_and_force"]
        self.assertAlmostEqual(force["masses_mu"][0], 0.29048164, places=6)
        self.assertTrue(all(value > 0.0 for value in force["alpha_uv_2_beta_squared"]))
        self.assertAlmostEqual(force["sum_alpha_short_distance"], 0.10676508, places=7)
        self.assertAlmostEqual(
            force["maximum_baryonic_acceleration_multiplier"],
            1.0 + force["sum_alpha_short_distance"],
            places=14,
        )

    def test_operator_representations_and_meshes_agree(self) -> None:
        convergence = self.result["convergence"]
        self.assertLess(
            convergence["maximum_junction_representation_mass_relative"],
            1.0e-4,
        )
        self.assertLess(convergence["half_grid"]["maximum_mass_relative"], 1.5e-4)
        self.assertLess(convergence["quarter_grid"]["maximum_mass_relative"], 7.0e-4)
        self.assertLess(convergence["half_grid"]["maximum_beta_relative"], 1.0e-4)
        self.assertLess(convergence["quarter_grid"]["maximum_beta_relative"], 4.0e-4)

    def test_static_force_decays_with_distance(self) -> None:
        anchors = self.result["spectrum_and_force"]["anchor_response"]
        response = [row["scalar_acceleration_over_newton"] for row in anchors]
        self.assertTrue(all(right < left for left, right in zip(response, response[1:])))
        self.assertAlmostEqual(
            response[0],
            self.result["spectrum_and_force"]["sum_alpha_short_distance"],
            places=14,
        )

    def test_rendered_artifact_matches_when_present(self) -> None:
        if OUTPUT.exists():
            self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
