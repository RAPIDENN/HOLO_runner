#!/usr/bin/env python3
"""Exact typed Frechet gate for the two EH and two GHY v5.2 terms.

This unit is intentionally narrow.  It byte-binds the literal v5.2 action,
adds one explicit coordinate semantic completion for the gravity notation,
constructs the four density ASTs, and differentiates those ASTs by two
structurally distinct exact traversals:

* forward nilpotent-dual propagation, and
* reverse output-to-leaf context propagation.

The embedding is allowed to move in the *raw* GHY derivative.  In particular,
evaluation obeys ``delta g_I(Y)=H_I(Y)+xi^C g_{I+C}(Y)`` and the cofactor unit
normal is differentiated rather than frozen.  That does not by itself prove a
shape equation.  The fixed-embedding EH+GHY/Brown--York comparison is built
only after both derivatives exist and remains fail-closed because this unit
does not implement the Palatini boundary-current/Stokes reducer.  No target
Brown--York formula is admitted into the action constructor.

Their agreement is an internal consistency check on the declared denotational
primitives, not an independent coordinate evaluation of every primitive.  Two
finite exact rational witnesses additionally exercise the inverse, volume and
moving-evaluation fragments in their declared dimensions.  No floating point
arithmetic, generated artifact, or promotion claim occurs here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"

SCHEMA = (
    "holo.one-omega-topological-so3-eh-ghy-semantic-frechet-"
    "v5-6-7-11-gate.v1"
)
FRECHET_ROW_SCHEMA = "FrechetRowV1"

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
COMPONENTS = ("EH_bulk_plus", "GHY_plus", "EH_bulk_minus", "GHY_minus")


class GravityFrechetError(RuntimeError):
    """A byte pin, typed AST rule, or exact differential identity failed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise GravityFrechetError(f"cannot hash {path}: {exc}") from exc


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
        raise GravityFrechetError(f"cannot read JSON {path}: {exc}") from exc
    if type(value) is not dict:
        raise GravityFrechetError(f"JSON object required: {path}")
    return value


@dataclass(frozen=True, order=True)
class GeoType:
    name: str
    base_dimension: int
    variance: tuple[str, ...] = ()
    density_weight: int = 0
    symmetry: str = "none"


SCALAR0 = GeoType("parameter_scalar", 0)
OUTWARD_SIGN = GeoType("outward_orientation_sign", 0)
SCALAR5 = GeoType("bulk_scalar", 5)
SCALAR4 = GeoType("interface_scalar", 4)
SCALAR4_DENSITY2 = GeoType("interface_scalar_density_weight_2", 4, (), 2)
SCALAR4_DENSITY1 = GeoType("interface_scalar_density_weight_1", 4, (), 1)
SCALAR4_DENSITY_MINUS1 = GeoType("interface_scalar_density_weight_minus_1", 4, (), -1)
SCALAR4_DENSITY_MINUS2 = GeoType("interface_scalar_density_weight_minus_2", 4, (), -2)
METRIC5 = GeoType("bulk_metric", 5, ("down", "down"), 0, "symmetric")
INVERSE5 = GeoType("bulk_inverse_metric", 5, ("up", "up"), 0, "symmetric")
METRIC1JET5 = GeoType(
    "bulk_metric_first_jet", 5, ("down", "down", "down"), 0, "metric_pair_symmetric"
)
METRIC2JET5 = GeoType(
    "bulk_metric_second_jet",
    5,
    ("down", "down", "down", "down"),
    0,
    "metric_pair_and_holonomic_derivative_pair_symmetric",
)
GAMMA5 = GeoType("bulk_Levi_Civita_connection", 5, ("up", "down", "down"), 0, "lower_pair_symmetric")
DGAMMA5 = GeoType("bulk_connection_first_jet", 5, ("up", "down", "down", "down"))
RICCI5 = GeoType("bulk_Ricci", 5, ("down", "down"), 0, "symmetric")
DENSITY5 = GeoType("bulk_coordinate_density", 5, (), 1, "alternating")

MAP5 = GeoType("embedding_map", 4, ("ambient_up",))
MAP1 = GeoType("embedding_first_jet", 4, ("boundary_down", "ambient_up"))
MAP2 = GeoType(
    "embedding_second_jet",
    4,
    ("boundary_down", "boundary_down", "ambient_up"),
    0,
    "holonomic_boundary_pair_symmetric",
)
PULLED_METRIC5 = GeoType("ambient_metric_along_interface", 4, ("ambient_down", "ambient_down"), 0, "symmetric")
PULLED_INVERSE5 = GeoType("ambient_inverse_metric_along_interface", 4, ("ambient_up", "ambient_up"), 0, "symmetric")
PULLED_METRIC1 = GeoType(
    "ambient_metric_first_jet_along_interface",
    4,
    ("ambient_down", "ambient_down", "ambient_down"),
    0,
    "metric_pair_symmetric",
)
PULLED_GAMMA5 = GeoType(
    "ambient_Levi_Civita_connection_along_interface",
    4,
    ("ambient_up", "ambient_down", "ambient_down"),
    0,
    "lower_pair_symmetric",
)
METRIC4 = GeoType("induced_metric", 4, ("down", "down"), 0, "symmetric")
INVERSE4 = GeoType("induced_inverse_metric", 4, ("up", "up"), 0, "symmetric")
DENSITY4 = GeoType("interface_coordinate_density", 4, (), 1, "alternating")
COFACTOR5 = GeoType("embedding_cofactor_covector", 4, ("ambient_down",), 1)
NORMAL5 = GeoType("outward_unit_normal_covector", 4, ("ambient_down",))
ACCELERATION5 = GeoType(
    "embedding_acceleration",
    4,
    ("boundary_down", "boundary_down", "ambient_up"),
    0,
    "holonomic_boundary_pair_symmetric",
)

