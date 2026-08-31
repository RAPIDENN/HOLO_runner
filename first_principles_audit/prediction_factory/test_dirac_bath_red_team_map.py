from __future__ import annotations

import json
import math
import unittest

from first_principles_audit.prediction_factory import (
    derive_dirac_bath_red_team_map as red_team,
)
from first_principles_audit.prediction_factory import (
    derive_dirac_critical_bath_gate as bath,
)


class DiracBathRedTeamMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = red_team.build()
        cls.threats = {
            threat["id"]: threat for threat in cls.result["threats"]
        }

    def test_attack_surface_has_seventeen_unique_ids_and_all_priorities(self) -> None:
        rows = self.result["threats"]
        ids = [row["id"] for row in rows]
        numbers = sorted(int(threat_id[2:4]) for threat_id in ids)
        self.assertEqual(len(rows), 17)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(numbers, list(range(1, 18)))
        self.assertEqual({row["priority"] for row in rows}, {"P0", "P1", "P2"})
        self.assertEqual(self.result["summary"]["threat_count"], 17)
        self.assertTrue(self.result["checks"]["threat_ids_unique"])
        self.assertTrue(self.result["checks"]["all_priorities_present"])

    def test_static_algebra_attacks_are_closed(self) -> None:
        for threat_id in (
            "RT01_determinant_factor_and_sign",
            "RT02_static_energy_instability",
        ):
            with self.subTest(threat_id=threat_id):
                threat = self.threats[threat_id]
                self.assertEqual(threat["priority"], "P0")
                self.assertEqual(threat["status"], "CLOSED")
                self.assertFalse(threat["blocks_physical_completion"])
                self.assertTrue(threat["executable_evidence"])

    def test_rt03_through_rt07_are_blocking_p0_attacks(self) -> None:
        expected_status = {
            "RT03_finite_spectrum_order_of_limits": "CONFIRMED_BLOCKER",
            "RT04_gapless_temporal_kernel": "CONFIRMED_BLOCKER",
            "RT05_unprotected_quadratic_matching": "CONFIRMED_BLOCKER",
            "RT06_current_5D_DOS_origin": "CONFIRMED_BLOCKER",
            "RT07_nonzero_physical_hopping": "OPEN_BLOCKER",
        }
        for threat_id, status in expected_status.items():
            with self.subTest(threat_id=threat_id):
                threat = self.threats[threat_id]
                self.assertEqual(threat["priority"], "P0")
                self.assertEqual(threat["status"], status)
                self.assertTrue(threat["blocks_physical_completion"])
                self.assertTrue(threat["kill_criterion"])
                self.assertTrue(threat["closure_evidence"])
        self.assertTrue(self.result["checks"]["p0_has_confirmed_blockers"])

    def test_acceptance_ladder_stops_after_uniform_static_spectral_level(self) -> None:
        ladder = [
            (row["level"], row["status"])
            for row in self.result["acceptance_ladder"]
        ]
        self.assertEqual(
            ladder,
            [
                ("L0_algebra", "PASS"),
                ("L1_uniform_static_spectral", "PASS"),
                ("L2_finite_local_QFT", "BLOCKED"),
                ("L3_causal_covariant_dynamics", "BLOCKED"),
                ("L4_current_HOLO_origin", "BLOCKED"),
                ("L5_physical_force_and_lensing", "BLOCKED"),
            ],
        )
        self.assertEqual(
            self.result["summary"]["highest_level_passed"],
            "L1_uniform_static_spectral",
        )
        self.assertEqual(
            self.result["summary"]["first_blocked_level"],
            "L2_finite_local_QFT",
        )

    def test_finite_tower_attack_is_executable(self) -> None:
        levels = [0.2, 0.7, 1.4]
        weights = [0.5, 0.3, 0.2]
        low, high = 1.0e-6, 1.0e-5
        low_remainder = abs(
            bath.discrete_critical_remainder(low, levels, weights)
        )
        high_remainder = abs(
            bath.discrete_critical_remainder(high, levels, weights)
        )
        quartic_power = math.log(high_remainder / low_remainder) / math.log(
            high / low
        )
        low_zero = bath.discrete_bath_lagrangian(low, [0.0], [1.0])
        high_zero = bath.discrete_bath_lagrangian(high, [0.0], [1.0])
        linear_power = math.log(high_zero / low_zero) / math.log(high / low)
        self.assertAlmostEqual(quartic_power, 4.0, places=12)
        self.assertAlmostEqual(linear_power, 1.0, places=12)
        self.assertTrue(self.result["checks"]["finite_tower_attack_is_executable"])
        self.assertEqual(
            self.threats["RT03_finite_spectrum_order_of_limits"][
                "executable_evidence"
            ],
            [
                "diagnostics.finite_positive_tower_critical_power",
                "diagnostics.finite_tower_zero_mode_power",
            ],
        )

    def test_temporal_nonanalyticity_attack_is_executable(self) -> None:
        low, high = 1.0e-9, 1.0e-8
        low_deficit = bath.temporal_kernel_deficit(low)
        high_deficit = bath.temporal_kernel_deficit(high)
        power = math.log(high_deficit / low_deficit) / math.log(high / low)
        self.assertAlmostEqual(power, 1.0, places=7)
        self.assertTrue(self.result["checks"]["temporal_attack_is_executable"])
        self.assertEqual(
            self.threats["RT04_gapless_temporal_kernel"][
                "executable_evidence"
            ],
            ["diagnostics.gapless_temporal_kernel_power"],
        )

    def test_target_genealogy_is_inherited_without_raw_tables(self) -> None:
        sources = self.result["sources"]
        self.assertEqual(
            sources["inherited_target_origin"], "SPARC training split only"
        )
        self.assertEqual(sources["raw_observational_tables_read_directly"], [])
        self.assertIn("inherits a SPARC training fit", self.result["evidence_boundary"])
        self.assertIn("no raw observation table", self.result["evidence_boundary"])

    def test_no_physical_or_publication_promotion(self) -> None:
        decision = self.result["decision"]
        self.assertTrue(decision["static_spectral_construction_survives"])
        for field in (
            "finite_local_qft_survives",
            "causal_covariant_completion_survives",
            "current_holo_mechanism",
            "physical_completion",
            "publication_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(decision[field])
        self.assertTrue(self.result["checks"]["source_has_no_physical_completion"])
        self.assertTrue(self.result["checks"]["no_attack_promotes_publication"])
        self.assertTrue(self.result["checks"]["all"])

    def test_stored_artifact_equals_fresh_builder(self) -> None:
        stored = json.loads(red_team.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.result)


if __name__ == "__main__":
    unittest.main()
