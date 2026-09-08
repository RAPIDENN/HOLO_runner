# Zero-free longitudinal-shift and lapse pivots for the scalar response

This note uses the exact three-field action in
[verify_one_omega_topological_sector_reduction_v1.py](verify_one_omega_topological_sector_reduction_v1.py)
and the finite-energy realization proved in
[one_omega_variational_dtn_lemma_v1.md](one_omega_variational_dtn_lemma_v1.md).
It proves both remaining constraint pivots, not the final scalar Schur factor.
All formulas below are analytic; no sampled eigenvalue or root count is used.

## Definitions and an exact regrouping of the action

Put \(M=M5c\), \(b=M_b^2\), \(k_b=k e^{-G/(6M)}\),
\(s=-iw\), \(z=s^2+q^2=q^2-w^2\), and \(q>0\).
The kernels depend on \(s,q\) through \(z\). Define
\[
 \Delta(z)=\frac{\beta G K_v(z)}{\beta+G K_v(z)},\quad
 m(z)=\frac{M K_T(z)}z,\quad
 C_\infty=\frac{6M}{k_b},\quad
 C(z)=C_\infty-6m(z)-\frac{\Delta(z)}z.
\]
Here \(\beta>0\), as at the selected point. The already established pivots
are \(P_D=\beta+GK_v\) and \(P_C=\hat\kappa+2Z_5\sqrt z\), with the
positive-real branch of the square root.

Use the gauge-fixed fields \((n,N,\zeta)\) and
\[
 U=q^2(n-\zeta)-wqN,\qquad Z=\zeta+\frac{U}{3z}.
\]
The three bulk-response terms regroup exactly as
\[
 -\frac{MK_T}{3z^2}U^2+
 \frac{C_\infty z-\Delta}{2}Z^2
 =m(z)\left[(q^2-3w^2)\zeta^2+2q^2n\zeta-2wqN\zeta\right]
   +\frac{zC(z)}2Z^2.
\]
The first bracket is the scalar Einstein quadratic form with coefficient
\(m(z)\). The second term is essential: replacing this expression by a frozen
Einstein coefficient plus a passive beta load would change the action.

## Positive spectral measure for the remaining coefficient

