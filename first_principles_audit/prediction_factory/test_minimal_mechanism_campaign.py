#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from first_principles_audit.prediction_factory import (
    derive_minimal_mechanism_campaign as ladder,
    validate_mechanism_campaign as contract,
)


class MinimalMechanismCampaignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        audits = {}
        tests = {}
        for index, step in enumerate(("C1", "C2", "C3"), 1):
            request_id = f"00000000-0000-4000-8000-{index:012d}"
            payload = self.root / f"{step.lower()}_payload.json"
            response = self.root / f"{step.lower()}_response.json"
            transcript = self.root / f"{step.lower()}_test.txt"
            payload.write_text(
                json.dumps(
                    {
                        "include_history": False,
                        "mode": "chat",
                        "model_fallback": "none",
                        "persist_history": False,
                        "request_id": request_id,
                        "source": "autonomous",
                        "speak": False,
                        "text": f"HOLO-{step}-BLIND-v1 sealed fixture",
                        "tool_policy": "none",
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            response.write_text(
                json.dumps(
                    {
                        "ok": False,
                        "error": "provider returned no model output",
                        "request_id": request_id,
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            transcript.write_text(f"{step}: tests passed\n", encoding="utf-8")
            audits[step] = {
                "payload_path": str(payload),
                "response_path": str(response),
                "verdict": "inconclusive",
            }
            tests[step] = {
                "command": ladder.TEST_COMMANDS[step],
                "exit_code": 0,
                "transcript_path": str(transcript),
            }
        self.receipts = self.root / "receipts.json"
        self.receipts.write_text(
            json.dumps(
                {"schema": ladder.RECEIPT_SCHEMA, "audits": audits, "tests": tests},
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_real_ladder_is_kill_kill_blocked_not_falsified(self) -> None:
        result = ladder.build(self.receipts)
        self.assertEqual(
            [step["status"] for step in result["steps"]],
            ["failed", "failed", "blocked"],
        )
        self.assertEqual(result["verdict"]["status"], "blocked")
        self.assertFalse(result["claim_gate"]["mechanism_candidate"])
        self.assertIs(contract.validate_campaign(result), result)

    def test_provider_errors_are_attempt_receipts_not_physics_evidence(self) -> None:
        result = ladder.build(self.receipts)
        for step in result["steps"]:
            review = step["evidence"]["review_attempts"][0]
            self.assertEqual(review["status"], "provider_error")
            self.assertEqual(review["verdict"], "inconclusive")
            self.assertFalse(review["literal_output_captured"])
            self.assertIsNone(review["literal_output_sha256"])
            for check in step["checks"]:
                self.assertNotIn(review["id"], check["evidence_refs"])

    def test_artifact_and_test_receipts_anchor_every_decision(self) -> None:
        result = ladder.build(self.receipts)
        for step in result["steps"]:
            artifact_id = step["evidence"]["artifact_receipts"][0]["id"]
            test_id = step["evidence"]["test_receipts"][0]["id"]
            self.assertTrue(
                all(
                    {artifact_id, test_id}.issubset(check["evidence_refs"])
                    for check in step["checks"]
                )
            )

    def test_c2_kill_is_scoped_and_c3_is_not_a_kill(self) -> None:
        result = ladder.build(self.receipts)
        self.assertEqual(
            result["steps"][1]["reason_codes"], ["frozen_compact_spectrum_killed"]
        )
        self.assertEqual(
            result["steps"][2]["reason_codes"], ["input_contract_incomplete"]
        )
        self.assertTrue(
            all(row["status"] == "blocked" for row in result["steps"][2]["checks"])
        )

    def test_target_exposure_and_record_time_limits_are_explicit(self) -> None:
        result = ladder.build(self.receipts)
        self.assertFalse(result["objective"]["target_blind"])
        self.assertEqual(
            [step["step_record"]["target_disclosure"] for step in result["steps"]],
            [
                "known_external_candidate",
                "known_acceptance_target",
                "known_mechanism_requirements",
            ],
        )
        self.assertTrue(
            all(not step["step_record"]["target_blind"] for step in result["steps"])
        )
        self.assertTrue(
            all(
                step["step_record"]["record_time_authentication"]
                == "content_addressed_not_timestamp_authenticated"
                for step in result["steps"]
            )
        )
        self.assertEqual(
            result["data_policy"]["provenance_audit_scope"],
            "declared_repository_paths_only",
        )

    def test_unsafe_skai_payload_fails_closed(self) -> None:
        receipt_doc = json.loads(self.receipts.read_text(encoding="utf-8"))
        payload_path = Path(receipt_doc["audits"]["C1"]["payload_path"])
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        payload["tool_policy"] = "auto"
        payload_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ladder.CampaignBuildError, "unsafe tool_policy"):
            ladder.build(self.receipts)

    def test_historical_exit_code_cannot_replace_a_fresh_test_run(self) -> None:
        failed = ladder.subprocess.CompletedProcess(
            args=["python3", "-m", "unittest"],
            returncode=1,
            stdout="",
            stderr="synthetic fresh failure",
        )
        with mock.patch.object(ladder.subprocess, "run", return_value=failed):
            with self.assertRaisesRegex(
                ladder.CampaignBuildError, "fresh tests failed"
            ):
                ladder.build(self.receipts)

    def test_generated_artifact_matches_when_private_receipts_exist(self) -> None:
        if not ladder.DEFAULT_RECEIPTS.exists() or not ladder.OUTPUT.exists():
            self.skipTest("private live receipts are intentionally not versioned")
        stored = json.loads(ladder.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, ladder.build(ladder.DEFAULT_RECEIPTS))

    def test_stored_repository_receipts_are_live_and_matching(self) -> None:
        if not ladder.OUTPUT.exists():
            self.skipTest("generated campaign artifact is absent")
        stored = contract.load_and_validate(
            ladder.OUTPUT,
            repository_root=ladder.REPO,
        )
        self.assertEqual(stored["verdict"]["status"], "blocked")

    def test_repository_verifier_binds_c3_status_to_its_gate_decision(self) -> None:
        result = ladder.build(self.receipts)
        c3 = result["steps"][2]
        c3["status"] = "failed"
        c3["checks"][0]["status"] = "fail"
        result["verdict"] = {
            "status": "falsified",
            "selected_step": None,
            "reason_codes": ["all_steps_failed"],
        }
        contract.validate_campaign(result)
        with self.assertRaisesRegex(
            contract.CampaignValidationError,
            "does not match bound C3 gate decision",
        ):
            contract.verify_repository_receipts(result, ladder.REPO)

    def test_repository_verifier_binds_check_projection_and_reason_codes(self) -> None:
        result = ladder.build(self.receipts)
        c2 = result["steps"][1]
        c2["checks"][0]["status"] = "pass"
        c2["reason_codes"] = ["contradictory_projection"]
        contract.validate_campaign(result)
        with self.assertRaises(contract.CampaignValidationError) as caught:
            contract.verify_repository_receipts(result, ladder.REPO)
        rendered = str(caught.exception)
        self.assertIn("checks: projection does not match", rendered)
        self.assertIn("reason_codes: projection does not match", rendered)

    def test_repository_verifier_rejects_an_unknown_declared_baseline(self) -> None:
        result = ladder.build(self.receipts)
        result["repository"]["declared_baseline_commit"] = "f" * 40
        contract.validate_campaign(result)
        with self.assertRaisesRegex(
            contract.CampaignValidationError,
            "declared commit is absent",
        ):
            contract.verify_repository_receipts(result, ladder.REPO)


if __name__ == "__main__":
    unittest.main(verbosity=2)
