#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

try:
    from first_principles_audit.prediction_factory import derive_jordan_selector_embedding as embedding
except ModuleNotFoundError:
    import derive_jordan_selector_embedding as embedding


class JordanSelectorEmbeddingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = embedding.build()

    def test_exponential_frame_map(self) -> None:
        q = np.asarray([-0.3, 0.0, 0.7])
        beta = 0.2
        frame = embedding.exponential_frame_map(q, beta)
        np.testing.assert_allclose(frame["s"] * frame["A_m"] ** 2, 1.0)
        np.testing.assert_allclose(frame["ds_dq"], -2.0 * beta * frame["s"])

    def test_jordan_kinetic_identity(self) -> None:
        s = np.asarray([0.1, 0.5, 1.0])
        beta = 0.13
        z = embedding.jordan_kinetic_coefficient(s, beta)
        np.testing.assert_allclose(s * z + 1.5, 1.0 / (4.0 * beta**2))

    def test_selector_occupies_gravitational_stiffness_slot(self) -> None:
        derivation = self.result["frame_derivation"]
        self.assertEqual(derivation["selector_definition"], "s(phi)=A_m(phi)^(-2)")
        self.assertIn("s*R_J", derivation["curvature_term"])
        self.assertIn("gravitational stiffness", self.result["collector_embedding"]["physical_meaning"])

    def test_required_static_target_has_correct_sign_and_normalization(self) -> None:
        embedding_data = self.result["collector_embedding"]
        target = embedding_data["required_constraint_reduced_target"]
        self.assertIn("s*|grad Phi|^2-a0^2*W_J(s)", target)
        self.assertIn("M_Pl^2=1/(8*pi*G)", target)
        self.assertEqual(
            embedding_data["matter_source_variation"],
            "div[s*grad(Phi)]=4*pi*G*rho",
        )
        self.assertIn("U_J=-M_Pl^2*a0^2*W_J", embedding_data["simple_potential_matching"])

    def test_previous_linear_failure_is_explained(self) -> None:
        diagnosis = " ".join(self.result["failure_diagnosis_of_previous_linear_routes"])
        self.assertIn("Yukawa", diagnosis)
        self.assertIn("linear in source mass", diagnosis)
        self.assertIn("vanish with mu0", diagnosis)

    def test_embedding_is_not_mislabelled_as_completion(self) -> None:
        gates = self.result["physical_gates"]
        self.assertFalse(gates["nonlinear_A_m_of_phi_derived"])
        self.assertFalse(gates["weak_field_constraint_reduction_equals_local_s_times_X"])
        self.assertFalse(gates["jordan_potential_equals_required_W_of_s"])
        self.assertFalse(gates["physical_completion"])

    def test_blind_certificate_passes(self) -> None:
        self.assertEqual(self.result["sources"]["observational_inputs_read"], [])
        self.assertTrue(self.result["checks"]["all"])


if __name__ == "__main__":
    unittest.main()
