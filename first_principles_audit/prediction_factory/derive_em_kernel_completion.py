#!/usr/bin/env python3
"""Derive the coordinate-correct Maxwell kernel behind historical Eq. 39.

The frozen trace coordinate was historically labelled ``z`` even though the
effective-action audit identifies it as domain-wall ``u``. This module keeps
those coordinates separate, constructs the true conformal coordinate, and
records the scalar-lapse response needed by the physical trace carrier.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy.integrate import cumulative_simpson, simpson


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LEGACY_INPUT = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/k_em_uv_projector.json"
)
EFFECTIVE_INPUT = Path(
    "first_principles_audit/artifacts/holo_effective_action.json"
)
OUTPUT = HERE / "em_kernel_completion.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trapz(values: Sequence[float], grid: Sequence[float]) -> float:
    if len(values) != len(grid) or len(grid) < 2:
        raise ValueError("values and grid must have the same length >= 2")
    return sum(
        0.5 * (values[i] + values[i + 1]) * (grid[i + 1] - grid[i])
        for i in range(len(grid) - 1)
    )


def _validate_common_grid(grid: Sequence[float], *arrays: Sequence[float]) -> None:
    n = len(grid)
    if n < 2 or any(len(values) != n for values in arrays):
        raise ValueError("all arrays must have the same length >= 2")
    if any(
        not math.isfinite(float(value))
        for values in (grid, *arrays)
        for value in values
    ):
        raise ValueError("all inputs must be finite")
    if any(grid[i + 1] <= grid[i] for i in range(n - 1)):
        raise ValueError("the radial grid must be strictly increasing")


def normalized_bulk_photon_kernel(
    z: Sequence[float],
    warp_a: Sequence[float],
    gauge_kinetic_z: Sequence[float],
    photon_profile: Sequence[float],
) -> list[float]:
    """Return exp(A) Z f_gamma^2 divided by its conformal-z integral."""

    _validate_common_grid(z, warp_a, gauge_kinetic_z, photon_profile)
    if any(value <= 0.0 for value in gauge_kinetic_z):
        raise ValueError("the gauge kinetic function Z must be strictly positive")
    raw = [
        math.exp(float(a))
        * float(gauge_kinetic_z[i])
        * float(photon_profile[i]) ** 2
        for i, a in enumerate(warp_a)
    ]
    norm = trapz(raw, z)
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("the photon zero mode has zero or invalid norm")
    return [value / norm for value in raw]


def normalized_domain_wall_photon_kernel(
    u: Sequence[float],
    gauge_kinetic_u: Sequence[float],
    photon_profile: Sequence[float],
) -> list[float]:
    """Return Z f_gamma^2 divided by its domain-wall-u integral."""

    _validate_common_grid(u, gauge_kinetic_u, photon_profile)
    if any(value <= 0.0 for value in gauge_kinetic_u):
        raise ValueError("the gauge kinetic function Z must be strictly positive")
    raw = [
        float(gauge_kinetic_u[i]) * float(photon_profile[i]) ** 2
        for i in range(len(u))
    ]
    norm = trapz(raw, u)
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("the photon zero mode has zero or invalid norm")
    return [value / norm for value in raw]


def conformal_coordinate_from_domain_wall(
    u: Sequence[float], warp_a: Sequence[float]
) -> list[float]:
    """Construct z_c with dz_c/du=exp(-A), fixing z_c(u_min)=0."""

    _validate_common_grid(u, warp_a)
    u_array = np.asarray(u, dtype=float)
    a_array = np.asarray(warp_a, dtype=float)
    z = np.concatenate(
        ([0.0], cumulative_simpson(np.exp(-a_array), x=u_array))
    )
    if not np.all(np.diff(z) > 0.0):
        raise RuntimeError("the constructed conformal coordinate is not monotone")
    return z.tolist()


def build() -> dict[str, object]:
    legacy_path = REPO / LEGACY_INPUT
    effective_path = REPO / EFFECTIVE_INPUT
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    effective = json.loads(effective_path.read_text(encoding="utf-8"))
    if not effective["summary"]["passes"]["all"]:
        raise RuntimeError("the effective-action input certificate does not pass")

    legacy_u = np.asarray(legacy["z_grid"], dtype=float)
    legacy_k = np.asarray(legacy["k_em"], dtype=float)
    legacy_norm = float(np.trapezoid(legacy_k, legacy_u))
    legacy_uniform = np.full_like(legacy_u, 1.0 / np.ptp(legacy_u))
    legacy_uniform_difference = float(np.max(np.abs(legacy_k - legacy_uniform)))

    u = np.asarray(effective["u"], dtype=float)
    warp_a = np.asarray(effective["A"], dtype=float)
    chi = np.asarray(effective["canonical_chi"], dtype=float)
    z_conformal = np.asarray(
        conformal_coordinate_from_domain_wall(u, warp_a), dtype=float
    )
    interval_u = float(np.ptp(u))

    # Z=1 and the Neumann-compatible massless photon profile f_gamma=constant.
    k_u = np.full_like(u, 1.0 / interval_u)
    z_norm = float(simpson(np.exp(warp_a), x=z_conformal))
    k_z = np.exp(warp_a) / z_norm
    cumulative_u = np.concatenate(([0.0], cumulative_simpson(k_u, x=u)))
    cumulative_z = np.concatenate(
        ([0.0], cumulative_simpson(k_z, x=z_conformal))
    )
    coordinate_measure_error = float(
        np.max(np.abs(cumulative_u - cumulative_z))
    )

    chi_mean = float(simpson(chi, x=u) / interval_u)
    dlog_kernel_dc = chi - chi_mean
    derivative_norm = float(simpson(k_u * dlog_kernel_dc, x=u))

    coordinate_certificate = {
        "samples": int(u.size),
        "domain_wall_interval": [float(u[0]), float(u[-1])],
        "domain_wall_span": interval_u,
        "conformal_interval_with_arbitrary_zero": [
            float(z_conformal[0]),
            float(z_conformal[-1]),
        ],
        "conformal_span": float(np.ptp(z_conformal)),
        "domain_wall_kernel_value": float(k_u[0]),
        "domain_wall_norm": float(simpson(k_u, x=u)),
        "conformal_norm": float(simpson(k_z, x=z_conformal)),
        "cumulative_measure_max_abs_difference": coordinate_measure_error,
        "passes": bool(coordinate_measure_error < 1.0e-9),
    }

    return {
        "schema": "holo.em-kernel-completion.v2",
        "title": "Coordinate-correct action completion of Eq. 39",
        "classification": "derived_kernel_and_trace_response_not_detection",
        "inputs": {
            "historical_kernel": {
                "path": str(LEGACY_INPUT),
                "sha256": _sha256(legacy_path),
                "historical_formula": legacy["provenance"]["formula"],
            },
            "effective_action": {
                "path": str(EFFECTIVE_INPUT),
                "sha256": _sha256(effective_path),
            },
        },
        "bulk_maxwell_branch": {
            "action": (
                "S_gamma=-(4 g5^2)^-1 int d5x sqrt(-g) "
                "Z(chi) F_MN F^MN"
            ),
            "health_condition": "Z(chi(u)) > 0 on the full interval",
            "domain_wall_gauge": {
                "metric": (
                    "ds^2=exp(2A(u)) eta_mu_nu dx^mu dx^nu+ell^2 du^2"
                ),
                "mode_equation": (
                    "-d_u[exp(2A) Z d_u f_n] = mu_gamma,n^2 Z f_n"
                ),
                "normalization": "int du Z f_m f_n = delta_mn",
                "kernel": (
                    "K_u=Z(chi)|f_gamma|^2/int du Z(chi)|f_gamma|^2"
                ),
            },
            "conformal_gauge": {
                "coordinate_relation": "du=exp(A) dz_c",
                "metric": (
                    "ds^2=exp(2A(z_c))[eta_mu_nu dx^mu dx^nu+ell^2 dz_c^2]"
                ),
                "mode_equation": (
                    "-d_z[exp(A) Z d_z f_n] = mu_gamma,n^2 exp(A) Z f_n"
                ),
                "normalization": "int dz_c exp(A) Z f_m f_n = delta_mn",
                "kernel": (
                    "K_z=exp(A)Z(chi)|f_gamma|^2/"
                    "int dz_c exp(A)Z(chi)|f_gamma|^2"
                ),
                "measure_identity": "K_u du=K_z dz_c",
            },
            "eq39_special_case": {
                "assumptions": [
                    "the electromagnetic field propagates in the five-dimensional bulk",
                    "Z(chi)=1",
                    "the massless photon mode is flat",
                    "Neumann-compatible photon boundary data",
                    "no brane-localized kinetic terms",
                ],
                "result": (
                    "Eq. 39 is the conformal-coordinate density K_z; the same "
                    "probability measure is uniform in domain-wall u"
                ),
                "coordinate_certificate": coordinate_certificate,
                "profiles": {
                    "u": u.tolist(),
                    "z_conformal_from_u": z_conformal.tolist(),
                    "K_u": k_u.tolist(),
                    "K_z_conformal": k_z.tolist(),
                },
            },
            "minimal_exponential_deformation_at_c_gamma_zero": {
                "family_not_fitted": "Z(chi)=exp(c_gamma chi)",
                "c_gamma_evaluated": 0.0,
                "chi_uniform_mean": chi_mean,
                "identity": "partial_c ln K_u|_0=chi-<chi>_u",
                "derivative_range": [
                    float(np.min(dlog_kernel_dc)),
                    float(np.max(dlog_kernel_dc)),
                ],
                "weighted_derivative_integral": derivative_norm,
            },
            "physical_trace_carrier_response": {
                "gauge": "almost-radial/unitary scalar gauge used for the h carrier",
                "metric_constraint": "A_u h_uu=(d_u h)/4",
                "maxwell_cancellation": (
                    "the four-dimensional conformal trace cancels in F_mu_nu F^mu_nu; "
                    "the scalar lapse N=h_uu/2 remains"
                ),
                "mode_expansion": (
                    "h=sum_n q_n f_n; varphi_n=sqrt(3 ell) q_n/(8 kappa_5)"
                ),
                "coupling": "B_F=1+sum_n d_gamma,n varphi_n/M_Pl+...",
                "derived_coefficient": (
                    "d_gamma,n(c)=sqrt(I_g/3) [int du exp(c chi) f_n'/A_u] / "
                    "[int du exp(c chi)]"
                ),
                "required_boundary_statement": (
                    "endpoints are comoving scalar boundaries, or all brane-bending "
                    "and endpoint-displacement terms must be included"
                ),
                "companion_artifact": (
                    "first_principles_audit/prediction_factory/"
                    "em_spectral_fingerprint.json"
                ),
            },
        },
        "historical_artifact_audit": {
            "coordinate_status": (
                "the historical grid is the frozen trace coordinate later adjudicated "
                "as domain-wall u, not a constructed conformal coordinate"
            ),
            "legacy_samples": int(legacy_u.size),
            "legacy_grid_span": float(np.ptp(legacy_u)),
            "legacy_trapezoid_norm": legacy_norm,
            "correct_Z1_domain_wall_uniform_value_on_legacy_support": float(
                legacy_uniform[0]
            ),
            "legacy_kernel_endpoint_values": [
                float(legacy_k[0]),
                float(legacy_k[-1]),
            ],
            "max_abs_difference_from_uniform_domain_wall_kernel": (
                legacy_uniform_difference
            ),
            "old_2e_minus_16_claim": (
                "removed: it set A_representative=log(K_legacy), so the comparison "
                "was an identity by construction rather than a trace-coordinate test"
            ),
            "pointwise_comparison_to_corrected_K_z": (
                "invalid because the historical 1999-node grid is not the constructed "
                "1979-node conformal grid"
            ),
        },
        "brane_localized_maxwell_branch": {
            "action": (
                "S_brane=-(4 g4^2)^-1 int d4x sqrt(-g4) "
                "F_mu_nu F^mu_nu"
            ),
            "result": (
                "Classical four-dimensional Maxwell theory is Weyl invariant; a "
                "purely conformal induced metric supplies no local scalar F^2 vertex"
            ),
            "eq39_status": "not derived for this branch",
        },
        "observable_boundary": {
            "kernel_is": "a coordinate-covariant normalized spatial overlap measure",
            "kernel_is_not": [
                "an observed scalar-photon coupling amplitude",
                "a conversion from radial coordinate to laboratory seconds",
                "an atomic differential-sensitivity coefficient",
                "evidence of a clock signal or fifth force",
            ],
            "required_before_dimensional_prediction": [
                "select the physical scalar boundary action without using target data",
                "select bulk-photon rather than brane-photon localization",
                "fix ell and a source or scalar occupation model",
                "supply atomic differential-sensitivity coefficients",
                "freeze the statistic and use an independent acquisition session",
            ],
        },
        "adjudication": (
            "The functional Eq. 39 follows for a minimal bulk photon only in the "
            "constructed conformal coordinate. The historical numerical kernel mixed "
            "radial gauges and is not retained as a physical projection. The scalar "
            "lapse constraint now supplies a conditional action-derived photon "
            "coupling, but no laboratory detection is claimed."
        ),
        "passes": {
            "effective_action_input_certified": True,
            "legacy_kernel_normalized_as_stored": abs(legacy_norm - 1.0) < 1.0e-12,
            "legacy_coordinate_mismatch_exposed": legacy_uniform_difference > 0.3,
            "corrected_domain_wall_kernel_normalized": abs(
                coordinate_certificate["domain_wall_norm"] - 1.0
            )
            < 1.0e-12,
            "corrected_conformal_kernel_normalized": abs(
                coordinate_certificate["conformal_norm"] - 1.0
            )
            < 1.0e-12,
            "coordinate_measure_invariant": coordinate_certificate["passes"],
            "kernel_response_derivative_normalized": abs(derivative_norm) < 1.0e-10,
            "no_free_c_gamma_fitted": True,
            "no_observational_series_read": True,
        },
    }


def main() -> int:
    artifact = build()
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    coordinate = artifact["bulk_maxwell_branch"]["eq39_special_case"][
        "coordinate_certificate"
    ]
    legacy = artifact["historical_artifact_audit"]
    print(f"[EM kernel completion] {OUTPUT}")
    print(
        "[coordinate identity] max_abs={:.3e}".format(
            coordinate["cumulative_measure_max_abs_difference"]
        )
    )
    print(
        "[legacy gauge-mix] max_abs_from_uniform={:.6f}".format(
            legacy["max_abs_difference_from_uniform_domain_wall_kernel"]
        )
    )
    passed = all(artifact["passes"].values())
    print(f"[certificate] {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
