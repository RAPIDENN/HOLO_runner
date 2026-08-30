#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import derive_collector_legendre_envelope as envelope
except ModuleNotFoundError:
    import derive_collector_legendre_envelope as envelope


class CollectorLegendreEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = envelope.build()

    def test_upper_envelope_selects_affine_branch(self) -> None:
        X = np.array([0.25, 1.0, 4.0])
        states = np.array([0.25, 0.5, 0.75])
        W = np.array([0.01, 0.1, 1.0])
        values, selectors, peak = envelope.upper_envelope(X, states, W)
        brute = X[:, None] * states[None, :] - W[None, :]
        np.testing.assert_allclose(values, np.max(brute, axis=1))
        np.testing.assert_allclose(selectors, states[np.argmax(brute, axis=1)])
        self.assertGreater(peak, 0)

    def test_interlaced_envelope_recovers_collector_action(self) -> None:
        diagnostics = self.result["diagnostics"]
        self.assertLess(diagnostics["maximum_envelope_relative_error"], 2.0e-4)
        self.assertLess(diagnostics["maximum_selector_relative_error"], 6.0e-3)

    def test_deep_dual_is_cubic(self) -> None:
        diagnostics = self.result["diagnostics"]
        self.assertAlmostEqual(diagnostics["deep_dual_log_slope"], 3.0, delta=3.0e-3)
        self.assertAlmostEqual(
            diagnostics["deep_dual_cubic_coefficient"], 1.0 / 3.0, delta=2.0e-3
        )

    def test_representation_is_not_mislabelled_as_holo_derivation(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertIn("microscopic_holo_selector_not_yet_derived", self.result["classification"])
        self.assertFalse(self.result["source"]["raw_sparc_or_vobs_read"])
        self.assertIn("new_unproved_link", self.result["holo_bridge_hypothesis"])

    def test_memory_is_bounded(self) -> None:
        self.assertLess(self.result["diagnostics"]["peak_branch_matrix_mib"], 8.0)


if __name__ == "__main__":
    unittest.main()
