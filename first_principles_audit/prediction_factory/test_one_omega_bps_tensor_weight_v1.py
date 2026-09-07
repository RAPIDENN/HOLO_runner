"""Independent exact references and fail-closed controls for the BPS TT receipt."""
from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

import sympy as sp

if __package__:
    from . import verify_one_omega_bps_tensor_weight_v1 as oracle
else:
    import verify_one_omega_bps_tensor_weight_v1 as oracle


class BPSTensorWeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = oracle.derive_model()
        cls.payload = oracle.build_payload()
        cls.s = cls.model["symbols"]

    def assertZero(self, expression):
        self.assertEqual(sp.simplify(expression), 0)

    def rehash(self, payload):
        core = {key: value for key, value in payload.items() if key != "calculation_digest"}
        payload["calculation_digest"]["sha256"] = oracle.canonical_digest(core)
        return payload

    def test_superpotential_differentiation_with_literal_G_normalization(self):
        o, G, M5c, k, a = (self.s[name] for name in ("omega", "G", "M5c", "k", "a"))
        literal = 3*M5c*k*sp.exp(-G*o**2/(6*M5c))
        substitution = {a: G/(6*M5c)}
        self.assertZero(self.model["omega_flow"].subs(substitution) - sp.diff(literal, o)/G)
        self.assertZero(self.model["A_flow"].subs(substitution) + literal/(3*M5c))

    def test_first_integral_and_initial_constant(self):
        o = self.s["omega"]
        self.assertZero(self.model["A_flow"] / self.model["omega_flow"] - 1/o)
        self.assertZero(self.model["A"].subs(o, 1))
        self.assertZero(sp.exp(self.model["A"]) - o)

    def test_w_coordinate_orientation_and_endpoint(self):
        o, a, k = (self.s[name] for name in ("omega", "a", "k"))
        independently_integrated = (sp.Ei(a)-sp.Ei(a*o**2))/(2*k)
        self.assertZero(sp.diff(independently_integrated, o)*self.model["omega_flow"] - 1)
        self.assertZero(independently_integrated.subs(o, 1))
        self.assertEqual(sp.limit(independently_integrated, o, 0, dir="+"), sp.oo)
        self.assertIs(self.model["dw_domega"].is_negative, True)

    def test_tensor_integral_by_independent_squared_coordinate(self):
        a, k, M5c = (self.s[name] for name in ("a", "k", "M5c"))
        u = sp.Symbol("u", real=True)
        # u=Omega^2 gives Omega*dOmega=du/2; integrate this different expression.
        unilateral = sp.integrate(sp.exp(a*u)/(2*k), (u, 0, 1))
        self.assertZero(unilateral - self.model["one_side_integral"])
        self.assertZero(2*M5c*unilateral - self.model["M4_bulk_squared"])
        self.assertFalse(oracle._zero(M5c*unilateral - self.model["M4_bulk_squared"]))

    def test_formal_G_zero_limit_and_first_correction(self):
        G, M5c, k, a = (self.s[name] for name in ("G", "M5c", "k", "a"))
        formula = self.model["M4_bulk_squared"].subs(a, G/(6*M5c))
        self.assertEqual(sp.limit(formula, G, 0, dir="+"), M5c/k)
        coefficient = sp.limit((formula-M5c/k)/G, G, 0, dir="+")
        self.assertEqual(coefficient, sp.Rational(1, 12)/k)
        wrong_sign = M5c*(1-sp.exp(-a))/(k*a)
        self.assertFalse(oracle._zero(wrong_sign-self.model["M4_bulk_squared"]))

    def test_frozen_value_without_float_parameters(self):
        expected = sp.Rational("1.10701379080084917")
        error = abs(sp.N(self.model["frozen_weight"]-expected, 50))
        self.assertLess(error, sp.Rational(1, 10**17))
        self.assertFalse(self.model["frozen_weight"].has(sp.Float))

    def test_TT_power_profiles_as_independent_closed_references(self):
        o, a, k, p = (self.s[name] for name in ("omega", "a", "k", "p"))
        h0, h1, h2 = (self.s[name] for name in ("H", "H_Omega", "H_OmegaOmega"))
        for n in (0, 1, 2):
            with self.subTest(power=n):
                profile = o**n
                jets = {h0: profile, h1: sp.diff(profile, o), h2: sp.diff(profile, o, 2)}
                expected = k**2*o**n*sp.exp(-2*a*o**2)*(n*(n+4)-2*a*n*o**2)-p**2*o**(n-2)
                self.assertZero(self.model["TT_w"].subs(jets)-expected)
                transformed = k**2*o**-3*sp.exp(-a*o**2)*self.model["TT_Omega"].subs(jets)
                self.assertZero(transformed-expected)

    def test_TT_divergence_form_with_general_function(self):
        o, a, k, p = (self.s[name] for name in ("omega", "a", "k", "p"))
        h = sp.Function("h")(o)
        jets = {self.s["H"]: h, self.s["H_Omega"]: sp.diff(h, o), self.s["H_OmegaOmega"]: sp.diff(h, o, 2)}
        expected = sp.diff(o**5*sp.exp(-a*o**2)*sp.diff(h,o),o)-p**2/k**2*o*sp.exp(a*o**2)*h
        self.assertZero(self.model["TT_Omega"].subs(jets)-expected)
        self.assertFalse(oracle._zero(self.model["TT_w"]-self.model["TT_Omega"]))

    def test_constant_profile_norm_and_unresolved_UV_condition(self):
        o, p = self.s["omega"], self.s["p"]
        constant = {self.s["H"]: 1, self.s["H_Omega"]: 0, self.s["H_OmegaOmega"]: 0, p: 0}
        self.assertZero(self.model["TT_w"].subs(constant))
        a, M5c, k = (self.s[name] for name in ("a", "M5c", "k"))
        positive_form = 2*M5c*sp.exp(a/2)*sp.sinh(a/2)/(k*a)
        self.assertIs(positive_form.is_positive, True)
        self.assertZero(self.model["M4_bulk_squared"]-positive_form.rewrite(sp.exp))
        self.assertIs(self.model["M4_bulk_squared"].is_finite, True)
        # This same profile fails a homogeneous Dirichlet condition at Omega=1.
        self.assertNotEqual(sp.S.One.subs(o, 1), 0)
        self.assertFalse(self.payload["decision"]["physical_massless_graviton_established"])
        self.assertFalse(self.payload["decision"]["UV_boundary_conditions_solved"])

    def test_positive_weights_and_negative_control_residuals(self):
        self.assertIs(self.model["P"].is_positive, True)
        self.assertIs(self.model["R"].is_positive, True)
        self.assertTrue(all(self.model["checks"].values()))
        self.assertTrue(all(self.model["negative_controls"].values()))
        for name, residual in self.model["negative_control_residuals"].items():
            with self.subTest(mutant=name):
                self.assertFalse(oracle._zero(residual))

    def test_exact_receipt_and_complete_digest(self):
        oracle.validate_payload(self.payload)
        core = {key: value for key, value in self.payload.items() if key != "calculation_digest"}
        self.assertEqual(self.payload["calculation_digest"]["sha256"], oracle.canonical_digest(core))
        self.assertEqual(set(self.payload["provenance"]), {"verifier", "test", "canonical_source_reader", "sympy_version"})

    def test_rehashed_false_equations_scope_provenance_and_type_are_rejected(self):
        changes = (
            ("equations", "M4_bulk_squared", "M5c/(2*k)"),
            ("decision", "N6_GLOBAL_STABILITY_pass", True),
            ("scope", "two_equal_bulk_sides_assumed", False),
            ("source", "sha256", "0"*64),
            ("checks", "TT_operator_coordinate_pullback", 1),
        )
        for block, key, value in changes:
            with self.subTest(block=block, key=key):
                mutant=copy.deepcopy(self.payload)
                mutant[block][key]=value
                with self.assertRaises(oracle.BPSTensorWeightError):
                    oracle.validate_payload(self.rehash(mutant))

    def test_stale_digest_and_malformed_container_are_rejected(self):
        mutant=copy.deepcopy(self.payload)
        mutant["checks"]["TT_operator_coordinate_pullback"]=False
        with self.assertRaises(oracle.BPSTensorWeightError):
            oracle.validate_payload(mutant)
        for malformed in (None, [], {}, {"calculation_digest": None}):
            with self.subTest(value=repr(malformed)):
                with self.assertRaises(oracle.BPSTensorWeightError):
                    oracle.validate_payload(malformed)

    def test_source_byte_pin_rejects_semantically_equal_reencoding(self):
        with tempfile.TemporaryDirectory() as directory:
            altered=Path(directory)/"reencoded.json"
            altered.write_bytes(oracle.CHARTER.read_bytes()+b"\n")
            with self.assertRaises(oracle.BPSTensorWeightError):
                oracle.build_payload(altered)

    def test_source_rehash_cannot_promote_an_altered_action(self):
        doc=json.loads(oracle.CHARTER.read_bytes())
        doc["action_charter"]["exact_action"]["superpotential"]="altered action"
        doc["action_charter_digest"]["sha256"]=oracle.canonical_digest(doc["action_charter"])
        doc["calculation_digest"]["sha256"]=oracle.canonical_digest({key:doc[key] for key in oracle.source_oracle.DIGEST_KEYS})
        with tempfile.TemporaryDirectory() as directory:
            altered=Path(directory)/"rebound.json"
            altered.write_text(json.dumps(doc))
            with self.assertRaises(oracle.BPSTensorWeightError):
                oracle.build_payload(altered)

    def test_strict_JSON_reader(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"bad.json"
            for raw in ('{"a":1,"a":2}', '{"a":NaN}', '[]'):
                with self.subTest(raw=raw):
                    p.write_text(raw)
                    with self.assertRaises(oracle.BPSTensorWeightError):
                        oracle._read_payload(p)

    def test_CLI_verification_recomputes_and_creation_is_exclusive(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            p=Path(directory)/"receipt.json"
            oracle.main(["--write",str(p)])
            before=p.read_bytes()
            oracle.main(["--verify",str(p)])
            with self.assertRaises(FileExistsError):
                oracle.main(["--write",str(p)])
            self.assertEqual(p.read_bytes(),before)
            mutant=json.loads(before)
            mutant["decision"]["B4_pass"]=True
            p.write_text(json.dumps(self.rehash(mutant)))
            with self.assertRaises(oracle.BPSTensorWeightError):
                oracle.main(["--verify",str(p)])

    def test_prior_work_is_credited_and_promotions_remain_closed(self):
        self.assertIn("Omega=exp(A)",self.payload["source"]["existing_background_statement"])
        self.assertEqual(len(self.payload["antecedents"]),2)
        expected_true={"bps_flow_tensor_measure_TT_transform_verified","constant_profile_normalizable_in_bulk"}
        self.assertEqual({key for key,value in self.payload["decision"].items() if value is True},expected_true)
        self.assertFalse(self.payload["scope"]["brane_kinetic_weight_included"])
        self.assertFalse(self.payload["scope"]["coupled_stability_inferred"])


if __name__ == "__main__":
    unittest.main()
