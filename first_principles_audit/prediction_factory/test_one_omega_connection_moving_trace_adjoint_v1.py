"""Independent finite-map, adjoint and BF change-of-coordinates tests."""
from copy import deepcopy
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_connection_moving_trace_adjoint_v1 as gate
else:
    import verify_one_omega_connection_moving_trace_adjoint_v1 as gate

@pytest.fixture(scope='module')
def model():return gate.derive_model()

@pytest.fixture(scope='module')
def payload(model):
    # Receipt mutations reuse a single freshly computed model, not an artifact.
    # The production --verify path calls derive_model again without this fixture.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(gate,'derive_model',lambda:model)
        return gate.build_payload()


def independent_pair_three_one(Q,a):
    return -gate.inner(Q[1,2,3],a[0])+gate.inner(Q[0,2,3],a[1])-gate.inner(Q[0,1,3],a[2])+gate.inner(Q[0,1,2],a[3])


def test_raw_trace_coordinate_chain_rule_without_using_curvature(model):
    trace=model['parts']['trace'];A,f,df=trace['A'],trace['f'],trace['df']
    for data in trace['sides'].values():
        for mu in range(4):
            independent=data['deltaA'][mu]+f*data['dnA'][mu]+df[mu]*data['An']+gate.bracket(data['eta'],A[mu])-data['deta'][mu]
            assert gate.zero(data['raw_trace'][mu]-independent)
            assert not gate.zero(data['raw_trace'][mu]-(independent-df[mu]*data['An']))


def test_metric_graph_has_gradient_squared_at_second_not_first_order(model):
    trace=model['parts']['trace'];eps,f,df=trace['epsilon'],trace['f'],trace['df']
    data=trace['sides']['plus'];K=data['K'];gamma=trace['gamma']
    # Direct embedding tangent vectors, no substitution of a shape formula.
    E=sp.zeros(5,4);E[0,:]=eps*df.T;E[1:,:]=sp.eye(4)
    g=sp.diag(sp.ones(1),gamma+2*eps*f*K)
    pulled=E.T*g*E
    assert gate.zero(pulled.diff(eps).subs(eps,0)-2*f*K)
    assert gate.zero(pulled.diff(eps,2).subs(eps,0)-2*df*df.T)
    assert df*df.T!=sp.zeros(4)


def test_distinct_normal_jets_require_two_bulk_adjustments(model):
    trace=model['parts']['trace'];f=trace['f'];plus,minus=(trace['sides'][n] for n in ('plus','minus'))
    frozen_plus=plus['induced_metric'].xreplace({x:0 for x in plus['delta_g'].free_symbols})
    frozen_minus=minus['induced_metric'].xreplace({x:0 for x in minus['delta_g'].free_symbols})
    assert gate.zero(frozen_plus-frozen_minus-2*f*(plus['K']-minus['K']))
    assert not gate.zero(frozen_plus-frozen_minus)
    for data in (plus,minus):
        assert gate.zero(data['induced_metric'].xreplace(data['metric_substitution'])-trace['common_h'])
        for mu in range(4):
            assert gate.zero(data['raw_trace'][mu].xreplace(data['connection_substitution'])-trace['common_a'][mu])


def test_independent_exact_Cayley_family_about_another_axis():
    """An exact SO3 family and nonabelian bulk connection, not formal commutator input."""
    eps,n,t,x,y,z=sp.symbols('epsilon n t x y z',real=True);coords=(t,x,y,z)
    T=[sp.Matrix(3,3,lambda a,b:sp.LeviCivita(I,a,b)) for I in range(3)]
    f=x+y*y;eta=(x-z)*T[0]
    r=(sp.eye(3)+eps*eta/2)*(sp.eye(3)-eps*eta/2).inv()
    rinv=r.T
    assert gate.zero(r.T*r-sp.eye(3))
    An=z*T[1]+x*T[2]
    bulk=[(n+y)*T[1]+z*T[0],n*T[2],x*T[1],n*T[0]]
    mixed_nonzero=False
    for mu,c in enumerate(coords):
        A=bulk[mu].subs(n,0)
        finite=r*(bulk[mu].subs(n,eps*f)+eps*sp.diff(f,c)*An)*rinv-r.diff(c)*rinv
        derivative=finite.diff(eps).subs(eps,0)
        Fn=bulk[mu].diff(n).subs(n,0)-An.diff(c)+gate.bracket(An,A)
        Lambda=f*An-eta
        reference=f*Fn+Lambda.diff(c)+gate.bracket(A,Lambda)
        assert gate.zero(derivative-reference)
        mixed_nonzero|=not gate.zero(Fn)
    assert mixed_nonzero and not gate.zero(gate.bracket(eta,bulk[0].subs(n,0)))


