#!/usr/bin/env python3
"""Assemble the proposed connection term with H15 and keep every pivot.

The new H18 is a selected linear boundary response. It does not adopt a new
nonlinear charter or establish the complete BF/embedding constraint quotient.
The positive-real proof is pinned separately from the exact matrix identities.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp
if __package__:
    from . import verify_one_omega_topological_boundary_assembly_v1 as assembly
    from . import verify_one_omega_projected_connection_linear_v1 as projected
else:
    import verify_one_omega_topological_boundary_assembly_v1 as assembly
    import verify_one_omega_projected_connection_linear_v1 as projected

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_connection_candidate_response_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_candidate_response_v1.py'
OUTPUT=HERE/'artifacts/one_omega_connection_candidate_response_v1.json'
NOTE_SHA256='f78d97a347b8269913ee0fe0f47ee0fd6386cb32e4365c8a17de42a287ff45a5'
SCHEMA='holo.one-omega-connection-candidate-response.v1'
SOURCE_PINS={
 'one_omega_topological_boundary_assembly_v1':'c3c93cd779fe684329419012202d2cf697aee926efe5efbaee1cb0e47f781bce',
 'one_omega_topological_sector_reduction_v1':'4fa7432924b429ce4d350d6b6f96ba92965ee57b2d979dbd0fa029c1d29874e3',
 'one_omega_variational_dtn_v1':'4ca0b1a1859610c6b3f472bf9704b83f23f1b740900ab387f844bcb985101095',
 'one_omega_scalar_spectral_energy_v1':'0589ffc81229a600d10b08fa158f938101a9f593415f0ab52bdac55bf6d052db',
 'one_omega_scalar_shift_static_v1':'8ca7d81f1dcb645147d694d68fc32c0cc50483d67f2b7353caaecf31a22f190e',
 'one_omega_zero_momentum_linear_v1':'f2c83fa82a87353b01d43790ddfe73bd8e42febaca2a5554ddb8a5f5c6d96539',
 'one_omega_projected_connection_linear_v1':'3e92a6ef617cd880bf0db936d9d2c260e2c0868c479aaddd3efbe7cace4f4a49',
 'one_omega_interface_connection_current_candidate_v1':'e14bba98d1c9d6976c1ed2f6c902d9a603e7f20a09796c2dddc9c31095331a1e',
}

class CandidateResponseError(ValueError):pass

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
                                    ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def read_json(raw):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise CandidateResponseError('duplicate JSON key')
            out[k]=v
        return out
    def invalid(x):raise CandidateResponseError('nonfinite JSON constant')
    try:out=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    except (ValueError,UnicodeError) as exc:raise CandidateResponseError('invalid JSON') from exc
    if type(out) is not dict:raise CandidateResponseError('JSON root is not object')
    return out

def zero(value):
    return all(sp.cancel(x)==0 for x in value) if isinstance(value,sp.MatrixBase) else sp.cancel(value)==0

def clean(value):
    return value.applyfunc(sp.cancel) if isinstance(value,sp.MatrixBase) else sp.cancel(value)

def load_sources(note=NOTE,artifact_directory=HERE/'artifacts'):
    if hashlib.sha256(Path(note).read_bytes()).hexdigest()!=NOTE_SHA256:
        raise CandidateResponseError('response lemma hash mismatch')
    records={}
    for stem,sha in SOURCE_PINS.items():
        path=Path(artifact_directory)/(stem+'.json');raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=sha:raise CandidateResponseError('upstream artifact hash mismatch: '+stem)
        data=read_json(raw)
        if not data.get('checks') or not all(v is True for v in data['checks'].values()):
            raise CandidateResponseError('upstream identities failed: '+stem)
        # All directly consumed implementations remain the ones behind their receipts.
        for name,pin in data.get('provenance',{}).items():
            if name.endswith('.py') and Path(name).name==name:
                if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=pin:
                    raise CandidateResponseError('upstream implementation changed: '+name)
        records[stem]={'sha256':sha,'schema':data['schema']}
    return {'lemma_sha256':NOTE_SHA256,'upstreams':records,
            'source_physical_gate_promotions_inherited':False,
            'upstream_analytic_results':'pinned verified lemmas, not re-proved by a finite matrix calculation'}

def derive_model():
    base=assembly.derive_model();ctx=projected.symbols_context();geo=projected.derive_geometry(ctx)
    P,w,q=base['parameters'],base['context']['w'],base['context']['q']
    chi=ctx['chi'];theta=sp.Matrix(sp.symbols('theta1:4',real=True))
    generators=tuple(sp.Matrix(3,3,lambda a,b:sp.LeviCivita(i,a,b)) for i in range(3))
    Theta=sum((theta[i]*generators[i] for i in range(3)),sp.zeros(3))
    amplitudes=base['amplitudes'];old=sp.Matrix([amplitudes[n] for n in base['field_order']])
    fields=sp.Matrix([*old,*theta]);idx={**base['index'],**{f'theta{i+1}':15+i for i in range(3)}}
    k=(-w,sp.Integer(0),sp.Integer(0),q)
    mapping={}
    for mu in range(4):
        for i in range(3):
            mapping[ctx['shift_gradient'][mu][i]]=k[mu]*amplitudes[f'N{i+1}']
            for j in range(i,3):
                mapping[ctx['H_gradient'][mu][i,j]]=k[mu]*amplitudes[f'H{i+1}{j+1}']
        for a in range(3):
            for b in range(a+1,3):mapping[ctx['A'][mu][a,b]]=-k[mu]*Theta[a,b]
    omega=[clean(x.xreplace(mapping)) for x in geo['omega']]
    C=[clean(ctx['A'][mu].xreplace(mapping)-omega[mu]) for mu in range(4)]
    # Every term is a product of two first derivatives. The opposite Fourier
    # partners give k_mu*k_nu, not (i*k_mu)*(i*k_nu) of the same mode.
    L=sp.expand(chi*(projected.inner(C[0],C[0])-sum(projected.inner(x,x) for x in C[1:]))/2)
    addition=sp.hessian(L,fields)
    H=sp.zeros(18);H[:15,:15]=base['H_full'];H+=addition
    gauges={}
    for name,old_g in base['gauge_vectors'].items():
        g=sp.zeros(18,1);g[:15,0]=old_g
        if name=='space_1':g[idx['theta2']]=sp.I*q/2
        if name=='space_2':g[idx['theta1']]=-sp.I*q/2
        gauges[name]=g
    b,M,KT=P['Mb2'],P['M5c'],P['K_T'];z=q*q-w*w;m=M*KT/z;B=b+m
    FT=b*(P['xi']*q*q-w*w)+M*KT
    tt_cross=H[idx['H12'],idx['H12']]
    plus=sp.zeros(18,1);plus[idx['H11']]=1;plus[idx['H22']]=-1
    tt_plus=(plus.T*H*plus)[0]
    injection=sp.zeros(18,5)
    for name,col,factor in [('n',0,1),('N3',1,1),('H11',2,2),('H22',2,2),('H33',2,2),('omega',3,1),('vphi3',4,1)]:
        injection[idx[name],col]=factor
    H5=clean(injection.T*H*injection)
    old_injection=injection[:15,:];oldH5=clean(old_injection.T*base['H_full']*old_injection)
    expected_delta=sp.zeros(5);expected_delta[2,2]=-2*chi*q*q
    scalar_material_pivots=H5[3:,3:]
    oldH3=clean(oldH5[:3,:3]-oldH5[:3,3:]*oldH5[3:,3:].inv()*oldH5[3:,:3])
    H3=clean(H5[:3,:3]-H5[:3,3:]*scalar_material_pivots.inv()*H5[3:,:3])
    vectors={}
    for axis,theta_index,orientation in ((1,1,1),(2,0,-1)):
        N=amplitudes[f'N{axis}'];hh=amplitudes[f'H{axis}3'];t=theta[theta_index]
        names=[f'N{axis}',f'H{axis}3',f'theta{theta_index+1}']
        indices=[idx[n] for n in names]
        block=H.extract(indices,indices)
        density=B*(q*N+w*hh)**2/4+chi*((w*t+orientation*q*N/2)**2-q*q*(t-orientation*hh/2)**2)/2
        reference=sp.hessian(density,(N,hh,t))
        gauge_fixed=block.extract([0,2],[0,2])
        pivot=gauge_fixed[0,0]
        schur=clean(gauge_fixed[1,1]-gauge_fixed[1,0]*gauge_fixed[0,1]/pivot)
        Keff=2*chi*B/(2*B+chi)
        vectors[str(axis)]={'field_order':names,'block':block,'density':density,
            'reference':reference,'gauge_fixed':gauge_fixed,'pivot':pivot,'Schur':schur,
            'reference_Schur':Keff*w*w-chi*q*q,'K_eff':Keff,
            'determinant_residual':clean(gauge_fixed.det()-pivot*schur),
            'matrix_residual':clean(block-reference)}
    direct_zero=sp.zeros(18)
    direct_zero[15:,15:]=chi*w*w*sp.eye(3)
    checks={
        'H18_formal_opposite_Fourier_adjoint':zero(H-H.T.xreplace({w:-w,q:-q})),
        'all_324_added_entries_from_projected_C_density':zero(H-sp.diag(base['H_full'],sp.zeros(3))-addition),
        **{'four_dimensional_gauge_'+name:zero(H*g) for name,g in gauges.items()},
        'tensor_cross_adds_chi_q_squared':zero(tt_cross+(FT+chi*q*q)/2),
        'tensor_plus_adds_chi_q_squared':zero(tt_plus+(FT+chi*q*q)/2),
        'all_25_scalar_entries_change_only_zeta_zeta':zero(H5-oldH5-expected_delta),
        'scalar_material_and_Omega_pivots_unchanged':zero(scalar_material_pivots-oldH5[3:,3:]),
        'all_nine_three_scalar_entries_change_only_zeta_zeta':zero(H3-oldH3-expected_delta[:3,:3]),
        'lapse_shift_pivot_and_schur_numerators_unchanged':zero(H3[:2,:]-oldH3[:2,:]),
        'scalar_chart_has_no_theta_mixing':zero(injection.T*H[:,15:]),
        **{'vector_'+axis+'_all_nine_entries':zero(data['matrix_residual']) for axis,data in vectors.items()},
        **{'vector_'+axis+'_shift_pivot_retained':zero(data['pivot']-q*q*(2*B+chi)/4) for axis,data in vectors.items()},
        **{'vector_'+axis+'_effective_theta_action':zero(data['Schur']-data['reference_Schur']) for axis,data in vectors.items()},
        **{'vector_'+axis+'_determinant_factorization':zero(data['determinant_residual']) for axis,data in vectors.items()},
        'theta_longitudinal_free_denominator':zero(H[idx['theta3'],idx['theta3']]-chi*(w*w-q*q)),
        'theta_longitudinal_decoupled':all(H[idx['theta3'],j]==0 for j in range(18) if j!=idx['theta3']),
        'all_324_homogeneous_added_entries_derived_directly':zero(addition.subs(q,0)-direct_zero),
        'homogeneous_projected_connection_zero':all(zero(x.subs(q,0)) for x in omega),
        'phi_and_Omega_no_direct_added_operator':all(addition[idx[name],:]==sp.zeros(1,18) for name in ('omega','vphi1','vphi2','vphi3')),
    }
    negatives={'omit_spatial_gauge_theta_compensation':H*sp.Matrix([*base['gauge_vectors']['space_1'],0,0,0]),
               'old_scalar_operator_reused_unchanged':H5-oldH5,
               'halve_tensor_connection_gradient':tt_cross+(FT+chi*q*q/2)/2,
               'drop_vector_shift_Schur_term':vectors['1']['gauge_fixed'][1,1]-vectors['1']['Schur']}
    return dict(base=base,geometry_context=ctx,w=w,q=q,s=sp.Symbol('s',nonzero=True),chi=chi,
                theta=theta,fields=fields,index=idx,omega=omega,C=C,L_C=L,addition=addition,H18=H,
                gauges=gauges,B=B,m=m,FT=FT,tensor_cross=tt_cross,tensor_plus=tt_plus,
                scalar_injection=injection,H5=H5,oldH5=oldH5,H3=H3,oldH3=oldH3,
                vectors=vectors,checks=checks,negative=negatives)

def derive_positive_real():
    sigma,b,chi,ell=sp.symbols('sigma b chi ell',positive=True)
    tau,q=sp.symbols('tau q',real=True);s=sigma+sp.I*tau
    atom=s*ell/(ell+s*s+q*q)
    atom_real=ell*sigma*(ell+sigma*sigma+tau*tau+q*q)/((sigma*sigma+tau*tau-ell-q*q)**2+4*sigma*sigma*(ell+q*q))
    # Two arbitrary positive-real values u=sB and v=chi*s; no fitted atoms.
    ux,vx=sp.symbols('ux vx',positive=True);uy,vy=sp.symbols('uy vy',real=True)
    u=ux+sp.I*uy;v=vx+sp.I*vy
    harmonic=2*u*v/(2*u+v)
    real_reference=(2*ux*(vx*vx+vy*vy)+4*vx*(ux*ux+uy*uy))/((2*ux+vx)**2+(2*uy+vy)**2)
    ms=sp.Symbol('m');ss=sp.Symbol('s',nonzero=True)
    B=b+ms;d=2*b+chi
    K=2*chi*B/(2*B+chi);K0=2*chi*b/d
    excess=2*chi*chi/d*ss*ms/(d+2*ms)
    q0=sp.limit(K,ms,0)
    checks={
        'Stieltjes_atom_s_m_real_part':sp.simplify(sp.re(atom)-atom_real)==0,
        'Stieltjes_atom_strictly_positive':atom_real.is_positive is True,
        'harmonic_positive_real_part_identity':sp.simplify(sp.re(harmonic)-real_reference)==0,
        'harmonic_real_part_strictly_positive':real_reference.is_positive is True,
        's_Keff_reciprocal_sum_identity':zero(ss*K-1/(1/(chi*ss)+1/(2*ss*B))),
        'K0_excess_identity':zero(ss*(K-K0)-excess),
        'excess_reciprocal_sum_identity':zero(ss*ms/(d+2*ms)-1/(d/(ss*ms)+2/ss)),
        'zero_measure_branch_Keff_equals_K0':q0==K0,
        'K0_strictly_positive':K0.is_positive is True,
        'scalar_increment_real_part_positive_for_q_nonzero':sp.simplify(sp.re(2*chi*q*q/s)-2*chi*q*q*sigma/(sigma*sigma+tau*tau))==0,
        'homogeneous_free_theta_real_part':sp.simplify(sp.re(chi*s)-chi*sigma)==0,
        'homogeneous_not_limit_of_vector_Schur':sp.simplify(K0-chi)!=0,
    }
    return dict(s=s,sigma=sigma,tau=tau,b=b,chi=chi,q=q,ell=ell,ux=ux,uy=uy,vx=vx,vy=vy,
                atom=atom,atom_real=atom_real,harmonic=harmonic,real_reference=real_reference,
                K0=K0,excess=excess,checks=checks)

def serialize(value):
    if isinstance(value,sp.MatrixBase):return [[sp.sstr(value[i,j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value,sp.Basic):return sp.sstr(value)
    if isinstance(value,dict):return {k:serialize(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serialize(v) for v in value]
    return value

def build_payload():
    sources=load_sources();model=derive_model();pr=derive_positive_real()
    checks={**model['checks'],**{'PR_'+k:v for k,v in pr['checks'].items()}}
    negative={k:not zero(v) for k,v in model['negative'].items()}
    if not all(checks.values()) or not all(negative.values()):raise CandidateResponseError('matrix or positive-real identity failed')
    compact={k:model[k] for k in ('L_C','addition','B','m','FT','H5','H3','vectors')}
    out={'schema':SCHEMA,'sources':sources,
         'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
         'checks':checks,'negative_controls':negative,'response':serialize(compact),
         'positive_real':serialize({k:pr[k] for k in ('atom_real','real_reference','K0','excess')}),
         'scope':{'new_coefficient':'chi>0, mass dimension 2, no selected value',
                  'frequency_domain':'Re(s)>0, w=i*s, selected BPS finite-energy IR branch',
                  'spatial_momentum':'q>0 per-mode proof and separate direct q=0 chart',
                  'scalar_analytic_input':'pinned strict positivity of -S_zeta/s for the selected original response',
                  'tensor_kernel_analytic_input':'pinned finite-mass Stieltjes measure for m=M*K_T/(s²+q²)',
                  'old_physical_domain_gates_inherited':False},
         'decision':{'proposed_H18_linear_response_assembled':True,
                     'new_scalar_and_tensor_RHP_denominators_nonzero':True,
                     'new_theta_channels_and_retained_shift_pivots_RHP_nonzero':True,
                     'homogeneous_added_block_derived_without_q_division':True,
                     'new_action_adopted':False,'new_chi_value_selected':False,
                     'uniform_shift_reconstruction_at_q_zero_proved':False,
                     'imaginary_axis_poles_or_global_modes_counted':False,
                     'nonlinear_torque_repair_completed':False,
                     'BF_boundary_domain_and_embeddings_completed':False,
                     'full_N2':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}
    out['calculation_digest']=digest(out)
    return out

def validate_payload(payload):
    expected=build_payload()
    if payload!=expected:raise CandidateResponseError('receipt differs from fresh source-bound derivation')
    return expected

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',action='store_true');modes.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.verify:out=validate_payload(read_json(OUTPUT.read_bytes()))
    else:
        out=build_payload()
        with OUTPUT.open('x') as f:json.dump(out,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    print(json.dumps({'checks_passed':len(out['checks']),'negative_controls':out['negative_controls'],
                      'calculation_digest':out['calculation_digest']}))
    return 0

if __name__=='__main__':raise SystemExit(main())
