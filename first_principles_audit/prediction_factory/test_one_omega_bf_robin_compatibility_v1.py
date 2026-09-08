"""Independent flux, SO3, half-line energy and second-order obstruction checks."""
from copy import deepcopy
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_bf_robin_compatibility_v1 as gate
else:
    import verify_one_omega_bf_robin_compatibility_v1 as gate

@pytest.fixture(scope='module')
def current():return gate.derive_current()

@pytest.fixture(scope='module')
def payload():return gate.build_payload()


def test_explicit_SO3_generators_match_cross_product_convention(current):
    explicit=(sp.Matrix([[0,0,0],[0,0,1],[0,-1,0]]),
              sp.Matrix([[0,0,-1],[0,0,0],[1,0,0]]),
              sp.Matrix([[0,1,0],[-1,0,0],[0,0,0]]))
    assert current['T']==explicit
    a,p=current['a'],current['phi']
    independently=sp.Matrix([a[1]*p[2]-a[2]*p[1],a[2]*p[0]-a[0]*p[2],a[0]*p[1]-a[1]*p[0]])
    assert gate.zero(sp.Matrix([a.dot(t*p) for t in explicit])-independently)


def test_current_is_direct_internal_rotation_torque(current):
    p,Pi=current['phi'],current['Pi']
    assert gate.zero(current['outgoing']-p.cross(Pi))
    # The common trace, not equality of the two normal derivatives, is needed.
    diff=sp.Matrix(sp.symbols('free1:4'))
    k,y=current['kappa'],current['y']
    total=-k*(p-y*current['a'])
    pplus=total/2+diff;pminus=total/2-diff
    raw=p.cross(pplus)+p.cross(pminus)
    assert gate.zero(raw-current['robin'])
    assert not gate.zero(raw)


def test_common_frame_cannot_remove_nonzero_alignment_norm(current):
    R=sp.Matrix([[1,0,0],[0,sp.Rational(3,5),-sp.Rational(4,5)],
                 [0,sp.Rational(4,5),sp.Rational(3,5)]])*sp.Matrix([[0,-1,0],[1,0,0],[0,0,1]])
    assert R.T*R==sp.eye(3) and R.det()==1
    a,p=current['a'],current['phi']
    assert gate.zero((R*a).cross(R*p)-R*a.cross(p))
    assert gate.zero(((R*a).cross(R*p)).dot((R*a).cross(R*p))-current['norm'])
    point={a[0]:1,a[1]:0,a[2]:0,p[0]:0,p[1]:1,p[2]:0}
    assert current['norm'].subs(point)==1


def test_passive_frame_Ward_does_not_create_A_current(current):
    e=sp.Symbol('epsilon');r=sp.Matrix([[0,1,-2],[-1,0,3],[2,-3,0]])
    p,a,k,y=current['phi'],current['a'],current['kappa'],current['y']
    # Simultaneously change components of both geometric vectors.
    moved=(p-e*r*p)-y*(a-e*r*a)
    L=-k*moved.dot(moved)/2
    assert sp.expand(sp.diff(L,e).subs(e,0))==0
    connection=sp.symbols('A0:3')
    assert all(sp.diff(L,A)==0 for A in connection)
    assert not gate.zero(current['robin'])


def test_alignment_requires_nonzero_kappa_y(current):
    assert gate.zero(current['robin'].subs(current['kappa'],0))
    assert gate.zero(current['robin'].subs(current['y'],0))
    assert not gate.zero(current['robin'])


def test_full_V4_material_port_from_independent_half_line_energy():
    r,p,Z,kappa,y,c,a=sp.symbols('r p Z kappa y c a',positive=True)
    profile=c*sp.exp(-p*r)
    # Both identical bulk sides and one Robin wall, counted exactly once.
    energy=2*sp.integrate(Z*(sp.diff(profile,r)**2+p*p*profile*profile)/2,(r,0,sp.oo))+kappa*(c-y*a)**2/2
    stationarity=sp.diff(energy,c)
    solution=kappa*y*a/(kappa+2*Z*p)
    assert sp.cancel(stationarity.subs(c,solution))==0
    assert sp.diff(energy,c,2)==kappa+2*Z*p
    assert not sp.cancel(stationarity.subs(c,kappa*y*a/(kappa+4*Z*p)))==0


def test_two_mode_source_and_response_directly_solve_bulk_and_Robin():
    x,z,r=sp.symbols('x z r',real=True);y=sp.sqrt(3)
    a=sp.Matrix([-sp.sin(x),0,-2*sp.sin(2*z)])
    bulk=sp.Matrix([-y*sp.sin(x)*sp.exp(-r)/3,0,-2*y*sp.sin(2*z)*sp.exp(-2*r)/5])
    for component in bulk:
        assert sp.simplify(sp.diff(component,r,2)+sp.diff(component,x,2)+sp.diff(component,z,2))==0
    phi=bulk.subs(r,0)
    assert gate.zero(-2*bulk.diff(r).subs(r,0)+phi-y*a)
    cross=sp.Matrix([a[1]*phi[2]-a[2]*phi[1],a[2]*phi[0]-a[0]*phi[2],a[0]*phi[1]-a[1]*phi[0]])
    assert gate.zero(cross-sp.Matrix([0,4*y*sp.sin(x)*sp.sin(2*z)/15,0]))
    residual=-y*cross.subs({x:sp.pi/2,z:sp.pi/4})
    assert residual==sp.Matrix([0,-sp.Rational(4,5),0])


