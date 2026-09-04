#!/usr/bin/env python3
"""TaylorDual3 and regular SO(3) primitives for Route C v5.6.7.1.

This is the first, deliberately small, M3 delivery after the full-T^4 M1+M2
primitives in v5.6.7.  It implements only a scalar truncated Taylor algebra
and an SO(3) exponential over that algebra.  Despite ``dual_local_action`` in
the reserved filename, this delivery does NOT implement a decoder, a local
density, a local density JVP, an integrated action, or quadrature.

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
and sampled SO(3) regularity/orthogonality/JVP consistency.  Decoder, density,
action, quadrature, margins, bridge, C1/N1, and B4/B5 keys remain FALSE.
"""

from __future__ import annotations

import hashlib
import importlib.util
from itertools import product
import json
import math
from numbers import Real
import operator
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
SCHEMA = "holo.one-omega-topological-so3-route-c-full-t4-dual-local-action-v5-6-7-1.v1"

UPSTREAM_PATH = HERE / "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
UPSTREAM_SHA256 = "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25"
UPSTREAM_SCHEMA = "holo.one-omega-topological-so3-route-c-full-t4-exact-primitives-v5-6-7.v1"

N_SPATIAL = 4
MAX_SPATIAL_DEGREE = 3
ZERO_ALPHA = (0, 0, 0, 0)
SO3_SERIES_BODY_NORM_LIMIT = math.pi - 1.0
SO3_SERIES_BODY_Z_LIMIT = SO3_SERIES_BODY_NORM_LIMIT**2
SO3_SERIES_NONBODY_L1_LIMIT = 8.0
SAMPLED_TOLERANCE = 8.0e-12

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


def _coefficient_residual(value: TaylorDual3, expected: TaylorDual3 | Real) -> float:
    right = TaylorDual3._require(expected)
    keys = set(value._coefficients) | set(right._coefficients)
    return max((abs(value._coefficients.get(key, 0.0) - right._coefficients.get(key, 0.0)) for key in keys), default=0.0)


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


def build_report() -> dict[str, Any]:
    upstream = _load_pinned_upstream()
    algebra = _check_mixed_algebra()
    validation = _check_fail_closed_inputs()
    analytic = _check_analytic_identities()
    rotation = _check_so3()
    decision = {
        "taylor_dual3_independent_eta_spatial_degree_three_algebra_pass": bool(
            algebra["pass"] and validation["pass"]
        ),
        "taylor_dual3_analytic_identities_sampled_within_tolerance_pass": bool(analytic["pass"]),
        "so3_entire_z_origin_regular_orthogonality_and_eta_jvp_sampled_pass": bool(rotation["pass"]),
        "full_t4_decoder_implemented_pass": False,
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
        },
        "algebra": algebra,
        "fail_closed_inputs": validation,
        "analytic_identities": analytic,
        "so3": rotation,
        "decision": decision,
        "scope": (
            "M3 first minimum only: sparse float64 Taylor algebra in four spatial variables through degree three "
            "with an independent nilpotent eta axis, plus SO(3) Rodrigues entire-z series on guarded inputs: "
            "|body(q)| <= pi-1 and non-body coefficient l1 <= 8. Analytic identities, orthogonality and eta-JVP "
            "consistency are sampled float64 "
            "checks, not symbolic proofs or rounding enclosures. No decoder, local density, local density JVP, "
            "integrated action, quadrature, margin certificate, uniform bridge, C1/N1 or B4/B5 claim. No receipt "
            "or artifact is written by design."
        ),
    }


def main() -> None:
    report = build_report()
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
