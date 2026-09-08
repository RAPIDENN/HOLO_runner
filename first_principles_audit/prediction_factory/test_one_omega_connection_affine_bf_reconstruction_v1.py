"""Independent exterior signs, affine lift, relative gauges and BPS weights."""
from copy import deepcopy
import itertools
import json
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_connection_affine_bf_reconstruction_v1 as gate
else:
    import verify_one_omega_connection_affine_bf_reconstruction_v1 as gate

@pytest.fixture(scope='module')
def model():return gate.derive_model()

@pytest.fixture(scope='module')
def payload():return gate.build_payload()

def independent_wedge(a,b):
    out={}
    for left,x in a.items():
        I=[i for i in range(5) if left&(1<<i)]
        for right,y in b.items():
            J=[i for i in range(5) if right&(1<<i)]
            if set(I).intersection(J):continue
            word=I+J
            sign=(-1)**sum(word[i]>word[j] for i in range(len(word)) for j in range(i+1,len(word)))
            mask=sum(1<<i for i in word);out[mask]=out.get(mask,0)+sign*x*y
    return {m:sp.expand(v) for m,v in out.items() if sp.expand(v)!=0}

def test_basis_counts_and_all_operator_identities(model):
    assert all(model['checks'].values())
    assert [len(model['complex']['basis_masks_by_degree'][p]) for p in range(6)]==[1,5,10,10,5,1]
    for part in ('oriented_green','complex','lift','affine','norms'):
        assert all(gate.zero(v) for v in model[part]['residuals'].values())

def test_wedge_against_independent_permutation_sign():
    for i in range(32):
        for j in range(32):assert gate.wedge({i:1},{j:1})==independent_wedge({i:1},{j:1})

def test_radial_derivative_and_time_contraction_signs_without_matrix_oracle():
    c=gate.symbols_context();r,s=c['r'],c['s'];c['k']=(0,0,0)
    # eta=dt wedge (r^2 dx1 wedge dr) + r^3 dx1 wedge dx2 wedge dr.
    eta={19:r*r,22:r**3}
    assert gate.h(eta,c)=={18:r*r/s}
    actual=gate.d(eta,c)
    # The normal derivative terms vanish because each term already contains dr.
    assert actual=={23:s*r**3}
    assert gate.plus(gate.d(gate.h(eta,c),c),gate.h(actual,c))==eta
    assert gate.contraction({17:1},0)=={16:1}
    assert gate.contraction({17:1},4)=={1:-1}

def test_closed_current_parameterization_does_not_omit_a_component(model):
    c=model['symbols'];lift=model['lift'];J=lift['current_general']
    k1,k2,k3=c['k']
    independent=c['s']*J[14]-sp.I*k1*J[13]+sp.I*k2*J[11]-sp.I*k3*J[7]
    assert sp.expand(lift['current_closure_coefficient']-independent)==0
    assert sp.cancel(lift['J'][14]-(sp.I*k1*J[13]-sp.I*k2*J[11]+sp.I*k3*J[7])/c['s'])==0
    # Arbitrary nonzero tangential momentum and closed current, checked directly.
    value={c['s']:2+sp.I,k1:3,k2:-2,k3:1,J[7]:2,J[11]:-3,J[13]:5}
    numeric=gate.substitute(lift['J'],value)
    nc=dict(c);nc['s']=2+sp.I;nc['k']=(3,-2,1)
    assert gate.d(numeric,nc,boundary=True)=={}

def test_explicit_current_lift_with_cutoff_derivative_has_the_required_signs():
    c=gate.symbols_context();r=c['r'];c['s']=sp.Integer(2);c['k']=(0,0,0)
    f=1-3*r*r+2*r**3;J={7:3} # 3 dt wedge dx1 wedge dx2.
    hJ=gate.h(J,c);B=gate.scale(-sp.Rational(1,2),gate.d(gate.scale(f,hJ),c))
    assert B=={7:-sp.Rational(3,2)*f,22:-sp.Rational(3,4)*sp.diff(f,r)}
    assert gate.d(B,c)=={}
    assert gate.trace(B,c)=={7:-sp.Rational(3,2)}
    assert gate.plus(gate.trace(B,c),gate.scale(-1,gate.trace(gate.scale(-1,B),c)))==gate.scale(-1,J)
    assert gate.d(gate.scale(-f/2,J),c)!={}

