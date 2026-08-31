from __future__ import annotations

import json
import math
import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_dirac_critical_bath_gate as bath,
)


class DiracCriticalBathGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = bath.build()

    def test_clifford_algebra_and_spectrum(self) -> None:
        self.assertEqual(bath.clifford_error(), 0.0)
        momentum = np.asarray([0.31, -0.47])
        gradient = np.asarray([0.23, 0.11, -0.38])
        velocity = 0.8
        yukawa = 1.4
        eigenvalues = bath.dirac_spectrum(
            momentum, gradient, velocity=velocity, yukawa=yukawa
        )
        energy = math.sqrt(
            velocity**2 * float(momentum @ momentum)
            + yukawa**2 * float(gradient @ gradient)
        )
        np.testing.assert_allclose(
            eigenvalues,
            [-energy, -energy, energy, energy],
            rtol=0.0,
            atol=2.0e-15,
        )

    def test_closed_filled_sea_matches_spectral_integral(self) -> None:
        parameters = {
            "cutoff": 2.7,
            "yukawa": 1.3,
            "rho_slope": 0.75,
            "degeneracy": 3,
        }
        for gap in (0.0, 0.16):
            for acceleration in (0.003, 0.04, 0.7, 3.0):
                with self.subTest(gap=gap, acceleration=acceleration):
                    closed = bath.bath_lagrangian(
                        acceleration, infrared_gap=gap, **parameters
                    )
                    numeric = bath.numerical_bath_lagrangian(
                        acceleration,
                        infrared_gap=gap,
                        intervals=16384,
                        **parameters,
                    )
                    self.assertLess(abs(numeric / closed - 1.0), 2.0e-9)

    def test_critical_matching_leaves_negative_cubic(self) -> None:
        parameters = {
            "cutoff": 3.1,
            "yukawa": 0.9,
            "rho_slope": 0.45,
            "degeneracy": 6,
        }
        expected_stiffness = (
            0.5
            * parameters["degeneracy"]
            * parameters["rho_slope"]
            * parameters["cutoff"]
            * parameters["yukawa"] ** 2
        )
        self.assertAlmostEqual(
            bath.critical_stiffness(**parameters), expected_stiffness
        )
        expected_cubic = (
            parameters["degeneracy"]
            * parameters["rho_slope"]
            * parameters["yukawa"] ** 3
            / 3.0
        )
        for acceleration in (1.0e-8, 3.0e-7, 1.0e-5):
            actual = bath.matched_lagrangian(acceleration, **parameters)
            self.assertLess(actual, 0.0)
            self.assertAlmostEqual(
                actual / (-expected_cubic * acceleration**3),
                1.0,
                places=5,
            )

    def test_scale_and_target_normalization_close(self) -> None:
        cutoff, yukawa, rho, degeneracy = 2.2, 1.1, 0.8, 4
        a0 = bath.acceleration_scale(cutoff=cutoff, yukawa=yukawa)
        stiffness = bath.critical_stiffness(
            cutoff=cutoff,
            yukawa=yukawa,
            rho_slope=rho,
            degeneracy=degeneracy,
        )
        microscopic_cubic = degeneracy * rho * yukawa**3 / 3.0
        target_cubic = 2.0 * stiffness / (3.0 * a0)
        self.assertAlmostEqual(a0, cutoff / yukawa)
        self.assertAlmostEqual(microscopic_cubic, target_cubic)

    def test_exact_constitutive_function_is_healthy_off_origin(self) -> None:
        values = np.geomspace(1.0e-12, 1.0e12, 600)
        mu = np.asarray([bath.matched_mu(value) for value in values])
        derivative = np.asarray(
            [bath.matched_mu_prime(value) for value in values]
        )
        self.assertTrue(np.all(mu > 0.0))
        self.assertTrue(np.all(mu < 1.0))
        self.assertTrue(np.all(derivative > 0.0))
        self.assertTrue(np.all(mu + values * derivative > 0.0))
        self.assertAlmostEqual(bath.matched_mu(0.0), 0.0)
        self.assertAlmostEqual(bath.matched_mu(1.0e-8) / 1.0e-8, 1.0)
        self.assertAlmostEqual(
            (1.0 - bath.matched_mu(1.0e8)) * 1.0e8,
            0.5,
            places=7,
        )

    def test_field_function_derivative_is_mu(self) -> None:
        for x in np.geomspace(0.002, 500.0, 48):
            step = 1.0e-4
            plus = x * (1.0 + step)
            minus = x * (1.0 - step)
            derivative = (
                bath.normalized_field_function(plus)
                - bath.normalized_field_function(minus)
            ) / (plus**2 - minus**2)
            self.assertLess(abs(derivative - bath.matched_mu(float(x))), 2.0e-7)
        for x in (1.0e-10, 1.0e-7, 1.0e-4):
            expected = (2.0 / 3.0) * x**3
            self.assertLess(
                abs(bath.normalized_field_function(x) / expected - 1.0),
                4.0e-5,
            )

    def test_spherical_solution_changes_mass_scaling(self) -> None:
        sources = np.geomspace(1.0e-12, 1.0e8, 120)
        fields = np.asarray(
            [bath.solve_spherical_field(float(value)) for value in sources]
        )
        residual = np.asarray(
            [bath.matched_mu(field) * field for field in fields]
        )
        np.testing.assert_allclose(residual, sources, rtol=2.0e-14, atol=0.0)
        deep = sources < 1.0e-6
        high = sources > 1.0e4
        deep_slope = np.polyfit(np.log(sources[deep]), np.log(fields[deep]), 1)[0]
        high_slope = np.polyfit(np.log(sources[high]), np.log(fields[high]), 1)[0]
        self.assertAlmostEqual(deep_slope, 0.5, places=4)
        self.assertAlmostEqual(high_slope, 1.0, places=4)

    def test_finite_gap_rounds_nonanalytic_cubic(self) -> None:
        parameters = {
            "cutoff": 2.0,
            "yukawa": 1.2,
            "rho_slope": 0.7,
            "degeneracy": 2,
            "infrared_gap": 0.1,
        }
        accelerations = np.geomspace(1.0e-8, 1.0e-4, 30)
        energy = np.asarray(
            [-bath.matched_lagrangian(float(value), **parameters) for value in accelerations]
        )
        slope = np.polyfit(np.log(accelerations), np.log(energy), 1)[0]
        self.assertAlmostEqual(slope, 4.0, places=5)

    def test_mixed_statistics_sum_rule_is_not_overpromoted(self) -> None:
        result = bath.mixed_statistics_sum_rule()
        self.assertEqual(result["signed_quadratic_sum"], 0.0)
        self.assertEqual(result["signed_cubic_sum"], 0.5)
        self.assertTrue(result["quadratic_cancels"])
        self.assertTrue(result["negative_lagrangian_cubic_survives"])
        self.assertFalse(result["radiatively_protected"])

    def test_mixed_statistics_energy_is_globally_stable(self) -> None:
        cutoff = 2.3
        masses = np.geomspace(1.0e-10, 1.0e7, 500) * cutoff
        energy = np.asarray(
            [bath.mixed_bath_energy(value, cutoff=cutoff) for value in masses]
        )
        slope = np.asarray(
            [
                bath.mixed_bath_energy_prime(value, cutoff=cutoff)
                for value in masses
            ]
        )
        curvature = np.asarray(
            [
                bath.mixed_bath_energy_second(value, cutoff=cutoff)
                for value in masses
            ]
        )
        self.assertTrue(np.all(energy > 0.0))
        self.assertTrue(np.all(slope > 0.0))
        self.assertTrue(np.all(curvature > 0.0))
        for mass in (1.0e-10, 1.0e-8, 1.0e-6):
            self.assertAlmostEqual(
                bath.mixed_bath_energy(mass, cutoff=cutoff) / mass**3,
                1.0 / 6.0,
                places=6,
            )
        mass = 0.7
        step = 1.0e-5
        numeric_slope = (
            bath.mixed_bath_energy(mass + step, cutoff=cutoff)
            - bath.mixed_bath_energy(mass - step, cutoff=cutoff)
        ) / (2.0 * step)
        self.assertAlmostEqual(
            numeric_slope,
            bath.mixed_bath_energy_prime(mass, cutoff=cutoff),
            places=9,
        )

    def test_temporal_kernel_exposes_nonanalytic_dynamic_obstruction(self) -> None:
        parameters = {
            "cutoff": 2.1,
            "yukawa": 1.3,
            "rho_slope": 0.7,
            "degeneracy": 2,
        }
        frequencies = np.geomspace(1.0e-12, 1.0e-5, 40)
        deficits = np.asarray(
            [
                bath.temporal_kernel_deficit(value, **parameters)
                for value in frequencies
            ]
        )
        expected = (
            math.pi
            * parameters["degeneracy"]
            * parameters["rho_slope"]
            * parameters["yukawa"] ** 2
            / 8.0
        )
        self.assertAlmostEqual(
            float(np.median(deficits / frequencies)) / expected,
            1.0,
            places=6,
        )
        self.assertEqual(bath.temporal_kernel_deficit(0.0, **parameters), 0.0)
        self.assertEqual(
            bath.temporal_kernel_deficit(-0.3, **parameters),
            bath.temporal_kernel_deficit(0.3, **parameters),
        )

    def test_finite_tower_cannot_have_exact_cubic_origin(self) -> None:
        levels = [0.2, 0.7, 1.4]
        weights = [0.5, 0.3, 0.2]
        accelerations = np.geomspace(1.0e-9, 1.0e-5, 30)
        remainders = np.asarray(
            [
                -bath.discrete_critical_remainder(value, levels, weights)
                for value in accelerations
            ]
        )
        quartic_slope = np.polyfit(
            np.log(accelerations), np.log(remainders), 1
        )[0]
        self.assertAlmostEqual(quartic_slope, 4.0, places=10)

        zero_response = np.asarray(
            [
                bath.discrete_bath_lagrangian(value, [0.0], [1.0])
                for value in accelerations
            ]
        )
        linear_slope = np.polyfit(
            np.log(accelerations), np.log(zero_response), 1
        )[0]
        self.assertAlmostEqual(linear_slope, 1.0, places=12)

    def test_extreme_finite_inputs_are_numerically_stable_or_rejected(self) -> None:
        for acceleration in (1.0e-10, 1.0e-8):
            closed = bath.bath_lagrangian(acceleration)
            numeric = bath.numerical_bath_lagrangian(
                acceleration, intervals=131072
            )
            self.assertGreater(closed, 0.0)
            self.assertLess(abs(numeric / closed - 1.0), 3.0e-6)
        self.assertAlmostEqual(
            bath.normalized_field_function(1.0e100) / 1.0e200,
            1.0,
        )
        for source in (1.0e-100, 1.0e-60, 1.0e100, 1.0e308):
            field = bath.solve_spherical_field(source)
            self.assertAlmostEqual(
                bath.matched_mu(field) * field / source,
                1.0,
                places=14,
            )
        for acceleration, cutoff in ((1.0e9, 2.3), (1.0e150, 1.0), (1.0e308, 1.0)):
            with self.subTest(acceleration=acceleration, cutoff=cutoff):
                closed = bath.bath_lagrangian(acceleration, cutoff=cutoff)
                numeric = bath.numerical_bath_lagrangian(
                    acceleration, cutoff=cutoff
                )
                self.assertGreater(closed, 0.0)
                self.assertAlmostEqual(numeric / closed, 1.0, places=14)
        mixed = bath.mixed_bath_energy(1.0e9, cutoff=2.3)
        self.assertGreater(mixed, 0.0)
        self.assertAlmostEqual(
            mixed / (0.5 * 2.3**2 * 1.0e9), 1.0, places=8
        )
        scaled_temporal = bath.temporal_kernel_deficit(
            1.0e-308,
            cutoff=1.0,
            yukawa=1.0e308,
            rho_slope=1.0e-308,
        )
        self.assertAlmostEqual(scaled_temporal, math.pi / 8.0, places=14)
        self.assertAlmostEqual(
            bath.temporal_kernel_deficit(
                1.0e308, cutoff=1.0e-100, rho_slope=1.0e100
            ),
            0.5,
            places=14,
        )
        balanced_bath = bath.bath_lagrangian(
            1.0e200, cutoff=1.0e200, rho_slope=1.0e-300
        )
        balanced_expected = ((2.0**1.5 - 2.0) / 3.0) * 1.0e300
        self.assertAlmostEqual(
            balanced_bath / balanced_expected, 1.0, places=14
        )
        self.assertAlmostEqual(
            bath.matched_lagrangian(1.0e200, rho_slope=1.0e-300)
            / -5.0e99,
            1.0,
            places=14,
        )
        self.assertAlmostEqual(
            bath.matched_lagrangian(
                1.0e100, cutoff=1.0e308, rho_slope=1.0e-300
            ),
            -1.0 / 3.0,
            places=14,
        )
        self.assertTrue(
            math.isclose(
                bath.matched_lagrangian(
                    1.0e50,
                    cutoff=1.0e200,
                    infrared_gap=1.0e100,
                    rho_slope=1.0e-200,
                ),
                -1.25e-101,
                rel_tol=2.0e-14,
            )
        )
        self.assertTrue(
            math.isclose(
                bath.discrete_critical_remainder(
                    1.0e100, [1.0e104], [1.0e200]
                ),
                -1.25e287,
                rel_tol=2.0e-14,
            )
        )
        self.assertTrue(
            math.isclose(
                bath.mixed_bath_energy(1.0e102, cutoff=1.0e105),
                1.6657291668619791e305,
                rel_tol=2.0e-14,
            )
        )
        with self.assertRaises(bath.DiracBathInputError):
            bath.discrete_bath_lagrangian(
                1.0e308, [1.0], [1.0e-308], yukawa=2.0
            )
        with self.assertRaises(bath.DiracBathInputError):
            bath.critical_stiffness(cutoff=1.0e308, yukawa=1.0e308)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(bath.DiracBathInputError):
            bath.bath_lagrangian(1.0, cutoff=0.0)
        with self.assertRaises(bath.DiracBathInputError):
            bath.bath_lagrangian(-1.0)
        with self.assertRaises(bath.DiracBathInputError):
            bath.bath_lagrangian(1.0, infrared_gap=1.0)
        with self.assertRaises(bath.DiracBathInputError):
            bath.bath_lagrangian(1.0, degeneracy=True)
        with self.assertRaises(bath.DiracBathInputError):
            bath.numerical_bath_lagrangian(1.0, intervals=7)
        with self.assertRaises(bath.DiracBathInputError):
            bath.dirac_spectrum([1.0], [1.0, 2.0, 3.0])
        with self.assertRaises(bath.DiracBathInputError):
            bath.solve_spherical_field(float("nan"))

    def test_decision_is_fail_closed_at_the_holo_boundary(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        decision = self.result["decision"]
        self.assertEqual(
            decision["verdict"],
            (
                "SURVIVES_STATIC_SPECTRAL_GATE_BLOCKED_MICROSCOPIC_"
                "LOCAL_QFT_AND_HOLO"
            ),
        )
        self.assertTrue(decision["uniform_static_spectral_candidate"])
        self.assertFalse(decision["finite_local_qft_realization_exhibited"])
        self.assertTrue(
            decision["deep_operator_candidate_survives_static_algebraic_gate"]
        )
        self.assertFalse(decision["exact_exposed_collector_interpolation_reproduced"])
        self.assertFalse(decision["current_holo_mechanism"])
        self.assertFalse(decision["physical_completion"])
        self.assertFalse(decision["new_force_as_fundamental_physics"])
        self.assertFalse(decision["lensing_derived"])
        gates = self.result["physical_gates"]
        self.assertFalse(
            gates["quadratic_matching_or_sum_rule_radiatively_protected"]
        )
        self.assertFalse(
            gates["time_dependent_bath_response_local_and_adiabatic_at_zero_gap"]
        )
        self.assertFalse(gates["five_dimensional_covariant_action_and_constraints_derived"])
        parameters = self.result["diagnostics"]["parameters"]
        self.assertEqual(parameters["negative_branches_per_4x4_multiplet"], 2)
        self.assertEqual(parameters["equivalent_4x4_multiplets"], 2.0)

    def test_no_observations_or_publication_claim(self) -> None:
        self.assertEqual(
            self.result["sources"]["raw_observational_tables_read_directly"], []
        )
        self.assertEqual(
            self.result["sources"]["inherited_exposed_target_origin"],
            "SPARC training split only",
        )
        self.assertGreater(
            self.result["diagnostics"][
                "maximum_absolute_mu_difference_from_exposed_target"
            ],
            0.07,
        )
        boundary = self.result["evidence_boundary"].lower()
        self.assertIn("not a completed", boundary)
        self.assertIn("not", boundary)
        self.assertFalse(self.result["decision"]["publication_authorized"])

    def test_artifact_equals_fresh_builder(self) -> None:
        artifact = json.loads(bath.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(artifact, self.result)


if __name__ == "__main__":
    unittest.main()
