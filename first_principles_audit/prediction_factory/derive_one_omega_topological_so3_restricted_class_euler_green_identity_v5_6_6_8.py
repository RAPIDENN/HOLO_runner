#!/usr/bin/env python3
"""Exact restricted-class Euler--Green identity, continuity bounds, and a
uniform-in-N stability audit of the declared collocation (v5.6.6.8).

This gate attacks the open obligation recorded by v5.6.6.7:

    "prove the exact second-order Euler--Green identity and continuity bounds
     on the declared restricted C2 spectral class".

It does three things and nothing more.

(A) Algebraic identity.  For an arbitrary second-order Lagrangian density
    L(q, q_i, q_ij) of n channels on the collar T^4 x [0,1] it verifies with
    exact symbolic total derivatives (sympy, no numerics) that

        dL = E . dq + sum_i D_i H^i,

    with the formal Euler operator
        E = C - sum_i D_i P^i + sum_{i<=j} D_i D_j Q^{ij}
    and the explicit boundary current
        H^i = P^i dq + sum_{j>=i} Q^{ij} dq_j - sum_{j<=i} (D_j Q^{ji}) dq,
    where C = dL/dq, P^i = dL/dq_i, Q^{ij} = dL/dq_ij (i<=j independent jets).
    It also verifies that the interface functional obtained after one periodic
    tangential integration by parts,

        G[dq] = int_{T^4} [ P^rho dq + Q^{rho rho} dq_rho - (D_rho Q^{rho rho}) dq
                            + sum_mu Q^{mu rho} dq_mu ] dx,

    contains no tangential derivative of order > 2 of the field and no
    radial derivative of order > 3.  It also transcribes the literal Route C
    two-coordinate (theta, rho) current of v5.6.6.3 _bulk_grid_euler_green,
    which differentiates the grid contraction fields Q.dq (product rule), and
    verifies that it is IDENTICALLY the unit-diagonal symmetric-split
    representative and that its subtraction-defined Euler contraction
    E.dq := dL - div H equals the formal Euler operator contraction exactly.
    Hence Route C's "bulk_Euler_contraction_integral" and "pointwise_Euler_Linf"
    are genuine Euler-operator quantities up to discretization error.  A
    separate, weaker observation is recorded: because E is defined by
    subtraction, the quantity "Stokes_residual_direct_minus_Euler_Green" is an
    identity of the discrete divergence theorem (zero-mean spectral derivative
    plus exact Gauss--Legendre integration of the barycentric derivative) and
    is therefore action-independent; the action-sensitive finite check in
    those receipts is the chain residual and the three-way AD/FD5/Route C
    comparison of first variations.

(B) Radial junction.  It verifies symbolically that the declared C2 radial
    primitives h0, h1 and the Legendre bumps b_j (j < K, K up to 8) have the
    declared jets at rho=0 and vanish with first and second derivatives at
    rho=1, so that every term of the outer current H^rho at rho=1 is
    identically zero for tangent variations sharing the class profiles (dq,
    dq_mu, dq_rho all vanish there).  The fields are C2 across the zero
    extension; the second-order density itself is only C0 there (the third
    derivatives of b_j and h0 do not vanish at rho=1), so no distribution
    enters S or DS, while the formal fourth-order Euler operator would carry a
    delta layer at rho=1 that tangent variations annihilate.

(C) Uniform-in-N stability audit of the declared discretization.  It
    re-implements the declared nested real T^4 Fourier enumeration and the
    declared Kronecker collocation nodes (2*pi*frac((n+0.173)*(sqrt2,sqrt3,
    sqrt5,sqrt7))) and measures the condition number and Lebesgue constant of
    the N x N collocation matrix for N up to N_MAX.  This is the matrix whose
    inverse enters the finite gluing map G_N and therefore DG_N.  The measured
    growth is recorded as a NEGATIVE result: the declared collocation does
    not admit a uniform right inverse in the Euclidean coefficient chart.

The theorem statement, hypotheses, norms, and the analytic continuity
argument are recorded in the scientific payload.  Only (A), (B), (C) and (D)
are machine-checked; the class-specific content (real-analyticity of the
literal v5.2 density on the margin set, Sobolev continuity, pointwise gluing
of arbitrary class members) is an analytic argument recorded as such and does
NOT flip the v5.6.4 key restricted_family_exact_action_identity_pass, which
stays False.  The theorem class deliberately differs from the v5.6.4 nodal
family: polynomial C2 radial profiles (v5.6.4.4) instead of exp-flat ones, and
pointwise gluing instead of gluing at N Kronecker nodes.

This gate does NOT flip uniform_N_to_infinity_bridge_pass, C1_ACTION_pass,
N1_ACTION_pass, B4/B5 or any promotion key.  It discharges the exact-identity
and continuity parts of the obligation on the continuum class and replaces
the remaining obligation by a sharper one: a uniformly stable finite
discretization (Galerkin or tensor equispaced FFT collocation) must replace
the Kronecker collocation before any DG_N uniform retraction can be claimed.
"""

from __future__ import annotations

import base64
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.json"
TEST = HERE / "test_one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.py"
SCHEMA = "holo.one-omega-topological-so3-restricted-class-euler-green-identity-v5-6-6-8.v1"

FROZEN_COMMIT = "ea014fd"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
V5667_PATH = ARTIFACTS / "one_omega_topological_so3_clean_process_mutant_redteam_v5_6_6_7.json"
V5667_SHA256 = "0319e1af291922f036cb45b0218fe9d636b07af3a7fd859bdf4426a745f8cdf1"

