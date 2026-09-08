# Variational existence and holomorphy of the one-Omega DtN kernels

This lemma establishes existence, uniqueness and positive-real boundary response
for the selected **finite-energy branch**. It supplies the analytic input to
[the sector reduction](verify_one_omega_topological_sector_reduction_v1.py)
(commit `03a695661ca2ee7550ae10ad18b8155e2387a29e`). It does not establish the
remaining coupled scalar determinant or the BF/interface domain.

## 1. Background, weights and statement

Write \(M=M5c>0\), \(G>0\), \(k>0\), and \(\alpha=G/(6M)\).
The selected BPS exterior has \(r\geq0\), \(A=\log\Omega\), and
\[
 \Omega(0)=1,\qquad \Omega'/\Omega=-k e^{-\alpha\Omega^2}.
\]
The smooth positive solution satisfies
\[
 e^{-kr}\leq\Omega(r)\leq e^{-k e^{-\alpha}r}\leq1.
\]
For the tensor and curvature-master profiles, respectively, use
\[
 (P_T,W_T)=(\Omega^4,\Omega^2),\qquad
 (P_R,W_R)=(\Omega^6,\Omega^4).
\]
Both pairs are smooth and strictly positive on every finite compact interval,
normalized by \(P(0)=W(0)=1\), and satisfy \(P/W=\Omega^2\leq1\).
In particular \(\int W<\infty\); no lower bound on the weights at infinity is
assumed.

**Claim.** For either pair, every fixed \(q\geq0\) and
\(s=\sigma+i\tau\), \(\sigma>0\), admit a unique finite-energy variational
solution of
\[
 -(PH')'+(s^2+q^2)WH=0,\qquad H(0)=1.
\]
Its two-sided DtN kernel is holomorphic in this open half-plane and obeys
\[
 K(s,q)=-2H'(0),\qquad \Re\frac{K(s,q)}s>0.
\]
The factor two counts identical exteriors, each with outward UV normal
\(-\partial_r\). Proof follows; the condition at infinity is defined by the
energy space, rather than an assumed pointwise flux.

## 2. Complete energy space and trace

Let \(\mathcal C=C_c^\infty([0,\infty))\): functions smooth **up to** zero,
compactly supported in the closed half-line, with freely varying trace there.
This is not \(C_c^\infty((0,\infty))\). Set
\[
 E(u,v)=\int_0^\infty Pu'\overline{v'}\,dr,\quad
 N(u,v)=\int_0^\infty Wu\bar v\,dr,\quad
 X=\overline{\mathcal C}^{\,\|\cdot\|_X},\quad
 \|u\|_X^2=E(u,u)+N(u,u).
\]
Use the complex inner product linear in its first argument. Local positive
upper and lower bounds on the weights identify every element of this completion
with an \(H^1\) function on each finite interval, with its distributional
first derivative. Thus no extra, nonfunctional completion elements arise.

