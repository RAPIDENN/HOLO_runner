"""Independent GN row identities and scalar ADM reduction controls."""
from __future__ import annotations
import copy
import json
import pytest
import sympy as sp
from . import one_omega_bps_scalar_master_rows_v1 as rows


@pytest.fixture(scope="module")
def source_doc():
    return json.loads(rows.BULK.read_text())


@pytest.fixture(scope="module")
def scalar_rows(source_doc):
    return rows.derive_rows(source_doc)


def test_gn_constraints_and_scalar_row_give_master_identity(scalar_rows):
    assert set(scalar_rows['residuals']) == {
        'time_momentum_constraint','space_momentum_constraint',
        'master_identity','null_cone_identity'}
    assert all(value == 0 for value in scalar_rows['residuals'].values())
    assert all(scalar_rows['checks'].values())


def test_row_identity_does_not_invert_wave_frequency_or_null_cone(scalar_rows):
    s=scalar_rows['symbols'];F,q=s['W_freq'],s['q_mom']
    for coefficient in scalar_rows['identity_coefficients'].values():
        denominator=sp.denom(sp.cancel(coefficient))
        assert not denominator.has(F,q)
    assert sp.simplify((scalar_rows['master_operator']-
                        scalar_rows['row_combination']).subs(F,q)) == 0


def test_comoving_curvature_is_invariant_under_a_normal_coordinate_change(scalar_rows):
    s=scalar_rows['symbols'];xi=sp.Symbol('xi_normal',real=True)
    Ap=scalar_rows['background']['A_prime'];Op=scalar_rows['background']['Omega_prime']
    R=scalar_rows['curvature']
    shifted=R.subs({s['P']:s['P']+Ap*xi,s['C']:s['C']+Op*xi},simultaneous=True)
    assert sp.simplify(shifted-R) == 0
    assert sp.diff(R,s['C']) == -1/s['Omega_value']


@pytest.mark.parametrize('row', ['04','34','44','Omega'])
def test_mutated_bulk_row_is_not_hidden_by_a_claimed_success(source_doc,row):
    mutant=copy.deepcopy(source_doc)
    mutant['helicity_odes'][row] += ' + Wm(w)'
    mutant['checks']={key:True for key in mutant['checks']}
    result=rows.derive_rows(mutant)
    assert not all(result['checks'].values())
    if row in ('44','Omega'):
        assert result['residuals']['master_identity'] != 0
    else:
        name='time_momentum_constraint' if row=='04' else 'space_momentum_constraint'
        assert result['residuals'][name] != 0


def test_hamiltonian_normalization_is_checked_even_on_homogeneous_equations(source_doc):
    mutant=copy.deepcopy(source_doc)
    mutant['helicity_odes']['44']='-('+mutant['helicity_odes']['44']+')'
    result=rows.derive_rows(mutant)
    assert result['residuals']['master_identity'] != 0


def test_scalar_master_is_not_the_tensor_transport_operator(scalar_rows):
    s=scalar_rows['symbols'];Ap=scalar_rows['background']['A_prime']
    wrong=scalar_rows['master_operator']-2*Ap*scalar_rows['curvature_first']
    assert sp.simplify(wrong-scalar_rows['row_combination']) != 0


from . import verify_one_omega_bps_scalar_master_v1 as adm


@pytest.fixture(scope="module")
def scalar_adm():
    return adm.derive_model()


@pytest.fixture(scope="module")
def boundary(scalar_rows):
    return rows.derive_boundary(scalar_rows)


def test_ADM_constraints_preserve_every_radial_and_tangential_current(scalar_adm):
    m=scalar_adm;s=m['symbols']
    residual=(m['raw_L2'].xreplace(m['alpha_substitutions'])-m['reduced_L2']-
              adm.radial_derivative(m['F_rad']+m['F_grad'],s)-
              adm.divergence(m['tangential_boundary_current'],s)-m['background_remainder'])
    assert sp.expand(residual) == 0
    assert all(m['checks'].values())
    assert len(m['checks']) == 20
    assert m['scope']['beta_reconstruction_at_null_or_zero_slice_momentum_certified'] is False


def test_erasing_gradient_boundary_current_breaks_density_identity(scalar_adm):
    m=scalar_adm;s=m['symbols']
    missing=adm.radial_derivative(m['F_grad'],s)
    assert sp.simplify(missing) != 0
    assert sp.simplify(m['UV_gradient_density']) != 0
    assert sp.simplify(-2*m['F_rad_UV']+m['wall_tension_L2']) == 0
    assert sp.simplify(-m['F_rad_UV']+m['wall_tension_L2']) != 0


def test_full_vector_constraint_retains_information_on_null_slice_momentum(scalar_adm):
    m=scalar_adm;s=m['symbols']
    covector=sp.Matrix([-1,0,0,1])
    assert (covector.T*s['eta']*covector)[0] == 0
    sub=dict(zip(s['grad_zeta_p'],covector))
    sub.update({x:0 for x in s['grad_alpha']})
    force=m['momentum_vector'].subs(sub).applyfunc(sp.simplify)
    assert any(component != 0 for component in force)
    assert sp.simplify((covector.T*force)[0]) == 0
    assert not m['alpha_solution'].has(*s['hess_beta'])


