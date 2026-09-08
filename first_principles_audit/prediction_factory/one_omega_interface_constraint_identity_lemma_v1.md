# Normal and tangential interface constraint identities

This is a local covariant identity package for the conventions of the literal
v5.2 action. It does not derive its complete moving-interface first variation.
The distinction matters: a constraint identity can prove that a candidate
normal equation is dependent once the actual Euler and gluing maps have been
identified; it cannot identify those maps by itself. N4 and N7 remain false.

## Conventions and the geometric identity

Let a timelike hypersurface Sigma carry a common Lorentz metric gamma of
signature (-,+,+,+). Choose one spacelike unit normal n from Mminus to Mplus,
and use it on both sides when defining

    Kplus/minus_ab = e_a^M e_b^N nabla_M n_N,
    pi_ab = K_ab - gamma_ab tr_gamma K,
    [X] = Xplus - Xminus,       Kbar = (Kplus + Kminus)/2.

All contractions use this same gamma. The outward normals of the two bulk
domains are nout,plus=-n and nout,minus=+n. Consequently the v5.2 equation
M sum(pi_out)=tau, with M=M5^3, has the residual

    I_ab = -M [pi_ab] - tau_ab.

Tau is the **complete** intrinsic metric Euler coefficient, normalized by
Delta Sbrane = integral sqrt(-gamma) tau^ab Delta gamma_ab/2 + other rows.
It is not an arbitrarily selected portion of the brane stress. In particular
it includes metric dependence of the constrained frame where present.

With Riemann convention R^rho_(sigma mu nu) = partial_mu Gamma^rho_(nu sigma)
- partial_nu Gamma^rho_(mu sigma) + Gamma^rho_(mu lambda) Gamma^lambda_(nu sigma)
- Gamma^rho_(nu lambda) Gamma^lambda_(mu sigma), Gauss and Codazzi for this
spacelike normal give

    G_nn = ((tr K)^2 - K:K - Rgamma)/2,
    G_nu = D^a pi_au.

The normal constraints and normal force are therefore

    Hplus/minus = M/2 [(tr Kplus/minus)^2 - Kplus/minus:Kplus/minus - Rgamma]
                  - Tnn,plus/minus,
    Fnormal = tau:Kbar - [Tnn].

The exact off-shell algebraic identity is

    Fnormal = [H] - Kbar:I.                                      (1)

Proof: the common Rgamma cancels in the jump, while

    [(tr K)^2 - K:K]
      = 2 tr(Kbar) [tr K] - 2 Kbar:[K]
      = -2 Kbar:[pi].

Thus [H] = -M Kbar:[pi] - [Tnn] = Kbar:I + Fnormal. This uses no
Einstein equation, Israel equation, Z2 symmetry, frequency division or
choice of background. Imposing both normal constraints and Israel then
implies Fnormal=0. Israel alone does not: for Kplus=a gamma, Kminus=0,
Tnn,plus=Tnn,minus=0 and tau=3 M a gamma, one has I=0 but Fnormal=6 M a^2.

The common induced metric, including its intrinsic derivatives, is essential.
If unrelated intrinsic scalar curvatures were inserted on the two sides,
[H] would acquire -M [Rgamma]/2 and (1) would require a corresponding extra
term. This package never treats discontinuous induced geometry as gluing.

## Tangential constraint and conservation identity

Use covariant derivatives compatible with the common gamma, with M constant.
Define

    E_nu,plus/minus = M D^a pi_plus/minus_au - T_nu,plus/minus,
    Ftangent_u = D^a tau_au + [T_nu].

Differentiating the definition of I gives the exact identity

    Ftangent = -D I - [E_n].                                   (2)

This is a tensor identity; the companion uses arbitrary covariant derivative
jets D_c K_ab and D_c tau_ab, symmetric in a,b. It does not silently replace
covariant derivatives by partial derivatives in a general chart. At one
point those jets may be prescribed independently subject to the displayed
symmetries and metric compatibility. Equations E_n=0 and I=0 imply the
interface conservation law (2).

