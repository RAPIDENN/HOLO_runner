#!/usr/bin/env python3
"""Ideal-rational theta-stencil truncation formula and float-evaluated
candidate jet envelopes for the pinned Route C members (v5.6.6.18).

Scope granted by the v12/v18 exchange in ~/.agent-bridge: analyse the bias of
the nine-point theta stencils (h = 0.03, formal order 8) used by the precision
Route C (v5.6.6.5, long double), without touching the density, free-parameter
FD5 axis or quadrature.  Nothing here is a bound on B_FD itself.

Analytic model.  A static, non-transitive lexical audit of thirteen named
functions is consistent with a manually stated entire-function pipeline:
degree-one trigonometric free data, Rodrigues rotations, finite real shifts,
products, minors and radial polynomials.  It is not a closed call-graph proof.
The Rodrigues switch is screened on a dense float grid with a float Lipschitz
margin; neither that screen nor the strip arithmetic uses directed rounding.

Exact formula.  For an entire F and the ideal rational nine-point
first-derivative stencil, D_h F - F' is bounded by h^8 C1 sup|F^(9)|.  The
second-derivative analogue is h^8 C2 sup|F^(10)| because its ninth moment
vanishes.  Taylor remainder and Cauchy's estimate give the analytic formula;
ordinary float propagation through the stated pipeline produces the recorded
candidate envelopes.  The two finite-difference layers are composed, with
the inner R0 derivative error propagated into the outer jet.

The generator evaluates 79 channel components x 6 jet entries x 11 radial
nodes x 2 collars x 3 members.  The receipt serializes maxima per node and
one complete component vector per member/side, not the full 31,284-entry
component ledger.  Radial exactness means exactness for the evaluator's
polynomial continuation, not for the separately declared zero extension.

Crucial boundary: the rational moment identities and Taylor/Cauchy formula
are exact mathematics, but the listed candidate envelopes do not enclose
rounding in the production long-double weights, stencil sums, transcendental
evaluations or upstream pipeline.  A pinned N=3, rho=0, log(Omega) qrr canary
has exact polynomial curvature zero and ideal candidate zero, yet production
returns a nonzero rounding residue.  This is not a production total-error
bound.

Also not established: density or action-JVP bias, the free FD5 axis, the
declared radial zero-extension semantics, Q -> infinity, B_FD, the bridge,
C1/N1 or B4/B5.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import platform
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_route_c_theta_stencil_jet_bias_bound_v5_6_6_18.json"
TEST = HERE / "test_one_omega_topological_so3_route_c_theta_stencil_jet_bias_bound_v5_6_6_18.py"
SCHEMA = "holo.one-omega-topological-so3-route-c-theta-stencil-jet-bias-bound-v5-6-6-18.v2"
FROZEN_COMMIT = "ea014fd"

LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
PRECISION_PATH = HERE / "derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5.py"
PRECISION_SHA256 = "5cf9c64fe8af45b55899275b2af1a9d55c706a138479e2cbd3a47ca4b270eca8"
ROUTE_C_PATH = HERE / "derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3.py"
ROUTE_C_SHA256 = "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"
V56612_PATH = ARTIFACTS / "one_omega_topological_so3_route_c_stencil_bias_v5_6_6_12.json"
V56612_SHA256 = "2c7c170b1e23fb32cb2c53c9d232069e3a8100c2950ebe9206813c6a5809ab23"

# Fixed before run.
SEED = 56618
SIGMA_GRID = tuple(float(x) for x in np.linspace(0.3, 2.5, 23))
DELTA_GRID = tuple(float(x) for x in np.linspace(0.2, 1.5, 14))
BOUND_INFLATION = 1.0 + 1.0e-6  # heuristic float cushion; not directed-rounding certification
BRANCH_THRESHOLD = 1.0e-12  # the Rodrigues small-angle switch in v5.6.6.5
BRANCH_CERTIFICATION_GRID = 20001
BRANCH_MINIMUM_MARGIN = 1.0e-3
CONTRAST_POINTS_PER_SIDE = 3
CONTRAST_FINE_THETA_STEP = "0.003"
CONTRAST_ROUNDING_ALLOWANCE = 1.0e-13
JET_ENTRIES = ("q", "qt", "qr", "qtt", "qtr", "qrr")
SIDES = ("plus", "minus")
REFERENCE_METRIC = np.diag((-1.64, 1.17, 1.31, 1.46, 1.17))
JET_FUNCTIONS = (
    "_series_ld",
    "_basis_values_ld",
    "_so3_exp_ld",
    "_matrix_theta_derivative_ld",
    "_trace_ambient_value_ld",
    "_radial_bumps_ld",
    "_ambient_value_ld",
    "_antisymmetric_tensor_ld",
    "_determinant3_ld",
    "_pullback_vector_ld",
    "_nine_point_jet_ld",
    "_weighted_sum",
    "stable_bulk_jet",
)
FORBIDDEN_IN_JET_PIPELINE = ("linalg.inv", "np.log", "math.log", "np.abs", "np.where", "np.sign", "arccos", "arcsin", "arctan", "np.exp", "math.exp", "np.power", "**0.5")


class ThetaStencilGateError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_precision() -> tuple[Any, Any]:
    if _sha256(PRECISION_PATH) != PRECISION_SHA256:
        raise ThetaStencilGateError("v5.6.6.5 byte pin drift")
    if _sha256(ROUTE_C_PATH) != ROUTE_C_SHA256:
        raise ThetaStencilGateError("v5.6.6.3 byte pin drift")
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from first_principles_audit.prediction_factory import (  # noqa: E402  (byte-pinned above)
        derive_one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5 as precision,
    )

    route_c = precision.route_c
    if Path(route_c.__file__).resolve() != ROUTE_C_PATH.resolve():
        raise ThetaStencilGateError("precision route does not import the pinned Route C")
    if float(precision.STABLE_THETA_STEP) != 0.03 or float(precision.STABLE_RHO_STEP) != 0.03:
        raise ThetaStencilGateError("production stencil steps drift")
    return precision, route_c


# --------------------------------------------------------------------------
# exact stencil facts (rational)
# --------------------------------------------------------------------------
def stencil_certificate(precision: Any) -> dict[str, Any]:
    first = {int(k): Fraction(float(v)).limit_denominator(10**6) for k, v in precision.FIRST_WEIGHTS.items()}
    second = {int(k): Fraction(float(v)).limit_denominator(10**6) for k, v in precision.SECOND_WEIGHTS.items()}
    expected_first = {-4: Fraction(1, 280), -3: Fraction(-4, 105), -2: Fraction(1, 5), -1: Fraction(-4, 5), 1: Fraction(4, 5), 2: Fraction(-1, 5), 3: Fraction(4, 105), 4: Fraction(-1, 280)}
    expected_second = {-4: Fraction(-1, 560), -3: Fraction(8, 315), -2: Fraction(-1, 5), -1: Fraction(8, 5), 0: Fraction(-205, 72), 1: Fraction(8, 5), 2: Fraction(-1, 5), 3: Fraction(8, 315), 4: Fraction(-1, 560)}
    if first != expected_first or second != expected_second:
        raise ThetaStencilGateError("stencil weights differ from the declared rationals")
    actual_first_m0 = sum((precision.LD(v) for v in precision.FIRST_WEIGHTS.values()), precision.LD(0))
    actual_second_m0 = sum((precision.LD(v) for v in precision.SECOND_WEIGHTS.values()), precision.LD(0))
    moments_first = [sum(w * Fraction(j) ** m for j, w in first.items()) / math.factorial(m) for m in range(11)]
    moments_second = [sum(w * Fraction(j) ** m for j, w in second.items()) / math.factorial(m) for m in range(11)]
    exact_first = moments_first[1] == 1 and all(moments_first[m] == 0 for m in range(11) if m not in (1, 9, 10)) and moments_first[10] == 0
    exact_second = moments_second[2] == 1 and all(moments_second[m] == 0 for m in range(10) if m != 2)
    C1 = sum(abs(w) * Fraction(abs(j)) ** 9 for j, w in first.items()) / math.factorial(9)
    C2 = sum(abs(w) * Fraction(abs(j)) ** 10 for j, w in second.items()) / math.factorial(10)
    return {
        "first_weights": {str(j): str(w) for j, w in first.items()},
        "second_weights": {str(j): str(w) for j, w in second.items()},
        "first_moments_0_to_10": [str(m) for m in moments_first],
        "second_moments_0_to_10": [str(m) for m in moments_second],
        "first_exact_through_degree_8_and_tenth_moment_zero": bool(exact_first),
        "second_exact_through_degree_8_and_ninth_moment_zero": bool(exact_second and moments_second[9] == 0),
        "remainder_constants": {"C1_first_order9": str(C1), "C2_second_order10": str(C2), "C1_float": float(C1), "C2_float": float(C2), "sum_abs_first_weights": float(sum(abs(w) for w in first.values()))},
        "production_longdouble_weight_zero_moment_residuals": {
            "first_m0": np.format_float_scientific(actual_first_m0, unique=False, precision=21),
            "second_m0": np.format_float_scientific(actual_second_m0, unique=False, precision=21),
            "second_m0_over_h_squared": np.format_float_scientific(
                actual_second_m0 / precision.STABLE_RHO_STEP**2, unique=False, precision=21
            ),
            "note": "nonzero production-weight residuals are outside the ideal-rational moment certificate",
        },
        "remainder_form": (
            "first: |D_h F - F'| <= h^8 C1 sup|F^(9)|; second: |D_h^2 F - F''| <= h^8 C2 sup|F^(10)| (ninth moment "
            "vanishes by symmetry); mixed: first-derivative bound applied to the exact radial derivative"
        ),
        "pass": bool(exact_first and exact_second and moments_second[9] == 0),
        "_C1": float(C1),
        "_C2": float(C2),
        "_sum_abs_first": float(sum(abs(w) for w in first.values())),
    }


# --------------------------------------------------------------------------
# static lexical inventory of selected jet-pipeline functions
# --------------------------------------------------------------------------
def pipeline_inventory(precision: Any) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    all_clean = True
    for name in JET_FUNCTIONS:
        source = inspect.getsource(getattr(precision, name))
        hits = [token for token in FORBIDDEN_IN_JET_PIPELINE if token in source]
        transcendental = [token for token in ("np.sin", "np.cos", "np.sqrt", "np.exp") if token in source]
        branch = "angle < LD(\"1e-12\")" in source or "angle < LD('1e-12')" in source
        rows[name] = {"forbidden_hits": hits, "transcendental_calls": transcendental, "small_angle_branch": branch}
        if hits:
            all_clean = False
    rodrigues = rows["_so3_exp_ld"]
    rodrigues_ok = rodrigues["small_angle_branch"] and set(rodrigues["transcendental_calls"]) == {"np.sin", "np.cos", "np.sqrt"}
    others_ok = all(not row["transcendental_calls"] for name, row in rows.items() if name not in ("_so3_exp_ld", "_basis_values_ld", "_series_ld"))
    basis_ok = set(rows["_basis_values_ld"]["transcendental_calls"]) <= {"np.sin", "np.cos"}
    return {
        "scope": "nontransitive_static_lexical_audit",
        "function_count": len(JET_FUNCTIONS),
        "functions": rows,
        "manual_entire_in_theta_argument": (
            "trigonometric series of degree <= 1 (entire); Rodrigues exp(hat v) = I + sin(a)/a hat(v) + (1-cos a)/a^2 "
            "hat(v)^2 with a^2 = v.v is entire in the components of v because sin(sqrt x)/sqrt x and (1 - cos sqrt x)/x "
            "are entire in x; the inner derivative is a finite combination of real shifts; products, minors and the "
            "radial profiles are polynomial; this mathematical description is not established by transitive call-graph analysis"
        ),
        "basis_transcendentals_allowlisted": bool(basis_ok),
        "pass": bool(all_clean and rodrigues_ok and others_ok and basis_ok),
    }


# --------------------------------------------------------------------------
# strip-bound arithmetic
# --------------------------------------------------------------------------
def _series_bounds(coefficients: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(constant-mode magnitude, sum of oscillating-mode magnitudes) per channel of a (N, ...) block."""
    c = np.abs(np.asarray(coefficients, dtype=float))
    b0 = c[0]
    b1 = c[1:].sum(axis=0) if c.shape[0] > 1 else np.zeros_like(b0)
    return b0, b1


