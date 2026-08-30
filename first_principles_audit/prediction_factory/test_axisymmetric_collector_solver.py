#!/usr/bin/env python3

from __future__ import annotations

import inspect
import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import (
        derive_axisymmetric_collector_solver as solver,
    )
except ModuleNotFoundError:
    import derive_axisymmetric_collector_solver as solver


class AxisymmetricCollectorSolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = solver.build()

    def test_uniform_sheet_control(self) -> None:
        control = self.result["analytic_control"]
        self.assertTrue(control["converged"])
        self.assertLess(control["final_relative_residual"], 5.0e-7)
        self.assertLess(control["maximum_relative_potential_error"], 2.0e-5)

    def test_gas_hankel_reconstruction_is_positive_and_mass_constrained(self) -> None:
        for galaxy in self.result["galaxies"].values():
            gas = galaxy["source"]["gas_reconstruction"]
            self.assertGreater(gas["target_gas_mass_msun"], 0.0)
            self.assertAlmostEqual(
                gas["reconstructed_gas_mass_msun"]
                / gas["target_gas_mass_msun"],
                1.0,
                places=12,
            )
            self.assertGreater(gas["hi_radius_kpc"], 0.0)
            self.assertGreaterEqual(gas["raw_negative_sample_fraction"], 0.0)

    def test_bulge_and_bulgeless_routes_are_both_exercised(self) -> None:
        self.assertEqual(
            self.result["galaxies"]["DDO154"]["source"][
                "bulge_asymptotic_curve_mass_msun"
            ],
            0.0,
        )
        self.assertGreater(
            self.result["galaxies"]["NGC2841"]["source"][
                "bulge_asymptotic_curve_mass_msun"
            ],
            0.0,
        )

    def test_all_galaxy_solves_reach_nonlinear_residual_gate(self) -> None:
        for galaxy in self.result["galaxies"].values():
            self.assertTrue(galaxy["solver"]["converged"])
            self.assertLess(galaxy["solver"]["final_relative_residual"], 5.0e-5)
            self.assertGreater(galaxy["solver"]["minimum_mu"], 0.0)

    def test_resolution_sentinel(self) -> None:
        sentinel = self.result["resolution_sentinel"]
        self.assertEqual(sentinel["galaxy"], "DDO154")
        self.assertLess(sentinel["rms_velocity_difference_over_fine_rms"], 0.15)

    def test_newtonian_source_gate_is_quantitative_and_fail_closed(self) -> None:
        gate = self.result["newtonian_source_gate"]
        self.assertEqual(
            gate["prospective_threshold_relative_rms_v2_over_component_peak"],
            0.15,
        )
        self.assertEqual(set(gate["eligible_galaxies"]), {"NGC2403", "NGC3198"})
        self.assertEqual(set(gate["failed_galaxies"]), {"DDO154", "NGC2841"})
        for name in gate["failed_galaxies"]:
            self.assertEqual(
                self.result["galaxies"][name]["score_after_prediction_only"][
                    "interpretation"
                ],
                "exploratory_only_source_closure_gate_failed",
            )

    def test_vobs_is_not_an_operator_or_stopping_input(self) -> None:
        names = " ".join(
            list(inspect.signature(solver.solve_aqual).parameters)
            + list(inspect.signature(solver.predict_rotation_curve).parameters)
        ).lower()
        self.assertNotIn("vobs", names)
        self.assertNotIn("observed", names)
        self.assertNotIn("uncertainty", names)
        self.assertIn("observed", inspect.signature(solver.score_prediction).parameters)
        source_fields = solver.load_source_rotation_table("NGC2403")
        self.assertNotIn("Vobs_kms", source_fields)
        self.assertNotIn("eVobs_kms", source_fields)

    def test_global_a0_genealogy_blocks_a_blind_claim(self) -> None:
        parameters = self.result["global_frozen_parameters"]
        self.assertTrue(parameters["operator_uses_vobs_derived_global_a0"])
        self.assertFalse(parameters["direct_per_galaxy_vobs_read_during_solve"])
        self.assertFalse(
            self.result["passes"]["operator_is_independent_of_vobs_genealogy"]
        )

    def test_predictions_and_scores_are_finite(self) -> None:
        for galaxy in self.result["galaxies"].values():
            prediction = np.asarray(galaxy["prediction_kms"])
            self.assertTrue(np.all(np.isfinite(prediction)))
            self.assertTrue(np.all(prediction >= 0.0))
            self.assertTrue(
                np.isfinite(galaxy["score_after_prediction_only"]["chi2_per_point"])
            )

    def test_resource_and_claim_boundaries(self) -> None:
        resource = self.result["resource_bound"]
        self.assertFalse(resource["three_dimensional_mesh_allocated"])
        self.assertLess(resource["conservative_dense_array_mib"], 8.0)
        self.assertEqual(
            self.result["global_frozen_parameters"]["per_galaxy_force_parameters"],
            0,
        )
        self.assertIn("modelling assumptions", self.result["claim_boundary"])
        self.assertFalse(self.result["passes"]["all"])
        self.assertTrue(self.result["audit_checks"]["all"])


if __name__ == "__main__":
    unittest.main()
