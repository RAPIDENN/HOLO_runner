"""Tests for the v5.6.6.14 proven symbolic Jacobian bound gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

import derive_one_omega_topological_so3_retraction_jacobian_bound_proved_symbolic_v5_6_6_14 as gate


EXPECTED_TRUE_KEYS = frozenset({"pointwise_retraction_jacobian_bound_proved_symbolic_pass"})
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


def test_generator_imports() -> None:
    source = Path(gate.__file__).read_text()
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    assert not any("one_omega_topological_so3" in name for name in names)
    assert not any(name in {"torch", "scipy", "runpy"} for name in names)
    assert source.count("spec_from_file_location") == 1
    for forbidden in ("independent_euler_green_route_c", "precision_stabilized_route_c", "ad_fd5_route_c", "three_way"):
        assert forbidden not in source, forbidden


def test_schema_and_pins(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["v5_6_6_9_derive_sha256"] == gate.V5669_DERIVE_SHA256 == gate._sha256(gate.V5669_DERIVE_PATH)
    assert pins["v5_6_6_9_receipt_sha256"] == gate.V5669_RECEIPT_SHA256 == gate._sha256(gate.V5669_RECEIPT_PATH)
    assert receipt["independence_boundary"]["imports_action_evaluators"] is False
    assert len(gate.FROZEN_COMMIT) == 40


def test_decision_allowlist(receipt: dict) -> None:
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key


def test_symbolic_phi_matches_numeric_phi_of_v5669() -> None:
    outputs, inputs, _groups, _den = gate.symbolic_phi()
    v5669 = gate.load_v5669()
    rng = np.random.default_rng(3)
    for _ in range(3):
        u = rng.uniform(-1.0, 1.0, size=v5669.U_SIZE)
        numeric = v5669._phi_numeric(u)
        symbolic = np.array([float(o.subs(dict(zip(inputs, u)))) for o in outputs])
        assert np.allclose(numeric, symbolic, atol=1e-12)


def test_coefficient_sum_bound_is_an_upper_bound() -> None:
    x, y = sp.symbols("x y")
    M = sp.Symbol("M", positive=True)
    expr = 3 * x**2 * y - 2 * x + 5
    bound = gate.coefficient_sum_bound(expr, [x, y], M)
    assert bound == 3 * M**3 + 2 * M + 5
    rng = np.random.default_rng(4)
    for _ in range(200):
        Mv = rng.uniform(0.0, 3.0)
        xv, yv = rng.uniform(-Mv, Mv, size=2)
        assert abs(3 * xv**2 * yv - 2 * xv + 5) <= float(bound.subs(M, Mv)) + 1e-12


def test_entry_bound_rejects_foreign_denominators() -> None:
    _outputs, inputs, groups, den = gate.symbolic_phi()
    M = sp.Symbol("M", positive=True)
    k = groups["k"]
    with pytest.raises(gate.ProvedBoundGateError):
        gate.entry_bound(1 / (1 + k[0]), inputs, k, den, M)
    bound, power, const = gate.entry_bound(k[0] / (2 * den**2), inputs, k, den, M)
    assert power == 2 and const == 2.0 and float(sp.simplify(bound - M / 2)) == 0.0


def test_proved_bound_structure(receipt: dict) -> None:
    b = receipt["scientific"]["proved_bound"]
    assert b["inputs"] == 53 and b["outputs"] == 34
    assert b["nonzero_jacobian_entries"] > 200
    assert b["max_denominator_power_of_1_plus_k2"] >= 1
    poly = {int(k): v for k, v in b["B_proved_squared_polynomial_in_M"].items()}
    assert all(v >= 0 for v in poly.values())
    assert max(poly) == 2 * b["B_proved_degree_in_M"]
    assert poly[0] >= 15.0  # the 15 unit entries of the g block plus the identities
    assert set(b["block_squared_polynomials"]) == {"g", "phi", "A_mu", "A_4", "log_Omega"}
    regenerated = gate.proved_bound()
    assert {int(k): v for k, v in regenerated["B_proved_squared_polynomial_in_M"].items()} == poly


def test_consistency_witness(receipt: dict) -> None:
    w = receipt["scientific"]["consistency_witness"]
    assert w["pass"] is True and w["violations"] == 0
    assert 0.0 < w["worst_sampled_norm_over_B_proved"] < 1.0
    rows = {row["M"]: row for row in w["B_proved_vs_v5669_formula"]}
    for M, row in rows.items():
        assert row["B_proved"] > 0 and row["B_sampled_formula_v5669"] > 0
    assert rows[1.0]["B_proved"] >= rows[0.5]["B_proved"] >= rows[0.001]["B_proved"]


def test_sobolev_lift_is_labelled(receipt: dict) -> None:
    lift = receipt["scientific"]["sobolev_lift"]
    assert lift["machine_checked"] is False
    assert "H^{s+1}" in lift["statement"]
    assert len(lift["hypotheses"]) == 3
    assert "gap_5" in receipt["open_obligation"]


def test_canonical_bytes_and_provenance(receipt: dict) -> None:
    assert gate.OUTPUT.read_text() == json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(Path(gate.__file__))
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
