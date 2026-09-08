# Moving scalar Green form and normal Legendre term

This lemma concerns the gauged scalar part of the literal v5.2 action, with
Omega>0, G>0 and Z>0. It is exact off shell, for arbitrary smooth fields and
compactly supported admissible variations. It does not solve the gravitational
junction, supply all frame/Robin Euler rows, or promote N4/N7/P4/B4/B5.

## 1. Local normal momentum of the literal scalar density

Let n be a unit spacelike normal. Set q=(Omega,phi^1,phi^2,phi^3), and write
v=(n.dOmega,n.D_A phi), with arbitrary covariant tangential first jets t_mu.
The internal SO(3) inner product is Euclidean. At a point, the scalar density
per invariant volume is

    L = -1/2 C_AB (v^A v^B + gamma^{mu nu} t_mu^A t_nu^B) - V(q),
    C_00 = G + 9 Z |phi|^2/(4 Omega^2),
    C_0a = 3 Z phi_a/(2 Omega),    C_ab = Z delta_ab,
    V = U(Omega) + Z m^2 Omega^-5 V4(Omega^(3/2)|phi|),
    V4(r) = r^4/(2 sqrt(1+r^4)).

The normal Green momentum, including its sign in delta S, is p=-C v.
Thus p_Omega=-(G v_Omega+3Z phi.P_n/(2Omega)) and p_phi=-Z P_n,
where P_n=v_phi+3 phi v_Omega/(2Omega). These are minus the outward Pi
used in the charter. They include the Omega/material mixed term.
Direct inverse-metric variation gives

    T_nn = v^T C v + L = L - p.v.                       (1)

There is no assumption that tangential derivatives vanish, no radial ansatz,
and no replacement of V4 by its quartic approximation. A generic tangent
Lorentz frame suffices because all terms in (1) are scalar contractions.
The connection occurs inside D_A phi. This is the scalar Green summand;
variations of A and the BF current are additional summands, not discarded.

Changing field coordinates to psi=Omega^(3/2) phi gives

    C_new=diag(G,Z Omega^-3,Z Omega^-3,Z Omega^-3),
    C_old=J^T C_new J,   v_new=J v_old,
    p_old=J^T p_new,   Delta q_new=J Delta q_old.

Hence both p.Delta q and L-p.v are invariant. This is a normal flux
coordinate change, not an instruction to omit the mixed momentum.

## 2. Why the moving term is L-p.v

For clarity first take a first-order one-dimensional density L(x,q,q') and
an interval whose endpoint moves at speed f. Differentiate the integral
before performing integration by parts. With material trace variation
Delta q=delta q+f q', the endpoint contribution is exactly

    p.delta q + f L = p.Delta q + f (L-p.q').           (2)

The endpoint incidence (upper +, lower -) multiplies the whole expression.
The multicomponent proof is identical. In normal coordinates the same local
calculation gives the scalar part of a hypersurface boundary form, with the
invariant measure and tangential currents retained. Equation (1) identifies
its normal Legendre summand with the normal stress. This reasoning does not
apply a first-order scalar formula to Einstein-Hilbert without GHY.

An independent fixed-reference calculation prevents double transgression.
Let x_epsilon(y)=y+epsilon xi(y), qtilde_epsilon(y)=q_epsilon(x_epsilon(y))
and Delta q=partial_epsilon qtilde. Then the entire density, including the
Jacobian and the transformed derivative, is pulled back once:

    Ltilde = J_x L(x_epsilon,qtilde,(partial_y qtilde)/J_x).

At epsilon=0 its variation is

    L_q.Delta q + p.(Delta q)' + xi' (L-p.q') + xi L_x
      = E.(Delta q-xi q')
          + partial_y[p.Delta q+xi(L-p.q')],            (3)
    E=L_q-partial_y p.

Indeed partial_y(L-p.q')=L_x+E.q'. All Euler terms remain off shell.
For L_x=0 the embedding row in material variables is -E.q', not zero
by fiat. Equation (3) contains the domain derivative already. Appending a
second xi L changes the variational principle. Conversely, retaining only
p.Delta q and forgetting -f p.q' also changes it. The verifier differentiates
a pulled-back nonlinear density with independent jets, then compares (3).

For a covariant higher-dimensional top form the underlying identity is
Cartan's Lie derivative and pullback functoriality. Additional metric,
connection and GHY Green summands must be included before using the full
Noether identity to infer dependence of a gravitational embedding equation.
The one-dimensional oracle is an independent exact check of the local
Legendre/transgression signs, not a full higher-derivative gravity proof.

## 3. Two-sided gluing and admissible tangent variations

Use one normal n from M_minus to M_plus and a common geometric interface
speed f. In scalar trace coordinates q_Sigma is common, so a tangent to the
gluing locus must satisfy

    delta q_minus| = Delta q_Sigma - f v_minus,
    delta q_plus | = Delta q_Sigma - f v_plus.          (4)

The two v's need not agree. They are derivatives along the same n, not two
outward derivatives. For M_minus the outward normal is n; for M_plus it is
-n. Summing (2) therefore gives

    (p_minus-p_plus).Delta q_Sigma
       + f (T_nn,minus-T_nn,plus).                    (5)

A wall density ell(q_Sigma) adds ell_q.Delta q_Sigma; consequently the scalar
natural row is p_minus-p_plus+ell_q and the normal scalar bulk force is
-[T_nn]. With ell=-Lambda this reproduces the charter's outward Pi sum
plus Lambda_q=0. The wall metric and geometric terms are separate.

If both Eulerian bulk variations are frozen, (4) requires
f(v_minus-v_plus)=0. Thus generic discontinuous normal jets do not admit two
arbitrary embedding variations with all bulk traces frozen. The test oracle
uses two different nonlinear profiles, different normal slopes and an
explicit shared Delta q, differentiates the actual moving integrals, and
compares their endpoint/volume decomposition. A separate negative witness
rejects an inadmissible frozen-bulk variation.

Equations (1)-(5) link the missing scalar Legendre term to the normal stress
used by the independent Gauss-Israel constraint identity. They do not prove
that the entire normal gravitational equation follows merely by replacing
Delta gamma by 2f K in a Green form whose bulk Euler rows were omitted.
All nonlinear coupled existence, hyperbolicity, stability and quantum gates
remain open.
