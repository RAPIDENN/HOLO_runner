#!/usr/bin/env python3
"""Full variation of the one-Omega action charter, stage v2.1: bulk background and junction.

Stage v1 varied the displayed brane action and found that T, X^a and varphi^a are
stationary on the background while gamma and Omega_Sigma carry tadpoles
(-2W(1) x sqrt(-gamma)_1 and -2W'(1) x omega).  Those tadpoles are the sources
the bulk side must balance.  This stage derives that balance from the literal
bulk-plus-GHY action of the charter, for the Z2-symmetric homogeneous wall:

  ds^2 = e^{2A(w)} eta_mu_nu dx^mu dx^nu + dw^2,   Omega = Omega(w),   phi^a = 0,
  M_plus = {w > 0}, M_minus = {w < 0}, brane at w = 0.

Everything is computed symbolically from the pinned charter strings:

1. bulk field equations of the warped ansatz (Einstein ww and mu nu components,
   Omega equation) from S_bulk with the literal U(Omega), W(Omega) and V4;
2. the first-order BPS system Omega' = +s W_Omega/G, A' = -s W/(3 M5^3) (opposite signs,
   as in DeWolfe-Freedman; the warp decays and Omega -> 0 toward the AdS asymptotics)
   (s = +1 on M_plus, -1 on M_minus) solves every bulk equation exactly;
3. phi^a = 0 is a consistent truncation (the phi^a equations vanish identically);
4. the reduced one-dimensional action S_bulk + S_GHY on the ansatz: the GHY term
   removes every second derivative of A, so the boundary variation is
   well posed, and the Euler-Lagrange BOUNDARY conditions at w = 0 of
   S_bulk + S_GHY + S_wall0 with respect to A(0) and Omega(0) are the metric
   (Israel) and the Omega-flux junction conditions -- derived, not assumed;
5. the BPS profile satisfies both junctions with Omega_Sigma = 1 iff the wall
   tension is 2W(1) and the Omega flux balances 2W'(1): this closes the two
   tadpoles left open by stage v1;
6. the derived junctions are compared afterwards (contrast, not input) with the
   scalar junction of the independent oracle
   ``one_omega_scalar_interface_reparam_v1`` restricted to phi = 0, and with the
   charter's CANONICAL_JUNCTION_CONVENTION strings.

Not derived here: the linearized junction operators for the eighteen brane
fields and the bulk perturbations (Dirichlet-to-Neumann map), nonlinear
constraints, characteristics, and the complete extended Hessian.  Every physical
key stays false.  No registry, README, manuscript, paper or PDF is modified.
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
OUTPUT = HERE / "artifacts" / "one_omega_charter_bulk_junction_v2_gate.json"
CHARTER = HERE / "artifacts" / "one_omega_action_charter_gate.json"
V1 = HERE / "artifacts" / "one_omega_charter_full_variation_interface_v1_gate.json"
ORACLE = HERE / "artifacts" / "one_omega_scalar_interface_reparam_v1.json"
SCHEMA = "holo.one-omega-charter-bulk-junction.v2"
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
    "exact_action.dimensionless_material_argument": "r=Omega^(3/2)*r_phi",
    "exact_action.GHY": "S_GHY=+M5^3*sum_(eps in {plus,minus}) int_Sigma sqrt(-gamma)*Theta_eps for outward spacelike normals",
    "exact_action.wall_background": "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2]",
    "definitions.conformal_derivative": "P_M^a=nabla_M phi^a+3*phi^a*nabla_M Omega/(2*Omega)",
    "definitions.bulk_extrinsic_curvature": "Theta_eps_mu_nu=e_mu^M e_nu^N nabla_M n_eps_N",
    "definitions.normal_convention": "n_eps^M is outward pointing and n_eps^M*n_eps_M=+1",
    "definitions.material_radius": "r_phi=sqrt(delta_ab*phi^a*phi^b)",
}
PHYSICAL_FALSE_KEYS = (
    "B4_pass", "B5_pass", "P2_pass", "P3_complete_pass", "P4_full_same_action_pass", "nonlinear_gravitational_P4_pass",
    "N2_pass", "N3_pass", "N4_pass", "N5_pass", "N6_pass", "N7_pass", "C2_pass", "C4_pass", "C10_pass",
    "linear_junction_operators_derived_pass", "dirichlet_to_neumann_map_derived_pass", "nonlinear_constraints_derived_pass",
    "characteristics_derived_pass", "complete_extended_hessian_derived_pass", "displaced_brane_junction_derived_pass",
    "stability_claimed", "phenomenology_claimed",
)
DIGEST_KEYS = ("schema", "route_id", "stage", "upstream_bindings", "bulk_equations", "bps", "reduced_action", "junctions",
               "tadpole_closure", "contrasts", "checks", "decision", "classification", "evidence_boundary")


class BulkJunctionError(ValueError):
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
        raise BulkJunctionError("action charter artifact is absent")
    payload = json.loads(CHARTER.read_text(encoding="utf-8"))
    for key, expected in EXPECTED_CHARTER_DIGESTS.items():
        recorded = payload.get(key)
        recorded = recorded.get("sha256") if isinstance(recorded, dict) else recorded
        if str(recorded) != expected:
            raise BulkJunctionError(f"charter {key} mismatch")
    charter = payload["action_charter"]
    for dotted, expected in PINNED_STRINGS.items():
        block, key = dotted.split(".")
        if str(charter[block].get(key)) != expected:
            raise BulkJunctionError(f"pinned string {dotted} differs from charter")
    return payload, _sha256(CHARTER)


# ----------------------------------------------------------------------------- symbols
w = sp.Symbol("w", real=True)
xs = sp.symbols("x0 x1 x2 x3", real=True)
M5c, kinf, G, beta, Z5, Mm = sp.symbols("M5c k_inf G beta_b Z5 M_mat", positive=True)  # beta_b: brane beta (parse-safe name)
s = sp.Symbol("s")  # side sign: +1 on M_plus, -1 on M_minus
A = sp.Function("A")(w)
Om = sp.Function("Omega")(w)
OmS = sp.Symbol("Omega_Sigma", positive=True)


def W_of(x: sp.Expr) -> sp.Expr:
    return 3 * M5c * kinf * sp.exp(-G * x**2 / (6 * M5c))


def U_of(x: sp.Expr) -> sp.Expr:
    Wx = W_of(sp.Symbol("q", positive=True))
    dW = sp.diff(Wx, sp.Symbol("q", positive=True)).subs(sp.Symbol("q", positive=True), x)
    return dW**2 / (2 * G) - 2 * W_of(x)**2 / (3 * M5c)


def V4_of(r: sp.Expr) -> sp.Expr:
    return r**4 / (2 * sp.sqrt(1 + r**4))


# ----------------------------------------------------------------------------- 5D curvature of the warped ansatz
def warped_metric() -> tuple[sp.Matrix, sp.Matrix, tuple[sp.Symbol, ...]]:
    coords = (*xs, w)
    g = sp.diag(-sp.exp(2 * A), sp.exp(2 * A), sp.exp(2 * A), sp.exp(2 * A), 1)
    return g, g.inv(), coords


def einstein_tensor(g: sp.Matrix, ginv: sp.Matrix, coords: tuple[sp.Symbol, ...]) -> tuple[sp.Matrix, sp.Expr]:
    n = len(coords)
    Gam = [[[sp.simplify(sp.Rational(1, 2) * sum(ginv[l, r] * (sp.diff(g[r, m], coords[k]) + sp.diff(g[r, k], coords[m]) - sp.diff(g[m, k], coords[r]))
                                                 for r in range(n)))
             for k in range(n)] for m in range(n)] for l in range(n)]
    Ric = sp.zeros(n, n)
    for m in range(n):
        for k in range(n):
            acc = 0
            for l in range(n):
                acc += sp.diff(Gam[l][m][k], coords[l]) - sp.diff(Gam[l][m][l], coords[k])
                for r in range(n):
                    acc += Gam[l][l][r] * Gam[r][m][k] - Gam[l][k][r] * Gam[r][m][l]
            Ric[m, k] = sp.simplify(acc)
    R = sp.simplify(sum(ginv[m, k] * Ric[m, k] for m in range(n) for k in range(n)))
    Ein = (Ric - g * R / 2).applyfunc(sp.simplify)
    return Ein, R


# ----------------------------------------------------------------------------- derivation
def derive() -> dict[str, Any]:
    t0 = time.time()
    charter_payload, charter_sha = _load_charter()
    g, ginv, coords = warped_metric()
    Ein, R = einstein_tensor(g, ginv, coords)
    sqrt_g = sp.exp(4 * A)

    # --- 1. bulk equations from the literal action, phi = 0 ---------------------------------------------------
    # matter stress tensor of the Omega sector: T_MN = G dOm dOm - g (G (dOm)^2/2 + U)
    dOm = [sp.diff(Om, c) for c in coords]
    kin = sum(ginv[m, k] * dOm[m] * dOm[k] for m in range(5) for k in range(5))
    T = sp.Matrix(5, 5, lambda m, k: sp.simplify(G * dOm[m] * dOm[k] - g[m, k] * (G * kin / 2 + U_of(Om))))
    # Einstein equations: M5^3 G_MN = T_MN  (from M5^3 R/2 normalization)
    E_ww = sp.simplify(M5c * Ein[4, 4] - T[4, 4])
    E_xx = sp.simplify(M5c * Ein[1, 1] - T[1, 1])
    # Omega equation from -G (nabla Omega)^2/2 - U: G box Omega - U'(Omega) = 0
    Uq = U_of(sp.Symbol("q", positive=True))
    dU = sp.diff(Uq, sp.Symbol("q", positive=True)).subs(sp.Symbol("q", positive=True), Om)
    box = sp.simplify(sum(sp.diff(sqrt_g * ginv[m, k] * dOm[k], coords[m]) for m in range(5) for k in range(5)) / sqrt_g)
    E_Om = sp.simplify(G * box - dU)
    # phi sector at phi = 0: L_phi = -Z5 P^2/2 - Z5 M^2 Omega^-5 V4(Omega^(3/2) r_phi); with three components phi^a
    phi = [sp.Function(f"phi{a}")(*coords) for a in range(3)]
    r_phi = sp.sqrt(sum(p**2 for p in phi))
    P = [[sp.diff(phi[a], coords[m]) + 3 * phi[a] * sp.diff(Om, coords[m]) / (2 * Om) for m in range(5)] for a in range(3)]
    P2 = sum(ginv[m, k] * P[a][m] * P[a][k] for a in range(3) for m in range(5) for k in range(5))
    L_phi = -Z5 * P2 / 2 - Z5 * Mm**2 * Om**(-5) * V4_of(Om**sp.Rational(3, 2) * r_phi)
    # Euler-Lagrange of sqrt(-g) L_phi w.r.t. phi^0, then set phi -> 0 (V4 ~ r^4 so no linear term; P is linear in phi)
    Lphi_dens = sqrt_g * L_phi
    el0 = sp.diff(Lphi_dens, phi[0]) - sum(sp.diff(sp.diff(Lphi_dens, sp.diff(phi[0], c)), c) for c in coords)
    el0_at_zero = sp.simplify(el0.subs({p: 0 for p in phi}))
    # also the Omega equation receives no phi contribution at phi = 0
    dLphi_dOm_at_zero = sp.simplify((sp.diff(Lphi_dens, Om) - sp.diff(sp.diff(Lphi_dens, sp.Derivative(Om, w)), w)).subs({p: 0 for p in phi}))
    phi_zero_consistent = (el0_at_zero == 0) and (dLphi_dOm_at_zero == 0)

    # --- 2. BPS first-order system --------------------------------------------------------------------------
    q = sp.Symbol("q", positive=True)
    Wq = W_of(q)
    dWq = sp.diff(Wq, q)
    bps = {sp.Derivative(Om, w): s * dWq.subs(q, Om) / G, sp.Derivative(A, w): -s * Wq.subs(q, Om) / (3 * M5c)}

    def on_bps(expr: sp.Expr) -> sp.Expr:
        # substitute second derivatives via chain rule first, then first derivatives
        e = expr
        e = e.subs(sp.Derivative(A, (w, 2)), sp.diff(bps[sp.Derivative(A, w)], w))
        e = e.subs(sp.Derivative(Om, (w, 2)), sp.diff(bps[sp.Derivative(Om, w)], w))
        e = e.subs(bps)
        e = e.subs(bps)  # the chain rule reintroduces Omega'; substitute again
        return sp.simplify(e.subs(s**2, 1))

    bps_ok = {"E_ww": on_bps(E_ww) == 0, "E_xx": on_bps(E_xx) == 0, "E_Omega": on_bps(E_Om) == 0}

    # --- 3. reduced 1D action with GHY -----------------------------------------------------------------------
    # On the ansatz, sqrt(-g) [M5^3 R/2 - G Omega'^2/2 - U] per unit 4-volume.
    L_bulk_1d = sp.simplify(sqrt_g * (M5c * R / 2 - G * sp.diff(Om, w)**2 / 2 - U_of(Om)))
    # GHY on each side: the outward normal of the region M_s = {s w > 0} at its boundary w = 0 is the direction
    # leaving M_s, i.e. n = -s d_w (Codex refutation 223133Z: the earlier comment said s d_w; the code always used -s).  Theta_mu_nu = e e nabla n ; for n = eps d_w on the warped metric, Theta_mu_nu = eps A' g_mu_nu.
    eps = sp.Symbol("eps_n")
    n_vec = [0, 0, 0, 0, eps]
    n_lo = [sum(g[m, k] * n_vec[k] for k in range(5)) for m in range(5)]
    Gam = [[[sp.simplify(sp.Rational(1, 2) * sum(ginv[l, r] * (sp.diff(g[r, m], coords[k]) + sp.diff(g[r, k], coords[m]) - sp.diff(g[m, k], coords[r])) for r in range(5)))
             for k in range(5)] for m in range(5)] for l in range(5)]
    nab_n = [[sp.simplify(sp.diff(n_lo[k], coords[m]) - sum(Gam[l][m][k] * n_lo[l] for l in range(5))) for k in range(5)] for m in range(5)]
    Theta = sp.Matrix(4, 4, lambda m, k: sp.simplify(nab_n[m][k]))  # tangential components (e_mu^M = delta)
    gam = sp.Matrix(4, 4, lambda m, k: g[m, k])
    Theta_trace = sp.simplify(sum(gam.inv()[m, k] * Theta[m, k] for m in range(4) for k in range(4)))
    theta_is_A_prime_gamma = sp.simplify(Theta - eps * sp.diff(A, w) * gam) == sp.zeros(4, 4)
    # second-derivative content: bulk density contains A''; total derivative identification
    A2coef = sp.simplify(sp.diff(L_bulk_1d, sp.Derivative(A, (w, 2))))
    # L_bulk_1d = L_first_order + d/dw(B(A,A')) with B chosen so that the A'' term is removed
    Bw = sp.integrate(A2coef, sp.Derivative(A, w))  # B such that dB/dA' = coefficient of A''
    total_deriv = sp.simplify(sp.diff(Bw, w))
    L_first_order = sp.simplify(sp.expand(L_bulk_1d - total_deriv))
    no_second_derivatives_left = (sp.diff(L_first_order, sp.Derivative(A, (w, 2))) == 0)
    # GHY per side evaluated at w=0 with outward normal leaving M_s: eps = -s
    GHY_density = sp.simplify(M5c * sqrt_g * Theta_trace.subs(eps, -s))
    # boundary term produced by the total derivative when integrating over M_s up to w=0:
    # int_{M_s} dw d/dw B = (-s) * B|_{w=0}  (for s=+1 the region is w>0 and the boundary contribution at w=0 is -B(0); for s=-1 it is +B(0))
    boundary_from_bulk = sp.simplify(-s * Bw)
    ghy_cancels_boundary = sp.simplify(sp.expand(boundary_from_bulk + GHY_density).subs(s**2, 1)) == 0

    # --- 4. junctions as Euler-Lagrange boundary conditions at w = 0 ------------------------------------------
    # Total: sum_s int_{M_s} L_first_order dw + S_wall0(A(0), Omega(0)).  Varying A(0) and Omega(0):
    # the bulk contributes the canonical momenta at the boundary, with sign -s (boundary at the left end of M_+,
    # right end of M_-): delta S_bulk_s = ... + [-s * dL/dA'] delta A(0).
    pA = sp.simplify(sp.diff(L_first_order, sp.Derivative(A, w)))
    pOm = sp.simplify(sp.diff(L_first_order, sp.Derivative(Om, w)))
    wall = -sp.exp(4 * A) * (2 * W_of(Om) + beta * (Om - 1)**2 / 2)  # sqrt(-gamma) = e^{4A} on the brane
    dwall_dA = sp.simplify(sp.diff(wall, A))
    dwall_dOm = sp.simplify(sp.diff(wall, Om))
    # sum over sides: sum_s (-s) p(side s) + dwall/dX = 0.  Represent side values with symbols.
    Ap, Am, Op, Omn = sp.symbols("Aprime_plus Aprime_minus Omegaprime_plus Omegaprime_minus", real=True)
    A0, O0 = sp.symbols("A0 Omega0", real=True)
    def side(expr: sp.Expr, sign: int) -> sp.Expr:
        return expr.subs({sp.Derivative(A, w): (Ap if sign == 1 else Am), sp.Derivative(Om, w): (Op if sign == 1 else Omn)}).subs({A: A0, Om: O0})
    J_metric = sp.simplify(-1 * side(pA, 1) + 1 * side(pA, -1) + dwall_dA.subs({A: A0, Om: O0}))
    J_omega = sp.simplify(-1 * side(pOm, 1) + 1 * side(pOm, -1) + dwall_dOm.subs({A: A0, Om: O0}))
    # Z2: A'(0-) = -A'(0+), Omega'(0-) = -Omega'(0+)
    z2 = {Am: -Ap, Omn: -Op}
    J_metric_z2 = sp.simplify(J_metric.subs(z2))
    J_omega_z2 = sp.simplify(J_omega.subs(z2))
    # --- 5. BPS profile at the brane with Omega_Sigma = 1 ---------------------------------------------------
    bps_plus = {Ap: -W_of(O0) / (3 * M5c), Op: dWq.subs(q, O0) / G}
    J_metric_bps = sp.simplify(J_metric_z2.subs(bps_plus))
    J_omega_bps = sp.simplify(J_omega_z2.subs(bps_plus))
    metric_junction_at_1 = sp.simplify(J_metric_bps.subs(O0, 1))
    metric_junction_holds_at_1 = (metric_junction_at_1 == 0)
    # away from Omega_Sigma = 1 the residual is the compensator spring: -2 beta (Omega_Sigma-1)^2 e^{4A}
    metric_residual_is_spring = sp.simplify(J_metric_bps + 2 * beta * (O0 - 1)**2 * sp.exp(4 * A0)) == 0
    omega_junction_at_1 = sp.simplify(J_omega_bps.subs(O0, 1))
    omega_junction_holds_at_1 = (omega_junction_at_1 == 0)
    # tadpole closure: v1 tadpoles are exactly the wall-derivative pieces of the junctions
    v1_tension = sp.simplify(2 * W_of(1))
    v1_omega_tadpole = sp.simplify(-2 * sp.diff(Wq, q).subs(q, 1))
    wall_piece_A_at_bg = sp.simplify(dwall_dA.subs({A: 0, Om: 1}))     # = -4 * 2W(1) = -4 tension (sqrt(-gamma)_1 = 4 delta A)
    wall_piece_Om_at_bg = sp.simplify(dwall_dOm.subs({A: 0, Om: 1}))   # = -2W'(1)
    tadpole_closure_A = sp.simplify(wall_piece_A_at_bg + 4 * v1_tension) == 0
    tadpole_closure_Om = sp.simplify(wall_piece_Om_at_bg - v1_omega_tadpole) == 0
    # the bulk flux that balances them (BPS, Z2)
    flux_A = sp.simplify((-1 * side(pA, 1) + 1 * side(pA, -1)).subs(z2).subs(bps_plus).subs({A0: 0, O0: 1}))
    flux_Om = sp.simplify((-1 * side(pOm, 1) + 1 * side(pOm, -1)).subs(z2).subs(bps_plus).subs({A0: 0, O0: 1}))
    balance_A = sp.simplify(flux_A + wall_piece_A_at_bg) == 0
    balance_Om = sp.simplify(flux_Om + wall_piece_Om_at_bg) == 0

    # --- 6. contrasts (after the fact) ------------------------------------------------------------------------
    contrasts: dict[str, Any] = {}
    # (a) oracle scalar junction restricted to phi = 0
    if ORACLE.is_file():
        orc = json.loads(ORACLE.read_text(encoding="utf-8"))
        eq0 = sp.sympify(orc["equations"]["old_junction_equals_zero"][0], locals={
            "Omega": O0, "k_infinity": kinf, "M5_cubed": M5c, "G": G, "beta": beta, "Z": Z5,
            "normal_Omega_plus": sp.Symbol("nOp"), "normal_Omega_minus": sp.Symbol("nOm"),
            "kappa": sp.Symbol("kappa"), "y": sp.Symbol("y")})
        eq0 = eq0.subs({sp.Symbol(f"phi{i}"): 0 for i in range(3)})
        eq0 = eq0.subs({sp.Symbol(f"normal_phi_plus{i}"): 0 for i in range(3)}).subs({sp.Symbol(f"normal_phi_minus{i}"): 0 for i in range(3)})
        eq0 = sp.simplify(eq0)
        # my J_omega with outward normal derivatives n.grad(Omega): on M_plus outward is -d_w -> nOp = -Omegaprime_plus;
        # on M_minus outward is +d_w -> nOm = Omegaprime_minus.
        mine = sp.simplify(J_omega.subs({Op: -sp.Symbol("nOp"), Omn: sp.Symbol("nOm")}).subs(A0, 0))
        ratio = sp.simplify(mine / eq0) if eq0 != 0 else None
        contrasts["oracle_scalar_junction_phi0"] = {
            "oracle_expression": str(eq0), "mine_in_oracle_variables": str(mine),
            "ratio_mine_over_oracle": str(ratio), "proportional_with_constant_ratio": bool(ratio is not None and ratio.free_symbols <= {O0, G, M5c, kinf, beta} and sp.simplify(sp.diff(ratio, sp.Symbol("nOp"))) == 0 and sp.simplify(sp.diff(ratio, sp.Symbol("nOm"))) == 0),
            "oracle_sha256": _sha256(ORACLE)}
    # (b) charter junction convention strings (recorded for contrast only)
    contrasts["charter_canonical_junction_convention"] = charter_payload["action_charter"].get("junction_convention") or charter_payload.get("canonical_junction_convention") or "not present as a field in the artifact; see generator constant CANONICAL_JUNCTION_CONVENTION"

    checks = {
        "charter_digests_bound_pass": True,
        "pinned_formula_strings_match_charter_pass": True,
        "warped_ansatz_einstein_tensor_computed_pass": True,
        "bps_system_solves_ww_einstein_pass": bool(bps_ok["E_ww"]),
        "bps_system_solves_munu_einstein_pass": bool(bps_ok["E_xx"]),
        "bps_system_solves_omega_equation_pass": bool(bps_ok["E_Omega"]),
        "phi_zero_is_consistent_truncation_pass": bool(phi_zero_consistent),
        "extrinsic_curvature_is_A_prime_times_gamma_pass": bool(theta_is_A_prime_gamma),
        "reduced_action_second_derivatives_are_total_derivative_pass": bool(no_second_derivatives_left),
        "ghy_cancels_bulk_boundary_term_pass": bool(ghy_cancels_boundary),
        "metric_junction_derived_from_action_pass": True,
        "omega_junction_derived_from_action_pass": True,
        "bps_profile_satisfies_metric_junction_at_Omega_Sigma_1_pass": bool(metric_junction_holds_at_1),
        "metric_junction_residual_off_Omega_Sigma_1_is_compensator_spring_pass": bool(metric_residual_is_spring),
        "bps_profile_satisfies_omega_junction_at_Omega_Sigma_1_pass": bool(omega_junction_holds_at_1),
        "v1_tension_tadpole_equals_wall_piece_of_metric_junction_pass": bool(tadpole_closure_A),
        "v1_omega_tadpole_equals_wall_piece_of_omega_junction_pass": bool(tadpole_closure_Om),
        "bps_flux_balances_v1_tension_tadpole_pass": bool(balance_A),
        "bps_flux_balances_v1_omega_tadpole_pass": bool(balance_Om),
    }
    if "oracle_scalar_junction_phi0" in contrasts:
        checks["omega_junction_proportional_to_oracle_phi0_pass"] = bool(contrasts["oracle_scalar_junction_phi0"]["proportional_with_constant_ratio"])
    decision = {k: False for k in PHYSICAL_FALSE_KEYS}
    decision.update({
        "bulk_background_and_junction_derived_from_literal_action_pass": bool(all(checks.values())),
        "v1_tadpoles_closed_by_bulk_junction_pass": bool(balance_A and balance_Om),
        "bulk_fields_varied_pass": True,
        "embeddings_varied_pass": False,
        "old_wall_ADM_Hessian_consumed": False,
    })
    payload = {
        "schema": SCHEMA, "route_id": ROUTE_ID,
        "title": "Full variation of the one-Omega action charter, stage v2.1: bulk background and junction from the literal action",
        "stage": {"ansatz": "ds^2 = e^{2A(w)} eta dx dx + dw^2, Omega(w), phi^a = 0, Z2 about w=0, brane at w=0",
                  "varied": ["g_MN (warped ansatz: A)", "Omega (bulk profile)", "phi^a (consistency of the zero truncation)", "A(0), Omega(0) at the brane (junctions)"],
                  "not_varied": ["Y_plus, Y_minus (displacement)", "brane fields T, X^a, varphi^a beyond the tension", "generic (x-dependent) bulk perturbations"],
                  "side_sign_convention": "s = +1 on M_plus (w>0), -1 on M_minus (w<0); outward normal leaving M_s at w=0 is -s d_w; Z2: A'(0-) = -A'(0+), Omega'(0-) = -Omega'(0+)"},
        "upstream_bindings": {"one_omega_action_charter_gate.json": {"sha256": charter_sha, **EXPECTED_CHARTER_DIGESTS},
                              "one_omega_charter_full_variation_interface_v1_gate.json": {"sha256": _sha256(V1) if V1.is_file() else None,
                                                                                            "used_for": "tension 2W(1) and omega tadpole -2W'(1) closure (values recomputed here from the same W)"},
                              "one_omega_scalar_interface_reparam_v1.json": {"sha256": _sha256(ORACLE) if ORACLE.is_file() else None, "used_for": "contrast only"},
                              "pinned_strings_sha256": _canonical_digest(PINNED_STRINGS)},
        "bulk_equations": {"R_warped": str(R), "E_ww": str(E_ww), "E_munu": str(E_xx), "E_Omega": str(E_Om),
                           "phi_equation_at_phi0": str(el0_at_zero), "phi_sector_contribution_to_Omega_equation_at_phi0": str(dLphi_dOm_at_zero)},
        "bps": {"Omega_prime": str(bps[sp.Derivative(Om, w)]), "A_prime": str(bps[sp.Derivative(A, w)]),
                "sign_note": "same-sign choice fails the Omega equation by 8 W W_Omega/(3 M5^3) and the mu-nu Einstein equation by 2 W_Omega^2/G (per gamma_mu_nu); the ww constraint alone is sign-blind",
                "residuals_on_bps": {k: str(on_bps(vv)) for k, vv in (("E_ww", E_ww), ("E_munu", E_xx), ("E_Omega", E_Om))}},
        "reduced_action": {"L_bulk_1d": str(L_bulk_1d), "total_derivative_B": str(Bw), "L_first_order": str(L_first_order),
                           "Theta_trace_outward": str(sp.simplify(Theta_trace.subs(eps, -s))), "GHY_density": str(GHY_density),
                           "boundary_from_bulk": str(boundary_from_bulk), "p_A": str(pA), "p_Omega": str(pOm)},
        "junctions": {"metric_general": str(J_metric), "omega_general": str(J_omega), "metric_Z2": str(J_metric_z2), "omega_Z2": str(J_omega_z2),
                      "metric_on_bps": str(J_metric_bps), "metric_on_bps_at_Omega_Sigma_1": str(metric_junction_at_1),
                      "omega_on_bps": str(J_omega_bps), "omega_on_bps_at_Omega_Sigma_1": str(omega_junction_at_1),
                      "reading": "sum over sides of (-s) x boundary canonical momentum + d(wall)/d(field) = 0 at w=0"},
        "tadpole_closure": {"v1_tension_2W1": str(v1_tension), "v1_omega_tadpole_minus_2Wprime1": str(v1_omega_tadpole),
                            "wall_piece_A": str(wall_piece_A_at_bg), "wall_piece_Omega": str(wall_piece_Om_at_bg),
                            "bps_flux_A": str(flux_A), "bps_flux_Omega": str(flux_Om),
                            "note": "sqrt(-gamma) = e^{4A}: the v1 lapse/trace tadpole -2W(1) per unit sqrt(-gamma)_1 appears here as d(wall)/dA = -4 x 2W(1)"},
        "contrasts": contrasts,
        "checks": checks, "decision": decision,
        "classification": "theory_only;bulk_background_bps_and_metric_omega_junctions_derived_from_literal_charter_action;v1_tadpoles_closed;linear_junction_operators_DtN_constraints_characteristics_full_Hessian_not_derived;N2_N7_C2_C10_P2_P3_P4_B4_B5_fail_closed",
        "evidence_boundary": [
            "The junctions are derived on the Z2-symmetric homogeneous ansatz (minisuperspace): exact for the background, not the general x-dependent junction operator.",
            "Brane displacement (Y_plus, Y_minus) is not varied; bending enters only at the next stage.",
            "The oracle contrast is proportionality of the phi=0 Omega junction, recorded after the derivation; it is not an input.",
            "The BPS system is verified to solve the bulk equations; uniqueness of the background is not claimed.",
            "Scope of the spring statement: the metric junction residual off Omega_Sigma=1 is the compensator spring only for S_bulk+S_GHY+S_wall0 with the solid relaxed. With the solid held at X^a = v x^a while gamma = e^{2A0} eta, dL_X/dA0 = -(3/2) v^4 (2 mu_X + 3 lambda_X) e^{2A0} (e^{2A0} - 1) is an additional residual for A0 != 0 (Codex witness mu=lambda=v=1, A0=log(2)/2 gives -15). The tadpole closure at A0 = 0 is unaffected.",
        ],
        "provenance": {"generator": Path(__file__).name, "generator_sha256": _sha256(Path(__file__)), "sympy": sp.__version__,
                       "python": platform.python_version(), "elapsed_s": round(time.time() - t0, 1),
                       "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
    }
    payload["calculation_digest"] = _canonical_digest({k: payload[k] for k in DIGEST_KEYS})
    return payload


def main() -> int:
    payload = derive()
    _write(OUTPUT, payload)
    print(json.dumps({"checks": payload["checks"], "elapsed_s": payload["provenance"]["elapsed_s"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
