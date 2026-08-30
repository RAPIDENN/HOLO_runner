from __future__ import annotations

import json
import unittest

from first_principles_audit.verify_minimal_probe_completion_shooting import (
    POSITIVE_MODE_COUNT,
    verify,
)


class MinimalProbeCompletionShootingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify()

    def test_verification_is_blind_to_observations(self) -> None:
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertEqual(self.result["target_observational_inputs_declared"], [])
        self.assertTrue(self.result["passes"]["observational_blinding"])

    def test_solver_is_independent_of_fem_implementation(self) -> None:
        method = self.result["method"]
        self.assertFalse(method["primary_solver_reused"])
        self.assertFalse(method["fem_matrix_reused"])
        self.assertIn("DOP853", method["integrator"])
        self.assertIn("Brent", method["root_finder"])

    def test_six_positive_neumann_modes_have_sturm_node_order(self) -> None:
        self.assertEqual(len(self.result["modes"]), POSITIVE_MODE_COUNT)
        self.assertEqual(
            self.result["summary"]["node_counts"],
            list(range(1, POSITIVE_MODE_COUNT + 1)),
        )
        self.assertTrue(self.result["passes"]["right_neumann_boundary"])

    def test_masses_match_primary_fem_with_preregistered_tolerance(self) -> None:
        self.assertLessEqual(
            self.result["summary"]["mass_relative_error_max"],
            self.result["criteria"]["mass_relative_error_max"],
        )
        self.assertTrue(self.result["passes"]["positive_masses_match"])

    def test_uv_couplings_match_primary_fem_with_preregistered_tolerance(self) -> None:
        self.assertLessEqual(
            self.result["summary"]["uv_coupling_relative_error_max"],
            self.result["criteria"]["uv_coupling_relative_error_max"],
        )
        self.assertTrue(self.result["passes"]["positive_uv_couplings_match"])
        self.assertTrue(self.result["passes"]["zero_mode_uv_coupling_match"])

    def test_payload_is_machine_readable_and_certificate_passes(self) -> None:
        encoded = json.dumps(self.result, allow_nan=False)
        self.assertIsInstance(json.loads(encoded), dict)
        self.assertTrue(self.result["passes"]["all"])


if __name__ == "__main__":
    unittest.main()
