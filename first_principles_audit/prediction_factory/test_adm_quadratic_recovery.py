#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_adm_quadratic_recovery as recovery,
)


class ADMQuadraticRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = recovery.build()

    def test_same_variable_S2_is_recovered(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        gates = self.result["physical_gates"]
        self.assertTrue(
            gates["same_variable_bulk_ADM_S2_action_recovered_on_compact_support"]
        )
        self.assertTrue(gates["certified_Sturm_Liouville_operator_recovered"])
        self.assertFalse(gates["compact_master_ADM_S2_including_endpoints_recovered"])
        self.assertFalse(gates["same_variable_ADM_S2_master_action_recovered"])
        self.assertFalse(gates["linear_scalar_shift_constraint_independently_tested"])
        self.assertFalse(gates["physical_S3_projected"])

    def test_raw_ADM_action_matches_reduced_action_on_nine_probes(self) -> None:
        backward = self.result["verification"][
            "periodic_compact_support_backward_test"
        ]
        self.assertEqual(len(backward["rows"]), 9)
        self.assertLess(backward["maximum_relative_error"], 1.0e-9)
        self.assertLess(
            backward["maximum_shift_independence_relative"], 1.0e-12
        )

    def test_weights_and_BMP_field_convention_are_explicit(self) -> None:
        verification = self.result["verification"]
        self.assertLess(verification["p_weight_max_relative"], 1.0e-12)
        self.assertLess(verification["w_weight_max_relative"], 1.0e-12)
        bridge = self.result["BMP_convention_bridge"]
        self.assertEqual(bridge["field_map"], "zeta=(2/3)*tilde_a")
        self.assertIn("rho_BMP=(2/3)*p", bridge["weight_map"])

    def test_observations_and_nonlinear_claims_remain_out(self) -> None:
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])
        self.assertFalse(
            self.result["physical_gates"]["nonlinear_lapse_shift_constraints_solved"]
        )
        self.assertIn("derive S3", self.result["evidence_boundary"])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if recovery.OUTPUT.exists():
            rendered = json.loads(recovery.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
