#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_tricritical_constitutive_bridge as bridge,
)


class TricriticalConstitutiveBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = bridge.build()

    def test_tricritical_saddle_is_exact(self) -> None:
        y = np.logspace(-10.0, 2.0, 64)
        selector, density = bridge.dual_density(y)
        np.testing.assert_allclose(selector, np.sqrt(y), rtol=2.0e-15)
        np.testing.assert_allclose(
            density, (2.0 / 3.0) * y**1.5, rtol=3.0e-15
        )

    def test_mass_and_quartic_are_relevant_deformations(self) -> None:
        y = np.asarray([1.0e-8, 1.0e-6, 1.0e-4])
        massive, _ = bridge.dual_density(y, mass2=1.0e-6)
        self.assertEqual(massive[0], 0.0)
        self.assertEqual(massive[1], 0.0)
        self.assertGreater(massive[2], 0.0)
        self.assertAlmostEqual(
            self.result["relevant_deformation_tests"][
                "quartic_contaminated_deep_P_power"
            ],
            2.0,
            delta=2.0e-3,
        )

    def test_old_and_new_source_exponents_are_separated(self) -> None:
        comparison = self.result["old_vs_new"]
        self.assertEqual(
            comparison["previous_fixed_poles"]["source_mass_exponent"], 1.0
        )
        self.assertEqual(
            comparison["new_collective_coordinate"]
            ["source_mass_exponent_in_deep_spherical_limit"],
            0.5,
        )

    def test_local_auxiliary_limit_is_not_assumed(self) -> None:
        obstruction = self.result["locality_obstruction"]
        self.assertAlmostEqual(obstruction["measured_power_in_Y"], -0.5)
        self.assertIn("cannot be integrated out uniformly", obstruction["interpretation"])
        self.assertFalse(
            self.result["physical_gates"][
                "q_is_auxiliary_or_gradient_terms_are_controlled"
            ]
        )

    def test_current_bulk_does_not_yet_fix_tricritical_vertices(self) -> None:
        boundary = self.result["current_bulk_boundary"]
        self.assertTrue(boundary["positive_canonical_carrier"])
        self.assertFalse(boundary["higher_brane_jets_selected"])
        self.assertFalse(
            self.result["physical_gates"]
            ["q_squared_times_Y_vertex_derived_from_constraint_action"]
        )

    def test_algebra_passes_without_observational_tables(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["checks"]["all"])
        self.assertFalse(self.result["physical_gates"]["physical_completion"])


if __name__ == "__main__":
    unittest.main()
