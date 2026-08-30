#!/usr/bin/env python3
"""Regression tests for the conditional space--time breathing response."""

from __future__ import annotations

import json
import math
import unittest

from first_principles_audit.prediction_factory.derive_breathing_response import (
    OUTPUT,
    build,
    physical_scale_from_first_mode,
    radial_response,
)


class BreathingResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_certificate_is_blind_and_fail_closed(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertEqual(self.result["historical_frequency_values_read"], [])
        self.assertIn("not_detection", self.result["classification"])
        self.assertIn("minimal superpotential", self.result["physical_closure_gates"]["boundary"])

    def test_static_limit_is_exact_stiff_kernel(self) -> None:
        self.assertLessEqual(
            self.result["static_recovery"]["maximum_absolute_error"], 1.0e-18
        )
        self.assertIn("stiff-boundary", self.result["static_recovery"]["force"])
        for mu in (0.9138989815720246, 1.54169473474637, 3.9544733937818783):
            for x in (0.0, 0.1, 1.0, 3.0):
                response = radial_response(mu, 0.0, x)
                expected = (1.0 + mu * x) * math.exp(-mu * x)
                self.assertEqual(response["regime"], "evanescent")
                self.assertAlmostEqual(response["force_factor"]["real"], expected, places=15)

    def test_threshold_transition_and_group_velocity(self) -> None:
        mu = 0.9138989815720246
        below = radial_response(mu, 0.9 * mu, 1.0)
        threshold = radial_response(mu, mu, 1.0)
        above = radial_response(mu, 1.1 * mu, 1.0)
        self.assertEqual(below["regime"], "evanescent")
        self.assertEqual(threshold["regime"], "threshold")
        self.assertEqual(above["regime"], "propagating")
        self.assertAlmostEqual(
            above["group_velocity_over_c"], math.sqrt(1.0 - 1.0 / 1.1**2), places=15
        )
        self.assertGreater(below["potential_factor"]["magnitude"], math.exp(-mu))

    def test_correlated_frequency_comb_and_times(self) -> None:
        clock = self.result["correlated_mode_clock"]
        ratios = [row["threshold_frequency_over_f1"] for row in clock["modes"]]
        self.assertAlmostEqual(ratios[0], 1.0, places=15)
        self.assertAlmostEqual(ratios[1], 4.2140266, places=6)
        self.assertTrue(all(right > left for left, right in zip(ratios[:-1], ratios[1:])))
        for row in clock["modes"]:
            self.assertAlmostEqual(
                row["period_over_T1"] * row["threshold_frequency_over_f1"],
                1.0,
                places=15,
            )
        self.assertGreater(
            clock["adjacent_resolution"]["minimum_first_zero_duration_over_T1"],
            0.0,
        )

    def test_frequency_anchor_has_correct_scaling_but_is_not_embedded(self) -> None:
        mu = self.result["correlated_mode_clock"]["modes"][0]["mu_n"]
        low = physical_scale_from_first_mode(1.0, mu)
        high = physical_scale_from_first_mode(10.0, mu)
        self.assertAlmostEqual(low["ell_m"] / high["ell_m"], 10.0, places=14)
        self.assertAlmostEqual(
            low["first_mode_static_range_m"] / high["first_mode_static_range_m"],
            10.0,
            places=14,
        )
        serialized = json.dumps(self.result, sort_keys=True).lower()
        self.assertNotIn("1.665", serialized)
        self.assertNotIn("2.159", serialized)

    def test_microscopic_boundary_update_is_not_mixed_with_old_residues(self) -> None:
        update = self.result["microscopic_boundary_update"]
        self.assertIn("rejected", update["minimal_superpotential_matching"]["result"])
        stiff = update["stiff_stabilized_candidate"]
        ratios = [
            row["threshold_frequency_over_f1"] for row in stiff["clock"]["modes"]
        ]
        self.assertAlmostEqual(ratios[0], 1.0, places=15)
        self.assertAlmostEqual(ratios[1], 4.2140266, places=6)
        self.assertTrue(stiff["absolute_force_residues_available"])
        self.assertEqual(len(stiff["force_residues_alpha"]), 7)
        self.assertAlmostEqual(stiff["sum_alpha_short_distance"], 0.10676507897978581)
        self.assertNotIn("historical", stiff["normalization_source"].split(";")[0])
        self.assertLess(
            stiff["independent_shooting_maximum_mass_relative_difference"],
            3.0e-4,
        )

    def test_rendered_artifact_matches_when_present(self) -> None:
        if OUTPUT.exists():
            self.assertEqual(
                json.loads(OUTPUT.read_text(encoding="utf-8")), self.result
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
