#!/usr/bin/env python3
"""Adjudicate competing nonlinear derivation routes with hard physics gates.

The score board is deliberately subordinate to the gates.  It rewards
reproducible intermediate evidence, while a compact S3/S4 claim remains
impossible until the same physical coefficient survives independent ADM and
gauge-invariant reductions, including finite boundaries.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "nonlinear_swarm_adjudication.json"
INPUTS = {
    "gauge_invariant_route": HERE / "artifacts" / "gauge_invariant_cubic_route.json",
    "adm_quartic_seed": HERE / "artifacts" / "radial_adm_quartic_seed.json",
    "adm_quadratic_recovery": HERE / "artifacts" / "adm_quadratic_recovery.json",
    "compact_boundaries": HERE / "artifacts" / "cubic_boundary_identifiability.json",
    "cubic_inventory": HERE / "artifacts" / "bulk_cubic_vertex_inventory.json",
}

WEIGHTS = {
    "S2_canonical": 20,
    "gauge_constraints": 15,
    "finite_boundaries": 15,
    "physical_c000": 20,
    "direct_S4": 10,
    "resources": 5,
    "blinding": 5,
    "independent_cross_route": 10,
}


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


def _scored_route(
    route_id: str,
    ceiling: int,
    points: Mapping[str, int],
    evidence: Mapping[str, list[str]],
) -> dict[str, Any]:
    if set(points) != set(WEIGHTS) or set(evidence) != set(WEIGHTS):
        raise ValueError("every route must address every reward category")
    if any(points[key] < 0 or points[key] > WEIGHTS[key] for key in WEIGHTS):
        raise ValueError("reward points must lie within their category weights")
    score = sum(points.values())
    if score > ceiling:
        raise ValueError("current score cannot exceed route ceiling")
    return {
        "id": route_id,
        "theoretical_ceiling": ceiling,
        "current_points": dict(points),
        "current_score": score,
        "evidence": dict(evidence),
        "warning": "score is a workflow reward, not a probability or a physics claim",
    }


def _has_empty_observational_inputs(payload: Mapping[str, Any]) -> bool:
    inputs = payload.get("inputs", {})
    if "observational_tables_read" in inputs:
        return inputs["observational_tables_read"] == []
    if "observational_inputs_read" in payload:
        return payload["observational_inputs_read"] == []
    return False


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    gauge = payloads["gauge_invariant_route"]
    adm = payloads["adm_quartic_seed"]
    quadratic = payloads["adm_quadratic_recovery"]
    boundary = payloads["compact_boundaries"]
    inventory = payloads["cubic_inventory"]
    if gauge.get("checks", {}).get("all") is not True:
        raise RuntimeError("gauge-invariant route is not certified")
    if adm.get("checks", {}).get("all") is not True:
        raise RuntimeError("ADM quartic seed is not certified")
    if quadratic.get("checks", {}).get("all") is not True:
        raise RuntimeError("ADM quadratic recovery is not certified")
    if boundary.get("checks", {}).get("all") is not True:
        raise RuntimeError("compact-boundary audit is not certified")
    if inventory.get("checks", {}).get("all") is not True:
        raise RuntimeError("cubic inventory is not certified")

    gauge_gates = gauge["physical_gates"]
    adm_gates = adm["physical_gates"]
    quadratic_gates = quadratic["physical_gates"]
    boundary_gates = boundary["physical_gates"]
    empty_observation_inputs = all(
        _has_empty_observational_inputs(payload) for payload in payloads.values()
    )

    bmp_points = {
        "S2_canonical": 12 if gauge_gates["same_local_S2_operator_identified"] else 0,
        "gauge_constraints": 8 if gauge_gates["bmp_linear_comoving_identity_identified"] else 0,
        "finite_boundaries": 0,
        "physical_c000": 0,
        "direct_S4": 0,
        "resources": 3,
        "blinding": 3 if empty_observation_inputs else 0,
        "independent_cross_route": 0,
    }
    adm_points = {
        "S2_canonical": (
            16
            if quadratic_gates[
                "same_variable_bulk_ADM_S2_action_recovered_on_compact_support"
            ]
            else 0
        ),
        "gauge_constraints": 5 if adm_gates["exact_bulk_ADM_scalar_density_identified"] else 0,
        "finite_boundaries": (
            4
            if boundary_gates[
                "formal_fixed_brane_GHY_prefactor_and_potential_jet_convolution_verified"
            ]
            else 0
        ),
        "physical_c000": 0,
        "direct_S4": 0,
        "resources": 3 if adm["bounded_execution_contract"]["cas_peak_rss_mib_max"] <= 512 else 0,
        "blinding": 3 if empty_observation_inputs else 0,
        "independent_cross_route": 0,
    }
    hybrid_points = {
        "S2_canonical": max(
            bmp_points["S2_canonical"], adm_points["S2_canonical"]
        ),
        "gauge_constraints": max(
            bmp_points["gauge_constraints"], adm_points["gauge_constraints"]
        ),
        "finite_boundaries": adm_points["finite_boundaries"],
        "physical_c000": 0,
        "direct_S4": 0,
        "resources": adm_points["resources"],
        "blinding": adm_points["blinding"],
        "independent_cross_route": 0,
    }
    shared_empty = {key: [] for key in WEIGHTS}
    routes = [
        _scored_route(
            "BMP_only",
            80,
            bmp_points,
            {
                **shared_empty,
                "S2_canonical": [
                    "exact local S2 operator and weight map",
                    "seven mapped bulk profiles",
                    "absolute trace normalization remains open",
                ],
                "gauge_constraints": [
                    "linear gauge-invariant active-scalar equation",
                    "no compact nonlinear constraint reduction",
                ],
                "resources": ["vectorized one-dimensional profile checks"],
                "blinding": ["empty observational input list, not syscall-sealed"],
            },
        ),
        _scored_route(
            "ADM_only",
            90,
            adm_points,
            {
                **shared_empty,
                "S2_canonical": [
                    "same-variable ADM action reproduces p,w and normalization",
                    "nine compact periodic probes agree below 1e-9",
                    "absolute matter residue remains open",
                ],
                "gauge_constraints": [
                    "exact Hamiltonian and momentum constraints identified",
                    "lapse/shift not yet solved and substituted",
                ],
                "finite_boundaries": [
                    "formal fixed-brane GHY prefactor and lambda jets through S4",
                    "bending and full junction system not yet combined",
                ],
                "resources": ["degree-four jets; dense N_mode^4 tensor forbidden"],
                "blinding": ["empty observational input list, not syscall-sealed"],
            },
        ),
        _scored_route(
            "hybrid_ADM_plus_BMP_oracle",
            100,
            hybrid_points,
            {
                **shared_empty,
                "S2_canonical": [
                    "ADM action and independent BMP operator now agree at S2"
                ],
                "gauge_constraints": ["best current linear invariant evidence"],
                "finite_boundaries": ["inherits the independent fixed-brane expansion"],
                "resources": ["bounded ADM jet architecture"],
                "blinding": ["empty observational input list, not syscall-sealed"],
                "independent_cross_route": [
                    "earns zero until kernels and endpoint code remain independent"
                ],
            },
        ),
    ]
    winner = max(routes, key=lambda row: row["current_score"])

    hard_gates = {
        "bulk_ADM_S2_compact_support_recovered": quadratic_gates[
            "same_variable_bulk_ADM_S2_action_recovered_on_compact_support"
        ],
        "lapse_shift_solved_through_required_order": bool(
            adm_gates["lapse_solution_substituted_through_second_order"]
            and adm_gates["shift_constraint_solved_through_second_order"]
        ),
        "finite_boundaries_and_bending_combined": bool(
            adm_gates["finite_endpoint_GHY_brane_bending_combined"]
            and boundary_gates["full_second_order_junction_source_derived"]
        ),
        "physical_c000_computed": bool(
            gauge_gates["physical_compact_modal_couplings_computed"]
            and adm_gates["compact_physical_S3_coefficients_projected"]
        ),
        "direct_S4_contact_computed": adm_gates[
            "direct_physical_S4_contact_projected"
        ],
        "two_independent_routes_agree": adm_gates["second_gauge_reduction_agrees"],
        "sealed_observation_blind_execution": False,
    }

    checks = {
        "certified_inputs": True,
        "no_observational_tables_read": empty_observation_inputs,
        "all_reward_categories_are_bounded": all(
            all(0 <= row["current_points"][key] <= WEIGHTS[key] for key in WEIGHTS)
            for row in routes
        ),
        "hybrid_route_wins_current_reward": winner["id"] == "hybrid_ADM_plus_BMP_oracle",
        "scores_do_not_open_physical_claim_gates": not any(
            hard_gates[key]
            for key in (
                "lapse_shift_solved_through_required_order",
                "finite_boundaries_and_bending_combined",
                "physical_c000_computed",
                "direct_S4_contact_computed",
                "two_independent_routes_agree",
                "sealed_observation_blind_execution",
            )
        ),
        "compact_claim_remains_fail_closed": True,
    }
    checks["all"] = all(checks.values())

    return {
        "schema": "holo.nonlinear-swarm-adjudication.v1",
        "title": "Cooperative adversarial race for compact S3 and S4",
        "classification": (
            "hybrid_route_selected_for_next_derivation;no_physical_cubic_or_force_claim"
        ),
        "reward_policy": {
            "weights": WEIGHTS,
            "rule": (
                "Award intermediate points only for an artifact, tests, input hashes "
                "and a numerical or algebraic residual. Scores never override gates."
            ),
            "penalties": {
                "uses_observational_target_during_derivation": "disqualify",
                "crosses_hard_RSS_cap": "disqualify that implementation",
                "calls_a_kernel_a_physical_action": "zero physical-coupling points",
                "shared_omission_between_routes": "zero independent-cross-route points",
            },
        },
        "routes": routes,
        "selection": {
            "winner": winner["id"],
            "current_score": winner["current_score"],
            "reason": (
                "ADM supplies the physical compact action and direct S4; BMP supplies "
                "an independently derived bulk EOM/correlator oracle. Neither alone "
                "currently computes a physical c000."
            ),
            "immediate_objective": (
                "With the ADM S2 backward test passed, solve the second-order "
                "constraint closure and compare the first cubic source with BMP."
            ),
        },
        "historical_analogies_as_tests": [
            {
                "idea": "Einstein covariance",
                "translation": "the same canonically normalized c000 in two gauges",
                "falsifier": "relative disagreement above 1 percent",
            },
            {
                "idea": "Ricci and Gauss-Codazzi geometry",
                "translation": "ADM Hamiltonian, momentum and junction residuals",
                "falsifier": "any normalized constraint residual above 1e-8",
            },
            {
                "idea": "Noether and Bianchi identities",
                "translation": "pure-gauge directions and endpoint terms cancel",
                "falsifier": "pure-gauge overlap above 1e-7",
            },
            {
                "idea": "Feynman action vertices",
                "translation": "S3 and S4 are derivatives of one frozen action",
                "falsifier": "Bose-permutation relative error above 1e-8",
            },
            {
                "idea": "Wilson mode elimination",
                "translation": "Schur-complement exchange on nested 3/5/7 modes",
                "falsifier": "5-to-7 exchange tail above 5 percent",
            },
        ],
        "decisive_assay": {
            "primary_observable": "canonically normalized c000 at finite gamma",
            "nonzero_control": "c011",
            "phase_alignment": (
                "choose signs so the weighted BMP-ADM modal overlap is positive; "
                "also report phase-invariant c^2/m^2"
            ),
            "eta_hat_steps": [0.001, 0.0005],
            "eta_scan": (
                "vary UV and IR cubic boundary jets independently with plus/minus "
                "steps while holding the background and S2 fixed"
            ),
            "independence": (
                "routes may share frozen backgrounds and modes, but not cubic kernels, "
                "constraint solvers or endpoint-expression code"
            ),
            "collaboration_after_blind_compare": (
                "unseal residuals, classify disagreement, share corrections, then rerun "
                "both routes from a fresh frozen manifest"
            ),
        },
        "numeric_contract": {
            "S2_action_norm_relative_max": 1.0e-8,
            "S2_eigenvalue_relative_max": 1.0e-10,
            "mode_MAC_min": 0.999,
            "constraint_residual_max": 1.0e-8,
            "pure_gauge_overlap_fraction_max": 1.0e-7,
            "integration_by_parts_relative_max": 1.0e-5,
            "bose_permutation_relative_max": 1.0e-8,
            "continuum_c000_uncertainty_relative_max": 0.0025,
            "cross_gauge_c000_relative_max": 0.01,
            "eta_slope_cross_gauge_relative_max": 0.01,
            "eta_slope_step_stability_relative_max": 0.005,
            "peak_arrays_mib_max": 8,
            "peak_rss_soft_mib": 128,
            "peak_rss_hard_mib": 256,
        },
        "hard_gates": hard_gates,
        "claim_gates": {
            "compact_S3": [
                "bulk_ADM_S2_compact_support_recovered",
                "lapse_shift_solved_through_required_order",
                "finite_boundaries_and_bending_combined",
                "physical_c000_computed",
                "sealed_observation_blind_execution",
            ],
            "total_Y2": ["compact_S3", "direct_S4_contact_computed"],
            "independently_crosschecked": ["total_Y2", "two_independent_routes_agree"],
            "new_force_or_observation": "never authorized by this theory-only artifact",
        },
        "checks": checks,
        "inputs": {
            "observational_tables_read": [],
            "files": {
                name: {
                    "path": str(path.relative_to(REPO)),
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
        },
        "evidence_boundary": (
            "This makes the agents cooperate through a shared falsifiable assay and "
            "selects the best next route. It is not evidence for a physical cubic "
            "coupling, a force law or an observation."
        ),
        "runtime": {"python": platform.python_version()},
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        raise SystemExit("nonlinear swarm adjudication failed")
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(
        f"[winner] {result['selection']['winner']} "
        f"score={result['selection']['current_score']}/100"
    )
    print(f"[physical c000] {result['hard_gates']['physical_c000_computed']}")
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
