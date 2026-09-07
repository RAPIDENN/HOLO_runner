"""Independent differential and representation checks for the brane Hessian.

Analytic toy Lagrangians test the jet/adjoint engine without using Claudia's
generator or its receipt.  The SO(2) tests use the spatial-metric Frobenius norm,
not a field partition copied from the old artifact.
"""
from __future__ import annotations

import copy
import hashlib
import json

import pytest
import sympy as sp

from . import one_omega_brane_hessian_algebra_v1 as algebra


OLD_NAMES = [
    "n", "N1", "N2", "N3", "H11", "H12", "H13", "H22", "H23", "H33",
    "tau", "pi1", "pi2", "pi3", "omega", "vphi1", "vphi2", "vphi3",
]
EXPECTED_GROUPS = {
    "scalar": ["n", "N3", "Htrace", "H33", "tau", "pi3", "omega", "vphi3"],
    "vector": ["N1", "N2", "Hxz", "Hyz", "pi1", "pi2", "vphi1", "vphi2"],
    "tensor": ["Hplus", "Hcross"],
}


@pytest.fixture(scope="module")
def context():
    return algebra.symbols_context()


def _fields(context):
    return dict(zip(context["field_names"], context["fields"]))


def _assert_equal(actual, expected):
    difference = actual - expected
    entries = list(difference) if isinstance(difference, sp.MatrixBase) else [difference]
    assert all(sp.simplify(entry) == 0 for entry in entries), difference


def _expected(context, entries):
    result = sp.zeros(18)
    indices = {name: index for index, name in enumerate(context["field_names"])}
    for (first, second), value in entries.items():
        result[indices[first], indices[second]] = value
    return result


def test_context_has_eighteen_distinct_real_fields(context):
    assert list(context["field_names"]) == OLD_NAMES
    assert len(context["fields"]) == len(set(context["fields"])) == 18
    assert len(context["coords"]) == 4
    for field in context["fields"]:
        assert tuple(field.args) == tuple(context["coords"])
    assert context["q"].is_real and context["w"].is_real
    assert context["parameters"]
    assert all(value.is_positive for value in context["parameters"].values())


@pytest.mark.parametrize("name", OLD_NAMES)
def test_each_field_mass_term_has_unit_diagonal(context, name):
    field = _fields(context)[name]
    actual = algebra.momentum_hessian(field**2 / 2, context)
    _assert_equal(actual, _expected(context, {(name, name): 1}))


@pytest.mark.parametrize("axis,sign", [(0, "w"), (3, "q")])
def test_squared_first_derivative_uses_formal_adjoint(context, axis, sign):
    field = _fields(context)["omega"]
    derivative = sp.diff(field, context["coords"][axis])
    actual = algebra.momentum_hessian(derivative**2 / 2, context)
    _assert_equal(actual, _expected(context, {("omega", "omega"): context[sign]**2}))


@pytest.mark.parametrize("axis,symbol,sign", [(0, "w", -1), (3, "q", 1)])
def test_mixed_odd_derivative_has_opposite_hermitian_entries(context, axis, symbol, sign):
    fields = _fields(context)
    lagrangian = fields["n"] * sp.diff(fields["omega"], context["coords"][axis])
    expected = sign * sp.I * context[symbol]
    actual = algebra.momentum_hessian(lagrangian, context)
    _assert_equal(actual, _expected(context, {
        ("n", "omega"): expected, ("omega", "n"): -expected,
    }))
    _assert_equal(actual, actual.conjugate().T)


def test_mixed_time_space_derivatives_have_minus_wq(context):
    fields = _fields(context)
    t, _, _, z = context["coords"]
    lagrangian = sp.diff(fields["n"], t) * sp.diff(fields["omega"], z)
    expected = -context["w"] * context["q"]
    _assert_equal(algebra.momentum_hessian(lagrangian, context), _expected(context, {
        ("n", "omega"): expected, ("omega", "n"): expected,
    }))


@pytest.mark.parametrize("mixed", [False, True])
def test_total_spatial_derivative_vanishes(context, mixed):
    fields = _fields(context)
    f = fields["n"]
    g = fields["omega"] if mixed else f
    divergence = sp.diff(f * g, context["coords"][3])
    _assert_equal(algebra.momentum_hessian(divergence, context), sp.zeros(18))


