"""Assemble the candidate's linear bulk response and local brane quadratic form.

The bulk metric is decomposed with four-dimensional Lorentz projectors at
k^2 != 0. Kernels KT, Kv and p are independent symbols for the regular TT,
canonical scalar, and material responses. No fitted spectrum is used. The
candidate BF quadratic block remains separate and is not eliminated here.

The local complement is foliation + intrinsic Robin ONLY. EH+GHY+2W+beta is
already in the newly derived bulk boundary response. In particular neither the
old solid contacts nor a second wall or induced Einstein term is added.
"""
from __future__ import annotations
import sympy as sp
if __package__:
    from . import verify_one_omega_brane_hessian_v1 as local
    from . import verify_one_omega_topological_tt_compatibility_v1 as source
else:
    import verify_one_omega_brane_hessian_v1 as local
    import verify_one_omega_topological_tt_compatibility_v1 as source

FIELD_NAMES=tuple(n for n in local.algebra.FIELD_NAMES if not n.startswith('pi'))


def _clean(matrix):
    return matrix.applyfunc(sp.cancel) if isinstance(matrix,sp.MatrixBase) else sp.cancel(matrix)


def _zero(value):
    return all(sp.cancel(x)==0 for x in value) if isinstance(value,sp.MatrixBase) else sp.cancel(value)==0


def project_metric(h,w,q):
    eta=sp.diag(-1,1,1,1)
    k=sp.Matrix([-w,0,0,q]);kup=eta*k;k2=q**2-w**2
    theta=eta-k*k.T/k2;thetaup=eta*theta*eta;mixed=theta*eta
    transverse=_clean(mixed*h*mixed.T)
    trace=sp.trace(thetaup*h)
    tt=_clean(transverse-theta*trace/3)
    return {'eta':eta,'k_cov':k,'k_up':kup,'k_squared':k2,'theta_cov':theta,
            'theta_up':thetaup,'mixed_projector':mixed,'transverse':transverse,
            'TT':tt,'Z':sp.cancel(trace/6)}


def quadratic_transfer():
    e,nu=sp.symbols('epsilon volume_first',real=True)
    q1=sp.Matrix(sp.symbols('residual_first0:3',real=True))
    q2=sp.Matrix(sp.symbols('residual_second0:3',real=True))
    metric_first=sp.Matrix(3,3,lambda i,j:sp.Symbol(f'metric_first_{min(i,j)}{max(i,j)}',real=True))
    residual=e*q1+e**2*q2
    norm=(1+e*nu)*(residual.T*(sp.eye(3)+e*metric_first)*residual)[0]
    robin=sp.expand(norm).coeff(e,2)-(q1.T*q1)[0]
    P1,P2,Achi=sp.symbols('P_first P_second A_first_phi_first',real=True)
    covariant_P=e*P1+e**2*(P2+Achi)
    kinetic=sp.expand((1+e*nu)*covariant_P**2).coeff(e,2)-P1**2
    B,dA,AA=sp.symbols('B_first dA_first A_first_wedge_A_first',real=True)
    bf=sp.expand(e*B*(e*dA+e**2*AA)).coeff(e,2)-B*dA
    return {'residuals':{'Robin_frame_and_volume_first_enter_after_order_two':robin,
                        'gauged_P_addition_first_enters_after_order_two':kinetic,
                        'BF_quadratic_is_B1_wedge_dA1':bf},
            'scope':'vacuum phi=A=B=acceleration=0; frame and iota corrections occur in residual_second; BF is metric independent as a top form'}


