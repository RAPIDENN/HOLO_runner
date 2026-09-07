"""Independent projections and mutation controls for displayed TT-row closure.

These tests audit both TT polarizations against the actual source equations.
They do not certify moving embeddings, all candidate equations or full N7.
"""
from __future__ import annotations

import copy
import json

import pytest
import sympy as sp

from . import verify_one_omega_topological_tt_closure_v1 as oracle


BULK_ROW_NAMES = {
    "00", "01", "02", "03", "04", "11", "12", "13", "14",
    "22", "23", "24", "33", "34", "44", "Omega", "chi0",
}


@pytest.fixture(scope="module")
def bulk_source():
    return json.loads(oracle.BULK.read_text())


@pytest.fixture(scope="module")
def brane_source():
    return json.loads(oracle.BRANE.read_text())


@pytest.fixture(scope="module")
def bulk_projection(bulk_source):
    return oracle.check_bulk_rows(bulk_source)


@pytest.fixture(scope="module")
def brane_projection(brane_source):
    return oracle.check_brane_columns(brane_source)


@pytest.fixture(scope="module")
def receipt():
    return oracle.build_payload()


def zero(expression):
    return sp.simplify(expression) == 0


def resign(document):
    document["calculation_digest"] = oracle.canonical_digest(
        {key: value for key, value in document.items() if key != "calculation_digest"}
    )
    return document


def test_parser_exact_derivatives_and_background_functions():
    w = oracle.SYMBOLS["w"]
    h = sp.Function("H12")(w)
    expected = sp.diff(h, w, 2) + sp.exp(2 * sp.Function("A")(w)) * h / 3
    parsed = oracle.parse_expression(
        "Derivative(H12(w), (w, 2)) + exp(2*A(w))*H12(w)/3"
    )
    assert zero(parsed - expected)
    assert oracle.parse_expression("sqrt(4) + I*I") == 1
    assert oracle.parse_expression("Omega(w)") == sp.Function("Omega")(w)


def test_parser_distinguishes_radial_coordinate_and_brane_frequency():
    assert oracle.parse_expression("w") == oracle.SYMBOLS["w"]
    assert oracle.parse_expression("w", brane=True) == oracle.SYMBOLS["W_freq"]
    assert oracle.parse_expression("q", brane=True) == oracle.SYMBOLS["q_mom"]
    assert oracle.SYMBOLS["w"] != oracle.SYMBOLS["W_freq"]


@pytest.mark.parametrize("text", [
    "unknown(H12(w))", "H12(w).diff(w)", "0.5*H12(w)", "(w, 2)",
    "exp((w, 2))", "Derivative(H12(w), (w, 3))",
    "Derivative(H12(w)**2, w)", "H12(q_mom)",
])
def test_parser_rejects_constructs_outside_declared_expression_language(text):
    with pytest.raises(oracle.TTClosureError):
        oracle.parse_expression(text)


def test_real_bulk_source_checks_all_seventeen_rows_for_both_polarizations(bulk_projection):
    results = bulk_projection["polarization_results"]
    assert set(results) == {"cross", "plus"}
    for case in results.values():
        for key in ("restricted_rows", "expected_rows", "residuals", "null_residuals"):
            assert set(case[key]) == BULK_ROW_NAMES
        assert all(zero(value) for value in case["residuals"].values())
        assert all(zero(value) for value in case["null_residuals"].values())


def test_bulk_normalization_matches_direct_warped_tensor_equation(bulk_projection):
    s = oracle.SYMBOLS
    M, A, G, k, o = (s[name] for name in ("M5c", "A_value", "G", "k_inf", "Omega_value"))
    # E_12 = -M5^3 e^(2A)/2 times the covariant TT wave operator.
    # A' = -s*k*exp(-G*Omega^2/(6*M5^3)) fixes the radial transport sign.
    Ap = -s["s"] * k * sp.exp(-G * o**2 / (6 * M))
    wave_operator = s["hrr"] + 4 * Ap * s["hr"] + sp.exp(-2 * A) * (
        s["W_freq"]**2 - s["q_mom"]**2
    ) * s["h"]
    expected = -M * sp.exp(2 * A) * wave_operator / 2
    cross = bulk_projection["polarization_results"]["cross"]["restricted_rows"]
    assert zero(cross["12"] - expected)
    assert zero(sp.diff(cross["12"], s["hrr"]) + M * sp.exp(2 * A) / 2)
    assert zero(sp.diff(cross["12"], s["h"], s["W_freq"], 2) + M)
    assert not zero(cross["12"])


def test_plus_polarization_is_a_rotation_of_cross_not_a_scalar_trace(bulk_projection):
    h = oracle.SYMBOLS["h"]
    shear = sp.Matrix([[0, h, 0], [h, 0, 0], [0, 0, 0]])
    r = sp.sqrt(2) / 2
    rotation = sp.Matrix([[r, r, 0], [-r, r, 0], [0, 0, 1]])
    plus = rotation * shear * rotation.T
    assert rotation.det() == 1
    assert plus == sp.diag(h, -h, 0)
    assert sp.trace(plus) == 0
    assert sp.trace(plus * plus) == sp.trace(shear * shear) == 2 * h**2
    results = bulk_projection["polarization_results"]
    expected = results["cross"]["restricted_rows"]["12"]
    assert zero(results["plus"]["restricted_rows"]["11"] - expected)
    assert zero(results["plus"]["restricted_rows"]["22"] + expected)
    assert all(zero(value) for key, value in results["plus"]["restricted_rows"].items()
               if key not in {"11", "22"})


