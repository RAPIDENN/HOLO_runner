#!/usr/bin/env python3
"""Tests for the independent v5.5.4 interface Ward red-team."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

if __package__:
    from . import derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam as gate
else:
    import derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam as gate


@pytest.fixture(scope="session")
def receipt() -> dict:
    return gate.build_payload()


def test_primary_three_file_binding_is_final_and_fail_closed(receipt: dict) -> None:
    lineage = receipt["lineage"]["primary_v5_5_4"]
    assert set(lineage) == {"artifact_sha256", "generator_sha256", "test_sha256"}
    assert all(len(value) == 64 for value in lineage.values())
    assert all(not value.startswith("PENDING_") for value in lineage.values())
    assert lineage["artifact_sha256"] == gate._sha256(gate.PRIMARY_V5_5_4_ARTIFACT)
    assert lineage["generator_sha256"] == gate._sha256(gate.PRIMARY_V5_5_4_GENERATOR)
    assert lineage["test_sha256"] == gate._sha256(gate.PRIMARY_V5_5_4_TEST)


def test_no_primary_helper_or_runtime_is_imported(receipt: dict) -> None:
    assert receipt["primary_helpers_or_runtime_imported"] == []
    route = receipt["runtime"]["implementation_route"]
    assert route["primary_helpers_or_runtime_imported"] == []
    assert route["same_field_family_as_primary"] is False
    source = Path(gate.__file__).read_text(encoding="utf-8")
    assert "import derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate" not in source
    assert "from torch.func import jacrev, jvp, vmap" in source
    assert "def _jvp_density_point(" in source
    assert "def _stokes_density_point(" in source
    lineage_source = source.split("def load_lineage()", 1)[1].split("def _write", 1)[0]
    assert '"decision"' not in lineage_source
    assert "PRIMARY_REQUIRED" not in source


def test_v5_2_literals_and_v5_5_2_controls_are_hash_pinned(receipt: dict) -> None:
    assert receipt["lineage"]["v5_2_artifact_sha256"] == gate.EXPECTED_V5_2_SHA256
    assert receipt["lineage"]["v5_5_2_artifact_sha256"] == gate.EXPECTED_V5_5_2_SHA256
    assert receipt["lineage"]["v5_5_2_redteam_artifact_sha256"] == gate.EXPECTED_V5_5_2_REDTEAM_SHA256
    assert receipt["formula_ledger"]["literal_action"] == gate.EXPECTED_ACTIONS


def test_distinct_geometry_and_finite_action_euler_routes_are_declared(receipt: dict) -> None:
    runtime = receipt["runtime"]
    assert "Ricci contraction" in runtime["geometry_route"]
    assert "centered finite differences" in runtime["implementation_route"]["Euler_pairings"]
    assert "reverse-mode jacrev" in runtime["implementation_route"]["coordinate_jets"]
    assert "torch.func.jvp" in runtime["implementation_route"]["local_JVP"]
    assert "separately assembled density" in runtime["implementation_route"]["boundary_Stokes"]
    assert "literal controls" in runtime["action_scope"]


def test_all_four_coordinates_and_two_compact_xi_are_active(receipt: dict) -> None:
    runtime = receipt["runtime"]
    activity = runtime["activity"]
    assert activity["all_four_coordinates_active"] is True
    assert activity["minimum_coordinate_activity"] > 1.0e-5
    assert activity["boundary_xi_exact_max"] == 0.0
    probes = runtime["compact_xi_probes"]
    assert [probe["xi_variant"] for probe in probes] == [0, 1]
    assert all(probe["xi_RMS"] > 1.0e-5 for probe in probes)


def test_finite_difference_euler_slots_close_and_converge(receipt: dict) -> None:
    for probe in receipt["runtime"]["compact_xi_probes"]:
        slots = probe["finite_difference_Euler_slot_pairings"]
        assert set(slots) == {"metric_stress", "khronon_T", "Omega", "psi_covector"}
        assert probe["minimum_absolute_slot_pairing"] > 1.0e-7
        assert probe["direct_all_vs_slot_sum_error"] < 5.0e-7
        assert probe["direct_all_step_convergence"] < 5.0e-7
        assert max(probe["slot_step_convergence"].values()) < 5.0e-7


def test_signed_raw_action_and_real_local_jvp_cover_all_sixteen_components(
    receipt: dict,
) -> None:
    for probe in receipt["runtime"]["compact_xi_probes"]:
        rows = probe["signed_component_action_and_local_JVP"]
        assert [row["component"] for row in rows] == list(gate.COMPONENT_LABELS)
        assert len(rows) == 16
        for row in rows:
            assert len(row["signed_local_JVP_values"]) == probe["point_count"]
            assert row["local_JVP_RMS"] > gate.COMPONENT_LOCAL_ACTIVITY_FLOOR
            assert row["action_vs_JVP_absolute_error"] < gate.COMPONENT_ACTION_JVP_TOLERANCE
            assert row["local_JVP_min"] <= row["local_JVP_max"]
        assert probe["maximum_component_action_vs_JVP_error"] < gate.COMPONENT_ACTION_JVP_TOLERANCE
        additivity = probe["component_JVP_additivity"]
        assert len(additivity["signed_joint_local_JVP_values"]) == probe["point_count"]
        assert len(additivity["signed_sum_of_16_local_JVP_values"]) == probe["point_count"]
        assert additivity["pointwise_Linf_error"] < 2.0e-10


def test_action_jvp_and_stokes_use_separate_density_assemblies(receipt: dict) -> None:
    for probe in receipt["runtime"]["compact_xi_probes"]:
        row = probe["independent_density_route_comparison"]
        assert len(row["signed_action_density_values"]) == probe["point_count"]
        assert len(row["signed_JVP_density_values"]) == probe["point_count"]
        assert len(row["signed_Stokes_density_values"]) == probe["point_count"]
        assert row["action_vs_JVP_Linf"] < 2.0e-10
        assert row["action_vs_Stokes_Linf"] < 2.0e-10


def test_density_divergence_matches_independent_action_variation(receipt: dict) -> None:
    for probe in receipt["runtime"]["compact_xi_probes"]:
        assert probe["weak_sum_vs_divergence_error"] < 5.0e-7
        assert probe["local_density_covariance_L2"] < 5.0e-7
        assert probe["local_density_covariance_Linf"] < 5.0e-6
        assert probe["density_variation_RMS"] > 1.0e-6
        assert probe["transport_RMS"] > 1.0e-6
        assert probe["density_Jacobian_term_RMS"] > 1.0e-6


def test_independent_eight_face_stokes_flux_is_runtime_zero(receipt: dict) -> None:
    stokes = receipt["runtime"]["compact_Stokes_boundary_flux"]
    assert set(stokes) == {"xi_variant_0", "xi_variant_1"}
    for row in stokes.values():
        assert row["face_count"] == 8
        assert len(row["faces"]) == 8
        assert row["boundary_zero_obtained_from_runtime_fields"] is True
        assert row["maximum_boundary_xi"] < 2.0e-15
        assert row["maximum_boundary_action_density"] > 1.0e-3
        assert row["maximum_boundary_flux_density"] < 2.0e-14
        assert row["total_oriented_boundary_flux_absolute"] < 2.0e-14
    assert max(
        receipt["runtime"]["selected_family_Stokes_weak_residual_bounds"].values()
    ) < 2.0e-5


def test_underresolved_gauss_volume_is_recorded_but_never_used_as_zero_gate(
    receipt: dict,
) -> None:
    runtime = receipt["runtime"]
    diagnostic = runtime["underresolved_Gauss_volume_diagnostics"]
    assert set(diagnostic) == {"xi_variant_0", "xi_variant_1"}
    for row in diagnostic.values():
        assert row["quadrature_orders_evaluated"] == [3]
        assert row["convergence_to_zero_tested"] is False
        assert row["certified"] is False
        assert row["used_by_selected_family_decision"] is False
        assert row["weak_sum_vs_divergence_error"] < 5.0e-7
    convergence = runtime["compact_divergence_quadrature_convergence"]
    assert convergence["convergence_to_zero_tested"] is False
    assert convergence["certified"] is False
    assert convergence["used_by_selected_family_decision"] is False


def test_mutants_are_nonvacuous_and_separated_from_nominal(receipt: dict) -> None:
    runtime = receipt["runtime"]
    required_suffixes = {
        "scalarize_psi_covector",
        "omit_density_Jacobian",
        "omit_sqrt_gamma_from_wall",
        "force_khronon_E_T_on_shell",
        "omit_metric_stress",
        "omit_khronon_T",
        "omit_Omega",
        "omit_psi_covector",
        "flip_sign_metric_stress",
        "flip_sign_khronon_T",
        "flip_sign_Omega",
        "flip_sign_psi_covector",
    }
    for probe_index in range(2):
        names = {
            key.removeprefix(f"probe{probe_index}_")
            for key in runtime["mutant_witnesses"]
            if key.startswith(f"probe{probe_index}_")
        }
        assert names == required_suffixes
        executed = runtime["compact_xi_probes"][probe_index]["executed_mutants"]
        assert set(executed) == required_suffixes
        for row in executed.values():
            assert "re-evaluated" in row["route"]
            assert row["mutant_residual"] > gate.MUTANT_RESIDUAL_FLOOR
    assert set(runtime["required_independent_control_mutants"]) == {
        "R_groupoid_frozen",
        "induced_pullback_broken",
        "omit_T_ui_matter",
        "flip_T_ui_matter_sign",
        "anisotropic_full_V4",
    }
    assert min(runtime["required_independent_control_mutants"].values()) > gate.MUTANT_RESIDUAL_FLOOR
    assert runtime["minimum_mutant_witness"] > 1.0e-6
    assert runtime["mutant_to_nominal_ratio"] > 10.0
    assert runtime["maximum_nominal_closure_error"] < 5.0e-6


def test_groupoid_pullback_matter_shift_and_full_v4_controls_are_rebuilt(
    receipt: dict,
) -> None:
    controls = receipt["runtime"]["independent_control_reconstructions"]
    tolerances = controls["tolerances"]
    groupoid = controls["R_groupoid_frozen"]
    assert groupoid["R_is_groupoid_data_not_an_independent_bifundamental_field"] is True
    assert len(groupoid["signed_nominal_delta_varphi_H"]) == 3
    assert len(groupoid["signed_frozen_R_delta_varphi_H"]) == 3
    assert groupoid["nominal_invariance_error"] < tolerances["R_groupoid_nominal_max"]
    assert groupoid["frozen_R_mutant_witness"] > tolerances["required_mutant_minimum"]

    pullback = controls["induced_pullback_broken"]
    assert pullback["ambient_dimension"] == 5
    assert pullback["interface_dimension"] == 4
    assert abs(pullback["normal_embedding_displacement"]) > 1.0e-4
    assert len(pullback["signed_finite_pullback_derivative"]) == 10
    assert len(pullback["signed_Lie_derivative_prediction"]) == 10
    assert len(pullback["signed_broken_pullback_derivative"]) == 10
    assert pullback["nominal_pullback_max_error"] < tolerances["induced_pullback_nominal_max"]
    assert pullback["broken_pullback_mutant_witness"] > tolerances["required_mutant_minimum"]

    matter = controls["matter_T_ui_omitted"]
    assert len(matter["signed_T_ui_components"]) == 3
    assert len(matter["signed_covariant_shift_prediction"]) == 3
    assert len(matter["signed_finite_action_shift_derivative"]) == 3
    assert len(matter["signed_omit_T_ui_equation_prediction"]) == 3
    assert len(matter["signed_flip_T_ui_sign_prediction"]) == 3
    assert matter["nominal_shift_max_error"] < tolerances["matter_shift_nominal_max"]
    assert matter["T_ui_activity_norm"] > 1.0e-3
    assert matter["minimum_absolute_T_ui_component"] > 1.0e-4
    assert matter["omit_T_ui_matter_mutant_witness"] > tolerances["required_mutant_minimum"]
    assert matter["flip_T_ui_sign_mutant_witness"] > tolerances["required_mutant_minimum"]

    v4 = controls["full_V4_anisotropic"]
    assert abs(v4["signed_radial_gauge_derivative"]) < tolerances["radial_V4_gauge_derivative_max"]
    assert v4["radial_potential_activity"] > 1.0e-6
    assert v4["anisotropic_V4_mutant_witness"] > tolerances["required_mutant_minimum"]
    assert controls["gate_helpers_imported"] == []
    assert controls["upstream_decision_booleans_used_as_oracle"] is False


def test_selected_redteam_green_does_not_promote_full_theory(receipt: dict) -> None:
    decision = receipt["decision"]
    assert decision["independent_interface_diffeomorphism_khronon_redteam_pass"] is True
    assert decision["local_density_Ward_equals_divergence_redteam_pass"] is True
    assert decision["real_local_JVP_10_gamma_T_Omega_4_psi_pass"] is True
    assert decision["independent_action_JVP_Stokes_density_assemblies_pass"] is True
    assert decision["executed_mutation_re_evaluation_pass"] is True
    assert decision["independent_R_groupoid_pullback_T_ui_V4_controls_pass"] is True
    assert decision["runtime_boundary_Stokes_flux_zero_redteam_pass"] is True
    assert decision["compact_xi_weak_Ward_zero_by_local_Stokes_redteam_pass"] is True
    assert decision["underresolved_Gauss_volume_Ward_diagnostic_pass"] is False
    assert decision["compact_divergence_quadrature_convergence_pass"] is False
    assert decision["independent_redteam_checks_pass"] is True
    assert {
        key
        for key, value in decision.items()
        if key.endswith("_pass") and value is True
    } == gate.ALLOWED_TRUE_PASS_KEYS
    for key in gate.FAIL_CLOSED_KEYS:
        assert decision[key] is False


@pytest.mark.parametrize(
    ("section", "field", "matching"),
    [
        ("R_groupoid_frozen", "frozen_R_mutant_witness", "R_groupoid_frozen"),
        ("induced_pullback_broken", "broken_pullback_mutant_witness", "induced_pullback_broken"),
        ("matter_T_ui_omitted", "omit_T_ui_matter_mutant_witness", "omit_T_ui_matter"),
        ("matter_T_ui_omitted", "flip_T_ui_sign_mutant_witness", "flip_T_ui_matter_sign"),
        ("full_V4_anisotropic", "anisotropic_V4_mutant_witness", "anisotropic_full_V4"),
    ],
)
def test_each_new_control_is_mandatory_and_fails_closed(
    receipt: dict, section: str, field: str, matching: str
) -> None:
    runtime = copy.deepcopy(receipt["runtime"])
    runtime["independent_control_reconstructions"][section][field] = 0.0
    runtime["required_independent_control_mutants"][matching] = 0.0
    decision = gate._decision(runtime)
    assert decision["independent_R_groupoid_pullback_T_ui_V4_controls_pass"] is False
    assert decision["independent_redteam_checks_pass"] is False


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("maximum_component_action_vs_JVP_error",), 1.0),
        (("component_JVP_additivity", "pointwise_Linf_error"), 1.0),
        (("independent_density_route_comparison", "action_vs_Stokes_Linf"), 1.0),
        (("executed_mutants", "omit_Omega", "mutant_residual"), 0.0),
    ],
)
def test_component_route_and_executed_mutant_contracts_fail_closed(
    receipt: dict, path: tuple[str, ...], replacement: object
) -> None:
    runtime = copy.deepcopy(receipt["runtime"])
    target = runtime["compact_xi_probes"][0]
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement
    decision = gate._decision(runtime)
    assert decision["independent_redteam_checks_pass"] is False


def test_artifact_is_canonical_and_provenance_bound(receipt: dict) -> None:
    stored_bytes = gate.OUTPUT.read_bytes()
    stored = json.loads(stored_bytes.decode("utf-8"))
    expected = (json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    assert stored == receipt
    assert stored_bytes == expected
    assert stored["provenance"]["generator_sha256"] == gate._sha256(Path(gate.__file__))
    assert stored["provenance"]["test_sha256"] == gate._sha256(gate.TEST)
    assert stored["provenance"]["threads"] == 1


def test_pending_primary_hashes_abort_before_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        gate,
        "EXPECTED_PRIMARY_V5_5_4_ARTIFACT_SHA256",
        "PENDING_FINAL_PRIMARY_V5_5_4_ARTIFACT_SHA256",
    )
    with pytest.raises(gate.InterfaceWardV554RedteamError, match="hashes are pending"):
        gate.build_payload()


def test_late_primary_artifact_change_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    real_hash = gate._sha256

    def changed(path: Path) -> str:
        if path == gate.PRIMARY_V5_5_4_ARTIFACT:
            return "0" * 64
        return real_hash(path)

    monkeypatch.setattr(gate, "_sha256", changed)
    with pytest.raises(gate.InterfaceWardV554RedteamError, match="lineage hash mismatch"):
        gate.build_payload()
