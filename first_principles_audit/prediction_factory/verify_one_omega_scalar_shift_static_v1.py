"""Companion algebra for scalar constraint pivots and all-q static invertibility.

The infinite-dimensional arguments are in the two pinned reviewed notes.
This verifier recomputes the matrix identities, rational bounds and polynomial
interval certificates. It never promotes the final dynamic scalar factor.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp
if __package__:
    from . import verify_one_omega_topological_sector_reduction_v1 as sectors
    from . import verify_one_omega_variational_dtn_v1 as variational
else:
    import verify_one_omega_topological_sector_reduction_v1 as sectors
    import verify_one_omega_variational_dtn_v1 as variational

HERE=Path(__file__).resolve().parent
OUTPUT=HERE/'artifacts/one_omega_scalar_shift_static_v1.json'
TEST=HERE/'test_one_omega_scalar_shift_static_v1.py'
PROOFS={'one_omega_scalar_shift_pivot_lemma_v1.md':'7524e53094aa71db8ff931506b00f027cd72ec8575c7a5aa56d17a719aef502e',
        'one_omega_scalar_static_invertibility_lemma_v1.md':'a2903edae1873a9f61860ce6fa1c0ed61015885592275f2c54203553df929722'}
VARIATIONAL_SHA='4ca0b1a1859610c6b3f472bf9704b83f23f1b740900ab387f844bcb985101095'
CANDIDATE_SHA='d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
SCHEMA='holo.one-omega-scalar-shift-static.v1'
canonical_digest=sectors.canonical_digest


def taylor_lower(x,order):
    return sum(x**j/sp.factorial(j) for j in range(order+1))


def derive_model():
    base=sectors.derive_model();P=base['parameters'];w,q=base['frequency'],base['q'];z=q*q-w*w
    M,G,k,Mb,lam,eta,xi,KT,Kv,kap,y,Z5,beta,b4,pm=(P[n] for n in ('M5c','G','k_inf','Mb2','lambda_K','eta','xi','K_T','K_v','kappa_hat','y','Z5','beta','B4bar','p_material'))
    C0=M*sp.exp(G/(6*M))/k;mass=M*KT/z;A=Mb*(1-lam);B=Mb*(1-3*lam)-2*mass
    Pi=base['Pi_R'];Delta=base['Delta_beta'];E=Mb*eta-Pi;C=6*C0-6*mass-Delta/z
    reference=sp.Matrix([[E*q*q,0,2*q*q*(Mb*xi+mass)],
                         [0,A*q*q,w*q*B],
                         [2*q*q*(Mb*xi+mass),w*q*B,3*w*w*B+2*q*q*(Mb*xi+mass)-Mb*b4*q**4/k**2]])
    u=sp.Matrix([q*q,-w*q,2*q*q-3*w*w])
    reference+=C*u*u.T/(9*z)
    H=base['scalar_3x3']
    regroup=sectors.clean(H-reference)
    hN=q*q*(A+w*w*C/(9*z))
    hn=q*q*(E+A*q*q*C/(9*A*z+w*w*C))
    lapse_actual=H[0,0]-H[0,1]*H[1,0]/H[1,1]
    residuals={'complete_matrix_regrouping':regroup,
               'shift_pivot':sp.cancel(H[1,1]-hN),
               'lapse_pivot_after_shift':sp.cancel(lapse_actual-hn)}
    # Independent abstract matrix for static intervals and scalar determinant.
    Q,m,c,EE,BB=sp.symbols('Q m c E B',positive=True);PP=2+m
    static=sp.Matrix([[EE+c,2*(PP+c)],[2*(PP+c),2*PP+4*c-BB]])
    F=2*PP*(EE-2*PP)+c*(4*EE-6*PP)-BB*(EE+c)
    residuals['static_two_by_two_determinant']=sp.expand(static.det()-F)
    static_from_source=H.extract([0,2],[0,2]).subs(w,0)/q**2
    static_expected=sp.Matrix([[E+C.subs(w,0)/9,2*(Mb*xi+mass.subs(w,0)+C.subs(w,0)/9)],
        [2*(Mb*xi+mass.subs(w,0)+C.subs(w,0)/9),2*(Mb*xi+mass.subs(w,0))+4*C.subs(w,0)/9-Mb*b4*q*q/k**2]])
    residuals['static_matrix_from_full_response']=sectors.clean(static_from_source-static_expected)
    # RHP positivity of one resolvent atom and exact pivot rearrangement.
    sigma=sp.Symbol('sigma',positive=True);tau=sp.Symbol('tau',real=True)
    ell=sp.Symbol('spectral_lambda',nonnegative=True);ss=sigma+sp.I*tau
    den=ss*ss+Q*Q+ell
    atom_numerator=sp.simplify(sp.re(sp.expand_complex(ss*sp.conjugate(den))))
    residuals['positive_resolvent_atom']=sp.expand(atom_numerator-sigma*(sigma*sigma+tau*tau+Q*Q+ell))
    aa,cc,ff=sp.symbols('A Cinf F',positive=True)
    shift_direct=ss*(aa-ss*ss*ff/9)
    shift_reference=(aa-cc/9)*ss+ss*(cc-(ss*ss+Q*Q)*ff+Q*Q*ff)/9
    residuals['shift_positive_real_rearrangement']=sp.expand(shift_direct-shift_reference)
    # Cauchy gap after combining the finite-mass inequality with Re(Y).
    atom_squared=(sigma*sigma+tau*tau)
    cauchy_slack=sp.expand(atom_numerator/sigma-atom_squared)
    # Frozen coefficients remain exact decimal rationals.
    E0=sp.Rational('6.214027581601698');lambda0=sp.Rational('-.5535068954004245')
    m_lower=2/(2+Q);ee=E0-6*Q/(1+2*Q);bb=sp.Rational(8,5)*Q*Q
    f0=sp.factor(F.subs({c:0,EE:ee,BB:bb}))
    f1=sp.factor(F.subs({c:sp.Rational(2,3)*(sp.Rational(5,4)-m),EE:ee,BB:bb}))
    derivatives={'c_zero':sp.factor(sp.diff(f0,m)), 'c_upper':sp.factor(sp.diff(f1,m))}
    residuals['upper_endpoint_derivative']=sp.cancel(derivatives['c_upper']-(sp.Rational(2,3)*(bb-ee)-13))
    x=sp.Symbol('offset_from_one_tenth',nonnegative=True)
    endpoints={}
    for name,Fm in [('c_zero',f0),('c_upper',f1)]:
        expr=sp.factor(Fm.subs(m,m_lower));num,denom=sp.fraction(expr)
        coeffs=sp.Poly(sp.expand(num.subs(Q,x+sp.Rational(1,10))),x).all_coeffs()
        endpoints[name]={'expression':expr,'numerator':num,'denominator':denom,
                         'shifted_coefficients':coeffs,
                         'all_coefficients_strictly_negative':all(v<0 for v in coeffs),
                         'positive_denominator':denom.is_positive is True}
    ir_lower=2*(2+5*(taylor_lower(sp.Rational(1,5),12)-1))-E0
    log_witness=taylor_lower(sp.Rational(231,100),12)-10
    small_margin=2*sp.Rational(29,10)*(-sp.Rational(107,25))+25*sp.Rational(13,50)
    checks={name:sectors.zero(value) for name,value in residuals.items()}
    checks.update({'exact_decimal_IR_margin_positive':ir_lower>0,
                   'log_ten_less_than_231_over_100':log_witness>0,
                   'exponential_cube_bound_less_than_two':sp.Rational(5,4)**3<2,
                   'small_q_TT_deficit_bound':(sp.Rational(5,4)+sp.Rational(231,100))/10<sp.Rational(9,25),
                   'small_q_C_bound':(6*sp.Rational(9,25)+(sp.Rational(3,20)+sp.Rational(9,8))/10)/9<sp.Rational(13,50),
                   'small_q_P_lower_bound':3-sp.Rational(9,250)>sp.Rational(29,10),
                   'small_q_determinant_negative':small_margin==-sp.Rational(4581,250),
                   'shift_strict_frozen_margin':2*(1-lambda0)>3,
                   'lapse_strict_frozen_margin':E0-3>3,
                   'large_q_E_minus_two_P_negative':sp.Rational(77,20)-4<0,
                   'large_q_c_coefficient_negative':4*sp.Rational(77,20)-12-sp.Rational(32,5)<0,
                   **{'endpoint_'+n+'_negative':v['all_coefficients_strictly_negative'] and v['positive_denominator'] for n,v in endpoints.items()}})
    checks={name:bool(value) for name,value in checks.items()}
    return {'residuals':residuals,'checks':checks,'static_matrix':static,'static_determinant':F,
            'endpoint_certificates':endpoints,'endpoint_derivatives':derivatives,
            'rational_IR_lower_margin':ir_lower,'rational_log_witness':log_witness,
            'small_q_determinant_upper_coefficient':small_margin,'resolvent_atom_positive_numerator':atom_numerator,
            'Cauchy_atom_slack':cauchy_slack,
            'kernel_mass_identity':'Cinf=6*m0+Ns; exact integrals, not frozen rounded metadata',
            'determinant_factorization':'det H5=PC*PD*HNN*Hnn_after_N*S_zeta',
            'scope':{'q':'q>0','static':'s=0, exact finite-energy branch',
                     'dynamic_constraint_pivots':'Re(s)>0, q>0',
                     'final_dynamic_scalar_factor_certified':False,
                     'formal_Hilbert_space_proof_checking':False}}


def build_payload():
    for name,digest in PROOFS.items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=digest:raise ValueError('reviewed proof changed')
    variational.validate_payload(sectors.assembly._load_receipt(variational.OUTPUT,VARIATIONAL_SHA))
    candidate=HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
    if hashlib.sha256(candidate.read_bytes()).hexdigest()!=CANDIDATE_SHA:raise ValueError('candidate changed')
    model=derive_model()
    if not all(model['checks'].values()):raise ValueError('constraint/static algebra check failed')
    files=[Path(__file__),TEST,*(HERE/name for name in PROOFS)]
    payload={'schema':SCHEMA,'sources':{'variational':VARIATIONAL_SHA,'candidate':CANDIDATE_SHA,'proofs':PROOFS},
             'model':sectors.assembly.scalar._serialize(model),'checks':model['checks'],
             'decision':{'shift_pivot_has_no_RHP_zero':True,'lapse_after_shift_has_no_RHP_zero':True,
                         'all_four_eliminated_pivots_preserved_and_nonzero_in_RHP':True,
                         'static_scalar_matrix_invertible_for_every_q_positive':True,
                         'static_final_scalar_Schur_strictly_negative':True,
                         'final_dynamic_scalar_factor_has_no_RHP_zero':False,
                         'q_zero_scalar_certified':False,'formal_machine_checked_analysis':False,
                         'full_physical_mode_count':False,'BF_and_embedding_closed':False,
                         'full_N7':False,'full_P4':False,'B4':False,'B5':False},
             'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:raise ValueError('constraint/static schema mismatch')
    if payload.get('calculation_digest')!=canonical_digest({k:v for k,v in payload.items() if k!='calculation_digest'}):raise ValueError('constraint/static digest mismatch')
    if payload!=build_payload():raise ValueError('constraint/static receipt differs from fresh derivation')


def main():
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path);modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args()
    if args.write:
        payload=build_payload()
        with args.write.open('x') as f:json.dump(payload,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
    else:
        payload=sectors.assembly.source.source_oracle._read_json(args.verify.read_bytes());validate_payload(payload)
    print(json.dumps({'checks_passed':sum(payload['checks'].values()),'calculation_digest':payload['calculation_digest']}))


if __name__=='__main__':main()
