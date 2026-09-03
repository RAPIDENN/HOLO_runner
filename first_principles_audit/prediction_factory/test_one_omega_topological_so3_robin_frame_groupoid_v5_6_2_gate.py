#!/usr/bin/env python3
"""Strict tests for the independent Robin/frame/groupoid corrective gate."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np

if __package__:
    from . import derive_one_omega_topological_so3_robin_frame_groupoid_v5_6_2_gate as gate
else:
    import derive_one_omega_topological_so3_robin_frame_groupoid_v5_6_2_gate as gate


def _artifact() -> dict:
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def test_artifact_is_fresh_and_deterministic() -> None:
    assert gate.OUTPUT.exists()
    assert _artifact() == gate.build_payload()


def test_module_does_not_import_primary_or_prior_ward_helpers() -> None:
    source = Path(gate.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any("full_moving_c1_n1_v5_6_2" in name for name in imported)
    assert not any("full_action_gauge_noether" in name for name in imported)
    assert gate.build_payload()["provenance"]["primary_v5_6_2_helpers_imported"] == []


def test_primary_bytes_theta_profiles_and_scope_are_exactly_pinned() -> None:
    payload = _artifact()
    contract = payload["literal_input"]["primary_v5_6_2_identity_and_scope_pin_only"]
    assert contract["sha256"] == gate.V562_PINS
    assert contract["decision_boolean_consumed"] is False
    assert contract["Eulerian_or_residual_consumed"] is False
    assert contract["primary_helper_imported_or_called"] is False
    assert contract["profiles_AST_executed"] is False
    assert contract["profiles_AST_sha256"] == gate.PRIMARY_PROFILES_AST_SHA256
    family = payload["primary_v5_6_2_family_contract"]
    assert family["profile_sample_sha256"] == gate.PRIMARY_PROFILE_SAMPLE_SHA256
    assert family["primary_parameter_order"] == list(gate.PRIMARY_PARAMETER_ORDER)
    assert family["primary_theta"] == gate.PRIMARY_THETA.tolist()
    assert family["scope"] == gate.PRIMARY_SCOPE


def test_chosen_local_frame_is_oriented_orthonormal_and_spatial() -> None:
    raw = _artifact()["frame_and_groupoid_invariants"]
    assert max(raw.values()) < 2.0e-12
    assert raw["sqrt_minus_gamma_det_u_E_minus_one_Linf"] < 2.0e-12
    assert _artifact()["checks"][
        "chosen_coordinate_adapted_Q_frame_from_induced_gamma_T_pass"
    ] is True


def test_source_groupoid_ward_and_right_left_sign_mutants() -> None:
    payload = _artifact()
    raw = payload["source_P_groupoid_Ward"]["raw"]
    assert raw["delta_varphi_Linf"] < 2.0e-13
    assert abs(raw["central_direct_Robin_derivative"]) < 2.0e-9
    assert abs(raw["Euler_pairing"]) < 2.0e-12
    assert set(raw["mutants"]) == {
        "omit_delta_R",
        "wrong_left_compensation",
        "wrong_source_sign",
    }
    for mutant in raw["mutants"].values():
        assert abs(mutant["central_direct_derivative"]) > 1.0e-5
        assert abs(
            mutant["central_direct_derivative"] - mutant["Euler_pairing"]
        ) < 2.0e-8
    assert payload["checks"]["source_P_groupoid_Robin_Ward_pass"] is True


def test_target_r_and_frame_ward_with_fixed_and_wrong_sign_mutants() -> None:
    payload = _artifact()
    raw = payload["target_Q_frame_Ward"]["raw"]
    assert raw["delta_spacetime_varphi_Linf"] < 2.0e-13
    assert abs(raw["central_direct_Robin_derivative"]) < 2.0e-9
    assert abs(raw["Euler_pairing"]) < 2.0e-12
    assert raw["delta_R_phi_minus_hat_q_varphi_Linf"] < 2.0e-13
    assert raw["finite_R_minus_gQ_R_Linf"] < 2.0e-13
    assert raw["finite_target_gauge_frame_orthonormality_Linf"] < 2.0e-12
    assert set(raw["mutants"]) == {"fixed_frame", "wrong_target_frame_sign"}
    for mutant in raw["mutants"].values():
        assert abs(mutant["central_direct_derivative"]) > 1.0e-5
        assert abs(
            mutant["central_direct_derivative"] - mutant["Euler_pairing"]
        ) < 2.0e-8
    assert payload["checks"]["target_Q_frame_Robin_Ward_pass"] is True


def test_combined_finite_and_infinitesimal_p_q_action() -> None:
    payload = _artifact()
    raw = payload["combined_P_Q_groupoid_Ward"]["raw"]
    assert raw["delta_E_R_phi_Linf"] < 2.0e-13
    assert abs(raw["central_direct_Robin_derivative"]) < 2.0e-9
    assert abs(raw["Euler_pairing"]) < 2.0e-12
    assert abs(raw["finite_combined_action_difference_at_scale_0_17"]) < 2.0e-12
    mutant = raw["target_inverse_R_mutant"]
    assert abs(mutant["central_direct_derivative"]) > 1.0e-5
    assert abs(mutant["central_direct_derivative"] - mutant["Euler_pairing"]) < 2.0e-8
    assert payload["checks"]["combined_P_Q_groupoid_Robin_Ward_pass"] is True


def test_selected_metric_embedding_omega_matter_jvps_match_fd() -> None:
    payload = _artifact()
    certificate = payload["selected_family_JVP_FD"]
    assert certificate["parameter_order"] == list(gate.PARAMETER_NAMES)
    assert certificate["maximum_raw_JVP_FD_error"] < 2.0e-7
    assert certificate["minimum_absolute_action_JVP"] > 1.0e-5
    assert certificate["routes_share_same_literal_action_evaluator"] is True
    assert certificate["independent_action_reconstruction_claimed"] is False
    for name in gate.PARAMETER_NAMES:
        assert abs(certificate["raw_rows"][name]["raw"]["action"]["complex_step_JVP"]) > 1.0e-5


def test_primary_r_identity_value_and_jvp_align_but_orbit_was_incomplete() -> None:
    payload = _artifact()
    alignment = payload["primary_R_identity_alignment_and_orbit_gap"]
    assert alignment["aligned_R_identity_action_compatible"] is True
    assert abs(alignment["aligned_R_identity_minus_primary_action"]) < 2.0e-12
    assert alignment["maximum_absolute_aligned_R_identity_JVP_difference"] < 2.0e-10
    assert abs(alignment["nontrivial_R_minus_primary_configuration_difference"]) > 1.0e-5
    assert "omit-delta-R mutant" in alignment["consequence"]


def test_c1_n1_and_larger_claims_remain_fail_closed() -> None:
    checks = _artifact()["checks"]
    assert all(checks[key] is False for key in gate.FAIL_CLOSED_KEYS)
    assert checks["C1_pass"] is False
    assert checks["N1_pass"] is False
    assert checks["C1_N1_promotion_pass"] is False
    assert checks["passive_Phase_A_J_disengaged_pass"] is False
    assert checks["LOCK_1_contamination_cleared_pass"] is False
    assert checks["publication_authorized"] is False
    assert checks["unrestricted_large_gauge_sector_pass"] is False
    assert checks["C1_ACTION_pass"] is False
    assert checks["N1_ACTION_pass"] is False
    assert checks["full_variational_principle_pass"] is False


def test_two_sided_master_is_only_a_contract_and_stays_red() -> None:
    payload = _artifact()
    contract = payload["two_sided_master_contract_not_executed"]
    assert contract["executed_here"] is False
    assert "R_+" in contract["solders"] and "R_-" in contract["solders"]
    assert any("non-Z2" in item for item in contract["future_master_obligations"])
    checks = payload["checks"]
    assert checks["two_sided_distinct_R_plus_R_minus_execution_pass"] is False
    assert checks["non_Z2_two_sided_interface_pass"] is False
    assert checks["two_sided_groupoid_master_integration_pass"] is False


def test_groupoid_solder_is_not_fixed_axis_phi() -> None:
    state = gate.selected_state(gate.THETA)
    reconstructed = np.einsum("...ab,...b->...a", state["R"], state["phi"])
    assert np.max(np.abs(state["varphi"] - reconstructed)) < 2.0e-15
    assert np.max(np.abs(state["varphi"] - state["phi"])) > 1.0e-3
