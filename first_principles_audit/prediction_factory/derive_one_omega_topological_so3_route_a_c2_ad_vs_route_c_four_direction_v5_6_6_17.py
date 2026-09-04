#!/usr/bin/env python3
"""Sampled fixed-Q cross-route check on the four published C2 tangents.

For each pinned N=1,2,3 member and each of its four published free-data
tangents, this gate recomputes

* the forward-AD JVP of Route A's discrete Qtheta=5, Qrho=10 action; and
* Route C's precision-stabilized local free-direction estimate at matched
  fixed orders.

Route A uses a 5^4 tensor grid while Route C uses the reduced theta=x0+x1
grid.  The receipt separately proves the finite-grid multiplicity reduction
for the restricted published family and records the numerical GL10
node/weight agreement; it does not call the two quadrature implementations
identical.

The 21 outputs are aligned by component name.  This is a finite, sampled,
fixed-quadrature comparison.  In particular it is not a symbolic
same-functional identity, a bound on Route C's finite-difference bias, or an
N-to-infinity/continuum bridge.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import math
import multiprocessing
import sys
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"

C2_SOURCE = HERE / "derive_one_omega_topological_so3_torch_c2_multin_v5_6_5_6.py"
C2_TEST = HERE / "test_one_omega_topological_so3_torch_c2_multin_v5_6_5_6.py"
C2_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_torch_c2_multin_v5_6_5_6.json"
ROUTE_A_WRAPPER_SOURCE = HERE / "derive_one_omega_topological_so3_torch_route_a_multin_v5_6_5_5.py"
ROUTE_A_SOURCE = HERE / "derive_one_omega_topological_so3_literal_torch_action_route_a_v5_6_5_certificate.py"
ROUTE_C_STABLE_SOURCE = HERE / "derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5.py"
ROUTE_C_STABLE_TEST = HERE / "test_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5.py"
ROUTE_C_STABLE_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5.json"
ROUTE_C_SOURCE = HERE / "derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3.py"
BUNDLE = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
THREE_WAY_SOURCE = HERE / "derive_one_omega_topological_so3_ad_fd5_route_c_three_way_v5_6_6_6.py"
THREE_WAY_TEST = HERE / "test_one_omega_topological_so3_ad_fd5_route_c_three_way_v5_6_6_6.py"
THREE_WAY_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_ad_fd5_route_c_three_way_v5_6_6_6.json"
V15_SOURCE = HERE / "derive_one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.py"
V15_TEST = HERE / "test_one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.py"
V15_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.json"

TEST = HERE / "test_one_omega_topological_so3_route_a_c2_ad_vs_route_c_four_direction_v5_6_6_17.py"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_route_a_c2_ad_vs_route_c_four_direction_v5_6_6_17.json"

C2_SOURCE_SHA256 = "2c3fb9adbaad90a77fd5cf1fd7df9bd61c2e4d1e92dbffeff4f3ffaa31ab7f6b"
C2_TEST_SHA256 = "6600fe91723b48c6b1ecb47bf96d67152d46c0c40f75f6717b2017e60f4302a0"
C2_ARTIFACT_SHA256 = "d0db75f97c580e417e2032211134546695691598714f0ace65db8f24afc11cdb"
ROUTE_A_WRAPPER_SOURCE_SHA256 = "5c24361ba431888ccaf473ba2ab17aa00354258ba70c31bb81bfb77ebf6d56b6"
ROUTE_A_SOURCE_SHA256 = "dfb1692b3af96c1827ad7fd435b0de7a2af89dd7535a328bc49ba5431d492a7c"
ROUTE_C_STABLE_SOURCE_SHA256 = "5cf9c64fe8af45b55899275b2af1a9d55c706a138479e2cbd3a47ca4b270eca8"
ROUTE_C_STABLE_TEST_SHA256 = "3d4ab86a1150460ea55315eaf66c4529307f2b968d1b8481696ba0b09f983a06"
ROUTE_C_STABLE_ARTIFACT_SHA256 = "06ad302a03d17e4ea718c9ab801113807a7f66c71102e69486f7869130f77654"
ROUTE_C_SOURCE_SHA256 = "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
THREE_WAY_SOURCE_SHA256 = "fd4c4a21358742017d79af1fcfdd340cf90609c96172fd82c5c1dc04b8f0e8e5"
THREE_WAY_TEST_SHA256 = "e1e401241180b4fd47245a15d31142e54829da3708767f42b64f1e7b87cbbea8"
THREE_WAY_ARTIFACT_SHA256 = "8ecc218622240ddb29521be237c33d81c46638544ebe1ff16b7b7e8fa7333092"

# Frozen after the sampled-scope correction in commit e1fcdaa.  The receipt is
# supporting sampled evidence only; its symbolic same-functional gate is red.
V15_SOURCE_SHA256 = "ca099da9f4f98a2a398cc0535ef2cd85e2e417e52fd8a7af0b87a3ef12664956"
V15_TEST_SHA256 = "1527d719692ed2f287a6edf66e2c0eb925b9fbae702ffe263b26c60fcb7960e3"
V15_ARTIFACT_SHA256 = "09a98c369bfce6f04670b5be6443e78b32c0083e53e478c71f7787c364d26f7f"

SCHEMA = "holo.one-omega-topological-so3-route-a-c2-ad-vs-route-c-four-direction-v5-6-6-17.v1"
V15_SCHEMA = "holo.one-omega-topological-so3-route-c-same-functional-pointwise-v5-6-6-15.v1"
THREE_WAY_SCHEMA = "holo.one-omega-topological-so3-ad-fd5-route-c-three-way-v5-6-6-6.v1"

CURVE_NAMES = (
    "compact_bulk_SO3_horizontal_candidate",
    "embedding_motion_SO3_horizontal_candidate",
    "free_B_SO3_horizontal_candidate",
    "joint_all_primitive_classes_control_candidate",
)
EXPECTED_COMPONENT_NAMES = (
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
    "S_total",
)
MEMBER_N = (1, 2, 3)
TANGENTIAL_ORDER = 5
RADIAL_ORDER = 10
FREE_STEP = 2.0e-3
CHUNK_SIZE = 64
WORKERS = 3
PAIRWISE_ATOL = 1.0e-8
PAIRWISE_RTOL = 1.0e-11
ACTIVE_SIGN_THRESHOLD = 1.0e-6
ADDITIVITY_ATOL = 1.0e-9
ADDITIVITY_RTOL = 1.0e-12
RADIAL_ALIGNMENT_ATOL = 1.0e-14
REPRODUCTION_ATOL = 1.0e-10


class FourDirectionCrossRouteError(RuntimeError):
    """A pinned input or finite comparison contract drifted."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def _assert_hash(path: Path, expected: str) -> None:
    observed = _sha256(path)
    if observed != expected:
        raise FourDirectionCrossRouteError(
            f"pinned input drift for {path.name}: expected {expected}, observed {observed}"
        )