If \(p_*=\min_{[0,1]}P>0\) and \(w_*=\min_{[0,1]}W>0\), then
\[
 |u(0)|^2\leq2\int_0^1(|u|^2+|u'|^2)\,dr
 \leq2\max(p_*^{-1},w_*^{-1})\|u\|_X^2.
\]
The trace extends continuously to \(X\), is surjective because a compact smooth
lift \(\ell(0)=1\) exists, and \(X_0=\ker\operatorname{tr}\) is closed and
complete.

Conversely, every locally \(H^1\) function with finite displayed norm belongs
to \(X\). Choose smooth cutoffs \(\chi_R=1\) on \([0,R]\), zero beyond
\(R+1\), with uniformly bounded derivative. The only additional derivative
error is controlled by
\[
 \int P|\chi_R'u|^2\leq C\int_R^{R+1}W|u|^2\longrightarrow0,
\]
using \(P/W\leq1\). The other errors are energy tails. Standard smoothing on
a finite interval, allowing extension across zero, completes the approximation.
Hence this domain is precisely the finite-energy space. For \(X_0\), subtract
the approximants' traces times \(\ell\) to obtain trace-preserving density.
In particular the constant function belongs to \(X\): it is not required
to vanish at infinity.
The closed form \(E\) on \(X_0\) identifies the nonnegative
Friedrichs/energy realization with homogeneous UV trace. The affine solution
below has unit UV trace in the same energy domain.

## 3. Existence without a presumed DtN solution

Define the bounded sesquilinear form
\[
 B_s(u,v)=E(u,v)+(s^2+q^2)N(u,v).
\]
It is linear in \(u\) and antilinear in \(v\); its operator therefore takes
values in the continuous **antidual**. A bound is
\(|B_s(u,v)|\leq\max(1,|s^2+q^2|)\|u\|_X\|v\|_X\).
For \(a_s=B_s/s\), direct algebra gives
\[
 \Re a_s(u,u)=\frac{\sigma}{|s|^2}
 \left[E(u,u)+(|s|^2+q^2)N(u,u)\right]
 \geq c_s\|u\|_X^2,
 \quad c_s=\frac{\sigma}{|s|^2}\min(1,|s|^2+q^2)>0.
\]

For completeness, represent \(a_s\) on \(X_0\) by the bounded operator
\(T_s\), with \(\langle T_su,v\rangle_X=a_s(u,v)\).
Coercivity implies \(\|T_su\|\geq c_s\|u\|\), hence injectivity and closed
range. The adjoint satisfies the same real diagonal coercivity, so
\(\ker T_s^*=0\). Its range is therefore also dense and consequently all of
\(X_0\). This proves bounded invertibility, including surjectivity, rather than
assuming it from a formal differential equation.

Fix a real compact lift \(\ell\) with trace one. The continuous antilinear
functional \(-a_s(\ell,\cdot)\) yields a unique \(u\in X_0\) satisfying
\[
 B_s(u,v)=-B_s(\ell,v)\quad(v\in X_0).
\]
Then \(H=\ell+u\) has trace one and \(B_s(H,v)=0\) on \(X_0\).
Any two such solutions differ by an element of \(X_0\); coercivity proves
uniqueness. The construction is independent of the chosen lift. Conversely,
a finite-energy distributional solution satisfies the same variational equation:
first test with compact zero-trace functions, then use their density in \(X_0\).

## 4. Holomorphy, UV flux and exact Green identity

On the fixed space \(X_0\), the operator
\(\mathcal B(s):X_0\to X_0^{\mathrm{anti}*}\) represented by \(B_s\)
is a bounded-operator polynomial in \(s\). Near any \(s_0\) in the open
half-plane, invertibility and a local Neumann series show that
\(\mathcal B(s)^{-1}\) is holomorphic. The fixed-lift right-hand side is also
polynomial, so \(H(s)\in X\) is holomorphic. Define
\[
 K(s,q)=2B_s(H(s),\ell).
\]
A different unit-trace lift differs from \(\ell\) by an element of \(X_0\),
so this definition is independent of that choice. With the second argument
fixed, it is manifestly holomorphic. Real coefficients and uniqueness also
imply \(K(\bar s,q)=\overline{K(s,q)}\).

Testing with compactly supported interior functions yields the stated ODE in
distributions. Local regularity, including the UV endpoint, makes \(PH'\)
continuous there. Integration against the compact lift gives
\[
 B_s(H,\ell)=-P(0)H'(0),
\]
with no integration boundary at infinity. Since \(P(0)=1\), this proves the
claimed derivative normalization.

The admissible test \(H-\ell\in X_0\) gives the exact identity
\[
 \frac K2=B_s(H,\ell)=B_s(H,H),\qquad
 \Re\frac Ks=\frac{2\sigma}{|s|^2}
 \left[E(H,H)+(|s|^2+q^2)N(H,H)\right]>0.
\]
Strictness follows from the nonzero trace. This excludes zeros of \(K\) in
the open half-plane. The equality with \(B_s(H,H)\) proves the energy identity;
it is the fixed-lift expression above that proves holomorphy.

There is also no hidden limiting energy flux. Put \(F(r)=P H'\bar H\).
The ODE implies
\[
 F'=P|H'|^2+(s^2+q^2)W|H|^2\in L^1(0,\infty).
\]
Thus \(F(\infty)\) exists. Integrating this identity and using
\(F(0)=-K/2\) and \(B_s(H,H)=K/2\) proves \(F(\infty)=0\).
This argument does not infer decay of the product merely from decay of \(PH'\).

## 5. Normalizations and the proved sector factors

With \(dz=dr/\Omega\), the tensor variable \(\Psi_T=\Omega^{3/2}H\) and
\(Q_T=\partial_z-3A_z/2\) have precisely the energy weights \(P_T,W_T\).
For the scalar curvature profile \(R\), set
\(v=-\sqrt G\,\Omega^{5/2}R\) and \(Q_R=\partial_z-5A_z/2\).
Its canonical energy divided by \(G\) has weights \(P_R,W_R\).
Consequently the kernels above are the normalized \(K_T\) and \(K_v\)
used in the boundary assembly; at the UV, \(-2Q_Rv/v=-2R'/R\).

Let \(M_b^2>0\), \(\xi\geq0\), and keep \(M,G>0\), \(\beta\geq0\).
The sector definitions after \(w=is\) are
\[
 F_T=M_b^2(s^2+\xi q^2)+MK_T,\qquad
 F_V=M_b^2(s^2+q^2)+MK_T.
\]
Since \(\Re[(s^2+cq^2)/s]=\sigma(1+cq^2/|s|^2)>0\) for \(c\geq0\),
both \(F_T/s\) and \(F_V/s\) have strictly positive real part.
They are holomorphic and zero-free in the open half-plane. This certifies the
tensor entry \(-F_T/2\). For \(q\ne0\), the vector gauge \(H_{13}=0\)
has entry \(q^2F_V/[2(s^2+q^2)]\), also nonzero. At \(q=0\), use the
separate gauge \(N_1=0\), available because \(s\ne0\), with entry \(-F_V/2\).
Here \(s^2+q^2\) never vanishes in the open half-plane.

Similarly,
\[
 \Re\frac{GK_v+\beta}{s}=G\Re\frac{K_v}{s}
       +\frac{\beta\sigma}{|s|^2}>0,
\]
so this scalar pivot is nonzero. The material branch
\(p=\sqrt{s^2+q^2}\), \(\Re p>0\), is holomorphic there; for
\(\hat\kappa,Z_5>0\), the material pivot
\(\hat\kappa+2Z_5p\) has positive real part and is nonzero.
No positive-real conclusion for the remaining coupled scalar determinant
follows merely by eliminating these pivots.

## 6. Scope boundary

This is a continuum analytic proof for the specified finite-energy realization,
not a claim based on sampled ODE solutions. It does not provide uniform
coercivity as \(\sigma\downarrow0\), boundary values on the real-frequency
axis, or a comparison with other infrared extensions. The kernel lemma itself
allows \(q=0\); a scalar gauge or Schur reduction dividing by \(q\) requires
its own separate analysis there. The outstanding coupled scalar determinant,
BF elimination and edge domain, independent moving-embedding equations,
complete N7/P4, B4 and B5 are **not established** by this lemma.
