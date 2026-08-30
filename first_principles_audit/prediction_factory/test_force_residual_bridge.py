#!/usr/bin/env python3
"""Regression tests for the origin-to-destination force differential."""

from __future__ import annotations

import json
import unittest

import numpy as np

from first_principles_audit.prediction_factory.derive_force_residual_bridge import (
    OUTPUT,
    build,
    point_yukawa_boost_and_log_radius_derivative,
    rar_nu,
)


class ForceResidualBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_certificate_passes_but_is_not_promoted(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertEqual(
            self.result["classification"], "empirical_inverse_diagnostic_not_prediction"
        )
        self.assertIn("by construction", self.result["evidence_boundary"])

    def test_origin_destination_and_crossing(self) -> None:
        parameters = self.result["parameters"]
        self.assertAlmostEqual(parameters["sum_alpha_stiff"], 0.10676508, places=7)
        crossing = parameters["zero_differential_crossing_gbar_m_s2"]
        self.assertGreater(crossing, 1.0e-10)
        self.assertLess(crossing, 1.0e-8)
        anchors = self.result["anchors"]
        self.assertGreater(anchors[0]["missing_multiplier"], 0.0)
        self.assertLess(anchors[-1]["missing_multiplier"], 0.0)

    def test_rar_multiplier_and_yukawa_derivative(self) -> None:
        nu = rar_nu(np.asarray([1.0e-12, 1.0e-10]), 1.2e-10)
        self.assertGreater(nu[0], nu[1])
        boost, derivative = point_yukawa_boost_and_log_radius_derivative(
            np.asarray([0.0, 0.1, 1.0]),
            np.asarray([0.3, 1.2]),
            np.asarray([0.02, 0.03]),
        )
        self.assertAlmostEqual(boost[0], 0.05, places=14)
        self.assertTrue(np.all(np.diff(boost) < 0.0))
        self.assertTrue(np.all(derivative <= 0.0))

    def test_diagnosis_requires_shape_not_constant_amplitude(self) -> None:
        diagnosis = self.result["diagnosis"]
        self.assertFalse(diagnosis["amplitude_only_sufficient"])
        self.assertFalse(diagnosis["fixed_linear_point_yukawa_scale_only_sufficient"])
        self.assertIn("environment", diagnosis["what_a_complete_theory_must_generate"])

    def test_rendered_artifact_matches_when_present(self) -> None:
        if OUTPUT.exists():
            self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