# Fixed before run.
SOBOLEV_S = 4.75
SPECTRAL_DECAY_POWER = 8.0
DIMENSION_T4 = 4
N_MAX_STABILITY = 160
STABILITY_ALERT_CONDITION = 1.0e6
STABILITY_ALERT_LEBESGUE = 1.0e4
RADIAL_K_MAX = 8
OFF_COLLOCATION_GLUING_TOLERANCE = 1.0e-12
SYMBOLIC_CASES = (
    {"label": "T4xI_one_channel", "coordinates": ("x0", "x1", "x2", "x3", "rho"), "channels": 1},
    {"label": "theta_rho_two_channel_route_C", "coordinates": ("theta", "rho"), "channels": 2},
    {"label": "x0_x1_rho_two_channel", "coordinates": ("x0", "x1", "rho"), "channels": 2},
)


class EulerGreenGateError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _load_json(path: Path, expected_sha256: str) -> Any:
    digest = _sha256(path)
    if digest != expected_sha256:
        raise EulerGreenGateError(f"byte pin drift for {path.name}: {digest} != {expected_sha256}")
    return json.loads(path.read_text())


# --------------------------------------------------------------------------
# (A) exact symbolic Euler--Green identity for a generic second-order density
# --------------------------------------------------------------------------

class _JetSpace:
    """Jet symbols q^a_I and dq^a_I with sorted multi-indices I (Schwarz symmetry built in).

    Total derivatives act on jet symbols by index extension, and on the generic density
    L(q, q_i, q_ij) through sympy's partial derivatives with respect to plain symbols, so
    every object is canonical and mixed partials commute identically.
    """

    def __init__(self, coordinates: tuple[str, ...], channels: int, q_order: int = 4, dq_order: int = 3):
        self.coordinates = coordinates
        self.n = len(coordinates)
        self.channels = channels
        self.q: dict[tuple[int, tuple[int, ...]], sp.Symbol] = {}
        self.dq: dict[tuple[int, tuple[int, ...]], sp.Symbol] = {}
        for a in range(channels):
            for order in range(q_order + 1):
                for index in itertools.combinations_with_replacement(range(self.n), order):
                    self.q[(a, index)] = sp.Symbol("q%d_%s" % (a, "".join(map(str, index)) or "o"))
            for order in range(dq_order + 1):
                for index in itertools.combinations_with_replacement(range(self.n), order):
                    self.dq[(a, index)] = sp.Symbol("dq%d_%s" % (a, "".join(map(str, index)) or "o"))
        self.inverse = {sym: key for key, sym in self.q.items()}
        self.inverse.update({sym: ("d", key) for key, sym in self.dq.items()})
        second_order_args = [self.q[(a, index)] for a in range(channels) for order in range(3) for index in itertools.combinations_with_replacement(range(self.n), order)]
        self.L = sp.Function("L")(*second_order_args)

    def extend(self, sym: sp.Symbol, i: int) -> sp.Symbol:
        key = self.inverse[sym]
        if key[0] == "d":
            a, index = key[1]
            return self.dq[(a, tuple(sorted(index + (i,))))]
        a, index = key
        return self.q[(a, tuple(sorted(index + (i,))))]

    def D(self, expr, i: int):
        """Total derivative along coordinate i."""

        expr = sp.sympify(expr)
        result = sp.S.Zero
        for sym in expr.free_symbols:
            if sym in self.inverse:
                result += sp.diff(expr, sym) * self.extend(sym, i)
        return sp.expand(result)

    def dq_orders(self, expr) -> tuple[int, int]:
        """(max tangential order, max radial order) among dq symbols present."""

        tangential = radial = 0
        for sym in sp.sympify(expr).free_symbols:
            key = self.inverse.get(sym)
            if key and key[0] == "d":
                index = key[1][1]
                radial = max(radial, sum(1 for k in index if k == self.n - 1))
                tangential = max(tangential, sum(1 for k in index if k != self.n - 1))
        return tangential, radial

    def has_dq_derivative(self, expr) -> bool:
        return any(
            self.inverse.get(sym, ("",))[0] == "d" and len(self.inverse[sym][1][1]) > 0
            for sym in sp.sympify(expr).free_symbols
        )


