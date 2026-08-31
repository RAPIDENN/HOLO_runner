#!/usr/bin/env python3
"""Derive a target-aware z=2 band-edge continuum mechanism.

The frozen compact C2 model contains seven gapped Gaussian poles and was
already killed in its declared scope.  This module tests one of the live
outside-scope classes without modifying that verdict: a zero-temperature
one-dimensional band edge with positive spectral measure and fermionic
occupation.

For a spinless continuum with

    epsilon(m) = Delta + m**2/(2 M_star),       m >= 0,

and a local chemical shift ``eta*Y``, minimization over occupations
``N_m in {0,1}`` fills precisely the modes below the band edge.  The pressure
is then

    P(Y) = (2 sqrt(2)/3) rho0 sqrt(M_star)
           [eta*Y - Delta]_+**(3/2).

Equivalently, the occupied density ``n`` is the physical selector and has
the convex energy ``W(n)=n**3/(6 M_star rho0**2)``.  Thus the cubic selector
and its sign are consequences of the quadratic band edge and occupation;
they are not inserted as a fractional-power action.

The calculation is intentionally fail-closed.  It does not claim that the
finite HOLO interval supplies this continuum, that Delta=0 is protected, or
that eta*Y, isotropy, locality, a0, causal completion, slip or lensing have
been derived from the current five-dimensional action.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PRIOR_C2 = HERE / "artifacts" / "c2_critical_continuum_gate.json"
PRIOR_PHASE_SPACE = HERE / "artifacts" / "phase_space_collector_bridge.json"
INHERITED_TARGET = HERE / "artifacts" / "nonlinear_collector_action.json"
OUTPUT = HERE / "artifacts" / "c2_band_edge_continuum.json"

SCHEMA = "holo.c2-band-edge-continuum.v1"
PRESSURE_RELATIVE_TOLERANCE = 5.0e-12
LEGENDRE_RELATIVE_TOLERANCE = 5.0e-14
SLOPE_ABSOLUTE_TOLERANCE = 2.0e-11
MAX_FINITE_LEVELS = 2_000_000


class BandEdgeInputError(ValueError):
    """A band-edge parameter or upstream certificate is malformed."""


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BandEdgeInputError(f"cannot read {path}: {exc}") from exc
    if type(value) is not dict:
        raise BandEdgeInputError(f"{path}: expected a JSON object")
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
        raise BandEdgeInputError(f"{name} must be positive and finite")
    return result


def _nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise BandEdgeInputError(f"{name} must be nonnegative and finite")
    return result


def _finite_product(*values: float, name: str) -> float:
    """Multiply finite factors with one final binary64 range check."""

    sign = 1.0
    mantissa = 1.0
    exponent = 0
    for raw in values:
        value = float(raw)
        if not math.isfinite(value):
            raise BandEdgeInputError(f"{name} received a nonfinite factor")
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
        raise BandEdgeInputError(f"{name} is outside binary64 range") from exc
    if not math.isfinite(result):
        raise BandEdgeInputError(f"{name} is outside binary64 range")
    return result


def _finite_ratio_product(
    numerators: tuple[float, ...],
    denominators: tuple[float, ...],
    *,
    name: str,
) -> float:
    """Evaluate a product ratio without materializing extreme reciprocals."""

    sign = 1.0
    mantissa = 1.0
    exponent = 0
    for raw, direction in (
        *((value, 1) for value in numerators),
        *((value, -1) for value in denominators),
    ):
        value = float(raw)
        if not math.isfinite(value) or (direction < 0 and value == 0.0):
            raise BandEdgeInputError(f"{name} has an invalid ratio factor")
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
        raise BandEdgeInputError(f"{name} is outside binary64 range") from exc
    if not math.isfinite(result):
        raise BandEdgeInputError(f"{name} is outside binary64 range")
    return result


def excess_chemical_potential(
    y: float, *, eta: float = 1.0, delta: float = 0.0
) -> float:
    """Return ``mu=eta*Y-Delta`` in natural units."""

    y = float(y)
    if not math.isfinite(y):
        raise BandEdgeInputError("y must be finite")
    eta = _positive(eta, "eta")
    delta = _nonnegative(delta, "delta")
    product = _finite_product(eta, y, name="chemical shift")
    result = product - delta
    if not math.isfinite(result):
        raise BandEdgeInputError("excess chemical potential is outside range")
    return result


def fermi_edge(
    y: float,
    *,
    mass: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
) -> float:
    """Return the occupied edge ``m_F=sqrt(2 M [eta Y-Delta]_+)``."""

    mass = _positive(mass, "mass")
    mu = excess_chemical_potential(y, eta=eta, delta=delta)
    return _finite_product(
        math.sqrt(2.0),
        math.sqrt(mass),
        math.sqrt(max(mu, 0.0)),
        name="Fermi edge",
    )


def band_edge_pressure(
    y: float,
    *,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
) -> float:
    """Return the exact zero-temperature pressure of the half-line band."""

    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    mu = excess_chemical_potential(y, eta=eta, delta=delta)
    if mu <= 0.0:
        return 0.0
    return _finite_product(
        2.0 * math.sqrt(2.0) / 3.0,
        rho0,
        math.sqrt(mass),
        mu,
        math.sqrt(mu),
        name="band-edge pressure",
    )


def selector_density(
    y: float,
    *,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
) -> float:
    """Return ``n=rho0*m_F=dP/d(eta*Y)``."""

    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    mu = excess_chemical_potential(y, eta=eta, delta=delta)
    if mu <= 0.0:
        return 0.0
    return _finite_product(
        rho0,
        math.sqrt(2.0),
        math.sqrt(mass),
        math.sqrt(mu),
        name="selector density",
    )


def equilibrium_grand_potential(
    y: float,
    *,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
) -> float:
    """Return the minimized stable-bath potential ``Omega_star=-P``."""

    return -band_edge_pressure(
        y, mass=mass, rho0=rho0, eta=eta, delta=delta
    )


def equilibrium_y_curvature(
    y: float,
    *,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
) -> float:
    """Return ``d^2 Omega_star/dY^2`` on the occupied branch.

    Strict stability in density makes this quantity negative.  This is the
    executable sign obstruction, not a convention inferred from the plotted
    positive pressure.
    """

    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    eta = _positive(eta, "eta")
    mu = excess_chemical_potential(y, eta=eta, delta=delta)
    if mu <= 0.0:
        raise BandEdgeInputError("curvature is defined only above the band edge")
    return _finite_product(
        -1.0 / math.sqrt(2.0),
        eta,
        eta,
        rho0,
        math.sqrt(mass),
        1.0 / math.sqrt(mu),
        name="equilibrium curvature",
    )


def selector_energy(
    density: float, *, mass: float = 1.0, rho0: float = 1.0
) -> float:
    """Return the filled-sea energy ``W(n)=n^3/(6 M rho0^2)``."""

    density = _nonnegative(density, "density")
    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    return _finite_ratio_product(
        (density, density, density),
        (6.0, mass, rho0, rho0),
        name="selector energy",
    )


def grand_potential(
    density: float,
    y: float,
    *,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
    attraction: float = 0.0,
) -> float:
    """Return ``Omega=W-g*n^2/2+(Delta-eta*Y)n``.

    ``attraction`` is zero for the declared candidate.  Positive values are
    exposed only to prove that an interior fold is a metastable spinodal and
    not the clean equilibrium onset.
    """

    density = _nonnegative(density, "density")
    attraction = _nonnegative(attraction, "attraction")
    mu = excess_chemical_potential(y, eta=eta, delta=delta)
    terms = [selector_energy(density, mass=mass, rho0=rho0)]
    if attraction > 0.0 and density > 0.0:
        terms.append(
            _finite_product(
                -0.5,
                attraction,
                density,
                density,
                name="attractive grand-potential term",
            )
        )
    if mu != 0.0 and density > 0.0:
        terms.append(
            _finite_product(
                -1.0, mu, density, name="chemical grand-potential term"
            )
        )
    result = math.fsum(terms)
    if not math.isfinite(result):
        raise BandEdgeInputError("grand potential is outside binary64 range")
    return result


def normalized_selector(
    density: float,
    *,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
) -> float:
    """Map the physical density to ``s`` with saddle ``s=sqrt(Y-Yc)``."""

    density = _nonnegative(density, "density")
    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    eta = _positive(eta, "eta")
    return _finite_ratio_product(
        (density,),
        (rho0, math.sqrt(2.0), math.sqrt(mass), math.sqrt(eta)),
        name="normalized selector",
    )


def selector_prefactor(
    *, mass: float = 1.0, rho0: float = 1.0, eta: float = 1.0
) -> float:
    """Return ``B=sqrt(2) rho0 sqrt(M) eta^(3/2)``."""

    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    eta = _positive(eta, "eta")
    return _finite_product(
        math.sqrt(2.0),
        rho0,
        math.sqrt(mass),
        eta,
        math.sqrt(eta),
        name="selector prefactor",
    )


def wire_spectral_density(
    total_length_per_volume: float, *, degeneracy: int = 1
) -> float:
    """Return the folded 1D density ``rho0=g*Lwire/(pi*V)``.

    A full spinless wire has measure ``dk/(2*pi)``.  Folding the two states
    ``k=+m`` and ``k=-m`` onto ``m>=0`` gives ``dm/pi``.  This is a finite
    material realization when the total wire length per three-volume is
    finite; it is not a derivation from a decompactified HOLO coordinate.
    """

    length_density = _positive(total_length_per_volume, "total_length_per_volume")
    if type(degeneracy) is not int or degeneracy < 1:
        raise BandEdgeInputError("degeneracy must be a positive integer")
    return _finite_product(
        degeneracy,
        length_density,
        1.0 / math.pi,
        name="wire spectral density",
    )


def numerical_spectral_pressure(
    y: float,
    *,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
    intervals: int = 4096,
) -> float:
    """Integrate the occupied continuum by composite Simpson quadrature."""

    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    if type(intervals) is not int or intervals < 2 or intervals % 2:
        raise BandEdgeInputError("intervals must be an even integer >= 2")
    mu = excess_chemical_potential(y, eta=eta, delta=delta)
    if mu <= 0.0:
        return 0.0
    grid = np.linspace(0.0, 1.0, intervals + 1, dtype=float)
    values = 1.0 - np.square(grid)
    dimensionless_integral = (
        1.0
        / (3.0 * intervals)
        * (
            values[0]
            + values[-1]
            + 4.0 * np.sum(values[1:-1:2])
            + 2.0 * np.sum(values[2:-1:2])
        )
    )
    return _finite_product(
        rho0,
        mu,
        math.sqrt(2.0),
        math.sqrt(mass),
        math.sqrt(mu),
        float(dimensionless_integral),
        name="numerical spectral pressure",
    )


def finite_spacing_pressure(
    y: float,
    *,
    spacing: float,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
) -> float:
    """Return the compact Riemann sum with levels ``m_j=j*spacing``.

    The zero mode makes the finite system linear immediately above threshold;
    the exact three-halves onset exists only after the continuum limit is
    taken before ``Y -> Yc``.
    """

    spacing = _positive(spacing, "spacing")
    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    mu = excess_chemical_potential(y, eta=eta, delta=delta)
    if mu <= 0.0:
        return 0.0
    edge = fermi_edge(y, mass=mass, eta=eta, delta=delta)
    index_ratio = edge / spacing
    if not math.isfinite(index_ratio) or index_ratio >= MAX_FINITE_LEVELS:
        raise BandEdgeInputError(
            f"finite spectrum exceeds the {MAX_FINITE_LEVELS} level audit cap"
        )
    maximum_index = int(math.floor(index_ratio))
    relative_levels = (spacing / edge) * np.arange(
        maximum_index + 1, dtype=float
    )
    # rho0 is the continuum density after folding k=+m and k=-m.  On a
    # finite periodic wire the isolated k=0 state has no partner, so its
    # trapezoidal endpoint weight is one half.
    weights = np.ones_like(relative_levels)
    weights[0] = 0.5
    dimensionless_sum = float(
        np.sum(
            weights * np.maximum(1.0 - np.square(relative_levels), 0.0)
        )
    )
    return _finite_product(
        rho0,
        spacing,
        mu,
        dimensionless_sum,
        name="finite-spacing pressure",
    )


def density_of_states_power(alpha: float, dynamic_exponent: float) -> float:
    """Return ``1+(alpha+1)/z`` for rho~m^alpha and epsilon~m^z."""

    alpha = float(alpha)
    dynamic_exponent = float(dynamic_exponent)
    if not math.isfinite(alpha) or alpha <= -1.0:
        raise BandEdgeInputError("alpha must be finite and greater than -1")
    if not math.isfinite(dynamic_exponent) or dynamic_exponent <= 0.0:
        raise BandEdgeInputError("dynamic_exponent must be positive and finite")
    return 1.0 + (alpha + 1.0) / dynamic_exponent


def attractive_fold(
    attraction: float,
    *,
    mass: float = 1.0,
    rho0: float = 1.0,
    eta: float = 1.0,
    delta: float = 0.0,
) -> dict[str, float]:
    """Return spinodal and coexistence points for an added ``-g n^2/2``."""

    attraction = _positive(attraction, "attraction")
    mass = _positive(mass, "mass")
    rho0 = _positive(rho0, "rho0")
    eta = _positive(eta, "eta")
    delta = _nonnegative(delta, "delta")
    scale = attraction**2 * mass * rho0**2
    return {
        "spinodal_density": attraction * mass * rho0**2,
        "spinodal_y": (delta - 0.5 * scale) / eta,
        "coexistence_density": 1.5 * attraction * mass * rho0**2,
        "coexistence_y": (delta - 0.375 * scale) / eta,
    }


def build() -> dict[str, Any]:
    prior_c2 = _read(PRIOR_C2)
    prior_phase_space = _read(PRIOR_PHASE_SPACE)
    inherited_target = _read(INHERITED_TARGET)
    if prior_c2.get("schema") != "holo.c2-critical-continuum-gate.v1":
        raise BandEdgeInputError("unexpected prior C2 schema")
    if prior_c2.get("decision", {}).get("kill_all_critical_continuum_models") is not False:
        raise BandEdgeInputError("prior C2 did not preserve outside-scope continua")
    if "decompactified_gapless_continuum" not in prior_c2.get(
        "outside_scope_live_classes", []
    ):
        raise BandEdgeInputError("prior C2 does not expose the tested live class")
    if prior_phase_space.get("schema") != "holo.phase-space-collector-bridge.v1":
        raise BandEdgeInputError("unexpected phase-space bridge schema")
    if inherited_target.get("schema") != "holo.nonlinear-collector-action-target.v1":
        raise BandEdgeInputError("unexpected inherited collector target schema")
    if inherited_target.get("source", {}).get("fit_origin") != (
        "SPARC training split only"
    ):
        raise BandEdgeInputError("inherited target genealogy is not explicit")

    mass = 1.7
    rho0 = 0.8
    eta = 1.3
    delta = 0.0
    y_values = np.geomspace(1.0e-12, 1.0e-2, 41)
    analytic = np.asarray(
        [
            band_edge_pressure(
                value, mass=mass, rho0=rho0, eta=eta, delta=delta
            )
            for value in y_values
        ]
    )
    numeric = np.asarray(
        [
            numerical_spectral_pressure(
                value, mass=mass, rho0=rho0, eta=eta, delta=delta
            )
            for value in y_values
        ]
    )
    pressure_relative = float(np.max(np.abs(numeric / analytic - 1.0)))
    pressure_slope = float(np.polyfit(np.log(y_values), np.log(analytic), 1)[0])

    legendre_errors: list[float] = []
    selector_errors: list[float] = []
    prefactor = selector_prefactor(mass=mass, rho0=rho0, eta=eta)
    for y_value, pressure_value in zip(y_values, analytic, strict=True):
        density = selector_density(
            y_value, mass=mass, rho0=rho0, eta=eta, delta=delta
        )
        dual = (
            eta * y_value * density
            - selector_energy(density, mass=mass, rho0=rho0)
        )
        legendre_errors.append(abs(dual / pressure_value - 1.0))
        selector = normalized_selector(
            density, mass=mass, rho0=rho0, eta=eta
        )
        selector_errors.append(abs(selector / math.sqrt(y_value) - 1.0))

    spacings = [0.2, 0.05, 0.0125]
    finite_rows = []
    finite_probe_y = 0.4
    continuum_probe = band_edge_pressure(
        finite_probe_y, mass=mass, rho0=rho0, eta=eta, delta=delta
    )
    for spacing in spacings:
        discrete = finite_spacing_pressure(
            finite_probe_y,
            spacing=spacing,
            mass=mass,
            rho0=rho0,
            eta=eta,
            delta=delta,
        )
        finite_rows.append(
            {
                "spacing": spacing,
                "pressure": discrete,
                "relative_error_to_continuum": abs(discrete / continuum_probe - 1.0),
                "first_excited_threshold_above_yc": spacing**2 / (2.0 * mass * eta),
            }
        )

    fold = attractive_fold(
        0.4, mass=mass, rho0=rho0, eta=eta, delta=0.3
    )
    spinodal_curvature = (
        fold["spinodal_density"] / (mass * rho0**2) - 0.4
    )
    coexistence_omega = grand_potential(
        fold["coexistence_density"],
        fold["coexistence_y"],
        mass=mass,
        rho0=rho0,
        eta=eta,
        delta=0.3,
        attraction=0.4,
    )
    sign_probe_y = 0.37
    sign_curvature = equilibrium_y_curvature(
        sign_probe_y, mass=mass, rho0=rho0, eta=eta, delta=delta
    )

    maximum_legendre_error = float(max(legendre_errors))
    maximum_selector_error = float(max(selector_errors))
    checks = {
        "prior_compact_C2_kill_is_scoped": True,
        "positive_spectral_measure": rho0 > 0.0,
        "quadratic_band_edge": mass > 0.0,
        "occupation_integral_matches_closed_form": pressure_relative
        <= PRESSURE_RELATIVE_TOLERANCE,
        "deep_log_slope_is_three_halves": abs(pressure_slope - 1.5)
        <= SLOPE_ABSOLUTE_TOLERANCE,
        "density_legendre_transform_closes": maximum_legendre_error
        <= LEGENDRE_RELATIVE_TOLERANCE,
        "physical_density_is_square_root_selector": maximum_selector_error
        <= LEGENDRE_RELATIVE_TOLERANCE,
        "z2_constant_measure_selects_three_halves": math.isclose(
            density_of_states_power(0.0, 2.0), 1.5, rel_tol=0.0, abs_tol=1.0e-15
        ),
        "z1_constant_measure_does_not": math.isclose(
            density_of_states_power(0.0, 1.0), 2.0, rel_tol=0.0, abs_tol=1.0e-15
        ),
        "finite_spacing_converges_at_fixed_y": all(
            finite_rows[index + 1]["relative_error_to_continuum"]
            < finite_rows[index]["relative_error_to_continuum"]
            for index in range(len(finite_rows) - 1)
        ),
        "attractive_fold_is_a_spinodal": abs(spinodal_curvature) < 1.0e-14,
        "coexistence_follows_spinodal_and_preempts_clean_onset": fold[
            "coexistence_y"
        ]
        > fold["spinodal_y"],
        "coexistence_free_energy_closes": abs(coexistence_omega) < 1.0e-14,
        "stable_bath_susceptibility_has_opposite_target_sign": sign_curvature < 0.0,
        "no_raw_observational_table_read_directly": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "explicit_positive_measure_occupation_problem": True,
        "selector_is_physical_number_density": True,
        "stable_convex_zero_temperature_onset": True,
        "fractional_power_inserted_by_hand": False,
        "current_finite_HOLO_interval_decompactified": False,
        "finite_four_dimensional_spectral_density_derived_from_HOLO": False,
        "gap_Delta_zero_protected_by_current_action": False,
        "z2_dispersion_and_single_component_occupation_protected": False,
        "eta_times_Y_vertex_derived_from_current_5d_action": False,
        "required_AQUAL_variational_sign_derived": False,
        "uniform_local_density_approximation_at_onset": False,
        "isotropic_stress_tensor_derived": False,
        "causal_relativistic_completion_derived": False,
        "a0_normalization_derived": False,
        "lensing_and_gravitational_slip_derived": False,
        "current_HOLO_physical_completion": False,
    }

    return {
        "schema": SCHEMA,
        "title": "Quadratic band-edge occupation mechanism for a three-halves response",
        "classification": (
            "exact_band_edge_exponent_with_stable_thermodynamics;"
            "wrong_AQUAL_variational_sign_and_no_current_holo_embedding"
        ),
        "sources": {
            "prior_compact_c2_gate": {
                "path": str(PRIOR_C2.relative_to(REPO)),
                "sha256": _sha256(PRIOR_C2),
            },
            "prior_phase_space_diagnostic": {
                "path": str(PRIOR_PHASE_SPACE.relative_to(REPO)),
                "sha256": _sha256(PRIOR_PHASE_SPACE),
            },
            "inherited_exposed_target": {
                "path": str(INHERITED_TARGET.relative_to(REPO)),
                "sha256": _sha256(INHERITED_TARGET),
            },
            "raw_observational_tables_read_directly": [],
            "inherited_exposed_target_origin": inherited_target["source"]
            ["fit_origin"],
        },
        "microscopic_occupation_problem": {
            "hamiltonian_density": (
                "Omega=min_{N_m in {0,1}} integral_0^infinity rho0 dm "
                "N_m[Delta+m^2/(2M_star)-eta Y]"
            ),
            "spectral_measure": "rho(m) dm=rho0 dm with rho0>0",
            "dispersion": "epsilon(m)=Delta+m^2/(2M_star)",
            "occupation_rule": "N_m=1 iff m<m_F=sqrt(2M_star[eta Y-Delta]_+)",
            "pressure": (
                "P=-Omega=(2sqrt(2)/3)rho0 sqrt(M_star)"
                "[eta Y-Delta]_+^(3/2)"
            ),
            "selector": "n=rho0*m_F is occupied number density, not a fitted radius",
            "selector_energy": "W(n)=n^3/(6M_star rho0^2)",
            "compressibility": (
                "d(eta Y-Delta)/dn=n/(M_star rho0^2)>0 for n>0"
            ),
        },
        "normalized_tricritical_map": {
            "definition": (
                "s=n/[rho0 sqrt(2M_star eta)], "
                "B=sqrt(2)rho0 sqrt(M_star)eta^(3/2), Yc=Delta/eta"
            ),
            "grand_potential": "Omega=B[s^3/3-s(Y-Yc)]",
            "stationary_selector": "s=sqrt(Y-Yc) for Y>Yc",
            "onshell_pressure": "P=(2B/3)[Y-Yc]_+^(3/2)",
            "interpretation": (
                "The q6-like cubic cost in s and q2Y-like conjugate term arise "
                "from filled z=2 states when s is identified with density."
            ),
        },
        "variational_sign_audit": {
            "stable_minimization": (
                "Omega(n,Y)=W(n)-eta*Y*n has Omega_nn=W''>0; at its "
                "minimum Omega_star(Y)=-P(Y)."
            ),
            "induced_static_actions": (
                "Gamma_E=beta*V*Omega_star=-beta*V*P, while the static "
                "Lorentzian density is L_gas=+P and H_gas=-P."
            ),
            "required_target_sign": (
                "The repository target is L_target=-C*P and H_target=+C*P "
                "for C=M_Pl^2*a0^2>0."
            ),
            "susceptibility_no_go": (
                "d2 Omega_star/dY2=-eta^2/W''<0 on every strictly stable "
                "interior branch, whereas the target energy requires +C*P_YY>0."
            ),
            "sign_flip_failure": (
                "Changing the chemical coupling to +eta*Y*n leaves the empty "
                "minimum for Y>0; reversing determinant multiplicity or "
                "occupation would abandon a stable positive-norm gas."
            ),
            "verdict": "FAIL_REQUIRED_AQUAL_VARIATIONAL_SIGN",
        },
        "scaling_selection": {
            "general_rule": (
                "rho(m)~m^alpha and epsilon-Delta~m^z imply "
                "P~[Y-Yc]^[1+(alpha+1)/z]"
            ),
            "constant_measure_z2_power": density_of_states_power(0.0, 2.0),
            "constant_measure_z1_power": density_of_states_power(0.0, 1.0),
            "meaning": (
                "Changing the dispersion or material changes the exponent; the "
                "three-halves value is selected specifically by alpha=0,z=2."
            ),
        },
        "diagnostics": {
            "parameters": {
                "M_star": mass,
                "rho0": rho0,
                "eta": eta,
                "Delta": delta,
            },
            "maximum_pressure_integral_relative_error": pressure_relative,
            "pressure_log_slope": pressure_slope,
            "maximum_legendre_relative_error": maximum_legendre_error,
            "maximum_selector_relative_error": maximum_selector_error,
            "selector_prefactor_B": prefactor,
            "finite_spacing_rows": finite_rows,
            "attractive_deformation": {
                **fold,
                "spinodal_curvature": spinodal_curvature,
                "coexistence_grand_potential": coexistence_omega,
            },
            "stable_bath_d2_Omega_star_dY2": sign_curvature,
        },
        "finite_size_and_fold_adjudication": {
            "clean_onset": (
                "At Delta=0 and zero attraction the boundary n=0 is stable for "
                "Y<=0; for Y>0 a unique stable n~sqrt(Y) branch appears."
            ),
            "ift_status": (
                "W''(0)=0, so the inverse map is nonanalytic at the band edge; "
                "this is a boundary onset, not two physical branches crossing."
            ),
            "interior_fold_no_go": (
                "For Omega=W(n)-eta Yn with eta>0 and strict equilibrium "
                "stability W''>0, dY/dn=W''/eta>0; a stable interior fold is impossible."
            ),
            "attractive_result": (
                "As Y increases, adding -g n^2/2 first creates a metastable "
                "high-density branch at the spinodal; coexistence occurs later "
                "but before the n=0 clean onset, so the equilibrium transition "
                "is first order."
            ),
            "compact_result": (
                "Finite level spacing gives a linear zero-mode segment and steps; "
                "the continuum limit must precede the deep-edge limit."
            ),
        },
        "dimensional_contract": {
            "natural_units": "hbar=c=1",
            "dimensions": {
                "Y": "dimensionless by convention",
                "eta_Delta_M_star_m": "mass",
                "n": "mass^3",
                "rho0": "mass^2 so rho0*dm is a number density",
                "W_P_B": "mass^4",
                "attraction_g": "mass^-2",
            },
            "candidate_scale_relation": (
                "If and only if this sector is the full target density, "
                "M_Pl^2 a0^2=B=sqrt(2)rho0 sqrt(M_star)eta^(3/2)."
            ),
            "scale_status": "relation derived; none of rho0,M_star,eta is selected by current HOLO",
        },
        "candidate_realizations_not_yet_HOLO_derivations": [
            {
                "class": "spinless_quantum_wire_or_Tonks_network",
                "rho0": "g times total wire length per three-volume divided by pi",
                "state_counting": "dk/(2pi) on the full wire folds to dm/pi for m=abs(k)",
                "advantage": (
                    "finite positive density; the cubic low-density energy is "
                    "exact for free spinless fermions and isolated impenetrable "
                    "Tonks segments"
                ),
                "open_gate": (
                    "junctions can spoil the Tonks map; isotropic network stress, "
                    "universal density and eta Y coupling remain unproved"
                ),
            },
            {
                "class": "decompactified_radial_or_internal_channel",
                "rho0": "not finite in 4D until a normalized channel density is derived",
                "advantage": "a one-dimensional quadratic spectrum is kinematically available",
                "open_gate": (
                    "a bare 5D KK continuum supplies neither fermionic occupation "
                    "nor a finite 4D density; ordinary three-momentum dispersion "
                    "also changes the density-of-states exponent"
                ),
            },
        ],
        "kill_criteria": [
            {
                "id": "K1_nonzero_unprotected_gap",
                "kill_if": "Delta is nonzero or unprotected, producing Yc=Delta/eta.",
                "current_result": "OPEN_FAIL_CURRENT_HOLO_HAS_NO_PROTECTION",
            },
            {
                "id": "K2_finite_level_spacing",
                "kill_if": "The physical spectrum remains compact/discrete in the required deep window.",
                "current_result": "FAIL_FOR_CURRENT_FINITE_HOLO_INTERVAL",
            },
            {
                "id": "K3_dispersion_or_measure_runs",
                "kill_if": "Interactions or geometry change alpha=0,z=2 in the infrared.",
                "current_result": "NOT_EVALUATED",
            },
            {
                "id": "K4_thermal_rounding",
                "kill_if": "T is not much smaller than eta*abs(Y-Yc) in the claimed window.",
                "current_result": "NOT_EVALUATED",
            },
            {
                "id": "K5_local_density_breakdown",
                "kill_if": "The variation length is not large compared with 1/m_F.",
                "current_result": "NOT_UNIFORMLY_SATISFIED_AT_ONSET",
            },
            {
                "id": "K6_wrong_conjugate_operator",
                "kill_if": "The same microscopic action does not derive eta*Y as the chemical shift.",
                "current_result": "NOT_DERIVED_FROM_CURRENT_HOLO",
            },
            {
                "id": "K7_anisotropy_or_bad_stress",
                "kill_if": "The channel realization leaves unacceptable preferred-direction stress or instability.",
                "current_result": "NOT_EVALUATED",
            },
            {
                "id": "K8_tensor_or_causality_failure",
                "kill_if": "Embedding the response creates a vanishing tensor coefficient, ghost, gradient instability or acausality.",
                "current_result": "NOT_EVALUATED",
            },
            {
                "id": "K9_wrong_variational_sign",
                "kill_if": (
                    "Stable occupation induces +P in the Lorentzian density "
                    "rather than the required -P."
                ),
                "current_result": "TRIGGERED",
            },
        ],
        "checks": checks,
        "physical_gates": physical_gates,
        "decision": {
            "verdict": "KILL_C2_BAND_EDGE_WRONG_VARIATIONAL_SIGN",
            "tested_live_C2_class": True,
            "kills_prior_scoped_compact_verdict": False,
            "exact_exponent_and_positive_pressure_derived": True,
            "required_AQUAL_variational_sign_derived": False,
            "candidate_survives": False,
            "current_holo_mechanism_candidate": False,
            "physical_completion": False,
            "new_force_derived": False,
            "lensing_derived": False,
            "next_action": (
                "Do not repair this equilibrium bath by flipping multiplicity. "
                "Test a constrained geometric sector whose static sign follows "
                "from the gravitational constraint, with tensor and Dirac gates "
                "evaluated before any phenomenological comparison."
            ),
        },
        "evidence_boundary": (
            "This theory calculation derives a convex stable "
            "band-edge occupation problem, its positive pressure, the three-halves "
            "power and a physical density selector. It reads no raw observation "
            "table, but its exposed acceptance target inherits a SPARC training "
            "fit through the phase-space bridge. It fails the variational sign "
            "required by AQUAL, so this candidate is killed rather than repaired. "
            "It is not an "
            "embedding in the current finite HOLO geometry, a force, "
            "a lensing prediction, an observation or a publication claim."
        ),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    if result["checks"]["all"] is not True:
        raise RuntimeError("band-edge algebra checks failed")
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(f"[verdict] {result['decision']['verdict']}")
    print("[scope] exact exponent; wrong AQUAL sign; candidate killed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
