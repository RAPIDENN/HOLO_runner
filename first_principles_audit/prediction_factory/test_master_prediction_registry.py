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

    def test_post_campaign_dirac_branch_stops_at_static_spectral_level(self) -> None:
        band = self.registry["current_predictions"]["c2_band_edge_continuum"]
        self.assertAlmostEqual(band["pressure_log_slope"], 1.5, places=11)
        self.assertTrue(band["exact_exponent_derived"])
        self.assertFalse(band["required_variational_sign_derived"])
        self.assertFalse(band["candidate_survives"])
        self.assertEqual(band["raw_observational_tables_read_directly"], [])
        self.assertEqual(band["inherited_target_origin"], "SPARC training split only")

        candidate = self.registry["current_predictions"][
            "dirac_critical_bath_gate"
        ]
        self.assertTrue(candidate["uniform_static_spectral_candidate"])
        self.assertFalse(candidate["finite_local_qft_realization_exhibited"])
        self.assertFalse(
            candidate["exact_exposed_collector_interpolation_reproduced"]
        )
        self.assertEqual(candidate["inherited_target_origin"], "SPARC training split only")
        self.assertFalse(candidate["physical_completion"])
        self.assertFalse(candidate["publication_authorized"])

        red_team = self.registry["current_predictions"]["dirac_bath_red_team"]
        self.assertEqual(red_team["threat_count"], 17)
        self.assertEqual(
            red_team["highest_level_passed"], "L1_uniform_static_spectral"
        )
        self.assertEqual(red_team["first_blocked_level"], "L2_finite_local_QFT")
        self.assertTrue(red_team["static_spectral_construction_survives"])
        self.assertFalse(red_team["finite_local_qft_survives"])
        self.assertFalse(red_team["causal_covariant_completion_survives"])
        self.assertFalse(red_team["current_holo_mechanism"])
        self.assertFalse(red_team["physical_completion"])
        self.assertFalse(red_team["publication_authorized"])

        links = {row["id"]: row for row in self.registry["links"]}
        self.assertEqual(
            links["minimal_campaign_to_band_edge_negative_control"]["gate"],
            "killed_wrong_AQUAL_variational_sign",
        )
        self.assertEqual(
            links["dirac_static_candidate_to_red_team_map"]["gate"],
            "first_blocked_level_L2_finite_local_QFT",
        )

    def test_covariant_origin_and_khronon_gates_stop_before_same_action_completion(self) -> None:
        origin = self.registry["current_predictions"][
            "covariant_5d_pseudogap_gate"
        ]
        self.assertFalse(origin["current_regular_compact_origin_survives"])
        self.assertTrue(origin["covariant_lifshitz_scaling_background_exhibited"])
        self.assertTrue(origin["effective_linear_state_counting_exponent_derived"])
        self.assertFalse(origin["literal_boundary_single_particle_DOS_derived"])
        self.assertFalse(origin["same_action_exact_Clifford_determinant_derived"])
        self.assertFalse(origin["quadratic_matching_Ward_protected"])
        self.assertFalse(origin["complete_constraint_and_time_stability"])
        self.assertFalse(origin["current_holo_mechanism"])
        self.assertFalse(origin["physical_completion"])
        self.assertFalse(origin["publication_authorized"])

        stability = self.registry["current_predictions"][
            "khronon_constraint_stability_gate"
        ]
        self.assertTrue(stability["geometric_critical_matching_rule_derived"])
        self.assertTrue(stability["exact_static_mu_from_Schur"])
        self.assertTrue(stability["static_effective_function_convex"])
        self.assertTrue(stability["local_lapse_constraint_rank_preserved"])
        self.assertEqual(stability["khronometric_gravitational_DOF"], 6)
        self.assertGreater(stability["minimum_lapse_symbol"], 0.0)
        self.assertLess(stability["maximum_Schur_mu_error"], 3.0e-15)
        self.assertFalse(stability["old_internal_quadratic_cancellation_required"])
        self.assertFalse(stability["same_action_local_5D_microscopic_bath_derived"])
        self.assertFalse(stability["fine_tuning_eliminated"])
        self.assertFalse(stability["same_5D_action_and_background_closed"])
        self.assertTrue(
            stability["truncated_z2_kernel_has_no_upper_half_plane_poles"]
        )
        self.assertFalse(stability["full_microscopic_retarded_kernel_derived"])
        self.assertFalse(stability["full_warped_brane_constraints_derived"])
        self.assertFalse(stability["complete_time_dependent_stability"])
        self.assertFalse(stability["physical_completion"])
        self.assertFalse(stability["publication_authorized"])

        links = {row["id"]: row for row in self.registry["links"]}
        self.assertEqual(
            links["dirac_red_team_to_covariant_5d_origin_gate"]["gate"],
            "L2_scaling_pass_L3_same_action_determinant_blocked",
        )
        self.assertEqual(
            links["covariant_5d_origin_to_khronon_geometric_matching"]["gate"],
            "K2_local_rank_pass_K4_retarded_and_K5_warped_blocked",
        )

    def test_bulk_z2_gate_closes_static_and_flat_banded_only(self) -> None:
        gate = self.registry["current_predictions"][
            "bulk_z2_clifford_completion_gate"
        ]
        self.assertTrue(gate["same_action_local_5D_Gaussian_static_bath_derived"])
        self.assertTrue(gate["UV_finite_static_completion_without_hard_cutoff"])
        self.assertTrue(gate["literal_bulk_single_particle_linear_DOS_derived"])
        self.assertTrue(gate["fundamental_flat_constraint_rank_preserved"])
        self.assertEqual(gate["spatial_dimensions"], 4)
        self.assertEqual(gate["khronometric_gravitational_DOF"], 6)
        self.assertTrue(
            gate["full_flat_finite_band_gaussian_retarded_kernel_derived"]
        )
        self.assertTrue(gate["retarded_branch_cut_resolved"])
        self.assertTrue(gate["exact_metric_lapse_Schur_complement_retained"])
        self.assertTrue(gate["critical_linear_flat_scalar_has_no_UHP_poles"])
        self.assertTrue(
            gate[
                "flat_background_linear_time_stability_complete_for_frozen_banded_model"
            ]
        )
        self.assertIn("C_R=eta_infinity+Pi_R/M5^3", gate["exact_Schur_critical_inverse"])
        self.assertIn("Delta_eta=2*K2/M5^3", gate["critical_relation"])
        self.assertAlmostEqual(
            gate["quadratic_increment_Delta_eta"],
            2.0 * gate["matter_quadratic_coefficient_K2"] / gate["planck5_cubed"],
        )

        self.assertFalse(gate["finite_band_regulator_from_local_UV_completion"])
        self.assertFalse(gate["same_action_local_UV_full_retarded_kernel_derived"])
        self.assertFalse(gate["minimal_same_action_UV_dynamics_survives"])
        self.assertEqual(
            gate["same_action_dynamic_status"],
            "KILL_MINIMAL_SAME_ACTION_GLOBAL_RETARDED_UV_COMPLETION",
        )
        self.assertGreater(
            gate["same_action_continuum_UHP_pole"],
            gate["same_action_continuum_lapse_zero"],
        )
        self.assertTrue(
            gate["same_action_finite_q_requires_gradient_counterterm"]
        )
        self.assertAlmostEqual(gate["finite_compact_strict_IR_DOS_power"], 0.5)
        self.assertAlmostEqual(gate["finite_compact_strict_IR_sea_power"], 2.5)
        self.assertFalse(gate["finite_compact_HOLO_strict_IR_cubic_survives"])
        self.assertEqual(
            gate["original_Lifshitz_background_status"],
            "KILL_NAIVE_ISOTROPIC_ORIGINAL_LIFSHITZ_BULK_ROUTE",
        )
        self.assertGreater(gate["original_Lifshitz_fermion_background_gap"], 0.0)
        self.assertFalse(
            gate["naive_isotropic_original_Lifshitz_background_route_survives"]
        )
        self.assertFalse(
            gate["gapless_radial_continuum_with_4D_gravity_localization_derived"]
        )
        self.assertFalse(gate["critical_matching_Ward_protected"])
        self.assertFalse(gate["nonlinear_global_time_stability_derived"])
        self.assertFalse(gate["warped_background_residuals_closed"])
        self.assertFalse(gate["warped_junction_conditions_closed"])
        self.assertFalse(gate["full_channel_QNM_spectrum_closed"])
        self.assertFalse(gate["current_compact_HOLO_completed"])
        self.assertFalse(gate["new_force_derived"])
        self.assertFalse(gate["lensing_derived"])
        self.assertFalse(gate["physical_completion"])
        self.assertFalse(gate["publication_authorized"])

        links = {row["id"]: row for row in self.registry["links"]}
        link = links["khronon_matching_to_bulk_z2_clifford_completion"]
        self.assertEqual(
            link["status"],
            "same_action_local_static_pass_separate_flat_banded_exact_schur_pass",
        )
        self.assertEqual(link["gate"], "Z0_Z4_pass_Z5_killed_Z6_blocked")
        self.assertIn("exact metric/lapse Schur", link["meaning"])
        self.assertIn("No force or lensing follows", link["meaning"])
        evidence = self.registry["artefacts"]["bulk_z2_clifford_completion_gate"]
        self.assertTrue(evidence["path"].endswith("bulk_z2_clifford_completion_gate.json"))

    def test_brane_tilted_semimetal_advances_same_action_gate_only(self) -> None:
        gate = self.registry["current_predictions"][
            "brane_tilted_semimetal_gate"
        ]
        self.assertTrue(gate["local_covariant_5D_defect_matter_ansatz_exhibited"])
        self.assertTrue(gate["literal_three_space_linear_DOS_derived"])
        self.assertTrue(
            gate[
                "bounded_below_Hamiltonian_and_finite_occupied_region_from_same_ansatz"
            ]
        )
        self.assertTrue(
            gate["exact_static_bracket_from_same_finite_occupied_region"]
        )
        self.assertTrue(
            gate[
                "prescribed_constant_radius_radial_acceleration_projected_out"
            ]
        )
        self.assertFalse(gate["ordinary_radial_KK_linear_DOS_required"])
        self.assertEqual(gate["director_count"], 3)
        self.assertEqual(gate["negative_branches"], 6)
        self.assertIn("epsilon/(8*pi*c*v)", gate["linear_three_space_DOS"])
        self.assertIn("eta_infinity+Pi_zero/M4^2", gate["critical_relation"])
        self.assertAlmostEqual(
            gate["quadratic_increment_Delta_eta"],
            gate["Pi_zero"] / gate["brane_Planck_squared"],
        )

        self.assertTrue(gate["fixed_charge_sector_required"])
        self.assertFalse(gate["fixed_charge_sector_dynamically_selected"])
        self.assertFalse(
            gate["inhomogeneous_fixed_charge_local_functional_derived"]
        )
        self.assertTrue(gate["same_ansatz_q0_acceleration_retarded_kernel_derived"])
        self.assertTrue(gate["same_ansatz_q0_acceleration_positive_spectral_measure"])
        self.assertTrue(
            gate[
                "reduced_brane_long_wavelength_Schur_has_no_UHP_poles"
            ]
        )
        self.assertIn("Re[D(p,q)/p]>0", gate["reduced_brane_q0_Schur"])
        self.assertTrue(
            gate[
                "same_ansatz_finite_q_acceleration_block_positive_Kubo_representation_derived"
            ]
        )
        self.assertTrue(gate["finite_q_sampled_static_response_below_q0"])
        self.assertFalse(
            gate[
                "full_q_all_vertex_global_Schur_stability_derived"
            ]
        )
        self.assertFalse(gate["metric_and_density_intraband_channels_included"])
        self.assertFalse(gate["continuous_SO3_dynamical_isotropy_derived"])
        self.assertFalse(gate["full_brane_constraint_and_junction_rank_derived"])
        self.assertFalse(gate["warped_backreacted_solution_derived"])
        self.assertFalse(gate["new_force_derived"])
        self.assertFalse(gate["lensing_derived"])
        self.assertFalse(gate["physical_completion"])
        self.assertFalse(gate["publication_authorized"])

        levels = {row["level"]: row["status"] for row in gate["acceptance_ladder"]}
        self.assertEqual(
            levels["B3_same_ansatz_q0_acceleration_retarded_kernel"], "PASS"
        )
        self.assertEqual(levels["B4_full_q_global_Schur_and_SO3"], "BLOCKED")
        self.assertEqual(
            levels["B5_warped_constraints_junctions_backreaction"], "BLOCKED"
        )
        self.assertEqual(levels["B6_force_matter_lensing"], "NOT_ENTERED")

        links = {row["id"]: row for row in self.registry["links"]}
        link = links["bulk_z2_to_brane_tilted_semimetal_completion"]
        self.assertEqual(
            link["status"],
            "same_ansatz_defect_static_and_q0_acceleration_retarded_pass",
        )
        self.assertEqual(link["gate"], "B0_B3_pass_B4_B5_blocked_B6_not_entered")
        self.assertIn("Fixed filling is declared", link["meaning"])
        self.assertIn("No force or lensing follows", link["meaning"])
        evidence = self.registry["artefacts"]["brane_tilted_semimetal_gate"]
        self.assertTrue(evidence["path"].endswith("brane_tilted_semimetal_gate.json"))

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
