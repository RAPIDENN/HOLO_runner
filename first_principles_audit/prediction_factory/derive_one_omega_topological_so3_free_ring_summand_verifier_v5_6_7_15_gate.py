#!/usr/bin/env python3
"""Exact free-ring kernel for later whole-summand variation certificates.

This module deliberately stops before geometry.  It proves only that a set of
claimed linearised coefficients is the exact Leibniz derivative of a supplied
polynomial in ``Q[Sigma]`` under a closed, typed generator inventory.  It does
not yet expand EH, GHY, intrinsic curvature, Green currents, or shape terms.

The narrow kernel exists to remove a recurring unsound pattern from the
v5.6.7 gates: finitely many rational witnesses cannot decide a polynomial
identity when the producer of the candidate is adversarial.  Here zero means
an empty canonical sparse polynomial; no generator is ever assigned a value.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import argparse
import hashlib
import json
import re
import types
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "holo.v5-6-7-15-free-ring-summand-verifier-kernel-v1"
SYMBOL_RE = re.compile(r"[A-Za-z][A-Za-z0-9_:.+-]*\Z")
VARIATION_PREFIX = "v::"
EXPECTED_LEIBNIZ_CODE_SHA256 = (
    "5ce4dbc9adda5d3f618ac02c1cddf660ee009330206cf9ad6417523cf9953852"
)
EXPECTED_TCB_MANIFEST_SHA256 = (
    "12739810b8ccb2d57434f1d32ebd3440f68f546551c2b5346da39535a2399c44"
)


class FreeRingVerifierError(RuntimeError):
    """The ring signature, expression grammar, or variation is malformed."""


Monomial = tuple[tuple[str, int], ...]


def _exact_fraction(value: Fraction | int) -> Fraction:
    if type(value) is int:
        return Fraction(value)
    if type(value) is Fraction:
        return value
    raise FreeRingVerifierError("free-ring coefficients must be int or Fraction")


def _canonical_monomial(powers: Iterable[tuple[str, int]]) -> Monomial:
    merged: dict[str, int] = {}
    for symbol, exponent in powers:
        if type(symbol) is not str or SYMBOL_RE.fullmatch(symbol) is None:
            raise FreeRingVerifierError(f"invalid generator name: {symbol!r}")
        if type(exponent) is not int or exponent < 0:
            raise FreeRingVerifierError("free-ring exponents must be non-negative integers")
        if exponent:
            merged[symbol] = merged.get(symbol, 0) + exponent
    return tuple(sorted((symbol, exponent) for symbol, exponent in merged.items() if exponent))


@dataclass(frozen=True)
class Polynomial:
    """Canonical sparse polynomial over exact rational coefficients."""

    terms: tuple[tuple[Monomial, Fraction], ...]

    def __post_init__(self) -> None:
        if type(self.terms) is not tuple:
            raise FreeRingVerifierError("polynomial terms must be a canonical tuple")
        previous: Monomial | None = None
        for row in self.terms:
            if type(row) is not tuple or len(row) != 2:
                raise FreeRingVerifierError("polynomial term is not a pair")
            monomial, coefficient = row
            if type(monomial) is not tuple or _canonical_monomial(monomial) != monomial:
                raise FreeRingVerifierError("polynomial monomial is not canonical")
            if type(coefficient) is not Fraction or not coefficient:
                raise FreeRingVerifierError("polynomial coefficient is not a nonzero Fraction")
            if previous is not None and not previous < monomial:
                raise FreeRingVerifierError("polynomial terms are not unique and sorted")
            previous = monomial

    @staticmethod
    def from_terms(
        rows: Iterable[tuple[Iterable[tuple[str, int]], Fraction | int]],
    ) -> "Polynomial":
        merged: dict[Monomial, Fraction] = {}
        for powers, coefficient_raw in rows:
            coefficient = _exact_fraction(coefficient_raw)
            monomial = _canonical_monomial(powers)
            if coefficient:
                merged[monomial] = merged.get(monomial, Fraction(0)) + coefficient
                if not merged[monomial]:
                    del merged[monomial]
        return Polynomial(tuple(sorted(merged.items())))

    @staticmethod
    def zero() -> "Polynomial":
        return Polynomial(())

    @staticmethod
    def constant(value: Fraction | int) -> "Polynomial":
        return Polynomial.from_terms([((), value)])

    @staticmethod
    def generator(name: str) -> "Polynomial":
        return Polynomial.from_terms([(((name, 1),), 1)])

    def __add__(self, other: "Polynomial") -> "Polynomial":
        return Polynomial.from_terms((*self.terms, *other.terms))

    def __neg__(self) -> "Polynomial":
        return self.scale(-1)

    def __sub__(self, other: "Polynomial") -> "Polynomial":
        return self + (-other)

    def scale(self, coefficient: Fraction | int) -> "Polynomial":
        exact = _exact_fraction(coefficient)
        return Polynomial.from_terms(
            (monomial, value * exact)
            for monomial, value in self.terms
        )

    def __mul__(self, other: "Polynomial") -> "Polynomial":
        return Polynomial.from_terms(
            ((*left, *right), left_coefficient * right_coefficient)
            for left, left_coefficient in self.terms
            for right, right_coefficient in other.terms
        )

    def power(self, exponent: int) -> "Polynomial":
        if type(exponent) is not int or exponent < 0:
            raise FreeRingVerifierError("polynomial power must be a non-negative integer")
        result = Polynomial.constant(1)
        factor = self
        remaining = exponent
        while remaining:
            if remaining & 1:
                result = result * factor
            remaining >>= 1
            if remaining:
                factor = factor * factor
        return result

    @property
    def symbols(self) -> frozenset[str]:
        return frozenset(symbol for monomial, _ in self.terms for symbol, _ in monomial)

    @property
    def is_zero(self) -> bool:
        return not self.terms

    def row(self) -> list[dict[str, Any]]:
        return [
            {
                "coefficient": [coefficient.numerator, coefficient.denominator],
                "powers": [[symbol, exponent] for symbol, exponent in monomial],
            }
            for monomial, coefficient in self.terms
        ]


@dataclass(frozen=True)
class RingSignature:
    """Closed inventory; every field must have an explicit variation rule."""

    parameters: tuple[str, ...]
    fields: tuple[str, ...]
    variations: tuple[str, ...]

    def __post_init__(self) -> None:
        groups = (self.parameters, self.fields, self.variations)
        if any(type(group) is not tuple for group in groups):
            raise FreeRingVerifierError("signature groups must be tuples")
        flattened = (*self.parameters, *self.fields, *self.variations)
        if len(flattened) != len(set(flattened)):
            raise FreeRingVerifierError("signature generators must be unique across kinds")
        if any(SYMBOL_RE.fullmatch(name) is None for name in flattened):
            raise FreeRingVerifierError("signature contains an invalid generator")
        if any(not name.startswith(VARIATION_PREFIX) for name in self.variations):
            raise FreeRingVerifierError("variation generators require the v:: prefix")
        if any(name.startswith(VARIATION_PREFIX) for name in (*self.parameters, *self.fields)):
            raise FreeRingVerifierError("only variation generators may use the v:: prefix")

    @property
    def all_symbols(self) -> frozenset[str]:
        return frozenset((*self.parameters, *self.fields, *self.variations))


def _assert_symbols(polynomial: Polynomial, allowed: frozenset[str], label: str) -> None:
    unknown = polynomial.symbols - allowed
    if unknown:
        raise FreeRingVerifierError(f"{label} contains generators outside Sigma: {sorted(unknown)}")


def _assert_rule_is_linear(
    rule: Polynomial, signature: RingSignature, label: str
) -> None:
    if rule.is_zero:
        raise FreeRingVerifierError(f"{label} is vacuous")
    variation_set = set(signature.variations)
    for monomial, _ in rule.terms:
        variation_degree = sum(
            exponent for symbol, exponent in monomial if symbol in variation_set
        )
        if variation_degree != 1:
            raise FreeRingVerifierError(
                f"{label} must be linear in variation generators term by term"
            )


def leibniz_derivative(
    primal: Polynomial,
    signature: RingSignature,
    field_rules: Mapping[str, Polynomial],
) -> Polynomial:
    """Apply the unique derivation fixed by ``D(parameter)=0`` and field rules."""

    _assert_symbols(primal, frozenset((*signature.parameters, *signature.fields)), "primal")
    if type(field_rules) is not dict or set(field_rules) != set(signature.fields):
        raise FreeRingVerifierError("variation rules must cover every field exactly once")
    for field_name, rule in field_rules.items():
        if not isinstance(rule, Polynomial):
            raise FreeRingVerifierError(f"variation rule for {field_name} is not a polynomial")
        _assert_symbols(rule, signature.all_symbols, f"variation rule {field_name}")
        _assert_rule_is_linear(rule, signature, f"variation rule {field_name}")

    result = Polynomial.zero()
    for monomial, coefficient in primal.terms:
        for symbol, exponent in monomial:
            if symbol in signature.parameters:
                continue
            if symbol not in field_rules:
                raise FreeRingVerifierError(f"no variation rule for field {symbol}")
            residual_powers = list(monomial)
            index = residual_powers.index((symbol, exponent))
            if exponent == 1:
                del residual_powers[index]
            else:
                residual_powers[index] = (symbol, exponent - 1)
            residual = Polynomial.from_terms([(residual_powers, coefficient * exponent)])
            result = result + residual * field_rules[symbol]
    return result


def _callable_code_sha256(function: Any) -> str:
    code = getattr(function, "__code__", None)
    if code is None:
        raise FreeRingVerifierError("trusted kernel callable has no Python code object")

    def constant_row(value: Any) -> Any:
        if isinstance(value, types.CodeType):
            return {"code": code_row(value)}
        if isinstance(value, tuple):
            return {"tuple": [constant_row(item) for item in value]}
        if isinstance(value, frozenset):
            return {"frozenset": sorted((constant_row(item) for item in value), key=repr)}
        if isinstance(value, bytes):
            return {"bytes": value.hex()}
        if value is None or type(value) in {bool, int, float, str}:
            return value
        raise FreeRingVerifierError(
            f"unsupported trusted-code constant {type(value).__name__}"
        )

    def code_row(item: types.CodeType) -> dict[str, Any]:
        return {
            "argcount": item.co_argcount,
            "posonlyargcount": item.co_posonlyargcount,
            "kwonlyargcount": item.co_kwonlyargcount,
            "flags": item.co_flags,
            "code": item.co_code.hex(),
            "consts": [constant_row(value) for value in item.co_consts],
            "names": list(item.co_names),
            "varnames": list(item.co_varnames),
            "freevars": list(item.co_freevars),
            "cellvars": list(item.co_cellvars),
            "exceptiontable": item.co_exceptiontable.hex(),
        }

    payload = code_row(code)
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def linear_variation_coefficients(
    derivative: Polynomial,
    signature: RingSignature,
) -> dict[str, Polynomial]:
    """Extract exact coefficients of degree-one variation generators."""

    _assert_symbols(derivative, signature.all_symbols, "derivative")
    variation_set = set(signature.variations)
    grouped: dict[str, list[tuple[Monomial, Fraction]]] = {}
    for monomial, coefficient in derivative.terms:
        variation_powers = [
            (symbol, exponent) for symbol, exponent in monomial if symbol in variation_set
        ]
        total_degree = sum(exponent for _, exponent in variation_powers)
        if total_degree != 1 or len(variation_powers) != 1:
            raise FreeRingVerifierError(
                "Frechet derivative must have variation degree exactly one in every term"
            )
        slot, exponent = variation_powers[0]
        if exponent != 1:
            raise FreeRingVerifierError("variation slot exponent must be one")
        background = tuple((symbol, power) for symbol, power in monomial if symbol != slot)
        grouped.setdefault(slot, []).append((background, coefficient))
    coefficients = {
        slot: Polynomial.from_terms(terms) for slot, terms in sorted(grouped.items())
    }
    missing = set(signature.variations) - set(coefficients)
    if missing:
        raise FreeRingVerifierError(f"declared variation slots are vacuous: {sorted(missing)}")
    return coefficients


def _require_keys(value: Any, keys: Sequence[str], label: str) -> None:
    if type(value) is not dict or tuple(value) != tuple(keys):
        raise FreeRingVerifierError(f"{label} key inventory/order drift")


def decode_polynomial_ast(value: Any, allowed_symbols: frozenset[str]) -> Polynomial:
    """Total JSON adapter.  It performs no identity-specific simplification."""

    if type(value) is not dict or "op" not in value:
        raise FreeRingVerifierError("polynomial AST node is not an operation object")
    operation = value["op"]
    if operation == "const":
        _require_keys(value, ("op", "value"), "const")
        rational = value["value"]
        if (
            type(rational) is not list
            or len(rational) != 2
            or type(rational[0]) is not int
            or type(rational[1]) is not int
            or type(rational[0]) is bool
            or type(rational[1]) is bool
            or rational[1] == 0
        ):
            raise FreeRingVerifierError("const value is not an exact rational pair")
        return Polynomial.constant(Fraction(rational[0], rational[1]))
    if operation == "symbol":
        _require_keys(value, ("op", "name"), "symbol")
        name = value["name"]
        if type(name) is not str or name not in allowed_symbols:
            raise FreeRingVerifierError(f"symbol {name!r} is outside the closed alphabet")
        return Polynomial.generator(name)
    if operation in {"add", "mul"}:
        _require_keys(value, ("op", "args"), operation)
        args = value["args"]
        if type(args) is not list or not args:
            raise FreeRingVerifierError(f"{operation} requires a non-empty operand list")
        decoded = [decode_polynomial_ast(arg, allowed_symbols) for arg in args]
        result = Polynomial.zero() if operation == "add" else Polynomial.constant(1)
        for item in decoded:
            result = result + item if operation == "add" else result * item
        return result
    if operation == "pow":
        _require_keys(value, ("op", "arg", "exponent"), "pow")
        exponent = value["exponent"]
        if type(exponent) is not int or exponent < 0:
            raise FreeRingVerifierError("pow exponent must be a non-negative integer")
        return decode_polynomial_ast(value["arg"], allowed_symbols).power(exponent)
    raise FreeRingVerifierError(f"unknown polynomial AST opcode: {operation!r}")


def encode_polynomial_ast(polynomial: Polynomial) -> dict[str, Any]:
    """Canonical verbose AST used only as a transport fixture for this kernel."""

    terms: list[dict[str, Any]] = []
    for monomial, coefficient in polynomial.terms:
        factors: list[dict[str, Any]] = [
            {
                "op": "const",
                "value": [coefficient.numerator, coefficient.denominator],
            }
        ]
        for symbol, exponent in monomial:
            node: dict[str, Any] = {"op": "symbol", "name": symbol}
            if exponent != 1:
                node = {"op": "pow", "arg": node, "exponent": exponent}
            factors.append(node)
        terms.append(factors[0] if len(factors) == 1 else {"op": "mul", "args": factors})
    if not terms:
        return {"op": "const", "value": [0, 1]}
    return terms[0] if len(terms) == 1 else {"op": "add", "args": terms}


def verify_claimed_coefficients(
    primal: Polynomial,
    signature: RingSignature,
    field_rules: Mapping[str, Polynomial],
    claimed_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compare every claimed row with the exact derivative support."""

    expected = linear_variation_coefficients(
        leibniz_derivative(primal, signature, field_rules), signature
    )
    if type(claimed_rows) is not list:
        raise FreeRingVerifierError("claimed rows must be a list")
    claimed: dict[str, Polynomial] = {}
    coefficient_alphabet = frozenset((*signature.parameters, *signature.fields))
    for ordinal, row in enumerate(claimed_rows):
        _require_keys(row, ("slot", "coefficient"), f"claimed row {ordinal}")
        slot = row["slot"]
        if type(slot) is not str or slot not in signature.variations:
            raise FreeRingVerifierError(f"claimed row {ordinal} has an unknown slot")
        if slot in claimed:
            raise FreeRingVerifierError(f"duplicate claimed variation slot {slot}")
        claimed[slot] = decode_polynomial_ast(row["coefficient"], coefficient_alphabet)

    support_exact = set(claimed) == set(expected)
    rows: dict[str, Any] = {}
    for slot in sorted(set(claimed) | set(expected)):
        residual = claimed.get(slot, Polynomial.zero()) - expected.get(
            slot, Polynomial.zero()
        )
        rows[slot] = {
            "claimed": claimed.get(slot, Polynomial.zero()).row(),
            "expected": expected.get(slot, Polynomial.zero()).row(),
            "residual": residual.row(),
            "residual_term_count": len(residual.terms),
            "pass": residual.is_zero and slot in claimed and slot in expected,
        }
    passed = support_exact and bool(rows) and all(row["pass"] for row in rows.values())
    return {
        "pass": passed,
        "support_exact": support_exact,
        "expected_slots": sorted(expected),
        "claimed_slots": sorted(claimed),
        "rows": rows,
    }


