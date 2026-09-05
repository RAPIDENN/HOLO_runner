#!/usr/bin/env python3
"""Tests for the exact named-member margin certificate v5.6.7.5."""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import math
import struct
import types
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE
    / "derive_one_omega_topological_so3_direct_free_finite_member_exact_margin_v5_6_7_5_gate.py"
)
SPEC = importlib.util.spec_from_file_location("v5675_exact_margin", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def _walk_has_float(value) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_walk_has_float(key) or _walk_has_float(item) for key, item in value.items())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_walk_has_float(item) for item in value)
    return False


def _load_v5671_for_non_authoritative_canary():
    assert hashlib.sha256(gate.V5671_SOURCE.read_bytes()).hexdigest() == gate.V5671_SOURCE_SHA256
    specification = importlib.util.spec_from_file_location("v5671_canary_for_v5675", gate.V5671_SOURCE)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _symmetric5_from_packed(values: np.ndarray) -> np.ndarray:
    result = np.zeros((5, 5), dtype=float)
    cursor = 0
    for i in range(5):
        for j in range(i, 5):
            result[i, j] = result[j, i] = values[cursor]
            cursor += 1
    return result


def _assignment_expression(path: Path, name: str) -> ast.expr:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return node.value
    raise AssertionError(f"missing assignment {name!r} in {path.name}")


def _binary64_fraction_from_source_float(value: float) -> Fraction:
    """Recover the exact normal binary64 rational through its packed word."""

    word = struct.unpack("<Q", struct.pack("<d", value))[0]
    sign = -1 if word >> 63 else 1
    exponent_bits = (word >> 52) & 0x7FF
    fraction_bits = word & ((1 << 52) - 1)
    if exponent_bits == 0 and fraction_bits == 0:
        return Fraction(0)
    assert 0 < exponent_bits < 0x7FF
    significand = (1 << 52) | fraction_bits
    exponent = exponent_bits - 1023 - 52
    if exponent >= 0:
        return Fraction(sign * significand * (1 << exponent))
    return Fraction(sign * significand, 1 << (-exponent))


def _fraction_from_json(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _load_gate_with_assignment_mutant(target_name: str, replacement: str):
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"), filename=str(MODULE_PATH))
    matches = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == target_name
            for target in node.targets
        )
    ]
    assert len(matches) == 1
    matches[0].value = ast.parse(replacement, mode="eval").body
    ast.fix_missing_locations(tree)
    module = types.ModuleType(f"v5675_mutant_{target_name}")
    module.__file__ = str(MODULE_PATH)
    exec(compile(tree, str(MODULE_PATH), "exec"), module.__dict__)
    return module


def _load_gate_with_empty_function_return_mutant(function_name: str):
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"), filename=str(MODULE_PATH))
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    ]
    assert len(functions) == 1
    returns = [node for node in ast.walk(functions[0]) if isinstance(node, ast.Return)]
    assert len(returns) == 1
    returns[0].value = ast.Dict(keys=[], values=[])
    ast.fix_missing_locations(tree)
    module = types.ModuleType(f"v5675_mutant_{function_name}")
    module.__file__ = str(MODULE_PATH)
    exec(compile(tree, str(MODULE_PATH), "exec"), module.__dict__)
    return module


