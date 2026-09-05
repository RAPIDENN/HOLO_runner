"""Tests for the fail-closed v5.6.7.1 TaylorDual3 local-density unit."""

from __future__ import annotations

import inspect
import math
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
import pytest
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derive_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1 as unit
import derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3 as route_c
import export_one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitives as pointwise


TRUE_KEYS = frozenset(
    {
        "taylor_dual3_independent_eta_spatial_degree_three_algebra_pass",
        "taylor_dual3_analytic_identities_sampled_within_tolerance_pass",
        "so3_entire_z_origin_regular_orthogonality_and_eta_jvp_sampled_pass",
        "full_t4_decoder_implemented_and_sampled_against_pinned_oracles_pass",
        "local_bulk_density_values_and_eta_jvps_sampled_N1_N3_against_pinned_torch_pass",
        "local_ghy_density_values_and_eta_jvps_sampled_N1_N3_against_pinned_torch_pass",
        "local_interface_density_values_and_eta_jvps_sampled_N1_N3_against_pinned_torch_pass",
        "twenty_separate_local_density_values_and_eta_jvps_sampled_pass",
        "finite_full_t4_rho_quadrature_rules_and_alias_canaries_sampled_pass",
        "finite_integrated_twenty_components_S_total_and_eta_jvp_same_grid_pinned_torch_sampled_pass",
    }
)
FALSE_KEYS = frozenset(
    {
        "integrated_action_pass",
        "quadrature_pass",
        "margins_certified_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_N_to_infinity_numerical_certificate_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    }
)


@pytest.fixture(scope="session")
def report() -> dict:
    return unit.build_report()


@pytest.fixture(scope="session")
def c2_bundle() -> dict:
    return route_c.load_bundle()


def _member_vectors(bundle: dict, N: int) -> tuple[dict, dict, np.ndarray, np.ndarray]:
    member = next(item for item in bundle["primary_members"] if int(item["N"]) == N)
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    free = route_c._decode_f64(member["authoritative_free_central_f64le"])
    curve = next(
        item
        for item in member["curves"]
        if item["name"] == "joint_all_primitive_classes_control_candidate"
    )
    tangent = route_c._decode_f64(curve["authoritative_free_tangent_f64le"])
    return member, contract, free, tangent


def _td3_layer(value, eta_order: int = 0) -> np.ndarray:
    array = np.asarray(value, dtype=object)
    return np.asarray(
        [entry.derivative(unit.ZERO_ALPHA, eta_order) for entry in array.flat],
        dtype=float,
    ).reshape(array.shape)


def _pointwise_side_x64(side: dict, point_index: int) -> np.ndarray:
    metric = np.asarray(side["g_trace"][point_index], dtype=float)
    return np.concatenate(
        (
            [metric[i, j] for i, j in unit.SYMMETRIC5],
            [side["log_Omega_trace"][point_index]],
            np.asarray(side["phi_trace"][point_index]).reshape(3),
            np.asarray(side["A_trace_full"][point_index]).reshape(15),
            np.asarray(side["B_trace_full"][point_index]).reshape(30),
        )
    )


def _numeric_skew(vector: np.ndarray) -> np.ndarray:
    a, b, c = vector
    return np.asarray(((0.0, -c, b), (c, 0.0, -a), (-b, a, 0.0)))


def _numeric_so3(vector: np.ndarray) -> np.ndarray:
    theta = float(np.linalg.norm(vector))
    generator = _numeric_skew(vector)
    if theta == 0.0:
        return np.eye(3)
    return np.eye(3) + math.sin(theta) / theta * generator + (
        (1.0 - math.cos(theta)) / theta**2
    ) * (generator @ generator)


def _bodies(matrix) -> np.ndarray:
    return np.asarray([[matrix[i][j].body for j in range(3)] for i in range(3)])


def _sympy_derivative(expression, x, eta, alpha, eta_order):
    result = expression
    for axis, order in enumerate(alpha):
        result = sp.diff(result, x[axis], order)
    result = sp.diff(result, eta, eta_order)
    return float(result.subs({**{symbol: 0 for symbol in x}, eta: 0}))


def test_upstream_source_is_byte_pinned_and_loaded_without_running_report() -> None:
    assert unit._sha256(unit.UPSTREAM_PATH) == unit.UPSTREAM_SHA256
    upstream = unit._load_pinned_upstream()
    assert upstream.SCHEMA == unit.UPSTREAM_SCHEMA
    assert upstream.N_MAX_CHECK == 11


def test_report_has_only_ten_true_scoped_decisions(report: dict) -> None:
    assert report["schema"] == unit.SCHEMA
    assert set(report["decision"]) == TRUE_KEYS | FALSE_KEYS
    assert {key for key, value in report["decision"].items() if value} == TRUE_KEYS
    assert {key for key, value in report["decision"].items() if not value} == FALSE_KEYS
    assert "sampled float64" in report["scope"]
    assert "sampled against byte-pinned decoder oracles only at N=1,2,3" in report["scope"]
    assert "twelve relative bulk, two GHY and six shared-interface" in report["scope"]
    assert "no pointwise S_total is formed" in report["scope"]
    assert "the rule is full T4 but the sampled action does not activate x2 or x3" in report["scope"]
    assert "Generic integrated_action_pass and quadrature_pass remain false" in report["scope"]
    assert "No receipt" in report["scope"]


def test_algebra_has_35_spatial_monomials_and_two_independent_layers(report: dict) -> None:
    assert len(unit.ALL_MULTIINDICES) == 35
    assert report["algebra"]["spatial_monomial_count"] == 35
    assert report["algebra"]["algebra_coefficient_capacity"] == 70


def test_eta_times_every_spatial_cubic_survives_but_eta_squared_and_quartics_do_not() -> None:
    variables = [unit.TaylorDual3.variable(axis) for axis in range(4)]
    eta = unit.TaylorDual3.eta()
    for alpha in unit.ALL_MULTIINDICES:
        if sum(alpha) != 3:
            continue
        monomial = eta
        for axis, exponent in enumerate(alpha):
            monomial *= variables[axis] ** exponent
        assert monomial.coefficient(alpha, 1) == 1.0
    assert not (eta * eta).coefficients
    assert not (variables[0] * variables[1] * variables[2] * variables[3]).coefficients


def test_discrete_inputs_are_strict_integral_nonbool() -> None:
    bad_alpha_entries = (0.9, -0.9, 1.1, "2", True)
    for bad in bad_alpha_entries:
        with pytest.raises(unit.TaylorDual3InputError):
            unit.TaylorDual3({(0, (bad, 0, 0, 0)): 1.0})
    for bad_eta in (True, 0.0, 1.0, "1"):
        with pytest.raises(unit.TaylorDual3InputError):
            unit.TaylorDual3({(bad_eta, unit.ZERO_ALPHA): 1.0})
    for bad_axis in (True, 0.0, 1.0, "1", -1, 4):
        with pytest.raises(unit.TaylorDual3InputError):
            unit.TaylorDual3.variable(bad_axis)
    value = unit.TaylorDual3.constant(1.0)
    for bad_order in (True, 0.0, 1.0):
        with pytest.raises(unit.TaylorDual3InputError):
            value.coefficient(unit.ZERO_ALPHA, bad_order)
    with pytest.raises(unit.TaylorDual3InputError):
        value**True


def test_nonfinite_inputs_and_arithmetic_fail_closed() -> None:
    for bad in (float("nan"), float("inf"), -float("inf")):
        with pytest.raises(unit.TaylorDual3InputError):
            unit.TaylorDual3.constant(bad)
        with pytest.raises(unit.TaylorDual3InputError):
            unit.TaylorDual3.constant(1.0).evaluate_spatial_layer((bad, 0.0, 0.0, 0.0))
    huge = unit.TaylorDual3.constant(1.0e308)
    with pytest.raises(unit.TaylorDual3NumericalError):
        _ = huge * huge


def test_public_unary_wrappers_reject_invalid_operands_with_typeerror() -> None:
    for function in (unit.exp, unit.sin, unit.cos, unit.sqrt):
        with pytest.raises(TypeError):
            function(object())
        with pytest.raises(TypeError):
            function(True)


def test_ring_arithmetic_inverse_and_domains() -> None:
    x0, x1, x2, _ = (unit.TaylorDual3.variable(axis) for axis in range(4))
    eta = unit.TaylorDual3.eta()
    value = 2.0 + 0.1 * x0 - 0.2 * x1 + 0.03 * x0 * x2 + eta * (0.4 + 0.2 * x1)
    assert (value * value.inverse()).almost_equal(1.0, atol=8.0e-14, rtol=8.0e-14)
    assert (value / value).almost_equal(1.0, atol=8.0e-14, rtol=8.0e-14)
    with pytest.raises(unit.TaylorDual3InputError):
        unit.TaylorDual3.variable(0).inverse()
    with pytest.raises(unit.TaylorDual3InputError):
        unit.TaylorDual3.constant(0.0).sqrt()
    with pytest.raises(unit.TaylorDual3InputError):
        unit.TaylorDual3.constant(-1.0).sqrt()


def test_analytic_functions_match_independent_sympy_mixed_jets(report: dict) -> None:
    x_symbol = sp.symbols("x0:4")
    eta_symbol = sp.symbols("eta")
    x = [unit.TaylorDual3.variable(axis) for axis in range(4)]
    eta = unit.TaylorDual3.eta()
    value = 1.7 + 0.2 * x[0] - 0.1 * x[1] + 0.03 * x[0] * x[2] + eta * (
        0.4 + 0.05 * x[1] - 0.02 * x[2] * x[3]
    )
    symbolic = 1.7 + 0.2 * x_symbol[0] - 0.1 * x_symbol[1] + 0.03 * x_symbol[0] * x_symbol[2] + eta_symbol * (
        0.4 + 0.05 * x_symbol[1] - 0.02 * x_symbol[2] * x_symbol[3]
    )
    cases = (
        (value.exp(), sp.exp(symbolic)),
        (value.sin(), sp.sin(symbolic)),
        (value.cos(), sp.cos(symbolic)),
        (value.inverse(), 1 / symbolic),
        (value.sqrt(), sp.sqrt(symbolic)),
    )
    alphas = (unit.ZERO_ALPHA, (1, 0, 0, 0), (0, 1, 1, 0), (2, 0, 0, 0), (1, 1, 1, 0), (0, 1, 1, 1))
    for actual, expected in cases:
        for eta_order in (0, 1):
            for alpha in alphas:
                reference = _sympy_derivative(expected, x_symbol, eta_symbol, alpha, eta_order)
                assert math.isclose(actual.derivative(alpha, eta_order), reference, abs_tol=3.0e-12, rel_tol=3.0e-12)
    assert report["analytic_identities"]["pass"] is True


def test_jet_extraction_uses_multiindex_factorials_on_both_layers() -> None:
    value = unit.TaylorDual3(
        {
            (0, unit.ZERO_ALPHA): 1.5,
            (0, (1, 1, 0, 0)): 4.0,
            (0, (2, 1, 0, 0)): 3.0,
            (1, unit.ZERO_ALPHA): 0.25,
            (1, (0, 0, 3, 0)): -2.0,
        }
    )
    jets = value.extract_jets()
    assert jets["primal"]["value"] == 1.5
    assert jets["primal"]["hessian"][0][1] == 4.0
    assert value.derivative((2, 1, 0, 0), 0) == 6.0
    assert jets["eta"]["value"] == 0.25
    assert jets["eta"]["third"][2][2][2] == -12.0


def test_spatial_layer_evaluation_does_not_treat_eta_as_a_real_number() -> None:
    x0 = unit.TaylorDual3.variable(0)
    x1 = unit.TaylorDual3.variable(1)
    eta = unit.TaylorDual3.eta()
    value = 2.0 + 3.0 * x0 - x1 * x1 + eta * (5.0 * x0 * x1)
    point = (0.2, -0.3, 0.0, 0.0)
    assert math.isclose(value.evaluate_spatial_layer(point, 0), 2.0 + 0.6 - 0.09)
    assert math.isclose(value.evaluate_spatial_layer(point, 1), -0.3)
    assert not hasattr(value, "evaluate")


def test_rodrigues_series_derivatives_match_high_precision_through_declared_body_domain() -> None:
    mp.mp.dps = 80
    for theta in (0.0, 1.0e-12, 1.0e-8, 1.0e-4, 0.1, 1.0, unit.SO3_SERIES_BODY_NORM_LIMIT):
        z = mp.mpf(str(theta)) ** 2
        for shift in (1, 2):
            actual = unit._rodrigues_entire_derivatives(float(z), shift)
            for derivative_order in range(5):
                expected = mp.nsum(
                    lambda k: (-1) ** k
                    * mp.factorial(k)
                    / mp.factorial(k - derivative_order)
                    * z ** (k - derivative_order)
                    / mp.factorial(2 * k + shift),
                    [derivative_order, mp.inf],
                )
                assert math.isclose(actual[derivative_order], float(expected), abs_tol=3.0e-15, rel_tol=3.0e-15)


def test_so3_domain_guards_reject_large_body_and_large_nonbody_jet(report: dict) -> None:
    with pytest.raises(unit.TaylorDual3InputError, match="wider rotations"):
        unit.so3_exp((unit.SO3_SERIES_BODY_NORM_LIMIT + 0.01, 0.0, 0.0))
    x0 = unit.TaylorDual3.variable(0)
    with pytest.raises(unit.TaylorDual3InputError, match="multiprecision"):
        unit.so3_exp((0.2 + (unit.SO3_SERIES_NONBODY_L1_LIMIT + 0.01) * x0, -0.3, 0.4))
    assert report["so3"]["outside_guard_rejected"] is True
    assert report["so3"]["outside_coefficient_guard_rejected"] is True


def test_so3_origin_is_regular_and_eta_tangent_is_hat_map() -> None:
    direction = np.asarray((0.7, -0.2, 0.5))
    eta = unit.TaylorDual3.eta()
    rotation = unit.so3_exp(tuple(value * eta for value in direction))
    np.testing.assert_array_equal(_bodies(rotation), np.eye(3))
    tangent = np.asarray(
        [[rotation[i][j].derivative(unit.ZERO_ALPHA, 1) for j in range(3)] for i in range(3)]
    )
    np.testing.assert_allclose(tangent, _numeric_skew(direction), atol=2.0e-15, rtol=0.0)


def test_so3_retains_eta_times_spatial_cubic_at_origin() -> None:
    x = unit.TaylorDual3.variable(0)
    eta = unit.TaylorDual3.eta()
    rotation = unit.so3_exp((x, eta, 0.0))
    e1 = _numeric_skew(np.asarray((1.0, 0.0, 0.0)))
    e2 = _numeric_skew(np.asarray((0.0, 1.0, 0.0)))
    expected = (
        e1 @ e1 @ e1 @ e2
        + e1 @ e1 @ e2 @ e1
        + e1 @ e2 @ e1 @ e1
        + e2 @ e1 @ e1 @ e1
    ) / 24.0
    actual = np.asarray(
        [[rotation[i][j].coefficient((3, 0, 0, 0), 1) for j in range(3)] for i in range(3)]
    )
    np.testing.assert_allclose(actual, expected, atol=3.0e-15, rtol=0.0)


def test_so3_constants_match_standard_rodrigues_inside_guard() -> None:
    for vector in (
        np.asarray((0.2, -0.3, 0.4)),
        np.asarray((unit.SO3_SERIES_BODY_NORM_LIMIT, 0.0, 0.0)),
    ):
        actual = _bodies(unit.so3_exp(vector))
        expected = _numeric_so3(vector)
        np.testing.assert_allclose(actual, expected, atol=3.0e-15, rtol=4.0e-15)
        np.testing.assert_allclose(actual.T @ actual, np.eye(3), atol=5.0e-15, rtol=0.0)
        assert math.isclose(float(np.linalg.det(actual)), 1.0, abs_tol=5.0e-15)


def test_so3_full_guarded_jets_are_orthogonal_in_the_quotient_algebra(report: dict) -> None:
    rng = np.random.default_rng(5671)
    variables = [unit.TaylorDual3.variable(axis) for axis in range(4)]
    eta = unit.TaylorDual3.eta()
    for _ in range(12):
        base = rng.uniform(-0.4, 0.4, size=3)
        q = []
        for component in range(3):
            value = unit.TaylorDual3.constant(base[component])
            for axis in range(4):
                value += rng.uniform(-0.15, 0.15) * variables[axis]
            value += eta * (rng.uniform(-0.15, 0.15) + rng.uniform(-0.08, 0.08) * variables[component])
            q.append(value)
        rotation = unit.so3_exp(q)
        residual = unit._matrix_orthogonality_residual(rotation)
        assert residual <= unit.SAMPLED_TOLERANCE
    assert report["so3"]["pass"] is True


def test_so3_eta_jvp_matches_spatial_seed_and_independent_numeric_oracle() -> None:
    base = np.asarray((0.2, -0.3, 0.4))
    tangent = np.asarray((1.0, 0.5, -0.25))
    x0 = unit.TaylorDual3.variable(0)
    eta = unit.TaylorDual3.eta()
    q = tuple(base[i] + tangent[i] * x0 + tangent[i] * eta for i in range(3))
    rotation = unit.so3_exp(q)
    spatial = np.asarray(
        [[rotation[i][j].derivative((1, 0, 0, 0), 0) for j in range(3)] for i in range(3)]
    )
    dual = np.asarray(
        [[rotation[i][j].derivative(unit.ZERO_ALPHA, 1) for j in range(3)] for i in range(3)]
    )
    step = 2.0e-6
    numeric = (_numeric_so3(base + step * tangent) - _numeric_so3(base - step * tangent)) / (2.0 * step)
    np.testing.assert_allclose(dual, spatial, atol=2.0e-14, rtol=2.0e-14)
    np.testing.assert_allclose(dual, numeric, atol=4.0e-10, rtol=2.0e-9)


def test_so3_implementation_has_no_norm_sqrt_or_origin_switch() -> None:
    source = inspect.getsource(unit.so3_exp)
    assert "sqrt" not in source
    assert "norm(" not in source
    assert "1.0e-" not in source
    assert "_rodrigues_entire_derivatives" in source
    assert "component * component" in source


def test_partial_and_rhojet2_product_rule_preserve_eta_spatial_layers() -> None:
    x0, x1 = unit.TaylorDual3.variable(0), unit.TaylorDual3.variable(1)
    eta = unit.TaylorDual3.eta()
    field = 2.0 + 3.0 * x0 * x1 + eta * (5.0 * x0 * x0 * x1)
    derivative = field.partial(0)
    assert derivative.derivative((0, 1, 0, 0), 0) == 3.0
    assert derivative.derivative((1, 1, 0, 0), 1) == 10.0

    left = unit.RhoJet2(field, 2.0 + eta, 3.0 - x0)
    right = unit.RhoJet2(4.0 + x1, -1.0 + 2.0 * eta, 0.5)
    product = left * right
    assert product.value.almost_equal(left.value * right.value)
    assert product.rho_first.almost_equal(
        left.rho_first * right.value + left.value * right.rho_first
    )
    assert product.rho_second.almost_equal(
        left.rho_second * right.value
        + 2.0 * left.rho_first * right.rho_first
        + left.value * right.rho_second
    )


def test_rhojet2_local_extraction_retains_eta_spatial_and_radial_two_jet() -> None:
    x0, x1 = unit.TaylorDual3.variable(0), unit.TaylorDual3.variable(1)
    eta = unit.TaylorDual3.eta()
    channel = unit.RhoJet2(
        1.0 + 2.0 * x0 + 3.0 * x0 * x1 + eta * (4.0 + 5.0 * x1),
        6.0 + 7.0 * x0 + eta * (8.0 + 9.0 * x0),
        10.0 + eta * 11.0,
    )
    jet = unit.rhojet2_local_two_jet((channel,))
    assert jet["channel_count"] == 1
    assert jet["value"][0].body == 1.0
    assert jet["value"][0].derivative(unit.ZERO_ALPHA, 1) == 4.0
    assert jet["first"][0][0].body == 2.0
    assert jet["first"][1][0].derivative(unit.ZERO_ALPHA, 1) == 5.0
    assert jet["first"][4][0].body == 6.0
    assert jet["first"][4][0].derivative(unit.ZERO_ALPHA, 1) == 8.0
    assert jet["second"][0][1][0].body == 3.0
    assert jet["second"][0][4][0].body == 7.0
    assert jet["second"][4][0][0].derivative(unit.ZERO_ALPHA, 1) == 9.0
    assert jet["second"][4][4][0].body == 10.0
    assert jet["second"][4][4][0].derivative(unit.ZERO_ALPHA, 1) == 11.0


def test_td3_determinant_cross_and_lorentzian_geometry_helpers() -> None:
    eta = unit.TaylorDual3.eta()
    matrix = (
        (1.0 + 0.2 * eta, 0.1, 0.0),
        (0.2, 1.3 - 0.1 * eta, 0.4),
        (0.0, -0.2, 0.9 + 0.3 * eta),
    )
    determinant = unit.td3_determinant(matrix)
    body = np.asarray([[unit.TaylorDual3._require(entry).body for entry in row] for row in matrix])
    tangent = np.asarray(
        [[unit.TaylorDual3._require(entry).derivative(unit.ZERO_ALPHA, 1) for entry in row] for row in matrix]
    )
    step = 1.0e-6
    numeric_jvp = (np.linalg.det(body + step * tangent) - np.linalg.det(body - step * tangent)) / (
        2.0 * step
    )
    assert math.isclose(determinant.body, float(np.linalg.det(body)), abs_tol=2.0e-15)
    assert math.isclose(determinant.derivative(unit.ZERO_ALPHA, 1), numeric_jvp, abs_tol=2.0e-10)
    cross = unit.td3_cross((1.0 + eta, 2.0, 3.0), (-1.0, 4.0, 0.5))
    np.testing.assert_allclose([entry.body for entry in cross], np.cross((1.0, 2.0, 3.0), (-1.0, 4.0, 0.5)))

    zero = unit.TaylorDual3.constant(0.0)
    euclidean = tuple(
        tuple(unit.TaylorDual3.constant(float(i == j)) for j in range(4))
        for i in range(4)
    )
    zero_first = tuple(
        tuple(tuple(zero for _ in range(4)) for _ in range(4))
        for _ in range(4)
    )
    with pytest.raises(unit.TaylorDual3InputError, match="Lorentzian"):
        unit.td3_metric_geometry(euclidean, zero_first)


def test_decoder_oracles_and_c2_bundle_are_byte_pinned(c2_bundle: dict, report: dict) -> None:
    assert unit._sha256(unit.POINTWISE_ORACLE_PATH) == unit.POINTWISE_ORACLE_SHA256
    assert pointwise.SCHEMA == unit.POINTWISE_ORACLE_SCHEMA
    assert route_c._sha256(route_c.BUNDLE) == route_c.BUNDLE_SHA256
    assert route_c._sha256(Path(route_c.__file__)) == (
        "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"
    )
    assert c2_bundle["schema"] == unit.C2_BUNDLE_SCHEMA
    assert report["source_pins"]["pointwise_decoder_v5_6_4_2_sha256"] == (
        unit.POINTWISE_ORACLE_SHA256
    )
    assert unit._sha256(unit.TORCH_C2_ORACLE_PATH) == unit.TORCH_C2_ORACLE_SHA256
    assert unit._sha256(unit.ROUTE_C_ORACLE_PATH) == unit.ROUTE_C_ORACLE_SHA256
    c2, literal_route_a, _bundle = unit._load_pinned_torch_c2_oracle()
    assert c2.BASE_ROUTE_WRAPPER_SHA256 == unit.TORCH_ROUTE_A_WRAPPER_SHA256
    assert c2.BUNDLE_SHA256 == unit.C2_BUNDLE_SHA256
    assert literal_route_a.V5_2_EXACT_ACTION_SHA256 == unit.LITERAL_ACTION_SHA256
    assert literal_route_a.SCHEMA.endswith("route-a-v5-6-5-certificate.v1")
    assert tuple(literal_route_a.COMPONENT_NAMES) == unit.LOCAL_DENSITY_COMPONENTS


def test_generated_layout_exactly_partitions_every_named_block(c2_bundle: dict) -> None:
    expected_names = (
        "common.gamma",
        "common.T",
        "common.log_Omega",
        "common.varphi_E0",
        "common.A_E0",
        "Q_frame.q",
        "plus.Y",
        "plus.metric_free",
        "plus.A_perp",
        "plus.B0_full",
        "plus.r_E0",
        "plus.boundary_jet_J1",
        "plus.interior_bump_C",
        "minus.Y",
        "minus.metric_free",
        "minus.A_perp",
        "minus.B0_full",
        "minus.r_E0",
        "minus.boundary_jet_J1",
        "minus.interior_bump_C",
    )
    for N in (1, 2, 3):
        K = N
        contract = unit.full_t4_decoder_contract(N, K)
        blocks = contract["free_layout"]["blocks"]
        assert tuple(blocks) == expected_names
        assert contract["free_coordinate_dimension"] == 242 * N + 128 * N * K
        assert contract["matches_pinned_c2_bundle_contract"] is True
        assert blocks == c2_bundle["pointwise_decoder_contract_by_N"][str(N)]["free_layout"]["blocks"]
        cursor = 0
        free = np.arange(contract["free_coordinate_dimension"], dtype=float)
        tangent = -free - 0.25
        for name, specification in blocks.items():
            assert specification["start"] == cursor
            cursor = specification["stop"]
            decoded = unit._free_block_td3(free, tangent, contract, name).reshape(-1)
            expected_slice = slice(specification["start"], specification["stop"])
            np.testing.assert_array_equal([entry.body for entry in decoded], free[expected_slice])
            np.testing.assert_array_equal(
                [entry.derivative(unit.ZERO_ALPHA, 1) for entry in decoded],
                tangent[expected_slice],
            )
        assert cursor == contract["free_coordinate_dimension"]


def test_boundary_decoder_matches_pinned_pointwise_oracle_N1_to_N3(c2_bundle: dict) -> None:
    points = np.asarray(((0.13, -0.27, 0.21, -0.08), (0.41, 0.19, -0.31, 0.07)))
    for N in (1, 2, 3):
        _member, contract, free, tangent = _member_vectors(c2_bundle, N)
        oracle = pointwise.decode_pointwise_boundary(free, contract, points)
        tables = pointwise.fourier_tables(contract["basis"], points)
        q_coefficients = pointwise._free_get(free, contract["free_layout"]["blocks"], "Q_frame.q")
        _oracle_S, oracle_dS = pointwise._rotation_field(q_coefficients, tables)
        for point_index, point in enumerate(points):
            decoded = unit.decode_common_first_boundary_td3(free, tangent, N, N, point)
            for name in ("gamma", "log_Omega", "varphi", "A_Sigma", "E0", "E_Q", "S_Q"):
                np.testing.assert_allclose(
                    _td3_layer(decoded["common"][name]),
                    np.asarray(oracle["common"][name][point_index]),
                    atol=5.0e-13,
                    rtol=0.0,
                )
            dS = np.asarray(
                [
                    [[decoded["common"]["dS_Q"][mu][i][j].body for j in range(3)] for i in range(3)]
                    for mu in range(4)
                ]
            )
            np.testing.assert_allclose(dS, oracle_dS[point_index], atol=5.0e-13, rtol=0.0)
            aliases = (
                ("Y_first", "Y_first"),
                ("metric_trace", "g_trace"),
                ("log_Omega_trace", "log_Omega_trace"),
                ("phi_trace", "phi_trace"),
                ("A_trace_full", "A_trace_full"),
                ("B_trace_full", "B_trace_full"),
                ("boundary_jet_J1", "boundary_jet_J1"),
                ("interior_bump_C", "interior_bump_C"),
                ("R_source_to_Q", "R_source_to_Q"),
                ("dR_source_to_Q", "dR_source_to_Q"),
            )
            for side in unit.SIDES:
                for mine, theirs in aliases:
                    np.testing.assert_allclose(
                        _td3_layer(decoded["sides"][side][mine]),
                        np.asarray(oracle["sides"][side][theirs][point_index]),
                        atol=5.0e-13,
                        rtol=0.0,
                    )
                np.testing.assert_allclose(
                    _td3_layer(decoded["sides"][side]["X64_trace"]),
                    _pointwise_side_x64(oracle["sides"][side], point_index),
                    atol=5.0e-13,
                    rtol=0.0,
                )


def test_boundary_eta_jvp_matches_only_sampled_central_difference_oracle(c2_bundle: dict) -> None:
    point = np.asarray((0.13, -0.27, 0.21, -0.08))
    step = 2.0e-6
    for N in (1, 2, 3):
        _member, contract, free, tangent = _member_vectors(c2_bundle, N)
        decoded = unit.decode_common_first_boundary_td3(free, tangent, N, N, point)
        plus = pointwise.decode_pointwise_boundary(free + step * tangent, contract, point[None, :])
        minus = pointwise.decode_pointwise_boundary(free - step * tangent, contract, point[None, :])
        for name in ("S_Q", "A_Sigma", "E_Q"):
            numeric = (np.asarray(plus["common"][name][0]) - np.asarray(minus["common"][name][0])) / (
                2.0 * step
            )
            np.testing.assert_allclose(
                _td3_layer(decoded["common"][name], 1), numeric, atol=5.0e-9, rtol=0.0
            )
        for side in unit.SIDES:
            numeric_x64 = (
                _pointwise_side_x64(plus["sides"][side], 0)
                - _pointwise_side_x64(minus["sides"][side], 0)
            ) / (2.0 * step)
            np.testing.assert_allclose(
                _td3_layer(decoded["sides"][side]["X64_trace"], 1),
                numeric_x64,
                atol=5.0e-9,
                rtol=0.0,
            )
            for name in ("R_source_to_Q", "dR_source_to_Q"):
                numeric = (
                    np.asarray(plus["sides"][side][name][0])
                    - np.asarray(minus["sides"][side][name][0])
                ) / (2.0 * step)
                np.testing.assert_allclose(
                    _td3_layer(decoded["sides"][side][name], 1),
                    numeric,
                    atol=5.0e-9,
                    rtol=0.0,
                )


def test_collar_values_and_eta_jvp_match_route_c_at_interior_and_endpoints(c2_bundle: dict) -> None:
    point = (0.13, -0.27, 0.21, -0.08)
    theta = point[0] + point[1]
    step = 2.0e-6
    for N in (1, 2, 3):
        _member, contract, free, tangent = _member_vectors(c2_bundle, N)
        for side in unit.SIDES:
            for rho in (0.0, 0.37, 1.0):
                decoded = unit.decode_full_t4_collar_point(free, tangent, N, N, point, rho, side)
                ambient, _Y, _Y_theta = route_c._ambient_value(free, contract, side, theta, rho)
                pulled, reference = route_c._pullback_vector(free, contract, side, theta, rho)
                np.testing.assert_allclose(
                    decoded["ambient_X64"]["primal"]["value"], ambient, atol=5.0e-11, rtol=0.0
                )
                np.testing.assert_allclose(
                    decoded["pulled_X64"]["primal"]["value"], pulled, atol=5.0e-11, rtol=0.0
                )
                np.testing.assert_allclose(
                    decoded["pulled_reference_metric15"]["primal"]["value"],
                    reference,
                    atol=5.0e-11,
                    rtol=0.0,
                )
                np.testing.assert_allclose(
                    decoded["pulled_X79"]["primal"]["value"],
                    np.concatenate((pulled, reference)),
                    atol=5.0e-11,
                    rtol=0.0,
                )
            decoded = unit.decode_full_t4_collar_point(free, tangent, N, N, point, 0.37, side)
            ambient_plus = route_c._ambient_value(free + step * tangent, contract, side, theta, 0.37)[0]
            ambient_minus = route_c._ambient_value(free - step * tangent, contract, side, theta, 0.37)[0]
            pulled_plus, reference_plus = route_c._pullback_vector(
                free + step * tangent, contract, side, theta, 0.37
            )
            pulled_minus, reference_minus = route_c._pullback_vector(
                free - step * tangent, contract, side, theta, 0.37
            )
            np.testing.assert_allclose(
                decoded["ambient_X64"]["eta"]["value"],
                (ambient_plus - ambient_minus) / (2.0 * step),
                atol=3.0e-9,
                rtol=0.0,
            )
            np.testing.assert_allclose(
                decoded["pulled_X79"]["eta"]["value"],
                np.concatenate(
                    (
                        (pulled_plus - pulled_minus) / (2.0 * step),
                        (reference_plus - reference_minus) / (2.0 * step),
                    )
                ),
                atol=3.0e-9,
                rtol=0.0,
            )


def test_complete_primal_five_dimensional_two_jet_matches_pinned_pullback(c2_bundle: dict) -> None:
    upstream = unit._load_pinned_upstream()
    point = (0.13, -0.27, 0.21, -0.08)
    units = tuple(tuple(int(i == j) for i in range(4)) for j in range(4))
    for N in (1, 2, 3):
        _member, _contract, free, tangent = _member_vectors(c2_bundle, N)
        for side in unit.SIDES:
            for rho in (0.0, 0.37, 1.0):
                decoded = unit.decode_full_t4_collar_point(free, tangent, N, N, point, rho, side)
                boundary = decoded["boundary"]["sides"][side]
                Y_first = np.asarray([entry.body for entry in boundary["Y_first"]])
                Y_second = np.asarray(
                    [[boundary["Y_first"][mu].derivative(units[a]) for a in range(4)] for mu in range(4)]
                )
                Y_third = np.asarray(
                    [
                        [
                            [
                                boundary["Y_first"][mu].derivative(
                                    tuple(units[a][i] + units[b][i] for i in range(4))
                                )
                                for b in range(4)
                            ]
                            for a in range(4)
                        ]
                        for mu in range(4)
                    ]
                )
                expected = upstream.pulled_back_two_jet(
                    decoded["ambient_X64"]["primal"]["value"],
                    decoded["ambient_X64"]["primal"]["first"],
                    decoded["ambient_X64"]["primal"]["second"],
                    Y_first,
                    Y_second,
                    Y_third,
                    side,
                )
                for derivative in ("value", "first", "second"):
                    np.testing.assert_allclose(
                        decoded["pulled_X79"]["primal"][derivative],
                        expected[derivative],
                        atol=5.0e-12,
                        rtol=0.0,
                    )


def test_q_cancels_only_from_lateral_traces_not_full_decoder(c2_bundle: dict) -> None:
    _member, contract, free, tangent = _member_vectors(c2_bundle, 3)
    point = (0.13, -0.27, 0.21, -0.08)
    q_block = contract["free_layout"]["blocks"]["Q_frame.q"]
    q_slice = slice(q_block["start"], q_block["stop"])
    zero_free, zero_tangent = free.copy(), tangent.copy()
    zero_free[q_slice] = 0.0
    zero_tangent[q_slice] = 0.0
    actual = unit.decode_common_first_boundary_td3(free, tangent, 3, 3, point)
    q_zero = unit.decode_common_first_boundary_td3(zero_free, zero_tangent, 3, 3, point)
    for side in unit.SIDES:
        for name in ("phi_trace", "A_trace_full"):
            for left, right in zip(
                np.asarray(actual["sides"][side][name], dtype=object).flat,
                np.asarray(q_zero["sides"][side][name], dtype=object).flat,
            ):
                assert left.coefficients == right.coefficients
    assert np.max(np.abs(_td3_layer(actual["common"]["S_Q"]) - np.eye(3))) > 1.0e-5


def test_effective_frame_sign_side_parity_antisymmetry_and_B_mutants(report: dict) -> None:
    decoder = report["decoder"]
    assert decoder["q_zero_r_E0_spatial_activity"] > 1.0e-5
    assert decoder["q_zero_r_E0_noncommuting_cross_activity"] > 1.0e-6
    assert decoder["missing_R_transpose_dR_mutant_max_abs_failure"] > 1.0e-5
    assert decoder["flipped_R_transpose_dR_mutant_max_abs_failure"] > 1.0e-5
    assert decoder["side_radial_sign_mutant_max_abs_failure"] > 1.0e-3
    assert decoder["symmetric_contamination_before_vee_rejected"] is True
    assert decoder["B_pullback_radial_and_tangential_one_hot_max_abs_residual"] == 0.0

    zero = unit.TaylorDual3.constant(0.0)
    contaminated = ((unit.TaylorDual3.constant(1.0e-4), zero, zero), (zero, zero, zero), (zero, zero, zero))
    with pytest.raises(unit.TaylorDual3NumericalError, match="not skew-symmetric"):
        unit._vee_checked_td3(contaminated, "test contamination")


def test_full_t4_axes_N9_N11_and_decoder_inputs_fail_closed(report: dict, c2_bundle: dict) -> None:
    assert report["decoder"]["full_t4_axis_activity"] == {"N9_x2": 0.1, "N11_x3": 0.1}
    _member, _contract, free, tangent = _member_vectors(c2_bundle, 1)
    for call in (
        lambda: unit.decode_common_first_boundary_td3(free[:-1], tangent, 1, 1, (0.0,) * 4),
        lambda: unit.decode_common_first_boundary_td3(free, tangent[:-1], 1, 1, (0.0,) * 4),
        lambda: unit.decode_common_first_boundary_td3(free, tangent, 1, 1, (0.0,) * 3),
        lambda: unit.decode_full_t4_collar_point(free, tangent, 1, 1, (0.0,) * 4, -1.0e-9, "plus"),
        lambda: unit.decode_full_t4_collar_point(free, tangent, 1, 1, (0.0,) * 4, 1.0 + 1.0e-9, "minus"),
        lambda: unit.decode_full_t4_collar_point(free, tangent, 1, 1, (0.0,) * 4, True, "plus"),
        lambda: unit.decode_full_t4_collar_point(free, tangent, 1, 1, (0.0,) * 4, 0.5, "bad"),
        lambda: unit.full_t4_decoder_contract(True, 1),
        lambda: unit.full_t4_decoder_contract(1, True),
    ):
        with pytest.raises(unit.TaylorDual3InputError):
            call()


def test_twenty_local_density_values_and_exact_eta_jvps_match_pinned_torch(report: dict) -> None:
    local = report["local_densities"]
    assert local["component_count"] == 20
    assert tuple(local["component_names"]) == unit.LOCAL_DENSITY_COMPONENTS
    assert tuple(local["sampled_N"]) == (1, 2, 3)
    assert tuple(local["sampled_bulk_rho"]) == (0.23, 0.71)
    assert len(local["sampled_T4_points"]) == 2
    assert local["domain_pass"] == {"bulk": True, "GHY": True, "interface": True}
    assert local["all_outputs_finite"] is True
    assert max(local["max_abs_value_residual_by_domain"].values()) <= 1.0e-11
    assert max(local["max_abs_eta_jvp_residual_by_domain"].values()) <= 2.0e-11
    assert local["route_c_secondary_value_max_abs_residual"] <= 2.0e-10
    assert local["route_c_secondary_nonzero_sign_mismatches"] == 0
    assert local["route_c_secondary_never_used_for_jvp"] is True
    assert local["pass"] is True


def test_local_density_api_keeps_domains_separate_accepts_endpoints_and_has_no_total(c2_bundle: dict) -> None:
    _member, _contract, free, tangent = _member_vectors(c2_bundle, 1)
    point = (0.13, -0.27, 0.21, -0.08)
    for rho in (0.0, 1.0):
        result = unit.local_density_values_and_eta_jvps(free, tangent, 1, 1, point, rho)
        assert tuple(result["component_names"]) == unit.LOCAL_DENSITY_COMPONENTS
        assert len(result["values"]) == len(result["eta_jvps"]) == 20
        assert all(math.isfinite(value) for value in result["values"] + result["eta_jvps"])
        assert result["rho_bulk"] == rho
        assert result["domain_separation"]["GHY"].startswith("rho=0 boundary")
        assert "S_total" not in result
        assert "S_total" not in result["components"]
    for bad_rho in (-1.0e-12, 1.0 + 1.0e-12, True, float("nan")):
        with pytest.raises(unit.TaylorDual3InputError):
            unit.local_density_values_and_eta_jvps(free, tangent, 1, 1, point, bad_rho)


def test_effective_local_density_mutants_and_regular_phi_zero_control(report: dict) -> None:
    local = report["local_densities"]
    failures = local["effective_mutant_max_abs_failures"]
    assert set(failures) == {
        "reference_bulk_omitted",
        "BF_duplicate_side_sign",
        "GHY_normal_reversed",
        "A_cross_phi_sign",
        "A_cross_A_sign",
        "Robin_plus_y_a",
    }
    assert min(failures.values()) > local["effective_mutant_threshold"]
    flrw = local["flat_spatial_FLRW_gauss_witness"]
    assert math.isclose(flrw["scale_factor"], 1.7)
    assert math.isclose(flrw["scale_first"], 0.23)
    assert math.isclose(flrw["scale_second"], -0.11)
    assert abs(flrw["nominal_Rcal"]) <= 2.0e-13
    assert math.isclose(flrw["opposite_gauss_sign_Rcal"], 0.21965397923875438, abs_tol=2.0e-15)
    assert flrw["pass"] is True
    assert local["V4_phi_zero_regular_and_exact_zero"] is True
    assert local["naive_phi_norm_at_zero_rejected_control"] is True

    eta = unit.TaylorDual3.eta()
    regular = unit._regular_v4_td3(
        1.2 + 0.3 * eta,
        (0.4 * eta, -0.2 * eta, 0.1 * eta),
    )
    assert regular.coefficients == {}
    with pytest.raises(unit.TaylorDual3InputError, match="strictly positive"):
        sum(
            (component * component for component in (0.4 * eta, -0.2 * eta, 0.1 * eta)),
            unit.TaylorDual3.constant(0.0),
        ).sqrt()


def test_bulk_formula_does_not_duplicate_side_sign_and_local_inputs_fail_closed(report: dict, c2_bundle: dict) -> None:
    assert report["local_densities"]["effective_mutant_max_abs_failures"]["BF_duplicate_side_sign"] > 1.0e-3
    assert report["local_densities"]["domain_pass"]["bulk"] is True
    assert all(report["local_densities"]["fail_closed_rejection_results"])
    _member, _contract, free, tangent = _member_vectors(c2_bundle, 1)
    point = (0.13, -0.27, 0.21, -0.08)
    for call in (
        lambda: unit.local_density_values_and_eta_jvps(free[:-1], tangent, 1, 1, point, 0.23),
        lambda: unit.local_density_values_and_eta_jvps(free, tangent[:-1], 1, 1, point, 0.23),
        lambda: unit.local_density_values_and_eta_jvps(free, tangent, 1, 1, point[:-1], 0.23),
    ):
        with pytest.raises(unit.TaylorDual3InputError):
            call()


def test_finite_full_t4_rho_rule_shapes_moments_aliases_and_resource_guards(report: dict) -> None:
    quadrature = unit.finite_full_t4_rho_quadrature(2, 3)
    assert quadrature["tangential_points"].shape == (16, 4)
    assert quadrature["tangential_weights"].shape == (16,)
    assert quadrature["rho_nodes"].shape == quadrature["radial_weights"].shape == (3,)
    assert np.all(quadrature["tangential_points"] >= 0.0)
    assert np.all(quadrature["tangential_points"] < 2.0 * math.pi)
    assert np.all((quadrature["rho_nodes"] > 0.0) & (quadrature["rho_nodes"] < 1.0))
    assert math.isclose(math.fsum(quadrature["tangential_weights"]), unit.T4_VOLUME)
    assert math.isclose(math.fsum(quadrature["radial_weights"]), 1.0)
    assert quadrature["bulk_node_count_per_side"] == 48
    assert quadrature["boundary_node_count"] == 16

    checked = report["finite_quadrature"]
    assert checked["tangential_order_per_axis"] == 5
    assert checked["tangential_node_count"] == 625
    assert checked["radial_order"] == 4
    assert tuple(checked["radial_exact_degrees"]) == tuple(range(8))
    assert checked["constant_T4_moment_abs_residual"] <= checked["moment_tolerance"]
    assert checked["worst_nonzero_Fourier_moment_abs_residual"] <= checked["moment_tolerance"]
    assert checked["worst_radial_exact_moment_abs_residual"] <= checked["moment_tolerance"]
    assert checked["periodic_alias_canary_abs_discrete_integral"] >= 0.99 * unit.T4_VOLUME
    assert checked["periodic_alias_canary_continuum_integral"] == 0.0
    assert checked["radial_first_nonexact_degree"] == 8
    assert checked["radial_first_nonexact_moment_abs_error_canary"] > 1.0e-8
    assert checked["pinned_torch_rule_max_abs_residual"] <= checked["pinned_torch_rule_tolerance"]
    assert checked["pinned_torch_T4_point_order_compared_entrywise"] is True
    assert min(checked["algebraic_mutant_witness_abs_failures"].values()) > checked["effective_mutant_threshold"]
    assert checked["finite_rule_not_continuum_exact"] is True
    assert checked["pass"] is True

    for q, radial in (
        (0, 1),
        (True, 1),
        (1.5, 1),
        (unit.MAX_FINITE_T4_ORDER_PER_AXIS + 1, 1),
        (1, 0),
        (1, True),
        (1, 1.5),
        (1, unit.MAX_FINITE_RADIAL_ORDER + 1),
    ):
        with pytest.raises(unit.TaylorDual3InputError):
            unit.finite_full_t4_rho_quadrature(q, radial)


def test_integrated_action_same_grid_oracle_totals_scope_and_mutants(report: dict) -> None:
    integrated = report["finite_integrated_action"]
    assert tuple(integrated["output_names"]) == unit.INTEGRATED_ACTION_OUTPUTS
    assert integrated["component_count_before_total"] == 20
    assert set(integrated["sampled_cases"]) == {"N1_Q1_R2", "N3_Q2_R1"}
    assert integrated["all_same_grid_comparisons_pass"] is True
    assert integrated["all_S_total_values_and_jvps_are_post_integration_fsum"] is True
    for label, expected_counts in {
        "N1_Q1_R2": {
            "common_boundary_decodes": 1,
            "bulk_points_per_side": 2,
            "boundary_points": 1,
        },
        "N3_Q2_R1": {
            "common_boundary_decodes": 16,
            "bulk_points_per_side": 16,
            "boundary_points": 16,
        },
    }.items():
        row = integrated["sampled_cases"][label]
        assert row["same_explicit_nodes_and_weights_passed_to_both_routes"] is True
        assert row["evaluation_counts"] == expected_counts
        assert row["S_total_value_is_post_integration_fsum"] is True
        assert row["S_total_eta_jvp_is_post_integration_fsum"] is True
        for comparison_name in ("value_comparison", "eta_jvp_comparison"):
            comparison = row[comparison_name]
            assert tuple(comparison["rows"]) == unit.INTEGRATED_ACTION_OUTPUTS
            assert max(
                output["residual_over_fixed_tolerance"]
                for output in comparison["rows"].values()
            ) <= 1.0
            assert comparison["max_residual_over_fixed_tolerance"] <= 1.0
            assert comparison["pass"] is True
    assert min(integrated["algebraic_mutant_witness_max_abs_failures"].values()) > integrated["effective_mutant_threshold"]
    assert integrated["unmapped_Gauss_node_outside_unit_interval_rejected"] is True
    assert integrated["sampled_N1_N3_members_are_theta_only_without_x2_x3_activity"] is True
    assert integrated["full_T4_rule_but_not_full_axis_active_action_sample"] is True
    assert integrated["finite_same_grid_result_not_continuum_quadrature_claim"] is True
    assert integrated["pass"] is True


def test_integrated_action_api_separates_domains_and_forms_total_last(c2_bundle: dict) -> None:
    _member, _contract, free, tangent = _member_vectors(c2_bundle, 1)
    result = unit.integrated_action_values_and_eta_jvps(free, tangent, 1, 1, 1, 1)
    assert tuple(result["component_names"]) == unit.LOCAL_DENSITY_COMPONENTS
    assert tuple(result["output_names"]) == unit.INTEGRATED_ACTION_OUTPUTS
    assert tuple(result["components"]) == unit.LOCAL_DENSITY_COMPONENTS
    assert "S_total" not in result["components"]
    assert len(result["values"]) == len(result["eta_jvps"]) == 21
    assert result["S_total"]["value"] == math.fsum(
        result["components"][name]["value"] for name in unit.LOCAL_DENSITY_COMPONENTS
    )
    assert result["S_total"]["eta_jvp"] == math.fsum(
        result["components"][name]["eta_jvp"] for name in unit.LOCAL_DENSITY_COMPONENTS
    )
    assert result["values"][-1] == result["S_total"]["value"]
    assert result["eta_jvps"][-1] == result["S_total"]["eta_jvp"]
    assert result["S_total_formed_only_after_twenty_domain_integrals"] is True
    assert result["domain_separation"] == {
        "bulk": "twelve atoms integrated on T4 x rho",
        "GHY": "two atoms integrated once on the T4 boundary",
        "interface": "six atoms integrated once on the shared T4 boundary",
    }
    for name in unit.BULK_COMPONENTS:
        assert result["components"][name]["domain"] == "T4 x rho"
    for name in unit.BOUNDARY_COMPONENTS:
        assert result["components"][name]["domain"] == "T4 boundary"


def test_reserved_pair_writes_no_receipt_and_main_prints_current_report(report: dict, capsys) -> None:
    source = Path(unit.__file__).read_text(encoding="utf-8")
    assert "write_text(" not in source
    assert "ARTIFACTS" not in source
    unit.main()
    output = capsys.readouterr().out
    assert unit.SCHEMA in output
    assert '"twenty_separate_local_density_values_and_eta_jvps_sampled_pass": true' in output
    assert '"finite_full_t4_rho_quadrature_rules_and_alias_canaries_sampled_pass": true' in output
    assert '"finite_integrated_twenty_components_S_total_and_eta_jvp_same_grid_pinned_torch_sampled_pass": true' in output
    assert '"all_S_total_values_and_jvps_are_post_integration_fsum": true' in output
    assert '"integrated_action_pass": false' in output
    assert '"quadrature_pass": false' in output
    assert '"C1_N1_promotion_authorized": false' in output
