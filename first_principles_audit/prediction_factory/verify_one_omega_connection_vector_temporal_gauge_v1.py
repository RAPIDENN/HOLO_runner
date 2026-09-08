#!/usr/bin/env python3
"""A regular N_a=0 chart of the proposed, source-bound H18 vector response.

The input matrix is recomputed by the H18 assembler; its desired vector
formulas are not input data. This proves coefficient bounds in one selected
linear chart, not the full BF/embedding quotient or imaginary-axis control.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp
if __package__:
    from . import verify_one_omega_connection_candidate_response_v1 as candidate
    from . import verify_one_omega_zero_momentum_linear_v1 as homogeneous
else:
    import verify_one_omega_connection_candidate_response_v1 as candidate
    import verify_one_omega_zero_momentum_linear_v1 as homogeneous

HERE=Path(__file__).resolve().parent
NOTE=HERE/'one_omega_connection_vector_temporal_gauge_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_vector_temporal_gauge_v1.py'
OUTPUT=HERE/'artifacts/one_omega_connection_vector_temporal_gauge_v1.json'
NOTE_SHA256='264f0e9b6035364553a43b133b81f18d600e92f2383613544d0bf428f654badd'
SCHEMA='holo.one-omega-connection-vector-temporal-gauge.v1'
SOURCE_PINS={
    'one_omega_connection_candidate_response_v1':'724e8f84148047105b9a4d997c3cdd14c03eceaa665d98a8fb55cbe1852f9c74',
    'one_omega_connection_horizontal_ward_v1':'d26d2cf58092eecacebd1f8d7f34f8a35222cd1ef7ec7153f5f0675a7e7e1f89',
    'one_omega_zero_momentum_linear_v1':'f2c83fa82a87353b01d43790ddfe73bd8e42febaca2a5554ddb8a5f5c6d96539',
}
SOURCE_NOTE_PINS={
    'one_omega_connection_candidate_response_lemma_v1.md':'f78d97a347b8269913ee0fe0f47ee0fd6386cb32e4365c8a17de42a287ff45a5',
    'one_omega_connection_horizontal_ward_lemma_v1.md':'6766dcacb59d9104aad83ce941ddef3d9c55c70d36339790440594487c31d14e',
    'one_omega_zero_momentum_linear_lemma_v1.md':'7f1129dd5b9b066ba1cafb20dcacac8a8a6d025586b16a172704bc98b1215d4f',
}

class TemporalGaugeError(ValueError):
    """An input pin, exact identity, or source-bound receipt failed."""


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
        ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def read_json(raw):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise TemporalGaugeError('duplicate JSON key')
            out[k]=v
        return out
    def invalid(value):raise TemporalGaugeError('nonfinite JSON constant')
    try:out=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    except (ValueError,UnicodeError) as exc:raise TemporalGaugeError('invalid JSON') from exc
    if type(out) is not dict:raise TemporalGaugeError('JSON root must be object')
    return out


def zero(value):
    return all(sp.cancel(x)==0 for x in value) if isinstance(value,sp.MatrixBase) else sp.cancel(value)==0


def clean(value):
    return value.applyfunc(sp.cancel) if isinstance(value,sp.MatrixBase) else sp.cancel(value)


def load_sources(note=NOTE,artifact_directory=HERE/'artifacts'):
    if hashlib.sha256(Path(note).read_bytes()).hexdigest()!=NOTE_SHA256:
        raise TemporalGaugeError('temporal lemma hash mismatch')
    records={}
    for stem,pin in SOURCE_PINS.items():
        raw=(Path(artifact_directory)/(stem+'.json')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=pin:
            raise TemporalGaugeError('source byte hash mismatch: '+stem)
        doc=read_json(raw)
        for name,sha in doc.get('provenance',{}).items():
            if Path(name).name!=name or not name.endswith(('.py','.md')):
                raise TemporalGaugeError('unexpected source provenance path')
            if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=sha:
                raise TemporalGaugeError('source implementation hash mismatch: '+name)
        records[stem]={'sha256':pin,'schema':doc['schema']}
    for name,pin in SOURCE_NOTE_PINS.items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=pin:
            raise TemporalGaugeError('source lemma hash mismatch: '+name)
    # Pin transitive implementations consumed by the fresh H18 calculation.
    try:transitive=candidate.load_sources()
    except candidate.CandidateResponseError as exc:
        raise TemporalGaugeError('H18 source binding failed') from exc
    return {'lemma_sha256':NOTE_SHA256,'upstreams':records,
            'upstream_lemmas':SOURCE_NOTE_PINS.copy(),'H18_transitive_sources':transitive,
            'physical_gates_inherited':False,
            'analytic_input':'finite positive spectral measure and RHP proof in pinned H18 lemma'}


def analyze_sector(block,orientation,w,q,chi,B):
    """Transform the supplied three-row operator, preserving sources and pivots."""
    if orientation not in (-1,1) or block.shape!=(3,3):
        raise TemporalGaugeError('expected a three-row transverse sector and orientation +/-1')
    o=sp.Integer(orientation)
    J=sp.Matrix([[1/w,0],[o/(2*w),1]])
    retained=block.extract([1,2],[1,2])
    transformed=clean(J.T*retained*J)
    pivot=transformed[0,0]
    schur=clean(transformed[1,1]-transformed[1,0]*transformed[0,1]/pivot)
    U,Psi,fU,fPsi=sp.symbols('U Psi f_U f_Psi')
    solution_U=clean((fU-transformed[0,1]*Psi)/pivot)
    retained_solution=clean(J*sp.Matrix([solution_U,Psi]))
    original_solution=sp.Matrix([0,*retained_solution])
    compatible_force=sp.Matrix([q*fU,w*fU-o*fPsi/2,fPsi])
    full_residual=clean(block*original_solution-compatible_force)
    remaining=clean(schur*Psi-fPsi+transformed[1,0]*fU/pivot)
    denominator=2*B+chi
    expected_reconstruction=sp.Matrix([
        4*fU/(w*denominator)-2*o*chi*Psi/denominator,
        2*o*fU/(w*denominator)+2*B*Psi/denominator])
    gauge=sp.I*sp.Matrix([-w,q,o*q/2])
    invariant_map=sp.Matrix([[q,w,0],[0,-o/2,1]])
    ward=clean(block[0,:]-q/w*(block[1,:]+o*block[2,:]/2))
    qzero=clean(retained.subs(q,0))
    residuals={
        'gauge_null':clean(block*gauge),
        'invariant_map_annihilates_gauge':clean(invariant_map*gauge),
        'ward_row':ward,
        'chart_determinant':clean(J.det()-1/w),
        'retained_pivot':clean(pivot-denominator/4),
        'mixed_entry':clean(transformed[0,1]-o*chi*w/2),
        'schur':clean(schur-(2*chi*B*w*w/denominator-chi*q*q)),
        'determinant_with_chart_and_pivot':clean(retained.det()-w*w*pivot*schur),
        'forced_reconstruction':clean(retained_solution-expected_reconstruction),
        'all_three_forced_rows':clean(full_residual-sp.Matrix([0,-o*remaining/2,remaining])),
        'force_covector':clean(J.T*compatible_force[1:,0]-sp.Matrix([fU,fPsi])),
        'direct_q_zero_matrix':clean(qzero-sp.diag(B*w*w/2,chi*w*w)),
        'direct_q_zero_determinant':clean(qzero.det()-chi*B*w**4/2),
        'q_zero_factorization':clean((w*w*pivot*schur).subs(q,0)-qzero.det()),
    }
    return {'orientation':orientation,'block':block,'retained':retained,'chart':J,
            'invariant_map':invariant_map,'gauge':gauge,'transformed':transformed,
            'pivot':pivot,'Schur':schur,'q_zero_retained':qzero,
            'force_symbols':(fU,fPsi),'response_symbols':(U,Psi),
            'compatible_force':compatible_force,'original_solution':original_solution,
            'remaining_row':remaining,'full_forced_residual':full_residual,
            'residuals':residuals,'checks':{k:zero(v) for k,v in residuals.items()}}


def derive_bounds():
    sigma,b,chi,r=sp.symbols('sigma b chi r',positive=True)
    margin=sp.Symbol('nonnegative_PR_margin',nonnegative=True)
    Y=sp.Symbol('imaginary_s_denominator',real=True)
    q=sp.Symbol('q_nonnegative',nonnegative=True)
    d=2*b+chi;X=d*sigma+margin
    reciprocal_squared=r*r/(X*X+Y*Y)
    gap=r*r/(d*d*sigma*sigma)-reciprocal_squared
    manifest=r*r*(2*d*sigma*margin+margin*margin+Y*Y)/(d*d*sigma*sigma*(X*X+Y*Y))
    K0=2*chi*b/d
    fU,fPsi=sp.symbols('abs_f_U abs_f_Psi',nonnegative=True)
    lower=r*sigma*K0+chi*sigma*q*q/r
    bound_Psi=(fPsi+2*chi*r*r*fU/(d*sigma))/lower
    bounds={
        'inverse_denominator':r/(d*sigma),
        'inverse_w_denominator':1/(d*sigma),
        'absolute_Schur_lower_bound':lower,'forced_Psi_upper_bound':bound_Psi,
        'forced_H_upper_bound':4*fU/(d*sigma)+2*chi*r*bound_Psi/(d*sigma),
        'forced_theta_upper_bound':2*fU/(d*sigma)+(1+chi*r/(d*sigma))*bound_Psi,
    }
    checks={
        'reciprocal_bound_squared_gap_identity':zero(gap-manifest),
        'reciprocal_bound_squared_gap_nonnegative':manifest.is_nonnegative is True,
        'w_inverse_squared_bound':zero(gap/r**2-manifest/r**2),
        'forced_Schur_lower_bound_strictly_positive':lower.is_positive is True,
        'K0_strictly_positive':K0.is_positive is True,
        'forced_bound_has_no_spatial_momentum_denominator_at_zero':
            all(not x.subs(q,0).has(sp.zoo,sp.oo,sp.nan) for x in bounds.values()),
    }
    return {'symbols':dict(sigma=sigma,b=b,chi=chi,r=r,q=q,margin=margin,Y=Y),
            'd':d,'K0':K0,'reciprocal_squared_gap':gap,
            'manifest_nonnegative_gap':manifest,'bounds':bounds,'checks':checks,
            'hypotheses':'r=abs(s)>0, sigma=Re(s)>0, finite positive spectral measure; no first moment required',
            'analytic_argument':'Re[s(2B+chi)]>=(2b+chi)sigma and Re[-Schur/s]>=sigma*(K0+chi*q²/r²), from pinned continuum proof'}


def derive_model():
    fresh=candidate.derive_model()
    w,q,chi=fresh['w'],fresh['q'],fresh['chi']
    P=fresh['base']['parameters'];b,M,KT=P['Mb2'],P['M5c'],P['K_T']
    B=sp.Symbol('B_response')
    kernel_coordinate={KT:(B-b)*(q*q-w*w)/M}
    H=fresh['H18'];idx=fresh['index']
    sectors={};checks={};negative={}
    qzero_source=homogeneous.derive_model()
    for axis,orientation,theta in ((1,1,'theta2'),(2,-1,'theta1')):
        names=[f'N{axis}',f'H{axis}3',theta]
        indices=[idx[name] for name in names]
        raw=H.extract(indices,indices)
        block=clean(raw.subs(kernel_coordinate,simultaneous=True))
        data=analyze_sector(block,orientation,w,q,chi,B)
        data['field_order']=names;data['raw_H18_block']=raw
        outside=[j for j in range(18) if j not in indices]
        data['residuals']['coupling_to_all_other_H18_fields']=clean(H.extract(indices,outside))
        source_gauge=fresh['gauges'][f'space_{axis}'].extract(indices,[0])
        data['residuals']['gauge_matches_horizontal_H18_compensation']=clean(source_gauge-data['gauge'])
        # Direct homogeneous calculation has no substitution K_T=(B-b)z/M.
        sh=qzero_source['s'];hi=qzero_source['index'][names[1]]
        direct=clean(raw.extract([1,2],[1,2]).subs({w:sp.I*sh,q:0},simultaneous=True))
        expected=sp.diag(qzero_source['H_q_zero'][hi,hi],-chi*sh*sh)
        data['residuals']['direct_homogeneous_source_comparison']=clean(direct-expected)
        data['direct_q_zero_raw']=direct
        data['checks']={k:zero(v) for k,v in data['residuals'].items()}
        sectors[str(axis)]=data
        checks.update({f'vector_{axis}_{k}':v for k,v in data['checks'].items()})
        bad_force=sp.Matrix([1,0,0])
        negative[f'vector_{axis}_incompatible_force']=(sp.Matrix([-w,q,orientation*q/2]).T*bad_force)[0]
        negative[f'vector_{axis}_omit_horizontal_compensation']=clean(block*sp.I*sp.Matrix([-w,q,0]))
    bounds=derive_bounds();checks.update({'bound_'+k:v for k,v in bounds['checks'].items()})
    direct_added=fresh['addition'].subs(q,0)
    checks['all_324_direct_homogeneous_added_entries']=zero(direct_added-sp.diag(sp.zeros(15),chi*w*w*sp.eye(3)))
    checks['all_four_source_gauge_vectors_are_null']=all(zero(H*g) for g in fresh['gauges'].values())
    # A changed mixed matrix entry cannot be hidden by changing the force law.
    changed=sectors['1']['block'].copy();changed[0,2]+=1
    negative['contaminated_Ward_entry']=clean(changed[0,:]-q/w*(changed[1,:]+changed[2,:]/2))
    negative['omit_retained_pivot_q_zero']=clean(sectors['1']['q_zero_retained'].det()-sectors['1']['Schur'].subs(q,0))
    return {'w':w,'q':q,'chi':chi,'b':b,'B':B,'kernel_coordinate':kernel_coordinate,
            'sectors':sectors,'bounds':bounds,'checks':checks,'negative':negative,
            'upstream_H18_recomputed':True,'homogeneous_H15_recomputed':True,
            'kernel_coordinate_domain':'M>0 and z=q²-w²=s²+q² != 0 in Re(s)>0; algebraic coordinate only'}


def serialize(value):
    if isinstance(value,sp.MatrixBase):
        return [[sp.sstr(value[i,j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value,sp.Basic):return sp.sstr(value)
    if isinstance(value,dict):return {str(k):serialize(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serialize(v) for v in value]
    return value


def build_payload():
    sources=load_sources();model=derive_model()
    negative={k:not zero(v) for k,v in model['negative'].items()}
    if not all(model['checks'].values()) or not all(negative.values()):
        failed=[k for k,v in model['checks'].items() if not v]+[k for k,v in negative.items() if not v]
        raise TemporalGaugeError('temporal vector derivation failed: '+','.join(failed))
    out={'schema':SCHEMA,'sources':sources,
         'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST)},
         'checks':model['checks'],'negative_controls':negative,
         'response':serialize({k:model[k] for k in ('kernel_coordinate','kernel_coordinate_domain','sectors')}),
         'bounds':serialize(model['bounds']),
         'scope':{'domain':'Re(s)>0, w=i*s, q>=0, fixed propagation axis and selected finite-energy response',
                  'forcing':'all three rows retained through the exact source Ward condition',
                  'uniformity':'q-independent coefficient bounds at fixed s or compact RHP subsets',
                  'source_recomputation':'fresh H18 from H15 plus literal projected C density; independent direct homogeneous H15',
                  'analytic_proof':'pinned finite-measure continuum lemma; exact algebra is not a sampled spectral proof'},
         'decision':{'regular_temporal_vector_chart_for_selected_H18':True,
                     'compatible_forced_response_has_q_uniform_coefficients_at_fixed_RHP_s':True,
                     'direct_q_zero_pivot_and_chart_determinant_preserved':True,
                     'old_H_zero_chart_formula_modified':False,
                     'uniform_bound_as_s_approaches_zero_or_imaginary_axis':False,
                     'global_Sobolev_gauge_reconstruction_proved':False,
                     'all_forces_without_Ward_compatibility_solvable':False,
                     'new_action_adopted':False,'chi_value_selected':False,
                     'BF_boundary_domain_and_embeddings_completed':False,
                     'full_N4':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False}}
    out['calculation_digest']=digest(out)
    return out


def validate_payload(payload):
    if type(payload) is not dict:raise TemporalGaugeError('receipt must be object')
    body={k:v for k,v in payload.items() if k!='calculation_digest'}
    try:valid=payload.get('calculation_digest')==digest(body)
    except (TypeError,ValueError) as exc:raise TemporalGaugeError('invalid receipt value') from exc
    if not valid:raise TemporalGaugeError('receipt calculation digest mismatch')
    expected=build_payload()
    if payload!=expected:raise TemporalGaugeError('receipt differs from fresh source-bound derivation')
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
