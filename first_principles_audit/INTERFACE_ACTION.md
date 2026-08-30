# From the corrected bulk to an interaction

The geometry-preserving completion supplies a canonical scalar `chi` and a
healthy gauge-invariant scalar/metric carrier.  On the monotonic background a
local superpotential exists,

```text
W(chi(u)) = -6 A_u(u),        W_chi = chi_u,
V(chi) = W_chi^2/2 - W^2/3.
```

For the scalar curvature perturbation, convention-dependent overall factors
do not affect the radial shape problem.  Its positive weights are

```text
epsilon_ED(u) = -A_uu/A_u^2,
p(u) = exp(4 A) epsilon_ED,
w(u) = exp(2 A) epsilon_ED,
-d_u[p d_u f_n] = m_n^2 w f_n.
```

Positivity of `epsilon_ED` follows from the corrected background equation
`A_uu = -chi_u^2/6 < 0`.  This establishes a ghost-free carrier on the
certified interval.  It does not select its boundary conditions.  In
particular, a constant massless mode exists for a Neumann--Neumann completion,
whereas Dirichlet, Robin, or boundary-potential completions can remove or lift
it.  A long-range force is therefore an allowed branch, not yet a prediction.

## Minimal four-dimensional interface

After a physical mode `varphi` has been selected and canonically normalized,
the most economical local interaction basis is

```text
S4 = integral sqrt(-g) [
       M_Pl^2 R/2 - (partial varphi)^2/2 - U(varphi)
       - B_F(varphi) F^2/4
     ] + S_m[A_m(varphi)^2 g, Psi],

ln A_m = beta varphi/M_Pl + ...,
B_F    = 1 + d_e varphi/M_Pl + ... .
```

QCD and fermion masses require their own coefficients (`d_g`, `d_mi`).  At
linear order the scalar equation contains

```text
box varphi = U_varphi - (beta/M_Pl) T
             + (d_e/4 M_Pl) F_mu_nu F^mu_nu + ... .
```

For two nonrelativistic, universally coupled test masses this basis gives the
conditional Yukawa form

```text
V_12(r) = -G m1 m2/r [1 + 2 beta^2 exp(-m_varphi r)].
```

The word *conditional* matters: the bulk fixes neither `beta` nor
`m_varphi` until the boundary completion, gravitational normalization, and
matter localization are specified.  Likewise, four-dimensional Maxwell theory
is conformally invariant, so a universal metric coupling alone does not fix an
atomic-clock signal.  Clock comparisons need the independent electromagnetic,
QCD, and mass coefficients.

## Forward equations to freeze before data

For a homogeneous cosmological branch,

```text
3 M_Pl^2 H^2 = rho_m + dot(varphi)^2/2 + U,
ddot(varphi) + 3 H dot(varphi) + U_varphi = -(beta/M_Pl) rho_m,
dot(rho_m) + 3 H rho_m = (beta/M_Pl) dot(varphi) rho_m.
```

For a weak, static source,

```text
(nabla^2 - m_varphi^2) varphi = (beta/M_Pl) rho,
a_varphi = -(beta/M_Pl) grad(varphi).
```

For electromagnetic metrology,

```text
delta ln(alpha_EM) = -d_e delta(varphi)/M_Pl,
```

with clock-ratio sensitivities additionally depending on `d_g` and `d_mi`.
These equations define the later prospective tests; no observational fit is
part of the present derivation.

## Evidence boundary

Achieved here: a geometry-derived, positive scalar carrier and the complete
lowest-order interaction basis it may inhabit.

Not achieved here: a unique force law, a numerical coupling strength, a
laboratory interaction, or a detection.  Those require a preregistered boundary
and matter model followed by genuinely out-of-sample comparison.
