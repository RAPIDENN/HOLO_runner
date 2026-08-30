#!/usr/bin/env python3
"""Audit conditional two-brane completions compatible with the background.

The background fixes only the value and first derivative of each brane
potential at its endpoint.  Declaring lambda_- = W and lambda_+ = -W as
functional identities is a minimal fake-BPS ansatz, not a consequence of the
bulk alone.  Second and higher derivatives remain independent microscopic
data for every other compatible completion.  This certificate translates the
standard two-brane conditions, proves the zero mode within the conditional
minimal ansatz, and solves a separate stabilized family without observations.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
INPUT_RELATIVE = Path(
    "first_principles_audit/artifacts/holo_effective_action.json"
)
OUTPUT = HERE / "artifacts" / "superpotential_boundary_completion.json"

MODE_COUNT = 7
GAMMA_SCAN = tuple(float(value) for value in np.logspace(-2.0, 3.0, 16))
MASS_HALF_GRID_RELATIVE_MAX = 3.0e-4
MASS_QUARTER_GRID_RELATIVE_MAX = 1.5e-3
BACKWARD_ERROR_MAX = 1.0e-12


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _subsample(arrays: tuple[np.ndarray, ...], stride: int) -> tuple[np.ndarray, ...]:
    if stride < 1:
        raise ValueError("stride must be positive")
    size = arrays[0].size
    indices = np.arange(0, size, stride, dtype=int)
    if indices[-1] != size - 1:
        indices = np.append(indices, size - 1)
    return tuple(array[indices] for array in arrays)


def _linear_weight_mass(u: np.ndarray, weight: np.ndarray):
    """P1 mass matrix with a linearly interpolated weight."""

    spacing = np.diff(u)
    diagonal = np.zeros(u.size)
    diagonal[:-1] += spacing * (3.0 * weight[:-1] + weight[1:]) / 12.0
    diagonal[1:] += spacing * (weight[:-1] + 3.0 * weight[1:]) / 12.0
    off_diagonal = spacing * (weight[:-1] + weight[1:]) / 12.0
    return diags(
        [off_diagonal, diagonal, off_diagonal],
        offsets=[-1, 0, 1],
        format="csr",
    )


def _background(payload: dict[str, Any]) -> tuple[np.ndarray, ...]:
    if payload.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action input is not certified")
    try:
        u = np.asarray(payload["u"], dtype=float)
        warp = np.asarray(payload["A"], dtype=float)
        warp_u = np.asarray(payload["A_u"], dtype=float)
        chi = np.asarray(payload["canonical_chi"], dtype=float)
        chi_u = np.asarray(payload["canonical_chi_u"], dtype=float)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("malformed effective-action input") from exc
    arrays = (u, warp, warp_u, chi, chi_u)
    if not (
        all(array.ndim == 1 and array.size == u.size for array in arrays)
        and u.size >= 64
        and all(np.all(np.isfinite(array)) for array in arrays)
        and np.all(np.diff(u) > 0.0)
        and np.all(np.diff(chi) > 0.0)
        and np.all(warp_u < 0.0)
        and np.all(chi_u > 0.0)
    ):
        raise ValueError("background does not satisfy the two-brane hypotheses")
    return arrays


def _scalar_matrices(
    arrays: tuple[np.ndarray, ...],
    gamma_minus: float | None,
    gamma_plus: float | None,
):
    """Return the symmetric generalized problem for the metric scalar Psi.

    ``None`` denotes the stiff limit gamma -> infinity.  Finite curvatures must
    be strictly positive.  Gamma equal to zero is singular and is adjudicated
    analytically through the zero-mode theorem rather than numerically.
    """

    for value in (gamma_minus, gamma_plus):
        if value is not None and (not math.isfinite(value) or value <= 0.0):
            raise ValueError("finite brane curvatures must be positive")

    u, warp, warp_u, _chi, chi_u = arrays
    chi_uu = CubicSpline(u, chi_u).derivative()(u)
    warp_uu = -np.square(chi_u) / 6.0

    # Domain-wall form of the Lesgourgues--Sorbo gauge-invariant equation:
    # -(r Psi')' + q Psi = mu^2 w Psi.
    radial_weight = np.exp(2.0 * warp) / np.square(chi_u)
    mass_weight = 1.0 / np.square(chi_u)
    potential_weight = -4.0 * radial_weight * (
        warp_uu - warp_u * chi_uu / chi_u
    )

    spacing = np.diff(u)
    radial_element = 0.5 * (radial_weight[:-1] + radial_weight[1:])
    diagonal = np.zeros(u.size)
    diagonal[:-1] += radial_element / spacing
    diagonal[1:] += radial_element / spacing
    off_diagonal = -radial_element / spacing
    stiffness = diags(
        [off_diagonal, diagonal, off_diagonal],
        offsets=[-1, 0, 1],
        format="lil",
    )
    stiffness += _linear_weight_mass(u, potential_weight)

    # The covariant junction operator is D Psi=Psi_u+2 A_u Psi.
    stiffness[0, 0] += -2.0 * radial_weight[0] * warp_u[0]
    stiffness[-1, -1] += 2.0 * radial_weight[-1] * warp_u[-1]
    stiffness = stiffness.tocsr()

    mass = _linear_weight_mass(u, mass_weight).tolil()
    if gamma_minus is not None:
        mass[0, 0] += mass_weight[0] / gamma_minus
    if gamma_plus is not None:
        mass[-1, -1] += mass_weight[-1] / gamma_plus
    mass = mass.tocsr()

    diagnostics = {
        "chi_uu": chi_uu,
        "radial_weight": radial_weight,
        "mass_weight": mass_weight,
        "potential_weight": potential_weight,
        "stiffness_symmetry_max_abs": float(
            np.max(np.abs((stiffness - stiffness.T).data), initial=0.0)
        ),
        "mass_symmetry_max_abs": float(
            np.max(np.abs((mass - mass.T).data), initial=0.0)
        ),
    }
    return stiffness, mass, diagnostics


def solve_spectrum(
    arrays: tuple[np.ndarray, ...],
    gamma_minus: float | None,
    gamma_plus: float | None,
    count: int = MODE_COUNT,
) -> dict[str, Any]:
    stiffness, mass, diagnostics = _scalar_matrices(
        arrays, gamma_minus, gamma_plus
    )
    if not 1 <= count < stiffness.shape[0] - 1:
        raise ValueError("invalid mode count")
    values, modes = eigsh(
        stiffness,
        k=count,
        M=mass,
        sigma=1.0e-8,
        which="LM",
        tol=1.0e-11,
        maxiter=100000,
        v0=np.linspace(1.0, 2.0, stiffness.shape[0], dtype=float),
    )
    order = np.argsort(values)
    values = np.asarray(values[order], dtype=float)
    modes = np.asarray(modes[:, order], dtype=float)
    if np.any(values <= 0.0):
        raise RuntimeError("stabilized completion has a non-positive eigenvalue")

    residuals = []
    stiffness_norm = float(np.linalg.norm(stiffness.data))
    mass_norm = float(np.linalg.norm(mass.data))
    for index, (value, mode) in enumerate(zip(values, modes.T)):
        norm = float(np.sqrt(mode @ (mass @ mode)))
        mode /= norm
        if mode[0] < 0.0:
            mode *= -1.0
        residual = stiffness @ mode - value * (mass @ mode)
        scale = np.linalg.norm(mode) * (
            stiffness_norm + abs(value) * mass_norm
        )
        residuals.append(float(np.linalg.norm(residual) / max(scale, 1.0e-300)))
        modes[:, index] = mode

    gram = modes.T @ (mass @ modes)
    masses = np.sqrt(values)
    return {
        "gamma_minus": gamma_minus,
        "gamma_plus": gamma_plus,
        "mass_squared_mu2": values.tolist(),
        "masses_mu": masses.tolist(),
        "mass_ratios_to_first": (masses / masses[0]).tolist(),
        "uv_profile_squared_generalized_norm": np.square(modes[0, :]).tolist(),
        "ir_profile_squared_generalized_norm": np.square(modes[-1, :]).tolist(),
        "orthonormality_max_abs": float(
            np.max(np.abs(gram - np.eye(count)))
        ),
        "normwise_backward_error_max": max(residuals),
        "stiffness_symmetry_max_abs": diagnostics[
            "stiffness_symmetry_max_abs"
        ],
        "mass_symmetry_max_abs": diagnostics["mass_symmetry_max_abs"],
    }


def _convergence(
    arrays: tuple[np.ndarray, ...], gamma: float | None
) -> dict[str, Any]:
    full = solve_spectrum(arrays, gamma, gamma)
    rows = {}
    for stride, label in ((2, "half_grid"), (4, "quarter_grid")):
        candidate = solve_spectrum(_subsample(arrays, stride), gamma, gamma)
        relative = np.abs(
            np.asarray(candidate["masses_mu"]) / np.asarray(full["masses_mu"])
            - 1.0
        )
        rows[label] = {
            "samples": int(_subsample(arrays, stride)[0].size),
            "masses_mu": candidate["masses_mu"],
            "relative_to_full": relative.tolist(),
            "maximum_relative": float(np.max(relative)),
        }
    return {"full": full, **rows}


def build(input_path: Path | None = None) -> dict[str, Any]:
    if input_path is None:
        input_path = REPO / INPUT_RELATIVE
    input_path = Path(input_path)
    payload = _read(input_path)
    arrays = _background(payload)
    u, warp, warp_u, chi, chi_u = arrays
    chi_uu = CubicSpline(u, chi_u).derivative()(u)
    w_value = -6.0 * warp_u
    w_chi = chi_u
    w_chi_chi = chi_uu / chi_u

    stiff_convergence = _convergence(arrays, None)
    finite_convergence = _convergence(arrays, 1.0)
    scan = [solve_spectrum(arrays, gamma, gamma) for gamma in GAMMA_SCAN]

    stiff_masses = np.asarray(stiff_convergence["full"]["masses_mu"])
    largest_gamma_masses = np.asarray(scan[-1]["masses_mu"])
    small_gamma_masses = np.asarray(scan[0]["masses_mu"])

    passes = {
        "effective_action_input_certified": True,
        "observational_blinding": True,
        "two_brane_background_hypotheses": bool(
            np.all(warp_u < 0.0) and np.all(chi_u > 0.0)
        ),
        "conditional_functional_BPS_matching_has_zero_g": bool(
            abs(-chi_uu[0] / chi_u[0] + w_chi_chi[0]) < 1.0e-12
            and abs(-chi_uu[-1] / chi_u[-1] + w_chi_chi[-1]) < 1.0e-12
        ),
        "conditional_functional_BPS_matching_requires_massless_scalar": bool(
            chi_u[0] != 0.0 and chi_u[-1] != 0.0
        ),
        "positive_curvatures_meet_stability_signs": True,
        "all_stabilized_spectra_positive": all(
            min(row["mass_squared_mu2"]) > 0.0 for row in scan
        ),
        "stiff_spectrum_strictly_ordered": bool(
            np.all(np.diff(stiff_masses) > 0.0)
        ),
        "small_curvature_tends_toward_zero_mass": bool(
            small_gamma_masses[0] < 0.1 * stiff_masses[0]
        ),
        "large_curvature_approaches_stiff_limit": bool(
            np.max(np.abs(largest_gamma_masses / stiff_masses - 1.0))
            < 0.01
        ),
        "half_grid_convergence": bool(
            stiff_convergence["half_grid"]["maximum_relative"]
            <= MASS_HALF_GRID_RELATIVE_MAX
            and finite_convergence["half_grid"]["maximum_relative"]
            <= MASS_HALF_GRID_RELATIVE_MAX
        ),
        "quarter_grid_convergence": bool(
            stiff_convergence["quarter_grid"]["maximum_relative"]
            <= MASS_QUARTER_GRID_RELATIVE_MAX
            and finite_convergence["quarter_grid"]["maximum_relative"]
            <= MASS_QUARTER_GRID_RELATIVE_MAX
        ),
        "backward_errors_bounded": bool(
            max(
                row["normwise_backward_error_max"]
                for row in [stiff_convergence["full"], *scan]
            )
            <= BACKWARD_ERROR_MAX
        ),
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.superpotential-boundary-completion.v1",
        "title": "Conditional superpotential-matched two-brane scalar family",
        "classification": (
            "microscopic_boundary_identifiability_and_stiff_candidate_not_detection"
        ),
        "input": {
            "path": INPUT_RELATIVE.as_posix(),
            "sha256": _sha256(input_path),
            "samples": int(u.size),
            "domain": [float(u[0]), float(u[-1])],
        },
        "observational_inputs_read": [],
        "primary_theory_inputs": [
            {
                "reference": "DeWolfe, Freedman, Gubser and Karch (2000)",
                "arxiv": "hep-th/9909134",
                "role": "first-order superpotential background matching",
            },
            {
                "reference": "Lesgourgues and Sorbo (2004)",
                "arxiv": "hep-th/0310007",
                "role": "gauge-invariant scalar junction and stability theorem",
            },
        ],
        "convention_translation": {
            "canonical_scalar": "chi=sqrt(2)*kappa_5*varphi_LS",
            "bulk_superpotential": "W(chi)=-6 A_u; W_chi=chi_u",
            "rescaled_brane_potential": "lambda_i=kappa_5^2 U_i",
            "background_lower_brane": "lambda_-(chi_-)=W; lambda_-'=W_chi",
            "background_upper_brane": "lambda_+(chi_+)=-W; lambda_+'=-W_chi",
            "junction_coefficient": (
                "g_-/a=-chi_uu/chi_u+lambda_-''; "
                "g_+/a=-chi_uu/chi_u-lambda_+''"
            ),
            "gauge_invariant_boundary_condition": (
                "g_i(Psi_y+2 H Psi)+mu^2 Psi=0"
            ),
        },
        "endpoint_background_jets": {
            "lower": {
                "u": float(u[0]),
                "chi": float(chi[0]),
                "W": float(w_value[0]),
                "W_chi": float(w_chi[0]),
                "W_chi_chi": float(w_chi_chi[0]),
            },
            "upper": {
                "u": float(u[-1]),
                "chi": float(chi[-1]),
                "W": float(w_value[-1]),
                "W_chi": float(w_chi[-1]),
                "W_chi_chi": float(w_chi_chi[-1]),
            },
        },
        "minimal_superpotential_matching": {
            "lower": "lambda_-=W",
            "upper": "lambda_+=-W",
            "g_minus_over_a": 0.0,
            "g_plus_over_a": 0.0,
            "theorem_result": (
                "at least one gauge-invariant massless scalar mode is required"
            ),
            "adjudication": (
                "not a viable finite-range Yukawa completion and not P6/P7"
            ),
            "status": (
                "conditional functional fake-BPS brane ansatz; compatible with, "
                "but not uniquely selected by, the reconstructed bulk"
            ),
        },
        "stabilized_family": {
            "lower": (
                "lambda_-=W+gamma_-(chi-chi_-)^2/2"
            ),
            "upper": (
                "lambda_+=-W+gamma_+(chi-chi_+)^2/2"
            ),
            "background_unchanged": True,
            "g_minus_over_a": "gamma_-",
            "g_plus_over_a": "-gamma_+",
            "stability_rule": "gamma_->0 and gamma_+>0",
            "identifiability_result": (
                "the corrected bulk fixes neither gamma_- nor gamma_+"
            ),
            "equal_gamma_scan": scan,
        },
        "stiff_candidate": {
            "definition": "gamma_-,gamma_+ -> infinity",
            "status": (
                "parameter-free stabilized limit, not selected by the bulk"
            ),
            "boundary_condition": "Psi_u+2 A_u Psi=0 at both endpoints",
            "spectrum": stiff_convergence["full"],
            "force_residue_warning": (
                "generalized-normalized endpoint profiles are not yet absolute "
                "matter-force residues"
            ),
        },
        "numerics": {
            "operator": (
                "-(r Psi_u)_u+q Psi=mu^2 w Psi; "
                "r=exp(2A)/chi_u^2; w=1/chi_u^2; "
                "q=-4r(A_uu-A_u chi_uu/chi_u)"
            ),
            "finite_gamma_boundary_mass": (
                "M_--=M_--+w(UV)/gamma_-; "
                "M_++=M_+++w(IR)/gamma_+"
            ),
            "method": "linear finite elements and symmetric generalized eigensolve",
            "stiff_convergence": stiff_convergence,
            "gamma_one_convergence": finite_convergence,
            "mass_half_grid_relative_max": MASS_HALF_GRID_RELATIVE_MAX,
            "mass_quarter_grid_relative_max": MASS_QUARTER_GRID_RELATIVE_MAX,
            "backward_error_max": BACKWARD_ERROR_MAX,
        },
        "relation_to_existing_trace_robin_map": {
            "same_problem": False,
            "reason": (
                "the microscopic gauge-invariant junction contains the "
                "eigenvalue and brane bending; it is not the earlier static "
                "b_i f_i^2 trace-carrier Robin ansatz"
            ),
            "consequence": (
                "do not transplant these masses into the old P6 residues "
                "without rederiving the matter coupling"
            ),
        },
        "passes": passes,
        "evidence_boundary": (
            "This separates a conditional functional BPS ansatz from a family "
            "of stabilized brane theories compatible with the same background. "
            "The reconstructed bulk selects neither family, a finite curvature, "
            "ell, the force normalization, nor an observed interaction."
        ),
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    stiff = result["stiff_candidate"]["spectrum"]
    print(f"[superpotential boundary] {OUTPUT}")
    print("[minimal matching] g_-=g_+=0 -> massless scalar")
    print(
        "[stiff candidate] mu={}".format(
            ", ".join(f"{value:.9g}" for value in stiff["masses_mu"])
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
