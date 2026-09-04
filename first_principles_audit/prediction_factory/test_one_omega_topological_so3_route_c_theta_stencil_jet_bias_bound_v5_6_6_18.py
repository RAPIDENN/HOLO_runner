"""Tests for the v5.6.6.18 theta-stencil jet bias bound gate."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

import derive_one_omega_topological_so3_route_c_theta_stencil_jet_bias_bound_v5_6_6_18 as gate

EXPECTED_TRUE_KEYS = frozenset(
    {
        "route_c_ideal_rational_theta_stencil_moment_identities_pass",
        "route_c_jet_pipeline_entire_static_lexical_audit_pass",
        "rodrigues_small_angle_branch_inactive_grid_lipschitz_float_screen_pass",
        "route_c_ideal_rational_theta_stencil_taylor_cauchy_bound_formula_pass",
        "route_c_production_coarse_fine_jet_difference_within_candidate_envelope_plus_allowance_sampled_pass",
        "route_c_production_rounding_gap_canary_observed_pass",
    }
)
EXPECTED_FALSE_KEYS = frozenset(
    {
        "route_c_ideal_rational_theta_stencil_numeric_enclosure_certified_pass",
        "route_c_jet_pipeline_transitive_entire_callgraph_certificate_pass",
        "route_c_full_component_node_candidate_envelope_ledger_serialized_pass",
        "route_c_radial_entries_match_declared_zero_extension_semantics_pass",
        "route_c_production_jet_total_error_bound_pass",
        "route_c_theta_stencil_density_bias_bound_pass",
        "B_FD_rigorous_bound_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_stability_pass",
        "spectral_N_convergence_pass",
        "restricted_family_exact_action_identity_pass",
        "periodic_box_exhaustion_and_tail_control_pass",
        "density_union_C_N_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    }
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    if not gate.OUTPUT.exists():
        pytest.fail(f"missing receipt {gate.OUTPUT.name}; run the derive first")
    return json.loads(gate.OUTPUT.read_text())


@pytest.fixture(scope="session")
def modules() -> tuple:
    return gate.load_precision()


@pytest.fixture(scope="session")
def rebuilt_payload() -> dict:
    return gate.build_payload()


def _canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def test_generator_imports_only_the_pinned_precision_route() -> None:
    source = Path(gate.__file__).read_text()
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
            names += [alias.name for alias in node.names]
    dynamic = [name for name in names if "one_omega_topological_so3" in name]
    assert dynamic == ["derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5"]
    assert not any(name in {"torch", "scipy", "sympy", "runpy"} for name in names)
    assert "spec_from_file_location" not in source
    for forbidden in ("_bulk_density", "_brane_density", "_ghy_density", "evaluate_direct_member", "v5_6_6_17", "v5_6_6_19"):
        assert forbidden not in source, forbidden


def test_schema_pins_and_keys(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["precision_route_c_v5_6_6_5_derive_sha256"] == gate.PRECISION_SHA256 == gate._sha256(gate.PRECISION_PATH)
    assert pins["route_c_v5_6_6_3_derive_sha256"] == gate.ROUTE_C_SHA256 == gate._sha256(gate.ROUTE_C_PATH)
    assert pins["v5_6_6_12_receipt_sha256"] == gate.V56612_SHA256 == gate._sha256(gate.V56612_PATH)
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key


def test_receipt_scientific_payload_and_decisions_match_a_fresh_build(receipt: dict, rebuilt_payload: dict) -> None:
    # Normalize tuples emitted by the in-memory optimizer to their JSON list representation.
    rebuilt_scientific = json.loads(json.dumps(rebuilt_payload["scientific"], allow_nan=False))
    assert rebuilt_scientific == receipt["scientific"]
    assert rebuilt_payload["decision"] == receipt["decision"]
    assert rebuilt_payload["scientific_payload_sha256"] == receipt["scientific_payload_sha256"]


def test_stencil_certificate_is_exact_rational(receipt: dict) -> None:
    cert = receipt["scientific"]["stencil_certificate"]
    assert cert["pass"] is True
    first = [Fraction(x) for x in cert["first_moments_0_to_10"]]
    second = [Fraction(x) for x in cert["second_moments_0_to_10"]]
    assert first[1] == 1 and all(first[m] == 0 for m in range(9) if m != 1) and first[9] == Fraction(-1, 630) and first[10] == 0
    assert second[2] == 1 and all(second[m] == 0 for m in range(10) if m != 2) and second[10] == Fraction(-1, 3150)
    assert Fraction(cert["remainder_constants"]["C1_first_order9"]) > 0
    assert Fraction(cert["remainder_constants"]["C2_second_order10"]) > 0
    production = cert["production_longdouble_weight_zero_moment_residuals"]
    assert np.longdouble(production["first_m0"]) != 0
    assert np.longdouble(production["second_m0"]) != 0
    assert np.longdouble(production["second_m0_over_h_squared"]) != 0


def test_inventory_and_branch(receipt: dict) -> None:
    inventory = receipt["scientific"]["pipeline_inventory"]
    assert inventory["pass"] is True
    assert inventory["scope"] == "nontransitive_static_lexical_audit"
    assert inventory["function_count"] == len(gate.JET_FUNCTIONS) == 13
    assert inventory["basis_transcendentals_allowlisted"] is True
    assert set(inventory["functions"]) == set(gate.JET_FUNCTIONS)
    for name, row in inventory["functions"].items():
        assert row["forbidden_hits"] == [], name
    assert inventory["functions"]["_so3_exp_ld"]["small_angle_branch"] is True
    assert "or True" not in Path(gate.__file__).read_text()
    assert receipt["decision"]["route_c_jet_pipeline_transitive_entire_callgraph_certificate_pass"] is False
    for member in receipt["scientific"]["members"].values():
        branch = member["rodrigues_branch"]
        assert branch["pass"] is True
        assert "without_directed_rounding" in branch["scope"]
        for row in branch["rows"].values():
            assert row["grid_lipschitz_lower_screen"] >= receipt["fixed_before_run"]["branch_minimum_margin"] > 1.0e3 * row["branch_threshold"]


def test_serialized_candidate_envelope_scope_is_finite_and_explicitly_partial(receipt: dict) -> None:
    accounting = receipt["scientific"]["candidate_envelope_accounting"]
    assert accounting["component_entry_node_side_member_values_computed"] == 31_284
    assert accounting["full_component_ledger_serialized"] is False
    assert receipt["decision"]["route_c_full_component_node_candidate_envelope_ledger_serialized_pass"] is False
    for member in receipt["scientific"]["members"].values():
        for side in gate.SIDES:
            summary = member["jet_truncation_candidate_envelopes"][side]
            assert len(summary["per_node_max_over_components"]) == 11  # rho = 0 plus ten Gauss-Legendre nodes
            worst = summary["worst_node_component_candidate_envelope"]
            for entry in gate.JET_ENTRIES:
                values = np.asarray(worst[entry])
                assert values.shape == (79,)
                assert np.all(np.isfinite(values)) and np.all(values >= 0.0)
            # radial-only entries: zero outside the six A_trace components 19..24
            for entry in ("q", "qr", "qrr"):
                values = np.asarray(worst[entry])
                assert np.all(values[:19] == 0.0) and np.all(values[25:] == 0.0)
            # theta entries: nonnegative everywhere, strictly positive wherever the channel has content
            # (a free-data block that is identically zero yields a zero strip bound, which is correct)
            for entry in ("qt", "qtt", "qtr"):
                values = np.asarray(worst[entry])
                assert np.all(values >= 0.0) and np.max(values) > 0.0
                # the metric and the pulled-back reference always have content on their diagonal components;
                # off-diagonal or constant-only channels may legitimately get a zero bound
                assert np.max(values[:15]) > 0.0 and np.max(values[64:79]) > 0.0


def test_bounds_are_small_but_not_vacuous(receipt: dict) -> None:
    overall = receipt["scientific"]["overall_max_candidate_envelope"]
    assert overall["qt"] < 1.0e-3 and overall["qtt"] < 1.0e-2 and overall["qtr"] < 1.0e-2
    assert overall["qt"] > 1.0e-14  # a bound of zero would be a bug, not a theorem


def test_contrast_within_bound(receipt: dict) -> None:
    for member in receipt["scientific"]["members"].values():
        contrast = member["contrast"]
        assert contrast["pass"] is True
        assert contrast["worst_difference_over_candidate_plus_allowance"] <= 1.0
        assert len(contrast["points"]) == 2 * receipt["fixed_before_run"]["contrast_points_per_side"]


def test_boundaries(receipt: dict) -> None:
    assert receipt["decision"]["route_c_theta_stencil_density_bias_bound_pass"] is False
    assert receipt["decision"]["route_c_ideal_rational_theta_stencil_numeric_enclosure_certified_pass"] is False
    assert receipt["decision"]["route_c_production_jet_total_error_bound_pass"] is False
    assert receipt["decision"]["route_c_radial_entries_match_declared_zero_extension_semantics_pass"] is False
    assert "production_total_error_uncertified" in receipt["classification"]
    assert "rigorous_jet_level_stencil_bound" not in receipt["classification"]
    boundary_text = receipt["evidence_boundary"] + " " + " ".join(receipt["scientific"]["what_is_not_established"])
    for token in ("rounding", "non-transitive", "zero extension"):
        assert token in boundary_text
    assert "Lipschitz" in " ".join(receipt["open_obligation"])
    assert "free" in " ".join(receipt["scientific"]["what_is_not_established"]).lower()
    assert receipt["independence_boundary"]["no_density_evaluated"] is True


def test_n3_rho0_logomega_qrr_exposes_unbounded_production_rounding(
    receipt: dict, modules: tuple
) -> None:
    precision, route_c = modules
    bundle = route_c.load_bundle()
    member = next(row for row in bundle["primary_members"] if int(row["N"]) == 3)
    N, K = int(member["N"]), int(member["K"])
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    free = route_c._decode_f64(member["authoritative_free_central_f64le"])
    cert = gate.stencil_certificate(precision)

    profiles = gate._radial_profiles(0.0, K)
    assert profiles["h0"][2] == 0.0
    assert profiles["h1"][2] == 0.0
    assert np.all(profiles["bumps"][2] == 0.0)

    for side in gate.SIDES:
        ideal_candidate = gate.jet_bound_ledger(
            route_c,
            gate.member_side_bounds(route_c, free, contract, side),
            0.0,
            K,
            float(precision.STABLE_THETA_STEP),
            cert["_C1"],
            cert["_C2"],
            cert["_sum_abs_first"],
        )["bounds"]["qrr"][15]
        produced = np.longdouble(
            precision.stable_bulk_jet(free, contract, side, theta=0.731, rho=0.0)["qrr"][15]
        )
        assert ideal_candidate == 0.0
        assert np.isfinite(produced)
        assert abs(produced) > ideal_candidate

    serialized = receipt["scientific"]["production_rounding_gap_canary"]
    assert serialized["pass"] is True
    assert receipt["decision"]["route_c_production_rounding_gap_canary_observed_pass"] is True


def test_cauchy_bound_holds_on_a_fresh_scalar_check(modules: tuple) -> None:
    """Sanity of the remainder form: the nine-point stencil error on exp(hat r(theta)) entries at a fresh point
    against a finer numerical reference is below the candidate formula plus a small float allowance."""
    precision, route_c = modules
    rng = np.random.default_rng(gate.SEED + 7)
    coefficients = rng.uniform(-0.3, 0.3, size=(3, 3))  # modes 1, cos, sin
    h = float(precision.STABLE_THETA_STEP)
    theta = float(rng.uniform(0.0, 2.0 * math.pi))
    first = {int(k): float(v) for k, v in precision.FIRST_WEIGHTS.items()}

    def rotation(t: float) -> np.ndarray:
        return np.asarray(precision._so3_exp_ld(precision._series_ld(coefficients, precision.LD(t))), dtype=float)

    stencil = sum(w * rotation(theta + j * h) for j, w in first.items()) / h
    fine_h = 1.0e-3
    fine_reference = sum(w * rotation(theta + j * fine_h) for j, w in first.items()) / fine_h
    error = float(np.max(np.abs(stencil - fine_reference)))
    b0, b1 = gate._series_bounds(coefficients)
    C1 = float(Fraction(gate.stencil_certificate(precision)["remainder_constants"]["C1_first_order9"]))
    best = min(h**8 * C1 * math.factorial(9) * gate._rotation_strip_bound(b0, b1, s) / s**9 for s in gate.SIGMA_GRID)
    assert error <= best * (1.0 + (fine_h / h) ** 8) + 1.0e-14
    assert error > 0.0
