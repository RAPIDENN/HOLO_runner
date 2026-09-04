# C1/N1 pointwise bridge — status and roadmap (2026-09-04)

Branch `checkpoint/c1-n1-restricted-v5658-20260903`, frozen evidence chain `ea014fd`.
Local-only commits `fc9d3e8..` (Claude / Fable 5.1) plus `fe80ef5` (Codex); nothing
pushed. Every gate below is a new `derive_*/test_*/artifacts/*.json` triple; no
upstream file, paper, registry or README was edited.

## Why C1/N1 was stuck

The v5.6.6.7 obligation asked for "the exact second-order Euler--Green identity and
continuity bounds on the declared restricted C2 spectral class" plus a uniformly
bounded retraction of `DG_N`. In the v5.6.4 coefficient chart that retraction cannot
exist: the declared Kronecker collocation has condition number 8 at N=3 and 7.7e11 by
N=159 (v5.6.6.8, refuted-and-confirmed with mpmath). The way through is the
**pointwise (common-first) formulation**, where the gluing is the graph of an explicit
N-free map Phi (v5.6.6.9). All later gates live there.

## Gates and what each one establishes

| Gate                          | Key flipped (True)                                                                                                                                                                                                                 | Machine-checked                                                                                                                                                                    | Prose / not proven                                                                 |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| v5.6.6.8                      | `generic_second_order_Euler_Green_identity_symbolic_pass`, `outer_radial_Green_form_vanishes_exactly_pass`, `route_C_literal_current_is_Euler_operator_representative_pass`, `bundle_members_glued_pointwise_off_collocation_pass` | jet-space identity dL = E.dq + div H, interface functional (<=2 tangential jets), C2 radial junction, Kronecker instability measured, pointwise gluing 4e-16                       | real-analyticity of the literal density on the margin set; Sobolev continuity (ii) |
| v5.6.6.9                      | `common_first_gluing_is_explicit_graph_pass`, `pointwise_jacobian_explicit_bound_sampled_pass`                                                                                                                                     | all gluing rows vanish symbolically (Cayley chart) and numerically; block-wise Jacobian bound sampled on ball/spikes/corners; static AST audit of Kronecker-inverse users          | Sobolev lift; margins as hypothesis                                                |
| v5.6.6.10                     | `route_c_tangential_ladders_saturated_pass`, `route_c_radial_ladders_geometric_contraction_pass`                                                                                                                                   | tangential ladders at the FD5 stencil floor (1e-10), radial per-component contraction 0.11 per two GL nodes, own-scale tail 5.9e-9; bridge component ledger with five genuine gaps | strip width / rate law (one ratio only)                                            |
| v5.6.6.11 (+ Codex `fe80ef5`) | `pinned_members_margins_on_dense_collar_pass` (everywhere key kept False)                                                                                                                                                          | all four v5.6.4 margins on a 256x129 grid; same-objects theorem with the stencil bias `B_FD` explicit                                                                              | between-node bound (see v5.6.6.13), `B_FD` not bounded                             |
| v5.6.6.13                     | `pinned_members_margins_everywhere_certified_pass`                                                                                                                                                                                 | Weyl + Lipschitz with exact harmonics and Bernstein-bounded profiles: min abs eig >= 1.036, Omega >= 0.9956, khronon <= -0.608, SO(3) clearance >= 2.852 everywhere                | rounding padded 1e-9, not interval-certified                                       |
| v5.6.6.14                     | `pointwise_retraction_jacobian_bound_proved_symbolic_pass`                                                                                                                                                                         | symbolic entry-by-entry bound B_proved(M) (degree 8 in M, denominators asserted as powers of 1+abs(k)^2), dominates the v5.6.6.9 sample design                                     | Sobolev lift (Moser)                                                               |
| v5.6.6.15 | `route_c_sector_list_is_literal_action_term_list_pass`, `route_c_bulk_and_ghy_densities_equal_pinned_literal_implementation_pointwise_pass`, `route_c_interface_densities_equal_pinned_literal_implementation_pointwise_pass`, `route_c_closed_form_coefficients_match_literal_formula_strings_pass` | all twenty sector densities of Route C (pulled-back formulation) agree pointwise with the pinned Route B implementation of the literal v5.2 action (ambient formulation) on exact random 2-jets inside the margins, both collars, worst 3.8e-15 relative; closed-form pieces checked against the literal strings | sampled, not symbolic; exact jets, so nothing about `B_FD` or quadrature |
| v5.6.6.16 | `Q_frame_coordinates_are_exact_kernel_of_the_decoder_symbolic_pass`, `Q_frame_coordinates_are_exact_kernel_of_pinned_and_route_c_decoders_numeric_pass`, `route_c_trace_decoder_matches_pinned_decoder_pass`, `free_data_family_jacobian_kernel_is_explicit_gauge_generators_pass`, `interface_densities_independent_of_Q_frame_pass` | the finite family is stated in free data only, `F_N = Phi(U_N)`; the 3N `Q_frame` coordinates are an exact kernel of the decoder (symbolic: `R = S R0` cancels `S`), the 6N `r_E0` coordinates are physical for `N >= 2`, and the whole kernel of `DPhi` on the trace coordinates at the pinned members is spanned by explicit generators (`Q_frame`, constant modes of `T`, `Y_plus`, `Y_minus`; at `N = 1` also the constant rotation about `varphi_E0`): dimensions 7 / 9 / 12 with gaps `>= 5e6` | numeric at the three members only (no constant-rank theorem); nothing on `N -> infinity` |

