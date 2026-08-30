#!/usr/bin/env python3
"""Derive the spectral density required by a Y^(3/2) constitutive term.

For Y>0,

  (2/3)Y^(3/2) = (2/(3*pi)) int_0^inf ds s^(-1/2) Y^2/(Y+s)
                   = (4/(3*pi)) int_0^inf dm Y^2/(Y+m^2).

Thus an exact Stieltjes representation needs a gapless continuum with constant
density per mass.  Finite positive pole sums are analytic and can only pass
through slope 3/2 over a bounded crossover.  This mathematical representation
does not prove that stable Gaussian bulk exchange generates the local positive
operator; eliminating a real Gaussian auxiliary gives the opposite stationary
sign, and a momentum continuum is generally nonlocal rather than amplitude
dependent.
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
STIFF = HERE / "artifacts" / "stiff_boundary_force.json"
TRICRITICAL = HERE / "artifacts" / "tricritical_constitutive_bridge.json"
ENVELOPE = HERE / "artifacts" / "collector_legendre_envelope.json"
OUTPUT = HERE / "artifacts" / "collective_spectral_bridge.json"


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


def cutoff_continuum_density(
    gradient_y: np.ndarray, mass_ir: float, mass_uv: float
) -> np.ndarray:
    """Return the exact constant-density continuum between two mass cutoffs."""

    y = np.asarray(gradient_y, dtype=float)
    if np.any(~np.isfinite(y)) or np.any(y <= 0.0):
        raise ValueError("Y must be positive and finite")
    if not (0.0 <= mass_ir < mass_uv < math.inf):
        raise ValueError("cutoffs must satisfy 0<=mass_ir<mass_uv<inf")
    root = np.sqrt(y)
    return (4.0 / (3.0 * np.pi)) * y**1.5 * (
        np.arctan(mass_uv / root) - np.arctan(mass_ir / root)
    )


def finite_pole_density(
    gradient_y: np.ndarray, masses: np.ndarray, weights: np.ndarray
) -> np.ndarray:
    """Evaluate sum_n w_n Y^2/(Y+m_n^2) with positive poles."""

    y = np.asarray(gradient_y, dtype=float)
    m = np.asarray(masses, dtype=float)
    w = np.asarray(weights, dtype=float)
    if np.any(y <= 0.0) or np.any(m <= 0.0) or np.any(w <= 0.0):
        raise ValueError("Y, masses and weights must be positive")
    if m.ndim != 1 or w.shape != m.shape:
        raise ValueError("masses and weights must be equal-length vectors")
    return np.sum(
        w[:, None] * y[None, :] ** 2 / (y[None, :] + m[:, None] ** 2),
        axis=0,
    )


def _log_slope(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.gradient(np.log(y), np.log(x), edge_order=2)


def build() -> dict[str, Any]:
    stiff = _read(STIFF)
    tricritical = _read(TRICRITICAL)
    envelope = _read(ENVELOPE)
    if stiff["passes"]["all"] is not True:
        raise RuntimeError("stiff spectrum must be certified")
    if tricritical["checks"]["all"] is not True:
        raise RuntimeError("tricritical bridge must be certified")
    if envelope["passes"]["all"] is not True:
        raise RuntimeError("collector envelope must be certified")

    spectrum = stiff["spectrum_and_force"]
    masses = np.asarray(spectrum["masses_mu"], dtype=float)
    weights = np.asarray(spectrum["alpha_uv_2_beta_squared"], dtype=float)
    y = np.logspace(-6.0, 6.0, 12000)
    finite = finite_pole_density(y, masses, weights)
    finite_slope = _log_slope(y, finite)
    closest = int(np.argmin(np.abs(finite_slope - 1.5)))
    mimic = np.abs(finite_slope - 1.5) <= 0.05
    mimic_indices = np.flatnonzero(mimic)
    mimic_low = float(y[mimic_indices[0]])
    mimic_high = float(y[mimic_indices[-1]])
    mimic_dex = float(np.log10(mimic_high / mimic_low))

    mass_spacing = np.gradient(masses)
    inferred_mass_density = weights / mass_spacing
    density_cv = float(
        np.std(inferred_mass_density) / np.mean(inferred_mass_density)
    )

    mass_ir = 1.0e-3
    mass_uv = 1.0e3
    continuum = cutoff_continuum_density(y, mass_ir, mass_uv)
    continuum_slope = _log_slope(y, continuum)
    continuum_window = np.abs(continuum_slope - 1.5) <= 0.05
    continuum_indices = np.flatnonzero(continuum_window)
    continuum_low = float(y[continuum_indices[0]])
    continuum_high = float(y[continuum_indices[-1]])

    anchors = np.logspace(-8.0, 8.0, 64)
    near_full = cutoff_continuum_density(anchors, 0.0, 1.0e30)
    exact = (2.0 / 3.0) * anchors**1.5
    exact_error = float(np.max(np.abs(near_full / exact - 1.0)))

    finite_first = np.sum(
        weights[:, None]
        * y[None, :]
        * (y[None, :] + 2.0 * masses[:, None] ** 2)
        / (y[None, :] + masses[:, None] ** 2) ** 2,
        axis=0,
    )
    finite_second = np.sum(
        weights[:, None]
        * 2.0
        * masses[:, None] ** 4
        / (y[None, :] + masses[:, None] ** 2) ** 3,
        axis=0,
    )

    checks = {
        "certified_inputs": True,
        "constant_mass_density_recovers_two_thirds_y_three_halves": exact_error < 2.0e-14,
        "finite_positive_tower_is_monotone_and_convex": bool(
            np.min(finite_first) > 0.0 and np.min(finite_second) > 0.0
        ),
        "finite_tower_three_halves_is_only_a_narrow_crossover": mimic_dex < 0.25,
        "stiff_residue_density_is_not_constant": density_cv > 0.5,
        "cutoff_continuum_has_a_resolved_scaling_window": bool(
            continuum_low < 100.0 * mass_ir**2
            and continuum_high > 0.01 * mass_uv**2
        ),
        "target_transverse_and_longitudinal_coefficients_positive": True,
        "no_observational_tables_read": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "gapless_continuum_present_in_current_compact_spectrum": False,
        "constant_positive_density_per_mass_derived": False,
        "positive_local_stieltjes_kernel_generated_by_healthy_tree_exchange": False,
        "momentum_spectral_continuum_reduced_to_local_amplitude_operator": False,
        "ir_and_uv_cutoffs_derived_without_target_tuning": False,
        "a0_matter_normalization_and_lensing_derived": False,
        "physical_completion": False,
    }

    return {
        "schema": "holo.collective-spectral-bridge.v1",
        "title": "Gapless spectral bridge to the three-halves constitutive power",
        "classification": (
            "exact_positive_stieltjes_representation;"
            "not_generated_by_current_finite_gaussian_tower"
        ),
        "sources": {
            "stiff_force": {
                "path": str(STIFF.relative_to(REPO)),
                "sha256": _sha256(STIFF),
            },
            "tricritical_bridge": {
                "path": str(TRICRITICAL.relative_to(REPO)),
                "sha256": _sha256(TRICRITICAL),
            },
            "collector_envelope": {
                "path": str(ENVELOPE.relative_to(REPO)),
                "sha256": _sha256(ENVELOPE),
            },
            "observational_inputs_read": [],
        },
        "exact_representation": {
            "mass_squared_measure": (
                "P(Y)=2/(3*pi)*integral_0^infinity ds*s^(-1/2)*Y^2/(Y+s)"
            ),
            "mass_measure": (
                "P(Y)=4/(3*pi)*integral_0^infinity dm*Y^2/(Y+m^2)"
            ),
            "required_density_per_mass": "rho_m=4/(3*pi), constant",
            "cutoff_formula": (
                "P_[eps,Lambda]=4/(3*pi)*Y^(3/2)*"
                "[atan(Lambda/sqrt(Y))-atan(eps/sqrt(Y))]"
            ),
            "scaling_window": "eps^2 << Y << Lambda^2",
            "below_ir_gap": "P is proportional to Y^2",
            "above_uv_cutoff": "P is proportional to Y",
            "maximum_full_integral_relative_error": exact_error,
        },
        "current_seven_mode_test": {
            "conditional_identification": (
                "Use stiff alpha_n as positive kernel weights only as a shape test; "
                "this is not the static Yukawa force formula."
            ),
            "closest_three_halves_Y": float(y[closest]),
            "closest_log_slope": float(finite_slope[closest]),
            "within_0p05_Y_interval": [mimic_low, mimic_high],
            "within_0p05_log10_width_dex": mimic_dex,
            "inferred_weight_over_mass_spacing": inferred_mass_density.tolist(),
            "coefficient_of_variation_vs_constant_density": density_cv,
            "conclusion": (
                "The finite tower passes through slope 3/2 only during a narrow "
                "crossover and is not a discretization of the required constant "
                "gapless density."
            ),
        },
        "cutoff_continuum_test": {
            "mass_ir": mass_ir,
            "mass_uv": mass_uv,
            "within_0p05_Y_interval": [continuum_low, continuum_high],
        },
        "stability": {
            "target_transverse_coefficient": "P'(Y)=sqrt(Y)>0",
            "target_longitudinal_coefficient": "P'(Y)+2*Y*P''(Y)=2*sqrt(Y)>0",
            "boundary": "both vanish at Y=0, so ellipticity is degenerate",
            "finite_positive_tower": "P_N'(Y)>0 and P_N''(Y)>0 for Y>0",
        },
        "generation_sign_and_locality": {
            "tree_gaussian_elimination": (
                "stationary elimination of 1/2*q*K*q-J*q gives -1/2*J*K^-1*J"
            ),
            "sign_warning": (
                "A positive Stieltjes identity is not a healthy bulk-generation "
                "proof. Reversing the Gaussian sign requires an imaginary coupling, "
                "a ghost, or an independently derived local counterterm."
            ),
            "locality_warning": (
                "A continuum over spacetime momentum usually produces a nonlocal "
                "fractional operator. P(Y) is local but nonlinear in field amplitude; "
                "equating the two requires a collective constraint not present in "
                "the current quadratic pole sum."
            ),
        },
        "old_vs_new": {
            "old": "seven fixed gapped poles; linear superposition; source exponent one",
            "new_requirement": (
                "gapless constant spectral density or a non-Gaussian tricritical "
                "collective coordinate; local nonlinear amplitude response"
            ),
        },
        "physical_gates": physical_gates,
        "decisive_next_calculation": (
            "Take a decompactification or critical boundary limit before mode "
            "truncation, derive its signed spectral measure and the full nonlinear "
            "constraint action, and test whether it produces a local q^2*Y vertex "
            "rather than ordinary nonlocal Gaussian exchange."
        ),
        "checks": checks,
        "software": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    finite = result["current_seven_mode_test"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[seven modes] slope=3/2 near Y={:.6g}; width={:.6g} dex".format(
            finite["closest_three_halves_Y"],
            finite["within_0p05_log10_width_dex"],
        )
    )
    print(f"[physical completion] {result['physical_gates']['physical_completion']}")
    print(f"[spectral certificate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
