"""Independent scope, exact interval and complex-frequency controls."""
import copy
import json
from decimal import Decimal
import pytest
import sympy as sp
from . import verify_one_omega_scalar_shift_static_v1 as oracle


@pytest.fixture(scope='module')
def model():return oracle.derive_model()


def test_regrouping_and_both_dynamic_pivots_equal_full_schur(model):
    for key in ('complete_matrix_regrouping','shift_pivot','lapse_pivot_after_shift','static_matrix_from_full_response'):
        assert oracle.sectors.zero(model['residuals'][key])
    assert all(model['checks'].values())


def test_literal_candidate_coefficients_are_the_proved_ones():
    p=oracle.HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
    data=json.loads(p.read_text(),parse_float=Decimal)
    values=data['exact_classical_charter']['coefficient_policy']['parameters']
    expected={'M5_cubed':'1.0','k_infinity':'1.0','compensator_metric_G':'1.2',
              'brane_Mb_squared':'2.0','brane_beta':'2.0','eta':'3.107013790800849',
              'lambda_K':'-0.5535068954004245','xi':'1.0','B4_bar':'0.8',
              'Robin_kappa_hat':'1.0','Robin_y_squared':'3.0','material_Z5_per_side':'1.0'}
    assert all(values[k]==Decimal(v) for k,v in expected.items())


def test_IR_margin_is_rational_positive_and_not_a_rounded_equality(model):
    margin=model['rational_IR_lower_margin']
    assert isinstance(margin,sp.Rational) and 0<margin<sp.Rational(1,10**15)
    # A slightly larger decimal changes the needed unilateral hypothesis.
    assert margin-sp.Rational(1,10**12)<0


def test_middle_interval_certificates_have_no_positive_or_zero_coefficient(model):
    for row in model['endpoint_certificates'].values():
        assert row['positive_denominator']
        assert row['shifted_coefficients']
        assert all(isinstance(c,sp.Rational) and c<0 for c in row['shifted_coefficients'])


def test_small_and_large_q_proofs_have_strict_margins(model):
    assert model['small_q_determinant_upper_coefficient']==-sp.Rational(4581,250)
    assert model['checks']['large_q_E_minus_two_P_negative']
    assert model['checks']['large_q_c_coefficient_negative']


def test_static_kernel_positivity_alone_does_not_force_the_sign(model):
    # Abstract positive coefficients, not claimed to arise from a BPS solution:
    # at E=2P and B=0, positive c contributes +2Pc.
    F=model['static_determinant'];sy={v.name:v for v in F.free_symbols}
    mutant=F.subs({sy['m']:1,sy['E']:6,sy['c']:sp.Rational(1,100),sy['B']:0})
    assert mutant==sp.Rational(3,50)>0


def test_double_schur_preserves_the_determinant_algebraically():
    a,b,c,d,e,f=sp.symbols('a b c d e f')
    H=sp.Matrix([[a,b,c],[b,d,e],[c,e,f]])
    lapse=a-b*b/d
    final=f-e*e/d-(c-b*e/d)**2/lapse
    assert sp.cancel(H.det()-d*lapse*final)==0


def test_positive_rotated_pivot_does_not_require_positive_unrotated_pivot(model):
    # One finite positive spectral atom illustrates why rotations matter.
    s=sp.Rational(1,10)+10*sp.I;q=1;mass=6;A=3;ell=98
    F=mass/(ell+s*s+q*q);pivot=A-s*s*F/9
    assert sp.re(sp.cancel(pivot))<0
    assert sp.re(sp.cancel(s*pivot))>0
    assert A>mass/9


def test_receipt_cannot_promote_dynamic_scalar_stability_by_rehashing():
    payload=oracle.build_payload()
    assert payload['decision']['static_scalar_matrix_invertible_for_every_q_positive']
    assert not payload['decision']['final_dynamic_scalar_factor_has_no_RHP_zero']
    mutant=copy.deepcopy(payload);mutant['decision']['final_dynamic_scalar_factor_has_no_RHP_zero']=True
    mutant['calculation_digest']=oracle.canonical_digest({k:v for k,v in mutant.items() if k!='calculation_digest'})
    with pytest.raises(ValueError,match='fresh derivation'):oracle.validate_payload(mutant)
