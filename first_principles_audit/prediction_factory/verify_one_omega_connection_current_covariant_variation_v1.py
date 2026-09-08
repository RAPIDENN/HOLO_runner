"""Covariant first variation of an unadopted connection-current term."""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import sympy as sp

HERE = Path(__file__).resolve().parent
SOURCE = HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
PROOF = HERE/'one_omega_connection_current_covariant_variation_lemma_v1.md'
PROJECTED = HERE/'one_omega_projected_connection_linear_lemma_v1.md'
CANDIDATE = HERE/'one_omega_interface_connection_current_candidate_lemma_v1.md'
TEST = HERE/'test_one_omega_connection_current_covariant_variation_v1.py'
OUTPUT = HERE/'artifacts/one_omega_connection_current_covariant_variation_v1.json'
SOURCE_SHA = 'd9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
ACTION_SHA = '3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a'
PROOF_SHA = '07a995c4058712f8611c9c8938640b1b6927d7265167c33e6e5af7da0cee64cc'
PROJECTED_SHA = '5eb335367c04c17930c42f18310b1750774088baafdff5906565232a3d40856a'
CANDIDATE_SHA = 'ab9745c81faf58e83fef2937b97f7de7e2c6f9ae3bce8bd3cf4fa8aeeb87966b'
SCHEMA = 'holo.one-omega-connection-current-covariant-variation.v1'


class CovariantVariationError(ValueError):
    pass


def canonical_digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def antisymmetric(prefix):
    values = {(a,b):sp.Symbol(f'{prefix}_{a}{b}', real=True) for a in range(3) for b in range(a+1,3)}
    return sp.Matrix(3,3,lambda a,b:0 if a==b else (1 if a<b else -1)*values[min(a,b),max(a,b)])


def symmetric(prefix, size=4):
    values = {(a,b):sp.Symbol(f'{prefix}_{a}{b}', real=True) for a in range(size) for b in range(a,size)}
    return sp.Matrix(size,size,lambda a,b:values[min(a,b),max(a,b)])


def expanded(value):
    return value.applyfunc(sp.expand) if isinstance(value, sp.MatrixBase) else sp.expand(value)


def is_zero(value):
    if isinstance(value, sp.MatrixBase):
        return all(x == 0 for x in value)
    if isinstance(value, (list,tuple)):
        return all(is_zero(x) for x in value)
    return value == 0


def point_context():
    """A boosted orthonormal frame at a normal-coordinate point; no field equations."""
    metric = sp.diag(-4,9,1,1)
    normal = sp.Matrix([sp.Rational(5,8),sp.Rational(1,4),0,0])
    frame = sp.Matrix([[sp.Rational(3,8),0,0],[sp.Rational(5,12),0,0],[0,1,0],[0,0,1]])
    return {
        'metric':metric,'inverse_metric':metric.inv(),'normal':normal,'frame':frame,
        'h':symmetric('h'),'dh':[symmetric(f'dh{mu}') for mu in range(4)],
        'omega':[antisymmetric(f'omega{mu}') for mu in range(4)],
        'kappa':sp.Matrix(4,3,lambda mu,a:sp.Symbol(f'kappa{mu}_{a}',real=True)),
        'beta':sp.Matrix(sp.symbols('beta0:3',real=True)),
        'dbeta':sp.Matrix(4,3,lambda mu,a:sp.Symbol(f'dbeta{mu}_{a}',real=True)),
        'C':[antisymmetric(f'C{mu}') for mu in range(4)],
        'delta_A':[antisymmetric(f'dA{mu}') for mu in range(4)],
        'rho':antisymmetric('rho'),'drho':[antisymmetric(f'drho{mu}') for mu in range(4)],
        'chi':sp.Symbol('chi',positive=True),'N':sp.Symbol('N',positive=True),
        'df':sp.Matrix(sp.symbols('df0:4',real=True))}


