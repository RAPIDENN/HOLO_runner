#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_collective_spectral_bridge as bridge,
)


class CollectiveSpectralBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = bridge.build()

    def test_constant_mass_density_recovers_target_power(self) -> None:
        y = np.logspace(-6.0, 6.0, 64)
        density = bridge.cutoff_continuum_density(y, 0.0, 1.0e30)
        np.testing.assert_allclose(
            density, (2.0 / 3.0) * y**1.5, rtol=2.0e-14
        )

    def test_finite_positive_poles_are_analytic_crossovers(self) -> None:
        test = self.result["current_seven_mode_test"]
        self.assertLess(test["within_0p05_log10_width_dex"], 0.25)
        self.assertGreater(
            test["coefficient_of_variation_vs_constant_density"], 0.5
        )
        self.assertIn("narrow crossover", test["conclusion"])

    def test_cutoffs_bound_the_three_halves_window(self) -> None:
        representation = self.result["exact_representation"]
        self.assertEqual(representation["below_ir_gap"], "P is proportional to Y^2")
        self.assertEqual(representation["above_uv_cutoff"], "P is proportional to Y")
        self.assertIn("eps^2", representation["scaling_window"])

    def test_positive_identity_is_not_a_gaussian_generation_claim(self) -> None:
        warning = self.result["generation_sign_and_locality"]
        self.assertIn("-1/2*J*K^-1*J", warning["tree_gaussian_elimination"])
        self.assertIn("ghost", warning["sign_warning"])
        self.assertIn("nonlocal fractional operator", warning["locality_warning"])
        self.assertFalse(
            self.result["physical_gates"]
            ["positive_local_stieltjes_kernel_generated_by_healthy_tree_exchange"]
        )

    def test_old_and_new_are_explicitly_separated(self) -> None:
        comparison = self.result["old_vs_new"]
        self.assertIn("seven fixed gapped poles", comparison["old"])
        self.assertIn("tricritical", comparison["new_requirement"])

    def test_certificate_passes_without_observational_tables(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["checks"]["all"])
        self.assertFalse(self.result["physical_gates"]["physical_completion"])


if __name__ == "__main__":
    unittest.main()