def _read_pinned_json(path: Path, expected_hash: str, expected_schema: str) -> Mapping[str, Any]:
    _assert_hash(path, expected_hash)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != expected_schema:
        raise FourDirectionCrossRouteError(f"schema drift for {path.name}")
    return payload


def _preflight() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    pins = (
        (C2_SOURCE, C2_SOURCE_SHA256),
        (C2_TEST, C2_TEST_SHA256),
        (C2_ARTIFACT, C2_ARTIFACT_SHA256),
        (ROUTE_A_WRAPPER_SOURCE, ROUTE_A_WRAPPER_SOURCE_SHA256),
        (ROUTE_A_SOURCE, ROUTE_A_SOURCE_SHA256),
        (ROUTE_C_STABLE_SOURCE, ROUTE_C_STABLE_SOURCE_SHA256),
        (ROUTE_C_STABLE_TEST, ROUTE_C_STABLE_TEST_SHA256),
        (ROUTE_C_STABLE_ARTIFACT, ROUTE_C_STABLE_ARTIFACT_SHA256),
        (ROUTE_C_SOURCE, ROUTE_C_SOURCE_SHA256),
        (BUNDLE, BUNDLE_SHA256),
        (THREE_WAY_SOURCE, THREE_WAY_SOURCE_SHA256),
        (THREE_WAY_TEST, THREE_WAY_TEST_SHA256),
        (V15_SOURCE, V15_SOURCE_SHA256),
        (V15_TEST, V15_TEST_SHA256),
    )
    for path, expected in pins:
        _assert_hash(path, expected)

    v15 = _read_pinned_json(V15_ARTIFACT, V15_ARTIFACT_SHA256, V15_SCHEMA)
    v15_decision = v15["decision"]
    required_v15_true = (
        "route_c_sector_partition_and_literal_total_term_names_static_audit_pass",
        "route_c_bulk_and_ghy_densities_match_pinned_literal_implementation_sampled_within_tolerance_pass",
        "route_c_interface_densities_match_pinned_literal_implementation_sampled_within_tolerance_pass",
        "route_c_closed_form_coefficients_match_literal_formula_strings_sampled_pass",
    )
    if not all(v15_decision.get(key) is True for key in required_v15_true):
        raise FourDirectionCrossRouteError("v5.6.6.15 sampled density receipt is not green")
    if v15_decision.get("same_functional_symbolic_identity_pass") is not False:
        raise FourDirectionCrossRouteError("v5.6.6.15 symbolic identity must remain false")

    three_way = _read_pinned_json(
        THREE_WAY_ARTIFACT, THREE_WAY_ARTIFACT_SHA256, THREE_WAY_SCHEMA
    )
    if three_way["decision"].get("AD_FD5_Route_C_three_way_comparison_pass") is not True:
        raise FourDirectionCrossRouteError("v5.6.6.6 joint-direction receipt is not green")
    return v15, three_way


def _float_map(names: tuple[str, ...], values: Any) -> dict[str, float]:
    sequence = values.detach().cpu().tolist()
    if len(sequence) != len(names):
        raise FourDirectionCrossRouteError("route-A output length drift")
    return {name: float(value) for name, value in zip(names, sequence)}


