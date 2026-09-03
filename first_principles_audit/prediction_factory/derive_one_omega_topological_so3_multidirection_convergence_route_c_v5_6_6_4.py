#!/usr/bin/env python3
"""Multi-direction and convergence campaign for independent Route C.

This additive receipt consumes the byte-pinned v5.6.6.3 Route-C lemma and its
primitive bundle.  It re-runs the three remaining primitive directions and
performs separate free-step, coordinate-step, radial-quadrature, and
tangential-quadrature refinements.  It never imports either action route A/B
or reads their values, tolerances, decisions, or helpers.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3
    as route_c,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
ROUTE_C_SOURCE = HERE / (
    "derive_one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3.py"
)
ROUTE_C_TEST = HERE / (
    "test_one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3.py"
)
ROUTE_C_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3.json"
)
TEST = HERE / (
    "test_one_omega_topological_so3_multidirection_convergence_"
    "route_c_v5_6_6_4.py"
)
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_multidirection_convergence_"
    "route_c_v5_6_6_4.json"
)

ROUTE_C_SOURCE_SHA256 = "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"
ROUTE_C_TEST_SHA256 = "00d3ce43fda74dca2215e2094aa2e5a68735c4fb7d56101a814620a8fc3e3ea7"
ROUTE_C_ARTIFACT_SHA256 = "4e343402192d539d7b5b8bf3e70dbbac139a779fea15273ce223143b0452bfd7"
SCHEMA = (
    "holo.one-omega-topological-so3-multidirection-convergence-"
    "route-c-v5-6-6-4.v1"
)

CURVE_NAMES = (
    "compact_bulk_SO3_horizontal_candidate",
    "embedding_motion_SO3_horizontal_candidate",
    "free_B_SO3_horizontal_candidate",
    "joint_all_primitive_classes_control_candidate",
)
RADIAL_ORDERS = (8, 10, 12)
TANGENTIAL_ORDERS = (3, 5, 7)
FREE_STEPS = (4.0e-3, 2.0e-3, 1.0e-3)
COORDINATE_STEPS = (4.0e-3, 5.0e-3, 6.0e-3)

# Reuse the already-frozen numerical standards of the C2 campaigns, not their
# runtime values.  Route C fixes its own coordinate/free-step envelope below.
RADIAL_ATOL = 5.0e-3
RADIAL_RTOL = 5.0e-7
TANGENTIAL_ATOL = 5.0e-8
TANGENTIAL_RTOL = 5.0e-10
FREE_STEP_ATOL = 2.0e-4
FREE_STEP_RTOL = 2.0e-8
COORDINATE_STEP_ATOL = 8.0e-5
COORDINATE_STEP_RTOL = 2.0e-8
PERIODIC_PRIMITIVE_TOLERANCE = 2.0e-11


class RouteCConvergenceError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_pinned_route_c() -> Mapping[str, Any]:
    observed = {
        "source": _sha256(ROUTE_C_SOURCE),
        "test": _sha256(ROUTE_C_TEST),
        "artifact": _sha256(ROUTE_C_ARTIFACT),
    }
    expected = {
        "source": ROUTE_C_SOURCE_SHA256,
        "test": ROUTE_C_TEST_SHA256,
        "artifact": ROUTE_C_ARTIFACT_SHA256,
    }
    if observed != expected:
        raise RouteCConvergenceError(f"Route-C v5.6.6.3 lineage drift: {observed}")
    payload = json.loads(ROUTE_C_ARTIFACT.read_text(encoding="utf-8"))
    if payload.get("schema") != route_c.SCHEMA:
        raise RouteCConvergenceError("Route-C v5.6.6.3 schema drift")
    if payload["decision"]["route_C_multin_independent_Euler_Green_pass"] is not True:
        raise RouteCConvergenceError("Route-C v5.6.6.3 is not green")
    return payload


def _component_comparison(
    left: Mapping[str, float],
    right: Mapping[str, float],
    *,
    atol: float,
    rtol: float,
) -> Mapping[str, Any]:
    if set(left) != set(right):
        raise RouteCConvergenceError("component key drift in refinement")
    rows: dict[str, Any] = {}
    all_pass = True
    for name in sorted(left):
        difference = abs(float(left[name]) - float(right[name]))
        scale = max(abs(float(left[name])), abs(float(right[name])))
        tolerance = atol + rtol * scale
        passed = difference <= tolerance
        rows[name] = {
            "left": float(left[name]),
            "right": float(right[name]),
            "absolute_difference": difference,
            "normalized_difference": difference / max(1.0, scale),
            "fixed_tolerance": tolerance,
            "pass": passed,
        }
        all_pass = all_pass and passed
    return {
        "absolute_tolerance": atol,
        "relative_tolerance": rtol,
        "rows": rows,
        "maximum_difference_over_tolerance": max(
            row["absolute_difference"] / row["fixed_tolerance"]
            for row in rows.values()
        ),
        "pass": all_pass,
    }


def _observed_dyadic_orders(
    coarse: Mapping[str, float],
    middle: Mapping[str, float],
    fine: Mapping[str, float],
) -> Mapping[str, Any]:
    result: dict[str, Any] = {}
    for name in sorted(coarse):
        coarse_gap = abs(float(coarse[name]) - float(middle[name]))
        fine_gap = abs(float(middle[name]) - float(fine[name]))
        order = None
        if coarse_gap > 0.0 and fine_gap > 0.0:
            order = math.log(coarse_gap / fine_gap, 2.0)
        result[name] = {
            "coarse_gap": coarse_gap,
            "fine_gap": fine_gap,
            "observed_order": order,
        }
    return result


def _with_coordinate_step(
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    curve_name: str,
    coordinate_step: float,
) -> Mapping[str, Any]:
    original_theta = route_c.COORD_THETA_STEP
    original_rho = route_c.COORD_RHO_STEP
    try:
        route_c.COORD_THETA_STEP = coordinate_step
        route_c.COORD_RHO_STEP = coordinate_step
        return route_c.evaluate_direct_member(
            bundle,
            member,
            curve_name=curve_name,
            tangential_order=route_c.PRIMARY_TANGENTIAL_ORDER,
            radial_order=route_c.PRIMARY_RADIAL_ORDER,
            free_step=route_c.FREE_JVP_STEP,
        )
    finally:
        route_c.COORD_THETA_STEP = original_theta
        route_c.COORD_RHO_STEP = original_rho


def _periodic_face_audit(
    bundle: Mapping[str, Any], member: Mapping[str, Any]
) -> Mapping[str, Any]:
    N = int(member["N"])
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    free = route_c._decode_f64(member["authoritative_free_central_f64le"])
    maximum = 0.0
    raw_rows: dict[str, Any] = {}
    for side in route_c.SIDES:
        side_rows = []
        for rho in (0.0, 0.5, 1.0):
            left_actual, left_reference = route_c._pullback_vector(
                free, contract, side, 0.0, rho
            )
            right_actual, right_reference = route_c._pullback_vector(
                free, contract, side, 2.0 * math.pi, rho
            )
            actual_residual = float(np.max(np.abs(left_actual - right_actual)))
            reference_residual = float(
                np.max(np.abs(left_reference - right_reference))
            )
            maximum = max(maximum, actual_residual, reference_residual)
            side_rows.append(
                {
                    "rho": rho,
                    "actual_primitive_Linf": actual_residual,
                    "reference_pullback_Linf": reference_residual,
                }
            )
        raw_rows[side] = side_rows
    face_pairs = {
        "x0_minus_plus": {
            "periodic_primitive_Linf": maximum,
            "current_pair_cancels_by_local_functional_periodicity": maximum
            <= PERIODIC_PRIMITIVE_TOLERANCE,
        },
        "x1_minus_plus": {
            "periodic_primitive_Linf": maximum,
            "current_pair_cancels_by_local_functional_periodicity": maximum
            <= PERIODIC_PRIMITIVE_TOLERANCE,
        },
        "x2_minus_plus": {
            "periodic_primitive_Linf": 0.0,
            "current_pair_cancels_by_absent_wavevector_component": True,
        },
        "x3_minus_plus": {
            "periodic_primitive_Linf": 0.0,
            "current_pair_cancels_by_absent_wavevector_component": True,
        },
    }
    return {
        "raw_endpoint_rows": raw_rows,
        "eight_oriented_faces_grouped_as_four_pairs": face_pairs,
        "maximum_periodic_primitive_Linf": maximum,
        "pass": maximum <= PERIODIC_PRIMITIVE_TOLERANCE,
    }


def _member_campaign(
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    frozen_joint: Mapping[str, Any],
) -> Mapping[str, Any]:
    N = int(member["N"])
    directions: dict[str, Any] = {
        "joint_all_primitive_classes_control_candidate": frozen_joint
    }
    for curve_name in CURVE_NAMES[:-1]:
        directions[curve_name] = route_c.evaluate_member(
            bundle,
            member,
            curve_name=curve_name,
            tangential_order=route_c.PRIMARY_TANGENTIAL_ORDER,
            radial_order=route_c.PRIMARY_RADIAL_ORDER,
        )

    joint_name = CURVE_NAMES[-1]
    primary = frozen_joint["direct_local_free_JVP_by_component"]
    radial_records: dict[str, Any] = {str(route_c.PRIMARY_RADIAL_ORDER): primary}
    for radial_order in RADIAL_ORDERS:
        if radial_order == route_c.PRIMARY_RADIAL_ORDER:
            continue
        row = route_c.evaluate_direct_member(
            bundle,
            member,
            curve_name=joint_name,
            tangential_order=route_c.PRIMARY_TANGENTIAL_ORDER,
            radial_order=radial_order,
        )
        radial_records[str(radial_order)] = row["direct_local_free_JVP_by_component"]

    tangential_records: dict[str, Any] = {
        str(route_c.PRIMARY_TANGENTIAL_ORDER): primary
    }
    for tangential_order in TANGENTIAL_ORDERS:
        if tangential_order == route_c.PRIMARY_TANGENTIAL_ORDER:
            continue
        row = route_c.evaluate_direct_member(
            bundle,
            member,
            curve_name=joint_name,
            tangential_order=tangential_order,
            radial_order=route_c.PRIMARY_RADIAL_ORDER,
        )
        tangential_records[str(tangential_order)] = row[
            "direct_local_free_JVP_by_component"
        ]

    free_step_records: dict[str, Any] = {str(route_c.FREE_JVP_STEP): primary}
    for free_step in FREE_STEPS:
        if free_step == route_c.FREE_JVP_STEP:
            continue
        row = route_c.evaluate_direct_member(
            bundle,
            member,
            curve_name=joint_name,
            tangential_order=route_c.PRIMARY_TANGENTIAL_ORDER,
            radial_order=route_c.PRIMARY_RADIAL_ORDER,
            free_step=free_step,
        )
        free_step_records[str(free_step)] = row["direct_local_free_JVP_by_component"]

    coordinate_records: dict[str, Any] = {
        str(route_c.COORD_THETA_STEP): primary
    }
    for coordinate_step in COORDINATE_STEPS:
        if coordinate_step == route_c.COORD_THETA_STEP:
            continue
        row = _with_coordinate_step(bundle, member, joint_name, coordinate_step)
        coordinate_records[str(coordinate_step)] = row[
            "direct_local_free_JVP_by_component"
        ]

    radial_comparison = _component_comparison(
        radial_records["10"],
        radial_records["12"],
        atol=RADIAL_ATOL,
        rtol=RADIAL_RTOL,
    )
    tangential_comparison = _component_comparison(
        tangential_records["5"],
        tangential_records["7"],
        atol=TANGENTIAL_ATOL,
        rtol=TANGENTIAL_RTOL,
    )
    free_step_comparison = _component_comparison(
        free_step_records[str(2.0e-3)],
        free_step_records[str(1.0e-3)],
        atol=FREE_STEP_ATOL,
        rtol=FREE_STEP_RTOL,
    )
    coordinate_comparison = _component_comparison(
        coordinate_records[str(5.0e-3)],
        coordinate_records[str(4.0e-3)],
        atol=COORDINATE_STEP_ATOL,
        rtol=COORDINATE_STEP_RTOL,
    )
    face_audit = _periodic_face_audit(bundle, member)
    directions_pass = all(
        bool(row["selected_member_Euler_Green_pass"])
        for row in directions.values()
    )
    convergence_pass = all(
        bool(item["pass"])
        for item in (
            radial_comparison,
            tangential_comparison,
            free_step_comparison,
            coordinate_comparison,
        )
    ) and bool(face_audit["pass"])
    return {
        "N": N,
        "K": int(member["K"]),
        "member_id": member["member_id"],
        "directions": directions,
        "all_four_directions_Euler_Green_pass": directions_pass,
        "refinement": {
            "radial": {
                "records_by_order": radial_records,
                "Q10_vs_Q12": radial_comparison,
                "successive_raw_difference_norms": {
                    "Q8_to_Q10_L2": float(
                        np.linalg.norm(
                            np.asarray(list(radial_records["8"].values()))
                            - np.asarray(list(radial_records["10"].values()))
                        )
                    ),
                    "Q10_to_Q12_L2": float(
                        np.linalg.norm(
                            np.asarray(list(radial_records["10"].values()))
                            - np.asarray(list(radial_records["12"].values()))
                        )
                    ),
                },
            },
            "tangential": {
                "records_by_order": tangential_records,
                "Q5_vs_Q7": tangential_comparison,
                "successive_raw_difference_norms": {
                    "Q3_to_Q5_L2": float(
                        np.linalg.norm(
                            np.asarray(list(tangential_records["3"].values()))
                            - np.asarray(list(tangential_records["5"].values()))
                        )
                    ),
                    "Q5_to_Q7_L2": float(
                        np.linalg.norm(
                            np.asarray(list(tangential_records["5"].values()))
                            - np.asarray(list(tangential_records["7"].values()))
                        )
                    ),
                },
            },
            "free_step": {
                "records_by_step": free_step_records,
                "h0p002_vs_h0p001": free_step_comparison,
                "observed_dyadic_orders": _observed_dyadic_orders(
                    free_step_records[str(4.0e-3)],
                    free_step_records[str(2.0e-3)],
                    free_step_records[str(1.0e-3)],
                ),
            },
            "coordinate_step": {
                "records_by_step": coordinate_records,
                "h0p005_vs_h0p004": coordinate_comparison,
                "envelope_Linf": max(
                    max(
                        abs(float(coordinate_records[str(step)][name]) - float(primary[name]))
                        for name in primary
                    )
                    for step in COORDINATE_STEPS
                ),
            },
            "N_and_K": {
                "N": N,
                "K_of_N": int(member["K"]),
                "basis_labels": bundle["nested_truncations"]["basis_labels_by_N"][str(N)],
                "class_inclusion_contract": bundle["nested_truncations"]["inclusion"],
                "not_a_continuum_rate": True,
            },
        },
        "periodic_eight_face_audit": face_audit,
        "member_convergence_pass": convergence_pass,
        "member_campaign_pass": directions_pass and convergence_pass,
    }


def _assert_no_forbidden_imports() -> None:
    tree = ast.parse(ROUTE_C_SOURCE.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = ("torch", "literal_torch_action", "numpy_c2_multin_fd5")
    if any(any(token in name for token in forbidden) for name in imports):
        raise RouteCConvergenceError(f"forbidden Route-C import graph: {imports}")


def build_payload() -> Mapping[str, Any]:
    _assert_no_forbidden_imports()
    frozen = _read_pinned_route_c()
    bundle = route_c.load_bundle()
    frozen_by_N = {
        int(member["N"]): member for member in frozen["scientific"]["members"]
    }
    campaigns = [
        _member_campaign(bundle, member, frozen_by_N[int(member["N"])])
        for member in bundle["primary_members"]
    ]
    all_directions = all(
        bool(row["all_four_directions_Euler_Green_pass"]) for row in campaigns
    )
    convergence = all(bool(row["member_convergence_pass"]) for row in campaigns)
    restricted_pass = all_directions and convergence
    return {
        "schema": SCHEMA,
        "classification": "theory_only;route_C;multi_N;four_directions;separate_convergence;restricted_spectral_family;fail_closed",
        "decision": {
            "route_C_all_four_directions_multi_N_pass": all_directions,
            "route_C_h_and_quadrature_convergence_pass": convergence,
            "restricted_spectral_family_Euler_Green_certificate_pass": restricted_pass,
            "independent_clean_process_redteam_pass": False,
            "full_mutant_campaign_pass": False,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "fixed_before_run": {
            "curve_names": list(CURVE_NAMES),
            "radial_orders": list(RADIAL_ORDERS),
            "tangential_orders": list(TANGENTIAL_ORDERS),
            "free_steps": list(FREE_STEPS),
            "coordinate_steps": list(COORDINATE_STEPS),
            "tolerances": {
                "radial_atol": RADIAL_ATOL,
                "radial_rtol": RADIAL_RTOL,
                "tangential_atol": TANGENTIAL_ATOL,
                "tangential_rtol": TANGENTIAL_RTOL,
                "free_step_atol": FREE_STEP_ATOL,
                "free_step_rtol": FREE_STEP_RTOL,
                "coordinate_step_atol": COORDINATE_STEP_ATOL,
                "coordinate_step_rtol": COORDINATE_STEP_RTOL,
                "periodic_primitive_tolerance": PERIODIC_PRIMITIVE_TOLERANCE,
            },
        },
        "scientific": {
            "member_campaigns": campaigns,
            "N_K_scope": {
                "N_values": bundle["nested_truncations"]["N_values"],
                "K_of_N": bundle["nested_truncations"]["K_of_N"],
                "inclusion": bundle["nested_truncations"]["inclusion"],
                "continuous_limit_inferred": False,
            },
        },
        "independence_audit": {
            "only_project_module_imported": str(ROUTE_C_SOURCE.relative_to(REPO)),
            "AD_or_FD5_action_modules_imported": [],
            "AD_or_FD5_values_read": False,
            "AD_or_FD5_tolerances_read": False,
            "all_non_joint_directions_reexecuted_from_primitives": True,
            "joint_direction_consumed_from_byte_pinned_route_C_receipt": True,
        },
        "source_pins": {
            "route_C_source_sha256": ROUTE_C_SOURCE_SHA256,
            "route_C_test_sha256": ROUTE_C_TEST_SHA256,
            "route_C_artifact_sha256": ROUTE_C_ARTIFACT_SHA256,
            "primitive_bundle_sha256": route_c.BUNDLE_SHA256,
            "literal_v5_2_action_sha256": route_c.LITERAL_V5_2_ACTION_SHA256,
        },
        "open_obligations": {
            "clean_room_and_mutants": "required next; no promotion before independent clean-process reproduction and all mandated mutants die",
            "uniform_continuum_bridge": "finite N=1,2,3 plus class inclusion is not density, uniform stability, or an N-to-infinity theorem",
        },
        "evidence_boundary": "This receipt certifies only the finite selected C_N members and four published tangent directions. N=1 is a spectral member and is not N1_ACTION. C1/N1, B4, B5, clean-room, mutants, and the continuous limit remain false.",
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
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(build_payload(), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
