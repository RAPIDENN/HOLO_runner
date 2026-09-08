"""Independent frame, stress-component and curved off-shell Ward controls."""
import copy
import hashlib
import json
import pytest
import sympy as sp
from . import verify_one_omega_connection_horizontal_ward_v1 as oracle


@pytest.fixture(scope='module')
def model():
    return oracle.derive_model()


def test_frame_transport_preserves_boost_and_has_the_required_rotation(model):
    t=model['transport'];g,e,u=t['metric'],t['frame'],t['normal']
    difference=t['natural_frame_variation']-t['horizontal_frame_variation']
    assert (u.T*g*difference).applyfunc(sp.expand)==sp.zeros(1,3)
    assert (difference-e*t['rho']).applyfunc(sp.expand)==sp.zeros(4,3)
    assert (t['rho']+t['rho'].T).applyfunc(sp.expand)==sp.zeros(3)
    assert any(value!=0 for value in t['beta'])
    assert not oracle.zero(t['negative_controls']['opposite_sigma_in_transport'])


def test_SO3_norm_and_H18_phase_follow_from_generator_entries(model):
    t=model['transport']
    assert sp.expand(t['G_sigma']-t['spin_gradient_half'])==0
    assert sp.expand(t['G_sigma']-2*t['spin_gradient_half'])!=0
    q,xi=sp.symbols('q xi_transverse',real=True)
    # With T_I,jk=epsilon_Ijk, T2,13=-1; rho13=-partial_z xi1/2.
    rho13=-sp.I*q*xi/2
    color2=rho13/(-1)
    assert t['phase_colors'][0]==sp.Matrix([0,color2,0])
    assert t['phase_colors'][1]==sp.Matrix([-sp.I*q*xi/2,0,0])
    delta_H13=sp.I*q*xi
    assert color2-delta_H13/2==0


def test_Cartan_and_horizontal_connection_keep_all_36_entries(model):
    r=model['transport']['residuals']
    for name in ('Cartan_connection_all_36_entries','horizontal_connection_all_36_entries'):
        assert sum(len(matrix) for matrix in r[name])==36
        assert all(matrix==sp.zeros(3) for matrix in r[name])
    assert r['horizontal_parameter_is_i_xi_C_minus_sigma']==sp.zeros(3)


def test_flat_linear_stress_components_independently_expose_missing_spin(model):
    _,x,_,z=model['symbols']['coords'];chi=model['symbols']['chi']
    tau=model['flat_linear_tau'];expected=sp.zeros(4)
    expected[1,1]=-chi*x
    expected[1,3]=expected[3,1]=chi*z/2
    assert tau==expected
    # Ordinary flat divergence of these explicit components, independent of the Ward RHS.
    coords=model['symbols']['coords']
    direct=sp.Matrix([sum(sp.diff(expected[mu,nu],coords[mu]) for mu in range(4)) for nu in range(4)])
    assert direct==sp.Matrix([0,-chi/2,0,0])
    assert model['flat_linear_divergence']==direct
    assert model['flat_linear_half_spin_divergence']==direct
    assert model['flat']['ward_residual']==sp.zeros(4,1)
    assert not oracle.zero(model['flat']['negative_controls']['omit_horizontal_spin_divergence'])


def test_curved_oracle_is_geometrically_curved_and_retains_nonzero_kappa(model):
    c=model['curved'];g=c['geometry'];_,x,_,_=model['symbols']['coords'];a=model['symbols']['a']
    N=1+a*x*x
    assert g['N']==N
    assert (g['metric']-sp.diag(-N*N,1,1,1)).applyfunc(sp.cancel)==sp.zeros(4)
    assert all(matrix==sp.zeros(3) for matrix in g['omega'])
    expected=sp.zeros(4,3);expected[0,0]=2*a*x
    assert g['kappa']==expected
    assert sp.cancel(g['R_1_0_1_0']-2*a*N)==0
    assert g['R_1_0_1_0'].subs(x,0)==2*a


def test_curved_time_space_stress_entries_from_manual_connection_contraction(model):
    c=model['curved'];_,x,_,z=model['symbols']['coords'];a,chi=model['symbols']['a'],model['symbols']['chi']
    N=1+a*x*x
    # Direct J contraction gives divJ03=-chi*z/N²; the boost subtracts chi*x*z*N'/(2N³).
    assert sp.cancel(c['tau_C'][0,1]+chi*x/(2*N*N))==0
    assert sp.cancel(c['tau_C'][0,3]-chi*z*(1-a*x*x)/(2*N**3))==0
    assert c['tau_C']==c['tau_C'].T
    assert sp.cancel(c['V'][3]-2*chi*a*x*x*z/N**2)==0
    assert c['V'][0]==c['V'][1]==c['V'][2]==0


