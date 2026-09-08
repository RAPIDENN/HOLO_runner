"""Local ADM velocity Hessian of the unadopted connection-current candidate."""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent
PROOF=HERE/'one_omega_connection_adm_kinetic_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_adm_kinetic_v1.py'
SOURCE=HERE/'artifacts/one_omega_connection_horizontal_ward_v1.json'
OUTPUT=HERE/'artifacts/one_omega_connection_adm_kinetic_v1.json'
PROOF_SHA='5d57ffa5829861d812253731f3c165ede8eba90cfc9d022aba6f9976471274f7'
SOURCE_SHA='d26d2cf58092eecacebd1f8d7f34f8a35222cd1ef7ec7153f5f0675a7e7e1f89'
SCHEMA='holo.one-omega-connection-adm-kinetic.v1'


class ADMKineticError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def clean(x):
    return x.applyfunc(sp.cancel) if isinstance(x,sp.MatrixBase) else sp.cancel(x)


def zero(x):
    if isinstance(x,sp.MatrixBase):return all(v==0 for v in x)
    if isinstance(x,(tuple,list)):return all(zero(v) for v in x)
    return x==0


def inner(A,B):
    return sum(A[i,j]*B[i,j] for i in range(3) for j in range(3))/2


def hodge_adm():
    N,chi,l1,l2,l3=sp.symbols('N chi l1 l2 l3',positive=True)
    l21,l31,l32=sp.symbols('l21 l31 l32',real=True)
    L=sp.Matrix([[l1,0,0],[l21,l2,0],[l31,l32,l3]])
    h=L*L.T;Li=L.inv();hi=Li.T*Li
    shift=sp.Matrix(sp.symbols('shift1:4',real=True));cov_shift=h*shift
    g=sp.zeros(4);g[0,0]=-N*N+(shift.T*h*shift)[0]
    g[0,1:4]=cov_shift.T;g[1:4,0]=cov_shift;g[1:4,1:4]=h
    inverse=sp.zeros(4);inverse[0,0]=-1/N**2
    inverse[0,1:4]=shift.T/N**2;inverse[1:4,0]=shift/N**2
    inverse[1:4,1:4]=hi-shift*shift.T/N**2
    shear=sp.eye(4);shear[1:4,0]=shift
    diagonal=sp.zeros(4);diagonal[0,0]=-N*N;diagonal[1:4,1:4]=h
    sqrt_h=l1*l2*l3;volume=N*sqrt_h
    C=[sp.Matrix(sp.symbols(f'C{mu}_1:4',real=True)) for mu in range(4)]
    density=-chi*volume*sum(inverse[mu,nu]*C[mu].dot(C[nu]) for mu in range(4) for nu in range(4))/2
    temporal=C[0]-sum((shift[i]*C[i+1] for i in range(3)),sp.zeros(3,1))
    reference=chi*sqrt_h*temporal.dot(temporal)/(2*N)
    reference-=chi*N*sqrt_h*sum(hi[i,j]*C[i+1].dot(C[j+1]) for i in range(3) for j in range(3))/2
    residuals={'ADM_inverse_all_16_entries':clean(g*inverse-sp.eye(4)),
               'ADM_metric_exact_shear_congruence':clean(g-shear.T*diagonal*shear),
               'unit_determinant_ADM_shear':clean(shear.det()-1),
               'SPD_Cholesky_volume':clean(h.det()-sqrt_h**2),
               'Lorentzian_Hodge_exact_temporal_square':clean(density-reference)}
    return {'N':N,'chi':chi,'cholesky':L,'h':h,'inverse_h':hi,'shift':shift,'metric':g,
            'inverse_metric':inverse,'sqrt_h':sqrt_h,'volume':volume,'C':C,
            'temporal_combination':temporal,'density':density,'ADM_density':reference,'residuals':residuals}


