#!/usr/bin/env python3
"""Exact whole-domain margins for one named full-T4 direct-free member.

This gate closes one deliberately finite obligation left open by v5.6.7.3.  It
constructs a sparse N=81, K=1 member of the byte-pinned v5.6.7/v5.6.7.1
direct-free layout and proves every analytic open margin on T4 x [0,1].  All
scientific comparisons use ``fractions.Fraction``.  There is no sampled grid,
floating-point eigensolver, decimal tolerance, or post-hoc safety pad in the
decision path.

The member is nontrivial in the new x2 direction: Y has a sin(x2) coefficient
and the interior log-Omega channel has b_0(rho) cos(x2).  Consequently the
moving-collar pullback is nontrivial, while its metric effect has a short exact
Weyl enclosure.  The proof is stronger than outward-rounded binary arithmetic:
every endpoint is an exact rational enclosing the real interpretation of the
named binary64 coefficient vector.

Scope is intentionally narrow.  This is not a generic interval engine, a
runtime/TaylorDual3 acceptance certificate, a quadrature certificate, an
infinite-target result, or a C1/N1/P4/B4/B5 promotion.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import platform
import struct
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = (
    ARTIFACTS
    / "one_omega_topological_so3_direct_free_finite_member_exact_margin_v5_6_7_5_gate.json"
)
TEST = (
    HERE
    / "test_one_omega_topological_so3_direct_free_finite_member_exact_margin_v5_6_7_5_gate.py"
)
SCHEMA = (
    "holo.one-omega-topological-so3-direct-free-finite-member-"
    "exact-margin-v5-6-7-5.v1"
)

V567_SOURCE = HERE / "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
V567_TEST = HERE / "test_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
V567_SOURCE_SHA256 = "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25"
V567_TEST_SHA256 = "3fdcd09c3e575893dade6a396865a593349ebc62d28c07706d3f2b58a0caacd4"

V5671_SOURCE = HERE / "derive_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
V5671_TEST = HERE / "test_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
V5671_SOURCE_SHA256 = "afe410507da533dfff9037b5bd730d90d5931f82aaeb8d4839a48f9a4d18e0c9"
V5671_TEST_SHA256 = "d7988e078fb81f9fa3001eaff2414962d45bfb240b024fbaacf8a9ab126b9694"

BD61D22_COMMIT = "bd61d22cbb989035a4f4b51ea706b54bd154a5ae"
V5673_SOURCE = HERE / "derive_one_omega_topological_so3_direct_free_pointwise_margin_diagonal_v5_6_7_3_gate.py"
V5673_TEST = HERE / "test_one_omega_topological_so3_direct_free_pointwise_margin_diagonal_v5_6_7_3_gate.py"
V5673_SOURCE_SHA256 = "e85d247bfbc766ff59105469626b0191adb6aaeda9799c84dca3fdeca4e3271a"
V5673_TEST_SHA256 = "1d7687ed37c9a10454d221440184080412ede621f8301aa940b1ed76d3c05fdd"

TARGET_MEMBER_ID = "fullT4.L1.K1.sparse-x2-direct-free.dyadic.v1"
TARGET_N = 81
TARGET_K = 1
TARGET_SHELL_RADIUS = 1
TARGET_DIMENSION = 29970
TARGET_NONZERO_COORDINATES = 13
TARGET_F64LE_SHA256 = "d9867b9651b9ca6dec961fe2356f2d2ef5d0b184ad947ef28601a3e988dc246a"

SIGNATURE_MARGIN = Fraction(1, 50)
OMEGA_MINIMUM = Fraction(1, 2)
TIMELIKE_MARGIN = Fraction(1, 5)
CUT_LOCUS_MARGIN = Fraction(1, 1)
Y_AMPLITUDE = Fraction(1, 256)
LOG_OMEGA_AMPLITUDE = Fraction(1, 64)
WEYL_BASE_POSITIVE_LOWER = Fraction(9, 8)
WEYL_RADIAL_UPPER = Fraction(6, 5)

# Exact real values of the binary64 literals in v5.6.7.1.  They are written as
# integer ratios so no scientific decision depends on parsing a decimal float.
REFERENCE_METRIC_DIAGONAL = (
    Fraction(-7385903388887613, 4503599627370496),
    Fraction(658651445502935, 562949953421312),
    Fraction(2949857755927675, 2251799813685248),
    Fraction(1643813863990231, 1125899906842624),
    Fraction(658651445502935, 562949953421312),
)

ANALYTIC_MARGIN_OBLIGATIONS = frozenset(
    {
        "common_gamma_lorentzian_eigen_gap",
        "pulled_bulk_actual_plus_lorentzian_eigen_gap",
        "pulled_bulk_actual_minus_lorentzian_eigen_gap",
        "pulled_bulk_reference_plus_lorentzian_eigen_gap",
        "pulled_bulk_reference_minus_lorentzian_eigen_gap",
        "ghy_spacelike_normal_plus",
        "ghy_spacelike_normal_minus",
        "khronon_timelike",
        "frame_gram_leading_minor_1",
        "frame_gram_leading_minor_2",
        "frame_gram_leading_minor_3",
        "omega_plus",
        "omega_minus",
        "so3_chart_q",
        "so3_chart_r_plus",
        "so3_chart_r_minus",
    }
)

TRUE_DECISION_KEYS = frozenset(
    {
        "v5_6_7_exact_primitives_byte_pinned_pass",
        "v5_6_7_1_direct_free_decoder_byte_pinned_pass",
        "bd61d22_conditional_ledger_byte_pinned_without_oracle_pass",
        "named_full_t4_finite_member_contract_exact_pass",
        "named_full_t4_finite_member_whole_domain_analytic_margins_exact_pass",
        "finite_member_whole_domain_outward_rounded_margin_certificate_pass",
        "adversarial_mutants_all_detected_pass",
    }
)

FALSE_DECISION_KEYS = frozenset(
    {
        "margins_certified_pass",
        "generic_whole_domain_interval_margin_engine_pass",
        "v5_6_7_1_runtime_eventual_acceptance_pass",
        "constructive_quadrature_remainder_certificate_pass",
        "quadrature_pass",
        "integrated_action_pass",
        "infinite_target_member_margin_certificate_pass",
        "continuum_decoder_C1_pass",
        "continuum_decoder_DGamma_continuity_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_N_to_infinity_numerical_certificate_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "P4_full_same_action_pass",
        "B4_pass",
        "B5_pass",
    }
)

V567_REQUIRED_FRAGMENTS = {
    "priority_x2_wavevector": "(0, 0, 1, 0)",
    "real_fourier_modes": "def real_fourier_modes(N: int)",
    "free_layout": "def free_layout(N: int, K: int)",
    "radial_profiles": "def radial_profile_polynomials(K: int)",
    "radial_envelope": "envelope = Poly([0.0, 0.0, 0.0, 64.0]) * Poly([1.0, -1.0]) ** 3",
}

V5671_REQUIRED_FRAGMENTS = {
    "side_radial_signs": 'SIDE_RADIAL_SIGN = {"plus": -1.0, "minus": 1.0}',
    "generated_contract": "def full_t4_decoder_contract(N: int, K: int)",
    "boundary_metric_quadratic": "+ normal_metric * Y_first[mu] * Y_first[nu]",
    "boundary_metric_cross": "cross = adapted_cross[mu] - normal_metric * Y_first[mu]",
    "collar_h0": "value = value + h0 * (trace[channel] - reference[channel])",
    "collar_h1": "value = value + h1 * J1[channel]",
    "collar_bumps": "value = value + bumps[k] * C[k][channel]",
    "pullback_embedding_gradient": "jacobian_rows[4][i] = RhoJet2(Y_first[i])",
    "pullback_side_sign": "jacobian_rows[4][4] = RhoJet2(SIDE_RADIAL_SIGN[side])",
    "pulled_metric": "pulled_metric = _matmul(_matmul(jacobian_transpose, metric, zero), jacobian, zero)",
    "pulled_reference": "pulled_reference = _matmul(_matmul(jacobian_transpose, reference, zero), jacobian, zero)",
}

V5673_REQUIRED_FRAGMENTS = {
    "conditional_scope": "conditional implication only",
    "finite_margin_false": '"finite_member_whole_domain_outward_rounded_margin_certificate_pass": False',
    "runtime_false": '"v5_6_7_1_runtime_eventual_acceptance_pass": False',
    "margin_inventory": "ANALYTIC_MARGIN_OBLIGATIONS = frozenset(",
    "unclosed_gamma": '"Gamma_is_C1_on_an_open_graded_Sobolev_neighborhood": False',
}


class ExactMarginGateError(RuntimeError):
    """Raised when a byte pin, exact contract, or rational proof drifts."""


class RationalInterval:
    """Closed rational interval with exact outward arithmetic."""

    __slots__ = ("lower", "upper")

    def __init__(self, lower: Fraction, upper: Fraction) -> None:
        if lower > upper:
            raise ValueError("interval lower endpoint exceeds upper endpoint")
        self.lower = lower
        self.upper = upper

    def __eq__(self, other: object) -> bool:
        return bool(
            isinstance(other, RationalInterval)
            and self.lower == other.lower
            and self.upper == other.upper
        )

    def __add__(self, other: "RationalInterval") -> "RationalInterval":
        return RationalInterval(self.lower + other.lower, self.upper + other.upper)

    def __neg__(self) -> "RationalInterval":
        return RationalInterval(-self.upper, -self.lower)

    def __sub__(self, other: "RationalInterval") -> "RationalInterval":
        return self + (-other)

    def __mul__(self, other: "RationalInterval") -> "RationalInterval":
        products = (
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        )
        return RationalInterval(min(products), max(products))

    def scale(self, scalar: Fraction) -> "RationalInterval":
        return self * RationalInterval(scalar, scalar)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_sha256(commit: str, path: Path) -> str | None:
    relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{commit}:{relative}"],
            cwd=REPO,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return hashlib.sha256(raw).hexdigest()


def _fraction_json(value: Fraction) -> dict[str, int | str]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "exact": f"{value.numerator}/{value.denominator}",
    }


def _interval_json(value: RationalInterval) -> dict[str, Any]:
    return {
        "lower": _fraction_json(value.lower),
        "upper": _fraction_json(value.upper),
        "closed": True,
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, Fraction):
        return _fraction_json(value)
    if isinstance(value, RationalInterval):
        return _interval_json(value)
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_json_ready(item) for item in value)
    return value


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Mapping):
        return any(_contains_float(key) or _contains_float(item) for key, item in value.items())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_float(item) for item in value)
    return False


def _source_pin_ledger() -> dict[str, Any]:
    records = {
        "v5_6_7_source": (V567_SOURCE, V567_SOURCE_SHA256, V567_REQUIRED_FRAGMENTS),
        "v5_6_7_test": (V567_TEST, V567_TEST_SHA256, {}),
        "v5_6_7_1_source": (V5671_SOURCE, V5671_SOURCE_SHA256, V5671_REQUIRED_FRAGMENTS),
        "v5_6_7_1_test": (V5671_TEST, V5671_TEST_SHA256, {}),
        "bd61d22_source": (V5673_SOURCE, V5673_SOURCE_SHA256, V5673_REQUIRED_FRAGMENTS),
        "bd61d22_test": (V5673_TEST, V5673_TEST_SHA256, {}),
    }
    rows: dict[str, Any] = {}
    for name, (path, expected, fragments) in records.items():
        observed = _sha256(path)
        text = path.read_text(encoding="utf-8")
        fragment_matches = {key: fragment in text for key, fragment in fragments.items()}
        rows[name] = {
            "path": path.name,
            "expected_sha256": expected,
            "observed_sha256": observed,
            "required_fragment_matches": fragment_matches,
            "pass": observed == expected and all(fragment_matches.values()),
        }

    bd_source_blob = _git_blob_sha256(BD61D22_COMMIT, V5673_SOURCE)
    bd_test_blob = _git_blob_sha256(BD61D22_COMMIT, V5673_TEST)
    bd_commit = {
        "commit": BD61D22_COMMIT,
        "source_blob_sha256": bd_source_blob,
        "test_blob_sha256": bd_test_blob,
        "matches_pinned_worktree_bytes": (
            bd_source_blob == V5673_SOURCE_SHA256
            and bd_test_blob == V5673_TEST_SHA256
        ),
        "conclusion_imported_or_consumed": False,
    }
    return {
        "records": rows,
        "bd61d22_commit_binding": bd_commit,
        "v5_6_7_pass": rows["v5_6_7_source"]["pass"] and rows["v5_6_7_test"]["pass"],
        "v5_6_7_1_pass": rows["v5_6_7_1_source"]["pass"] and rows["v5_6_7_1_test"]["pass"],
        "bd61d22_pass": (
            rows["bd61d22_source"]["pass"]
            and rows["bd61d22_test"]["pass"]
            and bd_commit["matches_pinned_worktree_bytes"]
            and bd_commit["conclusion_imported_or_consumed"] is False
        ),
    }


COMMON_BLOCKS = (
    ("common.gamma", (10,)),
    ("common.T", (1,)),
    ("common.log_Omega", (1,)),
    ("common.varphi_E0", (3,)),
    ("common.A_E0", (4, 3)),
    ("Q_frame.q", (3,)),
)
SIDE_BLOCKS = (
    ("Y", (1,)),
    ("metric_free", (5,)),
    ("A_perp", (3,)),
    ("B0_full", (10, 3)),
    ("r_E0", (3,)),
    ("boundary_jet_J1", (64,)),
    ("interior_bump_C", ("K", 64)),
)


def _strict_positive_integer(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def independent_free_layout(N: int, K: int) -> dict[str, Any]:
    """Independent row-major reconstruction of the pinned direct-free layout."""

    N = _strict_positive_integer("N", N)
    K = _strict_positive_integer("K", K)
    blocks: dict[str, Any] = {}
    cursor = 0

    def add(name: str, trailing: Sequence[int | str]) -> None:
        nonlocal cursor
        resolved = tuple(K if item == "K" else int(item) for item in trailing)
        shape = (N,) + resolved
        size = 1
        for item in shape:
            size *= item
        blocks[name] = {"start": cursor, "stop": cursor + size, "shape": list(shape)}
        cursor += size

    for name, shape in COMMON_BLOCKS:
        add(name, shape)
    for side in ("plus", "minus"):
        for name, shape in SIDE_BLOCKS:
            add(f"{side}.{name}", shape)
    return {"blocks": blocks, "free_coordinate_dimension": cursor}


def _load_pinned_v567() -> Any:
    if _sha256(V567_SOURCE) != V567_SOURCE_SHA256:
        raise ExactMarginGateError("v5.6.7 source byte pin drift")
    specification = importlib.util.spec_from_file_location("v567_exact_for_v5675", V567_SOURCE)
    if specification is None or specification.loader is None:
        raise ExactMarginGateError("cannot load pinned v5.6.7 exact primitives")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _row_major_offset(shape: Sequence[int], index: Sequence[int]) -> int:
    if len(shape) != len(index):
        raise ValueError("index rank does not match shape")
    offset = 0
    for extent, coordinate in zip(shape, index):
        if isinstance(coordinate, bool) or not isinstance(coordinate, int) or not 0 <= coordinate < extent:
            raise ValueError("coordinate outside target block")
        offset = offset * extent + coordinate
    return offset


def _flat_index(layout: Mapping[str, Any], block: str, index: Sequence[int]) -> int:
    specification = layout["blocks"][block]
    return int(specification["start"]) + _row_major_offset(specification["shape"], index)


def canonical_member_contract() -> dict[str, Any]:
    return {
        "schema": "full-T4-L1-K1-sparse-direct-free-member.v1",
        "member_id": TARGET_MEMBER_ID,
        "N": TARGET_N,
        "K": TARGET_K,
        "shell_radius": TARGET_SHELL_RADIUS,
        "expected_dimension": TARGET_DIMENSION,
        "expected_nonzero_coordinates": TARGET_NONZERO_COORDINATES,
        "expected_f64le_sha256": TARGET_F64LE_SHA256,
        "sides": ["plus", "minus"],
        "side_radial_signs": {"plus": -1, "minus": 1},
        "Y_mode": {"index": 8, "kind": "sin", "wavevector": [0, 0, 1, 0]},
        "log_Omega_C_mode": {"index": 7, "kind": "cos", "wavevector": [0, 0, 1, 0]},
        "log_Omega_C_radial_index": 0,
        "log_Omega_C_channel": 15,
        "gamma_diagonal": [Fraction(-5, 4), Fraction(9, 8), Fraction(5, 4), Fraction(11, 8)],
        "varphi_E0": [Fraction(3, 8), Fraction(-1, 4), Fraction(1, 4)],
        "normal_metric": Fraction(9, 8),
        "Y_amplitude": Y_AMPLITUDE,
        "log_Omega_C_amplitude": LOG_OMEGA_AMPLITUDE,
    }


def _member_contract_accepts(contract: Mapping[str, Any]) -> bool:
    return dict(contract) == canonical_member_contract()


def member_sparse_assignments(contract: Mapping[str, Any]) -> tuple[dict[int, Fraction], dict[str, Any]]:
    N = contract.get("N")
    K = contract.get("K")
    layout = independent_free_layout(N, K)
    assignments: dict[int, Fraction] = {}

    def assign(block: str, index: Sequence[int], value: Fraction) -> None:
        flat = _flat_index(layout, block, index)
        if flat in assignments:
            raise ValueError("duplicate target coordinate assignment")
        if value:
            assignments[flat] = value

    for packed_index, value in zip((0, 4, 7, 9), contract.get("gamma_diagonal", [])):
        assign("common.gamma", (0, packed_index), value)
    for component, value in enumerate(contract.get("varphi_E0", [])):
        assign("common.varphi_E0", (0, component), value)
    for side in contract.get("sides", []):
        assign(f"{side}.Y", (contract["Y_mode"]["index"], 0), contract["Y_amplitude"])
        assign(f"{side}.metric_free", (0, 4), contract["normal_metric"])
        assign(
            f"{side}.interior_bump_C",
            (
                contract["log_Omega_C_mode"]["index"],
                contract["log_Omega_C_radial_index"],
                contract["log_Omega_C_channel"],
            ),
            contract["log_Omega_C_amplitude"],
        )
    return assignments, layout


def _dyadic_binary64_bits(value: Fraction) -> int:
    """Encode a normal finite dyadic exactly, without a float conversion."""

    if value == 0:
        return 0
    sign = int(value < 0)
    absolute = abs(value)
    denominator = absolute.denominator
    if denominator & (denominator - 1):
        raise ValueError("target coefficient is not dyadic")
    denominator_power = denominator.bit_length() - 1
    numerator = absolute.numerator
    exponent = numerator.bit_length() - 1 - denominator_power
    if not -1022 <= exponent <= 1023:
        raise ValueError("target coefficient is outside normal binary64 range")
    shift = 52 - denominator_power - exponent
    if shift >= 0:
        significand = numerator << shift
    else:
        divisor = 1 << (-shift)
        if numerator % divisor:
            raise ValueError("target coefficient is not exactly representable in binary64")
        significand = numerator // divisor
    if not (1 << 52) <= significand < (1 << 53):
        raise ValueError("binary64 significand normalization failed")
    fraction_bits = significand - (1 << 52)
    return (sign << 63) | ((exponent + 1023) << 52) | fraction_bits


def member_f64le_bytes(contract: Mapping[str, Any] | None = None) -> bytes:
    selected = canonical_member_contract() if contract is None else contract
    assignments, layout = member_sparse_assignments(selected)
    raw = bytearray(int(layout["free_coordinate_dimension"]) * 8)
    for index, value in assignments.items():
        struct.pack_into("<Q", raw, index * 8, _dyadic_binary64_bits(value))
    return bytes(raw)


def _complete_shell_representatives(radius: int) -> set[tuple[int, int, int, int]]:
    radius = _strict_positive_integer("radius", radius)
    representatives: set[tuple[int, int, int, int]] = set()
    values = range(-radius, radius + 1)
    for k0 in values:
        for k1 in values:
            for k2 in values:
                for k3 in values:
                    vector = (k0, k1, k2, k3)
                    if vector == (0, 0, 0, 0):
                        continue
                    if next(item for item in vector if item) > 0:
                        representatives.add(vector)
    return representatives


def _member_ledger(contract: Mapping[str, Any] | None = None) -> dict[str, Any]:
    selected = canonical_member_contract() if contract is None else contract
    try:
        assignments, independent_layout = member_sparse_assignments(selected)
        raw = member_f64le_bytes(selected)
        observed_hash = hashlib.sha256(raw).hexdigest()
        upstream = _load_pinned_v567()
        upstream_layout = upstream.free_layout(selected["N"], selected["K"])
        modes = upstream.real_fourier_modes(selected["N"])
        representatives = _complete_shell_representatives(selected["shell_radius"])
        mode_pairs = {
            tuple(mode["wavevector"]): {modes[i]["kind"] for i, item in enumerate(modes) if tuple(item["wavevector"]) == tuple(mode["wavevector"])}
            for mode in modes[1:]
        }
        full_shell = bool(
            selected["N"] == (2 * selected["shell_radius"] + 1) ** 4
            and len(modes) == selected["N"]
            and set(mode_pairs) == representatives
            and all(kinds == {"cos", "sin"} for kinds in mode_pairs.values())
        )
        layout_match = bool(
            independent_layout["blocks"] == upstream_layout["blocks"]
            and independent_layout["free_coordinate_dimension"]
            == upstream_layout["free_coordinate_dimension"]
        )
        y_mode = selected["Y_mode"]
        c_mode = selected["log_Omega_C_mode"]
        mode_match = bool(
            modes[y_mode["index"]]["kind"] == y_mode["kind"]
            and list(modes[y_mode["index"]]["wavevector"]) == y_mode["wavevector"]
            and modes[c_mode["index"]]["kind"] == c_mode["kind"]
            and list(modes[c_mode["index"]]["wavevector"]) == c_mode["wavevector"]
        )
    except (KeyError, TypeError, ValueError, ExactMarginGateError):
        assignments = {}
        independent_layout = {"blocks": {}, "free_coordinate_dimension": -1}
        observed_hash = None
        full_shell = False
        layout_match = False
        mode_match = False

    accepted = _member_contract_accepts(selected)
    pass_value = bool(
        accepted
        and full_shell
        and layout_match
        and mode_match
        and independent_layout["free_coordinate_dimension"] == TARGET_DIMENSION
        and len(assignments) == TARGET_NONZERO_COORDINATES
        and observed_hash == TARGET_F64LE_SHA256
    )
    return {
        "contract": _json_ready(selected),
        "contract_exact_match": accepted,
        "complete_shell_L1": full_shell,
        "independent_layout_matches_pinned_v5_6_7": layout_match,
        "x2_modes_match_pinned_enumeration": mode_match,
        "free_coordinate_dimension": independent_layout["free_coordinate_dimension"],
        "nonzero_coordinate_count": len(assignments),
        "nonzero_coordinates": [
            {"flat_index": index, "value": _fraction_json(value)}
            for index, value in sorted(assignments.items())
        ],
        "f64le_sha256": observed_hash,
        "pass": pass_value,
    }


def _poly_trim(polynomial: Sequence[Fraction]) -> tuple[Fraction, ...]:
    result = list(polynomial)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def _poly_add(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, ...]:
    size = max(len(left), len(right))
    return _poly_trim(
        tuple(
            (left[index] if index < len(left) else Fraction(0))
            + (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        )
    )


def _poly_scale(polynomial: Sequence[Fraction], scalar: Fraction) -> tuple[Fraction, ...]:
    return _poly_trim(tuple(scalar * coefficient for coefficient in polynomial))


def _poly_multiply(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, ...]:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return _poly_trim(result)


def _poly_power(polynomial: Sequence[Fraction], exponent: int) -> tuple[Fraction, ...]:
    if isinstance(exponent, bool) or not isinstance(exponent, int) or exponent < 0:
        raise ValueError("polynomial exponent must be a non-negative integer")
    result: tuple[Fraction, ...] = (Fraction(1),)
    for _ in range(exponent):
        result = _poly_multiply(result, polynomial)
    return result


def _poly_derivative(polynomial: Sequence[Fraction]) -> tuple[Fraction, ...]:
    if len(polynomial) <= 1:
        return (Fraction(0),)
    return _poly_trim(tuple(index * polynomial[index] for index in range(1, len(polynomial))))


def _poly_evaluate(polynomial: Sequence[Fraction], value: Fraction) -> Fraction:
    result = Fraction(0)
    for coefficient in reversed(polynomial):
        result = result * value + coefficient
    return result


def _radial_envelope_ledger() -> dict[str, Any]:
    rho = (Fraction(0), Fraction(1))
    one_minus_rho = (Fraction(1), Fraction(-1))
    h0 = (
        Fraction(1),
        Fraction(0),
        Fraction(0),
        Fraction(-10),
        Fraction(15),
        Fraction(-6),
    )
    h0_derivative_expected = _poly_scale(
        _poly_multiply(_poly_power(rho, 2), _poly_power(one_minus_rho, 2)),
        Fraction(-30),
    )
    rho_one_minus_rho = _poly_multiply(rho, one_minus_rho)
    quarter_minus_product = _poly_add(
        (Fraction(1, 4),), _poly_scale(rho_one_minus_rho, Fraction(-1))
    )
    centered_square = _poly_power((Fraction(-1, 2), Fraction(1)), 2)
    b0 = _poly_scale(_poly_power(rho_one_minus_rho, 3), Fraction(64))
    pass_value = bool(
        _poly_derivative(h0) == h0_derivative_expected
        and _poly_evaluate(h0, Fraction(0)) == 1
        and _poly_evaluate(h0, Fraction(1)) == 0
        and quarter_minus_product == centered_square
        and _poly_evaluate(b0, Fraction(0)) == 0
        and _poly_evaluate(b0, Fraction(1, 2)) == 1
        and _poly_evaluate(b0, Fraction(1)) == 0
    )
    return {
        "h0_coefficients_ascending": [_fraction_json(item) for item in h0],
        "b0_coefficients_ascending": [_fraction_json(item) for item in b0],
        "h0_derivative_identity": "h0'=-30*rho^2*(1-rho)^2",
        "h0_range": _interval_json(RationalInterval(Fraction(0), Fraction(1))),
        "rho_one_minus_rho_identity": "1/4-rho*(1-rho)=(rho-1/2)^2",
        "b0_identity": "b0=64*[rho*(1-rho)]^3",
        "b0_range": _interval_json(RationalInterval(Fraction(0), Fraction(1))),
        "pass": pass_value,
    }


# Tiny exact multivariate-polynomial engine, used only to verify the pullback
# identity rather than trusting a hand-written simplified formula.
Poly = dict[tuple[int, ...], Fraction]


def _mp_const(value: Fraction, variables: int = 6) -> Poly:
    return {(0,) * variables: value} if value else {}


def _mp_var(index: int, variables: int = 6) -> Poly:
    exponent = [0] * variables
    exponent[index] = 1
    return {tuple(exponent): Fraction(1)}


def _mp_add(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, Fraction(0)) + coefficient
        if result[exponent] == 0:
            del result[exponent]
    return result


def _mp_neg(value: Poly) -> Poly:
    return {exponent: -coefficient for exponent, coefficient in value.items()}


def _mp_sub(left: Poly, right: Poly) -> Poly:
    return _mp_add(left, _mp_neg(right))


def _mp_mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for alpha, a in left.items():
        for beta, b in right.items():
            exponent = tuple(x + y for x, y in zip(alpha, beta))
            result[exponent] = result.get(exponent, Fraction(0)) + a * b
            if result[exponent] == 0:
                del result[exponent]
    return result


def _mp_scale(value: Poly, scalar: Fraction) -> Poly:
    return {exponent: scalar * coefficient for exponent, coefficient in value.items() if scalar * coefficient}


def _mp_matrix_multiply(left: Sequence[Sequence[Poly]], right: Sequence[Sequence[Poly]]) -> list[list[Poly]]:
    result: list[list[Poly]] = []
    for i in range(len(left)):
        row: list[Poly] = []
        for j in range(len(right[0])):
            entry: Poly = {}
            for k in range(len(right)):
                entry = _mp_add(entry, _mp_mul(left[i][k], right[k][j]))
            row.append(entry)
        result.append(row)
    return result


def _mp_transpose(matrix: Sequence[Sequence[Poly]]) -> list[list[Poly]]:
    return [[matrix[i][j] for i in range(len(matrix))] for j in range(len(matrix[0]))]


def _mp_primitive_ledger() -> dict[str, Any]:
    zero_exponent = (0, 0, 0, 0, 0, 0)
    t_exponent = (1, 0, 0, 0, 0, 0)
    y_exponent = (0, 1, 0, 0, 0, 0)
    ty_exponent = (1, 1, 0, 0, 0, 0)
    y2_exponent = (0, 2, 0, 0, 0, 0)
    checks = {
        "const_literal_anchor": _mp_const(Fraction(3, 2))
        == {zero_exponent: Fraction(3, 2)},
        "t_variable_literal_anchor": _mp_var(0) == {t_exponent: Fraction(1)},
        "y_variable_literal_anchor": _mp_var(1) == {y_exponent: Fraction(1)},
        "add_literal_anchor": _mp_add(
            {t_exponent: Fraction(2)},
            {t_exponent: Fraction(-1), y_exponent: Fraction(3)},
        )
        == {t_exponent: Fraction(1), y_exponent: Fraction(3)},
        "neg_literal_anchor": _mp_neg({y_exponent: Fraction(5)})
        == {y_exponent: Fraction(-5)},
        "sub_literal_anchor": _mp_sub(
            {zero_exponent: Fraction(2), t_exponent: Fraction(1)},
            {zero_exponent: Fraction(3), y_exponent: Fraction(4)},
        )
        == {
            zero_exponent: Fraction(-1),
            t_exponent: Fraction(1),
            y_exponent: Fraction(-4),
        },
        "mul_literal_anchor": _mp_mul(
            {t_exponent: Fraction(2), y_exponent: Fraction(-1)},
            {y_exponent: Fraction(3)},
        )
        == {ty_exponent: Fraction(6), y2_exponent: Fraction(-3)},
        "scale_literal_anchor": _mp_scale(
            {t_exponent: Fraction(2), y_exponent: Fraction(-3)}, Fraction(-2)
        )
        == {t_exponent: Fraction(-4), y_exponent: Fraction(6)},
    }
    return {"checks": checks, "pass": all(checks.values())}


def _mp_polynomial_payload(value: Poly) -> list[dict[str, Any]]:
    payload = []
    for exponent, coefficient in sorted(value.items()):
        if len(exponent) != 6 or any(exponent[index] for index in range(2, 6)):
            raise ExactMarginGateError("pullback polynomial escaped the t,y ring")
        if not isinstance(coefficient, Fraction) or coefficient == 0:
            raise ExactMarginGateError("noncanonical pullback polynomial coefficient")
        payload.append(
            {
                "powers_t_y": [exponent[0], exponent[1]],
                "coefficient": _fraction_json(coefficient),
            }
        )
    return payload


def _mp_matrix_payload(matrix: Sequence[Sequence[Poly]]) -> list[list[Any]]:
    if len(matrix) != 5 or any(len(row) != 5 for row in matrix):
        raise ExactMarginGateError("pullback polynomial matrix must be 5x5")
    return [[_mp_polynomial_payload(entry) for entry in row] for row in matrix]


def _mp_matrix_payload_sha256(matrix: Sequence[Sequence[Poly]]) -> str:
    encoded = json.dumps(
        _mp_matrix_payload(matrix),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mp_matrix_stats(matrix: Sequence[Sequence[Poly]]) -> dict[str, Any]:
    support = {
        (exponent[0], exponent[1])
        for row in matrix
        for entry in row
        for exponent in entry
    }
    return {
        "nonzero_polynomial_entries": sum(
            bool(entry) for row in matrix for entry in row
        ),
        "monomial_support_t_y": [list(exponent) for exponent in sorted(support)],
        "maximum_total_degree": max((sum(exponent) for exponent in support), default=-1),
    }


def _pullback_identity_ledger() -> dict[str, Any]:
    # Variable order is t=h0, y=d_2Y.  The named member and reference
    # coefficients are exact rationals.  The independently expanded expected
    # matrices below deliberately do not reuse base_x2 or ambient entries.
    primitives = _mp_primitive_ledger()
    t, y = (_mp_var(index) for index in range(2))
    one = _mp_const(Fraction(1))
    zero = _mp_const(Fraction(0))
    one_minus_t = _mp_sub(one, t)
    y_squared = _mp_mul(y, y)
    member = canonical_member_contract()
    gamma_values = tuple(member["gamma_diagonal"])
    normal_value = member["normal_metric"]
    reference_values = REFERENCE_METRIC_DIAGONAL
    gamma = tuple(_mp_const(value) for value in gamma_values)
    normal = _mp_const(normal_value)
    reference_diagonal = tuple(_mp_const(value) for value in reference_values)

    ambient = [[zero for _ in range(5)] for _ in range(5)]
    for index in range(4):
        ambient[index][index] = _mp_add(
            _mp_mul(one_minus_t, reference_diagonal[index]),
            _mp_mul(t, gamma[index]),
        )
    base_x2 = _mp_add(
        _mp_mul(one_minus_t, reference_diagonal[2]),
        _mp_mul(t, gamma[2]),
    )
    ambient[2][2] = _mp_add(base_x2, _mp_mul(_mp_mul(t, normal), y_squared))
    ambient[2][4] = ambient[4][2] = _mp_neg(_mp_mul(_mp_mul(t, normal), y))
    ambient[4][4] = _mp_add(
        _mp_mul(one_minus_t, reference_diagonal[4]),
        _mp_mul(t, normal),
    )

    reference_ambient = [[zero for _ in range(5)] for _ in range(5)]
    for index in range(5):
        reference_ambient[index][index] = reference_diagonal[index]

    side_rows: dict[str, Any] = {}
    all_match = True
    for side, sign in (("plus", -1), ("minus", 1)):
        J = [[zero for _ in range(5)] for _ in range(5)]
        for index in range(4):
            J[index][index] = one
        J[4][2] = y
        J[4][4] = _mp_const(Fraction(sign))
        pulled = _mp_matrix_multiply(_mp_matrix_multiply(_mp_transpose(J), ambient), J)
        expected = [[zero for _ in range(5)] for _ in range(5)]
        for index in (0, 1, 3):
            expected[index][index] = _mp_add(
                _mp_mul(_mp_sub(one, t), _mp_const(reference_values[index])),
                _mp_mul(t, _mp_const(gamma_values[index])),
            )
        expected[2][2] = _mp_add(
            _mp_add(
                _mp_mul(_mp_sub(one, t), _mp_const(reference_values[2])),
                _mp_mul(t, _mp_const(gamma_values[2])),
            ),
            _mp_mul(
                _mp_mul(_mp_sub(one, t), _mp_const(reference_values[4])),
                _mp_mul(y, y),
            ),
        )
        expected[2][4] = expected[4][2] = _mp_scale(
            _mp_mul(
                _mp_mul(_mp_sub(one, t), _mp_const(reference_values[4])), y
            ),
            Fraction(sign),
        )
        expected[4][4] = _mp_add(
            _mp_mul(_mp_sub(one, t), _mp_const(reference_values[4])),
            _mp_mul(t, _mp_const(normal_value)),
        )

        pulled_reference = _mp_matrix_multiply(
            _mp_matrix_multiply(_mp_transpose(J), reference_ambient), J
        )
        expected_reference = [[zero for _ in range(5)] for _ in range(5)]
        for index in (0, 1, 3):
            expected_reference[index][index] = _mp_const(reference_values[index])
        expected_reference[2][2] = _mp_add(
            _mp_const(reference_values[2]),
            _mp_mul(_mp_const(reference_values[4]), _mp_mul(y, y)),
        )
        expected_reference[2][4] = expected_reference[4][2] = _mp_scale(
            _mp_mul(_mp_const(reference_values[4]), y), Fraction(sign)
        )
        expected_reference[4][4] = _mp_const(reference_values[4])

        actual_entry_matches = {
            f"{row},{column}": pulled[row][column] == expected[row][column]
            for row in range(5)
            for column in range(5)
        }
        reference_entry_matches = {
            f"{row},{column}": (
                pulled_reference[row][column] == expected_reference[row][column]
            )
            for row in range(5)
            for column in range(5)
        }
        actual_match = all(actual_entry_matches.values())
        reference_match = all(reference_entry_matches.values())
        all_match = all_match and actual_match and reference_match
        side_rows[side] = {
            "radial_sign": sign,
            "actual_symbolic_identity_match": actual_match,
            "reference_symbolic_identity_match": reference_match,
            "actual_full_matrix_entry_matches": actual_entry_matches,
            "reference_full_matrix_entry_matches": reference_entry_matches,
            "actual_matrix_polynomial_payload_sha256": _mp_matrix_payload_sha256(
                pulled
            ),
            "reference_matrix_polynomial_payload_sha256": _mp_matrix_payload_sha256(
                pulled_reference
            ),
            "actual_matrix_polynomial_stats": _mp_matrix_stats(pulled),
            "reference_matrix_polynomial_stats": _mp_matrix_stats(pulled_reference),
            "actual_cross_at_rho_one_x2_zero": _fraction_json(
                Fraction(sign) * REFERENCE_METRIC_DIAGONAL[4] * Y_AMPLITUDE
            ),
            "reference_cross_at_x2_zero": _fraction_json(
                Fraction(sign) * REFERENCE_METRIC_DIAGONAL[4] * Y_AMPLITUDE
            ),
        }
    plus_actual_cross = -REFERENCE_METRIC_DIAGONAL[4] * Y_AMPLITUDE
    minus_actual_cross = REFERENCE_METRIC_DIAGONAL[4] * Y_AMPLITUDE
    return {
        "variables": ["h0", "d2Y"],
        "polynomial_ring_primitives": primitives,
        "independent_full_matrix_oracle": (
            "all 25 entries of each 5x5 actual/reference pulled metric; "
            "expected expansions do not reuse base_x2 or ambient entries"
        ),
        "full_matrix_shape": [5, 5],
        "sides": side_rows,
        "plus_pullback_nontrivial": plus_actual_cross != 0,
        "opposite_side_cross_signs": plus_actual_cross == -minus_actual_cross,
        "pass": bool(
            primitives["pass"]
            and all_match
            and plus_actual_cross != 0
            and plus_actual_cross == -minus_actual_cross
        ),
    }


def canonical_margin_contract() -> dict[str, Any]:
    return {
        "schema": "named-member-exact-analytic-margin-contract.v1",
        "actual_metric_source": "pulled_X64",
        "reference_metric_source": "pulled_reference_metric15",
        "actual_metric_sides": ["plus", "minus"],
        "reference_metric_sides": ["plus", "minus"],
        "ghy_normal_sides": ["plus", "minus"],
        "gram_leading_minor_orders": [1, 2, 3],
        "time_gradient_includes_dx0": True,
        "omega_representation": "Omega=exp(log_Omega)",
        "chart_fields": ["q", "r_plus", "r_minus"],
        "rounding_direction": "exact-rational-outward",
        "analytic_obligation_ids": sorted(ANALYTIC_MARGIN_OBLIGATIONS),
    }


def _margin_contract_accepts(contract: Mapping[str, Any]) -> bool:
    return dict(contract) == canonical_margin_contract()


def _reference_bounds_ledger(
    reference_metric_diagonal: Sequence[Fraction] | None = None,
    *,
    positive_lower: Fraction = WEYL_BASE_POSITIVE_LOWER,
    radial_upper: Fraction = WEYL_RADIAL_UPPER,
) -> dict[str, Any]:
    diagonal = (
        REFERENCE_METRIC_DIAGONAL
        if reference_metric_diagonal is None
        else tuple(reference_metric_diagonal)
    )
    exact_fraction_inputs = bool(
        len(diagonal) == 5
        and all(isinstance(value, Fraction) for value in diagonal)
        and isinstance(positive_lower, Fraction)
        and isinstance(radial_upper, Fraction)
    )
    if not exact_fraction_inputs:
        return {
            "binary64_literal_exact_ratios": [],
            "positive_lower": None,
            "radial_upper": None,
            "time_absolute_lower": None,
            "checks": {"exact_fraction_inputs": False},
            "pass": False,
        }
    time_abs_lower = Fraction(5, 4)
    checks = {
        "exact_fraction_inputs": exact_fraction_inputs,
        "time_is_negative": diagonal[0] < 0,
        "time_absolute_lower": abs(diagonal[0]) > time_abs_lower,
        "all_spatial_positive": all(value > 0 for value in diagonal[1:]),
        "all_spatial_above_base_lower": all(
            value > positive_lower for value in diagonal[1:]
        ),
        "radial_below_rational_upper": diagonal[4] < radial_upper,
    }
    return {
        "binary64_literal_exact_ratios": [_fraction_json(item) for item in diagonal],
        "positive_lower": _fraction_json(positive_lower),
        "radial_upper": _fraction_json(radial_upper),
        "time_absolute_lower": _fraction_json(time_abs_lower),
        "checks": checks,
        "pass": all(checks.values()),
    }


def _margin_ledger(
    margin_contract: Mapping[str, Any] | None = None,
    member_contract: Mapping[str, Any] | None = None,
    *,
    reference_metric_diagonal: Sequence[Fraction] | None = None,
    weyl_base_positive_lower: Fraction = WEYL_BASE_POSITIVE_LOWER,
    weyl_radial_upper: Fraction = WEYL_RADIAL_UPPER,
    chart_norm_upper_bounds: Mapping[str, Fraction] | None = None,
) -> dict[str, Any]:
    contract = canonical_margin_contract() if margin_contract is None else margin_contract
    member = canonical_member_contract() if member_contract is None else member_contract
    radial = _radial_envelope_ledger()
    pullback = _pullback_identity_ledger()
    reference = _reference_bounds_ledger(
        reference_metric_diagonal,
        positive_lower=weyl_base_positive_lower,
        radial_upper=weyl_radial_upper,
    )

    h0_interval = RationalInterval(Fraction(0), Fraction(1))
    b0_interval = RationalInterval(Fraction(0), Fraction(1))
    cosine_interval = RationalInterval(Fraction(-1), Fraction(1))
    y_interval = cosine_interval.scale(member.get("Y_amplitude", Fraction(0)))
    log_omega_interval = b0_interval * cosine_interval.scale(
        member.get("log_Omega_C_amplitude", Fraction(0))
    )

    reference_diagonal = (
        REFERENCE_METRIC_DIAGONAL
        if reference_metric_diagonal is None
        else tuple(reference_metric_diagonal)
    )
    gamma_diagonal = tuple(member.get("gamma_diagonal", ()))
    normal_metric = member.get("normal_metric", Fraction(0))
    y_amplitude = member.get("Y_amplitude", Fraction(0))
    log_omega_amplitude = member.get("log_Omega_C_amplitude", Fraction(0))
    perturbation_upper = weyl_radial_upper * (
        2 * y_amplitude + y_amplitude * y_amplitude
    )
    base_positive_lower = weyl_base_positive_lower
    pulled_positive_lower = base_positive_lower - perturbation_upper
    common_min_abs_eigenvalue_lower = min(
        abs(gamma_diagonal[0]), *gamma_diagonal[1:]
    )
    pulled_time_abs_lower = min(
        abs(gamma_diagonal[0]), abs(reference_diagonal[0])
    )
    pulled_min_abs_eigenvalue_lower = min(
        pulled_time_abs_lower, pulled_positive_lower
    )
    common_signature_slack = common_min_abs_eigenvalue_lower - SIGNATURE_MARGIN
    pulled_signature_slack = pulled_min_abs_eigenvalue_lower - SIGNATURE_MARGIN
    member_base_bounds_valid = bool(
        gamma_diagonal[0] < 0
        and all(value >= base_positive_lower for value in gamma_diagonal[1:])
        and normal_metric >= base_positive_lower
    )
    metric_enclosure_valid = bool(
        member_base_bounds_valid
        and reference["pass"]
        and reference_diagonal[0] < 0
        and common_signature_slack > 0
        and pulled_signature_slack > 0
    )

    ghy_normal = Fraction(1, 1) / normal_metric
    boundary_pullback_diagonal = bool(
        pullback["pass"]
        and radial["pass"]
        and normal_metric > 0
        and _poly_evaluate(
            tuple(
                Fraction(value["numerator"], value["denominator"])
                for value in radial["h0_coefficients_ascending"]
            ),
            Fraction(0),
        )
        == 1
    )
    timelike_norm = Fraction(1, 1) / gamma_diagonal[0]
    timelike_slack = -timelike_norm - TIMELIKE_MARGIN
    gram_minors = (
        gamma_diagonal[1],
        gamma_diagonal[1] * gamma_diagonal[2],
        gamma_diagonal[1] * gamma_diagonal[2] * gamma_diagonal[3],
    )
    omega_lower = Fraction(1) - log_omega_amplitude
    omega_slack = omega_lower - OMEGA_MINIMUM
    selected_chart_norms = (
        {"q": Fraction(0), "r_plus": Fraction(0), "r_minus": Fraction(0)}
        if chart_norm_upper_bounds is None
        else dict(chart_norm_upper_bounds)
    )
    chart_inputs_exact = bool(
        set(selected_chart_norms) == {"q", "r_plus", "r_minus"}
        and all(
            isinstance(value, Fraction) and value >= 0
            for value in selected_chart_norms.values()
        )
    )
    chart_clearances = {
        name: Fraction(2) - selected_chart_norms[name]
        for name in ("q", "r_plus", "r_minus")
    }

    obligation_results = {
        "common_gamma_lorentzian_eigen_gap": member_base_bounds_valid
        and common_signature_slack > 0,
        "pulled_bulk_actual_plus_lorentzian_eigen_gap": metric_enclosure_valid,
        "pulled_bulk_actual_minus_lorentzian_eigen_gap": metric_enclosure_valid,
        "pulled_bulk_reference_plus_lorentzian_eigen_gap": metric_enclosure_valid,
        "pulled_bulk_reference_minus_lorentzian_eigen_gap": metric_enclosure_valid,
        "ghy_spacelike_normal_plus": boundary_pullback_diagonal and ghy_normal > 0,
        "ghy_spacelike_normal_minus": boundary_pullback_diagonal and ghy_normal > 0,
        "khronon_timelike": gamma_diagonal[0] < 0 and timelike_slack > 0,
        "frame_gram_leading_minor_1": gram_minors[0] > 0,
        "frame_gram_leading_minor_2": gram_minors[1] > 0,
        "frame_gram_leading_minor_3": gram_minors[2] > 0,
        "omega_plus": omega_slack > 0,
        "omega_minus": omega_slack > 0,
        "so3_chart_q": chart_inputs_exact and chart_clearances["q"] > 0,
        "so3_chart_r_plus": chart_inputs_exact
        and chart_clearances["r_plus"] > 0,
        "so3_chart_r_minus": chart_inputs_exact
        and chart_clearances["r_minus"] > 0,
    }

    contract_match = _margin_contract_accepts(contract)
    member_match = _member_contract_accepts(member)
    pass_value = bool(
        contract_match
        and member_match
        and radial["pass"]
        and pullback["pass"]
        and reference["pass"]
        and chart_inputs_exact
        and y_interval == RationalInterval(-Y_AMPLITUDE, Y_AMPLITUDE)
        and log_omega_interval
        == RationalInterval(-LOG_OMEGA_AMPLITUDE, LOG_OMEGA_AMPLITUDE)
        and set(obligation_results) == ANALYTIC_MARGIN_OBLIGATIONS
        and all(obligation_results.values())
    )
    return {
        "contract": _json_ready(contract),
        "contract_exact_match": contract_match,
        "member_contract_exact_match": member_match,
        "arithmetic": {
            "backend": "fractions.Fraction and closed RationalInterval",
            "outward_property": "all endpoints are exact rationals; no rounding occurs in a scientific comparison",
            "float_or_decimal_consumed_by_decisions": False,
        },
        "domain": {
            "tangential": "all T4; only sin(x2), cos(x2) are active and each lies in [-1,1]",
            "radial": "all rho in [0,1]",
            "h0": _interval_json(h0_interval),
            "b0": _interval_json(b0_interval),
            "d2Y": _interval_json(y_interval),
            "log_Omega": _interval_json(log_omega_interval),
        },
        "radial_envelopes": radial,
        "reference_metric": reference,
        "pullback_identity": pullback,
        "metric_certificate": {
            "argument": (
                "time is uncoupled and negative; the four-dimensional positive block is a diagonal convex base "
                "plus E, with ||E||2<=||E||entrywise<=r(2|d2Y|+|d2Y|^2); Weyl applies"
            ),
            "perturbation_upper": _fraction_json(perturbation_upper),
            "base_positive_eigenvalue_lower": _fraction_json(base_positive_lower),
            "member_base_bounds_valid": member_base_bounds_valid,
            "reference_bounds_valid": bool(reference["pass"]),
            "radial_upper_to_base_lower_ratio": _fraction_json(
                weyl_radial_upper / base_positive_lower
            ),
            "common_min_abs_eigenvalue_lower": _fraction_json(
                common_min_abs_eigenvalue_lower
            ),
            "pulled_time_abs_eigenvalue_lower": _fraction_json(
                pulled_time_abs_lower
            ),
            "actual_and_reference_min_abs_eigenvalue_lower": _fraction_json(
                pulled_min_abs_eigenvalue_lower
            ),
            "signature_threshold": _fraction_json(SIGNATURE_MARGIN),
            "strict_slack_lower": _fraction_json(pulled_signature_slack),
            "exactly_one_negative_eigenvalue": metric_enclosure_valid,
            "both_actual_sides": ["plus", "minus"],
            "both_pulled_reference_sides": ["plus", "minus"],
        },
        "ghy_normal": {
            "boundary_metric_is_diag_gamma_9_over_8_after_exact_pullback": (
                boundary_pullback_diagonal and normal_metric == Fraction(9, 8)
            ),
            "inverse_rho_rho": _fraction_json(ghy_normal),
            "sides": ["plus", "minus"],
        },
        "khronon": {
            "d_tau": [1, 0, 0, 0],
            "gamma_inverse_contraction": _fraction_json(timelike_norm),
            "required_negative_clearance": _fraction_json(TIMELIKE_MARGIN),
            "strict_slack": _fraction_json(timelike_slack),
        },
        "frame_gram": {
            "pre_normalization_leading_minors": [_fraction_json(item) for item in gram_minors],
            "all_strictly_positive": all(item > 0 for item in gram_minors),
        },
        "Omega": {
            "inequality": "exp(-x)>=1-x for x>=0",
            "lower": _fraction_json(omega_lower),
            "required_minimum": _fraction_json(OMEGA_MINIMUM),
            "strict_slack": _fraction_json(omega_slack),
            "sides": ["plus", "minus"],
        },
        "SO3_charts": {
            "q_norm": _fraction_json(selected_chart_norms["q"]),
            "r_plus_norm": _fraction_json(selected_chart_norms["r_plus"]),
            "r_minus_norm": _fraction_json(selected_chart_norms["r_minus"]),
            "exact_fraction_norm_upper_bounds": chart_inputs_exact,
            "strict_rational_fact": "pi>3",
            "q_pi_minus_norm_minus_one_strictly_greater_than": _fraction_json(
                chart_clearances["q"]
            ),
            "r_plus_pi_minus_norm_minus_one_strictly_greater_than": _fraction_json(
                chart_clearances["r_plus"]
            ),
            "r_minus_pi_minus_norm_minus_one_strictly_greater_than": _fraction_json(
                chart_clearances["r_minus"]
            ),
            "each_pi_minus_norm_minus_one_strictly_greater_than": _fraction_json(
                min(chart_clearances.values())
            ),
        },
        "obligation_results": obligation_results,
        "pass": pass_value,
    }


def canonical_scope_contract() -> dict[str, bool]:
    return {key: False for key in sorted(FALSE_DECISION_KEYS)}


def _scope_contract_accepts(contract: Mapping[str, Any]) -> bool:
    return dict(contract) == canonical_scope_contract()


def _record_fraction(value: Mapping[str, Any]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _metamorphic_oracle_ledger() -> dict[str, Any]:
    weyl_member = copy.deepcopy(canonical_member_contract())
    weyl_member["Y_amplitude"] = Fraction(1, 512)
    radial_upper = Fraction(5, 4)
    base_lower = Fraction(1)
    weyl = _margin_ledger(
        member_contract=weyl_member,
        weyl_radial_upper=radial_upper,
        weyl_base_positive_lower=base_lower,
    )["metric_certificate"]
    expected_perturbation = radial_upper * (
        2 * weyl_member["Y_amplitude"] + weyl_member["Y_amplitude"] ** 2
    )
    expected_minimum = min(Fraction(5, 4), base_lower - expected_perturbation)

    leaf_member = copy.deepcopy(canonical_member_contract())
    leaf_member["normal_metric"] = Fraction(5, 4)
    leaf_member["gamma_diagonal"] = [
        Fraction(-3, 2),
        Fraction(3, 2),
        Fraction(7, 4),
        Fraction(2),
    ]
    leaf_member["log_Omega_C_amplitude"] = Fraction(1, 32)
    chart_norms = {
        "q": Fraction(1, 2),
        "r_plus": Fraction(1, 3),
        "r_minus": Fraction(1, 4),
    }
    leaves = _margin_ledger(
        member_contract=leaf_member,
        chart_norm_upper_bounds=chart_norms,
    )
    charts = leaves["SO3_charts"]
    checks = {
        "noncanonical_Y_and_Weyl_radial_base_recompute": (
            _record_fraction(weyl["perturbation_upper"]) == expected_perturbation
            and _record_fraction(weyl["base_positive_eigenvalue_lower"])
            == base_lower
            and _record_fraction(
                weyl["actual_and_reference_min_abs_eigenvalue_lower"]
            )
            == expected_minimum
        ),
        "GHY_inverse_recomputes": (
            _record_fraction(leaves["ghy_normal"]["inverse_rho_rho"])
            == Fraction(4, 5)
        ),
        "khronon_inverse_and_slack_recompute": (
            _record_fraction(leaves["khronon"]["gamma_inverse_contraction"])
            == Fraction(-2, 3)
            and _record_fraction(leaves["khronon"]["strict_slack"])
            == Fraction(7, 15)
        ),
        "three_Gram_minors_recompute": (
            tuple(
                _record_fraction(value)
                for value in leaves["frame_gram"][
                    "pre_normalization_leading_minors"
                ]
            )
            == (Fraction(3, 2), Fraction(21, 8), Fraction(21, 4))
        ),
        "Omega_lower_and_slack_recompute": (
            _record_fraction(leaves["Omega"]["lower"]) == Fraction(31, 32)
            and _record_fraction(leaves["Omega"]["strict_slack"]
            ) == Fraction(15, 32)
        ),
        "three_chart_leaves_recompute_separately": (
            _record_fraction(
                charts["q_pi_minus_norm_minus_one_strictly_greater_than"]
            )
            == Fraction(3, 2)
            and _record_fraction(
                charts["r_plus_pi_minus_norm_minus_one_strictly_greater_than"]
            )
            == Fraction(5, 3)
            and _record_fraction(
                charts["r_minus_pi_minus_norm_minus_one_strictly_greater_than"]
            )
            == Fraction(7, 4)
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def _mutant_campaign() -> dict[str, Any]:
    member_mutants: dict[str, dict[str, Any]] = {}

    n80 = copy.deepcopy(canonical_member_contract())
    n80["N"] = 80
    member_mutants["N_81_to_80_not_a_complete_shell"] = n80

    theta = copy.deepcopy(canonical_member_contract())
    theta["Y_mode"] = {"index": 2, "kind": "sin", "wavevector": [1, 1, 0, 0]}
    theta["log_Omega_C_mode"] = {
        "index": 1,
        "kind": "cos",
        "wavevector": [1, 1, 0, 0],
    }
    member_mutants["replace_new_x2_direction_by_legacy_theta"] = theta

    wrong_channel = copy.deepcopy(canonical_member_contract())
    wrong_channel["log_Omega_C_channel"] = 14
    member_mutants["move_C_from_log_Omega_channel_15_to_metric_channel_14"] = wrong_channel

    missing_side = copy.deepcopy(canonical_member_contract())
    missing_side["sides"] = ["plus"]
    member_mutants["omit_minus_side_member_data"] = missing_side

    wrong_sign = copy.deepcopy(canonical_member_contract())
    wrong_sign["side_radial_signs"] = {"plus": 1, "minus": 1}
    member_mutants["flip_plus_pullback_radial_sign"] = wrong_sign

    zero_y = copy.deepcopy(canonical_member_contract())
    zero_y["Y_amplitude"] = Fraction(0)
    zero_y["expected_nonzero_coordinates"] = 11
    member_mutants["erase_nontrivial_pullback_by_zeroing_Y"] = zero_y

    member_detected = {
        name: _member_ledger(mutant)["pass"] is False
        for name, mutant in member_mutants.items()
    }

    margin_mutants: dict[str, dict[str, Any]] = {}
    no_reference = copy.deepcopy(canonical_margin_contract())
    no_reference["reference_metric_sides"] = ["plus"]
    margin_mutants["omit_pulled_reference_minus"] = no_reference

    actual_ambient = copy.deepcopy(canonical_margin_contract())
    actual_ambient["actual_metric_source"] = "ambient_X64"
    margin_mutants["replace_actual_pulled_metric_by_ambient_metric"] = actual_ambient

    reference_ambient = copy.deepcopy(canonical_margin_contract())
    reference_ambient["reference_metric_source"] = "ambient_reference_metric15"
    margin_mutants["replace_pulled_reference_by_ambient_reference"] = reference_ambient

    no_normal = copy.deepcopy(canonical_margin_contract())
    no_normal["ghy_normal_sides"] = ["plus"]
    margin_mutants["omit_minus_GHY_normal"] = no_normal

    no_gram = copy.deepcopy(canonical_margin_contract())
    no_gram["gram_leading_minor_orders"] = [1, 3]
    margin_mutants["omit_frame_Gram_leading_minor_2"] = no_gram

    no_dx0 = copy.deepcopy(canonical_margin_contract())
    no_dx0["time_gradient_includes_dx0"] = False
    margin_mutants["omit_dx0_from_d_tau"] = no_dx0

    wrong_omega = copy.deepcopy(canonical_margin_contract())
    wrong_omega["omega_representation"] = "Omega=log_Omega"
    margin_mutants["treat_log_Omega_as_Omega"] = wrong_omega

    merged_charts = copy.deepcopy(canonical_margin_contract())
    merged_charts["chart_fields"] = ["product_exp_q_exp_r"]
    margin_mutants["replace_three_separate_charts_by_product_chart"] = merged_charts

    inward = copy.deepcopy(canonical_margin_contract())
    inward["rounding_direction"] = "inward"
    margin_mutants["replace_exact_outward_enclosure_by_inward_rounding"] = inward

    no_obligation = copy.deepcopy(canonical_margin_contract())
    no_obligation["analytic_obligation_ids"] = no_obligation["analytic_obligation_ids"][:-1]
    margin_mutants["drop_one_analytic_margin_obligation"] = no_obligation

    margin_detected = {
        name: _margin_ledger(mutant)["pass"] is False
        for name, mutant in margin_mutants.items()
    }
    margin_detected["swap_Weyl_radial_upper_and_base_positive_lower"] = (
        _margin_ledger(
            weyl_base_positive_lower=WEYL_RADIAL_UPPER,
            weyl_radial_upper=WEYL_BASE_POSITIVE_LOWER,
        )["pass"]
        is False
    )

    promotion_detected: dict[str, bool] = {}
    for key in sorted(FALSE_DECISION_KEYS):
        promoted = canonical_scope_contract()
        promoted[key] = True
        promotion_detected[f"forbid_promotion__{key}"] = not _scope_contract_accepts(promoted)

    metamorphic = _metamorphic_oracle_ledger()
    detected = {
        **member_detected,
        **margin_detected,
        **promotion_detected,
        **metamorphic["checks"],
    }
    return {
        "member_mutants": member_detected,
        "margin_mutants": margin_detected,
        "promotion_mutants": promotion_detected,
        "metamorphic_oracles": metamorphic,
        "mutant_detected": detected,
        "all_mutants_effective": all(detected.values()),
        "pass": all(detected.values()),
    }


def build_report() -> dict[str, Any]:
    pins = _source_pin_ledger()
    member = _member_ledger()
    margins = _margin_ledger()
    mutants = _mutant_campaign()
    scope_contract = canonical_scope_contract()

    decision: dict[str, bool] = {
        "v5_6_7_exact_primitives_byte_pinned_pass": bool(pins["v5_6_7_pass"]),
        "v5_6_7_1_direct_free_decoder_byte_pinned_pass": bool(pins["v5_6_7_1_pass"]),
        "bd61d22_conditional_ledger_byte_pinned_without_oracle_pass": bool(
            pins["bd61d22_pass"]
        ),
        "named_full_t4_finite_member_contract_exact_pass": bool(member["pass"]),
        "named_full_t4_finite_member_whole_domain_analytic_margins_exact_pass": bool(
            margins["pass"]
        ),
        "finite_member_whole_domain_outward_rounded_margin_certificate_pass": bool(
            member["pass"] and margins["pass"]
        ),
        "adversarial_mutants_all_detected_pass": bool(mutants["pass"]),
        **scope_contract,
    }
    observed_true = frozenset(key for key, value in decision.items() if value)
    observed_false = frozenset(key for key, value in decision.items() if not value)
    if observed_true != TRUE_DECISION_KEYS or observed_false != FALSE_DECISION_KEYS:
        raise ExactMarginGateError("decision allowlist drift or exact finite-member proof failed")

    report = {
        "schema": SCHEMA,
        "claim": (
            "One named N=81,K=1 complete-shell direct-free member has exact rational "
            "whole-domain analytic margins on T4 x [0,1]"
        ),
        "source_pins": pins,
        "member": member,
        "whole_domain_exact_margin_certificate": margins,
        "effective_mutants": mutants,
        "decision": decision,
        "scope": {
            "named_finite_member_only": True,
            "generic_interval_engine_claimed": False,
            "float64_runtime_acceptance_claimed": False,
            "tangent_or_JVP_runtime_claimed": False,
            "quadrature_or_action_integration_claimed": False,
            "infinite_target_or_eventual_index_claimed": False,
            "uniform_bridge_or_C1_N1_promotion_claimed": False,
            "bd61d22_conclusion_used_as_oracle": False,
            "meaning": (
                "Unlike bd61d22, this receipt supplies one explicit member and proves its margins. "
                "Because the member is finite, its later complete-shell/radial projections stabilize; "
                "this does not discharge decoder C1/DGamma continuity or any infinite-target bridge."
            ),
        },
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__)),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST) if TEST.exists() else None,
            },
            "python": platform.python_version(),
        },
    }
    if _contains_float(report):
        raise ExactMarginGateError("a float leaked into the exact scientific report")
    return report


def main() -> None:
    report = build_report()
    if not report["decision"][
        "finite_member_whole_domain_outward_rounded_margin_certificate_pass"
    ]:
        raise ExactMarginGateError("named finite-member exact margin certificate failed")
    OUTPUT.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"member={TARGET_MEMBER_ID} N={TARGET_N} K={TARGET_K} "
        f"dimension={TARGET_DIMENSION} nonzero={TARGET_NONZERO_COORDINATES} "
        "exact_whole_domain=True promotions=False"
    )


if __name__ == "__main__":
    main()
