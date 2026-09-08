"""Independent material conservation, Lorentz Hodge and static sourced BF tests."""
from copy import deepcopy
import json
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_connection_static_sourced_bf_v1 as gate
else:
    import verify_one_omega_connection_static_sourced_bf_v1 as gate

@pytest.fixture(scope='module')
def model():return gate.derive_model()

@pytest.fixture(scope='module')
def payload():return gate.build_payload()

def test_all_new_identities_and_static_degrees(model):
    assert all(model['checks'].values())
    for part in ('oriented_green','material','exterior','reconstruction','norms'):
        assert all(gate.zero(v) for v in model[part]['residuals'].values())
    assert model['exterior']['basis_count']==32
    assert model['exterior']['time_derivative_zero_but_dt_forms_retained'] is True

def test_material_current_on_nontrivial_exact_harmonic_polynomials(model):
    z,x,y,w=sp.symbols('z x y w',real=True);coords=(z,x,y,w)
    psi=sp.Matrix([x*z,y*z,x*x-z*z])
    first=[psi.diff(c) for c in coords]
    lap=sum((psi.diff(c,2) for c in coords),sp.zeros(3,1))
    assert lap==sp.zeros(3,1)
    Z=model['symbols']['Z'];direct=[Z*psi.cross(v) for v in first]
    assert any(Q!=sp.zeros(3,1) for Q in direct)
    divergence=sum((direct[m].diff(coords[m]) for m in range(4)),sp.zeros(3,1))
    assert divergence.applyfunc(sp.expand)==sp.zeros(3,1)
    m=model['material'];sub=dict(zip(m['psi'],psi))
    for i,c in enumerate(coords):
        sub.update(dict(zip(m['first_jets_order_z_x1_x2_x3'][i],first[i])))
        sub.update(dict(zip(m['second_diagonal_jets'][i],psi.diff(c,2))))
    for actual,expected in zip(m['Q_by_direction'],direct):assert gate.zero(actual.subs(sub)-expected)
    assert gate.zero(m['Euler_from_literal'].subs(sub))

def test_current_is_derived_before_Fourier_transforming_products(model):
    m=model['material'];Z=model['symbols']['Z']
    for direction in range(4):
        P=m['first_jets_order_z_x1_x2_x3'][direction]
        for I,T in enumerate(m['generators']):
            expected=-Z*(P.T*T*m['psi'])[0]
            assert sp.expand(m['Q_by_direction'][direction][I]-expected)==0
    assert model['norms']['analytic_hypotheses'][-1]=='current products transformed after multiplication; no single-mode shortcut'

def test_Robin_normal_incidence_from_independent_cross_product(model):
    c=model['symbols'];m=model['material'];phi=sp.Matrix([1,-2,3]);grad=sp.Matrix([2,1,-1])
    sub=dict(zip(m['phi_UV'],phi));sub.update(dict(zip(m['gradF'],grad)))
    normal=(c['kappa']*phi-c['kappa']*c['y']*grad)/(2*c['Z'])
    jump=2*c['Z']*phi.cross(normal)
    assert gate.zero(jump-c['kappa']*c['y']*grad.cross(phi))
    assert gate.zero(m['rho_from_oriented_trace'].subs(sub)-jump)
    assert not gate.zero(jump)

def test_spatial_h_sign_dt_components_and_unbounded_family():
    c=gate.symbols_context();c['xi']=(2,0,0);c['p2']=4
    assert gate.spatial_h({2:1},c)=={0:-sp.I/2}
    assert gate.spatial_h({3:1},c)=={1:sp.I/2}
    assert gate.plus(gate.static_d(gate.spatial_h({1:1},c),c),gate.spatial_h(gate.static_d({1:1},c),c))=={1:1}
    epsilon=sp.Symbol('epsilon',positive=True);c['xi']=(epsilon,0,0);c['p2']=epsilon**2
    v=gate.spatial_h({2:1},c)[0]
    norm=sp.simplify(sp.conjugate(v)*v)
    assert norm==epsilon**-2
    assert norm.subs(epsilon,sp.Rational(1,2))-1==3
    assert sp.limit(norm,epsilon,0,dir='+')==sp.oo
    c['xi']=(0,0,0);c['p2']=0
    with pytest.raises(gate.StaticSourcedBFError,match='p'):gate.spatial_h({2:1},c)

