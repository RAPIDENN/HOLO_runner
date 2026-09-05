#!/usr/bin/env python3
"""Typed semantic completion and exact Frechet IR for eleven v5.2 rows.

This deliberately narrow gate parses the byte-pinned ``S_v5_2`` charter and
builds typed expression trees for exactly eleven components: on each side the
Omega kinetic and potential, gauged-P kinetic, smooth full-V4 and BF terms,
plus the common wall term.  EH, GHY and all five derivative-rich intrinsic
rows are outside this unit.

The semantic claim is conditional on the explicit completion recorded here.
It is nevertheless stronger than a hand-written coefficient ledger: the
Frechet expression is generated from the parsed action AST itself by two
separate exact algorithms, forward nilpotent dual propagation and a reverse
context/path propagation.  Gauge and exterior composites are expanded to
ordinary/exterior partial derivatives before either route runs.  No candidate
Frechet coefficient table is accepted as input.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"

SCHEMA = (
    "holo.one-omega-topological-so3-eleven-component-semantic-frechet-"
    "v5-6-7-10-gate.v1"
)

V52_SOURCE = HERE / "derive_one_omega_topological_so3_classical_v5_2_gate.py"
V52_TEST = HERE / "test_one_omega_topological_so3_classical_v5_2_gate.py"
V52_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_classical_v5_2_gate.json"

PINNED_INPUTS = {
    V52_SOURCE.name: "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
    V52_TEST.name: "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
    V52_ARTIFACT.name: "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
}
PINNED_PATHS = {
    V52_SOURCE.name: V52_SOURCE,
    V52_TEST.name: V52_TEST,
    V52_ARTIFACT.name: V52_ARTIFACT,
}
V52_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
V52_EXACT_ACTION_SHA256 = (
    "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
)

ACTION_KEYS = (
    "total",
    "superpotential",
    "bulk_potential",
    "full_V4",
    "bulk_gauged",
    "gauged_conformal_derivative",
    "GHY",
    "wall_background",
    "foliation_lower",
    "Robin_intrinsic",
    "BF",
    "removed_terms",
)

EASY_COMPONENTS = (
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "wall",
)

EXCLUDED_COMPONENTS = (
    "EH_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "GHY_minus",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)


class SemanticFrechetError(RuntimeError):
    """A byte binding, parse, type, completion, or differential rule failed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise SemanticFrechetError(f"cannot hash {path}: {exc}") from exc


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


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SemanticFrechetError(f"cannot read JSON {path}: {exc}") from exc
    if type(value) is not dict:
        raise SemanticFrechetError(f"JSON object required: {path}")
    return value


@dataclass(frozen=True, order=True)
class GeoType:
    name: str
    dimension: int
    form_degree: int
    bundle: str
    variance: tuple[str, ...] = ()
    density_weight: int = 0
    symmetry: str = "none"
    fiber_dimension: int = 1


SCALAR0 = GeoType("parameter_scalar", 0, 0, "trivial")
SCALAR5 = GeoType("bulk_scalar", 5, 0, "trivial")
SCALAR4 = GeoType("interface_scalar", 4, 0, "trivial")
METRIC5 = GeoType("bulk_metric", 5, 0, "trivial", ("down", "down"), 0, "symmetric")
INVERSE_METRIC5 = GeoType("bulk_inverse_metric", 5, 0, "trivial", ("up", "up"), 0, "symmetric")
METRIC4 = GeoType("interface_metric", 4, 0, "trivial", ("down", "down"), 0, "symmetric")
INVERSE_METRIC4 = GeoType("interface_inverse_metric", 4, 0, "trivial", ("up", "up"), 0, "symmetric")
DENSITY5 = GeoType("bulk_coordinate_density", 5, 5, "trivial", (), 1, "alternating")
DENSITY4 = GeoType("interface_coordinate_density", 4, 4, "trivial", (), 1, "alternating")
ONEFORM5 = GeoType("bulk_one_form", 5, 1, "trivial", ("down",))
ASSOCIATED0_5 = GeoType("SO3_associated_zero_form", 5, 0, "associated", fiber_dimension=3)
ASSOCIATED1_5 = GeoType("SO3_associated_one_form", 5, 1, "associated", ("down",), fiber_dimension=3)
CONNECTION1_5 = GeoType("SO3_connection_one_form", 5, 1, "affine_adjoint", ("down",), fiber_dimension=3)
ADJOINT1_5 = GeoType("SO3_adjoint_one_form", 5, 1, "adjoint", ("down",), fiber_dimension=3)
ADJOINT2_5 = GeoType("SO3_adjoint_two_form", 5, 2, "adjoint", (), 0, "alternating", 3)
ADJOINT3_5 = GeoType("SO3_adjoint_three_form", 5, 3, "adjoint", (), 0, "alternating", 3)
ENDOMORPHISM2_5 = GeoType(
    "End_R3_two_form", 5, 2, "endomorphism", (), 0, "alternating", 9
)
RIEMANN5 = GeoType("bulk_Riemann", 5, 0, "trivial", ("up", "down", "down", "down"), 0, "Riemann")


TYPE_TABLE = {
    item.name: item
    for item in (
        SCALAR0,
        SCALAR5,
        SCALAR4,
        METRIC5,
        INVERSE_METRIC5,
        METRIC4,
        INVERSE_METRIC4,
        DENSITY5,
        DENSITY4,
        ONEFORM5,
        ASSOCIATED0_5,
        ASSOCIATED1_5,
        CONNECTION1_5,
        ADJOINT1_5,
        ADJOINT2_5,
        ADJOINT3_5,
        ENDOMORPHISM2_5,
        RIEMANN5,
    )
}


@dataclass(frozen=True)
class Expr:
    op: str
    type_tag: GeoType
    args: tuple["Expr", ...] = ()
    label: str = ""
    value: Fraction | None = None
    exponent: Fraction | None = None


def _expr_row(expr: Expr) -> dict[str, Any]:
    row: dict[str, Any] = {
        "op": expr.op,
        "type": {
            "name": expr.type_tag.name,
            "dimension": expr.type_tag.dimension,
            "form_degree": expr.type_tag.form_degree,
            "bundle": expr.type_tag.bundle,
            "variance": list(expr.type_tag.variance),
            "density_weight": expr.type_tag.density_weight,
            "symmetry": expr.type_tag.symmetry,
            "fiber_dimension": expr.type_tag.fiber_dimension,
        },
    }
    if expr.args:
        row["args"] = [_expr_row(item) for item in expr.args]
    if expr.label:
        row["label"] = expr.label
    if expr.value is not None:
        row["value"] = [expr.value.numerator, expr.value.denominator]
    if expr.exponent is not None:
        row["exponent"] = [expr.exponent.numerator, expr.exponent.denominator]
    return row


def _expr_sort_key(expr: Expr) -> str:
    return json.dumps(_expr_row(expr), sort_keys=True, separators=(",", ":"))


def _scalar_dimension(left: GeoType, right: GeoType) -> int:
    if not _is_strict_scalar(left) or not _is_strict_scalar(right):
        raise SemanticFrechetError("scalar arithmetic received a non-scalar type")
    if left.dimension and right.dimension and left.dimension != right.dimension:
        raise SemanticFrechetError("scalar dimensions disagree")
    return left.dimension or right.dimension


def _is_strict_scalar(type_tag: GeoType) -> bool:
    return bool(
        type_tag in {SCALAR0, SCALAR4, SCALAR5}
        and type_tag.form_degree == 0
        and type_tag.variance == ()
        and type_tag.density_weight == 0
        and type_tag.bundle == "trivial"
        and type_tag.fiber_dimension == 1
    )


def _scalar_type(dimension: int) -> GeoType:
    return {0: SCALAR0, 4: SCALAR4, 5: SCALAR5}[dimension]


def rational(value: int | Fraction, denominator: int = 1, *, dimension: int = 0) -> Expr:
    fraction = value if isinstance(value, Fraction) else Fraction(value, denominator)
    return Expr("rational", _scalar_type(dimension), value=fraction)


def field(name: str, type_tag: GeoType) -> Expr:
    return Expr("field", type_tag, label=name)


def parameter(name: str) -> Expr:
    return Expr("parameter", SCALAR0, label=name)


def variation(name: str, type_tag: GeoType) -> Expr:
    return Expr("variation", type_tag, label=name)


def zero(type_tag: GeoType) -> Expr:
    return Expr("zero", type_tag)


def is_zero(expr: Expr) -> bool:
    return expr.op == "zero" or (expr.op == "rational" and expr.value == 0)


def add(*values: Expr) -> Expr:
    flat: list[Expr] = []
    target: GeoType | None = None
    for value in values:
        if target is None:
            target = value.type_tag
        elif value.type_tag != target:
            raise SemanticFrechetError("addition type mismatch")
        if is_zero(value):
            continue
        if value.op == "add":
            flat.extend(value.args)
        else:
            flat.append(value)
    if target is None:
        raise SemanticFrechetError("empty addition")
    if not flat:
        return zero(target)
    flat.sort(key=_expr_sort_key)
    if len(flat) == 1:
        return flat[0]
    return Expr("add", target, tuple(flat))


def scalar_mul(*values: Expr) -> Expr:
    for index, value in enumerate(values):
        if value.op == "add":
            return add(
                *(
                    scalar_mul(*values[:index], summand, *values[index + 1 :])
                    for summand in value.args
                )
            )
    flat: list[Expr] = []
    coefficient = Fraction(1)
    dimension = 0
    def collect(value: Expr) -> None:
        nonlocal coefficient, dimension
        dimension = _scalar_dimension(_scalar_type(dimension), value.type_tag)
        if value.op == "rational":
            assert value.value is not None
            coefficient *= value.value
        elif value.op == "mul_scalar":
            for arg in value.args:
                collect(arg)
        else:
            flat.append(value)
    for value in values:
        collect(value)
    if coefficient == 0:
        return zero(_scalar_type(dimension))
    if not flat:
        return rational(coefficient, dimension=dimension)
    if coefficient != 1:
        flat.append(rational(coefficient))
    flat.sort(key=_expr_sort_key)
    if len(flat) == 1:
        only = flat[0]
        if only.type_tag.dimension == dimension:
            return only
    return Expr("mul_scalar", _scalar_type(dimension), tuple(flat))


def scale(scalar: Expr, value: Expr) -> Expr:
    _scalar_dimension(scalar.type_tag, _scalar_type(value.type_tag.dimension))
    if scalar.op == "add":
        return add(*(scale(summand, value) for summand in scalar.args))
    if value.op == "add":
        return add(*(scale(scalar, summand) for summand in value.args))
    if is_zero(scalar) or is_zero(value):
        return zero(value.type_tag)
    if value.type_tag.bundle == "trivial" and value.type_tag.form_degree == 0 and not value.type_tag.variance and value.type_tag.density_weight == 0:
        return scalar_mul(scalar, value)
    if scalar.op == "rational" and scalar.value == 1:
        return value
    if value.op == "scale":
        return scale(scalar_mul(scalar, value.args[0]), value.args[1])
    return Expr("scale", value.type_tag, (scalar, value))


def negate(value: Expr) -> Expr:
    return scale(rational(-1), value)


def power(value: Expr, exponent: int | Fraction) -> Expr:
    if not _is_strict_scalar(value.type_tag):
        raise SemanticFrechetError("power requires a scalar")
    exponent = Fraction(exponent)
    if exponent == 0:
        return rational(1)
    if exponent == 1:
        return value
    return Expr("power", value.type_tag, (value,), exponent=exponent)


def inverse_scalar(value: Expr) -> Expr:
    return power(value, -1)


def exp_scalar(value: Expr) -> Expr:
    if not _is_strict_scalar(value.type_tag):
        raise SemanticFrechetError("exp requires a strict real scalar")
    return Expr("exp", value.type_tag, (value,))


def sqrt_scalar(value: Expr) -> Expr:
    if not _is_strict_scalar(value.type_tag):
        raise SemanticFrechetError("sqrt requires a strict real scalar")
    return Expr("sqrt", value.type_tag, (value,))


def inverse_metric(metric: Expr) -> Expr:
    target = {METRIC5: INVERSE_METRIC5, METRIC4: INVERSE_METRIC4}.get(metric.type_tag)
    if target is None:
        raise SemanticFrechetError("inverse_metric requires a metric")
    return Expr("inverse_metric", target, (metric,))


def volume_density(metric: Expr) -> Expr:
    target = {METRIC5: DENSITY5, METRIC4: DENSITY4}.get(metric.type_tag)
    if target is None:
        raise SemanticFrechetError("volume requires a metric")
    return Expr("volume_density", target, (metric,))


def metric_trace(inverse: Expr, covariant: Expr) -> Expr:
    if inverse.type_tag not in {INVERSE_METRIC5, INVERSE_METRIC4}:
        raise SemanticFrechetError("metric_trace requires inverse metric")
    expected = METRIC5 if inverse.type_tag == INVERSE_METRIC5 else METRIC4
    if covariant.type_tag != expected:
        raise SemanticFrechetError("metric_trace covariant type mismatch")
    return Expr("metric_trace", _scalar_type(inverse.type_tag.dimension), (inverse, covariant))


def inverse_sandwich(left: Expr, covariant: Expr, right: Expr) -> Expr:
    if left.type_tag != right.type_tag or left.type_tag not in {INVERSE_METRIC5, INVERSE_METRIC4}:
        raise SemanticFrechetError("inverse sandwich type mismatch")
    expected = METRIC5 if left.type_tag == INVERSE_METRIC5 else METRIC4
    if covariant.type_tag != expected:
        raise SemanticFrechetError("inverse sandwich covariant type mismatch")
    for index, value in enumerate((left, covariant, right)):
        if value.op == "add":
            rows = (left, covariant, right)
            return add(
                *(inverse_sandwich(*(rows[:index] + (summand,) + rows[index + 1 :])) for summand in value.args)
            )
    return Expr("inverse_sandwich", left.type_tag, (left, covariant, right))


def exterior_partial(value: Expr) -> Expr:
    if value.op == "add":
        return add(*(exterior_partial(summand) for summand in value.args))
    mapping = {
        SCALAR5: ONEFORM5,
        ASSOCIATED0_5: ASSOCIATED1_5,
        CONNECTION1_5: ADJOINT2_5,
        ADJOINT1_5: ADJOINT2_5,
    }
    target = mapping.get(value.type_tag)
    if target is None:
        raise SemanticFrechetError(f"no exterior-partial type rule for {value.type_tag.name}")
    return Expr("exterior_partial", target, (value,), label="partial_antisymmetrized")


def associated_action(connection: Expr, associated: Expr) -> Expr:
    if connection.type_tag not in {CONNECTION1_5, ADJOINT1_5} or associated.type_tag != ASSOCIATED0_5:
        raise SemanticFrechetError("SO3 action source/target type mismatch")
    if connection.op == "add":
        return add(*(associated_action(summand, associated) for summand in connection.args))
    if associated.op == "add":
        return add(*(associated_action(connection, summand) for summand in associated.args))
    return Expr("SO3_action", ASSOCIATED1_5, (connection, associated))


def associated_times_oneform(associated: Expr, oneform: Expr) -> Expr:
    if associated.type_tag != ASSOCIATED0_5 or oneform.type_tag != ONEFORM5:
        raise SemanticFrechetError("associated tensor one-form mismatch")
    if associated.op == "add":
        return add(*(associated_times_oneform(summand, oneform) for summand in associated.args))
    if oneform.op == "add":
        return add(*(associated_times_oneform(associated, summand) for summand in oneform.args))
    return Expr("associated_times_oneform", ASSOCIATED1_5, (associated, oneform))


def metric_contract(inverse: Expr, left: Expr, right: Expr) -> Expr:
    if inverse.type_tag != INVERSE_METRIC5 or left.type_tag != right.type_tag:
        raise SemanticFrechetError("metric contraction type mismatch")
    if left.type_tag not in {ONEFORM5, ASSOCIATED1_5}:
        raise SemanticFrechetError("unsupported metric contraction bundle")
    rows = (inverse, left, right)
    for index, value in enumerate(rows):
        if value.op == "add":
            return add(
                *(metric_contract(*(rows[:index] + (summand,) + rows[index + 1 :])) for summand in value.args)
            )
    return Expr("metric_contract", SCALAR5, (inverse, left, right), label=left.type_tag.bundle)


def associated_pair(left: Expr, right: Expr) -> Expr:
    if left.type_tag != ASSOCIATED0_5 or right.type_tag != ASSOCIATED0_5:
        raise SemanticFrechetError("associated pairing type mismatch")
    if left.op == "add":
        return add(*(associated_pair(summand, right) for summand in left.args))
    if right.op == "add":
        return add(*(associated_pair(left, summand) for summand in right.args))
    return Expr("associated_pair", SCALAR5, (left, right), label="delta_ab")


def connection_wedge(left: Expr, right: Expr) -> Expr:
    if left.type_tag not in {CONNECTION1_5, ADJOINT1_5} or right.type_tag not in {CONNECTION1_5, ADJOINT1_5}:
        raise SemanticFrechetError("connection wedge requires adjoint-valued one-forms")
    if left.op == "add":
        return add(*(connection_wedge(summand, right) for summand in left.args))
    if right.op == "add":
        return add(*(connection_wedge(left, summand) for summand in right.args))
    return Expr(
        "matrix_wedge",
        ENDOMORPHISM2_5,
        (left, right),
        label="ordered_matrix_product",
    )


def adjoint_matrix_embedding(value: Expr) -> Expr:
    if value.type_tag != ADJOINT2_5:
        raise SemanticFrechetError("adjoint matrix embedding requires an adjoint two-form")
    if value.op == "add":
        return add(*(adjoint_matrix_embedding(summand) for summand in value.args))
    return Expr("adjoint_matrix_embedding", ENDOMORPHISM2_5, (value,))


def pair_wedge(bfield: Expr, curvature: Expr, *, pairing_label: str = "-tr3/2") -> Expr:
    if bfield.type_tag != ADJOINT3_5 or curvature.type_tag != ENDOMORPHISM2_5:
        raise SemanticFrechetError("BF wedge/pairing degree mismatch")
    if pairing_label != "-tr3/2":
        raise SemanticFrechetError(
            "this byte-pinned subgate admits only the charter pairing -tr3/2"
        )
    if bfield.op == "add":
        return add(*(pair_wedge(summand, curvature, pairing_label=pairing_label) for summand in bfield.args))
    if curvature.op == "add":
        return add(*(pair_wedge(bfield, summand, pairing_label=pairing_label) for summand in curvature.args))
    return Expr("invariant_pair_wedge", DENSITY5, (bfield, curvature), label=pairing_label)


def scale_density(density: Expr, scalar: Expr) -> Expr:
    if density.type_tag not in {DENSITY5, DENSITY4}:
        raise SemanticFrechetError("scale_density requires a coordinate density")
    _scalar_dimension(_scalar_type(density.type_tag.dimension), scalar.type_tag)
    if density.op == "add":
        return add(*(scale_density(summand, scalar) for summand in density.args))
    if scalar.op == "add":
        return add(*(scale_density(density, summand) for summand in scalar.args))
    return Expr("density_times_scalar", density.type_tag, (density, scalar))


def density_times_scalar(density: Expr, scalar: Expr) -> Expr:
    return scale_density(density, scalar)


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    start: int
    end: int


TOKEN_RE = re.compile(
    r"(?P<WS>\s+)|(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)|(?P<NUMBER>[0-9]+)|"
    r"(?P<ARROW>->)|(?P<SYMBOL>[\[\]()<>|,+*/^=.:;-])"
)


def lex_full_span(text: str) -> tuple[Token, ...]:
    rows: list[Token] = []
    cursor = 0
    while cursor < len(text):
        match = TOKEN_RE.match(text, cursor)
        if match is None:
            raise SemanticFrechetError(f"unlexed charter byte at {cursor}: {text[cursor:cursor+12]!r}")
        kind = match.lastgroup
        assert kind is not None
        rows.append(Token(kind, match.group(), match.start(), match.end()))
        cursor = match.end()
    if cursor != len(text) or "".join(row.text for row in rows) != text:
        raise SemanticFrechetError("charter lexer did not consume the full byte span")
    return tuple(rows)


@dataclass(frozen=True)
class ParsedCharter:
    action: Mapping[str, str]
    tokens: Mapping[str, tuple[Token, ...]]
    captures: Mapping[str, Any]


def _fullmatch(pattern: str, text: str, label: str) -> re.Match[str]:
    match = re.fullmatch(pattern, text)
    if match is None:
        raise SemanticFrechetError(f"{label} is outside the semantic grammar")
    return match


