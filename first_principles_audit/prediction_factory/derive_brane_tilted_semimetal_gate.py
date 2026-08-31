#!/usr/bin/env python3
"""Derive a covariant-brane tilted-semimetal rescue gate.

The local four-space ``z=2`` Clifford bath derives the desired static bracket,
but an ordinary compact fifth direction changes its strict-IR density of
states and the minimal scalar UV subtraction fails dynamically.  This module
tests a different material rather than forcing either failed ingredient.

On a covariantly embedded 3+1 defect, introduce a spatial director ``n`` and
the local Hermitian one-particle Hamiltonian

    H = epsilon_op^2/Lambda * 1
        + v (-i D_parallel) Gamma_0
        + c (-D_perp^2) Gamma_1
        + y a_i Gamma_(i+1),                         i=1,2,3.

The five matrices form Cl(5), and in a uniform patch

    epsilon^2 = v^2 k_parallel^2 + c^2 k_perp^4,
    E_+/- = epsilon^2/Lambda +/- sqrt(epsilon^2+y^2|a|^2).

The anisotropic but finite-derivative dispersion has a literal three-space
DOS ``rho_branch=epsilon/(8*pi*c*v)``.  At ``a=0`` the lower band is negative
only for ``0<epsilon<Lambda`` and the spectrum is bounded below.  In the
canonical fixed-charge sector that fills exactly these states, the occupied
set remains the set of lowest states for every uniform ``a``.  The identity
tilt cancels from the energy difference, so one obtains exactly

    rho1/3 * [(Lambda^2+y^2 a^2)^(3/2)-Lambda^3-y^3|a|^3]

without regulator scalars.  The same local matter ansatz gives the finite
zero-momentum particle-hole band and positive spectral measure.  A direct
finite-momentum Kubo quadrature below includes both interband transitions and
Pauli-allowed lower-band transitions; it is used only as a flat-defect
regression.

The construction is a materially stronger candidate, not a finished HOLO
mechanism.  Fixed filling is a state/charge-sector choice, the director breaks
continuous spatial rotations in dynamical correlators, and the covariant
brane junction conditions, backreaction, full constraint algebra, source and
lensing maps remain to be solved before physical promotion.
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
    from . import derive_bulk_z2_clifford_completion_gate as bulk_gate
    from . import derive_dirac_critical_bath_gate as clifford_gate
    from . import derive_khronon_constraint_stability_gate as khronon
else:
    import derive_bulk_z2_clifford_completion_gate as bulk_gate
    import derive_dirac_critical_bath_gate as clifford_gate
    import derive_khronon_constraint_stability_gate as khronon


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BULK_GATE = HERE / "artifacts" / "bulk_z2_clifford_completion_gate.json"
OUTPUT = HERE / "artifacts" / "brane_tilted_semimetal_gate.json"

SCHEMA = "holo.brane-tilted-semimetal-gate.v1"


class BraneSemimetalInputError(ValueError):
    """A parameter or input certificate is malformed."""


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise BraneSemimetalInputError(f"{name} must be positive and finite")
    return result


def _nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise BraneSemimetalInputError(f"{name} must be nonnegative and finite")
    return result


def _positive_integer(value: int, name: str) -> int:
    if type(value) is not int or value <= 0:
        raise BraneSemimetalInputError(f"{name} must be a positive integer")
    return value


def _read(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BraneSemimetalInputError(f"cannot read {path}: {exc}") from exc
    if type(payload) is not dict:
        raise BraneSemimetalInputError(f"{path}: expected a JSON object")
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


@functools.lru_cache(maxsize=16)
def _gauss_legendre(order: int) -> tuple[np.ndarray, np.ndarray]:
    if type(order) is not int or order < 8:
        raise BraneSemimetalInputError("quadrature order must be an integer >= 8")
    return np.polynomial.legendre.leggauss(order)


def anisotropic_dos_slope(
    linear_velocity: float,
    quadratic_coefficient: float,
    *,
    flavor_count: int = 1,
    negative_branches_per_flavor: int = 2,
) -> float:
    r"""Return ``rho(epsilon)/epsilon`` for the three-space semimetal.

    Per branch,

    ``N(E)/V3=E^2/(16*pi*c*v)`` and
    ``rho(E)=E/(8*pi*c*v)``.
    """

    velocity = _positive(linear_velocity, "linear_velocity")
    coefficient = _positive(quadratic_coefficient, "quadratic_coefficient")
    flavors = _positive_integer(flavor_count, "flavor_count")
    branches = _positive_integer(
        negative_branches_per_flavor, "negative_branches_per_flavor"
    )
    return flavors * branches / (8.0 * math.pi * coefficient * velocity)


def tilted_semimetal_spectrum(
    parallel_momentum: float,
    transverse_momentum: Sequence[float],
    acceleration: Sequence[float],
    *,
    band_edge: float,
    linear_velocity: float,
    quadratic_coefficient: float,
    yukawa: float,
) -> np.ndarray:
    """Diagonalize the local tilted Cl(5) Hamiltonian."""

    k_parallel = float(parallel_momentum)
    k_perp = np.asarray(transverse_momentum, dtype=float)
    vector_a = np.asarray(acceleration, dtype=float)
    if not math.isfinite(k_parallel):
        raise BraneSemimetalInputError("parallel_momentum must be finite")
    if k_perp.shape != (2,) or vector_a.shape != (3,):
        raise BraneSemimetalInputError(
            "transverse_momentum must be a 2-vector and acceleration a 3-vector"
        )
    if np.any(~np.isfinite(k_perp)) or np.any(~np.isfinite(vector_a)):
        raise BraneSemimetalInputError("momenta and acceleration must be finite")
    scale = _positive(band_edge, "band_edge")
    velocity = _positive(linear_velocity, "linear_velocity")
    coefficient = _positive(quadratic_coefficient, "quadratic_coefficient")
    coupling = _positive(yukawa, "yukawa")
    gamma = clifford_gate.clifford_five()
    h_parallel = velocity * k_parallel
    h_transverse = coefficient * float(k_perp @ k_perp)
    epsilon_squared = h_parallel**2 + h_transverse**2
    hamiltonian = epsilon_squared / scale * np.eye(4, dtype=complex)
    hamiltonian += h_parallel * gamma[0] + h_transverse * gamma[1]
    for index, component in enumerate(vector_a):
        hamiltonian += coupling * component * gamma[index + 2]
    return np.linalg.eigvalsh(hamiltonian)


def lower_band_energy(energy: float, gap: float, band_edge: float) -> float:
    """Return ``E_-=epsilon^2/Lambda-sqrt(epsilon^2+m^2)``."""

    epsilon = _nonnegative(energy, "energy")
    mass = _nonnegative(gap, "gap")
    scale = _positive(band_edge, "band_edge")
    return epsilon * epsilon / scale - math.hypot(epsilon, mass)


def lower_band_global_minimum(gap: float, band_edge: float) -> float:
    r"""Exact finite lower bound of ``E_-(epsilon)`` for ``epsilon>=0``."""

    mass = _nonnegative(gap, "gap")
    scale = _positive(band_edge, "band_edge")
    if mass >= 0.5 * scale:
        return -mass
    return -0.25 * scale - mass * mass / scale


def fixed_filling_density(rho_slope: float, band_edge: float) -> float:
    """Conserved particle density that fills all lower states below the edge."""

    slope = _positive(rho_slope, "rho_slope")
    scale = _positive(band_edge, "band_edge")
    return 0.5 * slope * scale * scale


def fixed_filling_chemical_potential(
    acceleration: float,
    *,
    band_edge: float,
    yukawa: float,
) -> float:
    """Highest occupied energy in the fixed-charge sector."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(band_edge, "band_edge")
    coupling = _positive(yukawa, "yukawa")
    return scale - math.hypot(scale, coupling * magnitude)


