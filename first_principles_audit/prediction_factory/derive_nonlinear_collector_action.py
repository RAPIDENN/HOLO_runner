#!/usr/bin/env python3
"""Reconstruct a minimal nonlinear action for the universal SPARC collector.

This is an action *target*, not a derivation from the current five-dimensional
Einstein--dilaton model.  Starting from the train-frozen universal response

    nu(y) = [1 - exp(-sqrt(y))]^-1,  y = g_N/a0,

we reconstruct the AQUAL-type constitutive function mu(x) and the scalar
Lagrangian F(X), with x=|grad Phi|/a0 and X=x^2.  In spherical symmetry

    mu(x) x = y,  x = y nu(y),

so the action reproduces the collector exactly.  Its differential operator is
elliptic when both mu and mu+x*dmu/dx are positive; those conditions are
checked numerically over a wide dynamic range.

The reconstruction also resolves the ambiguous ``600`` scale.  The response
is controlled by acceleration, not by a universal length.  For an isolated
mass M the transition radius is r_M=sqrt(G M/a0), so 0.6 kpc and 600 kpc refer
to very different source masses rather than universal cutoffs.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import scipy
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq


HERE = Path(__file__).resolve().parent
COLLECTOR = HERE / "artifacts" / "universal_residual_collector.json"
OUTPUT = HERE / "artifacts" / "nonlinear_collector_action.json"

G_SI = 6.67430e-11
M_SUN_KG = 1.98847e30
M_EARTH_KG = 5.9722e24
AU_METRES = 149_597_870_700.0
PC_METRES = 3.085677581491367e16
KPC_METRES = 1.0e3 * PC_METRES
EARTH_STANDARD_GRAVITY = 9.80665


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nu_of_y(y: np.ndarray) -> np.ndarray:
    values = np.asarray(y, dtype=float)
    if np.any(~np.isfinite(values)) or np.any(values <= 0.0):
        raise ValueError("y must be finite and strictly positive")
    t = np.sqrt(values)
    return 1.0 / (-np.expm1(-t))


def parametric_constitutive(t: np.ndarray) -> tuple[np.ndarray, ...]:
    """Return y, x, X, mu, dx/dt and the longitudinal eigenvalue."""

    t = np.asarray(t, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t <= 0.0):
        raise ValueError("t must be finite and strictly positive")
    denominator = -np.expm1(-t)
    exp_minus_t = np.exp(-t)
    y = np.square(t)
    mu = denominator
    x = y / denominator
    X = np.square(x)
    dx_dt = 2.0 * t / denominator - np.square(t) * exp_minus_t / np.square(
        denominator
    )
    dmu_dx = exp_minus_t / dx_dt
    longitudinal = mu + x * dmu_dx
    return y, x, X, mu, dx_dt, longitudinal


def reconstruct_action_table(
    samples: int = 8192,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    if samples < 1024:
        raise ValueError("action reconstruction needs at least 1024 samples")
    t = np.geomspace(1.0e-6, 40.0, samples)
    y, x, X, mu, dx_dt, longitudinal = parametric_constitutive(t)

    # F'(X)=mu(sqrt(X)).  Since mu*x=y, dF/dt=mu*d(x^2)/dt=2*y*dx/dt.
    dF_dt = 2.0 * y * dx_dt
    F0 = (2.0 / 3.0) * X[0] ** 1.5
    F = F0 + cumulative_trapezoid(dF_dt, t, initial=0.0)
    interpolator = PchipInterpolator(X, F)
    numerical_mu = interpolator.derivative()(X[8:-8])
    derivative_relative_error = float(
        np.max(
            np.abs(numerical_mu - mu[8:-8])
            / np.maximum(mu[8:-8], 1.0e-15)
        )
    )

    low = slice(0, 300)
    high = slice(-300, None)
    deep_mu_slope = float(np.polyfit(np.log(x[low]), np.log(mu[low]), 1)[0])
    deep_F_slope = float(np.polyfit(np.log(X[low]), np.log(F[low]), 1)[0])
    newton_F_slope = float(np.polyfit(np.log(X[high]), np.log(F[high]), 1)[0])

    indices = np.unique(np.linspace(0, samples - 1, 256, dtype=int))
    table = {
        "parameter": "t=sqrt(g_N/a0)",
        "columns": ["t", "y", "x", "X", "mu", "F"],
        "rows": [
            [
                float(t[i]),
                float(y[i]),
                float(x[i]),
                float(X[i]),
                float(mu[i]),
                float(F[i]),
            ]
            for i in indices
        ],
    }
    diagnostics = {
        "minimum_mu": float(np.min(mu)),
        "minimum_dx_dt": float(np.min(dx_dt)),
        "minimum_longitudinal_elliptic_eigenvalue": float(
            np.min(longitudinal)
        ),
        "maximum_F_prime_relative_error": derivative_relative_error,
        "deep_limit_dlog_mu_dlog_x": deep_mu_slope,
        "deep_limit_dlog_F_dlog_X": deep_F_slope,
        "newtonian_limit_dlog_F_dlog_X": newton_F_slope,
        # Evaluate the asymptotic remainder directly: 1-exp(-t) rounds to one
        # at the upper endpoint in binary64, while exp(-t) remains representable.
        "newtonian_limit_one_minus_mu": float(np.exp(-t[-1])),
        "uniformly_elliptic_on_x_greater_than_zero": False,
        "degenerately_elliptic_as_x_tends_to_zero": True,
        "limiting_transverse_eigenvalue_at_x_zero": 0.0,
        "limiting_longitudinal_eigenvalue_at_x_zero": 0.0,
    }
    arrays = {
        "t": t,
        "y": y,
        "x": x,
        "X": X,
        "mu": mu,
        "F": F,
        "dx_dt": dx_dt,
        "longitudinal": longitudinal,
    }
    return {"table": table, "diagnostics": diagnostics}, arrays


def numerical_constitutive_inversion(
    arrays: Mapping[str, np.ndarray],
    y: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Invert reconstructed mu(x)*x=y without using x=y*nu(y)."""

    values = np.asarray(y, dtype=float)
    if np.any(~np.isfinite(values)) or np.any(values <= 0.0):
        raise ValueError("y must be finite and strictly positive")
    x_grid = np.asarray(arrays["x"], dtype=float)
    mu_grid = np.asarray(arrays["mu"], dtype=float)
    mu_of_x = PchipInterpolator(x_grid, mu_grid, extrapolate=False)

    lower = float(x_grid[0])
    upper = float(x_grid[-1])
    y_lower = float(mu_of_x(lower) * lower)
    y_upper = float(mu_of_x(upper) * upper)
    if float(np.min(values)) <= y_lower or float(np.max(values)) >= y_upper:
        raise ValueError("requested y lies outside the reconstructed action table")

    roots = np.asarray(
        [
            brentq(
                lambda trial: float(mu_of_x(trial) * trial - target),
                lower,
                upper,
                xtol=1.0e-14,
                rtol=1.0e-14,
            )
            for target in values
        ],
        dtype=float,
    )
    return roots, np.asarray(mu_of_x(roots), dtype=float)


