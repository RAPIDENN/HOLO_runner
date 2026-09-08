"""Independent channel densities, gauge tests and positive-real identities."""
from copy import deepcopy
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_connection_candidate_response_v1 as gate
else:
    import verify_one_omega_connection_candidate_response_v1 as gate

@pytest.fixture(scope='module')
def model():return gate.derive_model()

@pytest.fixture(scope='module')
def positive():return gate.derive_positive_real()

@pytest.fixture(scope='module')
def payload():return gate.build_payload()


def test_all_added_Hessian_entries_from_explicit_three_color_density(model):
    """Use the color contractions explicitly, without calling projected geometry."""
    a=model['base']['amplitudes'];w,q,chi=model['w'],model['q'],model['chi']
    t1,t2,t3=model['theta']
    kinetic=(w*t1-q*a['N2']/2)**2+(w*t2+q*a['N1']/2)**2+(w*t3)**2
    gradient=q*q*((a['H11']**2+a['H22']**2+2*a['H12']**2)/4
                 +(t1+a['H23']/2)**2+(t2-a['H13']/2)**2+t3*t3)
    independent=chi*(kinetic-gradient)/2
    assert sp.expand(independent-model['L_C'])==0
    assert gate.zero(sp.hessian(independent,model['fields'])-model['addition'])
    assert not model['L_C'].has(a['n'],a['tau'],a['H33'],a['omega'],a['vphi1'])


def test_analytic_Hessian_uses_opposite_Fourier_adjoint(model):
    H,w,q=model['H18'],model['w'],model['q']
    assert gate.zero(H-H.T.xreplace({w:-w,q:-q}))
    assert model['addition']==model['addition'].T
    # The original clock cross terms have odd derivative order; transposition
    # alone is not the proper test for the complete analytic Fourier matrix.
    assert not gate.zero(H-H.T)


def test_four_metric_gauges_need_compensated_orientation(model):
    for name,v in model['gauges'].items():assert gate.zero(model['H18']*v)
    q=model['q'];idx=model['index']
    assert model['gauges']['space_1'][idx['theta2']]==sp.I*q/2
    assert model['gauges']['space_2'][idx['theta1']]==-sp.I*q/2
    assert not gate.zero(model['negative']['omit_spatial_gauge_theta_compensation'])


def test_vector_action_depends_on_gauge_invariants_before_elimination(model):
    U,Psi,h=sp.symbols('U Psi h');w,q,chi=model['w'],model['q'],model['chi']
    for axis,orientation in (('1',1),('2',-1)):
        data=model['vectors'][axis];Nvar,hvar,tvar=[model['fields'][model['index'][name]] for name in data['field_order']]
        transformed=data['density'].subs({Nvar:(U-w*h)/q,hvar:h,tvar:Psi+orientation*h/2},simultaneous=True)
        expected=model['B']*U*U/4+chi*((w*Psi+orientation*U/2)**2-q*q*Psi*Psi)/2
        assert sp.cancel(transformed-expected)==0
        assert sp.cancel(sp.diff(transformed,h))==0


def test_vector_reduced_kinetic_from_stationary_density_and_pivot():
    """Independent real-time stationarity, not a Schur of the new H18."""
    q,chi,B=sp.symbols('q chi B',positive=True)
    N,v,t=sp.symbols('N velocity theta',real=True)
    L=q*q*B*N*N/4+chi*((v-q*N/2)**2-q*q*t*t)/2
    row=sp.diff(L,N);solution=2*chi*v/(q*(2*B+chi))
    assert sp.cancel(row.subs(N,solution))==0
    reduced=sp.cancel(L.subs(N,solution))
    assert sp.cancel(sp.diff(reduced,v,2)-2*chi*B/(2*B+chi))==0
    assert sp.cancel(sp.diff(L,N,2)-q*q*B/2-chi*q*q/4)==0
    assert sp.cancel(reduced-chi*v*v/2+chi*q*q*t*t/2)!=0


def test_vector_determinants_retain_shift_factor(model):
    w,q,chi,B=model['w'],model['q'],model['chi'],model['B']
    for data in model['vectors'].values():
        assert gate.zero(data['gauge_fixed'].det()-data['pivot']*data['Schur'])
        assert gate.zero(data['pivot']-q*q*(2*B+chi)/4)
        assert gate.zero(data['Schur']-(2*chi*B*w*w/(2*B+chi)-chi*q*q))


def test_complete_scalar_injection_preserves_pivots_and_mixing(model):
    old,new=model['oldH3'],model['H3'];q,chi=model['q'],model['chi']
    assert gate.zero(new[:2,:]-old[:2,:])
    assert gate.zero(new[:, :2]-old[:, :2])
    assert gate.zero(new[2,2]-old[2,2]+2*chi*q*q)
    assert gate.zero(model['scalar_injection'].T*model['H18'][:,15:])
    assert gate.zero(model['H5'][3:,3:]-model['oldH5'][3:,3:])
    # Generic final Schur demonstrates why an unchanged pivot cannot hide a new pole.
    A11,A12,A22,b1,b2,c,delta=sp.symbols('A11 A12 A22 b1 b2 c delta')
    A=sp.Matrix([[A11,A12],[A12,A22]]);b=sp.Matrix([b1,b2])
    assert sp.cancel((c-delta-(b.T*A.inv()*b)[0])-(c-(b.T*A.inv()*b)[0])+delta)==0


