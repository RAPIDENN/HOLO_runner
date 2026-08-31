#!/usr/bin/env python3
"""Derive and gate a Dirac critical-bath AQUAL spectral candidate.

The previous equilibrium band-edge candidate generated the required
three-halves power but the wrong variational sign.  This module changes the
microscopic question.  It couples a *filled negative-energy* Clifford bath to
the spatial gradient vector ``a_i``.  At every physical point the bath has an
internal two-dimensional Dirac density of states

    rho(epsilon) = rho1 * epsilon,       0 <= epsilon <= Lambda,

and one-particle Hamiltonian

    H_epsilon = epsilon Gamma_1 + y a_i Gamma_{i+2}.

The anticommuting matrices give energies
``+/-sqrt(epsilon**2+y**2*|a|**2)`` without inserting ``|a|`` in the
microscopic coupling.  Filling the negative branch and subtracting its
zero-gradient energy gives the Lorentzian static density

    L_bath = g*rho1/3 * [
        (Lambda**2+y**2*a**2)**(3/2) - Lambda**3 - y**3*|a|**3
    ].

Its positive analytic quadratic term can cancel a bare spatial stiffness at
the critical matching point.  The remaining term is negative and cubic, so
it has the AQUAL sign that the chemical bath lacked.  At the same matching
point the complete finite-band response is

    mu(x) = 1 + x - sqrt(1+x**2),        x=|a|/a0,
    a0 = Lambda/y.

This is an explicit uniform-static spectral construction, not yet a finite
local QFT or a completed HOLO theory.  The executable gate keeps separate the
algebraic result from
the still-open protection, time-dependent, relativistic, lensing and 5D
origin requirements.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TARGET = HERE / "artifacts" / "nonlinear_collector_action.json"
BAND_EDGE = HERE / "artifacts" / "c2_band_edge_continuum.json"
ROUTE_MATRIX = HERE / "artifacts" / "holo_nonlinear_route_matrix.json"
OUTPUT = HERE / "artifacts" / "dirac_critical_bath_gate.json"

SCHEMA = "holo.dirac-critical-bath-gate.v1"
CLIFFORD_NEGATIVE_BRANCHES_PER_MULTIPLET = 2


class DiracBathInputError(ValueError):
    """A microscopic bath parameter or source certificate is malformed."""


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DiracBathInputError(f"cannot read {path}: {exc}") from exc
    if type(value) is not dict:
        raise DiracBathInputError(f"{path}: expected a JSON object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise DiracBathInputError(f"{name} must be positive and finite")
    return result


def _nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise DiracBathInputError(f"{name} must be nonnegative and finite")
    return result


def _finite_product(*values: float, name: str) -> float:
    """Multiply finite factors without avoidable intermediate overflow.

    The helper is intentionally binary64-only: it preserves representable
    products whose naive evaluation would overflow/underflow midway, and
    turns a genuinely unrepresentable result into the module's input error.
    """

    sign = 1.0
    mantissa = 1.0
    exponent = 0
    for raw in values:
        value = float(raw)
        if not math.isfinite(value):
            raise DiracBathInputError(f"{name} received a nonfinite factor")
        if value == 0.0:
            return math.copysign(0.0, sign * value)
        if value < 0.0:
            sign = -sign
            value = -value
        factor_mantissa, factor_exponent = math.frexp(value)
        mantissa *= factor_mantissa
        mantissa, carry = math.frexp(mantissa)
        exponent += factor_exponent + carry
    try:
        result = math.ldexp(sign * mantissa, exponent)
    except OverflowError as exc:
        raise DiracBathInputError(f"{name} is outside binary64 range") from exc
    if not math.isfinite(result):
        raise DiracBathInputError(f"{name} is outside binary64 range")
    return result


def _finite_ratio_product(
    numerators: tuple[float, ...],
    denominators: tuple[float, ...],
    *,
    name: str,
) -> float:
    """Evaluate a product ratio without materializing extreme powers."""

    sign = 1.0
    mantissa = 1.0
    exponent = 0
    for raw, direction in (
        *((value, 1) for value in numerators),
        *((value, -1) for value in denominators),
    ):
        value = float(raw)
        if not math.isfinite(value) or (direction < 0 and value == 0.0):
            raise DiracBathInputError(f"{name} has an invalid ratio factor")
        if value == 0.0:
            return 0.0
        if value < 0.0:
            sign = -sign
            value = -value
        factor_mantissa, factor_exponent = math.frexp(value)
        if direction > 0:
            mantissa *= factor_mantissa
            exponent += factor_exponent
        else:
            mantissa /= factor_mantissa
            exponent -= factor_exponent
        mantissa, carry = math.frexp(mantissa)
        exponent += carry
    try:
        result = math.ldexp(sign * mantissa, exponent)
    except OverflowError as exc:
        raise DiracBathInputError(f"{name} is outside binary64 range") from exc
    if not math.isfinite(result):
        raise DiracBathInputError(f"{name} is outside binary64 range")
    return result


def _scaled_power_difference_product(
    high: float,
    low: float,
    degree: int,
    *factors: float,
    name: str,
) -> float:
    """Return ``prod(factors)*(high**degree-low**degree)`` robustly."""

    if not 0.0 <= low <= high or degree < 1:
        raise DiracBathInputError(f"invalid power difference for {name}")
    if high == 0.0:
        return 0.0
    ratio = low / high
    if ratio == 0.0:
        relative = 1.0
    elif ratio == 1.0:
        return 0.0
    else:
        relative = -math.expm1(degree * math.log(ratio))
    return _finite_product(
        *factors,
        *([high] * degree),
        relative,
        name=name,
    )


def _sea_integral(
    mass: float,
    low: float,
    high: float,
    *,
    weights: tuple[float, ...] = (),
) -> float:
    """Evaluate a weighted ``integral e*(hypot(e,m)-e) de`` robustly."""

    if mass == 0.0 or low == high:
        return 0.0

    # When the lower edge is well below the upper edge, two individually
    # stable zero-edge primitives are more accurate than cancelling the two
    # almost-equal divided differences of the gapped closed form.
    if low > 0.0 and low / high < 0.5 and mass / high < 0.125:
        result = math.fsum(
            [
                _sea_integral(mass, 0.0, high, weights=weights),
                -_sea_integral(mass, 0.0, low, weights=weights),
            ]
        )
        if not math.isfinite(result) or result < 0.0:
            raise DiracBathInputError("sea integral lost numerical positivity")
        return result

    # Small-m expansions avoid subtracting the analytic high-energy pieces.
    small_scale = low if low > 0.0 else high
    small_limit = 1.0e-3 if low > 0.0 else 0.125
    if mass / small_scale < small_limit:
        quadratic = _scaled_power_difference_product(
            high,
            low,
            1,
            *weights,
            0.5,
            mass,
            mass,
            name="sea quadratic term",
        )
        if low == 0.0:
            cubic = _finite_product(
                *weights,
                -1.0 / 3.0,
                mass,
                mass,
                mass,
                name="sea cubic term",
            )
        else:
            cubic = 0.0
        if low > 0.0:
            quartic = _finite_product(
                *weights,
                -0.125,
                mass,
                mass,
                mass,
                mass,
                high - low,
                1.0 / high,
                1.0 / low,
                name="sea quartic term",
            )
        else:
            quartic = _finite_product(
                *weights,
                0.125,
                mass,
                mass,
                mass,
                mass,
                1.0 / high,
                name="sea quartic term",
            )
        higher_terms: list[float] = []
        if low == 0.0:
            higher_terms.extend(
                [
                    _finite_product(
                        *weights,
                        -1.0 / 48.0,
                        *([mass] * 6),
                        *([1.0 / high] * 3),
                        name="sea sixth-order term",
                    ),
                    _finite_product(
                        *weights,
                        1.0 / 128.0,
                        *([mass] * 8),
                        *([1.0 / high] * 5),
                        name="sea eighth-order term",
                    ),
                    _finite_product(
                        *weights,
                        -1.0 / 256.0,
                        *([mass] * 10),
                        *([1.0 / high] * 7),
                        name="sea tenth-order term",
                    ),
                ]
            )
        result = math.fsum([quadratic, cubic, quartic, *higher_terms])
        if not math.isfinite(result) or result < 0.0:
            raise DiracBathInputError("sea integral lost numerical positivity")
        return result

    # For m >> high, expand in high/m.  Every term is evaluated as a scaled
    # product so m=1e308 with a unit cutoff remains representable.
    if mass / high > 1.0e3:
        terms = [
            _scaled_power_difference_product(
                high,
                low,
                2,
                *weights,
                0.5,
                mass,
                name="large-m sea term",
            ),
            _scaled_power_difference_product(
                high,
                low,
                3,
                *weights,
                -1.0 / 3.0,
                name="large-m sea term",
            ),
            _scaled_power_difference_product(
                high,
                low,
                4,
                *weights,
                0.125,
                1.0 / mass,
                name="large-m sea term",
            ),
            _scaled_power_difference_product(
                high,
                low,
                6,
                *weights,
                -1.0 / 48.0,
                1.0 / mass,
                1.0 / mass,
                1.0 / mass,
                name="large-m sea term",
            ),
        ]
        result = math.fsum(terms)
        if not math.isfinite(result) or result < 0.0:
            raise DiracBathInputError("large-m sea integral is outside range")
        return result

    mass_ratio = mass / high
    low_ratio = low / high
    radial_high = math.hypot(1.0, mass_ratio)
    radial_low = math.hypot(low_ratio, mass_ratio)
    radial_divided_difference = (
        (1.0 + low_ratio)
        / (radial_high + radial_low)
        * (
            radial_high * radial_high
            + radial_high * radial_low
            + radial_low * radial_low
        )
    )
    bare_divided_difference = 1.0 + low_ratio + low_ratio * low_ratio
    dimensionless = (
        (1.0 - low_ratio)
        * (radial_divided_difference - bare_divided_difference)
        / 3.0
    )
    result = _finite_product(
        *weights,
        high,
        high,
        high,
        dimensionless,
        name="sea integral",
    )
    if not math.isfinite(result) or result < 0.0:
        raise DiracBathInputError("sea integral lost numerical positivity")
    return result


def _degeneracy(value: int) -> int:
    if type(value) is not int or value < 1:
        raise DiracBathInputError("degeneracy must be a positive integer")
    return value


def clifford_five() -> tuple[np.ndarray, ...]:
    """Return a Hermitian four-dimensional representation of Cl(5)."""

    identity = np.eye(2, dtype=complex)
    sigma1 = np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    sigma2 = np.asarray([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
    sigma3 = np.asarray([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    return (
        np.kron(sigma1, identity),
        np.kron(sigma2, identity),
        np.kron(sigma3, sigma1),
        np.kron(sigma3, sigma2),
        np.kron(sigma3, sigma3),
    )


def clifford_error(matrices: Sequence[np.ndarray] | None = None) -> float:
    """Return the largest ``{Gamma_A,Gamma_B}-2 delta_AB`` entry."""

    gamma = tuple(clifford_five() if matrices is None else matrices)
    if len(gamma) != 5 or any(matrix.shape != (4, 4) for matrix in gamma):
        raise DiracBathInputError("five 4x4 Clifford matrices are required")
    identity = np.eye(4, dtype=complex)
    errors = []
    for left, matrix_left in enumerate(gamma):
        for right, matrix_right in enumerate(gamma):
            target = 2.0 * identity if left == right else np.zeros_like(identity)
            anticommutator = matrix_left @ matrix_right + matrix_right @ matrix_left
            errors.append(float(np.max(np.abs(anticommutator - target))))
    return max(errors)


def dirac_spectrum(
    internal_momentum: Sequence[float],
    gradient: Sequence[float],
    *,
    velocity: float = 1.0,
    yukawa: float = 1.0,
) -> np.ndarray:
    """Diagonalize ``v k_A Gamma_A + y a_i Gamma_(i+2)``."""

    momentum = np.asarray(internal_momentum, dtype=float)
    field = np.asarray(gradient, dtype=float)
    if momentum.shape != (2,) or field.shape != (3,):
        raise DiracBathInputError("momentum and gradient must have shapes (2,) and (3,)")
    if np.any(~np.isfinite(momentum)) or np.any(~np.isfinite(field)):
        raise DiracBathInputError("spectrum inputs must be finite")
    velocity = _positive(velocity, "velocity")
    yukawa = _positive(yukawa, "yukawa")
    gamma = clifford_five()
    hamiltonian = velocity * (
        momentum[0] * gamma[0] + momentum[1] * gamma[1]
    )
    for index in range(3):
        hamiltonian = hamiltonian + yukawa * field[index] * gamma[index + 2]
    return np.linalg.eigvalsh(hamiltonian)


def bath_lagrangian(
    acceleration: float,
    *,
    cutoff: float = 1.0,
    yukawa: float = 1.0,
    rho_slope: float = 1.0,
    degeneracy: int = 1,
    infrared_gap: float = 0.0,
) -> float:
    """Return the exact filled-sea static density relative to ``a=0``.

    ``rho_slope*epsilon`` is the density of negative-energy branches per
    physical volume and unit energy.  ``infrared_gap`` exposes finite-spacing
    rounding; the exact cubic term requires a continuum down to zero.
    """

    acceleration = _nonnegative(acceleration, "acceleration")
    cutoff = _positive(cutoff, "cutoff")
    yukawa = _positive(yukawa, "yukawa")
    rho_slope = _positive(rho_slope, "rho_slope")
    degeneracy = _degeneracy(degeneracy)
    infrared_gap = _nonnegative(infrared_gap, "infrared_gap")
    if infrared_gap >= cutoff:
        raise DiracBathInputError("infrared_gap must be smaller than cutoff")
    mass = yukawa * acceleration
    if not math.isfinite(mass):
        raise DiracBathInputError("yukawa*acceleration overflowed")
    if mass == 0.0:
        return 0.0
    return _sea_integral(
        mass,
        infrared_gap,
        cutoff,
        weights=(float(degeneracy), rho_slope),
    )


def numerical_bath_lagrangian(
    acceleration: float,
    *,
    cutoff: float = 1.0,
    yukawa: float = 1.0,
    rho_slope: float = 1.0,
    degeneracy: int = 1,
    infrared_gap: float = 0.0,
    intervals: int = 8192,
) -> float:
    """Integrate the local spectral bath by composite Simpson quadrature."""

    acceleration = _nonnegative(acceleration, "acceleration")
    cutoff = _positive(cutoff, "cutoff")
    yukawa = _positive(yukawa, "yukawa")
    rho_slope = _positive(rho_slope, "rho_slope")
    degeneracy = _degeneracy(degeneracy)
    infrared_gap = _nonnegative(infrared_gap, "infrared_gap")
    if infrared_gap >= cutoff:
        raise DiracBathInputError("infrared_gap must be smaller than cutoff")
    if type(intervals) is not int or intervals < 2 or intervals % 2:
        raise DiracBathInputError("intervals must be an even integer >= 2")
    mass = yukawa * acceleration
    if not math.isfinite(mass):
        raise DiracBathInputError("yukawa*acceleration overflowed")
    if mass == 0.0:
        return 0.0
    scaled_gap = infrared_gap / cutoff
    scaled_energy = np.linspace(scaled_gap, 1.0, intervals + 1, dtype=float)
    mass_ratio = mass / cutoff
    if mass >= cutoff:
        inverse_ratio = cutoff / mass
        response = 1.0 / (
            np.hypot(inverse_ratio * scaled_energy, 1.0)
            + inverse_ratio * scaled_energy
        )
        outside = (mass, cutoff, cutoff)
    else:
        if mass_ratio == 0.0:
            values = np.full_like(scaled_energy, 0.5)
            if scaled_energy[0] == 0.0:
                values[0] = 0.0
            response = None
        else:
            response = 1.0 / (
                np.hypot(scaled_energy, mass_ratio) + scaled_energy
            )
        outside = (mass, mass, cutoff)
    if response is not None:
        values = scaled_energy * response
    scaled_spacing = (1.0 - scaled_gap) / intervals
    dimensionless_integral = scaled_spacing / 3.0 * (
        values[0]
        + values[-1]
        + 4.0 * np.sum(values[1:-1:2])
        + 2.0 * np.sum(values[2:-1:2])
    )
    return _finite_product(
        degeneracy,
        rho_slope,
        *outside,
        float(dimensionless_integral),
        name="numerical bath density",
    )


def critical_stiffness(
    *,
    cutoff: float = 1.0,
    yukawa: float = 1.0,
    rho_slope: float = 1.0,
    degeneracy: int = 1,
    infrared_gap: float = 0.0,
) -> float:
    """Return the bare ``K2`` in ``-K2*a^2`` cancelling the bath quadratic."""

    cutoff = _positive(cutoff, "cutoff")
    yukawa = _positive(yukawa, "yukawa")
    rho_slope = _positive(rho_slope, "rho_slope")
    degeneracy = _degeneracy(degeneracy)
    infrared_gap = _nonnegative(infrared_gap, "infrared_gap")
    if infrared_gap >= cutoff:
        raise DiracBathInputError("infrared_gap must be smaller than cutoff")
    return _finite_product(
        0.5,
        degeneracy,
        rho_slope,
        cutoff - infrared_gap,
        yukawa,
        yukawa,
        name="critical stiffness",
    )


def matched_lagrangian(
    acceleration: float,
    *,
    cutoff: float = 1.0,
    yukawa: float = 1.0,
    rho_slope: float = 1.0,
    degeneracy: int = 1,
    infrared_gap: float = 0.0,
) -> float:
    """Return ``-K2*a^2+L_bath`` at the quadratic critical point."""

    acceleration = _nonnegative(acceleration, "acceleration")
    yukawa_value = _positive(yukawa, "yukawa")
    mass = yukawa_value * acceleration
    if not math.isfinite(mass):
        raise DiracBathInputError("yukawa*acceleration overflowed")
    cutoff_value = _positive(cutoff, "cutoff")
    gap_value = _nonnegative(infrared_gap, "infrared_gap")
    degeneracy_value = _degeneracy(degeneracy)
    rho_value = _positive(rho_slope, "rho_slope")
    if gap_value >= cutoff_value:
        raise DiracBathInputError("infrared_gap must be smaller than cutoff")
    # The exact expression subtracts two O(m^2) numbers.  Use its convergent
    # small-m series when that cancellation would discard the quartic/cubic
    # remainder in binary64.
    if gap_value > 0.0 and mass < 1.0e-2 * gap_value:
        ratio = gap_value / cutoff_value
        terms = [
            _finite_ratio_product(
                (
                    -0.125,
                    float(degeneracy_value),
                    rho_value,
                    *([mass] * 4),
                    1.0 - ratio,
                ),
                (gap_value,),
                name="gapped matched quartic density",
            ),
            _finite_ratio_product(
                (
                    1.0 / 48.0,
                    float(degeneracy_value),
                    rho_value,
                    *([mass] * 6),
                    1.0 - ratio**3,
                ),
                (gap_value, gap_value, gap_value),
                name="gapped matched sixth-order density",
            ),
            _finite_ratio_product(
                (
                    -1.0 / 128.0,
                    float(degeneracy_value),
                    rho_value,
                    *([mass] * 8),
                    1.0 - ratio**5,
                ),
                (gap_value,) * 5,
                name="gapped matched eighth-order density",
            ),
        ]
        return math.fsum(terms)
    if gap_value == 0.0 and mass < 1.0e-4 * cutoff_value:
        terms = [
            _finite_product(
                -1.0 / 3.0,
                degeneracy_value,
                rho_value,
                mass,
                mass,
                mass,
                name="gapless matched cubic density",
            ),
            _finite_ratio_product(
                (
                    0.125,
                    float(degeneracy_value),
                    rho_value,
                    *([mass] * 4),
                ),
                (cutoff_value,),
                name="gapless matched quartic density",
            ),
            _finite_ratio_product(
                (
                    -1.0 / 48.0,
                    float(degeneracy_value),
                    rho_value,
                    *([mass] * 6),
                ),
                (cutoff_value, cutoff_value, cutoff_value),
                name="gapless matched sixth-order density",
            ),
        ]
        return math.fsum(terms)
    bare = _finite_product(
        -0.5,
        degeneracy_value,
        rho_value,
        cutoff_value - gap_value,
        yukawa_value,
        yukawa_value,
        acceleration,
        acceleration,
        name="matched bare density",
    )
    bath = bath_lagrangian(
        acceleration,
        cutoff=cutoff_value,
        yukawa=yukawa_value,
        rho_slope=rho_value,
        degeneracy=degeneracy_value,
        infrared_gap=gap_value,
    )
    result = math.fsum([bare, bath])
    if not math.isfinite(result):
        raise DiracBathInputError("matched density is outside binary64 range")
    return result


def acceleration_scale(*, cutoff: float = 1.0, yukawa: float = 1.0) -> float:
    """Return the gapless matched scale ``a0=Lambda/y``."""

    return _positive(cutoff, "cutoff") / _positive(yukawa, "yukawa")


def matched_mu(x: float) -> float:
    """Return the exact gapless constitutive function at ``x=a/a0``.

    The rationalized expression avoids cancellation for very small ``x``.
    """

    x = _nonnegative(x, "x")
    if x == 0.0:
        return 0.0
    root = math.hypot(1.0, x)
    if x >= 1.0:
        inverse = 1.0 / x
        deficit = inverse / (math.hypot(1.0, inverse) + 1.0)
        return 1.0 - deficit
    return 2.0 * x / (1.0 + x + root)


def matched_mu_prime(x: float) -> float:
    """Return ``d mu/dx=1-x/sqrt(1+x^2)``."""

    x = _nonnegative(x, "x")
    if x >= 1.0:
        inverse = 1.0 / x
        scaled_root = math.hypot(1.0, inverse)
        return inverse * inverse / (
            scaled_root * (scaled_root + 1.0)
        )
    root = math.hypot(1.0, x)
    return 1.0 / (root * (root + x))


def normalized_field_function(x: float) -> float:
    """Return ``F(X)`` with ``X=x^2`` and ``F'(X)=mu(x)``."""

    x = _nonnegative(x, "x")
    if x < 1.0e-3:
        # Expansion through x^10 avoids subtracting the matched x^2 terms.
        return (
            (2.0 / 3.0) * x**3
            - 0.25 * x**4
            + (1.0 / 24.0) * x**6
            - (1.0 / 64.0) * x**8
            + (7.0 / 960.0) * x**10
        )
    if x > 1.0e6:
        if x > math.sqrt(np.finfo(float).max) / 2.0:
            raise DiracBathInputError("x is too large for a finite field function")
        inverse = 1.0 / x
        return (
            x * x
            - x
            + 2.0 / 3.0
            - 0.25 * inverse
            + (1.0 / 24.0) * inverse**3
        )
    return x * x - (2.0 / 3.0) * (
        (1.0 + x * x) ** 1.5 - 1.0 - x**3
    )


