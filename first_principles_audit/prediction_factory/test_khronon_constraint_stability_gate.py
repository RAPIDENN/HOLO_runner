from __future__ import annotations

import json
import math
import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_dirac_critical_bath_gate as bath,
)
from first_principles_audit.prediction_factory import (
    derive_khronon_constraint_stability_gate as gate,
)


class KhrononConstraintStabilityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    def test_geometric_critical_value_knows_bulk_dimension(self) -> None:
        self.assertAlmostEqual(gate.geometric_critical_eta(3, 1.0), 2.0)
        self.assertAlmostEqual(gate.geometric_critical_eta(4, 1.0), 1.5)
        boundary = self.result["dimensional_boundary"]
        self.assertEqual(boundary["bulk_eta_c"], "3*xi/2")
        self.assertEqual(boundary["brane_eta_c"], "2*xi")
        self.assertIn("cannot be mixed", boundary["warning"])

    def test_lifshitz_origin_and_flat_constraint_backgrounds_are_not_conflated(self) -> None:
        self.assertAlmostEqual(gate.lifshitz_acceleration_magnitude(1.5, 1.0), 1.5)
        compatibility = self.result["background_compatibility_gate"]
        self.assertEqual(compatibility["origin_lifshitz_boundary_spatial_dimensions"], 3)
        self.assertEqual(compatibility["origin_free_witness_acceleration_components"], 3)
        self.assertEqual(compatibility["constraint_gate_bulk_spatial_dimensions"], 4)
        self.assertFalse(compatibility["same_background_analysis_completed"])
        self.assertFalse(
            compatibility["radial_projection_and_boundary_conditions_derived"]
        )
        self.assertFalse(
            self.result["decision"]
            ["flat_constraint_result_transferred_to_lifshitz_background"]
        )

    def test_shift_elimination_gives_general_scalar_kinetic_coefficient(self) -> None:
        lambda_k = 1.2
        expected_4d_space = 3.0 * (4.0 * lambda_k - 1.0) / (lambda_k - 1.0)
        expected_3d_space = 2.0 * (3.0 * lambda_k - 1.0) / (lambda_k - 1.0)
        self.assertAlmostEqual(
            gate.scalar_kinetic_coefficient(4, lambda_k), expected_4d_space
        )
        self.assertAlmostEqual(
            gate.scalar_kinetic_coefficient(3, lambda_k), expected_3d_space
        )
        self.assertGreater(expected_4d_space, 0.0)

    def test_sound_speed_reproduces_healthy_horava_form_and_critical_zero(self) -> None:
        lambda_k = 1.2
        eta_c_3 = gate.geometric_critical_eta(3, 1.0)
        expected = (lambda_k - 1.0) / (3.0 * lambda_k - 1.0) * (
            2.0 / 1.0 - 1.0
        )
        self.assertAlmostEqual(
            gate.scalar_sound_speed_squared(3, lambda_k, 1.0, 1.0), expected
        )
        self.assertAlmostEqual(
            gate.scalar_sound_speed_squared(3, lambda_k, 1.0, eta_c_3), 0.0
        )
        eta_c_4 = gate.geometric_critical_eta(4, 1.0)
        self.assertAlmostEqual(
            gate.scalar_sound_speed_squared(4, lambda_k, 1.0, eta_c_4), 0.0
        )
        self.assertGreater(
            gate.scalar_sound_speed_squared(4, lambda_k, 1.0, 1.4), 0.0
        )

    def test_positive_bath_quadratic_is_retained_at_geometric_matching(self) -> None:
        action = self.result["action"]
        self.assertAlmostEqual(
            action["positive_high_field_baseline_eta_infinity"]
            + action["bath_quadratic_increment"],
            action["bulk_4_plus_1_eta_c"],
        )
        self.assertFalse(action["critical_relation_is_radiatively_protected"])
        self.assertFalse(action["critical_relation_is_dynamically_selected"])
        self.assertIn("codimension-one tuning", action["matching_status"])
        self.assertFalse(
            self.result["decision"][
                "old_internal_bare_minus_bath_quadratic_cancellation_required"
            ]
        )
        self.assertIn("not added a second time", action["adapted_ADM_form"])
        self.assertIn("never both", action["bath_accounting"])
        self.assertFalse(
            self.result["decision"][
                "same_action_local_5D_microscopic_bath_derived"
            ]
        )
        self.assertFalse(self.result["decision"]["fine_tuning_eliminated"])
        self.assertTrue(
            self.result["checks"][
                "static_bath_is_not_double_counted_in_reduced_action"
            ]
        )

    def test_static_effective_function_equals_baseline_plus_filled_sea(self) -> None:
        eta_c = 1.5
        eta_inf = 1.4
        values = np.geomspace(1.0e-7, 1.0e5, 100)
        for value in values:
            with self.subTest(acceleration=value):
                action_value = gate.geometric_matched_function(
                    value,
                    a0=1.0,
                    eta_infinity=eta_inf,
                    eta_critical=eta_c,
                )
                bath_value = eta_inf * value * value + bath.bath_lagrangian(
                    value,
                    cutoff=1.0,
                    yukawa=1.0,
                    rho_slope=0.1,
                    degeneracy=2,
                )
                self.assertLess(
                    abs(action_value - bath_value) / abs(action_value), 2.0e-11
                )

    def test_schur_complement_gives_exact_mu_without_unstable_F(self) -> None:
        eta_c = 1.5
        eta_inf = 1.4
        delta = eta_c - eta_inf
        for x in np.geomspace(1.0e-12, 1.0e12, 300):
            with self.subTest(x=x):
                chi = gate.geometric_susceptibility(
                    x,
                    a0=1.0,
                    eta_infinity=eta_inf,
                    eta_critical=eta_c,
                )
                from_schur = (eta_c - chi) / delta
                direct = gate.geometric_mu(x, a0=1.0)
                expected = bath.matched_mu(float(x))
                self.assertAlmostEqual(direct, expected, places=14)
                self.assertLess(abs(from_schur - direct), 3.0e-15)

    def test_any_fixed_detuning_dominates_sufficiently_deep_infrared(self) -> None:
        x = 1.0e-8
        tuned = gate.geometric_mu(x, a0=1.0)
        detuned = gate.detuned_geometric_mu(
            x,
            a0=1.0,
            normalized_detuning=1.0e-4,
        )
        self.assertGreater(detuned, 1.0e3 * tuned)
        sensitivity = self.result["matching_sensitivity"]
        self.assertFalse(sensitivity["ward_identity_derived"])
        self.assertIn("beta_match", sensitivity["RG_normal_beta"])
        self.assertFalse(self.result["decision"]["fine_tuning_eliminated"])

    def test_hessian_bounds_keep_lapse_constraint_elliptic(self) -> None:
        eta_inf = 1.1
        eta_c = 1.5
        previous_transverse = math.inf
        previous_longitudinal = math.inf
        for acceleration in np.concatenate(([0.0], np.geomspace(1.0e-12, 1.0e12, 300))):
            row = gate.geometric_hessian_coefficients(
                float(acceleration),
                a0=1.0,
                eta_infinity=eta_inf,
                eta_critical=eta_c,
            )
            transverse = row["eta_transverse_F_prime_over_2a"]
            longitudinal = row["eta_longitudinal_F_second_over_2"]
            self.assertGreaterEqual(transverse, eta_inf)
            self.assertGreaterEqual(longitudinal, eta_inf)
            self.assertLessEqual(longitudinal, transverse)
            self.assertLessEqual(transverse, eta_c)
            self.assertLessEqual(transverse, previous_transverse)
            self.assertLessEqual(longitudinal, previous_longitudinal)
            self.assertGreaterEqual(row["lapse_symbol_longitudinal"], 2.0 * eta_inf)
            previous_transverse = transverse
            previous_longitudinal = longitudinal
        self.assertTrue(
            self.result["decision"]
            ["static_effective_acceleration_function_is_convex"]
        )

    def test_constraint_count_is_five_tensor_plus_one_khronon(self) -> None:
        without_dilaton = gate.local_constraint_inventory(4)
        self.assertEqual(without_dilaton["total_phase_space_dimension_including_lapse_shift"], 30)
        self.assertEqual(without_dilaton["first_class_constraints"], 8)
        self.assertEqual(without_dilaton["second_class_constraints"], 2)
        self.assertEqual(without_dilaton["einstein_tensor_dof"], 5)
        self.assertEqual(without_dilaton["extra_khronon_scalar_dof"], 1)
        self.assertEqual(without_dilaton["khronometric_gravitational_dof"], 6)
        with_dilaton = gate.local_constraint_inventory(4, include_dilaton=True)
        self.assertEqual(with_dilaton["total_bosonic_dof_before_bath"], 7)
        self.assertFalse(with_dilaton["global_time_reparametrization_mode_included"])

    def test_pure_negative_cubic_fundamental_aether_is_killed(self) -> None:
        killed = self.result["killed_realization"]
        self.assertEqual(
            killed["verdict"], "KILL_PURE_NEGATIVE_CUBIC_FUNDAMENTAL_AETHER"
        )
        self.assertEqual(killed["lapse_symbol_at_zero"], [0.0, 0.0])
        self.assertLess(max(killed["generic_aether_hessian_at_A_0p4_gamma_1"]), 0.0)
        self.assertFalse(
            self.result["decision"]["pure_negative_cubic_aether_realization_survives"]
        )

    def test_positive_ohmic_and_k4_coefficients_put_poles_below_axis(self) -> None:
        q_zeta = gate.scalar_kinetic_coefficient(4, 1.2)
        for damping in (0.0, 0.1, 10.0):
            for stabilizer in (0.0, 0.01, 5.0):
                roots = gate.critical_retarded_poles(
                    0.7,
                    q_zeta=q_zeta,
                    ohmic_coefficient=damping,
                    k4_coefficient=stabilizer,
                )
                with self.subTest(damping=damping, stabilizer=stabilizer):
                    self.assertLessEqual(max(root.imag for root in roots), 1.0e-15)
        diffusive = gate.critical_retarded_poles(
            1.0,
            q_zeta=q_zeta,
            ohmic_coefficient=0.4,
            k4_coefficient=0.0,
        )
        self.assertLess(min(root.imag for root in diffusive), 0.0)
        self.assertLess(min(abs(root) for root in diffusive), 1.0e-15)
        overdamped = gate.critical_retarded_poles(
            1.0,
            q_zeta=1.0,
            ohmic_coefficient=1.0e12,
            k4_coefficient=1.0,
        )
        self.assertAlmostEqual(overdamped[0].imag, -1.0e-12, delta=1.0e-27)
        self.assertAlmostEqual(overdamped[1].imag, -1.0e12, delta=1.0e-3)

    def test_z2_cubic_gradient_is_marginal_only_in_four_space_here(self) -> None:
        bulk = gate.critical_power_counting(4, 2.0)
        brane = gate.critical_power_counting(3, 2.0)
        self.assertEqual(bulk["field_dimension"], 1.0)
        self.assertEqual(bulk["cubic_gradient_operator_dimension"], 6.0)
        self.assertEqual(bulk["action_density_dimension"], 6.0)
        self.assertTrue(bulk["cubic_gradient_is_marginal"])
        self.assertFalse(brane["cubic_gradient_is_marginal"])

    def test_conditional_pole_pass_is_not_full_time_stability(self) -> None:
        temporal = self.result["conditional_temporal_completion"]
        self.assertTrue(
            temporal["microscopic_branch_cut_acknowledged_but_not_in_pole_model"]
        )
        self.assertFalse(temporal["branch_cut_resolved"])
        self.assertEqual(len(temporal["unproved_scope"]), 4)
        self.assertTrue(
            self.result["decision"]
            ["truncated_z2_kernel_has_no_upper_half_plane_poles"]
        )
        self.assertFalse(self.result["decision"]["full_microscopic_retarded_kernel_derived"])
        self.assertFalse(self.result["decision"]["complete_time_dependent_stability"])

    def test_acceptance_stops_before_full_retarded_problem(self) -> None:
        ladder = {
            row["level"]: row["status"] for row in self.result["acceptance_ladder"]
        }
        self.assertEqual(ladder["K1_geometric_matching_and_exact_mu"], "PASS")
        self.assertEqual(ladder["K2_local_flat_constraint_rank_and_DOF"], "PASS")
        self.assertEqual(
            ladder["K3_critical_local_z2_pole_model"],
            "CONDITIONAL_NO_UHP_IN_TRUNCATED_KERNEL",
        )
        self.assertEqual(ladder["K4_same_action_full_retarded_kernel"], "BLOCKED")
        self.assertEqual(ladder["K5_warped_brane_boundary_constraints"], "BLOCKED")

    def test_no_force_lensing_or_publication_promotion(self) -> None:
        decision = self.result["decision"]
        self.assertEqual(
            decision["verdict"],
            "GEOMETRIC_KHRONON_MATCHING_PRESERVES_LOCAL_CONSTRAINT_RANK_"
            "FULL_RETARDED_AND_WARPED_COMPLETION_BLOCKED",
        )
        for field in (
            "current_holo_mechanism",
            "physical_completion",
            "new_force_derived",
            "lensing_derived",
            "publication_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(decision[field])
        self.assertEqual(self.result["sources"]["raw_observational_tables_read_directly"], [])
        self.assertEqual(
            self.result["sources"]["inherited_target_origin"],
            "SPARC training split only",
        )
        self.assertTrue(self.result["checks"]["all"])

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(gate.KhrononGateInputError):
            gate.geometric_critical_eta(2, 1.0)
        with self.assertRaises(gate.KhrononGateInputError):
            gate.scalar_kinetic_coefficient(4, 1.0)
        with self.assertRaises(gate.KhrononGateInputError):
            gate.lifshitz_acceleration_magnitude(1.5, 0.0)
        with self.assertRaises(gate.KhrononGateInputError):
            gate.scalar_sound_speed_squared(4, 0.25, 1.0, 1.0)
        with self.assertRaises(gate.KhrononGateInputError):
            gate.geometric_matched_function(
                1.0, a0=1.0, eta_infinity=1.5, eta_critical=1.5
            )
        with self.assertRaises(gate.KhrononGateInputError):
            gate.geometric_hessian_coefficients(
                -1.0, a0=1.0, eta_infinity=1.0, eta_critical=1.5
            )
        with self.assertRaises(gate.KhrononGateInputError):
            gate.detuned_geometric_mu(
                1.0, a0=1.0, normalized_detuning=float("nan")
            )
        with self.assertRaises(gate.KhrononGateInputError):
            gate.critical_retarded_poles(
                1.0, q_zeta=-1.0, ohmic_coefficient=1.0, k4_coefficient=1.0
            )
        with self.assertRaises(gate.KhrononGateInputError):
            gate.critical_retarded_poles(
                1.0e200,
                q_zeta=1.0e200,
                ohmic_coefficient=1.0e200,
                k4_coefficient=1.0e200,
            )

    def test_stored_artifact_equals_fresh_builder(self) -> None:
        stored = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.result)


if __name__ == "__main__":
    unittest.main()