def lower_christoffel():
    coords=sp.symbols('t x y z',real=True);t=coords[0]
    N=sp.Function('lapse')(*coords)
    hs={(i,j):sp.Function(f'h{i+1}{j+1}')(*coords) for i in range(3) for j in range(i,3)}
    h=sp.Matrix(3,3,lambda i,j:hs[min(i,j),max(i,j)])
    shift=sp.Matrix([sp.Function(f'shift{i+1}')(*coords) for i in range(3)])
    cov_shift=h*shift
    g=sp.zeros(4);g[0,0]=-N*N+(shift.T*h*shift)[0]
    g[0,1:4]=cov_shift.T;g[1:4,0]=cov_shift;g[1:4,1:4]=h
    def lower(i,mu,j):
        return sp.expand((sp.diff(g[i+1,j+1],coords[mu])+sp.diff(g[i+1,mu],coords[j+1])
                          -sp.diff(g[mu,j+1],coords[i+1]))/2)
    all_lower=[sp.Matrix(3,3,lambda i,j:lower(i,mu,j)) for mu in range(4)]
    curl=sp.Matrix(3,3,lambda i,j:sp.diff(cov_shift[i],coords[j+1])-sp.diff(cov_shift[j],coords[i+1]))
    time_reference=h.diff(t)/2+curl/2
    spatial_reference=[sp.Matrix(3,3,lambda j,k:(sp.diff(h[j,k],coords[i+1])
                   +sp.diff(h[j,i],coords[k+1])-sp.diff(h[i,k],coords[j+1]))/2) for i in range(3)]
    forbidden=[sp.diff(N,t)]+[sp.diff(v,t) for v in shift]
    residuals={'lower_Gamma_time_all_9_entries':(all_lower[0]-time_reference).applyfunc(sp.expand),
               'lower_Gamma_spatial_all_27_entries':[(a-b).applyfunc(sp.expand) for a,b in zip(all_lower[1:],spatial_reference)],
               'no_lapse_or_shift_velocities_in_lower_Gamma':
                   [sp.diff(entry,v) for matrix in all_lower for entry in matrix for v in forbidden]}
    return {'coords':coords,'lapse':N,'h':h,'shift':shift,'covariant_shift':cov_shift,
            'lower_Gamma':all_lower,'time_reference':time_reference,'shift_curl':curl,
            'spatial_reference':spatial_reference,'forbidden_velocities':forbidden,'residuals':residuals}


def square_root_section():
    a=sp.symbols('a1:4',positive=True)
    velocities=sp.Matrix(sp.symbols('hdot11 hdot22 hdot33 hdot12 hdot13 hdot23',real=True))
    v=velocities
    hd=sp.Matrix([[v[0],v[3],v[4]],[v[3],v[1],v[5]],[v[4],v[5],v[2]]])
    S=sp.diag(*a);h=S*S;E=S.inv()
    Sd=sp.Matrix(3,3,lambda i,j:hd[i,j]/(a[i]+a[j]))
    Ed=clean(-E*Sd*E)
    frame_rotation=E.T*h*Ed
    skew=clean((frame_rotation-frame_rotation.T)/2)
    omega_no_shift=clean(frame_rotation+E.T*hd*E/2)
    reference=sp.Matrix(3,3,lambda i,j:hd[i,j]*(a[j]-a[i])/(2*a[i]*a[j]*(a[i]+a[j])))
    curl12,curl13,curl23=sp.symbols('curl12 curl13 curl23',real=True)
    curl=sp.Matrix([[0,curl12,curl13],[-curl12,0,curl23],[-curl13,-curl23,0]])
    omega_direct=clean(frame_rotation+E.T*(hd+curl)*E/2)
    omega_reference=clean(skew+E.T*curl*E/2)
    generators=[sp.Matrix(3,3,lambda j,k:sp.LeviCivita(i,j,k)) for i in range(3)]
    colors=sp.Matrix([clean(inner(T,skew)) for T in generators])
    L_E=colors.jacobian(velocities)
    point={a[0]:1,a[1]:2,a[2]:3};L_point=clean(L_E.subs(point))
    # An exact finite SPD curve; its inverse root is known by orthogonal conjugation.
    time=sp.Symbol('curve_time',real=True)
    R=sp.Matrix([[sp.cos(time),-sp.sin(time),0],[sp.sin(time),sp.cos(time),0],[0,0,1]])
    D=sp.diag(1,4,9);Droot_inv=sp.diag(1,sp.Rational(1,2),sp.Rational(1,3))
    hc=R*D*R.T;Ec=R*Droot_inv*R.T
    h0=hc.subs(time,0);E0=Ec.subs(time,0)
    hd0=hc.diff(time).subs(time,0);Ed0=Ec.diff(time).subs(time,0)
    omega0=clean(E0.T*h0*Ed0+E0.T*hd0*E0/2)
    finite_Sd=sp.Matrix(3,3,lambda i,j:hd0[i,j]/(sp.sqrt(D[i,i])+sp.sqrt(D[j,j])))
    reference0=clean(-E0*finite_Sd*E0)
    expected0=sp.Matrix([[0,-sp.Rational(1,4),0],[sp.Rational(1,4),0,0],[0,0,0]])
    isotropic=sp.Symbol('isotropic_scale',positive=True)
    residuals={'Sylvester_derivative_all_9_entries':clean(S*Sd+Sd*S-hd),
               'inverse_root_derivative_all_9_entries':clean(Sd*E+S*Ed),
               'varied_frame_orthonormality':clean(Ed.T*h*E+E.T*hd*E+E.T*h*Ed),
               'omega_time_equals_skew_frame_velocity':clean(omega_no_shift-skew),
               'omega_time_with_shift_curl':clean(omega_direct-omega_reference),
               'principal_root_anisotropic_coefficient':clean(skew-reference),
               'omega_time_is_antisymmetric':clean(omega_direct+omega_direct.T),
               'rotating_family_orthogonal':(R.T*R-sp.eye(3)).applyfunc(sp.trigsimp),
               'rotating_family_exact_inverse_root_diagonal':D*Droot_inv**2-sp.eye(3),
               'finite_SPD_curve_matches_Sylvester':Ed0-reference0,
               'finite_SPD_curve_nonzero_time_connection':omega0-expected0,
               'isotropic_frame_velocity_decouples':clean(L_E.subs({v:isotropic for v in a})),
               'anisotropic_hdot12_color3_coefficient':clean(L_point[2,3]-sp.Rational(1,12))}
    negatives={'freeze_E_violates_connection_antisymmetry':clean(E.T*hd*E),
               'omit_metric_velocity_mixing':L_point,
               'assume_h_and_hdot_commute_in_finite_curve':h0*hd0-hd0*h0}
    return {'a':a,'h':h,'E':E,'velocities':velocities,'hdot':hd,'Sdot':Sd,'Edot':Ed,
            'frame_rotation':frame_rotation,'L_matrix':skew,'L_colors':colors,'L_E':L_E,
            'L_E_at_1_2_3':L_point,'omega_time':omega_direct,'shift_curl':curl,
            'curve':{'parameter':time,'rotation':R,'h':hc,'E':Ec,'h0':h0,'E0':E0,'hdot0':hd0,
                     'Edot0':Ed0,'omega0':omega0},'residuals':residuals,'negative_controls':negatives}