def solve_spherical_field(newtonian_ratio: float) -> float:
    """Solve ``mu(x)*x=y_N`` by monotone bisection."""

    target = _nonnegative(newtonian_ratio, "newtonian_ratio")
    if target == 0.0:
        return 0.0
    lower = 0.0
    upper = (
        2.0 * math.sqrt(target)
        if target < 0.25
        else max(1.0, target + 1.0)
    )
    while matched_mu(upper) * upper < target:
        if upper > np.finfo(float).max / 2.0:
            return target
        upper *= 2.0
    for _ in range(180):
        middle = lower + 0.5 * (upper - lower)
        if middle == lower or middle == upper:
            break
        if matched_mu(middle) * middle < target:
            lower = middle
        else:
            upper = middle
    return lower + 0.5 * (upper - lower)


def mixed_statistics_sum_rule() -> dict[str, float | bool | str]:
    """Expose a finite stable-field cancellation witness, not a symmetry proof.

    A filled fermionic negative branch contributes weight ``+1`` to the
    Lorentzian determinant.  A real bosonic zero-point oscillator contributes
    ``-1/2``.  One fermion of coupling ``y`` plus eight real bosons of coupling
    ``y/2`` cancels the analytic quadratic supertrace but leaves half of the
    fermionic negative cubic coefficient.
    """

    components = ((1.0, 1.0, 1), (-0.5, 0.5, 8))
    quadratic = sum(weight * count * coupling**2 for weight, coupling, count in components)
    cubic = sum(weight * count * coupling**3 for weight, coupling, count in components)
    return {
        "field_content": "one filled fermion branch at y plus eight real bosons at y/2",
        "signed_quadratic_sum": quadratic,
        "signed_cubic_sum": cubic,
        "quadratic_cancels": math.isclose(quadratic, 0.0, abs_tol=1.0e-15),
        "negative_lagrangian_cubic_survives": cubic > 0.0,
        "radiatively_protected": False,
    }