def _local_polynomial_matrix_sha256(matrix) -> str:
    def polynomial_payload(polynomial):
        return [
            {
                "powers_t_y": [exponent[0], exponent[1]],
                "coefficient": {
                    "numerator": coefficient.numerator,
                    "denominator": coefficient.denominator,
                    "exact": f"{coefficient.numerator}/{coefficient.denominator}",
                },
            }
            for exponent, coefficient in sorted(polynomial.items())
        ]

    payload = [[polynomial_payload(entry) for entry in row] for row in matrix]
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _local_literal_pulled_matrices(sign: int):
    literal = ast.literal_eval(
        _assignment_expression(gate.V5671_SOURCE, "REFERENCE_METRIC_DIAGONAL")
    )
    reference = tuple(_binary64_fraction_from_source_float(value) for value in literal)
    gamma = (Fraction(-5, 4), Fraction(9, 8), Fraction(5, 4), Fraction(11, 8))
    normal = Fraction(9, 8)
    actual = [[{} for _ in range(5)] for _ in range(5)]
    pulled_reference = [[{} for _ in range(5)] for _ in range(5)]
    for index in (0, 1, 3):
        actual[index][index] = {
            (0, 0): reference[index],
            (1, 0): gamma[index] - reference[index],
        }
        pulled_reference[index][index] = {(0, 0): reference[index]}
    actual[2][2] = {
        (0, 0): reference[2],
        (1, 0): gamma[2] - reference[2],
        (0, 2): reference[4],
        (1, 2): -reference[4],
    }
    actual[2][4] = actual[4][2] = {
        (0, 1): sign * reference[4],
        (1, 1): -sign * reference[4],
    }
    actual[4][4] = {
        (0, 0): reference[4],
        (1, 0): normal - reference[4],
    }
    pulled_reference[2][2] = {
        (0, 0): reference[2],
        (0, 2): reference[4],
    }
    pulled_reference[2][4] = pulled_reference[4][2] = {
        (0, 1): sign * reference[4]
    }
    pulled_reference[4][4] = {(0, 0): reference[4]}
    return actual, pulled_reference


def test_upstream_sources_tests_and_bd61d22_commit_blobs_are_independently_pinned() -> None:
    pins = gate._source_pin_ledger()
    assert pins["v5_6_7_pass"] is True
    assert pins["v5_6_7_1_pass"] is True
    assert pins["bd61d22_pass"] is True
    assert pins["bd61d22_commit_binding"] == {
        "commit": "bd61d22cbb989035a4f4b51ea706b54bd154a5ae",
        "source_blob_sha256": gate.V5673_SOURCE_SHA256,
        "test_blob_sha256": gate.V5673_TEST_SHA256,
        "matches_pinned_worktree_bytes": True,
        "conclusion_imported_or_consumed": False,
    }
    assert all(row["pass"] for row in pins["records"].values())
    assert all(
        all(row["required_fragment_matches"].values())
        for row in pins["records"].values()
    )


def test_reference_metric_ratios_are_derived_from_the_pinned_v5671_ast_and_binary64_words() -> None:
    assert hashlib.sha256(gate.V5671_SOURCE.read_bytes()).hexdigest() == gate.V5671_SOURCE_SHA256
    literal = ast.literal_eval(
        _assignment_expression(gate.V5671_SOURCE, "REFERENCE_METRIC_DIAGONAL")
    )
    assert isinstance(literal, tuple) and len(literal) == 5
    source_ratios = tuple(_binary64_fraction_from_source_float(value) for value in literal)
    assert source_ratios == gate.REFERENCE_METRIC_DIAGONAL
    assert tuple(gate._dyadic_binary64_bits(value) for value in source_ratios) == tuple(
        struct.unpack("<Q", struct.pack("<d", value))[0] for value in literal
    )


def test_gamma_packed_indices_are_exactly_the_diagonal_of_pinned_v5671_symmetric4() -> None:
    assert hashlib.sha256(gate.V5671_SOURCE.read_bytes()).hexdigest() == gate.V5671_SOURCE_SHA256
    expression = _assignment_expression(gate.V5671_SOURCE, "SYMMETRIC4")
    symmetric4 = eval(
        compile(ast.Expression(expression), str(gate.V5671_SOURCE), "eval"),
        {"__builtins__": {"tuple": tuple, "range": range}},
    )
    diagonal_offsets = tuple(
        index for index, (left, right) in enumerate(symmetric4) if left == right
    )
    assert diagonal_offsets == (0, 4, 7, 9)

    assignments, layout = gate.member_sparse_assignments(gate.canonical_member_contract())
    gamma = layout["blocks"]["common.gamma"]
    active_offsets = tuple(
        index - gamma["start"]
        for index in sorted(assignments)
        if gamma["start"] <= index < gamma["stop"]
    )
    assert active_offsets == diagonal_offsets


