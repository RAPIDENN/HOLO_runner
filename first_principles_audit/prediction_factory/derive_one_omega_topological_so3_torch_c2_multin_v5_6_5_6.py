#!/usr/bin/env python3
"""Torch/AD evaluation of the corrected C2 radial N=1,2,3 family."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
BASE_ROUTE_WRAPPER = HERE / "derive_one_omega_topological_so3_torch_route_a_multin_v5_6_5_5.py"
BASE_ROUTE_WRAPPER_SHA256 = "5c24361ba431888ccaf473ba2ab17aa00354258ba70c31bb81bfb77ebf6d56b6"
BUNDLE = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_4_c2_radial_primitive_bundle.json"
)
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
TEST = HERE / "test_one_omega_topological_so3_torch_c2_multin_v5_6_5_6.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_torch_c2_multin_v5_6_5_6.json"
SCHEMA = "holo.one-omega-topological-so3-torch-c2-multin-v5-6-5-6.v1"
BUNDLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-4-c2-radial-primitive-bundle.v1"
)
TANGENTIAL_Q = 5
RADIAL_JVP_Q = 10
RADIAL_REFINEMENT = (6, 8, 10, 12)
TANGENTIAL_REFINEMENT = (3, 5, 7)
CHUNK_SIZE = 64
RADIAL_ATOL = 5.0e-3
RADIAL_RTOL = 5.0e-7
TANGENTIAL_ATOL = 5.0e-8
TANGENTIAL_RTOL = 5.0e-10


class C2MultiNRouteAError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_base_wrapper() -> Any:
    observed = _sha256(BASE_ROUTE_WRAPPER)
    if observed != BASE_ROUTE_WRAPPER_SHA256:
        raise C2MultiNRouteAError(f"base route-A wrapper drift: {observed}")
    name = "frozen_torch_multin_wrapper_v5655_for_c2"
    spec = importlib.util.spec_from_file_location(name, BASE_ROUTE_WRAPPER)
    if spec is None or spec.loader is None:
        raise C2MultiNRouteAError("cannot import base route-A wrapper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_bundle(route_a: Any) -> Mapping[str, Any]:
    observed = _sha256(BUNDLE)
    if observed != BUNDLE_SHA256:
        raise C2MultiNRouteAError(f"C2 primitive bundle drift: {observed}")
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise C2MultiNRouteAError("C2 primitive schema drift")
    embedded = bundle["payload_sha256"]
    material = {key: value for key, value in bundle.items() if key != "payload_sha256"}
    canonical = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    if canonical != embedded:
        raise C2MultiNRouteAError("C2 primitive payload hash drift")
    if bundle["action_contract"]["exact_action"] != route_a.EXACT_ACTION:
        raise C2MultiNRouteAError("literal action mismatch")
    return bundle


def c2_radial_profiles_torch(rho: Any, K: int) -> Mapping[str, Any]:
    """Route-A-owned polynomial implementation; no NumPy profile helper."""

    import torch

    if rho.ndim != 1 or bool(torch.any((rho <= 0.0) | (rho >= 1.0))):
        raise C2MultiNRouteAError("radial action nodes must lie inside (0,1)")
    h0 = 1.0 - 10.0 * rho**3 + 15.0 * rho**4 - 6.0 * rho**5
    h0_first = -30.0 * rho**2 + 60.0 * rho**3 - 30.0 * rho**4
    h0_second = -60.0 * rho + 180.0 * rho**2 - 120.0 * rho**3
    h1 = rho * h0
    h1_first = h0 + rho * h0_first
    h1_second = 2.0 * h0_first + rho * h0_second
    s = rho * (1.0 - rho)
    s_first = 1.0 - 2.0 * rho
    envelope = 64.0 * s**3
    envelope_first = 192.0 * s**2 * s_first
    envelope_second = 384.0 * s * s_first**2 - 384.0 * s**2
    coordinate = 2.0 * rho - 1.0
    polynomials = [torch.ones_like(coordinate)]
    first_z = [torch.zeros_like(coordinate)]
    second_z = [torch.zeros_like(coordinate)]
    if K > 1:
        polynomials.append(coordinate)
        first_z.append(torch.ones_like(coordinate))
        second_z.append(torch.zeros_like(coordinate))
    for degree in range(2, K):
        scale = float(2 * degree - 1)
        polynomials.append(
            (scale * coordinate * polynomials[-1]
             - float(degree - 1) * polynomials[-2]) / float(degree)
        )
        first_z.append(
            (scale * (polynomials[-2] + coordinate * first_z[-1])
             - float(degree - 1) * first_z[-2]) / float(degree)
        )
        second_z.append(
            (scale * (2.0 * first_z[-2] + coordinate * second_z[-1])
             - float(degree - 1) * second_z[-2]) / float(degree)
        )
    polynomial = torch.stack(polynomials, dim=-1)
    polynomial_first = 2.0 * torch.stack(first_z, dim=-1)
    polynomial_second = 4.0 * torch.stack(second_z, dim=-1)
    return {
        "h0": h0,
        "h0_first": h0_first,
        "h0_second": h0_second,
        "h1": h1,
        "h1_first": h1_first,
        "h1_second": h1_second,
        "bumps": envelope[:, None] * polynomial,
        "bumps_first": (
            envelope_first[:, None] * polynomial
            + envelope[:, None] * polynomial_first
        ),
        "bumps_second": (
            envelope_second[:, None] * polynomial
            + 2.0 * envelope_first[:, None] * polynomial_first
            + envelope[:, None] * polynomial_second
        ),
    }


@contextmanager
def _profile_patch(route_a: Any) -> Iterator[None]:
    original = route_a.radial_profile_evaluation
    route_a.radial_profile_evaluation = c2_radial_profiles_torch
    try:
        yield
    finally:
        route_a.radial_profile_evaluation = original


def _joint(member: Mapping[str, Any]) -> Mapping[str, Any]:
    return next(
        curve
        for curve in member["curves"]
        if curve["name"] == "joint_all_primitive_classes_control_candidate"
    )


def _chunked_value(
    route_a: Any, free: Any, N: int, K: int, tangential_q: int, radial_q: int
) -> Any:
    import torch

    points, weights = route_a.periodic_t4_quadrature(tangential_q)
    rho, radial_weights = route_a.gauss_legendre_unit_interval(radial_q)
    total = torch.zeros(len(route_a.OUTPUT_NAMES), dtype=route_a.DTYPE)
    for start in range(0, points.shape[0], CHUNK_SIZE):
        components = route_a.relative_action_components_on_nodes(
            free,
            N,
            K,
            points[start:start + CHUNK_SIZE],
            weights[start:start + CHUNK_SIZE],
            rho,
            radial_weights,
        )
        total += torch.stack(
            tuple(components[name] for name in route_a.OUTPUT_NAMES)
        ).detach()
    return total


def _pair_residual(
    left: Mapping[str, float],
    right: Mapping[str, float],
    names: tuple[str, ...],
    atol: float,
    rtol: float,
) -> Mapping[str, Any]:
    rows = {}
    maximum_ratio = 0.0
    for name in names:
        difference = abs(float(right[name]) - float(left[name]))
        tolerance = atol + rtol * max(abs(float(left[name])), abs(float(right[name])))
        ratio = difference / tolerance
        maximum_ratio = max(maximum_ratio, ratio)
        rows[name] = {
            "left": float(left[name]),
            "right": float(right[name]),
            "absolute_difference": difference,
            "fixed_tolerance": tolerance,
            "difference_over_tolerance": ratio,
        }
    return {
        "rows": rows,
        "maximum_difference_over_tolerance": maximum_ratio,
        "pass": maximum_ratio <= 1.0,
    }


def build_payload() -> Mapping[str, Any]:
    base = load_base_wrapper()
    route_a = base.load_route_a()
    bundle = load_bundle(route_a)
    records = []
    with _profile_patch(route_a):
        for member in bundle["primary_members"]:
            N, K = int(member["N"]), int(member["K"])
            free = route_a.decode_f64le(
                member["authoritative_free_central_f64le"], label=f"N{N}.central"
            )
            curve = _joint(member)
            tangent = route_a.decode_f64le(
                curve["authoritative_free_tangent_f64le"], label=f"N{N}.joint"
            )
            quadrature = route_a.QuadratureSpec(TANGENTIAL_Q, RADIAL_JVP_Q)
            value, jvp = route_a.action_value_and_jvp_chunked(
                free,
                tangent,
                N,
                K,
                quadrature,
                tangential_chunk_size=CHUNK_SIZE,
            )
            central_by_radial = {
                str(RADIAL_JVP_Q): route_a._float_record(value)
            }
            for radial_q in RADIAL_REFINEMENT:
                if radial_q != RADIAL_JVP_Q:
                    central_by_radial[str(radial_q)] = route_a._float_record(
                        _chunked_value(route_a, free, N, K, TANGENTIAL_Q, radial_q)
                    )
            radial_final = _pair_residual(
                central_by_radial["10"],
                central_by_radial["12"],
                route_a.OUTPUT_NAMES,
                RADIAL_ATOL,
                RADIAL_RTOL,
            )
            diagnostics = route_a.action_sampling_diagnostics(free, N, K, quadrature)
            records.append(
                {
                    "member_id": member["member_id"],
                    "N": N,
                    "K": K,
                    "free_dimension": int(free.numel()),
                    "central_S_rel_components_by_radial_order": central_by_radial,
                    "radial_Q10_vs_Q12": radial_final,
                    "AD_JVP_by_component_at_Q5_R10": route_a._float_record(jvp),
                    "action_node_diagnostics_at_Q5_R10": diagnostics,
                    "authoritative_free_central_sha256": member[
                        "authoritative_free_central_f64le"
                    ]["sha256"],
                    "authoritative_free_tangent_sha256": curve[
                        "authoritative_free_tangent_f64le"
                    ]["sha256"],
                }
            )

        worst = next(row for row in records if row["N"] == 3)
        member3 = next(row for row in bundle["primary_members"] if row["N"] == 3)
        free3 = route_a.decode_f64le(
            member3["authoritative_free_central_f64le"], label="N3.tangential_refinement"
        )
        central_by_tangential = {
            str(q): route_a._float_record(
                _chunked_value(route_a, free3, 3, 3, q, RADIAL_JVP_Q)
            )
            for q in TANGENTIAL_REFINEMENT
        }
        tangential_final = _pair_residual(
            central_by_tangential["5"],
            central_by_tangential["7"],
            route_a.OUTPUT_NAMES,
            TANGENTIAL_ATOL,
            TANGENTIAL_RTOL,
        )
        worst["tangential_Q3_Q5_Q7_at_R10"] = central_by_tangential
        worst["tangential_Q5_vs_Q7"] = tangential_final

    radial_pass = all(row["radial_Q10_vs_Q12"]["pass"] for row in records)
    tangential_pass = bool(tangential_final["pass"])
    return {
        "schema": SCHEMA,
        "classification": "theory_only;route_A;C2_radial;N1_N2_N3;AD_JVP;quadrature_refined;fail_closed",
        "decision": {
            "route_A_C2_multin_raw_evaluations_pass": True,
            "route_A_radial_Q10_Q12_refinement_pass": radial_pass,
            "route_A_tangential_Q5_Q7_refinement_pass": tangential_pass,
            "route_A_finite_quadrature_convergence_pass": radial_pass and tangential_pass,
            "AD_vs_independent_FD5_multin_pass": False,
            "Euler_Green_independent_route_pass": False,
            "continuous_limit_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "fixed_before_run": {
            "tangential_primary_order": TANGENTIAL_Q,
            "radial_AD_JVP_order": RADIAL_JVP_Q,
            "radial_refinement_orders": list(RADIAL_REFINEMENT),
            "tangential_refinement_orders_on_N3": list(TANGENTIAL_REFINEMENT),
            "radial_pair_atol": RADIAL_ATOL,
            "radial_pair_rtol": RADIAL_RTOL,
            "tangential_pair_atol": TANGENTIAL_ATOL,
            "tangential_pair_rtol": TANGENTIAL_RTOL,
            "chunk_size": CHUNK_SIZE,
        },
        "scientific": {"members": records},
        "source_pins": {
            "base_route_A_wrapper_sha256": BASE_ROUTE_WRAPPER_SHA256,
            "frozen_literal_route_A_sha256": base.ROUTE_A_SOURCE_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "literal_v5_2_action_sha256": route_a.V5_2_EXACT_ACTION_SHA256,
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
        "evidence_boundary": "The corrected C2 radial family is differentiated by Torch forward AD for N=1,2,3. Radial and tangential central-action refinements are recorded, but the independent FD5 comparison, Euler-Green identity, continuous limit, red-team, and C1/N1 promotion remain separate and false.",
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
