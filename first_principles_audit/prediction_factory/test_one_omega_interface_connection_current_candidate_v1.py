"""Current orientation, independent quadratic variation and limited-energy tests."""
import copy
import hashlib
import pytest
import sympy as sp
from . import verify_one_omega_interface_connection_current_candidate_v1 as oracle


@pytest.fixture(scope='module')
def model():
    return oracle.derive_model()


def test_Hodge_current_sign_for_time_and_each_space_direction():
    c0,c1,c2,c3,chi=sp.symbols('c0 c1 c2 c3 chi',real=True)
    actual={k:chi*v for k,v in oracle.star_one([c0,c1,c2,c3],sp.diag(-1,1,1,1),1).items()}
    expected={(1,2,3):-chi*c0,(0,2,3):-chi*c1,(0,1,3):chi*c2,(0,1,2):-chi*c3}
    assert actual==expected
    d0,d1,d2,d3=sp.symbols('d0 d1 d2 d3',real=True)
    paired=oracle.wedge(actual,{(0,):d0,(1,):d1,(2,):d2,(3,):d3})[(0,1,2,3)]
    assert sp.expand(paired-chi*(c0*d0-c1*d1-c2*d2-c3*d3))==0


def test_non_diagonal_metric_current_matches_exact_finite_variation():
    gamma=sp.Matrix([[-1,sp.Rational(1,2),0,0],[sp.Rational(1,2),1,0,0],
                     [0,0,2,sp.Rational(1,3)],[0,0,sp.Rational(1,3),1]])
    inverse=gamma.inv(); volume=sp.sqrt(-gamma.det()); chi=sp.Rational(3,7)
    C=[sp.Matrix([sp.Rational((color+2)*(mu+1)-3,mu+4) for mu in range(4)]) for color in range(3)]
    direction=[sp.Matrix([sp.Rational((-1)**mu*(color+mu+1),color+5) for mu in range(4)]) for color in range(3)]
    def action(step):
        return -chi*volume*sum(((v+step*d).T*inverse*(v+step*d))[0] for v,d in zip(C,direction))/2
    h=sp.Rational(2,9)
    # Exactly quadratic, so this central finite difference is exact at any nonzero h.
    finite=(action(h)-action(-h))/(2*h)
    paired=0
    for v,d in zip(C,direction):
        J={key:chi*value for key,value in oracle.star_one(v,inverse,volume).items()}
        # Explicit oriented 3+1 pairing, independent of the production wedge helper.
        paired+=-J[1,2,3]*d[0]+J[0,2,3]*d[1]-J[0,1,3]*d[2]+J[0,1,2]*d[3]
    assert sp.simplify(finite-paired)==0
    assert finite!=0


def test_covariant_compatibility_retains_all_three_equation_rows(model):
    row=model['compatibility']; symbols={str(s):s for s in row.free_symbols}
    assert sp.expand(row)==symbols['D_J_Sigma']+symbols['j4_plus']-symbols['j4_minus']
    assert row.subs({symbols['D_J_Sigma']:2,symbols['j4_plus']:3,symbols['j4_minus']:5})==0
    assert row.subs({symbols['D_J_Sigma']:-2,symbols['j4_plus']:3,symbols['j4_minus']:5})==-4
    assert model['residuals']['current_sign_from_independent_density_variation']==0
    assert model['negative_controls']['wrong_current_sign']!=0


def test_curvature_only_current_needs_flat_field_not_just_one_flat_point(model):
    sy=model['symbols']; first=model['curvature_squared_first_variation']
    assert first.subs({f:0 for f in sy['F'].values()})==0
    EL=model['curvature_squared_principal_EL']
    assert EL.subs({jet:0 for jet in sy['F_jets'].values()})==sp.zeros(4,1)
    point={jet:0 for jet in sy['F_jets'].values()}; point[sy['F_jets'][0,0,1]]=1
    assert EL.subs(point)!=sp.zeros(4,1)
    # F=0 at just a point does not force its first jets to vanish.
    assert EL.subs({f:0 for f in sy['F'].values()})==EL


