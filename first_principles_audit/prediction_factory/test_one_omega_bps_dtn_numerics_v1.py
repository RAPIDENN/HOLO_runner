"""Independent reference, convergence and failure checks for the bounded DtN solver."""
import cmath
import math
import numpy as np
import pytest
from . import one_omega_bps_dtn_numerics_v1 as num


@pytest.mark.parametrize("sector", ["TT", "scalarR"])
@pytest.mark.parametrize("p,k", [(0.7+0.2j,1.0),(0.3+0.8j,0.6),(2.0+0.1j,1.7)])
def test_geometric_limit_matches_exact_bessel_at_different_scales(sector,p,k):
    row=num.evaluate_dtn(p,sector=sector,k=k,a=0)
    reference=num.bessel_reference(p,sector=sector,k=k)
    assert abs(row['kernel']-reference)<3e-9*abs(reference)
    assert row['solver_success'] and not row['physical_claims_certified']
    assert not row['numerical_error_bound_certified']
    assert row['rhs_calls']==row['nfev'] and row['steps']>0


@pytest.mark.parametrize("sector", ["TT", "scalarR"])
def test_cutoff_tolerance_and_distinct_integration_methods_agree(sector):
    p=0.4+0.1j
    coarse=num.evaluate_dtn(p,sector=sector,omega_min=0.02,rtol=1e-8,atol=1e-11)
    fine=num.evaluate_dtn(p,sector=sector,omega_min=0.01,rtol=2e-10,atol=1e-13,max_nfev=12000)
    other=num.evaluate_dtn(p,sector=sector,omega_min=0.01,method='DOP853',rtol=2e-10,atol=1e-13,max_nfev=12000)
    assert abs(fine['kernel']-other['kernel'])<1e-8*abs(fine['kernel'])
    assert abs(coarse['kernel']-fine['kernel'])<2e-7*abs(fine['kernel'])
    assert coarse['cutoff']==0.02 and fine['cutoff']==0.01


@pytest.mark.parametrize("sector", ["TT", "scalarR"])
def test_conjugation_and_energy_sign_at_complex_frequency(sector):
    s=0.07+1.2j;q=0.5;p=cmath.sqrt(s*s+q*q)
    one=num.evaluate_dtn(p,sector=sector,max_nfev=12000)
    other=num.evaluate_dtn(p.conjugate(),sector=sector,max_nfev=12000)
    assert abs(other['kernel']-one['kernel'].conjugate())<1e-9*abs(one['kernel'])
    assert (one['kernel']/s).real>0


@pytest.mark.parametrize("sector,exponent", [("TT",2),("scalarR",4)])
def test_low_momentum_limit_matches_independent_zero_mode_quadrature(sector,exponent):
    from scipy.integrate import quad
    a=0.2;k=1.3;p=1e-3
    norm=2*quad(lambda o: math.exp(a*o*o)*o**(exponent-1)/k,0,1,epsabs=1e-13,epsrel=1e-13)[0]
    row=num.evaluate_dtn(p,sector=sector,a=a,k=k,rtol=2e-10,atol=1e-16,max_nfev=14000)
    assert abs(row['kernel']/p**2-norm)<1e-5*norm


def test_budget_exhaustion_returns_no_kernel():
    with pytest.raises(num.DTNEvaluationError,match='budget') as exc:
        num.evaluate_dtn(0.7+0.1j,max_nfev=1)
    assert exc.value.diagnostics['nfev']==1
    assert 'kernel' not in exc.value.diagnostics


@pytest.mark.parametrize("p,options", [(0j,{}),(-1+1j,{}),(1j,{}),(float('nan'),{}),(True,{}),
    (1,{'k':0}),(1,{'a':-1}),(1,{'omega_min':1}),(1,{'omega_min':0.2}),
    (1,{'a':20,'omega_min':0.01}),(1,{'method':'RK999'}),(1,{'rtol':1e-20}),
    (1,{'max_nfev':True}),(1,{'max_seconds':31})])
def test_invalid_or_unresolved_input_is_not_silently_clamped(p,options):
    with pytest.raises(num.DTNInputError):num.evaluate_dtn(p,**options)