def _unit_sea_integral(mass: float, cutoff: float) -> float:
    """Return ``integral epsilon*(sqrt(epsilon^2+m^2)-epsilon) d epsilon``."""

    mass = _nonnegative(mass, "mass")
    cutoff = _positive(cutoff, "cutoff")
    return _sea_integral(mass, 0.0, cutoff)


def mixed_bath_energy(mass: float, *, cutoff: float = 1.0) -> float:
    """Return the 1F+8B static energy in units of its common DOS slope.

    The convention counts one filled negative fermion branch.  Eight stable
    real bosonic oscillators contribute four zero-point determinants at mass
    ``m/2``.  Hence ``U=-I(m)+4 I(m/2)``.
    """

    mass = _nonnegative(mass, "mass")
    cutoff = _positive(cutoff, "cutoff")
    if mass / cutoff <= 1.0e-2:
        terms = [
            _finite_product(
                1.0 / 6.0, mass, mass, mass, name="mixed cubic energy"
            ),
            _finite_ratio_product(
                (-3.0 / 32.0, *([mass] * 4)),
                (cutoff,),
                name="mixed quartic energy",
            ),
            _finite_ratio_product(
                (5.0 / 256.0, *([mass] * 6)),
                (cutoff,) * 3,
                name="mixed sixth-order energy",
            ),
            _finite_ratio_product(
                (-63.0 / 8192.0, *([mass] * 8)),
                (cutoff,) * 5,
                name="mixed eighth-order energy",
            ),
        ]
        result = math.fsum(terms)
        if result < 0.0 or not math.isfinite(result):
            raise DiracBathInputError("mixed bath energy lost numerical positivity")
        return result
    fermion = _unit_sea_integral(mass, cutoff)
    bosons = _finite_product(
        4.0,
        _unit_sea_integral(0.5 * mass, cutoff),
        name="mixed bosonic energy",
    )
    result = bosons - fermion
    if not math.isfinite(result) or result < 0.0:
        raise DiracBathInputError("mixed bath energy lost numerical positivity")
    return result


