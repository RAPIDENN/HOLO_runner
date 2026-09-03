#!/usr/bin/env python3
"""Contract tests for the v5.6.4.2 authoritative free-coordinate bundle."""

from __future__ import annotations

import ast
import json
import sys
import unittest
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitives as export


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


class PointwisePrimitiveBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = export.build_bundle()

    def test_lineage_ids_and_four_original_tangent_hashes(self) -> None:
        primary = self.bundle["primary_member"]
        self.assertEqual(primary["member_id"], "N2.K2.seed20260902")
        self.assertEqual(
            primary["parent_ambient_q_sha256"],
            "628e056d97adb9e052b0e88552828d3dd8c0c585af59f6c5b06ce90326366ea8",
        )
        self.assertEqual(
            self.bundle["pointwise_decoder_contract"]["free_coordinate_dimension"],
            996,
        )
        self.assertEqual(
            export._decode_f64(primary["authoritative_free_central_f64le"]).size,
            996,
        )
        self.assertEqual(self.bundle["identity_control"]["member_id"], "N2.K2.seed0")
        observed = {
            item["name"]: item["parent_ambient_tangent_sha256"]
            for item in primary["curves"]
        }
        self.assertEqual(len(primary["curves"]), len(observed))
        self.assertEqual(
            observed,
            {
                "compact_bulk_SO3_horizontal_candidate": "b60207626a7599b1a81c953d6e7a23752ed64260eed1a4d6206547d69c85e840",
                "embedding_motion_SO3_horizontal_candidate": "c5fc04ff0d3f3c2b097954baa4cbd53a97704beccac6e0bc1bf4614d305268e4",
                "free_B_SO3_horizontal_candidate": "1c35d0cf81f25b7c7d64dd81078ce519d1618fe10638c140d334e6821f8e7294",
                "joint_all_primitive_classes_control_candidate": "84ac494a2bd03d2fca9ca2490b4905436ef80719dcf4744f16ce2eae28b7812f",
            },
        )
        roles = {item["name"]: item["comparison_role"] for item in primary["curves"]}
        self.assertEqual(roles[export.PRIMARY_CURVE], "primary_scientific_comparator")

    def test_multistep_curves_share_identity_and_center(self) -> None:
        central = export._decode_f64(
            self.bundle["primary_member"]["authoritative_free_central_f64le"]
        )
        for curve in self.bundle["primary_member"]["curves"]:
            self.assertEqual([item["label"] for item in curve["step_families"]], ["h", "h_over_2", "h_over_4"])
            for family in curve["step_families"]:
                endpoints = {
                    key: export._decode_f64(value)
                    for key, value in family["free_endpoints_f64le"].items()
                }
                midpoint = 0.5 * (endpoints["-1"] + endpoints["1"])
                self.assertLess(float(np.linalg.norm(midpoint - central)), 2.0e-13)
                tangent = export._decode_f64(
                    curve["authoritative_free_tangent_f64le"]
                )
                observed = (endpoints["1"] - endpoints["-1"]) / (
                    2.0 * float(family["step"])
                )
                self.assertLess(float(np.linalg.norm(observed - tangent)), 2.0e-9)
            self.assertLessEqual(curve["construct_pushforward_residual_L2"], 2.0e-9)

    def test_pointwise_gluing_on_independent_mesh_and_endpoints(self) -> None:
        points = export._decode_f64(
            self.bundle["off_collocation_validation_nodes"]["points_f64le"]
        )
        contract = self.bundle["pointwise_decoder_contract"]
        records = [self.bundle["primary_member"]["authoritative_free_central_f64le"]]
        joint = next(
            item
            for item in self.bundle["primary_member"]["curves"]
            if item["name"] == export.PRIMARY_CURVE
        )
        for family in joint["step_families"]:
            records.extend(family["free_endpoints_f64le"].values())
        for record in records:
            free = export._decode_f64(record)
            decoded = export.decode_pointwise_boundary(free, contract, points)
            defects = export.pointwise_gluing_defects(decoded)
            maximum = max(
                float(np.max(np.abs(value)))
                for side in defects.values()
                for value in side.values()
            )
            self.assertLess(maximum, 3.0e-12)

    def test_published_raw_pointwise_diagnostics_match_reconstruction(self) -> None:
        validation = self.bundle["off_collocation_validation_nodes"]
        points = export._decode_f64(validation["points_f64le"])
        contract = self.bundle["pointwise_decoder_contract"]
        joint = next(
            item
            for item in self.bundle["primary_member"]["curves"]
            if item["name"] == export.PRIMARY_CURVE
        )
        records = {
            "central": self.bundle["primary_member"][
                "authoritative_free_central_f64le"
            ]
        }
        for family in joint["step_families"]:
            for multiplier in export.MULTIPLIERS:
                records[f'{family["label"]}:{multiplier:+d}'] = family[
                    "free_endpoints_f64le"
                ][str(multiplier)]
        published = validation["raw_pointwise_gluing_diagnostics"]
        self.assertEqual(len(published), 13)
        self.assertEqual({item["record_id"] for item in published}, set(records))
        for item in published:
            source = records[item["record_id"]]
            self.assertEqual(item["free_coordinates_sha256"], source["sha256"])
            expected = export.pointwise_gluing_defects(
                export.decode_pointwise_boundary(
                    export._decode_f64(source), contract, points
                )
            )
            for side in ("plus", "minus"):
                self.assertEqual(
                    set(item["raw_defects_f64le"][side]),
                    {"gamma", "Omega", "phi", "A"},
                )
                for component, expected_values in expected[side].items():
                    observed = export._decode_f64(
                        item["raw_defects_f64le"][side][component]
                    )
                    np.testing.assert_array_equal(observed, expected_values)
                    self.assertLess(float(np.max(np.abs(observed))), 3.0e-12)

    def test_geometry_contract_fixes_spatial_Rcal_not_R4(self) -> None:
        formulas = self.bundle["geometry_convention"]["foliation"]
        self.assertIn(
            "equivalently Rcal=R4+2*Ric4_mu_nu*u^mu*u^nu-Kcal^2+Kcal_mu_nu*Kcal^mu_nu",
            formulas,
        )

    def test_mandatory_gauss_corrigendum_is_pinned_and_quarantines_v5_5_4(self) -> None:
        pin = self.bundle["source_pins"][
            "mandatory_v5_5_4_Gauss_sign_corrigendum"
        ]
        self.assertEqual(pin["source_sha256"], export.GAUSS_CORRIGENDUM_SOURCE_SHA256)
        self.assertEqual(pin["test_sha256"], export.GAUSS_CORRIGENDUM_TEST_SHA256)
        self.assertEqual(
            pin["artifact_sha256"], export.GAUSS_CORRIGENDUM_ARTIFACT_SHA256
        )
        self.assertEqual(
            pin["required_decision_path"],
            "decision.v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma",
        )
        self.assertEqual(pin["required_value_literal"], "false")
        export._validate_gauss_corrigendum()

    def test_codec_roundtrips_are_bounded(self) -> None:
        self.assertLess(
            self.bundle["primary_member"]["codec_roundtrip"][
                "ambient_reconstruction_Linf"
            ],
            3.0e-12,
        )
        self.assertLess(
            self.bundle["identity_control"]["codec_roundtrip"][
                "ambient_reconstruction_Linf"
            ],
            3.0e-12,
        )

    def test_no_boolean_payload_and_frozen_bytes(self) -> None:
        self.assertFalse(any(isinstance(value, bool) for value in _walk(self.bundle)))
        without_hash = dict(self.bundle)
        digest = without_hash.pop("payload_sha256")
        self.assertEqual(digest, export._canonical_sha256(without_hash))
        expected = export.render_bundle(self.bundle)
        self.assertEqual((export.REPO / export.OUTPUT).read_bytes(), expected)

    def test_exporter_ast_does_not_depend_on_action_routes(self) -> None:
        source = Path(export.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or "").split(".", 1)[0])
        self.assertFalse({"torch", "jax"} & imports)
        self.assertNotIn("action_route_a", source.lower())
        self.assertNotIn("action_route_b", source.lower())


if __name__ == "__main__":
    unittest.main()