def _cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    names = sorted(left)
    dot = sum(float(left[name]) * float(right[name]) for name in names)
    left_norm = math.sqrt(sum(float(left[name]) ** 2 for name in names))
    right_norm = math.sqrt(sum(float(right[name]) ** 2 for name in names))
    if left_norm == 0.0 or right_norm == 0.0:
        raise FourDirectionCrossRouteError("zero component vector")
    return dot / (left_norm * right_norm)


def compare_component_maps(
    route_a: Mapping[str, float], route_c: Mapping[str, float]
) -> Mapping[str, Any]:
    if set(route_a) != set(route_c):
        raise FourDirectionCrossRouteError("cross-route component-name drift")
    if any(
        not math.isfinite(float(value))
        for values in (route_a, route_c)
        for value in values.values()
    ):
        raise FourDirectionCrossRouteError("non-finite cross-route component")
    rows: dict[str, Any] = {}
    all_pass = True
    for name in sorted(route_a):
        left = float(route_a[name])
        right = float(route_c[name])
        scale = max(abs(left), abs(right))
        tolerance = PAIRWISE_ATOL + PAIRWISE_RTOL * scale
        difference = right - left
        active = scale >= ACTIVE_SIGN_THRESHOLD
        sign_pass = (not active) or left == 0.0 or right == 0.0 or math.copysign(1.0, left) == math.copysign(1.0, right)
        row_pass = abs(difference) <= tolerance and sign_pass
        rows[name] = {
            "Route_A_C2_AD": left,
            "Route_C_precision_stabilized_free_directional_estimate": right,
            "Route_C_minus_Route_A": difference,
            "absolute_difference": abs(difference),
            "fixed_tolerance": tolerance,
            "difference_over_tolerance": abs(difference) / tolerance,
            "active_for_sign_check": active,
            "same_sign_when_active": sign_pass,
            "pass": row_pass,
        }
        all_pass = all_pass and row_pass
    return {
        "rows": rows,
        "maximum_absolute_difference": max(row["absolute_difference"] for row in rows.values()),
        "maximum_difference_over_tolerance": max(row["difference_over_tolerance"] for row in rows.values()),
        "cosine": _cosine(route_a, route_c),
        "pass": all_pass,
    }


def compare_reproduction_maps(
    recomputed: Mapping[str, float], pinned: Mapping[str, float]
) -> Mapping[str, Any]:
    if set(recomputed) != set(pinned):
        raise FourDirectionCrossRouteError("reproduction component-name drift")
    rows: dict[str, Any] = {}
    for name in sorted(recomputed):
        current = float(recomputed[name])
        previous = float(pinned[name])
        if not math.isfinite(current) or not math.isfinite(previous):
            raise FourDirectionCrossRouteError("non-finite reproduction component")
        difference = abs(current - previous)
        rows[name] = {
            "recomputed": current,
            "pinned": previous,
            "absolute_difference": difference,
            "fixed_absolute_tolerance": REPRODUCTION_ATOL,
            "pass": difference <= REPRODUCTION_ATOL,
        }
    return {
        "rows": rows,
        "maximum_absolute_difference": max(
            row["absolute_difference"] for row in rows.values()
        ),
        "fixed_absolute_tolerance": REPRODUCTION_ATOL,
        "pass": all(row["pass"] for row in rows.values()),
    }


def sector_additivity(values: Mapping[str, float]) -> Mapping[str, Any]:
    if set(values) != set(EXPECTED_COMPONENT_NAMES):
        raise FourDirectionCrossRouteError("21-sector action ledger drift")
    if any(not math.isfinite(float(value)) for value in values.values()):
        raise FourDirectionCrossRouteError("non-finite sector ledger")
    subtotal = math.fsum(
        float(values[name]) for name in EXPECTED_COMPONENT_NAMES if name != "S_total"
    )
    total = float(values["S_total"])
    residual = total - subtotal
    scale = max(abs(total), abs(subtotal))
    tolerance = ADDITIVITY_ATOL + ADDITIVITY_RTOL * scale
    return {
        "reported_S_total": total,
        "sum_of_20_sectors": subtotal,
        "residual": residual,
        "fixed_tolerance": tolerance,
        "pass": abs(residual) <= tolerance,
    }


def sign_flip_canary_rejected(
    route_a: Mapping[str, float], route_c: Mapping[str, float]
) -> Mapping[str, Any]:
    component = max(
        (name for name in route_c if name != "S_total"),
        key=lambda name: abs(float(route_c[name])),
    )
    mutant = dict(route_c)
    mutant[component] = -float(mutant[component])
    comparison = compare_component_maps(route_a, mutant)
    return {
        "mutated_component": component,
        "mutation": "sign_flip",
        "mutant_comparison_pass": bool(comparison["pass"]),
        "rejected": not bool(comparison["pass"]),
    }


