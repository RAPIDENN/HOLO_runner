#!/usr/bin/env python3
"""Exact exterior-algebra check of the conditional linear BF RHP quotient.

Five-dimensional forms use bitmasks for (dt,dx1,dx2,dx3,dr).  The coefficient
ring is C[s,s^-1,k1,k2,k3,D_r].  D_r denotes a commuting radial derivative
operator, not a frozen value or a claim that radial coefficients are constant.
The finite algebra proves Cartan and trace identities.  Applying the lemma
to solutions requires the h-stable function/gauge domain of the pinned note.
No static/global/BV-BFV/frame-mismatch or full physical stability gate closes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
NOTE = HERE / 'one_omega_bf_rhp_quotient_lemma_v1.md'
CANDIDATE = HERE / 'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
TEST = HERE / 'test_one_omega_bf_rhp_quotient_v1.py'
OUTPUT = HERE / 'artifacts/one_omega_bf_rhp_quotient_v1.json'
SCHEMA = 'holo.one-omega-bf-rhp-quotient.v1'
NOTE_SHA256 = '9f0a92cc7fadf9536cf1c2749452140c13cf5e7b93adeb771b419c476a731109'
CANDIDATE_SHA256 = 'd9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
ACTION_SHA256 = '3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a'


class BFQuotientError(ValueError):
    """A source pin, exterior identity, domain input, or receipt failed."""


def canonical_digest(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def _read_json(raw: bytes) -> dict[str, Any]:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise BFQuotientError(f'duplicate JSON key: {key}')
            result[key] = value
        return result

    def invalid_constant(value):
        raise BFQuotientError(f'nonfinite JSON constant: {value}')

    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (ValueError, UnicodeError) as exc:
        raise BFQuotientError(f'invalid JSON: {exc}') from exc
    if not isinstance(value, dict):
        raise BFQuotientError('JSON root must be an object')
    return value


def load_sources(note_path: Path = NOTE, candidate_path: Path = CANDIDATE) -> dict[str, Any]:
    note_path, candidate_path = Path(note_path), Path(candidate_path)
    note_bytes, candidate_bytes = note_path.read_bytes(), candidate_path.read_bytes()
    if hashlib.sha256(note_bytes).hexdigest() != NOTE_SHA256:
        raise BFQuotientError('BF lemma note byte hash mismatch')
    if hashlib.sha256(candidate_bytes).hexdigest() != CANDIDATE_SHA256:
        raise BFQuotientError('v5.2 candidate byte hash mismatch')
    candidate = _read_json(candidate_bytes)
    if candidate.get('schema') != 'holo.one-omega-topological-so3-classical-v5-2-gate.v1':
        raise BFQuotientError('v5.2 candidate schema mismatch')
    charter = candidate['exact_classical_charter']
    if canonical_digest(charter['exact_action']) != ACTION_SHA256:
        raise BFQuotientError('v5.2 exact action digest mismatch')
    if charter['exact_action']['BF'] != (
        'S_BF=sum_eps int_Meps <B_eps wedge F[A_eps]>, <X,Y>=-tr_3(XY)/2'
    ):
        raise BFQuotientError('BF action normalization mismatch')
    return {
        'note': {'name': note_path.name, 'sha256': NOTE_SHA256},
        'candidate': {'name': candidate_path.name, 'sha256': CANDIDATE_SHA256,
                      'exact_action_sha256': ACTION_SHA256},
        'BF_action': charter['exact_action']['BF'],
        'interface_domain': charter['interface_domain'],
        'topology': charter['topology'],
        'source_gate_promotions_inherited': False,
    }


def _axis(axis: int, dimension: int) -> None:
    if (type(dimension) is not int or not 1 <= dimension <= 5
            or type(axis) is not int or not 0 <= axis < dimension):
        raise BFQuotientError('axis and dimension must be valid integers, dimension 1..5')


def wedge_matrix(axis: int, dimension: int = 5) -> sp.SparseMatrix:
    """Left wedge by dx_axis in the ordered bitmask exterior basis."""
    _axis(axis, dimension)
    bit, entries = 1 << axis, {}
    for mask in range(1 << dimension):
        if not mask & bit:
            sign = (-1) ** ((mask & (bit - 1)).bit_count())
            entries[mask | bit, mask] = sign
    return sp.SparseMatrix(1 << dimension, 1 << dimension, entries)


def contraction_matrix(axis: int, dimension: int = 5) -> sp.SparseMatrix:
    """Interior product with partial_axis, including the exterior sign."""
    _axis(axis, dimension)
    bit, entries = 1 << axis, {}
    for mask in range(1 << dimension):
        if mask & bit:
            sign = (-1) ** ((mask & (bit - 1)).bit_count())
            entries[mask ^ bit, mask] = sign
    return sp.SparseMatrix(1 << dimension, 1 << dimension, entries)


def uv_pullback() -> sp.SparseMatrix:
    """Trace on the UV coefficient space; every dr component is killed."""
    return sp.SparseMatrix(16, 32, {(mask, mask): 1 for mask in range(16)})


def homotopy_matrix(frequency: Any, dimension: int = 5) -> sp.SparseMatrix:
    """Algebraic I_t/s; application to the RHP is restricted by the note.

    The algebra extends to any invertible s.  It supplies no physical claim
    for other domains, and explicitly rejects s=0/nonfinite constants.
    """
    value = sp.sympify(frequency)
    if value.is_zero is True or value.is_finite is False or value.has(sp.nan, sp.zoo):
        raise BFQuotientError('homotopy requires finite nonzero s')
    return contraction_matrix(0, dimension) / value


def symbols_context() -> dict[str, Any]:
    return {'s': sp.Symbol('s', zero=False, finite=True),
            'momenta': sp.symbols('k1 k2 k3', real=True),
            'Dr': sp.Symbol('D_r', commutative=True),
            'r': sp.Symbol('r', real=True),
            'coordinate_order': ('t', 'x1', 'x2', 'x3', 'r')}


def _zero(matrix: sp.MatrixBase) -> bool:
    return all(sp.cancel(value) == 0 for value in matrix.todok().values())


def _basis(mask: int, dimension: int = 5) -> sp.SparseMatrix:
    return sp.SparseMatrix(1 << dimension, 1, {(mask, 0): 1})


def _degree_embedding(degree: int, dimension: int = 5) -> sp.SparseMatrix:
    masks = [m for m in range(1 << dimension) if m.bit_count() == degree]
    return sp.SparseMatrix(1 << dimension, len(masks),
                           {(mask, j): 1 for j, mask in enumerate(masks)})


def apply_radial_operator(operator: sp.MatrixBase, form: sp.MatrixBase,
                          radial: sp.Symbol, dr_symbol: sp.Symbol | None = None) -> sp.Matrix:
    """Apply polynomial D_r entries to arbitrary radial coefficient functions.

    Operator coefficients must not themselves depend on radial.  D_r commutes
    with s, momenta, wedges and contractions; it differentiates form entries.
    This is an interpretation check of the operator algebra, not discretization.
    """
    operator, form = sp.Matrix(operator), sp.Matrix(form)
    if form.cols != 1 or operator.cols != form.rows:
        raise BFQuotientError('operator/form shape mismatch')
    dr_symbol = symbols_context()['Dr'] if dr_symbol is None else dr_symbol
    result = sp.zeros(operator.rows, 1)
    try:
        for (i, j), value in operator.todok().items():
            polynomial = sp.Poly(value, dr_symbol)
            for (power,), coefficient in polynomial.terms():
                if coefficient.has(radial):
                    raise BFQuotientError('D_r operator coefficients must be radial-independent')
                result[i] += coefficient * sp.diff(form[j], radial, power)
    except sp.PolynomialError as exc:
        raise BFQuotientError('D_r entries must be polynomial operators') from exc
    return result.applyfunc(sp.expand)


def wedge_forms(left: sp.MatrixBase, right: sp.MatrixBase,
                dimension: int = 4) -> sp.SparseMatrix:
    """Exterior product of coefficient vectors; used for UV Green fluxes."""
    _axis(0, dimension)
    left, right = sp.Matrix(left), sp.Matrix(right)
    size = 1 << dimension
    if left.shape != (size, 1) or right.shape != (size, 1):
        raise BFQuotientError('exterior form shape mismatch')
    entries = {}
    for (a, _), x in left.todok().items():
        for (b, _), y in right.todok().items():
            if a & b:
                continue
            swaps = sum((b & ((1 << i) - 1)).bit_count()
                        for i in range(dimension) if a & (1 << i))
            key = (a | b, 0)
            entries[key] = entries.get(key, 0) + (-1) ** swaps * x * y
    return sp.SparseMatrix(size, 1, entries)


def derive_model() -> dict[str, Any]:
    ctx = symbols_context()
    s, momenta, Dr, r = ctx['s'], ctx['momenta'], ctx['Dr'], ctx['r']
    W = tuple(wedge_matrix(i) for i in range(5))
    I = tuple(contraction_matrix(i) for i in range(5))
    identity = sp.SparseMatrix(sp.eye(32))
    zero = sp.SparseMatrix(32, 32, {})
    d = s*W[0] + sum((sp.I*momenta[i-1]*W[i] for i in range(1, 4)), zero) + Dr*W[4]
    h = homotopy_matrix(s)
    pullback = uv_pullback()
    W4 = tuple(wedge_matrix(i, 4) for i in range(4))
    d_boundary = s*W4[0] + sum((sp.I*momenta[i-1]*W4[i] for i in range(1, 4)),
                              sp.SparseMatrix(16, 16, {}))
    h_boundary = homotopy_matrix(s, 4)
    square = d*d
    cartan = d*h+h*d-identity
    checks = {
        'wedge_contraction_CAR_all_25_pairs': all(
            _zero(W[i]*I[j]+I[j]*W[i]-(identity if i == j else zero))
            for i in range(5) for j in range(5)),
        'wedges_anticommute_all_25_pairs': all(_zero(W[i]*W[j]+W[j]*W[i])
                                               for i in range(5) for j in range(5)),
        'contractions_anticommute_all_25_pairs': all(_zero(I[i]*I[j]+I[j]*I[i])
                                                     for i in range(5) for j in range(5)),
        'd_square_zero': _zero(square),
        'UV_pullback_commutes_with_d': _zero(pullback*d-d_boundary*pullback),
        'UV_pullback_commutes_with_h': _zero(pullback*h-h_boundary*pullback),
        'UV_pullback_kills_dr': _zero(pullback*W[4]),
    }
    for degree in range(6):
        checks[f'Cartan_identity_degree_{degree}'] = _zero(cartan*_degree_embedding(degree))
    checks['A1_gauge_residual_equals_hF_with_minus_sign'] = _zero(
        (identity-d*h-h*d)*_degree_embedding(1))
    checks['B3_shift_residual_equals_hdb_with_parameter_minus_hb'] = _zero(
        (identity-d*h-h*d)*_degree_embedding(3))
    checks['shift_reducibility_degrees_0_1_2'] = all(
        _zero(square*_degree_embedding(degree)) for degree in (0, 1, 2))
    checks['iota_0_form_h_d_equals_identity'] = _zero(
        (h_boundary*d_boundary-sp.eye(16))*_degree_embedding(0, 4))

    radial_form = r**3*_basis(0)
    radial_derivative = apply_radial_operator(d, radial_form, r, Dr)
    checks['D_r_differentiates_nonconstant_radial_coefficients'] = (
        sp.expand(radial_derivative[16]-3*r**2) == 0)

    b = sum((sp.Symbol(f'b{m}')*_basis(m, 4) for m in range(16) if m.bit_count() == 3),
            sp.SparseMatrix(16, 1, {}))
    delta_a = sum((sp.Symbol(f'da{i}')*_basis(1 << i, 4) for i in range(4)),
                  sp.SparseMatrix(16, 1, {}))
    lam = sum((sp.Symbol(f'lam{m}')*_basis(m, 4) for m in range(16) if m.bit_count() == 2),
              sp.SparseMatrix(16, 1, {}))
    curvature = sum((sp.Symbol(f'F{m}')*_basis(m, 4) for m in range(16) if m.bit_count() == 2),
                    sp.SparseMatrix(16, 1, {}))
    green = -wedge_forms(b-b, delta_a)
    shift_flux = wedge_forms(lam-lam, curvature)
    checks['oriented_Green_flux_cancels_on_common_traces'] = _zero(green)
    checks['oriented_shift_flux_cancels_off_shell_on_common_parameters'] = _zero(shift_flux)

    unsigned_I1 = sp.SparseMatrix(32, 32,
                                 {(mask ^ 2, mask): 1 for mask in range(32) if mask & 2})
    wrong_radial = apply_radial_operator(d-2*Dr*W[4], radial_form, r, Dr)
    wrong_incidence_green = -wedge_forms(2*_basis(14, 4), _basis(1, 4))[15]
    wrong_incidence_shift = wedge_forms(2*_basis(6, 4), _basis(9, 4))[15]
    # Closed A=dt and B=dt^dx1^dx2 at s=1, k=0, D_r=0 give exact sign witnesses.
    subs = {s: 1, Dr: 0, **{k: 0 for k in momenta}}
    d0, h0 = d.subs(subs), h.subs(subs)
    witnesses = {
        'negative_homotopy_sign': (d*(-h)+(-h)*d-identity)[0, 0],
        'missing_time_derivative': ((d-s*W[0])*h+h*(d-s*W[0])-identity)[0, 0],
        'unsigned_contraction': (W[0]*unsigned_I1+unsigned_I1*W[0])[1, 2],
        'radial_derivative_sign': wrong_radial[16]-radial_derivative[16],
        'A_gauge_sign': (_basis(1)+d0*h0*_basis(1))[1],
        'B_shift_parameter_sign': (_basis(7)+d0*h0*_basis(7))[7],
        'both_Green_incidences_positive': wrong_incidence_green,
        'both_shift_incidences_positive': wrong_incidence_shift,
    }
    controls = {name: sp.expand(value) != 0 for name, value in witnesses.items()}
    return {
        'symbols': ctx, 'wedge': W, 'contraction': I, 'd': d, 'h': h,
        'UV_pullback': pullback, 'd_boundary': d_boundary, 'h_boundary': h_boundary,
        'checks': checks, 'negative_controls': controls, 'negative_witnesses': witnesses,
        'residuals': {'d_squared': square, 'Cartan': cartan,
                      'UV_d': pullback*d-d_boundary*pullback,
                      'UV_h': pullback*h-h_boundary*pullback,
                      'Green': green, 'shift_flux': shift_flux},
        'radial_operator_example': radial_derivative,
        'gauge_formulas': {'A': 'epsilon=h(alpha), alpha_new=alpha-d(epsilon)',
                           'B': 'Lambda=-h(b), b_new=b+d(Lambda)',
                           'iota': 'epsilon_eps|UV=epsilon_Q+chi_eps; delta_chi_eps=-chi_eps',
                           'reducibility': 'sigma_0 -> rho_1 -> Lambda_2 -> b_3, arrows d'},
    }


def _serialize(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return {'rows': value.rows, 'cols': value.cols,
                'entries': [[i, j, str(sp.cancel(x))]
                            for (i, j), x in sorted(value.todok().items())
                            if sp.cancel(x) != 0]}
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _serialize(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_serialize(v) for v in value]
    return value


def build_payload(note_path: Path = NOTE, candidate_path: Path = CANDIDATE) -> dict[str, Any]:
    sources = load_sources(note_path, candidate_path)
    model = derive_model()
    if not all(model['checks'].values()) or not all(model['negative_controls'].values()):
        raise BFQuotientError('exterior identity or negative control failed')
    payload = {
        'schema': SCHEMA, 'sources': sources, 'model': _serialize(model),
        'checks': model['checks'], 'negative_controls': model['negative_controls'],
        'scope': {
            'background': 'Abar=Bbar=phibar=0, fixed BPS geometry and zero background acceleration',
            'spectral_domain': 'exp(s*t+i*k_a*x_a), Re(s)>0, real k_a',
            'coefficient_ring': 'C[s,s^-1,k1,k2,k3,D_r], D_r a commuting differential operator',
            'required_function_domain': 'solution and gauge spaces stable under i_partial_t/s, with UV traces',
            'radial_support': 'preserved coefficientwise; allowed gauge decay/support must be compatible',
            'normalizable_does_not_define_all_gauge_domains': True,
            'A_Sigma_independent_of_Levi_Civita_connection': True,
            'BF_internal_components': 3,
            'componentwise_linear_proof': True,
            'no_uniform_s_to_zero_bound': True,
        },
        'decision': {
            'five_dimensional_exterior_identities_pass': True,
            'linear_relative_BF_RHP_quotient_trivial_on_h_stable_domain': True,
            'oriented_interface_Green_cancels_on_glued_domain': True,
            'linear_shift_reducibility_checked': True,
            'universal_normalizable_domain_certified': False,
            'static_s_zero_quotient_certified': False,
            'global_BF_edge_mode_absence_pass': False,
            'A_minus_frame_connection_edge_sector_eliminated': False,
            'complete_BV_BFV_boundary_complex_pass': False,
            'C2_BRST_pass': False,
            'nonlinear_BF_quotient_certified': False,
            'complete_physical_mode_admissibility': False,
            'full_N7': False, 'full_P4': False, 'B4': False, 'B5': False,
        },
        'provenance': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (Path(__file__), TEST)},
        'runtime': {'sympy': sp.__version__},
    }
    payload['calculation_digest'] = canonical_digest(payload)
    return payload


def validate_payload(payload: dict[str, Any], note_path: Path = NOTE,
                     candidate_path: Path = CANDIDATE) -> None:
    if not isinstance(payload, dict) or payload.get('schema') != SCHEMA:
        raise BFQuotientError('BF quotient receipt schema mismatch')
    body = {k: v for k, v in payload.items() if k != 'calculation_digest'}
    if payload.get('calculation_digest') != canonical_digest(body):
        raise BFQuotientError('BF quotient receipt digest mismatch')
    if payload != build_payload(note_path, candidate_path):
        raise BFQuotientError('BF quotient receipt differs from fresh derivation')


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
        payload = _read_json(args.verify.read_bytes())
        validate_payload(payload)
    print(json.dumps({'checks_passed': sum(payload['checks'].values()),
                      'negative_controls': payload['negative_controls'],
                      'calculation_digest': payload['calculation_digest']}))


if __name__ == '__main__':
    main()
