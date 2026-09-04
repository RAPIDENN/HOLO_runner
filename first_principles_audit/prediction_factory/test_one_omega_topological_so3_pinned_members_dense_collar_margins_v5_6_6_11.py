"""Tests for the v5.6.6.11 dense-collar margins and same-objects gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

import derive_one_omega_topological_so3_pinned_members_dense_collar_margins_v5_6_6_11 as gate


EXPECTED_TRUE_KEYS = frozenset({"pinned_members_margins_on_dense_collar_pass"})
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


def test_generator_imports_only_the_pinned_kinematic_decoder() -> None:
    source = Path(gate.__file__).read_text()
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    assert not any("one_omega_topological_so3" in name for name in names)
    assert not any(name in {"torch", "scipy", "sympy", "runpy"} for name in names)
    # the only dynamic import is the byte-pinned v5.6.4.2 decoder
    assert source.count("spec_from_file_location") == 1
    for forbidden in ("independent_euler_green_route_c", "precision_stabilized_route_c", "ad_fd5_route_c", "three_way"):
        assert forbidden not in source, forbidden  # no Route C / AD / FD5 module is referenced


def test_schema_and_pins(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["C2_multi_N_primitive_bundle_sha256"] == gate.BUNDLE_SHA256 == gate._sha256(gate.BUNDLE_PATH)
    assert pins["v5_6_4_2_pointwise_decoder_sha256"] == gate.DECODER_SHA256 == gate._sha256(gate.DECODER_PATH)
    assert pins["v5_6_6_8_receipt_sha256"] == gate.V5668_SHA256 == gate._sha256(gate.V5668_PATH)
    assert pins["v5_6_6_10_receipt_sha256"] == gate.V56610_SHA256 == gate._sha256(gate.V56610_PATH)
    assert receipt["independence_boundary"]["imports_pinned_kinematic_decoder"] is True
    assert receipt["independence_boundary"]["imports_action_evaluators"] is False
    assert len(gate.FROZEN_COMMIT) == 40


def test_decision_allowlist(receipt: dict) -> None:
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key


def test_margins_are_the_v5_6_4_tolerances(receipt: dict) -> None:
    margins = receipt["scientific"]["margins"]
    assert margins["signature_eigenvalue_margin"] == 2.0e-2
    assert margins["Omega_min"] == 5.0e-1
    assert margins["timelike_margin"] == 2.0e-1
    assert margins["rotation_cut_locus_margin"] == 1.0


def test_dense_collar_margins(receipt: dict) -> None:
    members = receipt["scientific"]["members"]
    assert [[m["N"], m["K"]] for m in members] == [[1, 1], [2, 2], [3, 3]]
    for member in members:
        assert member["pass"] is True
        assert member["grid"] == {"theta_points": gate.THETA_POINTS, "rho_points": gate.RHO_POINTS, "direction": "x0 (all modes depend on x0 + x1)"}
        b = member["boundary"]
        assert b["gamma_lorentzian_everywhere"] is True
        assert b["gamma_min_abs_eigenvalue"] > gate.SIGNATURE_EIGENVALUE_MARGIN
        assert b["khronon_T_norm2_max"] < -gate.TIMELIKE_MARGIN
        assert b["Omega_boundary_min"] > gate.OMEGA_MIN
        for side in ("plus", "minus"):
            s = member["sides"][side]
            assert s["pass"] is True
            assert s["bulk_metric_lorentzian_everywhere"] is True
            assert s["bulk_metric_min_abs_eigenvalue"] > gate.SIGNATURE_EIGENVALUE_MARGIN
            assert s["bulk_Omega_min"] > gate.OMEGA_MIN
            assert s["rotation_cut_locus_clearance"] > gate.ROTATION_CUT_LOCUS_MARGIN
            assert s["rotation_orthogonality_residual"] < 1.0e-10
            assert s["rho1_reference_residual"] < 1.0e-12
    clearance = receipt["scientific"]["clearance_summary"]
    assert clearance["min_abs_metric_eigenvalue_over_all"] > gate.SIGNATURE_EIGENVALUE_MARGIN
    assert clearance["min_Omega_over_all"] > gate.OMEGA_MIN
    assert clearance["max_khronon_T_norm2_over_all"] < -gate.TIMELIKE_MARGIN
    assert clearance["min_cut_locus_clearance_over_all"] > gate.ROTATION_CUT_LOCUS_MARGIN


def test_member_margins_regenerate_for_N1(receipt: dict) -> None:
    bundle = json.loads(gate.BUNDLE_PATH.read_text())
    decoder = gate.load_pinned_decoder()
    regenerated = gate.member_margins(decoder, bundle, bundle["primary_members"][0])
    recorded = receipt["scientific"]["members"][0]
    assert regenerated["pass"] is True
    for side in ("plus", "minus"):
        assert np.isclose(regenerated["sides"][side]["bulk_metric_min_abs_eigenvalue"], recorded["sides"][side]["bulk_metric_min_abs_eigenvalue"], rtol=1e-12)
        assert np.isclose(regenerated["sides"][side]["bulk_Omega_min"], recorded["sides"][side]["bulk_Omega_min"], rtol=1e-12)


def test_radial_profiles_match_the_c2_contract() -> None:
    rho = np.array([0.0, 0.5, 1.0])
    p = gate.radial_profiles(rho, 3)
    assert np.allclose(p["h0"], [1.0, 0.5, 0.0])
    assert np.allclose(p["h1"], [0.0, 0.25, 0.0])
    assert np.allclose(p["bumps"][[0, 2]], 0.0)
    assert p["bumps"].shape == (3, 3)


def test_packed_symmetric5_roundtrip() -> None:
    packed = np.arange(15.0)
    full = gate._sym5_from_packed(packed)
    assert np.allclose(full, full.T)
    assert full[0, 4] == 4.0 and full[4, 0] == 4.0 and full[4, 4] == 14.0


def test_same_objects_theorem_recorded(receipt: dict) -> None:
    theorem = receipt["scientific"]["same_objects_theorem"]
    assert len(theorem["hypotheses_machine_checked"]) == 4
    assert "no analyticity hypothesis" in theorem["statement"]
    assert any("classical" in item for item in theorem["analytic_not_machine_checked"])
    assert any("gap 4" in item for item in theorem["still_open_after_this_gate"])
    assert any("gap 5" in item for item in theorem["still_open_after_this_gate"])
    assert "interval" in receipt["scientific"]["between_grid_points"].lower()


def test_canonical_bytes_and_provenance(receipt: dict) -> None:
    assert gate.OUTPUT.read_text() == json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(Path(gate.__file__))
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