def positional_zip_canary_rejected(
    route_a: Mapping[str, float],
    route_c: Mapping[str, float],
    route_a_order: tuple[str, ...],
    route_c_order: tuple[str, ...],
) -> Mapping[str, Any]:
    if set(route_a_order) != set(route_c_order) or set(route_a_order) != set(route_a):
        raise FourDirectionCrossRouteError("component-order canary name drift")
    if route_a_order == route_c_order:
        raise FourDirectionCrossRouteError("component-order canary requires distinct route orders")
    positional_mutant = {
        route_a_name: float(route_c[route_c_name])
        for route_a_name, route_c_name in zip(route_a_order, route_c_order)
    }
    comparison = compare_component_maps(route_a, positional_mutant)
    return {
        "Route_A_component_order": list(route_a_order),
        "Route_C_component_order": list(route_c_order),
        "orders_are_distinct": True,
        "positional_zip_mutant_comparison_pass": bool(comparison["pass"]),
        "rejected": not bool(comparison["pass"]),
    }


def restricted_t4_to_theta_grid_reduction(order: int) -> Mapping[str, Any]:
    """Exact counting ledger for functions of theta=x0+x1 on the Q^4 grid."""

    if isinstance(order, bool) or not isinstance(order, int) or order <= 0:
        raise FourDirectionCrossRouteError("grid order must be a positive integer")
    multiplicities = [0] * order
    for i0 in range(order):
        for i1 in range(order):
            for _i2 in range(order):
                for _i3 in range(order):
                    multiplicities[(i0 + i1) % order] += 1
    expected = order**3
    return {
        "Route_A_tensor_node_count": order**4,
        "Route_C_reduced_theta_node_count": order,
        "residue_multiplicities": multiplicities,
        "expected_multiplicity_per_theta_residue": expected,
        "Route_A_aggregate_weight_over_T4_volume_exact": f"{expected}/{order**4}=1/{order}",
        "Route_C_weight_over_T4_volume_exact": f"1/{order}",
        "multiplicity_and_normalized_weight_identity_pass": bool(
            multiplicities == [expected] * order
        ),
        "scope": "exact for sampled functions depending only on theta=x0+x1 on the matched Q grid",
    }


def selected_bundle_theta_only_wavevector_audit() -> Mapping[str, Any]:
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    rows: dict[str, Any] = {}
    for N in MEMBER_N:
        basis = bundle["pointwise_decoder_contract_by_N"][str(N)]["basis"]
        wavevectors = [tuple(int(value) for value in row) for row in basis["mode_wavevectors"]]
        row_pass = all(
            len(vector) == 4
            and vector[0] == vector[1]
            and vector[2] == 0
            and vector[3] == 0
            for vector in wavevectors
        )
        rows[str(N)] = {
            "labels": list(basis["labels"]),
            "mode_wavevectors": [list(vector) for vector in wavevectors],
            "depends_only_on_theta_x0_plus_x1_pass": row_pass,
        }
    return {
        "members": rows,
        "pass": all(row["depends_only_on_theta_x0_plus_x1_pass"] for row in rows.values()),
        "scope": "static audit of the byte-pinned selected bundle basis; not a nodewise equality audit of the two action implementations",
    }


def _radial_gl_alignment(route_a: Any) -> Mapping[str, Any]:
    import numpy as np

    torch_nodes, torch_weights = route_a.gauss_legendre_unit_interval(RADIAL_ORDER)
    numpy_raw_nodes, numpy_raw_weights = np.polynomial.legendre.leggauss(RADIAL_ORDER)
    numpy_nodes = 0.5 * (numpy_raw_nodes + 1.0)
    numpy_weights = 0.5 * numpy_raw_weights
    torch_nodes_np = torch_nodes.detach().cpu().numpy()
    torch_weights_np = torch_weights.detach().cpu().numpy()
    node_difference = float(np.max(np.abs(torch_nodes_np - numpy_nodes)))
    weight_difference = float(np.max(np.abs(torch_weights_np - numpy_weights)))
    return {
        "order": RADIAL_ORDER,
        "Route_A_implementation": "Torch symmetric-tridiagonal Golub-Welsch",
        "Route_C_implementation": "NumPy leggauss mapped to (0,1)",
        "maximum_node_absolute_difference": node_difference,
        "maximum_weight_absolute_difference": weight_difference,
        "numeric_match_tolerance": RADIAL_ALIGNMENT_ATOL,
        "numeric_match_pass": bool(
            max(node_difference, weight_difference) <= RADIAL_ALIGNMENT_ATOL
        ),
    }


def _load_worker_modules() -> tuple[Any, Any, Any, Mapping[str, Any]]:
    # Check before importing so a drifted implementation never executes.
    _assert_hash(C2_SOURCE, C2_SOURCE_SHA256)
    _assert_hash(ROUTE_A_WRAPPER_SOURCE, ROUTE_A_WRAPPER_SOURCE_SHA256)
    _assert_hash(ROUTE_A_SOURCE, ROUTE_A_SOURCE_SHA256)
    _assert_hash(ROUTE_C_STABLE_SOURCE, ROUTE_C_STABLE_SOURCE_SHA256)
    _assert_hash(ROUTE_C_SOURCE, ROUTE_C_SOURCE_SHA256)
    _assert_hash(BUNDLE, BUNDLE_SHA256)

    # Under multiprocessing "spawn", direct execution gives the child the
    # prediction_factory directory as sys.path[0].  Insert the pinned repo root
    # so package imports resolve identically for direct and ``python -m`` runs.
    repo_text = str(REPO)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)

    from first_principles_audit.prediction_factory import (
        derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5
        as route_c_stable,
    )
    from first_principles_audit.prediction_factory import (
        derive_one_omega_topological_so3_torch_c2_multin_v5_6_5_6 as c2,
    )

    base = c2.load_base_wrapper()
    route_a = base.load_route_a()
    bundle = c2.load_bundle(route_a)
    route_c_bundle = route_c_stable.route_c.load_bundle()
    if bundle.get("payload_sha256") != route_c_bundle.get("payload_sha256"):
        raise FourDirectionCrossRouteError("Route A and Route C loaded different bundles")

    import torch

    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        # The child normally sets this once; retain fail-safe compatibility if
        # a future Torch build initializes the interop pool during import.
        pass
    return c2, route_a, route_c_stable, bundle


