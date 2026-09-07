"""Tests for stage v2.3a (tensor quadratic action, boundary bookkeeping, DtN witness, assembly)."""
from __future__ import annotations
import copy, json
import pytest
import sympy as sp
import derive_one_omega_charter_dtn_assembly_v2_3_gate as gate


@pytest.fixture(scope="module")
def stored() -> dict:
    assert gate.OUTPUT.is_file(), "artifact absent: run the generator first"
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fresh() -> dict:
    return gate.derive()


def test_charter_binds_and_frozen_M4_matches() -> None:
    payload, sha = gate._load_charter()
    assert len(sha) == 64
    frozen = payload["action_charter"]["coefficient_policy"]["parameters"]
    assert abs(frozen["M4_bulk_squared_selected_one_Omega_wall_value"] - gate.FROZEN["M4_bulk_squared_selected_one_Omega_wall_value"]) < 1e-15
    assert abs(frozen["eta"] - 3.107013790800849) < 1e-15


def test_tampered_M4_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(gate.FROZEN, "M4_bulk_squared_selected_one_Omega_wall_value", 1.0)
    with pytest.raises(gate.DtnAssemblyError):
        gate._load_charter()


def test_fresh_matches_stored_digest(stored: dict, fresh: dict) -> None:
    assert fresh["calculation_digest"] == stored["calculation_digest"]


def test_all_checks_true_and_physical_keys_false(stored: dict) -> None:
    assert [k for k, v in stored["checks"].items() if v is not True] == []
    for k in gate.PHYSICAL_FALSE_KEYS:
        assert stored["decision"][k] is False, k
    assert stored["decision"]["scalar_sector_assembled_pass"] is False


def test_tt_normalization_and_masslessness(stored: dict) -> None:
    t = stored["tensor_quadratic_action"]
    assert sp.sympify(t["C_0"]) == 0
    M5c = sp.Symbol("M5c", positive=True); A = sp.Function("A")(sp.Symbol("w", real=True))
    loc = {"M5c": M5c, "A": sp.Function("A"), "w": sp.Symbol("w", real=True)}
    assert sp.simplify(sp.sympify(t["C_w"], locals=loc) + M5c * sp.exp(4 * A) / 4) == 0
    assert sp.simplify(sp.sympify(t["C_t"], locals=loc) - M5c * sp.exp(2 * A) / 4) == 0


def test_boundary_terms_cancel_and_neumann_is_M5(stored: dict) -> None:
    b = stored["boundary_bookkeeping"]
    assert sp.sympify(b["total"]) == 0
    assert sp.sympify(b["boundary_action_h0_hprime_coefficient"]) == 0
    assert str(sp.sympify(b["neumann_coupling_from_canonical_momentum_Z2"])) == "M5c"


def test_M4_and_eta_reproduced_to_1e_minus_9(stored: dict) -> None:
    n = stored["numerics"]; a = stored["assembly"]
    assert n["M4_relative_error"] < 1e-9
    assert a["eta_relative_error"] < 1e-9
    assert abs(a["induced_planck_mass_squared_witness"] - (gate.FROZEN["brane_Mb_squared"] + n["M4_squared_numeric"])) < 1e-9


def test_dtn_slope_and_monotonicity(stored: dict) -> None:
    n = stored["numerics"]
    assert n["slope_relative_error"] < 1e-3
    r = n["tensor_dtn_Hprime_over_H_at_0plus"]
    vals = [r[k] for k in sorted(r, key=float)]
    assert all(v < 0 for v in vals)
    assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))  # more negative with larger p^2


def test_mutating_numerics_breaks_digest(stored: dict) -> None:
    mutant = copy.deepcopy(stored)
    mutant["numerics"]["M4_squared_numeric"] = 1.0
    assert gate._canonical_digest({k: mutant[k] for k in gate.DIGEST_KEYS}) != stored["calculation_digest"]
