#!/usr/bin/env python3
"""Tests for the raw multi-N Torch/AD route."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_torch_route_a_multin_v5_6_5_5.py"
ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_torch_route_a_multin_v5_6_5_5.json"
SPEC = importlib.util.spec_from_file_location("torch_route_a_multin_v5655", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_three_members_and_all_values_are_finite() -> None:
    members = _payload()["scientific"]["members"]
    assert [row["N"] for row in members] == [1, 2, 3]
    for row in members:
        assert len(row["S_rel_components"]) == 21
        assert len(row["AD_JVP_by_component"]) == 21
        assert all(math.isfinite(value) for value in row["S_rel_components"].values())
        assert all(math.isfinite(value) for value in row["AD_JVP_by_component"].values())


def test_every_member_is_pointwise_glued_and_lorentzian() -> None:
    for row in _payload()["scientific"]["members"]:
        diagnostics = row["action_node_diagnostics"]
        assert diagnostics["pointwise_full_gluing_Linf"] < 2.0e-12
        for inertia in diagnostics["lorentzian_inertia_at_every_action_node"].values():
            assert inertia["all_nodes_lorentzian"] is True


def test_route_alone_keeps_comparison_and_promotion_red() -> None:
    decision = _payload()["decision"]
    assert decision["route_A_multin_raw_evaluations_pass"] is True
    for key in (
        "AD_vs_independent_FD5_multin_pass",
        "Euler_Green_independent_route_pass",
        "continuous_limit_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False


def test_route_a_imports_no_numpy_fd5_evaluator() -> None:
    source = GENERATOR.read_text(encoding="utf-8")
    assert "numpy_fd5_action_route_b" not in source
    assert "FD5_action_directional_derivative" not in source