def test_bulk_scalar_kinetic_sign_and_BPS_pump(scalar_adm):
    m=scalar_adm;s=m['symbols']
    kinetic=m['reduced_L2']
    weight=s['G']*s['Op']**2/s['Ap']**2
    assert sp.simplify(sp.diff(kinetic,s['zeta_p'],2)+sp.exp(4*s['A'])*weight) == 0
    assert sp.simplify(sp.diff(kinetic,s['grad_zeta'][0],2)-sp.exp(2*s['A'])*weight) == 0
    assert sp.simplify(sp.diff(kinetic,s['grad_zeta'][3],2)+sp.exp(2*s['A'])*weight) == 0
    assert m['pump_BPS_squared'] == s['G']*s['omega']**5


def test_ADM_master_matches_GN_friction_without_importing_its_equation(scalar_adm,scalar_rows):
    m=scalar_adm;s=m['symbols'];r=scalar_rows['symbols']
    box_eigenvalue=sp.Symbol('box_eigenvalue',real=True)
    direct=m['master_equation_BPS'].subs({s['zeta_pp']:0,s['zeta_p']:0})
    assert sp.simplify(direct-sp.exp(-2*s['A'])*m['box_zeta']) == 0
    # Differentiate the independent divergence form before imposing the BPS ratio.
    expected=adm.radial_derivative(sp.exp(4*s['A'])*s['G']*s['omega']**2*s['zeta_p'],s)
    expected+=sp.exp(2*s['A'])*s['G']*s['omega']**2*m['box_zeta']
    assert sp.expand(expected-m['master_flux']) == 0
    assert sp.diff(m['master_equation_BPS'],s['zeta_p']) == 6*s['Ap']
    assert scalar_rows['checks']['master_identity']


def test_scalar_zero_norm_comes_from_radial_measure(scalar_adm):
    m=scalar_adm;s=m['symbols'];x=sp.Symbol('x',positive=True)
    a,G,k=s['a'],s['G'],s['k']
    # z-measure: 2*G*Omega^5*dz = 2G/k*Omega^3 exp(a Omega^2)*dOmega.
    primitive=G*sp.exp(a*x**2)*(a*x**2-1)/(k*a**2)
    assert sp.simplify(sp.diff(primitive,x)-2*G*x**3*sp.exp(a*x**2)/k) == 0
    assert sp.simplify(primitive.subs(x,1)-primitive.subs(x,0)-m['scalar_norm']) == 0
    assert m['conformal_EH_coefficient_residual'] == 0


def test_boundary_response_keeps_canonical_bulk_and_local_contact_separate(boundary):
    assert all(boundary['checks'].values())
    H=boundary['response_matrix'];s=boundary['symbols']
    assert H == H.T
    assert sp.diff(H[0,1],s['K_v']) > 0
    assert sp.simplify(H[0,0]+H[0,1]) != 0
    assert not sp.simplify(H[0,0]+H[0,1]).has(s['K_v'])
    assert sp.simplify(H[1,1]+H[0,1]+s['beta']) == 0
    assert not boundary['scope']['moving_embedding_equations_certified']


def test_direct_four_by_four_canonical_momentum_counts_off_diagonal_twice(scalar_rows,boundary):
    s=scalar_rows['symbols'];M,G=s['M5c'],s['G'];F,q=s['W_freq'],s['q_mom']
    e,P,E,Pp,Ep,D=sp.symbols('eps P E Pp Ep D',real=True)
    eta=sp.diag(-1,1,1,1);p=sp.Matrix([-F,0,0,q])
    h=2*P*eta-2*E*p*p.T;hp=2*Pp*eta-2*Ep*p*p.T
    a=boundary['A_prime_UV'];Wp=G*a
    def first(x):
        if isinstance(x,sp.MatrixBase):return x.applyfunc(first)
        x=sp.expand(x);return x.coeff(e,0)+e*x.coeff(e,1)
    gamma=eta+e*h;inv=eta-e*eta*h*eta
    Kcov=a*gamma+e*hp/2
    Ktrace=first(sp.trace(inv*Kcov))
    vol=1+e*sp.trace(eta*h)/2
    pi=first(M*vol*(Ktrace*inv-inv*Kcov*inv)/2)
    W=-3*M*a
    J=first(-2*pi-(W+e*Wp*D)*vol*inv).applyfunc(lambda x:sp.expand(x).coeff(e,1))
    Jp=sp.expand(sum(J[i,j]*sp.diff(h[i,j],P) for i in range(4) for j in range(4)))
    Je=sp.expand(sum(J[i,j]*sp.diff(h[i,j],E) for i in range(4) for j in range(4)))
    d=F**2-q**2
    assert sp.simplify(Jp+24*M*Pp+6*M*d*Ep+8*Wp*D) == 0
    assert sp.simplify(Je+2*d*(3*M*Pp+Wp*D)) == 0
    assert sp.simplify(Je.subs(Pp,-Wp*D/(3*M))) == 0


def test_rehashed_scalar_receipt_cannot_delete_the_local_Z_contact():
    payload=adm.build_payload()
    assert len(payload['checks']) == 30
    assert payload['decision']['canonical_GN_scalar_boundary_response_derived']
    assert not payload['decision']['global_spectrum_or_stability_certified']
    mutant=copy.deepcopy(payload)
    mutant['boundary']['response_matrix'][0][0]='-G*K_v'
    mutant['calculation_digest']=adm.canonical_digest({k:v for k,v in mutant.items() if k!='calculation_digest'})
    with pytest.raises(adm.ScalarMasterError,match='fresh derivation'):
        adm.validate_payload(mutant)
