#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import derive_phase_space_collector_bridge as bridge
except ModuleNotFoundError:
    import derive_phase_space_collector_bridge as bridge


class PhaseSpaceCollectorBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = bridge.build()

    def test_numeric_legendre_selector(self) -> None:
        X = np.asarray([0.01, 0.04, 0.09])
        states = np.linspace(0.001, 0.5, 10000)
        F, selector = bridge.legendre_phase_space(X, states, 3)
        np.testing.assert_allclose(F, (2.0 / 3.0) * X**1.5, rtol=2.0e-7)
        np.testing.assert_allclose(selector, np.sqrt(X), rtol=2.0e-4)

    def test_three_dimensions_is_the_required_scaling(self) -> None:
        d3 = next(
            row for row in self.result["dimension_matrix"] if row["dimension"] == 3
        )
        self.assertEqual(d3["primal_power_in_X"], 1.5)
        self.assertEqual(d3["spherical_mass_power"], 0.5)
        self.assertEqual(d3["spherical_radius_power"], -1.0)
        self.assertEqual(d3["primal_coefficient"], 2.0 / 3.0)

    def test_other_dimensions_do_not_give_both_targets(self) -> None:
        for row in self.result["dimension_matrix"]:
            if row["dimension"] == 3:
                continue
            self.assertFalse(
                row["spherical_mass_power"] == 0.5
                and row["spherical_radius_power"] == -1.0
            )

    def test_positive_occupation_is_not_vacuum_determinant(self) -> None:
        self.assertTrue(
            self.result["algebra_checks"][
                "kept_distinct_from_wrong_sign_vacuum_determinant"
            ]
        )
        self.assertIn("positive", self.result["generated_idea"]["sign_advantage"])

    def test_gapped_dispersion_generates_positive_deep_coefficients(self) -> None:
        check = self.result["gapped_dispersion_check"]
        self.assertAlmostEqual(check["deep_W_log_slope_vs_s"], 3.0, delta=2.0e-5)
        self.assertAlmostEqual(
            check["deep_W_cubic_coefficient"], 1.0 / 3.0, places=9
        )
        self.assertAlmostEqual(check["deep_F_log_slope_vs_X"], 1.5, delta=2.0e-5)
        self.assertAlmostEqual(
            check["deep_F_three_halves_coefficient"], 2.0 / 3.0, places=9
        )
        self.assertAlmostEqual(
            check["high_X_F_log_slope"], 4.0 / 3.0, delta=2.0e-4
        )

    def test_physical_hypotheses_remain_open(self) -> None:
        gates = self.result["physical_gates"]
        self.assertFalse(gates["positive_local_occupation_derived"])
        self.assertFalse(gates["stationary_flat_occupation_distribution_derived"])
        self.assertFalse(gates["local_s_times_X_coupling_derived"])
        self.assertFalse(gates["a0_and_normalization_derived"])
        self.assertFalse(gates["newtonian_high_acceleration_completion_derived"])
        self.assertFalse(gates["physical_completion"])

    def test_certificate_is_blind_and_passes(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["algebra_checks"]["all"])


if __name__ == "__main__":
    unittest.main()
