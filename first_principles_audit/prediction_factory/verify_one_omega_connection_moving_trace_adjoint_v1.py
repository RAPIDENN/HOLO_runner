#!/usr/bin/env python3
"""Local moving connection trace and its adjoint, retaining both BF complements.

The finite map is differentiated before rewriting its result covariantly.
The target representative is horizontal; eta is identification data relative
to that representative, not a newly introduced physical degree of freedom.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sympy as sp
if __package__:
    from . import verify_one_omega_interface_connection_current_candidate_v1 as current
else:
    import verify_one_omega_interface_connection_current_candidate_v1 as current

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_connection_moving_trace_adjoint_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_moving_trace_adjoint_v1.py'
OUTPUT=HERE/'artifacts/one_omega_connection_moving_trace_adjoint_v1.json'
NOTE_SHA256='3d2a3e1af0bf2da628acc364a16fa5f5cadc623cdd18dbcc02b09367be9971cf'
SCHEMA='holo.one-omega-connection-moving-trace-adjoint.v1'
SOURCE_PINS={
 'one_omega_interface_connection_current_candidate_v1':'e51d8d47ee97e20c6aea5aebb4680a65cba79254c2ea0a30fd6a88774b6535e8',
 'one_omega_connection_current_covariant_variation_v1':'d2a1b7af2e9b43eacafdece6d26d30433e6c4fbdb0d46922bf7eace34b30f6de',
 'one_omega_connection_horizontal_ward_v1':'d26d2cf58092eecacebd1f8d7f34f8a35222cd1ef7ec7153f5f0675a7e7e1f89',
}

class MovingTraceError(ValueError):pass


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
        ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def read_json(raw):
    def pairs(items):
        out={}
        for key,value in items:
            if key in out:raise MovingTraceError('duplicate JSON key')
            out[key]=value
        return out
    def invalid(value):raise MovingTraceError('nonfinite JSON constant')
    try:out=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    except (ValueError,UnicodeError) as exc:raise MovingTraceError('invalid JSON') from exc
    if type(out) is not dict:raise MovingTraceError('JSON root must be object')
    return out


def zero(value):
    return all(sp.cancel(x)==0 for x in value) if isinstance(value,sp.MatrixBase) else sp.cancel(value)==0


def clean(value):
    return value.applyfunc(sp.expand) if isinstance(value,sp.MatrixBase) else sp.expand(value)


def bracket(a,b):return a*b-b*a


def inner(a,b):return -sp.trace(a*b)/2


def color(prefix):
    components=sp.symbols(prefix+'_1:4',real=True)
    return sp.Matrix(3,3,lambda a,b:sum(sp.LeviCivita(I,a,b)*components[I] for I in range(3)))


def symmetric(prefix,n=4):
    slots={(i,j):sp.Symbol(f'{prefix}_{i}{j}',real=True) for i in range(n) for j in range(i,n)}
    return sp.Matrix(n,n,lambda i,j:slots[tuple(sorted((i,j)))])


def contraction(a,b):return sum(a[i,j]*b[i,j] for i in range(a.rows) for j in range(a.cols))


def matrix_wedge(left,right):
    result={}
    for a,ca in left.items():
        for b,cb in right.items():
            if set(a)&set(b):continue
            key=tuple(sorted(a+b));sign=(-1)**sum(i>j for i in a for j in b)
            result[key]=result.get(key,sp.zeros(3))+sign*ca*cb
    return {key:clean(value) for key,value in result.items()}


def paired_wedge(left,right):
    result={}
    for a,ca in left.items():
        for b,cb in right.items():
            if set(a)&set(b):continue
            key=tuple(sorted(a+b));sign=(-1)**sum(i>j for i in a for j in b)
            result[key]=result.get(key,0)+sign*inner(ca,cb)
    return {key:sp.expand(value) for key,value in result.items()}


def dual_three_form(vectors):
    return {tuple(i for i in range(4) if i!=mu):(-1)**mu*vectors[mu] for mu in range(4)}


def load_sources(note=NOTE,artifact_directory=HERE/'artifacts'):
    if hashlib.sha256(Path(note).read_bytes()).hexdigest()!=NOTE_SHA256:
        raise MovingTraceError('moving-trace lemma hash mismatch')
    records={}
    for stem,pin in SOURCE_PINS.items():
        raw=(Path(artifact_directory)/(stem+'.json')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=pin:raise MovingTraceError('source byte hash mismatch: '+stem)
        doc=read_json(raw)
        for name,sha in doc['provenance'].items():
            if Path(name).name!=name:raise MovingTraceError('unexpected source provenance path')
            if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=sha:
                raise MovingTraceError('source implementation hash mismatch: '+name)
        records[stem]={'sha256':pin,'schema':doc['schema']}
    return {'lemma_sha256':NOTE_SHA256,'upstreams':records,'physical_gates_inherited':False,
            'source_formula_scope':'complete intrinsic SC variation and tangential Ward; no imported complete embedding map'}


def derive_finite_trace_jets():
    eps,f=sp.symbols('epsilon f',real=True);df=sp.Matrix(sp.symbols('df_0:4',real=True))
    A=[color(f'A{mu}') for mu in range(4)]
    common_h=symmetric('h_common');common_a=[color(f'a_common{mu}') for mu in range(4)]
    gamma=sp.Matrix([[-2,sp.Rational(1,3),0,0],[sp.Rational(1,3),3,0,0],[0,0,4,sp.Rational(1,5)],[0,0,sp.Rational(1,5),5]])
    tangent=sp.zeros(5,4);tangent[0,:]=eps*df.T;tangent[1:,:]=sp.eye(4)
    sides={};residuals={};negative={}
    for side in ('plus','minus'):
        An=color('An_'+side);dAn=[color(f'dAn_{side}{mu}') for mu in range(4)]
        normal=[color(f'dnA_{side}{mu}') for mu in range(4)]
        delta=[color(f'deltaA_{side}{mu}') for mu in range(4)]
        deltaAn=color('deltaAn_'+side);eta=color('eta_'+side)
        deta=[color(f'deta_{side}{mu}') for mu in range(4)]
        # The second jets of exp(epsilon eta) and its inverse are sufficient
        # to differentiate the finite matrix map at zero, and are checked.
        r=sp.eye(3)+eps*eta+eps**2*eta*eta/2
        rinv=sp.eye(3)-eps*eta+eps**2*eta*eta/2
        dr=[eps*d+eps**2*(d*eta+eta*d)/2 for d in deta]
        Lambda=f*An-eta
        dLambda=[df[mu]*An+f*dAn[mu]-deta[mu] for mu in range(4)]
        Dlambda=[dLambda[mu]+bracket(A[mu],Lambda) for mu in range(4)]
        Fn=[normal[mu]-dAn[mu]+bracket(An,A[mu]) for mu in range(4)]
        raw=[]
        for mu in range(4):
            pulled=A[mu]+eps*(delta[mu]+f*normal[mu])+eps*df[mu]*(An+eps*deltaAn)
            finite=r*pulled*rinv-dr[mu]*rinv
            raw.append(clean(finite.diff(eps).subs(eps,0)))
        K=symmetric('K_'+side);dg=symmetric('delta_g_'+side)
        dgn=sp.Matrix(sp.symbols(f'delta_gn_{side}_0:4',real=True));dgnn=sp.Symbol('delta_gnn_'+side,real=True)
        bulk_g=sp.zeros(5);bulk_g[0,0]=1+eps*dgnn
        bulk_g[0,1:]=eps*dgn.T;bulk_g[1:,0]=eps*dgn
        bulk_g[1:,1:]=gamma+2*eps*f*K+eps*dg
        induced=clean((tangent.T*bulk_g*tangent).diff(eps).subs(eps,0))
        metric_sub=dict(zip(dg,common_h-2*f*K))
        connection_sub={symbol:value for mu in range(4) for symbol,value in zip(delta[mu],common_a[mu]-f*Fn[mu]-Dlambda[mu]) if symbol!=0}
        # Replace only the independent upper-triangle color entries. Their
        # negatives are expressions, not independent symbols.
        connection_sub={symbol:value for symbol,value in connection_sub.items() if isinstance(symbol,sp.Symbol)}
        glued_h=clean(induced.xreplace(metric_sub))
        glued_a=[clean(value.xreplace(connection_sub)) for value in raw]
        residuals[side+'_all_36_connection_trace_entries']=sp.Matrix([x for mu in range(4) for x in clean(raw[mu]-delta[mu]-f*Fn[mu]-Dlambda[mu])])
        residuals[side+'_all_16_metric_trace_entries']=clean(induced-dg-2*f*K)
        residuals[side+'_SO3_tangent_and_inverse_jets']=sp.Matrix([x for order in (1,2) for x in clean((r.T*r-sp.eye(3)).diff(eps,order).subs(eps,0))]+[x for order in (1,2) for x in clean((r*rinv-sp.eye(3)).diff(eps,order).subs(eps,0))])
        residuals[side+'_paired_metric_trace']=clean(glued_h-common_h)
        residuals[side+'_paired_connection_trace']=sp.Matrix([x for mu in range(4) for x in clean(glued_a[mu]-common_a[mu])])
        negative[side+'_omit_normal_connection_times_df']=sp.Matrix([x for mu in range(4) for x in df[mu]*An])
        negative[side+'_omit_identification_Deta']=sp.Matrix([x for mu in range(4) for x in clean(deta[mu]+bracket(A[mu],eta))])
        sides[side]={'An':An,'dAn':dAn,'dnA':normal,'deltaA':delta,'eta':eta,'deta':deta,
                     'Fn':Fn,'Lambda':Lambda,'dLambda':dLambda,'Dlambda':Dlambda,'raw_trace':raw,
                     'K':K,'delta_g':dg,'induced_metric':induced,'glued_h':glued_h,'glued_a':glued_a,
                     'connection_substitution':connection_sub,'metric_substitution':metric_sub}
    negative['freeze_both_bulk_metrics_with_distinct_K']=2*f*(sides['plus']['K']-sides['minus']['K'])
    rhoQ=color('target_rotation');drhoQ=[color(f'd_target_rotation{mu}') for mu in range(4)]
    data=sides['plus'];eta_h=data['eta']+rhoQ
    converted=[data['raw_trace'][mu]-drhoQ[mu]-bracket(A[mu],rhoQ) for mu in range(4)]
    expected=[data['deltaA'][mu]+f*data['Fn'][mu]+df[mu]*data['An']+f*data['dAn'][mu]-data['deta'][mu]-drhoQ[mu]+bracket(A[mu],f*data['An']-eta_h) for mu in range(4)]
    residuals['extra_target_rotation_converts_eta_with_plus_sign']=sp.Matrix([x for mu in range(4) for x in clean(converted[mu]-expected[mu])])
    X=sp.Matrix(sp.symbols('tangent_X_0:4',real=True));omega=[color(f'omega_tangent{mu}') for mu in range(4)]
    sigma=color('sigma_tangent')
    etaX=sum((X[mu]*omega[mu] for mu in range(4)),sp.zeros(3))+sigma
    LambdaX=sum((X[mu]*A[mu] for mu in range(4)),sp.zeros(3))-etaX
    residuals['pinned_tangential_compensation_specialization_only']=clean(
        LambdaX-sum((X[mu]*(A[mu]-omega[mu]) for mu in range(4)),sp.zeros(3))+sigma)
    return {'epsilon':eps,'f':f,'df':df,'A':A,'gamma':gamma,'common_h':common_h,'common_a':common_a,
            'sides':sides,'target_rotation':rhoQ,'residuals':residuals,
            'checks':{k:zero(v) for k,v in residuals.items()},'negative':negative}


def derive_cayley_oracle():
    eps,n,t,x,y,z=sp.symbols('epsilon n t x y z',real=True)
    coords=(t,x,y,z);f=1+x*z;angle=x+2*z
    T=[sp.Matrix(3,3,lambda a,b:sp.LeviCivita(I,a,b)) for I in range(3)]
    eta=angle*T[2]
    r=sp.eye(3)+(eps*eta+eps**2*eta*eta/2)/(1+eps**2*angle**2/4)
    An=x*T[0]+z*T[1]
    bulk=[(1+n)*T[0]+x*T[1],z*T[2]+n*x*T[1],n*T[0]+x*z*T[1],x*T[0]+n*z*T[2]]
    delta=[(x+z)*T[2],t*T[0],z*T[2],y*T[1]]
    A=[value.subs(n,0) for value in bulk]
    Fn=[bulk[mu].diff(n).subs(n,0)-An.diff(coords[mu])+bracket(An,A[mu]) for mu in range(4)]
    Lambda=f*An-eta;raw=[];reference=[]
    for mu in range(4):
        pull=(bulk[mu]+eps*delta[mu]).subs(n,eps*f)+eps*sp.diff(f,coords[mu])*An
        finite=r*pull*r.T-r.diff(coords[mu])*r.T
        raw.append(clean(finite.diff(eps).subs(eps,0)))
        reference.append(clean(delta[mu]+f*Fn[mu]+Lambda.diff(coords[mu])+bracket(A[mu],Lambda)))
    residuals={'Cayley_orthogonality':(r.T*r-sp.eye(3)).applyfunc(sp.cancel),
               'Cayley_determinant_one':sp.cancel(r.det()-1),
               'literal_moving_connection_all_36_entries':sp.Matrix([value for mu in range(4) for value in clean(raw[mu]-reference[mu])])}
    witnesses={'nonconstant_normal_displacement':sp.Matrix([sp.diff(f,c) for c in coords]),
               'normal_connection_nonzero':An,'mixed_curvature_nonzero':sp.Matrix([v for matrix in Fn for v in matrix]),
               'nonabelian_identification_commutator':bracket(eta,A[0])}
    return {'coords':coords,'epsilon':eps,'n':n,'f':f,'eta':eta,'r':r,'An':An,'bulk_A':bulk,'deltaA':delta,
            'Fn':Fn,'Lambda':Lambda,'raw_trace':raw,'reference_trace':reference,
            'residuals':residuals,'checks':{k:zero(v) for k,v in residuals.items()},
            'nondegenerate_witnesses':witnesses}


def derive_SC_adjoint(trace):
    chi=sp.Symbol('chi',positive=True);theta,E=sp.symbols('intrinsic_delta_T E_T',real=True)
    tau=symmetric('tau_contrav');C=[color(f'Craised{mu}') for mu in range(4)]
    dC=[color(f'partial_mu_Craised{mu}') for mu in range(4)]
    connection_trace=sp.Matrix(sp.symbols('Gamma_trace_0:4',real=True))
    A=trace['A'];f=trace['f']
    G=chi*sum((dC[mu]+connection_trace[mu]*C[mu]+bracket(A[mu],C[mu]) for mu in range(4)),sp.zeros(3))
    base_boundary=sp.Matrix(sp.symbols('SC_base_Green_boundary_0:4',real=True))
    def variation(h,a):return contraction(tau,h)/2+E*theta-chi*sum(inner(C[mu],a[mu]) for mu in range(4))
    common=variation(trace['common_h'],trace['common_a'])
    residuals={};densities={};sides={}
    for name,data in trace['sides'].items():
        raw=variation(data['induced_metric'],data['raw_trace'])
        Lambda=data['Lambda']
        normal=contraction(tau,data['K'])-chi*sum(inner(C[mu],data['Fn'][mu]) for mu in range(4))
        adjoint=variation(data['delta_g'],data['deltaA'])+f*normal+inner(G,Lambda)
        new_boundary=sp.Matrix([-chi*inner(C[mu],Lambda) for mu in range(4)])
        div_boundary=-chi*sum(inner(dC[mu],Lambda)+inner(C[mu],data['dLambda'][mu])+
                                     connection_trace[mu]*inner(C[mu],Lambda) for mu in range(4))
        residuals[name+'_SC_adjoint_including_G_and_boundary']=sp.expand(raw-adjoint-div_boundary)
        glued=variation(data['glued_h'],data['glued_a'])
        residuals[name+'_one_intrinsic_action_from_common_traces']=sp.expand(glued-common)
        densities[name]=glued
        sides[name]={'raw_variation':raw,'adjoint_interior':adjoint,'normal_coefficient_before_eta_adjoint':normal,
                     'G_Lambda':inner(G,Lambda),'new_boundary':new_boundary,
                     'total_boundary':base_boundary+new_boundary,'new_boundary_divergence':div_boundary}
    negative={'drop_G_Lambda':inner(G,trace['sides']['plus']['Lambda']),
              'drop_IBP_boundary':sides['plus']['new_boundary_divergence'],
              'count_SC_once_per_bulk_face':sp.expand(densities['plus']+densities['minus']-common)}
    return {'chi':chi,'theta':theta,'E_T':E,'tau':tau,'C_raised':C,'G':G,
            'base_boundary':base_boundary,'base_boundary_definition':'J^(alpha beta mu) h_common,alpha beta /2 - N V^mu intrinsic_delta_T',
            'common_intrinsic_variation':common,'sides':sides,'residuals':residuals,
            'checks':{k:zero(v) for k,v in residuals.items()},'negative':negative}


def derive_transport_operator_adjoint():
    f=sp.Symbol('f',real=True);df=sp.Matrix(sp.symbols('df_0:4',real=True))
    G=color('Gop');dG=[color(f'dGop{mu}') for mu in range(4)];R=color('Rop')
    S=[color(f'Sop{mu}') for mu in range(4)];dS=[color(f'dSop{mu}') for mu in range(4)]
    Gamma=sp.Matrix(sp.symbols('Gammaop_trace_0:4',real=True))
    eta=R*f+sum((S[mu]*df[mu] for mu in range(4)),sp.zeros(3))
    raw=-inner(G,eta)
    divGS=sum(inner(dG[mu],S[mu])+inner(G,dS[mu])+Gamma[mu]*inner(G,S[mu]) for mu in range(4))
    coefficient=-inner(G,R)+divGS
    boundary=sp.Matrix([-f*inner(G,S[mu]) for mu in range(4)])
    divboundary=-sum(df[mu]*inner(G,S[mu]) for mu in range(4))-f*divGS
    residual=sp.expand(raw-f*coefficient-divboundary)
    return {'f':f,'df':df,'G':G,'R':R,'S':S,'eta_operator':eta,'raw':raw,
            'local_normal_adjoint':coefficient,'boundary':boundary,'boundary_divergence':divboundary,
            'residuals':{'first_order_eta_operator_full_adjoint':residual},
            'checks':{'first_order_eta_operator_full_adjoint':residual==0},
            'negative':{'drop_df_in_identification':sp.expand(raw+f*inner(G,R)),
                        'drop_operator_boundary':sp.expand(raw-f*coefficient)},
            'not_an_identification_of_the_actual_geometric_eta_operator':True}


def derive_BF_rotation_and_reparametrization(trace):
    orientation=current.derive_oriented_bf_green()
    incidence=orientation['boundary_jump_coefficient']
    A=trace['A'];eta=color('eta_rotation');deta=[color(f'deta_rotation{mu}') for mu in range(4)]
    q=[color(f'Qdual{mu}') for mu in range(4)];dq=[color(f'dQdual{mu}') for mu in range(4)]
    Q=dual_three_form(q);Aform={(mu,):A[mu] for mu in range(4)}
    Deta={(mu,):deta[mu]+bracket(A[mu],eta) for mu in range(4)}
    raw=-paired_wedge(Q,Deta).get((0,1,2,3),0)
    AQ=matrix_wedge(Aform,Q);QA=matrix_wedge(Q,Aform)
    DQ=sum(dq,sp.zeros(3))+AQ.get((0,1,2,3),sp.zeros(3))+QA.get((0,1,2,3),sp.zeros(3))
    border_div=sum(inner(dq[mu],eta)+inner(q[mu],deta[mu]) for mu in range(4))
    dbp,dbm,jp,jm,dJ=(color(name) for name in ('Dbplus','Dbminus','jplus','jminus','DJ'))
    Eplus=dbp+jp;Eminus=dbm+jm
    normal_row=-(dbp-dbm+dJ)
    rhs=jp-jm-dJ-Eplus+Eminus
    bp=dual_three_form([color(f'bplus_dual{mu}') for mu in range(4)])
    bm=dual_three_form([color(f'bminus_dual{mu}') for mu in range(4)])
    jump={key:bp[key]-bm[key] for key in bp};common={(mu,):trace['common_a'][mu] for mu in range(4)}
    delta={};shift={}
    for side in ('plus','minus'):
        data=trace['sides'][side]
        shift[side]={(mu,):trace['f']*data['Fn'][mu]+data['Dlambda'][mu] for mu in range(4)}
        delta[side]={(mu,):trace['common_a'][mu]-shift[side][mu,] for mu in range(4)}
    original=incidence*(paired_wedge(bp,delta['plus']).get((0,1,2,3),0)-paired_wedge(bm,delta['minus']).get((0,1,2,3),0))
    common_part=incidence*paired_wedge(jump,common).get((0,1,2,3),0)
    complements=incidence*(-paired_wedge(bp,shift['plus']).get((0,1,2,3),0)+paired_wedge(bm,shift['minus']).get((0,1,2,3),0))
    # f=0, Eulerian deltaA=0, common eta: a_common=-Deta and
    # Lambda_plus=Lambda_minus=-eta. Both chart contributions must cancel.
    pure_induced={};pure_shifts={}
    for side in ('plus','minus'):
        data=trace['sides'][side]
        substitution={trace['f']:sp.Integer(0),**{v:sp.Integer(0) for v in trace['df']}}
        for old_matrix,new_matrix in [(data['eta'],eta),*zip(data['deta'],deta)]:
            substitution.update({v:new_matrix[i,j] for i in range(3) for j in range(3)
                                 if isinstance((v:=old_matrix[i,j]),sp.Symbol)})
        for old_matrix in data['deltaA']:
            substitution.update({v:sp.Integer(0) for v in old_matrix if isinstance(v,sp.Symbol)})
        pure_induced[side]={(mu,):clean(data['raw_trace'][mu].xreplace(substitution)) for mu in range(4)}
        pure_shifts[side]={(mu,):clean(shift[side][mu,].xreplace(substitution)) for mu in range(4)}
    pure_common=incidence*paired_wedge(jump,pure_induced['plus']).get((0,1,2,3),0)
    pure_complements=incidence*(-paired_wedge(bp,pure_shifts['plus']).get((0,1,2,3),0)
                                +paired_wedge(bm,pure_shifts['minus']).get((0,1,2,3),0))
    residuals={'rotation_three_form_IBP_with_nonabelian_connection':sp.expand(raw+inner(DQ,eta)-border_div),
               'rotation_row_as_bulk_and_interface_equation_combination':clean(normal_row-rhs),
               'BF_reparametrization_retains_both_face_complements':sp.expand(original-common_part-complements),
               'pure_identification_variation_of_fixed_bulk_BF_is_zero':sp.expand(pure_common+pure_complements),
               'pure_identification_trace_comes_from_finite_map':sp.Matrix([v for side in ('plus','minus')
                   for mu in range(4) for v in clean(pure_induced[side][mu,]+Deta[mu,])])}
    negative={'omit_rotation_boundary':sp.expand(raw+inner(DQ,eta)),
              'omit_BF_chart_complements':sp.expand(original-common_part),
              'call_common_rotation_summand_full_eta_Euler':pure_common}
    return {'orientation_coefficients':{key:orientation[key] for key in ('boundary_jump_coefficient','required_B_jump_coefficient','compatibility_current_coefficient')},
            'rotation_input':raw,'DQ':DQ,'rotation_interior':-inner(DQ,eta),'rotation_boundary_divergence':border_div,
            'bulk_connection_rows':(Eplus,Eminus),'full_row_before_bulk_equations':normal_row,
            'row_on_bulk_equations':jp-jm-dJ,
            'original_BF_in_Eulerian_variables':original,'common_trace_BF_part':common_part,
            'BF_chart_complements':complements,'pure_identification_common_part':pure_common,
            'pure_identification_complements':pure_complements,
            'residuals':residuals,'checks':{k:zero(v) for k,v in residuals.items()},'negative':negative,
            'not_the_complete_moving_BF_or_total_groupoid_Euler':True}


def derive_model():
    trace=derive_finite_trace_jets();cayley=derive_cayley_oracle()
    sc=derive_SC_adjoint(trace);operator=derive_transport_operator_adjoint()
    bf=derive_BF_rotation_and_reparametrization(trace)
    parts={'trace':trace,'Cayley':cayley,'SC':sc,'eta_operator':operator,'BF':bf}
    checks={prefix+'_'+key:value for prefix,data in parts.items() for key,value in data['checks'].items()}
    negative={prefix+'_'+key:not zero(value) for prefix,data in parts.items() for key,value in data.get('negative',{}).items()}
    witnesses={key:not zero(value) for key,value in cayley['nondegenerate_witnesses'].items()}
    return {'parts':parts,'checks':checks,'negative_controls':negative,'nondegenerate_witnesses':witnesses}


def serialize(value):
    if isinstance(value,sp.MatrixBase):return [[sp.sstr(value[i,j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value,sp.Basic):return sp.sstr(value)
    if isinstance(value,dict):return {str(key):serialize(v) for key,v in value.items()}
    if isinstance(value,(list,tuple)):return [serialize(v) for v in value]
    return value


def build_payload():
    sources=load_sources();model=derive_model()
    if not all(model['checks'].values()) or not all(model['negative_controls'].values()) or not all(model['nondegenerate_witnesses'].values()):
        failed=[key for section in ('checks','negative_controls','nondegenerate_witnesses') for key,value in model[section].items() if not value]
        raise MovingTraceError('moving trace derivation failed: '+','.join(failed))
    parts=model['parts']
    out={'schema':SCHEMA,'sources':sources,
         'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
         'checks':model['checks'],'negative_controls':model['negative_controls'],'nondegenerate_witnesses':model['nondegenerate_witnesses'],
         'finite_trace':serialize({side:{key:parts['trace']['sides'][side][key] for key in ('raw_trace','Fn','Lambda','induced_metric','glued_h','glued_a')} for side in ('plus','minus')}),
         'Cayley_oracle':serialize({key:parts['Cayley'][key] for key in ('f','r','An','Fn','raw_trace')}),
         'SC_adjoint':serialize({'G':parts['SC']['G'],'sides':parts['SC']['sides'],'base_boundary_definition':parts['SC']['base_boundary_definition']}),
         'eta_operator':serialize({key:parts['eta_operator'][key] for key in ('eta_operator','raw','local_normal_adjoint','boundary')}),
         'BF_adjoint':serialize({key:parts['BF'][key] for key in ('orientation_coefficients','rotation_interior','rotation_boundary_divergence','row_on_bulk_equations','BF_chart_complements','pure_identification_common_part','pure_identification_complements')}),
         'scope':{'domain':'local smooth Gaussian collars and one common intrinsic trace, target frame horizontal',
                  'T':'intrinsic delta T is independent; a postulated bulk-clock pullback requires an additional chain rule',
                  'eta':'identification relative to horizontal target; normal geometric operator not inferred from tangential sigma_X',
                  'BF':'common trace summand plus mandatory Eulerian chart complements, with corrected literal Stokes orientation'},
         'decision':{'moving_connection_and_metric_trace_maps_derived':True,
                     'SC_adjoint_retains_G_Lambda_and_boundary':True,
                     'paired_gluing_and_single_intrinsic_action_checked':True,
                     'first_order_identification_operator_adjoint_checked':True,
                     'BF_rotation_summand_and_chart_complements_checked':True,
                     'eta_is_new_independent_physical_degree_of_freedom':False,
                     'actual_normal_geometric_eta_operator_identified':False,
                     'normal_eta_inferred_from_tangential_sigma':False,
                     'common_BF_trace_part_is_entire_moving_BF_Green':False,
                     'complete_total_groupoid_Euler_identified':False,
                     'complete_EH_GHY_moving_variation':False,'global_admissible_embedding_space_constructed':False,
                     'new_action_adopted':False,'coupled_existence_proved':False,
                     'full_N4':False,'full_N7':False,'full_P4':False,'C1':False,'N1':False,'B4':False,'B5':False}}
    out['calculation_digest']=digest(out)
    return out


def validate_payload(payload):
    if type(payload) is not dict:raise MovingTraceError('receipt must be object')
    body={k:v for k,v in payload.items() if k!='calculation_digest'}
    try:valid=payload.get('calculation_digest')==digest(body)
    except (TypeError,ValueError) as exc:raise MovingTraceError('invalid receipt value') from exc
    if not valid:raise MovingTraceError('receipt calculation digest mismatch')
    expected=build_payload()
    if payload!=expected:raise MovingTraceError('receipt differs from fresh source-bound derivation')
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
    print(json.dumps({'checks_passed':len(out['checks']),'negative_controls':len(out['negative_controls']),
                      'nondegenerate_witnesses':len(out['nondegenerate_witnesses']),'calculation_digest':out['calculation_digest']}))
    return 0

if __name__=='__main__':raise SystemExit(main())
