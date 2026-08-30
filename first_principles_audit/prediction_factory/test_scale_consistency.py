#!/usr/bin/env python3
"""Tests for the conditional QCD--galaxy one-scale no-go."""

from __future__ import annotations

import json
import math
import unittest

from first_principles_audit.prediction_factory.derive_scale_consistency import (
    OUTPUT,
    build,
    ell_from_mode_energy,
    physical_mode_from_ell,
)


class ScaleConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_scale_conversion_round_trip(self) -> None:
        mu = 0.29048164010701055
        energy = 1.6000061433743422e9
        ell = ell_from_mode_energy(mu, energy)
        recovered = physical_mode_from_ell(mu, ell)
        self.assertAlmostEqual(recovered["rest_energy_ev"], energy)
        self.assertAlmostEqual(
            recovered["cyclic_frequency_hz"] * recovered["period_s"], 1.0
        )

    def test_conditional_readings_are_incompatible(self) -> None:
        comparison = self.result["comparison"]
        self.assertFalse(comparison["single_ell_can_realize_both_identifications"])
        self.assertGreater(comparison["orders_of_magnitude_in_ell"], 40.0)
        self.assertAlmostEqual(
            comparison["ell_galaxy_over_ell_qcd"], 8.613249688650596e40
        )

    def test_galaxy_clock_is_reported_as_boundary_not_measurement(self) -> None:
        reading = self.result["conditional_galaxy_boundary_reading"]
        self.assertAlmostEqual(reading["cyclic_frequency_hz"], 4.491681748233456e-18)
        self.assertAlmostEqual(reading["period_julian_year"], 7054838163.120446)
        self.assertIn("not a measured", reading["status"])
        self.assertFalse(
            self.result["inputs"]["sparc_finite_disk"]["finite_scale_identified"]
        )

    def test_certificate_passes_without_promoting_either_anchor(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertIn("not a measurement", self.result["evidence_boundary"])
        self.assertIn("external endpoint conversion", self.result["inputs"]
                      ["legacy_qcd_proxy"]["status"])
        self.assertTrue(math.isfinite(self.result["comparison"]
                                     ["orders_of_magnitude_in_ell"]))

    def test_rendered_artifact_matches_when_present(self) -> None:
        if OUTPUT.exists():
            self.assertEqual(
                json.loads(OUTPUT.read_text(encoding="utf-8")), self.result
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
