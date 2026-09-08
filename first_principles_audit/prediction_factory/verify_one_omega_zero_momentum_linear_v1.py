"""Direct q=0 reduction of the complete candidate boundary Hessian.

Recomputes H_full, rather than extending the q!=0 scalar gauge chart.
The five SO(3) traceless amplitudes use Frobenius normalization.  Nonzero
RHP denominators concern the selected finite-energy DtN branch and the
specified linear boundary block; its rank is never interpreted as particles.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import sympy as sp

if __package__:
    from . import verify_one_omega_topological_boundary_assembly_v1 as assembly
    from . import verify_one_omega_variational_dtn_v1 as variational
else:
    import verify_one_omega_topological_boundary_assembly_v1 as assembly
    import verify_one_omega_variational_dtn_v1 as variational

HERE = Path(__file__).resolve().parent
NOTE = HERE/'one_omega_zero_momentum_linear_lemma_v1.md'
TEST = HERE/'test_one_omega_zero_momentum_linear_v1.py'
OUTPUT = HERE/'artifacts/one_omega_zero_momentum_linear_v1.json'
ASSEMBLY_RECEIPT = assembly.OUTPUT
VARIATIONAL_RECEIPT = variational.OUTPUT
NOTE_SHA256 = '7f1129dd5b9b066ba1cafb20dcacac8a8a6d025586b16a172704bc98b1215d4f'
ASSEMBLY_SHA256 = 'c3c93cd779fe684329419012202d2cf697aee926efe5efbaee1cb0e47f781bce'
VARIATIONAL_SHA256 = '4ca0b1a1859610c6b3f472bf9704b83f23f1b740900ab387f844bcb985101095'
SCHEMA = 'holo.one-omega-zero-momentum-linear.v1'
LAMBDA_LITERAL = '-0.5535068954004245'
canonical_digest = assembly.canonical_digest


class ZeroMomentumError(ValueError):
    """A pin, a fresh upstream validation, or a reduction check failed."""


def _clean(value):
    return value.applyfunc(sp.cancel) if isinstance(value, sp.MatrixBase) else sp.cancel(value)


def _zero(value):
    return all(sp.cancel(x) == 0 for x in value) if isinstance(value, sp.MatrixBase) else sp.cancel(value) == 0


def _read_pinned(path: Path, expected: str) -> dict[str, Any]:
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ZeroMomentumError('source byte hash mismatch: '+Path(path).name)
    return assembly.source.source_oracle._read_json(raw)


def load_sources(note_path: Path = NOTE, assembly_path: Path = ASSEMBLY_RECEIPT,
                 variational_path: Path = VARIATIONAL_RECEIPT) -> dict[str, Any]:
    if hashlib.sha256(Path(note_path).read_bytes()).hexdigest() != NOTE_SHA256:
        raise ZeroMomentumError('zero-momentum note byte hash mismatch')
    assembled = _read_pinned(assembly_path, ASSEMBLY_SHA256)
    selected = _read_pinned(variational_path, VARIATIONAL_SHA256)
    # Both validators recompute their receipts. No production skip/cache flag.
    assembly.validate_payload(assembled)
    variational.validate_payload(selected)
    needed = ('selected_finite_energy_TT_and_R_DtN_exist_uniquely_in_RHP',
              'selected_finite_energy_DtN_holomorphic_in_RHP',
              'selected_DtN_strictly_positive_real_after_division_by_s',
              'material_and_Omega_pivots_have_no_RHP_zeros_on_selected_branch')
    if any(selected['decision'].get(key) is not True for key in needed):
        raise ZeroMomentumError('selected DtN hypotheses are not certified by the source receipt')
    policy = assembled['candidate_parameter_policy']
    pars = policy['parameters']
    exact_frozen = {'M5_cubed': sp.Integer(1), 'k_infinity': sp.Integer(1),
                    'compensator_metric_G': sp.Rational(6, 5),
                    'brane_Mb_squared': sp.Integer(2), 'lambda_K': sp.Rational(LAMBDA_LITERAL)}
    if any(sp.Rational(str(pars[key])) != value for key, value in exact_frozen.items()):
        raise ZeroMomentumError('literal candidate coefficients for Bstar changed')
    return {'note': {'name': Path(note_path).name, 'sha256': NOTE_SHA256},
            'assembly': {'name': Path(assembly_path).name, 'sha256': ASSEMBLY_SHA256,
                         'freshly_validated': True},
            'variational': {'name': Path(variational_path).name, 'sha256': VARIATIONAL_SHA256,
                            'freshly_validated': True},
            'candidate': assembled['sources']['candidate'],
            'candidate_action': assembled['sources']['candidate_action'],
            'candidate_parameter_policy': policy,
            'selected_DtN_decisions_used': {key: selected['decision'][key] for key in needed}}


def derive_positive_real_load() -> dict[str, Any]:
    sigma, x, beta = sp.symbols('sigma x beta_positive', positive=True)
    tau, y = sp.symbols('tau y', real=True)
    s, z = sigma+sp.I*tau, x+sp.I*y
    rho = x*x+y*y
    reciprocal_real = x/rho+sigma/beta
    reciprocal_imag = -y/rho+tau/beta
    load = beta*z/(beta+s*z)
    actual_real = sp.cancel(sp.expand_complex(sp.re(load)))
    denominator = (beta+sigma*x-tau*y)**2+(sigma*y+tau*x)**2
    expected_real = beta*(beta*x+sigma*rho)/denominator
    manifest_positive = reciprocal_real/(reciprocal_real**2+reciprocal_imag**2)
    B = sp.Symbol('Bstar_assumed_positive', positive=True)
    residuals = {
        'series_impedance_identity': sp.cancel(load-1/(1/z+s/beta)),
        'real_load_rational_identity': sp.cancel(actual_real-expected_real),
        'positive_reciprocal_representation': sp.cancel(actual_real-manifest_positive),
        'denominator_modulus_factorization': sp.cancel(
            denominator-beta**2*rho*(reciprocal_real**2+reciprocal_imag**2)),
    }
    checks = {name: value == 0 for name, value in residuals.items()}
    checks.update({'inverse_series_impedance_has_strictly_positive_real_part':
                       reciprocal_real.is_positive is True,
                   'Delta_beta_over_s_strictly_positive_real': manifest_positive.is_positive is True,
                   'minus_scalar_Schur_over_s_strictly_positive_real_if_Bstar_positive':
                       (3*B*sigma+manifest_positive).is_positive is True})
    return {'symbols': {'sigma': sigma, 'tau': tau, 'x': x, 'y': y, 'beta': beta,
                         's': s, 'z_is_GKv_over_s': z, 'Bstar': B},
            'load_Delta_beta_over_s': load, 'real_part': actual_real,
            'real_part_reference': expected_real, 'positive_reciprocal_form': manifest_positive,
            'reciprocal_real': reciprocal_real, 'denominator': denominator,
            'residuals': residuals, 'checks': checks,
            'hypotheses': 'Re(s)>0, Re(G*K_v/s)=x>0, beta>0; selected regular DtN branch'}


def derive_model() -> dict[str, Any]:
    base = assembly.derive_model()
    pars, index = base['parameters'], base['index']
    w, q = base['context']['w'], base['context']['q']
    s = sp.Symbol('s', zero=False, finite=True)
    H = _clean(base['H_full'].subs({w: sp.I*s, q: 0}, simultaneous=True))
    M, G, b, beta, lam, KT, Kv, kap, Z5, pm = (
        pars[n] for n in ('M5c', 'G', 'Mb2', 'beta', 'lambda_K', 'K_T', 'K_v',
                          'kappa_hat', 'Z5', 'p_material'))
    C0 = -M/base['A_prime_UV']
    Bstar = b*(1-3*lam)-2*C0
    FT, PD, PC = b*s*s+M*KT, G*Kv+beta, kap+2*Z5*pm
    null_names = ('n', 'N1', 'N2', 'N3', 'tau')
    tensor_basis = [sp.diag(1, -1, 0)/sp.sqrt(2), sp.diag(1, 1, -2)/sp.sqrt(6)]
    for i, j in ((0, 1), (0, 2), (1, 2)):
        E = sp.zeros(3)
        E[i, j] = E[j, i] = 1/sp.sqrt(2)
        tensor_basis.append(E)
    S = sp.zeros(15)
    for j, name in enumerate(null_names):
        S[index[name], j] = 1
    for column, E in enumerate(tensor_basis, 5):
        for i in range(3):
            for j in range(i, 3):
                S[index[f'H{i+1}{j+1}'], column] = E[i, j]
    for name in ('H11', 'H22', 'H33'):
        S[index[name], 10] = 2
    S[index['omega'], 11] = 1
    for i in range(1, 4):
        S[index[f'vphi{i}'], 11+i] = 1
    transformed = _clean(S.T*H*S)
    scalar_block = sp.Matrix([[-3*Bstar*s*s-G*Kv, G*Kv], [G*Kv, -PD]])
    expected = sp.zeros(15)
    for i in range(5, 10):
        expected[i, i] = -FT/4
    expected[10:12, 10:12] = scalar_block
    for i in range(12, 15):
        expected[i, i] = -PC
    extra_T = sp.zeros(15, 1)
    extra_T[index['tau']] = 1
    gauges = sp.Matrix.hstack(
        base['gauge_vectors']['time'].subs({w: sp.I*s, q: 0}),
        *(base['gauge_vectors'][f'space_{i}'].subs({w: sp.I*s, q: 0}) for i in range(1, 4)),
        extra_T)
    gauge_minor = sp.factor(gauges.extract([index[n] for n in null_names], range(5)).det())
    schur = _clean(scalar_block[0, 0]-scalar_block[0, 1]*scalar_block[1, 0]/scalar_block[1, 1])
    Delta = G*Kv*beta/PD
    scalar_expected = -3*Bstar*s*s-Delta
    left, right = sp.eye(2), sp.eye(2)
    left[0, 1] = -scalar_block[0, 1]/scalar_block[1, 1]
    right[1, 0] = -scalar_block[1, 0]/scalar_block[1, 1]
    Z0 = sp.cancel(base['Z'].subs(q, 0))
    trace_reference = sum(base['amplitudes'][n] for n in ('H11', 'H22', 'H33'))/6
    sigma, xT = sp.symbols('sigma xT_positive', positive=True)
    lam_literal = sp.Rational(LAMBDA_LITERAL)
    exponential_upper = sp.Rational(5, 4)
    Bstar_frozen = 2*(1-3*lam_literal)-2*sp.exp(sp.Rational(1, 5))
    Bstar_lower = 2*(1-3*lam_literal)-2*exponential_upper
    residuals = {
        'all_225_transformed_entries': _clean(transformed-expected),
        'five_null_coordinate_rows': H.extract([index[n] for n in null_names], range(15)),
        'five_gauge_vectors_null': _clean(H*gauges),
        'gauge_minor_s_fourth': sp.cancel(gauge_minor-s**4),
        'basis_determinant': sp.simplify(S.det()-sp.sqrt(6)/2),
        'SO3_Frobenius_Gram': sp.Matrix(5, 5, lambda i,j:
                                       sp.trace(tensor_basis[i]*tensor_basis[j])-(1 if i == j else 0)),
        'SO3_tensor_traces': sp.Matrix([sp.trace(E) for E in tensor_basis]),
        'Z_equals_spatial_trace_over_six': sp.cancel(Z0-trace_reference),
        'scalar_Schur': sp.cancel(schur-scalar_expected),
        'scalar_pivot_factorization': _clean(left*scalar_block*right-sp.diag(scalar_expected, -PD)),
        'scalar_eliminations_determinant_one': sp.Matrix([left.det()-1, right.det()-1]),
    }
    checks = {name: _zero(value) for name, value in residuals.items()}
    checks.update({'TT_denominator_positive_real_from_selected_kernel': (b*sigma+M*xT).is_positive is True,
                   'material_denominator_positive_real_at_p_equals_s': (kap+2*Z5*sigma).is_positive is True,
                   'literal_candidate_lambda_below_minus_half': (-sp.Rational(1, 2)-lam_literal).is_positive is True,
                   'geometric_series_upper_bound_is_five_fourths': 1/(1-sp.Rational(1,5)) == exponential_upper,
                   'Bstar_rigorous_lower_bound_exceeds_five_halves':
                       (Bstar_lower-sp.Rational(5, 2)).is_positive is True})
    wrong_frobenius = S.copy()
    wrong_frobenius[:, 7] *= sp.sqrt(2)
    wrong_gauge = gauges.copy()
    wrong_gauge[:, 4] = sp.zeros(15, 1)
    witnesses = {
        'omit_off_diagonal_Frobenius_normalization': _clean((wrong_frobenius.T*H*wrong_frobenius)[7, 7]+FT/4),
        'omit_time_only_khronon_reparametrization':
            wrong_gauge.extract([index[n] for n in null_names], range(5)).det()-s**4,
        'replace_series_spring_by_GKv': sp.cancel(schur-(-3*Bstar*s*s-G*Kv)),
        'drop_UV_scalar_contact': sp.cancel(schur-(-3*b*(1-3*lam)*s*s-Delta)),
        'flip_scalar_Schur_elimination_sign': sp.cancel(
            scalar_block[0,0]+scalar_block[0,1]*scalar_block[1,0]/scalar_block[1,1]-schur),
    }
    controls = {name: not _zero(value) for name, value in witnesses.items()}
    return {'s': s, 'parameters': pars, 'index': index, 'field_order': base['field_order'],
            'H_q_zero': H, 'transformed_order': (*null_names, 't1', 't2', 't3', 't4', 't5',
                                                'zeta', 'D', 'phi1', 'phi2', 'phi3'),
            'basis': S, 'basis_determinant': sp.simplify(S.det()), 'SO3_tensor_basis': tensor_basis,
            'transformed': transformed, 'reference': expected, 'gauge_vectors': gauges,
            'gauge_minor': gauge_minor, 'Z_at_q_zero': Z0, 'C0': C0, 'Bstar': Bstar,
            'F_T': FT, 'P_D': PD, 'P_chi': PC, 'scalar_block': scalar_block,
            'scalar_Schur': schur, 'Delta_beta': Delta,
            'scalar_left_elimination': left, 'scalar_right_elimination': right,
            'literal_candidate': {'lambda_K': lam_literal, 'Bstar': Bstar_frozen,
                                  'Bstar_lower_bound': Bstar_lower,
                                  'exponential_bound': 'exp(1/5)<5/4 by strict Taylor/geometric coefficient comparison',
                                  'not_a_decimal_to_exponential_identity': True},
            'algebraic_rank_under_nonzero_denominators': 10,
            'particle_count': None, 'checks': checks, 'residuals': residuals,
            'negative_controls': controls, 'negative_witnesses': witnesses}


def build_payload(note_path: Path = NOTE, assembly_path: Path = ASSEMBLY_RECEIPT,
                  variational_path: Path = VARIATIONAL_RECEIPT) -> dict[str, Any]:
    sources = load_sources(note_path, assembly_path, variational_path)
    model = derive_model()
    load = derive_positive_real_load()
    checks = {**model['checks'], **{'positive_real_'+k:v for k,v in load['checks'].items()}}
    if not all(checks.values()) or not all(model['negative_controls'].values()):
        raise ZeroMomentumError('q=0 matrix, positivity or negative-control check failed')
    files = (Path(__file__), TEST, Path(assembly.__file__), Path(variational.__file__))
    payload = {'schema': SCHEMA, 'sources': sources,
               'model': assembly.scalar._serialize(model),
               'positive_real_load': assembly.scalar._serialize(load),
               'checks': checks, 'negative_controls': model['negative_controls'],
               'scope': {'spatial_momentum': 'q=0', 'half_plane': 'Re(s)>0, s!=0, frequency=i*s',
                         'projector_domain': 'q^2-frequency^2=s^2!=0',
                         'DtN_domain': 'selected finite-energy variational IR branch only',
                         'material_branch': 'p_material=s at q=0 because Re(s)>0',
                         'gauge_extension': 'time-only T->f(T) at q=0, infinitesimal Fourier-Laplace modes',
                         'rank_interpretation': 'rank ten of the selected non-gauge boundary matrix, not a particle count',
                         'independent_BF_and_frame_domains_merged': False},
               'decision': {'q_zero_full_225_entry_reduction_checked': True,
                            'five_q_zero_gauge_directions_checked': True,
                            'q_zero_non_gauge_boundary_denominators_nonzero_on_selected_RHP_branch': True,
                            'literal_candidate_Bstar_exceeds_five_halves': True,
                            'particle_count_inferred_from_rank': False,
                            'static_s_zero_case_certified': False,
                            'imaginary_axis_uniform_extension_certified': False,
                            'other_IR_domains_certified': False,
                            'global_BF_edge_mode_absence_pass': False,
                            'A_minus_frame_connection_edge_sector_eliminated': False,
                            'independent_embedding_equations_certified': False,
                            'full_physical_constraint_reduction_certified': False,
                            'full_N7': False, 'full_P4': False, 'B4': False, 'B5': False},
               'provenance': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
               'runtime': {'sympy': sp.__version__}}
    payload['calculation_digest'] = canonical_digest(payload)
    return payload


def validate_payload(payload: dict[str, Any], note_path: Path = NOTE,
                     assembly_path: Path = ASSEMBLY_RECEIPT,
                     variational_path: Path = VARIATIONAL_RECEIPT) -> None:
    if not isinstance(payload, dict) or payload.get('schema') != SCHEMA:
        raise ZeroMomentumError('q=0 receipt schema mismatch')
    if payload.get('calculation_digest') != canonical_digest({k:v for k,v in payload.items() if k != 'calculation_digest'}):
        raise ZeroMomentumError('q=0 receipt digest mismatch')
    if payload != build_payload(note_path, assembly_path, variational_path):
        raise ZeroMomentumError('q=0 receipt differs from fresh derivation')


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write', nargs='?', const=OUTPUT, type=Path)
    modes.add_argument('--verify', nargs='?', const=OUTPUT, type=Path)
    args = parser.parse_args(argv)
    if args.write is not None:
        payload = build_payload()
        args.write.parent.mkdir(parents=True, exist_ok=True)
        with args.write.open('x', encoding='utf-8') as handle:
            json.dump(payload, handle, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write('\n')
    else:
        payload = assembly.source.source_oracle._read_json(args.verify.read_bytes())
        validate_payload(payload)
    print(json.dumps({'checks_passed': sum(payload['checks'].values()),
                      'negative_controls': payload['negative_controls'],
                      'calculation_digest': payload['calculation_digest']}))


if __name__ == '__main__':
    main()