def test_exact_radial_proof_coefficients_match_pinned_v567_profiles_coefficientwise() -> None:
    assert hashlib.sha256(gate.V567_SOURCE.read_bytes()).hexdigest() == gate.V567_SOURCE_SHA256
    upstream = gate._load_pinned_v567()
    profiles = upstream.radial_profile_polynomials(1)
    upstream_h0 = tuple(
        _binary64_fraction_from_source_float(value) for value in profiles["h0"].coef
    )
    upstream_b0 = tuple(
        _binary64_fraction_from_source_float(value) for value in profiles["bumps"][0].coef
    )
    radial = gate._radial_envelope_ledger()
    proof_h0 = tuple(_fraction_from_json(value) for value in radial["h0_coefficients_ascending"])
    proof_b0 = tuple(_fraction_from_json(value) for value in radial["b0_coefficients_ascending"])
    assert proof_h0 == upstream_h0
    assert proof_b0 == upstream_b0


def test_independent_layout_matches_first_complete_nonconstant_shell() -> None:
    ledger = gate._member_ledger()
    assert ledger["pass"] is True
    assert ledger["complete_shell_L1"] is True
    assert ledger["independent_layout_matches_pinned_v5_6_7"] is True
    assert ledger["x2_modes_match_pinned_enumeration"] is True
    assert ledger["free_coordinate_dimension"] == 29970
    upstream = gate._load_pinned_v567()
    modes = upstream.real_fourier_modes(81)
    assert modes[7] == {
        "kind": "cos",
        "wavevector": (0, 0, 1, 0),
        "label": "cos(1*x2)",
    }
    assert modes[8] == {
        "kind": "sin",
        "wavevector": (0, 0, 1, 0),
        "label": "sin(1*x2)",
    }


def test_member_bytes_have_exact_dimension_nonzeros_positions_and_hash() -> None:
    raw = gate.member_f64le_bytes()
    assert len(raw) == 29970 * 8
    assert hashlib.sha256(raw).hexdigest() == (
        "d9867b9651b9ca6dec961fe2356f2d2ef5d0b184ad947ef28601a3e988dc246a"
    )
    words = struct.unpack(f"<{29970}Q", raw)
    nonzero = {index: word for index, word in enumerate(words) if word}
    assignments, _layout = gate.member_sparse_assignments(gate.canonical_member_contract())
    assert set(nonzero) == {
        0,
        4,
        7,
        9,
        972,
        973,
        974,
        2438,
        2515,
        11479,
        16208,
        16285,
        25249,
    }
    assert len(assignments) == len(nonzero) == 13
    assert all(nonzero[index] == gate._dyadic_binary64_bits(value) for index, value in assignments.items())
    assert assignments[2438] == assignments[16208] == Fraction(1, 256)
    assert assignments[11479] == assignments[25249] == Fraction(1, 64)


def test_exact_binary64_encoder_rejects_non_dyadic_or_non_normal_values() -> None:
    assert gate._dyadic_binary64_bits(Fraction(1)) == 0x3FF0000000000000
    assert gate._dyadic_binary64_bits(Fraction(-5, 4)) == 0xBFF4000000000000
    assert gate._dyadic_binary64_bits(Fraction(1, 256)) == 0x3F70000000000000
    with pytest.raises(ValueError):
        gate._dyadic_binary64_bits(Fraction(1, 3))
    with pytest.raises(ValueError):
        gate._dyadic_binary64_bits(Fraction(1, 2**1100))


def test_scientific_gate_source_has_no_float_literal_decimal_or_float_conversion() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"), filename=str(MODULE_PATH))
    assert not any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, float)
        for node in ast.walk(tree)
    )
    forbidden_calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"float", "Decimal"}:
            forbidden_calls.append(node.func.id)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "from_decimal":
            forbidden_calls.append(node.func.attr)
    assert forbidden_calls == []


