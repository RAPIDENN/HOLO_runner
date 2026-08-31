# A first-principles consistency audit and exact baseline for a five-dimensional Einstein--dilaton flow

## Abstract

We perform a three-stage, equation-level audit of a frozen five-dimensional
Einstein--dilaton construction.  The stages are deliberately separated into a
sealed derivation, comparison with frozen candidate results, and independent
adjudication.  Starting from the declared scalar--gravity action, we derive the
domain-wall and conformal-gauge equations without using stored numerical
outputs as targets.  We then construct a new exact flow from the
superpotential

\[
W(\phi)=\frac{6}{L}+\frac{\phi^2}{2L},
\]

which generates

\[
V(\phi)=-\frac{12}{L^2}-\frac{3\phi^2}{2L^2}
        -\frac{\phi^4}{12L^2}
\]

and has ultraviolet mass \(m^2L^2=-3\).  The exact solution satisfies the
complete second-order system symbolically, agrees with an independent
second-order numerical integration to a maximum absolute error
\(4.92\times10^{-14}\), and remains consistent after transformation to
conformal gauge, where the largest residual is \(3.55\times10^{-15}\).

Applying the preregistered tests to the previous frozen trace gives normalized
residuals far above the acceptance thresholds in kinematic closure, the
Hamiltonian constraint, and both dynamical equations.  A separate holonomic
reconstruction satisfies the Hamiltonian constraint but not the scalar or warp
equations of the *declared polynomial canonical model*.  A follow-up inverse
reconstruction resolves the apparent impasse without replacing the achieved
geometry: the same warp and scalar profiles solve a non-canonical effective
action with a strictly positive kinetic function on the certified interval.
The operational deformation is recovered with correlation `0.9999999` and RMS
difference below `7e-4`.  Thus the shared-background instrument is retained,
while its correct action is an inferred effective completion rather than the
polynomial action previously attached to it.  A microscopic junction audit
then shows that functional superpotential matching defines an exactly flat
moduli branch: it forces `m^2=u^4=0`, but also gives a vanishing sextic and is
not selected by the bulk alone.  The finite-endpoint reduction resolves two
physical moduli with a positive kinetic metric.  On the declared separation
slice the minimally induced matter selectors have nonzero linear slopes.
Each selector separately has a covariantly stationary tangent and a nonzero
even jet, but no common tangent exists and the current BPS, quadratic and
sextic brane terms select none.  Minimal scalar matter also carries the inverse
selector and gives correctly signed candidate coefficients `-0.165489` and
`-0.128911` after its standard term is separated.  The constitutive `Y`,
tangent and normalization remain unselected, so a physical `q^2Y` operator is
not yet derived.  A target-independent `F=constant` candidate nearly aligns
the lower-brane kernel (`0.0686272` degrees), but is not exact; formal exact
alignment requires `A'_-=0` outside the certified interval, and the true
level-curve reduction gives the wrong sign for minimal `-Y/C`.  A shifted
`s=C-1` operator could reverse it only as additional physics.  The separate stiff stabilized limit gives seven canonically
normalized positive force residues with `sum(alpha)=0.106765`.  The SPARC input
is recomputed with signed gas and declared stellar mass-to-light factors.  The
stiff force improves test `chi2/point` from 414.23 to 371.58, but remains far
from the empirical RAR at 36.75.  A geometry-matched finite-disk scan with one
global scale runs to its long-range boundary under all declared sensitivity
checks; no finite scale is identified.  P6 and P5 are retained only as
numerical genealogy.  A dedicated `600` audit shows that neither restricting
the test to `R>=0.6 kpc` (`chi2/point=390.85`) nor setting `ell=600 kpc`
(`371.72`) rescues the stiff force.  The train-frozen universal signed
collector reaches `36.75` without per-galaxy parameters, but is exactly the
empirical response a new action sector must derive, not a HOLO prediction.
A separate theory-only extension closes one microscopic part of that problem.
A local \(4+1\), \(z=2\) Clifford fermion coupled to khronon acceleration has a
literal linear bulk density of states.  A filled negative branch and two
stable massive \(z=2\) scalars give a UV-finite static determinant with the
required negative \(|a|^3\) term.  Positive-stiffness geometric Schur matching
then yields \(\mu(x)=1+x-\sqrt{1+x^2}\), and a frozen finite-band kernel passes
the flat linear causal gate.  The actual scalar partners supply only a
quadratic seagull and their same-action continuum has an upper-half-plane pole,
killing that minimal global UV completion.  A compact fifth direction also
changes the strict-IR power; warped constraints, junctions, localization,
sourcing, and lensing remain open.
A covariantly embedded \(3+1\) tilted semimetal survives those two specific
falsifiers at \(q=0\).  One linear and two quadratic momentum directions give
the literal density \(\rho_-(\epsilon)=\epsilon/(8\pi cv)\); an identity tilt
makes the Hamiltonian bounded below and produces a finite occupied lower-band
region.  At declared fixed charge, the same defect-matter ansatz yields the
exact static bracket and a positive finite \(q=0\) acceleration-sector retarded
spectrum, while
tangential projection removes the radial background acceleration for the
prescribed constant-radius embedding.  Inhomogeneous charge redistribution,
finite-\(q\) density and metric channels, director \(SO(3)\), the full
bulk--brane Schur denominator, junctions, and backreaction remain open, so no
force, lensing, or publication claim is made.
The public tables also omit the gas surface-density and
vertical-density maps needed for a unique three-dimensional convolution, so
no complete HOLO galaxy force law is claimed.  The
cosmological and laboratory layers still use extra
coordinate and coupling dictionaries.  The positive results are a
reproducible exact Einstein--dilaton control solution, a healthy effective
completion of the frozen HOLO geometry, and a falsifiable protocol for deciding
which future extensions are genuine predictions.

## 1. Scope and evidential standard

The purpose of this work is not to reproduce a preferred collection of output
numbers.  It asks a narrower question: which statements follow from the
declared action and which require additional assumptions?

The existing programme has already achieved an operational result: one frozen
background is consumed reproducibly by its spectral, galactic, cosmological,
laboratory, and response-operator arms.  The audit does not erase that shared
instrument.  It separates this demonstrated computational architecture from
the stronger question of which action generates the background and which
interfaces have been derived dynamically.

Three evidential categories are kept separate:

1. **Derived:** follows algebraically from the declared action and boundary or
   gauge assumptions.
2. **Numerical:** follows from a derived system under a stated discretization,
   domain, and error criterion.