def test_field_times_its_derivative_vanishes(context):
    field = _fields(context)["omega"]
    lagrangian = field * sp.diff(field, context["coords"][3])
    _assert_equal(algebra.momentum_hessian(lagrangian, context), sp.zeros(18))


def test_second_derivative_squared_and_fourth_derivative_agree(context):
    field = _fields(context)["omega"]
    z = context["coords"][3]
    expected = _expected(context, {("omega", "omega"): context["q"]**4})
    for lagrangian in (sp.diff(field, z, 2)**2 / 2, field * sp.diff(field, z, 4) / 2):
        _assert_equal(algebra.momentum_hessian(lagrangian, context), expected)


@pytest.mark.parametrize("axis", [1, 2])
def test_transverse_jets_are_accepted_and_project_to_zero(context, axis):
    fields = _fields(context)
    coordinate = context["coords"][axis]
    z = context["coords"][3]
    lagrangian = (fields["n"]**2 / 2
                  + sp.diff(fields["omega"], coordinate)**2 / 2
                  + fields["n"] * sp.diff(fields["omega"], coordinate, z))
    _assert_equal(algebra.momentum_hessian(lagrangian, context),
                  _expected(context, {("n", "n"): 1}))


@pytest.mark.parametrize("kind", ["linear", "cubic", "linear_plus_quadratic", "sine"])
def test_nonquadratic_lagrangians_are_rejected(context, kind):
    field = _fields(context)["n"]
    expressions = {"linear": field, "cubic": field**3,
                   "linear_plus_quadratic": field + field**2, "sine": sp.sin(field)}
    with pytest.raises(ValueError):
        algebra.momentum_hessian(expressions[kind], context)


@pytest.mark.parametrize("kind", ["spatial", "temporal", "rational"])
def test_coordinate_dependent_coefficients_are_rejected(context, kind):
    t, x, _, z = context["coords"]
    field = _fields(context)["n"]
    coefficient = {"spatial": x, "temporal": sp.exp(t), "rational": 1/(1+z**2)}[kind]
    with pytest.raises(ValueError):
        algebra.momentum_hessian(coefficient * field**2, context)


def test_helicity_basis_is_invertible_and_has_eight_eight_two_fields(context):
    transform, names, groups = algebra.helicity_basis(context)
    assert transform.shape == (18, 18)
    assert len(names) == len(set(names)) == 18
    assert {key: [names[index] for index in indices] for key, indices in groups.items()} == EXPECTED_GROUPS
    assert sorted(sum((list(group) for group in groups.values()), [])) == list(range(18))
    assert sp.simplify(transform.det()) != 0
    _assert_equal(transform.inv() * transform, sp.eye(18))


def test_helicity_change_of_variables_keeps_both_tensor_polarizations(context):
    transform, names, _ = algebra.helicity_basis(context)
    new_symbols = {name: sp.Symbol("new_" + name) for name in names}
    transformed = transform * sp.Matrix([new_symbols[name] for name in names])
    old = dict(zip(context["field_names"], transformed))
    sqrt2 = sp.sqrt(2)
    expected = {
        "H11": (new_symbols["Htrace"] + new_symbols["Hplus"]) / sqrt2,
        "H22": (new_symbols["Htrace"] - new_symbols["Hplus"]) / sqrt2,
        "H12": new_symbols["Hcross"] / sqrt2,
        "H13": new_symbols["Hxz"] / sqrt2,
        "H23": new_symbols["Hyz"] / sqrt2,
    }
    for name in OLD_NAMES:
        _assert_equal(old[name], expected.get(name, new_symbols.get(name, 0)))


def test_new_metric_components_have_frobenius_unit_norm(context):
    transform, names, _ = algebra.helicity_basis(context)
    old_metric = _expected(context, {
        ("H11", "H11"): 1, ("H22", "H22"): 1, ("H33", "H33"): 1,
        ("H12", "H12"): 2, ("H13", "H13"): 2, ("H23", "H23"): 2,
    })
    expected = sp.zeros(18)
    for name in ("Htrace", "Hplus", "Hcross", "Hxz", "Hyz", "H33"):
        expected[names.index(name), names.index(name)] = 1
    _assert_equal(transform.T * old_metric * transform, expected)


