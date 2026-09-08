# Static sourced BF reconstruction for the localized quadratic port

This lemma completes a selected BF-sector reconstruction at order epsilon²
for the prescribed localized port of the separate connection candidate.
It does not solve the coupled Einstein/embedding problem, adopt the new
coefficient chi, or provide a full nonlinear continuation. The linear RHP
homotopy 1/s is not used at s=0. Instead a spatial homotopy is controlled in
an integrated three-dimensional Fourier norm, with the infrared estimate
proved explicitly below.

This revision corrects the oriented Green erratum without changing the
frozen v5.2 bytes or deleting the earlier Git history. The earlier receipt
checked a postulated jump sign; the current chain derives the interface
row from +integral B wedge F using the declared outward normals.

## 1. Sources, coordinates and orientation

Use a conformal radial coordinate z>=0 on each BPS half:

    g5=Omega(z)²(dz²-dt²+dx²), Omega(0)=1,
    dOmega/dz=-k Omega² exp(-a Omega²), k>0, a>=0.

The positive auxiliary metric for form norms is
Omega²(dz²+dt²+dx²). It defines a function space, not a Lorentzian physical
energy for B. The BPS equation gives

    1+k exp(-a) z <= Omega(z)^(-1) <= 1+k z.                 (1)

This z differs from the proper radial coordinate r, for which dr=Omega dz.
The same form norms expressed in r agree by change of variables. Per unit coordinate
time, a p-form has Euclidean-component weight Omega^(5-2p) in dz d³x.
This is the five-dimensional norm density divided by dt, without pulling
the forms back to t=constant; such a pullback would discard their dt
components and would define a different space.
In particular the B3 and J4 weights are Omega^-1 and Omega^-3.

Let F be real C_c^infinity(R3), U=g(|D|)F, with
 g(p)=kappa/(kappa+2Zp), and phi1=y grad U. The first-order conformally
transported material field in either half is

    psi1(z)=exp(-|D| z) phi1.                               (2)

It is static and solves (partial_z²+Delta_x)psi1=0. The full material
potential starts beyond the linear equation at the zero material background.
Metric corrections and phi2 do not enter the quadratic connection current.
The covariant normal mixing in phi=Omega^-3/2 psi cancels from the current:
phi dot T_I phi=0. Equivalently the conformally transported kinetic density
is exactly -Z/2 |Dpsi|_eta². Its Euler current components are

    Q_I^m=-Z partial^m psi1 dot T_I psi1
         = Z(psi1 cross partial^m psi1)_I, Q^t=0.           (3)

Thus partial_m Q^m=Z psi1 cross (partial_z²+Delta_x)psi1=0.
Use the common oriented normal n from minus to plus, vol5=dn wedge volSigma.
In the z coordinates directed into each half, define transported forms

    J4_plus = +i_Q(dz wedge volSigma),
    J4_minus= -i_Q(dz wedge volSigma).                       (4)

These signs express the same common orientation, not a second arbitrary
outward-normal factor. Both forms are closed and their common UV trace jump
is

    [j4]/volSigma = 2Z phi1 cross partial_z psi1(0)
                  = kappa*y (grad F cross phi1) = rho2.    (5)

The second equality uses the actual Robin relation
2Z|D|phi1=kappa*y grad F-kappa phi1, including both sides.
The prior localized-torque lemma constructs the unique L2 Theta with
chi Delta Theta=-rho2, so Theta_hat=+rho2_hat/(chi p²). Its current
J_Sigma=-chi *_Sigma dTheta therefore satisfies d_Sigma J_Sigma=+[j4]. This is a proved compatibility for the
specified source, not an assumed arbitrary boundary condition.

The second-order BF equations to solve are

    d5 B2,eps + J4,eps=0, b2,plus-b2,minus=-J_Sigma.         (6)

With n_out,plus=-partial_n and n_out,minus=+partial_n, the identity
B wedge D(delta A)=(D B) wedge delta A-d(B wedge delta A) gives the
interface Green +[b] wedge delta A. Adding +J_Sigma wedge delta A gives
[b]+J_Sigma=0; its exterior derivative and the bulk rows give dJ=[j4].
The core verifier derives this incidence before checking (6). Keeping the
old [b]=+J sign would instead leave twice the nonzero current.

A0=B0=phi0=0 and A1=B1=0 for this prescribed lapse-only port. Thus no
[A1,B1] term has been omitted in (6). An exactly flat A with leading
A2=-d(f Theta) is supplied by the earlier exponential construction; A2
acting on phi1 first affects the third-order material equation.

## 2. Spatial homotopy and sourced extension

For spatial Fourier momentum xi in R3, p=|xi|>0, define

    d5 = i xi_j dxj wedge + dz wedge partial_z,
    h_xi = -i sum_j xi_j i_(partial_xj) / p².

The dt components of forms remain present; only their time derivatives are
zero. Cartan's algebra gives

    d5 h+h d5=1, d5²=0, h²=0,
    tr_UV h=h tr_UV, tr_UV d5=d_Sigma tr_UV.                (7)

No radial derivative is dropped. There is no uniform operator bound as
p approaches zero; section 3 handles the actual source by integration.
Set

    B_part,eps=-h J4,eps,
    L=J_Sigma-h[j4],
    B2,eps=B_part,eps-eps/2 d5[f(z) hL], eps=+1,-1,        (8)

