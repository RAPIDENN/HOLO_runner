"""Tests for the fail-closed v5.6.7.1 TaylorDual3/SO(3) minimum."""

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


TRUE_KEYS = frozenset(
    {
        "taylor_dual3_independent_eta_spatial_degree_three_algebra_pass",
        "taylor_dual3_analytic_identities_sampled_within_tolerance_pass",
        "so3_entire_z_origin_regular_orthogonality_and_eta_jvp_sampled_pass",
    }
)
FALSE_KEYS = frozenset(
    {
        "full_t4_decoder_implemented_pass",
        "local_bulk_density_implemented_pass",
        "local_ghy_density_implemented_pass",
        "local_interface_density_implemented_pass",
        "local_density_values_and_jvps_pass",
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


def test_report_has_only_three_true_scoped_decisions(report: dict) -> None:
    assert report["schema"] == unit.SCHEMA
    assert set(report["decision"]) == TRUE_KEYS | FALSE_KEYS
    assert {key for key, value in report["decision"].items() if value} == TRUE_KEYS
    assert {key for key, value in report["decision"].items() if not value} == FALSE_KEYS
    assert "sampled float64" in report["scope"]
    assert "No decoder" in report["scope"]
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


def test_reserved_pair_writes_no_receipt_and_main_prints_current_report(report: dict, capsys) -> None:
    source = Path(unit.__file__).read_text(encoding="utf-8")
    assert "write_text(" not in source
    assert "ARTIFACTS" not in source
    unit.main()
    output = capsys.readouterr().out
    assert unit.SCHEMA in output
    assert '"local_density_values_and_jvps_pass": false' in output
    assert '"C1_N1_promotion_authorized": false' in output