def test_isotropic_metric_example_has_degenerate_tensor_block(context):
    fields = _fields(context)
    t, _, _, z = context["coords"]
    lagrangian = sp.Integer(0)
    for name, multiplicity in (("H11", 1), ("H22", 1), ("H33", 1),
                               ("H12", 2), ("H13", 2), ("H23", 2)):
        lagrangian += multiplicity * (sp.diff(fields[name], t)**2
                                     + sp.diff(fields[name], z)**2) / 2
    transform, names, _ = algebra.helicity_basis(context)
    result = transform.T * algebra.momentum_hessian(lagrangian, context) * transform
    tensor_indices = [names.index("Hplus"), names.index("Hcross")]
    _assert_equal(result.extract(tensor_indices, tensor_indices),
                  (context["w"]**2 + context["q"]**2) * sp.eye(2))
    others = [index for index in range(18) if index not in tensor_indices]
    _assert_equal(result.extract(tensor_indices, others), sp.zeros(2, 16))


def test_einstein_hilbert_khronon_terms_cancel_modulo_divergence(context):
    fields = _fields(context)
    t, *space = context["coords"]
    metric = sp.Matrix(3, 3, lambda i, j: fields[f"H{min(i,j)+1}{max(i,j)+1}"])
    shift = [fields[f"N{i+1}"] for i in range(3)]
    tau = fields["tau"]
    K0 = sp.Matrix(3, 3, lambda i, j: (
        sp.diff(metric[i, j], t) - sp.diff(shift[j], space[i])
        - sp.diff(shift[i], space[j])) / 2)
    K = K0 - sp.hessian(tau, space)
    R1 = sum(sp.diff(metric[i, j], space[i], space[j])
             for i in range(3) for j in range(3))
    R1 -= sum(sp.diff(metric.trace(), coordinate, 2) for coordinate in space)
    extra_K = sum(K[i,j]**2 - K0[i,j]**2 for i in range(3) for j in range(3))
    extra_K -= K.trace()**2 - K0.trace()**2
    cancellation = extra_K - sp.diff(tau, t) * R1
    _assert_equal(algebra.momentum_hessian(sp.expand(cancellation), context), sp.zeros(18))
    # Reversing the leaf-curvature correction must leave a mixed tau/metric term.
    wrong_sign = extra_K + sp.diff(tau, t) * R1
    result = algebra.momentum_hessian(sp.expand(wrong_sign), context)
    assert any(sp.simplify(entry) != 0 for entry in result)


def test_robin_parameter_y_is_distinct_from_coordinate_y(context):
    parameter_y = context["parameters"]["y"]
    coordinate_y = context["coords"][2]
    assert parameter_y != coordinate_y
    field = _fields(context)["vphi3"]
    _assert_equal(algebra.momentum_hessian(parameter_y * field**2 / 2, context),
                  _expected(context, {("vphi3", "vphi3"): parameter_y}))
    with pytest.raises(ValueError):
        algebra.momentum_hessian(coordinate_y * field**2 / 2, context)


@pytest.fixture(scope="module")
def audit():
    from . import verify_one_omega_brane_hessian_v1
    return verify_one_omega_brane_hessian_v1


def _source_document(audit, context):
    _, names, groups = audit.source_basis(context)
    return {"extended_hessian": {
        "fields": list(context["field_names"]),
        "helicity_field_order": list(names),
        "helicity_sets": copy.deepcopy(groups),
        "symbolic_matrix_helicity_basis": [["0" for _ in range(18)] for _ in range(18)],
    }}


def test_source_zero_matrix_compares_every_entry(audit, context):
    result = audit.compare_symbolic_matrix(_source_document(audit, context), sp.zeros(18), context)
    assert result == {"symbolic_entries_compared": 324, "symbolic_mismatches": 0}


