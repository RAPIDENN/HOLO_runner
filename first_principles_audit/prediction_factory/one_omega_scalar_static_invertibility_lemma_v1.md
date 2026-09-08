# Static scalar invertibility for the fixed candidate

This proof concerns the exact finite-energy bulk response at **s=0, q>0**.
It proves a negative scalar potential Hessian after lapse and shift elimination,
not dynamical stability, an RHP determinant theorem, or nonlinear closure.
The coefficients are the literal decimals of the pinned v5.2 candidate; no
matching relation is substituted for those decimals.

Write M=k=1, G=6/5, a=1/5, b=Mb²=2, beta=2, xi=1,
B=(8/5)q², C0=exp(a), m0=5(exp(a)-1), Ns=6(C0-m0), and

    E0 = 6.214027581601698,
    E(q) = E0 - 6q/(1+2q),
    m(q) = K_T(q²)/q²,
    J(q) = G K_v(q²)/q²,
    Delta(q) = beta G K_v/(beta+G K_v),
    C(q) = 6C0 - 6m(q) - Delta(q)/q²,
    c(q) = C(q)/9,             P(q)=2+m(q).

The spectral argument in `one_omega_scalar_shift_pivot_lemma_v1.md` gives
0<m<=m0, 0<J<=Ns, and 0<=C<=6(C0-m). This also follows directly from the
real positive variational problems below and the zero-mode mass identity.
The exact three-field reduction at zero frequency has shift pivot
b(1-lambda_K)q²>0. The remaining matrix, divided by q², is

    [[ E+c,       2(P+c) ],
     [ 2(P+c),   2P+4c-B ]].

Its determinant is

    F(q)=2P(E-2P)+c(4E-6P)-B(E+c).

Since E>E0-3>3 and c>=0, its lapse pivot is positive. It suffices to prove
F(q)<0. Then the final one-field static Schur complement is strictly negative.

## Bounds from the actual radial equations

For either real positive master solution H with UV trace one, the variational
minimum can be clipped to [0,1] without increasing energy. Uniqueness gives
0<=H<=1; the ODE gives strict positivity. Its flux obeys

    -P_rad(r) H'(r) = q² integral_r^infinity W_rad H dr.

The integration constant at infinity is zero: the right side is integrable,
and a nonzero limiting P_rad H' would contradict bounded H because
integral 1/P_rad diverges. With Omega'=-k Omega exp(-a Omega²), write
P_rad=Omega^(b_w+2), W_rad=Omega^b_w, b_w=2 for TT or 4 for R. Then

    1-H(Omega) <= q² exp(2a)/(2 b_w k²) (Omega^-2-1).

For TT split the zero-mode integral at Omega=q/k, for 0<q<k. Using 1-H<=1
on the lower interval gives

    0 <= m0-m <= (M q²/k³) [exp(a)+exp(3a)/2 log(k/q)].

For the scalar the unsplit integral converges and gives

    0 <= Ns-J <= G exp(3a) q²/(16 k³).

Series loading by beta adds at most J² q²/beta, hence

    0 <= Ns-Delta/q² <= [G exp(3a)/(16 k³)+Ns²/beta] q²,
    C <= 6(m0-m)+[G exp(3a)/(16 k³)+Ns²/beta] q².

These are rigorous upper bounds, not numerical approximations to the kernels.

A second bound is useful away from zero. Omega(r)>=exp(-kr), so both
positive radial weights dominate their a=0 values. Minimization over the
common trace-one domain gives

    m(q) >= (2M/q) K1(q/k)/K2(q/k) > 2M/(2k+q).

For completeness, the needed Bessel facts follow from
Knu(x)=integral_0^infinity exp(-x cosh t) cosh(nu t) dt: K1>K0>0, while
integrating d[sinh(t) exp(-x cosh t)] gives K2=K0+2K1/x. Domain comparison
is legitimate because each finite-energy actual profile also has finite
energy for the smaller reference weights and the same UV trace.

## Small momenta: 0<q<=1/10

The elementary bounds 6/5<exp(1/5)<5/4 imply exp(3/5)<2,
1<m0<5/4, and 0<Ns<3/2. The lower bound is the strict Taylor bound 1+x. The companion checks log(10)<231/100 using a
rational lower Taylor sum for exp(231/100). Since q[5/4+log(1/q)] increases
on this interval, writing d=m0-m gives

    d < (9/25)q,
    C <= 6d+(3/20+9/8)q²,
    c < (13/50)q.

Crucially, the exact decimal E0 satisfies E0<=2(2+m0). A rational lower
Taylor sum through order 12 for exp(1/5) proves this unilateral inequality;
the margin is small and is not rounded to zero. Thus

    P>29/10,     E-2P <= 2d-6q/(1+2q) < -(107/25)q.

Dropping the nonpositive -B(E+c), and using E<25/4, yields

    F < [2(29/10)(-107/25)+25(13/50)]q
      = -(4581/250)q < 0.

## Intermediate momenta: 1/10<=q<=2

Set mL=2/(2+q). The allowed c interval is contained in
[0, (2/3)(5/4-m)]. Since F is affine in c, maximize at its endpoints:

    F0(m)=2(2+m)[E-2(2+m)]-BE,
    F1(m)=F0(m)+(2/3)(5/4-m)[4E-6(2+m)-B].

Both decrease with m on this interval. Indeed

    dF0/dm=2E-8(2+m)<0,
    dF1/dm=(2/3)(B-E)-13<0,

using E<25/4, m>0, E>0 and B<=32/5. It therefore suffices to check F0(mL)
and F1(mL). Their denominators are positive. With the literal rational E0,
their numerator polynomials have **strictly negative coefficients** after
q=x+1/10, x>=0. The companion derives and checks every coefficient exactly.
This proves both expressions negative throughout the required interval.

## Large momenta: q>=2

E<=E0-12/5<77/20, P>=2, and B>=32/5. Consequently

    E-2P < -3/20,
    4E-6P-B < -3.

The expression F=2P(E-2P)+c(4E-6P-B)-BE is strictly negative.

Combining the three intervals proves static invertibility for every q>0 on
the selected finite-energy branch. The lapse and shift pivots are retained
and positive; no zero has been discarded in the reduction. There is no claim
about q=0, complex-frequency zeros, ghost counts, BF/global sectors, or full
N7/P4/B4/B5. The companion checks finite algebra and bounds; the variational
and ODE argument here is a reviewed mathematical proof, not a formal proof
assistant certificate.
