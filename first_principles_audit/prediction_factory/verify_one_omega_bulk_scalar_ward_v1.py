#!/usr/bin/env python3
"""Exact bulk scalar coordinate and stress conservation audit.

The Ward proof independently varies a generic four-field first-jet Lagrangian
in five-dimensional Lorentzian normal coordinates at an arbitrary point. All
first jets and symmetric second jets are independent. Since the stress tensor,
Euler covector and their covariant divergence are tensors, this pointwise proof
extends to every smooth Levi-Civita metric. It assumes neither a background
solution nor scalar field equations. The charter specialization uses its full
potential, not a radial truncation. This is not a gravity or junction audit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import sympy as sp

if __package__:
    from . import one_omega_bulk_scalar_equations_v1 as equations
    from .verify_one_omega_scalar_interface_reparam_v1 import (
        CHARTER, CHARTER_BYTES_SHA256, ACTION_SHA256, canonical_digest,
        load_charter, _read_json,
    )
else:
    import one_omega_bulk_scalar_equations_v1 as equations
    from verify_one_omega_scalar_interface_reparam_v1 import (
        CHARTER, CHARTER_BYTES_SHA256, ACTION_SHA256, canonical_digest,
        load_charter, _read_json,
    )

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'artifacts' / 'one_omega_bulk_scalar_ward_v1.json'
TEST = HERE / 'test_one_omega_bulk_scalar_ward_v1.py'
SCHEMA = 'holo.one-omega-bulk-scalar-ward.v1'


class BulkWardError(ValueError):
    """The independently checked scalar receipt is inconsistent."""


def _digest(value):
    return canonical_digest(value)


@lru_cache(maxsize=1)
def ward_identity():
    """Vary L directly and differentiate T with an independent total derivative.

    C and its first field derivatives are arbitrary independent symmetric
    matrix jets at this point. V and its field derivatives are independent too.
    No identities on them beyond C_AB=C_BA are used.
    """
    n, dimension = 4, 5
    eta = (-1, 1, 1, 1, 1)
    pairs = [(a, b) for a in range(n) for b in range(a, n)]
    Cs = {ab: sp.Symbol(f'C{ab[0]}{ab[1]}', real=True) for ab in pairs}
    C = sp.Matrix(n, n, lambda a, b: Cs[min(a, b), max(a, b)])
    dC = {(a, b, c): sp.Symbol(f'dC{a}{b}_{c}', real=True)
          for a, b in pairs for c in range(n)}
    V = sp.Symbol('V', real=True)
    dV = sp.Matrix(sp.symbols('dV0:4', real=True))
    v = sp.Matrix(n, dimension, lambda a, mu: sp.Symbol(f'v{a}_{mu}', real=True))
    hjets = {(a, mu, nu): sp.Symbol(f'h{a}_{mu}{nu}', real=True)
             for a in range(n) for mu in range(dimension) for nu in range(mu, dimension)}
    h = tuple(sp.Matrix(dimension, dimension,
              lambda mu, nu, a=a: hjets[a, min(mu, nu), max(mu, nu)]) for a in range(n))
    X = sp.Matrix(n, n, lambda a, b: sum(eta[mu]*v[a, mu]*v[b, mu] for mu in range(dimension)))
    boxes = sp.Matrix([sum(eta[mu]*h[a][mu, mu] for mu in range(dimension)) for a in range(n)])
    L = -sum(C[a, b]*X[a, b] for a in range(n) for b in range(n))/2 - V

    def partial_field(expr, a):
        return sum(sp.diff(expr, Cs[b, c])*dC[b, c, a] for b, c in pairs) + sp.diff(expr, V)*dV[a]

    def total(expr, mu):
        return sum(partial_field(expr, a)*v[a, mu] for a in range(n)) + sum(
            sp.diff(expr, v[a, nu])*h[a][mu, nu]
            for a in range(n) for nu in range(dimension))

    # Euler expression comes from literal jet differentiation, not sigma_euler.
    E = sp.Matrix([sp.expand(partial_field(L, a) - sum(
        total(sp.diff(L, v[a, mu]), mu) for mu in range(dimension))) for a in range(n)])
    T = sp.Matrix(dimension, dimension, lambda mu, nu: sum(
        C[a, b]*v[a, mu]*v[b, nu] for a in range(n) for b in range(n))
        + (eta[mu]*L if mu == nu else 0))
    divergence = sp.Matrix([sp.expand(sum(eta[mu]*total(T[mu, nu], mu)
                      for mu in range(dimension))) for nu in range(dimension)])
    E_gradient = v.T*E
    residual = (divergence-E_gradient).applyfunc(sp.expand)
    missing_potential = T + sp.diag(*[eta[mu]*V for mu in range(dimension)])
    missing_potential_residual = sp.Matrix([sp.expand(sum(
        eta[mu]*total(missing_potential[mu, nu], mu) for mu in range(dimension))
        - E_gradient[nu]) for nu in range(dimension)])
    half_trace = T-sp.diag(*[eta[mu]*L/2 for mu in range(dimension)])
    half_trace_residual = sp.Matrix([sp.expand(sum(
        eta[mu]*total(half_trace[mu, nu], mu) for mu in range(dimension))
        - E_gradient[nu]) for nu in range(dimension)])
    negatives = {'wrong_euler_sign': (divergence+E_gradient).applyfunc(sp.expand),
                 'missing_potential_in_stress': missing_potential_residual,
                 'half_trace_in_stress': half_trace_residual}
    checks = {'five_covariant_divergence_identities': residual == sp.zeros(dimension, 1),
              'stress_is_symmetric': T == T.T,
              'all_stress_mutants_rejected': all(r != sp.zeros(dimension, 1) for r in negatives.values())}
    return {'symbols': dict(C=C, Cs=Cs, dC=dC, V=V, dV=dV, v=v, h=h,
                           eta=eta, X=X, boxes=boxes, pairs=pairs),
            'lagrangian': L, 'euler': E, 'stress': T, 'divergence': divergence,
            'residual': residual, 'negative_control_residuals': negatives,
            'checks': checks}


def specialize_euler(ward, model):
    """Compare the direct Lagrangian variation to the coordinate-route equations."""
    z = ward['symbols']
    C, q, V = model['C_old'], model['q_old'], model['V_old']
    mapping = {z['Cs'][a, b]: C[a, b] for a, b in z['pairs']}
    mapping.update({z['dC'][a, b, c]: sp.diff(C[a, b], q[c])
                    for a, b in z['pairs'] for c in range(4)})
    mapping.update({z['dV'][a]: sp.diff(V, q[a]) for a in range(4)})
    mapping[z['V']] = V
    direct = ward['euler'].xreplace(mapping)
    jets = {model['X_old'][a, b]: z['X'][a, b] for a, b in z['pairs']}
    jets.update(dict(zip(model['box_old'], z['boxes'])))
    # Restore the potential gradient first so only rational kinetic coefficients
    # remain in the polynomial comparison. No nonlinear potential is approximated.
    residual = sp.Matrix([sp.expand((direct[a]+sp.diff(V, q[a]))
        - (model['E_old'][a]+sp.diff(V, q[a])).xreplace(jets)) for a in range(4)])
    return residual.applyfunc(sp.cancel)



def linear_triplet(model):
    """Extract the exact first-order triplet equations about phi=0.

    The background metric and Omega are arbitrary here. Metric or Omega
    perturbations times a triplet perturbation contribute only at second order.
    """
    epsilon = sp.Symbol('epsilon', real=True)
    o, phi, X, boxes = (model[k] for k in ('omega', 'phi', 'X_old', 'box_old'))
    Z = model['Z']
    scale = {field: epsilon*field for field in phi}
    scale.update({X[a, b]: epsilon**(int(a>0)+int(b>0))*X[a, b]
                  for a in range(4) for b in range(a, 4) if a or b})
    scale.update({boxes[a]: epsilon*boxes[a] for a in range(1, 4)})
    linear = sp.Matrix([sp.diff(expr.xreplace(scale), epsilon).subs(epsilon, 0)
                        for expr in model['E_old']]).applyfunc(sp.cancel)
    reference = sp.Matrix([0, *[
        Z*(boxes[a+1]+3*phi[a]*boxes[0]/(2*o)-15*phi[a]*X[0,0]/(4*o**2))
        for a in range(3)]])
    residual = (linear-reference).applyfunc(sp.cancel)
    material_V = (model['V_old']-model['U']).xreplace(scale)
    potential_jets = sp.Matrix([sp.diff(material_V, epsilon, degree).subs(epsilon, 0)
                                for degree in range(4)])
    # A generic tensor component: P_mu and P_nu are linear in the amplitude;
    # Q represents their arbitrary Lorentzian contraction before scaling.
    Pmu, Pnu, Q, gmn = sp.symbols('P_mu P_nu P_contraction g_mu_nu', real=True)
    Tmaterial = Z*epsilon**2*(Pmu*Pnu-gmn*Q/2)-gmn*material_V
    linear_stress = sp.diff(Tmaterial, epsilon).subs(epsilon, 0)
    return {'linear_equations': linear, 'reference': reference,
            'residual': residual, 'potential_amplitude_derivatives_0_to_3': potential_jets,
            'material_stress_linear_residual': linear_stress,
            'checks': {'triplet_linearization_matches_all_four_equations': residual == sp.zeros(4, 1),
                       'full_V4_starts_at_fourth_amplitude_order': potential_jets == sp.zeros(4, 1),
                       'triplet_does_not_source_Einstein_at_linear_order': linear_stress == 0}}


def _strings(value):
    if isinstance(value, sp.MatrixBase):
        return [[sp.sstr(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    return sp.sstr(value)


def build_payload():
    load_charter()
    model = equations.derive_model()
    ward = ward_identity()
    special = specialize_euler(ward, model)
    triplet = linear_triplet(model)
    o, phi, X, boxes = (model[k] for k in ('omega', 'phi', 'X_old', 'box_old'))
    # Consistent zero-triplet truncation requires zero triplet derivatives too.
    vacuum = dict.fromkeys(phi, 0)
    vacuum.update({X[a, b]: 0 for a in range(4) for b in range(a, 4) if a or b})
    vacuum.update({boxes[a]: 0 for a in range(1, 4)})
    zero_triplet = model['E_old'].xreplace(vacuum)
    truncation = sp.Matrix([sp.simplify(zero_triplet[0] - (
        model['G']*boxes[0]-sp.diff(model['U'], o))), *[sp.simplify(x) for x in zero_triplet[1:]]])
    principal = sp.Matrix(4, 4, lambda a, b: sp.diff(model['E_old'][a], boxes[b]))
    principal_residual = (principal-model['C_old']).applyfunc(sp.simplify)
    determinant = sp.factor(model['C_old'].det())
    checks = {**model['checks'], **ward['checks'], **triplet['checks'],
              'direct_five_dimensional_variation_matches_charter_equations': special == sp.zeros(4, 1),
              'zero_triplet_is_consistent_truncation': truncation == sp.zeros(4, 1),
              'scalar_principal_matrix_is_kinetic_metric': principal_residual == sp.zeros(4),
              'kinetic_determinant_is_G_Z_cubed': determinant == model['G']*model['Z']**3}
    files = [Path(__file__), Path(equations.__file__), TEST,
             HERE/'verify_one_omega_scalar_interface_reparam_v1.py']
    provenance = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    payload = {
        'schema': SCHEMA,
        'source': {'charter_sha256': CHARTER_BYTES_SHA256, 'action_sha256': ACTION_SHA256,
                   'code_sha256': provenance},
        'domain': {'spacetime_dimension': 5, 'fields': ['Omega', 'phi1', 'phi2', 'phi3'],
                   'assumptions': ['Omega>0', 'G>0', 'Z>0', 'smooth scalar fields',
                                   'smooth Lorentzian Levi-Civita metric', 'independent first and symmetric second jets'],
                   'potential': 'Full V4; no small-field or derivative truncation',
                   'translation': 'Manually reviewed literal scalar terms of the pinned charter'},
        'equations': {key: _strings(model[key]) for key in [
            'C_old', 'C_new', 'V_old', 'V_new', 'transform', 'jacobian',
            'box_new_pulled', 'E_old', 'E_new', 'covariance_residual',
            'expected_phi_equations', 'expected_omega_equation']},
        'ward': {'identity': 'nabla^mu T_mu_nu = sum_A E_A * partial_nu q_A',
                 'stress': 'T_mu_nu=C_AB partial_mu q_A partial_nu q_B + g_mu_nu L',
                 'derivation': 'Direct total derivative of stress and direct first-jet Euler variation at an arbitrary normal-coordinate point',
                 'residual': _strings(ward['residual']),
                 'specialization_residual': _strings(special),
                 'negative_controls': {key: _strings(value) for key, value in ward['negative_control_residuals'].items()}},
        'scalar_principal': {'matrix_residual': _strings(principal_residual),
                            'determinant': str(determinant),
                            'conclusion': 'Invertible positive field metric; scalar principal symbol is C_AB times g^MN xi_M xi_N on a prescribed metric'},
        'linear_triplet': {key: _strings(value) for key, value in triplet.items() if key != 'checks'},
        'zero_triplet_truncation_residual': _strings(truncation),
        'checks': checks,
        'not_established': ['metric Euler equations', 'moving junctions and GHY',
                            'full coupled gravity constraints or characteristics',
                            'full coupled Hessian or stability', 'global C2/N2/P2/P4/B4/B5 promotion'],
    }
    if not all(checks.values()):
        raise BulkWardError('symbolic check failed: '+', '.join(k for k,v in checks.items() if not v))
    payload['calculation_digest'] = _digest(payload)
    return payload


def validate_payload(doc, recompute=True):
    if not isinstance(doc, dict) or doc.get('schema') != SCHEMA:
        raise BulkWardError('schema mismatch')
    content = {k:v for k,v in doc.items() if k != 'calculation_digest'}
    if doc.get('calculation_digest') != _digest(content):
        raise BulkWardError('calculation digest mismatch')
    if not isinstance(doc.get('checks'), dict) or not doc['checks'] or not all(v is True for v in doc['checks'].values()):
        raise BulkWardError('invalid check set')
    if recompute and doc != build_payload():
        raise BulkWardError('receipt differs from fresh symbolic computation')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    choice=parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--write', type=Path, nargs='?', const=OUTPUT)
    choice.add_argument('--verify', type=Path, nargs='?', const=OUTPUT)
    args=parser.parse_args()
    if args.write:
        payload=build_payload()
        with args.write.open('x',encoding='utf-8') as f:
            json.dump(payload,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
    else:
        payload=_read_json(args.verify.read_bytes());validate_payload(payload)
    print(json.dumps({'checks':len(payload['checks']),'pass':all(payload['checks'].values()),
                      'calculation_digest':payload['calculation_digest']}))


if __name__ == '__main__':
    main()
