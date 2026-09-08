"""Pointwise positive-real Green-energy identities on Re(s)>0.

For a real positive radial pair P,W and the equation
    (P H')' - (s**2 + q**2) W H = 0,
multiplication by conjugate(H) gives the formal Green identity
    [conjugate(H) P H']_0^IR
       = integral(P*abs(H')**2) + (s**2+q**2)*integral(W*abs(H)**2).
Assume finite integrals, zero IR flux, P(0)=1 and nonzero UV trace H0.
With K=-2*H'(0)/H0 this becomes K*abs(H0)**2/2=Ir+(s**2+q**2)*Iw.
The scalar identity uses its radial weights divided by their UV G factor,
so Kv has this SAME canonical normalization and G is kept explicit in G*Kv.

Ir,Iw,Iv,Iq below are nonnegative energy values at each s, not assumed to be
constant functions of s. The algebra verifies the real-part consequences of
that Green identity. It does not construct an admissible profile, prove global
existence or holomorphy of a DtN branch, or classify the complete scalar system.
An arbitrary positive assignment of these integrals is not a new physical
kernel. The conclusions apply only when the stated Green hypotheses hold.

For material p=sqrt(s**2+q**2), choose Re(p)>0. With s=sigma+i*tau, sigma>0,
the radicand has imaginary part 2*sigma*tau. If that part vanishes then tau=0,
and the radicand is sigma**2+q**2>0. It therefore avoids the principal square
root cut throughout this half-plane. The material algebra is expressed using
p=u+i*v, u>0; its compatibility equations with s,q are recorded, not silently
imposed on otherwise independent symbols.

Exact rational/complex witnesses below refute altered algebra (missing complex
conjugation, reversed radial sign, missing temporal energy). They are not
solutions of a radial boundary problem and cannot promote any physical gate.
No I/O, external generator, process or receipt is used in this module.
"""
from __future__ import annotations

import sympy as sp


def symbols_context() -> dict:
    positive=("sigma","Iw","H0_squared","R0_squared","Mb2","M5c","xi","G","beta","kappa_hat","Z5","u")
    s=dict(zip(positive,sp.symbols(" ".join(positive),positive=True)))
    nonnegative=("q","Ir","Iv","Iq")
    s.update(dict(zip(nonnegative,sp.symbols(" ".join(nonnegative),nonnegative=True))))
    s["tau"],s["v"]=sp.symbols("tau v",real=True)
    s["s"]=s["sigma"]+sp.I*s["tau"]
    s["p"]=s["u"]+sp.I*s["v"]
    return s


def _real(expression: sp.Expr) -> sp.Expr:
    return sp.factor_terms(sp.cancel(sp.expand_complex(sp.re(expression))))


