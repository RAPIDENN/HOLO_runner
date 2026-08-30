#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import derive_nonlinear_collector_action as action
except ModuleNotFoundError:
    import derive_nonlinear_collector_action as action


class NonlinearCollectorActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = action.build()

    def test_spherical_map_recovers_collector(self) -> None:
        y = np.geomspace(1.0e-10, 1.0e10, 1000)
        nu = action.nu_of_y(y)
        x = y * nu
        mu = 1.0 / nu
        np.testing.assert_allclose(mu * x, y, rtol=2.0e-15, atol=0.0)

        checks = self.result["numerical_consistency_checks"]
        self.assertLess(
            checks["constitutive_inversion_closure_max_relative_error"], 2.0e-8
        )
        self.assertLess(
            checks["constitutive_inversion_target_x_max_relative_error"], 2.0e-6
        )

    def test_action_is_single_valued_and_elliptic(self) -> None:
        diagnostics = self.result["action_reconstruction"]["diagnostics"]
        self.assertGreater(diagnostics["minimum_dx_dt"], 0.0)
        self.assertGreater(diagnostics["minimum_mu"], 0.0)
        self.assertGreater(
            diagnostics["minimum_longitudinal_elliptic_eigenvalue"], 0.0
        )
        self.assertTrue(diagnostics["degenerately_elliptic_as_x_tends_to_zero"])
        self.assertFalse(diagnostics["uniformly_elliptic_on_x_greater_than_zero"])
        self.assertLess(diagnostics["maximum_F_prime_relative_error"], 2.0e-4)

    def test_spherical_plummer_pde_residual(self) -> None:
        pde = self.result["numerical_consistency_checks"]["spherical_plummer_pde"]
        self.assertLess(pde["maximum_flux_relative_error"], 2.0e-8)
        self.assertLess(
            pde["maximum_finite_difference_pde_relative_residual"], 2.0e-4
        )

    def test_deep_and_newtonian_limits(self) -> None:
        diagnostics = self.result["action_reconstruction"]["diagnostics"]
        self.assertAlmostEqual(
            diagnostics["deep_limit_dlog_mu_dlog_x"], 1.0, delta=2.0e-3
        )
        self.assertAlmostEqual(
            diagnostics["deep_limit_dlog_F_dlog_X"], 1.5, delta=2.0e-3
        )
        self.assertAlmostEqual(
            diagnostics["newtonian_limit_dlog_F_dlog_X"], 1.0, delta=2.0e-3
        )

    def test_six_hundred_is_mass_dependent_not_universal(self) -> None:
        scales = self.result["scale_map"]["mass_implied_by_candidate_radius"]
        m_small = scales["0.6_kpc"]["source_mass_for_gN_equal_a0_msun"]
        m_large = scales["600_kpc"]["source_mass_for_gN_equal_a0_msun"]
        self.assertAlmostEqual(m_large / m_small, 1.0e6, places=8)
        self.assertGreater(m_small, 1.0e8)
        self.assertLess(m_small, 1.0e9)
        self.assertGreater(m_large, 1.0e14)

    def test_high_acceleration_limits_are_formally_screened(self) -> None:
        limits = self.result["scale_map"][
            "formal_isolated_high_acceleration_limits"
        ]
        self.assertLess(limits["Earth_surface"]["log10_nu_minus_one"], -1.0e5)
        self.assertLess(limits["Sun_at_1_AU"]["log10_nu_minus_one"], -1000.0)
        self.assertIn("formal isolated-field limits", self.result["scale_map"]["interpretation"])

    def test_claim_remains_outside_current_holo_derivation(self) -> None:
        self.assertIn(
            "not_derived_from_current_holo_bulk", self.result["classification"]
        )
        self.assertEqual(self.result["source"]["per_galaxy_parameters"], 0)
        self.assertTrue(self.result["passes"]["all"])
        self.assertNotIn("well-posed", self.result["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