where f=1 near z=0 and is smooth and compactly supported radially.
Closure of J4 gives dB_part=-J4. The compatibility (5) gives d_Sigma L=0.
Hence

    d5[f hL]=f L+f' dz wedge hL,
    tr(B2,plus-B2,minus)=-h[j4]-L=-J_Sigma.                (9)

For the actual selected port there is a further exact simplification.
With volSigma=dt wedge dx1 wedge dx2 wedge dx3 and the Lorentzian Hodge,
star(dTheta_hat)=i*Theta_hat*i_xi(volSigma). Therefore

    J_Sigma_hat=-i*rho2_hat*i_xi(volSigma)/p²=+h[j4]_hat,
    L=0.                                                   (9a)

Consequently B2,eps=B_part,eps already supplies the required jump for this
port, with jump -J_Sigma. B_part=-hJ4 is unchanged by the correction of
the boundary sign; Theta and J_Sigma reverse sign. The affine correction in (8) is retained as a general algebraic
control for compatible currents with a nonzero closed remainder, not as
an extra field required by the selected Poisson solution.

Equations (6) follow exactly for the coefficients at this perturbative order.
The f' term and the one-half incidence factors are required. The construction
keeps the particular source solution; the homogeneous affine reconstruction
with dB=0 would fail (6). It does not gauge away the nonzero source or jump.

## 3. Global spatial and radial norm estimates

Write norms below in Euclidean x at each fixed z, with constants depending
on the fixed smooth F and the positive coefficients. Since |g|<=1 and
F_hat is bounded and rapidly decreasing, Fourier integration in R3 gives
for z>=1

    ||psi1||_2 <= C z^-5/2,
    ||partial_(z,x)psi1||_2 <= C z^-7/2,
    ||psi1||_infinity <= C z^-4.                            (10)

For example the first squared bound is controlled by
int_0^infinity p^4 exp(-2pz) dp, the second by p^6 instead of p^4,
and the infinity bound by int p^3 exp(-pz) dp. All norms remain bounded
on 0<=z<=1 by the high-frequency decay of F_hat. Thus z in the right-hand
bounds can be replaced by 1+z after adjusting constants. Products in (3)
and Holder's inequality imply

    ||J4(z)||_1 <= C (1+z)^-6,
    ||J4(z)||_2 <= C (1+z)^-15/2.                           (11)

The unitary spatial Fourier transform and |h_xi|<=1/p in component norm
give, splitting p<=1 and p>=1,

    ||h J4(z)||_2² <= C(||J4(z)||_1²+||J4(z)||_2²)
                    <= C(1+z)^-12.                       (12)

The low-frequency integral is finite in THREE spatial dimensions:
int_(p<1) p^-2 d³xi=4pi. No vanishing mean for all bulk source components
is needed here. This is an order-minus-one primitive, different from the
order-minus-two Theta equation, which did require the zero mean proved
in its own lemma. Combining (1), (11) and (12),

    int Omega^-1 ||B_part||_2² dz < infinity,
    int Omega^-3 ||J4||_2² dz < infinity.                  (13)

The respective majorants at infinity are (1+z)^-11 and (1+z)^-12.
Consequently B_part and dB_part=-J4 lie in the selected weighted graph
space of d, per time slice. Closure and (7) hold distributionally; the
bounds allow the corresponding Fourier multipliers to be defined as L2
fields, not merely as values at isolated momenta. The same smooth-source
estimates give partial_z J4 locally uniformly in L1 and L2, so h commutes
with that radial derivative in distributions and the UV trace is obtained
by L2 continuity; no delta distribution at xi=0 is inserted.

At the UV boundary rho2 is smooth compact with zero mean. Its transform
is O(p) at the origin and rapidly decreasing at high frequency. Both
J_Sigma_hat=-chi * i xi Theta_hat and h[j4]_hat are O(1) at p=0, and decrease
rapidly at high p up to harmless powers. Therefore L and hL are L2(R3):
for hL the low-frequency squared integrand is at worst p^-2. In the
actual selected port both L and hL vanish by (9a). The compact
radial correction in (8) consequently has finite weighted L2 norm. Its
derivative is zero, as required by (9), so the full B2 is in the same graph
space. Smoothness of the actual source and these explicit traces justify
(9) in the Green trace sense as well. No trace of a normal component is
imposed separately.

Thus (8) is a sourced BF solution with the correct trace jump and finite
auxiliary norm throughout both half spaces, integrated over R3. It is not
merely a periodic witness or a nonzero-momentum per-mode calculation.
Static fields over an infinite time interval need not be L2 in time.

## 4. Scope and remaining work

The frozen action's incompatibility is unchanged. For the proposed added
current, this lemma constructs the second-order BF sector associated with
the specified localized first-order material port. It proves no full
Einstein solution, no backreaction cancellation and no higher-order
continuation. In particular the new metric adjoint can already contribute
at second order; it cannot be discarded because the added action density
starts at fourth order on this selected family.

A uniqueness statement for all static weighted BF fields is not made:
h_xi is unbounded as p->0 on arbitrary L2 data, and the source estimates
above are specific. No topological holonomy sectors, large gauges, BV/BFV
complex or time-dependent boundary domain are classified. N4/N7/P4 and
B4/B5 remain unpromoted; chi is positive and unselected. The companion
verifies the exterior algebra, source signs and explicit norm exponents;
its finite identities do not replace the analytic estimates in section 3.
