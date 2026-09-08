"""Literal nonlinear ADM foliation/Robin first variations and IBP currents.

Calculations use arbitrary covariant jets in a spatial orthonormal normal
frame at one point. K, lapse, shift, acceleration and curvature are not set
to vacuum values. Independent variables are N, contravariant N^i, h_ij and
internal material components. The three material charts start from the
canonical bulk Green -Pi_a delta(phi_a), including its metric adjoints.
This does not certify the complete moving-interface or covariant E_u system.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import sympy as sp

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_adm_robin_euler_lemma_v1.md'
TEST=HERE/'test_one_omega_adm_robin_euler_v1.py'
CANDIDATE=HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
INVENTORY=HERE/'derive_one_omega_topological_so3_moving_interface_variational_completion_v5_6_7_8_gate.py'
OUTPUT=HERE/'artifacts/one_omega_adm_robin_euler_v1.json'
NOTE_SHA256='eb05778cc7d3ef57b5a511b0d60f344f8fb3165ace36b938f014a9c9c4b426ee'
CANDIDATE_SHA256='d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
INVENTORY_SHA256='18eb511418017a86c05ba506d3c6dac7c13b10b39ebdad607d8143d9a2872acb'
SCHEMA='holo.one-omega-adm-robin-euler.v1'

class ADMEulerError(ValueError):
    pass

def canonical_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
        ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def sym(prefix):
    return sp.Matrix(3,3,lambda i,j:sp.Symbol(f'{prefix}_{min(i,j)}{max(i,j)}',real=True))

def vec(prefix,n=3):
    return sp.Matrix(sp.symbols(f'{prefix}0:{n}',real=True))

def pair(a,b):
    return sum(a[i,j]*b[i,j] for i in range(a.rows) for j in range(a.cols))

def sym_outer(a,b):
    return (a*b.T+b*a.T)/2

def clean(value):
    return value.applyfunc(sp.cancel) if isinstance(value,sp.MatrixBase) else sp.cancel(value)

def zero(value):
    return all(sp.cancel(x)==0 for x in value) if isinstance(value,sp.MatrixBase) else sp.cancel(value)==0

def first(value,e):
    return value.applyfunc(lambda x:sp.expand(sp.diff(x,e).subs(e,0))) if isinstance(value,sp.MatrixBase) else sp.expand(sp.diff(value,e).subs(e,0))

def tensor_coefficient(expression,Q):
    return sp.Matrix(3,3,lambda i,j:sp.diff(expression,Q[i,j])/(1 if i==j else 2))

def symbols_context():
    b,N,V,k,kappa=sp.symbols('Mb_squared N volume k_inf kappa_hat',positive=True)
    lam,xi,eta,B4,y,R,n,e=sp.symbols('lambda_K xi eta B4_bar y R n epsilon',real=True)
    return dict(b=b,N=N,V=V,k=k,kappa=kappa,lam=lam,xi=xi,eta=eta,B4=B4,y=y,R=R,n=n,e=e)

def derive_kinetic(ctx):
    b,N,V,lam,n,e=(ctx[x] for x in ('b','N','V','lam','n','e'))
    K,Q,T=sym('K'),sym('Q'),sym('transport')
    inverse=sp.eye(3)-e*Q
    moved_K=K+e*(T/(2*N)-n*K)
    moved_F=sp.trace(inverse*moved_K*inverse*moved_K)-lam*sp.trace(inverse*moved_K)**2
    literal=b*N*(1+e*n)*V*(1+e*sp.trace(Q)/2)*moved_F/2
    raw=first(literal,e)
    F=sp.trace(K*K)-lam*sp.trace(K)**2
    C=tensor_coefficient(F,K)/2
    algebraic=sp.eye(3)*F/2-2*K*K+2*lam*sp.trace(K)*K
    reference=b*(N*V*(-F*n+pair(algebraic,Q))+V*pair(C,T))/2
    residuals={'literal_directional_derivative':sp.expand(raw-reference),
               'C_from_literal_dF_dK':C-(K-lam*sp.trace(K)*sp.eye(3)),
               'inverse_metric_first_jet':first((sp.eye(3)+e*Q)*inverse-sp.eye(3),e),
               'volume_first_jet':first(sp.sqrt((sp.eye(3)+e*Q).det()),e)-sp.trace(Q)/2,
               'lapse_row':sp.diff(raw,n)+b*N*V*F/2,
               'metric_algebraic_row':tensor_coefficient(raw,Q)-b*N*V*algebraic/2,
               'transport_momentum':tensor_coefficient(raw,T)-b*V*C/2}
    return {'K':K,'Q':Q,'transport':T,'F_K':F,'C':C,'metric_algebraic':algebraic,
            'literal_first_variation':raw,'reference':reference,'residuals':residuals}

def derive_transport_ibp():
    pi,pt,Q,Qt=sym('pi'),sym('pi_t'),sym('Q'),sym('Q_t')
    pg=[sym(f'pi_d{k}') for k in range(3)]
    Qg=[sym(f'Q_d{k}') for k in range(3)]
    shift,dv=vec('shift'),vec('delta_shift')
    J=sp.Matrix(3,3,lambda i,j:sp.Symbol(f'shift_d{i}_{j}',real=True))
    Dv=sp.Matrix(3,3,lambda i,j:sp.Symbol(f'delta_shift_d{i}_{j}',real=True))
    lieQ=sum((shift[k]*Qg[k] for k in range(3)),sp.zeros(3))+J*Q+Q*J.T
    T=Qt-lieQ-Dv-Dv.T
    raw=pair(pi,T)
    current_t=pair(pi,Q)
    current_x=sp.Matrix([-shift[k]*pair(pi,Q)-2*(pi*dv)[k] for k in range(3)])
    divergence=pair(pt,Q)+pair(pi,Qt)
    divergence-=sum(J[k,k]*pair(pi,Q)+shift[k]*pair(pg[k],Q)+shift[k]*pair(pi,Qg[k]) for k in range(3))
    divergence-=2*sum(pg[i][i,j]*dv[j]+pi[i,j]*Dv[i,j] for i in range(3) for j in range(3))
    bulk=sp.expand(raw-divergence)
    metric=tensor_coefficient(bulk,Q)
    shift_row=sp.Matrix([sp.diff(bulk,dv[i]) for i in range(3)])
    lie_density=sum((shift[k]*pg[k] for k in range(3)),sp.zeros(3))-J.T*pi-pi*J+sp.trace(J)*pi
    expected_metric=-pt+lie_density
    expected_shift=sp.Matrix([2*sum(pg[j][j,i] for j in range(3)) for i in range(3)])
    return {'pi_density':pi,'pi_time_jet':pt,'pi_spatial_jets':pg,'Q':Q,'Q_time_jet':Qt,
            'Q_spatial_jets':Qg,'shift':shift,'shift_gradient':J,'delta_shift':dv,
            'delta_shift_gradient':Dv,'transport':T,'raw':raw,'bulk':bulk,
            'metric_row':metric,'shift_row':shift_row,'Lie_density':lie_density,
            'current_t':current_t,'current_spatial':current_x,'current_divergence':divergence,
            'residuals':{'metric_IBP_density_weight_one':clean(metric-expected_metric),
                         'shift_IBP_factor_two':clean(shift_row-expected_shift),
                         'no_other_variation_jets_after_IBP':sp.expand(bulk-pair(metric,Q)-(shift_row.T*dv)[0])}}

def derive_curvature(ctx):
    N,V,b,R,xi,B4,k,n=(ctx[x] for x in ('N','V','b','R','xi','B4','k','n'))
    Q,Ric=sym('R_Q'),sym('Ricci')
    Q1=[sym(f'R_Q_d{i}') for i in range(3)]
    Q2=[[sym(f'R_Q_d{i}d{j}') for j in range(3)] for i in range(3)]
    def gamma_derivative(k,i,j,l):
        return (Q2[l][i][j,k]+Q2[l][j][i,k]-Q2[l][k][i,j])/2
    delta_Ric=sp.Matrix(3,3,lambda i,j:sum(gamma_derivative(k,i,j,k)-gamma_derivative(k,i,k,j) for k in range(3)))
    scalar_derivative=sp.trace(delta_Ric)-pair(Ric,Q)
    scalar_reference=-pair(Ric,Q)+sum(Q2[i][j][i,j]-Q2[i][i][j,j] for i in range(3) for j in range(3))
    f=xi*R-B4*R*R/(16*k*k);fR=sp.diff(f,R)
    F=sp.Symbol('weighted_fR',real=True);Fg=vec('weighted_fR_d');Fh=sym('weighted_fR_dd')
    differentiated_part=F*sp.trace(delta_Ric)
    current=sp.Matrix([F*sum(Q1[j][i,j]-Q1[i][j,j] for j in range(3))
                       -sum(Fg[j]*Q[i,j] for j in range(3))+Fg[i]*sp.trace(Q) for i in range(3)])
    div=sum(Fg[i]*(Q1[j][i,j]-Q1[i][j,j])+F*(Q2[i][j][i,j]-Q2[i][i][j,j])
            -Fh[i,j]*Q[i,j]-Fg[j]*Q1[i][i,j]+Fh[i,i]*Q[j,j]+Fg[i]*Q1[i][j,j]
            for i in range(3) for j in range(3))
    bulk=sp.expand(differentiated_part-div)
    bulk_matrix=tensor_coefficient(bulk,Q)
    Ng,Rg=vec('N_d'),vec('R_d');Nh,Rh=sym('N_dd'),sym('R_dd')
    def D(expr,i):
        out=sp.diff(expr,N)*Ng[i]+sp.diff(expr,R)*Rg[i]
        return out+sum(sp.diff(expr,Ng[j])*Nh[i,j]+sp.diff(expr,Rg[j])*Rh[i,j] for j in range(3))
    actual_grad=sp.Matrix([D(N*fR,i) for i in range(3)])
    actual_hess=sp.Matrix(3,3,lambda i,j:D(actual_grad[j],i))
    reference_hess=fR*Nh+sp.diff(fR,R)*(Ng*Rg.T+Rg*Ng.T+N*Rh)+N*sp.diff(fR,R,2)*Rg*Rg.T
    metric=f*sp.eye(3)/2-fR*Ric+(Fh-sp.trace(Fh)*sp.eye(3))/N
    return {'Q':Q,'Ricci':Ric,'Q_first_jets':Q1,'Q_second_ordered_jets':Q2,
            'delta_Ricci_from_delta_Christoffel':delta_Ric,'delta_R':scalar_derivative,
            'f':f,'f_R':fR,'lapse_row':f,'shift_row':sp.zeros(3,1),'metric_row':metric,
            'weighted_fR':F,'weighted_fR_gradient':Fg,'weighted_fR_hessian':Fh,
            'weighted_fR_gradient_from_literal':actual_grad,'weighted_fR_hessian_from_literal':actual_hess,
            'current_spatial_without_b_volume_half':current,'current_divergence':div,
            'residuals':{'Ricci_scalar_from_Christoffel':sp.expand(scalar_derivative-scalar_reference),
                         'two_IBP_metric_coefficient':clean(bulk_matrix-(Fh-sp.trace(Fh)*sp.eye(3))),
                         'two_IBP_no_remaining_Q_jets':sp.expand(bulk-pair(bulk_matrix,Q)),
                         'f_R_from_literal_quadratic_R':fR-(xi-B4*R/(8*k*k)),
                         'N_fR_weighted_hessian':clean(actual_hess-reference_hess)}}

def derive_lapse_acceleration_robin(ctx):
    N,V,b,eta,kappa,y,n,e=(ctx[x] for x in ('N','V','b','eta','kappa','y','n','e'))
    Ng,Nh=vec('a_N_d'),sym('a_N_dd')
    v=vec('material_cov');vg=sp.Matrix(3,3,lambda i,j:sp.Symbol(f'material_cov_d{i}_{j}',real=True))
    dn=vec('n_d');Q=sym('a_Q');dv=vec('delta_material_cov')
    a=Ng/N;r=v-y*a
    def D(expr,i):
        return sp.diff(expr,N)*Ng[i]+sum(sp.diff(expr,Ng[j])*Nh[i,j]+sp.diff(expr,v[j])*vg[i,j] for j in range(3))
    divergence_a=sum(D(a[i],i) for i in range(3))
    divergence_r=sum(D(r[i],i) for i in range(3))
    literal_a=b*eta*V*(Ng.T*Ng)[0]/(2*N)
    literal_R=-kappa*N*V*(r.T*r)[0]/2
    def lapse_euler(L):
        return sp.diff(L,N)-sum(D(sp.diff(L,Ng[i]),i) for i in range(3))
    a_euler=clean(lapse_euler(literal_a)/V)
    R_euler=clean(lapse_euler(literal_R)/V)
    a_expected=-b*eta*((a.T*a)[0]+2*divergence_a)/2
    R_expected=-kappa*((r.T*r)[0]+2*y*(divergence_r+(a.T*r)[0]))/2
    inv=sp.eye(3)-e*Q
    moved_a=a+e*dn
    moved_r=v+e*dv-y*moved_a
    raw_a=first(b*eta*N*(1+e*n)*V*(1+e*sp.trace(Q)/2)*(moved_a.T*inv*moved_a)[0]/2,e)
    raw_R=first(-kappa*N*(1+e*n)*V*(1+e*sp.trace(Q)/2)*(moved_r.T*inv*moved_r)[0]/2,e)
    metric_a=b*eta*(sp.eye(3)*(a.T*a)[0]/2-a*a.T)/2
    metric_R=-kappa*(sp.eye(3)*(r.T*r)[0]/2-r*r.T)/2
    current_a=b*eta*N*V*a*n
    current_R=kappa*y*N*V*r*n
    # Covariant D_i(volume)=0; D_i N=N*a_i. The derivatives remain arbitrary.
    div_a=b*eta*N*V*((divergence_a+(a.T*a)[0])*n+(a.T*dn)[0])
    div_R=kappa*y*N*V*((divergence_r+(a.T*r)[0])*n+(r.T*dn)[0])
    rebuilt_a=N*V*(a_euler*n+pair(metric_a,Q))+div_a
    rebuilt_R=N*V*(R_euler*n+pair(metric_R,Q)-kappa*(r.T*dv)[0])+div_R
    actual_da=first((Ng+e*(Ng*n+N*dn))/(N*(1+e*n)),e)
    return {'N_gradient':Ng,'N_hessian':Nh,'material_covector':v,'material_gradient':vg,
            'n_gradient':dn,'Q':Q,'delta_material_covector':dv,'a':a,'r':r,
            'divergence_a':divergence_a,'divergence_r':divergence_r,
            'literal_acceleration_density':literal_a,'literal_Robin_density':literal_R,
            'acceleration_lapse_row':a_euler,'Robin_lapse_row':R_euler,
            'acceleration_metric_row':metric_a,'Robin_covector_metric_row':metric_R,
            'Robin_covector_material_row':-kappa*r,'shift_rows':sp.zeros(3,1),
            'raw_acceleration_variation':raw_a,'raw_Robin_variation':raw_R,
            'acceleration_current_spatial':current_a,'Robin_current_spatial':current_R,
            'acceleration_current_divergence':div_a,'Robin_current_divergence':div_R,
            'residuals':{'delta_a_from_literal_N':clean(actual_da-dn),
                         'acceleration_lapse_from_N_gradient_Euler':clean(a_euler-a_expected),
                         'Robin_lapse_from_N_gradient_Euler':clean(R_euler-R_expected),
                         'acceleration_full_IBP':sp.expand(raw_a-rebuilt_a),
                         'Robin_full_covector_IBP':sp.expand(raw_R-rebuilt_R)}}

def derive_material_charts(ctx):
    N,V,kappa,y,n,e=(ctx[x] for x in ('N','V','kappa','y','n','e'))
    Q=sym('chart_Q');phi=vec('phi');Pi=vec('Pi');dphi=vec('delta_phi');a=vec('chart_a');dn=vec('chart_n_d')
    inv=sp.eye(3)-e*Q;frame=sp.eye(3)-e*Q/2;coframe=sp.eye(3)+e*Q/2
    moved_phi=phi+e*dphi
    moved_v_contra=frame*moved_phi;moved_v_cov=coframe*moved_phi
    r=phi-y*a
    literal_R=-kappa*N*(1+e*n)*V*(1+e*sp.trace(Q)/2)*((moved_v_cov-y*(a+e*dn)).T*inv*(moved_v_cov-y*(a+e*dn)))[0]/2
    raw_R=first(literal_R,e)/(N*V)
    Eh_int=-kappa*(sp.eye(3)*(r.T*r)[0]/2+y*sym_outer(r,a))/2
    Eh_cov_R=-kappa*(sp.eye(3)*(r.T*r)[0]/2-r*r.T)/2
    Eh_vec_R=-kappa*(sp.eye(3)*(r.T*r)[0]/2-r*r.T+2*sym_outer(r,phi))/2
    E_total=-Pi-kappa*r
    Eh_cov=Eh_cov_R+sym_outer(Pi,phi)/2
    Eh_vec=Eh_vec_R-sym_outer(Pi,phi)/2
    delta_v_contra=first(moved_v_contra,e);delta_v_cov=first(moved_v_cov,e)
    green_internal=-(Pi.T*dphi)[0]
    green_vector=-(Pi.T*delta_v_contra)[0]-pair(sym_outer(Pi,phi),Q)/2
    green_covector=-(Pi.T*delta_v_cov)[0]+pair(sym_outer(Pi,phi),Q)/2
    rot=sp.Matrix([[0,sp.Symbol('rho01'),sp.Symbol('rho02')],[-sp.Symbol('rho01'),0,sp.Symbol('rho12')],[-sp.Symbol('rho02'),-sp.Symbol('rho12'),0]])
    passive=first((sp.eye(3)+e*rot)*(phi-e*rot*phi),e)
    shift,row=vec('shift_chart'),vec('shift_Euler');dshift=vec('shift_delta')
    lower_shift_delta=dshift+Q*shift
    shift_chart_residual=pair(-sym_outer(row,shift),Q)+(row.T*lower_shift_delta)[0]-(row.T*dshift)[0]
    return {'Q':Q,'phi':phi,'Pi':Pi,'a':a,'r':r,'delta_phi':dphi,
            'delta_v_contravariant':delta_v_contra,'delta_v_covariant':delta_v_cov,
            'raw_Robin_internal':raw_R,'Robin_internal_metric_row':Eh_int,
            'Robin_covector_metric_row':Eh_cov_R,'Robin_vector_metric_row':Eh_vec_R,
            'total_covector_metric_row':Eh_cov,'total_vector_metric_row':Eh_vec,
            'total_internal_metric_row':Eh_int,'total_material_Euler_row':E_total,
            'Green_internal':green_internal,'Green_vector':green_vector,'Green_covector':green_covector,
            'residuals':{'upper_frame_constraint_first_jet':first(frame.T*(sp.eye(3)+e*Q)*frame-sp.eye(3),e),
                         'coframe_constraint_first_jet':first(coframe.T*inv*coframe-sp.eye(3),e),
                         'Robin_horizontal_metric_from_literal_action':clean(tensor_coefficient(raw_R,Q)-Eh_int),
                         'canonical_internal_to_vector_Green':sp.expand(green_vector-green_internal),
                         'canonical_internal_to_covector_Green':sp.expand(green_covector-green_internal),
                         'total_covector_to_internal_Euler_adjoint':clean(Eh_int-Eh_cov-sym_outer(phi,E_total)/2),
                         'total_vector_to_internal_Euler_adjoint':clean(Eh_int-Eh_vec+sym_outer(phi,E_total)/2),
                         'passive_frame_rotation_cancels':passive,
                         'contravariant_to_covariant_shift_adjoint':sp.expand(shift_chart_residual)}}

def derive_khronon(ctx):
    N=sp.Symbol('N_T',positive=True);e=ctx['e'];grad=vec('delta_T_gradient',4)
    eta=sp.diag(-1,1,1,1);background=sp.Matrix([1/N,0,0,0])
    moved=background+e*grad
    lapse=(-(moved.T*eta*moved)[0])**sp.Rational(-1,2)
    actual=first(-lapse*moved,e)
    reference=sp.Matrix([0,-N*grad[1],-N*grad[2],-N*grad[3]])
    J=vec('clock_current_density',4);divJ=sp.Symbol('clock_current_divergence',real=True);tau=sp.Symbol('delta_T',real=True)
    raw=-(J.T*grad)[0];current=-J*tau
    current_divergence=-divJ*tau-(J.T*grad)[0]
    return {'delta_u':actual,'reference':reference,'current':current,'Euler_density':divJ,
            'raw':raw,'residuals':{'u_from_literal_normalized_T_gradient':clean(actual-reference),
                                 'clock_IBP_adjoint_sign':sp.expand(raw-divJ*tau-current_divergence)},
            'scope':'E_T=div(N_T h E_u); E_u must already be the TOTAL Euler row, not expanded here'}

def derive_model():
    ctx=symbols_context()
    parts={'kinetic':derive_kinetic(ctx),'transport':derive_transport_ibp(),
           'curvature':derive_curvature(ctx),'lapse_acceleration_Robin':derive_lapse_acceleration_robin(ctx),
           'material_charts':derive_material_charts(ctx),'khronon':derive_khronon(ctx)}
    checks={part+'_'+name:zero(res) for part,data in parts.items() for name,res in data['residuals'].items()}
    t=parts['transport'];c=parts['material_charts'];a=parts['lapse_acceleration_Robin'];curv=parts['curvature']
    witnesses={
        'omit_density_weight_one':sp.trace(t['shift_gradient'])*pair(t['pi_density'],t['Q']),
        'halve_shift_Euler_row':(t['shift_row'].T*t['delta_shift'])[0]/2,
        'reverse_Robin_lapse_current':2*a['Robin_current_divergence'],
        'freeze_internal_covector_in_metric_variation':c['Robin_covector_metric_row']-c['Robin_internal_metric_row'],
        'omit_vector_Green_metric_adjoint':pair(sym_outer(c['Pi'],c['phi']),c['Q'])/2,
        'apply_Robin_chart_change_without_bulk_Green':c['Robin_internal_metric_row']-c['total_covector_metric_row']-sym_outer(c['phi'],-ctx['kappa']*c['r'])/2,
        'freeze_weight_N_inside_f_R_derivatives':curv['weighted_fR_hessian_from_literal']-ctx['N']*sp.diff(curv['f_R'],ctx['R'])*sym('R_dd'),
        'reverse_khronon_IBP_Euler_sign':2*parts['khronon']['Euler_density']}
    controls={name:not zero(res) for name,res in witnesses.items()}
    return {'symbols':ctx,'parts':parts,'checks':checks,'negative_controls':controls,'negative_witnesses':witnesses,
            'conventions':{'metric_variable':'h_ij covariant','shift_variable':'N^i contravariant',
                           'transport_weight':'sqrt(h) C^ij is a tensor density of weight +1',
                           'material_origin':'canonical Green -Pi_a delta(phi_a); three charts transformed together',
                           'spatial_normal_frame':'pointwise only; N,K,a,shift,Ricci and their jets remain arbitrary'},
            'scope':{'literal_nonlinear_fixed_clock_ADM_rows_and_currents':True,
                     'total_material_Green_chart_adjoint_exact':True,
                     'covariant_khronon_chain_adjoint_checked':True,
                     'all_covariant_E_u_coefficients_expanded':False,
                     'all_bulk_GHY_shape_groupoid_rows_derived':False,
                     'complete_moving_interface_Green_certified':False,
                     'BF_global_or_frame_sector_eliminated':False,
                     'N4_JUNCTION_BENDING_pass':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}

def _serialize(x):
    if isinstance(x,sp.MatrixBase):return _serialize(x.tolist())
    if isinstance(x,sp.Basic):return str(x)
    if isinstance(x,dict):return {str(k):_serialize(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [_serialize(v) for v in x]
    return x

def load_sources(note_path=NOTE,candidate_path=CANDIDATE,inventory_path=INVENTORY):
    bindings={}
    for kind,path,digest in [('note',Path(note_path),NOTE_SHA256),('candidate',Path(candidate_path),CANDIDATE_SHA256),('inventory',Path(inventory_path),INVENTORY_SHA256)]:
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ADMEulerError(kind+' byte hash mismatch')
        bindings[kind]={'name':path.name,'sha256':digest}
    candidate=json.loads(Path(candidate_path).read_bytes())
    action=candidate['exact_classical_charter']['exact_action']
    expected_fol='S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-B4_bar*Rcal^2/(16*k_infinity^2)]'
    expected_R='S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)'
    if action['foliation_lower']!=expected_fol or action['Robin_intrinsic']!=expected_R:
        raise ADMEulerError('literal foliation/Robin action changed')
    bindings['literal_action']={'foliation':action['foliation_lower'],'Robin':action['Robin_intrinsic']}
    bindings['inventory_gates_inherited']=False
    return bindings

def build_payload(note_path=NOTE,candidate_path=CANDIDATE,inventory_path=INVENTORY):
    sources=load_sources(note_path,candidate_path,inventory_path)
    model=derive_model()
    if not all(model['checks'].values()) or not all(model['negative_controls'].values()):raise ADMEulerError('ADM/Robin identity or mutant failed')
    doc={'schema':SCHEMA,'sources':sources,'model':_serialize(model),'checks':model['checks'],
         'negative_controls':model['negative_controls'],'decision':model['scope'],
         'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
         'runtime':{'sympy':sp.__version__}}
    doc['calculation_digest']=canonical_digest(doc)
    return doc

def validate_payload(doc,note_path=NOTE,candidate_path=CANDIDATE,inventory_path=INVENTORY):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:raise ADMEulerError('ADM receipt schema mismatch')
    if doc.get('calculation_digest')!=canonical_digest({k:v for k,v in doc.items() if k!='calculation_digest'}):raise ADMEulerError('ADM receipt digest mismatch')
    if doc!=build_payload(note_path,candidate_path,inventory_path):raise ADMEulerError('ADM receipt differs from fresh derivation')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path);modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args(argv)
    if args.write is not None:
        doc=build_payload();args.write.parent.mkdir(parents=True,exist_ok=True)
        with args.write.open('x',encoding='utf8') as f:json.dump(doc,f,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
    else:
        doc=json.loads(args.verify.read_bytes());validate_payload(doc)
    print(json.dumps({'checks_passed':sum(doc['checks'].values()),'negative_controls':doc['negative_controls'],'calculation_digest':doc['calculation_digest']}))

if __name__=='__main__':main()
