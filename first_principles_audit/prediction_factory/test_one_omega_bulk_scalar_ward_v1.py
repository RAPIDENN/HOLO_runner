"""Independent scalar Euler checks and Ward-receipt regression tests.

The one-dimensional literal variation is an additional exact point check, not a
replacement for the general symbolic covector and Ward identities. No physical
coupled-system promotion follows from these tests.
"""
from __future__ import annotations

import copy

import pytest
import sympy as sp

from . import one_omega_bulk_scalar_equations_v1 as science


def _zero(expression):
    entries = list(expression) if isinstance(expression, sp.MatrixBase) else [expression]
    return all(sp.simplify(value) == 0 for value in entries)


@pytest.fixture(scope="module")
def model():
    return science.derive_model()


def test_sigma_euler_variable_one_field_metric_and_potential_sign():
    field = sp.Symbol("independent_q", positive=True)
    gradient, box = sp.symbols("independent_X independent_box", real=True)
    result = science.sigma_euler(sp.Matrix([[field**2]]), sp.Matrix([field]),
                                sp.Matrix([[gradient]]), sp.Matrix([box]), field**4/4)
    assert _zero(result[0] - (field**2*box + field*gradient - field**3))


def test_sigma_euler_two_field_polar_metric_has_correct_connection_factor():
    radius, angle = sp.symbols("independent_r independent_theta", real=True)
    Xrr, Xra, Xaa, br, ba = sp.symbols("Xrr Xra Xaa br ba", real=True)
    result = science.sigma_euler(sp.diag(1, radius**2), sp.Matrix([radius, angle]),
                                sp.Matrix([[Xrr, Xra], [Xra, Xaa]]), sp.Matrix([br, ba]), 0)
    assert _zero(result - sp.Matrix([br-radius*Xaa, radius**2*ba+2*radius*Xra]))


def test_literal_sigma_metric_and_determinant(model):
    o, phi, G, Z = (model[key] for key in ("omega", "phi", "G", "Z"))
    expected = sp.diag(G + 9*Z*sum(f*f for f in phi)/(4*o**2), Z, Z, Z)
    for a in range(3):
        expected[0,a+1] = expected[a+1,0] = 3*Z*phi[a]/(2*o)
    assert _zero(model["C_old"] - expected)
    assert _zero(model["C_old"].det() - G*Z**3)
    assert _zero(model["C_new"] - sp.diag(G, Z/o**3, Z/o**3, Z/o**3))


def test_phi_box_and_minus_fifteen_quarters_coefficients(model):
    o, phi, Z, X, boxes = (model[key] for key in ("omega", "phi", "Z", "X_old", "box_old"))
    for a in range(3):
        equation = model["E_old"][a+1]
        assert _zero(sp.diff(equation, X[0,0]) + 15*Z*phi[a]/(4*o**2))
        assert _zero(sp.diff(equation, boxes[0]) - 3*Z*phi[a]/(2*o))
        for b in range(3):
            assert _zero(sp.diff(equation, X[0,b+1]))
            assert _zero(sp.diff(equation, boxes[b+1]) - (Z if a == b else 0))


def test_omega_retains_mixed_gradient_terms(model):
    o, phi, Z, X = (model[key] for key in ("omega", "phi", "Z", "X_old"))
    equation = model["E_old"][0]
    for a in range(3):
        assert _zero(sp.diff(equation, X[0,a+1]) - 9*Z*phi[a]/(2*o**2))
        assert _zero(sp.diff(equation, X[a+1,a+1]) - 3*Z/(2*o))


def test_phi_origin_is_regular_without_discarding_independent_gradient_jets(model):
    substitution = {field: 0 for field in model["phi"]}
    equations = model["E_old"].subs(substitution)
    assert not any(e.has(sp.nan, sp.zoo, sp.oo, -sp.oo) for e in equations)
    o, Z, boxes, X = (model[key] for key in ("omega", "Z", "box_old", "X_old"))
    for a in range(3):
        assert _zero(equations[a+1] - Z*boxes[a+1])
    expected_omega = (model["G"]*boxes[0] - sp.diff(model["U"], o)
                      + 3*Z*sum(X[a+1,a+1] for a in range(3))/(2*o))
    assert _zero(equations[0] - expected_omega)


