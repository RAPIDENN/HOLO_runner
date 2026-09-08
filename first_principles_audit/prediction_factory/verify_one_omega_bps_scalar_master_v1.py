"""Independent radial-ADM scalar reduction with every quadratic boundary current.

Comoving gauge delta Omega=0; gamma_mu_nu=exp(2A+2epsilon*zeta)*eta_mu_nu,
N=1+epsilon*alpha and the COVARIANT shift is N_mu=epsilon*partial_mu beta
(no exp(2A) factor). K=(gamma' - D N - D N)/(2N). The spacetime radial
normal is spacelike and eta=(-,+,+,+). The starting density includes EH+GHY
in radial ADM form, plus the complete background Omega kinetic energy and U.

The shift is varied as an unrestricted one-form BEFORE evaluating its momentum
constraint on a longitudinal shift. Varying beta alone would give box(C)=0
instead of partial_mu C=0 and lose information at null slice momentum.
C=zeta'-A'alpha is set to zero in the nonhomogeneous sector, or after fixing its
slice-constant integration function. No inverse slice d'Alembertian is used.
The remaining lapse equation specifies box(beta), not a reconstructed beta;
constraint reconstruction on a characteristic/zero-momentum sector is open.

Only fixed-comoving-wall primitives are recorded. Moving embeddings, brane
field mixing, physical scalar admissibility, full N7 and P4 are not certified.
No previous scalar master or boundary condition is imported as a premise.
"""
from __future__ import annotations

from itertools import combinations_with_replacement

import sympy as sp


class ScalarMasterError(ValueError):
    """An expression falls outside the declared scalar ADM jet domain."""


def symbols_context() -> dict:
    real_names = ("epsilon","A","App","Op","Opp","zeta","zeta_p","zeta_pp","alpha","alpha_p","beta")
    s = dict(zip(real_names,sp.symbols(" ".join(real_names),real=True)))
    s["Ap"] = sp.Symbol("Ap",real=True,nonzero=True)
    s.update(dict(zip(("omega","G","M5c","k","a"),sp.symbols("Omega G M5c k a",positive=True))))
    s["eta"] = sp.diag(-1,1,1,1)
    for key in ("grad_zeta","grad_zeta_p","grad_alpha","grad_beta"):
        s[key] = sp.Matrix(sp.symbols(key+"0:4",real=True))
    for key in ("hess_zeta","hess_beta"):
        entries={(i,j):sp.Symbol(f"{key}_{i}{j}",real=True) for i in range(4) for j in range(i,4)}
        s[key]=sp.Matrix(4,4,lambda i,j:entries[min(i,j),max(i,j)])
    s["third_beta"]={indices:sp.Symbol("third_beta_"+"".join(map(str,indices)),real=True)
                     for indices in combinations_with_replacement(range(4),3)}
    return s


def _trunc(expression: sp.Expr, epsilon: sp.Symbol) -> sp.Expr:
    expanded=sp.expand(expression)
    return sum(expanded.coeff(epsilon,n)*epsilon**n for n in range(3))


def radial_derivative(expression: sp.Expr, s: dict) -> sp.Expr:
    rules={s["A"]:s["Ap"],s["Ap"]:s["App"],s["omega"]:s["Op"],s["Op"]:s["Opp"],
           s["zeta"]:s["zeta_p"],s["zeta_p"]:s["zeta_pp"],s["alpha"]:s["alpha_p"]}
    rules.update(dict(zip(s["grad_zeta"],s["grad_zeta_p"])))
    return sp.expand(sum(sp.diff(expression,key)*value for key,value in rules.items()))


def tangential_derivative(expression: sp.Expr, mu: int, s: dict) -> sp.Expr:
    if mu not in range(4): raise ScalarMasterError("tangential index must be 0..3")
    rules={s["zeta"]:s["grad_zeta"][mu],s["zeta_p"]:s["grad_zeta_p"][mu],s["alpha"]:s["grad_alpha"][mu],s["beta"]:s["grad_beta"][mu]}
    for j in range(4):
        rules[s["grad_zeta"][j]]=s["hess_zeta"][mu,j]
        rules[s["grad_beta"][j]]=s["hess_beta"][mu,j]
    for i in range(4):
        for j in range(i,4):
            rules[s["hess_beta"][i,j]]=s["third_beta"][tuple(sorted((mu,i,j))) ]
    return sp.expand(sum(sp.diff(expression,key)*value for key,value in rules.items()))


