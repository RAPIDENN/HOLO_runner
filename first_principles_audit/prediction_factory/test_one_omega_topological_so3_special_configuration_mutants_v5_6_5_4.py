#!/usr/bin/env python3
"""Tests for the finite-N special configuration mutation receipt."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / (
    "derive_one_omega_topological_so3_special_configuration_mutants_"
    "v5_6_5_4.py"
)
ARTIFACT = HERE / "artifacts" / (
    "one_omega_topological_so3_special_configuration_mutants_"
    "v5_6_5_4.json"
)
SPEC = importlib.util.spec_from_file_location("special_configuration_mutants_v5654", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def _inputs():
    route_b, _a, _b, bundle = gate.load_inputs()
    member = bundle["primary_member"]
    layout = bundle["pointwise_decoder_contract"]["free_layout"]["blocks"]
    free = route_b._decode_f64(member["authoritative_free_central_f64le"])
    joint = next(
        curve
        for curve in member["curves"]
        if curve["comparison_role"] == "primary_scientific_comparator"
    )
    tangent = route_b._decode_f64(joint["authoritative_free_tangent_f64le"])
    return route_b, layout, free, tangent


def test_freeze_relative_rotation_only_zeros_the_two_r_blocks() -> None:
    route_b, layout, _free, tangent = _inputs()
    mutated = gate.freeze_relative_rotation_tangent(tangent, layout)
    changed = np.flatnonzero(mutated != tangent)
    expected = []
    for side in route_b.SIDES:
        item = layout[f"{side}.r_E0"]
        expected.extend(range(int(item["start"]), int(item["stop"])))
        assert np.count_nonzero(gate._block_view(mutated, layout, f"{side}.r_E0")) == 0
    assert set(changed).issubset(set(expected))
    assert changed.size > 0


def test_reflected_z2_transform_is_idempotent_and_central_is_non_z2() -> None:
    route_b, layout, free, _tangent = _inputs()
    before = gate.z2_free_residual(free, layout, route_b)
    transformed = gate.impose_reflected_z2_free_data(free, layout, route_b)
    twice = gate.impose_reflected_z2_free_data(transformed, layout, route_b)
    assert before > gate.ACTION_DELTA_KILL_ABS
    assert gate.z2_free_residual(transformed, layout, route_b) == 0.0
    assert np.array_equal(transformed, twice)


def test_tensor_component_parities_cover_all_64_channels() -> None:
    route_b, _layout, _free, _tangent = _inputs()
    parity = gate._tensor_component_parities(route_b)
    assert parity.shape == (64,)
    assert set(np.unique(parity)) == {-1.0, 1.0}
    assert parity[15] == 1.0
    assert np.all(parity[16:19] == 1.0)


def test_frozen_artifact_kills_executed_mutants_but_keeps_promotion_red() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["schema"] == gate.SCHEMA
    decision = payload["decision"]
    assert decision["executed_nonadditive_mutants_killed"] is True
    assert decision["T_ui_matter_nonzero_same_family_witness_pass"] is True
    assert decision["T_ui_matter_independent_action_shift_JVP_match_pass"] is True
    assert decision["special_geometric_action_mutants_pass"] is True
    for key in (
        "Euler_Green_independent_route_pass",
        "independent_clean_process_redteam_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False


def test_mutation_harness_does_not_encode_a_promotion_shortcut() -> None:
    source = GENERATOR.read_text(encoding="utf-8")
    assert "C1_ACTION_pass\": True" not in source
    assert "N1_ACTION_pass\": True" not in source
    assert "C1_N1_promotion_authorized\": True" not in source
    assert "local_action_shift_maximum_absolute_error" in source
