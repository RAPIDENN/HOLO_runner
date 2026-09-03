#!/usr/bin/env python3
"""Tests for the additive C2 radial primitive correction."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / (
    "export_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_4_c2_radial_primitives.py"
)
ARTIFACT = HERE / "artifacts" / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_4_c2_radial_primitive_bundle.json"
)
SPEC = importlib.util.spec_from_file_location("c2_radial_primitives_v5644", GENERATOR)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_trace_jet_and_cap_endpoint_contract_is_exact() -> None:
    endpoints = gate.endpoint_contract(4)
    assert endpoints["rho_0"] == {
        "h0": 1.0,
        "h0_first": 0.0,
        "h0_second": 0.0,
        "h1": 0.0,
        "h1_first": 1.0,
        "h1_second": 0.0,
        "bumps_Linf": 0.0,
        "bumps_first_Linf": 0.0,
        "bumps_second_Linf": 0.0,
    }
    assert max(endpoints["rho_1"].values()) == 0.0


def test_analytic_profile_derivatives_match_high_order_fd_interior() -> None:
    r = np.asarray((0.23, 0.41, 0.67), dtype=float)
    h = 1.0e-3
    center = gate.radial_profiles(r, 3)
    plus = gate.radial_profiles(r + h, 3)
    minus = gate.radial_profiles(r - h, 3)
    plus2 = gate.radial_profiles(r + 2.0 * h, 3)
    minus2 = gate.radial_profiles(r - 2.0 * h, 3)
    first = (
        minus2["bumps"]
        - 8.0 * minus["bumps"]
        + 8.0 * plus["bumps"]
        - plus2["bumps"]
    ) / (12.0 * h)
    second = (
        -plus2["bumps"]
        + 16.0 * plus["bumps"]
        - 30.0 * center["bumps"]
        + 16.0 * minus["bumps"]
        - minus2["bumps"]
    ) / (12.0 * h**2)
    assert np.max(np.abs(first - center["bumps_first"])) < 2.0e-9
    assert np.max(np.abs(second - center["bumps_second"])) < 2.0e-7


def test_all_primitive_arrays_are_byte_identical_to_parent() -> None:
    corrected = _payload()
    parent = json.loads(gate.PARENT.read_text(encoding="utf-8"))
    for key in ("primary_members", "identity_controls", "off_collocation_validation_by_N"):
        assert corrected[key] == parent[key]
    assert corrected["action_contract"] == parent["action_contract"]


def test_bundle_is_primitive_only_and_fail_closed_by_absence() -> None:
    payload = _payload()
    assert payload["schema"] == gate.SCHEMA
    assert gate._contains_boolean(payload) is False
    raw = json.dumps(payload, sort_keys=True)
    assert "C1_ACTION_pass" not in raw
    assert "S_total" not in raw


def test_payload_hash_recomputes() -> None:
    payload = _payload()
    observed = payload.pop("payload_sha256")
    assert gate._canonical_sha256(payload) == observed
