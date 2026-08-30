# Reproducibility — Instrument Closure (2026-01-04)

**Scientific specification (paper v3):** `A_single_Einstein_Dilaton geometry/A_single_Einstein-Dilaton_geometry.pdf`

This folder is a **sanitized, auditable historical bundle** (no absolute paths, no PI). It records the formerly claimed circuit:

Wilson loop → σ_eff → frozen ED geometry → SPARC → fσ₈ → 5D Ricci clock → UV-screened laboratory projection.

The frozen hashes remain useful, but the current audit does not regard this as
a physical closure.  The actual scale direction is `ED endpoint + external
alpha' + external c -> sigma_proxy -> m0`; the Ricci series used a mislabeled
radial derivative; and the UV channel is a dictionary.  None of these
corrections alters the frozen artefacts.

## Roles (public vs private)

- **HK-core (public) → gauge-kernel audit input**
  - Produces an IR-dominant plaquette/correlator decision run (`hkcore_refine_beta2.0_seed777.json`). It does not measure rectangular Wilson loops, a static potential, or string tension.

- **Einstein–Dilaton (ED) kernel (private) → frozen geometry & readouts**
  - The ED kernel is **private** and not shipped here.
  - This bundle includes the **frozen, versioned readouts** derived from the private ED kernel execution, including the endpoint scale proxy and downstream readouts (SPARC, growth/BOSS, legacy Ricci clock, UV projection).

- **HOLO_runner (public) → audit & manifest**
  - Provides the public audit surface (hashes + verification scripts).
  - The canonical manifest for this bundle is `instrument_closure_manifest.json`.

## One-command audit (public)

From the `HOLO_runner` repository root:

```bash
python3 instrument_closure/2026-01-04/run_instrument_closure.py \
  --sparc-dir /path/to/SPARC/sparc_175 \
  --run-hkcore --hkcore-url http://127.0.0.1:8080/mill/refine --hkcore-token devtoken
```

What it does:
- Verifies every JSON in this folder against the SHA-256 list in `instrument_closure_manifest.json`.
- Runs the HOLO_runner verification suite (SPARC, cosmology summary, Ricci summary, Bullet Cluster artefact checks).
- Optionally re-runs the HK-core `/mill/refine` call using the exact `config` stored in `hkcore_refine_beta2.0_seed777.json` and prints a compact verdict summary.

## Private regeneration (ED kernel)

Regenerating the **frozen ED geometry** and the readouts in this bundle requires the private **Einstein–Dilaton (ED) kernel**. This repository intentionally does not ship that kernel; the public guarantee is the manifest-hash audit of the frozen products.
