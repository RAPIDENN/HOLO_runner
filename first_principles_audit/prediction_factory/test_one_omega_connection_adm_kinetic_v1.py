"""Independent ADM metric, SPD-curve and finite-quadratic velocity controls."""
import copy
import hashlib
import json
import pytest
import sympy as sp
from . import verify_one_omega_connection_adm_kinetic_v1 as oracle


@pytest.fixture(scope='module')
def model():
    return oracle.derive_model()


def test_Hodge_ADM_against_direct_nondiagonal_metric_inverse_and_determinant(model):
    m=model['hodge'];replacement={m['N']:sp.Rational(5,3),m['chi']:sp.Rational(7,5)}
    Lnum=sp.Matrix([[2,0,0],[1,3,0],[-1,2,4]])
    for i in range(3):
        for j in range(i+1):replacement[m['cholesky'][i,j]]=Lnum[i,j]
    replacement.update(dict(zip(m['shift'],[sp.Rational(1,2),-sp.Rational(2,3),sp.Rational(3,4)])))
    for mu in range(4):
        replacement.update({m['C'][mu][a]:sp.Rational((mu+1)*(a+2)-3,mu+a+2) for a in range(3)})
    metric=m['metric'].subs(replacement);inverse=metric.inv();volume=sp.sqrt(-metric.det())
    colors=[C.subs(replacement) for C in m['C']]
    direct=-sp.Rational(7,10)*volume*sum(inverse[mu,nu]*colors[mu].dot(colors[nu])
                                      for mu in range(4) for nu in range(4))
    assert sp.simplify(direct-m['ADM_density'].subs(replacement))==0
    assert (inverse-m['inverse_metric'].subs(replacement)).applyfunc(sp.cancel)==sp.zeros(4)
    assert volume==40
    assert metric[0,1]!=0 and metric[1,2]!=0


def test_literal_Hodge_has_positive_orientation_velocity_coefficient(model):
    m=model['hodge'];prefactor=m['chi']*m['sqrt_h']/m['N']
    actual=sp.hessian(m['density'],list(m['C'][0]))
    assert (actual-prefactor*sp.eye(3)).applyfunc(sp.cancel)==sp.zeros(3)
    assert prefactor.is_positive is True
    assert model['literal_Hodge_prefactor']==prefactor


def test_lower_Christoffel_keeps_covariant_shift_curl_without_lapse_or_shift_dot(model):
    m=model['connection']
    assert all(not entry.has(velocity) for matrix in m['lower_Gamma'] for entry in matrix
               for velocity in m['forbidden_velocities'])
    _,x,_,z=m['coords']
    replacement={m['lapse']:2+x}
    for i in range(3):
        for j in range(i,3):replacement[m['h'][i,j]]=([4,9,16][i] if i==j else 0)
    replacement.update(dict(zip(m['shift'],[z,0,0])))
    Gamma=m['lower_Gamma'][0].subs(replacement).doit()
    E=sp.diag(sp.Rational(1,2),sp.Rational(1,3),sp.Rational(1,4))
    omega=E.T*Gamma*E
    expected=sp.Matrix([[0,0,sp.Rational(1,4)],[0,0,0],[-sp.Rational(1,4),0,0]])
    assert omega==expected
    # Using the contravariant shift in the curl would incorrectly give 1/16.
    assert omega[0,2]!=sp.Rational(1,16)


def test_root_section_satisfies_Sylvester_and_varied_orthonormality(model):
    m=model['section'];a=m['a'];S=sp.diag(*a);E=m['E'];h=m['h']
    assert (S*m['Sdot']+m['Sdot']*S-m['hdot']).applyfunc(sp.cancel)==sp.zeros(3)
    assert (m['Sdot']*E+S*m['Edot']).applyfunc(sp.cancel)==sp.zeros(3)
    assert (m['Edot'].T*h*E+E.T*m['hdot']*E+E.T*h*m['Edot']).applyfunc(sp.cancel)==sp.zeros(3)
    assert (m['omega_time']+m['omega_time'].T).applyfunc(sp.cancel)==sp.zeros(3)


