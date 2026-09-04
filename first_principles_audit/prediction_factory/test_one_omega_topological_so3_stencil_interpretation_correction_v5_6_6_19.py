"""Tests for the additive v5.6.6.19 stencil-interpretation correction."""

from __future__ import annotations

import ast
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_stencil_interpretation_correction_v5_6_6_19 as gate,
)


EXPECTED_TRUE_KEYS = frozenset(
    {
        "v5_6_6_12_artifact_byte_pinned_pass",
        "v5_6_6_13_artifact_byte_pinned_pass",
        "v12_measurements_reanalyzed_without_route_C_recomputation_pass",
        "v12_formal_order_not_supported_component_ledger_relabelled_pass",
        "FD5_formal_order_4_exact_arithmetic_p_minus_1_ladder_counterexample_pass",
        "selected_K_le_3_pullback_rho_degree_at_most_8_ledger_pass",
        "radial_nine_point_D1_D2_moments_exact_through_degree_8_pass",
        "pinned_pullback_radial_degree_preservation_static_source_audit_pass",
        "selected_K_le_3_qr_qrr_radial_stencil_exact_in_exact_arithmetic_pass",
        "selected_K_le_3_qtr_radial_leg_exact_in_exact_arithmetic_pass",
        "pinned_members_margins_everywhere_certified_pass",
        "extended_radial_continuation_oracle_gap_recorded_pass",
    }
)

