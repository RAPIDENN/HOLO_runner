from __future__ import annotations

import unittest

from first_principles_audit.audit_ricci_wilson_interface import audit


class RicciWilsonInterfaceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = audit()

    def test_certificate_passes_without_observational_inputs(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertEqual(self.result["observational_inputs_read"], [])

    def test_ricci_has_independent_trace_identity(self) -> None:
        ricci = self.result["ricci_5d"]
        self.assertLess(ricci["identity_max_abs_error"], 1e-10)
        self.assertLess(
            ricci["stored_derivative_relation_max_abs_error"], 2e-3
        )

    def test_ricci_agrees_in_domain_wall_and_conformal_coordinates(self) -> None:
        coordinate = self.result["ricci_5d"]["conformal_coordinate"]
        self.assertEqual(coordinate["definition"], "dz_c/du=exp(-A)")
        self.assertLess(coordinate["max_abs_error_vs_domain_wall"], 1e-10)

    def test_legacy_clock_curvature_is_not_the_corrected_curvature(self) -> None:
        ricci = self.result["ricci_5d"]
        self.assertGreater(ricci["legacy_minus_corrected_R5_rms"], 10.0)
        self.assertLess(
            ricci["legacy_R5_reproduced_by_mislabeled_dA_rms"], 0.01
        )

    def test_legacy_cosmology_factor_is_degenerate(self) -> None:
        counts = self.result["ricci_5d"]["legacy_E_unique_values_and_counts"]
        self.assertEqual(len(counts), 2)
        self.assertEqual(max(row["count"] for row in counts), 526)

    def test_wilson_label_is_only_an_arithmetic_proxy(self) -> None:
        wilson = self.result["wilson_scale"]
        self.assertIn("no rectangular W(R,T)", wilson["legacy_not_measured"])
        arithmetic = wilson["legacy_arithmetic"]
        self.assertAlmostEqual(
            arithmetic["sigma_recomputed_GeV2"],
            arithmetic["sigma_reported_GeV2"],
            places=14,
        )

    def test_canonical_string_frame_has_no_smooth_minimum(self) -> None:
        orientations = self.result["wilson_scale"][
            "conditional_string_frame_audit"
        ]["orientations"]
        self.assertEqual(orientations["plus"]["interior_minima_u"], [])
        self.assertEqual(orientations["minus"]["interior_minima_u"], [])

    def test_lock5_is_a_circular_historical_calibration(self) -> None:
        lock5 = self.result["legacy_lock5"]
        self.assertEqual(
            lock5["classification"],
            "circular_calibration_not_independent_lock",
        )
        self.assertEqual(
            lock5["stored_fit"]["reconstructed_target_mHz"],
            lock5["target_values"]["f_earth_mHz"],
        )
        self.assertEqual(lock5["stored_fit"]["reported_relative_error"], 0.0)
        self.assertIn("R4=0", lock5["curvature_mismatch"])


if __name__ == "__main__":
    unittest.main()
