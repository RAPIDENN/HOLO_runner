"""Tests for stage v2.4 (scalar-sector canonical momenta and brane currents from the literal action)."""
from __future__ import annotations
import copy, json
import pytest
import sympy as sp
import derive_one_omega_charter_scalar_momentum_v2_4_gate as gate


@pytest.fixture(scope="module")
def stored() -> dict:
    assert gate.OUTPUT.is_file(), "artifact absent: run the generator first"
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fresh() -> dict:
    return gate.derive()   # about ten seconds


def test_charter_binds_and_strings_verbatim() -> None:
    payload, sha = gate._load_charter(); assert len(sha) == 64


def test_tampered_string_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(gate.PINNED_STRINGS, "exact_action.wall_background", "x")
    with pytest.raises(gate.ScalarMomentumError):
        gate._load_charter()


def test_fresh_matches_stored_digest(stored: dict, fresh: dict) -> None:
    assert fresh["calculation_digest"] == stored["calculation_digest"]


def test_all_checks_true_and_physical_false(stored: dict) -> None:
    assert [k for k, v in stored["checks"].items() if v is not True] == []
    for k in gate.PHYSICAL_FALSE_KEYS:
        assert stored["decision"][k] is False, k


def test_codex_closure_after_constraint_and_raw_difference(stored: dict) -> None:
    c = stored["codex_closure"]
    assert sp.sympify(c["residual_after_constraint"]) == 0
    raw = sp.sympify(c["residual_raw"], locals={"C0": sp.Symbol("C0", real=True), "P_w": sp.Symbol("P_w", real=True)})
    assert raw != 0 and raw.has(sp.Symbol("P_w", real=True))


def test_E_has_no_current_and_P_momentum_is_ADM_like(stored: dict) -> None:
    assert sp.sympify(stored["currents"]["E"]) == 0
    assert "12*Derivative(P" in stored["momenta"]["P"]


def test_mutating_current_breaks_digest(stored: dict) -> None:
    mutant = copy.deepcopy(stored); mutant["currents"]["C"] = "0"
    assert gate._canonical_digest({k: mutant[k] for k in gate.DIGEST_KEYS}) != stored["calculation_digest"]
