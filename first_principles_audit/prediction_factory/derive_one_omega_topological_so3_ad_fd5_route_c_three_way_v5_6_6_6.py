#!/usr/bin/env python3
"""Three-way finite-member comparison: Torch AD, NumPy FD5, and Route C.

The comparator reads the byte-pinned raw AD and FD5 receipts, evaluates the
precision-stabilized independent Route C at the identical Qtheta=5, Qrho=10
quadrature, and compares all three pairs component by component.  It imports
neither action implementation A/B nor their helpers.

This is a restricted C_N certificate for the three selected members.  It is
not the clean-room mutant campaign and proves no N-to-infinity bridge.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5
    as route_c_stable,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
AD_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_torch_c2_multin_v5_6_5_6.json"
FD5_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.json"
ROUTE_C_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3.json"
)
FOUR_DIRECTION_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_multidirection_convergence_"
    "route_c_v5_6_6_4.json"
)
PRECISION_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_precision_stabilized_"
    "route_c_v5_6_6_5.json"
)
TEST = HERE / (
    "test_one_omega_topological_so3_ad_fd5_route_c_three_way_"
    "v5_6_6_6.py"
)
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_ad_fd5_route_c_three_way_"
    "v5_6_6_6.json"
)

AD_ARTIFACT_SHA256 = "d0db75f97c580e417e2032211134546695691598714f0ace65db8f24afc11cdb"
FD5_ARTIFACT_SHA256 = "501d5fddba619a32a8ab6c050e536c523cbc91795813f9a837b13c9d6fb133ea"
ROUTE_C_ARTIFACT_SHA256 = "4e343402192d539d7b5b8bf3e70dbbac139a779fea15273ce223143b0452bfd7"
FOUR_DIRECTION_ARTIFACT_SHA256 = "23579f90fc535a71d088e992a4f6f49aea515a8ab9c7b04bb6b7cc89bff9ddb8"
PRECISION_ARTIFACT_SHA256 = "06ad302a03d17e4ea718c9ab801113807a7f66c71102e69486f7869130f77654"

AD_SCHEMA = "holo.one-omega-topological-so3-torch-c2-multin-v5-6-5-6.v1"
FD5_SCHEMA = "holo.one-omega-topological-so3-numpy-c2-multin-fd5-v5-6-5-7.v1"
SCHEMA = "holo.one-omega-topological-so3-ad-fd5-route-c-three-way-v5-6-6-6.v1"

TANGENTIAL_ORDER = 5
RADIAL_ORDER = 10
PAIRWISE_ATOL = 1.0e-8
PAIRWISE_RTOL = 1.0e-11
ACTIVE_SIGN_THRESHOLD = 1.0e-6


class ThreeWayComparatorError(ValueError):
    """A frozen input or cross-route identity drifted."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_pinned(path: Path, expected_hash: str, expected_schema: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected_hash:
        raise ThreeWayComparatorError(f"pinned artifact drift for {path.name}: {observed}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != expected_schema:
        raise ThreeWayComparatorError(f"schema drift for {path.name}")
    return payload


def _cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    names = sorted(left)
    left_vector = np.asarray([float(left[name]) for name in names])
    right_vector = np.asarray([float(right[name]) for name in names])
    denominator = float(np.linalg.norm(left_vector) * np.linalg.norm(right_vector))
    if denominator == 0.0:
        raise ThreeWayComparatorError("zero three-way component vector")
    return float(left_vector @ right_vector / denominator)


def _three_way_rows(
    ad: Mapping[str, float],
    fd5: Mapping[str, float],
    route_c: Mapping[str, float],
) -> Mapping[str, Any]:
    if not (set(ad) == set(fd5) == set(route_c)):
        raise ThreeWayComparatorError("three-way component key drift")
    rows: dict[str, Any] = {}
    all_pass = True
    for name in sorted(ad):
        values = {
            "AD": float(ad[name]),
            "FD5": float(fd5[name]),
            "Route_C": float(route_c[name]),
        }
        scale = max(abs(value) for value in values.values())
        tolerance = PAIRWISE_ATOL + PAIRWISE_RTOL * scale
        signed = {
            "AD_minus_FD5": values["AD"] - values["FD5"],
            "AD_minus_Route_C": values["AD"] - values["Route_C"],
            "FD5_minus_Route_C": values["FD5"] - values["Route_C"],
        }
        absolute = {key: abs(value) for key, value in signed.items()}
        pairwise_pass = all(value <= tolerance for value in absolute.values())
        active = scale >= ACTIVE_SIGN_THRESHOLD
        nonzero_signs = {
            int(math.copysign(1.0, value)) for value in values.values() if value != 0.0
        }
        sign_pass = (not active) or len(nonzero_signs) == 1
        row_pass = pairwise_pass and sign_pass
        rows[name] = {
            "values": values,
            "raw_signed_residuals": signed,
            "absolute_residuals": absolute,
            "normalized_residuals": {
                key: value / max(1.0, scale) for key, value in absolute.items()
            },
            "fixed_tolerance": tolerance,
            "maximum_residual_over_tolerance": max(absolute.values()) / tolerance,
            "active_for_sign_check": active,
            "same_sign_when_active": sign_pass,
            "pass": row_pass,
        }
        all_pass = all_pass and row_pass
    names = sorted(ad)

    def l2(left: Mapping[str, float], right: Mapping[str, float]) -> float:
        return float(
            np.linalg.norm(
                np.asarray([float(left[name]) - float(right[name]) for name in names])
            )
        )

    return {
        "rows": rows,
        "pairwise_L2": {
            "AD_minus_FD5": l2(ad, fd5),
            "AD_minus_Route_C": l2(ad, route_c),
            "FD5_minus_Route_C": l2(fd5, route_c),
        },
        "pairwise_cosine": {
            "AD_FD5": _cosine(ad, fd5),
            "AD_Route_C": _cosine(ad, route_c),
            "FD5_Route_C": _cosine(fd5, route_c),
        },
        "maximum_residual_over_tolerance": max(
            row["maximum_residual_over_tolerance"] for row in rows.values()
        ),
        "pass": all_pass,
    }


def build_payload() -> Mapping[str, Any]:
    ad_payload = _read_pinned(AD_ARTIFACT, AD_ARTIFACT_SHA256, AD_SCHEMA)
    fd5_payload = _read_pinned(FD5_ARTIFACT, FD5_ARTIFACT_SHA256, FD5_SCHEMA)
    route_payload = _read_pinned(
        ROUTE_C_ARTIFACT, ROUTE_C_ARTIFACT_SHA256, route_c_stable.route_c.SCHEMA
    )
    four_direction = _read_pinned(
        FOUR_DIRECTION_ARTIFACT,
        FOUR_DIRECTION_ARTIFACT_SHA256,
        "holo.one-omega-topological-so3-multidirection-convergence-route-c-v5-6-6-4.v1",
    )
    precision = _read_pinned(
        PRECISION_ARTIFACT, PRECISION_ARTIFACT_SHA256, route_c_stable.SCHEMA
    )
    if not precision["decision"]["restricted_spectral_family_precision_correction_pass"]:
        raise ThreeWayComparatorError("precision correction is not green")
    if not four_direction["decision"]["route_C_all_four_directions_multi_N_pass"]:
        raise ThreeWayComparatorError("four-direction Route-C lemma is not green")
    if not route_payload["decision"]["route_C_multin_independent_Euler_Green_pass"]:
        raise ThreeWayComparatorError("base Route-C Euler-Green lemma is not green")

    ad_by_n = {int(row["N"]): row for row in ad_payload["scientific"]["members"]}
    fd5_by_n = {int(row["N"]): row for row in fd5_payload["scientific"]["members"]}
    route_by_n = {int(row["N"]): row for row in route_payload["scientific"]["members"]}
    bundle = route_c_stable.route_c.load_bundle()
    members: list[Mapping[str, Any]] = []
    for primitive_member in bundle["primary_members"]:
        N = int(primitive_member["N"])
        K = int(primitive_member["K"])
        if N not in ad_by_n or N not in fd5_by_n or N not in route_by_n:
            raise ThreeWayComparatorError(f"missing selected member N={N}")
        ad_row = ad_by_n[N]
        fd5_row = fd5_by_n[N]
        route_row = route_by_n[N]
        center_hashes = {
            primitive_member["authoritative_free_central_f64le"]["sha256"],
            ad_row["authoritative_free_central_sha256"],
            fd5_row["authoritative_free_central_sha256"],
            route_row["authoritative_free_central_sha256"],
        }
        tangent_hashes = {
            next(
                curve
                for curve in primitive_member["curves"]
                if curve["name"] == "joint_all_primitive_classes_control_candidate"
            )["authoritative_free_tangent_f64le"]["sha256"],
            ad_row["authoritative_free_tangent_sha256"],
            fd5_row["authoritative_free_tangent_sha256"],
            route_row["authoritative_free_tangent_sha256"],
        }
        if len(center_hashes) != 1 or len(tangent_hashes) != 1:
            raise ThreeWayComparatorError(f"center/tangent lineage mismatch for N={N}")
        route_c_record = route_c_stable.evaluate_direct_member_stable(
            bundle,
            primitive_member,
            tangential_order=TANGENTIAL_ORDER,
            radial_order=RADIAL_ORDER,
        )
        route_c_values = route_c_record["direct_local_free_JVP_by_component"]
        ad_values = ad_row["AD_JVP_by_component_at_Q5_R10"]
        fd5_values = fd5_row["FD5_Richardson_h002_h001"]
        comparison = _three_way_rows(ad_values, fd5_values, route_c_values)
        members.append(
            {
                "N": N,
                "K": K,
                "member_id": primitive_member["member_id"],
                "authoritative_free_central_sha256": next(iter(center_hashes)),
                "authoritative_free_tangent_sha256": next(iter(tangent_hashes)),
                "quadrature": {
                    "tangential_order_per_axis": TANGENTIAL_ORDER,
                    "radial_order": RADIAL_ORDER,
                },
                "AD_JVP": ad_values,
                "FD5_Richardson_JVP": fd5_values,
                "Route_C_precision_stabilized_JVP": route_c_values,
                "comparison": comparison,
                "member_three_way_pass": bool(comparison["pass"]),
            }
        )
        print(f"completed AD-FD5-Route-C comparison N={N} K={K}", flush=True)

    three_way_pass = all(bool(row["member_three_way_pass"]) for row in members)
    return {
        "schema": SCHEMA,
        "classification": "theory_only;AD;FD5;independent_route_C;three_way;multi_N;identical_quadrature;restricted_spectral_family;fail_closed",
        "decision": {
            "AD_FD5_Route_C_three_way_comparison_pass": three_way_pass,
            "Route_C_independent_Euler_Green_multi_N_pass": True,
            "Route_C_four_directions_multi_N_pass": True,
            "Route_C_precision_stabilized_convergence_pass": True,
            "restricted_spectral_family_three_route_certificate_pass": three_way_pass,
            "independent_clean_process_redteam_pass": False,
            "full_mutant_campaign_pass": False,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "fixed_before_acceptance_run": {
            "tangential_order_per_axis": TANGENTIAL_ORDER,
            "radial_order": RADIAL_ORDER,
            "pairwise_absolute_tolerance": PAIRWISE_ATOL,
            "pairwise_relative_tolerance": PAIRWISE_RTOL,
            "active_sign_threshold": ACTIVE_SIGN_THRESHOLD,
            "all_three_pairs_required_componentwise": True,
        },
        "scientific": {"members": members},
        "independence_audit": {
            "Torch_action_module_imported": False,
            "NumPy_FD5_action_module_imported": False,
            "raw_AD_receipt_read_only": True,
            "raw_FD5_receipt_read_only": True,
            "Route_C_recomputed_from_primitives": True,
            "Route_C_uses_extended_precision_coordinate_jets": True,
            "expected_component_values_hardcoded": False,
        },
        "source_pins": {
            "AD_raw_artifact_sha256": AD_ARTIFACT_SHA256,
            "FD5_raw_artifact_sha256": FD5_ARTIFACT_SHA256,
            "Route_C_Euler_Green_artifact_sha256": ROUTE_C_ARTIFACT_SHA256,
            "Route_C_four_direction_red_refinement_artifact_sha256": FOUR_DIRECTION_ARTIFACT_SHA256,
            "Route_C_precision_correction_artifact_sha256": PRECISION_ARTIFACT_SHA256,
            "primitive_bundle_sha256": route_c_stable.route_c.BUNDLE_SHA256,
            "literal_v5_2_action_sha256": route_c_stable.route_c.LITERAL_V5_2_ACTION_SHA256,
        },
        "open_obligations": {
            "clean_room_and_mutants": "required next; the comparator is not an independent process replica or mutant campaign",
            "uniform_continuum_bridge": "the three finite selected members do not prove density, uniform stability, or the N-to-infinity limit",
        },
        "evidence_boundary": "AD, Richardson FD5, and precision-stabilized Route C are compared componentwise only for the selected N=1,2,3 joint directions at Qtheta=5 and Qrho=10. C1/N1, B4/B5, clean-room mutants, and the continuous limit remain false.",
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
