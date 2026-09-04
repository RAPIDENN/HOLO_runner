"""Tests for the v5.6.7 full-T^4 exact primitives (unit M1 + M2). No receipt: the report is built in-process."""

from __future__ import annotations

import ast
import math
from pathlib import Path

import numpy as np
import pytest

import derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7 as unit

EXPECTED_TRUE_KEYS = frozenset(
    {
        "full_t4_real_fourier_enumeration_matches_declared_N1_to_N11_pass",
        "full_t4_enumeration_beyond_priority_N12_N13_N81_N82_N83_N200_matches_declared_pass",
        "x2_axis_first_active_at_N8_and_x3_at_N10_pass",
        "free_layout_matches_bundle_contracts_N1_to_N3_pass",
        "spectral_tables_through_third_derivative_four_axes_sampled_within_tolerance_vs_pinned_route_b_and_sympy_pass",
        "radial_profiles_analytic_polynomial_derivatives_checked_K_le_8_pass",
        "pullback_constants_equal_to_pinned_route_c_pass",
        "pulled_back_two_jet_chain_rule_sampled_within_tolerance_vs_sympy_pass",
        "lexical_derivative_path_audit_no_forbidden_tokens_pass",
    }
)
EXPECTED_FALSE_KEYS = frozenset(
    {
        "action_or_jvp_claim_pass",
        "quadrature_claim_pass",
        "margins_claim_pass",
        "uniform_N_to_infinity_bridge_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    }
)


@pytest.fixture(scope="session")
def report() -> dict:
    return unit.build_report()


def test_module_imports_and_pins() -> None:
    source = Path(unit.__file__).read_text()
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    assert not any("one_omega_topological_so3" in name for name in names)
    assert not any(name in {"torch", "scipy", "runpy"} for name in names)
    assert source.count("spec_from_file_location") == 1
    assert unit._sha256(unit.DECLARED_ENUMERATION_PATH) == unit.DECLARED_ENUMERATION_SHA256
    assert unit._sha256(unit.ROUTE_B_PATH) == unit.ROUTE_B_SHA256
    assert unit._sha256(unit.ROUTE_C_PATH) == unit.ROUTE_C_SHA256
    assert unit._sha256(unit.BUNDLE_PATH) == unit.BUNDLE_SHA256
    # no untracked artifact is read: the only JSON opened is the tracked C2 bundle
    assert source.count("ARTIFACTS /") == 1


def test_decision_keys(report: dict) -> None:
    decision = report["decision"]
    assert set(decision) == EXPECTED_TRUE_KEYS | EXPECTED_FALSE_KEYS
    for key in EXPECTED_TRUE_KEYS:
        assert decision[key] is True, key
    for key in EXPECTED_FALSE_KEYS:
        assert decision[key] is False, key
    assert "no receipt" in report["scope"]


def test_enumeration_against_declared_and_bundle(report: dict) -> None:
    enumeration = report["enumeration"]
    assert enumeration["declared_prefix_match_all_N"] and enumeration["bundle_labels_match_N1_to_N3"]
    beyond = report["enumeration_beyond_priority"]
    assert beyond["pass"] is True and beyond["rows"]["82"]["last_mode_inf_norm"] == 2 and beyond["rows"]["13"]["last_mode_kind"] == "sin"
    assert report["tables"]["max_abs_difference_vs_sympy_synthetic_mode_through_third"] <= 1.0e-10
    assert enumeration["first_N_with_x2"] == 8 and enumeration["first_N_with_x3"] == 10
    for N in range(1, 4):
        assert not enumeration["rows"][str(N)]["axes_active"][2]
    assert enumeration["rows"]["8"]["modes"][7] == "cos(1*x2)"
    assert enumeration["rows"]["9"]["modes"][8] == "sin(1*x2)"
    assert enumeration["rows"]["11"]["modes"][9:] == ["cos(1*x3)", "sin(1*x3)"]


def test_x2_derivatives_are_nonzero_from_N8(report: dict) -> None:
    rng = np.random.default_rng(1)
    points = rng.uniform(0.0, 2.0 * math.pi, size=(6, 4))
    for N in (7, 8, 9):
        tables = unit.spectral_tables(unit.real_fourier_modes(N), points)
        x2_first = float(np.max(np.abs(tables["first"][:, 2, :])))
        assert (x2_first > 0.1) == (N >= 8), N


def test_layout_general_and_bundle(report: dict) -> None:
    layout = report["layout"]
    for N in ("1", "2", "3"):
        assert layout["rows"][N]["blocks_equal"] and layout["rows"][N]["canonical_sha_equal"] and layout["rows"][N]["dimension_equal"]
    assert layout["rows"]["2"]["dimension"] == 996
    general = unit.free_layout(9, 9)
    assert general["free_coordinate_dimension"] == 9 * (10 + 1 + 1 + 3 + 12 + 3 + 2 * (1 + 5 + 3 + 30 + 3 + 64 + 9 * 64))
    order = [name for name, _ in sorted(general["blocks"].items(), key=lambda kv: kv[1]["start"])]
    assert order[:6] == ["common.gamma", "common.T", "common.log_Omega", "common.varphi_E0", "common.A_E0", "Q_frame.q"]
    assert order[6] == "plus.Y" and order[13] == "minus.Y"


def test_tables_radial_and_pullback_numbers(report: dict) -> None:
    assert report["tables"]["max_abs_difference_vs_pinned_route_b"] <= 1.0e-12
    assert report["tables"]["max_abs_difference_vs_sympy_through_third"] <= 1.0e-11
    assert report["radial"]["max_abs_difference_vs_v5_6_6_3_bumps_K_le_3"] <= 1.0e-12
    assert report["radial"]["max_abs_difference_vs_sympy_through_second_derivative_K8"] <= 1.0e-9
    assert report["radial"]["bump_degrees_K8"] == {f"b_{j}": 6 + j for j in range(8)}
    assert report["radial"]["rho_samples"][:2] == [0.0, 1.0] and report["radial"]["K_symbolic"] == 8
    assert report["constants_vs_pinned_route_c"]["pass"] is True
    assert report["pullback"]["max_abs_difference_vs_sympy_value_first_second"] <= 1.0e-10


def test_static_derivative_path_audit(report: dict, tmp_path: Path) -> None:
    # lexical audit of the shipped module (not a semantic proof); mutant written under pytest's tmp_path only
    assert report["static"]["forbidden_hits"] == []
    mutated = Path(unit.__file__).read_text() + "\nCOORD_THETA_STEP = 0.03\n"
    tmp = tmp_path / "_mutant_step_v5_6_7.py"
    tmp.write_text(mutated)
    assert unit.static_derivative_path_audit(tmp)["pass"] is False


def test_mutant_x2_axis_zeroed_fails_enumeration_activity() -> None:
    modes = unit.real_fourier_modes(9)
    zeroed = [dict(m, wavevector=(m["wavevector"][0], m["wavevector"][1], 0, m["wavevector"][3])) for m in modes]
    points = np.random.default_rng(2).uniform(0.0, 2.0 * math.pi, size=(4, 4))
    assert float(np.max(np.abs(unit.spectral_tables(zeroed, points)["first"][:, 2, :]))) == 0.0
    assert float(np.max(np.abs(unit.spectral_tables(modes, points)["first"][:, 2, :]))) > 0.1


def test_mutant_theta_only_basis_diverges_from_declared_at_N4() -> None:
    theta_only = [(1, 1, 0, 0)] * 6
    assert unit.nonzero_wavevectors(2)[1] == (1, 0, 0, 0) != theta_only[1]


def test_mutant_truncated_K_changes_radial_content() -> None:
    full = unit.radial_profiles(0.4, 5)
    truncated = unit.radial_profiles(0.4, 3)
    assert full["bumps"].shape == (3, 5) and truncated["bumps"].shape == (3, 3)
    assert np.allclose(full["bumps"][:, :3], truncated["bumps"])
    assert float(np.max(np.abs(full["bumps"][:, 3:]))) > 0.0


def test_spectral_tables_sin_branch_and_unknown_kind_rejected() -> None:
    points = np.random.default_rng(4).uniform(0.0, 2.0 * math.pi, size=(3, 4))
    k = (0, 1, 2, 0)
    phase = points @ np.asarray(k, dtype=float)
    sin_tables = unit.spectral_tables([{"kind": "sin", "wavevector": k, "label": "sin"}], points)
    assert np.allclose(sin_tables["values"][:, 0], np.sin(phase))
    assert np.allclose(sin_tables["first"][:, 1, 0], np.cos(phase))
    assert np.allclose(sin_tables["second"][:, 1, 2, 0], -2.0 * np.sin(phase))
    with pytest.raises(unit.ExactPrimitivesError):
        unit.spectral_tables([{"kind": "tan", "wavevector": k, "label": "bad"}], points)


def test_radial_rejects_K_below_one() -> None:
    for K in (0, -1):
        with pytest.raises(unit.ExactPrimitivesError):
            unit.radial_profile_polynomials(K)
        with pytest.raises(unit.ExactPrimitivesError):
            unit.radial_profiles(0.3, K)


def test_discrete_apis_reject_nonintegers_and_accept_numpy_integers() -> None:
    for bad in (True, 1.5, "2"):
        with pytest.raises(unit.ExactPrimitivesError):
            unit.nonzero_wavevectors(bad)
        with pytest.raises(unit.ExactPrimitivesError):
            unit.real_fourier_modes(bad)
        with pytest.raises(unit.ExactPrimitivesError):
            unit.free_layout(bad, 1)
        with pytest.raises(unit.ExactPrimitivesError):
            unit.free_layout(1, bad)
    with pytest.raises(unit.ExactPrimitivesError):
        unit.nonzero_wavevectors(-1)
    assert len(unit.real_fourier_modes(np.int64(3))) == 3
    assert unit.free_layout(np.int64(2), np.int64(2))["free_coordinate_dimension"] == 996


def test_constants_gate_detects_common_mode_drift() -> None:
    from types import SimpleNamespace

    same = SimpleNamespace(SIDES=unit.SIDES, SIDE_RADIAL_SIGN=unit.SIDE_RADIAL_SIGN, REFERENCE_METRIC=unit.REFERENCE_METRIC, SYMMETRIC5=unit.SYMMETRIC5, B_TRIPLES=unit.B_TRIPLES)
    assert unit.check_constants_against_pinned_route_c(same)["pass"] is True
    drifted = SimpleNamespace(**{**vars(same), "REFERENCE_METRIC": np.diag((-1.64, 1.17, 1.31, 1.46, 1.18))})
    assert unit.check_constants_against_pinned_route_c(drifted)["pass"] is False
    swapped = SimpleNamespace(**{**vars(same), "SIDE_RADIAL_SIGN": {"plus": 1.0, "minus": -1.0}})
    assert unit.check_constants_against_pinned_route_c(swapped)["pass"] is False


def test_pullback_rejects_wrong_shapes_and_side() -> None:
    rng = np.random.default_rng(5)
    good = dict(ambient_value=rng.normal(size=64), ambient_first=rng.normal(size=(5, 64)), ambient_second=rng.normal(size=(5, 5, 64)),
                Y_first=rng.normal(size=4), Y_second=rng.normal(size=(4, 4)), Y_third=rng.normal(size=(4, 4, 4)))
    out = unit.pulled_back_two_jet(side="plus", **good)
    assert out["value"].shape == (79,) and out["first"].shape == (5, 79) and out["second"].shape == (5, 5, 79)
    with pytest.raises(unit.ExactPrimitivesError):
        unit.pulled_back_two_jet(side="up", **good)
    for name, bad_shape in (("ambient_value", (65,)), ("ambient_first", (5, 65)), ("ambient_second", (5, 4, 64)), ("Y_first", (5,)), ("Y_second", (4, 5)), ("Y_third", (4, 4, 3))):
        bad = {**good, name: rng.normal(size=bad_shape)}
        with pytest.raises(unit.ExactPrimitivesError):
            unit.pulled_back_two_jet(side="minus", **bad)


def test_free_layout_uses_exact_integers_for_large_N() -> None:
    N, K = 10**16, 8
    layout = unit.free_layout(N, K)
    per_N = sum(math.prod(K if s == "K" else int(s) for s in shape) for _, shape in unit.COMMON_BLOCKS) + 2 * sum(math.prod(K if s == "K" else int(s) for s in shape) for _, shape in unit.SIDE_BLOCKS)
    assert layout["free_coordinate_dimension"] == N * per_N > 2**63
    assert all(block["stop"] - block["start"] == math.prod(block["shape"]) for block in layout["blocks"].values())


def test_main_uses_current_report_keys(report: dict, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(unit, "build_report", lambda: report)
    unit.main()
    output = capsys.readouterr().out
    assert "sympy K8" in output and "pullback vs sympy" in output


def test_jet2_product_rule() -> None:
    rng = np.random.default_rng(3)
    a = unit.Jet2(rng.normal(), rng.normal(size=5), rng.normal(size=(5, 5)))
    b = unit.Jet2(rng.normal(), rng.normal(size=5), rng.normal(size=(5, 5)))
    c = a * b
    assert math.isclose(c.v, a.v * b.v)
    assert np.allclose(c.d, a.v * b.d + b.v * a.d)
    assert np.allclose(c.dd, a.v * b.dd + b.v * a.dd + np.outer(a.d, b.d) + np.outer(b.d, a.d))
