from __future__ import annotations

import unittest

from first_principles_audit.prediction_factory.verify_nd_ultralight_shooting import (
    verify,
)


class NDUltralightShootingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify()

    def test_certificate_passes(self) -> None:
        self.assertTrue(self.result["passes"]["all"])

    def test_root_is_ultralight_and_not_zero(self) -> None:
        self.assertGreater(self.result["mass_mu"], 0.0)
        self.assertLess(self.result["mass_mu"], 0.01)

    def test_independent_mass_and_coupling_match(self) -> None:
        self.assertLess(self.result["mass_relative_error"], 2.0e-4)
        self.assertLess(self.result["beta_relative_error"], 2.0e-4)

    def test_no_observational_input(self) -> None:
        self.assertEqual(self.result["observational_inputs_read"], [])


if __name__ == "__main__":
    unittest.main()
