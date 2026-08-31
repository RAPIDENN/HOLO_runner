#!/usr/bin/env python3
"""Derive a local 4+1 dimensional z=2 Clifford-bath completion gate.

The previous covariant-origin audit used a three-spatial-dimensional
``z=3/2`` scaling witness.  Its density of states had the desired linear
power, but the fractional boundary symbol was not derived from the same local
five-dimensional action and its three acceleration components did not match
the four spatial components of the bulk khronon.

There is a more direct local construction.  On a 4+1 foliation, let a
four-component complex fermion have the Hermitian one-particle Hamiltonian

    H = c (-D_perp^2) Gamma_0 + y a_A Gamma_A,       A=1,...,4,

where the five Hermitian matrices form Cl(5).  The action is first order in
preferred time and second order in the four spatial directions.  It is local,
has ``z=2`` scaling, and can be written covariantly using the unit khronon
``U_M`` and its spatial projector.  In a uniform flat patch,

    E_+/- = +/-sqrt(c^2 |p|^4 + y^2 |a|^2),
    rho_-(epsilon) = N_- epsilon / (16 pi^2 c^2).

Thus a literal bulk single-particle density of states, the Clifford square
root, the filled-sea sign, and the nonanalytic ``-|a|^3`` term all follow from
a local 5D quadratic action.  The complete finite-scale bracket can also be
made UV finite without a hard momentum cutoff.  Per filled negative fermion
branch, add two stable real ``z=2`` scalars with
``omega_b^2=c^2 p^4+Lambda^2+y^2 a^2``.  Their combined zero-point determinant
has the opposite functional sign and gives

    [(Lambda^2+y^2 a^2)^(3/2)-Lambda^3]/3,

while the light filled fermion gives ``-y^3|a|^3/3``.  The leading UV terms
cancel inside the joint integrand.  This is an explicit free-field material,
not a protected supersymmetric identity; the field multiplicity and portals
remain frozen microscopic choices.

The light fermion also gives an analytic full-frequency particle-hole kernel
in a separately frozen symmetric finite band.  Its positive spectral measure
resolves the branch cut and proves that the critical *linearized
flat-background scalar sector* has no upper-half-plane poles when the khronon
kinetic residue and spatial stabilizer are nonnegative.

Two boundaries remain explicit.  The stable scalars above have an ``a^2 phi^2``
portal and therefore supply only a seagull, not a compensating branch cut, at
quadratic order about ``a=0``.  The same-action continuum response crosses
zero and produces an explicit upper-half-plane Schur pole: that minimal
material is killed as a global retarded UV completion and is at most an EFT
below its matter scale.  More importantly, a finite compact fifth direction becomes
three-dimensional below its first KK gap:
``rho ~ epsilon^(1/2)`` and the strict-IR nonanalyticity becomes ``|a|^(5/2)``.
The cubic survives asymptotically only with a gapless radial continuum, whose
simultaneous localization of four-dimensional gravity has not been derived in
the current HOLO geometry.  This gate therefore closes the local microscopic
and flat linear-causal steps without promoting a compactified HOLO force,
lensing prediction, nonlinear stability theorem, or publication claim.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

if __package__:
    from . import derive_dirac_critical_bath_gate as static_bath
    from . import derive_khronon_constraint_stability_gate as khronon
else:
    import derive_dirac_critical_bath_gate as static_bath
    import derive_khronon_constraint_stability_gate as khronon


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STATIC_GATE = HERE / "artifacts" / "dirac_critical_bath_gate.json"
ORIGIN_GATE = HERE / "artifacts" / "covariant_5d_pseudogap_gate.json"
KHRONON_GATE = HERE / "artifacts" / "khronon_constraint_stability_gate.json"
OUTPUT = HERE / "artifacts" / "bulk_z2_clifford_completion_gate.json"

SCHEMA = "holo.bulk-z2-clifford-completion-gate.v1"


class BulkZ2InputError(ValueError):
    """A proposed microscopic parameter or input certificate is malformed."""


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BulkZ2InputError(f"cannot read {path}: {exc}") from exc
    if type(value) is not dict:
        raise BulkZ2InputError(f"{path}: expected a JSON object")
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
        raise BulkZ2InputError(f"{name} must be positive and finite")
    return result


def _nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise BulkZ2InputError(f"{name} must be nonnegative and finite")
    return result


def _positive_integer(value: int, name: str) -> int:
    if type(value) is not int or value <= 0:
        raise BulkZ2InputError(f"{name} must be a positive integer")
    return value


def bulk_z2_dos_slope(
    dispersion_coefficient: float,
    *,
    flavor_count: int = 1,
    negative_branches_per_flavor: int = 2,
) -> float:
    """Return ``rho_-(epsilon)/epsilon`` per unit four-volume.

    For ``epsilon=c |p|^2`` in four spatial dimensions, one branch has

    ``rho(epsilon)=epsilon/(16*pi^2*c^2)``.

    A four-component Cl(5) multiplet has two filled negative branches.
    """

    coefficient = _positive(dispersion_coefficient, "dispersion_coefficient")
    flavors = _positive_integer(flavor_count, "flavor_count")
    branches = _positive_integer(
        negative_branches_per_flavor, "negative_branches_per_flavor"
    )
    return flavors * branches / (16.0 * math.pi**2 * coefficient**2)


def bulk_z2_clifford_spectrum(
    momentum: Sequence[float],
    acceleration: Sequence[float],
    *,
    dispersion_coefficient: float = 1.0,
    yukawa: float = 1.0,
) -> np.ndarray:
    """Diagonalize the local four-space ``z=2`` Clifford Hamiltonian."""

    vector_p = np.asarray(momentum, dtype=float)
    vector_a = np.asarray(acceleration, dtype=float)
    if vector_p.shape != (4,) or vector_a.shape != (4,):
        raise BulkZ2InputError("momentum and acceleration must be 4-vectors")
    if np.any(~np.isfinite(vector_p)) or np.any(~np.isfinite(vector_a)):
        raise BulkZ2InputError("momentum and acceleration must be finite")
    coefficient = _positive(dispersion_coefficient, "dispersion_coefficient")
    coupling = _positive(yukawa, "yukawa")
    gamma = static_bath.clifford_five()
    hamiltonian = coefficient * float(vector_p @ vector_p) * gamma[0]
    for index, component in enumerate(vector_a):
        hamiltonian = hamiltonian + coupling * component * gamma[index + 1]
    return np.linalg.eigvalsh(hamiltonian)


def sea_quadratic_increment(
    cutoff: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    """Matter coefficient ``K2`` multiplying ``a^2`` in the sea action.

    This is not yet the dimensionless coefficient inside the gravitational
    bracket.  For

    ``S_grav=(M5^3/2) int N sqrt(h) eta*a^2``

    the corresponding increment is ``Delta_eta=2*K2/M5^3``.
    """

    band = _positive(cutoff, "cutoff")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    return 0.5 * slope * band * coupling**2


def gravitational_eta_increment(
    matter_quadratic_coefficient: float,
    *,
    planck5_cubed: float,
) -> float:
    """Convert an external matter ``a^2`` coefficient into gravitational units."""

    coefficient = _nonnegative(
        matter_quadratic_coefficient, "matter_quadratic_coefficient"
    )
    gravitational_scale = _positive(planck5_cubed, "planck5_cubed")
    return 2.0 * coefficient / gravitational_scale


def local_gaussian_completion_integrand(
    energy: float,
    gap: float,
    regulator_mass: float,
) -> float:
    r"""UV-finite joint determinant integrand per negative branch.

    It is

    ``e[(sqrt(e^2+m^2)-e)
        -(sqrt(e^2+Lambda^2+m^2)-sqrt(e^2+Lambda^2))]``.

    The second bracket is the combined ``-1/2-1/2`` zero-point weight of two
    real stable scalars.  The rationalized form avoids cancellation at large
    energy.
    """

    epsilon = _nonnegative(energy, "energy")
    mass = _nonnegative(gap, "gap")
    scale = _positive(regulator_mass, "regulator_mass")
    if epsilon == 0.0 or mass == 0.0:
        return 0.0
    root_m = math.hypot(epsilon, mass)
    root_l = math.hypot(epsilon, scale)
    root_lm = math.sqrt(epsilon * epsilon + scale * scale + mass * mass)
    denominator_light = root_m + epsilon
    denominator_heavy = root_lm + root_l
    denominator_difference = (
        scale * scale * (1.0 / (root_lm + root_m) + 1.0 / (root_l + epsilon))
    )
    result = (
        epsilon
        * mass
        * mass
        * denominator_difference
        / (denominator_light * denominator_heavy)
    )
    if not math.isfinite(result) or result < 0.0:
        raise BulkZ2InputError("local completion integrand lost positivity")
    return result


def local_gaussian_completion_lagrangian(
    acceleration: float,
    *,
    regulator_mass: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    """Exact joint light-fermion plus massive-boson static determinant."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(regulator_mass, "regulator_mass")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    mass = coupling * magnitude
    result = slope / 3.0 * ((scale * scale + mass * mass) ** 1.5 - scale**3 - mass**3)
    if not math.isfinite(result) or result < 0.0:
        raise BulkZ2InputError("local Gaussian completion is outside binary64 range")
    return result


