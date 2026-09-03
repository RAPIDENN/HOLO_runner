#!/usr/bin/env python3
"""Adversarial tests for the independent full-5D v5.5.3 red-team."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any

import pytest

if __package__:
    from . import derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate as gate
else:
    import derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate as gate


def _set_path(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    current: Any = value
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = replacement


@pytest.fixture(scope="module")
def receipt() -> dict[str, Any]:
    return gate.independent_runtime_certificate()


def test_all_primary_v52_and_ADM_files_are_byte_hash_pinned() -> None:
    rows = {
        gate.PRIMARY_GENERATOR: gate.EXPECTED_PRIMARY_GENERATOR_SHA256,
        gate.PRIMARY_TEST: gate.EXPECTED_PRIMARY_TEST_SHA256,
        gate.PRIMARY_ARTIFACT: gate.EXPECTED_PRIMARY_ARTIFACT_SHA256,
        gate.V5_2_ARTIFACT: gate.EXPECTED_V5_2_SHA256,
        gate.ADM_GENERATOR: gate.EXPECTED_ADM_GENERATOR_SHA256,
        gate.ADM_TEST: gate.EXPECTED_ADM_TEST_SHA256,
        gate.ADM_ARTIFACT: gate.EXPECTED_ADM_ARTIFACT_SHA256,
        gate.ADM_REDTEAM_GENERATOR: gate.EXPECTED_ADM_REDTEAM_GENERATOR_SHA256,
        gate.ADM_REDTEAM_TEST: gate.EXPECTED_ADM_REDTEAM_TEST_SHA256,
        gate.ADM_REDTEAM_ARTIFACT: gate.EXPECTED_ADM_REDTEAM_ARTIFACT_SHA256,
    }
    assert all(gate._sha256(path) == expected for path, expected in rows.items())


def test_source_imports_no_primary_helper_and_contains_no_reduction_or_np_cross() -> None:
    source = Path(gate.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
        elif isinstance(node, ast.Call):
            calls.append(node)
    assert not any("full_action_gauge_noether_v5_5_3_gate" in name for name in imported)
    assert not any("v5_5_1" in name for name in imported)
    assert not any(
        isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "np"
        and node.func.attr == "cross"
        for node in calls
    )


def test_real_five_dimensional_form_engine_has_correct_degrees(
    receipt: dict[str, Any],
) -> None:
    row = receipt["matrix_and_form_representation_certificate"]
    assert row["Gram_identity_error"] < 2.0e-14
    assert row["maximum_structure_constant_error"] < 2.0e-14
    assert row["invariant_trace_error"] < 2.0e-14
    assert row["form_component_counts"] == {
        "0": 1, "1": 5, "2": 10, "3": 10, "4": 5, "5": 1
    }
    assert abs(row["four_form_wedge_normal_one_form"] - 1.0) < 2.0e-14
    assert abs(row["normal_one_form_wedge_four_form"] - 1.0) < 2.0e-14


def test_derivative_resolution_exhibits_fourth_order_ratio(
    receipt: dict[str, Any],
) -> None:
    row = receipt["derivative_resolution_certificate"]
    assert row["stencil"] == "centered fourth-order finite difference"
    assert len(row["coordinates"]) == 5
    assert row["minimum_observed_error_ratio"] > 12.0
    assert row["maximum_fine_error"] < 2.0e-8


def test_all_five_coordinates_are_active_and_interface_traces_match(
    receipt: dict[str, Any],
) -> None:
    row = receipt["five_coordinate_activity"]
    assert row["bulk_dimension"] == 5
    assert row["interface_dimension"] == 4
    assert [row[f"{name}_form_degree"] for name in ("connection", "curvature", "B", "connection_Euler", "Ward")] == [1, 2, 3, 4, 5]
    for side in row["side_activity"].values():
        for values in side.values():
            assert len(values) == 5
            assert min(values) > 1.0e-4
    assert max(row["interface_trace_match_errors"].values()) < 2.0e-13


def test_full_action_Euler_match_has_real_quadrature_convergence(
    receipt: dict[str, Any],
) -> None:
    row = receipt["action_to_Euler"]
    convergence = row["quadrature_convergence"]
    assert set(convergence) == {"2", "3", "4"}
    errors = row["successive_absolute_errors"]
    assert errors == [convergence[str(order)]["absolute_error"] for order in (2, 3, 4)]
    assert errors[2] < errors[0]
    assert errors[2] < errors[1]
    assert errors[2] / max(errors[0], errors[1]) < 0.25
    assert row["tensor_product_node_counts"] == {"2": 32, "3": 243, "4": 1024}
    assert row["arbitrary_variation_scale"] == 2.0
    assert min(row["successive_error_ratios"]) > 1.2
    assert row["absolute_error"] < 5.0e-7
    assert row["active_derivative_magnitude"] > 1.0e-4
    assert row["flip_matter_source_sign_witness"] > 1.0e-4
    assert row["neutral_piece_central_derivative_max"] == 0.0
    assert set(row["active_action_pieces"]) == {
        "BF", "matter", "EH", "Omega_and_U", "GHY", "wall_background",
        "foliation_lower", "Robin_intrinsic",
    }
    assert min(abs(value) for value in row["active_action_pieces"].values()) > 1.0e-4


def test_W_closes_off_shell_by_three_generators_on_both_full_5D_sides(
    receipt: dict[str, Any],
) -> None:
    sides = receipt["bulk_internal_gauge_identity_by_side"]
    assert set(sides) == {"-1", "1"}
    for side in sides.values():
        ward = side["off_shell_W"]
        assert ward["total_L2_residual"] < 5.0e-7
        assert set(ward["per_generator"]) == {"T_1", "T_2", "T_3"}
        assert max(row["absolute"] for row in ward["per_generator"].values()) < 2.0e-6
        assert min(ward["Euler_norms"].values()) > 1.0e-4
        assert min(ward["term_norms"].values()) > 1.0e-4


def test_D2B_DF_and_full_matter_current_close_separately(
    receipt: dict[str, Any],
) -> None:
    for side in receipt["bulk_internal_gauge_identity_by_side"].values():
        bf = side["D_squared_B"]
        assert bf["residual"] < 5.0e-7
        assert bf["lhs_norm"] > 1.0e-4
        assert bf["rhs_norm"] > 1.0e-4
        assert bf["wrong_sign_witness"] > 1.0e-4
        bianchi = side["five_dimensional_Bianchi"]
        assert bianchi["residual"] < 5.0e-7
        assert bianchi["curvature_norm"] > 1.0e-4
        assert bianchi["covariant_derivative_term_norm"] > 1.0e-4
        assert bianchi["ordinary_derivative_mutant_witness"] > 1.0e-4
        matter = side["matter_current"]
        assert matter["residual"] < 5.0e-7
        assert matter["D_A_current_norm"] > 1.0e-4
        assert matter["matter_moment_norm"] > 1.0e-4
        assert matter["c_i_P_i_norm"] > 1.0e-4
        assert matter["omit_c_i_P_i_witness"] > 1.0e-4
        assert matter["radial_V4_moment_norm"] < 1.0e-12
        assert matter["anisotropic_V4_moment_witness"] > 1.0e-4


def test_flip_J_and_both_conformal_omissions_are_explicitly_killed(
    receipt: dict[str, Any],
) -> None:
    for side in receipt["bulk_internal_gauge_identity_by_side"].values():
        mutants = side["mutant_witnesses"]
        assert mutants["flip_J_A_sign"] > 1.0e-3
        assert mutants["omit_conformal_minus_cP"] > 1.0e-4
        assert mutants["omit_c_phi_from_P_action_density"] > 1.0e-4
        assert mutants["replace_radial_V4_by_anisotropic_source"] > 1.0e-4
        assert min(mutants.values()) > 1.0e-4


def test_full_Omega_c_and_radial_V4_are_active_but_have_zero_gauge_moment(
    receipt: dict[str, Any],
) -> None:
    for side in receipt["bulk_internal_gauge_identity_by_side"].values():
        row = side["full_material"]
        assert row["Omega"] > 0.0
        assert row["c_norm"] > 1.0e-4
        assert row["P_norm"] > 1.0e-4
        assert row["V4_Ephi_norm"] > 1.0e-4
        assert row["radial_V4_moment_norm"] < 1.0e-12
        assert row["anisotropic_V4_moment_witness"] > 1.0e-4
        assert row["rho_zero_extension_norm"] == 0.0


def test_compact_lambda_precedes_boundary_and_bad_V4_breaks_invariance(
    receipt: dict[str, Any],
) -> None:
    row = receipt["compact_lambda"]
    assert row["bulk_dimensions"] == 5
    assert row["boundary_trace_max"] == 0.0
    assert min(row["all_three_generator_norms"]) > 1.0e-4
    assert abs(row["direct_full_action_gauge_derivative"]) < 5.0e-6
    assert abs(row["Euler_gauge_pairing"]) < 5.0e-6
    assert row["direct_vs_Euler_error"] < 5.0e-7
    assert max(row["per_generator_compact_pairing_absolute"].values()) < 5.0e-6
    assert abs(row["anisotropic_noninvariant_V4_mutant_derivative"]) > 1.0e-5


def test_Robin_neutrality_is_derived_from_phi_and_solder_frame_slots(
    receipt: dict[str, Any],
) -> None:
    row = receipt["Robin_solder_frame"]
    assert row["interface_dimensions"] == 4
    assert row["solder_definition"] == "varphi_H^i=e_a^i phi^a"
    assert row["internal_gauge_variation"] == "delta phi=lambda phi; delta e=-e lambda"
    assert row["derived_delta_varphi_H_Linf"] < 2.0e-14
    assert abs(row["direct_Robin_gauge_derivative"]) < 5.0e-9
    assert abs(row["Euler_slot_sum"]) < 5.0e-9
    assert row["direct_vs_slot_sum_error"] < 5.0e-9
    assert abs(row["fixed_frame_mutant_direct_derivative"]) > 1.0e-4
    assert row["fixed_frame_mutant_vs_phi_slot_error"] < 5.0e-8


def test_interface_residue_is_real_without_claiming_BV_BFV(
    receipt: dict[str, Any],
) -> None:
    row = receipt["interface_residue"]
    assert row["interface_dimensions"] == 4
    assert row["lambda_interface_L2"] > 1.0e-3
    assert row["interface_residue_magnitude"] > 1.0e-4
    assert row["Green_identity"] == (
        "delta S_bulk = <E,delta_gauge fields> - outward <E_A,lambda>"
    )
    assert abs(row["direct_full_action_gauge_derivative"]) < 5.0e-6
    assert row["direct_vs_Green_balance_error"] < 5.0e-6
    assert row["Euler_vs_outward_flux_error"] < 5.0e-6
    assert row["direct_vs_Euler_error"] > 1.0e-4
    assert row["direct_vs_outward_flux_error"] > 1.0e-4
    assert row["wrong_incidence_witness"] > 1.0e-4
    assert row["BV_BFV_edge_fields_constructed"] is False
    assert row["regulated_interface_charge_algebra_constructed"] is False


def test_internal_gauge_is_not_substituted_for_diffeomorphism_khronon(
    receipt: dict[str, Any],
) -> None:
    row = receipt["internal_vs_diffeomorphism_khronon"]
    assert row["identities_are_not_equated"] is True
    assert set(row["internal_SO3_slots"]) == {"A", "B", "phi", "solder_frame"}
    assert row["full_diffeomorphism_khronon_Ward_reproduced_status"] == "FAIL_CLOSED"
    for key, value in row.items():
        if key.startswith("ADM_") and key not in {"ADM_primary_gamma_chain_pass"}:
            if key.endswith(("_C1", "_N1", "_Green", "_normal_embedding")):
                assert value is False
    assert all(gate.adm_control_contract().values())


def test_primary_contract_binds_full_dimension_and_fail_closed_scope() -> None:
    contract = gate.primary_contract()
    assert len(contract) == 11
    assert all(contract.values())


def test_only_the_allowlisted_internal_gauge_passes_can_be_true() -> None:
    payload = gate.build_payload()
    assert payload["checks"]["all_independent_full_5D_redteam_checks"] is True
    decision = payload["decision"]
    true_passes = {
        key for key, value in decision.items() if key.endswith("_pass") and value is True
    }
    assert true_passes == gate.ALLOWED_TRUE_PASS_KEYS
    assert payload["true_pass_allowlist"] == sorted(gate.ALLOWED_TRUE_PASS_KEYS)
    for key in gate.FAIL_CLOSED_KEYS:
        assert decision[key] is False


@pytest.mark.parametrize(
    "target",
    [
        "PRIMARY_GENERATOR", "PRIMARY_TEST", "PRIMARY_ARTIFACT", "V5_2_ARTIFACT",
        "ADM_GENERATOR", "ADM_TEST", "ADM_ARTIFACT", "ADM_REDTEAM_GENERATOR",
        "ADM_REDTEAM_TEST", "ADM_REDTEAM_ARTIFACT",
    ],
)
def test_each_frozen_hash_mutation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    target: str,
) -> None:
    target_path = getattr(gate, target)
    real_sha256 = gate._sha256

    def changed(path: Path) -> str:
        return "0" * 64 if path == target_path else real_sha256(path)

    monkeypatch.setattr(gate, "_sha256", changed)
    with pytest.raises(gate.FullActionGaugeV553RedteamError, match="frozen input hash mismatch"):
        gate.build_payload()


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("schema",), "mutant.schema"),
        (("decision", "bulk_full_v5_2_internal_SO3_Ward_pass"), False),
        (("decision", "diffeomorphism_khronon_full_Ward_pass"), True),
        (("decision", "C1_ACTION_pass"), True),
        (("checks", "all_primary_scope_checks"), False),
        (("certificate", "form_degree_contract", "ambient_dimension"), 2),
        (("certificate", "form_degree_contract", "dimensional_reduction_or_spectator_ansatz_used"), True),
        (("certificate", "bulk_sides", "minus", "mutant_witnesses", "flip_J_A_sign"), 0.0),
        (("certificate", "bulk_sides", "plus", "mutant_witnesses", "omit_c_phi_from_P_action_mismatch"), 0.0),
        (("certificate", "diffeomorphism_khronon_attempt", "full_diffeomorphism_khronon_Ward_completed"), True),
        (("equation_ledger", "source_groupoid"), "frame fixed"),
        (("v5_5_1_preliminary_receipt", "consumed"), True),
        (("pinned_v5_2", "sha256"), "0" * 64),
        (("provenance", "generator", "sha256"), "0" * 64),
    ],
)
def test_primary_semantic_mutants_break_the_contract(
    monkeypatch: pytest.MonkeyPatch,
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    mutant = copy.deepcopy(gate._load_primary())
    _set_path(mutant, path, replacement)
    monkeypatch.setattr(gate, "_load_primary", lambda: mutant)
    with pytest.raises(gate.FullActionGaugeV553RedteamError, match="primary contract failed"):
        gate.build_payload()


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("action_to_Euler", "absolute_error"), 1.0),
        (("action_to_Euler", "successive_absolute_errors"), [1.0, 1.0, 1.0]),
        (("bulk_internal_gauge_identity_by_side", "-1", "off_shell_W", "total_L2_residual"), 1.0),
        (("bulk_internal_gauge_identity_by_side", "1", "mutant_witnesses", "flip_J_A_sign"), 0.0),
        (("bulk_internal_gauge_identity_by_side", "-1", "mutant_witnesses", "omit_c_phi_from_P_action_density"), 0.0),
        (("bulk_internal_gauge_identity_by_side", "1", "five_dimensional_Bianchi", "residual"), 1.0),
        (("compact_lambda", "anisotropic_noninvariant_V4_mutant_derivative"), 0.0),
        (("Robin_solder_frame", "fixed_frame_mutant_direct_derivative"), 0.0),
        (("interface_residue", "BV_BFV_edge_fields_constructed"), True),
        (("on_shell_and_circularity_detector", "on_shell_only_check_rejected"), False),
    ],
)
def test_independent_oracle_mutants_abort_build(
    monkeypatch: pytest.MonkeyPatch,
    receipt: dict[str, Any],
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    mutant = copy.deepcopy(receipt)
    _set_path(mutant, path, replacement)
    monkeypatch.setattr(gate, "independent_runtime_certificate", lambda: mutant)
    with pytest.raises(gate.FullActionGaugeV553RedteamError, match="independent full-5D red-team failed"):
        gate.build_payload()


def test_zero_Euler_circular_receipt_cannot_hardcode_a_pass(
    monkeypatch: pytest.MonkeyPatch,
    receipt: dict[str, Any],
) -> None:
    mutant = copy.deepcopy(receipt)
    mutant["on_shell_and_circularity_detector"]["actual_off_shell_Euler_minimum"] = 0.0
    mutant["on_shell_and_circularity_detector"]["actual_identity_term_minimum"] = 0.0
    mutant["on_shell_and_circularity_detector"]["on_shell_only_check_rejected"] = False
    monkeypatch.setattr(gate, "independent_runtime_certificate", lambda: mutant)
    with pytest.raises(gate.FullActionGaugeV553RedteamError, match="independent full-5D red-team failed"):
        gate.build_payload()


def test_artifact_is_canonical_deterministic_and_self_hash_bound() -> None:
    raw = gate.OUTPUT.read_bytes()
    stored = json.loads(raw.decode("utf-8"))
    fresh = gate.build_payload()
    canonical = (
        json.dumps(fresh, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    assert stored == fresh
    assert raw == canonical
    assert stored["provenance"]["generator"]["sha256"] == gate._sha256(
        Path(gate.__file__).resolve()
    )
    assert stored["provenance"]["test"]["sha256"] == gate._sha256(gate.TEST)