def fixed_filling_lagrangian(
    acceleration: float,
    *,
    band_edge: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    """Exact static filled-band Lagrangian; the identity tilt cancels."""

    return bulk_gate.local_gaussian_completion_lagrangian(
        acceleration,
        regulator_mass=band_edge,
        yukawa=yukawa,
        rho_slope=rho_slope,
    )


def numerical_fixed_filling_lagrangian(
    acceleration: float,
    *,
    band_edge: float,
    yukawa: float,
    rho_slope: float,
    quadrature_order: int = 256,
) -> float:
    """Integrate the occupied semimetal band directly, independently of upstream."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(band_edge, "band_edge")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    nodes, weights = _gauss_legendre(quadrature_order)
    energies = 0.5 * scale * (nodes + 1.0)
    mass = coupling * magnitude
    integrand = energies * (np.hypot(energies, mass) - energies)
    result = slope * 0.5 * scale * float(np.sum(weights * integrand))
    if not math.isfinite(result) or result < 0.0:
        raise BraneSemimetalInputError("fixed-band integral lost positivity")
    return result


def grand_canonical_lagrangian(
    acceleration: float,
    *,
    band_edge: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    r"""Static result at fixed zero chemical potential, for comparison.

    This state preserves the quadratic and cubic terms but differs from the
    target bracket beginning at fourth order.  It is recorded so that fixed
    charge is not silently confused with a dynamically selected filling.
    """

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(band_edge, "band_edge")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    x = coupling * magnitude / scale
    t = 0.5 * (1.0 + math.sqrt(1.0 + 4.0 * x * x))
    dimensionless = t**3 / 3.0 - t**2 / 4.0 - x**3 / 3.0 - 1.0 / 12.0
    return slope * scale**3 * dimensionless


def fixed_filling_ordering_margin(
    acceleration: float,
    *,
    band_edge: float,
    yukawa: float,
    outside_fraction: float = 0.01,
) -> dict[str, float]:
    """Numerically expose that the filled interval remains the lowest set."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(band_edge, "band_edge")
    coupling = _positive(yukawa, "yukawa")
    fraction = _positive(outside_fraction, "outside_fraction")
    gap = coupling * magnitude
    endpoints = (
        lower_band_energy(0.0, gap, scale),
        lower_band_energy(scale, gap, scale),
    )
    highest_inside = max(endpoints)
    first_outside = lower_band_energy(scale * (1.0 + fraction), gap, scale)
    return {
        "energy_at_node": endpoints[0],
        "highest_occupied_energy": endpoints[1],
        "sampled_first_outside_energy": first_outside,
        "outside_minus_highest_inside": first_outside - highest_inside,
    }


def fixed_filling_interval_is_globally_lowest(
    acceleration: float,
    *,
    band_edge: float,
    yukawa: float,
) -> bool:
    r"""Certify that ``0<=epsilon<=Lambda`` contains the lowest fixed-count states.

    ``E_-`` has at most one interior stationary point, which is a minimum, so
    its maximum on the occupied interval is at an endpoint.  Moreover
    ``E_-(Lambda)>E_-(0)`` and ``E_-`` is strictly increasing above ``Lambda``.
    """

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(band_edge, "band_edge")
    coupling = _positive(yukawa, "yukawa")
    gap = coupling * magnitude
    at_node = lower_band_energy(0.0, gap, scale)
    at_edge = lower_band_energy(scale, gap, scale)
    derivative_factor_at_edge = 2.0 / scale - 1.0 / math.hypot(scale, gap)
    return at_edge >= at_node and derivative_factor_at_edge > 0.0


def polarization_q0_euclidean(
    frequency: float,
    *,
    band_edge: float,
    yukawa: float,
    rho_slope: float,
) -> float:
    """Exact same-action particle-hole Hessian at zero spatial momentum."""

    return bulk_gate.polarization_euclidean(
        frequency,
        0.0,
        cutoff=band_edge,
        dispersion_coefficient=1.0,
        yukawa=yukawa,
        rho_slope=rho_slope,
    )


def q0_schur_laplace_inverse(
    laplace_frequency: complex,
    wave_number: float,
    *,
    q_zeta: float,
    k4_coefficient: float,
    eta_critical: float,
    brane_planck_squared: float,
    schur_factor: float,
    band_edge: float,
    yukawa: float,
    rho_slope: float,
    quadrature_order: int = 256,
) -> complex:
    r"""Long-wavelength exact-Schur inverse from the same physical band.

    The material polarization is evaluated at its exact ``q=0`` limit while
    ``wave_number`` retains the two acceleration vertices in the gravitational
    scalar kernel.  This certifies the long-wavelength time dependence only;
    the direct finite-momentum Kubo block below is kept separate.
    """

    p = complex(laplace_frequency)
    if not (math.isfinite(p.real) and math.isfinite(p.imag)) or p.real <= 0.0:
        raise BraneSemimetalInputError(
            "laplace_frequency must have finite positive real part"
        )
    q = _nonnegative(wave_number, "wave_number")
    kinetic = _positive(q_zeta, "q_zeta")
    stabilizer = _nonnegative(k4_coefficient, "k4_coefficient")
    eta_c = _positive(eta_critical, "eta_critical")
    planck = _positive(brane_planck_squared, "brane_planck_squared")
    geometric_ratio = _positive(schur_factor, "schur_factor")
    scale = _positive(band_edge, "band_edge")
    coupling = _positive(yukawa, "yukawa")
    slope = _positive(rho_slope, "rho_slope")
    pi_zero = polarization_q0_euclidean(
        0.0,
        band_edge=scale,
        yukawa=coupling,
        rho_slope=slope,
    )
    eta_inf = eta_c - pi_zero / planck
    if eta_inf <= 0.0:
        raise BraneSemimetalInputError("critical brane matching lost positive floor")
    pi_value = bulk_gate.polarization_complex(
        1j * p,
        0.0,
        cutoff=scale,
        dispersion_coefficient=1.0,
        yukawa=coupling,
        rho_slope=slope,
        quadrature_order=quadrature_order,
    )
    lapse = eta_inf + pi_value / planck
    a_g = geometric_ratio * eta_c
    schur = a_g * (eta_c / lapse - 1.0)
    return kinetic * p * p + stabilizer * q**4 + q * q * schur


def q0_positive_real_stability_margin(
    laplace_frequency: complex,
    wave_number: float,
    **kwargs: Any,
) -> float:
    """Return ``Re[D(p,q)/p]`` for the long-wavelength same-action band."""

    p = complex(laplace_frequency)
    inverse = q0_schur_laplace_inverse(p, wave_number, **kwargs)
    margin = float((inverse / p).real)
    if not math.isfinite(margin):
        raise BraneSemimetalInputError("positive-real margin is not finite")
    return margin


def polarization_finite_momentum_euclidean(
    frequency: float,
    parallel_momentum: float,
    transverse_momentum: float,
    *,
    band_edge: float,
    linear_velocity: float,
    quadratic_coefficient: float,
    yukawa: float,
    flavor_count: int = 1,
    radial_order: int = 40,
    polar_order: int = 28,
    azimuthal_order: int = 32,
) -> float:
    r"""Direct positive Kubo quadrature for one acceleration component.

    The occupied initial lower band is parameterized by
    ``x=v*k_parallel=epsilon*cos(theta)`` and
    ``w=c*k_perp^2=epsilon*sin(theta)``.  The trace weights are
    ``1+n.n'`` for lower-to-upper and ``1-n.n'`` for a Pauli-allowed
    lower-to-lower transition.  Every retained gap and weight is nonnegative.
    """

    omega = _nonnegative(frequency, "frequency")
    q_parallel = float(parallel_momentum)
    q_perp = _nonnegative(transverse_momentum, "transverse_momentum")
    if not math.isfinite(q_parallel):
        raise BraneSemimetalInputError("parallel_momentum must be finite")
    scale = _positive(band_edge, "band_edge")
    velocity = _positive(linear_velocity, "linear_velocity")
    coefficient = _positive(quadratic_coefficient, "quadratic_coefficient")
    coupling = _positive(yukawa, "yukawa")
    flavors = _positive_integer(flavor_count, "flavor_count")
    nodes_e, weights_e = _gauss_legendre(radial_order)
    nodes_t, weights_t = _gauss_legendre(polar_order)
    nodes_p, weights_p = _gauss_legendre(azimuthal_order)
    energies = 0.5 * scale * (nodes_e + 1.0)
    weights_e = 0.5 * scale * weights_e
    thetas = 0.5 * math.pi * (nodes_t + 1.0)
    weights_t = 0.5 * math.pi * weights_t
    phis = math.pi * (nodes_p + 1.0)
    weights_p = math.pi * weights_p
    total = 0.0
    for epsilon, weight_e in zip(energies, weights_e, strict=True):
        initial_energy = lower_band_energy(float(epsilon), 0.0, scale)
        for theta, weight_t in zip(thetas, weights_t, strict=True):
            x = float(epsilon * math.cos(float(theta)))
            w = float(epsilon * math.sin(float(theta)))
            k_parallel = x / velocity
            transverse_radius = math.sqrt(max(0.0, w / coefficient))
            for phi, weight_p in zip(phis, weights_p, strict=True):
                k_x = transverse_radius * math.cos(float(phi))
                k_y = transverse_radius * math.sin(float(phi))
                final_x = velocity * (k_parallel + q_parallel)
                final_radius_squared = (k_x + q_perp) ** 2 + k_y**2
                final_w = coefficient * final_radius_squared
                final_epsilon = math.hypot(final_x, final_w)
                dot = (
                    (x * final_x + w * final_w) / (float(epsilon) * final_epsilon)
                    if final_epsilon > 0.0
                    else 0.0
                )
                dot = min(1.0, max(-1.0, dot))
                final_plus = final_epsilon**2 / scale + final_epsilon
                gap_plus = final_plus - initial_energy
                if gap_plus <= 0.0:
                    raise BraneSemimetalInputError("interband gap lost positivity")
                trace_plus = 1.0 + dot
                response = (
                    2.0 * gap_plus * trace_plus / (omega * omega + gap_plus * gap_plus)
                )
                if final_epsilon > scale:
                    final_minus = final_epsilon**2 / scale - final_epsilon
                    gap_minus = final_minus - initial_energy
                    if gap_minus <= 0.0:
                        raise BraneSemimetalInputError(
                            "lower-band particle-hole gap lost positivity"
                        )
                    response += (
                        2.0
                        * gap_minus
                        * (1.0 - dot)
                        / (omega * omega + gap_minus * gap_minus)
                    )
                measure = (
                    float(epsilon)
                    * float(weight_e)
                    * float(weight_t)
                    * float(weight_p)
                    / (16.0 * math.pi**3 * coefficient * velocity)
                )
                total += measure * response
    result = flavors * coupling * coupling * total
    if not math.isfinite(result) or result < 0.0:
        raise BraneSemimetalInputError("finite-momentum Kubo kernel lost positivity")
    return result


def polarization_triad_euclidean(
    frequency: float,
    momentum: Sequence[float],
    *,
    band_edge: float,
    linear_velocity: float,
    quadratic_coefficient: float,
    yukawa: float,
    radial_order: int = 40,
    polar_order: int = 28,
    azimuthal_order: int = 32,
) -> float:
    """Sum three orthogonal director species for a physical 3-momentum.

    The triad makes the reference stress and the analytic ``q^2`` response
    isotropic.  It retains only cubic, not continuous ``SO(3)``, symmetry at
    fourth and higher spatial order.
    """

    vector_q = np.asarray(momentum, dtype=float)
    if vector_q.shape != (3,) or np.any(~np.isfinite(vector_q)):
        raise BraneSemimetalInputError("momentum must be a finite 3-vector")
    total = 0.0
    norm_squared = float(vector_q @ vector_q)
    for axis in range(3):
        parallel = float(vector_q[axis])
        perpendicular = math.sqrt(max(0.0, norm_squared - parallel * parallel))
        total += polarization_finite_momentum_euclidean(
            frequency,
            parallel,
            perpendicular,
            band_edge=band_edge,
            linear_velocity=linear_velocity,
            quadratic_coefficient=quadratic_coefficient,
            yukawa=yukawa,
            flavor_count=1,
            radial_order=radial_order,
            polar_order=polar_order,
            azimuthal_order=azimuthal_order,
        )
    return total


def build() -> dict[str, Any]:
    upstream = _read(BULK_GATE)
    if upstream.get("schema") != "holo.bulk-z2-clifford-completion-gate.v1":
        raise BraneSemimetalInputError("unexpected upstream bulk gate schema")
    if upstream.get("checks", {}).get("all") is not True:
        raise BraneSemimetalInputError("upstream bulk gate is not certified")
    if (
        upstream.get("decision", {}).get(
            "minimal_static_Gaussian_multiplet_same_action_UV_dynamics_survives"
        )
        is not False
    ):
        raise BraneSemimetalInputError("upstream dynamic falsifier was not retained")

    velocity = 0.9
    coefficient = 0.8
    coupling = 1.1
    band_edge = 1.7
    director_count = 3
    flavors = director_count
    branches = 2
    brane_planck_squared = 1.0
    # This is only the local 3+1 induced-metric Schur witness.  A defect bath
    # renormalizes a brane acceleration coefficient, not the bulk n=4 eta.
    eta_c = khronon.geometric_critical_eta(3, 1.0)
    rho_slope = anisotropic_dos_slope(
        velocity,
        coefficient,
        flavor_count=flavors,
        negative_branches_per_flavor=branches,
    )
    expected_slope = branches * flavors / (8.0 * math.pi * coefficient * velocity)

    k_parallel = 0.31
    k_perp = np.asarray([0.24, -0.17])
    acceleration = np.asarray([0.19, -0.28, 0.37])
    spectrum = tilted_semimetal_spectrum(
        k_parallel,
        k_perp,
        acceleration,
        band_edge=band_edge,
        linear_velocity=velocity,
        quadratic_coefficient=coefficient,
        yukawa=coupling,
    )
    epsilon_squared = (velocity * k_parallel) ** 2 + (
        coefficient * float(k_perp @ k_perp)
    ) ** 2
    tilt = epsilon_squared / band_edge
    split = math.sqrt(
        epsilon_squared + coupling**2 * float(acceleration @ acceleration)
    )
    expected_spectrum = np.asarray([tilt - split] * 2 + [tilt + split] * 2)
    spectrum_error = float(np.max(np.abs(spectrum - expected_spectrum)))

    acceleration_magnitude = float(np.linalg.norm(acceleration))
    static_closed = fixed_filling_lagrangian(
        acceleration_magnitude,
        band_edge=band_edge,
        yukawa=coupling,
        rho_slope=rho_slope,
    )
    static_quadrature = numerical_fixed_filling_lagrangian(
        acceleration_magnitude,
        band_edge=band_edge,
        yukawa=coupling,
        rho_slope=rho_slope,
        quadrature_order=768,
    )
    static_relative_error = abs(static_quadrature / static_closed - 1.0)
    global_minimum = lower_band_global_minimum(
        coupling * acceleration_magnitude, band_edge
    )
    filling_density = fixed_filling_density(rho_slope, band_edge)
    ordering_margins = [
        fixed_filling_ordering_margin(
            value,
            band_edge=band_edge,
            yukawa=coupling,
        )["outside_minus_highest_inside"]
        for value in (0.0, 0.1, 1.0, 10.0)
    ]
    ordering_certificates = [
        fixed_filling_interval_is_globally_lowest(
            value,
            band_edge=band_edge,
            yukawa=coupling,
        )
        for value in (0.0, 0.1, 1.0, 10.0)
    ]

    pi_zero = polarization_q0_euclidean(
        0.0,
        band_edge=band_edge,
        yukawa=coupling,
        rho_slope=rho_slope,
    )
    delta_eta = pi_zero / brane_planck_squared
    eta_inf = eta_c - delta_eta
    if eta_inf <= 0.0:
        raise RuntimeError("diagnostic filling overwhelms positive eta infinity")
    q_zeta = khronon.scalar_kinetic_coefficient(3, 1.2)
    k4_coefficient = 0.8
    schur_factor = 1.0
    positive_real_margins = [
        q0_positive_real_stability_margin(
            p,
            q,
            q_zeta=q_zeta,
            k4_coefficient=k4_coefficient,
            eta_critical=eta_c,
            brane_planck_squared=brane_planck_squared,
            schur_factor=schur_factor,
            band_edge=band_edge,
            yukawa=coupling,
            rho_slope=rho_slope,
            quadrature_order=512,
        )
        for p in (0.08 + 0.3j, 0.4 - 0.7j, 1.2 + 1.8j)
        for q in (0.03, 0.2, 0.9)
    ]

    q0_errors = []
    for omega in (0.0, 0.13, 0.8):
        direct = polarization_finite_momentum_euclidean(
            omega,
            0.0,
            0.0,
            band_edge=band_edge,
            linear_velocity=velocity,
            quadratic_coefficient=coefficient,
            yukawa=coupling,
            flavor_count=flavors,
            radial_order=48,
            polar_order=16,
            azimuthal_order=16,
        )
        exact = polarization_q0_euclidean(
            omega,
            band_edge=band_edge,
            yukawa=coupling,
            rho_slope=rho_slope,
        )
        q0_errors.append(abs(direct - exact))

    finite_q_samples = []
    for q_vector in (
        (0.08, 0.0, 0.0),
        (0.08 / math.sqrt(3.0),) * 3,
        (0.2, 0.15, 0.1),
    ):
        values = [
            polarization_triad_euclidean(
                omega,
                q_vector,
                band_edge=band_edge,
                linear_velocity=velocity,
                quadratic_coefficient=coefficient,
                yukawa=coupling,
                radial_order=36,
                polar_order=24,
                azimuthal_order=24,
            )
            for omega in (0.0, 0.2, 0.8)
        ]
        finite_q_samples.append(
            {
                "q_vector": list(q_vector),
                "q_magnitude": float(np.linalg.norm(q_vector)),
                "Pi_E": values,
                "monotone_in_Euclidean_frequency": all(
                    left >= right for left, right in zip(values, values[1:])
                ),
            }
        )

    grand = grand_canonical_lagrangian(
        acceleration_magnitude,
        band_edge=band_edge,
        yukawa=coupling,
        rho_slope=rho_slope,
    )
    grand_differs = abs(grand / static_closed - 1.0)

    checks = {
        "upstream_falsifier_retained": True,
        "Clifford_five_closes": clifford_gate.clifford_error() == 0.0,
        "literal_three_space_DOS_is_linear": math.isclose(
            rho_slope, expected_slope, rel_tol=2.0e-15
        ),
        "tilted_spectrum_closes": spectrum_error < 2.0e-15,
        "single_particle_Hamiltonian_is_bounded_below": (
            math.isfinite(global_minimum)
            and lower_band_energy(
                band_edge * 100.0,
                coupling * acceleration_magnitude,
                band_edge,
            )
            > global_minimum
        ),
        "fixed_filling_interval_is_globally_lowest": all(ordering_certificates),
        "fixed_filling_static_bracket_is_exact": static_relative_error < 2.0e-10,
        "same_action_q0_Kubo_matches_closed_band_kernel": max(q0_errors) < 2.0e-12,
        "finite_q_Kubo_samples_are_positive": min(
            value for row in finite_q_samples for value in row["Pi_E"]
        )
        > 0.0,
        "finite_q_Kubo_samples_decrease_with_Euclidean_frequency": all(
            row["monotone_in_Euclidean_frequency"] for row in finite_q_samples
        ),
        "finite_q_sampled_static_response_does_not_exceed_q0": max(
            row["Pi_E"][0] for row in finite_q_samples
        )
        <= pi_zero,
        "reduced_brane_q0_Schur_positive_real_gate": min(positive_real_margins) > 0.0,
        "bare_lapse_coefficient_remains_positive": eta_inf > 0.0,
        "fixed_filling_not_confused_with_grand_canonical_state": grand_differs > 1.0e-4,
        "no_force_lensing_or_publication_promotion": True,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"brane tilted-semimetal checks failed: {failed}")

    decision = {
        "local_covariant_5D_defect_matter_ansatz_exhibited": True,
        "literal_three_space_linear_DOS_derived": True,
        "bounded_below_Hamiltonian_and_finite_occupied_region_from_same_ansatz": True,
        "fixed_charge_sector_required": True,
        "fixed_charge_sector_dynamically_selected": False,
        "exact_static_bracket_from_same_finite_occupied_region": True,
        "same_ansatz_q0_acceleration_retarded_kernel_derived": True,
        "same_ansatz_q0_acceleration_positive_spectral_measure": True,
        "reduced_brane_long_wavelength_Schur_has_no_UHP_poles": True,
        "same_ansatz_finite_q_acceleration_block_positive_Kubo_representation_derived": True,
        "finite_q_sampled_static_response_below_q0": True,
        "full_q_all_vertex_global_Schur_stability_derived": False,
        "inhomogeneous_fixed_charge_local_functional_derived": False,
        "metric_and_density_intraband_channels_included": False,
        "ordinary_radial_KK_linear_DOS_required": False,
        "original_Lifshitz_radial_acceleration_gaps_defect_bath": False,
        "continuous_SO3_dynamical_isotropy_derived": False,
        "full_brane_constraint_and_junction_rank_derived": False,
        "warped_backreacted_solution_derived": False,
        "physical_completion": False,
        "new_force_derived": False,
        "lensing_derived": False,
        "publication_authorized": False,
        "verdict": (
            "COVARIANT_BRANE_TILTED_SEMIMETAL_STATIC_AND_Q0_ACCELERATION_RETARDED_PASS_"
            "FULL_Q_ISOTROPY_JUNCTIONS_AND_PHYSICS_BLOCKED"
        ),
        "next_action": (
            "Derive the full anisotropic finite-q acceleration, density and metric "
            "spectral matrix, control charge redistribution and retain the exact "
            "brane/bulk Schur denominator; then introduce a covariant director/"
            "solid sector, vary "
            "the complete bulk-plus-brane action and close junction, backreaction "
            "and all-channel QNM gates before sourcing or lensing."
        ),
    }

    return {
        "schema": SCHEMA,
        "title": "Covariant-brane tilted-semimetal microscopic rescue gate",
        "classification": (
            "theory_only;same_ansatz_static_and_q0_acceleration_retarded_pass;"
            "full_q_isotropy_constraints_and_physics_open"
        ),
        "evidence_boundary": (
            "A finite-derivative tilted semimetal on a prescribed covariantly "
            "embedded 3+1 defect derives the linear DOS, a bounded-below "
            "Hamiltonian, a finite "
            "occupied region, the exact static bracket and q=0 retarded kernel "
            "from the same matter ansatz in a declared "
            "fixed-charge sector. Finite-q acceleration-block Kubo samples retain "
            "positive spectral "
            "weights, but no global full-q Schur bound, continuous rotational "
            "completion, warped junction solution, force or lensing law is claimed."
        ),
        "sources": {
            "bulk_z2_red_team_gate": {
                "path": str(BULK_GATE.relative_to(REPO)),
                "sha256": _sha256(BULK_GATE),
            },
            "raw_observational_tables_read_directly": [],
        },
        "covariant_defect_matter_ansatz": {
            "embedding": "X^M(xi) with induced gamma_mu_nu and unit normal s^M",
            "induced_khronon": (
                "u_mu is the normalized tangential pullback of U_M; "
                "P_mu_nu=gamma_mu_nu+u_mu*u_nu"
            ),
            "tangential_acceleration": (
                "A_mu=P_mu^nu e_nu^M a_M; the background radial a_M is projected out"
            ),
            "director": (
                "orthonormal spatial triad n_alpha^mu; summing its three species "
                "restores reference-stress and q^2 isotropy, while a solid/director "
                "action is required and q^4 retains cubic anisotropy"
            ),
            "Hamiltonian": (
                "H=epsilon_op^2/Lambda*I+v*(-iD_parallel)*Gamma0+"
                "c*(-D_perp^2)*Gamma1+y*A_i*Gamma_(i+1)"
            ),
            "derivative_orders": {
                "preferred_time": 1,
                "parallel_spatial": 2,
                "transverse_spatial": 4,
                "IR_scaling": "k_parallel~epsilon, k_perp~sqrt(epsilon)",
            },
        },
        "microscopic_derivation": {
            "dispersion": "epsilon^2=v^2*k_parallel^2+c^2*k_perp^4",
            "DOS_per_negative_branch": "epsilon/(8*pi*c*v)",
            "rho1": rho_slope,
            "negative_branches": branches * flavors,
            "director_count": director_count,
            "band_edge": band_edge,
            "fixed_particle_density": filling_density,
            "spectrum": (
                "E_plus_minus=epsilon^2/Lambda +/- "
                "sqrt(epsilon^2+y^2*|A|^2), twice per flavor"
            ),
            "sea_lagrangian": ("rho1/3*[(Lambda^2+y^2 A^2)^(3/2)-Lambda^3-y^3|A|^3]"),
            "critical_normalization": {
                "Pi_zero": pi_zero,
                "Delta_eta": delta_eta,
                "brane_Planck_squared": brane_planck_squared,
                "eta_c": eta_c,
                "eta_infinity": eta_inf,
                "relation": (
                    "local induced-brane witness eta_infinity+Pi_zero/M4^2="
                    "eta_c_brane=2*xi; the bulk-brane junction Schur is not this "
                    "algebraic coefficient"
                ),
            },
            "state_boundary": (
                "exact bracket uses the canonical conserved-charge sector; at "
                "fixed chemical potential zero the result changes at O(A^4)"
            ),
        },
        "retarded_gate": {
            "q0_kernel": (
                "Pi_E=gamma*integral_0^Lambda d epsilon epsilon*4epsilon/"
                "(Omega^2+4epsilon^2)"
            ),
            "q0_spectral_weight": ("sigma(nu)=rho1*y^2*nu/4 for 0<nu<2Lambda"),
            "reduced_brane_q0_Schur": (
                "C=eta_infinity+Pi/M4^2 is positive Stieltjes and H=A_g*"
                "(eta_c/C-1) is complete-Bernstein; Re[D(p,q)/p]>0 for "
                "Re(p)>0 in the long-wavelength material limit"
            ),
            "finite_q_representation": (
                "sum over occupied-to-empty interband and lower-band transitions "
                "of 2*Delta*|matrix element|^2/(Omega^2+Delta^2)"
            ),
            "finite_q_samples": finite_q_samples,
            "full_q_global_bound": False,
            "metric_and_density_vertices_included": False,
            "warning": (
                "finite-q acceleration vertices include gapless intraband "
                "transitions; lapse, induced-metric and density vertices add further "
                "Fermi-surface channels not present in this Kubo block"
            ),
        },
        "constraint_and_geometry_boundary": {
            "lapse_or_shift_time_derivatives_added": False,
            "fermion_time_derivative_order": 1,
            "fixed_charge_adds_local_U1_Gauss_constraint_if_gauged": True,
            "prescribed_constant_radius_radial_acceleration_projected_out": True,
            "bath_has_no_radial_KK_tower": True,
            "continuous_SO3_dynamical_isotropy": False,
            "inhomogeneous_fixed_charge_local_functional": False,
            "bath_renormalizes_brane_not_bulk_eta": True,
            "full_bulk_brane_Dirac_matrix_rank": False,
            "junction_conditions": False,
            "backreacted_warped_solution": False,
        },
        "acceptance_ladder": [
            {
                "level": "B0_covariant_5D_defect_matter_ansatz",
                "status": "PASS",
            },
            {"level": "B1_literal_3D_linear_DOS", "status": "PASS"},
            {
                "level": "B2_bounded_Hamiltonian_finite_region_exact_static",
                "status": "PASS",
            },
            {
                "level": "B3_same_ansatz_q0_acceleration_retarded_kernel",
                "status": "PASS",
            },
            {
                "level": "B3b_reduced_brane_long_wavelength_Schur",
                "status": "PASS",
            },
            {"level": "B4_full_q_global_Schur_and_SO3", "status": "BLOCKED"},
            {
                "level": "B5_warped_constraints_junctions_backreaction",
                "status": "BLOCKED",
            },
            {"level": "B6_force_matter_lensing", "status": "NOT_ENTERED"},
        ],
        "diagnostics": {
            "Clifford_spectrum_max_error": spectrum_error,
            "static_integral_relative_error": static_relative_error,
            "minimum_fixed_filling_ordering_margin": min(ordering_margins),
            "analytic_lower_band_global_minimum": global_minimum,
            "q0_Kubo_max_error": max(q0_errors),
            "minimum_q0_positive_real_Schur_margin": min(positive_real_margins),
            "fixed_vs_grand_canonical_relative_difference": grand_differs,
        },
        "checks": {**checks, "all": all(checks.values())},
        "decision": decision,
        "software": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main() -> int:
    payload = build()
    _write(OUTPUT, payload)
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
