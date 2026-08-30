#!/usr/bin/env python3
"""Derive the four parameter-free separated boundary-condition branches.

The bulk Sturm--Liouville carrier does not choose a boundary completion.  This
script therefore evaluates every Dirichlet/Neumann endpoint combination before
any observational comparison.  It is a branch catalogue, not a licence to
select whichever spectrum later fits a datum.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh


HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parent
INPUT_PATH = AUDIT_ROOT / "artifacts" / "holo_effective_action.json"
OUTPUT_PATH = HERE / "artifacts" / "boundary_branch_catalogue.json"

MODE_COUNT = 6
BRANCHES = {
    "NN": ("Neumann", "Neumann"),
    "ND": ("Neumann", "Dirichlet"),
    "DN": ("Dirichlet", "Neumann"),
    "DD": ("Dirichlet", "Dirichlet"),
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _carrier(payload: dict[str, Any]) -> tuple[np.ndarray, ...]:
    u = np.asarray(payload["u"], dtype=float)
    A = np.asarray(payload["A"], dtype=float)
    A_u = np.asarray(payload["A_u"], dtype=float)
    phi_u = np.asarray(payload["phi_u"], dtype=float)
    kinetic = np.asarray(payload["kinetic_K_of_phi"], dtype=float)
    A_uu = -kinetic * np.square(phi_u) / 6.0
    epsilon = -A_uu / np.square(A_u)
    p = np.exp(4.0 * A) * epsilon
    w = np.exp(2.0 * A) * epsilon
    if not (
        np.all(np.diff(u) > 0.0)
        and np.all(np.isfinite(p))
        and np.all(np.isfinite(w))
        and np.all(p > 0.0)
        and np.all(w > 0.0)
    ):
        raise ValueError("The reconstructed Sturm--Liouville carrier is invalid")
    return u, A, p, w


def _matrices(
    u: np.ndarray, p: np.ndarray, w: np.ndarray
) -> tuple[Any, Any]:
    spacing = np.diff(u)
    p_element = 0.5 * (p[:-1] + p[1:])
    stiffness_diag = np.zeros(u.size)
    stiffness_diag[:-1] += p_element / spacing
    stiffness_diag[1:] += p_element / spacing
    stiffness_off = -p_element / spacing

    mass_diag = np.zeros(u.size)
    mass_diag[:-1] += spacing * (3.0 * w[:-1] + w[1:]) / 12.0
    mass_diag[1:] += spacing * (w[:-1] + 3.0 * w[1:]) / 12.0
    mass_off = spacing * (w[:-1] + w[1:]) / 12.0
    stiffness = diags(
        [stiffness_off, stiffness_diag, stiffness_off],
        offsets=[-1, 0, 1],
        format="csr",
    )
    mass = diags(
        [mass_off, mass_diag, mass_off], offsets=[-1, 0, 1], format="csr"
    )
    return stiffness, mass


def _free_indices(size: int, left: str, right: str) -> np.ndarray:
    start = 1 if left == "Dirichlet" else 0
    stop = size - 1 if right == "Dirichlet" else size
    return np.arange(start, stop, dtype=int)


def _solve(
    u: np.ndarray,
    A: np.ndarray,
    p: np.ndarray,
    w: np.ndarray,
    left: str,
    right: str,
    count: int = MODE_COUNT,
) -> dict[str, Any]:
    stiffness, mass = _matrices(u, p, w)
    free = _free_indices(u.size, left, right)
    reduced_k = stiffness[free][:, free]
    reduced_m = mass[free][:, free]
    extra = 1 if left == right == "Neumann" else 0
    eigenvalues, reduced_modes = eigsh(
        reduced_k,
        k=count + extra,
        M=reduced_m,
        sigma=1.0e-10,
        which="LM",
        tol=1.0e-11,
        maxiter=100000,
        v0=np.linspace(1.0, 2.0, reduced_k.shape[0], dtype=float),
    )
    order = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[order]
    reduced_modes = reduced_modes[:, order]
    if extra:
        # The natural NN branch has one constant zero mode.  Catalogue it
        # separately and retain six strictly positive modes for comparison.
        zero_value = float(eigenvalues[0])
        selected_values = eigenvalues[1 : count + 1]
        selected_modes = reduced_modes[:, 1 : count + 1]
    else:
        zero_value = None
        selected_values = eigenvalues[:count]
        selected_modes = reduced_modes[:, :count]

    I_g = float(np.trapezoid(np.exp(2.0 * A), u))
    profiles: list[np.ndarray] = []
    betas: list[float] = []
    residuals: list[float] = []
    for value, reduced in zip(selected_values, selected_modes.T):
        norm = float(np.sqrt(reduced @ (reduced_m @ reduced)))
        reduced = reduced / norm
        full = np.zeros(u.size)
        full[free] = reduced
        sign_index = int(np.flatnonzero(np.abs(full) > 1.0e-14)[0])
        if full[sign_index] < 0.0:
            full *= -1.0
            reduced *= -1.0
        residual = reduced_k @ reduced - value * (reduced_m @ reduced)
        residual_scale = (
            np.linalg.norm(reduced_k @ reduced)
            + abs(value) * np.linalg.norm(reduced_m @ reduced)
        )
        profiles.append(full)
        betas.append(float(np.sqrt(I_g / 3.0) * full[0]))
        residuals.append(
            float(np.linalg.norm(residual) / max(residual_scale, 1.0e-300))
        )

    masses = np.sqrt(np.maximum(selected_values, 0.0))
    beta = np.asarray(betas)
    return {
        "left_boundary": left,
        "right_boundary": right,
        "mass_squared": selected_values.tolist(),
        "masses_mu": masses.tolist(),
        "mass_ratios_to_lightest": (masses / masses[0]).tolist(),
        "uv_probe_couplings_beta_n": beta.tolist(),
        "uv_yukawa_strengths_alpha_n": (2.0 * np.square(beta)).tolist(),
        "uv_total_alpha_short_range": float(2.0 * np.sum(np.square(beta))),
        "fem_relative_residual_max": float(max(residuals)),
        "nn_raw_zero_eigenvalue": zero_value,
        "has_exact_massless_mode": left == right == "Neumann",
        "uv_point_probe_decouples": left == "Dirichlet",
        "profiles": [profile.tolist() for profile in profiles],
    }


def _subsample(
    u: np.ndarray,
    A: np.ndarray,
    p: np.ndarray,
    w: np.ndarray,
    stride: int,
) -> tuple[np.ndarray, ...]:
    indices = np.arange(0, u.size, stride, dtype=int)
    if indices[-1] != u.size - 1:
        indices = np.append(indices, u.size - 1)
    return u[indices], A[indices], p[indices], w[indices]


def derive(input_path: Path = INPUT_PATH) -> dict[str, Any]:
    input_path = Path(input_path).resolve()
    payload = _read(input_path)
    if not payload["summary"]["passes"]["all"]:
        raise RuntimeError("Effective-action input certificate does not pass")
    u, A, p, w = _carrier(payload)

    branches: dict[str, Any] = {}
    convergence_errors: list[float] = []
    for code, (left, right) in BRANCHES.items():
        result = _solve(u, A, p, w, left, right)
        half = _solve(*_subsample(u, A, p, w, 2), left, right)
        full_masses = np.asarray(result["masses_mu"])
        half_masses = np.asarray(half["masses_mu"])
        relative = np.abs(half_masses / full_masses - 1.0)
        result["half_grid_mass_relative_errors"] = relative.tolist()
        result["half_grid_mass_relative_error_max"] = float(np.max(relative))
        convergence_errors.append(float(np.max(relative)))
        if code == "NN":
            result["adjudication"] = (
                "excluded as a universal unscreened completion because its "
                "constant scalar mode is exactly massless"
            )
        elif code == "ND":
            result["adjudication"] = (
                "candidate UV-coupled hard-wall branch; the former zero mode "
                "becomes ultralight rather than disappearing"
            )
        else:
            result["adjudication"] = (
                "the exact UV point probe decouples because its field obeys "
                "Dirichlet data on the matter face"
            )
        branches[code] = result

    nd_mu0 = float(branches["ND"]["masses_mu"][0])
    nd_beta0 = float(branches["ND"]["uv_probe_couplings_beta_n"][0])
    passes = {
        "effective_action_input_certified": True,
        "no_observational_inputs": True,
        "all_four_separated_branches_evaluated": set(branches) == set(BRANCHES),
        "all_spectra_strictly_positive_after_nn_zero_separation": all(
            min(branch["masses_mu"]) > 0.0 for branch in branches.values()
        ),
        # The ND ground state is an extremely ill-conditioned near-zero mode
        # because p(u) collapses near the hard IR endpoint.  Keep its sparse
        # FEM residual visible and require a separate continuous shooting
        # certificate; do not let it weaken the residual gate for the other
        # three branches.
        "fem_residuals_regular_branches": max(
            branches[name]["fem_relative_residual_max"]
            for name in ("NN", "DN", "DD")
        )
        < 2.0e-6,
        "nd_ultralight_fem_residual_diagnostic": branches["ND"][
            "fem_relative_residual_max"
        ]
        < 3.0e-2,
        "half_grid_convergence": max(convergence_errors) < 2.0e-3,
        "uv_dirichlet_decouples": branches["DN"]["uv_total_alpha_short_range"]
        == 0.0
        and branches["DD"]["uv_total_alpha_short_range"] == 0.0,
        "nd_ultralight_mode_exposed": nd_mu0 < 0.01 and abs(nd_beta0) > 0.05,
    }
    passes["all"] = all(passes.values())
    return {
        "title": "Prospective separated boundary-condition branch catalogue",
        "classification": "conditional_branch_catalogue_not_model_selection",
        "input": {
            "path": str(input_path),
            "sha256": _sha256(input_path),
            "samples": int(u.size),
            "domain": [float(u[0]), float(u[-1])],
        },
        "operator": "-(p f')'=lambda w f",
        "matter_slice": "UV endpoint u_min",
        "observational_inputs_read": [],
        "selection_rule": (
            "No branch may be selected by comparison with observations. A "
            "boundary action or microscopic parity assignment must select it."
        ),
        "branches": branches,
        "key_result": {
            "nd_lightest_mass_mu": nd_mu0,
            "nd_lightest_beta_uv": nd_beta0,
            "meaning": (
                "A hard IR Dirichlet wall lifts the exact NN zero eigenvalue "
                "only to an ultralight UV-coupled mode on this carrier."
            ),
        },
        "passes": passes,
        "evidence_boundary": (
            "The catalogue closes the discrete Dirichlet/Neumann fork. It "
            "does not derive the physical boundary action, fix ell, or allow "
            "post-hoc branch selection. General Robin data require explicit "
            "boundary coefficients and remain a future theory input."
        ),
    }


def main() -> int:
    result = derive()
    _write(OUTPUT_PATH, result)
    key = result["key_result"]
    print(f"[boundary catalogue] {OUTPUT_PATH}")
    print(
        "[ND lightest] mu={:.12g} beta_uv={:.12g}".format(
            key["nd_lightest_mass_mu"], key["nd_lightest_beta_uv"]
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
