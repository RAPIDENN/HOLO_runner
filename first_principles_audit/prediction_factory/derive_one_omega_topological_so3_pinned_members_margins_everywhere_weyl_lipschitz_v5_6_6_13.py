#!/usr/bin/env python3
"""Class margins of the pinned members EVERYWHERE on the collar: a Weyl + Lipschitz
certificate with exact trigonometric/polynomial coefficients (v5.6.6.13).

v5.6.6.11 measured the four class margins on a 256 x 129 grid and, after review,
kept `pinned_members_margins_everywhere_on_collar_pass = False` because a finite
grid does not bound the fields between nodes.  This gate supplies that bound.

Structure used (all exact, read from the byte-pinned bundle through the byte-pinned
v5.6.4.2 kinematic decoder):
  * the free data of the pinned members are trigonometric polynomials of degree <= 1
    in the single direction theta = x0 + x1; the eliminated metric trace
    g_trace = gamma - dY - Yd + aYY is therefore a trigonometric polynomial of
    degree <= 3, and J1, C_j, gamma, log Omega, dT are of degree <= 1;
  * the bulk metric and log Omega are X(rho, theta) = X_inf + h0(rho)(X0(theta) - X_inf)
    + h1(rho) J1(theta) + sum_j b_j(rho) C_j(theta) with the v5.6.4.4 polynomial
    profiles (degrees 5, 6, 6 + j);
  * the frame rotation is R = exp(hat q(theta)) exp(hat r(theta)) with q, r of degree <= 1.

Certificates (each rigorous up to floating-point rounding, padded by SAFETY):
  (M) metric Lorentzian with eigenvalue margin everywhere.  On the grid the
      eigenvalues have clearance m_grid; by Weyl, moving to any (rho, theta) changes
      every eigenvalue by at most ||g(rho, theta) - g(rho_g, theta_g)||_2
      <= L_theta h_theta/2 + L_rho h_rho/2, where L_theta <= sum_k k (||A_k||_F + ||B_k||_F)
      over the exact theta-harmonics of the bulk metric (with sup_rho |h0| <= 1 etc.)
      and L_rho <= sup|h0'| sup_theta||X0 - X_inf|| + sup|h1'| sup||J1|| + sum_j sup|b_j'| sup||C_j||,
      polynomial sups on [0, 1] bounded by Bernstein coefficients and trigonometric
      sups by the sum of harmonic norms.  If m_grid - (L_theta h_theta/2 + L_rho h_rho/2)
      > margin, no eigenvalue can cross zero, so the signature and the margin hold everywhere.
  (O) Omega >= Omega_min everywhere: the same Lipschitz argument on the scalar log Omega.
  (K) khronon timelike margin on the boundary: T_norm2 = t^T gamma^{-1} t with
      t = dT + e0; |d T_norm2 / d theta| <= 2||t|| ||gamma^{-1}|| ||t'|| + ||t||^2 ||gamma^{-1}||^2 ||gamma'||
      with ||gamma^{-1}||_2 <= 1 / (min |eig gamma| everywhere) obtained from (M) on the boundary.
  (R) SO(3) chart clearance: angle(R) <= |q(theta)| + |r(theta)| (bi-invariant triangle
      inequality, angle(exp hat v) = |v| for |v| <= pi) and sup_theta |a + b cos + c sin|
      <= |a| + sqrt(|b|^2 + |c|^2).

The harmonic structure is not assumed: the gate checks that the FFT reconstruction
of every field reproduces the decoder at random off-grid points to 1e-12, which
fails if a field had harmonics above the truncation.

This gate does not flip the bridge, C1/N1, B4/B5 or any v5.6.4 fail-closed key, and
it does not edit v5.6.6.11 (its fail-closed key is discharged by THIS separate
certificate, to be flipped there only after independent review).
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_pinned_members_margins_everywhere_weyl_lipschitz_v5_6_6_13.json"
TEST = HERE / "test_one_omega_topological_so3_pinned_members_margins_everywhere_weyl_lipschitz_v5_6_6_13.py"
SCHEMA = "holo.one-omega-topological-so3-pinned-members-margins-everywhere-weyl-lipschitz-v5-6-6-13.v1"

FROZEN_COMMIT = "ea014fd1a8ed124c353058eb6f0a1c92b90353bc"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
DECODER_PATH = HERE / "export_one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitives.py"
DECODER_SHA256 = "4b7eda150cf2d22e04ef2b1b04391c31dc9e618839d7ead9e74a540371ab3d7f"
V56611_PATH = ARTIFACTS / "one_omega_topological_so3_pinned_members_dense_collar_margins_v5_6_6_11.json"
V56611_SHA256 = "89592cd0eb7a3357a7f0b6f69bebeed5fb18d7466719c226b482b8611201a7b6"

# Fixed before run.
SIGNATURE_EIGENVALUE_MARGIN = 2.0e-2
OMEGA_MIN = 5.0e-1
TIMELIKE_MARGIN = 2.0e-1
ROTATION_CUT_LOCUS_MARGIN = 1.0
THETA_GRID = 256
RHO_GRID = 129
FFT_POINTS = 16            # exact for trigonometric polynomials of degree <= 7; the fields have degree <= 3
MAX_HARMONIC = 7
EXACTNESS_TOLERANCE = 1.0e-12
SAFETY = 1.0e-9
REFERENCE_METRIC = np.diag((-1.64, 1.17, 1.31, 1.46, 1.17))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))
SIDES = ("plus", "minus")
RANDOM_CHECK_SEED = 20260904


class EverywhereGateError(RuntimeError):
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
        raise EverywhereGateError(f"byte pin drift for {path.name}: {digest} != {expected_sha256}")
    return json.loads(path.read_text())


def _decode_f64le(block: dict[str, Any]) -> np.ndarray:
    raw = np.frombuffer(base64.b64decode(block["data"]), dtype=block["dtype"])
    return raw.reshape(block["shape"]) if "shape" in block else raw


def load_pinned_decoder():
    if _sha256(DECODER_PATH) != DECODER_SHA256:
        raise EverywhereGateError("decoder byte pin drift")
    spec = importlib.util.spec_from_file_location("pinned_v5_6_4_2_decoder_for_v5_6_6_13", DECODER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# exact polynomial and trigonometric bounds
# --------------------------------------------------------------------------

def profile_polynomials(K: int) -> dict[str, np.ndarray]:
    """Monomial coefficients (ascending) of h0, h1 and the K bumps on [0, 1]."""

    h0 = np.array([1.0, 0.0, 0.0, -10.0, 15.0, -6.0])
    h1 = np.concatenate(([0.0], h0))
    s = np.array([0.0, 1.0, -1.0])                      # rho (1 - rho)
    envelope = 64.0 * np.polynomial.polynomial.polypow(s, 3)
    bumps = []
    for degree in range(K):
        legendre = np.zeros(degree + 1)
        legendre[degree] = 1.0
        # P_degree(2 rho - 1) as a polynomial in rho
        p_in_z = np.polynomial.legendre.leg2poly(legendre)
        # compose z = 2 rho - 1
        composed = np.zeros(1)
        for power, coefficient in enumerate(p_in_z):
            term = coefficient * np.polynomial.polynomial.polypow(np.array([-1.0, 2.0]), power) if power > 0 else np.array([coefficient])
            composed = np.polynomial.polynomial.polyadd(composed, term)
        bumps.append(np.polynomial.polynomial.polymul(envelope, composed))
    return {"h0": h0, "h1": h1, "bumps": bumps}


def polynomial_sup_on_unit_interval(coefficients: np.ndarray) -> float:
    """Rigorous upper bound of sup_{[0,1]} |p| via the max absolute Bernstein coefficient."""

    a = np.asarray(coefficients, dtype=float)
    n = a.size - 1
    if n < 0:
        return 0.0
    bernstein = np.zeros(n + 1)
    for i in range(n + 1):
        total = 0.0
        for j in range(i + 1):
            total += math.comb(i, j) / math.comb(n, j) * a[j]
        bernstein[i] = total
    return float(np.max(np.abs(bernstein)))


def polynomial_derivative(coefficients: np.ndarray) -> np.ndarray:
    return np.polynomial.polynomial.polyder(np.asarray(coefficients, dtype=float))


def harmonics(samples: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Real harmonics A_k (cos) and B_k (sin), k = 0..P/2, of samples on P equispaced points (axis 0)."""

    P = samples.shape[0]
    X = np.fft.rfft(samples, axis=0)
    A = 2.0 * X.real / P
    B = -2.0 * X.imag / P
    A[0] /= 2.0
    if P % 2 == 0:
        A[-1] /= 2.0
        B[-1] = 0.0
    return A, B


