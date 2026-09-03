#!/usr/bin/env python3
"""Targeted tests for the finite restricted-spectral family certificate."""

from __future__ import annotations

import ast
import base64
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm

if __package__:
    from . import derive_one_omega_topological_so3_restricted_spectral_family_v5_6_4_certificate as gate
else:
    import derive_one_omega_topological_so3_restricted_spectral_family_v5_6_4_certificate as gate


def _artifact() -> dict:
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _dimensions(N: int) -> tuple[int, int, int]:
    K = gate.radial_truncation(N)
    return (
        (294 + 128 * K) * N,
        (242 + 128 * K) * N,
        (233 + 128 * K) * N,
    )


def _decode_f64le(row: dict) -> np.ndarray:
    assert row["encoding"] == "base64"
    assert row["dtype"] == "<f8"
    raw = base64.b64decode(row["data"], validate=True)
    assert hashlib.sha256(raw).hexdigest() == row["sha256"]
    return np.frombuffer(raw, dtype="<f8").reshape(row["shape"])


def test_artifact_is_fresh_byte_canonical_and_deterministic() -> None:
    assert gate.OUTPUT.exists()
    rebuilt = gate.build_payload()
    assert rebuilt == _artifact()
    encoded = json.dumps(rebuilt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert gate.OUTPUT.read_bytes() == encoded.encode("utf-8")
    assert rebuilt["scientific_sha256"] == _canonical_sha256(rebuilt["scientific"])


def test_only_two_upstreams_are_byte_pinned_and_helpers_are_not_imported() -> None:
    payload = _artifact()
    assert set(payload["upstream_byte_pins"]) == {
        "literal_v5_2_action",
        "level_zero_v5_6_3_fixture",
    }
    for name, pin in gate.SOURCE_PINS.items():
        row = payload["upstream_byte_pins"][name]
        assert row["sha256"] == {
            "artifact": pin.artifact_sha256,
            "generator": pin.generator_sha256,
            "test": pin.test_sha256,
        }
        for key in (
            "python_helper_imported_or_called",
            "decision_boolean_consumed",
            "prediction_consumed",
            "ledger_consumed",
            "action_value_consumed",
        ):
            assert row[key] is False
    literal = payload["upstream_byte_pins"]["literal_v5_2_action"]["literal_exact_action_pin"]
    assert literal["json_path"] == "exact_classical_charter.exact_action"
    assert literal["canonical_byte_length"] == 1123
    assert literal["sha256"] == gate.V5_2_EXACT_ACTION_SHA256
    tree = ast.parse(Path(gate.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any("classical_v5_2" in name or "v5_6_3" in name for name in imported)
    assert payload["provenance"]["upstream_helpers_imported"] == []


def test_C_N_dynamic_dimensions_and_legacy_147_boundary() -> None:
    contract = _artifact()["scientific"]["mathematical_contract"]
    assert contract["family"] == "C_N=C_{+,N} x_{B_N} C_{-,N}"
    assert contract["base"] == "B_N=(gamma,T,Omega_Sigma,varphi_H,A_Sigma)"
    assert contract["G_per_side_per_retained_coefficient"]["total"] == 26
    assert contract["G_total_per_retained_coefficient"] == 52
    assert "10x3=30" in contract["B_constraint_note"]
    assert contract["legacy_147"] == {
        "role": "R=I legacy regression reference metadata only",
        "legacy_component_count": 147,
        "regression_executed": False,
        "used_to_define_ambient_dimension": False,
        "used_to_define_DG_rank": False,
        "used_to_define_kernel": False,
    }
    for N in gate.TRUNCATIONS:
        ambient, kernel, _ = _dimensions(N)
        assert gate.radial_truncation(N) == N
        assert gate.ambient_layout(N).size == ambient
        assert gate.free_layout(N).size == kernel
        assert ambient - 52 * N == kernel
        assert ambient != 147


def test_real_T4_Fourier_and_free_coefficients_are_nested_and_unisolvent() -> None:
    previous: list[str] = []
    previous_points = np.empty((0, 4))
    for N in range(1, 8):
        basis = gate.real_fourier_basis(N)
        labels = list(basis["labels"])
        assert labels[: len(previous)] == previous
        assert basis["values"].shape == (N, N)
        assert basis["derivatives"].shape == (4, N, N)
        assert basis["points_T4"].shape == (N, 4)
        assert np.array_equal(basis["points_T4"][: len(previous_points)], previous_points)
        assert np.linalg.matrix_rank(basis["values"]) == N
        previous, previous_points = labels, basis["points_T4"]
    for seed in gate.PRIMARY_SEEDS:
        assert gate.free_coefficients_are_prefix_nested(seed, 1, 2)
        assert gate.free_coefficients_are_prefix_nested(seed, 2, 3)


def test_common_first_retraction_induced_metric_and_connection_pullback() -> None:
    N = 3
    free = gate.build_free_coordinates(gate.DEVELOPMENT_SEED, N)
    q, detail = gate.construct_ambient_point(free, N, details=True)
    assert q.shape == (_dimensions(N)[0],)
    assert np.max(np.abs(gate.gluing_map(q, N))) < gate.TOLERANCES["gluing_Linf"]
    assert np.linalg.norm(
        detail["sides"]["plus"]["Y_nodes"]
        - detail["sides"]["minus"]["Y_nodes"]
    ) > gate.TOLERANCES["independent_embedding_L2"]
    for side in gate.SIDES:
        for node in range(N):
            tangent = np.zeros((5, 4))
            tangent[:4] = np.eye(4)
            tangent[4] = detail["sides"][side]["Y_gradient"][node]
            induced = tangent.T @ detail["sides"][side]["g_nodes"][node] @ tangent
            assert np.max(np.abs(induced - detail["gamma_nodes"][node])) < 3.0e-13

    layout = gate.ambient_layout(N)
    basis = gate.real_fourier_basis(N)
    F, Finv = basis["values"], basis["inverse"]
    uncompensated = q.copy()
    A_full = layout.get(uncompensated, "plus.A_trace_full").copy()
    A_full[0, 4, 0] += 0.03
    layout.put(uncompensated, "plus.A_trace_full", A_full)
    assert np.max(np.abs(gate.gluing_map(uncompensated, N))) > 1.0e-6
    compensated = q.copy()
    A_nodes = (F @ layout.get(q, "plus.A_trace_full").reshape(N, 15)).reshape(N, 5, 3)
    delta_normal = np.zeros((N, 3))
    delta_normal[:, 0] = 0.03
    A_nodes[:, 4] += delta_normal
    A_nodes[:, :4] -= detail["sides"]["plus"]["Y_gradient"][:, :, None] * delta_normal[:, None, :]
    layout.put(
        compensated,
        "plus.A_trace_full",
        (Finv @ A_nodes.reshape(N, 15)).reshape(N, 5, 3),
    )
    assert np.max(np.abs(gate.gluing_map(compensated, N))) < gate.TOLERANCES["gluing_Linf"]


def test_exponential_rotation_uses_exact_frechet_derivative() -> None:
    N = 3
    basis = gate.real_fourier_basis(N)
    coefficients = gate._spectral_coefficients(97, "frechet-test", (N, 3), 0.45)
    rotations, derivatives = gate._rotation_nodes(coefficients, basis)
    node, mu, step = 1, 0, 1.0e-7
    r = (basis["values"] @ coefficients)[node]
    direction = (basis["derivatives"][mu] @ coefficients)[node]
    finite = (
        expm(gate._hat(r + step * direction))
        - expm(gate._hat(r - step * direction))
    ) / (2.0 * step)
    assert np.max(np.abs(finite - derivatives[node, mu])) < 2.0e-9
    naive = rotations[node] @ gate._hat(direction)
    assert np.max(np.abs(naive - derivatives[node, mu])) > 1.0e-7


def test_finite_boundary_trivialization_orbit_has_9N_rank_and_rotates_B_J_C() -> None:
    N = 2
    q = gate.construct_ambient_point(
        gate.build_free_coordinates(gate.DEVELOPMENT_SEED, N), N
    )
    parameters = gate.gauge_parameter_layout(N)
    direction = np.zeros(parameters.size)
    direction[parameters.indices("source_plus")[1]] = 1.0
    moved = gate.finite_frame_gauge_action(q, N, direction, 0.07)
    assert np.max(np.abs(gate.gluing_map(moved, N))) < gate.TOLERANCES["gluing_Linf"]
    layout = gate.ambient_layout(N)
    assert not np.allclose(
        layout.get(q, "plus.B_trace_full"), layout.get(moved, "plus.B_trace_full")
    )
    for block in ("boundary_jet_J1", "interior_bump_C"):
        before = layout.get(q, f"plus.{block}")
        after = layout.get(moved, f"plus.{block}")
        assert np.allclose(before[..., :16], after[..., :16], atol=2.0e-14)
        assert not np.allclose(before[..., 16:], after[..., 16:])
    tangent = gate.runtime_SO3_gauge_tangents(q, N)
    assert tangent.shape == (_dimensions(N)[0], 9 * N)
    assert np.linalg.matrix_rank(tangent, tol=1.0e-8) == 9 * N


def test_every_receipt_has_full_DG_rank_complete_kernel_and_H_N_chart() -> None:
    receipts = _artifact()["scientific"]["configuration_and_tangent_receipts"]
    assert len(receipts) == len(gate.PRIMARY_SEEDS) * len(gate.TRUNCATIONS)
    for row in receipts:
        N = row["N"]
        ambient, kernel, horizontal = _dimensions(N)
        dimensions, svd = row["dimensions"], row["DG_SVD"]
        assert dimensions["ambient_domain"] == ambient
        assert dimensions["gluing_codomain"] == dimensions["DG_rank_measured"] == 52 * N
        assert dimensions["kernel_expected"] == dimensions["kernel_measured"] == kernel
        assert dimensions["retraction_domain"] == kernel
        assert dimensions["gauge_dimension"] == 9 * N
        assert dimensions["SO3_horizontal_admissible_dimension"] == horizontal
        assert len(svd["raw_singular_values"]) == 52 * N
        assert min(svd["raw_singular_values"]) > svd["rank_tolerance"]
        assert svd["kernel_basis_shape"] == [ambient, kernel]
        assert len(svd["raw_kernel_vector_residual_L2"]) == kernel
        assert svd["kernel_residual_max_L2"] < gate.TOLERANCES["kernel_residual_L2"]
        assert svd["kernel_orthonormality_probe_Linf"] < gate.TOLERANCES["orthonormality_Linf"]
        retract = row["common_first_retraction"]
        assert retract["dense_pushforward_materialized"] is False
        assert len(retract["selected_probe_DG_residual_L2"]) == 4
        assert retract["selected_probe_DG_residual_max_L2"] < gate.TOLERANCES["retraction_pushforward_residual_L2"]
        chart = row["H_N_pointwise_generator_and_retracted_stencils"]
        assert chart["operator_basis_shape"] == [ambient, horizontal]
        assert chart["rank"] == horizontal
        assert chart["all_stencil_endpoint_G_Linf_max"] < gate.TOLERANCES["reachable_chart_G_Linf"]
        assert chart["all_stencil_five_point_tangent_tracking_L2_max"] < gate.TOLERANCES["reachable_chart_first_order_L2"]
        assert chart["all_stencil_endpoint_sampled_kinematics_pass"] is True
        assert chart["reachability_or_neighborhood_chart_claimed"] is False
        assert set(chart["selected_horizontal_stencils"]) == {
            "compact_bulk_SO3_horizontal_candidate",
            "free_B_SO3_horizontal_candidate",
            "embedding_motion_SO3_horizontal_candidate",
            "joint_all_primitive_classes_control_candidate",
        }
        gauge_stencils = chart["selected_gauge_representative_stencils"]
        assert len(gauge_stencils) == 9 * N
        assert {item["sector"] for item in gauge_stencils.values()} == {
            "target_Q", "source_plus", "source_minus"
        }
        assert {item["so3_component"] for item in gauge_stencils.values()} == {0, 1, 2}
        if N >= 2:
            assert all(
                any(
                    item["sector"] == sector
                    and item["so3_component"] == component
                    and item["is_local_nonconstant_parameter"]
                    and item["gauge_parameter_four_gradient_L2"] > 0.0
                    for item in gauge_stencils.values()
                )
                for sector in ("target_Q", "source_plus", "source_minus")
                for component in range(3)
            )
        assert all(
            _decode_f64le(item["ambient_primitive_tangent_f64le"]).shape
            == (ambient,)
            for item in gauge_stencils.values()
        )
        for family in (
            chart["selected_horizontal_stencils"],
            chart["selected_gauge_representative_stencils"],
        ):
            for stencil in family.values():
                assert set(stencil["stencil_endpoints_ambient_q_f64le"]) == {"-2", "-1", "1", "2"}
                assert all(
                    audit["all_sampled_checks_pass"]
                    for audit in stencil["stencil_endpoint_sampled_kinematic_audits"].values()
                )
        assert all(
            value > gate.TOLERANCES["reachable_chart_activity_L2"]
            for value in chart["joint_control_motion_by_primitive_class_L2"].values()
        )
        assert chart["not_action_field"] is True
        assert chart["independent_Newton_retraction_checked"] is False


def test_SO3_horizontal_selected_tangents_are_active_independent_and_no_parity() -> None:
    for row in _artifact()["scientific"]["configuration_and_tangent_receipts"]:
        N = row["N"]
        ambient, _, horizontal = _dimensions(N)
        split = row["SO3_gauge_and_horizontal_split"]
        assert split["gauge_basis_shape"] == [ambient, 9 * N]
        assert split["gauge_rank"] == 9 * N
        assert split["SO3_horizontal_basis_shape"] == [ambient, horizontal]
        assert max(split["gauge_DG_residual_L2"]) < gate.TOLERANCES["kernel_residual_L2"]
        assert split["SO3_horizontal_DG_residual_max_L2"] < gate.TOLERANCES["kernel_residual_L2"]
        assert split["SO3_gauge_horizontal_overlap_Linf"] < gate.TOLERANCES["orthonormality_Linf"]
        assert split["Z2_gauge_covariance_residual_max_L2"] < gate.TOLERANCES["kernel_residual_L2"]
        assert "not a full physical quotient" in split["SO3_horizontal_basis_scope"]
        selected = split["selected_SO3_horizontal_tangents"]
        assert [item["name"] for item in selected] == [
            "compact_bulk_SO3_horizontal_candidate",
            "free_B_SO3_horizontal_candidate",
            "embedding_motion_SO3_horizontal_candidate",
            "joint_all_primitive_classes_control_candidate",
        ]
        vectors = np.stack(
            [np.asarray(item["ambient_primitive_tangent"]) for item in selected], axis=-1
        )
        assert np.max(np.abs(vectors.T @ vectors - np.eye(4))) < gate.TOLERANCES["orthonormality_Linf"]
        for item in selected:
            assert item["plus_activity_L2"] > gate.TOLERANCES["SO3_horizontal_tangent_activity_L2"]
            assert item["minus_activity_L2"] > gate.TOLERANCES["SO3_horizontal_tangent_activity_L2"]
            assert item["non_Z2_no_parity_ambient_distance_L2"] > gate.TOLERANCES["SO3_horizontal_non_Z2_L2"]
            assert item["gauge_quotient_claimed"] is False


def test_primitives_independently_recompute_G_DG_rank_and_endpoint_invariants() -> None:
    row = next(
        item
        for item in _artifact()["scientific"]["configuration_and_tangent_receipts"]
        if item["seed"] == gate.DEVELOPMENT_SEED and item["N"] == 1
    )
    q = np.asarray(row["primitive_configuration"]["ambient_q"])
    G = gate.gluing_map(q, 1)
    DG = gate.runtime_DG(q, 1)
    singulars = np.linalg.svd(DG, compute_uv=False)
    tolerance = gate._rank_tolerance(singulars, DG.shape)
    assert np.max(np.abs(G)) < gate.TOLERANCES["gluing_Linf"]
    assert int(np.sum(singulars > tolerance)) == 52
    assert np.allclose(singulars, row["DG_SVD"]["raw_singular_values"], rtol=2.0e-13, atol=2.0e-13)
    chart = row["H_N_pointwise_generator_and_retracted_stencils"]
    for family in (
        chart["selected_horizontal_stencils"],
        chart["selected_gauge_representative_stencils"],
    ):
        for stencil in family.values():
            for endpoint in stencil["stencil_endpoints_ambient_q_f64le"].values():
                audit = gate._sampled_endpoint_kinematic_audit(_decode_f64le(endpoint), 1)
                assert audit["all_sampled_checks_pass"] is True
                assert audit["Omega_min"] > gate.TOLERANCES["Omega_min"]


def test_bulk_log_Omega_radial_lifts_signature_orientation_and_Z2() -> None:
    for row in _artifact()["scientific"]["configuration_and_tangent_receipts"]:
        checks = row["checks"]
        for key in (
            "gamma_is_Lorentzian_with_margin",
            "ambient_metrics_are_Lorentzian_with_margin",
            "Omega_is_strictly_positive",
            "bulk_Omega_is_strictly_positive",
            "bulk_metrics_preserve_Lorentzian_signature",
            "T_gradient_is_uniformly_timelike",
            "horizontal_frame_from_gamma_T_is_orthonormal_spatial",
            "vertical_Q_frame_is_orthonormal",
            "R_is_SO3_and_local_chart_avoids_cut_locus",
            "radial_profiles_include_normal_jet_and_interior_bump",
            "B_is_excluded_from_G_and_is_free_kernel_data",
            "boundary_normals_are_derived_unit_and_orthogonal",
            "outward_orientation_contract_is_verified_from_declared_collar_domains",
            "declared_Z2_is_an_involution_and_G_equivariant_off_shell",
            "declared_Z2_maps_SO3_gauge_at_q_to_SO3_gauge_at_Jq",
        ):
            assert checks[key] is True
        normals = row["kinematic_invariants"]["boundary_normals"]
        assert normals["plus"]["interior_domain"] == "rho_plus=Y_plus(x)-y4>=0"
        assert normals["minus"]["interior_domain"] == "rho_minus=y4-Y_minus(x)>=0"
        assert set(normals["plus"]["outward_orientation_determinant_sign"]) == {1}
        assert set(normals["minus"]["outward_orientation_determinant_sign"]) == {-1}

    N = 2
    q = gate.construct_ambient_point(gate.build_free_coordinates(gate.DEVELOPMENT_SEED, N), N)
    rho = np.asarray((0.0, 0.2, 0.6, 1.0, 1.2))
    bulk = gate.bulk_primitives(q, N, rho)
    expected_shapes = {
        "g_MN": (len(rho), N, 5, 5),
        "Omega": (len(rho), N),
        "phi_a": (len(rho), N, 3),
        "A_Ma": (len(rho), N, 5, 3),
        "B_MNP_a": (len(rho), N, 10, 3),
    }
    for side in gate.SIDES:
        component = bulk[side]["component_contract"]
        assert component["B_MNP_a"] == 30
        assert component["radial_bump_mode_count"] == N
        assert component["Omega_coordinate"].startswith("log_Omega")
        for name, shape in expected_shapes.items():
            assert bulk[side]["values"][name].shape == shape
            assert bulk[side]["radial_derivatives"][name].shape == shape
        assert np.all(bulk[side]["values"]["Omega"] > 0.0)
        assert np.linalg.norm(bulk[side]["radial_derivatives"]["phi_a"][0]) > 1.0e-8
        assert np.max(np.abs(bulk[side]["values"]["phi_a"][-1])) == 0.0


def test_identity_nontrivial_rotations_and_unrevealed_holdout_protocol() -> None:
    scientific = _artifact()["scientific"]
    seeds = scientific["seeds"]
    assert seeds["identity_control"] == 0
    assert seeds["development"] == gate.DEVELOPMENT_SEED
    assert tuple(seeds["primary"]) == gate.PRIMARY_SEEDS
    assert tuple(seeds["reserved_seed_domains"]) == gate.RESERVED_SEED_DOMAINS
    assert seeds["reserved_seed_values_embedded"] is False
    assert seeds["reserved_seed_values_revealed"] is False
    assert seeds["reserved_seed_receipts_present"] is False
    assert seeds["independent_reserved_seed_protocol_pass"] is False
    assert "SHA256(generator_sha256" in seeds["external_clean_runner_protocol"]
    for row in scientific["configuration_and_tangent_receipts"]:
        if row["seed"] == gate.IDENTITY_CONTROL_SEED:
            assert row["kinematic_invariants"]["R_chart_norm_max"] < 2.0e-13
        else:
            assert row["kinematic_invariants"]["R_chart_norm_max"] > gate.TOLERANCES["nonidentity_rotation_Linf"]
            assert row["kinematic_invariants"]["R_plus_minus_Linf"] > gate.TOLERANCES["nonidentity_rotation_Linf"]


def test_only_finite_kinematics_and_reachable_chart_are_promoted() -> None:
    payload = _artifact()
    decision = payload["scientific"]["decision"]
    assert decision[gate.CERTIFICATE_NAME] is True
    assert decision["finite_C_N_kinematics_pass"] is True
    assert decision["finite_C_N_gluing_and_tangent_kernel_pass"] is True
    assert decision["finite_retracted_admissible_stencil_pass"] is True
    for key in gate.FAIL_CLOSED_KEYS:
        assert decision[key] is False
    for key in ("C1_ACTION_pass", "N1_ACTION_pass", "B4_pass", "B5_pass"):
        assert decision[key] is False
    assert any(limit.startswith("No action") for limit in payload["limits"])
    assert payload["provenance"]["Skai_or_device_control_touched"] is False