def _unit_sea_integral_prime(mass: float, cutoff: float) -> float:
    root = math.hypot(cutoff, mass)
    ratio = mass / root
    response = ratio / (1.0 + ratio)
    return _finite_product(
        cutoff, cutoff, response, name="sea first derivative"
    )


def _unit_sea_integral_second(mass: float, cutoff: float) -> float:
    root = math.hypot(cutoff, mass)
    return _finite_product(
        cutoff,
        cutoff / root,
        cutoff / (root + mass),
        cutoff / (root + mass),
        name="sea second derivative",
    )


def mixed_bath_energy_prime(mass: float, *, cutoff: float = 1.0) -> float:
    """Return the first derivative of the mixed stable-bath energy."""

    mass = _nonnegative(mass, "mass")
    cutoff = _positive(cutoff, "cutoff")
    return -_unit_sea_integral_prime(
        mass, cutoff
    ) + 2.0 * _unit_sea_integral_prime(0.5 * mass, cutoff)


def mixed_bath_energy_second(mass: float, *, cutoff: float = 1.0) -> float:
    """Return the positive curvature of the mixed stable-bath energy."""

    mass = _nonnegative(mass, "mass")
    cutoff = _positive(cutoff, "cutoff")
    return -_unit_sea_integral_second(
        mass, cutoff
    ) + _unit_sea_integral_second(0.5 * mass, cutoff)


