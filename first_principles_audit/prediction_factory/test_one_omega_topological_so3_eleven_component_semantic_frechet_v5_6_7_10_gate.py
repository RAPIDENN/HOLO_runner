#!/usr/bin/env python3
"""Independent exact tests for the narrow v5.6.7.10 semantic subgate."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_eleven_component_semantic_frechet_v5_6_7_10_gate
    as gate,
)


ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
COMPLETION_SHA256 = "392840aeaed507e742d673bcae32c8b9490825b27e293ec62f583d8c295139fe"
COMPONENT_ASTS_SHA256 = "3fe6fe35f6374448f107ce79cdb9d468e9eec95123c60122d6b1cfac372302e1"
FRECHET_ASTS_SHA256 = "e5514fa91b83706b3920dcb6ff09b2bfc203d7d42e2fac19796391d7e4513647"
FRECHET_ROWS_SHA256 = "fea5f8e791de0ae1fcc98e4b89426b73a464debb33d8d261b0e7f05704402c78"
INCLUDED = (
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "wall",
)
EXCLUDED = (
    "EH_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "GHY_minus",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


@pytest.fixture(scope="session")
def report() -> dict:
    return gate.build_report()


def test_byte_pins_and_full_span_parser_are_independent_of_semantic_claim(
    report: dict,
) -> None:
    assert report["upstream"]["exact_action_sha256"] == ACTION_SHA256
    payload = json.loads(gate.V52_ARTIFACT.read_text(encoding="utf-8"))
    action = payload["exact_classical_charter"]["exact_action"]
    assert canonical_hash(action) == ACTION_SHA256
    assert tuple(report["parser"]["action_key_order"]) == gate.ACTION_KEYS
    assert set(report["parser"]["token_coverage"]) == set(gate.ACTION_KEYS)
    for row in report["parser"]["token_coverage"].values():
        assert row["round_trip_exact"] is True
        assert row["first_start"] == 0
        assert row["last_end"] == row["byte_length"]


def test_completion_and_all_three_aggregate_hashes_are_test_local_pins(
    report: dict,
) -> None:
    assert report["semantic_completion_sha256"] == COMPLETION_SHA256
    assert canonical_hash(report["semantic_completion"]) == COMPLETION_SHA256
    hashes = report["aggregate_hashes"]
    assert hashes["component_ASTs_sha256"] == COMPONENT_ASTS_SHA256
    assert hashes["forward_Frechet_ASTs_sha256"] == FRECHET_ASTS_SHA256
    assert hashes["reverse_Frechet_ASTs_sha256"] == FRECHET_ASTS_SHA256
    assert hashes["FrechetRowV1_sha256"] == FRECHET_ROWS_SHA256


def test_exactly_eleven_components_and_no_v9_or_excluded_dependency(
    report: dict,
) -> None:
    assert tuple(report["scope"]["included_components"]) == INCLUDED
    assert tuple(report["scope"]["excluded_components"]) == EXCLUDED
    assert tuple(report["typed_component_certificate"]) == INCLUDED
    source = Path(gate.__file__).read_text(encoding="utf-8")
    assert "variational_ir_formal_adjoint_v5_6_7_9" not in source
    assert not set(INCLUDED) & set(EXCLUDED)


def test_forward_nilpotent_and_reverse_context_routes_match_exactly(
    report: dict,
) -> None:
    certificate = report["typed_component_certificate"]
    assert all(row["routes_exactly_equal"] is True for row in certificate.values())
    assert all(row["variation_degrees"] == [1] for row in certificate.values())
    assert certificate["P_kinetic_bulk_plus"]["frechet_ops"]["variation"] == 54
    assert certificate["BF_bulk_plus"]["frechet_ops"]["variation"] == 5
    assert report["checks"]["two_independent_symbolic_AD_routes_exactly_agree"] is True


def test_FrechetRowV1_binders_are_scoped_typed_and_source_bound(
    report: dict,
) -> None:
    rows = report["FrechetRowV1"]
    action, _payload = gate.certify_v52_dependency()
    assert len(rows) == 155
    assert all(gate.validate_frechet_row(row) for row in rows)
    assert {tuple(row["derivative"]["word"]) for row in rows} == {(), (0,)}
    for row in rows:
        assert row["coefficient_ast_sha256"] == canonical_hash(row["coefficient_ast"])
        assert row["source_spans"]
        for span in row["source_spans"]:
            source = action[span["action_key"]][span["start"] : span["end"]]
            assert hashlib.sha256(source.encode("utf-8")).hexdigest() == span["sha256"]
        if row["derivative"]["word"] == [0]:
            binder = row["derivative"]["binders"][0]
            assert binder["id"] == 0
            assert binder["scope"] == "row"
            assert binder["alpha_normalized"] is True
            assert binder["variance"] == "down"
            assert binder["dimension"] == (4 if row["domain"] == "Sigma" else 5)
    for bad_ordinal in ("0", 0.0, True, -1):
        mutant = deepcopy(rows[0])
        mutant["summand_ordinal"] = bad_ordinal
        with pytest.raises(gate.SemanticFrechetError):
            gate.validate_frechet_row(mutant)


def _find_slot(ast: dict) -> dict:
    if ast.get("op") == "linear_slot":
        return ast
    for arg in ast.get("args", []):
        try:
            return _find_slot(arg)
        except LookupError:
            pass
    raise LookupError("linear slot not found")


def _rehash(row: dict) -> None:
    row["coefficient_ast_sha256"] = canonical_hash(row["coefficient_ast"])


def test_binder_alpha_renaming_is_invariant_and_bad_binders_fail(
    report: dict,
) -> None:
    baseline = next(row for row in report["FrechetRowV1"] if row["derivative"]["word"] == [0])
    renamed = deepcopy(baseline)
    renamed["derivative"]["word"] = [19]
    renamed["derivative"]["binders"][0]["id"] = 19
    renamed["derivative"]["binders"][0]["alpha_normalized"] = False
    _find_slot(renamed["coefficient_ast"])["external_derivative_word"] = [19]
    _rehash(renamed)
    assert gate.canonicalize_frechet_row_binders(renamed) == baseline

    mutants = []
    wrong_dimension = deepcopy(baseline)
    wrong_dimension["derivative"]["binders"][0]["dimension"] = 4
    mutants.append(wrong_dimension)
    wrong_namespace = deepcopy(baseline)
    wrong_namespace["derivative"]["binders"][0]["namespace"] = "captured.coordinate"
    mutants.append(wrong_namespace)
    wrong_variance = deepcopy(baseline)
    wrong_variance["derivative"]["binders"][0]["variance"] = "up"
    mutants.append(wrong_variance)
    free = deepcopy(baseline)
    free["derivative"]["word"] = [23]
    mutants.append(free)
    capture = deepcopy(baseline)
    capture["coefficient_ast"]["external_derivative_word"] = [0]
    mutants.append(capture)
    wrong_slot = deepcopy(baseline)
    _find_slot(wrong_slot["coefficient_ast"])["type"] = gate._compat_type(gate.SCALAR0)
    mutants.append(wrong_slot)
    unresolved = deepcopy(baseline)
    _find_slot(unresolved["coefficient_ast"])["op"] = "unresolved_slot"
    mutants.append(unresolved)
    for mutant in mutants:
        _rehash(mutant)
        with pytest.raises(gate.SemanticFrechetError):
            gate.validate_frechet_row(mutant)


def test_symbolic_binder_is_not_physical_direction_zero_and_sums_5x3(
    report: dict,
) -> None:
    probe = report["executable_semantics"]["binder_and_fiber_expansion_probe"]
    assert probe["word_zero_is_alpha_normalized_binder_not_physical_direction_zero"] is True
    assert probe["coordinate_dimension"] == 5
    assert probe["coordinate_sum"] == Fraction(15)
    assert probe["SO3_fiber_dimension"] == 3
    assert probe["SO3_sum"] == Fraction(6)
    assert report["checks"]["symbolic_binder_and_SO3_fiber_expand_over_five_and_three_values"] is True


def test_nonzero_executable_P_BF_wedge_and_metric_paths_match_independent_oracles(
    report: dict,
) -> None:
    executable = report["executable_semantics"]
    probe = executable["eleven_component_probe"]
    for side in ("plus", "minus"):
        bf = probe["components"][f"BF_bulk_{side}"]
        assert bf["primal_nonzero"] is True
        assert bf["Frechet_nonzero"] is True
    bridge = executable["independent_oracle_bridge"]
    assert bridge["P_AST_value"] == (
        Fraction(17, 4), Fraction(9, 2), Fraction(2)
    )
    assert bridge["P_Frechet_AST_value"] == (
        Fraction(31, 8), Fraction(-5, 2), Fraction(9, 4)
    )
    assert bridge["P_alpha_phi_nonzero"] is True
    assert bridge["P_forward_reverse_expanded_value_equal"] is True
    assert bridge["matrix_wedge_01"] == bridge["matrix_wedge_01_expected"]
    assert bridge["BF_AST_value"] == Fraction(-6)
    assert bridge["BF_AST_value"] == bridge["BF_mini_exterior_oracle_value"]
    assert bridge["inverse_AST_value"] == bridge["inverse_dual_oracle_value"]
    assert bridge["volume_AST_value"] == bridge["volume_dual_oracle_value"]
    assert bridge["D_W_AST_terms"] == bridge["D_W_reverse_AST_terms"] == (
        (1, Fraction(-1)),
    )
    assert bridge["D_U_AST_terms"] == bridge["D_U_reverse_AST_terms"] == (
        (2, Fraction(14, 3)),
    )
    assert bridge["D_wall_AST_terms"] == bridge["D_wall_reverse_AST_terms"] == (
        (1, Fraction(2)),
    )
    assert bridge["V4_Q_AST_value"] == bridge["V4_Q_oracle_value"] == Fraction(9, 40)
    assert bridge["V4_Q_Omega_Frechet_AST_value"] == Fraction(-9, 500)
    assert bridge["V4_Q_s_Frechet_AST_value"] == Fraction(123, 250)
    assert report["checks"]["typed_AST_evaluator_matches_independent_P_BF_metric_oracles"] is True


def test_exact_P_oracle_kills_double_DA_alpha_and_inverse_square_mutants(
    report: dict,
) -> None:
    oracle = report["exact_oracles"]["P_one_dimensional"]
    assert oracle["P"] == (Fraction(17, 4), Fraction(9, 2), Fraction(2))
    assert oracle["delta_P"] == (
        Fraction(31, 8),
        Fraction(-5, 2),
        Fraction(9, 4),
    )
    assert oracle["mutants_killed"] == {
        "double_Dpsi": True,
        "omit_Omega_inverse_squared_piece": True,
        "omit_alpha_phi": True,
    }


def test_full_V4_is_smooth_exact_at_nonzero_oracle_and_has_no_norm_derivative_atom(
    report: dict,
) -> None:
    oracle = report["exact_oracles"]["full_V4_reduced_Q"]
    assert oracle["Q"] == Fraction(9, 40)
    assert oracle["partial_Omega_Q"] == Fraction(-9, 500)
    assert oracle["partial_s_Q"] == Fraction(123, 250)
    assert all(oracle["mutants_killed"].values())
    zero = report["executable_semantics"]["smooth_V4_phi_zero_probe"]
    assert zero["primal"] == 0
    assert zero["Frechet"] == 0
    assert zero["negative_direct_powers_of_phi_pair"] == []
    assert zero["finite"] is True
    forbidden = {"W_Omega", "U_Omega", "Q_derivative", "D_A", "F"}
    assert not forbidden & set(report["executable_semantics"]["used_ops"])
    assert report["executable_semantics"]["unresolved_ops"] == []


def _permutation_sign(values: tuple[int, ...]) -> int:
    inversions = sum(
        1
        for left in range(len(values))
        for right in range(left + 1, len(values))
        if values[left] > values[right]
    )
    return -1 if inversions % 2 else 1


def test_BF_pairing_wedge_executes_all_form_components_and_graded_sign(
    report: dict,
) -> None:
    generator = np.asarray(
        [[Fraction(0), Fraction(-1), Fraction(0)],
         [Fraction(1), Fraction(0), Fraction(0)],
         [Fraction(0), Fraction(0), Fraction(0)]],
        dtype=object,
    )
    bfield = np.zeros((5, 5, 5, 3, 3), dtype=object)
    curvature = np.zeros((5, 5, 3, 3), dtype=object)
    for permutation in itertools.permutations((0, 1, 2)):
        bfield[permutation] = _permutation_sign(permutation) * 2 * generator
    curvature[3, 4] = 3 * generator
    curvature[4, 3] = -3 * generator
    expr = gate.pair_wedge(
        gate.field("B", gate.ADJOINT3_5),
        gate.field("F", gate.ENDOMORPHISM2_5),
    )
    value = gate.evaluate_expr(
        expr,
        gate.EvaluationEnvironment(
            values={"B": bfield, "F": curvature}, parameters={}, partials={}
        ),
    )
    assert value == Fraction(6)
    oracle = report["exact_oracles"]["BF_graded_Leibniz"]
    assert oracle["B_wedge_dalpha"] == Fraction(-6)
    assert oracle["dB_wedge_alpha"] == Fraction(1)
    assert oracle["d_B_wedge_alpha"] == Fraction(7)
    assert oracle["wrong_plus_sign_mutant"] != oracle["expected"]


def test_inverse_metric_and_density_semantics_are_exact_not_opaque() -> None:
    metric = gate.field("g", gate.METRIC5)
    inverse = gate.inverse_metric(metric)
    volume = gate.volume_density(metric)
    g = np.diag(
        [Fraction(-1), Fraction(1), Fraction(1), Fraction(1), Fraction(1)]
    ).astype(object)
    environment = gate.EvaluationEnvironment(values={"g": g}, parameters={}, partials={})
    assert np.array_equal(gate.evaluate_expr(inverse, environment), g)
    assert gate.evaluate_expr(volume, environment) == Fraction(1)


def test_independent_fraction_dual_metric_and_W_U_wall_oracles(report: dict) -> None:
    metric = report["exact_oracles"]["metric_inverse_and_volume"]
    assert metric["g_of_t"] == "[[-1+t,2*t],[2*t,1+3*t]]"
    assert metric["delta_g_inverse"] == (
        (Fraction(-1), Fraction(2)),
        (Fraction(2), Fraction(-3)),
    )
    assert metric["sqrt_minus_det_linear_coefficient"] == Fraction(1)
    assert metric["mutants_killed"] == {
        "missing_volume_half": True,
        "wrong_positive_inverse_sign": True,
    }

    wall = report["exact_oracles"]["W_U_wall_at_origin"]
    assert wall["assumptions"] == (
        "M5=G=k_infinity=1, Omega=Omega_Sigma=0, beta=2"
    )
    assert wall["W_zero"] == Fraction(3)
    assert wall["W_Omega_zero"] == Fraction(0)
    assert wall["U_zero"] == Fraction(-6)
    assert wall["wall_bracket_zero"] == Fraction(7)
    assert all(wall["mutants_killed"].values())


def test_Omega_one_exp_derivatives_kill_correlated_forward_reverse_comutation(
    report: dict,
) -> None:
    oracle = report["exact_oracles"]["nontrivial_exp_derivatives_at_Omega_one"]
    assert oracle["D_W_terms"] == ((1, Fraction(-1)),)
    assert oracle["D_U_terms"] == ((2, Fraction(14, 3)),)
    assert oracle["D_wall_action_terms"] == ((1, Fraction(2)),)
    assert all(oracle["mutants_killed"].values())

    mutant = gate.build_report(mutation="correlated_double_exp_derivative")
    assert mutant["checks"]["two_independent_symbolic_AD_routes_exactly_agree"] is True
    bridge = mutant["executable_semantics"]["independent_oracle_bridge"]
    assert bridge["D_W_AST_terms"] == bridge["D_W_reverse_AST_terms"] == (
        (1, Fraction(-2)),
    )
    assert bridge["D_W_AST_terms"] != bridge["D_W_oracle_terms"]
    assert mutant["checks"]["typed_AST_evaluator_matches_independent_P_BF_metric_oracles"] is False
    assert mutant["decision"]["exactly_eleven_component_Frechet_IR_pass"] is False
    assert mutant["checks"]["all"] is False


def _test_cross_matrix(vector: tuple[int, int, int]) -> np.ndarray:
    x, y, z = map(Fraction, vector)
    return np.asarray(
        [[Fraction(0), -z, y], [z, Fraction(0), -x], [-y, x, Fraction(0)]],
        dtype=object,
    )


def _test_antisymmetric_form(
    axes: tuple[int, ...], coefficient: Fraction, matrix: np.ndarray
) -> np.ndarray:
    result = np.zeros((5,) * len(axes) + (3, 3), dtype=object)
    for permutation in itertools.permutations(axes):
        relative = tuple(axes.index(item) for item in permutation)
        result[permutation] = _permutation_sign(relative) * coefficient * matrix
    return result


def test_full_BF_Frechet_rows_match_test_local_sign_and_normalization_oracle(
    report: dict,
) -> None:
    oracle = report["exact_oracles"]["full_BF_Frechet"]
    expected_rows = (
        Fraction(35),
        Fraction(55, 2),
        Fraction(55, 2),
        Fraction(6),
        Fraction(3),
    )
    assert oracle["values_by_FrechetRowV1_ordinal"] == expected_rows
    assert oracle["total"] == Fraction(99)
    assert oracle["normalization_third_mutant"] == Fraction(66)
    assert oracle["wrong_trace_sign_mutant"] == Fraction(-99)
    assert all(oracle["mutants_killed"].values())

    jx = _test_cross_matrix((1, 0, 0))
    jy = _test_cross_matrix((0, 1, 0))
    jz = _test_cross_matrix((0, 0, 1))
    connection = np.zeros((5, 3, 3), dtype=object)
    connection[3], connection[4] = jx, jy
    alpha = np.zeros((5, 3, 3), dtype=object)
    alpha[3] = Fraction(11) * jx
    d_connection = _test_antisymmetric_form((3, 4), Fraction(2), jz)
    d_alpha = _test_antisymmetric_form((3, 4), Fraction(7), jz)
    bfield = _test_antisymmetric_form((0, 1, 2), Fraction(5), jz)
    b_variation = _test_antisymmetric_form((0, 1, 2), Fraction(3), jz)

    action, _payload = gate.certify_v52_dependency()
    program = gate.build_component_program(gate.parse_exact_action(action))
    forward = {
        name: gate.forward_nilpotent_dual(expr, program.tangents).tangent
        for name, expr in program.components.items()
    }
    rows = gate.export_frechet_rows(program, forward)
    for side in ("plus", "minus"):
        component = f"BF_bulk_{side}"
        environment = gate.EvaluationEnvironment(
            values={
                f"A_{side}": connection,
                f"B_{side}": bfield,
                f"alpha_{side}": alpha,
                f"b_{side}": b_variation,
            },
            parameters={},
            partials={f"A_{side}": d_connection, f"alpha_{side}": d_alpha},
        )
        assert gate.evaluate_expr(forward[component], environment) == Fraction(99)
        component_rows = sorted(
            (row for row in rows if row["component"] == component),
            key=lambda row: row["summand_ordinal"],
        )
        observed = []
        for row in component_rows:
            slot = (
                b_variation
                if row["variation_component"] == f"b_{side}"
                else d_alpha
                if row["derivative"]["word"]
                else alpha
            )
            coefficient = gate.compat_coefficient_ast_to_expr(row["coefficient_ast"])
            observed.append(
                gate.evaluate_expr(
                    coefficient,
                    gate.EvaluationEnvironment(
                        values={f"A_{side}": connection, f"B_{side}": bfield},
                        parameters={},
                        partials={f"A_{side}": d_connection},
                        linear_slot=slot,
                    ),
                )
            )
        assert tuple(observed) == expected_rows
        assert sum(observed, Fraction(0)) == Fraction(99)

    bf_row = deepcopy(next(row for row in rows if row["component"] == "BF_bulk_plus"))

    def replace_pairing(node: dict, convention: str) -> bool:
        if node.get("op") == "invariant_pair_wedge":
            node["convention"] = convention
            return True
        return any(replace_pairing(arg, convention) for arg in node.get("args", []))

    for convention in ("-tr3/3", "+tr3/2", "-tr999/2"):
        mutant = deepcopy(bf_row)
        assert replace_pairing(mutant["coefficient_ast"], convention)
        _rehash(mutant)
        with pytest.raises(gate.SemanticFrechetError):
            gate.validate_frechet_row(mutant)

    duplicate_mixed = deepcopy(rows)
    plus_rows = sorted(
        (row for row in duplicate_mixed if row["component"] == "BF_bulk_plus"),
        key=lambda row: row["summand_ordinal"],
    )
    plus_rows[2]["coefficient_ast"] = deepcopy(plus_rows[1]["coefficient_ast"])
    _rehash(plus_rows[2])
    with pytest.raises(gate.SemanticFrechetError):
        gate.validate_frechet_row_collection(duplicate_mixed, program)


def test_strict_scalar_typechecker_and_rogue_metric_row_mutants(report: dict) -> None:
    metric = gate.field("g", gate.METRIC5)
    scalar = gate.field("s", gate.SCALAR5)
    oneform = gate.field("v", gate.ONEFORM5)
    rejected = (
        lambda: gate.scalar_mul(metric, scalar),
        lambda: gate.scale(metric, oneform),
        lambda: gate.power(metric, 2),
        lambda: gate.exp_scalar(metric),
        lambda: gate.sqrt_scalar(metric),
        lambda: gate.scalar_partial(metric, "g"),
    )
    for operation in rejected:
        with pytest.raises(gate.SemanticFrechetError):
            operation()
    campaign = report["scalar_and_row_mutation_campaign"]
    assert campaign["reject_rogue_metric_scalar_Frechet_row"] is True
    assert campaign["reject_BF_pairing_denominator_three_row"] is True
    assert campaign["reject_cross_side_BF_alias_collection"] is True
    assert campaign["reject_duplicate_mixed_BF_skeleton_collection"] is True
    assert all(campaign.values())


def test_semantic_completion_post_cache_mutation_cannot_stay_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        gate.SEMANTIC_COMPLETION["differential_normal_form"],
        "strict_real_scalar",
        "rogue post-cache completion",
    )
    with pytest.raises(gate.SemanticFrechetError):
        gate.build_report()


def test_all_action_route_alias_double_count_and_binder_mutants_die(
    report: dict,
) -> None:
    assert report["mutation_campaign"]
    assert all(report["mutation_campaign"].values())
    assert report["binder_mutation_campaign"]
    assert all(report["binder_mutation_campaign"].values())
    assert report["scalar_and_row_mutation_campaign"]
    assert all(report["scalar_and_row_mutation_campaign"].values())


def test_producer_and_expected_hash_co_mutation_is_killed_by_test_local_hash(
    report: dict,
) -> None:
    action, _payload = gate.certify_v52_dependency()
    mutant = gate._replace_action_once(
        action,
        "gauged_conformal_derivative",
        "+3*phi_eps",
        "+1*phi_eps",
    )
    program = gate.build_component_program(gate.parse_exact_action(mutant))
    observed = gate._aggregate_expr_sha256(program.components)
    assert observed != COMPONENT_ASTS_SHA256
    assert report["aggregate_hashes"]["component_ASTs_sha256"] == COMPONENT_ASTS_SHA256


def test_true_and_false_claim_frontier_is_exact(report: dict) -> None:
    assert report["checks"]["all"] is True
    assert {key for key, value in report["decision"].items() if value} == {
        "semantic_completion_conditional_scope_only",
        "exactly_eleven_component_Frechet_IR_pass",
        "FrechetRowV1_export_pass",
    }
    for key in (
        "all_twenty_action_components_semantically_decoded_pass",
        "EH_or_GHY_Frechet_pass",
        "K_R_R2_a_or_Robin_Frechet_pass",
        "moving_embedding_or_shape_derivative_pass",
        "full_formal_adjoint_or_Green_identity_pass",
        "full_bulk_boundary_assembly_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "full_classical_variational_principle_selected_sector_pass",
        "B4_pass",
        "B5_pass",
        "publication_authorized",
    ):
        assert report["decision"][key] is False


def test_report_only_writes_no_artifact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.iterdir())
    assert gate.build_report()["checks"]["all"] is True
    assert set(tmp_path.iterdir()) == before
