"""Independent ambient-jet, orientation, exterior-algebra and receipt controls."""
import copy
from fractions import Fraction
from itertools import combinations, permutations
from math import factorial

import pytest
import sympy as sp

from . import verify_one_omega_interface_constraint_identity_v1 as oracle


@pytest.fixture(scope='module')
def model():
    return oracle.derive_model()


def test_generic_normal_rows_match_mixed_tensor_principal_minors(model):
    sy = model['symbols']; inv = model['metric'].inv(); M, R = sy['M'], sy['R']
    assert len(sy['K_plus'].free_symbols) == len(sy['K_minus'].free_symbols) == 10
    assert model['metric'] != sp.diag(*model['metric'].diagonal())
    assert model['coframe'].det() == 1
    assert model['metric'] == model['coframe'].T * sp.diag(-1, 1, 1, 1) * model['coframe']
    for label, K, stress in [('plus', sy['K_plus'], sy['T_plus']),
                             ('minus', sy['K_minus'], sy['T_minus'])]:
        mixed = inv * K
        # Sum of principal 2-minors is independent of the trace-square implementation.
        gauss = M * sum(mixed[i, i]*mixed[j, j] - mixed[i, j]*mixed[j, i]
                        for i in range(4) for j in range(i+1, 4)) - M*R/2 - stress
        assert sp.expand(model['normal']['H_'+label] - gauss) == 0
    force = sp.trace((inv*sy['tau']) * (inv*(sy['K_plus']+sy['K_minus'])/2))
    force -= sy['T_plus'] - sy['T_minus']
    assert sp.expand(model['normal']['force_normal'] - force) == 0
    assert model['normal']['residual'] == 0


def _fraction(x):
    return Fraction(int(sp.numer(x)), int(sp.denom(x)))


def _ambient_ricci_from_metric_jets(metric, inverse, first, second):
    """Coordinate definition of Ricci, without Gauss/Codazzi or production helpers."""
    n = 5; zero = Fraction(0)
    def dg(c, a, b): return first.get((c, a, b), zero)
    def ddg(d, c, a, b): return second.get((d, c, a, b), zero)
    dinv = [[[ -sum(inverse[a][i]*dg(d, i, j)*inverse[j][b]
                       for i in range(n) for j in range(n))
                for b in range(n)] for a in range(n)] for d in range(n)]
    Gamma = [[[sum(inverse[a][e]*(dg(b, e, c)+dg(c, e, b)-dg(e, b, c))
                       for e in range(n))/2 for c in range(n)] for b in range(n)] for a in range(n)]
    dGamma = [[[[sum(dinv[d][a][e]*(dg(b, e, c)+dg(c, e, b)-dg(e, b, c))
                        + inverse[a][e]*(ddg(d, b, e, c)+ddg(d, c, e, b)-ddg(d, e, b, c))
                        for e in range(n))/2 for c in range(n)] for b in range(n)]
                for a in range(n)] for d in range(n)]
    return [[sum(dGamma[a][a][i][j] - dGamma[j][a][i][a] for a in range(n))
             + sum(Gamma[a][a][b]*Gamma[b][i][j] - Gamma[a][j][b]*Gamma[b][i][a]
                   for a in range(n) for b in range(n)) for j in range(n)] for i in range(n)]


def test_gauss_and_codazzi_are_actual_ambient_Einstein_projections(model):
    gamma = model['metric']; inv = gamma.inv()
    K = sp.Matrix([[3, 1, -2, 1], [1, -1, 2, 0], [-2, 2, 4, -1], [1, 0, -1, 2]])/7
    Q = sp.Matrix(4, 4, lambda a, b: sp.Rational(2*a+2*b+3, 13))
    jets = [sp.Matrix(4, 4, lambda a, b: sp.Rational((d+2)*(a+b+1)+(-1)**(a+b), 10+d))
            for d in range(4)]
    metric5 = [[_fraction(gamma[a, b]) if a < 4 and b < 4 else Fraction(int(a == b))
                for b in range(5)] for a in range(5)]
    inverse5 = [[_fraction(inv[a, b]) if a < 4 and b < 4 else Fraction(int(a == b))
                 for b in range(5)] for a in range(5)]
    first, second = {}, {}
    for a in range(4):
        for b in range(4):
            first[4, a, b] = 2*_fraction(K[a, b])
            second[4, 4, a, b] = 2*_fraction(Q[a, b])
            for d in range(4):
                second[4, d, a, b] = second[d, 4, a, b] = 2*_fraction(jets[d][a, b])
    ricci = _ambient_ricci_from_metric_jets(metric5, inverse5, first, second)
    R5 = sum(inverse5[a][b]*ricci[a][b] for a in range(5) for b in range(5))
    Gnn = ricci[4][4]-R5/2
    reference = oracle.normal_rows(gamma, K, sp.zeros(4), sp.zeros(4), 0, 0, M=1, R=0)
    assert Gnn == reference['H_plus']
    assert Gnn != 0
    tan = oracle.tangential_rows(gamma, jets, [sp.zeros(4)]*4, [sp.zeros(4)]*4,
                                sp.zeros(4, 1), sp.zeros(4, 1), M=1)
    assert sp.Matrix([ricci[4][i] for i in range(4)]) == tan['E_n_plus']
    assert any(ricci[4][i] != 0 for i in range(4))


