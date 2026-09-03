from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5
    as correction,
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    assert correction.OUTPUT.exists()
    return json.loads(correction.OUTPUT.read_text(encoding="utf-8"))


def test_import_graph_contains_no_ad_or_fd5_action_route() -> None:
    tree = ast.parse(Path(correction.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = ("torch", "literal_torch_action", "numpy_c2_multin_fd5")
    assert not any(any(token in name for token in forbidden) for name in imported)


def test_previous_red_receipt_is_byte_pinned_and_preserved() -> None:
    previous = correction._read_previous_red_receipt()
    assert correction._sha256(correction.PREVIOUS_SOURCE) == correction.PREVIOUS_SOURCE_SHA256
    assert correction._sha256(correction.PREVIOUS_TEST) == correction.PREVIOUS_TEST_SHA256
    assert correction._sha256(correction.PREVIOUS_ARTIFACT) == correction.PREVIOUS_ARTIFACT_SHA256
    assert previous["decision"]["route_C_all_four_directions_multi_N_pass"] is True
    assert previous["decision"]["route_C_h_and_quadrature_convergence_pass"] is False


def test_nine_point_stencil_has_the_declared_moments() -> None:
    for power in range(9):
        first = sum(
            coefficient * correction.LD(offset) ** power
            for offset, coefficient in correction.FIRST_WEIGHTS.items()
        )
        second = sum(
            coefficient * correction.LD(offset) ** power
            for offset, coefficient in correction.SECOND_WEIGHTS.items()
        )
        expected_first = correction.LD(1) if power == 1 else correction.LD(0)
        expected_second = correction.LD(2) if power == 2 else correction.LD(0)
        assert abs(first - expected_first) < correction.LD("1e-14")
        assert abs(second - expected_second) < correction.LD("1e-14")


def test_stabilized_pullback_matches_value_map_and_retains_extended_precision() -> None:
    bundle = correction.route_c.load_bundle()
    member = bundle["primary_members"][1]
    contract = bundle["pointwise_decoder_contract_by_N"]["2"]
    free = correction.route_c._decode_f64(member["authoritative_free_central_f64le"])
    baseline = correction.route_c._pullback_vector(free, contract, "plus", 0.37, 0.41)
    stabilized = correction._pullback_vector_ld(free, contract, "plus", 0.37, 0.41)
    assert np.max(np.abs(np.asarray(baseline[0]) - np.asarray(stabilized[0]))) < 1.0e-12
    assert np.max(np.abs(np.asarray(baseline[1]) - np.asarray(stabilized[1]))) < 1.0e-12
    jet = correction.stable_bulk_jet(free, contract, "plus", 0.37, 0.41)
    assert all(value.dtype == np.dtype(np.longdouble) for value in jet.values())
    assert all(np.all(np.isfinite(value)) for value in jet.values())
    assert np.finfo(np.longdouble).eps < np.finfo(np.float64).eps


def test_all_precision_stabilized_refinements_pass(receipt: dict) -> None:
    members = receipt["scientific"]["members"]
    assert [(row["N"], row["K"]) for row in members] == [(1, 1), (2, 2), (3, 3)]
    expected_components = set(correction.route_c.ACTION_COMPONENTS) | {"S_total"}
    for row in members:
        assert set(row["radial"]["records_by_order"]) == {"12", "14", "16"}
        assert set(row["tangential"]["records_by_order"]) == {"11", "13", "15"}
        assert row["radial"]["Q14_vs_Q16"]["pass"] is True
        assert row["tangential"]["Q13_vs_Q15"]["pass"] is True
        assert row["member_precision_stabilized_convergence_pass"] is True
        for record in row["radial"]["records_by_order"].values():
            assert set(record) == expected_components
        for record in row["tangential"]["records_by_order"].values():
            assert set(record) == expected_components


def test_only_the_restricted_precision_correction_is_green(receipt: dict) -> None:
    decision = receipt["decision"]
    assert decision["v5_6_6_4_red_subresolved_receipt_preserved"] is True
    assert decision["route_C_all_four_directions_multi_N_pass_from_pinned_v5_6_6_4"] is True
    assert decision["precision_stabilized_radial_and_tangential_convergence_pass"] is True
    assert decision["restricted_spectral_family_precision_correction_pass"] is True
    for key in (
        "AD_FD5_Route_C_three_way_comparison_pass",
        "independent_clean_process_redteam_pass",
        "full_mutant_campaign_pass",
        "uniform_N_to_infinity_bridge_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False


def test_artifact_is_canonical_and_provenance_is_current(receipt: dict) -> None:
    encoded = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert correction.OUTPUT.read_text(encoding="utf-8") == encoded
    assert receipt["provenance"]["generator"]["sha256"] == correction._sha256(
        Path(correction.__file__)
    )
    assert receipt["provenance"]["test"]["sha256"] == correction._sha256(Path(__file__))
