#!/usr/bin/env python3
"""Exact raw Frechet microgate for the v5.2 K, a, and Robin densities.

This gate is intentionally smaller than a variational-principle gate.  It
expands, on the fixed abstract interface ``Sigma``, the three literal action
occurrences

``Kcal_mn Kcal^mn-lambda_K Kcal^2``, ``eta a_m a^m``, and the intrinsic
Robin square.  The independent variables of this *displayed semantic
completion* are the coordinate jets of ``gamma``, ``T``, and the coordinate
components of ``varphi_H``.  No integration by parts is performed: the output
is raw ``D L[H,tau,v]`` and not an Euler operator or a post-adjoint current.

The coordinate meaning of ``varphi_H`` is deliberately narrow.  Its four
contravariant components are an independent slot in this fixed-domain
completion.  Preservation of horizontality, a moving frame, the two groupoid
maps, trace assembly, and moving embeddings remain open.  Consequently the
gate proves neither the full physical Robin variation nor C1/N1.

Two genuinely separate mechanisms are used:

* a canonical scalar AST and symbolic linear-form visitor export every raw
  Frechet coefficient;
* an independent exact dual-number oracle reconstructs inverse matrices by
  Gaussian elimination and evaluates the composite geometry directly.

The oracle checks every basis variation at two rational Lorentzian jet
witnesses.  Correlated mutations of the AST inverse, volume, and fractional
power rules therefore remain rejected even when all internal structural
hashes are treated as repinned.  The exact symbolic derivation is the proof
object; the dual oracle is an independent adversarial check, not a replacement
for it.

No artifact is written.  ``main`` only prints the deterministic report.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
SCHEMA = "holo.one-omega-topological-so3-k-a-robin-semantic-frechet-v5-6-7-13.v1"
ROW_SCHEMA = "holo.raw-frechet-row.v1"
NODE_SCHEMA = "holo.strict-scalar-expression-node.v1"
DIM = 4

S10_SOURCE = HERE / "derive_one_omega_topological_so3_eleven_component_semantic_frechet_v5_6_7_10_gate.py"
S10_TEST = HERE / "test_one_omega_topological_so3_eleven_component_semantic_frechet_v5_6_7_10_gate.py"
S9_SOURCE = HERE / "derive_one_omega_topological_so3_variational_ir_formal_adjoint_v5_6_7_9_gate.py"
S9_TEST = HERE / "test_one_omega_topological_so3_variational_ir_formal_adjoint_v5_6_7_9_gate.py"
S8_SOURCE = HERE / "derive_one_omega_topological_so3_moving_interface_variational_completion_v5_6_7_8_gate.py"
S8_TEST = HERE / "test_one_omega_topological_so3_moving_interface_variational_completion_v5_6_7_8_gate.py"

PINNED_INPUTS = {
    S10_SOURCE.name: "f16644c585479849d72151f243a694317c19f88aee1f2ce684e0121e20a41d33",
    S10_TEST.name: "a6d8a735c78771788e138e5f9e5e12c9453195ae01c5e921f6b0b333a697a599",
    S9_SOURCE.name: "50808c6488ccfaa1626bbf98312a126facd281b8aaa7b2c5be2d772712766815",
    S9_TEST.name: "00f2009c236f6e340a5766f209384ab07151cb3488973a457f9fbd191693a913",
    S8_SOURCE.name: "18eb511418017a86c05ba506d3c6dac7c13b10b39ebdad607d8143d9a2872acb",
    S8_TEST.name: "9e8fab34d1e8d877a0e2ab799bec9ea26e40a05f8c63d4a333d0ea8d2664b0a0",
}
PINNED_PATHS = {
    path.name: path
    for path in (S10_SOURCE, S10_TEST, S9_SOURCE, S9_TEST, S8_SOURCE, S8_TEST)
}
LINEAGE_COMMITS = {
    "S10_exact_eleven_rows": "e8f831ddb383598c9b74b1606c87674bbd476617",
    "S9_variational_IR_infrastructure": "774100b84eb3d7d4642ecd8320c75680f46edbba",
    "S8_corrected_intrinsic_Rcal": "85585849fa65411a33330ce3822e03c77b067ad7",
}

COMPONENTS = ("K_foliation", "a_squared", "Robin")
EXPECTED_ROW_COUNTS = {"K_foliation": 64, "a_squared": 64, "Robin": 68}
PARAMETERS = frozenset({"Mb", "lambda_K", "eta", "y", "kappa_hat"})
SLOTS = ("H", "tau", "v")


class KARRawFrechetError(RuntimeError):
    """A dependency, semantic, algebraic, schema, or oracle check failed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise KARRawFrechetError(f"cannot hash {path}: {exc}") from exc


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise KARRawFrechetError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True, eq=False)
class Expr:
    op: str
    args: tuple["Expr", ...] = ()
    data: tuple[Any, ...] = ()
    _digest: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        payload = {
            "op": self.op,
            "data": list(self.data),
            "args": [arg._digest.hex() for arg in self.args],
        }
        object.__setattr__(self, "_digest", hashlib.sha256(_canonical_bytes(payload)).digest())

    def __hash__(self) -> int:
        return int.from_bytes(self._digest[:8], "big", signed=False)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Expr)
            and self._digest == other._digest
            and self.op == other.op
            and self.data == other.data
            and tuple(arg._digest for arg in self.args) == tuple(arg._digest for arg in other.args)
        )

    def __add__(self, other: "Expr | int | Fraction") -> "Expr":
        return add(self, other if isinstance(other, Expr) else const(other))

    __radd__ = __add__

    def __neg__(self) -> "Expr":
        return mul(const(-1), self)

    def __sub__(self, other: "Expr | int | Fraction") -> "Expr":
        return add(self, -other if isinstance(other, Expr) else const(-other))

    def __rsub__(self, other: "Expr | int | Fraction") -> "Expr":
        return (other if isinstance(other, Expr) else const(other)) - self

    def __mul__(self, other: "Expr | int | Fraction") -> "Expr":
        return mul(self, other if isinstance(other, Expr) else const(other))

    __rmul__ = __mul__


ZERO = Expr("const", data=(0, 1))
ONE = Expr("const", data=(1, 1))


def const(value: int | Fraction) -> Expr:
    value = Fraction(value)
    if value == 0:
        return ZERO
    if value == 1:
        return ONE
    return Expr("const", data=(value.numerator, value.denominator))


def param(name: str) -> Expr:
    if name not in PARAMETERS:
        raise KARRawFrechetError(f"unknown parameter {name}")
    return Expr("param", data=(name,))


def _canonical_pair(i: int, j: int) -> tuple[int, int]:
    if not all(type(index) is int and 0 <= index < DIM for index in (i, j)):
        raise KARRawFrechetError("coordinate index outside dimension four")
    return (i, j) if i <= j else (j, i)


def gamma(i: int, j: int) -> Expr:
    return Expr("gamma", data=_canonical_pair(i, j))


def dgamma(k: int, i: int, j: int) -> Expr:
    i, j = _canonical_pair(i, j)
    if type(k) is not int or not 0 <= k < DIM:
        raise KARRawFrechetError("derivative index outside dimension four")
    return Expr("dgamma", data=(k, i, j))


def t1(i: int) -> Expr:
    if type(i) is not int or not 0 <= i < DIM:
        raise KARRawFrechetError("T first-jet index outside dimension four")
    return Expr("T1", data=(i,))


def t2(i: int, j: int) -> Expr:
    return Expr("T2", data=_canonical_pair(i, j))


def varphi(i: int) -> Expr:
    if type(i) is not int or not 0 <= i < DIM:
        raise KARRawFrechetError("varphi index outside dimension four")
    return Expr("varphi", data=(i,))


def ginv(i: int, j: int) -> Expr:
    return Expr("ginv", data=_canonical_pair(i, j))


VOLUME = Expr("volume")


def _expr_sort_key(expr: Expr) -> bytes:
    return expr._digest


def _constant_factor(expr: Expr) -> tuple[Fraction, Expr]:
    if expr.op == "const":
        return Fraction(expr.data[0], expr.data[1]), ONE
    if expr.op == "mul" and expr.args and expr.args[0].op == "const":
        coefficient = Fraction(expr.args[0].data[0], expr.args[0].data[1])
        tail = mul(*expr.args[1:])
        return coefficient, tail
    return Fraction(1), expr


def add(*items: Expr) -> Expr:
    flat: list[Expr] = []
    for item in items:
        if item == ZERO:
            continue
        flat.extend(item.args if item.op == "add" else (item,))
    coefficients: dict[Expr, Fraction] = {}
    for item in flat:
        coefficient, core = _constant_factor(item)
        coefficients[core] = coefficients.get(core, Fraction(0)) + coefficient
    normalized: list[Expr] = []
    for core, coefficient in coefficients.items():
        if coefficient == 0:
            continue
        normalized.append(const(coefficient) if core == ONE else mul(const(coefficient), core))
    if not normalized:
        return ZERO
    normalized.sort(key=_expr_sort_key)
    if len(normalized) == 1:
        return normalized[0]
    return Expr("add", tuple(normalized))


def mul(*items: Expr) -> Expr:
    flat: list[Expr] = []
    coefficient = Fraction(1)
    for item in items:
        if item == ZERO:
            return ZERO
        children = item.args if item.op == "mul" else (item,)
        for child in children:
            if child.op == "const":
                coefficient *= Fraction(child.data[0], child.data[1])
            else:
                flat.append(child)
    if coefficient == 0:
        return ZERO
    flat.sort(key=_expr_sort_key)
    if not flat:
        return const(coefficient)
    if coefficient != 1:
        flat.insert(0, const(coefficient))
    if len(flat) == 1:
        return flat[0]
    return Expr("mul", tuple(flat))


def power(base: Expr, exponent: int | Fraction) -> Expr:
    exponent = Fraction(exponent)
    if exponent == 0:
        return ONE
    if exponent == 1:
        return base
    if base == ONE:
        return ONE
    return Expr("pow", (base,), (exponent.numerator, exponent.denominator))


def summation(items: Iterable[Expr]) -> Expr:
    return add(*tuple(items))


def _expr_tree(expr: Expr) -> dict[str, Any]:
    row: dict[str, Any] = {"op": expr.op}
    if expr.args:
        row["args"] = [_expr_tree(arg) for arg in expr.args]
    if expr.data:
        row["data"] = list(expr.data)
    return row


VariationKey = tuple[str, tuple[int, ...], tuple[int, ...]]
LinearForm = dict[VariationKey, Expr]


def _variation_key(slot: str, word: Sequence[int], indices: Sequence[int]) -> VariationKey:
    if slot not in SLOTS:
        raise KARRawFrechetError(f"unknown variation slot {slot}")
    return slot, tuple(word), tuple(indices)


def _lf_add(*forms: Mapping[VariationKey, Expr]) -> LinearForm:
    keys = set().union(*(form.keys() for form in forms)) if forms else set()
    return {
        key: coefficient
        for key in sorted(keys)
        if (coefficient := add(*(form.get(key, ZERO) for form in forms))) != ZERO
    }


def _lf_scale(factor: Expr, form: Mapping[VariationKey, Expr]) -> LinearForm:
    if factor == ZERO:
        return {}
    return {
        key: coefficient
        for key, value in form.items()
        if (coefficient := mul(factor, value)) != ZERO
    }


def _inverse_variation(i: int, j: int, mutation: str | None) -> LinearForm:
    sign = 1 if mutation == "correlated_wrong_inverse_sign" else -1
    forms: list[LinearForm] = []
    for a in range(DIM):
        for b in range(DIM):
            key = _variation_key("H", (), _canonical_pair(a, b))
            forms.append({key: mul(const(sign), ginv(i, a), ginv(b, j))})
    return _lf_add(*forms)


def _volume_variation(mutation: str | None) -> LinearForm:
    half = Fraction(1) if mutation == "correlated_wrong_volume_half" else Fraction(1, 2)
    forms: list[LinearForm] = []
    for a in range(DIM):
        for b in range(DIM):
            key = _variation_key("H", (), _canonical_pair(a, b))
            forms.append({key: mul(const(half), VOLUME, ginv(a, b))})
    return _lf_add(*forms)


@lru_cache(maxsize=None)
def frechet(expr: Expr, mutation: str | None = None) -> LinearForm:
    if expr.op in {"const", "param"}:
        return {}
    if expr.op == "gamma":
        return {_variation_key("H", (), expr.data): ONE}
    if expr.op == "dgamma":
        return {_variation_key("H", (expr.data[0],), expr.data[1:]): ONE}
    if expr.op == "T1":
        return {_variation_key("tau", expr.data, ()): ONE}
    if expr.op == "T2":
        return {_variation_key("tau", expr.data, ()): ONE}
    if expr.op == "varphi":
        return {_variation_key("v", (), expr.data): ONE}
    if expr.op == "ginv":
        return _inverse_variation(expr.data[0], expr.data[1], mutation)
    if expr.op == "volume":
        return _volume_variation(mutation)
    if expr.op == "add":
        return _lf_add(*(frechet(arg, mutation) for arg in expr.args))
    if expr.op == "mul":
        terms: list[LinearForm] = []
        for position, arg in enumerate(expr.args):
            other = mul(*(expr.args[:position] + expr.args[position + 1 :]))
            terms.append(_lf_scale(other, frechet(arg, mutation)))
        return _lf_add(*terms)
    if expr.op == "pow":
        exponent = Fraction(expr.data[0], expr.data[1])
        derivative_exponent = exponent
        if mutation == "correlated_wrong_fractional_power_sign" and exponent.denominator == 2:
            derivative_exponent = -exponent
        return _lf_scale(
            mul(const(derivative_exponent), power(expr.args[0], exponent - 1)),
            frechet(expr.args[0], mutation),
        )
    raise KARRawFrechetError(f"no Frechet rule for opcode {expr.op}")