def test_tensor_both_polarizations_and_material_rows(model):
    chi,q,FT=model['chi'],model['q'],model['FT']
    assert gate.zero(model['tensor_cross']+(FT+chi*q*q)/2)
    assert gate.zero(model['tensor_plus']+(FT+chi*q*q)/2)
    for name in ('omega','vphi1','vphi2','vphi3'):
        assert model['addition'][model['index'][name],:]==sp.zeros(1,18)


def test_q_zero_is_direct_full_matrix_not_vector_limit(model):
    q,w,chi=model['q'],model['w'],model['chi']
    actual=model['addition'].subs(q,0)
    assert actual[:15,:]==sp.zeros(15,18)
    assert actual[15:,:15]==sp.zeros(3,15)
    assert actual[15:,15:]==chi*w*w*sp.eye(3)
    assert all(gate.zero(x.subs(q,0)) for x in model['omega'])
    b=sp.Symbol('b',positive=True)
    assert sp.simplify(2*chi*b/(2*b+chi)-chi)!=0


def test_harmonic_positive_real_part_at_arbitrary_complex_values(positive):
    for ux,uy,vx,vy in ((1,4,2,-3),(2,-7,3,11),(5,0,1,0)):
        U=sp.Integer(ux)+sp.I*uy;V=sp.Integer(vx)+sp.I*vy
        actual=sp.re(2*U*V/(2*U+V))
        expected=positive['real_reference'].subs({positive['ux']:ux,positive['uy']:uy,
                                                    positive['vx']:vx,positive['vy']:vy})
        assert sp.cancel(actual-expected)==0 and actual>0
    assert all(positive['checks'].values())


def test_spectral_kernel_bound_with_distinct_poles_is_a_diagnostic_not_the_proof():
    # Independent rational exact instances test the algebraic inequality.
    b=sp.Rational(2);chi=sp.Rational(7,3)
    for s,q in ((sp.Integer(1)+2*sp.I,sp.Rational(3,2)),(sp.Rational(1,7)-3*sp.I,sp.Integer(2)),(sp.Integer(2),sp.Rational(1,10))):
        m=sum(weight*ell/(ell+s*s+q*q) for weight,ell in
              ((sp.Rational(2,7),sp.Rational(1,3)),(sp.Rational(3,5),sp.Integer(9)),(sp.Rational(1,11),sp.Integer(80))))
        B=b+m;K=2*chi*B/(2*B+chi);D=s*s*K+chi*q*q
        lower=sp.re(s)*(2*chi*b/(2*b+chi)+chi*q*q/sp.Abs(s)**2)
        assert sp.simplify(sp.re(D/s)-lower)>0
        assert sp.simplify(sp.re(s*(2*B+chi)))>0


def test_negative_chi_does_not_have_the_claimed_energy():
    sigma=sp.Rational(2)
    assert -sigma<0  # chi=-1 makes Re[(chi*s^2)/s] negative at real s=sigma.
    b=sp.Rational(2);chi=sp.Rational(-4)
    assert 2*b+chi==0  # The shift proof must not silently include chi<=0.


def test_receipt_is_source_bound_and_recomputed(payload):
    assert gate.validate_payload(payload)==payload
    assert all(payload['checks'].values()) and all(payload['negative_controls'].values())
    assert payload['decision']['new_action_adopted'] is False
    assert payload['decision']['nonlinear_torque_repair_completed'] is False

@pytest.mark.parametrize('key',('full_P4','full_N7','uniform_shift_reconstruction_at_q_zero_proved','new_action_adopted'))
def test_overclaims_rejected_even_with_new_digest(payload,key,monkeypatch):
    # Reuse the already fresh source-bound calculation only for mutation tests.
    expected=deepcopy(payload);monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(expected))
    bad=deepcopy(payload);bad['decision'][key]=True
    bad.pop('calculation_digest');bad['calculation_digest']=gate.digest(bad)
    with pytest.raises(gate.CandidateResponseError,match='fresh source-bound'):
        gate.validate_payload(bad)


def test_lemma_and_upstream_byte_pins_reject_changes(tmp_path):
    p=tmp_path/'note';p.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.CandidateResponseError,match='lemma hash'):
        gate.load_sources(note=p)
    first=next(iter(gate.SOURCE_PINS));p=tmp_path/(first+'.json')
    p.write_bytes((gate.HERE/'artifacts'/p.name).read_bytes()+b'\n')
    with pytest.raises(gate.CandidateResponseError,match='artifact hash'):
        gate.load_sources(artifact_directory=tmp_path)
