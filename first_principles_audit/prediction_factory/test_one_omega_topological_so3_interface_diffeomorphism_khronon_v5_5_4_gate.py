#!/usr/bin/env python3
"""Adversarial tests for the additive v5.5.4 interface Ward receipt.

The expensive higher-jet calculation is executed by the generator.  These
tests audit its immutable receipt without silently launching another thermal
workload; byte reproducibility is checked by running the generator a second
time as a separate, explicitly scheduled validation step.
"""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

if __package__:
    from . import derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate as gate
else:
    import derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate as gate


@pytest.fixture(scope="module")
def receipt() -> dict:
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def test_source_is_additive_and_imports_no_earlier_gate_helper(receipt: dict) -> None:
    tree = ast.parse(Path(gate.__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = (
        "classical_v5_2_gate",
        "green_identity_v5_5_candidate_gate",
        "restricted_c1_n1_v5_6_gate",
        "adm_induced_chain_v5_5_2_gate",
        "adm_induced_chain_v5_5_2_redteam",
    )
    assert not any(any(token in module for token in forbidden) for module in imported)
    assert receipt["earlier_gate_helpers_imported"] == []


def test_exact_lineage_artifacts_are_byte_pinned(receipt: dict) -> None:
    assert gate._sha256(gate.V5_2_ARTIFACT) == gate.EXPECTED_V5_2_SHA256
    assert gate._sha256(gate.V5_5_2_PRIMARY) == gate.EXPECTED_PRIMARY_V5_5_2_SHA256
    assert gate._sha256(gate.V5_5_2_REDTEAM) == gate.EXPECTED_REDTEAM_V5_5_2_SHA256
    assert receipt["lineage"] == {
        "v5_2_artifact_sha256": gate.EXPECTED_V5_2_SHA256,
        "v5_5_2_primary_artifact_sha256": gate.EXPECTED_PRIMARY_V5_5_2_SHA256,
        "v5_5_2_redteam_artifact_sha256": gate.EXPECTED_REDTEAM_V5_5_2_SHA256,
    }


def test_literal_action_and_diffeomorphism_convention_are_explicit(receipt: dict) -> None:
    ledger = receipt["formula_ledger"]
    action = ledger["selected_literal_action"]
    assert action["terms"] == "S_interface=S_fol_lower+S_wall0+S_R_intrinsic"
    assert action["u"].startswith("u_mu=-N partial_mu T")
    assert "Rcal=h^am h^bn R_abmn[gamma]+K^2-K_mn K^mn" == action["Rcal"]
    assert "Rcal^2" in action["Rcal_squared"]
    convention = ledger["infinitesimal_diffeomorphism_convention"]
    assert convention["metric"] == "delta_xi gamma_mn=L_xi gamma_mn"
    assert convention["khronon"] == "delta_xi T=xi^r partial_r T"
    assert convention["Omega"] == "delta_xi Omega=xi^r partial_r Omega"
    assert convention["psi"].endswith("=L_xi psi_m")
    assert "not the SO(3) gauge Ward" in ledger["separation"]


def test_all_fields_depend_on_all_four_coordinates_off_shell(receipt: dict) -> None:
    activity = receipt["runtime"]["field_activity"]
    assert receipt["runtime"]["spacetime_dimension"] == 4
    assert activity["all_four_coordinates_active"] is True
    assert activity["minimum_field_coordinate_derivative_RMS"] > 1.0e-4
    for field in ("gamma", "T", "Omega", "psi"):
        assert len(activity["coordinate_derivative_RMS"][field]) == 4
        assert min(activity["coordinate_derivative_RMS"][field]) > 1.0e-4
    assert activity["boundary_face_count"] == 8
    assert activity["boundary_xi_exact_max"] == 0.0


def test_underresolved_gauss_volume_sum_is_retained_as_a_failed_diagnostic(
    receipt: dict,
) -> None:
    probes = receipt["runtime"]["compact_arbitrary_xi_probes"]
    high = [row for row in probes if row["quadrature_order_per_coordinate"] == 3]
    assert len(high) == 2
    for row in high:
        assert row["weak_Ward_absolute_residual"] > 1.0e-3
        assert abs(row["integrated_density_divergence"]) > 1.0e-3
        assert row["weak_sum_vs_density_divergence_error"] < 2.0e-9
        assert row["minimum_absolute_slot_contribution"] > 1.0e-6
    assert receipt["decision"]["underresolved_Gauss_volume_Ward_diagnostic_pass"] is False


def test_failed_gauss_convergence_is_explicit_and_not_relabelled_green(receipt: dict) -> None:
    convergence = receipt["runtime"]["compact_weak_quadrature_convergence"]
    assert set(convergence) == {"xi_variant_0", "xi_variant_1"}
    for row in convergence.values():
        assert row["orders"] == [2, 3]
        assert row["reduction_factor_high_over_low"] >= 0.25
        assert row["high_order_integrated_divergence_absolute"] > 1.0e-3
        assert row["certified"] is False
    assert receipt["decision"]["compact_divergence_quadrature_convergence_pass"] is False


def test_compact_weak_ward_closes_by_runtime_local_identity_and_eight_face_stokes(
    receipt: dict,
) -> None:
    runtime = receipt["runtime"]
    stokes = runtime["compact_Stokes_boundary_flux"]
    assert set(stokes) == {"xi_variant_0", "xi_variant_1"}
    for row in stokes.values():
        assert row["face_count"] == 8
        assert len(row["faces"]) == 8
        assert row["boundary_zero_obtained_from_runtime_fields"] is True
        assert row["maximum_boundary_xi"] < 2.0e-15
        assert row["maximum_boundary_action_density"] > 1.0e-3
        assert row["maximum_boundary_flux_density"] < 2.0e-14
        assert row["total_oriented_boundary_flux_absolute"] < 2.0e-14
    assert max(runtime["selected_family_Stokes_weak_residual_bounds"].values()) < 2.0e-7
    assert receipt["decision"]["local_density_Ward_equals_divergence_pass"] is True
    assert receipt["decision"]["runtime_boundary_Stokes_flux_zero_pass"] is True
    assert receipt["decision"]["compact_xi_weak_Ward_zero_by_local_Stokes_pass"] is True


def test_local_density_identity_and_three_derivative_routes_agree(receipt: dict) -> None:
    probes = receipt["runtime"]["compact_arbitrary_xi_probes"]
    for row in probes:
        assert row["local_density_covariance_L2"] < 2.0e-8
        assert row["local_density_covariance_Linf"] < 2.0e-7
        assert row["reverse_vs_forward_local_slot_max_error"] < 2.0e-9
        assert min(row["local_slot_L2_norms"].values()) > 1.0e-6
        assert row["finite_difference_vs_automatic_sum_error"] < 2.0e-7
        assert row["density_variation_RMS"] > 1.0e-5


def test_every_required_mutant_has_a_nonvacuous_witness(receipt: dict) -> None:
    mutants = receipt["runtime"]["mutant_witnesses"]
    required_fragments = (
        "omit_E_T",
        "omit_metric_stress",
        "omit_E_Omega",
        "omit_E_psi",
        "flip_metric_sign",
        "flip_T_sign",
        "flip_Omega_sign",
        "flip_psi_sign",
        "scalarize_psi_covector",
        "circular_integrated_Euler",
        "force_T_on_shell",
        "Killing_only_or_constant_background_activity_loss",
    )
    for fragment in required_fragments:
        assert any(fragment in name for name in mutants)
    assert min(mutants.values()) > 1.0e-6
    assert receipt["runtime"]["vacuous_Killing_only_probe_rejected"] is True


def test_weak_residual_is_a_gate_not_diagnostic_metadata(receipt: dict) -> None:
    runtime = copy.deepcopy(receipt["runtime"])
    runtime["selected_family_Stokes_weak_residual_bounds"]["xi_variant_0"] = 1.0e-3
    assert gate._decision(runtime)["compact_xi_weak_Ward_zero_by_local_Stokes_pass"] is False
    assert gate._decision(runtime)["candidate_checks_pass"] is False


def test_divergence_agreement_is_a_gate_not_diagnostic_metadata(receipt: dict) -> None:
    runtime = copy.deepcopy(receipt["runtime"])
    runtime["compact_arbitrary_xi_probes"][0]["weak_sum_vs_density_divergence_error"] = 1.0e-3
    assert gate._decision(runtime)["local_density_Ward_equals_divergence_pass"] is False
    assert gate._decision(runtime)["candidate_checks_pass"] is False


def test_failed_quadrature_convergence_does_not_override_local_stokes_gate(
    receipt: dict,
) -> None:
    runtime = copy.deepcopy(receipt["runtime"])
    runtime["compact_weak_quadrature_convergence"]["xi_variant_0"]["certified"] = False
    assert gate._decision(runtime)["compact_divergence_quadrature_convergence_pass"] is False
    assert gate._decision(runtime)["candidate_checks_pass"] is True


def test_runtime_boundary_flux_is_a_gate_not_a_hardcoded_zero(receipt: dict) -> None:
    runtime = copy.deepcopy(receipt["runtime"])
    row = runtime["compact_Stokes_boundary_flux"]["xi_variant_0"]
    row["maximum_boundary_xi"] = 1.0e-3
    row["maximum_boundary_flux_density"] = 1.0e-3
    row["total_oriented_boundary_flux_absolute"] = 1.0e-3
    assert gate._decision(runtime)["runtime_boundary_Stokes_flux_zero_pass"] is False
    assert gate._decision(runtime)["candidate_checks_pass"] is False


def test_no_so3_or_downstream_promotion_is_inherited(receipt: dict) -> None:
    decision = receipt["decision"]
    assert decision["SO3_gauge_Ward_inherited_pass"] is False
    assert decision["candidate_checks_pass"] is True
    assert decision["continuum_all_configurations_theorem_pass"] is False
    for key in gate.FAIL_CLOSED_KEYS:
        assert decision[key] is False


def test_artifact_is_canonical_and_provenance_bound(receipt: dict) -> None:
    stored_bytes = gate.OUTPUT.read_bytes()
    canonical = (
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    assert stored_bytes == canonical
    assert receipt["provenance"]["generator_sha256"] == gate._sha256(
        Path(gate.__file__).resolve()
    )
    assert receipt["provenance"]["test_sha256"] == gate._sha256(gate.TEST)
    assert receipt["provenance"]["dtype"] == "torch.float64"


def test_late_lineage_change_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    real_sha = gate._sha256

    def changed(path: Path) -> str:
        if path == gate.V5_5_2_REDTEAM:
            return "0" * 64
        return real_sha(path)

    monkeypatch.setattr(gate, "_sha256", changed)
    with pytest.raises(gate.InterfaceWardV554Error, match="lineage byte hash mismatch"):
        gate.load_lineage()