def evaluate_harmonics(A: np.ndarray, B: np.ndarray, theta: np.ndarray) -> np.ndarray:
    k = np.arange(A.shape[0])
    cos = np.cos(np.outer(theta, k))
    sin = np.sin(np.outer(theta, k))
    return np.tensordot(cos, A, axes=([1], [0])) + np.tensordot(sin, B, axes=([1], [0]))


def _fro(x: np.ndarray) -> np.ndarray:
    """Frobenius norm over trailing axes for each harmonic index."""

    return np.sqrt(np.sum(np.asarray(x) ** 2, axis=tuple(range(1, np.ndim(x))))) if np.ndim(x) > 1 else np.abs(x)


def trig_sup_bound(A: np.ndarray, B: np.ndarray) -> float:
    """sup_theta ||F(theta)|| <= ||A_0|| + sum_k (||A_k|| + ||B_k||)."""

    return float(_fro(A)[0] + np.sum(_fro(A)[1:] + _fro(B)[1:]))


def trig_derivative_sup_bound(A: np.ndarray, B: np.ndarray) -> float:
    """sup_theta ||F'(theta)|| <= sum_k k (||A_k|| + ||B_k||)."""

    k = np.arange(A.shape[0])
    return float(np.sum(k * (_fro(A) + _fro(B))))


