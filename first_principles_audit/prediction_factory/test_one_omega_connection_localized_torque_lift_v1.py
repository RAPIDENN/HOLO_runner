"""Independent signs, infrared obstruction, compact-source identities and receipts."""
import copy
import json
from pathlib import Path
import pytest
import sympy as sp
import verify_one_omega_connection_localized_torque_lift_v1 as v

@pytest.fixture(scope='module')
def payload():return v.build_payload()

def test_concrete_compact_potential_has_zero_charge_by_integration():
 # This compact C1 cutoff is an independent integration-by-parts oracle,
 # not a replacement for the lemma's C_c^infinity response source.
 x,y,z=sp.symbols('x y z',real=True);coords=(x,y,z)
 F=(1-x*x)**2*(1-y*y)**2*(1-z*z)**2
 U=x*z+x*y*y
 a=sp.Matrix([sp.diff(F,c) for c in coords]);b=sp.Matrix([sp.diff(U,c) for c in coords])
 rho=a.cross(b)
 assert any(sp.expand(c)!=0 for c in rho)
 for component in rho:
  assert sp.integrate(sp.expand(component),(x,-1,1),(y,-1,1),(z,-1,1))==0
 # A false common gain would force phi parallel to a and erase this source.
 assert a.cross(2*a)==sp.zeros(3,1)

def test_generic_curl_uses_symmetric_hessians():
 m=v.derive_source()
 assert all(m['checks'].values())
 assert v.zero(m['curlW']-m['rho'])
 assert m['rho'].has(m['kappa'],m['y'])
 # A nonzero local value exists even though the spatial integral is zero.
 substitution=dict(zip([*m['f'],*m['u']],[1,0,0,0,0,1]))
 assert m['rho'].subs(substitution)==sp.Matrix([0,-m['kappa']*m['y']**2,0])

def test_jump_sign_independently_from_outward_normals():
 # J4=i_Q(dn wedge volSigma), while plus/minus outward signs are -/+.
 Qp,Qm=sp.Rational(7,3),sp.Rational(-2,5)
 jump=Qp-Qm;outgoing=-Qp+Qm
 assert jump==-outgoing and jump!=outgoing

def test_nonzero_mean_is_not_L2_though_gradient_has_finite_far_energy():
 r=sp.Symbol('r',positive=True)
 potential=1/r
 assert sp.integrate(r*r*potential*potential,(r,1,sp.oo))==sp.oo
 assert sp.integrate(r*r*sp.diff(potential,r)**2,(r,1,sp.oo))==1
 # Dipole tail produced by vanishing charge is square integrable.
 assert sp.integrate(r*r/r**4,(r,1,sp.oo))==1

def test_coulomb_sign_against_sphere_flux():
 m=v.derive_poisson();r=next(iter(m['kernel'].free_symbols-{m['chi']}))
 flux=sp.simplify(4*sp.pi*r*r*sp.diff(m['kernel'],r)*m['chi'])
 assert flux==-1
 assert -flux!=-1

def test_two_distinct_material_gains_give_exact_source_and_solution():
 m=v.derive_poisson();chi=m['chi']
 x,z=sp.symbols('x z',real=True)
 source=m['periodic_rho'][1];theta=m['periodic_Theta'][1]
 assert sp.simplify(source-sp.Rational(4,5)*sp.sin(x)*sp.sin(2*z))==0
 assert sp.simplify(chi*(sp.diff(theta,x,2)+sp.diff(theta,z,2))+source)==0
 assert sp.simplify(chi*(sp.diff(-theta,x,2)+sp.diff(-theta,z,2))+source)!=0
 assert sp.simplify(m['periodic_energy']-8*sp.pi**2/(125*chi))==0

def test_lapse_is_nonconstant_but_its_projected_connection_vanishes():
 m=v.derive_geometry()
 assert len(m['omega'])==36 and all(c==0 for c in m['omega'])
 assert m['acceleration_connection']!=0

def test_nonabelian_flatness_requires_second_Maurer_Cartan_term():
 m=v.derive_flatness()
 assert all(m['checks'].values())
 assert not v.zero(m['negative']['omit_Maurer_Cartan_quadratic_correction'])

def test_receipt_recomputed_from_sources(payload):
 assert v.validate_payload(payload)==payload
 assert len(payload['checks'])==18
 assert all(payload['negative_controls'].values())

@pytest.mark.parametrize('field',['coupled_Einstein_solution','full_sourced_B_bulk_lift','higher_order_continuation','candidate_adopted','full_N7'])
def test_self_rehashing_cannot_promote_scope(payload,field,monkeypatch):
 expected=copy.deepcopy(payload);changed=copy.deepcopy(payload)
 changed['decision'][field]=True
 changed.pop('calculation_digest');changed['calculation_digest']=v.digest(changed)
 # Avoid redundant symbolic runs across mutations; production still recomputes.
 monkeypatch.setattr(v,'build_payload',lambda:copy.deepcopy(expected))
 with pytest.raises(v.TorqueLiftError,match='fresh source-bound'):v.validate_payload(changed)

def test_local_note_tampering_is_rejected(tmp_path):
 path=tmp_path/'lemma.md';path.write_bytes(v.NOTE.read_bytes()+b'\nwrong sign')
 with pytest.raises(v.TorqueLiftError,match='lemma hash'):v.load_sources(note=path)

@pytest.mark.parametrize('raw',[b'{"a":1,"a":2}',b'{"x":NaN}',b'[]'])
def test_malformed_receipts_rejected(raw):
 with pytest.raises(v.TorqueLiftError):v.read_json(raw)


def test_material_gauge_variation_and_reduced_action_fix_source_sign():
 # Derive the material coefficient before integration by parts, without
 # using the assumed interface current equation.
 Z,chi=sp.symbols('Z chi',positive=True)
 phi=sp.Matrix(sp.symbols('phi0:3',real=True))
 derivative=sp.Matrix(sp.symbols('phi_n0:3',real=True))
 eta_n=sp.Matrix(sp.symbols('eta_n0:3',real=True))
 T=[sp.Matrix(3,3,lambda a,b:sp.LeviCivita(I,a,b)) for I in range(3)]
 deltaA=-sum((eta_n[I]*T[I] for I in range(3)),sp.zeros(3))
 literal_delta_L=-Z*derivative.dot(deltaA*phi)
 Q=Z*phi.cross(derivative)
 assert sp.expand(literal_delta_L+Q.dot(eta_n))==0
 # Thus the on-shell radial integral is -sum Q_out eta = +rho eta.
 x,z=sp.symbols('x z',real=True)
 theta=sp.Function('theta')(x,z);rho=sp.Function('rho')(x,z)
 L=-chi*(sp.diff(theta,x)**2+sp.diff(theta,z)**2)/2+rho*theta
 EL=sp.diff(L,theta)-sp.diff(sp.diff(L,sp.diff(theta,x)),x)-sp.diff(sp.diff(L,sp.diff(theta,z)),z)
 assert sp.expand(EL-rho-chi*(sp.diff(theta,x,2)+sp.diff(theta,z,2)))==0
 m=v.derive_poisson();Theta=m['periodic_Theta'][1];source=m['periodic_rho'][1]
 for sign,expected in ((1,0),(-1,2*source)):
  residual=source+m['chi']*sign*(sp.diff(Theta,x,2)+sp.diff(Theta,z,2))
  assert sp.simplify(residual-expected)==0
 assert source!=0
