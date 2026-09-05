#!/usr/bin/env python3
"""Adversarial tests for the solid C2a BRST inventory-only gate."""

from __future__ import annotations

import ast
import copy
import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import unittest

from . import derive_one_omega_solid_c2a_brst_algebra_inventory_gate as gate


class _CountingPath:
    def __init__(self, raw: bytes) -> None:
        self.raw = raw
        self.read_count = 0

    def read_bytes(self) -> bytes:
        self.read_count += 1
        return self.raw

    def __str__(self) -> str:
        return "counting://canonical-charter"


def _all_strings(value: object) -> list[str]:
    if type(value) is str:
        return [value]
    if type(value) is list:
        return [text for item in value for text in _all_strings(item)]
    if type(value) is dict:
        return [
            text
            for key, item in value.items()
            for text in _all_strings(key) + _all_strings(item)
        ]
    return []


class SolidC2ABRSTAlgebraInventoryGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = gate.CHARTER_ARTIFACT.read_bytes()
        cls.charter = gate._decode_strict_json(cls.raw)
        cls.report = gate.build_report()

    def _assert_charter_rejected(self, mutated: dict[str, object]) -> None:
        with self.assertRaises(gate.SolidC2AInventoryError):
            gate.validate_charter(mutated)

    def _assert_report_rejected(self, mutated: dict[str, object]) -> None:
        with self.assertRaises(gate.SolidC2AInventoryError):
            gate.validate_report(mutated)

    def test_canonical_loader_reads_exactly_one_byte_sequence(self) -> None:
        path = _CountingPath(self.raw)
        payload, observed = gate.load_canonical_charter(path)
        self.assertEqual(path.read_count, 1)
        self.assertEqual(observed, gate.CHARTER_ARTIFACT_SHA256)
        self.assertEqual(
            hashlib.sha256(self.raw).hexdigest(), gate.CHARTER_ARTIFACT_SHA256
        )
        self.assertEqual(payload["schema"], gate.CHARTER_SCHEMA)

    def test_canonical_action_digest_is_recomputed_not_only_copied(self) -> None:
        self.assertEqual(
            gate._canonical_digest(self.charter["action_charter"]),
            gate.CHARTER_ACTION_DIGEST,
        )
        copied_digest_mutant = copy.deepcopy(self.charter)
        copied_digest_mutant["action_charter"]["route_id"] = "mutated-route"
        self.assertEqual(
            copied_digest_mutant["action_charter_digest"]["sha256"],
            gate.CHARTER_ACTION_DIGEST,
        )
        self._assert_charter_rejected(copied_digest_mutant)

    def test_strict_decoder_rejects_duplicates_nonfinite_and_wrong_root_types(self) -> None:
        malformed = (
            b'{"x":1,"x":2}',
            b'{"outer":{"x":1,"x":2}}',
            b'{"x":NaN}',
            b'{"x":Infinity}',
            b'{"x":-Infinity}',
            b'{"x":1e400}',
            b'{"x":-1e400}',
            b'{"x":1e309}',
            b'[]',
        )
        for raw in malformed:
            with self.subTest(raw=raw):
                with self.assertRaises(gate.SolidC2AInventoryError):
                    gate._decode_strict_json(raw)
        with self.assertRaises(gate.SolidC2AInventoryError):
            gate._decode_strict_json(bytearray(b"{}"))  # type: ignore[arg-type]

    def test_canonical_loader_rejects_any_byte_drift_before_semantic_use(self) -> None:
        tampered = self.raw.replace(
            b'"C2_BRST_pass": false', b'"C2_BRST_pass": true', 1
        )
        path = _CountingPath(tampered)
        with self.assertRaisesRegex(
            gate.SolidC2AInventoryError, "byte hash mismatch"
        ):
            gate.load_canonical_charter(path)
        self.assertEqual(path.read_count, 1)

    def test_schema_route_and_every_selection_classification_are_exact(self) -> None:
        mutations: list[tuple[str, dict[str, object]]] = []

        schema = copy.deepcopy(self.charter)
        schema["schema"] = "mutated-schema"
        mutations.append(("schema", schema))

        route = copy.deepcopy(self.charter)
        route["action_charter"]["route_id"] = "mutated-route"
        mutations.append(("route", route))

        replacement = {
            "bifundamental_solder_selected": True,
            "bulk_compensator": "two-Omega",
            "bulk_compensator_count": 2,
            "canonical_genealogy_selected_for_C1_and_N1": False,
            "fixed_external_triad_selected": True,
            "old_P3_gate_automatically_updated": True,
            "solder_route": "bifundamental solder",
        }
        for key, value in replacement.items():
            mutant = copy.deepcopy(self.charter)
            mutant["action_charter"]["selection"][key] = value
            mutations.append((f"selection_{key}", mutant))

        extra = copy.deepcopy(self.charter)
        extra["action_charter"]["selection"]["extra"] = False
        mutations.append(("selection_extra", extra))
        missing = copy.deepcopy(self.charter)
        del missing["action_charter"]["selection"]["bulk_compensator"]
        mutations.append(("selection_missing", missing))

        for name, mutant in mutations:
            with self.subTest(name=name):
                self._assert_charter_rejected(mutant)

    def test_field_inventory_rejects_internal_relative_or_ISO_ghost_injection(self) -> None:
        fields = (
            "classical_FP_or_BRST_fields",
            "independent_auxiliary_fields",
            "independent_internal_gauge_fields",
        )
        injections = (
            "relative_SO3_ghost",
            "global_ISO3_FP_ghost",
            "unselected_auxiliary",
        )
        for field, injection in zip(fields, injections, strict=True):
            mutant = copy.deepcopy(self.charter)
            mutant["action_charter"]["independent_fields"][field].append(injection)
            with self.subTest(field=field, injection=injection):
                self._assert_charter_rejected(mutant)

        extra = copy.deepcopy(self.charter)
        extra["action_charter"]["independent_fields"]["extra_field_class"] = []
        self._assert_charter_rejected(extra)

        missing = copy.deepcopy(self.charter)
        del missing["action_charter"]["independent_fields"]["brane_dynamic"]
        self._assert_charter_rejected(missing)

        physical = copy.deepcopy(self.charter)
        physical["action_charter"]["independent_fields"]["bulk_dynamic"][2] = (
            "one local SO(3) gauge triplet"
        )
        self._assert_charter_rejected(physical)

    def test_every_symmetry_and_breaking_classification_is_exact(self) -> None:
        symmetries = self.charter["action_charter"]["symmetries"]
        for index in range(len(symmetries)):
            mutant = copy.deepcopy(self.charter)
            mutant["action_charter"]["symmetries"][index] = f"mutated-{index}"
            with self.subTest(symmetry=index):
                self._assert_charter_rejected(mutant)

        for name, mutate in (
            ("extra", lambda values: values.append("local relative SO3 gauge")),
            ("missing", lambda values: values.pop()),
            ("reordered", lambda values: values.reverse()),
        ):
            mutant = copy.deepcopy(self.charter)
            mutate(mutant["action_charter"]["symmetries"])
            with self.subTest(symmetry_inventory=name):
                self._assert_charter_rejected(mutant)

        replacements = {
            "internal_translations": "local translations",
            "relative_SO3": "gauged",
            "relative_SO3_is_gauged": True,
            "unbroken_on_X_equals_vx_background": "relative SO3",
        }
        for key, value in replacements.items():
            mutant = copy.deepcopy(self.charter)
            mutant["action_charter"]["symmetry_breaking_pattern"][key] = value
            with self.subTest(breaking=key):
                self._assert_charter_rejected(mutant)

        for mode in ("extra", "missing"):
            mutant = copy.deepcopy(self.charter)
            breaking = mutant["action_charter"]["symmetry_breaking_pattern"]
            if mode == "extra":
                breaking["extra"] = "value"
            else:
                del breaking["relative_SO3"]
            with self.subTest(breaking_inventory=mode):
                self._assert_charter_rejected(mutant)

    def test_every_domain_classification_and_gluing_row_is_exact(self) -> None:
        domain_replacements: dict[str, object] = {
            "BRST_closed_boundary_domain_selected": True,
            "Omega": "Omega>=0",
            "excluded": ["nothing"],
            "gluing_is_a_restricted_domain_not_a_multiplier_equation": False,
            "khronon": "any dT",
            "solder_patch": "include det(B)=0",
            "solid": "B semidefinite",
        }
        for key, value in domain_replacements.items():
            mutant = copy.deepcopy(self.charter)
            mutant["action_charter"]["domains"][key] = value
            with self.subTest(domain=key):
                self._assert_charter_rejected(mutant)

        gluing = self.charter["action_charter"]["domains"]["interface_gluing"]
        for key in gluing:
            mutant = copy.deepcopy(self.charter)
            mutant["action_charter"]["domains"]["interface_gluing"][key] = (
                f"mutated-{key}"
            )
            with self.subTest(gluing=key):
                self._assert_charter_rejected(mutant)

        for mode in ("extra", "missing"):
            mutant = copy.deepcopy(self.charter)
            domains = mutant["action_charter"]["domains"]
            if mode == "extra":
                domains["extra"] = False
            else:
                del domains["Omega"]
            with self.subTest(domain_inventory=mode):
                self._assert_charter_rejected(mutant)

    def test_C_and_N_ledgers_reject_extra_missing_reordered_and_promoted_items(self) -> None:
        ledger_mutations: list[tuple[str, dict[str, object]]] = []
        for ledger_name in ("C1_through_C10", "N1_through_N8"):
            extra = copy.deepcopy(self.charter)
            extra["certificate_ledger"][ledger_name]["items"].append(
                {
                    "current_evidence": "fake",
                    "id": "FAKE",
                    "pass": False,
                    "required": "fake",
                }
            )
            ledger_mutations.append((f"{ledger_name}_extra", extra))

            missing = copy.deepcopy(self.charter)
            missing["certificate_ledger"][ledger_name]["items"].pop()
            ledger_mutations.append((f"{ledger_name}_missing", missing))

            reordered = copy.deepcopy(self.charter)
            reordered["certificate_ledger"][ledger_name]["items"].reverse()
            ledger_mutations.append((f"{ledger_name}_reordered", reordered))

            extra_key = copy.deepcopy(self.charter)
            extra_key["certificate_ledger"][ledger_name]["items"][0]["extra"] = False
            ledger_mutations.append((f"{ledger_name}_item_extra_key", extra_key))

        for index in range(1, len(gate.C_ITEM_IDS)):
            promoted = copy.deepcopy(self.charter)
            promoted["certificate_ledger"]["C1_through_C10"]["items"][index][
                "pass"
            ] = True
            ledger_mutations.append((f"promote_{gate.C_ITEM_IDS[index]}", promoted))

        c1_false = copy.deepcopy(self.charter)
        c1_false["certificate_ledger"]["C1_through_C10"]["items"][0]["pass"] = False
        ledger_mutations.append(("C1_false", c1_false))
        n1_false = copy.deepcopy(self.charter)
        n1_false["certificate_ledger"]["N1_through_N8"]["items"][0]["pass"] = False
        ledger_mutations.append(("N1_false", n1_false))
        p3_true = copy.deepcopy(self.charter)
        p3_true["certificate_ledger"]["C1_through_C10"]["P3_complete"] = True
        ledger_mutations.append(("P3_true", p3_true))

        for name, mutant in ledger_mutations:
            with self.subTest(name=name):
                self._assert_charter_rejected(mutant)

    def test_bool_int_and_int_float_aliases_are_rejected(self) -> None:
        aliases: list[tuple[str, dict[str, object]]] = []

        count = copy.deepcopy(self.charter)
        count["action_charter"]["selection"]["bulk_compensator_count"] = 1.0
        aliases.append(("int_as_float", count))

        relative = copy.deepcopy(self.charter)
        relative["action_charter"]["symmetry_breaking_pattern"][
            "relative_SO3_is_gauged"
        ] = 0
        aliases.append(("false_as_int", relative))

        c1 = copy.deepcopy(self.charter)
        c1["decision"]["C1_ACTION_pass"] = 1
        aliases.append(("true_as_int", c1))

        c2 = copy.deepcopy(self.charter)
        c2["decision"]["C2_BRST_pass"] = 0
        aliases.append(("decision_false_as_int", c2))

        ledger = copy.deepcopy(self.charter)
        ledger["certificate_ledger"]["C1_through_C10"]["items"][1]["pass"] = 0
        aliases.append(("ledger_false_as_int", ledger))

        for name, mutant in aliases:
            with self.subTest(name=name):
                self._assert_charter_rejected(mutant)

    def test_every_fail_closed_input_decision_rejects_promotion(self) -> None:
        for key in gate.FAIL_CLOSED_DECISION_KEYS:
            mutant = copy.deepcopy(self.charter)
            mutant["decision"][key] = True
            with self.subTest(key=key):
                self._assert_charter_rejected(mutant)
        for key in ("C1_ACTION_pass", "N1_ACTION_pass"):
            mutant = copy.deepcopy(self.charter)
            mutant["decision"][key] = False
            with self.subTest(key=key):
                self._assert_charter_rejected(mutant)

    def test_report_classifies_relative_and_global_ISO3_as_no_FP_ghosts(self) -> None:
        classification = self.report["ghost_classification"]
        self.assertTrue(
            self.report["decision"][
                "declared_symmetry_ghost_classification_boundary_recorded"
            ]
        )
        self.assertNotIn(
            "selected_action_ghost_classification_inventory_complete",
            self.report["decision"],
        )
        self.assertEqual(classification["status"], "INVENTORY_ONLY")
        self.assertFalse(classification["bulk_side_ghost_identification_selected"])
        self.assertEqual(
            classification["forbidden_local_FP_ghost_ids"],
            ["global_internal_ISO3", "relative_SO3"],
        )
        no_ghost_ids = {
            row["id"] for row in classification["no_local_FP_ghost_from_charter"]
        }
        self.assertEqual(
            no_ghost_ids,
            {
                "global_internal_ISO3",
                "relative_SO3",
                "Z2_exchange",
                "time_orientation_reversal",
            },
        )
        khronon = classification[
            "candidate_required_if_the_declared_redundancies_are_quotiented"
        ][2]
        self.assertIn("only if", khronon["qualification"])
        self.assertIn("not an arbitrary local FP scalar", khronon["qualification"])

    def test_report_rejects_relative_or_global_ISO3_ghost_injection(self) -> None:
        for injected in ("relative_SO3", "global_internal_ISO3"):
            mutant = copy.deepcopy(self.report)
            mutant["ghost_classification"][
                "candidate_required_if_the_declared_redundancies_are_quotiented"
            ].append(
                {
                    "id": injected,
                    "candidate_ghosts": [f"{injected}_ghost"],
                    "qualification": "fake local gauge symmetry",
                }
            )
            with self.subTest(injected=injected):
                self._assert_report_rejected(mutant)

        for mode in ("extra", "missing"):
            mutant = copy.deepcopy(self.report)
            rows = mutant["ghost_classification"][
                "candidate_required_if_the_declared_redundancies_are_quotiented"
            ]
            if mode == "extra":
                rows.append(copy.deepcopy(rows[0]))
            else:
                rows.pop()
            with self.subTest(inventory=mode):
                self._assert_report_rejected(mutant)

    def test_candidate_formula_strings_are_explicitly_unchecked(self) -> None:
        candidates = self.report["candidate_transformations"]
        self.assertEqual(candidates["status"], "FORMULA_INVENTORY_ONLY")
        self.assertFalse(candidates["machine_checked"])
        self.assertTrue(candidates["graded_evaluation_terms_required"])
        forbidden_claim_words = {"proof", "proved", "proven", "certified"}
        words = {
            word.strip(".,;:()[]{}\"'").lower()
            for text in _all_strings(candidates)
            for word in text.split()
        }
        self.assertTrue(forbidden_claim_words.isdisjoint(words))

        for key, value in (
            ("machine_checked", True),
            ("graded_evaluation_terms_required", False),
            ("status", "ALGEBRA_PROVED"),
        ):
            mutant = copy.deepcopy(self.report)
            mutant["candidate_transformations"][key] = value
            with self.subTest(key=key):
                self._assert_report_rejected(mutant)

        formula = copy.deepcopy(self.report)
        formula["candidate_transformations"]["formulas"][0]["candidate"] = "s g=0"
        self._assert_report_rejected(formula)

    def test_every_proof_boundary_and_downstream_decision_rejects_promotion(self) -> None:
        for key in self.report["proof_boundary"]:
            mutant = copy.deepcopy(self.report)
            mutant["proof_boundary"][key] = True
            with self.subTest(proof_boundary=key):
                self._assert_report_rejected(mutant)

        for key, value in self.report["decision"].items():
            if value is False:
                mutant = copy.deepcopy(self.report)
                mutant["decision"][key] = True
                with self.subTest(decision=key):
                    self._assert_report_rejected(mutant)

        alias = copy.deepcopy(self.report)
        alias["proof_boundary"]["nonlinear_nilpotency_machine_proved"] = 0
        self._assert_report_rejected(alias)

    def test_every_blocker_and_report_inventory_is_exact(self) -> None:
        for index in range(len(self.report["blockers"])):
            mutant = copy.deepcopy(self.report)
            mutant["blockers"][index]["missing"] = "silently closed"
            with self.subTest(blocker=index):
                self._assert_report_rejected(mutant)

        for mode in ("extra", "missing"):
            mutant = copy.deepcopy(self.report)
            if mode == "extra":
                mutant["extra"] = False
            else:
                del mutant["blockers"]
            with self.subTest(report_inventory=mode):
                self._assert_report_rejected(mutant)

    def test_module_has_no_prohibited_dependency_or_write_primitive(self) -> None:
        source_path = Path(gate.__file__).resolve()
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        attributes: set[str] = set()
        calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            elif isinstance(node, ast.Attribute):
                attributes.add(node.attr)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.add(node.func.id)
        self.assertTrue(
            imports.issubset(
                {"__future__", "hashlib", "json", "math", "pathlib", "typing"}
            )
        )
        self.assertTrue({"write_text", "write_bytes", "touch", "mkdir"}.isdisjoint(attributes))
        self.assertNotIn("open", calls)

    def test_main_prints_only_and_never_writes_an_artifact(self) -> None:
        would_be_artifact = (
            gate.HERE
            / "artifacts"
            / "one_omega_solid_c2a_brst_algebra_inventory_gate.json"
        )
        self.assertFalse(hasattr(gate, "OUTPUT"))
        self.assertFalse(would_be_artifact.exists())
        canonical_before = hashlib.sha256(gate.CHARTER_ARTIFACT.read_bytes()).hexdigest()
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = gate.main()
        self.assertEqual(result, 0)
        printed = json.loads(stream.getvalue())
        gate.validate_report(printed)
        self.assertFalse(printed["artifact_written"])
        self.assertFalse(would_be_artifact.exists())
        canonical_after = hashlib.sha256(gate.CHARTER_ARTIFACT.read_bytes()).hexdigest()
        self.assertEqual(canonical_before, canonical_after)


if __name__ == "__main__":
    unittest.main()
