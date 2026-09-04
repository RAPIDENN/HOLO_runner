"""Tests for the v5.6.6.9 common-first explicit retraction gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

import derive_one_omega_topological_so3_common_first_explicit_retraction_v5_6_6_9 as gate


EXPECTED_TRUE_KEYS = frozenset(
    {
        "common_first_gluing_is_explicit_graph_pass",
        "pointwise_retraction_N_independent_lipschitz_bound_pass",
    }
)
EXPECTED_FALSE_KEYS = frozenset(
    {
        "uniform_stability_pass",
        "spectral_N_convergence_pass",
        "uniform_N_to_infinity_bridge_pass",
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
    assert not any(name in {"importlib", "runpy", "torch", "scipy"} for name in names)


def test_schema_and_pins(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["frozen_checkpoint_commit"] == gate.FROZEN_COMMIT
    assert pins["C2_multi_N_primitive_bundle_sha256"] == gate.BUNDLE_SHA256
    assert pins["v5_6_6_8_receipt_sha256"] == gate.V5668_SHA256
    assert gate._sha256(gate.BUNDLE_PATH) == gate.BUNDLE_SHA256
    assert gate._sha256(gate.V5668_PATH) == gate.V5668_SHA256


def test_decision_allowlist(receipt: dict) -> None:
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key


def test_graph_structure(receipt: dict) -> None:
    graph = receipt["scientific"]["graph_structure"]
    for key in (
        "metric_row_vanishes_identically",
        "cayley_R_orthogonal",
        "cayley_R_det_one",
        "RT_dR_skew_symmetric",
        "scalar_row_vanishes_identically",
        "connection_row_vanishes_identically",
        "pullback_consistency",
    ):
        assert graph[key] is True, key
    assert graph["map_depends_on_N"] is False
    degrees = graph["eliminated_metric_polynomial_degrees"]
    assert degrees == {"Y": 2, "d": 1, "a": 1, "gamma": 1}
    assert gate.graph_structure_certificate() == graph


def test_graph_numeric_witness(receipt: dict) -> None:
    witness = receipt["scientific"]["graph_numeric_witness"]
    assert witness["pass"] is True
    assert witness["worst_abs_row_residual"] < 1.0e-12
    assert witness["samples"] == gate.SAMPLES


def test_lipschitz_witness(receipt: dict) -> None:
    lip = receipt["scientific"]["lipschitz"]
    assert lip["pass"] is True
    assert lip["violations"] == 0
    assert 0.0 < lip["worst_norm_over_bound"] <= 1.0
    assert lip["bound_is_N_independent"] is True
    regenerated = gate.lipschitz_witness(gate.SAMPLES, gate.SAMPLE_SEED, gate.SAMPLE_RADIUS)
    assert regenerated["violations"] == 0
    assert np.isclose(regenerated["worst_norm_over_bound"], lip["worst_norm_over_bound"], rtol=1e-9)


def test_bound_formula_is_polynomial_in_M_only() -> None:
    values = [gate.lipschitz_bound_formula(M) for M in (0.0, 0.5, 1.0, 2.0)]
    assert all(np.isfinite(values)) and values == sorted(values)


def test_cayley_matches_numeric_rotation() -> None:
    k = np.array([0.3, -0.2, 0.1])
    R = gate._cayley_np(k)
    assert np.allclose(R.T @ R, np.eye(3), atol=1e-14)
    assert np.isclose(np.linalg.det(R), 1.0)


def test_theorem_and_boundaries(receipt: dict) -> None:
    theorem = receipt["scientific"]["theorem"]
    assert "N-independent" in theorem["statement"]
    assert "not machine-checked" in theorem["sobolev_lift"]
    assert "quadrature convergence" in theorem["not_claimed"]
    assert receipt["scientific"]["pointwise_formulation_needs_collocation_inverse"] is False
    assert len(receipt["scientific"]["kronecker_inverse_users_in_v5_6_4"]) == 5
    assert "C1_N1_beyond_the_bridge" in receipt["open_obligation"]
    boundary = receipt["independence_boundary"]
    assert boundary["imports_one_omega_modules"] is False
    assert boundary["imports_action_evaluators"] is False


def test_canonical_bytes_and_provenance(receipt: dict) -> None:
    assert gate.OUTPUT.read_text() == json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(Path(gate.__file__))
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
