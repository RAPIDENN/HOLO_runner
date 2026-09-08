"""Algebraic companion to the selected finite-energy DtN existence proof.

The infinite-dimensional argument is in one_omega_variational_dtn_lemma_v1.md.
This module verifies its coefficient identities, positivity and BPS weight
conditions. It is not a formal proof assistant for Hilbert-space theorems.
"""
from __future__ import annotations
import sympy as sp


def derive_model():
    sigma=sp.Symbol('sigma',positive=True);tau=sp.Symbol('tau',real=True)
    q=sp.Symbol('q',nonnegative=True);s=sigma+sp.I*tau
    Er,Em=sp.symbols('E_radial E_weighted',nonnegative=True)
    omega,k,a=sp.symbols('Omega k deformation',positive=True)
    rho=sigma**2+tau**2;m=rho+q**2
    form=Er+(s**2+q**2)*Em
    real_part=sp.simplify(sp.expand_complex(sp.re(form/s)))
    coercive=sigma*(Er+m*Em)/rho
    mass=sp.Symbol('mass_coefficient',positive=True)
    c=sp.Symbol('coercive_prefactor',positive=True)
    branch_low=c*(Er+mass*Em)-c*mass*(Er+Em)
    branch_high=c*(Er+mass*Em)-c*(Er+Em)
    slack=sp.Symbol('slack',nonnegative=True)
    low_positive=sp.factor(branch_low.subs(mass,1/(1+slack)))
    high_positive=sp.factor(branch_high.subs(mass,1+slack))
    modulus_gap=sp.simplify(m**2-sp.expand_complex((s**2+q**2)*sp.conjugate(s**2+q**2)))
    weights={}
    cutoff=sp.Symbol('lower_cutoff',positive=True)
    for name,powerP,powerW in [('tensor',4,2),('scalar_R',6,4)]:
        P=omega**powerP;W=omega**powerW
        weights[name]={'P':P,'W':W,'P_over_W':sp.cancel(P/W),'P_UV':P.subs(omega,1),
                       'W_radial_integrand':sp.exp(a*omega**2)*omega**(powerW-1)/k,
                       'W_integral_upper_bound':sp.exp(a)/(k*powerW),
                       'inverse_P_radial_integrand':sp.exp(a*omega**2)*omega**(-powerP-1)/k,
                       'inverse_P_integral_lower_bound':(cutoff**(-powerP)-1)/(k*powerP),
                       'inverse_P_integral_diverges':sp.limit((cutoff**(-powerP)-1)/(k*powerP),cutoff,0,dir='+')==sp.oo}
    # Weighted cutoff estimate with 0<=chi<=1 and |chi'|<=Cchi.
    Cchi=sp.Symbol('cutoff_derivative_bound',positive=True)
    cutoff_bound=2*Er+(1+2*Cchi**2)*Em
    residuals={'rotated_form_real_part':sp.simplify(real_part-coercive),
               'low_mass_coercivity_branch':sp.expand(branch_low-c*(1-mass)*Er),
               'high_mass_coercivity_branch':sp.expand(branch_high-c*(mass-1)*Em),
               'mass_modulus_bound':sp.simplify(modulus_gap-4*q**2*tau**2),
               **{'weight_ratio_'+name:sp.cancel(w['P_over_W']-omega**2) for name,w in weights.items()}}
    checks={name:value==0 for name,value in residuals.items()}
    checks.update({'low_mass_coercivity_remainder_nonnegative':low_positive.is_nonnegative is True,
                   'high_mass_coercivity_remainder_nonnegative':high_positive.is_nonnegative is True,
                   'strict_coercivity_coefficient':(sigma*sp.Min(1,m)/rho).is_positive is True,
                   'finite_positive_weight_integral_bounds':all(w['W_integral_upper_bound'].is_positive for w in weights.values()),
                   'both_weights_normalized_at_UV':all(w['P_UV']==1 for w in weights.values()),
                   'inverse_P_integrals_diverge':all(w['inverse_P_integral_diverges'] for w in weights.values())})
    return {'symbols':{'sigma':sigma,'tau':tau,'q':q,'s':s,'E_radial':Er,'E_weighted':Em,
                       'Omega':omega,'k':k,'deformation':a,'cutoff_derivative_bound':Cchi},
            'rho':rho,'mass_coefficient':m,'rotated_form_real_part':real_part,
            'coercivity_constant':sigma*sp.Min(1,m)/rho,
            'operator_inverse_bound':sp.sqrt(rho)/(sigma*sp.Min(1,m)),
            'coercivity_low_remainder':low_positive,'coercivity_high_remainder':high_positive,
            'mass_modulus_gap':modulus_gap,'weights':weights,'cutoff_tail_bound':cutoff_bound,
            'residuals':residuals,'checks':checks,
            'scope':{'Omega_range':'0<Omega<=1; Omega(0)=1; BPS Omega_prime=-k*Omega*exp(-deformation*Omega^2)',
                     'core':'smooth compactly supported functions on the closed half-line, with trace free at zero',
                     'space':'completion in integral P|u_prime|^2+W|u|^2; equivalent to all finite-energy functions for these weights',
                     'Dirichlet_subspace':'kernel of the continuous UV trace',
                     'half_plane':'Re(s)>0 with q real fixed',
                     'variational_IR_domain_selected':True,
                     'other_IR_domains_certified':False,'imaginary_axis_limits_certified':False,
                     'infinite_dimensional_proof_formally_machine_checked':False,
                     'remaining_scalar_determinant_stability':False,
                     'BF_edge_and_embedding_sectors_certified':False,'full_N7':False,'full_P4':False}}


