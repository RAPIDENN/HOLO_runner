#!/usr/bin/env python3
"""TaylorDual3 and regular SO(3) primitives for Route C v5.6.7.1.

This is the incremental M3 delivery after the full-T^4 M1+M2 primitives in
v5.6.7.  It implements a scalar truncated Taylor algebra, an SO(3) exponential
over that algebra, and the common-first C2 decoder at one full-T4 collar point.
The decoder returns ambient X64, pulled X64, pulled reference metric 15 and
their ordered X79 concatenation, each with primal and eta value/5D two-jet.
Despite ``dual_local_action`` in the reserved filename, this delivery does NOT
implement a local density, a local density JVP, an integrated action, or
quadrature.

The algebra is

    R[x0,x1,x2,x3,eta] / (eta**2, monomials with |alpha| > 3).

The eta axis is independent of spatial degree: every eta*x**alpha with
|alpha| <= 3 is retained.  Ordinary monomial coefficients are stored; jet
extraction multiplies them by the multi-index factorial.

Analytic scalar composition needs derivatives through order four, not three:
if delta contains an eta-constant term, delta**4 can contain eta times a
spatial cubic.  The SO(3) exponential uses the entire Rodrigues series in
z=q.q and never divides by z or sqrt(z), so q=0 is an ordinary series point.

Numerical scope is intentionally fail-closed.  Direct float64 Maclaurin sums
lose cancellation at large |q|.  This unit therefore accepts only
|body(q)| <= pi-1, checked as q.q <= (pi-1)**2 without taking a norm, and
the l1 sum of all non-body input coefficients must be <= 8.  Those deliberately
conservative domains are sampled against high precision in tests; they are not
uniform rounding enclosures and cannot support a uniform-in-N claim.  A future
wider-domain implementation must use audited scaling/squaring plus interval or
multiprecision error control before relaxing either guard.

TRUE decision keys cover only the mixed algebra, sampled analytic identities,
sampled SO(3) regularity/orthogonality/JVP consistency, and the decoder sampled
against byte-pinned finite-N oracles.  Density, action, quadrature, margins,
bridge, C1/N1, and B4/B5 keys remain FALSE.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
from functools import lru_cache
from itertools import product
import json
import math
from numbers import Real
import operator
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
SCHEMA = "holo.one-omega-topological-so3-route-c-full-t4-dual-local-action-v5-6-7-1.v1"

UPSTREAM_PATH = HERE / "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
UPSTREAM_SHA256 = "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25"
UPSTREAM_SCHEMA = "holo.one-omega-topological-so3-route-c-full-t4-exact-primitives-v5-6-7.v1"
POINTWISE_ORACLE_PATH = HERE / (
    "export_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_2_pointwise_primitives.py"
)
POINTWISE_ORACLE_SHA256 = "4b7eda150cf2d22e04ef2b1b04391c31dc9e618839d7ead9e74a540371ab3d7f"
POINTWISE_ORACLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-2-pointwise-primitive-bundle.v1"
)
C2_BUNDLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-4-c2-radial-primitive-bundle.v1"
)

N_SPATIAL = 4
MAX_SPATIAL_DEGREE = 3
ZERO_ALPHA = (0, 0, 0, 0)
SO3_SERIES_BODY_NORM_LIMIT = math.pi - 1.0
SO3_SERIES_BODY_Z_LIMIT = SO3_SERIES_BODY_NORM_LIMIT**2
SO3_SERIES_NONBODY_L1_LIMIT = 8.0
SAMPLED_TOLERANCE = 8.0e-12

SIDES = ("plus", "minus")
SIDE_RADIAL_SIGN = {"plus": -1.0, "minus": 1.0}
SYMMETRIC4 = tuple((i, j) for i in range(4) for j in range(i, 4))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))
B_TRIPLES = tuple(
    (i, j, k)
    for i in range(5)
    for j in range(i + 1, 5)
    for k in range(j + 1, 5)
)
REFERENCE_METRIC_DIAGONAL = (-1.64, 1.17, 1.31, 1.46, 1.17)

Alpha = tuple[int, int, int, int]
Key = tuple[int, Alpha]


class DualLocalActionError(RuntimeError):
    """Base error for this fail-closed M3 unit."""


class TaylorDual3InputError(DualLocalActionError, ValueError):
    """Malformed or out-of-domain input."""


class TaylorDual3NumericalError(DualLocalActionError, ArithmeticError):
    """A float64 operation left the supported finite numerical domain."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def _load_pinned_upstream() -> Any:
    observed = _sha256(UPSTREAM_PATH)
    if observed != UPSTREAM_SHA256:
        raise DualLocalActionError(f"v5.6.7 source pin drift: {observed}")
    spec = importlib.util.spec_from_file_location("pinned_full_t4_exact_primitives_v5_6_7", UPSTREAM_PATH)
    if spec is None or spec.loader is None:
        raise DualLocalActionError("cannot load pinned v5.6.7 source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if getattr(module, "SCHEMA", None) != UPSTREAM_SCHEMA:
        raise DualLocalActionError("v5.6.7 schema drift")
    return module


@lru_cache(maxsize=1)
def _load_pinned_pointwise_oracle() -> Any:
    observed = _sha256(POINTWISE_ORACLE_PATH)
    if observed != POINTWISE_ORACLE_SHA256:
        raise DualLocalActionError(f"v5.6.4.2 pointwise decoder pin drift: {observed}")
    spec = importlib.util.spec_from_file_location(
        "pinned_pointwise_primitives_v5_6_4_2", POINTWISE_ORACLE_PATH
    )
    if spec is None or spec.loader is None:
        raise DualLocalActionError("cannot load pinned v5.6.4.2 pointwise decoder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if getattr(module, "SCHEMA", None) != POINTWISE_ORACLE_SCHEMA:
        raise DualLocalActionError("v5.6.4.2 pointwise decoder schema drift")
    return module


@lru_cache(maxsize=1)
def _load_c2_bundle() -> Mapping[str, Any]:
    upstream = _load_pinned_upstream()
    observed = _sha256(upstream.BUNDLE_PATH)
    if observed != upstream.BUNDLE_SHA256:
        raise DualLocalActionError(f"C2 v5.6.4.4 bundle pin drift: {observed}")
    bundle = json.loads(upstream.BUNDLE_PATH.read_text(encoding="utf-8"))
    if bundle.get("schema") != C2_BUNDLE_SCHEMA:
        raise DualLocalActionError("C2 v5.6.4.4 bundle schema drift")
    payload = {key: value for key, value in bundle.items() if key != "payload_sha256"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if hashlib.sha256(encoded).hexdigest() != bundle.get("payload_sha256"):
        raise DualLocalActionError("C2 v5.6.4.4 bundle payload drift")
    return bundle


def _decode_pinned_f64(record: Mapping[str, Any]) -> np.ndarray:
    """Decode one digest-checked little-endian float64 array from the C2 bundle."""

    if record.get("dtype") != "<f8" or record.get("encoding") != "base64":
        raise DualLocalActionError("C2 float64 record codec drift")
    try:
        raw = base64.b64decode(record["data"], validate=True)
    except (KeyError, TypeError, ValueError) as exc:
        raise DualLocalActionError("malformed C2 float64 record") from exc
    if hashlib.sha256(raw).hexdigest() != record.get("sha256"):
        raise DualLocalActionError("C2 float64 record digest drift")
    try:
        shape = tuple(_strict_integer("record shape", item, 0) for item in record["shape"])
    except (KeyError, TypeError) as exc:
        raise DualLocalActionError("malformed C2 float64 record shape") from exc
    values = np.frombuffer(raw, dtype="<f8").copy()
    if values.size != math.prod(shape) or not np.all(np.isfinite(values)):
        raise DualLocalActionError("C2 float64 record shape or finiteness drift")
    return values.reshape(shape)


def _strict_integer(name: str, value: Any, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool) or type(value).__name__ == "bool_":
        raise TaylorDual3InputError(f"{name} must be an integer, not bool")
    try:
        result = operator.index(value)
    except TypeError as exc:
        raise TaylorDual3InputError(f"{name} must be an integer, got {value!r}") from exc
    result = int(result)
    if result < minimum or (maximum is not None and result > maximum):
        interval = f"[{minimum}, {maximum}]" if maximum is not None else f">= {minimum}"
        raise TaylorDual3InputError(f"{name} must be in {interval}, got {result}")
    return result


def _finite_real(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TaylorDual3InputError(f"{name} must be a finite real scalar, got {value!r}")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise TaylorDual3InputError(f"{name} must be a finite float64 scalar") from exc
    if not math.isfinite(result):
        raise TaylorDual3InputError(f"{name} must be finite")
    return result


def _validate_alpha(alpha: Iterable[Any]) -> Alpha:
    try:
        raw = tuple(alpha)
    except TypeError as exc:
        raise TaylorDual3InputError("alpha must be an iterable of four integers") from exc
    if len(raw) != N_SPATIAL:
        raise TaylorDual3InputError(f"alpha must have length {N_SPATIAL}, got {len(raw)}")
    result = tuple(_strict_integer(f"alpha[{axis}]", value, 0) for axis, value in enumerate(raw))
    return result  # type: ignore[return-value]


def _alpha_degree(alpha: Alpha) -> int:
    return sum(alpha)


def _alpha_add(left: Alpha, right: Alpha) -> Alpha:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def _alpha_factorial(alpha: Alpha) -> int:
    return math.prod(math.factorial(value) for value in alpha)


def _all_multiindices() -> tuple[Alpha, ...]:
    result = [
        alpha
        for alpha in product(range(MAX_SPATIAL_DEGREE + 1), repeat=N_SPATIAL)
        if sum(alpha) <= MAX_SPATIAL_DEGREE
    ]
    result.sort(key=lambda alpha: (sum(alpha), alpha))
    return tuple(result)  # type: ignore[return-value]


ALL_MULTIINDICES = _all_multiindices()


class TaylorDual3:
    """Sparse float64 element of the independent spatial/eta quotient algebra."""

    __slots__ = ("_coefficients",)

    def __init__(self, coefficients: Mapping[Key, Real] | None = None) -> None:
        cleaned: dict[Key, float] = {}
        if coefficients is not None:
            if not isinstance(coefficients, Mapping):
                raise TaylorDual3InputError("coefficients must be a mapping")
            for raw_key, raw_value in coefficients.items():
                try:
                    raw_eta_power, raw_alpha = raw_key
                except (TypeError, ValueError) as exc:
                    raise TaylorDual3InputError("each coefficient key must be (eta_power, alpha)") from exc
                eta_power = _strict_integer("eta_power", raw_eta_power, 0, 1)
                alpha = _validate_alpha(raw_alpha)
                if _alpha_degree(alpha) > MAX_SPATIAL_DEGREE:
                    raise TaylorDual3InputError("coefficient spatial degree exceeds three")
                value = _finite_real("coefficient", raw_value)
                key = (eta_power, alpha)
                combined = cleaned.get(key, 0.0) + value
                if not math.isfinite(combined):
                    raise TaylorDual3NumericalError("coefficient canonicalization overflowed")
                if combined == 0.0:
                    cleaned.pop(key, None)
                else:
                    cleaned[key] = combined
        self._coefficients = cleaned

    @classmethod
    def constant(cls, value: Real) -> "TaylorDual3":
        numeric = _finite_real("constant", value)
        return cls({(0, ZERO_ALPHA): numeric}) if numeric != 0.0 else cls()

    @classmethod
    def variable(cls, axis: int, value: Real = 0.0) -> "TaylorDual3":
        axis = _strict_integer("axis", axis, 0, N_SPATIAL - 1)
        alpha = [0] * N_SPATIAL
        alpha[axis] = 1
        return cls({(0, ZERO_ALPHA): _finite_real("value", value), (0, tuple(alpha)): 1.0})

    @classmethod
    def eta(cls, coefficient: Real = 1.0) -> "TaylorDual3":
        return cls({(1, ZERO_ALPHA): _finite_real("eta coefficient", coefficient)})

    @property
    def body(self) -> float:
        return self._coefficients.get((0, ZERO_ALPHA), 0.0)

    @property
    def coefficients(self) -> dict[Key, float]:
        return dict(self._coefficients)

    def coefficient(self, alpha: Iterable[Any] = ZERO_ALPHA, eta_order: int = 0) -> float:
        typed_alpha = _validate_alpha(alpha)
        typed_eta = _strict_integer("eta_order", eta_order, 0, 1)
        return self._coefficients.get((typed_eta, typed_alpha), 0.0)

    def derivative(self, alpha: Iterable[Any] = ZERO_ALPHA, eta_order: int = 0) -> float:
        typed_alpha = _validate_alpha(alpha)
        typed_eta = _strict_integer("eta_order", eta_order, 0, 1)
        if _alpha_degree(typed_alpha) > MAX_SPATIAL_DEGREE:
            return 0.0
        return _alpha_factorial(typed_alpha) * self._coefficients.get((typed_eta, typed_alpha), 0.0)

    def partial(self, axis: int) -> "TaylorDual3":
        """Differentiate the represented spatial Taylor polynomial exactly."""

        axis = _strict_integer("axis", axis, 0, N_SPATIAL - 1)
        out: dict[Key, float] = {}
        for (eta_power, alpha), coefficient in self._coefficients.items():
            exponent = alpha[axis]
            if exponent == 0:
                continue
            reduced = list(alpha)
            reduced[axis] -= 1
            key = (eta_power, tuple(reduced))
            out[key] = out.get(key, 0.0) + exponent * coefficient
        return TaylorDual3(out)

    def jet(self, eta_order: int = 0) -> dict[Alpha, float]:
        typed_eta = _strict_integer("eta_order", eta_order, 0, 1)
        return {alpha: self.derivative(alpha, typed_eta) for alpha in ALL_MULTIINDICES}

    def extract_jets(self) -> dict[str, dict[str, Any]]:
        units: list[Alpha] = [
            tuple(int(axis == selected) for axis in range(N_SPATIAL))  # type: ignore[misc]
            for selected in range(N_SPATIAL)
        ]

        def layer(eta_order: int) -> dict[str, Any]:
            gradient = tuple(self.derivative(unit, eta_order) for unit in units)
            hessian = tuple(
                tuple(self.derivative(_alpha_add(units[i], units[j]), eta_order) for j in range(N_SPATIAL))
                for i in range(N_SPATIAL)
            )
            third = tuple(
                tuple(
                    tuple(
                        self.derivative(_alpha_add(_alpha_add(units[i], units[j]), units[k]), eta_order)
                        for k in range(N_SPATIAL)
                    )
                    for j in range(N_SPATIAL)
                )
                for i in range(N_SPATIAL)
            )
            return {
                "value": self.derivative(ZERO_ALPHA, eta_order),
                "gradient": gradient,
                "hessian": hessian,
                "third": third,
            }

        return {"primal": layer(0), "eta": layer(1)}

    def evaluate_spatial_layer(self, displacement: Sequence[Real], eta_order: int = 0) -> float:
        """Evaluate one coefficient layer as a spatial polynomial.

        Eta is nilpotent, not a finite real displacement.  Evaluating the
        primal and eta-coefficient layers separately avoids presenting a map
        eta -> real as an algebra homomorphism.
        """

        if len(displacement) != N_SPATIAL:
            raise TaylorDual3InputError(f"displacement must have length {N_SPATIAL}")
        point = tuple(_finite_real(f"displacement[{axis}]", value) for axis, value in enumerate(displacement))
        typed_eta = _strict_integer("eta_order", eta_order, 0, 1)
        terms = []
        for (eta_power, alpha), coefficient in self._coefficients.items():
            if eta_power != typed_eta:
                continue
            monomial = 1.0
            for coordinate, exponent in zip(point, alpha):
                monomial *= coordinate**exponent
            terms.append(coefficient * monomial)
        try:
            result = math.fsum(terms)
        except (OverflowError, ValueError) as exc:
            raise TaylorDual3NumericalError("evaluation left the finite float64 domain") from exc
        if not math.isfinite(result):
            raise TaylorDual3NumericalError("evaluation left the finite float64 domain")
        return result

    @staticmethod
    def _coerce(value: object) -> "TaylorDual3" | Any:
        if isinstance(value, TaylorDual3):
            return value
        if isinstance(value, Real) and not isinstance(value, bool):
            return TaylorDual3.constant(value)
        return NotImplemented

    @staticmethod
    def _require(value: object) -> "TaylorDual3":
        result = TaylorDual3._coerce(value)
        if result is NotImplemented:
            raise TypeError(f"expected TaylorDual3 or finite real scalar, got {type(value).__name__}")
        return result

    def __add__(self, other: object) -> "TaylorDual3":
        right = self._coerce(other)
        if right is NotImplemented:
            return NotImplemented
        out = dict(self._coefficients)
        for key, value in right._coefficients.items():
            combined = out.get(key, 0.0) + value
            if not math.isfinite(combined):
                raise TaylorDual3NumericalError("addition overflowed")
            if combined == 0.0:
                out.pop(key, None)
            else:
                out[key] = combined
        return TaylorDual3(out)

    __radd__ = __add__

    def __neg__(self) -> "TaylorDual3":
        return TaylorDual3({key: -value for key, value in self._coefficients.items()})

    def __sub__(self, other: object) -> "TaylorDual3":
        right = self._coerce(other)
        if right is NotImplemented:
            return NotImplemented
        return self + (-right)

    def __rsub__(self, other: object) -> "TaylorDual3":
        left = self._coerce(other)
        if left is NotImplemented:
            return NotImplemented
        return left - self

    def __mul__(self, other: object) -> "TaylorDual3":
        right = self._coerce(other)
        if right is NotImplemented:
            return NotImplemented
        out: dict[Key, float] = {}
        for (left_eta, left_alpha), left_value in self._coefficients.items():
            for (right_eta, right_alpha), right_value in right._coefficients.items():
                eta_power = left_eta + right_eta
                if eta_power > 1:
                    continue
                alpha = _alpha_add(left_alpha, right_alpha)
                if _alpha_degree(alpha) > MAX_SPATIAL_DEGREE:
                    continue
                key = (eta_power, alpha)
                combined = out.get(key, 0.0) + left_value * right_value
                if not math.isfinite(combined):
                    raise TaylorDual3NumericalError("multiplication overflowed")
                if combined == 0.0:
                    out.pop(key, None)
                else:
                    out[key] = combined
        return TaylorDual3(out)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> "TaylorDual3":
        exponent = _strict_integer("exponent", exponent, -2**31, 2**31 - 1)
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = TaylorDual3.constant(1.0)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            power >>= 1
            if power:
                base = base * base
        return result

    def _analytic_compose(self, derivatives: Sequence[Real]) -> "TaylorDual3":
        if len(derivatives) != 5:
            raise TaylorDual3InputError("analytic composition requires derivatives of orders zero through four")
        values = tuple(_finite_real(f"derivative[{order}]", value) for order, value in enumerate(derivatives))
        delta = self - self.body
        power = TaylorDual3.constant(1.0)
        result = TaylorDual3.constant(values[0])
        for order in range(1, 5):
            power = power * delta
            result = result + (values[order] / math.factorial(order)) * power
        return result

    def inverse(self) -> "TaylorDual3":
        if self.body == 0.0:
            raise TaylorDual3InputError("inverse requires a non-zero primal body")
        try:
            derivatives = tuple(
                (-1.0) ** order * math.factorial(order) / self.body ** (order + 1)
                for order in range(5)
            )
        except (OverflowError, ZeroDivisionError) as exc:
            raise TaylorDual3NumericalError("inverse derivatives overflowed") from exc
        if not all(math.isfinite(value) for value in derivatives):
            raise TaylorDual3NumericalError("inverse derivatives left the finite float64 domain")
        return self._analytic_compose(derivatives)

    def __truediv__(self, other: object) -> "TaylorDual3":
        right = self._coerce(other)
        if right is NotImplemented:
            return NotImplemented
        return self * right.inverse()

    def __rtruediv__(self, other: object) -> "TaylorDual3":
        left = self._coerce(other)
        if left is NotImplemented:
            return NotImplemented
        return left * self.inverse()

    def exp(self) -> "TaylorDual3":
        try:
            value = math.exp(self.body)
        except OverflowError as exc:
            raise TaylorDual3NumericalError("exp body overflowed") from exc
        return self._analytic_compose((value, value, value, value, value))

    def sin(self) -> "TaylorDual3":
        sine, cosine = math.sin(self.body), math.cos(self.body)
        return self._analytic_compose((sine, cosine, -sine, -cosine, sine))

    def cos(self) -> "TaylorDual3":
        sine, cosine = math.sin(self.body), math.cos(self.body)
        return self._analytic_compose((cosine, -sine, -cosine, sine, cosine))

    def sqrt(self) -> "TaylorDual3":
        if self.body <= 0.0:
            raise TaylorDual3InputError("sqrt requires a strictly positive primal body")
        derivatives = []
        falling = 1.0
        for order in range(5):
            if order:
                falling *= 0.5 - (order - 1)
            derivatives.append(falling * self.body ** (0.5 - order))
        if not all(math.isfinite(value) for value in derivatives):
            raise TaylorDual3NumericalError("sqrt derivatives left the finite float64 domain")
        return self._analytic_compose(derivatives)

    def almost_equal(self, other: object, *, atol: float = 1.0e-12, rtol: float = 1.0e-12) -> bool:
        right = self._coerce(other)
        if right is NotImplemented:
            return False
        atol = _finite_real("atol", atol)
        rtol = _finite_real("rtol", rtol)
        if atol < 0.0 or rtol < 0.0:
            raise TaylorDual3InputError("comparison tolerances must be non-negative")
        keys = set(self._coefficients) | set(right._coefficients)
        return all(
            math.isclose(
                self._coefficients.get(key, 0.0),
                right._coefficients.get(key, 0.0),
                abs_tol=atol,
                rel_tol=rtol,
            )
            for key in keys
        )

    def __repr__(self) -> str:
        return f"TaylorDual3({self._coefficients!r})"


class RhoJet2:
    """Value and first/second rho derivatives, each carrying a TaylorDual3."""

    __slots__ = ("value", "rho_first", "rho_second")

    def __init__(
        self,
        value: TaylorDual3 | Real,
        rho_first: TaylorDual3 | Real = 0.0,
        rho_second: TaylorDual3 | Real = 0.0,
    ) -> None:
        self.value = TaylorDual3._require(value)
        self.rho_first = TaylorDual3._require(rho_first)
        self.rho_second = TaylorDual3._require(rho_second)

    @staticmethod
    def _coerce(value: object) -> "RhoJet2" | Any:
        if isinstance(value, RhoJet2):
            return value
        converted = TaylorDual3._coerce(value)
        if converted is NotImplemented:
            return NotImplemented
        return RhoJet2(converted)

    def __add__(self, other: object) -> "RhoJet2":
        right = self._coerce(other)
        if right is NotImplemented:
            return NotImplemented
        return RhoJet2(
            self.value + right.value,
            self.rho_first + right.rho_first,
            self.rho_second + right.rho_second,
        )

    __radd__ = __add__

    def __neg__(self) -> "RhoJet2":
        return RhoJet2(-self.value, -self.rho_first, -self.rho_second)

    def __sub__(self, other: object) -> "RhoJet2":
        right = self._coerce(other)
        if right is NotImplemented:
            return NotImplemented
        return self + (-right)

    def __rsub__(self, other: object) -> "RhoJet2":
        left = self._coerce(other)
        if left is NotImplemented:
            return NotImplemented
        return left - self

    def __mul__(self, other: object) -> "RhoJet2":
        right = self._coerce(other)
        if right is NotImplemented:
            return NotImplemented
        return RhoJet2(
            self.value * right.value,
            self.rho_first * right.value + self.value * right.rho_first,
            self.rho_second * right.value
            + 2.0 * self.rho_first * right.rho_first
            + self.value * right.rho_second,
        )

    __rmul__ = __mul__

    def almost_equal(self, other: object, *, atol: float = 1.0e-12, rtol: float = 1.0e-12) -> bool:
        right = self._coerce(other)
        if right is NotImplemented:
            return False
        return (
            self.value.almost_equal(right.value, atol=atol, rtol=rtol)
            and self.rho_first.almost_equal(right.rho_first, atol=atol, rtol=rtol)
            and self.rho_second.almost_equal(right.rho_second, atol=atol, rtol=rtol)
        )

    def __repr__(self) -> str:
        return (
            f"RhoJet2(value={self.value!r}, rho_first={self.rho_first!r}, "
            f"rho_second={self.rho_second!r})"
        )


def exp(value: TaylorDual3 | Real) -> TaylorDual3:
    return TaylorDual3._require(value).exp()


def sin(value: TaylorDual3 | Real) -> TaylorDual3:
    return TaylorDual3._require(value).sin()


def cos(value: TaylorDual3 | Real) -> TaylorDual3:
    return TaylorDual3._require(value).cos()


def sqrt(value: TaylorDual3 | Real) -> TaylorDual3:
    return TaylorDual3._require(value).sqrt()


def _rodrigues_entire_derivatives(z0: float, denominator_shift: int) -> tuple[float, ...]:
    """Derivatives 0..4 of A(z) (shift 1) or B(z) (shift 2)."""

    z0 = _finite_real("z body", z0)
    denominator_shift = _strict_integer("denominator_shift", denominator_shift, 1, 2)
    if z0 < 0.0:
        raise TaylorDual3InputError("q.q body must be non-negative")
    if z0 > SO3_SERIES_BODY_Z_LIMIT:
        raise TaylorDual3InputError(
            f"SO(3) series supports q.q body <= {SO3_SERIES_BODY_Z_LIMIT:.17g}; "
            "wider rotations require an audited stable evaluator"
        )

    derivatives = []
    for derivative_order in range(5):
        term = (
            (-1.0) ** derivative_order
            * math.factorial(derivative_order)
            / math.factorial(2 * derivative_order + denominator_shift)
        )
        terms = []
        consecutive_small = 0
        for series_order in range(96):
            terms.append(term)
            partial = math.fsum(terms)
            if series_order >= 4 and abs(term) <= 2.0e-16 * max(1.0, abs(partial)):
                consecutive_small += 1
            else:
                consecutive_small = 0
            if consecutive_small >= 4:
                break
            k = derivative_order + series_order
            denominator = (2 * k + denominator_shift + 1) * (2 * k + denominator_shift + 2)
            term *= -((k + 1) / (series_order + 1)) * z0 / denominator
            if not math.isfinite(term):
                raise TaylorDual3NumericalError("Rodrigues series overflowed")
        else:
            raise TaylorDual3NumericalError("Rodrigues series did not converge")
        value = math.fsum(terms)
        if not math.isfinite(value):
            raise TaylorDual3NumericalError("Rodrigues series produced a non-finite derivative")
        derivatives.append(value)
    return tuple(derivatives)


def _matrix_multiply(
    left: Sequence[Sequence[TaylorDual3]], right: Sequence[Sequence[TaylorDual3]]
) -> tuple[tuple[TaylorDual3, ...], ...]:
    if len(left) != 3 or len(right) != 3 or any(len(row) != 3 for row in left) or any(len(row) != 3 for row in right):
        raise TaylorDual3InputError("matrix multiplication expects two 3x3 matrices")
    zero = TaylorDual3.constant(0.0)
    return tuple(
        tuple(sum((left[i][k] * right[k][j] for k in range(3)), zero) for j in range(3))
        for i in range(3)
    )


def so3_exp(rotation_vector: Sequence[TaylorDual3 | Real]) -> tuple[tuple[TaylorDual3, ...], ...]:
    """Rodrigues exponential from entire series in z=q.q on the guarded domain."""

    if len(rotation_vector) != 3:
        raise TaylorDual3InputError("so3_exp expects exactly three components")
    q = tuple(TaylorDual3._require(component) for component in rotation_vector)
    try:
        nonbody_l1 = math.fsum(
            abs(value)
            for component in q
            for key, value in component._coefficients.items()
            if key != (0, ZERO_ALPHA)
        )
    except OverflowError as exc:
        raise TaylorDual3NumericalError("SO(3) Taylor input coefficient norm overflowed") from exc
    if nonbody_l1 > SO3_SERIES_NONBODY_L1_LIMIT:
        raise TaylorDual3InputError(
            f"SO(3) Taylor input non-body l1 norm must be <= {SO3_SERIES_NONBODY_L1_LIMIT}; "
            "larger jets require interval or multiprecision error control"
        )
    z = sum((component * component for component in q), TaylorDual3.constant(0.0))
    a = z._analytic_compose(_rodrigues_entire_derivatives(z.body, 1))
    b = z._analytic_compose(_rodrigues_entire_derivatives(z.body, 2))
    zero = TaylorDual3.constant(0.0)
    skew = (
        (zero, -q[2], q[1]),
        (q[2], zero, -q[0]),
        (-q[1], q[0], zero),
    )
    skew_squared = _matrix_multiply(skew, skew)
    return tuple(
        tuple(
            TaylorDual3.constant(float(i == j)) + a * skew[i][j] + b * skew_squared[i][j]
            for j in range(3)
        )
        for i in range(3)
    )


def _finite_vector(name: str, values: Sequence[Real], expected_size: int) -> np.ndarray:
    raw = np.asarray(values)
    if raw.ndim != 1 or raw.size != expected_size:
        raise TaylorDual3InputError(f"{name} must be a vector of length {expected_size}")
    if raw.dtype.kind not in "iuf":
        raise TaylorDual3InputError(f"{name} must contain real numeric scalars")
    result = np.asarray(raw, dtype=float)
    if not np.all(np.isfinite(result)):
        raise TaylorDual3InputError(f"{name} must contain only finite values")
    return result


def _finite_point(point: Sequence[Real]) -> tuple[float, float, float, float]:
    values = _finite_vector("x", point, N_SPATIAL)
    return tuple(float(value) for value in values)  # type: ignore[return-value]


def full_t4_decoder_contract(N: int, K: int) -> dict[str, Any]:
    """Return the generated full-T4 layout and identify exact C2-bundle matches."""

    N = _strict_integer("N", N, 1)
    K = _strict_integer("K", K, 1)
    upstream = _load_pinned_upstream()
    layout = upstream.free_layout(N, K)
    modes = upstream.real_fourier_modes(N)
    result = {
        "N": N,
        "K": K,
        "basis": {
            "labels": [mode["label"] for mode in modes],
            "mode_wavevectors": [list(mode["wavevector"]) for mode in modes],
        },
        "modes": modes,
        "free_layout": layout,
        "free_coordinate_dimension": layout["free_coordinate_dimension"],
        "contract_source": "v5.6.7 general full-T4 layout with v5.6.4.4 C2 radial formulas",
        "matches_pinned_c2_bundle_contract": False,
    }
    pinned = _load_c2_bundle()["pointwise_decoder_contract_by_N"].get(str(N))
    if pinned is not None and int(pinned["K"]) == K:
        pinned_blocks = {
            name: {
                "start": int(specification["start"]),
                "stop": int(specification["stop"]),
                "shape": [int(value) for value in specification["shape"]],
            }
            for name, specification in pinned["free_layout"]["blocks"].items()
        }
        generated_blocks = layout["blocks"]
        same = (
            pinned_blocks == generated_blocks
            and int(pinned["free_coordinate_dimension"]) == layout["free_coordinate_dimension"]
            and list(pinned["basis"]["labels"]) == result["basis"]["labels"]
            and [list(map(int, vector)) for vector in pinned["basis"]["mode_wavevectors"]]
            == result["basis"]["mode_wavevectors"]
        )
        if not same:
            raise DualLocalActionError(f"generated decoder contract disagrees with pinned C2 bundle at N={N}")
        result["contract_source"] = "byte-pinned v5.6.4.4 C2 bundle"
        result["matches_pinned_c2_bundle_contract"] = True
    return result


def _free_block_td3(
    free: np.ndarray,
    tangent: np.ndarray,
    contract: Mapping[str, Any],
    name: str,
) -> np.ndarray:
    blocks = contract["free_layout"]["blocks"]
    if name not in blocks:
        raise TaylorDual3InputError(f"unknown free-data block {name!r}")
    specification = blocks[name]
    start = int(specification["start"])
    stop = int(specification["stop"])
    shape = tuple(int(value) for value in specification["shape"])
    primal = free[start:stop].reshape(shape)
    dual = tangent[start:stop].reshape(shape)
    result = np.empty(shape, dtype=object)
    for index in np.ndindex(shape):
        result[index] = TaylorDual3.constant(float(primal[index])) + TaylorDual3.eta(float(dual[index]))
    return result


def _spectral_td3(
    coefficients: np.ndarray,
    modes: Sequence[Mapping[str, Any]],
    point: tuple[float, float, float, float],
) -> np.ndarray:
    if coefficients.ndim < 1 or coefficients.shape[0] != len(modes):
        raise TaylorDual3InputError("spectral coefficient leading dimension must equal the mode count")
    variables = tuple(TaylorDual3.variable(axis) for axis in range(N_SPATIAL))
    trailing_shape = coefficients.shape[1:]
    result = np.empty(trailing_shape, dtype=object)
    for index in np.ndindex(trailing_shape):
        result[index] = TaylorDual3.constant(0.0)
    for mode_index, mode in enumerate(modes):
        kind = mode["kind"]
        wavevector = tuple(int(value) for value in mode["wavevector"])
        if kind == "1":
            basis = TaylorDual3.constant(1.0)
        else:
            phase = TaylorDual3.constant(sum(k * x for k, x in zip(wavevector, point)))
            for axis, k in enumerate(wavevector):
                if k:
                    phase = phase + k * variables[axis]
            if kind == "cos":
                basis = phase.cos()
            elif kind == "sin":
                basis = phase.sin()
            else:
                raise DualLocalActionError(f"unknown full-T4 mode kind {kind!r}")
        for index in np.ndindex(trailing_shape):
            result[index] = result[index] + coefficients[(mode_index,) + index] * basis
    return result


def _transpose(matrix: Sequence[Sequence[Any]]) -> tuple[tuple[Any, ...], ...]:
    if not matrix or not matrix[0]:
        raise TaylorDual3InputError("matrix must be non-empty")
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise TaylorDual3InputError("matrix rows must have equal length")
    return tuple(tuple(matrix[i][j] for i in range(len(matrix))) for j in range(columns))


def _matmul(
    left: Sequence[Sequence[Any]],
    right: Sequence[Sequence[Any]],
    zero: Any,
) -> tuple[tuple[Any, ...], ...]:
    if not left or not right or not left[0] or not right[0]:
        raise TaylorDual3InputError("matrices must be non-empty")
    inner = len(left[0])
    if any(len(row) != inner for row in left) or len(right) != inner:
        raise TaylorDual3InputError("matrix dimensions do not compose")
    columns = len(right[0])
    if any(len(row) != columns for row in right):
        raise TaylorDual3InputError("matrix rows must have equal length")
    return tuple(
        tuple(sum((left[i][k] * right[k][j] for k in range(inner)), zero) for j in range(columns))
        for i in range(len(left))
    )


def _matvec(matrix: Sequence[Sequence[Any]], vector: Sequence[Any], zero: Any) -> tuple[Any, ...]:
    if any(len(row) != len(vector) for row in matrix):
        raise TaylorDual3InputError("matrix-vector dimensions do not compose")
    return tuple(sum((entry * value for entry, value in zip(row, vector)), zero) for row in matrix)


def _dot(left: Sequence[Any], right: Sequence[Any], zero: Any) -> Any:
    if len(left) != len(right):
        raise TaylorDual3InputError("dot-product dimensions differ")
    return sum((a * b for a, b in zip(left, right)), zero)


def _sym_matrix(values: Sequence[Any], dimension: int, zero: Any) -> tuple[tuple[Any, ...], ...]:
    pairs = SYMMETRIC4 if dimension == 4 else SYMMETRIC5 if dimension == 5 else None
    if pairs is None or len(values) != len(pairs):
        raise TaylorDual3InputError("symmetric-vector dimension mismatch")
    result = [[zero for _ in range(dimension)] for _ in range(dimension)]
    for value, (i, j) in zip(values, pairs):
        result[i][j] = value
        result[j][i] = value
    return tuple(tuple(row) for row in result)


def _sym_vector(matrix: Sequence[Sequence[Any]]) -> tuple[Any, ...]:
    dimension = len(matrix)
    pairs = SYMMETRIC4 if dimension == 4 else SYMMETRIC5 if dimension == 5 else None
    if pairs is None:
        raise TaylorDual3InputError("symmetric matrix must be 4x4 or 5x5")
    return tuple(matrix[i][j] for i, j in pairs)


def _hat(vector: Sequence[Any], zero: Any) -> tuple[tuple[Any, ...], ...]:
    if len(vector) != 3:
        raise TaylorDual3InputError("hat expects three components")
    x, y, z = vector
    return ((zero, -z, y), (z, zero, -x), (-y, x, zero))


def _vee(matrix: Sequence[Sequence[Any]]) -> tuple[Any, Any, Any]:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise TaylorDual3InputError("vee expects a 3x3 matrix")
    return matrix[2][1], matrix[0][2], matrix[1][0]


def _vee_checked_td3(
    matrix: Sequence[Sequence[TaylorDual3]],
    context: str,
) -> tuple[TaylorDual3, TaylorDual3, TaylorDual3]:
    """Apply vee only after guarded coefficient skew-symmetry through the two-jet."""

    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise TaylorDual3InputError("checked vee expects a 3x3 matrix")
    residual = max(
        _coefficient_residual_through_spatial_degree(
            matrix[i][j] + matrix[j][i], 0.0, 2
        )
        for i in range(3)
        for j in range(i, 3)
    )
    if residual > 2.0e-10:
        raise TaylorDual3NumericalError(
            f"{context} is not skew-symmetric through the declared two-jet: {residual:.3e}"
        )
    return _vee(matrix)


def _inverse_td3(matrix: Sequence[Sequence[TaylorDual3]]) -> tuple[tuple[TaylorDual3, ...], ...]:
    dimension = len(matrix)
    if dimension == 0 or any(len(row) != dimension for row in matrix):
        raise TaylorDual3InputError("inverse expects a non-empty square matrix")
    zero = TaylorDual3.constant(0.0)
    one = TaylorDual3.constant(1.0)
    augmented = [
        list(row) + [one if i == j else zero for j in range(dimension)]
        for i, row in enumerate(matrix)
    ]
    for column in range(dimension):
        pivot_row = max(range(column, dimension), key=lambda row: abs(augmented[row][column].body))
        if augmented[pivot_row][column].body == 0.0:
            raise TaylorDual3InputError("matrix primal body is singular")
        augmented[column], augmented[pivot_row] = augmented[pivot_row], augmented[column]
        pivot_inverse = augmented[column][column].inverse()
        augmented[column] = [entry * pivot_inverse for entry in augmented[column]]
        for row in range(dimension):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(augmented[row], augmented[column])
            ]
    return tuple(tuple(row[dimension:]) for row in augmented)


def _det3(matrix: Sequence[Sequence[Any]]) -> Any:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise TaylorDual3InputError("det3 expects a 3x3 matrix")
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def _matrix_add(
    left: Sequence[Sequence[Any]], right: Sequence[Sequence[Any]]
) -> tuple[tuple[Any, ...], ...]:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise TaylorDual3InputError("matrix dimensions differ")
    return tuple(tuple(a + b for a, b in zip(left_row, right_row)) for left_row, right_row in zip(left, right))


def _matrix_subtract(
    left: Sequence[Sequence[Any]], right: Sequence[Sequence[Any]]
) -> tuple[tuple[Any, ...], ...]:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise TaylorDual3InputError("matrix dimensions differ")
    return tuple(tuple(a - b for a, b in zip(left_row, right_row)) for left_row, right_row in zip(left, right))


def _partial_matrix(
    matrix: Sequence[Sequence[TaylorDual3]], axis: int
) -> tuple[tuple[TaylorDual3, ...], ...]:
    return tuple(tuple(entry.partial(axis) for entry in row) for row in matrix)


def _decoder_vectors_and_blocks(
    free: Sequence[Real],
    tangent: Sequence[Real],
    N: int,
    K: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any], dict[str, np.ndarray]]:
    contract = full_t4_decoder_contract(N, K)
    dimension = int(contract["free_coordinate_dimension"])
    free_vector = _finite_vector("free", free, dimension)
    tangent_vector = _finite_vector("tangent", tangent, dimension)
    blocks = {
        name: _free_block_td3(free_vector, tangent_vector, contract, name)
        for name in contract["free_layout"]["blocks"]
    }
    return free_vector, tangent_vector, contract, blocks


def decode_common_first_boundary_td3(
    free: Sequence[Real],
    tangent: Sequence[Real],
    N: int,
    K: int,
    x: Sequence[Real],
) -> dict[str, Any]:
    """Decode both common-first boundary sides as spatial/eta Taylor fields.

    Returned Taylor objects are intended for value, JVP, and spatial derivatives
    only through order two.  Degree three is retained internally so derivatives
    of Y, S, and R still carry complete second spatial jets.
    """

    _free, _tangent, contract, blocks = _decoder_vectors_and_blocks(free, tangent, N, K)
    point = _finite_point(x)
    modes = contract["modes"]
    zero = TaylorDual3.constant(0.0)
    one = TaylorDual3.constant(1.0)

    gamma_vector = _spectral_td3(blocks["common.gamma"], modes, point)
    gamma = _sym_matrix(tuple(gamma_vector), 4, zero)
    T = _spectral_td3(blocks["common.T"], modes, point)[0]
    log_omega = _spectral_td3(blocks["common.log_Omega"], modes, point)[0]
    varphi_e0 = tuple(_spectral_td3(blocks["common.varphi_E0"], modes, point))
    A_e0_array = _spectral_td3(blocks["common.A_E0"], modes, point)
    A_e0 = tuple(tuple(A_e0_array[mu, a] for a in range(3)) for mu in range(4))
    q = tuple(_spectral_td3(blocks["Q_frame.q"], modes, point))
    S = so3_exp(q)
    S_transpose = _transpose(S)
    dS = tuple(_partial_matrix(S, mu) for mu in range(4))
    varphi = _matvec(S, varphi_e0, zero)
    A_common = []
    for mu in range(4):
        rotated = _matmul(_matmul(S, _hat(A_e0[mu], zero), zero), S_transpose, zero)
        frame_term = _matmul(dS[mu], S_transpose, zero)
        A_common.append(
            _vee_checked_td3(
                _matrix_subtract(rotated, frame_term),
                f"common A frame at axis {mu}",
            )
        )
    A_common_tuple = tuple(A_common)

    time_gradient = tuple(T.partial(mu) + (one if mu == 0 else zero) for mu in range(4))
    gamma_inverse = _inverse_td3(gamma)
    inverse_time_gradient = _matvec(gamma_inverse, time_gradient, zero)
    normalization = (-_dot(time_gradient, inverse_time_gradient, zero)).sqrt()
    u_covector = tuple(-entry / normalization for entry in time_gradient)
    u_vector = _matvec(gamma_inverse, u_covector, zero)
    E0_columns: list[tuple[TaylorDual3, ...]] = []
    for column in range(3):
        candidate = [one if row == column + 1 else zero for row in range(4)]
        candidate = [candidate[row] + u_vector[row] * u_covector[column + 1] for row in range(4)]
        for previous in E0_columns:
            gamma_candidate = _matvec(gamma, candidate, zero)
            projection = _dot(previous, gamma_candidate, zero)
            candidate = [entry - projection * previous[row] for row, entry in enumerate(candidate)]
        gamma_candidate = _matvec(gamma, candidate, zero)
        candidate_norm = _dot(candidate, gamma_candidate, zero).sqrt()
        E0_columns.append(tuple(entry / candidate_norm for entry in candidate))
    E0 = tuple(tuple(E0_columns[column][row] for column in range(3)) for row in range(4))
    E_Q = _matmul(E0, S_transpose, zero)

    sides: dict[str, Any] = {}
    for side in SIDES:
        Y = _spectral_td3(blocks[f"{side}.Y"], modes, point)[0]
        Y_first = tuple(Y.partial(mu) for mu in range(4))
        metric_free = tuple(_spectral_td3(blocks[f"{side}.metric_free"], modes, point))
        adapted_cross = metric_free[:4]
        normal_metric = metric_free[4]
        metric_rows = [[zero for _ in range(5)] for _ in range(5)]
        for mu in range(4):
            for nu in range(4):
                metric_rows[mu][nu] = (
                    gamma[mu][nu]
                    - adapted_cross[mu] * Y_first[nu]
                    - Y_first[mu] * adapted_cross[nu]
                    + normal_metric * Y_first[mu] * Y_first[nu]
                )
            cross = adapted_cross[mu] - normal_metric * Y_first[mu]
            metric_rows[mu][4] = cross
            metric_rows[4][mu] = cross
        metric_rows[4][4] = normal_metric
        metric = tuple(tuple(row) for row in metric_rows)

        r_e0 = tuple(_spectral_td3(blocks[f"{side}.r_E0"], modes, point))
        R0 = so3_exp(r_e0)
        R0_transpose = _transpose(R0)
        dR0 = tuple(_partial_matrix(R0, mu) for mu in range(4))
        R = _matmul(S, R0, zero)
        R_transpose = _transpose(R)
        dR = tuple(
            _matrix_add(
                _matmul(dS[mu], R0, zero),
                _matmul(S, dR0[mu], zero),
            )
            for mu in range(4)
        )

        phi_source_full = _matvec(R_transpose, varphi, zero)
        phi_source = _matvec(R0_transpose, varphi_e0, zero)
        A_source_full = []
        A_source = []
        for mu in range(4):
            full_rotated = _matmul(
                _matmul(R_transpose, _hat(A_common_tuple[mu], zero), zero),
                R,
                zero,
            )
            full_frame = _matmul(R_transpose, dR[mu], zero)
            A_source_full.append(
                _vee_checked_td3(
                    _matrix_add(full_rotated, full_frame),
                    f"{side} full source frame at axis {mu}",
                )
            )
            reduced_rotated = _matmul(
                _matmul(R0_transpose, _hat(A_e0[mu], zero), zero),
                R0,
                zero,
            )
            reduced_frame = _matmul(R0_transpose, dR0[mu], zero)
            A_source.append(
                _vee_checked_td3(
                    _matrix_add(reduced_rotated, reduced_frame),
                    f"{side} reduced source frame at axis {mu}",
                )
            )
        A_source_full_tuple = tuple(A_source_full)
        A_source_tuple = tuple(A_source)
        cancellation_residual = max(
            [
                _coefficient_residual_through_spatial_degree(a, b, 2)
                for a, b in zip(phi_source_full, phi_source)
            ]
            + [
                _coefficient_residual_through_spatial_degree(
                    A_source_full_tuple[mu][a], A_source_tuple[mu][a], 2
                )
                for mu in range(4)
                for a in range(3)
            ]
        )
        if cancellation_residual > 2.0e-10:
            raise TaylorDual3NumericalError(
                f"common-frame cancellation residual {cancellation_residual:.3e} exceeds guarded tolerance"
            )

        A_perp = tuple(_spectral_td3(blocks[f"{side}.A_perp"], modes, point))
        A_full = tuple(
            tuple(A_source_tuple[mu][a] - Y_first[mu] * A_perp[a] for a in range(3))
            for mu in range(4)
        ) + (A_perp,)
        B_array = _spectral_td3(blocks[f"{side}.B0_full"], modes, point)
        B_full = tuple(tuple(B_array[position, a] for a in range(3)) for position in range(10))
        J1 = tuple(_spectral_td3(blocks[f"{side}.boundary_jet_J1"], modes, point))
        C_array = _spectral_td3(blocks[f"{side}.interior_bump_C"], modes, point)
        C = tuple(tuple(C_array[k, channel] for channel in range(64)) for k in range(contract["K"]))
        X64_trace = (
            _sym_vector(metric)
            + (log_omega,)
            + phi_source
            + tuple(A_full[mu][a] for mu in range(5) for a in range(3))
            + tuple(B_full[position][a] for position in range(10) for a in range(3))
        )
        if len(X64_trace) != 64:
            raise DualLocalActionError("boundary trace channel count drift")
        sides[side] = {
            "Y": Y,
            "Y_first": Y_first,
            "metric_trace": metric,
            "log_Omega_trace": log_omega,
            "phi_trace": phi_source,
            "A_trace_full": A_full,
            "B_trace_full": B_full,
            "boundary_jet_J1": J1,
            "interior_bump_C": C,
            "r_E0": r_e0,
            "R0": R0,
            "dR0": dR0,
            "R_source_to_Q": R,
            "dR_source_to_Q": dR,
            "phi_source_full_formula": phi_source_full,
            "A_source_full_formula": A_source_full_tuple,
            "common_frame_cancellation_two_jet_max_abs_coefficient_residual": cancellation_residual,
            "X64_trace": X64_trace,
        }

    return {
        "contract": contract,
        "x": point,
        "common": {
            "gamma": gamma,
            "T": T,
            "log_Omega": log_omega,
            "varphi_E0": varphi_e0,
            "A_E0": A_e0,
            "q": q,
            "S_Q": S,
            "dS_Q": dS,
            "varphi": varphi,
            "A_Sigma": A_common_tuple,
            "E0": E0,
            "E_Q": E_Q,
        },
        "sides": sides,
    }


def _reference_metric_td3() -> tuple[tuple[TaylorDual3, ...], ...]:
    zero = TaylorDual3.constant(0.0)
    return tuple(
        tuple(
            TaylorDual3.constant(REFERENCE_METRIC_DIAGONAL[i]) if i == j else zero
            for j in range(5)
        )
        for i in range(5)
    )


def _reference_x64_td3() -> tuple[TaylorDual3, ...]:
    zero = TaylorDual3.constant(0.0)
    return _sym_vector(_reference_metric_td3()) + tuple(zero for _ in range(49))


def _collar_ambient_x64(
    boundary_side: Mapping[str, Any],
    rho: float,
    K: int,
) -> tuple[RhoJet2, ...]:
    upstream = _load_pinned_upstream()
    profiles = upstream.radial_profiles(rho, K)
    h0 = RhoJet2(*[float(value) for value in profiles["h0"]])
    h1 = RhoJet2(*[float(value) for value in profiles["h1"]])
    bumps = tuple(
        RhoJet2(
            float(profiles["bumps"][0, k]),
            float(profiles["bumps"][1, k]),
            float(profiles["bumps"][2, k]),
        )
        for k in range(K)
    )
    reference = _reference_x64_td3()
    trace = boundary_side["X64_trace"]
    J1 = boundary_side["boundary_jet_J1"]
    C = boundary_side["interior_bump_C"]
    if len(trace) != 64 or len(J1) != 64 or len(C) != K or any(len(row) != 64 for row in C):
        raise DualLocalActionError("C2 collar input channel shape drift")
    result = []
    for channel in range(64):
        value = RhoJet2(reference[channel])
        value = value + h0 * (trace[channel] - reference[channel])
        value = value + h1 * J1[channel]
        for k in range(K):
            value = value + bumps[k] * C[k][channel]
        result.append(value)
    return tuple(result)


def _pullback_x64_and_reference15(
    ambient: Sequence[RhoJet2],
    Y_first: Sequence[TaylorDual3],
    side: str,
) -> tuple[tuple[RhoJet2, ...], tuple[RhoJet2, ...]]:
    if side not in SIDE_RADIAL_SIGN:
        raise TaylorDual3InputError(f"side must be one of {SIDES}")
    if len(ambient) != 64 or len(Y_first) != 4:
        raise TaylorDual3InputError("pullback expects X64 and four embedding-gradient components")
    zero = RhoJet2(0.0)
    one = RhoJet2(1.0)
    jacobian_rows = [[zero for _ in range(5)] for _ in range(5)]
    for i in range(4):
        jacobian_rows[i][i] = one
        jacobian_rows[4][i] = RhoJet2(Y_first[i])
    jacobian_rows[4][4] = RhoJet2(SIDE_RADIAL_SIGN[side])
    jacobian = tuple(tuple(row) for row in jacobian_rows)
    jacobian_transpose = _transpose(jacobian)

    metric = _sym_matrix(tuple(ambient[:15]), 5, zero)
    pulled_metric = _matmul(_matmul(jacobian_transpose, metric, zero), jacobian, zero)
    connection = tuple(
        tuple(ambient[19 + 3 * M + a] for a in range(3))
        for M in range(5)
    )
    pulled_connection = _matmul(jacobian_transpose, connection, zero)
    B = tuple(
        tuple(ambient[34 + 3 * position + a] for a in range(3))
        for position in range(10)
    )
    pulled_B = []
    for target in B_TRIPLES:
        row = [zero, zero, zero]
        for source_position, source in enumerate(B_TRIPLES):
            minor = _det3(tuple(tuple(jacobian[s][t] for t in target) for s in source))
            row = [row[a] + minor * B[source_position][a] for a in range(3)]
        pulled_B.append(tuple(row))

    actual = (
        _sym_vector(pulled_metric)
        + tuple(ambient[15:19])
        + tuple(pulled_connection[M][a] for M in range(5) for a in range(3))
        + tuple(pulled_B[position][a] for position in range(10) for a in range(3))
    )
    reference = tuple(tuple(RhoJet2(entry) for entry in row) for row in _reference_metric_td3())
    pulled_reference = _matmul(_matmul(jacobian_transpose, reference, zero), jacobian, zero)
    reference15 = _sym_vector(pulled_reference)
    if len(actual) != 64 or len(reference15) != 15:
        raise DualLocalActionError("pulled channel count drift")
    return actual, reference15


def _rho_channels_payload(channels: Sequence[RhoJet2]) -> dict[str, Any]:
    count = len(channels)
    units = tuple(
        tuple(int(axis == selected) for axis in range(N_SPATIAL))
        for selected in range(N_SPATIAL)
    )

    def layer(eta_order: int) -> dict[str, np.ndarray]:
        values = np.asarray(
            [channel.value.derivative(ZERO_ALPHA, eta_order) for channel in channels],
            dtype=float,
        )
        first = np.zeros((5, count), dtype=float)
        second = np.zeros((5, 5, count), dtype=float)
        for mu in range(4):
            first[mu] = [channel.value.derivative(units[mu], eta_order) for channel in channels]
            for nu in range(4):
                alpha = _alpha_add(units[mu], units[nu])
                second[mu, nu] = [channel.value.derivative(alpha, eta_order) for channel in channels]
            mixed = [channel.rho_first.derivative(units[mu], eta_order) for channel in channels]
            second[mu, 4] = mixed
            second[4, mu] = mixed
        first[4] = [channel.rho_first.derivative(ZERO_ALPHA, eta_order) for channel in channels]
        second[4, 4] = [channel.rho_second.derivative(ZERO_ALPHA, eta_order) for channel in channels]
        return {"value": values, "first": first, "second": second}

    return {
        "channel_count": count,
        "rho_td3": tuple(channels),
        "primal": layer(0),
        "eta": layer(1),
    }


def decode_full_t4_collar_point(
    free: Sequence[Real],
    tangent: Sequence[Real],
    N: int,
    K: int,
    x: Sequence[Real],
    rho: Real,
    side: str,
) -> dict[str, Any]:
    """Decode one C2 collar point into separately labelled X64 and X79 jets.

    ``primal`` and ``eta`` each contain ``value``, five first derivatives and
    a 5x5 second-derivative tensor.  ``ambient_X64`` is before pullback;
    ``pulled_X64`` is the physical pulled field; ``pulled_reference_metric15``
    is the extra reference block; ``pulled_X79`` is their ordered concatenation.
    """

    if side not in SIDES:
        raise TaylorDual3InputError(f"side must be one of {SIDES}")
    rho_value = _finite_real("rho", rho)
    if not 0.0 <= rho_value <= 1.0:
        raise TaylorDual3InputError("rho must lie in [0, 1] for the C2 collar")
    boundary = decode_common_first_boundary_td3(free, tangent, N, K, x)
    ambient = _collar_ambient_x64(boundary["sides"][side], rho_value, int(boundary["contract"]["K"]))
    pulled, reference15 = _pullback_x64_and_reference15(
        ambient,
        boundary["sides"][side]["Y_first"],
        side,
    )
    pulled79 = pulled + reference15
    return {
        "N": int(boundary["contract"]["N"]),
        "K": int(boundary["contract"]["K"]),
        "x": boundary["x"],
        "rho": rho_value,
        "side": side,
        "contract_source": boundary["contract"]["contract_source"],
        "boundary": boundary,
        "ambient_X64": _rho_channels_payload(ambient),
        "pulled_X64": _rho_channels_payload(pulled),
        "pulled_reference_metric15": _rho_channels_payload(reference15),
        "pulled_X79": _rho_channels_payload(pulled79),
    }


def _coefficient_residual(value: TaylorDual3, expected: TaylorDual3 | Real) -> float:
    right = TaylorDual3._require(expected)
    keys = set(value._coefficients) | set(right._coefficients)
    return max((abs(value._coefficients.get(key, 0.0) - right._coefficients.get(key, 0.0)) for key in keys), default=0.0)


def _coefficient_residual_through_spatial_degree(
    value: TaylorDual3,
    expected: TaylorDual3 | Real,
    maximum_degree: int,
) -> float:
    """Compare only the coefficients that contribute to a declared spatial jet."""

    maximum_degree = _strict_integer(
        "maximum_degree", maximum_degree, 0, MAX_SPATIAL_DEGREE
    )
    right = TaylorDual3._require(expected)
    keys = {
        key
        for key in set(value._coefficients) | set(right._coefficients)
        if _alpha_degree(key[1]) <= maximum_degree
    }
    return max(
        (
            abs(value._coefficients.get(key, 0.0) - right._coefficients.get(key, 0.0))
            for key in keys
        ),
        default=0.0,
    )


def _matrix_orthogonality_residual(matrix: Sequence[Sequence[TaylorDual3]]) -> float:
    transpose = tuple(tuple(matrix[j][i] for j in range(3)) for i in range(3))
    product_matrix = _matrix_multiply(transpose, matrix)
    return max(
        _coefficient_residual(product_matrix[i][j], float(i == j))
        for i in range(3)
        for j in range(3)
    )


def _check_mixed_algebra() -> dict[str, Any]:
    x = tuple(TaylorDual3.variable(axis) for axis in range(N_SPATIAL))
    eta = TaylorDual3.eta()
    eta_cubic = eta * x[0] * x[1] * x[2]
    generic_delta = x[0] + 0.2 * x[1] + eta * (1.0 + 0.3 * x[2])
    checks = {
        "spatial_monomial_count": len(ALL_MULTIINDICES),
        "algebra_coefficient_capacity": 2 * len(ALL_MULTIINDICES),
        "eta_times_mixed_cubic_coefficient": eta_cubic.coefficient((1, 1, 1, 0), 1),
        "eta_times_pure_cubic_coefficient": (eta * x[0] ** 3).coefficient((3, 0, 0, 0), 1),
        "eta_squared_zero": not (eta * eta).coefficients,
        "spatial_quartic_zero": not (x[0] * x[1] * x[2] * x[3]).coefficients,
        "generic_delta_fifth_power_zero": not (generic_delta**5).coefficients,
    }
    checks["pass"] = bool(
        checks["spatial_monomial_count"] == 35
        and checks["algebra_coefficient_capacity"] == 70
        and checks["eta_times_mixed_cubic_coefficient"] == 1.0
        and checks["eta_times_pure_cubic_coefficient"] == 1.0
        and checks["eta_squared_zero"]
        and checks["spatial_quartic_zero"]
        and checks["generic_delta_fifth_power_zero"]
    )
    return checks


def _check_fail_closed_inputs() -> dict[str, Any]:
    cases = (
        lambda: TaylorDual3({(0, (0.9, 0, 0, 0)): 1.0}),
        lambda: TaylorDual3({(True, ZERO_ALPHA): 1.0}),
        lambda: TaylorDual3.variable(True),
        lambda: TaylorDual3.constant(float("nan")),
        lambda: exp(object()),
        lambda: TaylorDual3.constant(1.0).evaluate_spatial_layer((float("nan"), 0.0, 0.0, 0.0)),
    )
    rejected = []
    for case in cases:
        try:
            case()
        except (TaylorDual3InputError, TypeError):
            rejected.append(True)
        else:
            rejected.append(False)
    overflow_rejected = False
    try:
        TaylorDual3.constant(1.0e308) * TaylorDual3.constant(1.0e308)
    except TaylorDual3NumericalError:
        overflow_rejected = True
    return {
        "strict_rejection_cases": len(cases),
        "strict_rejection_results": rejected,
        "post_operation_nonfinite_rejected": overflow_rejected,
        "pass": bool(all(rejected) and overflow_rejected),
    }


def _check_analytic_identities() -> dict[str, Any]:
    x0, x1, x2, _ = (TaylorDual3.variable(axis) for axis in range(N_SPATIAL))
    eta = TaylorDual3.eta()
    value = 1.7 + 0.2 * x0 - 0.1 * x1 + 0.03 * x0 * x2 + eta * (0.4 + 0.05 * x1)
    residuals = {
        "inverse": _coefficient_residual(value * value.inverse(), 1.0),
        "exp_inverse": _coefficient_residual(value.exp() * (-value).exp(), 1.0),
        "sin2_plus_cos2": _coefficient_residual(value.sin() ** 2 + value.cos() ** 2, 1.0),
        "sqrt_squared": _coefficient_residual(value.sqrt() ** 2, value),
        "eta_times_spatial_cubic_exp": abs(
            (eta + x0 + x1 + x2).exp().coefficient((1, 1, 1, 0), 1) - 1.0
        ),
    }
    worst = max(residuals.values())
    return {
        "sample_count": len(residuals),
        "coefficient_residuals": residuals,
        "max_abs_coefficient_residual": worst,
        "pass": bool(worst <= SAMPLED_TOLERANCE),
    }


def _check_so3() -> dict[str, Any]:
    eta = TaylorDual3.eta()
    zero_rotation = so3_exp((0.0, 0.0, 0.0))
    origin_residual = max(
        _coefficient_residual(zero_rotation[i][j], float(i == j))
        for i in range(3)
        for j in range(3)
    )
    direction = (0.7, -0.2, 0.5)
    dual_rotation = so3_exp(tuple(component * eta for component in direction))
    expected_skew = (
        (0.0, -direction[2], direction[1]),
        (direction[2], 0.0, -direction[0]),
        (-direction[1], direction[0], 0.0),
    )
    origin_eta_jvp_residual = max(
        abs(dual_rotation[i][j].derivative(ZERO_ALPHA, 1) - expected_skew[i][j])
        for i in range(3)
        for j in range(3)
    )

    x0 = TaylorDual3.variable(0)
    base = (0.2, -0.3, 0.4)
    tangent = (0.11, -0.07, 0.05)
    q = tuple(base[i] + tangent[i] * x0 + tangent[i] * eta for i in range(3))
    sampled_rotation = so3_exp(q)
    orthogonality_residual = _matrix_orthogonality_residual(sampled_rotation)
    eta_spatial_jvp_residual = max(
        abs(
            sampled_rotation[i][j].derivative(ZERO_ALPHA, 1)
            - sampled_rotation[i][j].derivative((1, 0, 0, 0), 0)
        )
        for i in range(3)
        for j in range(3)
    )

    guard_rejects_outside = False
    try:
        so3_exp((SO3_SERIES_BODY_NORM_LIMIT + 0.01, 0.0, 0.0))
    except TaylorDual3InputError:
        guard_rejects_outside = True
    coefficient_guard_rejects_outside = False
    try:
        so3_exp((0.2 + (SO3_SERIES_NONBODY_L1_LIMIT + 0.01) * x0, -0.3, 0.4))
    except TaylorDual3InputError:
        coefficient_guard_rejects_outside = True
    worst = max(origin_residual, origin_eta_jvp_residual, orthogonality_residual, eta_spatial_jvp_residual)
    return {
        "series_body_norm_limit": SO3_SERIES_BODY_NORM_LIMIT,
        "series_nonbody_l1_limit": SO3_SERIES_NONBODY_L1_LIMIT,
        "origin_identity_residual": origin_residual,
        "origin_eta_jvp_residual": origin_eta_jvp_residual,
        "sampled_orthogonality_max_abs_coefficient_residual": orthogonality_residual,
        "sampled_eta_vs_spatial_jvp_residual": eta_spatial_jvp_residual,
        "outside_guard_rejected": guard_rejects_outside,
        "outside_coefficient_guard_rejected": coefficient_guard_rejects_outside,
        "max_abs_sampled_residual": worst,
        "pass": bool(
            worst <= SAMPLED_TOLERANCE
            and guard_rejects_outside
            and coefficient_guard_rejects_outside
        ),
    }


def _sample_safe_free(N: int, K: int) -> tuple[np.ndarray, dict[str, Any]]:
    contract = full_t4_decoder_contract(N, K)
    free = np.zeros(int(contract["free_coordinate_dimension"]), dtype=float)

    def block(name: str) -> np.ndarray:
        specification = contract["free_layout"]["blocks"][name]
        return free[int(specification["start"]):int(specification["stop"])].reshape(
            tuple(int(value) for value in specification["shape"])
        )

    block("common.gamma")[0, [0, 4, 7, 9]] = (-1.2, 1.1, 1.3, 1.4)
    block("common.varphi_E0")[0] = (0.4, -0.2, 0.3)
    for side in SIDES:
        block(f"{side}.metric_free")[0, 4] = 1.17
    return free, contract


def _td3_layer_array(value: Any, eta_order: int) -> np.ndarray:
    """Convert a nested TaylorDual3 result into one numeric coefficient layer."""

    eta_order = _strict_integer("eta_order", eta_order, 0, 1)
    array = np.asarray(value, dtype=object)
    flattened = []
    for entry in array.flat:
        if not isinstance(entry, TaylorDual3):
            raise DualLocalActionError("decoder field contains a non-TaylorDual3 entry")
        flattened.append(entry.derivative(ZERO_ALPHA, eta_order))
    return np.asarray(flattened, dtype=float).reshape(array.shape)


def _numeric_x64_from_pointwise_side(side: Mapping[str, Any], point_index: int) -> np.ndarray:
    metric = np.asarray(side["g_trace"][point_index], dtype=float)
    return np.concatenate(
        (
            np.asarray([metric[i, j] for i, j in SYMMETRIC5], dtype=float),
            np.asarray([side["log_Omega_trace"][point_index]], dtype=float),
            np.asarray(side["phi_trace"][point_index], dtype=float).reshape(3),
            np.asarray(side["A_trace_full"][point_index], dtype=float).reshape(15),
            np.asarray(side["B_trace_full"][point_index], dtype=float).reshape(30),
        )
    )


def _pointwise_field_pairs(
    decoded: Mapping[str, Any],
    oracle: Mapping[str, Any],
    point_index: int,
) -> list[tuple[str, Any, np.ndarray]]:
    pairs: list[tuple[str, Any, np.ndarray]] = []
    for name in ("gamma", "log_Omega", "varphi", "A_Sigma", "E0", "E_Q", "S_Q"):
        pairs.append((f"common.{name}", decoded["common"][name], np.asarray(oracle["common"][name][point_index])))
    aliases = (
        ("Y_first", "Y_first"),
        ("metric_trace", "g_trace"),
        ("log_Omega_trace", "log_Omega_trace"),
        ("phi_trace", "phi_trace"),
        ("A_trace_full", "A_trace_full"),
        ("B_trace_full", "B_trace_full"),
        ("boundary_jet_J1", "boundary_jet_J1"),
        ("interior_bump_C", "interior_bump_C"),
        ("R_source_to_Q", "R_source_to_Q"),
        ("dR_source_to_Q", "dR_source_to_Q"),
    )
    for side in SIDES:
        for mine, theirs in aliases:
            pairs.append(
                (
                    f"{side}.{theirs}",
                    decoded["sides"][side][mine],
                    np.asarray(oracle["sides"][side][theirs][point_index]),
                )
            )
        pairs.append(
            (
                f"{side}.X64_trace",
                decoded["sides"][side]["X64_trace"],
                _numeric_x64_from_pointwise_side(oracle["sides"][side], point_index),
            )
        )
    return pairs


def _check_pointwise_oracle() -> dict[str, Any]:
    """Sample bodies and eta-JVPs against the byte-pinned SciPy oracle."""

    oracle_module = _load_pinned_pointwise_oracle()
    bundle = _load_c2_bundle()
    points = np.asarray(
        ((0.13, -0.27, 0.21, -0.08), (0.41, 0.19, -0.31, 0.07)),
        dtype=float,
    )
    step = 2.0e-6
    rows: dict[str, Any] = {}
    worst_body = 0.0
    worst_jvp = 0.0
    worst_dS = 0.0
    field_comparisons = 0
    members = {int(member["N"]): member for member in bundle["primary_members"]}
    for N in (1, 2, 3):
        member = members[N]
        contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
        free = _decode_pinned_f64(member["authoritative_free_central_f64le"])
        curve = next(
            item
            for item in member["curves"]
            if item["name"] == "joint_all_primitive_classes_control_candidate"
        )
        tangent = _decode_pinned_f64(curve["authoritative_free_tangent_f64le"])
        expected_dimension = int(contract["free_coordinate_dimension"])
        if free.shape != (expected_dimension,) or tangent.shape != free.shape:
            raise DualLocalActionError(f"C2 oracle vector shape drift at N={N}")
        center = oracle_module.decode_pointwise_boundary(free, contract, points)
        plus = oracle_module.decode_pointwise_boundary(free + step * tangent, contract, points)
        minus = oracle_module.decode_pointwise_boundary(free - step * tangent, contract, points)
        tables = oracle_module.fourier_tables(contract["basis"], points)
        layout = contract["free_layout"]["blocks"]
        q_coefficients = oracle_module._free_get(free, layout, "Q_frame.q")
        _oracle_S, oracle_dS = oracle_module._rotation_field(q_coefficients, tables)
        row_body = 0.0
        row_jvp = 0.0
        row_dS = 0.0
        for point_index, point in enumerate(points):
            decoded = decode_common_first_boundary_td3(free, tangent, N, N, point)
            center_pairs = _pointwise_field_pairs(decoded, center, point_index)
            plus_fields = {name: expected for name, _actual, expected in _pointwise_field_pairs(decoded, plus, point_index)}
            minus_fields = {name: expected for name, _actual, expected in _pointwise_field_pairs(decoded, minus, point_index)}
            for name, actual, expected in center_pairs:
                body = _td3_layer_array(actual, 0)
                eta = _td3_layer_array(actual, 1)
                if body.shape != expected.shape:
                    raise DualLocalActionError(f"pointwise oracle shape drift for {name} at N={N}")
                body_residual = float(np.max(np.abs(body - expected))) if body.size else 0.0
                numeric_jvp = (plus_fields[name] - minus_fields[name]) / (2.0 * step)
                jvp_residual = float(np.max(np.abs(eta - numeric_jvp))) if eta.size else 0.0
                row_body = max(row_body, body_residual)
                row_jvp = max(row_jvp, jvp_residual)
                field_comparisons += 1
            dS_body = np.asarray(
                [
                    [
                        [decoded["common"]["dS_Q"][mu][i][j].body for j in range(3)]
                        for i in range(3)
                    ]
                    for mu in range(4)
                ],
                dtype=float,
            )
            row_dS = max(row_dS, float(np.max(np.abs(dS_body - oracle_dS[point_index]))))
        rows[str(N)] = {
            "body_max_abs_residual": row_body,
            "eta_jvp_vs_central_difference_max_abs_residual": row_jvp,
            "dS_vs_scipy_frechet_max_abs_residual": row_dS,
        }
        worst_body = max(worst_body, row_body)
        worst_jvp = max(worst_jvp, row_jvp)
        worst_dS = max(worst_dS, row_dS)
    return {
        "oracle_source_sha256": POINTWISE_ORACLE_SHA256,
        "sampled_N": [1, 2, 3],
        "points_per_N": int(points.shape[0]),
        "central_difference_step": step,
        "field_comparisons": field_comparisons,
        "by_N": rows,
        "body_max_abs_residual": worst_body,
        "eta_jvp_vs_central_difference_max_abs_residual": worst_jvp,
        "dS_vs_scipy_frechet_max_abs_residual": worst_dS,
        "pass": bool(worst_body <= 5.0e-13 and worst_jvp <= 5.0e-9 and worst_dS <= 5.0e-13),
    }


def _check_decoder() -> dict[str, Any]:
    pinned_contracts = {
        str(N): full_t4_decoder_contract(N, N)["matches_pinned_c2_bundle_contract"]
        for N in (1, 2, 3)
    }
    pointwise_oracle = _check_pointwise_oracle()

    _unused, sentinel_contract = _sample_safe_free(3, 3)
    dimension = int(sentinel_contract["free_coordinate_dimension"])
    sentinel_free = np.arange(dimension, dtype=float) * 1.0e-6
    sentinel_tangent = -np.arange(dimension, dtype=float) * 2.0e-7
    sentinel_offsets = True
    expected_start = 0
    for name, specification in sentinel_contract["free_layout"]["blocks"].items():
        start, stop = int(specification["start"]), int(specification["stop"])
        sentinel_block = _free_block_td3(
            sentinel_free, sentinel_tangent, sentinel_contract, name
        )
        flattened = sentinel_block.reshape(-1)
        sentinel_offsets = bool(
            sentinel_offsets
            and start == expected_start
            and stop > start
            and sentinel_block.shape == tuple(specification["shape"])
            and flattened[0].body == sentinel_free[start]
            and flattened[-1].body == sentinel_free[stop - 1]
            and flattened[0].derivative(ZERO_ALPHA, 1) == sentinel_tangent[start]
            and flattened[-1].derivative(ZERO_ALPHA, 1) == sentinel_tangent[stop - 1]
        )
        expected_start = stop
    sentinel_offsets = bool(sentinel_offsets and expected_start == dimension)

    axis_activity = {}
    for N, axis, mode in ((9, 2, 8), (11, 3, 10)):
        free, contract = _sample_safe_free(N, N)
        tangent = np.zeros_like(free)
        specification = contract["free_layout"]["blocks"]["common.log_Omega"]
        block = free[int(specification["start"]):int(specification["stop"])].reshape(
            tuple(specification["shape"])
        )
        block[mode, 0] = 0.1
        decoded = decode_full_t4_collar_point(free, tangent, N, N, (0.0, 0.0, 0.0, 0.0), 0.0, "plus")
        derivative = float(decoded["ambient_X64"]["primal"]["first"][axis, 15])
        axis_activity[f"N{N}_x{axis}"] = derivative

    bundle = _load_c2_bundle()
    member3 = next(member for member in bundle["primary_members"] if int(member["N"]) == 3)
    free3 = _decode_pinned_f64(member3["authoritative_free_central_f64le"])
    curve3 = next(
        curve
        for curve in member3["curves"]
        if curve["name"] == "joint_all_primitive_classes_control_candidate"
    )
    tangent3 = _decode_pinned_f64(curve3["authoritative_free_tangent_f64le"])
    contract3 = full_t4_decoder_contract(3, 3)
    sample_point = (0.13, -0.27, 0.21, -0.08)
    boundary = decode_common_first_boundary_td3(free3, tangent3, 3, 3, sample_point)
    cancellation = max(
        float(
            boundary["sides"][side][
                "common_frame_cancellation_two_jet_max_abs_coefficient_residual"
            ]
        )
        for side in SIDES
    )

    q_specification = contract3["free_layout"]["blocks"]["Q_frame.q"]
    q_zero_free = free3.copy()
    q_zero_tangent = tangent3.copy()
    q_slice = slice(int(q_specification["start"]), int(q_specification["stop"]))
    q_zero_free[q_slice] = 0.0
    q_zero_tangent[q_slice] = 0.0
    q_zero_boundary = decode_common_first_boundary_td3(
        q_zero_free, q_zero_tangent, 3, 3, sample_point
    )
    projected_q_cancellation = max(
        _coefficient_residual(
            boundary["sides"][side][field][index],
            q_zero_boundary["sides"][side][field][index],
        )
        for side in SIDES
        for field in ("phi_trace",)
        for index in range(3)
    )
    projected_q_cancellation = max(
        projected_q_cancellation,
        max(
            _coefficient_residual(
                boundary["sides"][side]["A_trace_full"][mu][a],
                q_zero_boundary["sides"][side]["A_trace_full"][mu][a],
            )
            for side in SIDES
            for mu in range(5)
            for a in range(3)
        ),
    )
    pointwise_module = _load_pinned_pointwise_oracle()
    oracle_contract3 = bundle["pointwise_decoder_contract_by_N"]["3"]
    oracle_with_q = pointwise_module.decode_pointwise_boundary(
        free3, oracle_contract3, np.asarray([sample_point])
    )
    oracle_without_q = pointwise_module.decode_pointwise_boundary(
        q_zero_free, oracle_contract3, np.asarray([sample_point])
    )
    projected_q_numeric_residual = max(
        float(
            np.max(
                np.abs(
                    np.asarray(oracle_with_q["sides"][side][field][0])
                    - np.asarray(oracle_without_q["sides"][side][field][0])
                )
            )
        )
        for side in SIDES
        for field in ("phi_trace", "A_trace_full")
    )

    zero_td3 = TaylorDual3.constant(0.0)
    # Keep q identically zero here so the sentinel cannot pass by common-frame
    # cancellation: only the spatially varying R0 and its Maurer-Cartan term
    # can supply the expected connection contribution.
    side3 = q_zero_boundary["sides"]["plus"]
    r_body = np.asarray([entry.body for entry in side3["r_E0"]], dtype=float)
    r_first = np.asarray([entry.partial(0).body for entry in side3["r_E0"]], dtype=float)
    r_spatial_activity = float(np.max(np.abs(r_first)))
    r_noncommuting_activity = float(np.max(np.abs(np.cross(r_body, r_first))))
    R = side3["R_source_to_Q"]
    R_transpose = _transpose(R)
    A_common = q_zero_boundary["common"]["A_Sigma"]
    rotated_source_matrices = tuple(
        _matmul(
            _matmul(R_transpose, _hat(A_common[mu], zero_td3), zero_td3),
            R,
            zero_td3,
        )
        for mu in range(4)
    )
    frame_source_matrices = tuple(
        _matmul(R_transpose, side3["dR_source_to_Q"][mu], zero_td3)
        for mu in range(4)
    )
    missing_frame_source = tuple(_vee(matrix) for matrix in rotated_source_matrices)
    flipped_frame_source = tuple(
        _vee(_matrix_subtract(rotated_source_matrices[mu], frame_source_matrices[mu]))
        for mu in range(4)
    )
    A_perp = side3["A_trace_full"][4]
    frame_mutants = {}
    for mutant_name, mutant_source in (
        ("missing", missing_frame_source),
        ("flipped", flipped_frame_source),
    ):
        frame_mutants[mutant_name] = tuple(
            tuple(
                mutant_source[mu][a] - side3["Y_first"][mu] * A_perp[a]
                for a in range(3)
            )
            for mu in range(4)
        ) + (A_perp,)
    missing_frame_mutant_failure = max(
        abs(
            frame_mutants["missing"][mu][a].body
            - float(oracle_without_q["sides"]["plus"]["A_trace_full"][0, mu, a])
        )
        for mu in range(5)
        for a in range(3)
    )
    flipped_frame_mutant_failure = max(
        abs(
            frame_mutants["flipped"][mu][a].body
            - float(oracle_without_q["sides"]["plus"]["A_trace_full"][0, mu, a])
        )
        for mu in range(5)
        for a in range(3)
    )

    upstream = _load_pinned_upstream()
    pullback_residual = 0.0
    side_sign_mutant_failure = 0.0
    for side in SIDES:
        decoded = decode_full_t4_collar_point(
            free3, tangent3, 3, 3, sample_point, 0.37, side
        )
        side_boundary = decoded["boundary"]["sides"][side]
        units = tuple(
            tuple(int(axis == selected) for axis in range(4))
            for selected in range(4)
        )
        Y_first = np.asarray([entry.body for entry in side_boundary["Y_first"]])
        Y_second = np.asarray(
            [
                [side_boundary["Y_first"][mu].derivative(units[axis], 0) for axis in range(4)]
                for mu in range(4)
            ]
        )
        Y_third = np.asarray(
            [
                [
                    [
                        side_boundary["Y_first"][mu].derivative(
                            _alpha_add(units[left], units[right]), 0
                        )
                        for right in range(4)
                    ]
                    for left in range(4)
                ]
                for mu in range(4)
            ]
        )
        pullback_arguments = (
            decoded["ambient_X64"]["primal"]["value"],
            decoded["ambient_X64"]["primal"]["first"],
            decoded["ambient_X64"]["primal"]["second"],
            Y_first,
            Y_second,
            Y_third,
        )
        expected_pullback = upstream.pulled_back_two_jet(*pullback_arguments, side)
        wrong_side = "minus" if side == "plus" else "plus"
        sign_mutant = upstream.pulled_back_two_jet(*pullback_arguments, wrong_side)
        for derivative in ("value", "first", "second"):
            actual = decoded["pulled_X79"]["primal"][derivative]
            pullback_residual = max(
                pullback_residual,
                float(np.max(np.abs(actual - expected_pullback[derivative]))),
            )
            side_sign_mutant_failure = max(
                side_sign_mutant_failure,
                float(np.max(np.abs(actual - sign_mutant[derivative]))),
            )

    contaminated_vee_rejected = False
    contaminated = (
        (TaylorDual3.constant(1.0e-4), zero_td3, zero_td3),
        (zero_td3, zero_td3, zero_td3),
        (zero_td3, zero_td3, zero_td3),
    )
    try:
        _vee_checked_td3(contaminated, "deliberate symmetric contamination")
    except TaylorDual3NumericalError:
        contaminated_vee_rejected = True

    B_one_hot_residual = 0.0
    radial_triple = B_TRIPLES.index((0, 1, 4))
    tangential_triple = B_TRIPLES.index((0, 1, 2))
    for source_position, expects_side_sign in (
        (radial_triple, True),
        (tangential_triple, False),
    ):
        ambient_one_hot = [RhoJet2(0.0) for _ in range(64)]
        ambient_one_hot[34 + 3 * source_position] = RhoJet2(1.0)
        for side in SIDES:
            pulled_one_hot, _reference = _pullback_x64_and_reference15(
                ambient_one_hot,
                (zero_td3, zero_td3, zero_td3, zero_td3),
                side,
            )
            expected = SIDE_RADIAL_SIGN[side] if expects_side_sign else 1.0
            for target_position in range(10):
                for component in range(3):
                    target = 34 + 3 * target_position + component
                    wanted = expected if (target_position, component) == (source_position, 0) else 0.0
                    B_one_hot_residual = max(
                        B_one_hot_residual,
                        abs(pulled_one_hot[target].value.body - wanted),
                    )

    member1 = next(member for member in bundle["primary_members"] if int(member["N"]) == 1)
    free1 = _decode_pinned_f64(member1["authoritative_free_central_f64le"])
    curve1 = next(
        curve
        for curve in member1["curves"]
        if curve["name"] == "joint_all_primitive_classes_control_candidate"
    )
    tangent1 = _decode_pinned_f64(curve1["authoritative_free_tangent_f64le"])
    endpoint_shapes = {}
    endpoints_finite = True
    endpoint_c2_residual = 0.0
    for rho in (0.0, 1.0):
        decoded = decode_full_t4_collar_point(
            free1,
            tangent1,
            1,
            1,
            (0.2, -0.1, 0.3, -0.4),
            rho,
            "minus",
        )
        endpoint_shapes[str(rho)] = {
            name: int(decoded[name]["channel_count"])
            for name in ("ambient_X64", "pulled_X64", "pulled_reference_metric15", "pulled_X79")
        }
        endpoints_finite = endpoints_finite and all(
            bool(np.all(np.isfinite(decoded[name][layer][derivative])))
            for name in ("ambient_X64", "pulled_X64", "pulled_reference_metric15", "pulled_X79")
            for layer in ("primal", "eta")
            for derivative in ("value", "first", "second")
        )
        ambient = decoded["ambient_X64"]
        if rho == 0.0:
            trace = decoded["boundary"]["sides"]["minus"]["X64_trace"]
            J1 = decoded["boundary"]["sides"]["minus"]["boundary_jet_J1"]
            endpoint_c2_residual = max(
                endpoint_c2_residual,
                max(
                    _coefficient_residual(channel.value, expected)
                    for channel, expected in zip(ambient["rho_td3"], trace)
                ),
                max(
                    _coefficient_residual(channel.rho_first, expected)
                    for channel, expected in zip(ambient["rho_td3"], J1)
                ),
            )
        else:
            reference = _reference_x64_td3()
            endpoint_c2_residual = max(
                endpoint_c2_residual,
                max(
                    _coefficient_residual(channel.value, expected)
                    for channel, expected in zip(ambient["rho_td3"], reference)
                ),
                max(
                    _coefficient_residual(channel.rho_first, 0.0)
                    for channel in ambient["rho_td3"]
                ),
                max(
                    _coefficient_residual(channel.rho_second, 0.0)
                    for channel in ambient["rho_td3"]
                ),
            )

    decoder_rejections = []
    decoder_rejection_cases = (
        lambda: decode_common_first_boundary_td3(free1[:-1], tangent1, 1, 1, (0.0,) * 4),
        lambda: decode_common_first_boundary_td3(free1, tangent1[:-1], 1, 1, (0.0,) * 4),
        lambda: decode_common_first_boundary_td3(free1, tangent1, 1, 1, (0.0,) * 3),
        lambda: decode_common_first_boundary_td3(
            free1, tangent1, 1, 1, (float("nan"), 0.0, 0.0, 0.0)
        ),
        lambda: decode_full_t4_collar_point(free1, tangent1, 1, 1, (0.0,) * 4, -0.01, "plus"),
        lambda: decode_full_t4_collar_point(free1, tangent1, 1, 1, (0.0,) * 4, 1.01, "plus"),
        lambda: decode_full_t4_collar_point(free1, tangent1, 1, 1, (0.0,) * 4, True, "plus"),
        lambda: decode_full_t4_collar_point(free1, tangent1, 1, 1, (0.0,) * 4, 0.5, "unknown"),
        lambda: full_t4_decoder_contract(True, 1),
        lambda: full_t4_decoder_contract(1, True),
    )
    for case in decoder_rejection_cases:
        try:
            case()
        except TaylorDual3InputError:
            decoder_rejections.append(True)
        else:
            decoder_rejections.append(False)

    passed = bool(
        all(pinned_contracts.values())
        and pointwise_oracle["pass"]
        and sentinel_offsets
        and abs(axis_activity["N9_x2"]) > 0.05
        and abs(axis_activity["N11_x3"]) > 0.05
        and cancellation <= 2.0e-10
        and projected_q_cancellation == 0.0
        and projected_q_numeric_residual <= 5.0e-13
        and r_spatial_activity > 1.0e-5
        and r_noncommuting_activity > 1.0e-6
        and missing_frame_mutant_failure > 1.0e-5
        and flipped_frame_mutant_failure > 1.0e-5
        and pullback_residual <= 5.0e-12
        and side_sign_mutant_failure > 1.0e-3
        and contaminated_vee_rejected
        and B_one_hot_residual <= 5.0e-13
        and endpoints_finite
        and endpoint_c2_residual <= 5.0e-12
        and all(decoder_rejections)
        and all(
            shapes == {
                "ambient_X64": 64,
                "pulled_X64": 64,
                "pulled_reference_metric15": 15,
                "pulled_X79": 79,
            }
            for shapes in endpoint_shapes.values()
        )
    )
    return {
        "pinned_c2_contract_matches": pinned_contracts,
        "pointwise_oracle_sampled": pointwise_oracle,
        "offset_sentinel_pass": sentinel_offsets,
        "full_t4_axis_activity": axis_activity,
        "common_frame_cancellation_two_jet_max_abs_coefficient_residual": cancellation,
        "lateral_trace_q_cancellation_structural_residual": projected_q_cancellation,
        "lateral_trace_q_cancellation_numeric_oracle_residual": projected_q_numeric_residual,
        "q_zero_r_E0_spatial_activity": r_spatial_activity,
        "q_zero_r_E0_noncommuting_cross_activity": r_noncommuting_activity,
        "missing_R_transpose_dR_mutant_max_abs_failure": missing_frame_mutant_failure,
        "flipped_R_transpose_dR_mutant_max_abs_failure": flipped_frame_mutant_failure,
        "pullback_two_jet_vs_pinned_v5_6_7_max_abs_residual": pullback_residual,
        "side_radial_sign_mutant_max_abs_failure": side_sign_mutant_failure,
        "symmetric_contamination_before_vee_rejected": contaminated_vee_rejected,
        "B_pullback_radial_and_tangential_one_hot_max_abs_residual": B_one_hot_residual,
        "endpoint_channel_shapes": endpoint_shapes,
        "endpoint_jets_finite": endpoints_finite,
        "endpoint_C2_max_abs_coefficient_residual": endpoint_c2_residual,
        "decoder_fail_closed_rejection_results": decoder_rejections,
        "pass": passed,
    }


def build_report() -> dict[str, Any]:
    upstream = _load_pinned_upstream()
    algebra = _check_mixed_algebra()
    validation = _check_fail_closed_inputs()
    analytic = _check_analytic_identities()
    rotation = _check_so3()
    decoder = _check_decoder()
    decision = {
        "taylor_dual3_independent_eta_spatial_degree_three_algebra_pass": bool(
            algebra["pass"] and validation["pass"]
        ),
        "taylor_dual3_analytic_identities_sampled_within_tolerance_pass": bool(analytic["pass"]),
        "so3_entire_z_origin_regular_orthogonality_and_eta_jvp_sampled_pass": bool(rotation["pass"]),
        "full_t4_decoder_implemented_and_sampled_against_pinned_oracles_pass": bool(
            decoder["pass"]
        ),
        "local_bulk_density_implemented_pass": False,
        "local_ghy_density_implemented_pass": False,
        "local_interface_density_implemented_pass": False,
        "local_density_values_and_jvps_pass": False,
        "integrated_action_pass": False,
        "quadrature_pass": False,
        "margins_certified_pass": False,
        "uniform_N_to_infinity_bridge_pass": False,
        "uniform_N_to_infinity_numerical_certificate_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
    }
    return {
        "schema": SCHEMA,
        "source_pins": {
            "full_t4_exact_primitives_v5_6_7_sha256": UPSTREAM_SHA256,
            "full_t4_exact_primitives_v5_6_7_schema": upstream.SCHEMA,
            "pointwise_decoder_v5_6_4_2_sha256": POINTWISE_ORACLE_SHA256,
            "pointwise_decoder_v5_6_4_2_schema": POINTWISE_ORACLE_SCHEMA,
        },
        "algebra": algebra,
        "fail_closed_inputs": validation,
        "analytic_identities": analytic,
        "so3": rotation,
        "decoder": decoder,
        "decision": decision,
        "scope": (
            "M3 decoder milestone: sparse float64 Taylor algebra in four spatial variables through degree three "
            "with an independent nilpotent eta axis, plus SO(3) Rodrigues entire-z series on guarded inputs: "
            "|body(q)| <= pi-1 and non-body coefficient l1 <= 8. Analytic identities, orthogonality and eta-JVP "
            "consistency are sampled float64 "
            "checks, not symbolic proofs or rounding enclosures. The common-first decoder returns value, "
            "eta-JVP and complete 5D two-jets for C2 ambient X64, pulled X64, reference 15 and X79; its generic "
            "N,K implementation is sampled against byte-pinned decoder oracles only at N=1,2,3 and by x2/x3 "
            "probes at N=9,11. The eta oracle uses finite differences only inside the sampled self-check, never "
            "inside the decoder pipeline. No local density, local density JVP, "
            "integrated action, quadrature, margin certificate, uniform bridge, C1/N1 or B4/B5 claim. No receipt "
            "or artifact is written by design."
        ),
    }


def main() -> None:
    report = build_report()
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