@lru_cache(maxsize=None)
def reverse_context_frechet(expr: Expr) -> LinearForm:
    """Exact symbolic context traversal independent of ``frechet``/exporters.

    Each node is interpreted into a fresh ``(primal, tangent-context)`` pair.
    The implementation has its own form addition/scaling and local rules; the
    only shared layer is the canonical Expr algebra in which equality is
    decided.  This avoids the exponential path expansion of a naive reverse
    walk while retaining a genuinely separate traversal.
    """

    cache: dict[Expr, tuple[Expr, LinearForm]] = {}

    def form_add(*forms: Mapping[VariationKey, Expr]) -> LinearForm:
        keys: set[VariationKey] = set()
        for form in forms:
            keys.update(form)
        result: LinearForm = {}
        for key in sorted(keys):
            coefficient = add(*(form[key] for form in forms if key in form))
            if coefficient != ZERO:
                result[key] = coefficient
        return result

    def form_scale(factor: Expr, form: Mapping[VariationKey, Expr]) -> LinearForm:
        result: LinearForm = {}
        for key in sorted(form):
            coefficient = mul(factor, form[key])
            if coefficient != ZERO:
                result[key] = coefficient
        return result

    def interpret(node: Expr) -> tuple[Expr, LinearForm]:
        if node in cache:
            return cache[node]
        if node.op in {"const", "param"}:
            result = (node, {})
        elif node.op == "gamma":
            result = (node, {("H", (), tuple(node.data)): ONE})
        elif node.op == "dgamma":
            result = (
                node,
                {("H", (node.data[0],), tuple(node.data[1:])): ONE},
            )
        elif node.op == "T1":
            result = (node, {("tau", tuple(node.data), ()): ONE})
        elif node.op == "T2":
            result = (node, {("tau", tuple(node.data), ()): ONE})
        elif node.op == "varphi":
            result = (node, {("v", (), tuple(node.data)): ONE})
        elif node.op == "ginv":
            i, j = node.data
            pieces: list[LinearForm] = []
            for a in range(DIM):
                for b in range(DIM):
                    pieces.append(
                        {
                            ("H", (), _canonical_pair(a, b)): mul(
                                const(-1), ginv(i, a), ginv(b, j)
                            )
                        }
                    )
            result = (node, form_add(*pieces))
        elif node.op == "volume":
            pieces = []
            for a in range(DIM):
                for b in range(DIM):
                    pieces.append(
                        {
                            ("H", (), _canonical_pair(a, b)): mul(
                                const(Fraction(1, 2)), VOLUME, ginv(a, b)
                            )
                        }
                    )
            result = (node, form_add(*pieces))
        elif node.op == "add":
            children = [interpret(child) for child in node.args]
            result = (
                add(*(primal for primal, _ in children)),
                form_add(*(tangent for _, tangent in children)),
            )
        elif node.op == "mul":
            children = [interpret(child) for child in node.args]
            primals = tuple(primal for primal, _ in children)
            tangent_terms = [
                form_scale(
                    mul(*(primals[:position] + primals[position + 1 :])),
                    tangent,
                )
                for position, (_, tangent) in enumerate(children)
            ]
            result = (mul(*primals), form_add(*tangent_terms))
        elif node.op == "pow":
            base, tangent = interpret(node.args[0])
            exponent = Fraction(node.data[0], node.data[1])
            result = (
                power(base, exponent),
                form_scale(
                    mul(const(exponent), power(base, exponent - 1)), tangent
                ),
            )
        else:
            raise KARRawFrechetError(
                f"context traversal has no local rule for opcode {node.op}"
            )
        if result[0] != node:
            raise KARRawFrechetError(
                f"context traversal failed primal reconstruction at {node.op}"
            )
        cache[node] = result
        return result

    return interpret(expr)[1]


def _linear_forms_exact(
    left: Mapping[VariationKey, Expr], right: Mapping[VariationKey, Expr]
) -> bool:
    return set(left) == set(right) and all(left[key] == right[key] for key in left)


@lru_cache(maxsize=None)
def coordinate_partial(expr: Expr, k: int) -> Expr:
    if expr.op in {"const", "param"}:
        return ZERO
    if expr.op == "gamma":
        return dgamma(k, expr.data[0], expr.data[1])
    if expr.op == "T1":
        return t2(k, expr.data[0])
    if expr.op == "ginv":
        i, j = expr.data
        return summation(
            mul(const(-1), ginv(i, a), dgamma(k, a, b), ginv(b, j))
            for a in range(DIM)
            for b in range(DIM)
        )
    if expr.op == "add":
        return add(*(coordinate_partial(arg, k) for arg in expr.args))
    if expr.op == "mul":
        return add(
            *(
                mul(
                    coordinate_partial(arg, k),
                    *(expr.args[:position] + expr.args[position + 1 :]),
                )
                for position, arg in enumerate(expr.args)
            )
        )
    if expr.op == "pow":
        exponent = Fraction(expr.data[0], expr.data[1])
        return mul(
            const(exponent),
            power(expr.args[0], exponent - 1),
            coordinate_partial(expr.args[0], k),
        )
    raise KARRawFrechetError(f"coordinate partial unsupported for {expr.op}")


@lru_cache(maxsize=None)
def context_coordinate_partial(expr: Expr, k: int) -> Expr:
    """Independent context traversal for the coordinate-jet derivation.

    This deliberately does not call ``coordinate_partial``.  It is used only
    by the independently constructed literal program and supplies a second
    implementation of every local rule needed by the K/a/Robin densities.
    """

    if type(k) is not int or not 0 <= k < DIM:
        raise KARRawFrechetError("context derivative index outside dimension four")
    if expr.op in {"const", "param"}:
        return ZERO
    if expr.op == "gamma":
        return dgamma(k, expr.data[0], expr.data[1])
    if expr.op == "T1":
        return t2(k, expr.data[0])
    if expr.op == "ginv":
        i, j = expr.data
        return summation(
            mul(const(-1), ginv(i, a), dgamma(k, a, b), ginv(b, j))
            for a in range(DIM)
            for b in range(DIM)
        )
    if expr.op == "add":
        return add(*(context_coordinate_partial(arg, k) for arg in expr.args))
    if expr.op == "mul":
        return add(
            *(
                mul(
                    context_coordinate_partial(arg, k),
                    *(expr.args[:position] + expr.args[position + 1 :]),
                )
                for position, arg in enumerate(expr.args)
            )
        )
    if expr.op == "pow":
        exponent = Fraction(expr.data[0], expr.data[1])
        return mul(
            const(exponent),
            power(expr.args[0], exponent - 1),
            context_coordinate_partial(expr.args[0], k),
        )
    raise KARRawFrechetError(
        f"context coordinate partial unsupported for {expr.op}"
    )


@dataclass(frozen=True)
class ComponentProgram:
    components: Mapping[str, Expr]
    source_spans: Mapping[str, Mapping[str, Any]]
    convention: str


def _christoffel(last_sign: int = -1) -> list[list[list[Expr]]]:
    return [
        [
            [
                mul(
                    const(Fraction(1, 2)),
                    summation(
                        mul(
                            ginv(l, q),
                            add(
                                dgamma(r, q, s),
                                dgamma(s, q, r),
                                mul(const(last_sign), dgamma(q, r, s)),
                            ),
                        )
                        for q in range(DIM)
                    ),
                )
                for s in range(DIM)
            ]
            for r in range(DIM)
        ]
        for l in range(DIM)
    ]


def build_component_program(
    action: Mapping[str, str], *, mutation: str | None = None, u_sign: int = -1
) -> ComponentProgram:
    if u_sign not in {-1, 1}:
        raise KARRawFrechetError("u orientation sign must be plus or minus one")
    foliation = action["foliation_lower"]
    robin_literal = action["Robin_intrinsic"]
    k_fragment = "Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2"
    a_fragment = "eta*a_mu*a^mu"
    robin_fragment = "h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)"
    for literal, fragment in (
        (foliation, k_fragment),
        (foliation, a_fragment),
        (robin_literal, robin_fragment),
    ):
        if literal.count(fragment) != 1:
            raise KARRawFrechetError(f"literal fragment missing or duplicated: {fragment}")

    last_sign = 1 if mutation == "wrong_christoffel_last_sign" else -1
    connection = _christoffel(last_sign)
    norm = mul(
        const(-1),
        summation(ginv(i, j) * t1(i) * t1(j) for i in range(DIM) for j in range(DIM)),
    )
    lapse = power(norm, Fraction(-1, 2))
    dlapse = [coordinate_partial(lapse, k) for k in range(DIM)]
    u_cov = [mul(const(u_sign), lapse, t1(i)) for i in range(DIM)]
    du_cov = [
        [
            mul(const(u_sign), add(mul(dlapse[k], t1(i)), mul(lapse, t2(k, i))))
            for i in range(DIM)
        ]
        for k in range(DIM)
    ]
    u_contra = [summation(ginv(i, j) * u_cov[j] for j in range(DIM)) for i in range(DIM)]
    h_cov = [
        [add(gamma(i, j), mul(u_cov[i], u_cov[j])) for j in range(DIM)]
        for i in range(DIM)
    ]
    h_contra = [
        [add(ginv(i, j), mul(u_contra[i], u_contra[j])) for j in range(DIM)]
        for i in range(DIM)
    ]
    h_mixed = [
        [add(const(1 if i == r else 0), mul(u_cov[i], u_contra[r])) for r in range(DIM)]
        for i in range(DIM)
    ]
    nabla_u = [
        [
            add(
                du_cov[r][s],
                mul(
                    const(-1),
                    summation(connection[l][r][s] * u_cov[l] for l in range(DIM)),
                ),
            )
            for s in range(DIM)
        ]
        for r in range(DIM)
    ]
    k_tensor = [
        [
            summation(
                h_mixed[i][r] * h_mixed[j][s] * nabla_u[r][s]
                for r in range(DIM)
                for s in range(DIM)
            )
            for j in range(DIM)
        ]
        for i in range(DIM)
    ]
    k_trace = summation(
        h_contra[i][j] * k_tensor[i][j]
        for i in range(DIM)
        for j in range(DIM)
    )
    k_tensor_squared = summation(
        h_contra[i][r]
        * h_contra[j][s]
        * k_tensor[i][j]
        * k_tensor[r][s]
        for i in range(DIM)
        for j in range(DIM)
        for r in range(DIM)
        for s in range(DIM)
    )
    lambda_sign = 1 if mutation == "wrong_K_lambda_sign" else -1
    k_density = mul(
        const(Fraction(1, 2)),
        power(param("Mb"), 2),
        VOLUME,
        add(k_tensor_squared, mul(const(lambda_sign), param("lambda_K"), k_trace, k_trace)),
    )
    if mutation == "correlated_hidden_offdiagonal_term":
        # Adversarial term invisible on diagonal-metric witnesses.  It is not
        # multiplied by the literal density prefactor on purpose: any such
        # hidden summand must be rejected, not normalized into the action.
        k_density = add(k_density, mul(gamma(0, 1), gamma(0, 1)))
    if mutation == "orientation_odd_hidden_term" and u_sign == 1:
        k_density = add(k_density, ONE)
    if mutation == "orientation_odd_double_zero" and u_sign == 1:
        witness_zero = mul(
            add(gamma(0, 1), const(Fraction(1, 5))),
            add(gamma(0, 1), const(Fraction(-22, 105))),
        )
        k_density = add(k_density, power(witness_zero, 2))

    a_cov = [
        summation(u_contra[n] * nabla_u[n][m] for n in range(DIM))
        for m in range(DIM)
    ]
    a_contra = [summation(ginv(m, n) * a_cov[n] for n in range(DIM)) for m in range(DIM)]
    a_squared = summation(
        ginv(m, n) * a_cov[m] * a_cov[n]
        for m in range(DIM)
        for n in range(DIM)
    )
    a_half = Fraction(1) if mutation == "wrong_a_prefactor_half" else Fraction(1, 2)
    a_density = mul(
        const(a_half), power(param("Mb"), 2), param("eta"), VOLUME, a_squared
    )

    robin_cross = 1 if mutation == "wrong_Robin_cross_sign" else -1
    q_vector = [
        add(
            ZERO if mutation == "omit_Robin_varphi" else varphi(m),
            mul(const(robin_cross), param("y"), a_contra[m]),
        )
        for m in range(DIM)
    ]
    robin_norm = summation(
        h_cov[m][n] * q_vector[m] * q_vector[n]
        for m in range(DIM)
        for n in range(DIM)
    )
    robin_prefactor = Fraction(1, 2) if mutation == "wrong_Robin_prefactor_sign" else Fraction(-1, 2)
    robin_density = mul(const(robin_prefactor), param("kappa_hat"), VOLUME, robin_norm)

    def span(action_key: str, literal: str, fragment: str) -> dict[str, Any]:
        start = literal.index(fragment)
        return {
            "action_key": action_key,
            "start": start,
            "end": start + len(fragment),
            "text": fragment,
        }

    return ComponentProgram(
        components={
            "K_foliation": k_density,
            "a_squared": a_density,
            "Robin": robin_density,
        },
        source_spans={
            "K_foliation": span("foliation_lower", foliation, k_fragment),
            "a_squared": span("foliation_lower", foliation, a_fragment),
            "Robin": span("Robin_intrinsic", robin_literal, robin_fragment),
        },
        convention="u_m=-N_T partial_m T" if u_sign == -1 else "u_m=+N_T partial_m T",
    )


