"""Static sourced BF at order epsilon^2 for a prescribed localized port.

Only exterior primitives are reused from the pinned affine backend. The
static spatial homotopy, material-current derivation and norm exponents
are new. Fourier multipliers act on the total current (a product), not on
an incorrectly reused single material Fourier mode. Analytic estimates
are conditional on the pinned lemma; no full Einstein solution is claimed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp
if __package__:
    from . import verify_one_omega_connection_affine_bf_reconstruction_v1 as ext
else:
    import verify_one_omega_connection_affine_bf_reconstruction_v1 as ext

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_connection_static_sourced_bf_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_static_sourced_bf_v1.py'
BACKEND=Path(ext.__file__).resolve()
TORQUE=HERE/'artifacts/one_omega_connection_localized_torque_lift_v1.json'
CANDIDATE=HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
OUTPUT=HERE/'artifacts/one_omega_connection_static_sourced_bf_v1.json'
NOTE_SHA256='8f07d3ec6f64f471c15d3dac0d824200f9815f4710ad1f4ba32e0d782d6d9919'
BACKEND_SHA256='08bac3c5737f4acd9d7d240930cb2f057f9045705cc57d72d0033140eed918ab'
TORQUE_SHA256='b9d94ab321890be8733bf72dcb17221738d7375c1d8f47397dae23eab16378ee'
CANDIDATE_SHA256='d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
SCHEMA='holo.one-omega-connection-static-sourced-bf.v1'
plus,scale,wedge,contract,trace,zero=ext.plus,ext.scale,ext.wedge,ext.contraction,ext.trace,ext.zero
canonical_digest=ext.canonical_digest

class StaticSourcedBFError(ValueError):
    pass

def vector(prefix):return sp.Matrix([sp.Symbol(f'{prefix}_{i}',real=True) for i in range(3)])

def symbols_context():
    z=sp.Symbol('z',nonnegative=True);xi=sp.symbols('xi1 xi2 xi3',real=True)
    Z,kappa,y,chi,k=sp.symbols('Z kappa y chi k',positive=True)
    return {'z':z,'r':z,'xi':xi,'p2':sum(v*v for v in xi),'Z':Z,'kappa':kappa,'y':y,'chi':chi,'k':k,
            'a':sp.Symbol('a',nonnegative=True),'Omega':sp.Symbol('Omega',positive=True),
            'f':sp.Function('f',real=True)(z),'rho':sp.Symbol('rho_hat')}

def static_d(form,ctx,boundary=False):
    terms=[wedge({1<<(i+1):sp.I*k},form) for i,k in enumerate(ctx['xi'])]
    if not boundary:terms.append(wedge({16:1},{m:sp.diff(v,ctx['z']) for m,v in form.items()}))
    return plus(*terms)

def spatial_h(form,ctx):
    if sp.sympify(ctx['p2']).is_zero is True:raise StaticSourcedBFError('spatial homotopy requires p^2>0')
    return scale(-sp.I/ctx['p2'],plus(*(scale(k,contract(form,i+1)) for i,k in enumerate(ctx['xi']))))

def star_one_Lorentz(form):
    # alpha wedge *beta = eta^-1(alpha,beta) volSigma, volSigma=dt dx1 dx2 dx3.
    return plus(*(scale((-1 if i==0 else 1)*form.get(1<<i,0),contract({15:1},i)) for i in range(4)))

def derive_material(ctx):
    Z=ctx['Z'];psi=vector('psi');first=[vector(f'psi_d{m}') for m in range(4)]
    second=[vector(f'psi_dd{m}') for m in range(4)]
    A=[vector(f'A{m}') for m in range(4)]
    T=[sp.Matrix(3,3,lambda j,k:sp.LeviCivita(i,j,k)) for i in range(3)]
    covariant=[first[m]+sum((A[m][i]*T[i]*psi for i in range(3)),sp.zeros(3,1)) for m in range(4)]
    density=-Z*sum((v.T*v)[0] for v in covariant)/2
    azero={v:0 for a in A for v in a}
    Q=[sp.Matrix([sp.diff(density,A[m][i]).subs(azero) for i in range(3)]) for m in range(4)]
    def derivative(expr,m):
        return sum(sp.diff(expr,psi[i])*first[m][i]+sp.diff(expr,first[m][i])*second[m][i] for i in range(3))
    divergence=sp.Matrix([sum(derivative(Q[m][i],m) for m in range(4)) for i in range(3)])
    laplacian=sum(second,sp.zeros(3,1));EL=Z*laplacian
    # Direct Euler derivative of the ungauged conformal kinetic density.
    free=density.subs(azero)
    actual_EL=sp.Matrix([sp.diff(free,psi[i])-sum(derivative(sp.diff(free,first[m][i]),m) for m in range(4)) for i in range(3)])
    O,Od=ctx['Omega'],sp.Symbol('Omega_z',real=True)
    phi=O**sp.Rational(-3,2)*psi
    phi_z=O**sp.Rational(-3,2)*(first[0]-sp.Rational(3,2)*Od*psi/O)
    old_current=Z*O**3*phi.cross(phi_z)
    gradF=vector('gradF');phi0=vector('phi_UV');normal=vector('psi_z_UV')
    robin_normal=(ctx['kappa']*phi0-ctx['kappa']*ctx['y']*gradF)/(2*Z)
    rho_from_trace=2*Z*phi0.cross(robin_normal)
    expected_rho=ctx['kappa']*ctx['y']*gradF.cross(phi0)
    return {'psi':psi,'first_jets_order_z_x1_x2_x3':first,'second_diagonal_jets':second,
            'generators':T,'literal_kinetic_density':density,'Q_by_direction':Q,
            'Euler_from_literal':actual_EL,'laplacian':laplacian,'divergence_Q':divergence,
            'phi_UV':phi0,'gradF':gradF,'Robin_normal_derivative':robin_normal,'rho_from_oriented_trace':rho_from_trace,
            'residuals':{'current_from_literal_gauge_variation':[Q[m]-Z*psi.cross(first[m]) for m in range(4)],
                'harmonic_EL_from_literal_density':actual_EL-EL,
                'current_conservation_identity':divergence-psi.cross(actual_EL),
                'conformal_normal_mixing_cancels':old_current-Z*psi.cross(first[0]),
                'conformal_kinetic_weight_cancels':O**5*O**-2*O**-3-1,
                'two_side_Robin_source_sign':rho_from_trace-expected_rho}}

def derive_exterior(ctx):
    g=sp.Function('arbitrary_radial_coefficient')(ctx['z'])
    basis=[{mask:g} for mask in range(32)]
    return {'basis_count':32,'time_derivative_zero_but_dt_forms_retained':True,
            'residuals':{'static_d_squared':[static_d(static_d(a,ctx),ctx) for a in basis],
                'spatial_Cartan_all_degrees':[plus(static_d(spatial_h(a,ctx),ctx),spatial_h(static_d(a,ctx),ctx),scale(-1,a)) for a in basis],
                'h_squared':[spatial_h(spatial_h(a,ctx),ctx) for a in basis],
                'trace_commutes_d':[plus(trace(static_d(a,ctx),ctx),scale(-1,static_d(trace(a,ctx),ctx,boundary=True))) for a in basis],
                'trace_commutes_h':[plus(trace(spatial_h(a,ctx),ctx),scale(-1,spatial_h(trace(a,ctx),ctx))) for a in basis]}}

def derive_reconstruction(ctx):
    z,f=ctx['z'],ctx['f']
    # Q^t=0: the four source basis forms all contain dt. A general closed
    # source is represented by d h J_general; Cartan proves this projection
    # is the identity on every closed source, not an assumed radial ansatz.
    general={m:sp.Function(f'J4_{m}')(z) for m in ext.masks(4) if m&1}
    source=static_d(spatial_h(general,ctx),ctx)
    part_plus=scale(-1,spatial_h(source,ctx));part_minus=scale(-1,part_plus)
    jplus=trace(source,ctx);jump=scale(2,jplus)
    boundary_potential={m:sp.Symbol(f'boundary_K_{m}') for m in ext.masks(2,4)}
    L=static_d(boundary_potential,ctx,boundary=True)
    Jboundary=plus(scale(-1,spatial_h(jump,ctx)),L)
    correction=scale(sp.Rational(1,2),static_d(scale(f,spatial_h(L,ctx)),ctx))
    Bplus=plus(part_plus,correction);Bminus=plus(part_minus,scale(-1,correction))
    uv={f.subs(z,0):1}
    Bjump=ext.substitute(plus(trace(Bplus,ctx),scale(-1,trace(Bminus,ctx))),uv)
    # Actual Poisson port: rho, Theta and the Lorentzian star fix L exactly.
    rho=ctx['rho'];Theta=-rho/(ctx['chi']*ctx['p2'])
    dTheta={1<<(i+1):sp.I*k*Theta for i,k in enumerate(ctx['xi'])}
    actual_current=scale(-ctx['chi'],star_one_Lorentz(dTheta))
    actual_jump={15:rho}
    actual_L=plus(actual_current,spatial_h(actual_jump,ctx))
    actual_current_for_source=ext.substitute(actual_current,{rho:jump.get(15,0)})
    part_jump=plus(trace(part_plus,ctx),scale(-1,trace(part_minus,ctx)))
    return {'general_source_four_form':general,'closed_source_plus':source,'closed_source_minus':scale(-1,source),
            'B_part_plus':part_plus,'B_part_minus':part_minus,'source_UV_jump':jump,
            'general_closed_boundary_remainder':L,'general_compatible_boundary_current':Jboundary,
            'general_cutoff_correction_plus':correction,'general_B_plus':Bplus,'general_B_minus':Bminus,
            'Theta_hat_actual_port':Theta,'J_Sigma_actual_port':actual_current,'L_actual_port':actual_L,
            'actual_particular_jump':part_jump,'actual_current_for_general_closed_source':actual_current_for_source,
            'residuals':{'closed_source_projection_identity':plus(general,scale(-1,source),scale(-1,spatial_h(static_d(general,ctx),ctx))),
                'source_closed':static_d(source,ctx),
                'B_part_plus_sourced_equation':plus(static_d(part_plus,ctx),source),
                'B_part_minus_sourced_equation':plus(static_d(part_minus,ctx),scale(-1,source)),
                'general_boundary_compatibility':plus(static_d(Jboundary,ctx,boundary=True),jump),
                'general_L_closed':static_d(L,ctx,boundary=True),
                'general_B_plus_sourced_equation':plus(static_d(Bplus,ctx),source),
                'general_B_minus_sourced_equation':plus(static_d(Bminus,ctx),scale(-1,source)),
                'general_oriented_jump':plus(Bjump,scale(-1,Jboundary)),
                'actual_Hodge_Poisson_remainder_zero':actual_L,
                'actual_current_compatibility':plus(static_d(actual_current,ctx,boundary=True),actual_jump),
                'actual_B_part_alone_has_required_jump':plus(part_jump,scale(-1,actual_current_for_source))}}

def derive_norms(ctx):
    z=sp.Symbol('positive_z',positive=True);rate=sp.Symbol('positive_rate',positive=True)
    orders=(4,6,3)
    moments={n:sp.factorial(n)/(rate*z)**(n+1) for n in orders}
    residuals={f'Laplace_moment_{n}_from_base_derivatives':sp.simplify(moments[n]-(-1/rate)**n*sp.diff(1/(rate*z),z,n)) for n in orders}
    psi_l2=sp.Rational(4+1,2);derivative_l2=sp.Rational(6+1,2);psi_inf=sp.Integer(3+1)
    J_l1=psi_l2+derivative_l2;J_l2=psi_inf+derivative_l2
    B_l2_squared=min(2*J_l1,2*J_l2)
    weighted_B=B_l2_squared-1;weighted_source=2*J_l2-3
    O=ctx['Omega'];component_weights=[]
    for degree in (3,4):
        for mask in ext.masks(degree):
            tangential=(mask&15).bit_count()
            # dr=Omega dz; a dr coefficient is its dz coefficient /Omega.
            proper_weight=O**(4-2*tangential)*O*(O**-2 if mask&16 else 1)
            conformal_weight=O**(5-2*degree)
            component_weights.append({'degree':degree,'mask':mask,'weight':conformal_weight})
            residuals[f'proper_conformal_measure_agree_{degree}_{mask}']=sp.cancel(proper_weight-conformal_weight)
    radial_powers={'psi_L2':psi_l2,'derivative_psi_L2':derivative_l2,'psi_Linfinity':psi_inf,
        'J4_L1':J_l1,'J4_L2':J_l2,'B_part_coefficient_L2_squared':B_l2_squared,
        'weighted_B_integrand_decay_power':weighted_B,'weighted_dB_integrand_decay_power':weighted_source}
    source_L1,source_L2=sp.symbols('norm_J4_L1 norm_J4_L2',nonnegative=True)
    low_constant=sp.simplify(4*sp.pi/(2*sp.pi)**3)
    omega_derivative=-ctx['k']*O*O*sp.exp(-ctx['a']*O*O)
    residuals.update({'inverse_warp_BPS_derivative':sp.cancel(-omega_derivative/O**2-ctx['k']*sp.exp(-ctx['a']*O*O)),
        'unitary_Fourier_low_frequency_constant':low_constant-1/(2*sp.pi**2),
        'weighted_B_exponent':weighted_B-11,'weighted_source_exponent':weighted_source-12})
    return {'laplace_moments':moments,'radial_decay_powers':radial_powers,'form_component_weights':component_weights,
        'homotopy_source_norm_bound':source_L1**2/(2*sp.pi**2)+source_L2**2,
        'low_frequency_integral_p_minus_two_R3':4*sp.pi,
        'homotopy_unbounded_family':'xi=(epsilon,0,0), alpha=dx1: ||h alpha||^2=epsilon^-2; epsilon=1/2 violates unit bound by 3',
        'weighted_radial_integrability':{'B':bool(weighted_B>1),'dB':bool(weighted_source>1)},
        'auxiliary_norm_convention':'five-dimensional positive component norm per unit coordinate time, no pullback to t=constant',
        'warp_bound':'1+k exp(-a) z <= 1/Omega <= 1+k z, from 0<Omega<=1 and a>=0',
        'analytic_hypotheses':['F real C_c^infinity(R3)','psi=e^(-|D|z)y grad g(|D|)F',
            'g(p)=kappa/(kappa+2Zp)','rho has zero mean by the pinned localized torque lemma',
            'current products transformed after multiplication; no single-mode shortcut'],
        'residuals':residuals}

def derive_model():
    ctx=symbols_context();parts={'material':derive_material(ctx),'exterior':derive_exterior(ctx),
        'reconstruction':derive_reconstruction(ctx),'norms':derive_norms(ctx)}
    checks={part+'_'+name:zero(v) for part,data in parts.items() for name,v in data['residuals'].items()}
    rec=parts['reconstruction'];mat=parts['material']
    wrong_star_current=scale(-1,rec['J_Sigma_actual_port'])
    wrong_radial=scale(ctx['f']/2,rec['general_closed_boundary_remainder'])
    small_momentum=dict(ctx);small_momentum['xi']=(sp.Rational(1,2),0,0);small_momentum['p2']=sp.Rational(1,4)
    unit_form_primitive=spatial_h({2:1},small_momentum)[0]
    unit_bound_gap=sp.expand(sp.conjugate(unit_form_primitive)*unit_form_primitive-1)
    witnesses={'omit_sourced_particular_solution':rec['closed_source_plus'],
        'positive_h_for_B_part':plus(static_d(scale(-1,rec['B_part_plus']),ctx),rec['closed_source_plus']),
        'same_sign_source_on_both_oriented_halves':scale(2,rec['closed_source_plus']),
        'wrong_Lorentz_Hodge_sign':plus(wrong_star_current,spatial_h({15:ctx['rho']},ctx)),
        'omit_general_cutoff_normal_term':static_d(wrong_radial,ctx),
        'reverse_material_Robin_source_sign':scale(2,{0:mat['rho_from_oriented_trace'][0]}),
        'claim_unit_spatial_h_bound_at_zero':unit_bound_gap,
        'erase_dt_components_of_source':rec['closed_source_plus']}
    controls={name:not zero(v) for name,v in witnesses.items()}
    return {'symbols':ctx,**parts,'checks':checks,'negative_controls':controls,'negative_witnesses':witnesses,
        'decision':{'prescribed_port_order_two_sourced_BF_constructed':True,
            'actual_port_requires_no_closed_cutoff_correction':True,
            'material_current_conservation_from_harmonic_EL':True,
            'spatial_and_radial_auxiliary_graph_integrability_conditional':True,
            'candidate_term_adopted_in_v5_2':False,'chi_numerically_selected':False,
            'Einstein_or_embedding_equations_solved':False,'full_nonlinear_continuation_proved':False,
            'uniqueness_for_all_static_weighted_BF_fields':False,'uniform_h_on_arbitrary_L2_at_p_zero':False,
            'global_temporal_L2_or_physical_B_energy_proved':False,'BV_BFV_or_global_topology_closed':False,
            'N4_JUNCTION_BENDING_pass':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}

def load_sources(note_path=NOTE,backend_path=BACKEND,torque_path=TORQUE,candidate_path=CANDIDATE):
    out={}
    for kind,path,digest in [('note',Path(note_path),NOTE_SHA256),('exterior_backend',Path(backend_path),BACKEND_SHA256),
                            ('localized_torque',Path(torque_path),TORQUE_SHA256),('base_candidate',Path(candidate_path),CANDIDATE_SHA256)]:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise StaticSourcedBFError(kind+' byte hash mismatch')
        out[kind]={'name':path.name,'sha256':digest}
    out['reused_backend_scope']='wedge, contraction, trace and serialization only; no RHP 1/s homotopy'
    out['upstream_global_gates_inherited']=False
    return out

def build_payload(note_path=NOTE,backend_path=BACKEND,torque_path=TORQUE,candidate_path=CANDIDATE):
    sources=load_sources(note_path,backend_path,torque_path,candidate_path);model=derive_model()
    if not all(model['checks'].values()) or not all(model['negative_controls'].values()):
        raise StaticSourcedBFError('static sourced BF identity or negative control failed')
    doc={'schema':SCHEMA,'sources':sources,'model':ext._serialize(model),'checks':model['checks'],
        'negative_controls':model['negative_controls'],'decision':model['decision'],
        'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
        'runtime':{'sympy':sp.__version__}}
    doc['calculation_digest']=canonical_digest(doc)
    return doc

def validate_payload(doc,note_path=NOTE,backend_path=BACKEND,torque_path=TORQUE,candidate_path=CANDIDATE):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:raise StaticSourcedBFError('receipt schema mismatch')
    if doc.get('calculation_digest')!=canonical_digest({k:v for k,v in doc.items() if k!='calculation_digest'}):raise StaticSourcedBFError('receipt digest mismatch')
    if doc!=build_payload(note_path,backend_path,torque_path,candidate_path):raise StaticSourcedBFError('receipt differs from fresh derivation')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path);modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args(argv)
    if args.write is not None:
        doc=build_payload();args.write.parent.mkdir(parents=True,exist_ok=True)
        with args.write.open('x',encoding='utf8') as f:json.dump(doc,f,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
    else:doc=json.loads(args.verify.read_bytes());validate_payload(doc)
    print(json.dumps({'checks_passed':sum(doc['checks'].values()),'negative_controls':doc['negative_controls'],
                      'calculation_digest':doc['calculation_digest']}))

if __name__=='__main__':main()
