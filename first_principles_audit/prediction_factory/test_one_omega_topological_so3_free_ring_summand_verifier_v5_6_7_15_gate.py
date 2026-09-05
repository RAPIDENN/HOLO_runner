#!/usr/bin/env python3
"""Independent tests for the narrow v5.6.7.15 free-ring kernel."""

from __future__ import annotations

from fractions import Fraction
import copy
import hashlib
import inspect
from pathlib import Path
import types

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_free_ring_summand_verifier_v5_6_7_15_gate
    as gate,
)


EXPECTED_LEIBNIZ_CODE_SHA256 = (
    "5ce4dbc9adda5d3f618ac02c1cddf660ee009330206cf9ad6417523cf9953852"
)
EXPECTED_TCB_MANIFEST_SHA256 = (
    "12739810b8ccb2d57434f1d32ebd3440f68f546551c2b5346da39535a2399c44"
)
EXPECTED_SOURCE_SHA256 = (
    "b62422915e2188afe8393ee752e5c0f9a999d09d1ecceae0bd746673b3c9518e"
)


def test_sparse_ring_normalizes_exactly_without_values() -> None:
    x = gate.Polynomial.generator("x")
    y = gate.Polynomial.generator("y")
    assert ((x + y) * (x - y)).row() == [
        {"coefficient": [1, 1], "powers": [["x", 2]]},
        {"coefficient": [-1, 1], "powers": [["y", 2]]},
    ]
    assert (x - x).is_zero is True
    assert gate.Polynomial.constant(Fraction(2, 3)).power(3).row() == [
        {"coefficient": [8, 27], "powers": []}
    ]
    with pytest.raises(gate.FreeRingVerifierError, match="int or Fraction"):
        gate.Polynomial.constant(0.5)
    with pytest.raises(gate.FreeRingVerifierError, match="int or Fraction"):
        x.scale(True)


def test_leibniz_derivative_and_linear_slot_extraction_are_exact() -> None:
    signature = gate.RingSignature(
        parameters=("a",),
        fields=("x", "y"),
        variations=("v::x", "v::y"),
    )
    a = gate.Polynomial.generator("a")
    x = gate.Polynomial.generator("x")
    y = gate.Polynomial.generator("y")
    primal = a * x.power(2) * y
    rules = {
        "x": gate.Polynomial.generator("v::x"),
        "y": gate.Polynomial.generator("v::y"),
    }
    coefficients = gate.linear_variation_coefficients(
        gate.leibniz_derivative(primal, signature, rules), signature
    )
    assert coefficients["v::x"] == a * x * y.scale(2)
    assert coefficients["v::y"] == a * x.power(2)


def test_integer_power_rule_includes_exponents_above_two() -> None:
    certificate = gate._integer_power_rule_certificate()
    assert certificate["tested_exponents"] == [0, 1, 2, 3, 5]
    assert certificate["pass"] is True
    assert certificate["rows"]["3"]["observed"] == [
        {
            "coefficient": [3, 1],
            "powers": [["v::x", 1], ["x", 2]],
        }
    ]
    assert certificate["rows"]["5"]["observed"] == [
        {
            "coefficient": [5, 1],
            "powers": [["v::x", 1], ["x", 4]],
        }
    ]


def test_trusted_leibniz_code_and_module_source_are_independently_pinned() -> None:
    assert gate.EXPECTED_LEIBNIZ_CODE_SHA256 == EXPECTED_LEIBNIZ_CODE_SHA256
    assert gate._callable_code_sha256(gate.leibniz_derivative) == (
        EXPECTED_LEIBNIZ_CODE_SHA256
    )
    assert hashlib.sha256(Path(gate.__file__).read_bytes()).hexdigest() == (
        EXPECTED_SOURCE_SHA256
    )
    certificate = gate._trusted_kernel_code_certificate()
    assert gate.EXPECTED_TCB_MANIFEST_SHA256 == EXPECTED_TCB_MANIFEST_SHA256
    assert certificate["manifest_sha256"] == EXPECTED_TCB_MANIFEST_SHA256
    assert certificate["pass"] is True