Still False everywhere, by design: `uniform_N_to_infinity_bridge_pass`,
`uniform_stability_pass` (v5.6.4 key), `restricted_family_exact_action_identity_pass`
(v5.6.4 key), `C1_ACTION_pass`, `N1_ACTION_pass`, `C1_N1_promotion_authorized`,
`B4_pass`, `B5_pass`.

## Ledger of the bridge (from v5.6.6.10, updated)

1. Same objects: closed for the three pinned members **up to `B_FD`** (v5.6.6.11); the
   same-functional hypothesis of that theorem is discharged at the density level by v5.6.6.15
   (sampled pointwise identity with the pinned literal-action implementation, both collars).
2. Class drift: the pinned members are continuum-class points (v5.6.6.11/13); the v5.6.4
   nodal family is not the theorem class and is not used any more.
3. Margins on the whole collar: **closed** (v5.6.6.13).
4. Proven Jacobian bound: **closed** (v5.6.6.14); Sobolev lift stays an analytic argument.
5. Finite `DG_N` on `V_N` and the gauge quotient `H_N`: **retired by the free-data formulation**
   (v5.6.6.16): the family is `Phi(U_N)`, no finite gluing map or quotient enters the identity, and
   the kernel of `DPhi` is listed with explicit generators at the pinned members. The v5.6.4 keys
   `uniform_stability_pass` and `DG_N` stay False: retired, not discharged.

## What remains before any key flips

- **`B_FD`** (Codex lease, new files v5.6.6.12): bound the Q-independent bias of the FD5
  free-parameter stencil (`FREE_JVP_STEP = 2e-3`) and the 7-point coordinate stencils
  (`h = 5e-3`) by Richardson in both steps or complex-step / AD; optionally a Qrho = 18
  ladder to get two radial ratios instead of one.
- **Gap 5**: closed in the free-data formulation by v5.6.6.16 (family `Phi(U_N)`, 9N rotation
  coordinates treated explicitly: 3N exact kernel, 6N physical for `N >= 2`; full kernel of
  `DPhi` with generators at the three members). Still open inside it: constant rank away from
  the pinned members, and the continuum common-frame redundancy for the `N -> infinity` count.
- **N -> infinity for arbitrary class members**: density of degree-<=1 free data is
  false; use Fourier truncation of arbitrary free data plus re-gluing (part iii) and the
  continuity bound (ii) with the Moser constant made explicit.
- **Same functional**: closed by v5.6.6.15 at the density level (sampled pointwise identity
  of the twenty Route C sector densities with the pinned Route B implementation of the literal
  action, plus literal-text checks of the closed-form pieces). Still open inside it: a symbolic
  identity (not attempted), and the tie of the curvature/kinetic/foliation terms to the literal
  text rests on the v5.6.4/v5.6.5 pins of Route B.
- **Independent audit** (v5.6.1 quarantine wording) before `uniform_N_to_infinity_bridge_pass`.
- **C1/N1 beyond the bridge**: v5.6.1 quarantine obligations (full bulk diffeomorphism
  Ward identity, fully coupled moving-embedding cross terms, off-shell continuous extension).

## Working protocol (agreed in `~/.agent-bridge`, 2026-09-04)

- One writer per file set; Codex owns v5.6.6.12 (`B_FD`), Claude owns v5.6.6.13/14.
- Every gate gets an adversarial read-only refutation by the other agent before its key
  is trusted; every refutation so far found something real and is recorded in the commit
  messages.
- No push, no edits to paper / registry / README / foreign dirty files, no flip of any
  fail-closed key without the audit above.
