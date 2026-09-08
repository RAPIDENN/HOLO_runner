"""Off-shell horizontal diffeomorphism Ward identity for an unadopted term."""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent
PROOF=HERE/'one_omega_connection_horizontal_ward_lemma_v1.md'
TEST=HERE/'test_one_omega_connection_horizontal_ward_v1.py'
SOURCE=HERE/'artifacts/one_omega_connection_current_covariant_variation_v1.json'
OUTPUT=HERE/'artifacts/one_omega_connection_horizontal_ward_v1.json'
PROOF_SHA='6766dcacb59d9104aad83ce941ddef3d9c55c70d36339790440594487c31d14e'
SOURCE_SHA='664631af95ba89a0dadbf441d3ead9bd8c19f4ea8a9af53d377fc9b6f038348f'
SCHEMA='holo.one-omega-connection-horizontal-ward.v1'


class HorizontalWardError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def anti(prefix):
    s={(a,b):sp.Symbol(f'{prefix}_{a}{b}',real=True) for a in range(3) for b in range(a+1,3)}
    return sp.Matrix(3,3,lambda a,b:0 if a==b else (1 if a<b else -1)*s[min(a,b),max(a,b)])


def inner(A,B):
    return sum(A[a,b]*B[a,b] for a in range(3) for b in range(3))/2


def clean(value):
    return value.applyfunc(sp.cancel) if isinstance(value,sp.MatrixBase) else sp.cancel(value)


def expand(value):
    return value.applyfunc(sp.expand) if isinstance(value,sp.MatrixBase) else sp.expand(value)


def zero(value):
    if isinstance(value,sp.MatrixBase): return all(v==0 for v in value)
    if isinstance(value,(list,tuple)): return all(zero(v) for v in value)
    return value==0


