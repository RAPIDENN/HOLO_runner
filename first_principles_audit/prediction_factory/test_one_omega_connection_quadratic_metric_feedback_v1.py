"""Independent mixed-action, complex Fourier and source-norm contrasts."""
from copy import deepcopy
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_connection_quadratic_metric_feedback_v1 as gate
else:
    import verify_one_omega_connection_quadratic_metric_feedback_v1 as gate

@pytest.fixture(scope='module')
def model():return gate.derive_model()

@pytest.fixture(scope='module')
def payload():return gate.build_payload()


def substitute_port(expression,local,theta_values,h_values=None):
    mapping=dict(zip(local['theta'],theta_values))
    if h_values is not None:
        mapping.update({local['h'][i,j]:h_values[i,j] for i in range(3) for j in range(i,3)})
    return expression.subs(mapping,simultaneous=True).doit()


def test_local_polynomial_theta_has_correct_diagonal_metric_half_weight(model):
    """A local harmonic coefficient tests variation, not the selected L2 Poisson map."""
    local=model['local'];x,y,z=local['coords'];chi=local['chi']
    actual=substitute_port(local['tau_literal'],local,[0,0,x*y])
    assert actual==sp.diag(chi,-chi,0)
    assert substitute_port(local['rho'],local,[0,0,x*y])==sp.zeros(3,1)
    # This non-L2 harmonic theta is deliberately not a counterexample to Plancherel.


def test_connection_oracle_varies_the_frame_and_Christoffel_together(model):
    local=model['local'];coords=local['coords'];h=local['h']
    for i in range(3):
        christoffel=sp.Matrix(3,3,lambda a,b:(sp.diff(h[a,b],coords[i])+
            sp.diff(h[a,i],coords[b])-sp.diff(h[i,b],coords[a]))/2)
        frame=sp.Matrix(3,3,lambda a,b:-sp.diff(h[a,b],coords[i])/2)
        assert gate.zero(local['delta_omega_literal'][i]-christoffel-frame)
        assert not gate.zero(christoffel+christoffel.T)
        assert gate.zero(local['delta_omega_literal'][i]+local['delta_omega_literal'][i].T)


def test_literal_mixed_action_weak_variation_with_periodic_offdiagonal_metric(model):
    """Exact cell IBP independently checks the off-diagonal factor and sign."""
    local=model['local'];x,y,z=local['coords'];chi=local['chi']
    wave=sp.sin(x)*sp.sin(2*z)
    h=sp.zeros(3);h[0,2]=h[2,0]=wave
    literal=substitute_port(local['mixed_density'],local,[0,wave,0],h)
    independent_tau_xz=3*chi*wave/2
    actual=sp.integrate(literal,(x,0,2*sp.pi),(z,0,2*sp.pi))
    expected=sp.integrate(independent_tau_xz*wave,(x,0,2*sp.pi),(z,0,2*sp.pi))
    assert sp.simplify(actual-expected)==0
    assert expected==3*chi*sp.pi**2/2
    assert actual!=0


def test_periodic_cell_norm_is_half_source_norm_but_not_global_finite_energy(model):
    local=model['local'];x,y,z=local['coords'];chi=local['chi']
    wave=sp.sin(x)*sp.sin(2*z)
    tau=substitute_port(local['tau_literal'],local,[0,wave,0])
    rho=substitute_port(local['rho'],local,[0,wave,0])
    assert sp.expand(rho[1]-5*chi*wave)==0
    tau_norm=sum(entry**2 for entry in tau)
    rho_norm=sum(entry**2 for entry in rho)
    integral=sp.integrate(sp.expand(tau_norm-rho_norm/2),(x,0,2*sp.pi),(z,0,2*sp.pi))
    assert sp.simplify(integral)==0
    assert sp.integrate(rho_norm,(x,0,2*sp.pi),(z,0,2*sp.pi))==25*chi**2*sp.pi**2


