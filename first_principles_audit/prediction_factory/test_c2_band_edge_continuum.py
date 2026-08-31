from __future__ import annotations

import math
import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_c2_band_edge_continuum as band,
)


class C2BandEdgeContinuumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = band.build()

    def test_closed_pressure_matches_occupation_integral(self) -> None:
        parameters = {"mass": 2.3, "rho0": 0.7, "eta": 1.1, "delta": 0.2}
        for y in (0.19, 0.2 / 1.1, 0.3, 1.0, 4.0):
            with self.subTest(y=y):
                expected = band.band_edge_pressure(y, **parameters)
                actual = band.numerical_spectral_pressure(y, **parameters)
                self.assertAlmostEqual(actual, expected, places=13)

    def test_density_is_pressure_derivative_and_legendre_selector(self) -> None:
        mass, rho0, eta, delta = 1.4, 0.6, 0.9, 0.07
        for y in (0.2, 0.8, 2.0):
            density = band.selector_density(
                y, mass=mass, rho0=rho0, eta=eta, delta=delta
            )
            pressure = band.band_edge_pressure(
                y, mass=mass, rho0=rho0, eta=eta, delta=delta
            )
            dual = (
                (eta * y - delta) * density
                - band.selector_energy(density, mass=mass, rho0=rho0)
            )
            self.assertAlmostEqual(dual, pressure, places=13)

            step = 1.0e-6 * y
            derivative = (
                band.band_edge_pressure(
                    y + step, mass=mass, rho0=rho0, eta=eta, delta=delta
                )
                - band.band_edge_pressure(
                    y - step, mass=mass, rho0=rho0, eta=eta, delta=delta
                )
            ) / (2.0 * step)
            self.assertAlmostEqual(derivative / eta, density, places=9)

    def test_stable_bath_has_wrong_target_curvature_sign(self) -> None:
        parameters = {"mass": 1.6, "rho0": 0.75, "eta": 1.2, "delta": 0.1}
        y = 0.8
        curvature = band.equilibrium_y_curvature(y, **parameters)
        self.assertLess(curvature, 0.0)
        step = 1.0e-4
        numeric = (
            band.equilibrium_grand_potential(y + step, **parameters)
            - 2.0 * band.equilibrium_grand_potential(y, **parameters)
            + band.equilibrium_grand_potential(y - step, **parameters)
        ) / step**2
        self.assertAlmostEqual(numeric / curvature, 1.0, places=7)

    def test_normalized_selector_has_exact_square_root_branch(self) -> None:
        mass, rho0, eta, delta = 3.0, 1.2, 0.4, 0.3
        yc = delta / eta
        for excess in (1.0e-10, 1.0e-5, 0.2, 3.0):
            density = band.selector_density(
                yc + excess,
                mass=mass,
                rho0=rho0,
                eta=eta,
                delta=delta,
            )
            selector = band.normalized_selector(
                density, mass=mass, rho0=rho0, eta=eta
            )
            expected = math.sqrt(excess)
            self.assertLess(abs(selector / expected - 1.0), 1.0e-7)

    def test_threshold_is_fail_closed(self) -> None:
        for y in (-2.0, 0.0, 0.49):
            self.assertEqual(
                band.band_edge_pressure(y, eta=2.0, delta=1.0), 0.0
            )
            self.assertEqual(
                band.selector_density(y, eta=2.0, delta=1.0), 0.0
            )
        self.assertGreater(
            band.band_edge_pressure(0.51, eta=2.0, delta=1.0), 0.0
        )

    def test_scaling_rule_selects_z2_not_z1(self) -> None:
        self.assertEqual(band.density_of_states_power(0.0, 2.0), 1.5)
        self.assertEqual(band.density_of_states_power(0.0, 1.0), 2.0)
        self.assertAlmostEqual(band.density_of_states_power(2.0, 2.0), 2.5)

    def test_full_wire_state_counting_folds_to_one_over_pi(self) -> None:
        length_density = 2.7
        self.assertAlmostEqual(
            band.wire_spectral_density(length_density),
            length_density / math.pi,
        )
        self.assertAlmostEqual(
            band.wire_spectral_density(length_density, degeneracy=3),
            3.0 * length_density / math.pi,
        )

    def test_finite_spacing_does_not_have_exact_deep_continuum(self) -> None:
        spacing = 0.1
        mass = 1.0
        rho0 = 1.0
        # Below the first excited threshold only the zero level contributes,
        # so the compact pressure is linear while the continuum is Y^(3/2).
        y1, y2 = 1.0e-5, 2.0e-5
        p1 = band.finite_spacing_pressure(
            y1, spacing=spacing, mass=mass, rho0=rho0
        )
        p2 = band.finite_spacing_pressure(
            y2, spacing=spacing, mass=mass, rho0=rho0
        )
        self.assertAlmostEqual(p2 / p1, y2 / y1)
        continuum_ratio = band.band_edge_pressure(y2) / band.band_edge_pressure(y1)
        self.assertAlmostEqual(continuum_ratio, (y2 / y1) ** 1.5)
        self.assertNotAlmostEqual(p2 / p1, continuum_ratio)

    def test_stable_equilibrium_branch_has_no_interior_fold(self) -> None:
        mass, rho0 = 2.0, 0.9
        densities = (1.0e-8, 0.01, 0.4, 2.0)
        inverse_compressibilities = [
            density / (mass * rho0**2) for density in densities
        ]
        self.assertTrue(all(value > 0.0 for value in inverse_compressibilities))
        self.assertTrue(
            all(
                inverse_compressibilities[index + 1]
                > inverse_compressibilities[index]
                for index in range(len(inverse_compressibilities) - 1)
            )
        )

    def test_attraction_creates_spinodal_before_coexistence(self) -> None:
        parameters = {
            "attraction": 0.5,
            "mass": 1.8,
            "rho0": 0.75,
            "eta": 1.2,
            "delta": 0.6,
        }
        result = band.attractive_fold(**parameters)
        self.assertGreater(result["coexistence_y"], result["spinodal_y"])
        self.assertLess(
            result["coexistence_y"], parameters["delta"] / parameters["eta"]
        )
        curvature = (
            result["spinodal_density"]
            / (parameters["mass"] * parameters["rho0"] ** 2)
            - parameters["attraction"]
        )
        self.assertAlmostEqual(curvature, 0.0)
        omega = band.grand_potential(
            result["coexistence_density"],
            result["coexistence_y"],
            **parameters,
        )
        self.assertAlmostEqual(omega, 0.0, places=14)

    def test_declared_natural_unit_scaling_closes(self) -> None:
        mass, rho0, eta = 1.3, 0.8, 0.6
        scale = 7.0
        base = band.selector_prefactor(mass=mass, rho0=rho0, eta=eta)
        scaled = band.selector_prefactor(
            mass=scale * mass,
            rho0=scale**2 * rho0,
            eta=scale * eta,
        )
        self.assertAlmostEqual(scaled / base, scale**4, places=12)

    def test_invalid_inputs_are_rejected(self) -> None:
        with self.assertRaises(band.BandEdgeInputError):
            band.band_edge_pressure(1.0, mass=0.0)
        with self.assertRaises(band.BandEdgeInputError):
            band.band_edge_pressure(1.0, rho0=-1.0)
        with self.assertRaises(band.BandEdgeInputError):
            band.band_edge_pressure(1.0, eta=float("nan"))
        with self.assertRaises(band.BandEdgeInputError):
            band.numerical_spectral_pressure(1.0, intervals=3)
        with self.assertRaises(band.BandEdgeInputError):
            band.density_of_states_power(-1.0, 2.0)
        with self.assertRaises(band.BandEdgeInputError):
            band.density_of_states_power(0.0, 0.0)
        with self.assertRaises(band.BandEdgeInputError):
            band.wire_spectral_density(0.0)
        with self.assertRaises(band.BandEdgeInputError):
            band.wire_spectral_density(1.0, degeneracy=0)
        with self.assertRaises(band.BandEdgeInputError):
            band.equilibrium_y_curvature(0.0)

    def test_extreme_finite_scales_are_evaluated_without_intermediate_overflow(self) -> None:
        self.assertAlmostEqual(
            band.fermi_edge(1.0e-308, mass=1.0e308),
            math.sqrt(2.0),
            places=14,
        )
        pressure = band.band_edge_pressure(
            1.0e-200, mass=1.0e218, rho0=1.0e200
        )
        numerical = band.numerical_spectral_pressure(
            1.0e-200, mass=1.0e218, rho0=1.0e200
        )
        expected = 2.0 * math.sqrt(2.0) * 1.0e9 / 3.0
        self.assertAlmostEqual(pressure / expected, 1.0, places=14)
        self.assertAlmostEqual(numerical / pressure, 1.0, places=14)
        self.assertAlmostEqual(
            band.selector_energy(1.0e200, mass=1.0e200, rho0=1.0e200),
            1.0 / 6.0,
            places=14,
        )
        self.assertAlmostEqual(
            band.grand_potential(
                1.0e200, 0.0, mass=1.0e200, rho0=1.0e200
            ),
            1.0 / 6.0,
            places=14,
        )
        self.assertTrue(
            math.isclose(
                band.selector_energy(1.0e-200, mass=1.0e-320),
                1.666685222e-281,
                rel_tol=1.0e-8,
            )
        )
        self.assertAlmostEqual(
            band.normalized_selector(1.0e-320, rho0=1.0e-320),
            1.0 / math.sqrt(2.0),
            places=14,
        )
        maximum = float.fromhex("0x1.fffffffffffffp1023")
        balanced_pressure = band.band_edge_pressure(
            maximum, mass=maximum, rho0=5.0e-309
        )
        balanced_numerical = band.numerical_spectral_pressure(
            maximum, mass=maximum, rho0=5.0e-309
        )
        self.assertAlmostEqual(
            balanced_numerical / balanced_pressure, 1.0, places=14
        )
        balanced_density = band.selector_density(
            maximum, mass=maximum, rho0=1.0e-300
        )
        self.assertTrue(math.isfinite(balanced_density))
        self.assertGreater(balanced_density, 0.0)
        with self.assertRaises(band.BandEdgeInputError):
            band.finite_spacing_pressure(1.0, spacing=1.0e-20)
        with self.assertRaises(band.BandEdgeInputError):
            band.band_edge_pressure(1.0e308, mass=1.0e308)

    def test_wrong_variational_sign_kills_candidate(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        decision = self.result["decision"]
        self.assertEqual(
            decision["verdict"], "KILL_C2_BAND_EDGE_WRONG_VARIATIONAL_SIGN"
        )
        self.assertTrue(decision["exact_exponent_and_positive_pressure_derived"])
        self.assertTrue(decision["tested_live_C2_class"])
        self.assertFalse(decision["required_AQUAL_variational_sign_derived"])
        self.assertFalse(decision["candidate_survives"])
        self.assertFalse(decision["current_holo_mechanism_candidate"])
        self.assertFalse(decision["physical_completion"])
        self.assertFalse(decision["new_force_derived"])
        self.assertFalse(decision["lensing_derived"])
        gates = self.result["physical_gates"]
        self.assertFalse(gates["current_finite_HOLO_interval_decompactified"])
        self.assertFalse(gates["eta_times_Y_vertex_derived_from_current_5d_action"])
        self.assertFalse(gates["required_AQUAL_variational_sign_derived"])
        self.assertFalse(gates["uniform_local_density_approximation_at_onset"])
        sign = self.result["variational_sign_audit"]
        self.assertEqual(sign["verdict"], "FAIL_REQUIRED_AQUAL_VARIATIONAL_SIGN")
        self.assertIn("+P", sign["induced_static_actions"])
        self.assertIn("-C*P", sign["required_target_sign"])
        self.assertEqual(
            self.result["kill_criteria"][-1]["current_result"], "TRIGGERED"
        )

    def test_no_observational_input_or_target_blind_claim(self) -> None:
        self.assertEqual(
            self.result["sources"]["raw_observational_tables_read_directly"], []
        )
        self.assertEqual(
            self.result["sources"]["inherited_exposed_target_origin"],
            "SPARC training split only",
        )
        boundary = self.result["evidence_boundary"].lower()
        self.assertIn("not an embedding", boundary)
        self.assertIn("inherits a sparc training fit", boundary)
        self.assertIn("not", boundary)

    def test_versioned_artifact_equals_fresh_builder(self) -> None:
        artifact = json.loads(band.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(artifact, self.result)


if __name__ == "__main__":
    unittest.main()
