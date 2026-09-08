"""Independent tuple-form, radial-jet, sign, domain and receipt tests.

These tests do not import old BF producers.  Their direct exterior derivative
uses ordered tuples/permutation inversions, rather than the verifier's bit
insertion algorithm.  Radial coefficient functions are differentiated here.
"""
from copy import deepcopy
from itertools import combinations
import json

import pytest
import sympy as sp

if __package__:
    from . import verify_one_omega_bf_rhp_quotient_v1 as gate
else:
    import verify_one_omega_bf_rhp_quotient_v1 as gate


def ordered_product(left, right):
    """Tuple permutation oracle for exterior multiplication."""
    word = tuple(left) + tuple(right)
    if len(set(word)) != len(word):
        return 0, ()
    inversions = sum(word[i] > word[j] for i in range(len(word))
                     for j in range(i+1, len(word)))
    return (-1)**inversions, tuple(sorted(word))


def mask(indices):
    return sum(2**i for i in indices)


def coefficients_to_matrix(values, dimension=5):
    out = sp.zeros(2**dimension, 1)
    for indices, coefficient in values.items():
        out[mask(indices)] = coefficient
    return out


def direct_d(values, r, s, momenta):
    out = {}
    for indices, coefficient in values.items():
        derivatives = (s*coefficient, *(sp.I*k*coefficient for k in momenta),
                       sp.diff(coefficient, r))
        for axis, value in enumerate(derivatives):
            sign, target = ordered_product((axis,), indices)
            if sign:
                out[target] = out.get(target, 0)+sign*value
    return {indices: sp.expand(value) for indices, value in out.items()
            if sp.expand(value) != 0}


@pytest.fixture(scope='module')
def model():
    return gate.derive_model()


@pytest.fixture(scope='module')
def payload():
    return gate.build_payload()


def test_all_basis_wedges_and_contractions_against_tuple_oracle():
    for dimension in (4, 5):
        for axis in range(dimension):
            wedge = gate.wedge_matrix(axis, dimension)
            contraction = gate.contraction_matrix(axis, dimension)
            for degree in range(dimension+1):
                for indices in combinations(range(dimension), degree):
                    column = mask(indices)
                    expected_wedge = sp.zeros(2**dimension, 1)
                    sign, target = ordered_product((axis,), indices)
                    if sign:
                        expected_wedge[mask(target)] = sign
                    assert wedge[:, column] == expected_wedge
                    expected_contraction = sp.zeros(2**dimension, 1)
                    if axis in indices:
                        position = indices.index(axis)
                        remaining = indices[:position]+indices[position+1:]
                        expected_contraction[mask(remaining)] = (-1)**position
                    assert contraction[:, column] == expected_contraction


@pytest.mark.parametrize('degree', range(6))
def test_cartan_all_degrees_with_radial_functions(model, degree):
    ctx = model['symbols']
    r, s, momenta, Dr = ctx['r'], ctx['s'], ctx['momenta'], ctx['Dr']
    values = {indices: (j+1)*r**3+(j+2)*r+sp.Function(f'f{degree}_{j}')(r)
              for j, indices in enumerate(combinations(range(5), degree))}
    form = coefficients_to_matrix(values)
    direct = coefficients_to_matrix(direct_d(values, r, s, momenta))
    actual = gate.apply_radial_operator(model['d'], form, r, Dr)
    assert all(sp.expand(x) == 0 for x in actual-direct)
    dh = gate.apply_radial_operator(model['d'], model['h']*form, r, Dr)
    hd = model['h']*direct
    assert all(sp.expand(x) == 0 for x in dh+hd-form)
    # Derivatives of radial coefficients have not been replaced by D_r values.
    assert not any(x.has(Dr) for x in actual)


def test_radial_orientation_has_independent_nonconstant_witness(model):
    ctx = model['symbols']
    r, Dr = ctx['r'], ctx['Dr']
    scalar = sp.zeros(32, 1)
    scalar[0] = r**3
    derivative = gate.apply_radial_operator(model['d'], scalar, r, Dr)
    assert derivative[16] == 3*r**2
    wrong = model['d']-2*Dr*gate.wedge_matrix(4)
    wrong_result = gate.apply_radial_operator(wrong, scalar, r, Dr)
    assert sp.expand(wrong_result[16]-derivative[16]) == -6*r**2
    # Cartan alone does not fix the radial orientation; the jet test does.
    assert all(sp.expand(x) == 0 for x in wrong*model['h']+model['h']*wrong-sp.eye(32))