def _strip(b0: np.ndarray, b1: np.ndarray, sigma: float) -> np.ndarray:
    return b0 + b1 * math.cosh(sigma)


def _rotation_strip_bound(b0: np.ndarray, b1: np.ndarray, s: float) -> float:
    """||exp(hat r(z))||_2 <= exp(sqrt2 ||r(z)||_2) on |Im z| <= s (complex cross product: ||hat v|| <= sqrt2 ||v||)."""
    return math.exp(math.sqrt(2.0) * float(np.linalg.norm(_strip(b0, b1, s))))


def _permanent3(matrix: np.ndarray) -> float:
    m = matrix
    return float(
        m[0, 0] * (m[1, 1] * m[2, 2] + m[1, 2] * m[2, 1])
        + m[0, 1] * (m[1, 0] * m[2, 2] + m[1, 2] * m[2, 0])
        + m[0, 2] * (m[1, 0] * m[2, 1] + m[1, 1] * m[2, 0])
    )


def _radial_profiles(rho: float, K: int) -> dict[str, np.ndarray]:
    """h0, h1, bumps and their first two rho-derivatives (exact polynomials), as used by v5.6.6.5."""
    r = rho
    h0 = 1.0 - 10.0 * r**3 + 15.0 * r**4 - 6.0 * r**5
    h0_1 = -30.0 * r**2 + 60.0 * r**3 - 30.0 * r**4
    h0_2 = -60.0 * r + 180.0 * r**2 - 120.0 * r**3
    h1 = r * h0
    h1_1 = h0 + r * h0_1
    h1_2 = 2.0 * h0_1 + r * h0_2
    x = 2.0 * r - 1.0
    legendre = [np.polynomial.legendre.Legendre.basis(j) for j in range(K)]
    env = np.polynomial.Polynomial([0, 0, 0, 64.0]) * np.polynomial.Polynomial([1, -1.0]) ** 3  # 64 r^3 (1-r)^3
    bumps = []
    bumps_1 = []
    bumps_2 = []
    for j in range(K):
        leg = np.polynomial.Polynomial(legendre[j].convert(kind=np.polynomial.Polynomial).coef)  # in x
        leg_r = leg(np.polynomial.Polynomial([-1.0, 2.0]))  # x = 2r - 1
        b = env * leg_r
        bumps.append(float(b(r)))
        bumps_1.append(float(b.deriv(1)(r)))
        bumps_2.append(float(b.deriv(2)(r)))
    del x
    return {
        "h0": np.asarray([h0, h0_1, h0_2]),
        "h1": np.asarray([h1, h1_1, h1_2]),
        "bumps": np.asarray([bumps, bumps_1, bumps_2]),
    }


