#!/usr/bin/env python3
"""Tests for the fail-closed AD/FD5 comparator."""

from __future__ import annotations

import ast
import copy
import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_action_ad_fd5_comparator_v5_6_5_1_gate.py"
SPEC = importlib.util.spec_from_file_location("action_ad_fd5_comparator_v5651", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def test_comparator_imports_neither_action_evaluator() -> None:
    tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    assert roots <= {
        "__future__",
        "hashlib",
        "json",
        "math",
        "pathlib",
        "typing",
    }
    source = GENERATOR.read_text(encoding="utf-8")
    assert "import derive_one_omega" not in source
    assert "torch" not in roots
    assert "numpy" not in roots


def test_real_pinned_receipts_pass_only_the_direct_two_route_comparison() -> None:
    payload = gate.build_payload()
    decision = payload["decision"]
    assert decision["AD_vs_independent_FD5_comparator_pass"] is True
    assert decision["restricted_spectral_N2_two_route_derivative_certificate_pass"] is True
    for key in (
        "Euler_Green_independent_route_pass",
        "mutant_campaign_pass",
        "independent_clean_process_redteam_pass",
        "multi_N_convergence_pass",
        "continuous_dense_family_theorem_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False

    science = payload["scientific"]
    assert science["input_identity"]["member_id"] == "N2.K2.seed20260902"
    assert science["input_identity"]["quadrature"] == {
        "tangential_points_per_axis": 5,
        "tangential_node_count": 625,
        "radial_gauss_order": 3,
    }
    assert science["central_action_comparison"]["all_output_Linf"] < 5.0e-10
    assert science["R_identity_action_comparison"]["all_output_Linf"] < 5.0e-10
    assert science["Richardson_h4_cancellation"]["twenty_component_L2"] < 2.0e-8
    orders = [
        row["observed_L2_order_from_previous"]
        for row in science["raw_FD5_error_window"][1:3]
    ]
    assert all(3.25 <= order <= 4.75 for order in orders)
    assert abs(science["raw_AD_JVP"]["S_total"]) > 1.0e-6


def test_each_component_omission_and_sign_inversion_kills_direct_gate() -> None:
    route_a, route_b = gate.load_route_receipts()
    for component in gate.ACTION_COMPONENTS:
        omitted = copy.deepcopy(route_b)
        for row in omitted["scientific"]["FD5_refinement_window"]["derivatives"]:
            row["FD5_action_directional_derivative"][component] = 0.0
        result = gate.analyze_route_receipts(route_a, omitted)
        assert result["all_direct_comparison_checks_pass"] is False, component

        inverted = copy.deepcopy(route_b)
        for row in inverted["scientific"]["FD5_refinement_window"]["derivatives"]:
            values = row["FD5_action_directional_derivative"]
            values[component] = -values[component]
        result = gate.analyze_route_receipts(route_a, inverted)
        assert result["all_direct_comparison_checks_pass"] is False, component


def test_input_identity_mismatch_fails_closed() -> None:
    route_a, route_b = gate.load_route_receipts()
    mutant = copy.deepcopy(route_b)
    mutant["input_contract"]["authoritative_free_tangent_sha256"] = "0" * 64
    try:
        gate.analyze_route_receipts(route_a, mutant)
    except gate.ComparatorError as exc:
        assert "identical scientific primitives" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("mismatched tangent was accepted")


def test_upstream_global_promotion_is_rejected_as_input_drift() -> None:
    route_a, route_b = gate.load_route_receipts()
    mutant = copy.deepcopy(route_a)
    mutant["decision"]["C1_ACTION_pass"] = True
    try:
        gate.analyze_route_receipts(mutant, route_b)
    except gate.ComparatorError as exc:
        assert "illegally promoted" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("upstream global promotion was accepted")


def test_every_raw_endpoint_contains_all_twenty_components_plus_total() -> None:
    _, route_b = gate.load_route_receipts()
    endpoints = route_b["scientific"]["FD5_refinement_window"][
        "endpoint_records_by_float_hex"
    ]
    assert len(endpoints) == 12
    for row in endpoints.values():
        assert set(row["S_rel_components"]) == set(gate.OUTPUT_COMPONENTS)
        assert row["pointwise_gluing_Linf"] < 2.0e-12
