from __future__ import annotations

import json
import math
import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_brane_tilted_semimetal_gate as gate,
)


class BraneTiltedSemimetalGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()
        cls.parameters = {
            "band_edge": 1.7,
            "linear_velocity": 0.9,
            "quadratic_coefficient": 0.8,
            "yukawa": 1.1,
        }
        cls.rho = gate.anisotropic_dos_slope(0.9, 0.8)

    def test_generated_artifact_matches_fresh_build(self) -> None:
        committed = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(committed, self.result)

    def test_three_space_anisotropic_density_is_exactly_linear(self) -> None:
        v = 0.73
        c = 1.2
        one_branch = 1.0 / (8.0 * math.pi * c * v)
        self.assertAlmostEqual(
            gate.anisotropic_dos_slope(
                v, c, flavor_count=1, negative_branches_per_flavor=1
            ),
            one_branch,
            places=15,
        )
        self.assertAlmostEqual(gate.anisotropic_dos_slope(v, c), 2.0 * one_branch)

    def test_tilted_clifford_spectrum_and_bounded_band(self) -> None:
        k_parallel = 0.31
        k_perp = np.asarray([0.24, -0.17])
        acceleration = np.asarray([0.19, -0.28, 0.37])
        values = gate.tilted_semimetal_spectrum(
            k_parallel,
            k_perp,
            acceleration,
            **self.parameters,
        )
        epsilon2 = (0.9 * k_parallel) ** 2 + (0.8 * float(k_perp @ k_perp)) ** 2
        tilt = epsilon2 / 1.7
        split = math.sqrt(epsilon2 + 1.1**2 * float(acceleration @ acceleration))
        self.assertTrue(
            np.allclose(
                values,
                [tilt - split, tilt - split, tilt + split, tilt + split],
                atol=1.0e-15,
                rtol=0.0,
            )
        )
        energies = np.geomspace(1.0e-6, 1.0e4, 1000)
        lower = np.asarray(
            [gate.lower_band_energy(value, 0.0, 1.7) for value in energies]
        )
        self.assertTrue(np.all(lower[energies < 1.7] < 0.0))
        self.assertTrue(np.all(lower[energies > 1.7] > 0.0))
        self.assertGreater(lower[-1], lower.min())
        for gap in (0.0, 0.2, 0.85, 3.0):
            exact_minimum = gate.lower_band_global_minimum(gap, 1.7)
            sampled = np.asarray(
                [gate.lower_band_energy(value, gap, 1.7) for value in energies]
            )
            self.assertGreaterEqual(sampled.min(), exact_minimum)
            self.assertLess(sampled.min() - exact_minimum, 2.0e-4)

    def test_fixed_charge_keeps_band_and_exact_static_bracket(self) -> None:
        for acceleration in (0.0, 0.1, 1.0, 10.0):
            self.assertTrue(
                gate.fixed_filling_interval_is_globally_lowest(
                    acceleration,
                    band_edge=1.7,
                    yukawa=1.1,
                )
            )
            ordering = gate.fixed_filling_ordering_margin(
                acceleration,
                band_edge=1.7,
                yukawa=1.1,
            )
            self.assertGreater(ordering["outside_minus_highest_inside"], 0.0)
            self.assertGreaterEqual(
                ordering["highest_occupied_energy"], ordering["energy_at_node"]
            )
        acceleration = 0.43
        closed = gate.fixed_filling_lagrangian(
            acceleration,
            band_edge=1.7,
            yukawa=1.1,
            rho_slope=self.rho,
        )
        expected = (
            self.rho
            / 3.0
            * (
                (1.7**2 + (1.1 * acceleration) ** 2) ** 1.5
                - 1.7**3
                - (1.1 * acceleration) ** 3
            )
        )
        self.assertAlmostEqual(closed, expected, places=14)
        direct = gate.numerical_fixed_filling_lagrangian(
            acceleration,
            band_edge=1.7,
            yukawa=1.1,
            rho_slope=self.rho,
            quadrature_order=768,
        )
        self.assertAlmostEqual(direct / closed, 1.0, places=12)

    def test_fixed_charge_is_not_hidden_grand_canonical_assumption(self) -> None:
        acceleration = 0.43
        canonical = gate.fixed_filling_lagrangian(
            acceleration,
            band_edge=1.7,
            yukawa=1.1,
            rho_slope=self.rho,
        )
        grand = gate.grand_canonical_lagrangian(
            acceleration,
            band_edge=1.7,
            yukawa=1.1,
            rho_slope=self.rho,
        )
        self.assertGreater(abs(grand / canonical - 1.0), 1.0e-4)
        self.assertLess(
            gate.fixed_filling_chemical_potential(
                acceleration, band_edge=1.7, yukawa=1.1
            ),
            0.0,
        )

    def test_direct_q0_kubo_matches_same_action_closed_kernel(self) -> None:
        for omega in (0.0, 0.13, 0.8):
            direct = gate.polarization_finite_momentum_euclidean(
                omega,
                0.0,
                0.0,
                **self.parameters,
                flavor_count=1,
                radial_order=48,
                polar_order=16,
                azimuthal_order=16,
            )
            exact = gate.polarization_q0_euclidean(
                omega,
                band_edge=1.7,
                yukawa=1.1,
                rho_slope=self.rho,
            )
            self.assertLess(abs(direct - exact), 2.0e-12)
        for p in (0.08 + 0.3j, 0.4 - 0.7j, 1.2 + 1.8j):
            margin = gate.q0_positive_real_stability_margin(
                p,
                0.3,
                q_zeta=26.0,
                k4_coefficient=0.8,
                eta_critical=2.0,
                brane_planck_squared=1.0,
                schur_factor=1.0,
                band_edge=1.7,
                yukawa=1.1,
                rho_slope=self.rho,
                quadrature_order=512,
            )
            self.assertGreater(margin, 0.0)

    def test_finite_momentum_kubo_is_positive_but_not_claimed_global(self) -> None:
        value0 = gate.polarization_finite_momentum_euclidean(
            0.0,
            0.12,
            0.09,
            **self.parameters,
            radial_order=28,
            polar_order=20,
            azimuthal_order=20,
        )
        value1 = gate.polarization_finite_momentum_euclidean(
            0.5,
            0.12,
            0.09,
            **self.parameters,
            radial_order=28,
            polar_order=20,
            azimuthal_order=20,
        )
        self.assertGreater(value0, value1)
        self.assertGreater(value1, 0.0)
        self.assertFalse(
            self.result["decision"]["full_q_all_vertex_global_Schur_stability_derived"]
        )

    def test_decision_advances_without_physical_promotion(self) -> None:
        decision = self.result["decision"]
        for key in (
            "local_covariant_5D_defect_matter_ansatz_exhibited",
            "literal_three_space_linear_DOS_derived",
            "bounded_below_Hamiltonian_and_finite_occupied_region_from_same_ansatz",
            "exact_static_bracket_from_same_finite_occupied_region",
            "same_ansatz_q0_acceleration_retarded_kernel_derived",
            "same_ansatz_q0_acceleration_positive_spectral_measure",
            "reduced_brane_long_wavelength_Schur_has_no_UHP_poles",
            "same_ansatz_finite_q_acceleration_block_positive_Kubo_representation_derived",
            "finite_q_sampled_static_response_below_q0",
        ):
            with self.subTest(key=key):
                self.assertTrue(decision[key])
        for key in (
            "fixed_charge_sector_dynamically_selected",
            "full_q_all_vertex_global_Schur_stability_derived",
            "inhomogeneous_fixed_charge_local_functional_derived",
            "metric_and_density_intraband_channels_included",
            "continuous_SO3_dynamical_isotropy_derived",
            "full_brane_constraint_and_junction_rank_derived",
            "warped_backreacted_solution_derived",
            "physical_completion",
            "new_force_derived",
            "lensing_derived",
            "publication_authorized",
        ):
            with self.subTest(key=key):
                self.assertFalse(decision[key])
        self.assertTrue(self.result["checks"]["all"])

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(gate.BraneSemimetalInputError):
            gate.anisotropic_dos_slope(0.0, 1.0)
        with self.assertRaises(gate.BraneSemimetalInputError):
            gate.tilted_semimetal_spectrum(
                0.0,
                [0.0],
                [0.0, 0.0, 0.0],
                **self.parameters,
            )
        with self.assertRaises(gate.BraneSemimetalInputError):
            gate.polarization_finite_momentum_euclidean(
                -1.0,
                0.0,
                0.0,
                **self.parameters,
            )


if __name__ == "__main__":
    unittest.main()