def test_source_nonzero_matrix_uses_hs_hd_coordinate_normalization(audit, context):
    original = _expected(context, {("H11", "H11"): 2, ("H22", "H22"): 3})
    document = _source_document(audit, context)
    matrix = document["extended_hessian"]
    hs = matrix["helicity_field_order"].index("Hs")
    hd = matrix["helicity_field_order"].index("Hd")
    rows = matrix["symbolic_matrix_helicity_basis"]
    rows[hs][hs] = "5/4"
    rows[hd][hd] = "5"
    rows[hs][hd] = rows[hd][hs] = "-1/2"
    result = audit.compare_symbolic_matrix(document, original, context)
    assert result["symbolic_entries_compared"] == 324
    assert result["symbolic_mismatches"] == 0
    rows[hs][hd] = rows[hd][hs] = "-1"
    with pytest.raises(audit.HessianAuditError):
        audit.compare_symbolic_matrix(document, original, context)


@pytest.mark.parametrize("kind", ["diagonal", "off_diagonal", "symmetric_off_diagonal", "float_zero"])
def test_adulterated_matrix_is_rejected_even_when_square_and_parseable(audit, context, kind):
    document = _source_document(audit, context)
    rows = document["extended_hessian"]["symbolic_matrix_helicity_basis"]
    if kind == "diagonal":
        rows[0][0] = "1"
    elif kind == "off_diagonal":
        rows[0][1] = "q"
    elif kind == "symmetric_off_diagonal":
        rows[0][1] = rows[1][0] = "1"
    else:
        rows[0][0] = "0.0"
    with pytest.raises(audit.HessianAuditError):
        audit.compare_symbolic_matrix(document, sp.zeros(18), context)


@pytest.mark.parametrize("kind", ["missing_row", "short_row", "field_order", "basis_order", "wrong_helicity"])
def test_source_matrix_structure_and_basis_are_bound(audit, context, kind):
    document = _source_document(audit, context)
    matrix = document["extended_hessian"]
    if kind == "missing_row":
        matrix["symbolic_matrix_helicity_basis"].pop()
    elif kind == "short_row":
        matrix["symbolic_matrix_helicity_basis"][0].pop()
    elif kind == "field_order":
        matrix["fields"].reverse()
    elif kind == "basis_order":
        matrix["helicity_field_order"].reverse()
    else:
        matrix["helicity_sets"]["scalar"].append(matrix["helicity_sets"]["tensor"].pop())
    with pytest.raises(audit.HessianAuditError):
        audit.compare_symbolic_matrix(document, sp.zeros(18), context)


def test_expression_parser_keeps_parameter_y_and_derivative_coordinate_y_distinct(audit, context):
    fields = _fields(context)
    y = context["coords"][2]
    expected = context["parameters"]["y"] * sp.diff(fields["n"], y, 2)
    actual = audit.parse_expression("y*Derivative(n(t,x,y,z),(y,2))", context)
    _assert_equal(actual, expected)


@pytest.mark.parametrize("text", ["unknown_q+1", "n(z,x,y,t)", "Derivative(n(t,x,y,z),q)",
                                 "Derivative(n(t,x,y,z),(z,0))", "1/0", "q.real", "[q,w]"])
def test_expression_parser_rejects_unbound_or_malformed_input(audit, context, text):
    with pytest.raises(audit.HessianAuditError):
        audit.parse_expression(text, context)


@pytest.fixture(scope="module")
def canonical_blocks(audit, context):
    return audit.canonical_quadratic(context)


def test_canonical_wall_matches_independent_second_taylor_derivative(canonical_blocks, context):
    fields = _fields(context)
    parameters = context["parameters"]
    epsilon = sp.Symbol("independent_wall_expansion", real=True)
    metric = sp.Matrix(3, 3, lambda i, j: fields[f"H{min(i,j)+1}{max(i,j)+1}"])
    volume = (1 + epsilon * fields["n"]) * sp.sqrt((sp.eye(3) + epsilon * metric).det())
    omega = 1 + epsilon * fields["omega"]
    superpotential = 3 * parameters["M5c"] * parameters["k_inf"] * sp.exp(
        -parameters["G"] * omega**2 / (6 * parameters["M5c"]))
    action_density = -volume * (2 * superpotential + parameters["beta"] * (omega-1)**2 / 2)
    independent_coefficient = sp.diff(action_density, epsilon, 2).subs(epsilon, 0) / 2
    _assert_equal(canonical_blocks["wall"], sp.expand(independent_coefficient))


