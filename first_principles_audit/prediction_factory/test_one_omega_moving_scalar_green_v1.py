"""Independent moving-integral, metric and nonlinear-coordinate tests."""
from copy import deepcopy
import json
import pytest
import sympy as sp
if __package__:
    from . import verify_one_omega_moving_scalar_green_v1 as gate
else:
    import verify_one_omega_moving_scalar_green_v1 as gate

@pytest.fixture(scope='module')
def flux():return gate.derive_normal_flux()

@pytest.fixture(scope='module')
def payload():return gate.build_payload()

def test_literal_momenta_from_P_not_from_C(flux):
    o,G,Z=flux['o'],flux['G'],flux['Z']
    phi,v=flux['phi'],flux['v']
    P=[v[i+1]+3*phi[i]*v[0]/(2*o) for i in range(3)]
    literal=-G*v[0]**2/2-Z*sum(x*x for x in P)/2
    assert gate.zero(sp.Matrix([sp.diff(literal,x) for x in v])-flux['p'])
    assert not gate.zero(flux['negative']['omit_mixed_Omega_momentum'])


def test_full_potential_and_tangential_stress_are_present(flux):
    o,phi,Z,m=flux['o'],flux['phi'],flux['Z'],flux['m']
    radial=sp.sqrt(phi.dot(phi))*o**sp.Rational(3,2)
    V4=radial**4/(2*sp.sqrt(1+radial**4))
    assert gate.zero(flux['V']-sp.Function('U')(o)-Z*m*m*V4/o**5)
    # Holding all first jets fixed, V enters both T_nn and the moving term as -V.
    assert sp.diff(flux['Tnn'],sp.Function('U')(o)) == -1
    assert gate.zero(flux['Tnn']-flux['legendre'])
    assert flux['Tnn'].has(flux['tangents'][0,0],flux['tangents'][3,3])


def test_Hilbert_stress_independent_all_metric_diagonal_directions(flux):
    """Differentiate sqrt(-g)L using inverse metric variables in all 5 axes."""
    g=sp.symbols('gtt gxx gyy gzz grr',nonzero=True)
    jets=[flux['tangents'][:,i] for i in range(4)]+[flux['v']]
    C=flux['C']
    Q=[(u.T*C*u)[0] for u in jets]
    # At a diagonal inverse metric, d log sqrt(-g)/d g^{aa}=-1/(2g^{aa}).
    L=-sum(g[a]*Q[a] for a in range(5))/2-flux['V']
    eta=(-1,1,1,1,1);at=dict(zip(g,eta))
    for a in range(5):
        stress=-2*(sp.diff(L,g[a])-L/(2*g[a])).subs(at)
        expected=Q[a]+eta[a]*L.subs(at)
        assert gate.zero(stress-expected)
    assert gate.zero((Q[4]+L.subs(at))-flux['Tnn'])


def test_exact_nonlinear_field_coordinate_variation(flux):
    epsilon=sp.Symbol('eps')
    o,phi=flux['o'],flux['phi']
    delta=sp.Matrix(sp.symbols('d0:4'))
    direct=sp.Matrix([o+epsilon*delta[0],*[
        (o+epsilon*delta[0])**sp.Rational(3,2)*(phi[i]+epsilon*delta[i+1]) for i in range(3)]])
    tangent=direct.diff(epsilon).subs(epsilon,0)
    assert gate.zero(tangent-flux['J']*delta)
    assert gate.zero(flux['p'].dot(delta)-(-flux['Cnew']*flux['J']*flux['v']).dot(tangent))


