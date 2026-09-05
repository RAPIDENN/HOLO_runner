#!/usr/bin/env python3
"""Exact, bounded BRST-nilpotency candidate for the canonical solid action.

The calculation in this file is deliberately narrower than a C2 certificate.
It implements a free supercommutative Q-algebra and checks the kinematic
nilpotency of one explicit candidate convention on order-zero generators.  The
two bulk sides are evaluated in disjoint namespaces and in sequence.  Ambient,
world-volume, and target-line derivatives use lazy, unbounded symmetric jet
labels; order two is merely the largest order visited by these particular
checks, never a truncation rule.

The canonical action charter and the preceding inventory source/test pair are
read as pinned bytes.  The inventory module is neither imported nor executed,
and none of its formula strings is used as an algebra oracle.  No artifact is
written.  In particular this gate does not choose the side-ghost quotient or
the khronon quotient, prove action invariance or gluing tangency, construct a
gauge fermion or domain, or promote C2, C3, P3, P4, B4, or B5.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

INVENTORY_SOURCE = HERE / "derive_one_omega_solid_c2a_brst_algebra_inventory_gate.py"
INVENTORY_TEST = HERE / "test_one_omega_solid_c2a_brst_algebra_inventory_gate.py"
CHARTER_ARTIFACT = HERE / "artifacts" / "one_omega_action_charter_gate.json"

INVENTORY_SOURCE_SHA256 = (
    "56548e9c9e699ba93298e927e61f3df0fdfbc83a2bf03d626d3074f7a3de4e23"
)
INVENTORY_TEST_SHA256 = (
    "ed11cc3fc3c54fde2f5cb88aa61bc16b93d1a54f98ec03dae11651e6d1acc6ab"
)
CHARTER_ARTIFACT_SHA256 = (
    "b718cb68934a665cf0a7b89fafffcf2b9ebb2c0bb94c9386ff64f34d91a2e0ef"
)
CHARTER_ACTION_DIGEST = (
    "93105331d9da311afa7845f9939dbd60617b929ae9ede23286fa26bedaa815c1"
)
CHARTER_SCHEMA = "holo.one-omega-action-charter-gate.v1"
CHARTER_ROUTE = "canonical_one_Omega_backreacted_wall_with_rank_full_solid_v1"

SCHEMA = "holo.one-omega-solid-c2a-graded-nilpotency-gate.v1"
D_BULK = 5
D_WORLDVOLUME = 4
SIDES = ("plus", "minus")
OBSERVED_CERTIFICATE_JET_ORDER = 2


INVENTORY_FORMULA_ROWS = [
    {"field": "g_epsilon", "candidate": "s g_epsilon=-L_c_epsilon g_epsilon"},
    {"field": "Omega_epsilon", "candidate": "s Omega_epsilon=-L_c_epsilon Omega_epsilon"},
    {"field": "phi_epsilon^a", "candidate": "s phi_epsilon^a=-L_c_epsilon phi_epsilon^a"},
    {"field": "c_epsilon^M", "candidate": "s c_epsilon^M=-c_epsilon^N partial_N c_epsilon^M"},
    {"field": "Y_epsilon^M", "candidate": "s Y_epsilon^M=c_epsilon^M(Y_epsilon)-eta^mu partial_mu Y_epsilon^M"},
    {"field": "X^a", "candidate": "s X^a=-eta^mu partial_mu X^a"},
    {"field": "eta^mu", "candidate": "s eta^mu=-eta^nu partial_nu eta^mu"},
    {"field": "T", "candidate": "s T=-eta^mu partial_mu T+kappa(T)"},
    {"field": "kappa(t)", "candidate": "s kappa(t)=-kappa(t) partial_t kappa(t)"},
]
INVENTORY_FORMULA_ROWS_SHA256 = (
    "93dd5a5775bde0ddf445fb88f9ba164bad05108c7302fec55c5360889241b155"
)


RULE_BINDING = {
    "bulk_ghost": "s c_epsilon^M=-c_epsilon^N D_N c_epsilon^M",
    "bulk_metric": (
        "s g_epsilon_MN=-c_epsilon^P D_P g_epsilon_MN"
        "-(D_M c_epsilon^P)g_epsilon_PN"
        "-(D_N c_epsilon^P)g_epsilon_MP"
    ),
    "bulk_scalar_Omega": "s Omega_epsilon=-c_epsilon^N D_N Omega_epsilon",
    "bulk_scalar_phi": "s phi_epsilon^a=-c_epsilon^N D_N phi_epsilon^a",
    "brane_ghost": "s eta^mu=-eta^nu d_nu eta^mu",
    "solid_scalar": "s X^a=-eta^mu d_mu X^a",
    "embedding": (
        "s Y_epsilon^M=Ev_Y(c_epsilon^M)-eta^mu d_mu Y_epsilon^M"
    ),
    "khronon": "s T=-eta^mu d_mu T+Ev_T(kappa)",
    "target_ghost": "s kappa(t)=-kappa(t) d_t kappa(t)",
}

EVALUATION_BINDING = {
    "ambient_BRST_chain": (
        "s Ev_Y(c_I)=Ev_Y(s c_I)+(sY^P)Ev_Y(D_P c_I); sY is left"
    ),
    "ambient_total_derivative_chain": (
        "d_mu Ev_Y(c_I)=Y_mu^P Ev_Y(c_(I+P))"
    ),
    "target_BRST_chain": (
        "s Ev_T(kappa_r)=Ev_T(s kappa_r)+(sT)Ev_T(kappa_(r+1)); sT is left"
    ),
    "target_total_derivative_chain": (
        "d_mu Ev_T(kappa_r)=T_mu Ev_T(kappa_(r+1))"
    ),
    "graded_Leibniz": "s(uv)=s(u)v+(-1)^|u|u s(v)",
    "even_prolongation": (
        "[s,D_M]=[s,d_mu]=[s,d_t]=0 on modeled support-needed families"
    ),
}


class SolidC2AGradedError(ValueError):
    """A pinned input, algebra invariant, or bounded claim failed closed."""


def _canonical_json_digest(value: Any) -> str:
    try:
        raw = json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SolidC2AGradedError(f"cannot canonicalize value: {exc}") from exc
    return hashlib.sha256(raw).hexdigest()


RULE_BINDING_SHA256 = _canonical_json_digest(
    {"candidate_rules": RULE_BINDING, "evaluation_rules": EVALUATION_BINDING}
)
if _canonical_json_digest(INVENTORY_FORMULA_ROWS) != INVENTORY_FORMULA_ROWS_SHA256:
    raise SolidC2AGradedError("literal nine-row inventory formula binding drift")


def _read_pinned_bytes(path: Any, expected_sha256: str, label: str) -> bytes:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SolidC2AGradedError(f"cannot read {label}: {exc}") from exc
    if type(raw) is not bytes:
        raise SolidC2AGradedError(f"{label} read_bytes() must return exact bytes")
    observed = hashlib.sha256(raw).hexdigest()
    if observed != expected_sha256:
        raise SolidC2AGradedError(
            f"{label} byte hash mismatch: {observed} != {expected_sha256}"
        )
    return raw


def _decode_strict_json(raw: bytes) -> dict[str, Any]:
    if type(raw) is not bytes:
        raise SolidC2AGradedError("strict JSON input must have exact type bytes")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if type(key) is not str or key in result:
                raise SolidC2AGradedError(f"duplicate or non-string JSON key: {key!r}")
            result[key] = value
        return result

    def reject_nonfinite(token: str) -> None:
        raise SolidC2AGradedError(f"non-finite JSON constant: {token}")

    def parse_finite_float(token: str) -> float:
        value = float(token)
        if not math.isfinite(value):
            raise SolidC2AGradedError(f"JSON float overflows finite range: {token}")
        return value

    try:
        payload = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_nonfinite,
            parse_float=parse_finite_float,
        )
    except SolidC2AGradedError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SolidC2AGradedError(f"invalid UTF-8 JSON: {exc}") from exc
    if type(payload) is not dict:
        raise SolidC2AGradedError("charter JSON root must have exact type dict")
    return payload


def _require_exact(observed: Any, expected: Any, path: str) -> None:
    if type(observed) is not type(expected):
        raise SolidC2AGradedError(
            f"{path} type mismatch: {type(observed).__name__} != "
            f"{type(expected).__name__}"
        )
    if type(expected) is dict:
        if set(observed) != set(expected):
            raise SolidC2AGradedError(f"{path} key inventory mismatch")
        for key in expected:
            _require_exact(observed[key], expected[key], f"{path}.{key}")
    elif type(expected) is list:
        if len(observed) != len(expected):
            raise SolidC2AGradedError(f"{path} length mismatch")
        for index, item in enumerate(expected):
            _require_exact(observed[index], item, f"{path}[{index}]")
    elif observed != expected:
        raise SolidC2AGradedError(f"{path} value mismatch")


def validate_charter_semantics(payload: Any) -> None:
    """Independently bind only the charter semantics this calculation consumes."""

    if type(payload) is not dict:
        raise SolidC2AGradedError("charter payload must have exact type dict")
    _require_exact(payload.get("schema"), CHARTER_SCHEMA, "schema")
    action = payload.get("action_charter")
    if type(action) is not dict:
        raise SolidC2AGradedError("action_charter must have exact type dict")
    if _canonical_json_digest(action) != CHARTER_ACTION_DIGEST:
        raise SolidC2AGradedError("canonical action digest mismatch")
    _require_exact(action.get("route_id"), CHARTER_ROUTE, "action_charter.route_id")

    selection = action.get("selection")
    if type(selection) is not dict:
        raise SolidC2AGradedError("action_charter.selection must be a dict")
    for key, expected in {
        "bifundamental_solder_selected": False,
        "bulk_compensator": "Omega",
        "bulk_compensator_count": 1,
        "canonical_genealogy_selected_for_C1_and_N1": True,
        "fixed_external_triad_selected": False,
        "old_P3_gate_automatically_updated": False,
        "solder_route": "three brane Stueckelberg solid scalars X^a",
    }.items():
        _require_exact(selection.get(key), expected, f"action_charter.selection.{key}")

    fields = action.get("independent_fields")
    if type(fields) is not dict:
        raise SolidC2AGradedError("action_charter.independent_fields must be a dict")
    for key in (
        "classical_FP_or_BRST_fields",
        "independent_auxiliary_fields",
        "independent_internal_gauge_fields",
    ):
        _require_exact(fields.get(key), [], f"action_charter.independent_fields.{key}")

    breaking = action.get("symmetry_breaking_pattern")
    if type(breaking) is not dict:
        raise SolidC2AGradedError("symmetry_breaking_pattern must be a dict")
    _require_exact(
        breaking.get("relative_SO3_is_gauged"),
        False,
        "action_charter.symmetry_breaking_pattern.relative_SO3_is_gauged",
    )
    domains = action.get("domains")
    if type(domains) is not dict:
        raise SolidC2AGradedError("action_charter.domains must be a dict")
    _require_exact(
        domains.get("BRST_closed_boundary_domain_selected"),
        False,
        "action_charter.domains.BRST_closed_boundary_domain_selected",
    )

    decision = payload.get("decision")
    if type(decision) is not dict:
        raise SolidC2AGradedError("decision must be a dict")
    for key, expected in {
        "C1_ACTION_pass": True,
        "N1_ACTION_pass": True,
        "C2_BRST_pass": False,
        "C3_DOMAIN_pass": False,
        "C4_HESSIAN_pass": False,
        "C5_JACOBIANS_pass": False,
        "C6_ZERO_MODES_pass": False,
        "C7_REGULATOR_pass": False,
        "C8_CONTOUR_pass": False,
        "C9_REDUCTION_pass": False,
        "C10_INDEPENDENCE_UNITARITY_pass": False,
        "P3_complete_gauge_fixed_unitary_determinant_pass": False,
        "P4_full_same_action_pass": False,
        "B4_pass": False,
        "B5_pass": False,
        "publication_authorized": False,
    }.items():
        _require_exact(decision.get(key), expected, f"decision.{key}")


def load_pinned_inputs() -> dict[str, Any]:
    """Read each immutable input once; never import or execute the inventory pair."""

    inventory_source = _read_pinned_bytes(
        INVENTORY_SOURCE, INVENTORY_SOURCE_SHA256, "inventory source"
    )
    inventory_test = _read_pinned_bytes(
        INVENTORY_TEST, INVENTORY_TEST_SHA256, "inventory test"
    )
    charter_raw = _read_pinned_bytes(
        CHARTER_ARTIFACT, CHARTER_ARTIFACT_SHA256, "action charter"
    )
    charter = _decode_strict_json(charter_raw)
    validate_charter_semantics(charter)
    return {
        "inventory_source_bytes": len(inventory_source),
        "inventory_test_bytes": len(inventory_test),
        "charter_bytes": len(charter_raw),
        "charter": charter,
    }


@dataclass(frozen=True, order=True)
class GeneratorSpec:
    name: str
    parity: int
    family: str
    side: str
    component: tuple[int | str, ...]
    jet: tuple[int, ...]


@dataclass(frozen=True, order=True)
class Monomial:
    even: tuple[tuple[str, int], ...]
    odd: tuple[str, ...]


ZERO_MONOMIAL = Monomial((), ())


class Polynomial:
    """A sparse polynomial over Q in one explicitly supplied algebra."""

    __slots__ = ("algebra", "terms")

    def __init__(
        self,
        algebra: "SparseSuperAlgebra",
        terms: dict[Monomial, Fraction] | None = None,
    ) -> None:
        self.algebra = algebra
        self.terms = {
            monomial: coefficient
            for monomial, coefficient in (terms or {}).items()
            if coefficient
        }

    @classmethod
    def scalar(cls, algebra: "SparseSuperAlgebra", value: int | Fraction) -> "Polynomial":
        coefficient = Fraction(value)
        return cls(algebra, {} if not coefficient else {ZERO_MONOMIAL: coefficient})

    def _coerce(self, other: int | Fraction | "Polynomial") -> "Polynomial":
        if isinstance(other, Polynomial):
            if other.algebra is not self.algebra:
                raise SolidC2AGradedError("cannot mix distinct algebra instances")
            return other
        return Polynomial.scalar(self.algebra, other)

    def __add__(self, other: int | Fraction | "Polynomial") -> "Polynomial":
        rhs = self._coerce(other)
        terms = dict(self.terms)
        for monomial, coefficient in rhs.terms.items():
            terms[monomial] = terms.get(monomial, Fraction(0)) + coefficient
            if not terms[monomial]:
                del terms[monomial]
        return Polynomial(self.algebra, terms)

    def __radd__(self, other: int | Fraction | "Polynomial") -> "Polynomial":
        return self + other

    def __neg__(self) -> "Polynomial":
        return Polynomial(self.algebra, {m: -c for m, c in self.terms.items()})

    def __sub__(self, other: int | Fraction | "Polynomial") -> "Polynomial":
        return self + (-self._coerce(other))

    def __rsub__(self, other: int | Fraction | "Polynomial") -> "Polynomial":
        return self._coerce(other) - self

    def __mul__(self, other: int | Fraction | "Polynomial") -> "Polynomial":
        rhs = self._coerce(other)
        terms: dict[Monomial, Fraction] = {}
        for left_monomial, left_coefficient in self.terms.items():
            for right_monomial, right_coefficient in rhs.terms.items():
                product = self.algebra.multiply_monomials(
                    left_monomial, right_monomial
                )
                if product is None:
                    continue
                sign, monomial = product
                coefficient = left_coefficient * right_coefficient * sign
                terms[monomial] = terms.get(monomial, Fraction(0)) + coefficient
                if not terms[monomial]:
                    del terms[monomial]
        return Polynomial(self.algebra, terms)

    def __rmul__(self, other: int | Fraction | "Polynomial") -> "Polynomial":
        return self * other

    def __pow__(self, exponent: int) -> "Polynomial":
        if type(exponent) is not int or exponent < 0:
            raise SolidC2AGradedError("polynomial exponent must be a nonnegative int")
        result = Polynomial.scalar(self.algebra, 1)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    @property
    def is_zero(self) -> bool:
        return not self.terms

    def require_homogeneous(self, expected_parity: int, label: str) -> None:
        if expected_parity not in (0, 1):
            raise SolidC2AGradedError("expected parity must be zero or one")
        for monomial in self.terms:
            parity = len(monomial.odd) % 2
            if parity != expected_parity:
                raise SolidC2AGradedError(
                    f"{label} is not homogeneous of parity {expected_parity}"
                )


class SparseSuperAlgebra:
    """Sparse free supercommutative algebra with a deliberate commute mutant."""

    def __init__(self, *, odd_mode: str = "exterior") -> None:
        if odd_mode not in {"exterior", "commuting_mutant"}:
            raise SolidC2AGradedError("unknown odd multiplication mode")
        self.odd_mode = odd_mode
        self.specs: dict[str, GeneratorSpec] = {}

    def generator(self, spec: GeneratorSpec) -> Polynomial:
        existing = self.specs.get(spec.name)
        if existing is not None and existing != spec:
            raise SolidC2AGradedError(f"generator metadata collision: {spec.name}")
        self.specs[spec.name] = spec
        if spec.parity == 0:
            monomial = Monomial(((spec.name, 1),), ())
        elif spec.parity == 1:
            monomial = Monomial((), (spec.name,))
        else:
            raise SolidC2AGradedError("generator parity must be zero or one")
        return Polynomial(self, {monomial: Fraction(1)})

    def multiply_monomials(
        self, left: Monomial, right: Monomial
    ) -> tuple[int, Monomial] | None:
        even: dict[str, int] = dict(left.even)
        for name, power in right.even:
            even[name] = even.get(name, 0) + power

        if self.odd_mode == "exterior":
            if set(left.odd).intersection(right.odd):
                return None
            inversions = sum(
                1 for left_name in left.odd for right_name in right.odd
                if left_name > right_name
            )
            sign = -1 if inversions % 2 else 1
        else:
            sign = 1
        odd = tuple(sorted(left.odd + right.odd))
        return sign, Monomial(tuple(sorted(even.items())), odd)

    def derivation(
        self,
        polynomial: Polynomial,
        on_generator: Callable[[GeneratorSpec], Polynomial],
        *,
        operator_parity: int,
    ) -> Polynomial:
        if polynomial.algebra is not self:
            raise SolidC2AGradedError("derivation received a foreign polynomial")
        result = Polynomial.scalar(self, 0)
        for monomial, coefficient in polynomial.terms.items():
            factors: list[str] = []
            for name, power in monomial.even:
                factors.extend([name] * power)
            factors.extend(monomial.odd)
            for index, name in enumerate(factors):
                prefix = Polynomial.scalar(self, coefficient)
                prefix_parity = 0
                for prefix_name in factors[:index]:
                    prefix = prefix * self.generator(self.specs[prefix_name])
                    prefix_parity ^= self.specs[prefix_name].parity
                varied = on_generator(self.specs[name])
                suffix = Polynomial.scalar(self, 1)
                for suffix_name in factors[index + 1 :]:
                    suffix = suffix * self.generator(self.specs[suffix_name])
                sign = -1 if operator_parity * prefix_parity % 2 else 1
                result = result + sign * prefix * varied * suffix
        return result


def _unit_multiindex(dimension: int, axis: int) -> tuple[int, ...]:
    if type(dimension) is not int or type(axis) is not int:
        raise SolidC2AGradedError("multiindex dimension and axis must be ints")
    if dimension <= 0 or not 0 <= axis < dimension:
        raise SolidC2AGradedError("multiindex axis out of range")
    return tuple(1 if index == axis else 0 for index in range(dimension))


def _increment_multiindex(index: tuple[int, ...], axis: int) -> tuple[int, ...]:
    """Lazy unbounded symmetric multiindex factory; it never truncates jets."""

    if type(index) is not tuple or any(type(item) is not int or item < 0 for item in index):
        raise SolidC2AGradedError("jet multiindex must be a tuple of nonnegative ints")
    if not 0 <= axis < len(index):
        raise SolidC2AGradedError("jet axis out of range")
    return tuple(item + (position == axis) for position, item in enumerate(index))


def _zero_multiindex(dimension: int) -> tuple[int, ...]:
    return (0,) * dimension


def _jet_suffix(index: tuple[int, ...]) -> str:
    return ".".join(str(value) for value in index)


class CandidateModel:
    """One exact rule set in the lazy jet-labelled free algebra."""

    def __init__(
        self,
        *,
        mutations: Iterable[str] = (),
        odd_mode: str = "exterior",
    ) -> None:
        self.mutations = frozenset(mutations)
        self.algebra = SparseSuperAlgebra(odd_mode=odd_mode)
        self._s_cache: dict[str, Polynomial] = {}
        self.access_log: list[str] = []

    def _make(
        self,
        family: str,
        *,
        parity: int,
        side: str = "shared",
        component: tuple[int | str, ...] = (),
        jet: tuple[int, ...] = (),
    ) -> Polynomial:
        component_text = ",".join(str(value) for value in component) or "_"
        name = f"{family}[{side};{component_text}]@{_jet_suffix(jet)}"
        generator = self.algebra.generator(
            GeneratorSpec(name, parity, family, side, component, jet)
        )
        self.access_log.append(name)
        return generator

    def c(self, side: str, component: int, jet: tuple[int, ...] | None = None) -> Polynomial:
        return self._make(
            "c", parity=1, side=side, component=(component,),
            jet=_zero_multiindex(D_BULK) if jet is None else jet,
        )

    def scalar(
        self,
        side: str,
        species: str,
        component: int,
        jet: tuple[int, ...] | None = None,
    ) -> Polynomial:
        return self._make(
            "bulk_scalar", parity=0, side=side, component=(species, component),
            jet=_zero_multiindex(D_BULK) if jet is None else jet,
        )

    def metric(
        self,
        side: str,
        first: int,
        second: int,
        jet: tuple[int, ...] | None = None,
    ) -> Polynomial:
        low, high = sorted((first, second))
        return self._make(
            "g", parity=0, side=side, component=(low, high),
            jet=_zero_multiindex(D_BULK) if jet is None else jet,
        )

    def eta(self, component: int, jet: tuple[int, ...] | None = None) -> Polynomial:
        return self._make(
            "eta", parity=1, component=(component,),
            jet=_zero_multiindex(D_WORLDVOLUME) if jet is None else jet,
        )

    def X(self, component: int, jet: tuple[int, ...] | None = None) -> Polynomial:
        return self._make(
            "X", parity=0, component=(component,),
            jet=_zero_multiindex(D_WORLDVOLUME) if jet is None else jet,
        )

    def Y(
        self, side: str, component: int, jet: tuple[int, ...] | None = None
    ) -> Polynomial:
        return self._make(
            "Y", parity=0, side=side, component=(component,),
            jet=_zero_multiindex(D_WORLDVOLUME) if jet is None else jet,
        )

    def T(self, jet: tuple[int, ...] | None = None) -> Polynomial:
        return self._make(
            "T", parity=0,
            jet=_zero_multiindex(D_WORLDVOLUME) if jet is None else jet,
        )

    def kappa(self, order: int = 0) -> Polynomial:
        return self._make("kappa", parity=1, component=(), jet=(order,))

    def evaluated_c(
        self, side: str, component: int, ambient_jet: tuple[int, ...] | None = None
    ) -> Polynomial:
        return self._make(
            "EvY_c", parity=1, side=side, component=(component,),
            jet=_zero_multiindex(D_BULK) if ambient_jet is None else ambient_jet,
        )

    def evaluated_kappa(self, order: int = 0) -> Polynomial:
        return self._make("EvT_kappa", parity=1, component=(), jet=(order,))

    def local_kappa(
        self, jet: tuple[int, ...] | None = None
    ) -> Polynomial:
        return self._make(
            "local_kappa", parity=1,
            jet=_zero_multiindex(D_WORLDVOLUME) if jet is None else jet,
        )

    def local_C(
        self,
        side: str,
        component: int,
        jet: tuple[int, ...] | None = None,
    ) -> Polynomial:
        return self._make(
            "local_C",
            parity=1,
            side=side,
            component=(component,),
            jet=_zero_multiindex(D_WORLDVOLUME) if jet is None else jet,
        )

    @staticmethod
    def _only_spec(polynomial: Polynomial) -> GeneratorSpec:
        if len(polynomial.terms) != 1:
            raise SolidC2AGradedError("expected one generator monomial")
        monomial, coefficient = next(iter(polynomial.terms.items()))
        if coefficient != 1 or len(monomial.even) + len(monomial.odd) != 1:
            raise SolidC2AGradedError("expected one unit generator")
        name = monomial.even[0][0] if monomial.even else monomial.odd[0]
        return polynomial.algebra.specs[name]

    def _D_bulk_generator(self, spec: GeneratorSpec, axis: int) -> Polynomial:
        if spec.family not in {"c", "bulk_scalar", "g"} or len(spec.jet) != D_BULK:
            raise SolidC2AGradedError(f"D_bulk unsupported on {spec.name}")
        jet = _increment_multiindex(spec.jet, axis)
        return self._make(
            spec.family,
            parity=spec.parity,
            side=spec.side,
            component=spec.component,
            jet=jet,
        )

    def D_bulk(self, polynomial: Polynomial, axis: int) -> Polynomial:
        return self.algebra.derivation(
            polynomial,
            lambda spec: self._D_bulk_generator(spec, axis),
            operator_parity=0,
        )

    def _D_sigma_generator(self, spec: GeneratorSpec, axis: int) -> Polynomial:
        if spec.family in {"eta", "X", "Y", "T", "local_kappa", "local_C"}:
            return self._make(
                spec.family,
                parity=spec.parity,
                side=spec.side,
                component=spec.component,
                jet=_increment_multiindex(spec.jet, axis),
            )
        if spec.family == "EvY_c":
            component = int(spec.component[0])
            result = Polynomial.scalar(self.algebra, 0)
            for ambient in range(D_BULK):
                result += self.Y(
                    spec.side, ambient, _unit_multiindex(D_WORLDVOLUME, axis)
                ) * self.evaluated_c(
                    spec.side,
                    component,
                    _increment_multiindex(spec.jet, ambient),
                )
            return result
        if spec.family == "EvT_kappa":
            return self.T(_unit_multiindex(D_WORLDVOLUME, axis)) * self.evaluated_kappa(
                spec.jet[0] + 1
            )
        raise SolidC2AGradedError(f"d_sigma unsupported on {spec.name}")

    def D_sigma(self, polynomial: Polynomial, axis: int) -> Polynomial:
        return self.algebra.derivation(
            polynomial,
            lambda spec: self._D_sigma_generator(spec, axis),
            operator_parity=0,
        )

    def _D_target_generator(self, spec: GeneratorSpec) -> Polynomial:
        if spec.family != "kappa":
            raise SolidC2AGradedError(f"d_t unsupported on {spec.name}")
        return self.kappa(spec.jet[0] + 1)

    def D_target(self, polynomial: Polynomial) -> Polynomial:
        return self.algebra.derivation(
            polynomial, self._D_target_generator, operator_parity=0
        )

    def _prolong_bulk(self, polynomial: Polynomial, jet: tuple[int, ...]) -> Polynomial:
        result = polynomial
        for axis, count in enumerate(jet):
            for _ in range(count):
                result = self.D_bulk(result, axis)
        return result

    def _prolong_sigma(self, polynomial: Polynomial, jet: tuple[int, ...]) -> Polynomial:
        result = polynomial
        for axis, count in enumerate(jet):
            for _ in range(count):
                result = self.D_sigma(result, axis)
        return result

    def _prolong_target(self, polynomial: Polynomial, order: int) -> Polynomial:
        result = polynomial
        for _ in range(order):
            result = self.D_target(result)
        return result

    def _base_sc(self, side: str, component: int) -> Polynomial:
        if "sc_zero" in self.mutations:
            return Polynomial.scalar(self.algebra, 0)
        result = Polynomial.scalar(self.algebra, 0)
        for ambient in range(D_BULK):
            result += self.c(side, ambient) * self.c(
                side, component, _unit_multiindex(D_BULK, ambient)
            )
        return result if "sc_sign" in self.mutations else -result

    def _base_scalar(self, side: str, species: str, component: int) -> Polynomial:
        result = Polynomial.scalar(self.algebra, 0)
        for ambient in range(D_BULK):
            result -= self.c(side, ambient) * self.scalar(
                side,
                species,
                component,
                _unit_multiindex(D_BULK, ambient),
            )
        return result

    def _base_metric(self, side: str, first: int, second: int) -> Polynomial:
        result = Polynomial.scalar(self.algebra, 0)
        for ambient in range(D_BULK):
            result -= self.c(side, ambient) * self.metric(
                side,
                first,
                second,
                _unit_multiindex(D_BULK, ambient),
            )
            omit_first_here = (
                "omit_metric_first_leg" in self.mutations
                and tuple(sorted((first, second))) == (0, 1)
            )
            omit_second_here = (
                "omit_metric_second_leg" in self.mutations
                and tuple(sorted((first, second))) == (0, 1)
            )
            if not omit_first_here:
                result -= self.c(
                    side, ambient, _unit_multiindex(D_BULK, first)
                ) * self.metric(side, ambient, second)
            if not omit_second_here:
                result -= self.c(
                    side, ambient, _unit_multiindex(D_BULK, second)
                ) * self.metric(side, first, ambient)
        return result

    def _base_seta(self, component: int) -> Polynomial:
        if "seta_zero" in self.mutations:
            return Polynomial.scalar(self.algebra, 0)
        result = Polynomial.scalar(self.algebra, 0)
        for axis in range(D_WORLDVOLUME):
            result += self.eta(axis) * self.eta(
                component, _unit_multiindex(D_WORLDVOLUME, axis)
            )
        return result if "seta_sign" in self.mutations else -result

    def _base_X(self, component: int) -> Polynomial:
        result = Polynomial.scalar(self.algebra, 0)
        for axis in range(D_WORLDVOLUME):
            result -= self.eta(axis) * self.X(
                component, _unit_multiindex(D_WORLDVOLUME, axis)
            )
        return result

    def _base_Y(self, side: str, component: int) -> Polynomial:
        evaluated = (
            self.local_C(side, component)
            if "local_C_covariant" in self.mutations
            else self.evaluated_c(side, component)
        )
        if "wrong_Y_sign" in self.mutations:
            evaluated = -evaluated
        result = evaluated
        for axis in range(D_WORLDVOLUME):
            result -= self.eta(axis) * self.Y(
                side, component, _unit_multiindex(D_WORLDVOLUME, axis)
            )
        return result

    def _base_T(self) -> Polynomial:
        result = (
            self.local_kappa()
            if "local_kappa" in self.mutations
            else self.evaluated_kappa()
        )
        for axis in range(D_WORLDVOLUME):
            result -= self.eta(axis) * self.T(
                _unit_multiindex(D_WORLDVOLUME, axis)
            )
        return result

    def _base_skappa(self) -> Polynomial:
        if "skappa_zero" in self.mutations:
            return Polynomial.scalar(self.algebra, 0)
        result = self.kappa(0) * self.kappa(1)
        return result if "skappa_sign" in self.mutations else -result

    def _evaluate_bulk_ghost_polynomial(
        self, polynomial: Polynomial, side: str
    ) -> Polynomial:
        def replace(spec: GeneratorSpec) -> Polynomial:
            if spec.family != "c" or spec.side != side:
                raise SolidC2AGradedError("ambient evaluation received a foreign generator")
            return self.evaluated_c(side, int(spec.component[0]), spec.jet)

        return self._substitute_generators(polynomial, replace)

    def _evaluate_target_polynomial(self, polynomial: Polynomial) -> Polynomial:
        def replace(spec: GeneratorSpec) -> Polynomial:
            if spec.family != "kappa":
                raise SolidC2AGradedError("target evaluation received a foreign generator")
            return self.evaluated_kappa(spec.jet[0])

        return self._substitute_generators(polynomial, replace)

    def _substitute_generators(
        self,
        polynomial: Polynomial,
        replacement: Callable[[GeneratorSpec], Polynomial],
    ) -> Polynomial:
        result = Polynomial.scalar(self.algebra, 0)
        for monomial, coefficient in polynomial.terms.items():
            term = Polynomial.scalar(self.algebra, coefficient)
            for name, power in monomial.even:
                term *= replacement(self.algebra.specs[name]) ** power
            for name in monomial.odd:
                term *= replacement(self.algebra.specs[name])
            result += term
        return result

    def swap_bulk_sides(self, polynomial: Polynomial) -> Polynomial:
        """Apply the plus/minus label involution without identifying ghosts."""

        def replace(spec: GeneratorSpec) -> Polynomial:
            side = {"plus": "minus", "minus": "plus"}.get(spec.side, spec.side)
            return self._make(
                spec.family,
                parity=spec.parity,
                side=side,
                component=spec.component,
                jet=spec.jet,
            )

        return self._substitute_generators(polynomial, replace)

    def _s_evaluated_c(self, spec: GeneratorSpec) -> Polynomial:
        side = spec.side
        component = int(spec.component[0])
        ambient_variation = self._prolong_bulk(
            self._base_sc(side, component), spec.jet
        )
        result = self._evaluate_bulk_ghost_polynomial(ambient_variation, side)
        if "omit_c_evaluation" not in self.mutations:
            for ambient in range(D_BULK):
                # The sY factor is deliberately LEFT of the odd evaluated jet.
                evaluated_jet = self.evaluated_c(
                    side, component, _increment_multiindex(spec.jet, ambient)
                )
                if "evaluation_odd_order" in self.mutations:
                    result += evaluated_jet * self._base_Y(side, ambient)
                else:
                    result += self._base_Y(side, ambient) * evaluated_jet
        return result

    def _s_evaluated_kappa(self, spec: GeneratorSpec) -> Polynomial:
        target_variation = self._prolong_target(
            self._base_skappa(), spec.jet[0]
        )
        result = self._evaluate_target_polynomial(target_variation)
        if "omit_kappa_evaluation" not in self.mutations:
            evaluated_jet = self.evaluated_kappa(spec.jet[0] + 1)
            if "target_evaluation_odd_order" in self.mutations:
                result += evaluated_jet * self._base_T()
            else:
                result += self._base_T() * evaluated_jet
        return result

    def _base_local_covariant_ghost(
        self, side: str, component: tuple[int | str, ...], family: str
    ) -> Polynomial:
        result = Polynomial.scalar(self.algebra, 0)
        for axis in range(D_WORLDVOLUME):
            result -= self.eta(axis) * self._make(
                family,
                parity=1,
                side=side,
                component=component,
                jet=_unit_multiindex(D_WORLDVOLUME, axis),
            )
        return result

    def s_generator(self, spec: GeneratorSpec) -> Polynomial:
        self.access_log.append(spec.name)
        cached = self._s_cache.get(spec.name)
        if cached is not None:
            return cached
        if spec.family == "c":
            result = self._prolong_bulk(
                self._base_sc(spec.side, int(spec.component[0])), spec.jet
            )
        elif spec.family == "bulk_scalar":
            result = self._prolong_bulk(
                self._base_scalar(
                    spec.side, str(spec.component[0]), int(spec.component[1])
                ),
                spec.jet,
            )
        elif spec.family == "g":
            result = self._prolong_bulk(
                self._base_metric(
                    spec.side, int(spec.component[0]), int(spec.component[1])
                ),
                spec.jet,
            )
        elif spec.family == "eta":
            result = self._prolong_sigma(
                self._base_seta(int(spec.component[0])), spec.jet
            )
        elif spec.family == "X":
            result = self._prolong_sigma(
                self._base_X(int(spec.component[0])), spec.jet
            )
        elif spec.family == "Y":
            result = self._prolong_sigma(
                self._base_Y(spec.side, int(spec.component[0])), spec.jet
            )
        elif spec.family == "T":
            result = self._prolong_sigma(self._base_T(), spec.jet)
        elif spec.family == "kappa":
            if "bad_target_prolongation" in self.mutations and spec.jet[0] == 1:
                result = Polynomial.scalar(self.algebra, 0)
            else:
                result = self._prolong_target(self._base_skappa(), spec.jet[0])
        elif spec.family == "EvY_c":
            result = self._s_evaluated_c(spec)
        elif spec.family == "EvT_kappa":
            result = self._s_evaluated_kappa(spec)
        elif spec.family == "local_kappa":
            if "local_kappa_covariant" in self.mutations:
                result = self._prolong_sigma(
                    self._base_local_covariant_ghost(
                        spec.side, spec.component, spec.family
                    ),
                    spec.jet,
                )
            else:
                result = Polynomial.scalar(self.algebra, 0)
        elif spec.family == "local_C":
            result = self._prolong_sigma(
                self._base_local_covariant_ghost(
                    spec.side, spec.component, spec.family
                ),
                spec.jet,
            )
        else:
            raise SolidC2AGradedError(f"BRST unsupported on {spec.name}")
        expected = 1 - spec.parity
        result.require_homogeneous(expected, f"s({spec.name})")
        self._s_cache[spec.name] = result
        return result

    def s(self, polynomial: Polynomial) -> Polynomial:
        return self.algebra.derivation(
            polynomial, self.s_generator, operator_parity=1
        )

    def assert_certified_support(self, polynomial: Polynomial, label: str) -> int:
        """Reject a claimed trace beyond observed support without truncating it."""

        maximum = 0
        for monomial in polynomial.terms:
            for name, _ in monomial.even:
                order = sum(self.algebra.specs[name].jet)
                maximum = max(maximum, order)
            for name in monomial.odd:
                order = sum(self.algebra.specs[name].jet)
                maximum = max(maximum, order)
        if maximum > OBSERVED_CERTIFICATE_JET_ORDER:
            raise SolidC2AGradedError(
                f"{label} requests jet order {maximum} beyond observed certificate "
                f"support {OBSERVED_CERTIFICATE_JET_ORDER}"
            )
        return maximum

    def max_logged_order_since(self, start: int, label: str) -> int:
        maximum = 0
        for name in self.access_log[start:]:
            order = sum(self.algebra.specs[name].jet)
            maximum = max(maximum, order)
        if maximum > OBSERVED_CERTIFICATE_JET_ORDER:
            raise SolidC2AGradedError(
                f"{label} visited jet order {maximum} beyond certificate support "
                f"{OBSERVED_CERTIFICATE_JET_ORDER}"
            )
        return maximum


def serialize_polynomial(polynomial: Polynomial) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for monomial in sorted(polynomial.terms):
        coefficient = polynomial.terms[monomial]
        rows.append(
            {
                "numerator": coefficient.numerator,
                "denominator": coefficient.denominator,
                "even": [[name, power] for name, power in monomial.even],
                "odd": list(monomial.odd),
            }
        )
    return rows


def polynomial_digest(polynomial: Polynomial) -> str:
    return _canonical_json_digest(serialize_polynomial(polynomial))


def _identity_row(
    model: CandidateModel, label: str, generator: Polynomial
) -> dict[str, Any]:
    spec = model._only_spec(generator)
    trace_start = len(model.access_log)
    first = model.s(generator)
    second = model.s(first)
    first.require_homogeneous(1 - spec.parity, f"{label}.s")
    second.require_homogeneous(spec.parity, f"{label}.s2")
    first_order = model.assert_certified_support(first, f"{label}.s")
    second_order = model.assert_certified_support(second, f"{label}.s2")
    visited_order = model.max_logged_order_since(trace_start, label)
    if not second.is_zero:
        raise SolidC2AGradedError(f"exact nilpotency failed for {label}")
    return {
        "label": label,
        "generator": spec.name,
        "generator_parity": spec.parity,
        "s_terms": serialize_polynomial(first),
        "s_terms_sha256": polynomial_digest(first),
        "s2_terms": serialize_polynomial(second),
        "s2_exact_zero": True,
        "max_jet_order_in_serialized_result": max(first_order, second_order),
        "max_jet_order_visited": visited_order,
    }


def _core_identity_rows(model: CandidateModel) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Each side is completed before the next; no cross-side expression is built.
    for side in SIDES:
        for component in range(D_BULK):
            rows.append(_identity_row(model, f"{side}.c[{component}]", model.c(side, component)))
        rows.append(_identity_row(model, f"{side}.Omega", model.scalar(side, "Omega", 0)))
        for component in range(3):
            rows.append(
                _identity_row(
                    model,
                    f"{side}.phi[{component}]",
                    model.scalar(side, "phi", component),
                )
            )
        for first in range(D_BULK):
            for second in range(first, D_BULK):
                rows.append(
                    _identity_row(
                        model,
                        f"{side}.g[{first},{second}]",
                        model.metric(side, first, second),
                    )
                )

    for component in range(D_WORLDVOLUME):
        rows.append(_identity_row(model, f"eta[{component}]", model.eta(component)))
    for component in range(3):
        rows.append(_identity_row(model, f"X[{component}]", model.X(component)))
    for side in SIDES:
        for component in range(D_BULK):
            rows.append(_identity_row(model, f"{side}.Y[{component}]", model.Y(side, component)))
    rows.append(_identity_row(model, "T", model.T()))
    rows.append(_identity_row(model, "kappa", model.kappa()))

    for side in SIDES:
        for component in range(D_BULK):
            rows.append(
                _identity_row(
                    model,
                    f"{side}.C[{component}]=EvY(c[{component}])",
                    model.evaluated_c(side, component),
                )
            )
    rows.append(_identity_row(model, "K=EvT(kappa)", model.evaluated_kappa()))
    return rows


def _derived_chain_rows(model: CandidateModel) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for side in SIDES:
        for component in range(D_BULK):
            left = model.s(model.evaluated_c(side, component))
            for axis in range(D_WORLDVOLUME):
                left += model.eta(axis) * model.D_sigma(
                    model.evaluated_c(side, component), axis
                )
            model.assert_certified_support(left, f"derived {side}.C[{component}]")
            if not left.is_zero:
                raise SolidC2AGradedError("evaluated ambient ghost transport identity failed")
            rows.append(
                {
                    "label": f"s {side}.C[{component}]+eta^mu d_mu {side}.C[{component}]",
                    "terms": serialize_polynomial(left),
                    "exact_zero": True,
                }
            )
    left = model.s(model.evaluated_kappa())
    for axis in range(D_WORLDVOLUME):
        left += model.eta(axis) * model.D_sigma(model.evaluated_kappa(), axis)
    model.assert_certified_support(left, "derived K")
    if not left.is_zero:
        raise SolidC2AGradedError("evaluated target ghost transport identity failed")
    rows.append(
        {
            "label": "s K+eta^mu d_mu K",
            "terms": serialize_polynomial(left),
            "exact_zero": True,
        }
    )
    return rows


def _probe_generator(model: CandidateModel, mutant: str) -> tuple[str, Polynomial]:
    if mutant in {"sc_zero", "sc_sign", "dimension_last_index_omitted"}:
        return "plus.Omega", model.scalar("plus", "Omega", 0)
    if mutant in {"seta_zero", "seta_sign"}:
        return "X[0]", model.X(0)
    if mutant in {"omit_c_evaluation", "wrong_Y_sign", "evaluation_odd_order"}:
        return "plus.Y[0]", model.Y("plus", 0)
    if mutant in {
        "skappa_sign",
        "skappa_zero",
        "omit_kappa_evaluation",
        "target_evaluation_odd_order",
        "local_kappa",
    }:
        return "T", model.T()
    if mutant in {"omit_metric_first_leg", "omit_metric_second_leg"}:
        return "plus.g[0,1]", model.metric("plus", 0, 1)
    if mutant == "commuting_odd_algebra":
        return "plus.Omega", model.scalar("plus", "Omega", 0)
    if mutant == "bad_target_prolongation":
        return "[s,d_t]kappa", model.kappa(0)
    raise SolidC2AGradedError(f"unknown mutant probe: {mutant}")


def _build_mutant_residue(mutant: str) -> dict[str, Any]:
    odd_mode = "commuting_mutant" if mutant == "commuting_odd_algebra" else "exterior"
    mutations = set() if mutant == "commuting_odd_algebra" else {mutant}
    model = CandidateModel(mutations=mutations, odd_mode=odd_mode)

    # A dimension-omission mutant is implemented as a literal omission in the
    # scalar rule, rather than by changing the declared D=5 model.
    if mutant == "dimension_last_index_omitted":
        original = model._base_scalar

        def omitted(side: str, species: str, component: int) -> Polynomial:
            result = Polynomial.scalar(model.algebra, 0)
            for ambient in range(D_BULK - 1):
                result -= model.c(side, ambient) * model.scalar(
                    side, species, component, _unit_multiindex(D_BULK, ambient)
                )
            return result

        model._base_scalar = omitted  # type: ignore[method-assign]
        _ = original

    label, generator = _probe_generator(model, mutant)
    if mutant == "bad_target_prolongation":
        residue = model.s(model.D_target(generator)) - model.D_target(
            model.s(generator)
        )
    else:
        residue = model.s(model.s(generator))
    expected_parity = (
        1 - model._only_spec(generator).parity
        if mutant == "bad_target_prolongation"
        else model._only_spec(generator).parity
    )
    residue.require_homogeneous(expected_parity, f"mutant {mutant}")
    model.assert_certified_support(residue, f"mutant {mutant}")
    if residue.is_zero:
        raise SolidC2AGradedError(f"mutant {mutant} escaped with a zero residue")
    return {
        "id": mutant,
        "probe": label,
        "nonzero": True,
        "term_count": len(residue.terms),
        "residue_terms": serialize_polynomial(residue),
        "residue_sha256": polynomial_digest(residue),
    }


MUTANTS = (
    "sc_zero",
    "sc_sign",
    "seta_zero",
    "seta_sign",
    "omit_c_evaluation",
    "evaluation_odd_order",
    "wrong_Y_sign",
    "skappa_sign",
    "skappa_zero",
    "omit_kappa_evaluation",
    "target_evaluation_odd_order",
    "local_kappa",
    "bad_target_prolongation",
    "commuting_odd_algebra",
    "omit_metric_first_leg",
    "omit_metric_second_leg",
    "dimension_last_index_omitted",
)


def _mutated_inventory_digest(field: str, replacement: str) -> str:
    rows = [dict(row) for row in INVENTORY_FORMULA_ROWS]
    found = False
    for row in rows:
        if row["field"] == field:
            row["candidate"] = replacement
            found = True
    if not found:
        raise SolidC2AGradedError(f"unknown inventory formula field: {field}")
    return _canonical_json_digest(rows)


def _nilpotent_false_positive_controls() -> list[dict[str, Any]]:
    """Reject nilpotent alternatives by exact rule/provenance binding."""

    controls: list[dict[str, Any]] = []
    for identifier, marker in (
        ("all_rules_zero", "ALL_RULES_ZERO"),
        ("coherent_global_s_negation", "COHERENT_NEGATION"),
        ("coherent_global_s_rescale_by_2", "COHERENT_SCALE_2"),
    ):
        rows = [
            {"field": row["field"], "candidate": f"{marker}({row['candidate']})"}
            for row in INVENTORY_FORMULA_ROWS
        ]
        digest = _canonical_json_digest(rows)
        if digest == INVENTORY_FORMULA_ROWS_SHA256:
            raise SolidC2AGradedError("nilpotent convention control did not drift")
        controls.append(
            {
                "id": identifier,
                "nilpotency_can_survive": True,
                "accepted": False,
                "rejection": "exact_nine_formula_row_digest_mismatch",
                "mutant_formula_rows_sha256": digest,
            }
        )

    local_c = CandidateModel(mutations={"local_C_covariant"})
    if not local_c.s(local_c.s(local_c.Y("plus", 0))).is_zero:
        raise SolidC2AGradedError("local-C control was expected to be nilpotent")
    controls.append(
        {
            "id": "independent_local_C_covariant_transport",
            "nilpotency_can_survive": True,
            "accepted": False,
            "rejection": "C_is_not_literal_EvY_of_pinned_ambient_c_jets",
            "mutant_formula_rows_sha256": _mutated_inventory_digest(
                "Y_epsilon^M",
                "s Y_epsilon^M=C_local^M(sigma)-eta^mu partial_mu Y_epsilon^M",
            ),
        }
    )

    local_k = CandidateModel(mutations={"local_kappa", "local_kappa_covariant"})
    if not local_k.s(local_k.s(local_k.T())).is_zero:
        raise SolidC2AGradedError("local-K control was expected to be nilpotent")
    controls.append(
        {
            "id": "independent_local_K_covariant_transport",
            "nilpotency_can_survive": True,
            "accepted": False,
            "rejection": "K_is_not_literal_EvT_of_pinned_target_line_kappa_jets",
            "mutant_formula_rows_sha256": _mutated_inventory_digest(
                "T", "s T=-eta^mu partial_mu T+K_local(sigma)"
            ),
        }
    )
    return controls


def _prolongation_checks(model: CandidateModel) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for side in SIDES:
        for component in range(D_BULK):
            for axis in range(D_BULK):
                generator = model.c(side, component)
                difference = model.s(model.D_bulk(generator, axis)) - model.D_bulk(
                    model.s(generator), axis
                )
                model.assert_certified_support(difference, "bulk prolongation")
                if not difference.is_zero:
                    raise SolidC2AGradedError("[s,D_M] failed on a bulk ghost")
                rows.append({"domain": side, "generator": f"c[{component}]", "axis": axis})
    for component in range(D_WORLDVOLUME):
        for axis in range(D_WORLDVOLUME):
            generator = model.eta(component)
            difference = model.s(model.D_sigma(generator, axis)) - model.D_sigma(
                model.s(generator), axis
            )
            model.assert_certified_support(difference, "worldvolume prolongation")
            if not difference.is_zero:
                raise SolidC2AGradedError("[s,d_mu] failed on eta")
            rows.append({"domain": "Sigma", "generator": f"eta[{component}]", "axis": axis})
    kappa = model.kappa(0)
    target_difference = model.s(model.D_target(kappa)) - model.D_target(model.s(kappa))
    model.assert_certified_support(target_difference, "target prolongation")
    if not target_difference.is_zero:
        raise SolidC2AGradedError("[s,d_t] failed on kappa")
    rows.append({"domain": "R_T", "generator": "kappa", "axis": 0})
    return {
        "checked_rows": len(rows),
        "rows": rows,
        "all_exact_zero": True,
        "kappa_first_jet_is_derived_not_primitive": True,
    }


def _algebra_self_checks() -> dict[str, Any]:
    model = CandidateModel()
    u = model.c("plus", 0)
    v = model.c("plus", 1)
    w = model.c("plus", 2)
    checks = {
        "u_wedge_v_equals_minus_v_wedge_u": (u * v + v * u).is_zero,
        "u_wedge_u_equals_zero": (u * u).is_zero,
        "u_wedge_v_wedge_w_nonzero": not (u * v * w).is_zero,
        "c_plus_wedge_c_minus_nonzero": not (
            model.c("plus", 0) * model.c("minus", 0)
        ).is_zero,
    }
    # The factory is unbounded: D(jet2) creates jet3.  Certification then
    # rejects that trace rather than equating it to zero.
    jet2 = model.c("plus", 0, (2, 0, 0, 0, 0))
    jet3 = model.D_bulk(jet2, 0)
    checks["D_of_order2_is_nonzero_order3"] = not jet3.is_zero
    try:
        model.assert_certified_support(jet3, "self-check jet3")
    except SolidC2AGradedError:
        checks["order3_rejected_from_bounded_certificate"] = True
    else:
        checks["order3_rejected_from_bounded_certificate"] = False

    # Symmetric multiindex canonicalization: D0D1 and D1D0 name the same jet.
    scalar = model.scalar("plus", "Omega", 0)
    mixed_01 = model.D_bulk(model.D_bulk(scalar, 0), 1)
    mixed_10 = model.D_bulk(model.D_bulk(scalar, 1), 0)
    checks["symmetric_multiindex_D0D1_equals_D1D0"] = (
        mixed_01 - mixed_10
    ).is_zero
    if not all(checks.values()):
        raise SolidC2AGradedError(f"algebra self-check failed: {checks}")
    return checks


def _z2_automorphism_checks(model: CandidateModel) -> dict[str, Any]:
    """Check sJ=Js on side-labelled bases, without imposing a quotient."""

    generators: list[Polynomial] = []
    for side in SIDES:
        for component in range(D_BULK):
            generators.append(model.c(side, component))
        generators.append(model.scalar(side, "Omega", 0))
        for component in range(3):
            generators.append(model.scalar(side, "phi", component))
        for first in range(D_BULK):
            for second in range(first, D_BULK):
                generators.append(model.metric(side, first, second))
        for component in range(D_BULK):
            generators.append(model.Y(side, component))
            generators.append(model.evaluated_c(side, component))

    for generator in generators:
        lhs = model.s(model.swap_bulk_sides(generator))
        rhs = model.swap_bulk_sides(model.s(generator))
        difference = lhs - rhs
        model.assert_certified_support(difference, "Z2 automorphism")
        if not difference.is_zero:
            raise SolidC2AGradedError("side-label involution failed sJ=Js")
        twice = model.swap_bulk_sides(model.swap_bulk_sides(generator))
        if not (twice - generator).is_zero:
            raise SolidC2AGradedError("side-label involution failed J squared=id")
    return {
        "checked_generator_count": len(generators),
        "sJ_equals_Js": True,
        "J_squared_equals_identity_on_labels": True,
        "ghosts_identified": False,
        "quotient_selected": False,
    }


def _decision() -> dict[str, bool]:
    return {
        "explicit_modeled_candidate_kinematic_nilpotency_pass": True,
        "C2a_complete_BRST_algebra_pass": False,
        "C2_BRST_pass": False,
        "C3_DOMAIN_pass": False,
        "C4_HESSIAN_pass": False,
        "C5_JACOBIANS_pass": False,
        "C6_ZERO_MODES_pass": False,
        "C7_REGULATOR_pass": False,
        "C8_CONTOUR_pass": False,
        "C9_REDUCTION_pass": False,
        "C10_INDEPENDENCE_UNITARITY_pass": False,
        "P3_complete_gauge_fixed_unitary_determinant_pass": False,
        "P4_full_same_action_pass": False,
        "B4_pass": False,
        "B5_pass": False,
        "publication_authorized": False,
    }


def _proof_boundary() -> dict[str, bool]:
    return {
        "side_ghost_identification_selected": False,
        "khronon_Vect_R_quotient_selected": False,
        "action_BRST_invariance_proved": False,
        "gluing_tangency_proved": False,
        "gauge_fermion_constructed": False,
        "nonminimal_sector_constructed": False,
        "BRST_closed_boundary_domain_derived": False,
        "strong_ellipticity_or_Lorentzian_well_posedness_proved": False,
        "induced_metric_nilpotency_claimed": False,
        "all_jet_orders_claimed": False,
        "bulk_side_Z2_equivariant_quotient_claimed": False,
        "complete_gauge_irreducibility_or_reducibility_proved": False,
        "Killing_or_stabilizer_sectors_resolved": False,
        "kappa_mod_functions_vanishing_on_image_T_resolved": False,
        "edge_or_zero_modes_resolved": False,
        "reduced_subalgebroids_after_eliminating_Y_or_matching_derived": False,
    }


def _build_report_unvalidated() -> dict[str, Any]:
    inputs = load_pinned_inputs()
    model = CandidateModel()
    identities = _core_identity_rows(model)
    if len(identities) != 78:
        raise SolidC2AGradedError(f"identity inventory drift: {len(identities)} != 78")
    if max(row["max_jet_order_visited"] for row in identities) != 2:
        raise SolidC2AGradedError("certificate did not actually visit second jets")
    derived = _derived_chain_rows(model)
    if len(derived) != 11:
        raise SolidC2AGradedError("derived evaluation-chain inventory drift")
    mutants = [_build_mutant_residue(mutant) for mutant in MUTANTS]
    self_checks = _algebra_self_checks()
    z2_checks = _z2_automorphism_checks(model)
    prolongation_checks = _prolongation_checks(model)
    first_variation_digest = _canonical_json_digest(
        [
            {"generator": row["generator"], "s_terms": row["s_terms"]}
            for row in identities
        ]
    )

    report = {
        "schema": SCHEMA,
        "classification": (
            "theory_only;exact_free_supercommutative_Q_algebra;"
            "candidate_kinematic_nilpotency_only;C2_and_downstream_fail_closed"
        ),
        "summary": (
            "An explicit D=5, d=4 candidate BRST convention is exactly nilpotent "
            "on 78 listed order-zero generators in the modeled free jet algebra. "
            "This does not select the physical ghost quotients or prove action "
            "invariance, gluing tangency, a gauge fermion, or an operator domain."
        ),
        "pinned_inputs": {
            "inventory_source": {
                "path": str(INVENTORY_SOURCE.relative_to(REPO)),
                "sha256": INVENTORY_SOURCE_SHA256,
                "bytes": inputs["inventory_source_bytes"],
                "imported_or_executed": False,
            },
            "inventory_test": {
                "path": str(INVENTORY_TEST.relative_to(REPO)),
                "sha256": INVENTORY_TEST_SHA256,
                "bytes": inputs["inventory_test_bytes"],
                "imported_or_executed": False,
            },
            "charter": {
                "path": str(CHARTER_ARTIFACT.relative_to(REPO)),
                "sha256": CHARTER_ARTIFACT_SHA256,
                "bytes": inputs["charter_bytes"],
                "schema": CHARTER_SCHEMA,
                "route_id": CHARTER_ROUTE,
                "action_digest_sha256": CHARTER_ACTION_DIGEST,
            },
            "all_read_as_exact_bytes": True,
            "strict_charter_types_checked_independently": True,
        },
        "candidate_rule_binding": {
            "inventory_formula_rows": INVENTORY_FORMULA_ROWS,
            "inventory_formula_rows_sha256": INVENTORY_FORMULA_ROWS_SHA256,
            "candidate_rules": RULE_BINDING,
            "evaluation_rules": EVALUATION_BINDING,
            "sha256": RULE_BINDING_SHA256,
            "ordinary_commuting_ghost_symbols_used": False,
        },
        "algebra": {
            "coefficient_field": "Q via fractions.Fraction",
            "monomial_normal_form": "sorted even powers plus ordered odd wedge",
            "odd_duplicate_rule": "theta wedge theta = 0",
            "odd_product_sign": "inversion parity of ordered odd labels",
            "derivation": "left odd graded derivation",
            "total_derivatives": "even prolongations",
            "ambient_dimension": D_BULK,
            "worldvolume_dimension": D_WORLDVOLUME,
            "bulk_side_order": list(SIDES),
            "bulk_side_namespaces_disjoint": True,
            "bulk_side_ghost_identification_selected": False,
            "jet_label_universe": "lazy_unbounded_symmetric_multiindices",
            "certificate_support_is_not_a_truncation": True,
            "max_jet_order_observed": OBSERVED_CERTIFICATE_JET_ORDER,
            "each_run_uses_a_finitely_generated_subalgebra": True,
            "self_checks": self_checks,
        },
        "z2_label_automorphism": z2_checks,
        "prolongation_commutators": prolongation_checks,
        "exact_identities": {
            "count": len(identities),
            "rows": identities,
            "all_s2_exact_zero": all(row["s2_exact_zero"] for row in identities),
            "order_zero_generators_only": True,
            "all_first_variations_sha256": first_variation_digest,
        },
        "derived_evaluation_chain_identities": {
            "count": len(derived),
            "rows": derived,
            "raw_BRST_comes_only_from_evaluation_chain": True,
        },
        "mutant_campaign": {
            "required_nonzero_residue_count": len(mutants),
            "rows": mutants,
            "all_required_mutants_have_nonzero_residue": all(
                row["nonzero"] for row in mutants
            ),
            "nilpotent_false_positive_controls": _nilpotent_false_positive_controls(),
        },
        "proof_boundary": _proof_boundary(),
        "decision": _decision(),
        "artifact_written": False,
    }
    return report


def build_report() -> dict[str, Any]:
    """Construct the deterministic report after all executable checks pass."""

    report = _build_report_unvalidated()
    validate_report(report)
    return report


def validate_report(report: Any) -> None:
    if type(report) is not dict:
        raise SolidC2AGradedError("report must have exact type dict")
    if set(report) != {
        "schema",
        "classification",
        "summary",
        "pinned_inputs",
        "candidate_rule_binding",
        "algebra",
        "z2_label_automorphism",
        "prolongation_commutators",
        "exact_identities",
        "derived_evaluation_chain_identities",
        "mutant_campaign",
        "proof_boundary",
        "decision",
        "artifact_written",
    }:
        raise SolidC2AGradedError("report key inventory mismatch")
    _require_exact(report["schema"], SCHEMA, "report.schema")
    _require_exact(
        report["candidate_rule_binding"]["inventory_formula_rows"],
        INVENTORY_FORMULA_ROWS,
        "report.candidate_rule_binding.inventory_formula_rows",
    )
    _require_exact(
        report["candidate_rule_binding"]["inventory_formula_rows_sha256"],
        INVENTORY_FORMULA_ROWS_SHA256,
        "report.candidate_rule_binding.inventory_formula_rows_sha256",
    )
    _require_exact(
        report["candidate_rule_binding"]["candidate_rules"],
        RULE_BINDING,
        "report.candidate_rule_binding.candidate_rules",
    )
    _require_exact(
        report["candidate_rule_binding"]["evaluation_rules"],
        EVALUATION_BINDING,
        "report.candidate_rule_binding.evaluation_rules",
    )
    _require_exact(
        report["candidate_rule_binding"]["sha256"],
        RULE_BINDING_SHA256,
        "report.candidate_rule_binding.sha256",
    )
    _require_exact(
        report["candidate_rule_binding"]["ordinary_commuting_ghost_symbols_used"],
        False,
        "report.candidate_rule_binding.ordinary_commuting_ghost_symbols_used",
    )
    _require_exact(report["exact_identities"]["count"], 78, "report.identities.count")
    _require_exact(
        report["exact_identities"]["all_s2_exact_zero"],
        True,
        "report.identities.all_s2_exact_zero",
    )
    identity_rows = report["exact_identities"].get("rows")
    if type(identity_rows) is not list or len(identity_rows) != 78:
        raise SolidC2AGradedError("identity row inventory mismatch")
    labels: list[str] = []
    for index, row in enumerate(identity_rows):
        if type(row) is not dict or set(row) != {
            "label",
            "generator",
            "generator_parity",
            "s_terms",
            "s_terms_sha256",
            "s2_terms",
            "s2_exact_zero",
            "max_jet_order_in_serialized_result",
            "max_jet_order_visited",
        }:
            raise SolidC2AGradedError(f"identity row {index} key inventory mismatch")
        if type(row["label"]) is not str or type(row["generator"]) is not str:
            raise SolidC2AGradedError("identity labels and generators must be strings")
        labels.append(row["label"])
        if type(row["generator_parity"]) is not int or row["generator_parity"] not in (0, 1):
            raise SolidC2AGradedError("identity parity must be exact int 0 or 1")
        if type(row["s_terms"]) is not list or not row["s_terms"]:
            raise SolidC2AGradedError("first variation must have explicit nonempty terms")
        _require_exact(
            _canonical_json_digest(row["s_terms"]),
            row["s_terms_sha256"],
            f"report.identity[{index}].s_terms_sha256",
        )
        _require_exact(row["s2_terms"], [], f"report.identity[{index}].s2_terms")
        _require_exact(row["s2_exact_zero"], True, f"report.identity[{index}].s2_exact_zero")
        _require_exact(
            row["max_jet_order_in_serialized_result"],
            1,
            f"report.identity[{index}].serialized_order",
        )
        _require_exact(
            row["max_jet_order_visited"], 2, f"report.identity[{index}].visited_order"
        )
    if len(set(labels)) != 78:
        raise SolidC2AGradedError("identity labels are not unique")
    aggregate = _canonical_json_digest(
        [{"generator": row["generator"], "s_terms": row["s_terms"]} for row in identity_rows]
    )
    _require_exact(
        aggregate,
        report["exact_identities"]["all_first_variations_sha256"],
        "report.identities.all_first_variations_sha256",
    )
    _require_exact(
        report["derived_evaluation_chain_identities"]["count"],
        11,
        "report.derived.count",
    )
    if type(report["mutant_campaign"]["rows"]) is not list:
        raise SolidC2AGradedError("mutant rows must be a list")
    _require_exact(
        [row["id"] for row in report["mutant_campaign"]["rows"]],
        list(MUTANTS),
        "report.mutant.ids",
    )
    _require_exact(
        report["mutant_campaign"]["required_nonzero_residue_count"],
        len(MUTANTS),
        "report.mutant.required_nonzero_residue_count",
    )
    _require_exact(
        report["mutant_campaign"]["all_required_mutants_have_nonzero_residue"],
        True,
        "report.mutant.all_required_mutants_have_nonzero_residue",
    )
    for index, row in enumerate(report["mutant_campaign"]["rows"]):
        _require_exact(row["nonzero"], True, f"report.mutants[{index}].nonzero")
        if type(row["term_count"]) is not int or row["term_count"] <= 0:
            raise SolidC2AGradedError("mutant term_count must be a positive int")
        if not row["residue_terms"]:
            raise SolidC2AGradedError("mutant residue cannot be empty")
        _require_exact(
            _canonical_json_digest(row["residue_terms"]),
            row["residue_sha256"],
            f"report.mutants[{index}].residue_sha256",
        )
    controls = report["mutant_campaign"].get("nilpotent_false_positive_controls")
    if type(controls) is not list:
        raise SolidC2AGradedError("nilpotent false-positive controls must be a list")
    expected_controls = {
        "all_rules_zero": "exact_nine_formula_row_digest_mismatch",
        "coherent_global_s_negation": "exact_nine_formula_row_digest_mismatch",
        "coherent_global_s_rescale_by_2": "exact_nine_formula_row_digest_mismatch",
        "independent_local_C_covariant_transport": (
            "C_is_not_literal_EvY_of_pinned_ambient_c_jets"
        ),
        "independent_local_K_covariant_transport": (
            "K_is_not_literal_EvT_of_pinned_target_line_kappa_jets"
        ),
    }
    if [row.get("id") for row in controls] != list(expected_controls):
        raise SolidC2AGradedError("nilpotent false-positive control inventory mismatch")
    for index, row in enumerate(controls):
        identifier = row["id"]
        _require_exact(row.get("nilpotency_can_survive"), True, f"control[{index}].nilpotency")
        _require_exact(row.get("accepted"), False, f"control[{index}].accepted")
        _require_exact(row.get("rejection"), expected_controls[identifier], f"control[{index}].rejection")
        digest = row.get("mutant_formula_rows_sha256")
        if type(digest) is not str or len(digest) != 64 or digest == INVENTORY_FORMULA_ROWS_SHA256:
            raise SolidC2AGradedError("nilpotent false-positive digest did not drift")
    _require_exact(
        report["z2_label_automorphism"],
        {
            "checked_generator_count": 68,
            "sJ_equals_Js": True,
            "J_squared_equals_identity_on_labels": True,
            "ghosts_identified": False,
            "quotient_selected": False,
        },
        "report.z2_label_automorphism",
    )
    _require_exact(
        report["prolongation_commutators"]["checked_rows"],
        67,
        "report.prolongation.checked_rows",
    )
    _require_exact(
        report["prolongation_commutators"]["all_exact_zero"],
        True,
        "report.prolongation.all_exact_zero",
    )
    _require_exact(
        report["prolongation_commutators"]["kappa_first_jet_is_derived_not_primitive"],
        True,
        "report.prolongation.kappa_first_jet",
    )
    _require_exact(report["proof_boundary"], _proof_boundary(), "report.proof_boundary")
    _require_exact(report["decision"], _decision(), "report.decision")
    _require_exact(report["artifact_written"], False, "report.artifact_written")
    # The structural checks above provide localized errors.  This final exact
    # reconstruction binds every exported byte-level input description,
    # narrative scope, algebra flag, identity row, chain row, mutant probe,
    # prolongation row, and false boundary.  No unvalidated top-level prose or
    # nested block remains available for correlated overclaiming.
    _require_exact(report, _build_report_unvalidated(), "report")


def main() -> int:
    print(json.dumps(build_report(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
