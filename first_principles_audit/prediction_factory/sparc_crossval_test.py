#!/usr/bin/env python3
"""Tests for the retrospective SPARC P5 cross-validation report."""

from __future__ import annotations

import json
import math
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

try:
    from first_principles_audit.prediction_factory import sparc_crossval as crossval
except ModuleNotFoundError:  # direct execution from this directory
    import sparc_crossval as crossval


HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "sparc_crossval_report.json"
SPLIT_PATH = HERE / "sparc_split_v1.json"


class SparcCrossvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with REPORT_PATH.open("r", encoding="utf-8") as handle:
            cls.report = json.load(handle)
        cls.data_dir = crossval.default_sparc_dir()
        cls.trace_path = crossval.default_trace_path()
        cls.forward_artifact = crossval.default_forward_artifact_path()
        cls.groups = crossval.load_split(SPLIT_PATH)
        cls.trace_z, cls.trace_delta = crossval.load_trace(cls.trace_path)

    def test_report_is_explicitly_retrospective_not_confirmation(self) -> None:
        self.assertEqual(self.report["classification"], crossval.CLASSIFICATION)
        self.assertIn("not historically blind", self.report["claim_boundary"])
        self.assertIn("not independent confirmation", self.report["claim_boundary"])
        self.assertTrue(
            all(
                word not in self.report["classification"]
                for word in ("confirmed", "prospective")
            )
        )

    def test_dataset_hash_counts_and_split_cover_exactly(self) -> None:
        aggregate_hash, file_count = crossval.aggregate_dataset_sha256(self.data_dir)
        self.assertEqual(file_count, 175)
        self.assertEqual(
            aggregate_hash,
            "0a8cbe336032c4b2c65c8bc8b0f59f0768fb36e7db921b5a5dc85ff02c75b021",
        )
        self.assertEqual(aggregate_hash, self.report["provenance"]["dataset_aggregate_sha256"])
        files = {
            path.name.removesuffix("_rotmod.csv")
            for path in self.data_dir.glob("*_rotmod.csv")
        }
        split_names = {
            name for names in self.groups.values() for name in names
        }
        self.assertEqual(files, split_names)
        self.assertEqual(
            {group: len(names) for group, names in self.groups.items()},
            {"train": 122, "validation": 26, "test": 27},
        )

    def test_aggregate_data_diagnostics_are_frozen(self) -> None:
        diagnostics = crossval.audit_dataset(self.data_dir)
        self.assertEqual(diagnostics, self.report["data_diagnostics"])
        self.assertEqual(diagnostics["velocity_points"], 3391)
        self.assertEqual(diagnostics["negative_vgas_points"], 361)
        self.assertEqual(diagnostics["negative_vgas_galaxies"], 48)
        self.assertLess(
            diagnostics["vbar_vs_unsigned_component_quadrature_max_absdiff_kms"],
            5.1e-7,
        )

    def test_current_trace_backed_readout_is_reproduced_for_all_175(self) -> None:
        galaxies = crossval.load_galaxies(
            self.data_dir,
            [name for names in self.groups.values() for name in names],
            self.trace_z,
            self.trace_delta,
        )
        receipt = crossval.verify_current_forward_compatibility(
            galaxies, self.forward_artifact
        )
        self.assertEqual(receipt["galaxies_checked"], 175)
        self.assertTrue(receipt["exact_within_1e_8"])
        self.assertEqual(receipt, self.report["implementation_compatibility"])
        self.assertIn("older ed_p5_industrial.py", receipt["legacy_divergence_warning"])

    def test_forward_p5_curve_does_not_read_observed_velocity(self) -> None:
        galaxy = crossval.load_galaxies(
            self.data_dir,
            [self.groups["train"][0]],
            self.trace_z,
            self.trace_delta,
        )[0]
        params = crossval.P5Params(**self.report["frozen_fits"]["p5"]["parameters"])
        original = crossval.predict_p5(galaxy, params)
        altered = replace(galaxy, v_obs_kms=galaxy.v_obs_kms + 1.0e6)
        np.testing.assert_array_equal(original, crossval.predict_p5(altered, params))

    def test_fit_contract_uses_train_only_and_no_validation_selection(self) -> None:
        protocol = self.report["protocol"]
        self.assertEqual(protocol["fit_data"], "train only")
        self.assertIn("no hyperparameter or model selection", protocol["validation_use"])
        self.assertIn("no refit", protocol["test_use"])
        self.assertFalse(protocol["per_galaxy_tuning"])
        self.assertEqual(protocol["p5_fitted_parameters"], ["A", "n", "m", "gamma", "Sigma0"])
        self.assertEqual(protocol["rar_fitted_parameters"], ["g_dagger_m_s2"])

    def test_optimizer_nonconvergence_and_boundary_hits_are_not_hidden(self) -> None:
        p5 = self.report["frozen_fits"]["p5"]
        self.assertFalse(p5["optimizer"]["success"])
        self.assertEqual(p5["optimizer"]["nit"], 100)
        hits = {
            (item["parameter"], item["side"])
            for item in p5["parameters_at_preregistered_bounds"]
        }
        self.assertEqual(
            hits,
            {("A", "upper"), ("n", "lower"), ("m", "lower"), ("Sigma0", "lower")},
        )
        self.assertIn("not a certified optimum", p5["optimizer_warning"])

    def test_frozen_test_metrics_and_comparison_direction(self) -> None:
        test = self.report["results"]["test"]
        self.assertEqual(test["galaxies"], 27)
        self.assertEqual(test["velocity_points"], 621)
        self.assertAlmostEqual(test["models"]["p5"]["chi2_per_point"], 203.2561142826376)
        self.assertAlmostEqual(test["models"]["newton"]["chi2_per_point"], 254.2990052916549)
        self.assertAlmostEqual(test["models"]["rar"]["chi2_per_point"], 60.99045850206859)
        self.assertEqual(test["comparisons"]["p5_vs_newton"]["left_wins_galaxies"], 22)
        self.assertEqual(test["comparisons"]["p5_vs_rar"]["left_wins_galaxies"], 8)
        self.assertGreater(
            test["comparisons"]["p5_vs_newton"]["delta_loglike_per_point_left_minus_right"],
            0.0,
        )
        self.assertLess(
            test["comparisons"]["p5_vs_rar"]["delta_loglike_per_point_left_minus_right"],
            0.0,
        )

    def test_loglike_difference_matches_chi2_difference(self) -> None:
        test = self.report["results"]["test"]
        for comparison in ("p5_vs_newton", "p5_vs_rar", "rar_vs_newton"):
            values = test["comparisons"][comparison]
            self.assertAlmostEqual(
                values["delta_loglike_per_point_left_minus_right"],
                -0.5 * values["delta_chi2_per_point_left_minus_right"],
                places=12,
            )

    def test_bootstrap_is_galaxy_clustered_and_deterministic(self) -> None:
        params = crossval.P5Params(**self.report["frozen_fits"]["p5"]["parameters"])
        g_dagger = self.report["frozen_fits"]["rar"]["g_dagger_m_s2"]
        galaxies = crossval.load_galaxies(
            self.data_dir,
            self.groups["test"],
            self.trace_z,
            self.trace_delta,
        )
        rows = crossval.evaluate_galaxies(galaxies, params, g_dagger)
        first = crossval.bootstrap_test_rows(rows, replicates=200, seed=12345)
        second = crossval.bootstrap_test_rows(rows, replicates=200, seed=12345)
        self.assertEqual(first, second)
        self.assertIn("galaxy cluster", first["unit"])
        frozen = self.report["results"]["test_bootstrap"]["intervals"]
        self.assertLess(
            frozen["p5_minus_rar_delta_loglike_per_point"]["p97_5"], 0.0
        )
        self.assertLess(
            frozen["p5_minus_newton_delta_loglike_per_point"]["p2_5"], 0.0
        )
        self.assertGreater(
            frozen["p5_minus_newton_delta_loglike_per_point"]["p97_5"], 0.0
        )

    def test_report_has_no_absolute_paths_or_raw_curve_arrays(self) -> None:
        serialized = json.dumps(self.report, sort_keys=True)
        self.assertNotIn("/home/", serialized)
        self.assertFalse(crossval._contains_absolute_path(self.report))
        self.assertFalse(self.report["provenance"]["raw_data_copied_into_report"])
        self.assertNotIn("per_galaxy", self.report["results"])
        self.assertNotIn('"Vobs_kms":', serialized)

    def test_report_hash_receipts_match_current_inputs(self) -> None:
        provenance = self.report["provenance"]
        self.assertEqual(provenance["trace_sha256"], crossval.file_sha256(self.trace_path))
        self.assertEqual(provenance["split_sha256"], crossval.file_sha256(SPLIT_PATH))
        self.assertEqual(
            provenance["implementation_sha256"],
            crossval.file_sha256(Path(crossval.__file__).resolve()),
        )
        self.assertTrue(math.isfinite(self.report["frozen_fits"]["rar"]["g_dagger_m_s2"]))


if __name__ == "__main__":
    unittest.main()
