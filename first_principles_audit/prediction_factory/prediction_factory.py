#!/usr/bin/env python3
"""Build a fail-closed observational prediction manifest for HOLO_runner.

The factory does not fit any model.  It inventories frozen local artefacts,
recomputes only audit-level summaries, freezes deterministic holdout rules, and
marks every comparison that has already seen its target data as non-confirmatory.
Only Python's standard library is required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = "prediction-factory-manifest-v1"
PROTOCOL_VERSION = "holo-observational-protocol-v1"
FREEZE_DATE_UTC = "2026-08-29"
SPARC_SPLIT_ID = "sparc-name-sha256-70-15-15-v1"
SPARC_SPLIT_SALT = "HOLO_runner|prediction_factory|sparc|v1|2026-08-29"
CLOCK_SPLIT_ID = "clock-session-sha256-50-25-25-v1"
CLOCK_SPLIT_SALT = "HOLO_runner|prediction_factory|clock-session|v1|2026-08-29"

SPARC_FORWARD = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/sparc_forward_eval.json"
)
BOSS_DR12 = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/growth_validation_boss_dr12.json"
)
GROWTH_REPORT = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/growth_report.json"
)
DESI_RESIDUAL = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/desi_residual.json"
)
DESI_OPERATOR = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/response_operator_R_desi_nontoy.json"
)
DESI_RECONSTRUCTION = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/reconstructed_mode_delta_G_desi_nontoy.json"
)
NIST_UV = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/nist_comparison_uv.json"
)
NIST_NAIVE = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/nist_comparison_naive.json"
)
NIST_TIME_DICTIONARY = Path(
    "A_single_Einstein_Dilaton geometry/artifacts/tau_from_dictionary.json"
)
CLOSURE_MANIFEST = Path(
    "instrument_closure/2026-01-04/instrument_closure_manifest.json"
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def document_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact_record(repo_root: Path, relative_path: Path, role: str) -> dict[str, Any]:
    path = repo_root / relative_path
    record: dict[str, Any] = {
        "path": relative_path.as_posix(),
        "role": role,
        "exists": path.is_file(),
    }
    if path.is_file():
        record["bytes"] = path.stat().st_size
        record["sha256"] = file_sha256(path)
    return record


def _solve_linear(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]:
    """Solve a small dense linear system with pivoted Gauss-Jordan elimination."""

    n = len(vector)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square and match vector length")
    augmented = [
        [float(value) for value in row] + [float(vector[index])]
        for index, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(augmented[row][column]))
        if math.isclose(augmented[pivot][column], 0.0, abs_tol=1e-18):
            raise ValueError("singular covariance matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * reference
                for value, reference in zip(augmented[row], augmented[column])
            ]
    return [augmented[row][-1] for row in range(n)]


def generalized_chi2(
    observed: Sequence[float],
    predicted: Sequence[float],
    covariance: Sequence[Sequence[float]],
) -> float:
    if len(observed) != len(predicted):
        raise ValueError("observed and predicted vectors must have equal length")
    residual = [float(pred) - float(obs) for obs, pred in zip(observed, predicted)]
    weighted = _solve_linear(covariance, residual)
    return sum(left * right for left, right in zip(residual, weighted))


def _sparc_summary(sparc: dict[str, Any]) -> dict[str, Any]:
    rows = sparc["results"]
    return {
        "galaxies": len(rows),
        "median_rank_loss_ed": statistics.median(row["chi2_rank_ed"] for row in rows),
        "median_rank_loss_newton": statistics.median(
            row["chi2_rank_newton"] for row in rows
        ),
        "wins_rank_ed_over_newton": sum(row["ed_beats_newton"] for row in rows),
        "median_uncertainty_chi2_ed": statistics.median(
            row["chi2_sigma_ed"] for row in rows
        ),
        "median_uncertainty_chi2_newton": statistics.median(
            row["chi2_sigma_newton"] for row in rows
        ),
        "wins_uncertainty_ed_over_newton": sum(
            row["chi2_sigma_ed"] < row["chi2_sigma_newton"] for row in rows
        ),
        "interpretation": "descriptive reproduction of an all-data fit; never a holdout score",
    }


def _boss_summary(boss: dict[str, Any]) -> dict[str, Any]:
    dataset = boss["dataset"]
    observed = dataset["fsigma8_obs"]
    covariance = dataset["cov_fsigma8"]
    holo = boss["model_predictions"]["holo"]["fsigma8"]
    lcdm = boss["model_predictions"]["lcdm"]["fsigma8"]
    chi2_holo = generalized_chi2(observed, holo, covariance)
    chi2_lcdm = generalized_chi2(observed, lcdm, covariance)
    return {
        "points": len(observed),
        "chi2_holo_recomputed": chi2_holo,
        "chi2_lcdm_recomputed": chi2_lcdm,
        "delta_chi2_holo_minus_lcdm": chi2_holo - chi2_lcdm,
        "interpretation": "historical external comparison already inspected; no preference and not a new holdout",
    }


def _nist_summary(nist: dict[str, Any]) -> dict[str, Any]:
    metrics = nist["metrics"]
    redaction = nist.get("redaction", {})
    series = nist.get("series", {})
    removed = redaction.get("removed_series_fields", [])
    return {
        "samples_reported": metrics["n"],
        "pearson_r_reported": metrics["pearson_r"],
        "chi2_over_n_reported": metrics["chi2_over_n"],
        "local_series_fields": sorted(series),
        "observed_series_removed": "y_obs" in removed,
        "residual_series_removed": "resid" in removed,
        "raw_likelihood_recomputable_locally": False,
        "interpretation": "historical null/poor-fit summary; the local bundle redacts the observations",
    }


def _external_nist_declaration(closure: dict[str, Any]) -> dict[str, Any] | None:
    for item in closure.get("external_channels", []):
        if item.get("name") == "LAB_NIST_inputs":
            return item
    return None


def build_inventory(repo_root: Path) -> dict[str, Any]:
    sparc = read_json(repo_root / SPARC_FORWARD)
    boss = read_json(repo_root / BOSS_DR12)
    desi = read_json(repo_root / DESI_RESIDUAL)
    nist = read_json(repo_root / NIST_UV)
    closure = read_json(repo_root / CLOSURE_MANIFEST)
    nist_external = _external_nist_declaration(closure)

    sparc_artifacts = [
        artifact_record(repo_root, SPARC_FORWARD, "175-galaxy derived per-galaxy score table"),
        artifact_record(
            repo_root,
            Path("data/internal/sparc_p5_current.json"),
            "legacy all-sample derived summary",
        ),
        artifact_record(
            repo_root,
            Path("data/internal/sparc_p5_preprint_frozen.json"),
            "legacy frozen all-sample derived summary",
        ),
        artifact_record(
            repo_root,
            Path("instrument_closure/2026-01-04/ed_fixed_ic_sparc_eval.json"),
            "separate frozen all-sample score table",
        ),
    ]
    boss_artifacts = [
        artifact_record(repo_root, BOSS_DR12, "three-point observation, covariance, predictions, and scores"),
        artifact_record(repo_root, GROWTH_REPORT, "dictionary-derived growth curves"),
        artifact_record(
            repo_root,
            Path("instrument_closure/2026-01-04/growth_validation_boss_dr12.json"),
            "frozen duplicate comparison",
        ),
    ]
    desi_artifacts = [
        artifact_record(repo_root, DESI_RESIDUAL, "constructed residual vector, not an official DESI measurement table"),
        artifact_record(repo_root, DESI_OPERATOR, "finite-difference response operator"),
        artifact_record(repo_root, DESI_RECONSTRUCTION, "bounded single-arm inverse reconstruction"),
    ]
    nist_artifacts = [
        artifact_record(repo_root, NIST_UV, "redacted UV-projected comparison summary"),
        artifact_record(repo_root, NIST_NAIVE, "redacted naive comparison summary"),
        artifact_record(repo_root, NIST_TIME_DICTIONARY, "non-unique candidate time dictionaries"),
        artifact_record(repo_root, CLOSURE_MANIFEST, "external NIST file names and declared hashes"),
    ]

    return {
        "schema": "observational-inventory-v1",
        "freeze_date_utc": FREEZE_DATE_UTC,
        "scope": "local files only; absence means absent from this checkout, not absent upstream",
        "channels": {
            "sparc": {
                "upstream": {
                    "name": "SPARC database",
                    "official_url": "https://astroweb.cwru.edu/SPARC/",
                },
                "local_artifacts": sparc_artifacts,
                "derived_rows": len(sparc["results"]),
                "unique_galaxy_ids": len({row["galaxy"] for row in sparc["results"]}),
                "point_level_rotation_curves_local": False,
                "per_point_covariance_local": False,
                "calibration_exposure": "the five global readout parameters were optimized on all 175 observed curves",
                "historical_summary": _sparc_summary(sparc),
                "confirmatory_use_now": False,
            },
            "boss_dr12": {
                "upstream": {
                    "name": "BOSS DR12 consensus RSD",
                    "primary_reference": "https://arxiv.org/abs/1607.03155",
                },
                "local_artifacts": boss_artifacts,
                "observed_vector_local": True,
                "full_covariance_local": True,
                "redshifts": boss["dataset"]["z"],
                "historical_summary": _boss_summary(boss),
                "calibration_exposure": "the three values and covariance have already been used in the manuscript comparison",
                "confirmatory_use_now": False,
            },
            "desi": {
                "upstream": {
                    "name": "DESI full-shape and RSD likelihoods",
                    "year1_primary_reference": "https://arxiv.org/abs/2411.12021",
                    "official_results_guide": "https://www.desi.lbl.gov/2024/11/19/desi-y1-results-nov-19-guide/",
                },
                "local_artifacts": desi_artifacts,
                "constructed_residual_bins": len(desi["z_bins"]),
                "official_observed_vector_local": False,
                "official_covariance_or_likelihood_local": False,
                "local_residual_status": desi.get("status"),
                "local_residual_is_observation": False,
                "reason": "delta_fsigma8 is a constructed residual used by the inverse operator and has no official DESI data provenance",
                "confirmatory_use_now": False,
            },
            "nist_clocks": {
                "upstream": {
                    "name": "NIST mds2-2206 coherent optical-clock down-conversion data",
                    "official_dataset": "https://data.nist.gov/metrics/mds2-2206",
                    "declared_archive_doi": None if nist_external is None else nist_external.get("doi"),
                },
                "local_artifacts": nist_artifacts,
                "declared_external_files": [] if nist_external is None else nist_external.get("files", []),
                "raw_observed_series_local": False,
                "local_bundle_redacted": True,
                "historical_summary": _nist_summary(nist),
                "calibration_exposure": "both named channels were already used in historical clock/readout work",
                "confirmatory_use_now": False,
            },
        },
    }


def deterministic_sparc_split(galaxy_ids: Iterable[str]) -> dict[str, Any]:
    identifiers = sorted(set(galaxy_ids))
    if len(identifiers) != 175:
        raise ValueError(f"expected 175 unique SPARC galaxies, found {len(identifiers)}")
    ranked = sorted(
        identifiers,
        key=lambda name: (
            hashlib.sha256(f"{SPARC_SPLIT_SALT}|{name}".encode("utf-8")).hexdigest(),
            name,
        ),
    )
    groups = {
        "train": ranked[:122],
        "validation": ranked[122:148],
        "test": ranked[148:],
    }
    assignment = {
        name: group
        for group, names in groups.items()
        for name in names
    }
    return {
        "schema": "deterministic-holdout-v1",
        "split_id": SPARC_SPLIT_ID,
        "salt": SPARC_SPLIT_SALT,
        "algorithm": "sort unique galaxy IDs by SHA256(salt + '|' + galaxy_id), then take exact 122/26/27 partitions",
        "unit": "galaxy; radial samples from one galaxy may never cross partitions",
        "counts": {group: len(names) for group, names in groups.items()},
        "groups": groups,
        "assignment_sha256": document_sha256(assignment),
        "leakage_warning": "This split is frozen for a clean refit, but it cannot turn previously inspected SPARC outcomes into a blinded confirmatory test.",
        "confirmatory_status": "development_only_due_to_prior_full_sample_exposure",
    }


def deterministic_clock_session_bucket(session_id: str) -> str:
    """Assign a whole future acquisition session without sample-level leakage."""

    if not session_id.strip():
        raise ValueError("session_id must be non-empty")
    digest = hashlib.sha256(
        f"{CLOCK_SPLIT_SALT}|{session_id}".encode("utf-8")
    ).digest()
    unit_interval = int.from_bytes(digest, "big") / (1 << 256)
    if unit_interval < 0.50:
        return "calibration"
    if unit_interval < 0.75:
        return "validation"
    return "test"


def _metric_contract() -> dict[str, Any]:
    return {
        "common_rules": [
            "Freeze geometry, dictionaries, model parameters, masks, nuisance priors, and the score before opening a test outcome.",
            "Never label a score confirmatory when its observations were used to choose parameters, transforms, endpoints, cuts, or error models.",
            "Use the same observations, masks, covariance, nuisance policy, and likelihood normalization for every compared model.",
            "Report absolute goodness of fit and uncertainty, not only win counts or a delta relative to a weak baseline.",
            "A failed or null holdout is preserved; it is not moved into calibration and rerun under the same prediction ID.",
        ],
        "galaxy_rotation_curves": {
            "primary": "sum of held-out Gaussian log predictive densities, normalized per retained velocity datum",
            "required_inputs": [
                "point-level velocity observations",
                "reported errors or covariance",
                "baryonic component curves",
                "independently fixed or hierarchically predicted distance, inclination, and mass-to-light nuisances",
            ],
            "secondary": [
                "median per-galaxy chi2 per retained datum",
                "galaxy-level win fraction with a galaxy-cluster bootstrap interval",
                "residual calibration by radius and surface-brightness strata",
            ],
            "forbidden_primary_metric": "the historical velocity-weighted ranking loss",
        },
        "growth_rsd": {
            "primary": "generalized chi2 r^T C^-1 r or the official full-shape log likelihood",
            "primary_contrast": "delta chi2 = chi2_HOLO - chi2_LCDM on the same frozen data vector and nuisance treatment",
            "target_window": "predeclared effective-redshift bins intersecting 0.90 <= z_eff <= 1.05",
            "required_reporting": [
                "full covariance or official likelihood",
                "Alcock-Paczynski and fiducial-cosmology conventions",
                "scale cuts, tracer selection, nuisance count, and any look-elsewhere correction",
            ],
        },
        "atomic_clocks": {
            "primary": "out-of-session predictive log likelihood or predeclared matched-filter statistic with colored-noise covariance",
            "split_unit": "independent acquisition session/day/site/species, never interleaved samples",
            "required_reporting": [
                "injection-recovery efficiency",
                "environmental vetoes and dead time",
                "trials correction if frequency, phase, or coherence time is scanned",
                "cross-species or cross-site coherence with parameters fixed before the test session",
            ],
        },
    }


def _baseline_contract() -> dict[str, Any]:
    return {
        "sparc_primary_zero_test_tuning": [
            {
                "id": "baryons_only_newton",
                "rule": "same baryonic inputs and independently frozen nuisances as HOLO",
            },
            {
                "id": "canonical_rar_or_mond",
                "rule": "global acceleration scale and interpolation choice fixed on train only; no test-galaxy tuning",
            },
            {
                "id": "abundance_matched_cdm",
                "rule": "halo relation and scatter learned externally or on train only; evaluate the predictive distribution",
            },
        ],
        "sparc_secondary_nuisance_profiled": {
            "models": ["HOLO", "RAR/MOND", "NFW or cored CDM"],
            "rule": "all models receive the same nuisance prior budget; integrate or cross-validate nuisance parameters rather than quoting unpenalized best-fit test chi2",
        },
        "growth": [
            {
                "id": "matched_flat_lcdm",
                "rule": "freeze the same external cosmological parameters and use the identical official likelihood",
            },
            {
                "id": "survey_reference_model",
                "rule": "reproduce the collaboration baseline before scoring HOLO",
            },
        ],
        "clocks": [
            {
                "id": "noise_plus_registered_systematics",
                "rule": "constant/drift/environmental terms trained only on calibration sessions",
            },
            {
                "id": "blind_injection_controls",
                "rule": "include null and synthetic signals processed by the identical pipeline",
            },
        ],
    }


def build_manifest(
    repo_root: Path,
    inventory: dict[str, Any],
    sparc_split: dict[str, Any],
) -> dict[str, Any]:
    sparc = read_json(repo_root / SPARC_FORWARD)
    boss = read_json(repo_root / BOSS_DR12)
    growth = read_json(repo_root / GROWTH_REPORT)
    nist = read_json(repo_root / NIST_UV)

    predictions = [
        {
            "id": "sparc_global_readout_clean_refit_v1",
            "domain": "galaxy_rotation_curves",
            "observable": "point-level circular velocity conditioned only on baryonic inputs and five frozen global readout parameters",
            "local_descriptive_evaluation_available": True,
            "local_confirmatory_evaluation_available": False,
            "confirmatory_eligible_now": False,
            "status": "blocked_clean_refit_and_external_holdout",
            "reason_codes": [
                "ALL_175_USED_TO_FIT_GLOBAL_PARAMETERS",
                "POINT_LEVEL_OBSERVATIONS_NOT_LOCAL",
                "CURRENT_SPLIT_OUTCOMES_ALREADY_EXPOSED",
            ],
            "development_split": SPARC_SPLIT_ID,
            "next_test": "refit five parameters on train only, use validation once, then freeze; treat the SPARC test group as honest development estimation and reserve a new external galaxy catalogue for confirmation",
        },
        {
            "id": "boss_dr12_dictionary_growth_v1",
            "domain": "cosmological_growth",
            "observable": "f_sigma8 at z = 0.38, 0.51, 0.61",
            "local_descriptive_evaluation_available": True,
            "local_confirmatory_evaluation_available": False,
            "confirmatory_eligible_now": False,
            "status": "historical_external_comparison_only",
            "reason_codes": [
                "BOSS_VECTOR_ALREADY_INSPECTED",
                "COMPOSITE_DICTIONARY_NOT_4D_DERIVATION",
                "NO_STATISTICAL_PREFERENCE_OVER_LCDM",
            ],
            "audit_result": _boss_summary(boss),
            "next_test": "freeze a 4D growth prediction and score an untouched later survey release with its official likelihood",
        },
        {
            "id": "desi_high_redshift_growth_holdout_v1",
            "domain": "cosmological_growth",
            "observable": "f_sigma8 or full-shape growth likelihood in predeclared bins intersecting 0.90 <= z_eff <= 1.05",
            "local_descriptive_evaluation_available": False,
            "local_confirmatory_evaluation_available": False,
            "confirmatory_eligible_now": False,
            "status": "prospective_official_likelihood_missing",
            "reason_codes": [
                "LOCAL_DESI_RESIDUAL_IS_MODEL_DERIVED",
                "OFFICIAL_OBSERVED_VECTOR_AND_COVARIANCE_ABSENT",
                "YEAR1_RESULTS_ALREADY_PUBLIC_AND_INSPECTED",
            ],
            "release_holdout_rule": "BOSS DR12 and DESI Year 1 are development context; the first official later DESI growth likelihood not used to alter this protocol is the test release",
            "legacy_dictionary_signature": {
                "source": GROWTH_REPORT.as_posix(),
                "source_sha256": file_sha256(repo_root / GROWTH_REPORT),
                "endpoint_z": growth["series"]["z"][-1],
                "endpoint_delta_fsigma8_percent": growth["series"]["delta_pct"][-1],
                "classification": "edge-of-domain composite-dictionary signature; not a derived 4D prediction",
            },
            "next_test": "ingest the official frozen likelihood without changing the prediction curve, target window, cuts, or score",
        },
        {
            "id": "nist_uv_readout_historical_v1",
            "domain": "atomic_clocks",
            "observable": "historical Yb-channel phase-derived comparison",
            "local_descriptive_evaluation_available": True,
            "local_confirmatory_evaluation_available": False,
            "confirmatory_eligible_now": False,
            "status": "historical_null_redacted",
            "reason_codes": [
                "OBSERVED_AND_RESIDUAL_SERIES_REDACTED_LOCALLY",
                "BOTH_CHANNELS_ALREADY_USED",
                "TIME_DICTIONARY_NOT_UNIQUE",
            ],
            "audit_result": _nist_summary(nist),
            "next_test": "use a new acquisition session and dissimilar transition/site after deriving a dimensional, non-universal clock coupling",
        },
        {
            "id": "metric_only_tree_level_clock_null_v1",
            "domain": "atomic_clocks",
            "observable": "differential frequency ratio of co-located dissimilar atomic transitions",
            "local_descriptive_evaluation_available": False,
            "local_confirmatory_evaluation_available": False,
            "confirmatory_eligible_now": False,
            "status": "prospective_null_requires_new_data",
            "theory_statement": "the current universal metric-only completion has no direct classical Maxwell vertex and no leading universal differential clock-ratio signal",
            "reason_codes": [
                "NO_NEW_INDEPENDENT_CLOCK_SESSION_LOCAL",
                "NONUNIVERSAL_ANOMALY_COEFFICIENTS_NOT_DERIVED",
            ],
            "next_test": "a predeclared differential line in independent clock sessions would falsify the minimal null or require an explicitly new interaction model",
        },
    ]

    readiness = {
        "audit_only_now": [
            "sparc_global_readout_clean_refit_v1",
            "boss_dr12_dictionary_growth_v1",
            "nist_uv_readout_historical_v1",
        ],
        "prospective_or_blocked": [
            "sparc_global_readout_clean_refit_v1",
            "desi_high_redshift_growth_holdout_v1",
            "nist_uv_readout_historical_v1",
            "metric_only_tree_level_clock_null_v1",
        ],
        "confirmatory_evaluable_locally_now": [],
        "bottom_line": "No local observational arm currently qualifies as a clean confirmatory holdout.",
    }

    return {
        "schema": SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "freeze_date_utc": FREEZE_DATE_UTC,
        "claim_policy": "A local calculation may be reproducible yet remain in-sample, historical, or synthetic. Only a datum not used to choose the tested pipeline can support a confirmatory claim.",
        "input_documents": {
            "observational_inventory_sha256": document_sha256(inventory),
            "sparc_split_sha256": document_sha256(sparc_split),
        },
        "historical_audit_receipts": {
            "sparc": _sparc_summary(sparc),
            "boss_dr12": _boss_summary(boss),
            "nist_uv": _nist_summary(nist),
        },
        "data_separation": {
            "sparc": "deterministic galaxy-level 70/15/15 split for a clean refit; current outcomes remain development-only because the full sample was previously used",
            "growth": "dataset-release barrier: BOSS DR12 and inspected DESI Year 1 are development; a later untouched official release is test",
            "clocks": "group by independent acquisition session/day/site/species; no interleaved sample split and no reuse of the two historical NIST channels as test",
        },
        "prospective_split_rules": {
            "sparc": {
                "split_id": SPARC_SPLIT_ID,
                "unit": "galaxy",
                "assignment_document": "sparc_split_v1.json",
            },
            "growth": {
                "split_id": "chronological-official-release-barrier-v1",
                "development": ["BOSS_DR12", "DESI_YEAR1_INSPECTED"],
                "test": "chronologically first later official growth likelihood not used to change this protocol",
                "unit": "complete covariance-coupled survey likelihood, never individual correlated redshift rows",
            },
            "clocks": {
                "split_id": CLOCK_SPLIT_ID,
                "salt": CLOCK_SPLIT_SALT,
                "algorithm": "SHA256(salt + '|' + session_id) mapped to [0,1): calibration <0.50, validation <0.75, otherwise test",
                "unit": "complete independent acquisition session/day/site/species; all channels from one session stay together",
                "historical_nist_sessions": "development-only regardless of hash bucket because outcomes were already inspected",
            },
        },
        "metrics": _metric_contract(),
        "baselines": _baseline_contract(),
        "predictions": predictions,
        "readiness": readiness,
    }


def build_documents(repo_root: Path) -> dict[str, dict[str, Any]]:
    inventory = build_inventory(repo_root)
    sparc = read_json(repo_root / SPARC_FORWARD)
    split = deterministic_sparc_split(row["galaxy"] for row in sparc["results"])
    manifest = build_manifest(repo_root, inventory, split)
    return {
        "observational_inventory.json": inventory,
        "sparc_split_v1.json": split,
        "prediction_manifest.json": manifest,
    }


def write_documents(output_dir: Path, documents: dict[str, dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, document in documents.items():
        path = output_dir / filename
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
            + "\n",
            encoding="utf-8",
        )


def check_documents(output_dir: Path, documents: dict[str, dict[str, Any]]) -> list[str]:
    stale: list[str] = []
    for filename, expected in documents.items():
        path = output_dir / filename
        if not path.is_file() or read_json(path) != expected:
            stale.append(filename)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root_from_script())
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--check", action="store_true", help="fail if committed JSON differs from a fresh build")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
    documents = build_documents(repo_root)
    if args.check:
        stale = check_documents(output_dir, documents)
        if stale:
            raise SystemExit("stale prediction-factory documents: " + ", ".join(stale))
        print("prediction-factory documents are current")
        return 0

    write_documents(output_dir, documents)
    print(f"wrote {len(documents)} documents to {output_dir}")
    print(documents["prediction_manifest.json"]["readiness"]["bottom_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
