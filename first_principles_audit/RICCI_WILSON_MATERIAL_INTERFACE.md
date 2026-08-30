# Ricci, Wilson, and material interface

This note replaces the old single-arrow “instrument closure” with two explicit
physical branches and one conditional matching hypothesis.  It is generated
from the corrected Einstein--scalar completion; it does not reinterpret a
historical fit as a derivation.

Run the executable audit and material reduction with:

```bash
python3 first_principles_audit/audit_ricci_wilson_interface.py
python3 first_principles_audit/derive_material_transducer.py
python3 -m unittest \
  first_principles_audit.test_ricci_wilson_interface \
  first_principles_audit.test_material_transducer -v
```

## 1. What the 5D Ricci quantity really supplies

For the domain-wall metric

```text
ds^2 = exp(2 A(u)) eta_mu_nu dx^mu dx^nu + ell^2 du^2,
```

the physical curvature is `R5=R5_hat/ell^2`, with

```text
R5_hat = -8 A_uu - 20 A_u^2
       = chi_u^2/2 + 5 V/3.
```

The second equality is an independent trace-of-Einstein-equations check.  It
closes to `2.84e-14` in the executable certificate.

The stored clock artefact did not use this derivative.  In the frozen solver
trace, `dA` is a derivative with respect to `log(u)` and

```text
A_u = u * dA_stored.
```

The old clock instead inserted `dA_stored` as though it were `A_u`.  Its
curvature lies near `-21.60 ... -19.09` on the common certified slice; the
correct curvature spans `-13.25 ... -73.47`, with an rms discrepancy of
`26.91`.  The old cosmological factor also contains 526 copies of `E=1` and
only one non-unit entry.  That artefact is retained for provenance, not used as
the corrected curvature clock.

A geometry-only curvature phase can be defined as

```text
g_R(u) = exp(A(u)) sqrt(abs(R5_hat(u))) / [same quantity at u=1],
Theta_R(u) = integral_1^u g_R(s) ds.
```

This is a dimensionless protocol coordinate.  It is not detector proper time.
In a physical compact-interval interpretation, a local curvature frequency and
a rest-mode frequency would be

```text
omega_R(u) = c sqrt(abs(R5_hat(u))) / ell,
omega_n    = c mu_n / ell,
omega_n/omega_R = mu_n/sqrt(abs(R5_hat(u))).
```

The last ratio is fixed by the geometry; seconds still require `ell`.

The historical LOCK5 is not an independent determination of the coupling.  It
uses `1.6664 mHz` and `2.1590 mHz` to infer `xi` and then passes when the same
equation reconstructs `2.1590 mHz`.  It also mixes the bulk `R5` with the
four-dimensional matter estimate `R4 ~= 8 pi G rho/c^2` and rescales the latter
by surface-gravity factors.  In exterior Schwarzschild vacuum `R4=0`; tidal
curvature lives in the Riemann/Weyl tensor.  Consequently the old ISS, lunar,
and altitude rows do not follow from a scalar `xi R4` coupling.

## 2. What the existing “Wilson loop” does and does not do

The frozen JSON implements

```text
ED endpoint A + external alpha' + external c_scalar
    -> sigma_proxy -> m0,
```

not `Wilson loop -> sigma -> ED`.  The verifier correctly checks the arithmetic

```text
sigma_proxy = exp(2 A_IR)/(2 pi alpha'),
m0 = c_scalar sqrt(sigma_proxy),
```

but `alpha'=0.011527 GeV^-2` and `c_scalar=3.55` are external inputs.  There are
no rectangular loops `W(R,T)`, static potential, Creutz ratios, or area-law fit
in that artefact.

HK-core likewise currently contains only elementary `1x1` plaquettes and a
scalar plaquette correlator.  A genuine 4D SU(3) scale calculation needs:

1. ordered rectangular `W(R,T)` loops, averaged over origins and spatial
   orientations;
2. spatial-only smearing, with temporal links untouched;
3. autocorrelation blocking and jackknife propagation through the nonlinear
   ratios;
4. a temporal plateau for `V(R)` and stable Cornell/Creutz fits; and
5. several volumes, lattice spacings, and seeds followed by a continuum limit.

Even that calculation first returns `a^2 sigma`.  GeV units require one
external scale.  Connecting it to the compact length additionally requires a
derived relation

