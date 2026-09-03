#!/usr/bin/env python3
"""Adversarial tests for the sectorial topological SO(3) classical v5.2 gate."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

if __package__:
    from . import derive_one_omega_topological_so3_classical_v5_2_gate as gate
else:
    import derive_one_omega_topological_so3_classical_v5_2_gate as gate


def test_upstreams_are_directly_hash_bound_with_red_v5_1_and_green_material() -> None:
    rows = gate._load_upstreams()
    assert set(rows) == set(gate.UPSTREAMS)
    iso = rows["boundary_isomorphism_v5_1"]["decision"]
    assert iso["boundary_bundle_isomorphism_trivial_sector_pass"] is True
    assert iso["C1_ACTION_pass"] is False
    assert iso["N8_MATERIAL_PORT_pass"] is False
    material = rows["nonlinear_robin_full_V4"]["decision"]
    assert material["nonlinear_inhomogeneous_finite_q_material_BVP_pass"] is True
    assert material["canonical_time_dependent_material_Hamiltonian_positive"] is True


def test_one_action_is_literal_normalized_and_declares_every_field_class() -> None:
    charter = gate.exact_classical_charter(gate._load_upstreams())
    assert gate._contains_ellipsis(charter) is False
    assert charter["exact_action"]["total"].startswith("S_v5_2=")
    assert "S_X=0" in charter["exact_action"]["removed_terms"]
    pars = charter["coefficient_policy"]["parameters"]
    assert pars["kappa_BF_inner_product"] == 1.0
    assert pars["k_BF_trace_equivalent"] == -0.5
    assert pars["lambda_K"] == pytest.approx(-0.5535068954004245)
    assert "SO3 connection A_eps" in charter["independent_fields"]["bulk_each_side"]
    assert "adjoint-valued real three-form B_eps" in charter["independent_fields"]["bulk_each_side"]
    assert charter["BRST_BV_BFV_completion_included"] is False


def test_connection_and_material_gluing_are_transported_not_componentwise() -> None:
    charter = gate.exact_classical_charter(gate._load_upstreams())
    configuration = " ".join(charter["interface_domain"]["configuration"])
    assert "j_plus(Y_plus^*phi_plus)" in configuration
    assert "Trans_iota_plus(Y_plus^*A_plus)" in configuration
    assert "r*(Y^*A)*r^(-1)-(d r)*r^(-1)" in charter["definitions"]["connection_trace"]
    assert "Ad_r(Y^*B)" in charter["definitions"]["adjoint_form_trace"]


def test_metric_khronon_frame_and_Robin_variations_are_computed() -> None:
    frame = gate.frame_and_robin_variation_certificate()
    assert frame["linearized_u_norm_error"] < 2.0e-13
    assert frame["linearized_frame_spatiality_error"] < 2.0e-13
    assert frame["linearized_frame_orthonormality_error"] < 2.0e-13
    assert frame["Robin_finite_difference_error"] < 1.0e-9
    assert frame["vertical_frame_rotation_phi_cancellation_error"] < 2.0e-14
    assert frame["vertical_frame_rotation_acceleration_cancellation_error"] < 2.0e-14
    acceleration = gate.acceleration_variation_certificate()
    assert acceleration["finite_difference_error"] < 1.0e-9


def test_moving_pullbacks_use_covariant_connection_rule_and_transgression() -> None:
    row = gate.moving_pullback_certificate()
    assert row["finite_difference_error"] < 1.0e-9
    assert "delta A+i_xi F" in row["connection_material_variation"]
    assert "D_A(i_xi B)" in row["adjoint_form_material_variation"]
    assert row["separate_domain_transgression_added"] is False
    assert "double count" in row["reference_domain_convention"]


def test_BF_Green_form_requires_the_correct_oriented_incidence() -> None:
    row = gate.green_form_certificate()
    assert row["BF_boundary_form_error"] == 0.0
    assert row["BF_shift_boundary_form_error"] == 0.0
    assert row["BF_wrong_incidence_witness"] > 1.0e-2
    assert row["BF_shift_wrong_incidence_witness"] > 1.0e-2
    assert set(row["natural_interface_equations"]) == {
        "Israel",
        "Omega",
        "Robin",
        "BF_flux",
        "khronon",
    }
    assert row["complete_expanded_N4_junction_solution_claimed"] is False


def test_N8_transport_is_functional_all_direction_and_not_zero_equals_zero() -> None:
    upstream = gate._load_upstreams()["nonlinear_robin_full_V4"]
    row = gate.n8_functional_transport_certificate(upstream)
    assert row["derivative_intertwiner_max_error"] < 2.0e-13
    assert row["potential_argument_max_error"] < 2.0e-13
    assert row["V4_reference_value_max_error"] < 2.0e-14
    assert row["V4_prime_independent_finite_difference_max_error"] < 2.0e-9
    assert row["all_direction_SO3_current_max_norm"] < 2.0e-13
    assert row["manufactured_nonzero_scalar_residual_norm"] > 1.0e-2
    assert row["Euler_operator_intertwiner_max_error"] < 2.0e-13
    assert row["Robin_intertwiner_max_error"] < 2.0e-13
    assert row["global_periodic_null_homotopic_gauge_certificate_pass"] is True
    assert row["global_G_tangential_periodicity_max_error"] < 2.0e-13
    assert row["global_G_null_homotopy_identity_endpoint_error"] < 2.0e-14
    assert row["global_G_bulk_infinity_identity_error"] < 2.0e-14
    assert row["K_equals_dG_Ginverse_finite_difference_max_error"] < 2.0e-9
    assert row["Maurer_Cartan_components_checked"] == 6
    assert len(row["Maurer_Cartan_component_norms"]) == 6
    assert row["Maurer_Cartan_curvature_norm"] < 2.0e-9
    assert row["functional_energy_equality_error"] < 2.0e-12
    assert row["material_reduced_Hamiltonian_equality_error"] < 2.0e-12
    assert row["all_five_upstream_rows_converged"] is True
    assert row["all_upstream_row_parameters_match"] is True
    assert row["functional_transport_prerequisites_pass"] is True
    assert row["finite_q_material_solution_transported"] is True
    assert row["dynamic_gravity_claimed"] is False


def test_N8_old_missing_factor_wrong_sign_and_unsigned_shortcuts_fail() -> None:
    upstream = gate._load_upstreams()["nonlinear_robin_full_V4"]
    controls = gate.n8_functional_transport_certificate(upstream)["negative_controls"]
    assert controls["missing_Omega_minus_three_halves_witness"] > 1.0e-3
    assert controls["wrong_connection_sign_witness"] > 1.0e-3
    assert controls["wrong_Maurer_Cartan_sign_witness"] > 1.0e-3
    assert controls["absolute_value_would_destroy_signed_rows"] > 0
    assert controls["mismatched_boundary_G_witness"] > 1.0e-3
    assert controls["noncanonical_metric_conformal_factor_witness"] > 1.0e-3


def test_N8_rejects_a_global_G_whose_reported_K_is_not_dG_Ginverse(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gate,
        "_so3_exponential",
        lambda _generator, _parameter: np.eye(3),
    )
    row = gate.n8_functional_transport_certificate(
        gate._load_upstreams()["nonlinear_robin_full_V4"]
    )
    assert row["finite_q_material_solution_transported"] is False
    assert row["material_reduced_Hamiltonian_preserved"] is False
    with pytest.raises(RuntimeError, match="N8_is_a_full_functional"):
        gate.build_payload()


def test_N8_rejects_a_mutated_full_V4_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gate,
        "_v4",
        lambda value: np.zeros_like(np.asarray(value, dtype=float)),
    )
    row = gate.n8_functional_transport_certificate(
        gate._load_upstreams()["nonlinear_robin_full_V4"]
    )
    assert row["finite_q_material_solution_transported"] is False
    assert row["material_reduced_Hamiltonian_preserved"] is False
    with pytest.raises(RuntimeError, match="N8_is_a_full_functional"):
        gate.build_payload()


def test_N8_rejects_a_mutated_full_V4_derivative(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gate,
        "_v4_prime",
        lambda value: 17.0 * np.asarray(value, dtype=float) + 4.0,
    )
    row = gate.n8_functional_transport_certificate(
        gate._load_upstreams()["nonlinear_robin_full_V4"]
    )
    assert row["finite_q_material_solution_transported"] is False
    assert row["material_reduced_Hamiltonian_preserved"] is False
    with pytest.raises(RuntimeError, match="N8_is_a_full_functional"):
        gate.build_payload()


def test_decision_promotes_N8_but_keeps_C1_N1_on_moving_variation_hold() -> None:
    decision = gate.build_payload()["decision"]
    assert decision["exact_single_classical_action_candidate_charter_pass"] is True
    assert decision["full_classical_variational_principle_selected_sector_pass"] is False
    assert decision["N8_same_solution_functional_transport_theorem_pass"] is True
    assert decision["C1_ACTION_pass"] is False
    assert decision["N1_ACTION_pass"] is False
    assert decision["N8_MATERIAL_PORT_pass"] is True
    assert decision["dynamic_gravity_claimed"] is False
    assert decision["legacy_modes_or_CSV_reused"] is False
    for key in gate.FAIL_CLOSED_KEYS:
        assert decision[key] is False


def test_any_upstream_hash_mutation_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gate, "_sha256", lambda _path: "0" * 64)
    with pytest.raises(gate.ClassicalV52InputError, match="byte hash mismatch"):
        gate.build_payload()


def test_artifact_matches_fresh_payload_and_provenance() -> None:
    stored = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
    fresh = gate.build_payload()
    assert stored == fresh
    assert stored["provenance"]["generator"]["sha256"] == gate._sha256(
        Path(gate.__file__).resolve()
    )
    assert stored["provenance"]["test"]["sha256"] == gate._sha256(gate.TEST)
