# Prospective material prediction factory

This directory freezes the dimensionless signal that follows from the six
positive modes of the minimal compact-interval probe completion.  It does not
use SPARC, BOSS, NIST, a historical fitted coupling, or any detector result.

The generated curve uses `x = r/ell` and reports:

- scalar force divided by Newtonian force;
- radial scalar-force gradient divided by the Newtonian radial gradient;
- decay ratios between preregistered dimensionless distances;
- the universal normalized near-resonance transfer
  `H_tilde = 1/(1+i*delta)`.

Generate and then verify the frozen artifact:

```bash
python3 first_principles_audit/prediction_factory/material_prediction_factory.py
python3 first_principles_audit/prediction_factory/material_prediction_factory.py --check
sha256sum -c first_principles_audit/prediction_factory/material_predictions.sha256
python3 -m unittest discover \
  -s first_principles_audit/prediction_factory \
  -p 'material_*_test.py' -v
```

`material_predictions.json` contains a canonical payload hash and provenance
hashes for both its input completion and generator.  The detached
`material_predictions.sha256` hashes the full rendered JSON.  These are content
integrity hashes, not a private-key identity signature.

The companion `artifacts/breathing_response.json` promotes this static
fingerprint to the linear four-dimensional retarded response.  Generate and
test it with:

```bash
python3 first_principles_audit/prediction_factory/derive_breathing_response.py
python3 -m unittest \
  first_principles_audit.prediction_factory.test_breathing_response -v
```

## Evidence boundary

The artifact fixes only shape, relative strength, and normalized transfer.  A
dimensional prediction still requires an independently frozen `ell`, source
density and motion, and detector elasticity, damping, supports, modal overlap,
and readout calibration.  It supplies no ambient scalar amplitude and makes no
detection claim.  The massless Neumann zero mode is excluded from this factory;
changing the boundary action requires regenerating the mode table rather than
adding an after-the-fact screening factor.