def test_flat_theta_channel_has_three_positive_kinetic_and_twelve_energy_slots(model):
    sy=model['symbols']; chi=sy['chi']; v=sy['theta_jets']
    assert model['flat_theta_momenta']==sp.Matrix([chi*t[0] for t in v])
    assert model['flat_theta_kinetic']==chi*sp.eye(3)
    assert model['flat_theta_energy_hessian']==chi*sp.eye(12)
    assert sp.expand(model['flat_theta_energy']-chi*sum(t.dot(t) for t in v)/2)==0
    assert model['negative_controls']['negative_chi_gives_negative_kinetic'][0,0].is_negative is True


def test_geometric_connection_mixing_is_present_in_the_candidate_quadratic_action(model):
    chi=model['symbols']['chi']
    assert model['geometry_mixing']==sp.diag(chi,-chi,-chi,-chi)
    assert model['geometry_mixing'].det()==-chi**4
    assert model['negative_controls']['freeze_geometry_connection_in_quadratic_action']!=sp.zeros(4)


def test_static_two_direction_source_has_the_required_response_sign(model):
    sy=model['symbols']; x,z,J0,chi=(sy[k] for k in ('x','z','J0','chi'))
    theta=model['static_theta_solution']
    expected=-J0*sp.sin(x)*sp.sin(2*z)/(chi*(1**2+2**2))
    assert sp.expand(theta-expected)==0
    assert sp.expand(chi*(sp.diff(theta,x,2)+sp.diff(theta,z,2))-model['static_source'])==0
    assert model['static_current_divergence'].subs({x:sp.pi/2,z:sp.pi/4})==-J0
    bad=model['negative_controls']['wrong_static_response_sign']
    assert bad.subs({x:sp.pi/2,z:sp.pi/4})==2*J0
    # The illustrative positive orientation J0=4/5 is allowed, not selected globally.
    assert theta.subs({x:sp.pi/2,z:sp.pi/4,J0:sp.Rational(4,5)})==-sp.Rational(4,25)/chi


def test_static_cell_energy_by_fourier_orthogonality(model):
    sy=model['symbols']; J0,chi=sy['J0'],sy['chi']; amplitude=-J0/(5*chi)
    # Each integral sin² or cos² over a 2pi cell equals pi.
    independent=chi*amplitude**2*(1**2+2**2)*sp.pi**2/2
    assert sp.simplify(model['static_cell_energy']-independent)==0
    assert independent.is_nonnegative is True


@pytest.fixture(scope='module')
def payload():
    return oracle.build_payload()


@pytest.mark.parametrize('mutation',['adoption','coupled_energy','current_sign','static_sign'])
def test_resigned_receipt_cannot_adopt_candidate_or_change_its_math(payload,mutation):
    changed=copy.deepcopy(payload)
    if mutation=='adoption': changed['proposal']['adopted_into_v5_2']=True
    elif mutation=='coupled_energy': changed['decision']['complete_gravitational_khronon_energy_positive']=True
    elif mutation=='current_sign': changed['model']['residuals']['current_sign_from_independent_density_variation']='1'
    else: changed['model']['static_theta_solution']='-('+changed['model']['static_theta_solution']+')'
    changed['calculation_digest']=oracle.canonical_digest({k:v for k,v in changed.items() if k!='calculation_digest'})
    with pytest.raises(oracle.ConnectionCandidateError,match='fresh derivation'):
        oracle.validate_payload(changed)


def test_baseline_is_byte_pinned_and_no_chi_or_general_gate_is_selected(payload):
    assert hashlib.sha256(oracle.SOURCE.read_bytes()).hexdigest()==oracle.SOURCE_SHA
    assert payload['baseline']['literal_action_sha256']==oracle.ACTION_SHA
    assert payload['proposal']['A_Sigma_remains_independent'] is True
    assert payload['proposal']['adopted_into_v5_2'] is False
    assert all(payload['decision'][name] is False for name in (
        'candidate_adopted','new_coefficient_selected','complete_model_repair_proved',
        'N4_JUNCTION_BENDING_pass','N7_LINEAR_REDUCTION_pass','P4_full_same_action_pass','B4_pass','B5_pass'))


def test_malformed_or_unresigned_receipt_is_rejected(payload):
    with pytest.raises(oracle.ConnectionCandidateError,match='schema'):
        oracle.validate_payload(None)
    changed=copy.deepcopy(payload); changed['proposal']['chi']='selected 1'
    with pytest.raises(oracle.ConnectionCandidateError,match='digest'):
        oracle.validate_payload(changed)