import argparse
import hashlib
import json
from pathlib import Path
if __package__:
    from . import verify_one_omega_topological_sector_reduction_v1 as sectors
else:
    import verify_one_omega_topological_sector_reduction_v1 as sectors
HERE=Path(__file__).resolve().parent
OUTPUT=HERE/'artifacts/one_omega_variational_dtn_v1.json'
TEST=HERE/'test_one_omega_variational_dtn_v1.py'
PROOF=HERE/'one_omega_variational_dtn_lemma_v1.md'
PROOF_SHA='a31c714c3b3b75ac832dd929edf9bb2f79ebc7f81654bb86069d82fa26d72c54'
SECTORS_SHA='4fa7432924b429ce4d350d6b6f96ba92965ee57b2d979dbd0fa029c1d29874e3'
SCHEMA='holo.one-omega-variational-dtn.v1'
canonical_digest=sectors.canonical_digest


def build_payload():
    proof=PROOF.read_bytes()
    if hashlib.sha256(proof).hexdigest()!=PROOF_SHA:raise ValueError('reviewed variational proof hash changed')
    sectors.validate_payload(sectors.assembly._load_receipt(sectors.OUTPUT,SECTORS_SHA))
    model=derive_model()
    if not all(model['checks'].values()):raise ValueError('variational coefficient identity failed')
    files=[Path(__file__),TEST,PROOF,Path(sectors.__file__)]
    payload={'schema':SCHEMA,'sources':{'sector_reduction':SECTORS_SHA,'reviewed_mathematical_proof':PROOF_SHA},
             'proof_type':'self-contained mathematical proof independently reviewed; companion verifies coefficient algebra, not Hilbert-space proof objects',
             'model':sectors.assembly.scalar._serialize({k:v for k,v in model.items() if k!='symbols'}),
             'checks':model['checks'],
             'decision':{'selected_finite_energy_TT_and_R_DtN_exist_uniquely_in_RHP':True,
                         'selected_finite_energy_DtN_holomorphic_in_RHP':True,
                         'selected_DtN_strictly_positive_real_after_division_by_s':True,
                         'tensor_vector_denominators_have_no_RHP_zeros_on_selected_branch':True,
                         'material_and_Omega_pivots_have_no_RHP_zeros_on_selected_branch':True,
                         'remaining_scalar_determinant_nonzero_in_RHP':False,
                         'imaginary_axis_limits_certified':False,
                         'other_IR_domains_certified':False,
                         'BF_edge_and_independent_embedding_equations_certified':False,
                         'infinite_dimensional_proof_formally_machine_checked':False,
                         'full_N7':False,'full_P4':False,'B4':False,'B5':False},
             'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:raise ValueError('variational receipt schema mismatch')
    if payload.get('calculation_digest')!=canonical_digest({k:v for k,v in payload.items() if k!='calculation_digest'}):
        raise ValueError('variational receipt digest mismatch')
    if payload!=build_payload():raise ValueError('variational receipt differs from fresh derivation')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path)
    modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args()
    if args.write:
        payload=build_payload()
        with args.write.open('x',encoding='utf8') as f:
            json.dump(payload,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
    else:
        payload=sectors.assembly.source.source_oracle._read_json(args.verify.read_bytes());validate_payload(payload)
    print(json.dumps({'checks_passed':sum(payload['checks'].values()),'calculation_digest':payload['calculation_digest']}))


if __name__=='__main__':main()
