from __future__ import annotations

import math
import unittest

from first_principles_audit.prediction_factory.derive_em_kernel_completion import (
    build,
    conformal_coordinate_from_domain_wall,
    normalized_bulk_photon_kernel,
    normalized_domain_wall_photon_kernel,
    trapz,
)


class EmKernelCompletionTests(unittest.TestCase):
    def test_general_kernel_normalizes(self) -> None:
        z = [0.0, 0.2, 0.7, 1.0]
        kernel = normalized_bulk_photon_kernel(
            z,
            [0.0, -0.1, -0.4, -0.8],
            [1.0, 1.2, 1.5, 2.0],
            [1.0, 0.9, 0.8, 0.7],
        )
        self.assertAlmostEqual(trapz(kernel, z), 1.0, places=14)
        self.assertTrue(all(value > 0.0 for value in kernel))

    def test_eq39_is_exact_special_case(self) -> None:
        artifact = build()
        special = artifact["bulk_maxwell_branch"]["eq39_special_case"]
        self.assertTrue(special["coordinate_certificate"]["passes"])
        self.assertIn("Z(chi)=1", special["assumptions"])
        self.assertIn("flat", special["assumptions"][2])
        self.assertGreater(
            special["coordinate_certificate"]["conformal_span"], 4.9
        )

    def test_domain_wall_kernel_is_uniform_for_minimal_flat_mode(self) -> None:
        kernel = normalized_domain_wall_photon_kernel(
            [0.0, 0.2, 0.7, 1.0],
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
        )
        self.assertTrue(all(abs(value - 1.0) < 1.0e-14 for value in kernel))

    def test_nonpositive_gauge_kinetic_fails(self) -> None:
        with self.assertRaises(ValueError):
            normalized_bulk_photon_kernel(
                [0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0]
            )

    def test_zero_photon_mode_fails(self) -> None:
        with self.assertRaises(ValueError):
            normalized_bulk_photon_kernel(
                [0.0, 1.0], [0.0, 0.0], [1.0, 1.0], [0.0, 0.0]
            )

    def test_kernel_does_not_claim_signal(self) -> None:
        artifact = build()
        boundary = artifact["observable_boundary"]
        self.assertIn(
            "an observed scalar-photon coupling amplitude",
            boundary["kernel_is_not"],
        )
        self.assertIn(
            "independent acquisition session",
            boundary["required_before_dimensional_prediction"][-1],
        )
        self.assertTrue(artifact["passes"]["no_free_c_gamma_fitted"])
        self.assertTrue(artifact["passes"]["no_observational_series_read"])

    def test_conformal_and_domain_wall_measures_match_algebraically(self) -> None:
        bulk = build()["bulk_maxwell_branch"]
        equivalent = bulk["conformal_gauge"]
        self.assertEqual(equivalent["coordinate_relation"], "du=exp(A) dz_c")
        self.assertEqual(equivalent["measure_identity"], "K_u du=K_z dz_c")
        certificate = bulk["eq39_special_case"]["coordinate_certificate"]
        self.assertLess(
            certificate["cumulative_measure_max_abs_difference"], 1.0e-9
        )

    def test_historical_coordinate_mix_is_exposed_not_relabelled(self) -> None:
        artifact = build()
        audit = artifact["historical_artifact_audit"]
        self.assertGreater(
            audit["max_abs_difference_from_uniform_domain_wall_kernel"], 0.3
        )
        self.assertIn("identity by construction", audit["old_2e_minus_16_claim"])
        self.assertTrue(artifact["passes"]["legacy_coordinate_mismatch_exposed"])

    def test_conformal_coordinate_is_constructed_not_reused(self) -> None:
        z = conformal_coordinate_from_domain_wall(
            [0.0, 0.5, 1.0], [0.0, -0.2, -0.5]
        )
        self.assertEqual(z[0], 0.0)
        self.assertGreater(z[-1], 1.0)
        self.assertGreater(z[2], z[1])

    def test_inputs_must_be_finite_and_monotone(self) -> None:
        with self.assertRaises(ValueError):
            normalized_bulk_photon_kernel(
                [0.0, 0.0], [0.0, 0.0], [1.0, 1.0], [1.0, 1.0]
            )
        with self.assertRaises(ValueError):
            normalized_bulk_photon_kernel(
                [0.0, 1.0], [0.0, math.nan], [1.0, 1.0], [1.0, 1.0]
            )


if __name__ == "__main__":
    unittest.main()
