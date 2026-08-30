#!/usr/bin/env python3
"""Derive the geometry-fixed scalar carrier without reading observations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import cumulative_trapezoid


HERE = Path(__file__).resolve().parent
INPUT_PATH = HERE / "artifacts" / "holo_effective_action.json"
OUTPUT_PATH = HERE / "artifacts" / "interface_action_derivation.json"

CRITERIA = {
    "identity_max_abs": 1e-10,
    "zero_mode_norm_abs_error": 1e-12,
    "zero_mode_radial_energy_max": 1e-24,
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


def _weighted_median_coordinate(u: np.ndarray, weight: np.ndarray) -> float:
    accumulated = cumulative_trapezoid(weight, u, initial=0.0)
    target = 0.5 * accumulated[-1]
    return float(np.interp(target, accumulated, u))


def derive(input_path: Path = INPUT_PATH) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    summary = payload["summary"]

    u = np.asarray(payload["u"], dtype=float)
    A = np.asarray(payload["A"], dtype=float)
    A_u = np.asarray(payload["A_u"], dtype=float)
    phi_u = np.asarray(payload["phi_u"], dtype=float)
    kinetic_K = np.asarray(payload["kinetic_K_of_phi"], dtype=float)
    potential_V = np.asarray(payload["potential_V_of_phi"], dtype=float)
    chi = np.asarray(payload["canonical_chi"], dtype=float)
    chi_u = np.asarray(payload["canonical_chi_u"], dtype=float)

    arrays = (u, A, A_u, phi_u, kinetic_K, potential_V, chi, chi_u)
    if len({array.size for array in arrays}) != 1:
        raise ValueError("Effective-action arrays do not have a common length")
    if not np.all(np.diff(u) > 0):
        raise ValueError("Radial coordinate must be strictly increasing")

    # These are the exact background identities already certified for the
    # reconstructed action, evaluated from independent stored columns.
    A_uu_from_noncanonical = -kinetic_K * np.square(phi_u) / 6.0
    A_uu_from_canonical = -np.square(chi_u) / 6.0
    canonicalization_error = chi_u - np.sqrt(kinetic_K) * np.abs(phi_u)
    warp_identity_error = A_uu_from_noncanonical - A_uu_from_canonical

    W = -6.0 * A_u
    W_chi = -6.0 * A_uu_from_noncanonical / chi_u
    W_flow_error = W_chi - chi_u
    V_from_W = 0.5 * np.square(W_chi) - np.square(W) / 3.0
    V_identity_error = V_from_W - potential_V

    epsilon_ed = -A_uu_from_noncanonical / np.square(A_u)
    p_weight = np.exp(4.0 * A) * epsilon_ed
    w_weight = np.exp(2.0 * A) * epsilon_ed

    p_integral = float(np.trapezoid(p_weight, u))
    w_integral = float(np.trapezoid(w_weight, u))
    constant_zero_mode = 1.0 / np.sqrt(w_integral)
    zero_mode_norm = float(
        np.trapezoid(w_weight * np.square(constant_zero_mode), u)
    )
    # The derivative of the analytic constant trial function is identically
    # zero; do not manufacture differentiation noise with a finite difference.
    zero_mode_radial_energy = 0.0

    radial_span = u[-1] - u[0]
    uv_stop = u[0] + 0.1 * radial_span
    ir_start = u[-1] - 0.1 * radial_span
    uv = u <= uv_stop
    ir = u >= ir_start

    identity_metrics = {
        "canonicalization_max_abs": float(
            np.max(np.abs(canonicalization_error))
        ),
        "warp_representation_max_abs": float(
            np.max(np.abs(warp_identity_error))
        ),
        "W_flow_max_abs": float(np.max(np.abs(W_flow_error))),
        "V_from_W_max_abs": float(np.max(np.abs(V_identity_error))),
    }
    carrier_metrics = {
        "epsilon_min": float(np.min(epsilon_ed)),
        "epsilon_max": float(np.max(epsilon_ed)),
        "p_min": float(np.min(p_weight)),
        "p_max": float(np.max(p_weight)),
        "w_min": float(np.min(w_weight)),
        "w_max": float(np.max(w_weight)),
        "p_integral": p_integral,
        "w_integral": w_integral,
        "w_weighted_median_u": _weighted_median_coordinate(u, w_weight),
        "w_uv_decile_fraction": float(
            np.trapezoid(w_weight[uv], u[uv]) / w_integral
        ),
        "w_ir_decile_fraction": float(
            np.trapezoid(w_weight[ir], u[ir]) / w_integral
        ),
    }
    neumann_trial = {
        "completion": "Neumann--Neumann trial only",
        "constant_mode_amplitude": float(constant_zero_mode),
        "weighted_norm": zero_mode_norm,
        "radial_energy": zero_mode_radial_energy,
        "interpretation": (
            "A massless shape mode is allowed by this trial completion. "
            "It is not a physical prediction until boundary actions and "
            "normalization are fixed."
        ),
    }

    passes = {
        "effective_action_input_certified": bool(summary["passes"]["all"]),
        "canonical_field_monotonic": bool(np.all(np.diff(chi) > 0)),
        "A_uu_strictly_negative": bool(np.all(A_uu_from_noncanonical < 0)),
        "positive_carrier_weights": bool(
            np.all(epsilon_ed > 0)
            and np.all(p_weight > 0)
            and np.all(w_weight > 0)
        ),
        "finite_positive_carrier_integrals": bool(
            np.isfinite(p_integral)
            and np.isfinite(w_integral)
            and p_integral > 0
            and w_integral > 0
        ),
        "superpotential_identities": bool(
            max(identity_metrics.values()) <= CRITERIA["identity_max_abs"]
        ),
        "neumann_constant_mode_normalized": bool(
            abs(zero_mode_norm - 1.0)
            <= CRITERIA["zero_mode_norm_abs_error"]
            and zero_mode_radial_energy
            <= CRITERIA["zero_mode_radial_energy_max"]
        ),
        "blind_to_observations": True,
    }
    passes["all"] = all(passes.values())

    return {
        "title": "Geometry-derived scalar interaction carrier",
        "classification": "bulk_carrier_derived_interface_coefficients_unfixed",
        "input": {
            "path": str(input_path),
            "sha256": sha256_file(input_path),
            "samples": int(u.size),
            "domain": [float(u[0]), float(u[-1])],
        },
        "observational_inputs_read": [],
        "criteria": CRITERIA,
        "geometry_fixed": {
            "canonical_field": "d chi = sqrt(K(phi)) d phi",
            "local_superpotential": "W(chi(u)) = -6 A_u(u)",
            "potential_identity": "V = W_chi^2/2 - W^2/3",
            "carrier_factor": "epsilon_ED = -A_uu/A_u^2",
            "radial_weight": "p = exp(4 A) epsilon_ED",
            "four_dimensional_weight": "w = exp(2 A) epsilon_ED",
            "shape_equation": "-d_u(p d_u f_n) = m_n^2 w f_n",
            "shape_normalization": "integral w f_n f_m du = delta_nm",
        },
        "identity_metrics": identity_metrics,
        "carrier_metrics": carrier_metrics,
        "neumann_trial": neumann_trial,
        "unfixed_choices": [
            "radial boundary actions and boundary conditions",
            "five-dimensional gravitational normalization kappa_5",
            "absolute radial and four-dimensional mass scale",
            "Standard-Model localization in the radial direction",
            "universal matter Wilson coefficient beta",
            "electromagnetic Wilson coefficient d_e",
            "QCD and fermion-mass coefficients d_g and d_mi",
        ],
        "conditional_4d_interface": {
            "matter": "S_m[A_m(varphi)^2 g, Psi]",
            "ln_A_m": "beta varphi/M_Pl + O(varphi^2)",
            "electromagnetism": "-B_F(varphi) F^2/4",
            "B_F": "1 + d_e varphi/M_Pl + O(varphi^2)",
            "yukawa_potential": (
                "-G m1 m2/r [1 + 2 beta^2 exp(-m_varphi r)]"
            ),
        },
        "passes": passes,
        "evidence_boundary": (
            "This certificate derives a positive gauge-invariant scalar "
            "carrier and an allowed interaction basis from the corrected "
            "bulk. It does not select a boundary completion, determine any "
            "matter Wilson coefficient, or establish an observed interaction."
        ),
    }


def main() -> int:
    result = derive()
    write_json(OUTPUT_PATH, result)
    print(f"[interface derivation] {OUTPUT_PATH}")
    print(f"[observational inputs] {len(result['observational_inputs_read'])}")
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
