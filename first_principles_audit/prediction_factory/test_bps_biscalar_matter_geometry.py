#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_bps_biscalar_matter_geometry as geometry,
)


class BPSBiscalarMatterGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = geometry.build()

    def test_real_background_and_only_declared_inputs_are_used(self) -> None:
        self.assertEqual(self.result["actual_background"]["samples"], 1979)
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])
        self.assertTrue(self.result["checks"]["all"])
        self.assertTrue(
            self.result["checks"]["stored_zero_mode_Gram_recomputed"]
        )
        self.assertTrue(
            self.result["checks"]["real_local_fit_reproduces_selector_jets"]
        )
        self.assertTrue(
            self.result["checks"][
                "real_local_fit_reproduces_metric_derivatives"
            ]
        )

    def test_two_physical_moduli_are_resolved_without_selecting_q(self) -> None:
        gates = self.result["physical_gates"]
        self.assertTrue(gates["finite_endpoint_physical_mode_count_resolved_here"])
        self.assertEqual(gates["physical_moduli_count"], 2)
        self.assertFalse(gates["unique_tangent_selected_by_BPS_geometry"])
        self.assertTrue(self.result["checks"]["endpoint_map_is_invertible"])
        self.assertTrue(
            self.result["checks"]["endpoint_moduli_metric_is_positive"]
        )

    def test_Einstein_frame_metric_and_connection_match_real_background(self) -> None:
        metric = self.result["moduli_metric"]
        np.testing.assert_allclose(
            metric["Khat_equals_6I_over_F"],
            [[2.0025316942833, -0.03453086935997],
             [-0.03453086935997, 0.12590438815290]],
            rtol=2.0e-12,
            atol=2.0e-12,
        )
        np.testing.assert_allclose(
            metric["Christoffel_Gamma_c_ab"],
            [
                [[0.284405648747, -0.009874972463],
                 [-0.009874972463, 0.008156574802]],
                [[-0.238901919156, 0.582801108060],
                 [0.582801108060, -1.661829250622]],
            ],
            rtol=2.0e-9,
            atol=2.0e-9,
        )
        self.assertGreater(min(metric["Khat_eigenvalues"]), 0.0)
        self.assertEqual(metric["Einstein_frame_relation"], "Khat_ab=6I_ab/F")

    def test_selector_coordinate_jets_are_derived_for_both_brane_choices(self) -> None:
        lower = self.result["selectors"]["lower"]
        upper = self.result["selectors"]["upper"]
        np.testing.assert_allclose(
            lower["C_a"], [-1.14534882574869, 0.01974994492543], rtol=2.0e-12
        )
        np.testing.assert_allclose(
            upper["C_a"], [-1.16560221611921, 4.24994900418859], rtol=2.0e-12
        )
        np.testing.assert_allclose(
            lower["coordinate_C_ab"],
            [[1.96272391413752, 0.00040000334437],
             [0.00040000334437, -0.08354619844404]],
            rtol=2.0e-11,
            atol=2.0e-12,
        )
        np.testing.assert_allclose(
            upper["coordinate_C_ab"],
            [[0.02360739669981, -4.93072939810254],
             [-4.93072939810254, 21.9797392954542]],
            rtol=2.0e-11,
            atol=2.0e-12,
        )

    def test_each_selector_has_a_stationary_direction_with_negative_curvature(
        self,
    ) -> None:
        expected = {"lower": -0.330977166008, "upper": -0.257821098976}
        for label, curvature in expected.items():
            invariant = self.result["selectors"][label][
                "invariants_in_Khat_equals_6I_over_F_units"
            ]
            self.assertLess(invariant["linear_silence_residual"], 1.0e-12)
            self.assertLess(invariant["metric_unit_residual"], 1.0e-12)
            self.assertAlmostEqual(
                invariant["covariant_projected_curvature"], curvature, places=10
            )
            self.assertGreater(
                invariant["one_minus_C_quadratic_coefficient"], 0.0
            )
            mixed = self.result["selectors"][label][
                "conditional_geodesic_mixed_jets"
            ]
            selector = mixed["selector_expansion_on_silent_geodesic"]
            target = mixed["target_auxiliary_s_equals_one_minus_C"]
            minimal = mixed["minimal_canonical_brane_scalar_in_Einstein_frame"]
            mutation = mixed["non_target_minus_C_times_Y_mutation"]
            self.assertAlmostEqual(selector["c2"], 0.5 * curvature, places=10)
            self.assertAlmostEqual(
                target["s_qbar_squared_coefficient"],
                -0.5 * curvature,
                places=10,
            )
            self.assertEqual(target["qbar_Y_coefficient_by_construction"], 0.0)
            self.assertAlmostEqual(
                target["qbar_squared_Y_candidate_coefficient"],
                0.5 * curvature,
                places=10,
            )
            self.assertAlmostEqual(
                minimal["qbar_squared_Y_candidate_coefficient"],
                0.5 * curvature,
                places=10,
            )
            self.assertAlmostEqual(
                mutation["qbar_squared_Y_coefficient"],
                -0.5 * curvature,
                places=10,
            )
            self.assertFalse(
                mixed["matter_Y_operator_identified_with_constitutive_Y"]
            )
            self.assertFalse(mixed["physical_q2Y_vertex_derived"])

    def test_omitting_Einstein_Weyl_factor_is_a_sign_changing_mutation(self) -> None:
        for label in ("lower", "upper"):
            physical = self.result["selectors"][label][
                "invariants_in_Khat_equals_6I_over_F_units"
            ]["covariant_projected_curvature"]
            mutation = self.result["selectors"][label][
                "omit_Einstein_Weyl_factor_mutation"
            ]["covariant_projected_curvature"]
            self.assertLess(physical, 0.0)
            self.assertGreater(mutation, 0.0)

    def test_projected_result_is_invariant_under_linear_coordinate_change(self) -> None:
        metric = np.asarray(
            self.result["moduli_metric"]["Khat_equals_6I_over_F"]
        )
        transform = np.asarray([[1.3, -0.2], [0.4, 0.9]])
        for label in ("lower", "upper"):
            selector = self.result["selectors"][label]
            gradient = np.asarray(selector["C_a"])
            covariant_hessian = np.asarray(
                selector["covariant_nabla_a_nabla_b_C"]
            )
            original = geometry._selector_invariants(
                metric, gradient, covariant_hessian
            )
            transformed = geometry._selector_invariants(
                transform.T @ metric @ transform,
                transform.T @ gradient,
                transform.T @ covariant_hessian @ transform,
            )
            self.assertAlmostEqual(
                original["gradient_norm_squared"],
                transformed["gradient_norm_squared"],
                places=11,
            )
            self.assertAlmostEqual(
                original["covariant_projected_curvature"],
                transformed["covariant_projected_curvature"],
                places=11,
            )

    def test_no_nonzero_direction_is_stationary_for_both_selectors(self) -> None:
        joint = self.result["joint_selector_gate"]
        self.assertFalse(joint["common_nonzero_silent_tangent_exists"])
        self.assertGreater(joint["covector_gram_determinant"], 1.0)
        self.assertNotEqual(joint["ordinary_gradient_matrix_determinant"], 0.0)

    def test_Palma_Davis_correction_matches_and_printed_mutation_is_a_ghost(
        self,
    ) -> None:
        oracle = self.result["palma_davis_independent_oracle"]
        self.assertLess(
            oracle["Weyl_vs_closed_corrected_relative"], 1.0e-12
        )
        self.assertLess(oracle["corrected_relative_to_expected"], 1.0e-12)
        self.assertGreater(min(oracle["corrected_endpoint_eigenvalues"]), 0.0)
        self.assertLess(min(oracle["literal_endpoint_eigenvalues"]), 0.0)
        self.assertGreater(max(oracle["literal_endpoint_eigenvalues"]), 0.0)

    def test_existing_positive_diagonal_completions_do_not_select_silent_mode(
        self,
    ) -> None:
        for label in ("lower", "upper"):
            gate = self.result["selectors"][label]["local_diagonal_stabilizer"]
            np.testing.assert_allclose(
                gate["localized_quadratic_weights"],
                [2.64200591326018, 0.001528401638203],
                rtol=2.0e-12,
            )
            self.assertTrue(gate["silent_tangent_has_same_sign_endpoint_components"])
            self.assertFalse(
                gate["positive_diagonal_p2_or_p6_completion_can_select_silent_tangent"]
            )
            self.assertFalse(
                gate["positive_local_diagonal_quadratic_selects_silent_tangent"]
            )
            self.assertFalse(
                gate["diagonal_sextic_selects_a_unique_linear_tangent_at_origin"]
            )

    def test_physical_q2Y_gate_remains_closed(self) -> None:
        gates = self.result["physical_gates"]
        self.assertFalse(gates["matter_localization_selected_by_bulk"])
        self.assertFalse(gates["matter_Y_convention_fixed"])
        self.assertFalse(gates["constitutive_Y_operator_identification_derived"])
        self.assertFalse(gates["absolute_kappa5_ell_canonical_normalization_fixed"])
        self.assertTrue(gates["standard_base_minus_Y_algebraically_separated"])
        self.assertFalse(
            gates["q2Y_sign_and_normalization_fixed_after_base_subtraction"]
        )
        self.assertFalse(gates["full_lapse_shift_matter_qY_reduction_completed"])
        self.assertFalse(gates["physical_q2Y_selector_derived"])
        self.assertIn("constitutive Y", self.result["physical_compatibility"]["verdict"])

    def test_singular_endpoint_map_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "singular"):
            geometry._endpoint_metric_from_basis(
                np.eye(2), np.asarray([[1.0, 0.0], [2.0, 0.0]])
            )

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if geometry.OUTPUT.exists():
            rendered = json.loads(geometry.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
