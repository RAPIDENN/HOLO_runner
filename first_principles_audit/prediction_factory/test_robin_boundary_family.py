#!/usr/bin/env python3
"""Regression tests for the prospective positive Robin family."""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path
from typing import Any

from first_principles_audit.prediction_factory.derive_robin_boundary_family import (
    INPUT_RELATIVE,
    OUTPUT,
    REPO,
    RobinCarrier,
    _carrier,
    build,
)


def _walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_strings(child)


def _walk_numbers(value: Any):
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _walk_numbers(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_numbers(child)


class RobinBoundaryFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()
        cls.artifact = json.loads(Path(OUTPUT).read_text(encoding="utf-8"))
        cls.input_payload = json.loads(
            (REPO / INPUT_RELATIVE).read_text(encoding="utf-8")
        )
        cls.carrier = RobinCarrier(*_carrier(cls.input_payload))

    def test_certificate_is_fail_closed_and_observation_free(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertTrue(all(self.result["passes"].values()))
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertEqual(
            self.result["classification"],
            "operator_derived_phase_map_not_boundary_selection",
        )

    def test_portable_finite_json(self) -> None:
        self.assertFalse(Path(self.result["input"]["path"]).is_absolute())
        self.assertFalse(any(text.startswith("/") for text in _walk_strings(self.result)))
        self.assertTrue(all(math.isfinite(float(value)) for value in _walk_numbers(self.result)))
        self.assertEqual(self.artifact["input"]["sha256"], self.result["input"]["sha256"])
        self.assertTrue(self.artifact["passes"]["all"])

    def test_four_hard_corners_and_known_carrier_values(self) -> None:
        corners = self.result["hard_corners"]
        self.assertEqual(set(corners), {"NN", "ND", "DN", "DD"})
        self.assertEqual(corners["NN"]["poles"][0]["mu"], 0.0)
        self.assertAlmostEqual(corners["NN"]["poles"][1]["mu"], 0.91389898, places=5)
        self.assertAlmostEqual(corners["ND"]["poles"][0]["mu"], 0.002744976, places=7)
        self.assertAlmostEqual(corners["DN"]["poles"][0]["mu"], 0.91382169, places=5)
        self.assertAlmostEqual(corners["DD"]["poles"][0]["mu"], 1.23052824, places=5)
        self.assertTrue(
            all(item["passes"] for item in self.result["corner_recovery"].values())
        )

    def test_ir_only_no_go(self) -> None:
        no_go = self.result["ir_only_no_go"]
        self.assertTrue(no_go["passes"])
        self.assertLess(no_go["hard_nd_mu_ceiling"], 0.01)
        self.assertLessEqual(no_go["scan_max_over_hard_ceiling"], 1.000005)
        self.assertLess(no_go["beta_uv_squared_relative_span"], 1.0e-3)

    def test_uv_avoided_crossing_tracks_poles_and_residues(self) -> None:
        crossing = self.result["uv_avoided_crossing"]
        self.assertTrue(crossing["passes"])
        self.assertTrue(crossing["residue_exchange_detected"])
        self.assertTrue(crossing["positive_level_gap"])
        self.assertGreater(len(crossing["residue_exchange_brackets"]), 0)
        self.assertGreater(crossing["minimum_first_pair_mass_gap"], 1.0e-6)

    def test_hellmann_feynman_identity(self) -> None:
        certificate = self.result["hellmann_feynman"]
        self.assertTrue(certificate["passes"])
        self.assertLessEqual(certificate["worst_error_over_allowance"], 1.0)
        self.assertGreaterEqual(len(certificate["checks"]), 18)

    def test_positive_family_stability(self) -> None:
        self.assertTrue(self.result["passes"]["all_scanned_points_stable"])
        for section in self.result["scan_paths"].values():
            self.assertTrue(all(point["stable"] for point in section))
            self.assertTrue(
                all(point["rho_uv"] >= 0.0 and point["rho_ir"] >= 0.0 for point in section)
            )

    def test_uncertified_or_negative_inputs_fail_closed(self) -> None:
        uncertified = dict(self.input_payload)
        uncertified["summary"] = dict(self.input_payload["summary"])
        uncertified["summary"]["passes"] = dict(
            self.input_payload["summary"]["passes"]
        )
        uncertified["summary"]["passes"]["all"] = False
        with self.assertRaises(RuntimeError):
            _carrier(uncertified)
        with self.assertRaises(ValueError):
            self.carrier.solve_robin(-1.0e-6, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
