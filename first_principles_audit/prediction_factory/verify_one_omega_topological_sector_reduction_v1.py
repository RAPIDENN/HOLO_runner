"""Exact sector reduction of the candidate boundary matrix.

Kernels remain the exact regular-response symbols. Fixing gauge divides only
by momentum components known nonzero on the declared patch. Scalar elimination
uses the explicit material and Omega pivots; their nonvanishing in the RHP is
checked by the separate positive-real energy calculation. The remaining 3x3
scalar determinant is NOT declared stable by this reduction.
"""
from __future__ import annotations
import sympy as sp
if __package__:
    from . import verify_one_omega_topological_boundary_assembly_v1 as assembly
else:
    import verify_one_omega_topological_boundary_assembly_v1 as assembly


def clean(value):
    return value.applyfunc(sp.cancel) if isinstance(value,sp.MatrixBase) else sp.cancel(value)


def zero(value):
    return all(sp.cancel(x)==0 for x in value) if isinstance(value,sp.MatrixBase) else sp.cancel(value)==0


def derive_model():
    base=assembly.derive_model();H=base['H_full'];idx=base['index'];P=base['parameters']
    w,q=base['context']['w'],base['context']['q'];p2=q*q-w*w
    M,G,Mb,xi,KT,Kv,pm,Z5,kap,y,beta,lam,eta,b4,k=(P[n] for n in ('M5c','G','Mb2','xi','K_T','K_v','p_material','Z5','kappa_hat','y','beta','lambda_K','eta','B4bar','k_inf'))
    FT=Mb*(xi*q*q-w*w)+M*KT
    FV=Mb*p2+M*KT
    PC=kap+2*Z5*pm;PD=beta+G*Kv
    tensor_cross=H[idx['H12'],idx['H12']]
    plus=sp.zeros(15,1);plus[idx['H11']]=1;plus[idx['H22']]=-1
    tensor_plus=(plus.T*H*plus)[0]
    vector_blocks={}
    vector_direction=sp.Matrix([q,w])
    expected_vector=sp.zeros(3)
    expected_vector[:2,:2]=FV*vector_direction*vector_direction.T/(2*p2)
    expected_vector[2,2]=-PC
    for axis in (1,2):
        names=(f'N{axis}',f'H{axis}3',f'vphi{axis}')
        block=H.extract([idx[n] for n in names],[idx[n] for n in names])
        vector_blocks[str(axis)]={'field_order':names,'matrix':block,
                                 'reference':expected_vector,'residual':clean(block-expected_vector)}
    # tau=0 fixes time gauge. H33=H11=H22 fixes scalar spatial gauge for q!=0.
    # All three spatial metric diagonal entries equal 2*zeta.
    n,N,z,D,chi=sp.symbols('lapse shift3 zeta Omega_trace phi3_trace',real=True)
    fields=sp.Matrix([n,N,z,D,chi]);T=sp.zeros(15,5)
    for name,column,factor in [('n',0,1),('N3',1,1),('H11',2,2),('H22',2,2),('H33',2,2),('omega',3,1),('vphi3',4,1)]:
        T[idx[name],column]=factor
    H5=clean(T.T*H*T)
    A=H5[:3,:3];B=H5[:3,3:];C=H5[3:,:3];E=H5[3:,3:]
    E_inverse=sp.diag(-1/PD,-1/PC)
    reduced=clean(A-B*E_inverse*C)
    left=sp.eye(5);right=sp.eye(5)
    left[:3,3:]=-B*E_inverse;right[3:,:3]=-E_inverse*C
    diagonal=sp.zeros(5);diagonal[:3,:3]=reduced;diagonal[3:,3:]=E
    elimination_residual=clean(left*H5*right-diagonal)
    # Independent compact action in the surviving three metric variables.
    U=q*q*(n-z)-w*q*N
    Z=z+U/(3*p2)
    Pi_R=2*Z5*kap*y*y*pm/PC
    Delta_beta=G*Kv*beta/PD
    L_local=Mb*((3-9*lam)*w*w*z*z+2*(1-3*lam)*w*q*z*N+(1-lam)*q*q*N*N+
                 xi*(4*q*q*n*z+2*q*q*z*z)-b4*q**4*z*z/k**2+(eta-Pi_R/Mb)*q*q*n*n)/2
    L_T=-M*KT*U*U/(3*p2*p2)
    L_contact=-3*M/base['A_prime_UV']*p2*Z*Z
    L_load=-Delta_beta*Z*Z/2
    L3=L_local+L_T+L_contact+L_load
    reference=sp.hessian(L3,(n,N,z))
    residuals={
        'tensor_cross':clean(tensor_cross+FT/2),
        'tensor_plus':clean(tensor_plus+FT/2),
        **{'vector_'+axis:block['residual'] for axis,block in vector_blocks.items()},
        'scalar_elimination_pivots':clean(E-sp.diag(-PD,-PC)),
        'scalar_block_factorization':elimination_residual,
        'left_elimination_determinant_one':sp.simplify(left.det()-1),
        'right_elimination_determinant_one':sp.simplify(right.det()-1),
        'three_variable_action_equals_Schur':clean(reduced-reference),
        'vector_q_nonzero_gauge_entry':clean(expected_vector[0,0]-q*q*FV/(2*p2)),
        'vector_q_zero_alternate_gauge_entry':clean(expected_vector[1,1].subs(q,0)+FV.subs(q,0)/2),
    }
    return {'base':base,'parameters':P,'frequency':w,'q':q,'p_squared':p2,
            'F_tensor':FT,'F_vector':FV,'P_material':PC,'P_Omega':PD,
            'tensor_cross':tensor_cross,'tensor_plus':tensor_plus,'vector_blocks':vector_blocks,
            'scalar_field_order':['n','N3','zeta','Omega_trace','phi3_trace'],
            'scalar_fields':fields,'scalar_injection':T,'scalar_5x5':H5,
            'pivot_block':E,'left_elimination':left,'right_elimination':right,
            'scalar_3x3':reduced,'scalar_action_reference':reference,
            'scalar_U':U,'scalar_Z':Z,'Pi_R':Pi_R,'Delta_beta':Delta_beta,
            'L3_local':L_local,'L3_tensor':L_T,'L3_contact':L_contact,'L3_load':L_load,'L3':L3,
            'determinant_identity':'det(H5)=(G*K_v+beta)*(kappa_hat+2*Z5*p_material)*det(H3)',
            'residuals':residuals,'checks':{name:zero(value) for name,value in residuals.items()},
            'scope':{'tensor_vector_RHP_result_requires_regular_energy_kernel_hypotheses':True,
                     'scalar_gauge_patch_requires_q_nonzero':True,
                     'projectors_require_q_squared_minus_frequency_squared_nonzero':True,
                     'scalar_q_zero_alternate_reduction_certified':False,
                     'remaining_scalar_determinant_nonzero_in_RHP':False,
                     'pivots_discarded_as_unphysical':False,
                     'full_physical_mode_count_certified':False,
                     'BF_edge_or_embedding_sector_certified':False,
                     'full_N7':False,'full_P4':False,'B4':False,'B5':False}}


