#!/usr/bin/env python3
"""Common-first gluing as the graph of an explicit analytic map: the N-independent
retraction that the continuum bridge needs (v5.6.6.9).

The v5.6.6.8 receipt measured that the declared Kronecker collocation of v5.6.4 is
not uniformly stable in N, so no uniform right inverse of DG_N exists in the
coefficient chart, and observed that the v5.6.4.2 common-first pointwise decoder
never uses that inverse.  This gate turns the observation into a certificate.

(A) Graph structure (symbolic, sympy).  With the free data
      gamma (10), Y_mu = d_mu Y (4), d_mu (4), a (1), varphi_H (3), A_Sigma (4x3),
      R in SO(3) (exact Cayley parametrisation), dR_mu = D_mu R, A_perp (3),
    the eliminated traces
      g_{mu nu} = gamma_{mu nu} - d_mu Y_nu - Y_mu d_nu + a Y_mu Y_nu,
      g_{mu 4}  = d_mu - a Y_mu,   g_44 = a,
      phi       = R^T varphi_H,
      A_source,mu = vee(R^T hat(A_Sigma,mu) R + R^T dR_mu),
      A_mu = A_source,mu - Y_mu A_perp,   A_4 = A_perp,
    satisfy every row of the gluing map identically:
      t^T g t = gamma  (t = (I_4 ; Y_mu)),   R phi = varphi_H,
      R hat(Y*A_mu) R^T - dR_mu R^T = hat(A_Sigma,mu)   with Y*A_mu = A_mu + Y_mu A_4.
    Hence the pointwise-glued class is the graph of Phi: free data -> traces, an
    explicit map built from polynomials, R and R^T dR.  Phi does not depend on N.

(B) N-independent Lipschitz bound.  With M the maximum absolute entry of ALL
    free data (gamma, Y_mu, d_mu, a, varphi_H, A_Sigma, A_perp, k, kappa_mu,
    log Omega), the pointwise Jacobian of Phi is bounded in operator norm by an
    explicit polynomial B(M), obtained as the sum of block-wise Frobenius
    bounds (docstring of lipschitz_bound_terms).  The bound is checked on a
    random ball, on single-coordinate spikes at three scales and on random
    corners at three scales (tiny, large, larger).  Because Phi is pointwise
    and N-free, the bound is uniform in N by construction: this is the
    retraction of part (iii) of the v5.6.6.8 theorem in the continuum
    re-glued formulation.  It is NOT the finite DG_N obligation on V_N.

(C) What still uses the Kronecker inverse in v5.6.4 (recorded, not repaired):
    gluing_map, ambient_to_free_coordinates, retract_ambient_point, the frame
    gauge action feeding runtime_SO3_gauge_tangents, runtime_DG.  None of them
    is needed in the pointwise formulation, whose tangent space is the graph of
    dPhi applied to free tangents.

The Sobolev lift ||Phi(u)||_{H^s} <= C_s(||u||_inf) ||u||_{H^s} (Moser, s > 2) is
an analytic argument recorded as such.  This gate does not prove the quadrature
convergence of the finite Route C certificates and does not flip
uniform_N_to_infinity_bridge_pass, C1/N1, B4/B5 or any v5.6.4 fail-closed key.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_common_first_explicit_retraction_v5_6_6_9.json"
TEST = HERE / "test_one_omega_topological_so3_common_first_explicit_retraction_v5_6_6_9.py"
SCHEMA = "holo.one-omega-topological-so3-common-first-explicit-retraction-v5-6-6-9.v1"

FROZEN_COMMIT = "ea014fd1a8ed124c353058eb6f0a1c92b90353bc"
V5642_DECODER_PATH = HERE / "export_one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitives.py"
V5642_DECODER_SHA256 = "4b7eda150cf2d22e04ef2b1b04391c31dc9e618839d7ead9e74a540371ab3d7f"
V564_CERTIFICATE_PATH = HERE / "derive_one_omega_topological_so3_restricted_spectral_family_v5_6_4_certificate.py"
V564_CERTIFICATE_SHA256 = "198808b829a708ca9bc0314bfc5db235317f42eb48aa8f17ced6070cc3c87b7e"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
V5668_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.json"
V5668_SHA256 = "175dae746dcbf19854d1bdb6e0b6b5541d3eb18acea0050d41fccd444f197091"

# Fixed before run.
SAMPLES = 400
SAMPLE_SEED = 20260904
SAMPLE_RADIUS = 1.5
JACOBIAN_TOLERANCE = 1.0e-9
FD_STEP = 1.0e-6
GRAPH_RESIDUAL_TOLERANCE = 1.0e-11
# v5.6.4 functions expected to touch the Kronecker collocation inverse (statically checked below on the pinned source):
KRONECKER_INVERSE_USERS_V5_6_4 = (
    "gluing_map",
    "ambient_to_free_coordinates",
    "construct_ambient_point",
    "retract_ambient_point",
    "finite_frame_gauge_action",
    "runtime_SO3_gauge_tangents",
    "runtime_DG",
)


class RetractionGateError(RuntimeError):
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
        raise RetractionGateError(f"byte pin drift for {path.name}: {digest} != {expected_sha256}")
    return json.loads(path.read_text())


# --------------------------------------------------------------------------
# so(3) helpers (symbolic and numeric)
# --------------------------------------------------------------------------

def _hat(v):
    return sp.Matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def _vee(m):
    return sp.Matrix([m[2, 1], m[0, 2], m[1, 0]])


def _cayley(k):
    """Exact rational SO(3) element from three parameters: (I-K)^{-1}(I+K)."""

    K = _hat(k)
    I = sp.eye(3)
    return (I - K).inv() * (I + K)


def _hat_np(v):
    return np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])


def _vee_np(m):
    return np.array([m[2, 1], m[0, 2], m[1, 0]])


def _cayley_np(k):
    K = _hat_np(k)
    I = np.eye(3)
    return np.linalg.solve(I - K, I + K)


# --------------------------------------------------------------------------
# (A) graph structure
# --------------------------------------------------------------------------

def graph_structure_certificate() -> dict[str, Any]:
    gamma_syms = {(m, n): sp.Symbol(f"gamma{m}{n}") for m in range(4) for n in range(m, 4)}
    gamma = sp.Matrix(4, 4, lambda m, n: gamma_syms[(min(m, n), max(m, n))])
    Y = sp.Matrix(sp.symbols("Y0:4"))
    d = sp.Matrix(sp.symbols("d0:4"))
    a = sp.Symbol("a")

    # metric elimination
    g = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            g[m, n] = gamma[m, n] - d[m] * Y[n] - Y[m] * d[n] + a * Y[m] * Y[n]
        g[m, 4] = d[m] - a * Y[m]
        g[4, m] = g[m, 4]
    g[4, 4] = a
    t = sp.zeros(5, 4)
    t[:4, :] = sp.eye(4)
    t[4, :] = Y.T
    metric_row = sp.expand(t.T * g * t - gamma)
    metric_ok = metric_row == sp.zeros(4, 4)
    # degrees of the eliminated metric in the free data
    poly_vars = list(gamma_syms.values()) + list(Y) + list(d) + [a]
    degrees = {"Y": 0, "d": 0, "a": 0, "gamma": 0}
    for m in range(5):
        for n in range(5):
            P = sp.Poly(g[m, n], *poly_vars)
            for mono, _ in P.terms():
                degY = sum(mono[len(gamma_syms):len(gamma_syms) + 4])
                degd = sum(mono[len(gamma_syms) + 4:len(gamma_syms) + 8])
                dega = mono[-1]
                degg = sum(mono[:len(gamma_syms)])
                degrees["Y"] = max(degrees["Y"], degY)
                degrees["d"] = max(degrees["d"], degd)
                degrees["a"] = max(degrees["a"], dega)
                degrees["gamma"] = max(degrees["gamma"], degg)

    # rotation, scalar row
    k = sp.Matrix(sp.symbols("k0:3"))
    R = sp.simplify(_cayley(k))
    orthogonal = sp.simplify(R.T * R - sp.eye(3)) == sp.zeros(3, 3)
    det_one = sp.simplify(R.det()) == 1
    varphi = sp.Matrix(sp.symbols("vphi0:3"))
    phi = R.T * varphi
    phi_row_ok = sp.simplify(R * phi - varphi) == sp.zeros(3, 1)

    # connection row along one tangential direction mu with a generic derivative direction kappa
    kappa = sp.Matrix(sp.symbols("kappa0:3"))
    dR = sp.zeros(3, 3)
    for i in range(3):
        dR += sp.diff(R, k[i]) * kappa[i]
    dR = sp.simplify(dR)
    skew = sp.simplify(R.T * dR + (R.T * dR).T) == sp.zeros(3, 3)
    A_Sigma = sp.Matrix(sp.symbols("AS0:3"))
    A_perp = sp.Matrix(sp.symbols("Ap0:3"))
    Ymu = sp.Symbol("Ymu")
    A_source = _vee(R.T * _hat(A_Sigma) * R + R.T * dR)
    A_mu = A_source - Ymu * A_perp
    pulled = A_mu + Ymu * A_perp  # Y*A_mu = A_mu + d_mu Y A_4 with A_4 = A_perp
    connection_row = sp.simplify(R * _hat(pulled) * R.T - dR * R.T - _hat(A_Sigma))
    connection_ok = connection_row == sp.zeros(3, 3)
    pullback_ok = sp.simplify(pulled - A_source) == sp.zeros(3, 1)

    return {
        "metric_row_vanishes_identically": bool(metric_ok),
        "eliminated_metric_polynomial_degrees": degrees,
        "cayley_R_orthogonal": bool(orthogonal),
        "cayley_R_det_one": bool(det_one),
        "RT_dR_skew_symmetric": bool(skew),
        "scalar_row_vanishes_identically": bool(phi_row_ok),
        "connection_row_vanishes_identically": bool(connection_ok),
        "pullback_consistency": bool(pullback_ok),
        "log_Omega_row": "identity (log_Omega_trace := log Omega_Sigma)",
        "map_depends_on_N": False,
        "map_operations": ["polynomials in (gamma, Y, d, a)", "R^T varphi", "R^T hat(.) R", "R^T dR (skew)", "vee"],
    }


# --------------------------------------------------------------------------
# (B) N-independent Lipschitz bound with a numeric witness
# --------------------------------------------------------------------------
#
# Free data vector u (53 entries):  gamma (10, packed upper triangle), Y_mu (4), d_mu (4), a (1),
# varphi_H (3), A_Sigma,mu (4x3 = 12), A_perp (3), k (3, Cayley chart of R), kappa_mu (4x3 = 12, so that
# dR_mu = (dR/dk) . kappa_mu), log_Omega_Sigma (1).
# Output Phi(u) (34 entries): g (15 packed), phi (3), A_mu (12), A_4 (3), log_Omega_trace (1).
# M := max |u_i| over ALL entries.  The bound is a sum of Frobenius bounds of the Jacobian blocks, each
# entry bounded by an explicit monomial in M, using |R|_2 = 1, |(I-K)^{-1}|_2 <= 1 (eigenvalues 1 +- i|k|),
# |dR/dk_i|_2 <= 2, |d(I-K)^{-1}/dk_i|_2 <= 1, |vee(S)|_2 = |S|_F/sqrt(2) for skew S, |hat(v)|_2 = |v|_2,
# |v|_2 <= sqrt(3) M for 3-vectors, and ||J||_2 <= ||J||_F <= sum of block Frobenius norms.

U_SIZE = 53
OUT_SIZE = 34
_SL = {
    "gamma": slice(0, 10), "Y": slice(10, 14), "d": slice(14, 18), "a": slice(18, 19), "varphi": slice(19, 22),
    "A_Sigma": slice(22, 34), "A_perp": slice(34, 37), "k": slice(37, 40), "kappa": slice(40, 52), "log_Omega": slice(52, 53),
}


def _unpack(u: np.ndarray) -> dict[str, Any]:
    if u.shape != (U_SIZE,):
        raise RetractionGateError("free data size drift")
    gamma = np.zeros((4, 4))
    gamma[np.triu_indices(4)] = u[_SL["gamma"]]
    gamma = gamma + gamma.T - np.diag(np.diag(gamma))
    return {
        "gamma": gamma,
        "Y": u[_SL["Y"]],
        "d": u[_SL["d"]],
        "a": float(u[_SL["a"]][0]),
        "varphi": u[_SL["varphi"]],
        "A_Sigma": u[_SL["A_Sigma"]].reshape(4, 3),
        "A_perp": u[_SL["A_perp"]],
        "k": u[_SL["k"]],
        "kappa": u[_SL["kappa"]].reshape(4, 3),
        "log_Omega": float(u[_SL["log_Omega"]][0]),
    }


def _phi_numeric(u: np.ndarray) -> np.ndarray:
    f = _unpack(u)
    gamma, Y, d, a = f["gamma"], f["Y"], f["d"], f["a"]
    g = np.empty((5, 5))
    g[:4, :4] = gamma - np.outer(d, Y) - np.outer(Y, d) + a * np.outer(Y, Y)
    g[:4, 4] = d - a * Y
    g[4, :4] = g[:4, 4]
    g[4, 4] = a
    R = _cayley_np(f["k"])
    K = _hat_np(f["k"])
    Minv = np.linalg.inv(np.eye(3) - K)
    phi = R.T @ f["varphi"]
    A_mu = np.empty((4, 3))
    for mu in range(4):
        dR = 2.0 * Minv @ _hat_np(f["kappa"][mu]) @ Minv  # exact derivative of the Cayley map along kappa_mu
        A_source = _vee_np(R.T @ _hat_np(f["A_Sigma"][mu]) @ R + R.T @ dR)
        A_mu[mu] = A_source - Y[mu] * f["A_perp"]
    out = np.concatenate((g[np.triu_indices(5)], phi, A_mu.reshape(-1), f["A_perp"], [f["log_Omega"]]))
    if out.shape != (OUT_SIZE,):
        raise RetractionGateError("output size drift")
    return out


def lipschitz_bound_terms(M: float) -> dict[str, float]:
    """Explicit block-wise Frobenius bounds of dPhi for free data with max-entry size <= M (no N anywhere).

    metric block g (15 outputs):
      d g_{mu nu}/d gamma: 10 unit entries                      -> sqrt(10)
      d g_{mu nu}/d d_rho = -(delta Y + Y delta):  |.| <= 2M, 40 entries -> sqrt(40) 2M
      d g_{mu nu}/d a = Y_mu Y_nu:                 |.| <= M^2, 10 entries -> sqrt(10) M^2
      d g_{mu nu}/d Y_rho:                          |.| <= 2M + 2M^2, 40 entries -> sqrt(40)(2M + 2M^2)
      d g_{mu 4}/d d = I (4 entries) -> 2;  d g_{mu 4}/d a = -Y -> 2M;  d g_{mu 4}/d Y = -a I -> 2M;  d g_44/d a -> 1
    scalar block phi = R^T varphi (3 outputs):
      d phi/d varphi = R^T -> |.|_F = sqrt(3);  d phi/d k_i = (d_i R)^T varphi, |.|_2 <= 2 sqrt(3) M, 3 columns -> 6M
    connection block A_mu (12 outputs), per mu:
      d A_mu/d A_Sigma,mu = Ad(R^T): |.|_F = sqrt(3) per mu -> 2 sqrt(3)
      d A_mu/d kappa_mu = kappa -> vee(R^T 2 Minv hat(kappa) Minv): |.|_2 <= 2, |.|_F <= 2 sqrt(3) per mu -> 4 sqrt(3)
      d A_mu/d k_i: from R^T hat(A) R: |.|_2 <= (2 |d_i R| |A|)/sqrt(2) <= 2 sqrt(6) M;
                    from R^T dR: |(d_i R)^T dR| <= 2 * 2 sqrt(3) M and |R^T d_i dR| <= 2 * 2 * sqrt(3) M, /sqrt(2) -> 4 sqrt(6) M;
                    per (mu, i) column norm <= 6 sqrt(6) M, 12 columns -> sqrt(12) 6 sqrt(6) M
      d A_mu/d Y_mu = -A_perp: |.|_2 <= sqrt(3) M per mu -> 2 sqrt(3) M
      d A_mu/d A_perp = -Y_mu I: |.|_F <= sqrt(3) M per mu -> 2 sqrt(3) M
    A_4 = A_perp -> sqrt(3);  log_Omega -> 1.
    """

    r10, r40, r3, r6, r12 = np.sqrt(10.0), np.sqrt(40.0), np.sqrt(3.0), np.sqrt(6.0), np.sqrt(12.0)
    return {
        "metric": r10 + r40 * 2 * M + r10 * M**2 + r40 * (2 * M + 2 * M**2) + 2 + 2 * M + 2 * M + 1,
        "scalar": r3 + 6 * M,
        "connection": 2 * r3 + 4 * r3 + r12 * 6 * r6 * M + 2 * r3 * M + 2 * r3 * M,
        "A_perp_identity": r3,
        "log_Omega_identity": 1.0,
    }


def lipschitz_bound_formula(M: float) -> float:
    return float(sum(lipschitz_bound_terms(M).values()))


def _jacobian(u: np.ndarray, h: float = FD_STEP) -> np.ndarray:
    J = np.empty((OUT_SIZE, U_SIZE))
    for j in range(U_SIZE):
        e = np.zeros(U_SIZE)
        e[j] = h
        J[:, j] = (_phi_numeric(u + e) - _phi_numeric(u - e)) / (2.0 * h)
    return J


def _sample_set(samples: int, seed: int, radius: float) -> list[tuple[str, np.ndarray]]:
    rng = np.random.default_rng(seed)
    out: list[tuple[str, np.ndarray]] = []
    for _ in range(samples):
        out.append(("ball", rng.uniform(-radius, radius, size=U_SIZE)))
    for scale in (1.0e-3, 1.0, 10.0):  # single-coordinate spikes at three scales
        for j in range(U_SIZE):
            u = np.zeros(U_SIZE)
            u[j] = scale
            out.append((f"spike_{scale:g}", u))
            u2 = np.zeros(U_SIZE)
            u2[j] = -scale
            out.append((f"spike_{scale:g}", u2))
    for scale in (1.0e-3, 5.0, 10.0):  # large / tiny random corners
        for _ in range(20):
            out.append((f"corner_{scale:g}", rng.choice([-scale, scale], size=U_SIZE) * rng.uniform(0.5, 1.0, size=U_SIZE)))
    return out


def lipschitz_witness(samples: int, seed: int, radius: float) -> dict[str, Any]:
    worst_ratio = 0.0
    worst_norm = 0.0
    worst_M = 0.0
    violations = 0
    by_kind: dict[str, dict[str, float]] = {}
    for kind, u in _sample_set(samples, seed, radius):
        M = float(np.abs(u).max())
        norm = float(np.linalg.norm(_jacobian(u), 2))
        bound = lipschitz_bound_formula(M)
        ratio = norm / bound
        record = by_kind.setdefault(kind, {"count": 0, "worst_ratio": 0.0})
        record["count"] += 1
        record["worst_ratio"] = max(record["worst_ratio"], ratio)
        if ratio > worst_ratio:
            worst_ratio, worst_norm, worst_M = ratio, norm, M
        if norm > bound * (1.0 + JACOBIAN_TOLERANCE):
            violations += 1
    return {
        "samples_ball": samples,
        "samples_total": sum(int(r["count"]) for r in by_kind.values()),
        "seed": seed,
        "radius": radius,
        "M_definition": "max |u_i| over all 53 free-data entries (gamma, Y, d, a, varphi_H, A_Sigma, A_perp, k, kappa, log_Omega)",
        "violations": violations,
        "worst_norm_over_bound": worst_ratio,
        "worst_case": {"jacobian_operator_norm": worst_norm, "M": worst_M, "bound": lipschitz_bound_formula(worst_M)},
        "by_kind": by_kind,
        "bound_is_N_independent": True,
        "pass": bool(violations == 0),
    }


def graph_numeric_witness(samples: int, seed: int, radius: float) -> dict[str, Any]:
    """Numeric re-check of all gluing rows (metric, scalar, connection for mu = 0..3) on random free data."""

    rng = np.random.default_rng(seed + 1)
    worst = 0.0
    for _ in range(samples):
        u = rng.uniform(-radius, radius, size=U_SIZE)
        f = _unpack(u)
        out = _phi_numeric(u)
        g = np.zeros((5, 5))
        g[np.triu_indices(5)] = out[:15]
        g = g + g.T - np.diag(np.diag(g))
        t = np.zeros((5, 4))
        t[:4, :] = np.eye(4)
        t[4, :] = f["Y"]
        worst = max(worst, float(np.abs(t.T @ g @ t - f["gamma"]).max()))
        R = _cayley_np(f["k"])
        K = _hat_np(f["k"])
        Minv = np.linalg.inv(np.eye(3) - K)
        phi = out[15:18]
        worst = max(worst, float(np.abs(R @ phi - f["varphi"]).max()))
        A_mu = out[18:30].reshape(4, 3)
        A_perp = out[30:33]
        for mu in range(4):
            dR = 2.0 * Minv @ _hat_np(f["kappa"][mu]) @ Minv
            pulled = A_mu[mu] + f["Y"][mu] * A_perp
            worst = max(worst, float(np.abs(R @ _hat_np(pulled) @ R.T - dR @ R.T - _hat_np(f["A_Sigma"][mu])).max()))
        worst = max(worst, float(np.abs(R.T @ R - np.eye(3)).max()))
        worst = max(worst, abs(out[33] - f["log_Omega"]))
    return {"samples": samples, "worst_abs_row_residual": worst, "tolerance": GRAPH_RESIDUAL_TOLERANCE, "pass": bool(worst < GRAPH_RESIDUAL_TOLERANCE)}


def kronecker_inverse_static_audit() -> dict[str, Any]:
    """Static audit on the byte-pinned v5.6.4 source: which functions reference the collocation inverse.

    A function counts as a direct user if its body contains basis["inverse"] / Finv / np.linalg.inv(values) style
    references to the collocation matrix inverse, and as an indirect user if it calls a direct or indirect user.
    """

    import ast

    source = V564_CERTIFICATE_PATH.read_text()
    tree = ast.parse(source)
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    direct: set[str] = set()
    calls: dict[str, set[str]] = {}
    for name, node in functions.items():
        body = ast.get_source_segment(source, node) or ""
        if '["inverse"]' in body or "Finv" in body:
            direct.add(name)
        calls[name] = {
            child.func.id for child in ast.walk(node)
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id in functions
        }
    users = set(direct)
    changed = True
    while changed:
        changed = False
        for name, callees in calls.items():
            if name not in users and callees & users:
                users.add(name)
                changed = True
    expected = set(KRONECKER_INVERSE_USERS_V5_6_4)
    return {
        "direct_users": sorted(direct),
        "all_users_transitive": sorted(users),
        "expected_users_all_confirmed": bool(expected <= users),
        "expected_not_confirmed": sorted(expected - users),
        "decode_pointwise_boundary_in_decoder_uses_collocation_inverse": _decoder_uses_collocation_inverse(),
    }


def _decoder_uses_collocation_inverse() -> bool:
    import ast

    source = V5642_DECODER_PATH.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "decode_pointwise_boundary":
            body = ast.get_source_segment(source, node) or ""
            return '["inverse"]' in body or "Finv" in body
    raise RetractionGateError("decode_pointwise_boundary not found in the pinned decoder")


def build_payload() -> dict[str, Any]:
    _load_json(BUNDLE_PATH, BUNDLE_SHA256)  # lineage pin only: the class members live there
    for path, expected in ((V5642_DECODER_PATH, V5642_DECODER_SHA256), (V564_CERTIFICATE_PATH, V564_CERTIFICATE_SHA256)):
        if _sha256(path) != expected:
            raise RetractionGateError(f"byte pin drift for {path.name}")
    v5668 = _load_json(V5668_PATH, V5668_SHA256)
    if v5668["decision"].get("declared_collocation_uniform_stability_pass") is not False:
        raise RetractionGateError("upstream v5.6.6.8 must record the coefficient-chart instability")
    if v5668["decision"].get("bundle_members_glued_pointwise_off_collocation_pass") is not True:
        raise RetractionGateError("upstream v5.6.6.8 must record pointwise gluing of the members")

    graph = graph_structure_certificate()
    numeric_graph = graph_numeric_witness(SAMPLES, SAMPLE_SEED, SAMPLE_RADIUS)
    lipschitz = lipschitz_witness(SAMPLES, SAMPLE_SEED, SAMPLE_RADIUS)
    inverse_audit = kronecker_inverse_static_audit()

    graph_pass = bool(
        graph["metric_row_vanishes_identically"]
        and graph["cayley_R_orthogonal"]
        and graph["cayley_R_det_one"]
        and graph["RT_dR_skew_symmetric"]
        and graph["scalar_row_vanishes_identically"]
        and graph["connection_row_vanishes_identically"]
        and graph["pullback_consistency"]
        and numeric_graph["pass"]
    )
    degrees = graph["eliminated_metric_polynomial_degrees"]
    bound_pass = bool(
        lipschitz["pass"]
        and degrees["Y"] <= 2 and degrees["gamma"] <= 1 and degrees["d"] <= 1 and degrees["a"] <= 1
        and inverse_audit["expected_users_all_confirmed"]
        and not inverse_audit["decode_pointwise_boundary_in_decoder_uses_collocation_inverse"]
    )

    scientific = {
        "graph_structure": graph,
        "graph_numeric_witness": numeric_graph,
        "lipschitz": lipschitz,
        "lipschitz_bound_terms_doc": lipschitz_bound_terms.__doc__.strip(),
        "lipschitz_bound_terms_at_M1": lipschitz_bound_terms(1.0),
        "theorem": {
            "statement": (
                "Let Phi be the common-first elimination map defined pointwise on T^4 by the formulas of section (A), "
                "written chart-free in (R, dR_mu) (the Cayley chart is only used to certify it; the v5.6.4.2 decoder "
                "uses expm with R = S R0, dR = dS R0 + S dR0, A_Sigma = vee(S hat(A0) S^T - dS S^T), all pointwise). "
                "On the open margin set {a >= a_min > 0, gamma - d d^T / a Lorentzian with the signature margin, "
                "Omega >= Omega_min, timelike khronon margin} the pointwise-glued restricted class is exactly the graph "
                "{(u, Phi(u))} over the free data u, the retraction from any ambient point with the same free data is "
                "u -> (u, Phi(u)), and the tangent space is {(du, dPhi(u).du)}. Since Phi contains no N, the pointwise "
                "Lipschitz constant of Phi on max|u| <= M is the explicit polynomial recorded above, uniform in N by "
                "construction. Because Phi consumes first derivatives (Y_mu = d_mu Y, dR_mu), the Sobolev lift is "
                "Phi: H^{s+1}(Y, r, q_Q) x H^s(gamma, d, a, varphi, A, log Omega) -> H^s with "
                "||Phi(u) - Phi(u')||_{H^s} <= C_s(M) ||u - u'|| for s > 2 (Moser composition); the v5.6.6.8 class must "
                "therefore be read with r_+-, q_Q in H^{s+1} alongside Y_+-, otherwise the A trace lies only in H^{s-1} "
                "and the classical-jet chain rule of its part (i) fails for the connection channel."
            ),
            "discharges": (
                "the 'uniformly bounded right inverse/retraction' obligation in the continuum re-glued formulation "
                "(part (iii) of the v5.6.6.8 theorem: project the free data, then re-glue with Phi)."
            ),
            "does_not_discharge": (
                "the finite obligation on DG_N over the spectral space V_N (Phi(u) is not a trigonometric polynomial, so "
                "Phi(V_N) is not inside V_N); the v5.6.6.8 what_remains item about lifting the finite Stokes certificates "
                "with a rate stays open; uniform stability of the v5.6.4 coefficient-chart scheme (its key stays False); "
                "the gauge quotient H_N (the graph tangent space still contains the 9N orbit directions); any statement "
                "about the literal v5.2 action beyond the class structure."
            ),
            "sobolev_lift": "analytic argument (Moser composition, s > d/2 = 2); not machine-checked",
        },
        "kronecker_inverse_users_in_v5_6_4": inverse_audit,
        "pointwise_formulation_needs_collocation_inverse": bool(inverse_audit["decode_pointwise_boundary_in_decoder_uses_collocation_inverse"]),
        "machine_checked": {
            "graph_rows_vanish_symbolically": graph_pass,
            "graph_rows_vanish_numerically": numeric_graph["pass"],
            "lipschitz_bound_holds_on_ball_spikes_and_corners": lipschitz["pass"],
            "metric_degrees_bounded": bool(degrees["Y"] <= 2 and degrees["gamma"] <= 1),
        },
    }

    decision = {
        "common_first_gluing_is_explicit_graph_pass": graph_pass,
        "pointwise_jacobian_explicit_bound_sampled_pass": bound_pass,
        "uniform_stability_pass": False,
        "spectral_N_convergence_pass": False,
        "uniform_N_to_infinity_bridge_pass": False,
        "restricted_family_exact_action_identity_pass": False,
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
        "classification": "theory_only;symbolic_graph_structure;pointwise_retraction;restricted_spectral_family;fail_closed_bridge",
        "decision": decision,
        "fixed_before_run": {
            "SAMPLES": SAMPLES,
            "SAMPLE_SEED": SAMPLE_SEED,
            "SAMPLE_RADIUS": SAMPLE_RADIUS,
            "JACOBIAN_TOLERANCE": JACOBIAN_TOLERANCE,
            "FD_STEP": FD_STEP,
            "GRAPH_RESIDUAL_TOLERANCE": GRAPH_RESIDUAL_TOLERANCE,
            "adversarial_sample_design": "ball + single-coordinate spikes at 1e-3/1/10 + random corners at 1e-3/5/10",
            "rotation_chart": "Cayley (I-K)^{-1}(I+K), exact rational, no finite pole (misses only the angle-pi rotations); the v5.6.4.2 decoder uses expm; the graph identity is chart-free in (R, dR)",
            "free_data_layout": {k: [v.start, v.stop] for k, v in _SL.items()},
        },
        "scientific": scientific,
        "independence_boundary": {
            "scientific_inputs": "the elimination formulas transcribed from the byte-pinned v5.6.4.2 pointwise decoder (decode_pointwise_boundary); static AST audit of the byte-pinned v5.6.4 certificate; no upstream module imported",
            "imports_action_evaluators": False,
            "imports_one_omega_modules": False,
            "reads_upstream_expected_values": False,
            "symbolic_engine": f"sympy {sp.__version__}",
        },
        "open_obligation": {
            "finite_to_continuum_rate": "prove quadrature convergence of the finite Route C Stokes/chain certificates to the continuum identity of v5.6.6.8 with a rate in (Qtheta, Qrho)",
            "spectral_space_mismatch": "either enlarge V_N to contain Phi(u) for u in V_N (not trigonometric) or state the finite family in free data only",
            "periodic_box_exhaustion": "unchanged",
            "C1_N1_beyond_the_bridge": "v5.6.1 quarantine obligations remain: full bulk diffeomorphism Ward identity, fully coupled moving-embedding cross terms, off-shell continuous extension",
        },
        "evidence_boundary": (
            "Machine-checked: the common-first gluing is the graph of an explicit analytic map (all rows vanish symbolically "
            "and numerically), and its pointwise Lipschitz constant is an explicit N-independent polynomial verified on random "
            "samples. Analytic: the Sobolev lift. Not proven: the N-to-infinity bridge itself, C1/N1, B4/B5."
        ),
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "v5_6_6_8_receipt_sha256": V5668_SHA256,
            "v5_6_4_2_pointwise_decoder_sha256": V5642_DECODER_SHA256,
            "v5_6_4_certificate_sha256": V564_CERTIFICATE_SHA256,
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
    if not payload["decision"]["common_first_gluing_is_explicit_graph_pass"]:
        raise RetractionGateError("graph structure certificate failed")
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    d = payload["decision"]
    print(
        f"graph={d['common_first_gluing_is_explicit_graph_pass']} "
        f"jacobian_bound={d['pointwise_jacobian_explicit_bound_sampled_pass']} "
        f"bridge={d['uniform_N_to_infinity_bridge_pass']}"
    )


if __name__ == "__main__":
    main()
