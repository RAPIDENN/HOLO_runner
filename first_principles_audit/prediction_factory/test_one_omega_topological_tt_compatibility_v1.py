"""Independent geometry and boundary controls for the topological TT restriction."""
from __future__ import annotations

import copy
import json

import pytest
import sympy as sp

from . import verify_one_omega_topological_tt_compatibility_v1 as oracle


@pytest.fixture(scope='module')
def model():
    return oracle.derive_model()


@pytest.fixture(scope='module')
def symbols(model):
    return model['symbols']


def zero(value):
    if isinstance(value, sp.MatrixBase):
        return all(sp.simplify(x) == 0 for x in value)
    return sp.simplify(value) == 0


def quadratic(expression, epsilon):
    return sp.diff(expression, epsilon, 2).subs(epsilon, 0)/2


def test_determinant_and_inverse_from_exact_matrix(model, symbols):
    e, h, A = (symbols[k] for k in ('epsilon','h','A'))
    exact = sp.exp(2*A)*sp.Matrix([[-1,0,0,0],[0,1,e*h,0],[0,e*h,1,0],[0,0,0,1]])
    assert zero(exact-model['gamma'])
    assert zero(exact.det()+sp.exp(8*A)*(1-e**2*h**2))
    product = exact*model['gamma_inverse']-sp.eye(4)
    for expression in product:
        for order in range(3):
            assert zero(sp.diff(expression,e,order).subs(e,0))
    assert zero(quadratic(model['sqrt_gamma'],e)+sp.exp(4*A)*h**2/2)
    # A missing quadratic term in either spatial inverse diagonal is visible.
    wrong=sp.Matrix(model['gamma_inverse'])
    wrong[1,1]-=sp.exp(-2*A)*e**2*h**2
    assert not zero(quadratic((exact*wrong-sp.eye(4))[1,1],e))


def test_frame_varies_with_the_metric_and_stays_orthonormal(model, symbols):
    e, h = symbols['epsilon'],symbols['h']
    metric=sp.Matrix([[1,e*h,0],[e*h,1,0],[0,0,1]])
    frame=model['frame']
    defect=frame.T*metric*frame-sp.eye(3)
    for expression in defect:
        for order in range(3):
            assert zero(sp.diff(expression,e,order).subs(e,0))
    assert not zero(sp.diff((metric-sp.eye(3))[0,1],e).subs(e,0))


@pytest.fixture(scope='module')
def independent_spatial_ricci():
    # Direct Christoffel/Ricci calculation on a nonconstant 3-metric, not the
    # radial-ADM or Fierz-Pauli identity used in the implementation.
    x,y,z=sp.symbols('independent_x independent_y independent_z',real=True)
    e=sp.Symbol('independent_epsilon',real=True)
    h=sp.Function('independent_h')(z)
    coordinates=(x,y,z)
    metric=sp.Matrix([[1,e*h,0],[e*h,1,0],[0,0,1]])
    inverse=metric.inv()
    christoffel={}
    for a in range(3):
        for b in range(3):
            for c in range(3):
                christoffel[a,b,c]=sum(inverse[a,d]*(
                    sp.diff(metric[d,c],coordinates[b])+sp.diff(metric[d,b],coordinates[c])
                    -sp.diff(metric[b,c],coordinates[d]))/2 for d in range(3))
    ricci=sp.zeros(3)
    for a in range(3):
        for b in range(3):
            ricci[a,b]=sum(sp.diff(christoffel[c,a,b],coordinates[c])
                -sp.diff(christoffel[c,a,c],coordinates[b])
                +sum(christoffel[c,a,b]*christoffel[d,c,d]
                     -christoffel[d,a,c]*christoffel[c,b,d] for d in range(3))
                for c in range(3))
    scalar=sum(inverse[a,b]*ricci[a,b] for a in range(3) for b in range(3))
    density=sp.sqrt(1-e**2*h**2)*scalar
    return {'coordinate':z,'field':h,'quadratic':sp.simplify(quadratic(density,e))}


def test_intrinsic_curvature_from_independent_christoffels(model, symbols, independent_spatial_ricci):
    case=independent_spatial_ricci
    z,h=case['coordinate'],case['field']
    expected=3*sp.diff(h,z)**2/2+2*h*sp.diff(h,z,2)
    assert zero(case['quadratic']-expected)
    substitution={symbols['h']:h,symbols['hz']:sp.diff(h,z),symbols['hzz']:sp.diff(h,z,2)}
    assert zero(model['R3_raw_L2'].xreplace(substitution)-case['quadratic'])
    divergence=sp.diff(2*h*sp.diff(h,z),z)
    assert zero(case['quadratic']-divergence+sp.diff(h,z)**2/2)