TYPE_TABLE = {
    item.name: item
    for item in (
        SCALAR0,
        OUTWARD_SIGN,
        SCALAR5,
        SCALAR4,
        SCALAR4_DENSITY2,
        SCALAR4_DENSITY1,
        SCALAR4_DENSITY_MINUS1,
        SCALAR4_DENSITY_MINUS2,
        METRIC5,
        INVERSE5,
        METRIC1JET5,
        METRIC2JET5,
        GAMMA5,
        DGAMMA5,
        RICCI5,
        DENSITY5,
        MAP5,
        MAP1,
        MAP2,
        PULLED_METRIC5,
        PULLED_INVERSE5,
        PULLED_METRIC1,
        PULLED_GAMMA5,
        METRIC4,
        INVERSE4,
        DENSITY4,
        COFACTOR5,
        NORMAL5,
        ACCELERATION5,
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
    derivative_word: tuple[str, ...] = ()


def _type_row(type_tag: GeoType) -> dict[str, Any]:
    return {
        "name": type_tag.name,
        "base_dimension": type_tag.base_dimension,
        "variance": list(type_tag.variance),
        "density_weight": type_tag.density_weight,
        "symmetry": type_tag.symmetry,
    }


def expr_row(expr: Expr) -> dict[str, Any]:
    row: dict[str, Any] = {"op": expr.op, "type": _type_row(expr.type_tag)}
    if expr.args:
        row["args"] = [expr_row(arg) for arg in expr.args]
    if expr.label:
        row["label"] = expr.label
    if expr.value is not None:
        row["value"] = [expr.value.numerator, expr.value.denominator]
    if expr.exponent is not None:
        row["exponent"] = [expr.exponent.numerator, expr.exponent.denominator]
    if expr.derivative_word:
        row["derivative_word"] = list(expr.derivative_word)
    return row


def _sort_key(expr: Expr) -> str:
    return json.dumps(expr_row(expr), sort_keys=True, separators=(",", ":"))


def _scalar_type(dimension: int, density_weight: int = 0) -> GeoType:
    fixed = {
        (0, 0): SCALAR0,
        (4, 0): SCALAR4,
        (5, 0): SCALAR5,
        (4, 2): SCALAR4_DENSITY2,
        (4, 1): SCALAR4_DENSITY1,
        (4, -1): SCALAR4_DENSITY_MINUS1,
        (4, -2): SCALAR4_DENSITY_MINUS2,
    }.get((dimension, density_weight))
    if fixed is not None:
        return fixed
    return GeoType(
        f"scalar_density_dimension_{dimension}_weight_{density_weight}",
        dimension,
        (),
        density_weight,
    )


def rational(value: int | Fraction, denominator: int = 1, *, dimension: int = 0) -> Expr:
    number = value if isinstance(value, Fraction) else Fraction(value, denominator)
    if dimension not in {0, 4, 5}:
        raise GravityFrechetError("unsupported scalar dimension")
    target = _scalar_type(dimension)
    return Expr("rational", target, value=number)


def parameter(name: str) -> Expr:
    type_tag = (
        OUTWARD_SIGN
        if name in {"s_out_plus", "s_out_minus"}
        else SCALAR0
    )
    return Expr("parameter", type_tag, label=name)


def field(name: str, type_tag: GeoType) -> Expr:
    return Expr("field", type_tag, label=name)


def variation(name: str, type_tag: GeoType, word: Sequence[str] = ()) -> Expr:
    return Expr("variation", type_tag, label=name, derivative_word=tuple(word))


def zero(type_tag: GeoType) -> Expr:
    return Expr("zero", type_tag)


def is_zero(expr: Expr) -> bool:
    return expr.op == "zero" or (expr.op == "rational" and expr.value == 0)


def _is_scalar(type_tag: GeoType) -> bool:
    return not type_tag.variance and type_tag not in {DENSITY5, DENSITY4}


def _scalar_result(types: Sequence[GeoType]) -> GeoType:
    if any(not _is_scalar(item) for item in types):
        raise GravityFrechetError("scalar product received a tensor or density")
    dimensions = {item.base_dimension for item in types if item.base_dimension}
    if len(dimensions) > 1:
        raise GravityFrechetError("scalar base dimensions disagree")
    return _scalar_type(
        next(iter(dimensions), 0),
        sum(item.density_weight for item in types),
    )


def add(*values: Expr) -> Expr:
    if not values:
        raise GravityFrechetError("empty addition")
    target = values[0].type_tag
    flat: list[Expr] = []
    for value in values:
        if value.type_tag != target:
            raise GravityFrechetError("addition type mismatch")
        if is_zero(value):
            continue
        flat.extend(value.args if value.op == "add" else (value,))
    if not flat:
        return zero(target)
    flat.sort(key=_sort_key)
    return flat[0] if len(flat) == 1 else Expr("add", target, tuple(flat))


def mul_scalar(*values: Expr) -> Expr:
    if not values:
        return rational(1)
    for index, value in enumerate(values):
        if value.op == "add":
            return add(
                *(mul_scalar(*values[:index], term, *values[index + 1 :]) for term in value.args)
            )
    target = _scalar_result([value.type_tag for value in values])
    coefficient = Fraction(1)
    flat: list[Expr] = []

    def collect(value: Expr) -> None:
        nonlocal coefficient
        if value.op == "rational":
            assert value.value is not None
            coefficient *= value.value
        elif value.op == "mul_scalar":
            for child in value.args:
                collect(child)
        else:
            flat.append(value)

    for value in values:
        collect(value)
    if coefficient == 0:
        return zero(target)
    if coefficient != 1 or not flat:
        flat.append(rational(coefficient))
    flat.sort(key=_sort_key)
    if len(flat) == 1 and flat[0].type_tag == target:
        return flat[0]
    return Expr("mul_scalar", target, tuple(flat))


def scale(scalar: Expr, value: Expr) -> Expr:
    _scalar_result((scalar.type_tag, GeoType("temporary", value.type_tag.base_dimension)))
    if scalar.type_tag.density_weight != 0:
        raise GravityFrechetError("scale cannot silently change tensor density weight")
    if scalar.op == "add":
        return add(*(scale(term, value) for term in scalar.args))
    if value.op == "add":
        return add(*(scale(scalar, term) for term in value.args))
    if is_zero(scalar) or is_zero(value):
        return zero(value.type_tag)
    if _is_scalar(value.type_tag):
        return mul_scalar(scalar, value)
    if scalar.op == "rational" and scalar.value == 1:
        return value
    if value.op == "scale":
        return scale(mul_scalar(scalar, value.args[0]), value.args[1])
    return Expr("scale", value.type_tag, (scalar, value))


def negate(value: Expr) -> Expr:
    return scale(rational(-1), value)


def power(value: Expr, exponent: int | Fraction) -> Expr:
    if not _is_scalar(value.type_tag):
        raise GravityFrechetError("power requires a scalar")
    exponent = Fraction(exponent)
    if exponent == 0:
        return rational(1)
    if exponent == 1:
        return value
    target_weight = value.type_tag.density_weight * exponent
    if target_weight.denominator != 1:
        raise GravityFrechetError("power would produce a fractional density weight")
    return Expr(
        "power",
        _scalar_type(value.type_tag.base_dimension, target_weight.numerator),
        (value,),
        exponent=exponent,
    )


def sqrt_scalar(value: Expr) -> Expr:
    if not _is_scalar(value.type_tag):
        raise GravityFrechetError("sqrt requires a scalar")
    if value.type_tag.density_weight % 2:
        raise GravityFrechetError("sqrt requires an even density weight")
    return Expr(
        "sqrt",
        _scalar_type(value.type_tag.base_dimension, value.type_tag.density_weight // 2),
        (value,),
    )


def inverse_metric(metric: Expr) -> Expr:
    target = {
        METRIC5: INVERSE5,
        PULLED_METRIC5: PULLED_INVERSE5,
        METRIC4: INVERSE4,
    }.get(metric.type_tag)
    if target is None:
        raise GravityFrechetError("inverse_metric requires a registered metric")
    return Expr("inverse_metric", target, (metric,))


def volume_density(metric: Expr) -> Expr:
    target = {METRIC5: DENSITY5, METRIC4: DENSITY4}.get(metric.type_tag)
    if target is None:
        raise GravityFrechetError("volume_density requires a bulk or induced metric")
    return Expr("volume_density", target, (metric,))


OP_SIGNATURES: dict[str, tuple[tuple[GeoType, ...], GeoType]] = {
    "inverse_sandwich_5": ((INVERSE5, METRIC5, INVERSE5), INVERSE5),
    "inverse_sandwich_5_at_Sigma": ((PULLED_INVERSE5, PULLED_METRIC5, PULLED_INVERSE5), PULLED_INVERSE5),
    "inverse_sandwich_4": ((INVERSE4, METRIC4, INVERSE4), INVERSE4),
    "metric_trace_5": ((INVERSE5, METRIC5), SCALAR5),
    "metric_trace_5_at_Sigma": ((PULLED_INVERSE5, PULLED_METRIC5), SCALAR4),
    "metric_trace_4": ((INVERSE4, METRIC4), SCALAR4),
    "Christoffel_5": ((INVERSE5, METRIC1JET5), GAMMA5),
    "Christoffel_5_at_Sigma": ((PULLED_INVERSE5, PULLED_METRIC1), PULLED_GAMMA5),
    "partial_Christoffel_inverse_leg": ((INVERSE5, INVERSE5, METRIC1JET5, METRIC1JET5), DGAMMA5),
    "partial_Christoffel_second_jet": ((INVERSE5, METRIC2JET5), DGAMMA5),
    "Ricci_trace_difference": ((DGAMMA5,), RICCI5),
    "Ricci_trace_sum_mutant": ((DGAMMA5,), RICCI5),
    "Ricci_Gamma_Gamma": ((GAMMA5, GAMMA5), RICCI5),
    "trace_Ricci": ((INVERSE5, RICCI5), SCALAR5),
    "density_times_scalar_5": ((DENSITY5, SCALAR5), DENSITY5),
    "evaluate_metric_variation_0": ((METRIC5, MAP5), PULLED_METRIC5),
    "transport_metric_jet_0": ((METRIC1JET5, MAP5, MAP5), PULLED_METRIC5),
    "evaluate_metric_variation_1": ((METRIC1JET5, MAP5), PULLED_METRIC1),
    "transport_metric_jet_1": ((METRIC2JET5, MAP5, MAP5), PULLED_METRIC1),
    "pullback_metric": ((PULLED_METRIC5, MAP1, MAP1), METRIC4),
    "embedding_cofactor": ((MAP1, MAP1, MAP1, MAP1), COFACTOR5),
    "cofactor_norm_squared": ((PULLED_INVERSE5, COFACTOR5, COFACTOR5), SCALAR4_DENSITY2),
    "normal_from_cofactor": ((SCALAR4_DENSITY_MINUS1, COFACTOR5), NORMAL5),
    "normal_from_cofactor_constant_sign": ((OUTWARD_SIGN, COFACTOR5), NORMAL5),
    "connection_pullback_acceleration": ((PULLED_GAMMA5, MAP1, MAP1), ACCELERATION5),
    "Theta_contraction": ((INVERSE4, NORMAL5, ACCELERATION5), SCALAR4),
    "density_times_scalar_4": ((DENSITY4, SCALAR4), DENSITY4),
}


def multilinear(label: str, *args: Expr) -> Expr:
    try:
        expected, target = OP_SIGNATURES[label]
    except KeyError as exc:
        raise GravityFrechetError(f"unregistered multilinear operator {label}") from exc
    if tuple(arg.type_tag for arg in args) != expected:
        observed = tuple(arg.type_tag.name for arg in args)
        wanted = tuple(item.name for item in expected)
        raise GravityFrechetError(f"{label} type mismatch: {observed} != {wanted}")
    for index, arg in enumerate(args):
        if arg.op == "add":
            return add(
                *(multilinear(label, *(args[:index] + (term,) + args[index + 1 :])) for term in arg.args)
            )
        if is_zero(arg):
            return zero(target)
    return Expr("multilinear", target, tuple(args), label=label)


def covariant_acceleration(second_jet: Expr, connection_term: Expr) -> Expr:
    """Form Q=D2Y+Gamma(Y)(DY,DY) without identifying D2Y with Q's type."""

    if (second_jet.type_tag, connection_term.type_tag) != (MAP2, ACCELERATION5):
        raise GravityFrechetError("covariant_acceleration type mismatch")
    if is_zero(second_jet) and is_zero(connection_term):
        return zero(ACCELERATION5)
    return Expr(
        "covariant_acceleration",
        ACCELERATION5,
        (second_jet, connection_term),
        label="D2Y_plus_connection_pullback",
    )


def evaluate_jet(base: Expr, next_jet: Expr, embedding: Expr, order: int, *, moving: bool = True) -> Expr:
    specs = {
        0: (METRIC5, METRIC1JET5, PULLED_METRIC5),
        1: (METRIC1JET5, METRIC2JET5, PULLED_METRIC1),
    }
    try:
        base_type, next_type, target = specs[order]
    except KeyError as exc:
        raise GravityFrechetError("only metric jets 0 and 1 are evaluated here") from exc
    if (base.type_tag, next_jet.type_tag, embedding.type_tag) != (base_type, next_type, MAP5):
        raise GravityFrechetError("evaluate_jet type mismatch")
    label = f"metric_jet_{order}_at_moving_Y" if moving else f"metric_jet_{order}_at_frozen_Y"
    return Expr("evaluate_jet", target, (base, next_jet, embedding), label=label)


OPERATOR_SEMANTICS = {
    "inverse_sandwich_5": "(g^{-1} H g^{-1})^{MN}=g^{MA} H_AB g^{BN}",
    "inverse_sandwich_5_at_Sigma": "same inverse sandwich after evaluation on Y",
    "inverse_sandwich_4": "(gamma^{-1} h gamma^{-1})^{mn}=gamma^{mp} h_pq gamma^{qn}",
    "metric_trace_5": "tr_g H=g^{MN} H_MN",
    "metric_trace_5_at_Sigma": "tr_{g(Y)} H(Y)=g^{AB}(Y) H_AB(Y) with ambient dimension five",
    "metric_trace_4": "tr_gamma h=gamma^{mn} h_mn",
    "Christoffel_5": "Gamma^R_MN=g^{RS}(g_SN,M+g_SM,N-g_MN,S)/2",
    "Christoffel_5_at_Sigma": "Y^*Gamma from Y^*g^{-1} and Y^*(partial g) using the same coordinate formula",
    "partial_Christoffel_inverse_leg": "-g^{RU} g_UV,C g^{VS}(g_SN,M+g_SM,N-g_MN,S)/2 with the displayed C derivative index retained",
    "partial_Christoffel_second_jet": "g^{RS}(g_SN,MC+g_SM,NC-g_MN,SC)/2 with ordered derivative pair (C,second-index)",
    "Ricci_trace_difference": "R_MN=(partial_R Gamma^R_MN)-(partial_N Gamma^R_MR)+Gamma^R_RS Gamma^S_MN-Gamma^R_NS Gamma^S_MR: this node is the first two terms with their minus sign",
    "Ricci_Gamma_Gamma": "Gamma^R_RS Gamma^S_MN-Gamma^R_NS Gamma^S_MR with ordered contractions",
    "trace_Ricci": "R=g^{MN} R_MN",
    "density_times_scalar_5": "coordinate top density multiplied by a bulk scalar",
    "evaluate_metric_variation_0": "H_AB(Y)",
    "transport_metric_jet_0": "xi^C partial_C g_AB(Y)",
    "evaluate_metric_variation_1": "partial_C H_AB(Y)",
    "transport_metric_jet_1": "xi^D partial_D partial_C g_AB(Y), retaining the ordered jet indices",
    "pullback_metric": "gamma_mn=g_AB(Y) Y_m^A Y_n^B",
    "embedding_cofactor": "nu_A=(1/4!)*epsilon_ABCDE*epsilon^mnpq*Y_m^B*Y_n^C*Y_p^D*Y_q^E",
    "cofactor_norm_squared": "g^{AB}(Y) nu_A nu_B",
    "normal_from_cofactor": "a scalar factor c times nu_A; the constructor pins c=s_out/sqrt(g^{BC}nu_Bnu_C)",
    "normal_from_cofactor_constant_sign": "mutant-only unnormalized map s_out*nu_A, retained so both AD routes can type-check and reject it",
    "connection_pullback_acceleration": "Gamma^R_AB(Y) Y_m^A Y_n^B",
    "covariant_acceleration": "Q_mn^R=partial_m partial_n Y^R+Gamma^R_AB(Y) partial_m Y^A partial_n Y^B",
    "Theta_contraction": "gamma^{mn} n_R Q_mn^R",
    "density_times_scalar_4": "coordinate interface top density multiplied by an interface scalar",
}


SEMANTIC_COMPLETION = {
    "version": "v5.6.7.11-eh-ghy-coordinate-completion-v2",
    "literal_scope": {
        "components": list(COMPONENTS),
        "EH": "(M5^3/2)*sqrt(-det g)*R on each fixed bulk domain",
        "GHY": "M5^3*sqrt(-det gamma)*Theta on each interface copy",
    },
    "coordinate_gravity": {
        "signature": "Lorentzian and sqrt(-det g) is the oriented coordinate density",
        "inverse": "g^{MA} g_AN=delta^M_N",
        "volume_variation": "delta sqrt(-g)=sqrt(-g)*g^{MN}H_MN/2",
        "Christoffel": OPERATOR_SEMANTICS["Christoffel_5"],
        "Riemann": "R^R_SMN=partial_M Gamma^R_NS-partial_N Gamma^R_MS+Gamma^R_MT Gamma^T_NS-Gamma^R_NT Gamma^T_MS",
        "Ricci": "R_SN=R^R_SRN",
        "ordered_metric_jets": "g_AB,C and g_AB,CD are holonomic jets; the typed word is retained through Frechet export and is not silently reordered",
    },
    "embedding_and_normal": {
        "domain_convention": "each collar is M_eps={r_eps>=0}",
        "cofactor": OPERATOR_SEMANTICS["embedding_cofactor"],
        "cofactor_density_weights": "nu_A has boundary density weight +1, its norm has +1, the inverse norm has -1, and n_A has weight 0",
        "non_null_precondition": "g^{AB}nu_A nu_B>0 for the timelike interface used here; otherwise the gate fails closed",
        "unit_normal": "n_A=s_out*nu_A/sqrt(g^{BC}nu_B nu_C)",
        "outward_selector": "s_out is the unique locally constant sign satisfying n^A partial_A r_eps<0; it is not hard-coded from the plus/minus name",
        "outward_selector_type": "s_out has the distinguished OUTWARD_SIGN semantic type and is not an M5-like coupling scalar",
        "acceleration": "Q_mn^R=partial_m partial_n Y^R+Gamma^R_AB(Y) partial_m Y^A partial_n Y^B",
        "extrinsic_trace": "Theta=-gamma^{mn} n_R Q_mn^R",
    },
    "moving_evaluation": {
        "metric": "delta[g_AB(Y)]=H_AB(Y)+xi^C partial_C g_AB(Y)",
        "first_metric_jet": "delta[g_AB,C(Y)]=H_AB,C(Y)+xi^D g_AB,CD(Y)",
        "embedding_jets": "delta Y=xi, delta(partial_m Y)=partial_m xi, delta(partial_m partial_n Y)=partial_m partial_n xi",
        "normal": "the cofactor, inverse metric and norm are all differentiated; a frozen normal is forbidden",
    },
    "operators": OPERATOR_SEMANTICS,
    "differentiation": {
        "forward": "nilpotent dual epsilon^2=0 propagated locally through the action AST",
        "reverse": "enumerate each active field occurrence and lift its tangent independently through output-to-leaf contexts",
        "comparison": "canonical exact AST equality of two traversals, with no tolerance or sampling; this is not independent primitive denotation",
        "finite_local_denotation_bridge": (
            "two exact rational assignments with M5 and both outward signs nontrivial; "
            "all local inverse, volume, trace, moving-evaluation, embedding and pullback "
            "operands are evaluated as 5x5 ambient and 4x4 induced arrays and compared "
            "by component, summand ordinal, AST path and row route; finite witnesses do "
            "not establish a universal coordinate identity"
        ),
        "symbolic_whole_summand_replay": (
            "M5 and both outward signs remain exact polynomial indeterminates; a third "
            "local-rule visitor differentiates the primal AST independently, while direct "
            "producer and row decoders retain every outer factor and recursively nested "
            "operand and compare exact normal forms by component and summand ordinal"
        ),
        "FrechetRowV1_binders": "row derivative words are alpha-normalized integer ids; namespace and dimension come from the variation bundle plus ordered word, never from the integration domain; the unique linear_slot carries the same external_derivative_word",
        "internal_jet_binders": "background jet words use independently alpha-normalized node-scoped integer binders and cannot capture row binders",
    },
    "scope_limits": {
        "Palatini_boundary_current_reducer": False,
        "fixed_embedding_Brown_York_cancellation": False,
        "moving_shape_equation": False,
        "two_sided_Green_identity": False,
        "all_twenty_components": False,
        "C1": False,
        "N1": False,
        "S10_component_validator_interoperability": False,
    },
}

EXPECTED_SEMANTIC_COMPLETION_SHA256 = (
    "d933f3bd85d3495271877491016b50e739958ce73d2daf8083b42897a1dc84dc"
)
EXPECTED_PROGRAM_SHA256 = (
    "c1dcf794b0e18c0326791980ba7cbd65d413f0311bc311347d594bcee8881b75"
)
EXPECTED_DERIVATIVES_SHA256 = (
    "991e3a3d4fef746c10f17b39c8634d6bc10a820029d35a72b704fa3ef256fa07"
)
EXPECTED_FRECHET_ROWS_SHA256 = (
    "02db8501f63ef50451c094bdb1b3984e31f0b405fbe9dae637f0348d22742059"
)


def _semantic_completion_snapshot(mutation: str | None) -> dict[str, Any]:
    """Copy the completion so every build hashes the exact object it returns."""

    snapshot = copy.deepcopy(SEMANTIC_COMPLETION)
    if mutation == "semantic_completion_post_cache_tamper":
        snapshot["embedding_and_normal"]["extrinsic_trace"] = (
            "Theta=+gamma^{mn} n_R Q_mn^R"
        )
    return snapshot


@dataclass(frozen=True)
class ParsedCharter:
    action: Mapping[str, str]
    eh_denominator: int
    m5_power_bulk: int
    m5_power_ghy: int


def certify_v52_dependency() -> tuple[dict[str, Any], Mapping[str, str], Mapping[str, Any]]:
    observed = {name: _sha256(path) for name, path in PINNED_PATHS.items()}
    if observed != PINNED_INPUTS:
        raise GravityFrechetError(f"v5.2 byte-pin drift: {observed}")
    payload = _read_json(V52_ARTIFACT)
    if payload.get("schema") != V52_SCHEMA or payload.get("checks", {}).get("all") is not True:
        raise GravityFrechetError("v5.2 artifact is not the certified schema")
    charter = payload.get("exact_classical_charter")
    if type(charter) is not dict or type(charter.get("exact_action")) is not dict:
        raise GravityFrechetError("v5.2 exact action is absent")
    raw = charter["exact_action"]
    if set(raw) != set(ACTION_KEYS) or any(type(raw[key]) is not str for key in ACTION_KEYS):
        raise GravityFrechetError("v5.2 action key or string inventory drift")
    action = {key: raw[key] for key in ACTION_KEYS}
    action_hash = _canonical_sha256(action)
    if action_hash != V52_EXACT_ACTION_SHA256:
        raise GravityFrechetError("v5.2 exact-action canonical hash drift")
    green = payload.get("Green_form_certificate")
    if type(green) is not dict:
        raise GravityFrechetError("v5.2 Green-form diagnostic is absent")
    return (
        {
            "pass": True,
            "schema": payload["schema"],
            "files": {
                name: {"path": str(PINNED_PATHS[name]), "sha256": observed[name]}
                for name in sorted(observed)
            },
            "exact_action_sha256": action_hash,
        },
        action,
        green,
    )


def parse_charter(action: Mapping[str, str]) -> ParsedCharter:
    total = "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF"
    if action.get("total") != total:
        raise GravityFrechetError("literal total action drift")
    bulk = re.fullmatch(
        r"S_bulk_gauged=sum_eps int_Meps sqrt\(-g_eps\)\*\[M5\^(?P<m5>[0-9]+)\*R_eps/(?P<den>[0-9]+)-G\*\(nabla Omega_eps\)\^2/2-U\(Omega_eps\)-Z5\*delta_ab\*P_eps_M\^a\*P_eps\^\(b M\)/2-Z5\*M\^2\*Omega_eps\^\(-5\)\*V4\(Omega_eps\^\(3/2\)\*\|phi_eps\|\)\]",
        action.get("bulk_gauged", ""),
    )
    ghy = re.fullmatch(
        r"S_GHY=M5\^(?P<m5>[0-9]+)\*sum_eps int_Sigma sqrt\(-gamma\)\*Theta_eps for outward normals",
        action.get("GHY", ""),
    )
    if bulk is None or ghy is None:
        raise GravityFrechetError("EH or GHY literal is outside the exact grammar")
    parsed = ParsedCharter(
        dict(action),
        int(bulk.group("den")),
        int(bulk.group("m5")),
        int(ghy.group("m5")),
    )
    if (parsed.eh_denominator, parsed.m5_power_bulk, parsed.m5_power_ghy) != (2, 3, 3):
        raise GravityFrechetError("literal EH/GHY coefficients differ from v5.2")
    return parsed


@dataclass(frozen=True)
class Program:
    parsed: ParsedCharter
    components: Mapping[str, Expr]
    tangents: Mapping[str, Expr]
    side_geometry: Mapping[str, Mapping[str, Expr]]
    mutation: str | None


def _bulk_geometry(side: str, ricci_label: str) -> tuple[dict[str, Expr], Expr]:
    g = field(f"g_{side}", METRIC5)
    g1 = field(f"g1_{side}", METRIC1JET5)
    g2 = field(f"g2_{side}", METRIC2JET5)
    inverse = inverse_metric(g)
    gamma = multilinear("Christoffel_5", inverse, g1)
    dgamma = add(
        multilinear("partial_Christoffel_inverse_leg", inverse, inverse, g1, g1),
        multilinear("partial_Christoffel_second_jet", inverse, g2),
    )
    ricci = add(
        multilinear(ricci_label, dgamma),
        multilinear("Ricci_Gamma_Gamma", gamma, gamma),
    )
    scalar = multilinear("trace_Ricci", inverse, ricci)
    geometry = {
        "g": g,
        "g1": g1,
        "g2": g2,
        "inverse": inverse,
        "Gamma": gamma,
        "dGamma": dgamma,
        "Ricci": ricci,
        "R": scalar,
    }
    return geometry, multilinear("density_times_scalar_5", volume_density(g), scalar)


def _ghy_geometry(
    side: str,
    bulk: Mapping[str, Expr],
    *,
    mutation: str | None,
) -> tuple[dict[str, Expr], Expr]:
    embedding = field(f"Y_{side}", MAP5)
    embedding1 = field(f"Y1_{side}", MAP1)
    embedding2 = field(f"Y2_{side}", MAP2)
    moving = mutation != "omit_moved_point"
    pulled_g = evaluate_jet(bulk["g"], bulk["g1"], embedding, 0, moving=moving)
    pulled_g1 = evaluate_jet(bulk["g1"], bulk["g2"], embedding, 1, moving=moving)
    pulled_inverse = inverse_metric(pulled_g)
    pulled_gamma = multilinear("Christoffel_5_at_Sigma", pulled_inverse, pulled_g1)
    induced = multilinear("pullback_metric", pulled_g, embedding1, embedding1)
    induced_inverse = inverse_metric(induced)
    volume = volume_density(induced)
    cofactor = multilinear(
        "embedding_cofactor", embedding1, embedding1, embedding1, embedding1
    )
    norm_squared = multilinear(
        "cofactor_norm_squared", pulled_inverse, cofactor, cofactor
    )
    norm = sqrt_scalar(norm_squared)
    outward_sign = parameter(f"s_out_{side}")
    if mutation == "inward_normal":
        outward_sign = negate(outward_sign)
    if mutation == "frozen_normal":
        normal = field(f"n_frozen_{side}", NORMAL5)
    elif mutation == "unnormalized_normal":
        normal = multilinear(
            "normal_from_cofactor_constant_sign",
            outward_sign,
            cofactor,
        )
    else:
        normal = multilinear(
            "normal_from_cofactor",
            mul_scalar(outward_sign, power(norm, -1)),
            cofactor,
        )

    connection_acceleration = multilinear(
        "connection_pullback_acceleration", pulled_gamma, embedding1, embedding1
    )
    acceleration = (
        connection_acceleration
        if mutation == "omit_Y2"
        else covariant_acceleration(embedding2, connection_acceleration)
    )
    if mutation == "GHY_gamma_only":
        theta = field(f"Theta_gamma_only_{side}", SCALAR4)
    else:
        contraction = multilinear(
            "Theta_contraction", induced_inverse, normal, acceleration
        )
        theta = contraction if mutation == "wrong_Theta_sign" else negate(contraction)
    density = multilinear("density_times_scalar_4", volume, theta)
    geometry = {
        "Y": embedding,
        "Y1": embedding1,
        "Y2": embedding2,
        "pulled_g": pulled_g,
        "pulled_g1": pulled_g1,
        "pulled_inverse": pulled_inverse,
        "pulled_Gamma": pulled_gamma,
        "gamma": induced,
        "gamma_inverse": induced_inverse,
        "volume": volume,
        "cofactor": cofactor,
        "cofactor_norm_squared": norm_squared,
        "normal": normal,
        "Q": acceleration,
        "Theta": theta,
    }
    return geometry, density


def _read_once_M5_cubed_alias() -> Expr:
    """A one-leaf finite alias: P(1,2,3)=M5^3, but P(4)=1000."""

    return power(
        add(
            power(add(parameter("M5"), rational(-2)), 3),
            rational(2),
        ),
        3,
    )


def _replace_M5_cubed_by_read_once_alias(
    component: Expr, *, eh_component: bool
) -> Expr:
    """Test-only semantic mutant preserving row count and parameter-leaf count."""

    coupling = _read_once_M5_cubed_alias()
    outer = rational(Fraction(1, 2) if eh_component else Fraction(1))
    terms: list[Expr] = []
    for summand in _summands(component):
        if summand.op != "scale" or len(summand.args) != 2:
            raise GravityFrechetError(
                "read-once M5 alias requires the canonical coupled summand"
            )
        # Keep the two scale nodes intentionally unnormalised.  This attacks
        # an oracle which only looked at the outer scalar at M5=1; all three
        # derivative routes subsequently consume the nested primal normally.
        inner = Expr("scale", summand.type_tag, (coupling, summand.args[1]))
        terms.append(Expr("scale", summand.type_tag, (outer, inner)))
    return add(*terms)


def build_program(parsed: ParsedCharter, mutation: str | None = None) -> Program:
    ricci_label = (
        "Ricci_trace_sum_mutant" if mutation == "wrong_Ricci_trace" else "Ricci_trace_difference"
    )
    components: dict[str, Expr] = {}
    tangents: dict[str, Expr] = {}
    side_geometry: dict[str, Mapping[str, Expr]] = {}
    m5_power = power(parameter("M5"), parsed.m5_power_bulk)

    for side in ("plus", "minus"):
        bulk, eh_without_coupling = _bulk_geometry(side, ricci_label)
        eh_denominator = 1 if mutation == "wrong_EH_half" else parsed.eh_denominator
        components[f"EH_bulk_{side}"] = scale(
            mul_scalar(m5_power, rational(Fraction(1, eh_denominator))),
            eh_without_coupling,
        )
        ghy, ghy_without_coupling = _ghy_geometry(side, bulk, mutation=mutation)
        ghy_factor = Fraction(1, 2) if mutation == "wrong_GHY_half" else Fraction(1)
        components[f"GHY_{side}"] = scale(
            mul_scalar(power(parameter("M5"), parsed.m5_power_ghy), rational(ghy_factor)),
            ghy_without_coupling,
        )
        if mutation == "inject_Brown_York_target" and side == "plus":
            components[f"GHY_{side}"] = add(
                components[f"GHY_{side}"],
                field("Brown_York_target_forbidden", DENSITY4),
            )
        side_geometry[side] = {**bulk, **{f"GHY_{key}": value for key, value in ghy.items()}}

        h2_word = ("B", "A") if mutation == "collapse_mixed" else ("A", "B")
        xi2_word = ("nu", "mu") if mutation == "collapse_mixed" else ("mu", "nu")
        tangents.update(
            {
                f"g_{side}": variation(f"H_{side}", METRIC5),
                f"g1_{side}": variation(f"H_{side}", METRIC1JET5, ("A",)),
                f"g2_{side}": variation(f"H_{side}", METRIC2JET5, h2_word),
            }
        )
        if mutation != "freeze_Y":
            tangents.update(
                {
                    f"Y_{side}": variation(f"xi_{side}", MAP5),
                    f"Y1_{side}": variation(f"xi_{side}", MAP1, ("mu",)),
                    f"Y2_{side}": variation(f"xi_{side}", MAP2, xi2_word),
                }
            )

    if mutation == "primal_read_once_M5_alias":
        components = {
            name: _replace_M5_cubed_by_read_once_alias(
                component, eh_component=name.startswith("EH_bulk_")
            )
            for name, component in components.items()
        }

    ordered = {name: components[name] for name in COMPONENTS}
    return Program(parsed, ordered, tangents, side_geometry, mutation)


def _program_manifest(program: Program) -> dict[str, Any]:
    return {
        "components": {name: expr_row(expr) for name, expr in program.components.items()},
        "tangent_slots": {name: expr_row(expr) for name, expr in sorted(program.tangents.items())},
        "normal_orientation_constraints": {
            side: {
                "collar": f"M_{side}={{r_{side}>=0}}",
                "selector": f"n_{side}^A partial_A r_{side}<0",
                "sign_slot": f"s_out_{side}",
            }
            for side in ("plus", "minus")
        },
    }


@dataclass(frozen=True)
class DualExpr:
    primal: Expr
    tangent: Expr


def _sum_tangents(type_tag: GeoType, values: Iterable[Expr]) -> Expr:
    rows = [value for value in values if not is_zero(value)]
    return add(*rows) if rows else zero(type_tag)


def _inverse_sandwich_label(inverse_type: GeoType) -> str:
    return {
        INVERSE5: "inverse_sandwich_5",
        PULLED_INVERSE5: "inverse_sandwich_5_at_Sigma",
        INVERSE4: "inverse_sandwich_4",
    }[inverse_type]


def _metric_trace_label(inverse_type: GeoType) -> str:
    return {
        INVERSE5: "metric_trace_5",
        PULLED_INVERSE5: "metric_trace_5_at_Sigma",
        INVERSE4: "metric_trace_4",
    }[inverse_type]


def _evaluation_tangent(
    order: int,
    base_tangent: Expr,
    next_jet: Expr,
    embedding: Expr,
    embedding_tangent: Expr,
    target: GeoType,
    *,
    moving: bool,
) -> Expr:
    rows: list[Expr] = []
    if not is_zero(base_tangent):
        rows.append(
            multilinear(f"evaluate_metric_variation_{order}", base_tangent, embedding)
        )
    if moving and not is_zero(embedding_tangent):
        rows.append(
            multilinear(
                f"transport_metric_jet_{order}", next_jet, embedding, embedding_tangent
            )
        )
    return _sum_tangents(target, rows)


def forward_nilpotent_dual(
    expr: Expr,
    tangent_slots: Mapping[str, Expr],
    *,
    mutation: str | None = None,
) -> DualExpr:
    """Propagate a square-zero tangent through the gravity AST."""

    if expr.op in {"rational", "parameter", "zero"}:
        return DualExpr(expr, zero(expr.type_tag))
    if expr.op == "field":
        tangent = tangent_slots.get(expr.label, zero(expr.type_tag))
        if tangent.type_tag != expr.type_tag:
            raise GravityFrechetError(f"bad tangent type for {expr.label}")
        return DualExpr(expr, tangent)
    if expr.op in {"variation", "linear_slot"}:
        raise GravityFrechetError("a primal AST contains a linearized leaf")

    duals = tuple(
        forward_nilpotent_dual(arg, tangent_slots, mutation=mutation) for arg in expr.args
    )
    primals = tuple(item.primal for item in duals)
    tangents = tuple(item.tangent for item in duals)

    if expr.op == "add":
        return DualExpr(add(*primals), _sum_tangents(expr.type_tag, tangents))
    if expr.op == "mul_scalar":
        primal = mul_scalar(*primals)
        terms = [
            mul_scalar(tangent, *(arg for j, arg in enumerate(primals) if j != index))
            for index, tangent in enumerate(tangents)
            if not is_zero(tangent)
        ]
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "scale":
        primal = scale(primals[0], primals[1])
        terms = []
        if not is_zero(tangents[0]):
            terms.append(scale(tangents[0], primals[1]))
        if not is_zero(tangents[1]):
            terms.append(scale(primals[0], tangents[1]))
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "power":
        assert expr.exponent is not None
        primal = power(primals[0], expr.exponent)
        tangent = zero(expr.type_tag)
        if not is_zero(tangents[0]):
            tangent = mul_scalar(
                rational(expr.exponent),
                power(primals[0], expr.exponent - 1),
                tangents[0],
            )
        return DualExpr(primal, tangent)
    if expr.op == "sqrt":
        primal = sqrt_scalar(primals[0])
        tangent = zero(expr.type_tag)
        if not is_zero(tangents[0]):
            tangent = mul_scalar(
                rational(Fraction(1, 2)), power(primals[0], Fraction(-1, 2)), tangents[0]
            )
        return DualExpr(primal, tangent)
    if expr.op == "inverse_metric":
        primal = inverse_metric(primals[0])
        tangent = zero(expr.type_tag)
        if not is_zero(tangents[0]):
            if mutation == "correlated_inverse_operand_doubled":
                left_inverse = inverse_metric(add(primals[0], primals[0]))
            elif mutation == "correlated_inverse_operand_scaled_by_M5":
                left_inverse = inverse_metric(scale(parameter("M5"), primals[0]))
            else:
                left_inverse = primal
            tangent = negate(
                multilinear(
                    _inverse_sandwich_label(primal.type_tag),
                    left_inverse,
                    tangents[0],
                    primal,
                )
            )
            if mutation in {
                "wrong_inverse_sign",
                "correlated_wrong_inverse_sign",
            }:
                tangent = negate(tangent)
        return DualExpr(primal, tangent)
    if expr.op == "volume_density":
        primal = volume_density(primals[0])
        tangent = zero(expr.type_tag)
        if not is_zero(tangents[0]):
            inverse = inverse_metric(primals[0])
            half = (
                Fraction(1)
                if mutation
                in {"wrong_volume_half", "correlated_wrong_volume_half"}
                else Fraction(1, 2)
            )
            trace = multilinear(_metric_trace_label(inverse.type_tag), inverse, tangents[0])
            tangent = scale(mul_scalar(rational(half), trace), primal)
        return DualExpr(primal, tangent)
    if expr.op == "multilinear":
        primal = multilinear(expr.label, *primals)
        terms = [
            multilinear(expr.label, *(primals[:index] + (tangent,) + primals[index + 1 :]))
            for index, tangent in enumerate(tangents)
            if not is_zero(tangent)
        ]
        return DualExpr(primal, _sum_tangents(expr.type_tag, terms))
    if expr.op == "covariant_acceleration":
        primal = covariant_acceleration(primals[0], primals[1])
        terms: list[Expr] = []
        if not is_zero(tangents[0]):
            terms.append(covariant_acceleration(tangents[0], zero(ACCELERATION5)))
        if not is_zero(tangents[1]):
            terms.append(tangents[1])
        return DualExpr(primal, _sum_tangents(ACCELERATION5, terms))
    if expr.op == "evaluate_jet":
        order = 0 if expr.label.startswith("metric_jet_0") else 1
        moving = expr.label.endswith("moving_Y")
        primal = evaluate_jet(primals[0], primals[1], primals[2], order, moving=moving)
        tangent = _evaluation_tangent(
            order,
            tangents[0],
            primals[1],
            primals[2],
            tangents[2],
            expr.type_tag,
            moving=moving,
        )
        return DualExpr(primal, tangent)
    raise GravityFrechetError(f"forward dual has no rule for {expr.op}")


def _active_occurrences(
    expr: Expr,
    tangent_slots: Mapping[str, Expr],
    prefix: tuple[int, ...] = (),
) -> Iterable[tuple[tuple[int, ...], Expr]]:
    if expr.op == "field" and expr.label in tangent_slots:
        yield prefix, tangent_slots[expr.label]
        return
    for index, arg in enumerate(expr.args):
        yield from _active_occurrences(arg, tangent_slots, prefix + (index,))


def _reverse_local_lift(
    parent: Expr,
    child_index: int,
    child_tangent: Expr,
    *,
    mutation: str | None = None,
) -> Expr:
    """Independent local JVP rule used only by reverse context propagation."""

    args = parent.args
    if parent.op == "add":
        return child_tangent
    if parent.op == "mul_scalar":
        return mul_scalar(
            child_tangent, *(arg for index, arg in enumerate(args) if index != child_index)
        )
    if parent.op == "scale":
        return scale(child_tangent, args[1]) if child_index == 0 else scale(args[0], child_tangent)
    if parent.op == "power":
        assert parent.exponent is not None
        return mul_scalar(
            rational(parent.exponent),
            power(args[0], parent.exponent - 1),
            child_tangent,
        )
    if parent.op == "sqrt":
        return mul_scalar(
            rational(Fraction(1, 2)), power(args[0], Fraction(-1, 2)), child_tangent
        )
    if parent.op == "inverse_metric":
        inverse = inverse_metric(args[0])
        if mutation == "correlated_inverse_operand_doubled":
            left_inverse = inverse_metric(add(args[0], args[0]))
        elif mutation == "correlated_inverse_operand_scaled_by_M5":
            left_inverse = inverse_metric(scale(parameter("M5"), args[0]))
        else:
            left_inverse = inverse
        tangent = negate(
            multilinear(
                _inverse_sandwich_label(inverse.type_tag),
                left_inverse,
                child_tangent,
                inverse,
            )
        )
        return (
            negate(tangent)
            if mutation == "correlated_wrong_inverse_sign"
            else tangent
        )
    if parent.op == "volume_density":
        inverse = inverse_metric(args[0])
        trace = multilinear(_metric_trace_label(inverse.type_tag), inverse, child_tangent)
        factor = (
            Fraction(1)
            if mutation == "correlated_wrong_volume_half"
            else Fraction(1, 2)
        )
        return scale(mul_scalar(rational(factor), trace), volume_density(args[0]))
    if parent.op == "multilinear":
        return multilinear(
            parent.label, *(args[:child_index] + (child_tangent,) + args[child_index + 1 :])
        )
    if parent.op == "covariant_acceleration":
        if child_index == 0:
            return covariant_acceleration(child_tangent, zero(ACCELERATION5))
        return child_tangent
    if parent.op == "evaluate_jet":
        order = 0 if parent.label.startswith("metric_jet_0") else 1
        moving = parent.label.endswith("moving_Y")
        if child_index == 0:
            return multilinear(f"evaluate_metric_variation_{order}", child_tangent, args[2])
        if child_index == 1:
            # The next jet is context for the chain rule, not a direct argument
            # of evaluation of the lower jet.
            return zero(parent.type_tag)
        if child_index == 2 and moving:
            return multilinear(f"transport_metric_jet_{order}", args[1], args[2], child_tangent)
        return zero(parent.type_tag)
    raise GravityFrechetError(f"reverse context has no rule for {parent.op}")


def reverse_context_frechet(
    expr: Expr,
    tangent_slots: Mapping[str, Expr],
    *,
    mutation: str | None = None,
) -> Expr:
    contributions: list[Expr] = []
    for path, leaf_tangent in _active_occurrences(expr, tangent_slots):
        node = expr
        frames: list[tuple[Expr, int]] = []
        for index in path:
            frames.append((node, index))
            node = node.args[index]
        lifted = leaf_tangent
        for parent, index in reversed(frames):
            lifted = _reverse_local_lift(
                parent, index, lifted, mutation=mutation
            )
            if is_zero(lifted):
                break
        if not is_zero(lifted):
            contributions.append(lifted)
    return _sum_tangents(expr.type_tag, contributions)


def walk(expr: Expr) -> Iterable[Expr]:
    yield expr
    for arg in expr.args:
        yield from walk(arg)


def _summands(expr: Expr) -> tuple[Expr, ...]:
    return expr.args if expr.op == "add" else (expr,)


def _variation_count(expr: Expr) -> int:
    return sum(node.op == "variation" for node in walk(expr))


def _replace_variation_with_slot(expr: Expr) -> tuple[Expr, str, tuple[str, ...]]:
    leaves = [node for node in walk(expr) if node.op == "variation"]
    if len(leaves) != 1:
        raise GravityFrechetError(
            f"Frechet summand must contain one variation leaf, observed {len(leaves)}"
        )
    target = leaves[0]

    def replace(node: Expr) -> Expr:
        if node is target:
            return Expr("linear_slot", node.type_tag, label="eta")
        return Expr(
            node.op,
            node.type_tag,
            tuple(replace(arg) for arg in node.args),
            node.label,
            node.value,
            node.exponent,
            node.derivative_word,
        )

    return replace(expr), target.label, target.derivative_word


def _compat_type(type_tag: GeoType) -> dict[str, Any]:
    natural_bundle = (
        "Y_star_TM5"
        if type_tag in {MAP5, MAP1, MAP2, COFACTOR5, NORMAL5, ACCELERATION5}
        else "trivial"
    )
    return {
        "name": type_tag.name,
        "dimension": type_tag.base_dimension,
        "form_degree": type_tag.base_dimension if type_tag in {DENSITY5, DENSITY4} else 0,
        "bundle": natural_bundle,
        "variance": list(type_tag.variance),
        "density_weight": type_tag.density_weight,
        "symmetry": type_tag.symmetry,
        "fiber_dimension": 1,
    }


@dataclass(frozen=True)
class VariationBundleSpec:
    role: str
    jet_types: tuple[GeoType, ...]
    derivative_namespace: str
    derivative_dimension: int


VARIATION_BUNDLE_REGISTRY = {
    **{
        f"H_{side}": VariationBundleSpec(
            "bulk_metric",
            (METRIC5, METRIC1JET5, METRIC2JET5),
            f"M_{side}.coordinate",
            5,
        )
        for side in ("plus", "minus")
    },
    **{
        f"xi_{side}": VariationBundleSpec(
            "embedding_map",
            (MAP5, MAP1, MAP2),
            "Sigma.coordinate",
            4,
        )
        for side in ("plus", "minus")
    },
}


def _variation_bundle_spec(variation_component: str) -> VariationBundleSpec:
    try:
        return VARIATION_BUNDLE_REGISTRY[variation_component]
    except KeyError as exc:
        raise GravityFrechetError(
            f"unknown Frechet variation component {variation_component}"
        ) from exc


def _row_binders(
    variation_component: str,
    word: Sequence[int],
    *,
    alpha_normalized: bool = True,
) -> list[dict[str, Any]]:
    spec = _variation_bundle_spec(variation_component)
    return [
        {
            "id": identifier,
            "namespace": spec.derivative_namespace,
            "dimension": spec.derivative_dimension,
            "variance": "down",
            "scope": "row",
            "alpha_normalized": alpha_normalized,
        }
        for identifier in word
    ]


def coefficient_ast(expr: Expr) -> dict[str, Any]:
    if expr.op == "variation":
        raise GravityFrechetError("coefficient AST retained a variation leaf")
    row: dict[str, Any] = {
        "op": expr.op,
        "type": _compat_type(expr.type_tag),
    }
    if expr.op == "rational":
        row["op"] = "const"
        assert expr.value is not None
        row["value"] = [expr.value.numerator, expr.value.denominator]
    elif expr.op == "parameter":
        row["op"] = "param"
        row["symbol"] = expr.label
    elif expr.op == "field":
        row["op"] = "jet"
        match = re.fullmatch(r"(?P<stem>g|Y)(?P<order>[12])_(?P<side>plus|minus)", expr.label)
        if match is None:
            symbol = expr.label
            word: list[int] = []
            namespace = ""
            dimension = expr.type_tag.base_dimension
        else:
            symbol = f"{match.group('stem')}_{match.group('side')}"
            word = list(range(int(match.group("order"))))
            if match.group("stem") == "g":
                namespace = f"M_{match.group('side')}.coordinate"
                dimension = 5
            else:
                namespace = "Sigma.coordinate"
                dimension = 4
        row["symbol"] = symbol
        derivative: dict[str, Any] = {"kind": "partial", "word": word}
        if word:
            derivative["binders"] = [
                {
                    "id": identifier,
                    "namespace": namespace,
                    "dimension": dimension,
                    "variance": "down",
                    "scope": "node",
                    "alpha_normalized": True,
                }
                for identifier in word
            ]
        row["derivative"] = derivative
    elif expr.op == "linear_slot":
        row["slot"] = "eta"
        row["external_derivative_word"] = []
    elif expr.op == "zero":
        row["op"] = "const"
        row["value"] = [0, 1]
    elif expr.op == "add":
        pass
    elif expr.op in {"mul_scalar", "scale"}:
        row["op"] = "mul"
    elif expr.op == "power":
        row["op"] = "pow"
        assert expr.exponent is not None
        row["exponent"] = [expr.exponent.numerator, expr.exponent.denominator]
    elif expr.op in {"sqrt", "inverse_metric", "volume_density"}:
        pass
    elif expr.op == "multilinear":
        row["op"] = "tensor_contract"
        row["convention"] = expr.label
    elif expr.op == "covariant_acceleration":
        row["convention"] = expr.label
    elif expr.op == "evaluate_jet":
        row["op"] = "jet_evaluation"
        row["convention"] = expr.label
    else:
        raise GravityFrechetError(f"no FrechetRowV1 serialization for {expr.op}")
    if expr.args:
        row["args"] = [coefficient_ast(arg) for arg in expr.args]
    return row


def _set_linear_slot_word(ast: dict[str, Any], word: Sequence[int]) -> int:
    count = 0
    if ast.get("op") == "linear_slot":
        ast["external_derivative_word"] = list(word)
        count += 1
    for arg in ast.get("args", []):
        count += _set_linear_slot_word(arg, word)
    return count


def _source_spans(component: str, parsed: ParsedCharter) -> list[dict[str, Any]]:
    keys = ("total", "bulk_gauged") if component.startswith("EH_") else ("total", "GHY")
    return [
        {
            "action_key": key,
            "start": 0,
            "end": len(parsed.action[key]),
            "sha256": hashlib.sha256(parsed.action[key].encode("utf-8")).hexdigest(),
        }
        for key in keys
    ]


def export_frechet_rows(
    program: Program,
    derivatives: Mapping[str, Expr],
) -> list[dict[str, Any]]:
    if tuple(derivatives) != COMPONENTS:
        raise GravityFrechetError("four-component derivative inventory drift")
    rows: list[dict[str, Any]] = []
    for component, derivative in derivatives.items():
        for ordinal, summand in enumerate(_summands(derivative)):
            coefficient, variation_component, source_word = _replace_variation_with_slot(summand)
            word = tuple(range(len(source_word)))
            variation_spec = _variation_bundle_spec(variation_component)
            role = variation_spec.role
            ast = coefficient_ast(coefficient)
            if _set_linear_slot_word(ast, word) != 1:
                raise GravityFrechetError("coefficient AST must contain one bound linear slot")
            domain = (
                f"M_{component.rsplit('_', 1)[1]}"
                if component.startswith("EH_")
                else "Sigma"
            )
            derivative_row: dict[str, Any] = {"kind": "partial", "word": list(word)}
            if word:
                derivative_row["binders"] = _row_binders(
                    variation_component, word
                )
            rows.append(
                {
                    "schema": FRECHET_ROW_SCHEMA,
                    "component": component,
                    "domain": domain,
                    "role": role,
                    "variation_component": variation_component,
                    "derivative": derivative_row,
                    "coefficient_ast_sha256": _canonical_sha256(ast),
                    "coefficient_ast": ast,
                    "source_spans": _source_spans(component, program.parsed),
                    "summand_ordinal": ordinal,
                }
            )
    return rows


def _linear_slots(ast: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = [ast] if ast.get("op") == "linear_slot" else []
    args = ast.get("args", [])
    if type(args) is list:
        for arg in args:
            if type(arg) is dict:
                rows.extend(_linear_slots(arg))
    return rows


def _illegal_external_capture(ast: Mapping[str, Any]) -> bool:
    if ast.get("op") != "linear_slot" and "external_derivative_word" in ast:
        return True
    args = ast.get("args", [])
    return type(args) is list and any(
        type(arg) is dict and _illegal_external_capture(arg) for arg in args
    )


_COMPAT_AST_FIELDS = {
    "const": {"op", "type", "value"},
    "param": {"op", "type", "symbol"},
    "jet": {"op", "type", "symbol", "derivative"},
    "linear_slot": {"op", "type", "slot", "external_derivative_word"},
    "add": {"op", "type", "args"},
    "mul": {"op", "type", "args"},
    "pow": {"op", "type", "args", "exponent"},
    "sqrt": {"op", "type", "args"},
    "inverse_metric": {"op", "type", "args"},
    "volume_density": {"op", "type", "args"},
    "tensor_contract": {"op", "type", "args", "convention"},
    "covariant_acceleration": {"op", "type", "args", "convention"},
    "jet_evaluation": {"op", "type", "args", "convention"},
}


def _compat_ast_type(ast: Mapping[str, Any]) -> GeoType:
    type_row = ast.get("type")
    if type(type_row) is not dict:
        raise GravityFrechetError("coefficient node type is absent")
    try:
        expected_type = TYPE_TABLE[str(type_row["name"])]
    except (KeyError, TypeError) as exc:
        raise GravityFrechetError("unknown coefficient node type") from exc
    if type_row != _compat_type(expected_type):
        raise GravityFrechetError("coefficient node type metadata drift")
    return expected_type


def _require_compat_signature(
    ast: Mapping[str, Any],
    args: Sequence[Mapping[str, Any]],
    argument_types: Sequence[GeoType],
    result_type: GeoType,
    message: str,
) -> None:
    if (
        [_compat_ast_type(arg) for arg in args] != list(argument_types)
        or _compat_ast_type(ast) != result_type
    ):
        raise GravityFrechetError(message)


def _validate_compat_types_and_node_binders(ast: Mapping[str, Any]) -> None:
    if type(ast) is not dict:
        raise GravityFrechetError("coefficient AST node must be an object")
    operation = ast.get("op")
    if type(operation) is not str or operation not in _COMPAT_AST_FIELDS:
        raise GravityFrechetError("unknown coefficient AST opcode")
    if set(ast) != _COMPAT_AST_FIELDS[operation]:
        raise GravityFrechetError("coefficient AST opcode field inventory drift")
    result_type = _compat_ast_type(ast)
    args = ast.get("args", [])
    if operation in {"const", "param", "jet", "linear_slot"}:
        if "args" in ast:
            raise GravityFrechetError("coefficient AST leaf unexpectedly has arguments")
    elif type(args) is not list or any(type(arg) is not dict for arg in args):
        raise GravityFrechetError("coefficient node argument inventory drift")

    if operation == "const":
        value = ast.get("value")
        if (
            type(value) is not list
            or len(value) != 2
            or any(type(item) is not int for item in value)
            or value[1] == 0
        ):
            raise GravityFrechetError("constant rational payload drift")
        if not _is_scalar(result_type) and value[0] != 0:
            raise GravityFrechetError("nonzero tensor constant is not a scalar")
    elif operation == "param":
        expected_parameter_types = {
            "M5": SCALAR0,
            "s_out_plus": OUTWARD_SIGN,
            "s_out_minus": OUTWARD_SIGN,
        }
        if expected_parameter_types.get(ast.get("symbol")) != result_type:
            raise GravityFrechetError("parameter leaf signature drift")
    elif operation == "jet":
        symbol = ast.get("symbol")
        if type(symbol) is not str or symbol not in {
            "g_plus",
            "g_minus",
            "Y_plus",
            "Y_minus",
        }:
            raise GravityFrechetError("internal jet symbol inventory drift")
    elif operation == "linear_slot":
        external_word = ast.get("external_derivative_word")
        if (
            ast.get("slot") != "eta"
            or type(external_word) is not list
            or any(type(identifier) is not int for identifier in external_word)
            or external_word != list(range(len(external_word)))
            or len(external_word) > 2
        ):
            raise GravityFrechetError("linear slot signature drift")
    elif operation == "add":
        if len(args) < 2 or any(_compat_ast_type(arg) != result_type for arg in args):
            raise GravityFrechetError("addition signature drift")
    elif operation == "mul":
        if len(args) < 2:
            raise GravityFrechetError("multiplication arity drift")
        argument_types = [_compat_ast_type(arg) for arg in args]
        if all(_is_scalar(item) for item in argument_types):
            if _scalar_result(argument_types) != result_type:
                raise GravityFrechetError("scalar multiplication signature drift")
        elif len(args) == 2 and _is_scalar(argument_types[0]):
            scalar_type, value_type = argument_types
            if (
                scalar_type.density_weight != 0
                or scalar_type.base_dimension not in {0, value_type.base_dimension}
                or result_type != value_type
            ):
                raise GravityFrechetError("typed scale signature drift")
        else:
            raise GravityFrechetError("multiplication received an untyped tensor product")
    elif operation == "pow":
        exponent = ast.get("exponent")
        if (
            len(args) != 1
            or type(exponent) is not list
            or len(exponent) != 2
            or any(type(item) is not int for item in exponent)
            or exponent[1] == 0
        ):
            raise GravityFrechetError("power payload or arity drift")
        argument_type = _compat_ast_type(args[0])
        if not _is_scalar(argument_type):
            raise GravityFrechetError("power requires a scalar")
        power_value = Fraction(exponent[0], exponent[1])
        target_weight = argument_type.density_weight * power_value
        if target_weight.denominator != 1 or result_type != _scalar_type(
            argument_type.base_dimension, target_weight.numerator
        ):
            raise GravityFrechetError("power result type drift")
    elif operation == "sqrt":
        if len(args) != 1:
            raise GravityFrechetError("sqrt arity drift")
        argument_type = _compat_ast_type(args[0])
        if not _is_scalar(argument_type) or argument_type.density_weight % 2:
            raise GravityFrechetError("sqrt requires an even-weight scalar")
        if result_type != _scalar_type(
            argument_type.base_dimension, argument_type.density_weight // 2
        ):
            raise GravityFrechetError("sqrt result type drift")
    elif operation == "inverse_metric":
        if len(args) != 1:
            raise GravityFrechetError("inverse metric arity drift")
        expected = {
            METRIC5: INVERSE5,
            PULLED_METRIC5: PULLED_INVERSE5,
            METRIC4: INVERSE4,
        }.get(_compat_ast_type(args[0]))
        if expected is None or result_type != expected:
            raise GravityFrechetError("inverse metric signature drift")
    elif operation == "volume_density":
        if len(args) != 1:
            raise GravityFrechetError("volume density arity drift")
        expected = {METRIC5: DENSITY5, METRIC4: DENSITY4}.get(
            _compat_ast_type(args[0])
        )
        if expected is None or result_type != expected:
            raise GravityFrechetError("volume density signature drift")
    elif operation == "tensor_contract":
        convention = ast.get("convention")
        if type(convention) is not str:
            raise GravityFrechetError("tensor contraction convention drift")
        try:
            argument_types, result_type = OP_SIGNATURES[convention]
        except KeyError as exc:
            raise GravityFrechetError("unknown tensor contraction convention") from exc
        _require_compat_signature(
            ast, args, argument_types, result_type,
            "tensor contraction signature drift",
        )
    elif operation == "covariant_acceleration":
        if ast.get("convention") != "D2Y_plus_connection_pullback":
            raise GravityFrechetError("covariant acceleration convention drift")
        _require_compat_signature(
            ast,
            args,
            (MAP2, ACCELERATION5),
            ACCELERATION5,
            "covariant acceleration signature drift",
        )
    elif operation == "jet_evaluation":
        convention = ast.get("convention")
        conventions = {
            "metric_jet_0_at_moving_Y": 0,
            "metric_jet_0_at_frozen_Y": 0,
            "metric_jet_1_at_moving_Y": 1,
            "metric_jet_1_at_frozen_Y": 1,
        }
        try:
            order = conventions[convention]
        except (KeyError, TypeError) as exc:
            raise GravityFrechetError("unknown jet evaluation convention") from exc
        specs = {
            0: ((METRIC5, METRIC1JET5, MAP5), PULLED_METRIC5),
            1: ((METRIC1JET5, METRIC2JET5, MAP5), PULLED_METRIC1),
        }
        argument_types, result_type = specs[order]
        _require_compat_signature(
            ast, args, argument_types, result_type,
            "jet evaluation signature drift",
        )

    if operation == "jet":
        derivative = ast.get("derivative")
        if (
            type(derivative) is not dict
            or set(derivative) not in ({"kind", "word"}, {"kind", "word", "binders"})
            or derivative.get("kind") != "partial"
        ):
            raise GravityFrechetError("internal jet derivative metadata missing")
        word = derivative.get("word")
        if type(word) is not list or word != list(range(len(word))) or len(word) > 2:
            raise GravityFrechetError("internal jet word is not alpha-normalized")
        expected_derivative_fields = (
            {"kind", "word", "binders"} if word else {"kind", "word"}
        )
        if set(derivative) != expected_derivative_fields:
            raise GravityFrechetError("internal jet derivative field inventory drift")
        expected_jet_types = {
            "g_plus": (METRIC5, METRIC1JET5, METRIC2JET5),
            "g_minus": (METRIC5, METRIC1JET5, METRIC2JET5),
            "Y_plus": (MAP5, MAP1, MAP2),
            "Y_minus": (MAP5, MAP1, MAP2),
        }
        if result_type != expected_jet_types[str(ast.get("symbol"))][len(word)]:
            raise GravityFrechetError("internal jet type disagrees with its word")
        binders = derivative.get("binders", [])
        if word:
            symbol = str(ast.get("symbol"))
            if symbol.startswith("g_"):
                namespace = f"M_{symbol.rsplit('_', 1)[1]}.coordinate"
                dimension = 5
            elif symbol.startswith("Y_"):
                namespace = "Sigma.coordinate"
                dimension = 4
            else:
                raise GravityFrechetError("differentiated internal jet has no namespace")
            expected = [
                {
                    "id": identifier,
                    "namespace": namespace,
                    "dimension": dimension,
                    "variance": "down",
                    "scope": "node",
                    "alpha_normalized": True,
                }
                for identifier in word
            ]
            if binders != expected:
                raise GravityFrechetError("internal jet binder capture or namespace drift")
            if any(type(binder) is not dict or set(binder) != {
                "id", "namespace", "dimension", "variance", "scope",
                "alpha_normalized",
            } for binder in binders):
                raise GravityFrechetError("internal jet binder field inventory drift")
        elif binders:
            raise GravityFrechetError("zeroth-order internal jet has an unused binder")
    for arg in args:
        _validate_compat_types_and_node_binders(arg)


def _expected_linear_slot_type(variation_component: str, order: int) -> GeoType:
    choices = _variation_bundle_spec(variation_component).jet_types
    if order >= len(choices):
        raise GravityFrechetError("Frechet derivative order exceeds this subgate")
    return choices[order]


_FRECHET_ROW_FIELDS = {
    "schema",
    "component",
    "domain",
    "role",
    "variation_component",
    "derivative",
    "coefficient_ast_sha256",
    "coefficient_ast",
    "source_spans",
    "summand_ordinal",
}


def _validate_row_source_spans(spans: Any) -> None:
    if type(spans) is not list or not spans:
        raise GravityFrechetError("Frechet source span inventory is absent")
    action_keys: list[str] = []
    for span in spans:
        if type(span) is not dict or set(span) != {"action_key", "start", "end", "sha256"}:
            raise GravityFrechetError("Frechet source span field inventory drift")
        action_key = span.get("action_key")
        start = span.get("start")
        end = span.get("end")
        digest = span.get("sha256")
        if (
            type(action_key) is not str
            or action_key not in ACTION_KEYS
            or type(start) is not int
            or type(end) is not int
            or start != 0
            or end <= start
            or type(digest) is not str
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise GravityFrechetError("Frechet source span value drift")
        action_keys.append(action_key)
    if len(action_keys) != len(set(action_keys)):
        raise GravityFrechetError("Frechet source span action key duplicated")


def validate_neutral_frechet_row(row: Mapping[str, Any]) -> bool:
    """Validate the shared row mechanics without an S10/S11 component whitelist."""

    if type(row) is not dict or set(row) != _FRECHET_ROW_FIELDS:
        raise GravityFrechetError("Frechet row field inventory drift")
    if row.get("schema") != FRECHET_ROW_SCHEMA:
        raise GravityFrechetError("Frechet row schema drift")
    for key in ("component", "domain", "role", "variation_component"):
        if type(row.get(key)) is not str or not row[key]:
            raise GravityFrechetError(f"Frechet row {key} is not a nonempty string")
    if type(row.get("summand_ordinal")) is not int or row["summand_ordinal"] < 0:
        raise GravityFrechetError("Frechet summand ordinal drift")
    digest = row.get("coefficient_ast_sha256")
    if type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise GravityFrechetError("Frechet coefficient AST digest format drift")
    _validate_row_source_spans(row.get("source_spans"))
    variation_component = row["variation_component"]
    spec = _variation_bundle_spec(variation_component)
    derivative = row.get("derivative")
    if (
        type(derivative) is not dict
        or set(derivative) not in ({"kind", "word"}, {"kind", "word", "binders"})
        or derivative.get("kind") != "partial"
    ):
        raise GravityFrechetError("Frechet derivative kind drift")
    word = derivative.get("word")
    if (
        type(word) is not list
        or word != list(range(len(word)))
        or len(word) >= len(spec.jet_types)
    ):
        raise GravityFrechetError("Frechet word is free or not alpha-normalized")
    expected_derivative_fields = (
        {"kind", "word", "binders"} if word else {"kind", "word"}
    )
    if set(derivative) != expected_derivative_fields:
        raise GravityFrechetError("Frechet derivative field inventory drift")
    binders = derivative.get("binders", [])
    if word:
        expected = _row_binders(variation_component, word)
        if binders != expected:
            raise GravityFrechetError(
                "Frechet binder capture/dimension/variance/namespace drift"
            )
    elif binders:
        raise GravityFrechetError("zeroth-order row has an unused binder")
    ast = row.get("coefficient_ast")
    if type(ast) is not dict:
        raise GravityFrechetError("Frechet coefficient AST missing")
    if row.get("coefficient_ast_sha256") != _canonical_sha256(ast):
        raise GravityFrechetError("Frechet coefficient AST hash drift")
    if _illegal_external_capture(ast):
        raise GravityFrechetError("row binder captured outside the linear slot")
    slots = _linear_slots(ast)
    if len(slots) != 1 or slots[0].get("external_derivative_word") != word:
        raise GravityFrechetError("linear slot and row derivative word disagree")
    expected_slot_type = _compat_type(
        _expected_linear_slot_type(variation_component, len(word))
    )
    if slots[0].get("type") != expected_slot_type:
        raise GravityFrechetError("linear slot type disagrees with its derivative order")
    _validate_compat_types_and_node_binders(ast)
    if row.get("role") != spec.role:
        raise GravityFrechetError("Frechet variation role drift")
    return True


EXPECTED_COMPONENT_ROW_COUNTS = {
    "EH_bulk_plus": 16,
    "GHY_plus": 29,
    "EH_bulk_minus": 16,
    "GHY_minus": 29,
}


def validate_frechet_row(
    row: Mapping[str, Any],
    parsed: ParsedCharter | None = None,
) -> bool:
    """Apply the local four-component scope after the neutral row check."""

    validate_neutral_frechet_row(row)
    component = str(row.get("component"))
    if component not in COMPONENTS:
        raise GravityFrechetError("Frechet row component drift")
    domain = (
        f"M_{component.rsplit('_', 1)[1]}" if component.startswith("EH_") else "Sigma"
    )
    if row.get("domain") != domain:
        raise GravityFrechetError("Frechet row domain drift")
    if parsed is None:
        _, action, _ = certify_v52_dependency()
        parsed = parse_charter(action)
    expected_spans = _source_spans(component, parsed)
    if row.get("source_spans") != expected_spans:
        raise GravityFrechetError(
            "Frechet row source spans do not bind the parsed action bytes"
        )
    side = component.rsplit("_", 1)[1]
    expected_variations = (
        {f"H_{side}"}
        if component.startswith("EH_")
        else {f"H_{side}", f"xi_{side}"}
    )
    if row.get("variation_component") not in expected_variations:
        raise GravityFrechetError("Frechet variation component side drift")
    sideful_symbols = [
        str(node.get("symbol"))
        for node in _row_walk(row["coefficient_ast"])
        if node.get("op") == "jet"
    ]
    if any(symbol not in {f"g_{side}", f"Y_{side}"} for symbol in sideful_symbols):
        raise GravityFrechetError("Frechet coefficient jet symbol side drift")
    orientation_parameters = [
        str(node.get("symbol"))
        for node in _row_walk(row["coefficient_ast"])
        if node.get("op") == "param"
        and _compat_ast_type(node) == OUTWARD_SIGN
    ]
    expected_orientation_parameters = (
        [] if component.startswith("EH_") else [f"s_out_{side}"]
    )
    if orientation_parameters != expected_orientation_parameters:
        raise GravityFrechetError(
            "Frechet coefficient outward selector inventory or side drift"
        )
    return True


def frechet_row_collection_certificate(
    rows: Sequence[Mapping[str, Any]],
    parsed: ParsedCharter,
) -> dict[str, Any]:
    """Validate the complete ordered four-component export, not isolated rows."""

    if type(rows) is not list:
        raise GravityFrechetError("Frechet row collection must be a list")
    expected_order = [
        (component, ordinal)
        for component in COMPONENTS
        for ordinal in range(EXPECTED_COMPONENT_ROW_COUNTS[component])
    ]
    observed_order = [
        (row.get("component"), row.get("summand_ordinal"))
        for row in rows
    ]
    if len(observed_order) != len(set(observed_order)):
        raise GravityFrechetError("Frechet component ordinal duplicated")
    if observed_order != expected_order:
        raise GravityFrechetError(
            "Frechet component counts or canonical contiguous ordinals drift"
        )
    for row in rows:
        validate_frechet_row(row, parsed)
    observed_counts = {
        component: sum(row["component"] == component for row in rows)
        for component in COMPONENTS
    }
    return {
        "pass": observed_counts == EXPECTED_COMPONENT_ROW_COUNTS,
        "expected_component_counts": dict(EXPECTED_COMPONENT_ROW_COUNTS),
        "observed_component_counts": observed_counts,
        "canonical_component_order": list(COMPONENTS),
        "ordinals_contiguous_and_unique": True,
        "parsed_action_sha256": _canonical_sha256(parsed.action),
        "side_consistency_checked": True,
        "source_spans_bound_to_parsed_action": True,
    }


def canonicalize_frechet_row_binders(row: Mapping[str, Any]) -> dict[str, Any]:
    """Alpha-normalize one row, including arbitrary one- or two-index words."""

    canonical = copy.deepcopy(dict(row))
    derivative = canonical.get("derivative")
    if type(derivative) is not dict or type(derivative.get("word")) is not list:
        raise GravityFrechetError("cannot alpha-normalize a malformed derivative")
    word = derivative["word"]
    if not word:
        validate_frechet_row(canonical)
        return canonical
    binders = derivative.get("binders", [])
    if len(binders) != len(word) or [binder.get("id") for binder in binders] != word:
        raise GravityFrechetError("cannot alpha-normalize a free or captured binder")
    if len(set(word)) != len(word):
        raise GravityFrechetError("cannot alpha-normalize repeated binder ids")
    variation_component = str(canonical.get("variation_component"))
    spec = _variation_bundle_spec(variation_component)
    for binder in binders:
        expected_tail = {
            "namespace": spec.derivative_namespace,
            "dimension": spec.derivative_dimension,
            "variance": "down",
            "scope": "row",
        }
        if any(binder.get(key) != value for key, value in expected_tail.items()):
            raise GravityFrechetError("cannot alpha-normalize binder metadata drift")
    slots = _linear_slots(canonical["coefficient_ast"])
    if len(slots) != 1 or slots[0].get("external_derivative_word") != word:
        raise GravityFrechetError("cannot alpha-normalize a captured linear slot")
    normalized = list(range(len(word)))
    derivative["word"] = normalized
    for identifier, binder in enumerate(binders):
        binder["id"] = identifier
        binder["alpha_normalized"] = True
    slots[0]["external_derivative_word"] = normalized
    canonical["coefficient_ast_sha256"] = _canonical_sha256(canonical["coefficient_ast"])
    validate_frechet_row(canonical)
    return canonical


def _operator_labels(expr: Expr) -> set[str]:
    return {
        node.label if node.op != "covariant_acceleration" else "covariant_acceleration"
        for node in walk(expr)
        if node.op in {"multilinear", "covariant_acceleration"}
    }


def _field_labels(expr: Expr) -> set[str]:
    return {node.label for node in walk(expr) if node.op == "field"}


def _transparency_certificate(program: Program) -> dict[str, Any]:
    labels = set().union(*(_operator_labels(expr) for expr in program.components.values()))
    fields = set().union(*(_field_labels(expr) for expr in program.components.values()))
    expected_fields = {
        f"{stem}_{side}"
        for side in ("plus", "minus")
        for stem in ("g", "g1", "g2", "Y", "Y1", "Y2")
    }
    unknown_operators = sorted(labels - set(OPERATOR_SEMANTICS))
    unexpected_fields = sorted(fields - expected_fields)
    serialized = json.dumps(
        {name: expr_row(expr) for name, expr in program.components.items()},
        sort_keys=True,
    )
    forbidden_tokens = [
        token
        for token in (
            "opaque",
            "placeholder",
            "deltaK/d",
            "deltaR/d",
            "Brown_York_target",
        )
        if token in serialized
    ]
    moving_evaluations = [
        node.label
        for expr in program.components.values()
        for node in walk(expr)
        if node.op == "evaluate_jet"
    ]
    declared_atoms = sorted(
        labels
        | set(moving_evaluations)
        | {"inverse_metric", "volume_density", "sqrt"}
    )
    passed = bool(
        not unknown_operators
        and not unexpected_fields
        and not forbidden_tokens
        and moving_evaluations
        and all(label.endswith("moving_Y") for label in moving_evaluations)
    )
    return {
        "pass": passed,
        "all_operator_labels_have_declared_denotations": not unknown_operators,
        "every_primitive_has_independent_executable_coordinate_denotation": False,
        "unknown_operators": unknown_operators,
        "unexpected_primitive_fields": unexpected_fields,
        "forbidden_tokens": forbidden_tokens,
        "evaluation_nodes": moving_evaluations,
        "coefficient_projection_atoms": declared_atoms,
        "projection_free_claim": False,
        "scope": (
            "closed declared primitive inventory only; strings and typed signatures are "
            "not an independent executable coordinate denotation"
        ),
    }


def _normal_theta_certificate(
    program: Program,
    semantic_completion: Mapping[str, Any],
) -> dict[str, Any]:
    sides: dict[str, Any] = {}
    for side in ("plus", "minus"):
        geometry = program.side_geometry[side]
        normal = geometry["GHY_normal"]
        theta = geometry["GHY_Theta"]
        normal_nodes = list(walk(normal))
        theta_nodes = list(walk(theta))
        has_cofactor = any(
            node.op == "multilinear" and node.label == "embedding_cofactor"
            for node in normal_nodes
        )
        has_norm = any(
            node.op == "multilinear" and node.label == "cofactor_norm_squared"
            for node in normal_nodes
        )
        has_inverse_sqrt = any(
            node.op == "power" and node.exponent == -1 and node.args[0].op == "sqrt"
            for node in normal_nodes
        )
        has_outward_slot = any(
            node.op == "parameter"
            and node.type_tag == OUTWARD_SIGN
            and node.label == f"s_out_{side}"
            for node in normal_nodes
        )
        theta_contracts = [
            node
            for node in theta_nodes
            if node.op == "multilinear" and node.label == "Theta_contraction"
        ]
        orientation_not_negated = not any(
            node.op == "rational" and node.value == -1 for node in normal_nodes
        )
        theta_minus = bool(theta_contracts) and all(
            any(node.op == "rational" and node.value == -1 for node in walk(term))
            and any(
                node.op == "multilinear" and node.label == "Theta_contraction"
                for node in walk(term)
            )
            for term in _summands(theta)
        )
        row_pass = bool(
            has_cofactor
            and has_norm
            and has_inverse_sqrt
            and has_outward_slot
            and orientation_not_negated
            and theta_minus
        )
        sides[side] = {
            "pass": row_pass,
            "cofactor_present": has_cofactor,
            "unit_normal_denominator_present": has_norm and has_inverse_sqrt,
            "outward_selector_slot": f"s_out_{side}",
            "outward_constraint": f"n_{side}^A partial_A r_{side}<0 on M_{side}={{r_{side}>=0}}",
            "orientation_slot_not_negated_by_side_name": orientation_not_negated,
            "Theta_is_minus_n_dot_Q": theta_minus,
            "normal_ast_sha256": _canonical_sha256(expr_row(normal)),
            "Theta_ast_sha256": _canonical_sha256(expr_row(theta)),
        }
    normal_formula = semantic_completion["embedding_and_normal"]["unit_normal"]
    theta_formula = semantic_completion["embedding_and_normal"]["extrinsic_trace"]
    completion_exact = bool(
        normal_formula == "n_A=s_out*nu_A/sqrt(g^{BC}nu_B nu_C)"
        and theta_formula == "Theta=-gamma^{mn} n_R Q_mn^R"
    )
    return {
        "pass": all(row["pass"] for row in sides.values()) and completion_exact,
        "cofactor_formula": OPERATOR_SEMANTICS["embedding_cofactor"],
        "normal_formula": normal_formula,
        "Theta_formula": theta_formula,
        "semantic_completion_formulae_exact": completion_exact,
        "sides": sides,
    }


def _binder_schema_mutation(
    rows: list[dict[str, Any]],
    mutation: str | None,
    parsed: ParsedCharter,
) -> None:
    if mutation not in {
        "binder_wrong_dimension",
        "binder_wrong_namespace",
        "binder_GHY_H_uses_integration_domain",
        "xi_D2_slot_mistyped_as_acceleration",
        "binder_free_word",
        "binder_illegal_capture",
        "binder_not_alpha_normalized",
        "row_unknown_rehashed_opcode",
        "row_extra_rehashed_metadata",
        "fake_source_span_rehashed",
        "row_ordinal_999",
        "row_duplicate_ordinal",
        "row_plus_variation_to_minus",
        "row_plus_jet_to_minus",
        "row_GHY_outward_selector_to_M5",
        "row_evaluation_embedding_scaled_by_M5",
    }:
        return
    if mutation == "row_evaluation_embedding_scaled_by_M5":
        parameter_ast = coefficient_ast(parameter("M5"))

        def rewrite(node: dict[str, Any]) -> None:
            args = node.get("args", [])
            if type(args) is not list:
                return
            for arg in args:
                if type(arg) is dict:
                    rewrite(arg)
            if node.get("op") == "jet_evaluation" and len(args) == 3:
                embedding = args[2]
                node["args"][2] = {
                    "op": "mul",
                    "type": copy.deepcopy(embedding["type"]),
                    "args": [copy.deepcopy(parameter_ast), embedding],
                }

        for row in rows:
            rewrite(row["coefficient_ast"])
            row["coefficient_ast_sha256"] = _canonical_sha256(
                row["coefficient_ast"]
            )
        return
    if mutation == "row_GHY_outward_selector_to_M5":
        row = next(item for item in rows if item["component"] == "GHY_plus")
        selector = next(
            node
            for node in _row_walk(row["coefficient_ast"])
            if node.get("op") == "param" and node.get("symbol") == "s_out_plus"
        )
        selector["symbol"] = "M5"
        row["coefficient_ast_sha256"] = _canonical_sha256(row["coefficient_ast"])
        return
    if mutation == "fake_source_span_rehashed":
        row = rows[0]
        span = row["source_spans"][1]
        truncated = parsed.action[span["action_key"]][:-1]
        span["end"] = len(truncated)
        span["sha256"] = hashlib.sha256(truncated.encode("utf-8")).hexdigest()
        return
    if mutation == "row_ordinal_999":
        rows[0]["summand_ordinal"] = 999
        return
    if mutation == "row_duplicate_ordinal":
        rows[1]["summand_ordinal"] = rows[0]["summand_ordinal"]
        return
    if mutation == "row_plus_variation_to_minus":
        row = next(
            item
            for item in rows
            if item["component"] == "EH_bulk_plus"
            and item["variation_component"] == "H_plus"
            and item["derivative"]["word"] == []
        )
        row["variation_component"] = "H_minus"
        return
    if mutation == "row_plus_jet_to_minus":
        row = next(item for item in rows if item["component"] == "EH_bulk_plus")
        node = next(
            node
            for node in _row_walk(row["coefficient_ast"])
            if node.get("op") == "jet"
            and node.get("symbol") == "g_plus"
            and node.get("derivative", {}).get("word") == []
        )
        node["symbol"] = "g_minus"
        row["coefficient_ast_sha256"] = _canonical_sha256(row["coefficient_ast"])
        return
    if mutation in {"row_unknown_rehashed_opcode", "row_extra_rehashed_metadata"}:
        row = rows[0]
        if mutation == "row_unknown_rehashed_opcode":
            row["coefficient_ast"]["op"] = "unknown_rehashed_opcode"
        else:
            row["coefficient_ast"]["forged_metadata"] = "accepted_if_not_exhaustive"
        row["coefficient_ast_sha256"] = _canonical_sha256(row["coefficient_ast"])
        return
    row = next(item for item in rows if item["derivative"]["word"] == [0, 1])
    if mutation == "binder_GHY_H_uses_integration_domain":
        row = next(
            item
            for item in rows
            if item["component"] == "GHY_plus"
            and item["variation_component"] == "H_plus"
            and item["derivative"]["word"] == [0]
        )
        row["derivative"]["binders"][0].update(
            {"namespace": "Sigma.coordinate", "dimension": 4}
        )
        return
    if mutation == "xi_D2_slot_mistyped_as_acceleration":
        row = next(
            item
            for item in rows
            if item["variation_component"] == "xi_plus"
            and item["derivative"]["word"] == [0, 1]
        )
        slot = _linear_slots(row["coefficient_ast"])[0]
        slot["type"] = _compat_type(ACCELERATION5)
        row["coefficient_ast_sha256"] = _canonical_sha256(row["coefficient_ast"])
        return
    if mutation == "binder_wrong_dimension":
        row["derivative"]["binders"][0]["dimension"] = 4 if row["domain"] != "Sigma" else 5
    elif mutation == "binder_wrong_namespace":
        row["derivative"]["binders"][0]["namespace"] = "foreign.coordinate"
    elif mutation == "binder_free_word":
        row["derivative"]["word"] = [7, 1]
    elif mutation == "binder_illegal_capture":
        row["coefficient_ast"]["external_derivative_word"] = [0, 1]
        row["coefficient_ast_sha256"] = _canonical_sha256(row["coefficient_ast"])
    elif mutation == "binder_not_alpha_normalized":
        row["derivative"]["binders"][0]["alpha_normalized"] = False


def _binder_alpha_oracle(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    baseline = copy.deepcopy(next(row for row in rows if row["derivative"]["word"] == [0, 1]))
    renamed = copy.deepcopy(baseline)
    renamed["derivative"]["word"] = [7, 9]
    for identifier, binder in zip((7, 9), renamed["derivative"]["binders"], strict=True):
        binder["id"] = identifier
        binder["alpha_normalized"] = False
    slot = _linear_slots(renamed["coefficient_ast"])[0]
    slot["external_derivative_word"] = [7, 9]
    renamed["coefficient_ast_sha256"] = _canonical_sha256(renamed["coefficient_ast"])
    canonical = canonicalize_frechet_row_binders(renamed)
    return {
        "pass": canonical == baseline,
        "word_length": 2,
        "renamed_ids": [7, 9],
        "canonical_ids": [0, 1],
        "row_sha256": _canonical_sha256(baseline),
    }


def _scale_every_jet_evaluation_embedding(expr: Expr) -> Expr:
    """Correlated attack: change every evaluation point without changing its type."""

    args = tuple(_scale_every_jet_evaluation_embedding(arg) for arg in expr.args)
    if expr.op == "evaluate_jet":
        args = (args[0], args[1], scale(parameter("M5"), args[2]))
    return Expr(
        expr.op,
        expr.type_tag,
        args,
        expr.label,
        expr.value,
        expr.exponent,
        expr.derivative_word,
    )


def _multiply_inverse_tangents_by_dimension_trace(expr: Expr) -> Expr:
    """Correlated attack that is invisible when every probe is two-dimensional."""

    sandwich: Expr | None = None
    old_coefficient: Expr | None = None
    if (
        expr.op == "scale"
        and len(expr.args) == 2
        and expr.args[1].op == "multilinear"
        and expr.args[1].label in {
            "inverse_sandwich_5",
            "inverse_sandwich_5_at_Sigma",
            "inverse_sandwich_4",
        }
    ):
        old_coefficient, sandwich = expr.args
    elif expr.op == "multilinear" and expr.label in {
        "inverse_sandwich_5",
        "inverse_sandwich_5_at_Sigma",
        "inverse_sandwich_4",
    }:
        old_coefficient, sandwich = rational(1), expr
    if sandwich is not None and old_coefficient is not None:
        right_inverse = sandwich.args[2]
        if right_inverse.op != "inverse_metric" or len(right_inverse.args) != 1:
            raise GravityFrechetError(
                "dimension-factor mutant requires the explicit inverse operand"
            )
        identity_trace = multilinear(
            _metric_trace_label(right_inverse.type_tag),
            right_inverse,
            right_inverse.args[0],
        )
        factor = mul_scalar(rational(Fraction(1, 2)), identity_trace)
        return Expr(
            "scale",
            expr.type_tag,
            (mul_scalar(old_coefficient, factor), sandwich),
        )
    return Expr(
        expr.op,
        expr.type_tag,
        tuple(_multiply_inverse_tangents_by_dimension_trace(arg) for arg in expr.args),
        expr.label,
        expr.value,
        expr.exponent,
        expr.derivative_word,
    )


def _finite_alias_polynomial() -> Expr:
    """F(M5)=1+(M5-2)(M5-3), equal to one at the two finite witnesses."""

    return add(
        power(add(parameter("M5"), rational(Fraction(-5, 2))), 2),
        rational(Fraction(3, 4)),
    )


def _scale_first_inverse_operand_by_finite_alias(expr: Expr) -> Expr:
    if expr.op == "multilinear" and expr.label in {
        "inverse_sandwich_5",
        "inverse_sandwich_5_at_Sigma",
        "inverse_sandwich_4",
    }:
        left_inverse = expr.args[0]
        if left_inverse.op != "inverse_metric" or len(left_inverse.args) != 1:
            raise GravityFrechetError("finite-alias mutant requires explicit left inverse")
        changed_left = inverse_metric(
            scale(_finite_alias_polynomial(), left_inverse.args[0])
        )
        return Expr(
            expr.op,
            expr.type_tag,
            (changed_left, expr.args[1], expr.args[2]),
            expr.label,
            expr.value,
            expr.exponent,
            expr.derivative_word,
        )
    return Expr(
        expr.op,
        expr.type_tag,
        tuple(_scale_first_inverse_operand_by_finite_alias(arg) for arg in expr.args),
        expr.label,
        expr.value,
        expr.exponent,
        expr.derivative_word,
    )


def _strip_inverse_summand_outer_M5_cubed(
    expr: Expr, component: str, *, add_finite_alias: bool
) -> Expr:
    terms: list[Expr] = []
    for summand in _summands(expr):
        changed = summand
        if _expr_local_inverse_entries(summand):
            if summand.op != "scale" or len(summand.args) != 2:
                raise GravityFrechetError(
                    "lost-prefactor mutant requires an explicit outer scale"
                )
            residual = (
                rational(Fraction(1, 2))
                if component.startswith("EH_bulk_")
                else rational(1)
            )
            changed_body = (
                _scale_first_inverse_operand_by_finite_alias(summand.args[1])
                if add_finite_alias
                else summand.args[1]
            )
            changed = Expr("scale", summand.type_tag, (residual, changed_body))
        terms.append(changed)
    if len(terms) == 1:
        return terms[0]
    return Expr("add", expr.type_tag, tuple(terms))


def _derivative_certificate(program: Program, mutation: str | None) -> dict[str, Any]:
    forward_mutation = (
        mutation
        if mutation
        in {
            "wrong_inverse_sign",
            "wrong_volume_half",
            "correlated_wrong_inverse_sign",
            "correlated_wrong_volume_half",
            "correlated_inverse_operand_doubled",
            "correlated_inverse_operand_scaled_by_M5",
        }
        else None
    )
    reverse_mutation = (
        mutation
        if mutation
        in {
            "correlated_wrong_inverse_sign",
            "correlated_wrong_volume_half",
            "correlated_inverse_operand_doubled",
            "correlated_inverse_operand_scaled_by_M5",
        }
        else None
    )
    forward: dict[str, Expr] = {}
    reverse: dict[str, Expr] = {}
    comparison: dict[str, bool] = {}
    linear: dict[str, bool] = {}
    for name, primal in program.components.items():
        forward_expr = forward_nilpotent_dual(
            primal, program.tangents, mutation=forward_mutation
        ).tangent
        reverse_expr = reverse_context_frechet(
            primal, program.tangents, mutation=reverse_mutation
        )
        if mutation == "correlated_evaluation_embedding_scaled_by_M5":
            forward_expr = _scale_every_jet_evaluation_embedding(forward_expr)
            reverse_expr = _scale_every_jet_evaluation_embedding(reverse_expr)
        if mutation == "correlated_dimension_trace_identity_factor":
            forward_expr = _multiply_inverse_tangents_by_dimension_trace(
                forward_expr
            )
            reverse_expr = _multiply_inverse_tangents_by_dimension_trace(
                reverse_expr
            )
        if mutation in {
            "finite_alias_inverse_operand_lost_prefactor",
            "lost_inverse_summand_M5_cubed_prefactor",
        }:
            add_alias = mutation == "finite_alias_inverse_operand_lost_prefactor"
            forward_expr = _strip_inverse_summand_outer_M5_cubed(
                forward_expr, name, add_finite_alias=add_alias
            )
            reverse_expr = _strip_inverse_summand_outer_M5_cubed(
                reverse_expr, name, add_finite_alias=add_alias
            )
        forward[name] = forward_expr
        reverse[name] = reverse_expr
        comparison[name] = forward[name] == reverse[name]
        linear[name] = all(_variation_count(term) == 1 for term in _summands(forward[name]))
    if mutation == "integral_duplicate_minus_into_plus":
        for family in ("EH_bulk", "GHY"):
            plus = f"{family}_plus"
            minus = f"{family}_minus"
            forward[plus] = forward[minus]
            reverse[plus] = reverse[minus]
            comparison[plus] = forward[plus] == reverse[plus]
            linear[plus] = all(
                _variation_count(term) == 1
                for term in _summands(forward[plus])
            )
    derivative_hash = _canonical_sha256(
        {name: expr_row(expr) for name, expr in forward.items()}
    )
    rows = export_frechet_rows(program, forward)
    _binder_schema_mutation(rows, mutation, program.parsed)
    neutral_validation: list[bool] = []
    neutral_validation_errors: list[str] = []
    row_validation: list[bool] = []
    row_validation_errors: list[str] = []
    for row in rows:
        try:
            neutral_validation.append(validate_neutral_frechet_row(row))
        except GravityFrechetError as exc:
            neutral_validation.append(False)
            neutral_validation_errors.append(str(exc))
        try:
            row_validation.append(validate_frechet_row(row, program.parsed))
        except GravityFrechetError as exc:
            row_validation.append(False)
            row_validation_errors.append(str(exc))
    rows_hash = _canonical_sha256(rows)
    try:
        collection = frechet_row_collection_certificate(rows, program.parsed)
    except GravityFrechetError as exc:
        collection = {
            "pass": False,
            "error": str(exc),
            "expected_component_counts": dict(EXPECTED_COMPONENT_ROW_COUNTS),
            "source_spans_bound_to_parsed_action": False,
            "side_consistency_checked": False,
        }
    binder_oracle = (
        _binder_alpha_oracle(rows)
        if all(row_validation)
        else {"pass": False, "reason": "invalid row cannot enter alpha-renaming oracle"}
    )
    roles = sorted({row["role"] for row in rows})
    word_inventory = sorted(
        {
            tuple(row["derivative"]["word"])
            for row in rows
        }
    )
    return {
        "pass": (
            all(comparison.values())
            and all(linear.values())
            and all(neutral_validation)
            and all(row_validation)
            and collection["pass"]
            and binder_oracle["pass"]
        ),
        "raw_dual_equals_reverse_pass": (
            all(comparison.values()) and all(linear.values())
        ),
        "FrechetRowV1_schema_and_binder_pass": (
            all(neutral_validation)
            and all(row_validation)
            and collection["pass"]
            and binder_oracle["pass"]
        ),
        "FrechetRowV1_component_collection_pass": collection["pass"],
        "forward_equals_reverse_by_component": comparison,
        "every_summand_linear_in_one_tangent_jet": linear,
        "forward_derivatives": forward,
        "reverse_derivatives": reverse,
        "derivatives_sha256": derivative_hash,
        "FrechetRowV1_rows": rows,
        "FrechetRowV1_rows_sha256": rows_hash,
        "FrechetRowV1_collection_certificate": collection,
        "FrechetRowV1_validation": {
            "pass": all(row_validation),
            "validated_row_count": sum(row_validation),
            "errors": row_validation_errors,
        },
        "neutral_FrechetRowV1_validation": {
            "pass": all(neutral_validation),
            "validated_row_count": sum(neutral_validation),
            "errors": neutral_validation_errors,
            "component_whitelist_used": False,
            "binder_source": "variation_bundle_plus_ordered_word",
            "S10_validator_used": False,
            "S10_validator_interoperability_proved": False,
            "shared_density_metadata": {
                DENSITY5.name: _compat_type(DENSITY5),
                DENSITY4.name: _compat_type(DENSITY4),
            },
            "scope": (
                "neutral row mechanics for the four registered H/xi bundles; "
                "this does not claim that the component-restricted S10 validator consumes S11"
            ),
        },
        "binder_alpha_renaming_oracle": binder_oracle,
        "row_count": len(rows),
        "role_inventory": roles,
        "ordered_derivative_word_inventory": [list(word) for word in word_inventory],
        "comparison_mode": "exact canonical AST equality of two traversals over one primitive registry",
        "independent_coordinate_denotation_proved": False,
    }


def _permutation_sign(values: Sequence[int]) -> int:
    inversions = sum(
        values[i] > values[j]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return -1 if inversions % 2 else 1


_M5Polynomial = dict[int, Fraction]


def _M5_polynomial_add(
    left: _M5Polynomial, right: _M5Polynomial
) -> _M5Polynomial:
    result = dict(left)
    for degree, coefficient in right.items():
        result[degree] = result.get(degree, Fraction(0)) + coefficient
        if result[degree] == 0:
            del result[degree]
    return result


def _M5_polynomial_multiply(
    left: _M5Polynomial, right: _M5Polynomial
) -> _M5Polynomial:
    result: _M5Polynomial = {}
    for left_degree, left_coefficient in left.items():
        for right_degree, right_coefficient in right.items():
            degree = left_degree + right_degree
            result[degree] = (
                result.get(degree, Fraction(0))
                + left_coefficient * right_coefficient
            )
    return {degree: coefficient for degree, coefficient in result.items() if coefficient}


def _M5_polynomial_power(
    value: _M5Polynomial, exponent: int
) -> _M5Polynomial:
    if exponent < 0:
        raise GravityFrechetError("exterior M5 polynomial has a negative power")
    result: _M5Polynomial = {0: Fraction(1)}
    base = dict(value)
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = _M5_polynomial_multiply(result, base)
        base = _M5_polynomial_multiply(base, base)
        remaining //= 2
    return result


def _strict_exterior_M5_polynomial(expr: Expr) -> _M5Polynomial:
    """Decode only the closed Q[M5] scalar grammar, independently of AD."""

    if not _is_scalar(expr.type_tag) or expr.type_tag.base_dimension != 0:
        raise GravityFrechetError("exterior coupling is not a dimension-zero scalar")
    if expr.op == "rational":
        assert expr.value is not None
        return {0: expr.value}
    if expr.op == "parameter":
        if expr.label != "M5":
            raise GravityFrechetError("non-M5 parameter in exterior coupling")
        return {1: Fraction(1)}
    if expr.op == "add":
        result: _M5Polynomial = {}
        for arg in expr.args:
            result = _M5_polynomial_add(
                result, _strict_exterior_M5_polynomial(arg)
            )
        return result
    if expr.op == "mul_scalar":
        result = {0: Fraction(1)}
        for arg in expr.args:
            result = _M5_polynomial_multiply(
                result, _strict_exterior_M5_polynomial(arg)
            )
        return result
    if expr.op == "power":
        if (
            expr.exponent is None
            or expr.exponent.denominator != 1
            or expr.exponent < 0
        ):
            raise GravityFrechetError(
                "exterior M5 polynomial power is not a nonnegative integer"
            )
        return _M5_polynomial_power(
            _strict_exterior_M5_polynomial(expr.args[0]),
            expr.exponent.numerator,
        )
    raise GravityFrechetError(
        f"exterior M5 polynomial rejects scalar operation {expr.op}"
    )


def _M5_polynomial_normal_form(value: _M5Polynomial) -> tuple[Any, ...]:
    return tuple(
        (degree, (coefficient.numerator, coefficient.denominator))
        for degree, coefficient in sorted(value.items())
    )


def _literal_exterior_M5_polynomials(
    action: Mapping[str, str],
) -> dict[str, _M5Polynomial]:
    """Parse the byte-pinned v5.2 coupling literals without using Program."""

    bulk = action.get("bulk_gauged", "")
    bulk_matches = re.findall(r"M5\^(?P<power>[0-9]+)\*R_eps/(?P<den>[0-9]+)", bulk)
    ghy = re.fullmatch(
        r"S_GHY=M5\^(?P<power>[0-9]+)\*sum_eps int_Sigma sqrt\(-gamma\)\*Theta_eps for outward normals",
        action.get("GHY", ""),
    )
    if len(bulk_matches) != 1 or ghy is None:
        raise GravityFrechetError("independent literal M5 coupling parse failed")
    bulk_power, bulk_denominator = (int(value) for value in bulk_matches[0])
    ghy_power = int(ghy.group("power"))
    if (bulk_power, bulk_denominator, ghy_power) != (3, 2, 3):
        raise GravityFrechetError("independent literal is not EH M5^3/2 plus GHY M5^3")
    return {
        "EH_bulk_plus": {bulk_power: Fraction(1, bulk_denominator)},
        "GHY_plus": {ghy_power: Fraction(1)},
        "EH_bulk_minus": {bulk_power: Fraction(1, bulk_denominator)},
        "GHY_minus": {ghy_power: Fraction(1)},
    }


def _literal_exterior_M5_polynomial_oracle(
    program: Program,
) -> dict[str, Any]:
    """Compare every complete exterior scalar against literal Q[M5]."""

    expected = _literal_exterior_M5_polynomials(program.parsed.action)
    components: dict[str, Any] = {}
    passed = True
    for component_name in COMPONENTS:
        expected_polynomial = expected[component_name]
        records: list[dict[str, Any]] = []
        for ordinal, summand in enumerate(_summands(program.components[component_name])):
            coefficient: _M5Polynomial = {0: Fraction(1)}
            residual = summand
            error: str | None = None
            try:
                scale_depth = 0
                while residual.op == "scale" and len(residual.args) == 2:
                    coefficient = _M5_polynomial_multiply(
                        coefficient,
                        _strict_exterior_M5_polynomial(residual.args[0]),
                    )
                    residual = residual.args[1]
                    scale_depth += 1
                if scale_depth == 0:
                    raise GravityFrechetError("summand has no exterior scalar scale")
                if any(
                    node.op == "parameter" and node.label == "M5"
                    for node in walk(residual)
                ):
                    raise GravityFrechetError(
                        "M5 remains inside the residual instead of the complete exterior scalar"
                    )
            except GravityFrechetError as exc:
                error = str(exc)
            observed_normal_form = (
                _M5_polynomial_normal_form(coefficient) if error is None else None
            )
            expected_normal_form = _M5_polynomial_normal_form(expected_polynomial)
            row_pass = error is None and coefficient == expected_polynomial
            passed = passed and row_pass
            records.append(
                {
                    "component": component_name,
                    "summand_ordinal": ordinal,
                    "scale_depth": scale_depth if error is None else None,
                    "observed_Q_M5": observed_normal_form,
                    "expected_Q_M5": expected_normal_form,
                    "pass": row_pass,
                    "error": error,
                }
            )
        if not records:
            passed = False
        components[component_name] = {
            "pass": bool(records and all(row["pass"] for row in records)),
            "summand_count": len(records),
            "records": records,
        }
    return {
        "pass": bool(passed and set(components) == set(COMPONENTS)),
        "literal_parser": (
            "independent exact regex over byte-pinned v5.2 bulk_gauged and GHY strings"
        ),
        "comparison_ring": "Q[M5] with M5 an indeterminate",
        "expected_by_component": {
            component: _M5_polynomial_normal_form(polynomial)
            for component, polynomial in expected.items()
        },
        "components": components,
        "separation": "does not call Program builder, AD, row exporter, or symbolic replay",
    }


def _evaluate_exact_parameter_scalar(expr: Expr) -> Fraction:
    """Evaluate the coupling-only scalar fragment with M5=1 exactly."""

    if expr.op == "rational":
        assert expr.value is not None
        return expr.value
    if expr.op == "parameter":
        if expr.label != "M5":
            raise GravityFrechetError("small AST evaluator saw an unknown parameter")
        return Fraction(1)
    if expr.op == "mul_scalar":
        value = Fraction(1)
        for arg in expr.args:
            value *= _evaluate_exact_parameter_scalar(arg)
        return value
    if expr.op == "power":
        assert expr.exponent is not None
        base = _evaluate_exact_parameter_scalar(expr.args[0])
        if expr.exponent.denominator != 1:
            raise GravityFrechetError("small AST evaluator requires an integral power")
        return base ** expr.exponent.numerator
    raise GravityFrechetError(
        f"small AST evaluator cannot evaluate scalar operation {expr.op}"
    )


def _literal_prefactor_oracle(program: Program) -> dict[str, Any]:
    expected = {
        "EH_bulk_plus": Fraction(1, 2),
        "GHY_plus": Fraction(1),
        "EH_bulk_minus": Fraction(1, 2),
        "GHY_minus": Fraction(1),
    }
    observed: dict[str, Fraction | None] = {}
    for name, component in program.components.items():
        factors: list[Fraction] = []
        for summand in _summands(component):
            if summand.op != "scale" or len(summand.args) != 2:
                factors = []
                break
            factors.append(_evaluate_exact_parameter_scalar(summand.args[0]))
        if not factors or len(set(factors)) != 1:
            observed[name] = None
            continue
        observed[name] = factors[0]
    return {
        "pass": observed == expected,
        "evaluation": "exact rational interpretation of each action AST outer coupling with M5=1",
        "observed": observed,
        "expected": expected,
    }


def _covariant_acceleration_oracle(program: Program) -> dict[str, Any]:
    sides: dict[str, Any] = {}
    for side in ("plus", "minus"):
        q = program.side_geometry[side]["GHY_Q"]
        q_args = q.args if q.op == "covariant_acceleration" else ()
        second_jet = q_args[0] if len(q_args) == 2 else None
        connection = q_args[1] if len(q_args) == 2 else None
        passed = bool(
            second_jet is not None
            and second_jet.op == "field"
            and second_jet.label == f"Y2_{side}"
            and second_jet.type_tag == MAP2
            and connection is not None
            and connection.op == "multilinear"
            and connection.label == "connection_pullback_acceleration"
            and connection.type_tag == ACCELERATION5
            and q.type_tag == ACCELERATION5
        )
        sides[side] = {
            "pass": passed,
            "Q_ast_sha256": _canonical_sha256(expr_row(q)),
            "root_operation": q.op,
            "second_jet_type": second_jet.type_tag.name if second_jet else None,
            "connection_type": connection.type_tag.name if connection else None,
        }
    return {
        "pass": all(row["pass"] for row in sides.values()),
        "identity": "Q=covariant_acceleration(D2Y,Gamma(Y)(DY,DY))",
        "sides": sides,
    }


def _derivative_primitive_oracle(derivative: Mapping[str, Any]) -> dict[str, Any]:
    labels: set[str] = set()
    for expr in derivative["forward_derivatives"].values():
        for node in walk(expr):
            if node.op == "multilinear":
                labels.add(node.label)
            elif node.op == "covariant_acceleration":
                labels.add("covariant_acceleration")
    required = {
        "evaluate_metric_variation_0",
        "transport_metric_jet_0",
        "evaluate_metric_variation_1",
        "transport_metric_jet_1",
        "covariant_acceleration",
    }
    return {
        "pass": required <= labels,
        "required": sorted(required),
        "observed": sorted(labels),
        "scope": "operator inventory read from the generated forward derivative ASTs",
    }


def _fo_add(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return left[0] + right[0], left[1] + right[1]


def _fo_neg(value: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return -value[0], -value[1]


def _fo_mul(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return left[0] * right[0], left[1] * right[0] + left[0] * right[1]


def _fo_inverse(value: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    if value[0] == 0:
        raise GravityFrechetError("first-order rational inverse at zero")
    return Fraction(1, 1) / value[0], -value[1] / (value[0] * value[0])


def _independent_metric_family_oracle() -> dict[str, Any]:
    """Invert a 2x2 first-order matrix by adjugate/determinant, not AD rules."""

    g = (
        ((Fraction(-1), Fraction(1)), (Fraction(0), Fraction(2))),
        ((Fraction(0), Fraction(2)), (Fraction(1), Fraction(3))),
    )
    determinant = _fo_add(
        _fo_mul(g[0][0], g[1][1]),
        _fo_neg(_fo_mul(g[0][1], g[1][0])),
    )
    inverse_determinant = _fo_inverse(determinant)
    adjugate = (
        (g[1][1], _fo_neg(g[0][1])),
        (_fo_neg(g[1][0]), g[0][0]),
    )
    inverse = tuple(
        tuple(_fo_mul(adjugate[i][j], inverse_determinant) for j in range(2))
        for i in range(2)
    )
    minus_determinant = _fo_neg(determinant)
    if minus_determinant[0] != 1:
        raise GravityFrechetError("independent volume family lost its unit base")
    # Solve (s0+s1*t)^2=-det(g(t)) mod t^2 with the positive s0=1.
    sqrt_minus_determinant = (
        Fraction(1),
        minus_determinant[1] / 2,
    )
    return {
        "family": "g(t)=[[-1+t,2t],[2t,1+3t]] modulo t^2",
        "method": "exact Fraction adjugate/determinant inversion and coefficient matching of s(t)^2=-det(g(t))",
        "g_inverse_at_zero": tuple(tuple(entry[0] for entry in row) for row in inverse),
        "H": ((Fraction(1), Fraction(2)), (Fraction(2), Fraction(3))),
        "determinant_first_order": determinant,
        "inverse_derivative": tuple(tuple(entry[1] for entry in row) for row in inverse),
        "volume_derivative": sqrt_minus_determinant[1],
    }


_INVERSE_SANDWICH_CONVENTIONS = {
    "inverse_sandwich_5",
    "inverse_sandwich_5_at_Sigma",
    "inverse_sandwich_4",
}
_METRIC_TRACE_CONVENTIONS = {
    "metric_trace_5",
    "metric_trace_5_at_Sigma",
    "metric_trace_4",
}


def _expr_contains_metric_trace(expr: Expr) -> bool:
    return any(
        node.op == "multilinear" and node.label in _METRIC_TRACE_CONVENTIONS
        for node in walk(expr)
    )


def _row_walk(ast: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    yield ast
    args = ast.get("args", [])
    if type(args) is list:
        for arg in args:
            if type(arg) is dict:
                yield from _row_walk(arg)


def _row_contains_metric_trace(ast: Mapping[str, Any]) -> bool:
    return any(
        node.get("op") == "tensor_contract"
        and node.get("convention") in _METRIC_TRACE_CONVENTIONS
        for node in _row_walk(ast)
    )


def _expr_local_inverse_entries(
    expr: Expr,
) -> list[tuple[tuple[int, ...], Expr]]:
    roots: list[tuple[tuple[int, ...], Expr]] = []

    def visit(node: Expr, path: tuple[int, ...]) -> None:
        if (
            node.op == "scale"
            and len(node.args) == 2
            and node.args[1].op == "multilinear"
            and node.args[1].label in _INVERSE_SANDWICH_CONVENTIONS
        ):
            roots.append((path, node))
            visit(node.args[0], path + (0,))
            for index, arg in enumerate(node.args[1].args):
                visit(arg, path + (1, index))
            return
        if node.op == "multilinear" and node.label in _INVERSE_SANDWICH_CONVENTIONS:
            roots.append((path, node))
            for index, arg in enumerate(node.args):
                visit(arg, path + (index,))
            return
        for index, arg in enumerate(node.args):
            visit(arg, path + (index,))

    visit(expr, ())
    return roots


def _expr_local_inverse_roots(expr: Expr) -> list[Expr]:
    return [node for _, node in _expr_local_inverse_entries(expr)]


def _row_local_inverse_entries(
    ast: Mapping[str, Any],
) -> list[tuple[tuple[int, ...], Mapping[str, Any]]]:
    roots: list[tuple[tuple[int, ...], Mapping[str, Any]]] = []

    def is_inverse(node: Mapping[str, Any]) -> bool:
        return (
            node.get("op") == "tensor_contract"
            and node.get("convention") in _INVERSE_SANDWICH_CONVENTIONS
        )

    def visit(node: Mapping[str, Any], path: tuple[int, ...]) -> None:
        args = node.get("args", [])
        if type(args) is not list:
            return
        direct_inverse = [arg for arg in args if type(arg) is dict and is_inverse(arg)]
        if node.get("op") == "mul" and len(direct_inverse) == 1:
            roots.append((path, node))
            for index, arg in enumerate(args):
                if arg is direct_inverse[0]:
                    for nested_index, nested in enumerate(arg.get("args", [])):
                        visit(nested, path + (index, nested_index))
                else:
                    visit(arg, path + (index,))
            return
        if is_inverse(node):
            roots.append((path, node))
            for index, arg in enumerate(args):
                visit(arg, path + (index,))
            return
        for index, arg in enumerate(args):
            if type(arg) is dict:
                visit(arg, path + (index,))

    visit(ast, ())
    return roots


def _row_local_inverse_roots(ast: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [node for _, node in _row_local_inverse_entries(ast)]


def _expr_local_volume_entries(
    expr: Expr,
) -> list[tuple[tuple[int, ...], Expr]]:
    roots: list[tuple[tuple[int, ...], Expr]] = []

    def visit(node: Expr, path: tuple[int, ...]) -> None:
        if (
            node.op == "scale"
            and len(node.args) == 2
            and node.args[1].op == "volume_density"
            and _expr_contains_metric_trace(node.args[0])
        ):
            roots.append((path, node))
        for index, arg in enumerate(node.args):
            visit(arg, path + (index,))

    visit(expr, ())
    return roots


def _expr_local_volume_roots(expr: Expr) -> list[Expr]:
    return [node for _, node in _expr_local_volume_entries(expr)]


def _row_local_volume_entries(
    ast: Mapping[str, Any],
) -> list[tuple[tuple[int, ...], Mapping[str, Any]]]:
    roots: list[tuple[tuple[int, ...], Mapping[str, Any]]] = []

    def visit(node: Mapping[str, Any], path: tuple[int, ...]) -> None:
        args = node.get("args", [])
        if (
            node.get("op") == "mul"
            and type(args) is list
            and len(args) == 2
            and sum(arg.get("op") == "volume_density" for arg in args) == 1
        ):
            coefficient = next(arg for arg in args if arg.get("op") != "volume_density")
            if _row_contains_metric_trace(coefficient):
                roots.append((path, node))
        if type(args) is list:
            for index, arg in enumerate(args):
                if type(arg) is dict:
                    visit(arg, path + (index,))

    visit(ast, ())
    return roots


def _row_local_volume_roots(ast: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [node for _, node in _row_local_volume_entries(ast)]


def _matrix_scale(
    coefficient: Fraction,
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(coefficient * entry for entry in row) for row in matrix)


def _matrix_multiply(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        )
        for i in range(len(left))
    )


_PROBE_METRIC_TYPES = {METRIC5, PULLED_METRIC5, METRIC4}
_PROBE_INVERSE_TYPES = {INVERSE5, PULLED_INVERSE5, INVERSE4}


@dataclass(frozen=True)
class LocalDenotationWitness:
    name: str
    parameters: Mapping[str, Fraction]
    metric: tuple[tuple[Fraction, ...], ...]
    metric_first: tuple[tuple[tuple[Fraction, ...], ...], ...]
    metric_variation: tuple[tuple[Fraction, ...], ...]
    embedding: tuple[Fraction, ...]
    embedding_variation: tuple[Fraction, ...]
    embedding_first: tuple[tuple[Fraction, ...], ...]
    embedding_first_variation: tuple[tuple[Fraction, ...], ...]


def _diagonal_matrix(values: Sequence[Fraction | int]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(Fraction(value) if i == j else Fraction(0) for j in range(len(values)))
        for i, value in enumerate(values)
    )


def _local_denotation_witnesses() -> tuple[LocalDenotationWitness, ...]:
    embedding_first = tuple(
        tuple(Fraction(1 if ambient == boundary else 0) for boundary in range(4))
        for ambient in range(5)
    )
    data = (
        {
            "name": "five_four_witness_A",
            "M5": Fraction(2),
            "s_out_plus": Fraction(1),
            "s_out_minus": Fraction(-1),
            "metric": _diagonal_matrix((-1, 1, 1, 1, 1)),
            "jet_scale": Fraction(1),
            "metric_variation": (
                (Fraction(1), Fraction(1, 2), Fraction(0), Fraction(0), Fraction(0)),
                (Fraction(1, 2), Fraction(2), Fraction(1, 3), Fraction(0), Fraction(0)),
                (Fraction(0), Fraction(1, 3), Fraction(3), Fraction(0), Fraction(0)),
                (Fraction(0), Fraction(0), Fraction(0), Fraction(4), Fraction(1, 5)),
                (Fraction(0), Fraction(0), Fraction(0), Fraction(1, 5), Fraction(5)),
            ),
            "embedding": (Fraction(1), Fraction(1, 2), Fraction(-1, 3), Fraction(2, 5), Fraction(3, 7)),
            "embedding_variation": (Fraction(2), Fraction(-1), Fraction(1, 2), Fraction(1, 3), Fraction(-2, 3)),
            "embedding_first_variation": tuple(
                tuple(
                    Fraction((ambient + 1) * (boundary + 2), 11)
                    if ambient == boundary
                    else Fraction(((-1) ** (ambient + boundary)), 17)
                    for boundary in range(4)
                )
                for ambient in range(5)
            ),
        },
        {
            "name": "five_four_witness_B",
            "M5": Fraction(3),
            "s_out_plus": Fraction(-1),
            "s_out_minus": Fraction(1),
            "metric": _diagonal_matrix((-4, 1, 1, 1, 1)),
            "jet_scale": Fraction(1, 2),
            "metric_variation": (
                (Fraction(3), Fraction(-1, 3), Fraction(0), Fraction(0), Fraction(0)),
                (Fraction(-1, 3), Fraction(1), Fraction(1, 4), Fraction(0), Fraction(0)),
                (Fraction(0), Fraction(1, 4), Fraction(2), Fraction(-1, 5), Fraction(0)),
                (Fraction(0), Fraction(0), Fraction(-1, 5), Fraction(5), Fraction(1, 6)),
                (Fraction(0), Fraction(0), Fraction(0), Fraction(1, 6), Fraction(7)),
            ),
            "embedding": (Fraction(2), Fraction(-2, 3), Fraction(3, 5), Fraction(1, 7), Fraction(-1, 2)),
            "embedding_variation": (Fraction(-1), Fraction(2), Fraction(-3, 2), Fraction(4, 3), Fraction(1, 5)),
            "embedding_first_variation": tuple(
                tuple(
                    Fraction(((-1) ** (ambient + boundary)) * (ambient + boundary + 2), 13)
                    for boundary in range(4)
                )
                for ambient in range(5)
            ),
        },
    )
    witnesses: list[LocalDenotationWitness] = []
    for row in data:
        metric = row["metric"]
        metric_first = tuple(
            _matrix_scale(row["jet_scale"] if coordinate == 0 else Fraction(0), metric)
            for coordinate in range(5)
        )
        witnesses.append(
            LocalDenotationWitness(
                name=str(row["name"]),
                parameters={
                    "M5": row["M5"],
                    "s_out_plus": row["s_out_plus"],
                    "s_out_minus": row["s_out_minus"],
                },
                metric=metric,
                metric_first=metric_first,
                metric_variation=row["metric_variation"],
                embedding=row["embedding"],
                embedding_variation=row["embedding_variation"],
                embedding_first=embedding_first,
                embedding_first_variation=row["embedding_first_variation"],
            )
        )
    return tuple(witnesses)


def _matrix_add_exact(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right, strict=True)):
        raise GravityFrechetError("local matrix addition shape drift")
    return tuple(
        tuple(a + b for a, b in zip(left_row, right_row, strict=True))
        for left_row, right_row in zip(left, right, strict=True)
    )


def _matrix_inverse_exact(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    size = len(matrix)
    if size not in {4, 5} or any(len(row) != size for row in matrix):
        raise GravityFrechetError("local inverse evaluator requires a declared 4x4 or 5x5 matrix")
    augmented = [
        [Fraction(value) for value in row]
        + [Fraction(1 if i == j else 0) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column] != 0),
            None,
        )
        if pivot is None:
            raise GravityFrechetError("local inverse evaluator saw a singular operand")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * reference
                for value, reference in zip(
                    augmented[row], augmented[column], strict=True
                )
            ]
    return tuple(tuple(row[size:]) for row in augmented)


def _matrix_determinant_exact(
    matrix: Sequence[Sequence[Fraction]],
) -> Fraction:
    size = len(matrix)
    if size not in {4, 5} or any(len(row) != size for row in matrix):
        raise GravityFrechetError("local determinant evaluator requires dimension four or five")
    rows = [[Fraction(value) for value in row] for row in matrix]
    determinant = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if rows[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            determinant = -determinant
        pivot_value = rows[column][column]
        determinant *= pivot_value
        for row in range(column + 1, size):
            factor = rows[row][column] / pivot_value
            for inner in range(column + 1, size):
                rows[row][inner] -= factor * rows[column][inner]
    return determinant


def _matrix_volume_exact(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    minus_determinant = -_matrix_determinant_exact(matrix)
    if minus_determinant <= 0:
        raise GravityFrechetError("local volume evaluator requires Lorentzian sign")
    numerator = math.isqrt(minus_determinant.numerator)
    denominator = math.isqrt(minus_determinant.denominator)
    if (
        numerator * numerator != minus_determinant.numerator
        or denominator * denominator != minus_determinant.denominator
    ):
        raise GravityFrechetError("local volume evaluator requires an exact rational root")
    return Fraction(numerator, denominator)


def _matrix_contract_first_jet(
    metric_first: Sequence[Sequence[Sequence[Fraction]]],
    vector: Sequence[Fraction],
) -> tuple[tuple[Fraction, ...], ...]:
    if len(metric_first) != 5 or len(vector) != 5:
        raise GravityFrechetError("metric first-jet contraction dimension drift")
    result = _matrix_scale(Fraction(0), metric_first[0])
    for coefficient, matrix in zip(vector, metric_first, strict=True):
        result = _matrix_add_exact(result, _matrix_scale(coefficient, matrix))
    return result


def _pullback_matrix_exact(
    metric: Sequence[Sequence[Fraction]],
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    if len(metric) != 5 or len(left) != 5 or len(right) != 5:
        raise GravityFrechetError("pullback ambient dimension drift")
    if any(len(row) != 4 for row in left) or any(len(row) != 4 for row in right):
        raise GravityFrechetError("pullback boundary dimension drift")
    return tuple(
        tuple(
            sum(
                left[ambient][mu] * metric[ambient][other] * right[other][nu]
                for ambient in range(5)
                for other in range(5)
            )
            for nu in range(4)
        )
        for mu in range(4)
    )


def _expr_probe_embedding(
    expr: Expr, witness: LocalDenotationWitness
) -> tuple[Fraction, ...]:
    if expr.op == "field" and expr.type_tag == MAP5:
        return witness.embedding
    if expr.op in {"variation", "linear_slot"} and expr.type_tag == MAP5:
        return witness.embedding_variation
    if expr.op == "zero" and expr.type_tag == MAP5:
        return tuple(Fraction(0) for _ in range(5))
    if expr.op == "add":
        values = [_expr_probe_embedding(arg, witness) for arg in expr.args]
        return tuple(sum(items, Fraction(0)) for items in zip(*values, strict=True))
    if expr.op == "scale":
        coefficient = _expr_probe_scalar(expr.args[0], witness)
        return tuple(
            coefficient * value
            for value in _expr_probe_embedding(expr.args[1], witness)
        )
    raise GravityFrechetError(f"local embedding evaluator rejects {expr.op}:{expr.label}")


def _row_probe_embedding(
    ast: Mapping[str, Any], witness: LocalDenotationWitness
) -> tuple[Fraction, ...]:
    operation = ast.get("op")
    result_type = _compat_ast_type(ast)
    args = ast.get("args", [])
    if operation == "jet" and result_type == MAP5:
        return witness.embedding
    if operation == "linear_slot" and result_type == MAP5:
        return witness.embedding_variation
    if operation == "const" and result_type == MAP5 and ast.get("value") == [0, 1]:
        return tuple(Fraction(0) for _ in range(5))
    if operation == "add":
        values = [_row_probe_embedding(arg, witness) for arg in args]
        return tuple(sum(items, Fraction(0)) for items in zip(*values, strict=True))
    if operation == "mul":
        vector_args = [arg for arg in args if _compat_ast_type(arg) == MAP5]
        scalar_args = [arg for arg in args if _is_scalar(_compat_ast_type(arg))]
        if len(vector_args) != 1 or len(vector_args) + len(scalar_args) != len(args):
            raise GravityFrechetError("local row embedding scale signature drift")
        coefficient = Fraction(1)
        for arg in scalar_args:
            coefficient *= _row_probe_scalar(arg, witness)
        return tuple(
            coefficient * value
            for value in _row_probe_embedding(vector_args[0], witness)
        )
    raise GravityFrechetError(f"local row embedding evaluator rejects {operation}")


def _expr_probe_embedding_first(
    expr: Expr, witness: LocalDenotationWitness
) -> tuple[tuple[Fraction, ...], ...]:
    if expr.op == "field" and expr.type_tag == MAP1:
        return witness.embedding_first
    if expr.op in {"variation", "linear_slot"} and expr.type_tag == MAP1:
        return witness.embedding_first_variation
    if expr.op == "zero" and expr.type_tag == MAP1:
        return tuple(tuple(Fraction(0) for _ in range(4)) for _ in range(5))
    if expr.op == "add":
        values = [_expr_probe_embedding_first(arg, witness) for arg in expr.args]
        result = values[0]
        for value in values[1:]:
            result = _matrix_add_exact(result, value)
        return result
    if expr.op == "scale":
        return _matrix_scale(
            _expr_probe_scalar(expr.args[0], witness),
            _expr_probe_embedding_first(expr.args[1], witness),
        )
    raise GravityFrechetError(f"local embedding-jet evaluator rejects {expr.op}:{expr.label}")


def _row_probe_embedding_first(
    ast: Mapping[str, Any], witness: LocalDenotationWitness
) -> tuple[tuple[Fraction, ...], ...]:
    operation = ast.get("op")
    result_type = _compat_ast_type(ast)
    args = ast.get("args", [])
    if operation == "jet" and result_type == MAP1:
        return witness.embedding_first
    if operation == "linear_slot" and result_type == MAP1:
        return witness.embedding_first_variation
    if operation == "const" and result_type == MAP1 and ast.get("value") == [0, 1]:
        return tuple(tuple(Fraction(0) for _ in range(4)) for _ in range(5))
    if operation == "add":
        values = [_row_probe_embedding_first(arg, witness) for arg in args]
        result = values[0]
        for value in values[1:]:
            result = _matrix_add_exact(result, value)
        return result
    if operation == "mul":
        matrix_args = [arg for arg in args if _compat_ast_type(arg) == MAP1]
        scalar_args = [arg for arg in args if _is_scalar(_compat_ast_type(arg))]
        if len(matrix_args) != 1 or len(matrix_args) + len(scalar_args) != len(args):
            raise GravityFrechetError("local row embedding-jet scale signature drift")
        coefficient = Fraction(1)
        for arg in scalar_args:
            coefficient *= _row_probe_scalar(arg, witness)
        return _matrix_scale(
            coefficient, _row_probe_embedding_first(matrix_args[0], witness)
        )
    raise GravityFrechetError(f"local row embedding-jet evaluator rejects {operation}")


def _expr_probe_metric_first(
    expr: Expr, witness: LocalDenotationWitness
) -> tuple[tuple[tuple[Fraction, ...], ...], ...]:
    if expr.op == "field" and expr.type_tag == METRIC1JET5:
        return witness.metric_first
    if expr.op == "zero" and expr.type_tag == METRIC1JET5:
        zero_matrix = _matrix_scale(Fraction(0), witness.metric)
        return tuple(zero_matrix for _ in range(5))
    raise GravityFrechetError(f"local metric-jet evaluator rejects {expr.op}:{expr.label}")


def _row_probe_metric_first(
    ast: Mapping[str, Any], witness: LocalDenotationWitness
) -> tuple[tuple[tuple[Fraction, ...], ...], ...]:
    if ast.get("op") == "jet" and _compat_ast_type(ast) == METRIC1JET5:
        return witness.metric_first
    if ast.get("op") == "const" and _compat_ast_type(ast) == METRIC1JET5 and ast.get("value") == [0, 1]:
        zero_matrix = _matrix_scale(Fraction(0), witness.metric)
        return tuple(zero_matrix for _ in range(5))
    raise GravityFrechetError(f"local row metric-jet evaluator rejects {ast.get('op')}")


def _expr_probe_matrix(
    expr: Expr, witness: LocalDenotationWitness
) -> tuple[tuple[Fraction, ...], ...]:
    """Evaluate every operand of the local inverse/trace witness recursively."""

    if expr.op == "field" and expr.type_tag == METRIC5:
        return witness.metric
    if expr.op in {"variation", "linear_slot"} and expr.type_tag == METRIC5:
        return witness.metric_variation
    if expr.op == "zero" and expr.type_tag in _PROBE_METRIC_TYPES | _PROBE_INVERSE_TYPES:
        dimension = 4 if expr.type_tag in {METRIC4, INVERSE4} else 5
        return tuple(tuple(Fraction(0) for _ in range(dimension)) for _ in range(dimension))
    if expr.op == "add":
        values = [_expr_probe_matrix(arg, witness) for arg in expr.args]
        if not values:
            raise GravityFrechetError("local matrix evaluator saw empty addition")
        result = values[0]
        for value in values[1:]:
            result = _matrix_add_exact(result, value)
        return result
    if expr.op == "scale":
        return _matrix_scale(
            _expr_probe_scalar(expr.args[0], witness),
            _expr_probe_matrix(expr.args[1], witness),
        )
    if expr.op == "inverse_metric":
        return _matrix_inverse_exact(_expr_probe_matrix(expr.args[0], witness))
    if expr.op == "evaluate_jet" and expr.type_tag == PULLED_METRIC5:
        base = _expr_probe_matrix(expr.args[0], witness)
        first = _expr_probe_metric_first(expr.args[1], witness)
        point = _expr_probe_embedding(expr.args[2], witness)
        return _matrix_add_exact(base, _matrix_contract_first_jet(first, point))
    if expr.op == "multilinear":
        if expr.label in _INVERSE_SANDWICH_CONVENTIONS:
            return _matrix_multiply(
                _matrix_multiply(
                    _expr_probe_matrix(expr.args[0], witness),
                    _expr_probe_matrix(expr.args[1], witness),
                ),
                _expr_probe_matrix(expr.args[2], witness),
            )
        if expr.label == "evaluate_metric_variation_0":
            _expr_probe_embedding(expr.args[1], witness)
            return _expr_probe_matrix(expr.args[0], witness)
        if expr.label == "transport_metric_jet_0":
            first = _expr_probe_metric_first(expr.args[0], witness)
            _expr_probe_embedding(expr.args[1], witness)
            direction = _expr_probe_embedding(expr.args[2], witness)
            return _matrix_contract_first_jet(first, direction)
        if expr.label == "pullback_metric":
            return _pullback_matrix_exact(
                _expr_probe_matrix(expr.args[0], witness),
                _expr_probe_embedding_first(expr.args[1], witness),
                _expr_probe_embedding_first(expr.args[2], witness),
            )
    raise GravityFrechetError(
        f"local exact matrix evaluator rejects {expr.op}:{expr.label}"
    )


def _row_probe_matrix(
    ast: Mapping[str, Any], witness: LocalDenotationWitness
) -> tuple[tuple[Fraction, ...], ...]:
    operation = ast.get("op")
    result_type = _compat_ast_type(ast)
    args = ast.get("args", [])
    if operation == "jet" and result_type == METRIC5:
        return witness.metric
    if operation == "linear_slot" and result_type == METRIC5:
        return witness.metric_variation
    if operation == "const" and result_type in _PROBE_METRIC_TYPES | _PROBE_INVERSE_TYPES:
        value = ast.get("value")
        if value != [0, 1]:
            raise GravityFrechetError("local matrix evaluator saw a nonzero tensor constant")
        dimension = 4 if result_type in {METRIC4, INVERSE4} else 5
        return tuple(tuple(Fraction(0) for _ in range(dimension)) for _ in range(dimension))
    if operation == "add":
        values = [_row_probe_matrix(arg, witness) for arg in args]
        if not values:
            raise GravityFrechetError("local row matrix evaluator saw empty addition")
        result = values[0]
        for value in values[1:]:
            result = _matrix_add_exact(result, value)
        return result
    if operation == "mul":
        matrix_args = [arg for arg in args if _compat_ast_type(arg) in _PROBE_METRIC_TYPES | _PROBE_INVERSE_TYPES]
        scalar_args = [arg for arg in args if _is_scalar(_compat_ast_type(arg))]
        if len(matrix_args) != 1 or len(matrix_args) + len(scalar_args) != len(args):
            raise GravityFrechetError("local row matrix scale signature drift")
        coefficient = Fraction(1)
        for arg in scalar_args:
            coefficient *= _row_probe_scalar(arg, witness)
        return _matrix_scale(coefficient, _row_probe_matrix(matrix_args[0], witness))
    if operation == "inverse_metric":
        return _matrix_inverse_exact(_row_probe_matrix(args[0], witness))
    if operation == "jet_evaluation" and result_type == PULLED_METRIC5:
        base = _row_probe_matrix(args[0], witness)
        first = _row_probe_metric_first(args[1], witness)
        point = _row_probe_embedding(args[2], witness)
        return _matrix_add_exact(base, _matrix_contract_first_jet(first, point))
    if operation == "tensor_contract":
        convention = ast.get("convention")
        if convention in _INVERSE_SANDWICH_CONVENTIONS:
            return _matrix_multiply(
                _matrix_multiply(
                    _row_probe_matrix(args[0], witness),
                    _row_probe_matrix(args[1], witness),
                ),
                _row_probe_matrix(args[2], witness),
            )
        if convention == "evaluate_metric_variation_0":
            _row_probe_embedding(args[1], witness)
            return _row_probe_matrix(args[0], witness)
        if convention == "transport_metric_jet_0":
            first = _row_probe_metric_first(args[0], witness)
            _row_probe_embedding(args[1], witness)
            direction = _row_probe_embedding(args[2], witness)
            return _matrix_contract_first_jet(first, direction)
        if convention == "pullback_metric":
            return _pullback_matrix_exact(
                _row_probe_matrix(args[0], witness),
                _row_probe_embedding_first(args[1], witness),
                _row_probe_embedding_first(args[2], witness),
            )
    raise GravityFrechetError(
        f"local exact row matrix evaluator rejects {operation}:{ast.get('convention', '')}"
    )


def _expr_probe_scalar(expr: Expr, witness: LocalDenotationWitness) -> Fraction:
    if expr.op == "rational":
        assert expr.value is not None
        return expr.value
    if expr.op == "parameter":
        if expr.label not in {"M5", "s_out_plus", "s_out_minus"}:
            raise GravityFrechetError("local scalar evaluator saw an unknown parameter")
        return witness.parameters[expr.label]
    if expr.op == "zero":
        return Fraction(0)
    if expr.op == "add":
        return sum((_expr_probe_scalar(arg, witness) for arg in expr.args), Fraction(0))
    if expr.op == "mul_scalar":
        value = Fraction(1)
        for arg in expr.args:
            value *= _expr_probe_scalar(arg, witness)
        return value
    if expr.op == "power":
        assert expr.exponent is not None
        if expr.exponent.denominator != 1:
            raise GravityFrechetError("local scalar evaluator requires an integral power")
        return _expr_probe_scalar(expr.args[0], witness) ** expr.exponent.numerator
    if expr.op == "multilinear" and expr.label in _METRIC_TRACE_CONVENTIONS:
        inverse = _expr_probe_matrix(expr.args[0], witness)
        metric_variation = _expr_probe_matrix(expr.args[1], witness)
        dimension = len(inverse)
        return sum(
            inverse[i][j] * metric_variation[j][i]
            for i in range(dimension)
            for j in range(dimension)
        )
    raise GravityFrechetError(f"local exact evaluator rejects scalar op {expr.op}")


def _row_probe_scalar(ast: Mapping[str, Any], witness: LocalDenotationWitness) -> Fraction:
    operation = ast.get("op")
    if operation == "const":
        value = ast.get("value")
        if type(value) is not list or len(value) != 2:
            raise GravityFrechetError("local row evaluator saw malformed rational")
        return Fraction(value[0], value[1])
    if operation == "param":
        if ast.get("symbol") not in {"M5", "s_out_plus", "s_out_minus"}:
            raise GravityFrechetError("local row evaluator saw an unknown parameter")
        return witness.parameters[str(ast.get("symbol"))]
    if operation == "add":
        return sum((_row_probe_scalar(arg, witness) for arg in ast.get("args", [])), Fraction(0))
    if operation == "mul":
        value = Fraction(1)
        for arg in ast.get("args", []):
            value *= _row_probe_scalar(arg, witness)
        return value
    if operation == "pow":
        exponent = ast.get("exponent")
        if type(exponent) is not list or len(exponent) != 2 or exponent[1] != 1:
            raise GravityFrechetError("local row scalar evaluator requires an integral power")
        return _row_probe_scalar(ast["args"][0], witness) ** exponent[0]
    if operation == "tensor_contract" and ast.get("convention") in _METRIC_TRACE_CONVENTIONS:
        inverse = _row_probe_matrix(ast["args"][0], witness)
        metric_variation = _row_probe_matrix(ast["args"][1], witness)
        dimension = len(inverse)
        return sum(
            inverse[i][j] * metric_variation[j][i]
            for i in range(dimension)
            for j in range(dimension)
        )
    raise GravityFrechetError(f"local exact row evaluator rejects scalar op {operation}")


def _expr_probe_inverse(
    root: Expr, witness: LocalDenotationWitness
) -> tuple[tuple[Fraction, ...], ...]:
    return _expr_probe_matrix(root, witness)


def _row_probe_inverse(
    root: Mapping[str, Any], witness: LocalDenotationWitness
) -> tuple[tuple[Fraction, ...], ...]:
    return _row_probe_matrix(root, witness)


def _expr_probe_volume(root: Expr, witness: LocalDenotationWitness) -> Fraction:
    if root.op != "scale" or len(root.args) != 2 or root.args[1].op != "volume_density":
        raise GravityFrechetError("local volume evaluator did not receive coefficient times volume")
    return _expr_probe_scalar(root.args[0], witness) * _matrix_volume_exact(
        _expr_probe_matrix(root.args[1].args[0], witness)
    )


def _row_probe_volume(
    root: Mapping[str, Any], witness: LocalDenotationWitness
) -> Fraction:
    if root.get("op") != "mul" or type(root.get("args")) is not list:
        raise GravityFrechetError("local row volume evaluator did not receive a product")
    volume_args = [arg for arg in root["args"] if arg.get("op") == "volume_density"]
    if len(volume_args) != 1:
        raise GravityFrechetError("local row volume evaluator saw ambiguous volume")
    coefficient_args = [arg for arg in root["args"] if arg is not volume_args[0]]
    if len(coefficient_args) != 1:
        raise GravityFrechetError("local row volume evaluator saw ambiguous coefficient")
    return _row_probe_scalar(coefficient_args[0], witness) * _matrix_volume_exact(
        _row_probe_matrix(volume_args[0]["args"][0], witness)
    )


def _probe_capture(
    evaluator: Any, value: Any, witness: LocalDenotationWitness
) -> dict[str, Any]:
    """Turn malformed attacked operands into a reportable fail-closed record."""

    try:
        return {"value": evaluator(value, witness), "evaluation_error": None}
    except (GravityFrechetError, KeyError, IndexError, TypeError, ValueError) as exc:
        return {"value": None, "evaluation_error": str(exc)}


_EXPECTED_LOCAL_COVERAGE_BY_FAMILY = {
    "EH": (
        ("volume", 0, (1, 0)),
        ("volume", 1, (1, 0)),
        ("volume", 2, (1, 0)),
        ("inverse", 5, (1, 1, 1, 0, 1)),
        ("inverse", 9, (1, 1, 1, 1, 0)),
        ("inverse", 10, (1, 1, 1, 0, 0)),
        ("inverse", 11, (1, 1, 1, 0, 0)),
        ("inverse", 12, (1, 1, 1, 0, 0)),
        ("inverse", 13, (1, 1, 0)),
        ("inverse", 14, (1, 1, 0)),
        ("inverse", 15, (1, 1, 0)),
    ),
    "GHY": (
        ("volume", 0, (1, 0)),
        ("volume", 1, (1, 0)),
        ("volume", 2, (1, 0)),
        ("volume", 3, (1, 0)),
        ("inverse", 12, (1, 1, 0, 2, 0, 0)),
        ("inverse", 13, (1, 1, 0, 2, 0, 0)),
        ("inverse", 23, (1, 1, 0, 1, 0, 2, 0)),
        ("inverse", 24, (1, 1, 0, 1, 0, 2, 0)),
        ("inverse", 25, (1, 1, 0, 0)),
        ("inverse", 26, (1, 1, 0, 0)),
        ("inverse", 27, (1, 1, 0, 0)),
        ("inverse", 28, (1, 1, 0, 0)),
    ),
}


def _expected_local_coverage(component: str) -> tuple[tuple[str, int, tuple[int, ...]], ...]:
    family = "EH" if component.startswith("EH_") else "GHY"
    return _EXPECTED_LOCAL_COVERAGE_BY_FAMILY[family]


def _independent_local_base_and_tangent(
    component: str,
    kind: str,
    ordinal: int,
    witness: LocalDenotationWitness,
) -> tuple[tuple[tuple[Fraction, ...], ...], tuple[tuple[Fraction, ...], ...]]:
    """Canonical geometry for a local node, independent of either AD AST."""

    if component.startswith("EH_bulk_"):
        if kind not in {"inverse", "volume"}:
            raise GravityFrechetError("unknown EH local witness kind")
        return witness.metric, witness.metric_variation

    pulled_metric = _matrix_add_exact(
        witness.metric,
        _matrix_contract_first_jet(witness.metric_first, witness.embedding),
    )
    transported_metric = _matrix_contract_first_jet(
        witness.metric_first, witness.embedding_variation
    )
    induced_metric = _pullback_matrix_exact(
        pulled_metric, witness.embedding_first, witness.embedding_first
    )
    pulled_h = _pullback_matrix_exact(
        witness.metric_variation,
        witness.embedding_first,
        witness.embedding_first,
    )
    pulled_transport = _pullback_matrix_exact(
        transported_metric,
        witness.embedding_first,
        witness.embedding_first,
    )
    pulled_xi_left = _pullback_matrix_exact(
        pulled_metric,
        witness.embedding_first_variation,
        witness.embedding_first,
    )
    pulled_xi_right = _pullback_matrix_exact(
        pulled_metric,
        witness.embedding_first,
        witness.embedding_first_variation,
    )
    if kind == "volume":
        tangent_by_ordinal = {
            0: pulled_h,
            1: pulled_transport,
            2: pulled_xi_left,
            3: pulled_xi_right,
        }
        try:
            return induced_metric, tangent_by_ordinal[ordinal]
        except KeyError as exc:
            raise GravityFrechetError("unknown GHY volume witness ordinal") from exc
    if kind == "inverse":
        if ordinal in {12, 23}:
            return pulled_metric, witness.metric_variation
        if ordinal in {13, 24}:
            return pulled_metric, transported_metric
        tangent_by_ordinal = {
            25: pulled_h,
            26: pulled_transport,
            27: pulled_xi_left,
            28: pulled_xi_right,
        }
        try:
            return induced_metric, tangent_by_ordinal[ordinal]
        except KeyError as exc:
            raise GravityFrechetError("unknown GHY inverse witness ordinal") from exc
    raise GravityFrechetError("unknown local witness kind")


def _independent_local_expected_value(
    component: str,
    kind: str,
    ordinal: int,
    witness: LocalDenotationWitness,
) -> tuple[tuple[Fraction, ...], ...] | Fraction:
    base, tangent = _independent_local_base_and_tangent(
        component, kind, ordinal, witness
    )
    inverse = _matrix_inverse_exact(base)
    if kind == "inverse":
        return _matrix_scale(
            Fraction(-1), _matrix_multiply(_matrix_multiply(inverse, tangent), inverse)
        )
    trace_value = sum(
        inverse[i][j] * tangent[j][i]
        for i in range(len(inverse))
        for j in range(len(inverse))
    )
    return Fraction(1, 2) * trace_value * _matrix_volume_exact(base)


def _probe_all_witnesses(
    evaluator: Any,
    root: Any,
    witnesses: Sequence[LocalDenotationWitness],
) -> dict[str, Any]:
    values: dict[str, Any] = {}
    errors: dict[str, str] = {}
    for witness in witnesses:
        result = _probe_capture(evaluator, root, witness)
        values[witness.name] = result["value"]
        if result["evaluation_error"] is not None:
            errors[witness.name] = result["evaluation_error"]
    return {
        "value_by_witness": values,
        "evaluation_error_by_witness": errors,
    }


def _expr_parameter_entries(
    expr: Expr, path: tuple[int, ...] = ()
) -> list[tuple[tuple[int, ...], Expr]]:
    entries = [(path, expr)] if expr.op == "parameter" else []
    for index, arg in enumerate(expr.args):
        entries.extend(_expr_parameter_entries(arg, path + (index,)))
    return entries


def _row_parameter_entries(
    ast: Mapping[str, Any], path: tuple[int, ...] = ()
) -> list[tuple[tuple[int, ...], Mapping[str, Any]]]:
    entries = [(path, ast)] if ast.get("op") == "param" else []
    args = ast.get("args", [])
    if type(args) is list:
        for index, arg in enumerate(args):
            if type(arg) is dict:
                entries.extend(_row_parameter_entries(arg, path + (index,)))
    return entries


def _parameter_assignment_surface(
    derivative: Mapping[str, Any],
    witnesses: Sequence[LocalDenotationWitness],
) -> dict[str, Any]:
    """Consume every parameter leaf in AST and rows under both assignments."""

    surfaces: dict[str, dict[tuple[Any, ...], dict[str, Fraction]]] = {}
    public_records: dict[str, list[dict[str, Any]]] = {}
    for route_key, route_name in (
        ("forward_derivatives", "forward_AST"),
        ("reverse_derivatives", "reverse_AST"),
    ):
        value_map: dict[tuple[Any, ...], dict[str, Fraction]] = {}
        records: list[dict[str, Any]] = []
        for component in COMPONENTS:
            for ordinal, summand in enumerate(
                _summands(derivative[route_key][component])
            ):
                for path, node in _expr_parameter_entries(summand):
                    values = {
                        witness.name: _expr_probe_scalar(node, witness)
                        for witness in witnesses
                    }
                    key = (component, ordinal, path, node.label)
                    value_map[key] = values
                    records.append(
                        {
                            "component": component,
                            "summand_ordinal": ordinal,
                            "path": list(path),
                            "symbol": node.label,
                            "value_by_witness": values,
                        }
                    )
        surfaces[route_name] = value_map
        public_records[route_name] = records

    row_map: dict[tuple[Any, ...], dict[str, Fraction]] = {}
    row_records: list[dict[str, Any]] = []
    for row in derivative["FrechetRowV1_rows"]:
        for path, node in _row_parameter_entries(row["coefficient_ast"]):
            symbol = str(node.get("symbol"))
            values = {
                witness.name: _row_probe_scalar(node, witness)
                for witness in witnesses
            }
            key = (row["component"], row["summand_ordinal"], path, symbol)
            row_map[key] = values
            row_records.append(
                {
                    "component": row["component"],
                    "summand_ordinal": row["summand_ordinal"],
                    "path": list(path),
                    "symbol": symbol,
                    "value_by_witness": values,
                }
            )
    surfaces["FrechetRowV1"] = row_map
    public_records["FrechetRowV1"] = row_records

    route_values_agree = (
        surfaces["forward_AST"]
        == surfaces["reverse_AST"]
        == surfaces["FrechetRowV1"]
    )
    expected_symbols_exact = True
    for route_records in public_records.values():
        by_row: dict[tuple[str, int], list[str]] = {}
        for record in route_records:
            by_row.setdefault(
                (record["component"], record["summand_ordinal"]), []
            ).append(record["symbol"])
        expected_row_keys = {
            (component, ordinal)
            for component, count in EXPECTED_COMPONENT_ROW_COUNTS.items()
            for ordinal in range(count)
        }
        if set(by_row) != expected_row_keys:
            expected_symbols_exact = False
        for component in COMPONENTS:
            expected = ["M5"]
            if component.startswith("GHY_"):
                expected.append(f"s_out_{component.rsplit('_', 1)[1]}")
            component_rows = [
                symbols
                for (observed_component, _), symbols in by_row.items()
                if observed_component == component
            ]
            if not component_rows or any(sorted(symbols) != sorted(expected) for symbols in component_rows):
                expected_symbols_exact = False
    assignments_cover_all_parameters = all(
        set(witness.parameters) == {"M5", "s_out_plus", "s_out_minus"}
        and all(value != 0 for value in witness.parameters.values())
        for witness in witnesses
    )
    return {
        "pass": bool(
            route_values_agree
            and expected_symbols_exact
            and assignments_cover_all_parameters
        ),
        "route_and_row_values_agree": route_values_agree,
        "expected_symbols_exact_per_component_and_ordinal": (
            expected_symbols_exact
        ),
        "every_assignment_covers_M5_and_both_outward_signs_nonzero": (
            assignments_cover_all_parameters
        ),
        "records": public_records,
    }


def _local_component_surface(
    component: str,
    records: list[dict[str, Any]],
    witnesses: Sequence[LocalDenotationWitness],
) -> dict[str, Any]:
    observed_keys = [
        (record["kind"], record["summand_ordinal"], tuple(record["path"]))
        for record in records
    ]
    expected_keys = list(_expected_local_coverage(component))
    inverse_records = [record for record in records if record["kind"] == "inverse"]
    volume_records = [record for record in records if record["kind"] == "volume"]
    for record in records:
        expected_values: dict[str, Any] = {}
        expected_errors: dict[str, str] = {}
        for witness in witnesses:
            try:
                expected_values[witness.name] = _independent_local_expected_value(
                    component,
                    record["kind"],
                    record["summand_ordinal"],
                    witness,
                )
            except GravityFrechetError as exc:
                expected_values[witness.name] = None
                expected_errors[witness.name] = str(exc)
        record["expected_value_by_witness"] = expected_values
        record["expected_error_by_witness"] = expected_errors
        record["values_exact"] = bool(
            not expected_errors
            and not record["evaluation_error_by_witness"]
            and record["value_by_witness"] == record["expected_value_by_witness"]
        )
    values_exact = all(record["values_exact"] for record in records)
    coverage_exact = sorted(observed_keys) == sorted(expected_keys)
    no_duplicate_paths = len(observed_keys) == len(set(observed_keys))
    return {
        "pass": bool(coverage_exact and no_duplicate_paths and values_exact),
        "inverse_count": len(inverse_records),
        "volume_count": len(volume_records),
        "coverage_exact": coverage_exact,
        "no_duplicate_ordinal_paths": no_duplicate_paths,
        "values_exact": values_exact,
        "expected_coverage": [
            {"kind": kind, "summand_ordinal": ordinal, "path": list(path)}
            for kind, ordinal, path in expected_keys
        ],
        "observed_coverage": [
            {
                "kind": record["kind"],
                "summand_ordinal": record["summand_ordinal"],
                "path": record["path"],
            }
            for record in records
        ],
        "records": records,
        "coverage_sha256": _canonical_sha256(observed_keys),
    }


def _inverse_volume_ast_bridge(derivative: Mapping[str, Any]) -> dict[str, Any]:
    witnesses = _local_denotation_witnesses()
    parameter_surface = _parameter_assignment_surface(derivative, witnesses)

    surfaces: dict[str, Any] = {}
    for route_key, public_name in (
        ("forward_derivatives", "forward_AST"),
        ("reverse_derivatives", "reverse_AST"),
    ):
        components: dict[str, Any] = {}
        for component in COMPONENTS:
            records: list[dict[str, Any]] = []
            for ordinal, summand in enumerate(
                _summands(derivative[route_key][component])
            ):
                for path, root in _expr_local_inverse_entries(summand):
                    records.append(
                        {
                            "route": public_name,
                            "component": component,
                            "summand_ordinal": ordinal,
                            "kind": "inverse",
                            "path": list(path),
                            **_probe_all_witnesses(
                                _expr_probe_inverse, root, witnesses
                            ),
                            "local_ast_sha256": _canonical_sha256(expr_row(root)),
                        }
                    )
                for path, root in _expr_local_volume_entries(summand):
                    records.append(
                        {
                            "route": public_name,
                            "component": component,
                            "summand_ordinal": ordinal,
                            "kind": "volume",
                            "path": list(path),
                            **_probe_all_witnesses(
                                _expr_probe_volume, root, witnesses
                            ),
                            "local_ast_sha256": _canonical_sha256(expr_row(root)),
                        }
                    )
            records.sort(
                key=lambda record: (
                    record["summand_ordinal"], record["kind"], record["path"]
                )
            )
            components[component] = _local_component_surface(
                component, records, witnesses
            )
        surfaces[public_name] = {
            "pass": all(row["pass"] for row in components.values()),
            "components": components,
            "inverse_count": sum(row["inverse_count"] for row in components.values()),
            "volume_count": sum(row["volume_count"] for row in components.values()),
        }

    row_components: dict[str, Any] = {}
    for component in COMPONENTS:
        records = []
        for row in derivative["FrechetRowV1_rows"]:
            if row["component"] != component:
                continue
            ast = row["coefficient_ast"]
            for path, root in _row_local_inverse_entries(ast):
                records.append(
                    {
                        "route": "FrechetRowV1",
                        "component": component,
                        "summand_ordinal": row["summand_ordinal"],
                        "kind": "inverse",
                        "path": list(path),
                        **_probe_all_witnesses(
                            _row_probe_inverse, root, witnesses
                        ),
                        "local_ast_sha256": _canonical_sha256(root),
                        "coefficient_ast_sha256": row["coefficient_ast_sha256"],
                    }
                )
            for path, root in _row_local_volume_entries(ast):
                records.append(
                    {
                        "route": "FrechetRowV1",
                        "component": component,
                        "summand_ordinal": row["summand_ordinal"],
                        "kind": "volume",
                        "path": list(path),
                        **_probe_all_witnesses(
                            _row_probe_volume, root, witnesses
                        ),
                        "local_ast_sha256": _canonical_sha256(root),
                        "coefficient_ast_sha256": row["coefficient_ast_sha256"],
                    }
                )
        records.sort(
            key=lambda record: (
                record["summand_ordinal"], record["kind"], record["path"]
            )
        )
        row_components[component] = _local_component_surface(
            component, records, witnesses
        )
    surfaces["FrechetRowV1"] = {
        "pass": all(row["pass"] for row in row_components.values()),
        "components": row_components,
        "inverse_count": sum(row["inverse_count"] for row in row_components.values()),
        "volume_count": sum(row["volume_count"] for row in row_components.values()),
    }
    expected_counts = {
        "inverse": 32,
        "volume": 14,
        "by_component": {
            component: {
                "inverse": sum(
                    kind == "inverse"
                    for kind, _, _ in _expected_local_coverage(component)
                ),
                "volume": sum(
                    kind == "volume"
                    for kind, _, _ in _expected_local_coverage(component)
                ),
            }
            for component in COMPONENTS
        },
    }
    surface_coverage = {
        name: {
            component: row["coverage_sha256"]
            for component, row in surface["components"].items()
        }
        for name, surface in surfaces.items()
    }
    coverage_agrees = all(
        surface_coverage["forward_AST"][component]
        == surface_coverage["reverse_AST"][component]
        == surface_coverage["FrechetRowV1"][component]
        for component in COMPONENTS
    )
    denotational_values_by_surface = {
        surface_name: {
            component: {
                (
                    record["kind"],
                    record["summand_ordinal"],
                    tuple(record["path"]),
                ): record["value_by_witness"]
                for record in surface["components"][component]["records"]
            }
            for component in COMPONENTS
        }
        for surface_name, surface in surfaces.items()
    }
    denotational_values_agree = all(
        denotational_values_by_surface["forward_AST"][component]
        == denotational_values_by_surface["reverse_AST"][component]
        == denotational_values_by_surface["FrechetRowV1"][component]
        for component in COMPONENTS
    )
    witness_rows = [
        {
            "name": witness.name,
            "bulk_dimension": len(witness.metric),
            "interface_dimension": len(witness.embedding_first[0]),
            "parameters": dict(witness.parameters),
            "metric_sha256": _canonical_sha256(witness.metric),
            "metric_first_sha256": _canonical_sha256(witness.metric_first),
            "metric_variation_sha256": _canonical_sha256(
                witness.metric_variation
            ),
            "embedding_sha256": _canonical_sha256(witness.embedding),
            "embedding_variation_sha256": _canonical_sha256(
                witness.embedding_variation
            ),
        }
        for witness in witnesses
    ]
    return {
        "pass": bool(
            all(row["pass"] for row in surfaces.values())
            and coverage_agrees
            and denotational_values_agree
            and parameter_surface["pass"]
            and all(
                surface["inverse_count"] == expected_counts["inverse"]
                and surface["volume_count"] == expected_counts["volume"]
                for surface in surfaces.values()
            )
        ),
        "independent_expected": {
            "method": (
                "direct exact 5x5/4x4 Gauss-Jordan inverse, determinant, "
                "matrix multiplication, pullback, and first-jet contraction; "
                "no forward/reverse AD rule or attacked AST supplies expectations"
            ),
            "inverse_formula": "-base_inverse*tangent*base_inverse",
            "volume_formula": "sqrt(-det(base))*trace(base_inverse*tangent)/2",
            "GHY_ordinal_tangent_map": {
                "volume": {
                    "0": "pullback(H,E,E)",
                    "1": "pullback(partial_g.xi,E,E)",
                    "2": "pullback(g(Y),Dxi,E)",
                    "3": "pullback(g(Y),E,Dxi)",
                },
                "inverse": {
                    "12,23": "H(Y)",
                    "13,24": "partial_g.xi",
                    "25": "pullback(H,E,E)",
                    "26": "pullback(partial_g.xi,E,E)",
                    "27": "pullback(g(Y),Dxi,E)",
                    "28": "pullback(g(Y),E,Dxi)",
                },
            },
        },
        "declared_dimensions": {"bulk": 5, "interface": 4},
        "finite_exact_rational_witnesses": witness_rows,
        "finite_witness_count": len(witnesses),
        "parameter_assignment_surface": parameter_surface,
        "expected_local_primitive_counts": expected_counts,
        "coverage_agrees_across_routes_and_rows": coverage_agrees,
        "denotational_values_agree_across_routes_and_rows": (
            denotational_values_agree
        ),
        "coverage_sha256_by_surface_and_component": surface_coverage,
        "expected_coverage_sha256": _canonical_sha256(
            {
                component: _expected_local_coverage(component)
                for component in COMPONENTS
            }
        ),
        "surfaces": surfaces,
        "consumed_derivatives_sha256": derivative["derivatives_sha256"],
        "consumed_FrechetRowV1_sha256": derivative["FrechetRowV1_rows_sha256"],
        "scope": (
            "two finite exact rational witnesses for local inverse and volume derivative "
            "nodes only, in the declared ambient dimension five and interface dimension "
            "four; every inverse, trace, add, parameter scale, jet-evaluation, embedding, "
            "pullback, and volume operand is evaluated recursively and values are compared "
            "by component, summand ordinal, path, route, and row. This is not a universal "
            "coordinate identity or a denotation of every gravity primitive"
        ),
    }


_SYMBOLIC_PARAMETER_ORDER = ("M5", "s_out_plus", "s_out_minus")
_SymbolicPolynomial = dict[tuple[int, int, int], Fraction]


def _polynomial_add(
    left: _SymbolicPolynomial, right: _SymbolicPolynomial
) -> _SymbolicPolynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, Fraction(0)) + coefficient
        if result[monomial] == 0:
            del result[monomial]
    return result


def _polynomial_multiply(
    left: _SymbolicPolynomial, right: _SymbolicPolynomial
) -> _SymbolicPolynomial:
    result: _SymbolicPolynomial = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            monomial = tuple(
                a + b for a, b in zip(left_power, right_power, strict=True)
            )
            result[monomial] = (
                result.get(monomial, Fraction(0))
                + left_coefficient * right_coefficient
            )
    return {key: value for key, value in result.items() if value != 0}


def _polynomial_power(
    value: _SymbolicPolynomial, exponent: int
) -> _SymbolicPolynomial:
    if exponent < 0:
        raise GravityFrechetError(
            "parameter polynomial normal form rejects negative powers"
        )
    result: _SymbolicPolynomial = {(0, 0, 0): Fraction(1)}
    base = dict(value)
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = _polynomial_multiply(result, base)
        base = _polynomial_multiply(base, base)
        remaining //= 2
    return result


def _expr_parameter_polynomial(expr: Expr) -> _SymbolicPolynomial | None:
    if expr.op == "rational":
        assert expr.value is not None
        return {(0, 0, 0): expr.value}
    if expr.op == "parameter":
        if expr.label not in _SYMBOLIC_PARAMETER_ORDER:
            raise GravityFrechetError("symbolic normal form saw unknown parameter")
        powers = [0, 0, 0]
        powers[_SYMBOLIC_PARAMETER_ORDER.index(expr.label)] = 1
        return {tuple(powers): Fraction(1)}
    if expr.op == "add":
        result: _SymbolicPolynomial = {}
        for arg in expr.args:
            child = _expr_parameter_polynomial(arg)
            if child is None:
                return None
            result = _polynomial_add(result, child)
        return result
    if expr.op == "mul_scalar":
        result = {(0, 0, 0): Fraction(1)}
        for arg in expr.args:
            child = _expr_parameter_polynomial(arg)
            if child is None:
                return None
            result = _polynomial_multiply(result, child)
        return result
    if expr.op == "power":
        assert expr.exponent is not None
        child = _expr_parameter_polynomial(expr.args[0])
        if child is None or expr.exponent.denominator != 1 or expr.exponent < 0:
            return None
        return _polynomial_power(child, expr.exponent.numerator)
    return None


def _row_parameter_polynomial(ast: Mapping[str, Any]) -> _SymbolicPolynomial | None:
    operation = ast.get("op")
    if operation == "const":
        value = ast.get("value")
        if type(value) is not list or len(value) != 2:
            raise GravityFrechetError("symbolic row constant is malformed")
        return {(0, 0, 0): Fraction(value[0], value[1])}
    if operation == "param":
        symbol = ast.get("symbol")
        if symbol not in _SYMBOLIC_PARAMETER_ORDER:
            raise GravityFrechetError("symbolic row normal form saw unknown parameter")
        powers = [0, 0, 0]
        powers[_SYMBOLIC_PARAMETER_ORDER.index(symbol)] = 1
        return {tuple(powers): Fraction(1)}
    args = ast.get("args", [])
    if operation == "add":
        result: _SymbolicPolynomial = {}
        for arg in args:
            child = _row_parameter_polynomial(arg)
            if child is None:
                return None
            result = _polynomial_add(result, child)
        return result
    if operation == "mul":
        result = {(0, 0, 0): Fraction(1)}
        for arg in args:
            child = _row_parameter_polynomial(arg)
            if child is None:
                return None
            result = _polynomial_multiply(result, child)
        return result
    if operation == "pow":
        exponent = ast.get("exponent")
        child = _row_parameter_polynomial(args[0]) if len(args) == 1 else None
        if (
            child is None
            or type(exponent) is not list
            or len(exponent) != 2
            or exponent[1] != 1
            or exponent[0] < 0
        ):
            return None
        return _polynomial_power(child, exponent[0])
    return None


def _polynomial_normal_form(value: _SymbolicPolynomial) -> tuple[Any, ...]:
    return tuple(
        (powers, (coefficient.numerator, coefficient.denominator))
        for powers, coefficient in sorted(value.items())
    )


def _symbolic_type_key(type_tag: GeoType) -> tuple[Any, ...]:
    return (
        type_tag.name,
        type_tag.base_dimension,
        type_tag.variance,
        type_tag.density_weight,
        type_tag.symmetry,
    )


def _symbolic_sort(values: Iterable[tuple[Any, ...]]) -> tuple[tuple[Any, ...], ...]:
    return tuple(sorted(values, key=lambda value: repr(value)))


def _expr_free_jet_key(expr: Expr) -> tuple[str, int]:
    match = re.fullmatch(r"(?P<stem>g|Y)(?P<order>[12])_(?P<side>plus|minus)", expr.label)
    if match is None:
        return expr.label, 0
    return f"{match.group('stem')}_{match.group('side')}", int(match.group("order"))


def _expr_whole_summand_nf(expr: Expr) -> tuple[Any, ...]:
    parameter_polynomial = (
        _expr_parameter_polynomial(expr) if _is_scalar(expr.type_tag) else None
    )
    type_key = _symbolic_type_key(expr.type_tag)
    if parameter_polynomial is not None:
        return ("parameter_polynomial", type_key, _polynomial_normal_form(parameter_polynomial))
    if expr.op == "field":
        symbol, order = _expr_free_jet_key(expr)
        return ("typed_free_jet", type_key, symbol, order)
    if expr.op == "variation":
        return (
            "typed_variation",
            type_key,
            expr.label,
            len(expr.derivative_word),
        )
    if expr.op == "zero":
        return ("typed_zero", type_key)
    children = tuple(_expr_whole_summand_nf(arg) for arg in expr.args)
    if expr.op == "add":
        return ("add", type_key, _symbolic_sort(children))
    if expr.op in {"mul_scalar", "scale"}:
        return ("product", type_key, _symbolic_sort(children))
    if expr.op == "power":
        assert expr.exponent is not None
        return (
            "power",
            type_key,
            (expr.exponent.numerator, expr.exponent.denominator),
            children[0],
        )
    if expr.op in {"sqrt", "inverse_metric", "volume_density"}:
        return (expr.op, type_key, children)
    if expr.op == "multilinear":
        return ("typed_free_tensor_operator", type_key, expr.label, children)
    if expr.op == "covariant_acceleration":
        return ("covariant_acceleration", type_key, expr.label, children)
    if expr.op == "evaluate_jet":
        return ("jet_evaluation", type_key, expr.label, children)
    raise GravityFrechetError(
        f"symbolic producer normal form rejects operation {expr.op}"
    )


def _row_whole_summand_nf(
    ast: Mapping[str, Any], variation_component: str, derivative_order: int
) -> tuple[Any, ...]:
    type_tag = _compat_ast_type(ast)
    parameter_polynomial = (
        _row_parameter_polynomial(ast) if _is_scalar(type_tag) else None
    )
    type_key = _symbolic_type_key(type_tag)
    if parameter_polynomial is not None:
        return ("parameter_polynomial", type_key, _polynomial_normal_form(parameter_polynomial))
    operation = ast.get("op")
    if operation == "jet":
        derivative = ast.get("derivative", {})
        return (
            "typed_free_jet",
            type_key,
            ast.get("symbol"),
            len(derivative.get("word", [])),
        )
    if operation == "linear_slot":
        return (
            "typed_variation",
            type_key,
            variation_component,
            derivative_order,
        )
    if operation == "const":
        if ast.get("value") != [0, 1]:
            raise GravityFrechetError("non-scalar tensor constant is not zero")
        return ("typed_zero", type_key)
    args = ast.get("args", [])
    if type(args) is not list:
        raise GravityFrechetError("symbolic row operands are not a list")
    children = tuple(
        _row_whole_summand_nf(arg, variation_component, derivative_order)
        for arg in args
    )
    if operation == "add":
        return ("add", type_key, _symbolic_sort(children))
    if operation == "mul":
        return ("product", type_key, _symbolic_sort(children))
    if operation == "pow":
        exponent = ast.get("exponent")
        return ("power", type_key, tuple(exponent), children[0])
    if operation in {"sqrt", "inverse_metric", "volume_density"}:
        return (operation, type_key, children)
    if operation == "tensor_contract":
        return (
            "typed_free_tensor_operator",
            type_key,
            ast.get("convention"),
            children,
        )
    if operation == "covariant_acceleration":
        return (
            "covariant_acceleration",
            type_key,
            ast.get("convention"),
            children,
        )
    if operation == "jet_evaluation":
        return ("jet_evaluation", type_key, ast.get("convention"), children)
    raise GravityFrechetError(
        f"symbolic row decoder rejects operation {operation}"
    )


def _independent_symbolic_replay_frechet(
    expr: Expr, tangent_slots: Mapping[str, Expr]
) -> Expr:
    """Third derivative visitor; it calls neither production AD route nor exporter."""

    if expr.op in {"rational", "parameter", "zero"}:
        return zero(expr.type_tag)
    if expr.op == "field":
        return tangent_slots.get(expr.label, zero(expr.type_tag))
    if expr.op in {"variation", "linear_slot"}:
        raise GravityFrechetError("symbolic replay received a linearized primal leaf")
    tangents = tuple(
        _independent_symbolic_replay_frechet(arg, tangent_slots)
        for arg in expr.args
    )
    if expr.op == "add":
        return _sum_tangents(expr.type_tag, tangents)
    if expr.op == "mul_scalar":
        return _sum_tangents(
            expr.type_tag,
            (
                mul_scalar(
                    tangent,
                    *(arg for j, arg in enumerate(expr.args) if j != index),
                )
                for index, tangent in enumerate(tangents)
                if not is_zero(tangent)
            ),
        )
    if expr.op == "scale":
        terms: list[Expr] = []
        if not is_zero(tangents[0]):
            terms.append(scale(tangents[0], expr.args[1]))
        if not is_zero(tangents[1]):
            terms.append(scale(expr.args[0], tangents[1]))
        return _sum_tangents(expr.type_tag, terms)
    if expr.op == "power":
        assert expr.exponent is not None
        if is_zero(tangents[0]):
            return zero(expr.type_tag)
        return mul_scalar(
            rational(expr.exponent),
            power(expr.args[0], expr.exponent - 1),
            tangents[0],
        )
    if expr.op == "sqrt":
        if is_zero(tangents[0]):
            return zero(expr.type_tag)
        return mul_scalar(
            rational(Fraction(1, 2)),
            power(expr.args[0], Fraction(-1, 2)),
            tangents[0],
        )
    if expr.op == "inverse_metric":
        if is_zero(tangents[0]):
            return zero(expr.type_tag)
        inverse = inverse_metric(expr.args[0])
        return negate(
            multilinear(
                _inverse_sandwich_label(inverse.type_tag),
                inverse,
                tangents[0],
                inverse,
            )
        )
    if expr.op == "volume_density":
        if is_zero(tangents[0]):
            return zero(expr.type_tag)
        inverse = inverse_metric(expr.args[0])
        trace = multilinear(
            _metric_trace_label(inverse.type_tag), inverse, tangents[0]
        )
        return scale(
            mul_scalar(rational(Fraction(1, 2)), trace),
            volume_density(expr.args[0]),
        )
    if expr.op == "multilinear":
        return _sum_tangents(
            expr.type_tag,
            (
                multilinear(
                    expr.label,
                    *(expr.args[:index] + (tangent,) + expr.args[index + 1 :]),
                )
                for index, tangent in enumerate(tangents)
                if not is_zero(tangent)
            ),
        )
    if expr.op == "covariant_acceleration":
        terms = []
        if not is_zero(tangents[0]):
            terms.append(covariant_acceleration(tangents[0], zero(ACCELERATION5)))
        if not is_zero(tangents[1]):
            terms.append(tangents[1])
        return _sum_tangents(ACCELERATION5, terms)
    if expr.op == "evaluate_jet":
        order = 0 if expr.label.startswith("metric_jet_0") else 1
        moving = expr.label.endswith("moving_Y")
        terms = []
        if not is_zero(tangents[0]):
            terms.append(
                multilinear(
                    f"evaluate_metric_variation_{order}",
                    tangents[0],
                    expr.args[2],
                )
            )
        if moving and not is_zero(tangents[2]):
            terms.append(
                multilinear(
                    f"transport_metric_jet_{order}",
                    expr.args[1],
                    expr.args[2],
                    tangents[2],
                )
            )
        return _sum_tangents(expr.type_tag, terms)
    raise GravityFrechetError(
        f"symbolic replay has no local rule for {expr.op}"
    )


def _symbolic_whole_summand_certificate(
    program: Program, derivative: Mapping[str, Any]
) -> dict[str, Any]:
    component_rows: dict[str, Any] = {}
    all_pass = True
    total = 0
    for component in COMPONENTS:
        expected_expr = _independent_symbolic_replay_frechet(
            program.components[component], program.tangents
        )
        expected_terms = _summands(expected_expr)
        forward_terms = _summands(derivative["forward_derivatives"][component])
        reverse_terms = _summands(derivative["reverse_derivatives"][component])
        exported_rows = sorted(
            (
                row
                for row in derivative["FrechetRowV1_rows"]
                if row["component"] == component
            ),
            key=lambda row: row["summand_ordinal"],
        )
        count_exact = (
            len(expected_terms)
            == len(forward_terms)
            == len(reverse_terms)
            == len(exported_rows)
        )
        records: list[dict[str, Any]] = []
        for ordinal in range(
            max(
                len(expected_terms),
                len(forward_terms),
                len(reverse_terms),
                len(exported_rows),
            )
        ):
            try:
                expected_nf = _expr_whole_summand_nf(expected_terms[ordinal])
                forward_nf = _expr_whole_summand_nf(forward_terms[ordinal])
                reverse_nf = _expr_whole_summand_nf(reverse_terms[ordinal])
                row = exported_rows[ordinal]
                if row["summand_ordinal"] != ordinal:
                    raise GravityFrechetError(
                        "symbolic row ordinal is not canonical"
                    )
                row_nf = _row_whole_summand_nf(
                    row["coefficient_ast"],
                    row["variation_component"],
                    len(row["derivative"]["word"]),
                )
                route_equal = forward_nf == reverse_nf == row_nf
                expected_equal = expected_nf == forward_nf
                error = None
            except (
                GravityFrechetError,
                IndexError,
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                expected_nf = forward_nf = reverse_nf = row_nf = None
                route_equal = expected_equal = False
                error = str(exc)
            records.append(
                {
                    "component": component,
                    "summand_ordinal": ordinal,
                    "expected_replay_sha256": _canonical_sha256(expected_nf),
                    "forward_AST_sha256": _canonical_sha256(forward_nf),
                    "reverse_AST_sha256": _canonical_sha256(reverse_nf),
                    "FrechetRowV1_decoded_sha256": _canonical_sha256(row_nf),
                    "producer_reverse_row_denotational_equal": route_equal,
                    "independent_replay_equal": expected_equal,
                    "error": error,
                }
            )
        component_pass = bool(
            count_exact
            and records
            and all(
                row["producer_reverse_row_denotational_equal"]
                and row["independent_replay_equal"]
                and row["error"] is None
                for row in records
            )
        )
        all_pass = all_pass and component_pass
        total += len(records)
        component_rows[component] = {
            "pass": component_pass,
            "count_exact": count_exact,
            "expected_count": len(expected_terms),
            "forward_count": len(forward_terms),
            "reverse_count": len(reverse_terms),
            "row_count": len(exported_rows),
            "records": records,
        }
    return {
        "pass": bool(all_pass and total == 90),
        "whole_summand_count": total,
        "parameter_indeterminates": list(_SYMBOLIC_PARAMETER_ORDER),
        "parameter_normal_form": "exact multivariate Q polynomial, never point-evaluated",
        "tensor_primitive_semantics": (
            "typed free symbols/operators with every operand retained recursively"
        ),
        "expected_route": (
            "independent third local-rule replay from the byte-bound primal Program; "
            "does not call forward_nilpotent_dual, reverse_context_frechet, "
            "export_frechet_rows, or coefficient_ast"
        ),
        "comparison_key": "component plus canonical summand ordinal",
        "components": component_rows,
        "scope": (
            "symbolic whole-summand formal check; it retains outer factors and every "
            "operand but treats undeveloped tensor primitives as typed free operators, "
            "so it is not a full coordinate semantic Frechet proof"
        ),
    }


def exact_oracles(program: Program, derivative: Mapping[str, Any]) -> dict[str, Any]:
    g_inverse = ((Fraction(-1), Fraction(0)), (Fraction(0), Fraction(1)))
    h = ((Fraction(1), Fraction(2)), (Fraction(2), Fraction(3)))

    def mm(left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(
            tuple(
                sum(left[i][k] * right[k][j] for k in range(len(right)))
                for j in range(len(right[0]))
            )
            for i in range(len(left))
        )

    sandwich = mm(mm(g_inverse, h), g_inverse)
    delta_inverse = tuple(tuple(-value for value in row) for row in sandwich)
    volume_linear = Fraction(1, 2) * sum(
        g_inverse[i][j] * h[j][i] for i in range(2) for j in range(2)
    )

    gamma_1d = Fraction(2)
    gamma_prime_1d = Fraction(1)
    h_1d = Fraction(3)
    h_prime_1d = Fraction(5)
    delta_christoffel = (
        h_prime_1d / (2 * gamma_1d)
        - gamma_prime_1d * h_1d / (2 * gamma_1d * gamma_1d)
    )

    tangents = tuple(
        tuple(Fraction(1) if ambient == boundary else Fraction(0) for ambient in range(5))
        for boundary in range(4)
    )
    cofactor: list[Fraction] = []
    for a in range(5):
        total = Fraction(0)
        for ambient_tail in itertools.permutations([index for index in range(5) if index != a]):
            epsilon5 = _permutation_sign((a, *ambient_tail))
            for boundary_perm in itertools.permutations(range(4)):
                epsilon4 = _permutation_sign(boundary_perm)
                product = Fraction(epsilon5 * epsilon4)
                for slot in range(4):
                    product *= tangents[boundary_perm[slot]][ambient_tail[slot]]
                total += product
        cofactor.append(total / 24)
    outward_normal = tuple(-value for value in cofactor)
    outward_dot_dr = outward_normal[4]

    moved_metric = Fraction(11) + Fraction(2) * Fraction(5)
    moved_first_jet = Fraction(13) + Fraction(2) * Fraction(7)

    # Flat graph r=f(x): at f=0, delta gamma=0,
    # delta n_mu=-s_out partial_mu f and delta Theta=-s_out box(f).
    flat_graph = {
        "test_function": "f=t^2 at the origin in diag(-1,1,1,1,1)",
        "delta_gamma": Fraction(0),
        "delta_n_t_coefficient_of_t": Fraction(-2),
        "box_f": Fraction(-2),
        "delta_Theta_for_s_out_plus_one": Fraction(2),
    }

    warped = {
        "metric": "dr^2+a(r)^2 eta_mn dx^m dx^n",
        "a": Fraction(2),
        "a_prime": Fraction(3),
        "s_out": Fraction(1),
        "Theta": Fraction(6),
        "Brown_York_pi_coefficient_times_gamma_inverse": Fraction(-9, 2),
    }

    program_hash = _canonical_sha256(_program_manifest(program))
    return {
        "scope": (
            "prefactor, Q-composition, derivative-inventory, symbolic whole-summand replay "
            "and inverse/volume bridge checks consume generated ASTs and rows; the remaining "
            "rational coordinate examples are auxiliary algebra checks only"
        ),
        "consumed_AST": {
            "program_sha256": program_hash,
            "derivatives_sha256": derivative["derivatives_sha256"],
        },
        "literal_action_prefactors": _literal_prefactor_oracle(program),
        "literal_exterior_M5_polynomial": (
            _literal_exterior_M5_polynomial_oracle(program)
        ),
        "covariant_acceleration_composition": _covariant_acceleration_oracle(program),
        "derivative_primitive_inventory": _derivative_primitive_oracle(derivative),
        "derivative_AST_inverse_volume_bridge": _inverse_volume_ast_bridge(derivative),
        "symbolic_whole_summand_replay": _symbolic_whole_summand_certificate(
            program, derivative
        ),
        "inverse_and_volume": {
            "g_inverse": g_inverse,
            "H": h,
            "delta_g_inverse": delta_inverse,
            "expected_delta_g_inverse": ((Fraction(-1), Fraction(2)), (Fraction(2), Fraction(-3))),
            "delta_sqrt_minus_det": volume_linear,
            "expected_delta_sqrt_minus_det": Fraction(1),
        },
        "Christoffel_1d": {
            "formula": "delta Gamma=H'/(2g)-g'H/(2g^2)",
            "value": delta_christoffel,
            "expected": Fraction(7, 8),
        },
        "cofactor_outward": {
            "identity_embedding_cofactor": tuple(cofactor),
            "expected": (Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
            "selected_normal": outward_normal,
            "n_dot_dr": outward_dot_dr,
            "outward_inequality": "n^A partial_A r<0",
        },
        "moving_pulljet": {
            "delta_g_at_Y": moved_metric,
            "expected_delta_g_at_Y": Fraction(21),
            "delta_g1_at_Y": moved_first_jet,
            "expected_delta_g1_at_Y": Fraction(27),
        },
        "flat_graph_Theta_sign": flat_graph,
        "warped_Brown_York_nonzero_diagnostic": warped,
    }


def _oracles_pass(oracles: Mapping[str, Any]) -> bool:
    inverse = oracles["inverse_and_volume"]
    christoffel = oracles["Christoffel_1d"]
    cofactor = oracles["cofactor_outward"]
    moved = oracles["moving_pulljet"]
    flat = oracles["flat_graph_Theta_sign"]
    warped = oracles["warped_Brown_York_nonzero_diagnostic"]
    return bool(
        oracles["literal_action_prefactors"]["pass"]
        and oracles["literal_exterior_M5_polynomial"]["pass"]
        and oracles["covariant_acceleration_composition"]["pass"]
        and oracles["derivative_primitive_inventory"]["pass"]
        and oracles["derivative_AST_inverse_volume_bridge"]["pass"]
        and inverse["delta_g_inverse"] == inverse["expected_delta_g_inverse"]
        and inverse["delta_sqrt_minus_det"] == inverse["expected_delta_sqrt_minus_det"]
        and christoffel["value"] == christoffel["expected"]
        and cofactor["identity_embedding_cofactor"] == cofactor["expected"]
        and cofactor["n_dot_dr"] < 0
        and moved["delta_g_at_Y"] == moved["expected_delta_g_at_Y"]
        and moved["delta_g1_at_Y"] == moved["expected_delta_g1_at_Y"]
        and flat["delta_Theta_for_s_out_plus_one"] == -flat["box_f"]
        and warped["Brown_York_pi_coefficient_times_gamma_inverse"] != 0
    )


def _fixed_embedding_brown_york_subcertificate(
    program: Program,
    derivative: Mapping[str, Any],
    green_form: Mapping[str, Any],
) -> dict[str, Any]:
    """Post-process already-derived rows; never feed the target into AD."""

    rows = derivative["FrechetRowV1_rows"]
    xi_rows = [row for row in rows if row["variation_component"].startswith("xi_")]
    fixed_rows = [row for row in rows if not row["variation_component"].startswith("xi_")]
    constructor_serialized = json.dumps(
        {name: expr_row(expr) for name, expr in program.components.items()},
        sort_keys=True,
    )
    target = green_form.get("EH_plus_GHY_first_variation")
    if type(target) is not str:
        raise GravityFrechetError("v5.2 Brown--York diagnostic target missing")
    normal_metric_jet_rows = [
        row
        for row in fixed_rows
        if row["variation_component"].startswith("H_")
        and len(row["derivative"]["word"]) > 0
    ]
    # The raw bulk rows are volume densities on M_eps.  Comparing them with
    # Sigma rows requires deriving the Palatini current and applying oriented
    # Stokes.  This gate has no such reducer, so even a suggestive row count or
    # the v5.2 target string cannot close the identity.
    return {
        "pass": False,
        "constructed_after_both_raw_derivatives": derivative["pass"],
        "input_derivatives_sha256": derivative["derivatives_sha256"],
        "input_FrechetRowV1_sha256": derivative["FrechetRowV1_rows_sha256"],
        "projection": "xi_plus=xi_minus=0 applied to exported rows after differentiation",
        "raw_row_count": len(rows),
        "discarded_xi_row_count": len(xi_rows),
        "fixed_embedding_row_count": len(fixed_rows),
        "normal_metric_jet_row_count_before_boundary_reduction": len(normal_metric_jet_rows),
        "constructor_contains_Brown_York_target": "Brown_York" in constructor_serialized,
        "constructor_contains_v5_2_target_text": target in constructor_serialized,
        "v5_2_target_diagnostic_sha256": hashlib.sha256(target.encode("utf-8")).hexdigest(),
        "v5_2_target_role": "comparison_target_only_not_constructor_or_rewrite_rule",
        "Palatini_boundary_current_derived_from_EH_rows": False,
        "oriented_Stokes_map_from_Meps_to_Sigma_implemented": False,
        "normal_derivative_cancellation_exact": False,
        "Brown_York_remainder_exact": False,
        "reason": (
            "raw exact Frechet rows do not themselves identify the EH boundary current; "
            "a separately checked Palatini plus oriented-Stokes normal-form reducer is required"
        ),
    }


MANDATORY_MUTANTS = (
    "semantic_completion_post_cache_tamper",
    "primal_read_once_M5_alias",
    "wrong_EH_half",
    "wrong_GHY_half",
    "wrong_inverse_sign",
    "wrong_volume_half",
    "correlated_wrong_inverse_sign",
    "correlated_wrong_volume_half",
    "correlated_inverse_operand_doubled",
    "correlated_dimension_trace_identity_factor",
    "correlated_inverse_operand_scaled_by_M5",
    "correlated_evaluation_embedding_scaled_by_M5",
    "row_evaluation_embedding_scaled_by_M5",
    "finite_alias_inverse_operand_lost_prefactor",
    "lost_inverse_summand_M5_cubed_prefactor",
    "wrong_Ricci_trace",
    "wrong_Theta_sign",
    "frozen_normal",
    "unnormalized_normal",
    "inward_normal",
    "GHY_gamma_only",
    "omit_moved_point",
    "omit_Y2",
    "freeze_Y",
    "collapse_mixed",
    "inject_Brown_York_target",
    "binder_wrong_dimension",
    "binder_wrong_namespace",
    "binder_GHY_H_uses_integration_domain",
    "xi_D2_slot_mistyped_as_acceleration",
    "binder_free_word",
    "binder_illegal_capture",
    "binder_not_alpha_normalized",
    "row_unknown_rehashed_opcode",
    "row_extra_rehashed_metadata",
    "fake_source_span_rehashed",
    "row_ordinal_999",
    "row_duplicate_ordinal",
    "row_plus_variation_to_minus",
    "row_plus_jet_to_minus",
    "row_GHY_outward_selector_to_M5",
    "integral_duplicate_minus_into_plus",
)

MUTANT_REQUIRED_FAILURE_SURFACES = {
    "semantic_completion_post_cache_tamper": "semantic_completion_pin",
    "primal_read_once_M5_alias": "literal_exterior_M5_polynomial_exact",
    "wrong_EH_half": "AST_literal_EH_GHY_prefactors_exact",
    "wrong_GHY_half": "AST_literal_EH_GHY_prefactors_exact",
    "correlated_wrong_inverse_sign": "exact_small_oracles",
    "correlated_wrong_volume_half": "exact_small_oracles",
    "correlated_inverse_operand_doubled": "exact_small_oracles",
    "correlated_dimension_trace_identity_factor": "exact_small_oracles",
    "correlated_inverse_operand_scaled_by_M5": "exact_small_oracles",
    "correlated_evaluation_embedding_scaled_by_M5": "exact_small_oracles",
    "row_evaluation_embedding_scaled_by_M5": "exact_small_oracles",
    "finite_alias_inverse_operand_lost_prefactor": (
        "symbolic_whole_summand_replay_exact"
    ),
    "lost_inverse_summand_M5_cubed_prefactor": (
        "symbolic_whole_summand_replay_exact"
    ),
    "omit_Y2": "AST_Q_is_D2Y_plus_GammaYY_exact",
    "binder_GHY_H_uses_integration_domain": (
        "FrechetRowV1_schema_scope_capture_validation"
    ),
    "xi_D2_slot_mistyped_as_acceleration": (
        "FrechetRowV1_schema_scope_capture_validation"
    ),
    "row_unknown_rehashed_opcode": (
        "FrechetRowV1_schema_scope_capture_validation"
    ),
    "row_extra_rehashed_metadata": (
        "FrechetRowV1_schema_scope_capture_validation"
    ),
    "fake_source_span_rehashed": "FrechetRowV1_component_collection_exact",
    "row_ordinal_999": "FrechetRowV1_component_collection_exact",
    "row_duplicate_ordinal": "FrechetRowV1_component_collection_exact",
    "row_plus_variation_to_minus": "FrechetRowV1_component_collection_exact",
    "row_plus_jet_to_minus": "FrechetRowV1_component_collection_exact",
    "row_GHY_outward_selector_to_M5": (
        "FrechetRowV1_component_collection_exact"
    ),
    "integral_duplicate_minus_into_plus": (
        "FrechetRowV1_component_collection_exact"
    ),
}


def _literal_component_certificate(parsed: ParsedCharter) -> dict[str, Any]:
    return {
        "pass": bool(
            parsed.eh_denominator == 2
            and parsed.m5_power_bulk == 3
            and parsed.m5_power_ghy == 3
            and "M5^3*R_eps/2" in parsed.action["bulk_gauged"]
            and parsed.action["GHY"]
            == "S_GHY=M5^3*sum_eps int_Sigma sqrt(-gamma)*Theta_eps for outward normals"
        ),
        "components": list(COMPONENTS),
        "EH_capture": {"M5_power": parsed.m5_power_bulk, "denominator": parsed.eh_denominator},
        "GHY_capture": {"M5_power": parsed.m5_power_ghy, "denominator": 1},
        "scope": "four literal component occurrences only; coordinate meanings come from the separately pinned semantic completion",
    }


def _tangent_word_certificate(program: Program) -> dict[str, Any]:
    expected: dict[str, tuple[str, tuple[str, ...]]] = {}
    expected_types: dict[str, str] = {}
    for side in ("plus", "minus"):
        expected.update(
            {
                f"g_{side}": (f"H_{side}", ()),
                f"g1_{side}": (f"H_{side}", ("A",)),
                f"g2_{side}": (f"H_{side}", ("A", "B")),
                f"Y_{side}": (f"xi_{side}", ()),
                f"Y1_{side}": (f"xi_{side}", ("mu",)),
                f"Y2_{side}": (f"xi_{side}", ("mu", "nu")),
            }
        )
        expected_types.update(
            {
                f"g_{side}": METRIC5.name,
                f"g1_{side}": METRIC1JET5.name,
                f"g2_{side}": METRIC2JET5.name,
                f"Y_{side}": MAP5.name,
                f"Y1_{side}": MAP1.name,
                f"Y2_{side}": MAP2.name,
            }
        )
    observed = {
        key: (value.label, value.derivative_word)
        for key, value in sorted(program.tangents.items())
    }
    observed_types = {
        key: value.type_tag.name for key, value in sorted(program.tangents.items())
    }
    return {
        "pass": observed == expected and observed_types == expected_types,
        "ordered_words_preserved": observed == expected,
        "variation_jet_types_preserved": observed_types == expected_types,
        "observed_types": observed_types,
        "observed": {
            key: {"variation_component": label, "word": list(word)}
            for key, (label, word) in observed.items()
        },
    }


def _build_core(
    parsed: ParsedCharter,
    green_form: Mapping[str, Any],
    mutation: str | None,
) -> dict[str, Any]:
    if mutation is not None and mutation not in MANDATORY_MUTANTS:
        raise GravityFrechetError(f"unknown mutation {mutation}")
    semantic_completion = _semantic_completion_snapshot(mutation)
    semantic_completion_hash = _canonical_sha256(semantic_completion)
    program = build_program(parsed, mutation)
    manifest = _program_manifest(program)
    program_hash = _canonical_sha256(manifest)
    derivative = _derivative_certificate(program, mutation)
    transparency = _transparency_certificate(program)
    normal_theta = _normal_theta_certificate(program, semantic_completion)
    literal = _literal_component_certificate(parsed)
    words = _tangent_word_certificate(program)
    oracles = exact_oracles(program, derivative)
    brown_york = _fixed_embedding_brown_york_subcertificate(
        program, derivative, green_form
    )
    required_checks = {
        "literal_four_component_binding": literal["pass"],
        "semantic_completion_pin": (
            semantic_completion_hash == EXPECTED_SEMANTIC_COMPLETION_SHA256
        ),
        "typed_action_AST_pin": program_hash == EXPECTED_PROGRAM_SHA256,
        "declared_denotational_primitive_inventory": transparency["pass"],
        "cofactor_unit_outward_normal_and_Theta_minus_nQ": normal_theta["pass"],
        "ordered_holonomic_tangent_words": words["pass"],
        "nilpotent_dual_equals_reverse_Frechet_exact": derivative[
            "raw_dual_equals_reverse_pass"
        ],
        "FrechetRowV1_schema_scope_capture_validation": derivative[
            "FrechetRowV1_schema_and_binder_pass"
        ],
        "FrechetRowV1_component_collection_exact": derivative[
            "FrechetRowV1_component_collection_pass"
        ],
        "semantic_derivative_pin": (
            derivative["derivatives_sha256"] == EXPECTED_DERIVATIVES_SHA256
        ),
        "FrechetRowV1_export_pin": (
            derivative["FrechetRowV1_rows_sha256"] == EXPECTED_FRECHET_ROWS_SHA256
        ),
        "AST_literal_EH_GHY_prefactors_exact": oracles[
            "literal_action_prefactors"
        ]["pass"],
        "literal_exterior_M5_polynomial_exact": oracles[
            "literal_exterior_M5_polynomial"
        ]["pass"],
        "AST_Q_is_D2Y_plus_GammaYY_exact": oracles[
            "covariant_acceleration_composition"
        ]["pass"],
        "generated_derivative_primitive_inventory": oracles[
            "derivative_primitive_inventory"
        ]["pass"],
        "symbolic_whole_summand_replay_exact": oracles[
            "symbolic_whole_summand_replay"
        ]["pass"],
        "exact_small_oracles": _oracles_pass(oracles),
    }
    return {
        "semantic_completion": semantic_completion,
        "semantic_completion_sha256": semantic_completion_hash,
        "program": program,
        "program_manifest": manifest,
        "program_sha256": program_hash,
        "literal": literal,
        "transparency": transparency,
        "normal_theta": normal_theta,
        "tangent_words": words,
        "derivative": derivative,
        "oracles": oracles,
        "Brown_York": brown_york,
        "required_checks": required_checks,
        "ready": all(required_checks.values()),
    }


def _mutant_certificate(
    parsed: ParsedCharter,
    green_form: Mapping[str, Any],
) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for mutation in MANDATORY_MUTANTS:
        core = _build_core(parsed, green_form, mutation)
        failed = sorted(key for key, value in core["required_checks"].items() if not value)
        required_surface = MUTANT_REQUIRED_FAILURE_SURFACES.get(mutation)
        rows[mutation] = {
            "killed": not core["ready"],
            "required_semantic_failure_surface": required_surface,
            "required_semantic_failure_observed": (
                required_surface is None or required_surface in failed
            ),
            "failed_required_checks": failed,
            "program_sha256": core["program_sha256"],
            "derivatives_sha256": core["derivative"]["derivatives_sha256"],
            "FrechetRowV1_rows_sha256": core["derivative"]["FrechetRowV1_rows_sha256"],
            "dual_equals_reverse": core["derivative"]["raw_dual_equals_reverse_pass"],
            "FrechetRowV1_schema_and_binder_pass": core["derivative"][
                "FrechetRowV1_schema_and_binder_pass"
            ],
            "FrechetRowV1_component_collection_pass": core["derivative"][
                "FrechetRowV1_component_collection_pass"
            ],
        }
    return {
        "pass": set(rows) == set(MANDATORY_MUTANTS)
        and all(row["killed"] for row in rows.values())
        and all(row["required_semantic_failure_observed"] for row in rows.values()),
        "required_inventory": list(MANDATORY_MUTANTS),
        "rows": rows,
    }


def _public_derivative(
    certificate: Mapping[str, Any],
    *,
    inverse_volume_bridge_pass: bool,
    symbolic_whole_summand_pass: bool,
) -> dict[str, Any]:
    public = {
        key: value
        for key, value in certificate.items()
        if key not in {"forward_derivatives", "reverse_derivatives"}
    }
    public["traversal_and_row_consistency_pass"] = public["pass"]
    public["inverse_volume_local_denotation_bridge_pass"] = bool(
        inverse_volume_bridge_pass
    )
    public["symbolic_whole_summand_replay_pass"] = bool(
        symbolic_whole_summand_pass
    )
    public["pass"] = bool(
        public["pass"]
        and inverse_volume_bridge_pass
        and symbolic_whole_summand_pass
    )
    return public


def build_report(mutation: str | None = None) -> dict[str, Any]:
    dependency, action, green_form = certify_v52_dependency()
    parsed = parse_charter(action)
    core = _build_core(parsed, green_form, mutation)
    mutants = (
        _mutant_certificate(parsed, green_form)
        if mutation is None
        else {
            "pass": False,
            "required_inventory": list(MANDATORY_MUTANTS),
            "rows": {},
            "scope": "mutant-of-mutant recursion intentionally disabled",
        }
    )
    checks = {
        **core["required_checks"],
        "mandatory_mutants_rejected": mutants["pass"],
    }
    all_checks = all(checks.values())
    decision = {
        "literal_v5_2_EH_plus_minus_GHY_plus_minus_byte_bound_pass": all_checks,
        "gravity_semantic_completion_pinned_pass": all_checks,
        "typed_gravity_action_AST_with_declared_primitives_pass": all_checks,
        "self_contained_gravity_action_AST_pass": False,
        "cofactor_normal_outward_and_Theta_equals_minus_n_dot_Q_pass": all_checks,
        "EH_plus_minus_GHY_plus_minus_raw_formal_AST_Frechet_pass": all_checks,
        "EH_plus_minus_GHY_plus_minus_raw_semantic_Frechet_pass": False,
        "nilpotent_dual_equals_reverse_Frechet_exact_pass": all_checks,
        "independent_coordinate_Frechet_denotation_pass": False,
        "FrechetRowV1_four_component_export_pass": all_checks,
        "S10_component_validator_interoperability_pass": False,
        "fixed_embedding_xi_zero_normal_derivative_cancellation_pass": False,
        "fixed_embedding_xi_zero_Brown_York_pairing_exact_pass": False,
        "moving_embedding_shape_equation_pass": False,
        "two_sided_EH_GHY_full_Green_pairing_exact_pass": False,
        "all_twenty_components_semantic_Frechet_pass": False,
        "full_classical_variational_principle_pass": False,
        "C1_same_action_certificate_pass": False,
        "N1_nonlinear_gravity_certificate_pass": False,
        "promotion_or_publication_authorized": False,
    }
    return {
        "schema": SCHEMA,
        "title": "EH plus/minus and GHY plus/minus typed formal Frechet infrastructure gate",
        "status": "READY" if all_checks and mutation is None else "NOT_READY",
        "mutation": mutation,
        "dependency_certificate": dependency,
        "literal_component_certificate": core["literal"],
        "semantic_completion": core["semantic_completion"],
        "semantic_completion_sha256": core["semantic_completion_sha256"],
        "expected_semantic_completion_sha256": EXPECTED_SEMANTIC_COMPLETION_SHA256,
        "gravity_action_AST": core["program_manifest"],
        "gravity_action_AST_sha256": core["program_sha256"],
        "expected_gravity_action_AST_sha256": EXPECTED_PROGRAM_SHA256,
        "transparent_AST_certificate": core["transparency"],
        "cofactor_outward_normal_Theta_certificate": core["normal_theta"],
        "ordered_tangent_word_certificate": core["tangent_words"],
        "exact_raw_Frechet_certificate": _public_derivative(
            core["derivative"],
            inverse_volume_bridge_pass=core["oracles"][
                "derivative_AST_inverse_volume_bridge"
            ]["pass"],
            symbolic_whole_summand_pass=core["oracles"][
                "symbolic_whole_summand_replay"
            ]["pass"],
        ),
        "exact_small_oracles": core["oracles"],
        "fixed_embedding_xi_zero_Brown_York_subcertificate": core["Brown_York"],
        "mandatory_mutant_certificate": mutants,
        "checks": {**checks, "all": all_checks},
        "decision": decision,
        "evidence_boundary": {
            "proved": (
                "conditional on the byte-pinned declared primitive registry, the four raw "
                "density ASTs have two-traversal formal Frechet agreement and locally neutral "
                "FrechetRowV1 exports with bundle-derived binders; two finite exact rational "
                "5D/4D witnesses independently check the inverse, volume and moving-evaluation "
                "subexpressions by component, ordinal, path and route"
            ),
            "not_proved": (
                "independent executable coordinate denotation of every primitive, S10 validator "
                "interoperability, Palatini boundary current, EH+GHY normal-derivative cancellation, "
                "Brown--York remainder, shape equation, two-sided Green identity, full20, C1, or N1"
            ),
            "numerical_tolerance_used": False,
            "finite_exact_witnesses_used": True,
            "sampled_identity_used": False,
            "finite_witnesses_are_not_a_universal_identity": True,
            "formal_identity_basis": (
                "exact canonical AST equality of two production traversals plus an "
                "independent symbolic whole-summand local-rule replay; finite witnesses "
                "only test local rule denotations and do not establish identity"
            ),
            "artifact_written": False,
        },
    }


def main() -> None:
    print(json.dumps(_jsonable(build_report()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
