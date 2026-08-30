#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import derive_finite_gamma_brane_S2 as brane


class FiniteGammaBraneS2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = brane.build()

    def test_three_finite_asymmetric_brane_pairs(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        rows = self.result["finite_gamma_verification"]["rows"]
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertGreater(row["gamma_minus"], 0.0)
            self.assertGreater(row["gamma_plus"], 0.0)
            self.assertNotEqual(row["gamma_minus"], row["gamma_plus"])
            self.assertEqual(len(row["Boos_masses_mu"]), 7)

    def test_representation_maps_match_spectra_and_modes(self) -> None:
        verification = self.result["finite_gamma_verification"]
        self.assertLess(
            verification["maximum_Boos_LS_mass_relative"], 2.0e-4
        )
        self.assertLess(
            verification["maximum_Boos_LS_one_minus_MAC"], 1.0e-6
        )
        identity = self.result["representation_maps"]["verification"]
        self.assertLess(
            identity["maximum_pointwise_total_derivative_identity_relative"],
            1.0e-12,
        )
        self.assertLess(
            identity["maximum_integrated_stiffness_relative"], 1.0e-6
        )

    def test_target_free_shooting_recovers_all_modes(self) -> None:
        shooting = self.result["finite_gamma_verification"][
            "independent_global_shooting"
        ]
        self.assertIn("no FEM target", shooting["method"])
        self.assertLess(shooting["maximum_Boos_FEM_mass_relative"], 2.0e-4)
        self.assertEqual(sum(len(row["shooting_masses_mu"]) for row in shooting["rows"]), 21)

    def test_dimensionless_norm_passes_but_absolute_interval_norm_is_open(self) -> None:
        gates = self.result["physical_gates"]
        self.assertTrue(
            gates["finite_gamma_translated_operator_crosscheck_complete"]
        )
        self.assertFalse(gates["finite_gamma_brane_S2_backward_complete"])
        self.assertFalse(
            gates["synthetic_bent_brane_fixture_used_as_physical_evidence"]
        )
        self.assertTrue(gates["finite_gamma_dimensionless_norm_identity_verified"])
        self.assertFalse(gates["single_interval_absolute_canonical_norm_recovered"])
        self.assertFalse(
            gates["raw_EH_GHY_normal_derivative_cancellation_rederived_in_repo"]
        )
        self.assertFalse(gates["local_same_variable_ADM_boundary_auxiliary_action_recovered"])
        self.assertFalse(gates["physical_finite_gamma_S3_endpoint_ready"])

    def test_rational_ADM_endpoint_is_not_constant_Robin(self) -> None:
        endpoint = self.result["finite_gamma_ADM_endpoint_law"]
        self.assertIn("1-s_i*m^2*H_i/gamma_i", endpoint["endpoint_law"])
        self.assertIn("wrong finite-gamma norm", endpoint["warning"])

    def test_no_observational_or_cubic_claim(self) -> None:
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])
        self.assertIn("does not yet", self.result["evidence_boundary"])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if brane.OUTPUT.exists():
            rendered = json.loads(brane.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
