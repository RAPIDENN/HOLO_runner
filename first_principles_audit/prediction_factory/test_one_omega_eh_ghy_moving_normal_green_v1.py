"""Independent metric, immersion, ADM and moving-endpoint oracles.

No upstream constraint receipt is used as the expected momentum or shape
formula. The tests are deliberately restricted to the declared local
Green form and leave full coupled physical claims false.
"""
from copy import deepcopy
import json

import pytest
import sympy as sp

if __package__:
    from . import verify_one_omega_eh_ghy_moving_normal_green_v1 as gate
else:
    import verify_one_omega_eh_ghy_moving_normal_green_v1 as gate


@pytest.fixture(scope='module')
def model():
    return gate.derive_model()


@pytest.fixture(scope='module')
def payload():
    return gate.build_payload()


def sub_matrix(symbols, values):
    return {symbols[i, j]: values[i, j] for i in range(symbols.rows)
            for j in range(symbols.cols)}


def diagonal_metric_oracle():
    n = sp.Symbol('n_independent', real=True)
    a = tuple(map(sp.Rational, (1, -2, 3, -1)))
    c = (sp.Rational(2), sp.Rational(1), sp.Rational(-3), sp.Rational(4))
    signs = (-1, 1, 1, 1)
    gamma = sp.diag(*(signs[i] * (1 + 2 * a[i] * n + c[i] * n*n) for i in range(4)))
    metric = sp.diag(1, gamma)
    inverse = sp.diag(*(1 / metric[i, i] for i in range(5)))
    def derivative(expr, axis):
        return sp.diff(expr, n) if axis == 0 else sp.S.Zero
    Gamma = [[[sum(inverse[A, D] * (derivative(metric[D, B], C)
                                      + derivative(metric[D, C], B)
                                      - derivative(metric[B, C], D))
                    for D in range(5)) / 2
               for C in range(5)] for B in range(5)] for A in range(5)]
    G0 = [[[value.subs(n, 0) for value in row] for row in block] for block in Gamma]
    G1 = [[[sp.diff(value, n).subs(n, 0) for value in row] for row in block] for block in Gamma]
    Ricci = sp.zeros(5)
    for B in range(5):
        for D in range(5):
            Ricci[B, D] = sp.expand(sum(
                (G1[A][D][B] if A == 0 else 0) - (G1[A][A][B] if D == 0 else 0)
                + sum(G0[A][A][L] * G0[L][D][B] - G0[A][D][L] * G0[L][A][B]
                      for L in range(5)) for A in range(5)))
    return n, a, c, metric, inverse, Gamma, Ricci


def test_all_residuals_and_declared_scope(model):
    assert all(model['checks'].values())
    for part in ('geometry', 'palatini', 'shape', 'paired'):
        assert all(gate.zero(v) for v in model[part]['residuals'].values())
    assert 'arbitrary symmetric K' in model['geometry']['metric_jet_family']
    assert 'not a general curved-slice computer proof' in model['scope']['finite_geometry_oracle']


def test_Palatini_normal_covariant_derivative_is_not_zero(model):
    c, p = model['symbols'], model['palatini']
    gi = c['gamma'].inv()
    kh = sp.trace(gi * c['K'] * gi * c['h'])
    assert gate.zero(p['covariant_divergence_h_normal'] + kh)
    assert not gate.zero(p['covariant_divergence_h_normal'])
    assert gate.zero(p['normal_derivative_trace_h'] - sp.trace(gi * c['hp']) + 2 * kh)
    for i in range(4):
        assert sp.diff(p['EH_Palatini_current_normal'], c['hp'][i, i]) != 0
        assert sp.diff(p['combined_boundary_variation'], c['hp'][i, i]) == 0


def test_p_from_Palatini_matches_independently_differentiated_ADM_density(model):
    c = model['symbols']
    gi = c['gamma'].inv()
    velocity = gate.symmetric_matrix('independent_gamma_velocity')
    mixed = gi * velocity / 2
    L_ADM = c['M'] * (sp.trace(mixed)**2 - sp.trace(mixed * mixed) + c['R_gamma']) / 2
    # Ten independent entries, with the factor of two only for off-diagonal variations.
    independent_p = sp.Matrix(4, 4, lambda i, j:
                              sp.diff(L_ADM, velocity[i, j]) / (1 if i == j else 2))
    mapping = sub_matrix(velocity, 2 * c['K'])
    assert gate.zero(independent_p.subs(mapping) - model['palatini']['p_from_independent_metric_coefficients'])
    off_diagonal = model['palatini']['p_from_independent_metric_coefficients'][0, 1]
    assert sp.diff(model['palatini']['combined_boundary_variation'], c['h'][0, 1]) == 2 * off_diagonal


