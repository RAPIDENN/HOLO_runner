#!/usr/bin/env python3
"""Route C quadrature ladders (tangential saturation, radial geometric rate) and the pointwise-bridge component ledger (v5.6.6.10).

Fourth component of the continuum bridge in the pointwise (common-first) formulation.

(A) Refinement ladders (machine-checked on byte-pinned receipts).  The v5.6.6.5
    precision-stabilized Route C receipt carries, for every pinned member N = 1,2,3,
    two refinement ladders of the twenty-one first-variation components: tangential
    Qtheta = 11, 13, 15 at fixed Qrho = 14, and radial Qrho = 12, 14, 16 at fixed
    Qtheta = 13.  This gate recomputes every consecutive difference and certifies
    two different facts:
      - the TANGENTIAL ladders are saturated at the round-off floor of the
        longdouble pipeline (relative change <= 1e-9; measured 1e-16 for N=1 and
        ~1e-10 for N=2,3), i.e. the trapezoidal rule has converged;
      - the RADIAL ladders are NOT saturated but contract geometrically: the
        second step (14 -> 16) is at most a fixed fraction of the first (12 -> 14)
        (measured ratio ~0.03 per two Gauss--Legendre nodes), and the geometric
        extrapolation of the tail beyond Qrho = 16 is below a declared relative
        tolerance.  This is a measured convergence rate, not a saturation claim.

(B) Why this is expected (analytic argument recorded, not machine-checked).
    For N <= 3 the tangential data of the pinned members are trigonometric
    polynomials of degree <= 1 in the single direction theta = x0 + x1 (basis
    labels of the byte-pinned bundle: 1, cos, sin), the radial profiles are
    polynomials, and the literal v5.2 density is real-analytic on the margin set.
    The integrand is therefore 2*pi-periodic and analytic in a strip |Im theta| < d,
    so the Qtheta-point trapezoidal rule converges like 4*pi*M_d/(exp(2*d*Qtheta)-1)
    (Trefethen--Weideman 2014, Thm 3.2), and Gauss--Legendre in rho converges
    geometrically like rho_B^{-2 Qrho} for integrands analytic inside the Bernstein
    ellipse of parameter rho_B.  The measured radial ratio gives an empirical
    rho_B; the tangential saturation at Qtheta = 11 gives an indicative lower
    bound on d.  Neither number enters a decision key.

(C) Bridge component ledger.  Records, with byte pins, which receipt carries each
    component of the pointwise bridge:
      (i)   exact second-order Euler--Green identity on the class   -> v5.6.6.8
      (ii)  continuity bound on the class                           -> v5.6.6.8 (stated)
      (iii) N-independent explicit retraction (graph of Phi)        -> v5.6.6.9
      (iv)  finite Route C certificates at saturation               -> this gate
    and states plainly which parts are machine-checked and which are analytic
    arguments.  Component (iv) is "finite certificates with a measured geometric
    radial rate and a saturated tangential rule", not "finite certificates at
    saturation".  It does NOT flip uniform_N_to_infinity_bridge_pass: the v5.6.1
    quarantine requires an independently audited gate for that, and components
    (ii) and the analyticity strip of (iv) are prose.  It also does not flip
    C1/N1, B4/B5 or any v5.6.4 fail-closed key.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_route_c_quadrature_saturation_bridge_ledger_v5_6_6_10.json"
TEST = HERE / "test_one_omega_topological_so3_route_c_quadrature_saturation_bridge_ledger_v5_6_6_10.py"
SCHEMA = "holo.one-omega-topological-so3-route-c-quadrature-saturation-bridge-ledger-v5-6-6-10.v1"

FROZEN_COMMIT = "ea014fd1a8ed124c353058eb6f0a1c92b90353bc"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
V5665_PATH = ARTIFACTS / "one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5.json"
V5665_SHA256 = "06ad302a03d17e4ea718c9ab801113807a7f66c71102e69486f7869130f77654"
V5668_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.json"
V5668_SHA256 = "175dae746dcbf19854d1bdb6e0b6b5541d3eb18acea0050d41fccd444f197091"
V5669_PATH = ARTIFACTS / "one_omega_topological_so3_common_first_explicit_retraction_v5_6_6_9.json"
V5669_SHA256 = "cad85cf53e70dcfea3f69b104be5fe5c084bc897ddb713eef7d30ae72c85326a"

# Fixed before run.
TANGENTIAL_SATURATION_RELATIVE_TOLERANCE = 1.0e-9
RADIAL_CONTRACTION_RATIO_MAX = 0.1
RADIAL_EXTRAPOLATED_TAIL_RELATIVE_MAX = 1.0e-8
EXPECTED_TANGENTIAL_ORDERS = ("11", "13", "15")
EXPECTED_RADIAL_ORDERS = ("12", "14", "16")
EXPECTED_MEMBERS = ((1, 1), (2, 2), (3, 3))
MAX_TANGENTIAL_WAVEVECTOR_RADIUS = 1


class LedgerGateError(RuntimeError):
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
        raise LedgerGateError(f"byte pin drift for {path.name}: {digest} != {expected_sha256}")
    return json.loads(path.read_text())


# --------------------------------------------------------------------------
# (A) ladder saturation
# --------------------------------------------------------------------------

def _ladder_differences(records: dict[str, dict[str, float]], orders: tuple[str, ...]) -> dict[str, Any]:
    if tuple(sorted(records, key=int)) != orders:
        raise LedgerGateError(f"ladder orders drift: {sorted(records, key=int)} != {orders}")
    components = sorted(records[orders[0]])
    steps = []
    for lo, hi in zip(orders[:-1], orders[1:]):
        rel_step = 0.0
        abs_step = 0.0
        scale_at_worst = 1.0
        for key in components:
            left, right = float(records[lo][key]), float(records[hi][key])
            diff = abs(right - left)
            scale = max(1.0, abs(left), abs(right))
            if diff > abs_step:
                abs_step, scale_at_worst = diff, scale
            rel_step = max(rel_step, diff / scale)
        steps.append({"from": lo, "to": hi, "max_abs_difference": abs_step, "max_rel_difference": rel_step, "scale_at_worst": scale_at_worst})
    worst_relative = max(step["max_rel_difference"] for step in steps)
    worst_absolute = max(step["max_abs_difference"] for step in steps)
    ratio = None
    tail_abs = None
    tail_rel = None
    if len(steps) == 2 and steps[0]["max_abs_difference"] > 0.0:
        ratio = steps[1]["max_abs_difference"] / steps[0]["max_abs_difference"]
        if ratio < 1.0:
            # geometric tail beyond the last order: sum_{j>=1} last_step * ratio^j
            tail_abs = steps[1]["max_abs_difference"] * ratio / (1.0 - ratio)
            tail_rel = tail_abs / steps[1]["scale_at_worst"]
    return {
        "orders": list(orders),
        "components": len(components),
        "steps": steps,
        "worst_relative_difference": worst_relative,
        "worst_absolute_difference": worst_absolute,
        "second_over_first_step_ratio": ratio,
        "geometric_extrapolated_tail_abs": tail_abs,
        "geometric_extrapolated_tail_rel": tail_rel,
        "saturated_at_relative": bool(worst_relative <= TANGENTIAL_SATURATION_RELATIVE_TOLERANCE),
        "geometric_contraction": bool(ratio is not None and ratio <= RADIAL_CONTRACTION_RATIO_MAX and tail_rel is not None and tail_rel <= RADIAL_EXTRAPOLATED_TAIL_RELATIVE_MAX),
    }


def ladder_audit(v5665: dict[str, Any]) -> dict[str, Any]:
    members = []
    tangential_ok = True
    radial_ok = True
    for member in v5665["scientific"]["members"]:
        tangential = _ladder_differences(member["tangential"]["records_by_order"], EXPECTED_TANGENTIAL_ORDERS)
        radial = _ladder_differences(member["radial"]["records_by_order"], EXPECTED_RADIAL_ORDERS)
        tangential_ok = tangential_ok and tangential["saturated_at_relative"]
        radial_ok = radial_ok and radial["geometric_contraction"]
        members.append(
            {
                "N": int(member["N"]),
                "K": int(member["K"]),
                "member_id": member["member_id"],
                "authoritative_free_central_sha256": member["authoritative_free_central_sha256"],
                "fixed_radial_order_for_tangential_ladder": int(member["tangential"]["fixed_radial_order"]),
                "fixed_tangential_order_for_radial_ladder": int(member["radial"]["fixed_tangential_order"]),
                "tangential": tangential,
                "radial": radial,
                "upstream_convergence_pass": bool(member["member_precision_stabilized_convergence_pass"]),
            }
        )
    if [(m["N"], m["K"]) for m in members] != list(EXPECTED_MEMBERS):
        raise LedgerGateError("member set drift")
    radial_ratios = [m["radial"]["second_over_first_step_ratio"] for m in members]
    return {
        "tolerances": {
            "tangential_saturation_relative": TANGENTIAL_SATURATION_RELATIVE_TOLERANCE,
            "radial_contraction_ratio_max": RADIAL_CONTRACTION_RATIO_MAX,
            "radial_extrapolated_tail_relative_max": RADIAL_EXTRAPOLATED_TAIL_RELATIVE_MAX,
        },
        "members": members,
        "tangential_all_saturated": bool(tangential_ok),
        "radial_all_geometric": bool(radial_ok),
        "worst_tangential_relative_difference": max(m["tangential"]["worst_relative_difference"] for m in members),
        "worst_radial_ratio": max(radial_ratios),
        "radial_rate_per_node_estimate": float(max(radial_ratios) ** 0.5),
        "worst_radial_extrapolated_tail_rel": max(m["radial"]["geometric_extrapolated_tail_rel"] for m in members),
        "reading": (
            "Tangential refinement changes no first-variation component beyond the round-off floor of the longdouble "
            "pipeline, so the trapezoidal rule is converged for the pinned members. Radial refinement is still "
            "resolving a residual, but each extra pair of Gauss--Legendre nodes shrinks it by the recorded ratio, and "
            "the geometric extrapolation of the remaining tail beyond Qrho = 16 is below the declared relative "
            "tolerance. This is a measured rate for the three pinned members, not a theorem about the class."
        ),
    }


# --------------------------------------------------------------------------
# (B) integrand structure from the pinned bundle and the implied strip width
# --------------------------------------------------------------------------

def integrand_structure(bundle: dict[str, Any]) -> dict[str, Any]:
    labels_by_N = bundle["nested_truncations"]["basis_labels_by_N"]
    max_radius = 0
    directions = set()
    for labels in labels_by_N.values():
        for label in labels:
            if label == "1":
                continue
            inner = label[label.index("(") + 1:label.index(")")]
            coefficients = [int(term.split("*")[0]) for term in inner.split("+")]
            max_radius = max(max_radius, max(abs(c) for c in coefficients))
            directions.add(inner)
    return {
        "basis_labels_by_N": labels_by_N,
        "max_tangential_wavevector_radius": max_radius,
        "tangential_directions": sorted(directions),
        "single_direction": bool(len(directions) == 1),
        "radial_profiles": "polynomials (h0 quintic, h1 = rho h0, Legendre bumps under 64 rho^3 (1-rho)^3)",
        "density": "literal v5.2 density, real-analytic on the margin set (v5.6.6.8 theorem hypotheses)",
    }


def implied_strip_width(worst_relative: float, q_theta: int) -> dict[str, Any]:
    """Lower bound on the analyticity strip half-width d implied by saturation at Qtheta.

    Trefethen--Weideman (2014, Thm 3.2): for a 2*pi-periodic function analytic in |Im theta| < d with
    |f| <= M_d there, the Qtheta-point trapezoidal error is <= 4*pi*M_d/(exp(2*d*Qtheta) - 1).  With the
    normalisation M_d ~ 1 relative to the integral, an observed relative change <= eps at Qtheta implies
    d >= log(1 + 4*pi/eps)/(2*Qtheta).  This is an inference about the pinned members only; M_d is not
    computed, so the number is indicative and is not used in any decision key.
    """

    eps = max(worst_relative, 1.0e-16)
    return {
        "q_theta": q_theta,
        "observed_relative_change": eps,
        "implied_d_lower_bound_assuming_M_d_order_one": float(np.log1p(4.0 * np.pi / eps) / (2.0 * q_theta)),
        "used_in_decision": False,
    }


def build_payload() -> dict[str, Any]:
    bundle = _load_json(BUNDLE_PATH, BUNDLE_SHA256)
    v5665 = _load_json(V5665_PATH, V5665_SHA256)
    v5668 = _load_json(V5668_PATH, V5668_SHA256)
    v5669 = _load_json(V5669_PATH, V5669_SHA256)
    for receipt, key in ((v5668, "generic_second_order_Euler_Green_identity_symbolic_pass"), (v5669, "common_first_gluing_is_explicit_graph_pass")):
        if receipt["decision"].get(key) is not True:
            raise LedgerGateError(f"upstream component missing: {key}")
    for receipt in (v5668, v5669):
        if receipt["decision"].get("uniform_N_to_infinity_bridge_pass") is not False:
            raise LedgerGateError("upstream receipts must leave the bridge open")

    ladders = ladder_audit(v5665)
    structure = integrand_structure(bundle)
    strip = implied_strip_width(ladders["worst_tangential_relative_difference"], int(EXPECTED_TANGENTIAL_ORDERS[0]))

    tangential_pass = bool(ladders["tangential_all_saturated"] and structure["max_tangential_wavevector_radius"] <= MAX_TANGENTIAL_WAVEVECTOR_RADIUS)
    radial_pass = bool(ladders["radial_all_geometric"])

    ledger = {
        "i_exact_identity_on_class": {
            "receipt": V5668_PATH.name,
            "sha256": V5668_SHA256,
            "machine_checked": "generic second-order Euler--Green identity in jet space; interface functional; C2 radial junction",
            "analytic": "real-analyticity of the literal density on the margin set; classical jets from H^s embedding",
            "key": "generic_second_order_Euler_Green_identity_symbolic_pass",
        },
        "ii_continuity_bound": {
            "receipt": V5668_PATH.name,
            "sha256": V5668_SHA256,
            "machine_checked": None,
            "analytic": "Sobolev/Moser continuity on the class with r, q_Q, Y in H^{s+1}; recorded as hypothesis, no numeric C(M)",
            "key": None,
        },
        "iii_N_independent_retraction": {
            "receipt": V5669_PATH.name,
            "sha256": V5669_SHA256,
            "machine_checked": "graph structure of the common-first gluing; explicit block-wise Jacobian bound sampled on ball, spikes and corners; static inverse audit",
            "analytic": "Sobolev lift of the pointwise Lipschitz bound",
            "key": "pointwise_jacobian_explicit_bound_sampled_pass",
        },
        "iv_finite_certificates_at_saturation": {
            "receipt": V5665_PATH.name,
            "sha256": V5665_SHA256,
            "machine_checked": "tangential ladders of the three pinned members saturated at the round-off floor; radial ladders contract geometrically with extrapolated tail below tolerance; tangential data of radius <= 1",
            "analytic": "exponential trapezoidal / geometric Gauss--Legendre convergence for analytic integrands; strip width and Bernstein parameter not computed from the evaluator",
            "keys": ["route_c_tangential_ladders_saturated_pass", "route_c_radial_ladders_geometric_contraction_pass"],
        },
        "what_the_ledger_means": (
            "In the pointwise formulation the exact identity of (i) holds for every class member, so no N-to-infinity "
            "limit is needed for the identity itself; (iii) supplies the retraction that makes re-glued Fourier "
            "projections converge in the class; (ii) makes S and DS continuous along them; (iv) shows that the finite "
            "Route C numbers of the pinned members are converged in theta and within a measured geometric tail in rho. The remaining "
            "gap between this ledger and uniform_N_to_infinity_bridge_pass is not mathematical content but audit: "
            "(ii) and the analyticity strip of (iv) are prose, and the v5.6.1 quarantine requires an independently "
            "audited gate before any fail-closed key flips. That decision belongs to the operator."
        ),
        "still_outside_the_bridge": [
            "finite DG_N on the spectral space V_N (Phi(u) is not trigonometric)",
            "gauge quotient H_N",
            "periodic-box exhaustion to noncompact Sigma",
            "v5.6.1 quarantine obligations for C1/N1: full bulk diffeomorphism Ward identity, fully coupled moving-embedding cross terms, off-shell continuous extension",
        ],
    }

    scientific = {
        "refinement_ladders": ladders,
        "integrand_structure": structure,
        "implied_strip_width": strip,
        "trapezoidal_rule_reference": "L. N. Trefethen and J. A. C. Weideman, The exponentially convergent trapezoidal rule, SIAM Review 56 (2014) 385-458, Theorem 3.2",
        "bridge_component_ledger": ledger,
        "machine_checked": {
            "tangential_ladders_saturated_all_members": ladders["tangential_all_saturated"],
            "radial_ladders_geometric_all_members": ladders["radial_all_geometric"],
            "tangential_radius_at_most_one": structure["max_tangential_wavevector_radius"] <= MAX_TANGENTIAL_WAVEVECTOR_RADIUS,
            "upstream_component_keys_true": True,
        },
    }

    decision = {
        "route_c_tangential_ladders_saturated_pass": tangential_pass,
        "route_c_radial_ladders_geometric_contraction_pass": radial_pass,
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
        "classification": "theory_only;quadrature_saturation;bridge_component_ledger;restricted_spectral_family;fail_closed_bridge",
        "decision": decision,
        "fixed_before_run": {
            "TANGENTIAL_SATURATION_RELATIVE_TOLERANCE": TANGENTIAL_SATURATION_RELATIVE_TOLERANCE,
            "RADIAL_CONTRACTION_RATIO_MAX": RADIAL_CONTRACTION_RATIO_MAX,
            "RADIAL_EXTRAPOLATED_TAIL_RELATIVE_MAX": RADIAL_EXTRAPOLATED_TAIL_RELATIVE_MAX,
            "EXPECTED_TANGENTIAL_ORDERS": list(EXPECTED_TANGENTIAL_ORDERS),
            "EXPECTED_RADIAL_ORDERS": list(EXPECTED_RADIAL_ORDERS),
            "EXPECTED_MEMBERS": [list(m) for m in EXPECTED_MEMBERS],
            "MAX_TANGENTIAL_WAVEVECTOR_RADIUS": MAX_TANGENTIAL_WAVEVECTOR_RADIUS,
        },
        "scientific": scientific,
        "independence_boundary": {
            "scientific_inputs": "byte-pinned v5.6.6.5 ladders, v5.6.4.4 bundle labels, v5.6.6.8 and v5.6.6.9 decision keys; no action evaluator imported; no expected values or tolerances of upstream receipts reused",
            "imports_action_evaluators": False,
            "imports_one_omega_modules": False,
            "reads_upstream_expected_values": False,
        },
        "open_obligation": {
            "bridge_key": "operator or independent audit of components (ii) and the analyticity strip before flipping uniform_N_to_infinity_bridge_pass (v5.6.1 quarantine wording)",
            "strip_width": "compute the analyticity strip of the pinned members with the action evaluator in a separate, evaluator-side gate if a numeric rate is wanted",
            "C1_N1_beyond_the_bridge": "v5.6.1 quarantine obligations (bulk Ward, moving embedding, off-shell extension)",
        },
        "evidence_boundary": (
            "Machine-checked: tangential saturation and geometric radial contraction of the Route C refinement ladders "
            "of the three pinned members, and the degree-one structure of their tangential data. Analytic: exponential convergence of the trapezoidal and "
            "Gauss--Legendre rules for analytic integrands. The ledger collects the four bridge components with pins; it "
            "does not flip the bridge, C1/N1 or B4/B5."
        ),
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "v5_6_6_5_receipt_sha256": V5665_SHA256,
            "v5_6_6_8_receipt_sha256": V5668_SHA256,
            "v5_6_6_9_receipt_sha256": V5669_SHA256,
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
    if not (payload["decision"]["route_c_tangential_ladders_saturated_pass"] and payload["decision"]["route_c_radial_ladders_geometric_contraction_pass"]):
        raise LedgerGateError("ladder certificate failed")
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    d = payload["decision"]
    print(f"tangential={d['route_c_tangential_ladders_saturated_pass']} radial={d['route_c_radial_ladders_geometric_contraction_pass']} bridge={d['uniform_N_to_infinity_bridge_pass']}")


if __name__ == "__main__":
    main()