def test_independent_polynomial_SPD_family_has_nonzero_metric_velocity_connection(model):
    t=sp.Symbol('parameter',real=True);S0=sp.diag(1,2,3)
    direction=sp.Matrix([[0,1,0],[1,0,0],[0,0,0]])
    S=S0+t*direction;h=S*S;E=S.inv()
    # S is SPD for |t|<sqrt(2), so E is the principal inverse square root of h there.
    assert all(S.subs(t,sp.Rational(1,4))[:i,:i].det()>0 for i in range(1,4))
    hd=h.diff(t).subs(t,0);Ed=E.diff(t).subs(t,0);E0=E.subs(t,0);h0=h.subs(t,0)
    direct=(E0.T*h0*Ed+E0.T*hd*E0/2).applyfunc(sp.cancel)
    assert direct==sp.Matrix([[0,sp.Rational(1,4),0],[-sp.Rational(1,4),0,0],[0,0,0]])
    m=model['section'];replacement=dict(zip(m['a'],[1,2,3]))
    replacement.update(dict(zip(m['velocities'],[hd[0,0],hd[1,1],hd[2,2],hd[0,1],hd[0,2],hd[1,2]])))
    assert (m['L_matrix'].subs(replacement)-direct).applyfunc(sp.cancel)==sp.zeros(3)
    assert h0*hd-hd*h0!=sp.zeros(3)


def test_rotating_exact_SPD_family_has_the_opposite_signed_velocity(model):
    m=model['section']['curve']
    assert m['hdot0'][0,1]==-3
    assert m['Edot0'][0,1]==sp.Rational(1,2)
    assert m['omega0'][0,1]==-sp.Rational(1,4)
    angle=sp.atan(sp.Rational(3,4))
    h=m['h'].subs(m['parameter'],angle);E=m['E'].subs(m['parameter'],angle)
    assert (E.T*h*E-sp.eye(3)).applyfunc(sp.simplify)==sp.zeros(3)
    assert E==E.T


def test_anisotropic_mixing_is_not_the_isotropic_decoupling(model):
    m=model['section'];scale=sp.Symbol('scale',positive=True)
    assert m['L_E'].subs({a:scale for a in m['a']}).applyfunc(sp.cancel)==sp.zeros(3,6)
    assert m['L_E_at_1_2_3'][2,3]==sp.Rational(1,12)
    c=model['gram']['prefactor']
    assert sp.cancel(model['anisotropic_Hessian'][3,8]+c/12)==0
    assert not oracle.zero(model['negative_controls']['omit_nonisotropic_velocity_cross_block'])
    assert not oracle.zero(model['negative_controls']['freeze_E_violates_connection_antisymmetry'])


@pytest.fixture(scope='module')
def numeric_kinetic(model):
    g=model['gram'];c=sp.Rational(5,7)
    L=sp.Matrix(3,6,lambda i,j:sp.Rational((-1)**(i+j)*(2*i-j+1),i+j+2))
    replacement={g['prefactor']:c,**{g['L'][i,j]:L[i,j] for i in range(3) for j in range(6)}}
    return c,L,g['Hessian'].xreplace(replacement)


def test_all_kinetic_entries_by_exact_finite_polarization(numeric_kinetic):
    c,L,H=numeric_kinetic;point=sp.Matrix([sp.Rational(i-2,i+3) for i in range(9)])
    offset=sp.Matrix([1,-2,3]);step=sp.Rational(2,5)
    def action(v):
        difference=v[6:9,0]-L*v[:6,0]-offset
        return c*difference.dot(difference)/2
    basis=sp.eye(9)
    for i in range(9):
        for j in range(i,9):
            ei,ej=basis[:,i],basis[:,j]
            actual=(action(point+step*ei+step*ej)-action(point+step*ei-step*ej)
                    -action(point-step*ei+step*ej)+action(point-step*ei-step*ej))/(4*step**2)
            assert actual==H[i,j]==H[j,i]