def _sym5_from_packed(packed: np.ndarray) -> np.ndarray:
    out = np.zeros(packed.shape[:-1] + (5, 5))
    for index, (i, j) in enumerate(SYMMETRIC5):
        out[..., i, j] = packed[..., index]
        out[..., j, i] = packed[..., index]
    return out


# --------------------------------------------------------------------------
# per-member certificate
# --------------------------------------------------------------------------

def member_certificate(decoder, bundle: dict[str, Any], member: dict[str, Any]) -> dict[str, Any]:
    N, K = int(member["N"]), int(member["K"])
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    free = _decode_f64le(member["authoritative_free_central_f64le"])
    layout = contract["free_layout"]["blocks"]

    def decode(theta: np.ndarray) -> dict[str, Any]:
        points = np.zeros((theta.size, 4))
        points[:, 0] = theta
        out = decoder.decode_pointwise_boundary(free, contract, points)
        tables = decoder.fourier_tables(contract["basis"], points)
        _T, dT = decoder._spectral(decoder._free_get(free, layout, "common.T"), tables)
        t = dT[..., 0].copy()
        t[:, 0] += 1.0
        out["khronon_t"] = t
        q, _dq = decoder._spectral(decoder._free_get(free, layout, "Q_frame.q"), tables)
        out["q_field"] = q
        out["r_field"] = {side: decoder._spectral(decoder._free_get(free, layout, f"{side}.r_E0"), tables)[0] for side in SIDES}
        return out

    theta_fft = 2.0 * math.pi * np.arange(FFT_POINTS) / FFT_POINTS
    fft_decoded = decode(theta_fft)
    rng = np.random.default_rng(RANDOM_CHECK_SEED + N)
    theta_check = rng.uniform(0.0, 2.0 * math.pi, size=5)
    check_decoded = decode(theta_check)

    profiles = profile_polynomials(K)
    sup_h0 = polynomial_sup_on_unit_interval(profiles["h0"])
    sup_h1 = polynomial_sup_on_unit_interval(profiles["h1"])
    sup_bumps = [polynomial_sup_on_unit_interval(b) for b in profiles["bumps"]]
    sup_dh0 = polynomial_sup_on_unit_interval(polynomial_derivative(profiles["h0"]))
    sup_dh1 = polynomial_sup_on_unit_interval(polynomial_derivative(profiles["h1"]))
    sup_dbumps = [polynomial_sup_on_unit_interval(polynomial_derivative(b)) for b in profiles["bumps"]]

    h_theta = 2.0 * math.pi / THETA_GRID
    h_rho = 1.0 / (RHO_GRID - 1)
    theta_grid = 2.0 * math.pi * np.arange(THETA_GRID) / THETA_GRID
    rho_grid = np.linspace(0.0, 1.0, RHO_GRID)
    grid_decoded = decode(theta_grid)

    def profile_values(coefficients, rho):
        return np.polynomial.polynomial.polyval(rho, coefficients)

    h0_grid = profile_values(profiles["h0"], rho_grid)
    h1_grid = profile_values(profiles["h1"], rho_grid)
    bumps_grid = np.stack([profile_values(b, rho_grid) for b in profiles["bumps"]], axis=1)

    exactness = {}
    # boundary common fields
    gamma_A, gamma_B = harmonics(fft_decoded["common"]["gamma"])
    exactness["gamma"] = float(np.max(np.abs(evaluate_harmonics(gamma_A, gamma_B, theta_check) - check_decoded["common"]["gamma"])))
    t_A, t_B = harmonics(fft_decoded["khronon_t"])
    exactness["khronon_t"] = float(np.max(np.abs(evaluate_harmonics(t_A, t_B, theta_check) - check_decoded["khronon_t"])))
    lo_A, lo_B = harmonics(fft_decoded["common"]["log_Omega"])
    exactness["log_Omega_common"] = float(np.max(np.abs(evaluate_harmonics(lo_A, lo_B, theta_check) - check_decoded["common"]["log_Omega"])))
    q_A, q_B = harmonics(fft_decoded["q_field"])
    exactness["q"] = float(np.max(np.abs(evaluate_harmonics(q_A, q_B, theta_check) - check_decoded["q_field"])))

    # (K) khronon on the boundary: gamma eigenvalue clearance everywhere first
    gamma_grid = grid_decoded["common"]["gamma"]
    gamma_eigs = np.linalg.eigvalsh(gamma_grid)
    gamma_lorentzian_grid = bool(np.all(np.sum(gamma_eigs < 0.0, axis=-1) == 1))
    gamma_min_abs_grid = float(np.min(np.abs(gamma_eigs)))
    L_gamma = trig_derivative_sup_bound(gamma_A, gamma_B)
    gamma_min_abs_everywhere = gamma_min_abs_grid - L_gamma * h_theta / 2.0 - SAFETY
    gamma_inverse_norm = 1.0 / gamma_min_abs_everywhere if gamma_min_abs_everywhere > 0 else math.inf
    t_sup = trig_sup_bound(t_A, t_B)
    dt_sup = trig_derivative_sup_bound(t_A, t_B)
    L_T = 2.0 * t_sup * gamma_inverse_norm * dt_sup + t_sup**2 * gamma_inverse_norm**2 * L_gamma
    T_norm2_grid = np.einsum("pm,pmn,pn->p", grid_decoded["khronon_t"], np.linalg.inv(gamma_grid), grid_decoded["khronon_t"])
    T_norm2_max_everywhere = float(np.max(T_norm2_grid)) + L_T * h_theta / 2.0 + SAFETY
    khronon = {
        "gamma_lorentzian_on_grid": gamma_lorentzian_grid,
        "gamma_min_abs_eigenvalue_grid": gamma_min_abs_grid,
        "gamma_lipschitz_theta": L_gamma,
        "gamma_min_abs_eigenvalue_everywhere": gamma_min_abs_everywhere,
        "T_norm2_max_grid": float(np.max(T_norm2_grid)),
        "T_norm2_lipschitz_theta": L_T,
        "T_norm2_max_everywhere": T_norm2_max_everywhere,
        "pass": bool(gamma_lorentzian_grid and gamma_min_abs_everywhere > SIGNATURE_EIGENVALUE_MARGIN and T_norm2_max_everywhere < -TIMELIKE_MARGIN),
    }

    # (R) rotation chart clearance everywhere via the triangle inequality
    def vector_field_sup(A: np.ndarray, B: np.ndarray) -> float:
        # |a + sum_k (b_k cos + c_k sin)| <= |a| + sum_k sqrt(|b_k|^2 + |c_k|^2)
        return float(np.linalg.norm(A[0]) + np.sum(np.sqrt(np.sum(A[1:] ** 2, axis=1) + np.sum(B[1:] ** 2, axis=1))))

    q_sup = vector_field_sup(q_A, q_B)

    sides = {}
    for side in SIDES:
        block = fft_decoded["sides"][side]
        g_A, g_B = harmonics(block["g_trace"])
        J_A, J_B = harmonics(block["boundary_jet_J1"])
        C_A, C_B = harmonics(block["interior_bump_C"])
        check_block = check_decoded["sides"][side]
        exactness[f"{side}.g_trace"] = float(np.max(np.abs(evaluate_harmonics(g_A, g_B, theta_check) - check_block["g_trace"])))
        exactness[f"{side}.J1"] = float(np.max(np.abs(evaluate_harmonics(J_A, J_B, theta_check) - check_block["boundary_jet_J1"])))
        exactness[f"{side}.C"] = float(np.max(np.abs(evaluate_harmonics(C_A, C_B, theta_check) - check_block["interior_bump_C"])))
        r_A, r_B = harmonics(fft_decoded["r_field"][side])
        exactness[f"{side}.r"] = float(np.max(np.abs(evaluate_harmonics(r_A, r_B, theta_check) - check_decoded["r_field"][side])))

        # ---- (M) metric everywhere
        gJ_A, gJ_B = _sym5_from_packed(J_A[:, :15]), _sym5_from_packed(J_B[:, :15])
        gC_A, gC_B = _sym5_from_packed(C_A[:, :, :15]), _sym5_from_packed(C_B[:, :, :15])
        g0_A = g_A.copy()
        g0_A[0] = g0_A[0] - REFERENCE_METRIC          # X0 - X_inf harmonics
        # L_theta: sup over rho of sum_k k ||A_k(rho)|| with |h0| <= sup_h0, |h1| <= sup_h1, |b_j| <= sup_bumps
        k = np.arange(g_A.shape[0])
        L_theta_metric = float(np.sum(k * (
            sup_h0 * (_fro(g0_A) + _fro(g_B))
            + sup_h1 * (_fro(gJ_A) + _fro(gJ_B))
            + sum(sup_bumps[j] * (_fro(gC_A[:, j]) + _fro(gC_B[:, j])) for j in range(K))
        )))
        L_rho_metric = float(
            sup_dh0 * trig_sup_bound(g0_A, g_B)
            + sup_dh1 * trig_sup_bound(gJ_A, gJ_B)
            + sum(sup_dbumps[j] * trig_sup_bound(gC_A[:, j], gC_B[:, j]) for j in range(K))
        )
        grid_block = grid_decoded["sides"][side]
        g_bulk_grid = (
            REFERENCE_METRIC[None, None]
            + h0_grid[:, None, None, None] * (grid_block["g_trace"] - REFERENCE_METRIC)[None]
            + h1_grid[:, None, None, None] * _sym5_from_packed(grid_block["boundary_jet_J1"][:, :15])[None]
            + np.einsum("rk,pkij->rpij", bumps_grid, _sym5_from_packed(grid_block["interior_bump_C"][:, :, :15]))
        )
        eigs = np.linalg.eigvalsh(g_bulk_grid)
        lorentzian_grid = bool(np.all(np.sum(eigs < 0.0, axis=-1) == 1))
        min_abs_grid = float(np.min(np.abs(eigs)))
        weyl_radius = L_theta_metric * h_theta / 2.0 + L_rho_metric * h_rho / 2.0 + SAFETY
        min_abs_everywhere = min_abs_grid - weyl_radius
        metric = {
            "lorentzian_on_grid": lorentzian_grid,
            "min_abs_eigenvalue_grid": min_abs_grid,
            "lipschitz_theta": L_theta_metric,
            "lipschitz_rho": L_rho_metric,
            "weyl_radius": weyl_radius,
            "min_abs_eigenvalue_everywhere": min_abs_everywhere,
            "pass": bool(lorentzian_grid and min_abs_everywhere > SIGNATURE_EIGENVALUE_MARGIN),
        }

        # ---- (O) Omega everywhere (scalar log Omega)
        lo_trace_A, lo_trace_B = harmonics(block["log_Omega_trace"])
        k1 = np.arange(lo_trace_A.shape[0])
        L_theta_omega = float(np.sum(k1 * (
            sup_h0 * (np.abs(lo_trace_A) + np.abs(lo_trace_B))
            + sup_h1 * (np.abs(J_A[:, 15]) + np.abs(J_B[:, 15]))
            + sum(sup_bumps[j] * (np.abs(C_A[:, j, 15]) + np.abs(C_B[:, j, 15])) for j in range(K))
        )))
        L_rho_omega = float(
            sup_dh0 * trig_sup_bound(lo_trace_A, lo_trace_B)
            + sup_dh1 * trig_sup_bound(J_A[:, 15], J_B[:, 15])
            + sum(sup_dbumps[j] * trig_sup_bound(C_A[:, j, 15], C_B[:, j, 15]) for j in range(K))
        )
        log_omega_grid = (
            h0_grid[:, None] * grid_block["log_Omega_trace"][None]
            + h1_grid[:, None] * grid_block["boundary_jet_J1"][None, :, 15]
            + np.einsum("rk,pk->rp", bumps_grid, grid_block["interior_bump_C"][:, :, 15])
        )
        log_omega_min_grid = float(np.min(log_omega_grid))
        omega_radius = L_theta_omega * h_theta / 2.0 + L_rho_omega * h_rho / 2.0 + SAFETY
        log_omega_min_everywhere = log_omega_min_grid - omega_radius
        omega = {
            "log_Omega_min_grid": log_omega_min_grid,
            "lipschitz_theta": L_theta_omega,
            "lipschitz_rho": L_rho_omega,
            "radius": omega_radius,
            "Omega_min_everywhere": float(math.exp(log_omega_min_everywhere)),
            "pass": bool(math.exp(log_omega_min_everywhere) > OMEGA_MIN),
        }

        # ---- (R) rotation chart clearance everywhere
        r_sup = vector_field_sup(r_A, r_B)
        angle_bound = q_sup + r_sup
        rotation = {
            "sup_q": q_sup,
            "sup_r": r_sup,
            "angle_upper_bound": angle_bound,
            "angle_max_grid": float(np.max(np.arccos(np.clip((np.trace(grid_block["R_source_to_Q"], axis1=-2, axis2=-1) - 1.0) / 2.0, -1.0, 1.0)))),
            "clearance_everywhere": math.pi - angle_bound,
            "pass": bool(angle_bound < math.pi and math.pi - angle_bound > ROTATION_CUT_LOCUS_MARGIN),
        }
        sides[side] = {"metric": metric, "Omega": omega, "rotation": rotation, "pass": bool(metric["pass"] and omega["pass"] and rotation["pass"])}

    exact_ok = bool(max(exactness.values()) < EXACTNESS_TOLERANCE)
    return {
        "N": N,
        "K": K,
        "member_id": member["member_id"],
        "authoritative_free_central_sha256": member["authoritative_free_central_f64le"]["sha256"],
        "harmonic_exactness": {"worst_reconstruction_error_off_grid": max(exactness.values()), "per_field": exactness, "pass": exact_ok},
        "profile_sups": {"h0": sup_h0, "h1": sup_h1, "bumps": sup_bumps, "dh0": sup_dh0, "dh1": sup_dh1, "dbumps": sup_dbumps},
        "khronon": khronon,
        "sides": sides,
        "pass": bool(exact_ok and khronon["pass"] and all(s["pass"] for s in sides.values())),
    }