def _claims(coefficients: Mapping[str, Polynomial]) -> list[dict[str, Any]]:
    return [
        {"slot": slot, "coefficient": encode_polynomial_ast(coefficient)}
        for slot, coefficient in sorted(coefficients.items())
    ]


def _kernel_fixture() -> tuple[
    RingSignature, Polynomial, dict[str, Polynomial], dict[str, Polynomial]
]:
    signature = RingSignature(
        parameters=("M5", "u01"),
        fields=("x", "y"),
        variations=("v::x", "v::y"),
    )
    m5 = Polynomial.generator("M5")
    u01 = Polynomial.generator("u01")
    x = Polynomial.generator("x")
    y = Polynomial.generator("y")
    primal = m5.power(3) * x + u01 * y
    rules = {
        "x": Polynomial.generator("v::x"),
        "y": Polynomial.generator("v::y"),
    }
    expected = linear_variation_coefficients(
        leibniz_derivative(primal, signature, rules), signature
    )
    return signature, primal, rules, expected


def _finite_alias(variable: Polynomial, left: Fraction, right: Fraction) -> Polynomial:
    one = Polynomial.constant(1)
    return one + (variable + Polynomial.constant(-left)) * (
        variable + Polynomial.constant(-right)
    )


def _mutation_campaign() -> dict[str, Any]:
    signature, primal, rules, expected = _kernel_fixture()
    baseline = verify_claimed_coefficients(primal, signature, rules, _claims(expected))
    m5 = Polynomial.generator("M5")
    u01 = Polynomial.generator("u01")
    mutations = {
        "M1_M5_two_point_alias": {
            **expected,
            "v::x": expected["v::x"]
            * _finite_alias(m5, Fraction(2), Fraction(3)),
        },
        "M3_u01_two_point_alias": {
            **expected,
            "v::y": expected["v::y"]
            * _finite_alias(u01, Fraction(-1, 5), Fraction(22, 105)),
        },
        "M4_u01_one_point_alias": {
            **expected,
            "v::y": expected["v::y"] * u01.scale(-5),
        },
    }
    rows: dict[str, Any] = {}
    for name, coefficients in mutations.items():
        result = verify_claimed_coefficients(
            primal, signature, rules, _claims(coefficients)
        )
        rows[name] = {
            "killed": result["pass"] is False,
            "nonzero_residual_slots": sorted(
                slot
                for slot, row in result["rows"].items()
                if row["residual_term_count"] > 0
            ),
        }

    forbidden_symbol_killed = False
    bad = _claims(expected)
    bad[0]["coefficient"] = {
        "op": "mul",
        "args": [bad[0]["coefficient"], {"op": "symbol", "name": "g00"}],
    }
    try:
        verify_claimed_coefficients(primal, signature, rules, bad)
    except FreeRingVerifierError:
        forbidden_symbol_killed = True
    rows["M2_forbidden_trace_generator"] = {
        "killed": forbidden_symbol_killed,
        "nonzero_residual_slots": [],
    }
    return {
        "baseline_pass": baseline["pass"],
        "rows": rows,
        "pass": baseline["pass"] and all(row["killed"] for row in rows.values()),
        "finite_witnesses_used": False,
    }