import argparse
import hashlib
import json
from pathlib import Path
if __package__:
    from . import one_omega_positive_real_energy_v1 as energy
else:
    import one_omega_positive_real_energy_v1 as energy
HERE=Path(__file__).resolve().parent
OUTPUT=HERE/'artifacts/one_omega_topological_sector_reduction_v1.json'
TEST=HERE/'test_one_omega_topological_sector_reduction_v1.py'
ASSEMBLY_SHA='c3c93cd779fe684329419012202d2cf697aee926efe5efbaee1cb0e47f781bce'
SCHEMA='holo.one-omega-topological-sector-reduction.v1'
canonical_digest=assembly.canonical_digest


def build_payload():
    assembly.validate_payload(assembly._load_receipt(assembly.OUTPUT,ASSEMBLY_SHA))
    model=derive_model();positive=energy.derive_model()
    checks={**{'sector_'+k:v for k,v in model['checks'].items()},
            **{'energy_'+k:v for k,v in positive['checks'].items()}}
    if not all(checks.values()) or not all(positive['negative_controls'].values()):
        raise ValueError('sector reduction or conditional Green-energy check failed')
    keep={k:v for k,v in model.items() if k not in ('base','parameters')}
    files=[Path(__file__),TEST,Path(energy.__file__),Path(assembly.__file__)]
    payload={'schema':SCHEMA,'sources':{'boundary_assembly':ASSEMBLY_SHA},
             'sector_model':assembly.scalar._serialize(keep),
             'positive_real':assembly.scalar._serialize({k:v for k,v in positive.items() if k!='symbols'}),
             'checks':checks,'negative_controls':positive['negative_controls'],
             'decision':{'tensor_vector_denominators_nonzero_under_Green_hypotheses':True,
                         'material_and_Omega_pivots_nonzero_under_Green_hypotheses':True,
                         'scalar_five_to_three_reduction_preserves_pivots':True,
                         'remaining_scalar_RHP_determinant_certified_nonzero':False,
                         'global_DtN_existence_and_holomorphy_certified':False,
                         'all_Q_zero_scalar_cases_certified':False,
                         'complete_physical_constraint_reduction_certified':False,
                         'BF_edge_and_embedding_sectors_certified':False,
                         'full_N7':False,'full_P4':False,'B4':False,'B5':False},
             'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:raise ValueError('sector receipt schema mismatch')
    if payload.get('calculation_digest')!=canonical_digest({k:v for k,v in payload.items() if k!='calculation_digest'}):
        raise ValueError('sector receipt digest mismatch')
    if payload!=build_payload():raise ValueError('sector receipt differs from fresh derivation')


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
        payload=assembly.source.source_oracle._read_json(args.verify.read_bytes());validate_payload(payload)
    print(json.dumps({'checks_passed':sum(payload['checks'].values()),
                      'negative_controls':payload['negative_controls'],
                      'calculation_digest':payload['calculation_digest']}))


if __name__=='__main__':main()
