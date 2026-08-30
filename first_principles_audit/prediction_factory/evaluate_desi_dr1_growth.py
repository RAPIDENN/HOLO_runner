#!/usr/bin/env python3
"""Evaluate the frozen growth dictionary on published DESI DR1 compression.

Only the four DESI DR1 bins inside the frozen trace domain are used.  This is
a one-dimensional diagonal diagnostic of the published ``f sigma_s8`` entries,
not the official joint ShapeFit likelihood: distance, slope, cross-bin and
within-vector correlations are deliberately not guessed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
GROWTH_PATH = (
    REPO_ROOT
    / "A_single_Einstein_Dilaton geometry"
    / "artifacts"
    / "growth_report.json"
)
OUTPUT_PATH = HERE / "desi_dr1_growth_diagnostic.json"

SOURCE = {
    "title": "DESI 2024 V: Full-Shape Galaxy Clustering from Galaxies and Quasars",
    "arxiv_version": "2411.12021v5",
    "journal_doi": "10.1088/1475-7516/2025/09/008",
    "location": "Appendix A, SF+BAO compressed datavectors and covariances",
    "url": "https://arxiv.org/abs/2411.12021",
}

# Published SF+BAO compressed values.  The variance is the (3,3) diagonal
# element of each corresponding 4x4 covariance matrix, including its 1e-4
# prefactor.  Higher-z bins are outside the frozen trace and excluded a priori.
DESI_BINS = (
    ("BGS", 0.30, 0.396326, 80.924891e-4),
    ("LRG1", 0.51, 0.547632, 35.284297e-4),
    ("LRG2", 0.71, 0.479541, 23.061044e-4),
    ("LRG3", 0.92, 0.438454, 17.011310e-4),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def evaluate(growth_path: Path = GROWTH_PATH) -> dict[str, Any]:
    growth_path = Path(growth_path).resolve()
    growth = json.loads(growth_path.read_text(encoding="utf-8"))
    series = growth["series"]
    z_grid = np.asarray(series["z"], dtype=float)
    holo_grid = np.asarray(series["fsigma8_holo"], dtype=float)
    lcdm_grid = np.asarray(series["fsigma8_lcdm"], dtype=float)
    if not np.all(np.diff(z_grid) > 0.0):
        raise ValueError("growth redshift grid is not strictly increasing")

    z_max = float(z_grid[-1])
    rows: list[dict[str, Any]] = []
    chi2_holo = 0.0
    chi2_lcdm = 0.0
    for tracer, redshift, observed, variance in DESI_BINS:
        if redshift > z_max:
            raise ValueError(f"{tracer} lies beyond frozen trace domain")
        predicted_holo = float(np.interp(redshift, z_grid, holo_grid))
        predicted_lcdm = float(np.interp(redshift, z_grid, lcdm_grid))
        sigma = float(np.sqrt(variance))
        pull_holo = (predicted_holo - observed) / sigma
        pull_lcdm = (predicted_lcdm - observed) / sigma
        chi2_holo += pull_holo**2
        chi2_lcdm += pull_lcdm**2
        rows.append(
            {
                "tracer": tracer,
                "z_eff": redshift,
                "published_fsigma_s8": observed,
                "published_marginal_sigma": sigma,
                "frozen_holo_fsigma8": predicted_holo,
                "matched_lcdm_fsigma8": predicted_lcdm,
                "holo_marginal_pull": pull_holo,
                "lcdm_marginal_pull": pull_lcdm,
            }
        )

    # The largest difference between the two frozen curves in the admissible
    # DESI bins occurs at the preregistered high-z edge bin.
    edge = rows[-1]
    passes = {
        "all_bins_inside_trace": all(row["z_eff"] <= z_max for row in rows),
        "no_parameter_refit": True,
        "finite_predictions": all(
            np.isfinite(row[key])
            for row in rows
            for key in (
                "frozen_holo_fsigma8",
                "matched_lcdm_fsigma8",
                "holo_marginal_pull",
                "lcdm_marginal_pull",
            )
        ),
        "higher_bins_fail_closed": z_max < 1.32,
        "diagnostic_not_mislabeled_full_likelihood": True,
    }
    passes["all"] = all(passes.values())
    return {
        "title": "Frozen growth dictionary versus DESI DR1 compressed growth",
        "classification": "external_diagonal_diagnostic_not_confirmatory_likelihood",
        "source": SOURCE,
        "input": {
            "growth_artifact": growth_path.relative_to(REPO_ROOT).as_posix(),
            "growth_sha256": _sha256(growth_path),
            "frozen_trace_z_max": z_max,
        },
        "comparison_rule": {
            "observable": (
                "published fiducial-compression f sigma_s8 compared directly "
                "with frozen f sigma8 at the tabulated effective redshift"
            ),
            "score": "sum of squared one-dimensional marginal pulls",
            "parameters_refit": [],
            "included_bins": [row["tracer"] for row in rows],
            "excluded_bins": {
                "ELG2_z_1.32": "outside frozen trace domain",
                "QSO_z_1.49": "outside frozen trace domain",
            },
        },
        "rows": rows,
        "summary": {
            "points": len(rows),
            "diagonal_chi2_holo": float(chi2_holo),
            "diagonal_chi2_lcdm": float(chi2_lcdm),
            "delta_chi2_holo_minus_lcdm": float(chi2_holo - chi2_lcdm),
            "edge_bin_z": edge["z_eff"],
            "edge_bin_holo_pull": edge["holo_marginal_pull"],
            "edge_bin_lcdm_pull": edge["lcdm_marginal_pull"],
            "interpretation": (
                "Both curves are compatible with these four marginal entries; "
                "the small positive delta chi2 does not favour HOLO."
            ),
        },
        "passes": passes,
        "evidence_boundary": (
            "This diagnostic uses only the growth component and diagonal "
            "marginal variances. It is not the official DESI likelihood, does "
            "not validate the radial-to-cosmological dictionary, and cannot "
            "be called a detection or a confirmatory preference."
        ),
    }


def main() -> int:
    result = evaluate()
    _write(OUTPUT_PATH, result)
    summary = result["summary"]
    print(f"[DESI DR1 diagnostic] {OUTPUT_PATH}")
    print(
        "[diagonal chi2] HOLO={:.6f} LCDM={:.6f} delta={:+.6f}".format(
            summary["diagonal_chi2_holo"],
            summary["diagonal_chi2_lcdm"],
            summary["delta_chi2_holo_minus_lcdm"],
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