def test_reversing_normal_and_labels_preserves_Israel_and_reverses_force(model):
    sy = model['symbols']
    reverse = {sy['K_plus'][i,j]: -sy['K_minus'][i,j] for i in range(4) for j in range(i,4)}
    reverse.update({sy['K_minus'][i,j]: -sy['K_plus'][i,j] for i in range(4) for j in range(i,4)})
    reverse.update({sy['T_plus']:sy['T_minus'], sy['T_minus']:sy['T_plus']})
    row = model['normal']
    assert all(sp.expand(x) == 0 for x in row['Israel_residual'].subs(reverse, simultaneous=True)-row['Israel_residual'])
    assert sp.expand(row['force_normal'].subs(reverse, simultaneous=True)+row['force_normal']) == 0
    assert row['force_normal'] != 0


def test_Israel_without_Hamiltonian_does_not_imply_normal_force_zero(model):
    g = model['metric']; a, M = sp.symbols('a M', positive=True)
    result = oracle.normal_rows(g, a*g, sp.zeros(4), 3*M*a*g, 0, 0, M=M, R=0)
    assert result['Israel_residual'].applyfunc(sp.expand) == sp.zeros(4)
    assert sp.expand(result['force_normal']) == 6*M*a*a
    assert sp.expand(result['H_plus']-result['H_minus']) == 6*M*a*a


def test_noncommon_curvature_and_Israel_sign_mutants_are_detected(model):
    row = model['normal']; M = model['symbols']['M']; dr = sp.Symbol('R_jump', real=True)
    wrong_Hplus = row['H_plus']-M*dr/2
    reconstructed = wrong_Hplus-row['H_minus']-oracle.double_contract(
        row['Israel_residual'], row['mean_K'], row['inverse_metric'])
    assert sp.expand(row['force_normal']-reconstructed) == M*dr/2
    assert all(value != 0 for value in model['negative_controls']['normal'].values())


def test_tangential_rows_keep_every_flux_and_derivative(model):
    row = model['tangential']; sy = model['symbols']; inverse = model['metric'].inv()
    # Divergence of mixed tau, contracted one index at a time, is independently reconstructed.
    div_tau = sp.Matrix([sum((inverse*sy['tau_jets'][a])[a,b] for a in range(4)) for b in range(4)])
    assert (row['div_tau']-div_tau).applyfunc(sp.expand) == sp.zeros(4,1)
    assert row['residual'] == sp.zeros(4,1)
    assert model['negative_controls']['tangential_wrong_flux'] == -2*(sy['T_n_plus']-sy['T_n_minus'])


def _permutation_sign(p):
    # Cycle decomposition, independent of the production cross-inversion count.
    visited = set(); cycles = 0
    for i in range(len(p)):
        if i not in visited:
            cycles += 1; j = i
            while j not in visited:
                visited.add(j); j = p[j]
    return (-1)**(len(p)-cycles)


def _component(form, indices):
    if len(set(indices)) != len(indices): return 0
    ordered = tuple(sorted(indices))
    return _permutation_sign([ordered.index(i) for i in indices])*form.get(ordered, 0)


def _reference_wedge(left, right, p, q):
    answer = {}
    for key in combinations(range(5), p+q):
        total = sum(_permutation_sign([key.index(i) for i in perm])
                    *_component(left, perm[:p])*_component(right, perm[p:]) for perm in permutations(key))
        value = Fraction(total, factorial(p)*factorial(q))
        if value: answer[key] = value
    return answer


