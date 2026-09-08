"""Independent sector, gauge-patch, Schur and energy-identity controls."""
import sympy as sp
import pytest
from . import verify_one_omega_topological_sector_reduction_v1 as oracle


@pytest.fixture(scope='module')
def model():
    return oracle.derive_model()


def test_two_tensor_polarizations_have_same_full_denominator(model):
    assert sp.cancel(model['tensor_cross']+model['F_tensor']/2)==0
    assert sp.cancel(model['tensor_plus']+model['F_tensor']/2)==0
    assert not model['F_tensor'].has(model['parameters']['K_v'])


def test_vector_gauge_fix_does_not_divide_by_the_physical_denominator(model):
    q,w=model['q'],model['frequency'];p2=q*q-w*w
    gauge=sp.Matrix([-sp.I*w,sp.I*q])
    for block in model['vector_blocks'].values():
        metric=block['matrix'][:2,:2]
        assert all(sp.cancel(x)==0 for x in metric*gauge)
        # h13=0 is attained using xi=-h13/(i*q), no division by F_vector.
        assert sp.cancel(metric[0,0]-q*q*model['F_vector']/(2*p2))==0
        assert sp.cancel(metric[1,1].subs(q,0)+model['F_vector'].subs(q,0)/2)==0


def test_complex_gauge_block_eigenvalues_do_not_count_physical_poles(model):
    q,w=model['q'],model['frequency'];P=model['parameters']
    sub={q:1,w:sp.I,P['K_T']:1,P['M5c']:1,P['Mb2']:1}
    block=model['vector_blocks']['1']['matrix'][:2,:2].subs(sub)
    assert block.rank()==1
    assert block*block==sp.zeros(2)
    assert block[0,0]!=0
    assert model['F_vector'].subs(sub)!=0


def test_scalar_gauge_injection_uses_Hs_equal_four_zeta(model):
    idx=model['base']['index'];T=model['scalar_injection']
    assert T[idx['tau'],:]==sp.zeros(1,5)
    for name in ('H11','H22','H33'):
        assert T[idx[name],2]==2
    assert T[idx['H11'],2]+T[idx['H22'],2]==4


def test_exact_block_factorization_preserves_both_pivots(model):
    H=model['scalar_5x5'];L=model['left_elimination'];R=model['right_elimination']
    result=(L*H*R).applyfunc(sp.cancel)
    assert result[:3,:3]==model['scalar_3x3']
    assert result[:3,3:]==sp.zeros(3,2)
    assert result[3:,:3]==sp.zeros(2,3)
    assert result[3:,3:]==model['pivot_block']
    assert L.det()==R.det()==1
    assert sp.cancel(model['pivot_block'].det()-model['P_Omega']*model['P_material'])==0


def test_material_and_Omega_series_loads_are_independent_schur_reductions(model):
    P=model['parameters'];G,Kv,beta,kap,y,Z,p=(P[n] for n in ('G','K_v','beta','kappa_hat','y','Z5','p_material'))
    k=2*Z*p
    expected_robin=y*y*(kap-kap**2/(kap+k))
    expected_beta=G*Kv-(G*Kv)**2/(G*Kv+beta)
    assert sp.cancel(model['Pi_R']-expected_robin)==0
    assert sp.cancel(model['Delta_beta']-expected_beta)==0
    assert sp.simplify(model['Pi_R'].subs(p,0))==0
    assert sp.simplify(model['Delta_beta'].subs(Kv,0))==0


def test_local_wall_contact_cannot_be_discarded_from_scalar_action(model):
    fields=tuple(model['scalar_fields'][:3,:])
    full_reference=sp.hessian(model['L3'],fields)
    assert all(sp.cancel(x)==0 for x in full_reference-model['scalar_3x3'])
    missing=sp.hessian(model['L3']-model['L3_contact'],fields)
    assert any(sp.cancel(x)!=0 for x in missing-model['scalar_3x3'])


def test_reduction_does_not_claim_the_remaining_scalar_determinant_stable(model):
    assert all(model['checks'].values())
    assert not model['scope']['remaining_scalar_determinant_nonzero_in_RHP']
    assert not model['scope']['pivots_discarded_as_unphysical']
    assert not model['scope']['scalar_q_zero_alternate_reduction_certified']


from . import one_omega_positive_real_energy_v1 as energy


@pytest.fixture(scope='module')
def positive_energy():
    return energy.derive_model()


def test_Green_real_part_identity_is_exact_for_complex_frequency(positive_energy):
    m=positive_energy;s=m['symbols'];frequency=s['sigma']+sp.I*s['tau']
    identity=sp.re(m['KT']/frequency)*s['H0_squared']/2
    expected=s['sigma']*(s['Iw']+(s['Ir']+s['q']**2*s['Iw'])/(s['sigma']**2+s['tau']**2))
    assert sp.simplify(sp.expand_complex(identity-expected))==0
    assert all(m['checks'].values())
    assert all(value==0 for value in m['residuals'].values())


def test_strict_pivot_bound_needs_Re_P_over_s_not_Re_P(positive_energy):
    m=positive_energy;s=m['symbols']
    point={s['sigma']:1,s['tau']:3,s['q']:0,s['Iv']:0,s['Iq']:1,
           s['R0_squared']:1,s['G']:1,s['beta']:1}
    assert sp.re(m['Pv'].subs(point))<0
    assert sp.re((m['Pv']/m['s']).subs(point))>0
    assert m['expected_Pv_over_s'].is_positive is True
    assert m['expected_material'].is_positive is True


def test_Green_mutations_do_not_replace_a_physical_branch(positive_energy):
    m=positive_energy
    assert all(m['negative_controls'].values())
    assert m['witnesses']['missing_conjugate']['correct_energy']==1
    assert m['witnesses']['missing_conjugate']['wrong_energy']==-1
    assert not m['scope']['finite_witnesses_promote_global_physics']
    assert not m['scope']['global_DtN_existence_proved']


def test_principal_root_cut_is_avoided_in_the_open_RHP(positive_energy):
    s=positive_energy['symbols'];sigma,tau,q=s['sigma'],s['tau'],s['q']
    p2=(sigma+sp.I*tau)**2+q*q
    assert sp.simplify(sp.im(p2)-2*sigma*tau)==0
    assert sp.re(p2.subs(tau,0)).is_positive is True


def test_resigned_receipt_cannot_promote_the_remaining_scalar_determinant():
    import copy
    document=oracle.build_payload()
    assert len(document['checks'])==25
    mutant=copy.deepcopy(document)
    mutant['decision']['remaining_scalar_RHP_determinant_certified_nonzero']=True
    mutant['calculation_digest']=oracle.canonical_digest({k:v for k,v in mutant.items() if k!='calculation_digest'})
    with pytest.raises(ValueError,match='fresh derivation'):
        oracle.validate_payload(mutant)
