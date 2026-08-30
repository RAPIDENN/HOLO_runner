#!/usr/bin/env python3
"""Tests for the geometry-matched SPARC Yukawa certificate."""

from __future__ import annotations

import json
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

try:
    from first_principles_audit.prediction_factory import sparc_crossval as legacy
    from first_principles_audit.prediction_factory import sparc_physical_audit as audit
    from first_principles_audit.prediction_factory import derive_sparc_finite_disk_yukawa as disk
except ModuleNotFoundError:  # direct execution from this directory
    import sparc_crossval as legacy
    import sparc_physical_audit as audit
    import derive_sparc_finite_disk_yukawa as disk


HERE = Path(__file__).resolve().parent
ARTIFACT = HERE / "artifacts" / "sparc_finite_disk_yukawa.json"


class SparcFiniteDiskYukawaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.groups, _ = audit.load_groups(
            legacy.default_sparc_dir(),
            HERE / "sparc_split_v1.json",
            legacy.default_trace_path(),
        )
        force = json.loads(
            (HERE / "artifacts" / "stiff_boundary_force.json").read_text(
                encoding="utf-8"
            )
        )["spectrum_and_force"]
        cls.masses = np.asarray(force["masses_mu"])
        cls.strengths = np.asarray(force["alpha_uv_2_beta_squared"])

    def test_fftlog_round_trip_is_machine_precision(self) -> None:
        self.assertLess(
            self.report["baseline_scan"][
                "maximum_fractional_newtonian_identity_error"
            ],
            1.0e-12,
        )

    def test_long_scale_converges_to_exact_envelope(self) -> None:
        galaxy = self.groups["test"][0]
        curves, _ = disk.stiff_disk_velocity_curves(
            galaxy,
            np.asarray([1.0e12]),
            self.masses,
            self.strengths,
        )
        exact = audit.predict_p6_long_range_envelope(
            galaxy, float(np.sum(self.strengths))
        )
        np.testing.assert_allclose(curves[0], exact, rtol=3.0e-8, atol=2.0e-6)

    def test_forward_operator_does_not_read_observed_velocity(self) -> None:
        galaxy = self.groups["test"][0]
        altered = replace(galaxy, v_obs_kms=galaxy.v_obs_kms + 1.0e9)
        original, _ = disk.stiff_disk_velocity_curves(
            galaxy,
            np.asarray([0.1, 10.0, 1000.0]),
            self.masses,
            self.strengths,
        )
        changed, _ = disk.stiff_disk_velocity_curves(
            altered,
            np.asarray([0.1, 10.0, 1000.0]),
            self.masses,
            self.strengths,
        )
        np.testing.assert_array_equal(original, changed)

    def test_one_global_scale_runs_to_long_range_boundary(self) -> None:
        scan = self.report["baseline_scan"]
        self.assertEqual(scan["best_grid_index"], 80)
        self.assertEqual(scan["best_ell_kpc"], 100000.0)
        self.assertTrue(scan["best_at_upper_boundary"])
        self.assertTrue(scan["train_objective_nonincreasing_with_ell"])
        self.assertFalse(self.report["protocol"]["per_galaxy_force_parameters"])
        for sensitivity in self.report["sensitivity_scans"]:
            self.assertTrue(sensitivity["best_at_upper_boundary"])

    def test_frozen_scores_preserve_negative_result(self) -> None:
        metrics = self.report["metrics"]
        finite = metrics["finite_disk_at_train_selected_scale"]["test"]
        exact = metrics["exact_long_range_limit"]["test"]
        newton = metrics["newtonian"]["test"]
        self.assertAlmostEqual(finite["chi2_per_point"], 371.5790573727359)
        self.assertAlmostEqual(exact["chi2_per_point"], 371.5790515096818)
        self.assertAlmostEqual(newton["chi2_per_point"], 414.2292724496211)
        self.assertLess(finite["chi2_per_point"], newton["chi2_per_point"])
        self.assertGreater(finite["chi2_per_point"], 10.0)
        self.assertFalse(
            self.report["adjudication"]["disk_cancellation_rescues_stiff_candidate"]
        )

    def test_data_and_claim_boundaries_are_explicit(self) -> None:
        inventory = self.report["source_inventory"]
        self.assertEqual(inventory["local_catalogue_files"], 175)
        self.assertFalse(inventory["gas_surface_density_column_present"])
        self.assertFalse(inventory["vertical_density_profile_present"])
        self.assertFalse(
            self.report["adjudication"]["unique_physical_convolution_built"]
        )
        self.assertTrue(self.report["passes"]["all"])


if __name__ == "__main__":
    unittest.main()
