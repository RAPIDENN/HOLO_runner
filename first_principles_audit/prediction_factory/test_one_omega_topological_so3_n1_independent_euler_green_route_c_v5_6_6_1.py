#!/usr/bin/env python3
"""Tests for the independent N=1 Euler--Green route C."""

from __future__ import annotations

import ast
import importlib.util
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_n1_independent_euler_green_route_c_v5_6_6_1.py"
SPEC = importlib.util.spec_from_file_location("n1_euler_green_route_c_v5661", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
route = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = route
SPEC.loader.exec_module(route)
PAYLOAD = route.build_payload()


def test_route_imports_no_project_action_or_expected_route() -> None:
    tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    assert roots <= {"__future__", "base64", "hashlib", "json", "math", "pathlib", "typing", "numpy"}
    source = GENERATOR.read_text(encoding="utf-8")
    assert "import torch" not in source
    assert "import derive_one_omega" not in source
    assert "v5_6_5_8_restricted_certificate" not in source


def test_route_publishes_all_components_and_nonvacuous_ledgers() -> None:
    payload = PAYLOAD
    values = payload["scientific"]["predicted_Euler_Green_by_component"]
    assert set(values) == set(route.ACTION_COMPONENTS) | {"S_total"}
    assert all(math.isfinite(float(value)) for value in values.values())
    assert math.isclose(
        values["S_total"],
        math.fsum(values[name] for name in route.ACTION_COMPONENTS),
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    for side in route.SIDES:
        ledger = payload["scientific"]["side_ledgers"][side]["ledger"]
        assert set(ledger) == {
            "EH",
            "Omega_kinetic",
            "Omega_potential",
            "P_kinetic",
            "full_V4",
            "BF",
        }
        assert all(row["pointwise_Euler_activity_Linf"] > 0.0 for row in ledger.values())
        assert abs(ledger["Omega_kinetic"]["interface_Green"]) > 1.0e-6
        assert abs(ledger["P_kinetic"]["interface_Green"]) > 1.0e-6
        assert abs(ledger["BF"]["interface_Green"]) > 1.0e-6


def test_nontrivial_R_outer_flatness_and_no_corner_are_explicit() -> None:
    scientific = PAYLOAD["scientific"]
    assert all(
        row["distance_from_identity_Frobenius"] > 1.0e-3
        for row in scientific["nontrivial_R_controls"].values()
    )
    assert scientific["outer_boundary_tangent_Linf"] < 2.0e-10
    assert scientific["corner_residual"] == 0.0
    faces = scientific["face_audit"]["tangential_T4_eight_faces"]
    assert len(faces) == 8
    assert all(value == 0.0 for value in faces.values())


def test_radial_Stokes_residual_contracts_to_the_fixed_floor() -> None:
    convergence = PAYLOAD["scientific"]["Stokes_convergence"]
    assert convergence["monotone_component_contraction"] is True
    assert convergence["monotone_total_contraction"] is True
    assert convergence["maximum_component_residual_series"][-1] <= 5.0e-8
    assert convergence["total_residual_series"][-1] <= 5.0e-8
    assert convergence["pass"] is True


def test_N1_smoke_does_not_promote_any_full_gate() -> None:
    decision = PAYLOAD["decision"]
    assert decision["route_C_N1_independent_Euler_Green_raw_pass"] is True
    for key in (
        "route_C_N2_N3_independent_Euler_Green_pass",
        "Euler_Green_independent_route_pass",
        "clean_room_full_mutant_campaign_pass",
        "uniform_N_to_infinity_bridge_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False