def validate_route_c_record_metadata(
    record: Mapping[str, Any], member: Mapping[str, Any], curve_name: str
) -> Mapping[str, Any]:
    expected = {
        "N": int(member["N"]),
        "K": int(member["K"]),
        "member_id": member["member_id"],
        "curve_name": curve_name,
        "tangential_order": TANGENTIAL_ORDER,
        "radial_order": RADIAL_ORDER,
        "free_step": FREE_STEP,
    }
    observed = {key: record.get(key) for key in expected}
    if observed != expected:
        raise FourDirectionCrossRouteError(
            f"Route-C evaluation metadata drift: expected {expected}, observed {observed}"
        )
    return observed


def evaluate_member_worker(N: int) -> Mapping[str, Any]:
    c2, route_a, route_c_stable, bundle = _load_worker_modules()
    selected = [member for member in bundle["primary_members"] if int(member["N"]) == N]
    if len(selected) != 1:
        raise FourDirectionCrossRouteError(f"unique member N={N} missing")
    member = selected[0]
    K = int(member["K"])
    curves = {curve["name"]: curve for curve in member["curves"]}
    if set(curves) != set(CURVE_NAMES):
        raise FourDirectionCrossRouteError(f"published curve set drift at N={N}")

    free = route_a.decode_f64le(
        member["authoritative_free_central_f64le"], label=f"v17.N{N}.central"
    )
    layout = route_a.free_layout(N, K)
    if tuple(free.shape) != (layout.size,):
        raise FourDirectionCrossRouteError(f"free-data layout drift at N={N}")
    quadrature = route_a.QuadratureSpec(TANGENTIAL_ORDER, RADIAL_ORDER)
    radial_alignment = _radial_gl_alignment(route_a)
    if not radial_alignment["numeric_match_pass"]:
        raise FourDirectionCrossRouteError("Route A/Route C GL10 nodes or weights drifted")
    curve_records = []
    central_reference: Mapping[str, float] | None = None
    with c2._profile_patch(route_a):
        for curve_name in CURVE_NAMES:
            curve = curves[curve_name]
            tangent = route_a.decode_f64le(
                curve["authoritative_free_tangent_f64le"],
                label=f"v17.N{N}.{curve_name}",
            )
            value, jvp = route_a.action_value_and_jvp_chunked(
                free,
                tangent,
                N,
                K,
                quadrature,
                tangential_chunk_size=CHUNK_SIZE,
            )
            output_names = tuple(route_a.OUTPUT_NAMES)
            if output_names != EXPECTED_COMPONENT_NAMES:
                raise FourDirectionCrossRouteError("Route-A component order/name drift")
            route_a_value = _float_map(output_names, value)
            route_a_jvp = _float_map(output_names, jvp)
            if central_reference is None:
                central_reference = route_a_value
            elif route_a_value != central_reference:
                raise FourDirectionCrossRouteError(
                    f"Route-A central action changed across tangents at N={N}"
                )

            route_c_record = route_c_stable.evaluate_direct_member_stable(
                bundle,
                member,
                curve_name=curve_name,
                tangential_order=TANGENTIAL_ORDER,
                radial_order=RADIAL_ORDER,
                free_step=FREE_STEP,
            )
            route_c_metadata = validate_route_c_record_metadata(
                route_c_record, member, curve_name
            )
            route_c_jvp = {
                name: float(value)
                for name, value in route_c_record[
                    "direct_local_free_JVP_by_component"
                ].items()
            }
            if set(route_c_jvp) != set(EXPECTED_COMPONENT_NAMES):
                raise FourDirectionCrossRouteError("Route-C component-name drift")
            comparison = compare_component_maps(route_a_jvp, route_c_jvp)
            route_a_additivity = sector_additivity(route_a_jvp)
            route_c_additivity = sector_additivity(route_c_jvp)
            canary = sign_flip_canary_rejected(route_a_jvp, route_c_jvp)
            positional_canary = positional_zip_canary_rejected(
                route_a_jvp,
                route_c_jvp,
                output_names,
                tuple(route_c_jvp),
            )
            curve_records.append(
                {
                    "curve_name": curve_name,
                    "authoritative_free_tangent_sha256": curve[
                        "authoritative_free_tangent_f64le"
                    ]["sha256"],
                    "Route_A_C2_AD_JVP": route_a_jvp,
                    "Route_C_precision_stabilized_free_directional_estimate": route_c_jvp,
                    "Route_C_evaluation_metadata": route_c_metadata,
                    "comparison": comparison,
                    "sector_additivity": {
                        "Route_A_C2_AD": route_a_additivity,
                        "Route_C_precision_stabilized": route_c_additivity,
                    },
                    "sign_flip_canary": canary,
                    "positional_zip_component_order_canary": positional_canary,
                    "curve_sampled_fixed_Q_cross_route_pass": bool(
                        comparison["pass"]
                        and route_a_additivity["pass"]
                        and route_c_additivity["pass"]
                        and canary["rejected"]
                        and positional_canary["rejected"]
                    ),
                }
            )

    if central_reference is None:
        raise FourDirectionCrossRouteError(f"no curves evaluated at N={N}")
    return {
        "N": N,
        "K": K,
        "member_id": member["member_id"],
        "free_dimension": layout.size,
        "authoritative_free_central_sha256": member[
            "authoritative_free_central_f64le"
        ]["sha256"],
        "Route_A_C2_central_action_components_at_fixed_Q": central_reference,
        "radial_GL10_alignment": radial_alignment,
        "curves": curve_records,
        "member_sampled_fixed_Q_cross_route_pass": all(
            bool(curve["curve_sampled_fixed_Q_cross_route_pass"])
            for curve in curve_records
        ),
    }


