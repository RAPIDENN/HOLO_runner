"""Independent linear projected SO(3) connection and proposed C-squared term.

The metric, clock normal and horizontal frame vary together. The proposed
operator is not part of the pinned v5.2 action. This module proves local
linear geometry and restricted quadratic identities, not an extended
boundary theory, physical mode count or a positive-real kernel theorem.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_projected_connection_linear_lemma_v1.md'
TEST=HERE/'test_one_omega_projected_connection_linear_v1.py'
CANDIDATE=HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
OUTPUT=HERE/'artifacts/one_omega_projected_connection_linear_v1.json'
NOTE_SHA256='5eb335367c04c17930c42f18310b1750774088baafdff5906565232a3d40856a'
CANDIDATE_SHA256='d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
SCHEMA='holo.one-omega-projected-connection-linear.v1'

class ProjectedConnectionError(ValueError):
    pass

def canonical_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
        ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def symmetric(prefix,size=3):
    return sp.Matrix(size,size,lambda i,j:sp.Symbol(f'{prefix}_{min(i,j)}{max(i,j)}',real=True))

def antisymmetric(prefix):
    return sp.Matrix(3,3,lambda i,j:0 if i==j else
        (1 if i<j else -1)*sp.Symbol(f'{prefix}_{min(i,j)}{max(i,j)}',real=True))

def vector(prefix,size=3):
    return sp.Matrix([sp.Symbol(f'{prefix}_{i}',real=True) for i in range(size)])

def inner(X,Y):
    return sum(X[a,b]*Y[a,b] for a in range(3) for b in range(3))/2

def clean(value):
    if isinstance(value,sp.MatrixBase):return value.applyfunc(sp.cancel)
    return sp.cancel(value)

def zero(value):
    if isinstance(value,(tuple,list)):return all(zero(x) for x in value)
    if isinstance(value,sp.MatrixBase):return all(sp.cancel(x)==0 for x in value)
    return sp.cancel(value)==0

def first(value,e):
    if isinstance(value,sp.MatrixBase):return value.applyfunc(lambda x:sp.diff(x,e).subs(e,0))
    return sp.diff(value,e).subs(e,0)

def symbols_context():
    return {'epsilon':sp.Symbol('epsilon',real=True),'chi':sp.Symbol('chi',positive=True),
            'n':sp.Symbol('n',real=True),'n_gradient':vector('n_d',4),
            'shift':vector('N'),'shift_gradient':[vector(f'N_d{mu}') for mu in range(4)],
            'H':symmetric('H'),'H_gradient':[symmetric(f'H_d{mu}') for mu in range(4)],
            'tau_gradient':vector('tau_d',4),'tau_hessian':symmetric('tau_dd',4),
            'rho':antisymmetric('rho'),'rho_gradient':[antisymmetric(f'rho_d{mu}') for mu in range(4)],
            'A':[antisymmetric(f'A{mu}') for mu in range(4)],
            'q':sp.Symbol('q',positive=True),'s':sp.Symbol('s',nonzero=True),
            'B':sp.Symbol('B'),
            'h_t':sp.Symbol('h_t',real=True),'h_z':sp.Symbol('h_z',real=True),
            'zeta_t':sp.Symbol('zeta_t',real=True),'zeta_z':sp.Symbol('zeta_z',real=True),
            'theta_t':sp.Symbol('theta_t',real=True),'theta_z':sp.Symbol('theta_z',real=True),
            'theta':sp.Symbol('theta',real=True),'N_z':sp.Symbol('N_z',real=True),
            'N_mode':sp.Symbol('N_mode',real=True),
            'vector_H_t':sp.Symbol('H13_t',real=True),'vector_H_z':sp.Symbol('H13_z',real=True),
            'U':sp.Symbol('U',real=True),'Psi_t':sp.Symbol('Psi_t',real=True),
            'Psi_z':sp.Symbol('Psi_z',real=True)}

def derive_geometry(ctx):
    e=ctx['epsilon'];eta=sp.diag(-1,1,1,1)
    h=sp.zeros(4);h[0,0]=-2*ctx['n']
    for i in range(3):h[0,i+1]=h[i+1,0]=ctx['shift'][i]
    h[1:4,1:4]=ctx['H']
    dh=[]
    for mu in range(4):
        jet=sp.zeros(4);jet[0,0]=-2*ctx['n_gradient'][mu]
        for i in range(3):jet[0,i+1]=jet[i+1,0]=ctx['shift_gradient'][mu][i]
        jet[1:4,1:4]=ctx['H_gradient'][mu];dh.append(jet)
    inv1=-eta*h*eta
    e0=sp.zeros(4,3);e0[1:4,0:3]=sp.eye(3)
    e1=sp.zeros(4,3)
    for a in range(3):e1[0,a]=-ctx['tau_gradient'][a+1]
    e1[1:4,0:3]=-ctx['H']/2
    de1=[]
    for mu in range(4):
        jet=sp.zeros(4,3)
        for a in range(3):jet[0,a]=-ctx['tau_hessian'][mu,a+1]
        jet[1:4,0:3]=-ctx['H_gradient'][mu]/2;de1.append(jet)
    gradient_T=sp.Matrix([1,0,0,0])+e*ctx['tau_gradient']
    lapse_T=(-(gradient_T.T*(eta+e*inv1)*gradient_T)[0])**sp.Rational(-1,2)
    u0=sp.Matrix([-1,0,0,0]);u1=first(-lapse_T*gradient_T,e)
    expected_u=sp.Matrix([-ctx['n'],*[-ctx['tau_gradient'][i] for i in range(1,4)]])
    Gamma=[]
    for mu in range(4):
        Gamma.append(sp.Matrix(4,4,lambda nu,rho:
            eta[nu,nu]*(dh[mu][nu,rho]+dh[rho][nu,mu]-dh[nu][mu,rho])/2))
    # These are the separate product-rule terms of e^T gamma (de+Gamma e)
    # at a constant frame and vanishing connection background.
    frame_term=[e0.T*eta*jet for jet in de1]
    christoffel_term=[e0.T*eta*G*e0 for G in Gamma]
    omega=[clean(frame_term[mu]+christoffel_term[mu]) for mu in range(4)]
    expected=[sp.Matrix(3,3,lambda a,b:(dh[b+1][a+1,mu]-dh[a+1][mu,b+1])/2) for mu in range(4)]
    rotated_frame=e1+e0*ctx['rho']
    rotated=[clean(e0.T*eta*(de1[mu]+e0*ctx['rho_gradient'][mu])+christoffel_term[mu]) for mu in range(4)]
    excluded_lapse=[ctx['n'],*ctx['n_gradient']]
    excluded_clock=[*ctx['tau_gradient'],*sorted(set(ctx['tau_hessian']),key=str)]
    excluded_time=[*sorted(set(ctx['H_gradient'][0]),key=str),*ctx['shift_gradient'][0]]
    def excluded_residual(symbols):
        return sp.Matrix([sp.diff(entry,x) for matrix in omega for entry in matrix for x in symbols])
    # A constant, proper, nontrivial rotation, independent of the input jets.
    R=sp.Matrix([[sp.Rational(3,5),-sp.Rational(4,5),0],
                 [sp.Rational(4,5),sp.Rational(3,5),0],[0,0,1]])
    omega_constant_R=[clean((e0*R).T*eta*(de1[mu]*R+Gamma[mu]*e0*R)) for mu in range(4)]
    C=[ctx['A'][mu]-omega[mu] for mu in range(4)]
    Crot=[ctx['A'][mu]+ctx['rho_gradient'][mu]-rotated[mu] for mu in range(4)]
    residuals={
        'inverse_metric_product_rule':eta*inv1+h*eta,
        'normalized_clock_from_literal_gradient':clean(u1-expected_u),
        'clock_unit_norm_first_jet':clean((2*u0.T*eta*u1+u0.T*inv1*u0)[0]),
        'frame_orthonormal_first_jet':clean(e1.T*eta*e0+e0.T*eta*e1+e0.T*h*e0),
        'frame_clock_orthogonality':clean(u0.T*e1+u1.T*e0),
        'rotated_frame_orthonormal_first_jet':clean(rotated_frame.T*eta*e0+e0.T*eta*rotated_frame+e0.T*h*e0),
        'all_36_connection_entries':[(omega[mu]-expected[mu]) for mu in range(4)],
        'SO3_antisymmetry':[w+w.T for w in omega],
        'lapse_cancels':excluded_residual(excluded_lapse),
        'clock_and_second_jets_cancel':excluded_residual(excluded_clock),
        'metric_and_shift_time_jets_cancel':excluded_residual(excluded_time),
        'frame_rotation_inhomogeneous_sign':[rotated[mu]-omega[mu]-ctx['rho_gradient'][mu] for mu in range(4)],
        'simultaneous_gauge_frame_C_invariant':[Crot[mu]-C[mu] for mu in range(4)],
        'constant_rotation_orthogonal':R.T*R-sp.eye(3),
        'constant_rotation_proper':R.det()-1,
        'constant_rotation_connection_covariance':[omega_constant_R[mu]-R.T*omega[mu]*R for mu in range(4)]}
    return {'eta':eta,'metric_first_jet':h,'metric_gradient_first_jets':dh,'inverse_first_jet':inv1,
            'frame_background':e0,'frame_first_jet':e1,'frame_gradient_first_jets':de1,
            'clock_first_jet':u1,'clock_lapse_first_jet':first(lapse_T,e),
            'Christoffel_first_jets':Gamma,'frame_connection_parts':frame_term,
            'Christoffel_connection_parts':christoffel_term,'omega':omega,'omega_expected':expected,
            'omega_rotated':rotated,'C':C,'C_rotated':Crot,
            'constant_rotation':R,'omega_constant_rotation':omega_constant_R,
            'excluded_lapse_symbols':excluded_lapse,'excluded_clock_symbols':excluded_clock,
            'excluded_time_symbols':excluded_time,'residuals':residuals}

def derive_quadratic(ctx,geometry):
    chi,e=ctx['chi'],ctx['epsilon'];eta=geometry['eta'];C=geometry['C']
    volume1=sp.trace(eta*geometry['metric_first_jet'])/2
    # C starts at order epsilon. Extract the coefficient on the metric/Hodge
    # weight term by term; this avoids expanding irrelevant cubic expressions.
    L2=0
    for mu in range(4):
        for nu in range(4):
            weight=e*e*(1+e*volume1)*(eta[mu,nu]+e*geometry['inverse_first_jet'][mu,nu])
            coefficient=sp.diff(weight,e,2).subs(e,0)/2
            L2-=chi*coefficient*inner(C[mu],C[nu])/2
    reference=chi*(inner(C[0],C[0])-sum(inner(x,x) for x in C[1:]))/2
    zero_jets={x:0 for matrix in geometry['metric_gradient_first_jets'] for x in matrix.free_symbols}
    zero_A={x:0 for matrix in ctx['A'] for x in matrix.free_symbols}
    baseline={**zero_jets,**zero_A}
    def sliced(overrides):return sp.expand(L2.subs({**baseline,**overrides},simultaneous=True))
    Ht,Hz=ctx['H_gradient'][0],ctx['H_gradient'][3]
    TT=sliced({Ht[0,1]:ctx['h_t'],Hz[0,1]:ctx['h_z']})
    scalar=sliced({**{Ht[i,i]:2*ctx['zeta_t'] for i in range(3)},
                   **{Hz[i,i]:2*ctx['zeta_z'] for i in range(3)}})
    shift=sliced({ctx['shift_gradient'][3][0]:ctx['N_z']})
    vector=sliced({ctx['shift_gradient'][3][0]:ctx['N_z'],
                   ctx['A'][0][0,2]:ctx['theta_t'],ctx['A'][3][0,2]:ctx['theta_z']})
    vector_reference=chi*((ctx['theta_t']-ctx['N_z']/2)**2-ctx['theta_z']**2)/2
    vector_full=sliced({ctx['shift_gradient'][3][0]:ctx['N_z'],
        Ht[0,2]:ctx['vector_H_t'],Hz[0,2]:ctx['vector_H_z'],
        ctx['A'][0][0,2]:ctx['theta_t'],ctx['A'][3][0,2]:ctx['theta_z']})
    vector_full_reference=chi*((ctx['theta_t']-ctx['N_z']/2)**2-(ctx['theta_z']-ctx['vector_H_z']/2)**2)/2
    scalar_longitudinal=sliced({**{Hz[i,i]:2*ctx['zeta_z'] for i in range(3)},
                               ctx['A'][0][0,2]:ctx['theta_t'],ctx['A'][3][0,2]:ctx['theta_z']})
    TT_omega=[w.subs({**zero_jets,Ht[0,1]:ctx['h_t'],Hz[0,1]:ctx['h_z']},simultaneous=True) for w in geometry['omega']]
    scalar_omega=[w.subs({**zero_jets,**{Hz[i,i]:2*ctx['zeta_z'] for i in range(3)}},simultaneous=True) for w in geometry['omega']]
    residuals={'Lorentz_Hodge_quadratic_from_metric_weight':sp.expand(L2-reference),
               'TT_gradient_factor':TT+chi*ctx['h_z']**2/4,
               'TT_no_time_kinetic_added':sp.diff(TT,ctx['h_t']),
               'scalar_trace_gradient_factor':scalar+chi*ctx['zeta_z']**2,
               'scalar_no_time_kinetic_added':sp.diff(scalar,ctx['zeta_t']),
               'shift_curl_factor':shift-chi*ctx['N_z']**2/8,
               'vector_connection_shift_mixing':sp.expand(vector-vector_reference),
               'vector_before_H13_gauge_choice':sp.expand(vector_full-vector_full_reference),
               'scalar_longitudinal_connection_no_cross_term':sp.expand(scalar_longitudinal+chi*ctx['zeta_z']**2-chi*(ctx['theta_t']**2-ctx['theta_z']**2)/2)}
    return {'C':C,'metric_volume_first_jet':volume1,'L_C2':L2,'Hodge_reference':reference,
            'TT_slice':TT,'TT_omega':TT_omega,'scalar_slice':scalar,'scalar_omega':scalar_omega,
            'shift_slice':shift,'vector_slice':vector,'vector_full_slice':vector_full,'scalar_with_longitudinal_connection_slice':scalar_longitudinal,
            'residuals':residuals}

def derive_vector_algebra(ctx,quadratic):
    q,B,chi,N,td,theta,s=(ctx[k] for k in ('q','B','chi','N_mode','theta_t','theta','s'))
    total=q*q*B*N*N/4+quadratic['vector_slice'].subs({ctx['N_z']:q*N,ctx['theta_z']:q*theta})
    row=sp.diff(total,N);pivot=sp.diff(row,N)
    stationary=clean(-row.subs(N,0)/pivot)
    reduced=clean(total.subs(N,stationary));Keff=clean(sp.diff(reduced,td,2))
    harmonic=1/(1/(chi*s)+1/(2*s*B))
    full_total=B*(ctx['N_z']-ctx['vector_H_t'])**2/4+quadratic['vector_full_slice']
    invariant_total=sp.expand(full_total.subs({ctx['N_z']:ctx['U']+ctx['vector_H_t'],
        ctx['theta_t']:ctx['Psi_t']+ctx['vector_H_t']/2,
        ctx['theta_z']:ctx['Psi_z']+ctx['vector_H_z']/2},simultaneous=True))
    invariant_reference=B*ctx['U']**2/4+chi*((ctx['Psi_t']-ctx['U']/2)**2-ctx['Psi_z']**2)/2
    gauge_tz,gauge_zz=sp.symbols('xi1_tz xi1_zz',real=True)
    gauge_variation=gauge_tz*(sp.diff(full_total,ctx['N_z'])+sp.diff(full_total,ctx['vector_H_t'])
        +sp.diff(full_total,ctx['theta_t'])/2)+gauge_zz*(sp.diff(full_total,ctx['vector_H_z'])
        +sp.diff(full_total,ctx['theta_z'])/2)
    residuals={'N_stationarity':clean(row.subs(N,stationary)),
               'N_solution_factor':clean(stationary-2*chi*td/(q*(2*B+chi))),
               'effective_time_coefficient':clean(Keff-2*chi*B/(2*B+chi)),
               'full_reduced_density':clean(reduced-Keff*td*td/2+chi*q*q*theta*theta/2),
               'harmonic_identity_only':clean(s*Keff-harmonic),
               'vector_gauge_invariant_combinations':sp.expand(invariant_total-invariant_reference),
               'spatial_diffeomorphism_with_horizontal_frame_compensation':sp.expand(gauge_variation)}
    return {'input_old_vector_density':q*q*B*N*N/4,'total_density':total,'N_Euler':row,'N_pivot':pivot,
            'N_stationary':stationary,'reduced_density':reduced,
            'full_vector_density_before_gauge_choice':full_total,
            'gauge_invariant_density':invariant_total,'K_eff':Keff,'s_K_eff_harmonic':harmonic,
            'domain':'q>0; 2B+chi != 0; harmonic form additionally B != 0 and s != 0',
            'kernel_regular_or_positive_real_proved':False,'residuals':residuals}

def derive_model():
    ctx=symbols_context();geometry=derive_geometry(ctx);quadratic=derive_quadratic(ctx,geometry)
    vector=derive_vector_algebra(ctx,quadratic)
    parts={'geometry':geometry,'quadratic':quadratic,'vector_algebra':vector}
    checks={part+'_'+name:zero(value) for part,data in parts.items() for name,value in data['residuals'].items()}
    chi=ctx['chi']
    witnesses={
        'freeze_horizontal_frame':geometry['Christoffel_connection_parts'][0]-geometry['omega'][0],
        'reverse_shift_curl_sign':2*geometry['omega'][0],
        'inject_symmetric_tau_second_derivative':ctx['tau_hessian'][1,2],
        'replace_Lorentz_Hodge_by_Euclidean':-chi*inner(geometry['C'][0],geometry['C'][0]),
        'rotate_frame_without_A':-ctx['rho_gradient'][0],
        'halve_TT_Frobenius_contribution':quadratic['TT_slice']+chi*ctx['h_z']**2/8,
        'halve_scalar_trace_contribution':quadratic['scalar_slice']+chi*ctx['zeta_z']**2/2,
        'omit_shift_connection_half':clean(vector['K_eff']-chi*ctx['B']/(ctx['B']+2*chi))}
    controls={name:not zero(value) for name,value in witnesses.items()}
    return {'symbols':ctx,**parts,'checks':checks,'negative_controls':controls,'negative_witnesses':witnesses,
            'conventions':{'signature':'(-,+,+,+)','connection':'omega_mu,ab=e_a,nu nabla_mu e_b^nu',
                'frame':'columns e_a^mu; horizontal spatial first jet -H/2; e_a^0=-partial_a tau',
                'rotation':'e->eR, omega->R^T omega R+R^T dR; A transforms in the same convention',
                'SO3_inner_product':'tr(X^T Y)/2 = sum_(a<b) X_ab Y_ab',
                'Hodge':'Lorentzian induced metric in four interface dimensions'},
            'scope':{'proposed_extension_not_in_v5_2':True,'linear_dynamic_projected_connection_derived':True,
                'restricted_C_squared_densities_derived':True,'vector_stationary_elimination_algebra_checked':True,
                'A_identified_with_omega':False,'A_zero_slices_asserted_as_full_solutions':False,
                'extended_action_full_boundary_variation_derived':False,'full_scalar_pivots_rederived':False,
                'kernel_positive_real_or_pole_exclusion_proved':False,'physical_modes_or_stability_certified':False,
                'nonlinear_higher_derivative_absence_proved':False,'BF_BFV_or_embedding_closed':False,
                'N4_JUNCTION_BENDING_pass':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}

def _serialize(value):
    if isinstance(value,sp.MatrixBase):return _serialize(value.tolist())
    if isinstance(value,sp.Basic):return str(value)
    if isinstance(value,dict):return {str(k):_serialize(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [_serialize(v) for v in value]
    return value

def load_sources(note_path=NOTE,candidate_path=CANDIDATE):
    sources={}
    for kind,path,digest in [('note',Path(note_path),NOTE_SHA256),('candidate',Path(candidate_path),CANDIDATE_SHA256)]:
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ProjectedConnectionError(kind+' byte hash mismatch')
        sources[kind]={'name':path.name,'sha256':digest}
    action=json.loads(Path(candidate_path).read_bytes())['exact_classical_charter']['exact_action']
    sources['base_action_digest']=canonical_digest(action)
    sources['candidate_gates_inherited']=False
    sources['proposed_operator']='S_C=-chi/2 integral <(A_Sigma-omega) wedge *_gamma (A_Sigma-omega)>'
    sources['operator_status']='proposal only; not applied to the pinned candidate action'
    return sources

def build_payload(note_path=NOTE,candidate_path=CANDIDATE):
    sources=load_sources(note_path,candidate_path);model=derive_model()
    if not all(model['checks'].values()) or not all(model['negative_controls'].values()):
        raise ProjectedConnectionError('projected connection identity or negative control failed')
    doc={'schema':SCHEMA,'sources':sources,'model':_serialize(model),'checks':model['checks'],
         'negative_controls':model['negative_controls'],'decision':model['scope'],
         'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
         'runtime':{'sympy':sp.__version__}}
    doc['calculation_digest']=canonical_digest(doc)
    return doc

def validate_payload(doc,note_path=NOTE,candidate_path=CANDIDATE):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:raise ProjectedConnectionError('receipt schema mismatch')
    if doc.get('calculation_digest')!=canonical_digest({k:v for k,v in doc.items() if k!='calculation_digest'}):
        raise ProjectedConnectionError('receipt digest mismatch')
    if doc!=build_payload(note_path,candidate_path):raise ProjectedConnectionError('receipt differs from fresh derivation')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path)
    modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args(argv)
    if args.write is not None:
        doc=build_payload();args.write.parent.mkdir(parents=True,exist_ok=True)
        with args.write.open('x',encoding='utf8') as f:
            json.dump(doc,f,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
    else:
        doc=json.loads(args.verify.read_bytes());validate_payload(doc)
    print(json.dumps({'checks_passed':sum(doc['checks'].values()),'negative_controls':doc['negative_controls'],
                      'calculation_digest':doc['calculation_digest']}))

if __name__=='__main__':main()
