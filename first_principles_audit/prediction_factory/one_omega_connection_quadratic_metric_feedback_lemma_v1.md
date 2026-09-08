# Quadratic metric feedback of the localized connection repair

This note concerns the proposed, unadopted term S_C=-chi/2 integral
<C wedge *C>, chi>0, with independent A_Sigma. It does not alter the
frozen v5.2 action or solve its metric/embedding equations. The input is
the localized static order-epsilon^2 port of the pinned torque-lift lemma.
The new result is its actual leading metric source, including its size
and the horizontal Ward identity that must be retained when coupling it
to the rest of the equations.

## 1. Input and order bookkeeping

Use signature (-+++), T=t, gamma=-exp(2epsilon F)dt^2+dx^2,
and the spatial Cartesian frame. The generators are
(T_I)^a_b=epsilon_Iab with epsilon_123=+1, and
<X,Y>=sum_ab X_ab Y_ab/2. In this port omega=0 exactly, although
kappa_(t,a)=partial_a exp(epsilon F) need not vanish. Let

    rho=kappa_R*y^2 grad F cross grad U=curl W,
    W=kappa_R*y^2 F grad U, U=g(|D|)F,
    g(p)=kappa_R/(kappa_R+2Zp).

F is real C_c^infinity(R^3), hence W and rho are smooth compactly
supported, div rho=0 and integral rho=0. Here kappa_R is the Robin
coefficient, distinct from the frame tensor kappa_(mu,a).
The source orientation is [j4]/vol_Sigma=epsilon^2 rho+O(epsilon^3).
The literal oriented BF Green form is +[b] wedge deltaA, so its current
row is [b]=-J and D J=[j4]. This is the Stokes correction recorded in the
current-candidate lemma; the frozen v5.2 action itself is unchanged.
The unique L2 Poisson lift is

    chi Delta Theta=-rho,
    Theta_hat(xi)=rho_hat(xi)/(chi |xi|^2),
    A=-d exp(epsilon^2 Theta_mat) exp(-epsilon^2 Theta_mat),
    Theta_mat=Theta^I T_I.

A is flat exactly. Its leading term is -epsilon^2 dTheta_mat, and
C=A because omega=0. All coefficient superscripts (2) below mean the
coefficient of epsilon^2; there is no extra factorial.

## 2. The leading metric and clock contributions

Use the pinned covariant first variation

    tau_C^(mu nu)=T_C^(mu nu)-nabla_r J^((mu nu)r)-V^((mu)u^(nu)),
    J^(mu nu r)=chi C^(mu ab)e_a^nu e_b^r,
    V^s=chi C^(mu ab)kappa_(mu,a)e_b^s,
    E_T=nabla_s(N V^s).

The explicit quadratic stress T_C starts at epsilon^4. In this static
port C_t=0 and kappa_(i,a)=0, so V=0 exactly. Covariant-derivative
corrections acting on J^(2) start at epsilon^3. Thus, writing
v=curl Theta and symmetrization with weight one half,

    tau_C^(2)_(00)=tau_C^(2)_(0i)=0, E_T^(2)=0,
    J^(2)_(ijk)=-chi epsilon_Ijk partial_i Theta_I,
    tau_C^(2)_(ij)=chi partial_(i v_(j))
                 =chi/2 [partial_i v_j+partial_j v_i].       (1)

This source is second order despite the value of the added action
starting at fourth order on the prescribed family. Varying the metric
also varies omega. In fact the mixed epsilon^2 delta-gamma term of the
literal action is -chi<dTheta_mat,delta omega>, which after integration
by parts is tau_C^(2):delta-gamma/2. Holding omega fixed would miss (1).

In particular

    tr tau_C^(2)=0,
    partial_i tau_C^(2)_(ij)=-1/2 (curl rho)_j.                (2)

There is no reason to set this divergence to zero for the connection
term alone. G=chi D_mu C^mu has coefficient G^(2)=rho_I T_I.
Its horizontal image is G_H^(2)_(ij)=epsilon_Iij rho_I, so

    partial_i tau_C^(2)_(ij)=1/2 partial_i G_H^(2)_(ij).       (3)

All other terms in the pinned horizontal Ward identity vanish at this
order in the static port. Equation (3) is the required off-shell Ward
relation, with its sign and factor of two, not a total Einstein equation.

## 3. Exact size and tensor sector

Use the unitary spatial Fourier transform. Put p=|xi|>0 and
r=rho_hat(xi). Substitution of the Poisson multiplier into (1) gives

    tau_hat_(ij)=-[xi_i (xi cross r)_j
                         +xi_j (xi cross r)_i]/(2p^2).      (4)

The coefficient chi cancels. The vectors r may be complex; all norms
below are Hermitian, and the tensor norm sums all nine matrix entries.
For any r, |xi cross r|^2=p^2|r|^2-|xi dot r|^2. Therefore

    |tau_hat|_F^2=(|r|^2-|xi dot r|^2/p^2)/2.

