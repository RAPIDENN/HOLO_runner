from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_ad_fd5_route_c_three_way_v5_6_6_6
    as comparator,
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    assert comparator.OUTPUT.exists()
    return json.loads(comparator.OUTPUT.read_text(encoding="utf-8"))


def test_import_graph_does_not_load_ad_or_fd5_action_helpers() -> None:
    tree = ast.parse(Path(comparator.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = (
        "torch_c2_multin",
        "literal_torch_action",
        "numpy_c2_multin_fd5",
        "numpy_fd5_action",
    )
    assert not any(any(token in name for token in forbidden) for name in imported)


def test_all_five_input_receipts_are_byte_pinned() -> None:
    cases = (
        (comparator.AD_ARTIFACT, comparator.AD_ARTIFACT_SHA256, comparator.AD_SCHEMA),
        (comparator.FD5_ARTIFACT, comparator.FD5_ARTIFACT_SHA256, comparator.FD5_SCHEMA),
        (
            comparator.ROUTE_C_ARTIFACT,
            comparator.ROUTE_C_ARTIFACT_SHA256,
            comparator.route_c_stable.route_c.SCHEMA,
        ),
        (
            comparator.FOUR_DIRECTION_ARTIFACT,
            comparator.FOUR_DIRECTION_ARTIFACT_SHA256,
            "holo.one-omega-topological-so3-multidirection-convergence-route-c-v5-6-6-4.v1",
        ),
        (
            comparator.PRECISION_ARTIFACT,
            comparator.PRECISION_ARTIFACT_SHA256,
            comparator.route_c_stable.SCHEMA,
        ),
    )
    for path, digest, schema in cases:
        assert comparator._read_pinned(path, digest, schema)["schema"] == schema


def test_three_selected_members_close_componentwise(receipt: dict) -> None:
    members = receipt["scientific"]["members"]
    assert [(row["N"], row["K"]) for row in members] == [(1, 1), (2, 2), (3, 3)]
    expected = set(comparator.route_c_stable.route_c.ACTION_COMPONENTS) | {"S_total"}
    for row in members:
        assert row["quadrature"] == {
            "tangential_order_per_axis": 5,
            "radial_order": 10,
        }
        assert set(row["AD_JVP"]) == expected
        assert set(row["FD5_Richardson_JVP"]) == expected
        assert set(row["Route_C_precision_stabilized_JVP"]) == expected
        comparison = row["comparison"]
        assert set(comparison["rows"]) == expected
        assert comparison["maximum_residual_over_tolerance"] <= 1.0
        assert comparison["pass"] is True
        assert row["member_three_way_pass"] is True
        for component in comparison["rows"].values():
            assert set(component["raw_signed_residuals"]) == {
                "AD_minus_FD5",
                "AD_minus_Route_C",
                "FD5_minus_Route_C",
            }
            assert set(component["normalized_residuals"]) == set(
                component["raw_signed_residuals"]
            )
            assert component["pass"] is True
        assert all(value > 0.999999999999 for value in comparison["pairwise_cosine"].values())


def test_comparator_rejects_sign_and_component_mutants() -> None:
    baseline = {"bulk": 3.0, "interface": -2.0, "S_total": 1.0}
    sign_mutant = {"bulk": -3.0, "interface": 2.0, "S_total": -1.0}
    result = comparator._three_way_rows(baseline, baseline, sign_mutant)
    assert result["pass"] is False
    assert result["rows"]["bulk"]["same_sign_when_active"] is False
    with pytest.raises(comparator.ThreeWayComparatorError):
        comparator._three_way_rows(baseline, baseline, {"bulk": 3.0})


def test_only_restricted_three_route_certificate_is_green(receipt: dict) -> None:
    decision = receipt["decision"]
    assert decision["AD_FD5_Route_C_three_way_comparison_pass"] is True
    assert decision["Route_C_independent_Euler_Green_multi_N_pass"] is True
    assert decision["Route_C_four_directions_multi_N_pass"] is True
    assert decision["Route_C_precision_stabilized_convergence_pass"] is True
    assert decision["restricted_spectral_family_three_route_certificate_pass"] is True
    for key in (
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
    assert comparator.OUTPUT.read_text(encoding="utf-8") == encoded
    assert receipt["provenance"]["generator"]["sha256"] == comparator._sha256(
        Path(comparator.__file__)
    )
    assert receipt["provenance"]["test"]["sha256"] == comparator._sha256(Path(__file__))
