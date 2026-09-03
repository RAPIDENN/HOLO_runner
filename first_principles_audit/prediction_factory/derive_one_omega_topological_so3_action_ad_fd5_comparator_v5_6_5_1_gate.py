#!/usr/bin/env python3
"""Fail-closed comparator for the independent literal-action routes A and B.

This module never imports either evaluator.  It consumes their byte-pinned raw
receipts, verifies that they used the same primitive member and quadrature, and
compares action values plus off-shell directional derivatives.  It deliberately
does not promote C1/N1: Euler--Green, mutants, multi-N convergence, and an
independent clean-process audit remain separate obligations.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
ROUTE_A_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_literal_torch_action_route_a_v5_6_5_certificate.json"
ROUTE_B_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.json"
ROUTE_A_SOURCE = HERE / "derive_one_omega_topological_so3_literal_torch_action_route_a_v5_6_5_certificate.py"
ROUTE_A_TEST = HERE / "test_one_omega_topological_so3_literal_torch_action_route_a_v5_6_5_certificate.py"
ROUTE_B_SOURCE = HERE / "derive_one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.py"
ROUTE_B_TEST = HERE / "test_one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.py"
TEST = HERE / "test_one_omega_topological_so3_action_ad_fd5_comparator_v5_6_5_1_gate.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_action_ad_fd5_comparator_v5_6_5_1_gate.json"

ROUTE_A_ARTIFACT_SHA256 = "ec56360b271cea3d32b41c5d3c19e7a7dc85de4425b4cd3ab4e5fe290f696e2e"
ROUTE_A_SOURCE_SHA256 = "dfb1692b3af96c1827ad7fd435b0de7a2af89dd7535a328bc49ba5431d492a7c"
ROUTE_A_TEST_SHA256 = "ecf155ab10acc39f6b3e714833ea081758b353b5601ce5702e5d52400eb89987"
ROUTE_B_ARTIFACT_SHA256 = "7e1044cdc628052750f02f0ab4d134c89ee85f7296d3de027d998177578320db"
ROUTE_B_SOURCE_SHA256 = "6c98724d0e51c1cad16c80303e6ad7625d661bd1c9c56c9ff96c5b8124992909"
ROUTE_B_TEST_SHA256 = "a6ee90e92ae9584207753770f9fb9c8e5c20a1136356520283ba5f7d733fa2fa"

SCHEMA = "holo.one-omega-topological-so3-action-ad-fd5-comparator-v5-6-5-1.v1"
EXPECTED_STEPS = (4.0e-2, 2.0e-2, 1.0e-2, 5.0e-3, 2.5e-3)
RICHARDSON_COARSE_STEP = 4.0e-2
RICHARDSON_FINE_STEP = 2.0e-2
CENTRAL_ABS_LINF_TOLERANCE = 5.0e-10
CENTRAL_COMPONENT_REL_TOLERANCE = 1.0e-9
H4_ORDER_MINIMUM = 3.25
H4_ORDER_MAXIMUM = 4.75
RICHARDSON_COMPONENT_L2_TOLERANCE = 2.0e-8
RICHARDSON_COMPONENT_REL_TOLERANCE = 5.0e-5

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
OUTPUT_COMPONENTS = ACTION_COMPONENTS + ("S_total",)


class ComparatorError(ValueError):
    """One of the pinned inputs or comparison contracts drifted."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_pinned(path: Path, expected_sha256: str, *, label: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise ComparatorError(f"{label} byte pin drift: {observed}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ComparatorError(f"{label} is not a JSON object")
    return payload


def load_route_receipts() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    for path, expected, label in (
        (ROUTE_A_SOURCE, ROUTE_A_SOURCE_SHA256, "route A source"),
        (ROUTE_A_TEST, ROUTE_A_TEST_SHA256, "route A test"),
        (ROUTE_B_SOURCE, ROUTE_B_SOURCE_SHA256, "route B source"),
        (ROUTE_B_TEST, ROUTE_B_TEST_SHA256, "route B test"),
    ):
        if _sha256(path) != expected:
            raise ComparatorError(f"{label} byte pin drift")
    route_a = _load_pinned(
        ROUTE_A_ARTIFACT, ROUTE_A_ARTIFACT_SHA256, label="route A artifact"
    )
    route_b = _load_pinned(
        ROUTE_B_ARTIFACT, ROUTE_B_ARTIFACT_SHA256, label="route B artifact"
    )
    if route_a["provenance"]["generator"]["sha256"] != ROUTE_A_SOURCE_SHA256:
        raise ComparatorError("route A embedded source pin drift")
    if route_a["provenance"]["test"]["sha256"] != ROUTE_A_TEST_SHA256:
        raise ComparatorError("route A embedded test pin drift")
    if route_b["provenance"]["generator"]["sha256"] != ROUTE_B_SOURCE_SHA256:
        raise ComparatorError("route B embedded source pin drift")
    if route_b["provenance"]["test"]["sha256"] != ROUTE_B_TEST_SHA256:
        raise ComparatorError("route B embedded test pin drift")
    return route_a, route_b


