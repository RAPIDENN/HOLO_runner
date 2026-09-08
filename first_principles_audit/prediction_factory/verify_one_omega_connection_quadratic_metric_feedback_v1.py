#!/usr/bin/env python3
"""Leading metric feedback of the proposed localized connection-current lift.

Independent adjoint and literal mixed-action derivations are compared.
The continuum norm statement belongs to the pinned analytic lemma; these
finite identities neither solve Einstein nor define physical energy.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_connection_quadratic_metric_feedback_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_quadratic_metric_feedback_v1.py'
OUTPUT=HERE/'artifacts/one_omega_connection_quadratic_metric_feedback_v1.json'
SCHEMA='holo.one-omega-connection-quadratic-metric-feedback.v1'
NOTE_SHA256='aec6ee2f079bb761bda83b41948e4a3074d1c2b08f1c45191bd70c2ac3d7a5fb'
SOURCE_PINS={
    'one_omega_connection_current_covariant_variation_v1':'d2a1b7af2e9b43eacafdece6d26d30433e6c4fbdb0d46922bf7eace34b30f6de',
    'one_omega_connection_horizontal_ward_v1':'d26d2cf58092eecacebd1f8d7f34f8a35222cd1ef7ec7153f5f0675a7e7e1f89',
    'one_omega_connection_localized_torque_lift_v1':'b16337522d149b97952c347286ad85e7203bbe7c8a5598b15c359811a80b708b',
}
LIFT_NOTE_SHA256='8af2a8626df9fd665a721d203e30536396d85a83093a9352cfda4003f960561f'

class MetricFeedbackError(ValueError):
    """A source pin, exact identity, or recomputed receipt failed."""


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
        ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def read_json(raw):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise MetricFeedbackError('duplicate JSON key')
            out[k]=v
        return out
    def invalid(value):raise MetricFeedbackError('nonfinite JSON constant')
    try:out=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    except (ValueError,UnicodeError) as exc:raise MetricFeedbackError('invalid JSON') from exc
    if type(out) is not dict:raise MetricFeedbackError('JSON root must be object')
    return out


def zero(value):
    return all(sp.cancel(x)==0 for x in value) if isinstance(value,sp.MatrixBase) else sp.cancel(value)==0


def clean(value):
    return value.applyfunc(sp.expand) if isinstance(value,sp.MatrixBase) else sp.expand(value)


def curl(vector,coords):
    return sp.Matrix([sum(sp.LeviCivita(i,j,k)*sp.diff(vector[k],coords[j])
                          for j in range(3) for k in range(3)) for i in range(3)])


def divergence(vector,coords):
    return sum(sp.diff(vector[i],coords[i]) for i in range(3))


def inner(a,b):return sum(a[i,j]*b[i,j] for i in range(3) for j in range(3))/2


def load_sources(note=NOTE,artifact_directory=HERE/'artifacts'):
    if hashlib.sha256(Path(note).read_bytes()).hexdigest()!=NOTE_SHA256:
        raise MetricFeedbackError('feedback lemma hash mismatch')
    records={}
    for stem,pin in SOURCE_PINS.items():
        raw=(Path(artifact_directory)/(stem+'.json')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=pin:
            raise MetricFeedbackError('source byte hash mismatch: '+stem)
        doc=read_json(raw)
        for name,sha in doc.get('provenance',{}).items():
            if Path(name).name!=name or not name.endswith(('.py','.md')):
                raise MetricFeedbackError('unexpected source provenance path')
            if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=sha:
                raise MetricFeedbackError('source implementation hash mismatch: '+name)
        records[stem]={'sha256':pin,'schema':doc['schema']}
    lift_note=HERE/'one_omega_connection_localized_torque_lift_lemma_v1.md'
    if hashlib.sha256(lift_note.read_bytes()).hexdigest()!=LIFT_NOTE_SHA256:
        raise MetricFeedbackError('source lift lemma hash mismatch')
    return {'lemma_sha256':NOTE_SHA256,'upstreams':records,
            'lift_lemma_sha256':LIFT_NOTE_SHA256,'physical_gates_inherited':False,
            'method':'pinned covariant formulas plus independent fresh local and Fourier algebra; no imported large model'}


def derive_local_variation():
    coords=sp.symbols('x y z',real=True);chi=sp.Symbol('chi',positive=True)
    theta=sp.Matrix([sp.Function(f'Theta{i+1}')(*coords) for i in range(3)])
    hpairs={(i,j):sp.Function(f'h{i+1}{j+1}')(*coords) for i in range(3) for j in range(i,3)}
    h=sp.Matrix(3,3,lambda i,j:hpairs[tuple(sorted((i,j)))])
    theta_matrix=sp.Matrix(3,3,lambda a,b:sum(sp.LeviCivita(I,a,b)*theta[I] for I in range(3)))
    D=[theta_matrix.diff(x) for x in coords]
    C=[-d for d in D]
    # This is the pinned current definition, specialized to the static Cartesian port.
    J=[chi*c for c in C]
    tau_adjoint=sp.Matrix(3,3,lambda i,j:-sum(
        sp.diff(J[i][j,k]+J[j][i,k],coords[k])/2 for k in range(3)))
    v=curl(theta,coords)
    reference=sp.Matrix(3,3,lambda i,j:chi*(sp.diff(v[j],coords[i])+sp.diff(v[i],coords[j]))/2)
    # Independent oracle: vary e=I-h/2 and the lower Christoffel symbol.
    # Do not read the desired curl-metric formula as the input connection.
    delta_omega=[]
    for i in range(3):
        frame=sp.Matrix(3,3,lambda a,b:-sp.diff(h[a,b],coords[i])/2)
        christoffel=sp.Matrix(3,3,lambda a,b:(sp.diff(h[a,b],coords[i])+
            sp.diff(h[a,i],coords[b])-sp.diff(h[i,b],coords[a]))/2)
        delta_omega.append(clean(frame+christoffel))
    mixed=sp.expand(-chi*sum(inner(D[i],delta_omega[i]) for i in range(3)))
    metric_euler={}
    tau_literal=sp.zeros(3)
    for (a,b),field in hpairs.items():
        euler=-sum(sp.diff(sp.diff(mixed,sp.diff(field,x)),x) for x in coords)
        metric_euler[(a,b)]=sp.expand(euler)
        # delta S=(1/2)sum_ij tau_ij h_ij. The independent off-diagonal
        # metric entry occurs twice in the complete tensor contraction.
        tau_literal[a,b]=tau_literal[b,a]=sp.expand((2 if a==b else 1)*euler)
    rho=-chi*sp.Matrix([sum(sp.diff(theta[I],x,2) for x in coords) for I in range(3)])
    G_matrix=sp.Matrix(3,3,lambda i,j:sum(sp.LeviCivita(I,i,j)*rho[I] for I in range(3)))
    div_tau=sp.Matrix([sum(sp.diff(tau_adjoint[i,j],coords[i]) for i in range(3)) for j in range(3)])
    div_G=sp.Matrix([sum(sp.diff(G_matrix[i,j],coords[i]) for i in range(3)) for j in range(3)])
    epsilon,variation=sp.symbols('epsilon metric_variation',real=True)
    literal=-chi*sum(inner(epsilon**2*D[i]+variation*delta_omega[i],
                          epsilon**2*D[i]+variation*delta_omega[i]) for i in range(3))/2
    actual_mixed=sp.expand(sp.diff(literal,variation).subs(variation,0)).coeff(epsilon,2)
    actual_value=sp.expand(literal.subs(variation,0))
    action_quartic=-chi*sum(inner(d,d) for d in D)/2
    kappa_t=sp.Matrix(sp.symbols('kappa_t1:4',real=True))
    C_t=sp.zeros(3);kappa_spatial=sp.zeros(3)
    V=sp.Matrix([chi*(sum(C_t[a,b]*kappa_t[a] for a in range(3))+
             sum(C[i][a,b]*kappa_spatial[i,a] for i in range(3) for a in range(3))) for b in range(3)])
    residuals={
        'all_nine_adjoint_entries':clean(tau_adjoint-reference),
        'literal_mixed_metric_Euler_all_nine_entries':clean(tau_literal-tau_adjoint),
        'connection_oracle_is_antisymmetric':sp.Matrix([x for d in delta_omega for x in d+d.T]),
        'literal_mixed_action_order_two':clean(actual_mixed-mixed),
        'prescribed_action_value_has_only_order_four':clean(actual_value-epsilon**4*action_quartic),
        'spatial_trace_zero':clean(sp.trace(tau_adjoint)),
        'divergence_equals_minus_half_curl_rho':clean(div_tau+curl(rho,coords)/2),
        'horizontal_Ward_sign_and_half':clean(div_tau-div_G/2),
        'clock_V_zero_with_arbitrary_nonzero_kappa_t':V,
    }
    negative={
        'freeze_metric_dependent_omega':tau_literal,
        'flip_metric_source_sign':clean(tau_literal+tau_adjoint),
        'omit_metric_half_weight':clean(tau_literal-tau_adjoint/2),
        'flip_horizontal_G_image_sign':clean(div_tau+div_G/2),
        'mistake_action_order_four_for_metric_order_four':actual_mixed,
    }
    return {'coords':coords,'chi':chi,'theta':theta,'h':h,'J':J,'v':v,
            'delta_omega_literal':delta_omega,'mixed_density':mixed,
            'metric_euler':metric_euler,'tau_adjoint':clean(tau_adjoint),'tau_literal':tau_literal,
            'rho':rho,'G_H':G_matrix,'div_tau':clean(div_tau),'div_G':clean(div_G),
            'V':V,'literal_action_coefficient_four':action_quartic,
            'residuals':residuals,'checks':{k:zero(v) for k,v in residuals.items()},'negative':negative}


def derive_source_structure():
    coords=sp.symbols('x y z',real=True)
    F=sp.Function('F')(*coords);U=sp.Function('U')(*coords)
    kappa,y=sp.symbols('kappa_R y_positive',positive=True)
    gradF=sp.Matrix([sp.diff(F,x) for x in coords]);gradU=sp.Matrix([sp.diff(U,x) for x in coords])
    rho=kappa*y*y*gradF.cross(gradU);W=kappa*y*y*F*gradU
    residuals={'actual_port_rho_is_curl_W':clean(rho-curl(W,coords)),
               'actual_port_divergence_zero':clean(divergence(rho,coords))}
    return {'coords':coords,'F':F,'U':U,'rho':rho,'W':W,'residuals':residuals,
            'checks':{k:zero(v) for k,v in residuals.items()},
            'analytic_input':'F real compact smooth; U=g(|D|)F smooth from pinned Robin multiplier; W compact smooth, hence integral rho=0'}


def hermitian_squared(value):return sum(sp.conjugate(entry)*entry for entry in value)


def fourier_feedback(k,r):
    p2=k.dot(k);c=k.cross(r)
    return -(k*c.T+c*k.T)/(2*p2)


def derive_fourier():
    k=sp.Matrix(sp.symbols('k1:4',real=True))
    real=sp.Matrix(sp.symbols('rho_real1:4',real=True));imag=sp.Matrix(sp.symbols('rho_imag1:4',real=True))
    r=real+sp.I*imag;chi=sp.Symbol('chi',positive=True);p2=k.dot(k)
    theta=r/(chi*p2);c=k.cross(r)
    # Apply the current adjoint before substituting the desired stress formula.
    J=[sp.Matrix(3,3,lambda a,b:-chi*sp.I*k[i]*sum(sp.LeviCivita(I,a,b)*theta[I] for I in range(3))) for i in range(3)]
    actual=sp.Matrix(3,3,lambda i,j:-sp.I*sum(k[l]*(J[i][j,l]+J[j][i,l])/2 for l in range(3)))
    expected=fourier_feedback(k,r)
    numerator=-(k*c.T+c*k.T)
    norm_numerator=hermitian_squared(numerator)
    norm_r=hermitian_squared(r);longitudinal=hermitian_squared(sp.Matrix([k.dot(r)]))
    Q=p2*sp.eye(3)-k*k.T
    transverse_r=k.cross(r)
    transverse_c=k.cross(transverse_r)
    transverse_numerator=-(k*transverse_c.T+transverse_c*k.T)
    residuals={
        'all_nine_Poisson_adjoint_entries':(actual-expected).applyfunc(sp.cancel),
        'Hermitian_general_complex_norm_numerator':sp.expand(norm_numerator-2*p2*(p2*norm_r-longitudinal)),
        'transverse_complex_source_exact_half_norm_numerator':sp.expand(
            hermitian_squared(transverse_numerator)-2*p2*p2*hermitian_squared(transverse_r)),
        'double_transverse_projection_zero':clean(Q*numerator*Q),
        'spatial_trace_zero':sp.expand(sp.trace(numerator)),
        'Fourier_Ward_divergence':clean(k.T*numerator+p2*c.T),
        'chi_cancels_from_feedback':actual.diff(chi).applyfunc(sp.cancel),
        'source_transversality':sp.expand(k.dot(transverse_r)),
    }
    # The arbitrary complex longitudinal amplitude is a deliberate counterexample.
    alpha,beta=sp.symbols('longitudinal_real longitudinal_imag',real=True)
    rlong=(alpha+sp.I*beta)*k
    longitudinal_tau=fourier_feedback(k,rlong)
    negative={
        'half_norm_without_source_transversality':sp.expand(hermitian_squared(rlong)/2-hermitian_squared(longitudinal_tau)),
        'non_Hermitian_complex_tensor_norm':sp.expand(sum(e*e for e in numerator)-norm_numerator),
    }
    return {'k':k,'rho':r,'chi':chi,'p_squared':p2,'theta':theta,'tau':expected,
            'actual_tau_from_current':actual,'Hermitian_norm_squared':norm_numerator/(4*p2*p2),
            'general_norm_reference':(norm_r-longitudinal/p2)/2,
            'transverse_rho':transverse_r,'projector':Q/p2,
            'longitudinal_counterexample':rlong,'longitudinal_counterexample_tau':longitudinal_tau,
            'residuals':residuals,'checks':{k:zero(v) for k,v in residuals.items()},'negative':negative,
            'domain':'real spatial k != 0; rho Fourier components arbitrary complex; norm equality uses k dot rho=0'}


def derive_static_projection(fourier):
    """Orthogonal vector projection for a generic complex symmetric tensor.

    Its Ward-fixed value is checked independently of the particular Poisson
    representative. This is a static statement with C0=C1=0, not a claim
    about a time-dependent response or the sum of all stress tensors.
    """
    k=fourier['k'];p2=fourier['p_squared'];Q=p2*sp.eye(3)-k*k.T
    entries={(i,j):sp.Symbol(f'Sreal{i}{j}',real=True)+sp.I*sp.Symbol(f'Simag{i}{j}',real=True)
             for i in range(3) for j in range(i,3)}
    S=sp.Matrix(3,3,lambda i,j:entries[tuple(sorted((i,j)))])
    def numerator(tensor):
        t=Q*tensor*k
        return k*t.T+t*k.T
    N=numerator(S);vector=N/p2**2
    complement_numerator=p2**2*S-N
    orthogonal=sp.expand(sum(sp.conjugate(N[i,j])*complement_numerator[i,j]
                            for i in range(3) for j in range(3)))
    # Impose the Ward row only after deriving the projector on arbitrary S.
    r=fourier['rho'];ward_Sk=-k.cross(r)/2
    projected_from_ward=(k*(Q*ward_Sk).T+(Q*ward_Sk)*k.T)/p2**2
    tau=fourier['tau']
    residuals={
        'projector_idempotence_polynomial':clean(numerator(N)-p2**2*N),
        'Hermitian_vector_complement_orthogonality':orthogonal,
        'Ward_fixes_vector_projection_to_Poisson_feedback':(projected_from_ward-tau).applyfunc(sp.cancel),
        'Poisson_feedback_saturates_vector_projection':(numerator(tau)/p2**2-tau).applyfunc(sp.cancel),
        'complement_has_no_vector_component':clean(numerator(complement_numerator)),
    }
    # General longitudinal additions are orthogonal to V but can violate the
    # complete Ward row; the theorem imposes that row separately.
    return {'tensor':S,'vector_projection':vector,'complement':S-vector,
            'Ward_fixed_S_times_k':ward_Sk,'projection_from_Ward':projected_from_ward,
            'residuals':residuals,'checks':{name:zero(value) for name,value in residuals.items()},
            'hypotheses':'Minkowski/cartesian background, T0=t, C0=C1=0, static continuation, G2=+rho, fixed first-order data and transverse rho',
            'norm_bound':'||tau_C,spatial^(2)||² >= ||rho||²/2; equality for the Poisson port; Hermitian spatial norm only',
            'does_not_prove_cancellation_against_other_sectors':True,
            'do_not_add_unknown_linear_H18_connection_response_twice':True}


def serialize(value):
    if isinstance(value,sp.MatrixBase):return [[sp.sstr(value[i,j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value,sp.Basic):return sp.sstr(value)
    if isinstance(value,dict):return {str(k):serialize(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serialize(v) for v in value]
    return value


def derive_model():
    local=derive_local_variation();source=derive_source_structure();fourier=derive_fourier()
    projection=derive_static_projection(fourier)
    checks={prefix+'_'+k:v for prefix,data in (('local',local),('source',source),('Fourier',fourier),('projection',projection)) for k,v in data['checks'].items()}
    negative={prefix+'_'+k:not zero(v) for prefix,data in (('local',local),('Fourier',fourier)) for k,v in data['negative'].items()}
    return {'local':local,'source':source,'fourier':fourier,'static_projection':projection,'checks':checks,'negative_controls':negative}


def build_payload():
    sources=load_sources();model=derive_model()
    if not all(model['checks'].values()) or not all(model['negative_controls'].values()):
        failed=[k for k,v in model['checks'].items() if not v]+[k for k,v in model['negative_controls'].items() if not v]
        raise MetricFeedbackError('metric feedback derivation failed: '+','.join(failed))
    out={'schema':SCHEMA,'sources':sources,
         'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
         'checks':model['checks'],'negative_controls':model['negative_controls'],
         'local_variation':serialize({k:model['local'][k] for k in ('J','mixed_density','tau_adjoint','tau_literal','rho','G_H','div_tau','V','literal_action_coefficient_four')}),
         'source_structure':serialize({k:model['source'][k] for k in ('rho','W','analytic_input')}),
         'Fourier':serialize({k:model['fourier'][k] for k in ('k','rho','p_squared','theta','tau','general_norm_reference','projector','domain')}),
         'static_projection':serialize({k:model['static_projection'][k] for k in ('vector_projection','projection_from_Ward','hypotheses','norm_bound')}),
         'analytic_results':{'actual_source':'compact smooth curl, transverse Fourier amplitude and zero mean',
                             'norm':'all nine spatial tensor entries, Hermitian Fourier norm; ||tau^(2)||²=||rho||²/2',
                             'Sobolev':'same equality for every common nonnegative scalar Fourier weight for which norms exist',
                             'IR':'tau is an order-zero bounded multiplier; the distinct L2 Poisson lift uses zero mean',
                             'chi':'fixed F and Robin data imply rho and the leading metric coefficient are independent of chi',
                             'orders':'coefficient of epsilon² has no factorial; isolated channel action/energy starts at epsilon⁴'},
         'decision':{'leading_metric_source_derived_from_both_variations':True,
                     'actual_port_source_has_exact_chi_independent_half_squared_norm':True,
                     'leading_source_is_spatial_vector_with_zero_TT_projection':True,
                     'conditional_static_connection_contribution_has_half_squared_norm_lower_bound':True,
                     'lower_bound_proves_no_cancellation_with_other_sectors':False,
                     'unknown_linear_H18_connection_operator_should_be_added_twice':False,
                     'connection_term_alone_has_conserved_metric_source':False,
                     'spatial_tensor_norm_is_total_physical_energy':False,
                     'quartic_action_value_implies_no_quadratic_metric_feedback':False,
                     'prescribed_port_solves_full_linear_Einstein_equations':False,
                     'complete_second_order_Einstein_embedding_solution':False,
                     'static_lift_uses_temporal_chart_at_s_zero':False,
                     'new_action_adopted':False,'chi_value_selected':False,
                     'full_N4':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}
    out['calculation_digest']=digest(out)
    return out


def validate_payload(payload):
    if type(payload) is not dict:raise MetricFeedbackError('receipt must be object')
    body={k:v for k,v in payload.items() if k!='calculation_digest'}
    try:valid=payload.get('calculation_digest')==digest(body)
    except (TypeError,ValueError) as exc:raise MetricFeedbackError('invalid receipt value') from exc
    if not valid:raise MetricFeedbackError('receipt calculation digest mismatch')
    expected=build_payload()
    if payload!=expected:raise MetricFeedbackError('receipt differs from fresh source-bound derivation')
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
                      'calculation_digest':out['calculation_digest']}))
    return 0

if __name__=='__main__':raise SystemExit(main())
