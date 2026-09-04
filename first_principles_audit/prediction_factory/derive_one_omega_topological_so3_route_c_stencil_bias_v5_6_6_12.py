#!/usr/bin/env python3
"""Finite-member Route-C stencil-bias audit (v5.6.6.12).

This additive gate measures the two numerical differentiations hidden inside
the precision-stabilized Route C:

* the five-point free-parameter JVP, with formal error O(h_free**4); and
* the nine-point coordinate jets, with formal error O(h_coord**8).

The three axes are refined separately around the production point and the
complete production/fine 2**3 cube is evaluated to expose mixed effects.  The
production point is independently compared with the byte-pinned Torch-AD
record from v5.6.6.6 at identical Qtheta=5, Qrho=10.

Richardson extrapolation is an estimate conditional on an asymptotic error
expansion.  A finite ladder and a floating-point AD comparison are not a
rigorous continuum bound on B_FD.  This gate therefore leaves the exact-action
identity, the uniform bridge, C1/N1, and B4/B5 fail-closed.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator, Mapping

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5
    as precision,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_route_c_stencil_bias_v5_6_6_12.json"
TEST = HERE / "test_one_omega_topological_so3_route_c_stencil_bias_v5_6_6_12.py"
SCHEMA = "holo.one-omega-topological-so3-route-c-stencil-bias-v5-6-6-12.v1"

PRECISION_SOURCE = Path(precision.__file__).resolve()
BASE_ROUTE_C_SOURCE = Path(precision.route_c.__file__).resolve()
EXPECTED_PRECISION_SOURCE = HERE / (
    "derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5.py"
)
EXPECTED_BASE_ROUTE_C_SOURCE = HERE / (
    "derive_one_omega_topological_so3_multin_independent_euler_green_route_c_"
    "v5_6_6_3.py"
)
THREE_WAY_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_ad_fd5_route_c_three_way_v5_6_6_6.json"
)
V56611_SOURCE = HERE / (
    "derive_one_omega_topological_so3_pinned_members_dense_collar_margins_"
    "v5_6_6_11.py"
)
V56611_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_pinned_members_dense_collar_margins_"
    "v5_6_6_11.json"
)

PRECISION_SOURCE_SHA256 = "5cf9c64fe8af45b55899275b2af1a9d55c706a138479e2cbd3a47ca4b270eca8"
BASE_ROUTE_C_SOURCE_SHA256 = "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"
THREE_WAY_ARTIFACT_SHA256 = "8ecc218622240ddb29521be237c33d81c46638544ebe1ff16b7b7e8fa7333092"
V56611_SOURCE_SHA256 = "2fd3a021189f5e329395c4e220a3fe7ea2412d22ed6c5ee4cf90f79e63b895f5"
V56611_ARTIFACT_SHA256 = "89592cd0eb7a3357a7f0b6f69bebeed5fb18d7466719c226b482b8611201a7b6"
THREE_WAY_SCHEMA = "holo.one-omega-topological-so3-ad-fd5-route-c-three-way-v5-6-6-6.v1"
V56611_SCHEMA = "holo.one-omega-topological-so3-pinned-members-dense-collar-margins-v5-6-6-11.v1"

TANGENTIAL_ORDER = 5
RADIAL_ORDER = 10
EXPECTED_MEMBERS = ((1, 1), (2, 2), (3, 3))

FREE_STEPS = (4.0e-3, 2.0e-3, 1.0e-3)
THETA_STEPS = (6.0e-2, 3.0e-2, 1.5e-2)
RHO_STEPS = (6.0e-2, 3.0e-2, 1.5e-2)
FREE_FORMAL_ORDER = 4
COORDINATE_FORMAL_ORDER = 8

# The acceptance tolerance is inherited from the byte-pinned three-way gate.
FIXED_ABSOLUTE_TOLERANCE = 1.0e-8
FIXED_RELATIVE_TOLERANCE = 1.0e-11
REPRODUCTION_ABSOLUTE_TOLERANCE = 1.0e-11
REPRODUCTION_RELATIVE_TOLERANCE = 1.0e-13
RESOLUTION_ABSOLUTE_FLOOR = 2.0e-10
RESOLUTION_RELATIVE_FLOOR = 2.0e-13

DEFAULT_WORKERS = 3
EXPECTED_DISTINCT_EVALUATIONS_PER_MEMBER = 11
RADIAL_POLYNOMIAL_MAX_DEGREE = 8


class StencilBiasGateError(RuntimeError):
    """A byte pin, evaluator contract, or finite-ladder invariant drifted."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_pinned_json(
    path: Path, expected_sha256: str, expected_schema: str
) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise StencilBiasGateError(
            f"byte pin drift for {path.name}: {observed} != {expected_sha256}"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != expected_schema:
        raise StencilBiasGateError(f"schema drift for {path.name}")
    return payload


@contextmanager
def coordinate_stencil_steps(
    theta_step: float, rho_step: float
) -> Iterator[None]:
    """Temporarily change only the v5.6.6.5 coordinate-stencil steps.

    The precision evaluator already swaps ``route_c._bulk_jet`` while it runs.
    Consequently this context is process-safe but intentionally not thread-safe.
    """

    if not (math.isfinite(theta_step) and theta_step > 0.0):
        raise StencilBiasGateError("theta_step must be finite and positive")
    if not (math.isfinite(rho_step) and rho_step > 0.0):
        raise StencilBiasGateError("rho_step must be finite and positive")
    original_theta = precision.STABLE_THETA_STEP
    original_rho = precision.STABLE_RHO_STEP
    precision.STABLE_THETA_STEP = precision.LD(str(theta_step))
    precision.STABLE_RHO_STEP = precision.LD(str(rho_step))
    try:
        yield
    finally:
        precision.STABLE_THETA_STEP = original_theta
        precision.STABLE_RHO_STEP = original_rho


def _components_are_finite(values: Mapping[str, float]) -> bool:
    return bool(values) and all(math.isfinite(float(value)) for value in values.values())


def _fixed_tolerance(scale: float) -> float:
    return FIXED_ABSOLUTE_TOLERANCE + FIXED_RELATIVE_TOLERANCE * scale


def _resolution_floor(scale: float) -> float:
    return RESOLUTION_ABSOLUTE_FLOOR + RESOLUTION_RELATIVE_FLOOR * scale


def _radial_stencil_moment_certificate() -> Mapping[str, Any]:
    """Prove exact monomial moments for the nine-point D1/D2 formulas.

    This is an exact rational statement about the stencil only.  The separate
    degree-<=8 claim for the selected pullback follows from the byte-pinned
    polynomial radial profiles and remains recorded as a source-level ledger.
    """

    formulas = {
        "first": {
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
        "second": {
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
            for degree in range(RADIAL_POLYNOMIAL_MAX_DEGREE + 1)
        }
        expected = {
            degree: (
                Fraction(math.factorial(derivative_order))
                if degree == derivative_order
                else Fraction(0)
            )
            for degree in moments
        }
        rows[name] = {
            "derivative_order": derivative_order,
            "moments": {str(key): str(value) for key, value in moments.items()},
            "expected": {str(key): str(value) for key, value in expected.items()},
            "exact_through_degree_8_pass": moments == expected,
        }
    return {
        "rows": rows,
        "exact_rational_moments_through_degree_8_pass": all(
            row["exact_through_degree_8_pass"] for row in rows.values()
        ),
    }


def _axis_analysis(
    coarse: Mapping[str, float],
    production: Mapping[str, float],
    fine: Mapping[str, float],
    *,
    formal_order: int,
) -> Mapping[str, Any]:
    """Analyse a 2h, h, h/2 ladder without promoting it to a proof."""

    if not (set(coarse) == set(production) == set(fine)):
        raise StencilBiasGateError("component-key drift in a step ladder")
    factor = float(2**formal_order)
    denominator = factor - 1.0
    lower_order = 0.75 * formal_order
    upper_order = 1.25 * formal_order
    rows: dict[str, Any] = {}
    for name in sorted(production):
        c = float(coarse[name])
        p = float(production[name])
        f = float(fine[name])
        scale = max(1.0, abs(c), abs(p), abs(f))
        floor = _resolution_floor(scale)
        coarse_delta_signed = c - p
        fine_delta_signed = p - f
        coarse_delta = abs(coarse_delta_signed)
        fine_delta = abs(fine_delta_signed)
        assessed = coarse_delta > floor and fine_delta > floor
        contraction_ratio = coarse_delta / fine_delta if fine_delta > floor else None
        observed_order = (
            math.log2(contraction_ratio)
            if assessed and contraction_ratio is not None and contraction_ratio > 0.0
            else None
        )
        same_leading_error_sign = (
            coarse_delta_signed * fine_delta_signed > 0.0 if assessed else None
        )
        formal_order_supported = bool(
            assessed
            and same_leading_error_sign
            and observed_order is not None
            and lower_order <= observed_order <= upper_order
        )
        coarse_pair_bias_candidate = coarse_delta_signed / denominator
        fine_pair_bias_candidate = factor * fine_delta_signed / denominator
        extrapolated_from_coarse = p + (p - c) / denominator
        extrapolated_from_fine = f + (f - p) / denominator
        tolerance = _fixed_tolerance(scale)
        rows[name] = {
            "coarse": c,
            "production": p,
            "fine": f,
            "scale": scale,
            "resolution_floor": floor,
            "coarse_minus_production": coarse_delta_signed,
            "production_minus_fine": fine_delta_signed,
            "absolute_coarse_to_production_change": coarse_delta,
            "absolute_production_to_fine_change": fine_delta,
            "assessed_above_resolution_floor": assessed,
            "contraction_ratio_coarse_gap_over_fine_gap": contraction_ratio,
            "observed_order_log2_ratio": observed_order,
            "same_leading_error_sign": same_leading_error_sign,
            "formal_order_window": [lower_order, upper_order],
            "formal_order_supported_on_this_component": formal_order_supported,
            "Richardson_estimate_eligible": formal_order_supported,
            "raw_production_bias_candidate_from_coarse_pair": coarse_pair_bias_candidate,
            "raw_production_bias_candidate_from_fine_pair": fine_pair_bias_candidate,
            "conditional_production_bias_from_coarse_pair": (
                coarse_pair_bias_candidate if formal_order_supported else None
            ),
            "conditional_production_bias_from_fine_pair": (
                fine_pair_bias_candidate if formal_order_supported else None
            ),
            "conditional_extrapolated_limit_from_coarse_pair": extrapolated_from_coarse,
            "conditional_extrapolated_limit_from_fine_pair": extrapolated_from_fine,
            "conditional_extrapolant_disagreement": (
                extrapolated_from_coarse - extrapolated_from_fine
            ),
            "fixed_tolerance": tolerance,
            "production_to_fine_within_fixed_tolerance": fine_delta <= tolerance,
        }
    assessed_rows = [
        row for row in rows.values() if row["assessed_above_resolution_floor"]
    ]
    contradicted = [
        name
        for name, row in rows.items()
        if row["assessed_above_resolution_floor"]
        and not row["formal_order_supported_on_this_component"]
    ]
    return {
        "formal_order": formal_order,
        "expected_contraction_ratio": factor,
        "rows": rows,
        "component_count": len(rows),
        "assessed_component_count": len(assessed_rows),
        "unresolved_component_count": len(rows) - len(assessed_rows),
        "contradicted_components": contradicted,
        "no_resolved_component_contradicts_formal_order_pass": not contradicted,
        "asymptotic_window_observed_pass": bool(assessed_rows and not contradicted),
        "all_production_to_fine_changes_within_fixed_tolerance_pass": all(
            row["production_to_fine_within_fixed_tolerance"] for row in rows.values()
        ),
        "maximum_absolute_production_to_fine_change": max(
            row["absolute_production_to_fine_change"] for row in rows.values()
        ),
        "maximum_absolute_conditional_production_bias_estimate": (
            max(
                max(
                    abs(row["conditional_production_bias_from_coarse_pair"]),
                    abs(row["conditional_production_bias_from_fine_pair"]),
                )
                for row in rows.values()
                if row["Richardson_estimate_eligible"]
            )
            if any(row["Richardson_estimate_eligible"] for row in rows.values())
            else None
        ),
    }


def _cube_analysis(
    cube: Mapping[str, Mapping[str, float]],
) -> Mapping[str, Any]:
    """Resolve all one-, two-, and three-axis half-step interactions."""

    expected = {"ppp", "fpp", "pfp", "ppf", "ffp", "fpf", "pff", "fff"}
    if set(cube) != expected:
        raise StencilBiasGateError(f"incomplete production/fine cube: {set(cube)}")
    component_names = set(cube["ppp"])
    if any(set(values) != component_names for values in cube.values()):
        raise StencilBiasGateError("component-key drift in production/fine cube")
    rows: dict[str, Any] = {}
    for name in sorted(component_names):
        v = {label: float(values[name]) for label, values in cube.items()}
        scale = max(1.0, *(abs(value) for value in v.values()))
        free = v["fpp"] - v["ppp"]
        theta = v["pfp"] - v["ppp"]
        rho = v["ppf"] - v["ppp"]
        free_theta = v["ffp"] - v["fpp"] - v["pfp"] + v["ppp"]
        free_rho = v["fpf"] - v["fpp"] - v["ppf"] + v["ppp"]
        theta_rho = v["pff"] - v["pfp"] - v["ppf"] + v["ppp"]
        triple = (
            v["fff"]
            - v["ffp"]
            - v["fpf"]
            - v["pff"]
            + v["fpp"]
            + v["pfp"]
            + v["ppf"]
            - v["ppp"]
        )
        reconstructed = (
            free
            + theta
            + rho
            + free_theta
            + free_rho
            + theta_rho
            + triple
        )
        total = v["fff"] - v["ppp"]
        tolerance = _fixed_tolerance(scale)
        rows[name] = {
            "production_value": v["ppp"],
            "all_fine_value": v["fff"],
            "one_axis_effects": {"free": free, "theta": theta, "rho": rho},
            "two_axis_interactions": {
                "free_theta": free_theta,
                "free_rho": free_rho,
                "theta_rho": theta_rho,
            },
            "three_axis_interaction": triple,
            "absolute_nonadditive_interaction_sum": (
                abs(free_theta) + abs(free_rho) + abs(theta_rho) + abs(triple)
            ),
            "production_to_all_fine_change": total,
            "mobius_reconstructed_change": reconstructed,
            "algebraic_reconstruction_residual": total - reconstructed,
            "fixed_tolerance": tolerance,
            "production_to_all_fine_within_fixed_tolerance": abs(total) <= tolerance,
        }
    return {
        "rows": rows,
        "component_count": len(rows),
        "all_production_to_all_fine_changes_within_fixed_tolerance_pass": all(
            row["production_to_all_fine_within_fixed_tolerance"]
            for row in rows.values()
        ),
        "maximum_absolute_production_to_all_fine_change": max(
            abs(row["production_to_all_fine_change"]) for row in rows.values()
        ),
        "maximum_absolute_nonadditive_interaction_sum": max(
            row["absolute_nonadditive_interaction_sum"] for row in rows.values()
        ),
        "maximum_algebraic_reconstruction_residual": max(
            abs(row["algebraic_reconstruction_residual"])
            for row in rows.values()
        ),
    }


def _evaluate_member_campaign(member_index: int) -> Mapping[str, Any]:
    """Worker entry point; each process owns its temporary global step values."""

    bundle = precision.route_c.load_bundle()
    member = bundle["primary_members"][member_index]
    N = int(member["N"])
    K = int(member["K"])
    production_free = FREE_STEPS[1]
    production_theta = THETA_STEPS[1]
    production_rho = RHO_STEPS[1]
    cache: dict[tuple[float, float, float], Mapping[str, float]] = {}

    def evaluate(free_step: float, theta_step: float, rho_step: float) -> Mapping[str, float]:
        key = (free_step, theta_step, rho_step)
        if key not in cache:
            with coordinate_stencil_steps(theta_step, rho_step):
                result = precision.evaluate_direct_member_stable(
                    bundle,
                    member,
                    tangential_order=TANGENTIAL_ORDER,
                    radial_order=RADIAL_ORDER,
                    free_step=free_step,
                )
            values = {
                name: float(value)
                for name, value in result["direct_local_free_JVP_by_component"].items()
            }
            if not _components_are_finite(values):
                raise StencilBiasGateError(
                    f"non-finite Route-C values for N={N}, steps={key}"
                )
            cache[key] = values
            print(
                f"completed v5.6.6.12 N={N} "
                f"hfree={free_step:g} htheta={theta_step:g} hrho={rho_step:g}",
                flush=True,
            )
        return cache[key]

    point_specs: dict[str, tuple[float, float, float]] = {
        "baseline": (production_free, production_theta, production_rho),
        "free_coarse": (FREE_STEPS[0], production_theta, production_rho),
        "free_fine": (FREE_STEPS[2], production_theta, production_rho),
        "theta_coarse": (production_free, THETA_STEPS[0], production_rho),
        "theta_fine": (production_free, THETA_STEPS[2], production_rho),
        "rho_coarse": (production_free, production_theta, RHO_STEPS[0]),
        "rho_fine": (production_free, production_theta, RHO_STEPS[2]),
        "free_theta_fine": (FREE_STEPS[2], THETA_STEPS[2], production_rho),
        "free_rho_fine": (FREE_STEPS[2], production_theta, RHO_STEPS[2]),
        "theta_rho_fine": (production_free, THETA_STEPS[2], RHO_STEPS[2]),
        "all_fine": (FREE_STEPS[2], THETA_STEPS[2], RHO_STEPS[2]),
    }
    evaluations: dict[str, Any] = {}
    for label, steps in point_specs.items():
        evaluations[label] = {
            "steps": {
                "free": steps[0],
                "theta": steps[1],
                "rho": steps[2],
            },
            "components": evaluate(*steps),
        }
    if len(cache) != EXPECTED_DISTINCT_EVALUATIONS_PER_MEMBER:
        raise StencilBiasGateError(
            f"unexpected distinct evaluation count for N={N}: {len(cache)}"
        )

    components = lambda label: evaluations[label]["components"]
    axes = {
        "free": _axis_analysis(
            components("free_coarse"),
            components("baseline"),
            components("free_fine"),
            formal_order=FREE_FORMAL_ORDER,
        ),
        "theta": _axis_analysis(
            components("theta_coarse"),
            components("baseline"),
            components("theta_fine"),
            formal_order=COORDINATE_FORMAL_ORDER,
        ),
        "rho": _axis_analysis(
            components("rho_coarse"),
            components("baseline"),
            components("rho_fine"),
            formal_order=COORDINATE_FORMAL_ORDER,
        ),
    }
    cube = {
        "ppp": components("baseline"),
        "fpp": components("free_fine"),
        "pfp": components("theta_fine"),
        "ppf": components("rho_fine"),
        "ffp": components("free_theta_fine"),
        "fpf": components("free_rho_fine"),
        "pff": components("theta_rho_fine"),
        "fff": components("all_fine"),
    }
    cube_analysis = _cube_analysis(cube)

    conditional_rows: dict[str, Any] = {}
    for name in sorted(components("baseline")):
        axis_estimates = {
            axis: analysis["rows"][name][
                "conditional_production_bias_from_fine_pair"
            ]
            for axis, analysis in axes.items()
        }
        raw_axis_candidates = {
            axis: float(
                analysis["rows"][name][
                    "raw_production_bias_candidate_from_fine_pair"
                ]
            )
            for axis, analysis in axes.items()
        }
        eligible_axes = [
            axis for axis, value in axis_estimates.items() if value is not None
        ]
        all_axes_eligible = len(eligible_axes) == len(axes)
        conditional_rows[name] = {
            "axiswise_signed_estimates": axis_estimates,
            "raw_axiswise_signed_candidates": raw_axis_candidates,
            "eligible_axes": eligible_axes,
            "all_axes_eligible": all_axes_eligible,
            "axiswise_signed_sum": (
                math.fsum(float(value) for value in axis_estimates.values())
                if all_axes_eligible
                else None
            ),
            "axiswise_absolute_sum": (
                math.fsum(abs(float(value)) for value in axis_estimates.values())
                if all_axes_eligible
                else None
            ),
            "observed_production_to_all_fine_change": cube_analysis["rows"][name][
                "production_to_all_fine_change"
            ],
            "observed_absolute_nonadditive_interaction_sum": cube_analysis["rows"][name][
                "absolute_nonadditive_interaction_sum"
            ],
        }
    return {
        "N": N,
        "K": K,
        "member_id": member["member_id"],
        "authoritative_free_central_sha256": member[
            "authoritative_free_central_f64le"
        ]["sha256"],
        "authoritative_free_tangent_sha256": next(
            curve
            for curve in member["curves"]
            if curve["name"] == "joint_all_primitive_classes_control_candidate"
        )["authoritative_free_tangent_f64le"]["sha256"],
        "distinct_evaluation_count": len(cache),
        "evaluations": evaluations,
        "axis_ladders": axes,
        "production_fine_cube": cube_analysis,
        "conditional_axiswise_fixed_Q_stencil_estimate": {
            "rows": conditional_rows,
            "all_component_axes_eligible": all(
                row["all_axes_eligible"] for row in conditional_rows.values()
            ),
            "maximum_absolute_axiswise_signed_sum": (
                max(
                    abs(row["axiswise_signed_sum"])
                    for row in conditional_rows.values()
                    if row["all_axes_eligible"]
                )
                if any(row["all_axes_eligible"] for row in conditional_rows.values())
                else None
            ),
            "maximum_axiswise_absolute_sum": (
                max(
                    row["axiswise_absolute_sum"]
                    for row in conditional_rows.values()
                    if row["all_axes_eligible"]
                )
                if any(row["all_axes_eligible"] for row in conditional_rows.values())
                else None
            ),
            "warning": (
                "These are fixed-Q Richardson candidates, not estimates of the "
                "Q-to-infinity B_FD unless every axis is resolved at its formal "
                "order and the Q/h limits are proved to commute. Ineligible rows "
                "are deliberately null; raw algebraic candidates remain visible."
            ),
        },
    }


def _reference_comparison(
    observed: Mapping[str, float], reference_row: Mapping[str, Any]
) -> Mapping[str, Any]:
    route_reference = reference_row["Route_C_precision_stabilized_JVP"]
    ad_reference = reference_row["AD_JVP"]
    if not (set(observed) == set(route_reference) == set(ad_reference)):
        raise StencilBiasGateError("component-key drift against v5.6.6.6")
    rows: dict[str, Any] = {}
    for name in sorted(observed):
        value = float(observed[name])
        route_value = float(route_reference[name])
        ad_value = float(ad_reference[name])
        scale = max(1.0, abs(value), abs(route_value), abs(ad_value))
        reproduction_tolerance = (
            REPRODUCTION_ABSOLUTE_TOLERANCE
            + REPRODUCTION_RELATIVE_TOLERANCE * scale
        )
        ad_tolerance = _fixed_tolerance(scale)
        rows[name] = {
            "observed_production_route_C": value,
            "pinned_v5_6_6_6_route_C": route_value,
            "pinned_v5_6_6_6_Torch_AD": ad_value,
            "route_C_reproduction_residual": value - route_value,
            "route_C_reproduction_tolerance": reproduction_tolerance,
            "route_C_reproduction_pass": abs(value - route_value)
            <= reproduction_tolerance,
            "production_route_C_minus_AD": value - ad_value,
            "AD_crosscheck_tolerance": ad_tolerance,
            "AD_crosscheck_pass": abs(value - ad_value) <= ad_tolerance,
        }
    return {
        "rows": rows,
        "production_route_C_reproduced_pass": all(
            row["route_C_reproduction_pass"] for row in rows.values()
        ),
        "finite_Q_Torch_AD_crosscheck_pass": all(
            row["AD_crosscheck_pass"] for row in rows.values()
        ),
        "maximum_absolute_route_C_reproduction_residual": max(
            abs(row["route_C_reproduction_residual"])
            for row in rows.values()
        ),
        "maximum_absolute_production_route_C_minus_AD": max(
            abs(row["production_route_C_minus_AD"]) for row in rows.values()
        ),
    }


def _load_inputs() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    if PRECISION_SOURCE != EXPECTED_PRECISION_SOURCE.resolve():
        raise StencilBiasGateError("precision Route-C import is outside this checkout")
    if BASE_ROUTE_C_SOURCE != EXPECTED_BASE_ROUTE_C_SOURCE.resolve():
        raise StencilBiasGateError("base Route-C import is outside this checkout")
    if np.finfo(np.longdouble).eps >= np.finfo(np.float64).eps:
        raise StencilBiasGateError("extended-precision longdouble is required")
    source_pins = {
        PRECISION_SOURCE: PRECISION_SOURCE_SHA256,
        BASE_ROUTE_C_SOURCE: BASE_ROUTE_C_SOURCE_SHA256,
        V56611_SOURCE: V56611_SOURCE_SHA256,
    }
    for path, expected in source_pins.items():
        observed = _sha256(path)
        if observed != expected:
            raise StencilBiasGateError(
                f"source pin drift for {path.name}: {observed} != {expected}"
            )
    three_way = _read_pinned_json(
        THREE_WAY_ARTIFACT, THREE_WAY_ARTIFACT_SHA256, THREE_WAY_SCHEMA
    )
    v56611 = _read_pinned_json(
        V56611_ARTIFACT, V56611_ARTIFACT_SHA256, V56611_SCHEMA
    )
    if three_way["decision"]["AD_FD5_Route_C_three_way_comparison_pass"] is not True:
        raise StencilBiasGateError("v5.6.6.6 three-way input is no longer green")
    if v56611["decision"]["pinned_members_margins_everywhere_on_collar_pass"] is not False:
        raise StencilBiasGateError("v5.6.6.11 whole-collar gap must remain fail-closed")
    if "B_FD" not in v56611["open_obligation"]["stencil_bias"]:
        raise StencilBiasGateError("v5.6.6.11 no longer declares the stencil-bias gap")
    return three_way, v56611


def build_payload() -> Mapping[str, Any]:
    three_way, v56611 = _load_inputs()
    radial_moments = _radial_stencil_moment_certificate()
    raw_radial_nodes, _raw_radial_weights = np.polynomial.legendre.leggauss(
        RADIAL_ORDER
    )
    radial_nodes = 0.5 * (raw_radial_nodes + 1.0)
    coarse_radial_reach = [
        float(np.min(radial_nodes) - 4.0 * RHO_STEPS[0]),
        float(np.max(radial_nodes) + 4.0 * RHO_STEPS[0]),
    ]
    reference_by_n = {
        int(row["N"]): row for row in three_way["scientific"]["members"]
    }
    worker_count = min(len(EXPECTED_MEMBERS), DEFAULT_WORKERS)
    if worker_count == 1:
        members = [
            _evaluate_member_campaign(index) for index in range(len(EXPECTED_MEMBERS))
        ]
    else:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            members = list(
                executor.map(
                    _evaluate_member_campaign, range(len(EXPECTED_MEMBERS))
                )
            )
    members = sorted(members, key=lambda row: int(row["N"]))
    if [(row["N"], row["K"]) for row in members] != list(EXPECTED_MEMBERS):
        raise StencilBiasGateError("selected-member lineage drift")

    for member in members:
        N = int(member["N"])
        if N not in reference_by_n:
            raise StencilBiasGateError(f"missing v5.6.6.6 reference for N={N}")
        member["independent_reference_at_production"] = _reference_comparison(
            member["evaluations"]["baseline"]["components"], reference_by_n[N]
        )

    axes = ("free", "theta", "rho")
    decisions = {
        "v5_6_6_11_stencil_description_correction_recorded": True,
        "stencil_step_ladders_measured_pass": all(
            member["distinct_evaluation_count"]
            == EXPECTED_DISTINCT_EVALUATIONS_PER_MEMBER
            for member in members
        ),
        "production_fine_full_cube_measured_pass": all(
            member["production_fine_cube"]["component_count"]
            == len(precision.route_c.ACTION_COMPONENTS) + 1
            for member in members
        ),
        "free_FD5_asymptotic_window_observed_pass": all(
            member["axis_ladders"]["free"]["asymptotic_window_observed_pass"]
            for member in members
        ),
        "theta_stencil_asymptotic_window_observed_pass": all(
            member["axis_ladders"]["theta"]["asymptotic_window_observed_pass"]
            for member in members
        ),
        "rho_stencil_asymptotic_window_observed_pass": all(
            member["axis_ladders"]["rho"]["asymptotic_window_observed_pass"]
            for member in members
        ),
        "all_resolved_components_consistent_with_formal_orders_pass": all(
            member["axis_ladders"][axis][
                "no_resolved_component_contradicts_formal_order_pass"
            ]
            for member in members
            for axis in axes
        ),
        "selected_member_fixed_Q_production_to_all_fine_sensitivity_pass": all(
            member["production_fine_cube"][
                "all_production_to_all_fine_changes_within_fixed_tolerance_pass"
            ]
            for member in members
        ),
        "production_route_C_reproduced_from_v5_6_6_6_pass": all(
            member["independent_reference_at_production"][
                "production_route_C_reproduced_pass"
            ]
            for member in members
        ),
        "selected_member_fixed_Q_Torch_AD_crosscheck_pass": all(
            member["independent_reference_at_production"][
                "finite_Q_Torch_AD_crosscheck_pass"
            ]
            for member in members
        ),
        "radial_nine_point_moments_exact_through_degree_8_pass": radial_moments[
            "exact_rational_moments_through_degree_8_pass"
        ],
        "fixed_Q_stencil_Richardson_candidates_recorded_pass": True,
        "fixed_Q_stencil_Richardson_estimate_available_pass": all(
            member["conditional_axiswise_fixed_Q_stencil_estimate"][
                "all_component_axes_eligible"
            ]
            for member in members
        ),
        "Q_h_limit_commutation_proved_pass": False,
        "B_FD_Q_to_infinity_estimate_pass": False,
        "B_FD_rigorous_bound_pass": False,
        "restricted_family_exact_action_identity_pass": False,
        "pinned_members_margins_everywhere_on_collar_pass": False,
        "uniform_N_to_infinity_bridge_pass": False,
        "uniform_stability_pass": False,
        "spectral_N_convergence_pass": False,
        "periodic_box_exhaustion_and_tail_control_pass": False,
        "density_union_C_N_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
    }
    scientific = {
        "members": members,
        "radial_stencil_exactness": {
            "moment_certificate": radial_moments,
            "selected_pullback_degree_ledger": {
                "h0": 5,
                "h1": 6,
                "envelope_times_Legendre_max": 8,
                "pullback_jacobian_rho_degree": 0,
                "pulled_fields_max_rho_degree": 8,
            },
            "scope": (
                "The rational moments prove stencil exactness for polynomials "
                "through degree 8. The selected pullback degree ledger is a "
                "source-level consequence of the byte-pinned evaluator; the rho "
                "ladder therefore primarily diagnoses floating-point noise."
            ),
        },
        "summary": {
            "maximum_absolute_production_to_all_fine_change": max(
                member["production_fine_cube"][
                    "maximum_absolute_production_to_all_fine_change"
                ]
                for member in members
            ),
            "maximum_absolute_nonadditive_interaction_sum": max(
                member["production_fine_cube"][
                    "maximum_absolute_nonadditive_interaction_sum"
                ]
                for member in members
            ),
            "maximum_absolute_production_route_C_minus_AD": max(
                member["independent_reference_at_production"][
                    "maximum_absolute_production_route_C_minus_AD"
                ]
                for member in members
            ),
            "axis_assessed_component_counts": {
                axis: [
                    member["axis_ladders"][axis]["assessed_component_count"]
                    for member in members
                ]
                for axis in axes
            },
            "axis_contradicted_components_by_member": {
                axis: {
                    str(member["N"]): member["axis_ladders"][axis][
                        "contradicted_components"
                    ]
                    for member in members
                }
                for axis in axes
            },
        },
        "lineage_correction": {
            "v5_6_6_11_wording": (
                "7-point coordinate stencils, h=5e-3, O(h^8)"
            ),
            "actual_precision_route_C_used_here": (
                "v5.6.6.5 nine-point coordinate stencil, htheta=hrho=0.03, "
                "formal order 8"
            ),
            "base_route_C_not_used_for_this_bias_ladder": (
                "v5.6.6.3 seven-point first/second stencils at h=0.005 "
                "have formal order 6; its mixed tensor stencil has formal order 4"
            ),
        },
        "interpretation": (
            "The finite ladders measure step sensitivity of the three selected "
            "members at fixed Qtheta=5, Qrho=10. The full production/fine cube "
            "exposes non-additive interactions. This is not an estimator of the "
            "Q-to-infinity B_FD: the Q/h limit interchange is unproved, unresolved "
            "or wrong-order rows receive no Richardson estimate, and neither a "
            "floating-point Torch-AD comparison nor a finite ladder supplies the "
            "derivative suprema or interval enclosure required for a rigorous bound."
        ),
    }
    return {
        "schema": SCHEMA,
        "classification": (
            "theory_only;route_C;finite_step_ladders;full_refinement_cube;"
            "Torch_AD_crosscheck;multi_N;fixed_quadrature;conditional_Richardson;"
            "fail_closed_bridge"
        ),
        "decision": decisions,
        "fixed_before_run": {
            "members": [list(pair) for pair in EXPECTED_MEMBERS],
            "tangential_order": TANGENTIAL_ORDER,
            "radial_order": RADIAL_ORDER,
            "free_steps_coarse_production_fine": list(FREE_STEPS),
            "theta_steps_coarse_production_fine": list(THETA_STEPS),
            "rho_steps_coarse_production_fine": list(RHO_STEPS),
            "free_formal_order": FREE_FORMAL_ORDER,
            "coordinate_formal_order": COORDINATE_FORMAL_ORDER,
            "fixed_absolute_tolerance": FIXED_ABSOLUTE_TOLERANCE,
            "fixed_relative_tolerance": FIXED_RELATIVE_TOLERANCE,
            "resolution_absolute_floor": RESOLUTION_ABSOLUTE_FLOOR,
            "resolution_relative_floor": RESOLUTION_RELATIVE_FLOOR,
            "full_production_fine_cube_required": True,
            "expected_distinct_evaluations_per_member": (
                EXPECTED_DISTINCT_EVALUATIONS_PER_MEMBER
            ),
            "fixed_quadrature": {
                "Qtheta": TANGENTIAL_ORDER,
                "Qrho": RADIAL_ORDER,
            },
            "coarse_radial_stencil_reach_over_GL_nodes": coarse_radial_reach,
        },
        "scientific": scientific,
        "independence_boundary": {
            "precision_route_C_imported": True,
            "precision_route_C_import_path_matches_checkout": (
                PRECISION_SOURCE == EXPECTED_PRECISION_SOURCE.resolve()
            ),
            "base_route_C_import_path_matches_checkout": (
                BASE_ROUTE_C_SOURCE == EXPECTED_BASE_ROUTE_C_SOURCE.resolve()
            ),
            "extended_precision_longdouble_required": True,
            "Torch_action_module_imported": False,
            "NumPy_FD5_action_module_imported": False,
            "pinned_Torch_AD_values_read_only": True,
            "production_route_C_recomputed": True,
            "parallelism": (
                "members execute in separate processes; coordinate-step globals "
                "are never varied concurrently inside one process"
            ),
            "complex_step_attempted": False,
            "complex_step_reason": (
                "the pinned evaluator is real-valued, casts to longdouble/float, "
                "and uses non-holomorphic operations such as abs(det)"
            ),
        },
        "open_obligation": {
            "stencil_bias": (
                "B_FD still needs a rigorous derivative-supremum/interval bound "
                "or a certified exact-derivative reference in the continuum limit"
            ),
            "Q_h_limit_interchange": (
                "repeat the stencil comparison on a quadrature ladder and prove "
                "that differentiation/step refinement commutes with Q-to-infinity"
            ),
            "extended_stencil_domain": (
                "a rigorous remainder bound must certify the perturbed free-data "
                "tube and the radial stencil reach outside [0,1]"
            ),
            "whole_collar_margins": v56611["open_obligation"]["interval_bound"],
            "gap_4": v56611["open_obligation"]["gap_4"],
            "gap_5": v56611["open_obligation"]["gap_5"],
            "uniform_bridge": (
                "finite N=1,2,3 and fixed Q do not establish density, uniform "
                "stability, gauge quotient control, or N-to-infinity convergence"
            ),
        },
        "evidence_boundary": (
            "Machine-checked: three one-axis step ladders, the complete 2^3 "
            "production/fine cube, production reproducibility, and a finite-Q "
            "Torch-AD crosscheck for the three pinned members, plus exact rational "
            "moments of the radial stencil. Raw Richardson candidates are retained, "
            "but ineligible rows are null and no Q-to-infinity estimate is claimed. "
            "Not proven: Q/h limit interchange, a rigorous continuum B_FD bound, "
            "the exact-action identity, the uniform bridge, C1/N1, B4/B5."
        ),
        "source_pins": {
            "precision_route_C_v5_6_6_5_source_sha256": PRECISION_SOURCE_SHA256,
            "base_route_C_v5_6_6_3_source_sha256": BASE_ROUTE_C_SOURCE_SHA256,
            "three_way_v5_6_6_6_artifact_sha256": THREE_WAY_ARTIFACT_SHA256,
            "v5_6_6_11_source_sha256": V56611_SOURCE_SHA256,
            "v5_6_6_11_artifact_sha256": V56611_ARTIFACT_SHA256,
            "primitive_bundle_sha256": precision.route_c.BUNDLE_SHA256,
            "literal_v5_2_action_sha256": precision.route_c.LITERAL_V5_2_ACTION_SHA256,
            "frozen_checkpoint_commit": "ea014fd1a8ed124c353058eb6f0a1c92b90353bc",
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
            "python": platform.python_version(),
            "numpy": np.__version__,
            "workers": worker_count,
        },
        "scientific_payload_sha256": _canonical_sha256(scientific),
    }


def main() -> None:
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT, flush=True)


if __name__ == "__main__":
    main()
