#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import (
        derive_bps_volume_constraint_selector as volume,
    )
except ModuleNotFoundError:
    import derive_bps_volume_constraint_selector as volume


class BPSVolumeConstraintSelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.upstream = volume.biscalar.build()
        cls.result = volume.build(cls.upstream)

    def test_real_volume_normal_and_Khat_unit_tangent(self) -> None:
        candidate = self.result["volume_constraint_candidate"]
        np.testing.assert_allclose(
            candidate["normal_covector_nF_equals_dF"],
            [-0.9417600573320585, 0.015957167040401128],
            rtol=2.0e-13,
        )
        np.testing.assert_allclose(
            candidate["Khat_unit_kernel_tangent_vF"],
            [0.0478656724958490, 2.824936178194893],
            rtol=2.0e-12,
        )
        self.assertLess(abs(candidate["dF_vF_residual"]), 1.0e-14)
        self.assertLess(candidate["Khat_unit_residual"], 1.0e-13)
        self.assertFalse(candidate["physical_selection_by_current_action"])

    def test_selector_residuals_and_covariant_angles(self) -> None:
        selectors = self.result["selector_kernel_comparison"]
        expected = {
            "lower": (0.00096944215040605, 0.06862724410196),
            "upper": (11.9500423634785, 86.1252990507373),
        }
        for label, (residual, degrees) in expected.items():
            item = selectors[label]
            self.assertAlmostEqual(
                item["directional_residual_C_a_vF_a"], residual, places=12
            )
            self.assertAlmostEqual(
                item["covariant_kernel_angle_degrees"], degrees, places=9
            )
            self.assertLess(item["residual_identity_absolute_error"], 1.0e-12)
            self.assertLess(item["angle_Pythagorean_residual"], 1.0e-12)
        self.assertFalse(selectors["lower"]["exactly_aligned_on_current_background"])
        self.assertFalse(selectors["upper"]["exactly_aligned_on_current_background"])

    def test_residual_and_alignment_determinant_identities(self) -> None:
        tangent = np.asarray(
            self.result["volume_constraint_candidate"][
                "Khat_unit_kernel_tangent_vF"
            ]
        )
        background = self.result["actual_background"]
        E = background["E_endpoints"]
        H = background["A_u_endpoints"]
        for label, index, other_E in (
            ("lower", 0, E[1]),
            ("upper", 1, E[0]),
        ):
            item = self.result["selector_kernel_comparison"][label]
            self.assertAlmostEqual(
                item["directional_residual_C_a_vF_a"],
                -2.0 * H[index] * tangent[index],
                places=12,
            )
            self.assertAlmostEqual(
                item["covector_determinant_det_dF_dC"],
                2.0 * other_E * H[index],
                places=12,
            )
            self.assertAlmostEqual(
                item["W_at_endpoint_equals_minus_6_A_u"],
                -6.0 * H[index],
                places=14,
            )
        theorem = self.result["exact_alignment_theorem"]
        self.assertEqual(
            theorem["if_and_only_if"],
            "ker(dF)=ker(dC_i) iff A'_i=0 iff W_i=0",
        )

    def test_kernel_angle_is_coordinate_invariant(self) -> None:
        metric = np.asarray(
            self.upstream["moduli_metric"]["Khat_equals_6I_over_F"]
        )
        normal = np.asarray(
            self.result["volume_constraint_candidate"][
                "normal_covector_nF_equals_dF"
            ]
        )
        selector = np.asarray(
            self.result["selector_kernel_comparison"]["lower"]["C_a"]
        )
        tangent = volume._unit_kernel_tangent(metric, normal)
        original = volume._kernel_comparison(metric, tangent, selector)

        transform = np.asarray([[1.2, -0.3], [0.4, 0.9]])
        transformed_metric = transform.T @ metric @ transform
        transformed_normal = transform.T @ normal
        transformed_selector = transform.T @ selector
        transformed_tangent = volume._unit_kernel_tangent(
            transformed_metric, transformed_normal
        )
        changed = volume._kernel_comparison(
            transformed_metric, transformed_tangent, transformed_selector
        )
        self.assertAlmostEqual(
            original["covariant_kernel_angle_radians"],
            changed["covariant_kernel_angle_radians"],
            places=12,
        )
        self.assertAlmostEqual(
            original["covariant_misalignment_sine"],
            changed["covariant_misalignment_sine"],
            places=12,
        )

    def test_F_level_curve_includes_extrinsic_acceleration(self) -> None:
        limit = self.result["lower_exact_alignment_fixed_jet_diagnostic"]
        level = limit["F_level_set_curve"]
        ambient = limit["ambient_Khat_geodesic_diagnostic"]
        acceleration = level["extrinsic_acceleration"]
        self.assertAlmostEqual(
            level["selector_second_derivative"],
            0.004549619630257018,
            places=14,
        )
        self.assertAlmostEqual(
            ambient["covariant_selector_curvature"],
            -0.331058523518205,
            places=12,
        )
        self.assertGreater(level["selector_second_derivative"], 0.0)
        self.assertLess(ambient["covariant_selector_curvature"], 0.0)
        self.assertAlmostEqual(
            acceleration["ambient_Hessian_plus_extrinsic_term"],
            level["selector_second_derivative"],
            places=14,
        )
        self.assertLess(level["identity_absolute_error"], 1.0e-12)
        self.assertLess(acceleration["F_second_derivative_residual"], 1.0e-12)
        self.assertLess(
            acceleration["Khat_unit_speed_derivative_residual"], 1.0e-12
        )
        self.assertLess(
            acceleration["Khat_tangent_projection_residual"], 1.0e-12
        )

    def test_F_level_curve_signs_do_not_complete_minimal_q2Y(self) -> None:
        expansions = self.result["lower_exact_alignment_fixed_jet_diagnostic"][
            "F_level_set_curve"
        ]["expansions"]
        coefficient = 0.002274809815128509
        self.assertAlmostEqual(
            expansions["C"]["qbar_squared_coefficient"], coefficient, places=14
        )
        self.assertEqual(expansions["C"]["sign"], "positive")
        self.assertAlmostEqual(
            expansions["one_minus_C"]["qbar_squared_coefficient"],
            -coefficient,
            places=14,
        )
        self.assertEqual(expansions["one_minus_C"]["sign"], "negative")
        minimal = expansions["minus_Y_over_C"]
        self.assertAlmostEqual(
            minimal["qbar_squared_Y_coefficient"], coefficient, places=14
        )
        self.assertEqual(minimal["sign"], "positive")
        self.assertFalse(
            minimal["matches_requested_negative_qbar_squared_Y_sign"]
        )
        shifted = expansions["shifted_selector_s_equals_C_minus_1"]
        self.assertGreater(shifted["s_qbar_squared_coefficient"], 0.0)
        self.assertLess(shifted["minus_sY_qbar_squared_Y_coefficient"], 0.0)
        self.assertTrue(shifted["matches_requested_sign_conditionally"])
        self.assertFalse(shifted["selected_by_current_minimal_matter_action"])
        self.assertFalse(expansions["physical_q2Y_vertex_derived"])

    def test_ambient_sign_is_not_substituted_for_constraint_curve_sign(self) -> None:
        limit = self.result["lower_exact_alignment_fixed_jet_diagnostic"]
        level = limit["F_level_set_curve"]["expansions"]
        ambient = limit["ambient_Khat_geodesic_diagnostic"][
            "Riemann_normal_expansions"
        ]
        self.assertGreater(level["C"]["qbar_squared_coefficient"], 0.0)
        self.assertLess(ambient["C"]["qbar_squared_coefficient"], 0.0)
        self.assertIn("not the trajectory", limit["ambient_Khat_geodesic_diagnostic"]["scope"])
        self.assertTrue(
            self.result["checks"][
                "ambient_and_F_level_set_curvatures_have_opposite_sign"
            ]
        )

    def test_lower_zero_is_only_an_out_of_interval_Taylor_hypothesis(self) -> None:
        extrapolation = self.result["lower_A_u_zero_local_extrapolation"]
        self.assertAlmostEqual(
            extrapolation["delta_u_root_equals_minus_A_u_over_A_uu"],
            -0.010198486867468402,
            places=14,
        )
        self.assertAlmostEqual(
            extrapolation["estimated_u_at_A_u_zero"],
            3.467891583404728e-05,
            places=16,
        )
        self.assertFalse(extrapolation["inside_certified_domain"])
        self.assertFalse(extrapolation["Taylor_remainder_bounded_from_current_artifact"])
        self.assertFalse(extrapolation["outside_interval_background_evaluated"])
        self.assertFalse(extrapolation["zero_confirmed"])

    def test_current_theory_and_physical_gates_fail_closed(self) -> None:
        status = self.result["current_theory_vs_new_extension"]
        gates = self.result["physical_gates"]
        self.assertFalse(status["top_form_action_written_here"])
        self.assertFalse(status["stress_energy_or_backreaction_computed_here"])
        self.assertFalse(status["force_claim"])
        self.assertFalse(gates["top_form_present_in_current_repository_theory"])
        self.assertFalse(gates["global_F_constraint_present_in_current_repository_action"])
        self.assertFalse(gates["F_constraint_physically_selects_ker_dF"])
        self.assertFalse(gates["minimal_minus_Y_over_C_has_requested_negative_q2Y_sign"])
        self.assertFalse(gates["shifted_s_equals_C_minus_1_operator_selected_by_current_action"])
        self.assertFalse(gates["physical_q2Y_vertex_derived"])
        self.assertFalse(gates["force_law_derived_or_observed"])
        self.assertIn("fixing F alone is insufficient", self.result["candidate_verdict"])

    def test_falsifiers_cover_geometry_extension_and_matter_reduction(self) -> None:
        identifiers = {item["id"] for item in self.result["falsifiers"]}
        self.assertEqual(
            identifiers,
            {
                "F1_endpoint_derivative",
                "F2_alignment_identity",
                "F3_outside_interval_zero",
                "F4_constraint_dynamics",
                "F5_physical_matter_vertex",
            },
        )

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive definite"):
            volume._unit_kernel_tangent(
                np.asarray([[1.0, 0.0], [0.0, -1.0]]), np.asarray([1.0, 0.0])
            )
        with self.assertRaisesRegex(ValueError, "label"):
            volume._formal_alignment_limit(self.upstream, "middle")

        bad_checks = copy.deepcopy(self.upstream)
        bad_checks["checks"]["all"] = False
        with self.assertRaisesRegex(RuntimeError, "must pass first"):
            volume.build(bad_checks)

        open_q2Y = copy.deepcopy(self.upstream)
        open_q2Y["physical_gates"]["physical_q2Y_selector_derived"] = True
        with self.assertRaisesRegex(RuntimeError, "explicitly closed"):
            volume.build(open_q2Y)

    def test_certificate_and_generated_artifact_match(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])
        if volume.OUTPUT.exists():
            rendered = json.loads(volume.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