def test_sourced_particular_solution_against_explicit_radial_source():
    c=gate.symbols_context();z=c['z'];c['xi']=(2,0,0);c['p2']=4
    f=sp.exp(-3*z)
    source={15:f,29:3*sp.I*f/2}
    assert gate.static_d(source,c)=={}
    B=gate.scale(-1,gate.spatial_h(source,c))
    assert B=={13:-sp.I*f/2}
    assert gate.plus(gate.static_d(B,c),source)=={}
    assert gate.plus(gate.static_d(gate.scale(-1,B),c),gate.scale(-1,source))=={}
    assert gate.plus(gate.trace(B,c),gate.scale(-1,gate.trace(gate.scale(-1,B),c)))=={13:-sp.I}
    # Homogeneous B=0 fails the actual sourced equation.
    assert gate.plus(gate.static_d({},c),source)==source

def test_Lorentz_Hodge_by_defining_wedge_pairing():
    for i in range(4):
        for j in range(4):
            got=gate.wedge({1<<i:1},gate.star_one_Lorentz({1<<j:1}))
            expected={15:(-1 if i==0 else 1)} if i==j else {}
            assert got==expected

def test_actual_Poisson_current_has_zero_closed_remainder(model):
    c=model['symbols'];r=model['reconstruction'];rho=c['rho'];p2=c['p2']
    assert r['Theta_hat_actual_port']==rho/(c['chi']*p2)
    assert r['L_actual_port']=={}
    assert gate.plus(r['J_Sigma_actual_port'],gate.scale(-1,gate.spatial_h({15:rho},c)))=={}
    assert gate.plus(gate.static_d(r['J_Sigma_actual_port'],c,boundary=True),{15:-rho})=={}
    assert gate.zero(r['residuals']['actual_B_part_alone_has_required_jump'])

def test_general_closed_correction_and_source_are_both_retained(model):
    c=model['symbols'];r=model['reconstruction'];z=c['z'];uv={c['f'].subs(z,0):1}
    for side,sign in (('plus',1),('minus',-1)):
        B=r['general_B_'+side]
        assert gate.plus(gate.static_d(B,c),gate.scale(sign,r['closed_source_plus']))=={}
    jump=gate.ext.substitute(gate.plus(gate.trace(r['general_B_plus'],c),gate.scale(-1,gate.trace(r['general_B_minus'],c))),uv)
    assert jump==gate.scale(-1,r['general_compatible_boundary_current'])
    assert r['general_closed_boundary_remainder']!={}
    assert any(mask&16 for mask in r['general_cutoff_correction_plus'])

def test_Fourier_radial_moments_independently_integrated(model):
    p=sp.Symbol('p',nonnegative=True)
    for order,rate,expected in ((4,2,sp.Rational(3,4)),(6,2,sp.Rational(45,8)),(3,1,6)):
        direct=sp.integrate(p**order*sp.exp(-rate*p),(p,0,sp.oo))
        assert direct==expected
        expr=model['norms']['laplace_moments'][order]
        sub={x:(rate if str(x)=='positive_rate' else 1) for x in expr.free_symbols}
        assert expr.subs(sub)==expected

def test_integrated_norm_exponents_and_IR_split(model):
    n=model['norms'];powers=n['radial_decay_powers']
    assert powers['psi_L2']==sp.Rational(5,2)
    assert powers['derivative_psi_L2']==sp.Rational(7,2)
    assert powers['psi_Linfinity']==4
    assert powers['J4_L1']==6 and powers['J4_L2']==sp.Rational(15,2)
    assert powers['weighted_B_integrand_decay_power']==11
    assert powers['weighted_dB_integrand_decay_power']==12
    assert n['weighted_radial_integrability']=={'B':True,'dB':True}
    assert n['low_frequency_integral_p_minus_two_R3']==4*sp.pi
    assert 'no pullback to t=constant' in n['auxiliary_norm_convention']

def test_form_weights_by_independent_conformal_inverse_metric(model):
    O=model['symbols']['Omega'];inverse=sp.diag(*([O**-2]*5));volume=O**5
    for row in model['norms']['form_component_weights']:
        indices=[i for i in range(5) if row['mask']&(1<<i)]
        independent=volume*sp.prod(inverse[i,i] for i in indices)
        assert sp.cancel(independent-row['weight'])==0
        assert sp.cancel(row['weight']-O**(-1 if row['degree']==3 else -3))==0

