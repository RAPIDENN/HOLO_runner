from __future__ import annotations

import json
import math
import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_covariant_5d_pseudogap_gate as gate,
)


class Covariant5DPseudogapGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    def test_current_compact_action_is_killed_only_as_bath_origin(self) -> None:
        current = self.result["current_action_no_go"]
        self.assertEqual(
            current["result"], "KILLED_AS_EXACT_INFRARED_PSEUDOGAP_ORIGIN"
        )
        self.assertEqual(current["density_of_states_exponent"], 0.0)
        self.assertEqual(current["target_density_of_states_exponent"], 1.0)
        self.assertAlmostEqual(
            current["positive_tower_after_quadratic_subtraction_power"],
            4.0,
            places=12,
        )
        self.assertAlmostEqual(current["zero_mode_power"], 1.0, places=12)
        self.assertFalse(current["proca_khronon_or_clifford_sector_present"])

    def test_hyperscaling_target_family_and_nec_boundary(self) -> None:
        for z in (1.0, 1.2, 1.5, 2.0):
            theta = 3.0 - 2.0 * z
            scaling = gate.hyperscaling_spectral_exponents(3, z, theta)
            self.assertAlmostEqual(scaling["density_of_states_exponent"], 1.0)
            self.assertAlmostEqual(scaling["gap_free_energy_exponent"], 3.0)
        self.assertFalse(
            gate.hyperscaling_null_energy_condition(3, 1.0, 1.0)["satisfied"]
        )
        self.assertTrue(
            gate.hyperscaling_null_energy_condition(3, 1.2, 0.6)["satisfied"]
        )
        self.assertTrue(
            gate.hyperscaling_null_energy_condition(3, 1.5, 0.0)["satisfied"]
        )

    def test_einstein_proca_solution_uses_explicit_normalization(self) -> None:
        candidate = gate.einstein_proca_lifshitz_parameters(3, 1.5)
        self.assertEqual(candidate["bulk_spacetime_dimension"], 5)
        self.assertEqual(
            candidate["action_convention"],
            "R+Lambda-(F_MN F^MN+m_B^2 B_M B^M)/4",
        )
        self.assertAlmostEqual(
            candidate["proca_mass_squared_times_L_squared"], 9.0
        )
        self.assertAlmostEqual(
            candidate["timelike_tangent_amplitude_squared"], 2.0 / 3.0
        )
        self.assertAlmostEqual(candidate["Lambda_times_L_squared"], 57.0 / 4.0)
        self.assertTrue(candidate["real_timelike_vector"])
        self.assertTrue(candidate["isotropic_in_boundary_space"])

    def test_free_lifshitz_density_is_linear_with_closed_normalization(self) -> None:
        c = 0.73
        expected = 1.0 / (3.0 * math.pi**2 * c**2)
        actual = gate.lifshitz_dos_coefficient(
            3, 1.5, dispersion_coefficient=c
        )
        self.assertAlmostEqual(actual, expected, places=15)
        low = gate.lifshitz_density_of_states(
            0.2, 3, 1.5, dispersion_coefficient=c
        )
        high = gate.lifshitz_density_of_states(
            0.8, 3, 1.5, dispersion_coefficient=c
        )
        self.assertAlmostEqual(high / low, 4.0, places=14)

    def test_clifford_witness_depends_on_norms_not_inserted_absolute_field(self) -> None:
        momentum = np.asarray([0.3, -0.2, 0.4])
        acceleration = np.asarray([0.2, 0.1, -0.5])
        spectrum = gate.lifshitz_clifford_spectrum(momentum, acceleration)
        rotated = gate.lifshitz_clifford_spectrum(
            momentum[[2, 0, 1]], acceleration[[1, 2, 0]]
        )
        self.assertTrue(np.allclose(spectrum, rotated, rtol=0.0, atol=2.0e-15))
        self.assertAlmostEqual(spectrum[0], spectrum[1], places=14)
        self.assertAlmostEqual(spectrum[2], spectrum[3], places=14)
        self.assertAlmostEqual(spectrum[0], -spectrum[-1], places=14)

    def test_lifshitz_scaling_and_free_witness_are_not_conflated(self) -> None:
        candidate = self.result["covariant_5D_scaling_candidate"]
        self.assertTrue(
            self.result["decision"][
                "covariant_local_5D_Lifshitz_scaling_background_exhibited"
            ]
        )
        self.assertIn("fractional", candidate["free_witness"]["locality_status"])
        self.assertFalse(
            candidate["missing_bridge"][
                "bulk_spinor_flavor_action_and_boundary_conditions_frozen"
            ]
        )
        self.assertFalse(candidate["missing_bridge"]["determinant_sign_derived"])
        self.assertIn("Thermodynamic", candidate["scaling_interpretation"])
        self.assertTrue(
            self.result["decision"]
            ["effective_linear_state_counting_exponent_from_5D_scaling"]
        )
        self.assertFalse(
            self.result["decision"]["literal_boundary_single_particle_DOS_derived"]
        )
        self.assertFalse(
            self.result["decision"][
                "exact_Clifford_determinant_derived_from_same_local_5D_action"
            ]
        )

    def test_supertrace_is_per_negative_branch_and_counts_real_bosons(self) -> None:
        per_branch = gate.matching_supertraces(1, 8)
        self.assertTrue(per_branch["quadratic_cancels"])
        self.assertAlmostEqual(per_branch["signed_cubic_sum"], 0.5)
        self.assertAlmostEqual(per_branch["signed_quartic_sum"], 0.75)
        four_by_four = gate.matching_supertraces(2, 16)
        self.assertTrue(four_by_four["quadratic_cancels"])
        self.assertAlmostEqual(four_by_four["signed_cubic_sum"], 1.0)
        self.assertAlmostEqual(four_by_four["signed_quartic_sum"], 1.5)

    def test_matching_surface_drifts_when_anomalous_rates_split(self) -> None:
        tangent = gate.matching_beta_on_sum_rule(
            1,
            common_coupling=2.0,
            fermion_anomalous_rate=0.03,
            boson_anomalous_rate=0.03,
            fermion_dos_anomalous_rate=0.01,
            boson_dos_anomalous_rate=0.01,
        )
        drift = gate.matching_beta_on_sum_rule(
            1,
            common_coupling=2.0,
            fermion_anomalous_rate=0.03,
            boson_anomalous_rate=-0.01,
        )
        self.assertEqual(tangent, 0.0)
        self.assertAlmostEqual(drift, 0.32)
        self.assertEqual(
            self.result["critical_matching_audit"]["status"],
            "CODIMENSION_ONE_CRITICAL_MATCHING_NOT_PROTECTED",
        )

    def test_ims_cubic_is_kept_as_a_distinct_wrong_observable(self) -> None:
        phi = 0.37
        fixed = gate.ims_rank_one_prepotential(phi, root_charges=(-2.0, 2.0))
        scaled = gate.ims_rank_one_prepotential(
            2.0 * phi, root_charges=(-2.0, 2.0)
        )
        self.assertAlmostEqual(scaled / fixed, 8.0)
        alternative = self.result["protected_alternative_audit"]
        self.assertIn("not vacuum energy", alternative["fatal_identification_gap"])
        self.assertEqual(
            alternative["status"],
            "SURVIVES_AS_DISTINCT_PROTECTED_5D_ROUTE_NOT_AS_AQUAL_BATH",
        )
        self.assertFalse(
            self.result["decision"]["IMS_protected_cubic_is_same_AQUAL_observable"]
        )

    def test_static_rank_and_temporal_memory_block_dynamics(self) -> None:
        precheck = self.result["time_and_constraint_precheck"]
        self.assertEqual(
            gate.cubic_static_hessian_eigenvalues(0.0, 2.0),
            (0.0, 0.0, 0.0),
        )
        self.assertEqual(
            gate.cubic_static_hessian_eigenvalues(0.5, 2.0),
            (3.0, 3.0, 6.0),
        )
        self.assertAlmostEqual(precheck["gapless_static_bath_kernel_power"], 1.0, places=6)
        self.assertFalse(precheck["local_finite_derivative_effective_action"])
        self.assertFalse(precheck["constant_principal_rank_at_vacuum"])
        self.assertFalse(
            self.result["decision"][
                "complete_constraint_rank_and_time_stability_derived"
            ]
        )

    def test_acceptance_ladder_passes_scaling_not_determinant(self) -> None:
        ladder = {
            row["level"]: row["status"] for row in self.result["acceptance_ladder"]
        }
        self.assertEqual(ladder["L0_uniform_static_spectrum"], "PASS")
        self.assertEqual(ladder["L1_current_compact_5D_origin"], "KILLED")
        self.assertEqual(
            ladder["L2_covariant_5D_linear_scaling_background"], "PASS"
        )
        self.assertEqual(
            ladder["L3_same_action_Clifford_determinant"], "BLOCKED"
        )
        self.assertEqual(ladder["L4_protected_quadratic_matching"], "BLOCKED")
        self.assertEqual(
            ladder["L5_constraints_and_retarded_stability"], "BLOCKED"
        )

    def test_no_physical_or_publication_promotion(self) -> None:
        decision = self.result["decision"]
        self.assertEqual(
            decision["verdict"],
            "COVARIANT_5D_LIFSHITZ_SCALING_ROUTE_SURVIVES_"
            "DETERMINANT_MATCHING_AND_DYNAMICS_BLOCKED",
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
        with self.assertRaises(gate.CovariantOriginInputError):
            gate.hyperscaling_spectral_exponents(0, 1.5)
        with self.assertRaises(gate.CovariantOriginInputError):
            gate.hyperscaling_spectral_exponents(3, 0.0)
        with self.assertRaises(gate.CovariantOriginInputError):
            gate.hyperscaling_spectral_exponents(3, 1.0, 3.0)
        with self.assertRaises(gate.CovariantOriginInputError):
            gate.lifshitz_clifford_spectrum([1.0, 2.0], [1.0, 2.0, 3.0])
        with self.assertRaises(gate.CovariantOriginInputError):
            gate.matching_supertraces(-1, 8)
        with self.assertRaises(gate.CovariantOriginInputError):
            gate.ims_rank_one_prepotential(1.0, inverse_gauge_coupling=-1.0)
        with self.assertRaises(gate.CovariantOriginInputError):
            gate.cubic_static_hessian_eigenvalues(-1.0, 1.0)

    def test_stored_artifact_equals_fresh_builder(self) -> None:
        stored = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.result)


if __name__ == "__main__":
    unittest.main()
