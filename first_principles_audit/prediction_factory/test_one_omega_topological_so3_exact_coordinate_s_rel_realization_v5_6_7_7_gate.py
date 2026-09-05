#!/usr/bin/env python3
"""Independent tests for the fail-closed v5.6.7.7 semantic-audit ledger."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
from itertools import combinations, permutations
import json
from pathlib import Path
import subprocess
import sys

import pytest


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "derive_one_omega_topological_so3_exact_coordinate_s_rel_realization_v5_6_7_7_gate.py"
SPEC = importlib.util.spec_from_file_location("v5677_exact_coordinate_s_rel", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


RESTRICTED_KEY = "restricted_exact_real_twenty_component_S_rel_coordinate_realization_pass"
EXPECTED_TRUE: set[str] = set()
EXPECTED_FALSE = {
    RESTRICTED_KEY,
    "same_functional_symbolic_identity_pass",
    "integrated_action_pass",
    "quadrature_pass",
    "runtime_float64_exact_realization_pass",
    "margins_certified_pass",
    "uniform_N_to_infinity_bridge_pass",
    "uniform_N_to_infinity_numerical_certificate_pass",
    "all_N_q_zero_factorization_pass",
    "continuum_action_representative_independence_theorem_pass",
    "global_smooth_physical_gauge_quotient_manifold_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "C1_N1_promotion_authorized",
    "P4_full_same_action_pass",
    "B4_pass",
    "B5_pass",
}

EXPECTED_PINS = {
    "one_omega_topological_so3_classical_v5_2_gate.json": "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
    "one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitive_bundle.json": "bcbb0037a2b025d9ece7387b5962a910e31eced7294ccb5324ab764c3bc7cb26",
    "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py": "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25",
    "test_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py": "3fdcd09c3e575893dade6a396865a593349ebc62d28c07706d3f2b58a0caacd4",
    "derive_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py": "afe410507da533dfff9037b5bd730d90d5931f82aaeb8d4839a48f9a4d18e0c9",
    "test_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py": "d7988e078fb81f9fa3001eaff2414962d45bfb240b024fbaacf8a9ab126b9694",
    "derive_one_omega_topological_so3_geometric_bulk_diffeomorphism_naturality_v5_6_7_2_gate.py": "23d04b2d8347dca513389e0b4d7c8e329405a2e2eb4989dd1238e0d6dbf2687b",
    "test_one_omega_topological_so3_geometric_bulk_diffeomorphism_naturality_v5_6_7_2_gate.py": "6a26693799d22dfcba338add59d72260ec61c72ffe969ed8cefbf59a920d7fe6",
    "derive_one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.py": "ca099da9f4f98a2a398cc0535ef2cd85e2e417e52fd8a7af0b87a3ef12664956",
    "one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.json": "09a98c369bfce6f04670b5be6443e78b32c0083e53e478c71f7787c364d26f7f",
    "derive_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py": "ac290aebfd981e54e5c5a9bda697fb6e23a4c15c4a17e540aa33700c11f7c717",
    "one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.json": "7c2c3e46ea73b312f753d944e43cd2a2e224d000e5ddd3c3e15ff816e76e441a",
    "test_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py": "584192eb81e881fdd31fc60dd6c96926a9dfaac6e7d1dc9a7f5dacad15f8db78",
}

EXPECTED_CONTRACT_HASHES = {
    "exact_action": "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a",
    "coefficient_environment": "12bb13017541b0a08554f61e46775843870499bbfc80c15127ef9cdee8481fa3",
    "compact_relative_contract": "16cb2a062e706aa4c92c7e43e09965cf9965ae8f488898f17c8aaa649e48775a",
    "topology_orientation": "3381d123147bcfdc7f81e900e2dc7e10adfc54194a5e4412df1dce72fff90d48",
    "geometry_convention": "69a24514ac0b4f2a0c7d1d6612fe94c7f42502dc9085cd141273dd93df8b6f54",
}

EXPECTED_EXACT_ACTION = {
    "BF": "S_BF=sum_eps int_Meps <B_eps wedge F[A_eps]>, <X,Y>=-tr_3(XY)/2",
    "GHY": "S_GHY=M5^3*sum_eps int_Sigma sqrt(-gamma)*Theta_eps for outward normals",
    "Robin_intrinsic": "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)",
    "bulk_gauged": "S_bulk_gauged=sum_eps int_Meps sqrt(-g_eps)*[M5^3*R_eps/2-G*(nabla Omega_eps)^2/2-U(Omega_eps)-Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2-Z5*M^2*Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)]",
    "bulk_potential": "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
    "foliation_lower": "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-B4_bar*Rcal^2/(16*k_infinity^2)]",
    "full_V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
    "gauged_conformal_derivative": "P_eps_M=D_(A_eps,M)phi_eps+3*phi_eps*partial_M log(Omega_eps)/2",
    "removed_terms": "S_X=0 and every bulk screen-clock term=0",
    "superpotential": "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]",
    "total": "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF",
    "wall_background": "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2]",
}

EXPECTED_COMPONENTS = (
    "EH_bulk_plus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "GHY_minus",
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)

EXPECTED_WEIGHTS = {
    "EH": (1, 2, (("M5", 3),)),
    "Omega_kinetic": (-1, 2, (("G", 1),)),
    "Omega_potential": (-1, 1, ()),
    "P_kinetic": (-1, 2, (("Z", 1),)),
    "full_V4": (-1, 1, (("M", 2), ("Z", 1))),
    "BF": (1, 1, ()),
    "GHY": (1, 1, (("M5", 3),)),
    "wall": (-1, 1, ()),
    "K_foliation": (1, 2, (("Mb", 2),)),
    "R": (1, 2, (("Mb", 2), ("xi", 1))),
    "R_squared": (-1, 32, (("B4_bar", 1), ("Mb", 2), ("k_infinity", -2))),
    "a_squared": (1, 2, (("Mb", 2), ("eta", 1))),
    "Robin": (-1, 2, (("kappa_hat", 1),)),
}

EXPECTED_NORMAL_FORM_SHA256 = "4119a124f1419e9be3d57df13261a5af8513b8c2717d4e2a27bbeb64cea9f778"
EXPECTED_TYPED_SIGNATURE_SHA256 = "580b4dd1dfd1e82b97f6957631fde95dbe11d0a397746dd52851d20e6fadd0af"
EXPECTED_SOURCE_SEMANTIC_IR_SHA256 = "97a28538504ea94ff9f6cd611da48165d0c181222f4dc4a5357ecbfebe64c471"
EXPECTED_AXIOM_CONTRACT_SHA256 = "ffc551ea0222d04fff140d8ebdda4612f78fec4558b22358cd90727629c27c71"
EXPECTED_AXIOMS = (
    {
        "id": "A01_pullback_components",
        "statement": "metric, covector, and differential-form pullbacks obey the stated coordinate component rules",
        "role": "assumption",
    },
    {
        "id": "A02_levi_civita_naturality",
        "statement": "the pinned Levi-Civita, Riemann, Ricci, and scalar-curvature conventions are natural under pullback",
        "role": "assumption",
    },
    {
        "id": "A03_so3_connection_naturality",
        "statement": "dA plus A cross A and the associated SO3 derivative transform in the pinned convention",
        "role": "assumption",
    },
    {
        "id": "A04_oriented_top_form",
        "statement": "oriented top forms transform by the signed Jacobian determinant exactly once",
        "role": "assumption",
    },
    {
        "id": "A05_ghy_definition",
        "statement": "the induced metric, outward unit conormal, second fundamental form, trace, and GHY sign use the pinned convention",
        "role": "assumption",
    },
    {
        "id": "A06_gauss_equation",
        "statement": "the contracted Gauss equation uses the pinned Riemann index order and extrinsic-curvature sign",
        "role": "assumption",
    },
    {
        "id": "A07_so3_pairing",
        "statement": "the SO3 adjoint pairing is minus one half of the three-dimensional trace",
        "role": "assumption",
    },
    {
        "id": "A08_positive_branches",
        "statement": "all square roots use the positive branch on the explicitly guarded admissible open domain",
        "role": "assumption",
    },
    {
        "id": "A09_flat_reference",
        "statement": "the fixed diagonal reference metric is constant and flat while its pulled coordinate components may vary with the embedding",
        "role": "assumption",
    },
    {
        "id": "A10_domain_linearity",
        "statement": "integration is linear only after each of the twelve bulk and eight boundary atoms is assigned to its stated domain",
        "role": "assumption",
    },
)


def _canonical_sha256(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _family(component: str) -> str:
    if component.startswith("GHY_"):
        return "GHY"
    for family in ("EH", "Omega_kinetic", "Omega_potential", "P_kinetic", "full_V4", "BF"):
        if component.startswith(f"{family}_bulk_"):
            return family
    return component


def test_every_decision_including_the_restricted_predicate_is_fail_closed() -> None:
    report = gate.build_report()
    decision = report["decision"]
    assert {key for key, value in decision.items() if value} == EXPECTED_TRUE
    assert {key for key, value in decision.items() if not value} == EXPECTED_FALSE
    assert set(decision) == EXPECTED_TRUE | EXPECTED_FALSE
    assert decision[RESTRICTED_KEY] is False
    assert report["structural_evidence_pass"] is True
    assert report["semantic_discharge"]["pass"] is False
    assert report["semantic_discharge"]["all_obligations_discharged"] is False
    gate.validate_report(report)
    assert "does not prove" in report["theorem"]["statement"]
    assert "proof-assistant verification" in report["theorem"]["not_claimed"]
    assert "exact-real denotational equivalence" in report["theorem"]["not_claimed"]
    assert "a physical detection or empirical physics result" in report["theorem"]["not_claimed"]


def test_every_consumed_file_is_byte_pinned_by_test_local_hash() -> None:
    report = gate.build_report()["source_pins"]
    assert report["expected"] == EXPECTED_PINS
    assert report["v5_6_7_2_commit_pin"] == "91abcc1dcf73e597526c5fe4d510df0f00ade3b5"
    for name, expected in EXPECTED_PINS.items():
        matches = list(HERE.glob(name)) + list((HERE / "artifacts").glob(name))
        assert len(matches) == 1
        assert hashlib.sha256(matches[0].read_bytes()).hexdigest() == expected
        assert report["observed"][name] == expected
        assert report["matches"][name] is True


def test_exact_action_and_composite_contract_are_independently_literal_bound() -> None:
    bundle = json.loads(
        (HERE / "artifacts/one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitive_bundle.json").read_text()
    )
    v52 = json.loads((HERE / "artifacts/one_omega_topological_so3_classical_v5_2_gate.json").read_text())
    action = bundle["action_contract"]
    assert action["exact_action"] == EXPECTED_EXACT_ACTION
    assert v52["exact_classical_charter"]["exact_action"] == EXPECTED_EXACT_ACTION
    actual = {
        "exact_action": _canonical_sha256(action["exact_action"]),
        "coefficient_environment": _canonical_sha256(action["coefficient_parameters"]),
        "compact_relative_contract": _canonical_sha256(action["compact_relative_action_contract"]),
        "topology_orientation": _canonical_sha256(action["topology_orientation"]),
        "geometry_convention": _canonical_sha256(bundle["geometry_convention"]),
    }
    assert actual == EXPECTED_CONTRACT_HASHES
    reported = gate.build_report()["contract_pins"]
    assert reported["hashes"] == EXPECTED_CONTRACT_HASHES
    assert reported["exact_action_equal_to_v5_2"] is True
    assert reported["v5_6_6_15_negative_only"] is True
    assert reported["Gauss_corrigendum_consumed"] is True


def test_twenty_semantic_normal_forms_are_independent_of_AST_matching() -> None:
    report = gate.build_report()["normal_forms"]
    rows = report["rows"]
    assert tuple(row["component"] for row in rows) == EXPECTED_COMPONENTS
    assert len(rows) == 20
    assert _canonical_sha256(rows) == EXPECTED_NORMAL_FORM_SHA256
    assert report["sha256"] == EXPECTED_NORMAL_FORM_SHA256
    assert report["pass"] is True
    for row in rows:
        family = _family(row["component"])
        expected = EXPECTED_WEIGHTS[family]
        assert row["coefficient"] == {
            "numerator": expected[0],
            "denominator": expected[1],
            "powers": [list(item) for item in expected[2]],
        }
        if "_bulk_" in row["component"]:
            assert row["reference_policy"] == "actual_minus_pulled_X_infinity"
            assert row["domain"].startswith("T4_x_[0,1]")
        else:
            assert row["reference_policy"] == "literal_unsubtracted"
            assert row["domain"] == "T4_interface"


def test_source_AST_binding_covers_each_sensitive_semantic_fact() -> None:
    text = gate.V5671_SOURCE.read_text()
    audit = gate.audit_source_text(text)
    assert audit["pin_pass"] is True
    assert audit["pass"] is True
    assert audit["semantic_target_sha256"] == EXPECTED_NORMAL_FORM_SHA256
    assert set(audit["checks"]) == {
        "component_inventory",
        "metric_pullback",
        "connection_pullback",
        "three_form_pullback",
        "bulk_coefficients_and_signs",
        "Omega_P_and_V4_definitions",
        "BF_curvature_orientation_pairing",
        "bulk_reference_subtraction",
        "GHY_outward_normal_and_sign",
        "Gauss_sign_and_foliation",
        "Robin_minus_y_and_interface_coefficients",
        "unsubtracted_GHY_and_shared_producer",
        "separate_domains_then_total",
        "transitive_closed_structural_semantic_IR",
    }
    assert all(audit["checks"].values())
    assert audit["source_semantic_IR_sha256"] == EXPECTED_SOURCE_SEMANTIC_IR_SHA256
    assert audit["expected_source_semantic_IR_sha256"] == EXPECTED_SOURCE_SEMANTIC_IR_SHA256
    semantic_ir = audit["source_semantic_IR"]
    assert semantic_ir["closed"] is True
    assert semantic_ir["denotational_proof_claimed"] is False
    assert semantic_ir["missing_roots"] == []
    assert semantic_ir["missing_classes"] == []
    assert semantic_ir["missing_constants"] == []
    assert semantic_ir["unresolved_private_calls"] == []
    assert {"RhoJet2", "TaylorDual3"} <= set(semantic_ir["classes"])
    assert set(semantic_ir["observed_parameter_keys"]) == set(semantic_ir["required_parameter_keys"])
    assert all(count == 1 for count in semantic_ir["landmark_counts"].values())
    tree = ast.parse(text)
    assignments = {
        target.id: node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assert ast.literal_eval(assignments["SIDE_RADIAL_SIGN"]) == {"plus": -1.0, "minus": 1.0}


def test_transitive_IR_has_an_independent_test_local_oracle_and_named_use_sites() -> None:
    text = gate.V5671_SOURCE.read_text()
    semantic_ir = gate.extract_source_semantic_IR(text)
    assert _canonical_sha256(semantic_ir) == EXPECTED_SOURCE_SEMANTIC_IR_SHA256
    assert gate.SOURCE_SEMANTIC_IR_SHA256 == EXPECTED_SOURCE_SEMANTIC_IR_SHA256
    assert len(semantic_ir["functions"]) == 55
    assert set(gate.SEMANTIC_ROOTS) <= set(semantic_ir["functions"])
    assert {
        "_regular_v4_td3",
        "td3_metric_geometry",
        "_pullback_x64_and_reference15",
        "_relative_bulk_densities_td3",
        "_ghy_density_td3",
        "_foliation_geometry_td3",
        "_interface_component_densities_td3",
    } <= set(semantic_ir["function_ast_sha256"])
    sites = {(row["owner"], row["key"]) for row in semantic_ir["parameter_use_sites"]}
    assert ("_bulk_component_densities_td3", "material_Z5_per_side") in sites
    assert ("_bulk_component_densities_td3", "material_mass_M") in sites
    assert ("_bulk_component_densities_td3", "M5_cubed") in sites
    assert ("_bulk_component_densities_td3", "k_infinity") in sites
    assert ("_interface_component_densities_td3", "M5_cubed") in sites
    assert ("_interface_component_densities_td3", "k_infinity") in sites


def test_wrong_V4_dies_even_if_the_raw_source_SHA_is_repinned(monkeypatch) -> None:
    text = gate.V5671_SOURCE.read_text()
    old = "V4 = _regular_v4_td3(Omega, phi)"
    new = "V4 = _regular_v4_td3(Omega * Omega, phi)"
    assert text.count(old) == 1
    mutant = text.replace(old, new, 1)
    monkeypatch.setitem(
        gate.SOURCE_PINS,
        gate.V5671_SOURCE.name,
        hashlib.sha256(mutant.encode()).hexdigest(),
    )
    audit = gate.audit_source_text(mutant, require_pin=True)
    assert audit["pin_pass"] is True
    assert audit["source_semantic_IR_sha256"] != EXPECTED_SOURCE_SEMANTIC_IR_SHA256
    assert audit["checks"]["transitive_closed_structural_semantic_IR"] is False
    assert audit["pass"] is False


def test_axioms_are_structured_test_local_literal_bound_and_cannot_be_one_equals_zero(monkeypatch) -> None:
    assert gate.AXIOMS == EXPECTED_AXIOMS
    assert _canonical_sha256(EXPECTED_AXIOMS) == EXPECTED_AXIOM_CONTRACT_SHA256
    report = gate.build_report()
    axioms = report["axiom_contract"]
    assert axioms["records"] == list(EXPECTED_AXIOMS)
    assert axioms["sha256"] == EXPECTED_AXIOM_CONTRACT_SHA256
    assert axioms["expected_sha256"] == EXPECTED_AXIOM_CONTRACT_SHA256
    assert axioms["structurally_valid"] is True
    assert axioms["pass"] is True

    monkeypatch.setattr(gate, "AXIOMS", ("1=0",))
    corrupted = gate.build_report()
    assert corrupted["axiom_contract"]["pass"] is False
    assert corrupted["structural_evidence_pass"] is False
    assert corrupted["decision"][RESTRICTED_KEY] is False
    with pytest.raises(gate.ExactCoordinateRealizationError):
        gate.validate_report(corrupted)


TEST_LOCAL_MUTANTS = {
    "coefficient": ('"EH": volume * M5_cubed * scalar_curvature / 2.0', '"EH": volume * M5_cubed * scalar_curvature / 3.0'),
    "bulk_sign": ('"Omega_kinetic": -volume * G * Omega_squared_gradient / 2.0', '"Omega_kinetic": volume * G * Omega_squared_gradient / 2.0'),
    "metric_pullback": ("pulled_metric = _matmul(_matmul(jacobian_transpose, metric, zero), jacobian, zero)", "pulled_metric = _matmul(_matmul(jacobian, metric, zero), jacobian_transpose, zero)"),
    "connection_pullback": ("pulled_connection = _matmul(jacobian_transpose, connection, zero)", "pulled_connection = _matmul(jacobian, connection, zero)"),
    "three_form_pullback": ("minor = _det3(tuple(tuple(jacobian[s][t] for t in target) for s in source))", "minor = _det2(tuple(tuple(jacobian[s][t] for t in target) for s in source))"),
    "BF_orientation": ("orientation = _permutation_sign(triple + complement)", "orientation = -_permutation_sign(triple + complement)"),
    "GHY_normal": ("normal_sign: float = -1.0", "normal_sign: float = 1.0"),
    "Gauss_sign": ("Rcal = projected_riemann + gauss_extrinsic_sign * (K_squared - Ktrace * Ktrace)", "Rcal = projected_riemann + gauss_extrinsic_sign * (Ktrace * Ktrace - K_squared)"),
    "Robin_sign": ("robin_acceleration_sign: float = -1.0", "robin_acceleration_sign: float = 1.0"),
    "bulk_reference": ("actual[sector] - reference[sector]", "reference[sector] - actual[sector]"),
    "GHY_reference_scope": ('components[f"GHY_{side}"] = _ghy_density_td3(\n            boundary_pulled,', 'components[f"GHY_{side}"] = _ghy_density_td3(\n            _boundary_reference,'),
    "shared_producer": ("components.update(_interface_component_densities_td3(boundary))", "components.update({})"),
    "domain_partition": ("for name in BOUNDARY_COMPONENTS:", "for name in BULK_COMPONENTS:"),
    "regular_V4_power": (
        "radial_fourth = Omega**6 * phi_squared**2",
        "radial_fourth = Omega**5 * phi_squared**2",
    ),
    "scalar_curvature_factor_two": (
        '"EH": volume * M5_cubed * scalar_curvature / 2.0',
        '"EH": volume * M5_cubed * (2.0 * scalar_curvature) / 2.0',
    ),
    "curvature_dA_sum": (
        "dconnection[m][n][a]\n                - dconnection[n][m][a]",
        "dconnection[m][n][a]\n                + dconnection[n][m][a]",
    ),
    "embedding_Y_deleted_from_jacobian": (
        "jacobian_rows[4][i] = RhoJet2(Y_first[i])",
        "jacobian_rows[4][i] = zero",
    ),
    "side_determinant_deleted_from_jacobian": (
        "jacobian_rows[4][4] = RhoJet2(SIDE_RADIAL_SIGN[side])",
        "jacobian_rows[4][4] = one",
    ),
    "GHY_factor_two": ("        * theta\n", "        * (2.0 * theta)\n"),
    "projected_Riemann_index_permutation": (
        'geometry["riemann_lower"][a][s][m][n]',
        'geometry["riemann_lower"][a][m][s][n]',
    ),
    "reference_metric_derived_from_actual": (
        "reference = tuple(tuple(RhoJet2(entry) for entry in row) for row in _reference_metric_td3())",
        "reference = metric",
    ),
    "Z5_rebound_to_equal_valued_mass": (
        'Z5 = ACTION_COEFFICIENTS["material_Z5_per_side"]',
        'Z5 = ACTION_COEFFICIENTS["material_mass_M"]',
    ),
    "permutation_sign_inverted": (
        "return -1 if inversions % 2 else 1",
        "return 1 if inversions % 2 else -1",
    ),
    "wrong_V4_call_with_source_rehash": (
        "V4 = _regular_v4_td3(Omega, phi)",
        "V4 = _regular_v4_td3(Omega * Omega, phi)",
    ),
}


def test_all_test_local_coefficient_sign_pullback_and_producer_mutants_fall() -> None:
    text = gate.V5671_SOURCE.read_text()
    for name, (old, new) in TEST_LOCAL_MUTANTS.items():
        assert text.count(old) == 1, name
        mutant = text.replace(old, new, 1)
        audit = gate.audit_source_text(mutant, require_pin=False)
        assert audit["pass"] is False, name
        assert audit["failed_checks"], name
    campaign = gate.build_report()["mutant_campaign"]
    assert campaign["all_mutants_killed"] is True
    assert len(campaign["records"]) == len(TEST_LOCAL_MUTANTS)


def test_typed_geometric_producer_is_an_independent_signature_and_weight_oracle() -> None:
    typed = gate.build_report()["typed_geometric_producer"]
    assert typed["component_order"] == list(EXPECTED_COMPONENTS)
    assert typed["signature_sha256"] == EXPECTED_TYPED_SIGNATURE_SHA256
    assert typed["pass"] is True
    assert all(typed["operator_checks"].values())
    for component in EXPECTED_COMPONENTS:
        expected = EXPECTED_WEIGHTS[_family(component)]
        assert typed["weights"][component] == [expected[0], expected[1], [list(item) for item in expected[2]]]


def test_shared_typed_producer_corruption_cannot_leave_the_predicate_true(monkeypatch) -> None:
    original = gate._typed_geometric_ledger

    def corrupted():
        result = original()
        result["signature_sha256"] = "0" * 64
        result["pass"] = False
        return result

    monkeypatch.setattr(gate, "_typed_geometric_ledger", corrupted)
    report = gate.build_report()
    assert report["decision"][RESTRICTED_KEY] is False
    with pytest.raises(gate.ExactCoordinateRealizationError):
        gate.validate_report(report)


def _permutation_sign(values) -> int:
    inversions = sum(
        values[i] > values[j]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def test_BF_full_permutation_normalization_orientation_and_pairing_are_exact() -> None:
    ledger = gate.build_report()["BF_orientation_and_pairing"]
    assert ledger["sorted_three_subsets"] == 10
    assert ledger["permutation_terms_per_subset"] == [12]
    independently_expected = {
        str(triple): _permutation_sign(triple + tuple(sorted(set(range(5)) - set(triple))))
        for triple in combinations(range(5), 3)
    }
    assert ledger["normalized_coefficients"] == independently_expected
    assert ledger["expected_orientation_coefficients"] == independently_expected
    assert ledger["trace_Ta_Tb"] == [[-2, 0, 0], [0, -2, 0], [0, 0, -2]]
    assert ledger["pairing"] == "<X,Y>=-tr3(XY)/2"
    assert ledger["pullback_determinants"] == {"plus": -1, "minus": 1}
    assert sum(1 for _ in permutations(range(5))) == 120


def test_reference_subtraction_keeps_only_U1_and_does_not_subtract_GHY() -> None:
    reference = gate.build_report()["reference_subtraction"]
    forms = reference["bulk_reference_normal_forms"]
    assert set(forms) == {"EH", "Omega_kinetic", "Omega_potential", "P_kinetic", "full_V4", "BF"}
    assert forms["Omega_potential"] == "-sqrt(abs(det(g_infinity)))*U(1)"
    assert all(forms[name].startswith("0:") for name in forms if name != "Omega_potential")
    assert reference["only_nonzero_bulk_reference_family"] == "Omega_potential"
    assert reference["bulk_subtracted"] is True
    assert reference["GHY_subtracted"] is False
    assert reference["shared_interface_subtracted"] is False
    witness = reference["curved_graph_GHY_counterexample"]
    assert witness["formula"] == "Theta_s=s*Y_second/[b*e*(e^-1+b^-1*Y_prime^2)^(3/2)]"
    assert "s/(4*sqrt(2)) != 0" in witness["exact_specialization"]
    assert reference["planar_fixed_reference"].endswith("Theta_s=0")


def test_parameter_bindings_are_exact_binary64_without_y_squared_substitution() -> None:
    parameters = gate.build_report()["parameter_environment"]
    assert parameters["pass"] is True
    assert parameters["Robin_y_squared_not_substituted_for_Robin_y"] is True
    assert parameters["bindings"]["Robin_y"] == {
        "source_binary64": float(3.0**0.5).hex(),
        "contract_binary64": float(1.7320508075688772).hex(),
        "equal": True,
    }
    assert "Robin_y_squared" not in parameters["bindings"]
    assert set(parameters["formal_weight_symbols_remain_named"]) == {
        "B4_bar", "G", "M", "M5", "Mb", "Z", "eta", "k_infinity", "kappa_hat", "xi"
    }


def test_cli_emits_validated_JSON_and_writes_no_artifact() -> None:
    before = {path: path.stat().st_mtime_ns for path in (HERE / "artifacts").glob("*v5_6_7_7*")}
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)],
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    assert report["decision"][RESTRICTED_KEY] is False
    assert report["structural_evidence_pass"] is True
    assert report["semantic_discharge"]["pass"] is False
    after = {path: path.stat().st_mtime_ns for path in (HERE / "artifacts").glob("*v5_6_7_7*")}
    assert after == before == {}
