#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_c1_bk_derivative_gate as gate,
)


class C1BKDerivativeGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    def test_unregulated_solution_reproduces_eq92_and_eq93(self) -> None:
        x_values = np.logspace(-10.0, 6.0, 81)
        for x_abs in x_values:
            solution = gate.unregulated_solution(float(x_abs), mass=2.0, scale=3.0)
            expected_s = 3.0 * math.sqrt(4.0 * x_abs)
            expected_coefficient = 2.0 * 3.0 * 4.0**1.5 / 3.0
            self.assertAlmostEqual(solution["selector_s"] / expected_s, 1.0)
            self.assertAlmostEqual(
                solution["lagrangian"] / (-expected_coefficient * x_abs**1.5),
                1.0,
            )

    def test_radial_extremum_is_a_true_static_energy_minimum(self) -> None:
        for x_abs in (1.0e-8, 0.1, 3.0, 1.0e4):
            solution = gate.unregulated_solution(x_abs, mass=1.7, scale=0.8)
            selector_s = solution["selector_s"]
            first = gate.regulated_d_lagrangian_ds(
                selector_s, -x_abs, mass=1.7, scale=0.8
            )
            curvature = gate.radial_energy_curvature(
                selector_s, -x_abs, mass=1.7, scale=0.8
            )
            gradient_normalization = gate.radial_gradient_normalization(
                selector_s, -x_abs, mass=1.7, scale=0.8
            )
            self.assertAlmostEqual(first, 0.0, delta=2.0e-11 * x_abs)
            self.assertAlmostEqual(curvature / (16.0 * 1.7 * x_abs), 1.0)
            self.assertAlmostEqual(gradient_normalization, 2.0)
            self.assertAlmostEqual(
                solution["radial_inverse_correlation_scale_squared"]
                / (8.0 * 1.7 * x_abs),
                1.0,
            )
            self.assertGreater(curvature, 0.0)

    def test_regulator_creates_an_exact_fold(self) -> None:
        y_star, eta_star = gate.fold_point()
        self.assertAlmostEqual(
            gate.dimensionless_stationarity(y_star, eta_star), 0.0, delta=2.0e-11
        )
        self.assertAlmostEqual(
            gate.dimensionless_stationarity_derivative(y_star, eta_star),
            0.0,
            delta=2.0e-11,
        )
        self.assertEqual(gate.regulated_stationary_roots(0.999 * eta_star), [])
        self.assertEqual(gate.regulated_stationary_roots(eta_star), [y_star])

    def test_roots_above_fold_have_opposite_radial_stability(self) -> None:
        _, eta_star = gate.fold_point()
        eta = 3.0 * eta_star
        roots_y = gate.regulated_stationary_roots(eta)
        self.assertEqual(len(roots_y), 2)
        regulator = 0.2
        x_abs = gate.x_abs_from_eta(eta, regulator=regulator)
        curvatures = [
            gate.radial_energy_curvature(
                regulator**2 * root_y, -x_abs, regulator=regulator
            )
            for root_y in roots_y
        ]
        self.assertLess(curvatures[0], 0.0)
        self.assertGreater(curvatures[1], 0.0)
        for root_y in roots_y:
            self.assertLess(gate.normalized_stationarity_residual(root_y, eta), 2.0e-14)

    def test_fold_scale_tracks_regulator_to_the_fourth_power(self) -> None:
        _, eta_star = gate.fold_point()
        first = gate.x_abs_from_eta(eta_star, mass=2.0, scale=3.0, regulator=0.2)
        second = gate.x_abs_from_eta(eta_star, mass=2.0, scale=3.0, regulator=0.1)
        self.assertAlmostEqual(first / second, 16.0)
        self.assertAlmostEqual(
            gate.eta_from_parameters(first, mass=2.0, scale=3.0, regulator=0.2),
            eta_star,
        )

    def test_regulator_zero_limit_is_not_a_uniform_local_limit(self) -> None:
        small = gate.unregulated_solution(1.0e-12)
        smaller = gate.unregulated_solution(1.0e-16)
        self.assertLess(
            smaller["radial_inverse_correlation_scale"],
            small["radial_inverse_correlation_scale"],
        )
        self.assertGreater(
            smaller["radial_correlation_length"],
            small["radial_correlation_length"],
        )
        with self.assertRaises(ValueError):
            gate.regulated_lagrangian(0.0, -1.0, regulator=0.0)
        self.assertEqual(gate.regulated_lagrangian(0.0, -1.0, regulator=0.1), 0.0)

    def test_weyl_homogeneity_does_not_select_a_unique_wilson_function(self) -> None:
        minimal = gate.homogeneous_tower_minimum(0.0)
        deformed = gate.homogeneous_tower_minimum(1.0)
        self.assertEqual(minimal["power_in_x"], 1.5)
        self.assertEqual(deformed["power_in_x"], 1.5)
        self.assertGreater(minimal["dimensionless_radial_curvature"], 0.0)
        self.assertGreater(deformed["dimensionless_radial_curvature"], 0.0)
        self.assertNotAlmostEqual(
            minimal["onshell_energy_coefficient"],
            deformed["onshell_energy_coefficient"],
        )

    def test_relevant_deformations_and_5d_scaling_are_fail_closed(self) -> None:
        self.assertAlmostEqual(gate.relevant_deformation_power(1.0), 0.75)
        self.assertAlmostEqual(gate.relevant_deformation_power(2.0), 1.2)
        self.assertAlmostEqual(gate.relevant_deformation_power(3.0), 1.5)
        self.assertEqual(gate.quasistatic_weyl_power(3), 1.5)
        self.assertEqual(gate.quasistatic_weyl_power(4), 2.0)
        for q_power in (2.0, 4.0, 6.0):
            sigma_power = gate.compensator_power_for_bulk_operator(q_power)
            self.assertAlmostEqual(sigma_power + 1.5 * q_power, 5.0)

    def test_negative_x_phonon_sign_is_distinct_from_radial_stability(self) -> None:
        self.assertLess(gate.phonon_second_derivative(-2.0), 0.0)
        self.assertGreater(gate.phonon_second_derivative(2.0), 0.0)
        self.assertGreater(
            gate.unregulated_solution(2.0)["radial_energy_curvature"], 0.0
        )

    def test_certificate_passes_math_and_kills_physical_c1(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["checks"]["all"])
        self.assertTrue(
            self.result["decision"]["promote_as_mathematical_counterexample"]
        )
        self.assertFalse(self.result["binary_gates"]["all"])
        self.assertFalse(
            self.result["decision"]["promote_as_declared_holo_c1_completion"]
        )
        self.assertEqual(self.result["decision"]["verdict"], "KILL_C1")
        failed = [
            name
            for name, value in self.result["binary_gates"].items()
            if name != "all" and not value["passed"]
        ]
        self.assertEqual(len(failed), 6)

    def test_generated_artifact_matches_fresh_builder(self) -> None:
        stored = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.result)


if __name__ == "__main__":
    unittest.main()
