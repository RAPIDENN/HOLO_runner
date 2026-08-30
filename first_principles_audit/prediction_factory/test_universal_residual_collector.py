#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import derive_universal_residual_collector as collector
except ModuleNotFoundError:
    import derive_universal_residual_collector as collector


class UniversalResidualCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = collector.build()

    def test_multiplier_has_correct_limits_and_is_monotone(self) -> None:
        gdagger = 1.2e-10
        gbar = np.logspace(-15, -7, 200)
        nu = collector.collector_nu(gbar, gdagger)
        self.assertTrue(np.all(np.diff(nu) < 0.0))
        self.assertGreater(nu[0], 100.0)
        self.assertAlmostEqual(nu[-1], 1.0, places=10)

    def test_one_global_parameter_and_frozen_test(self) -> None:
        self.assertEqual(self.result["train_fit"]["per_galaxy_parameters"], 0)
        self.assertEqual(self.result["frozen_inputs"]["fit_split"], "train")
        self.assertEqual(
            self.result["frozen_inputs"]["evaluation_splits"],
            ["validation", "test"],
        )

    def test_rigid_positive_comb_is_mathematically_insufficient(self) -> None:
        inventory = self.result["acceleration_domain"]["all_catalogue"]
        ceiling = self.result["frozen_inputs"][
            "rigid_long_range_nu_ceiling"
        ]
        self.assertGreater(inventory["collector_nu_max"], ceiling)
        self.assertGreater(
            inventory["fraction_requiring_more_than_rigid_ceiling"], 0.5
        )
        self.assertGreater(
            inventory["fraction_requiring_screening_below_rigid_ceiling"],
            0.0,
        )

    def test_both_six_hundred_interpretations_fail_for_rigid_force(self) -> None:
        audit = self.result["six_hundred_disambiguation"]
        radius = audit["observed_radius_thresholds_test"][1]
        range_row = audit["global_yukawa_range_test"]["test"][1]
        self.assertEqual(radius["minimum_radius_kpc"], 0.6)
        self.assertEqual(range_row["ell_kpc"], 600.0)
        self.assertGreater(radius["stiff_long_range"]["chi2_per_point"], 100.0)
        self.assertGreater(range_row["chi2_per_point"], 100.0)

    def test_collector_is_better_but_not_promoted_to_action_prediction(self) -> None:
        metrics = self.result["metrics"]
        self.assertLess(
            metrics["collector"]["test"]["chi2_per_point"],
            metrics["stiff_long_range"]["test"]["chi2_per_point"],
        )
        self.assertIn("not_action_derivation", self.result["classification"])
        self.assertTrue(self.result["passes"]["all"])


if __name__ == "__main__":
    unittest.main()