def transport_model():
    g=sp.diag(-4,9,1,1);gi=g.inv()
    u=sp.Matrix([sp.Rational(5,8),sp.Rational(1,4),0,0])
    e=sp.Matrix([[sp.Rational(3,8),0,0],[sp.Rational(5,12),0,0],[0,1,0],[0,0,1]])
    xi=sp.Matrix(sp.symbols('xi0:4',real=True))
    dxi=sp.Matrix(4,4,lambda mu,nu:sp.Symbol(f'nabla{mu}_xi{nu}',real=True))
    omega=[anti(f'omega{mu}') for mu in range(4)]
    kappa=sp.Matrix(4,3,lambda mu,a:sp.Symbol(f'kappa{mu}_{a}',real=True))
    dframe=[e*omega[mu]+u*kappa.row(mu) for mu in range(4)]
    dnormal=[e*kappa.row(mu).T for mu in range(4)]
    h=dxi*g+g*dxi.T
    du_cov=sum((xi[mu]*g*dnormal[mu] for mu in range(4)),sp.zeros(4,1))+dxi*g*u
    beta=e.T*(du_cov-h*u/2)
    horizontal=-gi*h*e/2+u*beta.T
    natural=sum((xi[mu]*dframe[mu] for mu in range(4)),sp.zeros(4,3))-dxi.T*e
    sigma=expand(e.T*(dxi*g-g*dxi.T)*e/2)
    rho=expand(e.T*g*(natural-horizontal))
    rho_reference=sum((xi[mu]*omega[mu] for mu in range(4)),sp.zeros(3))+sigma
    A=[anti(f'A{mu}') for mu in range(4)]
    dA=[[anti(f'd{nu}A{mu}') for mu in range(4)] for nu in range(4)]
    drho=[anti(f'drho{mu}') for mu in range(4)]
    contraction=sum((xi[nu]*A[nu] for nu in range(4)),sp.zeros(3))
    C=[A[mu]-omega[mu] for mu in range(4)]
    Lambda=contraction-rho
    cartan=[]; horizontal_A=[]; horizontal_reference=[]
    for mu in range(4):
        lie=sum((xi[nu]*dA[nu][mu]+dxi[mu,nu]*A[nu] for nu in range(4)),sp.zeros(3))
        iF=sum((xi[nu]*(dA[nu][mu]-dA[mu][nu]+A[nu]*A[mu]-A[mu]*A[nu])
                for nu in range(4)),sp.zeros(3))
        derivative_contraction=sum((dxi[mu,nu]*A[nu]+xi[nu]*dA[mu][nu] for nu in range(4)),sp.zeros(3))
        D_contraction=derivative_contraction+A[mu]*contraction-contraction*A[mu]
        cartan.append(expand(lie-iF-D_contraction))
        horizontal_A.append(expand(lie-drho[mu]-A[mu]*rho+rho*A[mu]))
        D_Lambda=derivative_contraction-drho[mu]+A[mu]*Lambda-Lambda*A[mu]
        horizontal_reference.append(expand(iF+D_Lambda))
    G=anti('G');GH=e*G*e.T
    G_sigma=inner(G,sigma)
    spin_gradient=sum(GH[mu,nu]*(dxi*g)[mu,nu] for mu in range(4) for nu in range(4))/2
    T=[sp.Matrix(3,3,lambda j,k:sp.LeviCivita(i,j,k)) for i in range(3)]
    q,amplitude=sp.symbols('q xi_transverse',real=True)
    phase_colors=[]
    for direction in (1,2):
        grad=sp.zeros(4);grad[3,direction]=sp.I*q*amplitude
        ef=sp.Matrix([[0,0,0],[1,0,0],[0,1,0],[0,0,1]])
        flat_sigma=ef.T*(grad-grad.T)*ef/2
        phase_colors.append(sp.Matrix([inner(t,flat_sigma) for t in T]))
    residuals={
        'natural_minus_horizontal_is_pure_spatial_rotation':expand(natural-horizontal-e*rho),
        'rotation_is_i_xi_omega_plus_sigma':expand(rho-rho_reference),
        'rho_is_antisymmetric':expand(rho+rho.T),
        'Cartan_connection_all_36_entries':cartan,
        'horizontal_connection_all_36_entries':[expand(a-b) for a,b in zip(horizontal_A,horizontal_reference)],
        'horizontal_parameter_is_i_xi_C_minus_sigma':expand(Lambda-sum((xi[mu]*C[mu] for mu in range(4)),sp.zeros(3))+sigma),
        'SO3_norm_gives_exact_spin_half':expand(G_sigma-spin_gradient),
        'H18_x_diffeomorphism_color_sign':phase_colors[0]-sp.Matrix([0,sp.I*q*amplitude/2,0]),
        'H18_y_diffeomorphism_color_sign':phase_colors[1]-sp.Matrix([-sp.I*q*amplitude/2,0,0])}
    negatives={'opposite_sigma_in_transport':expand(natural-horizontal-e*(rho_reference-2*sigma)),
               'fixed_bundle_omits_horizontal_sigma':expand(sigma),
               'double_SO3_spin_factor':expand(G_sigma-2*spin_gradient)}
    return {'metric':g,'normal':u,'frame':e,'xi':xi,'nabla_xi':dxi,'h':h,'beta':beta,
            'natural_frame_variation':natural,'horizontal_frame_variation':horizontal,
            'rho':rho,'sigma':sigma,'G':G,'G_H':GH,'G_sigma':G_sigma,
            'spin_gradient_half':spin_gradient,'phase_colors':phase_colors,
            'residuals':residuals,'negative_controls':negatives}


def lapse_geometry(N,coords):
    g=sp.diag(-N**2,1,1,1);gi=sp.diag(-1/N**2,1,1,1)
    u=sp.Matrix([1/N,0,0,0]);ucov=g*u
    e=sp.Matrix([[0,0,0],[1,0,0],[0,1,0],[0,0,1]])
    Gamma=[[[clean(sum(gi[a,c]*(sp.diff(g[c,nu],coords[mu])+sp.diff(g[c,mu],coords[nu])
                              -sp.diff(g[mu,nu],coords[c])) for c in range(4))/2)
             for nu in range(4)] for mu in range(4)] for a in range(4)]
    omega=[]
    for mu in range(4):
        derivative_frame=sp.Matrix(4,3,lambda nu,b:sp.diff(e[nu,b],coords[mu])
                            +sum(Gamma[nu][mu][rho]*e[rho,b] for rho in range(4)))
        omega.append(clean(e.T*g*derivative_frame))
    kappa=sp.Matrix(4,3,lambda mu,a:clean(sum(e[nu,a]*(sp.diff(ucov[nu],coords[mu])
                    -sum(Gamma[rho][mu][nu]*ucov[rho] for rho in range(4))) for nu in range(4))))
    # R^1{}_{0 1 0}, derived directly from Christoffel, not from N'' as an input.
    curvature=clean(sp.diff(Gamma[1][0][0],coords[1])-sp.diff(Gamma[1][1][0],coords[0])
         +sum(Gamma[1][1][lam]*Gamma[lam][0][0]-Gamma[1][0][lam]*Gamma[lam][1][0] for lam in range(4)))
    return {'coords':coords,'N':N,'metric':g,'inverse_metric':gi,'normal':u,'frame':e,
            'Gamma':Gamma,'omega':omega,'kappa':kappa,'R_1_0_1_0':curvature}


