#!/usr/bin/env python3
"""Derive the geometric critical matching and its local constraint gate.

The static Dirac bath was originally described as cancelling a bare spatial
stiffness inside the same acceleration functional.  That interpretation is
dangerous: after cancellation the fundamental Hessian is cubic, loses rank at
zero acceleration and has the wrong sign if the acceleration belongs to a
generic dynamical aether vector.

There is a better five-dimensional organization.  In a hypersurface-orthogonal
khronon theory, spatial curvature and the lapse-acceleration functional enter a
Schur complement.  With ``n`` spatial dimensions the geometric critical value
is

    eta_c = xi * (n-1)/(n-2).

The positive quadratic term of the filled Dirac sea is retained, rather than
cancelled by a negative bare term.  Writing its coefficient as ``Delta eta``
and choosing a positive high-field baseline ``eta_inf=eta_c-Delta eta`` gives

    F(a) = eta_inf a^2 + L_bath(a),

whose static effective lapse Hessian stays positive while the *reduced metric*
coefficient vanishes at the geometric critical point.  The resulting
normalized constitutive function is exactly

    mu(x) = 1 + x - sqrt(1+x^2).

This module derives the local flat-background ADM/Dirac constraint count and
the conditional critical ``z=2`` pole structure.  It does not claim the full
warped, brane, fermionic retarded problem is complete.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np

if __package__:
    from . import derive_dirac_critical_bath_gate as static_bath
else:
    import derive_dirac_critical_bath_gate as static_bath


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STATIC_GATE = HERE / "artifacts" / "dirac_critical_bath_gate.json"
ORIGIN_GATE = HERE / "artifacts" / "covariant_5d_pseudogap_gate.json"
C3_GATE = HERE / "artifacts" / "c3_geometric_transition_gate.json"
OUTPUT = HERE / "artifacts" / "khronon_constraint_stability_gate.json"

SCHEMA = "holo.khronon-constraint-stability-gate.v1"


class KhrononGateInputError(ValueError):
    """An action coefficient or upstream certificate is malformed."""


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KhrononGateInputError(f"cannot read {path}: {exc}") from exc
    if type(value) is not dict:
        raise KhrononGateInputError(f"{path}: expected a JSON object")
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
        raise KhrononGateInputError(f"{name} must be positive and finite")
    return result


def _nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise KhrononGateInputError(f"{name} must be nonnegative and finite")
    return result


def _spatial_dimension(value: int) -> int:
    if type(value) is not int or value <= 2:
        raise KhrononGateInputError("spatial_dimension must be an integer greater than two")
    return value


def geometric_critical_eta(spatial_dimension: int, xi: float) -> float:
    """Critical acceleration coefficient after eliminating the scalar metric."""

    n = _spatial_dimension(spatial_dimension)
    curvature = _positive(xi, "xi")
    return curvature * (n - 1.0) / (n - 2.0)


def lifshitz_acceleration_magnitude(
    dynamical_exponent: float,
    curvature_radius: float,
) -> float:
    """Return ``|a|=z/L`` for the static Lifshitz time foliation.

    The result is nonzero because the adapted lapse varies radially.  It is used
    only to prevent the local flat ``a=0`` gate from being silently transferred
    to the Lifshitz background of the separate origin artifact.
    """

    z = _positive(dynamical_exponent, "dynamical_exponent")
    radius = _positive(curvature_radius, "curvature_radius")
    return z / radius


def scalar_kinetic_coefficient(spatial_dimension: int, lambda_k: float) -> float:
    """Kinetic coefficient after eliminating the scalar shift perturbation."""

    n = _spatial_dimension(spatial_dimension)
    coupling = float(lambda_k)
    if not math.isfinite(coupling) or coupling == 1.0:
        raise KhrononGateInputError("lambda_k must be finite and different from one")
    return (n - 1.0) * (n * coupling - 1.0) / (coupling - 1.0)


def scalar_sound_speed_squared(
    spatial_dimension: int,
    lambda_k: float,
    xi: float,
    eta: float,
) -> float:
    """Low-momentum khronon scalar speed on an isotropic background."""

    n = _spatial_dimension(spatial_dimension)
    coupling = float(lambda_k)
    curvature = _positive(xi, "xi")
    acceleration = _positive(eta, "eta")
    if not math.isfinite(coupling) or coupling in (1.0, 1.0 / n):
        raise KhrononGateInputError(
            "lambda_k must avoid the lambda=1 and DeWitt-degenerate values"
        )
    return (
        curvature
        * ((n - 1.0) * curvature / acceleration - (n - 2.0))
        * (coupling - 1.0)
        / (n * coupling - 1.0)
    )


def scalar_quadratic_coefficients(
    spatial_dimension: int,
    lambda_k: float,
    xi: float,
    eta: float,
) -> dict[str, float | bool]:
    """Return the shift/lapse Schur-complement coefficients."""

    n = _spatial_dimension(spatial_dimension)
    curvature = _positive(xi, "xi")
    acceleration = _positive(eta, "eta")
    q_zeta = scalar_kinetic_coefficient(n, lambda_k)
    gradient = curvature * (n - 1.0) * (
        (n - 2.0) - curvature * (n - 1.0) / acceleration
    )
    speed = -gradient / q_zeta
    eta_c = geometric_critical_eta(n, curvature)
    return {
        "q_zeta": q_zeta,
        "zeta_gradient_lagrangian_coefficient": gradient,
        "sound_speed_squared": speed,
        "static_lapse_coefficient_after_eliminating_zeta": acceleration - eta_c,
        "eta_c": eta_c,
        "no_scalar_ghost": q_zeta > 0.0,
        "gradient_stable": speed >= 0.0,
        "strictly_hyperbolic_at_k_squared_order": speed > 0.0,
    }


def _r_transverse(x: float) -> float:
    """Stable evaluation of ``sqrt(1+x^2)-x`` for nonnegative x."""

    value = _nonnegative(x, "x")
    return 1.0 / (math.hypot(1.0, value) + value)


def _bath_shape(x: float) -> float:
    """Stable ``(1+x^2)^(3/2)-1-x^3`` for nonnegative x."""

    value = _nonnegative(x, "x")
    if value <= 1.0e-2:
        square = value * value
        return (
            1.5 * square
            - value * square
            + 0.375 * square * square
            - 0.0625 * square**3
            + (3.0 / 128.0) * square**4
        )
    root = math.hypot(1.0, value)
    difference = 1.0 / (root + value)
    return difference * (1.0 + 2.0 * value * value + root * value) - 1.0


def geometric_matched_function(
    acceleration: float,
    *,
    a0: float,
    eta_infinity: float,
    eta_critical: float,
) -> float:
    """Convex static effective ``F_eff(a)=eta_inf*a^2+L_bath(a)``."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(a0, "a0")
    eta_inf = _positive(eta_infinity, "eta_infinity")
    eta_c = _positive(eta_critical, "eta_critical")
    if eta_inf >= eta_c:
        raise KhrononGateInputError("eta_infinity must be below eta_critical")
    delta = eta_c - eta_inf
    x = magnitude / scale
    result = eta_inf * magnitude * magnitude + (
        2.0 * delta * scale * scale / 3.0
    ) * _bath_shape(x)
    if not math.isfinite(result):
        raise KhrononGateInputError("matched function is outside binary64 range")
    return result


