#!/usr/bin/env python3
"""Tests for the repaired SPARC baryonic-input audit."""

from __future__ import annotations

import json
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

try:
    from first_principles_audit.prediction_factory import sparc_crossval as legacy
    from first_principles_audit.prediction_factory import sparc_physical_audit as audit
except ModuleNotFoundError:  # direct execution from this directory
    import sparc_crossval as legacy
    import sparc_physical_audit as audit


HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "sparc_physical_audit.json"
SPLIT_PATH = HERE / "sparc_split_v1.json"


class SparcPhysicalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.groups, cls.split = audit.load_groups(
            legacy.default_sparc_dir(), SPLIT_PATH, legacy.default_trace_path()
        )

    def test_signed_gas_and_stellar_mass_to_light_contract(self) -> None:
        gas = np.asarray([-3.0, 4.0])
        disk = np.asarray([10.0, 10.0])
        bulge = np.asarray([2.0, 2.0])
        actual = audit.physical_vbar_squared(gas, disk, bulge)
        expected = gas * np.abs(gas) + 0.5 * disk**2 + 0.7 * bulge**2
        np.testing.assert_array_equal(actual, expected)
        self.assertLess(actual[0], actual[1])

    def test_every_catalogue_velocity_point_was_recomputed(self) -> None:
        contract = self.report["baryonic_contract"]
        self.assertEqual(contract["velocity_points_total"], 3391)
        self.assertEqual(contract["velocity_points_changed_from_legacy_vbar"], 3391)
        self.assertEqual(contract["disk_mass_to_light_msun_per_lsun_3p6um"], 0.5)
        self.assertEqual(contract["bulge_mass_to_light_msun_per_lsun_3p6um"], 0.7)
        self.assertIn("Vgas*abs(Vgas)", contract["formula"])

    def test_standard_rar_is_exact_q_half_member(self) -> None:
        g_dagger = self.report["frozen_train_fits"]["rar"]["g_dagger_m_s2"]
        for galaxy in self.groups["test"]:
            np.testing.assert_allclose(
                audit.predict_generalized_rar(galaxy, g_dagger, 0.5),
                legacy.predict_rar(galaxy, g_dagger),
                rtol=2e-14,
                atol=2e-12,
            )

    def test_forward_curves_do_not_read_vobs(self) -> None:
        galaxy = self.groups["test"][0]
        altered = replace(galaxy, v_obs_kms=galaxy.v_obs_kms + 1.0e6)
        fits = self.report["frozen_train_fits"]
        p5 = legacy.P5Params(**fits["legacy_p5_on_repaired_inputs"]["parameters"])
        g_dagger = fits["rar"]["g_dagger_m_s2"]
        p6_alpha = fits["p6_corrected_long_range_convolution_envelope"][
            "sum_positive_alpha_n"
        ]
        stiff_alpha = fits["stiff_boundary_long_range_convolution_envelope"][
            "sum_positive_alpha_n"
        ]
        np.testing.assert_array_equal(
            legacy.predict_p5(galaxy, p5), legacy.predict_p5(altered, p5)
        )
        np.testing.assert_array_equal(
            legacy.predict_rar(galaxy, g_dagger),
            legacy.predict_rar(altered, g_dagger),
        )
        np.testing.assert_array_equal(
            audit.predict_p6_long_range_envelope(galaxy, p6_alpha),
            audit.predict_p6_long_range_envelope(altered, p6_alpha),
        )
        np.testing.assert_array_equal(
            audit.predict_p6_long_range_envelope(galaxy, stiff_alpha),
            audit.predict_p6_long_range_envelope(altered, stiff_alpha),
        )

    def test_fit_and_curve_selection_contracts_are_explicit(self) -> None:
        protocol = self.report["protocol"]
        self.assertEqual(protocol["fit_data"], "train only")
        self.assertEqual(protocol["validation_and_test_use"], "reported without refitting")
        self.assertFalse(protocol["per_galaxy_parameters"])
        self.assertIn("no outcome-based selection", protocol["test_curve_selection_rule"])
        self.assertEqual(protocol["test_curve_ids"], self.split["test"][:4])

    def test_repaired_test_metrics_are_frozen(self) -> None:
        models = self.report["results"]["test"]["models"]
        self.assertAlmostEqual(models["rar"]["chi2_per_point"], 36.747991080566734)
        self.assertAlmostEqual(models["legacy_p5_refit"]["chi2_per_point"], 290.98021691425674)
        self.assertAlmostEqual(models["newton"]["chi2_per_point"], 414.2292724496211)
        self.assertAlmostEqual(
            models["p6_corrected_long_range_envelope"]["chi2_per_point"],
            414.1983107105997,
        )
        self.assertAlmostEqual(
            models["stiff_boundary_long_range_envelope"]["chi2_per_point"],
            371.5790515096818,
        )
        self.assertAlmostEqual(
            models["rar"]["median_absolute_fractional_velocity_error"],
            0.144582962137798,
        )
        self.assertLess(models["rar"]["chi2_per_point"], models["legacy_p5_refit"]["chi2_per_point"])

    def test_p6_is_corrected_observation_free_long_range_convolution(self) -> None:
        p6 = self.report["frozen_train_fits"][
            "p6_corrected_long_range_convolution_envelope"
        ]
        self.assertEqual(p6["positive_mode_count"], 6)
        self.assertEqual(p6["observational_inputs_read"], [])
        self.assertFalse(p6["finite_ell_parameters_fitted"])
        self.assertAlmostEqual(p6["sum_positive_alpha_n"], 7.202299861734871e-5)
        self.assertAlmostEqual(
            p6["maximum_fractional_velocity_boost"], 3.601085091786693e-5
        )
        self.assertEqual(
            p6["limit"], "ell_to_infinity_exact_extended_source_convolution"
        )

    def test_extra_shape_returns_to_rar_and_is_not_promoted(self) -> None:
        fit = self.report["frozen_train_fits"]["generalized_rar_diagnostic"]
        adjudication = self.report["adjudication"]
        self.assertAlmostEqual(fit["shape_q"], 0.5, delta=0.02)
        self.assertTrue(adjudication["generalized_shape_returns_to_standard_rar"])
        self.assertFalse(adjudication["generalized_rar_selected"])
        self.assertLess(adjudication["generalized_test_relative_chi2_gain"], 0.01)

    def test_stiff_force_replaces_p5_without_overclaiming_detection(self) -> None:
        adjudication = self.report["adjudication"]
        self.assertFalse(adjudication["legacy_p5_accepted"])
        self.assertFalse(adjudication["legacy_p5_represents_corrected_completion"])
        self.assertTrue(adjudication["p6_current_curve_replaces_legacy_p5"])
        self.assertEqual(
            adjudication["p6_corrected_benchmark_status"],
            "evaluated_exact_long_range_convolution_envelope",
        )
        self.assertEqual(
            adjudication["holo_acceleration_law_status"],
            "action_derived_stiff_force_available_but_empirically_insufficient",
        )
        self.assertEqual(
            adjudication["corrected_completion_test_status"],
            "stiff_force_and_effective_disk_scan_complete_no_finite_scale",
        )
        self.assertIn("do not label RAR", adjudication["paper_action"])
        self.assertIn("retain legacy P5 only as numerical provenance", adjudication["paper_action"])
        self.assertTrue(self.report["passes"]["all"])

    def test_finite_disk_followup_runs_to_long_range_boundary(self) -> None:
        followup = self.report["finite_disk_followup"]
        self.assertEqual(followup["best_global_ell_kpc"], 100000.0)
        self.assertTrue(followup["best_at_upper_scan_boundary"])
        self.assertFalse(followup["finite_scale_identified"])
        self.assertFalse(followup["disk_cancellation_rescues_stiff_candidate"])
        self.assertFalse(followup["unique_physical_convolution_built"])
        self.assertAlmostEqual(followup["test_chi2_per_point"], 371.5790573727359)

    def test_report_is_portable_and_contains_no_curve_arrays(self) -> None:
        serialized = json.dumps(self.report, sort_keys=True)
        self.assertFalse(legacy._contains_absolute_path(self.report))
        self.assertNotIn("/home/", serialized)
        self.assertFalse(self.report["provenance"]["raw_curve_arrays_serialized"])
        self.assertNotIn('"Vobs_kms"', serialized)


if __name__ == "__main__":
    unittest.main()