def test_5D_curvature_against_exact_anisotropic_coordinate_metric(model):
    n, a, coeff, metric, inverse, Gamma, Ricci = diagonal_metric_oracle()
    c = model['symbols']
    K = sp.diag(-a[0], a[1], a[2], a[3])
    L = sp.diag(-coeff[0], coeff[1], coeff[2], coeff[3])
    mapping = sub_matrix(c['K'], K)
    mapping.update(sub_matrix(c['L'], L))
    assert gate.zero(model['geometry']['ricci'].subs(mapping) - Ricci)
    direct_R = sp.trace(inverse.subs(n, 0) * Ricci)
    assert gate.zero(model['geometry']['R_bulk_from_metric'].subs(mapping) - direct_R)
    assert Ricci[0, 0] == -sum(coeff) + sum(v*v for v in a)
    assert direct_R != 0


def test_normal_and_second_fundamental_form_from_exact_moved_immersion(model):
    n, a, coeff, metric, inverse, Gamma, Ricci = diagonal_metric_oracle()
    eps = sp.Symbol('eps_independent', real=True)
    x = sp.symbols('t_ind x_ind y_ind z_ind', real=True)
    coords = (n, *x)
    t, xx, y, z = x
    f = 2 + t + xx + sp.Rational(3, 2)*t*t + xx*xx + 2*y*y + 3*z*z + t*z + xx*y
    df = sp.Matrix([sp.diff(f, xi) for xi in x])
    ddf = sp.hessian(f, x)
    level_gradient = sp.Matrix([1, *(-eps * df)])
    unit_normal = level_gradient / sp.sqrt((level_gradient.T * inverse * level_gradient)[0])
    nabla = sp.Matrix(5, 5, lambda A, B: sp.diff(unit_normal[B], coords[A])
                      - sum(Gamma[C][A][B] * unit_normal[C] for C in range(5)))
    origin = {xi: 0 for xi in x}
    direct_delta_K = sp.zeros(4)
    for i in range(4):
        for j in range(i, 4):
            # Pull back both covariant indices of nabla N to the actual graph.
            pull = (nabla[i+1, j+1] + eps*df[i]*nabla[0, j+1]
                    + eps*df[j]*nabla[i+1, 0] + eps*eps*df[i]*df[j]*nabla[0, 0])
            value = sp.diff(pull.subs(n, eps*f), eps).subs(eps, 0).subs(origin)
            direct_delta_K[i, j] = direct_delta_K[j, i] = sp.simplify(value)
    c = model['symbols']
    K = sp.diag(-a[0], a[1], a[2], a[3])
    L = sp.diag(-coeff[0], coeff[1], coeff[2], coeff[3])
    mapping = sub_matrix(c['K'], K)
    mapping.update(sub_matrix(c['L'], L))
    mapping.update(sub_matrix(c['ddf'], ddf.subs(origin)))
    mapping.update(dict(zip(c['df'], df.subs(origin))))
    mapping[c['f']] = f.subs(origin)
    assert gate.zero(model['shape']['induced_K_first_variation'].subs(mapping) - direct_delta_K)
    # The exact induced metric has an additional eps^2 df df term; it has no first-order contribution.
    induced = metric[1:5, 1:5].subs(n, eps*f) + eps*eps*df*df.T
    direct_delta_gamma = induced.diff(eps).subs(eps, 0).subs(origin)
    assert gate.zero(model['shape']['induced_metric_first_variation'].subs(mapping) - direct_delta_gamma)
    gamma_inverse = c['gamma'].inv()
    inverse_prime = -gamma_inverse * direct_delta_gamma * gamma_inverse
    direct_delta_trace = sp.trace(gamma_inverse * direct_delta_K + inverse_prime * K)
    assert gate.zero(model['shape']['trace_K_first_variation_including_inverse'].subs(mapping) - direct_delta_trace)
    frozen_trace = sp.trace(gamma_inverse * direct_delta_K)
    assert frozen_trace != direct_delta_trace


