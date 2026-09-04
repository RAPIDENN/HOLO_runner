"""Tests for the v5.6.6.8 restricted-class Euler--Green identity gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

import derive_one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8 as gate


HERE = Path(__file__).resolve().parent

EXPECTED_TRUE_KEYS = frozenset(
    {
        "restricted_family_exact_action_identity_pass",
        "restricted_class_continuity_bound_stated_pass",
        "outer_radial_Green_form_vanishes_exactly_pass",
    }
)
EXPECTED_FALSE_KEYS = frozenset(
    {
        "declared_collocation_uniform_stability_pass",
        "route_C_literal_Euler_contraction_is_Euler_operator_pass",
        "uniform_N_to_infinity_bridge_pass",
        "spectral_N_convergence_pass",
        "uniform_stability_pass",
        "periodic_box_exhaustion_and_tail_control_pass",
        "density_union_C_N_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    }
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    if not gate.OUTPUT.exists():
        pytest.fail(f"missing receipt {gate.OUTPUT.name}; run the derive first")
    return json.loads(gate.OUTPUT.read_text())


def _canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def test_generator_imports_no_one_omega_modules() -> None:
    tree = ast.parse(Path(gate.__file__).read_text())
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    assert not any("one_omega_topological_so3" in name for name in names)
    assert not any(name in {"importlib", "runpy", "torch"} for name in names)


def test_schema_and_pins(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["frozen_checkpoint_commit"] == gate.FROZEN_COMMIT
    assert pins["literal_v5_2_action_sha256"] == gate.LITERAL_V5_2_ACTION_SHA256
    assert pins["C2_multi_N_primitive_bundle_sha256"] == gate.BUNDLE_SHA256
    assert pins["v5_6_6_7_receipt_sha256"] == gate.V5667_SHA256
    assert gate._sha256(gate.BUNDLE_PATH) == gate.BUNDLE_SHA256
    assert gate._sha256(gate.V5667_PATH) == gate.V5667_SHA256


def test_decision_allowlist(receipt: dict) -> None:
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key
    assert not any(k.endswith("_pass") and v is True for k, v in decision.items() if k not in EXPECTED_TRUE_KEYS)


def test_symbolic_identity_all_cases(receipt: dict) -> None:
    cases = receipt["scientific"]["symbolic_euler_green"]
    assert [tuple(c["coordinates"]) for c in cases] == [tuple(c["coordinates"]) for c in gate.SYMBOLIC_CASES]
    for case in cases:
        assert case["identity_dL_equals_E_dq_plus_div_H"] is True
        assert case["residual"] == "0"
        assert case["interface_functional_periodic_IBP_exact"] is True
        assert case["interface_max_tangential_field_derivative_order"] <= 2
        assert case["interface_max_radial_field_derivative_order"] <= 3
    route_c = [c for c in cases if tuple(c["coordinates"]) == ("theta", "rho")]
    assert len(route_c) == 1
    assert route_c[0]["route_C_symmetric_split_representative_exact"] is True
    assert route_c[0]["route_C_literal_current_subtraction_is_derivative_free"] is False
    assert route_c[0]["route_C_literal_current_offending_dq_derivatives"]


def test_symbolic_identity_regenerates_for_the_small_case() -> None:
    result = gate.symbolic_euler_green_case(("theta", "rho"), 1)
    assert result["identity_dL_equals_E_dq_plus_div_H"] is True
    assert result["route_C_symmetric_split_representative_exact"] is True
    assert result["route_C_literal_current_subtraction_is_derivative_free"] is False


def test_radial_junction(receipt: dict) -> None:
    radial = receipt["scientific"]["radial_junction"]
    assert radial["declared_C2_jets_pass"] is True
    assert radial["h0_jets_rho0"] == ["1", "0", "0"]
    assert radial["h0_jets_rho1"] == ["0", "0", "0"]
    assert radial["h1_jets_rho0"] == ["0", "1", "0"]
    assert radial["h1_jets_rho1"] == ["0", "0", "0"]
    assert radial["bumps_jets_rho0_all_zero"] is True
    assert radial["bumps_jets_rho1_all_zero"] is True
    assert radial["K_max_checked"] == gate.RADIAL_K_MAX
    assert radial["class_is_C2_across_zero_extension"] is True
    assert radial["class_is_C3_across_zero_extension"] is False
    regenerated = gate.radial_junction_certificate(gate.RADIAL_K_MAX)
    assert regenerated == radial


def test_collocation_reimplementation_matches_bundle_labels(receipt: dict) -> None:
    bundle = json.loads(gate.BUNDLE_PATH.read_text())
    for N, labels in bundle["nested_truncations"]["basis_labels_by_N"].items():
        assert gate.declared_collocation_matrix(int(N))[1] == list(labels)
    assert receipt["scientific"]["bundle_cross_check"] == {
        "basis_labels_match_bundle": True,
        "radial_profiles_match_bundle": True,
    }


def test_collocation_stability_negative_witness(receipt: dict) -> None:
    stability = receipt["scientific"]["collocation_stability"]
    assert stability["N_max"] == gate.N_MAX_STABILITY
    assert stability["declared_collocation_uniformly_stable"] is False
    assert stability["first_alert_N"] is not None
    assert stability["first_alert_N"] > 3, "the finite N=1,2,3 receipts must stay unaffected"
    assert stability["worst_condition_number"] > gate.STABILITY_ALERT_CONDITION
    rows = {row["N"]: row for row in stability["sampled_rows"]}
    for N in (1, 2, 3):
        assert rows[N]["condition_number"] < 10.0
    # spot re-measure one sampled row
    N = max(rows)
    V, _ = gate.declared_collocation_matrix(N)
    assert np.isclose(np.linalg.cond(V), rows[N]["condition_number"], rtol=1e-6)
    for row in stability["equispaced_1d_contrast"]:
        assert row["condition_number"] < 2.0


def test_theorem_statement_present(receipt: dict) -> None:
    theorem = receipt["scientific"]["theorem"]
    for key in ("class", "norm", "margins", "part_i_exact_identity", "part_ii_continuity", "part_iii_convergence_on_the_continuum_class", "what_remains"):
        assert isinstance(theorem[key], str) and len(theorem[key]) > 80
    assert "not machine-checked" in receipt["scientific"]["analytic_only"]["sobolev_continuity_bound"]
    assert receipt["scientific"]["machine_checked"]["route_C_literal_current_defines_an_Euler_contraction"] is False


def test_independence_boundary(receipt: dict) -> None:
    boundary = receipt["independence_boundary"]
    assert boundary["imports_action_evaluators"] is False
    assert boundary["imports_one_omega_modules"] is False
    assert boundary["reads_upstream_expected_values"] is False


def test_canonical_bytes_and_provenance(receipt: dict) -> None:
    assert gate.OUTPUT.read_text() == json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(Path(gate.__file__))
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
