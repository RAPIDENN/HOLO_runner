#!/usr/bin/env python3
"""Tests for the clean-process Route-C and mutant red-team gate."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_clean_process_mutant_redteam_v5_6_6_7
    as gate,
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    assert gate.OUTPUT.exists()
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def test_orchestrator_imports_no_scientific_route_helper() -> None:
    tree = ast.parse(Path(gate.__file__).read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    assert not any("one_omega_topological_so3" in name for name in imports)
    assert "importlib" not in imports
    assert "runpy" not in imports


def test_route_c_static_boundary_is_primary_free(receipt: dict) -> None:
    audit = receipt["scientific"]["Route_C_static_independence"]
    assert audit["primary_action_or_comparator_helpers_imported"] is False
    assert audit["primary_AD_or_FD5_receipt_symbols_read"] is False
    assert audit["primitive_bundle_only_scientific_input"] is True
    assert receipt["independence_boundary"][
        "Route_C_primary_AD_or_FD5_receipts_read"
    ] is False


def test_clean_execution_is_byte_identical_and_multi_n(receipt: dict) -> None:
    execution = receipt["scientific"]["clean_execution"]
    assert execution["target_commit"] == gate.FROZEN_COMMIT
    assert execution["module_loaded_under_clean_worktree"] is True
    assert execution["clean_status_before"] == ""
    assert execution["clean_status_after"] == ""
    assert len(execution["jobs"]) == 4
    assert all(row["exit_code"] == 0 for row in execution["jobs"])
    assert all(
        row["byte_identical_to_frozen_checkpoint"] is True
        for row in execution["jobs"]
    )
    assert [(row["N"], row["K"]) for row in execution["route_C"]["members"]] == [
        (1, 1),
        (2, 2),
        (3, 3),
    ]


def test_full_mutant_coverage_is_explicit(receipt: dict) -> None:
    execution = receipt["scientific"]["clean_execution"]
    additive = execution["additive_component_mutants"]
    special = execution["special_geometric_mutants"]
    assert additive["mutant_count"] == 40
    assert set(additive["covered_components"]) == gate.REQUIRED_COMPONENTS
    assert additive["covered_operations"] == ["omit", "invert_sign"]
    assert special["mutant_count"] == 7
    assert set(special["killed_mutants"]) == gate.REQUIRED_SPECIAL_MUTANTS
    assert special["T_ui_matter_independent_action_shift_JVP_match_pass"] is True
    assert special["T_ui_matter_nonzero_same_family_witness_pass"] is True


def test_eight_faces_and_underresolved_red_are_preserved(receipt: dict) -> None:
    execution = receipt["scientific"]["clean_execution"]
    stokes = execution["eight_face_Stokes"]
    assert stokes["probe_count"] == 2
    assert stokes["face_count_per_probe"] == [8, 8]
    assert max(stokes["total_oriented_boundary_flux_absolute"]) < 2.0e-14
    assert stokes["minimum_mutant_witness"] > 1.0e-6
    resolution = execution["resolution_adjudication"]
    assert resolution["false_refinement_witness_count"] > 0
    assert resolution["precision_correction_pass"] is True
    assert resolution["archived_red_receipt_sha256"] == gate.EXPECTED_SHA256[
        "underresolved_artifact"
    ]


def test_only_clean_room_and_mutants_are_promoted(receipt: dict) -> None:
    decision = receipt["decision"]
    for key in (
        "Route_C_clean_process_byte_reproduction_pass",
        "full_mutant_campaign_pass",
        "independent_clean_process_redteam_pass",
        "clean_room_and_mutants_pass",
    ):
        assert decision[key] is True
    for key in (
        "uniform_N_to_infinity_bridge_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False


def test_receipt_is_canonical_and_provenance_is_current(receipt: dict) -> None:
    encoded = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert gate.OUTPUT.read_text(encoding="utf-8") == encoded
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(
        Path(gate.__file__)
    )
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
    assert receipt["scientific_payload_sha256"] == gate._canonical_sha256(
        receipt["scientific"]
    )


@pytest.mark.skipif(
    os.environ.get("RUN_HOLO_V5667_CLEAN_INTEGRATION") != "1",
    reason="explicit opt-in required for the heavy detached-worktree reproduction",
)
def test_heavy_clean_campaign_reproduces_frozen_science(receipt: dict) -> None:
    regenerated = gate.build_payload(gate.run_clean_campaign())
    assert regenerated["scientific_payload_sha256"] == receipt[
        "scientific_payload_sha256"
    ]
