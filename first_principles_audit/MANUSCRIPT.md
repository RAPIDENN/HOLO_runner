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
