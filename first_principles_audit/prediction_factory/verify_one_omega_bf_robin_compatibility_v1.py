#!/usr/bin/env python3
"""Necessary BF/Robin torque compatibility and a prescribed-port obstruction.

The two-mode witness is not a coupled Einstein solution. Source-bound negative
scope is part of the receipt. No frozen action or broad gate is modified.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_bf_robin_compatibility_lemma_v1.md'
TEST=HERE/'test_one_omega_bf_robin_compatibility_v1.py'
OUTPUT=HERE/'artifacts/one_omega_bf_robin_compatibility_v1.json'
CANDIDATE=HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
NOTE_SHA256='db88d9f2d2f214face903a1a076ee0f2bd23db4359a5f48841adb187bb1040ac'
CANDIDATE_SHA256='d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
ACTION_SHA256='3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a'
SCHEMA='holo.one-omega-bf-robin-compatibility.v1'

class CompatibilityError(ValueError):pass

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
                                    ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def read_json(raw):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise CompatibilityError('duplicate JSON key')
            out[k]=v
        return out
    def invalid(x):raise CompatibilityError('nonfinite JSON constant')
    try:out=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    except (ValueError,UnicodeError) as exc:raise CompatibilityError('invalid JSON') from exc
    if type(out) is not dict:raise CompatibilityError('JSON root must be object')
    return out

def zero(value):
    return all(sp.cancel(x)==0 for x in value) if isinstance(value,sp.MatrixBase) else sp.cancel(value)==0

def load_sources(note=NOTE,candidate=CANDIDATE):
    bn,bc=Path(note).read_bytes(),Path(candidate).read_bytes()
    if hashlib.sha256(bn).hexdigest()!=NOTE_SHA256:raise CompatibilityError('lemma hash mismatch')
    if hashlib.sha256(bc).hexdigest()!=CANDIDATE_SHA256:raise CompatibilityError('candidate hash mismatch')
    c=read_json(bc)
    if c.get('schema')!='holo.one-omega-topological-so3-classical-v5-2-gate.v1':
        raise CompatibilityError('candidate schema mismatch')
    charter=c['exact_classical_charter']
    if digest(charter['exact_action'])!=ACTION_SHA256:raise CompatibilityError('action mismatch')
    params=charter['coefficient_policy']['parameters']
    for key,val in [('Robin_kappa_hat',1),('material_Z5_per_side',1),('Robin_y_squared',3)]:
        if sp.Rational(str(params[key]))!=val:raise CompatibilityError('frozen witness coefficient mismatch')
    if charter['interface_domain']['natural_B_flux_equation']!='sum_eps s_eps*b_eps=0 with s_plus=1 and s_minus=-1':
        raise CompatibilityError('BF flux gluing changed')
    return {'lemma_sha256':NOTE_SHA256,'candidate_sha256':CANDIDATE_SHA256,
            'action_sha256':ACTION_SHA256,
            'literal_coefficients':{key:str(params[key]) for key in ('Robin_kappa_hat','material_Z5_per_side','Robin_y_squared')},
            'BF_flux':charter['interface_domain']['natural_B_flux_equation'],
            'connection_trace':charter['definitions']['connection_trace'],
            'source_gate_promotions_inherited':False}

def generators():return tuple(sp.Matrix(3,3,lambda j,k:sp.LeviCivita(i,j,k)) for i in range(3))

def derive_current():
    T=generators()
    phi=sp.Matrix(sp.symbols('phi1:4',real=True))
    a=sp.Matrix(sp.symbols('a1:4',real=True))
    raw=sp.Matrix(sp.symbols('dphi1:4',real=True))
    An=sp.Matrix(sp.symbols('An1:4',real=True))
    Pi=sp.Matrix(sp.symbols('Pi1:4',real=True))
    Z,kappa,y,c=sp.symbols('Z kappa y c',positive=True)
    A=sum((An[i]*T[i] for i in range(3)),sp.zeros(3))
    P=raw+A*phi+c*phi
    L=-Z*P.dot(P)/2
    current=sp.Matrix([sp.diff(L,z) for z in An])
    reference=sp.Matrix([-Z*P.dot(t*phi) for t in T])
    outgoing=sp.Matrix([-Pi.dot(t*phi) for t in T])
    robin=outgoing.xreplace(dict(zip(Pi,-kappa*(phi-y*a))))
    target=-kappa*y*a.cross(phi)
    Lrobin=-kappa*(phi-y*a).dot(phi-y*a)/2
    ASigma=sp.symbols('Asigma1:4')
    normal_mix=sp.Matrix([-c*phi.dot(t*phi) for t in T])
    norm=a.cross(phi).dot(a.cross(phi))
    checks={
        'three_generators_antisymmetric':all(t.T==-t for t in T),
        'inner_product_trace_normalization':sp.Matrix(3,3,lambda i,j:-sp.trace(T[i]*T[j])/2)==sp.eye(3),
        'normal_connection_current_from_literal_kinetic_density':zero(current-reference),
        'conformal_normal_mixing_has_zero_torque':zero(normal_mix),
        'Robin_outgoing_current_equals_minus_kappa_y_cross':zero(robin-target),
        'alignment_norm_is_frame_invariant_Gram_determinant':zero(norm-(a.dot(a)*phi.dot(phi)-a.dot(phi)**2)),
        'literal_Robin_has_no_intrinsic_connection_current':all(sp.diff(Lrobin,z)==0 for z in ASigma),
    }
    # The subtraction of transported four-form equations is linear even for nonabelian A.
    dBplus,dBminus=[sp.Matrix(sp.symbols(prefix+'1:4')) for prefix in ('dBp','dBm')]
    Bplus,Bminus=[sp.Matrix(sp.symbols(prefix+'1:4')) for prefix in ('Bp','Bm')]
    def matrix(v):return sum((v[i]*T[i] for i in range(3)),sp.zeros(3))
    def cov(v,dv):return matrix(dv)+A*matrix(v)-matrix(v)*A
    difference=cov(Bplus,dBplus)-cov(Bminus,dBminus)
    checks['nonabelian_covariant_derivative_respects_common_gluing']=zero(difference-cov(Bplus-Bminus,dBplus-dBminus))
    glued=difference.xreplace({**dict(zip(Bplus,Bminus)),**dict(zip(dBplus,dBminus))})
    checks['smooth_B_and_connection_gluing_cancels_current_jump']=zero(glued)
    negatives={
        'omit_Robin_acceleration_torque':robin,
        'flip_one_outgoing_current_sign':2*outgoing,
        'identify_normal_current_with_zero_off_shell':current,
        'claim_no_conformally_transported_material_current':outgoing,
    }
    return dict(T=T,phi=phi,a=a,Pi=Pi,Z=Z,kappa=kappa,y=y,current=current,
                outgoing=outgoing,robin=robin,target=target,norm=norm,checks=checks,negative=negatives)

def derive_second_order():
    e=sp.Symbol('epsilon')
    a1,a2,p1,p2=[sp.Matrix(sp.symbols(prefix+'1:4')) for prefix in ('a1_','a2_','p1_','p2_')]
    a=e*a1+e*e*a2/2;p=e*p1+e*e*p2/2
    full=a.cross(p).applyfunc(sp.expand)
    coefficient=full.applyfunc(lambda x:x.coeff(e,2))
    av=sp.Matrix(sp.symbols('a1:4'));pv=sp.Matrix(sp.symbols('phi1:4'))
    jac=av.cross(pv).jacobian([*av,*pv])
    atzero=dict(zip([*av,*pv],[0]*6))
    aligned=dict(zip([*av,*pv],[1,0,0,2,0,0]))
    zero_rank=jac.subs(atzero).rank();aligned_rank=jac.subs(aligned).rank()
    checks={
        'vacuum_second_order_coefficient_is_a1_cross_phi1':zero(coefficient-a1.cross(p1)),
        'second_order_corrections_cannot_change_coefficient':not any(coefficient.has(x) for x in [*a2,*p2]),
        'first_order_alignment_row_at_vacuum_vanishes':zero(full.applyfunc(lambda x:x.coeff(e,1))),
        'alignment_map_Jacobian_rank_zero_at_origin':zero_rank==0,
        'alignment_map_Jacobian_rank_two_at_nonzero_aligned_point':aligned_rank==2,
        'two_alignment_reducibility_relations':zero(av.dot(av.cross(pv))) and zero(pv.dot(av.cross(pv))),
    }
    return dict(e=e,a1=a1,a2=a2,p1=p1,p2=p2,full=full,coefficient=coefficient,jacobian=jac,
                zero_rank=zero_rank,aligned_rank=aligned_rank,checks=checks)

def derive_port():
    radial,p,Z,kappa,y=sp.symbols('z_radial p Z kappa y',positive=True)
    o=sp.Symbol('Omega',positive=True)
    amp=sp.Symbol('amplitude')
    c=sp.Symbol('boundary_value')
    h=c*sp.exp(-p*radial)
    outward=-2*Z*sp.diff(h,radial).subs(radial,0)
    gain=kappa/(kappa+2*Z*p)
    robin=(outward+kappa*(c-y*amp)).subs(c,y*gain*amp)
    rho=sp.Symbol('psi_norm_squared',nonnegative=True);eps=sp.Symbol('epsilon',real=True)
    full_V4=eps**4*rho**2/(2*sp.sqrt(1+eps**4*rho**2))
    x,z=sp.symbols('x z',real=True)
    source=sp.cos(x)+sp.cos(2*z)
    a=sp.Matrix([sp.diff(source,x),0,sp.diff(source,z)])
    gains=(gain.subs({p:1,Z:1,kappa:1}),gain.subs({p:2,Z:1,kappa:1}))
    phi=y*sp.Matrix([gains[0]*a[0],0,gains[1]*a[2]])
    cross=a.cross(phi).applyfunc(sp.simplify)
    point=cross.subs({x:sp.pi/2,z:sp.pi/4})
    frozen=(-kappa*y*point).subs({kappa:1,y:sp.sqrt(3)})
    same_gain_phi=y*gains[0]*a
    checks={
        'exact_conformal_kinetic_weight_is_one':sp.simplify(o**5*o**(-2)*o**(-3))==1,
        'exact_conformal_potential_weight_is_one':sp.simplify(o**5*o**(-5))==1,
        'full_V4_amplitude_derivatives_zero_through_cubic':all(sp.diff(full_V4,eps,j).subs(eps,0)==0 for j in range(4)),
        'decaying_halfline_mode_solves_linear_static_bulk_equation':zero(sp.diff(h,radial,2)-p*p*h),
        'two_outgoing_material_momenta_are_2Zpc':zero(outward-2*Z*p*c),
        'exact_finite_Robin_response_gain':zero(robin),
        'frozen_two_wave_number_gains_are_different':gains==(sp.Rational(1,3),sp.Rational(1,5)),
        'two_direction_cross_coefficient':zero(cross-sp.Matrix([0,4*y*sp.sin(x)*sp.sin(2*z)/15,0])),
        'exact_frozen_current_residual_minus_four_fifths':frozen==sp.Matrix([0,-sp.Rational(4,5),0]),
        'each_single_direction_has_zero_torque':zero(a.cross(phi).subs(x,0)) and zero(a.cross(phi).subs(z,0)),
        'incorrect_common_gain_would_hide_the_obstruction':zero(a.cross(same_gain_phi)) and not zero(cross),
    }
    return dict(radial=radial,p=p,Z=Z,kappa=kappa,y=y,h=h,gain=gain,gains=gains,
                x=x,z=z,a=a,phi=phi,cross=cross,point=point,frozen=frozen,checks=checks)

def derive_localization():
    r,u,t,R,kappa,Z=sp.symbols('r u t R kappa Z',positive=True)
    poisson=u/(sp.pi**2*(u*u+r*r)**2)
    mass=4*sp.pi*sp.integrate(r*r*poisson,(r,0,sp.oo))
    majorant=u/(sp.pi**2*r**4)
    difference=sp.factor(majorant-poisson)
    expected_difference=u**3*(2*r*r+u*u)/(sp.pi**2*r**4*(r*r+u*u)**2)
    tail=4*sp.pi*sp.integrate(r*r*majorant,(r,R,sp.oo))
    mixture_tail=sp.integrate(kappa*sp.exp(-kappa*t)*tail.subs(u,2*Z*t),(t,0,sp.oo))
    response_error=7*mixture_tail.subs({Z:1,kappa:1})
    conservative_cross_error=56*sp.Rational(9,4)/(3*256)
    cross_margin=sp.Rational(4,15)-conservative_cross_error
    torque_margin=3*cross_margin
    checks={
        'Poisson_kernel_has_unit_R3_mass':sp.simplify(mass)==1,
        'Poisson_tail_majorant_pointwise_positive':zero(difference-expected_difference) and expected_difference.is_positive is True,
        'Poisson_tail_majorant_integral':zero(tail-4*u/(sp.pi*R)),
        'resolvent_mixture_tail_bound':zero(mixture_tail-8*Z/(sp.pi*kappa*R)),
        'localized_response_error_bound':zero(response_error-56/(sp.pi*R)),
        'cutoff_uniform_source_bound_below_seven':sp.sqrt(5)+4<7,
        'rational_pi_and_sqrt5_bounds':bool(sp.pi>3) and sp.Rational(9,4)**2>5,
        'radius_256_cross_error_below_21_over_128':conservative_cross_error==sp.Rational(21,128),
        'localized_cross_margin_197_over_1920':cross_margin==sp.Rational(197,1920),
        'localized_current_margin_197_over_640_positive':torque_margin==sp.Rational(197,640) and torque_margin>0,
    }
    return dict(poisson=poisson,mass=mass,majorant=majorant,difference=difference,
                r=r,u=u,R=R,kappa=kappa,Z=Z,tail=tail,mixture_tail=mixture_tail,
                cross_margin=cross_margin,torque_margin=torque_margin,
                checks={k:bool(v) for k,v in checks.items()})

def build_payload():
    source=load_sources();current=derive_current();second=derive_second_order();port=derive_port();local=derive_localization()
    checks={**current['checks'],**second['checks'],**port['checks'],**local['checks']}
    negative={k:not zero(v) for k,v in current['negative'].items()}
    if not all(checks.values()) or not all(negative.values()):raise CompatibilityError('calculation failed')
    out={'schema':SCHEMA,'sources':source,
         'implementation':{'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                           'test_sha256':hashlib.sha256(TEST.read_bytes()).hexdigest()},
         'checks':checks,'negative_controls':negative,
         'witness':{'source_lapse_first_order':'cos(x)+cos(2*z)',
                    'material_gains':[str(g) for g in port['gains']],
                    'cross_coefficient':[sp.sstr(v) for v in port['cross']],
                    'point_current_coefficient':[sp.sstr(v) for v in port['frozen']],
                    'localized_cutoff_radius':256,
                    'localized_current_lower_bound':str(local['torque_margin']),
                    'localized_domain':'compact smooth prescribed lapse; spatial finite energy per instant',
                    'rank_of_alignment_map_only':{'origin':second['zero_rank'],'aligned_nonzero':second['aligned_rank']}},
         'scope':{'literal_v5_2_bulk_BF_flux_Robin_rows_retained':True,
                  'smooth_transported_common_B_and_A_traces':True,
                  'nonzero_kappa_y_required':True,
                  'perturbative_background':'a0=phi0=0',
                  'witness':'prescribed material port, not a coupled Einstein solution',
                  'continuation_excluded':'C2 family with the displayed first-order data',
                  'fixed_direction_upstream_N8_lift_refuted':False},
         'decision':{'necessary_BF_Robin_torque_alignment_derived':True,
                     'two_direction_prescribed_port_C2_obstruction_checked':True,
                     'localized_spatial_finite_energy_port_obstruction_checked':True,
                     'full_N2_Dirac_rank_computed':False,'full_N4':False,'full_N7':False,
                     'unrestricted_nonlinear_material_port_promoted':False,
                     'full_P4':False,'B4':False,'B5':False,
                     'all_solutions_excluded_claimed':False,
                     'new_intrinsic_connection_current_adopted':False,
                     'repair_stability_certified':False}}
    out['calculation_digest']=digest(out)
    return out

def validate_payload(payload):
    expected=build_payload()
    if payload!=expected:raise CompatibilityError('receipt differs from fresh source-bound calculation')
    return expected

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write',action='store_true');group.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.verify:payload=validate_payload(read_json(OUTPUT.read_bytes()))
    else:
        payload=build_payload()
        with OUTPUT.open('x') as f:json.dump(payload,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    print(json.dumps({'checks_passed':len(payload['checks']),
                      'negative_controls':payload['negative_controls'],
                      'calculation_digest':payload['calculation_digest']},sort_keys=True))
    return 0

if __name__=='__main__':raise SystemExit(main())