def build_payload() -> dict[str, Any]:
    bundle = _load_json(BUNDLE_PATH, BUNDLE_SHA256)
    v56611 = _load_json(V56611_PATH, V56611_SHA256)
    if v56611["decision"].get("pinned_members_margins_on_dense_collar_pass") is not True:
        raise EverywhereGateError("upstream dense-grid certificate missing")
    if v56611["decision"].get("pinned_members_margins_everywhere_on_collar_pass") is not False:
        raise EverywhereGateError("this gate expects the upstream everywhere key to be fail-closed")
    decoder = load_pinned_decoder()
    members = [member_certificate(decoder, bundle, member) for member in bundle["primary_members"]]
    all_pass = bool(all(m["pass"] for m in members))
    summary = {
        "min_abs_metric_eigenvalue_everywhere": min(min(s["metric"]["min_abs_eigenvalue_everywhere"] for s in m["sides"].values()) for m in members),
        "max_weyl_radius": max(max(s["metric"]["weyl_radius"] for s in m["sides"].values()) for m in members),
        "min_Omega_everywhere": min(min(s["Omega"]["Omega_min_everywhere"] for s in m["sides"].values()) for m in members),
        "max_T_norm2_everywhere": max(m["khronon"]["T_norm2_max_everywhere"] for m in members),
        "min_cut_locus_clearance_everywhere": min(min(s["rotation"]["clearance_everywhere"] for s in m["sides"].values()) for m in members),
        "worst_harmonic_reconstruction_error": max(m["harmonic_exactness"]["worst_reconstruction_error_off_grid"] for m in members),
    }
    scientific = {
        "margins": {"signature": SIGNATURE_EIGENVALUE_MARGIN, "Omega_min": OMEGA_MIN, "timelike": TIMELIKE_MARGIN, "cut_locus": ROTATION_CUT_LOCUS_MARGIN, "source": "v5.6.4 TOLERANCES, transcribed"},
        "grid": {"theta": THETA_GRID, "rho": RHO_GRID, "fft_points": FFT_POINTS, "safety_padding": SAFETY},
        "members": members,
        "summary": summary,
        "method": {
            "metric": "Weyl eigenvalue perturbation + Lipschitz constants from exact harmonics (theta) and Bernstein-bounded profile derivatives (rho)",
            "Omega": "Lipschitz on log Omega with the same constants",
            "khronon": "derivative bound of t^T gamma^{-1} t with ||gamma^{-1}|| from the everywhere eigenvalue clearance of gamma",
            "rotation": "bi-invariant triangle inequality angle(exp(q) exp(r)) <= |q| + |r| and sup of degree-one vector fields",
            "rounding": "not interval arithmetic; floating-point rounding is padded by SAFETY = 1e-9, far below every recorded clearance",
        },
        "machine_checked": {
            "harmonic_structure_verified_off_grid": all(m["harmonic_exactness"]["pass"] for m in members),
            "all_margins_everywhere": all_pass,
        },
        "analytic_not_machine_checked": [
            "Weyl's inequality, the Lipschitz-to-oscillation step and the SO(3) triangle inequality (classical)",
            "that floating-point rounding of the eigenvalue solver and FFT stays below SAFETY (not interval-certified)",
        ],
    }
    decision = {
        "pinned_members_margins_everywhere_certified_pass": all_pass,
        "uniform_N_to_infinity_bridge_pass": False,
        "uniform_stability_pass": False,
        "spectral_N_convergence_pass": False,
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
        "classification": "theory_only;margins_everywhere;weyl_lipschitz;restricted_spectral_family;fail_closed_bridge",
        "decision": decision,
        "fixed_before_run": {
            "THETA_GRID": THETA_GRID, "RHO_GRID": RHO_GRID, "FFT_POINTS": FFT_POINTS, "MAX_HARMONIC": MAX_HARMONIC,
            "EXACTNESS_TOLERANCE": EXACTNESS_TOLERANCE, "SAFETY": SAFETY, "RANDOM_CHECK_SEED": RANDOM_CHECK_SEED,
            "margins": {"signature": SIGNATURE_EIGENVALUE_MARGIN, "Omega_min": OMEGA_MIN, "timelike": TIMELIKE_MARGIN, "cut_locus": ROTATION_CUT_LOCUS_MARGIN},
        },
        "scientific": scientific,
        "independence_boundary": {
            "imports_pinned_kinematic_decoder": True,
            "pinned_decoder": {"path": DECODER_PATH.name, "sha256": DECODER_SHA256},
            "imports_action_evaluators": False,
            "imports_route_c_or_ad_fd5_modules": False,
            "reads_upstream_expected_values": False,
            "edits_v5_6_6_11": False,
        },
        "open_obligation": {
            "flip_upstream_key": "after independent review, v5.6.6.11's pinned_members_margins_everywhere_on_collar_pass may cite this receipt; not edited here (write lease)",
            "interval_arithmetic": "optional hardening of the rounding padding",
        },
        "evidence_boundary": (
            "Machine-checked: exact harmonic structure of the pinned members' fields (verified off-grid), Weyl + Lipschitz "
            "clearances for the metric signature and Omega on the whole collar, the khronon margin on the whole boundary, "
            "and the SO(3) chart clearance everywhere, all with the v5.6.4 margins. Not proven: the bridge, C1/N1, B4/B5."
        ),
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "v5_6_4_2_pointwise_decoder_sha256": DECODER_SHA256,
            "v5_6_6_11_receipt_sha256": V56611_SHA256,
        },
        "provenance": {
            "generator": {"path": str(Path(__file__).resolve().relative_to(REPO)), "sha256": _sha256(Path(__file__))},
            "test": {"path": str(TEST.relative_to(REPO)), "sha256": _sha256(TEST) if TEST.exists() else None},
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "scientific_payload_sha256": _canonical_sha256(scientific),
    }
    return payload


def main() -> None:
    payload = build_payload()
    if not payload["decision"]["pinned_members_margins_everywhere_certified_pass"]:
        raise EverywhereGateError("everywhere-margins certificate failed")
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    s = payload["scientific"]["summary"]
    print(
        f"everywhere={payload['decision']['pinned_members_margins_everywhere_certified_pass']} "
        f"min|eig|={s['min_abs_metric_eigenvalue_everywhere']:.4f} weyl_radius<={s['max_weyl_radius']:.2e} "
        f"minOmega={s['min_Omega_everywhere']:.4f} maxT={s['max_T_norm2_everywhere']:.4f} cut={s['min_cut_locus_clearance_everywhere']:.3f} "
        f"harm_err={s['worst_harmonic_reconstruction_error']:.1e}"
    )


if __name__ == "__main__":
    main()
