#!/usr/bin/env python3
"""Audit the legacy Ricci-clock and Wilson-scale interface.

The purpose of this module is deliberately narrow.  It recomputes the 5D
curvature from the certified effective Einstein--scalar completion, checks it
against an independent trace identity, and classifies the old clock and
``sigma_eff`` artefacts without treating either one as a physical detection.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import UnivariateSpline


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
EFFECTIVE_PATH = HERE / "artifacts" / "holo_effective_action.json"
MINIMAL_PATH = HERE / "artifacts" / "minimal_probe_completion.json"
LEGACY_CLOCK_PATH = (
    REPO_ROOT
    / "A_single_Einstein_Dilaton geometry"
    / "artifacts"
    / "ed_bulk_clock.json"
)
LEGACY_WILSON_PATH = (
    REPO_ROOT
    / "instrument_closure"
    / "2026-01-04"
    / "wilson_loop_sigma_from_ed_trace.json"
)
LEGACY_LOCK5_PATH = REPO_ROOT / "data" / "internal" / "lock5_ricci_results.json"
RAW_TRACE_PATH = Path(
    "/home/debian/work/repos/HOLO_TRANSDUCTOR_instrument/"
    "data/internal/holo_physics_trace_ed_industrial.json"
)
OUTPUT_PATH = HERE / "artifacts" / "ricci_wilson_interface_audit.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _crossings(x: np.ndarray, derivative: np.ndarray, kind: str) -> list[float]:
    if kind == "minimum":
        mask = (derivative[:-1] < 0.0) & (derivative[1:] >= 0.0)
    elif kind == "maximum":
        mask = (derivative[:-1] > 0.0) & (derivative[1:] <= 0.0)
    else:
        raise ValueError(kind)
    return [float(x[i]) for i in np.flatnonzero(mask)]


def audit() -> dict[str, Any]:
    effective = _load(EFFECTIVE_PATH)
    minimal = _load(MINIMAL_PATH)
    legacy_clock = _load(LEGACY_CLOCK_PATH)["series"]
    legacy_wilson = _load(LEGACY_WILSON_PATH)
    legacy_lock5 = _load(LEGACY_LOCK5_PATH)
    raw_trace = _load(RAW_TRACE_PATH)["trace"]

    if not effective["summary"]["passes"]["all"]:
        raise RuntimeError("Effective-action certificate does not pass")
    if not minimal["passes"]["all"]:
        raise RuntimeError("Minimal probe certificate does not pass")

    u = np.asarray(effective["u"], dtype=float)
    warp = np.asarray(effective["A"], dtype=float)
    warp_u = np.asarray(effective["A_u"], dtype=float)
    phi_u = np.asarray(effective["phi_u"], dtype=float)
    kinetic = np.asarray(effective["kinetic_K_of_phi"], dtype=float)
    potential = np.asarray(effective["potential_V_of_phi"], dtype=float)
    chi = np.asarray(effective["canonical_chi"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)

    # Domain-wall gauge: ds^2=e^(2A) eta dx dx + ell^2 du^2.  The arrays below
    # are dimensionless; the physical scalar curvature is R5_hat/ell^2.
    warp_uu = -kinetic * np.square(phi_u) / 6.0
    ricci_geometry = -8.0 * warp_uu - 20.0 * np.square(warp_u)
    ricci_trace_identity = 0.5 * np.square(chi_u) + (5.0 / 3.0) * potential
    ricci_identity_error = ricci_geometry - ricci_trace_identity

    # Independent coordinate realization.  With dz_c/du=exp(-A), the metric is
    # conformally flat and R5_hat=exp(-2A)(-8 A_zz-12 A_z^2).
    z_conformal = cumulative_trapezoid(np.exp(-warp), u, initial=0.0)
    warp_z = np.exp(warp) * warp_u
    warp_zz = np.exp(2.0 * warp) * (warp_uu + np.square(warp_u))
    ricci_conformal = np.exp(-2.0 * warp) * (
        -8.0 * warp_zz - 12.0 * np.square(warp_z)
    )
    ricci_coordinate_error = ricci_geometry - ricci_conformal

    # The historical trace stores dA=dA/d(log u), while the profile obeys
    # A_u=u*dA.  Reproducing the old R5 is therefore possible by incorrectly
    # treating the stored dA as A_u.  This is an audit of provenance, not a new
    # definition of curvature.
    raw_u = np.asarray(raw_trace["z"], dtype=float)
    raw_d_a = np.asarray(raw_trace["dA"], dtype=float)
    d_a_spline = UnivariateSpline(raw_u, raw_d_a, k=5, s=0.0)
    relation_error = warp_u - u * d_a_spline(u)

    clock_u = np.asarray(legacy_clock["z"], dtype=float)
    clock_ricci = np.asarray(legacy_clock["R5"], dtype=float)
    clock_e = np.asarray(legacy_clock["E"], dtype=float)
    clock_mask = (clock_u >= u[0]) & (clock_u <= u[-1])
    clock_u_common = clock_u[clock_mask]
    clock_ricci_common = clock_ricci[clock_mask]
    corrected_on_clock = np.interp(clock_u_common, u, ricci_geometry)
    legacy_as_stored_derivative = (
        -8.0 * d_a_spline(clock_u_common, 1)
        - 20.0 * np.square(d_a_spline(clock_u_common))
    )

    legacy_minus_corrected = clock_ricci_common - corrected_on_clock
    legacy_reproduction_error = clock_ricci_common - legacy_as_stored_derivative

    clock_slice = u >= 1.0
    u_clock = u[clock_slice]
    a_clock = warp[clock_slice]
    r_clock = ricci_geometry[clock_slice]
    curvature_cadence = np.exp(a_clock) * np.sqrt(np.abs(r_clock))
    curvature_cadence /= curvature_cadence[0]
    curvature_phase = cumulative_trapezoid(
        curvature_cadence, u_clock, initial=0.0
    )

    masses = np.asarray(
        minimal["dimensionless_spectrum"]["masses_mu"], dtype=float
    )
    probe_indices = {
        "uv_probe_slice": 0,
        "legacy_clock_anchor_u1": int(np.argmin(np.abs(u - 1.0))),
    }
    ricci_scale_ratios: dict[str, Any] = {}
    for label, index in probe_indices.items():
        root_abs_ricci = math.sqrt(abs(float(ricci_geometry[index])))
        ricci_scale_ratios[label] = {
            "u": float(u[index]),
            "R5_hat": float(ricci_geometry[index]),
            "sqrt_abs_R5_hat": root_abs_ricci,
            "omega_n_over_omega_R": (masses / root_abs_ricci).tolist(),
            "interpretation": (
                "omega_R=c*sqrt(abs(R5_hat))/ell and omega_n=c*mu_n/ell "
                "only after a physical compact-interval interpretation"
            ),
        }

    # The conventional IHQCD normalization would identify Phi=sqrt(3/8) chi
    # and A_string=A_E+2 Phi/3=A_E+chi/sqrt(6).  Neither that identification
    # nor the orientation chi -> +/- chi follows from the inverse completion,
    # so both orientations are audited.
    string_frame: dict[str, Any] = {}
    for label, sign in (("plus", 1.0), ("minus", -1.0)):
        a_string = warp + sign * chi / math.sqrt(6.0)
        a_string_u = warp_u + sign * chi_u / math.sqrt(6.0)
        string_frame[label] = {
            "definition": f"A_string=A_E {label} chi/sqrt(6)",
            "interior_minima_u": _crossings(u, a_string_u, "minimum"),
            "interior_maxima_u": _crossings(u, a_string_u, "maximum"),
            "A_string_range": [float(np.min(a_string)), float(np.max(a_string))],
            "exp_2A_string_ir": float(np.exp(2.0 * a_string[-1])),
        }

    e2a = float(legacy_wilson["e2A_ir"])
    alpha_prime = float(legacy_wilson["alpha_prime_GeV-2"])
    sigma_reported = float(legacy_wilson["sigma_eff_GeV2"])
    sigma_arithmetic = e2a / (2.0 * math.pi * alpha_prime)
    c_scalar = float(legacy_wilson["c_scalar"])
    mass_arithmetic = c_scalar * math.sqrt(sigma_arithmetic)

    e_rounded, e_counts = np.unique(np.round(clock_e, 12), return_counts=True)

    result = {
        "title": "Ricci-clock and Wilson-scale interface audit",
        "classification": "corrected_geometry_audit_not_cross_branch_closure",
        "observational_inputs_read": [],
        "ricci_5d": {
            "metric_gauge": "domain_wall",
            "physical_units": "R5_physical=R5_hat/ell^2",
            "formula": "R5_hat=-8 A_uu-20 A_u^2",
            "independent_trace_identity": "R5_hat=chi_u^2/2+5 V/3",
            "identity_max_abs_error": float(
                np.max(np.abs(ricci_identity_error))
            ),
            "conformal_coordinate": {
                "definition": "dz_c/du=exp(-A)",
                "formula": "R5_hat=exp(-2A)*(-8 A_zz-12 A_z^2)",
                "z_c_domain": [float(z_conformal[0]), float(z_conformal[-1])],
                "max_abs_error_vs_domain_wall": float(
                    np.max(np.abs(ricci_coordinate_error))
                ),
            },
            "stored_derivative_relation": "A_u=u*dA_stored",
            "stored_derivative_relation_max_abs_error": float(
                np.max(np.abs(relation_error))
            ),
            "certified_domain": [float(u[0]), float(u[-1])],
            "legacy_clock_slice_corrected_R5_hat_range": [
                float(np.min(r_clock)),
                float(np.max(r_clock)),
            ],
            "legacy_clock_R5_hat_range": [
                float(np.min(clock_ricci_common)),
                float(np.max(clock_ricci_common)),
            ],
            "legacy_minus_corrected_R5_rms": float(
                np.sqrt(np.mean(np.square(legacy_minus_corrected)))
            ),
            "legacy_minus_corrected_R5_max_abs": float(
                np.max(np.abs(legacy_minus_corrected))
            ),
            "legacy_R5_reproduced_by_mislabeled_dA_rms": float(
                np.sqrt(np.mean(np.square(legacy_reproduction_error)))
            ),
            "legacy_E_unique_values_and_counts": [
                {"value": float(value), "count": int(count)}
                for value, count in zip(e_rounded, e_counts, strict=True)
            ],
            "corrected_dimensionless_curvature_protocol": {
                "definition": (
                    "g_R(u)=exp(A)*sqrt(abs(R5_hat)), normalized at u=1"
                ),
                "u": u_clock.tolist(),
                "g_R": curvature_cadence.tolist(),
                "Theta_R": curvature_phase.tolist(),
                "Theta_R_end": float(curvature_phase[-1]),
                "evidence_boundary": (
                    "This is a dimensionless curvature-phase convention. It is "
                    "not proper time and supplies no seconds until ell or an "
                    "external time standard is fixed."
                ),
            },
            "mode_to_curvature_scale_ratios": ricci_scale_ratios,
        },
        "wilson_scale": {
            "legacy_causal_direction": (
                "ED endpoint warp + external alpha_prime + external c_scalar "
                "-> sigma_proxy -> m0"
            ),
            "legacy_not_measured": [
                "no rectangular W(R,T)",
                "no static potential V_QQ(R)",
                "no Creutz ratio or area-law fit",
                "no string-frame minimum demonstrated",
            ],
            "legacy_arithmetic": {
                "sigma_reported_GeV2": sigma_reported,
                "sigma_recomputed_GeV2": sigma_arithmetic,
                "m0_reported_GeV": float(legacy_wilson["m0_GeV"]),
                "m0_recomputed_GeV": mass_arithmetic,
                "alpha_prime_external_GeV-2": alpha_prime,
                "c_scalar_external": c_scalar,
            },
            "conditional_string_frame_audit": {
                "assumption": (
                    "identify the reconstructed canonical scalar with an IHQCD "
                    "string dilaton; this is not fixed by the effective action"
                ),
                "orientations": string_frame,
                "result": (
                    "Neither canonical orientation supplies a certified smooth "
                    "interior minimum on the full interval; an endpoint tension "
                    "therefore requires a separately declared hard wall."
                ),
            },
            "scale_boundary": (
                "A lattice Wilson calculation yields a^2 sigma. Converting it "
                "to GeV needs an external scale, and fixing compactification ell "
                "additionally needs a derived relation ell*sqrt(sigma)."
            ),
        },
        "legacy_lock5": {
            "classification": "circular_calibration_not_independent_lock",
            "target_values": {
                "f_bulk_mHz": 1.6664,
                "f_earth_mHz": 2.1590,
            },
            "stored_fit": {
                "xi_m2_s2": float(legacy_lock5["xi"]),
                "xi_eff_m2_s2": float(legacy_lock5["xi_eff"]),
                "xi_eff_over_c_squared": float(
                    legacy_lock5["xi_eff"] / 299_792_458.0**2
                ),
                "reconstructed_target_mHz": float(
                    legacy_lock5["checks"]["xi_consistent"][
                        "f_predicted_mhz"
                    ]
                ),
                "reported_relative_error": float(
                    legacy_lock5["checks"]["xi_consistent"][
                        "error_relative"
                    ]
                ),
            },
            "circularity": (
                "LOCK5 infers xi from f_bulk and f_earth, then calls PASS when "
                "the same algebra reconstructs f_earth."
            ),
            "curvature_mismatch": (
                "The bulk clock uses a five-dimensional curvature scalar. "
                "LOCK5 instead inserts R4 approximately 8*pi*G*rho/c^2 for "
                "terrestrial matter and rescales it with surface-gravity "
                "factors. In exterior Schwarzschild vacuum R4=0; tidal "
                "curvature resides in the Riemann/Weyl tensor, not R4."
            ),
            "fail_open_checks": [
                "missing /couplings endpoint is marked passed",
                "missing temporal history is marked passed",
            ],
            "useful_remainder": (
                "The equation omega_eff^2=omega_0^2+xi*R is a valid model "
                "ansatz after xi, the curvature invariant, units, and source "
                "are fixed independently. The historical LOCK5 numbers do not "
                "perform that independent fixing."
            ),
        },
        "branch_compatibility": {
            "holographic_branch": (
                "u is an RG coordinate; scalar poles may be glueball states"
            ),
            "compact_material_branch": (
                "u is a physical interval; the same scalar degree of freedom "
                "becomes a KK/trace carrier"
            ),
            "no_double_use_rule": (
                "Wilson/QCD scale setting and a laboratory compactification "
                "cannot be chained without an explicit UV matching relation"
            ),
        },
        "passes": {
            "effective_input_certified": True,
            "minimal_probe_input_certified": True,
            "ricci_trace_identity": bool(
                np.max(np.abs(ricci_identity_error)) < 1e-10
            ),
            "ricci_coordinate_invariance": bool(
                np.max(np.abs(ricci_coordinate_error)) < 1e-10
            ),
            "stored_derivative_relation_verified": bool(
                # The two sides come from independently smoothed splines.  The
                # maximum mismatch is below 0.05 per cent of the largest slope.
                np.max(np.abs(relation_error)) < 2e-3
            ),
            "legacy_wilson_arithmetic_reproduced": bool(
                abs(sigma_arithmetic - sigma_reported) < 1e-12
                and abs(mass_arithmetic - float(legacy_wilson["m0_GeV"]))
                < 1e-12
            ),
            "observational_blinding": True,
        },
        "evidence_boundary": (
            "The corrected curvature and dimensionless ratios follow from the "
            "certified geometry. The old Ricci series and Wilson label do not "
            "close a laboratory or QCD scale, and no compactification scale, "
            "mode occupation, detector response, or observed interaction is "
            "derived here."
        ),
    }
    result["passes"]["all"] = all(result["passes"].values())
    return result


def main() -> int:
    result = audit()
    _write(OUTPUT_PATH, result)
    ricci = result["ricci_5d"]
    print(f"[audit] {OUTPUT_PATH}")
    print(
        "[R5] corrected={} legacy={} rms_delta={:.6g}".format(
            ricci["legacy_clock_slice_corrected_R5_hat_range"],
            ricci["legacy_clock_R5_hat_range"],
            ricci["legacy_minus_corrected_R5_rms"],
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
