#!/usr/bin/env python3
"""Assemble the recorded C1 -> C2 -> C3 mechanism campaign.

The physics verdict comes from content-addressed derivations and freshly run
tests.  Skai is a required independent review *attempt*, never the decision
authority: a literal one-shot answer is retained when available, while a
provider error is recorded as inconclusive and is not cited by any physics
check.  Version 1 is an adjudication record and cannot promote a positive
mechanism candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence

from first_principles_audit.prediction_factory import (
    derive_c1_bk_derivative_gate as c1,
    derive_c2_critical_continuum_gate as c2,
    derive_c3_geometric_transition_gate as c3,
    validate_mechanism_campaign as contract,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "minimal_mechanism_campaign.json"
DEFAULT_RECEIPTS = (
    Path.home()
    / ".local/share/skai/holo_mechanism_campaign/20260831/execution_receipts.json"
)
RECEIPT_SCHEMA = "holo.mechanism-execution-receipts.v1"
BASELINE_HEAD = "1906d5a9bee1443ffd304665fc737f9c04145135"
DECLARED_RECORD_TIME_UTC = "2026-08-31T15:21:00Z"

TEST_COMMANDS = {
    "C1": (
        "python3 -m unittest "
        "first_principles_audit.prediction_factory.test_c1_bk_derivative_gate"
    ),
    "C2": (
        "python3 -m unittest "
        "first_principles_audit.prediction_factory.test_c2_critical_continuum_gate"
    ),
    "C3": (
        "python3 -m unittest "
        "first_principles_audit.prediction_factory.test_c3_geometric_transition_gate"
    ),
}

TEST_SOURCES = {
    "C1": HERE / "test_c1_bk_derivative_gate.py",
    "C2": HERE / "test_c2_critical_continuum_gate.py",
    "C3": HERE / "test_c3_geometric_transition_gate.py",
}

GATES = {
    "C1": (c1.OUTPUT, "holo.c1-bk-derivative-gate.v1"),
    "C2": (c2.OUTPUT, "holo.c2-critical-continuum-gate.v1"),
    "C3": (c3.OUTPUT, "holo.c3-geometric-transition-gate.v1"),
}

INPUTS = {
    "effective_action": (
        REPO / "first_principles_audit/artifacts/holo_effective_action.json",
        "theory",
    ),
    "interface_action": (
        REPO / "first_principles_audit/artifacts/interface_action_derivation.json",
        "boundary",
    ),
    "adm_bps_flatness": (
        HERE / "artifacts/adm_bmp_tricritical_necessity.json",
        "prior_certificate",
    ),
    "adm_quadratic": (
        HERE / "artifacts/adm_quadratic_recovery.json",
        "prior_certificate",
    ),
    "bent_brane_geometry": (
        HERE / "artifacts/bent_brane_geometry_S2.json",
        "geometry",
    ),
    "compact_brane_s2": (
        HERE / "artifacts/compact_brane_S2_backward.json",
        "prior_certificate",
    ),
    "finite_gamma_s2": (
        HERE / "artifacts/finite_gamma_brane_S2.json",
        "prior_certificate",
    ),
    "bps_biscalar_geometry": (
        HERE / "artifacts/bps_biscalar_matter_geometry.json",
        "geometry",
    ),
    "volume_selector": (
        HERE / "artifacts/bps_volume_constraint_selector.json",
        "prior_certificate",
    ),
    "collective_spectral_bridge": (
        HERE / "artifacts/collective_spectral_bridge.json",
        "prior_certificate",
    ),
}


class CampaignBuildError(ValueError):
    """The declared evidence is absent, malformed or inconsistent."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CampaignBuildError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_strict_object,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CampaignBuildError(f"cannot read {path}: {exc}") from exc
    if type(value) is not dict:
        raise CampaignBuildError(f"{path}: expected JSON object")
    return value


def _exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        actual = sorted(value) if type(value) is dict else type(value).__name__
        raise CampaignBuildError(
            f"{label}: expected keys {sorted(expected)}, got {actual}"
        )
    return value


def _private_file(raw_path: Any, label: str) -> Path:
    if type(raw_path) is not str or not raw_path:
        raise CampaignBuildError(f"{label}: path must be non-empty")
    path = Path(raw_path).expanduser().resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise CampaignBuildError(f"{label}: missing or empty file")
    try:
        path.relative_to(REPO.resolve())
    except ValueError:
        return path
    raise CampaignBuildError(f"{label}: private receipt must remain outside repository")