def divergence(current: sp.MatrixBase, s: dict) -> sp.Expr:
    if not isinstance(current,sp.MatrixBase) or current.shape!=(4,1):
        raise ScalarMasterError("a contravariant four-current is required")
    return sp.expand(sum(tangential_derivative(current[mu],mu,s) for mu in range(4)))


def derive_model() -> dict:
    s=symbols_context()
    e,A,ap,app,op,opp,z,zp,zpp,alpha = (s[name] for name in ("epsilon","A","Ap","App","Op","Opp","zeta","zeta_p","zeta_pp","alpha"))
    o,G,M,k,eta = (s[name] for name in ("omega","G","M5c","k","eta"))
    gz,gzp,ga,gb,Hz,Hb = (s[name] for name in ("grad_zeta","grad_zeta_p","grad_alpha","grad_beta","hess_zeta","hess_beta"))
    def tr(value):return _trunc(value,e)
    def mt(value):return sp.Matrix(value).applyfunc(tr)
    def quad(value):return sp.expand(value).coeff(e,2)
    def dr(value):return radial_derivative(value,s)
    W=3*M*k*sp.exp(-G*o**2/(6*M))
    Wp=sp.diff(W,o)
    U=Wp**2/(2*G)-2*W**2/(3*M)
    bps={ap:-W/(3*M),op:Wp/G,app:-Wp**2/(3*M*G)}
    H0=6*M*ap**2-G*op**2/2+U
    Eacc=3*M*app+G*op**2
    X=(gz.T*eta*gz)[0]
    Xp=2*(gz.T*eta*gzp)[0]
    mixed=(gz.T*eta*gb)[0]
    box_zeta=sp.trace(eta*Hz)
    box_beta=sp.trace(eta*Hb)
    beta_hessian_norm=sp.trace(eta*Hb*eta*Hb)
    gamma=sp.exp(2*A)*(1+2*e*z+2*e**2*z**2)*eta
    gamma_inverse=sp.exp(-2*A)*(1-2*e*z+2*e**2*z**2)*eta
    sqrt_gamma=sp.exp(4*A)*(1+4*e*z+8*e**2*z**2)
    N=1+e*alpha
    inverse_N=1-e*alpha+e**2*alpha**2
    # D_mu N_nu includes the first-order conformal Christoffel connection.
    covariant_shift_derivative=e*Hb-e**2*(gz*gb.T+gb*gz.T-eta*mixed)
    Q=mt(gamma_inverse*covariant_shift_derivative)
    H=ap+e*zp
    K=mt(inverse_N*(H*sp.eye(4)-Q))
    trace_Q=tr(sp.trace(Q)); norm_Q=tr(sp.trace(Q*Q))
    K_invariant_numerator=tr(12*H**2-6*H*trace_Q+trace_Q**2-norm_Q)
    radial_density=tr(M*sqrt_gamma*inverse_N*12*H**2/2-sqrt_gamma*(G*op**2*inverse_N/2+N*U))
    shift_density=tr(M*sqrt_gamma*inverse_N*(-6*H*trace_Q+trace_Q**2-norm_Q)/2)
    # Exact conformal Ricci identity for four flat Lorentzian slice coordinates.
    R4=tr(sp.exp(-2*A)*(1-2*e*z+2*e**2*z**2)*(-6*e*box_zeta-6*e**2*X))
    intrinsic_density=tr(M*N*sqrt_gamma*R4/2)
    raw_radial_L2=sp.expand(quad(radial_density))
    raw_shift_L2=sp.expand(quad(shift_density))
    raw_intrinsic_L2=sp.expand(quad(intrinsic_density))
    raw_L2=raw_radial_L2+raw_shift_L2+raw_intrinsic_L2
    C=zp-ap*alpha
    F_rad=24*M*sp.exp(4*A)*ap*z**2
    radial_completed=sp.exp(4*A)*(6*M*C**2-G*op**2*alpha**2/2)+dr(F_rad)
    radial_background_remainder=-sp.exp(4*A)*(4*H0*z*alpha+8*(H0+Eacc)*z**2)
    beta_current=box_beta*(eta*gb)-eta*Hb*eta*gb
    shift_boundary_current=-6*M*sp.exp(2*A)*ap*z*(eta*gb)+M*beta_current/2
    curvature_current=-3*M*sp.exp(2*A)*(alpha+2*z)*(eta*gz)
    shift_reduced=-3*M*sp.exp(2*A)*C*box_beta
    intrinsic_after_tangential_parts=3*M*sp.exp(2*A)*((ga.T*eta*gz)[0]+X)
    # Full vector shift variation, evaluated only afterwards at b_mu=partial_mu beta.
    J=sp.Matrix(4,4,lambda i,j:sp.Symbol(f"shift_gradient_{i}{j}",real=True))
    symmetric_J=(J+J.T)/2
    vector_shift_quadratic=M*(sp.trace(eta*J)**2-sp.trace(eta*symmetric_J*eta*symmetric_J))/2
    vector_quadratic_Euler=sp.Matrix([
        -sum(sp.diff(sp.diff(vector_shift_quadratic,J[mu,nu]),J[rho,sigma])*s["third_beta"][tuple(sorted((mu,rho,sigma)))]
             for mu in range(4) for rho in range(4) for sigma in range(4))
        for nu in range(4)]).applyfunc(sp.expand)
    momentum_vector=3*M*sp.exp(2*A)*eta*(gzp-ap*ga)+vector_quadratic_Euler
    lapse_constraint=sp.diff(raw_L2,alpha)
    lapse_expected=-12*M*ap*sp.exp(4*A)*C-G*op**2*sp.exp(4*A)*alpha-3*M*sp.exp(2*A)*box_zeta+3*M*ap*sp.exp(2*A)*box_beta
    alpha_solution=zp/ap
    alpha_subs={alpha:alpha_solution}
    alpha_subs.update({ga[mu]:gzp[mu]/ap for mu in range(4)})
    box_beta_solution=box_zeta/ap+sp.exp(2*A)*G*op**2*zp/(3*M*ap**2)
    Qscalar=G*op**2/ap**2
    reduced_L2=-Qscalar*(sp.exp(4*A)*zp**2+sp.exp(2*A)*X)/2
    F_grad=3*M*sp.exp(2*A)*X/(2*ap)
    tangential_boundary_current=curvature_current.xreplace(alpha_subs)+shift_boundary_current
    background_remainder=-sp.exp(4*A)*(4*H0*z*zp/ap+8*(H0+Eacc)*z**2)+sp.exp(2*A)*Eacc*X/(2*ap**2)
    total_derivative_residual=sp.expand(raw_L2.xreplace(alpha_subs)-reduced_L2-dr(F_rad+F_grad)-divergence(tangential_boundary_current,s)-background_remainder)
    pump_squared=sp.exp(3*A)*Qscalar
    pump_BPS_squared=G*o**5
    Q_BPS=G*o**2
    master_flux=dr(sp.exp(4*A)*Q_BPS*zp)+sp.exp(2*A)*Q_BPS*box_zeta
    master_equation=sp.cancel(master_flux/(sp.exp(4*A)*Q_BPS))
    master_equation_BPS=zpp+6*ap*zp+sp.exp(-2*A)*box_zeta
    W0=W.subs(o,1); ap0=-W0/(3*M)
    F_rad_UV=F_rad.subs({A:0,ap:ap0},simultaneous=True)
    F_grad_UV=F_grad.subs({A:0,ap:ap0},simultaneous=True)
    wall_tension_L2=-16*W0*z**2
    UV_mass_cancellation=sp.simplify(-2*F_rad_UV+wall_tension_L2)
    UV_gradient_density=-2*F_grad_UV
    # Coefficient identity only: it does not authorize adding an induced EH term twice.
    a=s["a"]
    scalar_norm=G*(sp.exp(a)*(a-1)+1)/(k*a**2)
    M4_bulk_squared=M*(sp.exp(a)-1)/(k*a)
    UV_gradient_coefficient=3*M*sp.exp(a)/k
    conformal_EH_coefficient_residual=sp.cancel((UV_gradient_coefficient-scalar_norm/2-3*M4_bulk_squared).subs(G,6*M*a))
    rows={
        "inverse_conformal_metric":mt(gamma*gamma_inverse-sp.eye(4)),
        "extrinsic_invariant_from_matrix":tr(sp.trace(K)**2-sp.trace(K*K)-inverse_N**2*K_invariant_numerator),
        "conformal_shift_trace":tr(trace_Q-sp.exp(-2*A)*(e*box_beta+e**2*(2*mixed-2*z*box_beta))),
        "radial_square_and_primitive":sp.expand(raw_radial_L2-radial_completed-radial_background_remainder),
        "intrinsic_density_explicit":sp.expand(raw_intrinsic_L2+3*M*sp.exp(2*A)*((alpha+2*z)*box_zeta+X)),
        "shift_current_product_rule":sp.expand(raw_shift_L2-shift_reduced-divergence(shift_boundary_current,s)),
        "curvature_current_product_rule":sp.expand(raw_intrinsic_L2-intrinsic_after_tangential_parts-divergence(curvature_current,s)),
        "longitudinal_shift_vector_quadratic_Euler":vector_quadratic_Euler,
        "lapse_constraint_with_background_row":sp.expand(lapse_constraint-lapse_expected+4*sp.exp(4*A)*H0*z),
        "lapse_after_momentum_constraint":sp.expand(lapse_expected.xreplace(alpha_subs).subs(box_beta,box_beta_solution)),
        "all_total_derivatives_retained":total_derivative_residual,
        "BPS_Hamiltonian":sp.simplify(H0.subs(bps,simultaneous=True)),
        "BPS_acceleration":sp.simplify(Eacc.subs(bps,simultaneous=True)),
        "BPS_background_remainder":sp.simplify(background_remainder.subs(bps,simultaneous=True)),
        "BPS_flow_ratio":sp.simplify((op/ap-o).subs(bps,simultaneous=True)),
        "pump_in_conformal_radial_coordinate":sp.simplify(pump_squared.subs(bps,simultaneous=True).subs(A,sp.log(o))-pump_BPS_squared),
        "master_BPS_friction":sp.expand(master_equation.subs(op,ap*o)-master_equation_BPS),
        "two_sides_fixed_wall_mass_primitive":UV_mass_cancellation,
        "UV_gradient_primitive":sp.simplify(UV_gradient_density-3*M*sp.exp(G/(6*M))*X/k),
        "radially_constant_IR_conformal_EH_coefficient":conformal_EH_coefficient_residual,
    }
    residuals={name:value.applyfunc(sp.simplify) if isinstance(value,sp.MatrixBase) else sp.simplify(value) for name,value in rows.items()}
    checks={name:all(item==0 for item in value) if isinstance(value,sp.MatrixBase) else value==0 for name,value in residuals.items()}
    return {
        "symbols":s,"W":W,"U":U,"bps_substitutions":bps,"background_hamiltonian":H0,"background_acceleration":Eacc,
        "gamma":gamma,"gamma_inverse":gamma_inverse,"sqrt_gamma":sqrt_gamma,"N":N,"covariant_shift_derivative":covariant_shift_derivative,"K":K,"R4":R4,
        "X":X,"X_p":Xp,"box_zeta":box_zeta,"box_beta":box_beta,"beta_hessian_norm":beta_hessian_norm,
        "raw_L2":raw_L2,"raw_radial_L2":raw_radial_L2,"raw_intrinsic_L2":raw_intrinsic_L2,"raw_shift_L2":raw_shift_L2,
        "momentum_constraint":C,"momentum_vector":momentum_vector,"vector_shift_quadratic_Euler":vector_quadratic_Euler,
        "lapse_constraint":lapse_constraint,"lapse_constraint_background_reduced":lapse_expected,"alpha_solution":alpha_solution,
        "alpha_substitutions":alpha_subs,"box_beta_solution":box_beta_solution,"reduced_L2":reduced_L2,
        "F_rad":F_rad,"F_grad":F_grad,"F_rad_derivative":dr(F_rad),"F_grad_derivative":dr(F_grad),
        "shift_boundary_current":shift_boundary_current,"curvature_boundary_current":curvature_current,
        "tangential_boundary_current":tangential_boundary_current,"tangential_boundary_divergence":divergence(tangential_boundary_current,s),
        "background_remainder":background_remainder,"total_derivative_residual":total_derivative_residual,
        "pump_squared":pump_squared,"pump_BPS_squared":pump_BPS_squared,"master_flux":master_flux,
        "master_equation":master_equation,"master_equation_BPS":master_equation_BPS,
        "F_rad_UV":F_rad_UV,"F_grad_UV":F_grad_UV,"wall_tension_L2":wall_tension_L2,"UV_mass_cancellation":UV_mass_cancellation,
        "UV_gradient_density":UV_gradient_density,"scalar_norm":scalar_norm,"M4_bulk_squared":M4_bulk_squared,
        "a_relation":G/(6*M),"conformal_EH_coefficient_residual":conformal_EH_coefficient_residual,
        "checks":checks,"residuals":residuals,
        "scope":{"shift_convention":"covariant N_mu=epsilon*partial_mu beta, without exp(2A)",
                 "momentum_constraint":"full one-form variation before longitudinal restriction; no division by slice momentum squared",
                 "slice_homogeneous_integration_function_fixed":True,
                 "beta_reconstruction_at_null_or_zero_slice_momentum_certified":False,
                 "wall":"only fixed comoving UV values and their explicit primitives; no bending or mixed brane Hessian",
                 "scalar_physical_admissibility":False,"full_N7":False,"P4":False,
                 "coefficient_identity":"UV gradient minus half bilateral scalar bulk norm equals 3*M4_bulk_squared; do not add an induced EH term twice"}}


