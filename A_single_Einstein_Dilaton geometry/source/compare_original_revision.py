#!/usr/bin/env python3
"""Machine-check the preserved result set against the frozen original PDF."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path


SOURCE = Path(__file__).resolve().parent
PAPER_ROOT = SOURCE.parent
ORIGINAL = PAPER_ROOT / "A_single_Einstein-Dilaton_geometry_v1_frozen.pdf"
REVISION = PAPER_ROOT / "build" / "A_single_Einstein-Dilaton_geometry.pdf"
OUTPUT = PAPER_ROOT / "build" / "original_revision_comparison.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract(path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    text = unicodedata.normalize("NFKC", result.stdout)
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text)


def has(text: str, *patterns: str) -> bool:
    return all(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def main() -> int:
    original = extract(ORIGINAL)
    revision = extract(REVISION)
    metrics = [
        ("scalar_ratio", (r"1\.5455",), (r"1\.5455",)),
        ("ir_scale_proxy", (r"0\.203", r"451", r"1\.60"),
         (r"0\.203", r"451", r"1\.60")),
        ("sparc_ranking_medians", (r"1\.86", r"1\.93"),
         (r"1\.862", r"1\.928")),
        ("sparc_uncertainty_medians", (r"831", r"906"), (r"831", r"906")),
        ("sparc_win_counts", (r"150/175", r"149/175"),
         (r"150/175", r"149/175")),
        ("sparc_global_parameters",
         (r"0\.13983", r"2\.21605", r"1\.20433", r"0\.23356", r"0\.60488"),
         (r"0\.13983", r"2\.21605", r"1\.20433", r"0\.23356", r"0\.60488")),
        ("planck_reference", (r"0\.315", r"67\.4", r"0\.811"),
         (r"0\.315", r"67\.4", r"0\.811")),
        ("boss_covariance", (r"2\.266", r"2\.443", r"0\.177"),
         (r"2\.266", r"2\.443", r"0\.177")),
        ("high_redshift_shift", (r"-12",), (r"-12",)),
    ]
    checks = []
    for name, old_patterns, new_patterns in metrics:
        old_ok = has(original, *old_patterns)
        new_ok = has(revision, *new_patterns)
        checks.append({
            "name": name,
            "original_present": old_ok,
            "revision_present": new_ok,
            "passed": old_ok and new_ok,
        })

    interpretation_checks = {
        "newtonian_scope_explicit": has(revision, r"baryonic Newtonian baseline"),
        "not_state_of_the_art_claim": has(revision, r"not benchmarked"),
        "sparc_in_sample_label": has(revision, r"in-sample calibration"),
        "spectrum_diagnostic_label": has(revision, r"operator diagnostic"),
        "boss_dictionary_label": has(revision, r"dictionary model"),
        "clock_null_label": has(revision, r"null/poor-fit"),
        "no_mnras_banner": not has(revision, r"Compiled using MNRAS"),
        "no_preprint_banner": not has(revision, r"Preprint 29 August"),
        "impersonal_opening": not has(revision, r"We present"),
    }
    passed = all(item["passed"] for item in checks) and all(
        interpretation_checks.values()
    )
    payload = {
        "schema": "holo-original-revision-comparison.v1",
        "passed": passed,
        "original": {"path": str(ORIGINAL), "sha256": sha256(ORIGINAL)},
        "revision": {"path": str(REVISION), "sha256": sha256(REVISION)},
        "preserved_metrics": checks,
        "interpretation_checks": interpretation_checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"original_revision_comparison_passed={passed}")
    print(OUTPUT)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
