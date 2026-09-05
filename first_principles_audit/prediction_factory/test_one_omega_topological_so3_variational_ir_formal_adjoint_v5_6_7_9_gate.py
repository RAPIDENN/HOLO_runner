#!/usr/bin/env python3
"""Independent tests for the infrastructure-only v5.6.7.9 gate."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_variational_ir_formal_adjoint_v5_6_7_9_gate
    as gate,
)


COMPONENTS = (
    "EH_bulk_plus", "Omega_kinetic_bulk_plus", "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus", "full_V4_bulk_plus", "BF_bulk_plus", "GHY_plus",
    "EH_bulk_minus", "Omega_kinetic_bulk_minus", "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus", "full_V4_bulk_minus", "BF_bulk_minus", "GHY_minus",
    "wall", "K_foliation", "R", "R_squared", "a_squared", "Robin",
)
DEPENDENCIES = {
    "EH_bulk_plus": (("g_plus", 2),),
    "Omega_kinetic_bulk_plus": (("g_plus", 0), ("Omega_plus", 1)),
    "Omega_potential_bulk_plus": (("g_plus", 0), ("Omega_plus", 0)),
    "P_kinetic_bulk_plus": (("g_plus", 0), ("Omega_plus", 1), ("phi_plus", 1), ("A_plus", 0)),
    "full_V4_bulk_plus": (("g_plus", 0), ("Omega_plus", 0), ("phi_plus", 0)),
    "BF_bulk_plus": (("A_plus", 1), ("B_plus", 0)),
    "GHY_plus": (("g_plus", 1), ("Y_plus", 2)),
    "EH_bulk_minus": (("g_minus", 2),),
    "Omega_kinetic_bulk_minus": (("g_minus", 0), ("Omega_minus", 1)),
    "Omega_potential_bulk_minus": (("g_minus", 0), ("Omega_minus", 0)),
    "P_kinetic_bulk_minus": (("g_minus", 0), ("Omega_minus", 1), ("phi_minus", 1), ("A_minus", 0)),
    "full_V4_bulk_minus": (("g_minus", 0), ("Omega_minus", 0), ("phi_minus", 0)),
    "BF_bulk_minus": (("A_minus", 1), ("B_minus", 0)),
    "GHY_minus": (("g_minus", 1), ("Y_minus", 2)),
    "wall": (("gamma", 0), ("Omega_Sigma", 0)),
    "K_foliation": (("gamma", 1), ("T", 2)),
    "R": (("gamma", 2), ("T", 2)),
    "R_squared": (("gamma", 2), ("T", 2)),
    "a_squared": (("gamma", 1), ("T", 2)),
    "Robin": (("gamma", 1), ("T", 2), ("varphi_H", 0)),
}
WEIGHTS = {
    "EH_bulk_plus": (1, 2, (("M5", 3),)),
    "Omega_kinetic_bulk_plus": (-1, 2, (("G", 1),)),
    "Omega_potential_bulk_plus": (-1, 1, ()),
    "P_kinetic_bulk_plus": (-1, 2, (("Z5", 1),)),
    "full_V4_bulk_plus": (-1, 1, (("Z5", 1), ("M", 2))),
    "BF_bulk_plus": (1, 1, ()),
    "GHY_plus": (1, 1, (("M5", 3),)),
    "EH_bulk_minus": (1, 2, (("M5", 3),)),
    "Omega_kinetic_bulk_minus": (-1, 2, (("G", 1),)),
    "Omega_potential_bulk_minus": (-1, 1, ()),
    "P_kinetic_bulk_minus": (-1, 2, (("Z5", 1),)),
    "full_V4_bulk_minus": (-1, 1, (("Z5", 1), ("M", 2))),
    "BF_bulk_minus": (1, 1, ()),
    "GHY_minus": (1, 1, (("M5", 3),)),
    "wall": (-1, 1, ()),
    "K_foliation": (1, 2, (("Mb", 2),)),
    "R": (1, 2, (("Mb", 2), ("xi", 1))),
    "R_squared": (-1, 32, (("Mb", 2), ("B4_bar", 1), ("k_infinity", -2))),
    "a_squared": (1, 2, (("Mb", 2), ("eta", 1))),
    "Robin": (-1, 2, (("kappa_hat", 1),)),
}
ACTION_KEYS = {
    **{name: ("bulk_gauged",) for name in ("EH_bulk_plus", "Omega_kinetic_bulk_plus", "EH_bulk_minus", "Omega_kinetic_bulk_minus")},
    "Omega_potential_bulk_plus": ("bulk_gauged", "bulk_potential", "superpotential"),
    "Omega_potential_bulk_minus": ("bulk_gauged", "bulk_potential", "superpotential"),
    "P_kinetic_bulk_plus": ("bulk_gauged", "gauged_conformal_derivative"),
    "P_kinetic_bulk_minus": ("bulk_gauged", "gauged_conformal_derivative"),
    "full_V4_bulk_plus": ("bulk_gauged", "full_V4"),
    "full_V4_bulk_minus": ("bulk_gauged", "full_V4"),
    "BF_bulk_plus": ("BF",), "BF_bulk_minus": ("BF",),
    "GHY_plus": ("GHY",), "GHY_minus": ("GHY",),
    "wall": ("wall_background", "superpotential"),
    "K_foliation": ("foliation_lower",), "R": ("foliation_lower",),
    "R_squared": ("foliation_lower",), "a_squared": ("foliation_lower",),
    "Robin": ("Robin_intrinsic",),
}
DOMAINS = {
    **{name: "M_plus" for name in COMPONENTS[:6]},
    **{name: "M_minus" for name in COMPONENTS[7:13]},
    **{name: "Sigma" for name in ("GHY_plus", "GHY_minus", *COMPONENTS[14:])},
}
V52_ACTION_HASH = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
INVENTORY_HASH = "803addb5e01c138fe3ec61c68273f4aeb06c9061e0765c898a8bd15b447736be"
SMOOTH_V4_FORMULA = (
    "Q(Omega,s)=Omega*s^2/(2*sqrt(1+Omega^6*s^2)); "
    "s=delta_ab*phi^a*phi^b"
)
SMOOTH_V4_VARIATIONS = (
    "Q_Omega=s^2/(2*sqrt(1+Omega^6*s^2))-(3/2)*Omega^6*s^4/(1+Omega^6*s^2)^(3/2)",
    "Q_s=Omega*s/sqrt(1+Omega^6*s^2)-(1/2)*Omega^7*s^3/(1+Omega^6*s^2)^(3/2)",
    "delta Q=Q_Omega*omega+2*Q_s*delta_ab*phi^a*psi^b",
)
THETA_FORMULA = (
    "Theta=-gamma^mn*n_R*Q_mn^R; "
    "Q_mn^R=partial_m partial_n Y^R+Gamma^R_AB(g)(Y)*Y_m^A*Y_n^B"
)
THETA_VARIATIONS = (
    "delta gamma^mn=-gamma^mr*gamma^ns*delta gamma_rs",
    "delta n_R=Delta_Y g_RA*n^A+g_RA*delta n^A",
    "Delta_Y Gamma^R_AB=delta_H Gamma^R_AB(Y)+xi^S*partial_S Gamma^R_AB(Y)",
    "delta Q_mn^R=partial_m partial_n xi^R+Delta_Y Gamma^R_AB*Y_m^A*Y_n^B+Gamma^R_AB(Y)*(partial_m xi^A*Y_n^B+Y_m^A*partial_n xi^B)",
    "delta Theta=-delta(gamma^mn)*n_R*Q_mn^R-gamma^mn*delta(n_R)*Q_mn^R-gamma^mn*n_R*delta(Q_mn^R)",
)
GROUPOID_FORMULA = (
    "iota:P|Sigma->Q; j=iota times_Ad R3; "
    "varphi_H^a=j(Y^*phi)^a are Q-associated components; "
    "varphi_H^m=e_a^m*varphi_H^a"
)
GROUPOID_VARIATIONS = (
    "delta iota=lambda_Q o iota-iota o lambda_P",
    "delta j=lambda_Q o j-j o lambda_P",
    "delta e=delta_H e-e o lambda_Q",
    "delta(Y^*phi)=delta_H(Y^*phi)+lambda_P o (Y^*phi)",
    "delta varphi_H^a=delta_H varphi_H^a+(lambda_Q)^a_b*varphi_H^b",
    "delta_vertical(e o j o Y^*phi)=(-e o lambda_Q)o(j o Y^*phi)+e o((lambda_Q o j-j o lambda_P)o(Y^*phi)+j o(lambda_P o (Y^*phi)))=0",
    "D_(A_Sigma) E_A+varphi_H diamond E_varphi=0",
)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
    ).hexdigest()


def weight_tuple(row: dict) -> tuple[int, int, tuple[tuple[str, int], ...]]:
    value = row["weight"]
    return value["numerator"], value["denominator"], tuple(tuple(x) for x in value["powers"])


@pytest.fixture(scope="session")
def report() -> dict:
    return gate.build_report()


def test_byte_pins_exact_action_and_provenance_only_milestones(report: dict) -> None:
    dependency = report["dependency_certificate"]
    assert dependency["pass"] is True
    assert dependency["v5_2_exact_action_sha256"] == V52_ACTION_HASH
    action = json.loads(gate.V52_ARTIFACT.read_text(encoding="utf-8"))["exact_classical_charter"]["exact_action"]
    assert canonical_hash(action) == V52_ACTION_HASH
    assert set(dependency["milestones"]) == {"60aa1a0", "acd7787", "91abcc1"}
    assert all(row["role"] == "provenance_only_not_a_semantic_dependency" for row in dependency["milestones"].values())
    assert dependency["Gauss_corrigendum"]["eligible_as_intrinsic_Rcal_dependency"] is False


def test_test_local_twenty_component_inventory_oracle(report: dict) -> None:
    inventory = report["literal_action_component_inventory"]
    assert inventory["pass"] is True
    assert inventory["scope"] == "byte_bound_literal_twenty_component_inventory_not_variation"
    assert inventory["inventory_sha256"] == INVENTORY_HASH
    assert tuple(inventory["component_order"]) == COMPONENTS
    for name, row in zip(COMPONENTS, inventory["rows"], strict=True):
        assert row["name"] == name
        assert row["domain"] == DOMAINS[name]
        assert tuple(row["action_keys"]) == ACTION_KEYS[name]
        assert tuple(tuple(x) for x in row["dependencies"]) == DEPENDENCIES[name]
        assert weight_tuple(row) == WEIGHTS[name]


def test_Robin_has_one_common_material_slot_and_groupoid_is_not_EL(report: dict) -> None:
    robin = next(row for row in report["literal_action_component_inventory"]["rows"] if row["name"] == "Robin")
    assert tuple(tuple(x) for x in robin["dependencies"]) == DEPENDENCIES["Robin"]
    assert not any("iota" in role or "j_" in role for role, _order in DEPENDENCIES["Robin"])
    geometry = report["candidate_geometric_formula_diagnostic"]
    assert geometry["pass"] is False
    assert geometry["formula_string_self_checks"] is True
    assert geometry["single_common_interface_material_EL_slot"] == "varphi_H^a (Q-associated components)"
    assert geometry["vertical_gluing_parameters_not_independent_EL_slots"] == ["iota_plus/j_plus", "iota_minus/j_minus"]


def test_aliases_and_covariant_derivative_slots_are_unambiguous() -> None:
    primitives = {item.name: item for item in gate.primitive_specs()}
    assert "k_infinity" in primitives["W"].formula and "*k*" not in primitives["W"].formula
    terms = gate.frechet_terms()
    r2 = " ".join(item.coefficient for item in terms if item.component == "R_squared")
    assert "B4_bar" in r2 and "k_infinity" in r2
    assert "B4/" not in r2 and "k^2" not in r2
    p_phi = [item for item in terms if item.component == "P_kinetic_bulk_plus" and item.role == "phi_plus"]
    assert any(item.derivative_word == ("M",) and "D_(A,M)" not in item.coefficient for item in p_phi)
    assert any(item.derivative_word == () and "A_M.act()" in item.coefficient for item in p_phi)
    bf_a = [item for item in terms if item.component == "BF_bulk_plus" and item.role == "A_plus"]
    assert any(item.derivative_word == ("M",) and "d()" not in item.coefficient for item in bf_a)
    assert any(item.derivative_word == () and "[A,()]" in item.coefficient for item in bf_a)


def test_candidate_IR_exposes_opacity_and_is_never_promoted(report: dict) -> None:
    candidate = report["candidate_literal_action_variation_IR_diagnostic"]
    assert candidate["pass"] is False
    assert candidate["structural_self_consistency"] is True
    assert candidate["tensorial_action_decoder_present"] is False
    assert candidate["Frechet_terms_proved_equal_to_D_of_literal_action"] is False
    assert candidate["primitive_formula_strings_nonempty"] is True
    assert candidate["no_opaque_nodes"] is False
    assert candidate["uninterpreted_coefficient_projection_atoms"]
    diagnostic = report["candidate_component_formal_adjoint_diagnostic"]
    assert diagnostic["pass"] is False
    assert diagnostic["algebraic_given_coefficients_self_identity"] is True
    assert diagnostic["application_accepted"] is False
    assert diagnostic["component_residuals_all_zero"] is True
    assert diagnostic["summed_residual_zero"] is True
    assert report["decision"]["candidate_twenty_component_formal_adjoint_application_pass"] is False
    assert report["decision"]["candidate_componentwise_raw_equals_adjoint_plus_divergence_application_pass"] is False


def test_operator_free_kernel_local_oracle_and_ordered_mixed_words(report: dict) -> None:
    kernel = report["operator_free_formal_adjoint_kernel"]
    assert kernel["pass"] is True
    assert kernel["scope"] == "operator_free_universal_recursion_only_not_application_to_any_action"
    assert kernel["ordered_words_preserved"] is True and kernel["reverse_rule_exact"] is True
    assert kernel["residual"] == []
    terms = (
        gate.FrechetTerm("u", "eta", "c0", (), Fraction(3)),
        gate.FrechetTerm("u", "eta", "c1", ("x",), Fraction(2)),
        gate.FrechetTerm("u", "eta", "c2", ("x", "y")),
        gate.FrechetTerm("u", "eta", "c3", ("y", "x")),
    )
    euler, current = gate.formal_adjoint(terms)
    assert ("u", "c2", ("y", "x"), "eta", ()) in euler
    assert ("u", "c3", ("x", "y"), "eta", ()) in euler
    assert gate.polynomial_residual(gate.raw_polynomial(terms), euler, gate.divergence(current)) == {}


def test_V4_and_GHY_narrow_inventory_claims(report: dict) -> None:
    primitives = {item.name: item for item in gate.primitive_specs()}
    primitive = primitives["smooth_V4"]
    assert primitive.formula == SMOOTH_V4_FORMULA
    assert primitive.variation == SMOOTH_V4_VARIATIONS
    assert "|phi|" not in primitive.formula
    assert primitives["Theta"].formula == THETA_FORMULA
    assert primitives["Theta"].variation == THETA_VARIATIONS

    oracle = report["smooth_full_V4_exact_algebraic_certificate"]
    action = json.loads(gate.V52_ARTIFACT.read_text(encoding="utf-8"))["exact_classical_charter"]["exact_action"]
    assert action["full_V4"] == "V4(r)=r^4/(2*sqrt(1+r^4))"
    assert "Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)" in action["bulk_gauged"]
    assert oracle["v5_2_original_definition_and_pullback_byte_bound"] is True
    omega, s, sqrt_radicand = Fraction(1), Fraction(3, 4), Fraction(5, 4)
    q = omega * s**2 / (2 * sqrt_radicand)
    q_omega = s**2 / (2 * sqrt_radicand) - Fraction(3, 2) * omega**6 * s**4 / sqrt_radicand**3
    q_s = omega * s / sqrt_radicand - Fraction(1, 2) * omega**7 * s**3 / sqrt_radicand**3
    original = omega**-5 * (omega**6 * s**2) / (2 * sqrt_radicand)
    assert (q, q_omega, q_s, original) == (
        Fraction(9, 40), Fraction(-9, 500), Fraction(123, 250), Fraction(9, 40)
    )
    rational = oracle["rational_oracle"]
    assert tuple(rational["Q"]) == (q.numerator, q.denominator)
    assert tuple(rational["Q_Omega"]) == (q_omega.numerator, q_omega.denominator)
    assert tuple(rational["Q_s"]) == (q_s.numerator, q_s.denominator)
    assert tuple(rational["Omega_minus_five_V4_of_Omega_three_halves_sqrt_s"]) == (original.numerator, original.denominator)
    assert oracle["pass"] is True
    assert report["decision"]["smooth_full_V4_zero_safe_algebraic_rewrite_pass"] is True
    assert report["decision"]["GHY_g1_Y2_inventory_and_outward_Theta_sign_only_pass"] is True
    for side in ("plus", "minus"):
        row = next(item for item in gate.component_specs() if item.name == f"GHY_{side}")
        assert row.dependencies == ((f"g_{side}", 1), (f"Y_{side}", 2))
        assert f"outward_{side}" in row.density


def test_vertical_groupoid_free_word_cancellation_and_3x3_oracle(report: dict) -> None:
    certificate = report["vertical_groupoid_free_word_certificate"]
    assert certificate["pass"] is True and certificate["residual"] == []
    groupoid = next(item for item in gate.primitive_specs() if item.name == "groupoid_law")
    assert groupoid.formula == GROUPOID_FORMULA
    assert groupoid.variation == GROUPOID_VARIATIONS
    assert certificate["single_typed_law_consumed"] is True
    assert certificate["displayed_formula_and_laws_exact_byte_binding"] is True
    assert certificate["Noether_identity_with_iota_j_map_Euler_momenta_derived"] is False

    def mm(a, b):
        return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))
    def mv(a, v):
        return tuple(sum(a[i][k] * v[k] for k in range(3)) for i in range(3))
    def add(*vectors):
        return tuple(sum(v[i] for v in vectors) for i in range(3))

    e = ((2, 1, 0), (0, 1, 1), (1, 0, 1)); j = ((1, 2, 0), (0, 1, 1), (1, 0, 2))
    lq = ((0, 2, -1), (-2, 0, 3), (1, -3, 0)); lp = ((0, -1, 4), (1, 0, 2), (-4, -2, 0)); phi = (2, -1, 3)
    de = tuple(tuple(-x for x in row) for row in mm(e, lq))
    lqj, jlp = mm(lq, j), mm(j, lp)
    dj = tuple(tuple(lqj[i][k] - jlp[i][k] for k in range(3)) for i in range(3))
    assert add(mv(mm(de, j), phi), mv(mm(e, dj), phi), mv(mm(e, j), mv(lp, phi))) == (0, 0, 0)


def test_Rcal_is_only_available_and_byte_bound_never_integrated(report: dict) -> None:
    availability = report["audited_Rcal_v5_6_7_8_dependency_availability"]
    assert availability["pass"] is True and availability["available_and_byte_bound"] is True
    assert availability["status"] == "available_and_byte_bound"
    assert "consumed" not in availability
    assert report["decision"]["audited_v5_6_7_8_Rcal_dependency_available_and_byte_bound_pass"] is True
    assert report["decision"]["Rcal_dependency_integrated_into_variational_IR_pass"] is False
    assert report["decision"]["R_R_squared_Frechet_semantic_validation_pass"] is False


def test_corrupting_R_rows_does_not_change_availability_or_promote_integration() -> None:
    baseline = gate.build_report()
    corrupt = gate.build_report(mutation="corrupt_R_R2_candidate")
    key = "audited_v5_6_7_8_Rcal_dependency_available_and_byte_bound_pass"
    assert baseline["decision"][key] is True and corrupt["decision"][key] is True
    assert corrupt["decision"]["Rcal_dependency_integrated_into_variational_IR_pass"] is False
    assert corrupt["decision"]["R_R_squared_Frechet_semantic_validation_pass"] is False
    assert corrupt["checks"]["all"] is False
    assert corrupt["candidate_literal_action_variation_IR_diagnostic"]["candidate_ir_sha256"] != baseline["candidate_literal_action_variation_IR_diagnostic"]["candidate_ir_sha256"]


def test_exact_true_and_false_decision_frontiers(report: dict) -> None:
    assert {key for key, value in report["decision"].items() if value} == {
        "literal_v5_2_twenty_component_byte_bound_inventory_pass",
        "operator_free_ordered_formal_adjoint_kernel_pass",
        "GHY_g1_Y2_inventory_and_outward_Theta_sign_only_pass",
        "smooth_full_V4_zero_safe_algebraic_rewrite_pass",
        "vertical_groupoid_gluing_inventory_and_free_word_vertical_cancellation_pass",
        "audited_v5_6_7_8_Rcal_dependency_available_and_byte_bound_pass",
    }
    for key in (
        "Frechet_IR_equals_D_of_literal_S_v5_2_pass",
        "literal_v5_2_twenty_component_semantic_IR_exact_pass",
        "componentwise_deltaL_equals_Edeltaq_plus_dTheta_semantic_pass",
        "full_off_shell_Green_theorem_selected_sector_pass",
        "full_classical_variational_principle_selected_sector_pass",
        "moving_pullback_Cartan_i_xi_L_composed_once_exact_pass",
        "normal_shape_equation_from_literal_action_exact_pass",
        "C1_ACTION_pass", "N1_ACTION_pass", "C1_N1_promotion_authorized",
    ):
        assert report["decision"][key] is False
    assert report["checks"]["all"] is True


@pytest.mark.parametrize("mutation", gate.PROMOTED_SCOPE_MUTATIONS)
def test_every_declared_promoted_scope_mutant_kills_a_narrow_check_and_all(mutation: str) -> None:
    mutated = gate.build_report(mutation=mutation)
    assert mutated["checks"]["all"] is False
    assert any(value is False for key, value in mutated["checks"].items() if key != "all")


def test_exact_formula_drift_mutants_are_promoted_and_fail_closed() -> None:
    expected = {
        "V4_formula_extra_term": (
            "smooth_V4", "smooth_full_V4_zero_safe_algebraic_rewrite_pass",
            SMOOTH_V4_FORMULA, SMOOTH_V4_VARIATIONS,
        ),
        "Theta_formula_extra_term": (
            "Theta", "GHY_g1_Y2_inventory_and_outward_Theta_sign_only_pass",
            THETA_FORMULA, THETA_VARIATIONS,
        ),
        "groupoid_delta_j_extra_term": (
            "groupoid_law",
            "vertical_groupoid_gluing_inventory_and_free_word_vertical_cancellation_pass",
            GROUPOID_FORMULA, GROUPOID_VARIATIONS,
        ),
    }
    assert set(expected) <= set(gate.PROMOTED_SCOPE_MUTATIONS)
    baseline = {item.name: item for item in gate.primitive_specs()}
    for mutation, (primitive_name, key, formula, variations) in expected.items():
        expected_hash = canonical_hash(
            {"formula": formula, "variation": list(variations)}
        )
        baseline_hash = canonical_hash(
            {
                "formula": baseline[primitive_name].formula,
                "variation": list(baseline[primitive_name].variation),
            }
        )
        assert baseline_hash == expected_hash
        primitives, _components, _terms = gate._apply_mutation(
            mutation, gate.primitive_specs(), gate.component_specs(), gate.frechet_terms()
        )
        mutated_primitive = next(item for item in primitives if item.name == primitive_name)
        mutated_hash = canonical_hash(
            {
                "formula": mutated_primitive.formula,
                "variation": list(mutated_primitive.variation),
            }
        )
        assert mutated_hash != expected_hash
        mutated = gate.build_report(mutation=mutation)
        assert mutated["decision"][key] is False
        assert mutated["checks"]["all"] is False


def test_test_local_inventory_oracle_kills_producer_and_expected_co_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _dependency, action = gate._dependency_certificate()
    primitives, components, terms = gate._apply_mutation(
        "producer_expected_co_mutation",
        gate.primitive_specs(),
        gate.component_specs(),
        gate.frechet_terms(),
    )
    del primitives, terms
    mutated = gate._component_inventory_certificate(action, components)
    assert mutated["inventory_sha256"] != INVENTORY_HASH
    monkeypatch.setattr(
        gate, "EXPECTED_COMPONENT_INVENTORY_SHA256", mutated["inventory_sha256"]
    )
    self_consistent = gate.build_report(mutation="producer_expected_co_mutation")
    assert self_consistent["literal_action_component_inventory"]["pass"] is True
    assert self_consistent["literal_action_component_inventory"]["inventory_sha256"] != INVENTORY_HASH


def test_invalid_Rcal_pin_is_fail_closed_without_semantic_side_effect() -> None:
    report = gate.build_report(rcal_v5678_pins={"invented": "0" * 64})
    availability = report["audited_Rcal_v5_6_7_8_dependency_availability"]
    assert availability["pass"] is False
    assert availability["available_and_byte_bound"] is False
    assert report["checks"]["all"] is False
    assert report["decision"]["Rcal_dependency_integrated_into_variational_IR_pass"] is False


def test_report_only_no_artifact_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.iterdir())
    assert gate.build_report()["checks"]["all"] is True
    assert set(tmp_path.iterdir()) == before