def _block(free: np.ndarray, contract: Mapping[str, Any], name: str) -> np.ndarray:
    spec = contract["free_layout"]["blocks"][name]
    return free[int(spec["start"]):int(spec["stop"])].reshape(tuple(int(x) for x in spec["shape"]))


def member_side_bounds(route_c: Any, free: np.ndarray, contract: Mapping[str, Any], side: str) -> dict[str, Any]:
    """Coefficient-magnitude data of one collar, independent of sigma."""
    b = {}
    for name in ("common.gamma", "common.log_Omega", "common.varphi_E0", "common.A_E0", f"{side}.Y", f"{side}.metric_free", f"{side}.A_perp", f"{side}.B0_full", f"{side}.r_E0", f"{side}.boundary_jet_J1", f"{side}.interior_bump_C"):
        b[name.split(".")[1]] = _series_bounds(_block(free, contract, name))
    b["sign"] = float(route_c.SIDE_RADIAL_SIGN[side])
    return b


def jet_bound_ledger(
    route_c: Any,
    bounds: Mapping[str, Any],
    rho: float,
    K: int,
    h: float,
    C1: float,
    C2: float,
    sum_abs_first: float,
) -> dict[str, np.ndarray]:
    """Best float-evaluated ideal-model candidate envelope over sigma and delta."""
    pairs5 = [tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5]
    pairs4 = [tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC4]
    sign = bounds["sign"]
    prof = _radial_profiles(rho, K)
    ref = np.zeros(64)
    ref[:15] = np.asarray([REFERENCE_METRIC[i, j] for i, j in pairs5])
    best = {entry: np.full(79, np.inf) for entry in JET_ENTRIES}
    best_meta = {entry: [None] * 79 for entry in JET_ENTRIES}
    r0, r1 = bounds["r_E0"]
    for sigma in SIGMA_GRID:
        # strip bounds of the free-data series
        g0, g1 = bounds["gamma"]
        gamma_s = _strip(g0, g1, sigma)
        Yp = float(_strip(np.zeros(1), bounds["Y"][1], sigma)[0])  # |Y'(z)| on the strip
        Ypp = Yp  # |Y''(z)| on the strip: same magnitude bound for degree <= 1
        mf = _strip(*bounds["metric_free"], sigma)
        d_s, a_s = mf[:4], float(mf[4])
        logO = float(_strip(*bounds["log_Omega"], sigma)[0])
        phi0 = _strip(*bounds["varphi_E0"], sigma)
        A0 = _strip(*bounds["A_E0"], sigma)  # (4, 3)
        Aperp = _strip(*bounds["A_perp"], sigma)
        B0 = _strip(*bounds["B0_full"], sigma).reshape(30)
        J1 = _strip(*bounds["boundary_jet_J1"], sigma)
        C = _strip(*bounds["interior_bump_C"], sigma)  # (K, 64)
        M_R = _rotation_strip_bound(r0, r1, sigma)
        Yg = np.asarray([Yp, Yp, 0.0, 0.0])
        # trace metric (5x5 entrywise strip bounds)
        gm = np.zeros((4, 4))
        for value, (i, j) in zip(gamma_s, pairs4):
            gm[i, j] = gm[j, i] = value
        upper = gm + np.outer(d_s, Yg) + np.outer(Yg, d_s) + a_s * np.outer(Yg, Yg)
        cross = d_s + a_s * Yg
        Mg = np.zeros((5, 5))
        Mg[:4, :4] = upper
        Mg[:4, 4] = Mg[4, :4] = cross
        Mg[4, 4] = a_s
        phi_b = np.full(3, M_R * float(np.linalg.norm(phi0)))
        for delta in DELTA_GRID:
            M_R_wide = _rotation_strip_bound(r0, r1, sigma + delta)
            inner_taylor = M_R_wide / delta + h**8 * C1 * math.factorial(9) * M_R_wide / delta**9
            inner_crude = sum_abs_first * M_R / h
            M_dR0 = min(inner_taylor, inner_crude)
            A_source = np.zeros((4, 3))
            for mu in range(4):
                base = M_R * M_R * math.sqrt(2.0) * float(np.linalg.norm(A0[mu]))
                A_source[mu] = base + (M_R * M_dR0 if mu < 2 else 0.0)
            A_full = np.zeros((5, 3))
            A_full[:4] = A_source + np.outer(Yg, Aperp)
            A_full[4] = Aperp
            trace = np.zeros(64)
            trace[:15] = [Mg[i, j] for i, j in pairs5]
            trace[15] = logO
            trace[16:19] = phi_b
            trace[19:34] = A_full.reshape(15)
            trace[34:64] = B0
            # ambient value and its exact rho-derivative, strip bounds at this node
            def ambient(order: int) -> np.ndarray:
                h0, h1, bumps = prof["h0"][order], prof["h1"][order], prof["bumps"][order]
                out = abs(h0) * (trace + np.abs(ref)) + abs(h1) * J1 + np.einsum("k,kc->c", np.abs(bumps), C)
                if order == 0:
                    out = out + np.abs(ref)
                return out

            BJ = np.zeros((5, 5))
            BJ[:4, :4] = np.eye(4)
            BJ[4, :4] = Yg
            BJ[4, 4] = abs(sign)

            def pull(amb: np.ndarray) -> np.ndarray:
                metric = np.zeros((5, 5))
                for value, (i, j) in zip(amb[:15], pairs5):
                    metric[i, j] = metric[j, i] = value
                pulled_metric = BJ.T @ metric @ BJ
                pulled_conn = BJ.T @ amb[19:34].reshape(5, 3)
                Bten = amb[34:64].reshape(10, 3)
                pulled_B = np.zeros((10, 3))
                for position, target in enumerate(route_c.B_TRIPLES):
                    for source_position, source in enumerate(route_c.B_TRIPLES):
                        pulled_B[position] += _permanent3(BJ[np.ix_(source, target)]) * Bten[source_position]
                out = np.zeros(79)
                out[:15] = [pulled_metric[i, j] for i, j in pairs5]
                out[15:19] = amb[15:19]
                out[19:34] = pulled_conn.reshape(15)
                out[34:64] = pulled_B.reshape(30)
                reference = BJ.T @ np.abs(REFERENCE_METRIC) @ BJ
                out[64:79] = [reference[i, j] for i, j in pairs5]
                return out

            M_F = pull(ambient(0))
            M_Frho = pull(ambient(1))
            # outer stencil errors (Cauchy on the strip sigma)
            outer_qt = h**8 * C1 * math.factorial(9) * M_F / sigma**9
            outer_qtt = h**8 * C2 * math.factorial(10) * M_F / sigma**10
            outer_qtr = h**8 * C1 * math.factorial(9) * M_Frho / sigma**9
            # inner error of the trace decoder (real line), only in A_trace rows 0,1 -> components 19..24
            E0 = h**8 * C1 * math.factorial(9) * M_R / sigma**9
            E1 = h**8 * C1 * math.factorial(10) * M_R / sigma**10
            E2 = h**8 * C1 * math.factorial(11) * M_R / sigma**11
            R1 = M_R / sigma
            R2 = 2.0 * M_R / sigma**2
            inner_val = E0
            inner_d1 = R1 * E0 + E1
            inner_d2 = R2 * E0 + 2.0 * R1 * E1 + E2
            h0, h0_1, h0_2 = prof["h0"]
            inner = {entry: np.zeros(79) for entry in JET_ENTRIES}
            inner["q"][19:25] = abs(h0) * inner_val
            inner["qt"][19:25] = abs(h0) * inner_d1
            inner["qtt"][19:25] = abs(h0) * inner_d2
            inner["qr"][19:25] = abs(h0_1) * inner_val
            inner["qrr"][19:25] = abs(h0_2) * inner_val
            inner["qtr"][19:25] = abs(h0_1) * inner_d1
            total = {
                "q": inner["q"],
                "qt": outer_qt + inner["qt"],
                "qr": inner["qr"],
                "qtt": outer_qtt + inner["qtt"],
                "qtr": outer_qtr + inner["qtr"],
                "qrr": inner["qrr"],
            }
            for entry in JET_ENTRIES:
                candidate = total[entry] * BOUND_INFLATION
                better = candidate < best[entry]
                best[entry] = np.where(better, candidate, best[entry])
                for index in np.nonzero(better)[0]:
                    best_meta[entry][index] = (sigma, delta)
    return {"bounds": best, "parameters": best_meta}


