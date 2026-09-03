#!/usr/bin/env python3
"""Torch forward-AD route A on the primitive N=1,2,3 family."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
ROUTE_A_SOURCE = HERE / (
    "derive_one_omega_topological_so3_literal_torch_action_route_a_"
    "v5_6_5_certificate.py"
)
MULTIN_BUNDLE = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_3_multin_primitive_bundle.json"
)
TEST = HERE / "test_one_omega_topological_so3_torch_route_a_multin_v5_6_5_5.py"
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_torch_route_a_multin_v5_6_5_5.json"
)

ROUTE_A_SOURCE_SHA256 = "dfb1692b3af96c1827ad7fd435b0de7a2af89dd7535a328bc49ba5431d492a7c"
MULTIN_BUNDLE_SHA256 = "9ebf92cd760225667137247c65034bd56eccc714be9f3bb15d5a605a51656519"
BUNDLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-3-multin-primitive-bundle.v1"
)
SCHEMA = "holo.one-omega-topological-so3-torch-route-a-multin-v5-6-5-5.v1"
TANGENTIAL_Q = 5
RADIAL_Q = 4
CHUNK_SIZE = 64


class MultiNRouteAError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def load_route_a() -> Any:
    observed = _sha256(ROUTE_A_SOURCE)
    if observed != ROUTE_A_SOURCE_SHA256:
        raise MultiNRouteAError(f"frozen route A drift: {observed}")
    name = "frozen_torch_route_a_v565_for_multin"
    spec = importlib.util.spec_from_file_location(name, ROUTE_A_SOURCE)
    if spec is None or spec.loader is None:
        raise MultiNRouteAError("cannot import frozen route A")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_bundle(route_a: Any) -> Mapping[str, Any]:
    observed = _sha256(MULTIN_BUNDLE)
    if observed != MULTIN_BUNDLE_SHA256:
        raise MultiNRouteAError(f"multi-N primitive bundle drift: {observed}")
    payload = json.loads(MULTIN_BUNDLE.read_text(encoding="utf-8"))
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise MultiNRouteAError("multi-N primitive schema drift")
    embedded = payload["payload_sha256"]
    material = {key: value for key, value in payload.items() if key != "payload_sha256"}
    if _canonical_sha256(material) != embedded:
        raise MultiNRouteAError("multi-N primitive payload hash drift")
    action = payload["action_contract"]
    if action["exact_action"] != route_a.EXACT_ACTION:
        raise MultiNRouteAError("literal v5.2 action text mismatch")
    if action["exact_action_sha256"] != route_a.V5_2_EXACT_ACTION_SHA256:
        raise MultiNRouteAError("literal v5.2 action hash mismatch")
    return payload


def _joint(member: Mapping[str, Any]) -> Mapping[str, Any]:
    selected = [
        row
        for row in member["curves"]
        if row["name"] == "joint_all_primitive_classes_control_candidate"
    ]
    if len(selected) != 1:
        raise MultiNRouteAError("unique joint primitive curve missing")
    return selected[0]


def build_payload() -> Mapping[str, Any]:
    route_a = load_route_a()
    bundle = load_bundle(route_a)
    quadrature = route_a.QuadratureSpec(TANGENTIAL_Q, RADIAL_Q)
    records = []
    for member in bundle["primary_members"]:
        N = int(member["N"])
        K = int(member["K"])
        contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
        layout = route_a.free_layout(N, K)
        if int(contract["free_coordinate_dimension"]) != layout.size:
            raise MultiNRouteAError(f"free layout mismatch at N={N}")
        free = route_a.decode_f64le(
            member["authoritative_free_central_f64le"],
            label=f"N{N}.central",
        )
        curve = _joint(member)
        tangent = route_a.decode_f64le(
            curve["authoritative_free_tangent_f64le"],
            label=f"N{N}.joint_tangent",
        )
        value, jvp = route_a.action_value_and_jvp_chunked(
            free,
            tangent,
            N,
            K,
            quadrature,
            tangential_chunk_size=CHUNK_SIZE,
        )
        diagnostics = route_a.action_sampling_diagnostics(free, N, K, quadrature)
        records.append(
            {
                "member_id": member["member_id"],
                "N": N,
                "K": K,
                "free_dimension": layout.size,
                "authoritative_free_central_sha256": member[
                    "authoritative_free_central_f64le"
                ]["sha256"],
                "authoritative_free_tangent_sha256": curve[
                    "authoritative_free_tangent_f64le"
                ]["sha256"],
                "S_rel_components": route_a._float_record(value),
                "AD_JVP_by_component": route_a._float_record(jvp),
                "action_node_diagnostics": diagnostics,
            }
        )
    return {
        "schema": SCHEMA,
        "classification": "theory_only;route_A;forward_AD;N1_N2_N3;finite_spectral;fail_closed",
        "decision": {
            "route_A_multin_raw_evaluations_pass": True,
            "AD_vs_independent_FD5_multin_pass": False,
            "Euler_Green_independent_route_pass": False,
            "continuous_limit_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "quadrature": {
            "tangential_periodic_points_per_axis": TANGENTIAL_Q,
            "radial_Gauss_order": RADIAL_Q,
            "tangential_chunk_size": CHUNK_SIZE,
        },
        "scientific": {"members": records},
        "source_pins": {
            "route_A_source_sha256": ROUTE_A_SOURCE_SHA256,
            "multi_N_primitive_bundle_sha256": MULTIN_BUNDLE_SHA256,
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
        "evidence_boundary": "Raw Torch forward-AD values are evaluated independently for N=1,2,3 from primitive configurations. No comparison, convergence theorem, Euler-Green identity, or C1/N1 promotion is inferred by this route alone.",
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
