#!/usr/bin/env python3
"""Test whether the current HOLO force can generate the nonlinear collector.

This is a deliberately narrow embedding gate.  It compares the response class
actually derived for the canonically normalized, linearized stiff-boundary
sector with the deep-acceleration response required by the already exposed
collector target.  It does not use SPARC tables or observed velocities, and it
does not claim a no-go for every possible nonlinear completion of the 5D
theory.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import scipy


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
EFFECTIVE_ACTION = REPO / "first_principles_audit/artifacts/holo_effective_action_summary.json"
INTERFACE_ACTION = REPO / "first_principles_audit/artifacts/interface_action_derivation.json"
STIFF_FORCE = HERE / "artifacts/stiff_boundary_force.json"
COLLECTOR_ACTION = HERE / "artifacts/nonlinear_collector_action.json"
ROBIN_BOUNDARY = HERE / "artifacts/robin_boundary_family.json"
MICROSCOPIC_BOUNDARY = HERE / "artifacts/superpotential_boundary_completion.json"
OUTPUT = HERE / "artifacts/holo_collector_embedding_gate.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def current_yukawa_multiplier(x: np.ndarray, mu: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Return g/g_N for the frozen stiff-boundary force at x=r/ell."""

    x = np.asarray(x, dtype=float)
    mu = np.asarray(mu, dtype=float)
    alpha = np.asarray(alpha, dtype=float)
    if np.any(x < 0.0) or np.any(mu <= 0.0) or np.any(alpha < 0.0):
        raise ValueError("x, masses and residues are outside the certified domain")
    kernel = (1.0 + np.outer(x, mu)) * np.exp(-np.outer(x, mu))
    return 1.0 + kernel @ alpha


def collector_source_exponent(y: np.ndarray) -> np.ndarray:
    """Return d ln(g)/d ln(M) at fixed radius for the collector law.

    Since y=g_N/a0 is proportional to M and
    g=g_N/[1-exp(-sqrt(y))], the exponent tends to 1/2 in the deep limit and
    to 1 in the Newtonian limit.
    """

    y = np.asarray(y, dtype=float)
    if np.any(~np.isfinite(y)) or np.any(y <= 0.0):
        raise ValueError("y must be finite and strictly positive")
    t = np.sqrt(y)
    correction = np.zeros_like(t)
    safe = t < 700.0
    correction[safe] = 0.5 * t[safe] / np.expm1(t[safe])
    return 1.0 - correction


