"""Tests for the v5.6.6.13 everywhere-margins (Weyl + Lipschitz) certificate."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

import derive_one_omega_topological_so3_pinned_members_margins_everywhere_weyl_lipschitz_v5_6_6_13 as gate


EXPECTED_TRUE_KEYS = frozenset({"pinned_members_margins_everywhere_certified_pass"})
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
    assert source.count("spec_from_file_location") == 1
    for forbidden in ("independent_euler_green_route_c", "precision_stabilized_route_c", "ad_fd5_route_c", "three_way"):
        assert forbidden not in source, forbidden


def test_schema_pins_and_lease(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["C2_multi_N_primitive_bundle_sha256"] == gate.BUNDLE_SHA256 == gate._sha256(gate.BUNDLE_PATH)
    assert pins["v5_6_4_2_pointwise_decoder_sha256"] == gate.DECODER_SHA256 == gate._sha256(gate.DECODER_PATH)
    assert pins["v5_6_6_11_receipt_sha256"] == gate.V56611_SHA256 == gate._sha256(gate.V56611_PATH)
    assert receipt["independence_boundary"]["edits_v5_6_6_11"] is False
    assert receipt["independence_boundary"]["imports_action_evaluators"] is False
    upstream = json.loads(gate.V56611_PATH.read_text())
    assert upstream["decision"]["pinned_members_margins_everywhere_on_collar_pass"] is False  # still fail-closed upstream by design
    assert len(gate.FROZEN_COMMIT) == 40


def test_decision_allowlist(receipt: dict) -> None:
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key


def test_bernstein_bound_is_an_upper_bound() -> None:
    rng = np.random.default_rng(1)
    x = np.linspace(0.0, 1.0, 4001)
    for _ in range(50):
        coefficients = rng.normal(size=rng.integers(1, 10))
        bound = gate.polynomial_sup_on_unit_interval(coefficients)
        assert bound >= np.max(np.abs(np.polynomial.polynomial.polyval(x, coefficients))) - 1e-12
    assert gate.polynomial_sup_on_unit_interval(np.array([0.5])) == 0.5


def test_profile_polynomials_match_direct_formulas() -> None:
    p = gate.profile_polynomials(3)
    rho = np.linspace(0.0, 1.0, 11)
    assert np.allclose(np.polynomial.polynomial.polyval(rho, p["h0"]), 1 - 10 * rho**3 + 15 * rho**4 - 6 * rho**5)
    assert np.allclose(np.polynomial.polynomial.polyval(rho, p["h1"]), rho * (1 - 10 * rho**3 + 15 * rho**4 - 6 * rho**5))
    for j in range(3):
        direct = 64 * rho**3 * (1 - rho) ** 3 * np.polynomial.legendre.legval(2 * rho - 1, [0] * j + [1])
        assert np.allclose(np.polynomial.polynomial.polyval(rho, p["bumps"][j]), direct, atol=1e-12)


def test_harmonics_roundtrip_and_sup_bounds() -> None:
    theta = 2 * np.pi * np.arange(16) / 16
    samples = 0.3 + 1.2 * np.cos(theta) - 0.7 * np.sin(2 * theta)
    A, B = gate.harmonics(samples[:, None])
    assert np.allclose(A[[0, 1]].ravel(), [0.3, 1.2]) and np.isclose(B[2, 0], -0.7)
    fine = np.linspace(0, 2 * np.pi, 5001)
    values = gate.evaluate_harmonics(A, B, fine).ravel()
    assert np.max(np.abs(values)) <= gate.trig_sup_bound(A, B) + 1e-12
    derivative = np.gradient(values, fine)
    assert np.max(np.abs(derivative[10:-10])) <= gate.trig_derivative_sup_bound(A, B) + 1e-6


def test_everywhere_certificate(receipt: dict) -> None:
    members = receipt["scientific"]["members"]
    assert [[m["N"], m["K"]] for m in members] == [[1, 1], [2, 2], [3, 3]]
    for m in members:
        assert m["pass"] is True
        assert m["harmonic_exactness"]["pass"] is True
        assert m["harmonic_exactness"]["worst_reconstruction_error_off_grid"] < gate.EXACTNESS_TOLERANCE
        k = m["khronon"]
        assert k["gamma_lorentzian_on_grid"] is True
        assert k["gamma_min_abs_eigenvalue_everywhere"] > gate.SIGNATURE_EIGENVALUE_MARGIN
        assert k["T_norm2_max_everywhere"] < -gate.TIMELIKE_MARGIN
        assert k["T_norm2_max_everywhere"] > k["T_norm2_max_grid"]  # the bound is looser than the grid, as it must be
        for side in ("plus", "minus"):
            s = m["sides"][side]
            assert s["pass"] is True
            assert s["metric"]["lorentzian_on_grid"] is True
            assert s["metric"]["min_abs_eigenvalue_everywhere"] > gate.SIGNATURE_EIGENVALUE_MARGIN
            assert s["metric"]["min_abs_eigenvalue_everywhere"] < s["metric"]["min_abs_eigenvalue_grid"]
            assert s["metric"]["weyl_radius"] > gate.SAFETY
            assert s["Omega"]["Omega_min_everywhere"] > gate.OMEGA_MIN
            assert s["Omega"]["Omega_min_everywhere"] < 1.0
            assert s["rotation"]["clearance_everywhere"] > gate.ROTATION_CUT_LOCUS_MARGIN
            assert s["rotation"]["angle_upper_bound"] >= s["rotation"]["angle_max_grid"] - 1e-12
            assert s["rotation"]["angle_upper_bound"] < math.pi
    summary = receipt["scientific"]["summary"]
    assert summary["min_abs_metric_eigenvalue_everywhere"] > 1.0
    assert summary["max_weyl_radius"] < 0.05
    assert summary["worst_harmonic_reconstruction_error"] < 1e-14


def test_member_certificate_regenerates_for_N2(receipt: dict) -> None:
    bundle = json.loads(gate.BUNDLE_PATH.read_text())
    decoder = gate.load_pinned_decoder()
    regenerated = gate.member_certificate(decoder, bundle, bundle["primary_members"][1])
    recorded = receipt["scientific"]["members"][1]
    assert regenerated["pass"] is True
    for side in ("plus", "minus"):
        for block in ("metric", "Omega", "rotation"):
            for key, value in recorded["sides"][side][block].items():
                if isinstance(value, float):
                    assert np.isclose(regenerated["sides"][side][block][key], value, rtol=1e-10, atol=1e-14), (side, block, key)


def test_method_and_boundaries(receipt: dict) -> None:
    method = receipt["scientific"]["method"]
    assert "Weyl" in method["metric"] and "Bernstein" in method["metric"]
    assert "triangle inequality" in method["rotation"]
    assert "not interval arithmetic" in method["rounding"]
    assert len(receipt["scientific"]["analytic_not_machine_checked"]) == 2
    assert "flip_upstream_key" in receipt["open_obligation"]


def test_canonical_bytes_and_provenance(receipt: dict) -> None:
    assert gate.OUTPUT.read_text() == json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(Path(gate.__file__))
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
