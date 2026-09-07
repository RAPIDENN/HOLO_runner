#!/usr/bin/env python3
"""Independent exact scalar-interface oracle for the pinned one-Omega charter.

Differentiate the scalar normal kinetic densities and the single wall potential,
then repeat in psi=Omega**(3/2)*phi coordinates. Geometry, embeddings, T, X and
therefore Acal are FIXED. Normal jets on the two outward sides remain independent;
common scalar traces implement the charter's restricted gluing domain.

This is a manually reviewed translation of identified literal action terms, not
a general action parser. No upstream generator, junction implementation or new
full-variation generator is imported. General symbolic fields and coefficients
are used; neither a background nor equations of motion are imposed. The normal
kinetic polynomial suffices for the outward momentum because a spacelike unit
normal is orthogonal to tangential derivatives. Derivative-free bulk potentials
have no boundary momentum; their reparametrization is checked separately.

The second-variation check concerns ONLY the scalar wall potential, with Acal
fixed. Its off-shell chain correction cannot be dropped just because the WHOLE
action is stationary: a wall gradient can be balanced by bulk flux. No moving
junction, metric variation, constraint closure or full Hessian is certified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CHARTER = HERE / 'artifacts' / 'one_omega_action_charter_gate.json'
OUTPUT = HERE / 'artifacts' / 'one_omega_scalar_interface_reparam_v1.json'
TEST = HERE / 'test_one_omega_scalar_interface_reparam_v1.py'
SCHEMA = 'holo.one-omega-scalar-interface-reparam.v1'
CHARTER_BYTES_SHA256 = 'b718cb68934a665cf0a7b89fafffcf2b9ebb2c0bb94c9386ff64f34d91a2e0ef'
ACTION_SHA256 = '93105331d9da311afa7845f9939dbd60617b929ae9ede23286fa26bedaa815c1'
CALCULATION_SHA256 = '12b753fc2646aebfbb117db95031c2765cdd2cc040025481de08613d183ad8db'
DIGEST_KEYS = ('upstream_bindings', 'action_charter', 'algebraic_audits',
               'certificate_ledger', 'decision')
LITERALS = {
    'bulk': 'S_bulk=sum_(eps in {plus,minus}) int_Meps sqrt(-g)*[M5^3*R/2-G*(nabla Omega)^2/2-U(Omega)-Z5_per_side*P_M^a*P_a^M/2-Z5_per_side*M^2*Omega^(-5)*V4(Omega^(3/2)*r_phi)]',
    'wall_background': 'S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2]',
    'Robin': 'S_R=-kappa_hat*int_Sigma sqrt(-gamma)*delta_ab*(varphi^a-y*Acal^a)*(varphi^b-y*Acal^b)/2',
    'superpotential': 'W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]',
    'bulk_potential': 'U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)',
    'full_V4': 'V4(r)=r^4/(2*sqrt(1+r^4))',
    'dimensionless_material_argument': 'r=Omega^(3/2)*r_phi',
}


class ScalarInterfaceError(ValueError):
    """A source, algebraic comparison or receipt failed verification."""


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'),
                     ensure_ascii=True, allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ScalarInterfaceError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def _bad_constant(value: str) -> None:
    raise ScalarInterfaceError(f'non-finite JSON constant: {value}')


def _read_json(raw: bytes) -> dict:
    try:
        value = json.loads(raw, object_pairs_hook=_unique_object,
                           parse_constant=_bad_constant)
    except (ValueError, UnicodeError) as exc:
        raise ScalarInterfaceError(f'invalid JSON: {exc}') from exc
    if not isinstance(value, dict):
        raise ScalarInterfaceError('JSON root must be an object')
    return value


def load_charter(path: Path = CHARTER) -> dict:
    """Verify one immutable input snapshot; never regenerate the upstream."""
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != CHARTER_BYTES_SHA256:
        raise ScalarInterfaceError('charter byte hash differs from pinned source')
    doc = _read_json(raw)
    if doc.get('schema') != 'holo.one-omega-action-charter-gate.v1':
        raise ScalarInterfaceError('charter schema mismatch')
    action = doc['action_charter']
    if (canonical_digest(action) != ACTION_SHA256 or
            doc['action_charter_digest']['sha256'] != ACTION_SHA256):
        raise ScalarInterfaceError('action digest mismatch')
    if (canonical_digest({k: doc[k] for k in DIGEST_KEYS}) != CALCULATION_SHA256 or
            doc['calculation_digest']['sha256'] != CALCULATION_SHA256):
        raise ScalarInterfaceError('calculation digest mismatch')
    for name, literal in LITERALS.items():
        if action['exact_action'][name] != literal:
            raise ScalarInterfaceError(f'unrecognized action literal: {name}')
    if action['definitions']['conformal_derivative'] != (
            'P_M^a=nabla_M phi^a+3*phi^a*nabla_M Omega/(2*Omega)'):
        raise ScalarInterfaceError('conformal derivative differs from translation')
    if action['definitions']['normal_convention'] != (
            'n_eps^M is outward pointing and n_eps^M*n_eps_M=+1'):
        raise ScalarInterfaceError('normal convention differs from translation')
    return doc


def _zero(expr: sp.Expr) -> bool:
    return sp.simplify(expr) == 0


def _simplify_matrix(matrix: sp.MatrixBase) -> sp.Matrix:
    return sp.Matrix(matrix).applyfunc(sp.simplify)


def derive_model() -> dict:
    """Two independent coordinate derivations, with exact three-component jets."""
    o = sp.Symbol('Omega', positive=True)
    G, Z, beta, kap, M5, k, mass = sp.symbols(
        'G Z beta kappa M5_cubed k_infinity M', positive=True)
    y = sp.Symbol('y', real=True)
    phi = sp.symbols('phi0:3', real=True)
    psi = sp.symbols('psi0:3', real=True)
    A = sp.symbols('A0:3', real=True)
    no = sp.symbols('normal_Omega_plus normal_Omega_minus', real=True)
    nf = tuple(sp.symbols(f'normal_phi_{side}0:3', real=True)
               for side in ('plus', 'minus'))
    ns = tuple(sp.symbols(f'normal_psi_{side}0:3', real=True)
               for side in ('plus', 'minus'))
    old = sp.Matrix([o, *phi])
    new = sp.Matrix([o, *psi])
    change = sp.Matrix([o, *(o**sp.Rational(3, 2)*f for f in phi)])
    jac = change.jacobian(old)
    subs = dict(zip(psi, change[1:]))
    P = tuple(sp.Matrix([nf[e][a] + sp.Rational(3, 2)*phi[a]*no[e]/o
                         for a in range(3)]) for e in range(2))
    for e in range(2):
        for a in range(3):
            subs[ns[e][a]] = o**sp.Rational(3, 2)*nf[e][a] + (
                sp.Rational(3, 2)*sp.sqrt(o)*phi[a]*no[e])
    old_kin = tuple(-G*no[e]**2/2 - Z*(P[e].dot(P[e]))/2 for e in range(2))
    new_kin = tuple(-G*no[e]**2/2 - Z*sum(s*s for s in ns[e])/(2*o**3)
                    for e in range(2))
    W = 3*M5*k*sp.exp(-G*o**2/(6*M5))
    tension = 2*W + beta*(o-1)**2/2
    wall_old = tension + kap*sum((phi[a]-y*A[a])**2 for a in range(3))/2
    # This potential is defined directly in the independent psi coordinates.
    wall_new = tension + kap*sum((psi[a]/o**sp.Rational(3, 2)-y*A[a])**2
                                 for a in range(3))/2
    old_mom = tuple(sp.Matrix([-sp.diff(old_kin[e], v)
                              for v in (no[e], *nf[e])]) for e in range(2))
    new_mom = tuple(sp.Matrix([-sp.diff(new_kin[e], v)
                              for v in (no[e], *ns[e])]) for e in range(2))
    grad_old = sp.Matrix([sp.diff(wall_old, q) for q in old])
    grad_new = sp.Matrix([sp.diff(wall_new, q) for q in new])
    J_old = _simplify_matrix(old_mom[0] + old_mom[1] + grad_old)
    J_new = _simplify_matrix(new_mom[0] + new_mom[1] + grad_new)
    J_pull = _simplify_matrix(jac.T * J_new.subs(subs, simultaneous=True))
    # Independent explicit reference, compared only after both differentiations.
    expected = sp.Matrix([
        G*(no[0]+no[1]) + sp.Rational(3, 2)*Z/o*sum(
            phi[a]*(P[0][a]+P[1][a]) for a in range(3)) + sp.diff(tension, o),
        *(Z*(P[0][a]+P[1][a]) + kap*(phi[a]-y*A[a]) for a in range(3))])
    H_old = sp.hessian(wall_old, old)
    H_congruence = jac.T * sp.hessian(wall_new, new).subs(subs, simultaneous=True) * jac
    correction = sp.zeros(4)
    for a in range(4):
        correction += grad_new[a].subs(subs, simultaneous=True)*sp.hessian(change[a], old)
    correction = _simplify_matrix(correction)
    H_pull = _simplify_matrix(H_congruence + correction)
    # V4 is expressed using r^4; no radial Taylor or small-amplitude truncation.
    r4_old = o**6*sum(f*f for f in phi)**2
    r4_new = sum(s*s for s in psi)**2
    U = sp.diff(W, o)**2/(2*G) - 2*W**2/(3*M5)
    bulk_V_old = U + Z*mass**2/o**5*r4_old/(2*sp.sqrt(1+r4_old))
    bulk_V_new = U + Z*mass**2/o**5*r4_new/(2*sp.sqrt(1+r4_new))
    kinetic_hessian = -sp.hessian(old_kin[0], (no[0], *nf[0]))
    return {
        'symbols': dict(omega=o, phi=phi, psi=psi, normal_omega=no,
                        normal_phi=nf, normal_psi=ns, A=A, G=G, Z=Z,
                        beta=beta, kappa=kap, y=y, M5=M5, k=k, mass=mass),
        'old_fields': old, 'new_fields': new, 'transform': change,
        'jacobian': jac, 'substitutions': subs, 'P': P,
        'old_kinetic': old_kin, 'new_kinetic': new_kin,
        'old_wall_potential': wall_old, 'new_wall_potential': wall_new,
        'old_momenta': old_mom, 'new_momenta': new_mom,
        'old_wall_gradient': grad_old, 'new_wall_gradient': grad_new,
        'old_junction': J_old, 'new_junction': J_new,
        'expected_junction': expected, 'pulled_new_junction': J_pull,
        'wall_hessian_old': H_old, 'wall_hessian_pulled': H_pull,
        'wall_hessian_congruence_only': H_congruence,
        'wall_hessian_correction': correction,
        'bulk_potential_old': bulk_V_old, 'bulk_potential_new': bulk_V_new,
        'kinetic_hessian': kinetic_hessian,
    }


def check_junction(candidate: sp.MatrixBase, reference: sp.MatrixBase | None = None) -> bool:
    """Compare symbolic expressions, never truth flags or parsed input strings."""
    if not isinstance(candidate, sp.MatrixBase) or candidate.shape != (4, 1):
        return False
    if any(expr.has(sp.Float) for expr in candidate):
        return False
    if reference is None:
        reference = derive_model()['old_junction']
    return candidate.shape == reference.shape and all(_zero(x) for x in candidate-reference)


def _flatten(matrix: sp.MatrixBase) -> list[str]:
    return [sp.sstr(sp.simplify(x)) for x in matrix]


def build_payload(charter_path: Path = CHARTER) -> dict:
    doc = load_charter(charter_path)
    m = derive_model()
    s = m['symbols']
    o, G, Z, kap = (s[k] for k in ('omega', 'G', 'Z', 'kappa'))
    phi, A, y = s['phi'], s['A'], s['y']
    substitutions = m['substitutions']
    rows: dict[str, sp.Expr] = {}
    for e in range(2):
        rows[f'normal_kinetic_reparam_side_{e}'] = (
            m['old_kinetic'][e] - m['new_kinetic'][e].subs(substitutions, simultaneous=True))
        residual = m['old_momenta'][e] - m['jacobian'].T*m['new_momenta'][e].subs(
            substitutions, simultaneous=True)
        for a, expr in enumerate(residual):
            rows[f'outward_momentum_reparam_side_{e}_field_{a}'] = expr
    rows['wall_potential_reparam'] = m['old_wall_potential'] - m['new_wall_potential'].subs(
        substitutions, simultaneous=True)
    rows['full_V4_bulk_potential_reparam'] = m['bulk_potential_old'] - m['bulk_potential_new'].subs(
        substitutions, simultaneous=True)
    for a in range(4):
        rows[f'junction_from_differentiation_matches_declared_form_{a}'] = (
            m['old_junction'][a]-m['expected_junction'][a])
        rows[f'junction_off_shell_chain_{a}'] = m['old_junction'][a]-m['pulled_new_junction'][a]
    H_expected = sp.diag(sp.diff(m['old_wall_potential'], o, 2), kap, kap, kap)
    for a in range(4):
        for b in range(4):
            rows[f'wall_second_chain_{a}_{b}'] = m['wall_hessian_old'][a,b]-m['wall_hessian_pulled'][a,b]
            rows[f'wall_second_scalar_form_{a}_{b}'] = m['wall_hessian_old'][a,b]-H_expected[a,b]
    K_expected = m['jacobian'].T * sp.diag(G, Z/o**3, Z/o**3, Z/o**3) * m['jacobian']
    for a in range(4):
        for b in range(4):
            rows[f'kinetic_field_metric_chain_{a}_{b}'] = m['kinetic_hessian'][a,b]-K_expected[a,b]
    rows['kinetic_field_metric_determinant'] = m['kinetic_hessian'].det()-G*Z**3
    # Incorrect alternatives must actually fail an algebraic comparison.
    reference = m['old_junction']
    mixed = sp.Rational(3, 2)*Z/o*sum(phi[a]*(m['P'][0][a]+m['P'][1][a]) for a in range(3))
    no_mix = reference-sp.Matrix([mixed,0,0,0])
    wrong_normals = m['old_momenta'][0]-m['old_momenta'][1]+m['old_wall_gradient']
    duplicate_robin = reference+sp.Matrix([0,*(kap*(phi[a]-y*A[a]) for a in range(3))])
    missing_induced = sp.Matrix(m['new_junction'])
    missing_induced[0] = G*sum(s['normal_omega']) + sp.diff(m['old_wall_potential'],o)
    wrong_chain = m['jacobian'].T*missing_induced.subs(substitutions, simultaneous=True)
    mutants = {
        'omitted_Omega_phi_momentum': no_mix,
        'subtracted_outward_sides': wrong_normals,
        'Robin_wall_counted_twice': duplicate_robin,
        'omitted_induced_Robin_Omega_derivative': wrong_chain,
    }
    negative = {name: not check_junction(candidate, reference) for name,candidate in mutants.items()}
    negative['omitted_off_shell_wall_Hessian_chain_correction'] = any(
        not _zero(expr) for expr in m['wall_hessian_correction'])
    residuals = {name: sp.sstr(sp.simplify(expr)) for name, expr in rows.items()}
    checks = {name: value == '0' for name, value in residuals.items()}
    if not all(checks.values()) or not all(negative.values()):
        raise ScalarInterfaceError('exact algebra or negative control failed')
    decision = {name: False for name in (
        'full_first_variation_pass', 'N4_JUNCTION_BENDING_pass', 'C4_HESSIAN_pass',
        'N2_CONSTRAINTS_pass', 'N3_CHARACTERISTICS_pass', 'N5_COUPLED_BVP_pass',
        'N6_GLOBAL_STABILITY_pass', 'N7_LINEAR_REDUCTION_pass',
        'P4_full_same_action_pass', 'B4_pass', 'B5_pass')}
    decision['fixed_geometry_scalar_interface_pass'] = True
    payload = {
        'schema': SCHEMA,
        'source': {'path': str(CHARTER.relative_to(REPO)),
                   'sha256': CHARTER_BYTES_SHA256,
                   'action_charter_sha256': ACTION_SHA256,
                   'calculation_sha256': CALCULATION_SHA256,
                   'translation': 'manual literal-to-SymPy translation; source bytes and semantic digests pinned',
                   'translated_literals': LITERALS,
                   'charter_junction_convention_for_human_comparison': doc['algebraic_audits']['background_and_junctions']['junction_convention']},
        'scope': {
            'Omega_positive': True, 'internal_triplet_components': 3,
            'outward_spacelike_unit_normals': True,
            'two_sides_have_independent_normal_jets': True,
            'common_scalar_traces': True,
            'fixed_fields': ['g_plus', 'g_minus', 'Y_plus', 'Y_minus', 'T', 'X', 'Acal'],
            'on_shell_substitution_used': False, 'background_specialization_used': False,
            'numeric_sampling_used_as_proof': False,
            'bulk_potential_is_exact_full_V4': True,
            'bulk_Euler_Lagrange_equations_derived': False,
            'second_variation_scope': 'scalar wall potential only; fixed geometry and Acal',
            'wall_Hessian_gradient_correction': 'required even when bulk flux balances the wall gradient',
            'scalar_kinetic_metric_only': 'positive field metric is not a constrained gravity stability theorem',
        },
        'equations': {
            'field_order': ['Omega','phi0','phi1','phi2'],
            'new_field_order': ['Omega','psi0','psi1','psi2'],
            'transformation': _flatten(m['transform']),
            'old_junction_equals_zero': _flatten(reference),
            'new_junction_equals_zero': _flatten(m['new_junction']),
            'old_wall_scalar_Hessian_row_major': _flatten(m['wall_hessian_old']),
            'wall_Hessian_chain_correction_row_major': _flatten(m['wall_hessian_correction']),
        },
        'checks': checks, 'residuals': residuals,
        'negative_controls': negative,
        'negative_control_residuals': {name: _flatten(candidate-reference) for name,candidate in mutants.items()},
        'decision': decision,
        'provenance': {
            'verifier': {'path': str(Path(__file__).resolve().relative_to(REPO)),
                         'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'test': {'path': str(TEST.relative_to(REPO)),
                     'sha256': hashlib.sha256(TEST.read_bytes()).hexdigest()},
            'sympy_version': sp.__version__,
        },
    }
    payload['calculation_digest'] = {'algorithm': 'sha256(canonical-json(payload without calculation_digest))',
                                      'sha256': canonical_digest(payload)}
    return payload


def validate_payload(payload: dict, charter_path: Path = CHARTER) -> None:
    """Re-derive all expressions; rehashing incorrect flags is insufficient."""
    if not isinstance(payload, dict):
        raise ScalarInterfaceError('receipt must be a dictionary')
    core = {key: value for key,value in payload.items() if key != 'calculation_digest'}
    if payload.get('calculation_digest', {}).get('sha256') != canonical_digest(core):
        raise ScalarInterfaceError('receipt digest mismatch')
    expected = build_payload(charter_path)
    if canonical_digest(payload) != canonical_digest(expected):
        raise ScalarInterfaceError('receipt differs from independently recomputed expressions or provenance')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', nargs='?', const=str(OUTPUT), type=Path,
                       help='write a new receipt exclusively; never replace an existing file')
    group.add_argument('--verify', type=Path, help='recompute and verify an existing receipt')
    args = parser.parse_args()
    if args.verify:
        payload = _read_json(args.verify.read_bytes())
        validate_payload(payload)
    else:
        payload = build_payload()
        if args.write:
            with args.write.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps({'schema': SCHEMA, 'exact_checks': len(payload['checks']),
                      'negative_controls_rejected': sum(payload['negative_controls'].values()),
                      'decision': payload['decision'],
                      'calculation_sha256': payload['calculation_digest']['sha256']}, sort_keys=True))


if __name__ == '__main__':
    main()
