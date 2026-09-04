"""Tests for the v5.6.6.15 Route C same-functional pointwise gate."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

import derive_one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15 as gate

EXPECTED_TRUE_KEYS = frozenset(
    {
        "route_c_sector_list_is_literal_action_term_list_pass",
        "route_c_bulk_and_ghy_densities_equal_pinned_literal_implementation_pointwise_pass",
        "route_c_interface_densities_equal_pinned_literal_implementation_pointwise_pass",
        "route_c_closed_form_coefficients_match_literal_formula_strings_pass",
    }
)
EXPECTED_FALSE_KEYS = frozenset(
    {
        "same_functional_symbolic_identity_pass",
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
ALL_COMPONENTS = (
    [f"{s}_bulk_{side}" for side in gate.SIDES for s in gate.BULK_SECTORS]
    + [f"GHY_{side}" for side in gate.SIDES]
    + list(gate.BRANE_SECTORS)
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    if not gate.OUTPUT.exists():
        pytest.fail(f"missing receipt {gate.OUTPUT.name}; run the derive first")
    return json.loads(gate.OUTPUT.read_text())


@pytest.fixture(scope="session")
def routes() -> tuple:
    return gate.load_routes()


def _canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def test_generator_imports_exactly_the_two_pinned_routes() -> None:
    source = Path(gate.__file__).read_text()
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    assert not any("one_omega_topological_so3" in name for name in names)
    assert not any(name in {"torch", "scipy", "runpy"} for name in names)
    # exactly one dynamic loader, used for the two byte-pinned routes
    assert source.count("spec_from_file_location") == 1
    assert source.count("_load_pinned_module(") == 3  # definition + two calls
    for forbidden in ("three_way", "torch_action_route_a", "v5_6_6_12"):
        assert forbidden not in source, forbidden


def test_schema_and_pins(receipt: dict) -> None:
    assert receipt["schema"] == gate.SCHEMA
    pins = receipt["source_pins"]
    assert pins["literal_v5_2_action_sha256"] == gate.LITERAL_V5_2_ACTION_SHA256
    assert pins["C2_multi_N_primitive_bundle_sha256"] == gate.BUNDLE_SHA256 == gate._sha256(gate.BUNDLE_PATH)
    assert pins["route_c_v5_6_6_3_derive_sha256"] == gate.ROUTE_C_SHA256 == gate._sha256(gate.ROUTE_C_PATH)
    assert pins["route_b_v5_6_5_certificate_derive_sha256"] == gate.ROUTE_B_SHA256 == gate._sha256(gate.ROUTE_B_PATH)
    assert pins["v5_6_6_11_receipt_sha256"] == gate.V56611_SHA256 == gate._sha256(gate.V56611_PATH)
    assert receipt["scientific_payload_sha256"] == _canonical_sha256(receipt["scientific"])
    bundle = gate.load_bundle()
    assert pins["coefficient_parameters_sha256"] == bundle["action_contract"]["coefficient_parameters_sha256"]


def test_decision_keys_are_exactly_as_expected(receipt: dict) -> None:
    decision = receipt["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key


def test_every_component_compared_within_tolerance(receipt: dict) -> None:
    fixed = receipt["fixed_before_run"]
    block_a = receipt["scientific"]["block_A_bulk_and_GHY_pointwise"]
    block_b = receipt["scientific"]["block_B_interface_pointwise"]
    rows = {**block_a["sectors"], **block_b["sectors"]}
    assert set(rows) == set(ALL_COMPONENTS)
    for name in ALL_COMPONENTS:
        row = rows[name]
        assert row["samples"] >= 12, name
        assert row["max_relative_difference"] <= fixed["relative_tolerance"], name
        assert row["max_abs_value"] > 1.0e-3, f"{name}: comparison would be vacuous"
    assert block_a["worst_relative_difference"] <= fixed["relative_tolerance"]
    assert block_b["worst_relative_difference"] <= fixed["relative_tolerance"]
    assert block_a["route_c_reference_leak_outside_Omega_potential_max_abs"] <= 1.0e-9
    assert block_a["samples_per_side"] == fixed["bulk_samples_per_side"]
    assert block_b["samples"] == fixed["interface_samples"]


def test_samples_stayed_inside_the_declared_margins(receipt: dict) -> None:
    margins = receipt["fixed_before_run"]["margins"]
    a = receipt["scientific"]["block_A_bulk_and_GHY_pointwise"]["margins_observed"]
    b = receipt["scientific"]["block_B_interface_pointwise"]["margins_observed"]
    assert a["signature_bulk_min"] >= margins["signature_eigenvalue"]
    assert a["signature_induced_min"] >= margins["signature_eigenvalue"]
    assert a["omega_min"] >= margins["omega"]
    assert b["signature_common_min"] >= margins["signature_eigenvalue"]
    assert b["khronon_norm_max"] <= -margins["khronon"]
    assert b["rotation_norm_max"] <= math.pi - margins["rotation_cut_locus"]
    assert b["omega_min"] >= margins["omega"]


def test_closed_form_transcription_and_bijection(receipt: dict) -> None:
    c = receipt["scientific"]["block_C_closed_form_literal_transcription"]
    assert c["worst"] <= receipt["fixed_before_run"]["closed_form_tolerance"]
    checks = c["checks_max_relative_difference"]
    for key in (
        "Omega_potential_vs_literal_U_W",
        "full_V4_vs_literal_V4",
        "wall_vs_literal_W_beta",
        "Robin_static_flat_vs_literal",
        "BF_pairing_minus_half_trace_equals_dot",
        "BF_top_coefficient_vs_full_permutation_sum_over_3!2!",
    ):
        assert key in checks
    for key in c["literal_strings_used"]:
        assert c["literal_strings_used"][key]
    assert "NO extra factorial" in c["BF_normalisation_note"]
    bijection = receipt["scientific"]["sector_term_bijection"]
    assert bijection["pass"] is True
    assert bijection["route_c_action_components"] == ALL_COMPONENTS
    assert bijection["removed_terms_declared"].startswith("S_X=0")


def test_hypothesis_of_v5_6_6_11_is_the_one_discharged(receipt: dict) -> None:
    text = receipt["scientific"]["hypothesis_discharged_from_v5_6_6_11"]
    assert text is not None and "same functional" in text and "sector names" in text


def test_boundaries_are_fail_closed(receipt: dict) -> None:
    assert "not a symbolic identity" in receipt["evidence_boundary"].lower()
    assert "B_FD" in " ".join(receipt["open_obligation"])
    assert receipt["independence_boundary"]["no_finite_differences"] is True
    assert receipt["independence_boundary"]["no_route_c_pipeline_run"] is True
    assert "B_FD" in " ".join(receipt["scientific"]["what_is_not_established"])


def test_fresh_bulk_sample_with_another_seed_agrees(routes: tuple) -> None:
    """Reproduce block A on one fresh configuration per side with a seed the receipt did not use."""
    route_c, route_b = routes
    bundle = gate.load_bundle()
    parameters = bundle["action_contract"]["coefficient_parameters"]
    rng = np.random.default_rng(gate.SEED + 1000)
    pairs = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5)
    triples = tuple(tuple(int(x) for x in t) for t in route_c.B_TRIPLES)
    original = route_b.decode_bulk_state
    try:
        for side in gate.SIDES:
            theta0 = float(rng.uniform(0.0, 2.0 * math.pi))
            rho0 = float(rng.uniform(0.05, 0.95))
            configuration = gate.local_configuration(rng, pairs, theta0, rho0, side)
            state = gate.route_b_state(configuration, pairs, side, theta0, rho0, route_b)
            jet = gate.route_c_jet(configuration, pairs, triples, side, theta0, rho0)
            c_bulk = route_c._bulk_density(jet, parameters)
            b_bulk = route_b.bulk_action_components(state, np.asarray([1.0]), np.asarray([1.0]), parameters, side)
            for sector in gate.BULK_SECTORS:
                left, right = float(c_bulk[sector]), float(b_bulk[f"{sector}_bulk_{side}"])
                assert abs(left - right) <= gate.RELATIVE_TOLERANCE * max(1.0, abs(left), abs(right)), (side, sector, left, right)
            # BF must be nonzero and orientation-sensitive: flipping collar_sign on Route B flips its sign
            flipped = dict(state)
            flipped["collar_sign"] = np.asarray(-int(state["collar_sign"]))
            b_flipped = route_b.bulk_action_components(flipped, np.asarray([1.0]), np.asarray([1.0]), parameters, side)
            assert abs(b_bulk[f"BF_bulk_{side}"]) > 1.0e-6
            assert math.isclose(b_flipped[f"BF_bulk_{side}"], -b_bulk[f"BF_bulk_{side}"], rel_tol=1.0e-12)
            configuration0 = gate.local_configuration(rng, pairs, theta0, 0.0, side)
            state0 = gate.route_b_state(configuration0, pairs, side, theta0, 0.0, route_b)
            jet0 = gate.route_c_jet(configuration0, pairs, triples, side, theta0, 0.0)
            route_b.decode_bulk_state = lambda *args, _state=state0, **kwargs: _state
            b_ghy = route_b.ghy_component(None, None, None, 1, np.asarray([1.0]), parameters, side, 1, 1)
            route_b.decode_bulk_state = original
            c_ghy = route_c._ghy_density(jet0, parameters)
            assert abs(c_ghy - b_ghy) <= gate.RELATIVE_TOLERANCE * max(1.0, abs(c_ghy), abs(b_ghy)), (side, c_ghy, b_ghy)
    finally:
        route_b.decode_bulk_state = original


def test_mutant_detection_the_comparison_is_not_vacuous(routes: tuple) -> None:
    """A wrong coefficient in one sector is detected by the same comparison."""
    route_c, route_b = routes
    bundle = gate.load_bundle()
    parameters = dict(bundle["action_contract"]["coefficient_parameters"])
    rng = np.random.default_rng(gate.SEED + 2000)
    pairs = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5)
    triples = tuple(tuple(int(x) for x in t) for t in route_c.B_TRIPLES)
    theta0, rho0 = 1.3, 0.4
    configuration = gate.local_configuration(rng, pairs, theta0, rho0, "plus")
    state = gate.route_b_state(configuration, pairs, "plus", theta0, rho0, route_b)
    jet = gate.route_c_jet(configuration, pairs, triples, "plus", theta0, rho0)
    mutant = dict(parameters)
    mutant["compensator_metric_G"] = parameters["compensator_metric_G"] * (1.0 + 1.0e-6)
    c_bulk = route_c._bulk_density(jet, mutant)
    b_bulk = route_b.bulk_action_components(state, np.asarray([1.0]), np.asarray([1.0]), parameters, "plus")
    left, right = float(c_bulk["Omega_kinetic"]), float(b_bulk["Omega_kinetic_bulk_plus"])
    assert abs(left - right) > gate.RELATIVE_TOLERANCE * max(1.0, abs(left), abs(right))
