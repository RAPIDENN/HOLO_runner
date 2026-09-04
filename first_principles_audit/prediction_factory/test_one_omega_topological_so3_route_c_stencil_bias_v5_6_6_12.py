from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_route_c_stencil_bias_v5_6_6_12 as gate,
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    assert gate.OUTPUT.exists()
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def test_import_graph_uses_only_the_precision_route() -> None:
    tree = ast.parse(Path(gate.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = ("torch", "literal_torch_action", "numpy_c2_multin_fd5")
    assert not any(any(token in name for token in forbidden) for name in imported)
    assert gate.PRECISION_SOURCE == gate.EXPECTED_PRECISION_SOURCE.resolve()
    assert gate.BASE_ROUTE_C_SOURCE == gate.EXPECTED_BASE_ROUTE_C_SOURCE.resolve()


def test_all_inputs_are_byte_pinned_and_upstream_gaps_stay_red() -> None:
    three_way, v56611 = gate._load_inputs()
    assert gate._sha256(gate.PRECISION_SOURCE) == gate.PRECISION_SOURCE_SHA256
    assert gate._sha256(gate.BASE_ROUTE_C_SOURCE) == gate.BASE_ROUTE_C_SOURCE_SHA256
    assert gate._sha256(gate.THREE_WAY_ARTIFACT) == gate.THREE_WAY_ARTIFACT_SHA256
    assert gate._sha256(gate.V56611_SOURCE) == gate.V56611_SOURCE_SHA256
    assert gate._sha256(gate.V56611_ARTIFACT) == gate.V56611_ARTIFACT_SHA256
    assert three_way["decision"]["AD_FD5_Route_C_three_way_comparison_pass"] is True
    assert v56611["decision"]["pinned_members_margins_everywhere_on_collar_pass"] is False


def test_extended_precision_and_radial_moments_are_exact() -> None:
    assert gate.np.finfo(gate.np.longdouble).eps < gate.np.finfo(gate.np.float64).eps
    certificate = gate._radial_stencil_moment_certificate()
    assert certificate["exact_rational_moments_through_degree_8_pass"] is True
    assert set(certificate["rows"]) == {"first", "second"}


def test_coordinate_step_context_restores_globals_even_on_error() -> None:
    original_theta = gate.precision.STABLE_THETA_STEP
    original_rho = gate.precision.STABLE_RHO_STEP
    with pytest.raises(RuntimeError):
        with gate.coordinate_stencil_steps(0.06, 0.015):
            assert float(gate.precision.STABLE_THETA_STEP) == pytest.approx(0.06)
            assert float(gate.precision.STABLE_RHO_STEP) == pytest.approx(0.015)
            raise RuntimeError("synthetic abort")
    assert gate.precision.STABLE_THETA_STEP is original_theta
    assert gate.precision.STABLE_RHO_STEP is original_rho
    with pytest.raises(gate.StencilBiasGateError):
        with gate.coordinate_stencil_steps(0.0, 0.03):
            pass


@pytest.mark.parametrize("formal_order", [4, 8])
def test_richardson_analysis_recovers_a_synthetic_power_law(
    formal_order: int,
) -> None:
    truth = 3.25
    coefficient = -7.0
    h = 0.1

    def value(step: float) -> dict[str, float]:
        return {"component": truth + coefficient * step**formal_order}

    result = gate._axis_analysis(
        value(2.0 * h), value(h), value(0.5 * h), formal_order=formal_order
    )
    row = result["rows"]["component"]
    assert row["contraction_ratio_coarse_gap_over_fine_gap"] == pytest.approx(
        2**formal_order, rel=1.0e-8
    )
    assert row["observed_order_log2_ratio"] == pytest.approx(formal_order, rel=1.0e-8)
    assert row["conditional_extrapolated_limit_from_coarse_pair"] == pytest.approx(
        truth, abs=1.0e-12
    )
    assert row["conditional_extrapolated_limit_from_fine_pair"] == pytest.approx(
        truth, abs=1.0e-12
    )
    assert result["asymptotic_window_observed_pass"] is True


def test_richardson_analysis_rejects_a_noncontractive_mutant() -> None:
    result = gate._axis_analysis(
        {"component": 2.0},
        {"component": 1.0},
        {"component": 0.0},
        formal_order=4,
    )
    assert result["rows"]["component"][
        "formal_order_supported_on_this_component"
    ] is False
    assert result["asymptotic_window_observed_pass"] is False
    assert result["contradicted_components"] == ["component"]


@pytest.mark.parametrize(
    ("formal_order", "mutant_order"), [(4, 2), (8, 4)]
)
def test_richardson_analysis_rejects_a_lower_order_mutant(
    formal_order: int, mutant_order: int
) -> None:
    truth = 3.25
    coefficient = 7.0
    h = 0.1

    def value(step: float) -> dict[str, float]:
        return {"component": truth + coefficient * step**mutant_order}

    result = gate._axis_analysis(
        value(2.0 * h), value(h), value(0.5 * h), formal_order=formal_order
    )
    row = result["rows"]["component"]
    assert row["assessed_above_resolution_floor"] is True
    assert row["observed_order_log2_ratio"] == pytest.approx(mutant_order)
    assert row["formal_order_supported_on_this_component"] is False
    assert row["Richardson_estimate_eligible"] is False
    assert row["conditional_production_bias_from_fine_pair"] is None
    assert result["asymptotic_window_observed_pass"] is False


def test_cube_mobius_decomposition_detects_interactions() -> None:
    cube = {
        "ppp": {"component": 0.0},
        "fpp": {"component": 1.0},
        "pfp": {"component": 2.0},
        "ppf": {"component": 4.0},
        "ffp": {"component": 1.0 + 2.0 + 0.5},
        "fpf": {"component": 1.0 + 4.0 - 0.25},
        "pff": {"component": 2.0 + 4.0 + 0.75},
        "fff": {"component": 1.0 + 2.0 + 4.0 + 0.5 - 0.25 + 0.75 + 0.125},
    }
    result = gate._cube_analysis(cube)
    row = result["rows"]["component"]
    assert row["two_axis_interactions"] == pytest.approx(
        {"free_theta": 0.5, "free_rho": -0.25, "theta_rho": 0.75}
    )
    assert row["three_axis_interaction"] == pytest.approx(0.125)
    assert row["algebraic_reconstruction_residual"] == pytest.approx(0.0)


def test_receipt_contains_all_members_ladders_and_full_cubes(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    members = receipt["scientific"]["members"]
    assert [(row["N"], row["K"]) for row in members] == list(gate.EXPECTED_MEMBERS)
    expected_components = set(gate.precision.route_c.ACTION_COMPONENTS) | {"S_total"}
    expected_points = {
        "baseline",
        "free_coarse",
        "free_fine",
        "theta_coarse",
        "theta_fine",
        "rho_coarse",
        "rho_fine",
        "free_theta_fine",
        "free_rho_fine",
        "theta_rho_fine",
        "all_fine",
    }
    for member in members:
        assert member["distinct_evaluation_count"] == gate.EXPECTED_DISTINCT_EVALUATIONS_PER_MEMBER
        assert set(member["evaluations"]) == expected_points
        assert set(member["axis_ladders"]) == {"free", "theta", "rho"}
        assert member["production_fine_cube"]["component_count"] == len(expected_components)
        assert member["production_fine_cube"][
            "maximum_algebraic_reconstruction_residual"
        ] < 1.0e-12
        estimate = member["conditional_axiswise_fixed_Q_stencil_estimate"]
        assert estimate["all_component_axes_eligible"] is False
        assert estimate["maximum_absolute_axiswise_signed_sum"] is None
        assert estimate["maximum_axiswise_absolute_sum"] is None
        for point in member["evaluations"].values():
            assert set(point["components"]) == expected_components


def test_finite_reference_checks_are_green_but_rigorous_claims_are_red(
    receipt: dict,
) -> None:
    decision = receipt["decision"]
    assert decision["stencil_step_ladders_measured_pass"] is True
    assert decision["production_fine_full_cube_measured_pass"] is True
    assert decision["production_route_C_reproduced_from_v5_6_6_6_pass"] is True
    assert decision["selected_member_fixed_Q_Torch_AD_crosscheck_pass"] is True
    true_keys = {
        "v5_6_6_11_stencil_description_correction_recorded",
        "stencil_step_ladders_measured_pass",
        "production_fine_full_cube_measured_pass",
        "selected_member_fixed_Q_production_to_all_fine_sensitivity_pass",
        "production_route_C_reproduced_from_v5_6_6_6_pass",
        "selected_member_fixed_Q_Torch_AD_crosscheck_pass",
        "radial_nine_point_moments_exact_through_degree_8_pass",
        "fixed_Q_stencil_Richardson_candidates_recorded_pass",
    }
    false_keys = {
        "free_FD5_asymptotic_window_observed_pass",
        "theta_stencil_asymptotic_window_observed_pass",
        "rho_stencil_asymptotic_window_observed_pass",
        "all_resolved_components_consistent_with_formal_orders_pass",
        "fixed_Q_stencil_Richardson_estimate_available_pass",
        "Q_h_limit_commutation_proved_pass",
        "B_FD_Q_to_infinity_estimate_pass",
        "B_FD_rigorous_bound_pass",
        "restricted_family_exact_action_identity_pass",
        "pinned_members_margins_everywhere_on_collar_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_stability_pass",
        "spectral_N_convergence_pass",
        "periodic_box_exhaustion_and_tail_control_pass",
        "density_union_C_N_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    }
    assert set(decision) == true_keys | false_keys
    assert all(decision[key] is True for key in true_keys)
    assert all(decision[key] is False for key in false_keys)


def test_fixed_Q_scope_and_extended_stencil_domain_are_explicit(receipt: dict) -> None:
    fixed = receipt["fixed_before_run"]
    assert fixed["fixed_quadrature"] == {
        "Qtheta": gate.TANGENTIAL_ORDER,
        "Qrho": gate.RADIAL_ORDER,
    }
    lower, upper = fixed["coarse_radial_stencil_reach_over_GL_nodes"]
    assert lower < 0.0 < 1.0 < upper
    assert "Q-to-infinity" in receipt["open_obligation"]["Q_h_limit_interchange"]
    assert receipt["provenance"]["workers"] == gate.DEFAULT_WORKERS


def test_artifact_is_canonical_and_provenance_is_current(receipt: dict) -> None:
    encoded = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert gate.OUTPUT.read_text(encoding="utf-8") == encoded
    assert receipt["scientific_payload_sha256"] == gate._canonical_sha256(
        receipt["scientific"]
    )
    assert receipt["provenance"]["generator"]["sha256"] == gate._sha256(
        Path(gate.__file__)
    )
    assert receipt["provenance"]["test"]["sha256"] == gate._sha256(Path(__file__))