def test_canonical_solid_pure_shift_and_shear_coefficients(canonical_blocks, context):
    fields = _fields(context)
    parameters = context["parameters"]
    for surviving, expected in [
        ("N3", parameters["rho_X"] * parameters["v"]**2 * fields["N3"]**2 / 2),
        ("H12", -parameters["mu_X"] * parameters["v"]**4 * fields["H12"]**2 / 2),
    ]:
        substitutions = {field: 0 for name, field in fields.items() if name != surviving}
        actual = canonical_blocks["solid"].subs(substitutions, simultaneous=True).doit()
        _assert_equal(actual, expected)


def test_canonical_robin_is_stationary_under_linear_time_gauge(canonical_blocks, context):
    fields = _fields(context)
    t, *space = context["coords"]
    gauge_parameter = sp.Function("independent_time_gauge")(*context["coords"])
    epsilon = sp.Symbol("independent_gauge_amplitude", real=True)
    substitutions = {
        fields["n"]: fields["n"] + epsilon * sp.diff(gauge_parameter, t),
        fields["tau"]: fields["tau"] + epsilon * gauge_parameter,
    }
    transformed = canonical_blocks["robin"].subs(substitutions, simultaneous=True).doit()
    _assert_equal(transformed, canonical_blocks["robin"])
    for name in ("pi1", "pi2", "pi3", "H11", "H12", "H13", "H22", "H23", "H33"):
        assert not canonical_blocks["robin"].has(fields[name])
    mass_coefficient = sp.diff(canonical_blocks["robin"], fields["vphi3"], 2)
    _assert_equal(mass_coefficient, -context["parameters"]["kappa_hat"])


def test_canonical_blocks_keep_tadpoles_separate_without_losing_terms(canonical_blocks):
    complete = sum(canonical_blocks[key] for key in ("wall", "foliation", "solid", "robin"))
    _assert_equal(canonical_blocks["total"], complete)
    _assert_equal(canonical_blocks["gauge_free"], complete - canonical_blocks["tadpole"])
    assert canonical_blocks["tadpole"] != 0


@pytest.fixture(scope="module")
def reviewed_source_snapshot(audit, tmp_path_factory):
    """Freeze one source read; never follow a concurrently updated producer file.

    The temporary pin is local to this test process and covers the exact captured
    bytes.  It does not approve or publish a new production source pin.
    """
    raw = audit.SOURCE.read_bytes()
    source = json.loads(raw)
    snapshot = tmp_path_factory.mktemp("brane_hessian_source") / "source.json"
    snapshot.write_bytes(raw)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(audit, "EXPECTED_SOURCE_SHA256", hashlib.sha256(raw).hexdigest())
        receipt = audit.build_payload(snapshot)
        yield {"path": snapshot, "document": source, "receipt": receipt}


def _rebind_receipt_digest(audit, receipt):
    body = {key: value for key, value in receipt.items() if key != "calculation_digest"}
    receipt["calculation_digest"] = audit.canonical_digest(body)


def _changed_source_matrix(audit, reviewed_source_snapshot):
    source = copy.deepcopy(reviewed_source_snapshot["document"])
    rows = source["extended_hessian"]["symbolic_matrix_helicity_basis"]
    rows[0][1] = "(" + rows[0][1] + ")+1"
    source["calculation_digest"] = audit.canonical_digest(
        {key: source[key] for key in audit.SOURCE_DIGEST_KEYS})
    return source


def test_real_snapshot_receipt_recomputes_and_does_not_promote_gravity(audit, reviewed_source_snapshot):
    receipt = reviewed_source_snapshot["receipt"]
    assert receipt["comparison"] == {"symbolic_entries_compared": 324, "symbolic_mismatches": 0}
    assert receipt["decision"]["quadratic_brane_hessian_independently_reproduced_pass"] is True
    for key in ("bulk_variation_pass", "moving_embedding_variation_pass", "GHY_variation_pass",
                "nonlinear_Ward_identity_pass", "C4_HESSIAN_pass", "P4_full_same_action_pass", "B4_pass", "B5_pass"):
        assert receipt["decision"][key] is False
    audit.validate_payload(receipt, reviewed_source_snapshot["path"])


