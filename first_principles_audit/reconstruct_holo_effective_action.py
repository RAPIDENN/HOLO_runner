#!/usr/bin/env python3
"""Reconstruct a healthy effective action while preserving the HOLO geometry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import UnivariateSpline


HERE = Path(__file__).resolve().parent
ARTIFACT_ROOT = HERE / "artifacts"
TRACE_PATH = Path(
    "/home/debian/work/repos/HOLO_TRANSDUCTOR_instrument/"
    "data/internal/holo_physics_trace_ed_industrial.json"
)
TRACE_SHA256 = "e1c4b9d8495a563be31c36ceeeea7575b1d46afae74b45394edb77a8ffb06725"

SPLINE_DEGREE = 5
SMOOTH_A = 1e-10
SMOOTH_PHI = 1e-12
ENDPOINT_TRIM = 10

CRITERIA = {
    "A_fit_max_abs": 5e-6,
    "phi_fit_max_abs": 2e-7,
    "equation_max_abs": 1e-10,
    "equation_normalized_rms": 1e-12,
    "delta_rms": 1e-3,
    "delta_correlation_min": 0.999999,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _normalized_rms(residual: np.ndarray, scale_terms: list[np.ndarray]) -> float:
    numerator = float(np.sqrt(np.mean(np.square(residual))))
    scale = np.zeros_like(residual)
    for term in scale_terms:
        scale += np.abs(term)
    denominator = float(np.sqrt(np.mean(np.square(scale))))
    return numerator / max(denominator, np.finfo(float).tiny)


def reconstruct(trace_path: Path = TRACE_PATH) -> tuple[dict[str, Any], dict[str, Any]]:
    actual_hash = sha256_file(trace_path)
    if actual_hash != TRACE_SHA256:
        raise RuntimeError(
            f"Frozen trace hash changed: expected {TRACE_SHA256}, got {actual_hash}"
        )

    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    trace = payload["trace"]
    u_full = np.asarray(trace["z"], dtype=float)
    A_raw = np.asarray(trace["A"], dtype=float)
    phi_raw = np.asarray(trace["phi"], dtype=float)
    delta_stored_full = np.asarray(trace["delta"], dtype=float)

    if not np.all(np.diff(u_full) > 0):
        raise ValueError("Radial samples must be strictly increasing")

    A_spline = UnivariateSpline(
        u_full, A_raw, k=SPLINE_DEGREE, s=SMOOTH_A
    )
    phi_spline = UnivariateSpline(
        u_full, phi_raw, k=SPLINE_DEGREE, s=SMOOTH_PHI
    )

    interior = slice(ENDPOINT_TRIM, -ENDPOINT_TRIM)
    u = u_full[interior]
    A = A_spline(u)
    A_u = A_spline(u, 1)
    A_uu = A_spline(u, 2)
    A_uuu = A_spline(u, 3)
    phi = phi_spline(u)
    phi_u = phi_spline(u, 1)
    phi_uu = phi_spline(u, 2)

    if np.any(A_uu >= 0):
        raise RuntimeError("Canonical reconstruction fails: A_uu is not negative")
    if np.any(phi_u == 0) or not (
        np.all(phi_u > 0) or np.all(phi_u < 0)
    ):
        raise RuntimeError("Effective reconstruction requires monotonic phi")

    kinetic_K = -6.0 * A_uu / np.square(phi_u)
    potential_V = -3.0 * A_uu - 12.0 * np.square(A_u)

    kinetic_u = (
        -6.0 * A_uuu * np.square(phi_u)
        + 12.0 * A_uu * phi_u * phi_uu
    ) / np.power(phi_u, 4)
    kinetic_phi = kinetic_u / phi_u
    potential_u = -3.0 * A_uuu - 24.0 * A_u * A_uu
    potential_phi = potential_u / phi_u

    warp_residual = A_uu + kinetic_K * np.square(phi_u) / 6.0
    constraint_residual = (
        12.0 * np.square(A_u)
        - 0.5 * kinetic_K * np.square(phi_u)
        + potential_V
    )
    scalar_terms = [
        kinetic_K * phi_uu,
        4.0 * kinetic_K * A_u * phi_u,
        0.5 * kinetic_phi * np.square(phi_u),
        potential_phi,
    ]
    scalar_residual = scalar_terms[0] + scalar_terms[1] + scalar_terms[2] - scalar_terms[3]

    chi_u = np.sqrt(-6.0 * A_uu)
    chi_uu = -3.0 * A_uuu / chi_u
    chi = cumulative_trapezoid(chi_u, u, initial=0.0)
    potential_chi = potential_u / chi_u
    canonical_scalar_residual = chi_uu + 4.0 * A_u * chi_u - potential_chi
    canonical_warp_residual = A_uu + np.square(chi_u) / 6.0

    delta_stored = delta_stored_full[interior]
    delta_effective = -A_u - 1.0
    delta_error = delta_effective - delta_stored
    delta_rms = float(np.sqrt(np.mean(np.square(delta_error))))
    delta_correlation = float(np.corrcoef(delta_effective, delta_stored)[0, 1])

    A_fit_error = A - A_raw[interior]
    phi_fit_error = phi - phi_raw[interior]

    equation_metrics = {
        "warp_max_abs": float(np.max(np.abs(warp_residual))),
        "constraint_max_abs": float(np.max(np.abs(constraint_residual))),
        "scalar_max_abs": float(np.max(np.abs(scalar_residual))),
        "scalar_normalized_rms": _normalized_rms(scalar_residual, scalar_terms),
        "canonical_warp_max_abs": float(
            np.max(np.abs(canonical_warp_residual))
        ),
        "canonical_scalar_max_abs": float(
            np.max(np.abs(canonical_scalar_residual))
        ),
        "canonical_scalar_normalized_rms": _normalized_rms(
            canonical_scalar_residual,
            [chi_uu, 4.0 * A_u * chi_u, potential_chi],
        ),
    }
    preservation_metrics = {
        "A_fit_max_abs": float(np.max(np.abs(A_fit_error))),
        "phi_fit_max_abs": float(np.max(np.abs(phi_fit_error))),
        "delta_max_abs": float(np.max(np.abs(delta_error))),
        "delta_rms": delta_rms,
        "delta_correlation": delta_correlation,
    }

    passes = {
        "input_hash": actual_hash == TRACE_SHA256,
        "A_profile_preserved": preservation_metrics["A_fit_max_abs"]
        <= CRITERIA["A_fit_max_abs"],
        "phi_profile_preserved": preservation_metrics["phi_fit_max_abs"]
        <= CRITERIA["phi_fit_max_abs"],
        "positive_kinetic_function": bool(np.all(kinetic_K > 0)),
        "noncanonical_equations": bool(
            equation_metrics["warp_max_abs"] <= CRITERIA["equation_max_abs"]
            and equation_metrics["constraint_max_abs"]
            <= CRITERIA["equation_max_abs"]
            and equation_metrics["scalar_normalized_rms"]
            <= CRITERIA["equation_normalized_rms"]
        ),
        "canonical_equations": bool(
            equation_metrics["canonical_warp_max_abs"]
            <= CRITERIA["equation_max_abs"]
            and equation_metrics["canonical_scalar_normalized_rms"]
            <= CRITERIA["equation_normalized_rms"]
        ),
        "operational_delta_recovered": bool(
            delta_rms <= CRITERIA["delta_rms"]
            and delta_correlation >= CRITERIA["delta_correlation_min"]
        ),
    }
    passes["all"] = all(passes.values())

    summary = {
        "title": "Geometry-preserving effective Einstein--scalar reconstruction",
        "classification": "inverse_effective_completion_not_forward_prediction",
        "input": {
            "path": str(trace_path),
            "sha256": actual_hash,
            "samples_total": int(u_full.size),
            "samples_certified": int(u.size),
        },
        "method": {
            "metric_gauge": "domain_wall",
            "spline_degree": SPLINE_DEGREE,
            "smoothing_A": SMOOTH_A,
            "smoothing_phi": SMOOTH_PHI,
            "endpoint_trim_each_side": ENDPOINT_TRIM,
            "action": "R - (1/2) K(phi) (partial phi)^2 - V(phi)",
            "K_reconstruction": "-6 A_uu / phi_u^2",
            "V_reconstruction": "-3 A_uu - 12 A_u^2",
            "canonical_field": "chi_u=sqrt(-6 A_uu)",
            "recovered_deformation": "delta_eff=-A_u-1 for L=1",
        },
        "domain": [float(u[0]), float(u[-1])],
        "ranges": {
            "phi": [float(np.min(phi)), float(np.max(phi))],
            "canonical_chi": [float(np.min(chi)), float(np.max(chi))],
            "kinetic_K": [float(np.min(kinetic_K)), float(np.max(kinetic_K))],
            "potential_V": [float(np.min(potential_V)), float(np.max(potential_V))],
        },
        "criteria": CRITERIA,
        "preservation_metrics": preservation_metrics,
        "equation_metrics": equation_metrics,
        "passes": passes,
        "evidence_boundary": (
            "The action functions are reconstructed from the frozen geometry. "
            "This proves an effective completion exists on the certified interval; "
            "it does not make the geometry a prior prediction of those functions."
        ),
    }

    artifact = {
        "summary": summary,
        "u": u.tolist(),
        "A": A.tolist(),
        "A_u": A_u.tolist(),
        "phi": phi.tolist(),
        "phi_u": phi_u.tolist(),
        "kinetic_K_of_phi": kinetic_K.tolist(),
        "potential_V_of_phi": potential_V.tolist(),
        "canonical_chi": chi.tolist(),
        "canonical_chi_u": chi_u.tolist(),
        "delta_stored": delta_stored.tolist(),
        "delta_effective": delta_effective.tolist(),
    }
    return summary, artifact


def main() -> int:
    summary, artifact = reconstruct()
    summary_path = ARTIFACT_ROOT / "holo_effective_action_summary.json"
    artifact_path = ARTIFACT_ROOT / "holo_effective_action.json"
    write_json(summary_path, summary)
    write_json(artifact_path, artifact)
    print(f"[effective action] {artifact_path}")
    print(f"[certificate] {summary_path}")
    print(f"[result] all checks pass: {summary['passes']['all']}")
    return 0 if summary["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