def test_direct_moving_integrals_of_two_distinct_nonlinear_profiles():
    """Differentiate the integrals themselves; no Green formula is used to build LHS."""
    x,e=sp.symbols('x e',real=True)
    q,v=sp.symbols('q v',real=True)
    density=-(1+q*q)*v*v/2-q**4/4
    speed=sp.Rational(2,3);shared=sp.Rational(5,7)
    profiles=(1+x+x*x,1+2*x-x*x)
    variations=((shared-speed)*(1+x),(shared-2*speed)*(1-x))
    moved=[profiles[i]+e*variations[i] for i in range(2)]
    densities=[sp.expand(density.subs({q:u,v:sp.diff(u,x)},simultaneous=True)) for u in moved]
    # The wall value is a separate common material variable with the same first jet.
    wall=-(1+e*shared)**2/2
    actual=sp.integrate(densities[0],(x,-1,e*speed))+sp.integrate(densities[1],(x,e*speed,1))+wall
    derivative=sp.diff(actual,e).subs(e,0)
    p=sp.diff(density,v)
    volume=0;mom=[];ham=[]
    for i,u in enumerate(profiles):
        mapping={q:u,v:sp.diff(u,x)}
        pu=p.subs(mapping,simultaneous=True)
        Euler=sp.diff(density,q).subs(mapping,simultaneous=True)-sp.diff(pu,x)
        bounds=(-1,0) if i==0 else (0,1)
        volume+=sp.integrate(sp.expand(Euler*variations[i]),(x,*bounds))
        mom.append(pu.subs(x,0))
        ham.append((density.subs(mapping,simultaneous=True)-pu*sp.diff(u,x)).subs(x,0))
    expected=volume+(mom[0]-mom[1]-1)*shared+speed*(ham[0]-ham[1])
    assert sp.cancel(derivative-expected)==0
    # Omitting the Legendre subtraction changes this example; interface slopes differ.
    bad=volume+(mom[0]-mom[1]-1)*shared+speed*(
        densities[0].subs({x:0,e:0})-densities[1].subs({x:0,e:0}))
    assert sp.cancel(derivative-bad)!=0
    for i in range(2):
        trace=sp.diff(moved[i].subs(x,e*speed),e).subs(e,0)
        assert trace==shared


def test_reference_density_oracle_keeps_embedding_and_Euler_rows():
    result=gate.derive_moving_jets()
    assert all(result['checks'].values())
    assert result['E']!=sp.zeros(2,1)
    assert all(not gate.zero(x) for x in result['negative'].values())
    # Choosing delta=xi*v alone does not erase the boundary domain flux.
    mapping={result['delta'][i]:result['xi']*result['v'][i] for i in range(2)}
    assert gate.zero(result['green'].subs(mapping)-result['xi']*result['L'])


def test_common_normal_orientation_reversal_and_admissible_gluing():
    result=gate.derive_gluing()
    assert all(result['checks'].values())
    # Reverse n and swap names +/- together: the total Green form is invariant.
    mapping={result['f']:-result['f']}
    for i in range(4):
        mapping[result['vminus'][i]]=-result['vplus'][i]
        mapping[result['vplus'][i]]=-result['vminus'][i]
        mapping[result['pminus'][i]]=-result['pplus'][i]
        mapping[result['pplus'][i]]=-result['pminus'][i]
    Lm,Lp=sp.symbols('Lminus Lplus');mapping[Lm]=Lp;mapping[Lp]=Lm
    assert gate.zero(result['left'].xreplace(mapping)-result['left'])
    assert not gate.zero(result['negative']['frozen_bulk_generic_moving_gluing'])
    assert not gate.zero(result['negative']['same_outward_incidence_on_both_sides'])


def test_bound_receipt_is_recomputed(payload):
    assert gate.validate_payload(payload)==payload
    assert len(payload['checks'])==16
    assert len(payload['negative_controls'])==6
    assert all(payload['checks'].values())

@pytest.mark.parametrize('which',('full_N4','full_N7','B4','complete_gravitational_moving_variation'))
def test_favorable_scope_mutation_even_rehashed_is_rejected(payload,which):
    bad=deepcopy(payload);bad['decision'][which]=True
    bad.pop('calculation_digest');bad['calculation_digest']=gate.digest(bad)
    with pytest.raises(gate.MovingScalarError,match='fresh source-bound'):
        gate.validate_payload(bad)


def test_note_and_candidate_changes_rejected(tmp_path):
    note=tmp_path/'note.md';note.write_bytes(gate.NOTE.read_bytes()+b'\n')
    with pytest.raises(gate.MovingScalarError,match='lemma hash'):
        gate.load_sources(note=note)
    candidate=tmp_path/'candidate.json';candidate.write_bytes(gate.CANDIDATE.read_bytes()+b'\n')
    with pytest.raises(gate.MovingScalarError,match='candidate hash'):
        gate.load_sources(candidate=candidate)

@pytest.mark.parametrize('raw',(b'{"a":1,"a":2}',b'{"a":NaN}',b'[]'))
def test_strict_json(raw):
    with pytest.raises(gate.MovingScalarError):gate.read_json(raw)