def _joint_reproduction(
    members: list[Mapping[str, Any]], three_way: Mapping[str, Any]
) -> Mapping[str, Any]:
    fixed = three_way["fixed_before_acceptance_run"]
    fixed_contract_pass = fixed == {
        "active_sign_threshold": ACTIVE_SIGN_THRESHOLD,
        "all_three_pairs_required_componentwise": True,
        "pairwise_absolute_tolerance": PAIRWISE_ATOL,
        "pairwise_relative_tolerance": PAIRWISE_RTOL,
        "radial_order": RADIAL_ORDER,
        "tangential_order_per_axis": TANGENTIAL_ORDER,
    }
    if not fixed_contract_pass:
        raise FourDirectionCrossRouteError("pinned v5.6.6.6 fixed contract drift")
    previous = {
        int(row["N"]): row for row in three_way["scientific"]["members"]
    }
    if set(previous) != set(MEMBER_N):
        raise FourDirectionCrossRouteError("pinned v5.6.6.6 member set drift")
    records = []
    for member in members:
        N = int(member["N"])
        joint = next(
            curve
            for curve in member["curves"]
            if curve["curve_name"] == "joint_all_primitive_classes_control_candidate"
        )
        old = previous[N]
        lineage_pass = bool(
            int(old["K"]) == int(member["K"])
            and old["member_id"] == member["member_id"]
            and old["authoritative_free_central_sha256"]
            == member["authoritative_free_central_sha256"]
            and old["authoritative_free_tangent_sha256"]
            == joint["authoritative_free_tangent_sha256"]
            and old["quadrature"]
            == {
                "radial_order": RADIAL_ORDER,
                "tangential_order_per_axis": TANGENTIAL_ORDER,
            }
        )
        if not lineage_pass:
            raise FourDirectionCrossRouteError(
                f"pinned v5.6.6.6 lineage/quadrature drift at N={N}"
            )
        ad = compare_reproduction_maps(
            joint["Route_A_C2_AD_JVP"], old["AD_JVP"]
        )
        route_c = compare_reproduction_maps(
            joint["Route_C_precision_stabilized_free_directional_estimate"],
            old["Route_C_precision_stabilized_JVP"],
        )
        records.append(
            {
                "N": N,
                "lineage_and_quadrature_match": lineage_pass,
                "Route_A_C2_AD_reproduction": ad,
                "Route_C_precision_stabilized_reproduction": route_c,
                "pass": bool(lineage_pass and ad["pass"] and route_c["pass"]),
            }
        )
    return {
        "pinned_fixed_contract_match": fixed_contract_pass,
        "fixed_absolute_reproduction_tolerance": REPRODUCTION_ATOL,
        "records": records,
        "pass": all(row["pass"] for row in records),
    }