def test_curved_time_Ward_requires_nonzero_khronon_Euler(model):
    c=model['curved'];_,x,_,_=model['symbols']['coords'];a,chi=model['symbols']['a'],model['symbols']['chi']
    expected=2*chi*a*x*x/(1+a*x*x)
    assert sp.cancel(c['E_T']-expected)==0
    assert sp.cancel(c['divergence_tau'][0]-expected)==0
    assert c['force_chi_C_F'][0]==c['G_C'][0]==c['divergence_G_H'][0]==0
    assert c['ward_residual']==sp.zeros(4,1)
    assert sp.cancel(c['negative_controls']['omit_khronon_Euler'][0]-expected)==0


def test_curved_oracle_does_not_impose_flat_A_or_abelianize_its_components(model):
    c=model['curved'];_,x,_,z=model['symbols']['coords'];chi=model['symbols']['chi'];a=model['symbols']['a']
    generators=[sp.Matrix(3,3,lambda j,k:sp.LeviCivita(i,j,k)) for i in range(3)]
    T1,T2,T3=generators
    # The sign follows from [T2,T1]=+T3 for these exact generators.
    expected_F01=-z*T2+x*x*z*T3
    expected_F03=-x*T2-x*z*z*T1
    assert (c['F'][0][1]-expected_F01).applyfunc(sp.cancel)==sp.zeros(3)
    assert (c['F'][0][3]-expected_F03).applyfunc(sp.cancel)==sp.zeros(3)
    expected_G=chi*((1+3*a*x*x)*T1/(1+a*x*x)+T3)
    assert (c['G']-expected_G).applyfunc(sp.cancel)==sp.zeros(3)
    assert any(matrix!=sp.zeros(3) for row in c['commutators'] for matrix in row)
    assert c['G']!=sp.zeros(3)


def test_curved_divergences_match_independent_index_and_volume_contractions(model):
    c=model['curved']
    assert c['mixed_vs_contravariant_divergence']==sp.zeros(4,1)
    assert c['antisymmetric_divergence_vs_volume_formula']==sp.zeros(4,1)
    assert (c['G_H']+c['G_H'].T).applyfunc(sp.cancel)==sp.zeros(4)
    assert c['divergence_G_H']!=sp.zeros(4,1)
    assert c['ward_residual']==sp.zeros(4,1)


def test_omitting_the_covariant_boost_stress_breaks_the_curved_Ward(model):
    c=model['curved'];u=c['geometry']['normal'];V=c['V']
    wrong_tau=c['tau_C']+(V*u.T+u*V.T)/2
    residue=oracle.mixed_divergence(wrong_tau,c['geometry'])-c['rhs']
    assert residue.applyfunc(sp.cancel)!=sp.zeros(4,1)
    assert residue[0]!=0


@pytest.fixture(scope='module')
def payload():
    return oracle.build_payload()


@pytest.mark.parametrize('mutation',['spin','ET','curved_row','adoption'])
def test_resigned_receipt_cannot_change_Ward_or_adopt_the_candidate(payload,mutation):
    changed=copy.deepcopy(payload)
    if mutation=='spin': changed['model']['curved']['divergence_G_H'][2][0]='0'
    elif mutation=='ET': changed['model']['curved']['E_T']='0'
    elif mutation=='curved_row': changed['model']['curved']['ward_residual'][0][0]='1'
    else: changed['proposal']['adopted']=True
    changed['calculation_digest']=oracle.digest({k:v for k,v in changed.items() if k!='calculation_digest'})
    with pytest.raises(oracle.HorizontalWardError,match='trusted recomputation'):
        oracle.validate_payload(changed)


def test_scope_does_not_promote_full_gluing_or_an_Einstein_solution(payload):
    assert payload['proposal']['A_independent_of_omega'] is True
    assert payload['proposal']['adopted'] is False
    assert payload['sources']['source_gates_inherited'] is False
    assert all(payload['scope'][name] is False for name in (
        'N4_JUNCTION_BENDING_pass','N7_LINEAR_REDUCTION_pass','P4_full_same_action_pass',
        'B4_pass','B5_pass','BF_global_quotient_closed','full_moving_gluing_chain_closed',
        'coupled_Einstein_solution','nonlinear_stability_proved'))
    assert hashlib.sha256(oracle.SOURCE.read_bytes()).hexdigest()==oracle.SOURCE_SHA


def test_source_mutation_is_rejected_after_digest_rebinding(tmp_path,monkeypatch):
    source=json.loads(oracle.SOURCE.read_bytes());source['scope']['N4_JUNCTION_BENDING_pass']=True
    source['calculation_digest']=oracle.digest({k:v for k,v in source.items() if k!='calculation_digest'})
    path=tmp_path/'source.json';path.write_text(json.dumps(source))
    monkeypatch.setattr(oracle,'SOURCE',path)
    with pytest.raises(oracle.HorizontalWardError,match='covariant source byte pin mismatch'):
        oracle.build_payload()


def test_bad_types_and_unsigned_receipt_mutations_are_rejected(payload):
    with pytest.raises(oracle.HorizontalWardError,match='schema'):
        oracle.validate_payload(None)
    altered=copy.deepcopy(payload);altered['scope']['N4_JUNCTION_BENDING_pass']=True
    with pytest.raises(oracle.HorizontalWardError,match='digest'):
        oracle.validate_payload(altered)
