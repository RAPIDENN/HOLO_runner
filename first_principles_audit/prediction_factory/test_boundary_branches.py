from __future__ import annotations

import unittest

import numpy as np

from first_principles_audit.prediction_factory.derive_boundary_branches import (
    BRANCHES,
    derive,
)


class BoundaryBranchCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_certificate_passes(self) -> None:
        self.assertTrue(self.result["passes"]["all"])

    def test_all_discrete_branches_are_present(self) -> None:
        self.assertEqual(set(self.result["branches"]), set(BRANCHES))

    def test_only_nn_has_exact_massless_mode(self) -> None:
        flags = {
            name: branch["has_exact_massless_mode"]
            for name, branch in self.result["branches"].items()
        }
        self.assertEqual(flags, {"NN": True, "ND": False, "DN": False, "DD": False})

    def test_uv_dirichlet_branches_have_zero_point_coupling(self) -> None:
        for name in ("DN", "DD"):
            beta = np.asarray(
                self.result["branches"][name]["uv_probe_couplings_beta_n"]
            )
            np.testing.assert_array_equal(beta, np.zeros(beta.size))

    def test_hard_ir_wall_leaves_an_ultralight_uv_coupled_mode(self) -> None:
        branch = self.result["branches"]["ND"]
        self.assertLess(branch["masses_mu"][0], 0.01)
        self.assertGreater(abs(branch["uv_probe_couplings_beta_n"][0]), 0.05)

    def test_positive_spectra_are_ordered(self) -> None:
        for branch in self.result["branches"].values():
            masses = np.asarray(branch["masses_mu"])
            self.assertTrue(np.all(masses > 0.0))
            self.assertTrue(np.all(np.diff(masses) > 0.0))


if __name__ == "__main__":
    unittest.main()
