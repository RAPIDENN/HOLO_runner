#!/usr/bin/env python3
"""Tests for the C2 multi-N AD/FD5 sign comparator."""

from __future__ import annotations

import ast
import copy
import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_c2_multin_ad_fd5_sign_comparator_v5_6_5_8_gate.py"
SPEC = importlib.util.spec_from_file_location("c2_multin_sign_comparator_v5658", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def test_comparator_imports_no_action_or_route_implementation() -> None:
    tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    assert roots <= {"__future__", "hashlib", "json", "math", "pathlib", "typing"}
    source = GENERATOR.read_text(encoding="utf-8")
    assert "import torch" not in source
    assert "import numpy" not in source
    assert "import derive_one_omega" not in source


def test_frozen_N1_N2_N3_receipts_agree_without_promoting_C1_N1() -> None:
    payload = gate.build_payload()
    assert payload["decision"]["AD_vs_independent_FD5_multin_pass"] is True
    rows = payload["scientific"]["member_comparisons"]
    assert [row["N"] for row in rows] == [1, 2, 3]
    assert all(row["pass"] for row in rows)
    assert all(row["cosine_similarity_AD_FD5"] >= gate.COSINE_SIMILARITY_MINIMUM for row in rows)
    assert all(not row["active_sign_mismatches"] for row in rows)
    assert all(not row["global_sign_flip_hypothesis"] for row in rows)
    for key in (
        "Euler_Green_independent_route_pass",
        "independent_clean_process_redteam_pass",
        "uniform_spectral_limit_pass",
        "continuous_limit_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert payload["decision"][key] is False


def test_global_sign_flip_is_identified_and_kills_gate() -> None:
    route_a, route_b = gate.load_inputs()
    mutant = copy.deepcopy(route_b)
    for row in mutant["scientific"]["members"]:
        row["FD5_Richardson_h002_h001"] = {
            key: -float(value)
            for key, value in row["FD5_Richardson_h002_h001"].items()
        }
    result = gate.analyze(route_a, mutant)
    assert result["all_checks_pass"] is False
    assert all(row["global_sign_flip_hypothesis"] for row in result["member_comparisons"])
    assert all(not row["checks"]["global_sign_flip_rejected"] for row in result["member_comparisons"])


def test_single_sector_sign_flip_is_identified_and_kills_gate() -> None:
    route_a, route_b = gate.load_inputs()
    mutant = copy.deepcopy(route_b)
    target = mutant["scientific"]["members"][1]["FD5_Richardson_h002_h001"]
    target["EH_bulk_plus"] = -float(target["EH_bulk_plus"])
    result = gate.analyze(route_a, mutant)
    n2 = next(row for row in result["member_comparisons"] if row["N"] == 2)
    assert result["all_checks_pass"] is False
    assert n2["sign_relation_by_component"]["EH_bulk_plus"] == "opposite"
    assert n2["active_sign_mismatches"] == ["EH_bulk_plus"]


def test_primitive_hash_mismatch_fails_closed() -> None:
    route_a, route_b = gate.load_inputs()
    mutant = copy.deepcopy(route_b)
    mutant["scientific"]["members"][0]["authoritative_free_tangent_sha256"] = "0" * 64
    try:
        gate.analyze(route_a, mutant)
    except gate.SignComparatorError as exc:
        assert "primitive identity mismatch" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("mismatched primitive tangent hash was accepted")


def test_tolerances_are_owned_by_comparator_not_read_from_routes() -> None:
    source = GENERATOR.read_text(encoding="utf-8")
    assert "DERIVATIVE_COMPONENT_L2_ABS_FLOOR = 2.0e-8" in source
    assert "ACTIVE_COMPONENT_REL_TOLERANCE = 1.0e-7" in source
    route_a, route_b = gate.load_inputs()
    assert "tolerance" not in str(route_a.get("source_pins", {})).lower()
    assert "tolerance" not in str(route_b.get("source_pins", {})).lower()
