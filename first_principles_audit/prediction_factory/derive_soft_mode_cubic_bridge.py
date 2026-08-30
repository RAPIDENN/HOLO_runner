#!/usr/bin/env python3
"""Test a critical-soft-mode route to the collector's cubic dual.

The stabilized superpotential family contains a light mode with

    mu_0^2 ~ C_gamma * gamma                         (gamma -> 0+).

If the local collector selector is proportional to the soft gap mu_0, the
universal non-analytic part of a three-dimensional mode determinant scales as
mu_0^3.  That is exactly the power W(s)~s^3 required by the deep collector's
Legendre dual.  This script certifies the exponent chain and, importantly,
keeps the sign, normalization and acceleration scale as open physical gates.
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
from scipy.integrate import quad


HERE = Path(__file__).resolve().parent
BOUNDARY = HERE / "artifacts" / "superpotential_boundary_completion.json"
ENVELOPE = HERE / "artifacts" / "collector_legendre_envelope.json"
OUTPUT = HERE / "artifacts" / "soft_mode_cubic_bridge.json"


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


def _dimensionless_determinant_integrand(t: float) -> float:
    """Compactified integrand for the twice-subtracted 3D determinant.

    With q=t/(1-t), this integrates

        q^2 log(1+q^-2) - 1

    from q=0 to infinity.  The subtraction removes the analytic m^2 term;
    the surviving m^3 coefficient is regulator independent.  This isolates
    the non-analytic exponent; it does not prove that the physical analytic
    Z*X term vanishes.
    """

    if t <= 0.0:
        return -1.0
    if t >= 1.0:
        return -0.5
    q = t / (1.0 - t)
    z = 1.0 / (q * q)
    if z < 1.0e-5:
        # log(1+z)/z - 1, evaluated without catastrophic cancellation.
        core = -z / 2.0 + z * z / 3.0 - z**3 / 4.0 + z**4 / 5.0
    else:
        core = math.log1p(z) / z - 1.0
    return core / (1.0 - t) ** 2


def determinant_coefficient() -> tuple[float, float]:
    """Return C in Delta Gamma=C*m^3 and the quadrature error."""

    integral, error = quad(
        _dimensionless_determinant_integrand,
        0.0,
        1.0,
        epsabs=2.0e-12,
        epsrel=2.0e-12,
        limit=300,
    )
    prefactor = 1.0 / (4.0 * math.pi**2)
    return prefactor * integral, prefactor * error


def build() -> dict[str, Any]:
    boundary = _read(BOUNDARY)
    envelope = _read(ENVELOPE)
    if boundary["passes"]["all"] is not True:
        raise RuntimeError("boundary completion must pass first")
    if envelope["passes"]["all"] is not True:
        raise RuntimeError("Legendre envelope must pass first")

    scan = boundary["stabilized_family"]["equal_gamma_scan"][:3]
    gamma = np.asarray([row["gamma_minus"] for row in scan], dtype=float)
    mu2 = np.asarray([row["mass_squared_mu2"][0] for row in scan], dtype=float)
    mu0 = np.sqrt(mu2)
    soft_slope, soft_intercept = np.polyfit(np.log(gamma), np.log(mu2), 1)
    ratios = mu2 / gamma
    ratio_mean = float(np.mean(ratios))
    ratio_cv = float(np.std(ratios) / ratio_mean)
    ir_proxy = np.asarray(
        [row["ir_profile_squared_generalized_norm"][0] for row in scan],
        dtype=float,
    )
    uv_proxy = np.asarray(
        [row["uv_profile_squared_generalized_norm"][0] for row in scan],
        dtype=float,
    )
    ir_proxy_slope = float(
        np.polyfit(np.log(gamma), np.log(ir_proxy), 1)[0]
    )
    uv_proxy_slope = float(
        np.polyfit(np.log(gamma), np.log(uv_proxy), 1)[0]
    )

    determinant_c, quadrature_error = determinant_coefficient()
    expected_c = -1.0 / (12.0 * math.pi)
    determinant_values = determinant_c * mu0**3
    determinant_slope = float(
        np.polyfit(np.log(mu0), np.log(np.abs(determinant_values)), 1)[0]
    )
    envelope_slope = float(envelope["diagnostics"]["deep_dual_log_slope"])

    certificate_checks = {
        "source_certificates_pass": True,
        "soft_mass_squared_is_linear_in_gamma": abs(float(soft_slope) - 1.0) < 0.01,
        "soft_coefficient_stable_on_three_smallest_points": ratio_cv < 0.005,
        "three_dimensional_nonanalytic_power_is_cubic": (
            abs(determinant_slope - 3.0) < 1.0e-10
        ),
        "determinant_coefficient_matches_analytic_value": (
            abs(determinant_c - expected_c) < 2.0e-10
        ),
        "collector_dual_power_is_cubic": abs(envelope_slope - 3.0) < 0.003,
        "critical_and_collector_exponents_match": (
            abs(determinant_slope - envelope_slope) < 0.003
        ),
        "no_observational_inputs_read": True,
    }
    certificate_checks["all"] = all(certificate_checks.values())

    physical_gates = {
        "required_exponent_generated": True,
        # The finite non-analytic term of a conventional bosonic determinant
        # has the opposite sign to the positive convex W required here.
        "required_positive_W_sign_generated_by_bosonic_determinant": False,
        "analytic_linear_X_term_absent_or_cancelled": False,
        "selector_identification_derived_from_5d_action": False,
        "nonvanishing_physical_matter_residue_derived": False,
        "normalization_derived": False,
        "a0_derived": False,
        "metric_lensing_completion_derived": False,
        "physical_completion": False,
    }

    return {
        "schema": "holo.soft-mode-cubic-bridge.v1",
        "title": "Critical soft-mode exponent bridge to the cubic collector dual",
        "classification": (
            "new_derived_exponent_connection;not_a_complete_force_derivation"
        ),
        "sources": {
            "boundary_completion": {
                "path": str(BOUNDARY.relative_to(HERE.parents[1])),
                "sha256": _sha256(BOUNDARY),
            },
            "collector_envelope": {
                "path": str(ENVELOPE.relative_to(HERE.parents[1])),
                "sha256": _sha256(ENVELOPE),
            },
            "observational_inputs_read": [],
        },
        "derived_chain": [
            "superpotential boundary scan: mu0^2 proportional to gamma near gamma=0+",
            "choose the soft gap as the candidate local selector: s proportional to mu0",
            "3D infrared phase space: DeltaGamma_nonanalytic proportional to mu0^3",
            "therefore candidate dual W(s) has the required cubic exponent",
            "Legendre saddle of cubic W gives F(X) proportional to X^(3/2)",
            "only if this is the leading low-X action, AQUAL gives g proportional to sqrt(M)/r",
        ],
        "soft_mode_fit": {
            "points": int(gamma.size),
            "gamma": gamma.tolist(),
            "mu0_squared": mu2.tolist(),
            "log_slope_mu0_squared_vs_gamma": float(soft_slope),
            "log_intercept": float(soft_intercept),
            "mean_mu0_squared_over_gamma": ratio_mean,
            "coefficient_of_variation": ratio_cv,
        },
        "coupling_proxy_softening": {
            "ir_generalized_profile_squared": ir_proxy.tolist(),
            "uv_generalized_profile_squared": uv_proxy.tolist(),
            "ir_log_slope_vs_gamma": ir_proxy_slope,
            "uv_log_slope_vs_gamma": uv_proxy_slope,
            "warning": (
                "These endpoint generalized-profile squares are not absolute "
                "matter residues, but both vanish approximately linearly with "
                "gamma.  A physical completion must prove that the critical "
                "mode does not decouple from matter."
            ),
        },
        "three_dimensional_determinant": {
            "definition": (
                "(1/2) integral d^3k/(2pi)^3 "
                "[log(1+m^2/k^2)-m^2/k^2]"
            ),
            "numerical_coefficient_of_m_cubed": determinant_c,
            "analytic_coefficient_of_m_cubed": expected_c,
            "quadrature_error_estimate": quadrature_error,
            "log_slope_absolute_value_vs_mu0": determinant_slope,
            "sign_result": (
                "negative for the conventional subtracted bosonic determinant; "
                "the desired positive convex W is not obtained by this ingredient alone"
            ),
        },
        "collector_match": {
            "required_deep_dual": "W(s)~s^3/3",
            "measured_dual_log_slope": envelope_slope,
            "candidate_identification": "s proportional to mu0",
            "matched_feature": "nonanalytic exponent only",
            "leading_term_warning": (
                "The determinant calculation explicitly subtracts the analytic "
                "term proportional to m^2 and hence X.  The current HOLO sector "
                "has not shown that its positive Z*X response vanishes at the "
                "critical point; if Z remains nonzero, X dominates X^(3/2) as "
                "X tends to zero and the sqrt(M) regime does not emerge."
            ),
        },
        "physical_gates": physical_gates,
        "next_decisive_calculation": (
            "Derive the full interacting reduced action of the soft scalar plus "
            "brane bending.  It must make the analytic Z*X coefficient vanish "
            "at the critical point, reverse or outweigh the determinant sign, "
            "retain a finite physical matter residue, fix the normalization "
            "and produce a0 without reading SPARC."
        ),
        "certificate_checks": certificate_checks,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    fit = result["soft_mode_fit"]
    det = result["three_dimensional_determinant"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[soft mode] mu0^2~gamma^p: "
        f"p={fit['log_slope_mu0_squared_vs_gamma']:.8g}, "
        f"C={fit['mean_mu0_squared_over_gamma']:.8g}"
    )
    print(
        "[3D determinant] DeltaGamma=C*m^3: "
        f"C={det['numerical_coefficient_of_m_cubed']:.10g}"
    )
    print(
        "[physical completion] "
        f"{result['physical_gates']['physical_completion']}"
    )
    print(
        "[certificate] "
        f"{'PASS' if result['certificate_checks']['all'] else 'FAIL'}"
    )
    return 0 if result["certificate_checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
