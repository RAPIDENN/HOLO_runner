"""Independent q=0 local-density, SO(3), Schur and receipt tests.

The source fixture validates the upstream receipts once. Receipt mutation
checks reuse that already validated source identity while recomputing the
q=0 matrix; they do not repeat the complete upstream proof chain per mutation.
Production build_payload/validate_payload have no skip-validation argument.
"""
from copy import deepcopy
import json

import pytest
import sympy as sp

if __package__:
    from . import verify_one_omega_zero_momentum_linear_v1 as gate
else:
    import verify_one_omega_zero_momentum_linear_v1 as gate


def zero(value):
    return all(sp.cancel(x) == 0 for x in value) if isinstance(value, sp.MatrixBase) else sp.cancel(value) == 0


@pytest.fixture(scope='module')
def model():
    return gate.derive_model()


@pytest.fixture(scope='module')
def load():
    return gate.derive_positive_real_load()


@pytest.fixture(scope='module')
def payload():
    return gate.build_payload()


def test_all_spatial_entries_against_independent_local_density(model):
    """Use K_ij=dot(H_ij)/2 and an explicit spatial trace, not 4D projectors."""
    names = ('H11', 'H12', 'H13', 'H22', 'H23', 'H33')
    h11,h12,h13,h22,h23,h33 = sp.symbols('h11 h12 h13 h22 h23 h33')
    fields = (h11,h12,h13,h22,h23,h33)
    spatial = sp.Matrix([[h11,h12,h13],[h12,h22,h23],[h13,h23,h33]])
    trace = h11+h22+h33
    frobenius = h11*h11+h22*h22+h33*h33+2*(h12*h12+h13*h13+h23*h23)
    P,s = model['parameters'],model['s']
    b,lam,M,KT,G,Kv = (P[n] for n in ('Mb2','lambda_K','M5c','K_T','G','K_v'))
    # Local foliation kinetic density after w=i*s; all spatial derivatives zero.
    Llocal = -b*s*s*(frobenius-lam*trace*trace)/8
    LbulkTT = -M*KT*(frobenius-trace*trace/3)/8
    zeta = trace/6
    LbulkScalar = 3*model['C0']*s*s*zeta*zeta-G*Kv*zeta*zeta/2
    independently_differentiated = sp.hessian(Llocal+LbulkTT+LbulkScalar, fields)
    indices = [model['index'][name] for name in names]
    assert zero(independently_differentiated-model['H_q_zero'].extract(indices,indices))
    assert sp.expand(sp.trace(spatial*spatial)-frobenius) == 0


def test_five_traceless_components_keep_all_SO3_metric_directions(model):
    E = model['SO3_tensor_basis']
    assert len(E) == 5
    assert all(e.T == e and sp.trace(e) == 0 for e in E)
    assert sp.Matrix(5,5,lambda i,j:sp.trace(E[i]*E[j])) == sp.eye(5)
    spatial_tensor_columns = sp.Matrix.hstack(*(sp.Matrix(e).reshape(9,1) for e in E))
    assert spatial_tensor_columns.rank() == 5
    assert zero(model['transformed'][5:10,5:10]+model['F_T']*sp.eye(5)/4)
    assert model['basis_determinant'] == sp.sqrt(6)/2


def test_off_diagonal_and_plus_normalizations_independent_of_new_coordinates(model):
    H,idx,FT = model['H_q_zero'],model['index'],model['F_T']
    for name in ('H12','H13','H23'):
        assert zero(H[idx[name],idx[name]]+FT/2)
    plus = sp.zeros(15,1)
    plus[idx['H11']],plus[idx['H22']] = 1,-1
    assert zero((plus.T*H*plus)[0]+FT/2)
    # Missing 1/sqrt(2) produces a factor-two error, not a distinct pole.
    assert not zero(model['negative_witnesses']['omit_off_diagonal_Frobenius_normalization'])


def test_time_reparametrization_supplies_the_fifth_null_direction(model):
    idx,H,s = model['index'],model['H_q_zero'],model['s']
    time,extra = model['gauge_vectors'][:,0],model['gauge_vectors'][:,4]
    lapse = sp.zeros(15,1);lapse[idx['n']]=1
    tau = sp.zeros(15,1);tau[idx['tau']]=1
    assert zero((time-extra)/s-lapse)
    assert extra == tau
    for name in ('n','N1','N2','N3','tau'):
        assert H[idx[name],:] == sp.zeros(1,15)
    assert model['gauge_minor'] == s**4
    assert zero(H*model['gauge_vectors'])
    assert model['gauge_vectors'][:,1:4].extract([idx[n] for n in ('H11','H22','H33')],range(3)) == sp.zeros(3)


def test_scalar_spring_is_eliminated_by_its_own_stationary_equation(model):
    zeta,D = sp.symbols('zeta D')
    P,s = model['parameters'],model['s']
    G,Kv,beta = P['G'],P['K_v'],P['beta']
    density = -3*model['Bstar']*s*s*zeta*zeta/2-G*Kv*(zeta-D)**2/2-beta*D*D/2
    independent_D = G*Kv*zeta/(G*Kv+beta)
    assert sp.cancel(sp.diff(density,D).subs(D,independent_D)) == 0
    eliminated = sp.cancel(density.subs(D,independent_D))
    assert zero(sp.diff(eliminated,zeta,2)-model['scalar_Schur'])
    assert zero(sp.hessian(density,(zeta,D))-model['scalar_block'])
    assert zero(model['scalar_block'].det()+model['P_D']*model['scalar_Schur'])