For the actual source xi dot r=0. Plancherel gives the exact identity

    ||tau_C^(2)||_L2,F^2 = ||rho||_L2^2/2.                  (5)

The equality is a Euclidean spatial tensor/Sobolev norm identity for an
order-epsilon^2 coefficient. It is not the canonical energy of the coupled
metric, matter and BF system. Nor is it the order-epsilon^4 action value.

The same equality holds with any common scalar Fourier weight, including
the inhomogeneous H^m weight. In particular the feedback is smooth and
square integrable at all finite derivative orders. Formula (4) is a
bounded multiplier of order zero; no additional infrared integrability
assumption is needed for tau. Its representative at xi=0 has measure zero.
The zero mean of rho remains necessary for the separately asserted
L2 Poisson potential Theta. That is a different, order-minus-two map.

With P=I-xi tensor xi/p^2, (4) also gives

    P tau_hat P=0, tr tau_hat=0,
    i xi_i tau_hat_(ij)=-i/2 (xi cross r)_j.                  (6)

Thus this added source is in the spatial vector sector. It contains no
transverse-traceless component and no spatial scalar component. This is
a statement about the added source on this port, not a claim that the
complete matter/metric second-order source has only that sector.

For fixed F and the fixed Robin response, rho is independent of chi.
The positive quadratic connection energy of the lift decreases as

    E_C^(4)=1/(2chi) integral |rho_hat|^2/p^2,

whereas the norm (5) does not decrease at all. Increasing chi cannot
justify neglecting this leading metric contribution. This does not
prove failure of the proposed extension: it identifies a term that its
coupled equations must include.

## 4. A lower bound under static metric continuation

The size cannot be removed merely by allowing an additional static metric
response at order two. The precise hypotheses for this stronger statement
are a Minkowski background with Cartesian frame and T^(0)=t, C^(0)=C^(1)=0,
a fully static continuation, and the corrected current equation G^(2)=rho.
The first-order data and hence the source rho are held fixed. We do not
assume omega^(2)=0. At this order the terms C F and G C in the horizontal
Ward identity vanish, and E_T partial_j T has no spatial background factor.
Time derivatives also vanish. The remaining spatial Ward identity is

    partial_i S_ij = -1/2 (curl rho)_j,
    S_ij = tau_C,ij^(2).                                    (7)

Here S is the contribution from the proposed connection term, not the
complete metric source from all sectors. In Fourier space S is symmetric
and may be complex. Its orthogonal spatial vector projection, in the
Hermitian Frobenius product on symmetric matrices, is

    V(S)=[xi tensor (P S xi)+(P S xi) tensor xi]/p^2,
    P=I-xi tensor xi/p^2.

This map is an orthogonal projection: the complementary transverse tensor
P S P and longitudinal scalar component are orthogonal to its range.
Equation (7) fixes S xi=-(xi cross r)/2, already transverse, and therefore
V(S) is exactly the multiplier in (4). Since the actual rho is transverse,
pointwise Hermitian orthogonality and Plancherel imply

    ||S||_L2,F^2 = ||V(S)||_L2,F^2+||S-V(S)||_L2,F^2
                 >= ||rho||_L2^2/2.                        (8)

The inequality also holds with a common nonnegative scalar Fourier weight
whenever the corresponding norms exist. Equality holds for the prescribed
Poisson port (1); other compatible continuations can add orthogonal tensor
components. If transversality of rho were dropped, the right side would
instead be ||P rho||^2/2. This argument is not a time-dependent statement
and does not apply unchanged when C^(1) is nonzero.

No cancellation with the other action sectors is asserted. The selected
H18 operator already contains the linear connection response to the
unknown second-order fields. In a forced perturbation calculation those
linear terms and the known quadratic source must be separated once; adding
the whole tau_C^(2) again as an independent force would double count them.
The bound concerns the complete connection contribution satisfying (7),
not an extra load to add twice to H18.

## 5. What remains to couple

The material/Robin and bulk metric contributions must be varied in the
same horizontal frame and orientation as (3). Only their full Noether
identity, together with the current equation G^(2)-rho=0 and the other
first-order Euler equations, can provide conservation of the complete
second-order source. The prescribed lapse port was not claimed to solve
all those first-order Einstein equations. Consequently one cannot infer
solvability of the complete forced H18 response from (2)-(3) alone.

For a physical continuation the first-order data must first satisfy the
coupled linearized bulk, boundary and embedding equations (or explicit
external sources must be retained). One then computes all quadratic
sources, checks their Ward constraints, solves the retained response
with all pivots present, and reconstructs BF with those sources. The
static port uses a Poisson lift; the temporal N_a=0 chart requires Re(s)>0
and cannot be inserted at s=0 by division by s. Neither construction
provides the missing full Einstein/embedding second-order solution.

The result of this note is (1)-(6) for the given localized port and the
conditional static lower bound (7)-(8), derived
from the already pinned variation rather than an assumed conserved
stress. The proposal remains unadopted; chi stays symbolic and all
broad physical, nonlinear and global gates remain unpromoted.