def test_kinetic_rank_and_Schur_certificate_retains_orientation(model):
    g=model['gram'];c=g['prefactor']
    assert (g['Hessian']*g['kernel']).applyfunc(sp.cancel)==sp.zeros(9,6)
    assert g['kernel'][:6,:]==sp.eye(6)
    assert g['orientation_block']==c*sp.eye(3)
    assert g['orientation_block'].det()==c**3
    assert g['kinetic_Schur']==sp.zeros(6)
    assert g['extended_Hessian'][9:13,:]==sp.zeros(4,13)
    assert sp.expand(g['quadratic_form']-g['squared_norm'])==0


def test_regular_orientation_velocity_chart_is_a_congruence(numeric_kinetic):
    c,_,H=numeric_kinetic;R=sp.Matrix([[1,1,0],[0,2,1],[1,0,1]])
    assert R.det()!=0
    change=sp.diag(sp.eye(6),R);new=change.T*H*change
    assert new[6:9,6:9]==c*R.T*R
    schur=new[:6,:6]-new[:6,6:9]*new[6:9,6:9].inv()*new[6:9,:6]
    assert schur==sp.zeros(6)
    assert new[6:9,6:9].det()==c**3*R.det()**2


@pytest.fixture(scope='module')
def payload():
    return oracle.build_payload()


@pytest.mark.parametrize('mutation',['cross','Schur','field_elimination','adoption'])
def test_resigned_receipt_cannot_erase_mixing_or_promote_scope(payload,mutation):
    changed=copy.deepcopy(payload)
    if mutation=='cross':changed['model']['anisotropic_Hessian'][3][8]='0'
    elif mutation=='Schur':changed['model']['gram']['kinetic_Schur'][0][0]='1'
    elif mutation=='field_elimination':changed['scope']['orientation_field_algebraically_eliminated']=True
    else:changed['proposal']['adopted']=True
    changed['calculation_digest']=oracle.digest({k:v for k,v in changed.items() if k!='calculation_digest'})
    with pytest.raises(oracle.ADMKineticError,match='trusted recomputation'):
        oracle.validate_payload(changed)


def test_scope_keeps_local_chart_and_kinetic_only_limits(payload):
    assert payload['scope']['smooth_metric_dependent_frame_section_required'] is True
    assert payload['scope']['Schur_is_only_a_kinetic_velocity_Schur'] is True
    assert payload['sources']['source_gates_inherited'] is False
    assert all(payload['scope'][name] is False for name in (
        'horizontal_field_space_transport_assumed_integrable','orientation_field_algebraically_eliminated',
        'full_Dirac_mode_count','global_unitary_gauge_proved','complete_gravitational_reduced_energy_positive',
        'BF_global_quotient_closed','N4_JUNCTION_BENDING_pass','N7_LINEAR_REDUCTION_pass',
        'P4_full_same_action_pass','B4_pass','B5_pass','nonlinear_stability_proved'))
    assert hashlib.sha256(oracle.SOURCE.read_bytes()).hexdigest()==oracle.SOURCE_SHA


def test_source_mutation_is_rejected_even_after_digest_rebinding(tmp_path,monkeypatch):
    source=json.loads(oracle.SOURCE.read_bytes());source['scope']['N4_JUNCTION_BENDING_pass']=True
    source['calculation_digest']=oracle.digest({k:v for k,v in source.items() if k!='calculation_digest'})
    path=tmp_path/'source.json';path.write_text(json.dumps(source));monkeypatch.setattr(oracle,'SOURCE',path)
    with pytest.raises(oracle.ADMKineticError,match='Ward source byte pin mismatch'):
        oracle.build_payload()


def test_malformed_and_unsigned_receipts_are_rejected(payload):
    with pytest.raises(oracle.ADMKineticError,match='schema'):
        oracle.validate_payload(None)
    changed=copy.deepcopy(payload);changed['scope']['N4_JUNCTION_BENDING_pass']=True
    with pytest.raises(oracle.ADMKineticError,match='digest'):
        oracle.validate_payload(changed)
