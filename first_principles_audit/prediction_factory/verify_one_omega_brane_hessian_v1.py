#!/usr/bin/env python3
"""Independent quadratic brane-action and differential-adjoint Hessian audit.

Reconstruct the flat-background quadratic action using K1, a1, strain, velocity
and the spatial Fierz-Pauli density. Densities are equivalent modulo total
brane derivatives for compact-support variations. Differentiate their jet
polynomial using the formal adjoint, not the producer's plane-wave method.

The scalar-curvature term is xi*((n-d_t tau)*R1+FP3). Its clock term cancels the
clock term in K1^2-tr(K1)^2 at the Einstein-Hilbert coefficient point. This is a
second derivation of the quadratic brane form, not a variation of bulk/GHY or
moving embeddings. The full brane Hessian includes nonzero background
wall tadpoles; only the separately stated tadpole-free form has the checked
linear gauge null vectors. No nonlinear Ward identity is claimed.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp

try:
    from . import one_omega_brane_hessian_algebra_v1 as algebra
    from . import verify_one_omega_scalar_interface_reparam_v1 as charter_binding
except ImportError:
    import one_omega_brane_hessian_algebra_v1 as algebra
    import verify_one_omega_scalar_interface_reparam_v1 as charter_binding

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE = HERE / 'artifacts' / 'one_omega_brane_hessian_v1_source_snapshot.json'
OUTPUT = HERE / 'artifacts' / 'one_omega_brane_hessian_v1.json'
TEST = HERE / 'test_one_omega_brane_hessian_v1.py'
EXPECTED_SOURCE_SHA256 = '5d1be4316075435832085b4af8b1fe3f35d839b6a319a98641a55193c3036b69'
SCHEMA = 'holo.one-omega-brane-hessian-audit.v1'
SOURCE_DIGEST_KEYS = ('schema', 'route_id', 'stage', 'upstream_bindings', 'background',
                     'tadpoles', 'expected_tadpoles', 'quadratic_lagrangian',
                     'extended_hessian', 'checks', 'decision', 'classification', 'evidence_boundary')
SOURCE_NAMES = ('n','N1','N2','N3','Hs','H12','H13','Hd','H23','H33',
                'tau','pi1','pi2','pi3','omega','vphi1','vphi2','vphi3')
SOURCE_GROUPS = {
    'scalar': ['n','N3','Hs','H33','tau','pi3','omega','vphi3'],
    'vector': ['N1','N2','H13','H23','pi1','pi2','vphi1','vphi2'],
    'tensor': ['Hd','H12'],
}
PARAMETER_MAP = dict(M5c='M5_cubed', k_inf='k_infinity', G='compensator_metric_G',
                     beta='brane_beta', Mb2='brane_Mb_squared', lambda_K='lambda_K',
                     xi='xi', eta='eta', B4bar='B4_bar', kappa_hat='Robin_kappa_hat',
                     y='Robin_y', v='solid_v', rho_X='solid_rho', mu_X='solid_mu',
                     lambda_X='solid_lambda')


class HessianAuditError(ValueError):
    """Source binding, symbolic interpretation or independent comparison failed."""


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                      allow_nan=False).encode()).hexdigest()


def parse_expression(text: str, ctx: dict) -> sp.Expr:
    """Interpret a small arithmetic AST; never evaluate Python from an artifact.

    The upstream printer names both a coordinate and a coupling `y`. Field-call
    and Derivative arguments use the coordinate; isolated `y` uses the coupling.
    This convention is explicit and tested instead of silently merging symbols.
    """
    if not isinstance(text, str) or len(text) > 500_000:
        raise HessianAuditError('expression must be a bounded string')
    coordinates = dict(zip(('t','x','y','z'), ctx['coords']))
    field_map = dict(zip(ctx['field_names'], ctx['fields']))
    names = {**coordinates, **ctx['parameters'], 'q': ctx['q'], 'w': ctx['w'], 'I': sp.I}
    try:
        tree = ast.parse(text, mode='eval').body
    except (SyntaxError, RecursionError) as exc:
        raise HessianAuditError('invalid expression syntax') from exc

    def coordinate(node: ast.AST) -> sp.Symbol:
        if not isinstance(node, ast.Name) or node.id not in coordinates:
            raise HessianAuditError('unknown derivative coordinate')
        return coordinates[node.id]

    def walk(node: ast.AST) -> sp.Expr:
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return sp.Integer(node.value)
        if isinstance(node, ast.Constant) and type(node.value) is float and math.isfinite(node.value):
            return sp.Float(ast.get_source_segment(text, node), 18)
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd,ast.USub)):
            value = walk(node.operand)
            return value if isinstance(node.op,ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Add): return left+right
            if isinstance(node.op, ast.Sub): return left-right
            if isinstance(node.op, ast.Mult): return left*right
            if isinstance(node.op, ast.Div): return left/right
            if isinstance(node.op, ast.Pow): return left**right
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            name = node.func.id
            if name in field_map:
                if len(node.args) != 4 or tuple(coordinate(a) for a in node.args) != ctx['coords']:
                    raise HessianAuditError('field coordinate arguments differ from t,x,y,z')
                return field_map[name]
            if name in ('exp','sqrt') and len(node.args) == 1:
                return getattr(sp,name)(walk(node.args[0]))
            if name == 'Derivative' and len(node.args) >= 2:
                field = walk(node.args[0])
                if field not in ctx['fields']:
                    raise HessianAuditError('only derivatives of known fields are accepted')
                variables = []
                for arg in node.args[1:]:
                    if isinstance(arg,ast.Tuple) and len(arg.elts) == 2:
                        count = arg.elts[1]
                        if not isinstance(count,ast.Constant) or type(count.value) is not int or not 1 <= count.value <= 16:
                            raise HessianAuditError('unsupported derivative order')
                        variables.append((coordinate(arg.elts[0]), count.value))
                    else:
                        variables.append(coordinate(arg))
                return sp.Derivative(field,*variables)
        raise HessianAuditError(f'unsupported expression node: {type(node).__name__}')

    try:
        result = walk(tree)
    except (TypeError, ZeroDivisionError, RecursionError) as exc:
        raise HessianAuditError('invalid symbolic expression') from exc
    if result.has(sp.nan, sp.oo, -sp.oo, sp.zoo):
        raise HessianAuditError('non-finite expression')
    return result


def canonical_quadratic(ctx: dict) -> dict[str, sp.Expr]:
    """Compact independent brane L2, up to integrals of total derivatives."""
    fields = dict(zip(ctx['field_names'],ctx['fields']))
    p = ctx['parameters']
    t, *spatial = ctx['coords']
    n, tau, omega = (fields[name] for name in ('n','tau','omega'))
    N = [fields[f'N{i}'] for i in (1,2,3)]
    phonon = [fields[f'pi{i}'] for i in (1,2,3)]
    triplet = [fields[f'vphi{i}'] for i in (1,2,3)]
    H = sp.Matrix(3,3,lambda i,j:fields[f'H{min(i,j)+1}{max(i,j)+1}'])
    trace = sp.trace(H)
    divH = [sum(sp.diff(H[i,j],spatial[i]) for i in range(3)) for j in range(3)]
    R1 = sum(sp.diff(divH[j],spatial[j])-sp.diff(trace,spatial[j],2) for j in range(3))
    FP3 = -sum(sp.diff(H[i,j],c)**2 for i in range(3) for j in range(3) for c in spatial)/4
    FP3 += sum(sp.diff(trace,c)**2 for c in spatial)/4
    FP3 += sum(d*d for d in divH)/2
    FP3 -= sum(divH[j]*sp.diff(trace,spatial[j]) for j in range(3))/2
    K1 = sp.Matrix(3,3,lambda i,j:sp.diff(H[i,j],t)/2-
                   (sp.diff(N[j],spatial[i])+sp.diff(N[i],spatial[j]))/2-
                   sp.diff(tau,spatial[i],spatial[j]))
    clock_lapse = n-sp.diff(tau,t)
    a1 = [sp.diff(clock_lapse,c) for c in spatial]
    fol = p['Mb2']/2*(sum(e*e for e in K1)-p['lambda_K']*sp.trace(K1)**2+
                       p['eta']*sum(a*a for a in a1)+p['xi']*(clock_lapse*R1+FP3)-
                       p['B4bar']*R1**2/(16*p['k_inf']**2))
    V1 = [sp.diff(phonon[i],t)-p['v']*(N[i]+sp.diff(tau,spatial[i])) for i in range(3)]
    C1 = sp.Matrix(3,3,lambda i,j:p['v']*(sp.diff(phonon[i],spatial[j])+
                         sp.diff(phonon[j],spatial[i]))-p['v']**2*H[i,j])
    solid = (p['rho_X']*sum(e*e for e in V1)/2-p['mu_X']*sum(e*e for e in C1)/4-
             p['lambda_X']*sp.trace(C1)**2/8)
    robin = -p['kappa_hat']*sum((triplet[i]-p['y']*a1[i])**2 for i in range(3))/2
    W = 3*p['M5c']*p['k_inf']*sp.exp(-p['G']/(6*p['M5c']))
    Wprime = -p['G']*W/(3*p['M5c'])
    Wsecond = W*(p['G']**2/(9*p['M5c']**2)-p['G']/(3*p['M5c']))
    volume1 = n+trace/2
    volume2 = n*trace/2+(trace**2-2*sum(e*e for e in H))/8
    tadpole = -2*W*volume2-2*Wprime*omega*volume1
    mass = -(Wsecond+p['beta']/2)*omega**2
    wall = tadpole+mass
    return dict(total=sp.expand(wall+fol+solid+robin), wall=sp.expand(wall),
                tadpole=sp.expand(tadpole), foliation=sp.expand(fol), solid=sp.expand(solid),
                robin=sp.expand(robin), gauge_free=sp.expand(mass+fol+solid+robin))


def source_basis(ctx: dict) -> tuple[sp.Matrix, tuple, dict]:
    old = {name:i for i,name in enumerate(ctx['field_names'])}
    new = {name:i for i,name in enumerate(SOURCE_NAMES)}
    S = sp.zeros(18)
    for name,i in old.items():
        if name == 'H11':
            S[i,new['Hs']] = sp.Rational(1,2); S[i,new['Hd']] = 1
        elif name == 'H22':
            S[i,new['Hs']] = sp.Rational(1,2); S[i,new['Hd']] = -1
        else:
            S[i,new[name]] = 1
    return S, SOURCE_NAMES, {key:list(value) for key,value in SOURCE_GROUPS.items()}


def compare_symbolic_matrix(doc: dict, H: sp.MatrixBase, ctx: dict) -> dict:
    matrix = doc['extended_hessian']
    if (matrix.get('fields') != list(ctx['field_names']) or
            matrix.get('helicity_field_order') != list(SOURCE_NAMES) or
            matrix.get('helicity_sets') != SOURCE_GROUPS):
        raise HessianAuditError('source matrix basis or field inventory differs')
    rows = matrix.get('symbolic_matrix_helicity_basis')
    if not isinstance(rows,list) or len(rows)!=18 or any(not isinstance(row,list) or len(row)!=18 for row in rows):
        raise HessianAuditError('source symbolic matrix is not 18 by 18')
    S, _, _ = source_basis(ctx)
    expected = S.T*H*S
    failures = []
    for i in range(18):
        for j in range(18):
            value = parse_expression(rows[i][j],ctx)
            if value.has(sp.Float) or sp.simplify(value-expected[i,j]) != 0:
                failures.append((i,j))
    if failures:
        raise HessianAuditError(f'symbolic Hessian disagrees at {len(failures)} entries: {failures[:12]}')
    return {'symbolic_entries_compared':324, 'symbolic_mismatches':0}


def load_source(path: Path = SOURCE) -> dict:
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise HessianAuditError('source byte hash differs from reviewed corrected receipt')
    doc = charter_binding._read_json(raw)
    if canonical_digest({key:doc[key] for key in SOURCE_DIGEST_KEYS}) != doc.get('calculation_digest'):
        raise HessianAuditError('source mathematical digest mismatch')
    charter_binding.load_charter()
    upstream = doc['upstream_bindings']['one_omega_action_charter_gate.json']
    if (upstream['sha256'] != charter_binding.CHARTER_BYTES_SHA256 or
            upstream['action_charter_digest'] != charter_binding.ACTION_SHA256 or
            upstream['calculation_digest'] != charter_binding.CALCULATION_SHA256):
        raise HessianAuditError('source is not bound to the selected action charter')
    return doc


def first_order_foliation(ctx: dict) -> dict:
    """Derive the nonzero linear density, its current and its Euler derivatives."""
    fields=dict(zip(ctx['field_names'],ctx['fields']))
    spatial=ctx['coords'][1:]
    H=sp.Matrix(3,3,lambda i,j:fields[f'H{min(i,j)+1}{max(i,j)+1}'])
    trace=sp.trace(H)
    coefficient=ctx['parameters']['Mb2']*ctx['parameters']['xi']/2
    density=coefficient*(sum(sp.diff(H[i,j],spatial[i],spatial[j])
                            for i in range(3) for j in range(3))-
                         sum(sp.diff(trace,c,2) for c in spatial))
    current=[coefficient*(sum(sp.diff(H[i,j],spatial[j]) for j in range(3))-
                          sp.diff(trace,spatial[i])) for i in range(3)]
    divergence=sum(sp.diff(current[i],spatial[i]) for i in range(3))
    residual=sp.simplify(density-divergence)
    eulers={}
    for name,field in zip(ctx['field_names'],ctx['fields']):
        value=sp.diff(density,field)
        for jet in density.atoms(sp.Derivative):
            if jet.expr==field:
                term=sp.diff(density,jet)
                value+=(-1)**len(jet.variables)*sp.diff(term,*jet.variables)
        eulers[name]=sp.sstr(sp.simplify(value))
    return {'density':sp.sstr(sp.expand(density)),
            'spatial_current':[sp.sstr(sp.expand(value)) for value in current],
            'density_minus_divergence':sp.sstr(residual),
            'density_is_identically_zero':sp.expand(density)==0,
            'Euler_derivatives':eulers,
            'integrated_first_variation_zero_for_compact_support':
                residual==0 and all(value=='0' for value in eulers.values())}


def _sparse(matrix: sp.MatrixBase) -> dict:
    entries=[]
    for i in range(matrix.rows):
        for j in range(matrix.cols):
            value=sp.simplify(matrix[i,j])
            if value != 0: entries.append([i,j,sp.sstr(value)])
    return {'shape':[matrix.rows,matrix.cols], 'nonzero_entries':entries}


def _gauge_vectors(ctx: dict) -> dict[str,sp.Matrix]:
    idx={name:i for i,name in enumerate(ctx['field_names'])}
    q,w,v=ctx['q'],ctx['w'],ctx['parameters']['v']
    temporal=sp.zeros(18,1)
    temporal[idx['tau']]=1; temporal[idx['n']]=-sp.I*w; temporal[idx['N3']]=-sp.I*q
    vectors={'time_reparametrization':temporal}
    for a in (1,2,3):
        value=sp.zeros(18,1)
        value[idx[f'pi{a}']]=v; value[idx[f'N{a}']]=-sp.I*w
        value[idx['H33' if a==3 else f'H{a}3']]=(2 if a==3 else 1)*sp.I*q
        vectors[f'spatial_{a}']=value
    return vectors


def build_payload(source_path: Path = SOURCE) -> dict:
    source=load_source(source_path)
    ctx=algebra.symbols_context()
    blocks=canonical_quadratic(ctx)
    H=algebra.momentum_hessian(blocks['total'],ctx)
    comparison=compare_symbolic_matrix(source,H,ctx)
    S,names,groups=algebra.helicity_basis(ctx)
    linear=first_order_foliation(ctx)
    Hnorm=(S.T*H*S).applyfunc(sp.simplify)
    checks={'source_symbolic_matrix_matches_compact_action':comparison['symbolic_mismatches']==0,
            'hessian_hermitian': all(sp.simplify(e)==0 for e in H-H.conjugate().T),
            'mode_basis_invertible':sp.simplify(S.det())!=0,
            'linear_foliation_density_is_nonzero_divergence':not linear['density_is_identically_zero'] and linear['density_minus_divergence']=='0',
            'linear_foliation_Euler_derivatives_vanish':linear['integrated_first_variation_zero_for_compact_support']}
    keys=list(groups)
    for ai,a in enumerate(keys):
        for b in keys[ai+1:]:
            checks[f'{a}_{b}_blocks_decouple']=all(Hnorm[i,j]==0 for i in groups[a] for j in groups[b])
    t0,t1=groups['tensor']
    checks['two_tensor_polarizations_degenerate']=sp.simplify(Hnorm[t0,t0]-Hnorm[t1,t1])==0
    checks['tensor_cross_entry_zero']=Hnorm[t0,t1]==0
    Hfree=algebra.momentum_hessian(blocks['gauge_free'],ctx)
    gauge_residuals={}
    for name,vector in _gauge_vectors(ctx).items():
        r=(Hfree*vector).applyfunc(sp.simplify)
        checks[f'linear_gauge_free_null_{name}']=all(e==0 for e in r)
        gauge_residuals[name]=_sparse(H*vector)
    if not all(checks.values()):
        raise HessianAuditError(f'independent checks failed: {[k for k,v in checks.items() if not v]}')
    false_keys=('bulk_variation_pass','moving_embedding_variation_pass','GHY_variation_pass',
                'nonlinear_Ward_identity_pass','N2_CONSTRAINTS_pass','N3_CHARACTERISTICS_pass',
                'N4_JUNCTION_BENDING_pass','C4_HESSIAN_pass','P4_full_same_action_pass','B4_pass','B5_pass')
    decision={key:False for key in false_keys}
    decision['quadratic_brane_hessian_independently_reproduced_pass']=True
    files=[Path(__file__),HERE/'one_omega_brane_hessian_algebra_v1.py',TEST,
           HERE/'verify_one_omega_scalar_interface_reparam_v1.py']
    payload={
        'schema':SCHEMA,
        'source':{'path':str(SOURCE.relative_to(REPO)),'sha256':EXPECTED_SOURCE_SHA256,
                  'action_charter_sha256':charter_binding.ACTION_SHA256,
                  'calculation_digest':source['calculation_digest'],
                  'producer_generator_sha256':source['provenance']['generator_sha256'],
                  'producer_checks_not_inherited':[key for key,value in source['checks'].items() if value is not True],
                  'snapshot_reason':'immutable reviewed matrix while the producer corrects its linear-density versus integrated-variation check'},
        'scope':{'background':'flat brane, T=t, X=v*x, Omega=1, triplet=0',
                 'momentum':'q along z; w arbitrary, both symbolic',
                 'derivation':'compact quadratic action modulo total derivatives plus formal-adjoint jet Hessian',
                 'boundary_of_brane':'compact-support variations; no boundary of the brane',
                 'producer_plane_wave_function_imported':False,
                 'full_nonlinear_action_variation_claimed':False,
                 'bulk_GHY_and_moving_embeddings_included':False,
                 'linear_gauge_null_scope':'tadpole-free brane form only; full form residuals retained',
                 'translation':'manual analytic quadratic expansion, cross-checked with independent covariant producer'},
        'quadratic_action':{key:sp.sstr(value) for key,value in blocks.items()},
        'comparison':comparison, 'checks':checks, 'first_order_foliation':linear,
        'old_field_order':list(ctx['field_names']), 'normalized_mode_order':list(names),
        'normalized_mode_groups':{key:[names[i] for i in value] for key,value in groups.items()},
        'normalization':'Frobenius metric norm: H11=(Htrace+Hplus)/sqrt2, H22=(Htrace-Hplus)/sqrt2, H12=Hcross/sqrt2, H13=Hxz/sqrt2, H23=Hyz/sqrt2',
        'basis_old_from_normalized':_sparse(S),
        'hessian_original':_sparse(H),'hessian_normalized':_sparse(Hnorm),
        'full_hessian_linear_gauge_residuals':gauge_residuals,
        'decision':decision,
        'provenance':{'sympy':sp.__version__, 'files':[
            {'path':str(path.resolve().relative_to(REPO)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]},
    }
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(payload: dict, source_path: Path = SOURCE) -> None:
    if not isinstance(payload, dict):
        raise HessianAuditError('audit receipt must be a dictionary')
    core={key:value for key,value in payload.items() if key!='calculation_digest'}
    if canonical_digest(core)!=payload.get('calculation_digest'):
        raise HessianAuditError('audit receipt digest mismatch')
    expected=build_payload(source_path)
    if canonical_digest(payload)!=canonical_digest(expected):
        raise HessianAuditError('audit receipt differs from full independent recomputation')


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--write',nargs='?',const=str(OUTPUT),type=Path)
    group.add_argument('--verify',type=Path)
    args=parser.parse_args()
    if args.verify:
        payload=charter_binding._read_json(args.verify.read_bytes());validate_payload(payload)
    else:
        payload=build_payload()
        if args.write:
            with args.write.open('x',encoding='utf-8') as stream:
                stream.write(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'schema':SCHEMA,'comparison':payload['comparison'],
                      'checks_passed':sum(payload['checks'].values()),
                      'calculation_digest':payload['calculation_digest'],
                      'decision':payload['decision']},sort_keys=True))


if __name__=='__main__':
    main()
