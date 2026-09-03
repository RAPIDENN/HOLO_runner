#!/usr/bin/env python3
"""Fail-closed tests for the v5.5.4 freeze/v5.6.1 quarantine receipt."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

if __package__:
    from . import derive_one_omega_topological_so3_v5_6_1_quarantine_gate as gate
else:
    import derive_one_omega_topological_so3_v5_6_1_quarantine_gate as gate


EXPECTED_FORCED_FALSE_KEYS = {
    "full_bulk_diffeomorphism_Ward_pass",
    "complete_moving_embedding_Ward_pass",
    "continuum_all_configurations_theorem_pass",
    "complete_v5_2_all_field_normal_embedding_pass",
    "full_off_shell_Green_theorem_accepted",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "N4_JUNCTION_BENDING_pass",
    "P4_full_same_action_pass",
    "v5_6_promotion_authorized",
    "frozen_v5_6_receipt_rehabilitated",
    "B4_pass",
    "B5_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "unrestricted_large_gauge_sector_pass",
    "publication_authorized",
}
EXPECTED_TRUE_PASS_KEYS = {
    "ADM_induced_selected_local_chain_primary_redteam_pass",
    "internal_SO3_full_5D_primary_redteam_pass",
    "interface_diff_selected_family_primary_redteam_pass",
    "scientific_invariants_coefficients_hashes_residuals_comparison_pass",
    "v5_5_4_selected_4D_family_frozen_lemma_pass",
    "underresolved_Gauss_diagnostic_correctly_red_pass",
    "quarantine_consistency_pass",
}


@pytest.fixture(scope="module")
def receipt() -> dict:
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def test_adjudicator_imports_no_source_gate_helper(receipt: dict) -> None:
    tree = ast.parse(Path(gate.__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert not any("one_omega_topological_so3" in module for module in imported)
    assert receipt["earlier_gate_helpers_imported"] == []


def test_all_seven_inputs_are_final_three_file_byte_pins(receipt: dict) -> None:
    assert set(gate.SOURCES) == {
        "v5_2_action_charter",
        "v5_5_2_primary", "v5_5_2_redteam",
        "v5_5_3_primary", "v5_5_3_redteam",
        "v5_5_4_primary", "v5_5_4_redteam",
    }
    for name, contract in gate.SOURCES.items():
        assert gate._sha256(Path(contract["path"])) == contract["sha256"]
        assert gate._sha256(Path(contract["generator_path"])) == contract["generator_sha256"]
        assert gate._sha256(Path(contract["test_path"])) == contract["test_sha256"]
        recorded = receipt["source_hashes"][name]
        for key in ("sha256", "schema", "generator_sha256", "test_sha256"):
            assert recorded[key] == contract[key]


def test_v554_freezes_only_as_selected_family_4d_lemma(receipt: dict) -> None:
    decision = receipt["decision"]
    assert decision["ADM_induced_selected_local_chain_primary_redteam_pass"] is True
    assert decision["internal_SO3_full_5D_primary_redteam_pass"] is True
    assert decision["interface_diff_selected_family_primary_redteam_pass"] is True
    assert decision["scientific_invariants_coefficients_hashes_residuals_comparison_pass"] is True
    assert decision["v5_5_4_selected_4D_family_frozen_lemma_pass"] is True
    assert decision["underresolved_Gauss_diagnostic_correctly_red_pass"] is True
    assert decision["quarantine_consistency_pass"] is True
    assert decision["quarantine_active"] is True
    assert {
        key for key, value in decision.items() if key.endswith("_pass") and value is True
    } == EXPECTED_TRUE_PASS_KEYS
    assert gate.ALLOWED_TRUE_PASS_KEYS == EXPECTED_TRUE_PASS_KEYS


def test_literal_v52_action_and_coefficients_match_independently(receipt: dict) -> None:
    comparison = receipt["scientific_comparison"]
    checks = comparison["checks"]
    assert checks["primary_coefficient_keyset_exact"] is True
    assert checks["redteam_coefficient_keyset_exact"] is True
    assert checks["primary_action_keyset_exact"] is True
    assert checks["redteam_action_keyset_exact"] is True
    assert checks["primary_declared_matches_v5_2"] is True
    assert checks["redteam_declared_matches_v5_2"] is True
    assert checks["shared_coefficients_identical"] is True
    assert checks["primary_interface_literals_match_v5_2"] is True
    assert checks["redteam_six_literals_match_v5_2"] is True
    assert checks["v5_2_total_action_is_complete"] is True
    assert comparison["action_charter"]["exact_total_action"] == (
        "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF"
    )
    coefficients = comparison["coefficient_comparison"]
    assert set(coefficients["primary_declared"]) == {
        "brane_Mb_squared", "lambda_K", "xi", "eta", "B4_bar",
        "k_infinity", "M5_cubed", "compensator_metric_G", "brane_beta",
        "Robin_kappa_hat", "Robin_y",
    }
    assert set(coefficients["redteam_declared"]) == set(
        coefficients["primary_declared"]
    ) | {"material_Z5_per_side", "material_mass_M"}
    for key, value in coefficients["primary_declared"].items():
        assert coefficients["v5_2_parameters"][key] == value
        assert coefficients["redteam_declared"][key] == value


def test_scientific_geometric_contract_is_exact(receipt: dict) -> None:
    comparison = receipt["scientific_comparison"]
    invariant = comparison["scientific_invariants"]
    assert comparison["checks"]["input_lineages_match"] is True
    assert comparison["checks"]["selected_family_geometric_contract_matches"] is True
    assert invariant["interface_dimension"] == 4
    assert invariant["ambient_pullback_control_dimension"] == 5
    assert invariant["compact_xi_probe_count"] == 2
    assert invariant["quadrature_point_count_per_probe"] == 81
    assert invariant["oriented_face_count_per_probe"] == 8
    assert invariant["signed_Euler_JVP_component_count"] == 16
    assert invariant["signed_component_labels"] == gate.COMPONENT_LABELS


def test_raw_primary_residuals_are_recorded_and_within_fixed_contract(receipt: dict) -> None:
    comparison = receipt["scientific_comparison"]
    raw = comparison["raw_residual_comparison"]["primary"]
    assert comparison["checks"]["primary_residuals_within_fixed_tolerances"] is True
    assert raw["local_density_L2"] == [
        1.4606624312675158e-15, 9.820259667674257e-16,
    ]
    assert raw["local_density_Linf"] == [
        6.217248937900877e-15, 3.6637359812630166e-15,
    ]
    assert raw["action_vs_Euler"] == [
        3.604059273243365e-10, 1.3330891945884105e-11,
    ]
    assert raw["Stokes_weak"] == {
        "xi_variant_0": 2.673303242772817e-14,
        "xi_variant_1": 1.5753394109196957e-14,
    }


def test_raw_redteam_residuals_are_recorded_and_within_fixed_contract(receipt: dict) -> None:
    comparison = receipt["scientific_comparison"]
    raw = comparison["raw_residual_comparison"]["redteam"]
    assert comparison["checks"]["redteam_residuals_within_fixed_tolerances"] is True
    assert comparison["checks"]["redteam_tolerance_manifest_exact"] is True
    assert raw["local_density_L2"] == [
        9.518761953148456e-15, 1.0018641083350439e-14,
    ]
    assert raw["local_density_Linf"] == [
        4.1300296516055823e-14, 4.374278717023117e-14,
    ]
    assert raw["component_action_vs_JVP"] == [
        1.3235423867996587e-10, 9.809496270829499e-11,
    ]
    assert raw["pointwise_16_component_additivity"] == [
        3.68594044175552e-14, 2.353672812205332e-14,
    ]
    assert raw["density_route_Linf"] == [
        1.7763568394002505e-15, 1.7763568394002505e-15,
    ]
    assert raw["Stokes_weak"] == {
        "xi_variant_0": 1.412891469954048e-13,
        "xi_variant_1": 1.4964495676395024e-13,
    }
    assert raw["maximum_nominal_closure_error"] == 3.1086244689504383e-9
    assert raw["minimum_mutant_witness"] == 8.833240425992761e-5
    assert raw["minimum_component_local_JVP_RMS"] == [
        0.0001864801933784642, 0.00032160160767221395,
    ]
    assert raw["minimum_absolute_slot_pairing"] == [
        0.004217803262207553, 8.833138664954275e-5,
    ]
    assert raw["minimum_coordinate_activity"] == 0.002626577484441154


def test_required_reexecuted_controls_are_nonvacuous(receipt: dict) -> None:
    controls = receipt["scientific_comparison"]["raw_residual_comparison"]["redteam"][
        "required_control_mutants"
    ]
    assert controls == {
        "R_groupoid_frozen": 0.051751328484065925,
        "anisotropic_full_V4": 0.0018060271543898774,
        "flip_T_ui_matter_sign": 0.5446113165295684,
        "induced_pullback_broken": 1.0931052404825299,
        "omit_T_ui_matter": 0.2723056582569862,
    }
    assert min(controls.values()) > gate.REDTEAM_TOLERANCES["required_mutant_minimum"]


def test_underresolved_gauss_is_archived_raw_and_red(receipt: dict) -> None:
    comparison = receipt["scientific_comparison"]
    assert comparison["checks"]["underresolved_Gauss_preserved_red"] is True
    archived = comparison["archived_red_Gauss_diagnostics"]
    assert set(archived["primary"]) == {"xi_variant_0", "xi_variant_1"}
    assert set(archived["redteam"]) == {"xi_variant_0", "xi_variant_1"}
    assert all(row["certified"] is False for row in archived["primary"].values())
    assert archived["redteam"]["xi_variant_0"]["integrated_coordinate_divergence"] == 0.370311760175908
    assert archived["redteam"]["xi_variant_0"]["weak_Euler_sum"] == 0.3703117599229699
    assert archived["redteam"]["xi_variant_1"]["integrated_coordinate_divergence"] == 0.2618237859002482
    assert archived["redteam"]["xi_variant_1"]["weak_Euler_sum"] == 0.26182378665140504
    assert all(row["certified"] is False for row in archived["redteam"].values())
    assert all(row["used_by_selected_family_decision"] is False for row in archived["redteam"].values())


def test_four_open_obligations_are_explicit_before_c1_n1(receipt: dict) -> None:
    obligations = receipt["open_obligations_before_C1_N1_gate"]
    assert set(obligations) == {
        "convergence", "full_bulk", "moving_embedding", "off_shell_continuous_extension",
    }
    assert all(value.startswith("OPEN:") for value in obligations.values())


def test_bulk_moving_continuum_and_boundary_scopes_stay_red(receipt: dict) -> None:
    evidence = receipt["scope_evidence"]
    assert evidence["full_bulk_diff_is_red"] is True
    assert evidence["moving_embedding_is_red"] is True
    assert evidence["continuum_theorem_is_red_in_both"] is True
    assert evidence["all_field_normal_embedding_is_red"] is True
    assert evidence["BV_BFV_is_red"] is True
    assert evidence["large_gauge_is_red"] is True
    assert set(gate.FORCED_FALSE_KEYS) == EXPECTED_FORCED_FALSE_KEYS
    for key in EXPECTED_FORCED_FALSE_KEYS:
        assert receipt["decision"][key] is False


def test_consumption_policy_denies_promotion(receipt: dict) -> None:
    policy = receipt["consumption_policy"]
    assert policy["frozen_v5_6_modified"] is False
    assert "not promotion authority" in policy["authorization_statement"]
    for token in ("C1", "N1", "v5.6", "B4", "B5", "BV-BFV", "large gauge", "publication"):
        assert token in policy["forbidden"]


def test_scientific_failure_prevents_freeze_even_when_boolean_scopes_are_green(
    receipt: dict,
) -> None:
    evidence = copy.deepcopy(receipt["scope_evidence"])
    checks = copy.deepcopy(receipt["scientific_comparison"]["checks"])
    checks["redteam_six_literals_match_v5_2"] = False
    decision = gate._adjudicate(evidence, checks)
    assert decision["scientific_invariants_coefficients_hashes_residuals_comparison_pass"] is False
    assert decision["v5_5_4_selected_4D_family_frozen_lemma_pass"] is False
    assert decision["quarantine_consistency_pass"] is False
    assert decision["quarantine_active"] is True
    for key in gate.FORCED_FALSE_KEYS:
        assert decision[key] is False


def test_empty_primary_action_or_coefficient_mapping_fails_nonvacuously(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sources = gate._load_sources()
    primary_path = Path(gate.SOURCES["v5_5_4_primary"]["generator_path"])
    real_actions = gate._extract_string_mapping

    def empty_actions(path: Path, assignment: str) -> dict[str, str]:
        if path == primary_path and assignment == "EXPECTED_ACTIONS":
            return {}
        return real_actions(path, assignment)

    monkeypatch.setattr(gate, "_extract_string_mapping", empty_actions)
    comparison = gate._scientific_comparison(sources)
    assert comparison["checks"]["primary_action_keyset_exact"] is False
    assert comparison["checks"]["primary_interface_literals_match_v5_2"] is False
    assert comparison["all_checks_pass"] is False


def test_coefficient_subset_fails_nonvacuously(monkeypatch: pytest.MonkeyPatch) -> None:
    sources = gate._load_sources()
    primary_path = Path(gate.SOURCES["v5_5_4_primary"]["generator_path"])
    real_coefficients = gate._extract_numeric_mapping

    def subset(path: Path, assignment: str) -> dict[str, float]:
        values = real_coefficients(path, assignment)
        if path == primary_path and assignment == "EXPECTED_COEFFICIENTS":
            values.pop("B4_bar")
        return values

    monkeypatch.setattr(gate, "_extract_numeric_mapping", subset)
    comparison = gate._scientific_comparison(sources)
    assert comparison["checks"]["primary_coefficient_keyset_exact"] is False
    assert comparison["checks"]["primary_declared_matches_v5_2"] is False
    assert comparison["all_checks_pass"] is False


@pytest.mark.parametrize(
    "mutation",
    ("redteam_Stokes", "redteam_component_activity", "redteam_mutant", "primary_mutant"),
)
def test_recorded_residual_or_activity_mutants_prevent_freeze(mutation: str) -> None:
    sources = copy.deepcopy(gate._load_sources())
    if mutation == "redteam_Stokes":
        sources["v5_5_4_redteam"]["runtime"][
            "selected_family_Stokes_weak_residual_bounds"
        ]["xi_variant_0"] = 1.0
    elif mutation == "redteam_component_activity":
        sources["v5_5_4_redteam"]["runtime"]["compact_xi_probes"][0][
            "minimum_component_local_JVP_RMS"
        ] = 0.0
    elif mutation == "redteam_mutant":
        sources["v5_5_4_redteam"]["runtime"]["minimum_mutant_witness"] = 0.0
    elif mutation == "primary_mutant":
        sources["v5_5_4_primary"]["runtime"]["minimum_mutant_witness"] = 0.0
    comparison = gate._scientific_comparison(sources)
    failed_key = (
        "primary_residuals_within_fixed_tolerances"
        if mutation == "primary_mutant"
        else "redteam_residuals_within_fixed_tolerances"
    )
    assert comparison["checks"][failed_key] is False
    decision = gate._adjudicate(gate._scope_evidence(sources), comparison["checks"])
    assert decision["v5_5_4_selected_4D_family_frozen_lemma_pass"] is False


def test_second_probe_component_label_mutant_prevents_freeze() -> None:
    sources = copy.deepcopy(gate._load_sources())
    sources["v5_5_4_redteam"]["runtime"]["compact_xi_probes"][1][
        "signed_component_action_and_local_JVP"
    ][0]["component"] = "gamma_bad"
    comparison = gate._scientific_comparison(sources)
    assert comparison["checks"]["selected_family_geometric_contract_matches"] is False
    assert comparison["all_checks_pass"] is False


def test_missing_primary_gauss_rows_cannot_pass_vacuously() -> None:
    sources = copy.deepcopy(gate._load_sources())
    sources["v5_5_4_primary"]["runtime"]["compact_weak_quadrature_convergence"] = {}
    comparison = gate._scientific_comparison(sources)
    assert comparison["checks"]["underresolved_Gauss_preserved_red"] is False
    assert comparison["all_checks_pass"] is False


def test_attempted_c1_or_v56_escape_raises(receipt: dict) -> None:
    for key in ("C1_ACTION_pass", "N1_ACTION_pass", "B4_pass", "B5_pass", "v5_6_promotion_authorized"):
        escaped = copy.deepcopy(receipt["decision"])
        escaped[key] = True
        with pytest.raises(gate.V561QuarantineError, match="illegal downstream promotion"):
            gate._enforce_quarantine(escaped)


def test_unlisted_green_or_frozen_scope_cannot_escape(receipt: dict) -> None:
    escaped = copy.deepcopy(receipt["decision"])
    escaped["invented_5D_completion_pass"] = True
    with pytest.raises(gate.V561QuarantineError, match="unexpected green pass"):
        gate._enforce_quarantine(escaped)
    escaped = copy.deepcopy(receipt["decision"])
    escaped["invented_5D_frozen_lemma"] = True
    with pytest.raises(gate.V561QuarantineError, match="unexpected frozen scope"):
        gate._enforce_quarantine(escaped)


def test_late_source_change_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    target = Path(gate.SOURCES["v5_5_4_redteam"]["path"])
    real_hash = gate._sha256

    def changed(path: Path) -> str:
        if path == target:
            return "0" * 64
        return real_hash(path)

    monkeypatch.setattr(gate, "_sha256", changed)
    with pytest.raises(gate.V561QuarantineError, match="source byte hash mismatch"):
        gate._load_sources()


def test_artifact_is_rebuilt_canonical_and_provenance_bound(receipt: dict) -> None:
    assert receipt == gate.build_payload()
    canonical = (
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    assert gate.OUTPUT.read_bytes() == canonical
    assert receipt["provenance"]["generator_sha256"] == gate._sha256(
        Path(gate.__file__).resolve()
    )
    assert receipt["provenance"]["test_sha256"] == gate._sha256(gate.TEST)
