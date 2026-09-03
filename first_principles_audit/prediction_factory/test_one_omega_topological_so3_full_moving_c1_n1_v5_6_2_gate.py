#!/usr/bin/env python3
"""Strict fail-closed tests for the additive v5.6.2 diagnostics."""

from __future__ import annotations

import ast
import copy
import inspect
import json
import math
from pathlib import Path
from typing import Any, Iterator

import pytest

if __package__:
    from . import derive_one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate as gate
else:
    import derive_one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate as gate


EXPECTED_PIN_KEYS = {
    "v5_2_action",
    "v5_5_2_primary",
    "v5_5_2_redteam",
    "v5_5_3_primary",
    "v5_5_3_redteam",
    "v5_5_4_primary",
    "v5_5_4_redteam",
    "v5_6_1_freeze",
}
EXPECTED_ACTION_KEYS = {
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
EXPECTED_COMPONENTS = {
    "BF_bulk_minus",
    "BF_bulk_plus",
    "EH_bulk_minus",
    "EH_bulk_plus",
    "GHY_minus",
    "GHY_plus",
    "K_foliation",
    "Omega_kinetic_bulk_minus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_minus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_minus",
    "P_kinetic_bulk_plus",
    "R",
    "R_squared",
    "Robin",
    "S_total",
    "a_squared",
    "full_V4_bulk_minus",
    "full_V4_bulk_plus",
    "wall",
}
EXPECTED_FAIL_CLOSED_KEYS = {
    "independent_redteam_replication_complete",
    "internal_SO3_direct_orbit_diagnostic_pass",
    "selected_normal_slots_and_matter_shift_visible_pass",
    "primary_mutant_suite_pass",
    "v5_6_2_selected_family_primary_candidate_pass",
    "all_five_ordinary_coordinate_directions_active_pass",
    "same_action_independent_Euler_Green_identity_pass",
    "same_action_internal_SO3_Euler_Ward_rederived_pass",
    "full_bulk_diffeomorphism_Ward_pass",
    "complete_moving_embedding_Ward_pass",
    "continuum_all_configurations_theorem_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_selected_family_pass",
    "N1_ACTION_selected_family_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "unrestricted_large_gauge_sector_pass",
    "deterministic_freeze_receipt_issued",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
}
EXPECTED_TRUE_PASS_KEYS = {
    "all_upstream_bytes_and_literal_action_pinned_pass",
    "selected_moving_family_action_JVP_FD_pass",
    "selected_mixed_cross_terms_runtime_pass",
    "selected_nonabelian_BF_activity_pass",
    "selected_bulk_P_V4_BF_orbit_sanity_pass",
    "intrinsic_periodic_density_divergence_diagnostic_pass",
}


@pytest.fixture(scope="module")
def stored_receipt() -> dict[str, Any]:
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rebuilt_receipt() -> dict[str, Any]:
    return gate.build_payload()


def _numbers(value: Any, path: str = "root") -> Iterator[tuple[str, float]]:
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, (int, float)):
        yield path, float(value)
        return
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _numbers(child, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            yield from _numbers(child, f"{path}[{index}]")


def test_generator_imports_no_upstream_gate_and_reads_no_upstream_decision(
    rebuilt_receipt: dict[str, Any],
) -> None:
    source_path = Path(gate.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden_modules = (
        "first_principles_audit",
        "prediction_factory",
        "derive_one_omega",
        "test_one_omega",
    )
    assert not any(
        any(token in module for token in forbidden_modules) for module in imported
    )

    # SOURCE_PAYLOADS may be retained for auditability, but no runtime route may
    # consume it after the literal v5.2 action/coefficient pin has been checked.
    source_payload_loads = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "SOURCE_PAYLOADS"
        and isinstance(node.ctx, ast.Load)
    ]
    assert source_payload_loads == []

    loader_tree = ast.parse(inspect.getsource(gate._load_and_pin_sources))
    forbidden_upstream_keys = {"decision", "checks", "runtime", "residuals", "Eulerians"}
    assert not forbidden_upstream_keys.intersection(
        node.value
        for node in ast.walk(loader_tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )

    routes = rebuilt_receipt["scientific"]["route_separation_diagnostic"]
    assert routes["upstream_helpers_imported"] == []
    assert routes["upstream_decisions_or_residuals_read"] is False
    assert routes["plain_route_forbidden_references"] == []
    assert routes["dual_route_forbidden_references"] == []
    assert routes["symbolically_separate_codepaths"] is True
    assert routes["independent_assemblies"] is False
    assert routes["independence_claimed"] is False
    assert routes["circular_expected_JVP_mutant_rejected"] is False
    assert routes["shared_infrastructure"]


def test_all_inputs_are_exact_three_file_byte_pins(
    rebuilt_receipt: dict[str, Any],
) -> None:
    assert set(gate.SOURCE_PINS) == EXPECTED_PIN_KEYS
    assert set(rebuilt_receipt["upstream_byte_pins"]) == EXPECTED_PIN_KEYS
    for label, pin in gate.SOURCE_PINS.items():
        artifact = gate.HERE / "artifacts" / pin.artifact
        generator = gate.HERE / pin.generator
        test = gate.HERE / pin.test
        assert gate._sha256(artifact) == pin.artifact_sha256
        assert gate._sha256(generator) == pin.generator_sha256
        assert gate._sha256(test) == pin.test_sha256

        recorded = rebuilt_receipt["upstream_byte_pins"][label]
        assert recorded == {
            "artifact": str(artifact.relative_to(gate.REPO)),
            "artifact_sha256": pin.artifact_sha256,
            "schema": pin.schema,
            "generator": str(generator.relative_to(gate.REPO)),
            "generator_sha256": pin.generator_sha256,
            "test": str(test.relative_to(gate.REPO)),
            "test_sha256": pin.test_sha256,
            "decision_boolean_consumed": False,
            "Eulerian_or_residual_consumed": False,
        }


def test_literal_v52_action_and_coefficient_keysets_are_exact(
    rebuilt_receipt: dict[str, Any],
) -> None:
    assert set(gate.EXACT_ACTION) == EXPECTED_ACTION_KEYS
    assert gate.EXACT_ACTION["total"] == (
        "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF"
    )
    assert "V4(r)=r^4/(2*sqrt(1+r^4))" == gate.EXACT_ACTION["full_V4"]
    assert "B_eps wedge F[A_eps]" in gate.EXACT_ACTION["BF"]
    assert rebuilt_receipt["scientific"]["literal_action"] == gate.EXACT_ACTION

    charter = gate.SOURCE_PAYLOADS["v5_2_action"]["exact_classical_charter"]
    assert charter["exact_action"] == gate.EXACT_ACTION
    parameters = charter["coefficient_policy"]["parameters"]
    assert set(parameters) == set(gate.EXPECTED_COEFFICIENTS)
    assert rebuilt_receipt["scientific"]["coefficients"] == gate.EXPECTED_COEFFICIENTS
    for key, expected in gate.EXPECTED_COEFFICIENTS.items():
        assert float(parameters[key]) == expected
        assert math.isfinite(expected)


def test_raw_component_and_cross_term_receipts_are_finite_and_active(
    rebuilt_receipt: dict[str, Any],
) -> None:
    scientific = rebuilt_receipt["scientific"]
    finite_values = list(_numbers(scientific))
    assert finite_values
    nonfinite = [(path, value) for path, value in finite_values if not math.isfinite(value)]
    assert nonfinite == []
    json.dumps(scientific, sort_keys=True, allow_nan=False)

    jvp = scientific["component_JVP_FD"]
    assert set(jvp["raw_rows"]) == {
        "basis_moving_embedding",
        "basis_ambient_metric",
        "basis_Omega",
        "basis_associated_matter",
        "basis_SO3_connection",
        "basis_BF_three_form",
        "coupled_audit",
    }
    for row in jvp["raw_rows"].values():
        assert len(row["direction"]) == len(gate.PARAMETER_NAMES) == 6
        assert set(row["components"]) == EXPECTED_COMPONENTS
    assert jvp["maximum_component_value_route_error"] < 2.0e-12
    assert jvp["maximum_component_JVP_error"] < 2.0e-7
    assert jvp["minimum_absolute_coupled_component_JVP"] > 1.0e-5

    cross = scientific["mixed_cross_terms"]
    assert len(cross["raw_cross_terms"]) == 14
    for row in cross["raw_cross_terms"].values():
        assert row["absolute_activity"] > 1.0e-6
        assert row["absolute_error"] < 2.0e-6
    assert cross["maximum_cross_route_error"] < 2.0e-6
    assert cross["minimum_absolute_cross_term"] > 1.0e-6


def test_nonabelian_F_B_and_all_covariant_P_slots_are_visibly_active(
    rebuilt_receipt: dict[str, Any],
) -> None:
    activity = rebuilt_receipt["scientific"]["field_activity"]
    for key in ("F_tx_max_norm", "F_tq_max_norm", "F_xq_max_norm"):
        assert activity[key] > 1.0e-3
    for key in ("B_yzq_max_norm", "B_xyz_max_norm", "B_tyz_max_norm"):
        assert activity[key] > 1.0e-3
    for axis in ("t", "x", "y", "z", "q"):
        assert activity[f"P_{axis}_max_norm"] > 1.0e-4
    assert activity["five_covariant_components_active"] is True
    assert activity["nonabelian_At_cross_Ax_max_norm"] > 1.0e-4
    assert activity["abelianized_Ftx_mutant_witness"] > 1.0e-4

    gauge = rebuilt_receipt["scientific"]["internal_SO3_Ward"]
    assert gauge["bulk_probe_off_shell"] is True
    assert gauge["Euler_equations_imposed"] is False
    assert gauge["complete_same_action_SO3_orbit_claimed"] is False
    assert gauge["complete_same_action_SO3_Ward_claimed"] is False
    assert set(gauge["generator_rows"]) == {"T_1", "T_2", "T_3"}
    for row in gauge["generator_rows"].values():
        assert abs(row["BF_delta_B_integral"]) > 1.0e-3
        assert abs(row["BF_delta_F_integral"]) > 1.0e-3
        assert abs(row["BF_delta_B_integral"] + row["BF_delta_F_integral"]) < 3.0e-18
        assert abs(row["bulk_total_integral_residual"]) < 2.0e-12
        assert row["bulk_local_Linf_residual"] < 2.0e-12
    assert gauge["anisotropic_V4_mutant_witness"] > 1.0e-5
    assert gauge["omit_one_BF_orbit_contribution_witness"] > 1.0e-4
    assert abs(gauge["generator_rows"]["T_2"]["Robin_orbit_variation_integral"]) > 1.0e-4
    assert abs(gauge["generator_rows"]["T_3"]["Robin_orbit_variation_integral"]) > 5.0e-4
    assert gauge["maximum_Robin_orbit_obstruction"] > 5.0e-4


def test_mutation_and_normal_slot_activity_remain_diagnostics_only(
    rebuilt_receipt: dict[str, Any],
) -> None:
    scientific = rebuilt_receipt["scientific"]
    mutants = scientific["mutation_activity_accounting"]
    assert mutants["minimum_omission_witness"] > 1.0e-5
    assert mutants["minimum_sign_flip_witness"] > 1.0e-5
    assert mutants["minimum_special_witness"] == 0.0
    assert mutants["mutant_expected_route_is_nominal_independent_route"] is False
    assert mutants["independent_mutant_oracle_supplied"] is False
    assert mutants["primary_mutant_suite_complete"] is False
    assert "activity/accounting" in mutants["classification"]
    required_special = {
        "broken_pullback_jacobian",
        "wrong_GHY_orientation",
        "freeze_R",
        "frozen_moving_embedding",
        "anisotropic_V4",
        "abelianize_commutators",
        "remove_T_ui_matter",
        "circular_expected_route",
    }
    assert required_special.issubset(mutants["special_mutant_witnesses"])
    assert mutants["special_mutant_witnesses"]["circular_expected_route"] == 0.0
    assert min(
        mutants["special_mutant_witnesses"][key]
        for key in required_special - {"circular_expected_route"}
    ) > 1.0e-5

    flux = scientific["normal_flux_and_matter_shift"]
    assert flux["minimum_normal_slot_omission_witness"] > 1.0e-5
    assert set(flux["normal_slot_rows"]) == {"plus", "minus"}
    assert flux["normal_slots_visible_as_accounting_diagnostics"] is True
    assert flux["complete_normal_and_matter_shift_certificate"] is False
    assert flux["matter_shift"]["T_ui_norm"] > 1.0e-4
    assert flux["matter_shift"]["local_identity_maximum_error"] < 2.0e-8
    assert flux["matter_shift"]["T_ui_activity_witness"] > 1.0e-4
    assert flux["matter_shift"]["independent_same_action_variational_route_supplied"] is False
    decomposition = flux["matter_shift"]["P2_decomposition"]
    assert decomposition["absolute_orthogonal_decomposition_error"] < 2.0e-12
    assert decomposition["legacy_raw_Pq_decomposition_error"] > 1.0e-5


def test_missing_euler_green_yz_and_redteam_keep_every_promotion_false(
    rebuilt_receipt: dict[str, Any],
) -> None:
    scientific = rebuilt_receipt["scientific"]
    decision = scientific["decision"]
    assert set(gate.FAIL_CLOSED_KEYS) == EXPECTED_FAIL_CLOSED_KEYS
    assert gate.ALLOWED_TRUE_PASS_KEYS == EXPECTED_TRUE_PASS_KEYS
    assert all(decision[key] is False for key in EXPECTED_FAIL_CLOSED_KEYS)
    assert {
        key for key, value in decision.items() if key.endswith("_pass") and value is True
    } == EXPECTED_TRUE_PASS_KEYS
    assert decision["v5_6_2_selected_family_primary_candidate_pass"] is False
    assert decision["internal_SO3_direct_orbit_diagnostic_pass"] is False
    assert decision["selected_normal_slots_and_matter_shift_visible_pass"] is False
    assert decision["primary_mutant_suite_pass"] is False
    assert decision["deterministic_freeze_receipt_issued"] is False
    for key in (
        "C1_ACTION_selected_family_pass",
        "N1_ACTION_selected_family_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False

    activity = scientific["field_activity"]
    assert activity["ordinary_coordinate_dependence"] == {
        "t": True,
        "x": True,
        "y": False,
        "z": False,
        "q": True,
    }
    assert activity["all_five_ordinary_coordinate_derivatives_active"] is False
    assert activity["full_5D_coordinate_family_claimed"] is False

    flux = scientific["normal_flux_and_matter_shift"]
    assert flux["full_Euler_Green_identity_claimed"] is False
    assert len(flux["missing_for_full_Green"]) == 3
    assert any("Euler" in item for item in flux["missing_for_full_Green"])
    assert scientific["route_separation_diagnostic"]["upstream_decisions_or_residuals_read"] is False

    open_obligations = rebuilt_receipt["open_obligations_enumerated_before_promotion"]
    assert set(open_obligations) == {
        "convergence",
        "bulk_complete",
        "moving_embedding",
        "off_shell_continuous_extension",
        "same_action_internal_SO3",
        "normal_and_matter_shift",
        "mutation_adequacy",
    }
    assert all(item["closed"] is False for item in open_obligations.values())
    assert "PRIMARY_CANDIDATE_FAIL_CLOSED" in decision["status"]


def test_source_or_literal_action_drift_raises_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = gate.HERE / "artifacts" / gate.SOURCE_PINS["v5_5_4_redteam"].artifact
    real_hash = gate._sha256

    def changed(path: Path) -> str:
        if Path(path) == target:
            return "0" * 64
        return real_hash(path)

    monkeypatch.setattr(gate, "_sha256", changed)
    with pytest.raises(gate.FullMovingV562Error, match="pinned source drift"):
        gate._load_and_pin_sources()
    monkeypatch.setattr(gate, "_sha256", real_hash)

    altered_action = copy.deepcopy(gate.EXACT_ACTION)
    altered_action["full_V4"] = "mutated"
    monkeypatch.setattr(gate, "EXACT_ACTION", altered_action)
    with pytest.raises(gate.FullMovingV562Error, match="literal v5.2 action drift"):
        gate._load_and_pin_sources()


def test_build_payload_is_deterministic_and_matches_stored_artifact(
    stored_receipt: dict[str, Any], rebuilt_receipt: dict[str, Any]
) -> None:
    second = gate.build_payload()
    assert rebuilt_receipt == second
    assert rebuilt_receipt["scientific"] == stored_receipt["scientific"]
    assert rebuilt_receipt["scientific_sha256"] == gate._canonical_sha256(
        rebuilt_receipt["scientific"]
    )
    assert stored_receipt["scientific_sha256"] == gate._canonical_sha256(
        stored_receipt["scientific"]
    )

    assert rebuilt_receipt["provenance"]["generator"]["sha256"] == gate._sha256(
        Path(gate.__file__).resolve()
    )
    current_test = rebuilt_receipt["provenance"]["test"]
    assert current_test == {
        "path": str(gate.TEST.relative_to(gate.REPO)),
        "sha256": gate._sha256(gate.TEST),
        "present_at_generation": True,
    }

    # The committed candidate predates this self-referential test.  Permit only
    # that provenance leaf to differ; every scientific and structural byte must
    # otherwise be regenerated identically.
    normalized = copy.deepcopy(rebuilt_receipt)
    if stored_receipt["provenance"]["test"]["present_at_generation"] is False:
        assert stored_receipt["provenance"]["test"]["sha256"] is None
        normalized["provenance"]["test"] = stored_receipt["provenance"]["test"]
    assert normalized == stored_receipt

    canonical = (
        json.dumps(
            stored_receipt,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    assert gate.OUTPUT.read_bytes() == canonical
