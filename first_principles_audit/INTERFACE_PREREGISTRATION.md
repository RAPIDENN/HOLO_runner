# Preregistration: geometry-to-interaction interface

This stage is frozen before evaluating SPARC, BOSS/DESI, atomic-clock, or
laboratory residuals.  Its only numerical input is the certified
geometry-preserving effective-action artifact
`artifacts/holo_effective_action.json`.

## Question

What part of a four-dimensional interaction follows from the corrected
five-dimensional Einstein--scalar background, and what additional physical
choices are still required?

## Geometry-fixed calculation

1. Canonicalize the scalar by `d chi = sqrt(K(phi)) d phi`.
2. Reconstruct the local superpotential on the monotonic background,
   `W(chi(u)) = -6 A_u(u)`.
3. Verify independently that
   `W_chi = chi_u` and `V = W_chi^2/2 - W^2/3`.
4. Construct the gauge-invariant scalar carrier, up to its common positive
   gravitational normalization, with
   `epsilon_ED = -A_uu/A_u^2`,
   `p = exp(4 A) epsilon_ED`, and
   `w = exp(2 A) epsilon_ED`.
5. Define its shape eigenproblem
   `-d_u(p d_u f_n) = m_n^2 w f_n` and normalization
   `integral w f_n f_m du = delta_nm`.

## Acceptance gates

- The effective-action input certificate already passes.
- `chi(u)` is strictly monotonic.
- `A_uu < 0`, hence `epsilon_ED`, `p`, and `w` are positive everywhere.
- Both carrier integrals are finite and positive on the certified interval.
- The superpotential identities close to absolute error below `1e-10`.
- Under the explicitly labelled Neumann--Neumann trial completion, the
  constant zero mode has unit weighted norm and zero radial energy to numerical
  precision.

## Deliberately unchosen quantities

This stage does **not** choose radial boundary conditions, boundary actions,
the five-dimensional gravitational scale, a map between the finite radial
interval and physical distance, Standard-Model localization, or the Wilson
coefficients coupling the four-dimensional scalar to matter, QCD, fermion
masses, or electromagnetism.  Therefore it cannot yet predict a fifth-force
strength, a clock shift, a galaxy curve, or cosmological growth.

## Blindness rule

No observational table or residual is read by the derivation script.  The
machine-readable certificate must list an empty `observational_inputs_read`
field.  Observations may be opened only after a boundary completion and the
four-dimensional Wilson coefficients have been frozen in a later stage.
