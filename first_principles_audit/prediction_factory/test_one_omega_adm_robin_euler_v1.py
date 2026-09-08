"""Independent nonlinear ADM action/Euler and three-chart Green tests."""
from copy import deepcopy
import json
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_adm_robin_euler_v1 as gate
else:
    import verify_one_omega_adm_robin_euler_v1 as gate

@pytest.fixture(scope='module')
def model():return gate.derive_model()
@pytest.fixture(scope='module')
def payload():return gate.build_payload()

def total_derivative(expr,jets):
    return sum(sp.diff(expr,q)*dq for q,dq in jets.items())

def test_all_independent_jet_IBP_residuals(model):
    assert all(model['checks'].values())
    for part in model['parts'].values():
        assert all(gate.zero(x) for x in part['residuals'].values())

def test_anisotropic_time_dependent_metric_and_lapse_from_literal_action(model):
    ctx=model['symbols'];b,N,lam=ctx['b'],ctx['N'],ctx['lam']
    A=sp.symbols('A0:3',real=True);Ad=sp.symbols('Ad0:3',real=True);Add=sp.symbols('Add0:3',real=True)
    Nd=sp.Symbol('Ndot',real=True)
    jets={**dict(zip(A,Ad)),**dict(zip(Ad,Add)),N:Nd}
    V=sp.exp(sum(A));H=[x/N for x in Ad]
    literal=b*V*(sum(x*x for x in Ad)-lam*sum(Ad)**2)/(2*N)
    kin=model['parts']['kinetic'];K=kin['K']
    replacement={K[i,j]:(H[i] if i==j else 0) for i in range(3) for j in range(i,3)}
    C=kin['C'].subs(replacement);algebra=kin['metric_algebraic'].subs(replacement)
    for i in range(3):
        actual=sp.diff(literal,A[i])-total_derivative(sp.diff(literal,Ad[i]),jets)
        pi=V*sp.exp(-2*A[i])*C[i,i]
        expected=b*(-sp.exp(2*A[i])*total_derivative(pi,jets)+N*V*algebra[i,i])
        assert sp.simplify(actual-expected)==0
    assert sp.simplify(sp.diff(literal,N)+b*V*(sum(x*x for x in H)-lam*sum(H)**2)/2)==0

def test_shift_density_weight_is_required_at_nonzero_shift_gradient(model):
    t=model['parts']['transport'];Q=t['Q'];pi=t['pi_density'];J=t['shift_gradient']
    witness=sp.trace(J)*gate.pair(pi,Q)
    sub={}
    for mat in (Q,pi,J):
        for i in range(3):
            for j in range(3):sub[mat[i,j]]=1 if i==j else 0
    assert witness.subs(sub)==9
    assert gate.zero(t['metric_row']+t['pi_time_jet']-t['Lie_density'])
    assert t['current_t']==gate.pair(pi,Q)
    assert t['current_spatial'].shape==(3,1)

def test_conformal_spatial_curvature_with_nonconstant_lapse_direct_Euler(model):
    u,u1,u2,u3,u4=sp.symbols('u u1 u2 u3 u4',real=True)
    N,N1,N2=sp.symbols('NN NN1 NN2',positive=True)
    jets={u:u1,u1:u2,u2:u3,u3:u4,N:N1,N1:N2}
    D=lambda expr:total_derivative(expr,jets)
    R=sp.exp(-2*u)*(-4*u2-2*u1*u1)
    # A fixed rational member still contains the full R and R^2 nonlinearities.
    f=2*R-3*R*R/64;fR=2-3*R/32;F=N*fR
    L=N*sp.exp(3*u)*f
    actual=sp.diff(L,u)-D(sp.diff(L,u1))+D(D(sp.diff(L,u2)))
    expected=N*sp.exp(3*u)*(3*f-2*fR*R-4*sp.exp(-2*u)*(D(D(F))+u1*D(F))/N)
    assert sp.simplify(actual-expected)==0
    curv=model['parts']['curvature']
    assert gate.zero(curv['residuals']['Ricci_scalar_from_Christoffel'])
    assert not gate.zero(model['negative_witnesses']['freeze_weight_N_inside_f_R_derivatives'])

def test_Robin_lapse_full_nonlinear_one_dimensional_Euler(model):
    ctx=model['symbols'];N,kappa,y=ctx['N'],ctx['kappa'],ctx['y']
    N1,N2=sp.symbols('NL1 NL2',real=True);v=sp.Matrix(sp.symbols('v0:3',real=True));vp=sp.symbols('vp0:3',real=True)
    jets={N:N1,N1:N2,**dict(zip(v,vp))}
    r=v-y*sp.Matrix([N1/N,0,0])
    L=-kappa*N*(r.T*r)[0]/2
    actual=sp.diff(L,N)-total_derivative(sp.diff(L,N1),jets)
    data=model['parts']['lapse_acceleration_Robin']
    subs={data['N_gradient'][i]:(N1 if i==0 else 0) for i in range(3)}
    subs.update({data['N_hessian'][i,j]:(N2 if i==j==0 else 0) for i in range(3) for j in range(i,3)})
    subs.update({data['material_covector'][i]:v[i] for i in range(3)})
    subs.update({data['material_gradient'][i,j]:(vp[j] if i==0 else 0) for i in range(3) for j in range(3)})
    assert sp.cancel(actual-data['Robin_lapse_row'].subs(subs))==0
    assert data['Robin_current_spatial']!=sp.zeros(3,1)

