#!/usr/bin/env python3
"""Tests for exact additive component-action mutants."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_component_action_mutants_v5_6_5_3.py"
SPEC = importlib.util.spec_from_file_location("component_action_mutants_v5653", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def test_mutated_endpoint_recomputes_total_from_twenty_terms() -> None:
    nominal = {component: float(index + 1) for index, component in enumerate(gate.ACTION_COMPONENTS)}
    nominal["S_total"] = -999.0
    omitted = gate._mutated_endpoint(nominal, "R_squared", "omit")
    assert omitted["R_squared"] == 0.0
    assert omitted["S_total"] == math.fsum(omitted[name] for name in gate.ACTION_COMPONENTS)
    inverted = gate._mutated_endpoint(nominal, "BF_bulk_plus", "invert_sign")
    assert inverted["BF_bulk_plus"] == -nominal["BF_bulk_plus"]
    assert inverted["S_total"] == math.fsum(inverted[name] for name in gate.ACTION_COMPONENTS)


def test_real_raw_endpoint_campaign_kills_all_forty_mutants() -> None:
    route_a, route_b, comparator = gate.load_inputs()
    campaign = gate.run_mutant_campaign(route_a, route_b, comparator)
    assert campaign["mutant_count"] == 40
    assert campaign["all_mutants_killed"] is True
    identifiers = {row["id"] for row in campaign["records"]}
    assert len(identifiers) == 40
    assert "omit_R_squared" in identifiers
    assert "invert_sign_BF_bulk_minus" in identifiers
    assert all(row["target_component_relative_residual"] > gate.COMPONENT_REL_TOLERANCE for row in campaign["records"])


def test_payload_keeps_special_mutants_and_promotions_red() -> None:
    payload = gate.build_payload()
    decision = payload["decision"]
    assert decision["exact_additive_40_mutant_campaign_pass"] is True
    assert decision["special_geometric_action_mutants_pass"] is False
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


def test_nominal_values_are_not_read_from_comparator_expected_strings() -> None:
    source = GENERATOR.read_text(encoding="utf-8")
    assert "expected_derivative" not in source
    assert "nominal_AD_target_derivative" in source
    assert "S_rel_components" in source
