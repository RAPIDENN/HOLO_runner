"""Exact companion for the reviewed scalar spectral-energy realization.

Per-atom identities hold before integration against the actual positive
spectral measures. Finite algebra checks the coefficients and norm bounds;
the pinned note supplies the closed-form-domain and infinite-dimensional
energy argument. No nonlinear, global BF, or full N7/P4 gate is inherited.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp
if __package__:
    from . import verify_one_omega_scalar_shift_static_v1 as static
else:
    import verify_one_omega_scalar_shift_static_v1 as static
HERE=Path(__file__).resolve().parent
OUTPUT=HERE/'artifacts/one_omega_scalar_spectral_energy_v1.json'
PROOF=HERE/'one_omega_scalar_spectral_energy_lemma_v1.md'
TEST=HERE/'test_one_omega_scalar_spectral_energy_v1.py'
PROOF_SHA='acfe9cb3c6b021ff987a8d6e363b2ce8ffc26bb3d8ae2d362bea058c71b3e432'
STATIC_SHA='8ca7d81f1dcb645147d694d68fc32c0cc50483d67f2b7353caaecf31a22f190e'
SCHEMA='holo.one-omega-scalar-spectral-energy.v1'
canonical_digest=static.canonical_digest


def derive_model():
    w,q,n,N,zz,XT,Yb=sp.symbols('w q lapse shift zeta X_tensor Y_beta',real=True)
    z=q*q-w*w
    ellT,ellB,rhoT,rhoB,b,C0,A,Bstar,kap,y,Z5=sp.symbols('lambda_T lambda_beta rho_T rho_beta b C0 A Bstar kappa y Z5',positive=True)
    lam=sp.Symbol('lambda_K',real=True);p=sp.Symbol('p')
    U=q*q*(n-zz)-w*q*N;u=U+3*z*zz;EH=2*zz*U+3*z*zz*zz
    gT=sp.sqrt(2*rhoT/3);gb=sp.sqrt(rhoB)/3
    # These are measure-density identities, not a discrete approximation.
    TT_original=rhoT*ellT*EH/(ellT+z)+rhoT*u*u/(3*(ellT+z))
    TT_realized=rhoT*EH+gT*gT*U*U/(2*(ellT+z))
    beta_original=-(ellB+z)*(Yb+3*gb*zz)**2/2+gb*(Yb+3*gb*zz)*u
    beta_shifted=-(ellB+z)*Yb**2/2+gb*Yb*(U-3*ellB*zz)+rhoB*EH/6-rhoB*ellB*zz*zz/2
    residuals={'TT_measure_density_realization':sp.cancel(TT_original-TT_realized),
               'beta_admissible_field_shift':sp.expand(beta_original-beta_shifted),
               'TT_auxiliary_stationary_value':sp.cancel((-(ellT+z)*XT**2/2+gT*XT*U).subs(XT,gT*U/(ellT+z))-gT*gT*U*U/(2*(ellT+z)))}
    # Shift is kept as an algebraic constraint until the complete local kinetic form exists.
    Lkin=(3*Bstar*w*w*zz*zz+(w*w)*(XT*XT+Yb*Yb)+A*q*q*N*N)/2+w*q*N*(Bstar*zz-gT*XT-gb*Yb)
    Nsol=-w*(Bstar*zz-gT*XT-gb*Yb)/(A*q)
    after=sp.expand(Lkin.subs(N,Nsol)/w**2)
    fields=sp.Matrix([zz,XT,Yb]);direction=sp.Matrix([Bstar,-gT,-gb])
    diag=sp.diag(3*Bstar,1,1)
    K=sp.hessian(after,fields)
    residuals['kinetic_after_shift']=K-diag+direction*direction.T/A
    threshold=sp.cancel((direction.T*diag.inv()*direction)[0])
    residuals['weighted_Cauchy_threshold']=sp.cancel(threshold-(Bstar/3+2*rhoT/3+rhoB/9))
    # Exact BPS mass identities, independent of the rounded selected M4 metadata.
    substitutions={rhoB:6*(C0-rhoT),Bstar:b*(1-3*lam)-2*C0,A:b*(1-lam)}
    gap=sp.simplify((A-threshold).subs(substitutions,simultaneous=True))
    residuals['kinetic_margin_two_b_over_three']=sp.expand(gap-2*b/3)
    residuals['local_EH_mass_sum']=sp.expand((rhoT+rhoB/6-C0).subs(rhoB,6*(C0-rhoT)))
    residuals['coupling_norm_mass_sum']=sp.expand((2*rhoT/3+rhoB/9-2*C0/3).subs(rhoB,6*(C0-rhoT)))
    # Independent one-field Robin Schur realizes the frequency-dependent lapse coefficient.
    eta=sp.Symbol('eta',positive=True);phi=sp.Symbol('phi',real=True)
    Einf=b*eta-kap*y*y;PC=kap+2*Z5*p
    Lmaterial=Einf*q*q*n*n/2+kap*y*q*n*phi-PC*phi*phi/2
    phi_sol=kap*y*q*n/PC
    Pi=2*Z5*kap*y*y*p/PC
    residuals['material_Robin_lapse_realization']=sp.cancel(Lmaterial.subs(phi,phi_sol)-(b*eta-Pi)*q*q*n*n/2)
    # Completion of squares in a generic static block proves the sign bookkeeping.
    aa,hh,kk=sp.symbols('lapse_positive interior_positive final_positive',positive=True)
    bb,cc,dd,xx=sp.symbols('lapse_zeta lapse_interior zeta_interior interior',real=True)
    # H = a n²+2n(b*z+c*x)+h0*z²+2d*z*x-k*x².
    h0=sp.Symbol('unreduced_zeta_static',real=True)
    L2=aa*n*n+2*n*(bb*zz+cc*xx)+h0*zz*zz+2*dd*zz*xx-kk*xx*xx
    nsol=-(bb*zz+cc*xx)/aa
    V=-L2.subs(n,nsol);Kint=kk+cc*cc/aa;cross=-dd+bb*cc/aa
    D=-h0+bb*bb/aa-cross*cross/Kint
    residuals['static_positive_completion']=sp.cancel(V-(Kint*(xx+cross*zz/Kint)**2+D*zz*zz))
    hnn_after=aa+cc*cc/kk;hnz=bb+cc*dd/kk;hzz=h0+dd*dd/kk
    residuals['static_Schur_order_independence']=sp.cancel(D+(hzz-hnz*hnz/hnn_after))
    # Infinite-dimensional energy contradiction uses these two strictly positive scalar forms.
    sigma=sp.Symbol('sigma',positive=True);tau=sp.Symbol('tau',real=True)
    kinetic=sp.Symbol('kinetic_norm',positive=True);potential=sp.Symbol('potential_form',positive=True);s=sigma+sp.I*tau
    real_energy=sp.simplify(sp.re(sp.expand_complex((s*s*kinetic+potential)/s)))
    energy_reference=sigma*(kinetic+potential/(sigma*sigma+tau*tau))
    residuals['RHP_rotated_energy']=sp.cancel(real_energy-energy_reference)
    # The selected decimals supply strict kinetic/lapse hypotheses.
    lambda0=sp.Rational('-.5535068954004245');E0=sp.Rational('6.214027581601698')
    A_lower=sp.Integer(3);A_upper=sp.Rational(13,4);B_lower=sp.Rational(5,2)
    checks={name:static.sectors.zero(value) for name,value in residuals.items()}
    checks.update({'frozen_A_between_three_and_thirteen_fourths':A_lower<2*(1-lambda0)<A_upper,
                   'frozen_Bstar_lower_bound':2*(1-3*lambda0)-sp.Rational(5,2)>B_lower,
                   'frozen_Einf_greater_than_three':E0-3>3,
                   'uniform_kinetic_relative_gap':(sp.Rational(4,3)/A_upper)==sp.Rational(16,39),
                   'rotated_energy_strictly_positive':energy_reference.is_positive is True})
    checks={name:bool(value) for name,value in checks.items()}
    return {'symbols':{'w':w,'q':q,'n':n,'N':N,'zeta':zz,'X_tensor':XT,'Y_beta':Yb,
                       'lambda_T':ellT,'lambda_beta':ellB,'rho_T':rhoT,'rho_beta':rhoB,
                       'A':A,'Bstar':Bstar,'C0':C0,'b':b,'lambda_K':lam},
            'U':U,'u':u,'EH_scalar_unit':EH,'TT_original':TT_original,'TT_realized':TT_realized,
            'beta_original_after_shift':beta_original,'beta_realized':beta_shifted,
            'kinetic_matrix':K,'kinetic_diagonal':diag,'kinetic_rank_one_direction':direction,
            'kinetic_Cauchy_threshold':threshold,'exact_kinetic_gap':gap,
            'static_potential_completion':{'interior':Kint,'cross':cross,'last_Schur':D},
            'RHP_energy':real_energy,'residuals':residuals,'checks':checks,
            'measure_conditions':{'TT_mass':'m0','beta_mass':'Ns','beta_first_moment':'beta',
                                  'TT_first_moment_required':False,'mass_identity':'6*m0+Ns=6*C0'},
            'scope':{'all_spatial_momenta_q_positive':True,'all_frequencies_Re_s_positive':True,
                     'q_zero_in_this_chart':False,'finite_atoms_used_as_global_proof':False,
                     'formal_Hilbert_proof_objects_checked':False}}


def build_payload():
    if hashlib.sha256(PROOF.read_bytes()).hexdigest()!=PROOF_SHA:raise ValueError('reviewed spectral-energy proof changed')
    static.validate_payload(static.sectors.assembly._load_receipt(static.OUTPUT,STATIC_SHA))
    model=derive_model()
    if not all(model['checks'].values()):raise ValueError('spectral-energy identity failed')
    files=[Path(__file__),TEST,PROOF]
    payload={'schema':SCHEMA,'sources':{'constraint_static_receipt':STATIC_SHA,'reviewed_proof':PROOF_SHA},
             'model':static.sectors.assembly.scalar._serialize({k:v for k,v in model.items() if k!='symbols'}),
             'checks':model['checks'],
             'decision':{'actual_scalar_response_has_positive_energy_realization_for_q_positive':True,
                         'final_scalar_factor_has_no_RHP_zero_for_every_q_positive':True,
                         'negative_final_scalar_Schur_divided_by_s_strictly_positive_real':True,
                         'full_five_field_scalar_boundary_matrix_has_no_RHP_zero_for_q_positive':True,
                         'q_zero_scalar_certified':False,'imaginary_axis_pole_limits_certified':False,
                         'complete_nonlinear_constraint_reduction':False,'full_physical_mode_count':False,
                         'BF_global_and_embedding_sectors_closed':False,'formal_machine_checked_analysis':False,
                         'full_N7':False,'full_P4':False,'B4':False,'B5':False},
             'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    payload['calculation_digest']=canonical_digest(payload);return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:raise ValueError('spectral-energy schema mismatch')
    if payload.get('calculation_digest')!=canonical_digest({k:v for k,v in payload.items() if k!='calculation_digest'}):raise ValueError('spectral-energy digest mismatch')
    if payload!=build_payload():raise ValueError('spectral-energy receipt differs from fresh derivation')


def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write',nargs='?',const=OUTPUT,type=Path);group.add_argument('--verify',nargs='?',const=OUTPUT,type=Path);args=parser.parse_args()
    if args.write:
        payload=build_payload()
        with args.write.open('x') as f:json.dump(payload,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
    else:
        payload=static.sectors.assembly.source.source_oracle._read_json(args.verify.read_bytes());validate_payload(payload)
    print(json.dumps({'checks_passed':sum(payload['checks'].values()),'calculation_digest':payload['calculation_digest']}))


if __name__=='__main__':main()
