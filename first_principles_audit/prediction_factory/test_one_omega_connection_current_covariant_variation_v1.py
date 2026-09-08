"""Independent finite-family and integration tests of the covariant candidate term."""
import copy
import hashlib
import pytest
import sympy as sp
from . import verify_one_omega_connection_current_covariant_variation_v1 as oracle


@pytest.fixture(scope='module')
def model():
    return oracle.derive_model()


def flat_context():
    c=oracle.point_context()
    c.update(metric=sp.diag(-1,1,1,1),inverse_metric=sp.diag(-1,1,1,1),
             normal=sp.Matrix([1,0,0,0]),frame=sp.Matrix([[0,0,0],[1,0,0],[0,1,0],[0,0,1]]),
             h=sp.zeros(4),dh=[sp.zeros(4) for _ in range(4)],
             omega=[sp.zeros(3) for _ in range(4)],kappa=sp.zeros(4,3),
             beta=sp.zeros(3,1),dbeta=sp.zeros(4,3))
    return c


def test_all_connection_entries_and_independent_beta_jets(model):
    cv=model['connection_variation']; c=model['context']
    assert sum(len(m) for m in cv['direct'])==36
    assert all(sp.expand(a-b)==0 for left,right in zip(cv['direct'],cv['reference']) for a,b in zip(left,right))
    assert all(sp.diff(entry,jet)==0 for matrix in cv['direct'] for entry in matrix for jet in c['dbeta'])
    assert all(matrix+matrix.T==sp.zeros(3) for matrix in cv['direct'])
    assert any(c['kappa'][0,0] in value.free_symbols for value in cv['direct'][0])
    assert c['normal'][1]!=0  # The generic point calculation did not silently use a rest-frame normal.


def test_exact_finite_boost_family_fixes_kappa_sign_and_removes_d_beta():
    x,epsilon=sp.symbols('x epsilon',real=True); beta=1+x**2
    g=sp.diag(-1,1,1,1)
    u=sp.Matrix([sp.cosh(x),sp.sinh(x),0,0])
    e1=sp.Matrix([sp.sinh(x),sp.cosh(x),0,0]); e2=sp.Matrix([0,0,1,0])
    # This is an exact finite orthonormal frame family, independent of the infinitesimal helper.
    e2_epsilon=sp.sinh(epsilon*beta)*u+sp.cosh(epsilon*beta)*e2
    omega12=(e1.T*g*e2_epsilon.diff(x))[0]
    finite_family_derivative=sp.simplify(sp.diff(omega12,epsilon).subs(epsilon,0))
    assert finite_family_derivative==beta
    c=flat_context(); c['kappa'][1,0]=1; c['beta'][1]=beta; c['dbeta'][1,1]=sp.diff(beta,x)
    result=oracle.connection_variation(c)
    assert result['direct'][1][0,1]==finite_family_derivative
    assert result['direct'][1][1,0]==-finite_family_derivative
    assert sp.simplify(result['direct'][1][0,1]+finite_family_derivative)==2*beta


def test_exact_metric_family_fixes_metric_curl_factor():
    x,epsilon=sp.symbols('x epsilon',real=True)
    # ds²=-dt²+dx²+exp(2 epsilon x)dy²+dz², e_y=exp(-epsilon x)partial_y.
    gamma_yy=sp.exp(2*epsilon*x)
    christoffel_x_yy=-sp.diff(gamma_yy,x)/2
    exact_omega_y_xy=christoffel_x_yy*sp.exp(-epsilon*x)
    derivative=sp.diff(exact_omega_y_xy,epsilon).subs(epsilon,0)
    assert derivative==-1
    c=flat_context(); c['dh'][1][2,2]=2
    result=oracle.connection_variation(c)
    assert result['direct'][2][0,1]==derivative
    assert result['direct'][2][1,0]==-derivative