def kinetic_gram():
    c=sp.Symbol('kinetic_prefactor',positive=True)
    L=sp.Matrix(3,6,lambda i,j:sp.Symbol(f'L{i}_{j}',real=True))
    v=sp.Matrix(sp.symbols('v0:6',real=True));q=sp.Matrix(sp.symbols('q0:3',real=True))
    offset=sp.Matrix(sp.symbols('B0:3',real=True))
    difference=q-L*v-offset;density=c*difference.dot(difference)/2
    variables=list(v)+list(q);H=sp.hessian(density,variables)
    factor=(-L).row_join(sp.eye(3));reference=c*factor.T*factor
    kernel=sp.eye(6).col_join(L)
    orientation=H[6:9,6:9]
    schur=clean(H[:6,:6]-H[:6,6:9]*(sp.eye(3)/c)*H[6:9,:6])
    nondynamical=sp.symbols('Ndot shift1dot shift2dot shift3dot',real=True)
    extended=sp.hessian(density,variables+list(nondynamical))
    direction=sp.Matrix(sp.symbols('dv0:6 dq0:3',real=True))
    quadratic=(direction.T*H*direction)[0]
    norm=sp.expand(c*((factor*direction).T*(factor*direction))[0])
    residuals={'all_81_kinetic_Hessian_entries_match_Gram':clean(H-reference),
               'six_dimensional_kernel_is_explicit':clean(H*kernel),
               'kernel_coordinates_have_identity_minor':kernel[:6,:]-sp.eye(6),
               'positive_orientation_block':orientation-c*sp.eye(3),
               'nonzero_orientation_minor':clean(orientation.det()-c**3),
               'metric_velocity_Schur_is_exactly_zero':schur,
               'four_lapse_shift_velocity_rows_zero':extended[9:13,:],
               'quadratic_form_is_exact_squared_norm':sp.expand(quadratic-norm)}
    return {'prefactor':c,'L':L,'metric_velocities':v,'orientation_quasivelocities':q,'spatial_offset':offset,
            'density':density,'Hessian':H,'Gram_factor':factor,'kernel':kernel,'orientation_block':orientation,
            'kinetic_Schur':schur,'extended_Hessian':extended,'quadratic_form':quadratic,'squared_norm':norm,
            'residuals':residuals}


