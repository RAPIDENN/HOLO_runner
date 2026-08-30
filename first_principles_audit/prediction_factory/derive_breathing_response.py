#!/usr/bin/env python3
"""Derive the linear space--time response of the corrected scalar carrier.

P6 is the zero-frequency slice of the positive-mode Yukawa benchmark.  This
certificate restores the time dependence without assigning a frequency from
observations: a harmonic source is evanescent below each mode threshold and
propagating above it.  A physical clock can fix ``ell`` only after the clock is
independently measured and associated prospectively with one selected mode.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
COMPLETION_RELATIVE = Path(
    "first_principles_audit/artifacts/minimal_probe_completion.json"
)
MATERIAL_RELATIVE = Path(
    "first_principles_audit/prediction_factory/material_predictions.json"
)
BOUNDARY_RELATIVE = Path(
    "first_principles_audit/prediction_factory/artifacts/"
    "superpotential_boundary_completion.json"
)
BOUNDARY_SHOOTING_RELATIVE = Path(
    "first_principles_audit/prediction_factory/artifacts/"
    "superpotential_boundary_shooting.json"
)
STIFF_FORCE_RELATIVE = Path(
    "first_principles_audit/prediction_factory/artifacts/"
    "stiff_boundary_force.json"
)
OUTPUT = HERE / "artifacts" / "breathing_response.json"

DRIVE_OVER_FIRST_THRESHOLD = (0.0, 0.5, 0.9, 0.99, 1.0, 1.01, 1.1, 1.7, 2.4)
STATIC_CHECK_X = (0.03, 0.1, 0.3, 1.0, 3.0, 10.0)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def radial_response(mu: float, nu: float, x: float) -> dict[str, Any]:
    """Return the outgoing radial Green-function factors.

    ``mu=m*ell``, ``nu=Omega*ell/c`` and ``x=r/ell``.  The force factor is
    normalized to the Newtonian radial force before multiplication by the
    mode residue ``alpha``.  The convention is exp(-i Omega t).
    """

    if not all(math.isfinite(value) for value in (mu, nu, x)):
        raise ValueError("mu, nu and x must be finite")
    if mu <= 0.0 or nu < 0.0 or x < 0.0:
        raise ValueError("require mu>0, nu>=0 and x>=0")

    threshold_tolerance = 32.0 * math.ulp(max(mu, nu, 1.0))
    difference = mu * mu - nu * nu
    if abs(difference) <= threshold_tolerance * max(mu * mu, 1.0):
        return {
            "regime": "threshold",
            "radial_number_times_ell": 0.0,
            "group_velocity_over_c": 0.0,
            "potential_factor": {"real": 1.0, "imag": 0.0, "magnitude": 1.0},
            "force_factor": {"real": 1.0, "imag": 0.0, "magnitude": 1.0},
        }

    if difference > 0.0:
        kappa = math.sqrt(difference)
        attenuation = math.exp(-kappa * x)
        force = (1.0 + kappa * x) * attenuation
        return {
            "regime": "evanescent",
            "radial_number_times_ell": kappa,
            "group_velocity_over_c": None,
            "potential_factor": {
                "real": attenuation,
                "imag": 0.0,
                "magnitude": attenuation,
            },
            "force_factor": {"real": force, "imag": 0.0, "magnitude": force},
        }

    wave_number = math.sqrt(-difference)
    phase = wave_number * x
    cosine = math.cos(phase)
    sine = math.sin(phase)
    # (1-i*k*r) exp(i*k*r), for the exp(-i*Omega*t) convention.
    force_real = cosine + phase * sine
    force_imag = sine - phase * cosine
    return {
        "regime": "propagating",
        "radial_number_times_ell": wave_number,
        "group_velocity_over_c": wave_number / nu,
        "potential_factor": {"real": cosine, "imag": sine, "magnitude": 1.0},
        "force_factor": {
            "real": force_real,
            "imag": force_imag,
            "magnitude": math.hypot(force_real, force_imag),
        },
    }


def physical_scale_from_first_mode(frequency_hz: float, mu_first: float) -> dict[str, float]:
    """Convert an independently fixed first-mode cyclic frequency to SI."""

    if not math.isfinite(frequency_hz) or frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive and finite")
    if not math.isfinite(mu_first) or mu_first <= 0.0:
        raise ValueError("mu_first must be positive and finite")
    speed_of_light_m_s = 299_792_458.0
    omega = 2.0 * math.pi * frequency_hz
    ell_m = mu_first * speed_of_light_m_s / omega
    return {
        "frequency_hz": frequency_hz,
        "period_s": 1.0 / frequency_hz,
        "omega_rad_s": omega,
        "ell_m": ell_m,
        "first_mode_static_range_m": ell_m / mu_first,
        "first_mode_range_light_time_s": 1.0 / omega,
    }


def _mode_table(modes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mu_first = float(modes[0]["mu_n"])
    rows = []
    for mode in modes:
        mu = float(mode["mu_n"])
        rows.append(
            {
                "mode_index_in_completion": int(mode["mode_index_in_completion"]),
                "mu_n": mu,
                "alpha_n": float(mode["alpha_n_2_beta_squared"]),
                "threshold_frequency_over_f1": mu / mu_first,
                "period_over_T1": mu_first / mu,
                "static_range_over_first_mode_range": mu_first / mu,
                "static_range_light_time_over_T1": mu_first / (2.0 * math.pi * mu),
            }
        )
    return rows


def _mass_clock(masses: list[float]) -> dict[str, Any]:
    if len(masses) < 2 or not all(
        math.isfinite(value) and value > 0.0 for value in masses
    ):
        raise ValueError("a positive multi-mode mass comb is required")
    if not all(right > left for left, right in zip(masses[:-1], masses[1:])):
        raise ValueError("mass comb must be strictly ordered")
    first = masses[0]
    ratios = [value / first for value in masses]
    gaps = [right - left for left, right in zip(ratios[:-1], ratios[1:])]
    return {
        "anchor_definition": (
            "f1 denotes the cyclic rest frequency of the first stiff-boundary mode"
        ),
        "ell_over_c_times_T1": first / (2.0 * math.pi),
        "modes": [
            {
                "mode_index": index,
                "mu_n": value,
                "threshold_frequency_over_f1": ratio,
                "period_over_T1": 1.0 / ratio,
                "static_range_over_first_mode_range": 1.0 / ratio,
            }
            for index, (value, ratio) in enumerate(zip(masses, ratios))
        ],
        "adjacent_resolution": {
            "adjacent_threshold_gaps_over_f1": gaps,
            "minimum_gap_over_f1": min(gaps),
            "minimum_first_zero_duration_over_T1": 1.0 / min(gaps),
            "warning": (
                "first-zero separation is spectral resolution, not a detection time"
            ),
        },
    }


def build() -> dict[str, Any]:
    completion_path = REPO / COMPLETION_RELATIVE
    material_path = REPO / MATERIAL_RELATIVE
    boundary_path = REPO / BOUNDARY_RELATIVE
    boundary_shooting_path = REPO / BOUNDARY_SHOOTING_RELATIVE
    stiff_force_path = REPO / STIFF_FORCE_RELATIVE
    completion = _read(completion_path)
    material_report = _read(material_path)
    material = material_report["payload"]
    boundary = _read(boundary_path)
    boundary_shooting = _read(boundary_shooting_path)
    stiff_force = _read(stiff_force_path)

    if completion.get("passes", {}).get("all") is not True:
        raise RuntimeError("minimal probe completion is not certified")
    if completion.get("observational_inputs_read") != []:
        raise RuntimeError("minimal probe completion is not observationally blind")
    if material.get("provenance", {}).get("observational_inputs_read") != []:
        raise RuntimeError("material prediction is not observationally blind")
    if material.get("classification") != "prospective_dimensionless_prediction_not_detection":
        raise RuntimeError("unexpected material-prediction classification")
    if boundary.get("passes", {}).get("all") is not True:
        raise RuntimeError("microscopic boundary certificate is not certified")
    if boundary_shooting.get("passes", {}).get("all") is not True:
        raise RuntimeError("boundary shooting verification is not certified")
    if boundary.get("observational_inputs_read") != []:
        raise RuntimeError("boundary certificate is not observationally blind")
    if stiff_force.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff force certificate is not certified")
    if stiff_force.get("observational_inputs_read") != []:
        raise RuntimeError("stiff force certificate is not observationally blind")

    modes = material["positive_modes"]
    if len(modes) != 6:
        raise ValueError("expected six positive benchmark modes")
    mus = [float(mode["mu_n"]) for mode in modes]
    alphas = [float(mode["alpha_n_2_beta_squared"]) for mode in modes]
    if not (
        all(math.isfinite(value) and value > 0.0 for value in mus + alphas)
        and all(right > left for left, right in zip(mus[:-1], mus[1:]))
    ):
        raise ValueError("invalid positive-mode table")

    mu_first = mus[0]
    drive_map = []
    regimes_seen: set[str] = set()
    for drive_ratio in DRIVE_OVER_FIRST_THRESHOLD:
        nu = drive_ratio * mu_first
        responses = []
        for mode, mu in zip(modes, mus):
            response = radial_response(mu, nu, 1.0)
            regimes_seen.add(response["regime"])
            responses.append(
                {
                    "mode_index_in_completion": int(mode["mode_index_in_completion"]),
                    **response,
                }
            )
        drive_map.append(
            {
                "drive_frequency_over_f1": drive_ratio,
                "nu_Omega_ell_over_c": nu,
                "responses_at_x_1": responses,
            }
        )

    static_errors = []
    for x in STATIC_CHECK_X:
        dynamic = sum(
            alpha * radial_response(mu, 0.0, x)["force_factor"]["real"]
            for alpha, mu in zip(alphas, mus)
        )
        expected = sum(
            alpha * (1.0 + mu * x) * math.exp(-mu * x)
            for alpha, mu in zip(alphas, mus)
        )
        static_errors.append(abs(dynamic - expected))

    gap_rows = []
    for left, right in zip(mus[:-1], mus[1:]):
        gap_over_f1 = (right - left) / mu_first
        gap_rows.append(
            {
                "adjacent_threshold_gap_over_f1": gap_over_f1,
                "rectangular_window_first_zero_duration_over_T1": 1.0 / gap_over_f1,
            }
        )
    minimum_gap = min(row["adjacent_threshold_gap_over_f1"] for row in gap_rows)
    stiff_masses = [
        float(value)
        for value in boundary["stiff_candidate"]["spectrum"]["masses_mu"]
    ]
    stiff_clock = _mass_clock(stiff_masses)
    stiff_spectrum = stiff_force["spectrum_and_force"]
    stiff_force_masses = [float(value) for value in stiff_spectrum["masses_mu"]]
    stiff_alphas = [
        float(value) for value in stiff_spectrum["alpha_uv_2_beta_squared"]
    ]
    if len(stiff_force_masses) != len(stiff_masses) or not all(
        math.isclose(left, right, rel_tol=2.0e-4, abs_tol=1.0e-8)
        for left, right in zip(stiff_force_masses, stiff_masses)
    ):
        raise RuntimeError("stiff force and junction spectra disagree")
    for row, alpha in zip(stiff_clock["modes"], stiff_alphas):
        row["alpha_n_2_beta_squared"] = alpha

    stiff_drive_map = []
    stiff_regimes_seen: set[str] = set()
    stiff_first = stiff_force_masses[0]
    for drive_ratio in DRIVE_OVER_FIRST_THRESHOLD:
        nu = drive_ratio * stiff_first
        responses = []
        for mode_index, (mu, alpha) in enumerate(
            zip(stiff_force_masses, stiff_alphas)
        ):
            response = radial_response(mu, nu, 1.0)
            stiff_regimes_seen.add(response["regime"])
            responses.append(
                {
                    "mode_index": mode_index,
                    "alpha_n_2_beta_squared": alpha,
                    **response,
                }
            )
        stiff_drive_map.append(
            {
                "drive_frequency_over_f1": drive_ratio,
                "nu_Omega_ell_over_c": nu,
                "responses_at_x_1": responses,
            }
        )

    stiff_static_errors = []
    for x in STATIC_CHECK_X:
        dynamic = sum(
            alpha * radial_response(mu, 0.0, x)["force_factor"]["real"]
            for alpha, mu in zip(stiff_alphas, stiff_force_masses)
        )
        expected = sum(
            alpha * (1.0 + mu * x) * math.exp(-mu * x)
            for alpha, mu in zip(stiff_alphas, stiff_force_masses)
        )
        stiff_static_errors.append(abs(dynamic - expected))

    passes = {
        "certified_blind_inputs": True,
        "six_positive_modes": len(modes) == 6,
        "static_p6_recovered": max(static_errors) <= 1.0e-18,
        "evanescent_threshold_propagating_regimes_present": regimes_seen
        == {"evanescent", "threshold", "propagating"},
        "frequency_comb_strictly_ordered": all(
            right > left for left, right in zip(mus[:-1], mus[1:])
        ),
        "minimal_superpotential_boundary_rejected": (
            boundary["minimal_superpotential_matching"]["g_minus_over_a"] == 0.0
            and boundary["minimal_superpotential_matching"]["g_plus_over_a"] == 0.0
        ),
        "stiff_boundary_comb_independently_verified": (
            boundary_shooting["passes"]["all"]
            and len(stiff_clock["modes"]) == len(boundary_shooting["modes"])
        ),
        "stiff_force_residues_available_and_positive": (
            len(stiff_alphas) == len(stiff_masses)
            and all(value > 0.0 for value in stiff_alphas)
            and math.isclose(
                sum(stiff_alphas),
                float(stiff_spectrum["sum_alpha_short_distance"]),
                rel_tol=2.0e-14,
            )
        ),
        "stiff_static_force_recovered": max(stiff_static_errors) <= 1.0e-18,
        "stiff_dynamic_regimes_present": stiff_regimes_seen
        == {"evanescent", "threshold", "propagating"},
    }
    passes["all"] = all(passes.values())

    result = {
        "schema": "holo.breathing-response.v1",
        "title": "P7 conditional space-time breathing response",
        "classification": (
            "derived_dynamic_response_with_microscopic_stiff_candidate_not_detection"
        ),
        "inputs": {
            "minimal_probe_completion": {
                "path": COMPLETION_RELATIVE.as_posix(),
                "sha256": _sha256(completion_path),
            },
            "material_prediction": {
                "path": MATERIAL_RELATIVE.as_posix(),
                "sha256": _sha256(material_path),
                "payload_sha256": material_report["integrity"]["payload_sha256"],
            },
            "superpotential_boundary_completion": {
                "path": BOUNDARY_RELATIVE.as_posix(),
                "sha256": _sha256(boundary_path),
            },
            "independent_boundary_shooting": {
                "path": BOUNDARY_SHOOTING_RELATIVE.as_posix(),
                "sha256": _sha256(boundary_shooting_path),
            },
            "stiff_boundary_force": {
                "path": STIFF_FORCE_RELATIVE.as_posix(),
                "sha256": _sha256(stiff_force_path),
            },
        },
        "observational_inputs_read": [],
        "historical_frequency_values_read": [],
        "equations": {
            "four_dimensional_mode": "(partial_t^2-c^2 nabla^2+omega_n^2) phi_n = source_n",
            "rest_frequency": "omega_n=c*mu_n/ell",
            "dimensionless_drive": "nu=Omega*ell/c",
            "evanescent_below_threshold": "kappa_n*ell=sqrt(mu_n^2-nu^2), G_n proportional exp(-kappa_n*r)/r",
            "outgoing_above_threshold": "k_n*ell=sqrt(nu^2-mu_n^2), G_n proportional exp(i*k_n*r)/r",
            "group_velocity": "v_g/c=sqrt(1-(omega_n/Omega)^2), Omega>omega_n",
            "clock_to_length_if_mode_1_is_fixed": "ell=mu_1*c/(2*pi*f_1)",
            "finite_coherence_resolution": "a rectangular duration T has first spectral zero at |Delta f|=1/T",
            "damped_ring_up_if_Q_is_supplied": "tau_ring=2Q/omega=Q/(pi*f)",
        },
        "interpretation": {
            "static_relation": (
                "the canonically normalized stiff force is exactly the Omega=0 "
                "slice of the current response; legacy P6 is retained separately "
                "as a trace-only benchmark"
            ),
            "breathing_effect": (
                "A periodic source changes the spatial inverse range below threshold and "
                "launches an outgoing massive wave above threshold; the static SPARC P6 "
                "curve does not test this time-dependent channel."
            ),
            "causal_timing": (
                "The signal front cannot arrive before r/c. A narrow-band propagating "
                "packet travels at v_g<c; steady response additionally requires source "
                "coherence and, for a damped resonator, its independently measured ring-up time."
            ),
        },
        "correlated_mode_clock": stiff_clock,
        "microscopic_boundary_update": {
            "minimal_superpotential_matching": {
                "g_minus_over_a": 0.0,
                "g_plus_over_a": 0.0,
                "result": (
                    "rejected for a finite-range Yukawa force because a massless "
                    "gauge-invariant scalar is required"
                ),
            },
            "stiff_stabilized_candidate": {
                "selection_status": (
                    "parameter-free limiting candidate, not selected by the bulk"
                ),
                "clock": stiff_clock,
                "independent_shooting_maximum_mass_relative_difference": (
                    boundary_shooting["maximum_mass_relative_difference"]
                ),
                "absolute_force_residues_available": True,
                "force_residues_alpha": stiff_alphas,
                "sum_alpha_short_distance": sum(stiff_alphas),
                "maximum_baryonic_acceleration_multiplier": (
                    1.0 + sum(stiff_alphas)
                ),
                "normalization_source": (
                    "quadratic gauge-invariant scalar action and UV matter vertex; "
                    "no historical NN trace residues reused"
                ),
            },
            "provisional_trace_benchmark": (
                "the original P6/P7 NN comb is retained only as a conditional "
                "trace-carrier benchmark"
            ),
        },
        "drive_phase_map": {
            "radius": "x=r/ell=1",
            "rows": stiff_drive_map,
        },
        "static_recovery": {
            "x_values": list(STATIC_CHECK_X),
            "maximum_absolute_error": max(stiff_static_errors),
            "force": "canonically normalized stiff-boundary candidate",
        },
        "provisional_trace_benchmark": {
            "status": "legacy P6/P7 NN comb retained for numerical genealogy only",
            "clock": {
                "anchor_definition": "f1 denotes the first positive NN benchmark mode",
                "ell_over_c_times_T1": mu_first / (2.0 * math.pi),
                "modes": _mode_table(modes),
                "adjacent_resolution": {
                    "rows": gap_rows,
                    "minimum_gap_over_f1": minimum_gap,
                    "minimum_first_zero_duration_over_T1": 1.0 / minimum_gap,
                },
            },
            "drive_phase_rows": drive_map,
            "static_maximum_absolute_error": max(static_errors),
        },
        "physical_closure_gates": {
            "boundary": (
                "minimal superpotential matching is rejected; select or derive "
                "finite positive brane curvatures, or prospectively declare the "
                "stiff limit, before interpreting a physical branch"
            ),
            "clock": "measure an independent frequency and identify its mode before using ell=mu*c/omega",
            "source": "supply source modulation or ambient occupation amplitude, phase and coherence time",
            "propagation": "supply damping or linewidth and source-detector separation",
            "detector": "supply a calibrated response and noise covariance from a system without a shared reference channel",
        },
        "legacy_frequency_adjudication": {
            "one_over_600_code_units": "not an SI frequency and not used",
            "old_optical_to_microwave_cross_coherence": "shared-reference engineering observable, not an independent universal-field test and not used",
        },
        "passes": passes,
        "evidence_boundary": (
            "This certificate proves the linear space-time transfer law, rejects the "
            "minimal superpotential boundary through its massless scalar, and adds an "
            "independently verified stiff-boundary frequency comb with canonically "
            "normalized matter-force residues. It does not select that limit, assign "
            "ell or hertz, fix a source occupation, or establish an interaction in "
            "observed data."
        ),
    }
    if not passes["all"]:
        raise RuntimeError(f"breathing response failed: {passes}")
    return result


def main() -> None:
    result = build()
    _write(OUTPUT, result)
    print(f"[breathing-response] {OUTPUT}")
    print(f"[classification] {result['classification']}")
    print(f"[passes] {result['passes']}")


if __name__ == "__main__":
    main()
