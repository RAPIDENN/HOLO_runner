#!/usr/bin/env python3
"""Regression tests for the fail-closed mechanism-campaign contract."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from first_principles_audit.prediction_factory import (
    validate_mechanism_campaign as campaign,
)

CHECKS = campaign.REQUIRED_CHECK_IDS


def _step_record(step_id: str) -> dict[str, object]:
    return {
        "declared_record_time_utc": "2026-08-31T18:00:00Z",
        "hypothesis": f"{step_id} has a local target-independent realization.",
        "declared_test": (
            f"Derive every {step_id} coefficient from the declared theory inputs."
        ),
        "kill_gate": f"Fail {step_id} on the first unmet required check.",
        "allowed_input_ids": ["effective_action", "bps_geometry"],
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
    ordinal: int,
    family: str,
    status: str,
) -> dict[str, object]:
    step_record = _step_record(step_id)
    return {
        "id": step_id,
        "ordinal": ordinal,
        "family": family,
        "status": status,
        "step_record": step_record,
        "step_record_sha256": campaign.step_record_digest(step_record),
        "checks": [
            {"id": check_id, "status": "pending", "evidence_refs": []}
            for check_id in sorted(CHECKS[step_id])
        ],
        "evidence": {
            "artifact_receipts": [],
            "test_receipts": [],
            "review_attempts": [],
        },
        "reason_codes": [
            "awaiting_execution" if status == "ready" else "previous_step_not_failed"
        ],
    }


def valid_initial_campaign() -> dict[str, object]:
    return {
        "schema": campaign.SCHEMA_ID,
        "campaign_id": "mechanism-ladder-001",
        "declared_record_time_utc": "2026-08-31T18:00:00Z",
        "repository": {
            "declared_baseline_commit": "1" * 40,
            "declared_worktree_dirty_at_start": True,
            "unrelated_changes_preserved": True,
            "remote_mutation_authorized": False,
            "publication_authorized": False,
        },
        "objective": {
            "statement": "Derive or falsify one local microscopic mechanism.",
            "scope": "theory_only",
            "target_blind": False,
            "requested_output": "adjudication_record_only",
        },
        "inputs": [
            {
                "id": "effective_action",
                "path": "first_principles_audit/artifacts/holo_effective_action.json",
                "sha256": "a" * 64,
                "schema": "holo.effective-action.v1",
                "role": "theory",
                "integrity_verified": True,
                "observational": False,
            },
            {
                "id": "bps_geometry",
                "path": "first_principles_audit/artifacts/holo_bps_geometry.json",
                "sha256": "b" * 64,
                "schema": "holo.bps-geometry.v1",
                "role": "geometry",
                "integrity_verified": True,
                "observational": False,
            },
        ],
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
        "steps": [
            _step("C1", 1, "derivative_condensate", "ready"),
            _step("C2", 2, "critical_continuum", "locked"),
            _step("C3", 3, "geometric_brane_transition", "locked"),
        ],
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
            "reason_codes": ["c1_not_decided"],
        },
    }


def _complete(
    step: dict[str, object],
    verdict: str,
    *,
    review_verdict: str | None = None,
    review_status: str = "completed",
) -> None:
    step_code = str(step["id"])
    step_id = step_code.lower()
    binding = campaign.EXPECTED_RECEIPT_BINDINGS[step_code]
    receipt_ids = [
        binding["artifact_id"],
        binding["test_id"],
        binding["review_id"],
    ]
    step["status"] = {
        "pass": "passed",
        "fail": "failed",
        "blocked": "blocked",
    }[verdict]
    decision_receipts = receipt_ids[:2]
    checks = step["checks"]
    assert isinstance(checks, list)
    if verdict == "pass":
        for check in checks:
            check["status"] = "pass"
            check["evidence_refs"] = list(decision_receipts)
    else:
        checks[0]["status"] = verdict
        checks[0]["evidence_refs"] = list(decision_receipts)
    step["evidence"] = {
        "artifact_receipts": [
            {
                "id": receipt_ids[0],
                "path": binding["artifact_path"],
                "sha256": "c" * 64,
                "schema": binding["artifact_schema"],
            }
        ],
        "test_receipts": [
            {
                "id": receipt_ids[1],
                "command": binding["test_command"],
                "exit_code": 0,
                "source_path": binding["test_source_path"],
                "source_sha256": "d" * 64,
            }
        ],
        "review_attempts": [
            {
                "id": receipt_ids[2],
                "channel": "skai_chat",
                "status": review_status,
                "context_sha256": "e" * 64,
                "response_sha256": "f" * 64,
                "literal_output_sha256": (
                    "a" * 64 if review_status == "completed" else None
                ),
                "literal_output_captured": review_status == "completed",
                "independent_from_builder": review_status == "completed",
                "verdict": (
                    "inconclusive"
                    if review_status == "provider_error"
                    else review_verdict
                    or (verdict if verdict in {"pass", "fail"} else "inconclusive")
                ),
            }
        ],
    }
    step["reason_codes"] = [
        (
            "all_declared_checks_passed"
            if verdict == "pass"
            else (
                "binary_kill_gate_triggered"
                if verdict == "fail"
                else "input_contract_incomplete"
            )
        )
    ]


def _unlock(step: dict[str, object]) -> None:
    step["status"] = "ready"
    step["reason_codes"] = ["previous_step_failed"]


class MechanismCampaignContractTests(unittest.TestCase):
    def test_initial_three_step_contract_is_valid_and_blocked(self) -> None:
        payload = valid_initial_campaign()
        self.assertIs(campaign.validate_campaign(payload), payload)
        self.assertEqual([row["id"] for row in payload["steps"]], ["C1", "C2", "C3"])
        self.assertEqual(payload["verdict"]["status"], "blocked")
        self.assertFalse(payload["claim_gate"]["mechanism_candidate"])

    def test_schema_document_has_the_same_identity_and_ladder_size(self) -> None:
        schema = json.loads(campaign.SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema"
        )
        self.assertEqual(schema["properties"]["schema"]["const"], campaign.SCHEMA_ID)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["steps"]["minItems"], 3)
        self.assertEqual(schema["properties"]["steps"]["maxItems"], 3)

    def test_unknown_fields_and_wrong_schema_fail_closed(self) -> None:
        payload = valid_initial_campaign()
        payload["unexpected"] = True
        with self.assertRaisesRegex(campaign.CampaignValidationError, "unknown keys"):
            campaign.validate_campaign(payload)

        payload = valid_initial_campaign()
        payload["schema"] = "holo.mechanism-campaign.v2"
        with self.assertRaisesRegex(
            campaign.CampaignValidationError, "campaign.schema"
        ):
            campaign.validate_campaign(payload)

    def test_step_record_mutation_breaks_its_digest(self) -> None:
        payload = valid_initial_campaign()
        payload["steps"][0]["step_record"]["kill_gate"] = "A changed gate."
        with self.assertRaisesRegex(
            campaign.CampaignValidationError, "digest does not match"
        ):
            campaign.validate_campaign(payload)

    def test_v1_rejects_unauthenticated_target_blind_claims(self) -> None:
        payload = valid_initial_campaign()
        step_record = payload["steps"][0]["step_record"]
        step_record["target_blind"] = True
        payload["steps"][0]["step_record_sha256"] = campaign.step_record_digest(
            step_record
        )
        payload["objective"]["target_blind"] = True
        with self.assertRaisesRegex(
            campaign.CampaignValidationError,
            "target_blind: must be False",
        ):
            campaign.validate_campaign(payload)

    def test_target_aware_step_requires_a_recognized_disclosure_class(self) -> None:
        payload = valid_initial_campaign()
        step_record = payload["steps"][0]["step_record"]
        step_record["target_disclosure"] = "none"
        payload["steps"][0]["step_record_sha256"] = campaign.step_record_digest(
            step_record
        )
        with self.assertRaisesRegex(
            campaign.CampaignValidationError,
            "target_disclosure: expected one of",
        ):
            campaign.validate_campaign(payload)

    def test_observational_input_or_post_hoc_authority_is_rejected(self) -> None:
        payload = valid_initial_campaign()
        payload["inputs"][0]["path"] = "observational/sparc_table.csv"
        payload["data_policy"]["parameter_fitting_authorized"] = True
        with self.assertRaises(campaign.CampaignValidationError) as caught:
            campaign.validate_campaign(payload)
        rendered = str(caught.exception)
        self.assertIn("observational marker", rendered)
        self.assertIn("parameter_fitting_authorized", rendered)

    def test_observational_markers_are_path_tokens_not_substrings(self) -> None:
        payload = valid_initial_campaign()
        payload["inputs"][0][
            "path"
        ] = "first_principles_audit/artifacts/design_certificate.json"
        campaign.validate_campaign(payload)

        payload["inputs"][0]["path"] = "first_principles_audit/artifacts/desi_dr1.json"
        with self.assertRaisesRegex(
            campaign.CampaignValidationError,
            "observational marker",
        ):
            campaign.validate_campaign(payload)

    def test_later_steps_cannot_unlock_early(self) -> None:
        payload = valid_initial_campaign()
        _unlock(payload["steps"][1])
        with self.assertRaisesRegex(
            campaign.CampaignValidationError,
            "stay locked until C1 explicitly fails",
        ):
            campaign.validate_campaign(payload)

    def test_c1_failure_atomically_unlocks_c2(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _unlock(payload["steps"][1])
        campaign.validate_campaign(payload)

        payload["steps"][1]["status"] = "locked"
        payload["steps"][1]["reason_codes"] = ["previous_step_not_failed"]
        with self.assertRaisesRegex(
            campaign.CampaignValidationError,
            "C1 failure must unlock C2",
        ):
            campaign.validate_campaign(payload)

    def test_completed_review_requires_literal_independent_output(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _unlock(payload["steps"][1])
        review = payload["steps"][0]["evidence"]["review_attempts"][0]
        review["literal_output_captured"] = False
        review["independent_from_builder"] = False
        with self.assertRaises(campaign.CampaignValidationError) as caught:
            campaign.validate_campaign(payload)
        rendered = str(caught.exception)
        self.assertIn("literal_output_captured", rendered)
        self.assertIn("independent_from_builder", rendered)

    def test_decided_step_requires_all_evidence_classes(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _unlock(payload["steps"][1])
        payload["steps"][0]["evidence"]["test_receipts"] = []
        with self.assertRaises(campaign.CampaignValidationError) as caught:
            campaign.validate_campaign(payload)
        rendered = str(caught.exception)
        self.assertIn("artifact, test and review", rendered)
        self.assertIn("require a test receipt", rendered)

    def test_v1_cannot_promote_a_candidate_or_physical_claim(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "pass")
        payload["claim_gate"]["mechanism_candidate"] = True
        payload["verdict"] = {
            "status": "candidate",
            "selected_step": "C1",
            "reason_codes": ["c1_passed"],
        }
        payload["claim_gate"]["new_force_derived"] = True
        with self.assertRaises(campaign.CampaignValidationError) as caught:
            campaign.validate_campaign(payload)
        rendered = str(caught.exception)
        self.assertIn("campaign.steps[0].status", rendered)
        self.assertIn("mechanism_candidate", rendered)
        self.assertIn("new_force_derived", rendered)
        self.assertIn("campaign.verdict.status", rendered)
        self.assertIn("selected_step", rendered)

    def test_review_cannot_rescue_a_failed_gate_or_be_physics_evidence(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail", review_verdict="pass")
        _unlock(payload["steps"][1])
        campaign.validate_campaign(payload)
        review_id = payload["steps"][0]["evidence"]["review_attempts"][0]["id"]
        self.assertTrue(
            all(
                review_id not in check["evidence_refs"]
                for check in payload["steps"][0]["checks"]
            )
        )

    def test_no_private_review_can_authorize_a_positive_candidate(self) -> None:
        for review_status, review_verdict in (
            ("completed", "pass"),
            ("completed", "fail"),
            ("provider_error", None),
        ):
            with self.subTest(status=review_status, verdict=review_verdict):
                payload = valid_initial_campaign()
                _complete(
                    payload["steps"][0],
                    "pass",
                    review_status=review_status,
                    review_verdict=review_verdict,
                )
                payload["claim_gate"]["mechanism_candidate"] = True
                payload["verdict"] = {
                    "status": "candidate",
                    "selected_step": "C1",
                    "reason_codes": ["private_review_cannot_promote_v1"],
                }
                with self.assertRaises(campaign.CampaignValidationError):
                    campaign.validate_campaign(payload)

    def test_provider_failure_is_recorded_but_never_used_as_physics_evidence(
        self,
    ) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail", review_status="provider_error")
        _unlock(payload["steps"][1])
        campaign.validate_campaign(payload)
        review = payload["steps"][0]["evidence"]["review_attempts"][0]
        self.assertEqual(review["status"], "provider_error")
        self.assertEqual(review["verdict"], "inconclusive")
        self.assertFalse(review["literal_output_captured"])
        self.assertIsNone(review["literal_output_sha256"])
        for check in payload["steps"][0]["checks"]:
            self.assertNotIn("skai_c1_review_attempt", check["evidence_refs"])

    def test_malformed_review_fails_closed_without_internal_exception(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _unlock(payload["steps"][1])
        payload["steps"][0]["evidence"]["review_attempts"][0] = "not-an-object"
        with self.assertRaisesRegex(
            campaign.CampaignValidationError,
            r"review_attempts\[0\]: expected object",
        ):
            campaign.validate_campaign(payload)

    def test_decided_check_requires_reproducible_artifact_and_test(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _unlock(payload["steps"][1])
        check = payload["steps"][0]["checks"][0]
        check["evidence_refs"] = ["skai_c1_review_attempt"]
        with self.assertRaises(campaign.CampaignValidationError) as caught:
            campaign.validate_campaign(payload)
        rendered = str(caught.exception)
        self.assertIn("require an artifact receipt", rendered)
        self.assertIn("require a test receipt", rendered)
        self.assertIn("advisory non-evidence", rendered)

    def test_step_receipts_are_bound_to_the_declared_gate_and_test(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _unlock(payload["steps"][1])
        artifact = payload["steps"][0]["evidence"]["artifact_receipts"][0]
        artifact["path"] = campaign.EXPECTED_RECEIPT_BINDINGS["C2"]["artifact_path"]
        test = payload["steps"][0]["evidence"]["test_receipts"][0]
        test["command"] = campaign.EXPECTED_RECEIPT_BINDINGS["C2"]["test_command"]
        with self.assertRaises(campaign.CampaignValidationError) as caught:
            campaign.validate_campaign(payload)
        rendered = str(caught.exception)
        self.assertIn("artifact_receipts[0].path", rendered)
        self.assertIn("test_receipts[0].command", rendered)

    def test_blocked_step_records_input_incompleteness_without_falsifying(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _complete(payload["steps"][1], "fail")
        _complete(payload["steps"][2], "blocked")
        payload["verdict"] = {
            "status": "blocked",
            "selected_step": None,
            "reason_codes": ["c3_input_contract_incomplete"],
        }
        campaign.validate_campaign(payload)
        self.assertFalse(payload["claim_gate"]["mechanism_candidate"])

    def test_second_step_pass_is_also_non_promotable_in_v1(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _complete(payload["steps"][1], "pass")
        payload["claim_gate"]["mechanism_candidate"] = True
        payload["verdict"] = {
            "status": "candidate",
            "selected_step": "C2",
            "reason_codes": ["c2_passed"],
        }
        with self.assertRaises(campaign.CampaignValidationError):
            campaign.validate_campaign(payload)

    def test_all_three_explicit_failures_are_a_falsified_campaign(self) -> None:
        payload = valid_initial_campaign()
        for step in payload["steps"]:
            _complete(step, "fail")
        payload["verdict"] = {
            "status": "falsified",
            "selected_step": None,
            "reason_codes": ["all_steps_failed"],
        }
        campaign.validate_campaign(payload)

    def test_missing_or_unreferenced_receipts_fail_closed(self) -> None:
        payload = valid_initial_campaign()
        _complete(payload["steps"][0], "fail")
        _unlock(payload["steps"][1])
        payload["steps"][0]["checks"][0]["evidence_refs"] = ["unknown_receipt"]
        with self.assertRaises(campaign.CampaignValidationError) as caught:
            campaign.validate_campaign(payload)
        rendered = str(caught.exception)
        self.assertIn("unknown receipts", rendered)
        self.assertIn("unreferenced receipts", rendered)

    def test_loader_rejects_duplicate_json_keys_and_cli_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            duplicate = Path(temporary) / "duplicate.json"
            duplicate.write_text(
                '{"schema":"holo.mechanism-campaign.v1",'
                '"schema":"holo.mechanism-campaign.v1"}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                campaign.CampaignValidationError, "duplicate JSON key"
            ):
                campaign.load_and_validate(duplicate)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = campaign.main([str(duplicate)])
            self.assertEqual(status, 2)
            self.assertIn("INVALID", stderr.getvalue())

    def test_repository_receipts_require_real_matching_files(self) -> None:
        payload = valid_initial_campaign()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, receipt in enumerate(payload["inputs"]):
                path = root / receipt["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                content = f"input-{index}\n".encode()
                path.write_bytes(content)
                receipt["sha256"] = hashlib.sha256(content).hexdigest()
            campaign.validate_campaign(payload)
            self.assertIs(
                campaign.verify_repository_receipts(payload, root),
                payload,
            )

            first = root / payload["inputs"][0]["path"]
            first.write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(
                campaign.CampaignValidationError,
                "repository receipt mismatch",
            ):
                campaign.verify_repository_receipts(payload, root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