def test_material_triplet_decouples_from_every_other_amplitude(model):
    idx,H = model['index'],model['H_q_zero']
    for name in ('vphi1','vphi2','vphi3'):
        row = idx[name]
        assert zero(H[row,row]+model['P_chi'])
        assert all(H[row,j] == 0 for j in range(15) if j != row)
    assert not model['H_q_zero'].has(model['parameters']['y'])


def test_scalar_positive_real_load_uses_full_series_impedance(load):
    assert all(load['checks'].values())
    ctx = load['symbols']
    for vals in ((1,2,3,-4,2),(2,-1,1,5,3)):
        sigma,tau,x,y,beta = map(sp.Integer,vals)
        sc,z = sigma+sp.I*tau,x+sp.I*y
        expected = sp.re(1/(1/z+sc/beta))
        actual = load['real_part'].subs({ctx['sigma']:sigma,ctx['tau']:tau,
                                        ctx['x']:x,ctx['y']:y,ctx['beta']:beta})
        assert sp.cancel(actual-expected) == 0
        assert actual.is_positive is True
    assert load['reciprocal_real'].is_positive is True


def test_candidate_Bstar_bound_is_rational_and_keeps_decimal_lambda(model):
    literal = model['literal_candidate']
    lam = sp.Rational('-0.5535068954004245')
    assert literal['lambda_K'] == lam
    assert lam < -sp.Rational(1,2)
    assert literal['Bstar_lower_bound'] == 2*(1-3*lam)-sp.Rational(5,2)
    assert literal['Bstar_lower_bound'] > sp.Rational(5,2)
    assert literal['Bstar'] == 2*(1-3*lam)-2*sp.exp(sp.Rational(1,5))
    assert literal['not_a_decimal_to_exponential_identity'] is True
    assert model['parameters']['lambda_K'].is_positive is not True


def test_model_controls_and_rank_are_not_a_particle_count(model):
    assert all(model['checks'].values())
    assert all(model['negative_controls'].values())
    assert len(model['negative_controls']) == 5
    assert model['algebraic_rank_under_nonzero_denominators'] == 10
    assert model['particle_count'] is None


def test_load_sources_invokes_both_fresh_validators(monkeypatch):
    calls = []
    monkeypatch.setattr(gate.assembly,'validate_payload',lambda value:calls.append(('assembly',value['schema'])))
    monkeypatch.setattr(gate.variational,'validate_payload',lambda value:calls.append(('variational',value['schema'])))
    sources = gate.load_sources()
    assert [name for name,_ in calls] == ['assembly','variational']
    assert sources['assembly']['freshly_validated'] is True
    assert sources['variational']['freshly_validated'] is True


def test_invalid_pins_stop_build_before_matrix_calculation(monkeypatch):
    def stop(*args,**kwargs):
        raise gate.ZeroMomentumError('sentinel invalid pin')
    def forbidden():
        pytest.fail('matrix calculation started before source validation')
    monkeypatch.setattr(gate,'load_sources',stop)
    monkeypatch.setattr(gate,'derive_model',forbidden)
    with pytest.raises(gate.ZeroMomentumError,match='sentinel'):
        gate.build_payload()


def test_note_and_receipt_byte_pins_reject_modified_sources(tmp_path):
    note = tmp_path/'note.md';note.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.ZeroMomentumError,match='note byte hash'):
        gate.load_sources(note_path=note)
    receipt = json.loads(gate.ASSEMBLY_RECEIPT.read_bytes())
    receipt['decision']['full_N7'] = True
    receipt['calculation_digest'] = gate.canonical_digest({k:v for k,v in receipt.items() if k!='calculation_digest'})
    path = tmp_path/'assembly.json';path.write_text(json.dumps(receipt))
    with pytest.raises(gate.ZeroMomentumError,match='source byte hash'):
        gate.load_sources(assembly_path=path)


def test_payload_scope_keeps_all_exclusions(payload):
    assert all(payload['checks'].values())
    assert all(payload['negative_controls'].values())
    decision = payload['decision']
    assert decision['q_zero_non_gauge_boundary_denominators_nonzero_on_selected_RHP_branch'] is True
    for key in ('particle_count_inferred_from_rank','static_s_zero_case_certified',
                'imaginary_axis_uniform_extension_certified','other_IR_domains_certified',
                'global_BF_edge_mode_absence_pass','A_minus_frame_connection_edge_sector_eliminated',
                'independent_embedding_equations_certified','full_physical_constraint_reduction_certified',
                'full_N7','full_P4','B4','B5'):
        assert decision[key] is False


@pytest.mark.parametrize('mutation',['rank_to_particles','BF_promotion','trace_normalization'])
def test_rehashed_mutants_rejected_by_fresh_q_zero_matrix(payload,monkeypatch,mutation):
    # Reuse only the source identity whose expensive validators ran in payload.
    monkeypatch.setattr(gate,'load_sources',lambda *args,**kwargs:deepcopy(payload['sources']))
    altered = deepcopy(payload)
    if mutation == 'rank_to_particles':
        altered['decision']['particle_count_inferred_from_rank'] = True
    elif mutation == 'BF_promotion':
        altered['decision']['global_BF_edge_mode_absence_pass'] = True
    else:
        altered['model']['basis'][4][10] = '1'
    altered['calculation_digest'] = gate.canonical_digest({k:v for k,v in altered.items() if k!='calculation_digest'})
    with pytest.raises(gate.ZeroMomentumError,match='fresh derivation'):
        gate.validate_payload(altered)


def test_cli_write_is_exclusive(tmp_path,monkeypatch,payload):
    monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(payload))
    path = tmp_path/'receipt.json'
    gate.main(['--write',str(path)])
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        gate.main(['--write',str(path)])
    assert path.read_bytes() == original
