# Geometry-preserving effective reconstruction

## What this recovers

The first audit tested the frozen HOLO trace against the polynomial canonical
action declared by the original solver.  That test exposed a mismatch, but it
did not answer the more useful inverse question:

> Is there a healthy scalar--gravity action for which the achieved HOLO warp
> and scalar profiles are a solution?

On the finite frozen interval, the answer is **yes**.  The required action is
non-canonical,

\[
S_{\rm eff}=\frac{1}{2\kappa_5^2}\int d^5x\sqrt{-g}
\left[R-\frac12K(\phi)(\partial\phi)^2-V(\phi)\right],
\]

and the reconstruction finds `K(phi) > 0` everywhere on the certified
interior.  It therefore contains no kinetic ghost there and is equivalent,
through a field redefinition, to a canonical scalar.

This is a geometry-preserving completion.  It retains the operational shared
background instead of replacing it with the independent exact unit-test flow.
It does not claim that the reconstructed functions were predicted before the
trace was known.

## Reconstruction theorem

For

\[
ds^2=e^{2A(u)}\eta_{\mu\nu}dx^\mu dx^\nu+du^2,
\qquad \phi=\phi(u),
\]

the non-canonical equations are

\[
A''=-\frac16K\phi'^2,
\]

\[
12A'^2-\frac12K\phi'^2+V=0,
\]

\[
K(\phi''+4A'\phi')+\frac12K_{,\phi}\phi'^2=V_{,\phi}.
\]

If `phi` is monotonic and `A'' < 0`, define along the trace

\[
K(\phi(u))=-\frac{6A''(u)}{\phi'(u)^2},
\qquad
V(\phi(u))=-3A''(u)-12A'(u)^2.
\]

The first two equations then hold identically.  Differentiating the constraint
and using the warp equation gives the scalar equation, so it also holds wherever
`phi'` is nonzero.  Positivity of `K` follows from `A'' < 0`.

The canonical field is obtained from

\[
\frac{d\chi}{d\phi}=\operatorname{sgn}(\phi')\sqrt{K(\phi)},
\qquad
\chi'(u)=\sqrt{-6A''(u)}.
\]

Thus the same background can be represented either by the stored scalar with a
positive kinetic function or by a canonically normalized scalar with a
reconstructed potential `U(chi)`.

## Why the stored derivative columns looked inconsistent

The original preconditioner rescales the state before calling an untransformed
right-hand side and reverses the scaling afterwards.  Consequently, the
generated trace obeys, to numerical accuracy,

\[
A_{,u}\simeq u\,(dA)_{\rm stored},
\qquad
\phi_{,u}\simeq (d\phi)_{\rm stored}/u,
\]

rather than identifying the stored columns directly with the derivatives.
This explains the first audit's kinematic failures.

It also reveals a useful recovery: the stored deformation

\[
\delta_{\rm stored}=-u(dA)_{\rm stored}-1
\]

is numerically the domain-wall quantity

\[
\delta_{\rm eff}=-A_{,u}-1
\]

for `L=1`.  The reconstructed and stored deformations have correlation greater
than `0.9999999` and RMS difference below `7e-4` on the certified interior.
The operational deformation was therefore preserved even though its derivative
label was not.

## Numerical certificate

The reconstruction uses quintic smoothing splines solely to remove
sub-micro-scale integration noise.  Ten samples at each endpoint are excluded
from the certificate because high-order spline derivatives are boundary
sensitive.  The frozen input remains SHA-256 checked.

The generated certificate reports:

- maximum warp-profile displacement below `2.1e-6`;
- maximum scalar-profile displacement below `9e-8`;
- strictly positive `K(phi)` on all certified samples;
- Einstein constraint, warp equation, and scalar equation residuals at
  floating-point roundoff;
- canonical-field equations at floating-point roundoff; and
- recovery of the stored deformation at the precision above.

Run:

```bash
python3 first_principles_audit/reconstruct_holo_effective_action.py
python3 -m unittest first_principles_audit.test_effective_reconstruction -v
```

Outputs:

- `artifacts/holo_effective_action.json`: tabulated `K(phi)`, `V(phi)`, the
  canonical field, and the reconstructed background;
- `artifacts/holo_effective_action_summary.json`: compact pass/fail certificate.

## Evidence boundary

This reconstruction establishes the existence of a healthy effective
Einstein--scalar completion on the sampled interval.  Because `K` and `V` were
inferred from the achieved geometry, it is an inverse completion rather than an
independent prediction of that geometry.  The next prospective step is to fit a
compact analytic form to `K` and `V`, freeze it, solve its boundary-value problem
without the trace, and then retest the spectral and observational arms.
