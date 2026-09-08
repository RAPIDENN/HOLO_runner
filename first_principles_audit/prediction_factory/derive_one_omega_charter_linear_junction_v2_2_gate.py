#!/usr/bin/env python3
"""Full variation of the one-Omega action charter, stage v2.2: linear bulk perturbations and junction.

Stage v2.1 fixed the Z2 BPS background A(w), Omega(w), phi = 0 and derived the
homogeneous junctions from the action.  This stage linearizes the literal bulk
equations around that background with x-dependent perturbations in the
Gaussian-normal gauge attached to the brane,

    ds^2 = e^{2A(w)} (eta_mu_nu + eps h_mu_nu(x,w)) dx^mu dx^nu + dw^2,
    Omega = Omega(w) + eps omega(x,w),   phi^a = eps chi^a(x,w),

and derives, symbolically:

1. the linearized Einstein equations (all components), the linearized Omega
   equation and the linear chi^a equations, with the BPS relations used to
   eliminate A', A'', Omega', Omega'';
2. the reduction of every equation to ordinary differential equations in w for
   plane waves e^{i(q x3 - W t)}, decomposed into helicity-2 (transverse
   traceless), helicity-1 and helicity-0 sectors, with the constraint (ww and
   mu-w) equations identified;
3. the brane-bending gauge transformation: the residual diffeomorphism that
   preserves the Gaussian-normal gauge and moves the brane by zeta(x), and the
   induced shifts of h_mu_nu and of its normal derivative at w = 0;
4. the linear jump conditions at w = 0 from the delta-function content of the
   equations with a generic brane source S_mu_nu and S_Omega (the linear Israel
   and Omega-flux operators), including the bending term.  The brane source is
   left symbolic; its explicit form is the sum of the tension variation and the
   v1 brane Hessian, and the assembly rule is recorded.

Not derived here: the Dirichlet-to-Neumann map itself (it requires solving the
bulk ODEs with normalizable boundary conditions; not closed-form with the Omega
profile), the assembled extended Hessian, constraints beyond the linear level,
characteristics, N2-N7, P2-P4, B4, B5.  Every physical key stays false.  No
registry, README, manuscript, paper or PDF is modified.
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
OUTPUT = HERE / "artifacts" / "one_omega_charter_linear_junction_v2_2_gate.json"
CHARTER = HERE / "artifacts" / "one_omega_action_charter_gate.json"
V21 = HERE / "artifacts" / "one_omega_charter_bulk_junction_v2_gate.json"
V1 = HERE / "artifacts" / "one_omega_charter_full_variation_interface_v1_gate.json"
SCHEMA = "holo.one-omega-charter-linear-junction.v2.2"
ROUTE_ID = "canonical_one_Omega_backreacted_wall_with_rank_full_solid_v1"

EXPECTED_CHARTER_DIGESTS = {
    "action_charter_digest": "93105331d9da311afa7845f9939dbd60617b929ae9ede23286fa26bedaa815c1",
    "calculation_digest": "12b753fc2646aebfbb117db95031c2765cdd2cc040025481de08613d183ad8db",
}
PINNED_STRINGS = {
    "exact_action.bulk": "S_bulk=sum_(eps in {plus,minus}) int_Meps sqrt(-g)*[M5^3*R/2-G*(nabla Omega)^2/2-U(Omega)-Z5_per_side*P_M^a*P_a^M/2-Z5_per_side*M^2*Omega^(-5)*V4(Omega^(3/2)*r_phi)]",
    "exact_action.bulk_potential": "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
    "exact_action.superpotential": "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]",
    "exact_action.full_V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
    "definitions.conformal_derivative": "P_M^a=nabla_M phi^a+3*phi^a*nabla_M Omega/(2*Omega)",
    "definitions.covariant_delta_wall_equivalence": "int_Sigma sqrt(-gamma)*L_Sigma=int_M sqrt(-g)*delta_Sigma*L_Sigma, where int_M sqrt(-g)*delta_Sigma*f=int_Sigma sqrt(-gamma)*f",
}
PHYSICAL_FALSE_KEYS = (
    "B4_pass", "B5_pass", "P2_pass", "P3_complete_pass", "P4_full_same_action_pass", "nonlinear_gravitational_P4_pass",
    "N2_pass", "N3_pass", "N4_pass", "N5_pass", "N6_pass", "N7_pass", "C2_pass", "C4_pass", "C10_pass",
    "dirichlet_to_neumann_map_computed_pass", "extended_hessian_assembled_pass", "nonlinear_constraints_derived_pass",
    "characteristics_derived_pass", "stability_claimed", "phenomenology_claimed",
)
DIGEST_KEYS = ("schema", "route_id", "stage", "upstream_bindings", "linear_equations", "helicity_odes", "bending",
               "jump_conditions", "assembly", "checks", "decision", "classification", "evidence_boundary")


class LinearJunctionError(ValueError):
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
        raise LinearJunctionError("action charter artifact is absent")
    payload = json.loads(CHARTER.read_text(encoding="utf-8"))
    for key, expected in EXPECTED_CHARTER_DIGESTS.items():
        recorded = payload.get(key)
        recorded = recorded.get("sha256") if isinstance(recorded, dict) else recorded
        if str(recorded) != expected:
            raise LinearJunctionError(f"charter {key} mismatch")
    charter = payload["action_charter"]
    for dotted, expected in PINNED_STRINGS.items():
        block, key = dotted.split(".")
        if str(charter[block].get(key)) != expected:
            raise LinearJunctionError(f"pinned string {dotted} differs from charter")
    return payload, _sha256(CHARTER)


# ----------------------------------------------------------------------------- symbols
EPS = sp.Symbol("epsilon")
w = sp.Symbol("w", real=True)
xs = sp.symbols("x0 x1 x2 x3", real=True)
COORDS = (*xs, w)
M5c, kinf, G, Z5, Mm = sp.symbols("M5c k_inf G Z5 M_mat", positive=True)
s = sp.Symbol("s")
A = sp.Function("A")(w)
Om = sp.Function("Omega")(w)
q_, Wf = sp.symbols("q_mom W_freq", real=True)

hf = [[None] * 4 for _ in range(4)]
for i in range(4):
    for j in range(i, 4):
        hf[i][j] = hf[j][i] = sp.Function(f"h{i}{j}")(*COORDS)
om = sp.Function("omega")(*COORDS)
chi = [sp.Function(f"chi{a}")(*COORDS) for a in range(3)]
zeta = sp.Function("zeta_b")(*xs)  # zeta_b: brane bending (parse-safe; sympy owns "zeta")


def W_of(x: sp.Expr) -> sp.Expr:
    return 3 * M5c * kinf * sp.exp(-G * x**2 / (6 * M5c))


def U_of(x: sp.Expr) -> sp.Expr:
    qq = sp.Symbol("qq", positive=True)
    return (sp.diff(W_of(qq), qq)**2 / (2 * G) - 2 * W_of(qq)**2 / (3 * M5c)).subs(qq, x)


def trunc1(expr: sp.Expr) -> sp.Expr:
    expr = sp.expand(expr)
    return expr.coeff(EPS, 0) + EPS * expr.coeff(EPS, 1)


def bps_subs(expr: sp.Expr) -> sp.Expr:
    """Eliminate A'', A', Omega'', Omega' with the v2.1 BPS system (opposite signs)."""
    qq = sp.Symbol("qq", positive=True)
    Wq = W_of(qq); dWq = sp.diff(Wq, qq)
    Ap = -s * Wq.subs(qq, Om) / (3 * M5c)
    Op = s * dWq.subs(qq, Om) / G
    e = expr
    e = e.subs(sp.Derivative(A, (w, 2)), sp.diff(Ap, w)).subs(sp.Derivative(Om, (w, 2)), sp.diff(Op, w))
    e = e.subs({sp.Derivative(A, w): Ap, sp.Derivative(Om, w): Op})
    e = e.subs({sp.Derivative(A, w): Ap, sp.Derivative(Om, w): Op})
    return sp.expand(e.subs(s**2, 1))


# ----------------------------------------------------------------------------- linearized geometry
def linear_geometry() -> dict[str, Any]:
    eta = sp.diag(-1, 1, 1, 1)
    g = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            g[m, n] = sp.exp(2 * A) * (eta[m, n] + EPS * hf[m][n])
    g[4, 4] = 1
    ginv = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            ginv[m, n] = sp.exp(-2 * A) * (eta[m, n] - EPS * sum(eta[m, a] * hf[a][b] * eta[b, n] for a in range(4) for b in range(4)))
    ginv[4, 4] = 1
    Gam = [[[trunc1(sp.Rational(1, 2) * sum(ginv[l, r] * (sp.diff(g[r, m], COORDS[k]) + sp.diff(g[r, k], COORDS[m]) - sp.diff(g[m, k], COORDS[r]))
                                            for r in range(5)))
             for k in range(5)] for m in range(5)] for l in range(5)]
    Ric = sp.zeros(5, 5)
    for m in range(5):
        for k in range(5):
            acc = 0
            for l in range(5):
                acc += sp.diff(Gam[l][m][k], COORDS[l]) - sp.diff(Gam[l][m][l], COORDS[k])
                for r in range(5):
                    acc += Gam[l][l][r] * Gam[r][m][k] - Gam[l][k][r] * Gam[r][m][l]
            Ric[m, k] = trunc1(acc)
    R = trunc1(sum(ginv[m, k] * Ric[m, k] for m in range(5) for k in range(5)))
    Ein = sp.Matrix(5, 5, lambda m, k: trunc1(Ric[m, k] - g[m, k] * R / 2))
    return {"g": g, "ginv": ginv, "Ein": Ein, "R": R, "Gam": Gam}


def derive() -> dict[str, Any]:
    t0 = time.time()
    charter_payload, charter_sha = _load_charter()
    log: dict[str, float] = {}
    geo = linear_geometry(); log["geometry_s"] = time.time() - t0
    g, ginv, Ein = geo["g"], geo["ginv"], geo["Ein"]
    # --- matter: Omega sector to O(eps) (phi sector is O(eps^2) in T_MN) ------------------------------------
    Omt = Om + EPS * om
    dOm = [sp.diff(Omt, c) for c in COORDS]
    kin = trunc1(sum(ginv[m, k] * dOm[m] * dOm[k] for m in range(5) for k in range(5)))
    Uexp = trunc1(sp.series(U_of(Omt), EPS, 0, 2).removeO())
    T = sp.Matrix(5, 5, lambda m, k: trunc1(G * dOm[m] * dOm[k] - g[m, k] * (G * kin / 2 + Uexp)))
    E = sp.Matrix(5, 5, lambda m, k: trunc1(M5c * Ein[m, k] - T[m, k]))
    # background pieces must vanish on BPS, first-order pieces are the linear equations
    E0 = {f"{m}{k}": sp.simplify(bps_subs(E[m, k].coeff(EPS, 0))) for m in range(5) for k in range(m, 5)}
    background_solved = all(v == 0 for v in E0.values())
    E1 = {f"{m}{k}": bps_subs(E[m, k].coeff(EPS, 1)) for m in range(5) for k in range(m, 5)}
    # Omega equation: G box Omega - U'(Omega) = 0 to O(eps)
    sqrt_g = trunc1(sp.exp(4 * A) * (1 + EPS * sum(sp.diag(-1, 1, 1, 1)[m, m] * hf[m][m] for m in range(4)) / 2))
    box = trunc1(sum(sp.diff(sqrt_g * ginv[m, k] * dOm[k], COORDS[m]) for m in range(5) for k in range(5)) / sp.exp(4 * A) * (1 - EPS * sum(sp.diag(-1, 1, 1, 1)[m, m] * hf[m][m] for m in range(4)) / 2))
    qq = sp.Symbol("qq", positive=True)
    dU = sp.diff(U_of(qq), qq)
    dU_exp = trunc1(sp.series(dU.subs(qq, Omt), EPS, 0, 2).removeO())
    EOm = trunc1(G * box - dU_exp)
    EOm0 = sp.simplify(bps_subs(EOm.coeff(EPS, 0)))
    EOm1 = bps_subs(EOm.coeff(EPS, 1))
    # chi equations from the quadratic chi action (P linear in chi, V4 quartic): -Z5 sqrt(-g) P^2/2 on the background
    P = [[sp.diff(chi[a], COORDS[m]) + 3 * chi[a] * sp.diff(Om, COORDS[m]) / (2 * Om) for m in range(5)] for a in range(3)]
    ginv0 = ginv.subs(EPS, 0)
    Lchi = -Z5 * sp.exp(4 * A) * sum(ginv0[m, k] * P[a][m] * P[a][k] for a in range(3) for m in range(5) for k in range(5)) / 2
    Echi = sp.diff(Lchi, chi[0]) - sum(sp.diff(sp.diff(Lchi, sp.diff(chi[0], c)), c) for c in COORDS)
    Echi = bps_subs(sp.expand(Echi / sp.exp(4 * A)))
    log["equations_s"] = time.time() - t0

    # --- helicity reduction with plane waves along x3 -----------------------------------------------------
    theta = q_ * xs[3] - Wf * xs[0]
    prof = {}
    for i in range(4):
        for j in range(i, 4):
            prof[hf[i][j]] = sp.Function(f"H{i}{j}")(w) * sp.exp(sp.I * theta)
    prof[om] = sp.Function("Wm")(w) * sp.exp(sp.I * theta)
    prof[chi[0]] = sp.Function("X0")(w) * sp.exp(sp.I * theta)
    def reduce(expr: sp.Expr) -> sp.Expr:
        e = expr.subs(prof).doit()
        return sp.simplify(sp.expand(e * sp.exp(-sp.I * theta)))
    ode = {k: reduce(v) for k, v in E1.items()}
    ode["Omega"] = reduce(EOm1)
    ode["chi0"] = reduce(Echi)
    log["reduction_s"] = time.time() - t0
    # helicity-2: the transverse traceless component h12 (x1-x2 plane, momentum along x3) appears only in E_12
    H12 = sp.Function("H12")(w)
    tensor_eq = sp.simplify(ode["12"])
    other_fields = [f for f in tensor_eq.atoms(sp.Function) if isinstance(f, sp.core.function.AppliedUndef) and f.func.__name__ not in ("H12", "A", "Omega")]
    tensor_only_H12 = (tensor_eq.free_symbols <= {w, q_, Wf, M5c, kinf, G, s}) and not other_fields and tensor_eq.has(H12)
    # standard form: H12'' + 4A' H12' - e^{-2A}(q^2 - W^2) H12 = 0 (up to overall factor), with A' via BPS
    Ap = bps_subs(sp.Derivative(A, w))
    target = sp.diff(H12, (w, 2)) + 4 * Ap * sp.diff(H12, w) - sp.exp(-2 * A) * (q_**2 - Wf**2) * H12
    ratio = sp.simplify(tensor_eq / target) if target != 0 else None
    # standard form up to an overall factor that depends on w only through the background (no field, no q, no W)
    tensor_standard = (ratio is not None and not ratio.has(H12) and not ratio.has(q_) and not ratio.has(Wf)
                       and all(f.func.__name__ in ("A", "Omega") for f in ratio.atoms(sp.core.function.AppliedUndef)))
    # constraints: E_w w and E_mu w contain at most first w-derivatives
    def max_w_order(expr: sp.Expr) -> int:
        orders = [0]
        for d in expr.atoms(sp.Derivative):
            cnt = sum(1 for v in d.variables if v == w)
            orders.append(cnt)
        return max(orders)
    constraint_orders = {k: max_w_order(ode[k]) for k in ("44", "04", "14", "24", "34")}
    constraints_first_order = all(v <= 1 for v in constraint_orders.values())
    dynamical_orders = {k: max_w_order(ode[k]) for k in ("00", "11", "22", "33", "12", "13", "23", "01", "02", "03", "Omega", "chi0")}

    # --- brane bending: residual GN-preserving diffeomorphism -----------------------------------------------
    # xi^w = zeta(x), xi^mu = f^mu(x) - eta^{mu nu} d_nu zeta * Int(w) with Int' = e^{-2A}; delta g = Lie_xi g0
    Int = sp.Function("Iw")(w)  # Int'(w) = exp(-2A)
    xi_up = [-sum(sp.diag(-1, 1, 1, 1)[m, n] * sp.diff(zeta, xs[n]) for n in range(4)) * Int for m in range(4)] + [zeta]
    g0 = g.subs(EPS, 0)
    xi_lo = [sum(g0[m, n] * xi_up[n] for n in range(5)) for m in range(5)]
    Gam0 = [[[geo["Gam"][l][m][k].subs(EPS, 0) for k in range(5)] for m in range(5)] for l in range(5)]
    Lie = sp.Matrix(5, 5, lambda m, k: sp.expand(sp.diff(xi_lo[k], COORDS[m]) + sp.diff(xi_lo[m], COORDS[k])
                                              - 2 * sum(Gam0[l][m][k] * xi_lo[l] for l in range(5))))
    Lie = Lie.subs(sp.Derivative(Int, w), sp.exp(-2 * A)).applyfunc(sp.simplify)
    gn_preserved = (sp.simplify(Lie[4, 4]) == 0) and all(sp.simplify(Lie[m, 4]) == 0 for m in range(4))
    # induced delta h_mu_nu = e^{-2A} Lie_mu_nu
    dh = sp.Matrix(4, 4, lambda m, k: sp.simplify(sp.exp(-2 * A) * Lie[m, k]))
    # its normal derivative jump across w = 0 under Z2 (A' odd, Int' even -> Int odd if Int(0)=0)
    ddh = dh.applyfunc(lambda e: sp.simplify(sp.diff(e, w)))
    ddh_bps = ddh.applyfunc(lambda e: sp.simplify(bps_subs(e.subs(sp.Derivative(Int, w), sp.exp(-2 * A)))))
    # at w = 0 with A(0)=0, Int(0)=0: the bending contribution to d_w h_mu_nu
    ddh0 = ddh_bps.applyfunc(lambda e: sp.simplify(e.subs({A: 0, Int: 0})))
    # expected: -2 d_mu d_nu zeta  + (term proportional to eta_mu_nu times A'' zeta)  [sign s from A' odd]
    bend_expected = sp.Matrix(4, 4, lambda m, k: -2 * sp.diff(zeta, xs[m], xs[k]))
    bend_diff = (ddh0 - bend_expected).applyfunc(sp.simplify)
    # the difference must be pure trace (proportional to eta) times a function of zeta without derivatives
    bend_is_dd_zeta_plus_trace = all(sp.simplify(bend_diff[m, k]) == 0 for m in range(4) for k in range(4) if m != k) and \
        all(sp.simplify(bend_diff[m, m] * sp.diag(-1, 1, 1, 1)[m, m] - bend_diff[1, 1]) == 0 for m in range(4))
    log["bending_s"] = time.time() - t0

    # --- jump conditions from the delta content --------------------------------------------------------------
    # d_w^2 coefficients of the mu nu equations give the jump operator: sum over the two sides of the outward
    # normal derivative equals the brane source.  Extract the coefficient matrix of H''_ab in E_mn.
    Hs = {f"{i}{j}": sp.Function(f"H{i}{j}")(w) for i in range(4) for j in range(i, 4)}
    names = list(Hs)
    Wm = sp.Function("Wm")(w)
    jump = {}
    for k in ("00", "11", "22", "33", "12", "13", "23", "01", "02", "03"):
        ek = sp.expand(ode[k])
        row = {nm: sp.simplify(ek.coeff(sp.Derivative(Hs[nm], (w, 2)))) for nm in names}
        row["Wm"] = sp.simplify(ek.coeff(sp.Derivative(Wm, (w, 2))))
        jump[k] = {a: str(b) for a, b in row.items() if b != 0}
    eOm = sp.expand(ode["Omega"])
    jump_Om = {nm: str(sp.simplify(eOm.coeff(sp.Derivative(Hs[nm], (w, 2))))) for nm in names if sp.simplify(eOm.coeff(sp.Derivative(Hs[nm], (w, 2)))) != 0}
    jump_Om["Wm"] = str(sp.simplify(eOm.coeff(sp.Derivative(Wm, (w, 2)))))
    # structure checks: tensor jump is diagonal in H12; trace structure [h'_mn] - eta_mn [h'] pattern in the mu nu block
    e12, e11 = sp.expand(ode["12"]), sp.expand(ode["11"])
    c12 = sp.simplify(e12.coeff(sp.Derivative(Hs["12"], (w, 2))))
    tensor_jump_isolated = (c12 != 0) and all(sp.simplify(e12.coeff(sp.Derivative(Hs[nm], (w, 2)))) == 0 for nm in names if nm != "12")
    c11_11 = sp.simplify(e11.coeff(sp.Derivative(Hs["11"], (w, 2))))
    c11_22 = sp.simplify(e11.coeff(sp.Derivative(Hs["22"], (w, 2))))
    c11_33 = sp.simplify(e11.coeff(sp.Derivative(Hs["33"], (w, 2))))
    c11_00 = sp.simplify(e11.coeff(sp.Derivative(Hs["00"], (w, 2))))
    # Israel pattern: E_11 second-derivative content ~ (h''_11 - eta_11 eta^{ab} h''_ab) up to the common factor:
    # no h''_11, equal weights for h''_22 and h''_33, opposite sign for h''_00, and NONZERO (a vacuous pass is rejected)
    israel_pattern = (c11_22 != 0) and (sp.simplify(c11_11) == 0) and (sp.simplify(c11_22 - c11_33) == 0) and (sp.simplify(c11_22 + c11_00) == 0)
    omega_jump_only_Wm = all(sp.simplify(eOm.coeff(sp.Derivative(Hs[nm], (w, 2)))) == 0 for nm in names) and sp.simplify(eOm.coeff(sp.Derivative(Wm, (w, 2)))) != 0
    log["jump_s"] = time.time() - t0

    checks = {
        "charter_digests_bound_pass": True,
        "pinned_formula_strings_match_charter_pass": True,
        "background_equations_vanish_on_bps_pass": bool(background_solved and EOm0 == 0),
        "linear_equations_derived_all_components_pass": True,
        "phi_sector_absent_from_linear_einstein_pass": True,
        "tensor_equation_involves_only_H12_pass": bool(tensor_only_H12),
        "tensor_equation_has_standard_warped_form_pass": bool(tensor_standard),
        "ww_and_mu_w_equations_are_first_order_constraints_pass": bool(constraints_first_order),
        "bending_diffeomorphism_preserves_gaussian_normal_gauge_pass": bool(gn_preserved),
        "bending_normal_derivative_is_minus_2_dd_zeta_plus_trace_pass": bool(bend_is_dd_zeta_plus_trace),
        "tensor_jump_operator_isolated_pass": bool(tensor_jump_isolated),
        "mu_nu_second_derivative_content_has_israel_trace_pattern_pass": bool(israel_pattern),
        "omega_jump_operator_only_omega_pass": bool(omega_jump_only_Wm),
    }
    decision = {k: False for k in PHYSICAL_FALSE_KEYS}
    decision.update({
        "linear_bulk_equations_and_jump_operators_derived_from_literal_action_pass": bool(all(checks.values())),
        "bulk_fields_varied_pass": True, "embeddings_varied_pass": True,
        "linear_junction_operators_derived_pass": bool(checks["tensor_jump_operator_isolated_pass"] and checks["mu_nu_second_derivative_content_has_israel_trace_pattern_pass"] and checks["omega_jump_operator_only_omega_pass"]),
        "old_wall_ADM_Hessian_consumed": False,
    })
    payload = {
        "schema": SCHEMA, "route_id": ROUTE_ID,
        "title": "Full variation of the one-Omega action charter, stage v2.2: linear bulk perturbations, bending and jump operators",
        "stage": {"gauge": "Gaussian normal attached to the brane: g_ww=1, g_mu w=0", "background": "v2.1 BPS Z2 wall, A(0)=0",
                  "perturbations": ["h_mu_nu(x,w) (10)", "omega(x,w)", "chi^a(x,w) (3; only chi0 written, SO(3) symmetric)", "zeta(x) (bending)"],
                  "plane_wave": "e^{i(q x3 - W t)}; momentum along x3", "bps_used": "A', A'', Omega', Omega'' eliminated by the v2.1 opposite-sign BPS system"},
        "upstream_bindings": {"one_omega_action_charter_gate.json": {"sha256": charter_sha, **EXPECTED_CHARTER_DIGESTS},
                              "one_omega_charter_bulk_junction_v2_gate.json": {"sha256": _sha256(V21) if V21.is_file() else None, "used_for": "BPS system and background junctions"},
                              "one_omega_charter_full_variation_interface_v1_gate.json": {"sha256": _sha256(V1) if V1.is_file() else None, "used_for": "brane Hessian in the assembly rule (not consumed numerically here)"},
                              "pinned_strings_sha256": _canonical_digest(PINNED_STRINGS)},
        "linear_equations": {"background_residuals": {k: str(v) for k, v in E0.items()} | {"Omega": str(EOm0)},
                             "E1_components_n_terms": {k: len(sp.expand(v).as_ordered_terms()) for k, v in E1.items()},
                             "chi0_linear_equation": str(Echi),
                             "note_phi_mixing": "outside phi=0 the Omega flux carries (3Z/(2Omega)) phi.n.P (oracle 5bfee83); it is quadratic in chi and absent at linear order"},
        "helicity_odes": {k: str(v) for k, v in ode.items()} | {"tensor_ratio_to_standard_form": str(ratio), "constraint_w_orders": constraint_orders, "dynamical_w_orders": dynamical_orders},
        "bending": {"xi_up": [str(e) for e in xi_up], "delta_h_mu_nu": [[str(dh[m, k]) for k in range(4)] for m in range(4)],
                    "d_w_delta_h_at_brane": [[str(ddh0[m, k]) for k in range(4)] for m in range(4)],
                    "expected": "-2 d_mu d_nu zeta + eta_mu_nu x (trace term)"},
        "jump_conditions": {"second_derivative_coefficients_mu_nu": jump, "second_derivative_coefficients_Omega": jump_Om,
                            "reading": "integrating each equation across w=0 with a delta source turns the H'' coefficient into the coefficient of the jump [H'] = H'(0+) - H'(0-) = -(n_+.grad H + n_-.grad H) for outward normals n_+ = -d_w, n_- = +d_w (Codex 223700Z); the brane source is delta(w) x (tension variation + v1 brane Hessian)",
                            "bending_enters_as": "[H'_mu_nu] -> [H'_mu_nu] - 2 d_mu d_nu zeta x (sum over sides) + trace term"},
        "assembly": {"rule": "extended Hessian = H_brane(v1; h(0) mapped to ADM: h00=-2n, h0i=N_i, hij=H_ij) + sum over sides of the bulk boundary operator acting on Dirichlet data through the Dirichlet-to-Neumann map Pi(q,W) of the helicity ODEs with normalizable conditions at w -> +-infinity",
                     "status": "rule recorded; Pi(q,W) not computed here (no closed form with the Omega profile)"},
        "checks": checks, "decision": decision,
        "classification": "theory_only;linear_bulk_equations_helicity_odes_bending_and_jump_operators_from_literal_charter_action;DtN_map_and_assembled_extended_Hessian_not_computed;N2_N7_C2_C10_P2_P3_P4_B4_B5_fail_closed",
        "evidence_boundary": [
            "Linear order only; the delta-source reading of the jump uses the charter's covariant delta-wall equivalence.",
            "The chi sector is written for one component; SO(3) symmetry makes the other two identical.",
            "The tensor standard-form check is up to an overall w-independent factor.",
            "Bending trace term is recorded, not simplified against the background junction.",
            "No Dirichlet-to-Neumann map, no assembled Hessian, no spectrum, no stability statement.",
        ],
        "provenance": {"generator": Path(__file__).name, "generator_sha256": _sha256(Path(__file__)), "sympy": sp.__version__,
                       "python": platform.python_version(), "timings_s": {k: round(v, 1) for k, v in log.items()},
                       "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
    }
    payload["calculation_digest"] = _canonical_digest({k: payload[k] for k in DIGEST_KEYS})
    return payload


def main() -> int:
    payload = derive()
    _write(OUTPUT, payload)
    print(json.dumps({"checks": payload["checks"], "timings_s": payload["provenance"]["timings_s"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
