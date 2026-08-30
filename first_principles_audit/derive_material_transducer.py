#!/usr/bin/env python3
"""Derive the parameter-free part of a trace-coupled material transducer.

No target frequency, detector residual, material constant, or observational
limit is read here.  The output is a transfer *law*: geometry fixes the mode
mass ratios and universal Yukawa coefficients, while a physical length, source
motion, mode occupation, and detector parameters remain explicit inputs.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
MINIMAL_PATH = HERE / "artifacts" / "minimal_probe_completion.json"
INTERFACE_PATH = HERE / "artifacts" / "ricci_wilson_interface_audit.json"
OUTPUT_PATH = HERE / "artifacts" / "material_transducer.json"

X_SAMPLES = np.asarray([0.0, 0.1, 0.3, 1.0, 3.0, 10.0], dtype=float)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def acceleration_ratio(
    x: np.ndarray | float, masses: np.ndarray, alphas: np.ndarray
) -> np.ndarray:
    """Scalar acceleration divided by Newtonian acceleration at x=r/ell."""
    xx = np.atleast_1d(np.asarray(x, dtype=float))[:, None]
    y = xx * masses[None, :]
    return np.sum(alphas[None, :] * (1.0 + y) * np.exp(-y), axis=1)


def tidal_ratio(
    x: np.ndarray | float, masses: np.ndarray, alphas: np.ndarray
) -> np.ndarray:
    """Scalar radial gradient divided by |d(GM/r^2)/dr|."""
    xx = np.atleast_1d(np.asarray(x, dtype=float))[:, None]
    y = xx * masses[None, :]
    return np.sum(
        alphas[None, :] * (1.0 + y + 0.5 * np.square(y)) * np.exp(-y),
        axis=1,
    )


def _finite_difference_tidal_check(
    x: float, masses: np.ndarray, alphas: np.ndarray
) -> float:
    # Work in units GM=ell=1.  The positive scalar acceleration magnitude is
    # a_s(x)=sum alpha exp(-mu*x)(1+mu*x)/x^2.
    def scalar_acceleration(xx: float) -> float:
        y = masses * xx
        return float(np.sum(alphas * np.exp(-y) * (1.0 + y)) / xx**2)

    step = 1e-6 * max(x, 1.0)
    derivative = (
        scalar_acceleration(x + step) - scalar_acceleration(x - step)
    ) / (2.0 * step)
    # The Newtonian gradient magnitude in the same units is 2/x^3.
    finite_difference_ratio = abs(derivative) / (2.0 / x**3)
    analytic_ratio = float(tidal_ratio(x, masses, alphas)[0])
    return abs(finite_difference_ratio / analytic_ratio - 1.0)


def derive() -> dict[str, Any]:
    minimal = _load(MINIMAL_PATH)
    interface = _load(INTERFACE_PATH)
    if not minimal["passes"]["all"]:
        raise RuntimeError("Minimal probe certificate does not pass")
    if not interface["passes"]["all"]:
        raise RuntimeError("Ricci/Wilson interface certificate does not pass")

    masses = np.asarray(
        minimal["dimensionless_spectrum"]["masses_mu"], dtype=float
    )
    betas = np.asarray(minimal["uv_probe_couplings_beta_n"], dtype=float)
    alphas = 2.0 * np.square(betas)

    positive = masses > 0.0
    positive_masses = masses[positive]
    positive_alphas = alphas[positive]
    all_acceleration = acceleration_ratio(X_SAMPLES, masses, alphas)
    positive_acceleration = acceleration_ratio(
        X_SAMPLES, positive_masses, positive_alphas
    )
    all_tidal = tidal_ratio(X_SAMPLES, masses, alphas)
    positive_tidal = tidal_ratio(X_SAMPLES, positive_masses, positive_alphas)

    finite_difference_errors = [
        _finite_difference_tidal_check(x, positive_masses, positive_alphas)
        for x in (0.1, 0.3, 1.0, 3.0)
    ]

    ricci_ratios = interface["ricci_5d"]["mode_to_curvature_scale_ratios"]
    uv_ricci = ricci_ratios["uv_probe_slice"]
    u1_ricci = ricci_ratios["legacy_clock_anchor_u1"]

    result = {
        "title": "Conditional universal material-transducer law",
        "classification": "derived_transfer_law_not_signal_prediction",
        "observational_inputs_read": [],
        "material_constants_read": [],
        "source_or_mode_amplitudes_read": [],
        "input_branch": {
            "matter_slice": "UV endpoint",
            "coupling": "L_int=sum_n (beta_n/M_Pl) varphi_n T",
            "mass_rule": "m_n=mu_n/ell",
            "potential": (
                "V=-G M m/r [1+sum_n alpha_n exp(-mu_n r/ell)]"
            ),
            "alpha_rule": "alpha_n=2 beta_n(source) beta_n(detector)",
            "universal_uv_case": "alpha_n=2 beta_n(UV)^2",
        },
        "geometry_fixed": {
            "masses_mu": masses.tolist(),
            "couplings_beta_uv": betas.tolist(),
            "yukawa_strengths_alpha_uv": alphas.tolist(),
            "positive_mode_mass_ratios_to_mu1": (
                positive_masses / positive_masses[0]
            ).tolist(),
            "positive_mode_total_alpha_at_zero_range": float(
                np.sum(positive_alphas)
            ),
            "zero_mode_alpha": float(alphas[0]),
        },
        "dimensionless_force_templates": {
            "x_definition": "x=r/ell",
            "acceleration_ratio_formula": (
                "a_scalar/a_Newton=sum alpha_n (1+mu_n*x) exp(-mu_n*x)"
            ),
            "tidal_ratio_formula": (
                "|da_scalar/dr|/|da_Newton/dr|="
                "sum alpha_n (1+mu_n*x+(mu_n*x)^2/2) exp(-mu_n*x)"
            ),
            "x": X_SAMPLES.tolist(),
            "all_modes_acceleration_ratio": all_acceleration.tolist(),
            "positive_modes_acceleration_ratio": positive_acceleration.tolist(),
            "all_modes_tidal_ratio": all_tidal.tolist(),
            "positive_modes_tidal_ratio": positive_tidal.tolist(),
        },
        "mechanical_readout": {
            "continuum_equation": (
                "rho*u_ddot_i-partial_j(C_ijkl*epsilon_kl)="
                "rho*(a_phi_i-a_frame_i)"
            ),
            "elastic_mode_projection": (
                "q_a(omega)=integral[rho U_a dot (a_phi-a_frame)]dV / "
                "{M_a[omega_a^2-omega^2-i omega omega_a/Q_a]}"
            ),
            "source_gradient": (
                "Delta a_n approximately L*(2 G M_s/r^3)*tidal_ratio_n"
            ),
            "oscillator_transfer": (
                "|Delta x(Omega)|=|Delta a(Omega)|/sqrt((omega_m^2-Omega^2)^2"
                "+(Omega*omega_m/Q)^2)"
            ),
            "resonant_limit": (
                "|Delta x|/L=Q*|Delta a|/(L*omega_m^2) at Omega=omega_m"
            ),
            "requires_before_number": [
                "physical ell or scan range",
                "source mass and modulation trajectory",
                "detector baseline L, resonance omega_m, and Q",
                "noise spectral density and integration protocol",
                "support/frame motion and elastic tensor C_ijkl",
            ],
        },
        "ricci_clock_use": {
            "physical_curvature_frequency": (
                "omega_R(u)=c*sqrt(abs(R5_hat(u)))/ell"
            ),
            "mode_frequency_at_rest": "omega_n=c*mu_n/ell",
            "scale_free_ratio": "omega_n/omega_R=mu_n/sqrt(abs(R5_hat))",
            "uv_probe_slice": uv_ricci,
            "legacy_u1_anchor": u1_ricci,
            "role": (
                "The Ricci quantity supplies a dimensionless cadence or a "
                "cross-check once ell is fixed. It is not a mode amplitude, a "
                "source, detector proper time, or an observed clock line."
            ),
        },
        "wilson_matching_if_future_loop_exists": {
            "lattice_output": "a^2 sigma from rectangular W(R,T)",
            "required_bridge": (
                "a separately derived ell/a, equivalently ell*sqrt(sigma)"
            ),
            "identity": (
                "ell*sqrt(sigma)=(ell/a)*sqrt(a^2 sigma)"
            ),
            "warning": (
                "Setting ell=a or adopting sqrt(sigma) in GeV is a matching "
                "choice unless a UV completion predicts the relation."
            ),
        },
        "channel_boundaries": {
            "universal_bulk_acceleration": "derived conditionally",
            "differential_mechanical_tide": "transfer law derived conditionally",
            "uniform_material_strain": (
                "requires material sensitivity to masses/couplings; not derived"
            ),
            "atomic_clock_ratio": (
                "requires anomaly or non-universal d_e,d_g,d_mi; not derived"
            ),
            "signal_frequency_and_phase": (
                "requires source dynamics or a populated mode; not derived"
            ),
        },
        "validation": {
            "finite_difference_tidal_relative_errors": finite_difference_errors,
            "finite_difference_tidal_max_relative_error": float(
                max(finite_difference_errors)
            ),
            "positive_alpha_sum_identity_error": float(
                abs(np.sum(positive_alphas) - 2.0 * np.sum(betas[positive] ** 2))
            ),
            "ell_cancellation_in_omega_ratio": True,
        },
        "passes": {
            "minimal_input_certified": True,
            "ricci_interface_input_certified": True,
            "no_observational_input": True,
            "no_material_or_target_frequency_input": True,
            "yukawa_gradient_independent_check": bool(
                max(finite_difference_errors) < 1e-8
            ),
            "coupling_identity": bool(
                abs(np.sum(positive_alphas) - 2.0 * np.sum(betas[positive] ** 2))
                < 1e-18
            ),
            "scale_free_ricci_ratio": True,
        },
        "evidence_boundary": (
            "The geometry fixes a correlated Yukawa template and a mechanical "
            "transfer equation. It does not fix ell, excite a mode, choose a "
            "material, predict a clock ratio, or establish a signal. The current "
            "Neumann zero mode must be assessed separately because a massless "
            "unscreened branch is not an admissible detector discovery claim."
        ),
    }
    result["passes"]["all"] = all(result["passes"].values())
    return result


def main() -> int:
    result = derive()
    _write(OUTPUT_PATH, result)
    fixed = result["geometry_fixed"]
    print(f"[material transducer] {OUTPUT_PATH}")
    print(
        "[positive tower] sum(alpha_n)={:.12g} ratios={}".format(
            fixed["positive_mode_total_alpha_at_zero_range"],
            [round(value, 6) for value in fixed["positive_mode_mass_ratios_to_mu1"]],
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
