#!/usr/bin/env python3

from __future__ import annotations

import inspect
import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import (
        derive_axisymmetric_collector_prototype as prototype,
    )
except ModuleNotFoundError:
    import derive_axisymmetric_collector_prototype as prototype


class AxisymmetricCollectorPrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = prototype.build()

    def test_constitutive_inverse_closes(self) -> None:
        y = np.geomspace(1.0e-12, 1.0e12, 4096)
        nu = prototype.collector_nu(y)
        x = y * nu
        np.testing.assert_allclose(
            prototype.collector_mu(x) * x, y, rtol=8.0e-15, atol=0.0
        )

    def test_axisymmetric_finite_volume_control_converges(self) -> None:
        fv = self.result["analytic_and_numerical_controls"][
            "spherical_plummer_cylindrical_finite_volume"
        ]
        self.assertLess(fv["fine"]["weighted_relative_l2_residual"], 3.0e-3)
        self.assertGreater(fv["coarse_to_fine_l2_ratio"], 3.5)

    def test_razor_thin_jump_control(self) -> None:
        sheet = self.result["analytic_and_numerical_controls"][
            "razor_thin_sheet_jump"
        ]
        self.assertLess(sheet["maximum_relative_jump_error"], 2.0e-14)

    def test_flattened_algebraic_map_is_not_integrable(self) -> None:
        curl = self.result["analytic_and_numerical_controls"][
            "algebraic_field_integrability"
        ]
        self.assertLess(
            curl["spherical_plummer"]["normalized_weighted_rms_curl"], 1.0e-14
        )
        self.assertGreater(
            curl["flattened_miyamoto_nagai"]["normalized_weighted_rms_curl"],
            1.0e-3,
        )
        self.assertGreater(curl["flattened_to_spherical_rms_curl_ratio"], 1.0e12)

    def test_sparc_source_contract_fails_closed(self) -> None:
        audit = self.result["sparc_source_identifiability"]
        self.assertEqual(audit["tables"], 175)
        self.assertTrue(audit["uniform_header"])
        self.assertFalse(audit["physical_axisymmetric_pde_identifiable"])
        self.assertEqual(
            audit["status"], "FAIL_CLOSED_MISSING_UNIQUE_3D_BARYON_SOURCE"
        )
        self.assertIn("Vobs_kms", audit["scoring_only_columns"])

    def test_vobs_cannot_enter_the_operator(self) -> None:
        names = inspect.signature(prototype.predict_effective_midplane).parameters
        joined = " ".join(names).lower()
        self.assertNotIn("vobs", joined)
        self.assertNotIn("observed", joined)
        self.assertNotIn("uncertainty", joined)
        self.assertIn("observed_kms", inspect.signature(prototype.score_prediction).parameters)

    def test_frozen_effective_score_matches_existing_readout(self) -> None:
        score = self.result["effective_midplane_diagnostic"]["frozen_test_score"]
        self.assertEqual(score["galaxies"], 27)
        self.assertEqual(score["velocity_points"], 621)
        self.assertAlmostEqual(score["chi2_per_point"], 36.747991080566734, places=10)
        self.assertAlmostEqual(
            score["median_absolute_fractional_velocity_error"],
            0.144582962137798,
            places=12,
        )
        self.assertIn("not_axisymmetric_pde", score["classification"])

    def test_resource_bound_and_claim_boundary(self) -> None:
        bound = self.result["resource_bound"]
        self.assertFalse(bound["three_dimensional_mesh_allocated"])
        self.assertLess(bound["conservative_peak_array_mib"], 16.0)
        self.assertIn("not a valid flattened-disk", self.result["claim_boundary"])
        self.assertTrue(self.result["passes"]["all"])


if __name__ == "__main__":
    unittest.main()