def symbolic_euler_green_case(coordinates: tuple[str, ...], channels: int) -> dict[str, Any]:
    J = _JetSpace(coordinates, channels)
    n, L, D = J.n, J.L, J.D
    q0 = lambda a: J.q[(a, ())]
    q1 = lambda a, i: J.q[(a, (i,))]
    q2 = lambda a, i, j: J.q[(a, tuple(sorted((i, j))))]
    dq0 = lambda a: J.dq[(a, ())]
    dq1 = lambda a, i: J.dq[(a, (i,))]
    dq2 = lambda a, i, j: J.dq[(a, tuple(sorted((i, j))))]
    pairs = [(i, j) for i in range(n) for j in range(i, n)]

    C = [sp.diff(L, q0(a)) for a in range(channels)]
    P = [[sp.diff(L, q1(a, i)) for i in range(n)] for a in range(channels)]
    Q = [{(i, j): sp.diff(L, q2(a, i, j)) for (i, j) in pairs} for a in range(channels)]

    # Direct first variation (chain rule on independent jets).
    dL = sp.S.Zero
    for a in range(channels):
        dL += C[a] * dq0(a)
        for i in range(n):
            dL += P[a][i] * dq1(a, i)
        for (i, j) in pairs:
            dL += Q[a][(i, j)] * dq2(a, i, j)

    # Formal Euler operator.
    E = []
    for a in range(channels):
        Ea = C[a]
        for i in range(n):
            Ea -= D(P[a][i], i)
        for (i, j) in pairs:
            Ea += D(D(Q[a][(i, j)], i), j)
        E.append(sp.expand(Ea))

    # General boundary current representative.
    H = []
    for i in range(n):
        Hi = sp.S.Zero
        for a in range(channels):
            Hi += P[a][i] * dq0(a)
            for (k, j) in pairs:
                if k == i:
                    Hi += Q[a][(k, j)] * dq1(a, j)
                if j == i:
                    Hi -= D(Q[a][(k, j)], k) * dq0(a)
        H.append(Hi)

    residual = sp.expand(dL - sum(E[a] * dq0(a) for a in range(channels)) - sum(D(H[i], i) for i in range(n)))
    identity_ok = residual == 0

    # Interface functional after one periodic tangential IBP (radial coordinate last).
    rho = n - 1
    G = sp.S.Zero
    for a in range(channels):
        G += P[a][rho] * dq0(a) + Q[a][(rho, rho)] * dq1(a, rho) - D(Q[a][(rho, rho)], rho) * dq0(a)
        for mu in range(rho):
            G += Q[a][(mu, rho)] * dq1(a, mu)
    tangential_divergence = sp.S.Zero
    for a in range(channels):
        for mu in range(rho):
            tangential_divergence -= D(Q[a][(mu, rho)] * dq0(a), mu)
    interface_exact = sp.expand(H[rho] - G - tangential_divergence) == 0
    max_tangential_order, max_radial_order = J.dq_orders(G)
    # radial order of the FIELD jets entering G (D_rho Q^{rho rho} carries third radial jets of q)
    field_radial_order = 0
    for sym in G.free_symbols:
        key = J.inverse.get(sym)
        if key and key[0] != "d":
            field_radial_order = max(field_radial_order, sum(1 for k in key[1] if k == rho))
    field_tangential_order = 0
    for sym in G.free_symbols:
        key = J.inverse.get(sym)
        if key and key[0] != "d":
            field_tangential_order = max(field_tangential_order, sum(1 for k in key[1] if k != rho))

    route_c_literal_derivative_free = None
    route_c_symmetric_split_exact = None
    route_c_literal_offending_terms = None
    route_c_literal_equals_symmetric_split = None
    route_c_literal_euler_matches = None
    if coordinates == ("theta", "rho"):
        # Literal Route C current (v5.6.6.3 _bulk_grid_euler_green) with E DEFINED by subtraction.
        t, r = 0, 1
        Ht = Hr = sp.S.Zero
        for a in range(channels):
            Qtt, Qtr, Qrr = Q[a][(0, 0)], Q[a][(0, 1)], Q[a][(1, 1)]
            # v5.6.6.3 differentiates the grid CONTRACTION FIELDS Q.dq (qtt_q = Q_tt_dq etc.), not the momenta alone.
            Ht += P[a][t] * dq0(a) + 2 * Qtt * dq1(a, t) - D(Qtt * dq0(a), t) + Qtr * dq1(a, r) - sp.Rational(1, 2) * D(Qtr * dq0(a), r)
            Hr += P[a][r] * dq0(a) + 2 * Qrr * dq1(a, r) - D(Qrr * dq0(a), r) + Qtr * dq1(a, t) - sp.Rational(1, 2) * D(Qtr * dq0(a), t)
        rest = sp.expand(dL - D(Ht, t) - D(Hr, r))
        offending = sorted(str(sym) for sym in rest.free_symbols if J.inverse.get(sym, ("",))[0] == "d" and len(J.inverse[sym][1][1]) > 0)
        route_c_literal_derivative_free = len(offending) == 0
        route_c_literal_offending_terms = offending
        # Symmetric split with unit diagonal weights.
        Ht2 = Hr2 = sp.S.Zero
        for a in range(channels):
            Qtt, Qtr, Qrr = Q[a][(0, 0)], Q[a][(0, 1)], Q[a][(1, 1)]
            Ht2 += P[a][t] * dq0(a) + Qtt * dq1(a, t) - D(Qtt, t) * dq0(a) + sp.Rational(1, 2) * Qtr * dq1(a, r) - sp.Rational(1, 2) * D(Qtr, r) * dq0(a)
            Hr2 += P[a][r] * dq0(a) + Qrr * dq1(a, r) - D(Qrr, r) * dq0(a) + sp.Rational(1, 2) * Qtr * dq1(a, t) - sp.Rational(1, 2) * D(Qtr, t) * dq0(a)
        rest2 = sp.expand(dL - D(Ht2, t) - D(Hr2, r) - sum(E[a] * dq0(a) for a in range(channels)))
        route_c_symmetric_split_exact = rest2 == 0
        route_c_literal_equals_symmetric_split = sp.expand(Ht - Ht2) == 0 and sp.expand(Hr - Hr2) == 0
        route_c_literal_euler_matches = sp.expand(rest - sum(E[a] * dq0(a) for a in range(channels))) == 0

    jets = sum(1 + n + len(pairs) for _ in range(channels))
    return {
        "coordinates": list(coordinates),
        "channels": channels,
        "independent_jet_variables": jets,
        "identity_dL_equals_E_dq_plus_div_H": bool(identity_ok),
        "residual": str(residual),
        "interface_functional_periodic_IBP_exact": bool(interface_exact),
        "interface_max_tangential_field_derivative_order": int(max(max_tangential_order, field_tangential_order)),
        "interface_max_radial_field_derivative_order": int(max(max_radial_order, field_radial_order)),
        "route_C_literal_current_subtraction_is_derivative_free": route_c_literal_derivative_free,
        "route_C_literal_current_offending_dq_derivatives": route_c_literal_offending_terms,
        "route_C_symmetric_split_representative_exact": route_c_symmetric_split_exact,
        "route_C_literal_current_equals_symmetric_split_identically": route_c_literal_equals_symmetric_split,
        "route_C_literal_subtraction_equals_formal_Euler_operator": route_c_literal_euler_matches,
    }