def spherical_plummer_pde_check(
    arrays: Mapping[str, np.ndarray], samples: int = 4096
) -> dict[str, float | int | str]:
    """Solve and differentiate a dimensionless spherical Plummer test problem."""

    if samples < 1024:
        raise ValueError("Plummer PDE check needs at least 1024 samples")
    radius = np.geomspace(1.0e-3, 30.0, samples)
    # Units G=M=a0=b=1. M(<r)=r^3/(r^2+1)^(3/2).
    enclosed_mass = radius**3 / np.power(1.0 + radius**2, 1.5)
    y_newton = enclosed_mass / radius**2
    field_x, mu = numerical_constitutive_inversion(arrays, y_newton)
    flux = radius**2 * mu * field_x
    source = 3.0 / np.power(1.0 + radius**2, 2.5)
    divergence = np.gradient(flux, radius, edge_order=2) / radius**2
    interior = slice(8, -8)
    relative = np.abs(divergence[interior] - source[interior]) / source[interior]
    return {
        "problem": "spherical Plummer source in dimensionless units G=M=a0=b=1",
        "samples": samples,
        "maximum_flux_relative_error": float(
            np.max(np.abs(flux - enclosed_mass) / enclosed_mass)
        ),
        "maximum_finite_difference_pde_relative_residual": float(np.max(relative)),
        "rms_finite_difference_pde_relative_residual": float(
            np.sqrt(np.mean(np.square(relative)))
        ),
    }


