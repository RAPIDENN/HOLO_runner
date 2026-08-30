#!/usr/bin/env python3
"""Derive a blind compact-interval probe-matter benchmark."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh


HERE = Path(__file__).resolve().parent
INPUT_PATH = HERE / "artifacts" / "holo_effective_action.json"
OUTPUT_PATH = HERE / "artifacts" / "minimal_probe_completion.json"

MODE_COUNT = 7
CRITERIA = {
    "orthonormality_max_abs": 1e-10,
    "positive_mode_residual_max": 1e-4,
    "zero_mode_raw_eigenvalue_abs_max": 1e-6,
    "zero_mode_stiffness_relative_max": 1e-12,
    "half_grid_mass_relative_max": 2e-4,
    "quarter_grid_mass_relative_max": 1e-3,
    "half_grid_uv_coupling_relative_max": 5e-4,
    "quarter_grid_uv_coupling_relative_max": 3e-3,
    "zero_mode_norm_abs_error": 1e-12,
}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _carrier_arrays(payload: dict[str, Any]) -> tuple[np.ndarray, ...]:
    u = np.asarray(payload["u"], dtype=float)
    A = np.asarray(payload["A"], dtype=float)
    A_u = np.asarray(payload["A_u"], dtype=float)
    phi_u = np.asarray(payload["phi_u"], dtype=float)
    kinetic_K = np.asarray(payload["kinetic_K_of_phi"], dtype=float)
    A_uu = -kinetic_K * np.square(phi_u) / 6.0
    epsilon_ed = -A_uu / np.square(A_u)
    p_weight = np.exp(4.0 * A) * epsilon_ed
    w_weight = np.exp(2.0 * A) * epsilon_ed
    return u, A, p_weight, w_weight


def _subsample(
    u: np.ndarray,
    p_weight: np.ndarray,
    w_weight: np.ndarray,
    stride: int,
) -> tuple[np.ndarray, ...]:
    indices = np.arange(0, u.size, stride, dtype=int)
    if indices[-1] != u.size - 1:
        indices = np.append(indices, u.size - 1)
    return u[indices], p_weight[indices], w_weight[indices]


def _fem_matrices(
    u: np.ndarray, p_weight: np.ndarray, w_weight: np.ndarray
):
    spacing = np.diff(u)
    p_element = 0.5 * (p_weight[:-1] + p_weight[1:])

    stiffness_diag = np.zeros(u.size)
    stiffness_diag[:-1] += p_element / spacing
    stiffness_diag[1:] += p_element / spacing
    stiffness_off = -p_element / spacing

    # Exact P1 element integral when w is linearly interpolated between nodes.
    mass_diag = np.zeros(u.size)
    mass_diag[:-1] += spacing * (3.0 * w_weight[:-1] + w_weight[1:]) / 12.0
    mass_diag[1:] += spacing * (w_weight[:-1] + 3.0 * w_weight[1:]) / 12.0
    mass_off = spacing * (w_weight[:-1] + w_weight[1:]) / 12.0

    stiffness = diags(
        [stiffness_off, stiffness_diag, stiffness_off],
        offsets=[-1, 0, 1],
        format="csr",
    )
    mass = diags(
        [mass_off, mass_diag, mass_off], offsets=[-1, 0, 1], format="csr"
    )
    return stiffness, mass


def _solve_modes(
    u: np.ndarray,
    p_weight: np.ndarray,
    w_weight: np.ndarray,
    count: int = MODE_COUNT,
) -> dict[str, Any]:
    stiffness, mass = _fem_matrices(u, p_weight, w_weight)
    raw_values, raw_vectors = eigsh(
        stiffness,
        k=count,
        M=mass,
        sigma=1e-9,
        which="LM",
        tol=1e-11,
        maxiter=100000,
        v0=np.linspace(1.0, 2.0, stiffness.shape[0], dtype=float),
    )
    order = np.argsort(raw_values)
    raw_values = raw_values[order]
    raw_vectors = raw_vectors[:, order]

    zero_indices = np.flatnonzero(
        np.abs(raw_values) <= CRITERIA["zero_mode_raw_eigenvalue_abs_max"]
    )
    if zero_indices.size != 1:
        raise RuntimeError(
            f"Expected one numerical zero mode, found {zero_indices.size}: "
            f"{raw_values.tolist()}"
        )
    positive_indices = np.flatnonzero(
        raw_values > CRITERIA["zero_mode_raw_eigenvalue_abs_max"]
    )
    if positive_indices.size < count - 1:
        raise RuntimeError(
            f"Expected {count - 1} positive modes, found "
            f"{positive_indices.size}: {raw_values.tolist()}"
        )

    constant = np.ones(u.size)
    constant /= np.sqrt(float(constant @ (mass @ constant)))
    vectors = [constant]

    # Discard the numerical representation of the zero eigenvector and use
    # M-orthogonal Gram--Schmidt for the positive modes.
    for candidate in raw_vectors[:, positive_indices[: count - 1]].T:
        vector = candidate.copy()
        for accepted in vectors:
            vector -= accepted * float(accepted @ (mass @ vector))
        vector /= np.sqrt(float(vector @ (mass @ vector)))
        if vector[0] < 0:
            vector *= -1.0
        vectors.append(vector)
    modes = np.column_stack(vectors)

    zero_stiffness = stiffness @ constant
    zero_scale = np.linalg.norm(stiffness.data) * np.linalg.norm(constant)
    zero_stiffness_relative = float(
        np.linalg.norm(zero_stiffness) / max(zero_scale, 1e-300)
    )
    eigenvalues = [0.0]
    residuals = [zero_stiffness_relative]
    for mode in modes[:, 1:].T:
        denominator = float(mode @ (mass @ mode))
        eigenvalue = float(mode @ (stiffness @ mode) / denominator)
        residual = stiffness @ mode - eigenvalue * (mass @ mode)
        scale = (
            np.linalg.norm(stiffness @ mode)
            + abs(eigenvalue) * np.linalg.norm(mass @ mode)
        )
        eigenvalues.append(eigenvalue)
        residuals.append(float(np.linalg.norm(residual) / max(scale, 1e-300)))

    gram = modes.T @ (mass @ modes)
    return {
        "eigenvalues": np.asarray(eigenvalues),
        "masses": np.sqrt(np.maximum(eigenvalues, 0.0)),
        "modes": modes,
        "orthonormality_max_abs": float(
            np.max(np.abs(gram - np.eye(gram.shape[0])))
        ),
        "residuals": np.asarray(residuals),
        "raw_eigenvalues": raw_values,
        "raw_zero_eigenvalue": float(raw_values[zero_indices[0]]),
        "zero_stiffness_relative": zero_stiffness_relative,
        "numerical_zero_mode_count": int(zero_indices.size),
        "w_integral_fem": float(np.ones(u.size) @ (mass @ np.ones(u.size))),
    }


def derive(input_path: Path = INPUT_PATH) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not payload["summary"]["passes"]["all"]:
        raise RuntimeError("Effective-action input certificate does not pass")

    u, A, p_weight, w_weight = _carrier_arrays(payload)
    full = _solve_modes(u, p_weight, w_weight)
    I_g = float(np.trapezoid(np.exp(2.0 * A), u))

    convergence: dict[str, Any] = {}
    comparison_errors: dict[int, np.ndarray] = {}
    coupling_errors: dict[int, np.ndarray] = {}
    for stride, label in ((2, "half_grid"), (4, "quarter_grid")):
        u_sub, p_sub, w_sub = _subsample(u, p_weight, w_weight, stride)
        solution = _solve_modes(u_sub, p_sub, w_sub)
        relative = np.abs(
            solution["masses"][1:] / full["masses"][1:] - 1.0
        )
        coupling_relative = np.abs(
            solution["modes"][0, 1:] / full["modes"][0, 1:] - 1.0
        )
        comparison_errors[stride] = relative
        coupling_errors[stride] = coupling_relative
        convergence[label] = {
            "samples": int(u_sub.size),
            "positive_masses": solution["masses"][1:].tolist(),
            "relative_to_full": relative.tolist(),
            "max_relative": float(np.max(relative)),
            "uv_coupling_relative_to_full": coupling_relative.tolist(),
            "uv_coupling_max_relative": float(np.max(coupling_relative)),
        }

    I_w = full["w_integral_fem"]
    beta_profiles = np.sqrt(I_g / 3.0) * full["modes"]
    beta_zero = float(np.sqrt(I_g / (3.0 * I_w)))
    force_fraction_zero = 2.0 * beta_zero * beta_zero
    zero_norm = float(I_w * full["modes"][0, 0] ** 2)

    passes = {
        "effective_action_input_certified": True,
        "observational_blinding": True,
        "positive_carrier": bool(
            np.all(p_weight > 0.0) and np.all(w_weight > 0.0)
        ),
        "mode_orthonormality": bool(
            full["orthonormality_max_abs"]
            <= CRITERIA["orthonormality_max_abs"]
        ),
        "positive_mode_residuals": bool(
            np.max(full["residuals"][1:])
            <= CRITERIA["positive_mode_residual_max"]
        ),
        "unique_numerical_zero_mode": bool(
            full["numerical_zero_mode_count"] == 1
            and abs(full["raw_zero_eigenvalue"])
            <= CRITERIA["zero_mode_raw_eigenvalue_abs_max"]
        ),
        "zero_mode_stiffness_residual": bool(
            full["zero_stiffness_relative"]
            <= CRITERIA["zero_mode_stiffness_relative_max"]
        ),
        "half_grid_convergence": bool(
            np.max(comparison_errors[2])
            <= CRITERIA["half_grid_mass_relative_max"]
        ),
        "quarter_grid_convergence": bool(
            np.max(comparison_errors[4])
            <= CRITERIA["quarter_grid_mass_relative_max"]
        ),
        "half_grid_uv_coupling_convergence": bool(
            np.max(coupling_errors[2])
            <= CRITERIA["half_grid_uv_coupling_relative_max"]
        ),
        "quarter_grid_uv_coupling_convergence": bool(
            np.max(coupling_errors[4])
            <= CRITERIA["quarter_grid_uv_coupling_relative_max"]
        ),
        "zero_mode_normalized": bool(
            abs(zero_norm - 1.0)
            <= CRITERIA["zero_mode_norm_abs_error"]
        ),
        "zero_mode_coupling_identity": bool(
            abs(beta_profiles[0, 0] - beta_zero) <= 1e-14
        ),
    }
    passes["all"] = all(passes.values())

    return {
        "title": "Minimal compact-interval probe-matter completion",
        "classification": "conditional_forward_completion_not_detection",
        "input": {
            "path": str(input_path),
            "samples": int(u.size),
            "domain": [float(u[0]), float(u[-1])],
        },
        "observational_inputs_read": [],
        "historical_fitted_couplings_reused": [],
        "assumptions": [
            "finite radial domain is a one-copy physical compact interval",
            "a consistent GHY/background boundary completion adds no trace-sector kinetic or mass term",
            "Neumann-Neumann trace-carrier boundary conditions are explicitly selected",
            "probe Standard Model localized on a fixed radial slice",
            "no brane bending or probe backreaction",
            "induced-metric coupling only at tree level",
        ],
        "normalization": {
            "bulk_action": (
                "S5=(2 kappa_5^2)^-1 integral sqrt(-G) "
                "[R-(partial chi)^2/2-V]"
            ),
            "trace_quadratic_prefactor": "3/(128 kappa_5^2)",
            "trace_quadratic_action": (
                "S_h^(2)=-3 ell/(128 kappa_5^2) integral du d4x "
                "[w eta^mu_nu partial_mu h partial_nu h "
                "+p (partial_u h)^2/ell^2]"
            ),
            "metric_trace_convention": (
                "h is the transverse trace; its trace-sector contribution is "
                "delta g_mu_nu=(h/4) g_mu_nu; the longitudinal field "
                "decouples from conserved T_mu_nu"
            ),
            "radial_units": "u_phys=ell u",
            "canonical_mode": "varphi_n=sqrt(3 ell) q_n/(8 kappa_5)",
            "matter_variation": "delta S_m=integral sqrt(-g) h T/8",
            "planck_reduction": "M_Pl^2=ell I_g/kappa_5^2",
            "mode_coupling": "beta_n(u_m)=sqrt(I_g/3) f_n(u_m)",
        },
        "integrals": {"I_g": I_g, "I_w": I_w},
        "dimensionless_spectrum": {
            "boundary_conditions": "Neumann--Neumann",
            "masses_mu": full["masses"].tolist(),
            "mass_squared": full["eigenvalues"].tolist(),
            "physical_scale_rule": "m_n=mu_n/ell; ell is not fixed here",
            "orthonormality_max_abs": full["orthonormality_max_abs"],
            "raw_zero_eigenvalue": full["raw_zero_eigenvalue"],
            "zero_stiffness_relative": full["zero_stiffness_relative"],
            "positive_mode_relative_residuals": full["residuals"][1:].tolist(),
        },
        "convergence": convergence,
        "zero_mode_prediction": {
            "mass_mu": 0.0,
            "profile": "f_0=1/sqrt(I_w)",
            "beta_0": beta_zero,
            "relative_force_strength_2_beta_squared": force_fraction_zero,
            "probe_slice_dependence": "none for the constant zero mode",
        },
        "uv_probe_couplings_beta_n": beta_profiles[0, :].tolist(),
        "tree_level_channels": {
            "massive_matter_trace": "coupled",
            "classical_4d_photon": "no direct coupling because T_EM=0",
            "universal_clock_ratio": "no leading signal from common rescaling",
            "anomaly_or_nonuniversal_channels": "not derived in this completion",
        },
        "profiles": {
            "u": u.tolist(),
            "f_n": full["modes"].T.tolist(),
            "beta_n": beta_profiles.T.tolist(),
        },
        "criteria": CRITERIA,
        "passes": passes,
        "evidence_boundary": (
            "The normalized spectrum and beta_n follow from the declared "
            "compact-interval probe completion. The bulk did not uniquely "
            "select that completion or its Neumann boundary conditions, ell "
            "remains free, and no interaction has been compared with or "
            "detected in observations."
        ),
    }


def main() -> int:
    result = derive()
    write_json(OUTPUT_PATH, result)
    print(f"[minimal completion] {OUTPUT_PATH}")
    print(f"[observational inputs] {len(result['observational_inputs_read'])}")
    print(
        "[zero mode] beta_0={:.12g}  2 beta_0^2={:.12g}".format(
            result["zero_mode_prediction"]["beta_0"],
            result["zero_mode_prediction"][
                "relative_force_strength_2_beta_squared"
            ],
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