def temporal_kernel_deficit(
    frequency: float,
    *,
    cutoff: float = 1.0,
    yukawa: float = 1.0,
    rho_slope: float = 1.0,
    degeneracy: int = 1,
) -> float:
    """Return ``K(0)-K(i omega)`` for the gapless onsite fermion bubble.

    The exact quadratic response is nonanalytic at zero frequency even though
    the bath is ultralocal in physical space.  Its low-frequency limit is
    ``g*rho1*y^2*pi*|omega|/8``.
    """

    frequency = float(frequency)
    if not math.isfinite(frequency):
        raise DiracBathInputError("frequency must be finite")
    cutoff = _positive(cutoff, "cutoff")
    yukawa = _positive(yukawa, "yukawa")
    rho_slope = _positive(rho_slope, "rho_slope")
    degeneracy = _degeneracy(degeneracy)
    magnitude = abs(frequency)
    if magnitude == 0.0:
        return 0.0
    if magnitude >= cutoff:
        ratio = cutoff / magnitude
        z = 2.0 * ratio
        atan_over_z = 1.0 if z == 0.0 else math.atan(z) / z
        return _finite_product(
            0.5,
            degeneracy,
            rho_slope,
            yukawa,
            yukawa,
            cutoff,
            atan_over_z,
            name="temporal kernel deficit",
        )
    angle = math.atan2(cutoff, 0.5 * magnitude)
    return _finite_product(
        0.25,
        degeneracy,
        rho_slope,
        yukawa,
        yukawa,
        magnitude,
        angle,
        name="temporal kernel deficit",
    )


def discrete_bath_lagrangian(
    acceleration: float,
    levels: Sequence[float],
    weights: Sequence[float],
    *,
    yukawa: float = 1.0,
) -> float:
    """Return a finite filled-sea sum, exposing continuum-order limits."""

    acceleration = _nonnegative(acceleration, "acceleration")
    yukawa = _positive(yukawa, "yukawa")
    energy = np.asarray(levels, dtype=float)
    measure = np.asarray(weights, dtype=float)
    if energy.ndim != 1 or measure.shape != energy.shape or energy.size == 0:
        raise DiracBathInputError("levels and weights must be nonempty 1D peers")
    if np.any(~np.isfinite(energy)) or np.any(energy < 0.0):
        raise DiracBathInputError("levels must be finite and nonnegative")
    if np.any(~np.isfinite(measure)) or np.any(measure <= 0.0):
        raise DiracBathInputError("weights must be finite and positive")
    mass = yukawa * acceleration
    if not math.isfinite(mass):
        raise DiracBathInputError("yukawa*acceleration overflowed")
    result = float(np.sum(measure * (np.hypot(energy, mass) - energy)))
    if not math.isfinite(result):
        raise DiracBathInputError("discrete bath density is outside binary64 range")
    return result


def discrete_critical_remainder(
    acceleration: float,
    levels: Sequence[float],
    weights: Sequence[float],
    *,
    yukawa: float = 1.0,
) -> float:
    """Subtract the finite bath's quadratic response.

    All levels must be positive.  The remainder is quartic at the origin; a
    finite tower therefore cannot reproduce the continuum cubic asymptote.
    """

    acceleration = _nonnegative(acceleration, "acceleration")
    yukawa = _positive(yukawa, "yukawa")
    energy = np.asarray(levels, dtype=float)
    measure = np.asarray(weights, dtype=float)
    if energy.ndim != 1 or measure.shape != energy.shape or energy.size == 0:
        raise DiracBathInputError("levels and weights must be nonempty 1D peers")
    if np.any(~np.isfinite(energy)) or np.any(energy <= 0.0):
        raise DiracBathInputError("critical subtraction requires positive levels")
    if np.any(~np.isfinite(measure)) or np.any(measure <= 0.0):
        raise DiracBathInputError("weights must be finite and positive")
    mass = yukawa * acceleration
    if not math.isfinite(mass):
        raise DiracBathInputError("yukawa*acceleration overflowed")
    if mass < 1.0e-3 * float(np.min(energy)):
        terms = [
            _finite_ratio_product(
                (-0.125, float(weight), mass, mass, mass, mass),
                (float(level), float(level), float(level)),
                name="discrete critical quartic term",
            )
            for level, weight in zip(energy, measure, strict=True)
        ]
        result = math.fsum(terms)
        if not math.isfinite(result):
            raise DiracBathInputError(
                "discrete critical remainder is outside binary64 range"
            )
        return result
    quadratic = 0.5 * yukawa**2 * float(np.sum(measure / energy))
    return discrete_bath_lagrangian(
        acceleration, energy, measure, yukawa=yukawa
    ) - quadratic * acceleration**2