def numerical_local_gaussian_completion(
    acceleration: float,
    *,
    regulator_mass: float,
    yukawa: float,
    rho_slope: float,
    quadrature_order: int = 512,
) -> float:
    """Independently integrate the UV-finite completion over ``[0,infinity)``."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(regulator_mass, "regulator_mass")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    nodes, weights = _gauss_legendre(quadrature_order)
    unit = 0.5 * (nodes + 1.0)
    energy_scale = max(scale, coupling * magnitude, np.finfo(float).tiny)
    energies = energy_scale * unit / (1.0 - unit)
    jacobian = energy_scale / (1.0 - unit) ** 2
    values = np.asarray(
        [
            local_gaussian_completion_integrand(
                float(energy), coupling * magnitude, scale
            )
            for energy in energies
        ]
    )
    result = slope * 0.5 * float(np.sum(weights * jacobian * values))
    if not math.isfinite(result) or result < 0.0:
        raise BulkZ2InputError("completion quadrature lost positivity")
    return result


def compactified_ir_exponents(
    noncompact_spatial_dimensions: int,
    dynamical_exponent: float,
) -> dict[str, float]:
    """DOS and filled-sea nonanalytic powers after a finite KK reduction."""

    dimensions = _positive_integer(
        noncompact_spatial_dimensions, "noncompact_spatial_dimensions"
    )
    exponent_z = _positive(dynamical_exponent, "dynamical_exponent")
    dos_power = dimensions / exponent_z - 1.0
    return {
        "density_of_states_power": dos_power,
        "filled_sea_nonanalytic_power": dos_power + 2.0,
    }


def orthogonal_gapped_static_expansion(
    background_acceleration: float,
    *,
    regulator_mass: float,
    yukawa: float,
    rho_slope: float,
) -> dict[str, float]:
    r"""Expand the exact static bath in a perturbation orthogonal to ``a_bar``.

    If ``|a_bar|>0`` and ``a=a_bar+b`` with ``a_bar dot b=0``, the Clifford
    gap is ``sqrt(m0^2+y^2|b|^2)``.  The expansion is analytic in ``|b|^2``;
    in particular its cubic coefficient is exactly zero.  This is the local
    obstruction on the original ``T=t`` Lifshitz background.
    """

    background = _positive(background_acceleration, "background_acceleration")
    scale = _positive(regulator_mass, "regulator_mass")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    gap = coupling * background
    upper = math.hypot(scale, gap)
    return {
        "background_gap": gap,
        "quadratic_coefficient": 0.5 * slope * coupling**2 * (upper - gap),
        "cubic_coefficient": 0.0,
        "quartic_coefficient": 0.125 * slope * coupling**4 * (1.0 / upper - 1.0 / gap),
    }


def _momentum_shift(momentum: float, dispersion_coefficient: float) -> float:
    q = _nonnegative(momentum, "momentum")
    coefficient = _positive(dispersion_coefficient, "dispersion_coefficient")
    return 0.25 * coefficient * q * q


def polarization_euclidean(
    frequency: float,
    momentum: float,
    *,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    r"""Exact Euclidean acceleration polarization ``Pi_E(Omega,q)``.

    The quadratic effective Lagrangian is ``a_i Pi_E a_i / 2`` and

    ``Pi_E = y^2 int_0^Lambda d e rho1*e
                 4(e+s)/(Omega^2+4(e+s)^2)``,

    with ``s=c q^2/4``.  The symmetric loop routing makes the particle-hole
    threshold ``nu_min=2s``.  This is the fixed regulator used by this gate.
    """

    omega = _nonnegative(frequency, "frequency")
    band = _positive(cutoff, "cutoff")
    coefficient = _positive(dispersion_coefficient, "dispersion_coefficient")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    shift = _momentum_shift(momentum, coefficient)
    if omega == 0.0:
        integral = band if shift == 0.0 else band - shift * math.log1p(band / shift)
    else:
        lower = shift
        upper = shift + band
        angle = math.atan2(2.0 * upper, omega) - math.atan2(2.0 * lower, omega)
        logarithm = math.log(
            (omega * omega + 4.0 * upper * upper)
            / (omega * omega + 4.0 * lower * lower)
        )
        integral = band - 0.5 * omega * angle - 0.5 * shift * logarithm
    result = coupling * coupling * slope * integral
    if not math.isfinite(result) or result < 0.0:
        raise BulkZ2InputError("Euclidean polarization lost positivity")
    return result


@functools.lru_cache(maxsize=8)
def _gauss_legendre(order: int) -> tuple[np.ndarray, np.ndarray]:
    if type(order) is not int or order < 16:
        raise BulkZ2InputError("quadrature order must be an integer >= 16")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return nodes, weights


def polarization_complex(
    frequency: complex,
    momentum: float,
    *,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
    quadrature_order: int = 256,
) -> complex:
    r"""Evaluate analytic ``Pi(z,q)`` away from its real-axis branch cut.

    ``Pi(z,q)=y^2 int rho1*e 4(e+s)/[4(e+s)^2-z^2] de``.
    """

    z = complex(frequency)
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise BulkZ2InputError("frequency must be finite")
    band = _positive(cutoff, "cutoff")
    coefficient = _positive(dispersion_coefficient, "dispersion_coefficient")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    shift = _momentum_shift(momentum, coefficient)
    nodes, weights = _gauss_legendre(quadrature_order)
    energies = 0.5 * band * (nodes + 1.0)
    gaps = 2.0 * (energies + shift)
    values = slope * energies * (2.0 * gaps) / (gaps * gaps - z * z)
    result = coupling * coupling * 0.5 * band * np.sum(weights * values)
    answer = complex(result)
    if not (math.isfinite(answer.real) and math.isfinite(answer.imag)):
        raise BulkZ2InputError("complex polarization is outside binary64 range")
    return answer


def particle_hole_cut(
    momentum: float,
    *,
    cutoff: float,
    dispersion_coefficient: float,
) -> tuple[float, float]:
    """Positive-frequency endpoints of the regulated particle-hole cut."""

    shift = _momentum_shift(momentum, dispersion_coefficient)
    band = _positive(cutoff, "cutoff")
    return 2.0 * shift, 2.0 * (shift + band)


def polarization_spectral_weight(
    frequency: float,
    momentum: float,
    *,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    r"""Return positive ``sigma`` with ``Im Pi_R(omega)=pi*sigma``.

    The spectral representation is

    ``Pi(z,q)=int_cut dnu 2 nu sigma(nu,q)/(nu^2-z^2)``.
    """

    omega = _nonnegative(frequency, "frequency")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    lower, upper = particle_hole_cut(
        momentum,
        cutoff=cutoff,
        dispersion_coefficient=dispersion_coefficient,
    )
    if not lower < omega < upper:
        return 0.0
    return 0.25 * coupling * coupling * slope * (omega - lower)


def polarization_retarded_real(
    frequency: float,
    momentum: float,
    *,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
) -> complex:
    """Boundary value of the exact retarded polarization for real frequency.

    Values exactly at a hard-cutoff endpoint are rejected because the real
    part has a regulator-edge logarithm there.
    """

    omega = float(frequency)
    if not math.isfinite(omega):
        raise BulkZ2InputError("frequency must be finite")
    if omega == 0.0:
        return complex(
            polarization_euclidean(
                0.0,
                momentum,
                cutoff=cutoff,
                dispersion_coefficient=dispersion_coefficient,
                yukawa=yukawa,
                rho_slope=rho_slope,
            )
        )
    band = _positive(cutoff, "cutoff")
    coefficient = _positive(dispersion_coefficient, "dispersion_coefficient")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    shift = _momentum_shift(momentum, coefficient)
    absolute = abs(omega)
    lower, upper = particle_hole_cut(
        momentum, cutoff=band, dispersion_coefficient=coefficient
    )
    tolerance = 32.0 * np.finfo(float).eps * max(1.0, upper)
    if abs(absolute - lower) <= tolerance or abs(absolute - upper) <= tolerance:
        raise BulkZ2InputError("frequency lies on a hard-cutoff branch endpoint")
    u0 = shift
    u1 = shift + band

    def _logabs(value: float) -> float:
        return math.log(abs(value))

    primitive_difference = band + absolute / 4.0 * (
        _logabs(2.0 * u1 - absolute)
        - _logabs(2.0 * u1 + absolute)
        - _logabs(2.0 * u0 - absolute)
        + _logabs(2.0 * u0 + absolute)
    )
    if shift > 0.0:
        primitive_difference -= (
            0.5
            * shift
            * (
                _logabs(4.0 * u1 * u1 - absolute * absolute)
                - _logabs(4.0 * u0 * u0 - absolute * absolute)
            )
        )
    real = coupling * coupling * slope * primitive_difference
    sigma = polarization_spectral_weight(
        absolute,
        momentum,
        cutoff=band,
        dispersion_coefficient=coefficient,
        yukawa=coupling,
        rho_slope=slope,
    )
    imaginary = math.copysign(math.pi * sigma, omega)
    return complex(real, imaginary)


def critical_eta_infinity(
    pi_zero: float,
    *,
    eta_critical: float,
    planck5_cubed: float,
) -> float:
    r"""Bare ``eta`` required by the correctly normalized critical matching.

    ``Pi`` is the Hessian in ``S_matter^(2)=a Pi a/2``.  Factoring the
    gravitational normalization ``M5^3/2`` therefore gives

    ``eta_infinity=eta_c-Pi(0,0)/M5^3``.
    """

    static_hessian = _nonnegative(pi_zero, "pi_zero")
    eta_c = _positive(eta_critical, "eta_critical")
    gravitational_scale = _positive(planck5_cubed, "planck5_cubed")
    eta_inf = eta_c - static_hessian / gravitational_scale
    if eta_inf <= 0.0:
        raise BulkZ2InputError(
            "critical matching requires a positive bare lapse coefficient"
        )
    return eta_inf


def geometric_schur_response(
    pi_value: complex,
    *,
    pi_zero: float,
    eta_critical: float,
    planck5_cubed: float,
    schur_factor: float,
) -> complex:
    r"""Exact lapse/metric Schur response for an arbitrary bath Hessian.

    With ``A_g/eta_c=schur_factor`` and
    ``C=eta_infinity+Pi/M5^3``, elimination of the lapse gives

    ``H=A_g*(eta_c/C-1)``.

    Expanding this expression to first order in ``Pi(0)-Pi`` recovers the
    earlier linear response, but the reciprocal is retained here exactly.
    """

    value = complex(pi_value)
    if not (math.isfinite(value.real) and math.isfinite(value.imag)):
        raise BulkZ2InputError("pi_value must be finite")
    static_hessian = _nonnegative(pi_zero, "pi_zero")
    eta_c = _positive(eta_critical, "eta_critical")
    gravitational_scale = _positive(planck5_cubed, "planck5_cubed")
    geometric_ratio = _positive(schur_factor, "schur_factor")
    eta_inf = critical_eta_infinity(
        static_hessian,
        eta_critical=eta_c,
        planck5_cubed=gravitational_scale,
    )
    lapse_coefficient = eta_inf + value / gravitational_scale
    if abs(lapse_coefficient) <= 64.0 * np.finfo(float).tiny:
        raise BulkZ2InputError("exact Schur denominator vanished")
    a_g = geometric_ratio * eta_c
    result = a_g * (eta_c / lapse_coefficient - 1.0)
    if not (math.isfinite(result.real) and math.isfinite(result.imag)):
        raise BulkZ2InputError("exact Schur response is outside binary64 range")
    return result


def geometric_schur_euclidean_response(
    frequency: float,
    momentum: float,
    *,
    eta_critical: float,
    planck5_cubed: float,
    schur_factor: float,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    """Exact positive Euclidean Schur response of the finite-band bath."""

    pi_zero = polarization_euclidean(
        0.0,
        0.0,
        cutoff=cutoff,
        dispersion_coefficient=dispersion_coefficient,
        yukawa=yukawa,
        rho_slope=rho_slope,
    )
    pi_value = polarization_euclidean(
        frequency,
        momentum,
        cutoff=cutoff,
        dispersion_coefficient=dispersion_coefficient,
        yukawa=yukawa,
        rho_slope=rho_slope,
    )
    response = geometric_schur_response(
        pi_value,
        pi_zero=pi_zero,
        eta_critical=eta_critical,
        planck5_cubed=planck5_cubed,
        schur_factor=schur_factor,
    )
    if abs(response.imag) > 2.0e-14 * max(1.0, abs(response.real)):
        raise BulkZ2InputError("Euclidean Schur response acquired an imaginary part")
    if response.real < -1.0e-13:
        raise BulkZ2InputError("Euclidean Schur response lost positivity")
    return max(0.0, response.real)


def geometric_schur_retarded_response(
    frequency: complex,
    momentum: float,
    *,
    eta_critical: float,
    planck5_cubed: float,
    schur_factor: float,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
    quadrature_order: int = 256,
) -> complex:
    """Exact analytic Schur response above the retarded branch cut."""

    pi_zero = polarization_euclidean(
        0.0,
        0.0,
        cutoff=cutoff,
        dispersion_coefficient=dispersion_coefficient,
        yukawa=yukawa,
        rho_slope=rho_slope,
    )
    pi_value = polarization_complex(
        frequency,
        momentum,
        cutoff=cutoff,
        dispersion_coefficient=dispersion_coefficient,
        yukawa=yukawa,
        rho_slope=rho_slope,
        quadrature_order=quadrature_order,
    )
    return geometric_schur_response(
        pi_value,
        pi_zero=pi_zero,
        eta_critical=eta_critical,
        planck5_cubed=planck5_cubed,
        schur_factor=schur_factor,
    )


def matched_euclidean_inverse(
    frequency: float,
    momentum: float,
    *,
    q_zeta: float,
    k4_coefficient: float,
    eta_critical: float,
    planck5_cubed: float,
    schur_factor: float,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    """Critical scalar inverse kernel with the exact lapse Schur complement."""

    omega = _nonnegative(frequency, "frequency")
    q = _nonnegative(momentum, "momentum")
    kinetic = _positive(q_zeta, "q_zeta")
    stabilizer = _nonnegative(k4_coefficient, "k4_coefficient")
    response = geometric_schur_euclidean_response(
        omega,
        q,
        eta_critical=eta_critical,
        planck5_cubed=planck5_cubed,
        schur_factor=schur_factor,
        cutoff=cutoff,
        dispersion_coefficient=dispersion_coefficient,
        yukawa=yukawa,
        rho_slope=rho_slope,
    )
    result = kinetic * omega * omega + stabilizer * q**4 + q * q * response
    if not math.isfinite(result) or result < -1.0e-13:
        raise BulkZ2InputError("matched Euclidean inverse lost positivity")
    return max(0.0, result)


def matched_retarded_inverse_complex(
    frequency: complex,
    momentum: float,
    *,
    q_zeta: float,
    k4_coefficient: float,
    eta_critical: float,
    planck5_cubed: float,
    schur_factor: float,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
    quadrature_order: int = 256,
) -> complex:
    """Analytic critical inverse kernel in the upper frequency half-plane."""

    z = complex(frequency)
    q = _nonnegative(momentum, "momentum")
    kinetic = _positive(q_zeta, "q_zeta")
    stabilizer = _nonnegative(k4_coefficient, "k4_coefficient")
    response = geometric_schur_retarded_response(
        z,
        q,
        eta_critical=eta_critical,
        planck5_cubed=planck5_cubed,
        schur_factor=schur_factor,
        cutoff=cutoff,
        dispersion_coefficient=dispersion_coefficient,
        yukawa=yukawa,
        rho_slope=rho_slope,
        quadrature_order=quadrature_order,
    )
    return -kinetic * z * z + stabilizer * q**4 + q * q * response


def matched_laplace_inverse(
    laplace_frequency: complex,
    momentum: float,
    *,
    q_zeta: float,
    k4_coefficient: float,
    eta_critical: float,
    planck5_cubed: float,
    schur_factor: float,
    cutoff: float,
    dispersion_coefficient: float,
    yukawa: float,
    rho_slope: float,
    quadrature_order: int = 256,
) -> complex:
    """Return ``D(p,q)`` for ``p=-i omega`` in the right half-plane."""

    p = complex(laplace_frequency)
    if not (math.isfinite(p.real) and math.isfinite(p.imag)) or p.real <= 0.0:
        raise BulkZ2InputError("laplace_frequency must have finite positive real part")
    return matched_retarded_inverse_complex(
        1j * p,
        momentum,
        q_zeta=q_zeta,
        k4_coefficient=k4_coefficient,
        eta_critical=eta_critical,
        planck5_cubed=planck5_cubed,
        schur_factor=schur_factor,
        cutoff=cutoff,
        dispersion_coefficient=dispersion_coefficient,
        yukawa=yukawa,
        rho_slope=rho_slope,
        quadrature_order=quadrature_order,
    )


def positive_real_stability_margin(
    laplace_frequency: complex,
    momentum: float,
    **kwargs: Any,
) -> float:
    r"""Evaluate the exact positive-real no-UHP diagnostic ``Re[D(p,q)/p]``.

    Positivity is analytic, not inferred from this sample: ``C(p^2,q)`` is a
    positive Stieltjes function, so its reciprocal and the subtracted exact
    Schur response are complete-Bernstein.  Consequently every term in
    ``D/p`` has positive real part for ``Re(p)>0`` when ``Q_zeta>0`` and
    ``B4>=0``.  This routine supplies a numerical regression of that theorem.
    """

    p = complex(laplace_frequency)
    inverse = matched_laplace_inverse(p, momentum, **kwargs)
    margin = float((inverse / p).real)
    if not math.isfinite(margin):
        raise BulkZ2InputError("positive-real stability margin is not finite")
    return margin


def same_action_continuum_polarization_euclidean(
    frequency: float,
    *,
    regulator_mass: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    r"""Renormalized ``q=0`` Hessian of the static Gaussian multiplet.

    With an intermediate energy cutoff ``R``, the light fermion contributes

    ``gamma[R-|Omega| atan(2R/|Omega|)/2]``.

    The two stable scalars have the quadratic portal ``a^2 phi^2`` and hence
    contribute only the seagull
    ``-gamma[sqrt(R^2+Lambda^2)-Lambda]`` around ``a=0``.  Removing ``R`` gives

    ``Pi_same,E=gamma[Lambda-pi|Omega|/4]``.

    It reproduces the UV-finite static Hessian but is not positive at all
    frequencies, so it cannot replace the separately declared finite band.
    """

    omega = _nonnegative(frequency, "frequency")
    scale = _positive(regulator_mass, "regulator_mass")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    gamma = slope * coupling**2
    return gamma * (scale - 0.25 * math.pi * omega)


def same_action_continuum_polarization_retarded(
    frequency: complex,
    *,
    regulator_mass: float,
    yukawa: float,
    rho_slope: float,
) -> complex:
    """Analytic upper-half-plane continuation of the renormalized ``q=0`` Hessian."""

    z = complex(frequency)
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise BulkZ2InputError("frequency must be finite")
    scale = _positive(regulator_mass, "regulator_mass")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    gamma = slope * coupling**2
    return gamma * (scale + 0.25j * math.pi * z)


def same_action_continuum_lapse_coefficient_laplace(
    laplace_frequency: float,
    *,
    eta_critical: float,
    planck5_cubed: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    r"""Critical lapse coefficient ``C(ip)=eta_c-kappa*p``.

    The static matching has already used
    ``eta_infinity+rho1*y^2*Lambda/M5^3=eta_c``; consequently ``Lambda`` drops
    out of the frequency-dependent critical coefficient.
    """

    p = _nonnegative(laplace_frequency, "laplace_frequency")
    eta_c = _positive(eta_critical, "eta_critical")
    gravitational_scale = _positive(planck5_cubed, "planck5_cubed")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    kappa = math.pi * slope * coupling**2 / (4.0 * gravitational_scale)
    return eta_c - kappa * p


def same_action_continuum_uhp_pole_b4_zero(
    momentum: float,
    *,
    q_zeta: float,
    eta_critical: float,
    planck5_cubed: float,
    schur_factor: float,
    yukawa: float,
    rho_slope: float,
) -> dict[str, float]:
    r"""Closed UHP pole witness for the unbounded same-action multiplet.

    For ``B4=0``, the exact Schur inverse in Laplace frequency is

    ``D=Q p^2+q^2 A_g*kappa*p/(eta_c-kappa*p)``.

    Its positive root lies above the zero of the lapse coefficient for every
    ``q>0``.  A finite nonnegative ``B4`` does not remove the obstruction:
    immediately above that zero ``D`` tends to minus infinity, while
    ``D`` tends to plus infinity as ``p`` tends to infinity.
    """

    q = _positive(momentum, "momentum")
    kinetic = _positive(q_zeta, "q_zeta")
    eta_c = _positive(eta_critical, "eta_critical")
    gravitational_scale = _positive(planck5_cubed, "planck5_cubed")
    geometric_ratio = _positive(schur_factor, "schur_factor")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    kappa = math.pi * slope * coupling**2 / (4.0 * gravitational_scale)
    a_g = geometric_ratio * eta_c
    crossing = eta_c / kappa
    discriminant = (kinetic * eta_c) ** 2 + (
        4.0 * kinetic * a_g * kappa * kappa * q * q
    )
    pole = (kinetic * eta_c + math.sqrt(discriminant)) / (2.0 * kinetic * kappa)
    lapse_at_pole = eta_c - kappa * pole
    schur = a_g * kappa * pole / lapse_at_pole
    inverse = kinetic * pole * pole + q * q * schur
    inverse_scale = kinetic * pole * pole + abs(q * q * schur)
    return {
        "kappa": kappa,
        "lapse_zero": crossing,
        "positive_UHP_laplace_pole": pole,
        "pole_minus_lapse_zero": pole - crossing,
        "inverse_residual": inverse,
        "normalized_inverse_residual": abs(inverse) / inverse_scale,
    }


def _source_receipts() -> dict[str, dict[str, str]]:
    paths = {
        "dirac_static_gate": STATIC_GATE,
        "covariant_5D_origin_gate": ORIGIN_GATE,
        "khronon_constraint_gate": KHRONON_GATE,
    }
    return {
        name: {"path": str(path.relative_to(REPO)), "sha256": _sha256(path)}
        for name, path in paths.items()
    }


def build() -> dict[str, Any]:
    static = _read(STATIC_GATE)
    origin = _read(ORIGIN_GATE)
    geometry = _read(KHRONON_GATE)
    if static.get("schema") != "holo.dirac-critical-bath-gate.v1":
        raise BulkZ2InputError("unexpected static bath schema")
    if origin.get("schema") != "holo.covariant-5d-pseudogap-gate.v1":
        raise BulkZ2InputError("unexpected covariant-origin schema")
    if geometry.get("schema") != "holo.khronon-constraint-stability-gate.v1":
        raise BulkZ2InputError("unexpected khronon gate schema")
    if not all(
        item.get("checks", {}).get("all") is True for item in (static, origin, geometry)
    ):
        raise BulkZ2InputError("an upstream gate is not certified")

    spatial_dimensions = 4
    z = 2.0
    coefficient = 0.8
    coupling = 1.1
    flavors = 2
    branches_per_flavor = 2
    negative_branches = flavors * branches_per_flavor
    regulator_mass = 1.7
    planck5_cubed = 1.0
    # The finite-band kernel uses the same numerical scale only as a frozen
    # low-energy diagnostic; the static determinant below is UV finite and
    # does not use a hard momentum cutoff.
    cutoff = regulator_mass
    rho_slope = bulk_z2_dos_slope(
        coefficient,
        flavor_count=flavors,
        negative_branches_per_flavor=branches_per_flavor,
    )
    expected_rho_slope = negative_branches / (16.0 * math.pi**2 * coefficient**2)

    momenta = np.geomspace(1.0e-7, 1.0e3, 200)
    energies = coefficient * momenta**2
    densities = rho_slope * energies
    dos_power = float(np.polyfit(np.log(energies), np.log(densities), 1)[0])

    momentum = np.asarray([0.31, -0.27, 0.18, 0.23])
    acceleration = np.asarray([0.19, -0.23, 0.41, -0.11])
    spectrum = bulk_z2_clifford_spectrum(
        momentum,
        acceleration,
        dispersion_coefficient=coefficient,
        yukawa=coupling,
    )
    expected_energy = math.hypot(
        coefficient * float(momentum @ momentum),
        coupling * float(np.linalg.norm(acceleration)),
    )
    expected_spectrum = np.asarray(
        [-expected_energy, -expected_energy, expected_energy, expected_energy]
    )
    spectrum_error = float(np.max(np.abs(spectrum - expected_spectrum)))

    acceleration_magnitude = float(np.linalg.norm(acceleration))
    sea_closed = local_gaussian_completion_lagrangian(
        acceleration_magnitude,
        regulator_mass=regulator_mass,
        yukawa=coupling,
        rho_slope=rho_slope,
    )
    sea_numeric = numerical_local_gaussian_completion(
        acceleration_magnitude,
        regulator_mass=regulator_mass,
        yukawa=coupling,
        rho_slope=rho_slope,
        quadrature_order=768,
    )
    sea_relative_error = abs(sea_numeric / sea_closed - 1.0)
    matter_quadratic_coefficient = sea_quadratic_increment(cutoff, coupling, rho_slope)
    delta_eta = gravitational_eta_increment(
        matter_quadratic_coefficient,
        planck5_cubed=planck5_cubed,
    )
    eta_c = khronon.geometric_critical_eta(spatial_dimensions, 1.0)
    eta_inf = eta_c - delta_eta
    if eta_inf <= 0.0:
        raise RuntimeError("diagnostic sea overwhelms the positive baseline")
    a0 = cutoff / coupling
    x_values = np.geomspace(1.0e-10, 1.0e10, 401)
    mu_error = float(
        np.max(
            np.abs(
                np.asarray([khronon.geometric_mu(x * a0, a0=a0) for x in x_values])
                - np.asarray([static_bath.matched_mu(float(x)) for x in x_values])
            )
        )
    )

    analytic_numeric_errors = []
    for omega in (0.0, 0.03, 0.2, 1.1, 4.0):
        for q in (0.0, 0.17, 0.8, 2.0):
            analytic = polarization_euclidean(
                omega,
                q,
                cutoff=cutoff,
                dispersion_coefficient=coefficient,
                yukawa=coupling,
                rho_slope=rho_slope,
            )
            numerical = polarization_complex(
                1j * omega,
                q,
                cutoff=cutoff,
                dispersion_coefficient=coefficient,
                yukawa=coupling,
                rho_slope=rho_slope,
                quadrature_order=512,
            ).real
            analytic_numeric_errors.append(abs(analytic - numerical))
    maximum_euclidean_error = max(analytic_numeric_errors)

    pi_zero = polarization_euclidean(
        0.0,
        0.0,
        cutoff=cutoff,
        dispersion_coefficient=coefficient,
        yukawa=coupling,
        rho_slope=rho_slope,
    )
    eta_inf_from_hessian = critical_eta_infinity(
        pi_zero,
        eta_critical=eta_c,
        planck5_cubed=planck5_cubed,
    )
    low_frequencies = np.geomspace(1.0e-10, 1.0e-6, 48) * cutoff
    ohmic_values = np.asarray(
        [
            0.5
            * (
                pi_zero
                - polarization_euclidean(
                    value,
                    0.0,
                    cutoff=cutoff,
                    dispersion_coefficient=coefficient,
                    yukawa=coupling,
                    rho_slope=rho_slope,
                )
            )
            / value
            for value in low_frequencies
        ]
    )
    ohmic_numeric = float(np.median(ohmic_values))
    ohmic_expected = math.pi * coupling**2 * rho_slope / 8.0

    spectral_samples = []
    for q in (0.0, 0.3, 1.0):
        cut = particle_hole_cut(q, cutoff=cutoff, dispersion_coefficient=coefficient)
        for fraction in (0.1, 0.5, 0.9):
            omega = cut[0] + fraction * (cut[1] - cut[0])
            retarded = polarization_retarded_real(
                omega,
                q,
                cutoff=cutoff,
                dispersion_coefficient=coefficient,
                yukawa=coupling,
                rho_slope=rho_slope,
            )
            sigma = polarization_spectral_weight(
                omega,
                q,
                cutoff=cutoff,
                dispersion_coefficient=coefficient,
                yukawa=coupling,
                rho_slope=rho_slope,
            )
            spectral_samples.append((retarded.imag, math.pi * sigma))
    maximum_spectral_error = max(
        abs(imaginary - expected) for imaginary, expected in spectral_samples
    )

    positive_real_margins = []
    q_zeta = khronon.scalar_kinetic_coefficient(4, 1.2)
    schur_factor = 4.0
    k4_coefficient = 0.8
    for p_value in (
        0.11 + 0.17j,
        0.27 - 0.43j,
        0.08 + 1.2j,
        1.3 - 2.4j,
    ):
        for q in (0.07, 0.31, 1.1):
            positive_real_margins.append(
                positive_real_stability_margin(
                    p_value,
                    q,
                    q_zeta=q_zeta,
                    k4_coefficient=k4_coefficient,
                    eta_critical=eta_c,
                    planck5_cubed=planck5_cubed,
                    schur_factor=schur_factor,
                    cutoff=cutoff,
                    dispersion_coefficient=coefficient,
                    yukawa=coupling,
                    rho_slope=rho_slope,
                    quadrature_order=512,
                )
            )
    minimum_positive_real_margin = min(positive_real_margins)

    retarded_passivity_samples = []
    for q in (0.0, 0.3, 1.0):
        lower, upper = particle_hole_cut(
            q, cutoff=cutoff, dispersion_coefficient=coefficient
        )
        for fraction in (0.13, 0.47, 0.83):
            omega = lower + fraction * (upper - lower)
            response = geometric_schur_response(
                polarization_retarded_real(
                    omega,
                    q,
                    cutoff=cutoff,
                    dispersion_coefficient=coefficient,
                    yukawa=coupling,
                    rho_slope=rho_slope,
                ),
                pi_zero=pi_zero,
                eta_critical=eta_c,
                planck5_cubed=planck5_cubed,
                schur_factor=schur_factor,
            )
            retarded_passivity_samples.append(-response.imag / omega)

    exact_linearization_errors = []
    for deficit_fraction in (1.0e-8, 3.0e-7, 1.0e-5):
        pi_value = pi_zero * (1.0 - deficit_fraction)
        exact_response = geometric_schur_response(
            pi_value,
            pi_zero=pi_zero,
            eta_critical=eta_c,
            planck5_cubed=planck5_cubed,
            schur_factor=schur_factor,
        ).real
        linear_response = schur_factor * (pi_zero - pi_value) / planck5_cubed
        exact_linearization_errors.append(abs(exact_response / linear_response - 1.0))

    same_action_static_hessian = same_action_continuum_polarization_euclidean(
        0.0,
        regulator_mass=regulator_mass,
        yukawa=coupling,
        rho_slope=rho_slope,
    )
    same_action_pole = same_action_continuum_uhp_pole_b4_zero(
        0.7,
        q_zeta=q_zeta,
        eta_critical=eta_c,
        planck5_cubed=planck5_cubed,
        schur_factor=schur_factor,
        yukawa=coupling,
        rho_slope=rho_slope,
    )
    same_action_lapse_zero = same_action_continuum_lapse_coefficient_laplace(
        same_action_pole["lapse_zero"],
        eta_critical=eta_c,
        planck5_cubed=planck5_cubed,
        yukawa=coupling,
        rho_slope=rho_slope,
    )

    euclidean_values = [
        matched_euclidean_inverse(
            omega,
            q,
            q_zeta=q_zeta,
            k4_coefficient=k4_coefficient,
            eta_critical=eta_c,
            planck5_cubed=planck5_cubed,
            schur_factor=schur_factor,
            cutoff=cutoff,
            dispersion_coefficient=coefficient,
            yukawa=coupling,
            rho_slope=rho_slope,
        )
        for omega in (0.0, 0.01, 0.3, 2.0)
        for q in (0.05, 0.4, 1.3)
    ]
    imaginary_axis_values = [
        matched_retarded_inverse_complex(
            1j * gamma,
            q,
            q_zeta=q_zeta,
            k4_coefficient=k4_coefficient,
            eta_critical=eta_c,
            planck5_cubed=planck5_cubed,
            schur_factor=schur_factor,
            cutoff=cutoff,
            dispersion_coefficient=coefficient,
            yukawa=coupling,
            rho_slope=rho_slope,
            quadrature_order=512,
        ).real
        for gamma in (0.01, 0.2, 1.7)
        for q in (0.05, 0.4, 1.3)
    ]

    compact_ir = compactified_ir_exponents(3, z)
    continuum_ir = compactified_ir_exponents(4, z)
    lifshitz_z = 1.5
    lifshitz_radius = 1.0
    lifshitz_acceleration = khronon.lifshitz_acceleration_magnitude(
        lifshitz_z, lifshitz_radius
    )
    lifshitz_expansion = orthogonal_gapped_static_expansion(
        lifshitz_acceleration,
        regulator_mass=regulator_mass,
        yukawa=coupling,
        rho_slope=rho_slope,
    )
    constraint_inventory = khronon.local_constraint_inventory(4, include_dilaton=True)

    checks = {
        "certified_inputs": True,
        "five_local_Clifford_matrices_close": static_bath.clifford_error() == 0.0,
        "four_space_z2_DOS_is_exactly_linear": (
            math.isclose(rho_slope, expected_rho_slope, rel_tol=2.0e-15)
            and abs(dos_power - 1.0) < 2.0e-13
        ),
        "local_polynomial_Clifford_spectrum_closes": spectrum_error < 2.0e-15,
        "UV_finite_local_fermion_boson_integral_matches_exact_static_function": (
            sea_relative_error < 2.0e-10
        ),
        "positive_sea_quadratic_leaves_positive_baseline": (
            delta_eta > 0.0 and eta_inf > 0.0
        ),
        "matter_gravity_normalization_is_explicit_and_consistent": (
            math.isclose(
                pi_zero,
                2.0 * matter_quadratic_coefficient,
                rel_tol=2.0e-15,
            )
            and math.isclose(
                eta_inf_from_hessian,
                eta_inf,
                rel_tol=0.0,
                abs_tol=2.0e-15,
            )
        ),
        "geometric_Schur_still_gives_exact_mu": mu_error < 3.0e-15,
        "full_Euclidean_bubble_matches_spectral_integral": (
            maximum_euclidean_error < 2.0e-13
        ),
        "retarded_branch_cut_has_positive_exact_spectral_weight": (
            maximum_spectral_error < 2.0e-15
            and min(item[0] for item in spectral_samples) > 0.0
        ),
        "ohmic_limit_is_derived_not_assumed": math.isclose(
            ohmic_numeric, ohmic_expected, rel_tol=2.0e-6
        ),
        "critical_Euclidean_inverse_is_positive_off_origin": min(euclidean_values)
        > 0.0,
        "exact_Schur_reduces_to_linear_response_at_small_deficit": (
            max(exact_linearization_errors) < 1.0e-5
        ),
        "exact_Schur_retarded_response_is_passive_on_cut": (
            min(retarded_passivity_samples) > 0.0
        ),
        "exact_Schur_positive_real_no_UHP_theorem_sampled": (
            minimum_positive_real_margin > 0.0
        ),
        "same_action_continuum_q0_static_hessian_matches": math.isclose(
            same_action_static_hessian, pi_zero, rel_tol=2.0e-15
        ),
        "same_action_continuum_UV_has_explicit_UHP_pole": (
            abs(same_action_lapse_zero) < 3.0e-15
            and same_action_pole["positive_UHP_laplace_pole"]
            > same_action_pole["lapse_zero"]
            and same_action_pole["normalized_inverse_residual"] < 2.0e-11
        ),
        "same_action_finite_momentum_gradient_divergence_recorded": True,
        "pure_imaginary_upper_half_plane_axis_is_positive": min(imaginary_axis_values)
        > 0.0,
        "fundamental_lapse_constraint_keeps_positive_principal_rank": eta_inf > 0.0,
        "fermion_action_has_no_higher_preferred_time_derivative": True,
        "finite_compactification_changes_strict_IR_power": (
            math.isclose(compact_ir["density_of_states_power"], 0.5, abs_tol=1.0e-15)
            and math.isclose(
                compact_ir["filled_sea_nonanalytic_power"], 2.5, abs_tol=1.0e-15
            )
            and math.isclose(
                continuum_ir["filled_sea_nonanalytic_power"], 3.0, abs_tol=1.0e-15
            )
        ),
        "original_Lifshitz_radial_acceleration_gaps_the_cubic": (
            lifshitz_expansion["background_gap"] > 0.0
            and lifshitz_expansion["quadratic_coefficient"] > 0.0
            and lifshitz_expansion["cubic_coefficient"] == 0.0
            and lifshitz_expansion["quartic_coefficient"] < 0.0
        ),
        "local_scalar_completion_is_not_mislabelled_as_symmetry_protected": True,
        "finite_band_retarded_diagnostic_is_not_mislabelled_as_local_UV_completion": True,
        "no_force_lensing_or_publication_promotion": True,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"bulk z=2 completion checks failed: {failed}")

    decision = {
        "same_action_local_5D_Gaussian_static_bath_derived": True,
        "UV_finite_static_completion_without_hard_cutoff": True,
        "literal_bulk_single_particle_linear_DOS_derived": True,
        "exact_local_Clifford_spectrum_derived": True,
        "filled_negative_sea_sign_and_cubic_derived": True,
        "old_fractional_boundary_symbol_required": False,
        "three_vs_four_acceleration_component_mismatch_removed": True,
        "full_flat_finite_band_gaussian_retarded_kernel_derived": True,
        "same_action_local_UV_full_retarded_kernel_derived": False,
        "minimal_static_Gaussian_multiplet_same_action_UV_dynamics_survives": False,
        "same_action_q0_renormalized_retarded_kernel_derived": True,
        "same_action_continuum_has_upper_half_plane_pole": True,
        "same_action_finite_q_requires_gradient_counterterm": True,
        "retarded_branch_cut_resolved": True,
        "exact_metric_lapse_Schur_complement_retained": True,
        "critical_linear_flat_scalar_has_no_UHP_poles": True,
        "fundamental_flat_constraint_rank_preserved": True,
        "flat_background_linear_time_stability_complete_for_frozen_banded_model": True,
        "finite_band_retarded_regulator_derived_from_local_UV_completion": False,
        "critical_matching_Ward_protected": False,
        "finite_compact_HOLO_strict_IR_cubic_survives": False,
        "naive_isotropic_original_Lifshitz_background_route_survives": False,
        "gapless_radial_continuum_with_4D_gravity_localization_derived": False,
        "nonlinear_global_time_stability_derived": False,
        "current_compact_Einstein_dilaton_HOLO_completed": False,
        "physical_completion": False,
        "new_force_derived": False,
        "lensing_derived": False,
        "publication_authorized": False,
        "verdict": (
            "LOCAL_5D_Z2_GAUSSIAN_STATIC_BATH_AND_FLAT_BANDED_CAUSAL_GATE_PASS_"
            "COMPACT_HOLO_AND_RETARDED_UV_BLOCKED"
        ),
        "next_action": (
            "Replace the quadratic scalar portal by healthy UV partners whose "
            "linear response supplies the missing positive spectral weight, or "
            "derive a physical finite band before the explicit same-action UHP "
            "pole. In parallel construct a gapless radial continuum with localized "
            "4D gravity, or another covariant compact sector that keeps the linear "
            "DOS below its first KK gap; then repeat constraints, full kernels and "
            "junctions on that background before force or lensing."
        ),
    }

    return {
        "schema": SCHEMA,
        "title": "Local five-dimensional z=2 Clifford bath and causal flat gate",
        "classification": (
            "theory_only;local_5D_static_microscopic_and_banded_flat_causal_steps_closed;"
            "minimal_same_action_retarded_UV_killed;alternative_UV_and_compactification_open"
        ),
        "evidence_boundary": (
            "A local khronon-covariant 4+1 free-field action now derives the literal "
            "linear bulk DOS, Clifford spectrum, filled-sea sign and the complete "
            "UV-finite static bracket: two stable massive z=2 scalars per negative "
            "fermion branch supply its analytic part. A separately frozen positive-"
            "weight finite-band kernel resolves the flat linear branch cut; the "
            "exact metric/lapse Schur complement has no upper-half-plane pole. The "
            "actual local scalar partners contribute only a quadratic seagull; "
            "their same-action continuum response has an explicit upper-half-plane "
            "pole and is killed as a global UV completion. A finite "
            "compact radial direction also changes the strict-IR exponent. This is "
            "not a compact HOLO force or lensing result."
        ),
        "sources": {
            **_source_receipts(),
            "raw_observational_tables_read_directly": [],
            "primary_theory_references": [
                {
                    "topic": "healthy nonprojectable Horava gravity",
                    "url": "https://arxiv.org/abs/0909.3525",
                },
                {
                    "topic": "covariant khronon and MOND limit",
                    "url": "https://arxiv.org/abs/1107.5264",
                },
                {
                    "topic": "Hamiltonian constraints with lapse acceleration",
                    "url": "https://arxiv.org/abs/1106.2131",
                },
                {
                    "topic": "Lifshitz fermion power-counting precedent",
                    "url": "https://arxiv.org/abs/1612.05900",
                },
                {
                    "topic": "positive spectral bath influence functional",
                    "url": "https://doi.org/10.1016/0378-4371(83)90013-4",
                },
            ],
        },
        "single_local_5D_action": {
            "covariant_fields": [
                "G_MN",
                "T with U_M=-partial_M T/sqrt(-partial T squared)",
                "optional certified dilaton phi",
                "N_f four-component complex Spin(4) fermions Psi_f",
                "two real massive z=2 scalars per negative fermion branch",
            ],
            "spatial_projector": "h_MN=G_MN+U_M U_N",
            "acceleration": "a_M=U^N nabla_N U_M",
            "fermion_operator": (
                "Psi_dagger[i D_U-c Gamma_0(-D_perp^2)-" "y a_hatA Gamma_A]Psi, A=1..4"
            ),
            "derivative_order": {
                "preferred_time": 1,
                "spatial": 2,
                "dynamical_exponent": z,
            },
            "locality": "finite-derivative local bulk action",
            "covariance": (
                "five-dimensional diffeomorphism covariance with the preferred "
                "foliation carried by the dynamical khronon"
            ),
            "uniform_flat_solution": (
                "G=eta, T=t, a_A=0 and empty excitations after subtracting the "
                "a=0 sea stress"
            ),
            "static_UV_completion": (
                "per negative branch, two stable real scalars with "
                "omega_b^2=c^2 p^4+Lambda^2+y^2 a^2; their total -1 zero-point "
                "weight cancels the light-fermion UV integrand"
            ),
            "retarded_diagnostic_regulator": (
                "symmetric finite energy band epsilon<=Lambda; frozen for the exact "
                "linear response test but not derived from the continuum field action"
            ),
            "normalization": (
                "S_grav=(M5^3/2) integral N sqrt(h)[...+eta a^2]; matter "
                "Hessian Pi therefore contributes Pi/M5^3 to eta"
            ),
        },
        "microscopic_static_derivation": {
            "spatial_dimensions": spatial_dimensions,
            "dispersion": "epsilon=c*|p|^2",
            "negative_branches": negative_branches,
            "rho_negative": "rho1*epsilon",
            "rho1": rho_slope,
            "spectrum": "two copies of +/-sqrt(c^2|p|^4+y^2|a|^2) per flavor",
            "local_field_content_per_negative_branch": (
                "one filled light fermion branch plus two real stable z=2 scalars "
                "of mass squared Lambda^2+y^2 a^2"
            ),
            "joint_UV_finite_integrand": (
                "rho1*epsilon*{[sqrt(epsilon^2+m^2)-epsilon]-"
                "[sqrt(epsilon^2+Lambda^2+m^2)-sqrt(epsilon^2+Lambda^2)]}"
            ),
            "sea_lagrangian": ("rho1/3*[(Lambda^2+y^2 a^2)^(3/2)-Lambda^3-y^3|a|^3]"),
            "real_massive_scalars": 2 * negative_branches,
            "matter_quadratic_coefficient_K2": matter_quadratic_coefficient,
            "planck5_cubed": planck5_cubed,
            "quadratic_increment_Delta_eta": delta_eta,
            "geometric_eta_c": eta_c,
            "positive_eta_infinity": eta_inf,
            "critical_relation": (
                "eta_infinity+Delta_eta=eta_c with " "Delta_eta=2*K2/M5^3=Pi(0,0)/M5^3"
            ),
            "a0": a0,
            "reduced_mu": "1+x-sqrt(1+x^2)",
            "protection_status": (
                "the free Gaussian determinant is exact, but no Ward identity fixes "
                "the fermion-scalar multiplicity, equal c, portals or mass scale"
            ),
        },
        "constraint_completion": {
            "adapted_action": (
                "S_grav=(M5^3/2) integral N sqrt(h)[K_AB K^AB-lambda K^2+"
                "xi R4+eta_infinity a_A a^A+B4 spatial terms]+S_Psi+S_scalar"
            ),
            "lapse_or_shift_time_derivatives_added_by_bath": False,
            "fermion_time_derivative_order": 1,
            "fermion_spatial_derivative_order": 2,
            "fermion_primary_constraints": (
                "the first-order Grassmann momenta form an invertible second-class "
                "block; four complex canonical amplitudes per flavor"
            ),
            "gravity_constraint_inventory": constraint_inventory,
            "bare_lapse_principal_coefficient": 2.0 * eta_inf,
            "loop_corrected_static_lapse_principal_coefficient": 2.0 * eta_c,
            "gravity_DOF_unchanged_by_regular_fermion_constraint_block": True,
            "scope": "local uniform flat background and frozen EFT coefficients",
            "original_Proca_if_retained": {
                "massive_5D_Proca_DOF": 4,
                "total_bosonic_DOF_with_khronon_gravity_and_dilaton": 11,
                "warning": (
                    "Proca and the khronon are independent fields unless an "
                    "off-shell constraint is added and re-counted"
                ),
            },
            "full_warped_constraint_and_boundary_rank_derived": False,
        },
        "backreaction_and_boundary_gate": {
            "flat_patch": (
                "the a=0 vacuum energy and stress are subtracted by frozen local "
                "counterterms; this certifies only the uniform flat saddle"
            ),
            "warped_ansatz": ("ds^2=-exp(2V)dt^2+exp(2A)dx_3^2+exp(2D)dr^2, B=b(r)dt"),
            "required_background_equations": (
                "vary the combined gravity, khronon, Proca, fermion and scalar "
                "action before solving V,A,D,b; old Einstein-Proca parameters "
                "cannot be imported unchanged"
            ),
            "required_boundaries": (
                "Hamiltonian differentiability, zero symplectic flux, khronon/"
                "Proca junction conditions, radion and edge-mode count"
            ),
            "background_residuals_closed": False,
            "warped_junction_conditions_closed": False,
            "full_channel_QNM_spectrum_closed": False,
            "status": "BLOCKS_NONLINEAR_GLOBAL_STABILITY_AND_PHYSICAL_PROMOTION",
        },
        "retarded_completion": {
            "Pi_E": (
                "y^2 int_0^Lambda d epsilon rho1 epsilon*4(epsilon+s)/"
                "[Omega^2+4(epsilon+s)^2], s=c q^2/4"
            ),
            "Pi_R_spectral_representation": (
                "int_(2s)^(2s+2Lambda) dnu 2nu sigma(nu,q)/" "[nu^2-(omega+i0)^2]"
            ),
            "sigma": "y^2*rho1*(nu-2s)/4 on the cut and zero outside",
            "positive_spectral_measure": True,
            "positive_frequency_cut_at_q0": [0.0, 2.0 * cutoff],
            "small_frequency_F_coefficient_deficit": (
                "Pi(0,0)/2-Pi_E(Omega,0)/2=" "pi*y^2*rho1*|Omega|/8+O(Omega^2/Lambda)"
            ),
            "critical_inverse": (
                "D_R=-q_zeta omega^2+B4 q^4+q^2 H_R; "
                "C_R=eta_infinity+Pi_R/M5^3, "
                "H_R=A_g*(eta_c/C_R-1), A_g=(n-2)^2 eta_c"
            ),
            "linearized_Schur_limit": (
                "H_R=(n-2)^2[Pi(0,0)-Pi_R]/M5^3+O((Delta Pi)^2)"
            ),
            "no_UHP_proof": (
                "C(u,q)=eta_infinity+Pi_E(sqrt(u),q)/M5^3 is positive "
                "Stieltjes. Its reciprocal is complete-Bernstein, hence so is "
                "H(u,q)=A_g[eta_c/C(u,q)-1]. For p=-i omega with Re(p)>0, "
                "Re[D(p,q)/p]>0 because Re(p)>0, Re(1/p)>0 and each measure "
                "term obeys Re[p/(p^2+t)]>0. Therefore D has no UHP zero."
            ),
            "proof_scope": (
                "exact Gaussian/RPA linear response of the frozen positive-weight "
                "finite-band flat model at T=0; its logarithmic hard-band edge is "
                "included. It is separate from the local scalar completion, whose "
                "same-action continuum dynamics fails the following red-team gate"
            ),
            "nonlinear_or_running_coupling_stability": False,
        },
        "same_action_dynamic_red_team": {
            "fermion_q0_with_intermediate_cutoff": (
                "Pi_f,E=gamma*[R-|Omega|*atan(2R/|Omega|)/2]"
            ),
            "two_scalar_q0_seagull": (
                "Pi_b=-gamma*[sqrt(R^2+Lambda^2)-Lambda]; the a^2 phi^2 "
                "portal has no order-a^2 bubble or branch cut around a=0"
            ),
            "renormalized_q0_Hessian": ("Pi_same,E=gamma*[Lambda-pi*|Omega|/4]"),
            "critical_lapse_on_Laplace_axis": (
                "C(ip)=eta_c-kappa*p, kappa=pi*gamma/(4*M5^3)"
            ),
            "lapse_zero": same_action_pole["lapse_zero"],
            "explicit_B4_zero_UHP_pole": same_action_pole["positive_UHP_laplace_pole"],
            "normalized_inverse_residual": same_action_pole[
                "normalized_inverse_residual"
            ],
            "finite_B4_result": (
                "for every q>0, D tends to minus infinity just above the C=0 "
                "crossing and to plus infinity at large p, so finite B4 cannot "
                "remove the positive-p root"
            ),
            "finite_momentum_UV_behavior": (
                "Pi_same,E contains -gamma*c*q^2*log(R)/4; a (D_B a_A)^2 "
                "counterterm and a finite renormalization condition are required"
            ),
            "spectral_diagnosis": (
                "the fermion cut has positive weight only in a subtracted "
                "representation; the negative scalar contact has no compensating "
                "spectral continuum, so the total C is not positive Stieltjes"
            ),
            "EFT_window": (
                "eta_infinity>0 puts the lapse zero above 4*Lambda/pi, so the "
                "construction can remain conditional below its declared matter "
                "scale if new physics enters first"
            ),
            "status": "KILL_MINIMAL_SAME_ACTION_GLOBAL_RETARDED_UV_COMPLETION",
        },
        "lifshitz_background_obstruction": {
            "original_background": ("ds^2=L^2[du^2-exp(2zu)dt^2+exp(2u)dx_3^2], T=t"),
            "dynamical_exponent": lifshitz_z,
            "curvature_radius": lifshitz_radius,
            "khronon_acceleration": "a_hat_u=z/L",
            "acceleration_magnitude": lifshitz_acceleration,
            "fermion_background_gap": lifshitz_expansion["background_gap"],
            "orthogonal_perturbation_expansion": {
                "quadratic_coefficient": lifshitz_expansion["quadratic_coefficient"],
                "cubic_coefficient": lifshitz_expansion["cubic_coefficient"],
                "quartic_coefficient": lifshitz_expansion["quartic_coefficient"],
            },
            "spectral_geometry_warning": (
                "the spatial slice is H4, so the flat R4 DOS and commuting "
                "Clifford square are not an exact radial determinant on this "
                "background"
            ),
            "result": (
                "the nonzero radial acceleration makes tangential response analytic "
                "in b^2 and removes the required -|b|^3 term"
            ),
            "status": "KILL_NAIVE_ISOTROPIC_ORIGINAL_LIFSHITZ_BULK_ROUTE",
        },
        "compactification_obstruction": {
            "finite_interval_strict_IR_noncompact_spatial_dimensions": 3,
            "finite_interval_strict_IR_DOS_power": compact_ir[
                "density_of_states_power"
            ],
            "finite_interval_strict_IR_sea_power": compact_ir[
                "filled_sea_nonanalytic_power"
            ],
            "four_space_continuum_sea_power": continuum_ir[
                "filled_sea_nonanalytic_power"
            ],
            "finite_interval_result": (
                "below the first radial KK gap the zero mode gives rho~sqrt(epsilon) "
                "and |a|^(5/2), so the cubic is at most an intermediate-window law"
            ),
            "surviving_asymptotic_route": (
                "a gapless radial continuum, followed by an explicit demonstration "
                "that four-dimensional gravity and matter remain localized"
            ),
            "status": "BLOCKS_CURRENT_COMPACT_HOLO_PHYSICAL_COMPLETION",
        },
        "acceptance_ladder": [
            {"level": "Z0_local_5D_foliation_action", "status": "PASS"},
            {"level": "Z1_literal_linear_bulk_DOS", "status": "PASS"},
            {"level": "Z2_same_action_UV_finite_static_Clifford_sea", "status": "PASS"},
            {"level": "Z3_flat_constraint_rank", "status": "PASS"},
            {
                "level": "Z4_flat_finite_band_retarded_linear_stability",
                "status": "PASS",
            },
            {
                "level": "Z4a_minimal_same_action_global_retarded_UV",
                "status": "KILLED",
            },
            {
                "level": "Z4b_original_Lifshitz_background_transfer",
                "status": "KILLED",
            },
            {"level": "Z5_finite_compact_HOLO_strict_IR", "status": "KILLED"},
            {
                "level": "Z6_same_action_retarded_UV_and_protected_matching",
                "status": "BLOCKED",
            },
            {"level": "Z7_force_matter_lensing", "status": "NOT_ENTERED"},
        ],
        "diagnostics": {
            "rho_slope": rho_slope,
            "DOS_log_slope": dos_power,
            "Clifford_spectrum_max_error": spectrum_error,
            "sea_integral_relative_error": sea_relative_error,
            "mu_max_error": mu_error,
            "Euclidean_closed_form_max_error": maximum_euclidean_error,
            "retarded_spectral_weight_max_error": maximum_spectral_error,
            "ohmic_coefficient_numeric": ohmic_numeric,
            "ohmic_coefficient_expected": ohmic_expected,
            "minimum_Euclidean_inverse_off_origin": min(euclidean_values),
            "maximum_exact_Schur_linearization_relative_error": max(
                exact_linearization_errors
            ),
            "minimum_exact_Schur_retarded_passivity": min(retarded_passivity_samples),
            "minimum_positive_real_no_UHP_margin": minimum_positive_real_margin,
            "minimum_imaginary_axis_inverse": min(imaginary_axis_values),
            "same_action_continuum_lapse_zero": same_action_pole["lapse_zero"],
            "same_action_continuum_B4_zero_UHP_pole": same_action_pole[
                "positive_UHP_laplace_pole"
            ],
            "same_action_UHP_pole_normalized_residual": same_action_pole[
                "normalized_inverse_residual"
            ],
        },
        "checks": {**checks, "all": all(checks.values())},
        "decision": decision,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    payload = build()
    _write(OUTPUT, payload)
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
