"""Tests for stage v2.1 (bulk background + junction) of the one-Omega charter variation."""
from __future__ import annotations
import copy, json
import pytest
import sympy as sp
import derive_one_omega_charter_bulk_junction_v2_gate as gate


@pytest.fixture(scope="module")
def stored() -> dict:
    assert gate.OUTPUT.is_file(), "artifact absent: run the generator first"
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fresh() -> dict:
    return gate.derive()  # a few seconds


def test_charter_binds_and_pinned_strings_verbatim() -> None:
    payload, sha = gate._load_charter()
    assert len(sha) == 64
    for dotted, expected in gate.PINNED_STRINGS.items():
        block, key = dotted.split(".")
        assert payload["action_charter"][block][key] == expected


def test_tampered_digest_or_string_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(gate.EXPECTED_CHARTER_DIGESTS, "calculation_digest", "0" * 64)
    with pytest.raises(gate.BulkJunctionError):
        gate._load_charter()
    monkeypatch.undo()
    monkeypatch.setitem(gate.PINNED_STRINGS, "exact_action.GHY", "S_GHY=0")
    with pytest.raises(gate.BulkJunctionError):
        gate._load_charter()


def test_fresh_matches_stored_digest(stored: dict, fresh: dict) -> None:
    assert fresh["calculation_digest"] == stored["calculation_digest"]


def test_all_checks_true_and_physical_keys_false(stored: dict) -> None:
    assert [k for k, v in stored["checks"].items() if v is not True] == []
    for k in gate.PHYSICAL_FALSE_KEYS:
        assert stored["decision"][k] is False, k
    assert stored["decision"]["embeddings_varied_pass"] is False


def test_bps_residuals_are_exactly_zero(stored: dict) -> None:
    for k, v in stored["bps"]["residuals_on_bps"].items():
        assert sp.sympify(v) == 0, k


def test_same_sign_bps_is_rejected() -> None:
    """The ww constraint is sign-blind; the mu-nu and Omega equations are not."""
    q = sp.Symbol("q", positive=True)
    Wq = gate.W_of(q); dWq = sp.diff(Wq, q)
    g, ginv, coords = gate.warped_metric()
    Ein, R = gate.einstein_tensor(g, ginv, coords)
    Om, A, w, s = gate.Om, gate.A, gate.w, gate.s
    dU = sp.diff(gate.U_of(q), q).subs(q, Om)
    box = sp.diff(Om, (w, 2)) + 4 * sp.diff(A, w) * sp.diff(Om, w)
    E_Om = gate.G * box - dU
    wrong = {sp.Derivative(Om, w): -s * dWq.subs(q, Om) / gate.G, sp.Derivative(A, w): -s * Wq.subs(q, Om) / (3 * gate.M5c)}
    e = E_Om.subs(sp.Derivative(Om, (w, 2)), sp.diff(wrong[sp.Derivative(Om, w)], w)).subs(wrong).subs(wrong)
    assert sp.simplify(e.subs(s**2, 1)) != 0


def test_junction_closes_v1_tadpoles(stored: dict) -> None:
    t = stored["tadpole_closure"]
    assert sp.simplify(sp.sympify(t["bps_flux_A"]) + sp.sympify(t["wall_piece_A"])) == 0
    assert sp.simplify(sp.sympify(t["bps_flux_Omega"]) + sp.sympify(t["wall_piece_Omega"])) == 0
    assert sp.simplify(sp.sympify(t["wall_piece_Omega"]) - sp.sympify(t["v1_omega_tadpole_minus_2Wprime1"])) == 0


def test_metric_junction_residual_is_compensator_spring(stored: dict) -> None:
    j = stored["junctions"]
    assert sp.sympify(j["metric_on_bps_at_Omega_Sigma_1"]) == 0
    assert sp.sympify(j["omega_on_bps_at_Omega_Sigma_1"]) == 0
    expr = sp.sympify(j["metric_on_bps"])
    by_name = {str(x): x for x in expr.free_symbols}
    O0, A0, beta = by_name["Omega0"], by_name["A0"], by_name["beta_b"]
    assert sp.simplify(expr + 2 * beta * (O0 - 1)**2 * sp.exp(4 * A0)) == 0


def test_oracle_contrast_is_constant_ratio(stored: dict) -> None:
    c = stored["contrasts"]["oracle_scalar_junction_phi0"]
    assert c["proportional_with_constant_ratio"] is True
    assert sp.sympify(c["ratio_mine_over_oracle"]) in (1, -1)


def test_mutating_a_junction_breaks_the_digest(stored: dict) -> None:
    mutant = copy.deepcopy(stored)
    mutant["junctions"]["omega_Z2"] = "0"
    d = gate._canonical_digest({k: mutant[k] for k in gate.DIGEST_KEYS})
    assert d != stored["calculation_digest"]