def connection_variation(context):
    """Differentiate g(e_a,nabla_mu e_b) with the frame term retained."""
    g,gi,u,e,h = (context[k] for k in ('metric','inverse_metric','normal','frame','h'))
    beta,dbeta,kappa = (context[k] for k in ('beta','dbeta','kappa'))
    delta_e = -gi*h*e/2 + u*beta.T
    direct=[]; reference=[]; frozen=[]; rotation=[]; rotation_reference=[]
    for mu in range(4):
        omega=context['omega'][mu]
        dframe=e*omega+u*kappa.row(mu)
        dnormal=e*kappa.row(mu).T
        ddelta_e=-gi*context['dh'][mu]*e/2-gi*h*dframe/2+dnormal*beta.T+u*dbeta.row(mu)
        delta_gamma=sp.Matrix(4,4,lambda nu,rho:
            sum(gi[nu,a]*(context['dh'][mu][a,rho]+context['dh'][rho][a,mu]
                           -context['dh'][a][mu,rho]) for a in range(4))/2)
        direct.append(expanded(e.T*h*dframe+delta_e.T*g*dframe+e.T*g*ddelta_e+e.T*g*delta_gamma*e))
        reference.append(expanded(sp.Matrix(3,3,lambda a,b:
            sum(e[nu,a]*e[rho,b]*(context['dh'][rho][mu,nu]-context['dh'][nu][mu,rho])
                for nu in range(4) for rho in range(4))/2
            +kappa[mu,a]*beta[b]-kappa[mu,b]*beta[a])))
        frozen.append(expanded(e.T*h*dframe+e.T*g*delta_gamma*e))
        # An independent vertical rotation of the orthonormal frame.
        rho=context['rho']; drho=context['drho'][mu]
        de_rot=e*rho; dde_rot=dframe*rho+e*drho
        rotation.append(expanded(de_rot.T*g*dframe+e.T*g*dde_rot))
        rotation_reference.append(expanded(drho+omega*rho-rho*omega))
    return {'delta_e':delta_e,'direct':direct,'reference':reference,
            'residuals':[expanded(a-b) for a,b in zip(direct,reference)],
            'frozen_frame':frozen,'rotation_direct':rotation,'rotation_reference':rotation_reference,
            'rotation_residuals':[expanded(a-b) for a,b in zip(rotation,rotation_reference)]}


def adjoint_identity():
    """Product-rule derivation using independent smooth functions, not asserted divergences."""
    x=sp.symbols('x0:4',real=True)
    h={(a,b):sp.Function(f'h{a}{b}')(*x) for a in range(4) for b in range(a,4)}
    def hij(a,b): return h[min(a,b),max(a,b)]
    # J is antisymmetric only in its last two indices.
    J={(a,b,c):sp.Function(f'J{a}{b}{c}')(*x)
       for a in range(4) for b in range(4) for c in range(b+1,4)}
    def j(a,b,c): return 0 if b==c else (1 if b<c else -1)*J[a,min(b,c),max(b,c)]
    N=sp.Function('N')(*x); V=[sp.Function(f'V{a}')(*x) for a in range(4)]
    f=sp.Function('deltaT')(*x)
    direct=sum(j(a,b,c)*sp.diff(hij(a,b),x[c])/2
               for a,b,c in itertools.product(range(4),repeat=3))-sum(N*V[c]*sp.diff(f,x[c]) for c in range(4))
    divergence_J=sp.Matrix(4,4,lambda a,b:sum(sp.diff(j(a,b,c),x[c]) for c in range(4)))
    tau_derivative=-(divergence_J+divergence_J.T)/2
    ET=sum(sp.diff(N*V[c],x[c]) for c in range(4))
    boundary=[sum(j(a,b,c)*hij(a,b)/2 for a in range(4) for b in range(4))-N*V[c]*f for c in range(4)]
    divergence_boundary=sum(sp.diff(boundary[c],x[c]) for c in range(4))
    euler_pair=sum(tau_derivative[a,b]*hij(a,b)/2 for a in range(4) for b in range(4))+ET*f
    return {'metric_adjoint':tau_derivative,'E_T':ET,'boundary_current':boundary,
            'residual':sp.expand(direct-euler_pair-divergence_boundary),
            'wrong_T_sign_residual':sp.expand(direct-euler_pair-divergence_boundary+2*ET*f),
            'wrong_metric_half_residual':sp.expand(sum(tau_derivative[a,b]*hij(a,b)/2
                                                       for a in range(4) for b in range(4)))}