def test_normal_variation_matches_exact_normalized_metric_and_gradient_curve(model):
    c=model['context']; g=c['metric']; gi=c['inverse_metric']; u=c['normal']
    epsilon=sp.Symbol('epsilon',real=True); lapse=sp.Rational(7,5)
    v=sp.Matrix([1,sp.Rational(1,2),-1,sp.Rational(2,3)]); h=v*v.T
    df=sp.Matrix([sp.Rational(1,3),-2,1,sp.Rational(3,4)])
    # Exact Sherman-Morrison inverse for a rank-one metric curve.
    inverse_curve=gi-epsilon*(gi*v*v.T*gi)/(1+epsilon*(v.T*gi*v)[0])
    gradient_curve=-g*u/lapse+epsilon*df
    N_curve=1/sp.sqrt(-(gradient_curve.T*inverse_curve*gradient_curve)[0])
    normal_curve=-N_curve*gradient_curve
    exact=normal_curve.diff(epsilon).subs(epsilon,0).applyfunc(sp.simplify)
    replacements={c['N']:lapse}
    replacements.update({c['h'][i,j]:h[i,j] for i in range(4) for j in range(i,4)})
    replacements.update(dict(zip(c['df'],df)))
    actual=model['normal_variation'].subs(replacements)
    assert (actual-exact).applyfunc(sp.simplify)==sp.zeros(4,1)


def test_explicit_hodge_stress_from_an_exact_rank_one_metric_curve(model):
    c=model['context']; g=c['metric']; gi=c['inverse_metric']; chi=sp.Rational(3,7)
    epsilon=sp.Symbol('epsilon',real=True); v=sp.Matrix([1,sp.Rational(1,2),-1,sp.Rational(2,3)])
    h=v*v.T; inner=(v.T*gi*v)[0]
    inverse_curve=gi-epsilon*(gi*v*v.T*gi)/(1+epsilon*inner)
    volume_curve=sp.sqrt(-g.det()*(1+epsilon*inner))
    replacement={c['chi']:chi}
    for mu in range(4):
        for a in range(3):
            for b in range(a+1,3): replacement[c['C'][mu][a,b]]=sp.Rational((mu+1)*(a+2)-b,mu+b+3)
    colors=[sp.Matrix([c['C'][mu][a,b].subs(replacement) for mu in range(4)])
            for a in range(3) for b in range(a+1,3)]
    density=-chi*volume_curve*sum((color.T*inverse_curve*color)[0] for color in colors)/2
    direct=sp.diff(density,epsilon).subs(epsilon,0)
    T=model['T_C'].subs(replacement)
    predicted=sp.sqrt(-g.det())*sum(T[mu,nu]*h[mu,nu] for mu in range(4) for nu in range(4))/2
    assert sp.simplify(direct-predicted)==0
    assert direct!=0


def test_contracted_variation_has_metric_half_and_spatial_V(model):
    c=model['context']; J,V=model['J'],model['V']; g,u=c['metric'],c['normal']
    assert sp.expand(V.dot(g*u))==0
    assert sp.expand(model['omega_density_variation']-model['omega_density_reference'])==0
    assert sp.expand(sum(model['tau_boost'][i,j]*c['h'][i,j]/2 for i in range(4) for j in range(4))
                     +(V.T*c['h']*u)[0]/2)==0
    assert any(value!=0 for value in V)
    assert all(sp.expand(J[mu][nu][rho]+J[mu][rho][nu])==0
               for mu in range(4) for nu in range(4) for rho in range(4))


def test_metric_adjoint_normalization_by_independent_periodic_integral(model):
    x=sp.Symbol('x1',real=True)
    tau12=model['functional_adjoint']['metric_adjoint'][1,2]
    # J^{121}=sin(x), equivalently the stored independent J^{112}=-sin(x).
    replacement={f:(-sp.sin(x) if f.func.__name__=='J112' else 0) for f in tau12.atoms(sp.Function)}
    coefficient=tau12.subs(replacement).doit()
    assert sp.simplify(coefficient+sp.cos(x)/2)==0
    h12=sp.cos(x)
    direct=sp.integrate(sp.sin(x)*sp.diff(h12,x)/2,(x,0,2*sp.pi))
    predicted=sp.integrate(coefficient*h12,(x,0,2*sp.pi))
    assert direct==predicted==-sp.pi/2


