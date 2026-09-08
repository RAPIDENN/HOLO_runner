# Spectral energy proof for the final scalar Schur factor

This note proves an open-right-half-plane result for the **displayed linear
three-field scalar response, at every fixed q>0**, on the selected finite-energy
radial branch. Its inputs are the exact action in
[the sector reduction](verify_one_omega_topological_sector_reduction_v1.py),
[the variational DtN construction](one_omega_variational_dtn_lemma_v1.md),
[the spectral and pivot lemma](one_omega_scalar_shift_pivot_lemma_v1.md), and
[the all-q static proof](one_omega_scalar_static_invertibility_lemma_v1.md).
The theorem uses that static proof, including its exact bounds at the literal
frozen coefficients; it is not a theorem for arbitrary nearby coefficients.
Identification with additional BF, embedding or global sectors is not an input
and is not a conclusion. Finite algebra checks supplement the argument below;
they do not replace its infinite-dimensional form and domain arguments.

## 1. Exact response and assumptions

Write M=M5c>0, b=Mb2>0, k,G,beta,kappa,Z5>0, xi=1, and put
\[
 s=\sigma+i\tau,\quad \sigma>0,\quad w=is,\quad
 z=s^2+q^2=q^2-w^2,\quad q>0.
\]
The BPS profile has Omega(0)=1,
\[
 \Omega'=-k\Omega e^{-a\Omega^2},\quad a=G/(6M),\quad
 k_b=ke^{-a},\quad C_0=M/k_b.
\]
Set
\[
 m(z)=\frac{MK_T(z)}z,\quad
 \Delta(z)=\frac{\beta GK_v(z)}{\beta+GK_v(z)},\quad
 C(z)=6C_0-6m(z)-\frac{\Delta(z)}z,\quad F(z)=C(z)/z.
\]
For the scalar fields (n,N,zeta), abbreviate zeta by \(\zeta\), and define
\[
 U=q^2(n-\zeta)-wqN,\quad u=U+3z\zeta,\quad
 \mathcal E=(q^2-3w^2)\zeta^2+2q^2n\zeta-2wqN\zeta
            =3z\zeta^2+2\zeta U.
\]
Here \(\mathcal E\) is the unit-coefficient scalar Einstein quadratic
**density**, not an equation of motion. The exact reduced density is
\[
\begin{split}
 L_3={b\over2}\big[&3(1-3\lambda_K)w^2\zeta^2
 +2(1-3\lambda_K)wq\zeta N+(1-\lambda_K)q^2N^2\\
 &+4q^2n\zeta+2q^2\zeta^2
 -\bar B_4q^4\zeta^2/k^2+(\eta-\Pi_R/b)q^2n^2\big]
 +m(z)\mathcal E+{F(z)u^2\over18},\\
 \Pi_R&={2Z_5\kappa y^2p\over\kappa+2Z_5p},\qquad
 p=\sqrt z,\quad \Re p>0.
\end{split}                                                     \tag{1}
\]
Products here denote the analytic Fourier quadratic density; real-time
energy below uses the corresponding Hermitian pairing of opposite Fourier
modes, with the formal derivative adjoint retained.

The sufficient coefficient conditions used below are
\[
 A_0=b(1-\lambda_K)>0,\qquad
 B_*=b(1-3\lambda_K)-2C_0>0,\qquad
 E_\infty=b\eta-\kappa y^2>0,                                  \tag{2}
\]
and strict negativity of the last static Schur factor for every q>0.
All hold at the frozen point
\[
 M=k=1,\ G=6/5,\ b=\beta=2,\ \bar B_4=4/5,\
 \kappa=Z_5=1,\ y^2=3,\
 \lambda_K=-0.5535068954004245,\ \eta=3.107013790800849.
\]
Indeed \(C_0=e^{1/5}<5/4\), so \(A_0>3\), \(B_*>5/2\), and
\(E_\infty=3.214027581601698>3\). The separate static proof supplies the
remaining condition. No equality between a decimal coefficient and an exact
exponential integral is assumed.

