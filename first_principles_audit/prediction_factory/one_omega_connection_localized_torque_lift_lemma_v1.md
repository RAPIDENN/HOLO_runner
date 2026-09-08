# Localized second-order torque lift for the unadopted connection candidate

This is a prescribed-port compatibility theorem for the separate term
S_C = -chi/2 integral <(A-omega) wedge *(A-omega)>, chi>0.
It does not modify the frozen v5.2 action, assign chi, or prove a solution of
the Einstein/embedding equations. Its source is the obstruction already
localized in one_omega_bf_robin_compatibility_lemma_v1.md. In particular this
note does not infer nonlinear continuation from a positive linear response.

## 1. Signed source and perturbative order

Use a common normal coordinate n directed from the minus side to the plus
side, volume vol5=dn wedge volSigma, and outward normals -partial_n on the
plus half and +partial_n on the minus half. The bulk connection variation
is J4 wedge delta A, with J4=i_Q vol5. Consequently

    [j4]/volSigma = Q_plus,n-Q_minus,n = -sum Q_out.

With the existing generators (T_I)^J_K=epsilon_IJK, the material Green and
Robin row give sum Q_out=-kappa*y*(a cross phi). Thus the signed source in
these declared conventions is

    rho := [j4]/volSigma = kappa*y*(a cross phi).                (1)

Changing the common orientation changes the form components consistently;
one must not replace only the sign of rho in the equations below.

Let F be real and smooth with compact support on R3 and prescribe

    gamma_epsilon = -exp(2 epsilon F) dt^2 + dx^2,
    T=t, a_epsilon=epsilon grad F.                              (2)

This is interface geometry prescribed as data, not a constructed bulk
Einstein metric. Its Cartesian spatial frame e_a=partial_a has projected
SO3 connection omega=0 exactly: all spatial Gamma^a_(mu b) vanish. The
nonzero Christoffel coefficients involving two time indices do not enter
this projected connection. The scalar background is phi0=0, so metric
perturbations do not enter its first-order material equation. In the
selected conformal BPS variables and Robin branch, write

    g(p)=kappa/(kappa+2 Z p), U=g(|D|) F,
    phi_epsilon=epsilon*y*grad U+O(epsilon^2).                  (3)

All positive coefficients kappa,Z,y,chi may be left symbolic in this
statement. Formula (3) is the linear material response already derived
from the two half spaces, not a hypothesis about a nonlinear solution.
Since a0=phi0=0, the order-epsilon^2 coefficient in (1) is independent
of a2 and phi2:

    rho2 = kappa*y^2 grad F cross grad U.                      (4)

The volume and inverse-metric corrections in (2), multiplying a connection
that starts at order epsilon^2, enter the new current divergence only at
order epsilon^3. This order statement does not remove the separate metric
Euler equations of the new term.

## 2. Vanishing total charge follows from the actual source

Set W=kappa*y^2 F grad U. The multiplier g is bounded and commutes with
spatial derivatives. Therefore U belongs to H^m(R3) for every finite m;
Sobolev embedding makes U smooth. Although g(|D|)F need not be compactly
supported or Schwartz, W is smooth and compactly supported because F is.
The exact vector identities are

    rho2 = curl W, div rho2 = 0, integral_R3 rho2 dx = 0.       (5)

The last identity follows by integration by parts with compact W, not by
sampling a Fourier zero or discarding it. Spatial and internal directions
are identified by the fixed Cartesian frame of (2); (5) is a statement in
that chart, not an additional gauge law of the general theory. Rho2 is
C_c^infinity. In particular its Fourier transform is rapidly decreasing,
and its zero mean provides the quantitative bound, for the unitary Fourier
transform,

    |rho2_hat(k)| <= M1 |k|,
    M1=(2 pi)^(-3/2) integral |x| |rho2(x)| dx.                (6)

This uses exp(-i k.x)-1 and |exp(-i z)-1|<=|z|. A shifted choice of origin
also works because the total charge is zero.

## 3. Unique L2 finite-energy static orientation

For the candidate, J_Sigma=chi * C. On (2), choose the leading orientation
A_Sigma=-epsilon^2 dTheta+O(epsilon^4), so C=A_Sigma. The required BF
compatibility is d J_Sigma=-[j4] at this order. With (1), it becomes

    chi Delta Theta = rho2.                                  (7)

