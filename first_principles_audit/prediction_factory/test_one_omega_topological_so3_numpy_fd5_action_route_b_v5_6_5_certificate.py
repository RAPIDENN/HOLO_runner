#!/usr/bin/env python3
"""Light, independent tests for NumPy/FD5 action route B."""

from __future__ import annotations

import ast
import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derive_one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate as route_b


class RouteBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = route_b.load_primitive_bundle()
        cls.member = route_b._member(cls.bundle, "N2.K2.seed20260902")

    def test_ast_has_no_project_or_torch_dependency(self) -> None:
        source_path = Path(route_b.__file__).resolve()
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(source_path))
        import_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                import_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                import_roots.add((node.module or "").split(".", 1)[0])
        self.assertLessEqual(
            import_roots,
            {
                "__future__",
                "argparse",
                "base64",
                "hashlib",
                "itertools",
                "json",
                "math",
                "numpy",
                "pathlib",
                "typing",
            },
        )
        lowered = source.lower()
        self.assertNotIn("torch", lowered)
        self.assertNotIn("v5_6_2", lowered)
        self.assertNotIn("bulk_primitive_samples", source)
        self.assertNotIn("import export_", lowered)
        self.assertNotIn("GAUSS_CORRIGENDUM_ARTIFACT =", source)
        self.assertNotIn("--write-artifact", source)

    def test_current_bundle_member_and_gauss_corrigendum_pins(self) -> None:
        self.assertEqual(
            route_b._sha256_file(route_b.BUNDLE), route_b.BUNDLE_SHA256
        )
        self.assertEqual(self.member["member_id"], "N2.K2.seed20260902")
        self.assertEqual(self.member["N"], 2)
        self.assertEqual(self.member["K"], 2)
        self.assertEqual(
            self.bundle["pointwise_decoder_contract"]["free_coordinate_dimension"],
            996,
        )
        route_b._validate_gauss_corrigendum(self.bundle)

    def test_flat_tensor_geometry_is_zero(self) -> None:
        metric = np.diag((-1.0, 1.0, 1.0, 1.0, 1.0))
        first = np.zeros((5, 5, 5))
        second = np.zeros((5, 5, 5, 5))
        geometry = route_b.tensor_geometry(metric, first, second)
        self.assertEqual(float(geometry["scalar"]), 0.0)
        np.testing.assert_array_equal(geometry["ricci"], np.zeros((5, 5)))

    def test_inertia_rejects_three_negative_eigenvalues_despite_negative_det(self) -> None:
        wrong = np.diag((-3.0, -2.0, -1.0, 1.0, 2.0))
        self.assertLess(float(np.linalg.det(wrong)), 0.0)
        with self.assertRaisesRegex(ValueError, "wrong Lorentzian inertia"):
            route_b._lorentzian_inertia(wrong, 1, 4, "manufactured_wrong_bulk")
        right = route_b._lorentzian_inertia(
            np.diag((-3.0, 1.0, 2.0, 4.0, 5.0)), 1, 4, "manufactured_bulk"
        )
        self.assertEqual(right["negative_count"], 1)
        self.assertEqual(right["positive_count"], 4)
        self.assertGreater(right["spectral_margin_relative"], 0.0)
        summary = route_b._summarize_lorentzian_inertia({"bulk_plus": [right]})
        self.assertEqual(summary["bulk_plus"]["node_count"], 1)
        self.assertEqual(summary["bulk_plus"]["negative_count_at_each_node"], 1)
        self.assertIn("minimum_spectral_margin_absolute", summary["bulk_plus"])
        self.assertIn("minimum_spectral_margin_relative", summary["bulk_plus"])

    def test_radial_boundary_jets(self) -> None:
        profile = route_b.radial_profiles(np.asarray([0.0]), 3)
        self.assertEqual(float(profile["h0"][0]), 1.0)
        self.assertEqual(float(profile["h0_first"][0]), 0.0)
        self.assertEqual(float(profile["h1"][0]), 0.0)
        self.assertEqual(float(profile["h1_first"][0]), 1.0)
        np.testing.assert_array_equal(profile["bumps"][0], np.zeros(3))
        np.testing.assert_array_equal(profile["bumps_first"][0], np.zeros(3))

    def test_owned_quadrature_normalizations(self) -> None:
        tangential = route_b.tangential_quadrature(5)
        radial = route_b.radial_quadrature(3)
        self.assertAlmostEqual(float(np.sum(tangential["weights"])), (2.0 * math.pi) ** 4)
        self.assertAlmostEqual(float(np.sum(radial["weights"])), 1.0)
        self.assertEqual(tangential["points"].shape, (5 ** 4, 4))
        self.assertEqual(radial["points"].shape, (3,))

    def test_q3_is_smoke_only_and_refinable_grids_are_odd(self) -> None:
        self.assertEqual(
            route_b._pseudospectral_role(3, "smoke"), "aliased_smoke_only"
        )
        with self.assertRaisesRegex(ValueError, "Q=3"):
            route_b._pseudospectral_role(3, "refinable")
        with self.assertRaisesRegex(ValueError, "odd periodic grid"):
            route_b._pseudospectral_role(4, "refinable")
        self.assertEqual(
            route_b._pseudospectral_role(5, "refinable"),
            "odd_Q_refinable_projection",
        )

    def test_mutants_are_only_prepared_specifications(self) -> None:
        identifiers = {item["id"] for item in route_b.PREPARED_MUTANTS}
        self.assertIn("BF_insert_erroneous_inverse_factorial", identifiers)
        self.assertIn("BF_invert_complement_permutation_sign", identifiers)
        self.assertIn("freeze_relative_R", identifiers)
        self.assertIn("break_gluing", identifiers)

    def test_literal_component_coverage_is_twenty_plus_total(self) -> None:
        self.assertEqual(len(route_b.ACTION_COMPONENTS), 20)
        self.assertEqual(route_b.ACTION_COMPONENTS.count("wall"), 1)

    def test_pointwise_decoder_glues_at_reserved_noncollocation_nodes(self) -> None:
        free = route_b._decode_f64(
            self.member["authoritative_free_central_f64le"]
        )
        points = route_b._decode_f64(
            self.bundle["off_collocation_validation_nodes"]["points_f64le"]
        )
        defects = route_b.pointwise_gluing_defects(
            route_b.decode_pointwise_free_boundary(free, self.bundle, points)
        )
        maximum = max(
            float(np.max(np.abs(values)))
            for side in defects.values()
            for values in side.values()
        )
        self.assertLess(maximum, 3.0e-12)

    def test_all_four_free_curves_publish_same_center_and_three_fd5_steps(self) -> None:
        curves = self.member["curves"]
        self.assertEqual(len(curves), 4)
        self.assertEqual(len({curve["name"] for curve in curves}), 4)
        for curve in curves:
            self.assertEqual(
                [family["label"] for family in curve["step_families"]],
                ["h", "h_over_2", "h_over_4"],
            )
            for family in curve["step_families"]:
                self.assertEqual(family["multipliers"], [-2, -1, 1, 2])
        residuals = route_b._free_curve_affine_residuals(self.member, 996)
        self.assertEqual(set(residuals), {curve["name"] for curve in curves})
        for curve_records in residuals.values():
            self.assertEqual(len(curve_records), 12)
            for record in curve_records.values():
                self.assertLessEqual(record["Linf"], record["roundoff_bound"])

    def test_n2_seed0_is_an_explicit_R_identity_control(self) -> None:
        control = route_b._member(self.bundle, "N2.K2.seed0")
        free = route_b._decode_f64(control["authoritative_free_central_f64le"])
        points = route_b._decode_f64(
            self.bundle["off_collocation_validation_nodes"]["points_f64le"]
        )
        residual = route_b._identity_rotation_residual(free, self.bundle, points)
        self.assertLessEqual(max(residual.values()), 2.0e-14)

    def test_correct_gauss_leaf_scalar_flat_flrw(self) -> None:
        H = 0.4
        Hdot = -1.0 / 7.0
        scalar_R4 = 6.0 * (Hdot + 2.0 * H * H)
        ricci_uu = -3.0 * (Hdot + H * H)
        ricci = np.zeros((4, 4))
        ricci[0, 0] = ricci_uu
        observed = route_b.leaf_scalar_curvature(
            scalar_R4,
            ricci,
            np.asarray((1.0, 0.0, 0.0, 0.0)),
            3.0 * H,
            3.0 * H * H,
        )
        self.assertAlmostEqual(observed, 0.0, places=14)

    def test_correct_gauss_leaf_scalar_static_round_s3(self) -> None:
        radius = 1.5
        expected = 6.0 / (radius * radius)
        observed = route_b.leaf_scalar_curvature(
            expected,
            np.zeros((4, 4)),
            np.asarray((1.0, 0.0, 0.0, 0.0)),
            0.0,
            0.0,
        )
        self.assertAlmostEqual(observed, expected, places=14)

    def test_affine_fd5_window_is_dyadic_cached_and_fourth_order_exact(self) -> None:
        calls: list[float] = []

        def fake_action_evaluation(
            free: np.ndarray,
            bundle: object,
            member: object,
            tangential_points_per_axis: int,
            radial_gauss_order: int,
            numerical_role: str,
        ) -> dict[str, object]:
            del bundle, member, tangential_points_per_axis, radial_gauss_order, numerical_role
            x = float(free[0])
            calls.append(x)
            polynomial = 3.0 + 2.0 * x - 4.0 * x**2 + 0.5 * x**3 - 0.25 * x**4
            components = {name: polynomial for name in route_b.ACTION_COMPONENTS}
            components["S_total"] = 20.0 * polynomial
            defect = {"gamma": {"Linf": 0.0}}
            return {
                "components": components,
                "pointwise_gluing": {"plus": defect, "minus": defect},
                "lorentzian_inertia": {"manufactured": {"node_count": 1}},
            }

        original = route_b.action_evaluation
        route_b.action_evaluation = fake_action_evaluation
        try:
            receipt = route_b.affine_fd5_step_window(
                np.asarray((0.3,)),
                np.asarray((1.0,)),
                (0.02, 0.01, 0.005),
                {},
                {},
                5,
                3,
            )
        finally:
            route_b.action_evaluation = original
        expected = 2.0 - 8.0 * 0.3 + 1.5 * 0.3**2 - 1.0 * 0.3**3
        self.assertEqual(receipt["unique_endpoint_count"], 8)
        self.assertEqual(len(calls), 8)
        self.assertEqual(receipt["steps"], [0.02, 0.01, 0.005])
        for row in receipt["derivatives"]:
            self.assertAlmostEqual(
                row["FD5_action_directional_derivative"]["wall"], expected, places=11
            )
            self.assertAlmostEqual(
                row["FD5_action_directional_derivative"]["S_total"],
                20.0 * expected,
                places=9,
            )

        with self.assertRaisesRegex(ValueError, "dyadic"):
            route_b.affine_fd5_step_window(
                np.asarray((0.3,)),
                np.asarray((1.0,)),
                (0.02, 0.009),
                {},
                {},
                5,
                3,
            )

    def test_frozen_refinement_window_has_two_coarse_h4_intervals(self) -> None:
        self.assertEqual(
            route_b.FD5_REFINEMENT_STEPS,
            (4.0e-2, 2.0e-2, 1.0e-2, 5.0e-3, 2.5e-3),
        )


if __name__ == "__main__":
    unittest.main()