## 2. Spectral spaces, masses and the beta first moment

Use the closed nonnegative Dirichlet form
\(\int\Omega^4|f'|^2\) in \(L^2(\Omega^2dr)\), with zero UV trace, to
obtain its self-adjoint operator \(A_T\). Let \(\mu_m\) be 2M times the
spectral measure of the constant vector 1. It is finite even though 1 is
**not** in the Dirichlet form domain. The unit-trace solution is
\(1-z(A_T+z)^{-1}1\); the weak Green identity gives
\[
 m(z)=\int {\lambda\over\lambda+z}\,d\mu_m(\lambda),\qquad
 \mu_m([0,\infty))=m_0:=2M\int\Omega^2dr.                      \tag{3}
\]
For the scalar spring use the free-trace Robin form
\[
 a_\beta(f,f)=2G\int\Omega^6|f'|^2dr+\beta|f(0)|^2
 \quad\hbox{in }L^2(2G\Omega^4dr).
\]
Let \(\mu_\beta\) be the spectral measure of 1 for its operator. The
same resolvent construction, with \(a_\beta(1,f)=\beta\overline{f(0)}\),
gives
\[
 {\Delta(z)\over z}=\int{\lambda\over\lambda+z}\,d\mu_\beta,
 \quad \int d\mu_\beta=N_S:=2G\int\Omega^4dr,
 \quad \boxed{\int\lambda\,d\mu_\beta=\beta}.                 \tag{4}
\]
The last identity is the spectral characterization of the form value
\(a_\beta(1,1)\); 1 belongs to the Robin form domain. The weighted form
spaces are complete, have continuous UV trace, and their free-trace compact
smooth cores approximate all finite-energy functions: here P/W=Omega2<=1,
so radial cutoffs have vanishing added energy. In particular the constant
Robin vector is admitted by this domain, not imposed as an extra IR boundary
condition. Both operators have zero kernel, because zero derivative energy
forces a constant and either Dirichlet trace or the positive spring kills it.

The exact BPS mass identity is
\[
 m_0+N_S/6=C_0.                                                \tag{5}
\]
For example, the derivative of \(6M\Omega^2/A'\), where A=log Omega,
is \(12M\Omega^2+2G\Omega^4\), with endpoint values \(-6C_0\) and 0.
Equations (3)--(5) imply
\[
 F=6\int{d\mu_m\over\lambda+z}
       +\int{d\mu_\beta\over\lambda+z}.                       \tag{6}
\]
These are spectral representations of the actual energy-domain operators,
not positive-pole fits. No first moment of \(\mu_m\) is required.

## 3. Exact local realization without a TT domain shift

Using \(u=U+3z\zeta\) and \(\mathcal E=3z\zeta^2+2\zeta U\),
one has the exact identity
\[
 m(z)\mathcal E+\frac13\int{u^2\over\lambda+z}\,d\mu_m
 =m_0\mathcal E+\frac13\int{U^2\over\lambda+z}\,d\mu_m.       \tag{7}
\]
Introduce \(X_T\in L^2(\mu_m)\), with \(g_T=\sqrt{2/3}\), through
\[
 L_T^{\rm aux}=-\tfrac12\int(z+\lambda)X_T^2d\mu_m
                   +\int g_TX_TU\,d\mu_m.
\]
Eliminating it gives the second term on the right of (7). This TT variable
is **not shifted by a multiple of zeta**; such a shift could require the
unavailable moment \(\int\lambda d\mu_m\).

Realize the beta term in (6) by \(X_\beta\in L^2(\mu_\beta)\),
\(g_\beta=1/3\), and density
\[
 -\tfrac12\int(z+\lambda)X_\beta^2d\mu_\beta
             +\int g_\beta X_\beta u\,d\mu_\beta.
\]
Now shift only this variable: \(X_\beta=Y_\beta+3g_\beta\zeta\).
Expansion gives exactly
\[
 -\tfrac12\int(z+\lambda)Y_\beta^2d\mu_\beta
 +\int g_\beta Y_\beta(U-3\lambda\zeta)d\mu_\beta
 +{N_S\over6}\mathcal E-{\beta\over2}\zeta^2.                 \tag{8}
\]
Thus the local Einstein coefficient is C0 and the local spring is beta.
On \(\mathcal H_X=L^2(\mu_m)\oplus L^2(\mu_\beta)\), write
\(X=(X_T,Y_\beta)\), \(g=(g_T,g_\beta)\). Then
\[
 \|g\|^2=2m_0/3+N_S/9=2C_0/3.                               \tag{9}
\]
The spectral form domain is
\(\mathcal Q_X=D(\sqrt\Lambda_T)\oplus D(\sqrt\Lambda_\beta)\),
where Lambda denotes multiplication by lambda. The beta shift is an
invertible continuous map on the total form domain since
\(\int\lambda g_\beta^2d\mu_\beta=\beta/9\). In (8), the apparently
unbounded coupling means the form pairing
\[
 \left|\int\lambda g_\beta\overline{Y_\beta}\,d\mu_\beta\right|
 \leq\sqrt{\beta/9}\,\|\sqrt\Lambda_\beta Y_\beta\|.           \tag{10}
\]
One does not assert \(\Lambda_\beta g_\beta\in L^2\), or require a
second moment. All other spectral couplings use only finite masses.

## 4. Reintegrating the material Robin half-line

Keep a physical longitudinal material scalar \(\varphi(r)\) on a half-line,
with kinetic mass \(2Z_5\int|\dot\varphi|^2dr\). Its potential form before
coupling the lapse is
\[
 v_\varphi=2Z_5\int_0^\infty(|\varphi'|^2+q^2|\varphi|^2)dr
                       +\kappa|\varphi(0)|^2.                \tag{11}
\]
The two identical exteriors account for the factor **2Z5**. The boundary
spring density is \(-\kappa|\varphi(0)-yqn|^2/2\), after choosing the
longitudinal sine/cosine phase. Combining its bare n2 term with foliation
leaves \(E_\infty q^2|n|^2/2\), and its mixed density is
\(\kappa yq\Re(\bar n\varphi(0))\). The form domain is H1 on the
half-line; for q>0 its trace is continuous, for example
\[
 q|\varphi(0)|^2\leq\int(|\varphi'|^2+q^2|\varphi|^2)dr.
\]
The decaying solution has boundary value
\(\varphi(0)=\kappa yqn/(\kappa+2Z_5p)\). Eliminating it changes the
lapse coefficient to
\[
 E_\infty+\frac{\kappa^2y^2}{\kappa+2Z_5p}=b\eta-\Pi_R,
\]
exactly as in (1). It has positive kinetic energy; the longitudinal spatial
phase is unitary and does not change that sign.

## 5. Positive kinetic form after the local shift constraint

To track odd derivatives, use one normalized real spatial harmonic: n,zeta
and the spectral variables have cosine phase, while the shift has the
opposite sine phase, equivalently N=i nu in spatial complex Fourier
notation. With time convention exp(-iwt), U becomes
\(q^2(n-\zeta)+q\dot\nu\). Integrating the auxiliary derivative coupling
by parts in time gives the following real kinetic density, including the
shift terms:
\[
 \tfrac12[3B_*|\dot\zeta|^2+\|\dot X\|^2
                   +2Z_5\int|\dot\varphi|^2dr]
 +q\Re\{\bar\nu(B_*\dot\zeta-\langle\dot X,g\rangle)\}
 +\tfrac12 A_0q^2|\nu|^2.                                   \tag{12}
\]
Here and below Hilbert pairings are linear in the first argument. The shift
constraint is algebraic for q>0. Eliminating it gives the kinetic operator
on \(\mathbb C\oplus\mathcal H_X\)
\[
 K_X=D_0-A_0^{-1}vv^*,\quad
 D_0=\operatorname{diag}(3B_*,I),\quad v=(B_*,-g).
\]
Its exact margin is
\[
 A_0-\langle D_0^{-1}v,v\rangle
 =A_0-B_*/3-\|g\|^2=\boxed{2b/3}>0.                         \tag{13}
\]
Cauchy--Schwarz in the D0 norm therefore proves the operator inequality
\[
 K_X\ \geq\ {2b\over3A_0}D_0>0.                            \tag{14}
\]
Together with the identity on the material mass space
\(L^2(2Z_5dr)\), this is a bounded, uniformly positive kinetic operator K.
This is an infinite-dimensional rank-one form argument, not a count of
positive eigenvalues of a truncation.

## 6. Positive potential from the static Schur result

After the shift, the lapse still has no time derivatives. Its density is
\[
 \tfrac12 E_\infty q^2|n|^2+\Re(\bar n J),\quad
 J=q^2[2(b+C_0)\zeta+\langle X,g\rangle]
                         +\kappa yq\varphi(0).              \tag{15}
\]
Eliminating n adds \(|J|^2/(E_\infty q^2)\) to the potential form, with
real-time action convention \(L=\tfrac12 K[\dot u]-\tfrac12 V[u]\).
The full potential, written to make its domain explicit, is
\[
\begin{split}
 V={}&\int(\lambda+q^2)|X_T|^2d\mu_m
      +\int(\lambda+q^2)|Y_\beta|^2d\mu_\beta+v_\varphi\\
 &+[\beta+b\bar B_4q^4/k^2-2(b+C_0)q^2]|\zeta|^2\\
 &+2\Re\left\{\bar\zeta\left[q^2\langle X,g\rangle
                   +3\int\lambda g_\beta Y_\beta d\mu_\beta\right]\right\}
 +{|J|^2\over E_\infty q^2}.                                \tag{16}
\end{split}
\]
The domain is \(\mathcal Q=\mathbb C\oplus\mathcal Q_X\oplus H^1\),
in \(\mathcal H=\mathbb C\oplus\mathcal H_X\oplus L^2(2Z_5dr)\).
For zeta=0 its restriction Vint is a closed positive form, bounded below
by q2 times the interior Hilbert norm. The nonnegative last square is a
continuous form perturbation: use the finite norm of g and the trace bound
(11). Therefore the Vint norm is equivalent to the ordinary interior form
norm. The zeta-to-interior coupling in (16) is a continuous functional in
that norm, including the beta term by (10).

The Riesz theorem consequently gives a unique minimizing interior vector
\(x_*(\zeta)\in\mathcal Q_X\oplus H^1\), linear in zeta. Completing
squares in this Hilbert form norm, without a finite-dimensional truncation,
gives
\[
 V[\zeta,x]=V_{\rm int}[x-x_*(\zeta)]+d_0(q)|\zeta|^2.       \tag{17}
\]
At s=0 all auxiliary and material inverses exist since z=q2>0, and the
local shift and lapse coefficients are positive. Their Schur eliminations
can be performed in either order. Exact identities (7)--(8) and (11) then
identify \(d_0(q)=-S_\zeta(0,q)\) with the final factor of (1).

For clarity, the static proof uses
\[
 P=b+m(q^2),\quad E=b\eta-\Pi_R(q),\quad c=C(q^2)/9,\quad
 B=b\bar B_4q^2/k^2,
\]
whose remaining matrix divided by q2 is
\(\bigl(\begin{smallmatrix}E+c&2(P+c)\\2(P+c)&2P+4c-B\end{smallmatrix}\bigr)\).
It proves E+c>0 and
\[
 2P(E-2P)+c(4E-6P)-B(E+c)<0\quad\hbox{for every }q>0.
\]
Thus
\(d_0=-q^2[2P(E-2P)+c(4E-6P)-B(E+c)]/(E+c)>0\).
Equation (17) proves that **the entire realized potential is positive**.
It is a closed form and coercive in the Hilbert norm for each fixed q:
Vint is coercive, d0>0, and the triangular map
\((\zeta,x)\mapsto(\zeta,x-x_*(\zeta))\) is bounded and invertible.
No lower bound uniform as q tends to zero is asserted.

## 7. Equivalence of null problems and the energy contradiction

For Re s>0, z avoids the nonpositive real axis. The auxiliary multiplication
operators Lambda+z have regular resolvents. With n,N,zeta prescribed, the
unshifted auxiliary solutions are
\[
 X_T=g_TU/(\lambda+z),\qquad X_\beta=g_\beta u/(\lambda+z).
\]
They belong to the operator domains; after the beta shift the solution
belongs to the form domain, which is all the weak equations require.
The material solution is the unique finite-energy decaying exponential.
These eliminations exactly reproduce (1). Conversely every null vector of
H3 reconstructs these auxiliary and material fields uniquely. Homogeneous
auxiliary modes with vanishing retained fields cannot occur in this half
plane. The local constraints A0 q2 and Einfinity q2 are nonzero; the beta
shift is invertible on the form domain. Thus eliminating local constraints
first is equivalent, at the level of weak null equations, to eliminating the
auxiliary resolvents first. There is no extra homogeneous solution or lost
pivot in this correspondence.

After the local constraints the realized equation is the form equation
\[
 B_s(u,v):=s^2K(u,v)+V(u,v)=0\quad(v\in\mathcal Q).           \tag{18}
\]
For any nonzero u in that domain, (14) and (17) imply
\[
 \boxed{\Re\frac{B_s(u,u)}s
  =\sigma K(u,u)+\frac{\sigma}{|s|^2}V(u,u)>0}.              \tag{19}
\]
Taking v=u contradicts a nonzero solution of (18). Hence H3 has no
nonzero null vector for Re s>0, q>0.

This also proves a positive-real statement for the final scalar factor,
rather than just absence of its zeros. On the subspace zeta=0, Bs/s is
bounded and coercive in the complete norm K+V, for each fixed s in the
half-plane. The complex coercive-form theorem gives a unique solution with
prescribed zeta=1: choose the fixed lift l=(1,0,0), and solve
Bs(u_s,v)=0 for every zero-zeta test v. This existence result follows also
from the closed-range argument and the zero kernel of the adjoint of the
coercive operator. Testing with u_s-l gives the exact weak Green identity
\[
 D(s,q):=-S_\zeta(s,q)=B_s(u_s,l)=B_s(u_s,u_s),\qquad
 \boxed{\Re[D(s,q)/s]>0}.                                   \tag{20}
\]
The scalar coefficient on the left is the Schur response of (18), equal to
the negative action Schur coefficient in (1). This equality concerns the
linear response, not a claim that Bs is Hermitian at complex s.
Local inverse arguments on this fixed form space also give holomorphy.

Finally, the previous pivot proof retains
\[
 \det H_5=(\kappa+2Z_5p)(\beta+GK_v)H_{NN}H_{nn}^{\rm eff}S_\zeta.
\]
Each of the first four factors is holomorphic and nonzero for Re s>0,
q>0. Equation (20) now excludes zeros of the last one. The sign of an
individual conformal coordinate before the constraints is not used as a
physical ghost test.

## Scope of the theorem

For the exact response (1), the BPS finite-energy extension and the stated
frozen point, the remaining scalar determinant is nonzero throughout the
open right half-plane for every q>0. The full proof uses actual positive
spectral measures, the finite beta first moment, the margin (13), the
half-line trace form and the independently established all-q static bound.
The companion must bind its finite algebra to this action and these inputs;
a handful of positive residues or sampled roots cannot establish the theorem.

This result does not supply the alternate scalar gauge treatment at q=0,
limits or resonances on Re s=0, a complete physical mode count, nonlinear
stability, independent moving-embedding equations, BF/edge/global domains,
or a full N7 or P4 closure. Full N7, P4, B4 and B5 remain false. In
particular positivity of this realized scalar response is not a proof of
full theory consistency or any learning capability.