def test_box_chain_rule_has_both_first_and_second_field_derivatives(model):
    o, phi, X = (model[key] for key in ("omega", "phi", "X_old"))
    expected = sp.Matrix([0, *(
        3*phi[a]*X[0,0]/(4*sp.sqrt(o)) + 3*sp.sqrt(o)*X[0,a+1]
        for a in range(3))])
    assert _zero(model["box_chain_correction"] - expected)
    assert _zero(model["box_new_pulled"] - model["jacobian"]*model["box_old"] - expected)
    assert _zero(model["X_new_pulled"] - model["jacobian"]*X*model["jacobian"].T)
    assert _zero(model["covariance_residual"])


def test_omitting_second_box_chain_derivative_breaks_off_shell_covariance(model):
    substitutions = dict(model["substitutions"])
    only_first_derivative = model["jacobian"] * model["box_old"]
    substitutions.update(dict(zip(model["box_new"], only_first_derivative)))
    wrong = model["jacobian"].T * model["E_new"].xreplace(substitutions)
    # Differentiating with respect to one independent gradient contraction
    # removes every potential term and isolates the missing chain correction.
    coefficient = sp.diff(wrong[1] - model["E_old"][1], model["X_old"][0,1])
    assert _zero(coefficient + 3*model["Z"]/model["omega"])
    assert not _zero(coefficient)


@pytest.fixture(scope="module")
def literal_one_dimensional_point(model):
    q = model["q_old"]
    o, *phi = list(q)
    G, Z, mass, M5c, k = (model[key] for key in ("G", "Z", "M", "M5c", "k"))
    velocities = sp.Matrix(sp.symbols("independent_velocity0:4", real=True))
    accelerations = sp.Matrix(sp.symbols("independent_acceleration0:4", real=True))
    W = 3*M5c*k*sp.exp(-G*o**2/(6*M5c))
    U = sp.diff(W,o)**2/(2*G)-2*W**2/(3*M5c)
    radial_fourth_power = o**6*sum(field**2 for field in phi)**2
    potential = U + Z*mass**2/o**5 * radial_fourth_power/(2*sp.sqrt(1+radial_fourth_power))
    density = -G*velocities[0]**2/2 - Z*sum(
        (velocities[a+1] + 3*phi[a]*velocities[0]/(2*o))**2 for a in range(3))/2 - potential
    point = {o: 2, phi[0]: sp.Rational(1,4), phi[1]: -sp.Rational(1,4), phi[2]: 0,
             G: sp.Rational(6,5), Z: 1, mass: 1, M5c: 1, k: 1}
    point.update(dict(zip(velocities, map(sp.Rational, ["1/3", "-2/5", "3/7", "5/11"]))))
    point.update(dict(zip(accelerations, map(sp.Rational, ["7/13", "-11/17", "13/19", "-17/23"]))))
    exact = []
    for a in range(4):
        momentum = sp.diff(density, velocities[a])
        total_derivative = sum(sp.diff(momentum, q[b])*velocities[b]
                               + sp.diff(momentum, velocities[b])*accelerations[b] for b in range(4))
        exact.append((sp.diff(density, q[a]) - total_derivative).subs(point))
    jet_substitutions = {model["X_old"][a,b]: velocities[a]*velocities[b]
                         for a in range(4) for b in range(a,4)}
    jet_substitutions.update(dict(zip(model["box_old"], accelerations)))
    return {"expected": sp.Matrix(exact), "point": point, "jets": jet_substitutions}


def test_scalar_equations_match_literal_one_dimensional_variation_at_exact_point(model, literal_one_dimensional_point):
    case = literal_one_dimensional_point
    actual = model["E_old"].xreplace(case["jets"]).subs(case["point"])
    assert _zero(actual - case["expected"])


def test_minus_fifteen_quarters_omission_fails_literal_variation_point(model, literal_one_dimensional_point):
    case = literal_one_dimensional_point
    wrong = model["E_old"][1] + 15*model["Z"]*model["phi"][0]*model["X_old"][0,0]/(4*model["omega"]**2)
    actual = wrong.xreplace(case["jets"]).subs(case["point"])
    assert not _zero(actual - case["expected"][1])


