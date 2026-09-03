#!/usr/bin/env python3
"""Strict tests for the reusable two-sided primitive family engine."""

from __future__ import annotations

import ast
from dataclasses import asdict, fields
import hashlib
import json
from pathlib import Path

import numpy as np

if __package__:
    from . import derive_one_omega_topological_so3_two_sided_groupoid_non_z2_v5_6_3_gate as gate
else:
    import derive_one_omega_topological_so3_two_sided_groupoid_non_z2_v5_6_3_gate as gate


def _artifact() -> dict:
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(value, dtype="<f8").tobytes()
    ).hexdigest()


def test_artifact_is_byte_canonical_fresh_and_reproducible() -> None:
    assert gate.OUTPUT.exists()
    first = gate.build_payload()
    second = gate.build_payload()
    assert first == second == _artifact()
    encoded = json.dumps(first, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert gate.OUTPUT.read_bytes() == encoded.encode("utf-8")
    assert first["scientific_sha256"] == _canonical_sha256(first["scientific"])


def test_upstreams_are_exactly_pinned_without_helpers_or_derived_consumption() -> None:
    payload = _artifact()
    assert set(payload["upstream_byte_pins"]) == set(gate.SOURCE_PINS)
    for name, pin in gate.SOURCE_PINS.items():
        row = payload["upstream_byte_pins"][name]
        assert row["schema"] == pin.schema
        assert row["sha256"] == {
            "artifact": pin.artifact_sha256,
            "generator": pin.generator_sha256,
            "test": pin.test_sha256,
        }
        assert row["decision_boolean_consumed"] is False
        assert row["action_value_or_density_consumed"] is False
        assert row["Eulerian_or_residual_consumed"] is False
        assert row["helper_imported_or_called"] is False
    source = Path(gate.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    forbidden = (
        "classical_v5_2",
        "full_moving_c1_n1_v5_6_2",
        "robin_frame_groupoid_v5_6_2",
    )
    assert not any(any(token in name for token in forbidden) for name in imported)
    function_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert not any(
        token in name.lower()
        for name in function_names
        for token in ("action", "density", "euler", "green")
    )
    assert payload["provenance"]["upstream_helpers_imported"] == []


def test_family_spec_is_declarative_and_has_no_derived_physics_objects() -> None:
    spec = gate.family_spec()
    names = {item.name for item in fields(spec)}
    assert len(spec.seeds) >= 3
    assert spec.identity_control_seed in spec.seeds
    assert not names.intersection(
        {"action", "density", "P", "F", "Euler", "Green", "expected"}
    )
    serialized = asdict(spec)
    assert json.loads(json.dumps(serialized))
    contract = _artifact()["consumer_contract"]
    assert set(contract["derived_objects_absent"]) == {
        "action", "densities", "P", "F", "Euler", "Green", "expected_solution"
    }
    assert contract["name_separation"]["freeze_spatial_R3"].startswith(
        "different curvature mutant"
    )


def test_identity_control_and_two_noncommuting_two_sided_members() -> None:
    spec = gate.family_spec()
    members = {seed: gate.build_member(seed) for seed in spec.seeds}
    control = gate.member_kinematic_invariants(members[spec.identity_control_seed])
    assert control["R_plus_minus_Linf"] < 2.0e-14
    for side in ("plus", "minus"):
        assert np.max(
            np.abs(members[spec.identity_control_seed]["sides"][side]["R"] - np.eye(3))
        ) < 2.0e-14
    for seed in spec.seeds:
        raw = gate.member_kinematic_invariants(members[seed])
        for side in ("plus", "minus"):
            assert max(raw["per_side_without_cross_side_summation"][side].values()) < 3.0e-12
        assert raw["gamma_plus_minus_Linf"] < 3.0e-12
        assert raw["frame_orthonormality_Linf"] < 3.0e-12
        assert raw["frame_spatiality_Linf"] < 3.0e-12
        assert raw["B_oriented_flux_equation_imposed"] is False
        assert raw["B_oriented_flux_raw_Linf"] > 1.0e-3
    for seed in spec.seeds:
        if seed == spec.identity_control_seed:
            continue
        raw = gate.member_kinematic_invariants(members[seed])
        assert raw["R_plus_minus_Linf"] > 1.0e-3
        assert raw["R_plus_R_minus_commutator_Linf"] > 1.0e-5


def test_common_gluing_is_constructed_and_B_remains_side_local_off_shell() -> None:
    member = gate.build_member(17)
    assert not np.array_equal(
        member["sides"]["plus"]["source_phi_trace"],
        member["sides"]["minus"]["source_phi_trace"],
    )
    assert not np.array_equal(
        member["sides"]["plus"]["target_B_trace"],
        member["sides"]["minus"]["target_B_trace"],
    )
    for side in ("plus", "minus"):
        row = member["sides"][side]
        rotation = row["R"]
        transpose = np.swapaxes(rotation, -1, -2)
        assert np.max(
            np.abs(
                np.einsum("...ab,...b->...a", rotation, row["source_phi_trace"])
                - member["targets"]["varphi_H"]
            )
        ) < 2.0e-13
        transported_a = (
            rotation[..., None, :, :]
            @ row["source_A_trace_matrix"]
            @ transpose[..., None, :, :]
            - row["dR"] @ transpose[..., None, :, :]
        )
        assert np.max(
            np.abs(transported_a - member["targets"]["A_Sigma_matrix"])
        ) < 3.0e-13
        assert np.max(
            np.abs(
                np.einsum("...ab,...kb->...ka", rotation, row["source_B_trace"])
                - row["target_B_trace"]
            )
        ) < 2.0e-13


def test_collar_has_common_traces_and_real_side_specific_normal_jets() -> None:
    member = gate.build_member(29)
    plus_signature = gate._jet_signature(member, "plus")
    minus_signature = gate._jet_signature(member, "minus")
    assert np.max(np.abs(plus_signature - minus_signature)) > 1.0e-3
    rho = member["coordinates"]["rho"]
    chi, chi_prime = gate._chi(rho)
    bump = rho * chi
    bump_prime = chi + rho * chi_prime
    assert bump[0] == 0.0
    assert bump_prime[0] == 1.0
    for side in ("plus", "minus"):
        row = member["sides"][side]
        assert np.array_equal(row["metric"][0], gate._ambient_metric(
            member["graph"]["Y"], member["coefficients"]["ambient_metric"]
        )[0])
        assert np.max(
            np.abs(row["fields"]["Omega"][0] - member["targets"]["Omega"])
        ) < 2.0e-14
        assert np.max(
            np.abs(row["fields"]["phi"][0] - row["source_phi_trace"])
        ) < 2.0e-13
        for field in ("Omega", "v", "phi", "A", "B"):
            extra = (None,) * (row["field_rho"][field].ndim - 2)
            reconstructed = row["field_q"][field] * row["q_rho"][(...,) + extra]
            assert np.max(np.abs(reconstructed - row["field_rho"][field])) < 3.0e-13
        inverse = row["inverse_coordinate_jacobian"]
        assert np.max(
            np.abs(row["q_rho"] * inverse["partial_q_from_partial_rho"] - 1.0)
        ) < 2.0e-14
        assert np.max(
            np.abs(
                row["q_t_at_rho"]
                + row["q_rho"] * inverse["partial_t_at_q_from_partial_rho"]
            )
        ) < 2.0e-14
        assert np.max(
            np.abs(
                row["q_x_at_rho"]
                + row["q_rho"] * inverse["partial_x_at_q_from_partial_rho"]
            )
        ) < 2.0e-14


def test_every_admissible_tangent_is_coupled_active_and_preserves_linearized_gluing() -> None:
    required = {
        "embedding", "frame", "common_Omega", "common_varphi", "common_A",
        "plus:g", "minus:g", "plus:Omega", "minus:Omega",
        "plus:phi", "minus:phi", "plus:A", "minus:A",
        "plus:B", "minus:B", "plus:R", "minus:R",
    }
    payload = _artifact()
    for seed in gate.family_spec().seeds:
        receipts = payload["scientific"]["tangent_receipts"][str(seed)]
        assert len(receipts) == len(gate.admissible_tangents())
        for receipt in receipts:
            activity = receipt["raw_primitive_tangent_L2"]
            assert required.issubset(activity)
            assert min(activity[name] for name in required) > 1.0e-7
            for side in ("plus", "minus"):
                row = receipt["per_side_gluing_without_cross_side_summation"][side]
                assert row["finite_plus_gluing_Linf"] < 3.0e-12
                assert row["finite_minus_gluing_Linf"] < 3.0e-12
                assert row["linearized_gluing_Linf"] < 3.0e-9
            assert set(receipt["raw_primitive_tangent_sha256"]) == set(activity)


def test_primitive_hashes_are_reconstructible_without_action_helpers() -> None:
    member = gate.build_member(17)
    arrays = gate._primitive_arrays(member)
    receipt = next(
        item
        for item in _artifact()["scientific"]["member_receipts"]
        if item["seed"] == 17
    )
    assert receipt["primitive_sha256"] == {
        name: _array_sha256(value) for name, value in sorted(arrays.items())
    }
    assert receipt["all_primitives_sha256"] == _canonical_sha256(
        receipt["primitive_sha256"]
    )


def test_named_mutants_are_groupoid_specific_and_all_are_detected() -> None:
    mutants = _artifact()["scientific"]["mutant_witnesses"]
    assert set(mutants) == {
        "freeze_groupoid_R_plus",
        "freeze_groupoid_R_minus",
        "rotate_only_phi",
        "wrong_R_side",
        "wrong_R_sign",
        "reuse_plus_jet_on_minus",
        "break_common_trace",
        "omit_collar_chain_rule",
    }
    assert "freeze_R" not in mutants
    assert "freeze_spatial_R3" not in mutants
    assert min(mutants.values()) > 1.0e-5


def test_master_action_and_physical_claims_remain_fail_closed() -> None:
    payload = _artifact()
    decision = payload["scientific"]["decision"]
    assert decision["two_sided_groupoid_non_Z2_v5_6_3_family_engine_pass"] is True
    assert decision["serializable_member_builder_pass"] is True
    assert decision["admissible_coupled_tangent_builder_pass"] is True
    assert decision["B_oriented_flux_equation_imposed"] is False
    for key in gate.FAIL_CLOSED_KEYS:
        assert decision[key] is False
    assert decision["C1_ACTION_pass"] is False
    assert decision["N1_ACTION_pass"] is False
    assert decision["B4_pass"] is False
    assert decision["B5_pass"] is False
    assert decision["LOCK_1_contamination_cleared_pass"] is False
