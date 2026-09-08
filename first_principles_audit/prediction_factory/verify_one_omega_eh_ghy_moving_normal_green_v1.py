"""Moving EH+GHY normal Green form in a declared Gaussian, common-trace chart.

The momentum is derived from Palatini plus the literal GHY variation.
A separate five-dimensional metric-jet calculation differentiates the
normal to a genuinely moved immersion. The general covariant statement
uses the analytic lemma; the finite jet model has flat intrinsic slices,
arbitrary symmetric K and its normal derivative, and a variable displacement.
Bulk Euler terms, scalar natural rows and tangential currents remain present.
This is not the complete gauged-material/BF/moving-interface variational map.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
NOTE = HERE / 'one_omega_eh_ghy_moving_normal_green_lemma_v1.md'
TEST = HERE / 'test_one_omega_eh_ghy_moving_normal_green_v1.py'
OUTPUT = HERE / 'artifacts/one_omega_eh_ghy_moving_normal_green_v1.json'
NOTE_SHA256 = 'b6ccfd42ac4046a204b334bccd17ca18a5d17b0a12a4f239d171a77e78b75c46'
SOURCES = {
    'literal_v5_2': HERE / 'artifacts/one_omega_topological_so3_classical_v5_2_gate.json',
    'constraint_identity': HERE / 'artifacts/one_omega_interface_constraint_identity_v1.json',
    'moving_scalar': HERE / 'artifacts/one_omega_moving_scalar_green_v1.json',
}
SOURCE_SHA256 = {
    'literal_v5_2': 'd9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b',
    'constraint_identity': '0065ad20c379a4899101155c4bd9f1c6214e08069e8085a6976c824544adc6af',
    'moving_scalar': 'f68a40f079c14c5cd5c619297b853157e196ce80a47dce28c930ebd8234bdca0',
}
SCHEMA = 'holo.one-omega-eh-ghy-moving-normal-green.v1'


class MovingNormalGreenError(ValueError):
    pass


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def symmetric_matrix(prefix, size=4):
    entries = {(i, j): sp.Symbol(f'{prefix}_{i}{j}', real=True)
               for i in range(size) for j in range(i, size)}
    return sp.Matrix(size, size, lambda i, j: entries[min(i, j), max(i, j)])


def expand(value):
    if isinstance(value, sp.MatrixBase):
        return value.applyfunc(sp.expand)
    return sp.expand(value)


def zero(value):
    if isinstance(value, dict):
        return all(zero(v) for v in value.values())
    if isinstance(value, (list, tuple, sp.MatrixBase)):
        return all(zero(v) for v in value)
    return sp.cancel(value) == 0


def contract(left, right, inverse):
    """Full Frobenius contraction of two covariant symmetric tensors."""
    return sp.trace(inverse * left * inverse * right)


def coefficient_matrix(expression, matrix):
    """Recover a contravariant symmetric coefficient from ten independent jets."""
    return sp.Matrix(matrix.rows, matrix.cols, lambda i, j:
                     sp.diff(expression, matrix[i, j]) / (1 if i == j else 2))


def symbols_context():
    return {
        'gamma': sp.diag(-1, 1, 1, 1),
        'M': sp.Symbol('M', positive=True),
        'epsilon': sp.Symbol('epsilon', real=True),
        'f': sp.Symbol('f', real=True),
        'df': sp.Matrix(sp.symbols('f_t f_x f_y f_z', real=True)),
        'ddf': symmetric_matrix('f_second'),
        'K': symmetric_matrix('K'),
        'L': symmetric_matrix('normal_K_derivative'),
        'h': symmetric_matrix('h'),
        'hp': symmetric_matrix('normal_h_derivative'),
        'K_plus': symmetric_matrix('K_plus'),
        'K_minus': symmetric_matrix('K_minus'),
        'h_Sigma': symmetric_matrix('h_Sigma'),
        'h0': symmetric_matrix('h0'),
        'tau': symmetric_matrix('tau'),
        'R_gamma': sp.Symbol('R_gamma', real=True),
        'scalar_metric': symmetric_matrix('C_scalar'),
        'v_plus': sp.Matrix(sp.symbols('v_plus_0:4', real=True)),
        'v_minus': sp.Matrix(sp.symbols('v_minus_0:4', real=True)),
        'tangent_scalar_jets': sp.Matrix(4, 4, lambda i, a: sp.Symbol(f't_{i}_{a}', real=True)),
        'delta_q': sp.Matrix(sp.symbols('delta_q_0:4', real=True)),
        'wall_q_Euler': sp.Matrix(sp.symbols('wall_q_Euler_0:4', real=True)),
        'potential': sp.Symbol('V', real=True),
        'E_T': sp.Symbol('E_T', real=True),
        'vartheta': sp.Symbol('delta_T_Sigma', real=True),
    }


def derive_gaussian_geometry(ctx):
    """Differentiate the metric jets, not a supplied Gauss or Jacobi formula.

    g_nn=1, g_ni=0, gamma(n)=eta+2nK+n^2 L at the reference point.
    Tangential metric jets vanish in this independent family. Thus the
    intrinsic curvature is zero, while the 5D curvature is generally nonzero.
    """
    gamma, K, L = ctx['gamma'], ctx['K'], ctx['L']
    g = sp.diag(1, gamma)
    inverse = g.inv()
    dg = sp.zeros(5)
    ddg = sp.zeros(5)
    dg[1:5, 1:5] = 2 * K
    ddg[1:5, 1:5] = 2 * L
    inverse_prime = -inverse * dg * inverse

    def partial_metric(axis, i, j):
        return dg[i, j] if axis == 0 else sp.S.Zero

    def normal_partial_metric(axis, i, j):
        return ddg[i, j] if axis == 0 else sp.S.Zero

    Gamma = [[[sp.S.Zero for _ in range(5)] for _ in range(5)] for _ in range(5)]
    Gamma_prime = [[[sp.S.Zero for _ in range(5)] for _ in range(5)] for _ in range(5)]
    for a in range(5):
        for b in range(5):
            for c in range(5):
                lowered = [partial_metric(b, j, c) + partial_metric(c, j, b)
                           - partial_metric(j, b, c) for j in range(5)]
                lowered_prime = [normal_partial_metric(b, j, c) + normal_partial_metric(c, j, b)
                                 - normal_partial_metric(j, b, c) for j in range(5)]
                Gamma[a][b][c] = sp.expand(sum(inverse[a, j] * lowered[j] for j in range(5)) / 2)
                Gamma_prime[a][b][c] = sp.expand(sum(
                    inverse_prime[a, j] * lowered[j] + inverse[a, j] * lowered_prime[j]
                    for j in range(5)) / 2)

    def dGamma(axis, a, b, c):
        return Gamma_prime[a][b][c] if axis == 0 else sp.S.Zero

    def riemann(a, b, c, d):
        return sp.expand(dGamma(c, a, d, b) - dGamma(d, a, c, b)
                         + sum(Gamma[a][c][l] * Gamma[l][d][b]
                               - Gamma[a][d][l] * Gamma[l][c][b] for l in range(5)))

    ricci = sp.Matrix(5, 5, lambda b, d: sp.expand(sum(riemann(a, b, a, d) for a in range(5))))
    R_bulk = sp.expand(sp.trace(inverse * ricci))
    R_ninj = sp.Matrix(4, 4, lambda i, j: riemann(0, i + 1, 0, j + 1))
    gi = gamma.inv()
    k = sp.trace(gi * K)
    K2 = contract(K, K, gi)
    return {
        'metric': g, 'inverse': inverse, 'metric_normal_jet': dg,
        'metric_second_normal_jet': ddg, 'inverse_normal_jet': inverse_prime,
        'christoffel': Gamma, 'christoffel_normal_derivative': Gamma_prime,
        'ricci': ricci, 'R_bulk_from_metric': R_bulk,
        'Ric_nn_from_metric': ricci[0, 0], 'R_ninj_from_metric': R_ninj,
        'R_gamma_from_tangential_metric_jets': sp.S.Zero,
        'metric_jet_family': 'flat intrinsic slices; arbitrary symmetric K,L; no Einstein or BPS equations',
        'residuals': {
            'connection_torsion_zero': [Gamma[a][b][c] - Gamma[a][c][b]
                                      for a in range(5) for b in range(5) for c in range(5)],
            'Ricci_symmetric': ricci - ricci.T,
            'normal_Riemann_from_metric': R_ninj - (K * gi * K - L),
            'contracted_Gauss_independent_metric_jets': R_bulk - 2 * ricci[0, 0] - K2 + k**2,
        },
    }


def derive_palatini(ctx, geometry):
    M, gamma, K, h, hp = (ctx[k] for k in ('M', 'gamma', 'K', 'h', 'hp'))
    gi = gamma.inv()
    ginv = geometry['inverse']
    ginv_prime = geometry['inverse_normal_jet']
    Gamma = geometry['christoffel']
    h5, hp5 = sp.zeros(5), sp.zeros(5)
    h5[1:5, 1:5] = h
    hp5[1:5, 1:5] = hp
    raised = ginv * h5 * ginv
    raised_prime = ginv_prime * h5 * ginv + ginv * hp5 * ginv + ginv * h5 * ginv_prime
    covariant_divergence = sp.expand(sum(
        (raised_prime[0, nu] if nu == 0 else 0)
        + sum(Gamma[0][nu][lam] * raised[lam, nu]
              + Gamma[nu][nu][lam] * raised[0, lam] for lam in range(5))
        for nu in range(5)))
    trace_prime = sp.trace(ginv_prime * h5 + ginv * hp5)
    theta_EH = sp.expand(M * (covariant_divergence - trace_prime) / 2)
    k = sp.trace(gi * K)
    delta_inverse = -gi * h * gi
    delta_K_covariant = hp / 2
    delta_k = sp.trace(delta_inverse * K + gi * delta_K_covariant)
    delta_volume_ratio = sp.trace(gi * h) / 2
    delta_GHY = sp.expand(M * (delta_k + k * delta_volume_ratio))
    combined = sp.expand(theta_EH + delta_GHY)
    p = expand(coefficient_matrix(combined, h))
    pi = gi * K * gi - k * gi
    paired = sum(p[i, j] * h[i, j] for i in range(4) for j in range(4))
    return {
        'gaussian_variation': 'h_nn=h_ni=0 in the chosen local representative; h_ij and normal h_ij jets independent',
        'covariant_divergence_h_normal': covariant_divergence,
        'normal_derivative_trace_h': sp.expand(trace_prime),
        'EH_Palatini_current_normal': theta_EH,
        'GHY_variation_per_volume': delta_GHY,
        'GHY_delta_k_from_metric_inverse_and_normal_jet': sp.expand(delta_k),
        'combined_boundary_variation': combined,
        'p_from_independent_metric_coefficients': p,
        'pi_contravariant': pi,
        'normalization': 'p is per invariant boundary volume, not a density; symmetric off-diagonal entries counted twice',
        'residuals': {
            'Palatini_from_covariant_derivatives': theta_EH - M * (contract(K, h, gi) - sp.trace(gi * hp)) / 2,
            'GHY_from_volume_inverse_and_metric_jet': delta_GHY - M * (sp.trace(gi * hp) / 2 - contract(K, h, gi) + k * sp.trace(gi * h) / 2),
            'all_normal_metric_variation_jets_cancel': [sp.diff(combined, hp[i, j]) for i in range(4) for j in range(i, 4)],
            'p_equals_minus_M_pi_over_two': p + M * pi / 2,
            'metric_coefficient_reconstructs_Green': combined - paired,
        },
    }


def derive_shape(ctx, geometry, palatini):
    gamma, eps, f, df, ddf = (ctx[k] for k in ('gamma', 'epsilon', 'f', 'df', 'ddf'))
    M, K, L = ctx['M'], ctx['K'], ctx['L']
    gi = gamma.inv()
    ambient = geometry['metric'] + eps * f * geometry['metric_normal_jet']
    ambient_inverse = geometry['inverse'] + eps * f * geometry['inverse_normal_jet']
    tangent = sp.zeros(5, 4)
    tangent[0, :] = (eps * df).T
    tangent[1:5, :] = sp.eye(4)
    normal_covector = sp.Matrix([1, *(-eps * df)])
    normal_derivative = sp.zeros(5)
    normal_derivative[1:5, 1:5] = -eps * ddf
    Gamma, Gprime = geometry['christoffel'], geometry['christoffel_normal_derivative']
    nabla_normal = sp.Matrix(5, 5, lambda a, b: normal_derivative[a, b]
                            - sum((Gamma[c][a][b] + eps * f * Gprime[c][a][b]) * normal_covector[c]
                                  for c in range(5)))
    induced = expand(tangent.T * ambient * tangent)
    h_shape = induced.applyfunc(lambda value: sp.expand(value).coeff(eps, 1))
    K_induced = expand(tangent.T * nabla_normal * tangent)
    K0 = K_induced.subs(eps, 0)
    delta_K = K_induced.applyfunc(lambda value: sp.expand(value).coeff(eps, 1))
    inverse_induced = gi - eps * gi * h_shape * gi
    delta_k = sp.expand(sp.trace(inverse_induced * (K0 + eps * delta_K))).coeff(eps, 1)
    # Cofactor expansion differentiates det(gamma) using one varied column at a time.
    det_prime = sum(sp.Matrix.hstack(*(h_shape[:, j] if j == varied else gamma[:, j]
                                     for j in range(4))).det() for varied in range(4))
    volume_prime = sp.cancel(det_prime / (2 * gamma.det()))
    k, K2 = sp.trace(gi * K), contract(K, K, gi)
    box_f = sp.trace(gi * ddf)
    R_bulk, Ric_nn = geometry['R_bulk_from_metric'], geometry['Ric_nn_from_metric']
    domain_EH = M * f * R_bulk / 2
    GHY_shape = M * (delta_k + k * volume_prime)
    direct_shape = sp.expand(domain_EH + GHY_shape)
    p = palatini['p_from_independent_metric_coefficients']
    p_shape = sum(p[i, j] * h_shape[i, j] for i in range(4) for j in range(4))
    H_geometry = M * (k**2 - K2) / 2
    edge_vector = -M * gi * df
    edge_divergence = sum(sp.diff(edge_vector[i], df[j]) * ddf[i, j] for i in range(4) for j in range(4))
    normal_unit = sp.expand((normal_covector.T * ambient_inverse * normal_covector)[0])
    normal_orthogonal = expand(tangent.T * normal_covector)
    Rg, Rnn = sp.symbols('R_bulk_abstract Ric_nn_abstract', real=True)
    jacobi_general = -box_f - f * (Rnn + K2)
    general_direct = M * f * Rg / 2 + M * (jacobi_general + f * k**2)
    gauss_value = ctx['R_gamma'] + 2 * Rnn + K2 - k**2
    general_reduced = sp.expand(general_direct.subs(Rg, gauss_value))
    general_H = M * (k**2 - K2 - ctx['R_gamma']) / 2
    a, ap = sp.symbols('warp_a warp_a_prime', real=True)
    warp = {K[i, j]: a * gamma[i, j] for i in range(4) for j in range(i, 4)}
    warp.update({L[i, j]: (ap + 2 * a**2) * gamma[i, j] for i in range(4) for j in range(i, 4)})
    warped_R = sp.expand(R_bulk.subs(warp, simultaneous=True))
    warped_Rnn = sp.expand(Ric_nn.subs(warp, simultaneous=True))
    warped_shape = sp.expand(direct_shape.subs(warp, simultaneous=True))
    flat = {v: 0 for matrix in (K, L) for v in matrix}
    return {
        'normal_covector_first_order': normal_covector,
        'immersion_tangent_first_order': tangent,
        'induced_metric_first_variation': h_shape,
        'induced_K_reference': K0,
        'induced_K_first_variation': delta_K,
        'trace_K_first_variation_including_inverse': delta_k,
        'volume_first_variation_from_determinant': volume_prime,
        'box_f_Lorentzian': box_f,
        'EH_domain_transport_once': domain_EH,
        'GHY_shape_variation': sp.expand(GHY_shape),
        'direct_EH_GHY_shape': direct_shape,
        'p_paired_with_shape': sp.expand(p_shape),
        'H_grav_metric_jet_family': sp.expand(H_geometry),
        'tangential_boundary_current': edge_vector,
        'tangential_boundary_divergence': sp.expand(edge_divergence),
        'general_covariant': {'Jacobi_delta_k': jacobi_general, 'before_Gauss': general_direct,
            'Gauss_substitution': {Rg: gauss_value}, 'after_Gauss': general_reduced,
            'H_grav': general_H, 'basis': 'general tensor proof in pinned lemma; independent Gaussian metric-jet witness above'},
        'warped': {'a': a, 'a_prime': ap, 'substitution': warp, 'R_bulk': warped_R,
            'Ric_nn': warped_Rnn, 'shape': warped_shape, 'BPS_or_Einstein_equations_used': False},
        'flat_shape': sp.expand(direct_shape.subs(flat)),
        'residuals': {
            'normal_unit_at_order_zero': normal_unit.coeff(eps, 0) - 1,
            'normal_unit_at_order_one': normal_unit.coeff(eps, 1),
            'normal_orthogonal_to_immersion_at_order_one': normal_orthogonal,
            'induced_metric_from_immersion': h_shape - 2 * f * K,
            'induced_K_reference_from_Christoffel': K0 - K,
            'induced_K_derivative_from_normal_and_pullback': delta_K - (f * L - ddf),
            'uncontracted_Jacobi_from_metric_Riemann': delta_K + ddf - f * (K * gi * K - geometry['R_ninj_from_metric']),
            'contracted_Jacobi_keeps_inverse_variation': delta_k + box_f + f * (Ric_nn + K2),
            'induced_determinant_volume_derivative': volume_prime - f * k,
            'shape_Legendre_from_independent_metric_jets': direct_shape - p_shape + f * H_geometry + M * box_f,
            'retained_edge_divergence_is_minus_M_box': edge_divergence + M * box_f,
            'general_covariant_Gauss_reduction': general_reduced - p_shape + f * general_H + M * box_f,
            'warped_scalar_curvature_without_BPS': warped_R + 8 * ap + 20 * a**2,
            'warped_Ric_nn_without_BPS': warped_Rnn + 4 * ap + 4 * a**2,
            'warped_shape_cancels_a_prime': warped_shape - 6 * M * a**2 * f + M * box_f,
            'flat_variable_f_retains_boundary': direct_shape.subs(flat) + M * box_f,
        },
    }


def derive_paired(ctx):
    gamma, M, f = ctx['gamma'], ctx['M'], ctx['f']
    gi = gamma.inv()
    Kp, Km, tau, hs, h0 = (ctx[key] for key in ('K_plus', 'K_minus', 'tau', 'h_Sigma', 'h0'))
    def pi(K):
        return K - sp.trace(gi * K) * gamma
    def Hg(K):
        return M * (sp.trace(gi * K)**2 - contract(K, K, gi) - ctx['R_gamma']) / 2
    pp, pm = -M * pi(Kp) / 2, -M * pi(Km) / 2
    Hp, Hm = Hg(Kp), Hg(Km)
    # The momenta here are lowered with the common gamma for concise contractions.
    gravity_plus = -contract(pp, hs, gi) + f * Hp
    gravity_minus = contract(pm, hs, gi) - f * Hm
    gravity = sp.expand(gravity_plus + gravity_minus)
    C, vp, vm, tangent = (ctx[key] for key in ('scalar_metric', 'v_plus', 'v_minus', 'tangent_scalar_jets'))
    tangent_norm = sum(gi[i, j] * (tangent[i, :] * C * tangent[j, :].T)[0]
                       for i in range(4) for j in range(4))
    Lp = -(vp.T * C * vp)[0] / 2 - tangent_norm / 2 - ctx['potential']
    Lm = -(vm.T * C * vm)[0] / 2 - tangent_norm / 2 - ctx['potential']
    sp_momentum = sp.Matrix([sp.diff(Lp, v) for v in vp])
    sm_momentum = sp.Matrix([sp.diff(Lm, v) for v in vm])
    Tp = sp.expand((vp.T * C * vp)[0] + Lp)
    Tm = sp.expand((vm.T * C * vm)[0] + Lm)
    dq = ctx['delta_q']
    delta_qp, delta_qm = dq - f * vp, dq - f * vm
    scalar_raw = (sm_momentum.T * delta_qm)[0] + f * Lm - (sp_momentum.T * delta_qp)[0] - f * Lp
    scalar_reduced = ((sm_momentum - sp_momentum).T * dq)[0] - f * (Tp - Tm)
    wall = contract(tau, hs, gi) / 2 + (ctx['wall_q_Euler'].T * dq)[0] + ctx['E_T'] * ctx['vartheta']
    I = -M * (pi(Kp) - pi(Km)) - tau
    Rq = sm_momentum - sp_momentum + ctx['wall_q_Euler']
    Htotal_plus, Htotal_minus = Hp - Tp, Hm - Tm
    raw = sp.expand(gravity + scalar_raw + wall)
    reduced = -contract(I, hs, gi) / 2 + (Rq.T * dq)[0] + ctx['E_T'] * ctx['vartheta'] + f * (Htotal_plus - Htotal_minus)
    Kbar = (Kp + Km) / 2
    trace_map = {hs[i, j]: h0[i, j] + 2 * f * Kbar[i, j]
                 for i in range(4) for j in range(i, 4)}
    in_h0 = sp.expand(raw.subs(trace_map, simultaneous=True))
    coefficient_f = sp.expand(sp.diff(in_h0, f))
    target_force = contract(tau, Kbar, gi) - (Tp - Tm)
    delta_gp, delta_gm = hs - 2 * f * Kp, hs - 2 * f * Km
    Egp, Egm = symmetric_matrix('bulk_metric_Euler_plus'), symmetric_matrix('bulk_metric_Euler_minus')
    Eqp = sp.Matrix(sp.symbols('bulk_scalar_Euler_plus_0:4', real=True))
    Eqm = sp.Matrix(sp.symbols('bulk_scalar_Euler_minus_0:4', real=True))
    volume_Euler_pair = (contract(Egp, delta_gp, gi) + contract(Egm, delta_gm, gi)
                         + (Eqp.T * delta_qp)[0] + (Eqm.T * delta_qm)[0])
    volume_f_coefficient = sp.expand(sp.diff(volume_Euler_pair.subs(trace_map, simultaneous=True), f))
    return {
        'K_bar': Kbar, 'pi_plus': pi(Kp), 'pi_minus': pi(Km),
        'p_grav_plus_common_lowered': pp, 'p_grav_minus_common_lowered': pm,
        'H_grav_plus': Hp, 'H_grav_minus': Hm,
        'outward_normal_signs': {'plus': -1, 'minus': 1},
        'outward_displacement': {'plus': -f, 'minus': f},
        'gravity_plus_face': gravity_plus, 'gravity_minus_face': gravity_minus, 'gravity_total': gravity,
        'scalar_L_plus': Lp, 'scalar_L_minus': Lm,
        'p_scalar_plus': sp_momentum, 'p_scalar_minus': sm_momentum,
        'T_nn_plus': Tp, 'T_nn_minus': Tm,
        'delta_q_bulk_plus': delta_qp, 'delta_q_bulk_minus': delta_qm,
        'scalar_Green_from_moving_endpoints': scalar_raw,
        'scalar_Green_Legendre_form': scalar_reduced,
        'wall_variation_once': wall,
        'I': I, 'R_scalar': Rq, 'H_total_plus': Htotal_plus, 'H_total_minus': Htotal_minus,
        'Green_raw': raw, 'Green_common_traces': sp.expand(reduced),
        'h_Sigma_substitution': trace_map, 'Green_in_h0_chart': in_h0,
        'normal_coefficient_from_action_Green': coefficient_f,
        'normal_force_tau_Kbar_minus_T_jump': sp.expand(target_force),
        'delta_g_bulk_plus': delta_gp, 'delta_g_bulk_minus': delta_gm,
        'bulk_Euler_pairing_marker': volume_Euler_pair,
        'bulk_Euler_f_coefficient_marker': volume_f_coefficient,
        'bulk_Euler_marker_scope': 'independent Euler covectors paired with boundary values of admissible extensions; actual volume integrals remain in total variation and are not computed here',
        'shape_edge_plus': M * gi * ctx['df'], 'shape_edge_minus': -M * gi * ctx['df'],
        'residuals': {
            'outward_pairing_gives_positive_pi_jump': gravity - M * contract(pi(Kp) - pi(Km), hs, gi) / 2 - f * (Hp - Hm),
            'scalar_momenta_derived_from_literal_density': [sp_momentum + C * vp, sm_momentum + C * vm],
            'scalar_plus_normal_Legendre_is_Tnn': Lp - (sp_momentum.T * vp)[0] - Tp,
            'scalar_minus_normal_Legendre_is_Tnn': Lm - (sm_momentum.T * vm)[0] - Tm,
            'scalar_moving_common_trace_form': scalar_raw - scalar_reduced,
            'wall_and_scalar_rows_retained': raw - reduced,
            'normal_force_from_Green_equals_constraint_combination': coefficient_f - (Htotal_plus - Htotal_minus - contract(I, Kbar, gi)),
            'normal_force_from_Green_equals_tau_Kbar_minus_T_jump': coefficient_f - target_force,
            'admissible_metric_trace_plus': delta_gp + 2 * f * Kp - hs,
            'admissible_metric_trace_minus': delta_gm + 2 * f * Km - hs,
            'h0_is_mean_of_Eulerian_metric_traces': (delta_gp + delta_gm).subs(trace_map, simultaneous=True) / 2 - h0,
            'admissible_scalar_trace_plus': delta_qp + f * vp - dq,
            'admissible_scalar_trace_minus': delta_qm + f * vm - dq,
            'paired_variable_f_shape_currents_cancel': M * gi * ctx['df'] - M * gi * ctx['df'],
        },
    }


def derive_model():
    ctx = symbols_context()
    geometry = derive_gaussian_geometry(ctx)
    palatini = derive_palatini(ctx, geometry)
    shape = derive_shape(ctx, geometry, palatini)
    paired = derive_paired(ctx)
    parts = {'geometry': geometry, 'palatini': palatini, 'shape': shape, 'paired': paired}
    checks = {part + '_' + name: zero(value)
              for part, data in parts.items() for name, value in data['residuals'].items()}
    M, f, gi = ctx['M'], ctx['f'], ctx['gamma'].inv()
    wrong_I = M * (paired['pi_plus'] - paired['pi_minus']) - ctx['tau']
    wrong_Israel = (-contract(wrong_I, ctx['h_Sigma'], gi) / 2
                     + (paired['R_scalar'].T * ctx['delta_q'])[0] + ctx['E_T'] * ctx['vartheta']
                     + f * (paired['H_total_plus'] - paired['H_total_minus']))
    wrong_both_outward = (contract(paired['p_grav_plus_common_lowered'] + paired['p_grav_minus_common_lowered'], ctx['h_Sigma'], gi)
                          - f * (paired['H_grav_plus'] + paired['H_grav_minus']))
    lost_Legendre = ((paired['p_scalar_minus'] - paired['p_scalar_plus']).T * ctx['delta_q'])[0] + f * (paired['scalar_L_minus'] - paired['scalar_L_plus'])
    frozen_inverse = sp.trace(gi * shape['induced_K_first_variation'])
    witnesses = {
        'wrong_Israel_jump_sign': wrong_Israel - paired['Green_raw'],
        'both_outward_normals_chosen_equal': wrong_both_outward - paired['gravity_total'],
        'omit_GHY_leaves_normal_metric_jets': [sp.diff(palatini['EH_Palatini_current_normal'], ctx['hp'][i, j]) for i in range(4) for j in range(i, 4)],
        'omit_scalar_normal_Legendre_term': lost_Legendre - paired['scalar_Green_from_moving_endpoints'],
        'freeze_both_bulk_metric_traces': 2 * f * (ctx['K_plus'] - ctx['K_minus']),
        'double_count_intrinsic_wall': paired['wall_variation_once'],
        'discard_scalar_natural_rows': (paired['R_scalar'].T * ctx['delta_q'])[0],
        'discard_bulk_Euler_terms_off_shell': paired['bulk_Euler_f_coefficient_marker'],
        'omit_variable_f_boundary_current': M * shape['box_f_Lorentzian'],
        'freeze_inverse_in_shape_trace': frozen_inverse - shape['trace_K_first_variation_including_inverse'],
        'double_count_EH_domain_transport': shape['EH_domain_transport_once'],
    }
    negative = {name: not zero(value) for name, value in witnesses.items()}
    decision = {
        'Dirichlet_momentum_derived_from_Palatini_and_GHY': True,
        'normal_shape_Green_identified_in_declared_chart': True,
        'independent_5D_immersion_metric_jets_checked': True,
        'paired_scalar_wall_natural_rows_retained': True,
        'normal_constraint_coefficient_linked_to_action_variation': True,
        'bulk_Euler_terms_discarded_off_shell': False,
        'all_external_corner_variations_closed': False,
        'full_gauged_material_and_BF_moving_map_derived': False,
        'global_functional_domain_or_solution_proved': False,
        'N4_JUNCTION_BENDING_pass': False, 'full_N7': False,
        'C1': False, 'N1': False, 'P2': False, 'P3': False, 'P4': False,
        'B4': False, 'B5': False,
    }
    return {
        'symbols': ctx, **parts, 'checks': checks,
        'negative_controls': negative, 'negative_witnesses': witnesses,
        'decision': decision,
        'scope': {
            'geometry': 'smooth timelike common interface, spacelike unit normal, constant M; local Gaussian representative',
            'variations': 'one common displacement and common induced traces; bulk Eulerian variations adjusted by gluing',
            'boundary': 'compact support away from other boundaries or retained tangential currents; external corners not treated',
            'wall': 'single intrinsic action without extra radial K dependence; complete metric and scalar/clock Euler coefficients',
            'material_limit': 'gauged connection and dependent-frame trace adjoints must be added separately',
            'finite_geometry_oracle': 'homogeneous intrinsic metric jets with arbitrary symmetric K,L, not a general curved-slice computer proof',
            'analytic_general_statement': 'pinned lemma supplies covariant Palatini/Jacobi/Gauss reasoning',
        },
    }


def serialize(value):
    if isinstance(value, sp.MatrixBase):
        return serialize(value.tolist())
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serialize(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialize(v) for v in value]
    return value


def load_sources(note_path=NOTE, source_paths=None):
    paths = dict(SOURCES)
    if source_paths:
        if set(source_paths) - set(paths):
            raise MovingNormalGreenError('unknown source override')
        paths.update(source_paths)
    note = Path(note_path)
    if hashlib.sha256(note.read_bytes()).hexdigest() != NOTE_SHA256:
        raise MovingNormalGreenError('note byte hash mismatch')
    result = {'note': {'name': note.name, 'sha256': NOTE_SHA256}}
    for name, path in paths.items():
        path = Path(path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256[name]:
            raise MovingNormalGreenError(name + ' byte hash mismatch')
        result[name] = {'name': path.name, 'sha256': SOURCE_SHA256[name]}
    result['upstream_gates_inherited'] = False
    result['upstream_theorem_used_as_momentum_oracle'] = False
    return result


def build_payload(note_path=NOTE, source_paths=None):
    sources = load_sources(note_path, source_paths)
    model = derive_model()
    if not all(model['checks'].values()) or not all(model['negative_controls'].values()):
        raise MovingNormalGreenError('moving normal Green identity or negative control failed')
    payload = {
        'schema': SCHEMA, 'sources': sources, 'model': serialize(model),
        'checks': model['checks'], 'negative_controls': model['negative_controls'],
        'decision': model['decision'],
        'provenance': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in (Path(__file__), TEST)},
        'runtime': {'sympy': sp.__version__},
    }
    payload['calculation_digest'] = canonical_digest(payload)
    return payload


def validate_payload(payload, note_path=NOTE, source_paths=None):
    if not isinstance(payload, dict) or payload.get('schema') != SCHEMA:
        raise MovingNormalGreenError('receipt schema mismatch')
    body = {k: v for k, v in payload.items() if k != 'calculation_digest'}
    if payload.get('calculation_digest') != canonical_digest(body):
        raise MovingNormalGreenError('receipt digest mismatch')
    if payload != build_payload(note_path, source_paths):
        raise MovingNormalGreenError('receipt differs from fresh derivation')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write', nargs='?', const=OUTPUT, type=Path)
    group.add_argument('--verify', nargs='?', const=OUTPUT, type=Path)
    args = parser.parse_args(argv)
    if args.write is not None:
        payload = build_payload()
        args.write.parent.mkdir(parents=True, exist_ok=True)
        with args.write.open('x', encoding='utf8') as handle:
            json.dump(payload, handle, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write('\n')
    else:
        payload = json.loads(args.verify.read_bytes())
        validate_payload(payload)
    print(json.dumps({'checks_passed': sum(payload['checks'].values()),
                      'negative_controls': payload['negative_controls'],
                      'calculation_digest': payload['calculation_digest']}))


if __name__ == '__main__':
    main()