def test_UV_trace_discards_dr_and_commutes_with_boundary_operators(model):
    P = model['UV_pullback']
    for indices in combinations(range(5), 3):
        basis = coefficients_to_matrix({indices: 1})
        expected = sp.zeros(16, 1)
        if 4 not in indices:
            expected[mask(indices)] = 1
        assert P*basis == expected
    assert all(sp.expand(x) == 0 for x in P*model['d']-model['d_boundary']*P)
    assert all(sp.expand(x) == 0 for x in P*model['h']-model['h_boundary']*P)


def test_closed_A_and_B_are_removed_with_the_declared_distinct_signs(model):
    ctx = model['symbols']
    r, s, momenta, Dr = ctx['r'], ctx['s'], ctx['momenta'], ctx['Dr']
    alpha = coefficients_to_matrix(direct_d({(): r**2+1}, r, s, momenta))
    b = coefficients_to_matrix(direct_d({(1, 2): r**3+2*r}, r, s, momenta))
    for form, parameter, sign in ((alpha, model['h']*alpha, -1),
                                  (b, -model['h']*b, 1)):
        assert all(sp.expand(x) == 0 for x in gate.apply_radial_operator(model['d'], form, r, Dr))
        change = gate.apply_radial_operator(model['d'], parameter, r, Dr)
        assert all(sp.expand(x) == 0 for x in form+sign*change)
        assert any(sp.expand(x) != 0 for x in form-sign*change)


def test_iota_gauge_relation_and_common_shift_traces(model):
    ctx = model['symbols']
    r, s, momenta, Dr = ctx['r'], ctx['s'], ctx['momenta'], ctx['Dr']
    chi = sp.zeros(16, 1)
    chi[0] = sp.Symbol('chi')
    alpha = coefficients_to_matrix(direct_d({(): r**3+5}, r, s, momenta))
    trace = (model['UV_pullback']*alpha).subs(r, 0)
    boundary_alpha = trace-model['d_boundary']*chi
    epsilon_bulk = (model['UV_pullback']*model['h']*alpha).subs(r, 0)
    epsilon_Q = model['h_boundary']*boundary_alpha
    assert all(sp.expand(x) == 0 for x in epsilon_bulk-epsilon_Q-chi)
    assert all(sp.expand(x) == 0 for x in chi+epsilon_Q-epsilon_bulk)
    b_plus = coefficients_to_matrix({(0, 1, 2): r+1, (1, 2, 4): r**2})
    b_minus = coefficients_to_matrix({(0, 1, 2): 2*r+1, (1, 2, 4): 3*r**2})
    shift_plus = (-model['UV_pullback']*model['h']*b_plus).subs(r, 0)
    shift_minus = (-model['UV_pullback']*model['h']*b_minus).subs(r, 0)
    assert shift_plus == shift_minus


def test_reducibility_chain_has_correct_form_degrees(model):
    for degree in (0, 1, 2):
        for indices in combinations(range(5), degree):
            basis = coefficients_to_matrix({indices: 1})
            first = model['d']*basis
            for row, value in enumerate(first):
                if value != 0:
                    assert row.bit_count() == degree+1
            assert all(sp.expand(x) == 0 for x in model['d']*first)


def test_oriented_Green_and_shift_witnesses_against_ordered_forms(model):
    sign_green, target = ordered_product((1, 2, 3), (0,))
    assert target == (0, 1, 2, 3) and sign_green == -1
    sign_shift, _ = ordered_product((1, 2), (0, 3))
    assert sign_shift == 1
    assert -(1-1)*sign_green == 0
    assert -(1+1)*sign_green == 2
    assert (1-1)*sign_shift == 0
    assert (1+1)*sign_shift == 2
    assert model['negative_witnesses']['both_Green_incidences_positive'] == 2
    assert model['negative_witnesses']['both_shift_incidences_positive'] == 2