def test_same_sign_duplicate_drop_mutant_fails_complete_tcb_pin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def attacked_from_terms(rows):
        merged = {}
        for powers, coefficient_raw in rows:
            coefficient = gate._exact_fraction(coefficient_raw)
            monomial = gate._canonical_monomial(powers)
            if coefficient:
                if monomial in merged and merged[monomial] * coefficient > 0:
                    continue
                merged[monomial] = merged.get(monomial, Fraction(0)) + coefficient
                if not merged[monomial]:
                    del merged[monomial]
        return gate.Polynomial(tuple(sorted(merged.items())))

    monkeypatch.setattr(
        gate.Polynomial, "from_terms", staticmethod(attacked_from_terms)
    )
    report = gate.build_report()
    assert report["status"] == "NOT_READY"
    assert report["checks"][
        "local_callable_code_and_environment_snapshot_matches_audited_pin"
    ] is False
    assert report["trusted_kernel"]["audited_local_callable_manifest"]["pass"] is False


def test_same_code_with_private_global_namespace_fails_environment_pin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signature = gate.RingSignature(
        parameters=(), fields=("x",), variations=("v::x",)
    )
    primal = gate.Polynomial.generator("x")
    rules = {"x": gate.Polynomial.generator("v::x")}
    attacked_claim = [
        {
            "slot": "v::x",
            "coefficient": gate.encode_polynomial_ast(
                gate.Polynomial.constant(Fraction(8, 7))
            ),
        }
    ]
    assert gate.verify_claimed_coefficients(
        primal, signature, rules, attacked_claim
    )["pass"] is False

    original = gate.decode_polynomial_ast
    private_globals = dict(original.__globals__)

    def improper_fraction_floor(numerator, denominator=1):
        if denominator != 1 and abs(numerator) > denominator:
            return Fraction(numerator // denominator)
        return Fraction(numerator, denominator)

    private_globals["Fraction"] = improper_fraction_floor
    clone = types.FunctionType(
        original.__code__,
        private_globals,
        original.__name__,
        original.__defaults__,
        original.__closure__,
    )
    clone.__kwdefaults__ = original.__kwdefaults__
    private_globals["decode_polynomial_ast"] = clone
    monkeypatch.setattr(gate, "decode_polynomial_ast", clone)

    assert gate.verify_claimed_coefficients(
        primal, signature, rules, attacked_claim
    )["pass"] is True
    report = gate.build_report()
    certificate = report["trusted_kernel"]["audited_local_callable_manifest"]
    assert report["status"] == "NOT_READY"
    assert certificate["rows"]["decode_polynomial_ast"]["environment_pass"] is False
    assert certificate["pass"] is False


def test_exponent_truncation_mutant_makes_real_report_not_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = inspect.getsource(gate.leibniz_derivative)
    attacked_source = source.replace(
        "coefficient * exponent", "coefficient * min(exponent, 2)"
    )
    assert attacked_source != source
    namespace = dict(gate.__dict__)
    exec(attacked_source, namespace)
    monkeypatch.setattr(
        gate, "leibniz_derivative", namespace["leibniz_derivative"]
    )
    report = gate.build_report()
    assert report["status"] == "NOT_READY"
    assert report["checks"]["integer_power_Leibniz_rule_exact_at_0_1_2_3_5"] is False
    assert report["integer_power_rule_certificate"]["rows"]["3"]["pass"] is False


def test_finite_exponent_alias_mutant_fails_live_code_pin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = inspect.getsource(gate.leibniz_derivative)
    attacked_source = source.replace(
        "coefficient * exponent",
        "coefficient * exponent + coefficient * exponent * (exponent - 1) * "
        "(exponent - 2) * (exponent - 3) * (exponent - 5)",
    )
    assert attacked_source != source
    namespace = dict(gate.__dict__)
    exec(attacked_source, namespace)
    monkeypatch.setattr(
        gate, "leibniz_derivative", namespace["leibniz_derivative"]
    )
    report = gate.build_report()
    assert report["integer_power_rule_certificate"]["pass"] is True
    assert report["trusted_kernel"]["code_object_pin_pass"] is False
    assert report["checks"]["trusted_Leibniz_code_object_matches_audited_pin"] is False
    assert report["status"] == "NOT_READY"


def test_every_field_requires_an_explicit_rule() -> None:
    signature = gate.RingSignature(
        parameters=(), fields=("x",), variations=("v::x",)
    )
    with pytest.raises(gate.FreeRingVerifierError, match="cover every field"):
        gate.leibniz_derivative(
            gate.Polynomial.generator("x"), signature, {}
        )


def test_each_generator_rule_is_linear_before_cross_field_cancellation() -> None:
    signature = gate.RingSignature(
        parameters=(),
        fields=("x", "y"),
        variations=("v::x", "v::y"),
    )
    vx = gate.Polynomial.generator("v::x")
    vy = gate.Polynomial.generator("v::y")
    rules = {"x": vx + vx.power(2), "y": vy - vx.power(2)}
    with pytest.raises(gate.FreeRingVerifierError, match="term by term"):
        gate.leibniz_derivative(
            gate.Polynomial.generator("x") + gate.Polynomial.generator("y"),
            signature,
            rules,
        )


def test_raw_polynomial_constructor_cannot_bypass_canonical_invariants() -> None:
    with pytest.raises(gate.FreeRingVerifierError, match="exponents"):
        gate.Polynomial((((("x", True),), Fraction(1)),))
    with pytest.raises(gate.FreeRingVerifierError, match="coefficient"):
        gate.Polynomial((((("x", 1),), True),))
    with pytest.raises(gate.FreeRingVerifierError, match="unique and sorted"):
        gate.Polynomial(
            (
                ((("y", 1),), Fraction(1)),
                ((("x", 1),), Fraction(1)),
            )
        )


def test_nonlinear_or_vacuous_variation_fails_closed() -> None:
    signature = gate.RingSignature(
        parameters=(), fields=("x",), variations=("v::x",)
    )
    with pytest.raises(gate.FreeRingVerifierError, match="degree exactly one"):
        gate.linear_variation_coefficients(
            gate.Polynomial.generator("v::x").power(2), signature
        )
    with pytest.raises(gate.FreeRingVerifierError, match="vacuous"):
        gate.linear_variation_coefficients(gate.Polynomial.constant(0), signature)


def test_json_adapter_is_total_and_rejects_unknown_data() -> None:
    allowed = frozenset({"x"})
    assert gate.decode_polynomial_ast(
        {
            "op": "mul",
            "args": [
                {"op": "const", "value": [-3, 5]},
                {"op": "pow", "arg": {"op": "symbol", "name": "x"}, "exponent": 2},
            ],
        },
        allowed,
    ).row() == [{"coefficient": [-3, 5], "powers": [["x", 2]]}]
    with pytest.raises(gate.FreeRingVerifierError, match="key inventory"):
        gate.decode_polynomial_ast(
            {"op": "symbol", "name": "x", "ignored": True}, allowed
        )
    with pytest.raises(gate.FreeRingVerifierError, match="outside the closed alphabet"):
        gate.decode_polynomial_ast({"op": "symbol", "name": "y"}, allowed)
    with pytest.raises(gate.FreeRingVerifierError, match="unknown.*opcode"):
        gate.decode_polynomial_ast({"op": "reduce", "args": []}, allowed)
    with pytest.raises(gate.FreeRingVerifierError, match="non-negative integer"):
        gate.decode_polynomial_ast(
            {"op": "pow", "arg": {"op": "symbol", "name": "x"}, "exponent": True},
            allowed,
        )


def test_exact_claims_pass_and_missing_duplicate_or_extra_rows_fail() -> None:
    signature, primal, rules, expected = gate._kernel_fixture()
    claims = gate._claims(expected)
    assert gate.verify_claimed_coefficients(primal, signature, rules, claims)["pass"]
    assert not gate.verify_claimed_coefficients(
        primal, signature, rules, claims[:-1]
    )["pass"]
    with pytest.raises(gate.FreeRingVerifierError, match="duplicate"):
        gate.verify_claimed_coefficients(
            primal, signature, rules, [*claims, copy.deepcopy(claims[0])]
        )
    bad = copy.deepcopy(claims)
    bad[0]["ignored"] = 1
    with pytest.raises(gate.FreeRingVerifierError, match="key inventory"):
        gate.verify_claimed_coefficients(primal, signature, rules, bad)


@pytest.mark.parametrize(
    "name",
    (
        "M1_M5_two_point_alias",
        "M2_forbidden_trace_generator",
        "M3_u01_two_point_alias",
        "M4_u01_one_point_alias",
    ),
)
def test_required_alias_mutants_are_killed_symbolically(name: str) -> None:
    campaign = gate._mutation_campaign()
    assert campaign["finite_witnesses_used"] is False
    assert campaign["rows"][name]["killed"] is True


def test_finite_aliases_fail_through_real_adapter_without_campaign_oracle() -> None:
    signature = gate.RingSignature(
        parameters=("M5", "u01"),
        fields=("x", "y"),
        variations=("v::x", "v::y"),
    )
    m5 = gate.Polynomial.generator("M5")
    u01 = gate.Polynomial.generator("u01")
    x = gate.Polynomial.generator("x")
    y = gate.Polynomial.generator("y")
    primal = m5.power(3) * x + u01 * y
    rules = {
        "x": gate.Polynomial.generator("v::x"),
        "y": gate.Polynomial.generator("v::y"),
    }
    one = gate.Polynomial.constant(1)
    aliases = (
        {
            "v::x": m5.power(3)
            * (one + (m5 + gate.Polynomial.constant(-2)) * (m5 + gate.Polynomial.constant(-3))),
            "v::y": u01,
        },
        {
            "v::x": m5.power(3),
            "v::y": u01
            * (
                one
                + (u01 + gate.Polynomial.constant(Fraction(1, 5)))
                * (u01 + gate.Polynomial.constant(Fraction(-22, 105)))
            ),
        },
        {"v::x": m5.power(3), "v::y": u01 * u01.scale(-5)},
    )
    for attacked in aliases:
        result = gate.verify_claimed_coefficients(
            primal,
            signature,
            rules,
            [
                {
                    "slot": slot,
                    "coefficient": gate.encode_polynomial_ast(coefficient),
                }
                for slot, coefficient in sorted(attacked.items())
            ],
        )
        assert result["pass"] is False
        assert any(
            row["residual_term_count"] > 0 for row in result["rows"].values()
        )


def test_coherent_theory_change_is_explicitly_outside_kernel_scope() -> None:
    report = gate.build_report()
    boundary = report["trust_boundary"]
    assert boundary["coherent_primal_and_row_theory_change_is_detected"] is False
    assert boundary["coherent_theory_change_fixture_passes_algebra"] is True
    assert boundary["runtime_self_attestation_against_arbitrary_co_mutation"] is False
    assert "source decoder" in boundary["closure_requires"]


def test_report_is_kernel_ready_but_promotes_no_physics_or_c1_n1() -> None:
    report = gate.build_report()
    assert report["status"] == "KERNEL_READY"
    assert report["checks"]["all"] is True
    assert report["mandatory_mutant_certificate"]["pass"] is True
    assert report["evaluated_components"] == []
    assert report["not_evaluated_components"]
    assert report["decision"]["free_ring_kernel_ready_pass"] is True
    for key, value in report["decision"].items():
        if key != "free_ring_kernel_ready_pass":
            assert value is False, key