def transition_radius_metres(mass_kg: float, a0: float) -> float:
    if not (math.isfinite(mass_kg) and mass_kg > 0.0):
        raise ValueError("mass must be finite and positive")
    if not (math.isfinite(a0) and a0 > 0.0):
        raise ValueError("a0 must be finite and positive")
    return math.sqrt(G_SI * mass_kg / a0)


def transition_mass_kg(radius_metres: float, a0: float) -> float:
    if not (math.isfinite(radius_metres) and radius_metres > 0.0):
        raise ValueError("radius must be finite and positive")
    if not (math.isfinite(a0) and a0 > 0.0):
        raise ValueError("a0 must be finite and positive")
    return a0 * radius_metres**2 / G_SI


def log10_fractional_correction(g_newton_si: float, a0: float) -> float:
    """Return log10(nu-1) without underflow at high acceleration."""

    if not (math.isfinite(g_newton_si) and g_newton_si > 0.0):
        raise ValueError("Newtonian acceleration must be finite and positive")
    t = math.sqrt(g_newton_si / a0)
    if t < 700.0:
        return -math.log10(math.expm1(t))
    return -t / math.log(10.0)


def _scale_inventory(a0: float) -> dict[str, Any]:
    masses = {
        "Earth": M_EARTH_KG,
        "Sun": M_SUN_KG,
        "dwarf_3e8_Msun": 3.0e8 * M_SUN_KG,
        "Milky_Way_baryons_6e10_Msun": 6.0e10 * M_SUN_KG,
        "cluster_3e14_Msun": 3.0e14 * M_SUN_KG,
    }
    transitions: dict[str, Any] = {}
    for name, mass in masses.items():
        radius = transition_radius_metres(mass, a0)
        transitions[name] = {
            "mass_kg": mass,
            "mass_msun": mass / M_SUN_KG,
            "radius_metres": radius,
            "radius_au": radius / AU_METRES,
            "radius_pc": radius / PC_METRES,
            "radius_kpc": radius / KPC_METRES,
        }

    radius_readings = {}
    for label, radius_kpc in (("0.6_kpc", 0.6), ("600_kpc", 600.0)):
        mass = transition_mass_kg(radius_kpc * KPC_METRES, a0)
        radius_readings[label] = {
            "radius_kpc": radius_kpc,
            "source_mass_for_gN_equal_a0_kg": mass,
            "source_mass_for_gN_equal_a0_msun": mass / M_SUN_KG,
        }

    solar_g_1au = G_SI * M_SUN_KG / AU_METRES**2
    solar_g_neptune = G_SI * M_SUN_KG / (30.07 * AU_METRES) ** 2
    high_acceleration = {
        "Earth_surface": {
            "g_newton_m_s2": EARTH_STANDARD_GRAVITY,
            "g_over_a0": EARTH_STANDARD_GRAVITY / a0,
            "log10_nu_minus_one": log10_fractional_correction(
                EARTH_STANDARD_GRAVITY, a0
            ),
        },
        "Sun_at_1_AU": {
            "g_newton_m_s2": solar_g_1au,
            "g_over_a0": solar_g_1au / a0,
            "log10_nu_minus_one": log10_fractional_correction(solar_g_1au, a0),
        },
        "Sun_at_Neptune": {
            "g_newton_m_s2": solar_g_neptune,
            "g_over_a0": solar_g_neptune / a0,
            "log10_nu_minus_one": log10_fractional_correction(
                solar_g_neptune, a0
            ),
        },
    }
    return {
        "transition_definition": "r_M=sqrt(G*M/a0), where g_Newton(r_M)=a0",
        "transition_radii_by_source_mass": transitions,
        "mass_implied_by_candidate_radius": radius_readings,
        "formal_isolated_high_acceleration_limits": high_acceleration,
        "interpretation": (
            "There is no universal 0.6 kpc or 600 kpc switch. The same "
            "acceleration threshold maps to a mass-dependent radius. Solar and "
            "terrestrial entries are formal isolated-field limits only; external-"
            "field, relativistic and precision-ephemeris tests are not supplied "
            "by this nonrelativistic reconstruction."
        ),
    }