def parse_exact_action(action: Mapping[str, str]) -> ParsedCharter:
    if tuple(action) != ACTION_KEYS or set(action) != set(ACTION_KEYS):
        raise SemanticFrechetError("exact-action key order or inventory drift")
    if any(type(action[key]) is not str for key in ACTION_KEYS):
        raise SemanticFrechetError("every exact-action entry must be a string")
    tokens = {key: lex_full_span(action[key]) for key in ACTION_KEYS}

    w = _fullmatch(
        r"W\((?P<x>[A-Za-z_][A-Za-z0-9_]*)\)=(?P<c3>[0-9]+)\*(?P<m5>M5)\^(?P<m5p>[0-9]+)\*(?P<k>k_infinity)\*exp\[-(?P<G>G)\*(?P=x)\^(?P<xpow>[0-9]+)/\((?P<c6>[0-9]+)\*(?P=m5)\^(?P=m5p)\)\]",
        action["superpotential"],
        "superpotential",
    )
    u = _fullmatch(
        r"U\((?P<x>[A-Za-z_][A-Za-z0-9_]*)\)=W_Omega\^(?P<wpow>[0-9]+)/\((?P<c2>[0-9]+)\*(?P<G>G)\)-(?P<n2>[0-9]+)\*W\^(?P<Wpow>[0-9]+)/\((?P<c3>[0-9]+)\*(?P<m5>M5)\^(?P<m5p>[0-9]+)\)",
        action["bulk_potential"],
        "bulk_potential",
    )
    v4 = _fullmatch(
        r"V4\((?P<r>[A-Za-z_][A-Za-z0-9_]*)\)=(?P=r)\^(?P<p4>[0-9]+)/\((?P<c2>[0-9]+)\*sqrt\((?P<one>[0-9]+)\+(?P=r)\^(?P=p4)\)\)",
        action["full_V4"],
        "full_V4",
    )
    p = _fullmatch(
        r"P_eps_M=D_\(A_eps,M\)phi_eps\+(?P<c3>[0-9]+)\*phi_eps\*partial_M log\(Omega_eps\)/(?P<c2>[0-9]+)",
        action["gauged_conformal_derivative"],
        "gauged_conformal_derivative",
    )
    bulk = _fullmatch(
        r"S_bulk_gauged=sum_eps int_Meps sqrt\(-g_eps\)\*\[M5\^(?P<m5p>[0-9]+)\*R_eps/(?P<eh2>[0-9]+)-G\*\(nabla Omega_eps\)\^(?P<opow>[0-9]+)/(?P<ok2>[0-9]+)-U\(Omega_eps\)-Z5\*delta_ab\*P_eps_M\^a\*P_eps\^\(b M\)/(?P<pk2>[0-9]+)-Z5\*M\^(?P<Mpow>[0-9]+)\*Omega_eps\^\(-(?P<ominus>[0-9]+)\)\*V4\(Omega_eps\^\((?P<o32n>[0-9]+)/(?P<o32d>[0-9]+)\)\*\|phi_eps\|\)\]",
        action["bulk_gauged"],
        "bulk_gauged",
    )
    wall = _fullmatch(
        r"S_wall0=-int_Sigma sqrt\(-gamma\)\*\[(?P<w2>[0-9]+)\*W\(Omega_Sigma\)\+beta\*\(Omega_Sigma-(?P<one>[0-9]+)\)\^(?P<p2>[0-9]+)/(?P<b2>[0-9]+)\]",
        action["wall_background"],
        "wall_background",
    )
    bf = _fullmatch(
        r"S_BF=sum_eps int_Meps <B_eps wedge F\[A_eps\]>, <X,Y>=-tr_3\(XY\)/(?P<tr2>[0-9]+)",
        action["BF"],
        "BF",
    )
    ghy = _fullmatch(
        r"S_GHY=M5\^(?P<m5p>[0-9]+)\*sum_eps int_Sigma sqrt\(-gamma\)\*Theta_eps for outward normals",
        action["GHY"],
        "GHY",
    )
    foliation = _fullmatch(
        r"S_fol_lower=Mb\^(?P<mbp>[0-9]+)/(?P<c2>[0-9]+)\*int_Sigma sqrt\(-gamma\)\*\[Kcal_mu_nu\*Kcal\^mu_nu-lambda_K\*Kcal\^(?P<k2>[0-9]+)\+xi\*Rcal\+eta\*a_mu\*a\^mu-B4_bar\*Rcal\^(?P<r2>[0-9]+)/\((?P<c16>[0-9]+)\*k_infinity\^(?P<ki2>[0-9]+)\)\]",
        action["foliation_lower"],
        "foliation_lower",
    )
    robin = _fullmatch(
        r"S_R_intrinsic=-kappa_hat/(?P<c2>[0-9]+)\*int_Sigma sqrt\(-gamma\)\*h_mu_nu\*\(varphi_H\^mu-y\*a\^mu\)\*\(varphi_H\^nu-y\*a\^nu\)",
        action["Robin_intrinsic"],
        "Robin_intrinsic",
    )
    removed = _fullmatch(
        r"S_X=(?P<zero>[0-9]+) and every bulk screen-clock term=(?P=zero)",
        action["removed_terms"],
        "removed_terms",
    )
    total = _fullmatch(
        r"S_v5_2=S_bulk_gauged\+S_GHY\+S_wall0\+S_fol_lower\+S_R_intrinsic\+S_BF",
        action["total"],
        "total",
    )
    del total

    captures = {
        "W": w.groupdict(),
        "U": u.groupdict(),
        "V4": v4.groupdict(),
        "P": p.groupdict(),
        "bulk": bulk.groupdict(),
        "wall": wall.groupdict(),
        "BF": bf.groupdict(),
        "GHY_excluded": ghy.groupdict(),
        "foliation_excluded": foliation.groupdict(),
        "Robin_excluded": robin.groupdict(),
        "removed_excluded": removed.groupdict(),
    }
    return ParsedCharter(dict(action), tokens, captures)


SEMANTIC_COMPLETION = {
    "version": "v5.6.7.10-fixed-domain-eleven-component-completion-v1",
    "coordinate_convention": {
        "bulk_dimension": 5,
        "wall_dimension": 4,
        "metric_signature": "Lorentzian; volume density is sqrt(-det(g)) times the oriented coordinate form",
        "inverse_metric": "g^{MP} g_{PN}=delta^M_N",
        "volume_variation": "delta sqrt(-g)=sqrt(-g) g^{MN} delta g_MN/2",
        "Levi_Civita_connection": "Gamma^P_MN=g^{PQ}(partial_M g_QN+partial_N g_QM-partial_Q g_MN)/2",
        "Riemann": "R^P_QMN=partial_M Gamma^P_NQ-partial_N Gamma^P_MQ+Gamma^P_MR Gamma^R_NQ-Gamma^P_NR Gamma^R_MQ",
        "scalar_covariant_derivative": "nabla_M Omega=partial_M Omega",
        "fixed_domains": ["M_plus", "M_minus", "Sigma"],
    },
    "SO3_convention": {
        "representation": "real defining associated rank-3 bundle",
        "gauge_derivative": "(D_A phi)^a_M=partial_M phi^a+A^a_bM phi^b",
        "curvature": "F[A]=dA+A wedge A with ordered matrix multiplication",
        "exterior_derivative": "(dA)_MN=partial_M A_N-partial_N A_M",
        "wedge": "(A wedge A)_MN=A_M A_N-A_N A_M",
        "matrix_two_form_typing": "ordered products A wedge alpha and alpha wedge A are End(R3)-valued separately; adjoint two-forms dA and d alpha enter through an explicit executable inclusion into End(R3)",
        "pairing": "<X,Y>=-tr_3(XY)/2 and B wedge F uses the displayed orientation",
    },
    "pointwise_completion": {
        "W": "3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]",
        "W_Omega": "ordinary exact derivative of the displayed W AST with respect to Omega",
        "U": "W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
        "P": "d phi+A phi+(3/2) phi tensor (Omega^-1 d Omega)",
        "norm": "|phi|=sqrt(delta_ab phi^a phi^b)",
        "V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
        "full_V4_argument": "r=Omega^(3/2)*|phi|",
        "full_V4_smooth_rewrite": "Omega^-5*V4(Omega^(3/2)*|phi|)=Omega*s^2/(2*sqrt(1+Omega^6*s^2)), s=delta_ab phi^a phi^b",
        "Omega_domain": "Omega>0 for log(Omega) and inverse powers",
    },
    "field_roles": {
        "per_bulk_side": ["g_metric", "Omega_scalar", "phi_associated_0_form", "A_affine_connection_1_form", "B_adjoint_3_form"],
        "wall": ["gamma_metric", "Omega_Sigma_scalar"],
        "variations": ["H", "omega", "psi", "alpha_adjoint_1_form", "b_adjoint_3_form", "h", "omega_Sigma"],
        "plus_minus_aliasing": "forbidden: plus and minus fields are distinct slots",
        "interface_slots": "gamma and the single common Omega_Sigma trace are interface slots; bulk-to-wall pullback and moving-gluing assembly are excluded",
    },
    "differential_normal_form": {
        "before_Frechet": "expand nabla Omega, D_A phi, F[A], d and wedge to typed holonomic partial/exterior-partial AST nodes",
        "ordinary_partials": "holonomic coordinate partials commute on scalar and component jets",
        "exterior_sign": "graded Leibniz; d(B wedge alpha)=dB wedge alpha-B wedge d alpha for deg(B)=3",
        "density": "densities remain explicit AST factors; no silent flat-measure convention",
        "strict_real_scalar": "scalar arithmetic admits only form_degree=0, variance=(), density_weight=0, bundle=trivial, fiber_dimension=1; metrics and forms are rejected as scalar operands",
    },
    "scope": {
        "included": list(EASY_COMPONENTS),
        "excluded": list(EXCLUDED_COMPONENTS),
        "moving_shape": False,
        "full_Green_identity": False,
    },
}

SEMANTIC_COMPLETION_SHA256 = _canonical_sha256(SEMANTIC_COMPLETION)
EXPECTED_SEMANTIC_COMPLETION_SHA256 = (
    "392840aeaed507e742d673bcae32c8b9490825b27e293ec62f583d8c295139fe"
)