def _exact_components(record: Mapping[str, Any], *, label: str) -> dict[str, float]:
    if set(record) != set(OUTPUT_COMPONENTS):
        raise ComparatorError(f"{label} component coverage drift")
    result = {name: float(record[name]) for name in OUTPUT_COMPONENTS}
    if not all(math.isfinite(value) for value in result.values()):
        raise ComparatorError(f"{label} contains a non-finite value")
    return result


def _component_residuals(
    left: Mapping[str, float], right: Mapping[str, float]
) -> tuple[dict[str, Mapping[str, float]], float, float, float]:
    rows: dict[str, Mapping[str, float]] = {}
    component_squares: list[float] = []
    for component in OUTPUT_COMPONENTS:
        residual = float(left[component] - right[component])
        scale = max(abs(float(left[component])), abs(float(right[component])), 1.0e-300)
        rows[component] = {
            "left": float(left[component]),
            "right": float(right[component]),
            "residual": residual,
            "absolute_residual": abs(residual),
            "component_relative_residual": abs(residual) / scale,
        }
        if component != "S_total":
            component_squares.append(residual * residual)
    return (
        rows,
        max(row["absolute_residual"] for row in rows.values()),
        max(row["component_relative_residual"] for row in rows.values()),
        math.sqrt(math.fsum(component_squares)),
    )