def mixed_divergence(tensor,geometry):
    """D_mu B^mu_nu from B^{mu nu}, using explicit Christoffel on both slots."""
    coords=geometry['coords'];Gamma=geometry['Gamma'];mixed=tensor*geometry['metric']
    return sp.Matrix([clean(sum(sp.diff(mixed[mu,nu],coords[mu]) for mu in range(4))
                     +sum(Gamma[mu][mu][lam]*mixed[lam,nu]-Gamma[lam][mu][nu]*mixed[mu,lam]
                          for mu in range(4) for lam in range(4))) for nu in range(4)])


def current_oracle(geometry,A,chi):
    """Build tau from its variational tensors, then differentiate it independently of the Ward RHS."""
    coords=geometry['coords'];g=geometry['metric'];gi=geometry['inverse_metric']
    N=geometry['N'];u=geometry['normal'];e=geometry['frame'];Gamma=geometry['Gamma']
    C=[A[mu]-geometry['omega'][mu] for mu in range(4)]
    Cup=[sum((gi[mu,nu]*C[nu] for nu in range(4)),sp.zeros(3)) for mu in range(4)]
    trace_Gamma=[sum(Gamma[mu][mu][lam] for mu in range(4)) for lam in range(4)]
    J=[[[clean(chi*sum(Cup[mu][a,b]*e[nu,a]*e[rho,b] for a in range(3) for b in range(3)))
          for rho in range(4)] for nu in range(4)] for mu in range(4)]
    divJ=sp.Matrix(4,4,lambda mu,nu:clean(
        sum(sp.diff(J[mu][nu][rho],coords[rho]) for rho in range(4))
        +sum(Gamma[mu][rho][lam]*J[lam][nu][rho]+Gamma[nu][rho][lam]*J[mu][lam][rho]
             +Gamma[rho][rho][lam]*J[mu][nu][lam] for rho in range(4) for lam in range(4))))
    V=sp.Matrix([clean(chi*sum(Cup[mu][a,b]*geometry['kappa'][mu,a]*e[nu,b]
                     for mu in range(4) for a in range(3) for b in range(3))) for nu in range(4)])
    norm=sum(inner(C[mu],Cup[mu]) for mu in range(4))
    T=sp.Matrix(4,4,lambda mu,nu:clean(chi*(inner(Cup[mu],Cup[nu])-gi[mu,nu]*norm/2)))
    tau=clean(T-(divJ+divJ.T)/2-(V*u.T+u*V.T)/2)
    ET=clean(sum(sp.diff(N*V[mu],coords[mu]) for mu in range(4))
             +sum(trace_Gamma[mu]*N*V[mu] for mu in range(4)))
    div_tau=mixed_divergence(tau,geometry)
    div_tau_contra=sp.Matrix([clean(sum(sp.diff(tau[mu,nu],coords[mu]) for mu in range(4))
         +sum(Gamma[mu][mu][lam]*tau[lam,nu]+Gamma[nu][mu][lam]*tau[mu,lam]
              for mu in range(4) for lam in range(4))) for nu in range(4)])
    F=[[clean(A[mu].diff(coords[nu])-A[nu].diff(coords[mu])+A[nu]*A[mu]-A[mu]*A[nu])
        for mu in range(4)] for nu in range(4)]
    G=clean(chi*(sum((Cup[mu].diff(coords[mu])+trace_Gamma[mu]*Cup[mu]
             +A[mu]*Cup[mu]-Cup[mu]*A[mu] for mu in range(4)),sp.zeros(3))))
    GH=clean(e*G*e.T);div_GH=mixed_divergence(GH,geometry)
    form_div_GH=g*sp.Matrix([clean(sum(sp.diff(N*GH[mu,nu],coords[mu]) for mu in range(4))/N) for nu in range(4)])
    force=sp.Matrix([clean(chi*sum(inner(Cup[mu],F[nu][mu]) for mu in range(4))) for nu in range(4)])
    GC=sp.Matrix([clean(inner(G,C[nu])) for nu in range(4)])
    ET_dT=sp.Matrix([ET,0,0,0])
    rhs=clean(ET_dT-force+GC+div_GH/2)
    ward=clean(div_tau-rhs)
    commutators=[[clean(A[nu]*A[mu]-A[mu]*A[nu]) for mu in range(4)] for nu in range(4)]
    return {'geometry':geometry,'A':A,'C':C,'C_raised':Cup,'J':J,'divergence_J':divJ,'V':V,
            'T_C':T,'tau_C':tau,'E_T':ET,'F':F,'G':G,'G_H':GH,'divergence_tau':div_tau,
            'divergence_G_H':div_GH,'force_chi_C_F':force,'G_C':GC,'rhs':rhs,'ward_residual':ward,
            'mixed_vs_contravariant_divergence':clean(div_tau-g*div_tau_contra),
            'antisymmetric_divergence_vs_volume_formula':clean(div_GH-form_div_GH),
            'commutators':commutators,
            'negative_controls':{'omit_horizontal_spin_divergence':clean(ward+div_GH/2),
                                 'reverse_horizontal_spin_sign':clean(ward+div_GH),
                                 'omit_khronon_Euler':clean(ward+ET_dT)}}