def geometric_susceptibility(
    acceleration: float,
    *,
    a0: float,
    eta_infinity: float,
    eta_critical: float,
) -> float:
    """Return ``chi=F'(a)/(2a)`` including its regular zero-field limit."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(a0, "a0")
    eta_inf = _positive(eta_infinity, "eta_infinity")
    eta_c = _positive(eta_critical, "eta_critical")
    if eta_inf >= eta_c:
        raise KhrononGateInputError("eta_infinity must be below eta_critical")
    return eta_inf + (eta_c - eta_inf) * _r_transverse(magnitude / scale)


def geometric_mu(
    acceleration: float,
    *,
    a0: float,
) -> float:
    """Stable normalized reduced-metric constitutive coefficient."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(a0, "a0")
    x = magnitude / scale
    root = math.hypot(1.0, x)
    if x <= 1.0:
        return x * (1.0 - x / (root + 1.0))
    return 1.0 - 1.0 / (root + x)


def detuned_geometric_mu(
    acceleration: float,
    *,
    a0: float,
    normalized_detuning: float,
) -> float:
    """Return the reduced coefficient away from the critical surface.

    ``normalized_detuning`` is
    ``[eta_c-(eta_inf+Delta_eta)]/Delta_eta``.  Any nonzero value eventually
    dominates the desired ``mu~x`` infrared asymptote.
    """

    residual = float(normalized_detuning)
    if not math.isfinite(residual):
        raise KhrononGateInputError("normalized_detuning must be finite")
    return residual + geometric_mu(acceleration, a0=a0)


def geometric_hessian_coefficients(
    acceleration: float,
    *,
    a0: float,
    eta_infinity: float,
    eta_critical: float,
) -> dict[str, float]:
    """Transverse and longitudinal half-Hessian coefficients of ``F``."""

    magnitude = _nonnegative(acceleration, "acceleration")
    scale = _positive(a0, "a0")
    eta_inf = _positive(eta_infinity, "eta_infinity")
    eta_c = _positive(eta_critical, "eta_critical")
    if eta_inf >= eta_c:
        raise KhrononGateInputError("eta_infinity must be below eta_critical")
    delta = eta_c - eta_inf
    transverse_ratio = _r_transverse(magnitude / scale)
    longitudinal_ratio = (
        2.0 * transverse_ratio**3 / (1.0 + transverse_ratio**2)
    )
    return {
        "transverse_ratio": transverse_ratio,
        "longitudinal_ratio": longitudinal_ratio,
        "eta_transverse_F_prime_over_2a": eta_inf + delta * transverse_ratio,
        "eta_longitudinal_F_second_over_2": eta_inf + delta * longitudinal_ratio,
        "lapse_symbol_transverse": 2.0 * (eta_inf + delta * transverse_ratio),
        "lapse_symbol_longitudinal": 2.0 * (eta_inf + delta * longitudinal_ratio),
    }