def test_generic_source_structure_uses_commuting_derivatives_not_wave_samples(model):
    source=model['source'];coords=source['coords']
    assert gate.zero(source['rho']-gate.curl(source['W'],coords))
    assert sp.expand(sum(sp.diff(source['rho'][i],coords[i]) for i in range(3)))==0
    assert source['F'].is_Function and source['U'].is_Function


def test_independent_opposite_Fourier_metric_variation_for_complex_source(model):
    """Differentiate the literal mixed density with the metric at momentum -k."""
    data=model['fourier'];k,r,chi=data['k'],data['rho'],data['chi'];p2=k.dot(k)
    theta=r/(chi*p2)
    Theta=sp.Matrix(3,3,lambda a,b:sum(sp.LeviCivita(I,a,b)*theta[I] for I in range(3)))
    slots={(i,j):sp.Symbol(f'hbar{i}{j}') for i in range(3) for j in range(i,3)}
    h=sp.Matrix(3,3,lambda i,j:slots[tuple(sorted((i,j)))])
    mixed=0
    for i in range(3):
        frame=sp.I*k[i]*h/2
        Gamma=sp.Matrix(3,3,lambda a,b:-sp.I*(k[i]*h[a,b]+k[b]*h[a,i]-k[a]*h[i,b])/2)
        delta_omega=frame+Gamma
        for a in range(3):
            for b in range(3):mixed-=chi*sp.I*k[i]*Theta[a,b]*delta_omega[a,b]/2
    tau=sp.zeros(3)
    for (i,j),field in slots.items():
        tau[i,j]=tau[j,i]=sp.cancel((2 if i==j else 1)*sp.diff(mixed,field))
    assert gate.zero(tau-data['tau'])
    assert not gate.zero(tau+data['tau'])


def test_complex_Hermitian_norm_and_Ward_on_rotated_momentum(model):
    data=model['fourier'];k=sp.Matrix([2,-1,3])
    r=sp.Matrix([1+2*sp.I,-3+sp.I,4-2*sp.I]);p2=k.dot(k)
    P=sp.eye(3)-k*k.T/p2
    for source in (r,P*r):
        tau=gate.fourier_feedback(k,source)
        norm=sum(sp.conjugate(v)*v for v in tau)
        norm_source=sum(sp.conjugate(v)*v for v in source)
        dot=k.dot(source)
        expected=(norm_source-sp.conjugate(dot)*dot/p2)/2
        assert sp.simplify(norm-expected)==0
        assert gate.zero(tau*k+k.cross(source)/2)
        assert gate.zero(P*tau*P) and sp.trace(tau)==0
    transverse=P*r;tau=gate.fourier_feedback(k,transverse)
    assert sp.simplify(sum(sp.conjugate(v)*v for v in tau)-sum(sp.conjugate(v)*v for v in transverse)/2)==0
    assert sp.simplify(sum(v*v for v in tau)-sum(sp.conjugate(v)*v for v in tau))!=0


def test_nontransverse_source_cannot_use_half_full_norm(model):
    k=sp.Matrix([1,2,3]);rho=(1+2*sp.I)*k
    tau=gate.fourier_feedback(k,rho)
    assert tau==sp.zeros(3)
    assert sp.simplify(sum(sp.conjugate(v)*v for v in rho))==70
    assert sum(sp.conjugate(v)*v for v in tau)!=sum(sp.conjugate(v)*v for v in rho)/2


def test_static_projection_bound_allows_orthogonal_metric_response(model):
    k=sp.Matrix([1,2,3]);p2=k.dot(k);P=sp.eye(3)-k*k.T/p2
    rho=k.cross(sp.Matrix([1+sp.I,2-sp.I,-1+3*sp.I]))
    tau=gate.fourier_feedback(k,rho)
    arbitrary=sp.Matrix([[1+sp.I,2,3*sp.I],[2,-1+2*sp.I,4],[3*sp.I,4,3-sp.I]])
    extra=P*arbitrary*P;S=tau+extra
    projection=(k*(P*S*k).T+(P*S*k)*k.T)/p2
    assert gate.zero(S*k+k.cross(rho)/2)
    assert gate.zero(projection-tau)
    normS=sp.simplify(sum(sp.conjugate(v)*v for v in S))
    normTau=sp.simplify(sum(sp.conjugate(v)*v for v in tau))
    normExtra=sp.simplify(sum(sp.conjugate(v)*v for v in extra))
    assert sp.simplify(normS-normTau-normExtra)==0 and normExtra>0
    assert sp.simplify(normTau-sum(sp.conjugate(v)*v for v in rho)/2)==0
    # A longitudinal addition does not satisfy the same complete Ward row.
    assert not gate.zero((S+k*k.T)*k+k.cross(rho)/2)


