from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory.build_master_prediction_registry import (
    OUT_JSON,
    build_registry,
)


class MasterPredictionRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build_registry()

    def test_no_detection_or_confirmation_claim(self) -> None:
        label = self.registry["global_classification"].lower()
        self.assertIn("no new physical detection", label)
        self.assertIn("no clean confirmatory holdout", label)

    def test_missing_physics_fails_closed(self) -> None:
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertEqual(
            links["boundary_selects_spectrum"]["gate"],
            "blocked_finite_boundary_curvatures_not_derived",
        )
        self.assertIn("missing_ell", links["dimensionless_force_to_lab_signal"]["gate"])
        self.assertEqual(
            links["gauge_links_to_wilson_observable"]["gate"],
            "missing_su3_link_configurations",
        )
        self.assertIn(
            "missing_uv_matching", links["qcd_scale_to_compactification_length"]["gate"]
        )
        self.assertIn(
            "missing_ell", links["em_double_comb_to_clock_signal"]["gate"]
        )
        self.assertEqual(
            links["trace_to_galaxy_readout"]["gate"],
            "missing_state_dependent_sector_and_unique_source_density",
        )
        self.assertIn(
            "independent_clock", links["breathing_response_to_lab_signal"]["gate"]
        )

    def test_boundary_adjudication_is_preserved(self) -> None:
        branches = self.registry["current_predictions"]["boundary_branches"]["branches"]
        self.assertTrue(branches["NN"]["has_exact_massless_mode"])
        self.assertLess(branches["ND"]["masses_mu"][0], 0.003)
        self.assertTrue(branches["DN"]["uv_point_probe_decouples"])
        self.assertTrue(branches["DD"]["uv_point_probe_decouples"])

    def test_comparators_are_not_cherry_picked(self) -> None:
        sparc = self.registry["current_predictions"]["sparc"]
        scores = sparc["test_chi2_per_point"]
        self.assertLess(scores["rar"], scores["legacy_p5_refit"])
        self.assertLess(scores["rar"], scores["p6_corrected_long_range_envelope"])
        self.assertLess(scores["rar"], scores["stiff_boundary_long_range_envelope"])
        self.assertLess(scores["rar"], scores["newton"])
        self.assertFalse(sparc["legacy_p5_accepted"])
        self.assertTrue(sparc["p6_current_curve_replaces_legacy_p5"])
        self.assertEqual(
            sparc["p6_corrected_benchmark_status"],
            "evaluated_exact_long_range_convolution_envelope",
        )
        self.assertAlmostEqual(
            sparc["p6_maximum_fractional_velocity_boost"],
            3.601085091786693e-5,
        )
        self.assertEqual(
            sparc["holo_acceleration_law_status"],
            "action_derived_stiff_force_available_but_empirically_insufficient",
        )
        self.assertTrue(sparc["finite_disk_best_at_upper_boundary"])
        self.assertFalse(sparc["finite_scale_identified"])
        self.assertFalse(sparc["disk_cancellation_rescues_stiff_candidate"])
        self.assertEqual(len(sparc["p5_parameters_at_bounds"]), 5)

    def test_desi_is_labeled_diagonal_diagnostic(self) -> None:
        desi = self.registry["current_predictions"]["desi_dr1_growth"]
        self.assertIn("not_confirmatory_likelihood", desi["classification"])
        self.assertGreater(desi["delta_chi2_holo_minus_lcdm"], 0.0)

    def test_qcd_and_galaxy_single_scale_no_go_is_visible(self) -> None:
        scale = self.registry["current_predictions"]["scale_consistency"]
        self.assertFalse(scale["single_scale_viable"])
        self.assertGreater(scale["orders_of_magnitude_in_ell"], 40.0)
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertEqual(
            links["qcd_scale_to_compactification_length"]["status"],
            "conditional_single_scale_no_go",
        )

    def test_universal_collector_is_visible_but_not_promoted(self) -> None:
        sparc = self.registry["current_predictions"]["sparc"]
        self.assertIn("not_action_derivation", sparc["collector_classification"])
        self.assertLess(
            sparc["collector_test_chi2_per_point"],
            sparc["test_chi2_per_point"]["stiff_boundary_long_range_envelope"],
        )
        self.assertGreater(sparc["radius_0p6_kpc_stiff_chi2_per_point"], 100.0)
        self.assertGreater(sparc["ell_600_kpc_stiff_chi2_per_point"], 100.0)
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertEqual(
            links["galaxy_residual_to_universal_collector"]["gate"],
            "missing_action_derived_nonlinear_or_ultralight_sector",
        )

    def test_nonlinear_action_is_degenerate_and_not_holo_derived(self) -> None:
        action = self.registry["current_predictions"][
            "nonlinear_collector_action"
        ]
        self.assertTrue(action["passes"])
        self.assertEqual(action["per_galaxy_parameters"], 0)
        self.assertGreater(action["minimum_transverse_elliptic_eigenvalue"], 0.0)
        self.assertGreater(
            action["minimum_longitudinal_elliptic_eigenvalue"], 0.0
        )
        self.assertFalse(action["uniformly_elliptic"])
        self.assertTrue(action["degenerately_elliptic_at_zero"])
        self.assertLess(action["constitutive_inversion_closure_max_relative_error"], 1.0e-8)
        self.assertLess(action["plummer_pde_max_relative_residual"], 2.0e-4)
        self.assertAlmostEqual(
            action["transition_mass_at_600_kpc_msun"]
            / action["transition_mass_at_0p6_kpc_msun"],
            1.0e6,
            places=8,
        )
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertEqual(
            links["universal_collector_to_nonlinear_action"]["gate"],
            "missing_microscopic_holo_and_relativistic_completion",
        )

    def test_current_holo_embedding_gate_rejects_linear_sector_only(self) -> None:
        gate = self.registry["current_predictions"]["holo_collector_embedding_gate"]
        self.assertFalse(gate["current_linearized_sector_can_embed"])
        self.assertFalse(gate["full_nonlinear_completion_resolved"])
        self.assertAlmostEqual(gate["current_mass_exponent"], 1.0)
        self.assertAlmostEqual(gate["collector_deep_mass_exponent_range"][0], 0.5, places=5)
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertIn("conditional_no_go", links["current_holo_to_nonlinear_collector"]["status"])

    def test_nonlinear_route_matrix_rejects_direct_sR_but_keeps_derivative_route(self) -> None:
        route = self.registry["current_predictions"]["nonlinear_route_matrix"]
        self.assertTrue(route["passes"])
        self.assertFalse(route["physical_completion"])
        self.assertFalse(route["direct_full_planck_selector_completion"])
        self.assertEqual(
            route["leading_research_hypotheses"][0],
            "derivative_constitutive_scalar",
        )
        self.assertIn("rejected", route["direct_jordan_selector_status"])
        self.assertIn("surviving_architecture", route["surviving_architecture_status"])
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertIn(
            "missing_bulk_derived_PY",
            links["matter_interface_to_derivative_constitutive_scalar"]["gate"],
        )

    def test_minimal_mechanism_ladder_is_blocked_without_promoting_a_claim(self) -> None:
        campaign = self.registry["current_predictions"][
            "minimal_mechanism_campaign"
        ]
        self.assertEqual(
            campaign["step_statuses"],
            {"C1": "failed", "C2": "failed", "C3": "blocked"},
        )
        self.assertFalse(campaign["target_blind"])
        self.assertEqual(
            campaign["record_time_authentication"],
            "not_timestamp_authenticated",
        )
        self.assertEqual(
            campaign["provenance_scope"],
            "declared_repository_paths_only",
        )
        self.assertFalse(campaign["mechanism_candidate"])
        self.assertFalse(campaign["physical_completion"])
        self.assertFalse(campaign["new_force_derived"])
        self.assertFalse(campaign["lensing_derived"])
        self.assertFalse(campaign["publication_authorized"])
        self.assertEqual(campaign["verdict"]["status"], "blocked")
        self.assertEqual(
            set(campaign["skai_review_attempt_statuses"].values()),
            {"provider_error"},
        )
        links = {row["id"]: row for row in self.registry["links"]}
        link = links["nonlinear_route_matrix_to_minimal_mechanism_campaign"]
        self.assertEqual(link["gate"], "c3_input_contract_incomplete")
        self.assertIn("no physics evidence", link["meaning"])

    def test_critical_bridge_changes_exponent_but_remains_prospective(self) -> None:
        gate = self.registry["current_predictions"][
            "bulk_constitutive_decision_gate"
        ]
        self.assertTrue(gate["passes"])
        self.assertEqual(gate["old_source_mass_exponent"], 1.0)
        self.assertEqual(gate["new_source_mass_exponent"], 0.5)
        self.assertLess(gate["old_three_halves_crossover_width_dex"], 0.25)
        self.assertAlmostEqual(gate["minimal_radial_characteristic_ratio"], 2.0)
        self.assertTrue(gate["raw_metric_scalar_vertex_derived"])
        self.assertTrue(gate["fixed_metric_scalar_derivative_cubic_zero"])
        self.assertFalse(gate["physical_overlap_coefficients_computed"])
        self.assertFalse(gate["prospective_test_can_run"])
        self.assertFalse(gate["physical_completion"])
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertIn(
            "missing_q2Y_vertex",
            links["quadratic_carrier_to_critical_constitutive_bridge"]["gate"],
        )
        self.assertIn(
            "unfrozen_boundary",
            links["critical_constitutive_bridge_to_physical_force"]["gate"],
        )

    def test_blind_bulk_amplitude_scan_is_first_next_run(self) -> None:
        first = min(
            self.registry["next_falsifiable_runs"],
            key=lambda row: row["priority"],
        )
        self.assertEqual(first["id"], "blind_bulk_constitutive_amplitude_scan")
        self.assertIn("Dirichlet-to-Neumann", first["output"])

    def test_gauge_invariant_cubic_route_closes_bulk_map_not_boundaries(self) -> None:
        gate = self.registry["current_predictions"][
            "bulk_constitutive_decision_gate"
        ]
        self.assertTrue(gate["gauge_invariant_S2_operator_match"])
        self.assertTrue(gate["stiff_to_gauge_invariant_mode_map"])
        self.assertTrue(gate["bmp_holographic_three_point_kernel_identified"])
        self.assertFalse(gate["compact_bulk_S3_action_derived"])
        self.assertTrue(gate["cubic_boundary_jet_nonidentifiability_proved"])
        self.assertTrue(gate["natural_fixed_jet_stiff_path_defined"])
        self.assertLess(gate["stiff_mode_map_max_rms_relative"], 5.0e-4)
        self.assertFalse(gate["compact_S3_endpoint_terms_derived"])
        self.assertFalse(gate["full_second_order_junction_source_derived"])
        self.assertTrue(
            gate["formal_fixed_brane_GHY_and_potential_jet_convolution_verified"]
        )
        self.assertIn(
            "eta^2/gamma^5", gate["quartic_stiff_eta_squared_uniformity_rule"]
        )
        self.assertTrue(gate["exact_radial_ADM_bulk_density_derived"])
        self.assertTrue(gate["ADM_quartic_jet_generator_implemented"])
        self.assertTrue(gate["bulk_ADM_S2_compact_support_recovered"])
        self.assertFalse(gate["compact_master_ADM_S2_including_endpoints_recovered"])
        self.assertLess(gate["ADM_S2_backward_max_relative"], 1.0e-9)
        self.assertEqual(
            gate["nonlinear_swarm_winner"], "hybrid_ADM_plus_BMP_oracle"
        )
        self.assertFalse(gate["nonlinear_swarm_physical_c000"])
        self.assertFalse(gate["physical_compact_S3_complete"])
        self.assertFalse(gate["direct_quartic_contact_computed"])
        self.assertTrue(gate["conditional_functional_BPS_m2_zero"])
        self.assertTrue(gate["conditional_functional_BPS_u4_zero"])
        self.assertFalse(gate["conditional_functional_BPS_positive_q6"])
        self.assertTrue(
            gate["conditional_positive_q6_from_sixth_order_brane_detuning"]
        )
        self.assertFalse(gate["sixth_order_brane_detuning_selected_by_bulk"])
        self.assertFalse(gate["conditional_functional_BPS_q2Y_derived"])
        self.assertEqual(gate["BPS_candidate_bulk_zero_mode_count"], 2)
        self.assertFalse(gate["BPS_unique_canonical_q_selected"])
        self.assertGreater(gate["BPS_separation_slice_lower_selector_c1"], 0.0)
        self.assertGreater(gate["BPS_separation_slice_upper_selector_c1"], 0.0)
        self.assertFalse(gate["BPS_minimal_separation_slice_pure_q2Y"])
        self.assertTrue(gate["BPS_unselected_one_brane_orthogonal_tangent_exists"])
        self.assertFalse(
            gate["BPS_same_tangent_stationary_for_both_matter_brane_metrics"]
        )
        self.assertEqual(gate["BPS_finite_endpoint_physical_moduli_count"], 2)
        self.assertGreater(
            min(gate["BPS_Planck_normalized_kinetic_metric_eigenvalues"]), 0.0
        )
        self.assertLess(
            gate["BPS_lower_silent_covariant_selector_curvature"], 0.0
        )
        self.assertLess(
            gate["BPS_upper_silent_covariant_selector_curvature"], 0.0
        )
        self.assertAlmostEqual(
            gate["BPS_lower_conditional_q2Y_coefficient"],
            -0.1654885830040268,
        )
        self.assertAlmostEqual(
            gate["BPS_upper_conditional_q2Y_coefficient"],
            -0.1289105494877548,
        )
        self.assertFalse(
            gate["BPS_positive_local_p2_or_p6_selects_silent_tangent"]
        )
        self.assertFalse(gate["BPS_matter_Y_operator_identified"])
        self.assertFalse(gate["BPS_physical_q2Y_selector_derived"])
        self.assertLess(
            gate["BPS_volume_constraint_lower_kernel_angle_degrees"], 0.1
        )
        self.assertNotEqual(
            gate["BPS_volume_constraint_lower_selector_residual"], 0.0
        )
        self.assertFalse(
            gate["BPS_volume_constraint_exact_alignment_on_background"]
        )
        self.assertGreater(
            gate["BPS_volume_constraint_F_level_q2Y_coefficient"], 0.0
        )
        self.assertFalse(gate["BPS_volume_constraint_present_in_action"])
        self.assertFalse(gate["BPS_volume_constraint_physical_q2Y_derived"])
        self.assertFalse(gate["functional_BPS_branch_selected_by_bulk"])
        self.assertFalse(gate["m2_u4_zero_from_bulk_alone"])
        self.assertFalse(gate["synthetic_fixture_used_as_BPS_physical_evidence"])
        self.assertLess(gate["BPS_raw_action_max_relative"], 3.0e-8)
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertEqual(
            links["bps_moduli_to_even_matter_selector"]["gate"],
            "silent_tangent_exists_but_is_not_selected",
        )
        self.assertEqual(
            links["bps_volume_constraint_to_selected_even_mode"]["gate"],
            "constraint_absent_exact_alignment_absent_and_level_set_sign_wrong",
        )

    def test_axisymmetric_gate_preserves_missing_source_failure(self) -> None:
        axisymmetric = self.registry["current_predictions"]["axisymmetric_collector"]
        self.assertTrue(axisymmetric["passes"])
        self.assertFalse(axisymmetric["physical_sparc_pde_identifiable"])
        self.assertEqual(
            axisymmetric["sparc_source_status"],
            "FAIL_CLOSED_MISSING_UNIQUE_3D_BARYON_SOURCE",
        )
        self.assertGreater(axisymmetric["coarse_to_fine_l2_ratio"], 3.5)
        self.assertGreater(axisymmetric["flattened_normalized_curl"], 1.0e-3)
        self.assertTrue(axisymmetric["all_defined_source_solves_converged"])
        self.assertFalse(axisymmetric["defined_source_physical_completion"])
        self.assertEqual(
            set(axisymmetric["defined_source_eligible_galaxies"]),
            {"NGC2403", "NGC3198"},
        )
        self.assertEqual(
            set(axisymmetric["defined_source_failed_galaxies"]),
            {"DDO154", "NGC2841"},
        )

    def test_eq39_is_recovered_without_calling_it_a_signal(self) -> None:
        em = self.registry["current_predictions"]["em_kernel"]
        self.assertTrue(em["eq39_coordinate_certificate"])
        self.assertGreater(em["legacy_max_abs_error_from_correct_u_kernel"], 0.3)
        self.assertIn("historical numerical kernel mixed", em["result"])

    def test_robin_and_double_comb_are_conditional_not_selected(self) -> None:
        robin = self.registry["current_predictions"]["robin_boundary_family"]
        fingerprint = self.registry["current_predictions"][
            "em_spectral_fingerprint"
        ]
        self.assertFalse(robin["physical_boundary_coefficients_selected"])
        self.assertLess(robin["ir_only_lightest_mass_ceiling"], 0.003)
        self.assertFalse(fingerprint["ell_fixed"])
        self.assertFalse(fingerprint["physical_branch_selected"])
        self.assertAlmostEqual(
            fingerprint["photon_positive_masses_mu"][0], 0.6525966736654073
        )

    def test_breathing_response_recovers_p6_and_is_not_a_detection(self) -> None:
        breathing = self.registry["current_predictions"]["breathing_response"]
        self.assertTrue(breathing["stiff_static_slice_recovered"])
        self.assertTrue(breathing["absolute_force_residues_available"])
        self.assertFalse(breathing["ell_fixed"])
        self.assertFalse(breathing["source_occupation_fixed"])
        self.assertFalse(breathing["physical_boundary_selected"])
        self.assertEqual(breathing["threshold_frequency_ratios"][0], 1.0)
        self.assertTrue(
            all(
                right > left
                for left, right in zip(
                    breathing["threshold_frequency_ratios"][:-1],
                    breathing["threshold_frequency_ratios"][1:],
                )
            )
        )

    def test_all_evidence_hashes_are_real(self) -> None:
        for row in self.registry["artefacts"].values():
            self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")
            self.assertFalse(row["path"].startswith("/"))

    def test_generated_file_matches_builder_when_present(self) -> None:
        if OUT_JSON.exists():
            disk = json.loads(OUT_JSON.read_text(encoding="utf-8"))
            self.assertEqual(disk, self.registry)


if __name__ == "__main__":
    unittest.main()