def test_production_oracle_has_all_required_nonzero_inputs(model):
    data=model['parts']['Cayley']
    assert not gate.zero(data['An'])
    assert any(not gate.zero(value) for value in data['Fn'])
    assert any(sp.diff(data['f'],x)!=0 for x in data['coords'])
    assert not gate.zero(gate.bracket(data['eta'],data['bulk_A'][0].subs(data['n'],0)))
    for a,b in zip(data['raw_trace'],data['reference_trace']):assert gate.zero(a-b)


def test_SC_adjoint_with_nonconstant_volume_and_noncommuting_colors():
    x,z,chi=sp.symbols('x z chi',positive=True)
    T=[sp.Matrix(3,3,lambda a,b:sp.LeviCivita(I,a,b)) for I in range(3)]
    coords=(x,z);volume=1+x*x
    A=(x*T[0],z*T[1]);C=((1+z)*T[1],x*T[2]);Lambda=(x+z)*T[1]+x*z*T[2]
    raw=-chi*volume*sum(gate.inner(C[i],Lambda.diff(coords[i])+gate.bracket(A[i],Lambda)) for i in range(2))
    G=chi*sum(((volume*C[i]).diff(coords[i])/volume+gate.bracket(A[i],C[i]) for i in range(2)),sp.zeros(3))
    border=[-chi*volume*gate.inner(C[i],Lambda) for i in range(2)]
    divergence=sum(sp.diff(border[i],coords[i]) for i in range(2))
    assert sp.cancel(raw-volume*gate.inner(G,Lambda)-divergence)==0
    assert sp.expand(divergence)!=0 and sp.expand(volume*gate.inner(G,Lambda))!=0


def test_differential_identification_operator_keeps_its_boundary():
    x,z=sp.symbols('x z',real=True);volume=1+x*x;f=x*x+z
    T=[sp.Matrix(3,3,lambda a,b:sp.LeviCivita(I,a,b)) for I in range(3)]
    G=(x*x+z)*T[0]+(1+x*z)*T[1];R=z*T[2]
    S=((1+z)*T[0],x*T[1]);coords=(x,z)
    eta=R*f+sum((S[i]*sp.diff(f,coords[i]) for i in range(2)),sp.zeros(3))
    raw=-volume*gate.inner(G,eta)
    coefficient=-volume*gate.inner(G,R)+sum(sp.diff(volume*gate.inner(G,S[i]),coords[i]) for i in range(2))
    boundary=[-f*volume*gate.inner(G,s) for s in S]
    div=sum(sp.diff(boundary[i],coords[i]) for i in range(2))
    assert sp.expand(raw-f*coefficient-div)==0
    assert sp.expand(raw-f*coefficient)!=0


def test_intrinsic_clock_is_independent_and_SC_is_counted_once(model):
    part=model['parts']['SC'];common=part['common_intrinsic_variation']
    assert sp.diff(common,part['theta'])==part['E_T']
    assert gate.zero(part['negative']['count_SC_once_per_bulk_face']-common)
    assert not gate.zero(common)
    for side in part['sides'].values():
        assert gate.zero(side['total_boundary']-part['base_boundary']-side['new_boundary'])
        assert not gate.zero(side['G_Lambda'])


def test_extra_target_rotation_requires_plus_eta_conversion(model):
    trace=model['parts']['trace']
    assert gate.zero(trace['residuals']['extra_target_rotation_converts_eta_with_plus_sign'])
    assert not gate.zero(trace['target_rotation'])
    assert gate.zero(trace['residuals']['pinned_tangential_compensation_specialization_only'])