def test_generic_complex_projection_is_idempotent_and_orthogonal(model):
    data=model['static_projection']
    assert gate.zero(data['residuals']['projector_idempotence_polynomial'])
    assert data['residuals']['Hermitian_vector_complement_orthogonality']==0
    assert gate.zero(data['projection_from_Ward']-model['fourier']['tau'])
    assert any('Simag' in str(x) for x in data['tensor'])


def test_clock_and_explicit_stress_order_do_not_remove_metric_adjoint(model):
    local=model['local']
    assert local['V']==sp.zeros(3,1)
    assert local['literal_action_coefficient_four']!=0
    assert local['mixed_density']!=0 and local['tau_literal']!=sp.zeros(3)
    assert not gate.zero(local['negative']['mistake_action_order_four_for_metric_order_four'])


def test_recomputed_receipt_preserves_contribution_and_scope(payload):
    assert gate.validate_payload(payload)==payload
    assert payload['decision']['actual_port_source_has_exact_chi_independent_half_squared_norm'] is True
    assert payload['decision']['conditional_static_connection_contribution_has_half_squared_norm_lower_bound'] is True
    assert payload['decision']['complete_second_order_Einstein_embedding_solution'] is False


@pytest.mark.parametrize('mutation',('metric_sign','metric_half','energy','action_order','double_count','full_theory'))
def test_resigned_receipt_mutants_against_fresh_trusted_fixture(payload,monkeypatch,mutation):
    """Receipt comparison layer; the fixture came from an actual fresh derivation."""
    trusted=deepcopy(payload);monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(trusted))
    changed=deepcopy(payload)
    if mutation in ('metric_sign','metric_half'):
        changed['Fourier']['tau'][0][1]=('-1*' if mutation=='metric_sign' else '1/2*')+'('+changed['Fourier']['tau'][0][1]+')'
    else:
        keys={'energy':'spatial_tensor_norm_is_total_physical_energy',
              'action_order':'quartic_action_value_implies_no_quadratic_metric_feedback',
              'double_count':'unknown_linear_H18_connection_operator_should_be_added_twice',
              'full_theory':'full_N7'}
        changed['decision'][keys[mutation]]=True
    changed.pop('calculation_digest');changed['calculation_digest']=gate.digest(changed)
    with pytest.raises(gate.MetricFeedbackError,match='fresh source-bound'):
        gate.validate_payload(changed)


def test_changed_note_and_rebound_source_are_rejected(tmp_path):
    changed=tmp_path/'note.md';changed.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.MetricFeedbackError,match='lemma hash'):
        gate.load_sources(note=changed)
    stem=next(iter(gate.SOURCE_PINS));path=gate.HERE/'artifacts'/(stem+'.json')
    doc=gate.read_json(path.read_bytes());doc['claim_not_present_in_source']=True
    doc.pop('calculation_digest');doc['calculation_digest']=gate.digest(doc)
    (tmp_path/path.name).write_text(__import__('json').dumps(doc))
    with pytest.raises(gate.MetricFeedbackError,match='source byte hash'):
        gate.load_sources(artifact_directory=tmp_path)


def test_receipt_and_json_type_errors_are_explicit():
    for value in ('{"x":1,"x":2}','{"x":NaN}','[]'):
        with pytest.raises(gate.MetricFeedbackError):gate.read_json(value)
    with pytest.raises(gate.MetricFeedbackError,match='must be object'):gate.validate_payload(None)
    with pytest.raises(gate.MetricFeedbackError,match='digest'):gate.validate_payload({'schema':gate.SCHEMA})
