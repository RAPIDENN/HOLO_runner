from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory.build_master_prediction_registry import (
    OUT_JSON,
    build_registry,
)


class MasterPredictionRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build_registry()

    def test_no_detection_or_confirmation_claim(self) -> None:
        label = self.registry["global_classification"].lower()
        self.assertIn("no new physical detection", label)
        self.assertIn("no clean confirmatory holdout", label)

    def test_missing_physics_fails_closed(self) -> None:
        links = {row["id"]: row for row in self.registry["links"]}
        self.assertEqual(
            links["boundary_selects_spectrum"]["gate"],
            "blocked_missing_boundary_action",
        )
        self.assertIn("missing_ell", links["dimensionless_force_to_lab_signal"]["gate"])
        self.assertEqual(
            links["gauge_links_to_wilson_observable"]["gate"],
            "missing_su3_link_configurations",
        )
        self.assertIn(
            "missing_uv_matching", links["qcd_scale_to_compactification_length"]["gate"]
        )
        self.assertIn(
            "missing_ell", links["em_double_comb_to_clock_signal"]["gate"]
        )

    def test_boundary_adjudication_is_preserved(self) -> None:
        branches = self.registry["current_predictions"]["boundary_branches"]["branches"]
        self.assertTrue(branches["NN"]["has_exact_massless_mode"])
        self.assertLess(branches["ND"]["masses_mu"][0], 0.003)
        self.assertTrue(branches["DN"]["uv_point_probe_decouples"])
        self.assertTrue(branches["DD"]["uv_point_probe_decouples"])

    def test_comparators_are_not_cherry_picked(self) -> None:
        sparc = self.registry["current_predictions"]["sparc"]
        self.assertGreater(sparc["test_p5_vs_newton_galaxy_win_fraction"], 0.5)
        self.assertLess(sparc["test_p5_vs_rar_galaxy_win_fraction"], 0.5)
        self.assertLess(sparc["test_p5_minus_rar_delta_loglike_per_point"], 0.0)

    def test_desi_is_labeled_diagonal_diagnostic(self) -> None:
        desi = self.registry["current_predictions"]["desi_dr1_growth"]
        self.assertIn("not_confirmatory_likelihood", desi["classification"])
        self.assertGreater(desi["delta_chi2_holo_minus_lcdm"], 0.0)

    def test_eq39_is_recovered_without_calling_it_a_signal(self) -> None:
        em = self.registry["current_predictions"]["em_kernel"]
        self.assertTrue(em["eq39_coordinate_certificate"])
        self.assertGreater(em["legacy_max_abs_error_from_correct_u_kernel"], 0.3)
        self.assertIn("historical numerical kernel mixed", em["result"])

    def test_robin_and_double_comb_are_conditional_not_selected(self) -> None:
        robin = self.registry["current_predictions"]["robin_boundary_family"]
        fingerprint = self.registry["current_predictions"][
            "em_spectral_fingerprint"
        ]
        self.assertFalse(robin["physical_boundary_coefficients_selected"])
        self.assertLess(robin["ir_only_lightest_mass_ceiling"], 0.003)
        self.assertFalse(fingerprint["ell_fixed"])
        self.assertFalse(fingerprint["physical_branch_selected"])
        self.assertAlmostEqual(
            fingerprint["photon_positive_masses_mu"][0], 0.6525966736654073
        )

    def test_all_evidence_hashes_are_real(self) -> None:
        for row in self.registry["artefacts"].values():
            self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")
            self.assertFalse(row["path"].startswith("/"))

    def test_generated_file_matches_builder_when_present(self) -> None:
        if OUT_JSON.exists():
            disk = json.loads(OUT_JSON.read_text(encoding="utf-8"))
            self.assertEqual(disk, self.registry)


if __name__ == "__main__":
    unittest.main()