def analyze_route_receipts(
    route_a: Mapping[str, Any], route_b: Mapping[str, Any]
) -> Mapping[str, Any]:
    if route_a.get("schema") != "holo.one-omega-topological-so3-literal-torch-action-route-a-v5-6-5-certificate.v1":
        raise ComparatorError("route A schema drift")
    if route_b.get("schema") != "holo.one-omega-topological-so3-numpy-fd5-action-route-b-v5-6-5.v1":
        raise ComparatorError("route B schema drift")
    if route_a["decision"].get("route_A_Q5_literal_action_and_AD_JVP_pass") is not True:
        raise ComparatorError("route A raw receipt is not green")
    if route_b["decision"].get("route_B_Q5_literal_action_and_FD5_window_pass") is not True:
        raise ComparatorError("route B raw receipt is not green")
    for payload, label in ((route_a, "route A"), (route_b, "route B")):
        for key in ("C1_ACTION_pass", "N1_ACTION_pass", "C1_N1_promotion_authorized"):
            if payload["decision"].get(key) is not False:
                raise ComparatorError(f"{label} illegally promoted {key}")

    a_science = route_a["scientific"]
    b_science = route_b["scientific"]
    a_input = {
        "bundle_sha256": route_a["provenance"]["primitive_bundle"]["sha256"],
        "action_sha256": route_a["mathematical_contract"]["literal_action_sha256"],
        "member_id": a_science["member_id"],
        "identity_member_id": a_science["identity_control_member_id"],
        "central_sha256": a_science["authoritative_free_central_sha256"],
        "tangent_sha256": a_science["authoritative_free_tangent_sha256"],
        "ambient_tangent_sha256": a_science["parent_ambient_tangent_sha256"],
        "quadrature": a_science["quadrature"],
    }
    b_contract = route_b["input_contract"]
    b_quadrature = b_science["quadrature"]
    b_input = {
        "bundle_sha256": b_contract["primitive_bundle"]["sha256"],
        "action_sha256": b_contract["literal_action_sha256"],
        "member_id": b_contract["member_id"],
        "identity_member_id": b_contract["identity_control_member_id"],
        "central_sha256": b_contract["authoritative_free_central_sha256"],
        "tangent_sha256": b_contract["authoritative_free_tangent_sha256"],
        "ambient_tangent_sha256": b_contract["parent_ambient_tangent_sha256"],
        "quadrature": {
            "tangential_points_per_axis": b_quadrature[
                "tangential_points_per_axis"
            ],
            "tangential_node_count": b_quadrature["tangential_total_points"],
            "radial_gauss_order": b_quadrature["radial_gauss_order"],
        },
    }
    if a_input != b_input:
        raise ComparatorError("routes did not consume identical scientific primitives")

    a_central = _exact_components(a_science["central_S_rel_components"], label="route A central")
    b_central = _exact_components(b_science["central_S_rel_components"], label="route B central")
    central_rows, central_linf, central_relative, central_l2 = _component_residuals(
        a_central, b_central
    )
    a_identity = _exact_components(
        a_science["R_equals_identity_control"]["central_S_rel_components"],
        label="route A R=I",
    )
    b_identity = _exact_components(
        b_science["R_equals_identity_control"]["central_S_rel_components"],
        label="route B R=I",
    )
    identity_rows, identity_linf, identity_relative, identity_l2 = _component_residuals(
        a_identity, b_identity
    )
    ad = _exact_components(a_science["AD_JVP_by_component"], label="route A AD JVP")
    if abs(ad["S_total"]) <= 0.0:
        raise ComparatorError("off-shell comparison direction was made trivially stationary")

    window = b_science["FD5_refinement_window"]
    if tuple(float(step) for step in window["steps"]) != EXPECTED_STEPS:
        raise ComparatorError("FD5 refinement steps drift")
    endpoint_records = window["endpoint_records_by_float_hex"]
    if int(window["unique_endpoint_count"]) != 12 or len(endpoint_records) != 12:
        raise ComparatorError("raw FD5 endpoint cache is incomplete")
    for endpoint in endpoint_records.values():
        _exact_components(endpoint["S_rel_components"], label="route B endpoint")
        if float(endpoint["pointwise_gluing_Linf"]) >= 2.0e-12:
            raise ComparatorError("route B endpoint gluing drift")

    derivative_by_step: dict[float, dict[str, float]] = {}
    raw_error_rows: list[dict[str, Any]] = []
    for row in window["derivatives"]:
        step = float(row["step"])
        fd = _exact_components(
            row["FD5_action_directional_derivative"], label=f"route B FD5 h={step}"
        )
        derivative_by_step[step] = fd
        residuals, linf, relative, l2 = _component_residuals(ad, fd)
        raw_error_rows.append(
            {
                "step": step,
                "residual_by_component": residuals,
                "all_output_Linf": linf,
                "all_output_component_relative_Linf": relative,
                "twenty_component_L2": l2,
                "total_absolute_residual": abs(ad["S_total"] - fd["S_total"]),
            }
        )
    if tuple(row["step"] for row in raw_error_rows) != EXPECTED_STEPS:
        raise ComparatorError("FD5 derivative row order drift")
    for index in range(1, len(raw_error_rows)):
        previous = raw_error_rows[index - 1]["twenty_component_L2"]
        current = raw_error_rows[index]["twenty_component_L2"]
        raw_error_rows[index]["observed_L2_order_from_previous"] = math.log(
            previous / current, 2.0
        )

    coarse = derivative_by_step[RICHARDSON_COARSE_STEP]
    fine = derivative_by_step[RICHARDSON_FINE_STEP]
    richardson = {
        component: fine[component] + (fine[component] - coarse[component]) / 15.0
        for component in OUTPUT_COMPONENTS
    }
    rich_rows, rich_linf, rich_relative, rich_l2 = _component_residuals(ad, richardson)
    coarse_orders = tuple(
        raw_error_rows[index]["observed_L2_order_from_previous"]
        for index in (1, 2)
    )
    checks = {
        "byte_pinned_independent_route_receipts_loaded": True,
        "same_action_bundle_member_tangent_and_Q5_r3": True,
        "twenty_components_plus_total_present_in_every_raw_record": True,
        "central_action_component_Linf_within_tolerance": central_linf
        <= CENTRAL_ABS_LINF_TOLERANCE,
        "central_action_component_relative_Linf_within_tolerance": central_relative
        <= CENTRAL_COMPONENT_REL_TOLERANCE,
        "R_identity_action_component_Linf_within_tolerance": identity_linf
        <= CENTRAL_ABS_LINF_TOLERANCE,
        "R_identity_action_component_relative_Linf_within_tolerance": identity_relative
        <= CENTRAL_COMPONENT_REL_TOLERANCE,
        "two_consecutive_coarse_L2_orders_are_fourth_order": all(
            H4_ORDER_MINIMUM <= order <= H4_ORDER_MAXIMUM
            for order in coarse_orders
        ),
        "roundoff_floor_is_visible_after_h4_window": raw_error_rows[-1][
            "twenty_component_L2"
        ]
        > min(row["twenty_component_L2"] for row in raw_error_rows[:-1]),
        "Richardson_twenty_component_L2_within_tolerance": rich_l2
        <= RICHARDSON_COMPONENT_L2_TOLERANCE,
        "Richardson_each_component_relative_within_tolerance": rich_relative
        <= RICHARDSON_COMPONENT_REL_TOLERANCE,
        "off_shell_direction_is_nontrivial": abs(ad["S_total"]) > 1.0e-6,
        "no_on_shell_zero_was_used_as_acceptance": True,
    }
    return {
        "input_identity": a_input,
        "checks": checks,
        "all_direct_comparison_checks_pass": all(checks.values()),
        "central_action_comparison": {
            "residual_by_component": central_rows,
            "all_output_Linf": central_linf,
            "all_output_component_relative_Linf": central_relative,
            "twenty_component_L2": central_l2,
        },
        "R_identity_action_comparison": {
            "residual_by_component": identity_rows,
            "all_output_Linf": identity_linf,
            "all_output_component_relative_Linf": identity_relative,
            "twenty_component_L2": identity_l2,
        },
        "raw_AD_JVP": ad,
        "raw_FD5_error_window": raw_error_rows,
        "Richardson_h4_cancellation": {
            "coarse_step": RICHARDSON_COARSE_STEP,
            "fine_step": RICHARDSON_FINE_STEP,
            "formula": "D_R=D(h/2)+(D(h/2)-D(h))/15",
            "extrapolated_derivative": richardson,
            "residual_by_component": rich_rows,
            "all_output_Linf": rich_linf,
            "all_output_component_relative_Linf": rich_relative,
            "twenty_component_L2": rich_l2,
        },
    }


