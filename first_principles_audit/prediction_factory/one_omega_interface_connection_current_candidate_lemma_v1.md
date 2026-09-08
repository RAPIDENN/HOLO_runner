# Candidate interface connection current: local mechanism and limits

This is a reviewable **alternative action term**, not an amendment adopted
into v5.2. The frozen action and its coefficient policy are unchanged. Let
chi be a new strictly positive, otherwise unspecified coefficient. No value
is selected, and no general physical or nonlinear gate is promoted.

## 1. The current that a repair would need

Keep A_Sigma an independent SO3 connection on Q=Fr_SO^+(H_(gamma,T)).
Fix a common normal coordinate n from M_minus to M_plus and orientations

    vol5=dn wedge vol_Sigma,
    M_plus={n>=0}, M_minus={n<=0},
    n_out,plus=-partial_n, n_out,minus=+partial_n.

The transported traces are exactly b_eps=Ad_r(Y_eps^*B_eps) and the
corresponding pullbacks j4_eps of the bulk current, with no incidence sign
inside either definition. Both sides are compared in the same Sigma chart.
The bulk equations from the literal positive BF term are

    D_A b_plus+j4_plus=0, D_A b_minus+j4_minus=0.

The sign of the interface equation must also be derived from that term.
For a three-form B and a one-form variation Delta A, invariance of the
color pairing and the graded Leibniz rule give

    Delta_A <B wedge F> = <B wedge D_A Delta A>
      = <D_A B wedge Delta A> - d<B wedge Delta A>.

Thus the bulk Green form is -<B wedge Delta A>. The induced boundary
orientation is -vol_Sigma on M_plus and +vol_Sigma on M_minus. Summing the
two actual oriented boundaries therefore gives

    sum_eps integral_boundary_Meps -<B_eps wedge Delta A_eps>
      = integral_Sigma <(b_plus-b_minus) wedge Delta A_Sigma>.

This is **plus the jump** in the common chart. Define the intrinsic current
by Delta S_new=integral <J_Sigma wedge Delta A_Sigma>+other variations.
The full natural connection row and its consequence are

    b_plus-b_minus=-J_Sigma,
    D_A J_Sigma=j4_plus-j4_minus.                             (1)

All three rows are retained: differentiate [b]+J=0 and subtract
D_A[b]+[j4]=0 to obtain D_A J-[j4]=0.

A separate elementary component check fixes the same sign without reading
an interface equation. Use coordinates (n,t,x,y,z), B=b(n)dx wedge dy wedge
dz and Delta A=a(n)dt. Then B wedge dDelta A=b a' vol5. Choose a_plus and
a_minus with common value a0 at n=0 and zero values at the outer endpoints.
Integration by parts gives the interface contribution

    -b_plus(0)*a0+b_minus(0)*a0.

But [b_form] wedge Delta A=-(b_plus-b_minus)*a0 vol_Sigma because dt must
cross three spatial differentials. Hence this contribution is precisely
+[b_form] wedge Delta A. The companion evaluates both integrals with
independent polynomial bulk slopes and curvatures and independent test
profiles, rather than inserting endpoint signs as input data.

**Orientation erratum, 2026-09-08.** The frozen v5.2 artifact declares the
literal positive BF action and unsigned pullback b, but its separate Green
string uses -[b] wedge Delta A. That string is incompatible with the common
orientation stated above. The former candidate receipt inherited that
string; this revision corrects its candidate chain using Stokes. The frozen
v5.2 action, artifact and action hash remain unchanged, and the discrepancy
is recorded rather than silently changing their conventions. The old test
b_plus=b_minus cannot distinguish the two global signs. For a nonzero J,
substituting the former [b]=J into the derived row gives 2J instead of zero.
Similarly the former D_A J=-[j4] leaves a residual -2[j4].

A consistent orientation reversal also changes the conversion of [j4]
into a vector density. It cannot preserve the old response while keeping
rho=[j4]/vol_Sigma fixed. With vol5=dn wedge vol_Sigma and J4=i_Q vol5,
[j4]/vol_Sigma=-sum Q_out; the Robin row gives the physical torque
rho=kappa_R*y*(a cross phi) in this convention. For zero intrinsic current,
(1) still gives the original torque compatibility [j4]=0.

## 2. A local covariant candidate

Let omega_(gamma,T) be the metric connection on the spatial bundle H obtained
by projecting the Levi-Civita derivative. In a constrained orthonormal frame,

    omega_mu^a_b = e^a_nu h^nu_rho nabla_mu e_b^rho.

Both A_Sigma and omega transform as connections under a change of Q frame.
Their difference C=A_Sigma-omega is an adjoint-valued one-form. Propose

    S_C = -chi/2 integral_Sigma < C wedge star_gamma C >.       (2)

This preserves the independent variation of A_Sigma. It is not the constraint
A_Sigma=omega. At fixed gamma,T and frame, Delta C=Delta A, hence

    Delta_A S_C = -chi integral < Delta A wedge star C >
                = +chi integral < star C wedge Delta A >.

The last sign is (-1)^(1*3). In the Green convention of section 1,

    J_Sigma = chi star_gamma C,
    chi D_A star_gamma C = [j4].                             (3)