def _integer_power_rule_certificate() -> dict[str, Any]:
    signature = RingSignature(
        parameters=(), fields=("x",), variations=("v::x",)
    )
    x = Polynomial.generator("x")
    vx = Polynomial.generator("v::x")
    rows: dict[str, Any] = {}
    for exponent in (0, 1, 2, 3, 5):
        observed = leibniz_derivative(
            x.power(exponent), signature, {"x": vx}
        )
        expected = (
            Polynomial.zero()
            if exponent == 0
            else x.power(exponent - 1) * vx.scale(exponent)
        )
        rows[str(exponent)] = {
            "observed": observed.row(),
            "expected": expected.row(),
            "pass": observed == expected,
        }
    return {
        "tested_exponents": [0, 1, 2, 3, 5],
        "rows": rows,
        "pass": all(row["pass"] for row in rows.values()),
    }


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _trusted_callable_inventory() -> dict[str, Any]:
    """Every local callable whose semantics can affect a READY verification."""

    return {
        "_exact_fraction": _exact_fraction,
        "_canonical_monomial": _canonical_monomial,
        "Polynomial.__init__": Polynomial.__init__,
        "Polynomial.__post_init__": Polynomial.__post_init__,
        "Polynomial.__eq__": Polynomial.__eq__,
        "Polynomial.from_terms": Polynomial.from_terms,
        "Polynomial.zero": Polynomial.zero,
        "Polynomial.constant": Polynomial.constant,
        "Polynomial.generator": Polynomial.generator,
        "Polynomial.__add__": Polynomial.__add__,
        "Polynomial.__neg__": Polynomial.__neg__,
        "Polynomial.__sub__": Polynomial.__sub__,
        "Polynomial.scale": Polynomial.scale,
        "Polynomial.__mul__": Polynomial.__mul__,
        "Polynomial.power": Polynomial.power,
        "Polynomial.symbols": Polynomial.symbols.fget,
        "Polynomial.is_zero": Polynomial.is_zero.fget,
        "Polynomial.row": Polynomial.row,
        "RingSignature.__init__": RingSignature.__init__,
        "RingSignature.__post_init__": RingSignature.__post_init__,
        "RingSignature.all_symbols": RingSignature.all_symbols.fget,
        "_assert_symbols": _assert_symbols,
        "_assert_rule_is_linear": _assert_rule_is_linear,
        "leibniz_derivative": leibniz_derivative,
        "linear_variation_coefficients": linear_variation_coefficients,
        "_require_keys": _require_keys,
        "decode_polynomial_ast": decode_polynomial_ast,
        "encode_polynomial_ast": encode_polynomial_ast,
        "verify_claimed_coefficients": verify_claimed_coefficients,
        "_claims": _claims,
        "_kernel_fixture": _kernel_fixture,
        "_finite_alias": _finite_alias,
        "_mutation_campaign": _mutation_campaign,
        "_integer_power_rule_certificate": _integer_power_rule_certificate,
        "_canonical_sha256": _canonical_sha256,
        "_callable_code_sha256": _callable_code_sha256,
        "_trusted_callable_inventory": _trusted_callable_inventory,
        "_trusted_kernel_code_certificate": _trusted_kernel_code_certificate,
        "build_report": build_report,
    }


