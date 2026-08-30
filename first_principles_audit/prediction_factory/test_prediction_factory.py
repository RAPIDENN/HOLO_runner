#!/usr/bin/env python3
"""Regression tests for the fail-closed prediction factory."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    from first_principles_audit.prediction_factory import prediction_factory as factory
except ModuleNotFoundError:  # direct execution from this directory
    import prediction_factory as factory


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]


class PredictionFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.documents = factory.build_documents(REPO_ROOT)
        cls.inventory = cls.documents["observational_inventory.json"]
        cls.split = cls.documents["sparc_split_v1.json"]
        cls.manifest = cls.documents["prediction_manifest.json"]

    def test_sparc_split_is_exact_disjoint_and_frozen(self) -> None:
        groups = self.split["groups"]
        self.assertEqual(self.split["counts"], {"train": 122, "validation": 26, "test": 27})
        train = set(groups["train"])
        validation = set(groups["validation"])
        test = set(groups["test"])
        self.assertFalse(train & validation)
        self.assertFalse(train & test)
        self.assertFalse(validation & test)
        self.assertEqual(len(train | validation | test), 175)
        self.assertEqual(
            self.split["assignment_sha256"],
            "aaf3e7c3b678b46a8b530f4aeaf17f1f2bf76be3e7e7f12ba3acbe180348ad07",
        )
        self.assertEqual(groups["train"][:3], ["UGC11914", "F574-1", "UGC05716"])
        self.assertEqual(groups["test"][:3], ["NGC4157", "IC2574", "NGC4068"])

    def test_split_does_not_relabel_exposed_sparc_as_confirmation(self) -> None:
        sparc = self.inventory["channels"]["sparc"]
        self.assertFalse(sparc["confirmatory_use_now"])
        self.assertFalse(sparc["point_level_rotation_curves_local"])
        self.assertIn("all 175", sparc["calibration_exposure"])
        self.assertEqual(
            self.split["confirmatory_status"],
            "development_only_due_to_prior_full_sample_exposure",
        )

    def test_clock_split_is_deterministic_and_session_level(self) -> None:
        examples = {
            "future-session-0": "calibration",
            "future-session-13": "validation",
            "future-session-1": "test",
        }
        for session_id, expected in examples.items():
            self.assertEqual(factory.deterministic_clock_session_bucket(session_id), expected)
            self.assertEqual(factory.deterministic_clock_session_bucket(session_id), expected)
        with self.assertRaises(ValueError):
            factory.deterministic_clock_session_bucket("   ")

    def test_boss_chi2_is_recomputed_but_historical_only(self) -> None:
        result = self.manifest["historical_audit_receipts"]["boss_dr12"]
        self.assertAlmostEqual(result["chi2_holo_recomputed"], 2.265809623608075, places=12)
        self.assertAlmostEqual(result["chi2_lcdm_recomputed"], 2.4429961128699653, places=12)
        prediction = self._prediction("boss_dr12_dictionary_growth_v1")
        self.assertEqual(prediction["status"], "historical_external_comparison_only")
        self.assertFalse(prediction["confirmatory_eligible_now"])

    def test_desi_local_vector_is_not_promoted_to_observation(self) -> None:
        desi = self.inventory["channels"]["desi"]
        self.assertFalse(desi["local_residual_is_observation"])
        self.assertFalse(desi["official_observed_vector_local"])
        self.assertFalse(desi["official_covariance_or_likelihood_local"])
        prediction = self._prediction("desi_high_redshift_growth_holdout_v1")
        self.assertIn("LOCAL_DESI_RESIDUAL_IS_MODEL_DERIVED", prediction["reason_codes"])
        signature = prediction["legacy_dictionary_signature"]
        self.assertAlmostEqual(signature["endpoint_z"], 1.0)
        self.assertAlmostEqual(signature["endpoint_delta_fsigma8_percent"], -12.386473033641826)
        self.assertIn("not a derived 4D prediction", signature["classification"])

    def test_redacted_nist_summary_is_fail_closed(self) -> None:
        nist = self.inventory["channels"]["nist_clocks"]
        summary = nist["historical_summary"]
        self.assertTrue(summary["observed_series_removed"])
        self.assertTrue(summary["residual_series_removed"])
        self.assertFalse(summary["raw_likelihood_recomputable_locally"])
        self.assertAlmostEqual(summary["pearson_r_reported"], -0.055375790994458114)
        self.assertGreater(summary["chi2_over_n_reported"], 20.0)

    def test_no_local_arm_is_marked_confirmatory(self) -> None:
        self.assertEqual(self.manifest["readiness"]["confirmatory_evaluable_locally_now"], [])
        for prediction in self.manifest["predictions"]:
            self.assertFalse(prediction["confirmatory_eligible_now"], prediction["id"])
            self.assertFalse(prediction["local_confirmatory_evaluation_available"], prediction["id"])

    def test_metrics_and_baselines_are_matched(self) -> None:
        common = self.manifest["metrics"]["common_rules"]
        self.assertTrue(any("same observations" in rule.lower() for rule in common))
        self.assertIn(
            "the historical velocity-weighted ranking loss",
            self.manifest["metrics"]["galaxy_rotation_curves"]["forbidden_primary_metric"],
        )
        galaxy_baselines = self.manifest["baselines"]["sparc_primary_zero_test_tuning"]
        self.assertEqual(
            {item["id"] for item in galaxy_baselines},
            {"baryons_only_newton", "canonical_rar_or_mond", "abundance_matched_cdm"},
        )

    def test_metric_only_clock_statement_remains_a_prospective_null(self) -> None:
        prediction = self._prediction("metric_only_tree_level_clock_null_v1")
        self.assertEqual(prediction["status"], "prospective_null_requires_new_data")
        self.assertIn("no direct classical Maxwell vertex", prediction["theory_statement"])
        self.assertFalse(prediction["local_descriptive_evaluation_available"])

    def test_generated_json_matches_fresh_build(self) -> None:
        for filename, expected in self.documents.items():
            with (HERE / filename).open("r", encoding="utf-8") as handle:
                committed = json.load(handle)
            self.assertEqual(committed, expected, filename)

    def _prediction(self, prediction_id: str) -> dict[str, object]:
        for prediction in self.manifest["predictions"]:
            if prediction["id"] == prediction_id:
                return prediction
        self.fail(f"missing prediction: {prediction_id}")


if __name__ == "__main__":
    unittest.main()
