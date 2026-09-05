#!/usr/bin/env python3
"""Tests for the isolated v5.6.7.4 q-frame section/factorization gate."""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE
    / "derive_one_omega_topological_so3_q_frame_section_factorization_v5_6_7_4_gate.py"
)
MODULE_SHA256 = "7b3b6f10f17eff6203b962fdf2fd517af3b003cf32e956791a7ea4973530015b"
SPEC = importlib.util.spec_from_file_location("v5674_q_frame_section", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


@pytest.fixture(scope="session")
def report() -> dict:
    return gate.build_report()


def _q_slice(contract: dict) -> slice:
    specification = contract["free_layout"]["blocks"]["Q_frame.q"]
    return slice(int(specification["start"]), int(specification["stop"]))


def _assert_invalid_report(report: dict) -> None:
    with pytest.raises(gate.QFrameSectionGateError):
        gate.validate_report(report)


def test_new_source_is_frozen_and_upstream_targets_are_byte_pinned(report: dict) -> None:
    assert hashlib.sha256(MODULE_PATH.read_bytes()).hexdigest() == MODULE_SHA256
    pins = report["source_pins_and_target_contract"]
    assert pins["pass"] is True
    assert pins["v5_6_7_1"]["observed_sha256"] == gate.V5671_SOURCE_SHA256
    assert pins["v5_6_7_1_test"]["observed_sha256"] == gate.V5671_TEST_SHA256
    assert (
        pins["v5_6_7_exact_full_t4_primitives"]["observed_sha256"]
        == gate.V567_EXACT_SOURCE_SHA256
    )
    assert all(pins["independent_expected_constants_match_runtime_target"].values())
    assert all(pins["v5_6_7_1"]["AST_dataflow_contract"].values())


def test_report_has_exact_true_and_false_allowlists(report: dict) -> None:
    decision = report["decision"]
    assert set(decision) == gate.TRUE_DECISION_KEYS | gate.FALSE_DECISION_KEYS
    assert {key for key, value in decision.items() if value} == gate.TRUE_DECISION_KEYS
    assert {key for key, value in decision.items() if not value} == gate.FALSE_DECISION_KEYS
    assert decision["finite_Q_frame_q_zero_section_and_twenty_route_factorization_pass"]
    assert not decision["Q_frame_kernel_of_full_Phi_pass"]
    assert not decision["global_smooth_physical_gauge_quotient_manifold_pass"]
    assert not decision["r_plus_minus_quotiented_as_Q_frame_redundancy_pass"]
    assert not decision["continuum_action_representative_independence_theorem_pass"]
    assert not decision["uniform_N_to_infinity_bridge_pass"]
    assert not decision["C1_ACTION_pass"]
    assert not decision["N1_ACTION_pass"]
    assert not decision["P4_full_same_action_pass"]
    assert not decision["B4_pass"]
    assert not decision["B5_pass"]


def test_Q_is_explicitly_refuted_as_a_kernel_of_full_Phi_by_e3_cross_e1(
    report: dict,
) -> None:
    witness = report["full_Phi_kernel_counterexample"]
    assert witness["base_q"] == [0, 0, 0]
    e3 = np.asarray(witness["Q_frame_tangent_delta_q"], dtype=int)
    e1 = np.asarray(witness["base_phi0"], dtype=int)
    assert np.array_equal(np.cross(e3, e1), np.asarray([0, 1, 0]))
    assert witness["D_varphi_at_q0_equals_delta_q_cross_phi0"] == [0, 1, 0]
    assert witness["nonzero"] is True
    assert witness["conclusion"] == "Q_frame is not a subspace of ker D(Phi_full)"
    assert gate._canonical_sha256(witness) == (
        gate.EXPECTED_FULL_PHI_KERNEL_COUNTEREXAMPLE_SHA256
    )
    assert gate._kernel_counterexample_accepts(witness)


def test_kernel_validator_reconstructs_q0_derivative_without_calling_producer() -> None:
    source = inspect.getsource(gate._kernel_counterexample_accepts)
    assert "full_phi_kernel_counterexample(" not in source
    canonical = gate.full_phi_kernel_counterexample()
    delta = np.asarray(canonical["Q_frame_tangent_delta_q"], dtype=int)
    phi0 = np.asarray(canonical["base_phi0"], dtype=int)
    independently_derived = np.cross(delta, phi0).tolist()
    assert canonical["base_q"] == [0, 0, 0]
    assert independently_derived == [0, 1, 0]
    assert independently_derived == canonical[
        "D_varphi_at_q0_equals_delta_q_cross_phi0"
    ]


def test_kernel_producer_nonzero_q_monkeypatch_before_build_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mutant = copy.deepcopy(gate.full_phi_kernel_counterexample())
    mutant["base_q"] = [9, 9, 9]
    mutant["pass"] = True
    monkeypatch.setattr(gate, "full_phi_kernel_counterexample", lambda: mutant)
    assert gate._kernel_counterexample_accepts(mutant) is False
    with pytest.raises(gate.QFrameSectionGateError):
        gate.build_report()


def test_kernel_wrong_phi_and_delta_siblings_preserving_reported_derivative_die() -> None:
    canonical = gate.full_phi_kernel_counterexample()
    wrong_phi = copy.deepcopy(canonical)
    wrong_phi["base_phi0"] = [0, 1, 0]
    wrong_phi["pass"] = True
    assert gate._kernel_counterexample_accepts(wrong_phi) is False
    wrong_delta = copy.deepcopy(canonical)
    wrong_delta["Q_frame_tangent_delta_q"] = [1, 0, 0]
    wrong_delta["pass"] = True
    assert gate._kernel_counterexample_accepts(wrong_delta) is False


def test_three_invariant_identities_reduce_exactly_and_all_algebra_mutants_die(
    report: dict,
) -> None:
    ledger = report["three_exact_invariant_identities"]
    assert ledger["pass"] is True
    assert set(ledger["identities"]) == {
        "lateral_associated_field",
        "lateral_affine_connection",
        "shared_solder_contraction",
    }
    for identity in ledger["identities"].values():
        assert identity["pass"] is True
        assert identity["left_normal_form"] == identity["right_normal_form"]
    affine = ledger["identities"]["lateral_affine_connection"]
    assert affine["right_normal_form"] == [
        {"coefficient": "1", "word": ["R0_inv", "A0", "R0"]},
        {"coefficient": "1", "word": ["R0_inv", "dR0"]},
    ]
    assert gate._identity_mutants() == {
        "associated_wrong_R_order": True,
        "affine_wrong_common_frame_sign": True,
        "affine_omit_dR_term": True,
        "solder_freeze_EQ": True,
    }


def test_identity_validator_is_literal_and_never_calls_the_identity_producer() -> None:
    source = inspect.getsource(gate._identity_contract_accepts)
    assert "exact_invariant_identity_ledger(" not in source
    canonical = gate.exact_invariant_identity_ledger()
    assert gate._canonical_sha256(canonical) == gate.EXPECTED_IDENTITY_LEDGER_SHA256
    assert gate._identity_contract_accepts(canonical)
    assert gate.EXPECTED_IDENTITY_NORMAL_FORMS_LITERAL == {
        "lateral_associated_field": (("1", ("R0_inv", "phi0")),),
        "lateral_affine_connection": (
            ("1", ("R0_inv", "A0", "R0")),
            ("1", ("R0_inv", "dR0")),
        ),
        "shared_solder_contraction": (("1", ("E0", "phi0")),),
    }


def test_identity_producer_monkeypatch_before_build_cannot_self_oracle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mutant = copy.deepcopy(gate.exact_invariant_identity_ledger())
    wrong = [{"coefficient": "1", "word": ["R0_inv", "WRONG_phi0"]}]
    associated = mutant["identities"]["lateral_associated_field"]
    associated["left_normal_form"] = copy.deepcopy(wrong)
    associated["right_normal_form"] = copy.deepcopy(wrong)
    associated["pass"] = True
    mutant["pass"] = True
    monkeypatch.setattr(gate, "exact_invariant_identity_ledger", lambda: mutant)
    assert gate._identity_contract_accepts(mutant) is False
    with pytest.raises(gate.QFrameSectionGateError):
        gate.build_report()


def test_coherent_affine_and_solder_producer_siblings_cannot_self_oracle() -> None:
    canonical = gate.exact_invariant_identity_ledger()
    for name, word in (
        ("lateral_affine_connection", ["R0_inv", "WRONG_A0", "R0"]),
        ("shared_solder_contraction", ["E0", "WRONG_phi0"]),
    ):
        mutant = copy.deepcopy(canonical)
        wrong = [{"coefficient": "1", "word": word}]
        mutant["identities"][name]["left_normal_form"] = copy.deepcopy(wrong)
        mutant["identities"][name]["right_normal_form"] = copy.deepcopy(wrong)
        mutant["identities"][name]["pass"] = True
        mutant["pass"] = True
        assert gate._identity_contract_accepts(mutant) is False


def test_exactly_twelve_bulk_two_GHY_and_six_interface_routes_bind_real_leaves(
    report: dict,
) -> None:
    ledger = report["twenty_real_action_routes"]
    routes = ledger["routes"]
    assert ledger["pass"] is True
    assert ledger["counts"] == {"bulk": 12, "GHY": 2, "interface": 6}
    assert len(routes) == len({route["component"] for route in routes}) == 20
    assert tuple(route["component"] for route in routes) == gate.EXPECTED_COMPONENTS
    assert tuple(ledger["actual_runtime_component_names"]) == gate.EXPECTED_COMPONENTS
    assert all(
        route["producer"] == "_bulk_components_from_boundary_td3"
        and route["target_leaf"].startswith("_relative_bulk_densities_td3[")
        for route in routes
        if route["class"] == "bulk"
    )
    assert all(
        route["target_leaf"] == "_ghy_density_td3"
        for route in routes
        if route["class"] == "GHY"
    )
    robin = next(route for route in routes if route["component"] == "Robin")
    assert "(E0 S^-1)(S phi0)=E0 phi0" in robin["q_factor"]
    dataflow = report["source_pins_and_target_contract"]["v5_6_7_1"][
        "AST_dataflow_contract"
    ]
    assert dataflow["decoder_phi_source_is_reduced_R0_inverse_phi0"] is True
    assert dataflow["decoder_A_full_is_built_from_reduced_A_source"] is True
    assert dataflow["decoder_X64_trace_consumes_reduced_phi_and_A"] is True
    assert dataflow["side_payload_exports_that_exact_X64_trace"] is True
    assert dataflow["collar_consumes_side_X64_trace"] is True
    assert dataflow["X64_primitive_decoder_extracts_phi_channels_16_18"] is True
    assert dataflow["X64_primitive_decoder_extracts_A_channels_19_33"] is True
    assert dataflow["bulk_leaf_reads_decoded_phi"] is True
    assert dataflow["bulk_leaf_reads_decoded_A"] is True
    assert dataflow["six_bulk_leaves_are_actual_return_dictionary"] is True
    assert dataflow["six_interface_leaves_are_actual_return_dictionary"] is True
    assert dataflow["interface_EQ_reads_common_EQ"] is True
    assert dataflow["interface_varphi_reads_common_varphi"] is True
    assert dataflow["interface_phi_H_multiplies_EQ_and_varphi_exactly"] is True
    assert dataflow["Robin_is_the_only_q_sensitive_interface_leaf"] is True
    assert dataflow["Robin_dependency_closure_reaches_phi_H"] is True


def test_route_validator_uses_literal_component_leaf_map_not_route_producer() -> None:
    source = inspect.getsource(gate._routes_accept)
    assert "_expected_real_routes(" not in source
    canonical = gate._expected_real_routes()
    signatures = tuple(
        tuple(route[field] for field in gate.ROUTE_SIGNATURE_FIELDS)
        for route in canonical
    )
    assert gate._canonical_sha256(signatures) == gate.EXPECTED_ROUTE_SIGNATURES_SHA256
    assert tuple(
        (route["component"], route["target_leaf"]) for route in canonical
    ) == gate.EXPECTED_COMPONENT_TO_LEAF_LITERAL
    assert gate._routes_accept(canonical)


def test_route_producer_monkeypatch_before_build_cannot_self_oracle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mutant = [dict(route) for route in gate._expected_real_routes()]
    assert mutant[0]["component"] == "EH_bulk_plus"
    mutant[0]["target_leaf"] = "_relative_bulk_densities_td3['P_kinetic']"
    monkeypatch.setattr(
        gate,
        "_expected_real_routes",
        lambda: [dict(route) for route in mutant],
    )
    assert gate._routes_accept(mutant) is False
    with pytest.raises(gate.QFrameSectionGateError):
        gate.build_report()


def test_wrong_Robin_leaf_and_self_consistent_route_reordering_are_rejected() -> None:
    canonical = gate._expected_real_routes()
    wrong_robin = [dict(route) for route in canonical]
    wrong_robin[-1]["target_leaf"] = "_interface_component_densities_td3['wall']"
    assert gate._routes_accept(wrong_robin) is False
    reordered = [dict(route) for route in canonical]
    reordered[0], reordered[1] = reordered[1], reordered[0]
    assert gate._routes_accept(reordered) is False


def test_canonicalizer_zeros_all_primal_and_tangent_q_before_target_and_only_q() -> None:
    upstream = gate._load_v5671()
    free, contract = upstream._sample_safe_free(2, 1)
    tangent = np.linspace(-0.05, 0.05, free.size)
    q_slice = _q_slice(contract)
    free[q_slice] = (0.8, -0.7, 0.6, -0.5, 0.4, -0.3)
    tangent[q_slice] = (9.0, -8.0, 7.0, -6.0, 5.0, -4.0)
    free_before = free.copy()
    tangent_before = tangent.copy()
    canonical_free, canonical_tangent, metadata = gate.canonicalize_q_zero_before_decode(
        free, tangent, 2, 1
    )
    assert not np.shares_memory(canonical_free, free)
    assert not np.shares_memory(canonical_tangent, tangent)
    assert np.array_equal(canonical_free[q_slice], np.zeros(6))
    assert np.array_equal(canonical_tangent[q_slice], np.zeros(6))
    mask = np.ones(free.size, dtype=bool)
    mask[q_slice] = False
    assert np.array_equal(canonical_free[mask], free_before[mask])
    assert np.array_equal(canonical_tangent[mask], tangent_before[mask])
    assert np.array_equal(free, free_before)
    assert np.array_equal(tangent, tangent_before)
    assert metadata["q_block"]["shape"] == [2, 3]
    assert metadata["q_block"]["primal_exactly_zero_after"] is True
    assert metadata["q_block"]["tangent_exactly_zero_after"] is True
    assert all(metadata["r_plus_minus_preserved_exactly"].values())


def test_canonicalizer_rejects_malformed_or_nonfinite_vectors_without_mutating_inputs() -> None:
    upstream = gate._load_v5671()
    free, _contract = upstream._sample_safe_free(1, 1)
    tangent = np.zeros_like(free)
    with pytest.raises(gate.QFrameSectionGateError):
        gate.canonicalize_q_zero_before_decode(free[:-1], tangent, 1, 1)
    with pytest.raises(gate.QFrameSectionGateError):
        gate.canonicalize_q_zero_before_decode(free, tangent.reshape(1, -1), 1, 1)
    nonfinite = free.copy()
    nonfinite[0] = np.nan
    with pytest.raises(gate.QFrameSectionGateError):
        gate.canonicalize_q_zero_before_decode(nonfinite, tangent, 1, 1)


def test_wrapper_control_flow_puts_both_q_zero_assignments_before_every_data_guard(
    report: dict,
) -> None:
    contract = report["predecoder_q_zero_wrapper_source_contract"]
    assert contract["pass"] is True
    assert contract["canonicalizer_zeros_primal_q_slice"] is True
    assert contract["canonicalizer_zeros_tangent_q_slice"] is True
    assert contract["q_zero_assignments_precede_finiteness_guards"] is True
    assert contract[
        "q_zero_assignments_precede_upstream_hash_and_contract_guards"
    ] is True
    for wrapper in contract["wrappers"].values():
        assert wrapper["canonicalization_is_first_executable_statement"] is True
        assert wrapper["canonicalization_precedes_target"] is True
        assert wrapper["target_receives_only_canonical_arrays"] is True
        assert wrapper["no_direct_decoder_or_so3_call"] is True


def test_local_and_finite_action_outputs_are_exactly_q_representative_independent() -> None:
    upstream = gate._load_v5671()
    free, contract = upstream._sample_safe_free(1, 1)
    tangent = np.zeros_like(free)
    phi = contract["free_layout"]["blocks"]["common.varphi_E0"]
    tangent[int(phi["start"]):int(phi["stop"])] = (0.03, -0.02, 0.01)
    q_slice = _q_slice(contract)
    free_hostile = free.copy()
    free_hostile[q_slice] = (3.0, 0.0, 0.0)
    tangent_hostile = tangent.copy()
    tangent_hostile[q_slice] = (9.0, 0.0, 0.0)
    free_permitted = free.copy()
    free_permitted[q_slice] = (0.0, 0.0, 0.1)
    tangent_permitted = tangent.copy()
    tangent_permitted[q_slice] = (0.02, -0.01, 0.03)
    with pytest.raises(Exception):
        upstream.local_density_values_and_eta_jvps(
            free_hostile, tangent, 1, 1, (0.0, 0.0, 0.0, 0.0), 0.5
        )
    with pytest.raises(Exception):
        upstream.local_density_values_and_eta_jvps(
            free, tangent_hostile, 1, 1, (0.0, 0.0, 0.0, 0.0), 0.5
        )

    raw = upstream.local_density_values_and_eta_jvps(
        free, tangent, 1, 1, (0.2, 0.3, 0.4, 0.5), 0.37
    )
    raw_permitted = upstream.local_density_values_and_eta_jvps(
        free_permitted,
        tangent_permitted,
        1,
        1,
        (0.2, 0.3, 0.4, 0.5),
        0.37,
    )
    assert raw["values"] == raw_permitted["values"]
    assert raw["eta_jvps"] == raw_permitted["eta_jvps"]
    raw_finite = upstream.integrated_action_values_and_eta_jvps(
        free, tangent, 1, 1, 1, 1
    )
    raw_finite_permitted = upstream.integrated_action_values_and_eta_jvps(
        free_permitted, tangent_permitted, 1, 1, 1, 1
    )
    assert raw_finite["values"] == raw_finite_permitted["values"]
    assert raw_finite["eta_jvps"] == raw_finite_permitted["eta_jvps"]
    assert raw_finite["S_total"] == raw_finite_permitted["S_total"]

    decoded = upstream.decode_common_first_boundary_td3(
        free, tangent, 1, 1, (0.2, 0.3, 0.4, 0.5)
    )
    decoded_permitted = upstream.decode_common_first_boundary_td3(
        free_permitted,
        tangent_permitted,
        1,
        1,
        (0.2, 0.3, 0.4, 0.5),
    )
    common_motion = max(
        abs(right.body - left.body)
        for name in ("S_Q", "varphi", "E_Q")
        for left, right in zip(
            np.asarray(decoded["common"][name], dtype=object).flat,
            np.asarray(decoded_permitted["common"][name], dtype=object).flat,
        )
    )
    assert common_motion > 1.0e-3

    local = gate.q_zero_local_density_values_and_eta_jvps(
        free, tangent, 1, 1, (0.0, 0.0, 0.0, 0.0), 0.5
    )
    local_free = gate.q_zero_local_density_values_and_eta_jvps(
        free_hostile, tangent, 1, 1, (0.0, 0.0, 0.0, 0.0), 0.5
    )
    local_tangent = gate.q_zero_local_density_values_and_eta_jvps(
        free, tangent_hostile, 1, 1, (0.0, 0.0, 0.0, 0.0), 0.5
    )
    assert local["values"] == local_free["values"] == local_tangent["values"]
    assert local["eta_jvps"] == local_free["eta_jvps"] == local_tangent["eta_jvps"]
    assert tuple(local["component_names"]) == gate.EXPECTED_COMPONENTS

    finite = gate.q_zero_integrated_action_values_and_eta_jvps(
        free, tangent, 1, 1, 1, 1
    )
    finite_free = gate.q_zero_integrated_action_values_and_eta_jvps(
        free_hostile, tangent, 1, 1, 1, 1
    )
    finite_tangent = gate.q_zero_integrated_action_values_and_eta_jvps(
        free, tangent_hostile, 1, 1, 1, 1
    )
    assert finite["values"] == finite_free["values"] == finite_tangent["values"]
    assert finite["eta_jvps"] == finite_free["eta_jvps"] == finite_tangent["eta_jvps"]
    assert finite["S_total"] == finite_free["S_total"] == finite_tangent["S_total"]
    assert any(abs(value) > 0.0 for value in finite["eta_jvps"])


def test_runtime_witness_is_finite_nonvacuous_and_covers_all_twenty(report: dict) -> None:
    witness = report["finite_runtime_factorization_witness"]
    assert witness["pass"] is True
    assert witness["scope"] == {
        "N": 1,
        "K": 1,
        "tangential_order_per_axis": 1,
        "radial_order": 1,
        "finite_only": True,
        "arbitrary_N_or_continuum_claimed": False,
    }
    assert witness["local_all_twenty_values_and_JVP_exactly_equal"] is True
    assert witness["finite_all_twenty_values_and_JVP_exactly_equal"] is True
    assert witness["finite_S_total_value_and_JVP_exactly_equal"] is True
    assert witness["finite_JVP_witness_nonzero"] is True
    assert len(witness["component_names"]) == 20
    assert len(witness["output_names"]) == 21
    raw = witness["permitted_raw_v5_6_7_1_contrast"]
    assert raw["primal_q"] == [0.0, 0.0, 0.1]
    assert raw["tangent_q"] == [0.02, -0.01, 0.03]
    assert raw["common_full_Phi_moves_nontrivially"] is True
    assert max(raw["common_full_Phi_body_motion_max_abs"].values()) > 1.0e-3
    assert raw["lateral_reduced_traces_exactly_equal"] is True
    assert set(raw["lateral_reduced_trace_body_motion_max_abs"].values()) == {0.0}
    assert raw["raw_local_all_twenty_values_and_JVP_exactly_equal"] is True
    assert raw["raw_finite_all_twenty_values_and_JVP_exactly_equal"] is True
    assert raw["raw_finite_S_total_value_and_JVP_exactly_equal"] is True


def test_r_plus_and_minus_are_preserved_and_cannot_be_erased_with_q(report: dict) -> None:
    witness = report["r_plus_minus_retention_witness"]
    assert witness["pass"] is True
    assert witness["r_quotiented_or_declared_redundant"] is False
    assert witness["primal_and_tangent_r_retained_byte_exactly"] == {
        "plus": True,
        "minus": True,
    }
    assert witness["section_metadata_r_retained"] == {"plus": True, "minus": True}
    assert all(
        change > 1.0e-3
        for change in witness["lateral_phi_trace_change_if_r_is_wrongly_erased"].values()
    )


def test_N2_BCH_nonclosure_and_nonconstant_orbit_rank_are_exact_no_gos(
    report: dict,
) -> None:
    ledger = report["finite_group_and_global_quotient_no_go"]
    bch = ledger["N2_BCH_nonclosure"]
    assert ledger["pass"] is True
    assert bch["actual_N2_basis_labels"] == ["1", "cos(1*x0+1*x1)"]
    q = bch["q"]
    lam = bch["lambda"]
    assert q == gate.EXPECTED_BCH_INPUTS_LITERAL["q"]
    assert lam == gate.EXPECTED_BCH_INPUTS_LITERAL["lambda"]
    q_generator = np.asarray(q["generator"], dtype=int)
    lambda_generator = np.asarray(lam["generator"], dtype=int)
    local_generator_cross = np.cross(q_generator, lambda_generator).tolist()
    local_half = Fraction(q["coefficient"]) * Fraction(lam["coefficient"]) / 2
    local_decomposed = local_half / 2
    local_reconstruction = {
        "generator_cross": local_generator_cross,
        "half_bracket_coefficient_times_cos_squared": str(local_half),
        "constant_coefficient": str(local_decomposed),
        "double_cosine_coefficient": str(local_decomposed),
        "double_wavevector": [
            2 * value for value in q["basis_function"]["wavevector"]
        ],
    }
    assert local_reconstruction == bch["reconstructed_half_bracket"]
    assert bch["exact_decomposition_display"] == "(1/4)(1+cos(2 theta)) e3"
    assert bch["outside_coefficient"] == "1/4"
    assert bch["outside_mode_absent_from_actual_N2_basis"] is True
    rank = ledger["nonconstant_infinitesimal_orbit_rank"]

    def local_orbit_matrix(pair: dict) -> list[list[int]]:
        phi = np.asarray(pair["phi"], dtype=int)
        connection = np.asarray(pair["A"], dtype=int)
        columns = []
        for generator in np.eye(3, dtype=int):
            columns.append(
                np.concatenate(
                    (np.cross(generator, phi), np.cross(generator, connection))
                )
            )
        return np.asarray(columns, dtype=int).T.tolist()

    local_zero_matrix = local_orbit_matrix(rank["zero_pair"])
    local_generic_matrix = local_orbit_matrix(rank["generic_pair"])
    assert local_zero_matrix == rank["zero_pair_matrix"]
    assert local_generic_matrix == rank["generic_pair_matrix"]
    assert np.linalg.matrix_rank(np.asarray(local_zero_matrix, dtype=float)) == 0
    assert np.linalg.matrix_rank(np.asarray(local_generic_matrix, dtype=float)) == 3
    assert rank["zero_pair_rank"] == 0
    assert rank["generic_pair_rank"] == 3
    assert rank["zero_pair_stabilizer_dimension"] == 3
    assert rank["generic_pair_stabilizer_dimension"] == 0
    assert rank["generic_Gram_determinant"] == 2
    assert gate._canonical_sha256(ledger) == (
        gate.EXPECTED_FINITE_BCH_AND_RANK_NO_GO_SHA256
    )
    assert gate._no_go_contract_accepts(ledger)


def test_no_go_validator_reconstructs_inputs_without_calling_producer() -> None:
    source = inspect.getsource(gate._no_go_contract_accepts)
    assert "finite_BCH_and_variable_rank_no_go(" not in source


def test_BCH_zero_input_producer_monkeypatch_before_build_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mutant = copy.deepcopy(gate.finite_BCH_and_variable_rank_no_go())
    mutant["N2_BCH_nonclosure"]["q"] = "0"
    mutant["N2_BCH_nonclosure"]["lambda"] = "0"
    mutant["N2_BCH_nonclosure"]["pass"] = True
    mutant["pass"] = True
    monkeypatch.setattr(gate, "finite_BCH_and_variable_rank_no_go", lambda: mutant)
    assert gate._no_go_contract_accepts(mutant) is False
    with pytest.raises(gate.QFrameSectionGateError):
        gate.build_report()


def test_BCH_parallel_generator_and_wrong_wavevector_siblings_die() -> None:
    canonical = gate.finite_BCH_and_variable_rank_no_go()
    parallel = copy.deepcopy(canonical)
    parallel["N2_BCH_nonclosure"]["lambda"]["generator"] = [1, 0, 0]
    parallel["pass"] = True
    assert gate._no_go_contract_accepts(parallel) is False
    wrong_wavevector = copy.deepcopy(canonical)
    wrong_wavevector["N2_BCH_nonclosure"]["q"]["basis_function"][
        "wavevector"
    ] = [1, 0, 0, 0]
    wrong_wavevector["pass"] = True
    assert gate._no_go_contract_accepts(wrong_wavevector) is False


def test_rank_pair_producer_monkeypatch_before_build_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mutant = copy.deepcopy(gate.finite_BCH_and_variable_rank_no_go())
    mutant["nonconstant_infinitesimal_orbit_rank"]["generic_pair"] = {
        "phi": [0, 0, 0],
        "A": [0, 0, 0],
    }
    mutant["nonconstant_infinitesimal_orbit_rank"]["pass"] = True
    mutant["pass"] = True
    monkeypatch.setattr(gate, "finite_BCH_and_variable_rank_no_go", lambda: mutant)
    assert gate._no_go_contract_accepts(mutant) is False
    with pytest.raises(gate.QFrameSectionGateError):
        gate.build_report()


def test_rank_collinear_generic_and_nonzero_zero_pair_siblings_die() -> None:
    canonical = gate.finite_BCH_and_variable_rank_no_go()
    collinear = copy.deepcopy(canonical)
    collinear["nonconstant_infinitesimal_orbit_rank"]["generic_pair"] = {
        "phi": [1, 0, 0],
        "A": [1, 0, 0],
    }
    assert gate._no_go_contract_accepts(collinear) is False
    nonzero_zero_pair = copy.deepcopy(canonical)
    nonzero_zero_pair["nonconstant_infinitesimal_orbit_rank"]["zero_pair"] = {
        "phi": [1, 0, 0],
        "A": [0, 1, 0],
    }
    assert gate._no_go_contract_accepts(nonzero_zero_pair) is False


def test_prior_ledgers_are_links_only_and_never_shared_oracles(report: dict) -> None:
    links = report["linked_prior_evidence_not_used_as_oracle"]
    for key, item in links.items():
        if not isinstance(item, dict):
            continue
        assert item["imported_or_called"] is False
    assert links["v5_6_6_16_finite_gauge_kernel_ledger"]["observed_sha256"] == (
        gate.V56616_SOURCE_SHA256
    )
    assert links["v5_6_6_8_restricted_green_ledger"]["observed_sha256"] == (
        gate.V5668_SOURCE_SHA256
    )
    assert links["this_gate_exact_identity_engine_is_independent"] is True


def test_every_required_runtime_memory_and_source_mutant_is_independently_killed(
    report: dict,
) -> None:
    campaign = report["mutant_campaign"]
    assert campaign["pass"] is True
    rows = campaign["mutants"]
    assert {row["id"] for row in rows} == gate.REQUIRED_MUTANT_IDS
    assert all(row["detected"] is True for row in rows)
    assert all(row["producer"] != row["independent_target"] for row in rows)
    assert campaign["producer_target_independence_declared_for_every_mutant"] is True


def test_source_attacks_are_detected_by_hash_and_AST_contracts() -> None:
    attacks = gate._source_attack_campaign()
    assert attacks == {
        "mutate_byte_pinned_upstream_source": True,
        "wrapper_passes_uncanonicalized_free": True,
        "wrapper_does_not_zero_tangent_q": True,
        "invariant_formulas_present_but_not_consumed": True,
        "rotate_only_one_of_EQ_or_varphi": True,
    }
    upstream_text = gate.V5671_SOURCE.read_text(encoding="utf-8")
    unused = upstream_text.replace(
        "+ phi_source\n            + tuple(A_full[mu][a]",
        "+ phi_source_full\n            + tuple(A_full[mu][a]",
        1,
    )
    unused_contract = gate._upstream_source_contract_from_text(unused)
    assert unused_contract["AST_dataflow_contract"][
        "decoder_X64_trace_consumes_reduced_phi_and_A"
    ] is False
    unilateral = upstream_text.replace(
        "E_Q[mu][a] * varphi_Q[a]",
        "E_Q[mu][a] * common[\"varphi_E0\"][a]",
        1,
    )
    unilateral_contract = gate._upstream_source_contract_from_text(unilateral)
    assert unilateral_contract["AST_dataflow_contract"][
        "interface_phi_H_multiplies_EQ_and_varphi_exactly"
    ] is False
    text = MODULE_PATH.read_text(encoding="utf-8")
    late = text.replace(
        "canonical_free, canonical_tangent, section = canonicalize_q_zero_before_decode(\n"
        "        free, tangent, N, K\n"
        "    )\n"
        "    upstream = _load_v5671()",
        "upstream = _load_v5671()\n"
        "    upstream.decode_common_first_boundary_td3(free, tangent, N, K, x)\n"
        "    canonical_free, canonical_tangent, section = canonicalize_q_zero_before_decode(\n"
        "        free, tangent, N, K\n"
        "    )",
        1,
    )
    assert gate._static_wrapper_contract_from_text(late)["pass"] is False


def test_full_report_validator_kills_in_memory_claim_and_ledger_attacks(
    report: dict,
) -> None:
    flipped = copy.deepcopy(report)
    flipped["decision"]["Q_frame_kernel_of_full_Phi_pass"] = True
    _assert_invalid_report(flipped)

    identity = copy.deepcopy(report)
    identity["three_exact_invariant_identities"]["identities"][
        "lateral_affine_connection"
    ]["right_normal_form"] = []
    _assert_invalid_report(identity)

    route = copy.deepcopy(report)
    route["twenty_real_action_routes"]["routes"].pop()
    _assert_invalid_report(route)

    rank = copy.deepcopy(report)
    rank["finite_group_and_global_quotient_no_go"][
        "nonconstant_infinitesimal_orbit_rank"
    ]["generic_pair_rank"] = 2
    _assert_invalid_report(rank)

    overclaim = copy.deepcopy(report)
    overclaim["evidence_boundary"]["global_group_or_smooth_quotient_claimed"] = True
    _assert_invalid_report(overclaim)


def test_main_emits_one_valid_JSON_report_and_writes_no_artifact() -> None:
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HERE.glob("*v5_6_7_4_gate*.json")
    }
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    gate.validate_report(payload)
    after = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HERE.glob("*v5_6_7_4_gate*.json")
    }
    assert after == before
    assert payload["decision"][
        "finite_Q_frame_q_zero_section_and_twenty_route_factorization_pass"
    ] is True


def test_evidence_boundary_separates_finite_sample_exact_no_go_and_continuum(
    report: dict,
) -> None:
    boundary = report["evidence_boundary"]
    assert boundary == {
        "finite_runtime_N_values": [1],
        "exact_BCH_counterexample_N_values": [2],
        "sampled_or_finite_evidence_is_arbitrary_N_theorem": False,
        "continuum_action_or_uniform_bridge_claimed": False,
        "global_group_or_smooth_quotient_claimed": False,
        "complete_kernel_or_constant_rank_claimed": False,
        "q_zero_is_only_coordinate_adapted_section": True,
        "r_plus_minus_unchanged_and_not_quotiented": True,
    }
    assert "Nothing here proves arbitrary-N" in report["scope"]
