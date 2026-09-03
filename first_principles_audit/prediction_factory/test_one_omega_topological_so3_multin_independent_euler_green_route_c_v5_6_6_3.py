from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from first_principles_audit.prediction_factory import (
    derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3
    as route,
)


@pytest.fixture(scope="session")
def receipt() -> dict:
    return route.build_payload()


def test_route_c_import_graph_is_independent() -> None:
    tree = ast.parse(Path(route.__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = ("torch", "literal_torch_action", "numpy_c2_multin_fd5")
    assert not any(any(token in name for token in forbidden) for name in imported)


def test_literal_action_and_primitive_bundle_are_byte_pinned() -> None:
    bundle = route.load_bundle()
    assert route._sha256(route.BUNDLE) == route.BUNDLE_SHA256
    assert bundle["action_contract"]["exact_action_sha256"] == route.LITERAL_V5_2_ACTION_SHA256


def test_all_selected_spectral_members_close_locally(receipt: dict) -> None:
    members = receipt["scientific"]["members"]
    assert [(row["N"], row["K"]) for row in members] == [(1, 1), (2, 2), (3, 3)]
    for row in members:
        assert row["selected_member_Euler_Green_pass"] is True
        assert row["maximum_absolute_local_chain_residual"] <= route.LOCAL_CHAIN_ABS_TOLERANCE
        assert row["maximum_absolute_component_Stokes_residual"] <= route.STOKES_COMPONENT_ABS_TOLERANCE
        assert row["total_absolute_Stokes_residual"] <= route.STOKES_TOTAL_ABS_TOLERANCE
        expected = set(route.ACTION_COMPONENTS) | {"S_total"}
        assert set(row["direct_local_free_JVP_by_component"]) == expected
        assert set(row["Euler_plus_Green_by_component"]) == expected
        assert set(row["Stokes_residual_by_component"]) == expected


def test_only_restricted_route_c_lemma_is_green(receipt: dict) -> None:
    decision = receipt["decision"]
    assert decision["route_C_multin_independent_Euler_Green_pass"] is True
    for key in (
        "clean_room_full_mutant_campaign_pass",
        "uniform_N_to_infinity_bridge_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    ):
        assert decision[key] is False


def test_artifact_is_fresh_and_byte_reproducible(receipt: dict) -> None:
    assert route.OUTPUT.exists()
    stored = json.loads(route.OUTPUT.read_text(encoding="utf-8"))
    assert stored == receipt
    encoded = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert route.OUTPUT.read_text(encoding="utf-8") == encoded