@pytest.mark.parametrize("kind", ["nonsymmetric_metric", "nonsymmetric_products", "duplicate_fields", "bad_boxes", "nonfinite"])
def test_sigma_euler_rejects_malformed_inputs(kind):
    q, r = sp.symbols("q_independent r_independent", real=True)
    fields, metric, products, boxes = sp.Matrix([q,r]), sp.eye(2), sp.eye(2), sp.zeros(2,1)
    if kind == "nonsymmetric_metric": metric[0,1] = 1
    elif kind == "nonsymmetric_products": products[0,1] = 1
    elif kind == "duplicate_fields": fields[1] = q
    elif kind == "bad_boxes": boxes = sp.zeros(3,1)
    else: metric[0,0] = sp.oo
    with pytest.raises(science.BulkScalarError):
        science.sigma_euler(metric, fields, products, boxes, sp.Integer(0))


@pytest.fixture(scope="module")
def ward_module():
    from . import verify_one_omega_bulk_scalar_ward_v1
    return verify_one_omega_bulk_scalar_ward_v1


@pytest.fixture(scope="module")
def ward(ward_module):
    return ward_module.ward_identity()


def test_generic_ward_identity_and_five_dimensional_stress_trace(ward):
    symbols = ward["symbols"]
    C, X, V, eta = (symbols[key] for key in ("C", "X", "V", "eta"))
    assert len(eta) == 5 and tuple(eta) == (-1,1,1,1,1)
    assert ward["stress"].shape == (5,5)
    assert ward["euler"].shape == (4,1)
    assert _zero(ward["divergence"] - symbols["v"].T * ward["euler"])
    assert _zero(ward["stress"] - ward["stress"].T)
    kinetic_norm = sum(C[a,b]*X[a,b] for a in range(4) for b in range(4))
    trace = sum(eta[mu]*ward["stress"][mu,mu] for mu in range(5))
    assert _zero(trace + sp.Rational(3,2)*kinetic_norm + 5*V)
    for a in range(4):
        for b in range(4):
            assert _zero(sp.diff(ward["euler"][a], symbols["dV"][b]) + (1 if a == b else 0))


@pytest.fixture(scope="module")
def ward_one_dimensional_case(ward):
    symbols = ward["symbols"]
    position, velocity, acceleration, mass = sp.symbols(
        "independent_position independent_first_jet independent_second_jet independent_mass", real=True)
    substitution = {symbol: 0 for symbol in symbols["Cs"].values()}
    substitution.update({symbol: 0 for symbol in symbols["dC"].values()})
    substitution.update({symbol: 0 for symbol in symbols["v"]})
    substitution.update({symbol: 0 for hessian in symbols["h"] for symbol in hessian})
    substitution.update({symbol: 0 for symbol in symbols["dV"]})
    substitution.update({symbols["Cs"][0,0]: 1, symbols["v"][0,1]: velocity,
                         symbols["h"][0][1,1]: acceleration,
                         symbols["V"]: mass**2*position**2/2,
                         symbols["dV"][0]: mass**2*position})
    return dict(substitution=substitution, position=position, velocity=velocity,
                acceleration=acceleration, mass=mass)


def test_ward_matches_one_dimensional_canonical_scalar_without_equations_imposed(ward, ward_one_dimensional_case):
    case = ward_one_dimensional_case
    q, v, b, mass = (case[key] for key in ("position", "velocity", "acceleration", "mass"))
    residual_euler = b - mass**2*q
    expected_stress = sp.diag(v**2/2+mass**2*q**2/2,
                              v**2/2-mass**2*q**2/2,
                              *[-v**2/2-mass**2*q**2/2]*3)
    substitution = case["substitution"]
    assert _zero(ward["euler"].xreplace(substitution)-sp.Matrix([residual_euler,0,0,0]))
    assert _zero(ward["stress"].xreplace(substitution)-expected_stress)
    assert _zero(ward["divergence"].xreplace(substitution)-sp.Matrix([0,v*residual_euler,0,0,0]))
    assert residual_euler != 0  # The free second jet has not been put on shell.


def test_missing_potential_stress_has_exact_nonzero_gradient_defect(ward):
    actual = ward["negative_control_residuals"]["missing_potential_in_stress"]
    expected = ward["symbols"]["v"].T * ward["symbols"]["dV"]
    assert _zero(actual - expected)
    assert not _zero(actual)


