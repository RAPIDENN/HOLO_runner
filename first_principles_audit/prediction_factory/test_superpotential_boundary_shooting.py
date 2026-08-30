#!/usr/bin/env python3
"""Regression tests for the independent stiff-boundary shooting check."""

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory.verify_superpotential_boundary_shooting import (
    OUTPUT,
    build,
)


class SuperpotentialBoundaryShootingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_independent_verification_passes_without_observations(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertIn("no finite-element", self.result["method"]["independence"])

    def test_all_stiff_modes_are_recovered(self) -> None:
        self.assertEqual(len(self.result["modes"]), 7)
        self.assertLessEqual(
            self.result["maximum_mass_relative_difference"],
            self.result["criteria"]["mass_relative_tolerance"],
        )
        self.assertLessEqual(
            self.result["maximum_root_residual_over_bracket"],
            self.result["criteria"]["root_residual_over_bracket_max"],
        )
        for row in self.result["modes"]:
            self.assertLess(row["bracket_residual"][0] * row["bracket_residual"][1], 0.0)

    def test_rendered_artifact_matches_when_present(self) -> None:
        if OUTPUT.exists():
            self.assertEqual(
                json.loads(OUTPUT.read_text(encoding="utf-8")), self.result
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