def test_warped_off_shell_shape_cancels_second_warp_derivative(model):
    c, w = model['symbols'], model['shape']['warped']
    a, ap = w['a'], w['a_prime']
    assert w['R_bulk'] == -8*ap - 20*a*a
    assert w['Ric_nn'] == -4*ap - 4*a*a
    # Direct domain plus GHY variation, using geometric trace k=4a.
    box = model['shape']['box_f_Lorentzian']
    direct = c['M']*c['f']*(-8*ap - 20*a*a)/2 + c['M']*(16*c['f']*a*a - box + 4*c['f']*ap)
    assert gate.zero(direct - w['shape'])
    assert sp.diff(w['shape'], ap) == 0
    assert w['BPS_or_Einstein_equations_used'] is False


def test_flat_variable_f_has_nonzero_Lorentzian_corner_current(model):
    c, shape = model['symbols'], model['shape']
    expected_box = -c['ddf'][0, 0] + sum(c['ddf'][i, i] for i in range(1, 4))
    assert shape['box_f_Lorentzian'] == expected_box
    assert sp.expand(shape['flat_shape'] + c['M'] * expected_box) == 0
    assert not gate.zero(shape['flat_shape'])
    assert shape['tangential_boundary_current'] == -c['M'] * c['gamma'].inv() * c['df']
    assert sp.diff(shape['flat_shape'], c['ddf'][0, 0]) == c['M']


def test_finite_determinant_volume_derivative_independent(model):
    c = model['symbols']
    eps = sp.Symbol('det_eps', real=True)
    K = sp.Matrix([[1, 2, 0, -1], [2, 3, 1, 0], [0, 1, -2, 1], [-1, 0, 1, 2]])
    gamma = c['gamma']
    # Differentiate the actual finite determinant for a non-diagonal perturbation.
    det_derivative = sp.diff((gamma + 2*eps*K).det(), eps).subs(eps, 0)
    independent = det_derivative / (2 * gamma.det())
    mapping = sub_matrix(c['K'], K)
    mapping[c['f']] = 1
    assert gate.zero(model['shape']['volume_first_variation_from_determinant'].subs(mapping) - independent)


def test_paired_outward_normal_and_wall_factors_from_direct_face_pairings(model):
    c, p = model['symbols'], model['paired']
    gamma, gi = c['gamma'], c['gamma'].inv()
    direct = 0
    for name, normal_sign in (('plus', -1), ('minus', 1)):
        Kout = normal_sign * c['K_' + name]
        kout = sp.trace(gi * Kout)
        pout = -c['M'] * (gi * Kout * gi - kout * gi) / 2
        Hout = c['M'] * (kout*kout - sp.trace(gi*Kout*gi*Kout) - c['R_gamma']) / 2
        direct += sum(pout[i, j] * c['h_Sigma'][i, j] for i in range(4) for j in range(4)) - normal_sign*c['f']*Hout
    assert gate.zero(direct - p['gravity_total'])
    assert sp.diff(p['H_grav_plus'] - p['H_grav_minus'], c['R_gamma']) == 0
    wall_metric = sum((gi*c['tau']*gi)[i, j] * c['h_Sigma'][i, j] for i in range(4) for j in range(4)) / 2
    assert gate.zero(p['wall_variation_once'] - wall_metric
                     - (c['wall_q_Euler'].T*c['delta_q'])[0] - c['E_T']*c['vartheta'])


def test_scalar_Legendre_from_actual_two_moving_integrals(model):
    n, eps, f, vp, vm, dq, C = sp.symbols('n eps f vp vm dq C', real=True)
    qp = vp*n + eps*(1-n)*(dq-f*vp)
    qm = vm*n + eps*(1+n)*(dq-f*vm)
    Lp = -C*sp.diff(qp, n)**2/2
    Lm = -C*sp.diff(qm, n)**2/2
    actual = sp.diff(sp.integrate(Lp, (n, eps*f, 1)) + sp.integrate(Lm, (n, -1, eps*f)), eps).subs(eps, 0)
    expected = C*(vp-vm)*dq - f*C*(vp*vp-vm*vm)/2
    assert sp.expand(actual - expected) == 0
    c = model['symbols']
    mapping = sub_matrix(c['scalar_metric'], sp.diag(C, 0, 0, 0))
    mapping.update(dict(zip(c['v_plus'], (vp, 0, 0, 0))))
    mapping.update(dict(zip(c['v_minus'], (vm, 0, 0, 0))))
    mapping.update(dict(zip(c['delta_q'], (dq, 0, 0, 0))))
    mapping[c['f']] = f
    assert gate.zero(model['paired']['scalar_Green_from_moving_endpoints'].subs(mapping) - expected)


