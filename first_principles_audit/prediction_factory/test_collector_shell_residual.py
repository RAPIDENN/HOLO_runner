#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import derive_collector_shell_residual as residual
except ModuleNotFoundError:
    import derive_collector_shell_residual as residual


class CollectorShellResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = residual.build()

    def test_required_shell_cost_formula(self) -> None:
        s = np.asarray([0.01, 0.1, 0.5, 0.9])
        expected = (-np.log1p(-s) / s) ** 4
        np.testing.assert_allclose(residual.required_shell_cost(s), expected)

    def test_missing_shell_cost_is_positive(self) -> None:
        self.assertTrue(self.result["checks"]["interaction_shell_cost_positive"])
        self.assertGreater(
            self.result["diagnostics"]["minimum_missing_shell_cost"], 0.0
        )

    def test_deep_missing_interaction_is_quartic(self) -> None:
        asymptotics = self.result["asymptotics"]
        self.assertAlmostEqual(
            asymptotics["measured_deep_epsilon_power"], 1.0, delta=5.0e-4
        )
        self.assertAlmostEqual(
            asymptotics["measured_deep_Wint_quartic_coefficient"],
            0.5,
            delta=5.0e-4,
        )
        self.assertIn("conditional", asymptotics["normalization_dependency"])

    def test_decomposition_recovers_exposed_target(self) -> None:
        self.assertLess(
            self.result["diagnostics"]["maximum_target_F_relative_error"],
            3.0e-6,
        )

    def test_newtonian_limit_requires_saturation_barrier(self) -> None:
        self.assertTrue(
            self.result["checks"]["high_selector_cost_has_log_four_barrier"]
        )
        self.assertIn("divergent", self.result["asymptotics"]["newtonian_selector_limit"])

    def test_selector_is_saturation_transport_solution(self) -> None:
        transport = self.result["transport_equivalence"]
        self.assertEqual(transport["equation"], "ds/dt=1-s with s(0)=0")
        self.assertLess(transport["maximum_analytic_transport_residual"], 2.0e-16)
        self.assertIn("not evidence", transport["evidence_boundary"])

    def test_inverse_design_is_not_physical_completion(self) -> None:
        self.assertIn("inverse_design", self.result["classification"])
        self.assertFalse(self.result["physical_gates"]["physical_completion"])
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["checks"]["all"])


if __name__ == "__main__":
    unittest.main()
