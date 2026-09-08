"""Selected affine BF reconstruction in a nonzero Fourier-Laplace fibre.

A and B have degrees one and three in five dimensions. The boundary current
is a closed three-form; the bulk material current is ZERO at this order.
The maximum graph domain of d and regular boundary data are hypotheses,
not consequences of finite algebra checks. No sourced second-order B,
global temporal L2, nonlinear theory or BV/BFV claim is made.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_connection_affine_bf_reconstruction_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_affine_bf_reconstruction_v1.py'
CANDIDATE=HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
BF_RECEIPT=HERE/'artifacts/one_omega_bf_rhp_quotient_v1.json'
CURRENT_RECEIPT=HERE/'artifacts/one_omega_interface_connection_current_candidate_v1.json'
OUTPUT=HERE/'artifacts/one_omega_connection_affine_bf_reconstruction_v1.json'
NOTE_SHA256='359044f4bbbec42f7dc5eebf7f98f37d293378fa85394bba32beef95897827d6'
CANDIDATE_SHA256='d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
BF_SHA256='c14cf8d7b5820114837a4fb7f432ef250001224b8946f386c55350d2a829871d'
CURRENT_SHA256='e14bba98d1c9d6976c1ed2f6c902d9a603e7f20a09796c2dddc9c31095331a1e'
SCHEMA='holo.one-omega-connection-affine-bf-reconstruction.v1'

class AffineBFError(ValueError):
    pass

def canonical_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
        ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def masks(degree,dimension=5):
    return [sum(1<<i for i in indices) for indices in itertools.combinations(range(dimension),degree)]

def normalize(form):
    out={mask:sp.cancel(value) for mask,value in sorted(form.items())}
    return {mask:value for mask,value in out.items() if value!=0}

def plus(*forms):
    out={}
    for form in forms:
        for mask,value in form.items():out[mask]=out.get(mask,0)+value
    return normalize(out)

def scale(value,form):return normalize({mask:value*c for mask,c in form.items()})

def wedge(left,right):
    out={}
    for a,x in left.items():
        for b,y in right.items():
            if a&b:continue
            inversions=sum((b&((1<<i)-1)).bit_count() for i in range(5) if a&(1<<i))
            mask=a|b;out[mask]=out.get(mask,0)+(-1)**inversions*x*y
    return normalize(out)

def contraction(form,index):
    bit=1<<index
    return normalize({mask^bit:(-1)**((mask&(bit-1)).bit_count())*value
                      for mask,value in form.items() if mask&bit})

def d(form,ctx,boundary=False):
    p=(ctx['s'],*[sp.I*k for k in ctx['k']])
    terms=[wedge({1<<i:p[i]},form) for i in range(4)]
    if not boundary:terms.append(wedge({16:1},{mask:sp.diff(value,ctx['r']) for mask,value in form.items()}))
    return plus(*terms)

def h(form,ctx):return scale(1/ctx['s'],contraction(form,0))

def trace(form,ctx):
    return normalize({mask:value.subs(ctx['r'],0) for mask,value in form.items() if not mask&16})

def substitute(form,mapping):return normalize({mask:value.subs(mapping,simultaneous=True) for mask,value in form.items()})

def zero(value):
    if isinstance(value,dict):return all(zero(x) for x in value.values())
    if isinstance(value,(tuple,list)):return all(zero(x) for x in value)
    if isinstance(value,sp.MatrixBase):return all(zero(x) for x in value)
    return sp.cancel(value)==0

def symbols_context():
    r=sp.Symbol('r',nonnegative=True)
    return {'r':r,'s':sp.Symbol('s',nonzero=True),'k':sp.symbols('k1 k2 k3',real=True),
            'theta':sp.Symbol('theta'),'f':sp.Function('f',real=True)(r),
            'sigma':sp.Symbol('sigma',positive=True),'tau':sp.Symbol('tau',real=True),
            'Omega':sp.Symbol('Omega',positive=True),'omega_lower':sp.Symbol('omega_lower',positive=True),
            'F0':sp.Symbol('F0',nonnegative=True),'F1':sp.Symbol('F1',nonnegative=True)}

def derive_complex(ctx):
    radial=sp.Function('arbitrary_radial_coefficient')(ctx['r'])
    basis=[{mask:radial} for mask in range(32)]
    d2=[d(d(a,ctx),ctx) for a in basis]
    cartan=[plus(d(h(a,ctx),ctx),h(d(a,ctx),ctx),scale(-1,a)) for a in basis]
    trace_d=[plus(trace(d(a,ctx),ctx),scale(-1,d(trace(a,ctx),ctx,boundary=True))) for a in basis]
    trace_h=[plus(trace(h(a,ctx),ctx),scale(-1,h(trace(a,ctx),ctx))) for a in basis]
    anticommutators=[]
    for i in range(5):
        for j in range(5):
            for mask in range(32):
                a={mask:1}
                anticommutators.append(plus(wedge({1<<i:1},contraction(a,j)),
                    contraction(wedge({1<<i:1},a),j),scale(-int(i==j),a)))
    return {'basis_masks_by_degree':{p:masks(p) for p in range(6)},'radial_coefficient':radial,
            'SO3_independent_linear_copies':3,
            'residuals':{'d_squared_all_32_radial_bases':d2,'Cartan_all_32_radial_bases':cartan,
                'UV_pullback_commutes_with_d':trace_d,'UV_pullback_commutes_with_h':trace_h,
                'wedge_contraction_anticommutators':anticommutators}}

def derive_lift(ctx):
    r,f,theta,s=(ctx[k] for k in ('r','f','theta','s'))
    J_general={mask:sp.Symbol(f'J_{mask}') for mask in masks(3,4)}
    closure=d(J_general,ctx,boundary=True).get(15,0)
    spatial=J_general[14]
    eliminated=sp.cancel(-closure.subs(spatial,0)/s)
    J=substitute(J_general,{spatial:eliminated});primitive=h(J,ctx)
    A=scale(-1,d({0:f*theta},ctx))
    Bplus=scale(sp.Rational(1,2),d(scale(f,primitive),ctx));Bminus=scale(-1,Bplus)
    boundary_values={f.subs(r,0):1}
    trA=substitute(trace(A,ctx),boundary_values)
    trBp=substitute(trace(Bplus,ctx),boundary_values);trBm=substitute(trace(Bminus,ctx),boundary_values)
    A_boundary=scale(-1,d({0:theta},ctx,boundary=True))
    J_jump=plus(trBp,scale(-1,trBm))
    theta_restricted=scale(-1,h(trA,ctx))
    explicit_A=plus(scale(-f,d({0:theta},ctx,boundary=True)),{16:-sp.diff(f,r)*theta})
    explicit_B=scale(sp.Rational(1,2),plus(scale(f,J),wedge({16:sp.diff(f,r)},primitive)))
    return {'current_general':J_general,'current_closure_coefficient':closure,
            'closed_current_eliminated_component':{spatial:eliminated},'J':J,'hJ':primitive,
            'A_plus':A,'A_minus':A,'B_plus':Bplus,'B_minus':Bminus,
            'A_boundary':A_boundary,'B_plus_trace':trBp,'B_minus_trace':trBm,'jump':J_jump,
            'R_E_theta':theta_restricted,'cutoff_UV_substitution':boundary_values,
            'residuals':{'closed_current_parameterization_complete_for_nonzero_s':d(J,ctx,boundary=True),
                'current_is_d_hJ':plus(d(primitive,ctx,boundary=True),scale(-1,J)),
                'A_bulk_closed':d(A,ctx),'B_plus_bulk_closed':d(Bplus,ctx),'B_minus_bulk_closed':d(Bminus,ctx),
                'A_explicit_normal_cutoff_term':plus(A,scale(-1,explicit_A)),
                'B_explicit_normal_cutoff_term':plus(Bplus,scale(-1,explicit_B)),
                'A_trace_preserved':plus(trA,scale(-1,A_boundary)),
                'B_plus_trace_half':plus(trBp,scale(-sp.Rational(1,2),J)),
                'B_minus_trace_negative_half':plus(trBm,scale(sp.Rational(1,2),J)),
                'oriented_jump_is_J':plus(J_jump,scale(-1,J)),
                'restriction_after_extension_identity':plus(theta_restricted,{0:-theta})}}

def derive_affine(ctx,lift):
    r,f=ctx['r'],ctx['f'];a=sp.symbols('relative_a_plus relative_a_minus')
    delta_A=[d({0:r*f*c},ctx) for c in a];eps=[h(x,ctx) for x in delta_A]
    common={mask:sp.Symbol(f'common_Lambda_{mask}') for mask in masks(2,4)}
    potentials=[]
    for side in ('plus','minus'):
        tangential={mask:r*f*sp.Symbol(f'{side}_P_{mask}') for mask in masks(2,4)}
        radial=wedge({16:f},{mask:sp.Symbol(f'{side}_Q_{mask}') for mask in masks(1,4)})
        potentials.append(plus(scale(f,common),tangential,radial))
    delta_B=[d(p,ctx) for p in potentials];Lambda=[scale(-1,h(b,ctx)) for b in delta_B]
    boundary_values=lift['cutoff_UV_substitution']
    tr_eps=[substitute(trace(x,ctx),boundary_values) for x in eps]
    tr_Lambda=[substitute(trace(x,ctx),boundary_values) for x in Lambda]
    tr_delta_B=[substitute(trace(x,ctx),boundary_values) for x in delta_B]
    # The basis Cartan identity above proves the same statement for EVERY
    # closed difference; these are arbitrary relative representatives as a
    # separate check of the trace domains and gauge signs.
    forbidden_A=trace(h(lift['A_plus'],ctx),ctx)
    forbidden_B_jump=scale(-1,h(lift['jump'],ctx))
    return {'relative_A_differences':delta_A,'epsilon_removal':eps,
            'relative_B_potentials':potentials,'relative_B_differences':delta_B,'Lambda_removal':Lambda,
            'epsilon_traces':tr_eps,'Lambda_traces':tr_Lambda,
            'forbidden_A_erasing_trace':substitute(forbidden_A,boundary_values),
            'forbidden_B_erasing_parameter_jump':forbidden_B_jump,
            'residuals':{'relative_A_closed':[d(x,ctx) for x in delta_A],
                'relative_A_traces_zero':tr_eps,
                'relative_A_removed_with_positive_h':[plus(x,scale(-1,d(e,ctx))) for x,e in zip(delta_A,eps)],
                'relative_B_closed':[d(x,ctx) for x in delta_B],
                'relative_B_trace_jump_zero':plus(tr_delta_B[0],scale(-1,tr_delta_B[1])),
                'B_parameters_have_common_traces':plus(tr_Lambda[0],scale(-1,tr_Lambda[1])),
                'relative_B_removed_with_negative_h':[plus(x,d(l,ctx)) for x,l in zip(delta_B,Lambda)],
                'epsilon_preserves_physical_theta':[h(d(t,ctx,boundary=True),ctx) for t in tr_eps]}}

def derive_norms(ctx):
    O=ctx['Omega'];s2=ctx['sigma']**2+ctx['tau']**2
    table=[];residuals=[]
    for mask in range(32):
        k=(mask&15).bit_count();incoming=O**(4-2*k)
        if mask&1:
            outgoing=O**(4-2*(k-1))/s2
            residuals.append(sp.cancel(outgoing/incoming-O*O/s2))
        else:outgoing=sp.S.Zero
        table.append({'mask':mask,'degree':mask.bit_count(),'tangential_indices':k,
                      'input_weight':incoming,'h_output_weight':outgoing})
    theta2,dtheta2,J2,hJ2=sp.symbols('norm_theta_sq norm_dtheta_sq norm_J_sq norm_hJ_sq',nonnegative=True)
    IA,IAr,IB,IBr=sp.symbols('int_f2_Omega2 int_fp2_Omega4 int_f2_Omega_minus2 int_fp2',nonnegative=True)
    exact_A=IA*dtheta2+IAr*theta2;exact_B=(IB*J2+IBr*hJ2)/4
    bound_A=ctx['F0']*dtheta2+ctx['F1']*theta2
    bound_B=(ctx['F0']/ctx['omega_lower']**2+ctx['F1']/s2)*J2/4
    X,Y=sp.symbols('norm_alpha norm_dalpha',nonnegative=True)
    graph_bound=(2+1/s2)*X*X+2*Y*Y/s2
    triangle_bound=X*X/s2+(X+Y/sp.sqrt(s2))**2
    graph_gap=sp.expand(graph_bound-triangle_bound)
    return {'auxiliary_metric':'dr^2+Omega^2(dt^2+dx1^2+dx2^2+dx3^2), positive; not physical energy',
            'warp_hypotheses':'0<Omega<=1; inf Omega on fixed compact cutoff collar is omega_lower>0',
            'component_weights':table,'s_abs_squared':s2,
            'h_L2_operator_bound_squared':1/s2,'graph_bound_squared':graph_bound,
            'extension_A_norm_squared_exact':exact_A,'extension_B_each_side_norm_squared_exact':exact_B,
            'extension_A_norm_squared_bound':bound_A,'extension_B_each_side_norm_squared_bound':bound_B,
            'regular_boundary_data':['theta in L2','d_Sigma theta in L2','J in L2','d_Sigma J=0 distributionally'],
            'domain':'D_max(d) in each degree, with relative A trace zero and common B-gauge traces; same graph for gauges',
            'trace_statement':'fixed fibre: alpha_T prime=(d alpha)_radial+d_Sigma alpha_R in L2_loc, so alpha_T in H1_loc; general tangential trace may be weak',
            'residuals':{'all_component_contraction_weight_ratios':residuals,
                'graph_triangle_gap_is_square':sp.cancel(graph_gap-(X-Y/sp.sqrt(s2))**2),
                'A_cutoff_bound_substitution':sp.cancel(exact_A.subs({IA:ctx['F0'],IAr:ctx['F1']})-bound_A),
                'B_cutoff_and_h_bound_substitution':sp.cancel(exact_B.subs({IB:ctx['F0']/ctx['omega_lower']**2,IBr:ctx['F1'],hJ2:J2/s2})-bound_B)}}

def derive_model():
    ctx=symbols_context();complex_part=derive_complex(ctx);lift=derive_lift(ctx)
    affine=derive_affine(ctx,lift);norms=derive_norms(ctx)
    parts={'complex':complex_part,'lift':lift,'affine':affine,'norms':norms}
    checks={part+'_'+name:zero(value) for part,data in parts.items() for name,value in data['residuals'].items()}
    naive_A=scale(-ctx['f'],d({0:ctx['theta']},ctx,boundary=True))
    naive_B=scale(ctx['f']/2,lift['J'])
    not_closed_J={14:1}
    witnesses={'omit_A_normal_cutoff_term':d(naive_A,ctx),
        'omit_B_normal_cutoff_term':d(naive_B,ctx),
        'same_sign_on_both_faces':scale(-1,lift['J']),
        'omit_half_in_B_lift':lift['J'],
        'positive_h_for_B_removal':plus(affine['relative_B_differences'][0],d(h(affine['relative_B_differences'][0],ctx),ctx)),
        'nonclosed_current_cannot_be_recovered':plus(d(h(not_closed_J,ctx),ctx,boundary=True),scale(-1,not_closed_J)),
        'erase_A_with_nonrelative_gauge':affine['forbidden_A_erasing_trace'],
        'erase_B_with_noncommon_shift':affine['forbidden_B_erasing_parameter_jump']}
    controls={name:not zero(value) for name,value in witnesses.items()}
    return {'symbols':ctx,**parts,'checks':checks,'negative_controls':controls,'negative_witnesses':witnesses,
            'assumptions':{'spectral_fibre':'Re(s)>0, real spatial k; no division by k or s^2+|k|^2',
                'linear_bulk_material_current':'J4_bulk=0',
                'boundary_current':'J=chi *_Sigma(A_Sigma-omega), chi>0; d_Sigma J=0',
                'incidence':{'plus':1,'minus':-1},'gauge_signs':{'A':'-d epsilon','B':'+d Lambda'},
                'cutoff':'smooth f=1 near UV, compact radial support',
                'source_status':'connection-current extension remains a proposal; base v5.2 unchanged'},
            'decision':{'selected_linear_affine_BF_quotient_bijection':True,
                'closed_current_extension_and_trace_identity_checked':True,
                'relative_gauge_homotopies_checked':True,'BPS_auxiliary_graph_estimates_conditional':True,
                'theta_boundary_data_erased':False,'A_identified_with_omega':False,
                'all_weak_boundary_traces_admit_this_L2_lift':False,'compact_gauge_for_all_L2_solutions_claimed':False,
                'physical_energy_or_global_temporal_L2_proved':False,'s_zero_or_global_topology_closed':False,
                'sourced_B_order_epsilon_two_solved':False,'nonlinear_full_boundary_theory_derived':False,
                'BV_BFV_or_physical_mode_count_closed':False,'N4_JUNCTION_BENDING_pass':False,
                'full_N7':False,'full_P4':False,'B4':False,'B5':False}}

def _serialize(value):
    if isinstance(value,sp.MatrixBase):return _serialize(value.tolist())
    if isinstance(value,sp.Basic):return str(value)
    if isinstance(value,dict):return {str(k):_serialize(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [_serialize(v) for v in value]
    return value

def load_sources(note_path=NOTE,candidate_path=CANDIDATE,bf_path=BF_RECEIPT,current_path=CURRENT_RECEIPT):
    out={}
    for name,path,digest in [('note',Path(note_path),NOTE_SHA256),('candidate',Path(candidate_path),CANDIDATE_SHA256),
                            ('BF_antecedent',Path(bf_path),BF_SHA256),('current_proposal',Path(current_path),CURRENT_SHA256)]:
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise AffineBFError(name+' byte hash mismatch')
        out[name]={'name':path.name,'sha256':digest}
    out['upstream_gates_inherited']=False
    return out

def build_payload(note_path=NOTE,candidate_path=CANDIDATE,bf_path=BF_RECEIPT,current_path=CURRENT_RECEIPT):
    sources=load_sources(note_path,candidate_path,bf_path,current_path);model=derive_model()
    if not all(model['checks'].values()) or not all(model['negative_controls'].values()):
        raise AffineBFError('affine BF identity or negative control failed')
    doc={'schema':SCHEMA,'sources':sources,'model':_serialize(model),'checks':model['checks'],
         'negative_controls':model['negative_controls'],'decision':model['decision'],
         'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
         'runtime':{'sympy':sp.__version__}}
    doc['calculation_digest']=canonical_digest(doc)
    return doc

def validate_payload(doc,note_path=NOTE,candidate_path=CANDIDATE,bf_path=BF_RECEIPT,current_path=CURRENT_RECEIPT):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:raise AffineBFError('receipt schema mismatch')
    if doc.get('calculation_digest')!=canonical_digest({k:v for k,v in doc.items() if k!='calculation_digest'}):
        raise AffineBFError('receipt digest mismatch')
    if doc!=build_payload(note_path,candidate_path,bf_path,current_path):raise AffineBFError('receipt differs from fresh derivation')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path);modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
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