def test_bulk_detects_tt_source_in_scalar_constraint_even_with_success_flags(bulk_source):
    mutant = copy.deepcopy(bulk_source)
    mutant["helicity_odes"]["00"] += " + H12(w)"
    mutant["checks"] = {key: True for key in mutant["checks"]}
    mutant["helicity_odes"]["tensor_ratio_to_standard_form"] = "0"
    result = oracle.check_bulk_rows(mutant)
    cross = result["polarization_results"]["cross"]
    assert zero(cross["residuals"]["00"] - oracle.SYMBOLS["h"])
    assert zero(cross["null_residuals"]["00"] - oracle.SYMBOLS["h"])
    assert not result["checks"]["all_projected_bulk_rows_match_independent_TT_operator"]
    assert not result["checks"]["both_null_modes_satisfy_all_seventeen_bulk_rows"]


@pytest.mark.parametrize("factor", [-1, 2])
def test_wrong_bulk_sign_or_normalization_is_not_hidden_by_null_solution(bulk_source, factor):
    mutant = copy.deepcopy(bulk_source)
    mutant["helicity_odes"]["12"] = f"{factor}*({mutant['helicity_odes']['12']})"
    result = oracle.check_bulk_rows(mutant)
    cross = result["polarization_results"]["cross"]
    assert not zero(cross["residuals"]["12"])
    # A homogeneous equation with a wrong nonzero prefactor retains its kernel.
    assert all(zero(value) for value in cross["null_residuals"].values())
    assert not result["checks"]["all_projected_bulk_rows_match_independent_TT_operator"]


def test_plus_only_contamination_cannot_pass_cross_only_projection(bulk_source):
    mutant = copy.deepcopy(bulk_source)
    mutant["helicity_odes"]["11"] += " + H11(w)"
    result = oracle.check_bulk_rows(mutant)["polarization_results"]
    assert all(zero(value) for value in result["cross"]["residuals"].values())
    assert zero(result["plus"]["residuals"]["11"] - oracle.SYMBOLS["h"])
    assert not zero(result["plus"]["null_residuals"]["11"])


def test_real_brane_columns_include_contact_and_both_polarizations(brane_projection, brane_source):
    s = oracle.SYMBOLS
    M, G, k, Mb, mu, v = (s[name] for name in ("M5c", "G", "k_inf", "Mb2", "mu_X", "v"))
    W0 = 3 * M * k * sp.exp(-G / (6 * M))
    kinetic = Mb * (s["W_freq"]**2 - s["xi"] * s["q_mom"]**2) / 2
    columns = brane_projection["column_results"]
    assert set(columns) == {"Hd", "H12"}
    for case in columns.values():
        assert set(case["residuals"]) == set(brane_source["extended_hessian"]["helicity_field_order"])
        assert len(case["residuals"]) == 18
        assert all(zero(value) for value in case["residuals"].values())
        assert zero(case["diagonal"] - (2 * W0 + kinetic - mu * v**4))
        candidate = case["candidate_after_removing_solid_and_balancing_bulk_tension"]
        assert zero(candidate - kinetic)
        assert zero(candidate.subs({s["W_freq"]: s["q_mom"], s["xi"]: 1}))
        assert not zero(candidate.subs({s["W_freq"]: s["q_mom"], s["xi"]: 2}))


@pytest.mark.parametrize("column", ["Hd", "H12"])
def test_mixed_lapse_row_in_either_tt_column_is_detected(brane_source, column):
    mutant = copy.deepcopy(brane_source)
    block = mutant["extended_hessian"]
    names = block["helicity_field_order"]
    block["symbolic_matrix_helicity_basis"][names.index("n")][names.index(column)] = "1"
    mutant["checks"] = {key: True for key in mutant["checks"]}
    result = oracle.check_brane_columns(mutant)
    assert result["column_results"][column]["residuals"]["n"] == 1
    assert result["column_results"][column]["residuals"][column] == 0
    assert not result["checks"]["both_complete_brane_columns_match_TT_reference"]


def test_missing_elastic_contact_is_not_silently_inherited_as_candidate(brane_source):
    mutant = copy.deepcopy(brane_source)
    block = mutant["extended_hessian"]
    i = block["helicity_field_order"].index("Hd")
    block["symbolic_matrix_helicity_basis"][i][i] += " + mu_X*v**4"
    result = oracle.check_brane_columns(mutant)
    expected = oracle.SYMBOLS["mu_X"] * oracle.SYMBOLS["v"]**4
    assert zero(result["column_results"]["Hd"]["residuals"]["Hd"] - expected)
    assert not result["checks"]["both_complete_brane_columns_match_TT_reference"]


def test_receipt_validates_against_fresh_projections_with_limited_scope(receipt):
    oracle.validate_payload(receipt)
    assert receipt["decision"]["both_polarizations_checked_in_displayed_bulk_and_brane_rows"] is True
    for key in ("independent_derivation_of_every_bulk_row", "moving_embedding_equations_rederived",
                "complete_candidate_linearization_certified", "physical_mode_admissibility",
                "BF_edge_modes_eliminated", "full_N7", "full_P4", "B4", "B5"):
        assert receipt["decision"][key] is False
    assert receipt["transport"]["historical_source_flags_inherited"] is False


def test_resigned_receipt_cannot_change_a_projected_constraint(receipt):
    mutant = copy.deepcopy(receipt)
    mutant["bulk"]["polarization_results"]["cross"]["restricted_rows"]["00"] = "h"
    resign(mutant)
    with pytest.raises(oracle.TTClosureError, match="fresh TT projections"):
        oracle.validate_payload(mutant)


def test_unresigned_receipt_cannot_promote_physical_admissibility(receipt):
    mutant = copy.deepcopy(receipt)
    mutant["decision"]["physical_mode_admissibility"] = True
    with pytest.raises(oracle.TTClosureError, match="digest mismatch"):
        oracle.validate_payload(mutant)
