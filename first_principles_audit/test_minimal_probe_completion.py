from __future__ import annotations

import unittest

from first_principles_audit.derive_minimal_probe_completion import derive


class MinimalProbeCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_no_observational_or_historical_fit_inputs(self) -> None:
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertEqual(self.result["historical_fitted_couplings_reused"], [])
        self.assertTrue(self.result["passes"]["observational_blinding"])

    def test_mode_problem_is_numerically_certified(self) -> None:
        passes = self.result["passes"]
        for name in (
            "positive_carrier",
            "mode_orthonormality",
            "positive_mode_residuals",
            "unique_numerical_zero_mode",
            "zero_mode_stiffness_residual",
            "half_grid_convergence",
            "quarter_grid_convergence",
            "half_grid_uv_coupling_convergence",
            "quarter_grid_uv_coupling_convergence",
        ):
            self.assertTrue(passes[name], name)

    def test_zero_mode_coupling_is_derived_not_fitted(self) -> None:
        zero = self.result["zero_mode_prediction"]
        integrals = self.result["integrals"]
        expected = (integrals["I_g"] / (3.0 * integrals["I_w"])) ** 0.5
        self.assertAlmostEqual(zero["beta_0"], expected, places=14)
        self.assertAlmostEqual(
            zero["relative_force_strength_2_beta_squared"],
            2.0 * expected * expected,
            places=14,
        )
        self.assertTrue(self.result["passes"]["zero_mode_normalized"])
        self.assertTrue(self.result["passes"]["zero_mode_coupling_identity"])

    def test_physical_scale_remains_explicitly_unfixed(self) -> None:
        spectrum = self.result["dimensionless_spectrum"]
        self.assertIn("ell is not fixed", spectrum["physical_scale_rule"])
        self.assertEqual(spectrum["masses_mu"][0], 0.0)
        self.assertGreater(spectrum["masses_mu"][1], 0.0)

    def test_tree_level_channel_separation(self) -> None:
        channels = self.result["tree_level_channels"]
        self.assertEqual(channels["massive_matter_trace"], "coupled")
        self.assertIn("T_EM=0", channels["classical_4d_photon"])
        self.assertIn("no leading signal", channels["universal_clock_ratio"])
        self.assertIn("not derived", channels["anomaly_or_nonuniversal_channels"])

    def test_completion_assumptions_are_not_hidden(self) -> None:
        assumptions = " ".join(self.result["assumptions"])
        for required in (
            "physical compact interval",
            "GHY",
            "Neumann-Neumann",
            "localized",
            "no brane bending",
            "induced-metric coupling",
        ):
            self.assertIn(required, assumptions)

    def test_complete_certificate_passes(self) -> None:
        self.assertTrue(self.result["passes"]["all"])


if __name__ == "__main__":
    unittest.main()
