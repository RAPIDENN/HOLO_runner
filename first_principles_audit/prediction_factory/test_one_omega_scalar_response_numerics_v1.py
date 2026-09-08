"""Audit the numerical transcription against the independently derived Hessian."""
import numpy as np
import pytest
import sympy as sp
from . import one_omega_scalar_response_numerics_v1 as num
from . import verify_one_omega_topological_sector_reduction_v1 as exact


@pytest.fixture(scope='module')
def symbolic():return exact.derive_model()


@pytest.mark.parametrize('s,q,KT,Kv',[(0.2+0.4j,0.7,0.6+0.3j,0.2+0.5j),
    (0.6+1.2j,0.3,1.1-0.2j,0.8+0.1j),(1.2+0.2j,1.7,0.3+0.7j,0.4-0.1j)])
def test_complete_three_by_three_matches_symbolic_schur(symbolic,s,q,KT,Kv):
    P=num.frozen_parameters();S=symbolic['parameters'];p=np.sqrt(s*s+q*q)
    mapping={'M5c':'M','G':'G','k_inf':'k','Mb2':'Mb','beta':'beta','lambda_K':'lam',
             'eta':'eta','xi':'xi','B4bar':'b4','kappa_hat':'kap','Z5':'Z5'}
    point={S[key]:P[value] for key,value in mapping.items()}
    point.update({S['y']:sp.sqrt(sp.Integer(3)),S['K_T']:KT,S['K_v']:Kv,
                  S['p_material']:p,symbolic['frequency']:1j*s,symbolic['q']:q})
    expected=np.array(symbolic['scalar_3x3'].subs(point).evalf(18).tolist(),dtype=complex)
    measured=num.matrix_from_kernels(1j*s,q,p,KT,Kv,P)['matrix']
    assert np.max(abs(measured-expected))<2e-13*max(1,np.max(abs(expected)))


def test_preserves_literal_coefficients_and_explicit_squared_y_policy():
    P=num.frozen_parameters()
    assert P['lam']==-.5535068954004245 and P['y2']==3.0
    assert P['eta']==3.107013790800849


def test_euclidean_frequency_has_real_congruence_without_dropping_pivots():
    row=num.evaluate_scalar(0.3,0.7)
    T=np.diag([1,1j,1]);real=T@row['matrix']@T
    assert np.max(abs(real.imag))<1e-12
    assert abs(np.linalg.det(real)+row['determinant'])<1e-12*abs(row['determinant'])
    assert not row['no_RHP_zero_certified']
    assert row['P_material'].real>0 and row['P_Omega'].real>0


def test_distinct_cutoff_and_tolerance_agree_for_complete_scalar_matrix():
    one=num.evaluate_scalar(.3+.2j,.7,omega_min=.01,rtol=1e-8)
    other=num.evaluate_scalar(.3+.2j,.7,omega_min=.005,rtol=2e-10,atol=1e-13,max_nfev=14000)
    assert np.max(abs(one['matrix']-other['matrix']))<2e-8*np.max(abs(other['matrix']))


@pytest.mark.parametrize('s,q',[(0,.5),(1,0),(-1,.5),(1,-1)])
def test_does_not_silently_extend_gauge_or_frequency_domain(s,q):
    with pytest.raises(ValueError):num.evaluate_scalar(s,q)
