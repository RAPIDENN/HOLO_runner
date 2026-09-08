#!/usr/bin/env python3
"""Off-shell normal scalar Green term, moving density and admissible gluing.

The normal flux identities use the literal full-V4 scalar action. The moving
integral oracle is a separate generic nonlinear first-order density, not a
replacement action or a gravitational proof. No global gates are promoted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import sympy as sp

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_moving_scalar_green_lemma_v1.md'
TEST=HERE/'test_one_omega_moving_scalar_green_v1.py'
OUTPUT=HERE/'artifacts/one_omega_moving_scalar_green_v1.json'
CANDIDATE=HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
NOTE_SHA256='43e887eb8807605a9c62ad2202e9c6edcb03aa2bc2bc35e86f3e442abd0e511c'
CANDIDATE_SHA256='d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
ACTION_SHA256='3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a'
SCHEMA='holo.one-omega-moving-scalar-green.v1'

class MovingScalarError(ValueError):
    """The source, calculation, scope or receipt did not match."""

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
                                    ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def read_json(raw: bytes) -> dict:
    def pairs(items):
        result={}
        for k,v in items:
            if k in result: raise MovingScalarError('duplicate JSON key: '+k)
            result[k]=v
        return result
    def invalid(value):
        raise MovingScalarError('nonfinite JSON constant: '+value)
    try:
        out=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    except (UnicodeError,ValueError) as exc:
        raise MovingScalarError('invalid JSON') from exc
    if type(out) is not dict: raise MovingScalarError('JSON root is not an object')
    return out

def load_sources(note=NOTE,candidate=CANDIDATE):
    bnote,bcandidate=Path(note).read_bytes(),Path(candidate).read_bytes()
    if hashlib.sha256(bnote).hexdigest()!=NOTE_SHA256:
        raise MovingScalarError('lemma hash mismatch')
    if hashlib.sha256(bcandidate).hexdigest()!=CANDIDATE_SHA256:
        raise MovingScalarError('candidate hash mismatch')
    c=read_json(bcandidate)
    if c.get('schema')!='holo.one-omega-topological-so3-classical-v5-2-gate.v1':
        raise MovingScalarError('candidate schema mismatch')
    charter=c['exact_classical_charter']
    if digest(charter['exact_action'])!=ACTION_SHA256:
        raise MovingScalarError('literal action digest mismatch')
    if charter['exact_action']['full_V4']!='V4(r)=r^4/(2*sqrt(1+r^4))':
        raise MovingScalarError('full potential mismatch')
    return {'lemma_sha256':NOTE_SHA256,'candidate_sha256':CANDIDATE_SHA256,
            'exact_action_sha256':ACTION_SHA256,
            'reference_domain':charter['topology']['reference_domain_formulation'],
            'no_source_gate_promotions_inherited':True}

def zero(value):
    if isinstance(value,sp.MatrixBase):return all(sp.cancel(x)==0 for x in value)
    return sp.cancel(value)==0

def derive_normal_flux():
    o,G,Z,m=sp.symbols('Omega G Z m',positive=True)
    phi=sp.Matrix(sp.symbols('phi1:4',real=True))
    v=sp.Matrix(sp.symbols('v0:4',real=True))
    tangents=sp.Matrix(4,4,lambda a,mu:sp.Symbol(f't{a}_{mu}',real=True))
    C=sp.diag(G,Z,Z,Z)
    C[0,0]+=9*Z*(phi.dot(phi))/(4*o**2)
    for a in range(3):C[0,a+1]=C[a+1,0]=3*Z*phi[a]/(2*o)
    U=sp.Function('U')(o)
    r4=o**6*phi.dot(phi)**2
    V=U+Z*m*m*r4/(2*o**5*sp.sqrt(1+r4))
    eta=(-1,1,1,1)
    normal=(v.T*C*v)[0]
    tangent=sum(eta[mu]*(tangents[:,mu].T*C*tangents[:,mu])[0] for mu in range(4))
    L=-normal/2-tangent/2-V
    p=sp.Matrix([sp.diff(L,va) for va in v])
    Pn=v[1:4,0]+3*phi*v[0]/(2*o)
    p_expected=sp.Matrix([-G*v[0]-3*Z*phi.dot(Pn)/(2*o),*(-Z*Pn)])
    inverse_nn=sp.Symbol('inverse_g_nn',positive=True)
    metric_L=-inverse_nn*normal/2-tangent/2-V
    # Hilbert convention T_ab=-2 dL/dg^ab+g_ab L; g_nn=1 here.
    Tnn=-2*sp.diff(metric_L,inverse_nn).subs(inverse_nn,1)+L
    normal_legendre=L-p.dot(v)
    kinetic_normal=G*v[0]**2+Z*Pn.dot(Pn)
    literal_tangent=0
    for mu in range(4):
        P=tangents[1:4,mu]+3*phi*tangents[0,mu]/(2*o)
        literal_tangent+=eta[mu]*(G*tangents[0,mu]**2+Z*P.dot(P))
    old=sp.Matrix([o,*phi]);new=sp.Matrix([o,*(o**sp.Rational(3,2)*phi)])
    J=new.jacobian(old)
    Cnew=sp.diag(G,Z/o**3,Z/o**3,Z/o**3)
    vnew=J*v;pnew=-Cnew*vnew
    delta=sp.Matrix(sp.symbols('Delta0:4',real=True))
    bad_p=p.copy();bad_p[0]=-G*v[0]
    checks={
        'literal_normal_conformal_derivative':zero(normal-kinetic_normal),
        'all_tangential_Lorentz_derivatives_retained':zero(tangent-literal_tangent),
        'all_four_outward_Green_momenta':zero(p-p_expected),
        'normal_Hilbert_stress_is_L_minus_p_v':zero(Tnn-normal_legendre),
        'coordinate_field_metric_pullback':zero(J.T*Cnew*J-C),
        'normal_momentum_covector_transform':zero(p-J.T*pnew),
        'material_trace_Green_pairing_invariant':zero(p.dot(delta)-pnew.dot(J*delta)),
        'normal_Legendre_pairing_invariant':zero(p.dot(v)-pnew.dot(vnew)),
    }
    return dict(o=o,G=G,Z=Z,m=m,phi=phi,v=v,tangents=tangents,C=C,V=V,L=L,p=p,
                Tnn=Tnn,legendre=normal_legendre,J=J,Cnew=Cnew,checks=checks,
                negative={'omit_mixed_Omega_momentum':sp.expand((bad_p-p).dot(delta)),
                          'replace_normal_Legendre_by_L':sp.expand(L-Tnn)})

def derive_moving_jets():
    """Differentiate a genuinely nonlinear pulled-back density directly."""
    q=sp.Matrix(sp.symbols('q0:2',real=True));v=sp.Matrix(sp.symbols('v0:2',real=True))
    acc=sp.Matrix(sp.symbols('a0:2',real=True))
    delta=sp.Matrix(sp.symbols('dq0:2',real=True));deltaprime=sp.Matrix(sp.symbols('dqp0:2',real=True))
    x,epsilon,xi,xiprime=sp.symbols('x epsilon xi xiprime',real=True)
    C=sp.Matrix([[1+q[0]**2,q[0]*q[1]/3],[q[0]*q[1]/3,2+q[1]**2]])
    V=(q.dot(q))**2/4+x*q[0]*q[1]
    L=-(v.T*C*v)[0]/2-V
    def total(expr):
        return sp.diff(expr,x)+sum(sp.diff(expr,q[a])*v[a]+sp.diff(expr,v[a])*acc[a]
            +sp.diff(expr,delta[a])*deltaprime[a] for a in range(2))+sp.diff(expr,xi)*xiprime
    p=sp.Matrix([sp.diff(L,z) for z in v])
    E=sp.Matrix([sp.diff(L,q[a])-total(p[a]) for a in range(2)])
    H=L-p.dot(v)
    jac=1+epsilon*xiprime
    mapping={x:x+epsilon*xi}
    mapping.update({q[a]:q[a]+epsilon*delta[a] for a in range(2)})
    mapping.update({v[a]:(v[a]+epsilon*deltaprime[a])/jac for a in range(2)})
    pulled=jac*L.xreplace(mapping)
    direct=sp.diff(pulled,epsilon).subs(epsilon,0).expand()
    green=p.dot(delta)+xi*H
    expected=E.dot(delta-xi*v)+total(green)
    no_material_velocity=E.dot(delta)+total(green)
    double_transgression=expected+total(xi*L)
    checks={
        'direct_pulled_density_equals_off_shell_Euler_Green':zero(direct-expected),
        'normal_H_derivative_retains_Euler_times_velocity':zero(total(H)-sp.diff(L,x)-E.dot(v)),
        'embedding_Euler_row_is_minus_E_times_velocity':not zero(E.dot(v)),
        'nonzero_bulk_Euler_not_imposed':E!=sp.zeros(2,1),
        'nonconstant_field_metric_not_frozen':not zero(sp.diff(C[0,0],q[0])),
        'explicit_coordinate_dependence_retained':not zero(sp.diff(L,x)),
    }
    return dict(q=q,v=v,acc=acc,delta=delta,x=x,xi=xi,xiprime=xiprime,
                L=L,E=E,p=p,H=H,direct=direct,green=green,checks=checks,
                negative={'omit_material_velocity_in_Euler':sp.expand(direct-no_material_velocity),
                          'double_domain_transgression':sp.expand(direct-double_transgression)})

def derive_gluing():
    vminus=sp.Matrix(sp.symbols('vm0:4'));vplus=sp.Matrix(sp.symbols('vp0:4'))
    pminus=sp.Matrix(sp.symbols('pm0:4'));pplus=sp.Matrix(sp.symbols('pp0:4'))
    delta=sp.Matrix(sp.symbols('Delta0:4'));wall=sp.Matrix(sp.symbols('ellq0:4'))
    f,Lm,Lp=sp.symbols('f Lminus Lplus')
    dm=delta-f*vminus;dp=delta-f*vplus
    left=pminus.dot(dm)-pplus.dot(dp)+f*(Lm-Lp)+wall.dot(delta)
    right=(pminus-pplus+wall).dot(delta)+f*((Lm-pminus.dot(vminus))-(Lp-pplus.dot(vplus)))
    gluing=(dm+f*vminus)-(dp+f*vplus)
    bad_frozen=f*(vminus-vplus)
    bad_orientation=pminus.dot(dm)+pplus.dot(dp)+f*(Lm+Lp)+wall.dot(delta)
    return dict(left=left,right=right,f=f,gluing=gluing,pminus=pminus,pplus=pplus,
                vminus=vminus,vplus=vplus,delta=delta,
                checks={'four_common_material_trace_equations':zero(gluing),
                        'two_sided_Green_and_normal_jump':zero(left-right)},
                negative={'frozen_bulk_generic_moving_gluing':bad_frozen,
                          'same_outward_incidence_on_both_sides':sp.expand(left-bad_orientation)})

def build_payload():
    sources=load_sources()
    flux,jets,gluing=derive_normal_flux(),derive_moving_jets(),derive_gluing()
    checks={**flux['checks'],**jets['checks'],**gluing['checks']}
    negatives={k:not zero(v) for part in (flux,jets,gluing) for k,v in part['negative'].items()}
    if not all(checks.values()) or not all(negatives.values()):
        raise MovingScalarError('calculation or negative control failed')
    result={'schema':SCHEMA,'sources':sources,
            'implementation':{'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                              'test_sha256':hashlib.sha256(TEST.read_bytes()).hexdigest()},
            'checks':checks,'negative_controls':negatives,
            'formulas':{'C':[[sp.sstr(x) for x in flux['C'][i,:]] for i in range(4)],
                        'p':list(map(sp.sstr,flux['p'])),'full_V':sp.sstr(flux['V']),
                        'normal_force':'-[T_nn] in common-normal orientation',
                        'material_trace_row':'p_minus-p_plus+ell_q',
                        'moving_density':'E.(Delta q-xi*q_prime)+d[p.Delta q+xi*(L-p.q_prime)]'},
            'scope':{'scalar_part_only':True,'exact_full_V4_normal_flux':True,
                     'off_shell':True,'moving_density_oracle':'generic nonlinear first-order density with two fields',
                     'common_trace_variations_required':True,
                     'second_domain_transgression_added':False},
            'decision':{'normal_scalar_Green_and_Legendre_identity_checked':True,
                        'two_sided_scalar_gluing_tangent_checked':True,
                        'complete_gravitational_moving_variation':False,
                        'complete_ADM_Robin_frame_Euler_rows':False,
                        'full_N4':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}
    result['calculation_digest']=digest(result)
    return result

def validate_payload(payload):
    expected=build_payload()
    if payload!=expected:raise MovingScalarError('receipt differs from fresh source-bound calculation')
    return expected

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true');mode.add_argument('--verify',action='store_true')
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
