# C1: regulated derivative-condensate gate

This is a theory-only, fail-closed reproduction of Sec. 6 of Berezhiani and
Khoury, [*Theory of dark matter superfluidity*](https://doi.org/10.1103/PhysRevD.92.103510).
It reads no galaxy catalogue and does not fit a coefficient.

The calculation deliberately separates two conclusions:

1. The inverse-susceptibility radial energy is a valid counterexample to the
   earlier no-go for a canonical positive sextic potential. Its non-zero
   stationary branch is radially stable and gives the three-halves power.
2. It is not a target-blind microscopic completion of the current five-dimensional
   HOLO action. A finite regulator creates a fold, the regulator-free local
   reduction loses its radial inverse-correlation scale at the origin, spatial
   Weyl homogeneity does
   not select the Wilson function, the negative-`X` zero-temperature phonon has
   the wrong kinetic sign, and the physical `q^2 Y` vertex remains unproved.

## Reproduce

From the repository root:

```bash
python3 -m first_principles_audit.prediction_factory.derive_c1_bk_derivative_gate
python3 -m unittest first_principles_audit.prediction_factory.test_c1_bk_derivative_gate
```

The first command writes only the new certificate
`first_principles_audit/prediction_factory/artifacts/c1_bk_derivative_gate.json`.
It exits successfully when the mathematical reproduction is internally
consistent; the independent physical verdict is stored as `KILL_C1`.

## Binary stop rule

C1 is promoted only if every `binary_gates` entry passes in the same declared
action. A failed gate cannot be repaired by adding a regulator, finite-temperature
term, Wilson coefficient or boundary operator after inspecting the result. Such
an addition is a new candidate and must start a new recorded campaign.