def test_rational_interval_arithmetic_is_exact_and_fail_closed() -> None:
    left = gate.RationalInterval(Fraction(-1, 3), Fraction(2, 5))
    right = gate.RationalInterval(Fraction(-2), Fraction(3, 7))
    assert left + right == gate.RationalInterval(Fraction(-7, 3), Fraction(29, 35))
    assert left * right == gate.RationalInterval(Fraction(-4, 5), Fraction(2, 3))
    assert -left == gate.RationalInterval(Fraction(-2, 5), Fraction(1, 3))
    with pytest.raises(ValueError):
        gate.RationalInterval(Fraction(1), Fraction(0))


def test_polynomial_ring_primitives_match_test_local_literal_dictionaries() -> None:
    zero = (0, 0, 0, 0, 0, 0)
    t = (1, 0, 0, 0, 0, 0)
    y = (0, 1, 0, 0, 0, 0)
    ty = (1, 1, 0, 0, 0, 0)
    y2 = (0, 2, 0, 0, 0, 0)
    assert gate._mp_const(Fraction(3, 2)) == {zero: Fraction(3, 2)}
    assert gate._mp_var(0) == {t: Fraction(1)}
    assert gate._mp_var(1) == {y: Fraction(1)}
    assert gate._mp_add(
        {t: Fraction(2)}, {t: Fraction(-1), y: Fraction(3)}
    ) == {t: Fraction(1), y: Fraction(3)}
    assert gate._mp_neg({y: Fraction(5)}) == {y: Fraction(-5)}
    assert gate._mp_sub(
        {zero: Fraction(2), t: Fraction(1)},
        {zero: Fraction(3), y: Fraction(4)},
    ) == {zero: Fraction(-1), t: Fraction(1), y: Fraction(-4)}
    assert gate._mp_mul(
        {t: Fraction(2), y: Fraction(-1)}, {y: Fraction(3)}
    ) == {ty: Fraction(6), y2: Fraction(-3)}
    assert gate._mp_scale(
        {t: Fraction(2), y: Fraction(-3)}, Fraction(-2)
    ) == {t: Fraction(-4), y: Fraction(6)}
    primitives = gate._mp_primitive_ledger()
    assert primitives["pass"] is True
    assert all(primitives["checks"].values())


def test_radial_h0_and_b0_ranges_are_derived_by_exact_polynomial_identities() -> None:
    radial = gate._radial_envelope_ledger()
    assert radial["pass"] is True
    assert radial["h0_derivative_identity"] == "h0'=-30*rho^2*(1-rho)^2"
    assert radial["rho_one_minus_rho_identity"] == "1/4-rho*(1-rho)=(rho-1/2)^2"
    assert radial["b0_identity"] == "b0=64*[rho*(1-rho)]^3"
    assert radial["h0_range"] == gate._interval_json(
        gate.RationalInterval(Fraction(0), Fraction(1))
    )
    assert radial["b0_range"] == gate._interval_json(
        gate.RationalInterval(Fraction(0), Fraction(1))
    )


def test_symbolic_actual_and_reference_pullbacks_have_opposite_nonzero_side_signs() -> None:
    pullback = gate._pullback_identity_ledger()
    assert pullback["pass"] is True
    assert pullback["plus_pullback_nontrivial"] is True
    assert pullback["opposite_side_cross_signs"] is True
    assert pullback["sides"]["plus"]["radial_sign"] == -1
    assert pullback["sides"]["minus"]["radial_sign"] == 1
    assert pullback["sides"]["plus"]["actual_symbolic_identity_match"] is True
    assert pullback["sides"]["minus"]["reference_symbolic_identity_match"] is True
    expected_entries = {f"{row},{column}" for row in range(5) for column in range(5)}
    for side in ("plus", "minus"):
        actual_entries = pullback["sides"][side]["actual_full_matrix_entry_matches"]
        reference_entries = pullback["sides"][side][
            "reference_full_matrix_entry_matches"
        ]
        assert set(actual_entries) == expected_entries
        assert set(reference_entries) == expected_entries
        assert all(actual_entries.values())
        assert all(reference_entries.values())
    plus_actual = pullback["sides"]["plus"]["actual_cross_at_rho_one_x2_zero"]
    minus_actual = pullback["sides"]["minus"]["actual_cross_at_rho_one_x2_zero"]
    assert plus_actual["numerator"] == -minus_actual["numerator"]
    assert plus_actual["denominator"] == minus_actual["denominator"]
    assert plus_actual["numerator"] != 0
    plus = pullback["sides"]["plus"]["reference_cross_at_x2_zero"]
    minus = pullback["sides"]["minus"]["reference_cross_at_x2_zero"]
    assert plus["numerator"] == -minus["numerator"]
    assert plus["denominator"] == minus["denominator"]


