#!/usr/bin/env python3
"""Three-stage, preregistered audit of the HOLO Einstein--dilaton chain.

Stage 1 derives and seals an exact reference solution without reading any HOLO
answer artifact.  Stage 2 opens the frozen candidates and evaluates them against
the sealed equations.  Stage 3 adjudicates the result with a separate numerical
integration and a domain-wall/conformal-coordinate transformation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
import sympy as sp
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.special import kv, kvp


RUNNER_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = Path(__file__).resolve().parent
ARTIFACT_ROOT = AUDIT_ROOT / "artifacts"
DEFAULT_INSTRUMENT_ROOT = RUNNER_ROOT.parent / "HOLO_TRANSDUCTOR_instrument"

FROZEN_HASHES = {
    "pdf": "95af056f044d761f9f4ed79fc574788c70beeabaef341d726dd846dd7af73e58",
    "trace": "e1c4b9d8495a563be31c36ceeeea7575b1d46afae74b45394edb77a8ffb06725",
    "ansatz": "caed952a68815f8267f8f5ba60f709484041318d5498323e91350501b5eaaf89",
    "rust_rhs": "2a44892d782fab8d6667f36775a9a35d49c2869a9b48cb6c0d4ace1153456e2a",
    "spectrum": "6e3b56a805d1dec7634d91d2ac58ec29bd3e979c5c02530fd17dc1eba7a9ccb1",
    "sparc": "a218ead2a7568cfddc5e7c6ce31670aea15fb6cd7e92b9c8e2770257c25f168b",
    "growth": "e5b90a18d40d4a2715b808607e064358bd9ed5f87ffcf90474a11a3dc0077118",
    "nist": "27e84a3632cae471fa7e79c143698743fce11e958e852002b8c647245905f2ae",
}

THRESHOLDS = {
    "kinematic_normalized_rms": 1e-2,
    "constraint_normalized_p95": 1e-3,
    "eom_normalized_rms": 1e-2,
    "exact_symbolic_abs": 1e-12,
    "exact_integration_max_abs": 1e-7,
    "coordinate_residual_max_abs": 1e-11,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def rms(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(values * values)))


def normalized_rms(residual: np.ndarray, *terms: np.ndarray) -> float:
    residual = np.asarray(residual, dtype=float)
    scale = np.zeros_like(residual)
    for term in terms:
        scale += np.abs(np.asarray(term, dtype=float))
    denominator = rms(scale)
    return rms(residual) / max(denominator, np.finfo(float).eps)


def interior(values: np.ndarray, trim: int = 5) -> np.ndarray:
    values = np.asarray(values)
    if values.size <= 2 * trim:
        raise ValueError("Not enough samples for preregistered endpoint trimming")
    return values[trim:-trim]


def exact_reference_arrays(
    u: np.ndarray, *, L: float = 1.0, phi0: float = 1e-3, A0: float = 0.0
) -> dict[str, np.ndarray]:
    """Exact superpotential flow fixed before opening the answer artifacts."""
    u = np.asarray(u, dtype=float)
    x = u / L
    phi = phi0 * np.exp(x)
    dphi = phi / L
    ddphi = phi / (L * L)
    A = A0 - x - (phi * phi - phi0 * phi0) / 24.0
    dA = -1.0 / L - phi * phi / (12.0 * L)
    ddA = -(phi * phi) / (6.0 * L * L)
    V = -12.0 / (L * L) - 1.5 * phi * phi / (L * L) - phi**4 / (
        12.0 * L * L
    )
    dV = -3.0 * phi / (L * L) - phi**3 / (3.0 * L * L)
    return {
        "u": u,
        "phi": phi,
        "dphi": dphi,
        "ddphi": ddphi,
        "A": A,
        "dA": dA,
        "ddA": ddA,
        "V": V,
        "dV": dV,
    }


def symbolic_stage1() -> dict[str, Any]:
    """Derive the exact flow algebraically without reading repository outputs."""
    u = sp.symbols("u", real=True)
    L = sp.symbols("L", positive=True)
    phi0 = sp.symbols("phi_0", positive=True)
    A0 = sp.symbols("A_0", real=True)
    phi = phi0 * sp.exp(u / L)
    A = A0 - u / L - (phi**2 - phi0**2) / 24
    V = -12 / L**2 - 3 * phi**2 / (2 * L**2) - phi**4 / (12 * L**2)
    dV = sp.diff(
        -12 / L**2
        - 3 * sp.Symbol("p") ** 2 / (2 * L**2)
        - sp.Symbol("p") ** 4 / (12 * L**2),
        sp.Symbol("p"),
    ).subs(sp.Symbol("p"), phi)

    phi_u = sp.diff(phi, u)
    A_u = sp.diff(A, u)
    residuals = {
        "scalar_domain_wall": sp.simplify(sp.diff(phi, u, 2) + 4 * A_u * phi_u - dV),
        "warp_domain_wall": sp.simplify(sp.diff(A, u, 2) + phi_u**2 / 6),
        "constraint_domain_wall": sp.simplify(12 * A_u**2 - phi_u**2 / 2 + V),
    }

    # Chain-rule form of the conformal-gauge equations.  Since dz/du=e^-A,
    # d/dz=e^A d/du.
    phi_z = sp.exp(A) * phi_u
    A_z = sp.exp(A) * A_u
    phi_zz = sp.exp(2 * A) * (sp.diff(phi, u, 2) + A_u * phi_u)
    A_zz = sp.exp(2 * A) * (sp.diff(A, u, 2) + A_u**2)
    residuals.update(
        {
            "scalar_conformal": sp.simplify(phi_zz + 3 * A_z * phi_z - sp.exp(2 * A) * dV),
            "warp_conformal": sp.simplify(A_zz - A_z**2 + phi_z**2 / 6),
            "constraint_conformal": sp.simplify(
                12 * A_z**2 - phi_z**2 / 2 + sp.exp(2 * A) * V
            ),
        }
    )
    rendered = {name: str(sp.simplify(value)) for name, value in residuals.items()}
    checks = {name: value == "0" for name, value in rendered.items()}

    return {
        "stage": 1,
        "reads_existing_answer_artifacts": False,
        "action": "S=(2*kappa5^2)^-1 int sqrt(-g) [R-(dphi)^2/2-V(phi)]",
        "domain_wall_gauge": "ds^2=exp(2A(u))*eta_mn dx^m dx^n+du^2",
        "field_equations": {
            "scalar": "phi_uu+4*A_u*phi_u=V_phi",
            "warp": "A_uu=-phi_u^2/6",
            "constraint": "12*A_u^2-phi_u^2/2+V=0",
        },
        "conformal_equations": {
            "coordinate": "dz/du=exp(-A)",
            "scalar": "phi_zz+3*A_z*phi_z=exp(2A)*V_phi",
            "warp": "A_zz-A_z^2=-phi_z^2/6",
            "constraint": "12*A_z^2-phi_z^2/2+exp(2A)*V=0",
        },
        "exact_reference": {
            "superpotential": "W=6/L+phi^2/(2L)",
            "potential": "V=-12/L^2-3phi^2/(2L^2)-phi^4/(12L^2)",
            "physical_mass_squared_times_L_squared": -3.0,
            "solution": {
                "phi": "phi0*exp((u-u0)/L)",
                "A": "A0-(u-u0)/L-(phi(u)^2-phi0^2)/24",
            },
        },
        "symbolic_residuals": rendered,
        "symbolic_zero_checks": checks,
        "all_symbolic_checks_pass": all(checks.values()),
        "thresholds": THRESHOLDS,
    }


def _candidate_paths(instrument_root: Path) -> dict[str, Path]:
    paper_root = RUNNER_ROOT / "A_single_Einstein_Dilaton geometry"
    return {
        # The audit answer key is the immutable pre-revision PDF, never the
        # mutable delivery path used by later corrected builds.
        "pdf": paper_root / "A_single_Einstein-Dilaton_geometry_v1_frozen.pdf",
        "trace": instrument_root / "data/internal/holo_physics_trace_ed_industrial.json",
        "ansatz": instrument_root / "data/archive/symbolic_distill/PRIMARY_ANSATZ.json",
        "rust_rhs": instrument_root
        / "kernel/rust/holo_kerneld/src/ed_solver_plus/implicit_solver.rs",
        "spectrum": paper_root / "artifacts/invariant_flux_spectrum_u.json",
        "sparc": paper_root / "artifacts/sparc_forward_eval.json",
        "growth": paper_root / "artifacts/growth_validation_boss_dr12.json",
        "nist": paper_root / "artifacts/nist_comparison_uv.json",
    }


def verify_frozen_inputs(instrument_root: Path) -> dict[str, Any]:
    paths = _candidate_paths(instrument_root)
    report: dict[str, Any] = {}
    for name, expected in FROZEN_HASHES.items():
        path = paths[name]
        actual = sha256_file(path)
        report[name] = {
            "path": str(path),
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": actual == expected,
        }
    if not all(item["match"] for item in report.values()):
        mismatches = [name for name, item in report.items() if not item["match"]]
        raise RuntimeError(f"Frozen audit inputs changed: {', '.join(mismatches)}")
    return report


def potential_implemented(phi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Literal Rust/Python convention: m_sq=-3 in V=-12-m_sq*phi^2/2."""
    return -12.0 + 1.5 * phi * phi, 3.0 * phi


