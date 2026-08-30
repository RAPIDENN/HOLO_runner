from __future__ import annotations

import unittest

from first_principles_audit.derive_interface_action import derive


class InterfaceActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_derivation_is_blind_to_observations(self) -> None:
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertTrue(self.result["passes"]["blind_to_observations"])

    def test_geometry_fixed_carrier_is_ghost_free(self) -> None:
        passes = self.result["passes"]
        self.assertTrue(passes["A_uu_strictly_negative"])
        self.assertTrue(passes["positive_carrier_weights"])
        self.assertTrue(passes["finite_positive_carrier_integrals"])

    def test_local_superpotential_closes(self) -> None:
        self.assertTrue(self.result["passes"]["superpotential_identities"])
        metrics = self.result["identity_metrics"]
        self.assertLessEqual(
            max(metrics.values()), self.result["criteria"]["identity_max_abs"]
        )

    def test_neumann_zero_mode_is_only_a_labelled_trial(self) -> None:
        trial = self.result["neumann_trial"]
        self.assertTrue(self.result["passes"]["neumann_constant_mode_normalized"])
        self.assertIn("trial", trial["completion"].lower())
        self.assertIn("not a physical prediction", trial["interpretation"])

    def test_missing_physical_choices_are_explicit(self) -> None:
        choices = " ".join(self.result["unfixed_choices"])
        for required in (
            "boundary",
            "kappa_5",
            "mass scale",
            "localization",
            "beta",
            "d_e",
            "d_g",
        ):
            self.assertIn(required, choices)

    def test_complete_interface_certificate_passes(self) -> None:
        self.assertTrue(self.result["passes"]["all"])


if __name__ == "__main__":
    unittest.main()
