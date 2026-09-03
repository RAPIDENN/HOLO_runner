#!/usr/bin/env python3
"""Freeze the v5.6.5.8 finite C2 multi-N AD/FD5 certificate by hash.

The freeze is additive: it does not rewrite any raw route or comparator.  It
copies the complete finite-difference refinement windows and renders a flat
component table so later gates can consume this exact restricted result.
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

COMPARATOR_SOURCE = HERE / "derive_one_omega_topological_so3_c2_multin_ad_fd5_sign_comparator_v5_6_5_8_gate.py"
COMPARATOR_TEST = HERE / "test_one_omega_topological_so3_c2_multin_ad_fd5_sign_comparator_v5_6_5_8_gate.py"
COMPARATOR_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_c2_multin_ad_fd5_sign_comparator_v5_6_5_8_gate.json"
ROUTE_A_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_torch_c2_multin_v5_6_5_6.json"
ROUTE_B_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.json"
TEST = HERE / "test_freeze_one_omega_topological_so3_c2_multin_ad_fd5_v5_6_5_8_restricted_certificate.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_c2_multin_ad_fd5_v5_6_5_8_restricted_certificate.json"

COMPARATOR_SOURCE_SHA256 = "13b3a551f53cc260f81d84d3af07746ab7a730cbfd5a1bfec6cb24f29a8eb9dc"
COMPARATOR_TEST_SHA256 = "630165778c3386a3cf0e1f2808b00043eeaea02eec005bd9d70be8757d07d5a1"
COMPARATOR_ARTIFACT_SHA256 = "182d80a5aeb2c73ca345feab86bd550e7d917257680c8cb56e06adbcc66be173"
ROUTE_A_ARTIFACT_SHA256 = "d0db75f97c580e417e2032211134546695691598714f0ace65db8f24afc11cdb"
ROUTE_B_ARTIFACT_SHA256 = "501d5fddba619a32a8ab6c050e536c523cbc91795813f9a837b13c9d6fb133ea"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
C2_PRIMITIVE_BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"

SCHEMA = "holo.one-omega-topological-so3-c2-multin-ad-fd5-v5-6-5-8-restricted-certificate.v1"
EXPECTED_STEPS = (0.04, 0.02, 0.01)
EXPECTED_N = (1, 2, 3)


class FreezeReceiptError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, expected: str, label: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected:
        raise FreezeReceiptError(f"{label} byte pin drift: {observed}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise FreezeReceiptError(f"{label} is not a JSON object")
    return payload


def load_inputs() -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    for path, expected, label in (
        (COMPARATOR_SOURCE, COMPARATOR_SOURCE_SHA256, "v5.6.5.8 comparator source"),
        (COMPARATOR_TEST, COMPARATOR_TEST_SHA256, "v5.6.5.8 comparator test"),
    ):
        observed = _sha256(path)
        if observed != expected:
            raise FreezeReceiptError(f"{label} byte pin drift: {observed}")
    return (
        _load(COMPARATOR_ARTIFACT, COMPARATOR_ARTIFACT_SHA256, "v5.6.5.8 comparator artifact"),
        _load(ROUTE_A_ARTIFACT, ROUTE_A_ARTIFACT_SHA256, "route A artifact"),
        _load(ROUTE_B_ARTIFACT, ROUTE_B_ARTIFACT_SHA256, "route B artifact"),
    )


def _canonical_sha256(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(blob).hexdigest()


def build_payload() -> dict[str, Any]:
    comparator, route_a, route_b = load_inputs()
    if comparator["decision"].get("AD_vs_independent_FD5_multin_pass") is not True:
        raise FreezeReceiptError("v5.6.5.8 comparator is not green")
    for payload, label in (
        (comparator, "comparator"),
        (route_a, "route A"),
        (route_b, "route B"),
    ):
        for key in ("C1_ACTION_pass", "N1_ACTION_pass", "C1_N1_promotion_authorized"):
            if payload["decision"].get(key) is not False:
                raise FreezeReceiptError(f"{label} illegally promoted {key}")

    if comparator["source_pins"].get("literal_v5_2_action_sha256") != LITERAL_V5_2_ACTION_SHA256:
        raise FreezeReceiptError("literal v5.2 action pin mismatch")
    if comparator["source_pins"].get("C2_multi_N_primitive_bundle_sha256") != C2_PRIMITIVE_BUNDLE_SHA256:
        raise FreezeReceiptError("C2 primitive bundle pin mismatch")

    comparator_rows = {
        int(row["N"]): row for row in comparator["scientific"]["member_comparisons"]
    }
    route_a_rows = {int(row["N"]): row for row in route_a["scientific"]["members"]}
    route_b_rows = {int(row["N"]): row for row in route_b["scientific"]["members"]}
    if tuple(sorted(comparator_rows)) != EXPECTED_N:
        raise FreezeReceiptError("comparator member set drift")
    if tuple(sorted(route_a_rows)) != EXPECTED_N or tuple(sorted(route_b_rows)) != EXPECTED_N:
        raise FreezeReceiptError("route member set drift")

    member_records: list[dict[str, Any]] = []
    sector_table: list[dict[str, Any]] = []
    for n_value in EXPECTED_N:
        comparison = comparator_rows[n_value]
        a_row = route_a_rows[n_value]
        b_row = route_b_rows[n_value]
        for key in (
            "member_id",
            "authoritative_free_central_sha256",
            "authoritative_free_tangent_sha256",
        ):
            if comparison[key] != a_row[key] or comparison[key] != b_row[key]:
                raise FreezeReceiptError(f"N={n_value}: {key} drift across frozen inputs")

        window = b_row["FD5_refinement_window"]
        steps = tuple(float(value) for value in window["steps"])
        derivative_steps = tuple(float(row["step"]) for row in window["derivatives"])
        if steps != EXPECTED_STEPS or derivative_steps != EXPECTED_STEPS:
            raise FreezeReceiptError(f"N={n_value}: FD5 h sweep drift")
        ad = comparison["AD_JVP"]
        fd = comparison["Richardson_FD5_h002_h001"]
        direct = comparison["direct_residual_FD5_minus_AD"]
        flipped = comparison["global_flip_residual_FD5_plus_AD"]
        relations = comparison["sign_relation_by_component"]
        orders = b_row["FD5_observed_orders"]
        components = tuple(sorted(ad))
        if not (set(ad) == set(fd) == set(direct) == set(flipped) == set(orders)):
            raise FreezeReceiptError(f"N={n_value}: component table mismatch")

        rows_for_member: list[dict[str, Any]] = []
        for component in components:
            ad_value = float(ad[component])
            fd_value = float(fd[component])
            residual = float(direct[component])
            symmetric_denominator = abs(ad_value) + abs(fd_value)
            row = {
                "N": n_value,
                "K": int(comparison["K"]),
                "component": component,
                "AD_JVP": ad_value,
                "Richardson_FD5_h002_h001": fd_value,
                "FD5_minus_AD": residual,
                "absolute_error": abs(residual),
                "relative_error_to_larger_magnitude": abs(residual)
                / max(abs(ad_value), abs(fd_value), 1.0e-300),
                "symmetric_relative_error": 0.0
                if symmetric_denominator == 0.0
                else 2.0 * abs(residual) / symmetric_denominator,
                "FD5_plus_AD_global_flip_residual": float(flipped[component]),
                "sign_relation": "total_same"
                if component == "S_total"
                and math.copysign(1.0, ad_value) == math.copysign(1.0, fd_value)
                else relations.get(component, "not_applicable"),
                "FD5_observed_order": orders[component]["observed_order"],
                "FD5_coarse_gap": float(orders[component]["coarse_gap"]),
                "FD5_fine_gap": float(orders[component]["fine_gap"]),
            }
            rows_for_member.append(row)
            sector_table.append(row)

        member_records.append(
            {
                "N": n_value,
                "K": int(comparison["K"]),
                "member_id": comparison["member_id"],
                "free_dimension": int(a_row["free_dimension"]),
                "authoritative_free_central_sha256": comparison[
                    "authoritative_free_central_sha256"
                ],
                "authoritative_free_tangent_sha256": comparison[
                    "authoritative_free_tangent_sha256"
                ],
                "central_route_A_Q5_R10": comparison["central_route_A_Q5_R10"],
                "central_route_B_Q5_R10": comparison["central_route_B_Q5_R10"],
                "central_residual_by_component": comparison[
                    "central_residual_by_component"
                ],
                "AD_FD5_diagnostics": {
                    key: comparison[key]
                    for key in (
                        "component_direct_residual_L2",
                        "component_global_flip_residual_L2",
                        "component_derivative_L2_tolerance",
                        "total_absolute_residual",
                        "total_tolerance",
                        "cosine_similarity_AD_FD5",
                        "active_sign_threshold",
                        "active_components",
                        "active_sign_mismatches",
                        "active_component_relative_residuals",
                        "global_sign_flip_hypothesis",
                        "FD5_total_observed_order",
                        "checks",
                        "pass",
                    )
                },
                "FD5_complete_h_sweep": window,
                "sector_table": rows_for_member,
            }
        )

    frozen_pins = {
        "v5_6_5_8_comparator": {
            "source_sha256": COMPARATOR_SOURCE_SHA256,
            "test_sha256": COMPARATOR_TEST_SHA256,
            "artifact_sha256": COMPARATOR_ARTIFACT_SHA256,
        },
        "route_A_artifact_sha256": ROUTE_A_ARTIFACT_SHA256,
        "route_B_artifact_sha256": ROUTE_B_ARTIFACT_SHA256,
        "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
        "C2_multi_N_primitive_bundle_sha256": C2_PRIMITIVE_BUNDLE_SHA256,
    }
    return {
        "schema": SCHEMA,
        "classification": "theory_only;frozen_restricted_certificate;finite_C2_spectral_N1_N2_N3;AD_vs_FD5;fail_closed_C1_N1",
        "decision": {
            "v5_6_5_8_restricted_AD_FD5_multin_certificate_frozen": True,
            "Euler_Green_independent_route_pass": False,
            "clean_room_full_mutant_campaign_pass": False,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "frozen_scope": {
            "spectral_members": [1, 2, 3],
            "radial_members": [1, 2, 3],
            "tangential_quadrature": "Q1 exact for N1; Q5 per axis for N2/N3",
            "radial_quadrature": "Gauss order 10",
            "FD5_steps": list(EXPECTED_STEPS),
            "claim": "componentwise equality of Torch AD and independent NumPy FD5 for the three frozen finite members",
            "exclusions": [
                "Euler-Green identity",
                "clean-room reproduction",
                "uniform spectral limit",
                "continuous C1/N1 theorem",
                "B4",
                "B5",
            ],
        },
        "tolerances_frozen_from_v5_6_5_8": comparator[
            "tolerances_fixed_in_comparator"
        ],
        "scientific": {
            "diagnosis": comparator["scientific"]["diagnosis"],
            "member_records": member_records,
            "sector_table": sector_table,
            "sector_table_sha256": _canonical_sha256(sector_table),
        },
        "frozen_input_pins": frozen_pins,
        "frozen_input_pinset_sha256": _canonical_sha256(frozen_pins),
        "immutability_contract": {
            "mode": "additive_freeze",
            "upstream_files_modified": False,
            "future_consumers_must_pin_this_receipt_by_sha256": True,
            "retrospective_reinterpretation_forbidden": True,
        },
        "remaining_gate_order": [
            "Euler_Green_independent_route",
            "clean_room_full_mutant_campaign",
            "uniform_N_to_infinity_bridge",
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
        "evidence_boundary": "This freezes only the finite N=1,2,3 C2 AD-FD5 agreement. C1/N1 and B4/B5 remain false until the independent Euler-Green route, clean-room mutant campaign, and uniform N-to-infinity bridge all pass.",
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
