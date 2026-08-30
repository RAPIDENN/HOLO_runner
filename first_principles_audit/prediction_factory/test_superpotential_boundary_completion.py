#!/usr/bin/env python3
"""Regression tests for the superpotential-matched boundary certificate."""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path
from typing import Any

from first_principles_audit.prediction_factory.derive_superpotential_boundary_completion import (
    OUTPUT,
    REPO,
    INPUT_RELATIVE,
    _background,
    build,
    solve_spectrum,
)


def _numbers(value: Any):
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        yield float(value)
    elif isinstance(value, dict):
        for child in value.values():
            yield from _numbers(child)
    elif isinstance(value, list):
        for child in value:
            yield from _numbers(child)


class SuperpotentialBoundaryCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()
        cls.input_payload = json.loads(
            (REPO / INPUT_RELATIVE).read_text(encoding="utf-8")
        )
        cls.arrays = _background(cls.input_payload)

    def test_certificate_is_blind_finite_and_fail_closed(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertTrue(all(self.result["passes"].values()))
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertFalse(Path(self.result["input"]["path"]).is_absolute())
        self.assertTrue(all(math.isfinite(value) for value in _numbers(self.result)))

    def test_minimal_superpotential_matching_has_zero_mode_obstruction(self) -> None:
        minimal = self.result["minimal_superpotential_matching"]
        self.assertEqual(minimal["g_minus_over_a"], 0.0)
        self.assertEqual(minimal["g_plus_over_a"], 0.0)
        self.assertIn("massless", minimal["theorem_result"])
        self.assertIn("not P6/P7", minimal["adjudication"])
        self.assertIn("not uniquely selected", minimal["status"])

    def test_positive_curvatures_have_stability_signs(self) -> None:
        family = self.result["stabilized_family"]
        self.assertEqual(family["g_minus_over_a"], "gamma_-")
        self.assertEqual(family["g_plus_over_a"], "-gamma_+")
        self.assertTrue(family["background_unchanged"])
        self.assertIn("neither", family["identifiability_result"])

    def test_stiff_candidate_spectrum_and_ratios(self) -> None:
        spectrum = self.result["stiff_candidate"]["spectrum"]
        masses = spectrum["masses_mu"]
        self.assertAlmostEqual(masses[0], 0.2905023, places=6)
        self.assertTrue(all(right > left for left, right in zip(masses, masses[1:])))
        for mass, ratio in zip(masses, spectrum["mass_ratios_to_first"]):
            self.assertAlmostEqual(ratio, mass / masses[0], places=13)
        self.assertLessEqual(
            spectrum["normwise_backward_error_max"], 1.0e-12
        )

    def test_grid_convergence(self) -> None:
        numerics = self.result["numerics"]
        for section in ("stiff_convergence", "gamma_one_convergence"):
            convergence = numerics[section]
            self.assertLessEqual(
                convergence["half_grid"]["maximum_relative"],
                numerics["mass_half_grid_relative_max"],
            )
            self.assertLessEqual(
                convergence["quarter_grid"]["maximum_relative"],
                numerics["mass_quarter_grid_relative_max"],
            )

    def test_zero_or_negative_finite_curvature_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_spectrum(self.arrays, 0.0, 1.0)
        with self.assertRaises(ValueError):
            solve_spectrum(self.arrays, 1.0, -1.0)

    def test_uncertified_background_is_rejected(self) -> None:
        payload = dict(self.input_payload)
        payload["summary"] = dict(payload["summary"])
        payload["summary"]["passes"] = dict(payload["summary"]["passes"])
        payload["summary"]["passes"]["all"] = False
        with self.assertRaises(RuntimeError):
            _background(payload)

    def test_rendered_artifact_matches_when_present(self) -> None:
        if OUTPUT.exists():
            self.assertEqual(
                json.loads(OUTPUT.read_text(encoding="utf-8")), self.result
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