def build() -> dict[str, Any]:
    target = _read(TARGET)
    band_edge = _read(BAND_EDGE)
    route_matrix = _read(ROUTE_MATRIX)
    if target.get("schema") != "holo.nonlinear-collector-action-target.v1":
        raise DiracBathInputError("unexpected nonlinear collector target schema")
    if target.get("passes", {}).get("all") is not True:
        raise DiracBathInputError("nonlinear collector target is not certified")
    if target.get("action", {}).get("deep_limit") != (
        "mu(x)~x and F(X)~(2/3)*X^(3/2)"
    ):
        raise DiracBathInputError("unexpected nonlinear collector deep limit")
    if target.get("action", {}).get("newtonian_limit") != (
        "mu->1 and F(X)~X+constant"
    ):
        raise DiracBathInputError("unexpected nonlinear collector Newtonian limit")
    if target.get("source", {}).get("fit_origin") != "SPARC training split only":
        raise DiracBathInputError("target observational genealogy is not explicit")
    if band_edge.get("schema") != "holo.c2-band-edge-continuum.v1":
        raise DiracBathInputError("unexpected band-edge schema")
    if band_edge.get("checks", {}).get("all") is not True:
        raise DiracBathInputError("band-edge negative control is not certified")
    if band_edge.get("decision", {}).get("verdict") != (
        "KILL_C2_BAND_EDGE_WRONG_VARIATIONAL_SIGN"
    ):
        raise DiracBathInputError("band-edge sign obstruction is not frozen")
    if band_edge.get("sources", {}).get(
        "inherited_exposed_target_origin"
    ) != target["source"]["fit_origin"]:
        raise DiracBathInputError("band-edge and Dirac target genealogy diverged")
    if route_matrix.get("schema") != "holo.nonlinear-route-matrix.v1":
        raise DiracBathInputError("unexpected nonlinear route-matrix schema")
    if route_matrix.get("passes", {}).get("all") is not True:
        raise DiracBathInputError("nonlinear route matrix is not certified")

    cutoff = 2.4
    yukawa = 1.7
    rho_slope = 0.6
    degeneracy = 4
    probes = np.geomspace(1.0e-3, 4.0, 32)
    relative_integral_errors = []
    for acceleration in probes:
        analytic = bath_lagrangian(
            acceleration,
            cutoff=cutoff,
            yukawa=yukawa,
            rho_slope=rho_slope,
            degeneracy=degeneracy,
        )
        numeric = numerical_bath_lagrangian(
            acceleration,
            cutoff=cutoff,
            yukawa=yukawa,
            rho_slope=rho_slope,
            degeneracy=degeneracy,
        )
        relative_integral_errors.append(abs(numeric / analytic - 1.0))

    momentum = np.asarray([0.37, -0.22])
    gradient = np.asarray([0.19, -0.41, 0.28])
    velocity = 0.73
    spectrum = dirac_spectrum(
        momentum, gradient, velocity=velocity, yukawa=yukawa
    )
    expected_energy = math.sqrt(
        velocity**2 * float(momentum @ momentum)
        + yukawa**2 * float(gradient @ gradient)
    )
    expected_spectrum = np.asarray(
        [-expected_energy, -expected_energy, expected_energy, expected_energy]
    )
    spectrum_error = float(np.max(np.abs(spectrum - expected_spectrum)))

    x_values = np.geomspace(1.0e-9, 1.0e9, 721)
    mu_values = np.asarray([matched_mu(value) for value in x_values])
    mu_prime_values = np.asarray([matched_mu_prime(value) for value in x_values])
    longitudinal = mu_values + x_values * mu_prime_values
    deep = x_values <= 1.0e-4
    high = x_values >= 1.0e4
    deep_mu_slope = float(
        np.polyfit(np.log(x_values[deep]), np.log(mu_values[deep]), 1)[0]
    )
    deep_mu_coefficient = float(np.median(mu_values[deep] / x_values[deep]))
    high_one_minus_mu_coefficient = float(
        np.median((1.0 - mu_values[high]) * x_values[high])
    )

    derivative_points = np.geomspace(1.0e-3, 1.0e3, 80)
    derivative_errors = []
    for x in derivative_points:
        relative_step = 1.0e-4
        plus = x * (1.0 + relative_step)
        minus = x * (1.0 - relative_step)
        numerical_derivative = (
            normalized_field_function(plus)
            - normalized_field_function(minus)
        ) / (plus * plus - minus * minus)
        derivative_errors.append(abs(numerical_derivative - matched_mu(x)))
    maximum_derivative_error = float(max(derivative_errors))

    source_values = np.geomspace(1.0e-12, 1.0e8, 161)
    fields = np.asarray([solve_spherical_field(value) for value in source_values])
    deep_source = source_values <= 1.0e-6
    high_source = source_values >= 1.0e4
    deep_mass_slope = float(
        np.polyfit(np.log(source_values[deep_source]), np.log(fields[deep_source]), 1)[0]
    )
    high_mass_slope = float(
        np.polyfit(np.log(source_values[high_source]), np.log(fields[high_source]), 1)[0]
    )

    a0 = acceleration_scale(cutoff=cutoff, yukawa=yukawa)
    stiffness = critical_stiffness(
        cutoff=cutoff,
        yukawa=yukawa,
        rho_slope=rho_slope,
        degeneracy=degeneracy,
    )
    cubic_coefficient = degeneracy * rho_slope * yukawa**3 / 3.0
    target_cubic_coefficient = 2.0 * stiffness / (3.0 * a0)

    gap = 0.08
    gap_accelerations = np.geomspace(1.0e-7, 1.0e-4, 24)
    gapped_remainders = np.asarray(
        [
            -matched_lagrangian(
                value,
                cutoff=cutoff,
                yukawa=yukawa,
                rho_slope=rho_slope,
                degeneracy=degeneracy,
                infrared_gap=gap,
            )
            for value in gap_accelerations
        ]
    )
    gapped_power = float(
        np.polyfit(np.log(gap_accelerations), np.log(gapped_remainders), 1)[0]
    )
    sum_rule = mixed_statistics_sum_rule()
    mixture_masses = np.geomspace(1.0e-9, 1.0e6, 480) * cutoff
    mixture_energy = np.asarray(
        [mixed_bath_energy(value, cutoff=cutoff) for value in mixture_masses]
    )
    mixture_slope = np.asarray(
        [mixed_bath_energy_prime(value, cutoff=cutoff) for value in mixture_masses]
    )
    mixture_curvature = np.asarray(
        [mixed_bath_energy_second(value, cutoff=cutoff) for value in mixture_masses]
    )
    mixture_deep_coefficient = float(
        np.median(
            mixture_energy[:80] / np.power(mixture_masses[:80], 3)
        )
    )
    frequency_values = np.geomspace(1.0e-12, 1.0e-5, 48) * cutoff
    temporal_deficits = np.asarray(
        [
            temporal_kernel_deficit(
                value,
                cutoff=cutoff,
                yukawa=yukawa,
                rho_slope=rho_slope,
                degeneracy=degeneracy,
            )
            for value in frequency_values
        ]
    )
    temporal_power = float(
        np.polyfit(np.log(frequency_values), np.log(temporal_deficits), 1)[0]
    )
    temporal_linear_coefficient = float(
        np.median(temporal_deficits / frequency_values)
    )
    expected_temporal_coefficient = (
        math.pi * degeneracy * rho_slope * yukawa**2 / 8.0
    )

    positive_levels = np.asarray([0.13, 0.37, 0.91, 1.7]) * cutoff
    level_weights = np.asarray([0.2, 0.4, 0.3, 0.1])
    discrete_accelerations = np.geomspace(1.0e-8, 1.0e-5, 32) * cutoff / yukawa
    discrete_remainders = np.asarray(
        [
            -discrete_critical_remainder(
                value, positive_levels, level_weights, yukawa=yukawa
            )
            for value in discrete_accelerations
        ]
    )
    discrete_positive_tower_power = float(
        np.polyfit(
            np.log(discrete_accelerations),
            np.log(discrete_remainders),
            1,
        )[0]
    )
    zero_level_accelerations = np.geomspace(1.0e-10, 1.0e-6, 32)
    zero_level_response = np.asarray(
        [
            discrete_bath_lagrangian(value, [0.0], [1.0], yukawa=yukawa)
            for value in zero_level_accelerations
        ]
    )
    discrete_zero_mode_power = float(
        np.polyfit(
            np.log(zero_level_accelerations),
            np.log(zero_level_response),
            1,
        )[0]
    )
    target_t = np.geomspace(1.0e-8, 1.0e4, 2048)
    target_mu = -np.expm1(-target_t)
    target_x = np.square(target_t) / target_mu
    candidate_on_target_grid = np.asarray(
        [matched_mu(float(value)) for value in target_x]
    )
    target_absolute_difference = np.abs(candidate_on_target_grid - target_mu)
    target_maximum_absolute_difference = float(
        np.max(target_absolute_difference)
    )
    target_rms_absolute_difference = float(
        np.sqrt(np.mean(np.square(target_absolute_difference)))
    )

    checks = {
        "certified_inputs": True,
        "clifford_coupling_is_linear_and_isotropic": clifford_error() < 1.0e-14,
        "microscopic_spectrum_is_real_and_gapped_by_gradient": spectrum_error
        < 2.0e-15,
        "negative_branch_multiplicity_convention_is_explicit": (
            CLIFFORD_NEGATIVE_BRANCHES_PER_MULTIPLET == 2
            and degeneracy % CLIFFORD_NEGATIVE_BRANCHES_PER_MULTIPLET == 0
        ),
        "spectral_integral_matches_closed_form": max(relative_integral_errors)
        < 3.0e-8,
        "critical_matching_cancels_quadratic_term": math.isclose(
            stiffness,
            0.5 * degeneracy * rho_slope * cutoff * yukawa**2,
            rel_tol=5.0e-16,
            abs_tol=0.0,
        ),
        "remaining_cubic_has_required_negative_lagrangian_sign": cubic_coefficient
        > 0.0,
        "a0_relation_closes": math.isclose(
            cubic_coefficient,
            target_cubic_coefficient,
            rel_tol=2.0e-15,
            abs_tol=0.0,
        ),
        "constitutive_mu_is_between_zero_and_one": bool(
            np.min(mu_values) > 0.0 and np.max(mu_values) < 1.0
        ),
        "constitutive_mu_is_monotone": bool(np.min(mu_prime_values) > 0.0),
        "nonzero_background_is_elliptic": bool(
            np.min(mu_values) > 0.0 and np.min(longitudinal) > 0.0
        ),
        "deep_mu_is_x": abs(deep_mu_slope - 1.0) < 2.0e-6
        and abs(deep_mu_coefficient - 1.0) < 2.0e-5,
        "newtonian_mu_tends_to_one": abs(high_one_minus_mu_coefficient - 0.5)
        < 2.0e-4,
        "field_function_derivative_is_mu": maximum_derivative_error < 4.0e-7,
        "spherical_deep_source_scaling_is_square_root": abs(deep_mass_slope - 0.5)
        < 2.0e-4,
        "spherical_high_source_scaling_is_linear": abs(high_mass_slope - 1.0)
        < 2.0e-4,
        "finite_internal_gap_rounds_cubic_to_quartic": abs(gapped_power - 4.0)
        < 3.0e-3,
        "mixed_statistics_quadratic_sum_rule_exists": bool(
            sum_rule["quadratic_cancels"]
            and sum_rule["negative_lagrangian_cubic_survives"]
        ),
        "mixed_statistics_static_energy_is_positive_and_convex": bool(
            np.min(mixture_energy) > 0.0
            and np.min(mixture_slope) > 0.0
            and np.min(mixture_curvature) > 0.0
            and abs(mixture_deep_coefficient - 1.0 / 6.0) < 2.0e-7
        ),
        "gapless_temporal_kernel_is_linear_not_local_analytic": abs(
            temporal_power - 1.0
        )
        < 2.0e-7
        and abs(
            temporal_linear_coefficient / expected_temporal_coefficient - 1.0
        )
        < 2.0e-6,
        "finite_tower_excludes_exact_cubic_origin": abs(
            discrete_positive_tower_power - 4.0
        )
        < 2.0e-8
        and abs(discrete_zero_mode_power - 1.0) < 2.0e-12,
        "exposed_target_nonidentity_is_explicit": (
            target_maximum_absolute_difference > 0.07
        ),
        "no_raw_observational_table_read_directly": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "uniform_static_spectral_hamiltonian_explicit": True,
        "correct_deep_exponent_and_variational_sign": True,
        "finite_band_interpolation_and_a0_relation_derived": True,
        "pointwise_static_when_internal_bath_has_zero_physical_hopping": True,
        "finite_local_3p1_qft_realization": False,
        "nonnegative_fermion_excitation_spectrum": True,
        "quadratic_matching_or_sum_rule_radiatively_protected": False,
        "gapless_continuum_generated_by_current_finite_HOLO_interval": False,
        "time_dependent_bath_response_local_and_adiabatic_at_zero_gap": False,
        "nonzero_physical_hopping_uniformly_local_as_a_goes_to_zero": False,
        "vacuum_scalar_or_khronon_initial_value_problem_closed": False,
        "parity_and_gravitational_anomalies_cancelled_in_full_field_content": False,
        "five_dimensional_covariant_action_and_constraints_derived": False,
        "matter_coupling_absolute_normalization_derived": False,
        "lensing_and_gravitational_slip_derived": False,
        "current_HOLO_physical_completion": False,
    }

    return {
        "schema": SCHEMA,
        "title": "Dirac critical-bath spectral construction for the AQUAL static operator",
        "classification": (
            "uniform_static_spectral_candidate_survives;"
            "finite_local_qft_radiative_dynamic_relativistic_and_holo_gates_open"
        ),
        "sources": {
            "nonlinear_target": {
                "path": str(TARGET.relative_to(REPO)),
                "sha256": _sha256(TARGET),
            },
            "killed_chemical_band_edge": {
                "path": str(BAND_EDGE.relative_to(REPO)),
                "sha256": _sha256(BAND_EDGE),
            },
            "route_matrix": {
                "path": str(ROUTE_MATRIX.relative_to(REPO)),
                "sha256": _sha256(ROUTE_MATRIX),
            },
            "raw_observational_tables_read_directly": [],
            "inherited_exposed_target_origin": target["source"]["fit_origin"],
        },
        "microscopic_model": {
            "degrees_of_freedom": (
                "At each physical point, filled fermionic Clifford levels with "
                "internal spectral energy epsilon and rho(epsilon)=rho1*epsilon."
            ),
            "hamiltonian": "H_epsilon=epsilon*Gamma1+y*a_i*Gamma_(i+2)",
            "clifford_algebra": "{Gamma_A,Gamma_B}=2*delta_AB",
            "spectrum": "E_+/-=+/-sqrt(epsilon^2+y^2*|a|^2)",
            "branch_counting": (
                "Each 4x4 Clifford multiplet has two negative eigenvalue branches. "
                "The parameter g counts negative branches, so the demonstrated "
                "g=4 corresponds to two 4x4 multiplets before any further species "
                "multiplicity. The 1F+8B sum rule is explicitly per one branch."
            ),
            "microscopic_coupling": (
                "linear in the three components a_i; |a| appears only after "
                "diagonalizing the Hermitian Hamiltonian"
            ),
            "local_realizations": [
                (
                    "zero-physical-hopping pseudogap bath with a two-dimensional "
                    "internal Dirac density of states at every spatial site"
                ),
                (
                    "equal stacks of local 2D Clifford layers; their uniform "
                    "potential is isotropic, while derivative anisotropy must be gated"
                ),
            ],
            "stability_statement": (
                "The one-particle spectrum is real and the finite-cutoff filled sea "
                "is bounded at fixed a. Stability of the coupled gravity/scalar "
                "initial-value problem is a separate open gate."
            ),
        },
        "uniform_static_derivation": {
            "bath_lagrangian": (
                "L_bath=g*rho1/3*[(Lambda^2+y^2*a^2)^(3/2)-Lambda^3-y^3*|a|^3]"
            ),
            "small_a": (
                "L_bath=(g*rho1*Lambda*y^2/2)*a^2"
                "-(g*rho1*y^3/3)*|a|^3+O(a^4/Lambda)"
            ),
            "critical_bare_term": "L_bare=-K2*a^2, K2=g*rho1*Lambda*y^2/2",
            "matched_deep_term": "L_total=-(g*rho1*y^3/3)*|a|^3+O(a^4)",
            "acceleration_scale": "a0=Lambda/y",
            "normalized_action": (
                "L_total=-K2*a0^2*F(X), X=a^2/a0^2; "
                "F~2*X^(3/2)/3"
            ),
            "constitutive_function": "mu(x)=F'(x^2)=1+x-sqrt(1+x^2)",
            "limits": "mu=x+O(x^2) for x<<1; mu=1-1/(2x)+O(x^-2) for x>>1",
            "spherical_equation": "mu(g/a0)*g=g_N",
            "target_scope": (
                "The microscopic curve shares the required deep and Newtonian "
                "limits but is not the exact train-derived collector interpolation."
            ),
        },
        "diagnostics": {
            "parameters": {
                "Lambda": cutoff,
                "y": yukawa,
                "rho1": rho_slope,
                "negative_branch_degeneracy": degeneracy,
                "negative_branches_per_4x4_multiplet": (
                    CLIFFORD_NEGATIVE_BRANCHES_PER_MULTIPLET
                ),
                "equivalent_4x4_multiplets": (
                    degeneracy / CLIFFORD_NEGATIVE_BRANCHES_PER_MULTIPLET
                ),
                "a0": a0,
                "K2": stiffness,
            },
            "clifford_maximum_error": clifford_error(),
            "spectrum_maximum_absolute_error": spectrum_error,
            "spectral_integral_maximum_relative_error": max(
                relative_integral_errors
            ),
            "deep_mu_log_slope": deep_mu_slope,
            "deep_mu_coefficient": deep_mu_coefficient,
            "high_x_coefficient_of_one_minus_mu": high_one_minus_mu_coefficient,
            "minimum_mu_on_nonzero_grid": float(np.min(mu_values)),
            "minimum_longitudinal_elliptic_factor": float(
                np.min(longitudinal)
            ),
            "field_function_derivative_maximum_absolute_error": (
                maximum_derivative_error
            ),
            "deep_spherical_source_mass_slope": deep_mass_slope,
            "high_spherical_source_mass_slope": high_mass_slope,
            "gapped_critically_subtracted_deep_power": gapped_power,
            "mixed_statistics_sum_rule": sum_rule,
            "mixed_statistics_minimum_energy": float(np.min(mixture_energy)),
            "mixed_statistics_minimum_first_derivative": float(
                np.min(mixture_slope)
            ),
            "mixed_statistics_minimum_second_derivative": float(
                np.min(mixture_curvature)
            ),
            "mixed_statistics_deep_energy_coefficient": (
                mixture_deep_coefficient
            ),
            "gapless_temporal_kernel_power": temporal_power,
            "gapless_temporal_kernel_linear_coefficient": (
                temporal_linear_coefficient
            ),
            "expected_temporal_kernel_linear_coefficient": (
                expected_temporal_coefficient
            ),
            "finite_positive_tower_critical_power": (
                discrete_positive_tower_power
            ),
            "finite_tower_zero_mode_power": discrete_zero_mode_power,
            "maximum_absolute_mu_difference_from_exposed_target": (
                target_maximum_absolute_difference
            ),
            "rms_absolute_mu_difference_from_exposed_target": (
                target_rms_absolute_difference
            ),
        },
        "locality_and_regulator_audit": {
            "zero_hopping_static_result": (
                "Because the spectral modes are onsite/internal, integrating their "
                "ground-state energy produces no spatial kernel. This is pointwise "
                "as a static spectral model, but its continuum is an infinite "
                "internal fiber rather than a demonstrated finite local 3+1 QFT."
            ),
            "nonzero_hopping_condition": (
                "For physical group velocity v_phys and variation length L, the "
                "local-density approximation requires v_phys/(y*|a|*L)<<1. It "
                "cannot hold uniformly as a->0 at fixed L."
            ),
            "time_dependence": (
                "The continuum reaches epsilon=0, so integrating it out gives "
                "temporal memory and no uniform adiabatic expansion. Static fields "
                "are derived; causal dynamics are not."
            ),
            "leading_temporal_obstruction": (
                "After subtracting its zero-frequency piece, the linearly coupled "
                "fermion produces a nonanalytic kernel proportional to |omega|. "
                "The bosonic a^2 seagulls cancel the static coefficient but not "
                "that retarded kernel."
            ),
            "finite_spacing": (
                "An infrared gap removes the |a|^3 nonanalyticity and makes the "
                "critically subtracted onset quartic. The continuum/thermodynamic "
                "limit must precede a->0."
            ),
            "uv_status": (
                "The analytic a^2 coefficient depends on the physical bandwidth "
                "and local counterterms. Its exact cancellation is a critical "
                "matching condition, not yet a protected prediction."
            ),
        },
        "quadratic_cancellation_options": {
            "single_bath_matching": (
                "Match the bare scalar or lapse-gradient stiffness to "
                "K2=g*rho1*Lambda*y^2/2."
            ),
            "finite_stable_field_sum_rule": sum_rule,
            "sum_rule_static_energy": (
                "U_mix=-I(m)+4*I(m/2)>0, U_mix'>0 and U_mix''>0 for m>0; "
                "U_mix=m^3/6+O(m^4/Lambda)."
            ),
            "boundary": (
                "The displayed boson/fermion sum cancels the one-loop uniform "
                "quadratic coefficient pointwise for an onsite static bath and "
                "leaves a positive convex microscopic energy with the desired "
                "cubic sign. No current symmetry protects its multiplicities and "
                "coupling ratio, and it does not cancel the temporal |omega| kernel."
            ),
        },
        "current_holo_embedding": {
            "available_slots": [
                "a certified scalar-matter interface",
                "a separate derivative-constitutive route left open by the route matrix",
                "a finite compact scalar spectrum and boundary actions",
            ],
            "missing": [
                "the internal rho(epsilon) proportional to epsilon continuum",
                "the Clifford Yukawa coupling to a spatial gradient or aether acceleration",
                "a protected quadratic matching or sum rule",
                "the complete lapse, shift, scalar and brane constraints",
                "time-dependent hyperbolicity, matter normalization and lensing",
            ],
            "status": "new explicit sector; not derived from the current 5D action",
        },
        "checks": checks,
        "physical_gates": physical_gates,
        "decision": {
            "verdict": (
                "SURVIVES_STATIC_SPECTRAL_GATE_BLOCKED_MICROSCOPIC_"
                "LOCAL_QFT_AND_HOLO"
            ),
            "chemical_bath_sign_obstruction_avoided": True,
            "uniform_static_spectral_candidate": True,
            "pointwise_onsite_hamiltonian_exhibited": True,
            "finite_local_qft_realization_exhibited": False,
            "deep_operator_candidate_survives_static_algebraic_gate": True,
            "exact_exposed_collector_interpolation_reproduced": False,
            "current_holo_mechanism": False,
            "physical_completion": False,
            "new_force_as_fundamental_physics": False,
            "lensing_derived": False,
            "publication_authorized": False,
            "next_action": (
                "Derive the internal pseudogap bath and its cancellation rule from "
                "a covariant 5D action, then perform the full constraint and "
                "time-dependent stability analysis before any force or lensing claim."
            ),
        },
        "evidence_boundary": (
            "This theory-only calculation constructs an explicit stable spectrum "
            "whose uniform static determinant has the AQUAL three-halves "
            "power, attractive variational sign, monotone interpolation and an "
            "acceleration scale fixed by microscopic parameters. An onsite internal "
            "fiber makes the formal static response pointwise, but is not yet a "
            "finite local 3+1 QFT. The critical matching "
            "is not protected, zero-gap time dependence is not local after the bath "
            "is integrated out, and the sector is absent from the current HOLO action. "
            "The exposed comparison target inherits a SPARC training fit even though "
            "this script reads no raw observation table, and the derived mu is not "
            "that exact interpolation. It is therefore a "
            "surviving static spectral candidate, not a completed microscopic HOLO "
            "mechanism, relativistic theory, detection, lensing result or publication."
        ),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    if result["checks"]["all"] is not True:
        raise RuntimeError("Dirac critical-bath algebra checks failed")
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(f"[verdict] {result['decision']['verdict']}")
    print("[scope] static spectral candidate; local-QFT and HOLO gates remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
