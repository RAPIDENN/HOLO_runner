"""Tests for stage v2.2 (linear bulk perturbations, bending, jump operators) of the one-Omega charter variation."""
from __future__ import annotations
import copy, json
import pytest
import sympy as sp
import derive_one_omega_charter_linear_junction_v2_2_gate as gate


@pytest.fixture(scope="module")
def stored() -> dict:
    assert gate.OUTPUT.is_file(), "artifact absent: run the generator first"
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fresh() -> dict:
    return gate.derive()  # about ten seconds


def test_charter_binds_and_pinned_strings_verbatim() -> None:
    payload, sha = gate._load_charter()
    assert len(sha) == 64
    for dotted, expected in gate.PINNED_STRINGS.items():
        block, key = dotted.split(".")
        assert payload["action_charter"][block][key] == expected


def test_tampered_string_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(gate.PINNED_STRINGS, "definitions.covariant_delta_wall_equivalence", "x")
    with pytest.raises(gate.LinearJunctionError):
        gate._load_charter()


def test_fresh_matches_stored_digest(stored: dict, fresh: dict) -> None:
    assert fresh["calculation_digest"] == stored["calculation_digest"]


def test_all_checks_true_and_physical_keys_false(stored: dict) -> None:
    assert [k for k, v in stored["checks"].items() if v is not True] == []
    for k in gate.PHYSICAL_FALSE_KEYS:
        assert stored["decision"][k] is False, k
    assert stored["decision"]["dirichlet_to_neumann_map_computed_pass"] is False


def test_background_residuals_all_zero(stored: dict) -> None:
    for k, v in stored["linear_equations"]["background_residuals"].items():
        assert sp.sympify(v) == 0, k


def test_tensor_ode_is_standard_warped_form(stored: dict) -> None:
    ode = sp.sympify(stored["helicity_odes"]["12"])
    ratio = sp.sympify(stored["helicity_odes"]["tensor_ratio_to_standard_form"])
    w = [x for x in ode.free_symbols if str(x) == "w"][0]
    H12 = [f for f in ode.atoms(sp.core.function.AppliedUndef) if f.func.__name__ == "H12"][0]
    A = [f for f in ode.atoms(sp.core.function.AppliedUndef) if f.func.__name__ == "A"][0]
    Om = [f for f in ode.atoms(sp.core.function.AppliedUndef) if f.func.__name__ == "Omega"][0]
    by = {str(x): x for x in ode.free_symbols}
    q, W, M5c, k, G, s = by["q_mom"], by["W_freq"], by["M5c"], by["k_inf"], by["G"], by["s"]
    Ap = -s * 3 * M5c * k * sp.exp(-G * Om**2 / (6 * M5c)) / (3 * M5c)
    target = sp.diff(H12, (w, 2)) + 4 * Ap * sp.diff(H12, w) - sp.exp(-2 * A) * (q**2 - W**2) * H12
    assert sp.simplify(ode - ratio * target) == 0
    assert not ratio.has(H12) and not ratio.has(q) and not ratio.has(W)


def test_constraints_are_first_order_in_w(stored: dict) -> None:
    for k, v in stored["helicity_odes"]["constraint_w_orders"].items():
        assert v <= 1, k
    for k, v in stored["helicity_odes"]["dynamical_w_orders"].items():
        assert v == 2, k


def test_bending_preserves_gauge_and_has_dd_zeta(stored: dict) -> None:
    b = stored["bending"]
    ddh = [[sp.sympify(e) for e in row] for row in b["d_w_delta_h_at_brane"]]
    zeta = [f for f in ddh[1][2].atoms(sp.core.function.AppliedUndef) if f.func.__name__ == "zeta_b"]
    assert zeta, "off-diagonal bending entry must contain zeta"
    z = zeta[0]
    x1, x2 = [x for x in z.args if str(x) == "x1"][0], [x for x in z.args if str(x) == "x2"][0]
    assert sp.simplify(ddh[1][2] + 2 * sp.diff(z, x1, x2)) == 0


def test_jump_operators_structure(stored: dict) -> None:
    j = stored["jump_conditions"]
    assert set(j["second_derivative_coefficients_mu_nu"]["12"]) == {"12"}
    assert set(j["second_derivative_coefficients_Omega"]) == {"Wm"}
    row11 = j["second_derivative_coefficients_mu_nu"]["11"]
    assert "11" not in row11 and {"00", "22", "33"} <= set(row11)


def test_mutating_an_ode_breaks_the_digest(stored: dict) -> None:
    mutant = copy.deepcopy(stored)
    mutant["helicity_odes"]["12"] = "0"
    assert gate._canonical_digest({k: mutant[k] for k in gate.DIGEST_KEYS}) != stored["calculation_digest"]