def _trusted_kernel_code_certificate() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for name, function in _trusted_callable_inventory().items():
        try:
            digest = _callable_code_sha256(function)
            error = None
        except FreeRingVerifierError as exc:
            digest = None
            error = str(exc)
        generated_init = name in {"Polynomial.__init__", "RingSignature.__init__"}
        closure = function.__closure__
        closure_matches = (
            closure is not None
            and len(closure) == 1
            and closure[0].cell_contents is object
            if generated_init
            else closure is None
        )
        environment = {
            "uses_live_module_global_namespace": function.__globals__ is globals(),
            "module_name_matches": function.__module__ == __name__,
            "qualified_name_matches_inventory_key": function.__qualname__ == name,
            "positional_defaults_are_empty": function.__defaults__ is None,
            "keyword_defaults_are_empty": function.__kwdefaults__ is None,
            "closure_matches_closed_snapshot": closure_matches,
        }
        rows[name] = {
            "code_sha256": digest,
            "code_error": error,
            "environment": environment,
            "environment_pass": all(environment.values()),
        }
    manifest_sha256 = _canonical_sha256(rows)
    return {
        "rows": rows,
        "callable_count": len(rows),
        "manifest_sha256": manifest_sha256,
        "expected_manifest_sha256": EXPECTED_TCB_MANIFEST_SHA256,
        "pass": bool(
            manifest_sha256 == EXPECTED_TCB_MANIFEST_SHA256
            and all(row["environment_pass"] for row in rows.values())
        ),
    }


