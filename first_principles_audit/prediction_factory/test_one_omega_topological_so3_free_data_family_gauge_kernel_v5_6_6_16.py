"""Tests for the v5.6.6.16 free-data family / sampled-trace audit."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

import derive_one_omega_topological_so3_free_data_family_gauge_kernel_v5_6_6_16 as gate

EXPECTED_TRUE_KEYS = frozenset(
    {
        "pointwise_gluing_defects_of_free_embedding_sampled_within_tolerance_pass",
        "directional_FD_of_gluing_defects_composed_with_free_embedding_sampled_within_tolerance_pass",
        "Q_frame_cancels_exactly_from_lateral_phi_and_A_trace_formulas_symbolic_pass",
        "Q_frame_lateral_trace_invariance_numeric_at_pinned_members_within_tolerance_pass",
        "route_c_and_pinned_lateral_trace_decoders_agree_sampled_within_tolerance_pass",
        "sampled_trace_output_jacobian_nullspace_matches_listed_generators_at_pinned_members_pass",
        "constant_only_N2_nontrivial_sampled_output_fiber_canary_pass",
        "six_interface_density_Q_frame_invariance_sampled_within_tolerance_pass",
        "current_route_c_uniform_N_to_infinity_strategy_refuted_by_cos_x2_pass",
    }
)
EXPECTED_FALSE_KEYS = frozenset(
    {
        "Q_frame_kernel_of_full_free_embedding_Phi_N_pass",
        "complete_DPhi_N_kernel_and_constant_rank_theorem_pass",
        "pinned_member_sampled_nullspace_dimension_globalizes_over_U_N_pass",
        "r_E0_directions_globally_nonnull_for_all_U_N_with_N_ge_2_pass",
        "physical_gauge_quotient_and_representative_independence_pass",
        "all_sector_densities_and_action_invariant_under_listed_generators_pass",
        "gap_5_closed_pass",
        "current_route_c_supports_arbitrary_N_full_T4_spectral_projection_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_stability_pass",
        "spectral_N_convergence_pass",
        "restricted_family_exact_action_identity_pass",
        "periodic_box_exhaustion_and_tail_control_pass",
        "density_union_C_N_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    }
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    if not gate.OUTPUT.exists():
        pytest.fail(f"missing receipt {gate.OUTPUT.name}; run the derive first")
    return json.loads(gate.OUTPUT.read_text())


@pytest.fixture(scope="session")
def modules() -> tuple:
    return gate.load_modules()


def _canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def test_generator_imports_only_the_three_pinned_modules() -> None:
    source = Path(gate.__file__).read_text()
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    assert not any("one_omega_topological_so3" in name for name in names)
    assert not any(name in {"torch", "runpy"} for name in names)
    assert source.count("spec_from_file_location") == 1
    assert source.count("_load_pinned_module(") == 4  # definition + three calls
    # scipy only for the finite common-frame orbit candidates/canary
    assert source.count("from scipy.linalg import expm, logm") == 2
    for forbidden in ("three_way", "v5_6_6_12", "gluing_map(", "runtime_DG", "basis[\"inverse\"]"):
        assert forbidden not in source, forbidden


def test_schema_pins_and_keys(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["C2_multi_N_primitive_bundle_sha256"] == gate.BUNDLE_SHA256 == gate._sha256(gate.BUNDLE_PATH)
    assert pins["v5_6_4_2_pointwise_decoder_sha256"] == gate.DECODER_SHA256 == gate._sha256(gate.DECODER_PATH)
    assert pins["route_c_v5_6_6_3_derive_sha256"] == gate.ROUTE_C_SHA256 == gate._sha256(gate.ROUTE_C_PATH)
    assert pins["route_b_v5_6_5_certificate_derive_sha256"] == gate.ROUTE_B_SHA256 == gate._sha256(gate.ROUTE_B_PATH)
    assert pins["v5_6_6_9_receipt_sha256"] == gate._sha256(gate.V5669_PATH)
    assert pins["v5_6_6_8_target_class_derive_sha256"] == gate.TARGET_CLASS_SHA256 == gate._sha256(gate.TARGET_CLASS_PATH)
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key


def test_constraint_block_vanishes_with_its_derivative(receipt: dict) -> None:
    fixed = receipt["fixed_before_run"]
    g0 = receipt["scientific"]["G0_constraint_composed_with_free_embedding"]
    assert set(g0["members"]) == {"N1.K1.seed20260902", "N2.K2.seed20260902", "N3.K3.seed20260902"}
    for row in g0["members"].values():
        assert row["max_abs_defect"] <= fixed["constraint_tolerance"]
        assert row["max_abs_defect_derivative"] <= fixed["constraint_derivative_tolerance"]


def test_symbolic_block_is_exact_on_every_instance(receipt: dict) -> None:
    g1 = receipt["scientific"]["G1_symbolic_Q_frame_lateral_trace_cancellation"]
    assert g1["pass"] is True
    assert len(g1["instances"]) == receipt["fixed_before_run"]["symbolic_instances"] >= 2
    for instance in g1["instances"]:
        assert instance["S_R0_orthogonal"] and instance["phi_source_equals_R0T_varphi_E0"]
        assert instance["A_source_equals_R0T_hatA_R0_plus_R0T_dR0"] and instance["A_source_skew_symmetric"]


def test_numeric_lateral_invariance_is_nonvacuous(receipt: dict) -> None:
    fixed = receipt["fixed_before_run"]
    g2 = receipt["scientific"][
        "G2_numeric_Q_frame_lateral_trace_invariance_and_decoder_agreement"
    ]
    assert set(g2["members"]) == {"N1.K1.seed20260902", "N2.K2.seed20260902", "N3.K3.seed20260902"}
    for row in g2["members"].values():
        assert row["q_block_size"] == 3 * row["N"]
        assert row["pinned_decoder_lateral_change_under_q_perturbation"] <= fixed["q_independence_tolerance"]
        assert row["route_c_decoder_lateral_change_under_q_perturbation"] <= fixed["q_independence_tolerance"]
        assert row["common_frame_outputs_change_under_q_perturbation"] > 1.0e-2
        assert row["route_c_vs_pinned_decoder_lateral_traces_max_abs"] <= fixed["decoder_agreement_tolerance"]


def test_sampled_output_jacobian_nullspace_matches_generators(receipt: dict) -> None:
    fixed = receipt["fixed_before_run"]
    g3 = receipt["scientific"]["G3_sampled_trace_output_jacobian_nullspace"]
    assert g3["pass"] is True
    expected_dimension = {1: 3 * 1 + 3 + 1, 2: 3 * 2 + 3, 3: 3 * 3 + 3}
    for row in g3["members"].values():
        N = row["N"]
        assert row["kernel_dimension"] == row["generator_rank"] == len(row["explicit_generators"]) == expected_dimension[N]
        assert row["gap_ratio"] >= fixed["kernel_gap_minimum"]
        assert row["generators_inside_kernel_residual"] <= fixed["kernel_span_tolerance"]
        assert row["kernel_inside_generators_residual"] <= fixed["kernel_span_tolerance"]
        assert row["jacobian_on_generators_relative"] <= fixed["kernel_span_tolerance"]
        assert min(row["r_E0_blocks_smallest_singular_relative"]) > 10.0 * fixed["kernel_relative_threshold"]
        labels = row["explicit_generators"]
        assert sum(
            label.startswith("[exact lateral-trace null direction] Q_frame.q[")
            for label in labels
        ) == 3 * N
        assert "[decoder zero-mode, not SO(3)] common.T constant mode" in labels
        assert "[decoder zero-mode, not SO(3)] plus.Y constant mode" in labels
        assert "[decoder zero-mode, not SO(3)] minus.Y constant mode" in labels
        assert sum("[pinned N=1 member stabiliser]" in label for label in labels) == (1 if N == 1 else 0)
        categories = row["generator_categories"]
        assert categories == {
            "exact_lateral_trace_null_directions_Q_frame": 3 * N,
            "decoder_zero_modes_not_SO3": 3,
            "pinned_N1_member_stabiliser": 1 if N == 1 else 0,
        }


def test_interface_block_and_boundaries(receipt: dict) -> None:
    g4 = receipt["scientific"][
        "G4_six_interface_densities_Q_frame_invariance_sampled"
    ]
    assert g4["pass"] is True and g4["q_norm_max"] > 1.0
    assert "gap 5 remains open" in receipt["scientific"]["gap_5_restated"]["after"]
    assert "No physical quotient" in receipt["scientific"]["gap_5_restated"]["after"]
    assert "B_FD" in " ".join(receipt["open_obligation"])
    assert "N -> infinity" in " ".join(receipt["scientific"]["what_is_not_established"])


def test_constant_only_n2_sampled_output_fiber_blocks_global_rank_reading(receipt: dict) -> None:
    canary = receipt["scientific"][
        "constant_only_N2_nontrivial_sampled_output_fiber_canary"
    ]
    assert canary["pass"] is True
    assert canary["N"] == 2
    assert canary["free_parameter_max_abs_motion"] > 1.0e-3
    assert canary["sampled_trace_interface_output_max_abs_change"] <= canary[
        "tolerance"
    ]
    assert receipt["decision"][
        "pinned_member_sampled_nullspace_dimension_globalizes_over_U_N_pass"
    ] is False


def test_constant_only_n2_sampled_output_fiber_recomputes(modules: tuple) -> None:
    decoder, route_c, _route_b = modules
    canary = gate.constant_only_n2_nontrivial_sampled_output_fiber_canary(
        decoder, route_c, gate.load_bundle()
    )
    assert canary["pass"] is True
    assert canary["free_parameter_max_abs_motion"] > 1.0e-3
    assert canary["sampled_trace_interface_output_max_abs_change"] <= gate.Q_INDEPENDENCE_TOLERANCE


def test_current_theta_only_route_c_is_not_dense_in_declared_t4_class(
    receipt: dict, modules: tuple
) -> None:
    _decoder, route_c, _route_b = modules
    obstruction = receipt["scientific"][
        "G5_current_route_c_theta_only_T4_density_obstruction"
    ]
    assert obstruction["pass"] is True
    assert obstruction["target_scope_static_audit_pass"] is True
    assert obstruction["route_c_basis_arbitrary_N_rejection_guard_ast_pass"] is True
    assert obstruction["route_c_supported_N_probe"] == [1, 2, 3]
    assert obstruction["route_c_rejected_N_probe"] == [4, 5, 6]
    assert obstruction["theta_only_derivative_pattern_pass"] is True
    assert obstruction["normalized_inner_product_with_every_g_x0_plus_x1"] == "0"
    assert obstruction["witness_epsilon"] == "1/4"
    assert obstruction["witness_preserves_declared_Omega_margin"] is True
    assert obstruction["normalized_unit_amplitude_cos_x2_L2_norm_squared"] == "1/2"
    assert obstruction["normalized_witness_L2_norm_squared"] == "1/32"
    assert obstruction["normalized_squared_distance_lower_bound_to_theta_only_family"] == "1/32"
    assert "for every integrable g" in obstruction["normalized_inner_product_factorization"]
    assert receipt["decision"][
        "current_route_c_uniform_N_to_infinity_strategy_refuted_by_cos_x2_pass"
    ] is True
    assert receipt["decision"][
        "current_route_c_supports_arbitrary_N_full_T4_spectral_projection_pass"
    ] is False
    assert receipt["decision"]["uniform_N_to_infinity_bridge_pass"] is False

    fresh = gate.route_c_theta_only_t4_density_obstruction(route_c)
    assert fresh == obstruction

    # Independent discrete Fourier canary: every g(x0+x1) is orthogonal to cos(x2).
    grid = 2.0 * math.pi * np.arange(64) / 64.0
    x0, x1, x2 = np.meshgrid(grid, grid, grid, indexing="ij")
    witness = 0.25 * np.cos(x2)
    candidate = 0.4 - 0.7 * np.cos(x0 + x1) + 0.2 * np.sin(x0 + x1)
    assert abs(float(np.mean(witness * candidate))) < 1.0e-15
    assert float(np.mean((witness - candidate) ** 2)) >= 1.0 / 32.0 - 1.0e-14


def test_fresh_q_perturbation_on_the_pinned_decoder(modules: tuple) -> None:
    """Independent re-check with another seed: the lateral traces ignore Q_frame.q, the common frame does not."""
    decoder, route_c, _route_b = modules
    bundle = gate.load_bundle()
    rng = np.random.default_rng(gate.SEED + 4242)
    pairs5 = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5)
    for member in bundle["primary_members"]:
        contract = bundle["pointwise_decoder_contract_by_N"][str(member["N"])]
        free = gate._member_free(route_c, member)
        start, stop, _ = gate._block_slice(contract, "Q_frame.q")
        moved = free.copy()
        moved[start:stop] += rng.uniform(-1.0, 1.0, size=stop - start)
        points = rng.uniform(0.0, 2.0 * math.pi, size=(4, 4))
        base = decoder.decode_pointwise_boundary(free, contract, points)
        other = decoder.decode_pointwise_boundary(moved, contract, points)
        assert np.max(np.abs(gate._side_outputs(base, pairs5) - gate._side_outputs(other, pairs5))) <= 1.0e-12
        assert np.max(np.abs(base["common"]["varphi"] - other["common"]["varphi"])) > 1.0e-3


def test_mutant_pinned_n2_r_e0_perturbation_changes_sampled_lateral_traces(modules: tuple) -> None:
    """At the pinned N=2 member, an r_E0 perturbation changes the sampled lateral traces."""
    decoder, route_c, _route_b = modules
    bundle = gate.load_bundle()
    rng = np.random.default_rng(gate.SEED + 99)
    pairs5 = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5)
    member = bundle["primary_members"][1]
    contract = bundle["pointwise_decoder_contract_by_N"][str(member["N"])]
    free = gate._member_free(route_c, member)
    start, stop, _ = gate._block_slice(contract, "plus.r_E0")
    moved = free.copy()
    moved[start:stop] += 1.0e-3 * rng.uniform(-1.0, 1.0, size=stop - start)
    points = rng.uniform(0.0, 2.0 * math.pi, size=(4, 4))
    base = decoder.decode_pointwise_boundary(free, contract, points)
    other = decoder.decode_pointwise_boundary(moved, contract, points)
    assert np.max(np.abs(gate._side_outputs(base, pairs5) - gate._side_outputs(other, pairs5))) > 1.0e-5
