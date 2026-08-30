from __future__ import annotations

import unittest

from first_principles_audit.prediction_factory.evaluate_desi_dr1_growth import (
    evaluate,
)


class DesiDR1GrowthDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = evaluate()

    def test_certificate_passes(self) -> None:
        self.assertTrue(self.result["passes"]["all"])

    def test_only_in_domain_bins_are_used(self) -> None:
        self.assertEqual(
            [row["tracer"] for row in self.result["rows"]],
            ["BGS", "LRG1", "LRG2", "LRG3"],
        )
        self.assertEqual(
            set(self.result["comparison_rule"]["excluded_bins"]),
            {"ELG2_z_1.32", "QSO_z_1.49"},
        )

    def test_frozen_values_reproduce_the_diagnostic(self) -> None:
        summary = self.result["summary"]
        self.assertAlmostEqual(summary["diagonal_chi2_holo"], 2.6917155667, places=8)
        self.assertAlmostEqual(summary["diagonal_chi2_lcdm"], 2.4188584350, places=8)
        self.assertAlmostEqual(
            summary["delta_chi2_holo_minus_lcdm"], 0.2728571317, places=8
        )

    def test_no_preference_is_claimed(self) -> None:
        self.assertIn("does not favour HOLO", self.result["summary"]["interpretation"])
        self.assertIn("not the official DESI likelihood", self.result["evidence_boundary"])


if __name__ == "__main__":
    unittest.main()