def build_report() -> dict[str, Any]:
    signature, primal, rules, expected = _kernel_fixture()
    baseline = verify_claimed_coefficients(primal, signature, rules, _claims(expected))
    mutations = _mutation_campaign()
    power_rule = _integer_power_rule_certificate()

    # Deliberately demonstrate the kernel's trust boundary: if both the primal
    # theory and its rows are changed coherently, algebraic differentiation
    # accepts them.  A committed, independently decoded source DAG must close
    # that boundary in a later consumer.
    changed_primal = primal + Polynomial.generator("x")
    changed_expected = linear_variation_coefficients(
        leibniz_derivative(changed_primal, signature, rules), signature
    )
    coherent_theory_change = verify_claimed_coefficients(
        changed_primal, signature, rules, _claims(changed_expected)
    )["pass"]
    live_leibniz_code_sha256 = _callable_code_sha256(leibniz_derivative)
    trusted_kernel_code_exact = (
        live_leibniz_code_sha256 == EXPECTED_LEIBNIZ_CODE_SHA256
    )
    trusted_kernel = _trusted_kernel_code_certificate()

    checks = {
        "local_callable_code_and_environment_snapshot_matches_audited_pin": trusted_kernel[
            "pass"
        ],
        "trusted_Leibniz_code_object_matches_audited_pin": trusted_kernel_code_exact,
        "canonical_sparse_Q_Sigma_arithmetic_exact": baseline["pass"],
        "integer_power_Leibniz_rule_exact_at_0_1_2_3_5": power_rule["pass"],
        "finite_alias_mutants_rejected_without_sampling": mutations["pass"],
        "report_records_coherent_theory_change_boundary": coherent_theory_change,
        "no_geometry_claim_promoted": True,
    }
    decision = {
        "free_ring_kernel_ready_pass": all(checks.values()),
        "EH_GHY_whole_summand_verified_pass": False,
        "K_a_Robin_whole_summand_verified_pass": False,
        "R_R_squared_whole_summand_verified_pass": False,
        "all_twenty_components_componentwise_variation_pass": False,
        "raw_Frechet_to_formal_adjoint_bridge_pass": False,
        "two_sided_full_Green_pairing_pass": False,
        "moving_embedding_shape_equation_pass": False,
        "uniform_N_to_infinity_bridge_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "publication_authorized": False,
        "runtime_self_attestation_against_arbitrary_co_mutation_pass": False,
    }
    report = {
        "schema": SCHEMA,
        "status": "KERNEL_READY" if all(checks.values()) else "NOT_READY",
        "checks": {**checks, "all": all(checks.values())},
        "ring": {
            "coefficient_field": "Q",
            "zero_criterion": "empty canonical sparse polynomial",
            "finite_witnesses_used": False,
            "signature": {
                "parameters": list(signature.parameters),
                "fields": list(signature.fields),
                "variations": list(signature.variations),
            },
        },
        "trusted_kernel": {
            "Leibniz_code_sha256": live_leibniz_code_sha256,
            "expected_Leibniz_code_sha256": EXPECTED_LEIBNIZ_CODE_SHA256,
            "code_object_pin_pass": trusted_kernel_code_exact,
            "audited_local_callable_manifest": trusted_kernel,
            "epistemic_boundary": (
                "this local snapshot detects callable substitutions while its certificate path "
                "and module namespace remain trusted; it cannot self-attest against arbitrary "
                "co-mutation of the verifier, so the root of trust is an external clean import "
                "from byte-pinned source; finite property tests are not a universal proof of Python"
            ),
        },
        "baseline": baseline,
        "integer_power_rule_certificate": power_rule,
        "mandatory_mutant_certificate": mutations,
        "trust_boundary": {
            "coherent_primal_and_row_theory_change_is_detected": False,
            "coherent_theory_change_fixture_passes_algebra": coherent_theory_change,
            "runtime_self_attestation_against_arbitrary_co_mutation": False,
            "closure_requires": (
                "independent byte-pinned source decoder plus explicit indexed "
                "geometry DAG committed outside candidate rows"
            ),
        },
        "evaluated_components": [],
        "not_evaluated_components": [
            "EH_bulk_plus",
            "GHY_plus",
            "EH_bulk_minus",
            "GHY_minus",
            "K_foliation",
            "R",
            "R_squared",
            "a_squared",
            "Robin",
        ],
        "decision": decision,
    }
    report["report_sha256_without_self"] = _canonical_sha256(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "KERNEL_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