def test_pulled_matrix_hashes_support_counts_degrees_and_signs_match_local_literals() -> None:
    pullback = gate._pullback_identity_ledger()
    actual_hashes = {}
    reference_hashes = {}
    for side, sign in (("plus", -1), ("minus", 1)):
        expected_actual, expected_reference = _local_literal_pulled_matrices(sign)
        row = pullback["sides"][side]
        actual_hashes[side] = _local_polynomial_matrix_sha256(expected_actual)
        reference_hashes[side] = _local_polynomial_matrix_sha256(expected_reference)
        assert row["actual_matrix_polynomial_payload_sha256"] == actual_hashes[side]
        assert (
            row["reference_matrix_polynomial_payload_sha256"]
            == reference_hashes[side]
        )
        assert row["actual_matrix_polynomial_stats"] == {
            "nonzero_polynomial_entries": 7,
            "monomial_support_t_y": [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]],
            "maximum_total_degree": 3,
        }
        assert row["reference_matrix_polynomial_stats"] == {
            "nonzero_polynomial_entries": 7,
            "monomial_support_t_y": [[0, 0], [0, 1], [0, 2]],
            "maximum_total_degree": 2,
        }
    assert actual_hashes["plus"] != actual_hashes["minus"]
    assert reference_hashes["plus"] != reference_hashes["minus"]


@pytest.mark.parametrize("function_name", ("_mp_const", "_mp_var"))
def test_empty_polynomial_primitive_source_mutants_abort_pullback_and_report(
    function_name: str,
) -> None:
    mutant = _load_gate_with_empty_function_return_mutant(function_name)
    pullback = mutant._pullback_identity_ledger()
    assert pullback["polynomial_ring_primitives"]["pass"] is False
    assert pullback["pass"] is False
    with pytest.raises(mutant.ExactMarginGateError):
        mutant.build_report()


def test_zero_base_x2_source_mutant_is_killed_by_independent_full_matrix_oracle() -> None:
    mutant = _load_gate_with_assignment_mutant("base_x2", "zero")
    pullback = mutant._pullback_identity_ledger()
    assert pullback["pass"] is False
    for side in ("plus", "minus"):
        assert pullback["sides"][side]["actual_symbolic_identity_match"] is False
        assert pullback["sides"][side]["actual_full_matrix_entry_matches"][
            "2,2"
        ] is False
        assert pullback["sides"][side]["reference_symbolic_identity_match"] is True


def test_metric_certificate_is_exact_for_actual_and_pulled_reference_on_both_sides() -> None:
    certificate = gate._margin_ledger()
    metric = certificate["metric_certificate"]
    assert certificate["pass"] is True
    assert metric["perturbation_upper"] == gate._fraction_json(Fraction(1539, 163840))
    assert metric["radial_upper_to_base_lower_ratio"] == gate._fraction_json(
        Fraction(16, 15)
    )
    assert metric["actual_and_reference_min_abs_eigenvalue_lower"] == gate._fraction_json(
        Fraction(182781, 163840)
    )
    assert metric["strict_slack_lower"] == gate._fraction_json(Fraction(897521, 819200))
    assert metric["exactly_one_negative_eigenvalue"] is True
    assert metric["both_actual_sides"] == ["plus", "minus"]
    assert metric["both_pulled_reference_sides"] == ["plus", "minus"]