def test_static_homotopy_is_excluded_and_radial_constant_is_closed():
    with pytest.raises(gate.BFQuotientError, match='nonzero s'):
        gate.homotopy_matrix(0)
    # At s=k=0 the constant zero-form is closed, with no degree -1 primitive.
    r = sp.Symbol('r', real=True)
    assert direct_d({(): sp.Integer(1)}, r, 0, (0, 0, 0)) == {}


@pytest.mark.parametrize('axis,dimension', [(True, 5), (-1, 5), (5, 5), (0, 6), (0, 0)])
def test_invalid_exterior_dimensions_are_rejected(axis, dimension):
    with pytest.raises(gate.BFQuotientError):
        gate.wedge_matrix(axis, dimension)
    with pytest.raises(gate.BFQuotientError):
        gate.contraction_matrix(axis, dimension)


def test_operator_rejects_radial_dependent_coefficients_and_inverse_Dr():
    ctx = gate.symbols_context()
    for value in (ctx['r']*ctx['Dr'], 1/ctx['Dr']):
        with pytest.raises(gate.BFQuotientError):
            gate.apply_radial_operator(sp.Matrix([[value]]), sp.Matrix([ctx['r']]), ctx['r'])


def test_model_controls_and_explicit_scope(payload):
    assert all(payload['checks'].values())
    assert all(payload['negative_controls'].values())
    assert len(payload['negative_controls']) == 8
    decision = payload['decision']
    assert decision['linear_relative_BF_RHP_quotient_trivial_on_h_stable_domain'] is True
    for key in ('universal_normalizable_domain_certified', 'static_s_zero_quotient_certified',
                'global_BF_edge_mode_absence_pass', 'A_minus_frame_connection_edge_sector_eliminated',
                'complete_BV_BFV_boundary_complex_pass', 'C2_BRST_pass',
                'nonlinear_BF_quotient_certified', 'full_N7', 'full_P4', 'B4', 'B5'):
        assert decision[key] is False
    assert payload['scope']['no_uniform_s_to_zero_bound'] is True
    assert payload['scope']['A_Sigma_independent_of_Levi_Civita_connection'] is True


def test_receipt_recomputes_fresh(payload):
    gate.validate_payload(deepcopy(payload))


@pytest.mark.parametrize('mutation', ['false_promotion', 'operator_sign', 'domain_erased'])
def test_rehashed_receipt_mutants_fail_fresh_derivation(payload, mutation):
    bad = deepcopy(payload)
    if mutation == 'false_promotion':
        bad['decision']['global_BF_edge_mode_absence_pass'] = True
    elif mutation == 'operator_sign':
        bad['model']['h']['entries'][0][2] = '0'
    else:
        bad['scope']['required_function_domain'] = 'every normalizable field without gauge restrictions'
    bad['calculation_digest'] = gate.canonical_digest({k:v for k,v in bad.items() if k != 'calculation_digest'})
    with pytest.raises(gate.BFQuotientError, match='fresh derivation'):
        gate.validate_payload(bad)


def test_source_hash_mutation_and_rebound_action_are_rejected(tmp_path):
    wrong_note = tmp_path/'note.md'
    wrong_note.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.BFQuotientError, match='note byte hash'):
        gate.load_sources(note_path=wrong_note)
    candidate = json.loads(gate.CANDIDATE.read_bytes())
    candidate['exact_classical_charter']['exact_action']['BF'] = 'minus the canonical BF action'
    candidate['calculation_digest'] = gate.canonical_digest(candidate)
    wrong_candidate = tmp_path/'candidate.json'
    wrong_candidate.write_text(json.dumps(candidate))
    with pytest.raises(gate.BFQuotientError, match='candidate byte hash'):
        gate.load_sources(candidate_path=wrong_candidate)


def test_duplicate_and_nonfinite_json_are_rejected():
    for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'[]'):
        with pytest.raises(gate.BFQuotientError):
            gate._read_json(raw)


def test_cli_write_is_exclusive_without_overwriting(tmp_path, monkeypatch, payload):
    # The CLI persistence contract is tested without recalculating a model.
    monkeypatch.setattr(gate, 'build_payload', lambda: deepcopy(payload))
    target = tmp_path/'receipt.json'
    gate.main(['--write', str(target)])
    before = target.read_bytes()
    with pytest.raises(FileExistsError):
        gate.main(['--write', str(target)])
    assert target.read_bytes() == before
