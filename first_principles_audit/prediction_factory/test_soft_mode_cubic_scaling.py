#!/usr/bin/env python3

from __future__ import annotations

import unittest

try:
    from first_principles_audit.prediction_factory import derive_soft_mode_cubic_scaling as scaling
except ModuleNotFoundError:
    import derive_soft_mode_cubic_scaling as scaling


class SoftModeCubicScalingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = scaling.build()

    def test_endpoint_third_derivatives_converge(self) -> None:
        jets = self.result["endpoint_jets"]
        self.assertLess(jets["half_grid_maximum_relative_error"], 0.002)
        self.assertLess(jets["quarter_grid_maximum_relative_error"], 0.004)
        self.assertIn("Subsampling stability", jets["systematic_warning"])

    def test_endpoint_profiles_scale_as_soft_mass(self) -> None:
        law = self.result["scaling_law"]
        self.assertAlmostEqual(law["Psi_uv_power_in_mu0"], 1.0, delta=0.005)
        self.assertAlmostEqual(law["Psi_ir_power_in_mu0"], 1.0, delta=0.005)
        self.assertAlmostEqual(law["mean_Psi_ir_over_mu0"], 28.264, delta=0.002)
        self.assertGreater(
            law["smallest_gamma_ir_boundary_norm_contribution"], 0.99
        )

    def test_brane_proxy_has_cubic_scaling(self) -> None:
        law = self.result["scaling_law"]
        self.assertAlmostEqual(law["brane_proxy_power_in_mu0"], 3.0, delta=0.005)
        self.assertAlmostEqual(
            law["mean_brane_proxy_over_mu0_cubed"], -42.835, delta=0.003
        )

    def test_minimal_brane_quartic_proxy_is_positive_but_underidentified(self) -> None:
        law = self.result["scaling_law"]
        self.assertAlmostEqual(
            law["brane_quartic_proxy_power_in_mu0"], 4.0, delta=0.005
        )
        self.assertGreater(law["mean_brane_quartic_proxy_over_mu0_fourth"], 0.0)
        self.assertIn("shifts it arbitrarily", self.result["quartic_boundary"])

    def test_proxy_is_not_mislabelled_as_physical_vertex(self) -> None:
        self.assertIn("not_the_physical_cubic_vertex", self.result["classification"])
        self.assertIn("scaling diagnostic only", self.result["proxy_definition"])
        gates = self.result["physical_gates"]
        self.assertFalse(gates["bulk_cubic_vertex_derived"])
        self.assertFalse(
            gates["higher_brane_jets_selected_by_microscopic_boundary_theory"]
        )
        self.assertFalse(gates["W_third_derivative_robust_to_background_smoothing"])
        self.assertFalse(gates["brane_bending_cubic_vertex_derived"])
        self.assertFalse(gates["canonical_physical_g000_derived"])
        self.assertFalse(gates["physical_completion"])

    def test_blind_scaling_certificate_passes(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["scaling_checks"]["all"])


if __name__ == "__main__":
    unittest.main()