def test_weyl_formula_recomputes_for_noncanonical_y_radial_upper_and_base_lower() -> None:
    cases = (
        (Fraction(1, 512), Fraction(5, 4), Fraction(1)),
        (Fraction(1, 128), Fraction(5, 4), Fraction(1)),
        (Fraction(1, 512), Fraction(3, 2), Fraction(1)),
        (Fraction(1, 512), Fraction(5, 4), Fraction(17, 16)),
    )
    observed = []
    for y_amplitude, radial_upper, base_lower in cases:
        member = copy.deepcopy(gate.canonical_member_contract())
        member["Y_amplitude"] = y_amplitude
        certificate = gate._margin_ledger(
            member_contract=member,
            weyl_radial_upper=radial_upper,
            weyl_base_positive_lower=base_lower,
        )
        metric = certificate["metric_certificate"]
        expected_perturbation = radial_upper * (
            2 * y_amplitude + y_amplitude * y_amplitude
        )
        expected_minimum = min(
            Fraction(5, 4), base_lower - expected_perturbation
        )
        assert _fraction_from_json(metric["perturbation_upper"]) == expected_perturbation
        assert _fraction_from_json(metric["base_positive_eigenvalue_lower"]) == base_lower
        assert (
            _fraction_from_json(
                metric["actual_and_reference_min_abs_eigenvalue_lower"]
            )
            == expected_minimum
        )
        observed.append((expected_perturbation, expected_minimum))
    assert observed[0][0] != observed[1][0]
    assert observed[0][0] != observed[2][0]
    assert observed[0][0] == observed[3][0]
    assert observed[0][1] != observed[3][1]


def test_frozen_canonical_weyl_literal_source_mutant_is_killed_metamorphically() -> None:
    mutant = _load_gate_with_assignment_mutant(
        "perturbation_upper", "Fraction(1539, 163840)"
    )
    member = copy.deepcopy(mutant.canonical_member_contract())
    member["Y_amplitude"] = Fraction(1, 512)
    certificate = mutant._margin_ledger(
        member_contract=member,
        weyl_radial_upper=Fraction(5, 4),
        weyl_base_positive_lower=Fraction(1),
    )
    observed = _fraction_from_json(
        certificate["metric_certificate"]["perturbation_upper"]
    )
    independently_expected = Fraction(5, 4) * (
        2 * Fraction(1, 512) + Fraction(1, 512) ** 2
    )
    assert observed == Fraction(1539, 163840)
    assert observed != independently_expected


def test_ghy_khronon_gram_omega_and_chart_leaves_recompute_metamorphically() -> None:
    member = copy.deepcopy(gate.canonical_member_contract())
    member["normal_metric"] = Fraction(5, 4)
    member["gamma_diagonal"] = [
        Fraction(-3, 2),
        Fraction(3, 2),
        Fraction(7, 4),
        Fraction(2),
    ]
    member["log_Omega_C_amplitude"] = Fraction(1, 32)
    chart_norms = {
        "q": Fraction(1, 2),
        "r_plus": Fraction(1, 3),
        "r_minus": Fraction(1, 4),
    }
    certificate = gate._margin_ledger(
        member_contract=member,
        chart_norm_upper_bounds=chart_norms,
    )
    assert _fraction_from_json(certificate["ghy_normal"]["inverse_rho_rho"]) == Fraction(
        4, 5
    )
    assert _fraction_from_json(
        certificate["khronon"]["gamma_inverse_contraction"]
    ) == Fraction(-2, 3)
    assert _fraction_from_json(certificate["khronon"]["strict_slack"]) == Fraction(
        7, 15
    )
    assert [
        _fraction_from_json(value)
        for value in certificate["frame_gram"]["pre_normalization_leading_minors"]
    ] == [Fraction(3, 2), Fraction(21, 8), Fraction(21, 4)]
    assert _fraction_from_json(certificate["Omega"]["lower"]) == Fraction(31, 32)
    assert _fraction_from_json(certificate["Omega"]["strict_slack"]) == Fraction(
        15, 32
    )
    charts = certificate["SO3_charts"]
    assert _fraction_from_json(charts["q_norm"]) == Fraction(1, 2)
    assert _fraction_from_json(charts["r_plus_norm"]) == Fraction(1, 3)
    assert _fraction_from_json(charts["r_minus_norm"]) == Fraction(1, 4)
    assert _fraction_from_json(
        charts["q_pi_minus_norm_minus_one_strictly_greater_than"]
    ) == Fraction(3, 2)
    assert _fraction_from_json(
        charts["r_plus_pi_minus_norm_minus_one_strictly_greater_than"]
    ) == Fraction(5, 3)
    assert _fraction_from_json(
        charts["r_minus_pi_minus_norm_minus_one_strictly_greater_than"]
    ) == Fraction(7, 4)

    receipt_oracles = gate._metamorphic_oracle_ledger()
    assert receipt_oracles["pass"] is True
    assert len(receipt_oracles["checks"]) == 6
    assert all(receipt_oracles["checks"].values())


