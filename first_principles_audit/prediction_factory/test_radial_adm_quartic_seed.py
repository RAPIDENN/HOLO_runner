#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_radial_adm_quartic_seed as adm,
)


class RadialADMQuarticSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = adm.build()

    def test_exact_bulk_identities_and_background_pass(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        verification = self.result["verification"]
        self.assertLess(verification["background_constraint_max_abs"], 1.0e-12)
        self.assertLess(
            verification["extrinsic_curvature"]["maximum_relative_error"],
            1.0e-13,
        )
        self.assertLess(
            verification["lapse_variation"]["relative_error"], 1.0e-9
        )

    def test_quartic_jet_is_really_fourth_order(self) -> None:
        jet = self.result["verification"]["quartic_jet"]
        self.assertEqual(len(jet["local_coefficients_L0_to_L4"]), 5)
        for ratio in jet["halving_remainder_ratios"]:
            self.assertGreater(ratio, 27.0)
            self.assertLess(ratio, 37.0)

    def test_vehicle_does_not_claim_physical_vertices(self) -> None:
        gates = self.result["physical_gates"]
        self.assertTrue(gates["exact_bulk_ADM_scalar_density_identified"])
        self.assertTrue(gates["quartic_local_jet_generator_implemented"])
        self.assertTrue(
            gates["lapse_algebraic_solution_through_second_order_identified"]
        )
        self.assertFalse(gates["same_variables_recover_certified_S2_master_action"])
        self.assertFalse(gates["finite_endpoint_GHY_brane_bending_combined"])
        self.assertFalse(gates["compact_physical_S3_coefficients_projected"])
        self.assertFalse(gates["direct_physical_S4_contact_projected"])
        self.assertFalse(gates["physical_compact_S4_complete"])

    def test_memory_contract_forbids_dense_quartic_mode_tensor(self) -> None:
        contract = self.result["bounded_execution_contract"]
        self.assertEqual(contract["forbidden_dense_object"], "N_mode^4 quartic tensor")
        self.assertLessEqual(contract["cas_peak_rss_mib_max"], 512)
        self.assertLessEqual(contract["numeric_peak_rss_mib_max"], 128)
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])

    def test_constraint_orders_and_second_order_closure_are_explicit(self) -> None:
        contract = self.result["constraint_solution_contract"]
        self.assertEqual(contract["linear_solution"]["alpha1"], "zeta'/A'")
        self.assertIn("alpha2", contract["orders_needed"]["S4"])
        self.assertIn("P_T C^(2)", contract["second_order_closure_falsifier"])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if adm.OUTPUT.exists():
            rendered = json.loads(adm.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