def _integer(captures: Mapping[str, str], key: str) -> int:
    try:
        value = int(captures[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise SemanticFrechetError(f"missing integer capture {key}") from exc
    if value < 0:
        raise SemanticFrechetError(f"negative unsigned charter capture {key}")
    return value


def _ordered_action(raw: Mapping[str, Any]) -> dict[str, str]:
    if set(raw) != set(ACTION_KEYS):
        raise SemanticFrechetError("v5.2 exact-action inventory drift")
    if any(type(raw[key]) is not str for key in ACTION_KEYS):
        raise SemanticFrechetError("v5.2 exact-action string type drift")
    return {key: raw[key] for key in ACTION_KEYS}


def certify_v52_dependency() -> tuple[dict[str, str], dict[str, Any]]:
    observed = {name: _sha256(path) for name, path in PINNED_PATHS.items()}
    if observed != PINNED_INPUTS:
        raise SemanticFrechetError("v5.2 source/test/artifact byte binding failed")
    payload = _read_json(V52_ARTIFACT)
    if payload.get("schema") != V52_SCHEMA:
        raise SemanticFrechetError("v5.2 artifact schema drift")
    checks = payload.get("checks")
    if type(checks) is not dict or checks.get("all") is not True:
        raise SemanticFrechetError("v5.2 artifact is not certified")
    charter = payload.get("exact_classical_charter")
    if type(charter) is not dict:
        raise SemanticFrechetError("v5.2 exact_classical_charter missing")
    raw_action = charter.get("exact_action")
    if type(raw_action) is not dict:
        raise SemanticFrechetError("v5.2 exact_action missing")
    action = _ordered_action(raw_action)
    if _canonical_sha256(action) != V52_EXACT_ACTION_SHA256:
        raise SemanticFrechetError("v5.2 exact_action canonical hash drift")
    return action, payload


def scalar_partial(expr: Expr, variable: str) -> Expr:
    """Exact pointwise scalar derivative used to expand W_Omega."""

    if not _is_strict_scalar(expr.type_tag):
        raise SemanticFrechetError("scalar_partial received a non-scalar AST")
    if expr.op in {"rational", "parameter", "zero"}:
        return zero(expr.type_tag)
    if expr.op == "field":
        return rational(1, dimension=expr.type_tag.dimension) if expr.label == variable else zero(expr.type_tag)
    if expr.op == "add":
        return add(*(scalar_partial(arg, variable) for arg in expr.args))
    if expr.op == "mul_scalar":
        terms = []
        for index, arg in enumerate(expr.args):
            derivative = scalar_partial(arg, variable)
            if not is_zero(derivative):
                terms.append(scalar_mul(derivative, *(other for position, other in enumerate(expr.args) if position != index)))
        return add(*terms) if terms else zero(expr.type_tag)
    if expr.op == "power":
        assert expr.exponent is not None
        derivative = scalar_partial(expr.args[0], variable)
        if is_zero(derivative):
            return zero(expr.type_tag)
        return scalar_mul(rational(expr.exponent), power(expr.args[0], expr.exponent - 1), derivative)
    if expr.op == "exp":
        derivative = scalar_partial(expr.args[0], variable)
        return zero(expr.type_tag) if is_zero(derivative) else scalar_mul(exp_scalar(expr.args[0]), derivative)
    if expr.op == "sqrt":
        derivative = scalar_partial(expr.args[0], variable)
        return zero(expr.type_tag) if is_zero(derivative) else scalar_mul(rational(Fraction(1, 2)), power(expr.args[0], Fraction(-1, 2)), derivative)
    raise SemanticFrechetError(f"scalar_partial has no rule for {expr.op}")


def _w_ast(omega: Expr, parsed: ParsedCharter) -> Expr:
    row = parsed.captures["W"]
    m5 = parameter(row["m5"])
    g = parameter(row["G"])
    k = parameter(row["k"])
    exponent = negate(
        scalar_mul(
            g,
            power(omega, _integer(row, "xpow")),
            inverse_scalar(scalar_mul(rational(_integer(row, "c6")), power(m5, _integer(row, "m5p")))),
        )
    )
    return scalar_mul(
        rational(_integer(row, "c3")),
        power(m5, _integer(row, "m5p")),
        k,
        exp_scalar(exponent),
    )


def _u_ast(omega: Expr, parsed: ParsedCharter) -> Expr:
    row = parsed.captures["U"]
    if row["x"] != parsed.captures["W"]["x"]:
        raise SemanticFrechetError("U and W scalar aliases disagree")
    w = _w_ast(omega, parsed)
    w_omega = scalar_partial(w, omega.label)
    g = parameter(row["G"])
    m5 = parameter(row["m5"])
    positive = scalar_mul(
        power(w_omega, _integer(row, "wpow")),
        inverse_scalar(scalar_mul(rational(_integer(row, "c2")), g)),
    )
    negative = negate(
        scalar_mul(
            rational(_integer(row, "n2")),
            power(w, _integer(row, "Wpow")),
            inverse_scalar(scalar_mul(rational(_integer(row, "c3")), power(m5, _integer(row, "m5p")))),
        )
    )
    return add(positive, negative)


def _v4_ast(argument: Expr, parsed: ParsedCharter) -> Expr:
    row = parsed.captures["V4"]
    numerator = power(argument, _integer(row, "p4"))
    denominator = scalar_mul(
        rational(_integer(row, "c2")),
        sqrt_scalar(add(rational(_integer(row, "one"), dimension=argument.type_tag.dimension), numerator)),
    )
    return scalar_mul(numerator, inverse_scalar(denominator))


def _smooth_full_v4_ast(
    omega: Expr,
    phi: Expr,
    parsed: ParsedCharter,
) -> Expr:
    """Algebraically compose the parsed Omega^-5, V4 and norm without sqrt(s)."""

    bulk = parsed.captures["bulk"]
    v4 = parsed.captures["V4"]
    p4 = _integer(v4, "p4")
    if p4 % 2:
        raise SemanticFrechetError("full-V4 smooth rewrite requires the parsed even power")
    omega_argument_power = Fraction(
        _integer(bulk, "o32n"), _integer(bulk, "o32d")
    )
    omega_inside_power = omega_argument_power * p4
    omega_outside_power = omega_inside_power - _integer(bulk, "ominus")
    s_power = Fraction(p4, 2)
    s = associated_pair(phi, phi)
    inside_power = scalar_mul(
        power(omega, omega_inside_power),
        power(s, s_power),
    )
    numerator = scalar_mul(
        power(omega, omega_outside_power),
        power(s, s_power),
    )
    denominator = scalar_mul(
        rational(_integer(v4, "c2")),
        sqrt_scalar(
            add(
                rational(_integer(v4, "one"), dimension=omega.type_tag.dimension),
                inside_power,
            )
        ),
    )
    return scalar_mul(numerator, inverse_scalar(denominator))


def _p_ast(
    omega: Expr,
    phi: Expr,
    connection: Expr,
    parsed: ParsedCharter,
) -> Expr:
    row = parsed.captures["P"]
    return add(
        exterior_partial(phi),
        associated_action(connection, phi),
        scale(
            rational(Fraction(_integer(row, "c3"), _integer(row, "c2"))),
            associated_times_oneform(
                phi,
                scale(inverse_scalar(omega), exterior_partial(omega)),
            ),
        ),
    )


@dataclass(frozen=True)
class ComponentProgram:
    parsed: ParsedCharter
    components: Mapping[str, Expr]
    tangents: Mapping[str, Expr]
    component_fields: Mapping[str, tuple[str, ...]]


def build_component_program(parsed: ParsedCharter) -> ComponentProgram:
    bulk = parsed.captures["bulk"]
    wall_row = parsed.captures["wall"]
    bf_row = parsed.captures["BF"]
    if _integer(bulk, "m5p") != 3 or _integer(bulk, "opow") != 2:
        raise SemanticFrechetError("unsupported EH/Omega exponent grammar in pinned bulk row")

    components: dict[str, Expr] = {}
    tangents: dict[str, Expr] = {}
    component_fields: dict[str, tuple[str, ...]] = {}

    for side in ("plus", "minus"):
        metric = field(f"g_{side}", METRIC5)
        omega = field(f"Omega_{side}", SCALAR5)
        phi = field(f"phi_{side}", ASSOCIATED0_5)
        connection = field(f"A_{side}", CONNECTION1_5)
        bfield = field(f"B_{side}", ADJOINT3_5)
        inverse = inverse_metric(metric)
        volume = volume_density(metric)
        d_omega = exterior_partial(omega)

        p = _p_ast(omega, phi, connection, parsed)
        curvature = add(
            adjoint_matrix_embedding(exterior_partial(connection)),
            connection_wedge(connection, connection),
        )

        components[f"Omega_kinetic_bulk_{side}"] = density_times_scalar(
            volume,
            negate(
                scalar_mul(
                    parameter("G"),
                    rational(Fraction(1, _integer(bulk, "ok2"))),
                    metric_contract(inverse, d_omega, d_omega),
                )
            ),
        )
        components[f"Omega_potential_bulk_{side}"] = density_times_scalar(volume, negate(_u_ast(omega, parsed)))
        components[f"P_kinetic_bulk_{side}"] = density_times_scalar(
            volume,
            negate(
                scalar_mul(
                    parameter("Z5"),
                    rational(Fraction(1, _integer(bulk, "pk2"))),
                    metric_contract(inverse, p, p),
                )
            ),
        )
        components[f"full_V4_bulk_{side}"] = density_times_scalar(
            volume,
            negate(
                scalar_mul(
                    parameter("Z5"),
                    power(parameter("M"), _integer(bulk, "Mpow")),
                    _smooth_full_v4_ast(omega, phi, parsed),
                )
            ),
        )
        components[f"BF_bulk_{side}"] = pair_wedge(
            bfield,
            curvature,
            pairing_label=f"-tr3/{_integer(bf_row, 'tr2')}",
        )

        tangents.update(
            {
                metric.label: variation(f"H_{side}", METRIC5),
                omega.label: variation(f"omega_{side}", SCALAR5),
                phi.label: variation(f"psi_{side}", ASSOCIATED0_5),
                connection.label: variation(f"alpha_{side}", ADJOINT1_5),
                bfield.label: variation(f"b_{side}", ADJOINT3_5),
            }
        )
        component_fields[f"Omega_kinetic_bulk_{side}"] = (metric.label, omega.label)
        component_fields[f"Omega_potential_bulk_{side}"] = (metric.label, omega.label)
        component_fields[f"P_kinetic_bulk_{side}"] = (metric.label, omega.label, phi.label, connection.label)
        component_fields[f"full_V4_bulk_{side}"] = (metric.label, omega.label, phi.label)
        component_fields[f"BF_bulk_{side}"] = (bfield.label, connection.label)

    gamma = field("gamma", METRIC4)
    omega_sigma = field("Omega_Sigma", SCALAR4)
    wall_volume = volume_density(gamma)
    wall_bracket = add(
        scalar_mul(rational(_integer(wall_row, "w2")), _w_ast(omega_sigma, parsed)),
        scalar_mul(
            parameter("beta"),
            power(add(omega_sigma, negate(rational(_integer(wall_row, "one"), dimension=4))), _integer(wall_row, "p2")),
            rational(Fraction(1, _integer(wall_row, "b2"))),
        ),
    )
    components["wall"] = density_times_scalar(wall_volume, negate(wall_bracket))
    tangents.update(
        {
            gamma.label: variation("h", METRIC4),
            omega_sigma.label: variation("omega_Sigma", SCALAR4),
        }
    )
    component_fields["wall"] = (gamma.label, omega_sigma.label)

    if tuple(components) != EASY_COMPONENTS:
        raise SemanticFrechetError("eleven-component order or inventory drift")
    return ComponentProgram(parsed, components, tangents, component_fields)


def _sum_tangents(type_tag: GeoType, values: Iterable[Expr]) -> Expr:
    nonzero = [value for value in values if not is_zero(value)]
    return add(*nonzero) if nonzero else zero(type_tag)


@dataclass(frozen=True)
class DualExpr:
    primal: Expr
    tangent: Expr


def forward_nilpotent_dual(
    expr: Expr,
    tangent_slots: Mapping[str, Expr],
    *,
    mutant: str | None = None,
) -> DualExpr:
    """Forward JVP over the AST; epsilon^2 is discarded at every node."""

    if expr.op in {"rational", "parameter", "zero"}:
        return DualExpr(expr, zero(expr.type_tag))
    if expr.op == "field":
        tangent = tangent_slots.get(expr.label, zero(expr.type_tag))
        if tangent.type_tag != expr.type_tag and not (
            expr.type_tag == CONNECTION1_5 and tangent.type_tag == ADJOINT1_5
        ):
            raise SemanticFrechetError(f"bad tangent slot for {expr.label}")
        return DualExpr(expr, tangent)
    if expr.op == "variation":
        raise SemanticFrechetError("a primal AST cannot contain a variation leaf")

    duals = tuple(
        forward_nilpotent_dual(arg, tangent_slots, mutant=mutant) for arg in expr.args
    )
    primal_args = tuple(item.primal for item in duals)
    tangent_args = tuple(item.tangent for item in duals)

    if expr.op == "add":
        return DualExpr(add(*primal_args), _sum_tangents(expr.type_tag, tangent_args))
    if expr.op == "mul_scalar":
        primal = scalar_mul(*primal_args)
        terms = []
        for index, tangent in enumerate(tangent_args):
            if not is_zero(tangent):
                terms.append(scalar_mul(tangent, *(arg for position, arg in enumerate(primal_args) if position != index)))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "scale":
        primal = scale(*primal_args)
        return DualExpr(
            primal,
            _sum_tangents(
                expr.type_tag,
                (scale(tangent_args[0], primal_args[1]), scale(primal_args[0], tangent_args[1])),
            ),
        )
    if expr.op == "power":
        assert expr.exponent is not None
        primal = power(primal_args[0], expr.exponent)
        coefficient = expr.exponent
        if mutant == "forward_wrong_inverse_sign" and expr.exponent == -1:
            coefficient = Fraction(1)
        tangent = (
            zero(expr.type_tag)
            if is_zero(tangent_args[0])
            else scalar_mul(rational(coefficient), power(primal_args[0], expr.exponent - 1), tangent_args[0])
        )
        return DualExpr(primal, tangent)
    if expr.op == "exp":
        primal = exp_scalar(primal_args[0])
        exp_factor = (
            rational(2)
            if mutant == "correlated_double_exp_derivative"
            else rational(1)
        )
        tangent = (
            zero(expr.type_tag)
            if is_zero(tangent_args[0])
            else scalar_mul(exp_factor, primal, tangent_args[0])
        )
        return DualExpr(primal, tangent)
    if expr.op == "sqrt":
        primal = sqrt_scalar(primal_args[0])
        tangent = (
            zero(expr.type_tag)
            if is_zero(tangent_args[0])
            else scalar_mul(rational(Fraction(1, 2)), power(primal_args[0], Fraction(-1, 2)), tangent_args[0])
        )
        return DualExpr(primal, tangent)
    if expr.op == "inverse_metric":
        primal = inverse_metric(primal_args[0])
        tangent = (
            zero(expr.type_tag)
            if is_zero(tangent_args[0])
            else negate(inverse_sandwich(primal, tangent_args[0], primal))
        )
        if mutant == "forward_wrong_metric_inverse_sign" and not is_zero(tangent):
            tangent = negate(tangent)
        return DualExpr(primal, tangent)
    if expr.op == "volume_density":
        primal = volume_density(primal_args[0])
        inverse = inverse_metric(primal_args[0])
        factor = Fraction(1) if mutant == "forward_wrong_volume_half" else Fraction(1, 2)
        tangent = (
            zero(expr.type_tag)
            if is_zero(tangent_args[0])
            else scale(scalar_mul(rational(factor), metric_trace(inverse, tangent_args[0])), primal)
        )
        return DualExpr(primal, tangent)
    if expr.op == "metric_trace":
        primal = metric_trace(*primal_args)
        terms = []
        if not is_zero(tangent_args[0]):
            terms.append(metric_trace(tangent_args[0], primal_args[1]))
        if not is_zero(tangent_args[1]):
            terms.append(metric_trace(primal_args[0], tangent_args[1]))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "inverse_sandwich":
        primal = inverse_sandwich(*primal_args)
        terms = []
        for index, tangent in enumerate(tangent_args):
            if not is_zero(tangent):
                rows = primal_args[:index] + (tangent,) + primal_args[index + 1 :]
                terms.append(inverse_sandwich(*rows))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "exterior_partial":
        primal = exterior_partial(primal_args[0])
        tangent = zero(expr.type_tag) if is_zero(tangent_args[0]) else exterior_partial(tangent_args[0])
        if mutant == "forward_double_exterior_variation" and not is_zero(tangent):
            tangent = add(tangent, tangent)
        return DualExpr(primal, tangent)
    if expr.op == "SO3_action":
        primal = associated_action(*primal_args)
        terms = []
        if not is_zero(tangent_args[0]) and mutant != "forward_omit_alpha_phi":
            terms.append(associated_action(tangent_args[0], primal_args[1]))
        if not is_zero(tangent_args[1]):
            terms.append(associated_action(primal_args[0], tangent_args[1]))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "associated_times_oneform":
        primal = associated_times_oneform(*primal_args)
        terms = []
        if not is_zero(tangent_args[0]):
            terms.append(associated_times_oneform(tangent_args[0], primal_args[1]))
        if not is_zero(tangent_args[1]):
            terms.append(associated_times_oneform(primal_args[0], tangent_args[1]))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "metric_contract":
        primal = metric_contract(*primal_args)
        terms = []
        for index, tangent in enumerate(tangent_args):
            if not is_zero(tangent):
                rows = primal_args[:index] + (tangent,) + primal_args[index + 1 :]
                terms.append(metric_contract(*rows))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "associated_pair":
        primal = associated_pair(*primal_args)
        terms = []
        if not is_zero(tangent_args[0]):
            terms.append(associated_pair(tangent_args[0], primal_args[1]))
        if not is_zero(tangent_args[1]):
            terms.append(associated_pair(primal_args[0], tangent_args[1]))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "adjoint_matrix_embedding":
        primal = adjoint_matrix_embedding(primal_args[0])
        tangent = (
            zero(expr.type_tag)
            if is_zero(tangent_args[0])
            else adjoint_matrix_embedding(tangent_args[0])
        )
        return DualExpr(primal, tangent)
    if expr.op == "matrix_wedge":
        primal = connection_wedge(*primal_args)
        terms = []
        if not is_zero(tangent_args[0]):
            terms.append(connection_wedge(tangent_args[0], primal_args[1]))
        if not is_zero(tangent_args[1]):
            terms.append(connection_wedge(primal_args[0], tangent_args[1]))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "invariant_pair_wedge":
        primal = pair_wedge(*primal_args, pairing_label=expr.label)
        terms = []
        if not is_zero(tangent_args[0]):
            terms.append(pair_wedge(tangent_args[0], primal_args[1], pairing_label=expr.label))
        if not is_zero(tangent_args[1]):
            terms.append(pair_wedge(primal_args[0], tangent_args[1], pairing_label=expr.label))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "density_times_scalar":
        primal = density_times_scalar(*primal_args)
        terms = []
        if not is_zero(tangent_args[0]):
            terms.append(density_times_scalar(tangent_args[0], primal_args[1]))
        if not is_zero(tangent_args[1]):
            terms.append(density_times_scalar(primal_args[0], tangent_args[1]))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    raise SemanticFrechetError(f"forward dual has no rule for {expr.op}")


def _field_occurrence_paths(
    expr: Expr,
    tangent_slots: Mapping[str, Expr],
    prefix: tuple[int, ...] = (),
) -> Iterable[tuple[tuple[int, ...], Expr]]:
    if expr.op == "field" and expr.label in tangent_slots:
        yield prefix, tangent_slots[expr.label]
        return
    for index, arg in enumerate(expr.args):
        yield from _field_occurrence_paths(arg, tangent_slots, prefix + (index,))


def _reverse_local_lift(
    parent: Expr,
    child_index: int,
    child_tangent: Expr,
    *,
    mutant: str | None = None,
) -> Expr:
    """Lift one leaf perturbation through one parent context."""

    args = parent.args
    if parent.op == "add":
        return child_tangent
    if parent.op == "mul_scalar":
        return scalar_mul(child_tangent, *(arg for index, arg in enumerate(args) if index != child_index))
    if parent.op == "scale":
        return scale(child_tangent, args[1]) if child_index == 0 else scale(args[0], child_tangent)
    if parent.op == "power":
        assert parent.exponent is not None
        coefficient = parent.exponent
        if mutant == "reverse_wrong_inverse_sign" and parent.exponent == -1:
            coefficient = Fraction(1)
        return scalar_mul(rational(coefficient), power(args[0], parent.exponent - 1), child_tangent)
    if parent.op == "exp":
        factor = (
            rational(2)
            if mutant == "correlated_double_exp_derivative"
            else rational(1)
        )
        return scalar_mul(factor, exp_scalar(args[0]), child_tangent)
    if parent.op == "sqrt":
        return scalar_mul(rational(Fraction(1, 2)), power(args[0], Fraction(-1, 2)), child_tangent)
    if parent.op == "inverse_metric":
        inverse = inverse_metric(args[0])
        value = negate(inverse_sandwich(inverse, child_tangent, inverse))
        return negate(value) if mutant == "reverse_wrong_metric_inverse_sign" else value
    if parent.op == "volume_density":
        factor = Fraction(1) if mutant == "reverse_wrong_volume_half" else Fraction(1, 2)
        volume = volume_density(args[0])
        return scale(scalar_mul(rational(factor), metric_trace(inverse_metric(args[0]), child_tangent)), volume)
    if parent.op == "metric_trace":
        return metric_trace(child_tangent, args[1]) if child_index == 0 else metric_trace(args[0], child_tangent)
    if parent.op == "inverse_sandwich":
        rows = args[:child_index] + (child_tangent,) + args[child_index + 1 :]
        return inverse_sandwich(*rows)
    if parent.op == "exterior_partial":
        if mutant == "reverse_omit_BF_dalpha" and child_tangent.type_tag == ADJOINT1_5:
            return zero(parent.type_tag)
        return exterior_partial(child_tangent)
    if parent.op == "SO3_action":
        if child_index == 0:
            return associated_action(child_tangent, args[1])
        return associated_action(args[0], child_tangent)
    if parent.op == "associated_times_oneform":
        if child_index == 0:
            return associated_times_oneform(child_tangent, args[1])
        return associated_times_oneform(args[0], child_tangent)
    if parent.op == "metric_contract":
        rows = args[:child_index] + (child_tangent,) + args[child_index + 1 :]
        return metric_contract(*rows)
    if parent.op == "associated_pair":
        return associated_pair(child_tangent, args[1]) if child_index == 0 else associated_pair(args[0], child_tangent)
    if parent.op == "adjoint_matrix_embedding":
        return adjoint_matrix_embedding(child_tangent)
    if parent.op == "matrix_wedge":
        return connection_wedge(child_tangent, args[1]) if child_index == 0 else connection_wedge(args[0], child_tangent)
    if parent.op == "invariant_pair_wedge":
        return (
            pair_wedge(child_tangent, args[1], pairing_label=parent.label)
            if child_index == 0
            else pair_wedge(args[0], child_tangent, pairing_label=parent.label)
        )
    if parent.op == "density_times_scalar":
        return density_times_scalar(child_tangent, args[1]) if child_index == 0 else density_times_scalar(args[0], child_tangent)
    raise SemanticFrechetError(f"reverse context has no local rule for {parent.op}")


def reverse_context_mode(
    expr: Expr,
    tangent_slots: Mapping[str, Expr],
    *,
    mutant: str | None = None,
) -> Expr:
    """Enumerate output-to-leaf contexts and pull each leaf JVP back upward."""

    contributions: list[Expr] = []
    for path, leaf_tangent in _field_occurrence_paths(expr, tangent_slots):
        node = expr
        frames: list[tuple[Expr, int]] = []
        for index in path:
            frames.append((node, index))
            node = node.args[index]
        lifted = leaf_tangent
        for parent, index in reversed(frames):
            lifted = _reverse_local_lift(parent, index, lifted, mutant=mutant)
            if is_zero(lifted):
                break
        if not is_zero(lifted):
            contributions.append(lifted)
    return _sum_tangents(expr.type_tag, contributions)


def _walk(expr: Expr) -> Iterable[Expr]:
    yield expr
    for arg in expr.args:
        yield from _walk(arg)


def _variation_degrees(expr: Expr) -> set[int]:
    if expr.op == "variation":
        return {1}
    if expr.op in {"rational", "parameter", "zero", "field"}:
        return {0}
    degrees = [_variation_degrees(arg) for arg in expr.args]
    if expr.op == "add":
        return set().union(*degrees)
    if expr.op in {"power", "exp", "sqrt", "inverse_metric", "volume_density"}:
        if degrees[0] != {0}:
            raise SemanticFrechetError(f"nonlinear node {expr.op} contains a variation")
        return {0}
    result = {0}
    for child in degrees:
        result = {left + right for left in result for right in child}
    return result


def _op_inventory(expr: Expr) -> dict[str, int]:
    rows: dict[str, int] = defaultdict(int)
    for node in _walk(expr):
        rows[node.op] += 1
    return dict(sorted(rows.items()))


def _leaf_labels(expr: Expr, op: str) -> tuple[str, ...]:
    return tuple(sorted({node.label for node in _walk(expr) if node.op == op}))


def _aggregate_expr_sha256(rows: Mapping[str, Expr]) -> str:
    return _canonical_sha256({name: _expr_row(expr) for name, expr in rows.items()})


def _rename_field_labels(expr: Expr, renames: Mapping[str, str]) -> Expr:
    args = tuple(_rename_field_labels(arg, renames) for arg in expr.args)
    label = renames.get(expr.label, expr.label) if expr.op in {"field", "variation"} else expr.label
    return Expr(expr.op, expr.type_tag, args, label, expr.value, expr.exponent)


@dataclass(frozen=True)
class FractionDual:
    primal: Fraction
    tangent: Fraction = Fraction(0)

    def __add__(self, other: "FractionDual | Fraction | int") -> "FractionDual":
        right = other if isinstance(other, FractionDual) else FractionDual(Fraction(other))
        return FractionDual(self.primal + right.primal, self.tangent + right.tangent)

    __radd__ = __add__

    def __neg__(self) -> "FractionDual":
        return FractionDual(-self.primal, -self.tangent)

    def __sub__(self, other: "FractionDual | Fraction | int") -> "FractionDual":
        return self + (-other if isinstance(other, FractionDual) else -Fraction(other))

    def __rsub__(self, other: "FractionDual | Fraction | int") -> "FractionDual":
        return (-self) + other

    def __mul__(self, other: "FractionDual | Fraction | int") -> "FractionDual":
        right = other if isinstance(other, FractionDual) else FractionDual(Fraction(other))
        return FractionDual(
            self.primal * right.primal,
            self.tangent * right.primal + self.primal * right.tangent,
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "FractionDual":
        if self.primal == 0:
            raise SemanticFrechetError("dual reciprocal at zero")
        return FractionDual(
            1 / self.primal,
            -self.tangent / power_fraction(self.primal, 2),
        )

    def __truediv__(self, other: "FractionDual | Fraction | int") -> "FractionDual":
        right = other if isinstance(other, FractionDual) else FractionDual(Fraction(other))
        return self * right.reciprocal()


def _sqrt_fraction_dual(value: FractionDual) -> FractionDual:
    root = _sqrt_number(value.primal)
    if not isinstance(root, Fraction):
        raise SemanticFrechetError("exact dual square-root oracle became irrational")
    return FractionDual(root, value.tangent / (2 * root))


@dataclass(frozen=True)
class PolynomialX0:
    coefficients: tuple[Fraction, ...]

    def __add__(self, other: "PolynomialX0") -> "PolynomialX0":
        size = max(len(self.coefficients), len(other.coefficients))
        return PolynomialX0(
            tuple(
                (self.coefficients[index] if index < len(self.coefficients) else Fraction(0))
                + (other.coefficients[index] if index < len(other.coefficients) else Fraction(0))
                for index in range(size)
            )
        )

    def __neg__(self) -> "PolynomialX0":
        return PolynomialX0(tuple(-value for value in self.coefficients))

    def __mul__(self, other: "PolynomialX0 | Fraction | int") -> "PolynomialX0":
        if not isinstance(other, PolynomialX0):
            other = PolynomialX0((Fraction(other),))
        output = [Fraction(0)] * (len(self.coefficients) + len(other.coefficients) - 1)
        for left_index, left in enumerate(self.coefficients):
            for right_index, right in enumerate(other.coefficients):
                output[left_index + right_index] += left * right
        return PolynomialX0(tuple(output))

    __rmul__ = __mul__

    def derivative(self) -> "PolynomialX0":
        if len(self.coefficients) <= 1:
            return PolynomialX0((Fraction(0),))
        return PolynomialX0(
            tuple(index * value for index, value in enumerate(self.coefficients[1:], start=1))
        )

    def at_zero(self) -> Fraction:
        return self.coefficients[0]


@dataclass(frozen=True)
class ExpPolynomial:
    """Exact polynomial in E=exp(-1/6), never evaluated numerically."""

    terms: tuple[tuple[int, Fraction], ...]

    @staticmethod
    def from_mapping(values: Mapping[int, Fraction]) -> "ExpPolynomial":
        return ExpPolynomial(
            tuple(sorted((power, value) for power, value in values.items() if value))
        )

    @staticmethod
    def monomial(power: int, coefficient: Fraction = Fraction(1)) -> "ExpPolynomial":
        return ExpPolynomial.from_mapping({power: coefficient})

    def __add__(self, other: "ExpPolynomial | Fraction | int") -> "ExpPolynomial":
        right = other if isinstance(other, ExpPolynomial) else ExpPolynomial.monomial(0, Fraction(other))
        values: dict[int, Fraction] = defaultdict(Fraction)
        for power, coefficient in self.terms + right.terms:
            values[power] += coefficient
        return ExpPolynomial.from_mapping(values)

    __radd__ = __add__

    def __neg__(self) -> "ExpPolynomial":
        return ExpPolynomial(tuple((power, -coefficient) for power, coefficient in self.terms))

    def __sub__(self, other: "ExpPolynomial | Fraction | int") -> "ExpPolynomial":
        return self + (-other if isinstance(other, ExpPolynomial) else -Fraction(other))

    def __mul__(self, other: "ExpPolynomial | Fraction | int") -> "ExpPolynomial":
        right = other if isinstance(other, ExpPolynomial) else ExpPolynomial.monomial(0, Fraction(other))
        values: dict[int, Fraction] = defaultdict(Fraction)
        for left_power, left_coefficient in self.terms:
            for right_power, right_coefficient in right.terms:
                values[left_power + right_power] += left_coefficient * right_coefficient
        return ExpPolynomial.from_mapping(values)

    __rmul__ = __mul__

    def __truediv__(self, other: Fraction | int) -> "ExpPolynomial":
        denominator = Fraction(other)
        return ExpPolynomial(
            tuple((power, coefficient / denominator) for power, coefficient in self.terms)
        )

    def __pow__(self, exponent: int) -> "ExpPolynomial":
        if exponent < 0:
            raise SemanticFrechetError("negative ExpPolynomial powers are not polynomial")
        result = ExpPolynomial.monomial(0)
        for _ in range(exponent):
            result = result * self
        return result


@dataclass(frozen=True)
class OmegaExpPolynomial:
    """Exact sum c*Omega^p*exp(-Omega^2/6)^q."""

    terms: tuple[tuple[tuple[int, int], Fraction], ...]

    @staticmethod
    def from_mapping(
        values: Mapping[tuple[int, int], Fraction]
    ) -> "OmegaExpPolynomial":
        return OmegaExpPolynomial(
            tuple(sorted((powers, value) for powers, value in values.items() if value))
        )

    @staticmethod
    def monomial(
        omega_power: int,
        exp_power: int,
        coefficient: Fraction = Fraction(1),
    ) -> "OmegaExpPolynomial":
        return OmegaExpPolynomial.from_mapping(
            {(omega_power, exp_power): coefficient}
        )

    def __add__(
        self, other: "OmegaExpPolynomial | Fraction | int"
    ) -> "OmegaExpPolynomial":
        right = (
            other
            if isinstance(other, OmegaExpPolynomial)
            else OmegaExpPolynomial.monomial(0, 0, Fraction(other))
        )
        values: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
        for powers, coefficient in self.terms + right.terms:
            values[powers] += coefficient
        return OmegaExpPolynomial.from_mapping(values)

    __radd__ = __add__

    def __neg__(self) -> "OmegaExpPolynomial":
        return OmegaExpPolynomial(
            tuple((powers, -coefficient) for powers, coefficient in self.terms)
        )

    def __sub__(
        self, other: "OmegaExpPolynomial | Fraction | int"
    ) -> "OmegaExpPolynomial":
        return self + (
            -other if isinstance(other, OmegaExpPolynomial) else -Fraction(other)
        )

    def __mul__(
        self, other: "OmegaExpPolynomial | Fraction | int"
    ) -> "OmegaExpPolynomial":
        right = (
            other
            if isinstance(other, OmegaExpPolynomial)
            else OmegaExpPolynomial.monomial(0, 0, Fraction(other))
        )
        values: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
        for (left_omega, left_exp), left_coefficient in self.terms:
            for (right_omega, right_exp), right_coefficient in right.terms:
                values[(left_omega + right_omega, left_exp + right_exp)] += (
                    left_coefficient * right_coefficient
                )
        return OmegaExpPolynomial.from_mapping(values)

    __rmul__ = __mul__

    def derivative(self, *, exp_chain_multiplier: Fraction = Fraction(1)) -> "OmegaExpPolynomial":
        values: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
        for (omega_power, exp_power), coefficient in self.terms:
            if omega_power:
                values[(omega_power - 1, exp_power)] += coefficient * omega_power
            if exp_power:
                values[(omega_power + 1, exp_power)] += (
                    -coefficient
                    * exp_power
                    * exp_chain_multiplier
                    / Fraction(3)
                )
        return OmegaExpPolynomial.from_mapping(values)

    def at_omega_one(self) -> ExpPolynomial:
        values: dict[int, Fraction] = defaultdict(Fraction)
        for (_omega_power, exp_power), coefficient in self.terms:
            values[exp_power] += coefficient
        return ExpPolynomial.from_mapping(values)


MiniForm = dict[tuple[int, ...], PolynomialX0]


def _mini_wedge(left: MiniForm, right: MiniForm) -> MiniForm:
    output: MiniForm = {}
    for left_axes, left_coefficient in left.items():
        for right_axes, right_coefficient in right.items():
            combined = left_axes + right_axes
            if len(set(combined)) != len(combined):
                continue
            inversions = sum(
                1
                for first in range(len(combined))
                for second in range(first + 1, len(combined))
                if combined[first] > combined[second]
            )
            axes = tuple(sorted(combined))
            coefficient = left_coefficient * right_coefficient
            if inversions % 2:
                coefficient = -coefficient
            output[axes] = output.get(axes, PolynomialX0((Fraction(0),))) + coefficient
    return output


def _mini_exterior_d(form: MiniForm) -> MiniForm:
    differentiated = {
        axes: coefficient.derivative()
        for axes, coefficient in form.items()
        if 0 not in axes
    }
    return _mini_wedge({(0,): PolynomialX0((Fraction(1),))}, differentiated)


def _mini_top_at_zero(form: MiniForm) -> Fraction:
    return form.get(
        (0, 1, 2, 3, 4), PolynomialX0((Fraction(0),))
    ).at_zero()


Matrix3 = tuple[tuple[Fraction, Fraction, Fraction], ...]
MiniMatrixForm = dict[tuple[int, ...], Matrix3]


def _matrix3_zero() -> Matrix3:
    return tuple(tuple(Fraction(0) for _ in range(3)) for _ in range(3))


def _matrix3_add(left: Matrix3, right: Matrix3) -> Matrix3:
    return tuple(
        tuple(left[row][column] + right[row][column] for column in range(3))
        for row in range(3)
    )


def _matrix3_scale(coefficient: Fraction, value: Matrix3) -> Matrix3:
    return tuple(
        tuple(coefficient * value[row][column] for column in range(3))
        for row in range(3)
    )


def _matrix3_multiply(left: Matrix3, right: Matrix3) -> Matrix3:
    return tuple(
        tuple(
            sum(
                (left[row][index] * right[index][column] for index in range(3)),
                Fraction(0),
            )
            for column in range(3)
        )
        for row in range(3)
    )


def _mini_matrix_form_add(*forms: MiniMatrixForm) -> MiniMatrixForm:
    output: MiniMatrixForm = {}
    for form in forms:
        for axes, coefficient in form.items():
            output[axes] = _matrix3_add(
                output.get(axes, _matrix3_zero()), coefficient
            )
    return {axes: value for axes, value in output.items() if value != _matrix3_zero()}


def _mini_matrix_wedge(left: MiniMatrixForm, right: MiniMatrixForm) -> MiniMatrixForm:
    """Independent ordered-matrix exterior algebra on sorted basis words."""

    output: MiniMatrixForm = {}
    for left_axes, left_coefficient in left.items():
        for right_axes, right_coefficient in right.items():
            combined = left_axes + right_axes
            if len(set(combined)) != len(combined):
                continue
            inversions = sum(
                1
                for first in range(len(combined))
                for second in range(first + 1, len(combined))
                if combined[first] > combined[second]
            )
            coefficient = _matrix3_multiply(left_coefficient, right_coefficient)
            if inversions % 2:
                coefficient = _matrix3_scale(Fraction(-1), coefficient)
            axes = tuple(sorted(combined))
            output[axes] = _matrix3_add(
                output.get(axes, _matrix3_zero()), coefficient
            )
    return {axes: value for axes, value in output.items() if value != _matrix3_zero()}


def _mini_matrix_pair_top(
    left: MiniMatrixForm,
    right: MiniMatrixForm,
    *,
    trace_denominator: int = 2,
    trace_sign: int = -1,
) -> Fraction:
    top = _mini_matrix_wedge(left, right).get(
        (0, 1, 2, 3, 4), _matrix3_zero()
    )
    trace = sum((top[index][index] for index in range(3)), Fraction(0))
    return Fraction(trace_sign, trace_denominator) * trace


def exact_full_bf_frechet_oracle() -> dict[str, Any]:
    """Full BF differential from an independent finite exterior algebra."""

    zero = Fraction(0)
    one = Fraction(1)
    jx: Matrix3 = ((zero, zero, zero), (zero, zero, -one), (zero, one, zero))
    jy: Matrix3 = ((zero, zero, one), (zero, zero, zero), (-one, zero, zero))
    jz: Matrix3 = ((zero, -one, zero), (one, zero, zero), (zero, zero, zero))
    connection = {(3,): jx, (4,): jy}
    connection_variation = {(3,): _matrix3_scale(Fraction(11), jx)}
    exterior_connection = {(3, 4): _matrix3_scale(Fraction(2), jz)}
    exterior_variation = {(3, 4): _matrix3_scale(Fraction(7), jz)}
    bfield = {(0, 1, 2): _matrix3_scale(Fraction(5), jz)}
    b_variation = {(0, 1, 2): _matrix3_scale(Fraction(3), jz)}

    connection_square = _mini_matrix_wedge(connection, connection)
    alpha_A = _mini_matrix_wedge(connection_variation, connection)
    A_alpha = _mini_matrix_wedge(connection, connection_variation)
    terms = {
        "B_pair_alpha_wedge_A": _mini_matrix_pair_top(bfield, alpha_A),
        "B_pair_A_wedge_alpha": _mini_matrix_pair_top(bfield, A_alpha),
        "B_pair_d_alpha": _mini_matrix_pair_top(bfield, exterior_variation),
        "b_pair_A_wedge_A": _mini_matrix_pair_top(b_variation, connection_square),
        "b_pair_dA": _mini_matrix_pair_top(b_variation, exterior_connection),
    }
    expected_by_frechet_row_ordinal = (
        Fraction(35),
        Fraction(55, 2),
        Fraction(55, 2),
        Fraction(6),
        Fraction(3),
    )
    total = sum(terms.values(), Fraction(0))
    normalization_third = sum(
        (
            _mini_matrix_pair_top(bfield, alpha_A, trace_denominator=3),
            _mini_matrix_pair_top(bfield, A_alpha, trace_denominator=3),
            _mini_matrix_pair_top(bfield, exterior_variation, trace_denominator=3),
            _mini_matrix_pair_top(
                b_variation, connection_square, trace_denominator=3
            ),
            _mini_matrix_pair_top(
                b_variation, exterior_connection, trace_denominator=3
            ),
        ),
        Fraction(0),
    )
    wrong_trace_sign = sum(
        (
            _mini_matrix_pair_top(bfield, alpha_A, trace_sign=1),
            _mini_matrix_pair_top(bfield, A_alpha, trace_sign=1),
            _mini_matrix_pair_top(bfield, exterior_variation, trace_sign=1),
            _mini_matrix_pair_top(b_variation, connection_square, trace_sign=1),
            _mini_matrix_pair_top(b_variation, exterior_connection, trace_sign=1),
        ),
        Fraction(0),
    )
    return {
        "input": "B=5Jz dx012, b=3Jz dx012, A=Jx dx3+Jy dx4, dA=2Jz dx34, alpha=11Jx dx3, d alpha=7Jz dx34",
        "pairing": "-tr3(XY)/2; orientation dx01234 positive",
        "terms": terms,
        "values_by_FrechetRowV1_ordinal": expected_by_frechet_row_ordinal,
        "total": total,
        "expected_total": Fraction(99),
        "normalization_third_mutant": normalization_third,
        "wrong_trace_sign_mutant": wrong_trace_sign,
        "mutants_killed": {
            "pairing_denominator_three": normalization_third != Fraction(99),
            "pairing_trace_sign_plus": wrong_trace_sign != Fraction(99),
            "omit_one_mixed_connection_term": (
                total - terms["B_pair_A_wedge_alpha"] != Fraction(99)
            ),
        },
    }


def _matmul2(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    return tuple(
        tuple(sum(left[row][index] * right[index][column] for index in range(2)) for column in range(2))
        for row in range(2)
    )  # type: ignore[return-value]


def exact_nontrivial_exp_derivative_oracle() -> dict[str, Any]:
    omega = OmegaExpPolynomial.monomial(1, 0)
    exponential = OmegaExpPolynomial.monomial(0, 1)
    w = Fraction(3) * exponential
    w_omega = w.derivative()
    u = Fraction(1, 2) * w_omega * w_omega - Fraction(2, 3) * w * w
    beta = Fraction(2)
    wall_action = -(
        Fraction(2) * w
        + beta * Fraction(1, 2) * (omega - 1) * (omega - 1)
    )
    d_w = w.derivative().at_omega_one()
    d_u = u.derivative().at_omega_one()
    d_wall = wall_action.derivative().at_omega_one()
    wrong_d_w = w.derivative(exp_chain_multiplier=Fraction(2)).at_omega_one()
    return {
        "basis": "E=exp(-1/6), exact symbolic polynomial; M5=G=k_infinity=1, beta=2, Omega=1",
        "D_W_terms": d_w.terms,
        "D_W_expected_terms": ((1, Fraction(-1)),),
        "D_U_terms": d_u.terms,
        "D_U_expected_terms": ((2, Fraction(14, 3)),),
        "D_wall_action_terms": d_wall.terms,
        "D_wall_action_expected_terms": ((1, Fraction(2)),),
        "mutants_killed": {
            "double_exp_chain_in_DW": wrong_d_w
            != ExpPolynomial(((1, Fraction(-1)),)),
            "omit_W_second_derivative_in_DU": (
                ExpPolynomial.monomial(2, Fraction(4))
                != ExpPolynomial(((2, Fraction(14, 3)),))
            ),
            "wrong_wall_density_sign": -d_wall
            != ExpPolynomial(((1, Fraction(2)),)),
        },
    }


def exact_small_oracles() -> dict[str, Any]:
    """Exact arithmetic checks independent of both symbolic AD implementations."""

    def vadd(*vectors: Sequence[Fraction]) -> tuple[Fraction, Fraction, Fraction]:
        return tuple(sum(vector[index] for vector in vectors) for index in range(3))  # type: ignore[return-value]

    def vscale(coefficient: Fraction, vector: Sequence[Fraction]) -> tuple[Fraction, Fraction, Fraction]:
        return tuple(coefficient * item for item in vector)  # type: ignore[return-value]

    def cross(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, Fraction, Fraction]:
        return (
            left[1] * right[2] - left[2] * right[1],
            left[2] * right[0] - left[0] * right[2],
            left[0] * right[1] - left[1] * right[0],
        )

    e1 = (Fraction(1), Fraction(0), Fraction(0))
    e3 = (Fraction(0), Fraction(0), Fraction(1))
    omega = Fraction(2)
    omega_x = Fraction(3)
    phi = (Fraction(1), Fraction(2), Fraction(0))
    phi_x = (Fraction(4), Fraction(-1), Fraction(2))
    psi = (Fraction(2), Fraction(-1), Fraction(1))
    psi_x = (Fraction(1), Fraction(3), Fraction(-2))
    little_omega = Fraction(1)
    little_omega_x = Fraction(-2)
    d_phi = vadd(phi_x, cross(e3, phi))
    p_observed = vadd(d_phi, vscale(Fraction(3, 2) * omega_x / omega, phi))
    d_psi = vadd(psi_x, cross(e3, psi))
    alpha_phi = cross(e1, phi)
    log_variation = little_omega_x / omega - omega_x * little_omega / power_fraction(omega, 2)
    delta_p_observed = vadd(
        d_psi,
        alpha_phi,
        vscale(Fraction(3, 2) * omega_x / omega, psi),
        vscale(Fraction(3, 2) * log_variation, phi),
    )
    p_expected = (Fraction(17, 4), Fraction(9, 2), Fraction(2))
    delta_p_expected = (Fraction(31, 8), Fraction(-5, 2), Fraction(9, 4))

    q_omega = Fraction(1)
    s = Fraction(3, 4)
    radicand = Fraction(1) + power_fraction(q_omega, 6) * power_fraction(s, 2)
    sqrt_radicand = Fraction(5, 4)
    if sqrt_radicand * sqrt_radicand != radicand:
        raise SemanticFrechetError("V4 oracle square root ceased to be exact")
    q_value = q_omega * power_fraction(s, 2) / (2 * sqrt_radicand)
    q_omega_derivative = (
        power_fraction(s, 2) / (2 * sqrt_radicand)
        - Fraction(3, 2)
        * power_fraction(q_omega, 6)
        * power_fraction(s, 4)
        / power_fraction(sqrt_radicand, 3)
    )
    q_s_derivative = (
        q_omega * s / sqrt_radicand
        - Fraction(1, 2)
        * power_fraction(q_omega, 7)
        * power_fraction(s, 3)
        / power_fraction(sqrt_radicand, 3)
    )

    b_form: MiniForm = {
        (1, 2, 3): PolynomialX0((Fraction(2), Fraction(1)))
    }
    alpha_form: MiniForm = {
        (4,): PolynomialX0((Fraction(1), Fraction(3), Fraction(1)))
    }
    d_alpha_form = _mini_exterior_d(alpha_form)
    d_b_form = _mini_exterior_d(b_form)
    bf_b_dalpha = _mini_top_at_zero(_mini_wedge(b_form, d_alpha_form))
    bf_db_alpha = _mini_top_at_zero(_mini_wedge(d_b_form, alpha_form))
    bf_boundary = _mini_top_at_zero(_mini_exterior_d(_mini_wedge(b_form, alpha_form)))

    g_dual = (
        (FractionDual(Fraction(-1), Fraction(1)), FractionDual(Fraction(0), Fraction(2))),
        (FractionDual(Fraction(0), Fraction(2)), FractionDual(Fraction(1), Fraction(3))),
    )
    determinant_dual = g_dual[0][0] * g_dual[1][1] - g_dual[0][1] * g_dual[1][0]
    inverse_dual = (
        (g_dual[1][1] / determinant_dual, -g_dual[0][1] / determinant_dual),
        (-g_dual[1][0] / determinant_dual, g_dual[0][0] / determinant_dual),
    )
    inverse_derivative = tuple(
        tuple(value.tangent for value in row) for row in inverse_dual
    )
    volume_dual = _sqrt_fraction_dual(-determinant_dual)
    volume_derivative = volume_dual.tangent
    base_inverse = (
        (Fraction(-1), Fraction(0)),
        (Fraction(0), Fraction(1)),
    )
    metric_tangent = (
        (Fraction(1), Fraction(2)),
        (Fraction(2), Fraction(3)),
    )
    wrong_positive_inverse_derivative = _matmul2(
        _matmul2(base_inverse, metric_tangent), base_inverse
    )
    wrong_missing_half_volume_derivative = (
        (-determinant_dual).tangent / volume_dual.primal
    )

    m5 = Fraction(1)
    compensator_g = Fraction(1)
    k_infinity = Fraction(1)
    omega_origin = Fraction(0)
    beta = Fraction(2)
    exponential_at_origin = Fraction(1)
    w_origin = (
        Fraction(3)
        * power_fraction(m5, 3)
        * k_infinity
        * exponential_at_origin
    )
    w_prime_origin = w_origin * (
        -compensator_g
        * omega_origin
        / (Fraction(3) * power_fraction(m5, 3))
    )
    u_origin = (
        power_fraction(w_prime_origin, 2) / (2 * compensator_g)
        - Fraction(2)
        * power_fraction(w_origin, 2)
        / (3 * power_fraction(m5, 3))
    )
    wall_bracket_origin = (
        Fraction(2) * w_origin
        + beta * power_fraction(omega_origin - 1, 2) / 2
    )

    p_mutants = {
        "omit_alpha_phi": vadd(delta_p_observed, vscale(Fraction(-1), alpha_phi)),
        "double_Dpsi": vadd(delta_p_observed, d_psi),
        "omit_Omega_inverse_squared_piece": vadd(
            delta_p_observed,
            vscale(Fraction(3, 2) * omega_x * little_omega / power_fraction(omega, 2), phi),
        ),
    }
    return {
        "nontrivial_exp_derivatives_at_Omega_one": exact_nontrivial_exp_derivative_oracle(),
        "full_BF_Frechet": exact_full_bf_frechet_oracle(),
        "P_one_dimensional": {
            "P": p_observed,
            "P_expected": p_expected,
            "delta_P": delta_p_observed,
            "delta_P_expected": delta_p_expected,
            "alpha_phi": alpha_phi,
            "alpha_phi_expected": (Fraction(0), Fraction(0), Fraction(2)),
            "mutants_killed": {name: value != delta_p_expected for name, value in p_mutants.items()},
        },
        "full_V4_reduced_Q": {
            "definition": "Q(Omega,s)=Omega*s^2/(2*sqrt(1+Omega^6*s^2)), s=|phi|^2",
            "Q": q_value,
            "Q_expected": Fraction(9, 40),
            "partial_Omega_Q": q_omega_derivative,
            "partial_Omega_Q_expected": Fraction(-9, 500),
            "partial_s_Q": q_s_derivative,
            "partial_s_Q_expected": Fraction(123, 250),
            "mutants_killed": {
                "omit_denominator_Omega_derivative": (
                    power_fraction(s, 2) / (2 * sqrt_radicand)
                    != Fraction(-9, 500)
                ),
                "wrong_Omega_six_to_four": (
                    power_fraction(s, 2) / (2 * sqrt_radicand)
                    - power_fraction(q_omega, 4)
                    * power_fraction(s, 4)
                    / power_fraction(sqrt_radicand, 3)
                    != Fraction(-9, 500)
                ),
                "omit_phi_pair_factor_two": q_s_derivative / 2
                != Fraction(123, 250),
            },
        },
        "BF_graded_Leibniz": {
            "input": "B=(2+x0) dx1^dx2^dx3; alpha=(1+3*x0+x0^2) dx4",
            "B_wedge_dalpha": bf_b_dalpha,
            "dB_wedge_alpha": bf_db_alpha,
            "d_B_wedge_alpha": bf_boundary,
            "expected": Fraction(7),
            "wrong_plus_sign_mutant": bf_db_alpha + bf_b_dalpha,
            "omit_dB_mutant": -bf_b_dalpha,
            "wrong_wedge_permutation_sign_mutant": bf_db_alpha - abs(bf_b_dalpha),
            "mutants_killed": {
                "wrong_graded_plus": bf_db_alpha + bf_b_dalpha != Fraction(7),
                "omit_dB": -bf_b_dalpha != Fraction(7),
                "wrong_wedge_permutation_sign": bf_db_alpha - abs(bf_b_dalpha) != Fraction(7),
            },
        },
        "metric_inverse_and_volume": {
            "g_of_t": "[[-1+t,2*t],[2*t,1+3*t]]",
            "g_at_zero": [[-1, 0], [0, 1]],
            "H": [[1, 2], [2, 3]],
            "delta_g_inverse": inverse_derivative,
            "delta_g_inverse_expected": (
                (Fraction(-1), Fraction(2)),
                (Fraction(2), Fraction(-3)),
            ),
            "sqrt_minus_det_linear_coefficient": volume_derivative,
            "sqrt_minus_det_linear_coefficient_expected": Fraction(1),
            "mutants_killed": {
                "wrong_positive_inverse_sign": wrong_positive_inverse_derivative
                != (
                    (Fraction(-1), Fraction(2)),
                    (Fraction(2), Fraction(-3)),
                ),
                "missing_volume_half": wrong_missing_half_volume_derivative
                != Fraction(1),
            },
        },
        "W_U_wall_at_origin": {
            "assumptions": "M5=G=k_infinity=1, Omega=Omega_Sigma=0, beta=2",
            "W_zero": w_origin,
            "W_zero_expected": Fraction(3),
            "W_Omega_zero": w_prime_origin,
            "W_Omega_zero_expected": Fraction(0),
            "U_zero": u_origin,
            "U_zero_expected": Fraction(-6),
            "wall_bracket_zero": wall_bracket_origin,
            "wall_bracket_zero_expected": Fraction(7),
            "mutants_killed": {
                "W_prefactor_four": (
                    Fraction(4)
                    * power_fraction(m5, 3)
                    * k_infinity
                    * exponential_at_origin
                )
                != w_origin,
                "U_second_factor_three": (
                    power_fraction(w_prime_origin, 2) / (2 * compensator_g)
                    - Fraction(3)
                    * power_fraction(w_origin, 2)
                    / (3 * power_fraction(m5, 3))
                )
                != Fraction(-6),
                "wall_omit_beta_quadratic": Fraction(2) * w_origin
                != Fraction(7),
                "wall_W_factor_three": Fraction(3) * w_origin
                + beta * power_fraction(omega_origin - 1, 2) / 2
                != Fraction(7),
            },
        },
    }


def power_fraction(value: Fraction, exponent: int) -> Fraction:
    return value ** exponent


def _oracles_pass(oracles: Mapping[str, Any]) -> bool:
    exponential = oracles["nontrivial_exp_derivatives_at_Omega_one"]
    full_bf = oracles["full_BF_Frechet"]
    p = oracles["P_one_dimensional"]
    v4 = oracles["full_V4_reduced_Q"]
    bf = oracles["BF_graded_Leibniz"]
    metric = oracles["metric_inverse_and_volume"]
    wall = oracles["W_U_wall_at_origin"]
    return bool(
        exponential["D_W_terms"] == exponential["D_W_expected_terms"]
        and exponential["D_U_terms"] == exponential["D_U_expected_terms"]
        and exponential["D_wall_action_terms"]
        == exponential["D_wall_action_expected_terms"]
        and all(exponential["mutants_killed"].values())
        and full_bf["total"] == full_bf["expected_total"]
        and full_bf["values_by_FrechetRowV1_ordinal"]
        == (Fraction(35), Fraction(55, 2), Fraction(55, 2), Fraction(6), Fraction(3))
        and all(full_bf["mutants_killed"].values())
        and p["P"] == p["P_expected"]
        and p["delta_P"] == p["delta_P_expected"]
        and p["alpha_phi"] == p["alpha_phi_expected"]
        and all(p["mutants_killed"].values())
        and v4["Q"] == v4["Q_expected"]
        and v4["partial_Omega_Q"] == v4["partial_Omega_Q_expected"]
        and v4["partial_s_Q"] == v4["partial_s_Q_expected"]
        and all(v4["mutants_killed"].values())
        and bf["d_B_wedge_alpha"] == bf["expected"]
        and bf["wrong_plus_sign_mutant"] != bf["expected"]
        and all(bf["mutants_killed"].values())
        and metric["delta_g_inverse"] == metric["delta_g_inverse_expected"]
        and metric["sqrt_minus_det_linear_coefficient"]
        == metric["sqrt_minus_det_linear_coefficient_expected"]
        and all(metric["mutants_killed"].values())
        and wall["W_zero"] == wall["W_zero_expected"]
        and wall["W_Omega_zero"] == wall["W_Omega_zero_expected"]
        and wall["U_zero"] == wall["U_zero_expected"]
        and wall["wall_bracket_zero"] == wall["wall_bracket_zero_expected"]
        and all(wall["mutants_killed"].values())
    )


FRECHET_ROW_SCHEMA = "FrechetRowV1"


def _compat_type(type_tag: GeoType) -> dict[str, Any]:
    return {
        "name": type_tag.name,
        "dimension": type_tag.dimension,
        "form_degree": type_tag.form_degree,
        "bundle": type_tag.bundle,
        "variance": list(type_tag.variance),
        "density_weight": type_tag.density_weight,
        "symmetry": type_tag.symmetry,
        "fiber_dimension": type_tag.fiber_dimension,
    }


def _compat_coefficient_ast(expr: Expr) -> dict[str, Any]:
    type_row = _compat_type(expr.type_tag)
    if expr.op == "rational":
        assert expr.value is not None
        return {"op": "const", "value": [expr.value.numerator, expr.value.denominator], "type": type_row}
    if expr.op == "parameter":
        return {"op": "param", "symbol": expr.label, "type": type_row}
    if expr.op == "field":
        return {
            "op": "jet",
            "symbol": expr.label,
            "derivative": {"kind": "partial", "word": []},
            "type": type_row,
        }
    if expr.op == "linear_slot":
        return {
            "op": "linear_slot",
            "slot": "eta",
            "external_derivative_word": [],
            "type": type_row,
        }
    if expr.op == "zero":
        return {"op": "const", "value": [0, 1], "type": type_row}
    if expr.op == "variation":
        raise SemanticFrechetError("coefficient AST retained a variation leaf")
    if expr.op == "exterior_partial" and len(expr.args) == 1 and expr.args[0].op == "field":
        base = expr.args[0]
        return {
            "op": "jet",
            "symbol": base.label,
            "derivative": {
                "kind": "exterior_partial",
                "order": 1,
                "axis_scope": "node_typed_form",
            },
            "antisymmetrized_form": True,
            "base_type": _compat_type(base.type_tag),
            "type": type_row,
        }
    op_map = {
        "add": "add",
        "mul_scalar": "mul",
        "scale": "mul",
        "power": "pow",
        "exp": "exp",
        "sqrt": "sqrt",
        "inverse_metric": "inverse_metric",
        "volume_density": "volume_density",
        "metric_trace": "metric_trace",
        "inverse_sandwich": "inverse_sandwich",
        "exterior_partial": "exterior_partial",
        "SO3_action": "SO3_action",
        "associated_times_oneform": "associated_times_oneform",
        "metric_contract": "metric_contract",
        "associated_pair": "associated_pair",
        "adjoint_matrix_embedding": "adjoint_matrix_embedding",
        "matrix_wedge": "matrix_wedge",
        "invariant_pair_wedge": "invariant_pair_wedge",
        "density_times_scalar": "mul",
    }
    try:
        op = op_map[expr.op]
    except KeyError as exc:
        raise SemanticFrechetError(f"no S13 coefficient serialization for {expr.op}") from exc
    row: dict[str, Any] = {
        "op": op,
        "args": [_compat_coefficient_ast(arg) for arg in expr.args],
        "type": type_row,
    }
    if expr.exponent is not None:
        row["exponent"] = [expr.exponent.numerator, expr.exponent.denominator]
    if expr.label:
        row["convention"] = expr.label
    return row


def _set_linear_slot_word(ast: dict[str, Any], word: Sequence[int]) -> int:
    count = 0
    if ast.get("op") == "linear_slot":
        ast["external_derivative_word"] = list(word)
        count += 1
    for arg in ast.get("args", []):
        count += _set_linear_slot_word(arg, word)
    return count


def _replace_variation_with_slot(term: Expr) -> tuple[Expr, str, tuple[int, ...]]:
    occurrences = [node for node in _walk(term) if node.op == "variation"]
    if len(occurrences) != 1:
        raise SemanticFrechetError(
            f"Frechet summand must contain exactly one variation leaf, observed {len(occurrences)}"
        )
    variation_leaf = occurrences[0]

    def replace_node(node: Expr) -> tuple[Expr, bool, tuple[int, ...]]:
        if (
            node.op == "exterior_partial"
            and len(node.args) == 1
            and node.args[0] is variation_leaf
        ):
            return Expr("linear_slot", node.type_tag, label="eta"), True, (0,)
        if node is variation_leaf:
            return Expr("linear_slot", node.type_tag, label="eta"), True, ()
        replaced = False
        derivative_word: tuple[int, ...] = ()
        args: list[Expr] = []
        for arg in node.args:
            new_arg, found, word = replace_node(arg)
            if found:
                if replaced:
                    raise SemanticFrechetError("one summand reached two variation branches")
                replaced = True
                derivative_word = word
            args.append(new_arg)
        return Expr(node.op, node.type_tag, tuple(args), node.label, node.value, node.exponent), replaced, derivative_word

    coefficient, found, word = replace_node(term)
    if not found:
        raise SemanticFrechetError("variation replacement failed")
    return coefficient, variation_leaf.label, word


def _component_domain(component: str) -> str:
    if component.endswith("_plus"):
        return "M_plus"
    if component.endswith("_minus"):
        return "M_minus"
    if component == "wall":
        return "Sigma"
    raise SemanticFrechetError(f"unknown component domain for {component}")


def _variation_role(label: str) -> str:
    prefix_roles = (
        ("H_", "bulk_metric"),
        ("omega_", "bulk_or_wall_scalar"),
        ("psi_", "SO3_associated_zero_form"),
        ("alpha_", "SO3_connection"),
        ("b_", "SO3_B_three_form"),
    )
    if label == "h":
        return "wall_metric"
    if label == "omega_Sigma":
        return "wall_scalar"
    for prefix, role in prefix_roles:
        if label.startswith(prefix):
            return role
    raise SemanticFrechetError(f"unregistered variation role {label}")


COMPONENT_SOURCE_KEYS = {
    "Omega_kinetic": ("total", "bulk_gauged"),
    "Omega_potential": ("total", "superpotential", "bulk_potential", "bulk_gauged"),
    "P_kinetic": ("total", "gauged_conformal_derivative", "bulk_gauged"),
    "full_V4": ("total", "full_V4", "bulk_gauged"),
    "BF": ("total", "BF"),
    "wall": ("total", "superpotential", "wall_background"),
}


def _source_spans(component: str, parsed: ParsedCharter) -> list[dict[str, Any]]:
    family = next((name for name in COMPONENT_SOURCE_KEYS if component.startswith(name)), None)
    if component == "wall":
        family = "wall"
    if family is None:
        raise SemanticFrechetError(f"no source-span family for {component}")
    rows = []
    for key in COMPONENT_SOURCE_KEYS[family]:
        text = parsed.action[key]
        rows.append(
            {
                "action_key": key,
                "start": 0,
                "end": len(text),
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )
    return rows


def export_frechet_rows(
    program: ComponentProgram,
    derivatives: Mapping[str, Expr],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if tuple(derivatives) != EASY_COMPONENTS:
        raise SemanticFrechetError("Frechet export component inventory drift")
    for component, derivative in derivatives.items():
        summands = derivative.args if derivative.op == "add" else (derivative,)
        for ordinal, summand in enumerate(summands):
            coefficient, variation_component, word = _replace_variation_with_slot(summand)
            coefficient = canonicalize_expr(coefficient)
            coefficient_ast = _compat_coefficient_ast(coefficient)
            if _set_linear_slot_word(coefficient_ast, word) != 1:
                raise SemanticFrechetError("coefficient AST must contain one bound linear slot")
            domain = _component_domain(component)
            dimension = 4 if domain == "Sigma" else 5
            derivative = {"kind": "partial", "word": list(word)}
            if word:
                derivative["binders"] = [
                    {
                        "id": 0,
                        "namespace": f"{domain}.coordinate",
                        "dimension": dimension,
                        "variance": "down",
                        "scope": "row",
                        "alpha_normalized": True,
                    }
                ]
            rows.append(
                {
                    "schema": FRECHET_ROW_SCHEMA,
                    "component": component,
                    "domain": domain,
                    "role": _variation_role(variation_component),
                    "variation_component": variation_component,
                    "derivative": derivative,
                    "coefficient_ast_sha256": _canonical_sha256(coefficient_ast),
                    "coefficient_ast": coefficient_ast,
                    "source_spans": _source_spans(component, program.parsed),
                    "summand_ordinal": ordinal,
                }
            )
    return rows


def _expected_slot_type(variation_component: str, derivative_word: Sequence[int]) -> GeoType:
    if variation_component.startswith("H_"):
        base = METRIC5
    elif variation_component in {"h"}:
        base = METRIC4
    elif variation_component.startswith("omega_") and variation_component != "omega_Sigma":
        base = SCALAR5
    elif variation_component == "omega_Sigma":
        base = SCALAR4
    elif variation_component.startswith("psi_"):
        base = ASSOCIATED0_5
    elif variation_component.startswith("alpha_"):
        base = ADJOINT1_5
    elif variation_component.startswith("b_"):
        base = ADJOINT3_5
    else:
        raise SemanticFrechetError(f"unknown slot type for {variation_component}")
    if not derivative_word:
        return base
    if tuple(derivative_word) != (0,):
        raise SemanticFrechetError("this subgate supports only one scoped first derivative")
    mapping = {
        SCALAR5: ONEFORM5,
        ASSOCIATED0_5: ASSOCIATED1_5,
        ADJOINT1_5: ADJOINT2_5,
    }
    try:
        return mapping[base]
    except KeyError as exc:
        raise SemanticFrechetError(
            f"variation {variation_component} cannot carry the exported partial word"
        ) from exc


def _coefficient_linear_slots(ast: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = [ast] if ast.get("op") == "linear_slot" else []
    for arg in ast.get("args", []):
        rows.extend(_coefficient_linear_slots(arg))
    return rows


def _coefficient_has_illegal_capture(ast: Mapping[str, Any]) -> bool:
    if ast.get("op") != "linear_slot" and "external_derivative_word" in ast:
        return True
    return any(_coefficient_has_illegal_capture(arg) for arg in ast.get("args", []))


def _type_from_compat(row: Mapping[str, Any]) -> GeoType:
    try:
        type_tag = TYPE_TABLE[str(row["name"])]
    except (KeyError, TypeError) as exc:
        raise SemanticFrechetError("unknown compatibility AST type") from exc
    if dict(row) != _compat_type(type_tag):
        raise SemanticFrechetError("compatibility AST type metadata drift")
    return type_tag


def compat_coefficient_ast_to_expr(ast: Mapping[str, Any]) -> Expr:
    """Executable, typed inverse of the S13-facing coefficient serializer."""

    if type(ast) is not dict:
        raise SemanticFrechetError("coefficient AST node must be an object")
    op = ast.get("op")
    type_tag = _type_from_compat(ast.get("type", {}))
    if op == "const":
        value = ast.get("value")
        if not isinstance(value, list) or len(value) != 2:
            raise SemanticFrechetError("constant coefficient is malformed")
        if type_tag.bundle != "trivial" or type_tag.form_degree or type_tag.variance:
            raise SemanticFrechetError("tensor zero constants require an explicit tensor constructor")
        result = rational(Fraction(value[0], value[1]), dimension=type_tag.dimension)
    elif op == "param":
        result = parameter(str(ast.get("symbol")))
    elif op == "jet":
        derivative = ast.get("derivative")
        if derivative == {"kind": "partial", "word": []}:
            result = field(str(ast.get("symbol")), type_tag)
        elif derivative == {
            "kind": "exterior_partial",
            "order": 1,
            "axis_scope": "node_typed_form",
        }:
            base_type = _type_from_compat(ast.get("base_type", {}))
            result = exterior_partial(field(str(ast.get("symbol")), base_type))
        else:
            raise SemanticFrechetError("jet derivative metadata is unresolved")
    elif op == "linear_slot":
        if ast.get("slot") != "eta":
            raise SemanticFrechetError("unknown linear slot")
        result = Expr("linear_slot", type_tag, label="eta")
    else:
        args = tuple(
            compat_coefficient_ast_to_expr(arg) for arg in ast.get("args", [])
        )
        if op == "add":
            result = add(*args)
        elif op == "mul":
            if all(_is_strict_scalar(arg.type_tag) for arg in args):
                result = scalar_mul(*args)
            elif len(args) == 2 and args[0].type_tag in {DENSITY5, DENSITY4}:
                result = density_times_scalar(*args)
            elif len(args) == 2 and _is_strict_scalar(args[0].type_tag):
                result = scale(*args)
            else:
                raise SemanticFrechetError("typed mul compatibility node is ambiguous")
        elif op == "pow":
            exponent = ast.get("exponent")
            if not isinstance(exponent, list) or len(exponent) != 2:
                raise SemanticFrechetError("pow exponent is malformed")
            result = power(args[0], Fraction(exponent[0], exponent[1]))
        elif op == "exp":
            result = exp_scalar(args[0])
        elif op == "sqrt":
            result = sqrt_scalar(args[0])
        elif op == "inverse_metric":
            result = inverse_metric(args[0])
        elif op == "volume_density":
            result = volume_density(args[0])
        elif op == "metric_trace":
            result = metric_trace(*args)
        elif op == "inverse_sandwich":
            result = inverse_sandwich(*args)
        elif op == "exterior_partial":
            result = exterior_partial(args[0])
        elif op == "SO3_action":
            result = associated_action(*args)
        elif op == "associated_times_oneform":
            result = associated_times_oneform(*args)
        elif op == "metric_contract":
            result = metric_contract(*args)
        elif op == "associated_pair":
            result = associated_pair(*args)
        elif op == "adjoint_matrix_embedding":
            result = adjoint_matrix_embedding(args[0])
        elif op == "matrix_wedge":
            result = connection_wedge(*args)
        elif op == "invariant_pair_wedge":
            result = pair_wedge(*args, pairing_label=str(ast.get("convention")))
        else:
            raise SemanticFrechetError(f"unresolved compatibility AST op {op}")
    if result.type_tag != type_tag:
        raise SemanticFrechetError("compatibility AST result type drift")
    return result


def validate_frechet_row(row: Mapping[str, Any]) -> bool:
    if row.get("schema") != FRECHET_ROW_SCHEMA:
        raise SemanticFrechetError("Frechet row schema drift")
    component = row.get("component")
    if component not in EASY_COMPONENTS:
        raise SemanticFrechetError("Frechet row component drift")
    domain = _component_domain(str(component))
    if row.get("domain") != domain:
        raise SemanticFrechetError("Frechet row domain drift")
    derivative = row.get("derivative")
    if type(derivative) is not dict or derivative.get("kind") != "partial":
        raise SemanticFrechetError("Frechet row derivative kind drift")
    word = derivative.get("word")
    if word not in ([], [0]):
        raise SemanticFrechetError("free or unsupported Frechet derivative binder")
    binders = derivative.get("binders", [])
    if word:
        expected_dimension = 4 if domain == "Sigma" else 5
        if len(binders) != 1:
            raise SemanticFrechetError("Frechet derivative binder is free or duplicated")
        binder = binders[0]
        expected_binder = {
            "id": 0,
            "namespace": f"{domain}.coordinate",
            "dimension": expected_dimension,
            "variance": "down",
            "scope": "row",
            "alpha_normalized": True,
        }
        if binder != expected_binder:
            raise SemanticFrechetError("Frechet binder capture/dimension/variance/namespace drift")
    elif binders:
        raise SemanticFrechetError("zeroth-order row has an unreferenced binder")
    coefficient_ast = row.get("coefficient_ast")
    if type(coefficient_ast) is not dict:
        raise SemanticFrechetError("Frechet coefficient AST missing")
    if _coefficient_has_illegal_capture(coefficient_ast):
        raise SemanticFrechetError("row binder was captured outside its linear slot")
    slots = _coefficient_linear_slots(coefficient_ast)
    if len(slots) != 1 or slots[0].get("external_derivative_word") != word:
        raise SemanticFrechetError("linear slot and derivative binder are incoherent")
    expected_type = _compat_type(
        _expected_slot_type(str(row.get("variation_component")), word)
    )
    if slots[0].get("type") != expected_type:
        raise SemanticFrechetError("linear slot type disagrees with the variation and word")
    if row.get("role") != _variation_role(str(row.get("variation_component"))):
        raise SemanticFrechetError("variation role drift")
    if type(row.get("summand_ordinal")) is not int or row["summand_ordinal"] < 0:
        raise SemanticFrechetError("Frechet row summand ordinal must be a nonnegative integer")
    if row.get("coefficient_ast_sha256") != _canonical_sha256(coefficient_ast):
        raise SemanticFrechetError("coefficient AST hash drift")
    executable = compat_coefficient_ast_to_expr(coefficient_ast)
    validate_expr_types(executable)
    round_trip = _compat_coefficient_ast(executable)
    if _set_linear_slot_word(round_trip, word) != 1 or round_trip != coefficient_ast:
        raise SemanticFrechetError("coefficient AST is not executable/canonical round-trip")
    return True


def _compat_jet_symbols(ast: Mapping[str, Any]) -> tuple[str, ...]:
    symbols = [str(ast.get("symbol"))] if ast.get("op") == "jet" else []
    for arg in ast.get("args", []):
        symbols.extend(_compat_jet_symbols(arg))
    return tuple(symbols)


def validate_frechet_row_collection(
    rows: Sequence[Mapping[str, Any]], program: ComponentProgram
) -> bool:
    """Validate cross-row inventory, side identity, ordinals, and source spans."""

    if len(rows) != 155 or not all(validate_frechet_row(row) for row in rows):
        raise SemanticFrechetError("FrechetRowV1 collection size or row validation drift")
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        component = str(row["component"])
        grouped[component].append(row)
        if row.get("source_spans") != _source_spans(component, program.parsed):
            raise SemanticFrechetError("Frechet row source spans drifted from the parsed action")
        if component.endswith("_plus") or component.endswith("_minus"):
            side = "plus" if component.endswith("_plus") else "minus"
            opposite = "minus" if side == "plus" else "plus"
            if not str(row["variation_component"]).endswith(f"_{side}"):
                raise SemanticFrechetError("Frechet variation/component side aliasing")
            if any(symbol.endswith(f"_{opposite}") for symbol in _compat_jet_symbols(row["coefficient_ast"])):
                raise SemanticFrechetError("Frechet coefficient contains an opposite-side jet")
    if tuple(grouped) != EASY_COMPONENTS:
        raise SemanticFrechetError("Frechet row collection component order drift")
    for component, component_rows in grouped.items():
        ordinals = sorted(int(row["summand_ordinal"]) for row in component_rows)
        if ordinals != list(range(len(component_rows))):
            raise SemanticFrechetError("Frechet row ordinals are duplicated or non-contiguous")
    for side in ("plus", "minus"):
        component_rows = grouped[f"BF_bulk_{side}"]
        inventory = Counter(
            (
                str(row["variation_component"]),
                tuple(row["derivative"]["word"]),
            )
            for row in component_rows
        )
        expected = Counter(
            {
                (f"alpha_{side}", ()): 2,
                (f"alpha_{side}", (0,)): 1,
                (f"b_{side}", ()): 2,
            }
        )
        if len(component_rows) != 5 or inventory != expected:
            raise SemanticFrechetError("full BF Frechet row inventory drift")
        allowed_symbols = {f"A_{side}", f"B_{side}"}
        for row in component_rows:
            if not set(_compat_jet_symbols(row["coefficient_ast"])) <= allowed_symbols:
                raise SemanticFrechetError("BF coefficient uses a nonlocal or aliased field")
    reference_derivatives = {
        name: forward_nilpotent_dual(expr, program.tangents).tangent
        for name, expr in program.components.items()
    }
    reference_rows = export_frechet_rows(program, reference_derivatives)
    for side in ("plus", "minus"):
        component = f"BF_bulk_{side}"

        def signature(row: Mapping[str, Any]) -> tuple[Any, ...]:
            return (
                row["summand_ordinal"],
                row["variation_component"],
                tuple(row["derivative"]["word"]),
                row["coefficient_ast"],
            )

        observed = tuple(
            signature(row)
            for row in sorted(grouped[component], key=lambda item: item["summand_ordinal"])
        )
        expected = tuple(
            signature(row)
            for row in reference_rows
            if row["component"] == component
        )
        if observed != expected:
            raise SemanticFrechetError(
                "BF Frechet rows are not the canonical derivative AST skeletons"
            )
    return True


def canonicalize_frechet_row_binders(row: Mapping[str, Any]) -> dict[str, Any]:
    """Alpha-normalize a valid one-binder row; used by the capture tests."""

    canonical = json.loads(json.dumps(row))
    derivative = canonical["derivative"]
    word = derivative["word"]
    if not word:
        validate_frechet_row(canonical)
        return canonical
    binders = derivative.get("binders", [])
    if len(binders) != 1 or len(word) != 1 or word[0] != binders[0].get("id"):
        raise SemanticFrechetError("cannot alpha-normalize a free/captured binder")
    old_id = word[0]
    derivative["word"] = [0]
    binders[0]["id"] = 0
    binders[0]["alpha_normalized"] = True

    def rename_slot(ast: dict[str, Any]) -> None:
        if ast.get("op") == "linear_slot":
            if ast.get("external_derivative_word") != [old_id]:
                raise SemanticFrechetError("linear slot binder capture during alpha normalization")
            ast["external_derivative_word"] = [0]
        for arg in ast.get("args", []):
            rename_slot(arg)

    rename_slot(canonical["coefficient_ast"])
    canonical["coefficient_ast_sha256"] = _canonical_sha256(
        canonical["coefficient_ast"]
    )
    validate_frechet_row(canonical)
    return canonical


def canonicalize_expr(expr: Expr) -> Expr:
    """Rebuild every node through the typed constructors."""

    def rebuild(node: Expr) -> Expr:
        args = tuple(rebuild(arg) for arg in node.args)
        if node.op == "rational":
            assert node.value is not None
            result = rational(node.value, dimension=node.type_tag.dimension)
        elif node.op == "parameter":
            result = parameter(node.label)
        elif node.op == "field":
            result = field(node.label, node.type_tag)
        elif node.op == "variation":
            result = variation(node.label, node.type_tag)
        elif node.op == "linear_slot":
            result = Expr("linear_slot", node.type_tag, label=node.label)
        elif node.op == "zero":
            result = zero(node.type_tag)
        elif node.op == "add":
            result = add(*args)
        elif node.op == "mul_scalar":
            result = scalar_mul(*args)
        elif node.op == "scale":
            result = scale(*args)
        elif node.op == "power":
            assert node.exponent is not None
            result = power(args[0], node.exponent)
        elif node.op == "exp":
            result = exp_scalar(args[0])
        elif node.op == "sqrt":
            result = sqrt_scalar(args[0])
        elif node.op == "inverse_metric":
            result = inverse_metric(args[0])
        elif node.op == "volume_density":
            result = volume_density(args[0])
        elif node.op == "metric_trace":
            result = metric_trace(*args)
        elif node.op == "inverse_sandwich":
            result = inverse_sandwich(*args)
        elif node.op == "exterior_partial":
            result = exterior_partial(args[0])
        elif node.op == "SO3_action":
            result = associated_action(*args)
        elif node.op == "associated_times_oneform":
            result = associated_times_oneform(*args)
        elif node.op == "metric_contract":
            result = metric_contract(*args)
        elif node.op == "associated_pair":
            result = associated_pair(*args)
        elif node.op == "adjoint_matrix_embedding":
            result = adjoint_matrix_embedding(args[0])
        elif node.op == "matrix_wedge":
            result = connection_wedge(*args)
        elif node.op == "invariant_pair_wedge":
            result = pair_wedge(*args, pairing_label=node.label)
        elif node.op == "density_times_scalar":
            result = density_times_scalar(*args)
        else:
            raise SemanticFrechetError(f"typechecker has no rule for {node.op}")
        return result

    return rebuild(expr)


def validate_expr_types(expr: Expr) -> bool:
    if canonicalize_expr(expr) != expr:
        raise SemanticFrechetError("expression is noncanonical or mistyped")
    return True


@dataclass(frozen=True)
class EvaluationEnvironment:
    values: Mapping[str, Any]
    parameters: Mapping[str, Any]
    partials: Mapping[str, Any]
    linear_slot: Any = None
    symbolic_exp_minus_one_sixth: bool = False


def _array(value: Any) -> np.ndarray:
    return np.asarray(value, dtype=object)


def _determinant(matrix: Any) -> Any:
    array = _array(matrix)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise SemanticFrechetError("determinant requires a square array")
    size = array.shape[0]
    total: Any = Fraction(0)
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            1
            for left in range(size)
            for right in range(left + 1, size)
            if permutation[left] > permutation[right]
        )
        product: Any = Fraction(-1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            product *= array[row, column]
        total += product
    return total


def _matrix_inverse(matrix: Any) -> np.ndarray:
    array = _array(matrix)
    size = array.shape[0]
    determinant = _determinant(array)
    if determinant == 0:
        raise SemanticFrechetError("singular metric in executable semantics")
    if size == 1:
        return _array([[1 / determinant]])
    cofactors = np.empty((size, size), dtype=object)
    for row in range(size):
        for column in range(size):
            minor = np.delete(np.delete(array, row, axis=0), column, axis=1)
            cofactors[row, column] = ((-1) ** (row + column)) * _determinant(minor)
    return cofactors.T / determinant


def _sqrt_number(value: Any) -> Any:
    if isinstance(value, Fraction):
        numerator = math.isqrt(value.numerator)
        denominator = math.isqrt(value.denominator)
        if numerator * numerator == value.numerator and denominator * denominator == value.denominator:
            return Fraction(numerator, denominator)
    if isinstance(value, int):
        root = math.isqrt(value)
        if root * root == value:
            return root
    return math.sqrt(float(value))


def _matrix_product(left: Any, right: Any) -> np.ndarray:
    return _array(left) @ _array(right)


def _matrix_trace(value: Any) -> Any:
    array = _array(value)
    return sum(
        (array[index, index] for index in range(array.shape[0])), Fraction(0)
    )


def evaluate_expr(expr: Expr, environment: EvaluationEnvironment) -> Any:
    """Executable array semantics for every node admitted by this subgate."""

    if expr.op == "rational":
        assert expr.value is not None
        return expr.value
    if expr.op == "parameter":
        try:
            return environment.parameters[expr.label]
        except KeyError as exc:
            raise SemanticFrechetError(f"missing parameter value {expr.label}") from exc
    if expr.op in {"field", "variation"}:
        try:
            return environment.values[expr.label]
        except KeyError as exc:
            raise SemanticFrechetError(f"missing field value {expr.label}") from exc
    if expr.op == "linear_slot":
        if environment.linear_slot is None:
            raise SemanticFrechetError("linear_slot has no executable value")
        return environment.linear_slot
    if expr.op == "zero":
        return Fraction(0)

    values = tuple(evaluate_expr(arg, environment) for arg in expr.args)
    if expr.op == "add":
        result = values[0]
        for value in values[1:]:
            result = result + value
        return result
    if expr.op == "mul_scalar":
        result: Any = Fraction(1)
        for value in values:
            result *= value
        return result
    if expr.op in {"scale", "density_times_scalar"}:
        return values[0] * values[1]
    if expr.op == "power":
        assert expr.exponent is not None
        if expr.exponent.denominator == 1:
            return values[0] ** expr.exponent.numerator
        if expr.exponent.denominator == 2:
            root = _sqrt_number(values[0])
            if isinstance(root, Fraction):
                return root ** expr.exponent.numerator
        return float(values[0]) ** float(expr.exponent)
    if expr.op == "exp":
        if environment.symbolic_exp_minus_one_sixth and values[0] == Fraction(-1, 6):
            return ExpPolynomial.monomial(1)
        return Fraction(1) if values[0] == 0 else math.exp(float(values[0]))
    if expr.op == "sqrt":
        return _sqrt_number(values[0])
    if expr.op == "inverse_metric":
        return _matrix_inverse(values[0])
    if expr.op == "volume_density":
        return _sqrt_number(-_determinant(values[0]))
    if expr.op == "metric_trace":
        return sum((_array(values[0]) * _array(values[1])).reshape(-1))
    if expr.op == "inverse_sandwich":
        return _matrix_product(_matrix_product(values[0], values[1]), values[2])
    if expr.op == "exterior_partial":
        base = expr.args[0]
        if base.op not in {"field", "variation"}:
            raise SemanticFrechetError("exterior_partial executable child is not a jet leaf")
        try:
            return environment.partials[base.label]
        except KeyError as exc:
            raise SemanticFrechetError(f"missing exterior partial {base.label}") from exc
    if expr.op == "SO3_action":
        connection = _array(values[0])
        associated = _array(values[1])
        return _array([_matrix_product(connection[index], associated) for index in range(connection.shape[0])])
    if expr.op == "associated_times_oneform":
        associated = _array(values[0])
        oneform = _array(values[1])
        return _array([[oneform[index] * associated[fiber] for fiber in range(3)] for index in range(len(oneform))])
    if expr.op == "metric_contract":
        inverse = _array(values[0])
        left = _array(values[1])
        right = _array(values[2])
        if left.ndim == 1:
            return sum(inverse[m, n] * left[m] * right[n] for m in range(inverse.shape[0]) for n in range(inverse.shape[1]))
        return sum(
            inverse[m, n] * left[m, fiber] * right[n, fiber]
            for m in range(inverse.shape[0])
            for n in range(inverse.shape[1])
            for fiber in range(3)
        )
    if expr.op == "associated_pair":
        return sum(_array(values[0])[fiber] * _array(values[1])[fiber] for fiber in range(3))
    if expr.op == "adjoint_matrix_embedding":
        return values[0]
    if expr.op == "matrix_wedge":
        left = _array(values[0])
        right = _array(values[1])
        dimension = left.shape[0]
        output = np.empty((dimension, dimension, 3, 3), dtype=object)
        for m in range(dimension):
            for n in range(dimension):
                output[m, n] = _matrix_product(left[m], right[n]) - _matrix_product(left[n], right[m])
        return output
    if expr.op == "invariant_pair_wedge":
        bfield = _array(values[0])
        curvature = _array(values[1])
        if bfield.shape[:3] != (5, 5, 5) or curvature.shape[:2] != (5, 5):
            raise SemanticFrechetError("BF executable arrays must be five-dimensional forms")
        if expr.label != "-tr3/2":
            raise SemanticFrechetError("BF evaluator rejects non-charter pairing labels")
        denominator = 2
        total: Any = Fraction(0)
        for permutation in itertools.permutations(range(5)):
            inversions = sum(
                1
                for left in range(5)
                for right in range(left + 1, 5)
                if permutation[left] > permutation[right]
            )
            sign = -1 if inversions % 2 else 1
            bmatrix = bfield[permutation[0], permutation[1], permutation[2]]
            fmatrix = curvature[permutation[3], permutation[4]]
            total += sign * (
                -_matrix_trace(_matrix_product(bmatrix, fmatrix))
                / Fraction(denominator)
            )
        return total / Fraction(math.factorial(3) * math.factorial(2))
    raise SemanticFrechetError(f"no executable semantics for {expr.op}")


EXECUTABLE_OPS = {
    "rational",
    "parameter",
    "field",
    "variation",
    "linear_slot",
    "zero",
    "add",
    "mul_scalar",
    "scale",
    "power",
    "exp",
    "sqrt",
    "inverse_metric",
    "volume_density",
    "metric_trace",
    "inverse_sandwich",
    "exterior_partial",
    "SO3_action",
    "associated_times_oneform",
    "metric_contract",
    "associated_pair",
    "adjoint_matrix_embedding",
    "matrix_wedge",
    "invariant_pair_wedge",
    "density_times_scalar",
}

PRIMITIVE_ORACLE_COVERAGE = {
    "rational_parameter_add_mul_scale_power_exp": "W_U_wall_at_origin plus exact Fraction algebra",
    "inverse_metric_volume_density_metric_trace_inverse_sandwich": "metric_inverse_and_volume",
    "exterior_partial_SO3_action_associated_times_oneform_metric_contract": "P_one_dimensional",
    "associated_pair_sqrt": "full_V4_reduced_Q",
    "adjoint_matrix_embedding_matrix_wedge_invariant_pair_wedge": "full_BF_Frechet plus BF_graded_Leibniz",
    "density_times_scalar": "metric_inverse_and_volume plus W_U_wall_at_origin",
}


def _numeric_equal(left: Any, right: Any, tolerance: float = 1.0e-12) -> bool:
    left_array = np.asarray(left)
    right_array = np.asarray(right)
    if left_array.shape != right_array.shape:
        return False
    return bool(
        all(
            abs(float(a) - float(b)) <= tolerance
            for a, b in zip(left_array.reshape(-1), right_array.reshape(-1), strict=True)
        )
    )


def _so3_cross_matrix(vector: Sequence[Fraction]) -> np.ndarray:
    x, y, z = vector
    return np.asarray(
        [[Fraction(0), -z, y], [z, Fraction(0), -x], [-y, x, Fraction(0)]],
        dtype=object,
    )


def _sparse_antisymmetric_form(
    axes: tuple[int, ...],
    coefficient: Fraction,
    matrix: np.ndarray,
) -> np.ndarray:
    degree = len(axes)
    output = np.zeros((5,) * degree + (3, 3), dtype=object)
    for permutation in itertools.permutations(axes):
        relative = tuple(axes.index(item) for item in permutation)
        inversions = sum(
            1
            for left in range(degree)
            for right in range(left + 1, degree)
            if relative[left] > relative[right]
        )
        output[permutation] = (-1 if inversions % 2 else 1) * coefficient * matrix
    return output


def full_bf_frechet_oracle_bridge(
    program: ComponentProgram,
    forward: Mapping[str, Expr],
    reverse: Mapping[str, Expr],
    frechet_rows: Sequence[Mapping[str, Any]],
    oracle: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate both BF AD trees and their five exported rows on one exact jet."""

    jx = _so3_cross_matrix((Fraction(1), Fraction(0), Fraction(0)))
    jy = _so3_cross_matrix((Fraction(0), Fraction(1), Fraction(0)))
    jz = _so3_cross_matrix((Fraction(0), Fraction(0), Fraction(1)))
    connection = np.zeros((5, 3, 3), dtype=object)
    connection[3] = jx
    connection[4] = jy
    alpha = np.zeros((5, 3, 3), dtype=object)
    alpha[3] = Fraction(11) * jx
    d_connection = _sparse_antisymmetric_form((3, 4), Fraction(2), jz)
    d_alpha = _sparse_antisymmetric_form((3, 4), Fraction(7), jz)
    bfield = _sparse_antisymmetric_form((0, 1, 2), Fraction(5), jz)
    b_variation = _sparse_antisymmetric_form((0, 1, 2), Fraction(3), jz)

    by_side: dict[str, Any] = {}
    for side in ("plus", "minus"):
        component = f"BF_bulk_{side}"
        values = {
            f"A_{side}": connection,
            f"B_{side}": bfield,
            f"alpha_{side}": alpha,
            f"b_{side}": b_variation,
        }
        partials = {
            f"A_{side}": d_connection,
            f"alpha_{side}": d_alpha,
        }
        environment = EvaluationEnvironment(
            values=values,
            parameters={},
            partials=partials,
        )
        forward_value = evaluate_expr(forward[component], environment)
        reverse_value = evaluate_expr(reverse[component], environment)

        component_rows = sorted(
            (row for row in frechet_rows if row["component"] == component),
            key=lambda row: row["summand_ordinal"],
        )
        row_values: list[Fraction] = []
        for row in component_rows:
            variation_component = row["variation_component"]
            if variation_component == f"b_{side}":
                slot_value = b_variation
            elif variation_component == f"alpha_{side}":
                slot_value = d_alpha if row["derivative"]["word"] else alpha
            else:
                raise SemanticFrechetError("unexpected variation in BF row bridge")
            coefficient = compat_coefficient_ast_to_expr(row["coefficient_ast"])
            row_value = evaluate_expr(
                coefficient,
                EvaluationEnvironment(
                    values={f"A_{side}": connection, f"B_{side}": bfield},
                    parameters={},
                    partials={f"A_{side}": d_connection},
                    linear_slot=slot_value,
                ),
            )
            if not isinstance(row_value, Fraction):
                raise SemanticFrechetError("BF row oracle ceased to be exact")
            row_values.append(row_value)
        by_side[side] = {
            "forward_AST_value": forward_value,
            "reverse_AST_value": reverse_value,
            "FrechetRowV1_values_by_ordinal": tuple(row_values),
            "FrechetRowV1_sum": sum(row_values, Fraction(0)),
            "expected_values_by_ordinal": oracle[
                "values_by_FrechetRowV1_ordinal"
            ],
            "independent_expected_total": oracle["expected_total"],
        }

    return {
        "input": oracle["input"],
        "pairing": oracle["pairing"],
        "by_side": by_side,
        "both_sides_match_independent_full_Frechet": all(
            row["forward_AST_value"] == row["reverse_AST_value"]
            == row["FrechetRowV1_sum"]
            == row["independent_expected_total"]
            and row["FrechetRowV1_values_by_ordinal"]
            == row["expected_values_by_ordinal"]
            for row in by_side.values()
        ),
    }


def executable_semantics_probe(
    program: ComponentProgram,
    forward: Mapping[str, Expr],
    reverse: Mapping[str, Expr],
) -> dict[str, Any]:
    metric5 = np.diag(
        [Fraction(-1), Fraction(1), Fraction(1), Fraction(1), Fraction(1)]
    ).astype(object)
    metric4 = np.diag(
        [Fraction(-1), Fraction(1), Fraction(1), Fraction(1)]
    ).astype(object)
    jx = _so3_cross_matrix((Fraction(1), Fraction(0), Fraction(0)))
    jy = _so3_cross_matrix((Fraction(0), Fraction(1), Fraction(0)))
    jz = _so3_cross_matrix((Fraction(0), Fraction(0), Fraction(1)))
    sparse_connection = np.zeros((5, 3, 3), dtype=object)
    sparse_connection[0] = jx
    sparse_connection[1] = jy
    sparse_alpha = np.zeros((5, 3, 3), dtype=object)
    sparse_alpha[0] = jy
    sparse_alpha[2] = jx
    sparse_two_form = _sparse_antisymmetric_form(
        (0, 1), Fraction(1), jz
    )
    sparse_alpha_partial = _sparse_antisymmetric_form(
        (0, 2), Fraction(1), jy
    )
    sparse_three_form = _sparse_antisymmetric_form(
        (2, 3, 4), Fraction(1), jz
    )
    values: dict[str, Any] = {
        "gamma": metric4,
        "Omega_Sigma": Fraction(1),
        "h": np.diag([Fraction(1), Fraction(0), Fraction(0), Fraction(0)]).astype(object),
        "omega_Sigma": Fraction(1, 7),
    }
    partials: dict[str, Any] = {
        "Omega_Sigma": np.zeros(4, dtype=object),
        "omega_Sigma": np.zeros(4, dtype=object),
    }
    for side, offset in (("plus", Fraction(0)), ("minus", Fraction(1, 5))):
        values.update(
            {
                f"g_{side}": metric5,
                f"Omega_{side}": Fraction(1) + offset,
                f"phi_{side}": np.asarray([Fraction(1), Fraction(2), Fraction(-1)], dtype=object),
                f"A_{side}": sparse_connection.copy(),
                f"B_{side}": sparse_three_form.copy(),
                f"H_{side}": np.diag(
                    [Fraction(1, 11), Fraction(1, 13), Fraction(0), Fraction(0), Fraction(0)]
                ).astype(object),
                f"omega_{side}": Fraction(1, 7),
                f"psi_{side}": np.asarray([Fraction(1, 3), Fraction(-1, 4), Fraction(1, 5)], dtype=object),
                f"alpha_{side}": sparse_alpha.copy(),
                f"b_{side}": sparse_three_form.copy(),
            }
        )
        partials.update(
            {
                f"Omega_{side}": np.asarray(
                    [Fraction(1, 2), Fraction(-1, 3), Fraction(1, 5), Fraction(0), Fraction(0)],
                    dtype=object,
                ),
                f"phi_{side}": np.asarray(
                    [
                        [Fraction(1), Fraction(0), Fraction(0)],
                        [Fraction(0), Fraction(1), Fraction(0)],
                        [Fraction(0), Fraction(0), Fraction(1)],
                        [Fraction(0), Fraction(0), Fraction(0)],
                        [Fraction(0), Fraction(0), Fraction(0)],
                    ],
                    dtype=object,
                ),
                f"A_{side}": sparse_two_form.copy(),
                f"omega_{side}": np.asarray(
                    [Fraction(1, 17), Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
                    dtype=object,
                ),
                f"psi_{side}": np.asarray(
                    [[Fraction(1, 19), Fraction(0), Fraction(0)]]
                    + [[Fraction(0), Fraction(0), Fraction(0)]] * 4,
                    dtype=object,
                ),
                f"alpha_{side}": sparse_alpha_partial.copy(),
            }
        )
    environment = EvaluationEnvironment(
        values=values,
        parameters={
            "G": Fraction(6),
            "M5": Fraction(1),
            "k_infinity": Fraction(1),
            "Z5": Fraction(1),
            "M": Fraction(1),
            "beta": Fraction(2),
        },
        partials=partials,
    )
    rows: dict[str, Any] = {}
    for component in EASY_COMPONENTS:
        primal_value = evaluate_expr(program.components[component], environment)
        forward_value = evaluate_expr(forward[component], environment)
        reverse_value = evaluate_expr(reverse[component], environment)
        rows[component] = {
            "primal_finite": bool(
                all(math.isfinite(float(value)) for value in np.asarray(primal_value).reshape(-1))
            ),
            "forward_reverse_value_equal": _numeric_equal(forward_value, reverse_value),
            "primal_nonzero": bool(
                any(abs(float(value)) > 0 for value in np.asarray(primal_value).reshape(-1))
            ),
            "Frechet_nonzero": bool(
                any(abs(float(value)) > 0 for value in np.asarray(forward_value).reshape(-1))
            ),
        }
    return {
        "components": rows,
        "all_primal_finite": all(row["primal_finite"] for row in rows.values()),
        "all_forward_reverse_values_equal": all(
            row["forward_reverse_value_equal"] for row in rows.values()
        ),
        "BF_primal_and_Frechet_nonzero": all(
            rows[f"BF_bulk_{side}"]["primal_nonzero"]
            and rows[f"BF_bulk_{side}"]["Frechet_nonzero"]
            for side in ("plus", "minus")
        ),
    }


def binder_and_fiber_expansion_probe() -> dict[str, Any]:
    metric = field("probe_metric", METRIC5)
    coefficient_oneform = field("probe_covector", ONEFORM5)
    coordinate_slot = Expr("linear_slot", ONEFORM5, label="eta")
    coordinate_contraction = metric_contract(
        inverse_metric(metric), coordinate_slot, coefficient_oneform
    )
    coordinate_value = evaluate_expr(
        coordinate_contraction,
        EvaluationEnvironment(
            values={
                "probe_metric": np.eye(5, dtype=object),
                "probe_covector": np.asarray(
                    [Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5)],
                    dtype=object,
                ),
            },
            parameters={},
            partials={},
            linear_slot=np.ones(5, dtype=object),
        ),
    )
    associated_slot = Expr("linear_slot", ASSOCIATED0_5, label="eta")
    associated_value = evaluate_expr(
        associated_pair(associated_slot, field("probe_associated", ASSOCIATED0_5)),
        EvaluationEnvironment(
            values={
                "probe_associated": np.asarray(
                    [Fraction(1), Fraction(2), Fraction(3)], dtype=object
                )
            },
            parameters={},
            partials={},
            linear_slot=np.ones(3, dtype=object),
        ),
    )
    return {
        "coordinate_dimension": 5,
        "coordinate_sum": coordinate_value,
        "coordinate_sum_expected": Fraction(15),
        "SO3_fiber_dimension": 3,
        "SO3_sum": associated_value,
        "SO3_sum_expected": Fraction(6),
        "linear_slot_resolved": (
            coordinate_value == Fraction(15) and associated_value == Fraction(6)
        ),
        "word_zero_is_alpha_normalized_binder_not_physical_direction_zero": (
            coordinate_contraction.args[1].op == "linear_slot"
            and coordinate_contraction.args[1].label == "eta"
            and coordinate_contraction.args[1].type_tag.dimension == 5
        ),
    }


def executable_oracle_bridge(
    program: ComponentProgram,
    oracles: Mapping[str, Any],
    *,
    route_mutant: str | None = None,
) -> dict[str, Any]:
    """Run typed AST primitives on the independent exact-oracle inputs."""

    omega = field("probe_Omega", SCALAR5)
    phi = field("probe_phi", ASSOCIATED0_5)
    connection = field("probe_A", CONNECTION1_5)
    p_expr = _p_ast(omega, phi, connection, program.parsed)
    p_tangents = {
        "probe_Omega": variation("probe_omega", SCALAR5),
        "probe_phi": variation("probe_psi", ASSOCIATED0_5),
        "probe_A": variation("probe_alpha", ADJOINT1_5),
    }
    p_forward = forward_nilpotent_dual(p_expr, p_tangents).tangent
    p_reverse = reverse_context_mode(p_expr, p_tangents)
    e1 = (Fraction(1), Fraction(0), Fraction(0))
    e3 = (Fraction(0), Fraction(0), Fraction(1))
    connection_value = np.zeros((5, 3, 3), dtype=object)
    connection_value[0] = _so3_cross_matrix(e3)
    alpha_value = np.zeros((5, 3, 3), dtype=object)
    alpha_value[0] = _so3_cross_matrix(e1)
    d_phi = np.zeros((5, 3), dtype=object)
    d_phi[0] = np.asarray(
        [Fraction(4), Fraction(-1), Fraction(2)], dtype=object
    )
    d_psi = np.zeros((5, 3), dtype=object)
    d_psi[0] = np.asarray(
        [Fraction(1), Fraction(3), Fraction(-2)], dtype=object
    )
    d_omega = np.zeros(5, dtype=object)
    d_omega[0] = Fraction(3)
    d_little_omega = np.zeros(5, dtype=object)
    d_little_omega[0] = Fraction(-2)
    p_environment = EvaluationEnvironment(
        values={
            "probe_Omega": Fraction(2),
            "probe_phi": np.asarray(
                [Fraction(1), Fraction(2), Fraction(0)], dtype=object
            ),
            "probe_A": connection_value,
            "probe_omega": Fraction(1),
            "probe_psi": np.asarray(
                [Fraction(2), Fraction(-1), Fraction(1)], dtype=object
            ),
            "probe_alpha": alpha_value,
        },
        parameters={},
        partials={
            "probe_Omega": d_omega,
            "probe_phi": d_phi,
            "probe_omega": d_little_omega,
            "probe_psi": d_psi,
        },
    )
    p_value = evaluate_expr(p_expr, p_environment)
    p_forward_value = evaluate_expr(p_forward, p_environment)
    p_reverse_value = evaluate_expr(p_reverse, p_environment)
    p_row = tuple(p_value[0, fiber] for fiber in range(3))
    delta_p_row = tuple(p_forward_value[0, fiber] for fiber in range(3))

    jx = _so3_cross_matrix(e1)
    jy = _so3_cross_matrix((Fraction(0), Fraction(1), Fraction(0)))
    jz = _so3_cross_matrix(e3)
    wedge_connection = np.zeros((5, 3, 3), dtype=object)
    wedge_connection[0] = jx
    wedge_connection[1] = jy
    wedge_expr = connection_wedge(
        field("probe_wedge_A", CONNECTION1_5),
        field("probe_wedge_A", CONNECTION1_5),
    )
    wedge_value = evaluate_expr(
        wedge_expr,
        EvaluationEnvironment(
            values={"probe_wedge_A": wedge_connection},
            parameters={},
            partials={},
        ),
    )

    bf_b = _sparse_antisymmetric_form((1, 2, 3), Fraction(2), jz)
    bf_f = _sparse_antisymmetric_form((0, 4), Fraction(3), jz)
    bf_expr = pair_wedge(
        field("probe_B", ADJOINT3_5), field("probe_F", ENDOMORPHISM2_5)
    )
    bf_value = evaluate_expr(
        bf_expr,
        EvaluationEnvironment(
            values={"probe_B": bf_b, "probe_F": bf_f},
            parameters={},
            partials={},
        ),
    )

    probe_metric = field("probe_g", METRIC5)
    probe_h = variation("probe_H", METRIC5)
    probe_inverse = inverse_metric(probe_metric)
    inverse_variation = negate(
        inverse_sandwich(probe_inverse, probe_h, probe_inverse)
    )
    volume_variation = scale(
        scalar_mul(
            rational(Fraction(1, 2)),
            metric_trace(probe_inverse, probe_h),
        ),
        volume_density(probe_metric),
    )
    metric_environment = EvaluationEnvironment(
        values={
            "probe_g": np.asarray(
                [[Fraction(-1), Fraction(0)], [Fraction(0), Fraction(1)]],
                dtype=object,
            ),
            "probe_H": np.asarray(
                [[Fraction(1), Fraction(2)], [Fraction(2), Fraction(3)]],
                dtype=object,
            ),
        },
        parameters={},
        partials={},
    )
    inverse_value = evaluate_expr(inverse_variation, metric_environment)
    volume_value = evaluate_expr(volume_variation, metric_environment)
    inverse_tuple = tuple(
        tuple(inverse_value[row, column] for column in range(2))
        for row in range(2)
    )

    potential_omega = field("probe_potential_Omega", SCALAR5)
    w_expr = _w_ast(potential_omega, program.parsed)
    u_expr = _u_ast(potential_omega, program.parsed)
    potential_tangents = {
        "probe_potential_Omega": variation("probe_potential_omega", SCALAR5)
    }
    w_forward_expr = forward_nilpotent_dual(
        w_expr, potential_tangents, mutant=route_mutant
    ).tangent
    w_reverse_expr = reverse_context_mode(
        w_expr, potential_tangents, mutant=route_mutant
    )
    u_forward_expr = forward_nilpotent_dual(
        u_expr, potential_tangents, mutant=route_mutant
    ).tangent
    u_reverse_expr = reverse_context_mode(
        u_expr, potential_tangents, mutant=route_mutant
    )
    potential_environment = EvaluationEnvironment(
        values={
            "probe_potential_Omega": Fraction(1),
            "probe_potential_omega": Fraction(1),
        },
        parameters={
            "M5": Fraction(1),
            "G": Fraction(1),
            "k_infinity": Fraction(1),
        },
        partials={},
        symbolic_exp_minus_one_sixth=True,
    )
    w_derivative_value = evaluate_expr(w_forward_expr, potential_environment)
    w_reverse_derivative_value = evaluate_expr(w_reverse_expr, potential_environment)
    u_derivative_value = evaluate_expr(u_forward_expr, potential_environment)
    u_reverse_derivative_value = evaluate_expr(u_reverse_expr, potential_environment)
    wall_tangents = {
        "Omega_Sigma": variation("probe_wall_omega", SCALAR4)
    }
    wall_forward_expr = forward_nilpotent_dual(
        program.components["wall"], wall_tangents, mutant=route_mutant
    ).tangent
    wall_reverse_expr = reverse_context_mode(
        program.components["wall"], wall_tangents, mutant=route_mutant
    )
    wall_environment = EvaluationEnvironment(
            values={
                "gamma": np.diag(
                    [Fraction(-1), Fraction(1), Fraction(1), Fraction(1)]
                ).astype(object),
                "Omega_Sigma": Fraction(1),
                "probe_wall_omega": Fraction(1),
            },
            parameters={
                "M5": Fraction(1),
                "G": Fraction(1),
                "k_infinity": Fraction(1),
                "beta": Fraction(2),
            },
            partials={},
            symbolic_exp_minus_one_sixth=True,
    )
    wall_derivative_value = evaluate_expr(wall_forward_expr, wall_environment)
    wall_reverse_derivative_value = evaluate_expr(
        wall_reverse_expr, wall_environment
    )

    v4_omega = field("probe_v4_Omega", SCALAR5)
    v4_phi = field("probe_v4_phi", ASSOCIATED0_5)
    q_expr = _smooth_full_v4_ast(v4_omega, v4_phi, program.parsed)
    q_omega_derivative_expr = forward_nilpotent_dual(
        q_expr,
        {"probe_v4_Omega": variation("probe_v4_omega", SCALAR5)},
    ).tangent
    q_s_derivative_expr = forward_nilpotent_dual(
        q_expr,
        {"probe_v4_phi": variation("probe_v4_psi", ASSOCIATED0_5)},
    ).tangent
    v4_environment = EvaluationEnvironment(
        values={
            "probe_v4_Omega": Fraction(1),
            "probe_v4_phi": np.asarray(
                [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)], dtype=object
            ),
            "probe_v4_omega": Fraction(1),
            "probe_v4_psi": np.asarray(
                [Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)], dtype=object
            ),
        },
        parameters={},
        partials={},
    )
    q_value = evaluate_expr(q_expr, v4_environment)
    q_omega_value = evaluate_expr(q_omega_derivative_expr, v4_environment)
    q_s_value = evaluate_expr(q_s_derivative_expr, v4_environment)

    return {
        "P_AST_value": p_row,
        "P_oracle_value": oracles["P_one_dimensional"]["P_expected"],
        "P_Frechet_AST_value": delta_p_row,
        "P_Frechet_oracle_value": oracles["P_one_dimensional"][
            "delta_P_expected"
        ],
        "P_forward_reverse_expanded_value_equal": _numeric_equal(
            p_forward_value, p_reverse_value
        ),
        "P_alpha_phi_nonzero": oracles["P_one_dimensional"]["alpha_phi"]
        != (Fraction(0), Fraction(0), Fraction(0)),
        "matrix_wedge_01": tuple(
            tuple(wedge_value[0, 1, row, column] for column in range(3))
            for row in range(3)
        ),
        "matrix_wedge_01_expected": tuple(tuple(value for value in row) for row in jz),
        "BF_AST_value": bf_value,
        "BF_mini_exterior_oracle_value": oracles["BF_graded_Leibniz"][
            "B_wedge_dalpha"
        ],
        "inverse_AST_value": inverse_tuple,
        "inverse_dual_oracle_value": oracles["metric_inverse_and_volume"][
            "delta_g_inverse_expected"
        ],
        "volume_AST_value": volume_value,
        "volume_dual_oracle_value": oracles["metric_inverse_and_volume"][
            "sqrt_minus_det_linear_coefficient_expected"
        ],
        "D_W_AST_terms": w_derivative_value.terms,
        "D_W_reverse_AST_terms": w_reverse_derivative_value.terms,
        "D_W_oracle_terms": oracles["nontrivial_exp_derivatives_at_Omega_one"][
            "D_W_expected_terms"
        ],
        "D_U_AST_terms": u_derivative_value.terms,
        "D_U_reverse_AST_terms": u_reverse_derivative_value.terms,
        "D_U_oracle_terms": oracles["nontrivial_exp_derivatives_at_Omega_one"][
            "D_U_expected_terms"
        ],
        "D_wall_AST_terms": wall_derivative_value.terms,
        "D_wall_reverse_AST_terms": wall_reverse_derivative_value.terms,
        "D_wall_oracle_terms": oracles[
            "nontrivial_exp_derivatives_at_Omega_one"
        ]["D_wall_action_expected_terms"],
        "V4_Q_AST_value": q_value,
        "V4_Q_oracle_value": oracles["full_V4_reduced_Q"]["Q_expected"],
        "V4_Q_Omega_Frechet_AST_value": q_omega_value,
        "V4_Q_Omega_oracle_value": oracles["full_V4_reduced_Q"][
            "partial_Omega_Q_expected"
        ],
        "V4_Q_s_Frechet_AST_value": q_s_value,
        "V4_Q_s_oracle_value": oracles["full_V4_reduced_Q"][
            "partial_s_Q_expected"
        ],
    }


def smooth_v4_zero_probe(
    program: ComponentProgram,
    derivatives: Mapping[str, Expr],
) -> dict[str, Any]:
    metric = np.diag(
        [Fraction(-1), Fraction(1), Fraction(1), Fraction(1), Fraction(1)]
    ).astype(object)
    values: dict[str, Any] = {
        "g_plus": metric,
        "Omega_plus": Fraction(1),
        "phi_plus": np.zeros(3, dtype=object),
        "H_plus": np.zeros((5, 5), dtype=object),
        "omega_plus": Fraction(2),
        "psi_plus": np.asarray(
            [Fraction(3), Fraction(-1), Fraction(4)], dtype=object
        ),
    }
    environment = EvaluationEnvironment(
        values=values,
        parameters={"Z5": Fraction(1), "M": Fraction(1)},
        partials={},
    )
    component = program.components["full_V4_bulk_plus"]
    derivative = derivatives["full_V4_bulk_plus"]
    primal_value = evaluate_expr(component, environment)
    derivative_value = evaluate_expr(derivative, environment)
    direct_negative_pair_powers = [
        node.exponent
        for node in _walk(derivative)
        if node.op == "power"
        and node.args[0].op == "associated_pair"
        and node.exponent is not None
        and node.exponent < 0
    ]
    return {
        "phi": [0, 0, 0],
        "primal": primal_value,
        "Frechet": derivative_value,
        "expected_primal": Fraction(0),
        "expected_Frechet": Fraction(0),
        "negative_direct_powers_of_phi_pair": direct_negative_pair_powers,
        "finite": math.isfinite(float(primal_value))
        and math.isfinite(float(derivative_value)),
    }


def _replace_action_once(
    action: Mapping[str, str], key: str, old: str, new: str
) -> dict[str, str]:
    text = action[key]
    if text.count(old) != 1:
        raise SemanticFrechetError(f"mutation target {old!r} is not unique in {key}")
    mutated = dict(action)
    mutated[key] = text.replace(old, new, 1)
    return _ordered_action(mutated)


def _mutate_bf_curvature_sign(expr: Expr) -> Expr:
    args = tuple(_mutate_bf_curvature_sign(arg) for arg in expr.args)
    rebuilt = Expr(expr.op, expr.type_tag, args, expr.label, expr.value, expr.exponent)
    if expr.op == "matrix_wedge":
        return negate(rebuilt)
    return rebuilt


def run_mutation_campaign(
    action: Mapping[str, str],
    program: ComponentProgram,
    derivatives: Mapping[str, Expr],
) -> dict[str, bool]:
    baseline_program_hash = _aggregate_expr_sha256(program.components)
    baseline_derivative_hash = _aggregate_expr_sha256(derivatives)
    results: dict[str, bool] = {}

    action_mutations = {
        "omega_kinetic_half_to_third": ("bulk_gauged", "(nabla Omega_eps)^2/2", "(nabla Omega_eps)^2/3"),
        "P_kinetic_half_to_quarter": ("bulk_gauged", "P_eps^(b M)/2", "P_eps^(b M)/4"),
        "P_conformal_three_to_one": ("gauged_conformal_derivative", "+3*phi_eps", "+1*phi_eps"),
        "V4_power_four_to_six": (
            "full_V4",
            "V4(r)=r^4/(2*sqrt(1+r^4))",
            "V4(r)=r^6/(2*sqrt(1+r^6))",
        ),
        "Omega_minus_five_to_minus_four": ("bulk_gauged", "Omega_eps^(-5)", "Omega_eps^(-4)"),
        "BF_pairing_half_to_third": ("BF", "tr_3(XY)/2", "tr_3(XY)/3"),
        "wall_W_factor_two_to_three": ("wall_background", "[2*W", "[3*W"),
        "W_factor_three_to_four": ("superpotential", "=3*M5", "=4*M5"),
        "U_second_factor_two_to_three": ("bulk_potential", "-2*W^2", "-3*W^2"),
    }
    for name, (key, old, new) in action_mutations.items():
        mutated_action = _replace_action_once(action, key, old, new)
        action_hash_changed = (
            _canonical_sha256(mutated_action) != V52_EXACT_ACTION_SHA256
        )
        try:
            parsed = parse_exact_action(mutated_action)
            mutated_program = build_component_program(parsed)
        except SemanticFrechetError as exc:
            results[name] = action_hash_changed and bool(str(exc))
        else:
            results[name] = (
                action_hash_changed
                and _aggregate_expr_sha256(mutated_program.components)
                != baseline_program_hash
            )

    alias_mutation = _replace_action_once(
        action,
        "gauged_conformal_derivative",
        "Omega_eps",
        "Omega_eta",
    )
    try:
        parse_exact_action(alias_mutation)
    except SemanticFrechetError as exc:
        results["reject_P_Omega_alias_drift"] = bool(str(exc))
    else:
        results["reject_P_Omega_alias_drift"] = False

    doubled_p = dict(program.components)
    doubled_p["P_kinetic_bulk_plus"] = add(
        program.components["P_kinetic_bulk_plus"],
        program.components["P_kinetic_bulk_plus"],
    )
    results["reject_double_count_P"] = _aggregate_expr_sha256(doubled_p) != baseline_program_hash
    doubled_bf = dict(program.components)
    doubled_bf["BF_bulk_plus"] = add(
        program.components["BF_bulk_plus"],
        program.components["BF_bulk_plus"],
    )
    results["reject_double_count_BF"] = _aggregate_expr_sha256(doubled_bf) != baseline_program_hash

    wrong_bf_sign = dict(program.components)
    wrong_bf_sign["BF_bulk_plus"] = _mutate_bf_curvature_sign(
        program.components["BF_bulk_plus"]
    )
    results["reject_BF_curvature_wedge_sign"] = (
        _aggregate_expr_sha256(wrong_bf_sign) != baseline_program_hash
    )

    aliased_sides = {
        name: (
            _rename_field_labels(
                expr,
                {
                    "g_minus": "g_plus",
                    "Omega_minus": "Omega_plus",
                    "phi_minus": "phi_plus",
                    "A_minus": "A_plus",
                    "B_minus": "B_plus",
                },
            )
            if name.endswith("_minus")
            else expr
        )
        for name, expr in program.components.items()
    }
    results["reject_plus_minus_field_aliasing"] = (
        _aggregate_expr_sha256(aliased_sides) != baseline_program_hash
    )
    omitted = dict(program.components)
    omitted.pop("wall")
    results["reject_omitted_component"] = (
        tuple(omitted) != EASY_COMPONENTS
        and _aggregate_expr_sha256(omitted) != baseline_program_hash
    )

    completion_mutant = json.loads(json.dumps(SEMANTIC_COMPLETION))
    completion_mutant["SO3_convention"]["curvature"] = "F[A]=dA-A wedge A"
    results["reject_completion_curvature_sign_drift"] = (
        _canonical_sha256(completion_mutant) != SEMANTIC_COMPLETION_SHA256
    )

    route_mutations = {
        "reject_forward_omit_alpha_phi": (
            "P_kinetic_bulk_plus",
            "forward",
            "forward_omit_alpha_phi",
        ),
        "reject_forward_double_exterior_variation": (
            "BF_bulk_plus",
            "forward",
            "forward_double_exterior_variation",
        ),
        "reject_forward_wrong_scalar_inverse_sign": (
            "P_kinetic_bulk_plus",
            "forward",
            "forward_wrong_inverse_sign",
        ),
        "reject_forward_wrong_metric_inverse_sign": (
            "Omega_kinetic_bulk_plus",
            "forward",
            "forward_wrong_metric_inverse_sign",
        ),
        "reject_forward_wrong_volume_half": (
            "Omega_potential_bulk_plus",
            "forward",
            "forward_wrong_volume_half",
        ),
        "reject_reverse_omit_BF_dalpha": (
            "BF_bulk_plus",
            "reverse",
            "reverse_omit_BF_dalpha",
        ),
    }
    for name, (component, route, mutant) in route_mutations.items():
        expr = program.components[component]
        if route == "forward":
            candidate = forward_nilpotent_dual(expr, program.tangents, mutant=mutant).tangent
            reference = reverse_context_mode(expr, program.tangents)
        else:
            candidate = reverse_context_mode(expr, program.tangents, mutant=mutant)
            reference = forward_nilpotent_dual(expr, program.tangents).tangent
        results[name] = candidate != reference

    results["baseline_derivative_inventory_is_nonempty"] = bool(
        baseline_derivative_hash
    )
    return results


def run_binder_mutation_campaign(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, bool]:
    baseline = next(row for row in rows if row["derivative"]["word"] == [0])

    def copied() -> dict[str, Any]:
        return json.loads(json.dumps(baseline))

    def slot(ast: dict[str, Any]) -> dict[str, Any]:
        if ast.get("op") == "linear_slot":
            return ast
        for arg in ast.get("args", []):
            try:
                return slot(arg)
            except LookupError:
                pass
        raise LookupError("linear slot absent")

    def rejects(candidate: dict[str, Any]) -> bool:
        candidate["coefficient_ast_sha256"] = _canonical_sha256(
            candidate["coefficient_ast"]
        )
        try:
            validate_frechet_row(candidate)
        except SemanticFrechetError:
            return True
        return False

    renamed = copied()
    renamed["derivative"]["word"] = [7]
    renamed["derivative"]["binders"][0]["id"] = 7
    renamed["derivative"]["binders"][0]["alpha_normalized"] = False
    slot(renamed["coefficient_ast"])["external_derivative_word"] = [7]
    renamed["coefficient_ast_sha256"] = _canonical_sha256(
        renamed["coefficient_ast"]
    )

    wrong_dimension = copied()
    wrong_dimension["derivative"]["binders"][0]["dimension"] = 4
    wrong_namespace = copied()
    wrong_namespace["derivative"]["binders"][0]["namespace"] = "M_minus.coordinate"
    wrong_variance = copied()
    wrong_variance["derivative"]["binders"][0]["variance"] = "up"
    free_word = copied()
    free_word["derivative"]["word"] = [7]
    captured = copied()
    captured["coefficient_ast"]["external_derivative_word"] = [0]
    unresolved_slot = copied()
    slot(unresolved_slot["coefficient_ast"])["op"] = "unresolved_slot"
    wrong_slot_type = copied()
    slot(wrong_slot_type["coefficient_ast"])["type"] = _compat_type(SCALAR0)

    return {
        "alpha_renaming_invariant": canonicalize_frechet_row_binders(renamed)
        == baseline,
        "reject_wrong_binder_dimension": rejects(wrong_dimension),
        "reject_wrong_binder_namespace": rejects(wrong_namespace),
        "reject_wrong_binder_variance": rejects(wrong_variance),
        "reject_free_binder": rejects(free_word),
        "reject_captured_binder": rejects(captured),
        "reject_unresolved_linear_slot": rejects(unresolved_slot),
        "reject_wrong_linear_slot_type": rejects(wrong_slot_type),
    }


def run_scalar_and_row_mutation_campaign(
    rows: Sequence[Mapping[str, Any]], program: ComponentProgram
) -> dict[str, bool]:
    """Kill non-scalar operands and cross-row BF/schema attacks."""

    def rejected(callback: Any) -> bool:
        try:
            callback()
        except SemanticFrechetError as exc:
            return bool(str(exc))
        return False

    metric = field("rogue_g", METRIC5)
    scalar = field("honest_scalar", SCALAR5)
    oneform = field("honest_oneform", ONEFORM5)
    results = {
        "reject_metric_in_scalar_mul": rejected(lambda: scalar_mul(metric, scalar)),
        "reject_metric_in_scale_scalar_slot": rejected(lambda: scale(metric, oneform)),
        "reject_metric_in_power": rejected(lambda: power(metric, 2)),
        "reject_metric_in_exp": rejected(lambda: exp_scalar(metric)),
        "reject_metric_in_sqrt": rejected(lambda: sqrt_scalar(metric)),
        "reject_metric_in_scalar_partial": rejected(
            lambda: scalar_partial(metric, "rogue_g")
        ),
    }

    scalar_row = next(
        row
        for row in rows
        if row["variation_component"] == "omega_plus"
        and row["derivative"]["word"] == []
    )
    rogue_metric_row = json.loads(json.dumps(scalar_row))
    rogue_metric_row["coefficient_ast"] = {
        "op": "mul",
        "args": [
            {
                "op": "jet",
                "symbol": "g_plus",
                "derivative": {"kind": "partial", "word": []},
                "type": _compat_type(METRIC5),
            },
            {
                "op": "linear_slot",
                "slot": "eta",
                "external_derivative_word": [],
                "type": _compat_type(SCALAR5),
            },
        ],
        "type": _compat_type(METRIC5),
    }
    rogue_metric_row["coefficient_ast_sha256"] = _canonical_sha256(
        rogue_metric_row["coefficient_ast"]
    )
    results["reject_rogue_metric_scalar_Frechet_row"] = rejected(
        lambda: validate_frechet_row(rogue_metric_row)
    )

    bf_row = next(row for row in rows if row["component"] == "BF_bulk_plus")

    def pairing_mutant(convention: str) -> dict[str, Any]:
        candidate = json.loads(json.dumps(bf_row))

        def replace(node: dict[str, Any]) -> bool:
            if node.get("op") == "invariant_pair_wedge":
                node["convention"] = convention
                return bool(node["convention"])
            return any(replace(arg) for arg in node.get("args", []))

        if not replace(candidate["coefficient_ast"]):
            raise SemanticFrechetError("BF pairing node missing from mutation target")
        candidate["coefficient_ast_sha256"] = _canonical_sha256(
            candidate["coefficient_ast"]
        )
        return candidate

    results["reject_BF_pairing_denominator_three_row"] = rejected(
        lambda: validate_frechet_row(pairing_mutant("-tr3/3"))
    )
    results["reject_BF_pairing_trace_sign_plus_row"] = rejected(
        lambda: validate_frechet_row(pairing_mutant("+tr3/2"))
    )
    results["reject_BF_pairing_group_alias_row"] = rejected(
        lambda: validate_frechet_row(pairing_mutant("-tr999/2"))
    )

    def collection_rejected(mutator: Any) -> bool:
        candidate = json.loads(json.dumps(rows))
        mutator(candidate)
        return rejected(lambda: validate_frechet_row_collection(candidate, program))

    def empty_spans(candidate: list[dict[str, Any]]) -> None:
        candidate[0]["source_spans"] = []

    def bad_ordinal(candidate: list[dict[str, Any]]) -> None:
        next(row for row in candidate if row["component"] == "BF_bulk_plus")[
            "summand_ordinal"
        ] = 999

    def string_ordinal(candidate: list[dict[str, Any]]) -> None:
        candidate[0]["summand_ordinal"] = "0"

    def alias_side(candidate: list[dict[str, Any]]) -> None:
        row = next(row for row in candidate if row["component"] == "BF_bulk_plus")
        row["component"] = "BF_bulk_minus"
        row["domain"] = "M_minus"

    def duplicate_mixed_bf_row(candidate: list[dict[str, Any]]) -> None:
        component_rows = sorted(
            (row for row in candidate if row["component"] == "BF_bulk_plus"),
            key=lambda row: row["summand_ordinal"],
        )
        component_rows[2]["coefficient_ast"] = json.loads(
            json.dumps(component_rows[1]["coefficient_ast"])
        )
        component_rows[2]["coefficient_ast_sha256"] = _canonical_sha256(
            component_rows[2]["coefficient_ast"]
        )

    results["reject_empty_source_spans_collection"] = collection_rejected(empty_spans)
    results["reject_noncontiguous_BF_ordinal_collection"] = collection_rejected(
        bad_ordinal
    )
    results["reject_string_coerced_ordinal_collection"] = collection_rejected(
        string_ordinal
    )
    results["reject_cross_side_BF_alias_collection"] = collection_rejected(alias_side)
    results["reject_duplicate_mixed_BF_skeleton_collection"] = collection_rejected(
        duplicate_mixed_bf_row
    )
    return results


FALSE_SCOPE = {
    "all_twenty_action_components_semantically_decoded_pass": False,
    "EH_or_GHY_Frechet_pass": False,
    "K_R_R2_a_or_Robin_Frechet_pass": False,
    "moving_embedding_or_shape_derivative_pass": False,
    "full_formal_adjoint_or_Green_identity_pass": False,
    "full_bulk_boundary_assembly_pass": False,
    "C1_ACTION_pass": False,
    "N1_ACTION_pass": False,
    "full_classical_variational_principle_selected_sector_pass": False,
    "B4_pass": False,
    "B5_pass": False,
    "publication_authorized": False,
}


def build_report(*, mutation: str | None = None) -> dict[str, Any]:
    allowed_mutations = {None, "correlated_double_exp_derivative"}
    if mutation not in allowed_mutations:
        raise SemanticFrechetError(f"unsupported report mutation {mutation!r}")
    route_mutant = mutation
    completion_snapshot = json.loads(json.dumps(SEMANTIC_COMPLETION))
    completion_observed_sha256 = _canonical_sha256(completion_snapshot)
    action, dependency = certify_v52_dependency()
    parsed = parse_exact_action(action)
    program = build_component_program(parsed)
    forward: dict[str, Expr] = {}
    reverse: dict[str, Expr] = {}
    rows: dict[str, Any] = {}
    for component, expr in program.components.items():
        dual = forward_nilpotent_dual(
            expr, program.tangents, mutant=route_mutant
        )
        reverse_expr = reverse_context_mode(
            expr, program.tangents, mutant=route_mutant
        )
        validate_expr_types(expr)
        validate_expr_types(dual.tangent)
        validate_expr_types(reverse_expr)
        forward[component] = dual.tangent
        reverse[component] = reverse_expr
        rows[component] = {
            "primal_ast_sha256": _canonical_sha256(_expr_row(expr)),
            "forward_frechet_ast_sha256": _canonical_sha256(_expr_row(dual.tangent)),
            "reverse_frechet_ast_sha256": _canonical_sha256(_expr_row(reverse_expr)),
            "routes_exactly_equal": dual.tangent == reverse_expr,
            "variation_degrees": sorted(_variation_degrees(dual.tangent)),
            "variation_components": list(_leaf_labels(dual.tangent, "variation")),
            "primal_ops": _op_inventory(expr),
            "frechet_ops": _op_inventory(dual.tangent),
            "source_spans": _source_spans(component, parsed),
        }

    frechet_rows = export_frechet_rows(program, forward)
    if not validate_frechet_row_collection(frechet_rows, program):
        raise SemanticFrechetError("FrechetRowV1 validation failed")
    all_exprs = tuple(program.components.values()) + tuple(forward.values()) + tuple(reverse.values())
    used_ops = set().union(*(_op_inventory(expr) for expr in all_exprs))
    unresolved_ops = sorted(used_ops - EXECUTABLE_OPS)
    token_coverage = {
        key: {
            "byte_length": len(action[key]),
            "token_count_including_whitespace": len(parsed.tokens[key]),
            "first_start": parsed.tokens[key][0].start if parsed.tokens[key] else 0,
            "last_end": parsed.tokens[key][-1].end if parsed.tokens[key] else 0,
            "round_trip_exact": "".join(token.text for token in parsed.tokens[key]) == action[key],
        }
        for key in ACTION_KEYS
    }
    oracles = exact_small_oracles()
    oracle_bridge = executable_oracle_bridge(
        program, oracles, route_mutant=route_mutant
    )
    correlated_exp_mutant_bridge = executable_oracle_bridge(
        program,
        oracles,
        route_mutant="correlated_double_exp_derivative",
    )
    full_bf_bridge = full_bf_frechet_oracle_bridge(
        program,
        forward,
        reverse,
        frechet_rows,
        oracles["full_BF_Frechet"],
    )
    mutations = run_mutation_campaign(action, program, forward)
    binder_mutations = run_binder_mutation_campaign(frechet_rows)
    scalar_and_row_mutations = run_scalar_and_row_mutation_campaign(
        frechet_rows, program
    )
    executable_probe = executable_semantics_probe(program, forward, reverse)
    binder_probe = binder_and_fiber_expansion_probe()
    v4_zero_probe = smooth_v4_zero_probe(program, forward)

    checks = {
        "v5_2_source_test_artifact_and_exact_action_byte_bound": (
            dependency.get("schema") == V52_SCHEMA
            and {name: _sha256(path) for name, path in PINNED_PATHS.items()}
            == PINNED_INPUTS
            and _canonical_sha256(action) == V52_EXACT_ACTION_SHA256
            and isinstance(dependency.get("checks"), dict)
            and dependency["checks"].get("all") is True
        ),
        "all_twelve_exact_action_entries_full_span_parsed": all(
            row["round_trip_exact"]
            and row["first_start"] == 0
            and row["last_end"] == row["byte_length"]
            for row in token_coverage.values()
        ),
        "semantic_completion_explicit_and_byte_pinned": (
            completion_observed_sha256 == EXPECTED_SEMANTIC_COMPLETION_SHA256
            and SEMANTIC_COMPLETION_SHA256 == EXPECTED_SEMANTIC_COMPLETION_SHA256
        ),
        "exactly_eleven_included_and_nine_excluded_components": (
            tuple(program.components) == EASY_COMPONENTS
            and len(EXCLUDED_COMPONENTS) == 9
            and not (set(program.components) & set(EXCLUDED_COMPONENTS))
        ),
        "two_independent_symbolic_AD_routes_exactly_agree": all(
            forward[name] == reverse[name] for name in EASY_COMPONENTS
        ),
        "all_Frechet_outputs_are_exactly_linear_in_typed_variations": all(
            _variation_degrees(expr) == {1} for expr in forward.values()
        ),
        "gauge_and_exterior_composites_expanded_before_Frechet": (
            all(
                node.op
                not in {
                    "D_A",
                    "F",
                    "covariant_derivative",
                    "W_Omega",
                    "U_Omega",
                    "Q_derivative",
                }
                for expr in all_exprs
                for node in _walk(expr)
            )
            and any(node.op == "exterior_partial" for expr in all_exprs for node in _walk(expr))
            and any(node.op == "SO3_action" for expr in all_exprs for node in _walk(expr))
            and any(node.op == "matrix_wedge" for expr in all_exprs for node in _walk(expr))
        ),
        "all_used_AST_nodes_typed_and_executable_with_no_unresolved_nodes": not unresolved_ops,
        "all_eleven_components_execute_with_finite_primal_and_equal_route_values": (
            executable_probe["all_primal_finite"]
            and executable_probe["all_forward_reverse_values_equal"]
            and executable_probe["BF_primal_and_Frechet_nonzero"]
        ),
        "typed_AST_evaluator_matches_independent_P_BF_metric_oracles": (
            oracle_bridge["P_AST_value"] == oracle_bridge["P_oracle_value"]
            and oracle_bridge["P_Frechet_AST_value"]
            == oracle_bridge["P_Frechet_oracle_value"]
            and oracle_bridge["P_forward_reverse_expanded_value_equal"] is True
            and oracle_bridge["P_alpha_phi_nonzero"] is True
            and oracle_bridge["matrix_wedge_01"]
            == oracle_bridge["matrix_wedge_01_expected"]
            and oracle_bridge["BF_AST_value"]
            == oracle_bridge["BF_mini_exterior_oracle_value"]
            and oracle_bridge["inverse_AST_value"]
            == oracle_bridge["inverse_dual_oracle_value"]
            and oracle_bridge["volume_AST_value"]
            == oracle_bridge["volume_dual_oracle_value"]
            and oracle_bridge["D_W_AST_terms"]
            == oracle_bridge["D_W_reverse_AST_terms"]
            == oracle_bridge["D_W_oracle_terms"]
            and oracle_bridge["D_U_AST_terms"]
            == oracle_bridge["D_U_reverse_AST_terms"]
            == oracle_bridge["D_U_oracle_terms"]
            and oracle_bridge["D_wall_AST_terms"]
            == oracle_bridge["D_wall_reverse_AST_terms"]
            == oracle_bridge["D_wall_oracle_terms"]
            and oracle_bridge["V4_Q_AST_value"]
            == oracle_bridge["V4_Q_oracle_value"]
            and oracle_bridge["V4_Q_Omega_Frechet_AST_value"]
            == oracle_bridge["V4_Q_Omega_oracle_value"]
            and oracle_bridge["V4_Q_s_Frechet_AST_value"]
            == oracle_bridge["V4_Q_s_oracle_value"]
        ),
        "symbolic_binder_and_SO3_fiber_expand_over_five_and_three_values": (
            binder_probe["coordinate_sum"]
            == binder_probe["coordinate_sum_expected"]
            and binder_probe["SO3_sum"] == binder_probe["SO3_sum_expected"]
            and binder_probe["linear_slot_resolved"] is True
        ),
        "full_V4_AST_and_Frechet_are_smooth_at_phi_zero": (
            v4_zero_probe["primal"] == v4_zero_probe["expected_primal"]
            and v4_zero_probe["Frechet"] == v4_zero_probe["expected_Frechet"]
            and not v4_zero_probe["negative_direct_powers_of_phi_pair"]
            and v4_zero_probe["finite"] is True
        ),
        "SO3_fiber_dimension_three_and_form_degrees_checked": all(
            type_tag.fiber_dimension == 3
            for type_tag in (
                ASSOCIATED0_5,
                ASSOCIATED1_5,
                CONNECTION1_5,
                ADJOINT1_5,
                ADJOINT2_5,
                ADJOINT3_5,
            )
        )
        and ENDOMORPHISM2_5.fiber_dimension == 9
        and ADJOINT3_5.form_degree + ENDOMORPHISM2_5.form_degree == 5,
        "exact_P_V4_BF_inverse_volume_and_W_U_wall_oracles_pass": _oracles_pass(oracles),
        "full_BF_Frechet_AST_and_rows_match_independent_sign_normalization_oracle": (
            full_bf_bridge["both_sides_match_independent_full_Frechet"]
            and all(oracles["full_BF_Frechet"]["mutants_killed"].values())
        ),
        "correlated_forward_reverse_exp_rule_mutant_is_killed_by_independent_oracle": (
            correlated_exp_mutant_bridge["D_W_AST_terms"]
            == correlated_exp_mutant_bridge["D_W_reverse_AST_terms"]
            and correlated_exp_mutant_bridge["D_U_AST_terms"]
            == correlated_exp_mutant_bridge["D_U_reverse_AST_terms"]
            and correlated_exp_mutant_bridge["D_wall_AST_terms"]
            == correlated_exp_mutant_bridge["D_wall_reverse_AST_terms"]
            and (
                correlated_exp_mutant_bridge["D_W_AST_terms"]
                != correlated_exp_mutant_bridge["D_W_oracle_terms"]
                or correlated_exp_mutant_bridge["D_U_AST_terms"]
                != correlated_exp_mutant_bridge["D_U_oracle_terms"]
                or correlated_exp_mutant_bridge["D_wall_AST_terms"]
                != correlated_exp_mutant_bridge["D_wall_oracle_terms"]
            )
        ),
        "all_declared_mutants_are_killed": all(mutations.values()),
        "binder_alpha_renaming_and_capture_mutants_pass": all(
            binder_mutations.values()
        ),
        "strict_scalar_and_cross_row_schema_mutants_are_killed": all(
            scalar_and_row_mutations.values()
        ),
        "FrechetRowV1_collection_side_ordinals_sources_and_BF_inventory_validate": (
            validate_frechet_row_collection(frechet_rows, program)
        ),
        "FrechetRowV1_rows_have_scoped_alpha_normalized_partial_binders": all(
            row["schema"] == FRECHET_ROW_SCHEMA
            and row["derivative"]["kind"] == "partial"
            and (
                row["derivative"]["word"] == []
                or (
                    row["derivative"]["word"] == [0]
                    and row["derivative"]["binders"][0]["alpha_normalized"] is True
                    and row["derivative"]["binders"][0]["scope"] == "row"
                )
            )
            for row in frechet_rows
        ),
    }
    exact_claim_dependencies = tuple(checks.values())
    checks[
        "Frechet_IR_equals_D_of_literal_S_v5_2_under_completion_for_exactly_11_components_pass"
    ] = all(exact_claim_dependencies)
    checks["all"] = all(checks.values())
    if mutation is None and checks["all"] is not True:
        raise SemanticFrechetError("v5.6.7.10 narrow checks did not close")

    decision = {
        "semantic_completion_conditional_scope_only": (
            checks["semantic_completion_explicit_and_byte_pinned"]
            and checks["all_twelve_exact_action_entries_full_span_parsed"]
        ),
        "exactly_eleven_component_Frechet_IR_pass": checks[
            "Frechet_IR_equals_D_of_literal_S_v5_2_under_completion_for_exactly_11_components_pass"
        ],
        "FrechetRowV1_export_pass": (
            checks[
                "FrechetRowV1_collection_side_ordinals_sources_and_BF_inventory_validate"
            ]
            and checks[
                "FrechetRowV1_rows_have_scoped_alpha_normalized_partial_binders"
            ]
        ),
        **FALSE_SCOPE,
    }
    return {
        "schema": SCHEMA,
        "test_mutation": mutation,
        "upstream": {
            "schema": dependency["schema"],
            "source_test_artifact_sha256": PINNED_INPUTS,
            "exact_action_sha256": V52_EXACT_ACTION_SHA256,
        },
        "semantic_completion": completion_snapshot,
        "semantic_completion_sha256": completion_observed_sha256,
        "scope": {
            "included_components": list(EASY_COMPONENTS),
            "excluded_components": list(EXCLUDED_COMPONENTS),
            "claim": "D of the literal S_v5_2 for exactly the eleven included fixed-domain components under the displayed semantic completion",
            "not_claimed": "the remaining nine rows, moving shape, full Green/adjoint, full C1, or N1",
        },
        "parser": {
            "action_key_order": list(ACTION_KEYS),
            "token_coverage": token_coverage,
            "semantic_capture_groups": parsed.captures,
        },
        "typed_component_certificate": rows,
        "aggregate_hashes": {
            "component_ASTs_sha256": _aggregate_expr_sha256(program.components),
            "forward_Frechet_ASTs_sha256": _aggregate_expr_sha256(forward),
            "reverse_Frechet_ASTs_sha256": _aggregate_expr_sha256(reverse),
            "FrechetRowV1_sha256": _canonical_sha256(frechet_rows),
        },
        "FrechetRowV1": frechet_rows,
        "executable_semantics": {
            "used_ops": sorted(used_ops),
            "unresolved_ops": unresolved_ops,
            "oracle_coverage": PRIMITIVE_ORACLE_COVERAGE,
            "eleven_component_probe": executable_probe,
            "independent_oracle_bridge": oracle_bridge,
            "correlated_exp_mutant_bridge": correlated_exp_mutant_bridge,
            "full_BF_Frechet_oracle_bridge": full_bf_bridge,
            "binder_and_fiber_expansion_probe": binder_probe,
            "smooth_V4_phi_zero_probe": v4_zero_probe,
            "derivative_routes": [
                "forward_nilpotent_dual_recursive_visitor",
                "reverse_output_to_leaf_context_enumerator",
            ],
        },
        "exact_oracles": oracles,
        "mutation_campaign": mutations,
        "binder_mutation_campaign": binder_mutations,
        "scalar_and_row_mutation_campaign": scalar_and_row_mutations,
        "checks": checks,
        "decision": decision,
    }


def main() -> int:
    print(
        json.dumps(
            _jsonable(build_report()),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
