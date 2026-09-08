"""Independent coordinate/triad, Hodge and restricted-response checks."""
from copy import deepcopy
import json
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_projected_connection_linear_v1 as gate
else:
    import verify_one_omega_projected_connection_linear_v1 as gate

@pytest.fixture(scope='module')
def model():return gate.derive_model()

@pytest.fixture(scope='module')
def payload():return gate.build_payload()

def test_all_local_geometric_and_quadratic_residuals(model):
    assert all(model['checks'].values())
    for name in ('geometry','quadratic','vector_algebra'):
        assert all(gate.zero(x) for x in model[name]['residuals'].values())
    assert len(model['geometry']['omega'])==4
    assert all(x.shape==(3,3) for x in model['geometry']['omega'])

def test_coordinate_dependent_metric_and_clock_direct_Koszul_first_variation(model):
    # Independent coordinate polynomials, rather than the verifier's jet labels.
    t,x,y,z,e=sp.symbols('t x y z eps',real=True);coords=(t,x,y,z)
    eta=sp.diag(-1,1,1,1)
    n=2*t-3*x+y+z
    shift=sp.Matrix([t+2*y-z,3*t-x+2*z,-t+3*x-y])
    H=sp.Matrix([[2*t+x,3*t-y+z,-t+x+2*z],
                 [3*t-y+z,t-2*y,2*t+x-z],[-t+x+2*z,2*t+x-z,-t+y+3*z]])
    tau=t*x+2*y*z+t*t/3+x*x/2
    h=sp.zeros(4);h[0,0]=-2*n;h[1:4,1:4]=H
    for i in range(3):h[0,i+1]=h[i+1,0]=shift[i]
    E=sp.zeros(4,3);E[1:4,0:3]=sp.eye(3)-e*H/2
    for a in range(3):E[0,a]=-e*sp.diff(tau,coords[a+1])
    metric=eta+e*h
    ctx=model['symbols'];sub={}
    for mu in range(4):
        sub[ctx['n_gradient'][mu]]=sp.diff(n,coords[mu])
        for i in range(3):sub[ctx['shift_gradient'][mu][i]]=sp.diff(shift[i],coords[mu])
        for i in range(3):
            for j in range(i,3):sub[ctx['H_gradient'][mu][i,j]]=sp.diff(H[i,j],coords[mu])
    # Lowered Christoffel uses only derivatives of the metric. Its contraction
    # E^a E^b Gamma_lower avoids sharing the verifier's raised-index formula.
    for mu in range(4):
        lowered=sp.Matrix(4,4,lambda nu,rho:(sp.diff(metric[nu,rho],coords[mu])
            +sp.diff(metric[nu,mu],coords[rho])-sp.diff(metric[mu,rho],coords[nu]))/2)
        literal=E.T*metric*E.diff(coords[mu])+E.T*lowered*E
        actual=literal.applyfunc(lambda v:sp.expand(sp.diff(v,e).subs(e,0)))
        assert gate.zero(actual-model['geometry']['omega'][mu].subs(sub))

def test_exact_diagonal_time_dependent_triad_has_no_rotational_velocity(model):
    t=sp.Symbol('t',real=True);a=sp.Matrix([sp.exp(t),sp.exp(2*t),sp.exp(-3*t)])
    spatial=sp.diag(*[v*v for v in a]);frame=sp.diag(*[1/v for v in a])
    Gamma_t=sp.diag(*[sp.diff(v,t)/v for v in a])
    direct=frame.T*spatial*(frame.diff(t)+Gamma_t*frame)
    assert direct==sp.zeros(3)
    omega=model['geometry']['omega']
    forbidden=set(model['geometry']['excluded_time_symbols'])
    assert not set.union(*(w.free_symbols for w in omega)).intersection(forbidden)
    assert not gate.zero(model['negative_witnesses']['freeze_horizontal_frame'])

