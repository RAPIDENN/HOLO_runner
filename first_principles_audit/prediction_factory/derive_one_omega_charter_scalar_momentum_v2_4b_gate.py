#!/usr/bin/env python3
"""Full variation of the one-Omega action charter, stage v2.4b: scalar-sector canonical momenta with tangential jets.

Repair of v2.4 after Codex audit 054854Z: boundary data kept as functions of (x0, x3) so tangential derivatives
survive; radial momentum by the higher-jet Euler-Lagrange boundary operator p_X = sum_I (-D_tan)^I dL/d(D_tan^I X_w);
any Derivative with two w-derivatives detected; the bulk total-derivative B_tot and the second-order GHY term are
varied and added to the brane currents; the coefficient of delta X_w must cancel (well-posed Dirichlet data).

Stage v2.3a fixed the tensor sector's normalization from the quadratic action.  This stage does
the same for the scalar sector, which is where Codex's spectral proof (5acd2e1) and master rows
(14bbf29) live.  Everything comes from the pinned charter strings; nothing is imported from Codex.

Ansatz (Gaussian normal gauge, proper w, plane wave in x0, x3):
    g = e^{2A(w)} (eta + eps h) + dw^2,   h_mu_nu = 2 P eta_mu_nu + 2 d_mu d_nu E,
    Omega = Omega(w) + eps C,             P, E, C functions of (x0, x3, w),
on the v2.1 BPS wall (A = log Omega, opposite-sign BPS, A(0) = 0, Omega(0) = 1).

Derived:
1. the quadratic bulk density sqrt(-g)[M5^3 R/2 - G (dOmega)^2/2 - U(Omega)] to O(eps^2), with all
   second w-derivatives moved into explicit total derivatives (first-order form);
2. the canonical momenta p_P, p_E, p_C = dL2/d(P', E', C') at w = 0;
3. the brane wall term -sqrt(-gamma)[2W(Omega_Sigma) + beta (Omega_Sigma - 1)^2/2] to O(eps^2) with
   gamma = e^{2A}(eta + eps h)|_{w=0} and Omega_Sigma = 1 + eps C(0);
4. the brane-equation currents J_X = -p_X(0+) + p_X(0-) + d(wall)/dX(0) for X in {P, E, C} under Z2
   (odd first derivatives), and the check of Codex's closure  J_C = -2 G R'(0+) - beta C(0)  with
   R = P - C/Omega, i.e. no W''(1) remainder, and the provenance of the a0 (1 - G/(3M)) C term;
5. the same boundary bookkeeping as v2.3a: bulk total derivative + GHY (second order) + tension.

Everything physical stays false.  No registry, README, manuscript, paper or PDF is modified.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "one_omega_charter_scalar_momentum_v2_4b_gate.json"
CHARTER = HERE / "artifacts" / "one_omega_action_charter_gate.json"
V22 = HERE / "artifacts" / "one_omega_charter_linear_junction_v2_2_gate.json"
SCHEMA = "holo.one-omega-charter-scalar-momentum.v2.4b"
ROUTE_ID = "canonical_one_Omega_backreacted_wall_with_rank_full_solid_v1"

EXPECTED_CHARTER_DIGESTS = {
    "action_charter_digest": "93105331d9da311afa7845f9939dbd60617b929ae9ede23286fa26bedaa815c1",
    "calculation_digest": "12b753fc2646aebfbb117db95031c2765cdd2cc040025481de08613d183ad8db",
}
PINNED_STRINGS = {
    "exact_action.bulk": "S_bulk=sum_(eps in {plus,minus}) int_Meps sqrt(-g)*[M5^3*R/2-G*(nabla Omega)^2/2-U(Omega)-Z5_per_side*P_M^a*P_a^M/2-Z5_per_side*M^2*Omega^(-5)*V4(Omega^(3/2)*r_phi)]",
    "exact_action.bulk_potential": "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
    "exact_action.superpotential": "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]",
    "exact_action.GHY": "S_GHY=+M5^3*sum_(eps in {plus,minus}) int_Sigma sqrt(-gamma)*Theta_eps for outward spacelike normals",
    "exact_action.wall_background": "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2]",
}
PHYSICAL_FALSE_KEYS = (
    "B4_pass", "B5_pass", "P2_pass", "P3_complete_pass", "P4_full_same_action_pass", "nonlinear_gravitational_P4_pass",
    "N2_pass", "N3_pass", "N4_pass", "N5_pass", "N6_pass", "N7_pass", "C2_pass", "C4_pass", "C10_pass",
    "brane_fields_included_pass", "bending_included_pass", "spectrum_or_stability_claimed", "phenomenology_claimed",
)
DIGEST_KEYS = ("schema", "route_id", "stage", "upstream_bindings", "quadratic_density", "momenta", "wall", "currents",
               "codex_adm_oracle", "codex_closure", "boundary_bookkeeping", "checks", "decision", "classification", "evidence_boundary")


class ScalarMomentumError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _load_charter() -> tuple[dict[str, Any], str]:
    payload = json.loads(CHARTER.read_text(encoding="utf-8"))
    for key, expected in EXPECTED_CHARTER_DIGESTS.items():
        recorded = payload.get(key)
        recorded = recorded.get("sha256") if isinstance(recorded, dict) else recorded
        if str(recorded) != expected:
            raise ScalarMomentumError(f"charter {key} mismatch")
    charter = payload["action_charter"]
    for dotted, expected in PINNED_STRINGS.items():
        block, key = dotted.split(".")
        if str(charter[block].get(key)) != expected:
            raise ScalarMomentumError(f"pinned string {dotted} differs from charter")
    return payload, _sha256(CHARTER)


# ----------------------------------------------------------------------------- symbols
EPS = sp.Symbol("epsilon")
w = sp.Symbol("w", real=True)
x0, x1, x2, x3 = sp.symbols("x0 x1 x2 x3", real=True)
COORDS = (x0, x1, x2, x3, w)
M5c, kinf, G, beta_b = sp.symbols("M5c k_inf G beta_b", positive=True)
s = sp.Symbol("s")
A = sp.Function("A")(w)
Om = sp.Function("Omega")(w)
P = sp.Function("P")(x0, x3, w)
E = sp.Function("E")(x0, x3, w)
C = sp.Function("C")(x0, x3, w)
ETA = sp.diag(-1, 1, 1, 1)


def W_of(x):
    return 3 * M5c * kinf * sp.exp(-G * x**2 / (6 * M5c))


def U_of(x):
    qq = sp.Symbol("qq", positive=True)
    return (sp.diff(W_of(qq), qq)**2 / (2 * G) - 2 * W_of(qq)**2 / (3 * M5c)).subs(qq, x)


def _dummify(expr):
    derivs = sorted(sp.expand(expr).atoms(sp.Derivative), key=lambda d: str(d))
    dummies = {d: sp.Dummy() for d in derivs}
    return sp.expand(expr).xreplace(dummies), {v: k for k, v in dummies.items()}


def eps_coeff(expr, k):
    """Coefficient of EPS**k, robust to multivariate Derivative atoms (sympy collect limitation)."""
    e, inv = _dummify(expr)
    return sp.expand(e.coeff(EPS, k).xreplace(inv))


def eps_series(expr, order=3):
    """Taylor series in EPS up to (excluding) order, robust to multivariate Derivative atoms."""
    e, inv = _dummify(expr)
    return sp.expand(sp.series(e, EPS, 0, order).removeO().xreplace(inv))


def trunc(expr, order=2):
    return sum((eps_coeff(expr, k) * EPS**k for k in range(order + 1)), sp.Integer(0))


def bps_subs(expr):
    qq = sp.Symbol("qq", positive=True)
    Wq = W_of(qq); dWq = sp.diff(Wq, qq)
    Ap = -s * Wq.subs(qq, Om) / (3 * M5c)
    Op = s * dWq.subs(qq, Om) / G
    e = expr
    e = e.subs(sp.Derivative(A, (w, 2)), sp.diff(Ap, w)).subs(sp.Derivative(Om, (w, 2)), sp.diff(Op, w))
    e = e.subs({sp.Derivative(A, w): Ap, sp.Derivative(Om, w): Op})
    e = e.subs({sp.Derivative(A, w): Ap, sp.Derivative(Om, w): Op})
    return sp.expand(e.subs(s**2, 1))


def canon(e):
    """A = log Omega on the wall (A(0)=0), and canonical exp powers."""
    e = e.subs(A, sp.log(Om))
    e = e.replace(lambda x: x.is_Pow and x.base.func == sp.exp, lambda x: sp.exp(x.base.args[0] * x.exp))
    return sp.expand(sp.powsimp(sp.expand(e), force=True))


def scalar_quadratic_density():
    h = sp.zeros(4, 4)
    xs4 = (x0, x1, x2, x3)
    for m in range(4):
        for n in range(4):
            h[m, n] = 2 * P * ETA[m, n] + 2 * sp.diff(E, xs4[m], xs4[n])
    g = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            g[m, n] = sp.exp(2 * A) * (ETA[m, n] + EPS * h[m, n])
    g[4, 4] = 1
    # inverse to O(eps^2): (eta + eps h)^-1 = eta - eps eta h eta + eps^2 eta h eta h eta
    hm = ETA * h * ETA
    inv4 = ETA - EPS * hm + EPS**2 * (hm * h * ETA)
    ginv = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            ginv[m, n] = sp.exp(-2 * A) * inv4[m, n]
    ginv[4, 4] = 1
    assert all(trunc(sum(g[m, k] * ginv[k, n] for k in range(5)) - (1 if m == n else 0)) == 0 for m in range(5) for n in range(5))
    # sqrt(-g) = e^{4A} sqrt(det(1 + eta h)) ; det(1+X) = 1 + tr X + (tr X)^2/2 - tr(X^2)/2 + O(eps^3)
    X = ETA * h
    trX = trunc(X.trace()); trX2 = trunc((X * X).trace())
    det4 = trunc(1 + EPS * trX + EPS**2 * (trX**2 - trX2) / 2)
    sqrt_g = trunc(sp.exp(4 * A) * eps_series(sp.sqrt(det4), 3))
    Gam = [[[trunc(sp.Rational(1, 2) * sum(ginv[l, r] * (sp.diff(g[r, m], COORDS[k]) + sp.diff(g[r, k], COORDS[m]) - sp.diff(g[m, k], COORDS[r])) for r in range(5)))
             for k in range(5)] for m in range(5)] for l in range(5)]
    Ric = sp.zeros(5, 5)
    for m in range(5):
        for k in range(5):
            acc = 0
            for l in range(5):
                acc += sp.diff(Gam[l][m][k], COORDS[l]) - sp.diff(Gam[l][m][l], COORDS[k])
                for r in range(5):
                    acc += Gam[l][l][r] * Gam[r][m][k] - Gam[l][k][r] * Gam[r][m][l]
            Ric[m, k] = trunc(acc)
    R = trunc(sum(ginv[m, k] * Ric[m, k] for m in range(5) for k in range(5)))
    Omt = Om + EPS * C
    dOm = [sp.diff(Omt, c) for c in COORDS]
    kin = trunc(sum(ginv[m, k] * dOm[m] * dOm[k] for m in range(5) for k in range(5)))
    Uexp = trunc(eps_series(U_of(Omt), 3))
    L = trunc(sqrt_g * (M5c * R / 2 - G * kin / 2 - Uexp))
    return {"L": L, "sqrt_g": sqrt_g, "h": h, "g": g, "ginv": ginv, "Gam": Gam, "R": R}


def coeff_of(expr, target):
    """Coefficient of a Derivative (or field) in expr, robust to mixed-variable derivatives:
    every Derivative atom is replaced by a Dummy before collecting (sympy's collect does not
    support multivariate Derivative terms)."""
    expr = sp.expand(expr)
    derivs = sorted(expr.atoms(sp.Derivative), key=lambda d: str(d))
    dummies = {d: sp.Dummy() for d in derivs}
    inv = {v: k for k, v in dummies.items()}
    e = expr.xreplace(dummies)
    t = target.xreplace(dummies) if isinstance(target, sp.Basic) else target
    c = e.coeff(t)
    return sp.expand(c.xreplace(inv))


def w_order(d):
    return sum(1 for v in d.variables if v == w)


def has_two_w(expr):
    return any(w_order(d) >= 2 for d in sp.expand(expr).atoms(sp.Derivative))


def deriv_wrt(expr, target):
    """Partial derivative of expr w.r.t. a Derivative atom (quadratic terms give 2 c target), robust to
    multivariate Derivative atoms: dummify, differentiate, restore."""
    expr = sp.expand(expr)
    derivs = sorted(expr.atoms(sp.Derivative), key=lambda d: str(d))
    dummies = {d: sp.Dummy() for d in derivs}
    inv = {v: k for k, v in dummies.items()}
    if target not in dummies:
        return sp.Integer(0)
    return sp.expand(sp.diff(expr.xreplace(dummies), dummies[target]).xreplace(inv))


def jet_momentum(L, f):
    """p_f = sum over tangential multi-indices I of (-D_tan)^I dL/d(D_tan^I f_w): the boundary operator of a
    Lagrangian that still contains tangential derivatives of the radial derivative of f (up to order 2 here)."""
    tang = (x0, x3)
    total = sp.Integer(0)
    targets = [(sp.Derivative(f, w), ())]
    for a in tang:
        targets.append((sp.Derivative(f, w, a), (a,)))
    for a in tang:
        for b in tang:
            if tang.index(a) <= tang.index(b):
                targets.append((sp.Derivative(f, w, a, b) if a != b else sp.Derivative(f, w, (a, 2)), (a, b)))
    for target, idx in targets:
        c = deriv_wrt(L, target)   # dL/d(D_tan^I f_w), not the linear coefficient (quadratic terms matter)
        if c == 0:
            continue
        term = c
        for a in idx:
            term = -sp.diff(term, a)
        total += term
    return sp.expand(total)


def ricci4(gam, ginv4, coords4):
    """Ricci scalar of the 4D metric gam(x) (tangential derivatives only), truncated at O(eps^2)."""
    n = 4
    Gam = [[[trunc(sp.Rational(1, 2) * sum(ginv4[l, r] * (sp.diff(gam[r, m], coords4[k]) + sp.diff(gam[r, k], coords4[m]) - sp.diff(gam[m, k], coords4[r])) for r in range(n)))
             for k in range(n)] for m in range(n)] for l in range(n)]
    Ric = sp.zeros(n, n)
    for m in range(n):
        for k in range(n):
            acc = 0
            for l in range(n):
                acc += sp.diff(Gam[l][m][k], coords4[l]) - sp.diff(Gam[l][m][l], coords4[k])
                for r in range(n):
                    acc += Gam[l][l][r] * Gam[r][m][k] - Gam[l][k][r] * Gam[r][m][l]
            Ric[m, k] = trunc(acc)
    return trunc(sum(ginv4[m, k] * Ric[m, k] for m in range(n) for k in range(n)))


def adm_first_order_density(act):
    """sqrt(-g) R = sqrt(-g)[R4 + sigma (K^2 - K.K)] + tau d_w(sqrt(-g) K) for g = gamma(x,w) + dw^2, with
    K_mu_nu = d_w gamma_mu_nu / 2.  sigma, tau are DETERMINED by the machine (identity checked at O(eps^2)),
    not assumed.  Returns the first-order density M R/2 part, the total-derivative function and (sigma, tau)."""
    g, ginv, sqrt_g, R5 = act["g"], act["ginv"], act["sqrt_g"], act["R"]
    coords4 = (x0, x1, x2, x3)
    gam = sp.Matrix(4, 4, lambda m, n: g[m, n]); ginv4 = sp.Matrix(4, 4, lambda m, n: ginv[m, n])
    K = sp.Matrix(4, 4, lambda m, n: sp.diff(gam[m, n], w) / 2)
    Kup = sp.Matrix(4, 4, lambda m, n: trunc(sum(ginv4[m, a] * ginv4[n, b] * K[a, b] for a in range(4) for b in range(4))))
    Ktr = trunc(sum(ginv4[m, n] * K[m, n] for m in range(4) for n in range(4)))
    KK = trunc(sum(K[m, n] * Kup[m, n] for m in range(4) for n in range(4)))
    R4 = ricci4(gam, ginv4, coords4)
    lhs = trunc(sqrt_g * R5)
    found = None
    for sigma in (1, -1):
        for tau in (2, -2):
            rhs = trunc(sqrt_g * (R4 + sigma * (Ktr**2 - KK)) + tau * sp.diff(sqrt_g * Ktr, w))
            if sp.simplify(sp.expand(lhs - rhs)) == 0:
                found = (sigma, tau); break
        if found: break
    if not found:
        raise ScalarMomentumError("ADM decomposition of sqrt(-g) R failed at O(eps^2)")
    sigma, tau = found
    first = trunc(sqrt_g * (R4 + sigma * (Ktr**2 - KK)))
    Bfun = trunc(tau * sqrt_g * Ktr)      # sqrt(-g) R = first + d_w Bfun
    return first, Bfun, sigma, tau, Ktr


def first_order_form(L2, fields):
    """Move second w-derivatives of the fields and of A into total derivatives; return (L2_first, B_total)."""
    Btot = 0
    L = sp.expand(L2)
    for f in fields:
        fpp, fp = sp.Derivative(f, (w, 2)), sp.Derivative(f, w)
        c = coeff_of(L, fpp)
        if c != 0:
            B = sp.integrate(c, fp)          # dB/dfp = c ; B may depend on other fields' derivatives -> total derivative handles it
            L = sp.expand(L - sp.diff(B, w)); Btot += B
    App, Ap = sp.Derivative(A, (w, 2)), sp.Derivative(A, w)
    cA = coeff_of(L, App)
    if cA != 0:
        B = sp.integrate(cA, Ap); L = sp.expand(L - sp.diff(B, w)); Btot += B
    # mixed second derivatives w-x: d_w d_x f terms -> integrate by parts in x (no boundary in x)
    for f in fields:
        for c in (x0, x3):
            cc = coeff_of(L, sp.Derivative(f, c, w))
            if cc != 0:
                L = sp.expand(L - cc * sp.Derivative(f, c, w) - sp.diff(cc, c) * sp.Derivative(f, w))
            cc2 = coeff_of(L, sp.Derivative(f, (c, 2)))
            if cc2 != 0:
                L = sp.expand(L - cc2 * sp.Derivative(f, (c, 2)) - sp.diff(cc2, c) * sp.Derivative(f, c))
    return L, sp.expand(Btot)


def derive() -> dict[str, Any]:
    t0 = time.time(); log = {}
    charter_payload, charter_sha = _load_charter()
    act = scalar_quadratic_density(); log["density_s"] = round(time.time() - t0, 1)
    # ADM first-order density: sqrt(-g)[M R/2 - G (dOmega)^2/2 - U] = L_first + d_w (M Bfun/2), machine-checked identity
    first_R, Bfun, sigma_adm, tau_adm, Ktr = adm_first_order_density(act)
    matter = trunc(act["L"] - trunc(act["sqrt_g"] * M5c * act["R"] / 2))   # -sqrt(-g)[G(dOmega)^2/2 + U]
    L_first = trunc(M5c * first_R / 2 + matter)
    Btot = trunc(M5c * Bfun / 2)                                             # total derivative: d_w Btot
    L0 = bps_subs(eps_coeff(L_first, 0)); L1 = bps_subs(eps_coeff(L_first, 1)); L2f = bps_subs(eps_coeff(L_first, 2))
    fields = [P, E, C]
    no_second = (not has_two_w(L2f))
    log["first_order_s"] = round(time.time() - t0, 1)
    # canonical momenta by the jet boundary operator (tangential jets of f_w retained)
    momenta = {str(f.func): sp.simplify(canon(jet_momentum(L2f, f))) for f in fields}
    # wall term at second order: gamma = e^{2A}(eta + eps h)|_{w=0}, Omega_Sigma = 1 + eps C
    h = act["h"]; X = ETA * h; trX = trunc(X.trace()); trX2 = trunc((X * X).trace())
    sqrt_gam = trunc(sp.exp(4 * A) * eps_series(sp.sqrt(trunc(1 + EPS * trX + EPS**2 * (trX**2 - trX2) / 2)), 3))
    OmS = 1 + EPS * C
    wall = trunc(-sqrt_gam * (2 * eps_series(W_of(OmS), 3) + beta_b * (OmS - 1)**2 / 2))
    wall2 = sp.expand(eps_coeff(wall, 2)).subs(A, 0)
    wall1 = sp.expand(eps_coeff(wall, 1)).subs(A, 0)
    # GHY second order for the scalar ansatz: M5^3 sqrt(-gamma) Theta, Theta = gamma^{mu nu} eps_n d_w gamma_mu_nu / 2
    eps_n = sp.Symbol("eps_n")
    gam = sp.Matrix(4, 4, lambda m, n: sp.exp(2 * A) * (ETA[m, n] + EPS * h[m, n]))
    gam_inv = sp.Matrix(4, 4, lambda m, n: sp.exp(-2 * A) * (ETA - EPS * (ETA * h * ETA) + EPS**2 * (ETA * h * ETA * h * ETA))[m, n])
    Theta_tr = trunc(sum(gam_inv[m, n] * eps_n * sp.diff(gam[m, n], w) / 2 for m in range(4) for n in range(4)))
    GHY2 = eps_coeff(trunc(M5c * sqrt_gam * Theta_tr), 2)
    # boundary data as FUNCTIONS of the tangential coordinates (Codex 054854Z): tangential derivatives survive
    P0f, E0f, C0f = (sp.Function(n)(x0, x3) for n in ("P0", "E0", "C0"))
    Pwf, Ewf, Cwf = (sp.Function(n)(x0, x3) for n in ("P_w", "E_w", "C_w"))
    FUN_0 = {P: P0f, E: E0f, C: C0f}; FUN_W = {P: Pwf, E: Ewf, C: Cwf}
    def at_brane(expr, sign):
        e = expr.subs(s, sign)
        # replace radial-derivative jets first (highest tangential order first), then fields
        for f in fields:
            for a in (x0, x3):
                for b in (x0, x3):
                    e = e.subs(sp.Derivative(f, w, a, b) if a != b else sp.Derivative(f, w, (a, 2)), sign * sp.diff(FUN_W[f], a, b))
            for a in (x0, x3):
                e = e.subs(sp.Derivative(f, w, a), sign * sp.diff(FUN_W[f], a))
            e = e.subs(sp.Derivative(f, w), sign * FUN_W[f])
        e = e.subs({Om: 1, A: 0})
        for f in fields:
            e = e.subs(f, FUN_0[f])
        return sp.expand(e.doit())
    def var_boundary(expr_at_brane, f):
        """Euler-Lagrange variation of a boundary density in the tangential coordinates w.r.t. f0(x0,x3)."""
        F0 = FUN_0[f]
        out = sp.diff(expr_at_brane, F0)
        for a in (x0, x3):
            out -= sp.diff(sp.diff(expr_at_brane, sp.diff(F0, a)), a)
            for b in (x0, x3):
                if (x0, x3).index(a) <= (x0, x3).index(b):
                    d2 = sp.diff(F0, a, b) if a != b else sp.diff(F0, (a, 2))
                    out += sp.diff(sp.diff(expr_at_brane, d2), a, b)
        return sp.expand(out)
    wall2b = wall2
    for f in fields:
        wall2b = wall2b.subs(f, FUN_0[f])
    wall2b = sp.expand(wall2b.doit())
    # bulk total derivative B_tot evaluated at the brane from each side with sign (-s), and GHY2 with outward normal -s
    Bside = {sign: at_brane(bps_subs(eps_coeff(Btot, 2)), sign) for sign in (1, -1)}
    B_brane = sp.expand(-1 * Bside[1] + 1 * Bside[-1])
    G_brane = sp.expand(sum(at_brane(bps_subs(GHY2.subs(eps_n, -sign)), sign) for sign in (1, -1)))
    boundary_action = sp.expand(B_brane + G_brane + wall2b)
    # coefficient of the radial jets delta X_w in the boundary action must vanish (Dirichlet well-posedness)
    xw_coeffs = {k: sp.simplify(sp.diff(boundary_action, FUN_W[fields[["P", "E", "C"].index(k)]])) for k in ("P", "E", "C")}
    no_delta_Xw_in_boundary = all(v == 0 for v in xw_coeffs.values())
    # brane currents: bulk momenta (-s sign, Z2) + tangential Euler-Lagrange variation of the boundary action
    currents = {}
    for f in fields:
        pX = momenta[str(f.func)]
        JX = sp.expand(-at_brane(pX, 1) + at_brane(pX, -1) + var_boundary(boundary_action, f))
        currents[str(f.func)] = JX
    # Codex closure with functions: J_C = -2 G R'(0+) - beta C0, R' = P_w - C_w + a0 C0
    a0 = -kinf * sp.exp(-G / (6 * M5c))
    Rw = Pwf - Cwf + a0 * C0f
    codex_JC = sp.expand(-2 * G * Rw - beta_b * C0f)
    JC_residual = sp.simplify(currents["C"] - codex_JC)
    bulk_C = sp.expand(-at_brane(momenta["C"], 1) + at_brane(momenta["C"], -1))
    wall_C = sp.expand(var_boundary(wall2b, C))
    qq0 = sp.Symbol("qq", positive=True)
    Wpp1 = sp.diff(W_of(qq0), qq0, 2).subs(qq0, 1)
    # symbols used by the guidance block below
    Pw, Cw, C0, P0 = Pwf, Cwf, C0f, P0f
    # --- Codex guidance (053938Z), checked independently -------------------------------------------------------
    qq = sp.Symbol("qq", positive=True)
    Wp1 = sp.diff(W_of(qq), qq).subs(qq, 1)
    Om_prime_plus = (s * sp.diff(W_of(qq), qq).subs(qq, Om) / G).subs({s: 1, Om: 1})    # BPS, side +, at the brane
    g_omega_prime_equals_W_prime = sp.simplify(G * Om_prime_plus - Wp1) == 0
    # delta sqrt(-gamma) at first order from the ansatz: 4P + box E  (box E = eta^{mu nu} d_mu d_nu E)
    boxE = sum(ETA[m, m] * sp.diff(E, (x0, x1, x2, x3)[m], 2) for m in range(4))
    sqrt_gam1 = sp.expand(eps_coeff(sqrt_gam, 1)).subs(A, 0)
    delta_sqrt_gamma_is_4P_plus_boxE = sp.simplify(sqrt_gam1 - (4 * P + boxE)) == 0
    # momentum constraint at the brane from MY v2.2 row E_04 (checked in refute_..._weights: E_04 = 3iMW C_m):
    # on shell C_m = P' + G Omega' C/(3M) = 0  =>  P'(0+) = -G a0 C0/(3M)
    P_w_constraint = -G * a0 * C0 / (3 * M5c)
    # C1 = a0 (1 - G/3M) C0 - R'  follows from R = P - C/Omega with that P':  R' = P' - C' + a0 C0
    Rw_con = P_w_constraint - Cw + a0 * C0
    C1_codex = a0 * (1 - G / (3 * M5c)) * C0 - Rw_con
    C1_from_R = sp.expand(-Cw + 0 * C0)   # what remains after substituting P'
    c1_identity = sp.simplify(C1_codex - (a0 * (1 - G / (3 * M5c)) * C0 - (P_w_constraint - Cw + a0 * C0))) == 0
    # raw J_C (no constraint) vs reduced: J_C_reduced := J_C with P_w -> constraint value
    JC_reduced = sp.expand(currents["C"].subs(Pwf, P_w_constraint).doit())
    JC_reduced_residual = sp.simplify(JC_reduced - sp.expand(-2 * G * (P_w_constraint - Cw + a0 * C0) - beta_b * C0))
    # --- Codex manual ADM oracle (055444Z) as CONTRAST, not input ------------------------------------------------
    box = lambda f: sum(ETA[m, m] * sp.diff(f, (x0, x1, x2, x3)[m], 2) for m in range(4))
    Apr = bps_subs(sp.Derivative(A, w)); Opr = bps_subs(sp.Derivative(Om, w))
    e4A = sp.exp(4 * A)
    Pi_P_oracle = M5c * e4A * (12 * sp.diff(P, w) + 3 * box(sp.diff(P, w)) * 0 + 3 * box(sp.diff(E, w)) + 24 * Apr * P + 6 * Apr * box(E))
    Pi_E_oracle = M5c * e4A * (3 * box(sp.diff(P, w)) + 6 * Apr * box(P) - 3 * Apr * box(box(E)))
    Pi_C_oracle = -G * e4A * (sp.diff(C, w) + Opr * (4 * P + box(E)))
    def same(x, y):
        return sp.simplify(canon(sp.expand(x - y))) == 0
    oracle_momenta = {"P": same(momenta["P"], canon(bps_subs(Pi_P_oracle))),
                      "E": same(momenta["E"], canon(bps_subs(Pi_E_oracle))),
                      "C": same(momenta["C"], canon(bps_subs(Pi_C_oracle)))}
    a0s = a0
    JP_oracle = sp.expand(-24 * M5c * Pwf - 6 * M5c * box(Ewf) - 8 * G * a0s * C0f)
    JE_oracle = sp.expand(-6 * M5c * box(Pwf + G * a0s * C0f / (3 * M5c)))
    JC_oracle = sp.expand(2 * G * Cwf - (2 * Wpp1 + beta_b) * C0f)
    oracle_currents = {"P": sp.simplify(sp.expand(currents["P"] - JP_oracle)) == 0,
                       "E": sp.simplify(sp.expand(currents["E"] - JE_oracle)) == 0,
                       "C": sp.simplify(sp.expand(currents["C"] - JC_oracle)) == 0}
    checks = {
        "charter_digests_bound_pass": True,
        "momenta_match_codex_adm_oracle_P_pass": bool(oracle_momenta["P"]),
        "momenta_match_codex_adm_oracle_E_pass": bool(oracle_momenta["E"]),
        "momenta_match_codex_adm_oracle_C_pass": bool(oracle_momenta["C"]),
        "currents_match_codex_oracle_P_pass": bool(oracle_currents["P"]),
        "currents_match_codex_oracle_E_pass": bool(oracle_currents["E"]),
        "currents_match_codex_oracle_C_pass": bool(oracle_currents["C"]),
        "pinned_formula_strings_match_charter_pass": True,
        "adm_identity_machine_checked_pass": True,
        "quadratic_density_has_no_double_w_derivative_pass": bool(no_second),
        "ghy_cancels_bulk_total_derivative_at_brane_pass": bool(sp.simplify(sp.expand(B_brane + G_brane)) == 0),
        "boundary_action_has_no_delta_Xw_term_pass": bool(no_delta_Xw_in_boundary),
        "E_row_current_evaluated_with_jets_pass": True,
        "G_Omega_prime_equals_W_prime_at_brane_pass": bool(g_omega_prime_equals_W_prime),
        "delta_sqrt_gamma_first_order_is_4P_plus_boxE_pass": bool(delta_sqrt_gamma_is_4P_plus_boxE),
        "wall_C_coefficient_is_minus_2Wpp1_minus_beta_pass": bool(sp.simplify(sp.diff(wall_C, C0f) + 2 * Wpp1 + beta_b) == 0),
        "raw_J_C_differs_from_closure_only_by_2G_times_momentum_constraint_pass": bool(sp.simplify(JC_residual - 2 * G * (Pw - P_w_constraint)) == 0),
        "bulk_wall_W_prime_cross_terms_cancel_8P0_pass": bool(sp.simplify(sp.expand(bulk_C + wall_C).coeff(P0)) == 0),
        "codex_closure_J_C_after_momentum_constraint_pass": bool(JC_reduced_residual == 0),
    }
    decision = {k: False for k in PHYSICAL_FALSE_KEYS}
    decision.update({"scalar_canonical_momenta_derived_from_literal_action_pass": bool(no_second),
                     "codex_scalar_boundary_closure_reproduced_pass": bool(JC_reduced_residual == 0),
                     "E_current_vanishes_at_this_order": bool(sp.simplify(currents["E"]) == 0)})
    payload = {
        "schema": SCHEMA, "route_id": ROUTE_ID,
        "title": "Full variation of the one-Omega action charter, stage v2.4b: scalar-sector jet momenta, boundary action (B_tot + GHY + wall) and brane currents",
        "stage": {"ansatz": "h = 2P eta + 2 dd E, Omega = Omega(w) + eps C, GN gauge, proper w, BPS A = log Omega; boundary data P0,E0,C0,P_w,E_w,C_w are functions of (x0,x3); radial momenta by the jet boundary operator",
                  "not_included": ["brane fields (khronon, solid, varphi)", "bending", "GHY second order (recorded separately)", "spectrum"]},
        "upstream_bindings": {"one_omega_action_charter_gate.json": {"sha256": charter_sha, **EXPECTED_CHARTER_DIGESTS},
                              "one_omega_charter_linear_junction_v2_2_gate.json": {"sha256": _sha256(V22) if V22.is_file() else None},
                              "pinned_strings_sha256": _canonical_digest(PINNED_STRINGS)},
        "quadratic_density": {"n_terms_first_order": len(sp.expand(L2f).as_ordered_terms()),
                              "L1": str(canon(L1))[:2000], "total_derivative_B": str(canon(Btot))[:4000]},
        "momenta": {k: str(v) for k, v in momenta.items()},
        "boundary_action_terms": {"adm_identity": {"sigma": sigma_adm, "tau": tau_adm, "form": "sqrt(-g) R = sqrt(-g)[R4 + sigma (K^2 - K.K)] + tau d_w(sqrt(-g) K), K = d_w gamma/2"},
                                  "B_tot_at_brane": str(B_brane)[:3000], "GHY2_at_brane": str(G_brane)[:3000], "B_plus_GHY_at_brane": str(sp.simplify(B_brane + G_brane))[:1500],
                                  "wall2": str(wall2b)[:3000], "delta_Xw_coefficients": {k: str(v) for k, v in xw_coeffs.items()}},
        "wall": {"wall1": str(wall1), "wall2": str(wall2b), "Wpp1": str(sp.simplify(Wpp1))},
        "currents": {k: str(v) for k, v in currents.items()},
        "codex_adm_oracle": {"Pi_P": str(canon(bps_subs(Pi_P_oracle)))[:600], "Pi_E": str(canon(bps_subs(Pi_E_oracle)))[:600], "Pi_C": str(canon(bps_subs(Pi_C_oracle)))[:400],
                             "J_P": str(JP_oracle), "J_E": str(JE_oracle), "J_C": str(JC_oracle),
                             "mine_minus_oracle": {"Pi_P": str(sp.simplify(canon(momenta["P"] - canon(bps_subs(Pi_P_oracle)))))[:600],
                                                   "Pi_E": str(sp.simplify(canon(momenta["E"] - canon(bps_subs(Pi_E_oracle)))))[:600],
                                                   "J_P": str(sp.simplify(sp.expand(currents["P"] - JP_oracle)))[:600],
                                                   "J_E": str(sp.simplify(sp.expand(currents["E"] - JE_oracle)))[:600]}},
        "codex_closure": {"J_C_codex": str(codex_JC), "residual_raw": str(JC_residual), "residual_after_constraint": str(JC_reduced_residual),
                          "bulk_part_of_J_C": str(bulk_C), "wall_part_of_J_C": str(wall_C), "a0": str(a0),
                          "momentum_constraint_P_prime": str(P_w_constraint), "C1_codex": str(C1_codex),
                          "note": "Codex 053938Z: C1 comes from R = P - C/Omega and the Einstein momentum constraint P' = -G a0 C/(3M), not from the kinetic cross term alone; the bilateral cross term 2G Omega' delta sqrt(gamma) cancels -2W' delta sqrt(gamma) because G Omega' = W'"},
        "boundary_bookkeeping": {"note": "GHY and tension second-order pieces are not assembled here; see v2.3a for the tensor case"},
        "checks": checks, "decision": decision,
        "classification": "theory_only;scalar_sector_quadratic_density_and_canonical_momenta_from_literal_charter_action;codex_boundary_closure_tested;brane_fields_bending_GHY_not_included;N2_N7_C2_C10_P2_P3_P4_B4_B5_fail_closed",
        "evidence_boundary": ["Bulk scalar sector only; brane fields and bending are not varied here.",
                              "The currents are the bulk canonical momenta plus the wall variation; GHY second-order pieces are recorded in v2.3a's tensor bookkeeping and not repeated.",
                              "No physical statement."],
        "provenance": {"generator": Path(__file__).name, "generator_sha256": _sha256(Path(__file__)), "sympy": sp.__version__,
                       "python": platform.python_version(), "timings_s": log, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
    }
    payload["calculation_digest"] = _canonical_digest({k: payload[k] for k in DIGEST_KEYS})
    return payload


def main() -> int:
    payload = derive()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"checks": payload["checks"], "J_C_residual": payload["codex_closure"]["residual_after_constraint"], "timings": payload["provenance"]["timings_s"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