def test_trace_and_kinetic_from_diagonal_polarization(symbols, model):
    e,h,ht,hr,Ap=(symbols[k] for k in ('epsilon','h','ht','hr','Ap'))
    # Orthogonal rotation diagonalizes the shear: eigenvalues 1+e*h,1-e*h.
    radial_eigenvalues=[Ap,Ap+e*hr/(2*(1+e*h)),Ap-e*hr/(2*(1-e*h)),Ap]
    trace=sum(radial_eigenvalues)
    norm=sum(v*v for v in radial_eigenvalues)
    assert zero(quadratic(trace,e)+h*hr)
    assert zero(quadratic(norm,e)-(-2*Ap*h*hr+hr**2/2))
    for order in range(3):
        assert zero(sp.diff(trace-model['trace_K'],e,order).subs(e,0))
    time_eigenvalues=[e*ht/(2*(1+e*h)),-e*ht/(2*(1-e*h)),0]
    assert zero(quadratic(sum(time_eigenvalues)**2,e))
    assert zero(quadratic(sum(x*x for x in time_eigenvalues),e)-ht**2/2)


def test_radial_lagrangian_cross_term_and_exact_mass_cancellation(model,symbols):
    A,Ap,App,h,hr,G,M,Op=(symbols[k] for k in ('A','Ap','App','h','hr','G','M5c','Op'))
    o,k=symbols['omega'],symbols['k']
    W=3*M*k*sp.exp(-G*o**2/(6*M))
    U=sp.diff(W,o)**2/(2*G)-2*W**2/(3*M)
    expected=sp.exp(4*A)*(-M*hr**2/4-3*M*Ap*h*hr+(-3*M*Ap**2+G*Op**2/4+U/2)*h**2)
    assert zero(model['raw_radial_L2']-expected)
    primitive=-3*M*sp.exp(4*A)*Ap*h**2/2
    derivative=sp.diff(primitive,A)*Ap+sp.diff(primitive,Ap)*App+sp.diff(primitive,h)*hr
    after=sp.expand(expected-derivative)
    bps={Ap:-W/(3*M),Op:sp.diff(W,o)/G,App:-sp.diff(W,o)**2/(3*M*G)}
    assert zero(after.subs(bps)+M*sp.exp(4*A)*hr**2/4)
    assert zero(model['radial_mass_BPS'])


def test_two_uv_boundaries_cancel_tension_in_second_variation(model,symbols):
    M,G,k,o,h0=(symbols[k] for k in ('M5c','G','k','omega','h0'))
    W=3*M*k*sp.exp(-G*o**2/(6*M))
    Ap=-W/(3*M)
    single_uv=3*M*Ap*h0**2/2
    wall=W*h0**2
    assert zero(2*single_uv+wall)
    assert not zero(single_uv+wall)
    assert zero(model['bilateral_boundary_residual'])


def test_brane_tensor_kinetic_does_not_inherit_scalar_lambda(model,symbols):
    Mb2,xi,ht,hz=(symbols[k] for k in ('Mb2','xi','ht','hz'))
    assert zero(model['brane_L2']-Mb2*(ht**2-xi*hz**2)/4)
    for name in ['lambda_K','eta','B4bar']:
        assert zero(sp.diff(model['brane_L2'],symbols[name]))
    assert zero(sp.diff(model['brane_L2'],ht,2)-Mb2/2)
    assert zero(sp.diff(model['brane_L2'],hz,2)+Mb2*xi/2)


def test_boundary_momentum_outward_orientation_and_both_sides(model,symbols):
    M,Mb2,xi,freq,q,h0=(symbols[k] for k in ('M5c','Mb2','xi','freq','q','h0'))
    hp,hm=symbols['hr_plus'],symbols['hr_minus']
    expected=M*(hp+hm)/2+Mb2*(freq**2-xi*q**2)*h0/2
    assert zero(model['J_TT']-expected)
    np,nm=sp.symbols('independent_outward_plus independent_outward_minus',real=True)
    boundary=model['J_bulk'].subs({hp:-np,hm:-nm})
    assert zero(boundary+M*(np+nm)/2)
    assert not zero(boundary-M*(np+nm)/2)
    assert zero(model['J_bulk'].subs(hm,hp)-M*hp)


def test_gapless_mode_and_positive_norm_are_a_restricted_TT_result(model,symbols):
    freq,q,xi=symbols['freq'],symbols['q'],symbols['xi']
    case={symbols['hr_plus']:0,symbols['hr_minus']:0,xi:1,freq:q}
    assert zero(model['J_TT'].subs(case))
    assert zero(model['zero_mode_kinetic_coefficient']-(symbols['Mb2']+model['M4_bulk_squared'])/4)
    assert model['zero_mode_kinetic_coefficient'].is_positive is True