# --------------------------------------------------------------------------
# (B) radial junction of the declared C2 primitives
# --------------------------------------------------------------------------

def radial_junction_certificate(K_max: int) -> dict[str, Any]:
    rho = sp.Symbol("rho", real=True)
    h0 = 1 - 10 * rho**3 + 15 * rho**4 - 6 * rho**5
    h1 = rho * h0
    envelope = 64 * rho**3 * (1 - rho) ** 3
    z = 2 * rho - 1
    bumps = [sp.expand(envelope * sp.legendre(j, z)) for j in range(K_max)]

    def jets(expr, point):
        return [sp.nsimplify(sp.diff(expr, rho, k).subs(rho, point)) for k in range(3)]

    record = {
        "h0": str(h0),
        "h1": str(h1),
        "bump_envelope": str(envelope),
        "K_max_checked": K_max,
        "h0_jets_rho0": [str(v) for v in jets(h0, 0)],
        "h0_jets_rho1": [str(v) for v in jets(h0, 1)],
        "h1_jets_rho0": [str(v) for v in jets(h1, 0)],
        "h1_jets_rho1": [str(v) for v in jets(h1, 1)],
        "bumps_jets_rho0_all_zero": all(all(v == 0 for v in jets(b, 0)) for b in bumps),
        "bumps_jets_rho1_all_zero": all(all(v == 0 for v in jets(b, 1)) for b in bumps),
        "bumps_third_derivative_rho1_nonzero_count": int(sum(1 for b in bumps if sp.diff(b, rho, 3).subs(rho, 1) != 0)),
    }
    ok = (
        jets(h0, 0) == [1, 0, 0]
        and jets(h0, 1) == [0, 0, 0]
        and jets(h1, 0) == [0, 1, 0]
        and jets(h1, 1) == [0, 0, 0]
        and record["bumps_jets_rho0_all_zero"]
        and record["bumps_jets_rho1_all_zero"]
    )
    record["declared_C2_jets_pass"] = bool(ok)
    # Consequence: every field of the class equals X_inf with zero first and second radial jets at rho=1,
    # so dq, dq_mu, dq_rho vanish at rho=1 and H^rho(1) == 0 term by term (each term is linear in one of them).
    record["outer_current_H_rho_at_1_vanishes_termwise"] = bool(ok)
    record["outer_current_scope"] = "for tangent variations sharing the class profiles; D_rho Q^{rho rho}(1^-) is finite"
    record["class_is_C2_across_zero_extension"] = bool(ok)
    record["second_order_density_regularity_across_rho1"] = "C0 only (third derivatives of h0 and b_j nonzero at rho=1); no distribution in S or DS"
    record["class_is_C3_across_zero_extension"] = bool(record["bumps_third_derivative_rho1_nonzero_count"] == 0)
    return record


# --------------------------------------------------------------------------
# (C) uniform-in-N stability audit of the declared collocation
# --------------------------------------------------------------------------

