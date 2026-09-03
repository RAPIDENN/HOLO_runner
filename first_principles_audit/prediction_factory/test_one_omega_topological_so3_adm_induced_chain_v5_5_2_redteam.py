#!/usr/bin/env python3
"""Independent adversarial tests for the additive v5.5.2 ADM red-team."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

if __package__:
    from . import derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam as red
else:
    import derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam as red


def test_redteam_does_not_import_primary_or_frozen_gate_helpers() -> None:
    tree = ast.parse(Path(red.__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = (
        "green_identity_v5_5_candidate_gate",
        "restricted_c1_n1_v5_6_gate",
        "adm_induced_chain_v5_5_2_gate",
    )
    assert not any(any(token in module for token in forbidden) for module in imported)
    assert red.build_payload()["primary_helpers_imported"] == []


def test_primary_is_byte_pinned_but_only_read_as_json() -> None:
    primary = red._load_primary()
    assert primary["schema"] == red.PRIMARY_SCHEMA
    assert red._sha256(red.PRIMARY_GENERATOR) == red.EXPECTED_PRIMARY_GENERATOR_SHA256
    assert red._sha256(red.PRIMARY_TEST) == red.EXPECTED_PRIMARY_TEST_SHA256
    assert red._sha256(red.PRIMARY_ARTIFACT) == red.EXPECTED_PRIMARY_ARTIFACT_SHA256
    assert primary["v5_2_source_binding"]["sha256"] == red.EXPECTED_V5_2_SHA256


def test_all_five_variational_coordinates_are_literal_and_unambiguous() -> None:
    ledger = red.coordinate_ledger()
    assert ledger["n"] == "n=δN/N"
    assert ledger["b_shift"] == "b_shift^i=δβ^i"
    assert ledger["q"] == "q_ij=δh_ij"
    assert ledger["omega"] == "omega=δOmegaSigma"
    assert ledger["v"] == "v_i=δpsi_i"
    assert "not autonomous" in ledger["metric_status"]
    assert ledger["primary_Robin_coordinate"].startswith("psi_i")
    assert "not b_shift" in ledger["BF_trace_disambiguation"]


def test_nontrivial_pullback_and_bidirectional_adm_jacobian_have_rank_ten() -> None:
    row = red.induced_jacobian_certificate()
    assert row["ambient_dimension"] == 5
    assert row["embedding_tangent_last_row_norm"] > 1.0e-2
    assert row["ambient_metric_inertia"] == {"negative": 1, "positive": 4}
    assert row["Y_star_g_error"] < 2.0e-14
    assert row["ADM_roundtrip_error"] < 2.0e-14
    assert row["Jacobian_rank"] == 10
    assert abs(row["Jacobian_determinant"]) > 1.0e-2
    assert row["complex_step_vs_closed_tangent_error"] < 2.0e-13
    assert row["inverse_chart_left_error"] < 2.0e-9
    assert row["inverse_chart_right_error"] < 2.0e-9
    assert row["closed_inverse_probe_max_error"] < 2.0e-14
    assert row["nonzero_shift_norm"] > 1.0e-2
    assert row["offdiagonal_metric_norm"] > 1.0e-2


def test_two_separately_written_action_routes_obey_the_chain_off_shell() -> None:
    row = red.action_chain_certificate()
    assert row["action_representation_error"] < 2.0e-13
    assert row["ADM_vs_gamma_gradient_chain_error"] < 2.0e-10
    assert row["directional_pairing_max_error"] < 2.0e-10
    assert row["projection_1_plus_3_plus_6_max_error"] < 2.0e-10
    assert row["minimum_active_ADM_gradient"] > 1.0e-4
    assert abs(row["E_Omega"]) > 1.0e-4
    assert min(abs(value) for value in row["E_psi"]) > 1.0e-4
    assert row["genuinely_off_shell"] is True


def test_bulk_matter_shift_has_visible_tui_but_wall_robin_does_not() -> None:
    row = red.matter_shift_certificate()
    assert row["minimum_absolute_T_ui_component"] > 1.0e-3
    assert row["T_ui_norm"] > 1.0e-2
    assert row["matter_shift_error"] < 2.0e-10
    assert row["omit_matter_current_witness"] > 1.0e-2
    assert row["flip_matter_current_sign_witness"] > 1.0e-2
    assert row["wall_Robin_direct_shift_norm"] < 2.0e-13
    assert row["fake_wall_Robin_shift_current_witness"] > 1.0e-2


def test_psi_coordinate_term_is_observed_from_action_not_presupposed() -> None:
    row = red.psi_coordinate_certificate()
    assert row["fixed_coordinate"] == "psi_i"
    assert row["coordinate_chain_error"] < 2.0e-10
    assert row["coordinate_term_norm"] > 1.0e-3
    assert row["omit_coordinate_term_witness"] > 1.0e-3
    assert row["flip_coordinate_term_witness"] > 1.0e-3


def test_one_plus_three_plus_six_slots_reconstruct_one_junction_tensor() -> None:
    row = red.israel_certificate()
    assert row["Brown_York_convention"] == "pi^mn=Theta^mn-Theta gamma^mn"
    assert row["junction_convention"] == "I^mn=M pi^mn-tau^mn"
    assert row["Jacobian_rank"] == 10
    assert row["projection_component_count"] == 10
    assert row["projection_reconstruction_error"] < 2.0e-10
    assert row["junction_norm"] > 1.0e-2
    assert min(row["slot_mutant_witnesses"].values()) > 1.0e-2
    assert row["autonomous_metric_mutant_witness"] > 1.0e-2
    assert row["Brown_York_sign_mutant_witness"] > 1.0e-2


def test_normal_embedding_is_h_equals_two_f_theta_with_the_same_pairing() -> None:
    row = red.normal_embedding_certificate()
    assert row["normal_metric_identity"] == "H_mn=2 f Theta_mn"
    assert row["H_identity_error"] < 2.0e-11
    assert row["H_norm"] > 1.0e-2
    assert row["I_contract_Theta_absolute"] > 1.0e-3
    assert row["normal_pairing_error"] < 2.0e-11
    assert row["omit_normal_bending_witness"] > 1.0e-2
    assert row["flip_normal_bending_sign_witness"] > 1.0e-2
    assert row["full_all_field_normal_embedding_claimed"] is False


def test_all_independent_mutants_have_nonzero_witnesses() -> None:
    witnesses = red.mutation_certificate()
    assert set(witnesses) == {
        "Jacobian_flip_lapse_sign",
        "Jacobian_omit_q_beta_terms",
        "Jacobian_autonomize_gamma_and_ADM",
        "chain_flip_gamma_route_sign",
        "chain_omit_shift_slot",
        "chain_omit_metric_slots",
        "chain_double_offdiagonal_gamma_slots",
        "matter_omit_T_ui",
        "matter_flip_T_ui_sign",
        "Robin_fake_shift_current",
        "psi_omit_coordinate_term",
        "psi_flip_coordinate_term",
        "Israel_autonomous_metric",
        "Israel_Brown_York_sign",
        "normal_omit_2fTheta",
        "normal_flip_2fTheta_sign",
        "Israel_omit_1_lapse_projection",
        "Israel_omit_3_shift_projections",
        "Israel_omit_6_spatial_projections",
        "Israel_flip_all_projection_signs",
    }
    assert min(witnesses.values()) > 1.0e-5


def test_decision_is_green_only_inside_the_declared_selected_scope() -> None:
    payload = red.build_payload()
    assert payload["decision"]["independent_redteam_checks_pass"] is True
    assert "selected local" in payload["scope_boundary"]["proved"]
    assert "complete v5.2" in payload["scope_boundary"]["still_red"]
    for key in red.FAIL_CLOSED_KEYS:
        assert payload["decision"][key] is False


def test_on_shell_or_inactive_replacement_fails_the_redteam_build(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = red.action_chain_certificate()
    inactive = json.loads(json.dumps(original))
    inactive["genuinely_off_shell"] = False
    inactive["minimum_active_ADM_gradient"] = 0.0
    monkeypatch.setattr(red, "action_chain_certificate", lambda: inactive)
    with pytest.raises(red.ADMInducedV552RedteamError, match="did not all pass"):
        red.build_payload()


def test_late_primary_change_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    real_sha256 = red._sha256

    def changed(path: Path) -> str:
        if path == red.PRIMARY_ARTIFACT:
            return "0" * 64
        return real_sha256(path)

    monkeypatch.setattr(red, "_sha256", changed)
    with pytest.raises(red.ADMInducedV552RedteamError, match="byte hash mismatch"):
        red.build_payload()


def test_artifact_is_byte_reproducible_and_provenance_bound() -> None:
    stored_bytes = red.OUTPUT.read_bytes()
    stored = json.loads(stored_bytes.decode("utf-8"))
    fresh = red.build_payload()
    expected_bytes = (
        json.dumps(fresh, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    assert stored == fresh
    assert stored_bytes == expected_bytes
    assert stored["provenance"]["generator_sha256"] == red._sha256(
        Path(red.__file__).resolve()
    )
    assert stored["provenance"]["test_sha256"] == red._sha256(red.TEST)
