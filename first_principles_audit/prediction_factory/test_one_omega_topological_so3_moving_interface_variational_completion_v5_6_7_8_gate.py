#!/usr/bin/env python3
"""Independent tests for the scoped v5.6.7.8 Rcal microlemma."""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE
    / "derive_one_omega_topological_so3_moving_interface_variational_"
    "completion_v5_6_7_8_gate.py"
)
SPEC = importlib.util.spec_from_file_location("v5678_moving_interface", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


EXPECTED_PINS = {
    "derive_one_omega_topological_so3_classical_v5_2_gate.py": (
        "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8"
    ),
    "test_one_omega_topological_so3_classical_v5_2_gate.py": (
        "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26"
    ),
    "one_omega_topological_so3_classical_v5_2_gate.json": (
        "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b"
    ),
    "derive_one_omega_topological_so3_geometric_bulk_diffeomorphism_naturality_v5_6_7_2_gate.py": (
        "23d04b2d8347dca513389e0b4d7c8e329405a2e2eb4989dd1238e0d6dbf2687b"
    ),
    "test_one_omega_topological_so3_geometric_bulk_diffeomorphism_naturality_v5_6_7_2_gate.py": (
        "6a26693799d22dfcba338add59d72260ec61c72ffe969ed8cefbf59a920d7fe6"
    ),
    "derive_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py": (
        "ac290aebfd981e54e5c5a9bda697fb6e23a4c15c4a17e540aa33700c11f7c717"
    ),
    "test_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py": (
        "584192eb81e881fdd31fc60dd6c96926a9dfaac6e7d1dc9a7f5dacad15f8db78"
    ),
    "one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.json": (
        "7c2c3e46ea73b312f753d944e43cd2a2e224d000e5ddd3c3e15ff816e76e441a"
    ),
}

EXPECTED_TRUE_DECISIONS = {
    "corrected_intrinsic_Rcal_interface_variation_exact_pass",
}

EXPECTED_FALSE_DECISIONS = {
    "uniform_N_to_infinity_bridge_pass",
    "bounded_margin_ball_weaker_jet_exact_formula_uniform_bridge_pass",
    "same_functional_symbolic_identity_pass",
    "continuum_action_representative_independence_theorem_pass",
    "global_smooth_physical_gauge_quotient_manifold_pass",
    "fixed_reference_S_rel_diffeomorphism_Ward_pass",
    "two_sided_bulk_GHY_interface_Green_pairing_exact_pass",
    "complete_v5_2_all_field_normal_embedding_pass",
    "complete_moving_embedding_Ward_pass",
    "full_off_shell_Green_theorem_selected_sector_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "C1_N1_promotion_authorized",
    "unrestricted_large_gauge_sector_pass",
    "all_boundary_topologies_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "global_BF_edge_mode_absence_pass",
    "C2_BRST_pass",
    "C3_DOMAIN_pass",
    "C4_HESSIAN_pass",
    "C5_JACOBIANS_pass",
    "C6_ZERO_MODES_pass",
    "C7_REGULATOR_pass",
    "C8_CONTOUR_pass",
    "C9_REDUCTION_pass",
    "C10_INDEPENDENCE_UNITARITY_pass",
    "N2_CONSTRAINTS_pass",
    "N3_CHARACTERISTICS_pass",
    "N4_JUNCTION_BENDING_pass",
    "N5_COUPLED_BVP_pass",
    "N6_GLOBAL_STABILITY_pass",
    "N7_LINEAR_REDUCTION_pass",
    "P4_full_same_action_pass",
    "nonlinear_gravitational_P4_pass",
    "full_P2_pass",
    "B4_pass",
    "B5_pass",
    "global_noncompact_action_finite_pass",
    "publication_authorized",
}

EXPECTED_FALSE_CHECKS = {
    "action_AST_to_all_physical_Euler_rows_derived",
    "K_a_Robin_Euler_coefficients_expanded",
    "shape_row_derived_from_bulk_GHY_interface_action",
    "groupoid_row_derived_from_action",
    "nominal_moving_Ward_candidate_only",
    "two_sided_bulk_GHY_interface_Green_pairing_exact",
    "complete_v5_2_all_field_normal_embedding",
    "complete_moving_embedding_Ward",
    "full_off_shell_Green_theorem_selected_sector",
    "full_classical_variational_principle_selected_sector",
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

EXPECTED_R_CURRENT = (
    "(Mb^2/2)*sqrt(h)*[N*f_R*(D_j*H^ij-D^i*H)-"
    "D_j(N*f_R)*H^ij+D^i(N*f_R)*H]"
)

EXPECTED_LIFT_NORMAL_FORMS_SHA256 = (
    "e7c6765defdad9cc05e2dbd5375c10b6b31b37ca8bd04aac07966a3450f59e4a"
)
EXPECTED_ADM_ACTION_NORMAL_FORMS_SHA256 = (
    "bf2ed2b9404287fc3ef059b3644413547d8c3b71776170c671fae1caaa790940"
)


def _test_local_rows(*terms):
    """Canonical test-local Laurent rows; this never calls producer helpers."""

    combined = {}
    for coefficient, n_power, atom in terms:
        key = (atom, n_power)
        combined[key] = combined.get(key, Fraction(0)) + Fraction(coefficient)
        if not combined[key]:
            del combined[key]
    return [
        {
            "coefficient": [coefficient.numerator, coefficient.denominator],
            "N_power": n_power,
            "atom": atom,
        }
        for (atom, n_power), coefficient in sorted(combined.items())
    ]


def _test_local_expected_lift_normal_forms():
    sym = tuple(f"{i}{j}" for i in range(3) for j in range(i, 3))
    delta_ui = {
        str(i): _test_local_rows((-1, 1, f"D_tau_{i}")) for i in range(3)
    }
    mixed = {
        str(i): _test_local_rows(
            (1, 1, f"D_tau_{i}"), (1, 0, f"H_ui_{i}")
        )
        for i in range(3)
    }
    hij = {key: _test_local_rows((1, 0, f"H_ij_{key}")) for key in sym}
    qij = {
        key: _test_local_rows(
            (1, 0, f"H_ij_{key}"), (-2, 1, f"tau_K_{key}")
        )
        for key in sym
    }
    return {
        "delta_X": _test_local_rows((1, -2, "H_uu"), (2, -1, "U_tau")),
        "delta_N": _test_local_rows(
            (Fraction(-1, 2), 1, "H_uu"), (-1, 2, "U_tau")
        ),
        "delta_u_parallel_coefficient_of_u_covector": _test_local_rows(
            (Fraction(-1, 2), 0, "H_uu")
        ),
        "delta_u_spatial": delta_ui,
        "u_dot_delta_u": _test_local_rows((Fraction(1, 2), 0, "H_uu")),
        "delta_h_uu": [],
        "delta_h_ui": mixed,
        "delta_h_ij": hij,
        "chi_along_u": _test_local_rows((-1, 1, "tau")),
        "Lie_chi_T": _test_local_rows((-1, 0, "tau")),
        "delta_prime_T": [],
        "H_prime_uu": _test_local_rows(
            (2, 1, "A_tau"), (1, 0, "H_uu"), (2, 1, "U_tau")
        ),
        "H_prime_ui": mixed,
        "H_prime_ij": qij,
        "ADM_lapse_n": _test_local_rows(
            (-1, 1, "A_tau"),
            (Fraction(-1, 2), 0, "H_uu"),
            (-1, 1, "U_tau"),
        ),
        "ADM_shift_lower": {
            str(i): _test_local_rows(
                (1, 2, f"D_tau_{i}"), (1, 1, f"H_ui_{i}")
            )
            for i in range(3)
        },
        "ADM_spatial_metric_Q": qij,
    }


EXPECTED_ADM_ACTION_NORMAL_FORMS = {
    "density": {
        "overall_constant": "Mb^2/2",
        "measure": "N*sqrt(h)",
        "f": "xi*Rcal-B4*Rcal^2/(16*k^2)",
        "f_R": "xi-B4*Rcal/(8*k^2)",
        "Gauss_Rcal": "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab",
    },
    "independent_fixed_clock_ADM_variations": {
        "lapse": "n=delta_N/N=-H_prime_uu/2",
        "shift": "v_i=N*H_prime_ui",
        "spatial_metric": "Q_ij=H_prime_ij",
    },
    "Euler_coefficients_inside_N_sqrt_h": {
        "lapse_n": [[1, "f"]],
        "shift_v_i": [0, 0, 0],
        "spatial_metric_Q_ij": [
            [1, 2, "f*h^ij"],
            [-1, 1, "f_R*Rcal^ij"],
            [1, 1, "N^-1*(D^iD^j-h^ij*D^2)(N*f_R)"],
        ],
    },
    "weighted_IBP_current": {
        "prefactor": "(Mb^2/2)*sqrt(h)",
        "terms": [
            [1, "N*f_R", "D_j*Q^ij"],
            [-1, "N*f_R", "D^i*Q"],
            [-1, "D_j(N*f_R)", "Q^ij"],
            [1, "D^i(N*f_R)", "Q"],
        ],
        "free_product_rule_coefficient": "a=N*f_R",
    },
    "d4_current": {
        "spatial_current_multiplicity": 1,
        "source_clock_gauge_vector": "chi=-N*tau*u",
        "gauge_variation_is_subtracted": True,
        "Cartan_term": "+i_(N*tau*u)(l_Rcal)",
        "Cartan_coefficient": 1,
        "Cartan_multiplicity": 1,
        "separate_material_transgression_appended": False,
    },
}


def _dependency_snapshot():
    dependency = gate._dependency_certificate()
    ward = gate._load_ward_report(
        dependency["observed"][gate.V5672_SOURCE.name]
    )
    return dependency, ward


@pytest.fixture(scope="module")
def report():
    return gate.build_report()


def test_only_the_intrinsic_Rcal_microlemma_is_promoted(report) -> None:
    decision = report["decision"]
    assert {key for key, value in decision.items() if value} == EXPECTED_TRUE_DECISIONS
    assert {key for key, value in decision.items() if not value} == EXPECTED_FALSE_DECISIONS
    assert set(decision) == EXPECTED_TRUE_DECISIONS | EXPECTED_FALSE_DECISIONS
    assert gate.TRUE_DECISION_KEYS == EXPECTED_TRUE_DECISIONS
    assert gate.FALSE_DECISION_KEYS == EXPECTED_FALSE_DECISIONS
    assert {key for key, value in report["checks"].items() if not value} == EXPECTED_FALSE_CHECKS


def test_all_dependencies_are_byte_pinned_with_test_local_hashes(report) -> None:
    pins = report["source_pins"]
    assert pins["pass"] is True
    assert pins["expected"] == EXPECTED_PINS
    assert pins["milestone_commits"] == {
        "60aa1a0": "oriented BF incidence",
        "acd7787": "scoped literal Green ledger",
        "91abcc1": "compact-support differentiated interior bulk Ward",
    }
    for name, expected in EXPECTED_PINS.items():
        path = gate.PINNED_PATHS[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        assert pins["observed"][name] == expected
        assert pins["matches"][name] is True
    assert pins["wrong_v5_5_4_primary_or_redteam_consumed_as_lemma"] is False
    assert pins["Gauss_exact_witnesses_consumed"] is True


def test_v52_literal_and_corrigendum_are_semantically_bound(report) -> None:
    pins = report["source_pins"]
    assert pins["v5_2_canonical_exact_action_sha256"] == (
        "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
    )
    assert pins["v5_2_foliation_literal"] == (
        "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-"
        "lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
        "B4_bar*Rcal^2/(16*k_infinity^2)]"
    )
    assert pins["correct_Gauss_formula"] == (
        "R_leaf=h^ac h^bd R_abcd-K^2+K_ab K^ab="
        "R4+2 Ricci(u,u)-K^2+K_ab K^ab"
    )
    assert pins["correct_Gauss_formula_normalized"] == (
        "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab"
    )
    assert pins["intrinsic_f_monomials_read_from_v5_2_literal"] == [
        ["xi", 1, 1],
        ["-B4/(16*k^2)", 1, 2],
    ]
    assert pins["intrinsic_df_dR_monomials_from_exponent_rule"] == [
        ["xi", 1, 0],
        ["-B4/(16*k^2)", 2, 1],
    ]


def test_corrected_Gauss_and_polynomial_derivative_are_exact(report) -> None:
    row = report["corrected_intrinsic_Rcal_variation"]
    assert row["corrected_Gauss_normal_form"] == {
        "projected_ambient_Riemann": 1,
        "K_trace_squared": -1,
        "K_tensor_squared": 1,
    }
    assert row["Rcal_formula"] == "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab"
    assert row["polynomial"] == {
        "f_monomials": [["xi", 1, 1], ["-B4/(16*k^2)", 1, 2]],
        "df_dR_monomials": [["xi", 1, 0], ["-B4/(16*k^2)", 2, 1]],
        "f_formula": "xi*Rcal-B4*Rcal^2/(16*k^2)",
        "df_dR_formula": "xi-B4*Rcal/(8*k^2)",
    }
    assert row["metric_variation_before_IBP"] == (
        "delta_Rcal=-Rcal^ij*H_ij+D^i*D^j*H_ij-D^2*(h^ij*H_ij)"
    )
    assert row["spatial_current_theta_Rcal_i"] == EXPECTED_R_CURRENT
    assert row["shift_Euler_coefficient"] == "0"
    assert row["Euler_equations_imposed"] is False
    assert row["uses_v5_5_4_wrong_intrinsic_formula"] is False


def _test_local_symbolic_R_polynomials():
    """Independent product expansion using tuple-valued formal variables."""

    dim = 3
    raw: dict[tuple[str, ...], int] = {}
    bulk: dict[tuple[str, ...], int] = {}
    div: dict[tuple[str, ...], int] = {}

    def add(dst, coefficient, *parts):
        key = tuple(sorted(parts))
        dst[key] = dst.get(key, 0) + coefficient
        if dst[key] == 0:
            del dst[key]

    def ij(i, j):
        return f"{min(i,j)}{max(i,j)}"

    for i in range(dim):
        for j in range(dim):
            add(raw, 1, "a", f"DDH_{ij(i,j)}_{ij(i,j)}")
            add(raw, -1, "a", f"DDH_{ij(i,i)}_{ij(j,j)}")
            add(bulk, 1, f"DDa_{ij(i,j)}", f"H_{ij(i,j)}")
            add(bulk, -1, f"DDa_{ij(i,i)}", f"H_{ij(j,j)}")
            add(div, 1, f"Da_{i}", f"DH_{j}_{ij(i,j)}")
            add(div, 1, "a", f"DDH_{ij(i,j)}_{ij(i,j)}")
            add(div, -1, f"Da_{i}", f"DH_{i}_{ij(j,j)}")
            add(div, -1, "a", f"DDH_{ij(i,i)}_{ij(j,j)}")
            add(div, -1, f"DDa_{ij(i,j)}", f"H_{ij(i,j)}")
            add(div, -1, f"Da_{j}", f"DH_{i}_{ij(i,j)}")
            add(div, 1, f"DDa_{ij(i,i)}", f"H_{ij(j,j)}")
            add(div, 1, f"Da_{i}", f"DH_{i}_{ij(j,j)}")
    residual = dict(raw)
    for source in (bulk, div):
        for monomial, coefficient in source.items():
            add(residual, -coefficient, *monomial)
    assert not residual
    return raw, bulk, div


def _decode_symbolic_rows(rows):
    return {
        tuple(row["factors"]): int(row["coefficient"])
        for row in rows
    }


def test_Rcal_current_is_a_free_polynomial_identity_not_one_sample(report) -> None:
    oracle_raw, oracle_bulk, oracle_div = _test_local_symbolic_R_polynomials()
    proof = report["corrected_intrinsic_Rcal_variation"]["free_symbolic_product_rule"]
    assert proof["leaf_dimension"] == 3
    assert proof["numeric_values_substituted"] is False
    assert proof["free_polynomial_identity_exact_pass"] is True
    assert proof["normalized_residual"] == []
    assert _decode_symbolic_rows(proof["raw"]) == oracle_raw
    assert _decode_symbolic_rows(proof["bulk_after_IBP"]) == oracle_bulk
    assert _decode_symbolic_rows(proof["expanded_divergence"]) == oracle_div


def test_nonvacuous_fraction_oracle_checks_the_same_current_sign(report) -> None:
    witness = report["corrected_intrinsic_Rcal_variation"]["exact_product_rule_witness"]
    assert witness["dimension"] == 3
    assert witness["nonzero_raw_witness"] is True
    assert witness["nonzero_current_witness"] is True
    assert witness["exact_pass"] is True
    raw = Fraction(*witness["raw_second_derivative_part"])
    bulk = Fraction(*witness["bulk_after_IBP_part"])
    divergence = Fraction(*witness["expanded_divergence_part"])
    residual = Fraction(*witness["residual"])
    assert raw != 0 and divergence != 0
    assert raw == bulk + divergence
    assert residual == 0


def test_arbitrary_metric_clock_variation_lifts_exactly_to_ADM(report) -> None:
    lift = report["corrected_intrinsic_Rcal_variation"]["full_gamma_T_to_ADM_lift"]
    assert lift["exact_pass"] is True
    assert lift["arbitrary_variations"] == {
        "metric": "H_mu_nu=delta gamma_mu_nu",
        "clock": "tau=delta T",
        "free_components": [
            "H_uu",
            "H_ui[3]",
            "H_ij[6]",
            "U_tau=u^mu*D_mu(tau)",
            "D_tau_i[3]",
        ],
        "N_is_invertible_Laurent_indeterminate": True,
        "N_numeric_value_substituted_in_proof": False,
    }
    assert lift["adapted_clock_gauge"] == {
        "vector": "chi^mu=-N_T*tau*u^mu",
        "delta_prime_T": "tau+Lie_chi(T)=0",
        "metric_variation": "H_prime=H+Lie_chi(gamma)",
        "Cartan_current_retains_original_tau": True,
    }
    expected = _test_local_expected_lift_normal_forms()
    assert lift["normal_forms"] == expected
    encoded = json.dumps(
        expected,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == EXPECTED_LIFT_NORMAL_FORMS_SHA256
    assert lift["normal_forms_sha256"] == EXPECTED_LIFT_NORMAL_FORMS_SHA256
    residuals = lift["free_polynomial_residuals"]
    assert len(residuals) == 28
    assert all(value == [] for value in residuals.values())
    assert lift["all_free_polynomial_residuals_zero"] is True
    assert lift["ADM_variations"] == {
        "lapse": "n=delta N/N=-H_prime_uu/2",
        "background_shift": (
            "N^i arbitrary; H_prime_0i-N^j*H_prime_ji=N*H_prime_ui"
        ),
        "shift": "v_i=N_T*H_prime_ui; v_i is arbitrary",
        "spatial_metric": "Q_ij=H_prime_ij; Q_ij is arbitrary symmetric",
        "f_Rcal_shift_Euler_coefficient": "0",
    }


def _test_local_evaluate_rows(rows, N_value, atoms):
    return sum(
        Fraction(*row["coefficient"])
        * N_value ** int(row["N_power"])
        * atoms[row["atom"]]
        for row in rows
    )


def test_fraction_witness_is_nonzero_and_evaluates_every_lift_row(report) -> None:
    lift = report["corrected_intrinsic_Rcal_variation"]["full_gamma_T_to_ADM_lift"]
    witness = lift["nonvacuous_fraction_witness"]
    N_value = Fraction(*witness["N"])
    atoms = {name: Fraction(*value) for name, value in witness["inputs"].items()}
    outputs = {name: Fraction(*value) for name, value in witness["outputs"].items()}
    forms = _test_local_expected_lift_normal_forms()
    assert N_value == Fraction(7, 3) and N_value != 1
    assert len(atoms) == 25 and all(value != 0 for value in atoms.values())
    assert len(outputs) == 25 and all(value != 0 for value in outputs.values())
    assert outputs["delta_N"] == _test_local_evaluate_rows(forms["delta_N"], N_value, atoms)
    assert outputs["delta_u_parallel"] == _test_local_evaluate_rows(
        forms["delta_u_parallel_coefficient_of_u_covector"], N_value, atoms
    )
    for i in range(3):
        assert outputs[f"delta_u_spatial_{i}"] == _test_local_evaluate_rows(
            forms["delta_u_spatial"][str(i)], N_value, atoms
        )
        assert outputs[f"delta_h_ui_{i}"] == _test_local_evaluate_rows(
            forms["delta_h_ui"][str(i)], N_value, atoms
        )
        assert outputs[f"ADM_shift_{i}"] == _test_local_evaluate_rows(
            forms["ADM_shift_lower"][str(i)], N_value, atoms
        )
    for key in ("00", "01", "02", "11", "12", "22"):
        assert outputs[f"delta_h_ij_{key}"] == _test_local_evaluate_rows(
            forms["delta_h_ij"][key], N_value, atoms
        )
        assert outputs[f"ADM_metric_{key}"] == _test_local_evaluate_rows(
            forms["ADM_spatial_metric_Q"][key], N_value, atoms
        )
    assert outputs["ADM_lapse_n"] == _test_local_evaluate_rows(
        forms["ADM_lapse_n"], N_value, atoms
    )
    assert outputs["chi_generator"] == _test_local_evaluate_rows(
        forms["chi_along_u"], N_value, atoms
    )
    assert witness["all_independent_inputs_nonzero"] is True
    assert witness["all_lapse_shift_metric_and_tensor_outputs_nonzero"] is True


def test_ADM_Euler_weighted_current_and_Cartan_rows_are_test_local(report) -> None:
    row = report["corrected_intrinsic_Rcal_variation"]
    action = row["ADM_action_normal_forms"]
    assert action == EXPECTED_ADM_ACTION_NORMAL_FORMS
    encoded = json.dumps(
        EXPECTED_ADM_ACTION_NORMAL_FORMS,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == EXPECTED_ADM_ACTION_NORMAL_FORMS_SHA256
    assert row["ADM_action_normal_forms_sha256"] == EXPECTED_ADM_ACTION_NORMAL_FORMS_SHA256
    assert action["Euler_coefficients_inside_N_sqrt_h"]["shift_v_i"] == [0, 0, 0]
    assert action["d4_current"]["Cartan_term"] == "+i_(N*tau*u)(l_Rcal)"
    assert action["d4_current"]["Cartan_coefficient"] == 1
    assert action["d4_current"]["Cartan_multiplicity"] == 1


def test_d4_current_keeps_clock_Cartan_piece_and_compact_support(report) -> None:
    row = report["corrected_intrinsic_Rcal_variation"]
    assert row["d4_current"] == (
        "Theta_Rcal^mu=(0,theta_Rcal^i)+i_{N_T*tau*u}l_Rcal; "
        "d4 Theta_Rcal=partial_mu Theta_Rcal^mu"
    )
    assert row["compact_support_on_Sigma_removes_integrated_d4_flux"] is True
    assert row["T_variation_is_not_frozen"] is True
    assert "E_T=D_nu" in row["khronon_chain_rule"]


def test_generic_IBP_and_role_coverage_are_explicitly_nonpromoting(report) -> None:
    universal = report["universal_second_jet_Euler_Green_identity"]
    assert universal["proof_count"] == 45
    assert universal["field_jet_rows_exact"] is True
    assert universal["all_normalized_residuals_zero"] is True
    assert universal["no_Euler_equation_imposed"] is True
    assert report["variation_role_coverage"]["all_required_roles_covered"] is True
    assert report["checks"]["nominal_role_coverage_candidate_only"] is True
    assert report["checks"]["action_AST_to_all_physical_Euler_rows_derived"] is False
    assert report["checks"]["K_a_Robin_Euler_coefficients_expanded"] is False
    assert report["decision"]["complete_v5_2_all_field_normal_embedding_pass"] is False
    assert report["decision"]["C1_N1_promotion_authorized"] is False


def test_pinned_green_GHY_BF_rows_are_diagnostic_not_a_new_theorem(report) -> None:
    assert tuple(report["literal_action_inventory"]["actual"]) == EXPECTED_COMPONENTS
    green = report["two_sided_bulk_GHY_interface_Green_pairing"]
    assert green["rows_exact"] is True
    assert green["GHY"]["outward_normal_signs"] == {"plus": -1, "minus": 1}
    assert green["GHY"]["normal_derivative_of_H_remaining"] is False
    assert green["BF"]["boundary_pairing"] == "-<b_plus-b_minus,Delta A_Sigma>"
    assert green["BF"]["off_shell_flux_is_not_cancelled"] is True
    assert report["checks"]["candidate_two_sided_bulk_GHY_rows_match_pinned_ledger"] is True
    assert report["decision"]["two_sided_bulk_GHY_interface_Green_pairing_exact_pass"] is False


def test_shape_and_groupoid_templates_cannot_promote_C1_even_if_self_consistent(
    report, monkeypatch
) -> None:
    dependency, ward = _dependency_snapshot()
    original_shape = gate._shape_equation

    def jointly_wrong_shape(mutation=None):
        row = original_shape(mutation)
        for side in row["actual_normal_shape_rows"]:
            row["actual_normal_shape_rows"][side][0][0] = 7
            row["independent_expected_normal_shape_rows"][side][0][0] = 7
        row["shape_rows_exact"] = True
        return row

    monkeypatch.setattr(gate, "_shape_equation", jointly_wrong_shape)
    attacked = gate.build_report(
        dependency=dependency,
        ward_dependency=ward,
    )
    assert attacked["normal_embedding_shape_equation"]["shape_rows_exact"] is True
    assert attacked["normal_embedding_shape_equation"]["proof_status"] == (
        "unproved_diagnostic_do_not_consume"
    )
    assert attacked["normal_embedding_shape_equation"][
        "shape_row_proved_from_literal_action"
    ] is False
    assert attacked["normal_embedding_shape_equation"][
        "known_missing_Legendre_boundary_structure"
    ] == "i_n(L)-Theta_bulk(L_n q), with orientation fixed per side"
    assert attacked["normal_embedding_shape_equation"]["one_dimensional_oracle"] == (
        "(ell_q-p)*Delta_q+f*(L-p_n*partial_n_q), convention dependent"
    )
    assert attacked["checks"]["shape_row_derived_from_bulk_GHY_interface_action"] is False
    assert attacked["decision"]["complete_moving_embedding_Ward_pass"] is False
    assert attacked["decision"]["C1_N1_promotion_authorized"] is False


def test_shared_expected_helper_mutation_cannot_rescue_wrong_Gauss(monkeypatch) -> None:
    dependency, ward = _dependency_snapshot()
    original_expected = gate._expected_intrinsic_Rcal_normal_form

    def jointly_wrong_expected():
        row = original_expected()
        row["Gauss"] = {
            "projected_ambient_Riemann": 1,
            "K_trace_squared": 1,
            "K_tensor_squared": -1,
        }
        return row

    monkeypatch.setattr(gate, "_expected_intrinsic_Rcal_normal_form", jointly_wrong_expected)
    attacked = gate.build_report(
        "wrong_Gauss_sign",
        dependency=dependency,
        ward_dependency=ward,
    )
    assert attacked["corrected_intrinsic_Rcal_variation"]["corrected_Gauss_normal_form"] == jointly_wrong_expected()["Gauss"]
    # The external corrigendum binding is independent of the replaced target.
    assert attacked["checks"]["corrected_intrinsic_Rcal_interface_variation_exact"] is False
    assert attacked["decision"]["corrected_intrinsic_Rcal_interface_variation_exact_pass"] is False


@pytest.mark.parametrize(
    "attack",
    [
        "wrong_deltaN_power",
        "zero_deltaU",
        "wrong_deltaH",
        "wrong_projector",
        "wrong_chi",
        "zero_witness_with_forged_flags",
    ],
)
def test_monkeypatched_lift_cannot_hide_behind_exact_pass(
    attack, monkeypatch
) -> None:
    dependency, ward = _dependency_snapshot()
    original = gate._clock_metric_lift_certificate

    def forged(mutation=None):
        row = copy.deepcopy(original(mutation))
        forms = row["normal_forms"]
        if attack == "wrong_deltaN_power":
            forms["delta_N"][0]["N_power"] = 0
        elif attack == "zero_deltaU":
            forms["delta_u_parallel_coefficient_of_u_covector"] = []
            forms["delta_u_spatial"] = {"0": [], "1": [], "2": []}
        elif attack == "wrong_deltaH":
            forms["delta_h_ij"]["12"] = []
        elif attack == "wrong_projector":
            forms["delta_h_ui"]["0"][0]["coefficient"] = [-1, 1]
        elif attack == "wrong_chi":
            forms["chi_along_u"][0]["coefficient"] = [1, 1]
        elif attack == "zero_witness_with_forged_flags":
            row["nonvacuous_fraction_witness"]["inputs"] = {
                name: [0, 1]
                for name in row["nonvacuous_fraction_witness"]["inputs"]
            }
            row["nonvacuous_fraction_witness"]["outputs"] = {
                name: [0, 1]
                for name in row["nonvacuous_fraction_witness"]["outputs"]
            }
            row["nonvacuous_fraction_witness"]["all_independent_inputs_nonzero"] = True
            row["nonvacuous_fraction_witness"][
                "all_lapse_shift_metric_and_tensor_outputs_nonzero"
            ] = True
        row["normal_forms_sha256"] = gate._canonical_sha256(forms)
        row["free_polynomial_residuals"] = {
            name: [] for name in row["free_polynomial_residuals"]
        }
        row["all_free_polynomial_residuals_zero"] = True
        row["exact_pass"] = True
        return row

    monkeypatch.setattr(gate, "_clock_metric_lift_certificate", forged)
    attacked = gate.build_report(
        "wrong_GHY_outward_sign", dependency=dependency, ward_dependency=ward
    )
    assert attacked["checks"]["corrected_intrinsic_Rcal_interface_variation_exact"] is False
    assert attacked["decision"]["corrected_intrinsic_Rcal_interface_variation_exact_pass"] is False


@pytest.mark.parametrize(
    "attack",
    [
        "wrong_lapse_factor",
        "nonzero_shift",
        "omit_weighted_current",
        "flip_weighted_current",
        "omit_Cartan",
        "double_Cartan",
        "flip_Cartan",
    ],
)
def test_monkeypatched_ADM_and_Cartan_rows_cannot_rehash_themselves(
    attack, monkeypatch
) -> None:
    dependency, ward = _dependency_snapshot()
    original = gate._Rcal_ADM_action_normal_forms

    def forged(mutation, *, current_present, current_sign):
        row = copy.deepcopy(
            original(
                mutation,
                current_present=current_present,
                current_sign=current_sign,
            )
        )
        if attack == "wrong_lapse_factor":
            row["Euler_coefficients_inside_N_sqrt_h"]["lapse_n"] = [[2, "f"]]
        elif attack == "nonzero_shift":
            row["Euler_coefficients_inside_N_sqrt_h"]["shift_v_i"][0] = 1
        elif attack == "omit_weighted_current":
            row["weighted_IBP_current"]["terms"] = []
        elif attack == "flip_weighted_current":
            for term in row["weighted_IBP_current"]["terms"]:
                term[0] *= -1
        elif attack == "omit_Cartan":
            row["d4_current"]["Cartan_coefficient"] = 0
            row["d4_current"]["Cartan_multiplicity"] = 0
        elif attack == "double_Cartan":
            row["d4_current"]["Cartan_coefficient"] = 2
            row["d4_current"]["Cartan_multiplicity"] = 2
        elif attack == "flip_Cartan":
            row["d4_current"]["Cartan_coefficient"] = -1
        return row

    monkeypatch.setattr(gate, "_Rcal_ADM_action_normal_forms", forged)
    attacked = gate.build_report(
        "wrong_GHY_outward_sign", dependency=dependency, ward_dependency=ward
    )
    # The producer recomputes its own hash.  The test-local pinned normal form
    # and the independent literal comparisons still reject it.
    assert attacked["corrected_intrinsic_Rcal_variation"][
        "ADM_action_normal_forms_sha256"
    ] != EXPECTED_ADM_ACTION_NORMAL_FORMS_SHA256
    assert attacked["checks"]["corrected_intrinsic_Rcal_interface_variation_exact"] is False
    assert attacked["decision"]["corrected_intrinsic_Rcal_interface_variation_exact_pass"] is False


def test_jointly_wrong_producer_and_expected_helper_cannot_rescue_current(
    monkeypatch,
) -> None:
    dependency, ward = _dependency_snapshot()
    original_intrinsic = gate._intrinsic_Rcal_variation
    original_expected = gate._expected_intrinsic_Rcal_normal_form

    def jointly_wrong_intrinsic(mutation=None):
        row = copy.deepcopy(original_intrinsic(mutation))
        row["spatial_current_theta_Rcal_i"] = "JOINTLY_WRONG_CURRENT"
        return row

    def jointly_wrong_expected():
        row = copy.deepcopy(original_expected())
        row["current_formula"] = "JOINTLY_WRONG_CURRENT"
        return row

    monkeypatch.setattr(gate, "_intrinsic_Rcal_variation", jointly_wrong_intrinsic)
    monkeypatch.setattr(gate, "_expected_intrinsic_Rcal_normal_form", jointly_wrong_expected)
    attacked = gate.build_report(
        "wrong_GHY_outward_sign", dependency=dependency, ward_dependency=ward
    )
    assert attacked["corrected_intrinsic_Rcal_variation"][
        "spatial_current_theta_Rcal_i"
    ] == jointly_wrong_expected()["current_formula"]
    assert attacked["checks"]["corrected_intrinsic_Rcal_interface_variation_exact"] is False
    assert attacked["decision"]["corrected_intrinsic_Rcal_interface_variation_exact_pass"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_Gauss_sign",
        "wrong_R2_derivative_factor",
        "wrong_Rcal_current_sign",
        "wrong_clock_Cartan_sign",
        "wrong_N_powers",
        "wrong_deltaN_sign",
        "wrong_projector",
        "wrong_chi",
        "wrong_deltaN",
        "zero_deltaN",
        "wrong_deltaU",
        "zero_deltaU",
        "wrong_deltaH",
        "zero_deltaH",
        "wrong_lapse_factor",
        "nonzero_shift_coefficient",
        "omit_clock_Cartan",
        "double_clock_Cartan",
        "zero_lift_witness",
        "omit_intrinsic_d4_current",
        "freeze_T",
    ],
)
def test_every_microlemma_mutant_is_killed(mutation) -> None:
    dependency, ward = _dependency_snapshot()
    attacked = gate.build_report(
        mutation,
        dependency=dependency,
        ward_dependency=ward,
    )
    assert attacked["checks"]["corrected_intrinsic_Rcal_interface_variation_exact"] is False
    assert attacked["decision"]["corrected_intrinsic_Rcal_interface_variation_exact_pass"] is False
    assert attacked["decision"]["C1_N1_promotion_authorized"] is False


def test_all_requested_broader_attacks_remain_fail_closed(report) -> None:
    campaign = gate.mutant_campaign(
        dependency=report["source_pins"],
        ward_dependency=gate._load_ward_report(
            report["source_pins"]["observed"][gate.V5672_SOURCE.name]
        ),
    )
    assert campaign["mutant_count"] == 33
    assert campaign["all_killed"] is True
    expected_micro = {
        "wrong_Gauss_sign",
        "wrong_R2_derivative_factor",
        "wrong_Rcal_current_sign",
        "wrong_clock_Cartan_sign",
        "wrong_N_powers",
        "wrong_deltaN_sign",
        "wrong_projector",
        "wrong_chi",
        "wrong_deltaN",
        "zero_deltaN",
        "wrong_deltaU",
        "zero_deltaU",
        "wrong_deltaH",
        "zero_deltaH",
        "wrong_lapse_factor",
        "nonzero_shift_coefficient",
        "omit_clock_Cartan",
        "double_clock_Cartan",
        "zero_lift_witness",
        "omit_intrinsic_d4_current",
        "freeze_T",
    }
    for name, row in campaign["rows"].items():
        assert row["killed"] is True
        assert row["attacks_accepted_microlemma"] is (name in expected_micro)
        if name not in expected_micro:
            assert row["accepted_microlemma_survives_when_attack_is_out_of_scope"] is True
            assert "C1_N1_promotion_authorized" not in row["true_decision_keys"]


def test_source_has_no_artifact_writer_or_route_c_dependency() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert "write_text" not in calls
    assert "write_bytes" not in calls
    assert "open" not in calls
    assert all("route_c" not in name.lower() for name in gate.PINNED_INPUTS)
    assert "v5_5_4_gate.py" not in gate.PINNED_INPUTS
    assert "v5_5_4_redteam.py" not in gate.PINNED_INPUTS


def test_main_emits_the_same_fail_closed_report_without_writing_artifacts(report) -> None:
    artifact_names_before = {
        path.name for path in (HERE / "artifacts").glob("*v5_6_7_8*")
    }
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)],
        cwd=HERE.parents[1],
        check=True,
        capture_output=True,
        text=True,
    )
    emitted = json.loads(completed.stdout)
    artifact_names_after = {
        path.name for path in (HERE / "artifacts").glob("*v5_6_7_8*")
    }
    assert emitted["schema"] == gate.SCHEMA
    assert emitted["decision"] == report["decision"]
    assert emitted["mutant_campaign"]["all_killed"] is True
    assert artifact_names_after == artifact_names_before == set()
