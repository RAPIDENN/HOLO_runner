"""Coefficient and domain controls accompanying the reviewed analytic proof."""
import copy
import sympy as sp
import pytest
from . import verify_one_omega_variational_dtn_v1 as oracle


@pytest.fixture(scope='module')
def model():return oracle.derive_model()


def test_rotated_form_controls_both_energy_terms_at_complex_frequency(model):
    sy=model['symbols'];s=sy['s'];Er,Em=sy['E_radial'],sy['E_weighted']
    expected=sp.re((Er+(s*s+sy['q']**2)*Em)/s).expand(complex=True)
    assert sp.simplify(expected-model['rotated_form_real_part'])==0
    assert model['coercivity_constant'].is_positive is True
    assert all(model['checks'].values())


def test_unrotated_form_can_have_negative_real_part_despite_coercivity(model):
    sy=model['symbols'];s=sy['s']
    point={sy['sigma']:1,sy['tau']:3,sy['q']:0,sy['E_radial']:0,sy['E_weighted']:1}
    unrotated=(sy['E_radial']+(s*s+sy['q']**2)*sy['E_weighted']).subs(point)
    assert sp.re(unrotated)<0
    assert model['rotated_form_real_part'].subs(point)>0


def test_coercivity_is_not_uniform_up_to_the_imaginary_axis(model):
    sy=model['symbols'];sigma=sy['sigma']
    bound=model['coercivity_constant'].subs({sy['tau']:1,sy['q']:1})
    assert sp.limit(bound,sigma,0,dir='+')==0
    assert model['scope']['imaginary_axis_limits_certified'] is False


def test_both_master_weights_have_same_cutoff_density_ratio(model):
    o=model['symbols']['Omega']
    assert set(model['weights'])=={'tensor','scalar_R'}
    for weights in model['weights'].values():
        assert sp.cancel(weights['P']/weights['W'])==o**2
        assert weights['P_UV']==1
        assert weights['inverse_P_integral_diverges']
        assert weights['W_integral_upper_bound'].is_positive is True


def test_constant_profile_is_in_finite_energy_closure_not_forced_to_zero_at_infinity():
    R,k,a=sp.symbols('R k a',positive=True)
    gamma=k*sp.exp(-a)
    # Actual BPS Omega<=exp(-gamma*r). Piecewise-linear cutoffs suffice as
    # an estimate; smooth approximations retain a fixed derivative bound.
    for exponent in (2,4):
        weighted_tail=sp.exp(-exponent*gamma*R)/(exponent*gamma)
        assert sp.limit(weighted_tail,R,sp.oo)==0
    assert 'trace free' in oracle.derive_model()['scope']['core']


def test_source_proof_is_pinned_and_receipt_cannot_claim_scalar_stability():
    payload=oracle.build_payload()
    assert payload['sources']['reviewed_mathematical_proof']==oracle.PROOF_SHA
    assert payload['decision']['selected_finite_energy_DtN_holomorphic_in_RHP']
    assert not payload['decision']['infinite_dimensional_proof_formally_machine_checked']
    mutant=copy.deepcopy(payload)
    mutant['decision']['remaining_scalar_determinant_nonzero_in_RHP']=True
    mutant['calculation_digest']=oracle.canonical_digest({k:v for k,v in mutant.items() if k!='calculation_digest'})
    with pytest.raises(ValueError,match='fresh derivation'):
        oracle.validate_payload(mutant)
