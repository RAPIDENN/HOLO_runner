#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest

from first_principles_audit.prediction_factory import (
    derive_holo_nonlinear_route_matrix as matrix,
)


class HoloNonlinearRouteMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = matrix.build()
        cls.routes = {row["id"]: row for row in cls.result["routes"]}

    def test_complete_certificate_passes(self) -> None:
        self.assertTrue(self.result["passes"]["all"])
        self.assertEqual(
            self.result["classification"],
            "theory_only_route_generation_with_falsifiers_not_a_new_force_claim",
        )

    def test_every_route_crosses_all_five_axes(self) -> None:
        axes = set(self.result["design_axes"])
        self.assertEqual(
            axes,
            {"carrier", "selector", "geometry", "coupling", "observable"},
        )
        for route in self.routes.values():
            self.assertEqual(set(route["coordinates"]), axes)
            for axis, coordinate in route["coordinates"].items():
                self.assertIn(coordinate, self.result["design_axes"][axis])

    def test_scores_are_bounded_complete_and_not_probabilities(self) -> None:
        for route in self.routes.values():
            scores = route["scores"]
            values = [scores[field] for field in matrix.SCORE_FIELDS]
            self.assertTrue(all(type(value) is int for value in values))
            self.assertTrue(all(0 <= value <= matrix.SCORE_MAX for value in values))
            self.assertEqual(scores["total_unweighted"], sum(values))
        self.assertIn("not probabilities", self.result["score_rubric"]["warning"])

    def test_soft_mode_is_a_derived_critical_precursor(self) -> None:
        soft = self.result["derived_constraints"]["soft_boundary_precursor"]
        self.assertGreater(soft["C_gamma"], 0.0)
        self.assertLess(soft["relative_spread"], 0.01)
        self.assertAlmostEqual(soft["C_gamma"], 0.014962287389557556)
        route = self.routes["critical_ir_soft_mode"]
        self.assertEqual(
            route["status"],
            "derived_exponent_precursor_with_failed_current_sign_gate",
        )
        self.assertEqual(route["scores"]["sqrt_mass_scaling"], 2)
        self.assertIn("wrong sign", route["falsifier"])
        self.assertFalse(soft["current_positive_W_sign_gate"])
        self.assertFalse(soft["analytic_linear_X_term_gate"])
        self.assertFalse(soft["nonvanishing_matter_residue_gate"])

    def test_breathing_legendre_route_has_exact_deep_algebra(self) -> None:
        route = self.routes["breathing_legendre_condensate"]
        equations = " ".join(route["minimal_equations"])
        self.assertIn("sqrt(1+u^2)", equations)
        self.assertIn("2*X^(3/2)/3", equations)
        self.assertIn("ds/dt=1-s", equations)
        self.assertEqual(route["scores"]["sqrt_mass_scaling"], 3)
        self.assertIn("fits a0", route["falsifier"])
        generated = self.result["derived_constraints"][
            "gapped_occupation_inverse_design"
        ]
        self.assertFalse(generated["stationary_occupation_derived"])
        self.assertFalse(generated["transport_is_holo_derived"])

    def test_brane_px_is_control_not_microscopic_success(self) -> None:
        route = self.routes["brane_px_exact_control"]
        self.assertEqual(route["scores"]["derivability"], 0)
        self.assertEqual(
            route["status"],
            "exact_engineering_control_not_microscopic_derivation",
        )
        self.assertIn("copied from the target", route["falsifier"])
        self.assertEqual(
            self.result["prototype_selection"]["exact_solver_control"],
            route["id"],
        )

    def test_jordan_route_is_exact_frame_map_not_aqual_claim(self) -> None:
        route = self.routes["jordan_frame_gravitational_selector"]
        self.assertEqual(
            route["status"],
            "exact_frame_identity_rejected_as_direct_full_planck_selector",
        )
        equations = " ".join(route["minimal_equations"])
        self.assertIn("s=A_m(phi)^(-2)", equations)
        self.assertIn("desired but unproved", equations)
        gates = self.result["derived_constraints"]["jordan_selector_embedding"]
        self.assertFalse(gates["constraint_reduction_gate"])
        self.assertFalse(gates["target_potential_gate"])
        self.assertFalse(gates["physical_completion"])
        deep_gate = self.result["derived_constraints"]["jordan_deep_limit_gate"]
        self.assertFalse(deep_gate["direct_full_planck_selector_gate"])
        self.assertEqual(route["scores"]["sqrt_mass_scaling"], 0)

    def test_surviving_architecture_keeps_tensor_term_nondegenerate(self) -> None:
        route = self.routes["derivative_constitutive_scalar"]
        self.assertEqual(
            route["status"],
            "surviving_architecture_operator_not_microscopically_derived",
        )
        equations = " ".join(route["minimal_equations"])
        self.assertIn("M_Pl^2*R_E/2", equations)
        self.assertIn("F(Y)=sup_s", equations)
        self.assertEqual(route["scores"]["sqrt_mass_scaling"], 3)
        self.assertEqual(
            self.result["prototype_selection"]["leading_research_hypotheses"][0],
            route["id"],
        )

    def test_tricritical_route_is_exact_but_not_bulk_derived(self) -> None:
        route = self.routes["tricritical_collective_amplitude"]
        equations = " ".join(route["minimal_equations"])
        self.assertIn("m2=u4=0", equations)
        self.assertIn("2*Y^(3/2)/3", equations)
        self.assertEqual(route["scores"]["sqrt_mass_scaling"], 4)
        self.assertEqual(route["scores"]["derivability"], 1)
        constraints = self.result["derived_constraints"][
            "tricritical_constitutive_bridge"
        ]
        self.assertFalse(constraints["bulk_realization_complete"])

    def test_spectral_route_is_identity_not_generation_claim(self) -> None:
        route = self.routes["gapless_spectral_continuum"]
        self.assertEqual(
            route["status"],
            "exact_integral_identity_not_healthy_local_generation",
        )
        self.assertIn("Gaussian", route["falsifier"])
        constraints = self.result["derived_constraints"][
            "gapless_spectral_bridge"
        ]
        self.assertLess(
            constraints["current_seven_mode_crossover_width_dex"], 0.25
        )
        self.assertFalse(constraints["healthy_local_generation_complete"])

    def test_bulk_decision_gate_is_prospective_and_fail_closed(self) -> None:
        gate = self.result["derived_constraints"]["bulk_decision_gate"]
        self.assertEqual(gate["old_source_mass_exponent"], 1.0)
        self.assertEqual(gate["new_source_mass_exponent"], 0.5)
        self.assertAlmostEqual(gate["minimal_radial_characteristic_ratio"], 2.0)
        self.assertFalse(gate["prospective_test_can_run"])
        self.assertFalse(gate["physical_completion"])

        cubic = self.result["derived_constraints"]["bulk_cubic_vertex_inventory"]
        self.assertFalse(cubic["physical_overlap_coefficients_computed"])
        self.assertFalse(cubic["direct_quartic_contact_computed"])
        self.assertIn("Delta P_exchange=-0.5", cubic["gapped_exchange_contribution_to_P"])
        self.assertIn("C_Y2_direct_S4-0.5", cubic["total_Y2_coefficient"])

    def test_finite_yukawa_and_finite_elimination_are_negative_controls(self) -> None:
        yukawa = self.routes["finite_stiff_yukawa"]
        elimination = self.routes["finite_mode_tree_elimination"]
        self.assertEqual(yukawa["scores"]["sqrt_mass_scaling"], 0)
        self.assertEqual(elimination["scores"]["sqrt_mass_scaling"], 0)
        self.assertIn("linear in M", yukawa["falsifier"])
        self.assertIn("X^(3/2)", elimination["falsifier"])
        self.assertEqual(
            set(self.result["prototype_selection"]["negative_controls"]),
            {
                yukawa["id"],
                elimination["id"],
                "jordan_frame_gravitational_selector",
            },
        )

    def test_scale_no_go_and_independent_a0_gate_are_preserved(self) -> None:
        scale = self.result["derived_constraints"]["scale_boundary"]
        self.assertFalse(scale["single_ell_viable_for_qcd_and_galaxy_readings"])
        self.assertGreater(scale["orders_of_magnitude_in_ell"], 40.0)
        self.assertIn("predicted independently", scale["rule"])

    def test_no_observational_tables_are_inputs(self) -> None:
        contract = self.result["input_contract"]
        self.assertEqual(contract["observational_tables_read"], [])
        paths = [row["path"].lower() for row in contract["inputs"].values()]
        self.assertFalse(any("rotmod" in path for path in paths))
        self.assertFalse(any("sparc_data" in path for path in paths))
        self.assertIn("exposed_empirical_target_for_comparison_only", contract)

    def test_generated_artifact_matches_builder_when_present(self) -> None:
        if matrix.OUTPUT.exists():
            rendered = json.loads(matrix.OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(rendered, self.result)


if __name__ == "__main__":
    unittest.main()