@lru_cache(maxsize=1)
def derive_model():
    c=point_context(); cv=connection_variation(c)
    g,gi,u,e,h=(c[k] for k in ('metric','inverse_metric','normal','frame','h'))
    chi,N,df=c['chi'],c['N'],c['df']; ucov=g*u; huu=(u.T*h*u)[0]
    # Generic normal variation compatible with the independent horizontal beta.
    du_cov=-ucov*huu/2+g*e*(c['beta']+e.T*h*u/2)
    du_contra=gi*du_cov-gi*h*u
    normal_residual=expanded(u.dot(du_cov)-huu/2)
    orthonormal=expanded(e.T*h*e+cv['delta_e'].T*g*e+e.T*g*cv['delta_e'])
    orthogonal=expanded(e.T*h*u+cv['delta_e'].T*g*u+e.T*g*du_contra)
    # Direct variation of u=-N dT; differentiate the normalization scalar.
    delta_norm=huu/N**2+2*u.dot(df)/N
    delta_N=-N**3*delta_norm/2
    du_T_direct=-N*df+ucov*delta_N/N
    projector=sp.eye(4)+ucov*u.T
    du_T_reference=-ucov*huu/2-N*projector*df
    beta_T=expanded(e.T*du_T_direct-e.T*h*u/2)
    C=c['C']; Cup=[sum((gi[mu,nu]*C[nu] for nu in range(4)),sp.zeros(3)) for mu in range(4)]
    J=[[[expanded(chi*sum(Cup[mu][a,b]*e[nu,a]*e[rho,b] for a in range(3) for b in range(3)))
          for rho in range(4)] for nu in range(4)] for mu in range(4)]
    V=expanded(sp.Matrix([chi*sum(Cup[mu][a,b]*c['kappa'][mu,a]*e[nu,b]
                     for mu in range(4) for a in range(3) for b in range(3)) for nu in range(4)]))
    variation_omega=expanded(chi*sum(Cup[mu][a,b]*cv['direct'][mu][a,b]
                  for mu in range(4) for a in range(3) for b in range(3))/2)
    derivative_metric=sum(J[mu][nu][rho]*c['dh'][rho][mu,nu]/2
                          for mu,nu,rho in itertools.product(range(4),repeat=3))
    boost_metric=(V.T*h*u)[0]/2
    reference_variation=expanded(derivative_metric+V.dot(du_cov)-boost_metric)
    Cnorm=sum(C[mu][a,b]*Cup[mu][a,b] for mu in range(4) for a in range(3) for b in range(3))
    inv_variation=-gi*h*gi
    hodge_direct=expanded(-chi*(sum(inv_variation[mu,nu]*C[mu][a,b]*C[nu][a,b]
                           for mu,nu in itertools.product(range(4),repeat=2)
                           for a,b in itertools.product(range(3),repeat=2))+sp.trace(gi*h)*Cnorm/2)/4)
    T=sp.Matrix(4,4,lambda mu,nu:expanded(chi*(sum(Cup[mu][a,b]*Cup[nu][a,b]
                      for a in range(3) for b in range(3))-gi[mu,nu]*Cnorm/2)/2))
    T_pair=sum(T[mu,nu]*h[mu,nu]/2 for mu,nu in itertools.product(range(4),repeat=2))
    tau_boost=-(V*u.T+u*V.T)/2
    current_direct=expanded(-chi*sum(Cup[mu][a,b]*c['delta_A'][mu][a,b]
                              for mu in range(4) for a in range(3) for b in range(3))/2)
    current_forms=[]; current_pairing=0
    # Independent color pairs a<b; J wedge delta A, with 3+1 orientation.
    for a,b in itertools.combinations(range(3),2):
        forms={tuple(i for i in range(4) if i!=mu):chi*(-1)**mu*Cup[mu][a,b] for mu in range(4)}
        current_forms.append(forms)
        current_pairing+=sum((-1)**(3-mu)*forms[tuple(i for i in range(4) if i!=mu)]
                             *c['delta_A'][mu][a,b] for mu in range(4))
    rho=c['rho']; deltaC=[]; gauge_variation=0; wrong_frame_only=0
    for mu in range(4):
        A=C[mu]+c['omega'][mu]
        deltaA=c['drho'][mu]+A*rho-rho*A
        deltaC.append(expanded(deltaA-cv['rotation_direct'][mu]-(C[mu]*rho-rho*C[mu])))
        gauge_variation+=sum(Cup[mu][a,b]*(deltaA-cv['rotation_direct'][mu])[a,b]
                             for a in range(3) for b in range(3))
        wrong_frame_only+=sum(Cup[mu][a,b]*cv['rotation_direct'][mu][a,b]
                              for a in range(3) for b in range(3))
    adjoint=adjoint_identity()
    dbeta_coefficients=[sp.diff(value,jet) for matrix in cv['direct'] for value in matrix for jet in c['dbeta']]
    residuals={
        'point_orthonormal_frame':expanded(e.T*g*e-sp.eye(3)),
        'point_unit_timelike_normal':expanded((u.T*g*u)[0]+1),
        'point_spatial_frame':expanded(e.T*g*u),
        'varied_frame_normalization':orthonormal,'varied_frame_orthogonality':orthogonal,
        'varied_normal_normalization':normal_residual,
        'all_36_connection_entries':cv['residuals'],
        'connection_antisymmetric':[expanded(a+a.T) for a in cv['direct']],
        'all_d_beta_coefficients_cancel':dbeta_coefficients,
        'normal_variation_from_lapse':expanded(du_T_direct-du_T_reference),
        'beta_from_khronon':expanded(beta_T+N*e.T*df+e.T*h*u/2),
        'omega_variation_contracts_to_J_and_V':expanded(variation_omega-reference_variation),
        'V_is_spatial':expanded(V.dot(ucov)),
        'T_variation_has_minus_NV_gradient':expanded(V.dot(du_T_direct)+N*V.dot(df)),
        'Hodge_volume_and_metric_stress':expanded(hodge_direct-T_pair),
        'metric_boost_stress_factor':expanded(sum(tau_boost[mu,nu]*h[mu,nu]/2
                     for mu in range(4) for nu in range(4))+boost_metric),
        'current_three_form_sign':expanded(current_direct-current_pairing),
        'product_rule_metric_and_T_adjoint':adjoint['residual'],
        'all_36_frame_rotation_entries':cv['rotation_residuals'],
        'simultaneous_connection_rotation':deltaC,
        'rotation_leaves_action_invariant':expanded(gauge_variation)}
    negative={
        'freeze_frame':[expanded(a-b) for a,b in zip(cv['frozen_frame'],cv['reference'])],
        'reverse_boost_sign':[sp.Matrix(3,3,lambda a,b:2*(c['kappa'][mu,a]*c['beta'][b]
                                                         -c['kappa'][mu,b]*c['beta'][a])) for mu in range(4)],
        'omit_metric_curl':[expanded(matrix.subs({b:0 for b in c['beta']})) for matrix in cv['reference']],
        'reverse_current_sign':expanded(2*current_direct),
        'reverse_E_T_sign':adjoint['wrong_T_sign_residual'],
        'wrong_metric_adjoint_half':adjoint['wrong_metric_half_residual'],
        'rotate_frame_without_A':expanded(wrong_frame_only)}
    checks={name:is_zero(value) for name,value in residuals.items()}
    checks.update({f'negative_control_{name}_detected':not is_zero(value) for name,value in negative.items()})
    return {'context':c,'connection_variation':cv,'J':J,'V':V,'T_C':T,'tau_boost':tau_boost,
            'normal_variation':du_T_direct,'beta_khronon':beta_T,
            'omega_density_variation':variation_omega,'omega_density_reference':reference_variation,
            'Hodge_density_variation':hodge_direct,'current_density_variation':current_direct,
            'current_three_forms_per_unit_volume':current_forms,'current_pairing':expanded(current_pairing),
            'functional_adjoint':adjoint,'residuals':residuals,'negative_controls':negative,
            'checks':{name:bool(value) for name,value in checks.items()}}


