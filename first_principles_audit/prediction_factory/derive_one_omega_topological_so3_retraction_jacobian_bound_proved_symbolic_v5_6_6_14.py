#!/usr/bin/env python3
"""Proven (symbolic) Jacobian bound of the common-first retraction Phi and the
Sobolev-lift statement (v5.6.6.14) -- ledger gap 4.

v5.6.6.9 certified the graph structure of the common-first gluing and gave an
explicit Jacobian bound for Phi that was DERIVED analytically but VERIFIED only on
samples; the v5.6.6.10 ledger listed "proven (not sampled) Jacobian bound and
Sobolev lift" as gap 4.  This gate replaces the sampled verification by a
machine-checked symbolic certificate:

  * Phi is written symbolically in the 53 free-data symbols (gamma 10, Y 4, d 4, a 1,
    varphi 3, A_Sigma 12, A_perp 3, k 3 [Cayley chart of R], kappa 12, log Omega 1)
    with the 34 outputs (g 15, phi 3, A_mu 12, A_4 3, log Omega 1), exactly as in
    v5.6.6.9's _phi_numeric;
  * every Jacobian entry dPhi_i/du_j is a rational function whose denominator is a
    positive constant times a power of (1 + |k|^2) >= 1, so
      |dPhi_i/du_j| <= (sum of |coefficients| of the numerator, weighted by M^degree) / constant
    on the box max |u| <= M (triangle inequality, |monomial| <= M^degree);
  * ||dPhi||_2 <= ||dPhi||_F <= sqrt(sum of the squared entry bounds) =: B_proved(M),
    an explicit polynomial-under-square-root in M with NO N anywhere.

The certificate is checked by sympy (numerator/denominator structure asserted for
every entry) and, as a consistency witness only, B_proved is compared with the
finite-difference Jacobian norms of the v5.6.6.9 sample set (ball, spikes, corners):
B_proved must dominate every sampled norm, otherwise the derivation is wrong.

Sobolev lift (analytic argument, recorded, not machine-checked): on the class ball
||u||_{H^s} <= M0 with s > d/2 = 2, Phi is real-analytic on the open margin set and
polynomially bounded together with its derivatives by B_proved, so by the Moser
composition estimates ||Phi(u) - Phi(v)||_{H^s} <= C_s(M0) ||u - v||_{H^s}, where the
map consumes first derivatives of Y, r, q_Q (hence H^{s+1} for those, H^s for the
rest), with C_s(M0) depending only on s, M0 and the Sobolev embedding constant
c_s (||u||_inf <= c_s ||u||_{H^s}); no N enters.

This gate does not flip uniform_N_to_infinity_bridge_pass, C1/N1, B4/B5 or any
v5.6.4 fail-closed key, and touches no other file (write lease with Codex).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_retraction_jacobian_bound_proved_symbolic_v5_6_6_14.json"
TEST = HERE / "test_one_omega_topological_so3_retraction_jacobian_bound_proved_symbolic_v5_6_6_14.py"
SCHEMA = "holo.one-omega-topological-so3-retraction-jacobian-bound-proved-symbolic-v5-6-6-14.v1"

FROZEN_COMMIT = "ea014fd1a8ed124c353058eb6f0a1c92b90353bc"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
V5669_DERIVE_PATH = HERE / "derive_one_omega_topological_so3_common_first_explicit_retraction_v5_6_6_9.py"
V5669_DERIVE_SHA256 = "f625067230db6f6f7fc5a0a5ce23eccfb5572fefef4dd185365ca2f00ad65c38"
V5669_RECEIPT_PATH = ARTIFACTS / "one_omega_topological_so3_common_first_explicit_retraction_v5_6_6_9.json"
V5669_RECEIPT_SHA256 = "cad85cf53e70dcfea3f69b104be5fe5c084bc897ddb713eef7d30ae72c85326a"

# Fixed before run.
WITNESS_M_VALUES = (0.001, 0.25, 0.5, 1.0, 1.5, 5.0, 10.0)
WITNESS_SAMPLES_BALL = 100
WITNESS_SEED = 20260904
WITNESS_RADIUS = 1.5
CONSISTENCY_TOLERANCE = 1.0e-9


class ProvedBoundGateError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def load_v5669():
    if _sha256(V5669_DERIVE_PATH) != V5669_DERIVE_SHA256:
        raise ProvedBoundGateError("v5.6.6.9 derive byte pin drift")
    spec = importlib.util.spec_from_file_location("pinned_v5_6_6_9_retraction", V5669_DERIVE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# symbolic Phi (mirrors v5.6.6.9 _phi_numeric, all 53 inputs / 34 outputs)
# --------------------------------------------------------------------------

def _hat(v):
    return sp.Matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def _vee(m):
    return sp.Matrix([m[2, 1], m[0, 2], m[1, 0]])


def symbolic_phi() -> tuple[list[sp.Expr], list[sp.Symbol], dict[str, list[sp.Symbol]], sp.Expr]:
    pairs4 = [(i, j) for i in range(4) for j in range(i, 4)]
    g = list(sp.symbols("gam0:10"))
    Y = list(sp.symbols("Y0:4"))
    d = list(sp.symbols("d0:4"))
    a = sp.Symbol("a")
    varphi = list(sp.symbols("vphi0:3"))
    A_Sigma = [list(sp.symbols(f"AS{mu}_0:3")) for mu in range(4)]
    A_perp = list(sp.symbols("Ap0:3"))
    k = list(sp.symbols("k0:3"))
    kappa = [list(sp.symbols(f"kap{mu}_0:3")) for mu in range(4)]
    log_Omega = sp.Symbol("lOm")
    inputs = g + Y + d + [a] + varphi + sum(A_Sigma, []) + A_perp + k + sum(kappa, []) + [log_Omega]
    groups = {"gamma": g, "Y": Y, "d": d, "a": [a], "varphi": varphi, "A_Sigma": sum(A_Sigma, []), "A_perp": A_perp, "k": k, "kappa": sum(kappa, []), "log_Omega": [log_Omega]}

    gamma = sp.Matrix(4, 4, lambda m, n: g[pairs4.index((min(m, n), max(m, n)))])
    outputs: list[sp.Expr] = []
    # g (15, symmetric5 order)
    gfull = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            gfull[m, n] = gamma[m, n] - d[m] * Y[n] - Y[m] * d[n] + a * Y[m] * Y[n]
        gfull[m, 4] = d[m] - a * Y[m]
        gfull[4, m] = gfull[m, 4]
    gfull[4, 4] = a
    for i in range(5):
        for j in range(i, 5):
            outputs.append(gfull[i, j])
    # rotation (Cayley) and its exact directional derivative
    K = _hat(k)
    I3 = sp.eye(3)
    Minv = (I3 - K).inv()
    R = Minv * (I3 + K)
    phi = R.T * sp.Matrix(varphi)
    outputs += list(phi)
    for mu in range(4):
        dR = 2 * Minv * _hat(kappa[mu]) * Minv
        A_source = _vee(R.T * _hat(A_Sigma[mu]) * R + R.T * dR)
        A_mu = A_source - Y[mu] * sp.Matrix(A_perp)
        outputs += list(A_mu)
    outputs += A_perp
    outputs.append(log_Omega)
    if len(outputs) != 34 or len(inputs) != 53:
        raise ProvedBoundGateError("symbolic layout drift")
    den = 1 + k[0] ** 2 + k[1] ** 2 + k[2] ** 2
    return outputs, inputs, groups, den


def coefficient_sum_bound(expr: sp.Expr, symbols: list[sp.Symbol], M: sp.Symbol) -> sp.Expr:
    """sup over |symbols| <= M of |polynomial| <= sum |c| M^{total degree} (triangle inequality)."""

    P = sp.Poly(sp.expand(expr), *symbols)
    return sum(abs(c) * M ** sum(mono) for mono, c in P.terms())


def entry_bound(entry: sp.Expr, inputs: list[sp.Symbol], k: list[sp.Symbol], den: sp.Expr, M: sp.Symbol) -> tuple[sp.Expr, int, float]:
    """Bound |entry| on the box by numerator coefficient sum / positive constant, after asserting that the
    denominator is const * (1 + |k|^2)^p (>= const on the box)."""

    e = sp.together(entry)
    num, dn = sp.fraction(e)
    dn = sp.expand(dn)
    power = 0
    const = None
    for p in range(0, 9):
        ratio = sp.simplify(dn / den**p)
        if ratio.is_number:
            power, const = p, float(ratio)
            break
    if const is None or const <= 0:
        raise ProvedBoundGateError(f"denominator is not a positive power of (1+|k|^2): {dn}")
    return coefficient_sum_bound(num, inputs, M) / const, power, const


def proved_bound() -> dict[str, Any]:
    outputs, inputs, groups, den = symbolic_phi()
    k = groups["k"]
    M = sp.Symbol("M", positive=True)
    squared_sum = sp.S.Zero
    nonzero_entries = 0
    max_denominator_power = 0
    block_sq: dict[str, sp.Expr] = {}
    block_names = ["g"] * 15 + ["phi"] * 3 + ["A_mu"] * 12 + ["A_4"] * 3 + ["log_Omega"]
    for i, out in enumerate(outputs):
        for s in inputs:
            entry = sp.diff(out, s)
            if entry == 0:
                continue
            nonzero_entries += 1
            bound, power, _const = entry_bound(entry, inputs, k, den, M)
            max_denominator_power = max(max_denominator_power, power)
            squared_sum += sp.expand(bound**2)
            block_sq[block_names[i]] = block_sq.get(block_names[i], sp.S.Zero) + sp.expand(bound**2)
    squared_poly = sp.Poly(sp.expand(squared_sum), M)
    coefficients = {str(int(mono[0])): float(c) for mono, c in squared_poly.terms()}
    block_polys = {name: {str(int(mono[0])): float(c) for mono, c in sp.Poly(sp.expand(expr), M).terms()} for name, expr in block_sq.items()}
    return {
        "inputs": len(inputs),
        "outputs": len(outputs),
        "nonzero_jacobian_entries": nonzero_entries,
        "max_denominator_power_of_1_plus_k2": max_denominator_power,
        "B_proved_squared_polynomial_in_M": coefficients,
        "B_proved_degree_in_M": squared_poly.degree() / 2,
        "block_squared_polynomials": block_polys,
        "formula": "B_proved(M) = sqrt(sum_d c_d M^d) with the coefficients above; ||dPhi(u)||_2 <= B_proved(max|u|) for all free data u",
        "reasoning": [
            "each Jacobian entry is a rational function with denominator const * (1 + |k|^2)^p, const > 0 (asserted per entry)",
            "on max|u| <= M every monomial is bounded by M^degree, so |numerator| <= sum |c| M^deg (triangle inequality)",
            "(1 + |k|^2)^p >= 1, so |entry| <= numerator bound / const",
            "||J||_2 <= ||J||_F = sqrt(sum entry^2) <= sqrt(sum entry_bound^2)",
        ],
    }


def evaluate_B(coefficients: dict[str, float], M: float) -> float:
    return float(np.sqrt(sum(c * M ** int(d) for d, c in coefficients.items())))


def consistency_witness(coefficients: dict[str, float]) -> dict[str, Any]:
    """Compare B_proved against the finite-difference Jacobian norms of the v5.6.6.9 sample design."""

    v5669 = load_v5669()
    worst_ratio = 0.0
    violations = 0
    rows = []
    for kind, u in v5669._sample_set(WITNESS_SAMPLES_BALL, WITNESS_SEED, WITNESS_RADIUS):
        M = float(np.abs(u).max())
        norm = float(np.linalg.norm(v5669._jacobian(u), 2))
        bound = evaluate_B(coefficients, M)
        ratio = norm / bound
        worst_ratio = max(worst_ratio, ratio)
        if norm > bound * (1.0 + CONSISTENCY_TOLERANCE):
            violations += 1
    for M in WITNESS_M_VALUES:
        rows.append({"M": M, "B_proved": evaluate_B(coefficients, M), "B_sampled_formula_v5669": float(v5669.lipschitz_bound_formula(M))})
    return {
        "samples_total": len(v5669._sample_set(WITNESS_SAMPLES_BALL, WITNESS_SEED, WITNESS_RADIUS)),
        "violations": violations,
        "worst_sampled_norm_over_B_proved": worst_ratio,
        "B_proved_vs_v5669_formula": rows,
        "pass": bool(violations == 0),
        "note": "B_proved is looser than the v5.6.6.9 analytic formula (denominators bounded below by 1, Frobenius over 2-norm) but it is fully machine-derived; the sampled norms are a consistency witness, not the proof",
    }


def build_payload() -> dict[str, Any]:
    if _sha256(V5669_RECEIPT_PATH) != V5669_RECEIPT_SHA256:
        raise ProvedBoundGateError("v5.6.6.9 receipt byte pin drift")
    v5669_receipt = json.loads(V5669_RECEIPT_PATH.read_text())
    if v5669_receipt["decision"].get("common_first_gluing_is_explicit_graph_pass") is not True:
        raise ProvedBoundGateError("upstream graph certificate missing")
    bound = proved_bound()
    witness = consistency_witness(bound["B_proved_squared_polynomial_in_M"])
    proved_pass = bool(
        bound["nonzero_jacobian_entries"] > 0
        and bound["max_denominator_power_of_1_plus_k2"] >= 1
        and witness["pass"]
    )
    scientific = {
        "proved_bound": bound,
        "consistency_witness": witness,
        "sobolev_lift": {
            "statement": (
                "For s > 2 and free data u, v in the class ball ||.||_{H^s} <= M0 (with Y, r, q_Q in H^{s+1}) inside the "
                "margin set, ||Phi(u) - Phi(v)||_{H^s} <= C_s(M0) ||u - v||_{H^s}, where C_s(M0) depends only on s, M0 "
                "and the embedding constant c_s (max|u| <= c_s ||u||_{H^s}), through B_proved(c_s M0) and the Moser "
                "composition estimates for real-analytic maps with polynomially bounded derivatives. No N enters."
            ),
            "machine_checked": False,
            "hypotheses": ["s > d/2 = 2", "margins on the whole collar (v5.6.6.13 for the pinned members; hypothesis for arbitrary class members)", "Y, r, q_Q in H^{s+1}"],
        },
        "machine_checked": {
            "every_jacobian_entry_denominator_is_positive_power_of_1_plus_k2": True,
            "B_proved_polynomial_derived_symbolically": True,
            "B_proved_dominates_v5669_sample_design": witness["pass"],
        },
        "analytic_not_machine_checked": ["Moser composition estimates and the Sobolev embedding (classical)"],
    }
    decision = {
        "pointwise_retraction_jacobian_bound_proved_symbolic_pass": proved_pass,
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
        "classification": "theory_only;symbolic_jacobian_bound;pointwise_retraction;restricted_spectral_family;fail_closed_bridge",
        "decision": decision,
        "fixed_before_run": {
            "WITNESS_M_VALUES": list(WITNESS_M_VALUES),
            "WITNESS_SAMPLES_BALL": WITNESS_SAMPLES_BALL,
            "WITNESS_SEED": WITNESS_SEED,
            "WITNESS_RADIUS": WITNESS_RADIUS,
            "CONSISTENCY_TOLERANCE": CONSISTENCY_TOLERANCE,
            "rotation_chart": "Cayley (I-K)^{-1}(I+K); denominators are powers of 1 + |k|^2",
        },
        "scientific": scientific,
        "independence_boundary": {
            "imports_pinned_v5669_kinematic_module_for_witness_only": True,
            "pinned_v5669_derive": {"path": V5669_DERIVE_PATH.name, "sha256": V5669_DERIVE_SHA256},
            "imports_action_evaluators": False,
            "imports_route_c_or_ad_fd5_modules": False,
            "reads_upstream_expected_values": False,
            "symbolic_engine": f"sympy {sp.__version__}",
        },
        "open_obligation": {
            "gap_5": "finite DG_N on V_N and the gauge quotient H_N",
            "sobolev_lift_formalisation": "optional: make the Moser constant explicit for the class norm",
        },
        "evidence_boundary": (
            "Machine-checked: a symbolic, N-free polynomial bound B_proved(M) on the operator norm of dPhi on the box "
            "max|u| <= M, derived entry by entry with asserted denominator structure, and its domination of the v5.6.6.9 "
            "sample design. Analytic: the Sobolev lift. Not proven: the bridge, C1/N1, B4/B5."
        ),
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "v5_6_6_9_derive_sha256": V5669_DERIVE_SHA256,
            "v5_6_6_9_receipt_sha256": V5669_RECEIPT_SHA256,
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
    if not payload["decision"]["pointwise_retraction_jacobian_bound_proved_symbolic_pass"]:
        raise ProvedBoundGateError("proved bound certificate failed")
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    b = payload["scientific"]["proved_bound"]
    w = payload["scientific"]["consistency_witness"]
    print(
        f"proved={payload['decision']['pointwise_retraction_jacobian_bound_proved_symbolic_pass']} entries={b['nonzero_jacobian_entries']} "
        f"deg={b['B_proved_degree_in_M']} B(1)={evaluate_B(b['B_proved_squared_polynomial_in_M'], 1.0):.1f} "
        f"worst_ratio={w['worst_sampled_norm_over_B_proved']:.3f} violations={w['violations']}"
    )


if __name__ == "__main__":
    main()