def test_exact_conformal_spatial_connection_from_Christoffel(model):
    t,x,y,z=sp.symbols('t x y z',real=True);coords=(t,x,y,z)
    u=x+2*y-3*z;scale=sp.exp(u)
    metric=sp.diag(-1,scale**2,scale**2,scale**2)
    frame=sp.zeros(4,3);frame[1:4,0:3]=sp.eye(3)/scale
    for mu in range(4):
        lowered=sp.Matrix(4,4,lambda nu,rho:(sp.diff(metric[nu,rho],coords[mu])
            +sp.diff(metric[nu,mu],coords[rho])-sp.diff(metric[mu,rho],coords[nu]))/2)
        actual=(frame.T*metric*frame.diff(coords[mu])+frame.T*lowered*frame).applyfunc(sp.simplify)
        expected=sp.Matrix(3,3,lambda a,b:0 if mu==0 else
            (int(mu==a+1)*sp.diff(u,coords[b+1])-int(mu==b+1)*sp.diff(u,coords[a+1])))
        assert actual==expected
    assert model['quadratic']['scalar_slice']==-model['symbols']['chi']*model['symbols']['zeta_z']**2

def test_tau_tilt_is_in_frame_and_cancels_from_all_connection_entries(model):
    ctx=model['symbols'];g=model['geometry']
    for a in range(3):assert g['frame_first_jet'][0,a]==-ctx['tau_gradient'][a+1]
    assert g['clock_lapse_first_jet']==ctx['n']-ctx['tau_gradient'][0]
    forbidden=set(g['excluded_clock_symbols']+g['excluded_lapse_symbols'])
    for w in g['omega']:assert not w.free_symbols.intersection(forbidden)
    # Independently: the clock-induced shift is a gradient, hence its curl zero.
    t,x,y,z=sp.symbols('t x y z');tau=t*x*y+x*x*z+z*z*y
    spatial=(x,y,z)
    for a in range(3):
        for b in range(3):assert sp.diff(tau,spatial[a],spatial[b])-sp.diff(tau,spatial[b],spatial[a])==0

def test_exact_local_frame_rotation_sets_inhomogeneous_sign(model):
    t,z=sp.symbols('t z',real=True);angle=2*t-3*z
    R=sp.Matrix([[sp.cos(angle),-sp.sin(angle),0],[sp.sin(angle),sp.cos(angle),0],[0,0,1]])
    generator=sp.Matrix([[0,-1,0],[1,0,0],[0,0,0]])
    for coord in (t,z):
        actual=(R.T*R.diff(coord)).applyfunc(sp.trigsimp)
        assert actual==sp.diff(angle,coord)*generator
    g=model['geometry'];ctx=model['symbols']
    for mu in range(4):
        assert gate.zero(g['omega_rotated'][mu]-g['omega'][mu]-ctx['rho_gradient'][mu])
        assert gate.zero(g['C_rotated'][mu]-g['C'][mu])
    assert not gate.zero(model['negative_witnesses']['rotate_frame_without_A'])

def test_SO3_Frobenius_and_Lorentz_Hodge_normalizations(model):
    ctx=model['symbols'];g=model['geometry'];L=model['quadratic']['L_C2']
    amplitude=sp.Symbol('amplitude',real=True)
    sub={v:0 for w in g['omega'] for v in w.free_symbols}
    sub.update({v:0 for A in ctx['A'] for v in A.free_symbols})
    electric=L.subs({**sub,ctx['A'][0][0,1]:amplitude},simultaneous=True)
    spatial=L.subs({**sub,ctx['A'][2][0,1]:amplitude},simultaneous=True)
    assert electric==ctx['chi']*amplitude**2/2
    assert spatial==-ctx['chi']*amplitude**2/2
    J=sp.Matrix([[0,1,0],[-1,0,0],[0,0,0]])
    assert sp.trace(J.T*J)==2 and gate.inner(J,J)==1

def test_TT_has_two_distinct_connection_entries_and_no_elastic_contact(model):
    ctx=model['symbols'];w=model['quadratic']['TT_omega'];hz=ctx['h_z']
    assert w[1][1,2]==hz/2 and w[2][0,2]==hz/2
    assert w[0]==sp.zeros(3) and w[3]==sp.zeros(3)
    norm=sum(sp.trace(x.T*x)/2 for x in w[1:])
    assert norm==hz*hz/2
    assert model['quadratic']['TT_slice']==-ctx['chi']*hz*hz/4
    assert model['quadratic']['TT_slice'].free_symbols=={ctx['chi'],hz}

def test_scalar_trace_and_longitudinal_connection_do_not_mix_in_declared_slice(model):
    ctx=model['symbols'];quad=model['quadratic'];w=quad['scalar_omega'];zz=ctx['zeta_z']
    assert w[1][0,2]==zz and w[2][1,2]==zz
    L=quad['scalar_with_longitudinal_connection_slice']
    assert sp.diff(L,zz,ctx['theta_t'])==0 and sp.diff(L,zz,ctx['theta_z'])==0
    assert sp.diff(L,zz,2)==-2*ctx['chi']
    assert model['scope']['full_scalar_pivots_rederived'] is False