def test_khronon_adjoint_sign_by_independent_periodic_integral(model):
    x=sp.Symbol('x1',real=True); lapse=2+sp.cos(x); velocity=sp.sin(x); variation=sp.cos(2*x)
    ET=model['functional_adjoint']['E_T']
    replacement={f:(lapse if f.func.__name__=='N' else velocity if f.func.__name__=='V1' else 0)
                 for f in ET.atoms(sp.Function)}
    coefficient=ET.subs(replacement).doit()
    assert sp.simplify(coefficient-sp.diff(lapse*velocity,x))==0
    direct=sp.integrate(-lapse*velocity*sp.diff(variation,x),(x,0,2*sp.pi))
    predicted=sp.integrate(coefficient*variation,(x,0,2*sp.pi))
    assert direct==predicted==sp.pi
    assert direct!=-predicted


def test_current_wedge_order_is_3_plus_1_not_1_plus_3(model):
    assert sp.expand(model['current_density_variation']-model['current_pairing'])==0
    assert model['current_pairing']!=0
    # Independent temporal color component at the boosted-coordinate metric point.
    c=model['context']; substitution={s:0 for matrix in c['C']+c['delta_A'] for s in matrix.free_symbols}
    substitution.update({c['C'][0][0,1]:2,c['delta_A'][0][0,1]:3,c['chi']:5})
    assert model['current_pairing'].subs(substitution)==sp.Rational(15,2)


def test_simultaneous_frame_and_connection_rotation(model):
    cv=model['connection_variation']
    assert all(sp.expand(a-b)==0 for left,right in zip(cv['rotation_direct'],cv['rotation_reference'])
               for a,b in zip(left,right))
    assert all(matrix==sp.zeros(3) for matrix in model['residuals']['simultaneous_connection_rotation'])
    assert model['residuals']['rotation_leaves_action_invariant']==0
    assert model['negative_controls']['rotate_frame_without_A']!=0
    assert all(not oracle.is_zero(value) for value in model['negative_controls'].values())


@pytest.fixture(scope='module')
def payload():
    return oracle.build_payload()


@pytest.mark.parametrize('mutation',['J','E_T','global_order','adoption'])
def test_resigned_receipt_cannot_change_math_or_promote_scope(payload,mutation):
    changed=copy.deepcopy(payload)
    if mutation=='J': changed['model']['J'][0][1][2]='1+('+changed['model']['J'][0][1][2]+')'
    elif mutation=='E_T': changed['model']['functional_adjoint']['E_T']='-('+changed['model']['functional_adjoint']['E_T']+')'
    elif mutation=='global_order': changed['scope']['global_reduction_of_differential_order_proved']=True
    else: changed['proposal']['adopted']=True
    changed['calculation_digest']=oracle.canonical_digest({k:v for k,v in changed.items() if k!='calculation_digest'})
    with pytest.raises(oracle.CovariantVariationError,match='trusted recomputation'):
        oracle.validate_payload(changed)


def test_scope_and_byte_pins_are_preserved(payload):
    assert hashlib.sha256(oracle.SOURCE.read_bytes()).hexdigest()==oracle.SOURCE_SHA
    assert payload['proposal']['A_Sigma_independent'] is True
    assert payload['proposal']['adopted'] is False
    assert all(payload['scope'][key] is False for key in (
        'global_reduction_of_differential_order_proved','full_moving_gluing_chain_closed',
        'positive_full_energy_proved','N4_JUNCTION_BENDING_pass','N7_LINEAR_REDUCTION_pass',
        'P4_full_same_action_pass','B4_pass','B5_pass','BF_global_quotient_closed'))


def test_source_tampering_rejected_even_with_rebound_document_digest(tmp_path,monkeypatch):
    document=__import__('json').loads(oracle.SOURCE.read_bytes())
    document['independent_mutant']=True
    document['calculation_digest']=oracle.canonical_digest({k:v for k,v in document.items() if k!='calculation_digest'})
    path=tmp_path/'source.json'; path.write_text(__import__('json').dumps(document))
    monkeypatch.setattr(oracle,'SOURCE',path)
    with pytest.raises(oracle.CovariantVariationError,match='source byte pin mismatch'):
        oracle.build_payload()


def test_invalid_and_unresigned_receipts_are_rejected(payload):
    with pytest.raises(oracle.CovariantVariationError,match='schema'):
        oracle.validate_payload(None)
    changed=copy.deepcopy(payload); changed['scope']['N4_JUNCTION_BENDING_pass']=True
    with pytest.raises(oracle.CovariantVariationError,match='digest'):
        oracle.validate_payload(changed)
