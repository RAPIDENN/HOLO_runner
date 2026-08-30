# Preregistration: three-stage Einstein--dilaton audit

Date fixed: 2026-08-29

## Blinding boundary

Some published summary values and the existing frozen constraint maximum were
already visible before this audit began.  Perfect blinding is therefore not
claimed.  To prevent target chasing from this point onward:

- the existing inputs are frozen by SHA-256 below;
- the equations, alternative exact solution, metrics, and thresholds are fixed
  here before the new audit output is generated;
- existing output values will not be used to tune the exact reference solution
  or the thresholds;
- comparison occurs only after the stage-1 result has been serialized; and
- stage 3 uses a different representation from stage 1.

## Frozen answer-key candidates

| Candidate | SHA-256 |
|---|---|
| Original published PDF (`A_single_Einstein-Dilaton_geometry_v1_frozen.pdf`) | `95af056f044d761f9f4ed79fc574788c70beeabaef341d726dd846dd7af73e58` |
| Industrial trace | `e1c4b9d8495a563be31c36ceeeea7575b1d46afae74b45394edb77a8ffb06725` |
| Holonomic ansatz | `caed952a68815f8267f8f5ba60f709484041318d5498323e91350501b5eaaf89` |
| Rust ED RHS | `2a44892d782fab8d6667f36775a9a35d49c2869a9b48cb6c0d4ace1153456e2a` |
| Scalar-spectrum artifact | `6e3b56a805d1dec7634d91d2ac58ec29bd3e979c5c02530fd17dc1eba7a9ccb1` |
| SPARC artifact | `a218ead2a7568cfddc5e7c6ce31670aea15fb6cd7e92b9c8e2770257c25f168b` |
| BOSS/growth artifact | `e5b90a18d40d4a2715b808607e064358bd9ed5f87ffcf90474a11a3dc0077118` |
| UV/NIST artifact | `27e84a3632cae471fa7e79c143698743fce11e958e852002b8c647245905f2ae` |

Changing an input hash creates a new audit; it must not silently overwrite this
one.

## Stage 1: sealed derivation

### Declared action and gauge

Use signature `(-,+,+,+,+)` and

\[
S=\frac{1}{2\kappa_5^2}\int d^5x\sqrt{-g}
\left[R-\frac12(\partial\phi)^2-V(\phi)\right].
\]

In domain-wall gauge,

\[
ds^2=e^{2A(u)}\eta_{\mu\nu}dx^\mu dx^\nu+du^2,
\qquad \phi=\phi(u).
\]

Direct variation must give

\[
R_{MN}=\frac12\partial_M\phi\partial_N\phi+\frac13g_{MN}V,
\]

and therefore

\[
\phi''+4A'\phi'=V_{,\phi},\qquad
A''=-\frac16\phi'^2,\qquad
12A'^2-\frac12\phi'^2+V=0.
\]

Primes in these three equations mean `d/du`.  A matter profile cannot be added
to only one equation while retaining the vacuum constraint; a matter action and
its conserved stress tensor are required for a matter-coupled claim.

### Coordinate transform

Define conformal radius by `dz/du = exp(-A)`.  Then

\[
ds^2=e^{2A(z)}(\eta_{\mu\nu}dx^\mu dx^\nu+dz^2)
\]

and the equivalent equations are

\[
\phi_{zz}+3A_z\phi_z=e^{2A}V_{,\phi},\qquad
A_{zz}-A_z^2=-\frac16\phi_z^2,
\]
\[
12A_z^2-\frac12\phi_z^2+e^{2A}V=0.
\]

Thus pure AdS has `A_u=+-1/L` in domain-wall gauge and `A_z=-1/z`
in the usual conformal orientation.  These reference derivatives must not be
mixed.

### Exact reference flow

Use a superpotential only as an independent exact reference, not as a fit:

\[
W(\phi)=\frac6L+\frac{\phi^2}{2L},\qquad
V=\frac12W_{,\phi}^2-\frac13W^2
=-\frac{12}{L^2}-\frac{3\phi^2}{2L^2}
-\frac{\phi^4}{12L^2}.
\]

The first-order flow

\[
\phi'=W_{,\phi},\qquad A'=-W/6
\]

has the exact solution, for `x=(u-u0)/L`,

\[
\phi(u)=\phi_0e^x,\qquad
A(u)=A_0-x-\frac{\phi(u)^2-\phi_0^2}{24}.
\]

It must satisfy all three second-order equations identically.  The quadratic
mass is the physical `m^2=V''(0)=-3/L^2`, safely above the AdS5
Breitenlohner--Freedman bound `m^2 L^2 >= -4`.

## Fixed acceptance metrics

Evaluate finite-difference trace diagnostics on the interior after removing
five samples at each endpoint.

- Kinematic closure: normalized RMS of `d(phi)/du-dphi` and `d(A)/du-dA`
  must each be `<= 1e-2`.
- Hamiltonian constraint: the 95th percentile of
  `|H|/(|12A'^2|+|phi'^2/2|+|V|)` must be `<= 1e-3`.
- Scalar and warp equations: normalized RMS residuals, using the RMS sum of
  their individual terms as scale, must each be `<= 1e-2`.
- Exact reference: analytic residuals must be `<= 1e-12`; an independently
  integrated solution must agree with the exact flow to `<= 1e-7` in maximum
  absolute error on the preregistered interval.
- Coordinate check: the conformal and domain-wall residuals of the exact flow
  must agree at `<= 1e-11` after the declared Jacobian transformation.

Passing an internal file-integrity or recomputation test does not substitute
for these equation-level criteria.

## Stage 2: comparison rules

- Test both interpretations of the frozen polynomial notation:
  `V=-12/L^2-(m_sq/2)phi^2` with stored variable `m_sq=-3`, and the
  physically intended `V=-12/L^2+(m_physical^2/2)phi^2` with
  `m_physical^2=-3/L^2`.
- Report, rather than optimize away, any sign or coordinate mismatch.
- A holonomic construction that imposes only `H=0` is not a full solution
  unless the scalar and dynamical Einstein equations also pass.

## Stage 3: independent adjudication rules

- Recheck the exact flow by direct second-order numerical integration.
- Recheck it after transformation to conformal gauge.
- Classify an observational map as `derived` only if it follows from a declared
  action/dictionary with units and conserved sources.
- Classify parameters selected using the evaluated data as `phenomenological`,
  even when a single global set is shared by every object.
- A null laboratory comparison does not validate a projection kernel that was
  chosen to suppress the signal.
- Cross-domain reuse of one array is reproducibility; it is not by itself a
  physical derivation linking the domains.