def test_negative_controls_and_no_gravity_or_static_uniqueness_claim(model):
    assert len(model['negative_controls'])==9 and all(model['negative_controls'].values())
    positive={'prescribed_port_order_two_sourced_BF_constructed','actual_port_requires_no_closed_cutoff_correction',
              'material_current_conservation_from_harmonic_EL','spatial_and_radial_auxiliary_graph_integrability_conditional'}
    for name,value in model['decision'].items():assert value is (name in positive)

def test_old_Poisson_and_jump_sign_fail_core_Stokes_row(model):
    c=model['symbols'];r=model['reconstruction'];green=gate.current_core.derive_oriented_bf_green()
    assert green['boundary_jump_coefficient']==1
    assert green['required_B_jump_coefficient']==-1
    assert green['compatibility_current_coefficient']==1
    symbols=green['symbols'];component_row=green['component_oracle']['combined_interface_row']
    assert sp.expand(component_row.subs(symbols['bp'],symbols['bm']-symbols['J']))==0
    assert sp.expand(component_row.subs(symbols['bp'],symbols['bm']+symbols['J']))==-2*symbols['J']
    current=r['actual_current_for_general_closed_source']
    correct_row=gate.plus(gate.scale(green['boundary_jump_coefficient'],r['actual_particular_jump']),current)
    old_row=gate.plus(gate.scale(green['boundary_jump_coefficient'],r['actual_particular_jump']),gate.scale(-1,current))
    assert correct_row=={}
    assert old_row==gate.scale(-2,current) and old_row!={}
    old_theta=-r['Theta_hat_actual_port']
    assert sp.cancel(-c['chi']*c['p2']*old_theta+c['rho'])==2*c['rho']

@pytest.mark.parametrize('mutation',['Einstein','global_static_uniqueness','particular_sign','old_Poisson_sign'])
def test_rehashed_mutant_rejected_by_fresh_derivation(payload,model,mutation):
    bad=deepcopy(payload)
    if mutation=='Einstein':bad['decision']['Einstein_or_embedding_equations_solved']=True
    elif mutation=='global_static_uniqueness':bad['decision']['uniqueness_for_all_static_weighted_BF_fields']=True
    elif mutation=='particular_sign':bad['model']['reconstruction']['B_part_plus']={}
    else:bad['model']['reconstruction']['Theta_hat_actual_port']=gate.ext._serialize(-model['reconstruction']['Theta_hat_actual_port'])
    bad['calculation_digest']=gate.canonical_digest({k:v for k,v in bad.items() if k!='calculation_digest'})
    with pytest.raises(gate.StaticSourcedBFError,match='fresh derivation'):gate.validate_payload(bad)

def test_backend_and_torque_source_pins_reject_rebinding(tmp_path):
    backend=tmp_path/'backend.py';backend.write_bytes(gate.BACKEND.read_bytes()+b'\n')
    with pytest.raises(gate.StaticSourcedBFError,match='exterior_backend byte hash'):gate.load_sources(backend_path=backend)
    torque=json.loads(gate.TORQUE.read_bytes());torque['invented']=True;torque['calculation_digest']=gate.canonical_digest(torque)
    p=tmp_path/'torque.json';p.write_text(json.dumps(torque))
    with pytest.raises(gate.StaticSourcedBFError,match='localized_torque byte hash'):gate.load_sources(torque_path=p)
    core=tmp_path/'core.py';core.write_bytes(gate.CORE.read_bytes()+b'\n')
    with pytest.raises(gate.StaticSourcedBFError,match='oriented_Stokes_core byte hash'):gate.load_sources(core_path=core)

def test_CLI_write_is_exclusive(tmp_path,monkeypatch,payload):
    monkeypatch.setattr(gate,'build_payload',lambda:deepcopy(payload))
    p=tmp_path/'receipt.json';gate.main(['--write',str(p)]);before=p.read_bytes()
    with pytest.raises(FileExistsError):gate.main(['--write',str(p)])
    assert p.read_bytes()==before