def test_pure_identification_BF_cancellation_from_independent_finite_rotation():
    eps,t,x,y,z=sp.symbols('epsilon t x y z',real=True);coords=(t,x,y,z)
    T=[sp.Matrix(3,3,lambda a,b:sp.LeviCivita(I,a,b)) for I in range(3)]
    eta=x*T[1]
    r=(sp.eye(3)+eps*eta/2)*(sp.eye(3)-eps*eta/2).inv()
    A=(T[2],z*T[0],sp.zeros(3),sp.zeros(3))
    common=[];Deta=[]
    for mu,c in enumerate(coords):
        # f=0 and Eulerian deltaA=0; only the identification moves.
        common.append((r*A[mu]*r.T-r.diff(c)*r.T).diff(eps).subs(eps,0))
        Deta.append(eta.diff(c)+gate.bracket(A[mu],eta))
        assert gate.zero(common[-1]+Deta[-1])
    jump={(1,2,3):sp.zeros(3),(0,2,3):T[1],(0,1,3):sp.zeros(3),(0,1,2):sp.zeros(3)}
    trace_part=independent_pair_three_one(jump,common)
    # Substituting deltaA=a_common-DLambda with Lambda=-eta supplies this.
    complement=independent_pair_three_one(jump,Deta)
    assert sp.expand(trace_part+complement)==0 and sp.expand(trace_part)!=0
    # The original Eulerian BF summand is exactly zero, not trace_part alone.
    assert independent_pair_three_one(jump,[sp.zeros(3)]*4)==0


def test_BF_reparametrization_and_rotation_keep_distinct_obligations(model):
    data=model['parts']['BF']
    assert sp.expand(data['original_BF_in_Eulerian_variables']-data['common_trace_BF_part']-data['BF_chart_complements'])==0
    assert sp.expand(data['pure_identification_common_part']+data['pure_identification_complements'])==0
    assert data['pure_identification_common_part']!=0
    Eplus,Eminus=data['bulk_connection_rows']
    assert gate.zero(data['full_row_before_bulk_equations']-data['row_on_bulk_equations']+Eplus-Eminus)
    assert data['orientation_coefficients']['boundary_jump_coefficient']==1
    assert data['orientation_coefficients']['required_B_jump_coefficient']==-1


def test_receipt_uses_fresh_model_and_keeps_general_gates_false(payload,model,monkeypatch):
    monkeypatch.setattr(gate,'derive_model',lambda:model)
    assert gate.validate_payload(payload)==payload
    assert payload['decision']['actual_normal_geometric_eta_operator_identified'] is False
    assert payload['decision']['complete_total_groupoid_Euler_identified'] is False
    assert payload['decision']['complete_EH_GHY_moving_variation'] is False


@pytest.mark.parametrize('kind',('trace','boundary','normal_eta','BF_whole','double_action','promotion'))
def test_resigned_receipt_mutations_against_fresh_fixture(payload,monkeypatch,kind):
    expected=deepcopy(payload);monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(expected))
    bad=deepcopy(payload)
    if kind=='trace':bad['finite_trace']['plus']['raw_trace'][0][0][1]='0'
    elif kind=='boundary':bad['SC_adjoint']['sides']['plus']['new_boundary'][0][0]='0'
    elif kind=='double_action':bad['decision']['paired_gluing_and_single_intrinsic_action_checked']=False
    else:
        keys={'normal_eta':'normal_eta_inferred_from_tangential_sigma',
              'BF_whole':'common_BF_trace_part_is_entire_moving_BF_Green','promotion':'full_N4'}
        bad['decision'][keys[kind]]=True
    bad.pop('calculation_digest');bad['calculation_digest']=gate.digest(bad)
    with pytest.raises(gate.MovingTraceError,match='fresh source-bound'):gate.validate_payload(bad)


def test_source_pins_reject_changed_note_and_rebound_source(tmp_path):
    changed=tmp_path/'note.md';changed.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.MovingTraceError,match='lemma hash'):gate.load_sources(note=changed)
    stem=next(iter(gate.SOURCE_PINS));p=gate.HERE/'artifacts'/(stem+'.json')
    doc=gate.read_json(p.read_bytes());doc['extra_claim']='wrong'
    doc.pop('calculation_digest');doc['calculation_digest']=gate.digest(doc)
    (tmp_path/p.name).write_text(__import__('json').dumps(doc))
    with pytest.raises(gate.MovingTraceError,match='source byte hash'):gate.load_sources(artifact_directory=tmp_path)


def test_json_and_receipt_types_are_strict():
    for raw in ('{"x":1,"x":2}','{"x":NaN}','[]'):
        with pytest.raises(gate.MovingTraceError):gate.read_json(raw)
    with pytest.raises(gate.MovingTraceError,match='must be object'):gate.validate_payload(None)
    with pytest.raises(gate.MovingTraceError,match='digest'):gate.validate_payload({'schema':gate.SCHEMA})
