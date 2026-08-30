#!/usr/bin/env python3
"""Turn the nonlinear HOLO proposal into a prospective decision test.

This module compares the certified fixed-pole response with the two exact
three-halves bridges.  It deliberately does not read galaxy catalogues or fit
the exposed collector: its output is a list of microscopic conditions that a
frozen five-dimensional calculation must satisfy before the response can be
called a prediction.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "bulk_constitutive_decision_gate.json"

INPUTS = {
    "interface": REPO
    / "first_principles_audit/artifacts/interface_action_derivation.json",
    "scale_consistency": HERE / "artifacts" / "scale_consistency.json",
    "stiff_force": HERE / "artifacts" / "stiff_boundary_force.json",
    "bulk_cubic_inventory": HERE
    / "artifacts"
    / "bulk_cubic_vertex_inventory.json",
    "tricritical_bridge": HERE
    / "artifacts"
    / "tricritical_constitutive_bridge.json",
    "spectral_bridge": HERE / "artifacts" / "collective_spectral_bridge.json",
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


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    interface = payloads["interface"]
    scales = payloads["scale_consistency"]
    stiff = payloads["stiff_force"]
    cubic = payloads["bulk_cubic_inventory"]
    tricritical = payloads["tricritical_bridge"]
    spectral = payloads["spectral_bridge"]

    if interface.get("passes", {}).get("all") is not True:
        raise RuntimeError("interface input is not certified")
    if scales.get("passes", {}).get("all") is not True:
        raise RuntimeError("scale-consistency input is not certified")
    if stiff.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff-force input is not certified")
    if cubic.get("checks", {}).get("all") is not True:
        raise RuntimeError("bulk cubic vertex inventory is not certified")
    if tricritical.get("checks", {}).get("all") is not True:
        raise RuntimeError("tricritical bridge is not certified")
    if spectral.get("checks", {}).get("all") is not True:
        raise RuntimeError("spectral bridge is not certified")

    # Deep constitutive density P=2Y^(3/2)/3.
    y_probe = 1.0e-12
    transverse = math.sqrt(y_probe)
    longitudinal = 2.0 * math.sqrt(y_probe)
    radial_characteristic_ratio = longitudinal / transverse

    masses = stiff["spectrum_and_force"]["masses_mu"]
    seven_mode = spectral["current_seven_mode_test"]
    unfixed = list(interface["unfixed_choices"])

    algebra_checks = {
        "certified_inputs": True,
        "no_observational_tables_read": True,
        "old_fixed_tower_has_source_exponent_one": math.isclose(
            tricritical["old_vs_new"]["previous_fixed_poles"][
                "source_mass_exponent"
            ],
            1.0,
        ),
        "new_deep_constitutive_branch_has_source_exponent_one_half": (
            math.isclose(
                tricritical["old_vs_new"]["new_collective_coordinate"][
                    "source_mass_exponent_in_deep_spherical_limit"
                ],
                0.5,
            )
        ),
        "deep_transverse_coefficient_positive": transverse > 0.0,
        "deep_longitudinal_coefficient_positive": longitudinal > 0.0,
        "minimal_covariant_radial_characteristic_ratio_is_two": math.isclose(
            radial_characteristic_ratio, 2.0, rel_tol=0.0, abs_tol=1.0e-14
        ),
        "finite_tower_crossover_is_less_than_one_decade": (
            seven_mode["within_0p05_log10_width_dex"] < 1.0
        ),
    }
    algebra_checks["all"] = all(algebra_checks.values())

    physical_gates = {
        "five_dimensional_action_and_boundary_terms_frozen": False,
        "kappa5_ell_and_standard_model_localization_fixed": False,
        "matter_function_A_m_and_beta_fixed": False,
        "q_squared_Y_or_equivalent_nonlinear_vertex_derived": False,
        "direct_quartic_contact_from_S4_derived": False,
        "critical_relevant_couplings_vanish_without_target_tuning": False,
        "a0_derived_without_galaxy_data": False,
        "healthy_causal_covariant_completion_derived": False,
        "scalar_strong_coupling_at_Y_zero_resolved": False,
        "metric_slip_and_lensing_derived": False,
        "solar_system_and_high_field_decoupling_derived": False,
    }
    physical_gates["physical_completion"] = all(physical_gates.values())

    return {
        "schema": "holo.bulk-constitutive-decision-gate.v1",
        "title": "Old fixed poles versus a critical constitutive response",
        "classification": (
            "exact_exponent_mechanism_found;bulk_force_prediction_not_yet_derived"
        ),
        "evidence_boundary": (
            "The comparison is theory-only. It establishes why the old finite "
            "linear tower cannot give the required mass exponent and identifies "
            "two exact mathematical mechanisms. It does not establish that the "
            "current five-dimensional theory generates either mechanism."
        ),
        "old_vs_this": {
            "old_fixed_poles": {
                "number_of_modes": len(masses),
                "lowest_dimensionless_mass": min(masses),
                "operator": "finite quadratic Green functions and additive Yukawa exchange",
                "analyticity": "analytic about zero field while the gap stays positive",
                "source_mass_exponent": 1.0,
                "three_halves_crossover_width_dex": seven_mode[
                    "within_0p05_log10_width_dex"
                ],
                "verdict": "negative control; cannot generate sqrt(M)",
            },
            "this_critical_constitutive_response": {
                "operator": "P(Y)=2*Y^(3/2)/3 with P_Y=sqrt(Y)",
                "classical_realization": "s=q^2, W=s^3/3, Y=W'(s)",
                "spectral_identity": (
                    "constant gapless mass density represents the same power but "
                    "does not by itself provide healthy local generation"
                ),
                "source_mass_exponent": 0.5,
                "gain": "the required deep exponent is exact rather than a crossover",
                "cost": (
                    "a critical Hessian, an independently selected sextic point, "
                    "and a controlled covariant completion"
                ),
                "verdict": "viable mathematical architecture; microscopic origin open",
            },
        },
        "microscopic_progress": {
            "raw_metric_scalar_derivative_vertex": cubic[
                "exact_first_variation"
            ]["raw_derivative_cubic"],
            "fixed_metric_scalar_derivative_cubic": "exactly zero",
            "heavy_unit_overlap_inverse_mass_squared_moment": cubic[
                "modal_reduction"
            ]["unit_overlap_spectral_moment_sum_mu_inverse_squared"],
            "physical_c_a_computed": cubic["physical_gates"][
                "physical_overlap_coefficients_c_a_computed"
            ],
            "direct_S4_contact_computed": cubic["physical_gates"][
                "direct_quartic_contact_operator_computed"
            ],
            "gapped_exchange_contribution_to_P": cubic["modal_reduction"][
                "low_energy_result_if_c_a_were_known"
            ],
            "total_Y2_coefficient": cubic["modal_reduction"][
                "total_quartic_coefficient"
            ],
            "current_boundary": cubic["projection_obstruction"][
                "why_direct_insertion_is_invalid"
            ],
        },
        "principal_symbol_audit": {
            "deep_transverse_coefficient_at_probe": transverse,
            "deep_longitudinal_coefficient_at_probe": longitudinal,
            "radial_over_transverse_characteristic_ratio": (
                radial_characteristic_ratio
            ),
            "Y_probe": y_probe,
            "vacuum_limit": (
                "both principal coefficients vanish as Y tends to zero; the "
                "minimal scalar operator is degenerate there"
            ),
            "causality_boundary": (
                "For the minimal Lorentz-covariant P(Y) completion on a spacelike "
                "gradient, the radial characteristic speed squared relative to "
                "the tensor metric is 2. A different healthy completion must be "
                "derived, not assumed."
            ),
        },
        "matter_and_lensing_audit": {
            "certified_interface": interface["conditional_4d_interface"],
            "unfixed_microscopic_choices": unfixed,
            "linear_conformal_map": [
                "Phi_J=Phi_E+alpha*delta_phi",
                "Psi_J=Psi_E-alpha*delta_phi",
                "Phi_J+Psi_J=Phi_E+Psi_E",
            ],
            "consequence": (
                "A direct conformal scalar acceleration cancels from the lensing "
                "sum at linear order. Scalar stress or an additional coupling "
                "must be solved before claiming the observed lensing field."
            ),
        },
        "scale_audit": {
            "single_ell_qcd_galaxy_compatible": scales["comparison"][
                "single_ell_can_realize_both_identifications"
            ],
            "scale_mismatch_orders": scales["comparison"][
                "orders_of_magnitude_in_ell"
            ],
            "required_rule": (
                "derive a0 from frozen microscopic parameters before revealing "
                "the galaxy target"
            ),
        },
        "prospective_bulk_test": {
            "frozen_inputs": [
                "five-dimensional Einstein-scalar action",
                "all boundary actions and boundary conditions",
                "kappa_5 and ell",
                "A_m and Standard-Model localization",
                "a conserved matter source family",
            ],
            "calculation": (
                "Solve the nonlinear bulk constraints across a blind source-amplitude "
                "scan and extract the on-shell Dirichlet-to-Neumann flux Pi(g)."
            ),
            "pre_registered_acceptance_conditions": [
                "lim_{g->0} Pi(g)/g = 0",
                "lim_{g->0} Pi(g)/g^2 = 1/a0_bulk > 0",
                "lim_{g->infinity} Pi(g)/g = 1",
                "dlog(g)/dlog(source) -> 1/2 in the deep branch",
                "the same local constitutive map is recovered for at least two source geometries",
                "the fluctuation operator has no negative modes and has a well-posed causal principal symbol",
                "the independently computed Phi+Psi passes the revealed lensing test",
            ],
            "fail_closed_rule": (
                "Any inserted W, boundary B(Y), cancelled canonical term or a0 "
                "chosen after inspecting the target is inverse design, not a bulk prediction."
            ),
            "can_run_with_current_frozen_inputs": False,
            "current_blocker": (
                "The certified repository fixes the quadratic carrier but leaves "
                "the boundary completion, absolute scale, matter localization "
                "and Wilson coefficients unfixed."
            ),
        },
        "algebra_checks": algebra_checks,
        "physical_gates": physical_gates,
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
        "software": {"python": platform.python_version()},
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    old = result["old_vs_this"]["old_fixed_poles"]
    new = result["old_vs_this"]["this_critical_constitutive_response"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[old vs this] mass exponent {:.1f} -> {:.1f}; old 3/2 crossover "
        "width {:.3f} dex".format(
            old["source_mass_exponent"],
            new["source_mass_exponent"],
            old["three_halves_crossover_width_dex"],
        )
    )
    print(f"[algebra] {'PASS' if result['algebra_checks']['all'] else 'FAIL'}")
    print(f"[physical completion] {result['physical_gates']['physical_completion']}")
    return 0 if result["algebra_checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