def test_restoring_the_literal_solid_removes_the_gapless_TT_solution(model,symbols):
    mu,v,h,h0=(symbols[k] for k in ('mu_X','v','h','h0'))
    # C12=C21=-v²h; direct tr(C²) fixes the often-missed factor of two.
    strain=sp.Matrix([[0,-v**2*h,0],[-v**2*h,0,0],[0,0,0]])
    L=-mu*sp.trace(strain*strain)/4
    assert zero(L-model['old_solid_L2'])
    assert zero(sp.diff(L,h,2)-model['old_solid_contact_H'])
    assert zero(model['old_solid_contact_H']+mu*v**4)
    expected_contact=-mu*v**4*h0
    assert not zero(expected_contact)
    assert expected_contact.subs({mu:1,v:1,h0:1}) == -1


def test_nonzero_null_TT_wave_has_nonzero_linearized_Weyl_witness():
    # The BPS geometry is conformal to 5D Minkowski; its background Weyl tensor
    # is zero. A nonzero linearized Weyl component therefore cannot be a pure
    # infinitesimal coordinate transformation of that background. This check
    # does not substitute for the remaining coupled boundary/gauge equations.
    t,x1,x2,x3,z=sp.symbols('tt_t tt_x1 tt_x2 tt_x3 tt_z',real=True)
    q=sp.Symbol('tt_nonzero_momentum',positive=True)
    coordinates=(t,x1,x2,x3,z)
    eta=(-1,1,1,1,1)
    wave=sp.cos(q*(x3-t))
    perturbation=sp.zeros(5)
    perturbation[1,2]=perturbation[2,1]=wave
    trace=sum(eta[a]*perturbation[a,a] for a in range(5))
    divergence=sp.Matrix([sum(eta[a]*sp.diff(perturbation[a,b],coordinates[a])
                             for a in range(5)) for b in range(5)])
    assert zero(trace) and zero(divergence)
    ricci=sp.Matrix(5,5,lambda a,b: (
        sp.diff(divergence[b],coordinates[a])+sp.diff(divergence[a],coordinates[b])
        -sum(eta[c]*sp.diff(perturbation[a,b],coordinates[c],2) for c in range(5))
        -sp.diff(trace,coordinates[a],coordinates[b]))/2)
    assert zero(ricci)
    # R_0102 = -d_t^2 h_12/2, and Weyl=Riemann since the linearized Ricci is zero.
    weyl_witness=-sp.diff(wave,t,2)/2
    assert zero(weyl_witness-q**2*wave/2)
    assert weyl_witness.subs({t:0,x3:0}) == q**2/2
    assert not zero(weyl_witness)


@pytest.fixture(scope='module')
def payload():
    return oracle.build_payload()


def rehash(payload):
    result=copy.deepcopy(payload)
    core={k:v for k,v in result.items() if k!='calculation_digest'}
    encoded=json.dumps(core,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
    import hashlib
    value=hashlib.sha256(encoded).hexdigest()
    if isinstance(result.get('calculation_digest'),dict):
        result['calculation_digest']['sha256']=value
    else:
        result['calculation_digest']=value
    return result


def test_receipt_matches_current_symbolic_derivation(payload):
    oracle.validate_payload(payload)


def test_resigned_top_level_claim_cannot_be_added(payload):
    changed=copy.deepcopy(payload)
    changed['full_gravity_stability_established']=True
    with pytest.raises(oracle.TopologicalTTError):
        oracle.validate_payload(rehash(changed))


def test_stale_receipt_digest_is_rejected(payload):
    changed=copy.deepcopy(payload)
    changed['schema']='different_schema'
    with pytest.raises(oracle.TopologicalTTError):
        oracle.validate_payload(changed)


def test_candidate_source_pin_rejects_even_semantically_equal_reencoding(tmp_path):
    source=json.loads(oracle.CANDIDATE.read_text())
    copy_path=tmp_path/'candidate.json'
    copy_path.write_text(json.dumps(source,sort_keys=True,separators=(',',':')))
    assert copy_path.read_bytes()!=oracle.CANDIDATE.read_bytes()
    with pytest.raises(oracle.TopologicalTTError):
        oracle.load_sources(candidate_path=copy_path)


def test_candidate_reuses_W_U_wall_but_really_changes_material_and_scalar_branch():
    old=json.loads(oracle.CHARTER.read_bytes())['action_charter']
    new=json.loads(oracle.CANDIDATE.read_bytes())['exact_classical_charter']
    for name in ('superpotential','bulk_potential','full_V4','wall_background'):
        assert old['exact_action'][name]==new['exact_action'][name]
    assert 'solid' in old['exact_action']
    assert new['exact_action']['removed_terms']=='S_X=0 and every bulk screen-clock term=0'
    assert 'BF' in new['exact_action'] and 'BF' not in old['exact_action']
    assert old['coefficient_policy']['parameters']['lambda_K']>1
    assert new['coefficient_policy']['parameters']['lambda_K']<0
    assert new['coefficient_policy']['parameters']['xi']==1
    assert old['coefficient_policy']['parameters']['brane_Mb_squared']==new['coefficient_policy']['parameters']['brane_Mb_squared']
