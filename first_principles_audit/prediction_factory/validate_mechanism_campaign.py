#!/usr/bin/env python3
"""Validate a ``holo.mechanism-campaign.v1`` contract fail closed.

The adjacent JSON Schema defines the portable structural contract.  This
module adds the semantic rules that JSON Schema cannot express compactly:

* the C1 -> C2 -> C3 ladder only unlocks after an explicit failure;
* every step record is content-addressed, without claiming an authenticated
  pre-execution timestamp;
* completed or blocked gates require tests, artifacts and a recorded review
  attempt; provider failures are recorded without being treated as output;
* telemetry, observational inputs, post-hoc fitting and physical claims never
  count as mechanism evidence; and
* missing, unknown or inconsistent state is invalid rather than permissive.

Only the Python standard library is required.  Validation never writes files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_ID = "holo.mechanism-campaign.v1"
HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
SCHEMA_PATH = HERE / "schemas" / "holo.mechanism-campaign.v1.schema.json"

EXPECTED_LADDER = (
    ("C1", 1, "derivative_condensate"),
    ("C2", 2, "critical_continuum"),
    ("C3", 3, "geometric_brane_transition"),
)

EXPECTED_RECEIPT_BINDINGS = {
    "C1": {
        "artifact_id": "artifact_c1",
        "artifact_path": (
            "first_principles_audit/prediction_factory/artifacts/"
            "c1_bk_derivative_gate.json"
        ),
        "artifact_schema": "holo.c1-bk-derivative-gate.v1",
        "test_id": "test_c1",
        "test_command": (
            "python3 -m unittest "
            "first_principles_audit.prediction_factory.test_c1_bk_derivative_gate"
        ),
        "test_source_path": (
            "first_principles_audit/prediction_factory/" "test_c1_bk_derivative_gate.py"
        ),
        "review_id": "skai_c1_review_attempt",
    },
    "C2": {
        "artifact_id": "artifact_c2",
        "artifact_path": (
            "first_principles_audit/prediction_factory/artifacts/"
            "c2_critical_continuum_gate.json"
        ),
        "artifact_schema": "holo.c2-critical-continuum-gate.v1",
        "test_id": "test_c2",
        "test_command": (
            "python3 -m unittest "
            "first_principles_audit.prediction_factory.test_c2_critical_continuum_gate"
        ),
        "test_source_path": (
            "first_principles_audit/prediction_factory/"
            "test_c2_critical_continuum_gate.py"
        ),
        "review_id": "skai_c2_review_attempt",
    },
    "C3": {
        "artifact_id": "artifact_c3",
        "artifact_path": (
            "first_principles_audit/prediction_factory/artifacts/"
            "c3_geometric_transition_gate.json"
        ),
        "artifact_schema": "holo.c3-geometric-transition-gate.v1",
        "test_id": "test_c3",
        "test_command": (
            "python3 -m unittest "
            "first_principles_audit.prediction_factory.test_c3_geometric_transition_gate"
        ),
        "test_source_path": (
            "first_principles_audit/prediction_factory/"
            "test_c3_geometric_transition_gate.py"
        ),
        "review_id": "skai_c3_review_attempt",
    },
}

REQUIRED_CHECK_IDS = {
    "C1": frozenset(
        {
            "five_dimensional_operator_basis_closed",
            "ward_or_isometry_fixes_homogeneity",
            "x_negative_branch_hyperbolic_without_patch",
            "background_and_junctions_preserved",
        }
    ),
    "C2": frozenset(
        {
            "nonlinear_generating_functional_derived",
            "positive_gapless_spectral_measure",
            "local_amplitude_reduction",
            "target_exponent_and_sign_emerge",
            "no_gapless_mode_integrated_out",
        }
    ),
    "C3": frozenset(
        {
            "codimension_zero_criticality",
            "single_physical_collective",
            "dirac_rank_controlled",
            "uniform_positive_gap_for_other_modes",
            "q2y_and_g6_derived",
            "two_source_geometries_agree",
        }
    ),
}

REQUIRED_FORBIDDEN_INPUTS = frozenset(
    {
        "observational_tables",
        "post_hoc_target_coefficients",
        "undeclared_external_outputs",
    }
)

FORBIDDEN_INPUT_PATH_MARKERS = frozenset(
    {
        "sparc",
        "rotmod",
        "observational",
        "boss",
        "desi",
        "nist",
    }
)

TOP_LEVEL_KEYS = frozenset(
    {
        "schema",
        "campaign_id",
        "declared_record_time_utc",
        "repository",
        "objective",
        "inputs",
        "data_policy",
        "ladder_policy",
        "steps",
        "claim_gate",
        "verdict",
    }
)

HASH64 = re.compile(r"^[0-9a-f]{64}$")
COMMIT40 = re.compile(r"^[0-9a-f]{40}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
CAMPAIGN_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")


class CampaignValidationError(ValueError):
    """One or more contract violations, retained in deterministic order."""

    def __init__(self, errors: Iterable[str]):
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def step_record_digest(step_record: Mapping[str, Any]) -> str:
    """Return the canonical SHA-256 for a campaign step record."""

    rendered = json.dumps(
        step_record,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def _expect_exact_keys(
    value: Any,
    expected: frozenset[str],
    path: str,
    errors: list[str],
) -> dict[str, Any] | None:
    if type(value) is not dict:
        errors.append(f"{path}: expected object")
        return None
    actual = frozenset(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing:
        errors.append(f"{path}: missing keys {missing}")
    if unknown:
        errors.append(f"{path}: unknown keys {unknown}")
    return value


def _expect_list(value: Any, path: str, errors: list[str]) -> list[Any] | None:
    if type(value) is not list:
        errors.append(f"{path}: expected array")
        return None
    return value


def _expect_string(
    value: Any,
    path: str,
    errors: list[str],
    *,
    pattern: re.Pattern[str] | None = None,
) -> str | None:
    if type(value) is not str or not value.strip():
        errors.append(f"{path}: expected non-empty string")
        return None
    if pattern is not None and pattern.fullmatch(value) is None:
        errors.append(f"{path}: invalid format")
    return value


def _expect_bool(
    value: Any,
    expected: bool,
    path: str,
    errors: list[str],
) -> None:
    if type(value) is not bool or value is not expected:
        errors.append(f"{path}: must be {expected!r}")


def _expect_int(
    value: Any,
    expected: int,
    path: str,
    errors: list[str],
) -> None:
    if type(value) is not int or value != expected:
        errors.append(f"{path}: must be integer {expected}")


def _expect_choice(
    value: Any,
    choices: set[str] | frozenset[str],
    path: str,
    errors: list[str],
) -> None:
    if type(value) is not str or value not in choices:
        errors.append(f"{path}: expected one of {sorted(choices)}")


def _expect_utc(value: Any, path: str, errors: list[str]) -> None:
    if type(value) is not str or not value.endswith("Z"):
        errors.append(f"{path}: expected second-resolution UTC timestamp")
        return
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        errors.append(f"{path}: expected second-resolution UTC timestamp")
        return
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        errors.append(f"{path}: timestamp is not canonical")


def _expect_hash(value: Any, path: str, errors: list[str]) -> None:
    if type(value) is not str or HASH64.fullmatch(value) is None:
        errors.append(f"{path}: expected lowercase SHA-256")


def _expect_identifier(value: Any, path: str, errors: list[str]) -> None:
    if type(value) is not str or IDENTIFIER.fullmatch(value) is None:
        errors.append(f"{path}: invalid identifier")


def _expect_unique_strings(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int = 0,
) -> list[str] | None:
    items = _expect_list(value, path, errors)
    if items is None:
        return None
    if len(items) < minimum:
        errors.append(f"{path}: expected at least {minimum} item(s)")
    for index, item in enumerate(items):
        _expect_identifier(item, f"{path}[{index}]", errors)
    if len(items) != len(set(item for item in items if type(item) is str)):
        errors.append(f"{path}: duplicate values are forbidden")
    return items


def _expect_relative_path(value: Any, path: str, errors: list[str]) -> None:
    text = _expect_string(value, path, errors)
    if text is None:
        return
    if "\\" in text:
        errors.append(f"{path}: path must use POSIX separators")
        return
    candidate = PurePosixPath(text)
    if candidate.is_absolute() or text in {".", ".."} or ".." in candidate.parts:
        errors.append(f"{path}: path must be repository-relative without '..'")


def _reject_non_finite(value: Any, path: str, errors: list[str]) -> None:
    if type(value) is float and not math.isfinite(value):
        errors.append(f"{path}: non-finite numbers are forbidden")
    elif type(value) is dict:
        for key, child in value.items():
            _reject_non_finite(child, f"{path}.{key}", errors)
    elif type(value) is list:
        for index, child in enumerate(value):
            _reject_non_finite(child, f"{path}[{index}]", errors)


def _validate_schema_identity(errors: list[str]) -> None:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"schema_contract: cannot load {SCHEMA_PATH.name}: {exc}")
        return
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("schema_contract: unexpected JSON Schema dialect")
    declared = schema.get("properties", {}).get("schema", {}).get("const")
    if declared != SCHEMA_ID:
        errors.append("schema_contract: validator/schema identifier mismatch")
    if schema.get("additionalProperties") is not False:
        errors.append("schema_contract: top-level unknown fields must be rejected")


def _validate_repository(value: Any, errors: list[str]) -> None:
    path = "campaign.repository"
    expected = frozenset(
        {
            "declared_baseline_commit",
            "declared_worktree_dirty_at_start",
            "unrelated_changes_preserved",
            "remote_mutation_authorized",
            "publication_authorized",
        }
    )
    obj = _expect_exact_keys(value, expected, path, errors)
    if obj is None:
        return
    commit = obj.get("declared_baseline_commit")
    if type(commit) is not str or COMMIT40.fullmatch(commit) is None:
        errors.append(
            f"{path}.declared_baseline_commit: expected lowercase 40-hex commit"
        )
    if type(obj.get("declared_worktree_dirty_at_start")) is not bool:
        errors.append(f"{path}.declared_worktree_dirty_at_start: expected boolean")
    _expect_bool(
        obj.get("unrelated_changes_preserved"),
        True,
        f"{path}.unrelated_changes_preserved",
        errors,
    )
    _expect_bool(
        obj.get("remote_mutation_authorized"),
        False,
        f"{path}.remote_mutation_authorized",
        errors,
    )
    _expect_bool(
        obj.get("publication_authorized"),
        False,
        f"{path}.publication_authorized",
        errors,
    )


def _validate_objective(value: Any, errors: list[str]) -> None:
    path = "campaign.objective"
    expected = frozenset({"statement", "scope", "target_blind", "requested_output"})
    obj = _expect_exact_keys(value, expected, path, errors)
    if obj is None:
        return
    _expect_string(obj.get("statement"), f"{path}.statement", errors)
    if obj.get("scope") != "theory_only":
        errors.append(f"{path}.scope: must be 'theory_only'")
    _expect_bool(obj.get("target_blind"), False, f"{path}.target_blind", errors)
    if obj.get("requested_output") != "adjudication_record_only":
        errors.append(f"{path}.requested_output: must be 'adjudication_record_only'")


def _validate_inputs(value: Any, errors: list[str]) -> set[str]:
    path = "campaign.inputs"
    rows = _expect_list(value, path, errors)
    if rows is None:
        return set()
    if not rows:
        errors.append(f"{path}: at least one theory input is required")
    expected = frozenset(
        {
            "id",
            "path",
            "sha256",
            "schema",
            "role",
            "integrity_verified",
            "observational",
        }
    )
    identifiers: list[str] = []
    paths: list[str] = []
    for index, row in enumerate(rows):
        row_path = f"{path}[{index}]"
        obj = _expect_exact_keys(row, expected, row_path, errors)
        if obj is None:
            continue
        identifier = obj.get("id")
        _expect_identifier(identifier, f"{row_path}.id", errors)
        if type(identifier) is str:
            identifiers.append(identifier)
        input_path = obj.get("path")
        _expect_relative_path(input_path, f"{row_path}.path", errors)
        if type(input_path) is str:
            paths.append(input_path)
            path_tokens = frozenset(
                token for token in re.split(r"[/_.-]+", input_path.casefold()) if token
            )
            markers = sorted(FORBIDDEN_INPUT_PATH_MARKERS & path_tokens)
            if markers:
                errors.append(
                    f"{row_path}.path: observational marker(s) {markers} are forbidden"
                )
        _expect_hash(obj.get("sha256"), f"{row_path}.sha256", errors)
        schema = obj.get("schema")
        if schema is not None:
            _expect_string(schema, f"{row_path}.schema", errors)
        _expect_choice(
            obj.get("role"),
            {"theory", "geometry", "boundary", "prior_certificate"},
            f"{row_path}.role",
            errors,
        )
        _expect_bool(
            obj.get("integrity_verified"),
            True,
            f"{row_path}.integrity_verified",
            errors,
        )
        _expect_bool(
            obj.get("observational"),
            False,
            f"{row_path}.observational",
            errors,
        )
    if len(identifiers) != len(set(identifiers)):
        errors.append(f"{path}: input ids must be unique")
    if len(paths) != len(set(paths)):
        errors.append(f"{path}: input paths must be unique")
    return set(identifiers)


def _validate_data_policy(value: Any, errors: list[str]) -> None:
    path = "campaign.data_policy"
    expected = frozenset(
        {
            "observational_inputs_read",
            "provenance_audit_scope",
            "forbidden_inputs",
            "parameter_fitting_authorized",
            "post_hoc_target_matching_authorized",
            "external_physics_input_access_authorized",
            "review_channel_access_authorized",
            "physical_actions_authorized",
        }
    )
    obj = _expect_exact_keys(value, expected, path, errors)
    if obj is None:
        return
    observed = _expect_list(
        obj.get("observational_inputs_read"),
        f"{path}.observational_inputs_read",
        errors,
    )
    if observed is not None and observed:
        errors.append(f"{path}.observational_inputs_read: must be empty")
    if obj.get("provenance_audit_scope") != "declared_repository_paths_only":
        errors.append(
            f"{path}.provenance_audit_scope: must be "
            "'declared_repository_paths_only'"
        )
    forbidden = _expect_unique_strings(
        obj.get("forbidden_inputs"),
        f"{path}.forbidden_inputs",
        errors,
        minimum=3,
    )
    if forbidden is not None:
        missing = sorted(REQUIRED_FORBIDDEN_INPUTS - set(forbidden))
        if missing:
            errors.append(f"{path}.forbidden_inputs: missing mandatory bans {missing}")
    for key in (
        "parameter_fitting_authorized",
        "post_hoc_target_matching_authorized",
        "external_physics_input_access_authorized",
        "physical_actions_authorized",
    ):
        _expect_bool(obj.get(key), False, f"{path}.{key}", errors)
    _expect_bool(
        obj.get("review_channel_access_authorized"),
        True,
        f"{path}.review_channel_access_authorized",
        errors,
    )


def _validate_ladder_policy(value: Any, errors: list[str]) -> None:
    path = "campaign.ladder_policy"
    expected = frozenset(
        {
            "mode",
            "step_count",
            "unlock_requires_previous_failure",
        }
    )
    obj = _expect_exact_keys(value, expected, path, errors)
    if obj is None:
        return
    if obj.get("mode") != "sequential":
        errors.append(f"{path}.mode: must be 'sequential'")
    _expect_int(obj.get("step_count"), 3, f"{path}.step_count", errors)
    _expect_bool(
        obj.get("unlock_requires_previous_failure"),
        True,
        f"{path}.unlock_requires_previous_failure",
        errors,
    )


def _validate_step_record(
    value: Any,
    record_digest: Any,
    input_ids: set[str],
    path: str,
    errors: list[str],
) -> None:
    expected = frozenset(
        {
            "declared_record_time_utc",
            "hypothesis",
            "declared_test",
            "kill_gate",
            "allowed_input_ids",
            "target_blind",
            "target_disclosure",
            "no_tuning",
            "binary_kill_gate",
            "local_five_dimensional_action_required",
            "record_time_authentication",
        }
    )
    obj = _expect_exact_keys(value, expected, path, errors)
    if obj is None:
        return
    _expect_utc(
        obj.get("declared_record_time_utc"),
        f"{path}.declared_record_time_utc",
        errors,
    )
    for key in ("hypothesis", "declared_test", "kill_gate"):
        _expect_string(obj.get(key), f"{path}.{key}", errors)
    allowed = _expect_unique_strings(
        obj.get("allowed_input_ids"),
        f"{path}.allowed_input_ids",
        errors,
        minimum=1,
    )
    if allowed is not None:
        unknown = sorted(set(allowed) - input_ids)
        if unknown:
            errors.append(f"{path}.allowed_input_ids: unknown input ids {unknown}")
    target_blind = obj.get("target_blind")
    _expect_bool(target_blind, False, f"{path}.target_blind", errors)
    disclosure = obj.get("target_disclosure")
    _expect_choice(
        disclosure,
        {
            "known_external_candidate",
            "known_acceptance_target",
            "known_mechanism_requirements",
        },
        f"{path}.target_disclosure",
        errors,
    )
    for key in (
        "no_tuning",
        "binary_kill_gate",
        "local_five_dimensional_action_required",
    ):
        _expect_bool(obj.get(key), True, f"{path}.{key}", errors)
    if (
        obj.get("record_time_authentication")
        != "content_addressed_not_timestamp_authenticated"
    ):
        errors.append(
            f"{path}.record_time_authentication: must disclose the "
            "unauthenticated timestamp"
        )
    _expect_hash(record_digest, f"{path}_sha256", errors)
    if type(record_digest) is str and HASH64.fullmatch(record_digest):
        try:
            expected_digest = step_record_digest(obj)
        except (TypeError, ValueError) as exc:
            errors.append(f"{path}: cannot canonicalize step record: {exc}")
        else:
            if record_digest != expected_digest:
                errors.append(f"{path}_sha256: digest does not match step record")


def _validate_artifact_receipt(value: Any, path: str, errors: list[str]) -> str | None:
    expected = frozenset({"id", "path", "sha256", "schema"})
    obj = _expect_exact_keys(value, expected, path, errors)
    if obj is None:
        return None
    identifier = obj.get("id")
    _expect_identifier(identifier, f"{path}.id", errors)
    _expect_relative_path(obj.get("path"), f"{path}.path", errors)
    _expect_hash(obj.get("sha256"), f"{path}.sha256", errors)
    _expect_string(obj.get("schema"), f"{path}.schema", errors)
    return identifier if type(identifier) is str else None


def _validate_test_receipt(value: Any, path: str, errors: list[str]) -> str | None:
    expected = frozenset({"id", "command", "exit_code", "source_path", "source_sha256"})
    obj = _expect_exact_keys(value, expected, path, errors)
    if obj is None:
        return None
    identifier = obj.get("id")
    _expect_identifier(identifier, f"{path}.id", errors)
    _expect_string(obj.get("command"), f"{path}.command", errors)
    _expect_int(obj.get("exit_code"), 0, f"{path}.exit_code", errors)
    _expect_relative_path(obj.get("source_path"), f"{path}.source_path", errors)
    _expect_hash(obj.get("source_sha256"), f"{path}.source_sha256", errors)
    return identifier if type(identifier) is str else None


def _validate_review_attempt(
    value: Any, path: str, errors: list[str]
) -> tuple[str | None, str | None, str | None, str | None]:
    expected = frozenset(
        {
            "id",
            "channel",
            "status",
            "context_sha256",
            "response_sha256",
            "literal_output_sha256",
            "literal_output_captured",
            "independent_from_builder",
            "verdict",
        }
    )
    obj = _expect_exact_keys(value, expected, path, errors)
    if obj is None:
        return None, None, None, None
    identifier = obj.get("id")
    channel = obj.get("channel")
    status = obj.get("status")
    verdict = obj.get("verdict")
    _expect_identifier(identifier, f"{path}.id", errors)
    _expect_identifier(channel, f"{path}.channel", errors)
    _expect_choice(
        status,
        {"completed", "provider_error"},
        f"{path}.status",
        errors,
    )
    _expect_hash(obj.get("context_sha256"), f"{path}.context_sha256", errors)
    _expect_hash(obj.get("response_sha256"), f"{path}.response_sha256", errors)
    literal_hash = obj.get("literal_output_sha256")
    literal = obj.get("literal_output_captured")
    independent = obj.get("independent_from_builder")
    if type(literal) is not bool:
        errors.append(f"{path}.literal_output_captured: expected boolean")
    if type(independent) is not bool:
        errors.append(f"{path}.independent_from_builder: expected boolean")
    _expect_choice(
        verdict,
        {"pass", "fail", "inconclusive"},
        f"{path}.verdict",
        errors,
    )
    if status == "completed":
        _expect_hash(literal_hash, f"{path}.literal_output_sha256", errors)
        if literal is not True:
            errors.append(
                f"{path}.literal_output_captured: completed audit requires true"
            )
        if independent is not True:
            errors.append(
                f"{path}.independent_from_builder: completed audit requires true"
            )
    elif status == "provider_error":
        if literal_hash is not None:
            errors.append(f"{path}.literal_output_sha256: provider error requires null")
        if literal is not False:
            errors.append(
                f"{path}.literal_output_captured: provider error requires false"
            )
        if independent is not False:
            errors.append(
                f"{path}.independent_from_builder: provider error requires false"
            )
        if verdict != "inconclusive":
            errors.append(f"{path}.verdict: provider error requires 'inconclusive'")
    return (
        identifier if type(identifier) is str else None,
        channel if type(channel) is str else None,
        verdict if type(verdict) is str else None,
        status if type(status) is str else None,
    )


def _validate_step(
    value: Any,
    expected_step: tuple[str, int, str],
    input_ids: set[str],
    path: str,
    errors: list[str],
) -> str | None:
    expected_keys = frozenset(
        {
            "id",
            "ordinal",
            "family",
            "status",
            "step_record",
            "step_record_sha256",
            "checks",
            "evidence",
            "reason_codes",
        }
    )
    obj = _expect_exact_keys(value, expected_keys, path, errors)
    if obj is None:
        return None
    step_id, ordinal, family = expected_step
    if obj.get("id") != step_id:
        errors.append(f"{path}.id: must be {step_id!r}")
    _expect_int(obj.get("ordinal"), ordinal, f"{path}.ordinal", errors)
    if obj.get("family") != family:
        errors.append(f"{path}.family: must be {family!r}")
    status = obj.get("status")
    _expect_choice(
        status,
        {"locked", "ready", "failed", "blocked"},
        f"{path}.status",
        errors,
    )
    _validate_step_record(
        obj.get("step_record"),
        obj.get("step_record_sha256"),
        input_ids,
        f"{path}.step_record",
        errors,
    )

    checks = _expect_list(obj.get("checks"), f"{path}.checks", errors)
    check_rows: list[dict[str, Any]] = []
    if checks is not None:
        check_keys = frozenset({"id", "status", "evidence_refs"})
        for index, check in enumerate(checks):
            check_path = f"{path}.checks[{index}]"
            row = _expect_exact_keys(check, check_keys, check_path, errors)
            if row is None:
                continue
            _expect_identifier(row.get("id"), f"{check_path}.id", errors)
            _expect_choice(
                row.get("status"),
                {"pending", "pass", "fail", "blocked"},
                f"{check_path}.status",
                errors,
            )
            _expect_unique_strings(
                row.get("evidence_refs"),
                f"{check_path}.evidence_refs",
                errors,
            )
            check_rows.append(row)
        actual_check_ids = [row.get("id") for row in check_rows]
        if len(actual_check_ids) != len(set(actual_check_ids)):
            errors.append(f"{path}.checks: check ids must be unique")
        if set(actual_check_ids) != set(REQUIRED_CHECK_IDS[step_id]):
            errors.append(
                f"{path}.checks: required ids are {sorted(REQUIRED_CHECK_IDS[step_id])}"
            )

    evidence_keys = frozenset({"artifact_receipts", "test_receipts", "review_attempts"})
    evidence = _expect_exact_keys(
        obj.get("evidence"), evidence_keys, f"{path}.evidence", errors
    )
    receipt_ids: list[str] = []
    artifact_ids: set[str] = set()
    test_ids: set[str] = set()
    review_channels: list[str] = []
    review_ids: set[str] = set()
    artifact_rows: list[Any] = []
    test_rows: list[Any] = []
    review_rows: list[Any] = []
    if evidence is not None:
        artifact_rows = (
            _expect_list(
                evidence.get("artifact_receipts"),
                f"{path}.evidence.artifact_receipts",
                errors,
            )
            or []
        )
        test_rows = (
            _expect_list(
                evidence.get("test_receipts"),
                f"{path}.evidence.test_receipts",
                errors,
            )
            or []
        )
        review_rows = (
            _expect_list(
                evidence.get("review_attempts"),
                f"{path}.evidence.review_attempts",
                errors,
            )
            or []
        )
        for index, receipt in enumerate(artifact_rows):
            identifier = _validate_artifact_receipt(
                receipt, f"{path}.evidence.artifact_receipts[{index}]", errors
            )
            if identifier is not None:
                receipt_ids.append(identifier)
                artifact_ids.add(identifier)
        for index, receipt in enumerate(test_rows):
            identifier = _validate_test_receipt(
                receipt, f"{path}.evidence.test_receipts[{index}]", errors
            )
            if identifier is not None:
                receipt_ids.append(identifier)
                test_ids.add(identifier)
        for index, receipt in enumerate(review_rows):
            identifier, channel, _review_verdict, _review_status = (
                _validate_review_attempt(
                    receipt,
                    f"{path}.evidence.review_attempts[{index}]",
                    errors,
                )
            )
            if identifier is not None:
                receipt_ids.append(identifier)
                review_ids.add(identifier)
            if channel is not None:
                review_channels.append(channel)
    binding = EXPECTED_RECEIPT_BINDINGS[step_id]
    for rows, receipt_type in (
        (artifact_rows, "artifact"),
        (test_rows, "test"),
        (review_rows, "review"),
    ):
        if rows and len(rows) != 1:
            errors.append(
                f"{path}.evidence.{receipt_type}: exactly one receipt required"
            )
    if len(artifact_rows) == 1 and type(artifact_rows[0]) is dict:
        artifact = artifact_rows[0]
        for key, expected in (
            ("id", binding["artifact_id"]),
            ("path", binding["artifact_path"]),
            ("schema", binding["artifact_schema"]),
        ):
            if artifact.get(key) != expected:
                errors.append(
                    f"{path}.evidence.artifact_receipts[0].{key}: "
                    f"must be {expected!r}"
                )
    if len(test_rows) == 1 and type(test_rows[0]) is dict:
        test = test_rows[0]
        for key, expected in (
            ("id", binding["test_id"]),
            ("command", binding["test_command"]),
            ("source_path", binding["test_source_path"]),
        ):
            if test.get(key) != expected:
                errors.append(
                    f"{path}.evidence.test_receipts[0].{key}: must be {expected!r}"
                )
    if len(review_rows) == 1 and type(review_rows[0]) is dict:
        review = review_rows[0]
        if review.get("id") != binding["review_id"]:
            errors.append(
                f"{path}.evidence.review_attempts[0].id: "
                f"must be {binding['review_id']!r}"
            )
        if review.get("channel") != "skai_chat":
            errors.append(
                f"{path}.evidence.review_attempts[0].channel: must be 'skai_chat'"
            )
    if len(receipt_ids) != len(set(receipt_ids)):
        errors.append(f"{path}.evidence: receipt ids must be unique")

    referenced: set[str] = set()
    for index, check in enumerate(check_rows):
        check_status = check.get("status")
        refs = check.get("evidence_refs")
        refs_list = refs if type(refs) is list else []
        if check_status == "pending" and refs_list:
            errors.append(
                f"{path}.checks[{index}].evidence_refs: pending checks cannot cite evidence"
            )
        if check_status in {"pass", "fail", "blocked"} and not refs_list:
            errors.append(
                f"{path}.checks[{index}].evidence_refs: decided checks require evidence"
            )
        unknown_refs = sorted(set(refs_list) - set(receipt_ids))
        if unknown_refs:
            errors.append(
                f"{path}.checks[{index}].evidence_refs: unknown receipts {unknown_refs}"
            )
        if check_status in {"pass", "fail", "blocked"}:
            if not set(refs_list) & artifact_ids:
                errors.append(
                    f"{path}.checks[{index}].evidence_refs: decided checks "
                    "require an artifact receipt"
                )
            if not set(refs_list) & test_ids:
                errors.append(
                    f"{path}.checks[{index}].evidence_refs: decided checks "
                    "require a test receipt"
                )
            cited_reviews = sorted(set(refs_list) & review_ids)
            if cited_reviews:
                errors.append(
                    f"{path}.checks[{index}].evidence_refs: review attempts are "
                    f"advisory non-evidence {cited_reviews}"
                )
            expected_refs = {binding["artifact_id"], binding["test_id"]}
            if set(refs_list) != expected_refs:
                errors.append(
                    f"{path}.checks[{index}].evidence_refs: must equal the "
                    f"bound artifact and test receipts {sorted(expected_refs)}"
                )
        referenced.update(ref for ref in refs_list if type(ref) is str)
    orphaned = sorted(set(receipt_ids) - referenced - review_ids)
    if orphaned:
        errors.append(f"{path}.evidence: unreferenced receipts {orphaned}")

    reasons = _expect_unique_strings(
        obj.get("reason_codes"), f"{path}.reason_codes", errors, minimum=1
    )
    del reasons

    check_statuses = [row.get("status") for row in check_rows]
    evidence_is_empty = not artifact_rows and not test_rows and not review_rows
    if status in {"locked", "ready"}:
        if any(item != "pending" for item in check_statuses):
            errors.append(f"{path}: locked/ready steps require all checks pending")
        if not evidence_is_empty:
            errors.append(f"{path}: locked/ready steps cannot contain evidence")
    elif status in {"failed", "blocked"}:
        if not artifact_rows or not test_rows or not review_rows:
            errors.append(
                f"{path}: completed steps require artifact, test and review attempts"
            )
        if "skai_chat" not in review_channels:
            errors.append(f"{path}: completed steps require a skai_chat review attempt")
        if status == "failed":
            if "fail" not in check_statuses:
                errors.append(f"{path}: failed step requires at least one failed check")
        else:
            if "blocked" not in check_statuses:
                errors.append(
                    f"{path}: blocked step requires at least one blocked check"
                )
            if "fail" in check_statuses:
                errors.append(
                    f"{path}: blocked step cannot contain a failed check; "
                    "use failed status"
                )
    return status if type(status) is str else None


def _validate_sequence(statuses: Sequence[str | None], errors: list[str]) -> None:
    if len(statuses) != 3 or any(status is None for status in statuses):
        return
    first, second, third = statuses
    if first == "locked":
        errors.append("campaign.steps: C1 can never be locked")
        return
    if first in {"ready", "blocked"}:
        if second != "locked" or third != "locked":
            errors.append(
                "campaign.steps: C2 and C3 stay locked until C1 explicitly fails"
            )
        return
    if first == "failed":
        if second == "locked":
            errors.append("campaign.steps: C1 failure must unlock C2")
            return
        if second in {"ready", "blocked"}:
            if third != "locked":
                errors.append(
                    "campaign.steps: C3 stays locked until C2 explicitly fails"
                )
            return
        if second == "failed" and third == "locked":
            errors.append("campaign.steps: C2 failure must unlock C3")


def _validate_claims_and_verdict(
    claim_value: Any,
    verdict_value: Any,
    statuses: Sequence[str | None],
    errors: list[str],
) -> None:
    claim_path = "campaign.claim_gate"
    claim_keys = frozenset(
        {
            "mechanism_candidate",
            "physical_completion",
            "new_force_derived",
            "lensing_derived",
            "publication_authorized",
        }
    )
    claims = _expect_exact_keys(claim_value, claim_keys, claim_path, errors)
    if claims is not None:
        for key in (
            "mechanism_candidate",
            "physical_completion",
            "new_force_derived",
            "lensing_derived",
            "publication_authorized",
        ):
            _expect_bool(claims.get(key), False, f"{claim_path}.{key}", errors)

    verdict_path = "campaign.verdict"
    verdict_keys = frozenset({"status", "selected_step", "reason_codes"})
    verdict = _expect_exact_keys(verdict_value, verdict_keys, verdict_path, errors)
    if verdict is None or len(statuses) != 3 or any(item is None for item in statuses):
        return
    _expect_choice(
        verdict.get("status"),
        {"blocked", "falsified"},
        f"{verdict_path}.status",
        errors,
    )
    selected = verdict.get("selected_step")
    if selected is not None:
        errors.append(f"{verdict_path}.selected_step: v1 requires null")
    _expect_unique_strings(
        verdict.get("reason_codes"),
        f"{verdict_path}.reason_codes",
        errors,
        minimum=1,
    )

    if all(status == "failed" for status in statuses):
        expected_status = "falsified"
    else:
        expected_status = "blocked"
    expected_selected = None
    expected_candidate = False
    if verdict.get("status") != expected_status:
        errors.append(
            f"{verdict_path}.status: must be {expected_status!r} for current steps"
        )
    if selected != expected_selected:
        errors.append(
            f"{verdict_path}.selected_step: must be {expected_selected!r} for current steps"
        )
    if (
        claims is not None
        and claims.get("mechanism_candidate") is not expected_candidate
    ):
        errors.append(
            f"{claim_path}.mechanism_candidate: must be {expected_candidate!r} for current verdict"
        )


def validate_campaign(payload: Any) -> dict[str, Any]:
    """Validate and return *payload*, or raise ``CampaignValidationError``."""

    errors: list[str] = []
    _validate_schema_identity(errors)
    _reject_non_finite(payload, "campaign", errors)
    campaign = _expect_exact_keys(payload, TOP_LEVEL_KEYS, "campaign", errors)
    if campaign is None:
        raise CampaignValidationError(errors)

    if campaign.get("schema") != SCHEMA_ID:
        errors.append(f"campaign.schema: must be {SCHEMA_ID!r}")
    campaign_id = campaign.get("campaign_id")
    if type(campaign_id) is not str or CAMPAIGN_ID.fullmatch(campaign_id) is None:
        errors.append("campaign.campaign_id: invalid campaign identifier")
    _expect_utc(
        campaign.get("declared_record_time_utc"),
        "campaign.declared_record_time_utc",
        errors,
    )
    _validate_repository(campaign.get("repository"), errors)
    _validate_objective(campaign.get("objective"), errors)
    input_ids = _validate_inputs(campaign.get("inputs"), errors)
    _validate_data_policy(campaign.get("data_policy"), errors)
    _validate_ladder_policy(campaign.get("ladder_policy"), errors)

    steps = _expect_list(campaign.get("steps"), "campaign.steps", errors)
    statuses: list[str | None] = []
    if steps is not None:
        if len(steps) != len(EXPECTED_LADDER):
            errors.append("campaign.steps: exactly C1, C2 and C3 are required")
        for index, expected_step in enumerate(EXPECTED_LADDER):
            if index >= len(steps):
                statuses.append(None)
                continue
            statuses.append(
                _validate_step(
                    steps[index],
                    expected_step,
                    input_ids,
                    f"campaign.steps[{index}]",
                    errors,
                )
            )
        if len(steps) > len(EXPECTED_LADDER):
            statuses.extend([None] * (len(steps) - len(EXPECTED_LADDER)))
    _validate_sequence(statuses, errors)
    if steps is not None and len(steps) == len(EXPECTED_LADDER):
        flags = [
            (
                step.get("step_record", {}).get("target_blind")
                if type(step) is dict and type(step.get("step_record")) is dict
                else None
            )
            for step in steps
        ]
        if all(type(flag) is bool for flag in flags):
            campaign_blind = campaign.get("objective", {}).get("target_blind")
            if campaign_blind is not all(flags):
                errors.append(
                    "campaign.objective.target_blind: must equal the conjunction "
                    "of the three step-level blinding flags"
                )
    _validate_claims_and_verdict(
        campaign.get("claim_gate"),
        campaign.get("verdict"),
        statuses,
        errors,
    )
    if errors:
        raise CampaignValidationError(errors)
    return campaign


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def verify_repository_receipts(
    payload: Mapping[str, Any],
    repository_root: str | Path = REPOSITORY_ROOT,
) -> Mapping[str, Any]:
    """Verify every versioned input, gate artifact and test source receipt."""

    root = Path(repository_root).resolve()
    errors: list[str] = []
    repository = payload.get("repository")
    declared_commit = (
        repository.get("declared_baseline_commit") if type(repository) is dict else None
    )
    try:
        git_probe = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        errors.append(f"campaign.repository: Git inspection unavailable: {exc}")
        git_probe = None
    if (
        git_probe is not None
        and git_probe.returncode == 0
        and git_probe.stdout.strip() == "true"
    ):
        commit_probe = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", f"{declared_commit}^{{commit}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if commit_probe.returncode != 0:
            errors.append(
                "campaign.repository.declared_baseline_commit: declared commit "
                "is absent from the inspected repository"
            )
        else:
            ancestor_probe = subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "merge-base",
                    "--is-ancestor",
                    str(declared_commit),
                    "HEAD",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if ancestor_probe.returncode != 0:
                errors.append(
                    "campaign.repository.declared_baseline_commit: declared commit "
                    "is not an ancestor of inspected HEAD"
                )
    receipts: list[tuple[str, Mapping[str, Any], str]] = []
    for index, receipt in enumerate(payload.get("inputs", [])):
        if type(receipt) is dict:
            receipts.append((f"campaign.inputs[{index}]", receipt, "sha256"))
    for step_index, step in enumerate(payload.get("steps", [])):
        if type(step) is not dict:
            continue
        evidence = step.get("evidence")
        if type(evidence) is not dict:
            continue
        for index, receipt in enumerate(evidence.get("artifact_receipts", [])):
            if type(receipt) is dict:
                receipts.append(
                    (
                        f"campaign.steps[{step_index}].evidence."
                        f"artifact_receipts[{index}]",
                        receipt,
                        "sha256",
                    )
                )
        for index, receipt in enumerate(evidence.get("test_receipts", [])):
            if type(receipt) is dict:
                receipts.append(
                    (
                        f"campaign.steps[{step_index}].evidence."
                        f"test_receipts[{index}]",
                        receipt,
                        "source_sha256",
                    )
                )
    for label, receipt, digest_key in receipts:
        path_key = "source_path" if digest_key == "source_sha256" else "path"
        relative = receipt.get(path_key)
        expected = receipt.get(digest_key)
        if type(relative) is not str or type(expected) is not str:
            continue
        try:
            candidate = (root / relative).resolve(strict=True)
            candidate.relative_to(root)
        except (OSError, ValueError) as exc:
            errors.append(f"{label}.{path_key}: unavailable repository file: {exc}")
            continue
        if not candidate.is_file():
            errors.append(f"{label}.{path_key}: expected regular file")
            continue
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(
                f"{label}.{digest_key}: repository receipt mismatch for {relative}"
            )
    expected_gate_decisions = {
        "C1": {
            "campaign_status": "failed",
            "decision": {"verdict": "KILL_C1"},
            "check_statuses": {
                "five_dimensional_operator_basis_closed": "fail",
                "ward_or_isometry_fixes_homogeneity": "fail",
                "x_negative_branch_hyperbolic_without_patch": "fail",
                "background_and_junctions_preserved": "blocked",
            },
            "reason_codes": ["binary_kill_gate_triggered"],
        },
        "C2": {
            "campaign_status": "failed",
            "decision": {
                "verdict": "KILL_C2",
                "kill_current_frozen_compact_spectrum": True,
                "kill_all_critical_continuum_models": False,
            },
            "check_statuses": {
                "nonlinear_generating_functional_derived": "fail",
                "positive_gapless_spectral_measure": "fail",
                "local_amplitude_reduction": "fail",
                "target_exponent_and_sign_emerge": "fail",
                "no_gapless_mode_integrated_out": "blocked",
            },
            "reason_codes": ["frozen_compact_spectrum_killed"],
        },
        "C3": {
            "campaign_status": "blocked",
            "decision": {
                "status": "BLOCKED_C3",
                "input_status": "INPUT_INCOMPLETE",
                "kill_triggered": False,
            },
            "check_statuses": {
                check_id: "blocked" for check_id in REQUIRED_CHECK_IDS["C3"]
            },
            "reason_codes": ["input_contract_incomplete"],
        },
    }
    for step_index, step in enumerate(payload.get("steps", [])):
        if type(step) is not dict:
            continue
        step_id = step.get("id")
        evidence = step.get("evidence")
        artifacts = (
            evidence.get("artifact_receipts", []) if type(evidence) is dict else []
        )
        if (
            type(step_id) is not str
            or step_id not in expected_gate_decisions
            or len(artifacts) != 1
        ):
            continue
        receipt = artifacts[0]
        if type(receipt) is not dict or type(receipt.get("path")) is not str:
            continue
        try:
            artifact_path = (root / receipt["path"]).resolve(strict=True)
            artifact_path.relative_to(root)
            artifact = json.loads(
                artifact_path.read_text(encoding="utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
            )
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(
                f"campaign.steps[{step_index}].evidence.artifact_receipts[0]: "
                f"cannot load bound gate artifact: {exc}"
            )
            continue
        binding = EXPECTED_RECEIPT_BINDINGS[step_id]
        if (
            type(artifact) is not dict
            or artifact.get("schema") != binding["artifact_schema"]
        ):
            errors.append(f"campaign.steps[{step_index}]: bound gate schema mismatch")
            continue
        expected_gate = expected_gate_decisions[step_id]
        if step.get("status") != expected_gate["campaign_status"]:
            errors.append(
                f"campaign.steps[{step_index}].status: does not match bound "
                f"{step_id} gate decision"
            )
        checks = step.get("checks")
        actual_check_statuses = (
            {row.get("id"): row.get("status") for row in checks if type(row) is dict}
            if type(checks) is list
            else {}
        )
        if actual_check_statuses != expected_gate["check_statuses"]:
            errors.append(
                f"campaign.steps[{step_index}].checks: projection does not match "
                f"the bound {step_id} gate"
            )
        if step.get("reason_codes") != expected_gate["reason_codes"]:
            errors.append(
                f"campaign.steps[{step_index}].reason_codes: projection does not "
                f"match the bound {step_id} gate"
            )
        decision = artifact.get("decision")
        for key, expected_value in expected_gate["decision"].items():
            if type(decision) is not dict or decision.get(key) != expected_value:
                errors.append(
                    f"campaign.steps[{step_index}]: bound {step_id} gate decision "
                    f"requires {key}={expected_value!r}"
                )
    if errors:
        raise CampaignValidationError(errors)
    return payload


def load_and_validate(
    path: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load one JSON campaign without accepting duplicate keys, then validate."""

    source = Path(path)
    try:
        payload = json.loads(
            source.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise CampaignValidationError(
            [f"campaign_file: cannot load strict JSON: {exc}"]
        ) from exc
    campaign = validate_campaign(payload)
    if repository_root is not None:
        verify_repository_receipts(campaign, repository_root)
    return campaign


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path, help="campaign JSON to validate")
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="root used to verify versioned input, artifact and test-source receipts",
    )
    args = parser.parse_args(argv)
    try:
        payload = load_and_validate(
            args.campaign,
            repository_root=args.repository_root,
        )
    except CampaignValidationError as exc:
        print(f"INVALID {SCHEMA_ID}", file=sys.stderr)
        for error in exc.errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    print(f"VALID {SCHEMA_ID} campaign_id={payload['campaign_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