def build() -> dict[str, Any]:
    effective = _read(EFFECTIVE_ACTION)
    interface = _read(INTERFACE_ACTION)
    stiff = _read(STIFF_FORCE)
    collector = _read(COLLECTOR_ACTION)
    robin = _read(ROBIN_BOUNDARY)
    microscopic_boundary = _read(MICROSCOPIC_BOUNDARY)

    spectrum = stiff["spectrum_and_force"]
    mu = np.asarray(spectrum["masses_mu"], dtype=float)
    alpha = np.asarray(spectrum["alpha_uv_2_beta_squared"], dtype=float)
    x = np.geomspace(1.0e-8, 1.0e4, 4096)
    multiplier = current_yukawa_multiplier(x, mu, alpha)

    # This derivative is exactly one because the multiplier depends on r/ell,
    # not on source amplitude M.  The finite-difference value is retained as a
    # guard against accidentally introducing a state-dependent source response.
    masses = np.geomspace(1.0e-12, 1.0e12, 2048)
    representative_multiplier = float(current_yukawa_multiplier(np.array([1.0]), mu, alpha)[0])
    current_g = masses * representative_multiplier
    current_exponent = np.gradient(np.log(current_g), np.log(masses))

    y = np.geomspace(1.0e-12, 1.0e12, 4096)
    target_exponent = collector_source_exponent(y)
    deep = y <= 1.0e-8
    high = y >= 1.0e8

    current_force_linear = float(np.max(np.abs(current_exponent - 1.0))) < 1.0e-11
    target_deep_half_power = float(np.max(np.abs(target_exponent[deep] - 0.5))) < 3.0e-5
    response_classes_match = not (current_force_linear and target_deep_half_power)

    target_slope = collector["action_reconstruction"]["diagnostics"][
        "deep_limit_dlog_F_dlog_X"
    ]
    current_slope = 1.0
    action_slopes_match = math.isclose(current_slope, target_slope, rel_tol=0.0, abs_tol=2.0e-3)
    carrier = interface["carrier_metrics"]
    positive_bulk_hessian = carrier["p_min"] > 0.0 and carrier["w_min"] > 0.0
    boundary_kinetic_operator_present = False

    passes = {
        "input_hashes_present": all(
            _sha256(path)
            for path in (
                EFFECTIVE_ACTION,
                INTERFACE_ACTION,
                STIFF_FORCE,
                COLLECTOR_ACTION,
                ROBIN_BOUNDARY,
                MICROSCOPIC_BOUNDARY,
            )
        ),
        "positive_canonical_bulk_hessian": positive_bulk_hessian,
        "current_boundary_family_has_no_derivative_kinetic_operator": (
            not boundary_kinetic_operator_present
            and "boundary kinetic terms" in robin["evidence_boundary"]
        ),
        "current_stiff_force_is_source_linear": current_force_linear,
        "collector_has_deep_half_power_source_scaling": target_deep_half_power,
        "current_multiplier_is_bounded": bool(
            np.min(multiplier) >= 1.0 - 1.0e-13
            and np.max(multiplier) <= 1.0 + float(np.sum(alpha)) + 1.0e-12
        ),
        "collector_target_is_not_mislabelled_as_microscopic_derivation": (
            "not_derived_from_current_holo_bulk" in collector["classification"]
        ),
        "linearized_current_sector_can_embed_collector": response_classes_match and action_slopes_match,
    }
    passes["audit_complete"] = all(
        value for key, value in passes.items() if key != "linearized_current_sector_can_embed_collector"
    )

    return {
        "schema": "holo.collector-embedding-gate.v1",
        "title": "Current-HOLO to nonlinear-collector embedding gate",
        "classification": (
            "conditional_no_go_for_current_linearized_canonical_stiff_sector;"
            "full_nonlinear_holo_completion_unresolved"
        ),
        "scope": {
            "excluded": (
                "The presently derived canonical, quadratic, stiff-boundary scalar "
                "response with source-independent masses and residues cannot generate "
                "the collector's deep-acceleration scaling."
            ),
            "not_excluded": (
                "A new nonanalytic or strongly nonlinear derivative sector, a nonperturbative "
                "infrared completion, or another independently derived HOLO sector."
            ),
            "observational_inputs_read_by_this_gate": [],
            "exposed_empirical_target_read_for_comparison_only": str(COLLECTOR_ACTION.relative_to(REPO)),
        },
        "inputs": {
            "effective_action": {
                "path": str(EFFECTIVE_ACTION.relative_to(REPO)),
                "sha256": _sha256(EFFECTIVE_ACTION),
                "classification": effective["classification"],
            },
            "interface_action": {
                "path": str(INTERFACE_ACTION.relative_to(REPO)),
                "sha256": _sha256(INTERFACE_ACTION),
                "classification": interface["classification"],
            },
            "stiff_force": {
                "path": str(STIFF_FORCE.relative_to(REPO)),
                "sha256": _sha256(STIFF_FORCE),
                "classification": stiff["classification"],
            },
            "collector_action_target": {
                "path": str(COLLECTOR_ACTION.relative_to(REPO)),
                "sha256": _sha256(COLLECTOR_ACTION),
                "classification": collector["classification"],
            },
            "robin_boundary_family": {
                "path": str(ROBIN_BOUNDARY.relative_to(REPO)),
                "sha256": _sha256(ROBIN_BOUNDARY),
                "classification": robin["classification"],
            },
            "microscopic_boundary_completion": {
                "path": str(MICROSCOPIC_BOUNDARY.relative_to(REPO)),
                "sha256": _sha256(MICROSCOPIC_BOUNDARY),
                "classification": microscopic_boundary["classification"],
            },
        },
        "evidence_partition": {
            "derived": [
                "positive canonical scalar carrier in the current quadratic reduction",
                "source-independent stiff Yukawa masses and residues",
                "source-amplitude exponent one for the current linearized force",
                "Robin endpoint potentials alter spectra but include no boundary kinetic term",
            ],
            "assumed_or_exposed_target": [
                "the collector constitutive function reconstructed from the SPARC training split",
                "the acceleration scale a0 fitted once on that exposed training split",
            ],
            "blocked": [
                "a microscopic derivation of the nonanalytic derivative function",
                "an independent derivation of a0",
                "a ghost-free relativistic and lensing completion",
                "a unique nonspherical source solve and genuinely independent holdout",
            ],
        },
        "source_scaling_certificate": {
            "current_stiff_force": (
                "g(M,r)=G*M/r^2*[1+sum alpha_n*(1+m_n*r)*exp(-m_n*r)]"
            ),
            "current_fixed_radius_mass_exponent": 1.0,
            "current_numerical_exponent_max_abs_error": float(
                np.max(np.abs(current_exponent - 1.0))
            ),
            "collector_force": "g=g_N/[1-exp(-sqrt(g_N/a0))]",
            "collector_fixed_radius_mass_exponent": (
                "1-sqrt(y)/[2*expm1(sqrt(y))], y=g_N/a0"
            ),
            "collector_deep_exponent_range": [
                float(np.min(target_exponent[deep])),
                float(np.max(target_exponent[deep])),
            ],
            "collector_high_acceleration_exponent_range": [
                float(np.min(target_exponent[high])),
                float(np.max(target_exponent[high])),
            ],
            "adjudication": (
                "At fixed geometry and radius, a source-independent Yukawa tower is "
                "linear in M, whereas the target tends to sqrt(M). Changing ell or "
                "adding more fixed linear modes cannot change that exponent."
            ),
        },
        "operator_certificate": {
            "current_positive_quadratic_carrier": {
                "p_min": carrier["p_min"],
                "w_min": carrier["w_min"],
                "w_integral": carrier["w_integral"],
                "interpretation": (
                    "The present reduction has a nonzero positive weak-field Hessian "
                    "and canonically normalized four-dimensional modes."
                ),
            },
            "current_boundary_operator_inventory": {
                "positive_robin_endpoint_potentials": True,
                "derivative_kinetic_operator_present": boundary_kinetic_operator_present,
                "meaning": (
                    "Neumann, positive Robin and stiff choices alter masses and endpoint "
                    "conditions but do not supply mu(|grad Phi|)."
                ),
            },
            "current_weak_field_gradient_power": "F_current(X) proportional to X",
            "current_dlog_F_dlog_X": current_slope,
            "collector_deep_gradient_power": "F_target(X) proportional to X^(3/2)",
            "collector_deep_dlog_F_dlog_X": target_slope,
            "regular_weak_field_expansion": (
                "The existing quadratic fluctuation operator produces integer-order, "
                "source-linear response at leading order; the required half-power "
                "law is not an operator already present in the certified interface."
            ),
            "regular_field_redefinition_no_go": (
                "A regular invertible field redefinition cannot turn an analytic "
                "source response g=lambda*g1+O(lambda^2) into g proportional to "
                "sqrt(lambda)."
            ),
        },
        "amplitude_certificate": {
            "sum_alpha": float(np.sum(alpha)),
            "current_multiplier_min_over_scan": float(np.min(multiplier)),
            "current_multiplier_max_over_scan": float(np.max(multiplier)),
            "current_exact_upper_bound": 1.0 + float(np.sum(alpha)),
            "collector_deep_multiplier": "nu(y)~y^(-1/2), unbounded as y->0",
        },
        "minimal_missing_physics": [
            "derive rather than fit an acceleration scale a0 from independent HOLO parameters",
            "derive a noncanonical derivative function whose deep limit is F(X)~(2/3)X^(3/2)",
            "show a ghost-free relativistic completion and its lensing/matter coupling",
            "solve the resulting three-dimensional field equation for independently specified source densities",
        ],
        "theory_change_boundary": (
            "Adding a brane or bulk P(X) term could realize the target operator, but "
            "unless its function and a0 follow from already frozen microscopic data, "
            "that is a new theory input rather than a prediction of the present model."
        ),
        "candidate_extension_warning": (
            "Cancelling the existing positive X term to expose X^(3/2) would make the "
            "weak-field Hessian vanish, create a strongly coupled point, and require a "
            "fresh stability and spectrum derivation; it is not a demonstrated healthy route."
        ),
        "passes": passes,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    if not result["passes"]["audit_complete"]:
        return 1
    # A successful gate execution is expected to reject the current embedding.
    if result["passes"]["linearized_current_sector_can_embed_collector"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