def _audit_receipt(step_id: str, row: Any) -> dict[str, Any]:
    row = _exact_keys(
        row,
        {"payload_path", "response_path", "verdict"},
        f"receipts.audits.{step_id}",
    )
    payload_path = _private_file(row["payload_path"], f"{step_id} payload")
    response_path = _private_file(row["response_path"], f"{step_id} response")
    payload = _read_json(payload_path)
    expected_payload = {
        "include_history",
        "mode",
        "model_fallback",
        "persist_history",
        "request_id",
        "source",
        "speak",
        "text",
        "tool_policy",
    }
    _exact_keys(payload, expected_payload, f"{step_id} payload")
    safe_values = {
        "include_history": False,
        "mode": "chat",
        "model_fallback": "none",
        "persist_history": False,
        "source": "autonomous",
        "speak": False,
        "tool_policy": "none",
    }
    for key, expected in safe_values.items():
        if payload.get(key) != expected:
            raise CampaignBuildError(f"{step_id} payload: unsafe {key}")
    try:
        uuid.UUID(str(payload.get("request_id")))
    except ValueError as exc:
        raise CampaignBuildError(f"{step_id} payload: invalid request_id") from exc
    text = payload.get("text")
    if type(text) is not str or not text.startswith(f"HOLO-{step_id}-BLIND-v1"):
        raise CampaignBuildError(f"{step_id} payload: wrong legacy request identifier")

    response = _read_json(response_path)
    if response.get("request_id") != payload["request_id"]:
        raise CampaignBuildError(f"{step_id} response: request_id mismatch")
    requested_verdict = row.get("verdict")
    if requested_verdict not in {"pass", "fail", "inconclusive"}:
        raise CampaignBuildError(f"{step_id} receipt: invalid audit verdict")
    if response.get("ok") is True:
        reply = response.get("respuesta")
        if type(reply) is not str or not reply.strip():
            raise CampaignBuildError(f"{step_id} response: missing literal answer")
        for forbidden in ("task", "video", "tool", "resultado", "tool_blocked"):
            if response.get(forbidden) is not None:
                raise CampaignBuildError(
                    f"{step_id} response: forbidden execution field {forbidden}"
                )
        status = "completed"
        literal = True
        independent = True
        literal_output_hash: str | None = _sha256_bytes(reply.encode("utf-8"))
        verdict = requested_verdict
    else:
        error = response.get("error")
        if type(error) is not str or not error.strip():
            raise CampaignBuildError(f"{step_id} response: malformed provider error")
        if requested_verdict != "inconclusive":
            raise CampaignBuildError(
                f"{step_id} provider error can only be inconclusive"
            )
        status = "provider_error"
        literal = False
        independent = False
        literal_output_hash = None
        verdict = "inconclusive"
    return {
        "id": f"skai_{step_id.lower()}_review_attempt",
        "channel": "skai_chat",
        "status": status,
        "context_sha256": _sha256_bytes(text.encode("utf-8")),
        "response_sha256": _sha256(response_path),
        "literal_output_sha256": literal_output_hash,
        "literal_output_captured": literal,
        "independent_from_builder": independent,
        "verdict": verdict,
    }


def _test_receipt(step_id: str, row: Any) -> dict[str, Any]:
    row = _exact_keys(
        row,
        {"command", "exit_code", "transcript_path"},
        f"receipts.tests.{step_id}",
    )
    if row.get("command") != TEST_COMMANDS[step_id]:
        raise CampaignBuildError(
            f"{step_id} test command differs from the declared command"
        )
    if type(row.get("exit_code")) is not int or row["exit_code"] != 0:
        raise CampaignBuildError(f"{step_id} tests did not pass")
    _private_file(row["transcript_path"], f"{step_id} historical test transcript")
    module = TEST_COMMANDS[step_id].split()[-1]
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", module],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().splitlines()[-5:]
        raise CampaignBuildError(f"{step_id} fresh tests failed: {' | '.join(detail)}")
    source = TEST_SOURCES[step_id]
    return {
        "id": f"test_{step_id.lower()}",
        "command": TEST_COMMANDS[step_id],
        "exit_code": 0,
        "source_path": str(source.relative_to(REPO)),
        "source_sha256": _sha256(source),
    }


