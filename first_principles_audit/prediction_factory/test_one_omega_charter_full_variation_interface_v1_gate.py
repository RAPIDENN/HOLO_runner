"""Tests for the stage-v1 full variation of the one-Omega action charter (brane sector).

Fast tests bind the charter, check the pinned strings, the fail-closed physical
keys and the structure of the stored artifact.  The symbolic derivation itself is
re-run only when HOLO_FULL_VARIATION_FRESH=1 (it takes minutes); otherwise the
stored artifact is checked for internal consistency and provenance.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import sympy as sp

import derive_one_omega_charter_full_variation_interface_v1_gate as gate

FRESH = os.environ.get("HOLO_FULL_VARIATION_FRESH") == "1"


@pytest.fixture(scope="module")
def stored() -> dict:
    assert gate.OUTPUT.is_file(), "artifact absent: run the generator first"
    return json.loads(gate.OUTPUT.read_text(encoding="utf-8"))


def test_charter_binds_by_recorded_and_recomputed_digest() -> None:
    payload, sha = gate._load_charter()
    assert payload["action_charter_digest"]["sha256"] == gate.EXPECTED_CHARTER_DIGESTS["action_charter_digest"]
    assert len(sha) == 64


def test_pinned_strings_are_verbatim_in_charter() -> None:
    payload, _ = gate._load_charter()
    charter = payload["action_charter"]
    for dotted, expected in gate.PINNED_STRINGS.items():
        block, key = dotted.split(".")
        assert charter[block][key] == expected


def test_tampered_charter_digest_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(gate.EXPECTED_CHARTER_DIGESTS, "action_charter_digest", "0" * 64)
    with pytest.raises(gate.FullVariationError):
        gate._load_charter()


def test_tampered_pinned_string_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(gate.PINNED_STRINGS, "exact_action.solid", "S_X=0")
    with pytest.raises(gate.FullVariationError):
        gate._load_charter()


def test_truncation_helper_drops_higher_orders() -> None:
    e = gate.EPS
    assert sp.expand(gate.trunc(1 + e + e**2 + e**3 + 5 * e**4) - (1 + e + e**2)) == 0
    assert sp.expand(gate.series_sqrt(1 + e) - (1 + e / 2 - e**2 / 8)) == 0
    assert sp.expand(gate.series_inv_sqrt(1 + e) - (1 - e / 2 + 3 * e**2 / 8)) == 0


def test_n7_invariant_rebuilt_has_expected_shape() -> None:
    expr = gate.n7_solid_invariant({})
    # quadratic in the fluctuations, contains the shift-solid mixing and the H-solid mixing
    assert expr.has(gate.N[2]) and expr.has(gate.pi_[2]) and expr.has(gate.H[2][2])
    # V1 term: rho*(pi_dot - v N)^2/2 -> coefficient of N3^2 is rho v^2 / 2
    assert sp.simplify(expr.coeff(gate.N[2], 2) - gate.rho * gate.v**2 / 2) == 0


def test_every_physical_key_is_false(stored: dict) -> None:
    for key in gate.PHYSICAL_FALSE_KEYS:
        assert stored["decision"][key] is False, key


def test_stage_scope_is_declared_and_bulk_not_varied(stored: dict) -> None:
    assert "g_MN bulk" in stored["stage"]["not_varied"]
    assert "GHY" in stored["stage"]["not_varied"]
    assert stored["decision"]["bulk_fields_varied_pass"] is False
    assert stored["decision"]["junction_conditions_derived_pass"] is False
    assert stored["decision"]["old_wall_ADM_Hessian_consumed"] is False
    assert stored["decision"]["n7_v3_artifact_consumed"] is False


def test_stored_checks_all_pass(stored: dict) -> None:
    failing = [k for k, v in stored["checks"].items() if v is not True]
    assert not failing, failing


def test_tadpoles_match_expectations(stored: dict) -> None:
    tad = stored["tadpoles"]
    for name in ("tau", "pi1", "pi2", "pi3", "vphi1", "vphi2", "vphi3", "N1", "N2", "N3", "H12", "H13", "H23"):
        assert sp.simplify(sp.sympify(tad[name])) == 0, name
    tension = sp.sympify(stored["background"]["tension_2W_at_1"])
    assert sp.simplify(sp.sympify(tad["n"]) + tension) == 0
    for i in (1, 2, 3):
        assert sp.simplify(sp.sympify(tad[f"H{i}{i}"]) + tension / 2) == 0
    assert sp.simplify(sp.sympify(tad["omega"]) - sp.sympify(stored["expected_tadpoles"]["omega"])) == 0


def test_hessian_helicity_sets_partition_fields(stored: dict) -> None:
    sets = stored["extended_hessian"]["helicity_sets"]
    names = sorted(sum(sets.values(), []))
    assert names == sorted(gate.HEL_NAMES)
    assert len(sets["scalar"]) == 8 and len(sets["vector"]) == 8 and len(sets["tensor"]) == 2


def test_gauge_null_checks_recorded_and_true(stored: dict) -> None:
    g = stored["extended_hessian"]["gauge_null_checks"]
    assert set(g) == {"time_reparametrization", "spatial_diffeomorphism_x", "spatial_diffeomorphism_y", "spatial_diffeomorphism_z"}
    for k, v in g.items():
        assert v["null"] is True and v["residual_nonzero_rows"] == [], k


def test_numerical_blocks_are_square_and_finite(stored: dict) -> None:
    blocks = stored["extended_hessian"]["numerical_blocks_at_frozen_point"]
    for name, rows in blocks.items():
        n = len(rows)
        assert all(len(r) == n for r in rows), name
        for r in rows:
            for e in r:
                sp.sympify(e)  # must parse; may depend on q and w


def test_provenance_and_digest(stored: dict) -> None:
    assert stored["schema"] == gate.SCHEMA
    assert stored["upstream_bindings"]["one_omega_action_charter_gate.json"]["sha256"] == gate._sha256(gate.CHARTER)
    recomputed = gate._canonical_digest({k: stored[k] for k in gate.DIGEST_KEYS})
    assert recomputed == stored["calculation_digest"]
    assert "extended_hessian" in gate.DIGEST_KEYS and "checks" in gate.DIGEST_KEYS


def _digest_of(payload: dict) -> str:
    return gate._canonical_digest({k: payload[k] for k in gate.DIGEST_KEYS})


def test_mutating_a_hessian_entry_breaks_the_digest(stored: dict) -> None:
    import copy
    mutant = copy.deepcopy(stored)
    blocks = mutant["extended_hessian"]["numerical_blocks_at_frozen_point"]
    blocks["scalar"][0][0] = str(sp.sympify(blocks["scalar"][0][0]) + 1)
    assert _digest_of(mutant) != stored["calculation_digest"]
    mutant = copy.deepcopy(stored)
    mutant["extended_hessian"]["symbolic_matrix_helicity_basis"][0][0] = "0"
    assert _digest_of(mutant) != stored["calculation_digest"]


def test_mutating_gauge_or_source_record_breaks_the_digest(stored: dict) -> None:
    import copy
    mutant = copy.deepcopy(stored)
    mutant["extended_hessian"]["gauge_null_checks"]["time_reparametrization"]["null"] = False
    assert _digest_of(mutant) != stored["calculation_digest"]
    mutant = copy.deepcopy(stored)
    mutant["upstream_bindings"]["one_omega_action_charter_gate.json"]["sha256"] = "0" * 64
    assert _digest_of(mutant) != stored["calculation_digest"]


def test_helicity_basis_is_irreducible_8_8_2(stored: dict) -> None:
    sets = stored["extended_hessian"]["helicity_sets"]
    assert len(sets["scalar"]) == 8 and len(sets["vector"]) == 8 and len(sets["tensor"]) == 2
    assert sorted(sets["tensor"]) == ["H12", "Hd"]
    order = stored["extended_hessian"]["helicity_field_order"]
    M = stored["extended_hessian"]["symbolic_matrix_helicity_basis"]
    assert len(M) == 18 and all(len(r) == 18 for r in M)
    i, j = order.index("Hd"), order.index("H12")
    assert sp.simplify(sp.sympify(M[i][i]) - sp.sympify(M[j][j])) == 0
    assert sp.sympify(M[i][j]) == 0


@pytest.mark.skipif(not FRESH, reason="set HOLO_FULL_VARIATION_FRESH=1 to re-run the symbolic derivation")
def test_fresh_derivation_matches_stored_digest(stored: dict) -> None:
    fresh = gate.derive()
    assert fresh["calculation_digest"] == stored["calculation_digest"]
