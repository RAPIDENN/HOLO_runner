from __future__ import annotations

import unittest

from first_principles_audit.reconstruct_holo_effective_action import reconstruct


class EffectiveReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary, cls.artifact = reconstruct()

    def test_frozen_geometry_is_preserved(self) -> None:
        passes = self.summary["passes"]
        self.assertTrue(passes["input_hash"])
        self.assertTrue(passes["A_profile_preserved"])
        self.assertTrue(passes["phi_profile_preserved"])

    def test_effective_scalar_has_no_kinetic_ghost(self) -> None:
        self.assertTrue(self.summary["passes"]["positive_kinetic_function"])
        self.assertGreater(self.summary["ranges"]["kinetic_K"][0], 0.0)

    def test_both_field_representations_close(self) -> None:
        self.assertTrue(self.summary["passes"]["noncanonical_equations"])
        self.assertTrue(self.summary["passes"]["canonical_equations"])

    def test_operational_deformation_is_recovered(self) -> None:
        metrics = self.summary["preservation_metrics"]
        self.assertTrue(self.summary["passes"]["operational_delta_recovered"])
        self.assertGreater(metrics["delta_correlation"], 0.999999)
        self.assertLess(metrics["delta_rms"], 1e-3)

    def test_complete_certificate_passes(self) -> None:
        self.assertTrue(self.summary["passes"]["all"])


if __name__ == "__main__":
    unittest.main()
