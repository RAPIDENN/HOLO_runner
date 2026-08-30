# Protocol deviations

## Stage-1 zero comparison

The first execution stopped before stage 2.  SymPy had reduced every symbolic
residual to the string `"0"`, but the audit compared those serialized strings
to the integer `0`, so all six zero checks were falsely marked `false`.

The comparison was changed from `value == 0` to `value == "0"`.  No equation,
threshold, frozen input, or physical parameter changed.  Stage 1 was resealed
and only then was stage 2 allowed to open the candidate artifacts.

## Numerical interval stated in code

The prose preregistration referred to the "preregistered interval" without
printing its numerical values.  The stage-3 implementation already fixed these
before its first successful run as `L=1`, `u in [0,2]`, `phi(0)=1e-3`, and
`A(0)=0`, sampled at 401 points.  This file records that omission; the interval
was not changed after observing a result.
