#!/usr/bin/env python3
"""Mutation tests for the fail-closed one-Omega action charter."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from . import derive_one_omega_action_charter_gate as gate


class OneOmegaActionCharterGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = gate.build_payload()

    @staticmethod
    def _rebind(payload: dict) -> None:
        payload["action_charter_digest"]["sha256"] = gate._canonical_digest(
            payload["action_charter"]
        )
        core = {key: payload[key] for key in gate.DIGEST_KEYS}
        payload["calculation_digest"]["sha256"] = gate._canonical_digest(core)

    def test_schema_route_and_acyclic_direct_DAG(self) -> None:
        self.assertEqual(
            self.payload["schema"], "holo.one-omega-action-charter-gate.v1"
        )
        self.assertEqual(
            set(gate.UPSTREAM_PATHS),
            {"backreacted_wall", "wall_ADM", "nonlinear_Robin_full_V4"},
        )
        joined = " ".join(str(path) for path in gate.UPSTREAM_PATHS.values())
        self.assertNotIn("radial_p3", joined)
        self.assertNotIn("radial_nonlinear_gravity_p4", joined)
        charter = self.payload["action_charter"]
        self.assertEqual(charter["route_id"], gate.ROUTE_ID)
        self.assertEqual(charter["selection"]["bulk_compensator_count"], 1)
        self.assertEqual(
            charter["selection"]["solder_route"],
            "three brane Stueckelberg solid scalars X^a",
        )
        self.assertTrue(
            charter["selection"]["canonical_genealogy_selected_for_C1_and_N1"]
        )
        self.assertFalse(charter["selection"]["old_P3_gate_automatically_updated"])

    def test_every_parameter_is_a_single_frozen_number(self) -> None:
        policy = self.payload["action_charter"]["coefficient_policy"]
        self.assertEqual(set(policy["parameters"]), set(gate.FROZEN_PARAMETERS))
        for key, expected in gate.FROZEN_PARAMETERS.items():
            self.assertAlmostEqual(policy["parameters"][key], expected, places=14)
        self.assertEqual(policy["parameters"]["material_Z5_per_side"], 1.0)
        self.assertEqual(
            policy["parameters"]["M4_bulk_squared_selected_one_Omega_wall_value"],
            1.107013790800849,
        )
        self.assertEqual(policy["all_unlisted_operator_coefficients_at_mu_star"], 0.0)
        self.assertFalse(policy["radiative_closure_proved"])
        self.assertFalse(policy["UV_derivation_claimed"])

    def test_configuration_and_variation_gluing_are_explicit(self) -> None:
        domains = self.payload["action_charter"]["domains"]
        self.assertEqual(domains["interface_gluing"], gate.CANONICAL_GLUING)
        self.assertIn("gamma^+", domains["interface_gluing"]["configuration_metric"])
        self.assertIn("delta gamma^+", domains["interface_gluing"]["variation_metric"])
        self.assertIn("Omega_+(Y_+)", domains["interface_gluing"]["configuration_Omega"])
        self.assertIn("phi_+^a(Y_+)", domains["interface_gluing"]["configuration_phi"])
        self.assertTrue(domains["gluing_is_a_restricted_domain_not_a_multiplier_equation"])
        self.assertIn("no gluing Lagrange multiplier", gate.CANONICAL_GLUING["implementation"])

    def test_gluing_mutations_fail_after_digest_rebinding(self) -> None:
        for key in (
            "configuration_metric",
            "variation_metric",
            "configuration_Omega",
            "variation_phi",
        ):
            mutated = copy.deepcopy(self.payload)
            mutated["action_charter"]["domains"]["interface_gluing"][key] += " changed"
            self._rebind(mutated)
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    gate.OneOmegaActionCharterError, "interface gluing"
                ):
                    gate.validate_payload(mutated)

    def test_exact_action_indices_and_shear_are_literal(self) -> None:
        charter = self.payload["action_charter"]
        self.assertEqual(charter["exact_action"], gate.CANONICAL_ACTION)
        self.assertFalse(gate._contains_ellipsis(charter))
        self.assertEqual(
            charter["domains"]["khronon"],
            "-gamma^(mu nu)*D_mu T*D_nu T>0 with a global time orientation",
        )
        self.assertEqual(
            charter["definitions"]["triad_spatial_identity"],
            "sum_a E^(a mu)*E^(a nu)=h^(mu nu)",
        )
        self.assertIn("tr[(B-v^2*I)^2]", charter["exact_action"]["solid"])
        self.assertIn("Z5_per_side*M^2*Omega^(-5)", charter["exact_action"]["bulk"])

    def test_index_mutations_fail_after_digest_rebinding(self) -> None:
        mutations = (
            ("domains", "khronon", "-gamma^mu_nu*D_mu T*D_nu T>0"),
            (
                "definitions",
                "triad_spatial_identity",
                "sum_a E^(a mu)*E^(a nu)=h_mu_nu",
            ),
            (
                "definitions",
                "khronon_unit_vector",
                "u_mu=-D_mu T/sqrt(-gamma_(rho sigma)*D_rho T*D_sigma T)",
            ),
        )
        for block, key, value in mutations:
            mutated = copy.deepcopy(self.payload)
            mutated["action_charter"][block][key] = value
            self._rebind(mutated)
            with self.subTest(key=key):
                with self.assertRaises(gate.OneOmegaActionCharterError):
                    gate.validate_payload(mutated)

    def test_shear_parenthesis_mutation_fails_after_digest_rebinding(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["action_charter"]["exact_action"]["solid"] = mutated[
            "action_charter"
        ]["exact_action"]["solid"].replace(
            "tr[(B-v^2*I)^2]", "tr(B-v^2*I)^2"
        )
        self._rebind(mutated)
        with self.assertRaisesRegex(
            gate.OneOmegaActionCharterError, "exact-action formula"
        ):
            gate.validate_payload(mutated)

    def test_formula_sign_mutations_fail_after_digest_rebinding(self) -> None:
        for key, old, new in (
            ("GHY", "S_GHY=+", "S_GHY=-"),
            ("wall_background", "S_wall0=-", "S_wall0=+"),
            ("Robin", "S_R=-", "S_R=+"),
            ("bulk_potential", "-2*W^2", "+2*W^2"),
        ):
            mutated = copy.deepcopy(self.payload)
            value = mutated["action_charter"]["exact_action"][key]
            mutated["action_charter"]["exact_action"][key] = value.replace(old, new)
            self._rebind(mutated)
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    gate.OneOmegaActionCharterError, "exact-action formula"
                ):
                    gate.validate_payload(mutated)

    def test_formula_sign_receipt_mutation_is_not_saved_by_rebinding(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["algebraic_audits"]["formula_and_signs"]["coefficients"][
            "GHY_M5_cubed_Theta_coefficient"
        ] = -1.0
        self._rebind(mutated)
        with self.assertRaisesRegex(
            gate.OneOmegaActionCharterError, "formula/sign audit"
        ):
            gate.validate_payload(mutated)

    def test_mass_dimensions_include_gravity_wall_and_B4(self) -> None:
        audit = self.payload["algebraic_audits"]["mass_dimensions"]
        self.assertEqual(audit["maximum_absolute_residual"], 0.0)
        for key in (
            "EH_bulk",
            "Omega_kinetic",
            "superpotential_W",
            "U_from_WOmega_squared_over_G",
            "U_from_W_squared_over_M5_cubed",
            "GHY",
            "Mb2_Kcal_squared",
            "Mb2_B4_Rcal_squared_over_k_squared",
        ):
            self.assertEqual(audit["rows"][key], audit["expected"][key])
        self.assertEqual(audit["kappa_b"], 0.5)
        self.assertEqual(audit["kappa_hat_over_Z5_M"], 1.0)
        self.assertEqual(audit["arbitrary_k_reconstruction"]["sample_k"], 2.75)

    def test_dimensionally_incoherent_Robin_sum_is_rejected(self) -> None:
        charter = copy.deepcopy(self.payload["action_charter"])
        charter["mass_dimension_ledger"]["Robin_y"] = 0.0
        with self.assertRaisesRegex(
            gate.OneOmegaActionCharterError, "dimensionally incoherent"
        ):
            gate.dimension_audit(charter)

    def test_two_side_N8_normalization_is_exact(self) -> None:
        row = self.payload["algebraic_audits"]["mass_dimensions"][
            "N8_two_side_normalization"
        ]
        self.assertTrue(row["Z5_is_per_side"])
        self.assertEqual(
            row["raw_barred_T_kappa_y_squared"],
            {"T": 2.0, "kappa": 1.0, "y_squared": 3.0},
        )
        self.assertEqual(
            row["normalized_T_kappa_y_squared"],
            {"T": 1.0, "kappa": 0.5, "y_squared": 3.0},
        )
        self.assertEqual(row["Mb_squared_over_k_squared_divisor_for_T_and_kappa"], 2.0)

    def test_positive_sigma_metric_is_an_algebraic_completed_square(self) -> None:
        sigma = self.payload["algebraic_audits"]["positive_sigma"]
        self.assertEqual(sigma["Schur_complement_of_triplet_block"], 1.2)
        self.assertEqual(sigma["determinant_four_field_metric"], 1.2)
        self.assertTrue(sigma["positive_for_Omega_positive"])

    def test_background_phi_zero_and_junction_signs_close(self) -> None:
        audit = self.payload["algebraic_audits"]["background_and_junctions"]
        self.assertIn("phi^a=0", audit["background"])
        self.assertEqual(audit["junction_convention"], gate.CANONICAL_JUNCTION_CONVENTION)
        self.assertEqual(audit["GHY_sign_for_EH_plus_M5_cubed_R_over_2"], 1)
        self.assertEqual(audit["Israel_equation_momentum_equals_brane_stress_sign"], 1)
        self.assertEqual(audit["scalar_wall_derivative_enters_with_plus_sign"], 1)
        self.assertLess(abs(audit["Israel_residual"]), 2.0e-14)
        self.assertLess(abs(audit["scalar_junction_residual"]), 2.0e-14)

    def test_junction_sign_mutation_is_rejected_even_if_digest_is_rebound(self) -> None:
        for key in (
            "GHY_sign_for_EH_plus_M5_cubed_R_over_2",
            "Israel_equation_momentum_equals_brane_stress_sign",
            "scalar_wall_derivative_enters_with_plus_sign",
        ):
            mutated = copy.deepcopy(self.payload)
            mutated["algebraic_audits"]["background_and_junctions"][key] = -1
            self._rebind(mutated)
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    gate.OneOmegaActionCharterError, "junction sign convention"
                ):
                    gate.validate_payload(mutated)

    def test_rank_full_triad_and_diagonal_global_symmetry(self) -> None:
        triad = self.payload["algebraic_audits"]["triad_rank"]
        self.assertEqual(triad["Jacobian_dAcal_da_rank"], 3)
        self.assertEqual(triad["sample_E_diagonal"], [1.0, 1.0, 1.0])
        self.assertEqual(
            triad["algebraic_identities"][1], "sum_a E^(a mu)*E^(a nu)=h^(mu nu)"
        )
        symmetry = self.payload["action_charter"]["symmetry_breaking_pattern"]
        self.assertEqual(
            symmetry["unbroken_on_X_equals_vx_background"], "diagonal SO(3)⋉R^3_X"
        )
        self.assertFalse(symmetry["relative_SO3_is_gauged"])

    def test_rank_or_completeness_mutation_is_rejected_after_rebinding(self) -> None:
        for key, value in (
            ("Jacobian_dAcal_da_rank", 2),
            ("algebraic_identities", ["E E=delta", "E E=h"]),
        ):
            mutated = copy.deepcopy(self.payload)
            mutated["algebraic_audits"]["triad_rank"][key] = value
            self._rebind(mutated)
            with self.subTest(key=key):
                with self.assertRaisesRegex(gate.OneOmegaActionCharterError, "solder rank"):
                    gate.validate_payload(mutated)

    def test_one_Omega_window_does_not_import_hairy_value_or_P4(self) -> None:
        row = self.payload["algebraic_audits"]["bare_parameter_window"]
        self.assertAlmostEqual(row["M4_bulk_squared"], 1.107013790800849, places=14)
        self.assertAlmostEqual(row["hairy_multiscalar_M4_bulk_squared"], 1.2298525754296912)
        self.assertFalse(row["hairy_multiscalar_M4_bulk_squared_imported"])
        self.assertTrue(row["strict_window"])
        self.assertFalse(row["historical_linear_P4_consumed_as_certificate"])
        self.assertFalse(row["full_new_action_ghost_certificate"])

    def test_dynamic_solid_is_healthy_in_isolation_and_changes_Hessian(self) -> None:
        row = self.payload["algebraic_audits"]["solid_Hessian"]
        self.assertEqual(row["new_phonon_field_count"], 3)
        self.assertEqual(row["mixed_second_derivative_d2L_dpiDot_dShift"], -1.0)
        self.assertEqual(row["shift_second_derivative_d2L_dShift2"], 1.0)
        self.assertTrue(row["isolated_solid_has_no_obvious_kinetic_or_gradient_ghost"])
        self.assertTrue(row["dynamic_solid_changes_old_Hessian"])
        self.assertFalse(row["old_P4_determinant_or_modes_inherited"])

    def test_SX_zero_and_frozen_X_are_not_escapes(self) -> None:
        for key, message in (
            ("zero_solid_action_escape_is_viable", "S_X=0"),
            ("fixed_external_triad_escape_is_covariant", "frozen X"),
        ):
            mutated = copy.deepcopy(self.payload)
            mutated["algebraic_audits"]["solid_Hessian"][key] = True
            self._rebind(mutated)
            with self.subTest(key=key):
                with self.assertRaisesRegex(gate.OneOmegaActionCharterError, message):
                    gate.validate_payload(mutated)

    def test_literal_certificate_pass_set_is_C1_N1_N8(self) -> None:
        ledger = self.payload["certificate_ledger"]
        self.assertEqual(ledger["C1_through_C10"]["pass_ids"], ["C1_ACTION"])
        self.assertEqual(
            ledger["N1_through_N8"]["pass_ids"],
            ["N1_ACTION", "N8_MATERIAL_PORT"],
        )
        self.assertEqual(
            ledger["C1_through_C10"]["items"][0]["required"], gate.C1_REQUIRED
        )
        self.assertEqual(
            ledger["N1_through_N8"]["items"][0]["required"], gate.N1_REQUIRED
        )
        self.assertTrue(self.payload["decision"]["C1_ACTION_pass"])
        self.assertTrue(self.payload["decision"]["N1_ACTION_pass"])
        self.assertTrue(self.payload["decision"]["N8_MATERIAL_PORT_pass"])

    def test_N1_is_action_only_and_N2_through_N7_are_false(self) -> None:
        row = self.payload["algebraic_audits"]["missing_variations"]
        joined = " ".join(row["variations_still_required_for_N2_through_N7"])
        for token in ("g_plus", "Omega_plus", "phi_plus", "embeddings", "khronon T", "solid X"):
            self.assertIn(token, joined)
        self.assertTrue(row["N1_ACTION_pass"])
        self.assertFalse(row["complete_first_variation_and_interface_terms_derived"])
        for key in (
            "N2_CONSTRAINTS_pass",
            "N3_CHARACTERISTICS_pass",
            "N4_JUNCTION_BENDING_pass",
            "N5_COUPLED_BVP_pass",
            "N6_GLOBAL_STABILITY_pass",
            "N7_LINEAR_REDUCTION_pass",
        ):
            self.assertFalse(self.payload["decision"][key])

    def test_N1_or_N8_false_mutation_is_rejected(self) -> None:
        for key in ("N1_ACTION_pass", "N8_MATERIAL_PORT_pass"):
            mutated = copy.deepcopy(self.payload)
            mutated["decision"][key] = False
            self._rebind(mutated)
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    gate.OneOmegaActionCharterError, "required action/material pass"
                ):
                    gate.validate_payload(mutated)

    def test_literal_N1_or_N8_ledger_mutation_is_rejected(self) -> None:
        for item_index in (0, 7):
            mutated = copy.deepcopy(self.payload)
            mutated["certificate_ledger"]["N1_through_N8"]["items"][item_index][
                "pass"
            ] = False
            self._rebind(mutated)
            with self.subTest(item_index=item_index):
                with self.assertRaises(gate.OneOmegaActionCharterError):
                    gate.validate_payload(mutated)

    def test_all_downstream_claims_remain_fail_closed(self) -> None:
        self.assertTrue(self.payload["checks"]["all"])
        for key in gate.PHYSICAL_FALSE_KEYS:
            self.assertIs(self.payload["decision"][key], False, key)
        for key in (
            "N2_CONSTRAINTS_pass",
            "P3_complete_gauge_fixed_unitary_determinant_pass",
            "P4_full_same_action_pass",
            "B4_pass",
            "B5_pass",
        ):
            mutated = copy.deepcopy(self.payload)
            mutated["decision"][key] = True
            self._rebind(mutated)
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    gate.OneOmegaActionCharterError, "fail-closed key promoted"
                ):
                    gate.validate_payload(mutated)

    def test_upstreams_are_byte_hash_bound_and_provenance_is_live(self) -> None:
        bindings = self.payload["upstream_bindings"]
        self.assertEqual(set(bindings), set(gate.UPSTREAM_PATHS))
        for name, path in gate.UPSTREAM_PATHS.items():
            self.assertEqual(bindings[name]["sha256"], gate.UPSTREAM_HASHES[name])
            self.assertEqual(
                bindings[name]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
            )
            self.assertEqual(bindings[name]["schema"], gate.UPSTREAM_SCHEMAS[name])
        provenance = self.payload["provenance"]
        self.assertEqual(
            provenance["generator"]["sha256"],
            hashlib.sha256(Path(gate.__file__).read_bytes()).hexdigest(),
        )
        self.assertEqual(
            provenance["test"]["sha256"],
            hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        )

    def test_upstream_byte_mutation_is_rejected(self) -> None:
        payload = json.loads(gate.WALL.read_text(encoding="utf-8"))
        payload["summary"] += " changed"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changed_wall.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with mock.patch.dict(gate.UPSTREAM_PATHS, {"backreacted_wall": path}):
                with self.assertRaisesRegex(
                    gate.OneOmegaActionCharterError, "backreacted_wall byte hash changed"
                ):
                    gate._load_upstreams()

    def test_wall_upstream_overclaim_is_rejected_after_hash_rebinding(self) -> None:
        payload = json.loads(gate.WALL.read_text(encoding="utf-8"))
        payload["decision"]["B4_pass"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "overpromoted_wall.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rebound = hashlib.sha256(path.read_bytes()).hexdigest()
            with (
                mock.patch.dict(gate.UPSTREAM_PATHS, {"backreacted_wall": path}),
                mock.patch.dict(gate.UPSTREAM_HASHES, {"backreacted_wall": rebound}),
            ):
                with self.assertRaisesRegex(gate.OneOmegaActionCharterError, "over-promoted"):
                    gate._load_upstreams()

    def test_direct_Robin_upstream_scope_mutation_is_rejected(self) -> None:
        payload = json.loads(gate.NONLINEAR_ROBIN.read_text(encoding="utf-8"))
        payload["canonical_material_Hamiltonian"][
            "bounded_below_for_prescribed_A"
        ] = False
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changed_robin.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rebound = hashlib.sha256(path.read_bytes()).hexdigest()
            with (
                mock.patch.dict(gate.UPSTREAM_PATHS, {"nonlinear_Robin_full_V4": path}),
                mock.patch.dict(gate.UPSTREAM_HASHES, {"nonlinear_Robin_full_V4": rebound}),
            ):
                with self.assertRaisesRegex(
                    gate.OneOmegaActionCharterError, "Hamiltonian scope"
                ):
                    gate._load_upstreams()

    def test_route_or_parameter_mutation_fails_after_digest_rebinding(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["action_charter"]["selection"]["solder_route"] = "bifundamental"
        self._rebind(mutated)
        with self.assertRaisesRegex(gate.OneOmegaActionCharterError, "field-content selection"):
            gate.validate_payload(mutated)

        mutated = copy.deepcopy(self.payload)
        mutated["action_charter"]["coefficient_policy"]["parameters"]["solid_rho"] = 2.0
        self._rebind(mutated)
        with self.assertRaisesRegex(gate.OneOmegaActionCharterError, "frozen parameter"):
            gate.validate_payload(mutated)

    def test_calculation_and_action_digests_are_live(self) -> None:
        self.assertEqual(
            self.payload["action_charter_digest"]["sha256"],
            gate._canonical_digest(self.payload["action_charter"]),
        )
        core = {key: self.payload[key] for key in gate.DIGEST_KEYS}
        self.assertEqual(
            self.payload["calculation_digest"]["sha256"],
            gate._canonical_digest(core),
        )

    def test_artifact_matches_fresh_build(self) -> None:
        stored = json.loads(gate.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.payload)

    def test_external_build_is_byte_reproducible(self) -> None:
        before = gate.OUTPUT.read_bytes()
        result = subprocess.run(
            [sys.executable, str(Path(gate.__file__).resolve())],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(gate.OUTPUT.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
