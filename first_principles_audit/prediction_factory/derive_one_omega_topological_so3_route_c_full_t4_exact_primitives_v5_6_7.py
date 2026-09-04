#!/usr/bin/env python3
"""Full-T^4, arbitrary-N exact primitives for a stencil-free Route C (v5.6.7, unit M1+M2).

Lease (~/.agent-bridge, 2026-09-04): this module and its test only; no receipt,
no artifact, no roadmap.  It provides, with no finite difference anywhere:

  M1  the nested real Fourier basis of T^4 for arbitrary N, transcribed from the
      contract and compared with the byte-pinned declared enumeration
      (v5.6.6.8 `declared_wavevectors`) for N = 1..11 and, beyond the priority
      list, at N = 12, 13, 27, 81, 82, 83, 200 (sixth vector, first radius-2
      vector), with nestedness, canonical +-k representative and labels /
      parity against `declared_collocation_matrix`; with the C2 bundle labels
      for N = 1, 2, 3; the general free-data layout (N, K) in the contract block
      order, compared with the bundle contracts by start/stop/shape and by the
      canonical sha of the blocks;
  M2  spectral evaluation of value, first, second (and third, needed for
      the pull-back Jacobian) derivatives on all four axes at arbitrary T^4
      points, compared with the byte-pinned Route B tables and with sympy on
      SAMPLED N in {1, 3, 5, 9, 11} and random points, within tolerance; the
      radial profiles h0, h1, b_j and their first and second derivatives by
      analytic polynomial differentiation, on a general-K code path that is
      CHECKED only for K <= 8, the maximum of the target class (against
      v5.6.6.3 for K <= 3; against sympy for K = 8 at rho = 0, rho = 1 and
      random rho, jets 0..2; no uniform-in-K proof is claimed); and the
      pulled-back 2-jet of
      the 79 Route C channels from ambient jets and the embedding jets, obtained
      by second-order Taylor arithmetic in the five collar coordinates (so the
      product rule through J(x), its minors and the reference metric is
      automatic), compared with sympy on SAMPLED random configurations within
      tolerance (a sampled contrast, not a symbolic identity, and NOT an
      independent one: the sympy side reuses this module's SIDES,
      SIDE_RADIAL_SIGN, REFERENCE_METRIC, SYMMETRIC5 and B_TRIPLES, which a
      separate gate pins equal to the byte-pinned Route C constants).

Why.  The current Route C (v5.6.6.3) accepts only N in {1, 2, 3}, a single
tangential direction x0 + x1, and nine-point stencils; Codex's exact witness
(1/4) cos(x2) is at positive distance from that whole family, so no uniform
N -> infinity statement can be built on it.  These primitives are the first
unit of a planned full-T^4, arbitrary-N Route C rebuilt without finite
differences: they are DESIGNED so that a future action / JVP built on them
would have no stencil source of error.  This module implements no action and
no JVP, and it does not prove B_FD = 0 for anything; that claim, if it is
ever made, belongs to the future units and their own audits.

What this module does NOT claim: nothing about the action, the JVP, any
quadrature, any margin, any member, or any bridge / C1 / N1 / B4 / B5 key.

Scope note on even N (holo-028): because each wavevector enters cos-first and
sin-second, the span V_N is NOT closed under derivatives for even N (N = 2:
d cos(theta) = -sin(theta) lies outside V_2; x2 enters as cos at N = 8 and as
sin at N = 9).  This does not affect the evaluation tables or asymptotic
density, but it forbids P_N d = d P_N at every N: future commutation lemmas
must use the complete-pair subsequence N = 1 + 2M or state derivatives
outside V_N.

"Exact" in this module's name and keys means: given by an analytic formula
(spectral, polynomial, chain rule) instead of a differencing scheme.  The
arithmetic is float64 throughout; no uniform enclosure of rounding is claimed,
and every number reported is a sampled float64 residual.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"
SCHEMA = "holo.one-omega-topological-so3-route-c-full-t4-exact-primitives-v5-6-7.v1"

BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
DECLARED_ENUMERATION_PATH = HERE / "derive_one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.py"
DECLARED_ENUMERATION_SHA256 = "a8b26f130189dacfef14faf9cb9e1d1f19208cb645e267f198fc2f21ede428e4"
ROUTE_B_PATH = HERE / "derive_one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.py"
ROUTE_B_SHA256 = "6c98724d0e51c1cad16c80303e6ad7625d661bd1c9c56c9ff96c5b8124992909"
ROUTE_C_PATH = HERE / "derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3.py"
ROUTE_C_SHA256 = "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"

SEED = 567
N_MAX_CHECK = 11
K_MAX_SYMBOLIC = 8  # maximum K of the target class; the general-K code path is checked up to here only
SIDES = ("plus", "minus")
SIDE_RADIAL_SIGN = {"plus": -1.0, "minus": 1.0}
REFERENCE_METRIC = np.diag((-1.64, 1.17, 1.31, 1.46, 1.17))
CHANNELS = 64
COMMON_BLOCKS = (("common.gamma", (10,)), ("common.T", (1,)), ("common.log_Omega", (1,)), ("common.varphi_E0", (3,)), ("common.A_E0", (4, 3)), ("Q_frame.q", (3,)))
SIDE_BLOCKS = (("Y", (1,)), ("metric_free", (5,)), ("A_perp", (3,)), ("B0_full", (10, 3)), ("r_E0", (3,)), ("boundary_jet_J1", (64,)), ("interior_bump_C", ("K", 64)))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))
B_TRIPLES = tuple((i, j, k) for i in range(5) for j in range(i + 1, 5) for k in range(j + 1, 5))


class ExactPrimitivesError(RuntimeError):
    pass


def _validated_integer(name: str, value: Any, minimum: int) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ExactPrimitivesError(f"{name} must be an integer >= {minimum}, got {value!r}")
    result = int(value)
    if result < minimum:
        raise ExactPrimitivesError(f"{name} must be an integer >= {minimum}, got {value!r}")
    return result


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _load_pinned_module(path: Path, expected: str, name: str) -> Any:
    observed = _sha256(path)
    if observed != expected:
        raise ExactPrimitivesError(f"{path.name} byte pin drift: {observed}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# M1: nested real Fourier basis of T^4 and the free-data layout
# --------------------------------------------------------------------------
def nonzero_wavevectors(count: int) -> list[tuple[int, int, int, int]]:
    """Contract enumeration: fixed priority list, then |k|_inf shells sorted by (|k|_1, lexicographic),
    keeping one representative per +-k pair (first nonzero component positive)."""
    count = _validated_integer("count", count, 0)
    priority = [(1, 1, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    result: list[tuple[int, int, int, int]] = []
    for vector in priority:
        if vector not in result:
            result.append(vector)
    radius = 1
    while len(result) < count:
        candidates = []
        for vector in itertools.product(range(-radius, radius + 1), repeat=4):
            if vector == (0, 0, 0, 0) or max(map(abs, vector)) != radius:
                continue
            if next(item for item in vector if item != 0) < 0:
                continue
            candidates.append(vector)
        for vector in sorted(candidates, key=lambda item: (sum(map(abs, item)), item)):
            if vector not in result:
                result.append(vector)
        radius += 1
    return result[:count] if count > 0 else []


def _label(kind: str, vector: Sequence[int]) -> str:
    if kind == "1":
        return "1"
    terms = "+".join(f"{k}*x{i}" for i, k in enumerate(vector) if k != 0)
    return f"{kind}({terms})"


def real_fourier_modes(N: int) -> list[dict[str, Any]]:
    """Mode index m = 0 is the constant; odd m is cos, even m >= 2 is sin of nonzero[(m-1)//2]."""
    N = _validated_integer("N", N, 1)
    nonzero = nonzero_wavevectors(max(1, (N - 1 + 1) // 2))
    modes = [{"kind": "1", "wavevector": (0, 0, 0, 0), "label": "1"}]
    for index in range(1, N):
        vector = nonzero[(index - 1) // 2]
        kind = "cos" if index % 2 == 1 else "sin"
        modes.append({"kind": kind, "wavevector": vector, "label": _label(kind, vector)})
    return modes


def free_layout(N: int, K: int) -> dict[str, Any]:
    N = _validated_integer("N", N, 1)
    K = _validated_integer("K", K, 1)
    blocks: dict[str, Any] = {}
    cursor = 0

    def add(name: str, shape: tuple[Any, ...]) -> None:
        nonlocal cursor
        resolved = tuple(K if s == "K" else int(s) for s in shape)
        full = (N,) + resolved
        size = math.prod(int(s) for s in full)  # exact Python integers: no int64 overflow for large N
        blocks[name] = {"start": cursor, "stop": cursor + size, "shape": list(full)}
        cursor += size

    for name, shape in COMMON_BLOCKS:
        add(name, shape)
    for side in SIDES:
        for name, shape in SIDE_BLOCKS:
            add(f"{side}.{name}", shape)
    return {"blocks": blocks, "free_coordinate_dimension": cursor, "canonical_sha256": _canonical_sha256(blocks)}


# --------------------------------------------------------------------------
# M2a: analytic spectral tables in float64 (value, first, second, third) on the four axes
# --------------------------------------------------------------------------
def spectral_tables(modes: Sequence[Mapping[str, Any]], points: np.ndarray) -> dict[str, np.ndarray]:
    points = np.asarray(points, dtype=float)
    P, M = points.shape[0], len(modes)
    values = np.zeros((P, M))
    first = np.zeros((P, 4, M))
    second = np.zeros((P, 4, 4, M))
    third = np.zeros((P, 4, 4, 4, M))
    for m, mode in enumerate(modes):
        k = np.asarray(mode["wavevector"], dtype=float)
        phase = points @ k
        if mode["kind"] == "1":
            values[:, m] = 1.0
            continue
        c, s = np.cos(phase), np.sin(phase)
        if mode["kind"] == "cos":
            d0, d1, d2, d3 = c, -s, -c, s
        elif mode["kind"] == "sin":
            d0, d1, d2, d3 = s, c, -s, -c
        else:
            raise ExactPrimitivesError(f"unknown mode kind {mode['kind']!r}")
        values[:, m] = d0
        first[:, :, m] = d1[:, None] * k[None, :]
        second[:, :, :, m] = d2[:, None, None] * np.einsum("a,b->ab", k, k)[None]
        third[:, :, :, :, m] = d3[:, None, None, None] * np.einsum("a,b,c->abc", k, k, k)[None]
    return {"values": values, "first": first, "second": second, "third": third}


def evaluate_block(coefficients: np.ndarray, tables: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
    """coefficients (M, ...) -> value (P, ...), first (P, 4, ...), second (P, 4, 4, ...), third (P, 4, 4, 4, ...)."""
    return {
        "value": np.tensordot(tables["values"], coefficients, axes=([1], [0])),
        "first": np.tensordot(tables["first"], coefficients, axes=([2], [0])),
        "second": np.tensordot(tables["second"], coefficients, axes=([3], [0])),
        "third": np.tensordot(tables["third"], coefficients, axes=([4], [0])),
    }


# --------------------------------------------------------------------------
# M2b: radial profiles with analytic polynomial derivatives (general-K code path, checked for K <= 8 only)
# --------------------------------------------------------------------------
def radial_profile_polynomials(K: int) -> dict[str, Any]:
    K = _validated_integer("K", K, 1)
    Poly = np.polynomial.Polynomial
    h0 = Poly([1.0, 0.0, 0.0, -10.0, 15.0, -6.0])
    h1 = Poly([0.0, 1.0]) * h0
    envelope = Poly([0.0, 0.0, 0.0, 64.0]) * Poly([1.0, -1.0]) ** 3
    bumps = []
    for j in range(K):
        legendre = np.polynomial.legendre.Legendre.basis(j).convert(kind=Poly)
        bumps.append(envelope * legendre(Poly([-1.0, 2.0])))
    return {"h0": h0, "h1": h1, "bumps": bumps}


def radial_profiles(rho: float, K: int) -> dict[str, np.ndarray]:
    polys = radial_profile_polynomials(K)
    out = {}
    for name in ("h0", "h1"):
        p = polys[name]
        out[name] = np.asarray([p(rho), p.deriv(1)(rho), p.deriv(2)(rho)])
    out["bumps"] = np.asarray([[b(rho) for b in polys["bumps"]], [b.deriv(1)(rho) for b in polys["bumps"]], [b.deriv(2)(rho) for b in polys["bumps"]]])
    return out


# --------------------------------------------------------------------------
# M2c: second-order Taylor arithmetic in the five collar coordinates and the pulled-back 2-jet (checked by sampled contrast with sympy)
# --------------------------------------------------------------------------
class Jet2:
    """value, gradient (5,), Hessian (5, 5) in the collar coordinates (x0, x1, x2, x3, rho); ring operations only."""

    __slots__ = ("v", "d", "dd")

    def __init__(self, v: float, d: np.ndarray | None = None, dd: np.ndarray | None = None):
        self.v = float(v)
        self.d = np.zeros(5) if d is None else np.asarray(d, dtype=float)
        self.dd = np.zeros((5, 5)) if dd is None else np.asarray(dd, dtype=float)

    def __add__(self, o: "Jet2 | float") -> "Jet2":
        o = o if isinstance(o, Jet2) else Jet2(o)
        return Jet2(self.v + o.v, self.d + o.d, self.dd + o.dd)

    __radd__ = __add__

    def __neg__(self) -> "Jet2":
        return Jet2(-self.v, -self.d, -self.dd)

    def __sub__(self, o: "Jet2 | float") -> "Jet2":
        return self + (-(o if isinstance(o, Jet2) else Jet2(o)))

    def __mul__(self, o: "Jet2 | float") -> "Jet2":
        o = o if isinstance(o, Jet2) else Jet2(o)
        return Jet2(self.v * o.v, self.v * o.d + o.v * self.d, self.v * o.dd + o.v * self.dd + np.outer(self.d, o.d) + np.outer(o.d, self.d))

    __rmul__ = __mul__


def _det3(m: list[list[Jet2]]) -> Jet2:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def pulled_back_two_jet(ambient_value: np.ndarray, ambient_first: np.ndarray, ambient_second: np.ndarray, Y_first: np.ndarray, Y_second: np.ndarray, Y_third: np.ndarray, side: str) -> dict[str, np.ndarray]:
    """Exact 2-jet (value, first (5,79), second (5,5,79)) of the 79 pulled-back Route C channels.

    ambient_*: jets of the 64 ambient channels in the collar coordinates (x0..x3, rho);
    Y_first (4,), Y_second (4,4), Y_third (4,4,4): tangential derivatives of the embedding.
    Pull-back exactly as v5.6.6.3 _pullback_vector: J = [[I4, 0], [grad Y, sign]], metric J^T g J,
    connection J^T A, 3-form by 3x3 minors, reference J^T X_inf J.
    """
    if side not in SIDE_RADIAL_SIGN:
        raise ExactPrimitivesError(f"unknown side {side!r}")
    expected_shapes = {"ambient_value": (CHANNELS,), "ambient_first": (5, CHANNELS), "ambient_second": (5, 5, CHANNELS), "Y_first": (4,), "Y_second": (4, 4), "Y_third": (4, 4, 4)}
    given = {"ambient_value": ambient_value, "ambient_first": ambient_first, "ambient_second": ambient_second, "Y_first": Y_first, "Y_second": Y_second, "Y_third": Y_third}
    for name, array in given.items():
        if tuple(np.shape(array)) != expected_shapes[name]:
            raise ExactPrimitivesError(f"{name} has shape {tuple(np.shape(array))}, expected {expected_shapes[name]}")
    sign = SIDE_RADIAL_SIGN[side]
    amb = [Jet2(ambient_value[c], ambient_first[:, c], ambient_second[:, :, c]) for c in range(CHANNELS)]
    Yg: list[Jet2] = []
    for mu in range(4):
        d = np.zeros(5)
        d[:4] = Y_second[mu]
        dd = np.zeros((5, 5))
        dd[:4, :4] = Y_third[mu]
        Yg.append(Jet2(Y_first[mu], d, dd))
    zero, one = Jet2(0.0), Jet2(1.0)
    J = [[one if i == j else zero for j in range(5)] for i in range(5)]
    for mu in range(4):
        J[4][mu] = Yg[mu]
    J[4][4] = Jet2(sign)
    metric = [[zero] * 5 for _ in range(5)]
    for value, (i, j) in zip(amb[:15], SYMMETRIC5):
        metric[i][j] = value
        metric[j][i] = value

    def pull_metric(g: list[list[Jet2]]) -> list[Jet2]:
        out = []
        for a, b in SYMMETRIC5:
            total = zero
            for M in range(5):
                for Nn in range(5):
                    total = total + J[M][a] * g[M][Nn] * J[Nn][b]
            out.append(total)
        return out

    pulled_metric = pull_metric(metric)
    connection = [[amb[19 + 3 * M + a] for a in range(3)] for M in range(5)]
    pulled_connection = [[sum((J[M][a] * connection[M][c] for M in range(5)), zero) for c in range(3)] for a in range(5)]
    B = [[amb[34 + 3 * p + a] for a in range(3)] for p in range(10)]
    pulled_B = []
    for target in B_TRIPLES:
        row = [zero, zero, zero]
        for position, source in enumerate(B_TRIPLES):
            minor = _det3([[J[s][t] for t in target] for s in source])
            row = [row[a] + minor * B[position][a] for a in range(3)]
        pulled_B.append(row)
    reference = [[Jet2(REFERENCE_METRIC[i, j]) for j in range(5)] for i in range(5)]
    pulled_reference = pull_metric(reference)
    channels: list[Jet2] = list(pulled_metric) + amb[15:19] + [pulled_connection[a][c] for a in range(5) for c in range(3)] + [pulled_B[p][a] for p in range(10) for a in range(3)] + pulled_reference
    if len(channels) != 79:
        raise ExactPrimitivesError("pulled-back channel count")
    return {
        "value": np.asarray([c.v for c in channels]),
        "first": np.stack([c.d for c in channels], axis=-1),
        "second": np.stack([c.dd for c in channels], axis=-1),
    }


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def check_enumeration(declared: Any, bundle: Mapping[str, Any]) -> dict[str, Any]:
    rows = {}
    ok = True
    for N in range(1, N_MAX_CHECK + 1):
        modes = real_fourier_modes(N)
        nonzero_used = []
        for mode in modes[1:]:
            if mode["wavevector"] not in nonzero_used:
                nonzero_used.append(mode["wavevector"])
        declared_list = declared.declared_wavevectors(N)[: len(nonzero_used)]
        same = [tuple(v) for v in declared_list] == nonzero_used
        axes_active = [any(mode["wavevector"][axis] != 0 for mode in modes) for axis in range(4)]
        rows[str(N)] = {"modes": [m["label"] for m in modes], "matches_declared_nonzero_prefix": same, "axes_active": axes_active}
        ok = ok and same
    bundle_ok = True
    for N in ("1", "2", "3"):
        contract = bundle["pointwise_decoder_contract_by_N"][N]["basis"]
        modes = real_fourier_modes(int(N))
        bundle_ok = bundle_ok and list(contract["labels"]) == [m["label"] for m in modes] and [tuple(int(x) for x in v) for v in contract["mode_wavevectors"]] == [m["wavevector"] for m in modes]
    x2_first = next(N for N in range(1, N_MAX_CHECK + 1) if rows[str(N)]["axes_active"][2])
    x3_first = next(N for N in range(1, N_MAX_CHECK + 1) if rows[str(N)]["axes_active"][3])
    return {"rows": rows, "declared_prefix_match_all_N": ok, "bundle_labels_match_N1_to_N3": bundle_ok, "first_N_with_x2": x2_first, "first_N_with_x3": x3_first, "pass": bool(ok and bundle_ok and x2_first == 8 and x3_first == 10)}


def check_enumeration_beyond_priority(declared: Any) -> dict[str, Any]:
    """The dense N <= N_MAX_CHECK cross-check never leaves the five priority vectors.  This one exercises the
    shell loop: the sixth vector (N = 12 cos, N = 13 sin), the end of the |k|_inf = 1 shell (N = 81) and the first
    |k|_inf = 2 vector (N = 82 cos, N = 83 sin), plus N = 200 inside the second shell; nestedness of the mode list;
    one canonical representative per +-k pair; and labels / cos-sin parity against declared_collocation_matrix."""
    rows = {}
    ok = True
    for N in (12, 13, 27, 81, 82, 83, 200):
        modes = real_fourier_modes(N)
        mine = nonzero_wavevectors(max(1, N // 2))
        declared_prefix = [tuple(v) for v in declared.declared_wavevectors(N)[: len(mine)]]
        _, declared_labels = declared.declared_collocation_matrix(N)
        labels_same = list(declared_labels) == [m["label"] for m in modes]
        last = modes[-1]
        rows[str(N)] = {"declared_prefix_same": mine == declared_prefix, "labels_and_parity_same_as_declared_collocation": labels_same,
                        "last_mode": last["label"], "last_mode_kind": last["kind"], "last_mode_inf_norm": int(max(map(abs, last["wavevector"])))}
        ok = ok and mine == declared_prefix and labels_same
    nested = all(real_fourier_modes(N) == real_fourier_modes(N + 1)[:N] for N in range(1, 90))
    vectors = nonzero_wavevectors(120)
    canonical = all(next(item for item in v if item != 0) > 0 for v in vectors)
    distinct = len(set(vectors)) == len(vectors) and not any(tuple(-c for c in v) in set(vectors) for v in vectors)
    radius_one_complete = set(vectors[:40]) == {v for v in itertools.product(range(-1, 2), repeat=4) if v != (0, 0, 0, 0) and next(item for item in v if item != 0) > 0}
    sixth_ok = rows["12"]["last_mode_kind"] == "cos" and rows["13"]["last_mode_kind"] == "sin" and rows["13"]["last_mode"] == _label("sin", vectors[5])
    radius_two_ok = rows["81"]["last_mode_inf_norm"] == 1 and rows["82"]["last_mode_inf_norm"] == 2 and rows["82"]["last_mode_kind"] == "cos" and rows["83"]["last_mode_inf_norm"] == 2 and rows["83"]["last_mode_kind"] == "sin"
    return {"rows": rows, "declared_and_collocation_match": ok, "nested_1_to_90": nested, "canonical_positive_first_component": canonical,
            "distinct_and_no_pm_duplicates": distinct, "radius_one_shell_complete_in_first_40": radius_one_complete,
            "sixth_vector_enters_at_N12_N13": sixth_ok, "first_radius_two_vector_enters_at_N82_N83": radius_two_ok,
            "pass": bool(ok and nested and canonical and distinct and radius_one_complete and sixth_ok and radius_two_ok)}


def check_layout(bundle: Mapping[str, Any]) -> dict[str, Any]:
    rows = {}
    ok = True
    for N in ("1", "2", "3"):
        contract = bundle["pointwise_decoder_contract_by_N"][N]
        K = int(contract["K"])
        mine = free_layout(int(N), K)
        same_blocks = mine["blocks"] == {k: {"start": int(v["start"]), "stop": int(v["stop"]), "shape": [int(x) for x in v["shape"]]} for k, v in contract["free_layout"]["blocks"].items()}
        same_sha = mine["canonical_sha256"] == contract["free_layout"]["canonical_sha256"]
        same_dim = mine["free_coordinate_dimension"] == int(contract["free_coordinate_dimension"])
        rows[N] = {"blocks_equal": same_blocks, "canonical_sha_equal": same_sha, "dimension_equal": same_dim, "dimension": mine["free_coordinate_dimension"]}
        ok = ok and same_blocks and same_sha and same_dim
    general = {f"N{N}_K{N}": free_layout(N, N)["free_coordinate_dimension"] for N in range(4, N_MAX_CHECK + 1)}
    return {"rows": rows, "general_dimensions_K_equals_N": general, "pass": bool(ok)}


def check_tables(route_b: Any, rng: np.random.Generator) -> dict[str, Any]:
    worst_b = 0.0
    worst_sym = 0.0
    x = sp.symbols("x0 x1 x2 x3")
    for N in (1, 3, 5, 9, 11):
        modes = real_fourier_modes(N)
        points = rng.uniform(0.0, 2.0 * math.pi, size=(4, 4))
        mine = spectral_tables(modes, points)
        theirs = route_b.fourier_tables({"labels": [m["label"] for m in modes], "mode_wavevectors": [list(m["wavevector"]) for m in modes]}, points)
        for key in ("values", "first", "second"):
            worst_b = max(worst_b, float(np.max(np.abs(mine[key] - theirs[key]))))
        for m, mode in enumerate(modes):
            phase = sum(int(k) * xi for k, xi in zip(mode["wavevector"], x))
            expr = sp.Integer(1) if mode["kind"] == "1" else (sp.cos(phase) if mode["kind"] == "cos" else sp.sin(phase))
            for p in range(points.shape[0]):
                subs = dict(zip(x, points[p]))
                worst_sym = max(worst_sym, abs(float(expr.subs(subs)) - mine["values"][p, m]))
                for a in range(4):
                    worst_sym = max(worst_sym, abs(float(sp.diff(expr, x[a]).subs(subs)) - mine["first"][p, a, m]))
                    for b in range(4):
                        worst_sym = max(worst_sym, abs(float(sp.diff(expr, x[a], x[b]).subs(subs)) - mine["second"][p, a, b, m]))
                        for c in range(4):
                            worst_sym = max(worst_sym, abs(float(sp.diff(expr, x[a], x[b], x[c]).subs(subs)) - mine["third"][p, a, b, c, m]))
    # synthetic mode outside the priority list, all four axes and both signs active, against sympy only
    synthetic_k = (2, -3, 4, -5)
    synthetic_modes = [{"kind": kind, "wavevector": synthetic_k, "label": _label(kind, synthetic_k)} for kind in ("cos", "sin")]
    synthetic_points = rng.uniform(0.0, 2.0 * math.pi, size=(4, 4))
    synthetic = spectral_tables(synthetic_modes, synthetic_points)
    worst_synthetic = 0.0
    phase = sum(int(k) * xi for k, xi in zip(synthetic_k, x))
    for m, expr in enumerate((sp.cos(phase), sp.sin(phase))):
        for p in range(synthetic_points.shape[0]):
            subs = dict(zip(x, synthetic_points[p]))
            worst_synthetic = max(worst_synthetic, abs(float(expr.subs(subs)) - synthetic["values"][p, m]))
            for a in range(4):
                worst_synthetic = max(worst_synthetic, abs(float(sp.diff(expr, x[a]).subs(subs)) - synthetic["first"][p, a, m]))
                for b in range(4):
                    worst_synthetic = max(worst_synthetic, abs(float(sp.diff(expr, x[a], x[b]).subs(subs)) - synthetic["second"][p, a, b, m]))
                    for c in range(4):
                        worst_synthetic = max(worst_synthetic, abs(float(sp.diff(expr, x[a], x[b], x[c]).subs(subs)) - synthetic["third"][p, a, b, c, m]))
    return {"sampled_N": [1, 3, 5, 9, 11], "random_points_per_N": 4, "max_abs_difference_vs_pinned_route_b": worst_b, "max_abs_difference_vs_sympy_through_third": worst_sym, "synthetic_mode_k": list(synthetic_k), "max_abs_difference_vs_sympy_synthetic_mode_through_third": worst_synthetic, "pass": bool(worst_b <= 1.0e-12 and worst_sym <= 1.0e-11 and worst_synthetic <= 1.0e-10)}


def check_radial(route_c: Any, rng: np.random.Generator) -> dict[str, Any]:
    r = sp.symbols("rho")
    h0 = 1 - 10 * r**3 + 15 * r**4 - 6 * r**5
    h1 = r * h0
    worst_c = 0.0
    worst_sym = 0.0
    rhos = np.concatenate(([0.0, 1.0], rng.uniform(0.0, 1.0, size=5)))  # endpoints included
    for rho in rhos:
        for K in (1, 2, 3):
            mine = radial_profiles(float(rho), K)
            worst_c = max(worst_c, float(np.max(np.abs(mine["bumps"][0] - route_c._radial_bumps(float(rho), K)))))
        K = K_MAX_SYMBOLIC
        mine = radial_profiles(float(rho), K)
        for name, expr in (("h0", h0), ("h1", h1)):
            for order in range(3):
                worst_sym = max(worst_sym, abs(float(sp.diff(expr, r, order).subs(r, rho)) - mine[name][order]))
        for j in range(K):
            bump = 64 * r**3 * (1 - r) ** 3 * sp.legendre(j, 2 * r - 1)
            for order in range(3):
                worst_sym = max(worst_sym, abs(float(sp.diff(bump, r, order).subs(r, rho)) - mine["bumps"][order][j]))
    degrees = {f"b_{j}": int(radial_profile_polynomials(K_MAX_SYMBOLIC)["bumps"][j].degree()) for j in range(K_MAX_SYMBOLIC)}
    return {"K_symbolic": K_MAX_SYMBOLIC, "rho_samples": [float(v) for v in rhos], "jets_checked": [0, 1, 2], "max_abs_difference_vs_v5_6_6_3_bumps_K_le_3": worst_c, "max_abs_difference_vs_sympy_through_second_derivative_K8": worst_sym, "bump_degrees_K8": degrees, "pass": bool(worst_c <= 1.0e-12 and worst_sym <= 1.0e-9)}


def check_pullback(rng: np.random.Generator) -> dict[str, Any]:
    """Symbolic ambient configuration (quadratic in the five collar coordinates, cubic embedding) versus Jet2.
    Not independent: the sympy side reuses the module constants (see check_constants_against_pinned_route_c)."""
    X = sp.symbols("x0 x1 x2 x3 rho")
    worst = 0.0
    for side in SIDES:
        coefficients = rng.uniform(-0.3, 0.3, size=(CHANNELS, 21))
        monomials = [sp.Integer(1)] + list(X) + [X[a] * X[b] for a in range(5) for b in range(a, 5)]
        fields = [sum(c * mnm for c, mnm in zip(coefficients[ch], monomials)) for ch in range(CHANNELS)]
        y = rng.uniform(-0.3, 0.3, size=(1 + 4 + 10 + 20))
        cubic = [sp.Integer(1)] + list(X[:4]) + [X[a] * X[b] for a in range(4) for b in range(a, 4)] + [X[a] * X[b] * X[c] for a in range(4) for b in range(a, 4) for c in range(b, 4)]
        Y = sum(c * mnm for c, mnm in zip(y, cubic))
        point = dict(zip(X, rng.uniform(-0.5, 0.5, size=5)))
        # symbolic pull-back
        sign = SIDE_RADIAL_SIGN[side]
        Yg = [sp.diff(Y, X[mu]) for mu in range(4)]
        Jm = sp.eye(5)
        for mu in range(4):
            Jm[4, mu] = Yg[mu]
        Jm[4, 4] = sign
        g = sp.zeros(5, 5)
        for value, (i, j) in zip(fields[:15], SYMMETRIC5):
            g[i, j] = value
            g[j, i] = value
        pulled_metric = Jm.T * g * Jm
        A = sp.Matrix(5, 3, lambda M, a: fields[19 + 3 * M + a])
        pulled_connection = Jm.T * A
        Bm = sp.Matrix(10, 3, lambda p, a: fields[34 + 3 * p + a])
        pulled_B = sp.zeros(10, 3)
        for tp, target in enumerate(B_TRIPLES):
            for sp_, source in enumerate(B_TRIPLES):
                minor = Jm.extract(list(source), list(target)).det()
                for a in range(3):
                    pulled_B[tp, a] += minor * Bm[sp_, a]
        reference = Jm.T * sp.Matrix(5, 5, lambda i, j: sp.Float(REFERENCE_METRIC[i, j])) * Jm
        symbolic = [pulled_metric[i, j] for i, j in SYMMETRIC5] + fields[15:19] + [pulled_connection[a, c] for a in range(5) for c in range(3)] + [pulled_B[p, a] for p in range(10) for a in range(3)] + [reference[i, j] for i, j in SYMMETRIC5]
        # numeric inputs for Jet2
        value = np.asarray([float(f.subs(point)) for f in fields])
        first = np.asarray([[float(sp.diff(f, X[a]).subs(point)) for f in fields] for a in range(5)])
        second = np.asarray([[[float(sp.diff(f, X[a], X[b]).subs(point)) for f in fields] for b in range(5)] for a in range(5)])
        Y_first = np.asarray([float(Yg[mu].subs(point)) for mu in range(4)])
        Y_second = np.asarray([[float(sp.diff(Yg[mu], X[a]).subs(point)) for a in range(4)] for mu in range(4)])
        Y_third = np.asarray([[[float(sp.diff(Yg[mu], X[a], X[b]).subs(point)) for b in range(4)] for a in range(4)] for mu in range(4)])
        mine = pulled_back_two_jet(value, first, second, Y_first, Y_second, Y_third, side)
        for c, expr in enumerate(symbolic):
            worst = max(worst, abs(float(expr.subs(point)) - mine["value"][c]))
            for a in range(5):
                worst = max(worst, abs(float(sp.diff(expr, X[a]).subs(point)) - mine["first"][a, c]))
                for b in range(5):
                    worst = max(worst, abs(float(sp.diff(expr, X[a], X[b]).subs(point)) - mine["second"][a, b, c]))
    return {"max_abs_difference_vs_sympy_value_first_second": worst, "pass": bool(worst <= 1.0e-10)}


def check_constants_against_pinned_route_c(route_c: Any) -> dict[str, Any]:
    """The sympy expected value in check_pullback reuses this module's SIDES, SIDE_RADIAL_SIGN, REFERENCE_METRIC,
    SYMMETRIC5 and B_TRIPLES, so that contrast is NOT independent of them.  This gate pins each of them equal to
    the byte-pinned Route C (v5.6.6.3) so a common-mode transcription error cannot pass unnoticed."""
    equal = {
        "SIDES": tuple(route_c.SIDES) == SIDES,
        "SIDE_RADIAL_SIGN": dict(route_c.SIDE_RADIAL_SIGN) == SIDE_RADIAL_SIGN,
        "REFERENCE_METRIC": bool(np.array_equal(np.asarray(route_c.REFERENCE_METRIC, dtype=float), REFERENCE_METRIC)),
        "SYMMETRIC5": tuple(tuple(p) for p in route_c.SYMMETRIC5) == SYMMETRIC5,
        "B_TRIPLES": tuple(tuple(t) for t in route_c.B_TRIPLES) == B_TRIPLES,
    }
    return {"equal": equal, "pass": bool(all(equal.values()))}


def forbidden_tokens() -> tuple[str, ...]:
    """Assembled at runtime so the literals never appear in this module's code."""
    return ("_ST" + "EP", "WEI" + "GHTS", "sten" + "cil", "finite_" + "difference", "richard" + "son", "np.grad" + "ient")


def static_derivative_path_audit(source_path: Path) -> dict[str, Any]:
    """Lexical audit only: the code outside the module docstring must contain none of the assembled
    tokens.  It is not a semantic proof that no numerical differencing scheme exists in the module."""
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    first = tree.body[0]
    docstring_end = first.end_lineno if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) else 0
    code_only = "\n".join(source.splitlines()[docstring_end:])
    hits = [token for token in forbidden_tokens() if token in code_only]
    return {"kind": "lexical token audit, not a semantic proof", "forbidden_hits": hits, "pass": not hits}


def build_report() -> dict[str, Any]:
    if _sha256(BUNDLE_PATH) != BUNDLE_SHA256:
        raise ExactPrimitivesError("bundle drift")
    bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    declared = _load_pinned_module(DECLARED_ENUMERATION_PATH, DECLARED_ENUMERATION_SHA256, "pinned_v5_6_6_8")
    route_b = _load_pinned_module(ROUTE_B_PATH, ROUTE_B_SHA256, "pinned_route_b_v5_6_5")
    route_c = _load_pinned_module(ROUTE_C_PATH, ROUTE_C_SHA256, "pinned_route_c_v5_6_6_3")
    rng = np.random.default_rng(SEED)
    enumeration = check_enumeration(declared, bundle)
    beyond = check_enumeration_beyond_priority(declared)
    layout = check_layout(bundle)
    tables = check_tables(route_b, rng)
    radial = check_radial(route_c, rng)
    pullback = check_pullback(rng)
    constants = check_constants_against_pinned_route_c(route_c)
    static = static_derivative_path_audit(Path(__file__))
    decision = {
        "full_t4_real_fourier_enumeration_matches_declared_N1_to_N11_pass": bool(enumeration["pass"]),
        "full_t4_enumeration_beyond_priority_N12_N13_N81_N82_N83_N200_matches_declared_pass": bool(beyond["pass"]),
        "x2_axis_first_active_at_N8_and_x3_at_N10_pass": bool(enumeration["first_N_with_x2"] == 8 and enumeration["first_N_with_x3"] == 10),
        "free_layout_matches_bundle_contracts_N1_to_N3_pass": bool(layout["pass"]),
        "spectral_tables_through_third_derivative_four_axes_sampled_within_tolerance_vs_pinned_route_b_and_sympy_pass": bool(tables["pass"]),
        "radial_profiles_analytic_polynomial_derivatives_checked_K_le_8_pass": bool(radial["pass"]),
        "pulled_back_two_jet_chain_rule_sampled_within_tolerance_vs_sympy_pass": bool(pullback["pass"]),
        "pullback_constants_equal_to_pinned_route_c_pass": bool(constants["pass"]),
        "lexical_derivative_path_audit_no_forbidden_tokens_pass": bool(static["pass"]),
        "action_or_jvp_claim_pass": False,
        "quadrature_claim_pass": False,
        "margins_claim_pass": False,
        "uniform_N_to_infinity_bridge_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
    }
    return {
        "schema": SCHEMA,
        "source_pins": {"C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256, "declared_enumeration_v5_6_6_8_sha256": DECLARED_ENUMERATION_SHA256, "route_b_v5_6_5_sha256": ROUTE_B_SHA256, "route_c_v5_6_6_3_sha256": ROUTE_C_SHA256},
        "enumeration": enumeration,
        "enumeration_beyond_priority": beyond,
        "layout": layout,
        "tables": tables,
        "radial": radial,
        "pullback": pullback,
        "constants_vs_pinned_route_c": constants,
        "static": static,
        "decision": decision,
        "scope": "primitives only (M1 + M2); spectral tables checked on sampled N and random points; radial derivatives checked for K <= 8 only (rho = 0, 1 and random, jets 0..2); pull-back contrast sampled within tolerance, not a symbolic identity; the derivative-path audit is lexical, not semantic; the pull-back contrast is not independent of the module constants (gated equal to pinned Route C); 'exact' = analytic formula in float64 arithmetic, no uniform rounding enclosure; V_N is not derivative-closed for even N (use N = 1 + 2M for commutation lemmas); no action, JVP, quadrature, margin, member or bridge claim; B_FD = 0 is not claimed; no receipt written by design",
    }


def main() -> None:
    report = build_report()
    print(json.dumps({k: v for k, v in report["decision"].items() if v}, indent=2))
    print("enumeration x2 at N =", report["enumeration"]["first_N_with_x2"], "x3 at N =", report["enumeration"]["first_N_with_x3"])
    print("tables vs Route B", f"{report['tables']['max_abs_difference_vs_pinned_route_b']:.2e}", "vs sympy", f"{report['tables']['max_abs_difference_vs_sympy_through_third']:.2e}")
    print("radial vs v5.6.6.3", f"{report['radial']['max_abs_difference_vs_v5_6_6_3_bumps_K_le_3']:.2e}", "vs sympy K8", f"{report['radial']['max_abs_difference_vs_sympy_through_second_derivative_K8']:.2e}", report["radial"]["bump_degrees_K8"])
    print("pullback vs sympy", f"{report['pullback']['max_abs_difference_vs_sympy_value_first_second']:.2e}")


if __name__ == "__main__":
    main()
