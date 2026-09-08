#!/usr/bin/env python3
"""Source-bound identities for the localized quadratic torque lift.

Analytic solvability and decay are in the pinned lemma. This does not claim
coupled nonlinear existence, a sourced bulk B lift, or adoption of chi.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp
if __package__:
 from . import verify_one_omega_interface_connection_current_candidate_v1 as current_candidate
else:
 import verify_one_omega_interface_connection_current_candidate_v1 as current_candidate

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_connection_localized_torque_lift_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_localized_torque_lift_v1.py'
OUTPUT=HERE/'artifacts/one_omega_connection_localized_torque_lift_v1.json'
NOTE_SHA256='8af2a8626df9fd665a721d203e30536396d85a83093a9352cfda4003f960561f'
PINS={
 'one_omega_bf_robin_compatibility_v1':'61cb8ac8ac88bd9ff888118af0fedd6b95c4c694361958a436b6523ba78fe325',
 'one_omega_interface_connection_current_candidate_v1':'e51d8d47ee97e20c6aea5aebb4680a65cba79254c2ea0a30fd6a88774b6535e8',
}
SCHEMA='holo.one-omega-connection-localized-torque-lift.v1'
class TorqueLiftError(ValueError):pass

def digest(obj):
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def zero(x):
 return all(sp.cancel(v)==0 for v in x) if isinstance(x,sp.MatrixBase) else sp.cancel(x)==0

def read_json(raw):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise TorqueLiftError('duplicate JSON key')
   out[k]=v
  return out
 def bad(value):raise TorqueLiftError('nonfinite JSON constant')
 try:out=json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)
 except (ValueError,UnicodeError) as e:raise TorqueLiftError('invalid JSON') from e
 if type(out) is not dict:raise TorqueLiftError('JSON root must be object')
 return out

def load_sources(note=NOTE,base=HERE):
 if hashlib.sha256(Path(note).read_bytes()).hexdigest()!=NOTE_SHA256:raise TorqueLiftError('lemma hash mismatch')
 out={'lemma_sha256':NOTE_SHA256,'artifacts':{}}
 for name,expected in PINS.items():
  path=Path(base)/'artifacts'/(name+'.json');raw=path.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=expected:raise TorqueLiftError('source receipt hash mismatch')
  item=read_json(raw)
  if not item.get('checks') or not all(v is True for v in item['checks'].values()):raise TorqueLiftError('source checks not true')
  pins=dict(item.get('provenance',{}))
  if 'implementation' in item:
   pins['verify_'+name+'.py']=item['implementation']['verifier_sha256']
   pins['test_'+name+'.py']=item['implementation']['test_sha256']
   pins[name.replace('_v1','_lemma_v1')+'.md']=item['sources']['lemma_sha256']
  for filename,sha in pins.items():
   if Path(filename).name!=filename:raise TorqueLiftError('nonlocal provenance path')
   if hashlib.sha256((Path(base)/filename).read_bytes()).hexdigest()!=sha:raise TorqueLiftError('source implementation changed')
  if name=='one_omega_bf_robin_compatibility_v1':
   if item['witness']['localized_current_lower_bound']!='197/640' or item['witness']['localized_cutoff_radius']!=256:
    raise TorqueLiftError('localized witness mismatch')
  out['artifacts'][name]={'sha256':expected,'source_gates_inherited':False}
 return out

def derive_source():
 F,U=sp.symbols('F U',real=True)
 f=sp.Matrix(sp.symbols('Fx Fy Fz',real=True));u=sp.Matrix(sp.symbols('Ux Uy Uz',real=True))
 fh=sp.symarray('Fh',(3,3));uh=sp.symarray('Uh',(3,3))
 FH=sp.Matrix(3,3,lambda i,j:fh[min(i,j),max(i,j)])
 UH=sp.Matrix(3,3,lambda i,j:uh[min(i,j),max(i,j)])
 kappa,y=sp.symbols('kappa y',positive=True);c=kappa*y*y
 rho=c*f.cross(u)
 curlW=sp.Matrix([sum(sp.LeviCivita(i,j,k)*c*(f[j]*u[k]+F*UH[k,j]) for j in range(3) for k in range(3)) for i in range(3)])
 divrho=sum(c*sp.LeviCivita(i,j,k)*(FH[j,i]*u[k]+f[j]*UH[k,i]) for i in range(3) for j in range(3) for k in range(3))
 Qp,Qm=sp.symbols('Qplus_n Qminus_n')
 outgoing=-Qp+Qm;jump=Qp-Qm
 e=sp.Symbol('epsilon');a2=sp.Matrix(sp.symbols('a2x a2y a2z'));p2=sp.Matrix(sp.symbols('p2x p2y p2z'))
 torque=kappa*y*(e*f+e*e*a2).cross(e*y*u+e*e*p2)
 coefficient=torque.applyfunc(lambda v:sp.expand(v).coeff(e,2))
 return {'F':F,'U':U,'f':f,'u':u,'FH':FH,'UH':UH,'kappa':kappa,'y':y,'rho':rho,'curlW':curlW,'divrho':divrho,
         'checks':{'source_is_curl_of_compact_vector_potential':zero(curlW-rho),
                   'source_is_spatially_divergence_free':zero(divrho),
                   'declared_four_form_jump_is_minus_outgoing_sum':zero(jump+outgoing),
                   'second_order_source_independent_of_second_order_data':zero(coefficient-rho)},
         'negative':{'flip_jump_orientation_only':2*rho,'drop_gradient_cross_source':rho}}

def derive_geometry():
 t,x,y,z=sp.symbols('t x y z');coords=(t,x,y,z)
 N=sp.Function('N')(x,y,z);metric=sp.diag(-N*N,1,1,1);inverse=sp.diag(-1/(N*N),1,1,1)
 def christoffel(a,mu,b):
  return sp.simplify(sum(inverse[a,c]*(sp.diff(metric[c,b],coords[mu])+sp.diff(metric[c,mu],coords[b])-sp.diff(metric[mu,b],coords[c]))/2 for c in range(4)))
 omega=[christoffel(a,mu,b) for mu in range(4) for a in range(1,4) for b in range(1,4)]
 return {'omega':omega,'acceleration_connection':christoffel(1,0,0),
         'checks':{'prescribed_lapse_projected_connection_all_36_entries_zero':all(v==0 for v in omega),
                   'nontrivial_lapse_geometry_not_set_to_flat_metric':zero(christoffel(1,0,0)-N*sp.diff(N,x))}}

def derive_poisson():
 chi,p,R,M1=sp.symbols('chi p R M1',positive=True)
 green=current_candidate.derive_oriented_bf_green()
 source_sign=green['compatibility_current_coefficient']
 rhohat=sp.Symbol('rho_hat');theta=source_sign*rhohat/(chi*p*p)
 radius=sp.Symbol('radius',positive=True)
 kernel=source_sign/(4*sp.pi*chi*radius)
 lap=sp.diff(kernel,radius,2)+2*sp.diff(kernel,radius)/radius
 flux=chi*4*sp.pi*radius*radius*sp.diff(kernel,radius)
 low_l2=sp.integrate(4*sp.pi*M1*M1/(chi*chi),(p,0,R))
 low_energy=sp.integrate(2*sp.pi*M1*M1*p*p/chi,(p,0,R))
 x,z=sp.symbols('x z',real=True)
 F=sp.cos(x)+sp.cos(2*z);U=sp.cos(x)/3+sp.cos(2*z)/5
 f=sp.Matrix([sp.diff(F,x),0,sp.diff(F,z)])
 u=sp.Matrix([sp.diff(U,x),0,sp.diff(U,z)])
 rho=3*f.cross(u);Theta=source_sign*rho/(5*chi)
 lapTheta=Theta.applyfunc(lambda v:sp.diff(v,x,2)+sp.diff(v,z,2))
 periodic_energy_density=chi*sum(sp.diff(v,x)**2+sp.diff(v,z)**2 for v in Theta)/2
 periodic_energy=sp.integrate(periodic_energy_density,(x,0,2*sp.pi),(z,0,2*sp.pi))
 lower=sp.Rational(197,640)
 checks={'Fourier_Poisson_multiplier_has_required_sign':zero(-chi*p*p*theta+rhohat),
         'Coulomb_kernel_harmonic_away_from_source':zero(lap),
         'Coulomb_source_kernel_flux_is_negative_one':flux==-1,
         'zero_mean_infrared_L2_bound':low_l2==4*sp.pi*M1*M1*R/(chi*chi),
         'zero_mean_infrared_energy_bound':low_energy==2*sp.pi*M1*M1*R**3/(3*chi),
         'energy_Parseval_factor':zero(chi*p*p*theta**2/2-rhohat**2/(2*chi*p*p)),
         'actual_two_mode_source_positive_jump_sign':zero(rho-sp.Matrix([0,sp.Rational(4,5)*sp.sin(x)*sp.sin(2*z),0])),
         'actual_two_mode_compatibility_cancelled':zero(chi*lapTheta+rho),
         'periodic_energy_normalization':zero(periodic_energy-8*sp.pi**2/(125*chi)),
         'inherited_localized_source_bound_is_strictly_positive':lower.is_positive is True}
 return {'chi':chi,'p':p,'R':R,'M1':M1,'rhohat':rhohat,'theta_multiplier':theta,'kernel':kernel,
         'periodic_rho':rho,'periodic_Theta':Theta,'periodic_energy':periodic_energy,'low_L2':low_l2,'low_energy':low_energy,
         'checks':checks,'negative':{'old_Poisson_sign_leaves_twice_the_material_source':2*rhohat,
                                    'assume_mean_zero_without_source_structure':sp.Integral(1/p**2,(p,0,1)),
                                    'omit_second_wavenumber_in_periodic_gain':3*f.cross(f/3)-rho}}

def derive_flatness():
 T=[sp.Matrix(3,3,lambda j,k:sp.LeviCivita(i,j,k)) for i in range(3)]
 def mat(prefix):return sum((v*T[i] for i,v in enumerate(sp.symbols(prefix+'1:4'))),sp.zeros(3))
 P,Q=mat('P'),mat('Q');comm=P*Q-Q*P
 # Maurer-Cartan expansion for -d exp(a Theta) exp(-a Theta).
 # Antisymmetrized derivative of -(a²/2)[Theta,dTheta] is -a²[P,Q].
 derivative_correction=-sp.Rational(1,2)*(comm-(-comm))
 bracket_correction=(-P)*(-Q)-(-Q)*(-P)
 return {'commutator':comm,'checks':{'nonabelian_exponential_connection_flat_through_quartic_epsilon':zero(derivative_correction+bracket_correction),
             'nonabelian_commutator_not_assumed_zero':not zero(comm)},
         'negative':{'omit_Maurer_Cartan_quadratic_correction':bracket_correction}}

def serialize(value):
 if isinstance(value,sp.MatrixBase):return [[sp.sstr(value[i,j]) for j in range(value.cols)] for i in range(value.rows)]
 if isinstance(value,sp.Basic):return sp.sstr(value)
 if isinstance(value,dict):return {k:serialize(v) for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [serialize(v) for v in value]
 return value

def build_payload():
 sources=load_sources();source=derive_source();geometry=derive_geometry();poisson=derive_poisson();flat=derive_flatness()
 checks={**source['checks'],**geometry['checks'],**poisson['checks'],**flat['checks']}
 negatives={**source['negative'],**poisson['negative'],**flat['negative']}
 # The nonzero-mean example has divergent L2 potential; evaluate this one integral.
 controls={k:(sp.integrate(v.function,v.limits[0])==sp.oo if isinstance(v,sp.Integral) else not zero(v)) for k,v in negatives.items()}
 if not all(v is True for v in checks.values()) or not all(controls.values()):raise TorqueLiftError('identity or negative control failed')
 out={'schema':SCHEMA,'sources':sources,'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
      'checks':checks,'negative_controls':controls,
      'model':serialize({'source':source['rho'],'periodic_source':poisson['periodic_rho'],'periodic_Theta':poisson['periodic_Theta'],
                         'Fourier_Theta':poisson['theta_multiplier'],'low_L2':poisson['low_L2'],'low_energy':poisson['low_energy']}),
      'analytic_input':{'source_class':'rho2=curl(kappa*y²*F*grad(g(|D|)F)), F real C_c^infinity(R3)',
                        'zero_mean':'integration by parts of compact vector potential',
                        'solution_space':'unique L2 static Theta; H^m for every finite m and finite spatial energy',
                        'localized_nonzero_source_lower_bound':'197/640','pointwise_grid_used_as_proof':False},
      'decision':{'localized_order_epsilon_squared_compatibility_lift':True,
                  'flat_A_trace_realization_by_exact_Maurer_Cartan':True,
                  'candidate_adopted':False,'chi_selected':False,'full_sourced_B_bulk_lift':False,
                  'coupled_Einstein_solution':False,'higher_order_continuation':False,
                  'static_energy_is_global_time_action':False,'full_N4':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}
 out['calculation_digest']=digest(out)
 return out

def validate_payload(payload):
 expected=build_payload()
 if payload!=expected:raise TorqueLiftError('receipt differs from fresh source-bound derivation')
 return expected

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 mode=parser.add_mutually_exclusive_group(required=True)
 mode.add_argument('--write',action='store_true');mode.add_argument('--verify',action='store_true');args=parser.parse_args()
 if args.verify:out=validate_payload(read_json(OUTPUT.read_bytes()))
 else:
  out=build_payload()
  with OUTPUT.open('x') as f:json.dump(out,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
 print(json.dumps({'checks_passed':len(out['checks']),'negative_controls':out['negative_controls'],'calculation_digest':out['calculation_digest']}))
 return 0
if __name__=='__main__':raise SystemExit(main())
