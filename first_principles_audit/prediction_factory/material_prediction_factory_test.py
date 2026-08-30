#!/usr/bin/env python3
"""Independent checks for the prospective material prediction factory."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "material_prediction_factory.py"
SPEC = importlib.util.spec_from_file_location("material_prediction_factory", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {MODULE_PATH}")
FACTORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FACTORY)


class MaterialPredictionFactoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = FACTORY.build_report()
        cls.payload = cls.report["payload"]
        cls.modes = cls.payload["positive_modes"]

    def test_six_positive_blind_modes_only(self) -> None:
        self.assertEqual(len(self.modes), 6)
        self.assertTrue(all(mode["mu_n"] > 0.0 for mode in self.modes))
        self.assertTrue(all(mode["beta_n_uv"] > 0.0 for mode in self.modes))
        self.assertEqual(self.payload["provenance"]["observational_inputs_read"], [])
        self.assertEqual(
            self.payload["provenance"]["historical_fitted_couplings_reused"], []
        )
        self.assertIn("massless Neumann zero mode", self.payload["scope"]["excluded_mode"])

    def test_embedded_and_detached_hashes(self) -> None:
        expected_payload_hash = hashlib.sha256(
            FACTORY.canonical_json_bytes(self.payload)
        ).hexdigest()
        self.assertEqual(
            self.report["integrity"]["payload_sha256"], expected_payload_hash
        )
        FACTORY.check_artifacts(self.report)

    def test_short_distance_limit_and_monotonic_curves(self) -> None:
        alpha_sum = sum(mode["alpha_n_2_beta_squared"] for mode in self.modes)
        limits = self.payload["short_distance_limits"]
        self.assertAlmostEqual(limits["sum_alpha_n"], alpha_sum, places=18)

        at_zero = FACTORY.response_at_x(self.modes, 0.0)
        for key in (
            "potential_over_newtonian_potential",
            "force_over_newtonian_force",
            "radial_force_gradient_over_newtonian_gradient",
        ):
            self.assertAlmostEqual(at_zero[key], alpha_sum, places=18)

        samples = self.payload["dimensionless_curves"]["samples"]
        for key in (
            "potential_over_newtonian_potential",
            "force_over_newtonian_force",
            "radial_force_gradient_over_newtonian_gradient",
        ):
            values = [point[key] for point in samples]
            self.assertTrue(all(value > 0.0 for value in values))
            self.assertTrue(
                all(values[i + 1] < values[i] for i in range(len(values) - 1))
            )

    def test_gradient_formula_against_finite_difference(self) -> None:
        # Independently differentiate F_phi proportional to S_F(x)/x^2.
        for x in (0.03, 0.1, 0.3, 1.0, 3.0, 10.0):
            step = max(1.0e-7, x * 1.0e-5)

            def absolute_force_shape(value: float) -> float:
                force_fraction = FACTORY.response_at_x(self.modes, value)[
                    "force_over_newtonian_force"
                ]
                return force_fraction / (value * value)

            derivative = (
                absolute_force_shape(x + step) - absolute_force_shape(x - step)
            ) / (2.0 * step)
            gradient_ratio_fd = -0.5 * x**3 * derivative
            analytic = FACTORY.response_at_x(self.modes, x)[
                "radial_force_gradient_over_newtonian_gradient"
            ]
            self.assertAlmostEqual(gradient_ratio_fd / analytic, 1.0, delta=2.0e-8)

    def test_distance_ratios_reconstruct_from_anchor_values(self) -> None:
        ratios = self.payload["distance_ratios"]
        anchors = {
            point["x_r_over_ell"]: point for point in ratios["response_at_anchors"]
        }
        for row in ratios["adjacent_decay_ratios"]:
            near = anchors[row["near_x_r_over_ell"]]
            far = anchors[row["far_x_r_over_ell"]]
            self.assertAlmostEqual(
                row["force_at_far_over_near"],
                far["force_over_newtonian_force"]
                / near["force_over_newtonian_force"],
                places=15,
            )
            self.assertAlmostEqual(
                row["gradient_at_far_over_near"],
                far["radial_force_gradient_over_newtonian_gradient"]
                / near["radial_force_gradient_over_newtonian_gradient"],
                places=15,
            )

    def test_normalized_mechanical_transfer(self) -> None:
        curve = self.payload["normalized_mechanical_transfer"]["curve"]
        by_delta = {
            round(row["delta_2Q_omega_minus_omega0_over_omega0"], 8): row
            for row in curve
        }
        self.assertAlmostEqual(by_delta[0.0]["magnitude"], 1.0, places=15)
        self.assertAlmostEqual(by_delta[0.0]["phase_rad"], 0.0, places=15)
        self.assertAlmostEqual(by_delta[1.0]["magnitude"], 1.0 / math.sqrt(2.0), places=15)
        self.assertAlmostEqual(by_delta[-1.0]["magnitude"], 1.0 / math.sqrt(2.0), places=15)
        self.assertAlmostEqual(by_delta[1.0]["phase_rad"], -math.pi / 4.0, places=15)
        self.assertAlmostEqual(by_delta[-1.0]["phase_rad"], math.pi / 4.0, places=15)
        self.assertAlmostEqual(by_delta[1.0]["real"], by_delta[-1.0]["real"], places=15)
        self.assertAlmostEqual(by_delta[1.0]["imag"], -by_delta[-1.0]["imag"], places=15)

    def test_frozen_json_contains_no_observational_or_detector_values(self) -> None:
        serialized = json.dumps(self.report, sort_keys=True).lower()
        for forbidden in (
            "sparc",
            "boss",
            "nist",
            "f_bulk_mhz",
            "f_earth_mhz",
            "chi2",
            "p_value",
        ):
            self.assertNotIn(forbidden, serialized)
        required = self.payload["required_external_quantities"]
        self.assertIn("to_convert_x_to_metres", required)
        self.assertIn("to_predict_a_source_signal", required)
        self.assertIn("to_predict_detector_displacement", required)


if __name__ == "__main__":
    unittest.main(verbosity=2)
