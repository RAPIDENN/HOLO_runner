from __future__ import annotations

import unittest

from first_principles_audit.derive_and_audit import (
    DEFAULT_INSTRUMENT_ROOT,
    stage2_compare,
    stage3_adjudicate,
    symbolic_stage1,
    verify_frozen_inputs,
)


class FirstPrinciplesAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stage1 = symbolic_stage1()
        cls.stage2 = stage2_compare(DEFAULT_INSTRUMENT_ROOT)
        cls.stage3 = stage3_adjudicate(cls.stage1, cls.stage2)

    def test_frozen_inputs_match_preregistration(self) -> None:
        report = verify_frozen_inputs(DEFAULT_INSTRUMENT_ROOT)
        self.assertTrue(all(item["match"] for item in report.values()))

    def test_exact_flow_solves_both_coordinate_forms(self) -> None:
        self.assertTrue(self.stage1["all_symbolic_checks_pass"])
        self.assertTrue(self.stage3["independent_integration"]["pass"])
        self.assertTrue(self.stage3["conformal_coordinate_check"]["pass"])

    def test_frozen_trace_is_not_accepted_under_either_mass_sign(self) -> None:
        literal = self.stage2["trace_literal_implemented_potential"]
        intended = self.stage2["trace_intended_bf_mass_potential"]
        self.assertFalse(literal["all_preregistered_trace_checks_pass"])
        self.assertFalse(intended["all_preregistered_trace_checks_pass"])

    def test_holonomic_ansatz_must_pass_more_than_the_constraint(self) -> None:
        ansatz = self.stage2["holonomic_ansatz"]
        self.assertTrue(ansatz["passes"]["constraint"])
        self.assertFalse(ansatz["all_full_equation_checks_pass"])

    def test_observational_layers_are_not_promoted_to_derivations(self) -> None:
        claims = self.stage3["claim_matrix"]
        for name in (
            "sparc_result_is_out_of_sample_prediction",
            "growth_mapping_is_derived_from_the_action",
            "nist_null_validates_the_uv_coupling",
            "one_geometry_physically_unifies_all_reported_domains",
        ):
            self.assertFalse(claims[name]["pass"], name)


if __name__ == "__main__":
    unittest.main()