def declared_wavevectors(N: int) -> list[tuple[int, int, int, int]]:
    priority = [(1, 1, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    wavevectors: list[tuple[int, int, int, int]] = []
    for vector in priority:
        if vector not in wavevectors:
            wavevectors.append(vector)
    radius = 1
    while len(wavevectors) < max(1, N // 2):
        candidates = []
        for vector in itertools.product(range(-radius, radius + 1), repeat=4):
            if vector == (0, 0, 0, 0) or max(map(abs, vector)) != radius:
                continue
            first = next(item for item in vector if item != 0)
            if first < 0:
                continue
            candidates.append(vector)
        for vector in sorted(candidates, key=lambda item: (sum(map(abs, item)), item)):
            if vector not in wavevectors:
                wavevectors.append(vector)
        radius += 1
    return wavevectors


def declared_collocation_matrix(N: int) -> tuple[np.ndarray, list[str]]:
    wavevectors = declared_wavevectors(N)
    irrational = np.sqrt(np.asarray((2.0, 3.0, 5.0, 7.0)))
    points = 2.0 * math.pi * np.mod((np.arange(N, dtype=float)[:, None] + 0.173) * irrational[None, :], 1.0)
    labels = ["1"]
    columns = [np.ones(N)]
    for index in range(1, N):
        vector = np.asarray(wavevectors[(index - 1) // 2], dtype=float)
        phase = points @ vector
        cosine_mode = index % 2 == 1
        labels.append(("cos" if cosine_mode else "sin") + "(" + "+".join(f"{int(k)}*x{mu}" for mu, k in enumerate(vector) if k) + ")")
        columns.append(np.cos(phase) if cosine_mode else np.sin(phase))
    return np.stack(columns, axis=-1), labels


def collocation_stability_audit(N_max: int) -> dict[str, Any]:
    rows = []
    worst_condition = 0.0
    worst_lebesgue = 0.0
    first_alert_N = None
    first_condition_alert_N = None
    worst_condition_N = None
    for N in range(1, N_max + 1):
        V, _ = declared_collocation_matrix(N)
        cond = float(np.linalg.cond(V))
        inv = np.linalg.inv(V)
        lebesgue = float(np.abs(inv).sum(axis=0).max())
        if cond > worst_condition:
            worst_condition, worst_condition_N = cond, N
        worst_lebesgue = max(worst_lebesgue, lebesgue)
        if first_alert_N is None and (cond > STABILITY_ALERT_CONDITION or lebesgue > STABILITY_ALERT_LEBESGUE):
            first_alert_N = N
        if first_condition_alert_N is None and cond > STABILITY_ALERT_CONDITION:
            first_condition_alert_N = N
        if N <= 12 or N % 8 == 0 or N == N_max:
            rows.append({"N": N, "condition_number": cond, "lebesgue_constant_inf": lebesgue})
    # Contrast: tensor equispaced 1-D trigonometric collocation is uniformly stable (unitary up to scale).
    contrast = []
    for M in (8, 32, 128):
        x = 2.0 * math.pi * np.arange(M) / M
        cols = [np.ones(M)]
        for k in range(1, M // 2 + 1):
            cols.append(np.cos(k * x))
            if len(cols) < M:
                cols.append(np.sin(k * x))
        V = np.stack(cols[:M], axis=-1)
        contrast.append({"M": M, "condition_number": float(np.linalg.cond(V))})
    return {
        "N_max": N_max,
        "alert_thresholds": {"condition_number": STABILITY_ALERT_CONDITION, "lebesgue_constant_inf": STABILITY_ALERT_LEBESGUE},
        "first_alert_N": first_alert_N,
        "first_condition_alert_N": first_condition_alert_N,
        "worst_condition_number": worst_condition,
        "worst_condition_number_N": worst_condition_N,
        "worst_lebesgue_constant_inf": worst_lebesgue,
        "lebesgue_constant_definition": (
            "max column sum of |V^{-1}| (a cheap proxy that LOWER-bounds the true Lebesgue constant of the nested "
            "trigonometric interpolation on T^4; the sampled true constant is larger)"
        ),
        "mechanism": (
            "On the Kronecker sequence x_n = 2*pi*frac((n+0.173)*alpha) every 4-D mode k collapses to the 1-D frequency "
            "k.alpha mod 1, so V is a non-harmonic 1-D Vandermonde whose conditioning is governed by the minimal "
            "frequency gap times N; radius-2 modes enter at N = 82 and the gap shrinks with N."
        ),
        "sampled_rows": rows,
        "equispaced_1d_contrast": contrast,
        "declared_collocation_uniformly_stable": bool(first_alert_N is None),
    }


# --------------------------------------------------------------------------
# (D) off-collocation gluing defects of the byte-pinned members (bundle diagnostics)
# --------------------------------------------------------------------------

def _decode_f64le(block: Mapping[str, Any]) -> np.ndarray:
    raw = np.frombuffer(base64.b64decode(block["data"]), dtype=block["dtype"])
    return raw.reshape(block["shape"]) if "shape" in block else raw


def off_collocation_gluing_audit(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Maximum raw gluing defect of the pinned members at the bundle's off-collocation points.

    The v5.6.4.2 common-first pointwise decoder eliminates the lateral traces algebraically at
    every evaluator node, so the gluing constraint is satisfied pointwise (not only at the N
    Kronecker nodes).  These defects are read from the byte-pinned bundle, not recomputed.
    """

    rows = []
    worst = 0.0
    for N, record in sorted(bundle["off_collocation_validation_by_N"].items(), key=lambda kv: int(kv[0])):
        points = _decode_f64le(record["points_f64le"])
        member_worst = 0.0
        for diagnostic in record["raw_pointwise_gluing_diagnostics"]:
            for blocks in diagnostic["raw_defects_f64le"].values():
                for block in blocks.values():
                    member_worst = max(member_worst, float(np.max(np.abs(_decode_f64le(block)))))
        rows.append({"N": int(N), "off_collocation_points": int(points.shape[0]), "max_abs_gluing_defect": member_worst})
        worst = max(worst, member_worst)
    return {
        "tolerance": OFF_COLLOCATION_GLUING_TOLERANCE,
        "rows": rows,
        "worst_max_abs_gluing_defect": worst,
        "members_glued_pointwise": bool(worst <= OFF_COLLOCATION_GLUING_TOLERANCE),
        "reading": (
            "The pinned N=1,2,3 members satisfy G(X)=0 at machine precision away from the Kronecker nodes because the "
            "common-first decoder solves the trace variables explicitly; the collocation inverse is not used by the "
            "decoder. The exporter pipeline that GENERATED the bundle primitives did use the v5.6.4 ambient<->free codec "
            "(and therefore the inverse), but only at N = 1,2,3 where the condition number is <= 8.4, so numerically "
            "innocuous. The measured Kronecker instability therefore bears on the coefficient-chart gluing_map/kernel "
            "machinery of v5.6.4 (tangent generation, ambient<->free codec, runtime_DG), not on the pointwise class "
            "membership of the pinned members."
        ),
    }


# --------------------------------------------------------------------------
# theorem statement
# --------------------------------------------------------------------------

def theorem_statement() -> dict[str, Any]:
    return {
        "class": (
            "Restricted C2 spectral class: on each oriented collar {rho in [0,1]} x T^4 every one of the 64 channels "
            "X (g_MN, log Omega, phi_a, A_Ma, B_MNPa) is X(rho,x) = X_inf + h0(rho)(X0(x)-X_inf) + h1(rho) J1(x) "
            "+ sum_{j<K} b_j(rho) C_j(x), with X0, J1, C_j in H^s(T^4), s = 4.75 > 2 + d/2 = 4, d = 4, extended by X_inf for rho >= 1; "
            "common base (gamma, T, Omega_Sigma, varphi_H, A_Sigma) in H^s(T^4); embeddings Y_+- in H^{s+1}; relative rotations "
            "r_+- and the frame parameters q_Q in H^{s+1} (their first derivatives enter the eliminated connection trace, "
            "so H^s alone would leave A in H^{s-1} and break the classical second jets of the connection channel) with |r| "
            "below the cut locus (a chart condition for the SO(3) log, not an analyticity condition); "
            "gluing G(X) = 0 holds pointwise on T^4. CLASS DRIFT, stated on purpose: the v5.6.4 contract uses exp-flat "
            "C-infinity profiles and imposes G only at N Kronecker nodes, so its nodal members C_N are NOT elements of "
            "this class; the v5.6.4.4 common-first members are class points, but the explicit elimination of the lateral "
            "traces (nonlinear in R) pushes them outside the finite spectral space V_N, so they are continuum-class points, "
            "not spectral-family points."
        ),
        "norm": (
            "||X||^2 = ||X0||_{H^s}^2 + ||J1||_{H^s}^2 + sum_j (1+j^2)^4 ||C_j||_{H^s}^2 + base and embedding norms. "
            "The (1+|k|^2)^{-4} amplitude envelope of the certificate lies in H^s(T^4) for every s < 6 (d = 4), so it is "
            "compatible with s = 4.75; H^4 itself would be critical and does not embed in C^2."
        ),
        "margins": (
            "Omega >= 0.5, timelike khronon margin 0.2, signature eigenvalue margin 0.02 for g and the induced metric, "
            "rotation cut-locus margin 1.0: an open set U_margin in the C0 jet space on which the literal v5.2 density "
            "is real-analytic in (q, q_i, q_ij) (its only non-polynomial operations are exp, powers of Omega, "
            "1/det g, sqrt(-g), sqrt(1+r^4), the SO(3) exponential of r, and the khronon normalisation). "
            "Real-analyticity is asserted from the structure of the literal action, not machine-checked here; the "
            "integration by parts producing G needs L in C^2 of the jets, which analyticity provides. The pinned members "
            "are known to satisfy the margins only at the N nodes x 7 radial samples checked by v5.6.4."
        ),
        "part_i_exact_identity": (
            "For X in the class inside the margins and dX tangent (constraint preserving, compactly supported by the "
            "zero extension), the Gateaux derivative DS_rel[X].dX exists and equals the collar integral of "
            "C.dq + P^i dq_i + Q^{ij} dq_ij (chain rule: L is C^1 in jets, the jets are classical because "
            "H^s(T^4) embeds in C^2 for s > 4 and the radial profiles are polynomials). By (A) this equals "
            "int_collar E_weak.dq + G[dq] with G the interface functional at rho = 0 and the rho = 1 current "
            "identically zero by (B). E_weak is the distribution defined by this identity; it coincides with the "
            "formal fourth-order Euler operator E pointwise on the open collar (0,1) x T^4 for s > 6; at rho = 1 the formal "
            "E carries a delta layer (the density is only C^0 there) that tangent variations annihilate, so no C^4 "
            "subclass across rho = 1 exists or is needed. E_weak is a functional on the tangent space of the class, "
            "not a distribution on the collar (the radial tangent space is (K+2)-dimensional). Orientation: with the "
            "bundle contract n_out = -d/drho at rho = 0, int_0^1 D_rho H^rho drho = H^rho(1) - H^rho(0) = -H^rho(0), "
            "so DS_rel[X].dX = int_collar E_weak.dq - int_{T^4} H^rho(0) dx and G[dq] := -int_{T^4} H^rho(0) dx "
            "(equivalently the boundary term of the radial-only integration by parts). Tangential faces cancel "
            "exactly by periodicity of T^4."
        ),
        "part_ii_continuity": (
            "On the ball ||X|| <= M inside the margins, jets are bounded in C^0 by c_s M (Sobolev embedding) and the "
            "density is real-analytic on the compact closure of the jet range, so C, P, Q are Lipschitz in the jets. "
            "Hence |DS_rel[X].dX - DS_rel[X'].dX'| <= C(M) (||X - X'|| + ||dX - dX'||) and "
            "||G[X] - G[X']|| <= C(M) ||X - X'|| with C(M) finite (Moser composition estimates, s > d/2). "
            "This is an analytic argument recorded here with its hypotheses; it is not machine-checked and no numerical "
            "value of C(M) is claimed."
        ),
        "part_iii_convergence_on_the_continuum_class": (
            "For X in the class, the Fourier truncations P_N X converge to X in the class norm, and by (ii) "
            "S_rel(P_N X) -> S_rel(X) and DS_rel[P_N X] -> DS_rel[X], PROVIDED the projected point is re-glued: P_N acts on "
            "the free data (X0, J1, C_j, base, Y, r) and the lateral traces are then eliminated explicitly, since a "
            "naive Fourier truncation of a glued point leaves the class. This is convergence of the exact functional "
            "along re-glued projections; it says nothing about the v5.6.4 nodal members C_N, whose gluing is imposed "
            "only at N Kronecker nodes (see (C))."
        ),
        "what_remains": (
            "A uniformly stable finite discretization of the gluing map (Galerkin projection, or tensor equispaced "
            "FFT collocation with an aliasing-controlled quadrature) so that DG_N admits a right inverse bounded "
            "uniformly in N; only then can the finite Stokes certificates of v5.6.6.x be lifted to the continuum "
            "identity of part (i) with a rate. Periodic-box exhaustion to noncompact Sigma remains a separate, "
            "still-open key."
        ),
    }


def build_payload() -> dict[str, Any]:
    bundle = _load_json(BUNDLE_PATH, BUNDLE_SHA256)
    v5667 = _load_json(V5667_PATH, V5667_SHA256)
    if v5667["decision"].get("uniform_N_to_infinity_bridge_pass") is not False:
        raise EulerGreenGateError("upstream v5.6.6.7 must leave the bridge open")

    symbolic = [symbolic_euler_green_case(tuple(case["coordinates"]), case["channels"]) for case in SYMBOLIC_CASES]
    radial = radial_junction_certificate(RADIAL_K_MAX)
    stability = collocation_stability_audit(N_MAX_STABILITY)
    off_collocation = off_collocation_gluing_audit(bundle)

    # Cross-check the re-implemented enumeration against the byte-pinned bundle labels.
    labels_by_N = bundle["nested_truncations"]["basis_labels_by_N"]
    label_match = all(declared_collocation_matrix(int(N))[1] == list(labels) for N, labels in labels_by_N.items())
    profile_match = (
        bundle["radial_profile_correction"]["h0"] == "1-10*rho^3+15*rho^4-6*rho^5"
        and bundle["radial_profile_correction"]["interior_envelope"] == "64*rho^3*(1-rho)^3"
    )

    identity_all = all(case["identity_dL_equals_E_dq_plus_div_H"] for case in symbolic)
    interface_all = all(case["interface_functional_periodic_IBP_exact"] for case in symbolic)
    jet_order_ok = all(
        case["interface_max_tangential_field_derivative_order"] <= 2 and case["interface_max_radial_field_derivative_order"] <= 3
        for case in symbolic
    )
    route_c_cases = [case for case in symbolic if case["route_C_symmetric_split_representative_exact"] is not None]
    route_c_ok = all(case["route_C_symmetric_split_representative_exact"] for case in route_c_cases)
    route_c_literal_ok = all(
        case["route_C_literal_current_subtraction_is_derivative_free"]
        and case["route_C_literal_current_equals_symmetric_split_identically"]
        and case["route_C_literal_subtraction_equals_formal_Euler_operator"]
        for case in route_c_cases
    )

    generic_identity_pass = bool(identity_all and interface_all and jet_order_ok and radial["declared_C2_jets_pass"] and label_match and profile_match)

    scientific = {
        "theorem": theorem_statement(),
        "symbolic_euler_green": symbolic,
        "radial_junction": radial,
        "collocation_stability": stability,
        "off_collocation_gluing": off_collocation,
        "bundle_cross_check": {"basis_labels_match_bundle": label_match, "radial_profiles_match_bundle": profile_match},
        "machine_checked": {
            "algebraic_identity_all_cases": identity_all,
            "interface_functional_after_periodic_IBP": interface_all,
            "interface_jet_orders_within_class_regularity": jet_order_ok,
            "route_C_symmetric_split_representative_exact": route_c_ok,
            "route_C_literal_current_is_Euler_operator_representative": route_c_literal_ok,
            "radial_C2_junction": radial["declared_C2_jets_pass"],
            "collocation_growth_measured": True,
            "bundle_members_glued_pointwise_off_collocation": off_collocation["members_glued_pointwise"],
        },
        "route_C_observation": {
            "current": "literal v5.6.6.3 current == unit-diagonal symmetric-split representative (product rule on contraction fields)",
            "Euler_contraction": "subtraction-defined E.dq equals the formal Euler operator contraction exactly (symbolic)",
            "Stokes_residual": "direct - (Euler_integral + radial_Green) is a discrete divergence-theorem identity, independent of the action; not evidence about the action",
            "action_sensitive_checks_in_route_C": ["chain_residual (free_direct vs chain_direct)", "three-way AD/FD5/Route C first-variation comparison (v5.6.6.6)"],
        },
        "analytic_only": {
            "restricted_class_action_identity_theorem_recorded": True,
            "literal_v5_2_density_analyticity_checked": False,
            "continuity_bound_hypotheses_recorded": True,
            "sobolev_continuity_bound": "stated with hypotheses; not machine-checked; no numeric C(M)",
            "exact_functional_convergence_along_reglued_Fourier_projections": "follows from the continuity bound",
            "why_the_v5_6_4_key_stays_False": (
                "restricted_family_exact_action_identity_pass is a v5.6.4 FAIL_CLOSED key about the nodal exp-profile "
                "family and the literal v5.2 action; this gate machine-checks only a generic-density identity and the "
                "polynomial radial jets, so that key is not discharged here."
            ),
        },
    }

    decision = {
        "generic_second_order_Euler_Green_identity_symbolic_pass": generic_identity_pass,
        "restricted_family_exact_action_identity_pass": False,
        "outer_radial_Green_form_vanishes_exactly_pass": bool(radial["outer_current_H_rho_at_1_vanishes_termwise"]),
        "route_C_literal_current_is_Euler_operator_representative_pass": bool(route_c_literal_ok),
        "declared_collocation_uniform_stability_pass": bool(stability["declared_collocation_uniformly_stable"]),
        "bundle_members_glued_pointwise_off_collocation_pass": bool(off_collocation["members_glued_pointwise"]),
        "uniform_N_to_infinity_bridge_pass": False,
        "spectral_N_convergence_pass": False,
        "uniform_stability_pass": False,
        "periodic_box_exhaustion_and_tail_control_pass": False,
        "density_union_C_N_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
    }

    payload = {
        "schema": SCHEMA,
        "classification": "theory_only;symbolic_identity;restricted_spectral_family;negative_collocation_stability;fail_closed_bridge",
        "decision": decision,
        "fixed_before_run": {
            "SOBOLEV_S": SOBOLEV_S,
            "SPECTRAL_DECAY_POWER": SPECTRAL_DECAY_POWER,
            "N_MAX_STABILITY": N_MAX_STABILITY,
            "STABILITY_ALERT_CONDITION": STABILITY_ALERT_CONDITION,
            "STABILITY_ALERT_LEBESGUE": STABILITY_ALERT_LEBESGUE,
            "RADIAL_K_MAX": RADIAL_K_MAX,
            "symbolic_cases": [dict(case, coordinates=list(case["coordinates"])) for case in SYMBOLIC_CASES],
        },
        "scientific": scientific,
        "independence_boundary": {
            "scientific_inputs": "declared class definition (bundle contract strings and labels) and the literal v5.2 action structure only",
            "imports_action_evaluators": False,
            "imports_one_omega_modules": False,
            "reads_upstream_expected_values": False,
            "symbolic_engine": f"sympy {sp.__version__}",
        },
        "negative_result": {
            "declared_Kronecker_collocation": (
                "The N x N collocation matrix of the declared nested real Fourier basis at the Kronecker nodes has "
                f"condition number up to {stability['worst_condition_number']:.3e} and Lebesgue constant up to "
                f"{stability['worst_lebesgue_constant_inf']:.3e} for N <= {N_MAX_STABILITY} (first alert at N = "
                f"{stability['first_alert_N']}). In the v5.6.4 coefficient chart G_N is pushed to coefficients through "
                "this inverse, so DG_N has no right inverse bounded uniformly in N there. SCOPE: this obstructs the "
                "coefficient-chart formulation (kernel/tangent generation and the ambient<->free codec of v5.6.4); the "
                "v5.6.4.2 common-first pointwise decoder consumed by Route C eliminates the traces explicitly and the "
                f"pinned members are glued pointwise to {off_collocation['worst_max_abs_gluing_defect']:.1e}. The finite "
                "N = 1,2,3 receipts are unaffected (condition <= 8.4). Preserved as a red witness for any uniform-in-N "
                "claim made in the coefficient chart."
            )
        },
        "open_obligation": {
            "uniformly_stable_discretization": "for tangent generation and the ambient<->free codec, replace the Kronecker collocation inverse by Galerkin or tensor equispaced FFT projection, or certify the explicit common-first elimination as the retraction for all N (theorem part iii) and bound it uniformly",
            "finite_to_continuum_rate": "with a stable discretization, prove ||P_N X - X_N|| -> 0 for collocation-glued members and lift the Stokes certificates to part (i)",
            "periodic_box_exhaustion": "unchanged",
        },
        "evidence_boundary": (
            "Machine-checked: the exact second-order Euler--Green identity for arbitrary second-order densities on the "
            "collar, the admissibility of the Route C current, the interface functional needing only second tangential "
            "jets, and the C2 radial junction that kills the outer current. Stated with hypotheses: the Sobolev continuity "
            "bound on the declared class. Measured negative: the declared collocation is not uniformly stable. "
            "This does not prove the N-to-infinity bridge and does not authorize C1/N1 or B4/B5."
        ),
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "v5_6_6_7_receipt_sha256": V5667_SHA256,
        },
        "provenance": {
            "generator": {"path": str(Path(__file__).resolve().relative_to(REPO)), "sha256": _sha256(Path(__file__))},
            "test": {"path": str(TEST.relative_to(REPO)), "sha256": _sha256(TEST) if TEST.exists() else None},
            "python": platform.python_version(),
            "numpy": np.__version__,
            "sympy": sp.__version__,
        },
        "scientific_payload_sha256": _canonical_sha256(scientific),
    }
    return payload


def main() -> None:
    payload = build_payload()
    if not payload["decision"]["generic_second_order_Euler_Green_identity_symbolic_pass"]:
        raise EulerGreenGateError("generic Euler--Green identity certificate failed")
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    d = payload["decision"]
    print(
        f"identity={d['generic_second_order_Euler_Green_identity_symbolic_pass']} "
        f"outer_green_zero={d['outer_radial_Green_form_vanishes_exactly_pass']} "
        f"collocation_stable={d['declared_collocation_uniform_stability_pass']} "
        f"bridge={d['uniform_N_to_infinity_bridge_pass']}"
    )


if __name__ == "__main__":
    main()