def load_receipts(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    payload = _read_json(path)
    _exact_keys(payload, {"schema", "audits", "tests"}, "receipts")
    if payload.get("schema") != RECEIPT_SCHEMA:
        raise CampaignBuildError("unexpected execution-receipt schema")
    audits = _exact_keys(payload.get("audits"), set(GATES), "receipts.audits")
    tests = _exact_keys(payload.get("tests"), set(GATES), "receipts.tests")
    return {
        "audits": {step: _audit_receipt(step, audits[step]) for step in GATES},
        "tests": {step: _test_receipt(step, tests[step]) for step in GATES},
    }


def _artifact_receipt(step_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    path, schema = GATES[step_id]
    if payload.get("schema") != schema:
        raise CampaignBuildError(f"{step_id}: gate schema mismatch")
    return {
        "id": f"artifact_{step_id.lower()}",
        "path": str(path.relative_to(REPO)),
        "sha256": _sha256(path),
        "schema": schema,
    }


def _step_record(step_id: str, allowed_input_ids: list[str]) -> dict[str, Any]:
    statements = {
        "C1": (
            "A local five-dimensional U(1) derivative condensate is uniquely "
            "selected and remains regular, hyperbolic and coupled to matter.",
            "Enumerate the declared 5D operator basis and reduce its negative-X branch.",
            "Kill on any unfixed competing operator, singular deep limit, ghost, "
            "collapsing cutoff or underived matter vertex.",
        ),
        "C2": (
            "The frozen compact spectral sector generates a positive local "
            "nonlinear amplitude functional in the infrared.",
            "Derive the full source functional from the declared spectrum without "
            "using the target exponent.",
            "Kill the frozen model on a discrete gap plus analytic linear response "
            "and absence of a local nonlinear collective reduction.",
        ),
        "C3": (
            "The complete brane geometry forces a protected codimension-zero "
            "transition with one physical collective mode.",
            "Freeze the full variational problem and solve all branches for two "
            "conserved source geometries.",
            "Block rather than kill if the total action, constraints, sources, "
            "branch spectrum or free energies are not frozen.",
        ),
    }
    hypothesis, test, kill = statements[step_id]
    return {
        "declared_record_time_utc": DECLARED_RECORD_TIME_UTC,
        "hypothesis": hypothesis,
        "declared_test": test,
        "kill_gate": kill,
        "allowed_input_ids": allowed_input_ids,
        "target_blind": False,
        "target_disclosure": {
            "C1": "known_external_candidate",
            "C2": "known_acceptance_target",
            "C3": "known_mechanism_requirements",
        }[step_id],
        "no_tuning": True,
        "binary_kill_gate": True,
        "local_five_dimensional_action_required": True,
        "record_time_authentication": "content_addressed_not_timestamp_authenticated",
    }


def _step(
    step_id: str,
    status: str,
    check_statuses: Mapping[str, str],
    artifact: dict[str, Any],
    test: dict[str, Any],
    audit: dict[str, Any],
    allowed_inputs: list[str],
    reason: str,
) -> dict[str, Any]:
    step_record = _step_record(step_id, allowed_inputs)
    evidence_ids = [artifact["id"], test["id"]]
    expected = contract.REQUIRED_CHECK_IDS[step_id]
    if set(check_statuses) != set(expected):
        raise CampaignBuildError(f"{step_id}: incomplete campaign projection")
    ordinal, family = {
        "C1": (1, "derivative_condensate"),
        "C2": (2, "critical_continuum"),
        "C3": (3, "geometric_brane_transition"),
    }[step_id]
    return {
        "id": step_id,
        "ordinal": ordinal,
        "family": family,
        "status": status,
        "step_record": step_record,
        "step_record_sha256": contract.step_record_digest(step_record),
        "checks": [
            {
                "id": check_id,
                "status": check_statuses[check_id],
                "evidence_refs": list(evidence_ids),
            }
            for check_id in sorted(expected)
        ],
        "evidence": {
            "artifact_receipts": [artifact],
            "test_receipts": [test],
            "review_attempts": [audit],
        },
        "reason_codes": [reason],
    }


def build(receipt_path: Path = DEFAULT_RECEIPTS) -> dict[str, Any]:
    receipts = load_receipts(Path(receipt_path))
    gate_payloads = {step: _read_json(path) for step, (path, _schema) in GATES.items()}
    if gate_payloads["C1"].get("decision", {}).get("verdict") != "KILL_C1":
        raise CampaignBuildError("C1 did not trigger its declared kill gate")
    c2_decision = gate_payloads["C2"].get("decision", {})
    if not (
        c2_decision.get("verdict") == "KILL_C2"
        and c2_decision.get("kill_current_frozen_compact_spectrum") is True
        and c2_decision.get("kill_all_critical_continuum_models") is False
    ):
        raise CampaignBuildError("C2 scoped verdict is not certified")
    c3_decision = gate_payloads["C3"].get("decision", {})
    if not (
        c3_decision.get("status") == "BLOCKED_C3"
        and c3_decision.get("input_status") == "INPUT_INCOMPLETE"
        and c3_decision.get("kill_triggered") is False
    ):
        raise CampaignBuildError("C3 must remain blocked without a physical kill")

    input_rows = []
    for identifier, (path, role) in INPUTS.items():
        source = _read_json(path)
        input_rows.append(
            {
                "id": identifier,
                "path": str(path.relative_to(REPO)),
                "sha256": _sha256(path),
                "schema": source.get("schema"),
                "role": role,
                "integrity_verified": True,
                "observational": False,
            }
        )
    all_inputs = list(INPUTS)
    steps = [
        _step(
            "C1",
            "failed",
            {
                "five_dimensional_operator_basis_closed": "fail",
                "ward_or_isometry_fixes_homogeneity": "fail",
                "x_negative_branch_hyperbolic_without_patch": "fail",
                "background_and_junctions_preserved": "blocked",
            },
            _artifact_receipt("C1", gate_payloads["C1"]),
            receipts["tests"]["C1"],
            receipts["audits"]["C1"],
            [
                "effective_action",
                "interface_action",
                "adm_bps_flatness",
                "bps_biscalar_geometry",
            ],
            "binary_kill_gate_triggered",
        ),
        _step(
            "C2",
            "failed",
            {
                "nonlinear_generating_functional_derived": "fail",
                "positive_gapless_spectral_measure": "fail",
                "local_amplitude_reduction": "fail",
                "target_exponent_and_sign_emerge": "fail",
                "no_gapless_mode_integrated_out": "blocked",
            },
            _artifact_receipt("C2", gate_payloads["C2"]),
            receipts["tests"]["C2"],
            receipts["audits"]["C2"],
            [
                "collective_spectral_bridge",
                "compact_brane_s2",
                "finite_gamma_s2",
            ],
            "frozen_compact_spectrum_killed",
        ),
        _step(
            "C3",
            "blocked",
            {key: "blocked" for key in contract.REQUIRED_CHECK_IDS["C3"]},
            _artifact_receipt("C3", gate_payloads["C3"]),
            receipts["tests"]["C3"],
            receipts["audits"]["C3"],
            all_inputs,
            "input_contract_incomplete",
        ),
    ]
    result = {
        "schema": contract.SCHEMA_ID,
        "campaign_id": "minimal-mechanism-ladder-20260831",
        "declared_record_time_utc": DECLARED_RECORD_TIME_UTC,
        "repository": {
            "declared_baseline_commit": BASELINE_HEAD,
            "declared_worktree_dirty_at_start": True,
            "unrelated_changes_preserved": True,
            "remote_mutation_authorized": False,
            "publication_authorized": False,
        },
        "objective": {
            "statement": "Derive or falsify one local microscopic HOLO mechanism.",
            "scope": "theory_only",
            "target_blind": False,
            "requested_output": "adjudication_record_only",
        },
        "inputs": input_rows,
        "data_policy": {
            "observational_inputs_read": [],
            "provenance_audit_scope": "declared_repository_paths_only",
            "forbidden_inputs": [
                "observational_tables",
                "post_hoc_target_coefficients",
                "undeclared_external_outputs",
            ],
            "parameter_fitting_authorized": False,
            "post_hoc_target_matching_authorized": False,
            "external_physics_input_access_authorized": False,
            "review_channel_access_authorized": True,
            "physical_actions_authorized": False,
        },
        "ladder_policy": {
            "mode": "sequential",
            "step_count": 3,
            "unlock_requires_previous_failure": True,
        },
        "steps": steps,
        "claim_gate": {
            "mechanism_candidate": False,
            "physical_completion": False,
            "new_force_derived": False,
            "lensing_derived": False,
            "publication_authorized": False,
        },
        "verdict": {
            "status": "blocked",
            "selected_step": None,
            "reason_codes": ["c3_input_contract_incomplete"],
        },
    }
    contract.validate_campaign(result)
    return result


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    result = build(args.receipts)
    _write(args.output, result)
    print(f"[artifact] {args.output}")
    print("[ladder] C1=KILL C2=KILL_CURRENT C3=BLOCKED_INPUT_INCOMPLETE")
    print("[claim] mechanism_candidate=false physical_completion=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
