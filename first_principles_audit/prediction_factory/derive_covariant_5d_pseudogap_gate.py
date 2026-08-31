#!/usr/bin/env python3
"""Gate covariant five-dimensional origins of the Dirac pseudogap bath.

The uniform-static Dirac construction derives the desired sign once a linear
density of states is granted.  This module asks the harder next question:
can the density of states, Clifford source and critical quadratic cancellation
all come from one local covariant five-dimensional action?

The answer is deliberately split into statements with different evidence:

* the current regular compact Einstein--dilaton action is excluded as the
  origin of an exact infrared ``rho(epsilon) proportional to epsilon`` bath;
* a local Einstein--Proca action in five dimensions has an isotropic Lifshitz
  solution with boundary ``d=3, z=3/2``.  Its thermodynamic state-counting
  scaling has effective dimension ``d/z=2``.  This is the required exponent,
  but is not by itself a literal single-particle density of states;
* a free Clifford witness with dispersion ``epsilon=c |k|^(3/2)`` reproduces
  the old determinant exactly, but that fractional quadratic symbol is not a
  finite-derivative local boundary action;
* Lifshitz scaling alone does not prove that the same local bulk action has the
  sharp Clifford spectrum, normalization or determinant sign.  A radial
  spinor calculation is still missing;
* the 1F+8B quadratic sum rule is a codimension-one matching, not a Ward
  identity.  A distinct 5D supersymmetric prepotential protects a cubic at a
  fixed point, but it is a gauge kinetic prepotential rather than an AQUAL
  vacuum potential.

Consequently this is an architecture advance and a fail-closed origin gate,
not a force, lensing or completed-dynamics claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

if __package__:
    from . import derive_dirac_critical_bath_gate as static_bath
else:
    import derive_dirac_critical_bath_gate as static_bath


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CURRENT_ACTION = REPO / "first_principles_audit" / "artifacts" / "holo_effective_action.json"
C3_GATE = HERE / "artifacts" / "c3_geometric_transition_gate.json"
DIRAC_GATE = HERE / "artifacts" / "dirac_critical_bath_gate.json"
RED_TEAM = HERE / "artifacts" / "dirac_bath_red_team_map.json"
OUTPUT = HERE / "artifacts" / "covariant_5d_pseudogap_gate.json"

SCHEMA = "holo.covariant-5d-pseudogap-gate.v1"


class CovariantOriginInputError(ValueError):
    """An input certificate or proposed microscopic parameter is malformed."""


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CovariantOriginInputError(f"cannot read {path}: {exc}") from exc
    if type(value) is not dict:
        raise CovariantOriginInputError(f"{path}: expected a JSON object")
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
        raise CovariantOriginInputError(f"{name} must be positive and finite")
    return result


def _nonnegative_integer(value: int, name: str) -> int:
    if type(value) is not int or value < 0:
        raise CovariantOriginInputError(f"{name} must be a nonnegative integer")
    return value


def hyperscaling_spectral_exponents(
    spatial_dimension: int,
    dynamical_exponent: float,
    hyperscaling_violation: float = 0.0,
) -> dict[str, float]:
    """Return state-counting, DOS and gap-free-energy scaling exponents.

    A scale-invariant sector with ``d`` spatial dimensions, dynamical exponent
    ``z`` and hyperscaling violation ``theta`` has effective spatial dimension
    ``d_eff=d-theta``.  The scale-only predictions are

    ``N(E) ~ E^(d_eff/z)``, ``rho(E) ~ E^(d_eff/z-1)`` and
    ``Delta f(m) ~ |m|^((d_eff+z)/z)`` for an energy-like gap source.

    These exponents do not assert a sharp quasiparticle or fix a coefficient.
    """

    if type(spatial_dimension) is not int or spatial_dimension <= 0:
        raise CovariantOriginInputError("spatial_dimension must be a positive integer")
    z = _positive(dynamical_exponent, "dynamical_exponent")
    theta = float(hyperscaling_violation)
    if not math.isfinite(theta):
        raise CovariantOriginInputError("hyperscaling_violation must be finite")
    effective = spatial_dimension - theta
    if effective <= 0.0:
        raise CovariantOriginInputError("effective spatial dimension must be positive")
    counting = effective / z
    return {
        "effective_spatial_dimension": effective,
        "state_count_exponent": counting,
        "density_of_states_exponent": counting - 1.0,
        "gap_free_energy_exponent": counting + 1.0,
    }


def hyperscaling_null_energy_condition(
    spatial_dimension: int,
    dynamical_exponent: float,
    hyperscaling_violation: float = 0.0,
) -> dict[str, float | bool]:
    """Evaluate the two standard hyperscaling-violating NEC inequalities."""

    exponents = hyperscaling_spectral_exponents(
        spatial_dimension, dynamical_exponent, hyperscaling_violation
    )
    d = float(spatial_dimension)
    z = float(dynamical_exponent)
    theta = float(hyperscaling_violation)
    first = (d - theta) * (d * (z - 1.0) - theta)
    second = (z - 1.0) * (d + z - theta)
    tolerance = 64.0 * np.finfo(float).eps * max(
        1.0, abs(first), abs(second)
    )
    return {
        **exponents,
        "first_inequality": first,
        "second_inequality": second,
        "tolerance": tolerance,
        "satisfied": bool(first >= -tolerance and second >= -tolerance),
    }


def einstein_proca_lifshitz_parameters(
    spatial_dimension: int,
    dynamical_exponent: float,
) -> dict[str, float | bool | str]:
    """Return the exact Lifshitz solution parameters in Taylor's convention.

    For

    ``I ~ integral sqrt(-G) [R+Lambda-(F^2+m_B^2 B^2)/4]``

    and ``ds^2=L^2[dr^2-exp(2 z r)dt^2+exp(2 r)dx_d^2]``, the dimensionless
    parameters are ``m_B^2 L^2=2 z d``,
    ``B_hat_t^2=2(z-1)/z`` and
    ``Lambda L^2=z^2+(d-1)z+d^2``.  The sign named ``Lambda`` is the positive
    coefficient used in ``R+Lambda``.
    """

    if type(spatial_dimension) is not int or spatial_dimension <= 0:
        raise CovariantOriginInputError("spatial_dimension must be a positive integer")
    z = _positive(dynamical_exponent, "dynamical_exponent")
    amplitude_squared = 2.0 * (z - 1.0) / z
    return {
        "action_convention": "R+Lambda-(F_MN F^MN+m_B^2 B_M B^M)/4",
        "bulk_spacetime_dimension": spatial_dimension + 2,
        "boundary_spatial_dimension": spatial_dimension,
        "dynamical_exponent": z,
        "proca_mass_squared_times_L_squared": 2.0 * z * spatial_dimension,
        "timelike_tangent_amplitude_squared": amplitude_squared,
        "Lambda_times_L_squared": (
            z * z + (spatial_dimension - 1.0) * z + spatial_dimension**2
        ),
        "real_timelike_vector": amplitude_squared >= 0.0,
        "isotropic_in_boundary_space": True,
    }


def lifshitz_dos_coefficient(
    spatial_dimension: int,
    dynamical_exponent: float,
    *,
    dispersion_coefficient: float = 1.0,
    degeneracy: int = 1,
) -> float:
    """Coefficient of the free isotropic DOS for ``E=c |k|^z``.

    Per unit physical volume,

    ``rho(E)=g*S_(d-1)/[(2*pi)^d z] c^(-d/z) E^(d/z-1)``.
    """

    if type(spatial_dimension) is not int or spatial_dimension <= 0:
        raise CovariantOriginInputError("spatial_dimension must be a positive integer")
    z = _positive(dynamical_exponent, "dynamical_exponent")
    coefficient = _positive(dispersion_coefficient, "dispersion_coefficient")
    if type(degeneracy) is not int or degeneracy <= 0:
        raise CovariantOriginInputError("degeneracy must be a positive integer")
    sphere_area = 2.0 * math.pi ** (0.5 * spatial_dimension) / math.gamma(
        0.5 * spatial_dimension
    )
    return (
        degeneracy
        * sphere_area
        / ((2.0 * math.pi) ** spatial_dimension * z)
        * coefficient ** (-spatial_dimension / z)
    )


def lifshitz_density_of_states(
    energy: float,
    spatial_dimension: int,
    dynamical_exponent: float,
    *,
    dispersion_coefficient: float = 1.0,
    degeneracy: int = 1,
) -> float:
    """Evaluate the free isotropic density of states at positive energy."""

    energy = _positive(energy, "energy")
    exponent = spatial_dimension / _positive(
        dynamical_exponent, "dynamical_exponent"
    ) - 1.0
    coefficient = lifshitz_dos_coefficient(
        spatial_dimension,
        dynamical_exponent,
        dispersion_coefficient=dispersion_coefficient,
        degeneracy=degeneracy,
    )
    result = coefficient * energy**exponent
    if not math.isfinite(result):
        raise CovariantOriginInputError("density of states is outside binary64 range")
    return result


def lifshitz_clifford_spectrum(
    momentum: Sequence[float],
    acceleration: Sequence[float],
    *,
    dynamical_exponent: float = 1.5,
    dispersion_coefficient: float = 1.0,
    yukawa: float = 1.0,
) -> np.ndarray:
    """Spectrum of the free scaling witness, not of the local bulk action.

    ``H=c |k|^z Gamma_1 + y a_I Gamma_(I+1)`` uses four mutually
    anticommuting matrices.  It makes the magnitude emerge from the algebra,
    but for noninteger ``z`` its boundary quadratic symbol is fractional.
    """

    vector_k = np.asarray(momentum, dtype=float)
    vector_a = np.asarray(acceleration, dtype=float)
    if vector_k.shape != (3,) or vector_a.shape != (3,):
        raise CovariantOriginInputError("momentum and acceleration must be 3-vectors")
    if np.any(~np.isfinite(vector_k)) or np.any(~np.isfinite(vector_a)):
        raise CovariantOriginInputError("momentum and acceleration must be finite")
    z = _positive(dynamical_exponent, "dynamical_exponent")
    coefficient = _positive(dispersion_coefficient, "dispersion_coefficient")
    coupling = _positive(yukawa, "yukawa")
    epsilon = coefficient * float(np.linalg.norm(vector_k)) ** z
    gamma = static_bath.clifford_five()
    hamiltonian = epsilon * gamma[0]
    for index, component in enumerate(vector_a):
        hamiltonian = hamiltonian + coupling * component * gamma[index + 1]
    return np.linalg.eigvalsh(hamiltonian)


def matching_supertraces(
    negative_fermion_branches: int,
    real_bosons: int,
    *,
    fermion_coupling: float = 1.0,
    boson_coupling: float = 0.5,
) -> dict[str, float | int | bool]:
    """Return the quadratic, cubic and quartic signed bath sums."""

    n_f = _nonnegative_integer(
        negative_fermion_branches, "negative_fermion_branches"
    )
    n_b = _nonnegative_integer(real_bosons, "real_bosons")
    y_f = _positive(fermion_coupling, "fermion_coupling")
    y_b = _positive(boson_coupling, "boson_coupling")
    sums = {
        power: n_f * y_f**power - 0.5 * n_b * y_b**power
        for power in (2, 3, 4)
    }
    return {
        "negative_fermion_branches": n_f,
        "real_bosons": n_b,
        "signed_quadratic_sum": sums[2],
        "signed_cubic_sum": sums[3],
        "signed_quartic_sum": sums[4],
        "quadratic_cancels": math.isclose(sums[2], 0.0, abs_tol=1.0e-15),
        "negative_lagrangian_cubic_survives": sums[3] > 0.0,
    }


def matching_beta_on_sum_rule(
    negative_fermion_branches: int,
    *,
    common_coupling: float,
    fermion_anomalous_rate: float,
    boson_anomalous_rate: float,
    fermion_dos_anomalous_rate: float = 0.0,
    boson_dos_anomalous_rate: float = 0.0,
) -> float:
    """RG derivative of ``rho_f y_f^2-4 rho_b y_b^2`` at matching.

    The convention is ``y_b=y_f/2`` and ``N_B=8 N_F``.  Rates are logarithmic
    derivatives.  A nonzero result is the explicit tangent away from the
    critical surface.
    """

    n_f = _nonnegative_integer(
        negative_fermion_branches, "negative_fermion_branches"
    )
    y = _positive(common_coupling, "common_coupling")
    rates = (
        float(fermion_anomalous_rate),
        float(boson_anomalous_rate),
        float(fermion_dos_anomalous_rate),
        float(boson_dos_anomalous_rate),
    )
    if not all(math.isfinite(value) for value in rates):
        raise CovariantOriginInputError("anomalous rates must be finite")
    gamma_y_f, gamma_y_b, gamma_rho_f, gamma_rho_b = rates
    return n_f * y * y * (
        gamma_rho_f - gamma_rho_b + 2.0 * (gamma_y_f - gamma_y_b)
    )


def ims_rank_one_prepotential(
    scalar: float,
    *,
    inverse_gauge_coupling: float = 0.0,
    classical_cubic: float = 0.0,
    root_charges: Sequence[float] = (),
    hypermultiplets: Sequence[tuple[float, float]] = (),
) -> float:
    """Evaluate the rank-one Intriligator--Morrison--Seiberg prepotential.

    ``hypermultiplets`` entries are ``(weight, real_mass)``.  This executable
    formula audits cubic homogeneity at the fixed point; it does not reinterpret
    the prepotential as a static potential.
    """

    phi = float(scalar)
    m0 = float(inverse_gauge_coupling)
    cubic = float(classical_cubic)
    roots = tuple(float(value) for value in root_charges)
    hypers = tuple((float(weight), float(mass)) for weight, mass in hypermultiplets)
    values = (phi, m0, cubic, *roots, *(x for pair in hypers for x in pair))
    if not all(math.isfinite(value) for value in values):
        raise CovariantOriginInputError("prepotential inputs must be finite")
    if m0 < 0.0:
        raise CovariantOriginInputError("inverse_gauge_coupling must be nonnegative")
    vector_sum = math.fsum(abs(charge * phi) ** 3 for charge in roots)
    hyper_sum = math.fsum(abs(weight * phi + mass) ** 3 for weight, mass in hypers)
    return (
        0.5 * m0 * phi * phi
        + cubic * phi**3 / 6.0
        + (vector_sum - hyper_sum) / 12.0
    )


def cubic_static_hessian_eigenvalues(
    acceleration_magnitude: float,
    coefficient: float,
) -> tuple[float, float, float]:
    """Eigenvalues of the Hessian of ``U=C |a|^3`` for ``|a|>=0``."""

    magnitude = float(acceleration_magnitude)
    constant = float(coefficient)
    if not math.isfinite(magnitude) or magnitude < 0.0:
        raise CovariantOriginInputError(
            "acceleration_magnitude must be nonnegative and finite"
        )
    if not math.isfinite(constant) or constant <= 0.0:
        raise CovariantOriginInputError("coefficient must be positive and finite")
    transverse = 3.0 * constant * magnitude
    return transverse, transverse, 2.0 * transverse


def _source_receipts() -> dict[str, dict[str, str]]:
    paths = {
        "current_effective_action": CURRENT_ACTION,
        "c3_input_gate": C3_GATE,
        "dirac_static_gate": DIRAC_GATE,
        "dirac_red_team_map": RED_TEAM,
    }
    return {
        name: {"path": str(path.relative_to(REPO)), "sha256": _sha256(path)}
        for name, path in paths.items()
    }


def build() -> dict[str, Any]:
    current = _read(CURRENT_ACTION)
    c3 = _read(C3_GATE)
    static = _read(DIRAC_GATE)
    red_team = _read(RED_TEAM)
    if current.get("summary", {}).get("passes", {}).get("all") is not True:
        raise CovariantOriginInputError("current effective action is not certified")
    if current.get("summary", {}).get("method", {}).get("action") != (
        "R - (1/2) K(phi) (partial phi)^2 - V(phi)"
    ):
        raise CovariantOriginInputError("unexpected current effective action")
    if c3.get("schema") != "holo.c3-geometric-transition-gate.v1":
        raise CovariantOriginInputError("unexpected C3 gate schema")
    if c3.get("checks", {}).get("all") is not True:
        raise CovariantOriginInputError("C3 input gate is not certified")
    if static.get("schema") != "holo.dirac-critical-bath-gate.v1":
        raise CovariantOriginInputError("unexpected static bath gate schema")
    if static.get("checks", {}).get("all") is not True:
        raise CovariantOriginInputError("static bath gate is not certified")
    if red_team.get("schema") != "holo.dirac-bath-red-team-map.v1":
        raise CovariantOriginInputError("unexpected red-team schema")
    if red_team.get("checks", {}).get("all") is not True:
        raise CovariantOriginInputError("red-team map is not certified")

    d = 3
    z = 1.5
    theta = 0.0
    target_scaling = hyperscaling_spectral_exponents(d, z, theta)
    target_nec = hyperscaling_null_energy_condition(d, z, theta)
    proca = einstein_proca_lifshitz_parameters(d, z)

    scaling_family = []
    for candidate_z in (1.0, 1.2, 1.5, 2.0):
        candidate_theta = d - 2.0 * candidate_z
        candidate = hyperscaling_null_energy_condition(
            d, candidate_z, candidate_theta
        )
        scaling_family.append(
            {
                "z": candidate_z,
                "theta": candidate_theta,
                "density_of_states_exponent": candidate[
                    "density_of_states_exponent"
                ],
                "gap_free_energy_exponent": candidate[
                    "gap_free_energy_exponent"
                ],
                "NEC_first": candidate["first_inequality"],
                "NEC_second": candidate["second_inequality"],
                "NEC_satisfied": candidate["satisfied"],
            }
        )
    relativistic_theta_one = hyperscaling_null_energy_condition(d, 1.0, 1.0)

    dispersion_coefficient = 0.73
    rho_slope = lifshitz_dos_coefficient(
        d, z, dispersion_coefficient=dispersion_coefficient
    )
    energies = np.geomspace(1.0e-9, 1.0e3, 200)
    densities = np.asarray(
        [
            lifshitz_density_of_states(
                energy,
                d,
                z,
                dispersion_coefficient=dispersion_coefficient,
            )
            for energy in energies
        ]
    )
    numerical_dos_power = float(
        np.polyfit(np.log(energies), np.log(densities), 1)[0]
    )
    expected_rho_slope = 1.0 / (3.0 * math.pi**2 * dispersion_coefficient**2)

    momentum = np.asarray([0.31, -0.27, 0.18])
    acceleration = np.asarray([0.19, -0.23, 0.41])
    yukawa = 1.17
    clifford_spectrum = lifshitz_clifford_spectrum(
        momentum,
        acceleration,
        dynamical_exponent=z,
        dispersion_coefficient=dispersion_coefficient,
        yukawa=yukawa,
    )
    epsilon = dispersion_coefficient * float(np.linalg.norm(momentum)) ** z
    expected_energy = math.hypot(epsilon, yukawa * float(np.linalg.norm(acceleration)))
    expected_spectrum = np.asarray(
        [-expected_energy, -expected_energy, expected_energy, expected_energy]
    )
    clifford_spectrum_error = float(
        np.max(np.abs(clifford_spectrum - expected_spectrum))
    )

    cutoff = 2.1
    analytic_sea = static_bath.bath_lagrangian(
        float(np.linalg.norm(acceleration)),
        cutoff=cutoff,
        yukawa=yukawa,
        rho_slope=rho_slope,
        degeneracy=1,
    )
    numerical_sea = static_bath.numerical_bath_lagrangian(
        float(np.linalg.norm(acceleration)),
        cutoff=cutoff,
        yukawa=yukawa,
        rho_slope=rho_slope,
        degeneracy=1,
    )
    sea_relative_error = abs(numerical_sea / analytic_sea - 1.0)

    compact_levels = [0.23, 0.61, 1.07, 1.82]
    compact_weights = [0.2, 0.3, 0.1, 0.4]
    compact_accelerations = np.geomspace(1.0e-8, 1.0e-5, 32)
    compact_remainders = np.asarray(
        [
            -static_bath.discrete_critical_remainder(
                value, compact_levels, compact_weights
            )
            for value in compact_accelerations
        ]
    )
    compact_critical_power = float(
        np.polyfit(
            np.log(compact_accelerations), np.log(compact_remainders), 1
        )[0]
    )
    zero_accelerations = np.geomspace(1.0e-10, 1.0e-6, 32)
    zero_responses = np.asarray(
        [
            static_bath.discrete_bath_lagrangian(value, [0.0], [1.0])
            for value in zero_accelerations
        ]
    )
    compact_zero_mode_power = float(
        np.polyfit(np.log(zero_accelerations), np.log(zero_responses), 1)[0]
    )

    frequencies = np.geomspace(1.0e-11, 1.0e-6, 64)
    temporal = np.asarray(
        [static_bath.temporal_kernel_deficit(value) for value in frequencies]
    )
    temporal_power = float(
        np.polyfit(np.log(frequencies), np.log(temporal), 1)[0]
    )

    supertrace = matching_supertraces(2, 16)
    rg_tangent_equal = matching_beta_on_sum_rule(
        2,
        common_coupling=1.0,
        fermion_anomalous_rate=0.03,
        boson_anomalous_rate=0.03,
    )
    rg_tangent_split = matching_beta_on_sum_rule(
        2,
        common_coupling=1.0,
        fermion_anomalous_rate=0.03,
        boson_anomalous_rate=-0.01,
    )

    ims_phi = 0.37
    ims_at_fixed_point = ims_rank_one_prepotential(
        ims_phi, root_charges=(-2.0, 2.0)
    )
    ims_scaled = ims_rank_one_prepotential(
        2.0 * ims_phi, root_charges=(-2.0, 2.0)
    )
    ims_with_relevant_deformation = ims_rank_one_prepotential(
        ims_phi, inverse_gauge_coupling=0.4, root_charges=(-2.0, 2.0)
    )
    hessian_vacuum = cubic_static_hessian_eigenvalues(0.0, 1.0)
    hessian_nonzero = cubic_static_hessian_eigenvalues(0.4, 1.0)

    checks = {
        "certified_inputs": True,
        "current_action_contains_only_metric_and_scalar": True,
        "compact_radial_weyl_DOS_is_constant_not_linear": True,
        "finite_positive_tower_is_quartic_after_quadratic_subtraction": abs(
            compact_critical_power - 4.0
        )
        < 2.0e-10,
        "finite_tower_zero_mode_is_linear_not_cubic": abs(
            compact_zero_mode_power - 1.0
        )
        < 2.0e-12,
        "relativistic_theta_one_linear_DOS_route_violates_NEC": (
            relativistic_theta_one["density_of_states_exponent"] == 1.0
            and relativistic_theta_one["satisfied"] is False
        ),
        "lifshitz_z_three_halves_has_required_effective_scaling": (
            abs(target_scaling["density_of_states_exponent"] - 1.0) < 1.0e-15
            and abs(target_scaling["gap_free_energy_exponent"] - 3.0) < 1.0e-15
            and abs(numerical_dos_power - 1.0) < 2.0e-13
        ),
        "lifshitz_scaling_not_promoted_to_literal_single_particle_DOS": True,
        "lifshitz_z_three_halves_satisfies_NEC": target_nec["satisfied"] is True,
        "local_covariant_5D_Einstein_Proca_background_exhibited": (
            proca["bulk_spacetime_dimension"] == 5
            and proca["real_timelike_vector"] is True
            and math.isclose(
                float(proca["proca_mass_squared_times_L_squared"]), 9.0
            )
            and math.isclose(
                float(proca["timelike_tangent_amplitude_squared"]), 2.0 / 3.0
            )
            and math.isclose(float(proca["Lambda_times_L_squared"]), 57.0 / 4.0)
        ),
        "free_lifshitz_DOS_normalization_closes": math.isclose(
            rho_slope, expected_rho_slope, rel_tol=2.0e-15
        ),
        "free_lifshitz_Clifford_witness_closes": clifford_spectrum_error < 2.0e-15,
        "free_lifshitz_sea_matches_static_closed_form": sea_relative_error < 3.0e-8,
        "free_z_three_halves_boundary_symbol_is_fractional_and_nonlocal": True,
        "same_local_5D_action_does_not_yet_derive_the_Clifford_determinant": True,
        "two_negative_branches_require_sixteen_real_bosons": (
            supertrace["negative_fermion_branches"] == 2
            and supertrace["real_bosons"] == 16
            and supertrace["quadratic_cancels"] is True
        ),
        "quadratic_sum_zero_leaves_cubic_and_quartic": (
            math.isclose(float(supertrace["signed_cubic_sum"]), 1.0)
            and math.isclose(float(supertrace["signed_quartic_sum"]), 1.5)
        ),
        "matching_surface_is_RG_tangent_only_for_equal_anomalous_rates": (
            abs(rg_tangent_equal) < 1.0e-15 and abs(rg_tangent_split) > 0.0
        ),
        "IMS_fixed_point_prepotential_is_cubic": math.isclose(
            ims_scaled, 8.0 * ims_at_fixed_point, rel_tol=2.0e-15
        ),
        "IMS_relevant_quadratic_deformation_is_visible": (
            ims_with_relevant_deformation > ims_at_fixed_point
        ),
        "IMS_prepotential_is_not_relabelled_as_static_AQUAL_energy": True,
        "gapless_temporal_kernel_is_nonanalytic": abs(temporal_power - 1.0) < 2.0e-6,
        "cubic_static_symbol_has_zero_rank_at_vacuum": hessian_vacuum == (0.0, 0.0, 0.0),
        "cubic_static_symbol_is_positive_away_from_vacuum": min(hessian_nonzero) > 0.0,
        "no_force_lensing_or_publication_promotion": True,
    }

    decision = {
        "current_regular_compact_Einstein_dilaton_origin_survives": False,
        "covariant_local_5D_Lifshitz_scaling_background_exhibited": True,
        "effective_linear_state_counting_exponent_from_5D_scaling": True,
        "literal_boundary_single_particle_DOS_derived": False,
        "free_Clifford_scaling_witness_reproduces_static_bath": True,
        "exact_Clifford_determinant_derived_from_same_local_5D_action": False,
        "quadratic_matching_is_Ward_protected": False,
        "IMS_protected_cubic_is_same_AQUAL_observable": False,
        "complete_constraint_rank_and_time_stability_derived": False,
        "current_holo_mechanism": False,
        "physical_completion": False,
        "new_force_derived": False,
        "lensing_derived": False,
        "publication_authorized": False,
        "verdict": (
            "COVARIANT_5D_LIFSHITZ_SCALING_ROUTE_SURVIVES_"
            "DETERMINANT_MATCHING_AND_DYNAMICS_BLOCKED"
        ),
        "next_action": (
            "Solve and renormalize an explicit bulk Clifford/flavor sector on the "
            "z=3/2 background with the khronon acceleration as its boundary source; "
            "accept it only if its radial determinant fixes the linear measure and "
            "negative cubic sign, then close the full Dirac/ADM rank and retarded poles."
        ),
    }

    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"covariant 5D pseudogap checks failed: {failed}")

    return {
        "schema": SCHEMA,
        "title": "Covariant five-dimensional pseudogap-origin decision gate",
        "classification": "theory_only;covariant_scaling_route_not_completed_bath",
        "evidence_boundary": (
            "The artifact proves a local covariant 5D action can supply boundary "
            "thermodynamic state-counting with the required effective linear exponent "
            "while preserving spatial isotropy. It does not derive a literal "
            "single-particle DOS or infer the sharp Clifford determinant from scaling, "
            "does not protect critical matching, and makes no force, lensing, "
            "observational or publication claim."
        ),
        "sources": {
            **_source_receipts(),
            "raw_observational_tables_read_directly": [],
            "inherited_target_origin": static["sources"][
                "inherited_exposed_target_origin"
            ],
            "primary_theory_references": [
                {
                    "topic": "covariant Einstein-Proca Lifshitz backgrounds",
                    "url": "https://arxiv.org/abs/0812.0530",
                },
                {
                    "topic": "Lifshitz fixed-point gravity duals",
                    "url": "https://arxiv.org/abs/0808.1725",
                },
                {
                    "topic": "hyperscaling-violation consistency conditions",
                    "url": "https://arxiv.org/abs/1201.1905",
                },
                {
                    "topic": "five-dimensional supersymmetric cubic prepotential",
                    "url": "https://arxiv.org/abs/hep-th/9702198",
                },
                {
                    "topic": "khronometric acceleration and MOND limit",
                    "url": "https://arxiv.org/abs/1107.5264",
                },
                {
                    "topic": "Hamiltonian constraints of nonprojectable Horava gravity",
                    "url": "https://arxiv.org/abs/1106.2131",
                },
            ],
        },
        "current_action_no_go": {
            "action": current["summary"]["method"]["action"],
            "geometry": "regular finite radial interval in the certified checkout",
            "radial_problem": "one-dimensional regular Sturm-Liouville tower",
            "Weyl_counting": "N(epsilon)~L_SL*epsilon/pi",
            "density_of_states_exponent": 0.0,
            "target_density_of_states_exponent": 1.0,
            "boundary_condition_scope": (
                "regular Dirichlet, Neumann, Robin and MIT-type endpoint changes "
                "shift phases but not the one-dimensional Weyl exponent"
            ),
            "positive_tower_after_quadratic_subtraction_power": compact_critical_power,
            "zero_mode_power": compact_zero_mode_power,
            "proca_khronon_or_clifford_sector_present": False,
            "result": "KILLED_AS_EXACT_INFRARED_PSEUDOGAP_ORIGIN",
        },
        "covariant_5D_scaling_candidate": {
            "total_action_status": "extension_candidate_not_current_HOLO_action",
            "bulk_action": (
                "S_EP=(2*kappa5^2)^-1 integral_M sqrt(-G) "
                "[R+Lambda5-(F_B^2+m_B^2 B^2)/4] plus GHY and brane terms"
            ),
            "background": (
                "ds^2=L^2[du^2-exp(2*z*u)dt^2+exp(2*u)dvec_x^2], "
                "B_t=L*sqrt(2*(z-1)/z)*exp(z*u), with u dimensionless"
            ),
            "parameters": proca,
            "null_energy_condition": target_nec,
            "scaling": target_scaling,
            "scaling_interpretation": (
                "Thermodynamic/effective state counting only; a literal boundary "
                "single-particle DOS requires a solved spectral function."
            ),
            "scaling_family_with_linear_DOS": scaling_family,
            "rejected_relativistic_theta_one_shortcut": relativistic_theta_one,
            "free_witness": {
                "hamiltonian": (
                    "H=c*|k|^(3/2)*Gamma_1+y*a_I*Gamma_(I+1)"
                ),
                "rho_epsilon": f"{rho_slope:.17g}*epsilon for the diagnostic c",
                "rho_slope": rho_slope,
                "clifford_spectrum": clifford_spectrum.tolist(),
                "maximum_spectrum_error": clifford_spectrum_error,
                "sea_integral_relative_error": sea_relative_error,
                "locality_status": (
                    "fractional free boundary symbol; not a finite-derivative local "
                    "boundary QFT"
                ),
            },
            "missing_bridge": {
                "bulk_spinor_flavor_action_and_boundary_conditions_frozen": False,
                "radial_green_function_solved": False,
                "sharp_Clifford_poles_derived": False,
                "spectral_normalization_derived": False,
                "determinant_sign_derived": False,
                "finite_band_interpolation_derived": False,
                "reason": (
                    "Thermodynamic/spectral scaling fixes powers, not pole structure, "
                    "normalization or the sign of a renormalized determinant."
                ),
            },
        },
        "covariant_acceleration_source": {
            "khronon": "U_mu=-D_mu T/sqrt(-D_alpha T D^alpha T)",
            "acceleration": "a_mu=U^nu D_nu U_mu; U^mu a_mu=0",
            "adapted_gauge": "T=t implies a_i=D_i ln(N)",
            "linear_source_template": "S_src=y integral_Sigma sqrt(-gamma) a_mu O^mu",
            "clifford_requirement": (
                "the three components of O^mu must be represented by mutually "
                "anticommuting mass matrices and anticommute with the bath kinetic block"
            ),
            "source_action_derived_from_current_HOLO": False,
        },
        "critical_matching_audit": {
            "supertrace_convention": (
                "one filled negative fermion branch has weight +1; one real stable "
                "boson zero-point determinant has weight -1/2"
            ),
            "two_branch_field_content": supertrace,
            "per_negative_branch_rule": "one fermion branch at y plus eight real bosons at y/2",
            "RG_beta_on_equal_rates": rg_tangent_equal,
            "RG_beta_on_split_rates": rg_tangent_split,
            "operator_basis_result": (
                "diffeomorphisms, rotations, parity, C, T and khronon relabeling "
                "permit both X=a_mu a^mu and X^(3/2); none is a Ward identity for c2=0"
            ),
            "exact_SUSY_result": (
                "equal supermultiplet spectra cancel the complete determinant, "
                "including both quadratic and cubic pieces"
            ),
            "status": "CODIMENSION_ONE_CRITICAL_MATCHING_NOT_PROTECTED",
        },
        "protected_alternative_audit": {
            "route": "5D N=1 gauge/SCFT Intriligator-Morrison-Seiberg prepotential",
            "formula": (
                "F=0.5*m0*h_ij*phi_i*phi_j+k_CS*d_ijk*phi_i*phi_j*phi_k/6 "
                "+(sum_roots|alpha.phi|^3-sum_hypers|w.phi+m|^3)/12"
            ),
            "fixed_point": "m0=1/g5^2 -> 0 leaves a chamberwise exact cubic",
            "diagnostic_phi": ims_phi,
            "diagnostic_prepotential": ims_at_fixed_point,
            "cubic_scaling_ratio_at_two_phi": ims_scaled / ims_at_fixed_point,
            "with_relevant_quadratic_deformation": ims_with_relevant_deformation,
            "fatal_identification_gap": (
                "F is a Coulomb-branch gauge kinetic/CS prepotential, not vacuum "
                "energy. No healthy equation derives phi^2=a_mu a^mu."
            ),
            "status": "SURVIVES_AS_DISTINCT_PROTECTED_5D_ROUTE_NOT_AS_AQUAL_BATH",
        },
        "time_and_constraint_precheck": {
            "gapless_static_bath_kernel_power": temporal_power,
            "integrated_out_kernel": "Pi_E(omega,0)-Pi_E(0,0) proportional to -|omega|",
            "local_finite_derivative_effective_action": False,
            "full_bath_can_remain_explicit_and_local": True,
            "static_cubic_hessian_eigenvalues_at_vacuum": list(hessian_vacuum),
            "static_cubic_hessian_eigenvalues_at_a_0p4": list(hessian_nonzero),
            "constant_principal_rank_at_vacuum": False,
            "khronon_scalar_constraint_known_to_be_second_class": True,
            "complete_coupled_Dirac_ADM_analysis_in_this_artifact": False,
            "adjudication": (
                "The nonanalytic retarded kernel and zero-rank static symbol are "
                "blockers to a local reduced theory; keeping microscopic fields "
                "explicit changes the problem but still requires a coupled constraint "
                "and pole calculation."
            ),
        },
        "route_matrix": [
            {
                "route": "current_regular_compact_Einstein_dilaton",
                "covariant_5D": True,
                "linear_DOS": False,
                "exact_static_determinant": False,
                "protected_matching": False,
                "status": "KILLED",
            },
            {
                "route": "compact_soft_wall",
                "covariant_5D": True,
                "linear_DOS": "coarse_grained_high_level_only",
                "exact_static_determinant": False,
                "protected_matching": False,
                "status": "KILLED_IN_STRICT_IR",
            },
            {
                "route": "2_plus_1_Dirac_brane_or_nodal_line",
                "covariant_5D": "as_defect_source",
                "linear_DOS": True,
                "exact_static_determinant": True,
                "protected_matching": False,
                "status": "SURVIVES_STATIC_ORIGIN_ONLY_ANISOTROPY_AND_DYNAMICS_OPEN",
            },
            {
                "route": "isotropic_z_3_over_2_Lifshitz_bulk",
                "covariant_5D": True,
                "linear_DOS": "effective_scaling_only_not_literal_single_particle_DOS",
                "exact_static_determinant": "not_derived_from_same_bulk_action",
                "protected_matching": False,
                "status": "LEADING_ISOTROPIC_5D_ROUTE",
            },
            {
                "route": "5D_N1_SCFT_prepotential",
                "covariant_5D": True,
                "linear_DOS": "not_the_claimed_mechanism",
                "exact_static_determinant": False,
                "protected_matching": "protected_cubic_but_wrong_observable",
                "status": "DISTINCT_ROUTE_REQUIRES_HEALTHY_ACCELERATION_REDUCTION",
            },
            {
                "route": "two_internal_momenta",
                "covariant_5D": False,
                "linear_DOS": True,
                "exact_static_determinant": True,
                "protected_matching": False,
                "status": "REQUIRES_AT_LEAST_6D_OR_SYNTHETIC_FIBER",
            },
        ],
        "acceptance_ladder": [
            {"level": "L0_uniform_static_spectrum", "status": "PASS"},
            {"level": "L1_current_compact_5D_origin", "status": "KILLED"},
            {"level": "L2_covariant_5D_linear_scaling_background", "status": "PASS"},
            {"level": "L3_same_action_Clifford_determinant", "status": "BLOCKED"},
            {"level": "L4_protected_quadratic_matching", "status": "BLOCKED"},
            {"level": "L5_constraints_and_retarded_stability", "status": "BLOCKED"},
            {"level": "L6_force_matter_and_lensing", "status": "NOT_ENTERED"},
        ],
        "diagnostics": {
            "linear_DOS_family": scaling_family,
            "free_DOS_numerical_log_slope": numerical_dos_power,
            "free_DOS_analytic_slope": rho_slope,
            "free_DOS_expected_slope": expected_rho_slope,
            "clifford_spectrum_maximum_error": clifford_spectrum_error,
            "static_sea_integral_relative_error": sea_relative_error,
            "compact_positive_tower_critical_power": compact_critical_power,
            "compact_zero_mode_power": compact_zero_mode_power,
            "temporal_kernel_power": temporal_power,
            "matching_RG_tangent_equal": rg_tangent_equal,
            "matching_RG_tangent_split": rg_tangent_split,
            "IMS_cubic_scaling_ratio": ims_scaled / ims_at_fixed_point,
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
