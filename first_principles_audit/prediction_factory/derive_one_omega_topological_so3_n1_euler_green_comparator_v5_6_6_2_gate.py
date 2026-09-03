#!/usr/bin/env python3
"""Compare independent N=1 Euler--Green route C with frozen v5.6.5.8."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"

FREEZE_SOURCE = HERE / "freeze_one_omega_topological_so3_c2_multin_ad_fd5_v5_6_5_8_restricted_certificate.py"
FREEZE_TEST = HERE / "test_freeze_one_omega_topological_so3_c2_multin_ad_fd5_v5_6_5_8_restricted_certificate.py"
FREEZE_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_c2_multin_ad_fd5_v5_6_5_8_restricted_certificate.json"
ROUTE_C_SOURCE = HERE / "derive_one_omega_topological_so3_n1_independent_euler_green_route_c_v5_6_6_1.py"
ROUTE_C_TEST = HERE / "test_one_omega_topological_so3_n1_independent_euler_green_route_c_v5_6_6_1.py"
ROUTE_C_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_n1_independent_euler_green_route_c_v5_6_6_1.json"
TEST = HERE / "test_one_omega_topological_so3_n1_euler_green_comparator_v5_6_6_2_gate.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_n1_euler_green_comparator_v5_6_6_2_gate.json"

FREEZE_SOURCE_SHA256 = "b3127f2999f1f48998ab8d7701cf99e3ce78d34c50684951bd28dcbb3665eb51"
FREEZE_TEST_SHA256 = "ee5102ef029858999111d47d374fef3e65864795ced1269ae9eae5eef917ed8b"
FREEZE_ARTIFACT_SHA256 = "502a6499feb895c9da7f6b50ff8f42914e4a7772f77396dfcdf6af2bf854791c"
ROUTE_C_SOURCE_SHA256 = "726f5aaf65bd046f791be81abf25984d3e875bc0229f76f9eeaebaa28e578339"
ROUTE_C_TEST_SHA256 = "1894c57857fc36cd512e1c1135fb4737a0fdd4c269fa8f9b2e78ae1fbc248d16"
ROUTE_C_ARTIFACT_SHA256 = "4bc6dee8193a164288cebe8cdfa321f2b6744a53d9ba261fddeb69320b5427a0"

SCHEMA = "holo.one-omega-topological-so3-n1-euler-green-comparator-v5-6-6-2.v1"
DIRECT_COMPONENT_L2_ABS_FLOOR = 1.0e-7
DIRECT_COMPONENT_L2_REL_COEFFICIENT = 2.0e-10
DIRECT_TOTAL_ABS_FLOOR = 1.0e-7
DIRECT_TOTAL_REL_COEFFICIENT = 2.0e-10
ACTIVE_COMPONENT_FRACTION = 1.0e-10
ACTIVE_COMPONENT_REL_TOLERANCE = 1.0e-7
STOKES_FINAL_COMPONENT_ABS_TOLERANCE = 5.0e-8
STOKES_FINAL_TOTAL_ABS_TOLERANCE = 5.0e-8
STORED_RESIDUAL_ABS_TOLERANCE = 2.0e-12


class EulerGreenComparatorError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, expected: str, label: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected:
        raise EulerGreenComparatorError(f"{label} byte pin drift: {observed}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EulerGreenComparatorError(f"{label} is not a JSON object")
    return payload


def load_inputs() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    for path, expected, label in (
        (FREEZE_SOURCE, FREEZE_SOURCE_SHA256, "v5.6.5.8 freeze source"),
        (FREEZE_TEST, FREEZE_TEST_SHA256, "v5.6.5.8 freeze test"),
        (ROUTE_C_SOURCE, ROUTE_C_SOURCE_SHA256, "route C source"),
        (ROUTE_C_TEST, ROUTE_C_TEST_SHA256, "route C test"),
    ):
        observed = _sha256(path)
        if observed != expected:
            raise EulerGreenComparatorError(f"{label} byte pin drift: {observed}")
    return (
        _load(FREEZE_ARTIFACT, FREEZE_ARTIFACT_SHA256, "v5.6.5.8 freeze artifact"),
        _load(ROUTE_C_ARTIFACT, ROUTE_C_ARTIFACT_SHA256, "route C artifact"),
    )


def _l2(values: Mapping[str, float], components: tuple[str, ...]) -> float:
    return math.sqrt(math.fsum(float(values[name]) ** 2 for name in components))


def analyze(frozen: Mapping[str, Any], route_c: Mapping[str, Any]) -> Mapping[str, Any]:
    if frozen["decision"].get("v5_6_5_8_restricted_AD_FD5_multin_certificate_frozen") is not True:
        raise EulerGreenComparatorError("v5.6.5.8 restricted certificate is not frozen")
    if route_c["decision"].get("route_C_N1_independent_Euler_Green_raw_pass") is not True:
        raise EulerGreenComparatorError("route C N=1 raw theorem is red")
    for payload, label in ((frozen, "frozen certificate"), (route_c, "route C")):
        for key in ("C1_ACTION_pass", "N1_ACTION_pass", "C1_N1_promotion_authorized"):
            if payload["decision"].get(key) is not False:
                raise EulerGreenComparatorError(f"{label} illegally promoted {key}")

    member = next(row for row in frozen["scientific"]["member_records"] if row["N"] == 1)
    science = route_c["scientific"]
    for key in (
        "member_id",
        "authoritative_free_central_sha256",
        "authoritative_free_tangent_sha256",
    ):
        if science[key] != member[key]:
            raise EulerGreenComparatorError(f"N=1 primitive identity mismatch for {key}")
    expected_rows = {row["component"]: row for row in member["sector_table"]}
    direct = {
        key: float(value)
        for key, value in science["direct_local_jet_JVP_by_component"].items()
    }
    expected_ad = {key: float(row["AD_JVP"]) for key, row in expected_rows.items()}
    expected_fd = {
        key: float(row["Richardson_FD5_h002_h001"])
        for key, row in expected_rows.items()
    }
    if not (set(direct) == set(expected_ad) == set(expected_fd)):
        raise EulerGreenComparatorError("N=1 component set mismatch")
    components = tuple(sorted(name for name in direct if name != "S_total"))
    residual_ad = {name: direct[name] - expected_ad[name] for name in direct}
    residual_fd = {name: direct[name] - expected_fd[name] for name in direct}
    direct_l2 = _l2(direct, components)
    component_residual_l2_ad = _l2(residual_ad, components)
    component_residual_l2_fd = _l2(residual_fd, components)
    component_tolerance = DIRECT_COMPONENT_L2_ABS_FLOOR + (
        DIRECT_COMPONENT_L2_REL_COEFFICIENT * max(1.0, direct_l2)
    )
    total_tolerance = DIRECT_TOTAL_ABS_FLOOR + DIRECT_TOTAL_REL_COEFFICIENT * max(
        1.0, abs(direct["S_total"])
    )
    active_threshold = ACTIVE_COMPONENT_FRACTION * max(
        1.0, max(abs(direct[name]) for name in components)
    )
    active = tuple(name for name in components if abs(direct[name]) >= active_threshold)
    relative_ad = {
        name: abs(residual_ad[name])
        / max(abs(direct[name]), abs(expected_ad[name]), 1.0e-300)
        for name in active
    }

    refinement = sorted(
        science["radial_refinement_records"], key=lambda row: int(row["radial_Gauss_order"])
    )
    if [int(row["radial_Gauss_order"]) for row in refinement] != [8, 10, 12, 16, 20]:
        raise EulerGreenComparatorError("route C radial refinement order drift")
    recomputed_rows = []
    for row in refinement:
        predicted = {key: float(value) for key, value in row["predicted_Euler_Green_by_component"].items()}
        local_direct = {key: float(value) for key, value in row["direct_local_jet_JVP_by_component"].items()}
        if set(predicted) != set(local_direct):
            raise EulerGreenComparatorError("route C refinement component set mismatch")
        residual = {key: local_direct[key] - predicted[key] for key in predicted}
        stored = row["Stokes_residual_direct_minus_Euler_Green"]
        storage_error = max(abs(residual[key] - float(stored[key])) for key in residual)
        recomputed_rows.append(
            {
                "radial_Gauss_order": int(row["radial_Gauss_order"]),
                "maximum_absolute_component_Stokes_residual": max(
                    abs(value) for key, value in residual.items() if key != "S_total"
                ),
                "total_absolute_Stokes_residual": abs(residual["S_total"]),
                "maximum_stored_residual_reconstruction_error": storage_error,
            }
        )
    component_series = [row["maximum_absolute_component_Stokes_residual"] for row in recomputed_rows]
    total_series = [row["total_absolute_Stokes_residual"] for row in recomputed_rows]
    stokes_checks = {
        "stored_residuals_reconstruct": max(
            row["maximum_stored_residual_reconstruction_error"] for row in recomputed_rows
        )
        <= STORED_RESIDUAL_ABS_TOLERANCE,
        "component_residual_contracts_monotonically": all(
            right < left for left, right in zip(component_series, component_series[1:])
        ),
        "total_residual_contracts_monotonically": all(
            right < left for left, right in zip(total_series, total_series[1:])
        ),
        "final_component_residual_pass": component_series[-1]
        <= STOKES_FINAL_COMPONENT_ABS_TOLERANCE,
        "final_total_residual_pass": total_series[-1]
        <= STOKES_FINAL_TOTAL_ABS_TOLERANCE,
        "eight_periodic_face_fluxes_zero": len(
            science["face_audit"]["tangential_T4_eight_faces"]
        )
        == 8
        and all(
            float(value) == 0.0
            for value in science["face_audit"]["tangential_T4_eight_faces"].values()
        ),
        "outer_radial_tangent_flat": float(science["outer_boundary_tangent_Linf"])
        <= 2.0e-10,
        "corner_residual_zero": float(science["corner_residual"]) == 0.0,
    }
    comparison_checks = {
        "route_C_direct_component_vector_matches_AD": component_residual_l2_ad
        <= component_tolerance,
        "route_C_direct_component_vector_matches_FD5": component_residual_l2_fd
        <= component_tolerance,
        "route_C_direct_total_matches_AD": abs(residual_ad["S_total"]) <= total_tolerance,
        "route_C_direct_total_matches_FD5": abs(residual_fd["S_total"]) <= total_tolerance,
        "all_active_components_match_AD_relatively": bool(active)
        and max(relative_ad.values()) <= ACTIVE_COMPONENT_REL_TOLERANCE,
    }
    checks = {
        "frozen_inputs_and_primitive_hashes_match": True,
        "route_C_independence_contract_is_explicit": route_c["independence_audit"]
        == {
            "AD_or_FD_expected_values_read": False,
            "action_formula_reconstructed_from_literal_hash": "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a",
            "comparison_tolerances_read": False,
            "primitive_bundle_only_scientific_input": True,
            "project_action_or_Euler_modules_imported": [],
        },
        "direct_local_variation_matches_two_frozen_routes": all(comparison_checks.values()),
        "Euler_Green_Stokes_refinement_pass": all(stokes_checks.values()),
        "nontrivial_R_on_both_sides": all(
            float(row["distance_from_identity_Frobenius"]) > 1.0e-3
            for row in science["nontrivial_R_controls"].values()
        ),
    }
    return {
        "checks": checks,
        "all_N1_checks_pass": all(checks.values()),
        "direct_route_comparison": {
            "route_C_direct_local_JVP": direct,
            "frozen_Torch_AD": expected_ad,
            "frozen_NumPy_Richardson_FD5": expected_fd,
            "route_C_minus_AD": residual_ad,
            "route_C_minus_FD5": residual_fd,
            "component_residual_L2_vs_AD": component_residual_l2_ad,
            "component_residual_L2_vs_FD5": component_residual_l2_fd,
            "component_L2_tolerance": component_tolerance,
            "total_absolute_residual_vs_AD": abs(residual_ad["S_total"]),
            "total_absolute_residual_vs_FD5": abs(residual_fd["S_total"]),
            "total_tolerance": total_tolerance,
            "active_component_threshold": active_threshold,
            "active_component_relative_residual_vs_AD": relative_ad,
            "checks": comparison_checks,
        },
        "Euler_Green_Stokes_comparison": {
            "refinement_rows_recomputed": recomputed_rows,
            "checks": stokes_checks,
        },
    }


def build_payload() -> Mapping[str, Any]:
    frozen, route_c = load_inputs()
    scientific = analyze(frozen, route_c)
    n1_pass = bool(scientific["all_N1_checks_pass"])
    return {
        "schema": SCHEMA,
        "classification": "theory_only;N1_independent_Euler_Green_smoke;frozen_cross_route_comparison;fail_closed_multiN_C1_N1",
        "decision": {
            "N1_independent_Euler_Green_smoke_pass": n1_pass,
            "N2_N3_independent_Euler_Green_pass": False,
            "Euler_Green_independent_route_pass": False,
            "clean_room_full_mutant_campaign_pass": False,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "tolerances_fixed_in_comparator": {
            "direct_component_L2_abs_floor": DIRECT_COMPONENT_L2_ABS_FLOOR,
            "direct_component_L2_relative_coefficient": DIRECT_COMPONENT_L2_REL_COEFFICIENT,
            "direct_total_abs_floor": DIRECT_TOTAL_ABS_FLOOR,
            "direct_total_relative_coefficient": DIRECT_TOTAL_REL_COEFFICIENT,
            "active_component_fraction": ACTIVE_COMPONENT_FRACTION,
            "active_component_relative_tolerance": ACTIVE_COMPONENT_REL_TOLERANCE,
            "Stokes_final_component_abs_tolerance": STOKES_FINAL_COMPONENT_ABS_TOLERANCE,
            "Stokes_final_total_abs_tolerance": STOKES_FINAL_TOTAL_ABS_TOLERANCE,
            "stored_residual_abs_tolerance": STORED_RESIDUAL_ABS_TOLERANCE,
        },
        "scientific": scientific,
        "source_pins": {
            "v5_6_5_8_freeze": {
                "source_sha256": FREEZE_SOURCE_SHA256,
                "test_sha256": FREEZE_TEST_SHA256,
                "artifact_sha256": FREEZE_ARTIFACT_SHA256,
            },
            "route_C_N1": {
                "source_sha256": ROUTE_C_SOURCE_SHA256,
                "test_sha256": ROUTE_C_TEST_SHA256,
                "artifact_sha256": ROUTE_C_ARTIFACT_SHA256,
            },
        },
        "open_obligations": {
            "Euler_Green": "extend the independent route and Stokes audit to the x-dependent N=2 and N=3 members",
            "clean_room": "execute the full independent mutant campaign only after multi-N Euler-Green closure",
            "continuum": "prove the uniform N-to-infinity bridge separately",
            "promotion": "C1/N1 and B4/B5 remain closed",
        },
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
        "evidence_boundary": "The independent analytic route C closes Euler-Green only for the finite N=1 constant tangential member, with radial Stokes convergence and an external comparison to frozen AD/FD5. The multi-N Euler-Green gate and every C1/N1/B4/B5 promotion remain false.",
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