def test_vector_shift_curl_factor_and_completion_of_square(model):
    ctx=model['symbols'];v=model['vector_algebra'];q,B,chi,N=(ctx[k] for k in ('q','B','chi','N_mode'))
    residual=sp.cancel(v['total_density']-v['reduced_density']-v['N_pivot']*(N-v['N_stationary'])**2/2)
    assert residual==0
    assert sp.cancel(v['N_pivot']-q*q*(2*B+chi)/4)==0
    assert sp.cancel(v['K_eff']-2*chi*B/(2*B+chi))==0
    # Independent rational complex test: no positivity of an arbitrary B assumed.
    value={q:2,B:sp.Rational(3,2)+sp.I/3,chi:sp.Rational(5,4),ctx['theta_t']:3,ctx['theta']:2}
    assert sp.cancel(v['N_Euler'].subs(N,v['N_stationary']).subs(value))==0
    assert v['kernel_regular_or_positive_real_proved'] is False

def test_vector_before_gauge_fixing_and_compensated_spatial_diffeomorphism(model):
    c=model['symbols'];q=model['quadratic'];v=model['vector_algebra']
    L=q['vector_full_slice']
    expected=c['chi']*((c['theta_t']-c['N_z']/2)**2-(c['theta_z']-c['vector_H_z']/2)**2)/2
    assert sp.expand(L-expected)==0
    assert sp.diff(L,c['vector_H_t'])==0
    a,b=sp.symbols('gauge_tz gauge_zz')
    moved=v['full_vector_density_before_gauge_choice'].subs({
        c['N_z']:c['N_z']+a,c['vector_H_t']:c['vector_H_t']+a,
        c['theta_t']:c['theta_t']+a/2,c['vector_H_z']:c['vector_H_z']+b,
        c['theta_z']:c['theta_z']+b/2},simultaneous=True)
    assert sp.expand(moved-v['full_vector_density_before_gauge_choice'])==0
    assert not v['gauge_invariant_density'].has(c['vector_H_t'],c['vector_H_z'])

def test_negative_controls_and_no_theory_promotion(model):
    assert len(model['negative_controls'])==8
    assert all(model['negative_controls'].values())
    for key,value in model['scope'].items():
        if key not in ('proposed_extension_not_in_v5_2','linear_dynamic_projected_connection_derived',
                       'restricted_C_squared_densities_derived','vector_stationary_elimination_algebra_checked'):
            assert value is False

@pytest.mark.parametrize('mutation',['claim_poles','TT_factor','connection_tau'])
def test_rehashed_mutants_rejected_by_fresh_recomputation(payload,mutation):
    bad=deepcopy(payload)
    if mutation=='claim_poles':bad['decision']['kernel_positive_real_or_pole_exclusion_proved']=True
    elif mutation=='TT_factor':bad['model']['quadratic']['TT_slice']='-chi*h_z**2/8'
    else:bad['model']['geometry']['omega'][0][0][1]='tau_dd_12'
    bad['calculation_digest']=gate.canonical_digest({k:v for k,v in bad.items() if k!='calculation_digest'})
    with pytest.raises(gate.ProjectedConnectionError,match='fresh derivation'):gate.validate_payload(bad)

def test_note_and_candidate_hash_pins_are_not_rebound(tmp_path):
    note=tmp_path/'note.md';note.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.ProjectedConnectionError,match='note byte hash'):gate.load_sources(note_path=note)
    source=json.loads(gate.CANDIDATE.read_bytes());source['exact_classical_charter']['exact_action']['C_squared']='invented'
    source['calculation_digest']=gate.canonical_digest(source)
    path=tmp_path/'source.json';path.write_text(json.dumps(source))
    with pytest.raises(gate.ProjectedConnectionError,match='candidate byte hash'):gate.load_sources(candidate_path=path)

def test_receipt_cli_write_is_exclusive(tmp_path,monkeypatch,payload):
    monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(payload))
    p=tmp_path/'receipt.json';gate.main(['--write',str(p)]);old=p.read_bytes()
    with pytest.raises(FileExistsError):gate.main(['--write',str(p)])
    assert p.read_bytes()==old
