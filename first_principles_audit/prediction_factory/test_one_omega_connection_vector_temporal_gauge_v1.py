"""Independent density/chain-rule oracles for the N=0 vector chart."""
from copy import deepcopy
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_connection_vector_temporal_gauge_v1 as gate
else:
    import verify_one_omega_connection_vector_temporal_gauge_v1 as gate

@pytest.fixture(scope='module')
def model():return gate.derive_model()

@pytest.fixture(scope='module')
def payload():return gate.build_payload()


@pytest.mark.parametrize('axis,orientation',(('1',1),('2',-1)))
def test_extracted_H18_block_equals_independent_literal_density(model,axis,orientation):
    N,H,theta=sp.symbols('N H theta');w,q,B,chi=(model[k] for k in ('w','q','B','chi'))
    density=B*(q*N+w*H)**2/4+chi*((w*theta+orientation*q*N/2)**2-q*q*(theta-orientation*H/2)**2)/2
    reference=sp.hessian(density,(N,H,theta))
    assert gate.zero(model['sectors'][axis]['block']-reference)
    assert gate.zero(model['sectors'][axis]['residuals']['coupling_to_all_other_H18_fields'])
    # A sign flip of the orientation coupling changes real off-diagonal entries.
    wrong=density.xreplace({theta:-theta})
    assert not gate.zero(reference-sp.hessian(wrong,(N,H,theta)))


def test_chain_rule_and_source_compatibility_for_general_invariant_action():
    """A quartic action avoids merely reusing the quadratic matrix formulas."""
    N,H,theta,w,q,U,Psi=sp.symbols('N H theta w q U Psi',nonzero=True)
    for o in (1,-1):
        independent=U**4+U*Psi**2+3*Psi**3
        action=independent.subs({U:q*N+w*H,Psi:theta-o*H/2},simultaneous=True)
        rows=sp.Matrix([sp.diff(action,x) for x in (N,H,theta)])
        assert sp.expand(-w*rows[0]+q*rows[1]+o*q*rows[2]/2)==0
        # Covector compatibility follows from this identity, even off shell.
        bad=sp.Matrix([1,0,0])
        assert sp.expand((-w*bad[0]+q*bad[1]+o*q*bad[2]/2))==-w


@pytest.mark.parametrize('orientation',(1,-1))
def test_stationary_density_temporal_pivot_and_forcing_without_matrix_helpers(orientation):
    B,chi=sp.symbols('B chi',positive=True)
    w=sp.Symbol('w',nonzero=True);q=sp.Symbol('q',real=True)
    U,Psi,fU,fPsi,H,theta=sp.symbols('U Psi f_U f_Psi H theta')
    J=sp.Matrix([[1/w,0],[sp.Rational(orientation,2)/w,1]])
    L=B*U**2/4+chi*((w*Psi+orientation*U/2)**2-q*q*Psi**2)/2-fU*U-fPsi*Psi
    stationary=sp.solve(sp.diff(L,U),U)[0]
    assert sp.cancel(stationary-(4*fU-2*orientation*chi*w*Psi)/(2*B+chi))==0
    reduced=sp.cancel(L.subs(U,stationary))
    assert sp.cancel(sp.diff(reduced,Psi,2)-(2*chi*B*w*w/(2*B+chi)-chi*q*q))==0
    assert sp.cancel(sp.diff(L,U,2)-(2*B+chi)/4)==0
    source=(fU*(w*H)+fPsi*(theta-orientation*H/2))
    assert gate.zero(J.T*sp.Matrix([sp.diff(source,H),sp.diff(source,theta)])-sp.Matrix([fU,fPsi]))


def test_all_three_rows_with_nonzero_compatible_forces_including_q_zero(model):
    """Exact complex points test the original rows, including the deleted one."""
    for data in model['sectors'].values():
        fU,fPsi=data['force_symbols'];Psi=data['response_symbols'][1]
        w,q,B,chi=(model[k] for k in ('w','q','B','chi'))
        for qvalue in (0,sp.Rational(1,9),3):
            point={w:-2+sp.I,q:qvalue,B:sp.Rational(11,4),chi:sp.Rational(7,5),
                   fU:1+sp.I,fPsi:2-3*sp.I}
            remaining=sp.cancel(data['remaining_row'].subs(point))
            psi_value=sp.solve(remaining,Psi)[0]
            solution=data['original_solution'].subs(point).subs(Psi,psi_value)
            force=data['compatible_force'].subs(point)
            assert gate.zero(data['block'].subs(point)*solution-force)
            assert solution[0]==0
            assert not gate.zero(force)


def test_incompatible_force_cannot_be_repaired_by_retained_solution(model):
    data=model['sectors']['1'];w,q,B,chi=(model[k] for k in ('w','q','B','chi'))
    for qvalue in (0,2):
        block=data['block'].subs({w:sp.I,q:qvalue,B:3,chi:2})
        # Retained forcing is zero, so the unique retained solution is zero.
        solution=sp.zeros(3,1);bad=sp.Matrix([1,0,0])
        assert gate.zero(block[1:,1:]*solution[1:,0])
        assert block*solution-bad==sp.Matrix([-1,0,0])


def test_mutated_matrix_is_rejected_by_ward_and_density_comparison(model):
    data=model['sectors']['1'];changed=data['block'].copy()
    changed[0,2]+=1
    new=gate.analyze_sector(changed,1,model['w'],model['q'],model['chi'],model['B'])
    assert not gate.zero(new['residuals']['ward_row'])
    assert not gate.zero(new['residuals']['all_three_forced_rows'])
    assert not all(new['checks'].values())