def test_A_cutoff_normal_piece_and_boundary_theta_restriction(model):
    c=model['symbols'];lift=model['lift'];r,f,theta=c['r'],c['f'],c['theta']
    assert lift['A_plus'][16]==-sp.diff(f,r)*theta
    assert lift['A_plus'][1]==-c['s']*f*theta
    assert lift['R_E_theta']=={0:theta}
    assert lift['A_plus']==lift['A_minus']
    assert lift['A_boundary']!={}
    assert model['affine']['forbidden_A_erasing_trace']=={0:-theta}

def test_affine_relative_gauges_preserve_trace_and_have_opposite_signs(model):
    c=model['symbols'];a=model['affine'];uv=model['lift']['cutoff_UV_substitution']
    for delta,eps in zip(a['relative_A_differences'],a['epsilon_removal']):
        assert gate.plus(delta,gate.scale(-1,gate.d(eps,c)))=={}
        assert gate.substitute(gate.trace(delta,c),uv)=={}
        assert gate.substitute(gate.trace(eps,c),uv)=={}
    for delta,Lambda in zip(a['relative_B_differences'],a['Lambda_removal']):
        assert gate.plus(delta,gate.d(Lambda,c))=={}
        assert gate.plus(delta,gate.scale(-1,gate.d(Lambda,c)))!={}
    assert a['Lambda_traces'][0]==a['Lambda_traces'][1]
    assert a['forbidden_B_erasing_parameter_jump']==gate.h(model['lift']['J'],c)
    assert a['forbidden_B_erasing_parameter_jump']!={}

def test_choice_of_cutoff_changes_only_the_relative_gauge_class(model):
    c=model['symbols'];r=c['r'];theta=c['theta'];J=model['lift']['J']
    f=1-r*r;g=1-2*r*r+r**4
    delta_A=gate.scale(-1,gate.d({0:(f-g)*theta},c))
    delta_B=gate.scale(-sp.Rational(1,2),gate.d(gate.scale(f-g,gate.h(J,c)),c))
    assert gate.trace(delta_A,c)=={} and gate.trace(delta_B,c)=={}
    assert gate.plus(delta_A,gate.scale(-1,gate.d(gate.h(delta_A,c),c)))=={}
    assert gate.plus(delta_B,gate.d(gate.scale(-1,gate.h(delta_B,c)),c))=={}

def test_nonclosed_current_is_rejected_as_target_of_this_lift(model):
    c=model['symbols'];bad={14:1}
    assert gate.d(bad,c,boundary=True)=={15:c['s']}
    assert gate.h(bad,c)=={}
    assert gate.d(gate.h(bad,c),c,boundary=True)!=bad
    assert not gate.zero(model['negative_witnesses']['nonclosed_current_cannot_be_recovered'])

def test_zero_spatial_momentum_is_allowed_at_nonzero_s(model):
    c=model['symbols'];zero_k={k:0 for k in c['k']};lift=model['lift']
    J=gate.substitute(lift['J'],zero_k)
    assert 14 not in J and J!={}
    nc=dict(c);nc['k']=(0,0,0)
    assert gate.d(J,nc,boundary=True)=={}
    assert gate.d(gate.h(J,nc),nc,boundary=True)==J

def test_BPS_weights_from_inverse_metric_and_volume_independently(model):
    c=model['symbols'];O=c['Omega'];s2=c['sigma']**2+c['tau']**2
    inverse_diagonal=[O**-2]*4+[sp.Integer(1)];volume=O**4
    for row in model['norms']['component_weights']:
        mask=row['mask'];indices=[i for i in range(5) if mask&(1<<i)]
        source=volume*sp.prod(inverse_diagonal[i] for i in indices)
        assert sp.cancel(source-row['input_weight'])==0
        if 0 in indices:
            target=volume*sp.prod(inverse_diagonal[i] for i in indices if i!=0)/s2
            assert sp.cancel(target-row['h_output_weight'])==0
            assert sp.cancel(target/source-O**2/s2)==0
        else:assert row['h_output_weight']==0
    for degree in range(1,6):
        assert any(row['degree']==degree and row['h_output_weight']!=0 for row in model['norms']['component_weights'])

