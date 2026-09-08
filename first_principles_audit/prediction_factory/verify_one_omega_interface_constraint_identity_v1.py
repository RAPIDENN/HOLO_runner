"""Independent normal/Codazzi/BF constraint algebra, not a full N4/N7 gate."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
PROOF = HERE / 'one_omega_interface_constraint_identity_lemma_v1.md'
TEST = HERE / 'test_one_omega_interface_constraint_identity_v1.py'
OUTPUT = HERE / 'artifacts/one_omega_interface_constraint_identity_v1.json'
SOURCE_SHA = 'd9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
ACTION_SHA = '3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a'
PROOF_SHA = '384a548ea4961ba183a5138e98e59024f6d86848df2712bdad89a9c5632b9200'
SCHEMA = 'holo.one-omega-interface-constraint-identity.v1'


class ConstraintIdentityError(ValueError):
    """The convention source, proof or recomputed identity receipt disagrees."""


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def load_source(path=SOURCE):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ConstraintIdentityError('v5.2 source byte pin mismatch')
    doc = json.loads(raw)
    if doc.get('schema') != 'holo.one-omega-topological-so3-classical-v5-2-gate.v1':
        raise ConstraintIdentityError('v5.2 source schema mismatch')
    charter = doc['exact_classical_charter']
    if canonical_digest(charter['exact_action']) != ACTION_SHA:
        raise ConstraintIdentityError('literal v5.2 action changed')
    green = doc['Green_form_certificate']
    if green['natural_interface_equations']['Israel'] != (
            'M5^3*sum_eps pi_eps^(mu nu)=tau_Sigma^(mu nu)'):
        raise ConstraintIdentityError('Israel convention changed')
    if charter['exact_action']['BF'] != (
            'S_BF=sum_eps int_Meps <B_eps wedge F[A_eps]>, <X,Y>=-tr_3(XY)/2'):
        raise ConstraintIdentityError('BF trace convention changed')
    return {'source_sha256': SOURCE_SHA, 'literal_action_sha256': ACTION_SHA,
            'Israel': green['natural_interface_equations']['Israel'],
            'GHY': charter['exact_action']['GHY'], 'BF': charter['exact_action']['BF'],
            'common_metric': charter['definitions']['induced_metric'],
            'source_N4': doc['decision']['N4_JUNCTION_BENDING_pass'],
            'source_N7': doc['decision']['N7_LINEAR_REDUCTION_pass'],
            'source_gates_inherited': False}


def symmetric_symbols(prefix):
    slots = {(i, j): sp.Symbol(f'{prefix}_{i}{j}', real=True)
             for i in range(4) for j in range(i, 4)}
    return sp.Matrix(4, 4, lambda i, j: slots[min(i, j), max(i, j)])


def double_contract(left, right, inverse):
    raised = inverse * right * inverse
    return sum(left[i, j] * raised[i, j] for i in range(4) for j in range(4))


def normal_rows(metric, K_plus, K_minus, tau, T_plus, T_minus, *, M, R):
    """All K and stress slots are covariant; both K use the same unit normal."""
    matrices = tuple(sp.Matrix(a) for a in (metric, K_plus, K_minus, tau))
    if any(a.shape != (4, 4) or a != a.T for a in matrices):
        raise ConstraintIdentityError('symmetric four-dimensional matrices required')
    metric, K_plus, K_minus, tau = matrices
    inverse = metric.inv()
    trace_plus, trace_minus = (sp.trace(inverse * K) for K in (K_plus, K_minus))
    pi_plus = K_plus - metric * trace_plus
    pi_minus = K_minus - metric * trace_minus
    mean = (K_plus + K_minus) / 2
    Israel = -M * (pi_plus - pi_minus) - tau
    H_plus = M * (trace_plus**2 - double_contract(K_plus, K_plus, inverse) - R) / 2 - T_plus
    H_minus = M * (trace_minus**2 - double_contract(K_minus, K_minus, inverse) - R) / 2 - T_minus
    force = double_contract(tau, mean, inverse) - (T_plus - T_minus)
    reconstructed = H_plus - H_minus - double_contract(Israel, mean, inverse)
    return {'inverse_metric': inverse, 'pi_plus': pi_plus, 'pi_minus': pi_minus,
            'mean_K': mean, 'Israel_residual': Israel,
            'H_plus': H_plus, 'H_minus': H_minus, 'force_normal': force,
            'force_from_constraints': reconstructed,
            'residual': sp.expand(force - reconstructed)}


def covariant_divergence(jets, inverse):
    """jets[c][a,b] denotes D_c Q_ab, with D gamma=0 at the point."""
    return sp.Matrix([sum(inverse[a, c] * jets[c][a, b]
                          for a in range(4) for c in range(4)) for b in range(4)])


def tangential_rows(metric, K_plus_jets, K_minus_jets, tau_jets,
                    T_plus, T_minus, *, M):
    inverse = metric.inv()
    pi_plus_jets = [K - metric * sp.trace(inverse * K) for K in K_plus_jets]
    pi_minus_jets = [K - metric * sp.trace(inverse * K) for K in K_minus_jets]
    Israel_jets = [-M * (plus - minus) - stress
                   for plus, minus, stress in zip(pi_plus_jets, pi_minus_jets, tau_jets)]
    div_tau = covariant_divergence(tau_jets, inverse)
    div_Israel = covariant_divergence(Israel_jets, inverse)
    E_plus = M * covariant_divergence(pi_plus_jets, inverse) - T_plus
    E_minus = M * covariant_divergence(pi_minus_jets, inverse) - T_minus
    force = div_tau + T_plus - T_minus
    reconstructed = -div_Israel - (E_plus - E_minus)
    return {'div_tau': div_tau, 'div_Israel': div_Israel,
            'E_n_plus': E_plus, 'E_n_minus': E_minus, 'force_tangent': force,
            'force_from_constraints': reconstructed,
            'residual': (force - reconstructed).applyfunc(sp.expand)}


def clean_form(form):
    return {key: coefficient for key, value in form.items()
            if (coefficient := sp.expand(value)) != 0}


def add_forms(*weighted_forms):
    answer = {}
    for factor, form in weighted_forms:
        for key, value in form.items():
            answer[key] = answer.get(key, 0) + factor * value
    return clean_form(answer)


def wedge(left, right):
    """Exterior basis coefficients, not unnormalized antisymmetric arrays."""
    answer = {}
    for a, ca in left.items():
        for b, cb in right.items():
            if set(a).intersection(b):
                continue
            sign = (-1)**sum(i > j for i in a for j in b)
            key = tuple(sorted(a + b))
            answer[key] = answer.get(key, 0) + sign * ca * cb
    return clean_form(answer)


def interior(form, vector):
    answer = {}
    for key, coefficient in form.items():
        for position, axis in enumerate(key):
            reduced = key[:position] + key[position+1:]
            answer[reduced] = answer.get(reduced, 0) + (-1)**position * vector[axis] * coefficient
    return clean_form(answer)


def bf_identity(B_forms, F_forms, vector):
    if len(B_forms) != len(F_forms):
        raise ConstraintIdentityError('BF color counts differ')
    density = add_forms(*[(1, wedge(B, F)) for B, F in zip(B_forms, F_forms)])
    theta = add_forms(*[(-1, wedge(B, interior(F, vector)))
                        for B, F in zip(B_forms, F_forms)])
    expected = add_forms(*[(1, wedge(interior(B, vector), F))
                           for B, F in zip(B_forms, F_forms)])
    transgression = interior(density, vector)
    actual = add_forms((1, transgression), (-1, theta))
    return {'density': density, 'theta_on_covariant_diffeomorphism': theta,
            'transgression': transgression, 'Legendre_normal_form': actual,
            'expected_B_Euler_pairing': expected,
            'residual': add_forms((1, actual), (-1, expected)),
            'wrong_theta_sign_residual': add_forms((1, transgression), (1, theta), (-1, expected)),
            'double_transgression_residual': add_forms((2, transgression), (-1, theta), (-1, expected)),
            'omit_theta_residual': add_forms((1, transgression), (-1, expected))}


def derive_model():
    # Invertible rational congruence fixes Lorentz signature without sampled eigenvalues.
    coframe = sp.Matrix([[1, 0, 0, 0], [sp.Rational(1, 3), 1, 0, 0],
                        [0, sp.Rational(1, 2), 1, 0], [sp.Rational(1, 5), 0, sp.Rational(2, 3), 1]])
    eta = sp.diag(-1, 1, 1, 1)
    metric = coframe.T * eta * coframe
    K_plus, K_minus, tau = (symmetric_symbols(name) for name in ('Kp', 'Km', 'tau'))
    M = sp.Symbol('M5_cubed', positive=True)
    R, T_plus, T_minus = sp.symbols('R_gamma Tnn_plus Tnn_minus', real=True)
    normal = normal_rows(metric, K_plus, K_minus, tau, T_plus, T_minus, M=M, R=R)
    reverse = normal_rows(metric, -K_minus, -K_plus, tau, T_minus, T_plus, M=M, R=R)
    inverse, mean = normal['inverse_metric'], normal['mean_K']
    wrong_Israel = M * (normal['pi_plus'] - normal['pi_minus']) - tau
    no_trace_Israel = -M * (K_plus - K_minus) - tau
    normal_mutants = {
        'wrong_Israel_incidence': sp.expand(normal['force_normal'] - normal['H_plus'] + normal['H_minus']
                                          + double_contract(wrong_Israel, mean, inverse)),
        'omit_pi_trace': sp.expand(normal['force_normal'] - normal['H_plus'] + normal['H_minus']
                                   + double_contract(no_trace_Israel, mean, inverse)),
        'reverse_only_constraint_jump': sp.expand(normal['force_normal'] + normal['H_plus'] - normal['H_minus']
                                                   + double_contract(normal['Israel_residual'], mean, inverse)),
        'noncommon_R_gamma': M * sp.Symbol('Delta_R_gamma', real=True) / 2,
    }
    jets_plus = [symmetric_symbols(f'D{a}_Kp') for a in range(4)]
    jets_minus = [symmetric_symbols(f'D{a}_Km') for a in range(4)]
    jets_tau = [symmetric_symbols(f'D{a}_tau') for a in range(4)]
    flux_plus = sp.Matrix(sp.symbols('Tn_plus_0:4', real=True))
    flux_minus = sp.Matrix(sp.symbols('Tn_minus_0:4', real=True))
    tangent = tangential_rows(metric, jets_plus, jets_minus, jets_tau, flux_plus, flux_minus, M=M)
    tangent_wrong_flux = (tangent['force_tangent'] - 2 * (flux_plus - flux_minus)
                          - tangent['force_from_constraints']).applyfunc(sp.expand)
    vector = sp.Matrix(sp.symbols('xi_0:5', real=True))
    B_forms = [{key: sp.Symbol(f'B{color}_' + ''.join(map(str, key)), real=True)
                for key in itertools.combinations(range(5), 3)} for color in range(3)]
    F_forms = [{key: sp.Symbol(f'F{color}_' + ''.join(map(str, key)), real=True)
                for key in itertools.combinations(range(5), 2)} for color in range(3)]
    bf = bf_identity(B_forms, F_forms, vector)
    checks = {
        'Lorentz_signature_by_invertible_congruence': coframe.det() == 1 and metric == coframe.T * eta * coframe,
        'normal_constraint_Israel_identity': normal['residual'] == 0,
        'normal_reversal_Israel_invariant': reverse['Israel_residual'] == normal['Israel_residual'],
        'normal_reversal_force_odd': sp.expand(reverse['force_normal'] + normal['force_normal']) == 0,
        'normal_reversal_constraint_jump_odd': sp.expand(reverse['H_plus'] - reverse['H_minus']
                                                        + normal['H_plus'] - normal['H_minus']) == 0,
        'tangential_constraint_conservation_identity': tangent['residual'] == sp.zeros(4, 1),
        'BF_Cartan_minus_presymplectic_identity': not bf['residual'],
        'BF_normal_pairing_vanishes_on_F_zero': not clean_form({k: v.subs({f: 0 for F in F_forms for f in F.values()})
                                                               for k, v in bf['Legendre_normal_form'].items()}),
        'normal_sign_trace_and_gluing_mutants_detected': all(v != 0 for v in normal_mutants.values()),
        'tangential_wrong_flux_mutant_detected': tangent_wrong_flux != sp.zeros(4, 1),
        'BF_wrong_theta_sign_mutant_detected': bool(bf['wrong_theta_sign_residual']),
        'BF_double_transgression_mutant_detected': bool(bf['double_transgression_residual']),
        'BF_omitted_presymplectic_mutant_detected': bool(bf['omit_theta_residual']),
    }
    return {'metric': metric, 'coframe': coframe,
            'symbols': {'K_plus': K_plus, 'K_minus': K_minus, 'tau': tau, 'M': M, 'R': R,
                        'T_plus': T_plus, 'T_minus': T_minus, 'K_plus_jets': jets_plus,
                        'K_minus_jets': jets_minus, 'tau_jets': jets_tau,
                        'T_n_plus': flux_plus, 'T_n_minus': flux_minus, 'xi': vector,
                        'B_forms': B_forms, 'F_forms': F_forms},
            'normal': normal, 'tangential': tangent, 'BF': bf,
            'negative_controls': {'normal': normal_mutants, 'tangential_wrong_flux': tangent_wrong_flux},
            'checks': {k: bool(v) for k, v in checks.items()}}


def serialize(value):
    if isinstance(value, sp.MatrixBase):
        return [[serialize(x) for x in row] for row in value.tolist()]
    if isinstance(value, dict):
        return {(','.join(map(str, k)) if isinstance(k, tuple) else k): serialize(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialize(x) for x in value]
    if isinstance(value, sp.Basic):
        return str(value)
    return value


def build_payload(source_path=SOURCE):
    source = load_source(source_path)
    if hashlib.sha256(PROOF.read_bytes()).hexdigest() != PROOF_SHA:
        raise ConstraintIdentityError('reviewed interface proof pin mismatch')
    model = derive_model()
    if not all(model['checks'].values()):
        raise ConstraintIdentityError('interface constraint algebra failed')
    payload = {'schema': SCHEMA, 'source': source,
               'model': serialize(model), 'checks': model['checks'],
               'decision': {
                   'local_normal_constraint_Israel_identity_pass': True,
                   'local_tangential_constraint_conservation_identity_pass': True,
                   'BF_normal_Legendre_identity_pass': True,
                   'complete_literal_moving_Green_form_pass': False,
                   'complete_v5_2_all_field_normal_embedding_pass': False,
                   'complete_moving_embedding_Ward_pass': False,
                   'gluing_variation_adjoint_derived': False,
                   'BF_relative_domain_or_gauge_quotient_closed': False,
                   'N2_CONSTRAINTS_pass': False, 'N3_CHARACTERISTICS_pass': False,
                   'N4_JUNCTION_BENDING_pass': False, 'N5_COUPLED_BVP_pass': False,
                   'N6_GLOBAL_STABILITY_pass': False, 'N7_LINEAR_REDUCTION_pass': False,
                   'full_N7': False, 'P4_full_same_action_pass': False,
                   'B4_pass': False, 'B5_pass': False},
               'provenance': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (Path(__file__), TEST, PROOF)}}
    payload['calculation_digest'] = canonical_digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload, dict) or payload.get('schema') != SCHEMA:
        raise ConstraintIdentityError('interface identity receipt schema mismatch')
    supplied = payload.get('calculation_digest')
    if supplied != canonical_digest({k: v for k, v in payload.items() if k != 'calculation_digest'}):
        raise ConstraintIdentityError('interface identity receipt digest mismatch')
    if payload != build_payload():
        raise ConstraintIdentityError('interface receipt differs from fresh derivation')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write', nargs='?', const=OUTPUT, type=Path)
    modes.add_argument('--verify', nargs='?', const=OUTPUT, type=Path)
    args = parser.parse_args()
    if args.write:
        result = build_payload()
        with args.write.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write('\n')
    else:
        result = json.loads(args.verify.read_text())
        validate_payload(result)
    print(json.dumps({'schema': SCHEMA, 'checks_passed': sum(result['checks'].values()),
                      'checks_total': len(result['checks']), 'calculation_digest': result['calculation_digest']}))


if __name__ == '__main__':
    main()