def test_three_Green_charts_from_internal_origin_in_a_nonunit_metric():
    h=sp.diag(4,9,16);Q=sp.Matrix([[2,1,-1],[1,-3,2],[-1,2,5]])
    frame=sp.diag(sp.Rational(1,2),sp.Rational(1,3),sp.Rational(1,4))
    phi=sp.Matrix([1,-2,3]);dphi=sp.Matrix([2,1,-1]);Pi=sp.Matrix([3,-1,2])
    dframe=-h.inv()*Q*frame/2
    v=frame*phi;dv=dframe*phi+frame*dphi;dv_cov=Q*v+h*dv
    Pi_cov=frame.inv().T*Pi;Pi_contra=h.inv()*Pi_cov
    canonical=-(Pi.T*dphi)[0]
    adjoint=(Pi_contra.T*Q*v)[0]/2
    vector=-(Pi_cov.T*dv)[0]-adjoint
    covector=-(Pi_contra.T*dv_cov)[0]+adjoint
    assert sp.cancel(vector-canonical)==0
    assert sp.cancel(covector-canonical)==0
    assert adjoint!=0
    # Omitting the pre-existing vector metric term leaves the exact mismatch.
    assert sp.cancel(-(Pi_cov.T*dv)[0]-canonical-adjoint)==0

def test_horizontal_Robin_metric_variation_in_a_nonunit_metric():
    e=sp.Symbol('eps');h=sp.diag(4,9,16);hinv=h.inv()
    Q=sp.Matrix([[2,1,-1],[1,-3,2],[-1,2,5]])
    frame=sp.diag(sp.Rational(1,2),sp.Rational(1,3),sp.Rational(1,4))
    phi=sp.Matrix([1,-2,3]);a=sp.Matrix([2,-1,1]);y=sp.Rational(3,2);kappa=2
    v=frame*phi;dv=-hinv*Q*v/2
    moved_cov=(h+e*Q)*(v+e*dv);r=h*v-y*a
    moved_r=moved_cov-y*a
    density=-kappa*(1+e*sp.trace(hinv*Q)/2)*(moved_r.T*(hinv-e*hinv*Q*hinv)*moved_r)[0]/2
    actual=sp.diff(density,e).subs(e,0)
    r_up=hinv*r;a_up=hinv*a
    coefficient=-kappa*(hinv*(r.T*hinv*r)[0]/2+y*gate.sym_outer(r_up,a_up))/2
    assert sp.cancel(actual-gate.pair(coefficient,Q))==0

def test_Robin_y_zero_internal_norm_only_varies_through_volume(model):
    c=model['parts']['material_charts'];ctx=model['symbols']
    expected=-ctx['kappa']*(c['phi'].T*c['phi'])[0]*sp.eye(3)/4
    assert gate.zero(c['Robin_internal_metric_row'].subs(ctx['y'],0)-expected)
    assert not gate.zero(c['Robin_covector_metric_row'].subs(ctx['y'],0)-expected)

def test_total_material_row_controls_chart_change_off_shell(model):
    c=model['parts']['material_charts'];phi=c['phi'];E=c['total_material_Euler_row']
    assert gate.zero(c['total_internal_metric_row']-c['total_covector_metric_row']-gate.sym_outer(phi,E)/2)
    assert gate.zero(c['total_internal_metric_row']-c['total_vector_metric_row']+gate.sym_outer(phi,E)/2)
    assert E!=sp.zeros(3,1)
    assert c['Green_internal']==c['Green_vector'].expand()
    assert not gate.zero(model['negative_witnesses']['apply_Robin_chart_change_without_bulk_Green'])

def test_khronon_definition_and_current_sign(model):
    clock=model['parts']['khronon']
    assert gate.zero(clock['delta_u']-clock['reference'])
    assert clock['delta_u'][0]==0
    assert all(clock['delta_u'][i]!=0 for i in range(1,4))
    assert not gate.zero(model['negative_witnesses']['reverse_khronon_IBP_Euler_sign'])

def test_controls_and_limits(model):
    assert all(model['negative_controls'].values())
    assert len(model['negative_controls'])==8
    scope=model['scope']
    for key in ('all_covariant_E_u_coefficients_expanded','all_bulk_GHY_shape_groupoid_rows_derived',
                'complete_moving_interface_Green_certified','BF_global_or_frame_sector_eliminated',
                'N4_JUNCTION_BENDING_pass','full_N7','full_P4','B4','B5'):
        assert scope[key] is False

@pytest.mark.parametrize('mutation',['full_N4','omit_vector_adjoint'])
def test_rehashed_mutant_rejected_by_fresh_derivation(payload,mutation):
    bad=deepcopy(payload)
    if mutation=='full_N4':bad['decision']['N4_JUNCTION_BENDING_pass']=True
    else:bad['model']['parts']['material_charts']['Green_vector']='0'
    bad['calculation_digest']=gate.canonical_digest({k:v for k,v in bad.items() if k!='calculation_digest'})
    with pytest.raises(gate.ADMEulerError,match='fresh derivation'):gate.validate_payload(bad)

def test_note_and_candidate_pins_reject_mutations(tmp_path):
    p=tmp_path/'note.md';p.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.ADMEulerError,match='note byte hash'):gate.load_sources(note_path=p)
    candidate=json.loads(gate.CANDIDATE.read_bytes());candidate['exact_classical_charter']['exact_action']['Robin_intrinsic']='frozen covector'
    candidate['calculation_digest']=gate.canonical_digest(candidate)
    p=tmp_path/'candidate.json';p.write_text(json.dumps(candidate))
    with pytest.raises(gate.ADMEulerError,match='candidate byte hash'):gate.load_sources(candidate_path=p)

def test_cli_write_is_exclusive(tmp_path,monkeypatch,payload):
    monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(payload))
    p=tmp_path/'receipt.json';gate.main(['--write',str(p)]);old=p.read_bytes()
    with pytest.raises(FileExistsError):gate.main(['--write',str(p)])
    assert p.read_bytes()==old
