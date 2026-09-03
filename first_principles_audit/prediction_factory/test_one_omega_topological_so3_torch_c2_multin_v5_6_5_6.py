#!/usr/bin/env python3
"""Tests for the corrected C2 radial Torch/AD multi-N receipt."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_torch_c2_multin_v5_6_5_6.py"
ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_torch_c2_multin_v5_6_5_6.json"
SPEC = importlib.util.spec_from_file_location("torch_c2_multin_v5656", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_three_members_have_finite_ad_jvps_and_refinement_tables() -> None:
    members = _payload()["scientific"]["members"]
    assert [row["N"] for row in members] == [1, 2, 3]
    for row in members:
        assert set(row["central_S_rel_components_by_radial_order"]) == {"6", "8", "10", "12"}
        assert len(row["AD_JVP_by_component_at_Q5_R10"]) == 21
        assert all(math.isfinite(value) for value in row["AD_JVP_by_component_at_Q5_R10"].values())


def test_quadrature_refinement_is_green_but_cross_route_is_red() -> None:
    decision = _payload()["decision"]
    assert decision["route_A_radial_Q10_Q12_refinement_pass"] is True
    assert decision["route_A_tangential_Q5_Q7_refinement_pass"] is True
    assert decision["route_A_finite_quadrature_convergence_pass"] is True
    assert decision["AD_vs_independent_FD5_multin_pass"] is False


def test_gluing_and_lorentzian_signature_hold_at_every_primary_node() -> None:
    for row in _payload()["scientific"]["members"]:
        diagnostics = row["action_node_diagnostics_at_Q5_R10"]
        assert diagnostics["pointwise_full_gluing_Linf"] < 2.0e-12
        assert all(
            item["all_nodes_lorentzian"] is True
            for item in diagnostics["lorentzian_inertia_at_every_action_node"].values()
        )


def test_global_claims_remain_fail_closed() -> None:
    decision = _payload()["decision"]
    for key in (
        "Euler_Green_independent_route_pass",
        "continuous_limit_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False


def test_no_numpy_route_is_imported() -> None:
    source = GENERATOR.read_text(encoding="utf-8")
    assert "numpy_fd5_action_route_b" not in source
    assert "c2_radial_profiles_torch" in source
