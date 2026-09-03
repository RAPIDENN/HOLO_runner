#!/usr/bin/env python3
"""Structural tests for the primitive-only N=1,2,3 export."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / (
    "export_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_3_multin_primitives.py"
)
ARTIFACT = HERE / "artifacts" / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_3_multin_primitive_bundle.json"
)
SPEC = importlib.util.spec_from_file_location("multin_primitive_export_v5643", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def _artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_bundle_has_three_nested_primary_members_and_controls() -> None:
    payload = _artifact()
    assert payload["schema"] == gate.SCHEMA
    assert [row["N"] for row in payload["primary_members"]] == [1, 2, 3]
    assert [row["N"] for row in payload["identity_controls"]] == [1, 2, 3]
    assert set(payload["pointwise_decoder_contract_by_N"]) == {"1", "2", "3"}


def test_each_primary_member_has_all_four_primitive_curves() -> None:
    for member in _artifact()["primary_members"]:
        names = {curve["name"] for curve in member["curves"]}
        assert names == {
            "compact_bulk_SO3_horizontal_candidate",
            "embedding_motion_SO3_horizontal_candidate",
            "free_B_SO3_horizontal_candidate",
            "joint_all_primitive_classes_control_candidate",
        }


def test_raw_pointwise_gluing_is_machine_small_for_every_N() -> None:
    frozen = gate.load_frozen_exporter()
    payload = _artifact()
    maximum = 0.0
    for N, section in payload["off_collocation_validation_by_N"].items():
        del N
        for record in section["raw_pointwise_gluing_diagnostics"]:
            for side in record["raw_defects_f64le"].values():
                for encoded in side.values():
                    values = frozen._decode_f64(encoded)
                    maximum = max(maximum, float(abs(values).max()))
    assert maximum < 2.0e-12


def test_no_boolean_or_action_result_is_embedded() -> None:
    payload = _artifact()
    assert gate._contains_boolean(payload) is False
    source = json.dumps(payload, sort_keys=True)
    assert "C1_ACTION_pass" not in source
    assert "S_total" not in source
    assert "Eulerian" not in source


def test_payload_hash_recomputes_before_its_own_field() -> None:
    payload = _artifact()
    observed = payload.pop("payload_sha256")
    assert gate._canonical_sha256(payload) == observed
