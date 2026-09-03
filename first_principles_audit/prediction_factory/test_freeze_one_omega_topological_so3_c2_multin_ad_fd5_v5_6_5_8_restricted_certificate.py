#!/usr/bin/env python3
"""Tests for the additive v5.6.5.8 restricted freeze receipt."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "freeze_one_omega_topological_so3_c2_multin_ad_fd5_v5_6_5_8_restricted_certificate.py"
SPEC = importlib.util.spec_from_file_location("freeze_v5658_restricted", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def test_freeze_receipt_contains_complete_scope_and_h_sweeps() -> None:
    payload = gate.build_payload()
    assert payload["decision"]["v5_6_5_8_restricted_AD_FD5_multin_certificate_frozen"] is True
    members = payload["scientific"]["member_records"]
    assert [row["N"] for row in members] == [1, 2, 3]
    assert [row["K"] for row in members] == [1, 2, 3]
    for row in members:
        window = row["FD5_complete_h_sweep"]
        assert window["steps"] == [0.04, 0.02, 0.01]
        assert [entry["step"] for entry in window["derivatives"]] == [0.04, 0.02, 0.01]
        assert window["unique_endpoint_count"] == 8
        assert row["AD_FD5_diagnostics"]["pass"] is True


def test_sector_table_preserves_every_raw_component_and_error_measure() -> None:
    payload = gate.build_payload()
    table = payload["scientific"]["sector_table"]
    assert len(table) == 3 * 21
    for n_value in (1, 2, 3):
        rows = [row for row in table if row["N"] == n_value]
        assert len(rows) == 21
        assert {row["component"] for row in rows} >= {
            "EH_bulk_plus",
            "GHY_plus",
            "BF_bulk_plus",
            "Robin",
            "full_V4_bulk_plus",
            "wall",
            "S_total",
        }
        assert all("relative_error_to_larger_magnitude" in row for row in rows)
        assert all("symmetric_relative_error" in row for row in rows)
        assert all("FD5_plus_AD_global_flip_residual" in row for row in rows)


def test_freeze_keeps_all_promotion_and_phenomenology_flags_red() -> None:
    decision = gate.build_payload()["decision"]
    for key in (
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


def test_freeze_is_additive_and_requires_hash_pinned_consumers() -> None:
    payload = gate.build_payload()
    contract = payload["immutability_contract"]
    assert contract == {
        "mode": "additive_freeze",
        "upstream_files_modified": False,
        "future_consumers_must_pin_this_receipt_by_sha256": True,
        "retrospective_reinterpretation_forbidden": True,
    }
    assert len(payload["scientific"]["sector_table_sha256"]) == 64
    assert len(payload["frozen_input_pinset_sha256"]) == 64
