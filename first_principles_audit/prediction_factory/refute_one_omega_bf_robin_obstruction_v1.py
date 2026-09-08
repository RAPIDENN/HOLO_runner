#!/usr/bin/env python3
"""Independent refutation attempt of the BF/Robin torque obstruction (Codex a724b81 / aeaeba3).

Read-only with respect to Codex's files: nothing is imported from the verifier or the lemma;
the claim is rebuilt from the literal v5.2 rows recorded in the candidate artifact and attacked
at every step where it could fail.

Claim under test (lemma sections 1-3b): for the literal v5.2 action with kappa*y != 0,
the BF connection equation D_A B + J4 = 0 pulled back to Sigma with a common A_Sigma and the
flux gluing b_+ = b_- force the sum of outgoing matter currents to vanish; contracting the
natural Robin row with T_I phi_H then forces  a x phi_H = 0  on Sigma.  This is invisible at
linear order (it is the eps^2 coefficient a1 x phi1) and a two-direction prescribed port with
the exact half-space material response violates it, so those port data have no C2 continuation.

Attacks performed here:
 A1 contraction identity: with the su(2) generators (T_I)^J_K = eps_IJK and the current
    Q_I,out = -Pi_out . (T_I phi), the Robin row  sum_out Pi + kappa (phi_H - y a) = 0  gives
    sum_out Q_I = -kappa y (a x phi_H)_I exactly (generic symbolic vectors);
 A2 the conformal mixing term contributes no torque: phi . (T_I phi) = 0;
 A3 second-order expansion: a(e) x phi(e) = e^2 (a1 x phi1) + o(e^2); neither a2 nor phi2
    enters the e^2 coefficient;
 A4 conformal flattening of the material sector on the BPS wall: with g = Omega^2 eta_5 and
    psi = Omega^(3/2) phi, sqrt(-g) [-(Z/2) P.P - Z m^2 Omega^-5 V4(Omega^(3/2)|phi|)]
    = -(Z/2) (d psi)^2 - Z m^2 V4(|psi|) exactly (any Omega(w), any dimension count 5);
 A5 half-space linear response: the decaying solution of the flat Laplace equation with
    tangential modulus p has outgoing canonical momentum Z p per side; the Robin row then gives
    phi1(k) = kappa y a1(k) / (kappa + 2 Z |k|), a wavenumber-dependent gain;
 A6 Codex's witness reproduced from scratch (gains 1/3, 1/5; coefficient 4 y sin x sin 2z / 15;
    residual -4/5 at (pi/2, pi/4) with kappa = Z = 1, y^2 = 3);
 A7 an independent witness in a different pair of directions (x and y, cross component along
    z) and the general statement: for a = grad F with two Fourier shells of different modulus,
    a1 x phi1 = (g(p1) - g(p2)) (grad F_1 x grad F_2) which vanishes identically iff the two
    gains coincide, i.e. iff |k1| = |k2|;
 A8 absorber audit: which literal rows contain A_Sigma at all. Only S_BF does (through F[A]);
    S_R_intrinsic, S_fol_lower, S_wall0, S_GHY and the gauged kinetic term carry no derivative
    of A, so the boundary variation in A_Sigma produces b_+ - b_- = 0 and nothing else.
 A9 escape attempt: can a first-order connection A1 (flat, F=0) change the linear material
    response and re-align phi1 with a1?  No: A1 enters P only through A1 x phi, i.e. at second
    order; the eps^2 coefficient in A3 is fixed by (a1, phi1) alone.

Verdict is CONFIRMED if every attack fails to break the chain; the sharpening recorded is the
Noether reading: the brane Robin term explicitly breaks the internal SO(3) that BF gauges, so the
internal current has a brane source (the torque) while BF gluing demands a source-free normal
current.  Any completion keeping a flat BF connection and the explicit breaking inherits a x phi = 0.
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
OUTPUT = HERE / "artifacts" / "refute_one_omega_bf_robin_obstruction_v1.json"
CANDIDATE = HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
CODEX_RECEIPT = HERE / "artifacts" / "one_omega_bf_robin_compatibility_v1.json"
CODEX_NOTE = HERE / "one_omega_bf_robin_compatibility_lemma_v1.md"
SCHEMA = "holo.refute-one-omega-bf-robin-obstruction.v1"

PINNED_CANDIDATE_ROWS = {
    "exact_action.BF": "S_BF=sum_eps int_Meps <B_eps wedge F[A_eps]>, <X,Y>=-tr_3(XY)/2",
    "exact_action.Robin_intrinsic": "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)",
    "exact_action.gauged_conformal_derivative": "P_eps_M=D_(A_eps,M)phi_eps+3*phi_eps*partial_M log(Omega_eps)/2",
    "exact_action.bulk_gauged": "S_bulk_gauged=sum_eps int_Meps sqrt(-g_eps)*[M5^3*R_eps/2-G*(nabla Omega_eps)^2/2-U(Omega_eps)-Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2-Z5*M^2*Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)]",
    "exact_action.removed_terms": "S_X=0 and every bulk screen-clock term=0",
    "exact_action.total": "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF",
}
PINNED_INTERFACE = {
    "BF_flux": "sum_eps s_eps*b_eps=0",
    "Robin": "sum_eps Pi_phi_eps+kappa_hat*(varphi_H-y*a_sharp)=0",
}


class RefutationError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _load_candidate() -> tuple[dict[str, Any], str]:
    payload = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    ch = payload["exact_classical_charter"]
    for dotted, expected in PINNED_CANDIDATE_ROWS.items():
        block, key = dotted.split(".")
        if str(ch[block].get(key)) != expected:
            raise RefutationError(f"candidate row {dotted} differs")
    nat = payload["Green_form_certificate"]["natural_interface_equations"]
    for key, expected in PINNED_INTERFACE.items():
        if str(nat.get(key)) != expected:
            raise RefutationError(f"interface row {key} differs")
    return payload, _sha256(CANDIDATE)


def cross(u, v):
    return sp.Matrix([u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]])


def derive() -> dict[str, Any]:
    t0 = time.time()
    cand, cand_sha = _load_candidate()
    kap, y, Z, m = sp.symbols("kappa_hat y Z5 M_mat", positive=True)
    # generators (T_I)^J_K = eps_IJK acting on internal vectors: (T_I phi)^J = eps_IJK phi^K  ==  -(e_I x phi)^J
    def T(I, vec):
        # (T_I vec)^J = eps_IJK vec^K, the lemma's convention, so that a.(T_I phi) = (a x phi)_I
        return sp.Matrix([sum(sp.LeviCivita(I, J, K) * vec[K] for K in range(3)) for J in range(3)])
    # --- A1: contraction identity ---------------------------------------------------------------------------
    a = sp.Matrix(sp.symbols("a0 a1 a2", real=True))
    ph = sp.Matrix(sp.symbols("f0 f1 f2", real=True))           # phi_H in the internal frame
    Pip = sp.Matrix(sp.symbols("Pp0 Pp1 Pp2", real=True))       # Pi_out on the + side
    Pim = sp.Matrix(sp.symbols("Pm0 Pm1 Pm2", real=True))       # Pi_out on the - side
    robin_row = Pip + Pim + kap * (ph - y * a)                   # = 0 on shell
    # Q_I,out = -Pi_out . (T_I phi)
    Qsum = sp.Matrix([-(Pip.dot(T(I, ph))) - (Pim.dot(T(I, ph))) for I in range(3)])
    # substitute Pip + Pim from the Robin row: Pim = -Pip - kap (ph - y a)
    Qsum_on_shell = Qsum.subs({Pim[i]: -Pip[i] - kap * (ph[i] - y * a[i]) for i in range(3)})
    target = -kap * y * cross(a, ph)
    A1 = sp.simplify(Qsum_on_shell - target) == sp.zeros(3, 1)
    # --- A2: conformal mixing has no torque ------------------------------------------------------------------
    A2 = all(sp.simplify(ph.dot(T(I, ph))) == 0 for I in range(3))
    # --- A3: second-order expansion -------------------------------------------------------------------------
    e = sp.Symbol("epsilon")
    a1 = sp.Matrix(sp.symbols("a1_0 a1_1 a1_2", real=True)); a2 = sp.Matrix(sp.symbols("a2_0 a2_1 a2_2", real=True))
    p1 = sp.Matrix(sp.symbols("p1_0 p1_1 p1_2", real=True)); p2 = sp.Matrix(sp.symbols("p2_0 p2_1 p2_2", real=True))
    ae = e * a1 + e**2 * a2 / 2; pe = e * p1 + e**2 * p2 / 2
    c2 = sp.expand(cross(ae, pe)).applyfunc(lambda x: x.coeff(e, 2))
    A3 = sp.simplify(c2 - cross(a1, p1)) == sp.zeros(3, 1)
    A3_no_second_order = not any(c2[i].has(*a2) or c2[i].has(*p2) for i in range(3))
    # --- A4: conformal flattening on the BPS wall (g = Omega^2 eta_5, psi = Omega^(3/2) phi) ------------------
    xs = sp.symbols("x0 x1 x2 x3 w", real=True)
    Om = sp.Function("Omega")(*xs)   # general conformal factor
    phi = [sp.Function(f"phi{i}")(*xs) for i in range(3)]
    eta5 = sp.diag(-1, 1, 1, 1, 1)
    g = Om**2 * eta5; ginv = eta5 / Om**2; sqrt_g = Om**5
    P = [[sp.diff(phi[a_], xs[M]) + sp.Rational(3, 2) * phi[a_] * sp.diff(sp.log(Om), xs[M]) for M in range(5)] for a_ in range(3)]
    P2 = sum(ginv[M, M] * P[a_][M]**2 for a_ in range(3) for M in range(5))
    r_phi = sp.sqrt(sum(f**2 for f in phi))
    V4 = lambda r: r**4 / (2 * sp.sqrt(1 + r**4))
    L_curved = sqrt_g * (-Z * P2 / 2 - Z * m**2 * Om**(-5) * V4(Om**sp.Rational(3, 2) * r_phi))
    psi = [Om**sp.Rational(3, 2) * f for f in phi]
    L_flat = -Z * sum(eta5[M, M] * sp.diff(psi[a_], xs[M])**2 for a_ in range(3) for M in range(5)) / 2 - Z * m**2 * V4(sp.sqrt(sum(pp**2 for pp in psi)))
    A4 = sp.simplify(sp.expand(L_curved - L_flat)) == 0
    # --- A5: half-space response --------------------------------------------------------------------------------
    zr, p = sp.symbols("z_radial p", positive=True)
    c = sp.Symbol("c", real=True)
    psi_dec = c * sp.exp(-p * zr)
    # flat Laplace: -p^2 psi + psi'' = 0 for a tangential mode of modulus p
    A5_solution = sp.simplify(sp.diff(psi_dec, zr, 2) - p**2 * psi_dec) == 0
    # outgoing canonical momentum per side: Pi_out = Z * (-d/dz_radial psi at 0) = Z p c
    Pi_side = sp.simplify(-Z * sp.diff(psi_dec, zr).subs(zr, 0))
    A5_momentum = sp.simplify(Pi_side - Z * p * c) == 0
    # Robin: 2 Z p phi1 + kappa (phi1 - y a1) = 0 -> phi1 = kappa y a1 / (kappa + 2 Z p)
    a1s, phi1s = sp.symbols("a1s phi1s", real=True)
    sol = sp.solve(sp.Eq(2 * Z * p * phi1s + kap * (phi1s - y * a1s), 0), phi1s)[0]
    gain = sp.simplify(sol / a1s)
    A5_gain = sp.simplify(gain - kap * y / (kap + 2 * Z * p)) == 0
    # --- A6: Codex witness from scratch ---------------------------------------------------------------------------
    x, z = sp.symbols("x z", real=True)
    num = {kap: 1, Z: 1}
    F = sp.cos(x) + sp.cos(2 * z)
    a1w = sp.Matrix([sp.diff(F, x), 0, sp.diff(F, z)])           # gradient of the prescribed log N (tangential y-direction absent)
    g1 = gain.subs(num).subs(p, 1); g2 = gain.subs(num).subs(p, 2)  # |k| = 1 for cos x, |k| = 2 for cos 2z
    phi1w = sp.Matrix([g1 * sp.diff(sp.cos(x), x), 0, g2 * sp.diff(sp.cos(2 * z), z)])
    cw = cross(a1w, phi1w).applyfunc(sp.simplify)
    A6_gains = (sp.simplify(g1 / y - sp.Rational(1, 3)) == 0) and (sp.simplify(g2 / y - sp.Rational(1, 5)) == 0)
    A6_coeff = sp.simplify(cw[1] - 4 * y * sp.sin(x) * sp.sin(2 * z) / 15) == 0
    residual = sp.simplify((-kap * y * cw[1]).subs(num).subs({x: sp.pi / 2, z: sp.pi / 4}).subs(y**2, 3))
    A6_residual = sp.simplify(residual + sp.Rational(4, 5)) == 0
    # --- A7: independent witness (x and y directions; component along z) and the general statement ----------------
    yv = sp.Symbol("y_coord", real=True)
    F2 = sp.cos(x) + sp.cos(3 * yv)
    a1v = sp.Matrix([sp.diff(F2, x), sp.diff(F2, yv), 0])
    gA = gain.subs(num).subs(p, 1); gB = gain.subs(num).subs(p, 3)
    phi1v = sp.Matrix([gA * sp.diff(sp.cos(x), x), gB * sp.diff(sp.cos(3 * yv), yv), 0])
    cv = cross(a1v, phi1v).applyfunc(sp.simplify)
    A7_new_witness_nonzero = sp.simplify(cv[2]) != 0
    # general two-shell statement: F = F1 + F2 with gains gA, gB: a x phi = (gB - gA) (grad F1 x grad F2)
    F1s, F2s = sp.Function("F1")(x, yv, z), sp.Function("F2")(x, yv, z)
    gAs, gBs = sp.symbols("g_A g_B", real=True)
    grad = lambda f: sp.Matrix([sp.diff(f, x), sp.diff(f, yv), sp.diff(f, z)])
    lhs = cross(grad(F1s) + grad(F2s), gAs * grad(F1s) + gBs * grad(F2s))
    rhs = (gBs - gAs) * cross(grad(F1s), grad(F2s))
    A7_general = sp.simplify(sp.expand(lhs - rhs)) == sp.zeros(3, 1)
    A7_vanishes_if_equal_gains = sp.simplify(rhs.subs(gBs, gAs)) == sp.zeros(3, 1)
    # Codex counterexample (045939Z): parallel gradients with different moduli also give zero torque
    F1c, F2c = sp.cos(x), sp.cos(2 * x)
    gC1, gC2 = gain.subs(num).subs(p, 1), gain.subs(num).subs(p, 2)
    coll = cross(grad(F1c) + grad(F2c), gC1 * grad(F1c) + gC2 * grad(F2c)).applyfunc(sp.simplify)
    A7_collinear_counterexample_zero = (coll == sp.zeros(3, 1)) and sp.simplify(gC1 - gC2) != 0
    # --- A8: absorber audit on the literal rows ----------------------------------------------------------------------
    rows = cand["exact_classical_charter"]["exact_action"]
    contains_A = {k: ("F[A" in v or "D_(A" in v or "A_Sigma" in v) for k, v in rows.items() if isinstance(v, str)}
    derivative_of_A = {k: ("F[A" in v) for k, v in rows.items() if isinstance(v, str)}   # only the field strength differentiates A
    A8_only_BF_differentiates_A = [k for k, v in derivative_of_A.items() if v] == ["BF"]
    A8_robin_has_no_A = not contains_A.get("Robin_intrinsic", True)
    # --- A9: a flat first-order connection cannot re-align the linear response -----------------------------------------
    A1c = sp.Matrix(sp.symbols("A1_0 A1_1 A1_2", real=True))   # first-order connection component along some direction
    Pe = e * sp.Matrix(sp.symbols("dphi_0 dphi_1 dphi_2", real=True)) + cross(e * A1c, e * p1)   # D_A phi = d phi + A x phi
    A9 = all(sp.expand(Pe[i]).coeff(e, 1).has(*A1c) is False for i in range(3))
    # --- Noether sharpening: the brane term breaks the internal rotation that BF gauges --------------------------------
    lam = sp.Matrix(sp.symbols("l0 l1 l2", real=True))
    dphi = cross(lam, ph)                                     # infinitesimal internal rotation of phi_H, a fixed
    robin_density = -kap / 2 * (ph - y * a).dot(ph - y * a)
    d_robin = sp.simplify(sum(sp.diff(robin_density, ph[i]) * dphi[i] for i in range(3)))
    noether_source = sp.simplify(d_robin + kap * y * lam.dot(cross(a, ph)))
    noether_ok = (noether_source == 0)   # delta_lambda L_R = -kappa y lambda . (a x phi): torque source on Sigma (sign fixed by delta phi = lambda x phi)
    log = {"elapsed_s": round(time.time() - t0, 1)}

    attacks = {
        "A1_contraction_identity_sum_out_Q_equals_minus_kappa_y_a_cross_phi": bool(A1),
        "A2_conformal_mixing_has_no_torque": bool(A2),
        "A3_second_order_coefficient_is_a1_cross_phi1": bool(A3),
        "A3_no_a2_or_phi2_in_second_order_coefficient": bool(A3_no_second_order),
        "A4_material_sector_flattens_exactly_in_conformal_frame": bool(A4),
        "A5_decaying_mode_solves_flat_laplace": bool(A5_solution),
        "A5_outgoing_momentum_per_side_is_Z_p": bool(A5_momentum),
        "A5_robin_gain_is_kappa_y_over_kappa_plus_2Zp": bool(A5_gain),
        "A6_codex_gains_one_third_one_fifth": bool(A6_gains),
        "A6_codex_cross_coefficient_4y_sinx_sin2z_over_15": bool(A6_coeff),
        "A6_codex_residual_minus_four_fifths": bool(A6_residual),
        "A7_independent_two_direction_witness_nonzero": bool(A7_new_witness_nonzero),
        "A7_general_two_shell_identity": bool(A7_general),
        "A7_cross_vanishes_if_gains_equal": bool(A7_vanishes_if_equal_gains),
        "A7_collinear_gradients_give_zero_torque_despite_different_gains": bool(A7_collinear_counterexample_zero),
        "A8_only_BF_differentiates_A": bool(A8_only_BF_differentiates_A),
        "A8_robin_intrinsic_has_no_A_Sigma": bool(A8_robin_has_no_A),
        "A9_flat_first_order_connection_enters_P_only_at_second_order": bool(A9),
        "N_noether_robin_variation_equals_torque_source": bool(noether_ok),
    }
    every_attack_failed_to_break = all(attacks.values())
    verdict = "CONFIRMADA" if every_attack_failed_to_break else "SIN VEREDICTO"
    payload = {
        "schema": SCHEMA,
        "title": "Independent refutation attempt of the BF/Robin torque obstruction: verdict " + verdict,
        "claim_under_test": "literal v5.2 with kappa*y != 0: BF gluing + common A_Sigma + Robin row force a x phi_H = 0 on Sigma; eps^2 coefficient a1 x phi1; two-direction prescribed ports have no C2 continuation",
        "sources": {"candidate_v5_2_artifact_sha256": cand_sha,
                    "codex_receipt_sha256": _sha256(CODEX_RECEIPT) if CODEX_RECEIPT.is_file() else None,
                    "codex_note_sha256": _sha256(CODEX_NOTE) if CODEX_NOTE.is_file() else None,
                    "imported_from_codex": "nothing; rows re-pinned from the candidate artifact",
                    "pinned_rows_sha256": _canonical_digest({**PINNED_CANDIDATE_ROWS, **PINNED_INTERFACE})},
        "attacks": attacks,
        "independent_witness": {"lapse": "cos x + cos 3y (x and y tangential; cross component along z)",
                                "gains": [str(gA), str(gB)], "cross_component_z": str(cv[2])},
        "general_statement": "for a = grad(F1 + F2) with gains g_A, g_B on the two shells, a1 x phi1 = (g_B - g_A) grad F1 x grad F2; it vanishes identically iff g_A = g_B (i.e. |k_1| = |k_2|) OR grad F1 is parallel to grad F2 identically (Codex counterexample F1 = cos x, F2 = cos 2x: different moduli, zero torque). A nonvanishing torque needs both different moduli and non-collinear gradients, as in the x-z and x-y witnesses",
        "sharpening": {
            "noether_reading": "delta_lambda L_R = -kappa y lambda.(a x phi_H) for delta phi_H = lambda x phi_H: the intrinsic Robin term is a source of internal SO(3) torque localized on Sigma, while the BF flux gluing with a common flat A_Sigma demands a source-free normal current. A flat BF connection cannot be coupled to a current with a brane source; the alignment a x phi_H = 0 is the price of soldering an internal triplet to the geometric acceleration through a gauged SO(3).",
            "consequence": "any completion that keeps (i) a flat BF connection glued with common A_Sigma, (ii) the explicit breaking (phi_H - y a) on Sigma AND (iii) no intrinsic connection current on Sigma (b_+ - b_- = 0, J_Sigma = 0) inherits the condition (Codex 045740Z: the third ingredient is essential; S_C keeps (i)-(ii) and escapes through (iii)). The variation delta phi_H at fixed a is a relative variation, not a passive frame rotation, which would rotate a too. Repairs must either give the connection a source-carrying dynamics on Sigma (Codex's S_C proposal) or restrict the data class, and either changes the action or the admissible domain.",
            "not_claimed": ["inconsistency of every solution", "complete Dirac rank", "refutation of the fixed-direction N8 lift", "that the two-mode lapse solves the coupled Einstein problem"],
        },
        "verdict": verdict,
        "decision": {"obstruction_confirmed_by_independent_reconstruction": bool(every_attack_failed_to_break),
                     "codex_witness_reproduced": bool(A6_gains and A6_coeff and A6_residual),
                     "new_independent_witness_found": bool(A7_new_witness_nonzero),
                     "any_literal_absorber_found": False,
                     "S_C_repair_adopted": False, "B4_pass": False, "B5_pass": False, "N7_pass": False, "P4_full_same_action_pass": False},
        "provenance": {"generator": Path(__file__).name, "generator_sha256": _sha256(Path(__file__)), "sympy": sp.__version__,
                       "python": platform.python_version(), **log, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
    }
    payload["calculation_digest"] = _canonical_digest({k: payload[k] for k in ("schema", "claim_under_test", "sources", "attacks", "independent_witness", "general_statement", "sharpening", "verdict", "decision")})
    return payload


def main() -> int:
    payload = derive()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "attacks": payload["attacks"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
