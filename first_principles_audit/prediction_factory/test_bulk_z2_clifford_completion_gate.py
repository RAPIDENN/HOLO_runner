from __future__ import annotations

import json
import math
import unittest

import numpy as np

from first_principles_audit.prediction_factory import (
    derive_bulk_z2_clifford_completion_gate as gate,
)
from first_principles_audit.prediction_factory import (
    derive_dirac_critical_bath_gate as static_bath,
)


class BulkZ2CliffordCompletionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()
        cls.kwargs = {
            "cutoff": 1.7,
            "dispersion_coefficient": 0.8,
            "yukawa": 1.1,
            "rho_slope": gate.bulk_z2_dos_slope(0.8, flavor_count=2),
        }
        cls.schur_kwargs = {
            "q_zeta": 57.0,
            "k4_coefficient": 0.8,
            "eta_critical": 1.5,
            "planck5_cubed": 1.0,
            "schur_factor": 4.0,
        }

    def test_committed_artifact_matches_fresh_build(self) -> None:
        artifact = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(artifact, self.result)

    def test_four_space_z2_density_is_linear_with_branch_count(self) -> None:
        c = 0.73
        one_branch = 1.0 / (16.0 * math.pi**2 * c**2)
        self.assertAlmostEqual(
            gate.bulk_z2_dos_slope(c, flavor_count=1, negative_branches_per_flavor=1),
            one_branch,
            places=15,
        )
        self.assertAlmostEqual(
            gate.bulk_z2_dos_slope(c, flavor_count=3), 6.0 * one_branch
        )
        self.assertTrue(
            self.result["decision"]["literal_bulk_single_particle_linear_DOS_derived"]
        )

    def test_local_clifford_spectrum_uses_all_four_acceleration_components(
        self,
    ) -> None:
        p = np.asarray([0.3, -0.2, 0.4, 0.1])
        a = np.asarray([0.2, 0.1, -0.5, 0.3])
        values = gate.bulk_z2_clifford_spectrum(p, a)
        expected = math.hypot(float(p @ p), float(np.linalg.norm(a)))
        self.assertTrue(
            np.allclose(
                values,
                [-expected, -expected, expected, expected],
                rtol=0.0,
                atol=2.0e-15,
            )
        )
        rotated = gate.bulk_z2_clifford_spectrum(p[::-1], np.roll(a, 1))
        self.assertTrue(np.allclose(values, rotated, rtol=0.0, atol=2.0e-15))
        self.assertTrue(
            self.result["decision"][
                "three_vs_four_acceleration_component_mismatch_removed"
            ]
        )

    def test_bulk_dos_inserted_in_sea_gives_closed_static_function(self) -> None:
        rho = gate.bulk_z2_dos_slope(0.9)
        acceleration = 0.37
        closed = gate.local_gaussian_completion_lagrangian(
            acceleration,
            regulator_mass=1.4,
            yukawa=1.2,
            rho_slope=rho,
        )
        numeric = gate.numerical_local_gaussian_completion(
            acceleration,
            regulator_mass=1.4,
            yukawa=1.2,
            rho_slope=rho,
            quadrature_order=768,
        )
        self.assertLess(abs(numeric / closed - 1.0), 2.0e-11)
        # The same closed form was previously represented by a sharp spectral
        # cutoff; the local fermion-plus-two-boson integrand now derives it.
        cutoff_witness = static_bath.bath_lagrangian(
            acceleration,
            cutoff=1.4,
            yukawa=1.2,
            rho_slope=rho,
        )
        self.assertAlmostEqual(closed, cutoff_witness, places=14)
        matter_k2 = gate.sea_quadratic_increment(1.4, 1.2, rho)
        self.assertAlmostEqual(matter_k2, 0.5 * rho * 1.4 * 1.2**2)
        self.assertAlmostEqual(
            gate.gravitational_eta_increment(matter_k2, planck5_cubed=2.3),
            2.0 * matter_k2 / 2.3,
        )

    def test_euclidean_closed_form_matches_independent_simpson_integral(self) -> None:
        intervals = 20000
        energy = np.linspace(0.0, self.kwargs["cutoff"], intervals + 1)
        spacing = self.kwargs["cutoff"] / intervals
        for omega, momentum in ((0.0, 0.0), (0.0, 0.4), (0.3, 0.0), (0.7, 0.8)):
            shift = self.kwargs["dispersion_coefficient"] * momentum * momentum / 4.0
            numerator = (
                self.kwargs["yukawa"] ** 2
                * self.kwargs["rho_slope"]
                * energy
                * 4.0
                * (energy + shift)
            )
            denominator = omega * omega + 4.0 * (energy + shift) ** 2
            values = np.divide(
                numerator,
                denominator,
                out=np.zeros_like(numerator),
                where=denominator != 0.0,
            )
            if omega == 0.0 and shift == 0.0:
                values[0] = self.kwargs["yukawa"] ** 2 * self.kwargs["rho_slope"]
            numerical = (
                spacing
                / 3.0
                * (
                    values[0]
                    + values[-1]
                    + 4.0 * np.sum(values[1:-1:2])
                    + 2.0 * np.sum(values[2:-1:2])
                )
            )
            analytic = gate.polarization_euclidean(omega, momentum, **self.kwargs)
            self.assertAlmostEqual(analytic, numerical, places=10)

    def test_complex_kernel_on_matsubara_axis_equals_euclidean_kernel(self) -> None:
        for omega in (0.03, 0.4, 2.0):
            for momentum in (0.0, 0.2, 1.0):
                complex_value = gate.polarization_complex(
                    1j * omega, momentum, quadrature_order=512, **self.kwargs
                )
                euclidean = gate.polarization_euclidean(omega, momentum, **self.kwargs)
                self.assertAlmostEqual(complex_value.imag, 0.0, places=14)
                self.assertAlmostEqual(complex_value.real, euclidean, places=13)

    def test_retarded_cut_and_spectral_weight_are_exact_and_passive(self) -> None:
        q = 0.6
        lower, upper = gate.particle_hole_cut(
            q,
            cutoff=self.kwargs["cutoff"],
            dispersion_coefficient=self.kwargs["dispersion_coefficient"],
        )
        self.assertGreater(lower, 0.0)
        for fraction in (0.1, 0.5, 0.9):
            omega = lower + fraction * (upper - lower)
            sigma = gate.polarization_spectral_weight(omega, q, **self.kwargs)
            positive = gate.polarization_retarded_real(omega, q, **self.kwargs)
            negative = gate.polarization_retarded_real(-omega, q, **self.kwargs)
            self.assertGreater(sigma, 0.0)
            self.assertAlmostEqual(positive.imag, math.pi * sigma, places=14)
            self.assertAlmostEqual(negative.real, positive.real, places=14)
            self.assertAlmostEqual(negative.imag, -positive.imag, places=14)
        self.assertEqual(
            gate.polarization_spectral_weight(0.5 * lower, q, **self.kwargs),
            0.0,
        )

    def test_static_and_temporal_deficits_are_positive(self) -> None:
        pi_zero = gate.polarization_euclidean(0.0, 0.0, **self.kwargs)
        for omega in (0.0, 0.1, 1.0):
            for q in (0.1, 0.5, 2.0):
                self.assertLess(
                    gate.polarization_euclidean(omega, q, **self.kwargs),
                    pi_zero,
                )
        expected = math.pi * self.kwargs["yukawa"] ** 2 * self.kwargs["rho_slope"] / 8.0
        omega = 1.0e-7
        actual = (
            0.5
            * (pi_zero - gate.polarization_euclidean(omega, 0.0, **self.kwargs))
            / omega
        )
        self.assertAlmostEqual(actual / expected, 1.0, places=7)

    def test_exact_euclidean_inverse_is_positive_away_from_origin(self) -> None:
        for omega in (0.0, 0.01, 0.4, 3.0):
            for q in (0.03, 0.2, 1.4):
                value = gate.matched_euclidean_inverse(
                    omega,
                    q,
                    **self.schur_kwargs,
                    **self.kwargs,
                )
                self.assertGreater(value, 0.0)

    def test_exact_schur_positive_real_theorem_has_positive_samples(self) -> None:
        rng = np.random.default_rng(20260831)
        for _ in range(24):
            p = complex(rng.uniform(0.03, 1.5), rng.uniform(-2.0, 2.0))
            q = float(rng.uniform(0.03, 1.5))
            inverse = gate.matched_laplace_inverse(
                p,
                q,
                **self.schur_kwargs,
                quadrature_order=512,
                **self.kwargs,
            )
            margin = gate.positive_real_stability_margin(
                p,
                q,
                **self.schur_kwargs,
                quadrature_order=512,
                **self.kwargs,
            )
            self.assertAlmostEqual(margin, (inverse / p).real, places=13)
            self.assertGreater(margin, 0.0)

    def test_exact_schur_retains_reciprocal_and_linearizes_correctly(self) -> None:
        pi_zero = gate.polarization_euclidean(0.0, 0.0, **self.kwargs)
        eta_inf = gate.critical_eta_infinity(
            pi_zero,
            eta_critical=self.schur_kwargs["eta_critical"],
            planck5_cubed=self.schur_kwargs["planck5_cubed"],
        )
        self.assertGreater(eta_inf, 0.0)
        pi_value = 0.6 * pi_zero
        exact = gate.geometric_schur_response(
            pi_value,
            pi_zero=pi_zero,
            eta_critical=self.schur_kwargs["eta_critical"],
            planck5_cubed=self.schur_kwargs["planck5_cubed"],
            schur_factor=self.schur_kwargs["schur_factor"],
        ).real
        a_g = self.schur_kwargs["schur_factor"] * self.schur_kwargs["eta_critical"]
        expected = a_g * (
            self.schur_kwargs["eta_critical"]
            / (eta_inf + pi_value / self.schur_kwargs["planck5_cubed"])
            - 1.0
        )
        self.assertAlmostEqual(exact, expected, places=14)
        linear = (
            self.schur_kwargs["schur_factor"]
            * (pi_zero - pi_value)
            / self.schur_kwargs["planck5_cubed"]
        )
        self.assertGreater(exact, linear)

    def test_pure_imaginary_uhp_axis_has_strictly_positive_inverse(self) -> None:
        for gamma in (1.0e-3, 0.1, 1.0, 10.0):
            for q in (0.03, 0.5, 2.0):
                value = gate.matched_retarded_inverse_complex(
                    1j * gamma,
                    q,
                    **self.schur_kwargs,
                    quadrature_order=512,
                    **self.kwargs,
                )
                self.assertAlmostEqual(value.imag, 0.0, places=13)
                self.assertGreater(value.real, 0.0)

    def test_same_action_static_scalars_fail_global_retarded_uv_gate(self) -> None:
        pi_zero = gate.polarization_euclidean(0.0, 0.0, **self.kwargs)
        same_zero = gate.same_action_continuum_polarization_euclidean(
            0.0,
            regulator_mass=self.kwargs["cutoff"],
            yukawa=self.kwargs["yukawa"],
            rho_slope=self.kwargs["rho_slope"],
        )
        self.assertAlmostEqual(same_zero, pi_zero, places=14)
        negative = gate.same_action_continuum_polarization_euclidean(
            2.0 * self.kwargs["cutoff"],
            regulator_mass=self.kwargs["cutoff"],
            yukawa=self.kwargs["yukawa"],
            rho_slope=self.kwargs["rho_slope"],
        )
        self.assertLess(negative, 0.0)
        pole = gate.same_action_continuum_uhp_pole_b4_zero(
            0.7,
            q_zeta=self.schur_kwargs["q_zeta"],
            eta_critical=self.schur_kwargs["eta_critical"],
            planck5_cubed=self.schur_kwargs["planck5_cubed"],
            schur_factor=self.schur_kwargs["schur_factor"],
            yukawa=self.kwargs["yukawa"],
            rho_slope=self.kwargs["rho_slope"],
        )
        self.assertGreater(pole["positive_UHP_laplace_pole"], pole["lapse_zero"])
        self.assertLess(pole["normalized_inverse_residual"], 2.0e-11)
        self.assertEqual(
            self.result["same_action_dynamic_red_team"]["status"],
            "KILL_MINIMAL_SAME_ACTION_GLOBAL_RETARDED_UV_COMPLETION",
        )

    def test_constraint_gate_keeps_fundamental_lapse_rank(self) -> None:
        completion = self.result["constraint_completion"]
        self.assertFalse(completion["lapse_or_shift_time_derivatives_added_by_bath"])
        self.assertEqual(completion["fermion_time_derivative_order"], 1)
        self.assertEqual(completion["fermion_spatial_derivative_order"], 2)
        self.assertGreater(completion["bare_lapse_principal_coefficient"], 0.0)
        self.assertEqual(
            completion["gravity_constraint_inventory"][
                "khronometric_gravitational_dof"
            ],
            6,
        )
        self.assertTrue(
            self.result["decision"]["fundamental_flat_constraint_rank_preserved"]
        )

    def test_finite_fifth_dimension_kills_asymptotic_cubic(self) -> None:
        reduced = gate.compactified_ir_exponents(3, 2.0)
        bulk = gate.compactified_ir_exponents(4, 2.0)
        self.assertEqual(reduced["density_of_states_power"], 0.5)
        self.assertEqual(reduced["filled_sea_nonanalytic_power"], 2.5)
        self.assertEqual(bulk["density_of_states_power"], 1.0)
        self.assertEqual(bulk["filled_sea_nonanalytic_power"], 3.0)
        obstruction = self.result["compactification_obstruction"]
        self.assertIn("first radial KK gap", obstruction["finite_interval_result"])
        self.assertEqual(
            obstruction["status"], "BLOCKS_CURRENT_COMPACT_HOLO_PHYSICAL_COMPLETION"
        )
        self.assertFalse(
            self.result["decision"]["finite_compact_HOLO_strict_IR_cubic_survives"]
        )

    def test_original_lifshitz_radial_acceleration_gaps_cubic(self) -> None:
        expansion = gate.orthogonal_gapped_static_expansion(
            1.5,
            regulator_mass=1.7,
            yukawa=1.1,
            rho_slope=self.kwargs["rho_slope"],
        )
        self.assertGreater(expansion["background_gap"], 0.0)
        self.assertGreater(expansion["quadratic_coefficient"], 0.0)
        self.assertEqual(expansion["cubic_coefficient"], 0.0)
        self.assertLess(expansion["quartic_coefficient"], 0.0)
        obstruction = self.result["lifshitz_background_obstruction"]
        self.assertEqual(
            obstruction["status"],
            "KILL_NAIVE_ISOTROPIC_ORIGINAL_LIFSHITZ_BULK_ROUTE",
        )

    def test_acceptance_ladder_closes_local_steps_but_stops_before_force(self) -> None:
        ladder = {
            row["level"]: row["status"] for row in self.result["acceptance_ladder"]
        }
        for level in (
            "Z0_local_5D_foliation_action",
            "Z1_literal_linear_bulk_DOS",
            "Z2_same_action_UV_finite_static_Clifford_sea",
            "Z3_flat_constraint_rank",
            "Z4_flat_finite_band_retarded_linear_stability",
        ):
            self.assertEqual(ladder[level], "PASS")
        self.assertEqual(ladder["Z5_finite_compact_HOLO_strict_IR"], "KILLED")
        self.assertEqual(ladder["Z4a_minimal_same_action_global_retarded_UV"], "KILLED")
        self.assertEqual(ladder["Z7_force_matter_lensing"], "NOT_ENTERED")

    def test_decision_is_stronger_without_becoming_a_physical_claim(self) -> None:
        decision = self.result["decision"]
        self.assertEqual(
            decision["verdict"],
            "LOCAL_5D_Z2_GAUSSIAN_STATIC_BATH_AND_FLAT_BANDED_CAUSAL_GATE_PASS_"
            "COMPACT_HOLO_AND_RETARDED_UV_BLOCKED",
        )
        for field in (
            "same_action_local_5D_Gaussian_static_bath_derived",
            "UV_finite_static_completion_without_hard_cutoff",
            "full_flat_finite_band_gaussian_retarded_kernel_derived",
            "retarded_branch_cut_resolved",
            "exact_metric_lapse_Schur_complement_retained",
            "critical_linear_flat_scalar_has_no_UHP_poles",
            "same_action_q0_renormalized_retarded_kernel_derived",
            "same_action_continuum_has_upper_half_plane_pole",
            "same_action_finite_q_requires_gradient_counterterm",
        ):
            with self.subTest(field=field):
                self.assertTrue(decision[field])
        for field in (
            "finite_band_retarded_regulator_derived_from_local_UV_completion",
            "same_action_local_UV_full_retarded_kernel_derived",
            "minimal_static_Gaussian_multiplet_same_action_UV_dynamics_survives",
            "critical_matching_Ward_protected",
            "naive_isotropic_original_Lifshitz_background_route_survives",
            "gapless_radial_continuum_with_4D_gravity_localization_derived",
            "nonlinear_global_time_stability_derived",
            "physical_completion",
            "new_force_derived",
            "lensing_derived",
            "publication_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(decision[field])
        self.assertTrue(self.result["checks"]["all"])
        self.assertEqual(
            self.result["sources"]["raw_observational_tables_read_directly"], []
        )

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(gate.BulkZ2InputError):
            gate.bulk_z2_dos_slope(0.0)
        with self.assertRaises(gate.BulkZ2InputError):
            gate.bulk_z2_dos_slope(1.0, flavor_count=0)
        with self.assertRaises(gate.BulkZ2InputError):
            gate.bulk_z2_clifford_spectrum([1.0, 2.0], [0.0] * 4)
        with self.assertRaises(gate.BulkZ2InputError):
            gate.polarization_euclidean(-1.0, 0.0, **self.kwargs)
        lower, _ = gate.particle_hole_cut(
            0.4,
            cutoff=self.kwargs["cutoff"],
            dispersion_coefficient=self.kwargs["dispersion_coefficient"],
        )
        with self.assertRaises(gate.BulkZ2InputError):
            gate.polarization_retarded_real(lower, 0.4, **self.kwargs)


if __name__ == "__main__":
    unittest.main()