The density check in the companion allows an arbitrary symmetric inverse
metric and positive invariant-volume coefficient. It differentiates all
three SO3 colors and all four components of A independently, then compares
with the three-form pairing. It is not a substitution of the desired sign.

A curvature-only term -alpha/2 integral < F_Sigma wedge star F_Sigma >
does not provide this mechanism on the retained BF branch: F_bulk=0 implies
F_Sigma=0 identically by pullback. Its first variation is linear in F and
vanishes pointwise for any Delta F; its current D_A star F also vanishes.
This uses flatness as a field equation on a neighborhood, including its
induced jets, not merely F=0 at one point. In contrast C need not vanish for
a flat A, so (2) can carry a nonzero interface current.

## 3. Flat fixed-geometry principal channel

Only in this section freeze gamma=diag(-1,1,1,1), T=t and a fixed Cartesian
frame, so omega=0. Locally a flat connection has A=-d g g^-1. Write
g=exp(theta) near the identity. To first order C=-d theta, with three real
Lie-algebra components. The quadratic action and canonical energy of this
new channel are

    L_theta^(2) = chi/2 sum_I [(partial_t theta_I)^2
                              - sum_i (partial_i theta_I)^2],
    H_theta^(2) = chi/2 sum_I [(partial_t theta_I)^2
                              + sum_i (partial_i theta_I)^2] >= 0.            (4)

Thus chi>0 supplies the usual positive kinetic and spatial-gradient signs
for this fixed-geometry principal channel. These formulas do not count the
physical degrees of freedom of the coupled gravity/connection theory.

Keeping the old bulk F=0 row is consistent with the local parametrization:
A=-d g g^-1 is exactly flat by the Maurer-Cartan identity. The principal
field theta is therefore a relative-connection channel, not a violation of
BF flatness. At this order J=-chi star d theta. Equation (1) becomes

    -chi Box theta_I = [j4]_I / vol_Sigma.                   (5)

This is a possible dynamical route for absorbing the torque. It does not
construct the full B field, solve the matter equations or prove coupled
existence from the interface divergence condition alone.

## 4. The static two-direction source

The incompatible prescribed-port witness has a source proportional to
sin(x) sin(2z). Write its signed four-form jump as

    [j4]_I = J0 sin(x) sin(2z) vol_Sigma

in one fixed Lie-algebra direction; J0 includes the Robin coefficients and
the declared orientation. In the flat static channel, (5) is

    chi Delta theta_I = -J0 sin(x) sin(2z).

Since Delta[sin(x) sin(2z)] = -5 sin(x) sin(2z), it is solved by

    theta_I = J0 sin(x) sin(2z)/(5 chi).                     (6)

The opposite sign does not solve the compatibility equation. On one periodic
2pi by 2pi cell, per unit length of the remaining spatial direction, the
energy (4) of (6) is

    E_theta,cell = J0^2 pi^2/(10 chi) >= 0.                   (7)

This is a cell diagnostic for the added channel, not finite total energy of
a periodic field on all of R^3, and not a change of the frozen theory's global
interface domain. Retarded data, global zero modes, boundary charges and
falloff still need a separate analysis. For the original two-mode obstruction
J0 is second order in the perturbation amplitude; theta may therefore start
at that order in this prescribed flat-geometry compatibility calculation.
No continuation of the full coupled Einstein system is proved.

## 5. What changes and what remains unproved

If geometry is allowed to perturb, omega also perturbs. Already at quadratic
order,

    C^(1) = -d theta - delta omega,
    L_C^(2) = -chi/2 < d theta + delta omega,
                         d theta + delta omega >_gamma.

The cross term and (delta omega)^2 term are nonzero. Consequently the old
linear boundary response cannot be reused as the response of (2). The
projected connection contains first derivatives of the metric/frame and,
in a frame chosen from gamma and dT, up to second derivatives of T. These
mix with the existing gravitational and khronon kinetic terms. New Euler
rows, the actual gluing adjoint, constraint rank, boundary domain, all-helicity
reduction and coupled energy must be derived before any stability claim.
The principal positivity in (4) addresses only the new channel with geometry
fixed and omega=0; it is not a bound on that combined energy.

Reinterpreting delta j as a new current does not implement (2): the original
Robin density has no independent A_Sigma dependence. A frame-representative
Ward identity is not a source in the connection Euler equation. Imposing
A_Sigma=omega by hand would instead require F(omega)=0 from BF flatness and
change the configuration domain. Changing all orientations consistently
preserves (1); changing only a sign changes the variational problem.

A dynamical relative frame U would be another alternative, not an existing
gluing datum. To exchange Robin torque it would require a sourced action,
for example D U=dU+A U-U omega together with both a kinetic term and Robin
|phi-y U a|^2. A free kinetic field whose Euler equation merely conserves its
current need not absorb the original torque. Such a model is not constructed
or selected here.

The established result is limited to a covariant candidate current, its
necessary compatibility and a positive fixed-geometry principal channel with
an explicit static source solution. It is **not a demonstrated repair of the
complete model**. Adoption of the new term, an assigned chi, full moving
Green form, BF global quotient, N2 through N7, nonlinear stability, physical
P4 and B4/B5 all remain unapproved or false in this receipt.
