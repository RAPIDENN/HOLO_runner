# BF/Robin compatibility and a second-order prescribed-port obstruction

This result is for the literal v5.2 action and its displayed smooth interface
conditions, with nonzero kappa*y. It is a necessary compatibility consequence,
not a modification of that action. It neither proves inconsistency of every
solution nor supplies a complete Dirac-rank computation. The collinear
prescribed-port sector can satisfy the condition. All broad gates stay false.

## 1. Boundary integrability of the connection Euler equation

In an SO(3) orthonormal frame use (T_I)^J_K=epsilon_IJK, so
tr(T_I T_J)=-2 delta_IJ. The gauged scalar kinetic density is
-Z P_M.P^M/2, P_M=D_A,M phi+3 phi partial_M log Omega/2. Direct variation
of the normal connection gives the current

    Q_I,out = -Pi_phi,out . (T_I phi),   Pi_phi,out=Z P_out.       (1)

The conformal mixing contributes no independent torque: phi.T_I phi=0.
The connection equation from the BF action is D_A B+J4=0, with J4 the
four-form dual to this matter current (orientation included).

Transport this equation to the common bundle Q with each iota and pull it
back to Sigma. Covariant exterior derivative commutes with these operations:

    D_A_Sigma b_plus+j_plus=0,
    D_A_Sigma b_minus+j_minus=0.

The literal interface uses a common A_Sigma and b_plus-b_minus=0. Therefore
j_plus-j_minus=0. In common-normal versus outward-normal conventions this
is exactly vanishing sum of the transported outgoing currents (1). An
overall change of surface orientation changes both signs, not this equation.
This uses the gluing on Sigma as a smooth identity, including its tangential
derivatives, not merely equality of b at one isolated point.

The natural material equation is

    sum_out Pi_phi + kappa (phi_H-y a)=0.

Take its contraction with T_I phi_H and use antisymmetry. It follows that

    sum_out Q_I = -kappa*y a.(T_I phi_H).

With the specified generators, a.(T_I phi_H)=(a cross phi_H)_I. Consequently

    kappa*y != 0  ==>  a cross phi_H = 0.                      (2)

This is a **geometric**, gauge-invariant alignment condition: its squared
norm is |a|^2 |phi_H|^2-(a.phi_H)^2 in H_(gamma,T). Common changes of frame
cannot turn a nonzero norm into zero. The invariant inner product and j
transport preserve (1). Horizontal frame/metric variation changes metric
Euler coordinates; it does not add a connection current to the literal
intrinsic action. S_R has no A_Sigma argument, and A_Sigma is independent
of the Levi-Civita/frame connection. No intrinsic delta S/delta A_Sigma
term is present to absorb this outgoing torque. The cancellation of a
passive frame-representative Ward identity is a different statement.

The result is a compatibility of the displayed bulk, flux and Robin rows.
It remains necessary for any completion which keeps those rows unchanged.
It is not inferred merely from a BF homotopy, from rank of a linear Hessian,
or by identifying A_Sigma with a geometric connection.

## 2. Why the vacuum linearization does not see (2)

At the selected background a0=phi0=0, take any C2 family

    a(epsilon)=epsilon a1+epsilon^2 a2/2+o(epsilon^2),
    phi(epsilon)=epsilon phi1+epsilon^2 phi2/2+o(epsilon^2).

Then

    a(epsilon) cross phi(epsilon)
       = epsilon^2 (a1 cross phi1)+o(epsilon^2).                (3)

Thus a1 cross phi1=0 is necessary for continuation. Neither a2 nor phi2
can repair a nonzero coefficient in (3). The first variation of (2) at
this background is zero, so a linear boundary-response check alone misses it.

The Jacobian of (a,phi)->a cross phi has rank zero at the origin and rank
two on its aligned, nonzero locus. Its three written components have
reducibility relations a.(a cross phi)=phi.(a cross phi)=0. This is the rank
of this algebraic map only; it must not be relabelled as the complete
Hamiltonian/Dirac constraint rank. Nor does this lemma assert that every
solution of the full linearized Einstein system violates (3).

## 3. An explicit two-direction prescribed-port witness

The material response is fixed by the actual undeformed BPS background.
In conformal coordinates g=Omega^2 eta_5, set psi=Omega^(3/2) phi. Then
P=Omega^-3/2 D_A psi, sqrt(-g)=Omega^5 and the material action becomes

    -Z/2 int (D_A psi)^2 - Z m^2 int V4(|psi|).

This cancellation is exact, including the full V4. At psi0=0, V4 starts
at fourth amplitude order and its Euler derivative at third order. The
linear static equation in each conformal half-space z_radial>=0 is therefore
Laplace's equation. For a tangential Fourier mode of modulus p>0, the
solution with finite radial energy per Fourier mode and boundary value c is
c exp(-p z_radial).
Its sum of outward canonical momenta is 2 Z p c. Robin gives

    phi1(k)=kappa*y/(kappa+2 Z |k|) a1(k),                    (4)

because Omega_Sigma=1. This is derived from the decaying solution and the
two outgoing normals, not fitted to numerical DtN samples.

A first-order prescribed lapse source log N=epsilon[cos x+cos(2z)] has

    a1=(-sin x, 0, -2 sin(2z)).

Here x,z are tangential coordinates; z_radial denotes the bulk coordinate.
Possible first-order metric or connection perturbations do not alter the
linear material operator about phi0=0: their products with phi1 enter the
next order. The construction specifies a material port and traces; it does
not claim this imposed metric source solves the coupled Einstein problem.
For the frozen kappa=Z=1 and y^2=3, the response gains in (4) are 1/3 and
1/5 for the two different wave numbers. Hence

    (a1 cross phi1)_y = 4 y sin x sin(2z)/15.                 (5)