```text
ell sqrt(sigma) = (ell/a) sqrt(a^2 sigma).
```

Neither `ell/a` nor `alpha'/ell^2` is supplied by the present repositories.

There is a second missing interface on the holographic side: the reconstructed
canonical scalar has not been proved to be the string dilaton.  If the standard
IHQCD normalization is assumed, `A_string=A_E +/- chi/sqrt(6)`.  Auditing both
orientations finds no smooth interior minimum on the certified interval.  The
old endpoint formula therefore also assumes an IR hard wall.

## 3. The material transducer that can be derived now

On the conditional compact branch, induced-metric matter has

```text
L_int = sum_n (beta_n/M_Pl) varphi_n T,
m_n = mu_n/ell,
alpha_n = 2 beta_n(source) beta_n(detector).
```

For the same UV slice at source and detector, the geometry fixes
`alpha_n=2 beta_n^2`.  The six positive modes have

```text
sum alpha_n = 7.20230e-5,
mu_n/mu_1 = 1 : 1.686942 : 2.334807 : 2.985996 : 3.651009 : 4.327036.
```

They predict the correlated, scale-free templates

```text
a_scalar/a_Newton
  = sum alpha_n (1 + mu_n r/ell) exp(-mu_n r/ell),

|d a_scalar/dr| / |d a_Newton/dr|
  = sum alpha_n [1 + mu_n r/ell + (mu_n r/ell)^2/2]
                  exp(-mu_n r/ell).
```

A differential mechanical sensor of baseline `L`, mode frequency `omega_m`,
and quality factor `Q` then has

```text
Delta a ~= L (2 G M_source/r^3) * tidal_ratio,

rho u_ddot_i - partial_j(C_ijkl epsilon_kl)
  = rho (a_phi_i-a_frame_i),

q_a(omega) = integral rho U_a dot (a_phi-a_frame) dV /
  {M_a [omega_a^2-omega^2-i omega omega_a/Q_a]},

|Delta x(Omega)| = |Delta a(Omega)| /
  sqrt[(omega_m^2-Omega^2)^2 + (Omega omega_m/Q)^2].
```

This is the usable material transfer law.  Producing a number for a laboratory
requires a source mass and trajectory, `ell` (or a scan), `L`, `omega_m`, `Q`,
and a measured noise spectrum.  The geometry does not populate a mode or fix
its amplitude merely because a Ricci phase can be written down.

The Neumann zero mode is deliberately kept separate.  It has
`alpha_0=0.00589483`; if it remains exactly massless and unscreened, the branch
is already incompatible with Solar-System scalar-tensor bounds.  A new
boundary action may lift or remove it, but must be frozen before looking at
those limits and the whole spectrum must then be recomputed.

At tree level, classical Maxwell theory has `T=0`.  Therefore this universal
completion does not yield a direct atomic-clock line.  Clock ratios or
composition-dependent strain require independently derived anomaly or
non-universal coefficients such as `d_e`, `d_g`, and `d_mi`.

## 4. The non-double-counting rule

The gauge-invariant scalar operator and the compact trace carrier are the same
local Einstein--scalar degree of freedom under a Liouville transformation.
They admit two different physical readings:

- holographic branch: `u` is an RG coordinate and the poles are composite
  hadronic states;
- compact branch: `u` is a physical interval and the poles are propagating
  four-dimensional scalar modes.

They cannot be counted as two independent towers, and a QCD Wilson scale cannot
be used as a laboratory compactification scale without a new UV matching
action.

## 5. Three independent validation rungs

1. **Algebra:** `R5_hat` agrees with the independent stress-tensor trace
   identity; the scalar normalization fixes `beta_n` and `alpha_n`.
2. **Numerics:** finite elements and continuous ODE shooting agree on the mode
   tower; a separate finite-difference derivative reproduces the analytic
   material tidal template below `3e-10` relative error.
3. **External adjudication:** only after the action, boundary conditions,
   physical scale, and detector protocol are frozen are the predictions tested
   against fifth-force, hadronic, clock, or astronomical data.  Failure at this
   rung is reported; it is not repaired by fitting a new coupling to the same
   datum.

Machine-readable outputs are
`artifacts/ricci_wilson_interface_audit.json` and
`artifacts/material_transducer.json`.