def build() -> dict[str, Any]:
    collector = _read(COLLECTOR)
    if collector.get("passes", {}).get("all") is not True:
        raise RuntimeError("universal collector certificate must pass")
    a0 = float(collector["train_fit"]["g_dagger_m_s2"])
    action, arrays = reconstruct_action_table()

    # Invert the numerically reconstructed constitutive table.  This avoids the
    # previous tautological check x=y*nu and mu=1/nu.
    y_check = np.geomspace(1.0e-10, 1.0e3, 1024)
    x_numeric, mu_numeric = numerical_constitutive_inversion(arrays, y_check)
    closure_error = float(
        np.max(np.abs(mu_numeric * x_numeric - y_check) / y_check)
    )
    target_x = y_check * nu_of_y(y_check)
    target_x_error = float(np.max(np.abs(x_numeric - target_x) / target_x))
    plummer_check = spherical_plummer_pde_check(arrays)

    diagnostics = action["diagnostics"]
    passes = {
        "collector_input_passes": True,
        "single_global_acceleration_scale": a0 > 0.0,
        "no_per_galaxy_parameters": (
            collector["train_fit"]["per_galaxy_parameters"] == 0
        ),
        "spherical_collector_recovered_by_numerical_inversion": (
            closure_error < 2.0e-8 and target_x_error < 2.0e-6
        ),
        "constitutive_map_single_valued": diagnostics["minimum_dx_dt"] > 0.0,
        "transverse_ellipticity_positive": diagnostics["minimum_mu"] > 0.0,
        "longitudinal_ellipticity_positive": (
            diagnostics["minimum_longitudinal_elliptic_eigenvalue"] > 0.0
        ),
        "degenerate_not_uniform_ellipticity_recorded": (
            diagnostics["degenerately_elliptic_as_x_tends_to_zero"]
            and not diagnostics["uniformly_elliptic_on_x_greater_than_zero"]
        ),
        "spherical_plummer_pde_residual_small": (
            plummer_check["maximum_finite_difference_pde_relative_residual"]
            < 2.0e-4
        ),
        "action_derivative_reconstructs_mu": (
            diagnostics["maximum_F_prime_relative_error"] < 2.0e-4
        ),
        "deep_limit_is_mond_like": (
            abs(diagnostics["deep_limit_dlog_mu_dlog_x"] - 1.0) < 2.0e-3
            and abs(diagnostics["deep_limit_dlog_F_dlog_X"] - 1.5) < 2.0e-3
        ),
        "newtonian_limit_recovered": (
            diagnostics["newtonian_limit_one_minus_mu"] < 1.0e-16
            and abs(diagnostics["newtonian_limit_dlog_F_dlog_X"] - 1.0)
            < 2.0e-3
        ),
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.nonlinear-collector-action-target.v1",
        "title": "Minimal nonlinear action target for the universal collector",
        "classification": (
            "phenomenological_nonrelativistic_action_reconstruction_not_derived_"
            "from_current_holo_bulk"
        ),
        "claim_boundary": (
            "This certificate proves that the train-frozen galactic collector "
            "defines a single-valued constitutive function and a locally elliptic "
            "nonrelativistic scalar action for nonzero field. The operator becomes "
            "degenerately elliptic as the field tends to zero; this certificate "
            "does not prove global existence or uniqueness, derive the action from "
            "the five-dimensional Einstein-dilaton theory, establish a relativistic "
            "completion, or validate the response outside the exposed SPARC domain."
        ),
        "source": {
            "collector_path": str(COLLECTOR.relative_to(HERE.parents[1])),
            "collector_sha256": _sha256(COLLECTOR),
            "fit_origin": "SPARC training split only",
            "a0_m_s2": a0,
            "per_galaxy_parameters": 0,
        },
        "action": {
            "functional": (
                "S_NR=-integral d^3x [a0^2/(8*pi*G)*F(X)+rho*Phi], "
                "X=|grad Phi|^2/a0^2"
            ),
            "field_equation": (
                "div[mu(|grad Phi|/a0) grad Phi]=4*pi*G*rho, "
                "mu(sqrt(X))=dF/dX"
            ),
            "spherical_map": (
                "y=gN/a0; nu(y)=[1-exp(-sqrt(y))]^-1; "
                "x=g/a0=y*nu(y); mu(x)=1/nu(y)"
            ),
            "parametric_reconstruction": (
                "t=sqrt(y); mu=1-exp(-t); x=t^2/[1-exp(-t)]; "
                "F'(x^2)=mu"
            ),
            "deep_limit": "mu(x)~x and F(X)~(2/3)*X^(3/2)",
            "newtonian_limit": "mu->1 and F(X)~X+constant",
            "reference": {
                "label": "Bekenstein and Milgrom 1984 action class",
                "doi": "10.1086/162570",
                "url": "https://articles.adsabs.harvard.edu/pdf/1984ApJ...286....7B",
            },
        },
        "action_reconstruction": action,
        "numerical_consistency_checks": {
            "constitutive_inversion_closure_max_relative_error": closure_error,
            "constitutive_inversion_target_x_max_relative_error": target_x_error,
            "checked_y_min": float(y_check[0]),
            "checked_y_max": float(y_check[-1]),
            "action_table_y_min": float(arrays["y"][0]),
            "action_table_y_max": float(arrays["y"][-1]),
            "dense_reconstruction_samples": int(arrays["t"].size),
            "spherical_plummer_pde": plummer_check,
            "evidence_boundary": (
                "These are independent numerical operations on the reconstructed "
                "constitutive table, not independent observational evidence or a "
                "general nonspherical PDE solution."
            ),
        },
        "scale_map": _scale_inventory(a0),
        "galactic_readout": {
            "collector_test_chi2_per_point": collector["metrics"]["collector"]
            ["test"]["chi2_per_point"],
            "collector_test_median_absolute_fractional_velocity_error": (
                collector["metrics"]["collector"]["test"]
                ["median_absolute_fractional_velocity_error"]
            ),
            "scope": collector["scope"],
        },
        "next_gates": [
            "derive this nonlinear kinetic function from a microscopic HOLO sector",
            "construct a relativistic metric and lensing completion",
            "solve the full nonspherical field equation with unique 3D baryon maps",
            "establish weak-solution existence and uniqueness for the degenerate operator",
            "test Solar-System and laboratory observables including external fields",
            "freeze and evaluate a genuinely independent galaxy holdout",
        ],
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "passes": passes,
    }


def main() -> None:
    result = build()
    _write(OUTPUT, result)
    scales = result["scale_map"]["mass_implied_by_candidate_radius"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[0.6 kpc transition mass] "
        f"{scales['0.6_kpc']['source_mass_for_gN_equal_a0_msun']:.6g} Msun"
    )
    print(
        "[600 kpc transition mass] "
        f"{scales['600_kpc']['source_mass_for_gN_equal_a0_msun']:.6g} Msun"
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    if not result["passes"]["all"]:
        raise SystemExit("nonlinear collector action certificate failed")


if __name__ == "__main__":
    main()
