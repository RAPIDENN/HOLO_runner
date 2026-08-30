# Minimal probe-matter completion

This is a prospective model frozen before any SPARC, growth, clock, or
fifth-force comparison.  It is **not** the historical DOF1 model.

## Additional assumptions

The corrected bulk alone is a holographic background and does not make its
radial modes into particles in our four-dimensional spacetime.  To obtain a
testable interaction, this completion adds the following explicit assumptions:

1. The certified finite radial interval is treated as a physical compact
   interval with one copy, rather than only as an RG coordinate.
2. A consistent Gibbons--Hawking--York/background boundary completion is
   assumed to exist and to add no trace-sector kinetic or mass term.  Its full
   brane/junction dynamics are not derived here.
3. Neumann conditions are explicitly selected for the trace carrier at both
   ends.  They define this benchmark; they do not follow from the holographic
   boundary prescription of the bulk calculation cited below.
4. Standard-Model matter is a non-backreacting probe localized on a fixed
   radial slice; the reported benchmark slice is the UV endpoint.
5. Brane bending and additional localized scalar operators are absent.
6. At tree level matter sees only the induced metric.  Independent gauge
   kinetic, QCD, and fermion-mass Wilson coefficients are set to zero at the
   matching scale.

These assumptions define one minimal branch.  They are not claimed to be
uniquely selected by `ed-trace-solver` or by the frozen trace.

## Normalization from the five-dimensional action

Use

```text
S5 = 1/(2 kappa_5^2) integral sqrt(-G)
     [R - (partial chi)^2/2 - V(chi)].
```

For the dimensionless transverse metric trace `h`, whose trace-sector
contribution is `delta g_mu_nu = (h/4) g_mu_nu`, the decoupled
gravity--scalar calculation of [Arutyunov, Frolov and
Theisen](https://arxiv.org/abs/hep-th/0003116) maps to

```text
S_h^(2) = -3 ell/(128 kappa_5^2) integral du d4x
          [w(u) eta^mu_nu partial_mu h partial_nu h
           + p(u) h_u^2/ell^2],
p = exp(4A) epsilon_ED,
w = exp(2A) epsilon_ED,
epsilon_ED = -A_uu/A_u^2 > 0,
```

for the `(-,+,+,+)` four-dimensional signature.  The remaining longitudinal
trace-sector field does not couple to a conserved probe stress tensor.  The
stored coordinate is dimensionless and `u_phys = ell u`.  Expanding
`h(x,u)=sum q_n(x) f_n(u)` with

```text
integral w f_n f_m du = delta_nm
```

gives the canonical four-dimensional field

```text
varphi_n = sqrt(3 ell) q_n/(8 kappa_5).
```

The induced-metric variation of probe matter is

```text
delta S_m = integral sqrt(-g) h T/8,
```

so that

```text
delta S_m = integral sqrt(-g) (beta_n/M_Pl) varphi_n T,
beta_n(u_m) = M_Pl kappa_5 f_n(u_m)/sqrt(3 ell).
```

The same interval reduces the tensor zero mode to

```text
M_Pl^2 = ell I_g/kappa_5^2,
I_g = integral exp(2A) du,
```

and therefore removes the unknown gravitational normalization:

```text
beta_n(u_m) = sqrt(I_g/3) f_n(u_m).
```

The factors of `ell` cancel in this dimensionless coupling.  This is the
central result of the completion.  The historical fitted `alpha_b` is not
used.

## Neumann zero mode

Natural Neumann conditions admit

```text
f_0 = 1/sqrt(I_w),
I_w = integral w du,
m_0 = 0,
beta_0 = sqrt[I_g/(3 I_w)].
```

It mediates, for nonrelativistic unscreened matter, the conditional potential

```text
V_12(r) = -G m_1 m_2/r [1 + 2 beta_0^2].
```

The coefficient is now a consequence of the declared Neumann benchmark, not
an observational fit.  A different consistent boundary/junction completion
may lift or remove this zero mode.  Whether the massless branch survives
experimental constraints is a later question and is not used to alter the
model before comparison.

The higher modes satisfy

```text
-d_u(p d_u f_n) = mu_n^2 w f_n,
m_n,physical = mu_n/ell,
```

where `ell` is the still-unfixed physical length represented by one radial
unit.  Their dimensionless shapes and couplings are computable, but their
physical ranges are not fixed until `ell` is supplied independently.

## Channels at tree level

- Massive matter couples through its stress-tensor trace and therefore feels a
  scalar force.
- Classical four-dimensional electromagnetism has zero stress-tensor trace, so
  this minimal completion produces no independent direct photon coupling.
- A universal rescaling of all masses does not by itself produce a leading
  clock-ratio signal.  Such a signal requires trace-anomaly or non-universal
  coefficients (`d_e`, `d_g`, `d_mi`) that are outside this benchmark.

Thus the first interaction furnished by the completion is a matter fifth
force, not an atomic-clock line.

## Evidence boundary

The calculation can establish a normalized mode tower and coupling within the
six assumptions above.  It cannot establish that the compact-interval or
Neumann boundary completion is nature's choice, fix `ell`, add screening after
seeing a constraint, or claim a detected interaction.