# --------------------------------------------------------------------------
# Rodrigues branch float screen
# --------------------------------------------------------------------------
def screen_rodrigues_branch(route_c: Any, free: np.ndarray, contract: Mapping[str, Any]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    all_ok = True
    theta = np.linspace(0.0, 2.0 * math.pi, BRANCH_CERTIFICATION_GRID)
    spacing = theta[1] - theta[0]
    for name in ("Q_frame.q", "plus.r_E0", "minus.r_E0"):
        coefficients = _block(free, contract, name)
        _b0, b1 = _series_bounds(coefficients)
        lipschitz = float(np.linalg.norm(b1))  # |d/dtheta ||s(theta)||| <= ||s'|| <= ||b1||
        norms = np.asarray([float(np.linalg.norm(route_c._series(coefficients, float(t)))) for t in theta])
        screened_min = float(norms.min()) - lipschitz * spacing / 2.0
        ok = screened_min >= BRANCH_MINIMUM_MARGIN
        all_ok = all_ok and ok
        rows[name] = {"grid_min": float(norms.min()), "float_lipschitz": lipschitz, "grid_lipschitz_lower_screen": screened_min, "branch_threshold": BRANCH_THRESHOLD, "pass": bool(ok)}
    return {
        "rows": rows,
        "pass": bool(all_ok),
        "scope": "dense_float_grid_plus_float_lipschitz_screen_without_directed_rounding",
        "note": "the whole-circle float screen covers real stencil shifts but is not an interval certificate",
    }


# --------------------------------------------------------------------------
# numeric contrast: production step against a ten-times finer step (same long-double code)
# --------------------------------------------------------------------------
def contrast(precision: Any, route_c: Any, bundle: Mapping[str, Any], member: Mapping[str, Any], free: np.ndarray, contract: Mapping[str, Any], ledgers: Mapping[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    LD = precision.LD
    original = precision.STABLE_THETA_STEP
    rows = []
    worst_ratio = 0.0
    all_ok = True
    nodes = list(ledgers["rho_nodes"])
    try:
        for side in SIDES:
            for _ in range(CONTRAST_POINTS_PER_SIDE):
                theta = float(rng.uniform(0.0, 2.0 * math.pi))
                node_index = int(rng.integers(0, len(nodes)))
                rho = float(nodes[node_index])
                precision.STABLE_THETA_STEP = original
                coarse = precision.stable_bulk_jet(free, contract, side, theta, rho)
                precision.STABLE_THETA_STEP = LD(CONTRAST_FINE_THETA_STEP)
                fine = precision.stable_bulk_jet(free, contract, side, theta, rho)
                precision.STABLE_THETA_STEP = original
                scale_ratio = (float(LD(CONTRAST_FINE_THETA_STEP)) / float(original)) ** 8
                entry_rows = {}
                for entry in JET_ENTRIES:
                    difference = np.abs(np.asarray(coarse[entry], dtype=float) - np.asarray(fine[entry], dtype=float))
                    bound = ledgers["ledger"][side][node_index][entry] * (1.0 + scale_ratio) + CONTRAST_ROUNDING_ALLOWANCE
                    ratio = float(np.max(difference / bound))
                    worst_ratio = max(worst_ratio, ratio)
                    ok = bool(np.all(difference <= bound))
                    all_ok = all_ok and ok
                    entry_rows[entry] = {"max_abs_difference": float(difference.max()), "max_difference_over_candidate_plus_allowance": ratio, "pass": ok}
                rows.append({"side": side, "theta": theta, "rho": rho, "entries": entry_rows})
    finally:
        precision.STABLE_THETA_STEP = original
    return {"points": rows, "worst_difference_over_candidate_plus_allowance": worst_ratio, "fine_theta_step": CONTRAST_FINE_THETA_STEP, "pass": bool(all_ok)}


# --------------------------------------------------------------------------
def production_rounding_gap_canary(precision: Any, route_c: Any, bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Expose a production residue excluded by the ideal-rational candidate.

    Component 15 is log(Omega), which the pullback leaves unchanged.  At
    rho=0, h0'', h1'' and every K<=3 bump'' vanish, so its exact qrr under the
    polynomial continuation is zero.  The ideal ledger therefore assigns
    zero, while the long-double production stencil returns a nonzero residue.
    """
    member = next(row for row in bundle["primary_members"] if int(row["N"]) == 3)
    N, K = int(member["N"]), int(member["K"])
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    free = route_c._decode_f64(member["authoritative_free_central_f64le"])
    profiles = _radial_profiles(0.0, K)
    radial_curvature_exact_zero = bool(
        profiles["h0"][2] == 0.0
        and profiles["h1"][2] == 0.0
        and np.all(profiles["bumps"][2] == 0.0)
    )
    cert = stencil_certificate(precision)
    rows: dict[str, Any] = {}
    all_expose_gap = radial_curvature_exact_zero
    for side in SIDES:
        candidate = jet_bound_ledger(
            route_c,
            member_side_bounds(route_c, free, contract, side),
            0.0,
            K,
            float(precision.STABLE_THETA_STEP),
            cert["_C1"],
            cert["_C2"],
            cert["_sum_abs_first"],
        )["bounds"]["qrr"][15]
        produced = precision.LD(
            precision.stable_bulk_jet(free, contract, side, theta=0.731, rho=0.0)["qrr"][15]
        )
        exposes_gap = bool(candidate == 0.0 and np.isfinite(produced) and abs(produced) > candidate)
        all_expose_gap = all_expose_gap and exposes_gap
        rows[side] = {
            "ideal_candidate_qrr_bound": float(candidate),
            "production_qrr": np.format_float_scientific(produced, unique=False, precision=21),
            "absolute_production_qrr": float(abs(produced)),
            "residue_exceeds_ideal_candidate": exposes_gap,
        }
    return {
        "member_id": member["member_id"],
        "N": N,
        "K": K,
        "theta": 0.731,
        "rho": 0.0,
        "component": 15,
        "channel": "log_Omega",
        "entry": "qrr",
        "exact_polynomial_continuation_qrr": 0.0,
        "radial_profile_second_derivatives_zero": radial_curvature_exact_zero,
        "sides": rows,
        "pass": bool(all_expose_gap),
        "meaning": "PASS detects a missing production-rounding term; it does not certify the production bound",
    }


# --------------------------------------------------------------------------
def build_payload() -> dict[str, Any]:
    precision, route_c = load_precision()
    bundle = route_c.load_bundle()
    if bundle["action_contract"]["exact_action_sha256"] != LITERAL_V5_2_ACTION_SHA256:
        raise ThetaStencilGateError("literal action drift")
    if _sha256(V56612_PATH) != V56612_SHA256:
        raise ThetaStencilGateError("v5.6.6.12 receipt drift")
    h = float(precision.STABLE_THETA_STEP)
    certificate = stencil_certificate(precision)
    inventory = pipeline_inventory(precision)
    C1, C2, sum_abs_first = certificate.pop("_C1"), certificate.pop("_C2"), certificate.pop("_sum_abs_first")
    raw_nodes, _ = np.polynomial.legendre.leggauss(route_c.PRIMARY_RADIAL_ORDER)
    rho_nodes = [0.0] + [float(0.5 * (x + 1.0)) for x in raw_nodes]
    rng = np.random.default_rng(SEED)
    members: dict[str, Any] = {}
    overall_max = {entry: 0.0 for entry in JET_ENTRIES}
    all_branch = True
    all_contrast = True
    for member in bundle["primary_members"]:
        N, K = int(member["N"]), int(member["K"])
        contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
        free = route_c._decode_f64(member["authoritative_free_central_f64le"])
        branch = screen_rodrigues_branch(route_c, free, contract)
        all_branch = all_branch and branch["pass"]
        ledger: dict[str, list[dict[str, np.ndarray]]] = {}
        summary: dict[str, Any] = {}
        for side in SIDES:
            bounds = member_side_bounds(route_c, free, contract, side)
            ledger[side] = []
            per_node = []
            for rho in rho_nodes:
                result = jet_bound_ledger(route_c, bounds, rho, K, h, C1, C2, sum_abs_first)
                ledger[side].append(result["bounds"])
                per_node.append({"rho": rho, **{entry: float(result["bounds"][entry].max()) for entry in JET_ENTRIES}, "argmax_component": {entry: int(result["bounds"][entry].argmax()) for entry in JET_ENTRIES}, "sigma_delta_at_argmax": {entry: result["parameters"][entry][int(result["bounds"][entry].argmax())] for entry in JET_ENTRIES}})
            worst_node = max(range(len(rho_nodes)), key=lambda k: per_node[k]["qt"] + per_node[k]["qtt"] + per_node[k]["qtr"])
            summary[side] = {
                "per_node_max_over_components": per_node,
                "max_over_nodes": {entry: float(max(row[entry] for row in per_node)) for entry in JET_ENTRIES},
                "worst_node_component_candidate_envelope": {"rho": rho_nodes[worst_node], **{entry: [float(x) for x in ledger[side][worst_node][entry]] for entry in JET_ENTRIES}},
            }
            for entry in JET_ENTRIES:
                overall_max[entry] = max(overall_max[entry], summary[side]["max_over_nodes"][entry])
        member_contrast = contrast(precision, route_c, bundle, member, free, contract, {"rho_nodes": rho_nodes, "ledger": ledger}, rng)
        all_contrast = all_contrast and member_contrast["pass"]
        members[member["member_id"]] = {"N": N, "K": K, "rodrigues_branch": branch, "jet_truncation_candidate_envelopes": summary, "contrast": member_contrast}
    rounding_canary = production_rounding_gap_canary(precision, route_c, bundle)
    scientific = {
        "statement": (
            "The ideal rational nine-point theta stencils obey the recorded exact moment identities and the stated "
            "Taylor/Cauchy truncation formula. For the three pinned members, an ordinary-float evaluation of that formula "
            "produces candidate envelopes at every production radial node, with the inner relative-rotation derivative "
            "composed with the outer stencil. These numbers are not certified upper bounds for production: float evaluation "
            "is not outward-rounded, the named-function inventory is not a transitive call-graph proof, and long-double "
            "pipeline rounding is not enclosed. Radial exactness is only with respect to the evaluator's polynomial "
            "continuation. The N=3 rho=0 log(Omega) qrr canary records a nonzero production residue against candidate zero."
        ),
        "production_theta_step": h,
        "stencil_certificate": certificate,
        "pipeline_inventory": inventory,
        "strip_bound_rules": {
            "series": "|sum c_k e^{ik(theta+iy)}| <= |c_0| + sum_{k>=1} |c_k| cosh(sigma); same for the theta-derivatives of degree-1 series",
            "rotation": "||exp(hat r(z))||_2 <= exp(sqrt2 ||r(z)||_2) with ||hat v||_2 <= sqrt2 ||v||_2 for complex v; on the real line ||R0|| = 1",
            "inner_derivative_on_strip": "min( sum|w_j| M_R(sigma)/h , M_R(sigma+delta)/delta + h^8 C1 9! M_R(sigma+delta)/delta^9 )",
            "algebraic_identity_used": "A_source = vee(R0^T hat(A_E0) R0 + R0^T D_h R0) and phi_source = R0^T varphi_E0 (the Q-frame terms cancel exactly for any dS, v5.6.6.16 G1)",
            "products_minors": "entrywise nonnegative bound matrices; 3x3 minors bounded by permanents",
            "cauchy": "sup_real |F^(n)| <= n! M_sigma / sigma^n for entire F with M_sigma = sup_{|Im z|<=sigma} |F|",
            "composition": "total = (D_h F - F') + (F' - F_true'), the second term from e = D_h R0 - R0' with |e^(k)| <= h^8 C1 (9+k)! M_R/sigma^(9+k) and ||R0^(k)|| <= k! M_R/sigma^k on the real line",
            "search": "sigma in SIGMA_GRID and delta in DELTA_GRID; the smallest float-evaluated candidate is kept per component",
            "inflation": BOUND_INFLATION,
        },
        "overall_max_candidate_envelope": overall_max,
        "candidate_envelope_accounting": {
            "component_entry_node_side_member_values_computed": len(bundle["primary_members"]) * len(SIDES) * len(rho_nodes) * len(JET_ENTRIES) * 79,
            "full_component_ledger_serialized": False,
            "serialized_scope": "maxima per node plus one complete component vector per member and side",
        },
        "production_rounding_gap_canary": rounding_canary,
        "members": members,
        "what_is_not_established": [
            "any bound on the density or the action JVP (a certified Lipschitz constant of the density on the jet range would be needed)",
            "the free-parameter FD5 axis (Codex lane)",
            "a directed-rounding enclosure of the float-evaluated candidate envelopes",
            "a transitive call-graph proof of the manually stated entire-function pipeline",
            "long-double weight, stencil-sum, transcendental and upstream-pipeline rounding; the sampled contrast allowance is empirical only",
            "a full serialized component-by-component ledger at every node",
            "anything at Q -> infinity, B_FD as a whole, the bridge, C1/N1, B4/B5",
            "equivalence between the evaluator's radial polynomial continuation outside [0,1] and the separately declared zero extension; this affects boundary radial and mixed entries",
        ],
    }
    decision = {
        "route_c_ideal_rational_theta_stencil_moment_identities_pass": bool(certificate["pass"]),
        "route_c_jet_pipeline_entire_static_lexical_audit_pass": bool(inventory["pass"]),
        "rodrigues_small_angle_branch_inactive_grid_lipschitz_float_screen_pass": bool(all_branch),
        "route_c_ideal_rational_theta_stencil_taylor_cauchy_bound_formula_pass": bool(certificate["pass"] and inventory["pass"] and all_branch),
        "route_c_production_coarse_fine_jet_difference_within_candidate_envelope_plus_allowance_sampled_pass": bool(all_contrast),
        "route_c_production_rounding_gap_canary_observed_pass": bool(rounding_canary["pass"]),
        "route_c_ideal_rational_theta_stencil_numeric_enclosure_certified_pass": False,
        "route_c_jet_pipeline_transitive_entire_callgraph_certificate_pass": False,
        "route_c_full_component_node_candidate_envelope_ledger_serialized_pass": False,
        "route_c_radial_entries_match_declared_zero_extension_semantics_pass": False,
        "route_c_production_jet_total_error_bound_pass": False,
        "route_c_theta_stencil_density_bias_bound_pass": False,
        "B_FD_rigorous_bound_pass": False,
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
        "classification": "theory_only;ideal_rational_stencil_truncation_formula;float_evaluated_candidate_envelopes;pinned_members_N123;production_total_error_uncertified;fail_closed_bridge",
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "precision_route_c_v5_6_6_5_derive_sha256": PRECISION_SHA256,
            "route_c_v5_6_6_3_derive_sha256": ROUTE_C_SHA256,
            "v5_6_6_12_receipt_sha256": V56612_SHA256,
        },
        "fixed_before_run": {
            "seed": SEED,
            "sigma_grid": list(SIGMA_GRID),
            "delta_grid": list(DELTA_GRID),
            "bound_inflation": BOUND_INFLATION,
            "branch_threshold": BRANCH_THRESHOLD,
            "branch_certification_grid": BRANCH_CERTIFICATION_GRID,
            "branch_minimum_margin": BRANCH_MINIMUM_MARGIN,
            "contrast_points_per_side": CONTRAST_POINTS_PER_SIDE,
            "contrast_fine_theta_step": CONTRAST_FINE_THETA_STEP,
            "contrast_rounding_allowance": CONTRAST_ROUNDING_ALLOWANCE,
            "jet_functions_inventoried": list(JET_FUNCTIONS),
            "forbidden_tokens": list(FORBIDDEN_IN_JET_PIPELINE),
        },
        "scientific": scientific,
        "decision": decision,
        "evidence_boundary": (
            "Exact rational stencil moments and an analytic Taylor/Cauchy formula, followed by ordinary-float candidate "
            "envelopes on pinned members and a sampled coarse/fine contrast. Neither candidate-envelope arithmetic nor "
            "production long-double rounding is enclosed; the static lexical audit is non-transitive and the branch screen "
            "uses float arithmetic. The production total-error gate is therefore FALSE, as witnessed by the serialized "
            "rounding-gap canary. No statement about density, free FD5, B_FD, Q -> infinity or bridge/C1/N1/B4/B5."
        ),
        "independence_boundary": {
            "imports": {"precision_route_c": PRECISION_PATH.name, "route_c": ROUTE_C_PATH.name},
            "no_density_evaluated": True,
            "no_quadrature": True,
            "stencil_step_modified_only_inside_contrast_and_restored": True,
        },
        "open_obligation": [
            "directed-rounding enclosure of rational-weight representation, stencil sums, transcendental evaluation and upstream pipeline",
            "transitive call-graph closure for the entire-function pipeline or an independent symbolic specification",
            "a production jet-error enclosure, then a certified density Lipschitz constant, before any lift to density or JVP",
            "free FD5 axis (Codex, v5.6.6.12 follow-up)",
            "B_FD as a whole, N -> infinity, independent audit, v5.6.1 quarantine",
        ],
        "provenance": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(), "generator": Path(__file__).name, "test": TEST.name},
    }
    payload["scientific_payload_sha256"] = _canonical_sha256(scientific)
    return payload


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in payload["decision"].items() if v}, indent=2))
    s = payload["scientific"]
    print("overall max candidate envelope:", {k: f"{v:.3e}" for k, v in s["overall_max_candidate_envelope"].items()})
    for mid, row in s["members"].items():
        print(
            f"{mid}: branch screen {row['rodrigues_branch']['pass']}, contrast worst ratio "
            f"{row['contrast']['worst_difference_over_candidate_plus_allowance']:.3e}, pass {row['contrast']['pass']}"
        )
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