def derive_model():
    ctx=local.algebra.symbols_context()
    # The candidate selects a negative lambda. Do not inherit positivity from the old solid context.
    ctx['parameters']['lambda_K']=sp.Symbol('lambda_K',real=True)
    pars=ctx['parameters'];w,q=ctx['w'],ctx['q']
    M,G,kinf,Mb,beta=(pars[n] for n in ('M5c','G','k_inf','Mb2','beta'))
    KT,Kv,p=sp.symbols('K_T K_v p_material')
    Z5=sp.Symbol('Z5',positive=True)
    a0=-kinf*sp.exp(-G/(6*M))
    amplitudes={n:sp.Symbol('amp_'+n,real=True) for n in FIELD_NAMES}
    vector=sp.Matrix([amplitudes[n] for n in FIELD_NAMES]);index={n:i for i,n in enumerate(FIELD_NAMES)}
    h=sp.zeros(4);h[0,0]=-2*amplitudes['n']
    for i in range(1,4):h[0,i]=h[i,0]=amplitudes[f'N{i}']
    for i in range(1,4):
        for j in range(1,4):h[i,j]=amplitudes[f'H{min(i,j)}{max(i,j)}']
    projection=project_metric(h,w,q);eta=projection['eta'];tt=projection['TT'];Z=projection['Z'];D=amplitudes['omega'];d=w**2-q**2
    zrow=sp.Matrix([sp.diff(Z,x) for x in vector]);drow=sp.zeros(len(vector),1);drow[index['omega']]=1
    tt_map=sp.Matrix([tt[i,j] for i in range(4) for j in range(4)]).jacobian(vector)
    contraction=sp.diag(*[eta[i,i]*eta[j,j] for i in range(4) for j in range(4)])
    TT_gram=_clean(tt_map.T*contraction*tt_map)
    H_T=_clean(-M*KT*TT_gram/4)
    H_scalar=_clean((6*M*d/a0-G*Kv)*zrow*zrow.T+G*Kv*(zrow*drow.T+drow*zrow.T)-(G*Kv+beta)*drow*drow.T)
    H_material=sp.zeros(len(vector))
    for i in range(1,4):H_material[index[f'vphi{i}'],index[f'vphi{i}']]=-2*Z5*p
    density=local.canonical_quadratic(ctx)
    Hlocal18=local.algebra.momentum_hessian(density['foliation']+density['robin'],ctx)
    kept=[ctx['field_names'].index(n) for n in FIELD_NAMES]
    H_local=Hlocal18.extract(kept,kept)
    H_bulk=_clean(H_T+H_scalar+H_material)
    H_full=_clean(H_local+H_bulk)
    gauge={}
    g=sp.zeros(len(vector),1);g[index['n']]=-sp.I*w;g[index['tau']]=1
    g[index['N3']]=-sp.I*q;gauge['time']=g
    for i in range(1,4):
        g=sp.zeros(len(vector),1);g[index[f'N{i}']]=-sp.I*w
        g[index[f'H{min(i,3)}{max(i,3)}']]=sp.I*q*(2 if i==3 else 1)
        gauge[f'space_{i}']=g
    # Independent covariant Fierz-Pauli quadratic action, not the projector formula.
    M4=sp.Symbol('M4_bulk_squared',positive=True)
    trace_h=sp.trace(eta*h);norm_h=sp.trace(eta*h*eta*h)
    divergence_h=eta*h*projection['k_up']
    div_norm=(divergence_h.T*eta*divergence_h)[0]
    div_dot_k=(divergence_h.T*projection['k_cov'])[0]
    FP=M4*(-projection['k_squared']*norm_h+projection['k_squared']*trace_h**2+2*div_norm-2*div_dot_k*trace_h)/8
    H_FP=sp.hessian(FP,tuple(vector))
    # Ns=-6M/a0-6M4 follows from the independently proved exact radial measures.
    H_IR=_clean((H_T+H_scalar).subs({KT:-M4*d/M,Kv:(6*M/a0+6*M4)*d/G},simultaneous=True))
    metric_indices=list(range(10))
    IR_difference=_clean((H_IR-H_FP).extract(metric_indices,metric_indices))
    transfer=quadratic_transfer()
    checks={
        'theta_is_projector':_zero(projection['mixed_projector']**2-projection['mixed_projector']),
        'TT_trace_zero':_zero(sp.trace(eta*tt)),
        'TT_divergence_zero':_zero(projection['k_up'].T*tt),
        'bulk_metric_response_symmetric':_zero(H_bulk-H_bulk.T),
        'IR_all_100_metric_entries_equal_Fierz_Pauli':_zero(IR_difference),
        'local_complement_has_no_wall_or_solid_parameters':not any(H_local.has(pars[n]) for n in ('M5c','G','beta','rho_X','mu_X','lambda_X','v')),
        'beta_counted_once':sp.diff(H_full[index['omega'],index['omega']],beta)==-1,
        **{'gauge_'+name:_zero(H_full*v) for name,v in gauge.items()},
        **{name:value==0 for name,value in transfer['residuals'].items()}}
    return {'context':ctx,'parameters':{**pars,'K_T':KT,'K_v':Kv,'p_material':p,'Z5':Z5,'M4_bulk_squared':M4},
            'amplitudes':amplitudes,'field_order':FIELD_NAMES,'index':index,'metric':h,'projection':projection,
            'A_prime_UV':a0,'Z':Z,'D':D,'H_T':H_T,'H_scalar':H_scalar,'H_material':H_material,
            'H_local':H_local,'H_bulk':H_bulk,'H_full':H_full,'gauge_vectors':gauge,
            'Fierz_Pauli_action':FP,'H_Fierz_Pauli':H_FP,'H_IR':H_IR,'IR_difference':IR_difference,
            'transfer':transfer,'checks':checks,
            'scope':{'slice_momentum_squared_nonzero_required':True,
                     'null_cone_projector_extension_certified':False,
                     'kernels_are_unfitted_regular_responses':True,
                     'independent_moving_embedding_equations_certified':False,
                     'BF_block_eliminated':False,'BF_edge_domain_certified':False,
                     'full_constraint_reduction_certified':False,
                     'global_stability_certified':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}


import argparse
import hashlib
import json
from pathlib import Path
if __package__:
    from . import verify_one_omega_bps_scalar_master_v1 as scalar
else:
    import verify_one_omega_bps_scalar_master_v1 as scalar
HERE=Path(__file__).resolve().parent
OUTPUT=HERE/'artifacts/one_omega_topological_boundary_assembly_v1.json'
TEST=HERE/'test_one_omega_topological_boundary_assembly_v1.py'
SCALAR_RECEIPT=scalar.OUTPUT
SCALAR_SHA='45e180caf42b9033fd64fa8ae2a73b8c3e76a19525c54a2ead43f2b34df48f25'
TT_RECEIPT=source.OUTPUT
TT_SHA='e579cc886c355ba78d54d7c88550ac350c935a062733f14f60a1e588190f9208'
SCHEMA='holo.one-omega-topological-boundary-assembly.v1'
canonical_digest=source.canonical_digest


def _load_receipt(path,digest):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=digest:
        raise ValueError('boundary assembly upstream hash changed: '+path.name)
    return source.source_oracle._read_json(raw)


def build_payload():
    binding=source.load_sources()
    source.validate_payload(_load_receipt(TT_RECEIPT,TT_SHA))
    scalar.validate_payload(_load_receipt(SCALAR_RECEIPT,SCALAR_SHA))
    model=derive_model()
    if not all(model['checks'].values()):raise ValueError('boundary assembly identity failed')
    # Byte-pinned independently compared 18-field source; no historical flags inherited.
    original=local.load_source()
    full_original=local.algebra.momentum_hessian(local.canonical_quadratic(model['context'])['total'],model['context'])
    source_comparison=local.compare_symbolic_matrix(original,full_original,model['context'])
    files=[Path(__file__),TEST,Path(local.__file__),Path(local.algebra.__file__),Path(source.__file__),Path(scalar.__file__)]
    keep=('field_order','A_prime_UV','Z','D','H_T','H_scalar','H_material','H_local','H_bulk','H_full',
          'gauge_vectors','Fierz_Pauli_action','H_Fierz_Pauli','H_IR','IR_difference','transfer','scope')
    payload={'schema':SCHEMA,'sources':{'candidate':source.CANDIDATE_SHA256,
            'candidate_action':source.CANDIDATE_ACTION_SHA256,'scalar_boundary':SCALAR_SHA,
            'TT_boundary':TT_SHA,'old_brane_snapshot':local.EXPECTED_SOURCE_SHA256},
            'source_comparison':source_comparison,
            'candidate_parameter_policy':binding['candidate']['exact_classical_charter']['coefficient_policy'],
            'model':scalar._serialize({k:model[k] for k in keep}),
            'checks':model['checks'],
            'kernel_definitions':{'K_T':'-2 H_TT_prime(0)/H_TT(0) on the BPS half-space',
                'K_v':'-2 (Q_S v)(0)/v(0) = -2 R_prime(0)/R(0), R=Z-D',
                'p_material':'regular root sqrt(q^2-frequency^2); retarded continuation selected separately',
                'IR':'K_T=-(M4_bulk_squared/M5c)*d+o(d); K_v=-(Norm_S/G)*d+o(d), with regular IR branch and vanishing final flux',
                'exact_finite_momentum_kernels_replaced_by_IR':False},
            'evidence_limits':[
                'This is the vacuum quadratic metric/Omega/material block; the independent BF block and edge domain remain separate.',
                'The local complement contains foliation and Robin only. All old solid and wall terms are excluded before adding the canonical bulk+wall response.',
                'No inverse projector is used on k^2=0. The polynomial IR extension does not establish an extension of the full kernels.',
                'lambda_K is generic real in the algebra. Decimal candidate coefficients are recorded literally; no exact exponential equality is assigned to them.',
                'The displayed kernels are independent exact-response symbols. Four gauge nulls and IR matching are not a physical degree-of-freedom count or a stability proof.'],
            'decision':{'candidate_quadratic_non_BF_boundary_block_assembled':True,
                        'four_tangent_gauge_nulls_checked':True,
                        'all_100_metric_IR_entries_match_Einstein':True,
                        'independent_embedding_equations_certified':False,
                        'BF_block_or_edge_domain_eliminated':False,
                        'null_cone_complete_response_certified':False,
                        'physical_constraint_reduction_certified':False,
                        'global_spectrum_and_stability_certified':False,
                        'full_N7':False,'full_P4':False,'B4':False,'B5':False},
            'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:raise ValueError('assembly receipt schema mismatch')
    if payload.get('calculation_digest')!=canonical_digest({k:v for k,v in payload.items() if k!='calculation_digest'}):
        raise ValueError('assembly receipt digest mismatch')
    if payload!=build_payload():raise ValueError('assembly receipt differs from fresh derivation')


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
        payload=source.source_oracle._read_json(args.verify.read_bytes());validate_payload(payload)
    print(json.dumps({'checks_passed':sum(payload['checks'].values()),
                      'source_comparison':payload['source_comparison'],
                      'calculation_digest':payload['calculation_digest']}))


if __name__=='__main__':main()
