# Rebuilt paper source

This directory is the editable source for the corrected paper.  It preserves
the seven existing figure assets while integrating the geometry-preserving
effective action, the blind compact-interval matter benchmark, the
prediction-factory diagnostics, and the evidence labels from the three-stage
audit.

Build and validate locally with the user-installed Tectonic engine:

```bash
python3 build_revision.py
```

The build regenerates the bulk, interface, FEM, independent ODE-shooting,
boundary-branch, material, electromagnetic-kernel, DESI, and master-registry
certificates before compiling.  It then runs `compare_original_revision.py`
and `validate_revision.py`.  The comparison checks the frozen original PDF
against the revision; the validator checks required numerical claims, all 11
figure captions, references, page count, derived certificates, and
observational blinding before the primary PDF is replaced.

The document uses the standard LaTeX `article` class and carries no journal,
volume, preprint, or typesetting-provider banner.

The prior PDF is retained as `A_single_Einstein-Dilaton_geometry_v1_frozen.pdf`
when the validated revision is promoted.