def test_all_sixteen_analytic_margin_obligations_are_consumed_and_true() -> None:
    certificate = gate._margin_ledger()
    obligations = certificate["obligation_results"]
    assert set(obligations) == set(gate.ANALYTIC_MARGIN_OBLIGATIONS)
    assert len(obligations) == 16
    assert all(obligations.values())
    assert certificate["ghy_normal"]["inverse_rho_rho"] == gate._fraction_json(Fraction(8, 9))
    assert certificate["khronon"]["gamma_inverse_contraction"] == gate._fraction_json(
        Fraction(-4, 5)
    )
    assert certificate["khronon"]["strict_slack"] == gate._fraction_json(Fraction(3, 5))
    assert certificate["frame_gram"]["pre_normalization_leading_minors"] == [
        gate._fraction_json(Fraction(9, 8)),
        gate._fraction_json(Fraction(45, 32)),
        gate._fraction_json(Fraction(495, 256)),
    ]
    assert certificate["Omega"]["lower"] == gate._fraction_json(Fraction(63, 64))
    assert certificate["Omega"]["strict_slack"] == gate._fraction_json(Fraction(31, 64))
    assert set(certificate["SO3_charts"]) >= {
        "q_norm",
        "r_plus_norm",
        "r_minus_norm",
    }


def test_member_mutants_kill_shell_direction_channel_side_sign_and_nontrivial_pullback() -> None:
    campaign = gate._mutant_campaign()
    member = campaign["member_mutants"]
    assert set(member) == {
        "N_81_to_80_not_a_complete_shell",
        "replace_new_x2_direction_by_legacy_theta",
        "move_C_from_log_Omega_channel_15_to_metric_channel_14",
        "omit_minus_side_member_data",
        "flip_plus_pullback_radial_sign",
        "erase_nontrivial_pullback_by_zeroing_Y",
    }
    assert all(member.values())


def test_margin_mutants_kill_reference_pulled_ambient_normal_gram_dtau_omega_charts_and_rounding() -> None:
    campaign = gate._mutant_campaign()
    margins = campaign["margin_mutants"]
    assert set(margins) == {
        "omit_pulled_reference_minus",
        "replace_actual_pulled_metric_by_ambient_metric",
        "replace_pulled_reference_by_ambient_reference",
        "omit_minus_GHY_normal",
        "omit_frame_Gram_leading_minor_2",
        "omit_dx0_from_d_tau",
        "treat_log_Omega_as_Omega",
        "replace_three_separate_charts_by_product_chart",
        "replace_exact_outward_enclosure_by_inward_rounding",
        "drop_one_analytic_margin_obligation",
        "swap_Weyl_radial_upper_and_base_positive_lower",
    }
    assert all(margins.values())


