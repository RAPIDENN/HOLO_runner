# ED Trace Reproduction Bridge

This folder records the minimal public reproducibility metadata for the frozen
Einstein-Dilaton trace used by the `HOLO_runner` verification bundle.

It does not claim to prove the physical theory. It verifies the narrower
computational statement:

```text
canonical initial conditions + external solver checkout -> exact frozen ED trace hash
```

## Contents

| File | Purpose |
| --- | --- |
| [`canonical_ic.json`](./canonical_ic.json) | Initial conditions required to reproduce the frozen trace. |
| [`EXPECTED_SHA256`](./EXPECTED_SHA256) | Expected hash for `data/internal/holo_physics_trace_ed_industrial.json`. |
| [`reproduce_trace.sh`](./reproduce_trace.sh) | Runs the referenced solver in a temporary worktree and checks the hash. |
| [`README.md`](./README.md) | This guide and interpretation notes. |

## Public Scope

This public repository does not vendor the external solver source or name any
local checkout. It records only the portable inputs and expected output hash:

- canonical initial conditions: [`canonical_ic.json`](./canonical_ic.json)
- expected trace hash: [`EXPECTED_SHA256`](./EXPECTED_SHA256)
- optional runner path expected inside an external checkout:
  `kernel/rust/holo_kerneld`
- expected output trace path inside that checkout:
  `data/internal/holo_physics_trace_ed_industrial.json`

The same trace hash is used by the artifacts in:

```text
A_single_Einstein_Dilaton geometry/artifacts/
instrument_closure/2026-01-04/
```

## Canonical Initial Conditions

The trace is not reproduced by the runner defaults. It requires the canonical
initial conditions in:

```text
ed_trace_repro/canonical_ic.json
```

These values are the first state of the frozen ED trace.

## Expected Hash

The reproduced trace must have this SHA256:

```text
e1c4b9d8495a563be31c36ceeeea7575b1d46afae74b45394edb77a8ffb06725
```

## Reproduce

From the `HOLO_runner` root, this public self-check works in any normal clone:

```bash
./ed_trace_repro/reproduce_trace.sh
```

Expected public self-check line:

```text
[OK] Public reproduction metadata is self-consistent.
```

To run an external solver checkout, provide it explicitly:

```bash
ED_SOLVER_REPO=/path/to/solver-checkout ./ed_trace_repro/reproduce_trace.sh
```

Optionally pin a revision from that checkout:

```bash
ED_SOLVER_REPO=/path/to/solver-checkout ED_SOLVER_REV=<commit-or-tag> ./ed_trace_repro/reproduce_trace.sh
```

When `ED_SOLVER_REPO` is set, the script creates a temporary git worktree, runs
the solver there, compares the output hash, and removes the temporary worktree.
It does not modify the external checkout or this verification repo.

Expected external solver success line:

```text
[OK] ED trace reproduced exactly.
```

## Interpretation

Passing the public self-check means the portable reproduction metadata in this
folder is internally consistent. Passing the optional external solver check
means the frozen ED trace is computationally reproduced from that external
checkout and the canonical initial conditions.

It does not by itself establish that the model is physically correct. That
requires independent review of the equations, assumptions, initial-condition
choice, data comparisons, and predictive tests.
