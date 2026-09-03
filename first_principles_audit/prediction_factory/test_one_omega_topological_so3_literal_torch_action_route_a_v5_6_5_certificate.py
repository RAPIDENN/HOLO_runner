#!/usr/bin/env python3
"""Targeted structural and manufactured tests for literal Torch route A."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_literal_torch_action_route_a_v5_6_5_certificate.py"
SPEC = importlib.util.spec_from_file_location("literal_torch_route_a_v565", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
route = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = route
SPEC.loader.exec_module(route)


def test_literal_contract_has_twenty_atoms_plus_total() -> None:
    raw = json.dumps(
        route.EXACT_ACTION,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert len(raw) == 1123
    assert hashlib.sha256(raw).hexdigest() == route.V5_2_EXACT_ACTION_SHA256
    assert len(route.COMPONENT_NAMES) == 20
    assert len(route.OUTPUT_NAMES) == 21
    assert route.OUTPUT_NAMES[-1] == "S_total"


def test_route_source_has_no_local_or_forbidden_import() -> None:
    source = Path(route.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {
        "__future__",
        "base64",
        "hashlib",
        "itertools",
        "json",
        "math",
        "dataclasses",
        "pathlib",
        "typing",
        "torch",
    }
    for forbidden in ("v5_6_4", "v5_6_2", "euler", "green", "oracle"):
        assert not any(forbidden in name.lower() for name in imported)


def test_flat_metric_has_zero_curvature() -> None:
    metric = torch.diag(torch.tensor((-1.0, 1.2, 1.4, 1.7), dtype=route.DTYPE))[None]
    first = torch.zeros(1, 4, 4, 4, dtype=route.DTYPE)
    second = torch.zeros(1, 4, 4, 4, 4, dtype=route.DTYPE)
    geometry = route.metric_geometry(metric, first, second, include_riemann=True)
    assert torch.max(torch.abs(geometry["scalar_curvature"])) == 0.0
    assert torch.max(torch.abs(geometry["riemann_lower"])) == 0.0


def test_lorentzian_inertia_is_checked_node_by_node() -> None:
    metrics = torch.stack(
        (
            torch.diag(torch.tensor((-1.0, 1.2, 1.4, 1.7), dtype=route.DTYPE)),
            torch.diag(torch.tensor((-0.4, 0.8, 1.1, 2.0), dtype=route.DTYPE)),
        )
    )
    report = route.lorentzian_inertia_diagnostics(metrics, label="manufactured")
    assert report["all_nodes_lorentzian"] is True
    assert report["node_count"] == 2
    assert report["negative_count_min"] == report["negative_count_max"] == 1
    route.require_lorentzian_inertia(report)

    bad = metrics.clone()
    bad[1, 1, 1] = -0.8
    failed = route.lorentzian_inertia_diagnostics(bad, label="bad_manufactured")
    assert failed["all_nodes_lorentzian"] is False
    try:
        route.require_lorentzian_inertia(failed)
    except route.LiteralTorchRouteError:
        pass
    else:  # pragma: no cover - explicit fail-closed witness
        raise AssertionError("two-timelike-direction metric was accepted")


def _tau_data() -> tuple[torch.Tensor, torch.Tensor]:
    gradient = torch.tensor(((1.0, 0.0, 0.0, 0.0),), dtype=route.DTYPE)
    hessian = torch.zeros(1, 4, 4, dtype=route.DTYPE)
    return gradient, hessian


def test_static_stereographic_s3_has_Rcal_six_over_radius_squared() -> None:
    """At r=0 for h_ij=4 a^4 delta_ij/(a^2+r^2)^2."""

    for radius in (1.0, 1.7):
        gamma = torch.diag(
            torch.tensor((-1.0, 4.0, 4.0, 4.0), dtype=route.DTYPE)
        )[None]
        first = torch.zeros(1, 4, 4, 4, dtype=route.DTYPE)
        second = torch.zeros(1, 4, 4, 4, 4, dtype=route.DTYPE)
        for derivative in range(1, 4):
            for spatial_metric_index in range(1, 4):
                second[
                    0,
                    derivative,
                    derivative,
                    spatial_metric_index,
                    spatial_metric_index,
                ] = -16.0 / radius**2
        tau_gradient, tau_hessian = _tau_data()
        foliation = route.foliation_geometry_from_primitives(
            gamma, first, second, tau_gradient, tau_hessian
        )
        assert torch.allclose(
            foliation["Ktrace"], torch.zeros(1), atol=2.0e-14, rtol=0.0
        )
        assert torch.allclose(
            foliation["K_squared"], torch.zeros(1), atol=2.0e-14, rtol=0.0
        )
        assert torch.allclose(
            foliation["Rcal"],
            torch.tensor((6.0 / radius**2,), dtype=route.DTYPE),
            atol=2.0e-13,
            rtol=0.0,
        )


def test_flat_spatial_flrw_gauss_terms_cancel() -> None:
    """For ds2=-dt2+exp(2Ht)dx2, each constant-t leaf is intrinsically flat."""

    H = 0.23
    gamma = torch.diag(torch.tensor((-1.0, 1.0, 1.0, 1.0), dtype=route.DTYPE))[None]
    first = torch.zeros(1, 4, 4, 4, dtype=route.DTYPE)
    second = torch.zeros(1, 4, 4, 4, 4, dtype=route.DTYPE)
    for spatial in range(1, 4):
        first[0, 0, spatial, spatial] = 2.0 * H
        second[0, 0, 0, spatial, spatial] = 4.0 * H * H
    tau_gradient, tau_hessian = _tau_data()
    foliation = route.foliation_geometry_from_primitives(
        gamma, first, second, tau_gradient, tau_hessian
    )
    assert torch.allclose(
        foliation["Ktrace"], torch.tensor((3.0 * H,), dtype=route.DTYPE), atol=2.0e-14, rtol=0.0
    )
    assert torch.allclose(
        foliation["K_squared"], torch.tensor((3.0 * H * H,), dtype=route.DTYPE), atol=2.0e-14, rtol=0.0
    )
    assert torch.allclose(foliation["Rcal"], torch.zeros(1), atol=2.0e-13, rtol=0.0)
    assert torch.allclose(
        foliation["projected_riemann"]
        + foliation["K_squared"]
        - foliation["Ktrace"] ** 2,
        foliation["Rcal"],
        atol=0.0,
        rtol=0.0,
    )


def test_pointwise_bundle_pins_free_layout_and_affine_joint_curve() -> None:
    payload = route.load_primitive_bundle()
    assert route._sha256(route.PRIMITIVE_BUNDLE) == route.PRIMITIVE_BUNDLE_FILE_SHA256
    corrigendum_pin = payload["source_pins"]["mandatory_v5_5_4_Gauss_sign_corrigendum"]
    assert corrigendum_pin["artifact_sha256"] == route.GAUSS_SIGN_CORRIGENDUM_SHA256
    assert (
        corrigendum_pin["required_decision_path"]
        == "decision.v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma"
    )
    assert corrigendum_pin["required_value_literal"] == "false"
    primary = payload["primary_member"]
    identity = payload["identity_control"]
    assert primary["member_id"] == "N2.K2.seed20260902"
    assert identity["member_id"] == "N2.K2.seed0"
    layout = route.free_layout(2, 2)
    assert layout.size == 996
    assert payload["pointwise_decoder_contract"]["free_layout"]["blocks"] == layout.contract()

    free0 = route.decode_f64le(
        primary["authoritative_free_central_f64le"], label="primary.free"
    )
    joint = next(
        row
        for row in primary["curves"]
        if row["name"] == "joint_all_primitive_classes_control_candidate"
    )
    tangent = route.decode_f64le(
        joint["authoritative_free_tangent_f64le"], label="joint.free_tangent"
    )
    for family in joint["step_families"]:
        for multiplier_text, record in family["free_endpoints_f64le"].items():
            endpoint = route.decode_f64le(
                record, label=f"{family['label']}.{multiplier_text}"
            )
            expected = free0 + float(multiplier_text) * family["step"] * tangent
            assert torch.max(torch.abs(endpoint - expected)) < 3.0e-15


def test_common_first_decoder_glues_at_reserved_off_collocation_nodes() -> None:
    payload = route.load_primitive_bundle()
    free = route.decode_f64le(
        payload["primary_member"]["authoritative_free_central_f64le"],
        label="primary.free",
    )
    points = route.decode_f64le(
        payload["off_collocation_validation_nodes"]["points_f64le"],
        label="reserved.points",
    )
    residual = route.pointwise_gluing_residual(free, 2, 2, points)
    assert residual.shape == (7, 52)
    assert torch.max(torch.abs(residual)) < 3.0e-12


def test_pointwise_eliminated_trace_jets_are_exact_node_derivatives() -> None:
    payload = route.load_primitive_bundle()
    free = route.decode_f64le(
        payload["primary_member"]["authoritative_free_central_f64le"],
        label="primary.free",
    )
    point = torch.tensor(((0.37, 1.11, 0.23, 2.07),), dtype=route.DTYPE)
    value, first, second = route.common_first_trace_jets(
        free, 2, 2, "plus", point
    )
    assert value.shape == (1, 64)
    assert first.shape == (1, 4, 64)
    assert second.shape == (1, 4, 4, 64)
    assert torch.all(torch.isfinite(value))
    assert torch.all(torch.isfinite(first))
    assert torch.all(torch.isfinite(second))
    assert torch.max(torch.abs(second - second.transpose(1, 2))) < 3.0e-12

    step = 2.0e-5
    direction = torch.tensor((0.31, -0.27, 0.19, 0.41), dtype=route.DTYPE)
    plus = route._common_first_trace_value_at_point(
        free, 2, 2, "plus", point[0] + step * direction
    )
    minus = route._common_first_trace_value_at_point(
        free, 2, 2, "plus", point[0] - step * direction
    )
    finite_difference = (plus - minus) / (2.0 * step)
    exact_directional = torch.einsum("u,uc->c", direction, first[0])
    assert torch.max(torch.abs(finite_difference - exact_directional)) < 2.0e-9


def test_N2_seed_zero_is_the_R_identity_control() -> None:
    payload = route.load_primitive_bundle()
    free = route.decode_f64le(
        payload["identity_control"]["authoritative_free_central_f64le"],
        label="identity.free",
    )
    layout = route.free_layout(2, 2)
    assert torch.count_nonzero(layout.get(free, "Q_frame.q")) == 0
    assert torch.count_nonzero(layout.get(free, "plus.r_E0")) == 0
    assert torch.count_nonzero(layout.get(free, "minus.r_E0")) == 0


def test_chunked_action_and_jvp_match_monolithic_on_same_grid() -> None:
    payload = route.load_primitive_bundle()
    member = payload["primary_member"]
    free = route.decode_f64le(
        member["authoritative_free_central_f64le"], label="primary.free"
    )
    joint = next(
        row
        for row in member["curves"]
        if row["name"] == "joint_all_primitive_classes_control_candidate"
    )
    tangent = route.decode_f64le(
        joint["authoritative_free_tangent_f64le"], label="joint.free_tangent"
    )
    quadrature = route.QuadratureSpec(tangential_order_per_axis=2, radial_order=2)
    value_full, jvp_full = route.action_value_and_jvp(
        free, tangent, 2, 2, quadrature
    )
    value_chunked, jvp_chunked = route.action_value_and_jvp_chunked(
        free,
        tangent,
        2,
        2,
        quadrature,
        tangential_chunk_size=5,
    )
    assert torch.allclose(value_chunked, value_full, atol=3.0e-11, rtol=3.0e-13)
    assert torch.allclose(jvp_chunked, jvp_full, atol=3.0e-10, rtol=3.0e-12)
