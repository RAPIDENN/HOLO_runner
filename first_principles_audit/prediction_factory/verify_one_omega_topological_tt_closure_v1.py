#!/usr/bin/env python3
"""Project both TT polarizations through pinned bulk rows and brane columns.

This cross-check consumes the explicit linear equations of the original bulk
and the previously independently reconstructed brane Hessian. Their TT
projections are compared with the independently derived restricted TT operator.
It does not rederive every general bulk equation or moving-wall variation.
The candidate transfer is a vacuum, quadratic statement: no scalar block,
BF edge domain, nonlinear constraint or complete mode-admissibility certificate
is inherited from the old solid action.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

import sympy as sp

if __package__:
    from . import verify_one_omega_topological_tt_compatibility_v1 as compatibility
else:
    import verify_one_omega_topological_tt_compatibility_v1 as compatibility

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
BULK=HERE/'artifacts/one_omega_topological_tt_closure_bulk_snapshot_v1.json'
BRANE=HERE/'artifacts/one_omega_brane_hessian_v1_source_snapshot.json'
BASE=HERE/'artifacts/one_omega_topological_tt_compatibility_v1.json'
OUTPUT=HERE/'artifacts/one_omega_topological_tt_closure_v1.json'
TEST=HERE/'test_one_omega_topological_tt_closure_v1.py'
BULK_SHA='ea8b45c968056dda63fb4394d4395669b69d913adf94625b60a1804dc649777a'
BRANE_SHA='5d1be4316075435832085b4af8b1fe3f35d839b6a319a98641a55193c3036b69'
BASE_SHA='e579cc886c355ba78d54d7c88550ac350c935a062733f14f60a1e588190f9208'
SCHEMA='holo.one-omega-topological-tt-closure.v1'
canonical_digest=compatibility.canonical_digest


class TTClosureError(ValueError):
    pass


SYMBOLS={name:sp.Symbol(name,positive=True) for name in ('G','M5c','k_inf','Mb2','xi','mu_X','v','Z5','q_mom')}
SYMBOLS.update({name:sp.Symbol(name,real=True) for name in ('w','s','W_freq','h','hr','hrr','A_value')})
SYMBOLS['Omega_value']=sp.Symbol('Omega_value',positive=True)
PROFILE_NAMES=('H00','H01','H02','H03','H11','H12','H13','H22','H23','H33','Wm','X0')
FUNCTIONS={name:sp.Function(name) for name in ('A','Omega',*PROFILE_NAMES)}
BULK_ROWS=('00','01','02','03','04','11','12','13','14','22','23','24','33','34','44','Omega','chi0')


def parse_expression(text, *, brane=False):
    """Parse only the small arithmetic/derivative grammar of these snapshots.

    Never invoke Python eval, sympify or parse_expr on a source string. Tuples
    are accepted only for (w,1|2) derivative specifications.
    """
    if not isinstance(text,str) or len(text)>100000:
        raise TTClosureError('invalid or oversized symbolic expression')
    try: tree=ast.parse(text,mode='eval')
    except (SyntaxError,RecursionError) as exc: raise TTClosureError('invalid expression syntax') from exc
    if sum(1 for _ in ast.walk(tree))>15000:
        raise TTClosureError('expression exceeds node budget')
    names=dict(SYMBOLS);names['I']=sp.I
    if brane:
        names['w']=SYMBOLS['W_freq'];names['q']=SYMBOLS['q_mom']
    def read(node,depth=0):
        if depth>100:raise TTClosureError('expression exceeds depth budget')
        rec=lambda n:read(n,depth+1)
        if isinstance(node,ast.Constant) and type(node.value) is int:
            if abs(node.value)>10**9:raise TTClosureError('integer out of domain')
            return sp.Integer(node.value)
        if isinstance(node,ast.Name) and node.id in names:return names[node.id]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            value=rec(node.operand);return value if isinstance(node.op,ast.UAdd) else -value
        if isinstance(node,ast.BinOp):
            left,right=rec(node.left),rec(node.right)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):
                if right==0:raise TTClosureError('zero denominator')
                return left/right
            if isinstance(node.op,ast.Pow):
                if not isinstance(right,sp.Rational) or abs(right.p)>32 or right.q>16:
                    raise TTClosureError('power outside declared arithmetic domain')
                return left**right
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and not node.keywords:
            name=node.func.id
            if name in FUNCTIONS and not brane and len(node.args)==1:
                arg=rec(node.args[0])
                if arg!=SYMBOLS['w']:raise TTClosureError('profile has wrong coordinate')
                return FUNCTIONS[name](arg)
            if name in ('exp','sqrt') and len(node.args)==1:
                return {'exp':sp.exp,'sqrt':sp.sqrt}[name](rec(node.args[0]))
            if name=='Derivative' and not brane and len(node.args)==2:
                field=rec(node.args[0]);spec=node.args[1];order=1
                if isinstance(spec,ast.Tuple) and len(spec.elts)==2:
                    coordinate=rec(spec.elts[0]);order=rec(spec.elts[1])
                else:coordinate=rec(spec)
                if coordinate!=SYMBOLS['w'] or order not in (1,2):raise TTClosureError('derivative outside declared jet domain')
                if field not in [fn(SYMBOLS['w']) for fn in FUNCTIONS.values()]:raise TTClosureError('derivative must act on one declared profile')
                return sp.diff(field,coordinate,order)
        raise TTClosureError('expression uses an undeclared construct')
    result=read(tree.body)
    if result.has(sp.zoo,sp.nan,sp.oo,-sp.oo,sp.Float):raise TTClosureError('non-finite or inexact expression')
    return result


def _project(expression,polarization):
    w=SYMBOLS['w'];h,hr,hrr=(SYMBOLS[k] for k in ('h','hr','hrr'))
    coefficients={'H12':1} if polarization=='cross' else {'H11':1,'H22':-1}
    substitutions={}
    for name in PROFILE_NAMES:
        function=FUNCTIONS[name](w);factor=coefficients.get(name,0)
        substitutions.update({function:factor*h,sp.diff(function,w):factor*hr,sp.diff(function,w,2):factor*hrr})
    substitutions.update({FUNCTIONS['A'](w):SYMBOLS['A_value'],FUNCTIONS['Omega'](w):SYMBOLS['Omega_value']})
    result=expression.xreplace(substitutions)
    if result.has(sp.Derivative):raise TTClosureError('unresolved background derivative in projected row')
    return sp.simplify(result)


def check_bulk_rows(doc):
    try: rows=doc['helicity_odes']
    except (KeyError,TypeError) as exc:raise TTClosureError('missing bulk ODEs') from exc
    if not all(key in rows for key in BULK_ROWS):raise TTClosureError('incomplete bulk row set')
    parsed={key:parse_expression(rows[key]) for key in BULK_ROWS}
    G,M,k,o,A,side,freq,q,h,hr,hrr=(SYMBOLS[k] for k in ('G','M5c','k_inf','Omega_value','A_value','s','W_freq','q_mom','h','hr','hrr'))
    reference=-M*sp.exp(2*A)*(hrr-4*k*side*sp.exp(-G*o**2/(6*M))*hr+(freq**2-q**2)*sp.exp(-2*A)*h)/2
    results={}
    for polarization in ('cross','plus'):
        projected={key:_project(value,polarization) for key,value in parsed.items()}
        expected={key:sp.S.Zero for key in BULK_ROWS}
        if polarization=='cross':expected['12']=reference
        else:expected['11'],expected['22']=reference,-reference
        residuals={key:sp.simplify(projected[key]-expected[key]) for key in BULK_ROWS}
        nulls={key:sp.simplify(value.subs({hr:0,hrr:0,freq:q})) for key,value in projected.items()}
        results[polarization]={'restricted_rows':projected,'expected_rows':expected,'residuals':residuals,'null_residuals':nulls}
    return {'polarization_results':results,'reference':reference,
            'checks':{'all_projected_bulk_rows_match_independent_TT_operator':all(v==0 for p in results.values() for v in p['residuals'].values()),
                      'both_null_modes_satisfy_all_seventeen_bulk_rows':all(v==0 for p in results.values() for v in p['null_residuals'].values())}}


def check_brane_columns(doc):
    try:
        block=doc['extended_hessian'];names=block['helicity_field_order'];matrix=block['symbolic_matrix_helicity_basis']
    except (KeyError,TypeError) as exc:raise TTClosureError('missing brane matrix') from exc
    expected_names=['n','N1','N2','N3','Hs','H12','H13','Hd','H23','H33','tau','pi1','pi2','pi3','omega','vphi1','vphi2','vphi3']
    if names!=expected_names or len(matrix)!=18 or any(len(row)!=18 for row in matrix):raise TTClosureError('brane basis or matrix shape changed')
    G,M,k,Mb,xi,mu,v,freq,q=(SYMBOLS[n] for n in ('G','M5c','k_inf','Mb2','xi','mu_X','v','W_freq','q_mom'))
    W0=3*M*k*sp.exp(-G/(6*M))
    reference=2*W0+Mb*(freq**2-xi*q**2)/2-mu*v**4
    results={}
    for name in ('Hd','H12'):
        column=[parse_expression(matrix[i][names.index(name)],brane=True) for i in range(18)]
        residuals={row:sp.simplify(column[i]-(reference if row==name else 0)) for i,row in enumerate(names)}
        results[name]={'residuals':residuals,'diagonal':column[names.index(name)],
                       'candidate_after_removing_solid_and_balancing_bulk_tension':sp.simplify(column[names.index(name)]+mu*v**4-2*W0)}
    return {'column_results':results,'checks':{'both_complete_brane_columns_match_TT_reference':all(v==0 for r in results.values() for v in r['residuals'].values())}}


def _load(path,digest):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=digest:raise TTClosureError('snapshot hash mismatch: '+Path(path).name)
    return compatibility.source_oracle._read_json(raw)


def _serialize(value):
    if isinstance(value,sp.Basic):return str(value)
    if isinstance(value,dict):return {k:_serialize(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [_serialize(v) for v in value]
    return value


def build_payload():
    base=_load(BASE,BASE_SHA);compatibility.validate_payload(base)
    bulk=check_bulk_rows(_load(BULK,BULK_SHA));brane=check_brane_columns(_load(BRANE,BRANE_SHA))
    checks={**bulk['checks'],**brane['checks']}
    if not all(checks.values()):raise TTClosureError('TT row projection mismatch')
    payload={'schema':SCHEMA,'sources':{'bulk_snapshot':BULK_SHA,'brane_snapshot':BRANE_SHA,'restricted_TT_receipt':BASE_SHA},
             'bulk':_serialize(bulk),'brane':_serialize(brane),'checks':checks,
             'transport':{'shared_background':'W,U,GHY,wall0 unchanged; candidate source and differences verified by base receipt',
                'candidate_changes':'remove S_X and its pi_X variables; lambda_K changes; D_A replaces d; iota replaces the X-derived frame; BF added',
                'quadratic_mixed_TT_rows':'TT first variations of P, phi, acceleration, K trace and Rcal vanish. Their vacuum material/Robin/BF and lambda-change terms cannot add a mixed TT row. The removed solid changes the TT diagonal and has no other TT column entry in the displayed matrix.',
                'frame_and_connection':'same varying orthonormal frame on both sides; connection trace independent of Levi-Civita; A=B=phi=0 is admitted in this trivialization',
                'historical_source_flags_inherited':False},
             'decision':{'both_polarizations_checked_in_displayed_bulk_and_brane_rows':True,
                'independent_derivation_of_every_bulk_row':False,'moving_embedding_equations_rederived':False,
                'complete_candidate_linearization_certified':False,'physical_mode_admissibility':False,
                'BF_edge_modes_eliminated':False,'full_N7':False,'full_P4':False,'B4':False,'B5':False},
             'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),TEST,Path(compatibility.__file__)]}}
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(doc):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:raise TTClosureError('schema mismatch')
    if doc.get('calculation_digest')!=canonical_digest({k:v for k,v in doc.items() if k!='calculation_digest'}):raise TTClosureError('digest mismatch')
    if doc!=build_payload():raise TTClosureError('receipt differs from fresh TT projections')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',nargs='?',const=OUTPUT,type=Path)
    mode.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args()
    if args.write:
        doc=build_payload()
        with args.write.open('x') as f:json.dump(doc,f,sort_keys=True,indent=2);f.write('\n')
    else:
        doc=compatibility.source_oracle._read_json(args.verify.read_bytes());validate_payload(doc)
    print(json.dumps({'checks':doc['checks'],'calculation_digest':doc['calculation_digest']}))


if __name__=='__main__':main()