def test_graph_and_lift_regularities_are_not_replaced_by_normalizable_label(model):
    n=model['norms'];decision=model['decision']
    assert 'D_max(d)' in n['domain']
    assert len(n['regular_boundary_data'])==4
    assert 'H1_loc' in n['trace_statement']
    assert decision['all_weak_boundary_traces_admit_this_L2_lift'] is False
    assert decision['compact_gauge_for_all_L2_solutions_claimed'] is False
    assert decision['physical_energy_or_global_temporal_L2_proved'] is False
    assert decision['sourced_B_order_epsilon_two_solved'] is False
    assert model['assumptions']['linear_bulk_material_current']=='J4_bulk=0'

def test_controls_and_remaining_limits(model):
    assert len(model['negative_controls'])==9 and all(model['negative_controls'].values())
    positive={'selected_linear_affine_BF_quotient_bijection','closed_current_extension_and_trace_identity_checked',
              'relative_gauge_homotopies_checked','BPS_auxiliary_graph_estimates_conditional'}
    for name,value in model['decision'].items():assert value is (name in positive)

def test_old_positive_jump_is_rejected_against_core_Stokes_derivation(model):
    c=model['symbols'];lift=model['lift'];green=gate.current_core.derive_oriented_bf_green()
    assert green['boundary_jump_coefficient']==1
    assert green['required_B_jump_coefficient']==-1
    assert green['compatibility_current_coefficient']==1
    symbols=green['symbols'];component_row=green['component_oracle']['combined_interface_row']
    assert sp.expand(component_row.subs(symbols['bp'],symbols['bm']-symbols['J']))==0
    assert sp.expand(component_row.subs(symbols['bp'],symbols['bm']+symbols['J']))==-2*symbols['J']
    row=lambda jump:gate.plus(gate.scale(green['boundary_jump_coefficient'],jump),lift['J'])
    assert row(lift['jump'])=={}
    # This old candidate remains bulk closed; only the derived interface row rejects it.
    old_plus=gate.scale(-1,lift['B_plus']);old_minus=gate.scale(-1,lift['B_minus'])
    assert gate.d(old_plus,c)=={} and gate.d(old_minus,c)=={}
    old_jump=gate.substitute(gate.plus(gate.trace(old_plus,c),gate.scale(-1,gate.trace(old_minus,c))),lift['cutoff_UV_substitution'])
    assert row(old_jump)==gate.scale(2,lift['J'])

@pytest.mark.parametrize('mutation',['erase_theta','source_order_two','flip_B_minus','restore_old_jump'])
def test_rehashed_receipt_mutations_require_fresh_derivation(payload,model,mutation):
    bad=deepcopy(payload)
    if mutation=='erase_theta':bad['decision']['theta_boundary_data_erased']=True
    elif mutation=='source_order_two':bad['decision']['sourced_B_order_epsilon_two_solved']=True
    elif mutation=='flip_B_minus':bad['model']['lift']['B_minus']=deepcopy(bad['model']['lift']['B_plus'])
    else:bad['model']['lift']['jump']=gate._serialize(gate.scale(-1,model['lift']['jump']))
    bad['calculation_digest']=gate.canonical_digest({k:v for k,v in bad.items() if k!='calculation_digest'})
    with pytest.raises(gate.AffineBFError,match='fresh derivation'):gate.validate_payload(bad)

def test_pinned_note_and_current_proposal_cannot_be_rebound(tmp_path):
    note=tmp_path/'note.md';note.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.AffineBFError,match='note byte hash'):gate.load_sources(note_path=note)
    proposal=json.loads(gate.CURRENT_RECEIPT.read_bytes());proposal['arbitrary_promotion']=True
    proposal['calculation_digest']=gate.canonical_digest(proposal)
    path=tmp_path/'proposal.json';path.write_text(json.dumps(proposal))
    with pytest.raises(gate.AffineBFError,match='current_proposal byte hash'):gate.load_sources(current_path=path)
    core=tmp_path/'core.py';core.write_bytes(gate.CORE.read_bytes()+b'\n')
    with pytest.raises(gate.AffineBFError,match='oriented_Stokes_core byte hash'):gate.load_sources(core_path=core)

def test_cli_receipt_write_is_exclusive(tmp_path,monkeypatch,payload):
    monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(payload))
    path=tmp_path/'receipt.json';gate.main(['--write',str(path)]);before=path.read_bytes()
    with pytest.raises(FileExistsError):gate.main(['--write',str(path)])
    assert path.read_bytes()==before