@lru_cache(maxsize=None)
def _independent_literal_component_program_cached(
    foliation: str,
    robin_literal: str,
    u_sign: int,
) -> ComponentProgram:
    """Second construction of the three literal roots.

    It shares only the canonical Expr language with the producer.  It does
    not call ``build_component_program``, ``_christoffel``,
    ``coordinate_partial``, ``frechet``, or either exporter.
    """

    if u_sign not in {-1, 1}:
        raise KARRawFrechetError("independent u orientation must be plus or minus one")
    fragments = {
        "K_foliation": "Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2",
        "a_squared": "eta*a_mu*a^mu",
        "Robin": "h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)",
    }
    literal_by_component = {
        "K_foliation": foliation,
        "a_squared": foliation,
        "Robin": robin_literal,
    }
    for name in COMPONENTS:
        if literal_by_component[name].count(fragments[name]) != 1:
            raise KARRawFrechetError(
                f"independent literal binding is not unique for {name}"
            )

    connection = [
        [
            [
                mul(
                    const(Fraction(1, 2)),
                    summation(
                        ginv(l, q)
                        * add(
                            dgamma(r, q, s),
                            dgamma(s, q, r),
                            mul(const(-1), dgamma(q, r, s)),
                        )
                        for q in range(DIM)
                    ),
                )
                for s in range(DIM)
            ]
            for r in range(DIM)
        ]
        for l in range(DIM)
    ]
    norm = mul(
        const(-1),
        summation(
            ginv(i, j) * t1(i) * t1(j)
            for i in range(DIM)
            for j in range(DIM)
        ),
    )
    lapse = power(norm, Fraction(-1, 2))
    lapse_first = [context_coordinate_partial(lapse, k) for k in range(DIM)]
    u_cov = [const(u_sign) * lapse * t1(i) for i in range(DIM)]
    u_first = [
        [
            const(u_sign)
            * add(lapse_first[k] * t1(i), lapse * t2(k, i))
            for i in range(DIM)
        ]
        for k in range(DIM)
    ]
    u_contra = [
        summation(ginv(i, j) * u_cov[j] for j in range(DIM))
        for i in range(DIM)
    ]
    h_cov = [
        [gamma(i, j) + u_cov[i] * u_cov[j] for j in range(DIM)]
        for i in range(DIM)
    ]
    h_contra = [
        [ginv(i, j) + u_contra[i] * u_contra[j] for j in range(DIM)]
        for i in range(DIM)
    ]
    h_mixed = [
        [
            const(1 if i == r else 0) + u_cov[i] * u_contra[r]
            for r in range(DIM)
        ]
        for i in range(DIM)
    ]
    nabla_u = [
        [
            u_first[r][s]
            - summation(connection[l][r][s] * u_cov[l] for l in range(DIM))
            for s in range(DIM)
        ]
        for r in range(DIM)
    ]
    k_tensor = [
        [
            summation(
                h_mixed[i][r] * h_mixed[j][s] * nabla_u[r][s]
                for r in range(DIM)
                for s in range(DIM)
            )
            for j in range(DIM)
        ]
        for i in range(DIM)
    ]
    k_trace = summation(
        h_contra[i][j] * k_tensor[i][j]
        for i in range(DIM)
        for j in range(DIM)
    )
    k_tensor_squared = summation(
        h_contra[i][r]
        * h_contra[j][s]
        * k_tensor[i][j]
        * k_tensor[r][s]
        for i in range(DIM)
        for j in range(DIM)
        for r in range(DIM)
        for s in range(DIM)
    )
    k_density = (
        const(Fraction(1, 2))
        * power(param("Mb"), 2)
        * VOLUME
        * (k_tensor_squared - param("lambda_K") * k_trace * k_trace)
    )

    a_cov = [
        summation(u_contra[n] * nabla_u[n][m] for n in range(DIM))
        for m in range(DIM)
    ]
    a_contra = [
        summation(ginv(m, n) * a_cov[n] for n in range(DIM))
        for m in range(DIM)
    ]
    a_squared = summation(
        ginv(m, n) * a_cov[m] * a_cov[n]
        for m in range(DIM)
        for n in range(DIM)
    )
    a_density = (
        const(Fraction(1, 2))
        * power(param("Mb"), 2)
        * param("eta")
        * VOLUME
        * a_squared
    )

    q_vector = [varphi(m) - param("y") * a_contra[m] for m in range(DIM)]
    robin_norm = summation(
        h_cov[m][n] * q_vector[m] * q_vector[n]
        for m in range(DIM)
        for n in range(DIM)
    )
    robin_density = (
        const(Fraction(-1, 2)) * param("kappa_hat") * VOLUME * robin_norm
    )

    spans: dict[str, dict[str, Any]] = {}
    action_keys = {
        "K_foliation": "foliation_lower",
        "a_squared": "foliation_lower",
        "Robin": "Robin_intrinsic",
    }
    for name in COMPONENTS:
        literal = literal_by_component[name]
        fragment = fragments[name]
        start = literal.find(fragment)
        spans[name] = {
            "action_key": action_keys[name],
            "start": start,
            "end": start + len(fragment),
            "text": fragment,
        }
    return ComponentProgram(
        components={
            "K_foliation": k_density,
            "a_squared": a_density,
            "Robin": robin_density,
        },
        source_spans=spans,
        convention=(
            "u_m=-N_T partial_m T"
            if u_sign == -1
            else "u_m=+N_T partial_m T"
        ),
    )


def independent_literal_component_program(
    action: Mapping[str, str], *, u_sign: int = -1
) -> ComponentProgram:
    if set(action) < {"foliation_lower", "Robin_intrinsic"}:
        raise KARRawFrechetError("independent literal action inventory drift")
    return _independent_literal_component_program_cached(
        str(action["foliation_lower"]), str(action["Robin_intrinsic"]), u_sign
    )


def _expr_parameter_inventory(expr: Expr) -> list[str]:
    names: set[str] = set()
    seen: set[Expr] = set()
    stack = [expr]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        if node.op == "param":
            names.add(str(node.data[0]))
        stack.extend(node.args)
    return sorted(names)


def _local_calculus_rule_certificate(
    primary_mutation: str | None,
) -> dict[str, Any]:
    def hand_form_sum(forms: Sequence[Mapping[VariationKey, Expr]]) -> LinearForm:
        """Combine hand-written fixtures without calling the primary LF helper."""

        keys: set[VariationKey] = set()
        for form in forms:
            keys.update(form)
        combined: LinearForm = {}
        for key in sorted(keys):
            coefficient = add(*(form.get(key, ZERO) for form in forms))
            if coefficient != ZERO:
                combined[key] = coefficient
        return combined

    inverse_pieces: list[LinearForm] = []
    for a in range(DIM):
        for b in range(DIM):
            inverse_pieces.append(
                {
                    ("H", (), _canonical_pair(a, b)): mul(
                        const(-1), ginv(0, a), ginv(b, 1)
                    )
                }
            )
    inverse_expected = hand_form_sum(inverse_pieces)
    volume_expected = hand_form_sum(
        [
            {
                ("H", (), _canonical_pair(a, b)): mul(
                    const(Fraction(1, 2)), VOLUME, ginv(a, b)
                )
            }
            for a in range(DIM)
            for b in range(DIM)
        ]
    )
    product = gamma(0, 2) * t1(3)
    powered = power(gamma(1, 1), Fraction(-3, 2))
    fixtures: dict[str, tuple[Expr, LinearForm]] = {
        "constant": (const(Fraction(7, 11)), {}),
        "parameter": (param("Mb"), {}),
        "metric_leaf": (gamma(0, 2), {("H", (), (0, 2)): ONE}),
        "metric_first_jet": (
            dgamma(3, 0, 2),
            {("H", (3,), (0, 2)): ONE},
        ),
        "clock_first_jet": (t1(3), {("tau", (3,), ()): ONE}),
        "clock_second_jet": (t2(1, 3), {("tau", (1, 3), ()): ONE}),
        "varphi_leaf": (varphi(2), {("v", (), (2,)): ONE}),
        "inverse_metric": (ginv(0, 1), inverse_expected),
        "volume": (VOLUME, volume_expected),
        "product": (
            product,
            {
                ("H", (), (0, 2)): t1(3),
                ("tau", (3,), ()): gamma(0, 2),
            },
        ),
        "fractional_power": (
            powered,
            {
                ("H", (), (1, 1)): mul(
                    const(Fraction(-3, 2)),
                    power(gamma(1, 1), Fraction(-5, 2)),
                )
            },
        ),
    }
    rows: dict[str, Any] = {}
    for name, (expression, expected) in fixtures.items():
        primary = frechet(expression, primary_mutation)
        context = reverse_context_frechet(expression)
        rows[name] = {
            "primary_matches_hand_rule": _linear_forms_exact(primary, expected),
            "context_matches_hand_rule": _linear_forms_exact(context, expected),
            "routes_equal": _linear_forms_exact(primary, context),
        }
    coordinate_fixtures = {
        "metric": gamma(1, 3),
        "clock": t1(2),
        "inverse": ginv(0, 2),
        "product": gamma(0, 3) * t1(1),
        "power": power(gamma(2, 2), Fraction(-1, 2)),
    }
    coordinate_rows = {
        name: coordinate_partial(expression, 2)
        == context_coordinate_partial(expression, 2)
        for name, expression in coordinate_fixtures.items()
    }
    return {
        "route": (
            "hand-written leaf/product/power rules plus an independent "
            "memoized symbolic context interpreter"
        ),
        "rows": rows,
        "coordinate_partial_rows": coordinate_rows,
        "pass": all(
            all(row.values()) for row in rows.values()
        )
        and all(coordinate_rows.values()),
    }


def _exact_symbolic_semantic_certificate(
    action: Mapping[str, str],
    program: ComponentProgram,
    primary_forms: Mapping[str, Mapping[VariationKey, Expr]],
    *,
    primary_mutation: str | None,
) -> tuple[dict[str, Any], ComponentProgram, dict[str, LinearForm]]:
    expected_program = independent_literal_component_program(action)
    expected_forms = {
        name: reverse_context_frechet(expected_program.components[name])
        for name in COMPONENTS
    }
    observed_context_forms = {
        name: reverse_context_frechet(program.components[name])
        for name in COMPONENTS
    }
    expected_parameters = {
        "K_foliation": ["Mb", "lambda_K"],
        "a_squared": ["Mb", "eta"],
        "Robin": ["kappa_hat", "y"],
    }
    component_rows: dict[str, Any] = {}
    for name in COMPONENTS:
        primary = primary_forms[name]
        context = observed_context_forms[name]
        expected = expected_forms[name]
        component_rows[name] = {
            "literal_component_root_exact": (
                program.components[name] == expected_program.components[name]
            ),
            "literal_source_span_exact": (
                program.source_spans[name] == expected_program.source_spans[name]
            ),
            "parameter_inventory_exact": (
                _expr_parameter_inventory(program.components[name])
                == expected_parameters[name]
            ),
            "variation_key_inventory_exact": (
                set(primary) == set(context) == set(expected)
            ),
            "primary_form_equals_observed_context_form": _linear_forms_exact(
                primary, context
            ),
            "primary_form_equals_independent_literal_form": _linear_forms_exact(
                primary, expected
            ),
            "observed_context_form_equals_independent_literal_form": (
                _linear_forms_exact(context, expected)
            ),
            "coefficient_count": len(expected),
            "primary_root_expr_sha256": program.components[name]._digest.hex(),
            "independent_literal_root_expr_sha256": expected_program.components[
                name
            ]._digest.hex(),
        }
        component_rows[name]["pass"] = all(
            value
            for key, value in component_rows[name].items()
            if key
            not in {
                "coefficient_count",
                "primary_root_expr_sha256",
                "independent_literal_root_expr_sha256",
                "pass",
            }
        )
    local_rules = _local_calculus_rule_certificate(primary_mutation)
    all_components = all(row["pass"] for row in component_rows.values())
    return (
        {
            "route": (
                "exact full Expr and coefficient-map equality against an "
                "independently constructed literal program and symbolic "
                "context derivative"
            ),
            "epistemic_scope": (
                "universal identity inside the displayed finite formal Expr "
                "algebra; it is not inferred from numerical witnesses"
            ),
            "component_rows": component_rows,
            "local_calculus_rules": local_rules,
            "component_roots_bound_to_literal_program": all(
                row["literal_component_root_exact"]
                and row["literal_source_span_exact"]
                and row["parameter_inventory_exact"]
                for row in component_rows.values()
            ),
            "all_component_variation_keys_and_coefficients_exact": all_components,
            "pass": all_components and local_rules["pass"],
        },
        expected_program,
        expected_forms,
    )


SEMANTIC_COMPLETION = {
    "version": "v5.6.7.13-fixed-domain-K-a-Robin-coordinate-completion-v1",
    "stage": "raw_Frechet_before_formal_adjoint",
    "dimension": 4,
    "signature": "Lorentzian (-+++); all checks require -gamma^mn T_m T_n > 0",
    "independent_coordinate_jets": {
        "gamma_mn": "symmetric covariant metric through first jets",
        "T": "scalar through second jets; the densities have no undifferentiated T",
        "varphi_H^m": "independent contravariant coordinate components at order zero",
    },
    "composites": {
        "N_T": "(-gamma^mn partial_m T partial_n T)^(-1/2)",
        "u_m": "-N_T partial_m T",
        "h_mn": "gamma_mn+u_m u_n",
        "h_m^n": "delta_m^n+u_m u^n",
        "h^mn": "gamma^mn+u^m u^n",
        "Gamma^l_rs": "gamma^lq(partial_r gamma_qs+partial_s gamma_qr-partial_q gamma_rs)/2",
        "Kcal_mn": "h_m^r h_n^s (partial_r u_s-Gamma^l_rs u_l)",
        "Kcal": "h^mn Kcal_mn",
        "a_m": "u^n(partial_n u_m-Gamma^l_nm u_l)",
        "a^m": "gamma^mn a_n",
    },
    "literal_density_prefactors": {
        "K_foliation": "Mb^2/2",
        "a_squared": "Mb^2*eta/2",
        "Robin": "-kappa_hat/2",
    },
    "index_and_orientation_scope": {
        "coordinate_indices": [0, 1, 2, 3],
        "metric_and_second_scalar_jets": "canonical symmetric component indices",
        "time_orientation": "u_m=-N_T partial_m T",
        "quadratic_orientation_fact": "u -> -u sends Kcal -> -Kcal and leaves all three displayed densities invariant",
    },
    "excluded": [
        "formal adjoint and integration by parts",
        "Euler coefficients and currents",
        "horizontal-preserving variation of varphi_H",
        "frame and SO3 groupoid variation",
        "bulk trace and moving-interface assembly",
        "shape derivative",
    ],
}

EXPECTED_SEMANTIC_COMPLETION_SHA256 = (
    "8020baa5a3dad7c2cf17ea49ed7053603a0a10b0a47b65cda030f83f1bef2123"
)
EXPECTED_COMPONENT_ASTS_SHA256 = (
    "00fd2501d34305fd49f02da61d15b109d7c74a4b0449fa89b76838b06da8668e"
)
EXPECTED_RAW_ROWS_SHA256 = (
    "5457e0486676ac265b640dcd2e9162a37d7ef023e366f634dae865601cbfa580"
)
EXPECTED_COEFFICIENT_DAG_SHA256 = (
    "e1574b8e7343082c161234147e437220f516392e7c175bce618fa0da433c1579"
)


def _selected_s9_semantics(module: Any) -> dict[str, Any]:
    primitives = {item.name: item for item in module.primitive_specs()}
    names = ("N_T", "u", "h", "Gamma4", "Kcal", "acceleration", "Robin")
    if not all(name in primitives for name in names):
        raise KARRawFrechetError("S9 semantic primitive inventory drift")
    return {
        name: {
            "formula": primitives[name].formula,
            "variation": list(primitives[name].variation),
            "uses": list(primitives[name].uses),
            "opaque": primitives[name].opaque,
        }
        for name in names
    }


def certify_dependencies() -> tuple[dict[str, str], dict[str, Any]]:
    observed = {name: _sha256(path) for name, path in PINNED_PATHS.items()}
    if observed != PINNED_INPUTS:
        raise KARRawFrechetError("byte-pinned S8/S9/S10 dependency drift")
    s10 = _load(S10_SOURCE, "_holo_s10_for_v56713")
    s9 = _load(S9_SOURCE, "_holo_s9_for_v56713")
    action, dependency = s10.certify_v52_dependency()
    if _canonical_sha256(action) != s10.V52_EXACT_ACTION_SHA256:
        raise KARRawFrechetError("S10 exact action binding drift")
    if dependency.get("checks", {}).get("all") is not True:
        raise KARRawFrechetError("S10 v5.2 dependency is not certified")
    if action["foliation_lower"] != (
        "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-"
        "lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
        "B4_bar*Rcal^2/(16*k_infinity^2)]"
    ):
        raise KARRawFrechetError("v5.2 foliation literal drift")
    if action["Robin_intrinsic"] != (
        "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*"
        "h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)"
    ):
        raise KARRawFrechetError("v5.2 Robin literal drift")
    selected = _selected_s9_semantics(s9)
    required_fragments = {
        "N_T": "(-gamma^mn*D_m T*D_n T)^(-1/2)",
        "u": "u_m=-N_T*D_m T",
        "h": "h_mn=gamma_mn+u_m*u_n",
        "Kcal": "Kcal_mn=h_m^r*h_n^s*D_r u_s",
        "acceleration": "a_m=u^n*D_n u_m",
        "Robin": "l_Robin=-(kappa_hat/2)*vol_gamma*h_mn*q^m*q^n",
    }
    for name, fragment in required_fragments.items():
        if fragment not in selected[name]["formula"]:
            raise KARRawFrechetError(f"S9 {name} semantic formula drift")
    lineage = {
        "observed_source_test_sha256": observed,
        "declared_commits": LINEAGE_COMMITS,
        "S10_exact_action_sha256": s10.V52_EXACT_ACTION_SHA256,
        "S9_selected_semantics": selected,
        "S9_selected_semantics_sha256": _canonical_sha256(selected),
        "S8_role": "correct khronon chain-rule provenance; its R/R2 post-adjoint microlemma is not imported as raw rows",
    }
    return dict(action), lineage


