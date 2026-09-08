#!/usr/bin/env python3
"""Full variation of the one-Omega action charter, stage v2.3a: tensor sector, Dirichlet-to-Neumann map and assembly.

Symbolic part (exact):
1. the quadratic action of the transverse-traceless bulk mode h_12(x0, x3, w) on the
   v2.1 BPS wall, from sqrt(-g) [M5^3 R/2 - G (dOmega)^2/2 - U] to second order,
   reduced with the BPS relations to a first-order-in-w density plus an explicit
   total w-derivative;
2. its Euler-Lagrange equation reproduces the v2.2 tensor ODE;
3. the boundary bookkeeping at w = 0: the total-derivative term of both sides, the
   second-order GHY term and the second-order tension term of the brane cancel
   exactly on the BPS background, so the tensor mode has no tadpole residual;
4. the resulting normalization of the bulk boundary operator that multiplies
   h'(0+) in the assembled brane quadratic form.

Numerical part (witness, not proof; frozen charter parameters):
5. the BPS profile A(w), Omega(w) for w > 0 (Z2), and M5^3 * Int e^{2A} dw over
   both sides compared with the charter's frozen
   M4_bulk_squared_selected_one_Omega_wall_value;
6. the tensor Dirichlet-to-Neumann function Pi_T(p^2) for spacelike momenta
   p^2 = q^2 - W^2 > 0 from the decaying bulk solution, its small-p^2 slope
   compared with the same warp integral, and the assembled tensor operator
   brane(v1, tadpole-free) + Pi_T with the induced Planck mass and the
   solid-induced tensor mass term read off.

Not done: vector and scalar sectors, timelike momenta, spectrum/stability,
constraints, characteristics, N2-N7, P2-P4, B4, B5.  Every physical key stays
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

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp, quad

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "one_omega_charter_dtn_assembly_v2_3_gate.json"
CHARTER = HERE / "artifacts" / "one_omega_action_charter_gate.json"
V1 = HERE / "artifacts" / "one_omega_charter_full_variation_interface_v1_gate.json"
V22 = HERE / "artifacts" / "one_omega_charter_linear_junction_v2_2_gate.json"
SCHEMA = "holo.one-omega-charter-dtn-assembly.v2.3a"
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
FROZEN = {"M5_cubed": 1.0, "k_infinity": 1.0, "compensator_metric_G": 1.2, "brane_Mb_squared": 2.0, "xi": 1.0,
          "solid_mu": 1.0, "solid_v": 1.0, "M4_bulk_squared_selected_one_Omega_wall_value": 1.107013790800849}
PHYSICAL_FALSE_KEYS = (
    "B4_pass", "B5_pass", "P2_pass", "P3_complete_pass", "P4_full_same_action_pass", "nonlinear_gravitational_P4_pass",
    "N2_pass", "N3_pass", "N4_pass", "N5_pass", "N6_pass", "N7_pass", "C2_pass", "C4_pass", "C10_pass",
    "vector_sector_assembled_pass", "scalar_sector_assembled_pass", "timelike_dtn_pass", "spectrum_or_stability_claimed",
    "nonlinear_constraints_derived_pass", "characteristics_derived_pass", "phenomenology_claimed",
)
DIGEST_KEYS = ("schema", "route_id", "stage", "upstream_bindings", "tensor_quadratic_action", "boundary_bookkeeping",
               "numerics", "assembly", "checks", "decision", "classification", "evidence_boundary")


class DtnAssemblyError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_charter() -> tuple[dict[str, Any], str]:
    if not CHARTER.is_file():
        raise DtnAssemblyError("action charter artifact is absent")
    payload = json.loads(CHARTER.read_text(encoding="utf-8"))
    for key, expected in EXPECTED_CHARTER_DIGESTS.items():
        recorded = payload.get(key)
        recorded = recorded.get("sha256") if isinstance(recorded, dict) else recorded
        if str(recorded) != expected:
            raise DtnAssemblyError(f"charter {key} mismatch")
    charter = payload["action_charter"]
    for dotted, expected in PINNED_STRINGS.items():
        block, key = dotted.split(".")
        if str(charter[block].get(key)) != expected:
            raise DtnAssemblyError(f"pinned string {dotted} differs from charter")
    frozen = (charter.get("coefficient_policy") or {}).get("parameters") or {}
    if "M4_bulk_squared_selected_one_Omega_wall_value" not in frozen:
        raise DtnAssemblyError("charter coefficient_policy.parameters lacks the frozen M4^2")
    for key in ("M4_bulk_squared_selected_one_Omega_wall_value", "M5_cubed", "compensator_metric_G", "brane_Mb_squared", "xi", "solid_mu", "solid_v"):
        if key in frozen and abs(float(frozen[key]) - FROZEN[key]) > 1e-15:
            raise DtnAssemblyError(f"frozen parameter {key} differs from the charter")
    if abs(float(frozen.get("eta", 3.107013790800849)) - 3.107013790800849) > 1e-15:
        raise DtnAssemblyError("frozen eta differs from the charter")
    return payload, _sha256(CHARTER)


# ----------------------------------------------------------------------------- symbols
EPS = sp.Symbol("epsilon")
w = sp.Symbol("w", real=True)
x0, x1, x2, x3 = sp.symbols("x0 x1 x2 x3", real=True)
COORDS = (x0, x1, x2, x3, w)
M5c, kinf, G = sp.symbols("M5c k_inf G", positive=True)
s = sp.Symbol("s")
A = sp.Function("A")(w)
Om = sp.Function("Omega")(w)
h = sp.Function("h")(x0, x3, w)


def W_of(x):
    return 3 * M5c * kinf * sp.exp(-G * x**2 / (6 * M5c))


def U_of(x):
    qq = sp.Symbol("qq", positive=True)
    return (sp.diff(W_of(qq), qq)**2 / (2 * G) - 2 * W_of(qq)**2 / (3 * M5c)).subs(qq, x)


def trunc(expr, order=2):
    expr = sp.expand(expr)
    return sum((expr.coeff(EPS, k) * EPS**k for k in range(order + 1)), sp.Integer(0))


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


def tt_quadratic_action():
    """sqrt(-g) L_bulk to O(eps^2) for the single TT mode h_12 = h(x0,x3,w)."""
    eta = sp.diag(-1, 1, 1, 1)
    g = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            g[m, n] = sp.exp(2 * A) * eta[m, n]
    g[1, 2] = g[2, 1] = sp.exp(2 * A) * EPS * h
    g[4, 4] = 1
    # inverse to O(eps^2): only the 1-2 block is perturbed
    ginv = sp.zeros(5, 5)
    for m in range(4):
        ginv[m, m] = sp.exp(-2 * A) * eta[m, m]
    ginv[1, 1] = sp.exp(-2 * A) * (1 + EPS**2 * h**2)
    ginv[2, 2] = sp.exp(-2 * A) * (1 + EPS**2 * h**2)
    ginv[1, 2] = ginv[2, 1] = -sp.exp(-2 * A) * EPS * h
    ginv[4, 4] = 1
    # check inverse to O(eps^2)
    assert all(trunc(sum(g[m, k] * ginv[k, n] for k in range(5)) - (1 if m == n else 0)) == 0 for m in range(5) for n in range(5))
    det = trunc(g.det())
    sqrt_g = trunc(sp.exp(4 * A) * sp.sqrt(sp.expand(-det * sp.exp(-8 * A))).series(EPS, 0, 3).removeO())  # Lorentzian: sqrt(-det)
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
    dOm = [sp.diff(Om, c) for c in COORDS]
    kin = trunc(sum(ginv[m, k] * dOm[m] * dOm[k] for m in range(5) for k in range(5)))
    L = trunc(sqrt_g * (M5c * R / 2 - G * kin / 2 - U_of(Om)))
    return {"L": L, "sqrt_g": sqrt_g, "R": R}


def derive() -> dict[str, Any]:
    t0 = time.time()
    charter_payload, charter_sha = _load_charter()
    log = {}
    act = tt_quadratic_action(); log["symbolic_action_s"] = time.time() - t0
    L = act["L"]
    L0 = bps_subs(L.coeff(EPS, 0)); L1 = bps_subs(L.coeff(EPS, 1)); L2 = sp.expand(L.coeff(EPS, 2))
    # L0 on BPS: the background density; L1 must vanish (TT mode has no tadpole in the bulk density)
    tt_no_first_order = sp.simplify(L1) == 0
    # remove second w-derivatives of h and of A from L2 by explicit total derivatives
    hpp = sp.Derivative(h, (w, 2)); hp = sp.Derivative(h, w)
    c_hpp = sp.expand(L2).coeff(hpp)
    B1 = sp.integrate(c_hpp, hp)               # d/dw B1 reproduces the c_hpp * h'' term (plus extra pieces)
    L2a = sp.expand(L2 - sp.diff(B1, w))
    App = sp.Derivative(A, (w, 2))
    c_App = sp.expand(L2a).coeff(App)
    B2 = sp.integrate(c_App, sp.Derivative(A, w))
    L2b = sp.expand(L2a - sp.diff(B2, w))
    # also x-second-derivatives -> integrate by parts in x0, x3 (no boundary in x)
    for c in (x0, x3):
        cc = sp.expand(L2b).coeff(sp.Derivative(h, (c, 2)))
        L2b = sp.expand(L2b - cc * sp.Derivative(h, (c, 2)) - sp.diff(cc, c) * sp.Derivative(h, c))
    L2_first = bps_subs(L2b)
    # cross term c(w) h h' = d/dw(c h^2/2) - (c'/2) h^2 : move it into the total derivative
    c_cross = sp.simplify(sp.expand(L2_first).coeff(h).coeff(hp))
    B3 = c_cross * h**2 / 2
    L2_first = bps_subs(sp.expand(L2_first - c_cross * h * hp - sp.diff(c_cross, w) * h**2 / 2))
    no_second = (sp.expand(L2_first).coeff(hpp) == 0) and (sp.expand(L2_first).coeff(App) == 0)
    # canonical form: C_w h'^2 + C_t hdot^2 + C_x h_,3^2 + C_0 h^2
    hd, hx = sp.Derivative(h, x0), sp.Derivative(h, x3)
    C_w = sp.simplify(sp.expand(L2_first).coeff(hp, 2)); C_t = sp.simplify(sp.expand(L2_first).coeff(hd, 2))
    C_x = sp.simplify(sp.expand(L2_first).coeff(hx, 2)); C_0 = sp.simplify(sp.expand(L2_first).coeff(h, 2))
    rest = sp.simplify(sp.expand(L2_first - C_w * hp**2 - C_t * hd**2 - C_x * hx**2 - C_0 * h**2))
    canonical = (rest == 0)
    mass_term_vanishes = (C_0 == 0)
    # expected normalization: -(M5^3/4) e^{4A} h'^2 + (M5^3/4) e^{2A} (hdot^2 - h_,3^2)
    norm_ok = (sp.simplify(C_w + M5c * sp.exp(4 * A) / 4) == 0 and sp.simplify(C_t - M5c * sp.exp(2 * A) / 4) == 0
               and sp.simplify(C_x + M5c * sp.exp(2 * A) / 4) == 0)
    # Euler-Lagrange -> tensor ODE; compare with v2.2 form: h'' + 4A'h' - e^{-2A}(q^2 - W^2) h = 0
    EL = sp.diff(L2_first, h) - sp.diff(sp.diff(L2_first, hp), w) - sp.diff(sp.diff(L2_first, hd), x0) - sp.diff(sp.diff(L2_first, hx), x3)
    EL = bps_subs(sp.expand(EL))
    q_, Wf = sp.symbols("q_mom W_freq", real=True)
    H = sp.Function("H")(w)
    theta = q_ * x3 - Wf * x0
    ELr = sp.simplify(sp.expand(EL.subs(h, H * sp.exp(sp.I * theta)).doit() * sp.exp(-sp.I * theta)))
    Ap_b = bps_subs(sp.Derivative(A, w))
    target = sp.diff(H, (w, 2)) + 4 * Ap_b * sp.diff(H, w) - sp.exp(-2 * A) * (q_**2 - Wf**2) * H
    ratio = sp.simplify(ELr / target)
    el_matches_v22 = (not ratio.has(H)) and (not ratio.has(q_)) and (not ratio.has(Wf))
    log["symbolic_reduction_s"] = time.time() - t0
    # --- boundary bookkeeping at w = 0 (Z2): total derivative from both sides + GHY(2) + tension(2) --------
    # bulk total derivative B = B1 + B2 evaluated at w=0 from side s contributes (-s) B
    Btot = sp.expand(B1 + B2 + B3)
    Bside = bps_subs(Btot)   # contains s via A'
    # sum over sides of (-s) * B_s: with Z2, h'(0-) = -h'(0+) (h even), A' odd -> substitute
    hp_p = sp.Symbol("hprime_plus"); h0 = sp.Symbol("h0"); A0 = 0
    def side_val(sign):
        e = Bside.subs(s, sign).subs(sp.Derivative(h, w), sign * hp_p).subs(h, h0)
        return e.subs(A, A0).subs(Om, 1)   # brane values: A(0)=0, Omega_Sigma=1
    bulk_boundary = sp.simplify(-1 * side_val(1) + 1 * side_val(-1))
    # GHY to second order: M5^3 sqrt(-gamma) Theta with outward normal -s d_w; Theta = trace of (eps A' gamma + eps h-terms)
    # For the TT mode gamma_mu_nu = e^{2A}(eta + eps h e12), Theta_mu_nu = (1/2) eps_n d_w gamma_mu_nu, Theta = gamma^{mu nu} Theta_mu_nu
    eps_n = sp.Symbol("eps_n")
    gam = sp.Matrix(4, 4, lambda m, n: sp.exp(2 * A) * (sp.diag(-1, 1, 1, 1)[m, n] + (EPS * h if {m, n} == {1, 2} else 0)))
    gam_inv = sp.Matrix(4, 4, lambda m, n: sp.exp(-2 * A) * (sp.diag(-1, 1, 1, 1)[m, n] + (EPS**2 * h**2 if m == n and m in (1, 2) else 0) - (EPS * h if {m, n} == {1, 2} else 0)))
    Theta_tr = trunc(sum(gam_inv[m, n] * eps_n * sp.diff(gam[m, n], w) / 2 for m in range(4) for n in range(4)))
    sqrt_gam = trunc(sp.exp(4 * A) * (1 - EPS**2 * h**2 / 2))
    GHY2 = trunc(M5c * sqrt_gam * Theta_tr).coeff(EPS, 2)
    GHY2_sum = 0
    for sign in (1, -1):
        e = GHY2.subs(eps_n, -sign)
        e = bps_subs(e).subs(s, sign).subs(sp.Derivative(h, w), sign * hp_p).subs(h, h0).subs(A, A0).subs(Om, 1)
        GHY2_sum += e
    GHY2_sum = sp.simplify(GHY2_sum)
    tension2 = sp.simplify((-2 * W_of(1) * sqrt_gam.coeff(EPS, 2)).subs(h, h0).subs(A, A0))
    total_boundary = sp.simplify(bulk_boundary + GHY2_sum + tension2)
    boundary_cancels = (total_boundary == 0)
    # boundary action has no h0*h' term once GHY is included (that is what GHY is for):
    boundary_hhprime = sp.simplify(sp.expand(bulk_boundary + GHY2_sum).coeff(hp_p).coeff(h0))
    # the Neumann coupling of the brane equation comes from the canonical momentum p = dL2/dh' = 2 C_w h' with the
    # (-s) boundary sign per side; Z2 (h'_- = -h'_+) gives  -p_+ + p_- = -4 C_w(0) h'_+
    neumann_coeff = sp.simplify(-4 * C_w.subs(A, 0))   # = M5^3 : bulk adds neumann_coeff * H'(0+)/H(0) to the brane operator
    log["boundary_s"] = time.time() - t0

    # --- numerics at the frozen point -------------------------------------------------------------------------
    M5, k, Gn = FROZEN["M5_cubed"], FROZEN["k_infinity"], FROZEN["compensator_metric_G"]
    def Wn(o): return 3 * M5 * k * math.exp(-Gn * o * o / (6 * M5))
    def dWn(o): return -Gn * o / (3 * M5) * Wn(o)
    def rhs(_, y):
        a, o = y
        return [-Wn(o) / (3 * M5), dWn(o) / Gn]
    wmax = 40.0
    sol = solve_ivp(rhs, (0.0, wmax), [0.0, 1.0], rtol=1e-11, atol=1e-13, dense_output=True, max_step=0.05)
    A_of = lambda ww: float(sol.sol(ww)[0]); Om_of = lambda ww: float(sol.sol(ww)[1])
    half_int, err = quad(lambda ww: math.exp(2 * A_of(ww)), 0.0, wmax, limit=400, epsabs=1e-12, epsrel=1e-12)
    tail = math.exp(2 * A_of(wmax)) / 2.0  # AdS tail with A' -> -k = -1
    M4_num = M5 * 2 * (half_int + tail)
    M4_charter = FROZEN["M4_bulk_squared_selected_one_Omega_wall_value"]
    m4_rel = abs(M4_num - M4_charter) / M4_charter
    m4_match = m4_rel < 1e-6
    # tensor DtN for spacelike p^2: solve H'' + 4A'H' - e^{-2A} p2 H = 0 inward from wmax with decaying data
    def dtn(p2):
        def f(ww, y):
            Hh, Hp = y
            return [Hp, -4 * (-Wn(Om_of(ww)) / (3 * M5)) * Hp + math.exp(-2 * A_of(ww)) * p2 * Hh]
        # start the inward integration where e^{-2A} p2 reaches 1e4 (deep in the decaying WKB regime, before stiffness)
        ws = 0.5
        while ws < wmax - 0.5 and math.exp(-2 * A_of(ws)) * p2 < 1e4:
            ws += 0.05
        Ap0 = -Wn(Om_of(ws)) / (3 * M5)
        lam = -2 * Ap0 - math.sqrt(4 * Ap0 * Ap0 + math.exp(-2 * A_of(ws)) * p2)   # decaying root of the local characteristic
        y0 = [1.0, lam]
        r = solve_ivp(f, (ws, 0.0), y0, rtol=1e-10, atol=1e-14, max_step=0.02, method="DOP853")
        Hh, Hp = r.y[0, -1], r.y[1, -1]
        return Hp / Hh
    grid = [1e-4, 1e-3, 1e-2, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
    ratios = {str(p2): dtn(p2) for p2 in grid}
    # small-p2 law: H'(0+)/H(0) -> -p2 * Int_0^inf e^{2A} dw  (zero mode)   [with A(0)=0]
    slope = ratios[str(1e-4)] / 1e-4
    slope_expected = -(half_int + tail)
    slope_rel = abs(slope - slope_expected) / abs(slope_expected)
    slope_ok = slope_rel < 1e-3
    # assembled tensor operator per unit amplitude: brane tadpole-free block + Neumann coupling x sum over sides
    Mb2, xi, mu, v = FROZEN["brane_Mb_squared"], FROZEN["xi"], FROZEN["solid_mu"], FROZEN["solid_v"]
    neumann_num = float(neumann_coeff.subs({M5c: M5}))
    def assembled(p2):
        # brane (v1, tadpole-free, xi=1 -> Lorentz invariant): -(Mb2/2) p2 - mu v^4 ; bulk: neumann_coeff * H'(0+)/H(0) per side, two sides
        # neumann_coeff = M5^3 already carries the Z2 sum of both sides (Codex 005334Z caught a duplicated factor 2 here)
        return -(Mb2 / 2) * p2 - mu * v**4 + neumann_num * ratios_at(p2)
    def ratios_at(p2):
        return dtn(p2)
    assembled_grid = {str(p2): assembled(p2) for p2 in (1e-3, 1e-2, 0.1, 1.0)}
    # brane operator -(Mb2/2) p2 plus bulk neumann_num * (-p2 * I) = -(Mb2 + 2 neumann_num I) p2 / 2 -> induced Planck mass^2
    induced_planck = Mb2 + 2 * neumann_num * (half_int + tail)
    # grid-vs-Planck consistency: at small p2 the assembled operator must equal -(induced_planck/2) p2 - mu v^4
    p2s = 1e-3
    grid_small = -(Mb2 / 2) * p2s - mu * v**4 + neumann_num * dtn(p2s)
    grid_pred = -(induced_planck / 2) * p2s - mu * v**4
    grid_vs_planck_rel = abs(grid_small - grid_pred) / abs(grid_pred)
    grid_vs_planck_ok = grid_vs_planck_rel < 1e-3
    # exact closed form of the warp integral (Codex 223839Z / 2e5fbf3; antecedent compensator_wall:512): with A = log Omega
    a_par = Gn / (6 * M5)
    M4_closed = 6 * M5**2 * (math.exp(a_par) - 1) / (k * Gn)
    m4_closed_rel = abs(M4_num - M4_closed) / M4_closed
    m4_closed_ok = m4_closed_rel < 1e-9
    eta_charter = 3.107013790800849
    eta_rel = abs(induced_planck - eta_charter) / eta_charter
    eta_match = eta_rel < 1e-6
    log["numerics_s"] = time.time() - t0

    checks = {
        "charter_digests_bound_pass": True,
        "pinned_formula_strings_match_charter_pass": True,
        "tt_mode_has_no_first_order_density_pass": bool(tt_no_first_order),
        "tt_quadratic_density_reduced_to_first_order_pass": bool(no_second),
        "tt_quadratic_density_canonical_form_pass": bool(canonical),
        "tt_mode_massless_in_bulk_pass": bool(mass_term_vanishes),
        "tt_normalization_M5_over_4_pass": bool(norm_ok),
        "tt_euler_lagrange_reproduces_v2_2_ode_pass": bool(el_matches_v22),
        "tt_boundary_terms_cancel_on_bps_pass": bool(boundary_cancels),
        "bps_warp_integral_reproduces_charter_M4_squared_pass": bool(m4_match),
        "tensor_dtn_small_momentum_slope_is_warp_integral_pass": bool(slope_ok),
        "boundary_action_has_no_h_hprime_term_after_ghy_pass": bool(boundary_hhprime == 0),
        "assembled_grid_consistent_with_induced_planck_pass": bool(grid_vs_planck_ok),
        "bps_warp_integral_matches_closed_form_pass": bool(m4_closed_ok),
        "induced_tensor_planck_mass_reproduces_charter_eta_pass": bool(eta_match),
    }
    decision = {k: False for k in PHYSICAL_FALSE_KEYS}
    decision.update({"tensor_sector_quadratic_action_boundary_and_dtn_pass": bool(all(checks.values())),
                     "tensor_dtn_computed_numerically_witness": True,
                     "old_wall_ADM_Hessian_consumed": False})
    payload = {
        "schema": SCHEMA, "route_id": ROUTE_ID,
        "title": "Full variation of the one-Omega action charter, stage v2.3a: tensor quadratic action, boundary bookkeeping, DtN witness and assembly",
        "stage": {"symbolic": "TT mode h_12(x0,x3,w) on the v2.1 BPS wall, second order, exact", "numeric": "frozen charter point; witness only",
                  "not_done": ["vector sector", "scalar sector (radion/khronon/solid mixing)", "timelike momenta", "spectrum"]},
        "upstream_bindings": {"one_omega_action_charter_gate.json": {"sha256": charter_sha, **EXPECTED_CHARTER_DIGESTS},
                              "one_omega_charter_full_variation_interface_v1_gate.json": {"sha256": _sha256(V1) if V1.is_file() else None, "used_for": "tensor block -(Mb2/2)(xi q^2 - W^2) - mu v^4 (tadpole-free)"},
                              "one_omega_charter_linear_junction_v2_2_gate.json": {"sha256": _sha256(V22) if V22.is_file() else None, "used_for": "tensor ODE cross-check"},
                              "pinned_strings_sha256": _canonical_digest(PINNED_STRINGS), "frozen_parameters": FROZEN},
        "tensor_quadratic_action": {"L0_on_bps": str(L0), "L1_on_bps": str(L1), "C_w": str(C_w), "C_t": str(C_t), "C_x": str(C_x), "C_0": str(C_0),
                                    "total_derivative_B": str(Btot), "euler_lagrange_over_v2_2_form": str(ratio)},
        "boundary_bookkeeping": {"bulk_total_derivative_both_sides": str(bulk_boundary), "GHY_second_order_both_sides": str(GHY2_sum),
                                 "tension_second_order": str(tension2), "total": str(total_boundary),
                                 "boundary_action_h0_hprime_coefficient": str(boundary_hhprime),
                                 "neumann_coupling_from_canonical_momentum_Z2": str(neumann_coeff),
                                 "reading": "on the BPS background the h^2 boundary pieces cancel between bulk, GHY and tension; the surviving h(0) h'(0+) coupling is the bulk boundary operator that acts through the DtN map"},
        "numerics": {"wmax": wmax, "A_at_wmax": A_of(wmax), "Omega_at_wmax": Om_of(wmax), "A_prime_asymptotic": -Wn(Om_of(wmax)) / (3 * M5),
                     "half_warp_integral": half_int, "ads_tail": tail, "M4_squared_numeric": M4_num, "M4_squared_charter": M4_charter, "M4_relative_error": m4_rel,
                     "tensor_dtn_Hprime_over_H_at_0plus": ratios, "small_p2_slope": slope, "small_p2_slope_expected": slope_expected, "slope_relative_error": slope_rel},
        "assembly": {"tensor_operator_per_amplitude": "-(Mb2/2)(xi q^2 - W^2) - mu v^4 + C_N * H'(0+)/H(0)  with C_N = " + str(neumann_coeff) + " (Z2 sum of both sides already included)",
                     "assembled_on_grid_spacelike_p2": assembled_grid,
                     "small_p2_reading": "H'/H -> -p2 * I with I = Int_0^inf e^{2A}; the bulk (both sides, via C_N = M5^3 = -p_+ + p_-) adds -M5^3 I p2 to the brane -(Mb2/2) p2, i.e. -(Mb2 + 2 M5^3 I) p2 / 2 = -(Mb2 + M4^2) p2 / 2; the solid contributes the p2-independent -mu v^4",
                     "jump_vs_outward_sign": "[H'] = H'(0+) - H'(0-) = -(n_+.grad H + n_-.grad H) with n_+ = -d_w, n_- = +d_w; the brane-equation bulk term -p_+ + p_- = M5^3 h'(0+) = (M5^3/2)[h'] (Codex 223700Z)",
                     "induced_planck_mass_squared_witness": induced_planck, "charter_eta": eta_charter, "eta_relative_error": eta_rel,
                     "eta_reading": "eta reproduces Mb2 + M4^2 because the charter selected eta_bare = 2(xi_bare + r0) with r0 = M4_bulk^2/Mb^2 (wall_adm gate lines 874-893, imported by the charter): a prior matching choice in Mb units, reproduced here from the literal action, not a new identity (Codex 224209Z)",
                     "M4_closed_form": M4_closed, "M4_closed_form_relative_error": m4_closed_rel,
                     "M4_reading": "M5^3 Int e^{2A} reproduces the charter's frozen M4^2; with A = log Omega (charter.background) the integral is 6 M5^6 [e^{G/(6M5^3)} - 1]/(k G), an antecedent of compensator_wall:512, verified exactly by Codex 2e5fbf3",
                     "grid_vs_planck_relative_error": grid_vs_planck_rel,
                     "solid_tensor_mass_term_witness": -mu * v**4},
        "checks": checks, "decision": decision,
        "classification": "theory_only;tensor_sector_quadratic_action_and_boundary_bookkeeping_exact;bps_warp_reproduces_charter_M4;tensor_DtN_numerical_witness;vector_scalar_sectors_spectrum_constraints_characteristics_not_done;N2_N7_C2_C10_P2_P3_P4_B4_B5_fail_closed",
        "evidence_boundary": [
            "Numerical parts are witnesses at the frozen point, not proofs; tolerances are recorded.",
            "The DtN is computed for spacelike momenta with the decaying bulk solution; timelike momenta need outgoing conditions.",
            "The assembled operator uses the v1 tensor block by its printed formula (xi=1 at the frozen point); vector and scalar sectors, where the khronon, solid and radion mix, are not assembled.",
            "No spectrum, mass, or stability statement is made; the induced Planck mass and solid term are read-offs of the operator, not predictions.",
        ],
        "provenance": {"generator": Path(__file__).name, "generator_sha256": _sha256(Path(__file__)), "sympy": sp.__version__, "numpy": np.__version__,
                       "python": platform.python_version(), "timings_s": {k2: round(v2, 1) for k2, v2 in log.items()},
                       "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
    }
    payload["calculation_digest"] = _canonical_digest({k2: payload[k2] for k2 in DIGEST_KEYS})
    return payload


def main() -> int:
    payload = derive()
    _write(OUTPUT, payload)
    print(json.dumps({"checks": payload["checks"], "M4": [payload["numerics"]["M4_squared_numeric"], payload["numerics"]["M4_squared_charter"]],
                      "timings_s": payload["provenance"]["timings_s"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
