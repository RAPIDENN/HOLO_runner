#!/usr/bin/env python3
"""Full variation of the frozen one-Omega action charter, stage v1: the brane sector.

The action charter gate (``one_omega_action_charter_gate.json``) resolves C1 and N1
and leaves one explicit next action: vary g, Omega, phi, both embeddings, T and X
from that exact action and derive the interface equations, constraints and the
extended Hessian before N2-N7, C4 or P4 are reconsidered.  It also records that a
dynamical solid changes the full quadratic Hessian and that no historical wall-ADM
Hessian is inherited.

This gate performs the first stage of that obligation directly from the literal
formula strings of the charter, with no historical block consumed:

* the displayed brane action S_Sigma = S_wall0 + S_fol + S_X + S_R is transcribed
  term by term into sympy and the transcription is audited against the pinned
  strings of the charter;
* the khronon T, the three solid scalars X^a, the induced metric gamma (in ADM
  form), the brane traces Omega_Sigma and varphi^a are all varied: the background
  T=t, X^a=v x^a, gamma=eta, Omega_Sigma=1, varphi=0 is expanded to second order
  in every field simultaneously, without fixing the khronon gauge;
* the first-order variation gives the background tadpoles.  T, X^a and varphi^a
  are stationary; gamma and Omega_Sigma are not, and their tadpoles are recorded
  as the sources that the bulk junction (GHY plus bulk Omega flux) must balance.
  Nothing about that balance is claimed here;
* the second-order Lagrangian is the extended brane Hessian.  It is reduced to a
  momentum-space matrix over the eighteen brane fluctuations, decomposed into
  helicities with respect to the momentum, and checked for the two gauge null
  directions (time reparametrization and spatial diffeomorphisms), for the
  nonzero mixed solid/shift/spatial-metric second derivatives the charter asserts,
  for the four-sector Robin coupling, and against the solid quadratic invariant
  of the N7 v3 gate, which is reproduced rather than imported.

Stage v1 does not vary the bulk fields, the two embeddings or the GHY term, so it
does not derive the junction conditions, the nonlinear constraints or the
characteristics.  Every physical key (B4, B5, P2, P3, P4, N2-N7, C2-C10) stays
false.  No registry, README, manuscript, paper or PDF is modified.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "one_omega_charter_full_variation_interface_v1_gate.json"
CHARTER = HERE / "artifacts" / "one_omega_action_charter_gate.json"
SCHEMA = "holo.one-omega-charter-full-variation-interface.v1"
ROUTE_ID = "canonical_one_Omega_backreacted_wall_with_rank_full_solid_v1"

EXPECTED_CHARTER_DIGESTS = {
    "action_charter_digest": "93105331d9da311afa7845f9939dbd60617b929ae9ede23286fa26bedaa815c1",
    "calculation_digest": "12b753fc2646aebfbb117db95031c2765cdd2cc040025481de08613d183ad8db",
}

# Literal strings that this gate transcribes.  They are compared byte for byte
# with the charter artifact before any algebra runs.
PINNED_STRINGS = {
    "exact_action.wall_background": "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2]",
    "exact_action.foliation": "S_fol=Mb^2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-B4_bar*Rcal^2/(16*k_infinity^2)]/2",
    "exact_action.solid": "S_X=int_Sigma sqrt(-gamma)*[rho_X*(u^mu*partial_mu X^a)^2/2-mu_X*tr[(B-v^2*I)^2]/4-lambda_X*(tr(B-v^2*I))^2/8]",
    "exact_action.Robin": "S_R=-kappa_hat*int_Sigma sqrt(-gamma)*delta_ab*(varphi^a-y*Acal^a)*(varphi^b-y*Acal^b)/2",
    "exact_action.superpotential": "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]",
    "definitions.khronon_unit_vector": "u_mu=-D_mu T/sqrt(-gamma^(rho sigma)*D_rho T*D_sigma T)",
    "definitions.spatial_metric": "h_mu_nu=gamma_mu_nu+u_mu*u_nu",
    "definitions.leaf_extrinsic_curvature": "Kcal_mu_nu=h_mu^rho*h_nu^sigma*D_rho u_sigma",
    "definitions.acceleration": "a_mu=u^nu*D_nu u_mu",
    "definitions.solid_metric": "B^ab=h^(mu nu)*partial_mu X^a*partial_nu X^b",
    "definitions.orthonormal_triad": "E^a_mu=h_mu^nu*partial_nu X^b*(B^(-1/2))_b^a",
    "definitions.raised_triad": "E^(a mu)=h^(mu nu)*E^a_nu",
    "definitions.soldered_acceleration": "Acal^a=E^(a mu)*a_mu",
}

# Leaf curvature is a composite the charter names but does not spell out.  It is
# fixed here by the Gauss equation for a timelike unit normal and cross-checked
# against the direct three-dimensional Ricci scalar in the tau=0 chart.
LEAF_CURVATURE_DEFINITION = (
    "Rcal = R[gamma] + 2*Ric[gamma]_mu_nu*u^mu*u^nu - Kcal^2 + Kcal_mu_nu*Kcal^mu_nu "
    "(Gauss equation, timelike unit normal u, u^mu*u_mu=-1)"
)

FROZEN_PARAMETERS = {
    "M5_cubed": 1.0, "k_infinity": 1.0, "compensator_metric_G": 1.2, "brane_beta": 2.0,
    "brane_Mb_squared": 2.0, "lambda_K": 1.3107013790800848, "xi": 1.0, "eta": 3.107013790800849,
    "B4_bar": 0.8, "Robin_kappa_hat": 1.0, "Robin_y": math.sqrt(3.0),
    "solid_v": 1.0, "solid_rho": 1.0, "solid_mu": 1.0, "solid_lambda": 1.0,
}

PHYSICAL_FALSE_KEYS = (
    "B4_pass", "B5_pass", "P2_pass", "P3_complete_pass", "P4_full_same_action_pass",
    "nonlinear_gravitational_P4_pass", "N2_pass", "N3_pass", "N4_pass", "N5_pass", "N6_pass", "N7_pass",
    "C2_pass", "C4_pass", "C10_pass", "junction_conditions_derived_pass", "nonlinear_constraints_derived_pass",
    "characteristics_derived_pass", "bulk_fields_varied_pass", "embeddings_varied_pass",
    "stability_claimed", "phenomenology_claimed",
)


class FullVariationError(ValueError):
    pass


# ----------------------------------------------------------------------------- utilities
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_charter() -> tuple[dict[str, Any], str]:
    if not CHARTER.is_file():
        raise FullVariationError("action charter artifact is absent")
    payload = json.loads(CHARTER.read_text(encoding="utf-8"))
    for key, expected in EXPECTED_CHARTER_DIGESTS.items():
        recorded = payload.get(key)
        recorded = recorded.get("sha256") if isinstance(recorded, dict) else recorded
        if str(recorded) != expected:
            raise FullVariationError(f"charter {key} mismatch")
    charter = payload["action_charter"]
    # independent recomputation of the charter digest (canonical JSON, two serializations tried)
    recomputed = {
        "ensure_ascii_false": _canonical_digest(charter),
        "ensure_ascii_true": hashlib.sha256(json.dumps(charter, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }
    if EXPECTED_CHARTER_DIGESTS["action_charter_digest"] not in recomputed.values():
        raise FullVariationError("action_charter digest could not be recomputed from the artifact body")
    for dotted, expected in PINNED_STRINGS.items():
        block, key = dotted.split(".")
        if str(charter[block].get(key)) != expected:
            raise FullVariationError(f"pinned string {dotted} differs from charter")
    return payload, _sha256(CHARTER)


# ----------------------------------------------------------------------------- symbols
EPS = sp.Symbol("epsilon")
t, x, y, z = sp.symbols("t x y z", real=True)
COORDS = (t, x, y, z)
M5c, kinf, G, beta, Mb2, lamK, xi, eta, B4bar, kap, yR, v, rho, mu, lam = sp.symbols(
    "M5c k_inf G beta Mb2 lambda_K xi eta B4bar kappa_hat y v rho_X mu_X lambda_X", positive=True)
PARAM_MAP = {
    M5c: "M5_cubed", kinf: "k_infinity", G: "compensator_metric_G", beta: "brane_beta", Mb2: "brane_Mb_squared",
    lamK: "lambda_K", xi: "xi", eta: "eta", B4bar: "B4_bar", kap: "Robin_kappa_hat", yR: "Robin_y",
    v: "solid_v", rho: "solid_rho", mu: "solid_mu", lam: "solid_lambda",
}

# eighteen brane fluctuations, all functions of the four brane coordinates
n = sp.Function("n")(*COORDS)
N = [sp.Function(f"N{i}")(*COORDS) for i in (1, 2, 3)]
H = [[None] * 3 for _ in range(3)]
for i in range(3):
    for j in range(i, 3):
        H[i][j] = H[j][i] = sp.Function(f"H{i + 1}{j + 1}")(*COORDS)
tau = sp.Function("tau")(*COORDS)
pi_ = [sp.Function(f"pi{a}")(*COORDS) for a in (1, 2, 3)]
omega = sp.Function("omega")(*COORDS)
vphi = [sp.Function(f"vphi{a}")(*COORDS) for a in (1, 2, 3)]
FIELDS = [n, *N, H[0][0], H[0][1], H[0][2], H[1][1], H[1][2], H[2][2], tau, *pi_, omega, *vphi]
FIELD_NAMES = ["n", "N1", "N2", "N3", "H11", "H12", "H13", "H22", "H23", "H33", "tau", "pi1", "pi2", "pi3",
               "omega", "vphi1", "vphi2", "vphi3"]


def trunc(expr: sp.Expr, order: int = 2) -> sp.Expr:
    """Drop every power of EPS above ``order``."""
    expr = sp.expand(expr)
    return sum((expr.coeff(EPS, k) * EPS**k for k in range(order + 1)), sp.Integer(0))


def series_sqrt(expr: sp.Expr) -> sp.Expr:
    """sqrt(1+d) to second order where expr = 1 + d, d = O(EPS)."""
    d = trunc(expr - 1)
    return trunc(1 + d / 2 - d**2 / 8)


def series_inv_sqrt(expr: sp.Expr) -> sp.Expr:
    d = trunc(expr - 1)
    return trunc(1 - d / 2 + 3 * d**2 / 8)


# ----------------------------------------------------------------------------- geometry
def build_geometry() -> dict[str, Any]:
    """Metric, inverse, Christoffels, khronon vector, spatial metric, Kcal, a, Rcal to O(EPS^2)."""
    lapse = 1 + EPS * n
    shift = [EPS * Ni for Ni in N]
    hsp = sp.Matrix(3, 3, lambda i, j: (1 if i == j else 0) + EPS * H[i][j])
    # ADM form: gamma_00 = -N^2 + N_i N^i (indices with h), gamma_0i = N_i, gamma_ij = h_ij
    hinv0 = sp.eye(3)
    dh = hsp - sp.eye(3)
    hinv = trunc_matrix(hinv0 - dh + dh * dh)  # (1+dh)^-1 to O(eps^2)
    NiNi = sum(shift[i] * hinv[i, j] * shift[j] for i in range(3) for j in range(3))
    g = sp.zeros(4, 4)
    g[0, 0] = trunc(-lapse**2 + NiNi)
    for i in range(3):
        g[0, i + 1] = g[i + 1, 0] = shift[i]
        for j in range(3):
            g[i + 1, j + 1] = hsp[i, j]
    eta4 = sp.diag(-1, 1, 1, 1)
    dg = g - eta4
    ginv = trunc_matrix(eta4 - eta4 * dg * eta4 + eta4 * dg * eta4 * dg * eta4)
    # sqrt(-gamma) = N sqrt(det h)
    deth = trunc(hsp.det())
    sqrt_g = trunc(lapse * series_sqrt(deth))
    # Christoffels Gamma^l_{mn}
    dgd = [[[sp.diff(g[m, nn], COORDS[k]) for nn in range(4)] for m in range(4)] for k in range(4)]
    Gam = [[[trunc(sp.Rational(1, 2) * sum(ginv[l, s] * (dgd[m][s][nn] + dgd[nn][s][m] - dgd[s][m][nn])
                                           for s in range(4)))
             for nn in range(4)] for m in range(4)] for l in range(4)]
    # khronon: T = t + eps*tau
    dT = [1 + EPS * sp.diff(tau, t)] + [EPS * sp.diff(tau, c) for c in (x, y, z)]
    norm2 = trunc(-sum(ginv[m, nn] * dT[m] * dT[nn] for m in range(4) for nn in range(4)))  # = -gamma^{mn} dT dT > 0
    inv_norm = series_inv_sqrt(norm2)
    u_lo = [trunc(-dT[m] * inv_norm) for m in range(4)]
    u_up = [trunc(sum(ginv[m, nn] * u_lo[nn] for nn in range(4))) for m in range(4)]
    h_lo = sp.Matrix(4, 4, lambda m, nn: trunc(g[m, nn] + u_lo[m] * u_lo[nn]))
    h_up = sp.Matrix(4, 4, lambda m, nn: trunc(ginv[m, nn] + u_up[m] * u_up[nn]))
    h_mix = sp.Matrix(4, 4, lambda m, nn: trunc(sum(h_up[m, s] * g[s, nn] for s in range(4))))  # h^m_n
    # D_r u_s
    Du = [[trunc(sp.diff(u_lo[s], COORDS[r]) - sum(Gam[l][r][s] * u_lo[l] for l in range(4)))
           for s in range(4)] for r in range(4)]
    K_lo = sp.Matrix(4, 4, lambda m, nn: trunc(sum(h_mix[r, m] * h_mix[s, nn] * Du[r][s]
                                                  for r in range(4) for s in range(4))))
    a_lo = [trunc(sum(u_up[r] * Du[r][m] for r in range(4))) for m in range(4)]
    K_up = sp.Matrix(4, 4, lambda m, nn: trunc(sum(ginv[m, r] * ginv[nn, s] * K_lo[r, s]
                                                  for r in range(4) for s in range(4))))
    K_trace = trunc(sum(ginv[m, nn] * K_lo[m, nn] for m in range(4) for nn in range(4)))
    K2 = trunc(sum(K_lo[m, nn] * K_up[m, nn] for m in range(4) for nn in range(4)))
    a2 = trunc(sum(ginv[m, nn] * a_lo[m] * a_lo[nn] for m in range(4) for nn in range(4)))
    # Riemann/Ricci of gamma to O(eps^2): R^l_{m r nn}
    Ric = sp.zeros(4, 4)
    for m in range(4):
        for nn in range(4):
            acc = 0
            for l in range(4):
                acc += sp.diff(Gam[l][m][nn], COORDS[l]) - sp.diff(Gam[l][m][l], COORDS[nn])
                for s in range(4):
                    acc += Gam[l][l][s] * Gam[s][m][nn] - Gam[l][nn][s] * Gam[s][m][l]
            Ric[m, nn] = trunc(acc)
    Rscal = trunc(sum(ginv[m, nn] * Ric[m, nn] for m in range(4) for nn in range(4)))
    Ricuu = trunc(sum(Ric[m, nn] * u_up[m] * u_up[nn] for m in range(4) for nn in range(4)))
    Rleaf = trunc(Rscal + 2 * Ricuu - K_trace**2 + K2)
    return {"g": g, "ginv": ginv, "sqrt_g": sqrt_g, "u_lo": u_lo, "u_up": u_up, "h_lo": h_lo, "h_up": h_up,
            "h_mix": h_mix, "K_lo": K_lo, "K_trace": K_trace, "K2": K2, "a_lo": a_lo, "a2": a2,
            "Rleaf": Rleaf, "Rscal": Rscal, "hsp": hsp, "hinv": hinv}


def trunc_matrix(M: sp.Matrix) -> sp.Matrix:
    return M.applyfunc(trunc)


def direct_3d_ricci_tau0(hsp: sp.Matrix, hinv: sp.Matrix) -> sp.Expr:
    """Three-dimensional Ricci scalar of h_ij (ADM leaf t=const), for the tau=0 cross-check."""
    sc = (x, y, z)
    dh = [[[sp.diff(hsp[m, nn], sc[k]) for nn in range(3)] for m in range(3)] for k in range(3)]
    Gam = [[[trunc(sp.Rational(1, 2) * sum(hinv[l, s] * (dh[m][s][nn] + dh[nn][s][m] - dh[s][m][nn])
                                           for s in range(3)))
             for nn in range(3)] for m in range(3)] for l in range(3)]
    Ric = sp.zeros(3, 3)
    for m in range(3):
        for nn in range(3):
            acc = 0
            for l in range(3):
                acc += sp.diff(Gam[l][m][nn], sc[l]) - sp.diff(Gam[l][m][l], sc[nn])
                for s in range(3):
                    acc += Gam[l][l][s] * Gam[s][m][nn] - Gam[l][nn][s] * Gam[s][m][l]
            Ric[m, nn] = trunc(acc)
    return trunc(sum(hinv[m, nn] * Ric[m, nn] for m in range(3) for nn in range(3)))


# ----------------------------------------------------------------------------- brane Lagrangian
def solid_block(geo: dict[str, Any]) -> dict[str, Any]:
    """B^ab, triad E^a_mu, u.dX, and the solid Lagrangian density (without sqrt(-gamma))."""
    X = [v * x + EPS * pi_[0], v * y + EPS * pi_[1], v * z + EPS * pi_[2]]
    dX = [[sp.diff(X[a], COORDS[m]) for m in range(4)] for a in range(3)]
    h_up = geo["h_up"]
    B = sp.Matrix(3, 3, lambda a, b: trunc(sum(h_up[m, nn] * dX[a][m] * dX[b][nn]
                                              for m in range(4) for nn in range(4))))
    Bm = B - v**2 * sp.eye(3)
    trB2 = trunc(sum(Bm[a, b] * Bm[b, a] for a in range(3) for b in range(3)))
    trB = trunc(Bm.trace())
    udX = [trunc(sum(geo["u_up"][m] * dX[a][m] for m in range(4))) for a in range(3)]
    L_X = trunc(rho * sum(w**2 for w in udX) / 2 - mu * trB2 / 4 - lam * trB**2 / 8)
    # B^{-1/2}: B = v^2 (1 + d), (1+d)^{-1/2} = 1 - d/2 + 3 d^2/8
    d = trunc_matrix(B / v**2 - sp.eye(3))
    Binvhalf = trunc_matrix((sp.eye(3) - d / 2 + sp.Rational(3, 8) * d * d) / v)
    h_mix = geo["h_mix"]
    E_lo = [[trunc(sum(h_mix[nn, m] * dX[b][nn] * Binvhalf[b, a] for nn in range(4) for b in range(3)))
             for m in range(4)] for a in range(3)]
    E_up = [[trunc(sum(h_up[m, nn] * E_lo[a][nn] for nn in range(4))) for m in range(4)] for a in range(3)]
    Acal = [trunc(sum(E_up[a][m] * geo["a_lo"][m] for m in range(4))) for a in range(3)]
    return {"L_X": L_X, "B": B, "E_lo": E_lo, "E_up": E_up, "Acal": Acal, "udX": udX}


def brane_lagrangian(geo: dict[str, Any], sol: dict[str, Any]) -> dict[str, sp.Expr]:
    Om = 1 + EPS * omega
    W_expr = 3 * M5c * kinf * sp.exp(-G * Om**2 / (6 * M5c))
    W_ser = trunc(sp.series(W_expr, EPS, 0, 3).removeO())
    L_wall0 = trunc(-(2 * W_ser + beta * (Om - 1)**2 / 2))
    L_fol = trunc(Mb2 * (geo["K2"] - lamK * geo["K_trace"]**2 + xi * geo["Rleaf"] + eta * geo["a2"]
                         - B4bar * geo["Rleaf"]**2 / (16 * kinf**2)) / 2)
    phis = [EPS * f for f in vphi]
    L_R = trunc(-kap * sum((phis[a] - yR * sol["Acal"][a])**2 for a in range(3)) / 2)
    total = trunc(geo["sqrt_g"] * (L_wall0 + L_fol + sol["L_X"] + L_R))
    return {"L_wall0": L_wall0, "L_fol": L_fol, "L_X": sol["L_X"], "L_R": L_R,
            "sqrt_g_L_total": total,
            "sqrt_g_L_wall0": trunc(geo["sqrt_g"] * L_wall0), "sqrt_g_L_fol": trunc(geo["sqrt_g"] * L_fol),
            "sqrt_g_L_X": trunc(geo["sqrt_g"] * sol["L_X"]), "sqrt_g_L_R": trunc(geo["sqrt_g"] * L_R)}


# ----------------------------------------------------------------------------- variations
def tadpoles(L1: sp.Expr) -> dict[str, sp.Expr]:
    """First-order Lagrangian -> Euler-Lagrange tadpole for each field (integrating by parts)."""
    out = {}
    for f, name in zip(FIELDS, FIELD_NAMES):
        e = sp.diff(L1, f)
        for c in COORDS:
            e -= sp.diff(sp.diff(L1, sp.diff(f, c)), c)
            for c2 in COORDS:
                e += sp.diff(sp.diff(L1, sp.diff(f, c, c2)), c, c2) * (sp.Rational(1, 2) if c != c2 else 1)
        out[name] = sp.simplify(e)
    return out


def hessian_momentum_space(L2: sp.Expr) -> tuple[sp.Matrix, dict[str, sp.Symbol]]:
    """Plane-wave reduction: f -> A_f e^{i theta} + conj, theta = q z - w t; H_fg = d2 L2 / d conj(A_f) d A_g."""
    q, w = sp.symbols("q w", real=True)
    theta = q * z - w * t
    A = {name: sp.Symbol(f"A_{name}") for name in FIELD_NAMES}
    Ab = {name: sp.Symbol(f"Ab_{name}") for name in FIELD_NAMES}
    sub = {}
    for f, name in zip(FIELDS, FIELD_NAMES):
        sub[f] = A[name] * sp.exp(sp.I * theta) + Ab[name] * sp.exp(-sp.I * theta)
    expr = L2
    # replace derivatives first (sympy substitutes Derivative objects by differentiating the replacement)
    expr = expr.subs(sub).doit()
    expr = sp.expand(expr)
    # keep only the theta-independent part: terms with e^{0}
    expr = expr.subs(sp.exp(sp.I * theta), sp.Symbol("Eth")).subs(sp.exp(-sp.I * theta), 1 / sp.Symbol("Eth"))
    expr = sp.expand(expr)
    expr0 = sum((term for term in expr.as_ordered_terms() if not term.has(sp.Symbol("Eth"))), sp.Integer(0))
    Hm = sp.Matrix(len(FIELD_NAMES), len(FIELD_NAMES),
                   lambda i, j: sp.simplify(sp.diff(expr0, Ab[FIELD_NAMES[i]], A[FIELD_NAMES[j]])))
    return Hm, {"q": q, "w": w}


HELICITY = {
    "scalar": ["n", "N3", "H11", "H22", "H33", "tau", "pi3", "omega", "vphi3"],
    "vector": ["N1", "N2", "H13", "H23", "pi1", "pi2", "vphi1", "vphi2"],
    "tensor": ["H12"],
}


def gauge_null_checks(Hm: sp.Matrix, qw: dict[str, sp.Symbol]) -> dict[str, Any]:
    """Linear gauge transformations of the brane fields; each must be a null vector of the Hessian."""
    q, w = qw["q"], qw["w"]
    idx = {nme: i for i, nme in enumerate(FIELD_NAMES)}
    results = {}
    # time reparametrization xi^0 = f: delta tau = f, delta n = d_t f, delta N_i = d_i f (lower index), delta H = 0,
    # delta pi^a = -f d_t X^a = 0 on the static background, delta omega = delta vphi = 0.
    # plane wave f -> F e^{i theta}: d_t -> -i w, d_z -> i q.
    vec = sp.zeros(len(FIELD_NAMES), 1)
    vec[idx["tau"]] = 1
    vec[idx["n"]] = -sp.I * w
    vec[idx["N3"]] = -sp.I * q
    r = (Hm * vec).applyfunc(sp.simplify)
    results["time_reparametrization"] = {"null": all(e == 0 for e in r), "residual_nonzero_rows":
                                         [FIELD_NAMES[i] for i in range(len(FIELD_NAMES)) if r[i] != 0]}
    # spatial diffeomorphism xi^i: delta H_ij = d_i xi_j + d_j xi_i, delta N_i = d_t xi_i, delta pi^a = v xi^a.
    for comp, name in ((0, "x"), (1, "y"), (2, "z")):
        vec = sp.zeros(len(FIELD_NAMES), 1)
        vec[idx[f"pi{comp + 1}"]] = v
        vec[idx[f"N{comp + 1}"]] = -sp.I * w
        # only d_z is nonzero for the plane wave
        if comp == 2:
            vec[idx["H33"]] = 2 * sp.I * q
        else:
            vec[idx[f"H{comp + 1}3"]] = sp.I * q
        r = (Hm * vec).applyfunc(sp.simplify)
        results[f"spatial_diffeomorphism_{name}"] = {"null": all(e == 0 for e in r), "residual_nonzero_rows":
                                                     [FIELD_NAMES[i] for i in range(len(FIELD_NAMES)) if r[i] != 0]}
    return results


def n7_solid_invariant(geo: dict[str, Any]) -> sp.Expr:
    """The N7 v3 quadratic solid invariant, rebuilt from its printed formula (not imported)."""
    V1 = [sp.diff(pi_[a], t) - v * N[a] for a in range(3)]
    C1 = sp.Matrix(3, 3, lambda a, b: v * (sp.diff(pi_[b], (x, y, z)[a]) + sp.diff(pi_[a], (x, y, z)[b])) - v**2 * H[a][b])
    return sp.expand(rho * sum(w**2 for w in V1) / 2 - mu * sum(C1[a, b]**2 for a in range(3) for b in range(3)) / 4
                     - lam * C1.trace()**2 / 8)


# ----------------------------------------------------------------------------- main derivation
def derive() -> dict[str, Any]:
    t0 = time.time()
    charter_payload, charter_sha = _load_charter()
    log: dict[str, float] = {}
    geo = build_geometry(); log["geometry_s"] = time.time() - t0
    sol = solid_block(geo); log["solid_s"] = time.time() - t0
    L = brane_lagrangian(geo, sol); log["lagrangian_s"] = time.time() - t0
    total = L["sqrt_g_L_total"]
    L0 = sp.simplify(total.coeff(EPS, 0))
    L1 = sp.expand(total.coeff(EPS, 1))
    L2 = sp.expand(total.coeff(EPS, 2))

    # background and tadpoles
    tad = tadpoles(L1); log["tadpoles_s"] = time.time() - t0
    W1 = 3 * M5c * kinf * sp.exp(-G / (6 * M5c))
    tension = sp.simplify(2 * W1)
    dW1 = sp.simplify(sp.diff(3 * M5c * kinf * sp.exp(-G * sp.Symbol("Om")**2 / (6 * M5c)), sp.Symbol("Om")).subs(sp.Symbol("Om"), 1))
    background_ok = sp.simplify(L0 + tension) == 0
    stationary = {k: sp.simplify(tad[k]) == 0 for k in FIELD_NAMES}
    # expected tadpoles: metric -> -tension * (1/2) delta gamma^{..} sqrt(-gamma) variation; Omega -> -2 W'(1)
    expected_omega_tadpole = sp.simplify(-2 * dW1)
    omega_tadpole_ok = sp.simplify(tad["omega"] - expected_omega_tadpole) == 0
    # sqrt(-gamma) to first order: n + H_ii/2, so lapse tadpole = -tension, H_ii tadpole = -tension/2, others 0
    metric_tadpoles_ok = (sp.simplify(tad["n"] + tension) == 0 and all(sp.simplify(tad[f"H{i}{i}"] + tension / 2) == 0 for i in (1, 2, 3))
                          and all(sp.simplify(tad[k]) == 0 for k in ("N1", "N2", "N3", "H12", "H13", "H23")))

    # leaf curvature cross-check in the tau=0 chart at O(eps^2)
    R3 = direct_3d_ricci_tau0(geo["hsp"], geo["hinv"])
    Rleaf_tau0 = trunc(geo["Rleaf"].subs(tau, 0).doit())
    leaf_ok = sp.simplify(sp.expand(Rleaf_tau0 - R3)) == 0
    log["leaf_check_s"] = time.time() - t0

    # solid invariant against N7 v3 printed formula
    L2_solid = sp.expand(L["sqrt_g_L_X"].coeff(EPS, 2))
    solid_first = sp.expand(L["sqrt_g_L_X"].coeff(EPS, 1))
    solid_zero = sp.simplify(L["sqrt_g_L_X"].coeff(EPS, 0))
    n7 = n7_solid_invariant(geo)
    L2_solid_tau0 = sp.expand(L2_solid.subs(tau, 0).doit())
    solid_matches = sp.simplify(sp.expand(L2_solid_tau0 - n7)) == 0
    solid_tau_terms = sp.expand(L2_solid - L2_solid_tau0)
    solid_khronon_mixing = solid_tau_terms != 0
    solid_lower_orders_vanish = (solid_zero == 0) and (sp.simplify(solid_first) == 0)

    # momentum-space Hessian
    Hm, qw = hessian_momentum_space(L2); log["hessian_s"] = time.time() - t0
    idx = {nme: i for i, nme in enumerate(FIELD_NAMES)}
    mixed = {
        "pi3_N3": sp.simplify(Hm[idx["pi3"], idx["N3"]]),
        "pi3_H33": sp.simplify(Hm[idx["pi3"], idx["H33"]]),
        "pi1_H13": sp.simplify(Hm[idx["pi1"], idx["H13"]]),
        "pi1_N1": sp.simplify(Hm[idx["pi1"], idx["N1"]]),
    }
    mixed_nonzero = all(e != 0 for e in mixed.values())
    robin_rows = {
        "vphi3_tau": sp.simplify(Hm[idx["vphi3"], idx["tau"]]),
        "vphi3_n": sp.simplify(Hm[idx["vphi3"], idx["n"]]),
        "vphi3_pi3": sp.simplify(Hm[idx["vphi3"], idx["pi3"]]),
        "vphi3_H33": sp.simplify(Hm[idx["vphi3"], idx["H33"]]),
        "vphi3_vphi3": sp.simplify(Hm[idx["vphi3"], idx["vphi3"]]),
    }
    # Robin couples gamma (n, H), T (tau), X (pi) and varphi: every sector must appear in the varphi row
    robin_quadratic = (robin_rows["vphi3_vphi3"] != 0 and robin_rows["vphi3_tau"] != 0 and robin_rows["vphi3_n"] != 0)
    robin_solid_decouples = (robin_rows["vphi3_pi3"] == 0 and robin_rows["vphi3_H33"] == 0)
    gauge_full = gauge_null_checks(Hm, qw)
    # Tadpole-free quadratic form: drop the pieces proportional to W(1) (tension x sqrt(-gamma)_2) and to
    # W'(1) (omega x sqrt(-gamma)_1); keep the gauge-invariant omega mass term (W''(1)+beta/2) omega^2.
    W2 = sp.simplify(sp.diff(3 * M5c * kinf * sp.exp(-G * sp.Symbol("Om")**2 / (6 * M5c)), sp.Symbol("Om"), 2).subs(sp.Symbol("Om"), 1))
    L2_wall0 = sp.expand(L["sqrt_g_L_wall0"].coeff(EPS, 2))
    L2_tadpole_free = sp.expand(L2 - L2_wall0 - (W2 + beta / 2) * omega**2)
    Hm_tf, _ = hessian_momentum_space(L2_tadpole_free)
    Hm_tadpole = (Hm - Hm_tf).applyfunc(sp.simplify)
    gauge = gauge_null_checks(Hm_tf, qw)
    gauge_tadpole = gauge_null_checks(Hm_tadpole, qw)
    residual_is_pure_tadpole = all(set(gauge_full[k]["residual_nonzero_rows"]) == set(gauge_tadpole[k]["residual_nonzero_rows"])
                                   for k in gauge_full)
    log["gauge_s"] = time.time() - t0
    gauge_ok = all(r["null"] for r in gauge.values())
    hermitian_ok = all(sp.simplify(Hm[i, j] - sp.conjugate(Hm[j, i])) == 0
                       for i in range(len(FIELD_NAMES)) for j in range(i, len(FIELD_NAMES)))
    # helicity block structure: no cross terms between scalar/vector/tensor sets
    def cross(a: list[str], b: list[str]) -> bool:
        return all(sp.simplify(Hm[idx[p], idx[r]]) == 0 for p in a for r in b)
    helicity_ok = (cross(HELICITY["scalar"], HELICITY["vector"]) and cross(HELICITY["scalar"], HELICITY["tensor"])
                   and cross(HELICITY["vector"], HELICITY["tensor"]))
    # numerical matrix at the frozen point for the record
    num_sub = {s: FROZEN_PARAMETERS[k] for s, k in PARAM_MAP.items()}
    Hnum = Hm.subs(num_sub)
    def block(names: list[str]) -> list[list[str]]:
        return [[str(sp.nsimplify(sp.simplify(Hnum[idx[a], idx[b]]), rational=False)) for b in names] for a in names]

    checks = {
        "charter_digests_bound_pass": True,
        "pinned_formula_strings_match_charter_pass": True,
        "background_lagrangian_equals_minus_tension_pass": bool(background_ok),
        "khronon_solid_material_background_stationary_pass": bool(all(stationary[k] for k in ("tau", "pi1", "pi2", "pi3", "vphi1", "vphi2", "vphi3"))),
        "metric_tadpole_is_pure_tension_pass": bool(metric_tadpoles_ok),
        "omega_tadpole_is_minus_two_W_prime_pass": bool(omega_tadpole_ok),
        "leaf_curvature_gauss_equals_direct_3d_ricci_pass": bool(leaf_ok),
        "solid_background_and_first_order_vanish_pass": bool(solid_lower_orders_vanish),
        "solid_quadratic_block_matches_n7_v3_invariant_pass": bool(solid_matches),
        "mixed_solid_shift_spatial_metric_second_derivatives_nonzero_pass": bool(mixed_nonzero),
        "solid_khronon_mixing_present_pass": bool(solid_khronon_mixing),
        "robin_quadratic_couples_varphi_lapse_khronon_pass": bool(robin_quadratic),
        "robin_solid_and_spatial_metric_decouple_at_quadratic_order_pass": bool(robin_solid_decouples),
        "gauge_residual_of_full_hessian_is_pure_tadpole_pass": bool(residual_is_pure_tadpole),
        "extended_hessian_hermitian_pass": bool(hermitian_ok),
        "helicity_blocks_decouple_pass": bool(helicity_ok),
        "time_reparametrization_null_direction_tadpole_free_pass": bool(gauge["time_reparametrization"]["null"]),
        "spatial_diffeomorphism_null_directions_tadpole_free_pass": bool(all(gauge[k]["null"] for k in gauge if k.startswith("spatial"))),
        "gauge_null_directions_pass": bool(gauge_ok),
    }
    decision = {k: False for k in PHYSICAL_FALSE_KEYS}
    decision.update({
        "brane_sector_full_variation_from_literal_action_pass": bool(all(checks.values())),
        "extended_brane_hessian_derived_not_inherited_pass": bool(checks["solid_quadratic_block_matches_n7_v3_invariant_pass"] and checks["gauge_null_directions_pass"]),
        "old_wall_ADM_Hessian_consumed": False,
        "n7_v3_artifact_consumed": False,
    })
    tad_str = {k: str(vv) for k, vv in tad.items()}
    payload = {
        "schema": SCHEMA,
        "route_id": ROUTE_ID,
        "title": "Full variation of the one-Omega action charter, stage v1: brane sector from the literal action",
        "stage": {"varied": ["gamma_mu_nu (ADM: n, N_i, H_ij)", "T (tau)", "X^a (pi^a)", "Omega_Sigma (omega)", "varphi^a"],
                  "not_varied": ["g_MN bulk", "Omega bulk", "phi^a bulk", "Y_plus, Y_minus", "GHY"],
                  "background": "gamma=eta, T=t, X^a=v x^a, Omega_Sigma=1, varphi=0",
                  "order": "second order in every field simultaneously; khronon gauge NOT fixed",
                  "leaf_curvature_definition": LEAF_CURVATURE_DEFINITION},
        "upstream_bindings": {"one_omega_action_charter_gate.json": {"sha256": charter_sha, **EXPECTED_CHARTER_DIGESTS},
                              "pinned_strings_sha256": _canonical_digest(PINNED_STRINGS)},
        "background": {"L0": str(L0), "tension_2W_at_1": str(tension), "W_prime_at_1": str(dW1)},
        "tadpoles": tad_str,
        "expected_tadpoles": {"n": str(-tension), "H_ii": str(-tension / 2), "omega": str(expected_omega_tadpole),
                              "interpretation": "the gamma and Omega_Sigma tadpoles are the sources the bulk junction (GHY plus bulk Omega flux) must balance; not derived here"},
        "quadratic_lagrangian": {"n_terms_total": len(L2.as_ordered_terms()), "n_terms_solid": len(L2_solid.as_ordered_terms()),
                                 "solid_block": str(L2_solid), "solid_block_tau0": str(L2_solid_tau0),
                                 "solid_khronon_mixing_terms": str(solid_tau_terms), "n7_v3_invariant_rebuilt": str(n7)},
        "extended_hessian": {"fields": FIELD_NAMES, "momentum": "q along z, frequency w; plane wave A e^{i(qz-wt)} + c.c.",
                             "helicity_sets": HELICITY,
                             "symbolic_diagonal": {nme: str(sp.simplify(Hm[idx[nme], idx[nme]])) for nme in FIELD_NAMES},
                             "mixed_solid_metric_entries": {k: str(vv) for k, vv in mixed.items()},
                             "robin_row_vphi3": {k: str(vv) for k, vv in robin_rows.items()},
                             "gauge_null_checks": {k: {"null": vv["null"], "residual_nonzero_rows": vv["residual_nonzero_rows"]} for k, vv in gauge.items()},
                             "gauge_null_checks_full_hessian": {k: {"null": vv["null"], "residual_nonzero_rows": vv["residual_nonzero_rows"]} for k, vv in gauge_full.items()},
                             "gauge_null_checks_tadpole_part": {k: {"null": vv["null"], "residual_nonzero_rows": vv["residual_nonzero_rows"]} for k, vv in gauge_tadpole.items()},
                             "tadpole_free_definition": "L2 minus the W(1) and W'(1) pieces of sqrt(-gamma)*L_wall0, keeping (W''(1)+beta/2)*omega^2",
                             "numerical_blocks_at_frozen_point": {k: block(names) for k, names in HELICITY.items()},
                             "frozen_parameters": FROZEN_PARAMETERS},
        "checks": checks,
        "decision": decision,
        "classification": "theory_only;brane_sector_full_variation_from_literal_charter_action;extended_brane_hessian_derived;bulk_embeddings_GHY_junction_constraints_characteristics_not_derived;N2_N7_C2_C10_P2_P3_P4_B4_B5_fail_closed",
        "evidence_boundary": [
            "Only the displayed brane action is varied; the bulk, the two embeddings and GHY are not, so no junction condition, constraint or characteristic is derived.",
            "The Hessian is the brane-localized quadratic form; the complete extended Hessian needs the bulk quadratic form and the junction.",
            "Reproducing the N7 v3 solid invariant is a consistency check on the transcription, not an inheritance of any N7 conclusion.",
            "Gauge null directions are checked at the linear level only, and on the tadpole-free quadratic form: around a background that is not a solution of the brane sector alone (tension and Omega-flux tadpoles), the quadratic action is not invariant under the linear gauge transformation; the residual is recorded and shown to come only from the tadpole pieces, which the bulk junction must cancel.",
            "The charter's statement that the Robin term couples gamma, T, X^a and varphi^a is nonlinear; at quadratic order around X^a=v x^a the solid and the spatial metric drop out of the Robin block, which couples varphi, the lapse and the khronon.",
            "Not fixing the khronon gauge exposes a khronon-solid mixing (V1 acquires -v*grad(tau)) absent from the N7 v3 khronon-gauge invariant; the two agree at tau=0.",
        ],
        "provenance": {"generator": Path(__file__).name, "generator_sha256": _sha256(Path(__file__)), "sympy": sp.__version__,
                       "python": platform.python_version(), "timings_s": {k: round(vv, 1) for k, vv in log.items()},
                       "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
    }
    payload["calculation_digest"] = _canonical_digest({k: payload[k] for k in ("background", "tadpoles", "quadratic_lagrangian", "checks", "decision")})
    return payload


def main() -> int:
    payload = derive()
    _write(OUTPUT, payload)
    print(json.dumps({"checks": payload["checks"], "timings_s": payload["provenance"]["timings_s"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
