#!/usr/bin/env python3
"""Tests for the independent corrected C2 NumPy/FD5 multi-N route."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.py"
ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_numpy_c2_multin_fd5_v5_6_5_7.json"
SPEC = importlib.util.spec_from_file_location("numpy_c2_multin_fd5_v5657", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_three_raw_members_have_three_fd5_levels_and_eight_endpoints() -> None:
    members = _payload()["scientific"]["members"]
    assert [row["N"] for row in members] == [1, 2, 3]
    for row in members:
        window = row["FD5_refinement_window"]
        assert window["steps"] == [0.04, 0.02, 0.01]
        assert len(window["derivatives"]) == 3
        assert window["unique_endpoint_count"] == 8
        assert len(row["FD5_Richardson_h002_h001"]) == 21
        assert all(math.isfinite(value) for value in row["FD5_Richardson_h002_h001"].values())


def test_N1_uses_exact_constant_rule_and_others_use_Q5() -> None:
    members = _payload()["scientific"]["members"]
    assert [row["tangential_points_per_axis"] for row in members] == [1, 5, 5]
    assert members[0]["tangential_rule"] == "constant_mode_exact"


def test_every_endpoint_stays_glued_and_lorentzian() -> None:
    for row in _payload()["scientific"]["members"]:
        window = row["FD5_refinement_window"]
        assert max(
            endpoint["pointwise_gluing_Linf"]
            for endpoint in window["endpoint_records_by_float_hex"].values()
        ) < 2.0e-12
        for endpoint in window["endpoint_records_by_float_hex"].values():
            assert endpoint["lorentzian_inertia"]


def test_route_b_does_not_read_route_a_or_promote() -> None:
    source = GENERATOR.read_text(encoding="utf-8")
    assert "import torch" not in source.lower()
    assert "torch_route_a" not in source.lower()
    decision = _payload()["decision"]
    assert decision["route_B_C2_multin_raw_evaluations_pass"] is True
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
