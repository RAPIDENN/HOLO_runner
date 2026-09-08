"""Tests for stage v2.4b (scalar-sector jet momenta from the ADM first-order density, boundary action and currents)."""
from __future__ import annotations
import copy, json
import pytest
import sympy as sp
import derive_one_omega_charter_scalar_momentum_v2_4b_gate as gate


@pytest.fixture(scope="module")
def stored() -> dict:
    assert gate.OUTPUT.is_file(), "artifact absent: run the generator first"
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fresh() -> dict:
    return gate.derive()   # ~16 s


def test_charter_binds_and_tamper_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    payload, sha = gate._load_charter(); assert len(sha) == 64
    monkeypatch.setitem(gate.PINNED_STRINGS, "exact_action.GHY", "x")
    with pytest.raises(gate.ScalarMomentumError):
        gate._load_charter()


def test_fresh_matches_stored_digest(stored: dict, fresh: dict) -> None:
    assert fresh["calculation_digest"] == stored["calculation_digest"]


def test_all_checks_true_and_physical_false(stored: dict) -> None:
    assert [k for k, v in stored["checks"].items() if v is not True] == []
    for k in gate.PHYSICAL_FALSE_KEYS:
        assert stored["decision"][k] is False, k


def test_adm_identity_signs_were_determined_by_machine(stored: dict) -> None:
    adm = stored["boundary_action_terms"]["adm_identity"]
    assert adm["sigma"] in (1, -1) and adm["tau"] in (2, -2)
    assert (adm["sigma"], adm["tau"]) == (1, -2)


def test_ghy_cancels_total_derivative_and_no_delta_Xw(stored: dict) -> None:
    b = stored["boundary_action_terms"]
    assert sp.sympify(b["B_plus_GHY_at_brane"]) == 0
    assert all(sp.sympify(v) == 0 for v in b["delta_Xw_coefficients"].values())


def test_matches_codex_adm_oracle_exactly(stored: dict) -> None:
    o = stored["codex_adm_oracle"]["mine_minus_oracle"]
    for k, v in o.items():
        assert sp.sympify(v) == 0, k


def test_closure_after_constraint_and_E_current_not_identically_zero(stored: dict) -> None:
    c = stored["codex_closure"]
    assert sp.sympify(c["residual_after_constraint"]) == 0
    assert "Derivative(" in stored["currents"]["E"]      # J_E carries tangential jets off shell (vanishes with the constraint)


def test_jet_momentum_uses_derivative_not_linear_coefficient() -> None:
    f = sp.Function("f")(gate.x0, gate.x3, gate.w)
    L = 3 * sp.Derivative(f, gate.w)**2 + sp.Derivative(f, gate.w, gate.x0) * f
    p = gate.jet_momentum(L, f)
    assert sp.simplify(p - (6 * sp.Derivative(f, gate.w) - sp.Derivative(f, gate.x0))) == 0


def test_mutating_momentum_breaks_digest(stored: dict) -> None:
    mutant = copy.deepcopy(stored); mutant["momenta"]["C"] = "0"
    assert gate._canonical_digest({k: mutant[k] for k in gate.DIGEST_KEYS}) != stored["calculation_digest"]
