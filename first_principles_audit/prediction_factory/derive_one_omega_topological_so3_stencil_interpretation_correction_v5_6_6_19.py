#!/usr/bin/env python3
"""Fail-closed reinterpretation of the byte-pinned v5.6.6.12 ladders.

This additive receipt does not rerun Route C.  It fixes two evidence-boundary
problems in the frozen v5.6.6.12 receipt:

* a noncontractive three-step ladder does not contradict a stencil's formal
  order and does not certify roundoff dominance; and
* the selected K<=3 pulled-back *field channels* are degree <=8 in rho, so the
  radial D1/D2 stencils are exact in exact arithmetic under the evaluator's
  polynomial-continuation oracle.  This does not make the nonlinear density,
  action, radial quadrature, or the theta leg of qtr exact.

The receipt also pins the later v5.6.6.13 whole-collar margin certificate so a
red historical v5.6.6.11 key cannot be misread as a refutation.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"

V12_SOURCE = HERE / "derive_one_omega_topological_so3_route_c_stencil_bias_v5_6_6_12.py"
V12_TEST = HERE / "test_one_omega_topological_so3_route_c_stencil_bias_v5_6_6_12.py"
V12_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_route_c_stencil_bias_v5_6_6_12.json"
V13_SOURCE = HERE / "derive_one_omega_topological_so3_pinned_members_margins_everywhere_weyl_lipschitz_v5_6_6_13.py"
V13_TEST = HERE / "test_one_omega_topological_so3_pinned_members_margins_everywhere_weyl_lipschitz_v5_6_6_13.py"
V13_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_pinned_members_margins_everywhere_weyl_lipschitz_v5_6_6_13.json"
PRECISION_SOURCE = HERE / "derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5.py"

TEST = HERE / "test_one_omega_topological_so3_stencil_interpretation_correction_v5_6_6_19.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_stencil_interpretation_correction_v5_6_6_19.json"

V12_SOURCE_SHA256 = "544b23cbb3052e83ce58b34ee175a73cb3f120ca8b4ac18b820d00d25defc862"
V12_TEST_SHA256 = "b7109480bee0a5a66ef59d0c7c7d951ed5eb1e41966f234f4394a7fca5424fae"
V12_ARTIFACT_SHA256 = "2c7c170b1e23fb32cb2c53c9d232069e3a8100c2950ebe9206813c6a5809ab23"
V12_PRODUCER_COMMIT = "da7a8269286bdd228753dfa4d7a381516778e9d6"
V13_SOURCE_SHA256 = "ffae8313cde809bf2a65a431677e41f330c6f802085b1decb07a029868cd4ae3"
V13_TEST_SHA256 = "288d910159efc71ef683737e1d86c3a9407cdaa2a738507e4cd21dbaa6579d44"
V13_ARTIFACT_SHA256 = "4051ecc137da00aedc8bd7acc613a4f341f3f48f218804291406ba46dc730a21"
V13_PRODUCER_COMMIT = "270f8d73e8708fe0acbd5eecee46d5ea44a1547b"
PRECISION_SOURCE_SHA256 = "5cf9c64fe8af45b55899275b2af1a9d55c706a138479e2cbd3a47ca4b270eca8"

V12_SCHEMA = "holo.one-omega-topological-so3-route-c-stencil-bias-v5-6-6-12.v1"
V13_SCHEMA = "holo.one-omega-topological-so3-pinned-members-margins-everywhere-weyl-lipschitz-v5-6-6-13.v1"
SCHEMA = "holo.one-omega-topological-so3-stencil-interpretation-correction-v5-6-6-19.v1"

EXPECTED_MEMBERS = ((1, 1), (2, 2), (3, 3))
AXES = ("free", "theta", "rho")
RADIAL_ORDER = 10
RADIAL_STEPS = (6.0e-2, 3.0e-2, 1.5e-2)


class StencilInterpretationCorrectionError(RuntimeError):
    """A frozen receipt, exact ledger, or correction contract drifted."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def _read_pinned(path: Path, expected_hash: str, expected_schema: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected_hash:
        raise StencilInterpretationCorrectionError(
            f"byte pin drift for {path.name}: expected {expected_hash}, observed {observed}"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != expected_schema:
        raise StencilInterpretationCorrectionError(f"schema drift for {path.name}")
    return payload


def load_inputs() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    for path, expected in (
        (V12_SOURCE, V12_SOURCE_SHA256),
        (V12_TEST, V12_TEST_SHA256),
        (V13_SOURCE, V13_SOURCE_SHA256),
        (V13_TEST, V13_TEST_SHA256),
        (PRECISION_SOURCE, PRECISION_SOURCE_SHA256),
    ):
        observed = _sha256(path)
        if observed != expected:
            raise StencilInterpretationCorrectionError(
                f"source/test pin drift for {path.name}: {observed}"
            )
    v12 = _read_pinned(V12_ARTIFACT, V12_ARTIFACT_SHA256, V12_SCHEMA)
    v13 = _read_pinned(V13_ARTIFACT, V13_ARTIFACT_SHA256, V13_SCHEMA)
    if v12["decision"].get("stencil_step_ladders_measured_pass") is not True:
        raise StencilInterpretationCorrectionError("v5.6.6.12 ladder receipt is not green")
    if v12["decision"].get("B_FD_rigorous_bound_pass") is not False:
        raise StencilInterpretationCorrectionError("v5.6.6.12 B_FD bound must remain false")
    if v13["decision"].get("pinned_members_margins_everywhere_certified_pass") is not True:
        raise StencilInterpretationCorrectionError("v5.6.6.13 margin receipt is not green")
    return v12, v13


def _trim(poly: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    values = list(poly)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def _poly_add(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    size = max(len(left), len(right))
    return _trim(
        tuple(
            (left[index] if index < len(left) else Fraction(0))
            + (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        )
    )


def _poly_scale(poly: tuple[Fraction, ...], scale: Fraction) -> tuple[Fraction, ...]:
    return _trim(tuple(scale * coefficient for coefficient in poly))


def _poly_mul(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return _trim(tuple(result))


def _poly_pow(poly: tuple[Fraction, ...], power: int) -> tuple[Fraction, ...]:
    result = (Fraction(1),)
    for _ in range(power):
        result = _poly_mul(result, poly)
    return result


def _degree(poly: tuple[Fraction, ...]) -> int:
    return len(_trim(poly)) - 1


def radial_profile_degree_certificate() -> Mapping[str, Any]:
    rho = (Fraction(0), Fraction(1))
    one_minus_rho = (Fraction(1), Fraction(-1))
    x = (Fraction(-1), Fraction(2))
    envelope = _poly_scale(
        _poly_mul(_poly_pow(rho, 3), _poly_pow(one_minus_rho, 3)), Fraction(64)
    )
    legendre = [(Fraction(1),), x]
    for degree in range(1, 7):
        following = _poly_scale(
            _poly_add(
                _poly_scale(_poly_mul(x, legendre[degree]), Fraction(2 * degree + 1)),
                _poly_scale(legendre[degree - 1], Fraction(-degree)),
            ),
            Fraction(1, degree + 1),
        )
        legendre.append(following)
    h0 = (
        Fraction(1),
        Fraction(0),
        Fraction(0),
        Fraction(-10),
        Fraction(15),
        Fraction(-6),
    )
    h1 = _poly_mul(rho, h0)
    bumps = tuple(_poly_mul(envelope, polynomial) for polynomial in legendre)
    degrees = {
        "h0": _degree(h0),
        "h1": _degree(h1),
        "b0": _degree(bumps[0]),
        "b1": _degree(bumps[1]),
        "b2": _degree(bumps[2]),
    }
    expected = {"h0": 5, "h1": 6, "b0": 6, "b1": 7, "b2": 8}
    return {
        "exact_fraction_coefficients": {
            "h0": [str(value) for value in h0],
            "h1": [str(value) for value in h1],
            "bumps_K_le_3": [[str(value) for value in poly] for poly in bumps[:3]],
        },
        "degrees": degrees,
        "expected_degrees": expected,
        "selected_K_le_3_degree_le_8_pass": bool(degrees == expected),
        "same_profile_formula_beyond_selected_campaign": {
            "b3_degree_if_K_at_least_4": _degree(bumps[3]),
            "b7_degree_if_K_equals_8": _degree(bumps[7]),
            "K_le_8_degree_le_8": False,
        },
    }


def radial_stencil_moment_certificate() -> Mapping[str, Any]:
    formulas = {
        "D1": {
            "derivative_order": 1,
            "weights": {
                -4: Fraction(1, 280),
                -3: Fraction(-4, 105),
                -2: Fraction(1, 5),
                -1: Fraction(-4, 5),
                1: Fraction(4, 5),
                2: Fraction(-1, 5),
                3: Fraction(4, 105),
                4: Fraction(-1, 280),
            },
        },
        "D2": {
            "derivative_order": 2,
            "weights": {
                -4: Fraction(-1, 560),
                -3: Fraction(8, 315),
                -2: Fraction(-1, 5),
                -1: Fraction(8, 5),
                0: Fraction(-205, 72),
                1: Fraction(8, 5),
                2: Fraction(-1, 5),
                3: Fraction(8, 315),
                4: Fraction(-1, 560),
            },
        },
    }
    rows: dict[str, Any] = {}
    for name, formula in formulas.items():
        derivative_order = int(formula["derivative_order"])
        weights = formula["weights"]
        moments = {
            degree: sum(
                coefficient * Fraction(offset) ** degree
                for offset, coefficient in weights.items()
            )
            for degree in range(11)
        }
        expected = {
            degree: (
                Fraction(math.factorial(derivative_order))
                if degree == derivative_order
                else Fraction(0)
            )
            for degree in moments
        }
        exact_degrees = [degree for degree in moments if moments[degree] == expected[degree]]
        first_failure = next(
            (degree for degree in moments if moments[degree] != expected[degree]), None
        )
        rows[name] = {
            "derivative_order": derivative_order,
            "moments_0_through_10": {
                str(degree): str(value) for degree, value in moments.items()
            },
            "exact_degrees": exact_degrees,
            "first_failure_degree": first_failure,
            "first_failure_moment": (
                str(moments[first_failure]) if first_failure is not None else None
            ),
            "exact_through_selected_degree_8_pass": all(
                moments[degree] == expected[degree] for degree in range(9)
            ),
        }
    return {
        "rows": rows,
        "D1_and_D2_exact_through_selected_degree_8_pass": all(
            row["exact_through_selected_degree_8_pass"] for row in rows.values()
        ),
    }


def fd5_moment_certificate() -> Mapping[str, Any]:
    weights = {
        -2: Fraction(1, 12),
        -1: Fraction(-8, 12),
        1: Fraction(8, 12),
        2: Fraction(-1, 12),
    }
    moments = {
        degree: sum(
            coefficient * Fraction(offset) ** degree
            for offset, coefficient in weights.items()
        )
        for degree in range(6)
    }
    expected = {
        degree: Fraction(1) if degree == 1 else Fraction(0)
        for degree in moments
    }
    return {
        "moments_0_through_5": {
            str(degree): str(value) for degree, value in moments.items()
        },
        "exact_through_degree_4_pass": all(
            moments[degree] == expected[degree] for degree in range(5)
        ),
        "first_failure_degree": 5,
        "first_failure_moment": str(moments[5]),
        "formal_order": 4,
    }


def pinned_pullback_radial_structure_static_audit() -> Mapping[str, Any]:
    source = PRECISION_SOURCE.read_text(encoding="utf-8")
    required_fragments = (
        "def _ambient_value_ld(",
        "trace, Y, Y_theta = _trace_ambient_value_ld(",
        "value = reference + h0 * (trace - reference) + h1 * jet",
        "value = value + np.sum(bumps[:, None] * interior, axis=0, dtype=LD)",
        "def _pullback_vector_ld(",
        "jacobian[4, :4] = Y_gradient",
        "jacobian[4, 4] = sign",
        "pulled_metric = jacobian.T @ metric @ jacobian",
        "pulled_connection = jacobian.T @ connection",
        "minor = jacobian[np.ix_(source, target)]",
    )
    missing = [fragment for fragment in required_fragments if fragment not in source]
    return {
        "precision_source_sha256": _sha256(PRECISION_SOURCE),
        "required_source_fragments": list(required_fragments),
        "missing_fragments": missing,
        "abstract_degree_propagation": {
            "trace_jet_interior_reference_rho_degree": 0,
            "maximum_profile_degree_for_K_le_3": 8,
            "pullback_jacobian_rho_degree": 0,
            "metric_connection_B_pullbacks_are_linear_in_fields_for_fixed_jacobian": True,
            "maximum_pulled_field_channel_rho_degree": 8,
        },
        "pass": not missing,
        "scope": "static audit of the byte-pinned source plus abstract polynomial-degree propagation; not a symbolic audit of the downstream nonlinear densities",
    }


def fd5_negative_order_exact_counterexample() -> Mapping[str, Any]:
    h0 = Fraction(1)

    def function(value: Fraction) -> Fraction:
        return 903 * value**5 - 44 * value**7

    def fd5(step: Fraction) -> Fraction:
        return (
            function(-2 * step)
            - 8 * function(-step)
            + 8 * function(step)
            - function(2 * step)
        ) / (12 * step)

    coarse = fd5(2 * h0)
    production = fd5(h0)
    fine = fd5(h0 / 2)
    coarse_gap = coarse - production
    fine_gap = production - fine
    absolute_ratio = abs(coarse_gap) / abs(fine_gap)
    observed_power_exact = Fraction(-1) if absolute_ratio == Fraction(1, 2) else None
    return {
        "function": "f(t)=903*t^5-44*t^7 at h0=1",
        "exact_derivative_at_zero": "0",
        "formal_FD5_order": 4,
        "D_2h": str(coarse),
        "D_h": str(production),
        "D_h_over_2": str(fine),
        "D_2h_minus_D_h": str(coarse_gap),
        "D_h_minus_D_h_over_2": str(fine_gap),
        "absolute_gap_ratio": str(absolute_ratio),
        "observed_power_exact": (
            str(observed_power_exact) if observed_power_exact is not None else None
        ),
        "observed_order_log2_ratio": math.log2(float(absolute_ratio)),
        "gap_signs_are_opposite": coarse_gap * fine_gap < 0,
        "exact_arithmetic_no_roundoff": True,
        "negative_order_without_roundoff_pass": bool(
            observed_power_exact == Fraction(-1)
            and coarse_gap * fine_gap < 0
            and coarse == Fraction(-1472)
            and production == Fraction(-2732)
            and fine == Fraction(-212)
        ),
    }


def classify_ladder_row(row: Mapping[str, Any]) -> Mapping[str, Any]:
    assessed = bool(row["assessed_above_resolution_floor"])
    supported = bool(row["formal_order_supported_on_this_component"])
    observed = row["observed_order_log2_ratio"]
    same_sign = row["same_leading_error_sign"]
    lower, upper = (float(value) for value in row["formal_order_window"])
    if not assessed:
        label = "below_heuristic_fixed_screening_floor"
    elif supported:
        label = "formal_order_window_supported"
    elif observed is None:
        label = "formal_order_not_supported_indeterminate_gap_pattern"
    elif float(observed) <= 0.0:
        label = "noncontractive_gap_pattern_roundoff_compatible_not_diagnostic"
    elif same_sign is False:
        label = "sign_changing_preasymptotic_or_noise_pattern"
    elif float(observed) < lower:
        label = "lower_order_or_preasymptotic_pattern"
    elif float(observed) > upper:
        label = "higher_order_or_cancellation_pattern"
    else:
        label = "formal_order_not_supported_indeterminate_gap_pattern"
    return {
        "heuristic_fixed_screening_floor": float(row["resolution_floor"]),
        "above_heuristic_fixed_screening_floor": assessed,
        "observed_order_log2_ratio": observed,
        "same_leading_error_sign": same_sign,
        "formal_order_window": [lower, upper],
        "formal_order_supported_on_this_component": supported,
        "classification": label,
        "roundoff_compatible": bool(
            assessed and observed is not None and float(observed) <= 0.0
        ),
        "roundoff_dominance_certified": False,
        "Richardson_estimate_eligible": bool(row["Richardson_estimate_eligible"]),
    }


def reinterpret_ladders(v12: Mapping[str, Any]) -> Mapping[str, Any]:
    members = []
    for member in v12["scientific"]["members"]:
        axes: dict[str, Any] = {}
        for axis in AXES:
            old = member["axis_ladders"][axis]
            rows = {
                name: classify_ladder_row(row) for name, row in old["rows"].items()
            }
            not_supported = [
                name
                for name, row in rows.items()
                if row["above_heuristic_fixed_screening_floor"]
                and not row["formal_order_supported_on_this_component"]
            ]
            legacy = list(old["contradicted_components"])
            if not_supported != legacy:
                raise StencilInterpretationCorrectionError(
                    f"lossless ladder relabel failed for N={member['N']} axis={axis}"
                )
            axes[axis] = {
                "formal_order": int(old["formal_order"]),
                "rows": rows,
                "fixed_floor_assessed_component_count": sum(
                    row["above_heuristic_fixed_screening_floor"]
                    for row in rows.values()
                ),
                "formal_order_not_supported_components": not_supported,
                "legacy_contradicted_components_equal_new_ledger_pass": True,
                "all_fixed_floor_assessed_components_support_formal_order_pass": not not_supported,
                "asymptotic_window_observed_pass": bool(
                    old["asymptotic_window_observed_pass"]
                ),
                "roundoff_dominance_certified_pass": False,
            }
        members.append(
            {
                "N": int(member["N"]),
                "K": int(member["K"]),
                "member_id": member["member_id"],
                "axis_ladders_reinterpreted": axes,
            }
        )
    if [(row["N"], row["K"]) for row in members] != list(EXPECTED_MEMBERS):
        raise StencilInterpretationCorrectionError("v5.6.6.12 member lineage drift")
    return {
        "members": members,
        "summary": {
            axis: {
                "fixed_floor_assessed_counts": [
                    member["axis_ladders_reinterpreted"][axis][
                        "fixed_floor_assessed_component_count"
                    ]
                    for member in members
                ],
                "formal_order_not_supported_components_by_N": {
                    str(member["N"]): member["axis_ladders_reinterpreted"][axis][
                        "formal_order_not_supported_components"
                    ]
                    for member in members
                },
            }
            for axis in AXES
        },
    }


def radial_stencil_reach_ledger() -> Mapping[str, Any]:
    raw_nodes, _weights = np.polynomial.legendre.leggauss(RADIAL_ORDER)
    nodes = 0.5 * (raw_nodes + 1.0)
    rows = {}
    for step in RADIAL_STEPS:
        rows[str(step)] = {
            "bulk_GL10_reach": [
                float(np.min(nodes) - 4.0 * step),
                float(np.max(nodes) + 4.0 * step),
            ],
            "GHY_rho0_reach": [-4.0 * step, 4.0 * step],
        }
    return {
        "radial_order": RADIAL_ORDER,
        "rows": rows,
        "evaluator_behavior": "the stabilized evaluator algebraically continues h0, h1 and the Legendre bumps outside [0,1]",
        "declared_class_behavior": "the C2 family contract is stated on [0,1], fixes the reference/zero extension for rho>=1, and does not authorize the negative-rho values reached across the interface",
        "semantics_match_outside_collar": False,
    }


def v13_margin_scope_audit(v13: Mapping[str, Any]) -> Mapping[str, Any]:
    source = V13_SOURCE.read_text(encoding="utf-8")
    domain_fragments = (
        "def polynomial_sup_on_unit_interval(",
        "rho_grid = np.linspace(0.0, 1.0, RHO_GRID)",
    )
    rounding = v13["scientific"]["method"]["rounding"]
    return {
        "artifact_sha256": V13_ARTIFACT_SHA256,
        "producer_commit": V13_PRODUCER_COMMIT,
        "pinned_members_margins_everywhere_certified_pass": v13["decision"][
            "pinned_members_margins_everywhere_certified_pass"
        ],
        "certified_rho_domain": [0.0, 1.0],
        "domain_source_fragments_present_pass": all(
            fragment in source for fragment in domain_fragments
        ),
        "extended_radial_stencil_reach_certified": False,
        "interval_rounding_enclosure_pass": False,
        "rounding_scope": rounding,
        "optional_interval_arithmetic_hardening": v13["open_obligation"][
            "interval_arithmetic"
        ],
    }


def build_payload() -> Mapping[str, Any]:
    v12, v13 = load_inputs()
    reinterpretation = reinterpret_ladders(v12)
    counterexample = fd5_negative_order_exact_counterexample()
    fd5_moments = fd5_moment_certificate()
    profiles = radial_profile_degree_certificate()
    moments = radial_stencil_moment_certificate()
    source_audit = pinned_pullback_radial_structure_static_audit()
    reach = radial_stencil_reach_ledger()
    v13_scope = v13_margin_scope_audit(v13)
    rho_counts = reinterpretation["summary"]["rho"]["fixed_floor_assessed_counts"]
    if rho_counts != [0, 0, 0]:
        raise StencilInterpretationCorrectionError("pinned rho ladder screening changed")
    radial_channel_exact = bool(
        profiles["selected_K_le_3_degree_le_8_pass"]
        and moments["D1_and_D2_exact_through_selected_degree_8_pass"]
        and source_audit["pass"]
    )
    scientific = {
        "v5_6_6_12_ladder_reinterpretation": reinterpretation,
        "negative_observed_order_exact_counterexample": {
            "FD5_moment_certificate": fd5_moments,
            "ladder": counterexample,
        },
        "radial_field_channel_exactness": {
            "profile_degree_certificate": profiles,
            "stencil_moment_certificate": moments,
            "pinned_pullback_source_audit": source_audit,
            "D1_qr_field_channel_truncation_zero_in_exact_arithmetic": radial_channel_exact,
            "D2_qrr_field_channel_truncation_zero_in_exact_arithmetic": radial_channel_exact,
            "qtr_radial_D1_leg_truncation_zero_in_exact_arithmetic": radial_channel_exact,
            "qtr_theta_leg_exact": False,
            "nonlinear_density_action_or_quadrature_exact": False,
            "scope": "selected N=K=1,2,3 fields before nonlinear density evaluation, under the stabilized evaluator's polynomial continuation oracle",
        },
        "radial_stencil_domain": reach,
        "v5_6_6_13_margin_receipt": v13_scope,
    }
    decisions = {
        "v5_6_6_12_artifact_byte_pinned_pass": True,
        "v5_6_6_13_artifact_byte_pinned_pass": True,
        "v12_measurements_reanalyzed_without_route_C_recomputation_pass": True,
        "v12_formal_order_not_supported_component_ledger_relabelled_pass": True,
        "FD5_formal_order_4_exact_arithmetic_p_minus_1_ladder_counterexample_pass": bool(
            fd5_moments["exact_through_degree_4_pass"]
            and fd5_moments["first_failure_moment"] == "-4"
            and counterexample["observed_power_exact"] == "-1"
            and counterexample["negative_order_without_roundoff_pass"]
        ),
        "selected_K_le_3_pullback_rho_degree_at_most_8_ledger_pass": bool(
            profiles["selected_K_le_3_degree_le_8_pass"]
            and source_audit["pass"]
        ),
        "radial_nine_point_D1_D2_moments_exact_through_degree_8_pass": bool(
            moments["D1_and_D2_exact_through_selected_degree_8_pass"]
        ),
        "pinned_pullback_radial_degree_preservation_static_source_audit_pass": bool(
            source_audit["pass"]
        ),
        "selected_K_le_3_qr_qrr_radial_stencil_exact_in_exact_arithmetic_pass": radial_channel_exact,
        "selected_K_le_3_qtr_radial_leg_exact_in_exact_arithmetic_pass": radial_channel_exact,
        "pinned_members_margins_everywhere_certified_pass": bool(
            v13_scope["pinned_members_margins_everywhere_certified_pass"]
            and v13_scope["domain_source_fragments_present_pass"]
        ),
        "extended_radial_continuation_oracle_gap_recorded_pass": True,
        "free_FD5_roundoff_dominance_certified_pass": False,
        "free_FD5_rigorous_roundoff_bound_pass": False,
        "free_FD5_asymptotic_window_observed_pass": False,
        "theta_stencil_asymptotic_window_observed_pass": False,
        "rho_stencil_asymptotic_window_observed_pass": False,
        "all_assessed_components_support_formal_orders_pass": False,
        "fixed_Q_stencil_Richardson_estimate_available_pass": False,
        "selected_radial_density_action_or_quadrature_exactness_pass": False,
        "selected_K_le_3_full_qtr_stencil_exact_in_exact_arithmetic_pass": False,
        "restricted_K_le_8_family_radial_stencil_exactness_pass": False,
        "extended_radial_continuation_oracle_certified_pass": False,
        "pinned_members_margins_on_extended_radial_stencil_domain_pass": False,
        "v5_6_6_13_interval_rounding_enclosure_pass": False,
        "theta_coordinate_stencil_rigorous_bound_pass": False,
        "Q_h_limit_commutation_proved_pass": False,
        "B_FD_Q_to_infinity_estimate_pass": False,
        "B_FD_rigorous_bound_pass": False,
        "restricted_family_exact_action_identity_pass": False,
        "same_functional_symbolic_identity_pass": False,
        "density_union_C_N_pass": False,
        "spectral_N_convergence_pass": False,
        "periodic_box_exhaustion_and_tail_control_pass": False,
        "uniform_stability_pass": False,
        "uniform_N_to_infinity_bridge_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
    }
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": "theory_only;additive_correction;byte_pinned_reanalysis;exact_FD5_counterexample;radial_field_channel_polynomial_ledger;oracle_domain_gap;fail_closed",
        "decision": decisions,
        "scientific": scientific,
        "scientific_payload_sha256": _canonical_sha256(scientific),
        "interpretation_correction": {
            "supersedes_wording_only": [
                "v5.6.6.12 contradicted_components -> formal_order_not_supported_components",
                "v5.6.6.12 resolution_floor -> heuristic_fixed_screening_floor",
            ],
            "does_not_change": "the pinned numerical values, tolerance comparisons, or any false B_FD/bridge/promotion decision",
            "roundoff_boundary": "p_obs<=0 is compatible with roundoff but is not diagnostic; a rigorous bound needs error bounds for the four raw density evaluations propagated through quadrature",
            "radial_boundary": "exactness is limited to pulled-back field-channel D1/D2 under the polynomial-continuation oracle; downstream densities, action, quadrature, theta differentiation and free FD5 remain uncertified",
        },
        "source_pins": {
            "v5_6_6_12_producer_commit": V12_PRODUCER_COMMIT,
            "v5_6_6_12_source_sha256": V12_SOURCE_SHA256,
            "v5_6_6_12_test_sha256": V12_TEST_SHA256,
            "v5_6_6_12_artifact_sha256": V12_ARTIFACT_SHA256,
            "v5_6_6_13_producer_commit": V13_PRODUCER_COMMIT,
            "v5_6_6_13_source_sha256": V13_SOURCE_SHA256,
            "v5_6_6_13_test_sha256": V13_TEST_SHA256,
            "v5_6_6_13_artifact_sha256": V13_ARTIFACT_SHA256,
            "precision_route_C_v5_6_6_5_source_sha256": PRECISION_SOURCE_SHA256,
        },
        "open_obligation": {
            "free_roundoff": "certify forward errors of the four raw density evaluations and propagate them through quadrature, or use a certified higher-precision/interval evaluator",
            "radial_domain": "authorize and prove the polynomial-continuation oracle or replace the out-of-collar stencil with analytic/one-sided C2 radial derivatives",
            "theta": "bound the nine-point theta stencil across every actual nonlinear branch; no global analytic-strip bound is supplied here",
            "continuum": "Q/h limit interchange, arbitrary-member density, box exhaustion, and the uniform bridge remain open",
        },
        "evidence_boundary": "Machine-checked from byte-pinned receipts: a lossless reclassification of the finite ladders, an exact-arithmetic FD5 counterexample with observed order -1 and no roundoff, exact K<=3 radial profile degrees, exact D1/D2 stencil moments, and the later v5.6.6.13 whole-collar margin decision on rho in [0,1]. Static source audit propagates radial degree only through the pinned pulled-field construction. Not proven: roundoff dominance, K<=8 radial exactness, nonlinear density/action/quadrature exactness, the extended radial continuation oracle, margins on its out-of-collar reach, a theta/free B_FD bound, Q/h interchange, C1/N1, B4, or B5.",
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST) if TEST.exists() else None,
            },
            "python": platform.python_version(),
            "numpy": np.__version__,
            "recomputed_Route_C": False,
        },
    }
    return payload


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(build_payload(), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
