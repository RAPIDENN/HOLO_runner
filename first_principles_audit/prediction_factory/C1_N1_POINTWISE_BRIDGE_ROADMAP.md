# C1/N1 pointwise bridge — corrected status (2026-09-04)

Branch: `checkpoint/c1-n1-restricted-v5658-20260903`. All work is local; nothing
in this chain has been pushed.

## Verdict

`uniform_N_to_infinity_bridge_pass`, `C1_ACTION_pass`, `N1_ACTION_pass` and
`C1_N1_promotion_authorized` remain **False**.

The byte-pinned Route C implementation cannot supply the claimed uniform
bridge. It accepts only `N in {1,2,3}` and every tangential field depends on
`theta = x0 + x1`, whereas the target class contains arbitrary `H^s(T^4)` free
data. This is an exact non-density obstruction, not a numerical failure.

It refutes the current Route C strategy. It does not refute the continuum
Euler--Green theorem or a future arbitrary-N, full-T4 Route C implementation.

## Exact obstruction

Let `A = {g(x0+x1)}` and choose the admissible free datum
`f(x) = (1/4) cos(x2)` in `common.log_Omega`, leaving the other background data
inside the open margins. Then `Omega >= exp(-1/4) > 0.5`, and with normalized
Haar measure on `T^4`,

```text
<f, g> = (1/4) mean_x2(cos x2) mean_x0,x1(g) = 0
||f||_2^2 = 1/32
inf_{g in A} ||f-g||_2^2 >= 1/32.
```

Therefore the implemented theta-only family is not dense in the declared
class. v5.6.6.16 records the pinned-source AST guard, the exact Fubini proof and
an independent Fourier canary.

## Evidence ledger

| Gate | What survives audit | What it does not prove |
| --- | --- | --- |
| v5.6.6.8 | Exact generic Euler--Green jet identity and the target `H^s(T^4)` class; the old Kronecker chart is non-uniform | A working arbitrary-N Route C or a numerical bridge |
| v5.6.6.13 | Whole-collar margin estimates for the three pinned members | Directed-rounding interval certification or arbitrary members |
| v5.6.6.14 | Symbolic pointwise bound for the lateral elimination map | A bound for the complete free decoder, its Sobolev lift or truncation commutation |
| v5.6.6.15 (`e1fcdaa`) | Static sector partition plus sampled Route B/Route C density agreement within tolerance | Symbolic same-functional identity, stencil bias or quadrature control |
| v5.6.6.12 + v5.6.6.19 (`49dfca7`) | Exact stencil moments and the limited polynomial-continuation reading of radial channels | `p_obs <= 0` does not certify roundoff dominance; no production `B_FD` bound |
| v5.6.6.16 (`65004db`) | Sampled gluing defects, exact lateral Q-frame cancellation, sampled projected-Jacobian spans, and the exact theta-only non-density obstruction | Full `ker D Phi`, constant rank, physical quotient, representative independence or a uniform bridge |
| v5.6.6.17 (`6892511`) | Four published directions at `N=1,2,3`, `Q=5`, `R=10`: Route A AD and precision Route C agree within the fixed tolerance; worst absolute difference `1.94e-9` | Anything beyond the selected finite family, grids and tangents |
| v5.6.6.18 (`c60234b`) | Exact ideal-rational stencil moments and Taylor/Cauchy formula; sampled coarse/fine contrast | Float candidate envelopes are not outward-rounded production bounds; the N=3 `qrr` canary has nonzero production residue against ideal zero |
| v5.6.7 (`bb97849`) | Nested full-T4 Fourier enumeration through real shell transitions, analytic spectral/radial formulas checked through `K=8`, and a sampled pulled-back two-jet contrast; clean checkout `18/18` | No complete decoder, action, JVP, quadrature, uniform margin or bridge claim; arithmetic is float64 and the lexical derivative-path audit is only a canary |

## Exact conditions on the replacement bridge

- Uniform approximation on an entire bounded `H^s` ball cannot converge in the
  same `H^s` norm: for every finite projector there is a normalized omitted
  mode.  This does not refute the pointwise-in-`X` convergence stated in
  v5.6.6.8.  Any uniform-on-balls or uniform-rate strengthening must instead
  lose regularity (`H^s -> H^{s0}`, `4 < s0 < s`), add uniform tail control, or
  work on a compact subset; the final bridge must state this quantifier
  explicitly.
- Because each wavevector enters as cosine and then sine, even-dimensional
  `V_N` is not closed under differentiation.  Any commutation lemma must use
  complete sine/cosine pairs (preferably complete Fourier shells) or evaluate
  derivatives outside `V_N` without claiming `P_N d = d P_N`.
- `K(N) -> infinity` is compatible with radial density, but radial quadrature
  cannot stay fixed: if `Q_rho < K`, a nonzero radial combination vanishes at
  every node while its squared integral is positive.
- The literal action contains exponentials, inverses and square roots, so its
  composed integrands are not band-limited.  No finite T4 grid makes their
  quadrature exactly alias-free; the route needs growing quadrature plus a
  proved remainder bound, not a finite exactness claim.

## Remaining route

The current theta-only bridge is closed as a no-go. The v5.6.7 primitive
foundation now exists, but a replacement must still:

1. evaluate the complete common-first decoder and pullback in analytic jets;
2. obtain local density JVPs by dual/AD propagation without hidden stencils;
3. integrate on a growing genuine T4 x rho quadrature with aliasing and
   nonlinear-remainder control;
4. prove margins and C2/Moser bounds for the complete decoder, then prove
   re-glued truncations converge in an explicitly weaker or tail-controlled
   target norm;
5. resolve the gauge quotient / representative-independence obligation; and
6. discharge the independent v5.6.1 quarantine obligations before any C1/N1
   promotion.

## Working protocol

- One writer per file set; adversarial review is read-only.
- Commits are narrow and local; no push without explicit authorization.
- Sampled agreement, static audits and ideal arithmetic are never promoted to
  a continuum or production theorem.
