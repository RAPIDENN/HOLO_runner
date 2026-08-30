#!/usr/bin/env python3
"""Place the Legendre selector in the existing scalar--matter interface.

The certified conditional interface is written in Einstein variables,

    S_E = integral sqrt(-g_E)[M_Pl^2 R_E/2 - (dphi)^2/2 - U_E(phi)]
          + S_m[A_m(phi)^2 g_E, Psi].

Define the matter/Jordan metric g_J=A_m^2 g_E and selector s=A_m^-2.  Then
matter is minimally coupled while the curvature coefficient is M_Pl^2 s/2.
Thus s occupies exactly the field-dependent gravitational-stiffness slot that
the Legendre collector needs; it need not be a particle number or chemical
variable.  The full conformal transformation also generates scalar-gradient
and metric-mixing terms, so this is an embedding route, not yet an AQUAL
derivation.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
INTERFACE = REPO / "first_principles_audit/artifacts/interface_action_derivation.json"
ENVELOPE = HERE / "artifacts" / "collector_legendre_envelope.json"
OUTPUT = HERE / "artifacts" / "jordan_selector_embedding.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def exponential_frame_map(
    phi_over_mpl: np.ndarray, beta: float
) -> dict[str, np.ndarray]:
    """Evaluate the local frame map for ln A=beta*phi/M_Pl."""

    q = np.asarray(phi_over_mpl, dtype=float)
    if np.any(~np.isfinite(q)) or not np.isfinite(beta):
        raise ValueError("frame-map inputs must be finite")
    conformal = np.exp(beta * q)
    selector = np.exp(-2.0 * beta * q)
    derivative = -2.0 * beta * selector
    return {"A_m": conformal, "s": selector, "ds_dq": derivative}


def jordan_kinetic_coefficient(selector: np.ndarray, beta: float) -> np.ndarray:
    """Return Z_J/M_Pl^2 for an exponential Einstein-frame matter factor.

    The Jordan action convention is

        integral sqrt(-g_J)[M_Pl^2*s*R_J/2 - Z_J(s)(ds)^2/2 - U_J].

    Conformal mixing makes the combined Einstein-frame scalar healthy even
    when Z_J alone is negative.
    """

    s = np.asarray(selector, dtype=float)
    if np.any(s <= 0.0) or not np.isfinite(beta) or beta == 0.0:
        raise ValueError("positive selector and nonzero finite beta required")
    return (1.0 / (4.0 * beta * beta) - 1.5) / s


def build() -> dict[str, Any]:
    interface = _read(INTERFACE)
    envelope = _read(ENVELOPE)
    if interface["passes"]["all"] is not True:
        raise RuntimeError("interface action must pass first")
    if envelope["passes"]["all"] is not True:
        raise RuntimeError("collector envelope must pass first")

    q = np.linspace(-0.7, 0.9, 128)
    beta = 0.13
    frame = exponential_frame_map(q, beta)
    selector_identity_error = float(
        np.max(np.abs(frame["s"] * np.square(frame["A_m"]) - 1.0))
    )
    derivative_error = float(
        np.max(
            np.abs(
                np.gradient(frame["s"], q, edge_order=2) - frame["ds_dq"]
            )
        )
    )
    kinetic = jordan_kinetic_coefficient(frame["s"], beta)
    # Transforming back to Einstein variables must recover unit canonical
    # coefficient: s*Z_J/M_Pl^2 + 3/2 = (dq/ds)^2*s^2 = 1/(4 beta^2).
    canonical_identity = frame["s"] * kinetic + 1.5
    canonical_error = float(
        np.max(np.abs(canonical_identity - 1.0 / (4.0 * beta * beta)))
    )

    checks = {
        "certified_inputs": True,
        # exp(x)*exp(-x) is evaluated through two rounded arrays, so allow a
        # small multiple of binary64 epsilon rather than demanding sub-epsilon
        # cancellation.
        "matter_metric_identity": bool(
            selector_identity_error < 8.0 * np.finfo(float).eps
        ),
        "selector_derivative_identity": derivative_error < 3.0e-6,
        "canonical_frame_kinetic_identity": canonical_error < 3.0e-14,
        "selector_is_positive": bool(np.min(frame["s"]) > 0.0),
        "collector_dual_is_convex": envelope["passes"][
            "dual_is_strictly_increasing"
        ],
        "no_observational_tables_read": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "nonlinear_A_m_of_phi_derived": False,
        "selector_range_zero_to_one_reached_on_healthy_branch": False,
        "jordan_scalar_gradient_terms_negligible_or_correctly_included": False,
        "weak_field_constraint_reduction_equals_local_s_times_X": False,
        "jordan_potential_equals_required_W_of_s": False,
        "a0_and_absolute_normalization_derived": False,
        "post_newtonian_and_lensing_response_derived": False,
        "physical_completion": False,
    }

    return {
        "schema": "holo.jordan-selector-embedding.v1",
        "title": "Jordan-frame embedding of the nonlinear collector selector",
        "classification": (
            "existing_interface_contains_selector_slot;nonlinear_embedding_not_derived"
        ),
        "sources": {
            "interface_action": {
                "path": str(INTERFACE.relative_to(REPO)),
                "sha256": _sha256(INTERFACE),
            },
            "collector_envelope": {
                "path": str(ENVELOPE.relative_to(REPO)),
                "sha256": _sha256(ENVELOPE),
            },
            "observational_inputs_read": [],
        },
        "frame_derivation": {
            "einstein_matter_metric": "g_J=A_m(phi)^2*g_E",
            "selector_definition": "s(phi)=A_m(phi)^(-2)",
            "metric_inverse": "g_E=s*g_J",
            "matter_action": "S_m[g_J,Psi]",
            "curvature_term": "sqrt(-g_J)*M_Pl^2*s*R_J/2",
            "jordan_potential": "U_J(s)=s^2*U_E(phi(s))",
            "jordan_kinetic": (
                "Z_J(s)=s*(dphi/ds)^2-(3/2)*M_Pl^2/s; "
                "for ln A=beta*phi/M_Pl, Z_J/M_Pl^2="
                "[1/(4 beta^2)-3/2]/s"
            ),
        },
        "collector_embedding": {
            "required_constraint_reduced_target": (
                "S_target=-M_Pl^2*integral[s*|grad Phi|^2-a0^2*W_J(s)]"
                "-integral[rho*Phi], with M_Pl^2=1/(8*pi*G)"
            ),
            "selector_variation_if_auxiliary": (
                "X=W_J'(s), X=|grad Phi|^2/a0^2"
            ),
            "matter_source_variation": "div[s*grad(Phi)]=4*pi*G*rho",
            "simple_potential_matching": (
                "Because the covariant action contains -U_J while the target "
                "contains +M_Pl^2*a0^2*W_J, a direct auxiliary identification "
                "would require U_J=-M_Pl^2*a0^2*W_J; stability and constraint "
                "contributions must therefore be checked rather than assumed."
            ),
            "physical_meaning": (
                "s is a local gravitational stiffness/constitutive response, "
                "not an occupation number; matter still couples through rho*Phi"
            ),
            "target_relation": (
                "The s*R_J term does not by itself imply the displayed target. "
                "The exact collector follows only if the lapse, shift, second "
                "potential and scalar constraints reduce the Jordan action to "
                "that normalization and sign, yield W_J(s)=W_target(s), control "
                "the extra gradient terms, and span the healthy s branch."
            ),
        },
        "failure_diagnosis_of_previous_linear_routes": [
            (
                "Expanding ln A_m only to beta*phi/M_Pl freezes the constitutive "
                "coefficient around one background and produces Yukawa exchange."
            ),
            (
                "The deep target requires s to approach zero, an order-one "
                "departure from s=1; for an exponential frame map this lies at "
                "large positive phi and cannot survive a small-field truncation."
            ),
            (
                "A finite fixed tower remains linear in source mass and therefore "
                "cannot generate the deep sqrt(M) law."
            ),
            (
                "In the soft gamma limit the generalized-normalized endpoint "
                "profiles vanish with mu0, so treating each pole as an additive "
                "force suppresses rather than collectivizes the response."
            ),
            (
                "The nonlinear route must derive the full field dependence of "
                "A_m and the constraint-reduced metric stiffness before "
                "linearizing around a galaxy."
            ),
        ],
        "numerical_identity_check": {
            "test_beta": beta,
            "samples": int(q.size),
            "selector_times_A_squared_max_error": selector_identity_error,
            "selector_derivative_max_error": derivative_error,
            "canonical_kinetic_identity_max_error": canonical_error,
        },
        "physical_gates": physical_gates,
        "decisive_next_calculation": (
            "Choose or derive a complete nonlinear A_m(phi), transform the "
            "five-dimensional light-mode effective action to the matter frame, "
            "eliminate lapse/shift and scalar constraints without a weak-field "
            "Taylor truncation, and read the resulting W_J(s), slip and lensing."
        ),
        "checks": checks,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print("[selector] s=A_m^-2 places the local state in the curvature coefficient")
    print(f"[physical completion] {result['physical_gates']['physical_completion']}")
    print(f"[embedding certificate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
