#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

from first_principles_audit.prediction_factory import derive_jordan_deep_limit_gate as gate


class JordanDeepLimitGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    def test_exact_target_frame_map(self) -> None:
        t = np.asarray([1.0e-8, 1.0e-5, 0.1])
        beta = 0.13
        frame = gate.target_frame_path(t, beta)
        np.testing.assert_allclose(frame["s"], -np.expm1(-t))
        np.testing.assert_allclose(frame["A_m"] ** 2 * frame["s"], 1.0)
        np.testing.assert_allclose(frame["x"], t**2 / frame["s"])

    def test_direct_jordan_tensor_coefficient_vanishes(self) -> None:
        path = self.result["exact_path"]
        self.assertEqual(path["jordan_tensor_coefficient"], "M_J^2/M_Pl^2=s")
        diagnostics = self.result["diagnostics"]
        self.assertAlmostEqual(diagnostics["selector_power_in_t"], 1.0, places=4)
        self.assertAlmostEqual(diagnostics["conformal_power_in_t"], -0.5, places=4)

    def test_early_linearization_failure_is_mass_analyticity(self) -> None:
        failure = self.result["failure_of_early_linearization"]
        self.assertIn("linear in M", failure["consequence"])
        self.assertIn("sqrt(M)", failure["consequence"])
        self.assertIn("degenerate s=0 endpoint", failure["why_the_target_disappeared"])

    def test_derivative_constitutive_route_remains_open(self) -> None:
        implication = self.result["architecture_implication"]
        self.assertIn("nondegenerate Einstein-Hilbert", implication["surviving_route"])
        self.assertIn("gradient invariant", implication["surviving_route"])
        self.assertFalse(
            self.result["physical_gates"][
                "direct_s_as_full_planck_coefficient_completion"
            ]
        )

    def test_asymptotic_certificate_passes_without_observations(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["checks"]["all"])


if __name__ == "__main__":
    unittest.main()