def test_arbitrary_second_order_corrections_cannot_repair_vacuum_witness():
    e=sp.Symbol('e')
    A=sp.Matrix([-1,0,-2]);P=sp.sqrt(3)*sp.Matrix([-sp.Rational(1,3),0,-sp.Rational(2,5)])
    A2=sp.Matrix(sp.symbols('A2_1:4'));P2=sp.Matrix(sp.symbols('P2_1:4'))
    actual=(e*A+e*e*A2/2).cross(e*P+e*e*P2/2)
    coefficient=actual.diff(e,2).subs(e,0)/2
    assert coefficient==sp.Matrix([0,4*sp.sqrt(3)/15,0])
    assert not any(coefficient.has(v) for v in [*A2,*P2])


def test_vacuum_obstruction_must_not_be_claimed_at_nonzero_background():
    e=sp.Symbol('e');a=sp.Matrix([1,e,0]);phi=e*a
    assert a.cross(phi)==sp.zeros(3,1)
    a1=a.diff(e).subs(e,0);p1=phi.diff(e).subs(e,0)
    assert a1.cross(p1)!=sp.zeros(3,1)
    # Here a0 cross phi2/2 cancels that coefficient; the vacuum proof cannot apply.
    assert gate.zero(a1.cross(p1)+a.subs(e,0).cross(phi.diff(e,2).subs(e,0))/2)


def test_alignment_Jacobian_rank_is_not_a_particle_or_Dirac_count():
    data=gate.derive_second_order()
    assert data['zero_rank']==0 and data['aligned_rank']==2
    a,p=sp.Matrix(sp.symbols('a1:4')),sp.Matrix(sp.symbols('phi1:4'))
    J=data['jacobian']
    assert J.subs(dict(zip([*a,*p],[0,0,0,1,2,3]))).rank()==2
    assert J.subs(dict(zip([*a,*p],[1,0,0,0,1,0]))).rank()==3
    assert gate.zero(J*sp.Matrix([*a,*p])-2*a.cross(p))


def test_receipt_recomputation_and_negative_scope(payload):
    assert gate.validate_payload(payload)==payload
    assert len(payload['checks'])==36
    assert all(payload['checks'].values()) and all(payload['negative_controls'].values())
    assert payload['scope']['fixed_direction_upstream_N8_lift_refuted'] is False
    assert payload['decision']['all_solutions_excluded_claimed'] is False

@pytest.mark.parametrize('key',('full_N7','full_N2_Dirac_rank_computed','repair_stability_certified','all_solutions_excluded_claimed'))
def test_rehashed_overclaim_is_rejected(payload,key):
    bad=deepcopy(payload);bad['decision'][key]=True
    bad.pop('calculation_digest');bad['calculation_digest']=gate.digest(bad)
    with pytest.raises(gate.CompatibilityError,match='fresh source-bound'):
        gate.validate_payload(bad)


def test_rehashed_disappearing_witness_is_rejected(payload):
    bad=deepcopy(payload);bad['witness']['point_current_coefficient']=['0','0','0']
    bad.pop('calculation_digest');bad['calculation_digest']=gate.digest(bad)
    with pytest.raises(gate.CompatibilityError):gate.validate_payload(bad)


def test_source_byte_changes_rejected(tmp_path):
    note=tmp_path/'note';note.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.CompatibilityError,match='lemma hash'):gate.load_sources(note=note)
    candidate=tmp_path/'candidate';candidate.write_bytes(gate.CANDIDATE.read_bytes()+b'\n')
    with pytest.raises(gate.CompatibilityError,match='candidate hash'):gate.load_sources(candidate=candidate)

@pytest.mark.parametrize('raw',(b'{"a":1,"a":2}',b'{"a":NaN}',b'[]'))
def test_strict_json(raw):
    with pytest.raises(gate.CompatibilityError):gate.read_json(raw)


def test_localization_bound_is_strict_and_keeps_R3_normalization():
    data=gate.derive_localization()
    assert all(data['checks'].values())
    u,r=data['u'],data['r']
    # Independent substitution r=u tan(theta) integrates the radial probability.
    theta=sp.Symbol('theta',nonnegative=True)
    angular_density=4*sp.sin(theta)**2/sp.pi
    assert sp.integrate(angular_density,(theta,0,sp.pi/2))==1
    assert data['torque_margin']==sp.Rational(197,640)>0
    assert sp.Rational(4,15)-sp.Rational(21,128)==data['cross_margin']
    assert sp.factor(data['difference']).is_positive is True
    # Omitting the 4*pi radial measure or the factor 2Z gives a different tail.
    assert not gate.zero(data['mixture_tail']-4*data['Z']/(sp.pi*data['kappa']*data['R']))


def test_Fourier_halfline_energy_and_L2_integrals_for_localized_data():
    radial,p,c=sp.symbols('radial p c',positive=True)
    h=c*sp.exp(-p*radial)
    assert sp.integrate(sp.diff(h,radial)**2+p*p*h*h,(radial,0,sp.oo))==p*c*c
    assert sp.integrate(h*h,(radial,0,sp.oo))==c*c/(2*p)
    # For phi_hat=O(p), the radial L2 integrand including R3 measure is O(p^3).
    assert sp.integrate(p**3,(p,0,1))==sp.Rational(1,4)
