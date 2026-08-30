#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_bulk_cubic_vertex_inventory as inventory,
)


class BulkCubicVertexInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = inventory.build()

    def test_raw_metric_scalar_vertex_is_derived_and_checked(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        exact = self.result["exact_first_variation"]
        self.assertIn("h*Gbar^AB/2-h^AB", exact["identity"])
        self.assertLess(
            exact["numerical_identity_check"]["smallest_step_relative_error"],
            2.0e-8,
        )

    def test_fixed_metric_canonical_scalar_has_no_derivative_cubic(self) -> None:
        exact = self.result["exact_first_variation"]
        self.assertIn("h_AB=0", exact["fixed_metric_result"])
        self.assertIn("not sigma_a*Y", exact["potential_cubic"])

    def test_heavy_spectral_moment_is_only_a_unit_overlap_diagnostic(self) -> None:
        modal = self.result["modal_reduction"]
        self.assertEqual(modal["heavy_mode_count"], 6)
        self.assertAlmostEqual(
            modal["unit_overlap_spectral_moment_sum_mu_inverse_squared"],
            1.4978789,
            places=6,
        )
        self.assertIn("not a physical", modal["normalization_warning"])
        self.assertIn("Delta P_exchange=-0.5", modal["low_energy_result_if_c_a_were_known"])
        self.assertIn("direct_S4", modal["total_quartic_coefficient"])

    def test_stored_quadratic_profiles_are_not_misused_as_raw_fields(self) -> None:
        obstruction = self.result["projection_obstruction"]
        self.assertIn("mix gauges", obstruction["why_direct_insertion_is_invalid"])
        self.assertFalse(
            self.result["physical_gates"][
                "nonlinear_map_from_stored_h_to_metric_and_delta_chi_derived"
            ]
        )
        self.assertFalse(
            self.result["physical_gates"]["physical_cubic_vertex_complete"]
        )

    def test_next_reducer_must_recover_quadratic_action_first(self) -> None:
        contract = self.result["next_output_contract"]
        self.assertIn("reproduces S2", contract["decisive_gate"])
        self.assertIn(
            "S3 exchange E_N on 3, 5 and 7 mode truncations",
            contract["required_arrays"],
        )
        self.assertIn("total_Y2_sign_requires_direct_S4", contract["classification_if_all_gates_pass"])
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if inventory.OUTPUT.exists():
            rendered = json.loads(inventory.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