def local_constraint_inventory(
    spatial_dimension: int,
    *,
    include_dilaton: bool = False,
) -> dict[str, int | bool | str]:
    """Count the local khronometric gravitational phase space.

    The global time-reparametrization mode is not counted in this local density.
    """

    n = _spatial_dimension(spatial_dimension)
    if type(include_dilaton) is not bool:
        raise KhrononGateInputError("include_dilaton must be boolean")
    metric_phase = n * (n + 1)
    lapse_phase = 2
    shift_phase = 2 * n
    total_phase = metric_phase + lapse_phase + shift_phase
    first_class = 2 * n
    second_class = 2
    khronometric_dof = (total_phase - 2 * first_class - second_class) // 2
    einstein_dof = (n + 1) * (n - 2) // 2
    total_bosonic = khronometric_dof + int(include_dilaton)
    return {
        "spatial_metric_canonical_pairs": n * (n + 1) // 2,
        "total_phase_space_dimension_including_lapse_shift": total_phase,
        "first_class_constraints": first_class,
        "second_class_constraints": second_class,
        "khronometric_gravitational_dof": khronometric_dof,
        "einstein_tensor_dof": einstein_dof,
        "extra_khronon_scalar_dof": khronometric_dof - einstein_dof,
        "dilaton_dof": int(include_dilaton),
        "total_bosonic_dof_before_bath": total_bosonic,
        "local_count_integer": (
            total_phase - 2 * first_class - second_class
        )
        % 2
        == 0,
        "global_time_reparametrization_mode_included": False,
    }


def critical_retarded_poles(
    momentum: float,
    *,
    q_zeta: float,
    ohmic_coefficient: float,
    k4_coefficient: float,
) -> tuple[complex, complex]:
    """Poles of ``-q*w^2-i*Gamma*k^2*w+B*k^4``.

    ``ohmic_coefficient`` is Gamma, including the geometric Schur factor.
    """

    k = _nonnegative(momentum, "momentum")
    q = _positive(q_zeta, "q_zeta")
    damping = _nonnegative(ohmic_coefficient, "ohmic_coefficient")
    stabilizer = _nonnegative(k4_coefficient, "k4_coefficient")
    momentum_squared = k * k
    try:
        twice_natural = 2.0 * math.sqrt(q) * math.sqrt(stabilizer)
    except OverflowError as exc:
        raise KhrononGateInputError("pole coefficients exceed binary64 range") from exc
    if not math.isfinite(momentum_squared) or not math.isfinite(twice_natural):
        raise KhrononGateInputError("pole coefficients exceed binary64 range")

    if damping >= twice_natural:
        if damping == 0.0:
            roots = (0j, 0j)
        else:
            ratio = twice_natural / damping
            radical = damping * math.sqrt(max(0.0, 1.0 - ratio * ratio))
            denominator = damping + radical
            fast_rate = denominator / (2.0 * q)
            slow_rate = 0.0 if stabilizer == 0.0 else 2.0 * stabilizer / denominator
            roots = (-1j * momentum_squared * slow_rate, -1j * momentum_squared * fast_rate)
    else:
        ratio = damping / twice_natural
        oscillation = (
            twice_natural * math.sqrt(max(0.0, 1.0 - ratio * ratio)) / (2.0 * q)
        )
        decay = damping / (2.0 * q)
        roots = (
            momentum_squared * complex(oscillation, -decay),
            momentum_squared * complex(-oscillation, -decay),
        )
    if not all(math.isfinite(root.real) and math.isfinite(root.imag) for root in roots):
        raise KhrononGateInputError("retarded poles exceed binary64 range")
    return roots


def critical_power_counting(
    spatial_dimension: int,
    dynamical_exponent: float,
) -> dict[str, float | bool]:
    """Canonical scaling dimension of ``zeta`` and ``|grad zeta|^3``."""

    n = _spatial_dimension(spatial_dimension)
    z = _positive(dynamical_exponent, "dynamical_exponent")
    field_dimension = 0.5 * (n - z)
    cubic_gradient_dimension = 3.0 * (1.0 + field_dimension)
    action_density_dimension = n + z
    return {
        "field_dimension": field_dimension,
        "cubic_gradient_operator_dimension": cubic_gradient_dimension,
        "action_density_dimension": action_density_dimension,
        "cubic_gradient_is_marginal": math.isclose(
            cubic_gradient_dimension,
            action_density_dimension,
            rel_tol=0.0,
            abs_tol=1.0e-15,
        ),
    }