def test_scalar_natural_rows_and_clock_are_retained(model):
    c, p = model['symbols'], model['paired']
    for i in range(4):
        assert gate.zero(sp.diff(p['Green_common_traces'], c['delta_q'][i]) - p['R_scalar'][i])
    assert sp.diff(p['Green_common_traces'], c['vartheta']) == c['E_T']
    assert not gate.zero((p['R_scalar'].T * c['delta_q'])[0])


def test_h0_is_mean_of_adjusted_bulk_traces_and_bulk_Eulers_remain(model):
    c, p = model['symbols'], model['paired']
    mapping = p['h_Sigma_substitution']
    dp = p['delta_g_bulk_plus'].subs(mapping, simultaneous=True)
    dm = p['delta_g_bulk_minus'].subs(mapping, simultaneous=True)
    assert gate.zero((dp + dm)/2 - c['h0'])
    assert gate.zero(dp - dm + 2*c['f']*(c['K_plus'] - c['K_minus']))
    assert not gate.zero(dp - dm)
    assert not gate.zero(p['bulk_Euler_f_coefficient_marker'])
    assert model['decision']['bulk_Euler_terms_discarded_off_shell'] is False
    assert 'actual volume integrals remain' in p['bulk_Euler_marker_scope']


def test_Israel_alone_does_not_set_normal_coefficient_to_zero(model):
    c, p = model['symbols'], model['paired']
    a = sp.Symbol('a_Israel', positive=True)
    mapping = sub_matrix(c['K_plus'], a*c['gamma'])
    mapping.update(sub_matrix(c['K_minus'], sp.zeros(4)))
    mapping.update(sub_matrix(c['tau'], 3*c['M']*a*c['gamma']))
    mapping.update({v: 0 for v in c['v_plus']})
    mapping.update({v: 0 for v in c['v_minus']})
    assert gate.zero(p['I'].subs(mapping))
    assert sp.expand(p['normal_coefficient_from_action_Green'].subs(mapping)) == 6*c['M']*a*a


def test_negative_controls_are_nonvacuous_and_general_gates_false(model):
    assert len(model['negative_controls']) == 11
    assert all(model['negative_controls'].values())
    positive = {'Dirichlet_momentum_derived_from_Palatini_and_GHY',
                'normal_shape_Green_identified_in_declared_chart',
                'independent_5D_immersion_metric_jets_checked',
                'paired_scalar_wall_natural_rows_retained',
                'normal_constraint_coefficient_linked_to_action_variation'}
    for name, value in model['decision'].items():
        assert value is (name in positive)


@pytest.mark.parametrize('mutation', ['N4', 'drop_scalar_rows', 'flip_momentum', 'omit_shape_edge'])
def test_rehashed_mutant_is_rejected_by_fresh_derivation(payload, mutation):
    bad = deepcopy(payload)
    if mutation == 'N4':
        bad['decision']['N4_JUNCTION_BENDING_pass'] = True
    elif mutation == 'drop_scalar_rows':
        bad['model']['paired']['R_scalar'] = [[0], [0], [0], [0]]
    elif mutation == 'flip_momentum':
        bad['model']['palatini']['p_from_independent_metric_coefficients'] = [[0]*4 for _ in range(4)]
    else:
        bad['model']['shape']['tangential_boundary_current'] = [[0], [0], [0], [0]]
    bad['calculation_digest'] = gate.canonical_digest({k: v for k, v in bad.items() if k != 'calculation_digest'})
    with pytest.raises(gate.MovingNormalGreenError, match='fresh derivation'):
        gate.validate_payload(bad)


def test_note_and_source_cannot_be_rebound(tmp_path):
    note = tmp_path/'note.md'
    note.write_bytes(gate.NOTE.read_bytes() + b'\n')
    with pytest.raises(gate.MovingNormalGreenError, match='note byte hash'):
        gate.load_sources(note_path=note)
    source = json.loads(gate.SOURCES['literal_v5_2'].read_bytes())
    source['invented_promotion'] = True
    path = tmp_path/'source.json'
    path.write_text(json.dumps(source))
    with pytest.raises(gate.MovingNormalGreenError, match='literal_v5_2 byte hash'):
        gate.load_sources(source_paths={'literal_v5_2': path})


def test_CLI_write_is_exclusive(tmp_path, monkeypatch, payload):
    monkeypatch.setattr(gate, 'build_payload', lambda: deepcopy(payload))
    path = tmp_path/'receipt.json'
    gate.main(['--write', str(path)])
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        gate.main(['--write', str(path)])
    assert path.read_bytes() == before