def test_direct_q_zero_determinant_and_metric_response_are_retained(model):
    for data in model['sectors'].values():
        w,q,B,chi=(model[k] for k in ('w','q','B','chi'))
        direct=data['block'].subs(q,0).extract([1,2],[1,2])
        assert direct==sp.diag(B*w*w/2,chi*w*w)
        assert sp.cancel(direct.det()-chi*B*w**4/2)==0
        assert sp.cancel(direct.det()-(w*w*data['pivot']*data['Schur']).subs(q,0))==0
        assert not gate.zero(data['Schur'].subs(q,0)-chi*w*w)
        assert gate.zero(data['residuals']['direct_homogeneous_source_comparison'])


def test_old_spatial_chart_has_a_different_nonuniform_representative(model):
    w,q,B,chi=(model[k] for k in ('w','q','B','chi'))
    Psi=sp.Symbol('Psi')
    old_N=-2*chi*w*Psi/(q*(2*B+chi))
    assert sp.limit(q*old_N,q,0)!=0
    data=model['sectors']['1'];fU,fPsi=data['force_symbols']
    new=data['original_solution'].subs(fU,0)
    assert all(not entry.subs(q,0).has(sp.zoo,sp.nan) for entry in new)
    assert sp.cancel(data['chart'].det()-1/w)==0


def test_exact_rational_spectral_diagnostics_obey_q_uniform_bounds(model):
    """Finite examples check factors; the pinned lemma handles the continuum."""
    b,chi=sp.Rational(2),sp.Rational(7,3)
    for s,q in ((1+2*sp.I,0),(sp.Rational(1,7)-3*sp.I,sp.Rational(1,10)),(2+sp.I,8)):
        m=sum(weight*ell/(ell+s*s+q*q) for weight,ell in
              ((sp.Rational(2,7),sp.Rational(1,3)),(sp.Rational(3,5),9),(sp.Rational(1,11),80)))
        B=b+m;den=2*B+chi;r2=sp.expand_complex(s*sp.conjugate(s));sigma=sp.re(s)
        reciprocal_squared=sp.cancel(1/(den*sp.conjugate(den)))
        assert sp.cancel(r2/((2*b+chi)**2*sigma**2)-reciprocal_squared)>0
        Keff=2*chi*B/den;minus_S=s*s*Keff+chi*q*q
        lower=sigma*(2*chi*b/(2*b+chi)+chi*q*q/r2)
        assert sp.cancel(sp.re(minus_S/s)-lower)>0


def test_bound_coefficients_have_finite_q_zero_values_and_required_time_domain(model):
    bounds=model['bounds'];symbols=bounds['symbols'];q=symbols['q']
    for expression in bounds['bounds'].values():
        assert not expression.subs(q,0).has(sp.zoo,sp.oo,sp.nan)
    # The bound itself diverges as sigma -> 0: that limit is not certified.
    inverse=bounds['bounds']['inverse_denominator']
    assert sp.limit(inverse,symbols['sigma'],0,dir='+')==sp.oo


def test_receipt_recomputes_and_preserves_scope(payload):
    actual=gate.validate_payload(payload)
    assert actual==payload
    assert actual['decision']['regular_temporal_vector_chart_for_selected_H18'] is True
    assert actual['decision']['full_N7'] is False
    assert actual['decision']['global_Sobolev_gauge_reconstruction_proved'] is False


@pytest.mark.parametrize('kind',('matrix','q0_determinant','overclaim'))
def test_resigned_receipt_mutations_against_precomputed_trusted_oracle(payload,monkeypatch,kind):
    """Receipt comparison layer only; the fixture was independently recomputed."""
    expected=deepcopy(payload)
    monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(expected))
    bad=deepcopy(payload)
    if kind=='matrix':bad['response']['sectors']['1']['block'][0][2]='999'
    elif kind=='q0_determinant':bad['response']['sectors']['1']['pivot']='1'
    else:bad['decision']['full_N7']=True
    bad.pop('calculation_digest');bad['calculation_digest']=gate.digest(bad)
    with pytest.raises(gate.TemporalGaugeError,match='fresh source-bound'):
        gate.validate_payload(bad)


def test_source_byte_pins_reject_rebound_receipt_and_changed_note(tmp_path):
    changed=tmp_path/'note.md';changed.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.TemporalGaugeError,match='lemma hash'):
        gate.load_sources(note=changed)
    stem=next(iter(gate.SOURCE_PINS));path=gate.HERE/'artifacts'/(stem+'.json')
    doc=gate.read_json(path.read_bytes());doc['decision']['full_N7']=True
    doc.pop('calculation_digest');doc['calculation_digest']=gate.digest(doc)
    (tmp_path/path.name).write_text(__import__('json').dumps(doc))
    with pytest.raises(gate.TemporalGaugeError,match='source byte hash'):
        gate.load_sources(artifact_directory=tmp_path)


def test_json_and_receipt_types_are_strict():
    for value in ('{"x":1,"x":2}','{"x":NaN}','[]'):
        with pytest.raises(gate.TemporalGaugeError):gate.read_json(value)
    with pytest.raises(gate.TemporalGaugeError,match='must be object'):gate.validate_payload(None)
    with pytest.raises(gate.TemporalGaugeError,match='digest'):gate.validate_payload({'schema':gate.SCHEMA})