def _node_record(expr: Expr) -> dict[str, Any]:
    if expr.op == "const":
        return {"schema": NODE_SCHEMA, "op": "const", "numerator": expr.data[0], "denominator": expr.data[1]}
    if expr.op == "param":
        return {"schema": NODE_SCHEMA, "op": "param", "name": expr.data[0]}
    if expr.op in {"gamma", "dgamma", "T1", "T2", "varphi", "ginv"}:
        return {"schema": NODE_SCHEMA, "op": expr.op, "indices": list(expr.data)}
    if expr.op == "volume":
        return {"schema": NODE_SCHEMA, "op": "volume"}
    if expr.op in {"add", "mul"}:
        return {
            "schema": NODE_SCHEMA,
            "op": expr.op,
            "args": sorted(_node_hash(arg) for arg in expr.args),
        }
    if expr.op == "pow":
        return {
            "schema": NODE_SCHEMA,
            "op": "pow",
            "arg": _node_hash(expr.args[0]),
            "exponent": [expr.data[0], expr.data[1]],
        }
    raise KARRawFrechetError(f"cannot serialize opcode {expr.op}")


@lru_cache(maxsize=None)
def _node_hash(expr: Expr) -> str:
    return _canonical_sha256(_node_record(expr))


def export_coefficient_dag(roots: Iterable[Expr]) -> dict[str, dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}

    def visit(expr: Expr) -> None:
        digest = _node_hash(expr)
        if digest in nodes:
            return
        for child in expr.args:
            visit(child)
        record = _node_record(expr)
        if digest in nodes and nodes[digest] != record:
            raise KARRawFrechetError("coefficient DAG hash collision")
        nodes[digest] = record

    for root in roots:
        visit(root)
    return dict(sorted(nodes.items()))


def _validate_indices(op: str, indices: Any) -> bool:
    if type(indices) is not list or any(type(i) is not int or not 0 <= i < DIM for i in indices):
        return False
    if op in {"gamma", "ginv", "T2"}:
        return len(indices) == 2 and indices[0] <= indices[1]
    if op == "dgamma":
        return len(indices) == 3 and indices[1] <= indices[2]
    return op in {"T1", "varphi"} and len(indices) == 1


def validate_coefficient_dag(
    dag: Mapping[str, Mapping[str, Any]], roots: Iterable[str]
) -> bool:
    if type(dag) is not dict or any(type(key) is not str or type(value) is not dict for key, value in dag.items()):
        return False
    dependencies: dict[str, list[str]] = {}
    for digest, record in dag.items():
        if _canonical_sha256(record) != digest or record.get("schema") != NODE_SCHEMA:
            return False
        op = record.get("op")
        if op == "const":
            if set(record) != {"schema", "op", "numerator", "denominator"}:
                return False
            if type(record["numerator"]) is not int or type(record["denominator"]) is not int or record["denominator"] <= 0:
                return False
            if math.gcd(record["numerator"], record["denominator"]) != 1:
                return False
            refs: list[str] = []
        elif op == "param":
            if set(record) != {"schema", "op", "name"} or record["name"] not in PARAMETERS:
                return False
            refs = []
        elif op in {"gamma", "dgamma", "T1", "T2", "varphi", "ginv"}:
            if set(record) != {"schema", "op", "indices"} or not _validate_indices(op, record["indices"]):
                return False
            refs = []
        elif op == "volume":
            if set(record) != {"schema", "op"}:
                return False
            refs = []
        elif op in {"add", "mul"}:
            if set(record) != {"schema", "op", "args"} or type(record["args"]) is not list or len(record["args"]) < 2:
                return False
            if any(type(ref) is not str for ref in record["args"]) or record["args"] != sorted(record["args"]):
                return False
            refs = list(record["args"])
        elif op == "pow":
            if set(record) != {"schema", "op", "arg", "exponent"}:
                return False
            exponent = record["exponent"]
            if type(record["arg"]) is not str or type(exponent) is not list or len(exponent) != 2:
                return False
            if any(type(value) is not int for value in exponent) or exponent[1] <= 0 or math.gcd(*exponent) != 1:
                return False
            refs = [record["arg"]]
        else:
            return False
        if any(ref not in dag for ref in refs):
            return False
        dependencies[digest] = refs

    root_list = list(roots)
    if any(type(root) is not str or root not in dag for root in root_list):
        return False
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(digest: str) -> bool:
        if digest in visiting:
            return False
        if digest in visited:
            return True
        visiting.add(digest)
        if not all(visit(child) for child in dependencies[digest]):
            return False
        visiting.remove(digest)
        visited.add(digest)
        return True

    if not all(visit(root) for root in root_list):
        return False
    return visited == set(dag)


def decode_coefficient_dag_expression(
    digest: str,
    dag: Mapping[str, Mapping[str, Any]],
    memo: dict[str, Expr] | None = None,
) -> Expr:
    """Decode the public DAG without consulting ``_node_record``.

    This is the inverse bridge missing from earlier drafts: a malicious
    serializer cannot silently relabel an Expr leaf and remain self-consistent
    merely by rehashing the exported graph.
    """

    if memo is None:
        memo = {}
    if digest in memo:
        return memo[digest]
    try:
        record = dag[digest]
    except KeyError as exc:
        raise KARRawFrechetError("DAG decoder saw an absent digest") from exc
    op = record["op"]
    if op == "const":
        expression = const(Fraction(record["numerator"], record["denominator"]))
    elif op == "param":
        expression = param(record["name"])
    elif op == "gamma":
        expression = gamma(*record["indices"])
    elif op == "dgamma":
        expression = dgamma(*record["indices"])
    elif op == "T1":
        expression = t1(*record["indices"])
    elif op == "T2":
        expression = t2(*record["indices"])
    elif op == "varphi":
        expression = varphi(*record["indices"])
    elif op == "ginv":
        expression = ginv(*record["indices"])
    elif op == "volume":
        expression = VOLUME
    elif op == "add":
        expression = add(*(decode_coefficient_dag_expression(child, dag, memo) for child in record["args"]))
    elif op == "mul":
        expression = mul(*(decode_coefficient_dag_expression(child, dag, memo) for child in record["args"]))
    elif op == "pow":
        expression = power(
            decode_coefficient_dag_expression(record["arg"], dag, memo),
            Fraction(record["exponent"][0], record["exponent"][1]),
        )
    else:
        raise KARRawFrechetError(f"DAG decoder rejects opcode {op!r}")
    memo[digest] = expression
    return expression


def validate_expr_row_dag_binding(
    forms: Mapping[str, Mapping[VariationKey, Expr]],
    rows: Sequence[Mapping[str, Any]],
    dag: Mapping[str, Mapping[str, Any]],
    independent_forms: Mapping[str, Mapping[VariationKey, Expr]] | None = None,
) -> bool:
    """Bind each decoded row root to both symbolic derivation routes."""

    if not validate_coefficient_dag(
        dag, [row.get("coefficient_root_sha256") for row in rows]
    ):
        return False
    observed: dict[tuple[str, VariationKey], str] = {}
    for row in rows:
        try:
            variation = row["variation"]
            key = _variation_key(
                variation["slot"],
                variation["derivative_word"],
                variation["component_indices"],
            )
            lookup = (row["component"], key)
            root = row["coefficient_root_sha256"]
        except (KeyError, TypeError, KARRawFrechetError):
            return False
        if lookup in observed or type(root) is not str:
            return False
        observed[lookup] = root
    expected = {
        (component, key): coefficient
        for component in COMPONENTS
        for key, coefficient in forms[component].items()
    }
    if set(observed) != set(expected):
        return False
    independent = (
        {
            (component, key): coefficient
            for component in COMPONENTS
            for key, coefficient in independent_forms[component].items()
        }
        if independent_forms is not None
        else expected
    )
    if set(independent) != set(expected) or any(
        expected[lookup] != independent[lookup] for lookup in expected
    ):
        return False
    memo: dict[str, Expr] = {}
    try:
        return all(
            decode_coefficient_dag_expression(observed[lookup], dag, memo)
            == coefficient
            == independent[lookup]
            for lookup, coefficient in expected.items()
        )
    except (KeyError, TypeError, KARRawFrechetError):
        return False


def _field_for_slot(slot: str) -> str:
    return {"H": "gamma", "tau": "T", "v": "varphi_H"}[slot]


