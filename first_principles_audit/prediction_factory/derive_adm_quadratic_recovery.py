#!/usr/bin/env python3
"""Recover the certified scalar S2 operator from the exact radial ADM seed.

The check uses compact radial envelopes and periodic four-dimensional test
fields.  It substitutes the linear momentum constraint for the lapse, keeps
the scalar shift explicit, and verifies that the unreduced ADM density differs
from the compact quadratic action only by integrated total derivatives.  No
observational inputs or nonlinear coefficients enter.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import simpson


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "adm_quadratic_recovery.json"
INPUTS = {
    "effective_action": REPO
    / "first_principles_audit/artifacts/holo_effective_action.json",
    "adm_quartic_seed": HERE / "artifacts/radial_adm_quartic_seed.json",
    "gauge_invariant_route": HERE / "artifacts/gauge_invariant_cubic_route.json",
}
CRITERIA = {
    "background_weight_identity_max_relative": 1.0e-12,
    "integrated_quadratic_action_max_relative": 1.0e-9,
    "shift_independence_max_relative": 1.0e-12,
}


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


def _integrated_raw_S2(
    *,
    u: np.ndarray,
    warp: np.ndarray,
    warp_u: np.ndarray,
    chi_u: np.ndarray,
    potential: np.ndarray,
    envelope: np.ndarray,
    envelope_u: np.ndarray,
    wave_number: int,
    beta_amplitude: np.ndarray,
    x_samples: int = 64,
) -> float:
    """Integrate the epsilon^2 coefficient of the exact ADM density."""

    x = np.arange(x_samples, dtype=float) * (2.0 * np.pi / x_samples)
    cosine = np.cos(wave_number * x)[None, :]
    sine = np.sin(wave_number * x)[None, :]
    zeta = envelope[:, None] * cosine
    zeta_u = envelope_u[:, None] * cosine
    alpha = zeta_u / warp_u[:, None]
    zeta_x = -wave_number * envelope[:, None] * sine
    beta_x = -wave_number * beta_amplitude[:, None] * sine
    beta_xx = -(wave_number**2) * beta_amplitude[:, None] * cosine
    box_zeta = -(wave_number**2) * zeta

    exp_minus_two_A = np.exp(-2.0 * warp)[:, None]
    shift_trace_1 = exp_minus_two_A * beta_xx
    shift_trace_2 = exp_minus_two_A * (
        2.0 * zeta_x * beta_x - 2.0 * zeta * beta_xx
    )
    radial_0 = 12.0 * warp_u[:, None] ** 2 - 0.5 * chi_u[:, None] ** 2
    radial_1 = (
        24.0 * warp_u[:, None] * zeta_u
        - 6.0 * warp_u[:, None] * shift_trace_1
    )
    # For a single plane-wave direction, (tr B1)^2-tr(B1^2)=0.
    radial_2 = (
        12.0 * zeta_u**2
        - 6.0 * warp_u[:, None] * shift_trace_2
        - 6.0 * zeta_u * shift_trace_1
    )
    ricci_1 = -6.0 * exp_minus_two_A * box_zeta
    ricci_2 = exp_minus_two_A * (
        -6.0 * zeta_x**2 + 12.0 * zeta * box_zeta
    )

    coefficient = np.exp(4.0 * warp)[:, None] * (
        ricci_2
        + alpha * ricci_1
        + 4.0 * zeta * ricci_1
        + radial_2
        - alpha * radial_1
        + alpha**2 * radial_0
        + 4.0 * zeta * (radial_1 - alpha * radial_0)
        + 8.0 * zeta**2 * radial_0
        - potential[:, None] * (8.0 * zeta**2 + 4.0 * zeta * alpha)
    )
    return float(simpson(np.mean(coefficient, axis=1), x=u))


def _periodic_backward_check(effective: Mapping[str, Any]) -> dict[str, Any]:
    u = np.asarray(effective["u"], dtype=float)
    warp = np.asarray(effective["A"], dtype=float)
    warp_u = np.asarray(effective["A_u"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)
    potential = np.asarray(effective["potential_V_of_phi"], dtype=float)
    epsilon = chi_u**2 / (6.0 * warp_u**2)
    coordinate = (u - u[0]) / (u[-1] - u[0])
    rows: list[dict[str, float | int]] = []
    shift_differences: list[float] = []

    for power in (2, 3, 4):
        envelope = np.sin(np.pi * coordinate) ** power
        envelope_u = (
            power
            * np.sin(np.pi * coordinate) ** (power - 1)
            * np.cos(np.pi * coordinate)
            * np.pi
            / (u[-1] - u[0])
        )
        for wave_number in (1, 2, 3):
            constrained_beta = (
                envelope / warp_u
                - np.exp(2.0 * warp)
                * epsilon
                * envelope_u
                / wave_number**2
            )
            raw = _integrated_raw_S2(
                u=u,
                warp=warp,
                warp_u=warp_u,
                chi_u=chi_u,
                potential=potential,
                envelope=envelope,
                envelope_u=envelope_u,
                wave_number=wave_number,
                beta_amplitude=constrained_beta,
            )
            radial = float(
                simpson(
                    0.5 * np.exp(4.0 * warp) * epsilon * envelope_u**2,
                    x=u,
                )
            )
            transverse = float(
                simpson(
                    0.5
                    * np.exp(2.0 * warp)
                    * epsilon
                    * (wave_number * envelope) ** 2,
                    x=u,
                )
            )
            reduced = -3.0 * (radial + transverse)
            relative = abs(raw - reduced) / max(abs(raw), abs(reduced), 1.0e-300)

            arbitrary_beta = 0.37 * envelope
            raw_arbitrary_shift = _integrated_raw_S2(
                u=u,
                warp=warp,
                warp_u=warp_u,
                chi_u=chi_u,
                potential=potential,
                envelope=envelope,
                envelope_u=envelope_u,
                wave_number=wave_number,
                beta_amplitude=arbitrary_beta,
            )
            shift_relative = abs(raw_arbitrary_shift - raw) / max(
                abs(raw_arbitrary_shift), abs(raw), 1.0e-300
            )
            shift_differences.append(shift_relative)
            rows.append(
                {
                    "envelope_power": power,
                    "wave_number": wave_number,
                    "raw_ADM_S2": raw,
                    "reduced_S2": reduced,
                    "relative_error": relative,
                    "shift_independence_relative": shift_relative,
                }
            )
    return {
        "periodic_x_samples": 64,
        "radial_samples": int(u.size),
        "rows": rows,
        "maximum_relative_error": max(float(row["relative_error"]) for row in rows),
        "maximum_shift_independence_relative": max(shift_differences),
    }


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    effective = payloads["effective_action"]
    adm = payloads["adm_quartic_seed"]
    gauge = payloads["gauge_invariant_route"]
    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective action is not certified")
    if adm.get("checks", {}).get("all") is not True:
        raise RuntimeError("ADM seed is not certified")
    if gauge.get("checks", {}).get("all") is not True:
        raise RuntimeError("gauge-invariant route is not certified")

    warp = np.asarray(effective["A"], dtype=float)
    warp_u = np.asarray(effective["A_u"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)
    epsilon = chi_u**2 / (6.0 * warp_u**2)
    p = np.exp(4.0 * warp) * epsilon
    w = np.exp(2.0 * warp) * epsilon
    superpotential = -6.0 * warp_u
    rho_bmp = 4.0 * np.exp(4.0 * warp) * chi_u**2 / superpotential**2
    bmp_mass_weight = rho_bmp * np.exp(-2.0 * warp)
    p_relative = float(
        np.max(np.abs(rho_bmp - (2.0 / 3.0) * p) / np.maximum(p, 1.0e-300))
    )
    w_relative = float(np.max(
        np.abs(bmp_mass_weight - (2.0 / 3.0) * w)
        / np.maximum(w, 1.0e-300)
    ))
    backward = _periodic_backward_check(effective)

    checks = {
        "certified_inputs": True,
        "no_observational_tables_read": True,
        "ADM_weights_equal_certified_p_and_w": bool(
            max(p_relative, w_relative)
            < CRITERIA["background_weight_identity_max_relative"]
        ),
        "unreduced_ADM_S2_equals_reduced_action": backward["maximum_relative_error"]
        < CRITERIA["integrated_quadratic_action_max_relative"],
        "scalar_shift_drops_after_momentum_constraint": backward[
            "maximum_shift_independence_relative"
        ]
        < CRITERIA["shift_independence_max_relative"],
        "compact_envelopes_remove_radial_endpoint_terms": True,
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "same_variable_bulk_ADM_S2_action_recovered_on_compact_support": True,
        "compact_master_ADM_S2_including_endpoints_recovered": False,
        "same_variable_ADM_S2_master_action_recovered": False,
        "linear_lapse_constraint_substituted": True,
        "linear_scalar_shift_constraint_formula_identified": True,
        "linear_scalar_shift_constraint_independently_tested": False,
        "certified_Sturm_Liouville_operator_recovered": True,
        "absolute_bulk_normalization_in_terms_of_kappa5_identified": True,
        "absolute_matter_coupling_normalization_fixed": False,
        "nonlinear_lapse_shift_constraints_solved": False,
        "physical_S3_projected": False,
    }

    return {
        "schema": "holo.adm-quadratic-recovery.v1",
        "title": "Backward recovery of the certified S2 operator from radial ADM",
        "classification": (
            "same_variable_bulk_ADM_S2_compact_support_recovered;"
            "endpoint_S2_and_nonlinear_constraints_pending"
        ),
        "linear_constraints": {
            "momentum": "alpha1=zeta'/A'",
            "hamiltonian": (
                "box(beta1)=box(zeta)/A'+exp(2A)*epsilon_ED*zeta'"
            ),
            "epsilon_ED": "chi_bar'^2/(6*A'^2)=-A''/A'^2",
            "shift_role": (
                "Once alpha1 satisfies the momentum constraint, beta1 multiplies "
                "that constraint and drops from the integrated S2 action. The "
                "Hamiltonian equation fixes beta1 for reconstruction."
            ),
        },
        "reduced_action": {
            "result": (
                "S2=-(3/(2*kappa5^2))*integral du d4x "
                "[p*(zeta')^2+w*partial_mu(zeta)*partial^mu(zeta)]"
            ),
            "p": "exp(4A)*epsilon_ED",
            "w": "exp(2A)*epsilon_ED",
            "equation": "-(p*f')'=m^2*w*f",
            "canonical_mode_if_integral_w_f2_is_one": (
                "Q_n=sqrt(3)*q_n/kappa5 before restoring the dimensional ell factors"
            ),
        },
        "BMP_convention_bridge": {
            "isotropic_unitary_representative": (
                "delta_gamma_mn=2*zeta*gamma_bar_mn gives h_R=8*zeta, "
                "h_BMP=6*zeta and tilde_a=3*zeta/2"
            ),
            "field_map": "zeta=(2/3)*tilde_a",
            "weight_map": "rho_BMP=(2/3)*p; rho_BMP*exp(-2A)=(2/3)*w",
            "consequence": (
                "The constant field and weight maps reproduce the same local "
                "Sturm-Liouville operator. They do not yet fix a brane matter residue."
            ),
        },
        "verification": {
            "p_weight_max_relative": float(p_relative),
            "w_weight_max_relative": float(w_relative),
            "periodic_compact_support_backward_test": backward,
        },
        "physical_gates": physical_gates,
        "checks": checks,
        "criteria": CRITERIA,
        "inputs": {
            "observational_tables_read": [],
            "files": {
                name: {
                    "path": str(path.relative_to(REPO)),
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
        },
        "next_decisive_test": (
            "Solve alpha2 and beta2, include the second-order transverse/TT closure "
            "test, and verify that the ADM cubic bulk source agrees with the "
            "independent BMP oracle before adding physical endpoints."
        ),
        "evidence_boundary": (
            "This closes the mandatory ADM-to-S2 bulk backward test for compactly "
            "supported probes, including the overall bulk normalization in terms "
            "of kappa5. It does not rederive the two finite-endpoint Neumann action, "
            "independently test the beta reconstruction formula, derive S3, S4 or a force."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        raise SystemExit("ADM quadratic recovery certificate failed")
    _write(OUTPUT, result)
    backward = result["verification"]["periodic_compact_support_backward_test"]
    print(f"[artifact] {OUTPUT}")
    print(f"[ADM S2 max relative] {backward['maximum_relative_error']:.3e}")
    print(
        "[same-variable S2 recovered] "
        f"{result['physical_gates']['same_variable_bulk_ADM_S2_action_recovered_on_compact_support']}"
    )
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
