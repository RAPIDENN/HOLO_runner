#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from first_principles_audit.prediction_factory import derive_bent_brane_geometry_S2 as bent


class BentBraneGeometryS2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = bent.build()

    def test_fixed_endpoint_orientations_and_background_junctions(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        endpoints = self.result["verification"]["endpoints"]
        self.assertEqual(
            {(row["label"], row["orientation"]) for row in endpoints},
            {("lower", -1), ("upper", 1)},
        )
        self.assertLess(
            self.result["verification"]["maxima"]["background_junction_max_abs"],
            1.0e-12,
        )
        self.assertGreater(
            self.result["verification"][
                "minimum_wrong_orientation_junction_abs"
            ],
            1.0e-3,
        )

    def test_bending_and_straightening_agree_through_second_order(self) -> None:
        maxima = self.result["verification"]["maxima"]
        self.assertLess(maxima["pointwise_chart_max_relative"], 1.0e-11)
        self.assertLess(
            maxima["coefficient_O0_O1_O2_chart_max_relative"], 1.0e-9
        )
        self.assertLess(
            maxima["normalization_and_orthogonality_max_abs"], 1.0e-12
        )
        self.assertLess(
            maxima["normal_covector_transform_max_relative"], 1.0e-12
        )
        self.assertLess(
            maxima["background_extrinsic_oracle_max_abs"], 1.0e-12
        )

    def test_nontrivial_bending_and_jet_sweep_are_measured(self) -> None:
        checks = self.result["checks"]
        self.assertTrue(checks["multiple_positive_gamma_values_exercised"])
        self.assertTrue(checks["zero_and_nonzero_eta_values_exercised"])
        self.assertTrue(checks["bending_value_gradient_and_hessian_are_nonzero"])
        self.assertTrue(checks["first_and_second_order_responses_are_nonzero"])
        self.assertGreater(
            self.result["verification"][
                "minimum_nontrivial_O1_coefficient_abs"
            ],
            1.0e-3,
        )
        self.assertGreater(
            self.result["verification"][
                "minimum_nontrivial_O2_coefficient_abs"
            ],
            1.0e-4,
        )

    def test_brane_jet_sensitivity_identities(self) -> None:
        self.assertTrue(self.result["checks"]["brane_jet_sensitivity_identities"])
        for row in self.result["verification"]["jet_sensitivities"]:
            self.assertLess(row["dB1_dgamma_error_abs"], 1.0e-9)
            self.assertLess(row["dB2_deta_error_abs"], 1.0e-9)
            self.assertNotEqual(row["expected_dB1_dgamma"], 0.0)
            self.assertGreater(row["expected_dB2_deta"], 0.0)

    def test_zero_bending_and_degenerate_jet_sweeps_fail_closed(self) -> None:
        with (
            patch.object(bent, "_bending", lambda x: 0.0 * x),
            patch.object(bent, "_bending_x", lambda x: 0.0 * x),
            patch.object(bent, "_bending_xx", lambda x: 0.0 * x),
        ):
            zero_bending = bent.build()
        self.assertFalse(
            zero_bending["checks"][
                "bending_value_gradient_and_hessian_are_nonzero"
            ]
        )
        self.assertFalse(
            zero_bending["physical_gates"][
                "radial_gauge_straightening_verified_through_O2"
            ]
        )
        with patch.object(
            bent,
            "JET_SWEEP",
            (("zero_a", 0.0, 0.0), ("zero_b", 0.0, 0.0)),
        ):
            zero_jets = bent.build()
        self.assertFalse(
            zero_jets["checks"]["multiple_positive_gamma_values_exercised"]
        )
        self.assertFalse(
            zero_jets["checks"]["zero_and_nonzero_eta_values_exercised"]
        )
        self.assertFalse(zero_jets["checks"]["all"])

    def test_geometry_closes_but_action_and_spectrum_do_not(self) -> None:
        gates = self.result["physical_gates"]
        self.assertTrue(gates["exact_bent_induced_metric_implemented"])
        self.assertTrue(gates["exact_inclined_unit_normal_implemented"])
        self.assertTrue(gates["exact_bent_extrinsic_curvature_implemented"])
        self.assertTrue(gates["radial_gauge_straightening_verified_through_O2"])
        self.assertFalse(gates["total_action_variation_reproduces_linear_junctions"])
        self.assertFalse(gates["EH_GHY_normal_derivative_cancellation_verified"])
        self.assertFalse(gates["finite_gamma_compact_ADM_S2_spectrum_recovered"])
        self.assertFalse(gates["finite_gamma_compact_ADM_S2_norm_recovered"])
        self.assertFalse(gates["finite_gamma_bent_brane_S2_complete"])

    def test_no_observational_input_or_cubic_claim(self) -> None:
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])
        self.assertIn("does not yet", self.result["evidence_boundary"])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if bent.OUTPUT.exists():
            rendered = json.loads(bent.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
