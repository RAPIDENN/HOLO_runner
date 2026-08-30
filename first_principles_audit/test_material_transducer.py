from __future__ import annotations

import unittest

import numpy as np

from first_principles_audit.derive_material_transducer import (
    acceleration_ratio,
    derive,
    tidal_ratio,
)


class MaterialTransducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_certificate_is_blind_to_targets_and_materials(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertEqual(self.result["material_constants_read"], [])
        self.assertEqual(self.result["source_or_mode_amplitudes_read"], [])

    def test_correlated_positive_tower(self) -> None:
        fixed = self.result["geometry_fixed"]
        self.assertAlmostEqual(
            fixed["positive_mode_total_alpha_at_zero_range"],
            7.202299861734871e-05,
            places=16,
        )
        expected = np.asarray(
            [1.0, 1.686942, 2.334807, 2.985996, 3.651009, 4.327036]
        )
        np.testing.assert_allclose(
            fixed["positive_mode_mass_ratios_to_mu1"], expected, rtol=5e-7
        )

    def test_force_templates_at_zero_range_equal_alpha_sum(self) -> None:
        fixed = self.result["geometry_fixed"]
        masses = np.asarray(fixed["masses_mu"])
        alphas = np.asarray(fixed["yukawa_strengths_alpha_uv"])
        expected = float(np.sum(alphas))
        self.assertAlmostEqual(acceleration_ratio(0.0, masses, alphas)[0], expected)
        self.assertAlmostEqual(tidal_ratio(0.0, masses, alphas)[0], expected)

    def test_yukawa_gradient_is_independently_checked(self) -> None:
        validation = self.result["validation"]
        self.assertLess(
            validation["finite_difference_tidal_max_relative_error"], 1e-8
        )

    def test_ricci_ratio_cancels_ell(self) -> None:
        clock = self.result["ricci_clock_use"]
        self.assertEqual(
            clock["scale_free_ratio"],
            "omega_n/omega_R=mu_n/sqrt(abs(R5_hat))",
        )
        self.assertTrue(self.result["validation"]["ell_cancellation_in_omega_ratio"])

    def test_wilson_matching_does_not_identify_ell(self) -> None:
        matching = self.result["wilson_matching_if_future_loop_exists"]
        self.assertIn("ell/a", matching["required_bridge"])
        self.assertIn("matching choice", matching["warning"])


if __name__ == "__main__":
    unittest.main()
