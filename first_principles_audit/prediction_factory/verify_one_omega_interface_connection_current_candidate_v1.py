"""Unadopted connection-current candidate; only its local channel is checked."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sympy as sp

HERE = Path(__file__).resolve().parent
SOURCE = HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
PROOF = HERE/'one_omega_interface_connection_current_candidate_lemma_v1.md'
TEST = HERE/'test_one_omega_interface_connection_current_candidate_v1.py'
OUTPUT = HERE/'artifacts/one_omega_interface_connection_current_candidate_v1.json'
SOURCE_SHA = 'd9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
ACTION_SHA = '3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a'
PROOF_SHA = 'ab9745c81faf58e83fef2937b97f7de7e2c6f9ae3bce8bd3cf4fa8aeeb87966b'
SCHEMA = 'holo.one-omega-interface-connection-current-candidate.v1'


class ConnectionCandidateError(ValueError):
    pass


def canonical_digest(value):
    raw = json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def wedge(left,right):
    result={}
    for a,ca in left.items():
        for b,cb in right.items():
            if set(a)&set(b): continue
            key=tuple(sorted(a+b)); sign=(-1)**sum(i>j for i in a for j in b)
            result[key]=result.get(key,0)+sign*ca*cb
    return {key:value for key,raw in result.items() if (value:=sp.expand(raw))!=0}


def star_one(components,inverse_metric,volume):
    raised=inverse_metric*sp.Matrix(components)
    return {tuple(a for a in range(4) if a!=mu):(-1)**mu*volume*raised[mu] for mu in range(4)}


def derive_model():
    chi=sp.Symbol('chi',positive=True); volume=sp.Symbol('sqrt_minus_gamma',positive=True)
    slots={(i,j):sp.Symbol(f'gamma_inv_{i}{j}',real=True) for i in range(4) for j in range(i,4)}
    inverse=sp.Matrix(4,4,lambda i,j:slots[min(i,j),max(i,j)])
    A=[sp.Matrix(sp.symbols(f'A{c}_0:4',real=True)) for c in range(3)]
    omega=[sp.Matrix(sp.symbols(f'omega{c}_0:4',real=True)) for c in range(3)]
    delta=[sp.Matrix(sp.symbols(f'deltaA{c}_0:4',real=True)) for c in range(3)]
    C=[a-o for a,o in zip(A,omega)]
    density=-chi*volume*sum((c.T*inverse*c)[0] for c in C)/2
    direct=sum(sp.diff(density,A[color][mu])*delta[color][mu] for color in range(3) for mu in range(4))
    current=[{k:chi*v for k,v in star_one(c,inverse,volume).items()} for c in C]
    paired=sum(wedge(j,{(mu,):d[mu] for mu in range(4)}).get((0,1,2,3),0) for j,d in zip(current,delta))
    dBp,dBm,jp,jm,dJ=sp.symbols('D_b_plus D_b_minus j4_plus j4_minus D_J_Sigma',real=True)
    Eplus=dBp+jp; Eminus=dBm+jm; D_boundary=dBp-dBm-dJ
    compatibility=sp.expand(Eplus-Eminus-D_boundary)
    # Curvature-only first variation vanishes identically on the BF flat branch.
    alpha=sp.Symbol('alpha',positive=True); eta=sp.diag(-1,1,1,1)
    pairs=list(itertools.combinations(range(4),2))
    F={key:sp.Symbol('F_'+''.join(map(str,key)),real=True) for key in pairs}
    deltaF={key:sp.Symbol('deltaF_'+''.join(map(str,key)),real=True) for key in pairs}
    YM=-alpha*sum(eta[i,i]*eta[j,j]*F[i,j]**2 for i,j in pairs)/2
    dYM=sum(sp.diff(YM,F[key])*deltaF[key] for key in pairs)
    Fjets={(a,i,j):sp.Symbol(f'D{a}F{i}{j}',real=True) for a in range(4) for i,j in pairs}
    def jet(a,i,j):
        return 0 if i==j else (1 if i<j else -1)*Fjets[a,min(i,j),max(i,j)]
    YM_EL=sp.Matrix([alpha*sum(eta[mu,mu]*eta[nu,nu]*jet(mu,mu,nu) for mu in range(4)) for nu in range(4)])
    # Flat fixed geometry only: C=-d theta, no gravitational perturbation frozen into a claim.
    theta_jets=[sp.Matrix(sp.symbols(f'dtheta{c}_0:4',real=True)) for c in range(3)]
    Ltheta=-chi*sum((v.T*eta*v)[0] for v in theta_jets)/2
    momenta=sp.Matrix([sp.diff(Ltheta,v[0]) for v in theta_jets])
    Htheta=sp.expand(sum(p*v[0] for p,v in zip(momenta,theta_jets))-Ltheta)
    energy_reference=chi*sum(v[mu]**2 for v in theta_jets for mu in range(4))/2
    velocities=[v[0] for v in theta_jets]
    kinetic=sp.hessian(Ltheta,velocities)
    full_energy_hessian=sp.hessian(Htheta,[v[mu] for v in theta_jets for mu in range(4)])
    geom=sp.Matrix(sp.symbols('delta_omega_0:4',real=True)); dtheta=theta_jets[0]
    Lmoving=-chi*((dtheta+geom).T*eta*(dtheta+geom))[0]/2
    cross=sp.Matrix(4,4,lambda i,j:sp.diff(Lmoving,dtheta[i],geom[j]))
    # Explicit signed source. J0 is not fixed by an orientation guess.
    x,z=sp.symbols('x z',real=True); J0=sp.Symbol('J0',real=True)
    source=J0*sp.sin(x)*sp.sin(2*z)
    theta=-source/(5*chi)
    lap=sp.diff(theta,x,2)+sp.diff(theta,z,2)
    current_div=-chi*lap
    energy_density=chi*(sp.diff(theta,x)**2+sp.diff(theta,z)**2)/2
    cell_energy=sp.integrate(energy_density,(x,0,2*sp.pi),(z,0,2*sp.pi))
    residuals={
        'current_sign_from_independent_density_variation':sp.expand(direct-paired),
        'bulk_and_boundary_rows_give_DJ_plus_jumpj':sp.expand(compatibility-(dJ+jp-jm)),
        'curvature_squared_first_variation_zero_on_flat_field':sp.expand(dYM.subs({f:0 for f in F.values()})),
        'curvature_squared_current_zero_with_flat_jets':YM_EL.subs({j:0 for j in Fjets.values()}),
        'flat_theta_canonical_energy':sp.expand(Htheta-energy_reference),
        'flat_theta_kinetic_matrix':kinetic-chi*sp.eye(3),
        'flat_theta_full_energy_hessian':full_energy_hessian-chi*sp.eye(12),
        'moving_geometry_cross_coefficient':cross+chi*eta,
        'static_signed_source_absorbed':sp.expand(current_div+source),
        'static_source_cell_energy':sp.simplify(cell_energy-J0**2*sp.pi**2/(10*chi)),
    }
    negative={
        'wrong_current_sign':sp.expand(direct+paired),
        'omit_intrinsic_current_from_boundary_row':sp.expand(Eplus-Eminus-(dBp-dBm)-compatibility),
        'wrong_static_response_sign':sp.expand(-current_div+source),
        'freeze_geometry_connection_in_quadratic_action':cross,
        'negative_chi_gives_negative_kinetic':-kinetic,
    }
    def zero(value):
        return all(v==0 for v in value) if isinstance(value,sp.MatrixBase) else value==0
    checks={name:zero(value) for name,value in residuals.items()}
    checks.update({'positive_symbolic_chi':chi.is_positive is True,
                   'wrong_current_sign_detected':negative['wrong_current_sign']!=0,
                   'missing_boundary_current_detected':negative['omit_intrinsic_current_from_boundary_row']!=0,
                   'wrong_static_response_sign_detected':negative['wrong_static_response_sign']!=0,
                   'geometry_mixing_is_nonzero':cross!=sp.zeros(4),
                   'channel_kinetic_coefficient_positive':kinetic[0,0].is_positive is True})
    return {'symbols':{'chi':chi,'volume':volume,'inverse_metric':inverse,'A':A,'omega':omega,
                       'delta_A':delta,'F':F,'delta_F':deltaF,'F_jets':Fjets,
                       'theta_jets':theta_jets,'delta_omega':geom,'J0':J0,'x':x,'z':z},
            'candidate_action_density':density,'density_variation':direct,'current_three_forms':current,
            'current_pairing':paired,'compatibility':compatibility,
            'curvature_squared_first_variation':dYM,'curvature_squared_principal_EL':YM_EL,
            'flat_theta_action':Ltheta,'flat_theta_momenta':momenta,'flat_theta_energy':Htheta,
            'flat_theta_kinetic':kinetic,'flat_theta_energy_hessian':full_energy_hessian,
            'geometry_mixing':cross,'moving_geometry_action_one_color':Lmoving,
            'static_source':source,'static_theta_solution':theta,'static_current_divergence':current_div,
            'static_energy_density':energy_density,'static_cell_energy':cell_energy,
            'residuals':residuals,'negative_controls':negative,
            'checks':{key:bool(value) for key,value in checks.items()}}


def serialize(value):
    if isinstance(value,sp.MatrixBase): return [[serialize(x) for x in row] for row in value.tolist()]
    if isinstance(value,dict):
        return {(','.join(map(str,key)) if isinstance(key,tuple) else key):serialize(v) for key,v in value.items()}
    if isinstance(value,(tuple,list)): return [serialize(v) for v in value]
    return str(value) if isinstance(value,sp.Basic) else value


def build_payload():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA: raise ConnectionCandidateError('frozen source byte pin mismatch')
    frozen=json.loads(raw)
    if canonical_digest(frozen['exact_classical_charter']['exact_action'])!=ACTION_SHA:
        raise ConnectionCandidateError('frozen literal action mismatch')
    if hashlib.sha256(PROOF.read_bytes()).hexdigest()!=PROOF_SHA:
        raise ConnectionCandidateError('candidate proof pin mismatch')
    model=derive_model()
    if not all(model['checks'].values()): raise ConnectionCandidateError('candidate algebra check failed')
    payload={'schema':SCHEMA,'baseline':{'source_sha256':SOURCE_SHA,'literal_action_sha256':ACTION_SHA},
             'proposal':{'new_term':'S_C=-chi/2*integral_Sigma <(A_Sigma-omega) wedge star_gamma(A_Sigma-omega)>',
                         'chi':'strictly positive symbolic coefficient; no value selected',
                         'A_Sigma_remains_independent':True,'adopted_into_v5_2':False},
             'model':serialize(model),'checks':model['checks'],
             'decision':{'candidate_current_variation_checked':True,
                         'necessary_current_compatibility_checked':True,
                         'fixed_flat_geometry_channel_positive_principal_energy':True,
                         'static_periodic_cell_source_response_checked':True,
                         'complete_model_repair_proved':False,'old_linear_response_unchanged':False,
                         'full_B_field_or_coupled_solution_constructed':False,
                         'global_energy_or_boundary_domain_proved':False,
                         'complete_gravitational_khronon_energy_positive':False,
                         'new_coefficient_selected':False,'candidate_adopted':False,
                         'N2_CONSTRAINTS_pass':False,'N3_CHARACTERISTICS_pass':False,
                         'N4_JUNCTION_BENDING_pass':False,'N5_COUPLED_BVP_pass':False,
                         'N6_GLOBAL_STABILITY_pass':False,'N7_LINEAR_REDUCTION_pass':False,
                         'BF_global_quotient_closed':False,'full_N7':False,
                         'P4_full_same_action_pass':False,'B4_pass':False,'B5_pass':False},
             'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST,PROOF)}}
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:
        raise ConnectionCandidateError('candidate receipt schema mismatch')
    if payload.get('calculation_digest')!=canonical_digest({k:v for k,v in payload.items() if k!='calculation_digest'}):
        raise ConnectionCandidateError('candidate receipt digest mismatch')
    if payload!=build_payload(): raise ConnectionCandidateError('candidate receipt differs from fresh derivation')


def main():
    parser=argparse.ArgumentParser(description=__doc__); modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path)
    modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path); args=parser.parse_args()
    if args.write:
        result=build_payload()
        with args.write.open('x',encoding='utf-8') as stream:
            json.dump(result,stream,sort_keys=True,indent=2,allow_nan=False); stream.write('\n')
    else:
        result=json.loads(args.verify.read_text()); validate_payload(result)
    print(json.dumps({'schema':SCHEMA,'checks_passed':sum(result['checks'].values()),
                      'checks_total':len(result['checks']),'calculation_digest':result['calculation_digest']}))


if __name__=='__main__': main()
