#!/usr/bin/env python3
"""Independent NumPy/FD5 route on the corrected C2 radial multi-N family."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
ROUTE_B_SOURCE = HERE / (
    "derive_one_omega_topological_so3_numpy_fd5_action_route_b_"
    "v5_6_5_certificate.py"
)
BUNDLE = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_4_c2_radial_primitive_bundle.json"
)
TEST = HERE / "test_one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.json"

ROUTE_B_SOURCE_SHA256 = "6c98724d0e51c1cad16c80303e6ad7625d661bd1c9c56c9ff96c5b8124992909"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
BUNDLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-4-c2-radial-primitive-bundle.v1"
)
SCHEMA = "holo.one-omega-topological-so3-numpy-c2-multin-fd5-v5-6-5-7.v1"
RADIAL_Q = 10
FD5_STEPS = (4.0e-2, 2.0e-2, 1.0e-2)


class C2MultiNRouteBError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def load_route_b() -> Any:
    observed = _sha256(ROUTE_B_SOURCE)
    if observed != ROUTE_B_SOURCE_SHA256:
        raise C2MultiNRouteBError(f"frozen route B drift: {observed}")
    name = "frozen_numpy_route_b_v565_for_c2_multin"
    spec = importlib.util.spec_from_file_location(name, ROUTE_B_SOURCE)
    if spec is None or spec.loader is None:
        raise C2MultiNRouteBError("cannot import frozen route B")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_bundle(route_b: Any) -> Mapping[str, Any]:
    observed = _sha256(BUNDLE)
    if observed != BUNDLE_SHA256:
        raise C2MultiNRouteBError(f"C2 primitive bundle drift: {observed}")
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise C2MultiNRouteBError("C2 primitive schema drift")
    embedded = bundle["payload_sha256"]
    material = {key: value for key, value in bundle.items() if key != "payload_sha256"}
    if _canonical_sha256(material) != embedded:
        raise C2MultiNRouteBError("C2 primitive payload hash drift")
    if bundle["action_contract"]["exact_action_sha256"] != route_b.LITERAL_ACTION_SHA256:
        raise C2MultiNRouteBError("literal action hash mismatch")
    return bundle


def c2_radial_profiles_numpy(rho: np.ndarray, K: int) -> Mapping[str, np.ndarray]:
    """Route-B-owned polynomial formula; imports no Torch/profile helper."""

    r = np.asarray(rho, dtype=float)
    if r.ndim != 1 or np.any((r < 0.0) | (r > 1.0)):
        raise C2MultiNRouteBError("rho must lie in [0,1]")
    h0 = 1.0 - 10.0 * r**3 + 15.0 * r**4 - 6.0 * r**5
    h0_first = -30.0 * r**2 + 60.0 * r**3 - 30.0 * r**4
    h0_second = -60.0 * r + 180.0 * r**2 - 120.0 * r**3
    h1 = r * h0
    h1_first = h0 + r * h0_first
    h1_second = 2.0 * h0_first + r * h0_second
    s = r * (1.0 - r)
    s_first = 1.0 - 2.0 * r
    envelope = 64.0 * s**3
    envelope_first = 192.0 * s**2 * s_first
    envelope_second = 384.0 * s * s_first**2 - 384.0 * s**2
    z = 2.0 * r - 1.0
    bumps = np.empty((r.size, K), dtype=float)
    bumps_first = np.empty_like(bumps)
    bumps_second = np.empty_like(bumps)
    for degree in range(K):
        coefficients = np.zeros(degree + 1, dtype=float)
        coefficients[degree] = 1.0
        first_coefficients = np.polynomial.legendre.legder(coefficients, 1)
        second_coefficients = np.polynomial.legendre.legder(coefficients, 2)
        polynomial = np.polynomial.legendre.legval(z, coefficients)
        polynomial_first = 2.0 * np.polynomial.legendre.legval(z, first_coefficients)
        polynomial_second = 4.0 * np.polynomial.legendre.legval(z, second_coefficients)
        bumps[:, degree] = envelope * polynomial
        bumps_first[:, degree] = envelope_first * polynomial + envelope * polynomial_first
        bumps_second[:, degree] = (
            envelope_second * polynomial
            + 2.0 * envelope_first * polynomial_first
            + envelope * polynomial_second
        )
    return {
        "h0": h0,
        "h0_first": h0_first,
        "h0_second": h0_second,
        "h1": h1,
        "h1_first": h1_first,
        "h1_second": h1_second,
        "bumps": bumps,
        "bumps_first": bumps_first,
        "bumps_second": bumps_second,
    }


@contextmanager
def _route_b_patches(route_b: Any) -> Iterator[None]:
    original_profile = route_b.radial_profiles
    original_role = route_b._pseudospectral_role

    def role(points_per_axis: int, numerical_role: str) -> str:
        if points_per_axis == 1:
            return "constant_mode_exact"
        return original_role(points_per_axis, numerical_role)

    route_b.radial_profiles = c2_radial_profiles_numpy
    route_b._pseudospectral_role = role
    try:
        yield
    finally:
        route_b.radial_profiles = original_profile
        route_b._pseudospectral_role = original_role


def _single_bundle(bundle: Mapping[str, Any], N: int) -> Mapping[str, Any]:
    return {
        "action_contract": bundle["action_contract"],
        "pointwise_decoder_contract": bundle["pointwise_decoder_contract_by_N"][str(N)],
    }


def _joint(member: Mapping[str, Any]) -> Mapping[str, Any]:
    return next(
        curve
        for curve in member["curves"]
        if curve["name"] == "joint_all_primitive_classes_control_candidate"
    )


def _orders(window: Mapping[str, Any], names: tuple[str, ...]) -> Mapping[str, Any]:
    derivatives = [row["FD5_action_directional_derivative"] for row in window["derivatives"]]
    rows = {}
    for name in names:
        coarse_gap = abs(float(derivatives[0][name]) - float(derivatives[1][name]))
        fine_gap = abs(float(derivatives[1][name]) - float(derivatives[2][name]))
        order = (
            math.log(coarse_gap / fine_gap, 2.0)
            if coarse_gap > 0.0 and fine_gap > 0.0
            else None
        )
        rows[name] = {
            "coarse_gap": coarse_gap,
            "fine_gap": fine_gap,
            "observed_order": order,
        }
    return rows


def _richardson(window: Mapping[str, Any], names: tuple[str, ...]) -> Mapping[str, float]:
    coarse = window["derivatives"][1]["FD5_action_directional_derivative"]
    fine = window["derivatives"][2]["FD5_action_directional_derivative"]
    return {
        name: float(fine[name] + (fine[name] - coarse[name]) / 15.0)
        for name in names
    }


def build_payload() -> Mapping[str, Any]:
    route_b = load_route_b()
    bundle = load_bundle(route_b)
    records = []
    with _route_b_patches(route_b):
        for member in bundle["primary_members"]:
            N, K = int(member["N"]), int(member["K"])
            tangential_q = 1 if N == 1 else 5
            local_bundle = _single_bundle(bundle, N)
            free = route_b._decode_f64(member["authoritative_free_central_f64le"])
            curve = _joint(member)
            tangent = route_b._decode_f64(curve["authoritative_free_tangent_f64le"])
            central = route_b.action_evaluation(
                free, local_bundle, member, tangential_q, RADIAL_Q, "refinable"
            )
            window = route_b.affine_fd5_step_window(
                free,
                tangent,
                FD5_STEPS,
                local_bundle,
                member,
                tangential_q,
                RADIAL_Q,
                "refinable",
            )
            records.append(
                {
                    "member_id": member["member_id"],
                    "N": N,
                    "K": K,
                    "tangential_points_per_axis": tangential_q,
                    "tangential_rule": (
                        "constant_mode_exact" if N == 1 else "odd_Q5_refinable_projection"
                    ),
                    "central_S_rel_components": central["components"],
                    "central_pointwise_gluing": central["pointwise_gluing"],
                    "central_lorentzian_inertia": central["lorentzian_inertia"],
                    "FD5_refinement_window": window,
                    "FD5_observed_orders": _orders(window, route_b.OUTPUT_NAMES if hasattr(route_b, "OUTPUT_NAMES") else route_b.ACTION_COMPONENTS + ("S_total",)),
                    "FD5_Richardson_h002_h001": _richardson(
                        window, route_b.ACTION_COMPONENTS + ("S_total",)
                    ),
                    "authoritative_free_central_sha256": member[
                        "authoritative_free_central_f64le"
                    ]["sha256"],
                    "authoritative_free_tangent_sha256": curve[
                        "authoritative_free_tangent_f64le"
                    ]["sha256"],
                }
            )
    return {
        "schema": SCHEMA,
        "classification": "theory_only;route_B;C2_radial;N1_N2_N3;independent_FD5;raw;fail_closed",
        "decision": {
            "route_B_C2_multin_raw_evaluations_pass": True,
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
            "radial_Gauss_order": RADIAL_Q,
            "FD5_steps": list(FD5_STEPS),
            "N1_tangential_rule": "Q1 exact because the N1 basis contains only the constant mode",
            "N2_N3_tangential_points_per_axis": 5,
        },
        "scientific": {"members": records},
        "source_pins": {
            "frozen_literal_route_B_sha256": ROUTE_B_SOURCE_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "literal_v5_2_action_sha256": route_b.LITERAL_ACTION_SHA256,
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
        "evidence_boundary": "Raw NumPy central actions and three-level FD5 windows are evaluated for N=1,2,3 from the corrected primitive family. This route reads no Torch values or comparison tolerances and cannot promote C1/N1 by itself.",
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