# Receipt I/O is separate from the symbolic construction above.
import argparse
import hashlib
import json
from pathlib import Path
if __package__:
    from . import one_omega_bps_scalar_master_rows_v1 as row_oracle
    from . import verify_one_omega_topological_tt_compatibility_v1 as source_oracle
else:
    import one_omega_bps_scalar_master_rows_v1 as row_oracle
    import verify_one_omega_topological_tt_compatibility_v1 as source_oracle

HERE=Path(__file__).resolve().parent
OUTPUT=HERE/'artifacts/one_omega_bps_scalar_master_v1.json'
TEST=HERE/'test_one_omega_bps_scalar_master_v1.py'
SCHEMA='holo.one-omega-bps-scalar-master.v1'
canonical_digest=source_oracle.canonical_digest


def _serialize(value):
    if isinstance(value,sp.MatrixBase):return _serialize(value.tolist())
    if isinstance(value,sp.Basic):return str(value)
    if isinstance(value,dict):return {str(k):_serialize(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [_serialize(v) for v in value]
    return value


def build_payload():
    sources=source_oracle.load_sources()
    adm=derive_model();gn=row_oracle.derive_rows();boundary=row_oracle.derive_boundary(gn)
    checks={**{'ADM_'+k:v for k,v in adm['checks'].items()},
            **{'GN_'+k:v for k,v in gn['checks'].items()},
            **{'boundary_'+k:v for k,v in boundary['checks'].items()}}
    if not all(checks.values()):raise ScalarMasterError('scalar ADM or GN boundary identity failed')
    files=[Path(__file__),Path(row_oracle.__file__),TEST,Path(source_oracle.__file__),
           Path(row_oracle.source.__file__)]
    payload={'schema':SCHEMA,
             'sources':{'old_charter':source_oracle.source_oracle.CHARTER_BYTES_SHA256,
                        'candidate':source_oracle.CANDIDATE_SHA256,
                        'candidate_action':source_oracle.CANDIDATE_ACTION_SHA256,
                        'bulk_snapshot':row_oracle.BULK_SHA},
             'action_compatibility':sources['compatibility'],
             'ADM':_serialize({k:v for k,v in adm.items() if k!='symbols'}),
             'GN_rows':_serialize({k:v for k,v in gn.items() if k!='symbols'}),
             'boundary':_serialize({k:v for k,v in boundary.items() if k!='symbols'}),
             'checks':checks,
             'decision':{'bulk_scalar_master_derived_from_radial_ADM':True,
                         'all_quadratic_boundary_currents_retained':True,
                         'GN_constraint_identity_without_inverse_slice_wave_operator':True,
                         'canonical_GN_scalar_boundary_response_derived':True,
                         'legacy_Robin_base_equivalence_certified':False,
                         'full_vector_and_tensor_boundary_projectors_assembled':False,
                         'complete_candidate_linearization_certified':False,
                         'moving_embedding_equations_certified':False,
                         'BF_edge_sector_certified':False,
                         'physical_scalar_admissibility':False,
                         'global_spectrum_or_stability_certified':False,
                         'full_N7':False,'full_P4':False,'B4':False,'B5':False},
             'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:
        raise ScalarMasterError('scalar receipt schema mismatch')
    digest=canonical_digest({k:v for k,v in payload.items() if k!='calculation_digest'})
    if payload.get('calculation_digest')!=digest:raise ScalarMasterError('scalar receipt digest mismatch')
    if payload!=build_payload():raise ScalarMasterError('scalar receipt differs from fresh derivation')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path)
    modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args()
    if args.write:
        payload=build_payload()
        with args.write.open('x',encoding='utf8') as f:
            json.dump(payload,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
    else:
        payload=source_oracle.source_oracle._read_json(args.verify.read_bytes())
        validate_payload(payload)
    print(json.dumps({'checks_passed':sum(payload['checks'].values()),
                      'calculation_digest':payload['calculation_digest']}))


if __name__=='__main__':main()