def build_payload() -> Mapping[str, Any]:
    _v15, three_way = _preflight()
    context = multiprocessing.get_context("spawn")
    by_n: dict[int, Mapping[str, Any]] = {}
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=WORKERS, mp_context=context
    ) as executor:
        futures = {
            executor.submit(evaluate_member_worker, N): N for N in MEMBER_N
        }
        for future in concurrent.futures.as_completed(futures):
            N = futures[future]
            by_n[N] = future.result()
            print(f"completed v5.6.6.17 N={N}", flush=True)
    if set(by_n) != set(MEMBER_N):
        raise FourDirectionCrossRouteError("member campaign incomplete")
    members = [by_n[N] for N in MEMBER_N]
    radial_alignment = members[0]["radial_GL10_alignment"]
    if any(member["radial_GL10_alignment"] != radial_alignment for member in members[1:]):
        raise FourDirectionCrossRouteError("radial quadrature alignment changed by member")
    tangential_reduction = restricted_t4_to_theta_grid_reduction(TANGENTIAL_ORDER)
    theta_only_basis = selected_bundle_theta_only_wavevector_audit()
    if not tangential_reduction["multiplicity_and_normalized_weight_identity_pass"]:
        raise FourDirectionCrossRouteError("restricted T4-to-theta grid reduction failed")
    if not theta_only_basis["pass"]:
        raise FourDirectionCrossRouteError("selected bundle is not theta=x0+x1 only")
    reproduction = _joint_reproduction(members, three_way)

    curves = [curve for member in members for curve in member["curves"]]
    observed_lineages = {
        (int(member["N"]), curve["curve_name"], curve["authoritative_free_tangent_sha256"])
        for member in members
        for curve in member["curves"]
    }
    expected_pairs = {(N, curve_name) for N in MEMBER_N for curve_name in CURVE_NAMES}
    lineage_pass = bool(
        {(N, name) for N, name, _sha in observed_lineages} == expected_pairs
        and len(observed_lineages) == 12
        and len({_sha for _N, _name, _sha in observed_lineages}) == 12
        and all(len(_sha) == 64 for _N, _name, _sha in observed_lineages)
    )
    comparison_pass = all(
        bool(curve["comparison"]["pass"]) for curve in curves
    )
    additivity_pass = all(
        bool(route["pass"])
        for curve in curves
        for route in curve["sector_additivity"].values()
    )
    canary_pass = all(bool(curve["sign_flip_canary"]["rejected"]) for curve in curves)
    positional_canary_pass = all(
        bool(curve["positional_zip_component_order_canary"]["rejected"])
        for curve in curves
    )
    route_c_metadata_pass = all(
        curve["Route_C_evaluation_metadata"]
        == {
            "N": int(member["N"]),
            "K": int(member["K"]),
            "member_id": member["member_id"],
            "curve_name": curve["curve_name"],
            "tangential_order": TANGENTIAL_ORDER,
            "radial_order": RADIAL_ORDER,
            "free_step": FREE_STEP,
        }
        for member in members
        for curve in member["curves"]
    )
    scientific = {
        "members": members,
        "joint_direction_reproduction_of_v5_6_6_6": reproduction,
        "quadrature_relation": {
            "selected_bundle_theta_only_wavevector_audit": theta_only_basis,
            "restricted_T4_tensor_grid_residue_multiplicity": tangential_reduction,
            "radial_GL10_implementation_alignment": radial_alignment,
        },
        "campaign_summary": {
            "member_count": len(members),
            "curve_count": len(curves),
            "component_count_per_curve": 21,
            "maximum_absolute_cross_route_difference": max(
                float(curve["comparison"]["maximum_absolute_difference"])
                for curve in curves
            ),
            "maximum_cross_route_difference_over_tolerance": max(
                float(curve["comparison"]["maximum_difference_over_tolerance"])
                for curve in curves
            ),
            "minimum_cross_route_cosine": min(
                float(curve["comparison"]["cosine"]) for curve in curves
            ),
        },
    }
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": "theory_only;sampled;fixed_Q;route_A_forward_AD;route_C_precision_stabilized;C2_radial;four_published_tangents;N1_N2_N3;fail_closed",
        "decision": {
            "v5_6_6_15_sampled_density_receipt_byte_pinned_pass": True,
            "selected_N123_four_published_curve_lineages_byte_aligned_pass": lineage_pass,
            "selected_N123_bundle_wavevectors_depend_only_on_theta_x0_plus_x1_pass": bool(theta_only_basis["pass"]),
            "restricted_Q5_theta_only_grid_residue_multiplicity_identity_pass": True,
            "Route_A_and_Route_C_GL10_nodes_weights_numeric_match_pass": True,
            "Route_C_selected_evaluation_metadata_match_requested_campaign_pass": route_c_metadata_pass,
            "route_A_C2_AD_and_precision_stabilized_route_C_selected_fixed_Q_evaluations_completed_pass": len(curves) == 12,
            "route_A_C2_AD_vs_precision_stabilized_route_C_selected_N123_four_curves_Q5_R10_componentwise_within_fixed_tolerance_pass": comparison_pass,
            "route_A_and_route_C_twenty_sector_totals_additive_within_fixed_tolerance_pass": additivity_pass,
            "joint_direction_strictly_reproduces_pinned_v5_6_6_6_receipt_pass": bool(reproduction["pass"]),
            "single_component_sign_flip_canary_rejected_pass": canary_pass,
            "positional_zip_component_order_canary_rejected_pass": positional_canary_pass,
            "same_functional_symbolic_identity_pass": False,
            "actual_route_A_route_C_integrand_nodewise_identity_audited_pass": False,
            "route_A_fixed_Q_AD_equals_continuum_first_variation_pass": False,
            "route_A_C2_JVP_quadrature_convergence_pass": False,
            "route_C_free_FD5_exact_derivative_pass": False,
            "route_C_coordinate_stencil_exact_derivative_pass": False,
            "Q_h_limit_commutation_proved_pass": False,
            "differentiation_and_quadrature_limit_interchange_pass": False,
            "route_A_float64_roundoff_enclosed_pass": False,
            "selected_member_open_tube_branch_smoothness_certified_pass": False,
            "route_C_B_FD_Q_to_infinity_estimate_pass": False,
            "route_C_B_FD_rigorous_bound_pass": False,
            "density_union_C_N_pass": False,
            "spectral_N_convergence_pass": False,
            "periodic_box_exhaustion_and_tail_control_pass": False,
            "uniform_stability_pass": False,
            "independent_clean_process_redteam_pass": False,
            "full_mutant_campaign_pass": False,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "fixed_before_run": {
            "member_N": list(MEMBER_N),
            "curve_names": list(CURVE_NAMES),
            "tangential_order_per_axis": TANGENTIAL_ORDER,
            "radial_order": RADIAL_ORDER,
            "Route_C_free_step": FREE_STEP,
            "Route_A_tangential_chunk_size": CHUNK_SIZE,
            "process_workers": WORKERS,
            "pairwise_absolute_tolerance": PAIRWISE_ATOL,
            "pairwise_relative_tolerance": PAIRWISE_RTOL,
            "active_sign_threshold": ACTIVE_SIGN_THRESHOLD,
            "sector_additivity_absolute_tolerance": ADDITIVITY_ATOL,
            "sector_additivity_relative_tolerance": ADDITIVITY_RTOL,
            "radial_node_weight_alignment_tolerance": RADIAL_ALIGNMENT_ATOL,
            "joint_direction_reproduction_absolute_tolerance": REPRODUCTION_ATOL,
            "component_alignment": "by exact name, never by position",
            "tangential_quadrature_relation": "the selected bundle wavevectors are theta=x0+x1 only, and the Q=5 tensor grid has an exact combinatorial residue multiplicity; no nodewise equality of the two action integrands is claimed",
        },
        "scientific": scientific,
        "scientific_payload_sha256": _canonical_sha256(scientific),
        "source_pins": {
            "route_A_C2_source_sha256": C2_SOURCE_SHA256,
            "route_A_C2_test_sha256": C2_TEST_SHA256,
            "route_A_C2_artifact_sha256": C2_ARTIFACT_SHA256,
            "route_A_wrapper_source_sha256": ROUTE_A_WRAPPER_SOURCE_SHA256,
            "route_A_core_source_sha256": ROUTE_A_SOURCE_SHA256,
            "route_C_precision_source_sha256": ROUTE_C_STABLE_SOURCE_SHA256,
            "route_C_precision_test_sha256": ROUTE_C_STABLE_TEST_SHA256,
            "route_C_precision_artifact_sha256": ROUTE_C_STABLE_ARTIFACT_SHA256,
            "route_C_base_source_sha256": ROUTE_C_SOURCE_SHA256,
            "C2_primitive_bundle_sha256": BUNDLE_SHA256,
            "three_way_v5_6_6_6_source_sha256": THREE_WAY_SOURCE_SHA256,
            "three_way_v5_6_6_6_test_sha256": THREE_WAY_TEST_SHA256,
            "three_way_v5_6_6_6_artifact_sha256": THREE_WAY_ARTIFACT_SHA256,
            "v5_6_6_15_source_sha256": V15_SOURCE_SHA256,
            "v5_6_6_15_test_sha256": V15_TEST_SHA256,
            "v5_6_6_15_artifact_sha256": V15_ARTIFACT_SHA256,
        },
        "independence_boundary": {
            "Route_A_and_Route_C_are_distinct_implementations": True,
            "same_C2_bundle_and_tangents_used": True,
            "tangential_quadrature_implementations_identical_claimed": False,
            "selected_bundle_theta_only_wavevectors_audited": True,
            "theta_only_grid_residue_multiplicity_proved": True,
            "actual_cross_route_integrand_nodewise_identity_claimed": False,
            "radial_quadrature_implementations_identical_claimed": False,
            "Route_A_uses_forward_AD_of_discrete_action": True,
            "Route_C_uses_free_FD5_and_coordinate_stencils": True,
            "both_routes_recomputed_in_this_campaign": True,
            "v15_is_only_a_pinned_sampled_density_receipt": True,
            "symbolic_same_functional_identity_claimed": False,
            "clean_room_process_claimed": False,
        },
        "open_obligations": {
            "same_functional": "v5.6.6.15 is sampled; a symbolic identity remains open",
            "Route_C_bias": "fixed-Q agreement does not bound the free/coordinate stencil bias or its Q-to-infinity behavior",
            "continuum": "JVP quadrature convergence, limit interchange, roundoff enclosure, and open-tube smoothness remain open",
            "N_to_infinity": "twelve finite pinned curves do not prove density, arbitrary-member convergence, box exhaustion, or a uniform bridge",
        },
        "evidence_boundary": "Twelve pinned finite comparisons at matched orders Qtheta=5, Qrho=10 agree only within the stated mixed tolerance. The selected bundle basis is theta=x0+x1 only, and Route A's T4 grid has the recorded exact combinatorial residue count; no nodewise identity of the two action integrands or quadrature implementations is claimed. Sector additivity and v5.6.6.6 reproduction use separately declared fixed tolerances, not a roundoff enclosure. This gate does not prove a symbolic same-functional identity, a rigorous B_FD bound, convergence of AD JVP quadrature, N-to-infinity, C1/N1, B4, or B5.",
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
    return payload


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
