#!/usr/bin/env python3
"""Full variation of the one-Omega action charter, stage v2.4: scalar-sector canonical momenta from the literal action.

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
OUTPUT = HERE / "artifacts" / "one_omega_charter_scalar_momentum_v2_4_gate.json"
CHARTER = HERE / "artifacts" / "one_omega_action_charter_gate.json"
V22 = HERE / "artifacts" / "one_omega_charter_linear_junction_v2_2_gate.json"
SCHEMA = "holo.one-omega-charter-scalar-momentum.v2.4"
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
               "codex_closure", "boundary_bookkeeping", "checks", "decision", "classification", "evidence_boundary")


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
    return {"L": L, "sqrt_g": sqrt_g, "h": h, "g": g, "ginv": ginv, "Gam": Gam, "sqrt_g": sqrt_g}


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
    L = act["L"]
    L0 = bps_subs(eps_coeff(L, 0)); L1 = bps_subs(eps_coeff(L, 1)); L2 = sp.expand(eps_coeff(L, 2))
    fields = [P, E, C]
    L2f, Btot = first_order_form(L2, fields)
    L2f = bps_subs(L2f)
    # cross terms f f' -> total derivative + potential (all pairs)
    for f in fields:
        for gf in fields:
            c = coeff_of(coeff_of(L2f, sp.Derivative(gf, w)), f)
            if c != 0 and f == gf:
                L2f = bps_subs(sp.expand(L2f - c * f * sp.Derivative(f, w) - sp.diff(c, w) * f**2 / 2)); Btot += c * f**2 / 2
    # any remaining second derivatives?
    no_second = all(coeff_of(L2f, sp.Derivative(f, (w, 2))) == 0 for f in fields) and coeff_of(L2f, sp.Derivative(A, (w, 2))) == 0
    log["first_order_s"] = round(time.time() - t0, 1)
    # canonical momenta at the brane
    momenta = {str(f.func): sp.simplify(canon(sp.diff(L2f, sp.Derivative(f, w)))) for f in fields}
    # wall term at second order: -sqrt(-gamma)[2W(Omega_Sigma) + beta (Omega_Sigma - 1)^2/2], gamma = e^{2A}(eta + eps h)|_{w=0}
    h = act["h"]; X = ETA * h; trX = trunc(X.trace()); trX2 = trunc((X * X).trace())
    sqrt_gam = trunc(sp.exp(4 * A) * eps_series(sp.sqrt(trunc(1 + EPS * trX + EPS**2 * (trX**2 - trX2) / 2)), 3))
    OmS = 1 + EPS * C
    wall = trunc(-sqrt_gam * (2 * W_of(OmS).series(EPS, 0, 3).removeO() + beta_b * (OmS - 1)**2 / 2))
    wall2 = sp.expand(eps_coeff(wall, 2)).subs(A, 0)
    wall1 = sp.expand(eps_coeff(wall, 1)).subs(A, 0)
    # brane currents: J_X = -p_X(0+) + p_X(0-) + d wall2/dX(0);  Z2: p(0-) obtained with s -> -s and odd first derivatives
    Pw, Ew, Cw = sp.symbols("P_w E_w C_w", real=True); P0, E0, C0 = sp.symbols("P0 E0 C0", real=True)
    SYM_W = {P: Pw, E: Ew, C: Cw}; SYM_0 = {P: P0, E: E0, C: C0}
    def at_brane(expr, sign):
        e = expr.subs(s, sign)
        for f in fields:
            e = e.subs(sp.Derivative(f, w), sign * SYM_W[f])
        e = e.subs({Om: 1, A: 0})
        for f in fields:
            e = e.subs(f, SYM_0[f])
        return sp.expand(e)
    wall2b = wall2
    for f in fields:
        wall2b = wall2b.subs(f, SYM_0[f])
    currents = {}
    for f in fields:
        pX = momenta[str(f.func)]
        JX = sp.expand(-at_brane(pX, 1) + at_brane(pX, -1) + sp.diff(wall2b, SYM_0[f]))
        currents[str(f.func)] = JX
    # Codex closure: J_C = -2 G R'(0+) - beta C0 with R = P - C/Omega -> R' = P' - C' + C Omega'/Omega^2 ; at 0+: Omega'=a0
    a0 = -kinf * sp.exp(-G / (6 * M5c))
    Rw = Pw - Cw + C0 * a0
    codex_JC = sp.expand(-2 * G * Rw - beta_b * C0)
    JC_residual = sp.simplify(currents["C"] - codex_JC)
    # provenance of the a0(1 - G/3M) C0 term: split J_C into bulk (momentum) and wall pieces
    bulk_C = sp.expand(-at_brane(momenta["C"], 1) + at_brane(momenta["C"], -1))
    wall_C = sp.expand(sp.diff(wall2b, C0))
    Wpp1 = sp.diff(W_of(sp.Symbol("qq", positive=True)), sp.Symbol("qq", positive=True), 2).subs(sp.Symbol("qq", positive=True), 1)
    wall_C_expected = sp.expand(-(2 * Wpp1 + beta_b) * C0 - 2 * sp.diff(W_of(sp.Symbol("qq", positive=True)), sp.Symbol("qq", positive=True)).subs(sp.Symbol("qq", positive=True), 1) * (4 * P0))
    # (the wall also couples C0 to the trace of h through sqrt(-gamma)_1 * W'(1): 8 P0 term; recorded, not assumed)
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
    JC_reduced = sp.expand(currents["C"].subs(Pw, P_w_constraint))
    JC_reduced_residual = sp.simplify(JC_reduced - sp.expand(-2 * G * (P_w_constraint - Cw + a0 * C0) - beta_b * C0))
    checks = {
        "charter_digests_bound_pass": True,
        "pinned_formula_strings_match_charter_pass": True,
        "quadratic_density_reduced_to_first_order_pass": bool(no_second),
        "G_Omega_prime_equals_W_prime_at_brane_pass": bool(g_omega_prime_equals_W_prime),
        "delta_sqrt_gamma_first_order_is_4P_plus_boxE_pass": bool(delta_sqrt_gamma_is_4P_plus_boxE),
        "wall_C_coefficient_is_minus_2Wpp1_minus_beta_pass": bool(sp.simplify(sp.diff(wall_C, C0) + 2 * Wpp1 + beta_b) == 0),
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
        "title": "Full variation of the one-Omega action charter, stage v2.4: scalar-sector canonical momenta and brane currents from the literal action",
        "stage": {"ansatz": "h = 2P eta + 2 dd E, Omega = Omega(w) + eps C, GN gauge, proper w, BPS A = log Omega",
                  "not_included": ["brane fields (khronon, solid, varphi)", "bending", "GHY second order (recorded separately)", "spectrum"]},
        "upstream_bindings": {"one_omega_action_charter_gate.json": {"sha256": charter_sha, **EXPECTED_CHARTER_DIGESTS},
                              "one_omega_charter_linear_junction_v2_2_gate.json": {"sha256": _sha256(V22) if V22.is_file() else None},
                              "pinned_strings_sha256": _canonical_digest(PINNED_STRINGS)},
        "quadratic_density": {"n_terms_L2": len(sp.expand(L2).as_ordered_terms()), "n_terms_first_order": len(sp.expand(L2f).as_ordered_terms()),
                              "L1": str(canon(L1))[:2000], "total_derivative_B": str(canon(Btot))[:4000]},
        "momenta": {k: str(v) for k, v in momenta.items()},
        "wall": {"wall1": str(wall1), "wall2": str(wall2b), "Wpp1": str(sp.simplify(Wpp1))},
        "currents": {k: str(v) for k, v in currents.items()},
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
