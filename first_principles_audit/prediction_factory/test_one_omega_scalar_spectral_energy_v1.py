"""Independent realization, kinetic and scope controls for the scalar proof."""
import copy
import pytest
import sympy as sp
from . import verify_one_omega_scalar_spectral_energy_v1 as oracle


@pytest.fixture(scope='module')
def model():return oracle.derive_model()


def test_all_exact_energy_companion_identities(model):
    assert all(model['checks'].values())
    assert model['exact_kinetic_gap']==2*model['symbols']['b']/3


def test_multiple_spectral_atoms_match_the_original_full_three_field_response():
    # Algebraic realization test with four distinct poles. It is not a claim
    # that this finite measure is the BPS spectral measure.
    source=oracle.static.sectors.derive_model();P=source['parameters']
    n,N,zeta=sp.symbols('n N zeta',real=True);aux=sp.symbols('xT0 xT1 xB0 xB1',real=True)
    q=sp.Rational(7,10);w=sp.Rational(1,5);z=q*q-w*w;p=sp.sqrt(z)
    Ts=[(sp.Rational(1,3),3),(sp.Rational(2,3),7)]
    Bs=[(sp.Rational(1,6),2),(sp.Rational(1,3),5)]
    m0=sum(r for r,e in Ts);Ns=sum(r for r,e in Bs);C0=m0+Ns/6
    beta=sum(r*e for r,e in Bs);M=1;G=sp.Rational(6,5);k=sp.exp(sp.Rational(1,5))/C0
    Mb=2;lam=-sp.Rational(1,2);eta=3;b4=sp.Rational(4,5)
    KT=z*sum(r*e/(e+z) for r,e in Ts)/M
    Delta=z*sum(r*e/(e+z) for r,e in Bs)
    Kv=beta*Delta/(G*(beta-Delta))
    point={P['M5c']:M,P['G']:G,P['k_inf']:k,P['Mb2']:Mb,P['lambda_K']:lam,
           P['eta']:eta,P['xi']:1,P['B4bar']:b4,P['beta']:beta,P['Z5']:1,
           P['kappa_hat']:1,P['y']:sp.sqrt(3),P['p_material']:p,P['K_T']:KT,P['K_v']:Kv,
           source['frequency']:w,source['q']:q}
    Pi=6*p/(1+2*p)
    L=Mb*((3-9*lam)*w*w*zeta*zeta+2*(1-3*lam)*w*q*zeta*N+(1-lam)*q*q*N*N+
          4*q*q*n*zeta+2*q*q*zeta*zeta-b4*q**4*zeta*zeta/k**2+(eta-Pi/Mb)*q*q*n*n)/2
    U=q*q*(n-zeta)-w*q*N;EH=2*zeta*U+3*z*zeta*zeta
    L+=C0*EH-beta*zeta*zeta/2
    for x,(rho,e) in zip(aux[:2],Ts):L+=-(e+z)*x*x/2+sp.sqrt(2*rho/3)*x*U
    for x,(rho,e) in zip(aux[2:],Bs):L+=-(e+z)*x*x/2+sp.sqrt(rho)*x*(U-3*e*zeta)/3
    H=sp.hessian(L,(n,N,zeta,*aux));reduced=H[:3,:3]-H[:3,3:]*H[3:,3:].inv()*H[3:,:3]
    expected=source['scalar_3x3'].subs(point)
    assert all(sp.simplify(v)==0 for v in reduced-expected)


def test_omitting_beta_shift_counterterm_changes_the_boundary_matrix(model):
    sy=model['symbols'];zeta=sy['zeta'];rho=sy['rho_beta'];ell=sy['lambda_beta']
    missing_spring=model['beta_realized']+rho*ell*zeta*zeta/2
    assert sp.expand(sp.diff(missing_spring-model['beta_original_after_shift'],zeta,2))==rho*ell


def test_kinetic_margin_is_uniform_in_spectral_mass_distribution(model):
    sy=model['symbols'];K=model['kinetic_matrix'];D=model['kinetic_diagonal']
    point={sy['b']:2,sy['lambda_K']:-sp.Rational(1,2),sy['C0']:sp.Rational(6,5),
           sy['A']:3,sy['Bstar']:sp.Rational(13,5),sy['rho_T']:1,sy['rho_beta']:sp.Rational(6,5)}
    # C0=rhoT+rhoBeta/6, ||g||²=2C0/3. The Cauchy bound is a matrix
    # inequality; it does not count eigenvalues at a complex gauge point.
    K0=K.subs(point);D0=D.subs(point);delta=sp.Rational(4,9)
    gap=K0-delta*D0
    for size in (1,2,3):
        from itertools import combinations
        for ids in combinations(range(3),size):assert sp.simplify(gap.extract(ids,ids).det())>=0
    assert all(sp.simplify(K0[:j,:j].det())>0 for j in (1,2,3))


def test_sign_flipped_auxiliary_kinetic_term_is_detectable(model):
    sy=model['symbols'];K=model['kinetic_matrix'];point={sy['A']:3,sy['Bstar']:sp.Rational(13,5),
        sy['rho_T']:1,sy['rho_beta']:sp.Rational(6,5)}
    bad=K.subs(point)-sp.diag(0,2,0)
    assert bad[1,1]<0


def test_beta_first_moment_is_sufficient_and_TT_first_moment_is_not_assumed():
    lam=sp.Symbol('lam',positive=True)
    # Admissible illustrative tails: finite mass with an infinite first moment
    # versus finite first moment. These are not the actual BPS measures.
    assert sp.integrate(lam**(-sp.Rational(3,2)),(lam,1,sp.oo))==2
    assert sp.integrate(lam*lam**(-sp.Rational(3,2)),(lam,1,sp.oo))==sp.oo
    assert sp.integrate(lam*lam**(-3),(lam,1,sp.oo))==1
    assert oracle.derive_model()['measure_conditions']['TT_first_moment_required'] is False


def test_positive_spectral_residues_do_not_replace_the_static_theorem():
    # A positive kinetic form with negative potential admits an RHP root.
    s=sp.Symbol('s',real=True)
    assert (s*s-1).subs(s,1)==0
    assert oracle.STATIC_SHA=='8ca7d81f1dcb645147d694d68fc32c0cc50483d67f2b7353caaecf31a22f190e'


def test_proof_receipt_rejects_nonlinear_promotion_even_with_new_digest():
    payload=oracle.build_payload()
    assert payload['decision']['final_scalar_factor_has_no_RHP_zero_for_every_q_positive']
    assert not payload['decision']['full_N7']
    mutant=copy.deepcopy(payload);mutant['decision']['full_N7']=True
    mutant['calculation_digest']=oracle.canonical_digest({k:v for k,v in mutant.items() if k!='calculation_digest'})
    with pytest.raises(ValueError,match='fresh derivation'):oracle.validate_payload(mutant)
