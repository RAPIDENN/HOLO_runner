#!/usr/bin/env python3

from __future__ import annotations

import math
import unittest

try:
    from first_principles_audit.prediction_factory import derive_soft_mode_cubic_bridge as bridge
except ModuleNotFoundError:
    import derive_soft_mode_cubic_bridge as bridge


class SoftModeCubicBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = bridge.build()

    def test_soft_mode_is_critical(self) -> None:
        fit = self.result["soft_mode_fit"]
        self.assertAlmostEqual(
            fit["log_slope_mu0_squared_vs_gamma"], 1.0, delta=0.01
        )
        self.assertLess(fit["coefficient_of_variation"], 0.005)

    def test_subtracted_3d_determinant_has_cubic_nonanalyticity(self) -> None:
        det = self.result["three_dimensional_determinant"]
        self.assertAlmostEqual(det["log_slope_absolute_value_vs_mu0"], 3.0, places=10)
        self.assertAlmostEqual(
            det["numerical_coefficient_of_m_cubed"],
            -1.0 / (12.0 * math.pi),
            places=9,
        )

    def test_exponent_matches_collector_dual(self) -> None:
        self.assertTrue(
            self.result["certificate_checks"][
                "critical_and_collector_exponents_match"
            ]
        )

    def test_endpoint_coupling_proxies_soften_too(self) -> None:
        proxy = self.result["coupling_proxy_softening"]
        self.assertAlmostEqual(proxy["ir_log_slope_vs_gamma"], 1.0, delta=0.01)
        self.assertAlmostEqual(proxy["uv_log_slope_vs_gamma"], 1.0, delta=0.01)
        self.assertIn("not absolute matter residues", proxy["warning"])

    def test_wrong_sign_and_missing_scales_remain_explicit(self) -> None:
        gates = self.result["physical_gates"]
        self.assertFalse(
            gates["required_positive_W_sign_generated_by_bosonic_determinant"]
        )
        self.assertFalse(gates["analytic_linear_X_term_absent_or_cancelled"])
        self.assertFalse(gates["nonvanishing_physical_matter_residue_derived"])
        self.assertFalse(gates["normalization_derived"])
        self.assertFalse(gates["a0_derived"])
        self.assertFalse(gates["physical_completion"])

    def test_certificate_is_blind_and_passes(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["certificate_checks"]["all"])


if __name__ == "__main__":
    unittest.main()
