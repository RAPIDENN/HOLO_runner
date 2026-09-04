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

(B) N-independent Lipschitz bound.  The pointwise Jacobian of Phi is bounded by
    an explicit polynomial in M = max(|Y|, |d|, |a|, |A_Sigma|, |dR|) with |R| = 1:
      |dPhi_g| <= |dgamma| + 2|Y||dd| + |Y|^2|da| + 2(|d| + |a||Y|)|dY|
      |dPhi_A| <= |dA_Sigma| + 2|A_Sigma||dR| + |dR||dR_in| ... (recorded exactly below)
    The bound is checked symbolically (degrees of the Jacobian entries) and on
    random samples (operator norm of the exact Jacobian against the formula).
    Because Phi is pointwise and N-free, the bound is uniform in N by
    construction: this is the retraction of part (iii) of the v5.6.6.8 theorem.

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

FROZEN_COMMIT = "ea014fd"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
V5668_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.json"
V5668_SHA256 = "cca4e3a4299b6f1817575e352f2888b2cedb30bedf04ac77102338e56bf4cce7"

# Fixed before run.
SAMPLES = 400
SAMPLE_SEED = 20260904
SAMPLE_RADIUS = 1.5
JACOBIAN_TOLERANCE = 1.0e-9
KRONECKER_INVERSE_USERS_V5_6_4 = (
    "gluing_map (basis['inverse'] einsum)",
    "ambient_to_free_coordinates",
    "retract_ambient_point (via construct_ambient_point)",
    "finite_frame_gauge_action -> runtime_SO3_gauge_tangents",
    "runtime_DG (differentiates gluing_map)",
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

def _phi_numeric(free: dict[str, np.ndarray]) -> np.ndarray:
    gamma, Y, d, a = free["gamma"], free["Y"], free["d"], free["a"]
    A_Sigma, A_perp, k, kappa = free["A_Sigma"], free["A_perp"], free["k"], free["kappa"]
    g = np.empty((5, 5))
    g[:4, :4] = gamma - np.outer(d, Y) - np.outer(Y, d) + a * np.outer(Y, Y)
    g[:4, 4] = d - a * Y
    g[4, :4] = g[:4, 4]
    g[4, 4] = a
    R = _cayley_np(k)
    # dR along kappa (exact derivative of Cayley map): dR = 2 (I-K)^{-1} hat(kappa) (I-K)^{-1}
    K = _hat_np(k)
    Minv = np.linalg.inv(np.eye(3) - K)
    dR = 2.0 * Minv @ _hat_np(kappa) @ Minv
    A_source = _vee_np(R.T @ _hat_np(A_Sigma) @ R + R.T @ dR)
    Ymu = Y[0]
    A_mu = A_source - Ymu * A_perp
    return np.concatenate((g[np.triu_indices(5)], A_mu, A_perp))


def _pack(free: dict[str, np.ndarray]) -> np.ndarray:
    return np.concatenate((free["gamma"][np.triu_indices(4)], free["Y"], free["d"], [free["a"]], free["A_Sigma"], free["A_perp"], free["k"], free["kappa"]))


def _unpack(x: np.ndarray) -> dict[str, np.ndarray]:
    gamma = np.zeros((4, 4))
    gamma[np.triu_indices(4)] = x[:10]
    gamma = gamma + gamma.T - np.diag(np.diag(gamma))
    return {
        "gamma": gamma,
        "Y": x[10:14],
        "d": x[14:18],
        "a": float(x[18]),
        "A_Sigma": x[19:22],
        "A_perp": x[22:25],
        "k": x[25:28],
        "kappa": x[28:31],
    }


def lipschitz_bound_formula(M: float) -> float:
    """Explicit pointwise bound on the operator norm of dPhi for free data of size <= M.

    Metric block: entries of g are polynomials of degree <= 2 in Y and <= 1 in (gamma, d, a), so the
    Frobenius norm of the Jacobian block is bounded by  sqrt(10) + 2*4*M + 4*M^2 + 2*4*(M + M^2)  (crude
    but explicit).  Connection block with |R| = 1:  |dA_source| <= |dA_Sigma| + 2|A_Sigma||dR| + |d(R^T dR)|,
    and for the Cayley chart |dR/dk| <= 2|(I-K)^{-1}|^2 <= 2, |d(R^T dR)| <= (2 + 4|kappa|)|dk| + 2|dkappa|.
    The returned constant is a polynomial in M; N does not appear anywhere.
    """

    metric = np.sqrt(10.0) + 8.0 * M + 4.0 * M**2 + 8.0 * (M + M**2)
    connection = 1.0 + 2.0 * M * 2.0 + (2.0 + 4.0 * M) + 2.0 + M + 1.0  # dA_Sigma, dR terms, d(R^T dR), Y*A_perp, dA_perp
    return float(metric + connection + 1.0)


def lipschitz_witness(samples: int, seed: int, radius: float) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    worst_ratio = 0.0
    worst_norm = 0.0
    violations = 0
    rows = []
    for index in range(samples):
        x = rng.uniform(-radius, radius, size=31)
        x[25:28] *= 0.5  # keep the Cayley chart away from its pole
        free = _unpack(x)
        M = float(max(np.abs(free["Y"]).max(), np.abs(free["d"]).max(), abs(free["a"]), np.abs(free["A_Sigma"]).max(), np.abs(free["kappa"]).max(), np.abs(free["k"]).max()))
        base = _phi_numeric(free)
        J = np.empty((base.size, 31))
        h = 1.0e-6
        for j in range(31):
            e = np.zeros(31)
            e[j] = h
            J[:, j] = (_phi_numeric(_unpack(x + e)) - _phi_numeric(_unpack(x - e))) / (2.0 * h)
        norm = float(np.linalg.norm(J, 2))
        bound = lipschitz_bound_formula(M)
        ratio = norm / bound
        worst_ratio = max(worst_ratio, ratio)
        worst_norm = max(worst_norm, norm)
        if norm > bound * (1.0 + JACOBIAN_TOLERANCE):
            violations += 1
        if index < 5:
            rows.append({"M": M, "jacobian_operator_norm": norm, "bound": bound})
    return {
        "samples": samples,
        "seed": seed,
        "radius": radius,
        "violations": violations,
        "worst_norm_over_bound": worst_ratio,
        "worst_jacobian_operator_norm": worst_norm,
        "first_rows": rows,
        "bound_is_N_independent": True,
        "pass": bool(violations == 0),
    }


def graph_numeric_witness(samples: int, seed: int, radius: float) -> dict[str, Any]:
    """Numeric re-check of the gluing rows on random free data (independent of the symbolic path)."""

    rng = np.random.default_rng(seed + 1)
    worst = 0.0
    for _ in range(samples):
        x = rng.uniform(-radius, radius, size=31)
        x[25:28] *= 0.5
        free = _unpack(x)
        out = _phi_numeric(free)
        g = np.zeros((5, 5))
        g[np.triu_indices(5)] = out[:15]
        g = g + g.T - np.diag(np.diag(g))
        t = np.zeros((5, 4))
        t[:4, :] = np.eye(4)
        t[4, :] = free["Y"]
        worst = max(worst, float(np.abs(t.T @ g @ t - free["gamma"]).max()))
        R = _cayley_np(free["k"])
        K = _hat_np(free["k"])
        Minv = np.linalg.inv(np.eye(3) - K)
        dR = 2.0 * Minv @ _hat_np(free["kappa"]) @ Minv
        A_mu, A_perp = out[15:18], out[18:21]
        pulled = A_mu + free["Y"][0] * A_perp
        worst = max(worst, float(np.abs(R @ _hat_np(pulled) @ R.T - dR @ R.T - _hat_np(free["A_Sigma"])).max()))
        worst = max(worst, float(np.abs(R.T @ R - np.eye(3)).max()))
    return {"samples": samples, "worst_abs_row_residual": worst, "pass": bool(worst < 1.0e-12)}


def build_payload() -> dict[str, Any]:
    _load_json(BUNDLE_PATH, BUNDLE_SHA256)
    v5668 = _load_json(V5668_PATH, V5668_SHA256)
    if v5668["decision"].get("declared_collocation_uniform_stability_pass") is not False:
        raise RetractionGateError("upstream v5.6.6.8 must record the coefficient-chart instability")
    if v5668["decision"].get("bundle_members_glued_pointwise_off_collocation_pass") is not True:
        raise RetractionGateError("upstream v5.6.6.8 must record pointwise gluing of the members")

    graph = graph_structure_certificate()
    numeric_graph = graph_numeric_witness(SAMPLES, SAMPLE_SEED, SAMPLE_RADIUS)
    lipschitz = lipschitz_witness(SAMPLES, SAMPLE_SEED, SAMPLE_RADIUS)

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
    bound_pass = bool(lipschitz["pass"] and degrees["Y"] <= 2 and degrees["gamma"] <= 1 and degrees["d"] <= 1 and degrees["a"] <= 1)

    scientific = {
        "graph_structure": graph,
        "graph_numeric_witness": numeric_graph,
        "lipschitz": lipschitz,
        "lipschitz_bound_formula": lipschitz_bound_formula.__doc__.strip(),
        "theorem": {
            "statement": (
                "Let Phi be the common-first elimination map defined pointwise on T^4 by the formulas of section (A). "
                "The pointwise-glued restricted class is exactly the graph {(u, Phi(u))} over the free data u, so the "
                "retraction from any ambient point with the same free data onto the class is u -> (u, Phi(u)) and the "
                "tangent space is {(du, dPhi(u).du)}. Since Phi contains no N, the Lipschitz constant of Phi on |u| <= M "
                "is the N-independent polynomial recorded above, and by Moser composition estimates "
                "||Phi(u) - Phi(u')||_{H^s} <= C_s(M) ||u - u'||_{H^s} for s > 2 on ||u||_{H^s} <= M. This discharges "
                "the 'uniformly bounded right inverse/retraction of DG_N' obligation in the pointwise formulation; it is "
                "the retraction used implicitly by the v5.6.4.2 decoder and by part (iii) of the v5.6.6.8 theorem."
            ),
            "not_claimed": (
                "Uniform stability of the v5.6.4 coefficient-chart scheme (its key stays False); quadrature convergence "
                "of the finite Route C certificates to the continuum identity with a rate; membership of Fourier-truncated "
                "class points in the finite spectral space V_N (the eliminated traces are not trigonometric polynomials); "
                "any statement about the literal v5.2 action beyond the class structure."
            ),
            "sobolev_lift": "analytic argument (Moser composition, s > d/2 = 2); not machine-checked",
        },
        "kronecker_inverse_users_in_v5_6_4": list(KRONECKER_INVERSE_USERS_V5_6_4),
        "pointwise_formulation_needs_collocation_inverse": False,
        "machine_checked": {
            "graph_rows_vanish_symbolically": graph_pass,
            "graph_rows_vanish_numerically": numeric_graph["pass"],
            "lipschitz_bound_holds_on_samples": lipschitz["pass"],
            "metric_degrees_bounded": bool(degrees["Y"] <= 2 and degrees["gamma"] <= 1),
        },
    }

    decision = {
        "common_first_gluing_is_explicit_graph_pass": graph_pass,
        "pointwise_retraction_N_independent_lipschitz_bound_pass": bound_pass,
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
            "rotation_chart": "Cayley (I-K)^{-1}(I+K), exact rational; the v5.6.4.2 decoder uses expm, same group element set locally",
        },
        "scientific": scientific,
        "independence_boundary": {
            "scientific_inputs": "the elimination formulas transcribed from the v5.6.4.2 pointwise decoder contract; no upstream module imported",
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
        f"lipschitz={d['pointwise_retraction_N_independent_lipschitz_bound_pass']} "
        f"bridge={d['uniform_N_to_infinity_bridge_pass']}"
    )


if __name__ == "__main__":
    main()
