#!/usr/bin/env python3
"""Compare the frozen C2 multi-N Torch/AD and NumPy/FD5 routes.

This comparator evaluates only frozen raw receipts.  It does not import either
action implementation, and it records direct and globally sign-flipped
residuals separately so that a sign error cannot be hidden by a norm-only
comparison.
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

A_SOURCE = HERE / "derive_one_omega_topological_so3_torch_c2_multin_v5_6_5_6.py"
A_TEST = HERE / "test_one_omega_topological_so3_torch_c2_multin_v5_6_5_6.py"
A_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_torch_c2_multin_v5_6_5_6.json"
B_SOURCE = HERE / "derive_one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.py"
B_TEST = HERE / "test_one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.py"
B_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.json"
TEST = HERE / "test_one_omega_topological_so3_c2_multin_ad_fd5_sign_comparator_v5_6_5_8_gate.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_c2_multin_ad_fd5_sign_comparator_v5_6_5_8_gate.json"

A_SOURCE_SHA256 = "2c3fb9adbaad90a77fd5cf1fd7df9bd61c2e4d1e92dbffeff4f3ffaa31ab7f6b"
A_TEST_SHA256 = "6600fe91723b48c6b1ecb47bf96d67152d46c0c40f75f6717b2017e60f4302a0"
A_ARTIFACT_SHA256 = "d0db75f97c580e417e2032211134546695691598714f0ace65db8f24afc11cdb"
B_SOURCE_SHA256 = "009d889861eb7679e2297de0fc863118c74c00e479518e601ac49057a996bf76"
B_TEST_SHA256 = "4b534cff9d073b4d52a2f4377abc97fddc7dd9321a9b4a423aa0190446eda482"
B_ARTIFACT_SHA256 = "501d5fddba619a32a8ab6c050e536c523cbc91795813f9a837b13c9d6fb133ea"
C2_PRIMITIVE_BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"

SCHEMA = "holo.one-omega-topological-so3-c2-multin-ad-fd5-sign-comparator-v5-6-5-8.v1"
EXPECTED_N = (1, 2, 3)

# These acceptance constants are local to this comparator.  Neither raw route
# contains or supplies the comparator tolerances.
CENTRAL_COMPONENT_L2_ABS_FLOOR = 2.0e-9
CENTRAL_COMPONENT_L2_REL_COEFFICIENT = 2.0e-12
DERIVATIVE_COMPONENT_L2_ABS_FLOOR = 2.0e-8
DERIVATIVE_COMPONENT_L2_REL_COEFFICIENT = 2.0e-10
TOTAL_ABS_FLOOR = 2.0e-8
TOTAL_REL_COEFFICIENT = 2.0e-10
ACTIVE_SIGN_ABS_FLOOR = 1.0e-12
ACTIVE_COMPONENT_FRACTION = 1.0e-10
ACTIVE_COMPONENT_REL_TOLERANCE = 1.0e-7
COSINE_SIMILARITY_MINIMUM = 1.0 - 1.0e-12
GLOBAL_FLIP_DISCRIMINATION_FACTOR = 10.0
TOTAL_FD5_ORDER_MINIMUM = 3.5
REFINEMENT_ROUNDOFF_ALLOWANCE = 1.0e-13


class SignComparatorError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, expected_sha256: str, label: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise SignComparatorError(f"{label} byte pin drift: {observed}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SignComparatorError(f"{label} is not a JSON object")
    return payload


def load_inputs() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    for path, expected, label in (
        (A_SOURCE, A_SOURCE_SHA256, "route A source"),
        (A_TEST, A_TEST_SHA256, "route A test"),
        (B_SOURCE, B_SOURCE_SHA256, "route B source"),
        (B_TEST, B_TEST_SHA256, "route B test"),
    ):
        observed = _sha256(path)
        if observed != expected:
            raise SignComparatorError(f"{label} byte pin drift: {observed}")
    return (
        _load(A_ARTIFACT, A_ARTIFACT_SHA256, "route A artifact"),
        _load(B_ARTIFACT, B_ARTIFACT_SHA256, "route B artifact"),
    )


def _float_map(raw: Mapping[str, Any], label: str) -> dict[str, float]:
    values = {str(key): float(value) for key, value in raw.items()}
    if not values or any(not math.isfinite(value) for value in values.values()):
        raise SignComparatorError(f"{label} contains missing or non-finite values")
    return values


def _l2(values: Mapping[str, float], components: tuple[str, ...]) -> float:
    return math.sqrt(math.fsum(values[name] ** 2 for name in components))


def _sign_relation(ad: float, fd: float, threshold: float) -> str:
    if max(abs(ad), abs(fd)) < threshold:
        return "inactive_below_threshold"
    if min(abs(ad), abs(fd)) < threshold:
        return "one_route_near_zero"
    return "same" if math.copysign(1.0, ad) == math.copysign(1.0, fd) else "opposite"


def analyze(route_a: Mapping[str, Any], route_b: Mapping[str, Any]) -> Mapping[str, Any]:
    if route_a["decision"].get("route_A_C2_multin_raw_evaluations_pass") is not True:
        raise SignComparatorError("route A raw evaluation is red")
    if route_b["decision"].get("route_B_C2_multin_raw_evaluations_pass") is not True:
        raise SignComparatorError("route B raw evaluation is red")
    for payload, label in ((route_a, "route A"), (route_b, "route B")):
        for key in ("C1_ACTION_pass", "N1_ACTION_pass", "C1_N1_promotion_authorized"):
            if payload["decision"].get(key) is not False:
                raise SignComparatorError(f"{label} illegally promoted {key}")
        pins = payload["source_pins"]
        if pins.get("C2_multi_N_primitive_bundle_sha256") != C2_PRIMITIVE_BUNDLE_SHA256:
            raise SignComparatorError(f"{label} C2 primitive bundle pin mismatch")
        if pins.get("literal_v5_2_action_sha256") != LITERAL_V5_2_ACTION_SHA256:
            raise SignComparatorError(f"{label} literal v5.2 action pin mismatch")

    rows_a = {int(row["N"]): row for row in route_a["scientific"]["members"]}
    rows_b = {int(row["N"]): row for row in route_b["scientific"]["members"]}
    if tuple(sorted(rows_a)) != EXPECTED_N or tuple(sorted(rows_b)) != EXPECTED_N:
        raise SignComparatorError("expected exactly the N=1,2,3 members")

    comparisons: list[dict[str, Any]] = []
    for n_value in EXPECTED_N:
        row_a = rows_a[n_value]
        row_b = rows_b[n_value]
        for key in (
            "K",
            "member_id",
            "authoritative_free_central_sha256",
            "authoritative_free_tangent_sha256",
        ):
            if row_a[key] != row_b[key]:
                raise SignComparatorError(f"N={n_value}: primitive identity mismatch for {key}")

        central_a = _float_map(
            row_a["central_S_rel_components_by_radial_order"]["10"],
            f"N={n_value} route A central action",
        )
        central_b = _float_map(
            row_b["central_S_rel_components"], f"N={n_value} route B central action"
        )
        ad = _float_map(
            row_a["AD_JVP_by_component_at_Q5_R10"], f"N={n_value} route A AD"
        )
        fd = _float_map(
            row_b["FD5_Richardson_h002_h001"], f"N={n_value} route B FD5"
        )
        if set(central_a) != set(central_b):
            raise SignComparatorError(f"N={n_value}: central action component set mismatch")
        if set(ad) != set(fd) or "S_total" not in ad:
            raise SignComparatorError(f"N={n_value}: derivative component set mismatch")

        components = tuple(sorted(name for name in ad if name != "S_total"))
        central_residual = {
            name: central_b[name] - central_a[name] for name in central_a
        }
        direct_residual = {name: fd[name] - ad[name] for name in ad}
        flipped_residual = {name: fd[name] + ad[name] for name in ad}

        central_l2 = _l2(central_residual, components)
        central_scale = max(_l2(central_a, components), _l2(central_b, components), 1.0)
        central_tolerance = (
            CENTRAL_COMPONENT_L2_ABS_FLOOR
            + CENTRAL_COMPONENT_L2_REL_COEFFICIENT * central_scale
        )
        ad_l2 = _l2(ad, components)
        fd_l2 = _l2(fd, components)
        direct_l2 = _l2(direct_residual, components)
        flipped_l2 = _l2(flipped_residual, components)
        derivative_tolerance = (
            DERIVATIVE_COMPONENT_L2_ABS_FLOOR
            + DERIVATIVE_COMPONENT_L2_REL_COEFFICIENT * max(ad_l2, fd_l2, 1.0)
        )
        dot = math.fsum(ad[name] * fd[name] for name in components)
        cosine = dot / (ad_l2 * fd_l2)
        cosine = min(1.0, max(-1.0, cosine))

        component_scale = max(
            1.0, max(max(abs(ad[name]), abs(fd[name])) for name in components)
        )
        active_threshold = max(
            ACTIVE_SIGN_ABS_FLOOR, ACTIVE_COMPONENT_FRACTION * component_scale
        )
        sign_relations = {
            name: _sign_relation(ad[name], fd[name], active_threshold)
            for name in components
        }
        active_components = tuple(
            name
            for name in components
            if sign_relations[name] != "inactive_below_threshold"
        )
        sign_mismatches = tuple(
            name for name in active_components if sign_relations[name] != "same"
        )
        active_relative_residuals = {
            name: abs(direct_residual[name])
            / max(abs(ad[name]), abs(fd[name]), 1.0e-300)
            for name in active_components
        }

        total_tolerance = TOTAL_ABS_FLOOR + TOTAL_REL_COEFFICIENT * max(
            abs(ad["S_total"]), abs(fd["S_total"]), 1.0
        )
        total_order = float(row_b["FD5_observed_orders"]["S_total"]["observed_order"])
        contracting_components = {
            name: (
                float(record["fine_gap"])
                <= float(record["coarse_gap"]) + REFINEMENT_ROUNDOFF_ALLOWANCE
            )
            for name, record in row_b["FD5_observed_orders"].items()
        }
        global_flip_hypothesis = flipped_l2 * GLOBAL_FLIP_DISCRIMINATION_FACTOR < direct_l2
        global_flip_rejected = flipped_l2 > (
            GLOBAL_FLIP_DISCRIMINATION_FACTOR * max(direct_l2, 1.0e-300)
        )
        checks = {
            "central_component_vector_agrees": central_l2 <= central_tolerance,
            "derivative_component_vector_agrees": direct_l2 <= derivative_tolerance,
            "total_derivative_agrees": abs(direct_residual["S_total"]) <= total_tolerance,
            "all_active_component_signs_agree": bool(active_components)
            and not sign_mismatches,
            "all_active_component_relative_residuals_pass": bool(active_components)
            and max(active_relative_residuals.values()) <= ACTIVE_COMPONENT_REL_TOLERANCE,
            "cosine_has_same_orientation": cosine >= COSINE_SIMILARITY_MINIMUM,
            "global_sign_flip_rejected": global_flip_rejected and not global_flip_hypothesis,
            "FD5_total_fourth_order_window_pass": total_order >= TOTAL_FD5_ORDER_MINIMUM,
            "FD5_all_component_gaps_nonexpanding": all(contracting_components.values()),
        }
        comparisons.append(
            {
                "N": n_value,
                "K": int(row_a["K"]),
                "member_id": row_a["member_id"],
                "authoritative_free_central_sha256": row_a[
                    "authoritative_free_central_sha256"
                ],
                "authoritative_free_tangent_sha256": row_a[
                    "authoritative_free_tangent_sha256"
                ],
                "central_route_A_Q5_R10": central_a,
                "central_route_B_Q5_R10": central_b,
                "central_residual_by_component": central_residual,
                "central_component_residual_L2": central_l2,
                "central_component_L2_tolerance": central_tolerance,
                "AD_JVP": ad,
                "Richardson_FD5_h002_h001": fd,
                "direct_residual_FD5_minus_AD": direct_residual,
                "global_flip_residual_FD5_plus_AD": flipped_residual,
                "component_direct_residual_L2": direct_l2,
                "component_global_flip_residual_L2": flipped_l2,
                "component_derivative_L2_tolerance": derivative_tolerance,
                "total_absolute_residual": abs(direct_residual["S_total"]),
                "total_tolerance": total_tolerance,
                "cosine_similarity_AD_FD5": cosine,
                "active_sign_threshold": active_threshold,
                "sign_relation_by_component": sign_relations,
                "active_components": list(active_components),
                "active_sign_mismatches": list(sign_mismatches),
                "active_component_relative_residuals": active_relative_residuals,
                "global_sign_flip_hypothesis": global_flip_hypothesis,
                "FD5_total_observed_order": total_order,
                "FD5_component_gap_contracts_or_roundoff": contracting_components,
                "checks": checks,
                "pass": all(checks.values()),
            }
        )

    checks = {
        "frozen_route_A_and_B_bytes_loaded": True,
        "same_literal_v5_2_action_and_C2_primitive_bundle": True,
        "same_N_K_member_centers_and_tangents": True,
        "all_N1_N2_N3_AD_vs_FD5_sign_diagnostics_pass": all(
            row["pass"] for row in comparisons
        ),
        "no_global_sign_flip_detected": not any(
            row["global_sign_flip_hypothesis"] for row in comparisons
        ),
        "no_active_sector_sign_mismatch_detected": not any(
            row["active_sign_mismatches"] for row in comparisons
        ),
    }
    return {
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "diagnosis": {
            "current_C2_route_relation": "same_orientation_componentwise",
            "global_action_sign_error": "excluded_for_the_three_frozen_finite_members",
            "sector_sign_error": "not_detected_in_any_active_published_component",
            "scope_warning": "This comparison does not evaluate Euler-Green closure or the continuous limit.",
        },
        "member_comparisons": comparisons,
    }


def build_payload() -> dict[str, Any]:
    route_a, route_b = load_inputs()
    scientific = analyze(route_a, route_b)
    passed = bool(scientific["all_checks_pass"])
    comparisons = scientific["member_comparisons"]
    global_sign_error = any(row["global_sign_flip_hypothesis"] for row in comparisons)
    sector_sign_error = any(row["active_sign_mismatches"] for row in comparisons)
    return {
        "schema": SCHEMA,
        "classification": "theory_only;finite_C2_spectral_members;AD_vs_independent_FD5;sign_diagnostic;fail_closed_C1_N1",
        "decision": {
            "AD_vs_independent_FD5_multin_pass": passed,
            "global_action_sign_error_detected": global_sign_error,
            "active_sector_sign_error_detected": sector_sign_error,
            "Euler_Green_independent_route_pass": False,
            "independent_clean_process_redteam_pass": False,
            "uniform_spectral_limit_pass": False,
            "continuous_limit_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "tolerances_fixed_in_comparator": {
            "central_component_L2_abs_floor": CENTRAL_COMPONENT_L2_ABS_FLOOR,
            "central_component_L2_relative_coefficient": CENTRAL_COMPONENT_L2_REL_COEFFICIENT,
            "derivative_component_L2_abs_floor": DERIVATIVE_COMPONENT_L2_ABS_FLOOR,
            "derivative_component_L2_relative_coefficient": DERIVATIVE_COMPONENT_L2_REL_COEFFICIENT,
            "total_abs_floor": TOTAL_ABS_FLOOR,
            "total_relative_coefficient": TOTAL_REL_COEFFICIENT,
            "active_sign_abs_floor": ACTIVE_SIGN_ABS_FLOOR,
            "active_component_fraction": ACTIVE_COMPONENT_FRACTION,
            "active_component_relative_tolerance": ACTIVE_COMPONENT_REL_TOLERANCE,
            "cosine_similarity_minimum": COSINE_SIMILARITY_MINIMUM,
            "global_flip_discrimination_factor": GLOBAL_FLIP_DISCRIMINATION_FACTOR,
            "total_FD5_order_minimum": TOTAL_FD5_ORDER_MINIMUM,
            "refinement_roundoff_allowance": REFINEMENT_ROUNDOFF_ALLOWANCE,
        },
        "scientific": scientific,
        "source_pins": {
            "route_A": {
                "source_sha256": A_SOURCE_SHA256,
                "test_sha256": A_TEST_SHA256,
                "artifact_sha256": A_ARTIFACT_SHA256,
            },
            "route_B": {
                "source_sha256": B_SOURCE_SHA256,
                "test_sha256": B_TEST_SHA256,
                "artifact_sha256": B_ARTIFACT_SHA256,
            },
            "C2_multi_N_primitive_bundle_sha256": C2_PRIMITIVE_BUNDLE_SHA256,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
        },
        "open_obligations": {
            "Euler_Green": "derive and compare the bulk, interface, Robin, corner, Green, and gluing decomposition independently",
            "redteam": "regenerate from a clean process without reading the primary receipt",
            "spectral_limit": "show uniform stability and controlled convergence as N and K increase",
            "continuum": "prove density and continuity of the variational residual in the declared function space",
            "promotion": "C1/N1 remain false until every scoped obligation and independent audit passes",
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
        "evidence_boundary": "For the three frozen finite C2 spectral members only, Torch AD and independently implemented NumPy FD5 agree componentwise with the same sign. This is not Euler-Green closure, a full tangent-space theorem, a continuum theorem, or C1/N1 promotion.",
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