The following representation follows from the spectral theorem for the closed
nonnegative forms; its input is the energy domain, not a fitted DtN function.
For the tensor let \(A_T\) be the operator of
\(E_T=\int\Omega^4|u'|^2\) with zero UV trace in
\(L^2(\Omega^2dr)\). The constant function \(1\) belongs to this Hilbert
space, although it is not in the zero-trace form domain. Let \(\mu_T\) be
its positive spectral measure. The unit-trace solution is
\[
 H_T=1-z(A_T+z)^{-1}1,
 \qquad \frac{K_T(z)}z
 =2\int_{[0,\infty)}\frac{\lambda}{\lambda+z}\,d\mu_T(\lambda).
\]
Indeed, subtracting the resolvent term solves the zero-trace variational
problem, and using the unit-trace function \(1\) as lift in the DtN
definition gives \(K_T=2z\int\Omega^2H_T\).
The nullspace of \(A_T\) is zero: zero derivative energy implies a constant,
and zero UV trace then makes it vanish. Thus \(\mu_T(\{0\})=0\).

For the beta load, use \(L^2(2G\Omega^4dr)\) and the Robin form
\[
 a_\beta(u,v)=2G\int\Omega^6u'\bar v'\,dr+
              \beta u(0)\overline{v(0)}.
\]
Its domain is the full finite-energy space with free trace. Let \(A_\beta\)
be its nonnegative operator and \(\mu_\beta\) the spectral measure of \(1\).
Because \(a_\beta(1,v)=\beta\overline{v(0)}\), the spring-driven solution is
\(H_\beta=1-z(A_\beta+z)^{-1}1\). Its trace equals
\(\beta/(\beta+GK_v)\). Testing with \(1\) yields
\[
 \frac{\Delta(z)}z
 =\int_{[0,\infty)}\frac{\lambda}{\lambda+z}\,d\mu_\beta(\lambda).
\]
The Robin nullspace is also zero when \(\beta>0\). In particular these
ratios are Stieltjes functions and their values at \(z\downarrow0\) are
fixed by the finite masses of the displayed measures.

Write the exact profile integrals as
\(M_{4,\mathrm{bulk}}^2=2M\int\Omega^2dr\) and
\(N_S=2G\int\Omega^4dr\). The BPS identity is
\[
 6M_{4,\mathrm{bulk}}^2+N_S=\frac{6M}{k_b}=C_\infty.
\]
One may verify it without evaluating special functions: the derivative of
\(6M\Omega^2/A'\) is \(12M\Omega^2+2G\Omega^4\), and its endpoint
values are \(-6M/k_b\) and zero. The exact integrals here must not be
replaced by rounded metadata while asserting equality.

Consequently, for the finite positive measure
\(\nu=12M\mu_T+\mu_\beta\),
\[
 C(z)=\int\frac{z}{\lambda+z}\,d\nu(\lambda),\qquad
 \nu([0,\infty))=C_\infty.
\]
In particular \(C(0)=0\), \(0<C(z)<C_\infty\) for real \(z>0\), and
\(C(z)/z\) is Stieltjes. These statements retain the full beta response.

## Exact shift pivot and its right-half-plane certificate

Let \(A_0=b(1-\lambda_K)\). The regrouped action gives
\[
 H_{NN}=q^2\left[A_0-\frac{s^2C(z)}{9z}\right].
\]
Using the positive measure above, rearrange this expression as
\[
 \frac{sH_{NN}}{q^2}
 =\left(A_0-\frac{C_\infty}{9}\right)s+
   \frac19\int\frac{s(\lambda+q^2)}{s^2+\lambda+q^2}\,d\nu(\lambda).
\]
For \(s=\sigma+i\tau\), \(\sigma>0\), and \(c\geq0\),
\[
 \Re\frac{s}{s^2+c}=\frac{\sigma(|s|^2+c)}{|s^2+c|^2}>0.
\]
Thus the sufficient condition
\[
 A_0>\frac{C_\infty}{9}=\frac{2M}{3k_b}
\]
makes \(sH_{NN}/q^2\) strictly positive-real and proves \(H_{NN}\ne0\)
throughout the open right half-plane, for every \(q>0\).

The frozen values satisfy this condition with a large rigorous margin:
\(b=2\) and \(\lambda_K=-0.5535068954004245<-1/2\) give \(A_0>3\).
For \(M=k=1\), \(G=1.2\),
\[
 \frac{2M}{3k_b}=\frac23e^{1/5}<\frac{5}{6},
 \qquad A_0-\frac{C_\infty}{9}>\frac{13}{6}.
\]
The elementary bound \(e^x<(1-x)^{-1}\), \(0<x<1\), suffices; no rounded
exponential or exact identification of \(\lambda_K\) with an IR ratio is used.

Let \(J=\{n,\zeta\}\). The determinant reduction now preserves every pivot:
\[
 \det H_5=P_CP_D\,H_{NN}\det\left(H_{JJ}-H_{JN}H_{NN}^{-1}H_{NJ}\right).
\]
All three displayed pivots are nonzero on this gauge patch. Their elimination
therefore neither creates nor discards any open-right-half-plane zero.

## A direct Cauchy argument for the dynamic lapse pivot

No closure theorem for Bernstein functions is needed. Write
\[
 F(z)=\frac{C(z)}z=\int\frac{1}{\lambda+z}\,d\nu(\lambda),
 \qquad Y(s)=sF(s^2+q^2).
\]
The spectral measure has finite mass \(C_\infty>0\). For \(\sigma=\Re s>0\),
\[
 \Re Y=\sigma\int\frac{|s|^2+q^2+\lambda}
                         {|s^2+q^2+\lambda|^2}\,d\nu>0.
\]
Cauchy--Schwarz for this finite measure gives
\[
 |Y|^2\leq C_\infty\int\frac{|s|^2}
                            {|s^2+q^2+\lambda|^2}\,d\nu
       \leq\frac{C_\infty}{\sigma}\Re Y.
\]
In particular \(Y\ne0\), and
\(\Re(1/Y)=\Re Y/|Y|^2\geq\sigma/C_\infty\).
Define the analytic denominator
\[
 D_N(s,q)=\frac{9A_0}{F(z)}-s^2.
\]
Then
\[
 \Re\frac{D_N}{s}
 =9A_0\Re\frac1Y-\sigma
 \geq\sigma\left(\frac{9A_0}{C_\infty}-1\right)>0.
\]
Thus \(D_N\) does not vanish and \(\Re(s/D_N)>0\).

Let \(\kappa=\hat\kappa\), \(p=\sqrt{s^2+q^2}\), \(\Re p>0\), and
\[
 E(s,q)=b\eta-\Pi_R(p)
       =E_\infty+\frac{\kappa^2y^2}{\kappa+2Z_5p},
 \qquad E_\infty=b\eta-\kappa y^2.
\]
Before the shift elimination the entries of the exact three-field matrix are
\[
 H_{nn}=q^2E+q^4F/9,\qquad
 H_{nN}=H_{Nn}=-isq^3F/9,\qquad
 H_{NN}=q^2(A_0-s^2F/9).
\]
Therefore the lapse pivot after eliminating the shift is exactly
\[
 \frac{H_{nn}^{\rm eff}}{q^2}
 =E+\frac{A_0q^2F}{9A_0-s^2F}
 =E+\frac{A_0q^2}{D_N}.
\]
For \(p=u+iv\), one has \(u>0\) and \(uv=\sigma\tau\). Hence
\[
 \Re\frac{s}{\kappa+2Z_5p}
 =\frac{\sigma(\kappa+2Z_5u)+2Z_5\tau v}
        {|\kappa+2Z_5p|^2}>0.
\]
If \(E_\infty>0\), \(\kappa,Z_5>0\), the two terms in
\[
 \Re\frac{sH_{nn}^{\rm eff}}{q^2}
 =\Re(sE)+A_0q^2\Re(s/D_N)
\]
are positive. This proves the lapse pivot nonzero throughout the open right
half-plane. At the frozen point \(E_\infty=6.214027581601698-3>3\),
so the condition is satisfied with no near-cancellation.

Writing \(S_\zeta\) for the final one-field Schur complement, the complete
factorization on the declared \(q>0\) patch is now
\[
 \det H_5=P_CP_D\,H_{NN}\,H_{nn}^{\rm eff}\,S_\zeta.
\]
All four displayed pivots are holomorphic and nonzero in the open right
half-plane; no complex-frequency zero is lost by these eliminations. This
argument does **not** determine the sign or zeros of \(S_\zeta\).

## Static diagnostic and the unresolved determinant

The continuation to \(s=0\), with fixed \(q>0\), has \(z=q^2>0\) and is
well defined by the same positive resolvents. The shift decouples. Define
\[
 P=b\xi+m(q^2),\quad E=b\eta-\Pi_R(q),\quad
 c=C(q^2)/9,\quad B=b\bar B_4q^2/k^2,
 \quad \Pi_R(q)=\frac{2Z_5\hat\kappa y^2q}{\hat\kappa+2Z_5q}.
\]
The remaining static matrix, divided by \(q^2\), is
\[
 \begin{pmatrix}E+c&2(P+c)\\2(P+c)&2P+4c-B\end{pmatrix},
\]
with determinant
\[
 2P(E-2P)+c(4E-6P)-B(E+c).
\]
At the frozen point \(E>b\eta-\hat\kappa y^2>3\), so its lapse pivot is
positive. The [separate static proof](one_omega_scalar_static_invertibility_lemma_v1.md)
treats its determinant for all \(q>0\) at the frozen coefficients. The
dynamic one-field factor for complex \(s\) still requires an independent
argument; positivity of the kernels and pivots alone does not settle it.

This note certifies both longitudinal-shift and lapse pivots on \(q>0\). It establishes
neither scalar \(q=0\) gauge reduction nor the residual scalar spectrum,
BF/edge or moving-embedding closure, full N7/P4, B4 or B5.