For the gauged scalar sector of v5.2,

    T_nu = G (n.Omega) D_u Omega + Z5 <n.P, P_u>,
    Pi_Omega = G n.Omega + 3 Z5 <phi,n.P>/(2 Omega),
    Pi_phi = Z5 n.P,

so T_nu = Pi_Omega D_u Omega + <Pi_phi,D_A,u phi> before applying the
associated frame map. Mapping this identity to common intrinsic variables
requires the constrained variation of that map. The khronon row and the
full induced-metric Ward identity are not supplied by (2) alone.

Under reversal of the common normal together with exchange of the side
labels, Kplus becomes -Kminus, Kminus becomes -Kplus, while tau is unchanged.
Then I is unchanged, Kbar changes sign, and Fnormal and [H] change sign.
This is the consistent reversal that preserves the stated outward-normal
convention. Flipping only the Israel incidence or only a jump is a different,
incorrect identity and is detected by the negative controls.

## BF transgression and its equation-dependent normal term

On each five-dimensional side let B be an adjoint three-form and F an
adjoint two-form. In the v5.2 SO3 basis the invariant pairing is
<X,Y>=-tr_3(XY)/2=delta_IJ X^I Y^J. With LBF=<B wedge F>, integration by
parts in the connection variation gives

    Theta_BF(delta A) = -<B wedge delta A>.

For the gauge-compensated diffeomorphism delta_xi A=i_xi F, the interior
product rule for the odd-degree form B is

    i_xi(B wedge F) = i_xi B wedge F - B wedge i_xi F.

Consequently

    i_xi LBF - Theta_BF(i_xi F) = <i_xi B wedge F>.               (3)

Equation (3) is exact off shell, for a general xi, without commuting internal
matrices or setting F=0. It holds componentwise inside the invariant trace.
For normal xi the remaining four-form is proportional to the bulk B Euler
row F=0. It may therefore be removed on that equation; it must not be
silently discarded in the off-shell Green form. At B=F=0 its first
variation vanishes because it is bilinear in their perturbations.

This is the Legendre/transgression **combination**, not authorization to add
a second domain-motion term. In the fixed-reference convention the complete
bulk top form is pulled back once. Its Cartan representative i_xi L occurs
once. The BF incidence equation on the common interface remains
bplus-bminus=0; it is distinct from the outward-normal metric convention.
The independent interface connection A_Sigma is not the Levi-Civita
connection of gamma or its constrained frame.

## What the companion establishes, and what remains to be linked

The executable checks (1) for fully symbolic symmetric Kplus, Kminus and
tau with a non-diagonal Lorentz metric obtained by an invertible rational
congruence. It checks (2) with arbitrary covariant derivative jets. It checks
(3) by exterior algebra with general three-color forms and vector xi. The
tests independently reconstruct normal and tangential Einstein projections
from five-dimensional Gaussian-normal metric jets, and reconstruct BF wedge
products by full antisymmetrization. Sign, trace, curvature-jump, normal
reversal and double-transgression controls remain nonvacuous. These finite
checks support the general tensor proof above; they do not constitute a
formal proof assistant verification of the complete nonlinear action.

To identify Fnormal with the candidate's complete embedding Euler row one
still has to derive the moving pullback and its adjoint on admissible paired
embedding variations, including common metric/Omega/material/connection
traces, the natural scalar and Robin equations and the constrained delta j.
Varying two arbitrary normal displacements while freezing both bulk fields
generally violates the common-trace domain. The actual off-shell row can
contain combinations of these natural rows. No such combination is assumed
proved by this package. Likewise the expanded K/a/Robin Euler coefficients,
complete interface Ward map and relative BF gauge/domain quotient are not
constructed here.

N7 additionally requires that the linearization of that identified nonlinear
system, including constraints and gluing, reproduce the independent
all-helicity blocks and the homogeneous quotient. A pole-free reduced block
does not provide this equivalence. N5 remains a separate coupled nonlinear
BVP problem; zero harmonics and possible bifurcations are not settled by a
linear energy estimate. N4, N7, all general nonlinear/physical gates and
B4/B5 remain false in this receipt.
