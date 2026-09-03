#!/usr/bin/env python3
"""Additive Gauss-sign corrigendum for the frozen v5.5.4 Ward receipts.

The v5.5.4 primary and red-team computations used a scalar density that is
diffeomorphism covariant, but named its Gauss combination ``Rcal`` with a sign
incompatible with their own definitions of the Riemann tensor and
``K_ab=h_a^c h_b^d nabla_c u_d``.  This file does not rewrite either frozen
receipt.  It records the mismatch with exact manufactured witnesses and keeps
the receipt fail-closed as an intrinsic-curvature dependency of C1/N1.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
PF = Path("first_principles_audit/prediction_factory")
ARTIFACTS = PF / "artifacts"

PRIMARY_SOURCE = PF / (
    "derive_one_omega_topological_so3_interface_diffeomorphism_"
    "khronon_v5_5_4_gate.py"
)
REDTEAM_SOURCE = PF / (
    "derive_one_omega_topological_so3_interface_diffeomorphism_"
    "khronon_v5_5_4_redteam.py"
)
PRIMARY_TEST = PF / (
    "test_one_omega_topological_so3_interface_diffeomorphism_"
    "khronon_v5_5_4_gate.py"
)
REDTEAM_TEST = PF / (
    "test_one_omega_topological_so3_interface_diffeomorphism_"
    "khronon_v5_5_4_redteam.py"
)
PRIMARY_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_interface_diffeomorphism_"
    "khronon_v5_5_4_gate.json"
)
REDTEAM_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_interface_diffeomorphism_"
    "khronon_v5_5_4_redteam.json"
)
V52_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_classical_v5_2_gate.json"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.json"

SCHEMA = "holo.one-omega-topological-so3-v5-5-4-gauss-sign-corrigendum.v1"

PINNED_SHA256 = {
    "v5_5_4_primary_source": "299d07965f0a6feb4f9f577664a7c13f09107fefe85ac80ac6efdf5b0e22c024",
    "v5_5_4_redteam_source": "ddfbd9fc7bb3d50f09bebea927b6a63c1295aa729fa17e88be7bba7cd0f08bab",
    "v5_5_4_primary_test": "2c37ccd958c9bee99d8d3a5b28bd345a22b90786d1b36b33cf01c23477c877c6",
    "v5_5_4_redteam_test": "04a44a3956056ee82da0a87543fd9696b5505e1c7077c35f8a64710a64bc5142",
    "v5_5_4_primary_artifact": "d5e60c535cdfb19aeee7d8007e3c39afcff699e34128ca1a016d4ba4469cd23c",
    "v5_5_4_redteam_artifact": "e1e70a013513ec154f3458891b28bb77a47739bcc264b571935cac1f06d1ade7",
    "v5_2_artifact": "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
}

PINNED_PATHS = {
    "v5_5_4_primary_source": PRIMARY_SOURCE,
    "v5_5_4_redteam_source": REDTEAM_SOURCE,
    "v5_5_4_primary_test": PRIMARY_TEST,
    "v5_5_4_redteam_test": REDTEAM_TEST,
    "v5_5_4_primary_artifact": PRIMARY_ARTIFACT,
    "v5_5_4_redteam_artifact": REDTEAM_ARTIFACT,
    "v5_2_artifact": V52_ARTIFACT,
}

PRIMARY_WRONG_FORMULA = "projected_ambient_R + K_trace * K_trace - K_squared"
REDTEAM_WRONG_FORMULA = (
    "scalar_r\n        + 2.0 * (u_up @ ricci @ u_up)\n"
    "        + k_trace * k_trace\n        - k_squared"
)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def _source_pins() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for name, relative_path in PINNED_PATHS.items():
        observed = _sha256_bytes((REPO / relative_path).read_bytes())
        expected = PINNED_SHA256[name]
        if observed != expected:
            raise RuntimeError(
                f"frozen input drift for {relative_path}: {observed} != {expected}"
            )
        result[name] = {"path": relative_path.as_posix(), "sha256": observed}
    return result


def _verify_mismatched_implementations_are_present() -> dict[str, bool]:
    primary = (REPO / PRIMARY_SOURCE).read_text(encoding="utf-8")
    redteam = (REPO / REDTEAM_SOURCE).read_text(encoding="utf-8")
    primary_artifact = json.loads((REPO / PRIMARY_ARTIFACT).read_text(encoding="utf-8"))
    redteam_artifact = json.loads((REPO / REDTEAM_ARTIFACT).read_text(encoding="utf-8"))
    return {
        "primary_source_contains_opposite_Gauss_sign": PRIMARY_WRONG_FORMULA in primary,
        "redteam_source_contains_same_opposite_Gauss_sign": REDTEAM_WRONG_FORMULA in redteam,
        "primary_receipt_kept_C1_false": primary_artifact["decision"]["C1_ACTION_pass"] is False,
        "primary_receipt_kept_N1_false": primary_artifact["decision"]["N1_ACTION_pass"] is False,
        "redteam_receipt_kept_C1_false": redteam_artifact["decision"]["C1_ACTION_pass"] is False,
        "redteam_receipt_kept_N1_false": redteam_artifact["decision"]["N1_ACTION_pass"] is False,
    }


def _flat_flrw_witness() -> dict[str, Any]:
    """Exact point witness for ds^2=-dt^2+a(t)^2 delta_ij dx^i dx^j."""

    H = Fraction(2, 5)
    Hdot = Fraction(-1, 7)
    projected_R = 6 * H * H
    K_trace_squared = 9 * H * H
    K_tensor_squared = 3 * H * H
    R4 = 6 * (Hdot + 2 * H * H)
    Ricci_uu = -3 * (Hdot + H * H)
    projected_from_ricci = R4 + 2 * Ricci_uu
    corrected = projected_R - K_trace_squared + K_tensor_squared
    inherited = projected_R + K_trace_squared - K_tensor_squared
    return {
        "family": "spatially_flat_FLRW_at_one_point",
        "parameters": {"H": _fraction_record(H), "Hdot": _fraction_record(Hdot)},
        "projected_ambient_R": _fraction_record(projected_R),
        "R4": _fraction_record(R4),
        "Ricci_uu": _fraction_record(Ricci_uu),
        "R4_plus_2_Ricci_uu": _fraction_record(projected_from_ricci),
        "K_trace_squared": _fraction_record(K_trace_squared),
        "K_tensor_squared": _fraction_record(K_tensor_squared),
        "correct_intrinsic_R_leaf": _fraction_record(corrected),
        "v5_5_4_inherited_combination": _fraction_record(inherited),
        "checks": {
            "projected_routes_agree_exactly": projected_from_ricci == projected_R,
            "flat_leaf_has_zero_intrinsic_curvature": corrected == 0,
            "inherited_v5_5_4_formula_is_nonzero": inherited != 0,
        },
    }


def _static_round_s3_witness() -> dict[str, Any]:
    """Exact time-product witness R x S^3(a), with K_ab=0."""

    radius = Fraction(3, 2)
    expected = 6 / (radius * radius)
    projected_R = expected
    K_trace_squared = Fraction(0)
    K_tensor_squared = Fraction(0)
    corrected = projected_R - K_trace_squared + K_tensor_squared
    return {
        "family": "static_product_time_x_round_S3_at_one_point",
        "parameters": {"radius": _fraction_record(radius)},
        "projected_ambient_R": _fraction_record(projected_R),
        "K_trace_squared": _fraction_record(K_trace_squared),
        "K_tensor_squared": _fraction_record(K_tensor_squared),
        "correct_intrinsic_R_leaf": _fraction_record(corrected),
        "expected_round_S3_scalar": _fraction_record(expected),
        "checks": {
            "positive_curvature_sign_fixed": corrected > 0,
            "round_S3_value_exact": corrected == expected,
        },
    }


def build_payload() -> dict[str, Any]:
    implementation_checks = _verify_mismatched_implementations_are_present()
    flrw = _flat_flrw_witness()
    sphere = _static_round_s3_witness()
    witness_checks = {
        "flat_FLRW_witness_pass": all(flrw["checks"].values()),
        "static_round_S3_witness_pass": all(sphere["checks"].values()),
    }
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "title": "Additive Gauss-sign corrigendum for v5.5.4",
        "classification": "theory_only;manufactured_exact_witness;additive_corrigendum;fail_closed",
        "source_pins": _source_pins(),
        "conventions": {
            "signature": "(-,+,+,+)",
            "Riemann": (
                "R^rho_{ sigma mu nu}=partial_mu Gamma^rho_{nu sigma}-"
                "partial_nu Gamma^rho_{mu sigma}+Gamma^rho_{mu lambda}"
                "Gamma^lambda_{nu sigma}-Gamma^rho_{nu lambda}Gamma^lambda_{mu sigma}"
            ),
            "unit_normal": "u_mu u^mu=-1",
            "projector": "h_mu_nu=gamma_mu_nu+u_mu u_nu",
            "extrinsic_curvature": "K_mu_nu=h_mu^a h_nu^b nabla_a u_b",
            "correct_Gauss_scalar": (
                "R_leaf=h^ac h^bd R_abcd-K^2+K_ab K^ab="
                "R4+2 Ricci(u,u)-K^2+K_ab K^ab"
            ),
            "v5_5_4_opposite_combination": (
                "h^ac h^bd R_abcd+K^2-K_ab K^ab"
            ),
        },
        "manufactured_witnesses": {
            "flat_FLRW": flrw,
            "static_round_S3": sphere,
        },
        "checks": {
            **implementation_checks,
            **witness_checks,
            "all_frozen_input_pins_verified": True,
            "v5_5_4_intrinsic_Rcal_binding_pass": False,
            "v5_5_4_eligible_as_intrinsic_Rcal_dependency_for_C1_N1": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "decision": {
            "Gauss_sign_mismatch_reproduced": all(implementation_checks.values())
            and all(witness_checks.values()),
            "v5_5_4_Ward_result_retracted": False,
            "v5_5_4_Ward_scope_after_corrigendum": (
                "the off-shell Ward/Stokes calculation remains evidence for covariance "
                "of the scalar density it actually implemented; it is not a certificate "
                "that this scalar equals the intrinsic leaf curvature in the v5.2 action"
            ),
            "v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma": False,
            "corrected_action_route_execution_authorized": all(witness_checks.values()),
            "C1_N1_promotion_authorized": False,
        },
        "open_obligations": [
            "bind the corrected Gauss convention in the additive pointwise primitive contract",
            "verify two independent action routes on the same N2 member and free tangent",
            "retain pointwise gluing at all action quadrature nodes",
            "establish derivative, quadrature, radial and spectral convergence",
            "run mutants and an independent clean-process red-team",
        ],
    }
    payload["payload_sha256"] = _sha256_bytes(_canonical_bytes(payload))
    return payload


def render_payload(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def main() -> None:
    payload = build_payload()
    destination = REPO / OUTPUT
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(render_payload(payload))
    print(destination)
    print(_sha256_bytes(destination.read_bytes()))


if __name__ == "__main__":
    main()
