#!/usr/bin/env python3
"""Independent symbolic verification of the existing one-Omega BPS tensor weight.

The canonical charter already states Omega=exp(A), and the existing backreacted
wall generator evaluates the one-sided tensor measure numerically. This module
rechecks that relation, its exact integral, and the TT coordinate transformation
without importing a background generator or parsing any symbolic source text.

The decreasing BPS branch has Omega(0)=1, A(0)=0, Omega in (0,1], and two equal
bulk sides are assumed when quoting M4_bulk_squared. A constant p=0 profile is
normalizable in the bulk measure; its admissibility at the UV wall is unresolved.
No coupled stability, junction, boundary-value solution or finite-momentum DtN
map is certified. The TT equation is the stated Euclidean bulk TT equation,
not a derivation of the complete coupled perturbation operator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

if __package__:
    from . import verify_one_omega_scalar_interface_reparam_v1 as source_oracle
else:
    import verify_one_omega_scalar_interface_reparam_v1 as source_oracle

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CHARTER = source_oracle.CHARTER
OUTPUT = HERE / "artifacts" / "one_omega_bps_tensor_weight_v1.json"
TEST = HERE / "test_one_omega_bps_tensor_weight_v1.py"
SCHEMA = "holo.one-omega-bps-tensor-weight.v1"
canonical_digest = source_oracle.canonical_digest


class BPSTensorWeightError(ValueError):
    """A pinned source, exact identity or receipt failed verification."""


def load_charter(path: Path = CHARTER) -> dict:
    """Reuse the immutable canonical source binding, never its derived model."""
    try:
        return source_oracle.load_charter(path)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise BPSTensorWeightError("canonical charter verification failed") from exc


def _zero(expression: sp.Expr) -> bool:
    return sp.simplify(expression) == 0


def derive_model() -> dict:
    """Exact symbolic branch, measure and TT pullback with independent TT jets."""
    o, a, G, M5c, k = sp.symbols("Omega a G M5c k", positive=True)
    p = sp.Symbol("p", nonnegative=True)
    h0, h1, h2 = sp.symbols("H H_Omega H_OmegaOmega", real=True)
    a_relation = G / (6 * M5c)
    W = 3 * M5c * k * sp.exp(-a * o**2)
    omega_flow_from_W = sp.diff(W, o) / G
    omega_flow = sp.simplify(omega_flow_from_W.subs(G, 6 * M5c * a))
    A_flow = -W / (3 * M5c)
    first_integral_residual = sp.simplify(A_flow - omega_flow / o)
    A = sp.log(o)  # Its integration constant is fixed by A(1)=0.
    dw_domega = -sp.exp(a * o**2) / (k * o)
    distance = (sp.Ei(a) - sp.Ei(a * o**2)) / (2 * k)
    log_remainder_derivative = sp.simplify(dw_domega + 1 / (k * o))
    log_remainder_derivative_limit = sp.limit(log_remainder_derivative, o, 0, dir="+")
    # The orientation reverses: w:0->infinity corresponds to Omega:1->0.
    one_side_density = -sp.exp(2 * A) * dw_domega
    primitive = sp.exp(a * o**2) / (2 * a * k)
    one_side_integral = sp.simplify(primitive.subs(o, 1) - primitive.subs(o, 0))
    M4_bulk_squared = 2 * M5c * one_side_integral
    positive_norm_form = 2 * M5c * sp.exp(a/2) * sp.sinh(a/2) / (k*a)
    G_zero_limit = sp.limit(M4_bulk_squared.subs(a, a_relation), G, 0, dir="+")
    frozen = {G: sp.Rational(6, 5), M5c: sp.S.One, k: sp.S.One}
    frozen_weight = M4_bulk_squared.subs(a, a_relation).subs(frozen)

    # Route one: chain rule in the original w operator, with arbitrary H jets.
    H_w = omega_flow * h1
    H_ww = omega_flow**2 * h2 + omega_flow * sp.diff(omega_flow, o) * h1
    TT_w = H_ww + 4 * A_flow * H_w - p**2 * sp.exp(-2 * A) * h0
    # Route two: differentiate the independently stated divergence-form operator.
    P = o**5 * sp.exp(-a * o**2)
    R = o * sp.exp(a * o**2)
    TT_Omega = P * h2 + sp.diff(P, o) * h1 - p**2 * R * h0 / k**2
    TT_multiplier = k**2 * o**-3 * sp.exp(-a * o**2)
    TT_residual = sp.simplify(TT_w - TT_multiplier * TT_Omega)
    rows = {
        "Omega_flow_from_superpotential": omega_flow + k * o * sp.exp(-a * o**2),
        "A_flow_from_superpotential": A_flow + k * sp.exp(-a * o**2),
        "A_minus_log_Omega_first_integral": first_integral_residual,
        "warp_initial_value": A.subs(o, 1),
        "distance_Jacobian_inverse_flow": dw_domega * omega_flow - 1,
        "distance_primitive_derivative": sp.diff(distance, o) - dw_domega,
        "distance_initial_value": distance.subs(o, 1),
        "logarithmic_distance_remainder_regular": log_remainder_derivative_limit,
        "oriented_tensor_measure": one_side_density - R / k,
        "tensor_measure_primitive": sp.diff(primitive, o) - one_side_density,
        "two_sided_weight_closed_form": M4_bulk_squared - M5c * (sp.exp(a) - 1) / (k * a),
        "tensor_norm_manifest_positive_identity": M4_bulk_squared - positive_norm_form.rewrite(sp.exp),
        "formal_G_to_zero_weight": G_zero_limit - M5c / k,
        "TT_operator_coordinate_pullback": TT_residual,
        "constant_zero_momentum_bulk_profile": TT_Omega.subs({p: 0, h0: 1, h1: 0, h2: 0}),
    }
    residuals = {name: sp.simplify(value) for name, value in rows.items()}
    checks = {name: value == 0 for name, value in residuals.items()}
    checks.update({
        "positive_TT_weights_on_declared_domain": P.is_positive is True and R.is_positive is True,
        "positive_finite_bulk_constant_profile_norm": positive_norm_form.is_positive is True and positive_norm_form.is_finite is True,
        "decreasing_Omega_positive_distance_measure": omega_flow.is_negative is True and (-dw_domega).is_positive is True,
    })
    wrong_friction = H_ww + 3 * A_flow * H_w - p**2 * sp.exp(-2 * A) * h0
    wrong_p_sign = P * h2 + sp.diff(P, o) * h1 + p**2 * R * h0 / k**2
    wrong_weight_exp = P * h2 + sp.diff(P, o) * h1 - p**2 * o * sp.exp(-a * o**2) * h0 / k**2
    mutants = {
        "omitted_second_equal_bulk_side": M4_bulk_squared / 2 - M4_bulk_squared,
        "forgotten_orientation_reversal": -M4_bulk_squared - M4_bulk_squared,
        "TT_friction_three_instead_of_four": TT_w - wrong_friction,
        "TT_Euclidean_momentum_sign_reversed": TT_w - TT_multiplier * wrong_p_sign,
        "TT_weight_exponential_sign_reversed": TT_w - TT_multiplier * wrong_weight_exp,
    }
    negative_residuals = {name: sp.simplify(value) for name, value in mutants.items()}
    negative_controls = {name: value != 0 for name, value in negative_residuals.items()}
    return {
        "symbols": dict(omega=o, a=a, G=G, M5c=M5c, k=k, p=p, H=h0, H_Omega=h1, H_OmegaOmega=h2),
        "a_relation": a_relation, "W": W,
        "omega_flow_from_W": omega_flow_from_W, "omega_flow": omega_flow, "A_flow": A_flow,
        "A": A, "first_integral_residual": first_integral_residual,
        "dw_domega": dw_domega, "distance": distance,
        "log_remainder_derivative": log_remainder_derivative,
        "log_remainder_derivative_limit": log_remainder_derivative_limit,
        "one_side_density": one_side_density, "primitive": primitive,
        "one_side_integral": one_side_integral, "M4_bulk_squared": M4_bulk_squared,
        "G_zero_limit": G_zero_limit, "frozen_weight": frozen_weight,
        "positive_norm_form": positive_norm_form,
        "P": P, "R": R, "TT_w": TT_w, "TT_Omega": TT_Omega,
        "TT_multiplier": TT_multiplier, "TT_residual": TT_residual,
        "residuals": residuals, "checks": checks,
        "negative_control_residuals": negative_residuals, "negative_controls": negative_controls,
    }


def _file_provenance(path: Path) -> dict:
    return {"path": str(path.resolve().relative_to(REPO)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def build_payload(charter_path: Path = CHARTER) -> dict:
    charter = load_charter(charter_path)
    model = derive_model()
    if not all(model["checks"].values()) or not all(model["negative_controls"].values()):
        raise BPSTensorWeightError("an exact check or negative control failed")
    equations = {name: sp.sstr(model[name]) for name in (
        "a_relation", "W", "omega_flow", "A_flow", "A", "dw_domega", "distance",
        "log_remainder_derivative", "one_side_density", "primitive", "one_side_integral",
        "M4_bulk_squared", "positive_norm_form", "G_zero_limit", "P", "R", "TT_w", "TT_Omega", "TT_multiplier")}
    decision = {name: False for name in (
        "physical_massless_graviton_established", "UV_boundary_conditions_solved",
        "junction_conditions_reverified", "finite_momentum_DtN_solved", "TT_spectrum_stability_pass",
        "full_first_variation_pass", "N2_CONSTRAINTS_pass", "N3_CHARACTERISTICS_pass",
        "N4_JUNCTION_BENDING_pass", "N5_COUPLED_BVP_pass", "N6_GLOBAL_STABILITY_pass",
        "N7_LINEAR_REDUCTION_pass", "C4_HESSIAN_pass", "P4_full_same_action_pass", "B4_pass", "B5_pass")}
    decision.update({"bps_flow_tensor_measure_TT_transform_verified": True,
                     "constant_profile_normalizable_in_bulk": True})
    payload = {
        "schema": SCHEMA,
        "source": {
            "path": str(CHARTER.relative_to(REPO)), "sha256": source_oracle.CHARTER_BYTES_SHA256,
            "action_charter_sha256": source_oracle.ACTION_SHA256,
            "calculation_sha256": source_oracle.CALCULATION_SHA256,
            "literal_W": charter["action_charter"]["exact_action"]["superpotential"],
            "existing_background_statement": charter["algebraic_audits"]["background_and_junctions"]["background"],
            "translation": "manual independent symbolic translation; source bytes and semantic digests pinned; no source expressions parsed"},
        "scope": {
            "role": "independent symbolic verification of existing BPS background and tensor weight, plus exact TT measure/operator transformation",
            "domain": "G,M5c,k,a positive; a=G/(6*M5c); 0<Omega<=1; Euclidean p>=0",
            "background": "flat four-dimensional slices; phi^a=0; decreasing BPS branch; Omega(0)=1 and A(0)=0",
            "two_equal_bulk_sides_assumed": True,
            "brane_kinetic_weight_included": False,
            "mass_scale_name": "M4_bulk_squared is the bilateral bulk tensor integral, excluding brane kinetic terms",
            "TT_starting_equation": "H_ww+4*A_w*H_w-p^2*exp(-2*A)*H=0; taken as the bulk TT equation for this background, not derived from all coupled fields here",
            "IR_distance_proof": "w_Omega=-exp(a*Omega^2)/(k*Omega); w(1)=0; for 0<Omega<=1, -log(Omega)/k <= w(Omega) <= -exp(a)*log(Omega)/k, so Omega->0 requires w->infinity",
            "constant_profile_boundary_limit": "The p=0 constant solves the bulk equation and has finite bulk norm. A UV condition can exclude it (for example homogeneous Dirichlet); no physical zero-mode claim follows without that condition.",
            "coupled_stability_inferred": False,
            "numeric_frozen_value_is_proof": False},
        "antecedents": [
            {"path": str(CHARTER.relative_to(REPO)), "location": "algebraic_audits.background_and_junctions.background", "prior_result": "already states Omega=exp(A)"},
            {"path": "first_principles_audit/prediction_factory/derive_backreacted_compensator_wall_gate.py", "location": "tensor_one_side assignment (line 512 when reviewed)", "prior_result": "already evaluates math.expm1(gamma)/(2.0*gamma*k); referenced only, never imported"}],
        "equations": equations,
        "frozen_evaluation": {"parameters": {"G": "6/5", "M5c": "1", "k": "1", "a": "1/5"},
                              "M4_bulk_squared_exact": sp.sstr(model["frozen_weight"]),
                              "M4_bulk_squared_decimal_50_digits": str(sp.N(model["frozen_weight"], 50))},
        "checks": model["checks"],
        "residuals": {name: sp.sstr(value) for name, value in model["residuals"].items()},
        "negative_controls": model["negative_controls"],
        "negative_control_residuals": {name: sp.sstr(value) for name, value in model["negative_control_residuals"].items()},
        "decision": decision,
        "provenance": {"verifier": _file_provenance(Path(__file__)),
                       "test": _file_provenance(TEST),
                       "canonical_source_reader": _file_provenance(Path(source_oracle.__file__)),
                       "sympy_version": sp.__version__},
    }
    payload["calculation_digest"] = {"algorithm": "sha256(canonical-json(payload without calculation_digest))",
                                     "sha256": canonical_digest(payload)}
    return payload


def validate_payload(payload: Any, charter_path: Path = CHARTER) -> None:
    """Recompute the complete receipt; rehashing altered claims does not suffice."""
    if not isinstance(payload, dict) or not isinstance(payload.get("calculation_digest"), dict):
        raise BPSTensorWeightError("receipt and calculation_digest must be dictionaries")
    core = {key: value for key, value in payload.items() if key != "calculation_digest"}
    try:
        digest = canonical_digest(core)
    except (TypeError, ValueError) as exc:
        raise BPSTensorWeightError("receipt is not finite canonical JSON") from exc
    if payload["calculation_digest"].get("sha256") != digest:
        raise BPSTensorWeightError("receipt digest mismatch")
    expected = build_payload(charter_path)
    if canonical_digest(payload) != canonical_digest(expected):
        raise BPSTensorWeightError("receipt differs from recomputed equations, scope or provenance")


def _read_payload(path: Path) -> dict:
    def unique(pairs: list[tuple[str, Any]]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise BPSTensorWeightError("duplicate JSON key")
            result[key] = value
        return result
    def reject_constant(value: str) -> None:
        raise BPSTensorWeightError("non-finite JSON constant")
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique, parse_constant=reject_constant)
    except (OSError, ValueError, UnicodeError) as exc:
        raise BPSTensorWeightError("invalid receipt JSON") from exc
    if not isinstance(value, dict):
        raise BPSTensorWeightError("receipt JSON must be an object")
    return value


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", nargs="?", const=OUTPUT, type=Path,
                       help="create a new receipt exclusively; never overwrite")
    group.add_argument("--verify", type=Path, help="recompute an existing receipt")
    args = parser.parse_args(argv)
    if args.verify:
        payload = _read_payload(args.verify)
        validate_payload(payload)
    else:
        payload = build_payload()
        if args.write:
            with args.write.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"schema": SCHEMA, "checks_passed": sum(payload["checks"].values()),
                      "negative_controls_rejected": sum(payload["negative_controls"].values()),
                      "calculation_sha256": payload["calculation_digest"]["sha256"],
                      "decision": payload["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
