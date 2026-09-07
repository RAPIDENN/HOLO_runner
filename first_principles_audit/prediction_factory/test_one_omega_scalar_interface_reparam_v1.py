#!/usr/bin/env python3
"""Independent exact and adversarial tests for the fixed-geometry scalar audit.

These checks establish reparametrization identities and artifact rejection only.
They neither promote the full interface problem nor modify its source charter.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import sympy as sp

from . import verify_one_omega_scalar_interface_reparam_v1 as gate


def _zero(expr):
    """Elementwise symbolic equality, without the verifier's comparison helper."""
    if isinstance(expr, sp.MatrixBase):
        return all(sp.simplify(value) == 0 for value in expr)
    return sp.simplify(expr) == 0


class IndependentReparametrizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = gate.derive_model()

    def test_change_of_fields_has_three_components_and_invertible_jacobian(self):
        m = self.model
        omega = m["symbols"]["omega"]
        phi = m["symbols"]["phi"]
        expected = sp.Matrix([omega, *(omega**sp.Rational(3, 2)*p for p in phi)])
        self.assertEqual(len(phi), 3)
        self.assertTrue(_zero(m["transform"] - expected))
        independent_jacobian = expected.jacobian(m["old_fields"])
        self.assertTrue(_zero(m["jacobian"] - independent_jacobian))
        self.assertEqual(sp.simplify(independent_jacobian.det()), omega**sp.Rational(9, 2))

    def test_charter_kinetic_reparametrization_in_each_of_three_components(self):
        m = self.model
        s = m["symbols"]
        omega, phi, psi = s["omega"], s["phi"], s["psi"]
        for side in range(2):
            dn = s["normal_omega"][side]
            dphi, dpsi = s["normal_phi"][side], s["normal_psi"][side]
            expected_old = s["G"]*dn**2 + s["Z"]*sum(
                (dphi[a] + sp.Rational(3, 2)*phi[a]*dn/omega)**2 for a in range(3))
            expected_new = s["G"]*dn**2 + s["Z"]*omega**(-3)*sum(v**2 for v in dpsi)
            with self.subTest(side=side):
                self.assertTrue(_zero(-2*m["old_kinetic"][side] - expected_old))
                self.assertTrue(_zero(-2*m["new_kinetic"][side] - expected_new))
                inverse = {phi[a]: psi[a]*omega**sp.Rational(-3, 2) for a in range(3)}
                inverse.update({dphi[a]: omega**sp.Rational(-3, 2)*dpsi[a]
                                - sp.Rational(3, 2)*psi[a]*omega**sp.Rational(-5, 2)*dn
                                for a in range(3)})
                self.assertTrue(_zero(expected_old.subs(inverse, simultaneous=True) - expected_new))
                wrong_coefficient = s["G"]*dn**2 + s["Z"]*sum(
                    (dphi[a] + phi[a]*dn/omega)**2 for a in range(3))
                self.assertFalse(_zero(wrong_coefficient.subs(inverse, simultaneous=True) - expected_new))
                wrong_weight = s["G"]*dn**2 + s["Z"]*omega**(-2)*sum(v**2 for v in dpsi)
                self.assertFalse(_zero(expected_new - wrong_weight))

    def test_off_shell_junction_transforms_as_a_covector(self):
        m = self.model
        jacobian = m["transform"].jacobian(m["old_fields"])
        pulled = jacobian.T*m["new_junction"].subs(m["substitutions"], simultaneous=True)
        self.assertTrue(_zero(m["old_junction"] - pulled))
        self.assertTrue(_zero(m["pulled_new_junction"] - pulled))
        self.assertTrue(_zero(m["old_junction"] - m["expected_junction"]))
        # No junction equation has been substituted here: all normal derivatives
        # and wall coefficients remain independent symbols.
        self.assertTrue(any(value != 0 for value in m["old_junction"]))
        wrong_pullback = jacobian*m["new_junction"].subs(m["substitutions"], simultaneous=True)
        self.assertFalse(_zero(m["old_junction"] - wrong_pullback))

    def test_nonlinear_hessian_chain_rule_uses_gradient_term(self):
        m = self.model
        q, Q = m["old_fields"], m["new_fields"]
        jacobian = m["transform"].jacobian(q)
        grad_new = sp.Matrix([sp.diff(m["new_wall_potential"], x) for x in Q])
        hessian_new = sp.hessian(m["new_wall_potential"], list(Q))
        pulled = jacobian.T*hessian_new.subs(m["substitutions"], simultaneous=True)*jacobian
        correction = sp.zeros(len(q))
        for component, value in zip(m["transform"], grad_new):
            correction += value.subs(m["substitutions"], simultaneous=True)*sp.hessian(component, list(q))
        direct = sp.hessian(m["old_wall_potential"], list(q))
        self.assertTrue(_zero(direct - pulled - correction))
        self.assertTrue(_zero(m["wall_hessian_old"] - direct))
        self.assertTrue(_zero(m["wall_hessian_congruence_only"] - pulled))
        self.assertTrue(_zero(m["wall_hessian_pulled"] - direct))
        self.assertTrue(_zero(m["wall_hessian_correction"] - correction))
        self.assertFalse(_zero(correction))
        self.assertFalse(_zero(direct - pulled))

    def test_bulk_balance_does_not_make_wall_gradient_vanish(self):
        # W_old=phi has zero old Hessian but nonzero wall gradient. An
        # independent bulk gradient can balance it without erasing the nonlinear
        # field-coordinate correction. This example is not built by gate code.
        omega, psi = sp.symbols("test_omega test_psi", positive=True)
        inverse = sp.Matrix([omega, psi*omega**sp.Rational(-3, 2)])
        wall_gradient = sp.Matrix([0, 1])
        bulk_gradient = sp.Matrix([0, -1])
        self.assertEqual(wall_gradient + bulk_gradient, sp.zeros(2, 1))
        direct = sp.hessian(inverse[1], (omega, psi))
        tensor_only = inverse.jacobian((omega, psi)).T*sp.zeros(2)*inverse.jacobian((omega, psi))
        self.assertFalse(_zero(direct - tensor_only))
        self.assertEqual(direct.subs({omega: 4, psi: 8}),
                         sp.Matrix([[sp.Rational(15, 64), sp.Rational(-3, 64)],
                                    [sp.Rational(-3, 64), 0]]))


    def test_outward_fluxes_add_and_single_robin_comes_from_charter(self):
        m = self.model
        s = m["symbols"]
        omega, G, Z = s["omega"], s["G"], s["Z"]
        phi, normal_o, normal_phi = s["phi"], s["normal_omega"], s["normal_phi"]
        P = [[normal_phi[e][a] + sp.Rational(3, 2)*phi[a]*normal_o[e]/omega
              for a in range(3)] for e in range(2)]
        # Written from the literal action coefficients, independently of the
        # verifier's expected_junction and old_momenta helpers.
        wall = sp.Matrix([
            s["beta"]*(omega-1) - 2*G*s["k"]*omega*sp.exp(-G*omega**2/(6*s["M5"])),
            *(s["kappa"]*(phi[a]-s["y"]*s["A"][a]) for a in range(3))])
        fluxes = [sp.Matrix([
            G*normal_o[e] + sp.Rational(3, 2)*Z/omega*sum(phi[a]*P[e][a] for a in range(3)),
            *(Z*P[e][a] for a in range(3))]) for e in range(2)]
        expected = fluxes[0] + fluxes[1] + wall
        self.assertTrue(_zero(m["old_junction"] - expected))
        self.assertTrue(gate.check_junction(m["old_junction"], expected))
        zero_normals = {q: 0 for q in (*normal_o, *normal_phi[0], *normal_phi[1])}
        self.assertTrue(_zero(m["old_junction"].subs(zero_normals) - wall))
        # Normals are already outward: reversing the second sign is not an
        # alternate convention once each normal derivative is defined this way.
        mutants = {
            "subtract_second_outward_face": fluxes[0]-fluxes[1]+wall,
            "omit_second_face": fluxes[0]+wall,
            "double_wall": fluxes[0]+fluxes[1]+2*wall,
            "double_robin_only": expected+sp.Matrix([0, *wall[1:]]),
            "omit_robin_only": expected-sp.Matrix([0, *wall[1:]]),
        }
        for name, candidate in mutants.items():
            with self.subTest(mutant=name):
                self.assertFalse(_zero(candidate-expected))
                self.assertFalse(gate.check_junction(candidate, expected))

    def test_junction_rejects_wrong_shape_and_inexact_float_inputs(self):
        expected = self.model["old_junction"]
        for candidate in (None, list(expected), sp.zeros(3, 1), sp.zeros(4, 4), expected.T):
            with self.subTest(candidate_type=type(candidate).__name__):
                self.assertFalse(gate.check_junction(candidate, expected))
        candidate = sp.Matrix(expected)
        candidate[1] += sp.Float("0.5")
        self.assertFalse(gate.check_junction(candidate, expected))


class SourceBindingAndPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.charter_bytes = gate.CHARTER.read_bytes()
        cls.charter = gate.load_charter()
        cls.payload = gate.build_payload()

    @staticmethod
    def _digest(value):
        # Deliberately independent of gate.canonical_digest.
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode()
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def _rebind_receipt(cls, payload):
        core = {k: v for k, v in payload.items() if k != "calculation_digest"}
        payload["calculation_digest"]["sha256"] = cls._digest(core)

    def test_baseline_is_bound_to_actual_source_and_validates(self):
        self.assertEqual(hashlib.sha256(self.charter_bytes).hexdigest(), gate.CHARTER_BYTES_SHA256)
        self.assertEqual(self._digest(self.charter["action_charter"]), gate.ACTION_SHA256)
        self.assertEqual(self._digest({k: self.charter[k] for k in gate.DIGEST_KEYS}), gate.CALCULATION_SHA256)
        gate.validate_payload(copy.deepcopy(self.payload))

    def test_source_reformatting_does_not_bypass_byte_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/"charter.json"
            p.write_bytes(self.charter_bytes+b"\n")
            with self.assertRaisesRegex(gate.ScalarInterfaceError, "byte hash"):
                gate.load_charter(p)

    def test_altered_source_fails_even_after_rebinding_both_embedded_hashes(self):
        changed = copy.deepcopy(self.charter)
        changed["action_charter"]["definitions"]["conformal_derivative"] = (
            "P_M^a=nabla_M phi^a+phi^a*nabla_M Omega/Omega")
        changed["action_charter_digest"]["sha256"] = self._digest(changed["action_charter"])
        changed["calculation_digest"]["sha256"] = self._digest({k: changed[k] for k in gate.DIGEST_KEYS})
        self.assertNotEqual(changed["action_charter_digest"]["sha256"], gate.ACTION_SHA256)
        self.assertEqual(changed["calculation_digest"]["sha256"], self._digest({k: changed[k] for k in gate.DIGEST_KEYS}))
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/"rebound.json"
            p.write_text(json.dumps(changed, sort_keys=True, ensure_ascii=False))
            with self.assertRaisesRegex(gate.ScalarInterfaceError, "byte hash"):
                gate.build_payload(p)

    def test_receipt_tampering_without_rebinding_fails_digest_check(self):
        changed = copy.deepcopy(self.payload)
        changed["equations"]["old_junction_equals_zero"][0] = "0"
        with self.assertRaisesRegex(gate.ScalarInterfaceError, "receipt digest mismatch"):
            gate.validate_payload(changed)

    def test_changed_equations_sources_scope_and_residuals_fail_after_rebinding(self):
        def mutate_equation(p):
            p["equations"]["old_junction_equals_zero"][1] = "0"

        def mutate_source(p):
            p["source"]["sha256"] = "0"*64

        def mutate_scope(p):
            p["scope"]["on_shell_substitution_used"] = True

        def mutate_residual(p):
            p["residuals"][next(iter(p["residuals"]))] = "1"

        def mutate_test_provenance(p):
            p["provenance"]["test"]["sha256"] = "0"*64

        for mutation in (mutate_equation, mutate_source, mutate_scope, mutate_residual, mutate_test_provenance):
            changed = copy.deepcopy(self.payload)
            mutation(changed)
            self._rebind_receipt(changed)
            self.assertEqual(changed["calculation_digest"]["sha256"],
                             self._digest({k: v for k, v in changed.items() if k != "calculation_digest"}))
            with self.subTest(mutation=mutation.__name__):
                with self.assertRaisesRegex(gate.ScalarInterfaceError, "independently recomputed"):
                    gate.validate_payload(changed)

    def test_no_broad_gate_is_promoted_by_local_exact_identities(self):
        expected_false = {
            "full_first_variation_pass", "N4_JUNCTION_BENDING_pass", "C4_HESSIAN_pass",
            "N2_CONSTRAINTS_pass", "N3_CHARACTERISTICS_pass", "N5_COUPLED_BVP_pass",
            "N6_GLOBAL_STABILITY_pass", "N7_LINEAR_REDUCTION_pass", "P4_full_same_action_pass",
            "B4_pass", "B5_pass",
        }
        decision = self.payload["decision"]
        self.assertIs(decision["fixed_geometry_scalar_interface_pass"], True)
        self.assertEqual(set(decision), expected_false | {"fixed_geometry_scalar_interface_pass"})
        for name in expected_false:
            self.assertIs(decision[name], False)
        self.assertIs(self.payload["scope"]["numeric_sampling_used_as_proof"], False)
        self.assertIs(self.payload["scope"]["bulk_Euler_Lagrange_equations_derived"], False)

    def test_rehashed_promotion_attempts_are_rejected(self):
        for name in ("C4_HESSIAN_pass", "N4_JUNCTION_BENDING_pass", "P4_full_same_action_pass", "B4_pass", "B5_pass"):
            changed = copy.deepcopy(self.payload)
            changed["decision"][name] = True
            self._rebind_receipt(changed)
            with self.subTest(gate=name):
                with self.assertRaisesRegex(gate.ScalarInterfaceError, "independently recomputed"):
                    gate.validate_payload(changed)

    def test_negative_controls_have_actual_nonzero_symbolic_residuals(self):
        controls = self.payload["negative_controls"]
        self.assertEqual(set(controls), {
            "omitted_Omega_phi_momentum", "subtracted_outward_sides", "Robin_wall_counted_twice",
            "omitted_induced_Robin_Omega_derivative", "omitted_off_shell_wall_Hessian_chain_correction"})
        self.assertTrue(all(value is True for value in controls.values()))
        for name, residual in self.payload["negative_control_residuals"].items():
            with self.subTest(control=name):
                self.assertTrue(any(value != "0" for value in residual))


if __name__ == "__main__":
    unittest.main()
