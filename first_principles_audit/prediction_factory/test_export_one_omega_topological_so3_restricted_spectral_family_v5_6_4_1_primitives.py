#!/usr/bin/env python3
"""Hermetic contract tests for the v5.6.4.1 primitive-only export."""

from __future__ import annotations

import ast
import base64
import hashlib
import json
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_one_omega_topological_so3_restricted_spectral_family_v5_6_4_1_primitives as exporter


ROOT_KEYS = {
    "schema",
    "source_pins",
    "action_contract",
    "spectral_contract",
    "seed_contract",
    "primitive_members",
    "dependency_graph",
    "payload_sha256",
}
MEMBER_KEYS = {
    "member_id",
    "N",
    "K",
    "seed",
    "seed_role",
    "seed_sha256",
    "ambient_q_f64le",
    "bulk_primitive_samples",
    "stencil_contract",
    "horizontal_primitives",
    "gauge_primitives",
    "member_payload_sha256",
}
FORBIDDEN_KEY_FRAGMENTS = (
    "check",
    "decision",
    "euler",
    "ledger",
    "prediction",
    "residual",
    "tolerance",
    "pass",
    "claim",
    "svd",
    "invariant",
)
ALLOWED_EXPORTER_IMPORT_ROOTS = {
    "__future__",
    "base64",
    "hashlib",
    "json",
    "pathlib",
    "struct",
    "typing",
}
FORBIDDEN_CALL_NAMES = {"eval", "exec", "compile", "__import__"}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def walk_values(value: Any):
    yield value
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_values(item)


def f64_record_bytes(record: Mapping[str, Any]) -> bytes:
    if set(record) != {"data", "dtype", "encoding", "sha256", "shape"}:
        raise AssertionError("unexpected compact-array field")
    if record["dtype"] != "<f8" or record["encoding"] != "base64":
        raise AssertionError("unexpected compact-array encoding")
    raw = base64.b64decode(record["data"], validate=True)
    length = 1
    for item in record["shape"]:
        length *= item
    if len(raw) != 8 * length:
        raise AssertionError("compact-array shape mismatch")
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise AssertionError("compact-array digest mismatch")
    return raw


class PrimitiveBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = exporter.build_bundle()

    def test_final_source_pins_and_literal_action(self) -> None:
        observed = {
            name: item["sha256"] for name, item in self.bundle["source_pins"].items()
        }
        self.assertEqual(
            observed["v5_6_4_generator"],
            "198808b829a708ca9bc0314bfc5db235317f42eb48aa8f17ced6070cc3c87b7e",
        )
        self.assertEqual(
            observed["v5_6_4_test"],
            "24888a723e29af0d7b6f2df02d9739e676af72694280053b8b17a137eb8f5c82",
        )
        self.assertEqual(
            observed["v5_6_4_artifact"],
            "51d820b4652ca2fbf3039a6471ffbca5cdd29f57dc34f5f3006c2f68a5b4115e",
        )
        action = self.bundle["action_contract"]
        self.assertEqual(canonical_sha256(action["exact_action"]), action["exact_action_sha256"])
        self.assertEqual(
            action["exact_action_sha256"],
            "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a",
        )
        self.assertEqual(
            canonical_sha256(action["coefficient_parameters"]),
            action["coefficient_parameters_sha256"],
        )
        self.assertEqual(
            action["coefficient_parameters_source_json_path"],
            "exact_classical_charter.coefficient_policy.parameters",
        )
        self.assertEqual(
            canonical_sha256(action["topology_orientation"]),
            action["topology_orientation_sha256"],
        )
        relative = action["compact_relative_action_contract"]
        self.assertEqual(relative["bulk_domain"]["tangential"], "T4=[0,2*pi)^4")
        self.assertIn("L_i[X]-L_i[X_infinity]", relative["bulk_definition"])
        self.assertIn("subtract the central S_rel", relative["FD5_centering"])

    def test_output_allowlist_and_no_boolean_payload(self) -> None:
        self.assertEqual(set(self.bundle), ROOT_KEYS)
        for member in self.bundle["primitive_members"]:
            self.assertEqual(set(member), MEMBER_KEYS)
        for value in walk_values(self.bundle):
            self.assertNotIsInstance(value, bool)
        for mapping in (item for item in walk_values(self.bundle) if isinstance(item, dict)):
            for key in mapping:
                lowered = str(key).lower()
                self.assertFalse(
                    any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS),
                    key,
                )

    def test_compact_primitive_arrays_and_dimensions(self) -> None:
        convention = self.bundle["spectral_contract"]["primitive_component_convention"]
        self.assertEqual(convention["primitive_storage_basis"], "tau_I=hat(e_I)")
        self.assertEqual(
            convention["same_matrix_component_conversion"],
            ["A_tau=-A_T", "B_tau=-B_T", "lambda_tau=-lambda_T"],
        )
        self.assertIn("no additional factorial", convention["B_wedge_F_top_coefficient"])
        self.assertEqual(
            convention["tau_internal_pairing"], "dot_tau(X,Y)=-tr_3(XY)/2"
        )
        frame = self.bundle["spectral_contract"]["frame_rotation_contract"]
        self.assertEqual(frame["Q_frame_decoder"], "E_Q=E0 exp(-hat(q_Q))")
        embedding = self.bundle["spectral_contract"][
            "embedding_pullback_orientation_contract"
        ]
        self.assertIn("s_plus=partial y4/partial rho_plus=-1", embedding["collar_maps"]["plus"])
        self.assertIn("s_minus=partial y4/partial rho_minus=+1", embedding["collar_maps"]["minus"])
        self.assertEqual(
            embedding["oriented_interface_BF_flux_signs"], {"plus": 1, "minus": -1}
        )
        for member in self.bundle["primitive_members"]:
            N = member["N"]
            self.assertEqual(member["K"], N)
            ambient = f64_record_bytes(member["ambient_q_f64le"])
            layout = self.bundle["spectral_contract"]["ambient_layout_by_N"][str(N)][
                "blocks"
            ]
            self.assertEqual(len(ambient) // 8, max(item["stop"] for item in layout.values()))
            self.assertEqual(len(member["gauge_primitives"]), 9 * N)
            for family in (member["horizontal_primitives"], member["gauge_primitives"]):
                for primitive in family:
                    tangent = f64_record_bytes(primitive["ambient_primitive_tangent_f64le"])
                    self.assertEqual(len(tangent), len(ambient))
                    endpoints = primitive["stencil_endpoints_ambient_q_f64le"]
                    self.assertEqual(set(endpoints), {"-2", "-1", "1", "2"})
                    for endpoint in endpoints.values():
                        self.assertEqual(len(f64_record_bytes(endpoint)), len(ambient))

    def test_payload_hashes_and_deterministic_frozen_artifact(self) -> None:
        top_without_hash = dict(self.bundle)
        observed = top_without_hash.pop("payload_sha256")
        self.assertEqual(observed, canonical_sha256(top_without_hash))
        for member in self.bundle["primitive_members"]:
            without_hash = dict(member)
            member_hash = without_hash.pop("member_payload_sha256")
            self.assertEqual(member_hash, canonical_sha256(without_hash))
        expected = exporter.render_bundle(self.bundle)
        self.assertEqual((exporter.REPO / exporter.OUTPUT).read_bytes(), expected)
        self.assertEqual(expected, exporter.render_bundle(exporter.build_bundle()))

    def test_exporter_ast_import_allowlist(self) -> None:
        source_path = Path(exporter.__file__).resolve()
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                roots.add((node.module or "").split(".", 1)[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, FORBIDDEN_CALL_NAMES)
        self.assertLessEqual(roots, ALLOWED_EXPORTER_IMPORT_ROOTS)
        self.assertFalse({"numpy", "scipy", "torch", "jax", "importlib", "subprocess"} & roots)

    def test_dependency_graph_has_only_bundle_to_route_edges(self) -> None:
        graph = self.bundle["dependency_graph"]
        route_ids = {
            node["id"] for node in graph["nodes"] if node["kind"] == "future_evaluator"
        }
        self.assertEqual(len(route_ids), 4)
        incoming = {route: [] for route in route_ids}
        for edge in graph["edges"]:
            if edge["to"] in incoming:
                incoming[edge["to"]].append(edge["from"])
            self.assertFalse(edge["from"] in route_ids and edge["to"] in route_ids)
        self.assertEqual(
            incoming,
            {route: ["v5_6_4_1_primitive_bundle"] for route in route_ids},
        )


if __name__ == "__main__":
    unittest.main()
