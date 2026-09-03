#!/usr/bin/env python3
"""Adversarial tests for the additive full-action Ward v5.5.3 gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

if __package__:
    from . import derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate as gate
else:
    import derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate as gate


def test_v5_2_full_action_schema_hash_literals_and_coefficients_are_exact() -> None:
    payload = gate.build_payload()
    pinned = payload["pinned_v5_2"]
    assert pinned["sha256"] == gate.EXPECTED_V5_2_SHA256
    assert pinned["schema"] == gate.EXPECTED_V5_2_SCHEMA
    assert pinned["literal_actions"] == gate.EXPECTED_ACTIONS
    assert pinned["coefficients"] == gate.EXPECTED_COEFFICIENTS
    assert set(pinned["literal_actions"]) == {
        "BF",
        "GHY",
        "Robin_intrinsic",
        "bulk_gauged",
        "bulk_potential",
        "foliation_lower",
        "full_V4",
        "gauged_conformal_derivative",
        "removed_terms",
        "superpotential",
        "total",
        "wall_background",
    }


def test_v5_5_2_is_hash_bound_only_as_explicit_adm_controls() -> None:
    row = gate.build_payload()["pinned_v5_5_2_ADM_controls"]
    assert row["sha256"] == gate.EXPECTED_V5_5_2_SHA256
    assert row["literal_slots"] == {
        "omega": "omega=δOmegaSigma",
        "v": "v_i=δpsi_i",
        "b_shift": "b_shift^i=δβ^i",
    }
    assert row["ADM_Jacobian_rank"] == 10
    assert row["Israel_projection_reconstruction_error"] < 1.0e-10
    assert row["matter_T_ui_norm"] > 1.0e-3
    assert all(row["imported_control_flags"].values())
    assert "no inherited Ward boolean" in row["scope"]


def test_real_exterior_form_degrees_have_no_spectator_coordinate() -> None:
    certificate = gate.full_action_certificate()
    row = certificate["form_degree_contract"]
    assert row["ambient_dimension"] == 5
    assert row["bulk_grid_shape"] == [7, 7, 7, 7, 7]
    assert row["interface_grid_shape"] == [7, 7, 7, 7]
    assert row["dealiasing_claimed"] is False
    assert row["active_coordinates"] == ["x0", "x1", "x2", "x3", "x4"]
    assert row["A"] == {"degree": 1, "independent_components": 5}
    assert row["B"] == {"degree": 3, "independent_components": 10}
    assert row["F_and_E_B"] == {"degree": 2, "independent_components": 10}
    assert row["D_B_J_and_E_A"] == {"degree": 4, "independent_components": 5}
    assert row["W"] == {"degree": 5, "independent_components": 1}
    assert row["dimensional_reduction_or_spectator_ansatz_used"] is False
    for side in certificate["bulk_sides"].values():
        for derivatives in side["five_coordinate_activity"].values():
            assert len(derivatives) == 5
            assert min(derivatives) > 1.0e-4


def test_every_bulk_sector_is_active_and_euler_follows_full_action() -> None:
    for side in gate.full_action_certificate()["bulk_sides"].values():
        sectors = side["action_sectors"]
        assert set(sectors) == {
            "Einstein_Hilbert",
            "Omega_kinetic",
            "Omega_superpotential",
            "matter_kinetic",
            "matter_full_V4",
            "BF",
            "total",
        }
        assert min(abs(value) for key, value in sectors.items() if key != "total") > 1.0e-5
        assert set(side["action_to_Euler"]) == {
            "A_only",
            "B_only",
            "phi_only",
            "A_B_phi",
        }
        for row in side["action_to_Euler"].values():
            assert row["absolute_error"] < 2.0e-6
            assert row["coarse_step"] == 4.0e-5
            assert row["fine_step"] == 2.0e-5
            assert row["step_convergence_difference"] < 2.0e-5
            assert row["active_magnitude"] > 1.0e-4


def test_five_form_ward_closes_off_shell_on_both_sides() -> None:
    for side in gate.full_action_certificate()["bulk_sides"].values():
        row = side["Ward"]
        assert row["L2_residual"] < 5.0e-4
        assert row["Linf_residual"] < 2.0e-3
        assert min(row["term_L2_norms"].values()) > 1.0e-4
        assert set(row["per_generator"]) == {"W_1", "W_2", "W_3"}
        assert min(side["off_shell_Euler_norms"].values()) > 1.0e-4


def test_curvature_bianchi_and_material_current_close_separately() -> None:
    residuals = []
    mutants = []
    for side in gate.full_action_certificate()["bulk_sides"].values():
        rows = side["separated_structural_identities"]
        curvature = rows["D_A_squared_B"]
        assert curvature["identity"] == (
            "D_A^2 B=[F,B]:=F cross-wedge B=-B cross-wedge F"
        )
        assert curvature["L2_residual"] < 5.0e-4
        assert curvature["Linf_residual"] < 2.0e-3
        assert curvature["D_A_squared_B_L2"] > 1.0e-4
        assert curvature["F_cross_B_L2"] > 1.0e-4
        assert curvature["flip_curvature_commutator_sign_mutant_L2"] > 1.0e-4
        residuals.append(curvature["L2_residual"])
        mutants.append(curvature["flip_curvature_commutator_sign_mutant_L2"])

        bianchi = rows["D_A_F_Bianchi"]
        assert bianchi["component_count"] == 10
        assert bianchi["L2_residual"] < 5.0e-4
        assert bianchi["Linf_residual"] < 2.0e-3
        assert bianchi["ordinary_d_instead_of_D_A_mutant_L2"] > 1.0e-4
        residuals.append(bianchi["L2_residual"])
        mutants.append(bianchi["ordinary_d_instead_of_D_A_mutant_L2"])

        matter = rows["material_current"]
        assert matter["L2_residual"] < 5.0e-4
        assert matter["Linf_residual"] < 2.0e-3
        assert matter["D_A_J_A_L2"] > 1.0e-4
        assert matter["matter_moment_L2"] > 1.0e-4
        assert set(matter["per_generator"]) == {
            "W_material_1",
            "W_material_2",
            "W_material_3",
        }
        for generator in matter["per_generator"].values():
            assert generator["L2"] < 5.0e-4
            assert generator["Linf"] < 2.0e-3
        assert matter["flip_J_A_sign_mutant_L2"] > 1.0e-4
        residuals.append(matter["L2_residual"])
        mutants.append(matter["flip_J_A_sign_mutant_L2"])
    assert min(mutants) / max(residuals) > 10.0


def test_full_matter_has_omega_c_metric_signs_and_radial_v4() -> None:
    for side in gate.full_action_certificate()["bulk_sides"].values():
        row = side["matter"]
        assert row["Omega_minimum"] > 0.0
        assert row["Omega_maximum"] > row["Omega_minimum"]
        assert row["c_covector_L2"] > 1.0e-4
        assert row["P_covector_L2"] > 1.0e-4
        assert row["radial_V4_E_phi_L2"] > 1.0e-4
        assert row["radial_V4_moment_L2"] < 1.0e-12
        assert row["rho_zero_extension_Linf"] == 0.0
        assert row["anisotropic_V4_mutant_E_phi_L2"] > 1.0e-4
        assert row["anisotropic_V4_mutant_moment_L2"] > 1.0e-4


def test_required_bulk_mutants_and_circular_euler_are_rejected() -> None:
    required = {
        "omit_BF_from_Euler_action_mismatch",
        "omit_E_B_from_W",
        "omit_J_from_E_A",
        "omit_material_E_phi",
        "omit_c_M_P_M_in_E_phi",
        "omit_c_phi_from_P_action_mismatch",
        "flip_J_A_sign",
        "flip_D_A_E_A_sign",
        "flip_E_B_sign",
        "abelianize_D_A_and_curvature_terms",
        "omit_radial_V4_from_Euler_action_mismatch",
    }
    sides = gate.full_action_certificate()["bulk_sides"]
    for side in sides.values():
        assert set(side["mutant_witnesses"]) == required
        assert min(side["mutant_witnesses"].values()) > 1.0e-4
        circular = side["circular_Euler_detector"]
        assert circular["forced_W_L2"] < 1.0e-15
        assert circular["actual_D_of_zero_E_A_vs_forced_D_L2"] > 1.0e-4
        assert circular["action_to_circular_Euler_mismatch"] > 1.0e-4
    minimum_mutant = min(
        value for side in sides.values() for value in side["mutant_witnesses"].values()
    )
    maximum_nominal = max(side["Ward"]["L2_residual"] for side in sides.values())
    assert minimum_mutant / maximum_nominal > 10.0


def test_compact_lambda_is_first_and_noninvariant_v4_breaks_gauge_ward() -> None:
    row = gate.full_action_certificate()["compact_lambda_first"]
    assert row["compact_lambda_is_first"] is True
    for side in row["sides"]:
        assert 0.0 < side["support_fraction"] < 0.5
        assert side["boundary_trace_max"] < 1.0e-14
        assert min(side["three_generator_L2"]) > 1.0e-5
        assert abs(side["direct_full_action_derivative"]) < 2.0e-6
        assert abs(side["Euler_pairing"]) < 2.0e-6
        assert side["direct_vs_Euler_error"] < 2.0e-6
        assert abs(side["anisotropic_V4_mutant_direct_gauge_derivative"]) > 1.0e-4


def test_all_literal_interface_terms_are_executed_on_actual_khronon_geometry() -> None:
    row = gate.full_action_certificate()["interface_4D"]["all_literal_interface_terms"]
    assert row["terms"] == ["GHY", "wall_background", "foliation_lower", "Robin_intrinsic"]
    assert row["minimum_sector_activity"] > 1.0e-5
    assert row["frame_orthonormality_error"] < 1.0e-10
    assert row["khronon_unit_norm_error"] < 1.0e-10
    assert row["gauge_neutral_without_internal_indices"] == [
        "GHY",
        "wall_background",
        "foliation_lower",
    ]


def test_source_groupoid_variation_keeps_traces_and_robin_invariant() -> None:
    row = gate.full_action_certificate()["interface_4D"]["source_P_gauge_groupoid"]
    assert row["convention"]["delta_R"] == "-R hat(lambda), with Q fixed"
    assert max(row["trace_derivative_L2"].values()) < 5.0e-5
    assert abs(row["Robin_direct_derivative"]) < 2.0e-7
    assert abs(row["Robin_Euler_pairing"]) < 2.0e-7
    assert abs(row["omit_delta_R_mutant_direct_derivative"]) > 1.0e-4
    assert abs(row["omit_delta_R_mutant_Euler_pairing"]) > 1.0e-4


def test_target_q_frame_and_varphi_transform_together() -> None:
    row = gate.full_action_certificate()["interface_4D"]["target_Q_frame_Ward"]
    assert abs(row["direct_derivative"]) < 2.0e-7
    assert abs(row["Euler_pairing"]) < 2.0e-7
    assert abs(row["frame_fixed_mutant_direct_derivative"]) > 1.0e-4


def test_boundary_green_records_charge_exact_and_material_current_separately() -> None:
    row = gate.full_action_certificate()["boundary_Green_and_BFV"][
        "boundary_Green_identity"
    ]
    assert row["formula"] == "Theta_gauge-<lambda,E_A>=-d_boundary<B lambda>"
    assert row["Theta_BF_L2"] > 1.0e-4
    assert row["Theta_matter_current_L2"] > 1.0e-4
    assert row["E_A_material_current_trace_L2"] > 1.0e-4
    assert row["charge_3form_L2"] > 1.0e-4
    assert row["exact_4form_L2"] > 1.0e-4
    assert row["identity_L2_residual"] < 2.0e-10
    assert row["identity_Linf_residual"] < 2.0e-9
    assert row["omit_matter_from_Theta_mutant_L2"] > 1.0e-4
    assert row["omit_material_J_from_E_A_mutant_L2"] > 1.0e-4


def test_interface_lambda_gluing_and_unglued_bfv_residual_are_distinct() -> None:
    row = gate.full_action_certificate()["boundary_Green_and_BFV"][
        "interface_lambda_and_BFV"
    ]
    assert row["lambda_interface_L2"] > 1.0e-4
    assert row["oriented_signs"] == {"plus": 1, "minus": -1}
    assert row["selected_local_trace_gluing_defect_L2"] < 1.0e-12
    assert row["selected_glued_BFV_residual_L2"] < 1.0e-12
    assert row["unglued_defect_L2"] > 1.0e-4
    assert row["unglued_BFV_residual_L2"] > 1.0e-4
    assert row["global_or_large_gauge_gluing_claimed"] is False
    assert row["complete_BV_BFV_boundary_complex_claimed"] is False


def test_diffeomorphism_khronon_attempt_is_honestly_incomplete() -> None:
    row = gate.full_action_certificate()["diffeomorphism_khronon_attempt"]
    assert row["maximum_bulk_translation_action_difference"] < 1.0e-8
    assert row["full_diffeomorphism_khronon_Ward_completed"] is False
    assert len(row["missing_for_full_diffeomorphism_khronon_Ward"]) >= 4


def test_flags_are_separated_and_every_downstream_claim_stays_false() -> None:
    payload = gate.build_payload()
    decision = payload["decision"]
    assert decision["bulk_full_v5_2_internal_SO3_Ward_pass"] is True
    assert decision["interface_full_v5_2_internal_SO3_Ward_selected_sector_pass"] is True
    assert decision["boundary_Green_local_exact_identity_pass"] is True
    assert decision["internal_SO3_full_action_selected_trivial_sector_Ward_pass"] is True
    for key in gate.FAIL_CLOSED_KEYS:
        assert decision[key] is False
    preliminary = payload["v5_5_1_preliminary_receipt"]
    assert preliminary["consumed"] is False
    assert preliminary["promotable_by_this_gate"] is False


def test_artifact_is_canonical_deterministic_and_provenance_bound() -> None:
    stored_bytes = gate.OUTPUT.read_bytes()
    stored = json.loads(stored_bytes.decode("utf-8"))
    fresh = gate.build_payload()
    expected_bytes = (
        json.dumps(fresh, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    assert stored == fresh
    assert stored_bytes == expected_bytes
    assert stored["provenance"]["generator"]["sha256"] == gate._sha256(
        Path(gate.__file__).resolve()
    )
    assert stored["provenance"]["test"]["sha256"] == gate._sha256(gate.TEST)


@pytest.mark.parametrize(
    ("target", "message"),
    (("v5.2", "v5.2 artifact byte hash mismatch"), ("v5.5.2", "v5.5.2 artifact byte hash mismatch")),
)
def test_late_pinned_source_change_fails_closed(
    monkeypatch: pytest.MonkeyPatch, target: str, message: str
) -> None:
    real_sha256 = gate._sha256

    def changed(path: Path) -> str:
        if (target == "v5.2" and path == gate.V5_2) or (
            target == "v5.5.2" and path == gate.V5_5_2
        ):
            return "0" * 64
        return real_sha256(path)

    monkeypatch.setattr(gate, "_sha256", changed)
    with pytest.raises(gate.FullActionWardV553Error, match=message):
        gate.build_payload()
