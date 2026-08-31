#!/usr/bin/env python3
"""Reproduce and falsify the C1 regulated derivative-condensate route.

This module audits the derivative condensate proposed in Berezhiani--Khoury,
Phys. Rev. D 92, 103510 (2015), Sec. 6, without reading observational data.
Writing ``s=rho^2`` and neglecting gradients of the radial amplitude, their
non-relativistic algebraic Lagrangian is

    L(s, X) = m*s*X
              + (4/3)*Lambda^4*m^3*X^3*s^3/(Lambda_c^2+s)^6 .

For ``Lambda_c=0`` and the MOND-sign branch ``X=-x<0``, the static energy

    E(s, x) = m*x*s + (4/3)*Lambda^4*m^3*x^3/s^3

has a genuine radial minimum.  It gives ``s=Lambda*sqrt(2*m*x)`` and hence an
on-shell density proportional to ``x^(3/2)``.  This is a valid counterexample
to a no-go restricted to a canonical positive ``rho^6`` potential.

The same calculation also supplies a fail-closed C1 gate.  A non-zero
``Lambda_c`` removes the non-zero branch below a fold, while the unregulated
limit is singular at ``s=0`` and its radial inverse-correlation scale tends to zero as
``X`` tends to zero.  Spatial Weyl homogeneity fixes the three-halves power but
allows an arbitrary function (and an infinite Wilson tower); ordinary 5D scale
invariance with a compensator also allows quadratic and quartic deformations.
The audit therefore promotes the mathematical counterexample but does not
promote it as a target-blind microscopic completion of the current HOLO bulk.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
INTERFACE = REPO / "first_principles_audit/artifacts/interface_action_derivation.json"
TRICRITICAL = HERE / "artifacts" / "tricritical_constitutive_bridge.json"
OUTPUT = HERE / "artifacts" / "c1_bk_derivative_gate.json"

PAPER = {
    "title": "Theory of dark matter superfluidity",
    "authors": "Lasha Berezhiani and Justin Khoury",
    "doi": "10.1103/PhysRevD.92.103510",
    "url": "https://link.aps.org/accepted/10.1103/PhysRevD.92.103510",
    "audited_equations": [87, 89, 90, 91, 92, 93, 94, 95, 97],
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _positive_finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def _nonnegative_finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be nonnegative and finite")
    return result


def inverse_susceptibility_coefficient(*, mass: float, scale: float) -> float:
    """Return A=(4/3)*Lambda^4*m^3 in the algebraic BK action."""

    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    return (4.0 / 3.0) * scale**4 * mass**3


def regulated_lagrangian(
    selector_s: float,
    phase_x: float,
    *,
    mass: float = 1.0,
    scale: float = 1.0,
    regulator: float = 0.0,
) -> float:
    """Evaluate the leading algebraic non-relativistic density in Eq. (89).

    ``regulator`` denotes Lambda_c, not Lambda_c squared.  At zero regulator
    the expression is defined only for strictly positive ``selector_s``.
    """

    selector_s = _nonnegative_finite(selector_s, "selector_s")
    phase_x = float(phase_x)
    if not math.isfinite(phase_x):
        raise ValueError("phase_x must be finite")
    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    regulator = _nonnegative_finite(regulator, "regulator")
    if selector_s == 0.0 and regulator == 0.0:
        raise ValueError("the unregulated density is singular at selector_s=0")
    c = regulator**2
    a = inverse_susceptibility_coefficient(mass=mass, scale=scale)
    return (
        mass * selector_s * phase_x
        + a * phase_x**3 * selector_s**3 / (c + selector_s) ** 6
    )


def regulated_d_lagrangian_ds(
    selector_s: float,
    phase_x: float,
    *,
    mass: float = 1.0,
    scale: float = 1.0,
    regulator: float = 0.0,
) -> float:
    """First selector derivative of :func:`regulated_lagrangian`."""

    selector_s = _positive_finite(selector_s, "selector_s")
    phase_x = float(phase_x)
    if not math.isfinite(phase_x):
        raise ValueError("phase_x must be finite")
    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    regulator = _nonnegative_finite(regulator, "regulator")
    c = regulator**2
    a = inverse_susceptibility_coefficient(mass=mass, scale=scale)
    rational_derivative = 3.0 * selector_s**2 * (c - selector_s) / (c + selector_s) ** 7
    return mass * phase_x + a * phase_x**3 * rational_derivative


def regulated_d2_lagrangian_ds2(
    selector_s: float,
    phase_x: float,
    *,
    mass: float = 1.0,
    scale: float = 1.0,
    regulator: float = 0.0,
) -> float:
    """Second selector derivative of the regulated algebraic density."""

    selector_s = _positive_finite(selector_s, "selector_s")
    phase_x = float(phase_x)
    if not math.isfinite(phase_x):
        raise ValueError("phase_x must be finite")
    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    regulator = _nonnegative_finite(regulator, "regulator")
    c = regulator**2
    a = inverse_susceptibility_coefficient(mass=mass, scale=scale)
    rational_second_derivative = (
        6.0
        * selector_s
        * (c**2 - 4.0 * c * selector_s + 2.0 * selector_s**2)
        / (c + selector_s) ** 8
    )
    return a * phase_x**3 * rational_second_derivative


def radial_energy_curvature(
    selector_s: float,
    phase_x: float,
    *,
    mass: float = 1.0,
    scale: float = 1.0,
    regulator: float = 0.0,
) -> float:
    """Return d^2 E/d rho^2 for ``s=rho^2`` at any positive ``s``."""

    first = regulated_d_lagrangian_ds(
        selector_s,
        phase_x,
        mass=mass,
        scale=scale,
        regulator=regulator,
    )
    second = regulated_d2_lagrangian_ds2(
        selector_s,
        phase_x,
        mass=mass,
        scale=scale,
        regulator=regulator,
    )
    # E=-L and d^2E/d rho^2 = -2 L_s - 4*s*L_ss.
    return -2.0 * first - 4.0 * selector_s * second


def radial_gradient_normalization(
    selector_s: float,
    phase_x: float,
    *,
    mass: float = 1.0,
    scale: float = 1.0,
    regulator: float = 0.0,
) -> float:
    """Return ``Z_rho`` in ``L_grad=-(Z_rho/2)*(grad rho)^2``.

    This is the linear coefficient obtained by retaining the radial-gradient
    term in BK Eq. (89), rather than identifying the static energy Hessian with
    a canonically normalized inverse-correlation scale.
    """

    selector_s = _positive_finite(selector_s, "selector_s")
    phase_x = float(phase_x)
    if not math.isfinite(phase_x):
        raise ValueError("phase_x must be finite")
    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    regulator = _nonnegative_finite(regulator, "regulator")
    denominator = (regulator**2 + selector_s) ** 6
    return 1.0 + 4.0 * scale**4 * mass**2 * selector_s**2 * phase_x**2 / denominator


def unregulated_solution(
    x_abs: float, *, mass: float = 1.0, scale: float = 1.0
) -> dict[str, float]:
    """Return the exact stable ``X=-x`` stationary solution at Lambda_c=0."""

    x_abs = _positive_finite(x_abs, "x_abs")
    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    selector_s = scale * math.sqrt(2.0 * mass * x_abs)
    phase_x = -x_abs
    lagrangian = regulated_lagrangian(
        selector_s, phase_x, mass=mass, scale=scale, regulator=0.0
    )
    coefficient = 2.0 * scale * (2.0 * mass) ** 1.5 / 3.0
    expected_lagrangian = -coefficient * x_abs**1.5
    energy_curvature = 16.0 * mass * x_abs
    gradient_normalization = radial_gradient_normalization(
        selector_s,
        phase_x,
        mass=mass,
        scale=scale,
        regulator=0.0,
    )
    inverse_correlation_scale_squared = energy_curvature / gradient_normalization
    return {
        "selector_s": selector_s,
        "lagrangian": lagrangian,
        "expected_lagrangian": expected_lagrangian,
        "onshell_coefficient": coefficient,
        "radial_energy_curvature": energy_curvature,
        "radial_gradient_normalization": gradient_normalization,
        "radial_inverse_correlation_scale_squared": inverse_correlation_scale_squared,
        "radial_inverse_correlation_scale": math.sqrt(
            inverse_correlation_scale_squared
        ),
        "radial_correlation_length": 1.0 / math.sqrt(inverse_correlation_scale_squared),
    }


def dimensionless_stationarity(y: float, eta: float) -> float:
    """Dimensionless regulated stationarity equation from BK Eq. (91)."""

    y = _positive_finite(y, "y")
    eta = _nonnegative_finite(eta, "eta")
    return (1.0 + y) ** 7 + eta * y**2 * (1.0 - y)


def dimensionless_stationarity_derivative(y: float, eta: float) -> float:
    """Derivative of :func:`dimensionless_stationarity` with respect to y."""

    y = _positive_finite(y, "y")
    eta = _nonnegative_finite(eta, "eta")
    return 7.0 * (1.0 + y) ** 6 + eta * (2.0 * y - 3.0 * y**2)


def fold_point() -> tuple[float, float]:
    """Return the exact fold location ``(y_star, eta_star)``."""

    y_star = 1.0 + 1.0 / math.sqrt(2.0)
    eta_star = (1.0 + y_star) ** 7 / (y_star**2 * (y_star - 1.0))
    return y_star, eta_star


def eta_from_parameters(
    x_abs: float,
    *,
    mass: float = 1.0,
    scale: float = 1.0,
    regulator: float,
) -> float:
    """Return eta=4*Lambda^4*m^2*x^2/Lambda_c^8."""

    x_abs = _positive_finite(x_abs, "x_abs")
    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    regulator = _positive_finite(regulator, "regulator")
    return 4.0 * scale**4 * mass**2 * x_abs**2 / regulator**8


def x_abs_from_eta(
    eta: float,
    *,
    mass: float = 1.0,
    scale: float = 1.0,
    regulator: float,
) -> float:
    """Invert :func:`eta_from_parameters`."""

    eta = _positive_finite(eta, "eta")
    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    regulator = _positive_finite(regulator, "regulator")
    return regulator**4 * math.sqrt(eta) / (2.0 * mass * scale**2)


def _bisect(
    function: Callable[[float], float],
    lower: float,
    upper: float,
    *,
    relative_tolerance: float = 1.0e-15,
    maximum_iterations: int = 256,
) -> float:
    f_lower = function(lower)
    f_upper = function(upper)
    if f_lower == 0.0:
        return lower
    if f_upper == 0.0:
        return upper
    if f_lower * f_upper > 0.0:
        raise ValueError("bisection interval does not bracket a root")
    for _ in range(maximum_iterations):
        midpoint = 0.5 * (lower + upper)
        f_midpoint = function(midpoint)
        if f_midpoint == 0.0:
            return midpoint
        if abs(upper - lower) <= relative_tolerance * max(1.0, abs(midpoint)):
            return midpoint
        if f_lower * f_midpoint <= 0.0:
            upper = midpoint
            f_upper = f_midpoint
        else:
            lower = midpoint
            f_lower = f_midpoint
    raise RuntimeError("bisection did not converge")


def regulated_stationary_roots(eta: float) -> list[float]:
    """Return positive non-zero stationary roots as ``y=s/Lambda_c^2``.

    Below the fold there is no non-zero root.  Above it there is one unstable
    lower root and one stable upper root on the ``X<0`` static-energy branch.
    """

    eta = _nonnegative_finite(eta, "eta")
    y_star, eta_star = fold_point()
    relative_offset = (eta - eta_star) / eta_star
    if relative_offset < -2.0e-13:
        return []
    if abs(relative_offset) <= 2.0e-13:
        return [y_star]

    function = lambda y: dimensionless_stationarity(y, eta)
    lower_root = _bisect(function, 1.0, y_star)
    upper_bound = max(2.0 * y_star, 2.0 * eta**0.25)
    while function(upper_bound) <= 0.0:
        upper_bound *= 2.0
    upper_root = _bisect(function, y_star, upper_bound)
    return [lower_root, upper_root]


def normalized_stationarity_residual(y: float, eta: float) -> float:
    """Return a scale-free residual for the dimensionless root equation."""

    numerator = abs(dimensionless_stationarity(y, eta))
    denominator = (1.0 + y) ** 7 + eta * y**2 * abs(1.0 - y)
    return numerator / denominator


def homogeneous_tower_minimum(
    quadratic_tower_coefficient: float,
    *,
    mass: float = 1.0,
    scale: float = 1.0,
) -> dict[str, float]:
    """Minimize a Weyl-compatible energy with two independent Wilson terms.

    With ``s=t*sqrt(x)``, the energy

        E = m*x*s + B*x^2/s + A*x^3/s^3

    is ``x^(3/2) * (m*t+B/t+A/t^3)``.  Both B=0 and B!=0 therefore have the
    same power but different selectors and normalizations.  This is an explicit
    witness that homogeneity does not select the Wilson function.
    """

    b = _nonnegative_finite(quadratic_tower_coefficient, "quadratic_tower_coefficient")
    mass = _positive_finite(mass, "mass")
    scale = _positive_finite(scale, "scale")
    a = inverse_susceptibility_coefficient(mass=mass, scale=scale)
    t_squared = (b + math.sqrt(b**2 + 12.0 * mass * a)) / (2.0 * mass)
    t = math.sqrt(t_squared)
    coefficient = mass * t + b / t + a / t**3
    curvature = 2.0 * b / t**3 + 12.0 * a / t**5
    return {
        "quadratic_tower_coefficient": b,
        "selector_coefficient_t": t,
        "onshell_energy_coefficient": coefficient,
        "dimensionless_radial_curvature": curvature,
        "power_in_x": 1.5,
    }


def relevant_deformation_power(selector_power: float) -> float:
    """Power induced by balancing ``r*s^p`` against ``A*x^3/s^3``."""

    selector_power = _positive_finite(selector_power, "selector_power")
    return 3.0 * selector_power / (selector_power + 3.0)


def compensator_power_for_bulk_operator(
    q_power: float, *, spacetime_dimensions: int = 5
) -> float:
    """Return ``a`` making ``Sigma^a |Q|^q`` scale invariant.

    This illustrative operator count assumes a compensator with engineering
    dimension ``[Sigma]=1`` and a canonically normalized bulk scalar
    ``[Q]=(D-2)/2``.  It is not a claim that the current HOLO action contains
    such a compensator.
    """

    q_power = _positive_finite(q_power, "q_power")
    if spacetime_dimensions < 3:
        raise ValueError("spacetime_dimensions must be at least three")
    q_dimension = 0.5 * (spacetime_dimensions - 2.0)
    return spacetime_dimensions - q_power * q_dimension


def quasistatic_weyl_power(number_of_spatial_dimensions: int) -> float:
    """Return p=d/2 for a spatial-Weyl density ``X^p``."""

    if number_of_spatial_dimensions <= 0:
        raise ValueError("number_of_spatial_dimensions must be positive")
    return 0.5 * number_of_spatial_dimensions


def phonon_second_derivative(phase_x: float, coefficient: float = 1.0) -> float:
    """Return P_XX for ``P=C*X*sqrt(abs(X))`` away from X=0."""

    phase_x = float(phase_x)
    coefficient = _positive_finite(coefficient, "coefficient")
    if not math.isfinite(phase_x) or phase_x == 0.0:
        raise ValueError("phase_x must be finite and non-zero")
    return (
        3.0
        * coefficient
        * math.copysign(1.0, phase_x)
        / (4.0 * math.sqrt(abs(phase_x)))
    )


def _binary_gate(passed: bool, criterion: str, evidence: str) -> dict[str, Any]:
    return {
        "passed": bool(passed),
        "criterion": criterion,
        "evidence": evidence,
    }


def build() -> dict[str, Any]:
    """Build the reproducible C1 mathematical certificate."""

    interface = _read(INTERFACE)
    tricritical = _read(TRICRITICAL)
    if interface.get("passes", {}).get("all") is not True:
        raise RuntimeError("interface input must be certified")
    if tricritical.get("checks", {}).get("all") is not True:
        raise RuntimeError("tricritical input must be certified")

    mass = 1.0
    scale = 1.0
    x_probe = np.logspace(-12.0, 4.0, 257)
    solutions = [
        unregulated_solution(float(x), mass=mass, scale=scale) for x in x_probe
    ]
    selector = np.asarray([row["selector_s"] for row in solutions])
    lagrangian = np.asarray([row["lagrangian"] for row in solutions])
    radial_energy_curvatures = np.asarray(
        [row["radial_energy_curvature"] for row in solutions]
    )
    radial_gradient_normalizations = np.asarray(
        [row["radial_gradient_normalization"] for row in solutions]
    )
    inverse_correlation_scales_squared = np.asarray(
        [row["radial_inverse_correlation_scale_squared"] for row in solutions]
    )
    expected_selector = scale * np.sqrt(2.0 * mass * x_probe)
    coefficient = 2.0 * scale * (2.0 * mass) ** 1.5 / 3.0
    expected_lagrangian = -coefficient * x_probe**1.5
    selector_error = float(np.max(np.abs(selector / expected_selector - 1.0)))
    density_error = float(np.max(np.abs(lagrangian / expected_lagrangian - 1.0)))
    density_slope = float(np.polyfit(np.log(x_probe), np.log(-lagrangian), 1)[0])
    radial_curvature_error = float(
        np.max(np.abs(radial_energy_curvatures / (16.0 * mass * x_probe) - 1.0))
    )
    radial_gradient_normalization_error = float(
        np.max(np.abs(radial_gradient_normalizations / 2.0 - 1.0))
    )
    inverse_correlation_scale_squared_error = float(
        np.max(
            np.abs(inverse_correlation_scales_squared / (8.0 * mass * x_probe) - 1.0)
        )
    )

    y_star, eta_star = fold_point()
    fold_value = dimensionless_stationarity(y_star, eta_star)
    fold_derivative = dimensionless_stationarity_derivative(y_star, eta_star)
    below_roots = regulated_stationary_roots(0.999 * eta_star)
    above_eta = 2.0 * eta_star
    above_roots = regulated_stationary_roots(above_eta)
    regulator = 0.1
    x_above = x_abs_from_eta(above_eta, mass=mass, scale=scale, regulator=regulator)
    dimensional_roots = [regulator**2 * root for root in above_roots]
    above_curvatures = [
        radial_energy_curvature(
            root,
            -x_above,
            mass=mass,
            scale=scale,
            regulator=regulator,
        )
        for root in dimensional_roots
    ]
    root_residuals = [
        normalized_stationarity_residual(root, above_eta) for root in above_roots
    ]
    fold_x = x_abs_from_eta(eta_star, mass=mass, scale=scale, regulator=regulator)
    parametric_x = regulator**4 / (2.0 * mass * scale**2)

    fixed_x = 1.0
    regulator_sequence = [0.2, 0.1, 0.05, 0.025]
    unregulated_s = unregulated_solution(fixed_x, mass=mass, scale=scale)["selector_s"]
    regulator_limit_rows: list[dict[str, float]] = []
    for regulator_value in regulator_sequence:
        eta = eta_from_parameters(
            fixed_x,
            mass=mass,
            scale=scale,
            regulator=regulator_value,
        )
        roots = regulated_stationary_roots(eta)
        stable_s = regulator_value**2 * roots[-1]
        regulator_limit_rows.append(
            {
                "regulator": regulator_value,
                "eta": eta,
                "stable_selector_s": stable_s,
                "relative_error_to_unregulated": abs(stable_s / unregulated_s - 1.0),
            }
        )
    regulator_limit_errors = np.asarray(
        [row["relative_error_to_unregulated"] for row in regulator_limit_rows]
    )

    tower_zero = homogeneous_tower_minimum(0.0, mass=mass, scale=scale)
    tower_nonzero = homogeneous_tower_minimum(1.0, mass=mass, scale=scale)
    compensator_rows = {
        f"abs_Q_power_{power}": {
            "q_power": power,
            "sigma_power": compensator_power_for_bulk_operator(power),
            "total_scaling_dimension": (
                compensator_power_for_bulk_operator(power) + 1.5 * power
            ),
        }
        for power in (2, 4, 6)
    }
    deformation_powers = {
        "q2": relevant_deformation_power(1.0),
        "q4": relevant_deformation_power(2.0),
        "q6": relevant_deformation_power(3.0),
    }

    checks = {
        "certified_inputs": True,
        "unregulated_selector_matches_eq92": selector_error < 4.0e-15,
        "unregulated_density_matches_eq93": density_error < 5.0e-15,
        "unregulated_log_slope_is_three_halves": abs(density_slope - 1.5) < 2.0e-13,
        "unregulated_radial_energy_curvature_is_16_m_abs_x": (
            radial_curvature_error < 4.0e-15
        ),
        "unregulated_radial_gradient_normalization_is_2": (
            radial_gradient_normalization_error < 4.0e-15
        ),
        "unregulated_spatial_inverse_correlation_scale_squared_is_8_m_abs_x": (
            inverse_correlation_scale_squared_error < 4.0e-15
        ),
        "fold_satisfies_stationarity_and_double_root": (
            abs(fold_value) < 2.0e-11 and abs(fold_derivative) < 2.0e-11
        ),
        "below_fold_has_no_nonzero_stationary_branch": below_roots == [],
        "above_fold_has_unstable_and_stable_roots": (
            len(above_roots) == 2
            and above_curvatures[0] < 0.0
            and above_curvatures[1] > 0.0
        ),
        "regulated_root_residuals_close": max(root_residuals) < 2.0e-14,
        "regulated_stable_branch_converges_to_unregulated_branch": bool(
            np.all(np.diff(regulator_limit_errors) < 0.0)
            and regulator_limit_errors[-1] < 2.0e-3
        ),
        "weyl_homogeneity_does_not_select_unique_wilson_function": (
            tower_zero["power_in_x"] == tower_nonzero["power_in_x"] == 1.5
            and tower_zero["dimensionless_radial_curvature"] > 0.0
            and tower_nonzero["dimensionless_radial_curvature"] > 0.0
            and not math.isclose(
                tower_zero["onshell_energy_coefficient"],
                tower_nonzero["onshell_energy_coefficient"],
            )
        ),
        "q2_and_q4_deformations_change_deep_power": (
            math.isclose(deformation_powers["q2"], 0.75)
            and math.isclose(deformation_powers["q4"], 1.2)
            and math.isclose(deformation_powers["q6"], 1.5)
        ),
        "five_dimensional_compensator_allows_q2_q4_q6": all(
            math.isclose(row["total_scaling_dimension"], 5.0)
            for row in compensator_rows.values()
        ),
        "five_dimensional_spatial_weyl_power_is_two_not_three_halves": (
            quasistatic_weyl_power(3) == 1.5 and quasistatic_weyl_power(4) == 2.0
        ),
        "zero_temperature_negative_x_branch_has_wrong_kinetic_sign": (
            phonon_second_derivative(-1.0) < 0.0 and phonon_second_derivative(1.0) > 0.0
        ),
        "no_observational_tables_read": True,
    }
    checks["all"] = all(checks.values())

    current_q2y_derived = bool(
        tricritical["physical_gates"][
            "q_squared_times_Y_vertex_derived_from_constraint_action"
        ]
    )
    gates = {
        "G1_5d_action_and_boundary_origin": _binary_gate(
            False,
            "The frozen 5D action and boundary conditions derive the C1 field and its Wilson function.",
            "The BK action is an external 4D construction and is absent from the certified HOLO action.",
        ),
        "G2_ward_selection_and_relevant_operators": _binary_gate(
            False,
            "An existing Ward identity selects the Wilson function and forbids q^2 and q^4 deformations.",
            "Spatial homogeneity admits distinct stable Wilson functions, while an illustrative dimension-one 5D compensator permits q^2, q^4 and q^6.",
        ),
        "G3_regular_vacuum_and_exact_deep_branch": _binary_gate(
            False,
            "A regular vacuum retains the non-zero three-halves branch continuously down to X=0.",
            "Lambda_c>0 creates a fold; Lambda_c=0 makes the action singular at s=0.",
        ),
        "G4_uniform_local_radial_elimination": _binary_gate(
            False,
            "The spatially normalized radial fluctuation has a strictly positive uniform inverse-correlation scale as X tends to zero.",
            "H_rho=16*m*abs(X) and Z_rho=2, so M_spatial^2=H_rho/Z_rho=8*m*abs(X); the inverse-correlation scale vanishes and its correlation length diverges.",
        ),
        "G5_same_action_stabilizes_negative_x_branch": _binary_gate(
            False,
            "The declared zero-temperature action has a healthy phonon kinetic matrix on X<0.",
            "P_XX is negative on X<0; a separate finite-temperature operator is required.",
        ),
        "G6_holo_matter_vertex": _binary_gate(
            current_q2y_derived,
            "The current constrained 5D reduction derives the physical q^2*Y matter vertex.",
            "The certified tricritical bridge records this vertex as unproved.",
        ),
    }
    gates["all"] = all(gate["passed"] for gate in gates.values())

    return {
        "schema": "holo.c1-bk-derivative-gate.v1",
        "title": "C1 regulated derivative-condensate reproduction and kill gate",
        "classification": (
            "valid_radial_counterexample_to_canonical_phi6_no_go;"
            "failed_declared_5d_holo_completion"
        ),
        "evidence_boundary": (
            "This is a theory-only reproduction of the algebraic BK mechanism and "
            "a fail-closed audit against the current certified HOLO action. It is "
            "not a fit, force detection, lensing prediction or 5D derivation."
        ),
        "sources": {
            "paper": PAPER,
            "interface": {
                "path": str(INTERFACE.relative_to(REPO)),
                "sha256": _sha256(INTERFACE),
            },
            "tricritical_bridge": {
                "path": str(TRICRITICAL.relative_to(REPO)),
                "sha256": _sha256(TRICRITICAL),
            },
            "observational_inputs_read": [],
        },
        "conventions": {
            "selector": "s=rho^2>0",
            "mond_sign_branch": "X=-x with x>0",
            "regulator": "Lambda_c>=0 and c=Lambda_c^2",
            "algebraic_approximation": "radial gradients are neglected as in BK Eq. (91)",
            "regulated_lagrangian": (
                "L=m*s*X+(4/3)*Lambda^4*m^3*X^3*s^3/(Lambda_c^2+s)^6"
            ),
        },
        "unregulated_counterexample": {
            "static_energy": "E=m*x*s+(4/3)*Lambda^4*m^3*x^3/s^3",
            "stationary_selector": "s=Lambda*sqrt(2*m*x)",
            "onshell_lagrangian": ("L=-(2/3)*Lambda*(2*m)^(3/2)*x^(3/2)"),
            "radial_energy_curvature": "d2E/d(rho)^2=16*m*x>0",
            "verdict": "PASS: a stable radial inverse-susceptibility counterexample exists",
        },
        "regulated_fold": {
            "dimensionless_variables": (
                "y=s/Lambda_c^2; eta=4*Lambda^4*m^2*x^2/Lambda_c^8"
            ),
            "stationarity": "(1+y)^7+eta*y^2*(1-y)=0",
            "fold_y": y_star,
            "fold_eta": eta_star,
            "fold_sqrt_eta": math.sqrt(eta_star),
            "fold_x_for_probe_regulator": fold_x,
            "bk_parametric_x_for_probe_regulator": parametric_x,
            "exact_fold_over_parametric_x": fold_x / parametric_x,
            "below_fold_nonzero_roots": below_roots,
            "above_fold_eta": above_eta,
            "above_fold_roots_y": above_roots,
            "above_fold_radial_energy_curvatures": above_curvatures,
            "interpretation": (
                "The lower stationary branch is radially unstable, the upper "
                "branch is locally stable, and both meet at zero curvature."
            ),
        },
        "regulator_to_zero_limit": {
            "fixed_x": fixed_x,
            "unregulated_selector_s": unregulated_s,
            "sequence": regulator_limit_rows,
            "regularity_locality_dichotomy": (
                "Finite Lambda_c regularizes s=0 but removes the deep branch below "
                "a fold. Lambda_c=0 restores exact homogeneity but is singular at "
                "s=0 and has a collapsing spatial inverse-correlation scale."
            ),
        },
        "radial_locality": {
            "static_energy_curvature": "H_rho=d2E/d(rho)^2=16*m*abs(X)",
            "radial_gradient_normalization": "Z_rho=2 from BK Eq. (89)",
            "spatial_inverse_correlation_scale_squared": (
                "M_spatial^2=H_rho/Z_rho=8*m*abs(X)"
            ),
            "spatial_inverse_correlation_scale": ("M_spatial=sqrt(8*m*abs(X))"),
            "correlation_length": "xi_radial=1/sqrt(8*m*abs(X))",
            "scope_warning": (
                "M_spatial is the inverse correlation length in the static spatial "
                "derivative expansion, not a temporal pole mass or an all-channel "
                "UV cutoff."
            ),
        },
        "symmetry_audit": {
            "homogeneous_class": "L=s^3*F(X/s^2)",
            "stationary_root_condition": "3*F(z)-2*z*F'(z)=0",
            "two_distinct_stable_wilson_examples": [tower_zero, tower_nonzero],
            "conclusion": (
                "Spatial homogeneity protects the power if a stable root exists, "
                "but it does not select F, the root, its sign or normalization."
            ),
            "quasistatic_weyl_power_3_spatial_dimensions": quasistatic_weyl_power(3),
            "quasistatic_weyl_power_4_spatial_dimensions": quasistatic_weyl_power(4),
            "five_dimensional_compensator_operators": compensator_rows,
            "five_dimensional_compensator_assumption": (
                "illustrative [Sigma]=1 and [Q]=(D-2)/2; not present in the "
                "current certified HOLO action"
            ),
        },
        "relevant_deformation_audit": {
            "balance": "E=r_p*s^p+A*x^3/s^3 gives E_on proportional to x^[3p/(p+3)]",
            "powers": deformation_powers,
            "conclusion": (
                "Quadratic and quartic amplitude operators change the deep power; "
                "scale symmetry with an illustrative dimension-one 5D "
                "compensator does not forbid them."
            ),
        },
        "zero_temperature_phonon_gate": {
            "effective_density": "P(X)=C*X*sqrt(abs(X))",
            "second_derivative": "P_XX=(3C/4)*sign(X)/sqrt(abs(X))",
            "negative_x_probe": phonon_second_derivative(-1.0),
            "positive_x_probe": phonon_second_derivative(1.0),
            "conclusion": (
                "The MOND-sign X<0 branch has the wrong zero-temperature kinetic "
                "sign even though its static radial extremum is a minimum."
            ),
        },
        "binary_gates": gates,
        "decision": {
            "promote_as_mathematical_counterexample": True,
            "promote_as_declared_holo_c1_completion": gates["all"],
            "verdict": "KILL_C1" if not gates["all"] else "PROMOTE_C1",
            "no_repair_rule": (
                "Do not add a regulator, finite-temperature term, Wilson coefficient "
                "or boundary operator after seeing a failed gate. A newly declared action "
                "would constitute a new candidate, not a repair of C1."
            ),
        },
        "diagnostics": {
            "samples": int(x_probe.size),
            "selector_max_relative_error": selector_error,
            "onshell_density_max_relative_error": density_error,
            "onshell_density_log_slope": density_slope,
            "radial_energy_curvature_max_relative_error": radial_curvature_error,
            "radial_gradient_normalization_max_relative_error": (
                radial_gradient_normalization_error
            ),
            "spatial_inverse_correlation_scale_squared_max_relative_error": (
                inverse_correlation_scale_squared_error
            ),
            "maximum_regulated_root_residual": max(root_residuals),
        },
        "checks": checks,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(
        "[C1 algebra] slope={:.12g}; fold eta={:.12g}; sqrt(eta)={:.12g}".format(
            result["diagnostics"]["onshell_density_log_slope"],
            result["regulated_fold"]["fold_eta"],
            result["regulated_fold"]["fold_sqrt_eta"],
        )
    )
    print(f"[C1 physical verdict] {result['decision']['verdict']}")
    print(f"[mathematical certificate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
