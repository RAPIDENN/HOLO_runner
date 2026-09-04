from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_route_a_c2_ad_vs_route_c_four_direction_v5_6_6_17
    as gate,
)


EXPECTED_TRUE = {
    "v5_6_6_15_sampled_density_receipt_byte_pinned_pass",
    "selected_N123_four_published_curve_lineages_byte_aligned_pass",
    "selected_N123_bundle_wavevectors_depend_only_on_theta_x0_plus_x1_pass",
    "restricted_Q5_theta_only_grid_residue_multiplicity_identity_pass",
    "Route_A_and_Route_C_GL10_nodes_weights_numeric_match_pass",
    "Route_C_selected_evaluation_metadata_match_requested_campaign_pass",
    "route_A_C2_AD_and_precision_stabilized_route_C_selected_fixed_Q_evaluations_completed_pass",
    "route_A_C2_AD_vs_precision_stabilized_route_C_selected_N123_four_curves_Q5_R10_componentwise_within_fixed_tolerance_pass",
    "route_A_and_route_C_twenty_sector_totals_additive_within_fixed_tolerance_pass",
    "joint_direction_strictly_reproduces_pinned_v5_6_6_6_receipt_pass",
    "single_component_sign_flip_canary_rejected_pass",
    "positional_zip_component_order_canary_rejected_pass",
}
EXPECTED_FALSE = {
    "same_functional_symbolic_identity_pass",
    "actual_route_A_route_C_integrand_nodewise_identity_audited_pass",
    "route_A_fixed_Q_AD_equals_continuum_first_variation_pass",
    "route_A_C2_JVP_quadrature_convergence_pass",
    "route_C_free_FD5_exact_derivative_pass",
    "route_C_coordinate_stencil_exact_derivative_pass",
    "Q_h_limit_commutation_proved_pass",
    "differentiation_and_quadrature_limit_interchange_pass",
    "route_A_float64_roundoff_enclosed_pass",
    "selected_member_open_tube_branch_smoothness_certified_pass",
    "route_C_B_FD_Q_to_infinity_estimate_pass",
    "route_C_B_FD_rigorous_bound_pass",
    "density_union_C_N_pass",
    "spectral_N_convergence_pass",
    "periodic_box_exhaustion_and_tail_control_pass",
    "uniform_stability_pass",
    "independent_clean_process_redteam_pass",
    "full_mutant_campaign_pass",
    "uniform_N_to_infinity_bridge_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "C1_N1_promotion_authorized",
    "B4_pass",
    "B5_pass",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def receipt() -> dict:
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def test_schema_and_canonical_serialization(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    expected = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert gate.OUTPUT.read_text(encoding="utf-8") == expected


def test_provenance_hashes_current_generator_and_test(receipt: dict) -> None:
    assert receipt["provenance"]["generator"]["sha256"] == _sha256(Path(gate.__file__))
    assert receipt["provenance"]["test"]["sha256"] == _sha256(Path(__file__))


def test_scientific_payload_hash_is_exact(receipt: dict) -> None:
    assert receipt["scientific_payload_sha256"] == gate._canonical_sha256(
        receipt["scientific"]
    )


def test_decision_allowlist_and_fail_closed(receipt: dict) -> None:
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE | EXPECTED_FALSE
    assert all(decision[key] is True for key in EXPECTED_TRUE)
    assert all(decision[key] is False for key in EXPECTED_FALSE)


def test_fixed_campaign_contract(receipt: dict) -> None:
    fixed = receipt["fixed_before_run"]
    assert fixed["member_N"] == [1, 2, 3]
    assert fixed["curve_names"] == list(gate.CURVE_NAMES)
    assert fixed["tangential_order_per_axis"] == 5
    assert fixed["radial_order"] == 10
    assert fixed["Route_C_free_step"] == pytest.approx(2.0e-3, abs=0.0)
    assert fixed["process_workers"] == 3
    assert fixed["radial_node_weight_alignment_tolerance"] == pytest.approx(
        1.0e-14, abs=0.0
    )
    assert fixed["joint_direction_reproduction_absolute_tolerance"] == pytest.approx(
        1.0e-10, abs=0.0
    )
    assert fixed["component_alignment"] == "by exact name, never by position"
    assert "exact combinatorial residue multiplicity" in fixed[
        "tangential_quadrature_relation"
    ]


def test_member_curve_and_component_coverage(receipt: dict) -> None:
    members = receipt["scientific"]["members"]
    bundle = json.loads(gate.BUNDLE.read_text(encoding="utf-8"))
    expected_members = {int(member["N"]): member for member in bundle["primary_members"]}
    assert [member["N"] for member in members] == [1, 2, 3]
    assert len(members) == 3
    for member in members:
        expected_member = expected_members[member["N"]]
        expected_curves = {curve["name"]: curve for curve in expected_member["curves"]}
        assert member["authoritative_free_central_sha256"] == expected_member[
            "authoritative_free_central_f64le"
        ]["sha256"]
        assert member["member_sampled_fixed_Q_cross_route_pass"] is True
        assert [curve["curve_name"] for curve in member["curves"]] == list(
            gate.CURVE_NAMES
        )
        assert len(member["curves"]) == 4
        for curve in member["curves"]:
            assert curve["authoritative_free_tangent_sha256"] == expected_curves[
                curve["curve_name"]
            ]["authoritative_free_tangent_f64le"]["sha256"]
            left = curve["Route_A_C2_AD_JVP"]
            right = curve[
                "Route_C_precision_stabilized_free_directional_estimate"
            ]
            assert set(left) == set(right)
            assert len(left) == 21
            assert set(left) == set(gate.EXPECTED_COMPONENT_NAMES)
            assert set(curve["comparison"]["rows"]) == set(left)
            assert all(math.isfinite(value) for value in left.values())
            assert all(math.isfinite(value) for value in right.values())
            assert curve["curve_sampled_fixed_Q_cross_route_pass"] is True
            assert curve["Route_C_evaluation_metadata"] == {
                "N": member["N"],
                "K": member["K"],
                "member_id": member["member_id"],
                "curve_name": curve["curve_name"],
                "tangential_order": 5,
                "radial_order": 10,
                "free_step": gate.FREE_STEP,
            }
    summary = receipt["scientific"]["campaign_summary"]
    assert summary["member_count"] == 3
    assert summary["curve_count"] == 12
    assert summary["component_count_per_curve"] == 21


def test_restricted_quadrature_relation_is_explicit(receipt: dict) -> None:
    relation = receipt["scientific"]["quadrature_relation"]
    basis = relation["selected_bundle_theta_only_wavevector_audit"]
    assert basis["pass"] is True
    for row in basis["members"].values():
        assert row["depends_only_on_theta_x0_plus_x1_pass"] is True
        assert all(k[0] == k[1] and k[2:] == [0, 0] for k in row["mode_wavevectors"])
    tangential = relation["restricted_T4_tensor_grid_residue_multiplicity"]
    assert tangential["Route_A_tensor_node_count"] == 625
    assert tangential["Route_C_reduced_theta_node_count"] == 5
    assert tangential["residue_multiplicities"] == [125] * 5
    assert tangential["multiplicity_and_normalized_weight_identity_pass"] is True
    radial = relation["radial_GL10_implementation_alignment"]
    assert radial["order"] == 10
    assert radial["numeric_match_pass"] is True
    assert radial["maximum_node_absolute_difference"] <= 1.0e-14
    assert radial["maximum_weight_absolute_difference"] <= 1.0e-14


def test_residue_ledger_recomputes_exactly(receipt: dict) -> None:
    recorded = receipt["scientific"]["quadrature_relation"][
        "restricted_T4_tensor_grid_residue_multiplicity"
    ]
    assert gate.restricted_t4_to_theta_grid_reduction(5) == recorded


def test_every_component_respects_predeclared_tolerance_and_sign(receipt: dict) -> None:
    for member in receipt["scientific"]["members"]:
        for curve in member["curves"]:
            comparison = curve["comparison"]
            assert comparison["pass"] is True
            assert comparison["maximum_difference_over_tolerance"] <= 1.0
            assert math.isfinite(comparison["cosine"])
            for row in comparison["rows"].values():
                scale = max(
                    abs(row["Route_A_C2_AD"]),
                    abs(row["Route_C_precision_stabilized_free_directional_estimate"]),
                )
                assert row["fixed_tolerance"] == pytest.approx(
                    1.0e-8 + 1.0e-11 * scale, rel=0.0, abs=1.0e-24
                )
                assert row["absolute_difference"] <= row["fixed_tolerance"]
                assert row["same_sign_when_active"] is True
                assert row["pass"] is True


def test_sector_ledgers_and_canaries(receipt: dict) -> None:
    for member in receipt["scientific"]["members"]:
        for curve in member["curves"]:
            assert all(
                row["pass"] is True
                for row in curve["sector_additivity"].values()
            )
            canary = curve["sign_flip_canary"]
            assert canary["mutation"] == "sign_flip"
            assert canary["mutant_comparison_pass"] is False
            assert canary["rejected"] is True
            positional = curve["positional_zip_component_order_canary"]
            assert positional["orders_are_distinct"] is True
            assert positional["Route_A_component_order"] != positional[
                "Route_C_component_order"
            ]
            assert set(positional["Route_A_component_order"]) == set(
                positional["Route_C_component_order"]
            )
            assert positional["positional_zip_mutant_comparison_pass"] is False
            assert positional["rejected"] is True


def test_comparisons_and_sector_additivity_recompute_from_raw_maps(
    receipt: dict,
) -> None:
    for member in receipt["scientific"]["members"]:
        for curve in member["curves"]:
            left = curve["Route_A_C2_AD_JVP"]
            right = curve[
                "Route_C_precision_stabilized_free_directional_estimate"
            ]
            assert gate.compare_component_maps(left, right) == curve["comparison"]
            assert gate.sector_additivity(left) == curve["sector_additivity"][
                "Route_A_C2_AD"
            ]
            assert gate.sector_additivity(right) == curve["sector_additivity"][
                "Route_C_precision_stabilized"
            ]


def test_joint_direction_reproduces_prior_pinned_receipt(receipt: dict) -> None:
    reproduction = receipt["scientific"][
        "joint_direction_reproduction_of_v5_6_6_6"
    ]
    assert reproduction["pass"] is True
    assert reproduction["pinned_fixed_contract_match"] is True
    assert reproduction["fixed_absolute_reproduction_tolerance"] == pytest.approx(
        gate.REPRODUCTION_ATOL, abs=0.0
    )
    assert [row["N"] for row in reproduction["records"]] == [1, 2, 3]
    for row in reproduction["records"]:
        assert row["pass"] is True
        assert row["lineage_and_quadrature_match"] is True
        assert row["Route_A_C2_AD_reproduction"]["pass"] is True
        assert row["Route_C_precision_stabilized_reproduction"]["pass"] is True


def test_joint_reproduction_recomputes_from_pinned_raw_maps(receipt: dict) -> None:
    pinned = json.loads(gate.THREE_WAY_ARTIFACT.read_text(encoding="utf-8"))
    recomputed = gate._joint_reproduction(receipt["scientific"]["members"], pinned)
    assert recomputed == receipt["scientific"][
        "joint_direction_reproduction_of_v5_6_6_6"
    ]


def test_all_source_pins_match_files(receipt: dict) -> None:
    expected = {
        "route_A_C2_source_sha256": (gate.C2_SOURCE, gate.C2_SOURCE_SHA256),
        "route_A_C2_test_sha256": (gate.C2_TEST, gate.C2_TEST_SHA256),
        "route_A_C2_artifact_sha256": (gate.C2_ARTIFACT, gate.C2_ARTIFACT_SHA256),
        "route_A_wrapper_source_sha256": (
            gate.ROUTE_A_WRAPPER_SOURCE,
            gate.ROUTE_A_WRAPPER_SOURCE_SHA256,
        ),
        "route_A_core_source_sha256": (gate.ROUTE_A_SOURCE, gate.ROUTE_A_SOURCE_SHA256),
        "route_C_precision_source_sha256": (
            gate.ROUTE_C_STABLE_SOURCE,
            gate.ROUTE_C_STABLE_SOURCE_SHA256,
        ),
        "route_C_precision_test_sha256": (
            gate.ROUTE_C_STABLE_TEST,
            gate.ROUTE_C_STABLE_TEST_SHA256,
        ),
        "route_C_precision_artifact_sha256": (
            gate.ROUTE_C_STABLE_ARTIFACT,
            gate.ROUTE_C_STABLE_ARTIFACT_SHA256,
        ),
        "route_C_base_source_sha256": (gate.ROUTE_C_SOURCE, gate.ROUTE_C_SOURCE_SHA256),
        "C2_primitive_bundle_sha256": (gate.BUNDLE, gate.BUNDLE_SHA256),
        "three_way_v5_6_6_6_source_sha256": (
            gate.THREE_WAY_SOURCE,
            gate.THREE_WAY_SOURCE_SHA256,
        ),
        "three_way_v5_6_6_6_test_sha256": (
            gate.THREE_WAY_TEST,
            gate.THREE_WAY_TEST_SHA256,
        ),
        "three_way_v5_6_6_6_artifact_sha256": (
            gate.THREE_WAY_ARTIFACT,
            gate.THREE_WAY_ARTIFACT_SHA256,
        ),
        "v5_6_6_15_source_sha256": (gate.V15_SOURCE, gate.V15_SOURCE_SHA256),
        "v5_6_6_15_test_sha256": (gate.V15_TEST, gate.V15_TEST_SHA256),
        "v5_6_6_15_artifact_sha256": (
            gate.V15_ARTIFACT,
            gate.V15_ARTIFACT_SHA256,
        ),
    }
    assert set(receipt["source_pins"]) == set(expected)
    for key, (path, pinned) in expected.items():
        assert receipt["source_pins"][key] == pinned
        assert _sha256(path) == pinned


def test_comparator_is_name_aligned_and_rejects_drift() -> None:
    assert gate.compare_component_maps(
        {"left": 1.0, "right": -2.0},
        {"right": -2.0, "left": 1.0},
    )["pass"] is True
    with pytest.raises(gate.FourDirectionCrossRouteError):
        gate.compare_component_maps({"left": 1.0}, {"right": 1.0})


def test_comparator_rejects_sign_flip_canary() -> None:
    left = {"a": 3.0, "b": 2.0, "S_total": 5.0}
    right = dict(left)
    result = gate.sign_flip_canary_rejected(left, right)
    assert result["mutated_component"] == "a"
    assert result["mutant_comparison_pass"] is False
    assert result["rejected"] is True


def test_positional_zip_canary_rejects_distinct_component_orders() -> None:
    left = {"a": 100.0, "b": -3.0, "c": 7.0}
    right = dict(left)
    result = gate.positional_zip_canary_rejected(
        left,
        right,
        ("a", "b", "c"),
        ("b", "a", "c"),
    )
    assert result["orders_are_distinct"] is True
    assert result["positional_zip_mutant_comparison_pass"] is False
    assert result["rejected"] is True


def test_comparator_rejects_nonfinite_and_component_drift() -> None:
    with pytest.raises(gate.FourDirectionCrossRouteError):
        gate.compare_component_maps({"a": float("nan")}, {"a": 1.0})
    with pytest.raises(gate.FourDirectionCrossRouteError):
        gate.compare_component_maps({"a": 1.0}, {"a": float("inf")})
    with pytest.raises(gate.FourDirectionCrossRouteError):
        gate.compare_component_maps({"a": 1.0, "b": 2.0}, {"a": 1.0})


def test_strict_reproduction_comparator_rejects_scientifically_tolerated_drift() -> None:
    assert gate.compare_component_maps({"a": 1.0}, {"a": 1.0 + 5.0e-9})[
        "pass"
    ] is True
    strict = gate.compare_reproduction_maps({"a": 1.0}, {"a": 1.0 + 5.0e-9})
    assert strict["pass"] is False
    assert strict["rows"]["a"]["pass"] is False


def test_route_c_metadata_validator_rejects_mutation() -> None:
    member = {"N": 2, "K": 2, "member_id": "member"}
    good = {
        "N": 2,
        "K": 2,
        "member_id": "member",
        "curve_name": gate.CURVE_NAMES[0],
        "tangential_order": gate.TANGENTIAL_ORDER,
        "radial_order": gate.RADIAL_ORDER,
        "free_step": gate.FREE_STEP,
    }
    assert gate.validate_route_c_record_metadata(
        good, member, gate.CURVE_NAMES[0]
    ) == good
    bad = dict(good)
    bad["radial_order"] = 11
    with pytest.raises(gate.FourDirectionCrossRouteError):
        gate.validate_route_c_record_metadata(bad, member, gate.CURVE_NAMES[0])


def test_sector_additivity_rejects_missing_or_nonfinite_component() -> None:
    values = {name: 0.0 for name in gate.EXPECTED_COMPONENT_NAMES}
    assert gate.sector_additivity(values)["pass"] is True
    missing = dict(values)
    missing.pop("GHY_plus")
    with pytest.raises(gate.FourDirectionCrossRouteError):
        gate.sector_additivity(missing)
    nonfinite = dict(values)
    nonfinite["EH_bulk_plus"] = float("inf")
    with pytest.raises(gate.FourDirectionCrossRouteError):
        gate.sector_additivity(nonfinite)


def test_upstream_monkeypatch_contexts_restore_after_exception() -> None:
    from first_principles_audit.prediction_factory import (
        derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5
        as stable,
    )
    from first_principles_audit.prediction_factory import (
        derive_one_omega_topological_so3_torch_c2_multin_v5_6_5_6 as c2,
    )

    class DummyRouteA:
        pass

    dummy = DummyRouteA()
    sentinel = object()
    dummy.radial_profile_evaluation = sentinel
    with pytest.raises(RuntimeError, match="profile canary"):
        with c2._profile_patch(dummy):
            assert dummy.radial_profile_evaluation is c2.c2_radial_profiles_torch
            raise RuntimeError("profile canary")
    assert dummy.radial_profile_evaluation is sentinel

    original_bulk_jet = stable.route_c._bulk_jet
    with pytest.raises(RuntimeError, match="bulk-jet canary"):
        with stable.stabilized_route_c_bulk_jet():
            assert stable.route_c._bulk_jet is stable.stable_bulk_jet
            raise RuntimeError("bulk-jet canary")
    assert stable.route_c._bulk_jet is original_bulk_jet


def test_evidence_boundary_does_not_promote_finite_agreement(receipt: dict) -> None:
    boundary = receipt["evidence_boundary"]
    assert "Twelve pinned finite comparisons" in boundary
    assert "does not prove" in boundary
    assert receipt["independence_boundary"]["symbolic_same_functional_identity_claimed"] is False
    assert receipt["independence_boundary"]["clean_room_process_claimed"] is False
    assert receipt["independence_boundary"][
        "tangential_quadrature_implementations_identical_claimed"
    ] is False
    assert receipt["independence_boundary"][
        "radial_quadrature_implementations_identical_claimed"
    ] is False
    assert set(receipt["open_obligations"]) == {
        "same_functional",
        "Route_C_bias",
        "continuum",
        "N_to_infinity",
    }
