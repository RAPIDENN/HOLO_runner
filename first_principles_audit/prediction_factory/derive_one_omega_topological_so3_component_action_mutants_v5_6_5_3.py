#!/usr/bin/env python3
"""Exact additive omit/sign mutants on raw Q5 endpoint action values."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
A_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_literal_torch_action_route_a_v5_6_5_certificate.json"
B_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.json"
COMPARATOR = ARTIFACTS / "one_omega_topological_so3_action_ad_fd5_comparator_v5_6_5_1_gate.json"
TEST = HERE / "test_one_omega_topological_so3_component_action_mutants_v5_6_5_3.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_component_action_mutants_v5_6_5_3.json"

A_ARTIFACT_SHA256 = "ec56360b271cea3d32b41c5d3c19e7a7dc85de4425b4cd3ab4e5fe290f696e2e"
B_ARTIFACT_SHA256 = "7e1044cdc628052750f02f0ab4d134c89ee85f7296d3de027d998177578320db"
COMPARATOR_SHA256 = "26cef70ab86c666b33f62a6e6ce5375cb4da4669a25ca070cc3346493a660828"
SCHEMA = "holo.one-omega-topological-so3-component-action-mutants-v5-6-5-3.v1"
COARSE_STEP = 4.0e-2
FINE_STEP = 2.0e-2
COMPONENT_REL_TOLERANCE = 5.0e-5

ACTION_COMPONENTS = (
    "EH_bulk_plus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "GHY_minus",
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)


class ComponentMutantError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, expected: str, label: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected:
        raise ComponentMutantError(f"{label} byte pin drift: {observed}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_inputs() -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    return (
        _load(A_ARTIFACT, A_ARTIFACT_SHA256, "route A artifact"),
        _load(B_ARTIFACT, B_ARTIFACT_SHA256, "route B artifact"),
        _load(COMPARATOR, COMPARATOR_SHA256, "direct comparator artifact"),
    )


def _mutated_endpoint(
    nominal: Mapping[str, Any], target: str, operation: str
) -> dict[str, float]:
    if target not in ACTION_COMPONENTS:
        raise ComponentMutantError(f"unknown component mutant target: {target}")
    if operation not in {"omit", "invert_sign"}:
        raise ComponentMutantError(f"unknown component mutant operation: {operation}")
    result = {component: float(nominal[component]) for component in ACTION_COMPONENTS}
    result[target] = 0.0 if operation == "omit" else -result[target]
    result["S_total"] = math.fsum(result[component] for component in ACTION_COMPONENTS)
    return result


def _fd5(
    endpoints: Mapping[float, Mapping[str, float]], step: float
) -> dict[str, float]:
    return {
        component: math.fsum(
            (
                endpoints[-2.0 * step][component],
                -8.0 * endpoints[-step][component],
                8.0 * endpoints[step][component],
                -endpoints[2.0 * step][component],
            )
        )
        / (12.0 * step)
        for component in ACTION_COMPONENTS + ("S_total",)
    }


def run_mutant_campaign(
    route_a: Mapping[str, Any],
    route_b: Mapping[str, Any],
    comparator: Mapping[str, Any],
) -> Mapping[str, Any]:
    if comparator["decision"]["AD_vs_independent_FD5_comparator_pass"] is not True:
        raise ComponentMutantError("nominal comparator is not green")
    ad = {
        key: float(value)
        for key, value in route_a["scientific"]["AD_JVP_by_component"].items()
    }
    raw_endpoints = route_b["scientific"]["FD5_refinement_window"][
        "endpoint_records_by_float_hex"
    ]
    nominal_by_displacement = {
        float(record["displacement"]): record["S_rel_components"]
        for record in raw_endpoints.values()
    }
    needed = {
        multiplier * step
        for step in (COARSE_STEP, FINE_STEP)
        for multiplier in (-2.0, -1.0, 1.0, 2.0)
    }
    if not needed.issubset(nominal_by_displacement):
        raise ComponentMutantError("raw endpoint action values do not cover Richardson pair")
    records: list[dict[str, Any]] = []
    for operation in ("omit", "invert_sign"):
        for target in ACTION_COMPONENTS:
            endpoints = {
                displacement: _mutated_endpoint(nominal, target, operation)
                for displacement, nominal in nominal_by_displacement.items()
                if displacement in needed
            }
            coarse = _fd5(endpoints, COARSE_STEP)
            fine = _fd5(endpoints, FINE_STEP)
            richardson = {
                component: fine[component]
                + (fine[component] - coarse[component]) / 15.0
                for component in ACTION_COMPONENTS + ("S_total",)
            }
            residual = richardson[target] - ad[target]
            relative = abs(residual) / max(
                abs(richardson[target]), abs(ad[target]), 1.0e-300
            )
            records.append(
                {
                    "id": f"{operation}_{target}",
                    "operation": operation,
                    "target": target,
                    "mutated_Richardson_target_derivative": richardson[target],
                    "nominal_AD_target_derivative": ad[target],
                    "target_residual": residual,
                    "target_component_relative_residual": relative,
                    "mutated_Richardson_total_derivative": richardson["S_total"],
                    "killed": relative > COMPONENT_REL_TOLERANCE,
                }
            )
    return {
        "campaign_kind": "exact additive action mutation on independently evaluated raw endpoints",
        "endpoint_operation": "replace one literal action component at every raw endpoint, recompute S_total, FD5, and Richardson",
        "mutant_count": len(records),
        "records": records,
        "all_mutants_killed": len(records) == 40 and all(row["killed"] for row in records),
    }


def build_payload() -> dict[str, Any]:
    route_a, route_b, comparator = load_inputs()
    campaign = run_mutant_campaign(route_a, route_b, comparator)
    passed = campaign["all_mutants_killed"]
    return {
        "schema": SCHEMA,
        "classification": "theory_only;finite_N2;exact_additive_component_mutants;special_mutants_pending",
        "decision": {
            "all_twenty_component_omit_mutants_pass": passed,
            "all_twenty_component_sign_mutants_pass": passed,
            "exact_additive_40_mutant_campaign_pass": passed,
            "special_geometric_action_mutants_pass": False,
            "Euler_Green_independent_route_pass": False,
            "independent_clean_process_redteam_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "tolerance": {
            "target_component_relative_residual_kill_threshold": COMPONENT_REL_TOLERANCE
        },
        "scientific": campaign,
        "source_pins": {
            "route_A_artifact_sha256": A_ARTIFACT_SHA256,
            "route_B_artifact_sha256": B_ARTIFACT_SHA256,
            "nominal_comparator_artifact_sha256": COMPARATOR_SHA256,
        },
        "open_special_mutants": [
            "freeze_relative_R",
            "rotate_phi_only",
            "break_induced_pullback",
            "remove_T_ui_matter",
            "V4_anisotropic",
            "break_gluing",
            "impose_Z2",
            "circular_Eulerian_route",
        ],
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST) if TEST.exists() else None,
            },
        },
        "evidence_boundary": "The 40 exact additive omit/sign mutants are killed on raw Q5 endpoint actions. This does not execute non-additive geometric/configuration mutants, derive Euler-Green, or promote C1/N1.",
    }


def main() -> None:
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