def export_raw_rows(
    forms: Mapping[str, Mapping[VariationKey, Expr]],
    program: ComponentProgram,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for component in COMPONENTS:
        ordered = sorted(forms[component].items())
        for ordinal, (key, coefficient) in enumerate(ordered):
            slot, word, indices = key
            rows.append(
                {
                    "schema": ROW_SCHEMA,
                    "component": component,
                    "domain": "Sigma",
                    "field": _field_for_slot(slot),
                    "variation": {
                        "slot": slot,
                        "derivative_word": list(word),
                        "component_indices": list(indices),
                    },
                    "coefficient_root_sha256": _node_hash(coefficient),
                    "summand_ordinal": ordinal,
                    "source_span": dict(program.source_spans[component]),
                }
            )
    return rows


def validate_raw_rows(
    rows: Sequence[Mapping[str, Any]],
    dag: Mapping[str, Mapping[str, Any]],
    action: Mapping[str, str],
) -> bool:
    if type(rows) is not list or any(type(row) is not dict for row in rows):
        return False
    required = {
        "schema", "component", "domain", "field", "variation",
        "coefficient_root_sha256", "summand_ordinal", "source_span",
    }
    grouped: dict[str, list[Mapping[str, Any]]] = {name: [] for name in COMPONENTS}
    for row in rows:
        if set(row) != required or row["schema"] != ROW_SCHEMA or row["component"] not in COMPONENTS:
            return False
        if row["domain"] != "Sigma" or type(row["summand_ordinal"]) is not int or row["summand_ordinal"] < 0:
            return False
        variation = row["variation"]
        if type(variation) is not dict or set(variation) != {"slot", "derivative_word", "component_indices"}:
            return False
        slot = variation["slot"]
        word = variation["derivative_word"]
        indices = variation["component_indices"]
        if slot not in SLOTS or row["field"] != _field_for_slot(slot):
            return False
        if type(word) is not list or any(type(i) is not int or not 0 <= i < DIM for i in word):
            return False
        if type(indices) is not list or any(type(i) is not int or not 0 <= i < DIM for i in indices):
            return False
        if slot == "H" and (len(word) not in {0, 1} or len(indices) != 2 or indices[0] > indices[1]):
            return False
        if slot == "tau" and (len(word) not in {1, 2} or indices):
            return False
        if slot == "tau" and len(word) == 2 and word[0] > word[1]:
            return False
        if slot == "v" and (word or len(indices) != 1):
            return False
        root = row["coefficient_root_sha256"]
        if type(root) is not str or root not in dag:
            return False
        span = row["source_span"]
        if type(span) is not dict or set(span) != {"action_key", "start", "end", "text"}:
            return False
        key = span["action_key"]
        if key not in {"foliation_lower", "Robin_intrinsic"}:
            return False
        if any(type(span[name]) is not int for name in ("start", "end")) or type(span["text"]) is not str:
            return False
        if not (0 <= span["start"] < span["end"] <= len(action[key])):
            return False
        if action[key][span["start"] : span["end"]] != span["text"]:
            return False
        grouped[row["component"]].append(row)
    if any(not grouped[name] for name in COMPONENTS):
        return False
    for name in COMPONENTS:
        if [row["summand_ordinal"] for row in grouped[name]] != list(range(len(grouped[name]))):
            return False
    roots = [row["coefficient_root_sha256"] for row in rows]
    if not validate_coefficient_dag(dag, roots):
        return False

    # A schema-valid row is not yet a semantic row.  Reconstruct metadata and
    # variation keys through the independent literal program/context route.
    # Root semantics are checked by the independent DAG decoder bridge rather
    # than by reusing the producer serializer here.
    canonical_program = independent_literal_component_program(action)
    canonical_forms = {
        name: reverse_context_frechet(expr)
        for name, expr in canonical_program.components.items()
    }
    canonical_rows: list[dict[str, Any]] = []
    slot_to_field = {"H": "gamma", "tau": "T", "v": "varphi_H"}
    for component in COMPONENTS:
        for ordinal, (variation_key, coefficient) in enumerate(
            sorted(canonical_forms[component].items())
        ):
            slot, derivative_word, component_indices = variation_key
            canonical_rows.append(
                {
                    "schema": ROW_SCHEMA,
                    "component": component,
                    "domain": "Sigma",
                    "field": slot_to_field[slot],
                    "variation": {
                        "slot": slot,
                        "derivative_word": list(derivative_word),
                        "component_indices": list(component_indices),
                    },
                    "coefficient_root_sha256": None,
                    "summand_ordinal": ordinal,
                    "source_span": dict(canonical_program.source_spans[component]),
                }
            )
    if len(rows) != len(canonical_rows):
        return False
    for observed_row, canonical_row in zip(rows, canonical_rows, strict=True):
        observed_metadata = dict(observed_row)
        root = observed_metadata.pop("coefficient_root_sha256", None)
        canonical_metadata = dict(canonical_row)
        canonical_metadata.pop("coefficient_root_sha256")
        if type(root) is not str or observed_metadata != canonical_metadata:
            return False
    canonical_counts = {
        name: sum(row["component"] == name for row in canonical_rows)
        for name in COMPONENTS
    }
    if canonical_counts != EXPECTED_ROW_COUNTS:
        return False
    component_roots = {
        name: {
            row["coefficient_root_sha256"]
            for row in rows
            if row["component"] == name
        }
        for name in COMPONENTS
    }
    if any(len(component_roots[name]) != EXPECTED_ROW_COUNTS[name] for name in COMPONENTS):
        return False
    if any(
        not component_roots[left].isdisjoint(component_roots[right])
        for index, left in enumerate(COMPONENTS)
        for right in COMPONENTS[index + 1 :]
    ):
        return False
    return True


def _matrix_inverse_fraction(matrix: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    augmented = [
        [Fraction(value) for value in row] + [Fraction(1 if i == j else 0) for j in range(DIM)]
        for i, row in enumerate(matrix)
    ]
    for column in range(DIM):
        pivot = next((row for row in range(column, DIM) if augmented[row][column] != 0), None)
        if pivot is None:
            raise KARRawFrechetError("singular metric witness")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(DIM):
            if row == column:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                value - scale * reference
                for value, reference in zip(augmented[row], augmented[column], strict=True)
            ]
    return [row[DIM:] for row in augmented]


def _det_fraction(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    total = Fraction(0)
    for permutation in itertools.permutations(range(DIM)):
        inversions = sum(permutation[i] > permutation[j] for i in range(DIM) for j in range(i + 1, DIM))
        term = Fraction(-1 if inversions % 2 else 1)
        for i, j in enumerate(permutation):
            term *= matrix[i][j]
        total += term
    return total


def _sqrt_fraction(value: Fraction) -> Fraction:
    if value < 0:
        raise KARRawFrechetError("negative exact square-root witness")
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise KARRawFrechetError("oracle witness is not an exact rational square")
    return Fraction(numerator, denominator)


@dataclass(frozen=True)
class Witness:
    gamma: tuple[tuple[Fraction, ...], ...]
    congruence_frame: tuple[tuple[Fraction, ...], ...]
    minkowski_clock: tuple[Fraction, ...]
    dgamma: tuple[tuple[tuple[Fraction, ...], ...], ...]
    T1: tuple[Fraction, ...]
    T2: tuple[tuple[Fraction, ...], ...]
    varphi: tuple[Fraction, ...]
    parameters: Mapping[str, Fraction]


def _fraction_witness(seed: int) -> Witness:
    if seed == 1:
        frame = (
            (Fraction(1), Fraction(1, 5), Fraction(-1, 7), Fraction(2, 9)),
            (Fraction(0), Fraction(1), Fraction(1, 4), Fraction(-1, 6)),
            (Fraction(0), Fraction(0), Fraction(1), Fraction(1, 3)),
            (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
        )
        minkowski_clock = (
            Fraction(325, 144),
            Fraction(3, 4),
            Fraction(5, 3),
            Fraction(125, 144),
        )
    elif seed == 2:
        frame = (
            (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
            (Fraction(1, 3), Fraction(1), Fraction(0), Fraction(0)),
            (Fraction(-1, 4), Fraction(2, 5), Fraction(1), Fraction(0)),
            (Fraction(1, 6), Fraction(-1, 7), Fraction(3, 8), Fraction(1)),
        )
        minkowski_clock = (
            Fraction(325, 144),
            Fraction(5, 12),
            Fraction(13, 16),
            Fraction(65, 36),
        )
    else:
        raise KARRawFrechetError("only the two frozen rational witnesses exist")
    eta = (Fraction(-1), Fraction(1), Fraction(1), Fraction(1))
    metric = tuple(
        tuple(
            sum(
                (eta[k] * frame[k][i] * frame[k][j] for k in range(DIM)),
                Fraction(0),
            )
            for j in range(DIM)
        )
        for i in range(DIM)
    )
    first = tuple(
        tuple(
            tuple(Fraction(((-1) ** (seed + k + i + j)) * (seed + 1 + k + 2 * i + 3 * j), 17 + seed + k + i + j) for j in range(DIM))
            for i in range(DIM)
        )
        for k in range(DIM)
    )
    # Symmetrize the last two metric indices exactly.
    first = tuple(
        tuple(tuple(first[k][min(i, j)][max(i, j)] for j in range(DIM)) for i in range(DIM))
        for k in range(DIM)
    )
    # If gamma=A^T eta A and T=A^T t, then
    # T^T gamma^-1 T=t^T eta t.  The two displayed t are independently
    # generated by rational Lorentz boosts and have norm exactly -1.
    t_gradient = tuple(
        sum((frame[k][i] * minkowski_clock[k] for k in range(DIM)), Fraction(0))
        for i in range(DIM)
    )
    second = tuple(
        tuple(Fraction(((-1) ** (seed + i + j)) * (2 + seed + i + 2 * j), 19 + seed + i + j) for j in range(DIM))
        for i in range(DIM)
    )
    second = tuple(tuple(second[min(i, j)][max(i, j)] for j in range(DIM)) for i in range(DIM))
    return Witness(
        gamma=metric,
        congruence_frame=frame,
        minkowski_clock=minkowski_clock,
        dgamma=first,
        T1=t_gradient,
        T2=second,
        varphi=tuple(Fraction(((-1) ** (seed + i)) * (3 + seed + i), 11 + seed + i) for i in range(DIM)),
        parameters={
            "Mb": Fraction(7 + seed, 5),
            "lambda_K": Fraction(2 + seed, 7),
            "eta": Fraction(5 + seed, 9),
            "y": Fraction(3 + seed, 8),
            "kappa_hat": Fraction(11 + seed, 6),
        },
    )


@dataclass(frozen=True)
class EvalContext:
    witness: Witness
    inverse: tuple[tuple[Fraction, ...], ...]
    volume: Fraction


def _eval_context(witness: Witness) -> EvalContext:
    inverse = tuple(tuple(row) for row in _matrix_inverse_fraction(witness.gamma))
    volume = _sqrt_fraction(-_det_fraction(witness.gamma))
    return EvalContext(witness, inverse, volume)


def eval_expr(expr: Expr, context: EvalContext, cache: dict[Expr, Fraction] | None = None) -> Fraction:
    if cache is None:
        cache = {}
    if expr in cache:
        return cache[expr]
    w = context.witness
    if expr.op == "const":
        value = Fraction(expr.data[0], expr.data[1])
    elif expr.op == "param":
        value = w.parameters[expr.data[0]]
    elif expr.op == "gamma":
        value = w.gamma[expr.data[0]][expr.data[1]]
    elif expr.op == "dgamma":
        value = w.dgamma[expr.data[0]][expr.data[1]][expr.data[2]]
    elif expr.op == "T1":
        value = w.T1[expr.data[0]]
    elif expr.op == "T2":
        value = w.T2[expr.data[0]][expr.data[1]]
    elif expr.op == "varphi":
        value = w.varphi[expr.data[0]]
    elif expr.op == "ginv":
        value = context.inverse[expr.data[0]][expr.data[1]]
    elif expr.op == "volume":
        value = context.volume
    elif expr.op == "add":
        value = sum((eval_expr(arg, context, cache) for arg in expr.args), Fraction(0))
    elif expr.op == "mul":
        value = Fraction(1)
        for arg in expr.args:
            value *= eval_expr(arg, context, cache)
    elif expr.op == "pow":
        base = eval_expr(expr.args[0], context, cache)
        exponent = Fraction(expr.data[0], expr.data[1])
        if exponent.denominator == 1:
            value = base ** exponent.numerator
        elif exponent.denominator == 2:
            root = _sqrt_fraction(base)
            value = root ** exponent.numerator
        else:
            raise KARRawFrechetError("unsupported exact evaluator exponent")
    else:
        raise KARRawFrechetError(f"no evaluator for {expr.op}")
    cache[expr] = value
    return value


def eval_coefficient_dag(
    digest: str,
    dag: Mapping[str, Mapping[str, Any]],
    context: EvalContext,
    cache: dict[str, Fraction] | None = None,
) -> Fraction:
    """Evaluate the serialized public DAG, independently of ``Expr``."""

    if cache is None:
        cache = {}
    if digest in cache:
        return cache[digest]
    record = dag[digest]
    op = record["op"]
    w = context.witness
    if op == "const":
        value = Fraction(record["numerator"], record["denominator"])
    elif op == "param":
        value = w.parameters[record["name"]]
    elif op == "gamma":
        i, j = record["indices"]
        value = w.gamma[i][j]
    elif op == "dgamma":
        k, i, j = record["indices"]
        value = w.dgamma[k][i][j]
    elif op == "T1":
        value = w.T1[record["indices"][0]]
    elif op == "T2":
        i, j = record["indices"]
        value = w.T2[i][j]
    elif op == "varphi":
        value = w.varphi[record["indices"][0]]
    elif op == "ginv":
        i, j = record["indices"]
        value = context.inverse[i][j]
    elif op == "volume":
        value = context.volume
    elif op == "add":
        value = sum(
            (eval_coefficient_dag(child, dag, context, cache) for child in record["args"]),
            Fraction(0),
        )
    elif op == "mul":
        value = Fraction(1)
        for child in record["args"]:
            value *= eval_coefficient_dag(child, dag, context, cache)
    elif op == "pow":
        base = eval_coefficient_dag(record["arg"], dag, context, cache)
        exponent = Fraction(record["exponent"][0], record["exponent"][1])
        if exponent.denominator == 1:
            value = base ** exponent.numerator
        elif exponent.denominator == 2:
            value = _sqrt_fraction(base) ** exponent.numerator
        else:
            raise KARRawFrechetError("DAG evaluator exponent is not half-integral")
    else:
        raise KARRawFrechetError(f"DAG evaluator rejects opcode {op!r}")
    cache[digest] = value
    return value


@dataclass(frozen=True)
class Dual:
    primal: Fraction
    tangent: Fraction = Fraction(0)

    def __add__(self, other: "Dual | Fraction | int") -> "Dual":
        other = _dual(other)
        return Dual(self.primal + other.primal, self.tangent + other.tangent)

    __radd__ = __add__

    def __neg__(self) -> "Dual":
        return Dual(-self.primal, -self.tangent)

    def __sub__(self, other: "Dual | Fraction | int") -> "Dual":
        return self + (-_dual(other))

    def __rsub__(self, other: "Dual | Fraction | int") -> "Dual":
        return _dual(other) - self

    def __mul__(self, other: "Dual | Fraction | int") -> "Dual":
        other = _dual(other)
        return Dual(
            self.primal * other.primal,
            self.tangent * other.primal + self.primal * other.tangent,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: "Dual | Fraction | int") -> "Dual":
        other = _dual(other)
        if other.primal == 0:
            raise KARRawFrechetError("division by zero in dual oracle")
        return Dual(
            self.primal / other.primal,
            (self.tangent * other.primal - self.primal * other.tangent) / (other.primal * other.primal),
        )

    def __rtruediv__(self, other: "Dual | Fraction | int") -> "Dual":
        return _dual(other) / self


def _dual(value: Dual | Fraction | int) -> Dual:
    return value if isinstance(value, Dual) else Dual(Fraction(value))


def _dual_power(value: Dual, exponent: Fraction) -> Dual:
    if exponent.denominator == 1:
        primal = value.primal ** exponent.numerator
        tangent = exponent * (value.primal ** (exponent - 1)) * value.tangent
        return Dual(primal, tangent)
    if exponent.denominator != 2:
        raise KARRawFrechetError("independent oracle exponent is not half-integral")
    root = _sqrt_fraction(value.primal)
    primal = root ** exponent.numerator
    tangent = exponent * (root ** (exponent.numerator - 2)) * value.tangent
    return Dual(primal, tangent)


def _inverse_dual(matrix: Sequence[Sequence[Dual]]) -> list[list[Dual]]:
    augmented = [
        [value for value in row] + [Dual(Fraction(1 if i == j else 0)) for j in range(DIM)]
        for i, row in enumerate(matrix)
    ]
    for column in range(DIM):
        pivot = next((row for row in range(column, DIM) if augmented[row][column].primal != 0), None)
        if pivot is None:
            raise KARRawFrechetError("singular metric in independent dual oracle")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(DIM):
            if row == column:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                value - scale * reference
                for value, reference in zip(augmented[row], augmented[column], strict=True)
            ]
    return [row[DIM:] for row in augmented]


def _det_dual(matrix: Sequence[Sequence[Dual]]) -> Dual:
    total = Dual(Fraction(0))
    for permutation in itertools.permutations(range(DIM)):
        inversions = sum(permutation[i] > permutation[j] for i in range(DIM) for j in range(i + 1, DIM))
        term = Dual(Fraction(-1 if inversions % 2 else 1))
        for i, j in enumerate(permutation):
            term *= matrix[i][j]
        total += term
    return total


def all_variation_keys() -> tuple[VariationKey, ...]:
    keys: list[VariationKey] = []
    keys.extend(_variation_key("H", (), (i, j)) for i in range(DIM) for j in range(i, DIM))
    keys.extend(_variation_key("H", (k,), (i, j)) for k in range(DIM) for i in range(DIM) for j in range(i, DIM))
    keys.extend(_variation_key("tau", (i,), ()) for i in range(DIM))
    keys.extend(_variation_key("tau", (i, j), ()) for i in range(DIM) for j in range(i, DIM))
    keys.extend(_variation_key("v", (), (i,)) for i in range(DIM))
    return tuple(keys)


def _basis_tangent(key: VariationKey) -> Mapping[VariationKey, Fraction]:
    return {key: Fraction(1)}


def independent_dual_components(
    witness: Witness,
    tangent: Mapping[VariationKey, Fraction],
    *,
    u_sign: int = -1,
) -> dict[str, Dual]:
    def tangent_of(slot: str, word: Sequence[int], indices: Sequence[int]) -> Fraction:
        return tangent.get(_variation_key(slot, word, indices), Fraction(0))

    metric = [
        [Dual(witness.gamma[i][j], tangent_of("H", (), _canonical_pair(i, j))) for j in range(DIM)]
        for i in range(DIM)
    ]
    metric_first = [
        [
            [Dual(witness.dgamma[k][i][j], tangent_of("H", (k,), _canonical_pair(i, j))) for j in range(DIM)]
            for i in range(DIM)
        ]
        for k in range(DIM)
    ]
    T_first = [Dual(witness.T1[i], tangent_of("tau", (i,), ())) for i in range(DIM)]
    T_second = [
        [Dual(witness.T2[i][j], tangent_of("tau", _canonical_pair(i, j), ())) for j in range(DIM)]
        for i in range(DIM)
    ]
    phi = [Dual(witness.varphi[i], tangent_of("v", (), (i,))) for i in range(DIM)]
    inverse = _inverse_dual(metric)
    determinant = _det_dual(metric)
    volume = _dual_power(-determinant, Fraction(1, 2))
    clock_norm = -sum(
        (inverse[i][j] * T_first[i] * T_first[j] for i in range(DIM) for j in range(DIM)),
        Dual(Fraction(0)),
    )
    lapse = _dual_power(clock_norm, Fraction(-1, 2))
    connection = [
        [
            [
                sum(
                    (
                        inverse[l][q]
                        * (metric_first[r][q][s] + metric_first[s][q][r] - metric_first[q][r][s])
                        / 2
                        for q in range(DIM)
                    ),
                    Dual(Fraction(0)),
                )
                for s in range(DIM)
            ]
            for r in range(DIM)
        ]
        for l in range(DIM)
    ]
    # Independent route: differentiate the clock norm directly, not through
    # the AST coordinate-partial visitor.
    inverse_first = [
        [
            [
                -sum(
                    (inverse[i][a] * metric_first[k][a][b] * inverse[b][j] for a in range(DIM) for b in range(DIM)),
                    Dual(Fraction(0)),
                )
                for j in range(DIM)
            ]
            for i in range(DIM)
        ]
        for k in range(DIM)
    ]
    norm_first = [
        -sum(
            (
                inverse_first[k][i][j] * T_first[i] * T_first[j]
                + inverse[i][j] * T_second[k][i] * T_first[j]
                + inverse[i][j] * T_first[i] * T_second[k][j]
                for i in range(DIM)
                for j in range(DIM)
            ),
            Dual(Fraction(0)),
        )
        for k in range(DIM)
    ]
    lapse_first = [Fraction(-1, 2) * _dual_power(clock_norm, Fraction(-3, 2)) * norm_first[k] for k in range(DIM)]
    u_cov = [u_sign * lapse * T_first[i] for i in range(DIM)]
    u_first = [
        [u_sign * (lapse_first[k] * T_first[i] + lapse * T_second[k][i]) for i in range(DIM)]
        for k in range(DIM)
    ]
    u_contra = [sum((inverse[i][j] * u_cov[j] for j in range(DIM)), Dual(Fraction(0))) for i in range(DIM)]
    h_cov = [[metric[i][j] + u_cov[i] * u_cov[j] for j in range(DIM)] for i in range(DIM)]
    h_contra = [[inverse[i][j] + u_contra[i] * u_contra[j] for j in range(DIM)] for i in range(DIM)]
    h_mixed = [
        [Dual(Fraction(1 if i == r else 0)) + u_cov[i] * u_contra[r] for r in range(DIM)]
        for i in range(DIM)
    ]
    nabla_u = [
        [u_first[r][s] - sum((connection[l][r][s] * u_cov[l] for l in range(DIM)), Dual(Fraction(0))) for s in range(DIM)]
        for r in range(DIM)
    ]
    k_tensor = [
        [
            sum(
                (h_mixed[i][r] * h_mixed[j][s] * nabla_u[r][s] for r in range(DIM) for s in range(DIM)),
                Dual(Fraction(0)),
            )
            for j in range(DIM)
        ]
        for i in range(DIM)
    ]
    k_trace = sum((h_contra[i][j] * k_tensor[i][j] for i in range(DIM) for j in range(DIM)), Dual(Fraction(0)))
    k2 = sum(
        (
            h_contra[i][r] * h_contra[j][s] * k_tensor[i][j] * k_tensor[r][s]
            for i in range(DIM) for j in range(DIM) for r in range(DIM) for s in range(DIM)
        ),
        Dual(Fraction(0)),
    )
    p = witness.parameters
    k_density = Fraction(1, 2) * p["Mb"] ** 2 * volume * (k2 - p["lambda_K"] * k_trace * k_trace)
    a_cov = [sum((u_contra[n] * nabla_u[n][m] for n in range(DIM)), Dual(Fraction(0))) for m in range(DIM)]
    a_contra = [sum((inverse[m][n] * a_cov[n] for n in range(DIM)), Dual(Fraction(0))) for m in range(DIM)]
    a2 = sum((inverse[m][n] * a_cov[m] * a_cov[n] for m in range(DIM) for n in range(DIM)), Dual(Fraction(0)))
    a_density = Fraction(1, 2) * p["Mb"] ** 2 * p["eta"] * volume * a2
    q = [phi[m] - p["y"] * a_contra[m] for m in range(DIM)]
    robin_norm = sum((h_cov[m][n] * q[m] * q[n] for m in range(DIM) for n in range(DIM)), Dual(Fraction(0)))
    robin_density = Fraction(-1, 2) * p["kappa_hat"] * volume * robin_norm
    return {"K_foliation": k_density, "a_squared": a_density, "Robin": robin_density}


def _independent_oracle_certificate(
    program: ComponentProgram,
    forms: Mapping[str, Mapping[VariationKey, Expr]],
    rows: Sequence[Mapping[str, Any]],
    dag: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    keys = all_variation_keys()
    row_roots: dict[tuple[str, VariationKey], str] = {}
    row_lookup_valid = True
    for row in rows:
        try:
            variation = row["variation"]
            key = _variation_key(
                variation["slot"],
                variation["derivative_word"],
                variation["component_indices"],
            )
            lookup = (row["component"], key)
            if lookup in row_roots:
                row_lookup_valid = False
            row_roots[lookup] = row["coefficient_root_sha256"]
        except (KeyError, TypeError, KARRawFrechetError):
            row_lookup_valid = False
    witness_rows: list[dict[str, Any]] = []
    all_primal = True
    all_frechet = True
    all_geometry = True
    mismatch_examples: list[dict[str, Any]] = []
    for seed in (1, 2):
        witness = _fraction_witness(seed)
        context = _eval_context(witness)
        eta = (Fraction(-1), Fraction(1), Fraction(1), Fraction(1))
        reconstructed_metric = tuple(
            tuple(
                sum(
                    (
                        eta[k]
                        * witness.congruence_frame[k][i]
                        * witness.congruence_frame[k][j]
                        for k in range(DIM)
                    ),
                    Fraction(0),
                )
                for j in range(DIM)
            )
            for i in range(DIM)
        )
        transformed_clock = tuple(
            sum(
                (
                    witness.congruence_frame[k][i]
                    * witness.minkowski_clock[k]
                    for k in range(DIM)
                ),
                Fraction(0),
            )
            for i in range(DIM)
        )
        clock_norm = -sum(
            (
                context.inverse[i][j] * witness.T1[i] * witness.T1[j]
                for i in range(DIM)
                for j in range(DIM)
            ),
            Fraction(0),
        )
        minkowski_clock_norm = -sum(
            (
                eta[k] * witness.minkowski_clock[k] * witness.minkowski_clock[k]
                for k in range(DIM)
            ),
            Fraction(0),
        )
        frame_det = _det_fraction(witness.congruence_frame)
        metric_det = _det_fraction(witness.gamma)
        geometry = {
            "congruence_reconstruction_exact": reconstructed_metric == witness.gamma,
            "clock_covector_transform_exact": transformed_clock == witness.T1,
            "congruence_frame_determinant": _jsonable(frame_det),
            "metric_determinant": _jsonable(metric_det),
            "Lorentz_signature_by_invertible_congruence": frame_det != 0,
            "all_six_metric_offdiagonals_nonzero": all(
                witness.gamma[i][j] != 0
                for i in range(DIM)
                for j in range(i + 1, DIM)
            ),
            "all_four_clock_components_nonzero": all(value != 0 for value in witness.T1),
            "clock_norm": _jsonable(clock_norm),
            "minkowski_clock_norm": _jsonable(minkowski_clock_norm),
            "volume": _jsonable(context.volume),
        }
        geometry_pass = (
            geometry["congruence_reconstruction_exact"]
            and geometry["clock_covector_transform_exact"]
            and frame_det == 1
            and metric_det == -1
            and minkowski_clock_norm == 1
            and geometry["all_six_metric_offdiagonals_nonzero"]
            and geometry["all_four_clock_components_nonzero"]
            and clock_norm == 1
            and context.volume == 1
        )
        all_geometry &= geometry_pass
        direct_zero = independent_dual_components(witness, {})
        primal_matches = {
            component: eval_expr(program.components[component], context) == direct_zero[component].primal
            for component in COMPONENTS
        }
        all_primal &= all(primal_matches.values())
        coefficient_cache: dict[Expr, Fraction] = {}
        dag_cache: dict[str, Fraction] = {}
        checked = 0
        mismatches = 0
        for key in keys:
            direct = independent_dual_components(witness, _basis_tangent(key))
            for component in COMPONENTS:
                ast_value = eval_expr(forms[component].get(key, ZERO), context, coefficient_cache)
                root = row_roots.get((component, key))
                try:
                    dag_value = (
                        eval_coefficient_dag(root, dag, context, dag_cache)
                        if root is not None
                        else Fraction(0)
                    )
                except (KeyError, TypeError, KARRawFrechetError):
                    dag_value = None
                observed = direct[component].tangent
                checked += 1
                if ast_value != observed or dag_value != ast_value:
                    mismatches += 1
                    if len(mismatch_examples) < 8:
                        mismatch_examples.append(
                            {
                                "seed": seed,
                                "component": component,
                                "variation_key": _jsonable(key),
                                "AST_coefficient": _jsonable(ast_value),
                                "exported_DAG_coefficient": _jsonable(dag_value),
                                "independent_dual": _jsonable(observed),
                            }
                        )
        all_frechet &= row_lookup_valid and mismatches == 0
        witness_rows.append(
            {
                "seed": seed,
                "rational_congruence_geometry": geometry,
                "rational_congruence_geometry_pass": geometry_pass,
                "primal_matches": primal_matches,
                "basis_component_comparisons": checked,
                "mismatches": mismatches,
            }
        )
    return {
        "route": "independent exact Dual arithmetic plus Gauss-Jordan inverse and Leibniz determinant",
        "epistemic_scope": "finite exact evaluation at two explicit non-diagonal rational Lorentzian jet witnesses; not a universal identity by sampling",
        "witnesses": witness_rows,
        "variation_basis_size": len(keys),
        "component_count": len(COMPONENTS),
        "total_frechet_comparisons": len(keys) * len(COMPONENTS) * 2,
        "all_primal_components_match": all_primal,
        "all_basis_Frechet_coefficients_match": all_frechet,
        "row_lookup_is_bijective": row_lookup_valid,
        "all_rational_congruence_witnesses_verified": all_geometry,
        "mismatch_examples": mismatch_examples,
    }


def _orientation_parity_certificate() -> dict[str, Any]:
    def product(*values: int) -> int:
        return sum(values) % 2

    def compatible_sum(*values: int) -> int:
        if len(set(values)) != 1:
            raise KARRawFrechetError(
                f"orientation parity sum mixes even/odd terms: {values}"
            )
        return values[0]

    parity: dict[str, int] = {
        "gamma_ginv_volume_T_varphi_parameters": 0,
        "lapse": 0,
        "connection": 0,
        "u_cov": 1,
        "u_contra": 1,
        "partial_u": 1,
    }
    parity["h_cov_h_contra_h_mixed"] = compatible_sum(0, product(1, 1))
    parity["nabla_u"] = compatible_sum(
        parity["partial_u"], product(parity["connection"], parity["u_cov"])
    )
    parity["K_tensor"] = product(
        parity["h_cov_h_contra_h_mixed"],
        parity["h_cov_h_contra_h_mixed"],
        parity["nabla_u"],
    )
    parity["K_trace"] = product(
        parity["h_cov_h_contra_h_mixed"], parity["K_tensor"]
    )
    parity["K_tensor_squared"] = product(
        parity["K_tensor"], parity["K_tensor"]
    )
    parity["K_trace_squared"] = product(
        parity["K_trace"], parity["K_trace"]
    )
    parity["K_density"] = compatible_sum(
        parity["K_tensor_squared"], parity["K_trace_squared"]
    )
    parity["a_cov"] = product(parity["u_contra"], parity["nabla_u"])
    parity["a_contra"] = parity["a_cov"]
    parity["a_squared_density"] = product(parity["a_cov"], parity["a_cov"])
    parity["Robin_q"] = compatible_sum(0, parity["a_contra"])
    parity["Robin_density"] = product(
        parity["h_cov_h_contra_h_mixed"],
        parity["Robin_q"],
        parity["Robin_q"],
    )
    return {
        "convention": "0=even and 1=odd under u -> -u",
        "derived_parities": parity,
        "pass": all(
            parity[name] == 0
            for name in ("K_density", "a_squared_density", "Robin_density")
        ),
    }


def _orientation_invariance_certificate(
    action: Mapping[str, str], *, mutation: str | None = None
) -> dict[str, Any]:
    if mutation not in {
        None,
        "orientation_odd_hidden_term",
        "orientation_odd_double_zero",
    }:
        raise KARRawFrechetError(f"unknown orientation mutation {mutation}")
    minus = build_component_program(action, mutation=mutation, u_sign=-1)
    plus = build_component_program(action, mutation=mutation, u_sign=1)
    minus_forms = {name: frechet(expr) for name, expr in minus.components.items()}
    plus_forms = {name: frechet(expr) for name, expr in plus.components.items()}
    independent_minus = independent_literal_component_program(action, u_sign=-1)
    independent_plus = independent_literal_component_program(action, u_sign=1)
    independent_minus_forms = {
        name: reverse_context_frechet(independent_minus.components[name])
        for name in COMPONENTS
    }
    independent_plus_forms = {
        name: reverse_context_frechet(independent_plus.components[name])
        for name in COMPONENTS
    }

    def repinned_export_pipeline(
        program: ComponentProgram,
        forms: Mapping[str, Mapping[VariationKey, Expr]],
        independent_program: ComponentProgram,
        independent_forms: Mapping[str, Mapping[VariationKey, Expr]],
    ) -> dict[str, Any]:
        """Exercise an orientation candidate through export and independent decode."""

        rows = export_raw_rows(forms, program)
        roots = [
            coefficient
            for component_form in forms.values()
            for coefficient in component_form.values()
        ]
        dag = export_coefficient_dag(roots)
        observed_hashes = {
            "component_ASTS_sha256": _canonical_sha256(
                {
                    name: _node_hash(program.components[name])
                    for name in COMPONENTS
                }
            ),
            "raw_rows_sha256": _canonical_sha256(rows),
            "coefficient_DAG_sha256": _canonical_sha256(dag),
        }
        # Model the adversary repinning every internal digest after mutation.
        repinned_hashes = dict(observed_hashes)
        pin_checks = {
            name: observed_hashes[name] == repinned_hashes[name]
            for name in observed_hashes
        }
        literal_roots_bound = all(
            program.components[name] == independent_program.components[name]
            for name in COMPONENTS
        )
        strict_schema = validate_raw_rows(rows, dag, action)
        independent_binding = validate_expr_row_dag_binding(
            forms, rows, dag, independent_forms
        )
        return {
            "observed_hashes": observed_hashes,
            "repinned_hashes": repinned_hashes,
            "pin_checks": pin_checks,
            "internal_hashes_repinned": all(pin_checks.values()),
            "row_count": len(rows),
            "DAG_node_count": len(dag),
            "literal_component_roots_bound": literal_roots_bound,
            "strict_schema_pass": strict_schema,
            "independent_row_DAG_binding_pass": independent_binding,
            "ready_before_finite_witness_regression": (
                all(pin_checks.values())
                and literal_roots_bound
                and strict_schema
                and independent_binding
            ),
        }

    export_pipelines = {
        "u_sign_minus": repinned_export_pipeline(
            minus, minus_forms, independent_minus, independent_minus_forms
        ),
        "u_sign_plus": repinned_export_pipeline(
            plus, plus_forms, independent_plus, independent_plus_forms
        ),
    }
    symbolic_rows = {
        name: {
            "minus_root_bound_to_independent_literal": (
                minus.components[name] == independent_minus.components[name]
            ),
            "plus_root_bound_to_independent_literal": (
                plus.components[name] == independent_plus.components[name]
            ),
            "minus_form_bound_to_independent_context_derivative": (
                _linear_forms_exact(minus_forms[name], independent_minus_forms[name])
            ),
            "plus_form_bound_to_independent_context_derivative": (
                _linear_forms_exact(plus_forms[name], independent_plus_forms[name])
            ),
        }
        for name in COMPONENTS
    }
    for row in symbolic_rows.values():
        row["pass"] = all(row.values())
    parity = _orientation_parity_certificate()
    universal_symbolic = parity["pass"] and all(
        row["pass"] for row in symbolic_rows.values()
    )
    rows = []
    all_equal = True
    for seed in (1, 2):
        witness = _fraction_witness(seed)
        context = _eval_context(witness)
        minus_direct = independent_dual_components(witness, {}, u_sign=-1)
        plus_direct = independent_dual_components(witness, {}, u_sign=1)
        primal_equal: dict[str, bool] = {}
        both_primal_routes_match_oracles: dict[str, bool] = {}
        for name in COMPONENTS:
            minus_ast = eval_expr(minus.components[name], context)
            plus_ast = eval_expr(plus.components[name], context)
            primal_equal[name] = minus_ast == plus_ast
            both_primal_routes_match_oracles[name] = (
                minus_ast == minus_direct[name].primal
                and plus_ast == plus_direct[name].primal
            )
        derivative_equal = True
        both_derivative_routes_match_oracles = True
        minus_cache: dict[Expr, Fraction] = {}
        plus_cache: dict[Expr, Fraction] = {}
        for key in all_variation_keys():
            m = independent_dual_components(witness, _basis_tangent(key), u_sign=-1)
            p = independent_dual_components(witness, _basis_tangent(key), u_sign=1)
            for name in COMPONENTS:
                minus_coefficient = eval_expr(
                    minus_forms[name].get(key, ZERO), context, minus_cache
                )
                plus_coefficient = eval_expr(
                    plus_forms[name].get(key, ZERO), context, plus_cache
                )
                derivative_equal &= minus_coefficient == plus_coefficient
                both_derivative_routes_match_oracles &= (
                    minus_coefficient == m[name].tangent
                    and plus_coefficient == p[name].tangent
                )
        witness_pass = (
            all(primal_equal.values())
            and all(both_primal_routes_match_oracles.values())
            and derivative_equal
            and both_derivative_routes_match_oracles
        )
        all_equal &= witness_pass
        rows.append(
            {
                "seed": seed,
                "AST_primal_plus_equals_minus": primal_equal,
                "both_AST_primals_match_independent_oracles": both_primal_routes_match_oracles,
                "all_AST_basis_coefficients_plus_equal_minus": derivative_equal,
                "both_AST_basis_routes_match_independent_oracles": both_derivative_routes_match_oracles,
                "witness_pass": witness_pass,
            }
        )
    repinned_pipeline = {
        "orientation_signs": export_pipelines,
        "all_internal_hashes_repinned": all(
            row["internal_hashes_repinned"] for row in export_pipelines.values()
        ),
        "all_strict_schema_pass": all(
            row["strict_schema_pass"] for row in export_pipelines.values()
        ),
        "all_independent_row_DAG_bindings_pass": all(
            row["independent_row_DAG_binding_pass"]
            for row in export_pipelines.values()
        ),
        "finite_witness_oracle_pass": all_equal,
        "ready_after_repin": (
            all(
                row["ready_before_finite_witness_regression"]
                for row in export_pipelines.values()
            )
            and all_equal
        ),
    }
    return {
        "mutation": mutation,
        "conventions": [minus.convention, plus.convention],
        "meaning": "these even densities do not select the time orientation or the sign of Kcal",
        "epistemic_scope": (
            "universal formal parity plus exact root/form bindings; finite exact "
            "witness rows below are regression checks, not the proof"
        ),
        "symbolic_component_bindings": symbolic_rows,
        "orientation_parity_calculus": parity,
        "universal_symbolic_invariance": universal_symbolic,
        "finite_witness_regression_only": True,
        "witnesses": rows,
        "exact_rational_invariance": all_equal,
        "repinned_export_pipeline": repinned_pipeline,
        "orientation_selected_by_this_gate": False,
    }


def _rewrite_exported_dag(
    rows: list[dict[str, Any]],
    dag: dict[str, dict[str, Any]],
    record_mutator: Any,
) -> None:
    """Apply a serializer-level mutation and transitively repin every root."""

    old_dag = json.loads(json.dumps(dag))
    rebuilt: dict[str, dict[str, Any]] = {}
    memo: dict[str, str] = {}

    def rewrite(old: str) -> str:
        if old in memo:
            return memo[old]
        record = json.loads(json.dumps(old_dag[old]))
        if record["op"] in {"add", "mul"}:
            record["args"] = sorted(rewrite(child) for child in record["args"])
        elif record["op"] == "pow":
            record["arg"] = rewrite(record["arg"])
        record_mutator(record)
        new = _canonical_sha256(record)
        memo[old] = new
        rebuilt[new] = record
        return new

    for row in rows:
        row["coefficient_root_sha256"] = rewrite(row["coefficient_root_sha256"])
    dag.clear()
    dag.update(dict(sorted(rebuilt.items())))


CORE_MUTATIONS = (
    "correlated_wrong_inverse_sign",
    "correlated_wrong_volume_half",
    "correlated_wrong_fractional_power_sign",
    "correlated_hidden_offdiagonal_term",
    "serializer_leaf_relabel_after_repin",
    "wrong_christoffel_last_sign",
    "wrong_K_lambda_sign",
    "wrong_a_prefactor_half",
    "wrong_Robin_cross_sign",
    "wrong_Robin_prefactor_sign",
    "omit_Robin_varphi",
    "frechet_times_finite_gamma_factor",
    "frechet_times_parameter_y_alias_factor",
    "frechet_times_tau_varphi_double_zero_factor",
    "component_form_redistribution_preserving_aggregate",
)


def _apply_finite_witness_form_exploit(
    forms: Mapping[str, Mapping[VariationKey, Expr]],
    mutation: str | None,
) -> dict[str, LinearForm]:
    copied = {name: dict(forms[name]) for name in COMPONENTS}
    if mutation == "frechet_times_finite_gamma_factor":
        factor = add(
            ONE,
            mul(
                add(gamma(0, 1), const(Fraction(1, 5))),
                add(gamma(0, 1), const(Fraction(-22, 105))),
            ),
        )
        return {
            name: {key: mul(factor, value) for key, value in copied[name].items()}
            for name in COMPONENTS
        }
    if mutation == "frechet_times_parameter_y_alias_factor":
        factor = add(
            ONE,
            mul(
                add(param("y"), const(Fraction(-1, 2))),
                add(param("y"), const(Fraction(-5, 8))),
            ),
        )
        return {
            name: {key: mul(factor, value) for key, value in copied[name].items()}
            for name in COMPONENTS
        }
    if mutation == "frechet_times_tau_varphi_double_zero_factor":
        first = _fraction_witness(1)
        second = _fraction_witness(2)
        tau_zero = mul(
            add(t1(0), const(-first.T1[0])),
            add(t1(0), const(-second.T1[0])),
        )
        varphi_zero = mul(
            add(varphi(0), const(-first.varphi[0])),
            add(varphi(0), const(-second.varphi[0])),
        )
        factor = add(ONE, power(tau_zero, 2), power(varphi_zero, 2))
        return {
            name: {key: mul(factor, value) for key, value in copied[name].items()}
            for name in COMPONENTS
        }
    if mutation == "component_form_redistribution_preserving_aggregate":
        key = ("H", (), (0, 0))
        hidden = mul(
            add(gamma(0, 1), const(Fraction(1, 5))),
            add(gamma(0, 1), const(Fraction(-22, 105))),
        )
        copied["K_foliation"][key] = add(
            copied["K_foliation"].get(key, ZERO), hidden
        )
        copied["a_squared"][key] = add(
            copied["a_squared"].get(key, ZERO), mul(const(-1), hidden)
        )
    return copied


def _core(
    action: Mapping[str, str],
    *,
    mutation: str | None = None,
    repin_internal_hashes: bool = False,
) -> dict[str, Any]:
    if mutation not in {None, *CORE_MUTATIONS}:
        raise KARRawFrechetError(f"unknown core mutation {mutation}")
    program_mutations = {
        "correlated_hidden_offdiagonal_term",
        "wrong_christoffel_last_sign",
        "wrong_K_lambda_sign",
        "wrong_a_prefactor_half",
        "wrong_Robin_cross_sign",
        "wrong_Robin_prefactor_sign",
        "omit_Robin_varphi",
    }
    program = build_component_program(action, mutation=mutation if mutation in program_mutations else None)
    derivative_mutation = mutation if mutation in {
        "correlated_wrong_inverse_sign",
        "correlated_wrong_volume_half",
        "correlated_wrong_fractional_power_sign",
    } else None
    primary_forms = {
        name: frechet(expr, derivative_mutation)
        for name, expr in program.components.items()
    }
    forms = _apply_finite_witness_form_exploit(primary_forms, mutation)
    aggregate_form_preserved = _linear_forms_exact(
        _lf_add(*(primary_forms[name] for name in COMPONENTS)),
        _lf_add(*(forms[name] for name in COMPONENTS)),
    )
    symbolic, independent_program, independent_forms = (
        _exact_symbolic_semantic_certificate(
            action,
            program,
            forms,
            primary_mutation=derivative_mutation,
        )
    )
    rows = export_raw_rows(forms, program)
    roots = [coefficient for form in forms.values() for coefficient in form.values()]
    dag = export_coefficient_dag(roots)
    if mutation == "serializer_leaf_relabel_after_repin":
        def relabel_gamma_00(record: dict[str, Any]) -> None:
            if record.get("op") == "gamma" and record.get("indices") == [0, 0]:
                record["indices"] = [0, 1]

        _rewrite_exported_dag(rows, dag, relabel_gamma_00)
    hashes = {
        "component_ASTS_sha256": _canonical_sha256(
            {name: _node_hash(program.components[name]) for name in COMPONENTS}
        ),
        "raw_rows_sha256": _canonical_sha256(rows),
        "coefficient_DAG_sha256": _canonical_sha256(dag),
    }
    pin_checks = {
        "component_ASTS_pin": hashes["component_ASTS_sha256"] == EXPECTED_COMPONENT_ASTS_SHA256,
        "raw_rows_pin": hashes["raw_rows_sha256"] == EXPECTED_RAW_ROWS_SHA256,
        "coefficient_DAG_pin": hashes["coefficient_DAG_sha256"] == EXPECTED_COEFFICIENT_DAG_SHA256,
    }
    if repin_internal_hashes:
        pin_checks = {name: True for name in pin_checks}
    expr_row_dag_binding = validate_expr_row_dag_binding(
        forms, rows, dag, independent_forms
    )
    oracle = _independent_oracle_certificate(program, forms, rows, dag)
    schema_pass = validate_raw_rows(rows, dag, action)
    ready = (
        all(pin_checks.values())
        and symbolic["pass"]
        and schema_pass
        and expr_row_dag_binding
        and oracle["all_primal_components_match"]
        and oracle["all_basis_Frechet_coefficients_match"]
        and oracle["all_rational_congruence_witnesses_verified"]
    )
    return {
        "mutation": mutation,
        "internal_hashes_repinned": repin_internal_hashes,
        "program": program,
        "independent_program": independent_program,
        "forms": forms,
        "independent_forms": independent_forms,
        "aggregate_form_preserved_vs_unmutated": aggregate_form_preserved,
        "rows": rows,
        "dag": dag,
        "hashes": hashes,
        "pin_checks": pin_checks,
        "exact_symbolic_semantic_certificate": symbolic,
        "strict_schema_pass": schema_pass,
        "Expr_row_DAG_structural_binding_pass": expr_row_dag_binding,
        "independent_oracle": oracle,
        "ready": ready,
    }


def _schema_mutation_campaign(core: Mapping[str, Any], action: Mapping[str, str]) -> dict[str, bool]:
    canonical_rows = json.loads(json.dumps(core["rows"]))
    canonical_dag = json.loads(json.dumps(core["dag"]))

    def rejected(mutator: Any) -> bool:
        rows = json.loads(json.dumps(canonical_rows))
        dag = json.loads(json.dumps(canonical_dag))
        mutator(rows, dag)
        return not (
            validate_raw_rows(rows, dag, action)
            and validate_expr_row_dag_binding(
                core["independent_forms"],
                rows,
                dag,
                core["independent_forms"],
            )
        )

    def rehash_transitive(
        rows: list[dict[str, Any]],
        dag: dict[str, Any],
        target: str,
        mutate_record: Any,
    ) -> None:
        rebuilt: dict[str, dict[str, Any]] = {}
        memo: dict[str, str] = {}

        def rewrite(old: str) -> str:
            if old in memo:
                return memo[old]
            record = json.loads(json.dumps(dag[old]))
            if record["op"] in {"add", "mul"}:
                record["args"] = sorted(rewrite(child) for child in record["args"])
            elif record["op"] == "pow":
                record["arg"] = rewrite(record["arg"])
            if old == target:
                mutate_record(record)
            new = _canonical_sha256(record)
            memo[old] = new
            rebuilt[new] = record
            return new

        for row in rows:
            row["coefficient_root_sha256"] = rewrite(row["coefficient_root_sha256"])
        dag.clear()
        dag.update(rebuilt)

    def unknown_opcode(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        target = rows[0]["coefficient_root_sha256"]
        rehash_transitive(rows, dag, target, lambda record: record.__setitem__("op", "mystery"))

    def extra_node_field(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        target = rows[0]["coefficient_root_sha256"]
        rehash_transitive(rows, dag, target, lambda record: record.__setitem__("untrusted", 1))

    def bad_arity(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        target = next(key for key, value in dag.items() if value["op"] in {"add", "mul"})
        rehash_transitive(
            rows,
            dag,
            target,
            lambda record: record.__setitem__("args", record["args"][:1]),
        )

    def extra_row_field(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        rows[0]["untrusted"] = 1

    def wrong_field(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        rows[0]["field"] = "T" if rows[0]["field"] != "T" else "gamma"

    def noncanonical_indices(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        row = next(row for row in rows if row["variation"]["slot"] == "H" and row["variation"]["component_indices"][0] < row["variation"]["component_indices"][1])
        row["variation"]["component_indices"].reverse()

    def ordinal_gap(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        rows[0]["summand_ordinal"] = 999

    def source_drift(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        rows[0]["source_span"]["start"] += 1

    def swap_component_roots_and_repin(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        spans = {
            name: dict(next(row for row in rows if row["component"] == name)["source_span"])
            for name in ("K_foliation", "a_squared")
        }
        for row in rows:
            if row["component"] == "K_foliation":
                row["component"] = "a_squared"
                row["source_span"] = spans["a_squared"]
            elif row["component"] == "a_squared":
                row["component"] = "K_foliation"
                row["source_span"] = spans["K_foliation"]
        order = {name: index for index, name in enumerate(COMPONENTS)}
        rows.sort(key=lambda row: (order[row["component"]], row["summand_ordinal"]))

    def swap_roots_within_component(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        component_rows = [row for row in rows if row["component"] == "Robin"]
        component_rows[0]["coefficient_root_sha256"], component_rows[1]["coefficient_root_sha256"] = (
            component_rows[1]["coefficient_root_sha256"],
            component_rows[0]["coefficient_root_sha256"],
        )

    def interleave_global_component_order(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        rows.sort(key=lambda row: (row["summand_ordinal"], row["component"]))

    def swap_exported_variation_labels(rows: list[dict[str, Any]], dag: dict[str, Any]) -> None:
        del dag
        for component in COMPONENTS:
            component_rows = sorted(
                (row for row in rows if row["component"] == component),
                key=lambda row: row["summand_ordinal"],
            )
            component_rows[0]["variation"], component_rows[1]["variation"] = (
                component_rows[1]["variation"],
                component_rows[0]["variation"],
            )

    return {
        "unknown_opcode_rejected_after_rehash": rejected(unknown_opcode),
        "extra_node_field_rejected_after_rehash": rejected(extra_node_field),
        "bad_opcode_arity_rejected_after_rehash": rejected(bad_arity),
        "extra_row_field_rejected": rejected(extra_row_field),
        "slot_field_mismatch_rejected": rejected(wrong_field),
        "noncanonical_tensor_indices_rejected": rejected(noncanonical_indices),
        "noncontiguous_component_ordinal_rejected": rejected(ordinal_gap),
        "literal_source_span_drift_rejected": rejected(source_drift),
        "component_root_and_span_swap_rejected_after_repin": rejected(swap_component_roots_and_repin),
        "within_component_root_swap_rejected": rejected(swap_roots_within_component),
        "global_component_interleave_rejected": rejected(interleave_global_component_order),
        "swap_exported_variation_labels_after_repin_rejected": rejected(
            swap_exported_variation_labels
        ),
    }


FALSE_SCOPE = {
    "remaining_seventeen_components_raw_Frechet_pass": False,
    "all_twenty_components_semantic_Frechet_pass": False,
    "horizontal_varphi_H_constraint_preservation_pass": False,
    "frame_and_SO3_groupoid_Robin_variation_pass": False,
    "formal_adjoint_or_Euler_coefficients_pass": False,
    "intrinsic_d4_Green_current_pass": False,
    "full_off_shell_Green_identity_pass": False,
    "bulk_GHY_interface_assembly_pass": False,
    "moving_embedding_or_shape_derivative_pass": False,
    "full_classical_variational_principle_selected_sector_pass": False,
    "C1_ACTION_pass": False,
    "N1_ACTION_pass": False,
    "B4_pass": False,
    "B5_pass": False,
    "publication_authorized": False,
}


def bootstrap_hashes() -> dict[str, Any]:
    action, _ = certify_dependencies()
    # Bypass only the equality to the not-yet-filled constants.  Algebra,
    # schemas, and independent oracle remain executed.
    core = _core(action, repin_internal_hashes=True)
    return {
        "semantic_completion_sha256": _canonical_sha256(SEMANTIC_COMPLETION),
        **core["hashes"],
        "strict_schema_pass": core["strict_schema_pass"],
        "Expr_row_DAG_structural_binding_pass": core[
            "Expr_row_DAG_structural_binding_pass"
        ],
        "independent_oracle_pass": (
            core["independent_oracle"]["all_primal_components_match"]
            and core["independent_oracle"]["all_basis_Frechet_coefficients_match"]
            and core["independent_oracle"][
                "all_rational_congruence_witnesses_verified"
            ]
        ),
        "row_count": len(core["rows"]),
        "DAG_node_count": len(core["dag"]),
    }


def build_report() -> dict[str, Any]:
    action, lineage = certify_dependencies()
    semantic_hash = _canonical_sha256(SEMANTIC_COMPLETION)
    core = _core(action)
    schema_mutations = _schema_mutation_campaign(core, action)
    correlated: dict[str, Any] = {}
    for mutation in CORE_MUTATIONS:
        attacked = _core(action, mutation=mutation, repin_internal_hashes=True)
        correlated[mutation] = {
            "internal_hashes_repinned": all(attacked["pin_checks"].values()),
            "exact_symbolic_semantic_pass": attacked[
                "exact_symbolic_semantic_certificate"
            ]["pass"],
            "literal_component_roots_bound": attacked[
                "exact_symbolic_semantic_certificate"
            ]["component_roots_bound_to_literal_program"],
            "strict_schema_pass": attacked["strict_schema_pass"],
            "aggregate_form_preserved_vs_unmutated": attacked[
                "aggregate_form_preserved_vs_unmutated"
            ],
            "Expr_row_DAG_structural_binding_pass": attacked[
                "Expr_row_DAG_structural_binding_pass"
            ],
            "primal_oracle_pass": attacked["independent_oracle"]["all_primal_components_match"],
            "Frechet_oracle_pass": attacked["independent_oracle"]["all_basis_Frechet_coefficients_match"],
            "ready_after_repin": attacked["ready"],
            "mismatch_examples": attacked["independent_oracle"]["mismatch_examples"][:2],
        }
    orientation = _orientation_invariance_certificate(action)
    orientation_odd_attack = _orientation_invariance_certificate(
        action, mutation="orientation_odd_hidden_term"
    )
    orientation_double_zero_attack = _orientation_invariance_certificate(
        action, mutation="orientation_odd_double_zero"
    )
    finite_locus_names = (
        "frechet_times_finite_gamma_factor",
        "frechet_times_parameter_y_alias_factor",
        "frechet_times_tau_varphi_double_zero_factor",
        "component_form_redistribution_preserving_aggregate",
    )
    mandatory_finite_locus_exploits = {
        name: {
            "internal_hashes_repinned": correlated[name][
                "internal_hashes_repinned"
            ],
            "finite_witness_oracle_pass": (
                correlated[name]["primal_oracle_pass"]
                and correlated[name]["Frechet_oracle_pass"]
            ),
            "exact_symbolic_semantic_pass": correlated[name][
                "exact_symbolic_semantic_pass"
            ],
            "independent_route_binding_pass": correlated[name][
                "Expr_row_DAG_structural_binding_pass"
            ],
            "strict_schema_pass": correlated[name]["strict_schema_pass"],
            "aggregate_form_preserved_vs_unmutated": correlated[name][
                "aggregate_form_preserved_vs_unmutated"
            ],
            "ready_after_repin": correlated[name]["ready_after_repin"],
        }
        for name in finite_locus_names
    }
    mandatory_finite_locus_exploits["orientation_odd_double_zero"] = {
        "internal_hashes_repinned": orientation_double_zero_attack[
            "repinned_export_pipeline"
        ]["all_internal_hashes_repinned"],
        "finite_witness_oracle_pass": orientation_double_zero_attack[
            "repinned_export_pipeline"
        ]["finite_witness_oracle_pass"],
        "exact_symbolic_semantic_pass": orientation_double_zero_attack[
            "universal_symbolic_invariance"
        ],
        "independent_route_binding_pass": orientation_double_zero_attack[
            "repinned_export_pipeline"
        ]["all_independent_row_DAG_bindings_pass"],
        "strict_schema_pass": orientation_double_zero_attack[
            "repinned_export_pipeline"
        ]["all_strict_schema_pass"],
        "aggregate_form_preserved_vs_unmutated": None,
        "ready_after_repin": orientation_double_zero_attack[
            "repinned_export_pipeline"
        ]["ready_after_repin"],
    }
    mandatory_finite_locus_exploit_pass = all(
        row["internal_hashes_repinned"]
        and row["finite_witness_oracle_pass"]
        and not row["exact_symbolic_semantic_pass"]
        and not row["independent_route_binding_pass"]
        and row["strict_schema_pass"] is True
        and not row["ready_after_repin"]
        and (
            name != "component_form_redistribution_preserving_aggregate"
            or row["aggregate_form_preserved_vs_unmutated"] is True
        )
        for name, row in mandatory_finite_locus_exploits.items()
    )
    keys_by_component = {
        name: {
            "row_count": len(core["forms"][name]),
            "slots": sorted({key[0] for key in core["forms"][name]}),
            "maximum_derivative_order": max(len(key[1]) for key in core["forms"][name]),
        }
        for name in COMPONENTS
    }
    component_root_sets = {
        name: {
            row["coefficient_root_sha256"]
            for row in core["rows"]
            if row["component"] == name
        }
        for name in COMPONENTS
    }
    checks = {
        "S8_S9_S10_source_and_test_dependencies_byte_pinned": lineage["observed_source_test_sha256"] == PINNED_INPUTS,
        "literal_v5_2_K_a_Robin_occurrences_exactly_bound": all(
            action[row["action_key"]][row["start"] : row["end"]] == row["text"]
            for row in core["program"].source_spans.values()
        ),
        "semantic_completion_live_snapshot_and_pin_match": semantic_hash == EXPECTED_SEMANTIC_COMPLETION_SHA256,
        "stage_is_raw_Frechet_not_post_adjoint": SEMANTIC_COMPLETION["stage"] == "raw_Frechet_before_formal_adjoint",
        "exactly_three_component_program_with_separate_roots": (
            tuple(core["program"].components) == COMPONENTS
            and {name: len(component_root_sets[name]) for name in COMPONENTS}
            == EXPECTED_ROW_COUNTS
            and all(
                component_root_sets[left].isdisjoint(component_root_sets[right])
                for index, left in enumerate(COMPONENTS)
                for right in COMPONENTS[index + 1 :]
            )
        ),
        "component_program_rows_and_DAG_match_canonical_pins": all(core["pin_checks"].values()),
        "component_roots_and_complete_forms_match_independent_literal_context_derivation": (
            core["exact_symbolic_semantic_certificate"]["pass"]
        ),
        "strict_exhaustive_opcode_field_arity_and_row_schema_pass": core["strict_schema_pass"],
        "every_Expr_row_root_decodes_back_to_the_same_symbolic_coefficient": core[
            "Expr_row_DAG_structural_binding_pass"
        ],
        "all_raw_coefficients_match_independent_exact_dual_oracle_at_two_explicit_witnesses": (
            core["independent_oracle"]["all_primal_components_match"]
            and core["independent_oracle"]["all_basis_Frechet_coefficients_match"]
            and core["independent_oracle"][
                "all_rational_congruence_witnesses_verified"
            ]
        ),
        "field_orders_match_K_a_Robin_literal_dependency_orders": keys_by_component == {
            "K_foliation": {"row_count": 64, "slots": ["H", "tau"], "maximum_derivative_order": 2},
            "a_squared": {"row_count": 64, "slots": ["H", "tau"], "maximum_derivative_order": 2},
            "Robin": {"row_count": 68, "slots": ["H", "tau", "v"], "maximum_derivative_order": 2},
        },
        "all_correlated_and_formula_mutants_fail_even_after_internal_repin": all(
            row["internal_hashes_repinned"] and not row["ready_after_repin"]
            and (
                not row["exact_symbolic_semantic_pass"]
                or not row["Expr_row_DAG_structural_binding_pass"]
                or not row["primal_oracle_pass"]
                or not row["Frechet_oracle_pass"]
            )
            for row in correlated.values()
        ),
        "all_strict_schema_mutants_rejected": all(schema_mutations.values()),
        "quadratic_time_orientation_invariance_recorded_without_selecting_orientation": (
            orientation["universal_symbolic_invariance"]
            and orientation["exact_rational_invariance"]
            and orientation["orientation_selected_by_this_gate"] is False
        ),
        "orientation_odd_builder_mutant_is_killed_by_AST_and_oracle_comparison": (
            orientation_odd_attack["universal_symbolic_invariance"] is False
        ),
        "orientation_odd_double_zero_mutant_is_killed_symbolically_despite_finite_witness_pass": (
            orientation_double_zero_attack["universal_symbolic_invariance"] is False
            and orientation_double_zero_attack["exact_rational_invariance"] is True
        ),
        "five_finite_locus_and_aggregate_exploits_fail_symbolically_after_repin": (
            mandatory_finite_locus_exploit_pass
        ),
        "no_artifact_output_path_or_writer_declared": "OUTPUT" not in globals(),
    }
    checks["all"] = all(checks.values())
    if checks["all"] is not True:
        failed = sorted(key for key, value in checks.items() if not value)
        raise KARRawFrechetError(
            "v5.6.7.13 narrow checks did not close: " + ", ".join(failed)
        )
    decision = {
        "fixed_domain_K_a_Robin_semantic_completion_pinned_pass": True,
        "K_a_Robin_raw_Frechet_exact_under_displayed_completion_pass": True,
        "strict_RawFrechetRowV1_export_pass": True,
        "time_orientation_selected_by_K_a_Robin_even_densities_pass": False,
        **FALSE_SCOPE,
    }
    return {
        "schema": SCHEMA,
        "lineage": lineage,
        "semantic_completion": json.loads(json.dumps(SEMANTIC_COMPLETION)),
        "semantic_completion_sha256": semantic_hash,
        "scope": {
            "included_components": list(COMPONENTS),
            "stage": "raw Frechet before formal adjoint",
            "claim": "D of exactly the K, a-squared, and Robin literal fixed-domain densities under the displayed coordinate completion",
            "not_claimed": "horizontal/groupoid Robin, remaining components, adjoint/Green, assembly, shape, C1, or N1",
        },
        "component_certificate": keys_by_component,
        "aggregate_hashes": core["hashes"],
        "RawFrechetRowV1": core["rows"],
        "coefficient_DAG": core["dag"],
        "exact_symbolic_semantic_certificate": core[
            "exact_symbolic_semantic_certificate"
        ],
        "independent_exact_oracle": core["independent_oracle"],
        "orientation_invariance": orientation,
        "orientation_odd_mutation_probe": orientation_odd_attack,
        "orientation_odd_double_zero_mutation_probe": orientation_double_zero_attack,
        "mandatory_finite_locus_exploit_certificate": {
            "pass": mandatory_finite_locus_exploit_pass,
            "witness_role": (
                "finite exact regressions deliberately pass these exploits; "
                "the universal formal certificate rejects them"
            ),
            "rows": mandatory_finite_locus_exploits,
        },
        "correlated_repin_mutation_campaign": correlated,
        "strict_schema_mutation_campaign": schema_mutations,
        "checks": checks,
        "decision": decision,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", action="store_true", help="print observed canonical hashes before freezing constants")
    args = parser.parse_args(argv)
    payload = bootstrap_hashes() if args.bootstrap else build_report()
    print(json.dumps(_jsonable(payload), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