def build_payload() -> dict[str, Any]:
    route_a, route_b = load_route_receipts()
    scientific = analyze_route_receipts(route_a, route_b)
    direct_pass = scientific["all_direct_comparison_checks_pass"]
    return {
        "schema": SCHEMA,
        "title": "Independent Torch-AD versus NumPy-FD5 literal v5.2 action comparator",
        "classification": "theory_only;finite_N2;two_route_direct_variation_certificate;fail_closed_C1_N1",
        "decision": {
            "AD_vs_independent_FD5_comparator_pass": direct_pass,
            "restricted_spectral_N2_two_route_derivative_certificate_pass": direct_pass,
            "Euler_Green_independent_route_pass": False,
            "mutant_campaign_pass": False,
            "independent_clean_process_redteam_pass": False,
            "multi_N_convergence_pass": False,
            "continuous_dense_family_theorem_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "tolerances_fixed_in_comparator": {
            "central_absolute_Linf": CENTRAL_ABS_LINF_TOLERANCE,
            "central_component_relative_Linf": CENTRAL_COMPONENT_REL_TOLERANCE,
            "coarse_h4_order_interval": [H4_ORDER_MINIMUM, H4_ORDER_MAXIMUM],
            "Richardson_twenty_component_L2": RICHARDSON_COMPONENT_L2_TOLERANCE,
            "Richardson_each_component_relative": RICHARDSON_COMPONENT_REL_TOLERANCE,
        },
        "scientific": scientific,
        "source_pins": {
            "route_A": {
                "artifact_sha256": ROUTE_A_ARTIFACT_SHA256,
                "source_sha256": ROUTE_A_SOURCE_SHA256,
                "test_sha256": ROUTE_A_TEST_SHA256,
            },
            "route_B": {
                "artifact_sha256": ROUTE_B_ARTIFACT_SHA256,
                "source_sha256": ROUTE_B_SOURCE_SHA256,
                "test_sha256": ROUTE_B_TEST_SHA256,
            },
        },
        "mutant_campaign_status": {
            "output_level_omit_and_sign_mutants": "implemented_in_comparator_tests_only",
            "reexecuted_action_mutants": "pending",
            "circular_route_mutant": "rejected by byte-pinned route artifacts; clean-process audit pending",
        },
        "open_obligations": {
            "Euler_Green": "derive the bulk/interface/Robin/corner Green decomposition independently from the same literal action",
            "mutants": "reexecute BF/material/conformal/Robin/R/gluing/sign/Z2 mutants through the action evaluators",
            "multi_N": "repeat on independently generated N values with simultaneous Q, radial, and h refinement",
            "continuous_extension": "prove density, uniform stability, and continuity of the residual as N tends to infinity",
            "redteam": "regenerate and compare from a clean process without reading this comparator receipt",
            "boundary": "large gauges and BV-BFV/interface edge modes remain outside this finite certificate",
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
        "evidence_boundary": "Agreement of two independent numerical implementations of S_rel and D_xi S on one finite N2 member is now testable. This is not yet Euler-Green closure, multi-N convergence, a continuum theorem, or authorization to promote C1/N1 or open B4/B5.",
    }


def render_payload(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render_payload(payload))
    print(OUTPUT)


if __name__ == "__main__":
    main()