def test_weyl_radial_base_ratio_mutant_is_killed_by_the_bounds_not_contract_matching() -> None:
    mutant = gate._margin_ledger(
        weyl_base_positive_lower=gate.WEYL_RADIAL_UPPER,
        weyl_radial_upper=gate.WEYL_BASE_POSITIVE_LOWER,
    )
    assert mutant["contract_exact_match"] is True
    assert mutant["member_contract_exact_match"] is True
    assert mutant["reference_metric"]["checks"]["all_spatial_above_base_lower"] is False
    assert mutant["reference_metric"]["checks"]["radial_below_rational_upper"] is False
    assert mutant["pass"] is False
    assert gate._mutant_campaign()["margin_mutants"][
        "swap_Weyl_radial_upper_and_base_positive_lower"
    ] is True


def test_every_global_promotion_mutant_is_rejected() -> None:
    campaign = gate._mutant_campaign()
    promotions = campaign["promotion_mutants"]
    assert len(promotions) == len(gate.FALSE_DECISION_KEYS)
    assert all(promotions.values())
    assert campaign["all_mutants_effective"] is True
    assert campaign["pass"] is True


def test_decision_allowlists_have_only_scoped_support_and_one_finite_margin_result() -> None:
    report = gate.build_report()
    decision = report["decision"]
    assert {key for key, value in decision.items() if value} == set(gate.TRUE_DECISION_KEYS)
    assert {key for key, value in decision.items() if not value} == set(gate.FALSE_DECISION_KEYS)
    assert decision["named_full_t4_finite_member_whole_domain_analytic_margins_exact_pass"] is True
    assert decision["finite_member_whole_domain_outward_rounded_margin_certificate_pass"] is True
    for key in gate.FALSE_DECISION_KEYS:
        assert decision[key] is False
    assert report["scope"]["bd61d22_conclusion_used_as_oracle"] is False
    assert "stabilize" in report["scope"]["meaning"]


def test_report_and_artifact_contain_no_float_and_receipt_is_reproducible() -> None:
    report = gate.build_report()
    assert gate._contains_float(report) is False
    assert _walk_has_float(report) is False
    json.dumps(report, sort_keys=True, allow_nan=False)
    artifact = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
    assert artifact == report
    assert _walk_has_float(artifact) is False


def test_actual_float64_decoder_matches_special_point_canaries_but_is_not_a_proof_input() -> None:
    """A binding canary only; build_report never calls this float evaluator."""

    decoder = _load_v5671_for_non_authoritative_canary()
    free = np.frombuffer(gate.member_f64le_bytes(), dtype="<f8")
    tangent = np.zeros_like(free)

    plus = decoder.decode_full_t4_collar_point(
        free, tangent, 81, 1, (0, 0, 0, 0), Fraction(1, 2), "plus"
    )
    plus_actual = _symmetric5_from_packed(
        np.asarray(plus["pulled_X64"]["primal"]["value"][:15], dtype=float)
    )
    plus_reference = _symmetric5_from_packed(
        np.asarray(
            plus["pulled_reference_metric15"]["primal"]["value"], dtype=float
        )
    )
    reference_radial = float(gate.REFERENCE_METRIC_DIAGONAL[4])
    assert math.isclose(plus_actual[2, 4], -reference_radial / 512, rel_tol=0, abs_tol=1e-15)
    assert math.isclose(plus_reference[2, 4], -reference_radial / 256, rel_tol=0, abs_tol=1e-15)
    assert plus["pulled_X64"]["primal"]["value"][15] == float(Fraction(1, 64))

    minus = decoder.decode_full_t4_collar_point(
        free, tangent, 81, 1, (0, 0, 0, 0), 1, "minus"
    )
    minus_actual = _symmetric5_from_packed(
        np.asarray(minus["pulled_X64"]["primal"]["value"][:15], dtype=float)
    )
    assert math.isclose(minus_actual[2, 4], reference_radial / 256, rel_tol=0, abs_tol=1e-15)
    assert gate.build_report()["whole_domain_exact_margin_certificate"]["arithmetic"][
        "float_or_decimal_consumed_by_decisions"
    ] is False