@lru_cache(maxsize=1)
def derive_model():
    transport=transport_model()
    t,x,y,z=sp.symbols('t x y z',real=True);coords=(t,x,y,z)
    a,chi=sp.symbols('a chi',positive=True);epsilon=sp.Symbol('epsilon',real=True)
    generators=[sp.Matrix(3,3,lambda j,k:sp.LeviCivita(i,j,k)) for i in range(3)]
    M13=sp.zeros(3);M13[0,2]=1;M13[2,0]=-1
    flat=current_oracle(lapse_geometry(sp.S.One,coords),[sp.zeros(3),epsilon*x*z*M13,sp.zeros(3),sp.zeros(3)],chi)
    flat_linear=flat['tau_C'].diff(epsilon).subs(epsilon,0).applyfunc(sp.expand)
    flat_div_linear=flat['divergence_tau'].diff(epsilon).subs(epsilon,0).applyfunc(sp.expand)
    flat_spin_linear=flat['divergence_G_H'].diff(epsilon).subs(epsilon,0).applyfunc(sp.expand)/2
    N=1+a*x*x
    curved=current_oracle(lapse_geometry(N,coords),[x*z*generators[1],x*generators[0],sp.zeros(3),z*generators[2]],chi)
    expected_G=chi*((1+3*a*x*x)*generators[0]/N+generators[2])
    residuals={**transport['residuals'],
        'flat_all_four_exact_Ward_rows':flat['ward_residual'],
        'flat_linear_divergence_matches_half_spin':clean(flat_div_linear-flat_spin_linear),
        'flat_explicit_missing_spin_witness':clean(flat_div_linear-sp.Matrix([0,-chi/2,0,0])),
        'curved_all_four_exact_Ward_rows':curved['ward_residual'],
        'curved_nonzero_E_T_normalization':clean(curved['E_T']-2*chi*a*x*x/N),
        'curved_G_normalization':clean(curved['G']-expected_G),
        'curved_all_36_projected_connection_entries':[clean(o) for o in curved['geometry']['omega']],
        'curved_kappa_from_covariant_normal':clean(curved['geometry']['kappa'][0,0]-2*a*x),
        'curved_Riemann_from_Christoffel':clean(curved['geometry']['R_1_0_1_0']-2*a*N),
        'curved_mixed_divergence_independent_contraction':curved['mixed_vs_contravariant_divergence'],
        'curved_spin_divergence_independent_volume_formula':curved['antisymmetric_divergence_vs_volume_formula']}
    negatives={**transport['negative_controls'],
        'flat_omit_spin':flat['negative_controls']['omit_horizontal_spin_divergence'],
        'curved_omit_spin':curved['negative_controls']['omit_horizontal_spin_divergence'],
        'curved_reverse_spin':curved['negative_controls']['reverse_horizontal_spin_sign'],
        'curved_omit_E_T':curved['negative_controls']['omit_khronon_Euler']}
    checks={name:zero(value) for name,value in residuals.items()}
    checks.update({f'negative_control_{name}_detected':not zero(value) for name,value in negatives.items()})
    checks.update({'curved_connection_is_nonabelian':not zero(curved['commutators']),
                   'curved_F_is_not_zero':not zero(curved['F']),
                   'curved_G_is_not_zero':not zero(curved['G']),
                   'curved_E_T_is_not_zero':curved['E_T']!=0,
                   'curved_metric_is_not_Rindler_flat':curved['geometry']['R_1_0_1_0']!=0})
    return {'symbols':{'coords':coords,'a':a,'chi':chi,'epsilon':epsilon},'transport':transport,
            'flat':flat,'flat_linear_tau':flat_linear,'flat_linear_divergence':flat_div_linear,
            'flat_linear_half_spin_divergence':flat_spin_linear,'curved':curved,
            'residuals':residuals,'negative_controls':negatives,'checks':{k:bool(v) for k,v in checks.items()}}