EXPECTED_FALSE_KEYS = frozenset(
    {
        "free_FD5_roundoff_dominance_certified_pass",
        "free_FD5_rigorous_roundoff_bound_pass",
        "free_FD5_asymptotic_window_observed_pass",
        "theta_stencil_asymptotic_window_observed_pass",
        "rho_stencil_asymptotic_window_observed_pass",
        "all_assessed_components_support_formal_orders_pass",
        "fixed_Q_stencil_Richardson_estimate_available_pass",
        "selected_radial_density_action_or_quadrature_exactness_pass",
        "selected_K_le_3_full_qtr_stencil_exact_in_exact_arithmetic_pass",
        "restricted_K_le_8_family_radial_stencil_exactness_pass",
        "extended_radial_continuation_oracle_certified_pass",
        "pinned_members_margins_on_extended_radial_stencil_domain_pass",
        "v5_6_6_13_interval_rounding_enclosure_pass",
        "theta_coordinate_stencil_rigorous_bound_pass",
        "Q_h_limit_commutation_proved_pass",
        "B_FD_Q_to_infinity_estimate_pass",
        "B_FD_rigorous_bound_pass",
        "restricted_family_exact_action_identity_pass",
        "same_functional_symbolic_identity_pass",
        "density_union_C_N_pass",
        "spectral_N_convergence_pass",
        "periodic_box_exhaustion_and_tail_control_pass",
        "uniform_stability_pass",
        "uniform_N_to_infinity_bridge_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    }
)


def _receipt() -> dict:
    assert gate.OUTPUT.exists(), f"run {Path(gate.__file__).name} first"
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def test_generator_is_a_json_only_reanalysis_without_route_c_imports() -> None:
    source = Path(gate.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert not any("one_omega_topological_so3" in name for name in imported)
    assert not any(name in {"torch", "scipy", "sympy", "runpy", "importlib"} for name in imported)
    assert "recomputed_Route_C\": False" in source


def test_all_frozen_inputs_are_byte_pinned() -> None:
    v12, v13 = gate.load_inputs()
    expected = {
        gate.V12_SOURCE: gate.V12_SOURCE_SHA256,
        gate.V12_TEST: gate.V12_TEST_SHA256,
        gate.V12_ARTIFACT: gate.V12_ARTIFACT_SHA256,
        gate.V13_SOURCE: gate.V13_SOURCE_SHA256,
        gate.V13_TEST: gate.V13_TEST_SHA256,
        gate.V13_ARTIFACT: gate.V13_ARTIFACT_SHA256,
        gate.PRECISION_SOURCE: gate.PRECISION_SOURCE_SHA256,
    }
    assert all(gate._sha256(path) == sha256 for path, sha256 in expected.items())
    assert v12["schema"] == gate.V12_SCHEMA
    assert v13["schema"] == gate.V13_SCHEMA
    assert gate.V12_PRODUCER_COMMIT == "da7a8269286bdd228753dfa4d7a381516778e9d6"
    assert gate.V13_PRODUCER_COMMIT == "270f8d73e8708fe0acbd5eecee46d5ea44a1547b"


def test_negative_order_counterexample_is_exact_and_contains_no_roundoff() -> None:
    row = gate.fd5_negative_order_exact_counterexample()
    assert row["exact_arithmetic_no_roundoff"] is True
    assert row["negative_order_without_roundoff_pass"] is True
    assert Fraction(row["absolute_gap_ratio"]) == Fraction(1, 2)
    assert row["observed_power_exact"] == "-1"
    assert row["observed_order_log2_ratio"] == -1.0
    assert row["gap_signs_are_opposite"] is True
    assert row["exact_derivative_at_zero"] == "0"
    assert [Fraction(row[key]) for key in ("D_2h", "D_h", "D_h_over_2")] == [
        -1472,
        -2732,
        -212,
    ]
    moments = gate.fd5_moment_certificate()
    assert moments["exact_through_degree_4_pass"] is True
    assert moments["first_failure_degree"] == 5
    assert Fraction(moments["first_failure_moment"]) == -4


def test_noncontractive_row_is_not_promoted_to_roundoff_dominance() -> None:
    row = gate.classify_ladder_row(
        {
            "assessed_above_resolution_floor": True,
            "formal_order_supported_on_this_component": False,
            "observed_order_log2_ratio": -1.0,
            "same_leading_error_sign": False,
            "formal_order_window": [3.5, 4.5],
            "resolution_floor": 2.0e-10,
            "Richardson_estimate_eligible": False,
        }
    )
    assert row["roundoff_compatible"] is True
    assert row["roundoff_dominance_certified"] is False
    assert row["classification"] == "noncontractive_gap_pattern_roundoff_compatible_not_diagnostic"
    assert row["Richardson_estimate_eligible"] is False


def test_reclassification_is_lossless_for_the_pinned_ladders() -> None:
    v12, _v13 = gate.load_inputs()
    corrected = gate.reinterpret_ladders(v12)
    summary = corrected["summary"]
    assert summary["free"]["fixed_floor_assessed_counts"] == [3, 5, 2]
    assert summary["theta"]["fixed_floor_assessed_counts"] == [0, 0, 0]
    assert summary["rho"]["fixed_floor_assessed_counts"] == [0, 0, 0]
    for old, new in zip(v12["scientific"]["members"], corrected["members"]):
        for axis in gate.AXES:
            old_axis = old["axis_ladders"][axis]
            new_axis = new["axis_ladders_reinterpreted"][axis]
            assert new_axis["formal_order_not_supported_components"] == old_axis[
                "contradicted_components"
            ]
            for component, old_row in old_axis["rows"].items():
                new_row = new_axis["rows"][component]
                assert new_row["observed_order_log2_ratio"] == old_row[
                    "observed_order_log2_ratio"
                ]
                assert new_row["Richardson_estimate_eligible"] == old_row[
                    "Richardson_estimate_eligible"
                ]


def test_selected_radial_profiles_have_exact_degree_at_most_eight() -> None:
    certificate = gate.radial_profile_degree_certificate()
    assert certificate["selected_K_le_3_degree_le_8_pass"] is True
    assert certificate["degrees"] == {
        "h0": 5,
        "h1": 6,
        "b0": 6,
        "b1": 7,
        "b2": 8,
    }
    rho = np.linspace(0.0, 1.0, 31)
    h0 = np.array([float(Fraction(value)) for value in certificate["exact_fraction_coefficients"]["h0"]])
    h1 = np.array([float(Fraction(value)) for value in certificate["exact_fraction_coefficients"]["h1"]])
    direct_h0 = 1 - 10 * rho**3 + 15 * rho**4 - 6 * rho**5
    assert np.allclose(np.polynomial.polynomial.polyval(rho, h0), direct_h0)
    assert np.allclose(np.polynomial.polynomial.polyval(rho, h1), rho * direct_h0)
    beyond = certificate["same_profile_formula_beyond_selected_campaign"]
    assert beyond == {
        "b3_degree_if_K_at_least_4": 9,
        "b7_degree_if_K_equals_8": 13,
        "K_le_8_degree_le_8": False,
    }


def test_nine_point_moments_are_exact_only_in_the_claimed_range() -> None:
    certificate = gate.radial_stencil_moment_certificate()
    assert certificate["D1_and_D2_exact_through_selected_degree_8_pass"] is True
    d1 = certificate["rows"]["D1"]
    d2 = certificate["rows"]["D2"]
    assert d1["first_failure_degree"] == 9
    assert Fraction(d1["first_failure_moment"]) == -576
    assert d2["first_failure_degree"] == 10
    assert Fraction(d2["first_failure_moment"]) == -1152
    assert 9 not in d1["exact_degrees"]
    assert 10 not in d2["exact_degrees"]


def test_source_audit_stops_before_nonlinear_densities() -> None:
    audit = gate.pinned_pullback_radial_structure_static_audit()
    assert audit["pass"] is True
    assert audit["abstract_degree_propagation"]["maximum_pulled_field_channel_rho_degree"] == 8
    assert "not a symbolic audit" in audit["scope"]
    receipt = _receipt()
    exactness = receipt["scientific"]["radial_field_channel_exactness"]
    assert exactness["D1_qr_field_channel_truncation_zero_in_exact_arithmetic"] is True
    assert exactness["D2_qrr_field_channel_truncation_zero_in_exact_arithmetic"] is True
    assert exactness["qtr_radial_D1_leg_truncation_zero_in_exact_arithmetic"] is True
    assert exactness["qtr_theta_leg_exact"] is False
    assert exactness["nonlinear_density_action_or_quadrature_exact"] is False


def test_radial_reach_exposes_the_exterior_semantics_gap() -> None:
    ledger = gate.radial_stencil_reach_ledger()
    assert ledger["semantics_match_outside_collar"] is False
    for row in ledger["rows"].values():
        lower, upper = row["bulk_GL10_reach"]
        assert lower < 0.0 < 1.0 < upper
        ghy_lower, ghy_upper = row["GHY_rho0_reach"]
        assert ghy_lower < 0.0 < ghy_upper


def test_v13_margin_scope_does_not_cover_the_extended_stencil_domain() -> None:
    _v12, v13 = gate.load_inputs()
    scope = gate.v13_margin_scope_audit(v13)
    assert scope["pinned_members_margins_everywhere_certified_pass"] is True
    assert scope["certified_rho_domain"] == [0.0, 1.0]
    assert scope["domain_source_fragments_present_pass"] is True
    assert scope["extended_radial_stencil_reach_certified"] is False
    assert scope["interval_rounding_enclosure_pass"] is False
    assert "not interval arithmetic" in scope["rounding_scope"]


def test_decision_allowlist_is_closed_and_promotions_remain_false() -> None:
    decision = _receipt()["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    assert all(decision[key] is True for key in EXPECTED_TRUE_KEYS)
    assert all(decision[key] is False for key in EXPECTED_FALSE_KEYS)


def test_receipt_is_canonical_and_provenance_is_current() -> None:
    receipt = _receipt()
    encoded = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert gate.OUTPUT.read_text(encoding="utf-8") == encoded
    assert receipt["schema"] == gate.SCHEMA
    assert receipt["scientific_payload_sha256"] == gate._canonical_sha256(
        receipt["scientific"]
    )
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(
        Path(gate.__file__)
    )
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
    assert receipt["provenance"]["recomputed_Route_C"] is False
