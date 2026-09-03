#!/usr/bin/env python3
"""Tests for the external N=1 Euler--Green comparator."""

from __future__ import annotations

import ast
import copy
import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_n1_euler_green_comparator_v5_6_6_2_gate.py"
SPEC = importlib.util.spec_from_file_location("n1_euler_green_comparator_v5662", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def test_comparator_imports_no_action_or_euler_evaluator() -> None:
    tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    assert roots <= {"__future__", "hashlib", "json", "math", "pathlib", "typing"}
    assert "import derive_one_omega" not in GENERATOR.read_text(encoding="utf-8")


def test_real_N1_receipts_close_only_the_smoke_gate() -> None:
    payload = gate.build_payload()
    assert payload["decision"]["N1_independent_Euler_Green_smoke_pass"] is True
    comparison = payload["scientific"]["direct_route_comparison"]
    assert all(comparison["checks"].values())
    stokes = payload["scientific"]["Euler_Green_Stokes_comparison"]
    assert all(stokes["checks"].values())
    for key in (
        "N2_N3_independent_Euler_Green_pass",
        "Euler_Green_independent_route_pass",
        "clean_room_full_mutant_campaign_pass",
        "uniform_N_to_infinity_bridge_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert payload["decision"][key] is False


def test_omitting_a_material_Green_term_kills_Stokes_gate() -> None:
    frozen, route_c = gate.load_inputs()
    mutant = copy.deepcopy(route_c)
    q20 = next(
        row
        for row in mutant["scientific"]["radial_refinement_records"]
        if row["radial_Gauss_order"] == 20
    )
    green = q20["side_ledgers"]["plus"]["ledger"]["P_kinetic"]["interface_Green"]
    q20["predicted_Euler_Green_by_component"]["P_kinetic_bulk_plus"] -= green
    result = gate.analyze(frozen, mutant)
    assert result["all_N1_checks_pass"] is False
    assert result["Euler_Green_Stokes_comparison"]["checks"]["final_component_residual_pass"] is False


def test_inverting_Brown_York_boundary_kills_Stokes_gate() -> None:
    frozen, route_c = gate.load_inputs()
    mutant = copy.deepcopy(route_c)
    q20 = next(
        row
        for row in mutant["scientific"]["radial_refinement_records"]
        if row["radial_Gauss_order"] == 20
    )
    split = q20["side_ledgers"]["minus"]["EH_GHY_split"]
    brown_york = float(split["combined_Brown_York_boundary"])
    q20["predicted_Euler_Green_by_component"]["EH_bulk_minus"] -= 2.0 * brown_york
    result = gate.analyze(frozen, mutant)
    assert result["all_N1_checks_pass"] is False
    assert result["Euler_Green_Stokes_comparison"]["checks"]["final_component_residual_pass"] is False


def test_substituting_a_circular_expected_vector_is_detected() -> None:
    frozen, route_c = gate.load_inputs()
    mutant = copy.deepcopy(route_c)
    expected = {
        row["component"]: row["AD_JVP"]
        for row in frozen["scientific"]["member_records"][0]["sector_table"]
    }
    mutant["scientific"]["direct_local_jet_JVP_by_component"] = expected
    mutant["independence_audit"]["AD_or_FD_expected_values_read"] = True
    result = gate.analyze(frozen, mutant)
    assert result["all_N1_checks_pass"] is False
    assert result["checks"]["route_C_independence_contract_is_explicit"] is False