def _reference_interior(form, vector, degree):
    answer = {}
    for key in combinations(range(5), degree-1):
        value = sum(vector[a]*_component(form, (a,)+key) for a in range(5))
        if value: answer[key] = value
    return answer


def _reference_sum(forms):
    keys = {key for form in forms for key in form}
    return {key: val for key in keys if (val := sum(form.get(key,0) for form in forms)) != 0}


def test_BF_three_colors_against_full_antisymmetrization():
    B = [{key: Fraction((color+1)*(sum(key)+2)+(-1)**key[0], color+3)
          for key in combinations(range(5),3)} for color in range(3)]
    F = [{key: Fraction((color+2)*(sum(key)+1)-(-1)**key[1], color+4)
          for key in combinations(range(5),2)} for color in range(3)]
    vector = [Fraction(x,7) for x in [2,-1,3,1,-2]]
    result = oracle.bf_identity(B,F,vector)
    density = _reference_sum([_reference_wedge(b,f,3,2) for b,f in zip(B,F)])
    transgression = _reference_interior(density,vector,5)
    minus_theta = _reference_sum([_reference_wedge(b,_reference_interior(f,vector,2),3,1) for b,f in zip(B,F)])
    expected = _reference_sum([_reference_wedge(_reference_interior(b,vector,3),f,2,2) for b,f in zip(B,F)])
    assert density == result['density']
    assert transgression == result['transgression']
    assert expected == result['Legendre_normal_form']
    assert expected == _reference_sum([transgression, minus_theta])
    assert expected and result['wrong_theta_sign_residual'] and result['double_transgression_residual']
    assert not result['residual']


def test_BF_normal_term_is_off_shell_and_quadratic_at_the_empty_vacuum():
    a,b,c,d = sp.symbols('a b c d',real=True)
    result = oracle.bf_identity([{(0,1,4):a,(2,3,4):b}], [{(0,1):c,(2,3):d}], [0,0,0,0,1])
    assert sp.expand(result['Legendre_normal_form'][(0,1,2,3)]) == a*d+b*c
    epsilon = sp.Symbol('epsilon',real=True)
    scaled = result['Legendre_normal_form'][(0,1,2,3)].subs({a:epsilon*a,b:epsilon*b,c:epsilon*c,d:epsilon*d}, simultaneous=True)
    assert sp.diff(scaled,epsilon).subs(epsilon,0) == 0
    assert sp.expand(scaled-epsilon**2*(a*d+b*c)) == 0
    assert result['expected_B_Euler_pairing'][(0,1,2,3)].subs({c:0,d:0}) == 0


@pytest.fixture(scope='module')
def payload():
    return oracle.build_payload()


@pytest.mark.parametrize('mutation', ['normal_coefficient','BF_coefficient','N4_promotion','N7_promotion'])
def test_receipt_rejects_resigned_mathematical_or_scope_corruption(payload,mutation):
    changed = copy.deepcopy(payload)
    if mutation == 'normal_coefficient': changed['model']['normal']['residual'] = '1'
    elif mutation == 'BF_coefficient':
        values = changed['model']['BF']['Legendre_normal_form']; key = next(iter(values))
        values[key] = '('+values[key]+')+1'
    elif mutation == 'N4_promotion': changed['decision']['N4_JUNCTION_BENDING_pass'] = True
    else: changed['decision']['N7_LINEAR_REDUCTION_pass'] = True
    changed['calculation_digest'] = oracle.canonical_digest({k:v for k,v in changed.items() if k!='calculation_digest'})
    with pytest.raises(oracle.ConstraintIdentityError,match='fresh derivation'):
        oracle.validate_payload(changed)


def test_source_alteration_cannot_be_authorized_by_retagging_its_content(tmp_path):
    import json
    source = json.loads(oracle.SOURCE.read_text())
    source['Green_form_certificate']['natural_interface_equations']['Israel'] = 'wrong sign'
    source['replacement_digest'] = oracle.canonical_digest(source)
    path = tmp_path/'changed_source.json'; path.write_text(json.dumps(source))
    with pytest.raises(oracle.ConstraintIdentityError,match='byte pin'):
        oracle.load_source(path)


def test_schema_and_digest_fail_before_recomputation(payload):
    with pytest.raises(oracle.ConstraintIdentityError,match='schema'):
        oracle.validate_payload(None)
    changed = copy.deepcopy(payload); changed['checks']['normal_constraint_Israel_identity'] = False
    with pytest.raises(oracle.ConstraintIdentityError,match='digest'):
        oracle.validate_payload(changed)
