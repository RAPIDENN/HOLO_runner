"""Tests for the v5.6.6.10 quadrature saturation and bridge ledger gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

import derive_one_omega_topological_so3_route_c_quadrature_saturation_bridge_ledger_v5_6_6_10 as gate


EXPECTED_TRUE_KEYS = frozenset({"route_c_tangential_ladders_saturated_pass", "route_c_radial_ladders_geometric_contraction_pass"})
EXPECTED_FALSE_KEYS = frozenset(
    {
        "uniform_N_to_infinity_bridge_pass",
        "uniform_stability_pass",
        "spectral_N_convergence_pass",
        "restricted_family_exact_action_identity_pass",
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
    assert not any(name in {"importlib", "runpy", "torch", "scipy", "sympy"} for name in names)


def test_schema_and_pins(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["v5_6_6_5_receipt_sha256"] == gate.V5665_SHA256 == gate._sha256(gate.V5665_PATH)
    assert pins["v5_6_6_8_receipt_sha256"] == gate.V5668_SHA256 == gate._sha256(gate.V5668_PATH)
    assert pins["v5_6_6_9_receipt_sha256"] == gate.V5669_SHA256 == gate._sha256(gate.V5669_PATH)
    assert pins["C2_multi_N_primitive_bundle_sha256"] == gate.BUNDLE_SHA256 == gate._sha256(gate.BUNDLE_PATH)
    assert len(gate.FROZEN_COMMIT) == 40


def test_decision_allowlist(receipt: dict) -> None:
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key


def test_ladders(receipt: dict) -> None:
    lad = receipt["scientific"]["refinement_ladders"]
    assert lad["tangential_all_saturated"] is True
    assert lad["radial_all_geometric"] is True
    assert [(m["N"], m["K"]) for m in lad["members"]] == list(gate.EXPECTED_MEMBERS)
    for member in lad["members"]:
        t, r = member["tangential"], member["radial"]
        assert t["components"] == 21 and r["components"] == 21
        assert len(t["steps"]) == 2 and len(r["steps"]) == 2
        assert t["saturated_at_relative"] is True
        assert t["worst_relative_difference"] <= gate.TANGENTIAL_SATURATION_RELATIVE_TOLERANCE
        assert r["geometric_contraction"] is True
        assert 0.0 < r["second_over_first_step_ratio"] <= gate.RADIAL_CONTRACTION_RATIO_MAX
        assert r["geometric_extrapolated_tail_rel"] <= gate.RADIAL_EXTRAPOLATED_TAIL_RELATIVE_MAX
        assert r["saturated_at_relative"] is False, "radial ladders are honestly NOT saturated"
        assert member["upstream_convergence_pass"] is True
    assert lad["worst_tangential_relative_difference"] < 1.0e-9
    assert 0.0 < lad["radial_rate_per_node_estimate"] < 0.5
    v5665 = json.loads(gate.V5665_PATH.read_text())
    assert gate.ladder_audit(v5665) == lad


def test_ladder_differences_reject_order_drift() -> None:
    with pytest.raises(gate.LedgerGateError):
        gate._ladder_differences({"11": {"x": 0.0}, "13": {"x": 0.0}}, gate.EXPECTED_TANGENTIAL_ORDERS)


def test_ladder_differences_detect_unsaturated_ladder() -> None:
    records = {"11": {"x": 1.0}, "13": {"x": 1.001}, "15": {"x": 1.0011}}
    result = gate._ladder_differences(records, gate.EXPECTED_TANGENTIAL_ORDERS)
    assert result["saturated_at_relative"] is False
    assert 0.0 < result["second_over_first_step_ratio"] < 1.0
    assert result["geometric_contraction"] is False  # ratio 0.1 but the extrapolated tail ~1e-5 exceeds 1e-8


def test_integrand_structure(receipt: dict) -> None:
    structure = receipt["scientific"]["integrand_structure"]
    assert structure["max_tangential_wavevector_radius"] == 1
    assert structure["single_direction"] is True
    assert structure["tangential_directions"] == ["1*x0+1*x1"]
    bundle = json.loads(gate.BUNDLE_PATH.read_text())
    assert gate.integrand_structure(bundle) == structure


def test_strip_width_is_indicative_only(receipt: dict) -> None:
    strip = receipt["scientific"]["implied_strip_width"]
    assert strip["used_in_decision"] is False
    assert strip["q_theta"] == 11
    assert strip["implied_d_lower_bound_assuming_M_d_order_one"] > 1.0


def test_ledger(receipt: dict) -> None:
    ledger = receipt["scientific"]["bridge_component_ledger"]
    assert ledger["i_exact_identity_on_class"]["sha256"] == gate.V5668_SHA256
    assert ledger["ii_continuity_bound"]["machine_checked"] is None
    assert ledger["iii_N_independent_retraction"]["sha256"] == gate.V5669_SHA256
    assert ledger["iv_finite_certificates_at_saturation"]["keys"] == ["route_c_tangential_ladders_saturated_pass", "route_c_radial_ladders_geometric_contraction_pass"]
    assert "belongs to the operator" in ledger["what_the_ledger_means"]
    assert len(ledger["still_outside_the_bridge"]) == 4
    assert "bridge_key" in receipt["open_obligation"]


def test_canonical_bytes_and_provenance(receipt: dict) -> None:
    assert gate.OUTPUT.read_text() == json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(Path(gate.__file__))
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
