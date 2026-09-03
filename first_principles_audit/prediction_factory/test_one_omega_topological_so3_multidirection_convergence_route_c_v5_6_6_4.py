from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_multidirection_convergence_route_c_v5_6_6_4
    as campaign,
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    assert campaign.OUTPUT.exists()
    return json.loads(campaign.OUTPUT.read_text(encoding="utf-8"))


def test_campaign_import_graph_reads_only_independent_route_c() -> None:
    tree = ast.parse(Path(campaign.__file__).read_text(encoding="utf-8"))
    project_imports: list[str] = []
    all_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            all_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            all_imports.append(module)
            if module.startswith("first_principles_audit"):
                project_imports.append(module)
    assert project_imports == ["first_principles_audit.prediction_factory"]
    forbidden = ("torch", "literal_torch_action", "numpy_c2_multin_fd5")
    assert not any(any(token in name for token in forbidden) for name in all_imports)


def test_route_c_lineage_is_byte_pinned() -> None:
    assert campaign._sha256(campaign.ROUTE_C_SOURCE) == campaign.ROUTE_C_SOURCE_SHA256
    assert campaign._sha256(campaign.ROUTE_C_TEST) == campaign.ROUTE_C_TEST_SHA256
    assert campaign._sha256(campaign.ROUTE_C_ARTIFACT) == campaign.ROUTE_C_ARTIFACT_SHA256
    pinned = campaign._read_pinned_route_c()
    assert pinned["decision"]["route_C_multin_independent_Euler_Green_pass"] is True


def test_all_members_and_all_four_directions_are_published(receipt: dict) -> None:
    rows = receipt["scientific"]["member_campaigns"]
    assert [(row["N"], row["K"]) for row in rows] == [(1, 1), (2, 2), (3, 3)]
    expected_components = set(campaign.route_c.ACTION_COMPONENTS) | {"S_total"}
    for row in rows:
        assert set(row["directions"]) == set(campaign.CURVE_NAMES)
        assert row["all_four_directions_Euler_Green_pass"] is True
        assert row["member_campaign_pass"] is False
        for direction in row["directions"].values():
            assert direction["selected_member_Euler_Green_pass"] is True
            assert set(direction["direct_local_free_JVP_by_component"]) == expected_components
            assert set(direction["Euler_plus_Green_by_component"]) == expected_components
            assert set(direction["Stokes_residual_by_component"]) == expected_components
            assert set(direction["normalized_Stokes_residual_by_component"]) == expected_components


def test_separate_refinements_archive_the_observed_subresolution(receipt: dict) -> None:
    rows = receipt["scientific"]["member_campaigns"]
    expected = {
        1: {"radial": False, "tangential": True},
        2: {"radial": True, "tangential": False},
        3: {"radial": True, "tangential": False},
    }
    for row in rows:
        refinement = row["refinement"]
        assert set(refinement["radial"]["records_by_order"]) == {"8", "10", "12"}
        assert refinement["radial"]["Q10_vs_Q12"]["pass"] is expected[row["N"]]["radial"]
        assert set(refinement["tangential"]["records_by_order"]) == {"3", "5", "7"}
        assert refinement["tangential"]["Q5_vs_Q7"]["pass"] is expected[row["N"]]["tangential"]
        assert set(refinement["free_step"]["records_by_step"]) == {
            "0.001",
            "0.002",
            "0.004",
        }
        assert refinement["free_step"]["h0p002_vs_h0p001"]["pass"] is True
        assert set(refinement["coordinate_step"]["records_by_step"]) == {
            "0.004",
            "0.005",
            "0.006",
        }
        assert refinement["coordinate_step"]["h0p005_vs_h0p004"]["pass"] is True
        assert refinement["N_and_K"]["not_a_continuum_rate"] is True
        faces = row["periodic_eight_face_audit"]
        assert len(faces["eight_oriented_faces_grouped_as_four_pairs"]) == 4
        assert faces["pass"] is True
        assert row["member_convergence_pass"] is False
        assert row["member_campaign_pass"] is False


def test_only_four_direction_lemma_is_green_and_refinement_fails_closed(receipt: dict) -> None:
    decision = receipt["decision"]
    assert decision["route_C_all_four_directions_multi_N_pass"] is True
    assert decision["route_C_h_and_quadrature_convergence_pass"] is False
    assert decision["restricted_spectral_family_Euler_Green_certificate_pass"] is False
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
    assert receipt["scientific"]["N_K_scope"]["continuous_limit_inferred"] is False


def test_artifact_is_canonical_and_provenance_is_current(receipt: dict) -> None:
    encoded = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert campaign.OUTPUT.read_text(encoding="utf-8") == encoded
    provenance = receipt["provenance"]
    assert provenance["generator"]["sha256"] == campaign._sha256(Path(campaign.__file__))
    assert provenance["test"]["sha256"] == campaign._sha256(Path(__file__))