At x=pi/2,z=pi/4 this equals 4y/15, and the current compatibility residual
-kappa*y(a1 cross phi1)_y equals -4/5. Each mode separately is collinear
and satisfies this necessary condition; their two-direction combination
does not. Its violation is the epsilon^2 coefficient, not a finite-amplitude
numerical error. By (3) there is **no C2 continuation of these prescribed
port data and their response** satisfying all the unchanged BF, gluing and
Robin rows. Higher full-V4 terms and second-order corrections cannot remove
that coefficient.

This does not refute the upstream fixed-direction scalar N8 lift. It shows
why that lift and a pole-free unrestricted linear response cannot be promoted
to arbitrary multidirectional nonlinear material ports. The selected linear
energy and RHP receipts remain statements about their displayed linear
operator; their equivalence to a regular, unrestricted nonlinear solution
space has not been proved.

## 3b. A spatially localized, finite-energy witness

The sinusoidal reference is bounded but is not L2 on all of R3. This does not
limit the obstruction to periodic data. The response multiplier admits the
positive Poisson-mixture representation

    g(p)=kappa/(kappa+2Zp)
        = integral_0^infinity kappa exp(-kappa t) exp(-2Ztp) dt,
    P_u(x)=u/[pi^2(u^2+|x|^2)^2],   integral_R3 P_u=1.

The mixture kernel K=integral kappa exp(-kappa t) P_(2Zt) dt is nonnegative,
has L1 norm one, and acts by absolutely convergent convolution on bounded
functions. Thus it also defines the periodic reference response without
incorrectly calling that reference an L2 field. Direct radial integration
and (u^2+r^2)^2>=r^4 give

    integral_(|x|>R) P_u <= 4u/(pi R),
    integral_(|x|>R) K <= 8Z/(pi kappa R).                    (6)

Center the cutoff at x*=(pi/2,0,pi/4). Choose eta_R smooth, between zero and
one, equal to one on B_R(x*), zero outside B_(2R)(x*), and with
|grad eta_R|<=2/R. One concrete construction is to convolve the uniform
probability density on [9/8,15/8] with a smooth probability mollifier of
radius strictly less than 1/8; call the resulting function b. It has integral
one, support inside (1,2), and maximum at most 4/3. Set eta(r)=1-int_1^r b
with the constant extensions and eta_R(x)=eta(|x-x*|/R). The plateau near
r=0 removes the radial-coordinate singularity and gives eta_R in C_c^infty.

Set F_R=eta_R (cos x+cos(2z)), a_R=grad F_R and phi_R=y K*a_R. Then a_R=a1
on B_R(x*), including at x*, and, for R>=1,

    ||a_R-a1||_infinity <= sqrt(5)+4/R < 7.

For kappa=Z=1, (6) bounds the difference of the material responses at x* by
56y/(pi R), and the difference of cross products by 56 sqrt(5)y/(pi R).
With R=256, pi>3 and sqrt(5)<9/4 imply that this last error is strictly less
than 21y/128. Equation (5) therefore leaves a strictly positive y-component:

    (a_R cross phi_R)_y(x*) > (4/15-21/128)y = 197y/1920,
    |sum Q_out,y(x*)| > 197/640,                              (7)

using kappa=1,y^2=3. No numerical quadrature, chosen favorable cutoff sample
or unproved limiting interchange enters this lower bound. The verifier
checks the Poisson normalization and pointwise tail majorant, the mixture
integral and every rational constant in (6)-(7).

This localized linear response belongs to the stated energy domain.
F_R is smooth and compactly supported, so

    phi_hat_R(xi)=y g(|xi|) i xi F_hat_R(xi)

belongs to H^s for every finite s and is O(|xi|) near xi=0. Its half-space
extension psi_hat_R(r,xi)=exp(-r|xi|) phi_hat_R(xi) satisfies

    int_0^infinity int_R3 (|partial_r psi_R|^2+|grad_x psi_R|^2)
      = int_R3 |xi| |phi_hat_R|^2 < infinity,
    int_0^infinity ||psi_R||_L2^2 dr
      = 1/2 int_R3 |phi_hat_R|^2/|xi| < infinity,

with a unitary Fourier convention. The first-order metric/lapse perturbation
can be prescribed smoothly with this compact boundary trace. As before,
this is a material port, not a solution of the coupled Einstein constraints.
Equations (3) and (7) exclude its C2 continuation under the unchanged rows.
The obstruction now has a spatially localized witness of finite energy per
instant. No finite action over an infinite time interval is asserted.

## 4. Repair obligation, not a silent change of model

A repair that retains BF must account for the torque in its interface current
balance. For example, if a *new* intrinsic connection current modified the
flux equation to b_plus-b_minus=B_Sigma, subtracting the bulk equations would
require D_A_Sigma B_Sigma+(j_plus-j_minus)=0. The literal action has no such
term. Adding one changes the action, its Euler equations and its stability
obligations; no such repair is adopted or certified here. Restricting all
ports to (2) instead changes the admissible data class and must be stated.
Changing orientation, dropping the condition, or calling a physical angle a
passive frame rotation does not repair the same equations.

The verifier checks the generator normalization, the current from the
literal kinetic term, the Robin contraction, frame-invariant norm, exact
second-order expansion, algebraic ranks and the decaying-mode response.
Independent tests use explicit cross products and direct half-line energy,
plus mismatched momentum gains and favorable-promotion mutants. These support
the analytic implication above without claiming a complete proof assistant
verification, a solution of nonlinear gravity or failure of all solutions.