def serialize(value):
    if isinstance(value,sp.MatrixBase): return [[serialize(x) for x in row] for row in value.tolist()]
    if isinstance(value,dict): return {k:serialize(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serialize(v) for v in value]
    return str(value) if isinstance(value,sp.Basic) else value


def load_sources():
    if hashlib.sha256(PROOF.read_bytes()).hexdigest()!=PROOF_SHA: raise HorizontalWardError('proof byte pin mismatch')
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA: raise HorizontalWardError('covariant source byte pin mismatch')
    source=json.loads(raw)
    if not source.get('checks') or not all(v is True for v in source['checks'].values()):
        raise HorizontalWardError('covariant source checks invalid')
    for name,pin in source['provenance'].items():
        if Path(name).name!=name or hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=pin:
            raise HorizontalWardError('covariant source implementation changed')
    return {'covariant_receipt_sha256':SOURCE_SHA,'lemma_sha256':PROOF_SHA,'source_gates_inherited':False}


def build_payload():
    source=load_sources();model=derive_model()
    if not all(model['checks'].values()): raise HorizontalWardError('horizontal Ward check failed')
    payload={'schema':SCHEMA,'sources':source,
        'proposal':{'adopted':False,'chi':'positive mass-squared symbol; no selected value','A_independent_of_omega':True},
        'model':serialize(model),'checks':model['checks'],
        'scope':{'covariant_off_shell_Ward_proof_bound':True,'horizontal_frame_transport_checked':True,
                 'all_four_flat_and_curved_Ward_rows_checked':True,'curved_oracle_has_nonzero_F_G_and_E_T':True,
                 'N4_JUNCTION_BENDING_pass':False,'N7_LINEAR_REDUCTION_pass':False,'P4_full_same_action_pass':False,
                 'B4_pass':False,'B5_pass':False,'BF_global_quotient_closed':False,
                 'full_moving_gluing_chain_closed':False,'coupled_Einstein_solution':False,
                 'nonlinear_stability_proved':False,'candidate_adopted':False,'chi_selected':False},
        'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),TEST,PROOF)}}
    payload['calculation_digest']=digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA: raise HorizontalWardError('receipt schema mismatch')
    if payload.get('calculation_digest')!=digest({k:v for k,v in payload.items() if k!='calculation_digest'}):
        raise HorizontalWardError('receipt digest mismatch')
    if payload!=build_payload(): raise HorizontalWardError('receipt differs from trusted recomputation')


def main():
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',nargs='?',const=OUTPUT,type=Path)
    mode.add_argument('--verify',nargs='?',const=OUTPUT,type=Path);args=parser.parse_args()
    if args.write:
        result=build_payload()
        with args.write.open('x',encoding='utf-8') as stream:
            json.dump(result,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')
    else:
        result=json.loads(args.verify.read_bytes());validate_payload(result)
    print(json.dumps({'schema':SCHEMA,'checks_passed':sum(result['checks'].values()),
                      'checks_total':len(result['checks']),'calculation_digest':result['calculation_digest']}))


if __name__=='__main__': main()
