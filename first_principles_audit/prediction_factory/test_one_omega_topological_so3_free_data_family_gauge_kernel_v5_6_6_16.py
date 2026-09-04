"""Tests for the v5.6.6.16 free-data family / gauge kernel gate."""

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
        "pointwise_constraint_G_composed_with_free_embedding_zero_sampled_pass",
        "pointwise_DG_composed_with_DI_zero_sampled_pass",
        "Q_frame_coordinates_are_exact_kernel_of_the_decoder_symbolic_pass",
        "Q_frame_coordinates_are_exact_kernel_of_pinned_and_route_c_decoders_numeric_at_pinned_members_pass",
        "route_c_trace_decoder_matches_pinned_decoder_sampled_pass",
        "free_data_family_trace_jacobian_kernel_rank_and_generators_sampled_at_pinned_members_pass",
        "interface_densities_independent_of_Q_frame_sampled_pass",
    }
)
EXPECTED_FALSE_KEYS = frozenset(
    {
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
    # scipy only for the finite common-frame orbit at N = 1
    assert source.count("from scipy.linalg import expm, logm") == 1
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
    g1 = receipt["scientific"]["G1_symbolic_Q_frame_kernel"]
    assert g1["pass"] is True
    assert len(g1["instances"]) == receipt["fixed_before_run"]["symbolic_instances"] >= 2
    for instance in g1["instances"]:
        assert instance["S_R0_orthogonal"] and instance["phi_source_equals_R0T_varphi_E0"]
        assert instance["A_source_equals_R0T_hatA_R0_plus_R0T_dR0"] and instance["A_source_skew_symmetric"]


def test_numeric_kernel_is_exact_and_not_vacuous(receipt: dict) -> None:
    fixed = receipt["fixed_before_run"]
    g2 = receipt["scientific"]["G2_numeric_Q_frame_kernel_and_decoder_agreement"]
    assert set(g2["members"]) == {"N1.K1.seed20260902", "N2.K2.seed20260902", "N3.K3.seed20260902"}
    for row in g2["members"].values():
        assert row["q_block_size"] == 3 * row["N"]
        assert row["pinned_decoder_lateral_change_under_q_perturbation"] <= fixed["q_independence_tolerance"]
        assert row["route_c_decoder_lateral_change_under_q_perturbation"] <= fixed["q_independence_tolerance"]
        assert row["common_frame_outputs_change_under_q_perturbation"] > 1.0e-2
        assert row["route_c_vs_pinned_decoder_lateral_traces_max_abs"] <= fixed["decoder_agreement_tolerance"]


def test_jacobian_kernel_matches_explicit_generators(receipt: dict) -> None:
    fixed = receipt["fixed_before_run"]
    g3 = receipt["scientific"]["G3_jacobian_kernel_on_trace_coordinates"]
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
        assert sum(label.startswith("[SO(3) exact kernel] Q_frame.q[") for label in labels) == 3 * N
        assert "[decoder zero-mode, not SO(3)] common.T constant mode" in labels
        assert "[decoder zero-mode, not SO(3)] plus.Y constant mode" in labels
        assert "[decoder zero-mode, not SO(3)] minus.Y constant mode" in labels
        assert sum("[N=1 only stabiliser]" in label for label in labels) == (1 if N == 1 else 0)
        categories = row["generator_categories"]
        assert categories == {"SO3_exact_kernel_Q_frame": 3 * N, "decoder_zero_modes_not_SO3": 3, "N1_only_stabiliser": 1 if N == 1 else 0}


def test_interface_block_and_boundaries(receipt: dict) -> None:
    g4 = receipt["scientific"]["G4_interface_densities_independent_of_Q_frame"]
    assert g4["pass"] is True and g4["q_norm_max"] > 1.0
    assert "retired" in receipt["scientific"]["gap_5_restated"]["after"]
    assert "not discharged" in receipt["scientific"]["gap_5_restated"]["after"]
    assert "B_FD" in " ".join(receipt["open_obligation"])
    assert "N -> infinity" in " ".join(receipt["scientific"]["what_is_not_established"])


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


def test_mutant_a_physical_coordinate_is_not_in_the_kernel(modules: tuple) -> None:
    """Perturbing r_E0 (the claimed physical block) changes the lateral traces; the check is not vacuous."""
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