def serialize(value):
    if isinstance(value,sp.MatrixBase): return [[serialize(x) for x in row] for row in value.tolist()]
    if isinstance(value,dict): return {(','.join(map(str,k)) if isinstance(k,tuple) else k):serialize(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [serialize(x) for x in value]
    return str(value) if isinstance(value,sp.Basic) else value


def build_payload():
    for path,pin in ((SOURCE,SOURCE_SHA),(PROOF,PROOF_SHA),(PROJECTED,PROJECTED_SHA),(CANDIDATE,CANDIDATE_SHA)):
        if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:
            raise CovariantVariationError(f'source byte pin mismatch: {path.name}')
    baseline=json.loads(SOURCE.read_bytes())
    if canonical_digest(baseline['exact_classical_charter']['exact_action'])!=ACTION_SHA:
        raise CovariantVariationError('literal action pin mismatch')
    model=derive_model()
    if not all(model['checks'].values()): raise CovariantVariationError('covariant variation algebra failed')
    payload={'schema':SCHEMA,'baseline':{'source_sha256':SOURCE_SHA,'literal_action_sha256':ACTION_SHA},
        'proposal':{'term':'-chi/2 integral <(A_Sigma-omega) wedge star_gamma(A_Sigma-omega)>',
                    'chi':'positive mass-squared symbol, no selected value','adopted':False,
                    'A_Sigma_independent':True,'Q_comparison':'horizontal local identification'},
        'model':serialize(model),'checks':model['checks'],
        'scope':{'exact_covariant_first_variation_checked':True,'all_36_spatial_connection_entries_checked':True,
                 'metric_and_khronon_adjoint_checked':True,'normal_and_frame_not_frozen':True,
                 'arbitrary_kappa_jets_are_a_stronger_point_identity_not_a_foliation_solution':True,
                 'no_d_beta_in_horizontal_first_variation':True,
                 'global_reduction_of_differential_order_proved':False,'full_moving_gluing_chain_closed':False,
                 'positive_full_energy_proved':False,'candidate_adopted':False,'new_coefficient_selected':False,
                 'N4_JUNCTION_BENDING_pass':False,'N7_LINEAR_REDUCTION_pass':False,
                 'P4_full_same_action_pass':False,'B4_pass':False,'B5_pass':False,
                 'BF_global_quotient_closed':False,'nonlinear_stability_proved':False},
        'provenance':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (Path(__file__),TEST,PROOF,PROJECTED,CANDIDATE)}}
    payload['calculation_digest']=canonical_digest(payload)
    return payload


def validate_payload(payload):
    if not isinstance(payload,dict) or payload.get('schema')!=SCHEMA:
        raise CovariantVariationError('receipt schema mismatch')
    if payload.get('calculation_digest')!=canonical_digest({k:v for k,v in payload.items() if k!='calculation_digest'}):
        raise CovariantVariationError('receipt digest mismatch')
    if payload!=build_payload(): raise CovariantVariationError('receipt differs from trusted recomputation')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--write',nargs='?',const=OUTPUT,type=Path)
    modes.add_argument('--verify',nargs='?',const=OUTPUT,type=Path)
    args=parser.parse_args()
    if args.write:
        payload=build_payload()
        with args.write.open('x',encoding='utf-8') as stream:
            json.dump(payload,stream,sort_keys=True,indent=2,allow_nan=False); stream.write('\n')
    else:
        payload=json.loads(args.verify.read_text()); validate_payload(payload)
    print(json.dumps({'schema':SCHEMA,'checks_passed':sum(payload['checks'].values()),
                      'checks_total':len(payload['checks']),'calculation_digest':payload['calculation_digest']}))


if __name__=='__main__': main()