def potential_intended_bf(phi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Physical m^2=-3 convention: V=-12+m^2*phi^2/2."""
    return -12.0 - 1.5 * phi * phi, -3.0 * phi


def evaluate_trace_equations(
    trace_payload: dict[str, Any],
    potential: Callable[[np.ndarray], tuple[np.ndarray, np.ndarray]],
    *,
    rho0: float = 0.01,
    kappa: float = 1.0,
    z_scale: float = 1.0,
) -> dict[str, Any]:
    trace = trace_payload["trace"]
    u = np.asarray(trace["z"], dtype=float)
    phi = np.asarray(trace["phi"], dtype=float)
    dphi = np.asarray(trace["dphi"], dtype=float)
    A = np.asarray(trace["A"], dtype=float)
    dA = np.asarray(trace["dA"], dtype=float)
    V, dV = potential(phi)
    rho = rho0 * np.exp(-u / z_scale)

    phi_u_num = np.gradient(phi, u, edge_order=2)
    A_u_num = np.gradient(A, u, edge_order=2)
    phi_uu_num = np.gradient(dphi, u, edge_order=2)
    A_uu_num = np.gradient(dA, u, edge_order=2)

    r_phi_kin = phi_u_num - dphi
    r_A_kin = A_u_num - dA
    r_scalar = phi_uu_num + 4.0 * dA * dphi - dV
    r_warp_with_source = A_uu_num + dphi * dphi / 6.0 + kappa * rho
    r_warp_vacuum = A_uu_num + dphi * dphi / 6.0
    H = 12.0 * dA * dA - 0.5 * dphi * dphi + V

    arrays = [
        u,
        phi,
        dphi,
        A,
        dA,
        V,
        dV,
        rho,
        phi_u_num,
        A_u_num,
        phi_uu_num,
        A_uu_num,
        r_phi_kin,
        r_A_kin,
        r_scalar,
        r_warp_with_source,
        r_warp_vacuum,
        H,
    ]
    (
        u_i,
        phi_i,
        dphi_i,
        A_i,
        dA_i,
        V_i,
        dV_i,
        rho_i,
        phi_u_num_i,
        A_u_num_i,
        phi_uu_num_i,
        A_uu_num_i,
        r_phi_kin_i,
        r_A_kin_i,
        r_scalar_i,
        r_warp_source_i,
        r_warp_vacuum_i,
        H_i,
    ) = [interior(item) for item in arrays]

    constraint_scale = (
        np.abs(12.0 * dA_i * dA_i)
        + np.abs(0.5 * dphi_i * dphi_i)
        + np.abs(V_i)
    )
    H_normalized = np.abs(H_i) / np.maximum(
        constraint_scale, np.finfo(float).eps
    )
    metrics = {
        "phi_kinematic_normalized_rms": normalized_rms(
            r_phi_kin_i, phi_u_num_i, dphi_i
        ),
        "A_kinematic_normalized_rms": normalized_rms(r_A_kin_i, A_u_num_i, dA_i),
        "constraint_abs_max": float(np.max(np.abs(H_i))),
        "constraint_normalized_p95": float(np.percentile(H_normalized, 95.0)),
        "scalar_eom_normalized_rms": normalized_rms(
            r_scalar_i, phi_uu_num_i, 4.0 * dA_i * dphi_i, dV_i
        ),
        "warp_source_eom_normalized_rms": normalized_rms(
            r_warp_source_i, A_uu_num_i, dphi_i * dphi_i / 6.0, kappa * rho_i
        ),
        "warp_vacuum_eom_normalized_rms": normalized_rms(
            r_warp_vacuum_i, A_uu_num_i, dphi_i * dphi_i / 6.0
        ),
    }
    passes = {
        "phi_kinematic": metrics["phi_kinematic_normalized_rms"]
        <= THRESHOLDS["kinematic_normalized_rms"],
        "A_kinematic": metrics["A_kinematic_normalized_rms"]
        <= THRESHOLDS["kinematic_normalized_rms"],
        "constraint": metrics["constraint_normalized_p95"]
        <= THRESHOLDS["constraint_normalized_p95"],
        "scalar_eom": metrics["scalar_eom_normalized_rms"]
        <= THRESHOLDS["eom_normalized_rms"],
        "warp_source_eom": metrics["warp_source_eom_normalized_rms"]
        <= THRESHOLDS["eom_normalized_rms"],
    }

    # If rho is inserted only into A'', differentiating the unchanged vacuum
    # constraint gives H'=-24*kappa*A'*rho.  This predicts constraint drift and
    # exposes the missing matter constraint/conservation equation.
    predicted_H = H[0] + cumulative_trapezoid(
        -24.0 * kappa * dA * rho, u, initial=0.0
    )
    propagation_error = interior(H - predicted_H)
    source_consistency = {
        "vacuum_constraint_derivative_identity": "H_u=-24*kappa*A_u*rho",
        "source_is_nonzero": bool(np.any(np.abs(rho_i) > 0.0)),
        "unchanged_vacuum_constraint_is_preserved": False,
        "predicted_constraint_drift_end": float(predicted_H[-1] - predicted_H[0]),
        "observed_constraint_drift_end": float(H[-1] - H[0]),
        "propagation_error_rms": rms(propagation_error),
        "formal_status": "inconsistent_without_a_declared_matter_action_and_modified_constraint",
    }

    return {
        "domain_interpreted_as": "domain_wall_u",
        "n_samples": int(u.size),
        "metrics": metrics,
        "passes": passes,
        "all_preregistered_trace_checks_pass": all(passes.values()),
        "source_consistency": source_consistency,
        "coordinate_reference": {
            "implemented_delta": "delta=-u*A_u-1",
            "domain_wall_ads_reference": "A_u=+-1/L (constant)",
            "conformal_ads_reference": "A_z=-1/z",
            "classification": "inconsistent_coordinate_mix",
        },
        "ranges": {
            "u": [float(u[0]), float(u[-1])],
            "phi": [float(np.min(phi)), float(np.max(phi))],
            "A": [float(np.min(A)), float(np.max(A))],
        },
    }


def evaluate_holonomic_ansatz(ansatz_payload: dict[str, Any]) -> dict[str, Any]:
    terms = ansatz_payload["phi_terms"]
    z = np.linspace(0.01, 2.0, 2000)
    p0 = float(terms["p0"])
    p1 = float(terms["p1"])
    c0 = float(terms["c0"])
    k0 = float(terms["k0"])
    c1 = float(terms["c1"])
    k1 = float(terms["k1"])

    phi = p0 + p1 * z + c0 * kv(0, k0 * z) + c1 * kv(1, k1 * z)
    dphi = p1 + c0 * k0 * kvp(0, k0 * z, 1) + c1 * k1 * kvp(1, k1 * z, 1)
    ddphi = c0 * k0**2 * kvp(0, k0 * z, 2) + c1 * k1**2 * kvp(
        1, k1 * z, 2
    )
    V, dV = potential_implemented(phi)
    q = (0.5 * dphi * dphi - V) / 12.0
    if np.any(q <= 0.0):
        raise ValueError("Holonomic ansatz has a non-real A' branch")
    sqrt_q = np.sqrt(q)
    dA = -sqrt_q
    dq = dphi * (ddphi - dV) / 12.0
    ddA = -dq / (2.0 * sqrt_q)

    H = 12.0 * dA * dA - 0.5 * dphi * dphi + V
    scalar = ddphi + 4.0 * dA * dphi - dV
    warp = ddA + dphi * dphi / 6.0
    H_i, scalar_i, warp_i = (interior(H), interior(scalar), interior(warp))
    ddphi_i, dA_i, dphi_i, dV_i, ddA_i = (
        interior(ddphi),
        interior(dA),
        interior(dphi),
        interior(dV),
        interior(ddA),
    )
    V_i = interior(V)
    constraint_scale = (
        np.abs(12.0 * dA_i * dA_i)
        + np.abs(0.5 * dphi_i * dphi_i)
        + np.abs(V_i)
    )
    metrics = {
        "constraint_normalized_p95": float(
            np.percentile(
                np.abs(H_i) / np.maximum(constraint_scale, np.finfo(float).eps),
                95.0,
            )
        ),
        "scalar_eom_normalized_rms": normalized_rms(
            scalar_i, ddphi_i, 4.0 * dA_i * dphi_i, dV_i
        ),
        "warp_eom_normalized_rms": normalized_rms(
            warp_i, ddA_i, dphi_i * dphi_i / 6.0
        ),
    }
    passes = {
        "constraint": metrics["constraint_normalized_p95"]
        <= THRESHOLDS["constraint_normalized_p95"],
        "scalar_eom": metrics["scalar_eom_normalized_rms"]
        <= THRESHOLDS["eom_normalized_rms"],
        "warp_eom": metrics["warp_eom_normalized_rms"]
        <= THRESHOLDS["eom_normalized_rms"],
    }
    return {
        "interpretation": "domain_wall_because_the_imposed_constraint_is_domain_wall",
        "metrics": metrics,
        "passes": passes,
        "all_full_equation_checks_pass": all(passes.values()),
        "classification": "holonomic_constraint_solution_not_full_ED_solution"
        if not all(passes.values())
        else "full_ED_solution_on_preregistered_tests",
    }


def static_claim_audit(instrument_root: Path) -> dict[str, Any]:
    paper_root = RUNNER_ROOT / "A_single_Einstein_Dilaton geometry" / "artifacts"
    sparc = load_json(paper_root / "sparc_forward_eval.json")
    growth = load_json(paper_root / "growth_report.json")
    nist = load_json(paper_root / "nist_comparison_uv.json")
    tau = load_json(paper_root / "tau_from_dictionary.json")
    spectrum = load_json(paper_root / "covariant_invariance_proof.json")
    optimizer_path = instrument_root / "tools/phase5/ed_p5_industrial.py"
    optimizer_source = optimizer_path.read_text(encoding="utf-8")
    optimizer_markers = {
        "uses_differential_evolution": "differential_evolution" in optimizer_source,
        "objective_reads_v_obs": "v_obs = gal['v_obs']" in optimizer_source,
        "optimizes_all_loaded_galaxies": "optimize_params(all_galaxies" in optimizer_source,
    }

    return {
        "scalar_spectrum": {
            "artifact_assumption": spectrum.get("assumption"),
            "solver_gauge_from_sealed_derivation": "domain_wall",
            "classification": "numerical_operator_result_on_a_coordinate-misidentified_trace",
            "physical_claim_status": "unsupported_until_recomputed_on_a_full_ED_solution",
        },
        "sparc": {
            "final_curve_uses_v_obs_directly": bool(
                sparc.get("meta", {}).get("uses_v_obs_in_construction", True)
            ),
            "global_parameter_count": len(sparc.get("model", {}).get("params", {})),
            "calibration_evidence": optimizer_markers,
            "classification": "phenomenological_in_sample_calibration",
            "reason": "The final curve is forward-evaluated, but its global parameters were optimized on the same 175 observed curves.",
        },
        "growth": {
            "mapping": growth.get("mapping"),
            "classification": "phenomenological_coordinate_dictionary",
            "reason": "z_trace=1+z_cosmo is declared as a mapping, not derived from the five-dimensional action.",
        },
        "laboratory": {
            "chi2_over_n": nist.get("metrics", {}).get("chi2_over_n"),
            "pearson_r": nist.get("metrics", {}).get("pearson_r"),
            "tau_non_uniqueness_note": tau.get("notes", {}).get("non_uniqueness"),
            "classification": "phenomenological_null_comparison",
            "reason": "The UV kernel and physical time conversion are additional assumptions; a null correlation does not derive or validate them.",
        },
        "cross_domain_unification": {
            "classification": "unsupported",
            "reason": "Reuse of one frozen array across declared readout maps is reproducible, but the maps are not jointly derived from the action.",
        },
    }


def stage2_compare(instrument_root: Path) -> dict[str, Any]:
    frozen = verify_frozen_inputs(instrument_root)
    paths = _candidate_paths(instrument_root)
    trace = load_json(paths["trace"])
    ansatz = load_json(paths["ansatz"])
    return {
        "stage": 2,
        "frozen_inputs": frozen,
        "trace_literal_implemented_potential": evaluate_trace_equations(
            trace, potential_implemented
        ),
        "trace_intended_bf_mass_potential": evaluate_trace_equations(
            trace, potential_intended_bf
        ),
        "holonomic_ansatz": evaluate_holonomic_ansatz(ansatz),
        "claim_audit": static_claim_audit(instrument_root),
    }


def stage3_adjudicate(stage1: dict[str, Any], stage2: dict[str, Any]) -> dict[str, Any]:
    L = 1.0
    phi0 = 1e-3
    A0 = 0.0
    u = np.linspace(0.0, 2.0, 401)
    exact = exact_reference_arrays(u, L=L, phi0=phi0, A0=A0)

    def rhs(_u: float, state: np.ndarray) -> np.ndarray:
        phi, dphi, _A, dA = state
        dV = -3.0 * phi / (L * L) - phi**3 / (3.0 * L * L)
        return np.array([dphi, dV - 4.0 * dA * dphi, dA, -dphi * dphi / 6.0])

    y0 = np.array(
        [exact["phi"][0], exact["dphi"][0], exact["A"][0], exact["dA"][0]]
    )
    solution = solve_ivp(
        rhs,
        (float(u[0]), float(u[-1])),
        y0,
        t_eval=u,
        method="DOP853",
        rtol=1e-12,
        atol=1e-14,
    )
    target = np.vstack([exact["phi"], exact["dphi"], exact["A"], exact["dA"]])
    integration_errors = np.max(np.abs(solution.y - target), axis=1)
    integration_max = float(np.max(integration_errors))

    expA = np.exp(exact["A"])
    phi_z = expA * exact["dphi"]
    A_z = expA * exact["dA"]
    phi_zz = expA**2 * (exact["ddphi"] + exact["dA"] * exact["dphi"])
    A_zz = expA**2 * (exact["ddA"] + exact["dA"] ** 2)
    conformal_residuals = {
        "scalar": phi_zz + 3.0 * A_z * phi_z - expA**2 * exact["dV"],
        "warp": A_zz - A_z**2 + phi_z**2 / 6.0,
        "constraint": 12.0 * A_z**2 - 0.5 * phi_z**2 + expA**2 * exact["V"],
    }
    conformal_max = {
        name: float(np.max(np.abs(values)))
        for name, values in conformal_residuals.items()
    }

    z_conformal = 1.0 + cumulative_trapezoid(np.exp(-exact["A"]), u, initial=0.0)
    exact_baseline = {
        "description": "Exact five-dimensional Einstein--dilaton superpotential flow; not fitted to an observational result.",
        "parameters": {"L": L, "phi_at_u0": phi0, "A_at_u0": A0},
        "coordinate_relation": "dz/du=exp(-A), z(u=0)=1",
        "u": u.tolist(),
        "z_conformal": z_conformal.tolist(),
        "phi": exact["phi"].tolist(),
        "phi_u": exact["dphi"].tolist(),
        "A": exact["A"].tolist(),
        "A_u": exact["dA"].tolist(),
        "V": exact["V"].tolist(),
        "independent_integration_max_abs_error": integration_max,
        "conformal_equation_max_abs_residuals": conformal_max,
    }
    write_json(ARTIFACT_ROOT / "exact_ed_baseline.json", exact_baseline)

    exact_pass = bool(stage1["all_symbolic_checks_pass"])
    integration_pass = integration_max <= THRESHOLDS["exact_integration_max_abs"]
    coordinate_pass = max(conformal_max.values()) <= THRESHOLDS[
        "coordinate_residual_max_abs"
    ]

    literal = stage2["trace_literal_implemented_potential"]
    intended = stage2["trace_intended_bf_mass_potential"]
    holonomic = stage2["holonomic_ansatz"]
    claim_audit = stage2["claim_audit"]

    claims = {
        "field_equations_from_declared_action": {
            "classification": "derived",
            "pass": exact_pass and integration_pass and coordinate_pass,
        },
        "new_exact_superpotential_baseline": {
            "classification": "derived_and_independently_reproduced",
            "pass": exact_pass and integration_pass and coordinate_pass,
        },
        "frozen_industrial_trace_solves_declared_action": {
            "classification": "inconsistent",
            "pass": bool(
                literal["all_preregistered_trace_checks_pass"]
                or intended["all_preregistered_trace_checks_pass"]
            ),
        },
        "holonomic_ansatz_is_a_full_solution": {
            "classification": holonomic["classification"],
            "pass": bool(holonomic["all_full_equation_checks_pass"]),
        },
        "reported_scalar_ratio_is_a_physical_prediction_of_the_declared_action": {
            "classification": claim_audit["scalar_spectrum"]["physical_claim_status"],
            "pass": False,
        },
        "sparc_result_is_out_of_sample_prediction": {
            "classification": claim_audit["sparc"]["classification"],
            "pass": False,
        },
        "growth_mapping_is_derived_from_the_action": {
            "classification": claim_audit["growth"]["classification"],
            "pass": False,
        },
        "nist_null_validates_the_uv_coupling": {
            "classification": claim_audit["laboratory"]["classification"],
            "pass": False,
        },
        "one_geometry_physically_unifies_all_reported_domains": {
            "classification": claim_audit["cross_domain_unification"]["classification"],
            "pass": False,
        },
    }

    return {
        "stage": 3,
        "independent_integration": {
            "method": "scipy.solve_ivp_DOP853_on_second_order_equations",
            "component_max_abs_errors": {
                "phi": float(integration_errors[0]),
                "phi_u": float(integration_errors[1]),
                "A": float(integration_errors[2]),
                "A_u": float(integration_errors[3]),
            },
            "max_abs_error": integration_max,
            "pass": integration_pass,
        },
        "conformal_coordinate_check": {
            "max_abs_residuals": conformal_max,
            "pass": coordinate_pass,
        },
        "claim_matrix": claims,
        "surviving_manuscript_scope": {
            "title": "A first-principles consistency audit and exact baseline for a five-dimensional Einstein--dilaton flow",
            "supported": [
                "variation of the scalar-gravity action in domain-wall gauge",
                "exact superpotential solution with m^2 L^2=-3",
                "independent numerical and coordinate-covariance checks",
                "equation-level audit of the frozen HOLO trace",
            ],
            "must_be_reframed_as_phenomenology": [
                "SPARC readout",
                "trace-to-cosmology dictionary",
                "UV clock projection and time conversion",
            ],
            "must_not_be_claimed_from_current_evidence": [
                "first-principles cross-domain unification",
                "physical scalar-spectrum prediction from the frozen trace",
                "out-of-sample SPARC success",
                "laboratory detection or validation",
            ],
        },
    }


def build_final_payload(
    stage1: dict[str, Any], stage2: dict[str, Any], stage3: dict[str, Any]
) -> dict[str, Any]:
    return {
        "protocol": "three_stage_blind_then_compare_then_independent_adjudication",
        "preregistration": "first_principles_audit/PREREGISTRATION.md",
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=("derive", "compare", "adjudicate", "all"),
        default="all",
    )
    parser.add_argument(
        "--instrument-root",
        type=Path,
        default=DEFAULT_INSTRUMENT_ROOT,
        help="Sibling HOLO_TRANSDUCTOR_instrument checkout",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stage1_path = ARTIFACT_ROOT / "stage1_sealed_derivation.json"
    stage2_path = ARTIFACT_ROOT / "stage2_comparison.json"
    stage3_path = ARTIFACT_ROOT / "stage3_adjudication.json"

    if args.stage in ("derive", "all"):
        stage1 = symbolic_stage1()
        write_json(stage1_path, stage1)
        print(f"[stage 1] sealed: {stage1_path} sha256={sha256_file(stage1_path)}")
    else:
        stage1 = load_json(stage1_path)

    if args.stage in ("compare", "all"):
        if not stage1["all_symbolic_checks_pass"]:
            raise RuntimeError("Stage 1 derivation did not pass its symbolic checks")
        stage2 = stage2_compare(args.instrument_root.resolve())
        write_json(stage2_path, stage2)
        print(f"[stage 2] compared: {stage2_path} sha256={sha256_file(stage2_path)}")
    elif args.stage in ("adjudicate",):
        stage2 = load_json(stage2_path)
    else:
        return 0

    if args.stage in ("adjudicate", "all"):
        stage3 = stage3_adjudicate(stage1, stage2)
        write_json(stage3_path, stage3)
        final = build_final_payload(stage1, stage2, stage3)
        final_path = ARTIFACT_ROOT / "ed_audit.json"
        write_json(final_path, final)
        print(f"[stage 3] adjudicated: {stage3_path} sha256={sha256_file(stage3_path)}")
        print(f"[final] {final_path} sha256={sha256_file(final_path)}")
        failed = [
            name
            for name, item in stage3["claim_matrix"].items()
            if not item["pass"]
        ]
        print(f"[final] claims not established: {len(failed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