Define a real Lie-algebra component vector, with the three components
solved independently,

    Theta_hat(k) = -rho2_hat(k)/(chi |k|^2), k!=0,
    Theta(x) = -1/(4 pi chi) integral rho2(y)/|x-y| dy.        (8)

The value assigned to the Fourier representative at k=0 has measure zero.
It is not a physical zero-mode omission: (5)-(6) establish solvability and
integrability there. Since Delta[-1/(4 pi |x|)]=delta_0, (8) has the sign
required by (7). Using (6), for every R>0 the low-frequency estimates are

    integral_(|k|<R) |Theta_hat|^2 <= 4 pi M1^2 R/chi^2,
    E_(|k|<R) <= 2 pi M1^2 R^3/(3 chi),
    E = chi/2 integral |grad Theta|^2
      = 1/(2 chi) integral |rho2_hat(k)|^2/|k|^2.             (9)

At high frequency the rapid decay of rho2_hat proves Theta is in H^m for
all finite m. Hence (8) is smooth, L2, and has finite positive spatial
energy (strictly positive when rho2 is nonzero). The zero charge also gives
Theta=O(|x|^-2) and grad Theta=O(|x|^-3) at spatial infinity, by subtracting
1/|x| inside the convolution and differentiating the kernel away from its
compact source. If two L2 solutions exist, their difference has Fourier
transform supported at k=0 and thus vanishes as an L2 function. This proves
uniqueness in that selected space. It is not uniqueness among arbitrary
harmonic fields or boundary conditions. Energy is per time slice, not a
finite action over an infinite static time interval.

In contrast, a generic compact source with nonzero total charge has a
1/|x| tail and its potential is not L2(R3). The compact-gradient structure
in (4) supplies the missing condition; mere locality of a source would not.

## 4. Nonzero localized witness and exact flatness

The earlier localized witness takes a smooth cutoff of
F_ref=cos x+cos(2z), equal to that function on the ball of radius R=256
around x_star=(pi/2,0,pi/4), with the specified cutoff derivative bound.
For kappa=Z=1,y^2=3 the pinned Poisson estimate proves

    |rho2(x_star)| > 197/640.

Thus the compatible Theta above is not zero. This lower bound is inherited
from the independently source-bound analytic localization proof; no grid
is substituted for the cutoff argument. The periodic unlocalized reference
is only a sign and normalization diagnostic:

    rho2 = (0, (4/5) sin x sin(2z), 0),
    Theta = (0, -4/(25 chi) sin x sin(2z), 0).

It has finite cell energy, not the global finite energy proved for the
compact source in section 3.

For the actual localized Theta, let Theta_mat=sum_I Theta_I T_I and set
on the interface

    g_epsilon=exp(epsilon^2 Theta_mat),
    A_epsilon=-d g_epsilon g_epsilon^(-1).                   (10)

The Maurer-Cartan identity gives F(A_epsilon)=0 exactly, and
A_epsilon=-epsilon^2 dTheta_mat+O(epsilon^4). Therefore this construction
respects BF flatness while cancelling the specified order-epsilon^2
compatibility source. A smooth compact radial cutoff multiplying Theta
inside the exponential extends (10) as a flat connection into each half
with the common trace. That is a statement about A, not a solution for B.

The first new connection term does not change (3): A2 acting on phi1 is
third order. Its metric variation, however, can already be second order
through the derivative adjoint of omega. Consequently this construction
must not be advertised as an unforced gravity solution. It is a lift of
the particular quadratic current obstruction for prescribed ports.

## 5. Remaining obligations

This note proves a finite-energy solution of the leading sourced interface
compatibility, and an exactly flat connection realizing its leading trace.
It does not solve sourced bulk D_A B+J4=0 in a chosen global weighted domain,
the entire coupled field equations, backreaction, higher-order torque,
nonlinear existence, or retarded initial data. The RHP affine BF lift in its
own note concerns the linear zero-background-current problem and cannot be
silently reused for this quadratic sourced problem at s=0. No continuation
theorem, global stability, particle count, general N4/N7/P4 or B4/B5 gate is
promoted. The added action remains a candidate and chi stays unselected.
The companion checks algebra, source signs and normalization, and binds this
analytic lemma. Its finite identities do not replace estimates (5)-(9).