def test_rehashed_hessian_receipt_fails_real_mathematical_recomputation(audit, reviewed_source_snapshot):
    """No stubbed derivation: the actual verifier recomputes from the snapshot."""
    altered = copy.deepcopy(reviewed_source_snapshot["receipt"])
    entry = altered["hessian_normalized"]["nonzero_entries"][0]
    entry[2] = "(" + entry[2] + ")+1"
    _rebind_receipt_digest(audit, altered)
    with pytest.raises(audit.HessianAuditError, match="independent recomputation"):
        audit.validate_payload(altered, reviewed_source_snapshot["path"])


def test_rehashed_source_matrix_still_fails_immutable_byte_pin(audit, reviewed_source_snapshot, tmp_path):
    source = _changed_source_matrix(audit, reviewed_source_snapshot)
    path = tmp_path / "mutated_source.json"
    path.write_text(json.dumps(source, sort_keys=True, separators=(",", ":")))
    with pytest.raises(audit.HessianAuditError, match="byte hash"):
        audit.load_source(path)


def test_retagged_wrong_source_matrix_fails_independent_action_comparison(
        audit, reviewed_source_snapshot, tmp_path, monkeypatch):
    source = _changed_source_matrix(audit, reviewed_source_snapshot)
    raw = json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
    path = tmp_path / "retagged_source.json"
    path.write_bytes(raw)
    # Even if an operator changes both provenance tags, the actual matrix must
    # still agree with the independently translated action.
    monkeypatch.setattr(audit, "EXPECTED_SOURCE_SHA256", hashlib.sha256(raw).hexdigest())
    assert audit.load_source(path)["calculation_digest"] == source["calculation_digest"]
    with pytest.raises(audit.HessianAuditError, match="symbolic Hessian disagrees"):
        audit.build_payload(path)


@pytest.mark.parametrize("text", ["0/0", "0**-1", "1e309", "-1e309", "nan", "oo", "zoo"])
def test_expression_parser_rejects_nonfinite_values(audit, context, text):
    with pytest.raises(audit.HessianAuditError):
        audit.parse_expression(text, context)



def test_linear_foliation_is_nonzero_density_but_exact_spatial_divergence(audit, context):
    from sympy.calculus.euler import euler_equations

    result = audit.first_order_foliation(context)
    fields = _fields(context)
    _, x, y, z = context["coords"]
    mixed_curvature = 2 * (sp.diff(fields["H12"], x, y)
                           + sp.diff(fields["H13"], x, z)
                           + sp.diff(fields["H23"], y, z))
    transverse_diagonals = (sp.diff(fields["H11"], y, 2) + sp.diff(fields["H11"], z, 2)
                            + sp.diff(fields["H22"], x, 2) + sp.diff(fields["H22"], z, 2)
                            + sp.diff(fields["H33"], x, 2) + sp.diff(fields["H33"], y, 2))
    expected = context["parameters"]["Mb2"] * context["parameters"]["xi"] / 2
    expected *= mixed_curvature - transverse_diagonals
    density = audit.parse_expression(result["density"], context)
    current = [audit.parse_expression(value, context) for value in result["spatial_current"]]
    assert len(current) == 3
    divergence = sum(sp.diff(value, coordinate) for value, coordinate in zip(current, (x, y, z)))
    _assert_equal(density, expected)
    _assert_equal(density, divergence)
    assert sp.expand(density) != 0
    assert result["density_is_identically_zero"] is False
    assert result["density_minus_divergence"] == "0"
    assert result["integrated_first_variation_zero_for_compact_support"] is True
    assert set(result["Euler_derivatives"]) == set(OLD_NAMES)
    for value in result["Euler_derivatives"].values():
        _assert_equal(audit.parse_expression(value, context), sp.Integer(0))
    # SymPy's variational-calculus routine supplies an independent check of the
    # recorded zero Euler derivatives, rather than trusting their string values.
    assert euler_equations(density, list(context["fields"]), list(context["coords"])) == []
    for wrong_coefficient in (-1, sp.Rational(1, 2)):
        assert sp.simplify(density - wrong_coefficient * divergence) != 0


def test_receipt_validator_rejects_none_before_any_recomputation(audit, monkeypatch):
    def unexpected_recomputation(*args, **kwargs):
        raise AssertionError("a malformed receipt must not start a derivation")

    monkeypatch.setattr(audit, "build_payload", unexpected_recomputation)
    with pytest.raises(audit.HessianAuditError, match="dictionary"):
        audit.validate_payload(None)
