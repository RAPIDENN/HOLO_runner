#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_nonlinear_swarm_adjudication as swarm,
)


class NonlinearSwarmAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = swarm.build()
        cls.routes = {row["id"]: row for row in cls.result["routes"]}

    def test_hybrid_wins_without_opening_physical_gates(self) -> None:
        self.assertTrue(self.result["checks"]["all"])
        self.assertEqual(
            self.result["selection"]["winner"], "hybrid_ADM_plus_BMP_oracle"
        )
        self.assertTrue(
            self.result["hard_gates"]["bulk_ADM_S2_compact_support_recovered"]
        )
        self.assertFalse(self.result["hard_gates"]["physical_c000_computed"])
        self.assertFalse(
            self.result["hard_gates"]["two_independent_routes_agree"]
        )

    def test_every_route_uses_same_bounded_rubric(self) -> None:
        for route in self.routes.values():
            self.assertEqual(set(route["current_points"]), set(swarm.WEIGHTS))
            self.assertEqual(
                route["current_score"], sum(route["current_points"].values())
            )
            self.assertLessEqual(route["current_score"], route["theoretical_ceiling"])
            self.assertIn("not a probability", route["warning"])

    def test_analogies_are_translated_into_falsifiers(self) -> None:
        analogies = self.result["historical_analogies_as_tests"]
        self.assertEqual(len(analogies), 5)
        self.assertTrue(all(row["translation"] and row["falsifier"] for row in analogies))
        names = {row["idea"] for row in analogies}
        self.assertIn("Einstein covariance", names)
        self.assertIn("Wilson mode elimination", names)

    def test_decisive_assay_preserves_independence_then_cooperates(self) -> None:
        assay = self.result["decisive_assay"]
        self.assertIn("not cubic kernels", assay["independence"])
        self.assertIn("share corrections", assay["collaboration_after_blind_compare"])
        self.assertEqual(assay["eta_hat_steps"], [0.001, 0.0005])

    def test_no_observational_input_or_force_claim(self) -> None:
        self.assertEqual(self.result["inputs"]["observational_tables_read"], [])
        self.assertIn("never authorized", self.result["claim_gates"]["new_force_or_observation"])

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if swarm.OUTPUT.exists():
            rendered = json.loads(swarm.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
