from __future__ import annotations

import json
import unittest

import numpy as np

from first_principles_audit.prediction_factory.derive_em_spectral_fingerprint import (
    BOUNDARIES,
    EFFECTIVE,
    OUTPUT,
    REPO,
    build,
    scalar_photon_coefficient_and_slope,
)


class EmSpectralFingerprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_full_certificate_passes_without_observations(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertEqual(self.result["observational_inputs_read"], [])
        self.assertIsNone(self.result["scale_rule"]["ell"])
        self.assertTrue(self.result["passes"]["no_branch_selected"])

    def test_scalar_lapse_vertex_cancels_four_dimensional_trace(self) -> None:
        check = self.result["determinant_vertex_check"]
        self.assertTrue(check["passes"])
        self.assertLess(abs(check["pure_four_dimensional_trace_derivative"]), 1.0e-10)
        self.assertLess(check["absolute_error"], 2.0e-8)

    def test_nn_fingerprint_matches_frozen_values(self) -> None:
        modes = self.result["scalar_boundary_branches"]["NN"]["modes"]
        self.assertEqual(modes[0]["mu_scalar"], 0.0)
        self.assertEqual(modes[0]["d_gamma_at_c0"], 0.0)
        self.assertAlmostEqual(modes[1]["mu_scalar"], 0.9138989815715508)
        self.assertAlmostEqual(modes[1]["d_gamma_at_c0"], 3.9456343150046416)
        self.assertLess(modes[2]["d_gamma_at_c0"], 0.0)

    def test_mode_sign_drops_out_of_source_to_alpha_product(self) -> None:
        effective = json.loads((REPO / EFFECTIVE).read_text(encoding="utf-8"))
        boundary = json.loads((REPO / BOUNDARIES).read_text(encoding="utf-8"))
        u = np.asarray(effective["u"], dtype=float)
        warp_u = np.asarray(effective["A_u"], dtype=float)
        chi = np.asarray(effective["canonical_chi"], dtype=float)
        warp_a = np.asarray(effective["A"], dtype=float)
        root = float(np.sqrt(np.trapezoid(np.exp(2.0 * warp_a), u) / 3.0))
        profile = np.asarray(boundary["branches"]["NN"]["profiles"][0])
        beta = float(boundary["branches"]["NN"]["uv_probe_couplings_beta_n"][0])
        d_plus, _ = scalar_photon_coefficient_and_slope(
            u, warp_u, chi, profile, root
        )
        d_minus, _ = scalar_photon_coefficient_and_slope(
            u, warp_u, chi, -profile, root
        )
        self.assertAlmostEqual(beta * d_plus, (-beta) * d_minus, places=13)

    def test_uv_dirichlet_source_has_zero_cross_channel_transfer(self) -> None:
        for code in ("DN", "DD"):
            modes = self.result["scalar_boundary_branches"][code]["modes"]
            self.assertTrue(
                all(row["source_to_delta_ln_alpha_per_U"] == 0.0 for row in modes)
            )

    def test_bulk_photon_has_independently_checked_double_comb(self) -> None:
        tower = self.result["bulk_photon_tower"]
        modes = tower["modes"]
        self.assertEqual(modes[0]["mu_gamma"], 0.0)
        self.assertAlmostEqual(modes[1]["mu_gamma"], 0.6525966736654073)
        self.assertAlmostEqual(
            modes[1]["uv_charge_coupling_squared_relative_to_zero_mode"],
            0.6193584713405876,
        )
        self.assertLess(
            max(tower["independent_shooting"]["relative_errors"]), 2.0e-5
        )

    def test_hellmann_feynman_and_grid_checks_are_visible(self) -> None:
        metrics = self.result["metrics"]
        self.assertLess(
            metrics["photon"]["hf_finite_difference_relative_max"], 5.0e-6
        )
        self.assertLess(
            metrics["scalar"]["d_quarter_grid_relative_max"], 4.0e-3
        )

    def test_input_paths_are_portable(self) -> None:
        for row in self.result["inputs"].values():
            self.assertFalse(row["path"].startswith("/"))
            self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")

    def test_generated_file_matches_builder_when_present(self) -> None:
        if OUTPUT.exists():
            stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(stored, self.result)


if __name__ == "__main__":
    unittest.main()
