#!/usr/bin/env python3
"""Independent tests for the narrow v5.6.7.12 intrinsic R/R^2 split."""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys

import pytest


HERE = Path(__file__).resolve().parent
MODULE_PATH = (
    HERE
    / "derive_one_omega_topological_so3_intrinsic_r_r2_split_v5_6_7_12_gate.py"
)
SPEC = importlib.util.spec_from_file_location("v56712_intrinsic_r_r2_split", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


EXPECTED_PRODUCER_SHA256 = (
    "1ee423bd8da0b5536ca3a4585e22b750fef440caede8a07024bb2ecc92728d2a"
)
EXPECTED_V5678_SHA256 = {
    "derive_one_omega_topological_so3_moving_interface_variational_completion_v5_6_7_8_gate.py": (
        "18eb511418017a86c05ba506d3c6dac7c13b10b39ebdad607d8143d9a2872acb"
    ),
    "test_one_omega_topological_so3_moving_interface_variational_completion_v5_6_7_8_gate.py": (
        "9e8fab34d1e8d877a0e2ab799bec9ea26e40a05f8c63d4a333d0ea8d2664b0a0"
    ),
}
EXPECTED_V5678_BLOBS = {
    "derive_one_omega_topological_so3_moving_interface_variational_completion_v5_6_7_8_gate.py": (
        "ae8c029b646569a67e2e1180a59b8cbd0afbcba5"
    ),
    "test_one_omega_topological_so3_moving_interface_variational_completion_v5_6_7_8_gate.py": (
        "e44017431a2496f1bd333e08bab17e3eb3dba0bb"
    ),
}
EXPECTED_V5678_COMMIT = "85585849fa65411a33330ce3822e03c77b067ad7"
EXPECTED_V52_ACTION_SHA256 = (
    "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
)
EXPECTED_V52_LITERAL = (
    "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*["
    "Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
    "B4_bar*Rcal^2/(16*k_infinity^2)]"
)
EXPECTED_BLOCKS_SHA256 = (
    "fd25b86f601c517ce7648581e91b2275ea28535919bad12e36b7955ac3025eb3"
)
EXPECTED_ADAPTER_SHA256 = (
    "bf2ed2b9404287fc3ef059b3644413547d8c3b71776170c671fae1caaa790940"
)
EXPECTED_BLOCK_SCHEMA = (
    "holo.one-omega-topological-so3-intrinsic-r-r2-"
    "post-adjoint-component-row-v1"
)
EXPECTED_SLOT_SCHEMA = (
    "holo.one-omega-topological-so3-intrinsic-r-r2-"
    "component-local-scalar-slot-v1"
)
EXPECTED_CURRENT_COEFFICIENT_SCHEMA = (
    "holo.one-omega-topological-so3-intrinsic-r-r2-"
    "component-local-current-coefficient-v1"
)
EXPECTED_COMPONENTS = ("R", "R_squared")
EXPECTED_NEW_REPIN_MUTANTS = {
    "shared_oracle_swap",
    "wrong_literal_derivative_expression",
    "wrong_Gauss_formula",
    "wrong_weighted_current_terms",
    "wrong_Cartan_term",
    "wrong_component_label",
    "wrong_component_ordinal",
    "wrong_source_span",
    "wrong_side",
    "wrong_domain",
    "extra_public_field",
    "swap_aggregate_components_after_repin",
    "combined_swap_relabel_and_unconsumed_fields_after_repin",
}

EXPECTED_TRUE = {
    "literal_v5_2_R_R_squared_component_split_byte_bound_pass",
    "componentwise_R_R_squared_polynomial_derivative_exact_pass",
    "componentwise_R_R_squared_post_adjoint_Euler_Green_split_exact_pass",
    "R_R_squared_sum_reconstructs_v5_6_7_8_normal_form_pass",
    "R_R_squared_no_cross_cancellation_pass",
}
EXPECTED_FALSE = {
    "raw_action_AST_Frechet_rows_recovered_pass",
    "FrechetRowV1_adapter_export_pass",
    "raw_Frechet_to_post_adjoint_bridge_pass",
    "K_a_Robin_componentwise_variation_pass",
    "all_twenty_components_componentwise_variation_pass",
    "moving_embedding_shape_equation_pass",
    "full_off_shell_Green_theorem_selected_sector_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "C1_N1_promotion_authorized",
    "publication_authorized",
}


def _expected_causal_source_paths():
    paths = set()
    for component in ("R", "R_squared"):
        paths.update(
            f"{component}.density_context.{field}"
            for field in ("overall_constant", "measure")
        )
        paths.update(
            f"{component}.independent_fixed_clock_ADM_variations.{field}"
            for field in ("lapse", "shift", "spatial_metric")
        )
        paths.update(
            f"{component}.adapter_aliases.{field}"
            for field in ("xi", "B4_bar", "k_infinity", "Rcal")
        )
        paths.update(
            f"{component}.Gauss.{field}"
            for field in (
                "projected_ambient_Riemann",
                "K_trace_squared",
                "K_tensor_squared",
            )
        )
        for slot in ("component_action", "component_derivative"):
            paths.add(
                f"{component}.scalar_slots.{slot}.polynomial.0.coefficient"
            )
            paths.add(f"{component}.scalar_slots.{slot}.polynomial.0.powers")
        paths.update(
            {
                f"{component}.Euler_coefficients_inside_N_sqrt_h.lapse_n.0.rational",
                f"{component}.Euler_coefficients_inside_N_sqrt_h.lapse_n.0.tensor",
            }
        )
        for index, payload in enumerate(("tensor", "tensor", "operator")):
            base = (
                f"{component}.Euler_coefficients_inside_N_sqrt_h."
                f"spatial_metric_Q_ij.{index}"
            )
            paths.update({f"{base}.rational", f"{base}.{payload}"})
        paths.update(
            f"{component}.Euler_coefficients_inside_N_sqrt_h.shift_v_i.{index}"
            for index in range(3)
        )
        paths.update(
            {
                f"{component}.weighted_IBP_current.present",
                f"{component}.weighted_IBP_current.prefactor",
                f"{component}.weighted_IBP_current.coefficient.operator",
            }
        )
        for index in range(4):
            base = f"{component}.weighted_IBP_current.terms.{index}"
            paths.update({f"{base}.rational", f"{base}.operator"})
        paths.update(
            f"{component}.d4_Cartan_current.{field}"
            for field in (
                "operator.operator",
                "occurrences",
                "source_clock_gauge_vector",
                "gauge_variation_is_subtracted",
                "separate_material_transgression_appended",
            )
        )
    return paths

R_ACTION_ROW = [
    {
        "coefficient": [1, 1],
        "powers": [["xi", 1], ["Rcal", 1]],
    }
]
R_DERIVATIVE_ROW = [
    {"coefficient": [1, 1], "powers": [["xi", 1]]}
]
R2_ACTION_ROW = [
    {
        "coefficient": [-1, 16],
        "powers": [["B4_bar", 1], ["k_infinity", -2], ["Rcal", 2]],
    }
]
R2_DERIVATIVE_ROW = [
    {
        "coefficient": [-1, 8],
        "powers": [["B4_bar", 1], ["k_infinity", -2], ["Rcal", 1]],
    }
]

def _slot_ref(kind, component):
    return {
        "schema": EXPECTED_SLOT_SCHEMA,
        "kind": kind,
        "component": component,
    }


def _expected_operator_template(component):
    action = _slot_ref("component_action", component)
    derivative = _slot_ref("component_derivative", component)
    return {
        "Euler_coefficients_inside_N_sqrt_h": {
            "lapse_n": [
                {"rational": [1, 1], "scalar_slot": action, "tensor": "1"}
            ],
            "shift_v_i": [0, 0, 0],
            "spatial_metric_Q_ij": [
                {
                    "rational": [1, 2],
                    "scalar_slot": action,
                    "tensor": "h^ij",
                },
                {
                    "rational": [-1, 1],
                    "scalar_slot": derivative,
                    "tensor": "Rcal^ij",
                },
                {
                    "rational": [1, 1],
                    "scalar_slot": derivative,
                    "operator": "N^-1*(D^iD^j-h^ij*D^2)(N*())",
                },
            ],
        },
        "weighted_IBP_current_terms": [
            {
                "rational": [1, 1],
                "scalar_slot": derivative,
                "operator": "N*()*D_j*Q^ij",
            },
            {
                "rational": [-1, 1],
                "scalar_slot": derivative,
                "operator": "N*()*D^i*Q",
            },
            {
                "rational": [-1, 1],
                "scalar_slot": derivative,
                "operator": "D_j(N*())*Q^ij",
            },
            {
                "rational": [1, 1],
                "scalar_slot": derivative,
                "operator": "D^i(N*())*Q",
            },
        ],
        "Cartan": {
            "operator": "+i_(N*tau*u)(l_())",
            "scalar_slot": action,
        },
    }

EXPECTED_ADAPTER = {
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


def _local_canonical_sha256(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _local_row_dict(rows):
    result = {}
    variables = ("xi", "B4_bar", "k_infinity", "Rcal")
    for row in rows:
        powers = dict(row["powers"])
        monomial = tuple(powers.get(variable, 0) for variable in variables)
        numerator, denominator = row["coefficient"]
        result[monomial] = result.get(monomial, Fraction(0)) + Fraction(
            numerator, denominator
        )
    return {monomial: value for monomial, value in result.items() if value}


def _local_derivative(rows):
    derivative = {}
    for monomial, coefficient in _local_row_dict(rows).items():
        power = monomial[3]
        if not power:
            continue
        next_monomial = (*monomial[:3], power - 1)
        derivative[next_monomial] = (
            derivative.get(next_monomial, Fraction(0)) + coefficient * power
        )
    return {monomial: value for monomial, value in derivative.items() if value}


def _local_evaluate(rows, values):
    variables = ("xi", "B4_bar", "k_infinity", "Rcal")
    total = Fraction(0)
    for monomial, coefficient in _local_row_dict(rows).items():
        term = coefficient
        for variable, power in zip(variables, monomial, strict=True):
            term *= values[variable] ** power
        total += term
    return total


@pytest.fixture(scope="module")
def report():
    return gate.build_report()


def test_producer_is_test_local_byte_pinned():
    assert hashlib.sha256(MODULE_PATH.read_bytes()).hexdigest() == EXPECTED_PRODUCER_SHA256
    assert gate.EXPECTED_BLOCKS_SHA256 == EXPECTED_BLOCKS_SHA256
    assert gate.EXPECTED_COMPOSED_ADAPTER_SHA256 == EXPECTED_ADAPTER_SHA256


def test_audited_v5678_dependency_and_literal_are_exact(report):
    dependency = report["dependency_certificate"]
    assert dependency["pass"] is True
    assert dependency["audited_commit"] == EXPECTED_V5678_COMMIT
    assert dependency["audited_tree"] == {
        "commit": EXPECTED_V5678_COMMIT,
        "file_blobs": EXPECTED_V5678_BLOBS,
    }
    assert dependency["commit_binding"].startswith("provenance plus exact")
    assert dependency["v5_2_exact_action_sha256"] == EXPECTED_V52_ACTION_SHA256
    assert dependency["v5_2_foliation_literal"] == EXPECTED_V52_LITERAL
    assert dependency["input_stage"] == "post_adjoint_ADM_Euler_Green_normal_form"
    assert dependency["raw_Frechet_rows_present"] is False
    assert {
        name: row["sha256"] for name, row in dependency["files"].items()
    } == EXPECTED_V5678_SHA256
    assert {
        name: row["git_blob_sha1"] for name, row in dependency["files"].items()
    } == EXPECTED_V5678_BLOBS


def test_literal_parser_and_component_polynomials_are_exact(report):
    certificate = report["literal_component_split"]
    assert certificate["pass"] is True
    assert certificate["literal_components"] == {
        "R": "xi*Rcal",
        "R_squared": "-B4_bar*Rcal^2/(16*k_infinity^2)",
    }
    assert certificate["generated_components"] == certificate["literal_components"]
    assert certificate["literal_order"] == ["R", "R_squared"]
    independent = certificate["independent_literal_semantic_derivation"]
    assert tuple(independent) == EXPECTED_COMPONENTS
    assert independent["R"]["owner"] == "R"
    assert independent["R"]["sign"] == 1
    assert independent["R"]["coefficient"] == [1, 1]
    assert independent["R"]["numerator_symbol"] == "xi"
    assert independent["R"]["denominator_symbol"] is None
    assert independent["R"]["Rcal_power"] == 1
    assert independent["R"]["action_polynomial"] == R_ACTION_ROW
    assert independent["R"]["derivative_polynomial"] == R_DERIVATIVE_ROW
    assert independent["R_squared"]["owner"] == "R_squared"
    assert independent["R_squared"]["sign"] == -1
    assert independent["R_squared"]["coefficient"] == [-1, 16]
    assert independent["R_squared"]["numerator_symbol"] == "B4_bar"
    assert independent["R_squared"]["denominator_symbol"] == "k_infinity"
    assert independent["R_squared"]["denominator_power"] == 2
    assert independent["R_squared"]["Rcal_power"] == 2
    assert independent["R_squared"]["action_polynomial"] == R2_ACTION_ROW
    assert independent["R_squared"]["derivative_polynomial"] == R2_DERIVATIVE_ROW
    blocks = report["componentwise_post_adjoint_Euler_Green_blocks"]
    assert blocks["R"]["action_polynomial"] == R_ACTION_ROW
    assert blocks["R"]["d_action_d_Rcal"] == R_DERIVATIVE_ROW
    assert blocks["R_squared"]["action_polynomial"] == R2_ACTION_ROW
    assert blocks["R_squared"]["d_action_d_Rcal"] == R2_DERIVATIVE_ROW


def test_independent_literal_derivator_has_no_shared_semantic_oracle():
    source = inspect.getsource(
        gate._derive_intrinsic_components_from_pinned_literal_bytes
    )
    for forbidden in (
        "_expected_component_polynomials",
        "_build_component_blocks",
        "_strict_decode_public_blocks",
        "_independent_expected_public_blocks",
        "_parse_literal_split",
        "_literal_component_spans",
        "_poly_from_row",
        "_poly_row",
        "_render_polynomial",
    ):
        assert forbidden not in source
    with pytest.raises(
        gate.IntrinsicRR2SplitError,
        match="independent intrinsic parser byte pin",
    ):
        gate._derive_intrinsic_components_from_pinned_literal_bytes(
            EXPECTED_V52_LITERAL.replace("16*k_infinity", "8*k_infinity")
        )


def test_public_rows_have_strict_component_provenance_and_exact_schema(report):
    blocks = report["componentwise_post_adjoint_Euler_Green_blocks"]
    assert tuple(blocks) == EXPECTED_COMPONENTS
    certificate = report["strict_public_component_row_schema"]
    assert certificate["schema"] == EXPECTED_BLOCK_SCHEMA
    assert certificate["component_order"] == list(EXPECTED_COMPONENTS)
    assert certificate["pass"] is True
    assert all(certificate["checks"].values())
    assert certificate["expected_rows_sha256"] == EXPECTED_BLOCKS_SHA256
    assert certificate["observed_rows_sha256"] == EXPECTED_BLOCKS_SHA256
    expected_builder_source = inspect.getsource(
        gate._independent_expected_public_blocks
    )
    assert "_post_adjoint_block(" not in expected_builder_source
    assert "_build_component_blocks(" not in expected_builder_source
    assert "_post_adjoint_operator_template(" not in expected_builder_source
    assert "_expected_component_polynomials(" not in expected_builder_source
    spans = {
        "R": {
            "source_id": "v5.2.S_fol_lower.intrinsic_Rcal",
            "start": 81,
            "end": 88,
            "text": "xi*Rcal",
        },
        "R_squared": {
            "source_id": "v5.2.S_fol_lower.intrinsic_Rcal",
            "start": 102,
            "end": 134,
            "text": "-B4_bar*Rcal^2/(16*k_infinity^2)",
        },
    }
    for ordinal, name in enumerate(EXPECTED_COMPONENTS):
        row = blocks[name]
        assert row["schema"] == EXPECTED_BLOCK_SCHEMA
        assert row["component"] == name
        assert row["component_ordinal"] == ordinal
        assert row["side"] == "lower"
        assert row["domain"] == "Sigma"
        assert row["source_span"] == spans[name]
        assert EXPECTED_V52_LITERAL[
            spans[name]["start"] : spans[name]["end"]
        ] == spans[name]["text"]
    binding = report["component_local_slot_source_binding"]
    assert binding["pass"] is True
    assert binding["error"] is None
    assert all(all(row.values()) for row in binding["rows"].values())


def test_test_local_formal_ring_derivative_and_nonzero_evaluation(report):
    blocks = report["componentwise_post_adjoint_Euler_Green_blocks"]
    values = {
        "xi": Fraction(-8, 7),
        "B4_bar": Fraction(5, 9),
        "k_infinity": Fraction(11, 6),
        "Rcal": Fraction(13, 10),
    }
    for name in ("R", "R_squared"):
        action = blocks[name]["action_polynomial"]
        derivative = blocks[name]["d_action_d_Rcal"]
        assert _local_derivative(action) == _local_row_dict(derivative)
        assert _local_evaluate(action, values) != 0
        assert _local_evaluate(derivative, values) != 0
    combined = _local_evaluate(R_DERIVATIVE_ROW, values) + _local_evaluate(
        R2_DERIVATIVE_ROW, values
    )
    expected = values["xi"] - (
        values["B4_bar"] * values["Rcal"] / (8 * values["k_infinity"] ** 2)
    )
    assert combined == expected != 0


def test_independent_central_difference_has_exact_nonzero_goldens(report):
    oracle = report["formal_polynomial_certificate"][
        "independent_central_difference_oracle"
    ]
    assert oracle["pass"] is True
    assert oracle["Rcal_step"] == [2, 9]
    assert oracle["rows"]["R"]["central_difference"] == [7, 5]
    assert oracle["rows"]["R"]["formal_derivative"] == [7, 5]
    assert oracle["rows"]["R_squared"]["central_difference"] == [495, 9464]
    assert oracle["rows"]["R_squared"]["formal_derivative"] == [495, 9464]


def test_post_adjoint_operator_ir_is_explicit_and_composer_consumes_it(report):
    blocks = report["componentwise_post_adjoint_Euler_Green_blocks"]
    for name, action, derivative in (
        ("R", R_ACTION_ROW, R_DERIVATIVE_ROW),
        ("R_squared", R2_ACTION_ROW, R2_DERIVATIVE_ROW),
    ):
        block = blocks[name]
        expected_template = _expected_operator_template(name)
        assert block["stage"] == "post_adjoint_component_normal_form"
        assert block["scalar_slots"] == {
            "component_action": {
                "ref": _slot_ref("component_action", name),
                "polynomial": action,
            },
            "component_derivative": {
                "ref": _slot_ref("component_derivative", name),
                "with_respect_to": "Rcal",
                "polynomial": derivative,
            },
        }
        assert block["Euler_coefficients_inside_N_sqrt_h"] == (
            expected_template["Euler_coefficients_inside_N_sqrt_h"]
        )
        assert block["weighted_IBP_current"]["coefficient"] == {
            "schema": EXPECTED_CURRENT_COEFFICIENT_SCHEMA,
            "operator": "N_times",
            "scalar_slot": _slot_ref("component_derivative", name),
        }
        assert block["weighted_IBP_current"]["terms"] == (
            expected_template["weighted_IBP_current_terms"]
        )
        assert block["d4_Cartan_current"]["operator"] == (
            expected_template["Cartan"]
        )
        assert block["raw_Frechet_rows_exported"] is False

    dependency = report["dependency_certificate"]
    public = gate._public_blocks(gate._build_component_blocks(None))
    corrupted_slot = copy.deepcopy(public)
    corrupted_slot["R"]["scalar_slots"]["component_action"]["ref"]["kind"] = (
        "total_action"
    )
    with pytest.raises(gate.IntrinsicRR2SplitError, match="R-local component_action"):
        gate._compose_v5678_adapter(corrupted_slot, dependency)

    corrupted_operator = copy.deepcopy(public)
    corrupted_operator["R_squared"][
        "Euler_coefficients_inside_N_sqrt_h"
    ]["spatial_metric_Q_ij"][2]["operator"] += "+X"
    with pytest.raises(gate.IntrinsicRR2SplitError, match="Euler operators"):
        gate._compose_v5678_adapter(corrupted_operator, dependency)

    composer_source = inspect.getsource(gate._compose_v5678_adapter)
    assert "v5_6_7_8_ADM_normal_form" not in composer_source
    assert "_compose_v5678_adapter_with_trace" in composer_source
    traced_source = inspect.getsource(gate._compose_v5678_adapter_with_trace)
    assert "_strict_decode_public_blocks" in traced_source
    assert "_build_pre_normalized_provenance_trace" in traced_source
    assert "_fold_pre_normalized_provenance_trace" in traced_source
    decoder_source = inspect.getsource(gate._strict_decode_public_blocks)
    assert "_public_block_schema_certificate" not in decoder_source
    assert "_independent_expected_public_blocks" not in decoder_source
    poisoned_dependency = copy.deepcopy(dependency)
    poisoned_dependency["v5_6_7_8_ADM_normal_form"] = {"forbidden": "hardcode"}
    assert gate._compose_v5678_adapter(public, poisoned_dependency) == EXPECTED_ADAPTER


def test_componentwise_exact_product_rule_goldens(report):
    oracle = report["component_product_rule_oracle"]
    assert oracle["pass"] is True
    assert oracle["dimension"] == 2
    assert oracle["exact_rational_arithmetic"] is True
    assert oracle["rows"] == {
        "R": {
            "pass": True,
            "current_encoded": True,
            "raw": [-91, 285],
            "Euler_bulk": [-3649, 4158],
            "current_divergence": [220529, 395010],
            "residual": [0, 1],
        },
        "R_squared": {
            "pass": True,
            "current_encoded": True,
            "raw": [-119, 7600],
            "Euler_bulk": [-5287697, 756756000],
            "current_divergence": [-124668667, 14378364000],
            "residual": [0, 1],
        },
    }
    for row in oracle["rows"].values():
        raw = Fraction(*row["raw"])
        bulk = Fraction(*row["Euler_bulk"])
        divergence = Fraction(*row["current_divergence"])
        assert raw == bulk + divergence
        assert raw and bulk and divergence


def test_gauss_oracle_fixes_the_sign_on_each_tagged_block(report):
    oracle = report["Gauss_sign_oracle"]
    assert oracle["pass"] is True
    assert oracle["principal_curvature_witness"] == [[2, 3], [-3, 5], [5, 4]]
    for name in ("R", "R_squared"):
        assert oracle["rows"][name] == {
            "pass": True,
            "observed": [283, 210],
            "expected": [283, 210],
        }
        block = report["componentwise_post_adjoint_Euler_Green_blocks"][name]
        assert block["Gauss"] == {
            "projected_ambient_Riemann": 1,
            "K_trace_squared": -1,
            "K_tensor_squared": 1,
        }


def test_no_cross_cancellation_and_exact_v5678_recomposition(report):
    certificate = report["no_cross_component_cancellation_certificate"]
    assert certificate["pass"] is True
    assert certificate["criterion"] == "disjoint tagged monomial supports before normalization"
    assert certificate["action_overlap"] == 0
    assert certificate["derivative_overlap"] == 0
    assert certificate["normalization_dropped_tagged_action_terms"] == 0
    assert certificate["normalization_dropped_tagged_derivative_terms"] == 0
    assert report["component_blocks_sha256"] == EXPECTED_BLOCKS_SHA256
    assert report["composed_v5_6_7_8_adapter"] == EXPECTED_ADAPTER
    assert _local_canonical_sha256(EXPECTED_ADAPTER) == EXPECTED_ADAPTER_SHA256
    assert report["composed_v5_6_7_8_adapter_sha256"] == EXPECTED_ADAPTER_SHA256
    assert (
        report["composed_v5_6_7_8_adapter"]
        == report["dependency_certificate"]["v5_6_7_8_ADM_normal_form"]
    )


def test_metadata_inventory_is_honest_and_typed_units_are_causally_traced(report):
    inventory = report["public_field_inventory_certificate"]
    assert inventory["pass"] is True
    assert inventory["classification"] == "validated_not_folded"
    assert inventory["validation_source"] == (
        "strict independent expected-row snapshot certificate"
    )
    assert inventory["total_public_leaf_inventory"] == 252
    assert inventory["validated_not_folded_leaf_count"] == 54
    assert inventory["claim_every_scalar_leaf_is_causally_consumed"] is False

    certificate = report["semantic_payload_causal_consumption_certificate"]
    assert certificate["pass"] is True
    assert certificate["block_hash_pin_consulted"] is False
    assert certificate["survives_internal_block_hash_repin"] is True
    assert certificate["decoder_rejection_counts_as_consumption"] is False
    assert certificate["typed_reachability_unit_count"] == 86
    assert certificate["causal_alternative_count"] == 86
    assert certificate["reachability_units_all_exercised"] is True
    assert len(certificate["rows"]) == 86
    assert all(
        row["mutation_scoped_to_declared_source"]
        and row["decoder_accepted_structurally_valid_alternative"]
        and row["pre_normalized_trace_changed"]
        and row["declared_pre_normalized_target_changed"]
        and row["fold_rejected_or_adapter_changed"]
        for row in certificate["rows"]
    )
    trace = report["pre_normalized_component_provenance_trace"]
    assert trace["schema"].endswith("pre-normalized-provenance-trace-v1")
    assert trace["component_order"] == ["R", "R_squared"]
    assert len(trace["reachability"]) == 86
    expected_paths = _expected_causal_source_paths()
    assert len(expected_paths) == 86
    assert {row["source_path"] for row in trace["reachability"]} == expected_paths
    assert {row["source_path"] for row in certificate["rows"]} == expected_paths
    assert trace["explicit_component_sums"]["f"]["operation"] == (
        "ordered_sum_R_then_R_squared"
    )
    assert trace["explicit_component_sums"]["f_R"]["operation"] == (
        "ordered_sum_R_then_R_squared"
    )


@pytest.mark.parametrize(
    ("mutation", "required_failure"),
    [
        ("shared_oracle_swap", "component_local_slots_bind_literal_derivative_exact"),
        ("wrong_R2_derivative_factor", "formal_Laurent_polynomial_derivatives_exact"),
        ("wrong_Gauss_sign", "component_Gauss_sign_exact"),
        ("mix_xi_B4_across_blocks", "no_cross_component_monomial_cancellation"),
        ("omit_R2_weighted_current", "every_component_current_present"),
        ("double_Cartan", "component_Cartan_currents_compose_once"),
        ("alias_k_to_itself", "sum_reconstructs_v5_6_7_8_ADM_normal_form"),
    ],
)
def test_each_mandatory_mutant_hits_its_semantic_surface(
    report, mutation, required_failure
):
    row = report["mandatory_mutant_certificate"]["rows"][mutation]
    assert row["killed"] is True
    assert row["required_failure_observed"] is True
    assert row["required_failure_surface"] == required_failure
    assert required_failure in row["failed_checks"]
    mutated = gate.build_report(mutation)
    assert mutated["status"] == "NOT_READY"
    assert mutated["checks"]["all"] is False
    assert mutated["checks"][required_failure] is False


def test_all_mutants_are_killed_after_internal_block_hash_repin(report):
    campaign = report["mandatory_mutant_certificate"]
    assert set(campaign["required_inventory"]) == set(gate.MUTATIONS)
    assert set(campaign["rows"]) == set(gate.MUTATIONS)
    assert campaign["pass"] is True
    for name, row in campaign["rows"].items():
        assert row["internal_hashes_repinned"] is True, name
        assert row["block_pin_pass_after_repin"] is True, name
        assert row["killed"] is True, name
        assert row["required_failure_observed"] is True, name
        assert row["failed_checks"], name


@pytest.mark.parametrize("mutation", sorted(EXPECTED_NEW_REPIN_MUTANTS))
def test_new_public_row_and_combined_mutants_fail_after_repin(report, mutation):
    row = report["mandatory_mutant_certificate"]["rows"][mutation]
    assert row["internal_hashes_repinned"] is True
    assert row["block_pin_pass_after_repin"] is True
    assert row["killed"] is True
    assert "strict_public_component_row_schema_and_expected_rows_exact" in row[
        "failed_checks"
    ]
    assert "composer_decodes_and_folds_exported_rows" in row["failed_checks"]
    assert "typed_component_slots_and_operator_terms_causally_traced" in row[
        "failed_checks"
    ]


def test_exact_combined_exporter_exploit_stays_dead_after_repin(report, monkeypatch):
    original_builder = gate._build_component_blocks

    def compromised_builder(mutation):
        if mutation is None:
            return original_builder(
                "combined_swap_relabel_and_unconsumed_fields_after_repin"
            )
        return original_builder(mutation)

    monkeypatch.setattr(gate, "_build_component_blocks", compromised_builder)
    core = gate._build_core(
        report["dependency_certificate"],
        None,
        repin_internal_hashes=True,
    )
    assert core["internal_hashes_repinned"] is True
    assert core["checks"]["component_blocks_canonical_pin"] is True
    assert core["checks"][
        "strict_public_component_row_schema_and_expected_rows_exact"
    ] is False
    assert core["checks"]["composer_decodes_and_folds_exported_rows"] is False
    assert core["checks"]["sum_reconstructs_v5_6_7_8_ADM_normal_form"] is False
    assert core["ready"] is False


def test_expected_rows_do_not_share_the_exporter_template_after_repin(
    report, monkeypatch
):
    original_template = gate._post_adjoint_operator_template

    def corrupted_exporter_template(component):
        template = original_template(component)
        template["weighted_IBP_current_terms"][0]["operator"] = (
            "N*()*FORGED_Q"
        )
        return template

    monkeypatch.setattr(
        gate, "_post_adjoint_operator_template", corrupted_exporter_template
    )
    core = gate._build_core(
        report["dependency_certificate"],
        None,
        repin_internal_hashes=True,
    )
    assert core["checks"]["component_blocks_canonical_pin"] is True
    assert core["checks"][
        "strict_public_component_row_schema_and_expected_rows_exact"
    ] is False
    assert core["checks"]["composer_decodes_and_folds_exported_rows"] is False
    assert core["ready"] is False


def test_whitelist_decoder_cannot_turn_rejection_into_consumption(report, monkeypatch):
    dependency = report["dependency_certificate"]
    baseline_public = gate._public_blocks(gate._build_component_blocks(None))
    baseline_decoded, baseline_paths = gate._strict_decode_public_blocks(
        baseline_public, dependency
    )

    def whitelist_decoder(candidate, _dependency):
        if not gate._strict_equal(candidate, baseline_public):
            raise gate.IntrinsicRR2SplitError("whitelist rejects every alternative")
        return copy.deepcopy(baseline_decoded), list(baseline_paths)

    monkeypatch.setattr(gate, "_strict_decode_public_blocks", whitelist_decoder)
    core = gate._build_core(dependency, None, repin_internal_hashes=True)
    assert core["checks"]["composer_decodes_and_folds_exported_rows"] is True
    assert core["checks"]["sum_reconstructs_v5_6_7_8_ADM_normal_form"] is True
    assert core["checks"][
        "typed_component_slots_and_operator_terms_causally_traced"
    ] is False
    certificate = core["field_consumption"]
    assert certificate["decoder_rejection_counts_as_consumption"] is False
    assert not all(
        row["decoder_accepted_structurally_valid_alternative"]
        for row in certificate["rows"]
    )
    assert core["ready"] is False


def test_hardcoded_fold_cannot_pass_causal_trace(report, monkeypatch):
    dependency = report["dependency_certificate"]
    baseline_adapter = copy.deepcopy(report["composed_v5_6_7_8_adapter"])

    def hardcoded_fold(_trace):
        return copy.deepcopy(baseline_adapter)

    monkeypatch.setattr(gate, "_fold_pre_normalized_provenance_trace", hardcoded_fold)
    core = gate._build_core(dependency, None, repin_internal_hashes=True)
    assert core["checks"]["composer_decodes_and_folds_exported_rows"] is True
    assert core["checks"]["sum_reconstructs_v5_6_7_8_ADM_normal_form"] is True
    assert core["checks"][
        "typed_component_slots_and_operator_terms_causally_traced"
    ] is False
    assert all(
        row["decoder_accepted_structurally_valid_alternative"]
        and row["pre_normalized_trace_changed"]
        and not row["fold_rejected_or_adapter_changed"]
        for row in core["field_consumption"]["rows"]
    )
    assert core["ready"] is False


@pytest.mark.parametrize(
    ("section", "field", "case_suffix"),
    (
        ("weighted_current", "prefactor", "current_prefactor"),
        (
            "Cartan",
            "separate_material_transgression_appended",
            "Cartan_transgression",
        ),
    ),
)
def test_fold_that_silently_ignores_a_valid_semantic_field_is_detected(
    report, monkeypatch, section, field, case_suffix
):
    original_fold = gate._fold_pre_normalized_provenance_trace
    baseline_trace = report["pre_normalized_component_provenance_trace"]

    def compromised_fold(trace):
        sanitized = copy.deepcopy(trace)
        for component in EXPECTED_COMPONENTS:
            sanitized["components"][component][section][field] = copy.deepcopy(
                baseline_trace["components"][component][section][field]
            )
        return original_fold(sanitized)

    monkeypatch.setattr(
        gate, "_fold_pre_normalized_provenance_trace", compromised_fold
    )
    core = gate._build_core(
        report["dependency_certificate"], None, repin_internal_hashes=True
    )
    target_rows = [
        row
        for row in core["field_consumption"]["rows"]
        if row["case"].endswith(case_suffix)
    ]
    assert len(target_rows) == 2
    assert all(
        row["decoder_accepted_structurally_valid_alternative"]
        and row["pre_normalized_trace_changed"]
        and not row["fold_rejected_or_adapter_changed"]
        for row in target_rows
    )
    assert core["checks"][
        "typed_component_slots_and_operator_terms_causally_traced"
    ] is False
    assert core["ready"] is False


def _replace_component_derivative_with_forbidden_total_slot(public, mode):
    mutated = copy.deepcopy(public)
    for component in EXPECTED_COMPONENTS:
        if mode in {"coefficient", "combined"}:
            mutated[component]["weighted_IBP_current"]["coefficient"][
                "scalar_slot"
            ]["kind"] = "total_derivative"
        if mode in {"terms", "combined"}:
            for term in mutated[component]["weighted_IBP_current"]["terms"]:
                term["scalar_slot"]["kind"] = "total_derivative"
    return mutated


def _swap_component_slot_polynomials_preserving_sum(public):
    mutated = copy.deepcopy(public)
    for slot in ("component_action", "component_derivative"):
        mutated["R"]["scalar_slots"][slot]["polynomial"], mutated[
            "R_squared"
        ]["scalar_slots"][slot]["polynomial"] = (
            copy.deepcopy(
                mutated["R_squared"]["scalar_slots"][slot]["polynomial"]
            ),
            copy.deepcopy(mutated["R"]["scalar_slots"][slot]["polynomial"]),
        )
    return mutated


def test_aggregate_preserving_slot_swap_fails_source_binding_after_co_mutation(
    report, monkeypatch
):
    original_builder = gate._build_component_blocks
    original_expected = gate._independent_expected_public_blocks

    def compromised_builder(mutation):
        blocks = original_builder(mutation)
        if mutation is None:
            forged = _swap_component_slot_polynomials_preserving_sum(
                gate._public_blocks(blocks)
            )
            for component in EXPECTED_COMPONENTS:
                blocks[component]["row"] = forged[component]
        return blocks

    def compromised_expected(dependency):
        return _swap_component_slot_polynomials_preserving_sum(
            original_expected(dependency)
        )

    monkeypatch.setattr(gate, "_build_component_blocks", compromised_builder)
    monkeypatch.setattr(
        gate, "_independent_expected_public_blocks", compromised_expected
    )
    core = gate._build_core(
        report["dependency_certificate"], None, repin_internal_hashes=True
    )
    assert core["checks"]["component_blocks_canonical_pin"] is True
    assert core["checks"][
        "strict_public_component_row_schema_and_expected_rows_exact"
    ] is True
    assert core["checks"]["composer_decodes_and_folds_exported_rows"] is True
    assert core["checks"]["sum_reconstructs_v5_6_7_8_ADM_normal_form"] is True
    assert core["checks"]["component_local_slots_bind_literal_derivative_exact"] is False
    assert core["ready"] is False


def test_shared_polynomial_oracle_and_golden_co_mutation_fails_independent_binding(
    report, monkeypatch
):
    original_builder = gate._build_component_blocks
    original_polynomials = gate._expected_component_polynomials
    original_expected = gate._independent_expected_public_blocks
    canonical_r, canonical_r2 = original_polynomials()

    def compromised_polynomials():
        return canonical_r2, canonical_r

    def compromised_builder(mutation):
        blocks = original_builder(mutation)
        if mutation is None:
            blocks["R"]["row"]["literal_expression"] = "xi*Rcal"
            blocks["R_squared"]["row"]["literal_expression"] = (
                "-B4_bar*Rcal^2/(16*k_infinity^2)"
            )
        return blocks

    def compromised_expected(dependency):
        expected = original_expected(dependency)
        swapped_rows = {
            "R": (
                R2_ACTION_ROW,
                R2_DERIVATIVE_ROW,
                "-B4_bar*Rcal/(8*k_infinity^2)",
            ),
            "R_squared": (R_ACTION_ROW, R_DERIVATIVE_ROW, "xi"),
        }
        for component, (action, derivative, derivative_text) in swapped_rows.items():
            row = expected[component]
            row["action_polynomial"] = copy.deepcopy(action)
            row["d_action_d_Rcal"] = copy.deepcopy(derivative)
            row["literal_derivative_expression"] = derivative_text
            row["scalar_slots"]["component_action"]["polynomial"] = copy.deepcopy(
                action
            )
            row["scalar_slots"]["component_derivative"][
                "polynomial"
            ] = copy.deepcopy(derivative)
        return expected

    monkeypatch.setattr(
        gate, "_expected_component_polynomials", compromised_polynomials
    )
    monkeypatch.setattr(gate, "_build_component_blocks", compromised_builder)
    monkeypatch.setattr(
        gate, "_independent_expected_public_blocks", compromised_expected
    )
    core = gate._build_core(
        report["dependency_certificate"], None, repin_internal_hashes=True
    )
    assert core["checks"]["component_blocks_canonical_pin"] is True
    assert core["checks"][
        "strict_public_component_row_schema_and_expected_rows_exact"
    ] is True
    assert core["checks"]["composer_decodes_and_folds_exported_rows"] is True
    assert core["checks"]["sum_reconstructs_v5_6_7_8_ADM_normal_form"] is True
    assert core["checks"][
        "typed_component_slots_and_operator_terms_causally_traced"
    ] is True
    assert core["field_consumption"]["causal_alternative_count"] == 86
    assert core["checks"]["literal_R_R_squared_split_exact"] is False
    assert core["checks"]["formal_Laurent_polynomial_derivatives_exact"] is False
    assert core["checks"][
        "component_local_slots_bind_literal_derivative_exact"
    ] is False
    binding = core["slot_source_binding"]
    assert binding["rows"]["R"][
        "source_span_matches_independent_literal_bytes"
    ] is True
    assert binding["rows"]["R"][
        "literal_expression_matches_independent_literal_bytes"
    ] is True
    assert binding["rows"]["R"][
        "action_metadata_matches_independent_literal_polynomial"
    ] is False
    assert binding["rows"]["R_squared"][
        "component_action_matches_literal_component"
    ] is False
    assert core["ready"] is False


@pytest.mark.parametrize("mode", ("coefficient", "terms", "combined"))
def test_total_current_slots_fail_closed_even_if_producer_expected_and_hash_repin(
    report, monkeypatch, mode
):
    original_builder = gate._build_component_blocks
    original_expected = gate._independent_expected_public_blocks

    def compromised_builder(mutation):
        blocks = original_builder(mutation)
        if mutation is None:
            forged_rows = _replace_component_derivative_with_forbidden_total_slot(
                gate._public_blocks(blocks), mode
            )
            for component in EXPECTED_COMPONENTS:
                blocks[component]["row"] = forged_rows[component]
        return blocks

    def compromised_expected(dependency):
        return _replace_component_derivative_with_forbidden_total_slot(
            original_expected(dependency), mode
        )

    monkeypatch.setattr(gate, "_build_component_blocks", compromised_builder)
    monkeypatch.setattr(
        gate, "_independent_expected_public_blocks", compromised_expected
    )
    core = gate._build_core(
        report["dependency_certificate"], None, repin_internal_hashes=True
    )
    assert core["checks"]["component_blocks_canonical_pin"] is True
    assert core["checks"][
        "strict_public_component_row_schema_and_expected_rows_exact"
    ] is True
    assert core["checks"]["composer_decodes_and_folds_exported_rows"] is False
    assert core["checks"][
        "typed_component_slots_and_operator_terms_causally_traced"
    ] is False
    assert "local component_derivative slot" in core["composition_error"]
    assert core["ready"] is False


def test_post_adjoint_boundary_and_fail_closed_decisions(report):
    assert report["status"] == "READY"
    assert report["checks"]["all"] is True
    assert report["raw_Frechet_export"]["rows"] == []
    assert report["raw_Frechet_export"]["FrechetRowV1_adapter_exported"] is False
    assert set(key for key, value in report["decision"].items() if value) == EXPECTED_TRUE
    assert set(key for key, value in report["decision"].items() if not value) == EXPECTED_FALSE
    for key in (
        "raw_action_AST_Frechet_rows_recovered_pass",
        "raw_Frechet_to_post_adjoint_bridge_pass",
        "moving_embedding_shape_equation_pass",
        "full_off_shell_Green_theorem_selected_sector_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
    ):
        assert report["decision"][key] is False
    boundary = report["evidence_boundary"]
    assert "post-adjoint" in boundary["proved"]
    assert "raw Frechet rows" in boundary["not_proved"]
    assert boundary["Route_C_used"] is False
    assert boundary["quotient_or_margin_argument_used"] is False
    assert boundary["artifact_written"] is False


def test_dependency_hash_drift_and_unknown_mutation_fail_closed(monkeypatch):
    original = gate._sha256

    def drift(path):
        if path == gate.V5678_SOURCE:
            return "0" * 64
        return original(path)

    monkeypatch.setattr(gate, "_sha256", drift)
    with pytest.raises(gate.IntrinsicRR2SplitError, match="SHA256 drift"):
        gate.build_report()
    monkeypatch.setattr(gate, "_sha256", original)
    with pytest.raises(gate.IntrinsicRR2SplitError, match="unknown mutation"):
        gate.build_report("not_a_declared_mutation")


def test_cli_emits_same_ready_report_without_writing_an_artifact(report):
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)],
        check=True,
        capture_output=True,
        text=True,
    )
    observed = json.loads(completed.stdout)
    assert observed["schema"] == report["schema"]
    assert observed["status"] == "READY"
    assert observed["component_blocks_sha256"] == EXPECTED_BLOCKS_SHA256
    assert observed["composed_v5_6_7_8_adapter_sha256"] == EXPECTED_ADAPTER_SHA256
    assert observed["checks"]["all"] is True
