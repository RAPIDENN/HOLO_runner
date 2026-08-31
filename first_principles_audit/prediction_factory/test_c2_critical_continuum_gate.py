#!/usr/bin/env python3

from __future__ import annotations

import copy
import hashlib
import json
import math
import unittest

from first_principles_audit.prediction_factory import (
    derive_c2_critical_continuum_gate as gate,
)


class C2CriticalContinuumGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = json.loads(gate.SPECTRAL_CERTIFICATE.read_text(encoding="utf-8"))
        cls.result = gate.build()

    def adjudicate(self, source: dict[str, object]) -> dict[str, object]:
        return gate.adjudicate(
            source,
            source_path="frozen/spectral.json",
            source_sha256="0" * 64,
        )

    def test_source_is_content_addressed_and_zero_data(self) -> None:
        receipt = self.result["sources"]["spectral_certificate"]
        expected = hashlib.sha256(gate.SPECTRAL_CERTIFICATE.read_bytes()).hexdigest()
        self.assertEqual(receipt["sha256"], expected)
        self.assertEqual(receipt["schema"], gate.SOURCE_SCHEMA)
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertFalse(self.result["declared_scope"]["target_blind"])
        self.assertFalse(self.result["declared_scope"]["parameter_fitting"])

    def test_current_compact_spectrum_triggers_exact_three_part_kill(self) -> None:
        conditions = self.result["kill_conditions"]
        self.assertTrue(conditions["finite_discrete_gapped_current_spectrum"])
        self.assertTrue(conditions["three_halves_is_only_a_narrow_mimic"])
        self.assertTrue(conditions["local_nonlinear_amplitude_reduction_absent"])
        self.assertTrue(conditions["all"])
        self.assertEqual(self.result["decision"]["verdict"], "KILL_C2")
        self.assertEqual(self.result["campaign_transition"], "UNLOCK_C3")

    def test_gap_and_discreteness_are_specific_to_seven_frozen_poles(self) -> None:
        evidence = self.result["evidence"]
        self.assertEqual(evidence["frozen_pole_count"], 7)
        self.assertFalse(evidence["gapless_continuum_present"])
        self.assertFalse(evidence["constant_positive_density_per_mass_derived"])
        self.assertEqual(
            evidence["source_old_model_statement"], gate.FROZEN_MODEL_STATEMENT
        )

    def test_three_halves_match_is_only_the_declared_narrow_window(self) -> None:
        width = self.result["evidence"]["three_halves_mimic_width_dex"]
        self.assertAlmostEqual(width, 0.21001750145845488)
        self.assertLess(width, gate.MIMIC_WIDTH_LIMIT_DEX)

    def test_momentum_continuum_is_not_a_local_amplitude_reduction(self) -> None:
        evidence = self.result["evidence"]
        self.assertFalse(evidence["local_amplitude_reduction_derived"])
        self.assertIn(
            "nonlocal fractional operator", evidence["source_locality_warning"]
        )
        self.assertIn("not present", evidence["source_locality_warning"])

    def test_each_kill_fact_is_independently_necessary(self) -> None:
        alternatives = []

        gapless = copy.deepcopy(self.source)
        gapless["physical_gates"][
            "gapless_continuum_present_in_current_compact_spectrum"
        ] = True
        alternatives.append(gapless)

        broad = copy.deepcopy(self.source)
        broad["current_seven_mode_test"][
            "within_0p05_log10_width_dex"
        ] = gate.MIMIC_WIDTH_LIMIT_DEX
        alternatives.append(broad)

        local = copy.deepcopy(self.source)
        local["physical_gates"][
            "momentum_spectral_continuum_reduced_to_local_amplitude_operator"
        ] = True
        alternatives.append(local)

        for source in alternatives:
            with self.subTest(source=source):
                result = self.adjudicate(source)
                self.assertFalse(result["kill_conditions"]["all"])
                self.assertEqual(
                    result["decision"]["verdict"],
                    "C2_NOT_KILLED_BY_THIS_GATE",
                )
                self.assertEqual(result["campaign_transition"], "HOLD_C2")

    def test_verdict_is_not_a_universal_no_go(self) -> None:
        decision = self.result["decision"]
        self.assertTrue(decision["kill_current_frozen_compact_spectrum"])
        self.assertFalse(decision["kill_all_critical_continuum_models"])
        self.assertFalse(self.result["declared_scope"]["universal_no_go_claimed"])
        self.assertEqual(
            set(self.result["outside_scope_live_classes"]),
            {
                "decompactified_gapless_continuum",
                "critical_boundary_limit",
                "non_gaussian_collective_constraint",
            },
        )

    def test_observational_or_uncertified_source_fails_closed(self) -> None:
        observational = copy.deepcopy(self.source)
        observational["sources"]["observational_inputs_read"] = ["table.csv"]
        with self.assertRaisesRegex(
            gate.SpectralCertificateError, "observational_inputs_read"
        ):
            self.adjudicate(observational)

        uncertified = copy.deepcopy(self.source)
        uncertified["checks"]["all"] = False
        with self.assertRaisesRegex(gate.SpectralCertificateError, "do not pass"):
            self.adjudicate(uncertified)

    def test_malformed_or_nonfinite_source_fails_closed(self) -> None:
        wrong_schema = copy.deepcopy(self.source)
        wrong_schema["schema"] = "holo.collective-spectral-bridge.v2"
        with self.assertRaisesRegex(gate.SpectralCertificateError, "schema"):
            self.adjudicate(wrong_schema)

        nonfinite = copy.deepcopy(self.source)
        nonfinite["current_seven_mode_test"]["within_0p05_log10_width_dex"] = math.nan
        with self.assertRaisesRegex(gate.SpectralCertificateError, "finite numeric"):
            self.adjudicate(nonfinite)

    def test_generated_artifact_matches_fresh_builder(self) -> None:
        stored = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
