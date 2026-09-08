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


def test_jump_vs_outward_sign_two_independent_derivatives() -> None:
    """[H'] = H'(0+) - H'(0-) equals MINUS the sum of outward normal derivatives (n_+ = -d_w, n_- = +d_w)."""
    hp, hm = sp.symbols("hprime_plus hprime_minus", real=True)
    jump = hp - hm
    outward_sum = (-1) * hp + (+1) * hm
    assert sp.simplify(jump + outward_sum) == 0
    # brane-equation bulk term from the canonical momentum with the (-s) boundary sign: -p_+ + p_-, p = 2 C_w h', C_w(0) = -M5^3/4
    M5c = sp.Symbol("M5c", positive=True)
    term = -(2 * (-M5c / 4) * hp) + (2 * (-M5c / 4) * hm)
    assert sp.simplify(term - M5c * jump / 2) == 0


def test_assembled_grid_uses_single_Z2_factor(stored: dict) -> None:
    a = stored["assembly"]; n = stored["numerics"]
    assert a["grid_vs_planck_relative_error"] < 1e-3
    assert "2 * C_N" not in a["tensor_operator_per_amplitude"]
    assert n["M4_relative_error"] < 1e-9 and a["M4_closed_form_relative_error"] < 1e-9


def test_mutating_numerics_breaks_digest(stored: dict) -> None:
    mutant = copy.deepcopy(stored)
    mutant["numerics"]["M4_squared_numeric"] = 1.0
    assert gate._canonical_digest({k: mutant[k] for k in gate.DIGEST_KEYS}) != stored["calculation_digest"]