def test_wrong_stress_trace_and_euler_sign_fail_exact_one_dimensional_case(ward, ward_one_dimensional_case):
    case = ward_one_dimensional_case
    q, v, b, mass = (case[key] for key in ("position", "velocity", "acceleration", "mass"))
    negatives = ward["negative_control_residuals"]
    for key, expected in {
        "half_trace_in_stress": v*(b+mass**2*q)/2,
        "wrong_euler_sign": 2*v*(b-mass**2*q),
    }.items():
        actual = negatives[key].xreplace(case["substitution"])
        assert _zero(actual-sp.Matrix([0,expected,0,0,0]))
        assert not _zero(actual)


def test_generic_direct_variation_specializes_to_charter(ward_module, ward, model):
    assert _zero(ward_module.specialize_euler(ward, model))


@pytest.fixture(scope="module")
def receipt(ward_module):
    return ward_module.build_payload()


def test_receipt_domain_and_structure_without_claiming_a_fresh_derivation(ward_module, receipt):
    # This call intentionally checks only the validation layer; separate tests
    # below exercise the real fresh mathematical recomputation.
    ward_module.validate_payload(receipt, recompute=False)
    assert receipt["domain"]["spacetime_dimension"] == 5
    assert receipt["domain"]["fields"] == ["Omega", "phi1", "phi2", "phi3"]
    assert "Omega>0" in receipt["domain"]["assumptions"]
    assert "full coupled Hessian or stability" in receipt["not_established"]
    assert receipt["ward"]["residual"] == [["0"] for _ in range(5)]


def test_rehashed_equation_corruption_fails_fresh_symbolic_recomputation(ward_module, receipt):
    altered = copy.deepcopy(receipt)
    altered["equations"]["E_old"][0][0] = "(" + altered["equations"]["E_old"][0][0] + ")+1"
    altered["calculation_digest"] = ward_module._digest(
        {key:value for key,value in altered.items() if key != "calculation_digest"})
    with pytest.raises(ward_module.BulkWardError, match="fresh symbolic computation"):
        ward_module.validate_payload(altered)


def test_unresigned_matrix_corruption_fails_digest(ward_module, receipt):
    altered = copy.deepcopy(receipt)
    altered["equations"]["C_old"][0][1] = "(" + altered["equations"]["C_old"][0][1] + ")+1"
    with pytest.raises(ward_module.BulkWardError, match="digest"):
        ward_module.validate_payload(altered, recompute=False)


@pytest.mark.parametrize("bad", [None, [], {}, {"schema": "wrong"}])
def test_receipt_validator_rejects_wrong_type_or_schema(ward_module, bad):
    with pytest.raises(ward_module.BulkWardError):
        ward_module.validate_payload(bad)


def test_scientific_context_rejects_unproven_omega_domain():
    context = science.symbols_context()
    context["omega"] = sp.Symbol("unconstrained_Omega", real=True)
    with pytest.raises(science.BulkScalarError, match="positive"):
        science.derive_model(context)



def test_triplet_linearization_and_nonzero_fourth_order_material_potential(ward_module, model):
    result = ward_module.linear_triplet(model)
    o, phi, X, boxes, Z = (model[key] for key in ("omega", "phi", "X_old", "box_old", "Z"))
    expected = sp.Matrix([0, *[
        Z*(boxes[a+1]+3*phi[a]*boxes[0]/(2*o)-15*phi[a]*X[0,0]/(4*o**2))
        for a in range(3)]])
    assert _zero(result["linear_equations"]-expected)
    assert _zero(result["potential_amplitude_derivatives_0_to_3"])
    assert _zero(result["material_stress_linear_residual"])
    epsilon = sp.Symbol("independent_material_amplitude", real=True)
    material = (model["V_old"]-model["U"]).xreplace({field:epsilon*field for field in phi})
    fourth = sp.diff(material,epsilon,4).subs(epsilon,0)
    expected_fourth = 12*Z*model["M"]**2*o*sum(field**2 for field in phi)**2
    assert _zero(fourth-expected_fourth)
    assert not _zero(fourth)
