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

## Remaining route

The current theta-only bridge is closed as a no-go. A replacement must:

1. implement the declared nested real Fourier basis on all four torus axes for
   arbitrary `N`, with an explicit radial schedule `K(N)`;
2. compute tangential and radial first/second derivatives analytically, not by
   hidden stencils;
3. evaluate the complete common-first decoder and pullback in those exact jets;
4. obtain action JVPs by dual/AD propagation and integrate on a genuine T4
   quadrature with aliasing control;
5. prove margins and a uniform C1/Sobolev bound for the complete decoder, then
   prove re-glued Fourier truncations converge in the target norm; and
6. discharge the independent v5.6.1 quarantine obligations before any C1/N1
   promotion.

The first reusable foundation is being built as one source/test pair for
full-T4 spectral and radial primitives; it intentionally has no action,
quadrature, bridge or promotion claim.

## Working protocol

- One writer per file set; adversarial review is read-only.
- Commits are narrow and local; no push without explicit authorization.
- Sampled agreement, static audits and ideal arithmetic are never promoted to
  a continuum or production theorem.
