#!/usr/bin/env python3
"""Build a prospective, dimensionless material-response prediction artifact.

The factory consumes only the six positive modes and their UV probe couplings
from ``minimal_probe_completion.json``.  It deliberately does not assign the
compactification length, a source history, detector properties, or any
observationally fitted coefficient.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
DEFAULT_INPUT = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "minimal_probe_completion.json"
)
DEFAULT_OUTPUT = SCRIPT_PATH.with_name("material_predictions.json")
DEFAULT_CHECKSUM = SCRIPT_PATH.with_name("material_predictions.sha256")

SCHEMA_VERSION = "holo.material-prediction-factory.v1"
CURVE_X_MIN = 1.0e-3
CURVE_X_MAX = 20.0
CURVE_SAMPLES = 241
DISTANCE_ANCHORS = (0.03, 0.1, 0.3, 1.0, 3.0, 10.0)
MECHANICAL_DETUNING_MIN = -10.0
MECHANICAL_DETUNING_MAX = 10.0
MECHANICAL_DETUNING_SAMPLES = 161


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def log_grid(low: float, high: float, count: int) -> list[float]:
    if not (low > 0.0 and high > low and count >= 2):
        raise ValueError("invalid logarithmic grid")
    lo = math.log(low)
    span = math.log(high) - lo
    return [math.exp(lo + span * i / (count - 1)) for i in range(count)]


def linear_grid(low: float, high: float, count: int) -> list[float]:
    if not (high > low and count >= 2):
        raise ValueError("invalid linear grid")
    return [low + (high - low) * i / (count - 1) for i in range(count)]


def _validate_modes(masses: Iterable[float], betas: Iterable[float]) -> list[dict[str, float | int]]:
    masses_list = [float(value) for value in masses]
    betas_list = [float(value) for value in betas]
    if len(masses_list) != len(betas_list):
        raise ValueError("mass and coupling arrays have different lengths")

    positive = [
        (mode_index, mu, beta)
        for mode_index, (mu, beta) in enumerate(zip(masses_list, betas_list))
        if mu > 0.0
    ]
    if len(positive) != 6:
        raise ValueError(f"expected exactly six positive modes, found {len(positive)}")
    if any(not (math.isfinite(mu) and math.isfinite(beta)) for _, mu, beta in positive):
        raise ValueError("non-finite mode input")
    if any(mu <= 0.0 or beta <= 0.0 for _, mu, beta in positive):
        raise ValueError("positive-mode masses and UV couplings must be positive")
    if any(positive[i + 1][1] <= positive[i][1] for i in range(len(positive) - 1)):
        raise ValueError("positive-mode masses must be strictly increasing")

    return [
        {
            "mode_index_in_completion": mode_index,
            "mu_n": mu,
            "beta_n_uv": beta,
            "alpha_n_2_beta_squared": 2.0 * beta * beta,
            "range_over_ell": 1.0 / mu,
        }
        for mode_index, mu, beta in positive
    ]


def response_at_x(modes: list[dict[str, float | int]], x: float) -> dict[str, float]:
    """Return point-source Yukawa corrections at x=r/ell.

    ``force_fraction`` is F_scalar/F_Newton.  ``gradient_fraction`` is
    |dF_scalar/dr|/|dF_Newton/dr|, where |dF_Newton/dr|=2 G M m/r^3.
    """

    if x < 0.0 or not math.isfinite(x):
        raise ValueError("x=r/ell must be finite and non-negative")

    potential_fraction = 0.0
    force_fraction = 0.0
    gradient_fraction = 0.0
    for mode in modes:
        mu = float(mode["mu_n"])
        alpha = float(mode["alpha_n_2_beta_squared"])
        y = mu * x
        attenuation = math.exp(-y)
        potential_fraction += alpha * attenuation
        force_fraction += alpha * (1.0 + y) * attenuation
        gradient_fraction += alpha * (1.0 + y + 0.5 * y * y) * attenuation

    return {
        "x_r_over_ell": x,
        "potential_over_newtonian_potential": potential_fraction,
        "force_over_newtonian_force": force_fraction,
        "radial_force_gradient_over_newtonian_gradient": gradient_fraction,
    }


def build_distance_ratios(
    modes: list[dict[str, float | int]],
    anchors: Iterable[float],
) -> dict[str, Any]:
    points = [response_at_x(modes, float(x)) for x in anchors]
    reference = next(point for point in points if math.isclose(point["x_r_over_ell"], 0.1))

    relative_to_reference = []
    for point in points:
        relative_to_reference.append(
            {
                "x_r_over_ell": point["x_r_over_ell"],
                "force_ratio_to_x_0p1": point["force_over_newtonian_force"]
                / reference["force_over_newtonian_force"],
                "gradient_ratio_to_x_0p1": point[
                    "radial_force_gradient_over_newtonian_gradient"
                ]
                / reference["radial_force_gradient_over_newtonian_gradient"],
            }
        )

    adjacent_decay_ratios = []
    for near, far in zip(points[:-1], points[1:]):
        adjacent_decay_ratios.append(
            {
                "near_x_r_over_ell": near["x_r_over_ell"],
                "far_x_r_over_ell": far["x_r_over_ell"],
                "force_at_far_over_near": far["force_over_newtonian_force"]
                / near["force_over_newtonian_force"],
                "gradient_at_far_over_near": far[
                    "radial_force_gradient_over_newtonian_gradient"
                ]
                / near["radial_force_gradient_over_newtonian_gradient"],
            }
        )

    return {
        "definition": "ratios use the positive-mode scalar correction only; source and detector masses cancel",
        "anchors_x_r_over_ell": [point["x_r_over_ell"] for point in points],
        "response_at_anchors": points,
        "relative_to_reference": relative_to_reference,
        "adjacent_decay_ratios": adjacent_decay_ratios,
    }


def build_mechanical_transfer() -> dict[str, Any]:
    curve = []
    for delta in linear_grid(
        MECHANICAL_DETUNING_MIN,
        MECHANICAL_DETUNING_MAX,
        MECHANICAL_DETUNING_SAMPLES,
    ):
        denominator = 1.0 + delta * delta
        real = 1.0 / denominator
        imag = -delta / denominator
        curve.append(
            {
                "delta_2Q_omega_minus_omega0_over_omega0": delta,
                "real": real,
                "imag": imag,
                "magnitude": 1.0 / math.sqrt(denominator),
                "phase_rad": -math.atan(delta),
                "power_gain": 1.0 / denominator,
            }
        )

    return {
        "classification": "universal_near_resonance_shape_not_a_detector_calibration",
        "exact_single_mode_equation": "q/F = [M_eff*omega_0^2*(1-s^2+i*s/Q)]^-1, s=omega/omega_0",
        "normalized_near_resonance_definition": "H_tilde(delta)=H/H(omega_0)=1/(1+i*delta), delta=2Q(omega-omega_0)/omega_0, Q>>1",
        "normalization": "unit magnitude and zero phase at resonance; M_eff, omega_0, Q, force overlap, and readout gain are not assigned",
        "curve": curve,
    }


def build_payload(input_path: Path = DEFAULT_INPUT) -> dict[str, Any]:
    completion = json.loads(input_path.read_text(encoding="utf-8"))
    if completion.get("observational_inputs_read") != []:
        raise ValueError("input completion is not observationally blind")
    if completion.get("historical_fitted_couplings_reused") != []:
        raise ValueError("input completion reuses fitted historical couplings")

    spectrum = completion["dimensionless_spectrum"]
    modes = _validate_modes(
        spectrum["masses_mu"],
        completion["uv_probe_couplings_beta_n"],
    )
    alpha_sum = sum(float(mode["alpha_n_2_beta_squared"]) for mode in modes)
    curve = [response_at_x(modes, x) for x in log_grid(CURVE_X_MIN, CURVE_X_MAX, CURVE_SAMPLES)]

    input_relative = input_path.resolve().relative_to(REPO_ROOT).as_posix()
    generator_relative = SCRIPT_PATH.relative_to(REPO_ROOT).as_posix()
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "classification": "prospective_dimensionless_prediction_not_detection",
        "provenance": {
            "input_completion": input_relative,
            "input_completion_sha256": sha256_file(input_path),
            "generator": generator_relative,
            "generator_sha256": sha256_file(SCRIPT_PATH),
            "observational_inputs_read": [],
            "historical_fitted_couplings_reused": [],
        },
        "scope": {
            "included_modes": "six positive Neumann benchmark modes at the UV probe slice",
            "excluded_mode": "the massless Neumann zero mode is deliberately excluded; its viability requires a separate boundary-sector decision",
            "source_geometry": "point-source Yukawa kernel; extended sources require volume integration of the same kernel",
            "force_sign": "attractive for equal-sign universal beta_n",
        },
        "equations": {
            "physical_mass": "m_n=mu_n/ell",
            "physical_range": "lambda_n=ell/mu_n",
            "mode_strength": "alpha_n=2*beta_n(source)*beta_n(detector); this artifact uses the same derived UV beta_n for both",
            "point_source_potential": "V_phi/V_Newton=sum_n alpha_n*exp(-mu_n*x)",
            "point_source_force": "F_phi/F_Newton=sum_n alpha_n*(1+mu_n*x)*exp(-mu_n*x)",
            "radial_force_gradient": "|dF_phi/dr|/|dF_Newton/dr|=sum_n alpha_n*(1+mu_n*x+(mu_n*x)^2/2)*exp(-mu_n*x)",
            "distance_variable": "x=r/ell",
        },
        "positive_modes": modes,
        "short_distance_limits": {
            "sum_alpha_n": alpha_sum,
            "potential_fraction_x_to_0": alpha_sum,
            "force_fraction_x_to_0": alpha_sum,
            "gradient_fraction_x_to_0": alpha_sum,
        },
        "dimensionless_curves": {
            "grid": {
                "kind": "natural_log_uniform",
                "x_min": CURVE_X_MIN,
                "x_max": CURVE_X_MAX,
                "samples": CURVE_SAMPLES,
            },
            "samples": curve,
        },
        "distance_ratios": build_distance_ratios(modes, DISTANCE_ANCHORS),
        "normalized_mechanical_transfer": build_mechanical_transfer(),
        "required_external_quantities": {
            "to_convert_x_to_metres": [
                "ell in metres, fixed independently and before comparison",
            ],
            "to_predict_a_source_signal": [
                "source mass-density geometry and modulation history",
                "source and detector localization slices if they differ from the frozen UV benchmark",
                "a retuned mode table if the boundary action differs from the frozen Neumann benchmark",
            ],
            "to_predict_detector_displacement": [
                "detector density and stiffness tensor",
                "mechanical mode shapes and effective masses",
                "resonance frequencies, damping or Q, supports, and reference-frame acceleration",
                "force-overlap integral and readout transfer calibration",
            ],
            "not_supplied_by_the_frozen_geometry": [
                "ambient scalar occupation or oscillation amplitude",
                "laboratory time scale or drive frequency",
                "atomic-clock coefficients d_e, d_g, or d_mi",
                "noise model, sensitivity, significance, or a detection threshold",
            ],
        },
        "freeze_rules": [
            "fix the boundary action, matter slice, and ell without reading the target experiment",
            "calibrate the mechanical transfer with an ordinary independent actuator",
            "freeze source geometry, distance bins, null arms, and excluded data before unblinding",
            "do not infer an ambient mode amplitude from the same material data used to test it",
        ],
    }
    return payload


def build_report(input_path: Path = DEFAULT_INPUT) -> dict[str, Any]:
    payload = build_payload(input_path)
    return {
        "payload": payload,
        "integrity": {
            "algorithm": "sha256",
            "canonicalization": "UTF-8 JSON of payload with sort_keys=true, separators=(',', ':'), ensure_ascii=true, allow_nan=false",
            "payload_sha256": sha256_bytes(canonical_json_bytes(payload)),
            "authenticity_note": "content-integrity hash only; no private-key identity signature is claimed",
        },
    }


def render_report(report: dict[str, Any]) -> bytes:
    return pretty_json_bytes(report)


def checksum_label(output_path: Path) -> str:
    """Return a sha256sum-compatible label, repo-relative when possible."""

    try:
        return output_path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(output_path.resolve())


def write_artifacts(
    report: dict[str, Any],
    output_path: Path = DEFAULT_OUTPUT,
    checksum_path: Path = DEFAULT_CHECKSUM,
) -> str:
    output_bytes = render_report(report)
    output_path.write_bytes(output_bytes)
    full_hash = sha256_bytes(output_bytes)
    checksum_path.write_text(
        f"{full_hash}  {checksum_label(output_path)}\n", encoding="ascii"
    )
    return full_hash


def check_artifacts(
    report: dict[str, Any],
    output_path: Path = DEFAULT_OUTPUT,
    checksum_path: Path = DEFAULT_CHECKSUM,
) -> None:
    expected = render_report(report)
    if not output_path.exists():
        raise SystemExit(f"missing frozen artifact: {output_path}")
    if output_path.read_bytes() != expected:
        raise SystemExit(f"frozen artifact differs from generator output: {output_path}")

    expected_full_hash = sha256_bytes(expected)
    expected_sidecar = f"{expected_full_hash}  {checksum_label(output_path)}\n"
    if not checksum_path.exists() or checksum_path.read_text(encoding="ascii") != expected_sidecar:
        raise SystemExit(f"checksum sidecar mismatch: {checksum_path}")

    payload = report["payload"]
    embedded = report["integrity"]["payload_sha256"]
    if embedded != sha256_bytes(canonical_json_bytes(payload)):
        raise SystemExit("embedded payload hash mismatch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--checksum", type=Path, default=DEFAULT_CHECKSUM)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the frozen JSON and checksum match a fresh deterministic build",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.input)
    if args.check:
        check_artifacts(report, args.output, args.checksum)
        print(f"[OK] frozen material prediction artifact: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.checksum.parent.mkdir(parents=True, exist_ok=True)
    full_hash = write_artifacts(report, args.output, args.checksum)
    print(f"Wrote {args.output}")
    print(f"SHA256 {full_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