@lru_cache(maxsize=1)
def derive_model():
    hodge=hodge_adm();connection=lower_christoffel();section=square_root_section();gram=kinetic_gram()
    residuals={**hodge['residuals'],**connection['residuals'],**section['residuals'],**gram['residuals']}
    replacement={gram['L'][i,j]:section['L_E_at_1_2_3'][i,j] for i in range(3) for j in range(6)}
    H_point=clean(gram['Hessian'].subs(replacement));c=gram['prefactor']
    residuals['anisotropic_mixed_kinetic_entry']=clean(H_point[3,8]+c/12)
    hodge_prefactor=hodge['chi']*hodge['sqrt_h']/hodge['N']
    residuals['Gram_prefactor_bound_to_literal_Hodge']=clean(sp.hessian(hodge['density'],list(hodge['C'][0]))-hodge_prefactor*sp.eye(3))
    negatives={**section['negative_controls'],
               'omit_nonisotropic_velocity_cross_block':H_point[:6,6:9],
               'reverse_temporal_Hodge_sign':-gram['orientation_block']}
    checks={name:zero(value) for name,value in residuals.items()}
    checks.update({f'negative_control_{name}_detected':not zero(value) for name,value in negatives.items()})
    checks.update({'positive_kinetic_prefactor':c.is_positive is True,
                   'positive_literal_Hodge_prefactor':hodge_prefactor.is_positive is True,
                   'positive_orientation_minor_value':(c**3).is_positive is True,
                   'negative_temporal_Hodge_mutant_detected':(-c).is_negative is True})
    return {'hodge':hodge,'connection':connection,'section':section,'gram':gram,'anisotropic_Hessian':H_point,'literal_Hodge_prefactor':hodge_prefactor,
            'residuals':residuals,'negative_controls':negatives,'checks':{k:bool(v) for k,v in checks.items()}}


def serialize(value):
    if isinstance(value,sp.MatrixBase):return [[serialize(x) for x in row] for row in value.tolist()]
    if isinstance(value,dict):return {k:serialize(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [serialize(v) for v in value]
    return str(value) if isinstance(value,sp.Basic) else value


def load_sources():
    if hashlib.sha256(PROOF.read_bytes()).hexdigest()!=PROOF_SHA:raise ADMKineticError('lemma byte pin mismatch')
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ADMKineticError('Ward source byte pin mismatch')
    source=json.loads(raw)
    if not source.get('checks') or not all(v is True for v in source['checks'].values()):raise ADMKineticError('source checks invalid')
    for name,pin in source['provenance'].items():
        if Path(name).name!=name or hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=pin:
            raise ADMKineticError('source implementation changed')
    return {'Ward_receipt_sha256':SOURCE_SHA,'lemma_sha256':PROOF_SHA,'source_gates_inherited':False}


def build_payload():
    sources=load_sources();model=derive_model()
    if not all(model['checks'].values()):raise ADMKineticError('ADM kinetic identity failed')
    payload={'schema':SCHEMA,'sources':sources,
        'proposal':{'adopted':False,'chi':'positive mass-squared symbol, no selected value','A_independent_of_omega':True},
        'model':serialize(model),'checks':model['checks'],
        'scope':{'local_unitary_chart_only':True,'smooth_metric_dependent_frame_section_required':True,
                 'horizontal_field_space_transport_assumed_integrable':False,
                 'Hessian_is_PSD_rank_three_in_nine_metric_and_orientation_velocities':True,
                 'Schur_is_only_a_kinetic_velocity_Schur':True,'lapse_and_shift_velocities_absent_from_added_term':True,
                 'orientation_field_algebraically_eliminated':False,'full_Dirac_mode_count':False,
                 'complete_gravitational_reduced_energy_positive':False,'global_unitary_gauge_proved':False,
                 'BF_global_quotient_closed':False,'N4_JUNCTION_BENDING_pass':False,'N7_LINEAR_REDUCTION_pass':False,
                 'P4_full_same_action_pass':False,'B4_pass':False,'B5_pass':False,'nonlinear_stability_proved':False,
                 'candidate_adopted':False,'chi_selected':False},
        'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST,PROOF)}}
    payload['calculation_digest']=digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:raise ADMKineticError('receipt schema mismatch')
    if payload.get('calculation_digest')!=digest({k:v for k,v in payload.items() if k!='calculation_digest'}):raise ADMKineticError('receipt digest mismatch')
    if payload!=build_payload():raise ADMKineticError('receipt differs from trusted recomputation')


def main():
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',nargs='?',const=OUTPUT,type=Path);mode.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args()
    if args.write:
        result=build_payload()
        with args.write.open('x',encoding='utf-8') as stream:
            json.dump(result,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')
    else:
        result=json.loads(args.verify.read_bytes());validate_payload(result)
    print(json.dumps({'schema':SCHEMA,'checks_passed':sum(result['checks'].values()),
                      'checks_total':len(result['checks']),'calculation_digest':result['calculation_digest']}))


if __name__=='__main__':main()