3. **Phenomenological:** introduces a fitted readout, coordinate dictionary, or
   coupling that is not fixed by the action.

Reusing one stored geometry in several calculations demonstrates a common data
dependency.  It does not, by itself, demonstrate a dynamical unification of the
physical sectors.  This distinction is particularly important here because
the declared action contains only a five-dimensional metric and scalar field;
it contains no galactic baryon action, four-dimensional cosmological matter
sector, electromagnetic clock action, or compactification prescription.

## 2. Declared action and direct variation

We use signature \((- + + + +)\) and the action

\[
S=\frac{1}{2\kappa_5^2}\int d^5x\sqrt{-g}
\left[R-\frac12 g^{MN}\partial_M\phi\partial_N\phi-V(\phi)\right].
\tag{1}
\]

Varying with respect to \(\phi\) gives

\[
\nabla^2\phi-V_{,\phi}=0.
\tag{2}
\]

The metric variation gives

\[
R_{MN}-\frac12g_{MN}R
=\frac12\partial_M\phi\partial_N\phi
-\frac14g_{MN}(\partial\phi)^2-\frac12g_{MN}V.
\tag{3}
\]

Tracing (3) in five dimensions and substituting the result back yields the
equivalent trace-reversed form

\[
R_{MN}=\frac12\partial_M\phi\partial_N\phi+\frac13g_{MN}V.
\tag{4}
\]

For a Poincare-invariant domain wall,

\[
ds^2=e^{2A(u)}\eta_{\mu\nu}dx^\mu dx^\nu+du^2,
\qquad \phi=\phi(u),
\tag{5}
\]

the nonzero curvature components are

