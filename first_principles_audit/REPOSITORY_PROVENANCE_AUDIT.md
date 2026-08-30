# Cross-repository provenance audit

Audit date: 2026-08-29.  This map prevents a reproducible artifact, a fitted
readout, and an independently derived physical coupling from being conflated.

| Repository | Audited revision | Actual role | What it does not establish |
| --- | --- | --- | --- |
| `ed-trace-solver` | `d21a64355d0ce67f9184e956abcd9822f58a5e6e` | Standalone Rust generator of the exact frozen trace SHA-256 `e1c4b9d8...b06725`. | It has no fluctuation problem, boundary action, matter action, or modal normalization. Its prescribed density enters only `A''`; the vacuum Hamiltonian residual reaches about `1.81`. |
| `HOLO_TRANSDUCTOR_instrument` | `7df7f3c419b9db7d8515978203b01a6450c73811` | Original integrated location of the same frozen trace and downstream experimental scripts. | Exact trace reproduction is not a proof that the nominal canonical polynomial action closes. |
| `HOLO_TRANSDUCTOR_V2` | `c8742758700658253d4fac9b04f4d8469dfd4e90` | Branch snapshot containing the same canonical trace and many of the same coupling scripts. | It is not an independent replication: the canonical trace and the inspected Standard-Model coupling script are byte-identical to `instrument`. |
| `HOLO_TRANSDUCTOR` | `9edd945e699e4f8868f244092430a4ac40364d26` | Historical design, calibration, screening, and particle-coupling experiments. | The DOF1 prediction reads `v_obs` while constructing the curve and scans its coupling on the same SPARC sample. Its numerical coupling and imposed UV suppression are not blind predictions. |
| `HK-core` | `d0f664f631b32d3d3ca0c94dff5292e21e6905a4` | Pure-gauge lattice engine. Its current code contains a 4D SU(3) plaquette operator that could eventually support an independent scalar-glueball calculation. | It has no dilaton or ED interface. The saved 4D SU(3) result is explicitly inconclusive, while the closure bundle uses a 3D SU(2) artifact; neither fixes QCD string tension, `alpha'`, nor a dilaton coupling. |
| `HOLO_QG` | empty remote repository | Reserved name only. | No code or evidence. |
| `RAPIDENN` | public profile repository | Profile and project index. | No ED or coupling implementation. |
| `Claw` | operational agent fork | Tooling/agent operations. | Not part of the physics derivation. |
| `HOLO_runner` | public HEAD `a933551b1133a0c39e359eac7029579f3f7179e2`, plus this local audit | Public verification pack, corrected action audit, and paper build. | The geometry-preserving action is an inverse effective completion; by itself it does not make the frozen geometry an upstream prediction. |

## Reproduction result

The public bridge now accepts both the standalone solver layout and the legacy
monorepo path.  Running it against the pinned private solver revision and the
canonical initial conditions reproduced all 1999 samples and the exact expected
trace hash.  The same execution reported `Max |H| constraint: 1.81e0`.

Both facts must be retained: the array has exact computational provenance, and
the nominal canonical/polynomial equations do not form a closed physical model
for that array.

## Reuse decision

- Reuse the frozen arrays and hash as the object being explained.
- Reuse the corrected positive `K(phi), V(phi)` only as an explicitly labelled
  inverse effective completion.
- Reuse the general idea of conformal matter coupling only after deriving it
  from a declared matter metric and canonical mode normalization.
- Do not reuse the old values `alpha_b=0.3`, `phi_falloff=30 kpc`, pointwise
  `v_obs` gating, `S_UV=10^-30`, the 3D SU(2) closure artifact, or the old
  polynomial `V''=3` fluctuation spectrum as first-principles inputs.

This audit changes the forward task from “copy the existing coupling” to
“define one physical completion, freeze it without observations, and derive
its consequences.”
