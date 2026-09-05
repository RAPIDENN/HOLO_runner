#!/usr/bin/env python3
"""TaylorDual3 and regular SO(3) primitives for Route C v5.6.7.1.

This is the incremental M3 delivery after the full-T^4 M1+M2 primitives in
v5.6.7.  It implements a scalar truncated Taylor algebra, an SO(3) exponential
over that algebra, the common-first C2 decoder at one full-T4 collar point, and
twenty separate local density values with exact eta-direction JVPs.  The
decoder returns ambient X64, pulled X64, pulled reference metric 15 and their
ordered X79 concatenation, each with primal and eta value/5D two-jet.  The
density API keeps its twelve bulk, two GHY and six shared-interface outputs on
their distinct domains; it deliberately does not form a pointwise S_total and
does not implement integration or quadrature.

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
sampled SO(3) regularity/orthogonality/JVP consistency, the decoder sampled
against byte-pinned finite-N oracles, and the three local-density domains
sampled at N=1,2,3 against byte-pinned Torch Route A+C2 values and
``torch.func.jvp``.  Integrated action, quadrature, margins, bridge, C1/N1,
and B4/B5 keys remain FALSE.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
from functools import lru_cache
from itertools import permutations, product
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
TORCH_C2_ORACLE_PATH = HERE / "derive_one_omega_topological_so3_torch_c2_multin_v5_6_5_6.py"
TORCH_C2_ORACLE_SHA256 = "2c3fb9adbaad90a77fd5cf1fd7df9bd61c2e4d1e92dbffeff4f3ffaa31ab7f6b"
TORCH_ROUTE_A_WRAPPER_SHA256 = "5c24361ba431888ccaf473ba2ab17aa00354258ba70c31bb81bfb77ebf6d56b6"
TORCH_ROUTE_A_CORE_SHA256 = "dfb1692b3af96c1827ad7fd435b0de7a2af89dd7535a328bc49ba5431d492a7c"
C2_BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
LITERAL_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
ROUTE_C_ORACLE_PATH = HERE / (
    "derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3.py"
)
ROUTE_C_ORACLE_SHA256 = "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"
ROUTE_C_ORACLE_SCHEMA = (
    "holo.one-omega-topological-so3-multin-independent-euler-green-route-c-v5-6-6-3.v1"
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
BULK_SECTORS = ("EH", "Omega_kinetic", "Omega_potential", "P_kinetic", "full_V4", "BF")
INTERFACE_SECTORS = ("wall", "K_foliation", "R", "R_squared", "a_squared", "Robin")
LOCAL_DENSITY_COMPONENTS = tuple(
    name
    for side in SIDES
    for name in tuple(f"{sector}_bulk_{side}" for sector in BULK_SECTORS)
    + (f"GHY_{side}",)
) + INTERFACE_SECTORS
ACTION_COEFFICIENTS = {
    "B4_bar": 0.8,
    "M5_cubed": 1.0,
    "Robin_kappa_hat": 1.0,
    "Robin_y": math.sqrt(3.0),
    "brane_Mb_squared": 2.0,
    "brane_beta": 2.0,
    "compensator_metric_G": 1.2,
    "eta": 3.107013790800849,
    "k_infinity": 1.0,
    "lambda_K": -0.5535068954004245,
    "material_Z5_per_side": 1.0,
    "material_mass_M": 1.0,
    "xi": 1.0,
}

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
def _load_pinned_torch_c2_oracle() -> tuple[Any, Any, Mapping[str, Any]]:
    """Load the C2 profile wrapper and its pinned literal Torch Route A."""

    observed = _sha256(TORCH_C2_ORACLE_PATH)
    if observed != TORCH_C2_ORACLE_SHA256:
        raise DualLocalActionError(f"Torch C2 oracle pin drift: {observed}")
    spec = importlib.util.spec_from_file_location(
        "pinned_torch_c2_multin_v5_6_5_6", TORCH_C2_ORACLE_PATH
    )
    if spec is None or spec.loader is None:
        raise DualLocalActionError("cannot load pinned Torch C2 oracle")
    c2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c2)
    if getattr(c2, "SCHEMA", None) != "holo.one-omega-topological-so3-torch-c2-multin-v5-6-5-6.v1":
        raise DualLocalActionError("Torch C2 oracle schema drift")
    if c2.BASE_ROUTE_WRAPPER_SHA256 != TORCH_ROUTE_A_WRAPPER_SHA256:
        raise DualLocalActionError("Torch Route A wrapper pin drift inside C2 oracle")
    if c2.BUNDLE_SHA256 != C2_BUNDLE_SHA256:
        raise DualLocalActionError("C2 primitive bundle pin drift inside Torch oracle")
    base = c2.load_base_wrapper()
    if base.ROUTE_A_SOURCE_SHA256 != TORCH_ROUTE_A_CORE_SHA256:
        raise DualLocalActionError("Torch Route A core pin drift inside wrapper")
    route_a = base.load_route_a()
    if route_a.V5_2_EXACT_ACTION_SHA256 != LITERAL_ACTION_SHA256:
        raise DualLocalActionError("literal action contract pin drift inside Torch oracle")
    bundle = c2.load_bundle(route_a)
    if tuple(route_a.BULK_ATOMS) != BULK_SECTORS or tuple(route_a.BRANE_ATOMS) != INTERFACE_SECTORS:
        raise DualLocalActionError("literal Torch local-density names drift")
    if tuple(route_a.COMPONENT_NAMES) != LOCAL_DENSITY_COMPONENTS:
        raise DualLocalActionError("literal Torch twenty-component order drift")
    for name, expected in ACTION_COEFFICIENTS.items():
        if float(route_a.COEFFICIENTS[name]) != expected:
            raise DualLocalActionError(f"literal action coefficient drift: {name}")
    return c2, route_a, bundle


@lru_cache(maxsize=1)
def _load_pinned_route_c_oracle() -> Any:
    observed = _sha256(ROUTE_C_ORACLE_PATH)
    if observed != ROUTE_C_ORACLE_SHA256:
        raise DualLocalActionError(f"Route C local-value oracle pin drift: {observed}")
    spec = importlib.util.spec_from_file_location(
        "pinned_route_c_local_values_v5_6_6_3", ROUTE_C_ORACLE_PATH
    )
    if spec is None or spec.loader is None:
        raise DualLocalActionError("cannot load pinned Route C local-value oracle")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if getattr(module, "SCHEMA", None) != ROUTE_C_ORACLE_SCHEMA:
        raise DualLocalActionError("Route C local-value oracle schema drift")
    return module


@lru_cache(maxsize=1)
def _load_c2_bundle() -> Mapping[str, Any]:
    upstream = _load_pinned_upstream()
    if upstream.BUNDLE_SHA256 != C2_BUNDLE_SHA256:
        raise DualLocalActionError("v5.6.7 embedded C2 bundle pin drift")
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


def _permutation_sign(indices: Sequence[int]) -> int:
    if sorted(indices) != list(range(len(indices))):
        raise TaylorDual3InputError("permutation must contain each index exactly once")
    inversions = sum(
        int(indices[left] > indices[right])
        for left in range(len(indices))
        for right in range(left + 1, len(indices))
    )
    return -1 if inversions % 2 else 1


def td3_determinant(matrix: Sequence[Sequence[TaylorDual3 | Real]]) -> TaylorDual3:
    """Exact Leibniz determinant over the TaylorDual3 coefficient algebra."""

    dimension = len(matrix)
    if dimension == 0 or dimension > 5 or any(len(row) != dimension for row in matrix):
        raise TaylorDual3InputError("TD3 determinant expects a square matrix of dimension one through five")
    typed = tuple(tuple(TaylorDual3._require(entry) for entry in row) for row in matrix)
    zero = TaylorDual3.constant(0.0)
    return sum(
        (
            _permutation_sign(permutation)
            * math.prod((typed[row][permutation[row]] for row in range(dimension)), start=TaylorDual3.constant(1.0))
            for permutation in permutations(range(dimension))
        ),
        zero,
    )


def td3_cross(
    left: Sequence[TaylorDual3 | Real],
    right: Sequence[TaylorDual3 | Real],
) -> tuple[TaylorDual3, TaylorDual3, TaylorDual3]:
    """Three-dimensional cross product over TaylorDual3."""

    if len(left) != 3 or len(right) != 3:
        raise TaylorDual3InputError("TD3 cross product expects two three-vectors")
    a = tuple(TaylorDual3._require(entry) for entry in left)
    b = tuple(TaylorDual3._require(entry) for entry in right)
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def td3_metric_geometry(
    metric: Sequence[Sequence[TaylorDual3 | Real]],
    first: Sequence[Sequence[Sequence[TaylorDual3 | Real]]],
    second: Sequence[Sequence[Sequence[Sequence[TaylorDual3 | Real]]]] | None = None,
    *,
    include_riemann: bool = False,
    context: str = "metric",
) -> dict[str, Any]:
    """Levi-Civita geometry over TD3 with strict Lorentzian body guards.

    Index order matches the pinned literal Torch route: ``first[p][m][n]``
    and ``second[p][q][m][n]``.  This helper is used only after projecting a
    decoded jet to its value/eta layer, so it claims a pointwise JVP rather
    than a uniform interval enclosure.
    """

    dimension = len(metric)
    if dimension not in (4, 5) or any(len(row) != dimension for row in metric):
        raise TaylorDual3InputError(f"{context} must be a 4x4 or 5x5 matrix")
    if len(first) != dimension or any(
        len(layer) != dimension or any(len(row) != dimension for row in layer)
        for layer in first
    ):
        raise TaylorDual3InputError(f"{context} first derivative shape drift")
    if include_riemann and second is None:
        raise TaylorDual3InputError("Riemann curvature requires metric second derivatives")
    if second is not None and (
        len(second) != dimension
        or any(
            len(layer) != dimension
            or any(
                len(matrix_layer) != dimension
                or any(len(row) != dimension for row in matrix_layer)
                for matrix_layer in layer
            )
            for layer in second
        )
    ):
        raise TaylorDual3InputError(f"{context} second derivative shape drift")

    g = tuple(tuple(TaylorDual3._require(entry) for entry in row) for row in metric)
    dg = tuple(
        tuple(tuple(TaylorDual3._require(entry) for entry in row) for row in layer)
        for layer in first
    )
    ddg = None
    if second is not None:
        ddg = tuple(
            tuple(
                tuple(tuple(TaylorDual3._require(entry) for entry in row) for row in matrix_layer)
                for matrix_layer in layer
            )
            for layer in second
        )

    body = np.asarray([[entry.body for entry in row] for row in g], dtype=float)
    if not np.allclose(body, body.T, atol=2.0e-12, rtol=0.0):
        raise TaylorDual3InputError(f"{context} body must be symmetric")
    eigenvalues = np.linalg.eigvalsh(body)
    scale = max(1.0, float(np.max(np.abs(eigenvalues))))
    if int(np.count_nonzero(eigenvalues < 0.0)) != 1 or float(np.min(np.abs(eigenvalues))) <= 1.0e-10 * scale:
        raise TaylorDual3InputError(f"{context} body must be nondegenerate Lorentzian")
    if float(np.linalg.cond(body)) > 1.0e10:
        raise TaylorDual3InputError(f"{context} body condition number exceeds guarded domain")

    zero = TaylorDual3.constant(0.0)
    inverse = _inverse_td3(g)
    determinant = td3_determinant(g)
    if determinant.body >= 0.0:
        raise TaylorDual3InputError(f"{context} Lorentzian determinant must be negative")
    measure = (-determinant).sqrt()
    derivative_inverse = tuple(
        tuple(
            tuple(
                -sum(
                    (
                        inverse[k][a] * dg[p][a][b] * inverse[b][l]
                        for a in range(dimension)
                        for b in range(dimension)
                    ),
                    zero,
                )
                for l in range(dimension)
            )
            for k in range(dimension)
        )
        for p in range(dimension)
    )
    christoffel = tuple(
        tuple(
            tuple(
                0.5
                * sum(
                    (
                        inverse[k][l]
                        * (dg[m][l][n] + dg[n][l][m] - dg[l][m][n])
                        for l in range(dimension)
                    ),
                    zero,
                )
                for n in range(dimension)
            )
            for m in range(dimension)
        )
        for k in range(dimension)
    )
    result: dict[str, Any] = {
        "inverse": inverse,
        "determinant": determinant,
        "sqrt_abs_determinant": measure,
        "derivative_inverse": derivative_inverse,
        "christoffel": christoffel,
        "body_eigenvalues": tuple(float(value) for value in eigenvalues),
        "body_condition_number": float(np.linalg.cond(body)),
    }
    if ddg is None:
        return result

    derivative_christoffel = tuple(
        tuple(
            tuple(
                tuple(
                    0.5
                    * (
                        sum(
                            (
                                derivative_inverse[p][k][l]
                                * (dg[m][l][n] + dg[n][l][m] - dg[l][m][n])
                                for l in range(dimension)
                            ),
                            zero,
                        )
                        + sum(
                            (
                                inverse[k][l]
                                * (ddg[p][m][l][n] + ddg[p][n][l][m] - ddg[p][l][m][n])
                                for l in range(dimension)
                            ),
                            zero,
                        )
                    )
                    for n in range(dimension)
                )
                for m in range(dimension)
            )
            for k in range(dimension)
        )
        for p in range(dimension)
    )
    ricci = tuple(
        tuple(
            sum((derivative_christoffel[k][k][m][n] for k in range(dimension)), zero)
            - sum((derivative_christoffel[n][k][m][k] for k in range(dimension)), zero)
            + sum(
                (
                    christoffel[k][k][l] * christoffel[l][m][n]
                    for k in range(dimension)
                    for l in range(dimension)
                ),
                zero,
            )
            - sum(
                (
                    christoffel[k][n][l] * christoffel[l][m][k]
                    for k in range(dimension)
                    for l in range(dimension)
                ),
                zero,
            )
            for n in range(dimension)
        )
        for m in range(dimension)
    )
    scalar_curvature = sum(
        (inverse[m][n] * ricci[m][n] for m in range(dimension) for n in range(dimension)),
        zero,
    )
    result.update(
        {
            "derivative_christoffel": derivative_christoffel,
            "ricci": ricci,
            "scalar_curvature": scalar_curvature,
        }
    )
    if include_riemann:
        riemann_upper = tuple(
            tuple(
                tuple(
                    tuple(
                        derivative_christoffel[m][r][n][s]
                        - derivative_christoffel[n][r][m][s]
                        + sum(
                            (
                                christoffel[r][m][l] * christoffel[l][n][s]
                                - christoffel[r][n][l] * christoffel[l][m][s]
                                for l in range(dimension)
                            ),
                            zero,
                        )
                        for n in range(dimension)
                    )
                    for m in range(dimension)
                )
                for s in range(dimension)
            )
            for r in range(dimension)
        )
        riemann_lower = tuple(
            tuple(
                tuple(
                    tuple(
                        sum((g[a][r] * riemann_upper[r][s][m][n] for r in range(dimension)), zero)
                        for n in range(dimension)
                    )
                    for m in range(dimension)
                )
                for s in range(dimension)
            )
            for a in range(dimension)
        )
        result["riemann_upper"] = riemann_upper
        result["riemann_lower"] = riemann_lower
    return result


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


def _dual_value(value: TaylorDual3 | Real) -> TaylorDual3:
    """Project one TD3 value to its body plus independent eta coefficient."""

    typed = TaylorDual3._require(value)
    return TaylorDual3.constant(typed.body) + TaylorDual3.eta(
        typed.derivative(ZERO_ALPHA, 1)
    )


def rhojet2_local_two_jet(channels: Sequence[RhoJet2]) -> dict[str, Any]:
    """Extract a pointwise five-dimensional two-jet retaining value and eta.

    Spatial differentiation is taken in TD3 before projecting to the
    ``1+eta`` layer.  Radial derivatives come from RhoJet2.  Thus every entry
    remains a TaylorDual3, but carries only the primal value and its exact
    directional eta coefficient needed by the local-density API.
    """

    if not channels or any(not isinstance(channel, RhoJet2) for channel in channels):
        raise TaylorDual3InputError("RhoJet2 extraction requires a non-empty channel sequence")
    value = tuple(_dual_value(channel.value) for channel in channels)
    first = tuple(
        tuple(
            _dual_value(channel.value.partial(axis))
            if axis < N_SPATIAL
            else _dual_value(channel.rho_first)
            for channel in channels
        )
        for axis in range(5)
    )
    second = tuple(
        tuple(
            tuple(
                _dual_value(channel.value.partial(left).partial(right))
                if left < N_SPATIAL and right < N_SPATIAL
                else _dual_value(
                    channel.rho_first.partial(left if left < N_SPATIAL else right)
                )
                if (left < N_SPATIAL) != (right < N_SPATIAL)
                else _dual_value(channel.rho_second)
                for channel in channels
            )
            for right in range(5)
        )
        for left in range(5)
    )
    return {"channel_count": len(channels), "value": value, "first": first, "second": second}


def _x64_local_primitives(jet: Mapping[str, Any]) -> dict[str, Any]:
    if int(jet.get("channel_count", -1)) != 64:
        raise TaylorDual3InputError("local bulk primitives require exactly 64 pulled channels")
    value = jet["value"]
    first = jet["first"]
    second = jet["second"]
    if (
        len(value) != 64
        or len(first) != 5
        or any(len(layer) != 64 for layer in first)
        or len(second) != 5
        or any(len(layer) != 5 or any(len(row) != 64 for row in layer) for layer in second)
    ):
        raise TaylorDual3InputError("local X64 two-jet shape drift")
    zero = TaylorDual3.constant(0.0)
    metric = _sym_matrix(value[:15], 5, zero)
    metric_first = tuple(_sym_matrix(first[axis][:15], 5, zero) for axis in range(5))
    metric_second = tuple(
        tuple(_sym_matrix(second[left][right][:15], 5, zero) for right in range(5))
        for left in range(5)
    )
    return {
        "g": metric,
        "d_g": metric_first,
        "dd_g": metric_second,
        "log_Omega": value[15],
        "d_log_Omega": tuple(first[axis][15] for axis in range(5)),
        "phi": tuple(value[16 + a] for a in range(3)),
        "d_phi": tuple(tuple(first[axis][16 + a] for a in range(3)) for axis in range(5)),
        "A": tuple(tuple(value[19 + 3 * axis + a] for a in range(3)) for axis in range(5)),
        "d_A": tuple(
            tuple(
                tuple(first[derivative][19 + 3 * axis + a] for a in range(3))
                for axis in range(5)
            )
            for derivative in range(5)
        ),
        "B": tuple(
            tuple(value[34 + 3 * triple + a] for a in range(3))
            for triple in range(10)
        ),
    }


def _regular_v4_td3(Omega: TaylorDual3, phi: Sequence[TaylorDual3]) -> TaylorDual3:
    """Analytic V4 form regular at phi=0; no vector norm or division by |phi|."""

    zero = TaylorDual3.constant(0.0)
    phi_squared = sum((component * component for component in phi), zero)
    radial_fourth = Omega**6 * phi_squared**2
    return radial_fourth / (2.0 * (1.0 + radial_fourth).sqrt())


def _bulk_component_densities_td3(
    primitives: Mapping[str, Any],
    *,
    context: str,
    phi_cross_sign: float = 1.0,
    curvature_cross_sign: float = 1.0,
    bf_pullback_multiplier: float = 1.0,
) -> dict[str, TaylorDual3]:
    """Six literal Route-A bulk atoms in the pulled positive collar chart."""

    for name, sign in (
        ("phi_cross_sign", phi_cross_sign),
        ("curvature_cross_sign", curvature_cross_sign),
        ("bf_pullback_multiplier", bf_pullback_multiplier),
    ):
        numeric = _finite_real(name, sign)
        if numeric not in (-1.0, 1.0):
            raise TaylorDual3InputError(f"{name} must be +/-1")
    geometry = td3_metric_geometry(
        primitives["g"],
        primitives["d_g"],
        primitives["dd_g"],
        context=context,
    )
    inverse = geometry["inverse"]
    volume = geometry["sqrt_abs_determinant"]
    scalar_curvature = geometry["scalar_curvature"]
    zero = TaylorDual3.constant(0.0)
    log_omega = primitives["log_Omega"]
    Omega = log_omega.exp()
    dlog = primitives["d_log_Omega"]
    dOmega = tuple(Omega * entry for entry in dlog)
    phi = primitives["phi"]
    dphi = primitives["d_phi"]
    connection = primitives["A"]
    dconnection = primitives["d_A"]

    Omega_squared_gradient = sum(
        (
            inverse[m][n] * dOmega[m] * dOmega[n]
            for m in range(5)
            for n in range(5)
        ),
        zero,
    )
    covariant_phi = tuple(
        tuple(
            dphi[m][a]
            + phi_cross_sign * td3_cross(connection[m], phi)[a]
            + 1.5 * phi[a] * dlog[m]
            for a in range(3)
        )
        for m in range(5)
    )
    P_squared = sum(
        (
            inverse[m][n] * covariant_phi[m][a] * covariant_phi[n][a]
            for m in range(5)
            for n in range(5)
            for a in range(3)
        ),
        zero,
    )

    M5_cubed = ACTION_COEFFICIENTS["M5_cubed"]
    G = ACTION_COEFFICIENTS["compensator_metric_G"]
    k_infinity = ACTION_COEFFICIENTS["k_infinity"]
    Z5 = ACTION_COEFFICIENTS["material_Z5_per_side"]
    material_mass = ACTION_COEFFICIENTS["material_mass_M"]
    W = 3.0 * M5_cubed * k_infinity * (-G * Omega * Omega / (6.0 * M5_cubed)).exp()
    W_Omega = -G * Omega * W / (3.0 * M5_cubed)
    U = W_Omega * W_Omega / (2.0 * G) - 2.0 * W * W / (3.0 * M5_cubed)
    V4 = _regular_v4_td3(Omega, phi)

    curvature = tuple(
        tuple(
            tuple(
                dconnection[m][n][a]
                - dconnection[n][m][a]
                + curvature_cross_sign * td3_cross(connection[m], connection[n])[a]
                for a in range(3)
            )
            for n in range(5)
        )
        for m in range(5)
    )
    all_indices = set(range(5))
    BF_density = zero
    for triple_index, triple in enumerate(B_TRIPLES):
        complement = tuple(sorted(all_indices - set(triple)))
        orientation = _permutation_sign(triple + complement)
        BF_density = BF_density + orientation * sum(
            (
                primitives["B"][triple_index][a]
                * curvature[complement[0]][complement[1]][a]
                for a in range(3)
            ),
            zero,
        )

    return {
        "EH": volume * M5_cubed * scalar_curvature / 2.0,
        "Omega_kinetic": -volume * G * Omega_squared_gradient / 2.0,
        "Omega_potential": -volume * U,
        "P_kinetic": -volume * Z5 * P_squared / 2.0,
        "full_V4": -volume * Z5 * material_mass**2 * Omega**-5 * V4,
        # B already carries the lateral det(J) sign through the X64 pullback.
        "BF": bf_pullback_multiplier * BF_density,
    }


def _relative_bulk_densities_td3(
    pulled: Sequence[RhoJet2],
    pulled_reference15: Sequence[RhoJet2],
    *,
    side: str,
    phi_cross_sign: float = 1.0,
    curvature_cross_sign: float = 1.0,
    bf_pullback_multiplier: float = 1.0,
) -> dict[str, TaylorDual3]:
    if side not in SIDES:
        raise TaylorDual3InputError(f"side must be one of {SIDES}")
    if len(pulled) != 64 or len(pulled_reference15) != 15:
        raise TaylorDual3InputError("relative bulk density requires pulled X64 plus reference metric 15")
    actual = _bulk_component_densities_td3(
        _x64_local_primitives(rhojet2_local_two_jet(pulled)),
        context=f"{side} pulled bulk metric",
        phi_cross_sign=phi_cross_sign,
        curvature_cross_sign=curvature_cross_sign,
        bf_pullback_multiplier=bf_pullback_multiplier,
    )
    reference_channels = tuple(pulled_reference15) + tuple(RhoJet2(0.0) for _ in range(49))
    reference = _bulk_component_densities_td3(
        _x64_local_primitives(rhojet2_local_two_jet(reference_channels)),
        context=f"{side} pulled reference metric",
    )
    return {sector: actual[sector] - reference[sector] for sector in BULK_SECTORS}


def _ghy_density_td3(
    pulled_boundary: Sequence[RhoJet2],
    *,
    side: str,
    normal_sign: float = -1.0,
) -> TaylorDual3:
    """GHY density on rho=0 in the pulled positive collar chart.

    Both side collars use the same outward covector ``-d rho/sqrt(g^rho rho)``.
    The side-dependent ambient orientation has already been absorbed by the
    pullback, exactly as for the bulk top form.
    """

    if side not in SIDES:
        raise TaylorDual3InputError(f"side must be one of {SIDES}")
    normal_sign = _finite_real("normal_sign", normal_sign)
    if normal_sign not in (-1.0, 1.0):
        raise TaylorDual3InputError("normal_sign must be +/-1")
    primitives = _x64_local_primitives(rhojet2_local_two_jet(pulled_boundary))
    geometry = td3_metric_geometry(
        primitives["g"],
        primitives["d_g"],
        context=f"{side} pulled GHY metric",
    )
    inverse = geometry["inverse"]
    if inverse[4][4].body <= 1.0e-10:
        raise TaylorDual3InputError("GHY rho-normal must be spacelike and nondegenerate")
    normal_covector_rho = normal_sign / inverse[4][4].sqrt()
    induced = tuple(tuple(primitives["g"][mu][nu] for nu in range(4)) for mu in range(4))
    induced_first = tuple(
        tuple(
            tuple(primitives["d_g"][axis][mu][nu] for nu in range(4))
            for mu in range(4)
        )
        for axis in range(4)
    )
    induced_geometry = td3_metric_geometry(
        induced,
        induced_first,
        context=f"{side} induced GHY metric",
    )
    induced_inverse = induced_geometry["inverse"]
    extrinsic = tuple(
        tuple(-normal_covector_rho * geometry["christoffel"][4][mu][nu] for nu in range(4))
        for mu in range(4)
    )
    zero = TaylorDual3.constant(0.0)
    theta = sum(
        (induced_inverse[mu][nu] * extrinsic[mu][nu] for mu in range(4) for nu in range(4)),
        zero,
    )
    return (
        ACTION_COEFFICIENTS["M5_cubed"]
        * induced_geometry["sqrt_abs_determinant"]
        * theta
    )


def _foliation_geometry_td3(
    gamma: Sequence[Sequence[TaylorDual3]],
    gamma_first: Sequence[Sequence[Sequence[TaylorDual3]]],
    gamma_second: Sequence[Sequence[Sequence[Sequence[TaylorDual3]]]],
    tau_gradient: Sequence[TaylorDual3],
    tau_hessian: Sequence[Sequence[TaylorDual3]],
    *,
    gauss_extrinsic_sign: float = 1.0,
) -> dict[str, Any]:
    """Literal contracted-Gauss foliation geometry in four dimensions."""

    gauss_extrinsic_sign = _finite_real("gauss_extrinsic_sign", gauss_extrinsic_sign)
    if gauss_extrinsic_sign not in (-1.0, 1.0):
        raise TaylorDual3InputError("gauss_extrinsic_sign must be +/-1")
    if len(tau_gradient) != 4 or len(tau_hessian) != 4 or any(len(row) != 4 for row in tau_hessian):
        raise TaylorDual3InputError("tau gradient/Hessian shape drift")
    geometry = td3_metric_geometry(
        gamma,
        gamma_first,
        gamma_second,
        include_riemann=True,
        context="interface gamma",
    )
    inverse = geometry["inverse"]
    zero = TaylorDual3.constant(0.0)
    one = TaylorDual3.constant(1.0)
    tau_norm_squared = sum(
        (inverse[i][j] * tau_gradient[i] * tau_gradient[j] for i in range(4) for j in range(4)),
        zero,
    )
    if tau_norm_squared.body >= -1.0e-10:
        raise TaylorDual3InputError(
            "interface tau gradient must be timelike and nondegenerate at this sampled body"
        )
    normalization = (-tau_norm_squared).sqrt()
    u_covector = tuple(-tau_gradient[i] / normalization for i in range(4))
    u_vector = _matvec(inverse, u_covector, zero)
    derivative_tau_norm_squared = tuple(
        sum(
            (
                geometry["derivative_inverse"][p][i][j]
                * tau_gradient[i]
                * tau_gradient[j]
                for i in range(4)
                for j in range(4)
            ),
            zero,
        )
        + 2.0
        * sum(
            (
                inverse[i][j] * tau_hessian[p][i] * tau_gradient[j]
                for i in range(4)
                for j in range(4)
            ),
            zero,
        )
        for p in range(4)
    )
    derivative_normalization = tuple(
        -entry / (2.0 * normalization) for entry in derivative_tau_norm_squared
    )
    derivative_u_covector = tuple(
        tuple(
            -tau_hessian[p][n] / normalization
            + tau_gradient[n] * derivative_normalization[p] / normalization**2
            for n in range(4)
        )
        for p in range(4)
    )
    covariant_u = tuple(
        tuple(
            derivative_u_covector[i][j]
            - sum(
                (geometry["christoffel"][k][i][j] * u_covector[k] for k in range(4)),
                zero,
            )
            for j in range(4)
        )
        for i in range(4)
    )
    projector_covariant = tuple(
        tuple(gamma[i][j] + u_covector[i] * u_covector[j] for j in range(4))
        for i in range(4)
    )
    projector_contravariant = tuple(
        tuple(inverse[i][j] + u_vector[i] * u_vector[j] for j in range(4))
        for i in range(4)
    )
    projector_mixed = tuple(
        tuple((one if i == j else zero) + u_covector[i] * u_vector[j] for j in range(4))
        for i in range(4)
    )
    Kcal = tuple(
        tuple(
            sum(
                (
                    projector_mixed[m][a]
                    * projector_mixed[n][b]
                    * covariant_u[a][b]
                    for a in range(4)
                    for b in range(4)
                ),
                zero,
            )
            for n in range(4)
        )
        for m in range(4)
    )
    Ktrace = sum(
        (projector_contravariant[m][n] * Kcal[m][n] for m in range(4) for n in range(4)),
        zero,
    )
    K_squared = sum(
        (
            projector_contravariant[m][r]
            * projector_contravariant[n][s]
            * Kcal[m][n]
            * Kcal[r][s]
            for m in range(4)
            for r in range(4)
            for n in range(4)
            for s in range(4)
        ),
        zero,
    )
    acceleration_covector = tuple(
        sum((u_vector[a] * covariant_u[a][n] for a in range(4)), zero)
        for n in range(4)
    )
    acceleration_squared = sum(
        (
            inverse[m][n] * acceleration_covector[m] * acceleration_covector[n]
            for m in range(4)
            for n in range(4)
        ),
        zero,
    )
    projected_riemann = sum(
        (
            projector_contravariant[a][m]
            * projector_contravariant[s][n]
            * geometry["riemann_lower"][a][s][m][n]
            for a in range(4)
            for s in range(4)
            for m in range(4)
            for n in range(4)
        ),
        zero,
    )
    Rcal = projected_riemann + gauss_extrinsic_sign * (K_squared - Ktrace * Ktrace)
    return {
        **geometry,
        "tau_norm_squared": tau_norm_squared,
        "u_covector": u_covector,
        "u_vector": u_vector,
        "projector_covariant": projector_covariant,
        "projector_contravariant": projector_contravariant,
        "Kcal": Kcal,
        "Ktrace": Ktrace,
        "K_squared": K_squared,
        "acceleration_covector": acceleration_covector,
        "acceleration_squared": acceleration_squared,
        "projected_riemann": projected_riemann,
        "Rcal": Rcal,
    }


def _interface_component_densities_td3(
    boundary: Mapping[str, Any],
    *,
    robin_acceleration_sign: float = -1.0,
    gauss_extrinsic_sign: float = 1.0,
) -> dict[str, TaylorDual3]:
    """Six literal shared-interface atoms from common-first fields."""

    robin_acceleration_sign = _finite_real("robin_acceleration_sign", robin_acceleration_sign)
    if robin_acceleration_sign not in (-1.0, 1.0):
        raise TaylorDual3InputError("robin_acceleration_sign must be +/-1")
    common = boundary["common"]
    gamma_full = common["gamma"]
    gamma = tuple(tuple(_dual_value(gamma_full[i][j]) for j in range(4)) for i in range(4))
    gamma_first = tuple(
        tuple(tuple(_dual_value(gamma_full[i][j].partial(p)) for j in range(4)) for i in range(4))
        for p in range(4)
    )
    gamma_second = tuple(
        tuple(
            tuple(
                tuple(_dual_value(gamma_full[i][j].partial(p).partial(q)) for j in range(4))
                for i in range(4)
            )
            for q in range(4)
        )
        for p in range(4)
    )
    T = common["T"]
    tau_gradient = tuple(
        _dual_value(T.partial(axis) + (1.0 if axis == 0 else 0.0))
        for axis in range(4)
    )
    tau_hessian = tuple(
        tuple(_dual_value(T.partial(left).partial(right)) for right in range(4))
        for left in range(4)
    )
    foliation = _foliation_geometry_td3(
        gamma,
        gamma_first,
        gamma_second,
        tau_gradient,
        tau_hessian,
        gauss_extrinsic_sign=gauss_extrinsic_sign,
    )
    inverse = foliation["inverse"]
    measure = foliation["sqrt_abs_determinant"]
    zero = TaylorDual3.constant(0.0)
    E_Q = common["E_Q"]
    varphi_Q = common["varphi"]
    phi_H = tuple(
        _dual_value(sum((E_Q[mu][a] * varphi_Q[a] for a in range(3)), zero))
        for mu in range(4)
    )
    acceleration_vector = tuple(
        sum((inverse[m][n] * foliation["acceleration_covector"][n] for n in range(4)), zero)
        for m in range(4)
    )
    robin_vector = tuple(
        phi_H[m]
        + robin_acceleration_sign * ACTION_COEFFICIENTS["Robin_y"] * acceleration_vector[m]
        for m in range(4)
    )
    robin_norm = sum(
        (
            foliation["projector_covariant"][m][n]
            * robin_vector[m]
            * robin_vector[n]
            for m in range(4)
            for n in range(4)
        ),
        zero,
    )
    Omega = _dual_value(common["log_Omega"]).exp()
    M5_cubed = ACTION_COEFFICIENTS["M5_cubed"]
    G = ACTION_COEFFICIENTS["compensator_metric_G"]
    k_infinity = ACTION_COEFFICIENTS["k_infinity"]
    W = 3.0 * M5_cubed * k_infinity * (-G * Omega * Omega / (6.0 * M5_cubed)).exp()
    Mb_squared = ACTION_COEFFICIENTS["brane_Mb_squared"]
    Rcal = foliation["Rcal"]
    Ktrace = foliation["Ktrace"]
    K_squared = foliation["K_squared"]
    return {
        "wall": measure
        * (-2.0 * W - ACTION_COEFFICIENTS["brane_beta"] * (Omega - 1.0) ** 2 / 2.0),
        "K_foliation": measure
        * Mb_squared
        * (K_squared - ACTION_COEFFICIENTS["lambda_K"] * Ktrace * Ktrace)
        / 2.0,
        "R": measure * Mb_squared * ACTION_COEFFICIENTS["xi"] * Rcal / 2.0,
        "R_squared": -measure
        * Mb_squared
        * ACTION_COEFFICIENTS["B4_bar"]
        * Rcal
        * Rcal
        / (32.0 * k_infinity**2),
        "a_squared": measure
        * Mb_squared
        * ACTION_COEFFICIENTS["eta"]
        * foliation["acceleration_squared"]
        / 2.0,
        "Robin": -measure * ACTION_COEFFICIENTS["Robin_kappa_hat"] * robin_norm / 2.0,
    }


def _local_density_td3(
    free: Sequence[Real],
    tangent: Sequence[Real],
    N: int,
    K: int,
    x: Sequence[Real],
    rho: Real,
) -> tuple[dict[str, TaylorDual3], dict[str, Any]]:
    rho_value = _finite_real("rho", rho)
    if not 0.0 <= rho_value <= 1.0:
        raise TaylorDual3InputError("rho must lie in [0, 1] for local density decoding")
    boundary = decode_common_first_boundary_td3(free, tangent, N, K, x)
    K_value = int(boundary["contract"]["K"])
    components: dict[str, TaylorDual3] = {}
    for side in SIDES:
        side_boundary = boundary["sides"][side]
        ambient = _collar_ambient_x64(side_boundary, rho_value, K_value)
        pulled, reference15 = _pullback_x64_and_reference15(
            ambient,
            side_boundary["Y_first"],
            side,
        )
        bulk = _relative_bulk_densities_td3(pulled, reference15, side=side)
        for sector in BULK_SECTORS:
            components[f"{sector}_bulk_{side}"] = bulk[sector]

        # GHY is a boundary density: it is always decoded at rho=0, never at
        # the supplied interior bulk node.
        boundary_ambient = _collar_ambient_x64(side_boundary, 0.0, K_value)
        boundary_pulled, _boundary_reference = _pullback_x64_and_reference15(
            boundary_ambient,
            side_boundary["Y_first"],
            side,
        )
        components[f"GHY_{side}"] = _ghy_density_td3(
            boundary_pulled,
            side=side,
        )
    components.update(_interface_component_densities_td3(boundary))
    if tuple(components) != LOCAL_DENSITY_COMPONENTS:
        raise DualLocalActionError("twenty local-density component order drift")
    return components, boundary


def local_density_values_and_eta_jvps(
    free: Sequence[Real],
    tangent: Sequence[Real],
    N: int,
    K: int,
    x: Sequence[Real],
    rho: Real,
) -> dict[str, Any]:
    """Return 20 separate local density values and exact eta-direction JVPs.

    ``rho`` selects the bulk point only.  GHY and shared-interface components
    are boundary densities on their own domains.  The result deliberately has
    no pointwise ``S_total`` because those densities cannot be added before
    applying their distinct bulk/boundary integration measures.
    """

    components_td3, boundary = _local_density_td3(free, tangent, N, K, x, rho)
    records = {
        name: {
            "value": component.body,
            "eta_jvp": component.derivative(ZERO_ALPHA, 1),
        }
        for name, component in components_td3.items()
    }
    flattened = tuple(records[name][field] for name in LOCAL_DENSITY_COMPONENTS for field in ("value", "eta_jvp"))
    if not all(math.isfinite(value) for value in flattened):
        raise TaylorDual3NumericalError("local density value/JVP left the finite float64 domain")
    return {
        "N": int(boundary["contract"]["N"]),
        "K": int(boundary["contract"]["K"]),
        "x": boundary["x"],
        "rho_bulk": _finite_real("rho", rho),
        "component_names": LOCAL_DENSITY_COMPONENTS,
        "components": records,
        "values": tuple(records[name]["value"] for name in LOCAL_DENSITY_COMPONENTS),
        "eta_jvps": tuple(records[name]["eta_jvp"] for name in LOCAL_DENSITY_COMPONENTS),
        "domain_separation": {
            "bulk": "supplied rho_bulk in [0,1]",
            "GHY": "rho=0 boundary on each pulled collar",
            "interface": "shared T4 boundary from common fields",
        },
    }


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


def _pinned_member_vectors(N: int) -> tuple[np.ndarray, np.ndarray]:
    bundle = _load_c2_bundle()
    try:
        member = next(item for item in bundle["primary_members"] if int(item["N"]) == N)
        curve = next(
            item
            for item in member["curves"]
            if item["name"] == "joint_all_primitive_classes_control_candidate"
        )
    except (KeyError, StopIteration) as exc:
        raise DualLocalActionError(f"missing pinned primary member/tangent at N={N}") from exc
    free = _decode_pinned_f64(member["authoritative_free_central_f64le"])
    tangent = _decode_pinned_f64(curve["authoritative_free_tangent_f64le"])
    expected = int(full_t4_decoder_contract(N, N)["free_coordinate_dimension"])
    if free.shape != (expected,) or tangent.shape != free.shape:
        raise DualLocalActionError(f"pinned local-density vector shape drift at N={N}")
    return free, tangent


def _torch_local_density_value_jvp(
    free: np.ndarray,
    tangent: np.ndarray,
    N: int,
    K: int,
    x: Sequence[Real],
    rho: Real,
) -> tuple[np.ndarray, np.ndarray]:
    """Independent literal Torch+C2 oracle, sampled only inside self-checks."""

    c2, route_a, _bundle = _load_pinned_torch_c2_oracle()
    torch = route_a.torch
    free_tensor = torch.tensor(free, dtype=route_a.DTYPE)
    tangent_tensor = torch.tensor(tangent, dtype=route_a.DTYPE)
    point_tensor = torch.tensor([_finite_point(x)], dtype=route_a.DTYPE)
    rho_value = _finite_real("rho", rho)
    if not 0.0 < rho_value < 1.0:
        raise TaylorDual3InputError("Torch C2 bulk oracle requires interior rho in (0,1)")
    rho_tensor = torch.tensor([rho_value], dtype=route_a.DTYPE)
    one = torch.ones(1, dtype=route_a.DTYPE)

    def evaluate(trial: Any) -> Any:
        with c2._profile_patch(route_a):
            components = route_a.relative_action_components_on_nodes(
                trial,
                N,
                K,
                point_tensor,
                one,
                rho_tensor,
                one,
            )
        # Only the twenty named local atoms are selected.  S_total is
        # deliberately excluded because bulk and boundary domains differ.
        return torch.stack(tuple(components[name] for name in route_a.COMPONENT_NAMES))

    value, jvp = torch.func.jvp(evaluate, (free_tensor,), (tangent_tensor,))
    value_array = value.detach().cpu().numpy()
    jvp_array = jvp.detach().cpu().numpy()
    if value_array.shape != (20,) or jvp_array.shape != (20,):
        raise DualLocalActionError("Torch local-density oracle shape drift")
    if not np.all(np.isfinite(value_array)) or not np.all(np.isfinite(jvp_array)):
        raise DualLocalActionError("Torch local-density oracle produced non-finite output")
    return value_array, jvp_array


def _route_c_secondary_local_values(
    free: np.ndarray,
    N: int,
    x: Sequence[Real],
    rho: Real,
) -> np.ndarray:
    """Reduced-theta Route C secondary value/sign oracle; never a JVP oracle."""

    route_c = _load_pinned_route_c_oracle()
    bundle = route_c.load_bundle()
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    parameters = bundle["action_contract"]["coefficient_parameters"]
    point = _finite_point(x)
    theta = point[0] + point[1]
    rho_value = _finite_real("rho", rho)
    records: dict[str, float] = {}
    for side in SIDES:
        bulk = route_c._bulk_density(
            route_c._bulk_jet(free, contract, side, theta, rho_value),
            parameters,
        )
        for sector in BULK_SECTORS:
            records[f"{sector}_bulk_{side}"] = float(bulk[sector])
        boundary_jet = route_c._bulk_jet(free, contract, side, theta, 0.0)
        records[f"GHY_{side}"] = float(route_c._ghy_density(boundary_jet, parameters))
    records.update(
        {
            name: float(value)
            for name, value in route_c._brane_density(
                route_c._common_brane_jet(free, contract, theta),
                parameters,
            ).items()
        }
    )
    if tuple(records) != LOCAL_DENSITY_COMPONENTS:
        raise DualLocalActionError("Route C secondary local-density order drift")
    values = np.asarray([records[name] for name in LOCAL_DENSITY_COMPONENTS], dtype=float)
    if not np.all(np.isfinite(values)):
        raise DualLocalActionError("Route C secondary oracle produced non-finite values")
    return values


def _flrw_gauss_witness() -> dict[str, float | bool]:
    """Flat-spatial FLRW witness for the contracted-Gauss sign."""

    scale_factor = 1.7
    scale_first = 0.23
    scale_second = -0.11
    zero = TaylorDual3.constant(0.0)
    gamma = tuple(
        tuple(
            TaylorDual3.constant(
                -1.0
                if i == j == 0
                else scale_factor**2
                if i == j
                else 0.0
            )
            for j in range(4)
        )
        for i in range(4)
    )
    first = [[ [zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    second = [
        [[[zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
        for _ in range(4)
    ]
    for spatial in range(1, 4):
        first[0][spatial][spatial] = TaylorDual3.constant(
            2.0 * scale_factor * scale_first
        )
        second[0][0][spatial][spatial] = TaylorDual3.constant(
            2.0 * (scale_first**2 + scale_factor * scale_second)
        )
    tau_gradient = tuple(TaylorDual3.constant(1.0 if axis == 0 else 0.0) for axis in range(4))
    tau_hessian = tuple(tuple(zero for _ in range(4)) for _ in range(4))
    nominal = _foliation_geometry_td3(
        gamma,
        tuple(tuple(tuple(row) for row in layer) for layer in first),
        tuple(
            tuple(tuple(tuple(row) for row in matrix_layer) for matrix_layer in layer)
            for layer in second
        ),
        tau_gradient,
        tau_hessian,
    )["Rcal"].body
    opposite = _foliation_geometry_td3(
        gamma,
        tuple(tuple(tuple(row) for row in layer) for layer in first),
        tuple(
            tuple(tuple(tuple(row) for row in matrix_layer) for matrix_layer in layer)
            for layer in second
        ),
        tau_gradient,
        tau_hessian,
        gauss_extrinsic_sign=-1.0,
    )["Rcal"].body
    return {
        "scale_factor": scale_factor,
        "scale_first": scale_first,
        "scale_second": scale_second,
        "nominal_Rcal": nominal,
        "opposite_gauss_sign_Rcal": opposite,
        "pass": bool(abs(nominal) <= 2.0e-13 and abs(opposite) >= 0.2),
    }


@lru_cache(maxsize=1)
def _check_local_densities() -> dict[str, Any]:
    """Sample all 20 local value/JVP atoms and effective sign mutants."""

    points = (
        (0.13, -0.27, 0.21, -0.08),
        (0.41, 0.19, -0.31, 0.07),
    )
    rhos = (0.23, 0.71)
    categories = {
        "bulk": tuple(index for index, name in enumerate(LOCAL_DENSITY_COMPONENTS) if "_bulk_" in name),
        "GHY": tuple(index for index, name in enumerate(LOCAL_DENSITY_COMPONENTS) if name.startswith("GHY_")),
        "interface": tuple(index for index, name in enumerate(LOCAL_DENSITY_COMPONENTS) if name in INTERFACE_SECTORS),
    }
    worst_value = {name: 0.0 for name in categories}
    worst_jvp = {name: 0.0 for name in categories}
    rows: dict[str, Any] = {}
    all_finite = True
    for N in (1, 2, 3):
        free, tangent = _pinned_member_vectors(N)
        row_value = {name: 0.0 for name in categories}
        row_jvp = {name: 0.0 for name in categories}
        for point, rho_value in zip(points, rhos):
            actual = local_density_values_and_eta_jvps(
                free,
                tangent,
                N,
                N,
                point,
                rho_value,
            )
            expected_value, expected_jvp = _torch_local_density_value_jvp(
                free,
                tangent,
                N,
                N,
                point,
                rho_value,
            )
            actual_value = np.asarray(actual["values"], dtype=float)
            actual_jvp = np.asarray(actual["eta_jvps"], dtype=float)
            all_finite = bool(
                all_finite
                and np.all(np.isfinite(actual_value))
                and np.all(np.isfinite(actual_jvp))
            )
            for category, indices in categories.items():
                value_residual = float(np.max(np.abs(actual_value[list(indices)] - expected_value[list(indices)])))
                jvp_residual = float(np.max(np.abs(actual_jvp[list(indices)] - expected_jvp[list(indices)])))
                row_value[category] = max(row_value[category], value_residual)
                row_jvp[category] = max(row_jvp[category], jvp_residual)
                worst_value[category] = max(worst_value[category], value_residual)
                worst_jvp[category] = max(worst_jvp[category], jvp_residual)
        rows[str(N)] = {
            "sample_count": len(points),
            "max_abs_value_residual_by_domain_at_N": row_value,
            "max_abs_eta_jvp_residual_by_domain_at_N": row_jvp,
        }

    free3, tangent3 = _pinned_member_vectors(3)
    mutant_point = points[0]
    mutant_rho = rhos[0]
    boundary = decode_common_first_boundary_td3(free3, tangent3, 3, 3, mutant_point)
    mutant_failures = {
        "reference_bulk_omitted": 0.0,
        "BF_duplicate_side_sign": 0.0,
        "GHY_normal_reversed": 0.0,
        "A_cross_phi_sign": 0.0,
        "A_cross_A_sign": 0.0,
        "Robin_plus_y_a": 0.0,
    }
    for side in SIDES:
        side_boundary = boundary["sides"][side]
        ambient = _collar_ambient_x64(side_boundary, mutant_rho, 3)
        pulled, reference15 = _pullback_x64_and_reference15(
            ambient,
            side_boundary["Y_first"],
            side,
        )
        nominal = _relative_bulk_densities_td3(pulled, reference15, side=side)
        actual_without_reference = _bulk_component_densities_td3(
            _x64_local_primitives(rhojet2_local_two_jet(pulled)),
            context=f"{side} reference-omission mutant",
        )
        phi_mutant = _relative_bulk_densities_td3(
            pulled,
            reference15,
            side=side,
            phi_cross_sign=-1.0,
        )
        curvature_mutant = _relative_bulk_densities_td3(
            pulled,
            reference15,
            side=side,
            curvature_cross_sign=-1.0,
        )
        bf_sign_mutant = _relative_bulk_densities_td3(
            pulled,
            reference15,
            side=side,
            bf_pullback_multiplier=SIDE_RADIAL_SIGN[side],
        )
        mutant_failures["reference_bulk_omitted"] = max(
            mutant_failures["reference_bulk_omitted"],
            max(abs(actual_without_reference[name].body - nominal[name].body) for name in BULK_SECTORS),
        )
        mutant_failures["A_cross_phi_sign"] = max(
            mutant_failures["A_cross_phi_sign"],
            abs(phi_mutant["P_kinetic"].body - nominal["P_kinetic"].body),
        )
        mutant_failures["A_cross_A_sign"] = max(
            mutant_failures["A_cross_A_sign"],
            abs(curvature_mutant["BF"].body - nominal["BF"].body),
        )
        mutant_failures["BF_duplicate_side_sign"] = max(
            mutant_failures["BF_duplicate_side_sign"],
            abs(bf_sign_mutant["BF"].body - nominal["BF"].body),
        )
        boundary_ambient = _collar_ambient_x64(side_boundary, 0.0, 3)
        boundary_pulled, _reference = _pullback_x64_and_reference15(
            boundary_ambient,
            side_boundary["Y_first"],
            side,
        )
        nominal_ghy = _ghy_density_td3(boundary_pulled, side=side)
        reversed_ghy = _ghy_density_td3(boundary_pulled, side=side, normal_sign=1.0)
        mutant_failures["GHY_normal_reversed"] = max(
            mutant_failures["GHY_normal_reversed"],
            abs(reversed_ghy.body - nominal_ghy.body),
        )
    nominal_interface = _interface_component_densities_td3(boundary)
    robin_mutant = _interface_component_densities_td3(
        boundary,
        robin_acceleration_sign=1.0,
    )
    mutant_failures["Robin_plus_y_a"] = abs(
        robin_mutant["Robin"].body - nominal_interface["Robin"].body
    )

    flrw = _flrw_gauss_witness()
    V4_zero = _regular_v4_td3(
        TaylorDual3.constant(1.2) + TaylorDual3.eta(0.3),
        (TaylorDual3.eta(0.2), TaylorDual3.eta(-0.1), TaylorDual3.eta(0.4)),
    )
    V4_zero_regular = bool(not V4_zero.coefficients)
    naive_phi_norm_rejected = False
    try:
        sum(
            (component * component for component in (
                TaylorDual3.eta(0.2),
                TaylorDual3.eta(-0.1),
                TaylorDual3.eta(0.4),
            )),
            TaylorDual3.constant(0.0),
        ).sqrt()
    except TaylorDual3InputError:
        naive_phi_norm_rejected = True

    free2, tangent2 = _pinned_member_vectors(2)
    secondary_actual = local_density_values_and_eta_jvps(
        free2,
        tangent2,
        2,
        2,
        points[0],
        rhos[0],
    )
    secondary_expected = _route_c_secondary_local_values(
        free2,
        2,
        points[0],
        rhos[0],
    )
    secondary_values = np.asarray(secondary_actual["values"], dtype=float)
    secondary_residual = float(np.max(np.abs(secondary_values - secondary_expected)))
    secondary_sign_mismatches = sum(
        int(math.copysign(1.0, actual) != math.copysign(1.0, expected))
        for actual, expected in zip(secondary_values, secondary_expected)
        if abs(actual) > 1.0e-12 and abs(expected) > 1.0e-12
    )

    free1, tangent1 = _pinned_member_vectors(1)
    rejection_cases = (
        lambda: local_density_values_and_eta_jvps(free1[:-1], tangent1, 1, 1, points[0], 0.5),
        lambda: local_density_values_and_eta_jvps(free1, tangent1[:-1], 1, 1, points[0], 0.5),
        lambda: local_density_values_and_eta_jvps(free1, tangent1, 1, 1, points[0][:-1], 0.5),
        lambda: local_density_values_and_eta_jvps(free1, tangent1, 1, 1, points[0], -1.0e-9),
        lambda: local_density_values_and_eta_jvps(free1, tangent1, 1, 1, points[0], 1.0 + 1.0e-9),
        lambda: local_density_values_and_eta_jvps(free1, tangent1, 1, 1, points[0], True),
    )
    rejections = []
    for case in rejection_cases:
        try:
            case()
        except TaylorDual3InputError:
            rejections.append(True)
        else:
            rejections.append(False)

    value_tolerance = 1.0e-11
    jvp_tolerance = 2.0e-11
    mutant_threshold = 1.0e-7
    domain_pass = {
        category: bool(
            all_finite
            and worst_value[category] <= value_tolerance
            and worst_jvp[category] <= jvp_tolerance
        )
        for category in categories
    }
    mutants_pass = bool(
        all(value > mutant_threshold for value in mutant_failures.values())
        and flrw["pass"]
        and V4_zero_regular
        and naive_phi_norm_rejected
    )
    passed = bool(
        all(domain_pass.values())
        and mutants_pass
        and secondary_residual <= 2.0e-10
        and secondary_sign_mismatches == 0
        and all(rejections)
    )
    return {
        "component_names": LOCAL_DENSITY_COMPONENTS,
        "component_count": len(LOCAL_DENSITY_COMPONENTS),
        "sampled_N": (1, 2, 3),
        "sampled_T4_points": points,
        "sampled_bulk_rho": rhos,
        "torch_route_a_c2_rows": rows,
        "max_abs_value_residual_by_domain": worst_value,
        "max_abs_eta_jvp_residual_by_domain": worst_jvp,
        "value_tolerance": value_tolerance,
        "eta_jvp_tolerance": jvp_tolerance,
        "domain_pass": domain_pass,
        "effective_mutant_max_abs_failures": mutant_failures,
        "effective_mutant_threshold": mutant_threshold,
        "flat_spatial_FLRW_gauss_witness": flrw,
        "V4_phi_zero_regular_and_exact_zero": V4_zero_regular,
        "naive_phi_norm_at_zero_rejected_control": naive_phi_norm_rejected,
        "route_c_secondary_value_max_abs_residual": secondary_residual,
        "route_c_secondary_nonzero_sign_mismatches": secondary_sign_mismatches,
        "route_c_secondary_never_used_for_jvp": True,
        "fail_closed_rejection_results": rejections,
        "all_outputs_finite": all_finite,
        "pass": passed,
    }


def build_report() -> dict[str, Any]:
    upstream = _load_pinned_upstream()
    algebra = _check_mixed_algebra()
    validation = _check_fail_closed_inputs()
    analytic = _check_analytic_identities()
    rotation = _check_so3()
    decoder = _check_decoder()
    local_densities = _check_local_densities()
    decision = {
        "taylor_dual3_independent_eta_spatial_degree_three_algebra_pass": bool(
            algebra["pass"] and validation["pass"]
        ),
        "taylor_dual3_analytic_identities_sampled_within_tolerance_pass": bool(analytic["pass"]),
        "so3_entire_z_origin_regular_orthogonality_and_eta_jvp_sampled_pass": bool(rotation["pass"]),
        "full_t4_decoder_implemented_and_sampled_against_pinned_oracles_pass": bool(
            decoder["pass"]
        ),
        "local_bulk_density_values_and_eta_jvps_sampled_N1_N3_against_pinned_torch_pass": bool(
            local_densities["domain_pass"]["bulk"]
            and local_densities["pass"]
        ),
        "local_ghy_density_values_and_eta_jvps_sampled_N1_N3_against_pinned_torch_pass": bool(
            local_densities["domain_pass"]["GHY"]
            and local_densities["pass"]
        ),
        "local_interface_density_values_and_eta_jvps_sampled_N1_N3_against_pinned_torch_pass": bool(
            local_densities["domain_pass"]["interface"]
            and local_densities["pass"]
        ),
        "twenty_separate_local_density_values_and_eta_jvps_sampled_pass": bool(
            local_densities["pass"]
        ),
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
            "torch_c2_multin_v5_6_5_6_sha256": TORCH_C2_ORACLE_SHA256,
            "torch_route_a_multin_v5_6_5_5_sha256": TORCH_ROUTE_A_WRAPPER_SHA256,
            "literal_torch_route_a_v5_6_5_sha256": TORCH_ROUTE_A_CORE_SHA256,
            "C2_multi_N_primitive_bundle_sha256": C2_BUNDLE_SHA256,
            "literal_action_contract_sha256": LITERAL_ACTION_SHA256,
            "route_c_v5_6_6_3_secondary_values_sha256": ROUTE_C_ORACLE_SHA256,
            "route_c_v5_6_6_3_secondary_values_schema": ROUTE_C_ORACLE_SCHEMA,
        },
        "algebra": algebra,
        "fail_closed_inputs": validation,
        "analytic_identities": analytic,
        "so3": rotation,
        "decoder": decoder,
        "local_densities": local_densities,
        "decision": decision,
        "scope": (
            "M3 local-density milestone: sparse float64 Taylor algebra in four spatial variables through degree three "
            "with an independent nilpotent eta axis, plus SO(3) Rodrigues entire-z series on guarded inputs: "
            "|body(q)| <= pi-1 and non-body coefficient l1 <= 8. Analytic identities, orthogonality and eta-JVP "
            "consistency are sampled float64 "
            "checks, not symbolic proofs or rounding enclosures. The common-first decoder returns value, "
            "eta-JVP and complete 5D two-jets for C2 ambient X64, pulled X64, reference 15 and X79; its generic "
            "N,K implementation is sampled against byte-pinned decoder oracles only at N=1,2,3 and by x2/x3 "
            "probes at N=9,11. The eta oracle uses finite differences only inside the sampled self-check, never "
            "inside the decoder pipeline. The API returns twelve relative bulk, two GHY and six shared-interface "
            "densities separately, with values and exact eta-direction JVPs sampled at N=1,2,3, two T4 coordinate "
            "points of the pinned N=1,2,3 members "
            "and bulk rho=0.23,0.71 against byte-pinned Torch Route A+C2 and torch.func.jvp. Route C v5.6.6.3 "
            "is a secondary value/sign check only and never certifies JVPs. Bulk rho and boundary GHY/interface "
            "domains remain separate; no pointwise S_total is formed. The regular V4 formula is finite at phi=0. "
            "No integrated action, quadrature, density margin certificate, uniform bridge, C1/N1 or B4/B5 claim. No receipt "
            "or artifact is written by design."
        ),
    }


def main() -> None:
    report = build_report()
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