\[
R_{uu}=-4(A''+A'^2),\qquad
R_{\mu\nu}=-(A''+4A'^2)g_{\mu\nu}.
\tag{6}
\]

Equations (2) and (4) therefore reduce to

\[
\phi''+4A'\phi'=V_{,\phi},
\tag{7}
\]

\[
A''=-\frac16\phi'^2,
\tag{8}
\]

and the first integral

\[
H\equiv12A'^2-\frac12\phi'^2+V=0.
\tag{9}
\]

Here and through Eq. (9), a prime denotes \(d/du\).  Any numerical trace
claimed to solve Eq. (1) must satisfy the two dynamical equations and the
constraint simultaneously.  Enforcing Eq. (9) alone is insufficient.

### 2.1. Constraint propagation and undeclared matter

Differentiate Eq. (9), then insert Eqs. (7)--(8):

\[
H'=24A'A''-\phi'\phi''+V_{,\phi}\phi'=0.
\tag{10}
\]

Suppose instead that a source is inserted only into the warp equation,
\(A''=-\phi'^2/6-\kappa\rho\), while the scalar equation and vacuum constraint
are left unchanged.  The same calculation gives

\[
H'=-24\kappa A'\rho.
\tag{11}
\]

Thus a nonzero source generically destroys the vacuum constraint.  A
matter-coupled claim requires an explicit matter action, its conserved stress
tensor, and the corresponding modification of every constraint and dynamical
equation.  Equation (11) is an algebraic consistency test, not a numerical
preference.

## 3. Coordinate covariance

Introduce the conformal coordinate by

\[
\frac{dz}{du}=e^{-A}.
\tag{12}
\]

The same metric becomes

\[
ds^2=e^{2A(z)}\left(\eta_{\mu\nu}dx^\mu dx^\nu+dz^2\right).
\tag{13}
\]

Using \(d/du=e^{-A}d/dz\), Eqs. (7)--(9) become

\[
\phi_{zz}+3A_z\phi_z=e^{2A}V_{,\phi},
\tag{14}
\]

\[
A_{zz}-A_z^2=-\frac16\phi_z^2,
\tag{15}
\]

\[
12A_z^2-\frac12\phi_z^2+e^{2A}V=0.
\tag{16}
\]

This transformation also provides a simple convention test.  Pure AdS has a
constant \(A_u=\pm1/L\) in domain-wall gauge, whereas in the usual conformal
orientation \(A_z=-1/z\).  A residual that combines the domain-wall field
equations with a conformal-gauge reference derivative is not coordinate
covariant.

## 4. New exact baseline

For the normalization in Eq. (1), choose a superpotential satisfying

\[
V=\frac12W_{,\phi}^2-\frac13W^2.
\tag{17}
\]

The first-order system

\[
\phi'=W_{,\phi},\qquad A'=-\frac16W
\tag{18}
\]

then implies Eqs. (7)--(9).  This construction is a standard way to generate
scalar--gravity domain walls, but here it is used only as an exact audit
baseline rather than as a fit [1].

Taking

\[
W(\phi)=\frac6L+\frac{\phi^2}{2L}
\tag{19}
\]

gives

\[
V(\phi)=-\frac{12}{L^2}-\frac{3\phi^2}{2L^2}
-\frac{\phi^4}{12L^2}.
\tag{20}
\]

Near \(\phi=0\), the scalar mass is

\[
m^2=V''(0)=-\frac3{L^2},
\tag{21}
\]

which lies above the \(AdS_5\) Breitenlohner--Freedman bound
\(m^2L^2\geq-4\) [2].  With \(x=(u-u_0)/L\), Eq. (18) integrates exactly:

\[
\phi(u)=\phi_0e^x,
\tag{22}
\]

\[
A(u)=A_0-x-\frac{\phi(u)^2-\phi_0^2}{24}.
\tag{23}
\]

Direct substitution produces zero symbolic residual in Eqs. (7)--(9).  This
is the constructive result of the audit: a complete nonlinear solution with a
fixed potential and unambiguous coordinate convention.

This baseline is not presented as a confining QCD background.  Its purpose is
to establish a correct solution and validation pipeline.  A physical glueball
spectrum additionally requires a confining infrared geometry, a well-defined
gauge-invariant fluctuation operator, normalizability, and infrared boundary
conditions.  Those ingredients cannot be replaced by imposing an arbitrary
finite radial cutoff [3,4].

## 5. Three-stage blind protocol

### Stage 1: derive and seal

The action, equations, coordinate transformation, exact solution, metrics, and
thresholds were written to `PREREGISTRATION.md`.  Candidate input files were
identified by SHA-256.  The stage-1 derivation was serialized before candidate
outputs were evaluated.  Perfect historical blinding is not claimed because
some headline values had already been seen; sealing prevents further target
chasing.

### Stage 2: open and compare

The frozen trace was tested under both interpretations of its polynomial mass
notation.  The holonomic reconstruction was tested not only against its imposed
constraint but also against the scalar and warp equations.  Observational code
was examined for fitted parameters and extra dictionaries.

### Stage 3: independent adjudication

The exact solution was independently integrated as a second-order initial
value problem with SciPy's DOP853 method, rather than with the first-order
superpotential equations used to derive it.  It was then transformed to
conformal gauge and re-evaluated using Eqs. (14)--(16).  Finally, claims were
classified without assuming either the previous outputs or the new derivation
to be the answer key.

One protocol implementation defect was encountered: symbolic zero residuals
were initially compared as integers after JSON serialization had converted
them to strings.  The run stopped before Stage 2.  The type check was corrected,
the incident was recorded in `PROTOCOL_DEVIATIONS.md`, and no equation,
threshold, or physical result was changed.

## 6. Results

### 6.1. Exact solution

For \(L=1\), \(u\in[0,2]\), \(A_0=0\), and \(\phi_0=10^{-3}\), the independent
integration gives:

| Check | Maximum absolute discrepancy | Criterion | Result |
|---|---:|---:|---|
| Independent second-order integration | \(4.92\times10^{-14}\) | \(10^{-7}\) | pass |
| Conformal scalar equation | \(1.73\times10^{-18}\) | \(10^{-11}\) | pass |
| Conformal warp equation | \(2.69\times10^{-16}\) | \(10^{-11}\) | pass |
| Conformal constraint | \(3.55\times10^{-15}\) | \(10^{-11}\) | pass |

The full sampled solution, including both radial coordinates, is stored in
`artifacts/exact_ed_baseline.json`.

### 6.2. Frozen trace

The preregistered equation-level tests give:

| Metric | Literal stored potential | Intended BF-sign potential | Criterion |
|---|---:|---:|---:|
| \(\phi\) kinematic normalized RMS | 0.3139 | 0.3139 | \(\leq0.01\) |
| \(A\) kinematic normalized RMS | 0.4615 | 0.4615 | \(\leq0.01\) |
| Constraint normalized p95 | 0.03852 | 0.03851 | \(\leq0.001\) |
| Scalar EOM normalized RMS | 0.3220 | 0.3543 | \(\leq0.01\) |
| Sourced warp EOM normalized RMS | 0.8903 | 0.8903 | \(\leq0.01\) |

No preregistered trace criterion passes under either mass-sign interpretation.
The result is therefore not a disagreement about rounding or a marginal
threshold.  The stored coordinates, derivatives, field equations, and
constraint do not describe one numerical solution of the declared action.

The implementation also combines a domain-wall evolution system with the
quantity \(-uA_u-1\), whose AdS reference belongs to conformal gauge.  In its
sourced mode it modifies only the warp equation while retaining the vacuum
constraint, producing precisely the structural incompatibility in Eq. (11).

### 6.3. Holonomic reconstruction

The analytic reconstruction obtains:

| Metric | Value | Criterion | Result |
|---|---:|---:|---|
| Constraint normalized p95 | \(1.48\times10^{-16}\) | \(\leq0.001\) | pass |
| Scalar EOM normalized RMS | 0.9546 | \(\leq0.01\) | fail |
| Warp EOM normalized RMS | 0.9494 | \(\leq0.01\) | fail |

This is a valid solution of the imposed holonomic constraint but not a full
solution of the Einstein--dilaton equations.  The distinction is decisive: a
constraint can reconstruct one derivative algebraically while leaving the
remaining Euler--Lagrange equations unsatisfied.

### 6.4. Geometry-preserving effective completion

The failed polynomial-action test does not imply that the achieved HOLO
geometry has no consistent action.  Consider instead

\[
S_{\rm eff}=\frac{1}{2\kappa_5^2}\int d^5x\sqrt{-g}
\left[R-\frac12K(\phi)(\partial\phi)^2-V(\phi)\right].
\tag{24}
\]

For monotonic \(\phi(u)\) and \(A''(u)<0\), the inverse definitions

\[
K(\phi(u))=-\frac{6A''(u)}{\phi'(u)^2},\qquad
V(\phi(u))=-3A''(u)-12A'(u)^2
\tag{25}
\]

make the warp equation and Hamiltonian constraint identities.  Differentiating
the constraint then yields the non-canonical scalar equation.  The frozen
profiles satisfy the required monotonicity and null-energy sign throughout the
certified interior after sub-micro-scale spline regularization.

The numerical reconstruction preserves the warp profile to
\(2.04\times10^{-6}\) and the scalar profile to \(8.54\times10^{-8}\).  The
kinetic function remains positive, \(K\in[8.55,9.39\times10^6]\), so no kinetic
ghost is introduced on the interval.  The canonical redefinition

\[
\chi'(u)=\sqrt{-6A''(u)}
\tag{26}
\]

provides a second representation of the same geometry; its largest scalar and
warp residuals are \(1.07\times10^{-14}\) and \(4.44\times10^{-16}\),
respectively.

The original preconditioner explains the derivative-label mismatch: it evolves
a rescaled state through an untransformed right-hand side.  Empirically the
stored arrays obey \(A_{,u}\simeq u(dA)_{\rm stored}\).  Therefore the stored
readout

\[
\delta_{\rm stored}=-u(dA)_{\rm stored}-1
\tag{27}
\]

is precisely the recovered domain-wall deformation
\(\delta_{\rm eff}=-A_{,u}-1\), up to an RMS difference
\(6.88\times10^{-4}\).  The two have correlation \(0.999999905\).  This is why
the observational instrument can remain operational even though the original
derivative interpretation fails the polynomial-action audit.

This completion is inverse: \(K\) and \(V\) were reconstructed from the
geometry.  It proves that a healthy effective action supports the achieved
background on the finite interval; it does not yet prove that compact analytic
forms of those functions predict the geometry from independent boundary data.

## 7. Status of the observational layers

### 7.1. Scalar spectrum

The stored scalar-spectrum calculation treats the trace coordinate as
conformal and transforms it to domain-wall gauge, while the generating solver
uses domain-wall equations.  The reported agreement between the transformed
operators can establish internal covariance of that operator manipulation; it
cannot validate a coordinate-misidentified background.  Since the background
also fails the field equations, the stored mass ratio is not presently a
physical prediction of Eq. (1).

This does not mean Einstein--dilaton models cannot predict glueball spectra.
Confining Einstein--dilaton models with a controlled infrared and calibrated
potential do precisely that [3,4].  It means the spectrum must be recomputed on
a full solution with declared boundary conditions.

### 7.2. SPARC rotation curves

SPARC contains 175 disk galaxies with photometry and resolved rotation curves
[5].  The physical audit constructs
\(V_{\rm bar}^2=V_{\rm gas}|V_{\rm gas}|+0.5V_{\rm disk}^2+0.7V_{\rm bul}^2\)
and recomputes all 3391 points.  A deterministic 122/26/27 galaxy split fixes
the global parameters on train only; validation and test are reported without
refitting or selecting visually favourable galaxies.

On the 621 test points, the train-frozen empirical RAR gives
\(\chi^2/{\rm point}=36.75\) and 14.5% median absolute velocity error.  The
action-derived stiff force gives 371.58, compared with baryons at 414.23 and
the old six-mode P6 trace limit at 414.20.  An order-one Hankel operator applies
the seven Yukawa transfers to each effective disk with one global `ell`; the
training score improves monotonically to the `1e5 kpc` upper grid boundary and
the result survives resolution and radial-tail changes.  Thus disk
cancellation does not rescue the candidate.  The force residual changes sign
at `gbar=6.25719e-10 m/s^2` and grows toward low acceleration, identifying a
missing common state-dependent source or coupling.  Fitting that residual
object by object would reproduce the data by construction and is not evidence.
The universal collector instead uses one train-fitted `g_dagger` and no
per-object coefficient.  Over the sampled `0.08--108.31 kpc` domain it demands
an acceleration multiplier from `1.00033` to `23.9192`; the positive stiff
Yukawa comb is bounded by `1.106765`.  Thus 94.3% of catalogue points require
more than its ceiling and 5.7% require screening below it: changing a single
length cannot solve the mismatch.  This statement is limited to the sampled
galactic domain, not all physical scales.

The universal response does admit a minimal nonlinear nonrelativistic action
target.  Writing `X=|grad Phi|^2/a0^2`, the reconstructed field equation is
`div[mu(sqrt(X)) grad Phi]=4 pi G rho`, with the parametric spherical map
`t=sqrt(gN/a0)`, `mu=1-exp(-t)`, and
`g/a0=t^2/[1-exp(-t)]`.  The reconstruction is single-valued and locally
elliptic for nonzero field, but both principal coefficients tend to zero in
the deep limit, so it is not uniformly elliptic and no global existence or
uniqueness result is claimed.  A numerical constitutive inversion closes to
`3.46e-10`, and a spherical Plummer finite-difference PDE control reaches
`1.26e-5`.  It also proves that the transition radius is
mass-dependent: `0.6 kpc` corresponds to `2.955e8 Msun`, `600 kpc` to
`2.955e14 Msun`, and a `6e10 Msun` baryonic galaxy to `8.55 kpc`.  This action
was reconstructed from the empirical target; it is not derived from the HOLO
bulk and has no relativistic, lensing, or external-field completion yet.
The current canonical HOLO sector cannot hide this collector in its Yukawa
tower: its regular weak-field response scales as `M` and starts with `F~X`,
whereas the deep collector scales as `sqrt(M)` and requires `F~X^(3/2)`.
Positive endpoint potentials change masses and boundary conditions, not that
operator class.  This is a conditional no-go for the present linearized
sector, not for a new derivative or nonperturbative completion.

#### 7.2.1. Local \(4+1\) dimensional \(z=2\) Clifford material

A separate extension now derives the static sign and power from local bulk
fields; it does not modify the evidential status of the compact
Einstein--dilaton model.  Introduce a dynamical khronon \(T\) [8--10],

\[
U_M=-\frac{\nabla_MT}{\sqrt{-G^{PQ}\nabla_PT\nabla_QT}},\qquad
h_{MN}=G_{MN}+U_MU_N,\qquad a_M=U^N\nabla_NU_M .
\]

In coordinates adapted to this foliation, \(\sqrt{-G}=N\sqrt h\).  One local
finite-derivative realization is

\[
\begin{aligned}
S_g={}&\frac{M_5^3}{2}\int d^5x\,N\sqrt h
 [K_{AB}K^{AB}-\lambda K^2+\xi\,{}^{(4)}R
  +\eta_\infty a_Aa^A+B_4\mathcal O_4],\\
S_\Psi={}&\sum_f\int d^5x\sqrt{-G}\,\Psi_f^\dagger
[iD_U-c\Gamma_0(-D_\perp^2)-y a_{\hat A}\Gamma_{\hat A}]\Psi_f,\\
S_b={}&\frac12\sum_{r=1}^{2N_-}\int d^5x\,N\sqrt h
[(D_U\varphi_r)^2-c^2(D_\perp^2\varphi_r)^2
-(\Lambda^2+y^2a^2)\varphi_r^2].
\end{aligned}
\]

Here \(\{\Gamma_I,\Gamma_J\}=2\delta_{IJ}\), \(N_-\) is the number of filled
negative single-particle branches, and the scalar multiplicity is two per
branch.  The fermion is first order in preferred time and second order in the
four spatial directions.  The Stückelberg form of \(T\) carries the preferred
foliation covariantly.  The equal dispersion coefficient, scalar multiplicity,
portal, and regulator mass are frozen microscopic choices, not a protected
supersymmetric identity.

In a uniform flat patch,

\[
H=c|\mathbf p|^2\Gamma_0+y a_{\hat A}\Gamma_{\hat A},\qquad
H^2=(c^2|\mathbf p|^4+y^2a^2)\mathbf1_4,
\]

so a four-component flavour has two copies of each energy
\(E_\pm=\pm\sqrt{c^2|\mathbf p|^4+y^2a^2}\).  For
\(\epsilon=c|\mathbf p|^2\), direct four-momentum counting gives

\[
\rho_-(\epsilon)=\frac{\epsilon}{16\pi^2c^2},\qquad
\rho_1=\frac{N_-}{16\pi^2c^2}.
\]

This is a literal bulk single-particle density of states, not a hyperscaling
proxy.  With \(m=y|a|\), the filled light branch plus the two massive bosonic
zero-point determinants have the UV-finite joint fermion--boson
superdeterminant

\[
\begin{aligned}
\mathcal L_{\rm bath}={}&\rho_1\int_0^\infty d\epsilon\,\epsilon
\{[\sqrt{\epsilon^2+m^2}-\epsilon]
-[\sqrt{\epsilon^2+\Lambda^2+m^2}-\sqrt{\epsilon^2+\Lambda^2}]\}\\
={}&\frac{\rho_1}{3}[(\Lambda^2+m^2)^{3/2}-\Lambda^3-m^3].
\end{aligned}
\]

The leading UV terms cancel inside the joint integrand.  Its small-field
expansion is \(K_2a^2-\rho_1y^3|a|^3/3+O(a^4)\), with the gravitational
normalization kept explicit:

\[
K_2=\frac{\rho_1\Lambda y^2}{2},\qquad
\Delta\eta=\frac{2K_2}{M_5^3}
=\frac{\rho_1\Lambda y^2}{M_5^3},\qquad a_0=\frac{\Lambda}{y}.
\]

For \(n\) spatial dimensions the metric--lapse Schur complement has
\(\eta_c=\xi(n-1)/(n-2)\), or \(3\xi/2\) here.  The critical choice
\(\eta_\infty+\Delta\eta=\eta_c\), with \(\eta_\infty>0\), retains the positive
bath quadratic instead of cancelling it with a negative bare stiffness.  The
fundamental static susceptibility and reduced response are

\[
C(a)=\eta_\infty+\Delta\eta(\sqrt{1+x^2}-x)\geq\eta_\infty,
\qquad
\mu(x)=\frac{\eta_c-C(a)}{\Delta\eta}
=1+x-\sqrt{1+x^2},\quad x=|a|/a_0.
\]

This closes the desired deep constitutive power.  It does not by itself derive
a source response \(g\propto\sqrt M\): that also requires a matter coupling and
the nonlinear boundary-value problem.

Thus the desired cubic sign does not destroy the lapse principal rank.  The
local flat count is six khronometric gravitational degrees of freedom (five
tensor plus one scalar), plus the optional dilaton.  The bath gives no lapse
or shift time derivative, and the first-order fermion constraints form a
regular second-class block.  This is not yet a warped or boundary constraint
analysis, and the critical relation is codimension one with no derived Ward
protection or dynamical selection.

The time-dependent check is deliberately separate.  For a frozen symmetric
energy band, put \(s=cq^2/4\) and \(\gamma=\rho_1y^2\).  Its endpoint is denoted
by \(\Lambda\) for comparison with the static scale, but this equality is a
frozen diagnostic convention, not a result of the local action.  The exact
Euclidean particle--hole bubble is

\[
\begin{aligned}
\Pi_E(\Omega,q)={}&\gamma\int_0^\Lambda d\epsilon\,\epsilon
\frac{4(\epsilon+s)}{\Omega^2+4(\epsilon+s)^2}\\
={}&\gamma\left[\Lambda-\frac{|\Omega|}{2}
\left(\tan^{-1}\frac{2(\Lambda+s)}{|\Omega|}
-\tan^{-1}\frac{2s}{|\Omega|}\right)
-\frac{s}{2}\log\frac{\Omega^2+4(\Lambda+s)^2}
{\Omega^2+4s^2}\right].
\end{aligned}
\]

Its retarded continuation has positive spectral density

\[
\Pi_R(\omega,q)=\int_{\nu_-}^{\nu_+}d\nu\,
\frac{2\nu\sigma_q(\nu)}{\nu^2-(\omega+i0)^2},\qquad
\nu_-=\frac{cq^2}{2},\quad \nu_+=2\Lambda+\frac{cq^2}{2},\quad
\sigma_q(\nu)=\frac{\gamma}{4}(\nu-\nu_-).
\]

At \(q=0\),
\([\Pi_E(0,0)-\Pi_E(\Omega,0)]/2
=\pi\gamma|\Omega|/8+O(\Omega^2/\Lambda)\).  At nonzero momentum the cut begins
at \(cq^2/2\), so a uniform \(q^2|\omega|\) truncation is invalid in the
\(\omega\sim q^2\) regime.

For the exact geometric elimination, define
\(\pi_R=\Pi_R/M_5^3\), \(C_R=\eta_\infty+\pi_R\),
\(\pi_0=\Pi_R(0,0)/M_5^3\), and
\(\widehat\pi_R=\pi_0-\pi_R\), with
\(\eta_\infty+\pi_0=\eta_c=B_g^2/A_g\).  Then

\[
H_R=\frac{B_g^2}{C_R}-A_g
=A_g\frac{\widehat\pi_R}{\eta_c-\widehat\pi_R},\qquad
D_R=-Q_\zeta\omega^2+B_4q^4+q^2H_R.
\]

The positive Stieltjes measure makes the Schur response complete-Bernstein.
For \(Q_\zeta>0\), \(B_4\geq0\), and positive \(C\), the corresponding
positive-real test excludes upper-half-plane zeros in this frozen flat
finite-band model.  This is a full-kernel linear stability result for that
regulator, not a nonlinear global theorem.

The same-action continuum fails the stronger dynamical gate.  With an
intermediate energy cutoff \(R\), the light fermion and the two scalar seagulls
give at \(q=0\)

\[
\begin{aligned}
\Pi_E^{\rm same}(\Omega,0;R)=\gamma[&R-\tfrac{|\Omega|}{2}
\tan^{-1}\tfrac{2R}{|\Omega|}-\sqrt{R^2+\Lambda^2}+\Lambda]\\
&\xrightarrow{R\to\infty}
\gamma(\Lambda-\tfrac{\pi|\Omega|}{4}).
\end{aligned}
\]

The \(a^2\varphi^2\) portal has no order-\(a^2\) scalar bubble or branch cut
around \(a=0\); it cancels the static divergence but not the fermion's
unbounded spectral tail.  Critical matching therefore gives on \(z=ip\)

\[
C(ip)=\eta_c-\kappa p,\qquad
\kappa=\frac{\pi\rho_1y^2}{4M_5^3}.
\]

It crosses at \(p_*=\eta_c/\kappa\).  For \(B_4=0\), the exact Schur inverse has
the positive root

\[
p_+=\frac{Q_\zeta\eta_c+
\sqrt{Q_\zeta^2\eta_c^2+4Q_\zeta A_g\kappa^2q^2}}
{2Q_\zeta\kappa}>p_*,\qquad q>0.
\]

Finite \(B_4\geq0\) cannot remove it because the inverse runs from minus
infinity just above \(p_*\) to plus infinity at large \(p\).  At nonzero
momentum there is also an uncancelled
\(-\gamma cq^2\log R/4\), so a \((D_Ba_A)^2\) counterterm and finite
renormalization condition are required.  Thus the static multiplet is only a
conditional EFT below its matter scale.  A physical finite band or healthy
partners with the missing linear spectral response must replace it before the
same-action time-stability gate can pass.

The construction cannot be transplanted to the earlier \(z=3/2\) Lifshitz
candidate.  On
\(ds^2=L^2[du^2-e^{2zu}dt^2+e^{2u}d\mathbf x^2]\), \(T=t\) gives
\(a_{\hat u}=z/L\neq0\).  The material is already gapped by \(yz/L\), so
tangential perturbations start analytically at quadratic order and the
\(-|a|^3\) term disappears; the hyperbolic constant-time slice also lacks the
flat linear infrared measure.  Nor does a finite compact fifth direction
preserve the cubic: below its first KK gap only three spatial momenta remain,
so \(\rho(\epsilon)\propto\epsilon^{1/2}\) and the filled-sea nonanalyticity is
\(|a|^{5/2}\), or analytic if there is no zero mode.  A gapless radial continuum
would restore four-dimensional state counting only after localized
four-dimensional gravity and matter and the brane radial Green determinant
have been derived.

Finally, the finite band used for the retarded test is not generated by the
unbounded local fermion--boson determinant above.  Its hard upper edge carries
a regulator logarithm, while the calculation just given shows that the
minimal same-action alternative fails globally.  The achieved result is
therefore an exact local static microscopic completion plus a separate flat
finite-band causal gate.  It is not a compact HOLO mechanism, force or lensing
law, or publication result.

#### 7.2.2. Covariant-defect tilted semimetal

The scalar-multiplet no-go can be bypassed by changing the material rather
than its regulator.  Embed a timelike \(3+1\) defect as \(X^M(\xi)\), with
\(e_\mu{}^M=\partial_\mu X^M\), induced metric
\(\gamma_{\mu\nu}=G_{MN}e_\mu{}^Me_\nu{}^N\), and unit normal \(s^M\).  The
normalized pullback of the bulk khronon and its tangential acceleration are

\[
u_\mu=\frac{e_\mu{}^MU_M}
{\sqrt{-\gamma^{\alpha\beta}e_\alpha{}^PU_Pe_\beta{}^QU_Q}},\qquad
P_{\mu\nu}=\gamma_{\mu\nu}+u_\mu u_\nu,\qquad
\mathcal A_\mu=P_\mu{}^\nu e_\nu{}^Ma_M.
\]

For the prescribed constant-radius embedding, a radial background
\(a_M\propto s_M\) is projected out and does not gap the defect bath.  This is
a kinematic projection, not a derived embedding.  With a unit spatial director
\(n^\mu\), define
\(P_\perp^{\mu\nu}=P^{\mu\nu}-n^\mu n^\nu\),
\(D_\parallel=n^\mu D_\mu\), and
\(D_\perp^2=P_\perp^{\mu\nu}D_\mu D_\nu\).  On the prescribed embedding and
director background, a self-adjointly symmetrized covariant local
finite-derivative defect-matter ansatz is

\[
\begin{aligned}
S_{\rm sm}&=\int_\Sigma d^4\xi\sqrt{-\gamma}\,
\Psi^\dagger(iD_u-\mathcal H)\Psi,\\
\mathcal H&=\frac{\mathcal E^2}{\Lambda}\mathbf1_4
+v(-iD_\parallel)\Gamma_0+c(-D_\perp^2)\Gamma_1
+y\mathcal A_i\Gamma_{i+1},\\
\mathcal E^2&=v^2(-D_\parallel^2)+c^2(D_\perp^2)^2,
\qquad \{\Gamma_A,\Gamma_B\}=2\delta_{AB}.
\end{aligned}
\]

All bulk indices enter through pullbacks, so the defect-matter measure and
ansatz are covariant under five-dimensional diffeomorphisms.  For a level-set wall
\(\Phi_\Sigma(X)=0\), the same measure is
\(\int d^5X\sqrt{-G}\,\delta(\Phi_\Sigma)
\sqrt{G^{MN}\nabla_M\Phi_\Sigma\nabla_N\Phi_\Sigma}\,\mathcal L_{\rm sm}\).

In a uniform flat patch,

\[
\epsilon^2=v^2k_\parallel^2+c^2k_\perp^4,\qquad
E_\pm=\frac{\epsilon^2}{\Lambda}
\pm\sqrt{\epsilon^2+y^2|\mathcal A|^2},
\]

twice per four-component flavour.  The identity tilt makes the Hamiltonian
bounded below and leaves a finite negative lower-band interval
\(0<\epsilon<\Lambda\) at zero acceleration.  Direct three-momentum counting
gives, per lower-band copy,

\[
\frac{N(\epsilon)}{V_3}=\frac{\epsilon^2}{16\pi cv},\qquad
\rho_-(\epsilon)=\frac{\epsilon}{8\pi cv}.
\]

This is the required literal linear density without a radial continuum.  Let
\(N_{\rm occ}\) count occupied lower-band copies and
\(\rho_1=N_{\rm occ}/(8\pi cv)\).  The canonical sector with

\[
n_{\rm fix}=\frac{\rho_1\Lambda^2}{2},\qquad
\mu_F(\mathcal A)=\Lambda-
\sqrt{\Lambda^2+y^2|\mathcal A|^2}
\]

fills the same lowest-state interval \(0<\epsilon<\Lambda\) for every uniform
\(\mathcal A\).  The identity tilt then cancels from the energy difference,
and the same local bounded Hamiltonian gives exactly

\[
\begin{aligned}
\mathcal L_{\rm sm}(\mathcal A)
&=\rho_1\int_0^\Lambda d\epsilon\,\epsilon
[\sqrt{\epsilon^2+y^2|\mathcal A|^2}-\epsilon]\\
&=\frac{\rho_1}{3}
[(\Lambda^2+y^2\mathcal A^2)^{3/2}-\Lambda^3-y^3|\mathcal A|^3].
\end{aligned}
\]

No regulator scalar or imposed hard cutoff has entered.  The state choice is
essential: at fixed zero chemical potential the answer differs beginning at
order \(\mathcal A^4\).

The normalization is a brane one.  For

\[
S_{\rm br,g}=\frac{M_4^2}{2}\int_\Sigma d^4\xi\sqrt{-\gamma}
[\xi_{\rm br}\,{}^{(3)}R+\eta_{\infty,{\rm br}}\mathcal A^2+\cdots],
\]

the static Hessian and local induced-metric matching are

\[
\Pi_0=\rho_1y^2\Lambda,\qquad
\Delta\eta_{\rm br}=\frac{\Pi_0}{M_4^2},\qquad
\eta_{c,{\rm br}}=2\xi_{\rm br},\qquad
\eta_{\infty,{\rm br}}+\Delta\eta_{\rm br}=\eta_{c,{\rm br}}.
\]

They give the same static reduced coefficient

\[
\mu(x)=1+x-\sqrt{1+x^2},\qquad x=|\mathcal A|/(\Lambda/y).
\]

This is only a local \(3+1\) induced-metric witness.  It must not be replaced
by the bulk \(M_5^3\), \(3\xi/2\) matching, and it is not the exact
bulk--brane junction Schur complement.

The finite occupied region also supplies a same-ansatz dynamical result at zero
spatial momentum.  With \(\gamma_{\rm sm}=\rho_1y^2\),

\[
\begin{aligned}
\Pi_E(\Omega,0)
&=\gamma_{\rm sm}\int_0^\Lambda d\epsilon\,\epsilon
\frac{4\epsilon}{\Omega^2+4\epsilon^2}\\
&=\gamma_{\rm sm}\left[\Lambda-\frac{|\Omega|}{2}
\tan^{-1}\frac{2\Lambda}{|\Omega|}\right],\\
\Pi_R(\omega,0)&=\int_0^{2\Lambda}d\nu\,
\frac{2\nu\sigma(\nu)}{\nu^2-(\omega+i0)^2},\qquad
\sigma(\nu)=\frac{\gamma_{\rm sm}\nu}{4}>0.
\end{aligned}
\]

The exact static bracket and positive finite \(q=0\) acceleration spectral band
therefore comes from one defect-matter ansatz and one declared state, without the scalar
multiplet's unbounded spectral tail.

This is not yet a complete mechanism.  Fixed total charge in an inhomogeneous
\(\mathcal A(\mathbf x)\) allows density redistribution, so the uniform bracket
has not been proved to be a local functional; enforcing local filling by a
gauge field adds its Gauss-law and electrostatic sector.  At finite momentum,
the acceleration vertex contains both interband and gapless lower-band
intraband transitions.  The density, lapse, and induced-metric vertices bring
additional Fermi-surface channels, and neither their full spectral matrix nor
the exact bulk--brane Schur stability bound has been closed.  The fixed
director also breaks continuous \(SO(3)\) to \(SO(2)\).  Three orthogonal
copies restore background and quadratic-tensor isotropy but not the full
finite-momentum correlator, so a covariant director/solid action and stable
orientational sector are still required.

Finally, the full bulk-plus-brane variation, junction conditions, constraint
rank, warped backreaction, and all-channel quasinormal spectrum remain open.
Without those gates and a matter-source boundary-value solution, this is not a
force law, lensing law, physical HOLO completion, or publication result.

The axisymmetric controls also expose why the algebraic score is not yet a
disk solution.  A cylindrical Plummer test converges at second order
(`L2=2.21e-3`, coarse/fine `4.00`), but a flattened Miyamoto--Nagai algebraic
field has normalized curl `0.0211`.  The local 175-galaxy tables do not identify
`rho(R,z)`, component thicknesses, or PDE boundary conditions, so the physical
SPARC PDE fails closed.  The `36.75` score remains a non-PDE mid-plane
diagnostic.
The five-parameter legacy P5 refit gives 290.98, reaches all five bounds, and
is retained only as rejected provenance.  RAR is an empirical target, not
relabelled as HOLO; a new external holdout remains necessary.

The scale layer supplies an additional conditional no-go.  If the first stiff
mode is identified with the legacy `1.600006 GeV` endpoint proxy, it requires
`ell=3.58248e-17 m` and a `1.23329e-16 m` range.  The SPARC scan saturates at
`ell=1e5 kpc`, which would instead imply `f0=4.49168e-18 Hz`, a `7.05484 Gyr`
period, and a `3.44256e5 kpc` range.  The lengths differ by `8.61325e40`.
Neither endpoint is a measurement, but one `ell` cannot support both readings;
a separate ultralight sector or a derived UV scale map is required.

### 7.3. Cosmological growth

The growth layer identifies the trace coordinate through
\(z_{\rm trace}=1+z_{\rm cosmo}\) and then sets \(N=-\ln z_{\rm trace}\).  This is
a declared dictionary, not a result of Eq. (1).  The five-dimensional
Poincare-domain-wall ansatz contains neither a four-dimensional FRW metric nor
a cosmological matter stress tensor.  BOSS and Planck provide valid comparison
data [6,7], but agreement after an extra dictionary tests the composite
phenomenological model, not the scalar--gravity action alone.

### 7.4. Laboratory projection

The UV kernel and conversion to physical time introduce additional coupling
assumptions.  The stored comparison has \(\chi^2/n=22.59\) and Pearson
\(r=-0.055\).  A near-zero correlation is a null result; it cannot select or
validate a projection kernel chosen to suppress infrared contributions.  A
laboratory prediction requires an explicit matter coupling, units for the
radial/time dictionary, and a noise model fixed before comparison.

## 8. Remaining closure boundary

There is a simple dependency obstruction.  Variation of Eq. (1) can produce
only equations for \(g_{MN}\) and \(\phi\).  None of the following objects occurs
in the action or the domain-wall ansatz:

- a baryonic density or disk stress tensor;
- a four-dimensional FRW scale factor and conserved matter density;
- an electromagnetic field or atomic transition;
- a map from holographic radius to galaxy radius, cosmological redshift, or
  laboratory time.

Therefore those response laws cannot be uniquely derived from Eq. (1), nor from
the reconstructed bulk action alone.  Any
such map is an additional model ingredient and must be varied, dimensionally
normalized, and independently tested.  This does not undo the common-background
architecture or claim that cross-domain couplings are impossible.  It identifies
the remaining interface terms required to promote the operational unification
to a forward dynamical prediction.

## 9. Constructive next model

A physically closed extension should begin from

\[
S_{\rm total}=S_{\rm eff}+S_{\rm matter}+S_{\rm EM}+S_{\rm interface},
\tag{28}
\]

where every new term is explicit.  A minimal research programme is:

1. Choose a potential with asymptotically AdS ultraviolet behaviour and a
   confining infrared; solve the complete vacuum equations with convergence
   and constraint propagation tests.
   The reconstructed `K(phi)` and `V(phi)` provide the geometry-preserving
   starting data for this analytic compression.
2. Derive the gauge-invariant scalar fluctuation operator on that solution and
   fix normalizable UV/IR boundary conditions before computing eigenvalues.
3. Calibrate only the minimal QCD potential parameters on a declared training
   set; reserve lattice observables for validation.
4. If galaxies or cosmology are retained, specify a separate four-dimensional
   effective action obtained by an explicit reduction or brane embedding.
   Derive its Poisson/FRW and perturbation equations from that action.
5. If laboratory clocks are retained, declare the electromagnetic/matter
   coupling and its dimensional scale before opening the data.
6. Use nested or external held-out datasets and report likelihoods relative to
   matched baselines with the parameter count included.

The exact flow in Section 4 is the unit test for this programme.  It is not the
final phenomenological geometry; it proves that the solver, coordinate
transformation, residual definitions, and independent-integration machinery can
all succeed on a known nonlinear solution.

## 10. Reproducibility

From the `HOLO_runner` repository root:

```bash
python3 first_principles_audit/derive_and_audit.py
python3 -m unittest first_principles_audit.test_derive_and_audit -v
```

The principal outputs are:

- `artifacts/stage1_sealed_derivation.json`;
- `artifacts/stage2_comparison.json`;
- `artifacts/stage3_adjudication.json`;
- `artifacts/exact_ed_baseline.json`;
- `artifacts/holo_effective_action.json`;
- `artifacts/holo_effective_action_summary.json`;
- `artifacts/ed_audit.json`.

All frozen candidate inputs are hash-checked.  A changed hash aborts the run and
requires a new audit rather than silently updating the comparison.

## 11. Conclusion

The HOLO programme has achieved a reproducible shared-background instrument:
the same frozen geometry and deformation are propagated through multiple
observational arms.  The three-stage test shows that the original polynomial
canonical action and derivative labels do not generate that trace as stated.
The geometry-preserving reconstruction then supplies the missing positive
result: a non-canonical Einstein--scalar action with \(K>0\) supports the same
warp and scalar profiles, and its canonical field representation closes the
full equations at floating-point precision.

The work therefore survives in a sharper form.  It now contains a new exact
control flow with \(m^2L^2=-3\), a healthy effective completion of the actual
HOLO background, an independently checked equation-level suite, and an explicit
list of interface terms still needed for forward cross-domain predictions.  The
existing spectral and observational arms are retained as operational results
and phenomenological hypotheses; their next decisive test is rerunning them on
a prospectively frozen analytic completion with held-out data.

The khronon--Clifford extension adds a different, theory-only positive result:
it derives the literal linear density of states, the negative cubic static
term, the \(M_5^3\)-normalized geometric matching, and a stable flat finite-band
linear kernel.  It does not close the compactification problem: the KK infrared
power is \(5/2\), the Lifshitz radial acceleration gaps the candidate, and the
minimal same-action continuum has an explicit upper-half-plane pole.  Healthy
alternative UV partners, warped constraints, backreaction, junctions,
localization, source, and lensing sectors remain to be derived.

The covariant-defect tilted semimetal improves the microscopic status without
crossing that evidential boundary.  Its local bounded-below Hamiltonian derives
the literal linear density of states, the exact uniform fixed-charge bracket,
and the positive same-ansatz \(q=0\) acceleration spectral band; for the
prescribed constant-radius embedding, the defect projection also removes the
radial background acceleration.  Its local normalization is
\(M_4^2\) with \(\eta_{c,{\rm br}}=2\xi_{\rm br}\), not the bulk matching.
Finite-\(q\) acceleration, density and metric intraband channels, local
inhomogeneous charge control, continuous \(SO(3)\), the exact bulk--brane
Schur complement, junction rank, and warped backreaction remain to be closed
before any force or lensing calculation.

## References

1. O. DeWolfe, D. Z. Freedman, S. S. Gubser, and A. Karch, “Modeling the fifth
   dimension with scalars and gravity,” *Phys. Rev. D* **62**, 046008 (2000),
   [doi:10.1103/PhysRevD.62.046008](https://doi.org/10.1103/PhysRevD.62.046008),
   [arXiv:hep-th/9909134](https://arxiv.org/abs/hep-th/9909134).
2. P. Breitenlohner and D. Z. Freedman, “Stability in gauged extended
   supergravity,” *Annals of Physics* **144**, 249--281 (1982),
   [doi:10.1016/0003-4916(82)90116-6](https://doi.org/10.1016/0003-4916(82)90116-6).
3. U. Gursoy, E. Kiritsis, and F. Nitti, “Exploring improved holographic
   theories for QCD: Part II,” *JHEP* **02**, 019 (2008),
   [arXiv:0707.1349](https://arxiv.org/abs/0707.1349).
4. U. Gursoy, E. Kiritsis, L. Mazzanti, G. Michalogiorgakis, and F. Nitti,
   “Improved Holographic QCD,” *Lect. Notes Phys.* **828**, 79--146 (2011),
   [arXiv:1006.5461](https://arxiv.org/abs/1006.5461).
5. F. Lelli, S. S. McGaugh, and J. M. Schombert, “SPARC: Mass Models for 175
   Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves,”
   *Astron. J.* **152**, 157 (2016),
   [arXiv:1606.09251](https://arxiv.org/abs/1606.09251).
6. S. Alam et al., “The clustering of galaxies in the completed SDSS-III
   Baryon Oscillation Spectroscopic Survey,” *Mon. Not. R. Astron. Soc.*
   **470**, 2617--2652 (2017),
   [arXiv:1607.03155](https://arxiv.org/abs/1607.03155).
7. Planck Collaboration, “Planck 2018 results. VI. Cosmological parameters,”
   *Astron. Astrophys.* **641**, A6 (2020),
   [doi:10.1051/0004-6361/201833910](https://doi.org/10.1051/0004-6361/201833910),
   [arXiv:1807.06209](https://arxiv.org/abs/1807.06209).
8. D. Blas, O. Pujol\`as, and S. Sibiryakov, “A healthy extension of Horava
   gravity,” *Phys. Rev. Lett.* **104**, 181302 (2010),
   [doi:10.1103/PhysRevLett.104.181302](https://doi.org/10.1103/PhysRevLett.104.181302),
   [arXiv:0909.3525](https://arxiv.org/abs/0909.3525).
9. W. Donnelly and T. Jacobson, “Hamiltonian structure of Horava gravity,”
   *Phys. Rev. D* **84**, 104019 (2011),
   [doi:10.1103/PhysRevD.84.104019](https://doi.org/10.1103/PhysRevD.84.104019),
   [arXiv:1106.2131](https://arxiv.org/abs/1106.2131).
10. L. Blanchet and S. Marsat, “Modified gravity approach based on a preferred
    time foliation,” *Phys. Rev. D* **84**, 044056 (2011),
    [doi:10.1103/PhysRevD.84.044056](https://doi.org/10.1103/PhysRevD.84.044056),
    [arXiv:1107.5264](https://arxiv.org/abs/1107.5264).