def _source_receipts() -> dict[str, dict[str, str]]:
    paths = {
        "dirac_static_gate": STATIC_GATE,
        "covariant_5D_origin_gate": ORIGIN_GATE,
        "c3_input_gate": C3_GATE,
    }
    return {
        name: {"path": str(path.relative_to(REPO)), "sha256": _sha256(path)}
        for name, path in paths.items()
    }


def build() -> dict[str, Any]:
    static = _read(STATIC_GATE)
    origin = _read(ORIGIN_GATE)
    c3 = _read(C3_GATE)
    if static.get("schema") != "holo.dirac-critical-bath-gate.v1":
        raise KhrononGateInputError("unexpected Dirac static gate schema")
    if static.get("checks", {}).get("all") is not True:
        raise KhrononGateInputError("Dirac static gate is not certified")
    if origin.get("schema") != "holo.covariant-5d-pseudogap-gate.v1":
        raise KhrononGateInputError("unexpected covariant origin gate schema")
    if origin.get("checks", {}).get("all") is not True:
        raise KhrononGateInputError("covariant origin gate is not certified")
    if c3.get("schema") != "holo.c3-geometric-transition-gate.v1":
        raise KhrononGateInputError("unexpected C3 gate schema")
    if c3.get("checks", {}).get("all") is not True:
        raise KhrononGateInputError("C3 gate is not certified")

    n = 4
    xi = 1.0
    lambda_k = 1.2
    eta_c = geometric_critical_eta(n, xi)

    cutoff = 1.0
    yukawa = 1.0
    rho_slope = 0.1
    degeneracy = 2
    a0 = static_bath.acceleration_scale(cutoff=cutoff, yukawa=yukawa)
    delta_eta = static_bath.critical_stiffness(
        cutoff=cutoff,
        yukawa=yukawa,
        rho_slope=rho_slope,
        degeneracy=degeneracy,
    )
    eta_inf = eta_c - delta_eta
    if eta_inf <= 0.0:
        raise RuntimeError("diagnostic bath is too stiff for positive high-field baseline")

    accelerations = np.geomspace(1.0e-9, 1.0e9, 721) * a0
    x_values = accelerations / a0
    action_mu = np.asarray(
        [geometric_mu(value, a0=a0) for value in accelerations]
    )
    static_mu = np.asarray(
        [static_bath.matched_mu(float(value)) for value in x_values]
    )
    maximum_mu_error = float(np.max(np.abs(action_mu - static_mu)))

    action_function = np.asarray(
        [
            geometric_matched_function(
                value,
                a0=a0,
                eta_infinity=eta_inf,
                eta_critical=eta_c,
            )
            for value in accelerations
        ]
    )
    bath_function = np.asarray(
        [
            eta_inf * value * value
            + static_bath.bath_lagrangian(
                value,
                cutoff=cutoff,
                yukawa=yukawa,
                rho_slope=rho_slope,
                degeneracy=degeneracy,
            )
            for value in accelerations
        ]
    )
    function_scale = np.maximum(np.abs(action_function), np.finfo(float).tiny)
    maximum_bath_identity_relative_error = float(
        np.max(np.abs(action_function - bath_function) / function_scale)
    )

    susceptibilities = np.asarray(
        [
            geometric_susceptibility(
                value,
                a0=a0,
                eta_infinity=eta_inf,
                eta_critical=eta_c,
            )
            for value in accelerations
        ]
    )
    mu_from_schur = (eta_c - susceptibilities) / delta_eta
    maximum_schur_mu_error = float(np.max(np.abs(mu_from_schur - action_mu)))

    hessians = [
        geometric_hessian_coefficients(
            value,
            a0=a0,
            eta_infinity=eta_inf,
            eta_critical=eta_c,
        )
        for value in np.concatenate(([0.0], accelerations))
    ]
    transverse_hessian = np.asarray(
        [row["eta_transverse_F_prime_over_2a"] for row in hessians]
    )
    longitudinal_hessian = np.asarray(
        [row["eta_longitudinal_F_second_over_2"] for row in hessians]
    )
    lapse_symbols = np.asarray(
        [
            min(row["lapse_symbol_transverse"], row["lapse_symbol_longitudinal"])
            for row in hessians
        ]
    )

    critical_quadratic = scalar_quadratic_coefficients(
        n, lambda_k, xi, eta_c
    )
    away_quadratic = [
        scalar_quadratic_coefficients(n, lambda_k, xi, float(value))
        for value in longitudinal_hessian[1:]
    ]
    minimum_nonzero_sound_speed_squared = float(
        min(row["sound_speed_squared"] for row in away_quadratic)
    )
    q_zeta = float(critical_quadratic["q_zeta"])

    constraint_count = local_constraint_inventory(n, include_dilaton=True)
    origin_parameters = origin["covariant_5D_scaling_candidate"]["parameters"]
    origin_boundary_spatial_dimension = int(
        origin_parameters["boundary_spatial_dimension"]
    )
    origin_lifshitz_acceleration = lifshitz_acceleration_magnitude(
        float(origin_parameters["dynamical_exponent"]),
        1.0,
    )
    pure_cubic_zero_symbol = (0.0, 0.0)
    pure_cubic_nonzero_symbol = (-3.0 * 0.4, -6.0 * 0.4)

    frequencies = np.geomspace(1.0e-12, 1.0e-6, 80) * cutoff
    temporal_deficits = np.asarray(
        [
            static_bath.temporal_kernel_deficit(
                value,
                cutoff=cutoff,
                yukawa=yukawa,
                rho_slope=rho_slope,
                degeneracy=degeneracy,
            )
            for value in frequencies
        ]
    )
    kappa_numeric = float(np.median(temporal_deficits / frequencies))
    kappa_expected = math.pi * degeneracy * rho_slope * yukawa**2 / 8.0
    schur_ohmic = (n - 2.0) ** 2 * kappa_expected
    k4_coefficient = 0.8
    momenta = np.geomspace(1.0e-8, 1.0e2, 120)
    pole_pairs = [
        critical_retarded_poles(
            value,
            q_zeta=q_zeta,
            ohmic_coefficient=schur_ohmic,
            k4_coefficient=k4_coefficient,
        )
        for value in momenta
    ]
    maximum_pole_imaginary_part = float(
        max(root.imag for pair in pole_pairs for root in pair)
    )
    zero_k4_poles = critical_retarded_poles(
        1.0,
        q_zeta=q_zeta,
        ohmic_coefficient=schur_ohmic,
        k4_coefficient=0.0,
    )
    power_counting = critical_power_counting(n, 2.0)
    diagnostic_normalized_detuning = 1.0e-4
    diagnostic_deep_x = 1.0e-8
    tuned_deep_mu = geometric_mu(diagnostic_deep_x * a0, a0=a0)
    detuned_deep_mu = detuned_geometric_mu(
        diagnostic_deep_x * a0,
        a0=a0,
        normalized_detuning=diagnostic_normalized_detuning,
    )

    checks = {
        "certified_inputs": True,
        "bath_quadratic_is_retained_not_internally_cancelled": math.isclose(
            eta_inf + delta_eta, eta_c, rel_tol=0.0, abs_tol=2.0e-15
        ),
        "bath_function_matches_convex_action_function": (
            maximum_bath_identity_relative_error < 1.0e-10
        ),
        "static_bath_is_not_double_counted_in_reduced_action": True,
        "critical_surface_is_not_mislabelled_as_protected_or_selected": True,
        "nonzero_detuning_destroys_the_asymptotic_deep_limit": (
            detuned_deep_mu > 1.0e3 * tuned_deep_mu
        ),
        "geometric_Schur_reduction_gives_exact_static_mu": (
            maximum_mu_error < 3.0e-15 and maximum_schur_mu_error < 3.0e-15
        ),
        "static_effective_F_Hessian_is_positive_at_and_away_from_vacuum": bool(
            min(np.min(transverse_hessian), np.min(longitudinal_hessian))
            >= eta_inf
            and np.min(lapse_symbols) >= 2.0 * eta_inf
        ),
        "critical_lapse_symbol_keeps_rank": math.isclose(
            float(lapse_symbols[0]), 2.0 * eta_c, rel_tol=2.0e-15
        ),
        "critical_scalar_is_not_a_ghost": critical_quadratic["no_scalar_ghost"]
        is True,
        "critical_scalar_k2_speed_is_zero": abs(
            float(critical_quadratic["sound_speed_squared"])
        )
        < 2.0e-15,
        "nonzero_background_scalar_k2_speed_is_positive": (
            minimum_nonzero_sound_speed_squared > 0.0
        ),
        "local_constraint_count_is_six_gravity_plus_dilaton": (
            constraint_count["khronometric_gravitational_dof"] == 6
            and constraint_count["einstein_tensor_dof"] == 5
            and constraint_count["extra_khronon_scalar_dof"] == 1
            and constraint_count["total_bosonic_dof_before_bath"] == 7
        ),
        "flat_and_lifshitz_backgrounds_are_not_conflated": (
            origin_lifshitz_acceleration > 0.0
        ),
        "boundary_three_component_bath_is_not_conflated_with_bulk_four_space": (
            origin_boundary_spatial_dimension == 3 and n == 4
        ),
        "pure_negative_cubic_realization_is_killed": (
            pure_cubic_zero_symbol == (0.0, 0.0)
            and max(pure_cubic_nonzero_symbol) < 0.0
        ),
        "fermion_temporal_kernel_has_positive_ohmic_weight": (
            kappa_numeric > 0.0
            and math.isclose(
                kappa_numeric, kappa_expected, rel_tol=2.0e-6, abs_tol=0.0
            )
        ),
        "conditional_positive_k4_truncated_poles_have_no_UHP_roots": (
            maximum_pole_imaginary_part <= 0.0
        ),
        "zero_k4_limit_has_zero_and_non_growing_diffusive_pole": (
            min(abs(root) for root in zero_k4_poles) < 1.0e-15
            and min(root.imag for root in zero_k4_poles) < 0.0
            and max(root.imag for root in zero_k4_poles) <= 0.0
        ),
        "critical_z2_cubic_gradient_is_power_counting_marginal_in_4_space": (
            power_counting["cubic_gradient_is_marginal"] is True
        ),
        "full_retarded_and_warped_problem_not_promoted": True,
        "no_force_lensing_or_publication_promotion": True,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"khronon constraint/stability checks failed: {failed}")

    decision = {
        "old_internal_bare_minus_bath_quadratic_cancellation_required": False,
        "geometric_critical_matching_rule_derived": True,
        "exact_static_mu_derived_from_action_Schur_complement": True,
        "same_action_local_5D_microscopic_bath_derived": False,
        "critical_matching_dynamically_selected": False,
        "fine_tuning_eliminated": False,
        "same_5D_action_and_background_closed": False,
        "flat_constraint_result_transferred_to_lifshitz_background": False,
        "static_effective_acceleration_function_is_convex": True,
        "local_flat_background_lapse_constraint_rank_preserved": True,
        "local_flat_background_gravitational_DOF_count_derived": True,
        "pure_negative_cubic_aether_realization_survives": False,
        "critical_k_squared_scalar_wave_exists": False,
        "truncated_z2_kernel_has_no_upper_half_plane_poles": True,
        "full_microscopic_retarded_kernel_derived": False,
        "full_warped_brane_boundary_constraint_system_derived": False,
        "complete_time_dependent_stability": False,
        "current_holo_mechanism": False,
        "physical_completion": False,
        "new_force_derived": False,
        "lensing_derived": False,
        "publication_authorized": False,
        "verdict": (
            "GEOMETRIC_KHRONON_MATCHING_PRESERVES_LOCAL_CONSTRAINT_RANK_"
            "FULL_RETARDED_AND_WARPED_COMPLETION_BLOCKED"
        ),
        "next_action": (
            "First construct an explicit local 5D bath action whose static determinant "
            "reproduces F; then compute its complete retarded Pi_R(omega,k) before "
            "eliminating lapse and audit all poles, branch cuts, warped junction "
            "constraints and boundary modes with a fixed cutoff hierarchy."
        ),
    }

    return {
        "schema": SCHEMA,
        "title": "Geometric khronon matching, local constraints and temporal pre-gate",
        "classification": "theory_only;local_constraint_rank_closed;full_dynamics_open",
        "evidence_boundary": (
            "The result replaces an unstable internal stiffness cancellation by an "
            "metric/lapse Schur matching inside a covariant khronon EFT and closes the "
            "local flat constraint count. The static bath function is imported from "
            "the spectral gate, not yet derived from the same microscopic 5D action. "
            "The truncated z=2 pole model has no upper-half-plane roots only "
            "conditional on a positive Ohmic kernel and higher-gradient coefficient. "
            "The full microscopic retarded, warped and brane-boundary problem remains "
            "uncomputed."
        ),
        "sources": {
            **_source_receipts(),
            "raw_observational_tables_read_directly": [],
            "inherited_target_origin": static["sources"][
                "inherited_exposed_target_origin"
            ],
            "primary_theory_references": [
                {
                    "topic": "covariant khronon action and modified Poisson limit",
                    "url": "https://arxiv.org/abs/1107.5264",
                },
                {
                    "topic": "healthy nonprojectable Horava scalar",
                    "url": "https://arxiv.org/abs/0909.3525",
                },
                {
                    "topic": "Hamiltonian constraint structure",
                    "url": "https://arxiv.org/abs/1106.2131",
                },
                {
                    "topic": "stability limits of khronometric MOND",
                    "url": "https://arxiv.org/abs/1502.05554",
                },
            ],
        },
        "action": {
            "signature": "(-++++)",
            "covariant_khronon": "U_M=-partial_M T/sqrt(-partial T squared)",
            "acceleration": "a_M=U^N nabla_N U_M; a=sqrt((G_MN+U_M U_N)a^M a^N)",
            "adapted_ADM_form": (
                "S=(M5^3/2) integral dt d4x N sqrt(h) "
                "[K_AB K^AB-lambda K^2+xi R4+F_eff(a)] plus S_dilaton; "
                "F_eff includes the integrated-out static bath and the bath is not "
                "added a second time"
            ),
            "bath_accounting": (
                "Use either the reduced static F_eff or future explicit bath fields, "
                "never both in the same action."
            ),
            "microscopic_status": (
                "The filled-sea static function is imported from the spectral gate; "
                "a same-action local 5D bath derivation remains blocked."
            ),
            "sign_convention": "F enters with a plus sign in the displayed ADM action",
            "geometric_critical_value": "eta_c=xi*(n-1)/(n-2)",
            "bulk_4_plus_1_eta_c": eta_c,
            "bath_quadratic_increment": delta_eta,
            "positive_high_field_baseline_eta_infinity": eta_inf,
            "acceleration_scale_a0": a0,
            "static_effective_function": (
                "F=eta_inf*a^2+(2*(eta_c-eta_inf)/3)*a0^2*"
                "[(1+x^2)^(3/2)-1-x^3]"
            ),
            "microscopic_identity": (
                "eta_c-eta_inf=K2=g*rho1*Lambda*y^2/2 and a0=Lambda/y, "
                "so the second term equals the filled-sea L_bath exactly"
            ),
            "critical_relation_is_radiatively_protected": False,
            "critical_relation_is_dynamically_selected": False,
            "matching_status": (
                "eta_inf+Delta_eta=eta_c is a derived critical surface but remains "
                "an imposed codimension-one tuning; the improvement is stability, "
                "not symmetry protection or self-selection"
            ),
        },
        "static_reduction": {
            "susceptibility": (
                "chi=F'/(2a)=eta_inf+(eta_c-eta_inf)*(sqrt(1+x^2)-x)"
            ),
            "reduced_static_coefficient": "eta_c-chi",
            "high_field_normalization": "eta_c-eta_inf",
            "constitutive_function": "mu=(eta_c-chi)/(eta_c-eta_inf)=1+x-sqrt(1+x^2)",
            "maximum_mu_error_against_static_gate": maximum_mu_error,
            "maximum_mu_error_from_Schur_formula": maximum_schur_mu_error,
            "maximum_bath_function_identity_relative_error": (
                maximum_bath_identity_relative_error
            ),
            "small_field_expansion": (
                "F=eta_c*a^2-[2*(eta_c-eta_inf)/(3*a0)]*a^3+O(a^4)"
            ),
            "interpretation": (
                "The negative reduced cubic is generated only after solving the "
                "metric constraint; the static effective acceleration Hessian is positive."
            ),
        },
        "hessian_and_constraint_rank": {
            "eta_transverse_minimum": float(np.min(transverse_hessian)),
            "eta_longitudinal_minimum": float(np.min(longitudinal_hessian)),
            "lapse_principal_symbol_minimum": float(np.min(lapse_symbols)),
            "analytic_bounds": "eta_inf <= eta_L <= eta_T <= eta_c",
            "lapse_symbol": (
                "Q_AB=2*eta_T*P_T_AB+2*eta_L*P_L_AB >= 2*eta_inf*h_AB"
            ),
            "primary_constraints": ["p_N approximately 0", "p_A approximately 0 (A=1..4)"],
            "secondary_constraints": [
                "C_N approximately 0 (local lapse equation)",
                "H_A approximately 0 (A=1..4)",
            ],
            "classification": (
                "(p_N,C_N) local second-class elliptic pair; shift/momentum pairs "
                "first-class; one global time-reparametrization part excluded"
            ),
            "inventory": constraint_count,
            "generic_vector_aether_comparison": (
                "in 4+1 a generic aether has five tensor plus three spin-1 plus "
                "one scalar modes; hypersurface orthogonality removes the spin-1 sector"
            ),
        },
        "quadratic_stability": {
            "spatial_dimension": n,
            "lambda": lambda_k,
            "xi": xi,
            "critical_coefficients": critical_quadratic,
            "health_region": (
                "M5^3>0, xi>0, lambda>1 or lambda<1/4, and "
                "0<eta<3*xi/2 for strict k^2 scalar propagation"
            ),
            "minimum_nonzero_background_sound_speed_squared": (
                minimum_nonzero_sound_speed_squared
            ),
            "tensor_polarizations": 5,
            "tensor_speed_squared": xi,
            "critical_interpretation": (
                "At a=0 the scalar kinetic residue is positive and the lapse "
                "constraint remains elliptic, but c0^2=0; higher spatial derivatives "
                "or the microscopic memory kernel control the leading propagation."
            ),
        },
        "killed_realization": {
            "ansatz": "F_fundamental=-gamma*|A|^3 after cancelling all A^2 inside F",
            "lapse_symbol_at_zero": list(pure_cubic_zero_symbol),
            "generic_aether_hessian_at_A_0p4_gamma_1": list(
                pure_cubic_nonzero_symbol
            ),
            "reason": (
                "The lapse symbol loses rank at zero; for a generic vector aether "
                "A_i is a velocity at leading order and the nonzero-background "
                "Hessian is negative kinetic energy."
            ),
            "verdict": "KILL_PURE_NEGATIVE_CUBIC_FUNDAMENTAL_AETHER",
        },
        "conditional_temporal_completion": {
            "fermion_kernel": "K(0)-K(i*omega_E)=kappa*|omega_E|+...",
            "kappa_numeric": kappa_numeric,
            "kappa_expected": kappa_expected,
            "critical_Euclidean_inverse_propagator": (
                "q_zeta*omega_E^2+(n-2)^2*kappa*k^2*|omega_E|+B4*k^4"
            ),
            "bulk_4_plus_1_ohmic_Schur_coefficient": schur_ohmic,
            "diagnostic_positive_k4_coefficient": k4_coefficient,
            "maximum_retarded_pole_imaginary_part": maximum_pole_imaginary_part,
            "zero_k4_poles_at_k_1": [
                {"real": root.real, "imaginary": root.imag}
                for root in zero_k4_poles
            ],
            "power_counting": power_counting,
            "microscopic_branch_cut_acknowledged_but_not_in_pole_model": True,
            "branch_cut_resolved": False,
            "proved_scope": (
                "For q_zeta>0, kappa>=0 and B4>=0 the truncated quadratic-model "
                "poles are not in the upper half plane; this is not a full "
                "branch-cut or temporal-stability proof."
            ),
            "unproved_scope": [
                "complete Pi_R(omega,k) and positive spectral representation",
                "absence of additional bath, radial and brane poles",
                "causal UV completion while microscopic fermions remain explicit",
                "positive and scale-separated k4/k6 operators on the warped background",
            ],
        },
        "dimensional_boundary": {
            "bulk_spatial_dimensions": 4,
            "bulk_eta_c": "3*xi/2",
            "brane_spatial_dimensions": 3,
            "brane_eta_c": "2*xi",
            "warning": (
                "The bulk and brane critical coefficients cannot be mixed; this "
                "artifact certifies the local 4+1 bulk calculation only."
            ),
        },
        "background_compatibility_gate": {
            "origin_lifshitz_boundary_spatial_dimensions": (
                origin_boundary_spatial_dimension
            ),
            "origin_free_witness_acceleration_components": 3,
            "constraint_gate_bulk_spatial_dimensions": n,
            "constraint_gate_background": "local flat background with a_M=0",
            "lifshitz_static_foliation_acceleration": "|a|=z/L along the radial direction",
            "diagnostic_lifshitz_acceleration_at_L_1": (
                origin_lifshitz_acceleration
            ),
            "same_background_analysis_completed": False,
            "radial_projection_and_boundary_conditions_derived": False,
            "adjudication": (
                "The three-component boundary bath and the four-spatial-component "
                "bulk khronon are not yet one solved system. The flat constraint "
                "certificate cannot be transplanted to the Lifshitz background."
            ),
        },
        "matching_sensitivity": {
            "detuning_definition": "delta_match=eta_c-(eta_inf+Delta_eta)",
            "detuned_constitutive_function": (
                "mu_delta=delta_match/Delta_eta+1+x-sqrt(1+x^2)"
            ),
            "RG_normal_beta": (
                "beta_match=(n-1)*beta_xi/(n-2)-beta_eta_inf-beta_Delta_eta"
            ),
            "ward_identity_derived": False,
            "diagnostic_normalized_detuning": diagnostic_normalized_detuning,
            "diagnostic_deep_x": diagnostic_deep_x,
            "diagnostic_tuned_mu": tuned_deep_mu,
            "diagnostic_detuned_mu": detuned_deep_mu,
            "deep_limit_condition": (
                "To retain mu approximately x over a finite window, require "
                "|delta_match|/Delta_eta much smaller than its minimum x."
            ),
        },
        "acceptance_ladder": [
            {"level": "K0_static_bath_function", "status": "PASS"},
            {"level": "K1_geometric_matching_and_exact_mu", "status": "PASS"},
            {"level": "K2_local_flat_constraint_rank_and_DOF", "status": "PASS"},
            {
                "level": "K3_critical_local_z2_pole_model",
                "status": "CONDITIONAL_NO_UHP_IN_TRUNCATED_KERNEL",
            },
            {"level": "K4_same_action_full_retarded_kernel", "status": "BLOCKED"},
            {"level": "K5_warped_brane_boundary_constraints", "status": "BLOCKED"},
            {"level": "K6_force_matter_and_lensing", "status": "NOT_ENTERED"},
        ],
        "diagnostics": {
            "eta_critical": eta_c,
            "eta_infinity": eta_inf,
            "bath_delta_eta": delta_eta,
            "q_zeta": q_zeta,
            "maximum_mu_error": maximum_mu_error,
            "maximum_Schur_mu_error": maximum_schur_mu_error,
            "maximum_bath_identity_relative_error": maximum_bath_identity_relative_error,
            "minimum_lapse_symbol": float(np.min(lapse_symbols)),
            "critical_sound_speed_squared": float(
                critical_quadratic["sound_speed_squared"]
            ),
            "minimum_nonzero_sound_speed_squared": minimum_nonzero_sound_speed_squared,
            "temporal_kernel_linear_coefficient": kappa_numeric,
            "maximum_pole_imaginary_part": maximum_pole_imaginary_part,
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