def derive_model() -> dict:
    sy=symbols_context()
    sigma,tau,s,q,Ir,Iw,H2,R2,Mb2,M,xi,G,beta,kappa,Z,u,v,p=(sy[key] for key in (
        "sigma","tau","s","q","Ir","Iw","H0_squared","R0_squared","Mb2","M5c","xi","G","beta","kappa_hat","Z5","u","v","p"))
    Iv,Iq=sy["Iv"],sy["Iq"]
    rho=sigma**2+tau**2
    p_squared=s**2+q**2
    KT=2*(Ir+p_squared*Iw)/H2
    Kv=2*(Iv+p_squared*Iq)/R2
    GKv=G*Kv
    Pv=GKv+beta
    tensor=Mb2*(s**2+xi*q**2)+M*KT
    vector=Mb2*(s**2+q**2)+M*KT
    material=kappa+2*Z*p
    real_KT_over_s=_real(KT/s)
    real_tensor_over_s=_real(tensor/s)
    real_vector_over_s=_real(vector/s)
    real_Pv_over_s=_real(Pv/s)
    real_material=_real(material)
    expected_KT=2*sigma*(Iw+(Ir+q**2*Iw)/rho)/H2
    expected_tensor=Mb2*sigma*(1+xi*q**2/rho)+M*expected_KT
    expected_vector=Mb2*sigma*(1+q**2/rho)+M*expected_KT
    expected_Pv=2*G*sigma*(Iq+(Iv+q**2*Iq)/rho)/R2+beta*sigma/rho
    expected_material=kappa+2*Z*u
    residuals={
        "TT_Green_real_part":sp.cancel(real_KT_over_s-expected_KT),
        "tensor_denominator_real_part":sp.cancel(real_tensor_over_s-expected_tensor),
        "vector_denominator_real_part":sp.cancel(real_vector_over_s-expected_vector),
        "scalar_pivot_real_part":sp.cancel(real_Pv_over_s-expected_Pv),
        "material_Robin_real_part":sp.cancel(real_material-expected_material),
        "vector_is_tensor_at_xi_one":sp.expand(vector-tensor.subs(xi,1)),
        "scalar_G_factor_explicit":sp.expand(Pv-(G*Kv+beta)),
        "radicand_imaginary_part":sp.expand(sp.im(p_squared)-2*sigma*tau),
    }
    checks={name:value==0 for name,value in residuals.items()}
    checks.update({
        "strict_TT_positive_real":expected_KT.is_positive is True,
        "strict_tensor_positive_real":expected_tensor.is_positive is True,
        "strict_vector_positive_real":expected_vector.is_positive is True,
        "strict_scalar_pivot_positive_real":expected_Pv.is_positive is True,
        "strict_material_Robin_real_part":expected_material.is_positive is True,
        "square_root_radicand_positive_when_imaginary_zero":(sigma**2+q**2).is_positive is True,
    })
    radial_point={sigma:sp.S.One,tau:sp.S.Zero,q:sp.S.Zero,Ir:sp.Integer(2),Iw:sp.S.One,H2:sp.S.One}
    wrong_radial_KT=2*(-Ir+p_squared*Iw)/H2
    wrong_radial_value=_real(wrong_radial_KT/s).subs(radial_point)
    correct_radial_value=real_KT_over_s.subs(radial_point)
    temporal_point={sigma:sp.S.One,tau:sp.S.Zero,q:sp.S.Zero,Ir:sp.S.Zero,Iw:sp.S.One,H2:sp.S.One}
    wrong_temporal_KT=2*(Ir+q**2*Iw)/H2
    wrong_temporal_value=_real(wrong_temporal_KT/s).subs(temporal_point)
    correct_temporal_value=real_KT_over_s.subs(temporal_point)
    local_derivative=sp.I
    correct_local_energy=sp.conjugate(local_derivative)*local_derivative
    wrong_local_energy=local_derivative**2
    negative_controls={
        "missing_conjugate_destroys_nonnegative_density":correct_local_energy==1 and wrong_local_energy==-1,
        "reversed_radial_sign_fails_positive_real":bool(correct_radial_value>0 and wrong_radial_value<0),
        "missing_temporal_energy_loses_strictness":bool(correct_temporal_value>0 and wrong_temporal_value==0),
    }
    witnesses={
        "missing_conjugate":{"derivative":local_derivative,"correct_energy":correct_local_energy,"wrong_energy":wrong_local_energy},
        "reversed_radial_sign":{"substitutions":radial_point,"correct_Re_KT_over_s":correct_radial_value,"wrong_Re_KT_over_s":wrong_radial_value},
        "missing_temporal_energy":{"substitutions":temporal_point,"correct_Re_KT_over_s":correct_temporal_value,"wrong_Re_KT_over_s":wrong_temporal_value},
    }
    return {
        "symbols":sy,"s":s,"p":p,"s_modulus_squared":rho,"p_squared":p_squared,
        "KT":KT,"Kv":Kv,"GKv":GKv,"Pv":Pv,"tensor_denominator":tensor,"vector_denominator":vector,"material_denominator":material,
        "real_KT_over_s":real_KT_over_s,"real_tensor_over_s":real_tensor_over_s,"real_vector_over_s":real_vector_over_s,
        "real_Pv_over_s":real_Pv_over_s,"real_material":real_material,
        "expected_KT_over_s":expected_KT,"expected_tensor_over_s":expected_tensor,"expected_vector_over_s":expected_vector,
        "expected_Pv_over_s":expected_Pv,"expected_material":expected_material,
        "p_branch_compatibility":sp.Matrix([u**2-v**2-(sigma**2-tau**2+q**2),2*u*v-2*sigma*tau]),
        "residuals":residuals,"checks":checks,"negative_controls":negative_controls,"witnesses":witnesses,
        "scope":{
            "half_plane":"Re(s)=sigma>0; q real and nonnegative; p chosen with Re(p)>0",
            "TT_integrals":"Ir>=0, Iw>0, H0_squared>0; finite Green integrals and vanishing IR flux",
            "scalar_integrals":"Iv>=0,Iq>=0,R0_squared>0; weights normalized by their UV G; beta>0 supplies strictness even at zero abstract integrals",
            "normalization":"KT=-2H_prime(0)/H(0), Kv=-2R_prime(0)/R(0); G remains explicit in Pv=G*Kv+beta",
            "conditional_consequence":"the displayed tensor/vector denominators, scalar pivot and material Robin denominator are nonzero in this half-plane wherever the assumed Green representation exists",
            "actual_kernel_constructed":False,"global_DtN_existence_proved":False,"global_DtN_holomorphy_proved":False,
            "full_scalar_stability":False,"BF_sector_certified":False,"embedding_sector_certified":False,
            "finite_witnesses_promote_global_physics":False}}
