#!/usr/bin/env python3
"""Assemble the C3 geometric-transition input and analytic decision gate.

C3 asks whether the complete five-dimensional Einstein--dilaton plus brane
system can select a non-analytic geometric phase-transition branch without
target-driven boundary choices.  This module does not invent the missing
action.  It content-addresses the existing ADM, GHY, bending, BPS and selector
certificates, distinguishes their verified precursors from the nonlinear
inputs still absent, and returns ``INPUT_INCOMPLETE / BLOCKED_C3`` whenever the
full variational problem is not frozen.

The analytic theorem encoded here is deliberately conditional.  On fixed
function spaces, an analytic gauge-fixed boundary-value map with constant
Dirac rank and boundedly invertible full linearization has a unique local
analytic stationary branch by the analytic implicit-function theorem.  Its
local on-shell and Dirichlet-to-Neumann maps are analytic.  This excludes a
continuous non-analytic transition only inside that certified neighborhood.
It does not exclude a first-order crossing with a distinct branch unless an
exhaustive, uniform free-energy gap to all competitors is also proved.  If any
hypothesis is missing, the theorem is inapplicable; that is not a physical
no-go.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "c3_geometric_transition_gate.json"

SOURCE_PATHS = {
    "effective_action": REPO
    / "first_principles_audit"
    / "artifacts"
    / "holo_effective_action.json",
    "interface": REPO
    / "first_principles_audit"
    / "artifacts"
    / "interface_action_derivation.json",
    "adm_bps_flatness": HERE / "artifacts" / "adm_bmp_tricritical_necessity.json",
    "adm_quadratic_recovery": HERE / "artifacts" / "adm_quadratic_recovery.json",
    "bent_brane_geometry": HERE / "artifacts" / "bent_brane_geometry_S2.json",
    "compact_brane_s2": HERE / "artifacts" / "compact_brane_S2_backward.json",
    "finite_gamma_s2": HERE / "artifacts" / "finite_gamma_brane_S2.json",
    "bps_biscalar_geometry": HERE / "artifacts" / "bps_biscalar_matter_geometry.json",
    "volume_selector": HERE / "artifacts" / "bps_volume_constraint_selector.json",
    "c2_gate": HERE / "artifacts" / "c2_critical_continuum_gate.json",
}

LOCAL_THEOREM_HYPOTHESES = (
    "maps_analytic_between_fixed_banach_spaces",
    "gauge_fixed_boundary_value_problem_complete",
    "dirac_rank_constant",
    "algebraic_auxiliary_jacobian_invertible_or_absent",
    "full_linearized_gauge_fixed_bvp_is_bounded_isomorphism",
)
GLOBAL_EXTENSION_HYPOTHESIS = (
    "exhaustive_uniform_free_energy_gap_to_all_competing_branches"
)

C3_CAMPAIGN_CHECK_IDS = (
    "codimension_zero_criticality",
    "single_physical_collective",
    "dirac_rank_controlled",
    "uniform_positive_gap_for_other_modes",
    "q2y_and_g6_derived",
    "two_source_geometries_agree",
)


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


def _input_requirement(
    present: bool,
    description: str,
    evidence_refs: list[str],
    consequence_if_missing: str,
) -> dict[str, Any]:
    return {
        "present": bool(present),
        "description": description,
        "evidence_refs": list(evidence_refs),
        "consequence_if_missing": consequence_if_missing,
    }


def analytic_branch_theorem(hypotheses: Mapping[str, bool]) -> dict[str, Any]:
    """Evaluate only the logical applicability of the analytic branch theorem.

    The function accepts exactly the five local hypotheses plus the independent
    exhaustive global free-energy-gap hypothesis.  A missing hypothesis returns
    ``NOT_APPLICABLE`` and never a physical rejection.
    """

    expected = set(LOCAL_THEOREM_HYPOTHESES) | {GLOBAL_EXTENSION_HYPOTHESIS}
    actual = set(hypotheses)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise ValueError(
            f"theorem hypotheses mismatch: missing={missing}, unknown={unknown}"
        )
    if any(type(hypotheses[key]) is not bool for key in expected):
        raise TypeError("every theorem hypothesis must be a literal boolean")

    missing_local = [key for key in LOCAL_THEOREM_HYPOTHESES if not hypotheses[key]]
    local_applies = not missing_local
    global_gap = hypotheses[GLOBAL_EXTENSION_HYPOTHESIS]
    selected_ground_state_applies = local_applies and global_gap
    return {
        "local_status": "APPLIES" if local_applies else "NOT_APPLICABLE",
        "missing_local_hypotheses": missing_local,
        "local_unique_analytic_stationary_branch": local_applies,
        "local_onshell_map_is_analytic": local_applies,
        "local_continuous_nonanalytic_transition_excluded": local_applies,
        "exhaustive_uniform_free_energy_gap_to_all_competing_branches": global_gap,
        "selected_ground_state_status": (
            "ANALYTIC_IN_CERTIFIED_NEIGHBORHOOD"
            if selected_ground_state_applies
            else "UNDECIDED"
        ),
        "first_order_crossing_excluded": selected_ground_state_applies,
        "physical_no_go_claimed": False,
        "interpretation": (
            "The theorem controls a regular local branch whose full gauge-fixed "
            "linearization is an isomorphism. A C3 branch with one critical "
            "collective is outside this theorem and instead needs a "
            "Lyapunov--Schmidt reduction with a uniform gap on the complement. "
            "A first-order crossing needs an exhaustive uniform free-energy gap. "
            "Missing hypotheses leave the physical question open."
        ),
    }


def schur_gap_certificate(
    physical_hessian: np.ndarray,
    auxiliary_hessian: np.ndarray,
    mixing: np.ndarray,
    *,
    tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Audit the finite-dimensional quadratic core of the rank/gap theorem.

    For Hessian blocks ``Hqq``, ``Haa`` and ``Hqa``, elimination of genuinely
    algebraic nondegenerate auxiliaries gives
    ``Hred=Hqq-Hqa Haa^-1 Hqa^T``.  This finite-dimensional control does not
    eliminate ADM lapse/shift multipliers, certify a gauge-fixed boundary-value
    problem, or establish constant Dirac rank throughout a nonlinear branch.
    """

    hqq = np.asarray(physical_hessian, dtype=float)
    haa = np.asarray(auxiliary_hessian, dtype=float)
    hqa = np.asarray(mixing, dtype=float)
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("tolerance must be positive and finite")
    if hqq.ndim != 2 or hqq.shape[0] != hqq.shape[1] or hqq.shape[0] == 0:
        raise ValueError("physical_hessian must be a non-empty square matrix")
    if haa.ndim != 2 or haa.shape[0] != haa.shape[1] or haa.shape[0] == 0:
        raise ValueError("auxiliary_hessian must be a non-empty square matrix")
    if hqa.shape != (hqq.shape[0], haa.shape[0]):
        raise ValueError("mixing must have shape (physical, auxiliary)")
    if not all(np.all(np.isfinite(matrix)) for matrix in (hqq, haa, hqa)):
        raise ValueError("all matrices must be finite")
    if not np.allclose(hqq, hqq.T, rtol=0.0, atol=tolerance):
        raise ValueError("physical_hessian must be symmetric")
    if not np.allclose(haa, haa.T, rtol=0.0, atol=tolerance):
        raise ValueError("auxiliary_hessian must be symmetric")

    singular_values = np.linalg.svd(haa, compute_uv=False)
    minimum_auxiliary_singular_value = float(np.min(singular_values))
    auxiliary_invertible = minimum_auxiliary_singular_value > tolerance
    if not auxiliary_invertible:
        return {
            "status": "NOT_APPLICABLE_AUXILIARY_SINGULAR",
            "auxiliary_invertible": False,
            "minimum_auxiliary_singular_value": minimum_auxiliary_singular_value,
            "reduced_hessian": None,
            "reduced_gap": None,
            "reduced_positive_gap": False,
            "constant_rank_in_neighborhood_certified": False,
            "adm_lapse_shift_or_boundary_value_problem_certified": False,
            "scope": "algebraic_auxiliaries_only",
        }

    reduced = hqq - hqa @ np.linalg.solve(haa, hqa.T)
    reduced = 0.5 * (reduced + reduced.T)
    eigenvalues = np.linalg.eigvalsh(reduced)
    reduced_gap = float(np.min(eigenvalues))
    return {
        "status": (
            "QUADRATIC_GAP_POSITIVE"
            if reduced_gap > tolerance
            else "REDUCED_GAP_NOT_POSITIVE"
        ),
        "auxiliary_invertible": True,
        "minimum_auxiliary_singular_value": minimum_auxiliary_singular_value,
        "reduced_hessian": reduced.tolist(),
        "reduced_eigenvalues": eigenvalues.tolist(),
        "reduced_gap": reduced_gap,
        "reduced_positive_gap": reduced_gap > tolerance,
        "constant_rank_in_neighborhood_certified": False,
        "adm_lapse_shift_or_boundary_value_problem_certified": False,
        "scope": "algebraic_auxiliaries_only",
    }


def _source_receipts() -> dict[str, dict[str, str]]:
    return {
        name: {
            "path": str(path.relative_to(REPO)),
            "sha256": _sha256(path),
        }
        for name, path in SOURCE_PATHS.items()
    }


def _require_upstream(condition: bool, label: str) -> None:
    if condition is not True:
        raise RuntimeError(f"upstream certificate failed: {label}")


def _kill_criterion(
    criterion_id: str,
    test: str,
    kill_if: str,
) -> dict[str, Any]:
    return {
        "id": criterion_id,
        "test": test,
        "kill_if": kill_if,
        "evaluated": False,
        "result": "NOT_EVALUATED_INPUT_INCOMPLETE",
    }


def build() -> dict[str, Any]:
    """Build the C3 input-completeness and conditional theorem certificate."""

    sources = {name: _read(path) for name, path in SOURCE_PATHS.items()}
    effective = sources["effective_action"]
    interface = sources["interface"]
    adm_bps = sources["adm_bps_flatness"]
    adm_s2 = sources["adm_quadratic_recovery"]
    bending = sources["bent_brane_geometry"]
    compact = sources["compact_brane_s2"]
    finite_gamma = sources["finite_gamma_s2"]
    biscalar = sources["bps_biscalar_geometry"]
    selector = sources["volume_selector"]
    c2_gate = sources["c2_gate"]

    _require_upstream(effective["summary"]["passes"]["all"], "effective action")
    _require_upstream(interface["passes"]["all"], "interface")
    _require_upstream(adm_bps["checks"]["all"], "ADM/BPS flatness")
    _require_upstream(adm_s2["checks"]["all"], "ADM quadratic recovery")
    _require_upstream(bending["checks"]["all"], "bent brane geometry")
    _require_upstream(compact["checks"]["all"], "compact brane S2")
    _require_upstream(finite_gamma["checks"]["all"], "finite-gamma S2")
    _require_upstream(biscalar["checks"]["all"], "BPS biscalar geometry")
    _require_upstream(selector["checks"]["all"], "volume selector")
    _require_upstream(
        c2_gate["decision"]["verdict"] == "KILL_C2"
        and c2_gate["campaign_transition"] == "UNLOCK_C3",
        "C2 ladder transition",
    )

    precursor_certificates = {
        "einstein_dilaton_background_and_bulk_action_reconstructed": bool(
            effective["summary"]["passes"]["all"]
        ),
        "functional_bps_background_action_and_junctions_close": bool(
            adm_bps["checks"]["symbolic_on_shell_action_cancels"]
            and adm_bps["checks"]["actual_endpoint_junctions"]
        ),
        "bulk_adm_s2_recovered_on_compact_support": bool(
            adm_s2["physical_gates"][
                "same_variable_bulk_ADM_S2_action_recovered_on_compact_support"
            ]
        ),
        "bent_geometry_and_radial_straightening_close_through_o2": bool(
            bending["physical_gates"]["exact_bent_extrinsic_curvature_implemented"]
            and bending["physical_gates"][
                "radial_gauge_straightening_verified_through_O2"
            ]
        ),
        "stiff_compact_s2_spectrum_recovered": bool(
            compact["physical_gates"][
                "stiff_compact_S2_spectrum_two_representation_verified"
            ]
        ),
        "finite_gamma_s2_spectrum_crosschecked": bool(
            finite_gamma["physical_gates"][
                "finite_gamma_compact_spectrum_three_route_verified"
            ]
        ),
        "two_physical_bps_moduli_and_positive_kinetic_metric_resolved": bool(
            biscalar["physical_gates"][
                "finite_endpoint_physical_mode_count_resolved_here"
            ]
            and min(biscalar["moduli_metric"]["Khat_eigenvalues"]) > 0.0
        ),
        "warped_volume_selector_exists_as_a_geometric_functional": bool(
            selector["physical_gates"]["warped_volume_F_exists_as_geometric_functional"]
        ),
        "c2_frozen_scope_failed_and_c3_unlocked": bool(
            c2_gate["decision"]["verdict"] == "KILL_C2"
            and c2_gate["campaign_transition"] == "UNLOCK_C3"
        ),
    }

    requirements = {
        "R1_bulk_action_and_background_frozen": _input_requirement(
            True,
            "A concrete Einstein--dilaton bulk action and background are available on the certified interval.",
            ["effective_action", "adm_bps_flatness"],
            "No nonlinear C3 variational problem can be posed.",
        ),
        "R2_complete_boundary_action_and_jets_frozen": _input_requirement(
            bool(
                finite_gamma["physical_gates"]["nonlinear_brane_jets_frozen"]
                and adm_bps["scope_boundary"]["functional_BPS_branch_selected_by_bulk"]
            ),
            "All brane potentials and boundary jets required by the nonlinear order are fixed before the C3 scan.",
            ["adm_bps_flatness", "finite_gamma_s2"],
            "Boundary normal forms and any apparent critical point remain selectable inputs.",
        ),
        "R3_eh_ghy_boundary_variation_complete": _input_requirement(
            bool(
                bending["physical_gates"][
                    "EH_GHY_normal_derivative_cancellation_verified"
                ]
                and finite_gamma["physical_gates"][
                    "raw_EH_GHY_normal_derivative_cancellation_rederived_in_repo"
                ]
            ),
            "The complete EH+GHY+brane variation is recovered on nonzero endpoint profiles.",
            ["bent_brane_geometry", "finite_gamma_s2", "compact_brane_s2"],
            "The endpoint action and junction operator are not derived in the same variables.",
        ),
        "R4_nonlinear_junctions_with_bending_complete": _input_requirement(
            bool(
                bending["physical_gates"][
                    "total_action_variation_reproduces_linear_junctions"
                ]
                and bending["physical_gates"]["finite_gamma_bent_brane_S2_complete"]
            ),
            "Scalar and Israel junctions including bending are derived from the frozen total action through the required order.",
            ["bent_brane_geometry", "compact_brane_s2"],
            "A candidate branch cannot be checked against the actual endpoint equations.",
        ),
        "R5_nonlinear_lapse_shift_and_dirac_system_complete": _input_requirement(
            bool(adm_s2["physical_gates"]["nonlinear_lapse_shift_constraints_solved"]),
            "Nonlinear lapse and shift constraints, gauge quotient and Dirac rank are solved on every candidate branch.",
            ["adm_quadratic_recovery"],
            "A gauge kernel or constraint-rank change could be mistaken for a physical transition.",
        ),
        "R6_matter_action_localization_and_source_frozen": _input_requirement(
            bool(
                biscalar["physical_gates"]["matter_localization_selected_by_bulk"]
                and biscalar["physical_gates"]["matter_Y_convention_fixed"]
                and len(interface["unfixed_choices"]) == 0
            ),
            "The conserved matter action, radial localization, Y convention and absolute normalization are frozen.",
            ["interface", "bps_biscalar_geometry"],
            "The source family and its coupling to the geometric branch remain undefined.",
        ),
        "R7_physical_q2y_and_g6_vertices_derived": _input_requirement(
            bool(
                biscalar["physical_gates"]["physical_q2Y_selector_derived"]
                and adm_bps["tricritical_gate"]["positive_q6"]
            ),
            "The same constrained reduction derives the physical q^2Y vertex and stable g6 coefficient.",
            ["adm_bps_flatness", "bps_biscalar_geometry"],
            "The proposed transition is not connected to the required local constitutive vertex.",
        ),
        "R8_branch_family_and_selection_rule_frozen": _input_requirement(
            bool(
                biscalar["physical_gates"]["unique_tangent_selected_by_BPS_geometry"]
                and selector["physical_gates"]["F_constraint_physically_selects_ker_dF"]
            ),
            "All competing branches and a target-independent rule selecting the physical branch are specified.",
            ["bps_biscalar_geometry", "volume_selector"],
            "Neither codimension nor free-energy competition can be evaluated.",
        ),
        "R9_candidate_spectrum_symbol_and_free_energy_gap_complete": _input_requirement(
            False,
            "Each nonlinear branch has a physical fluctuation spectrum, principal symbol and free-energy comparison.",
            ["adm_quadratic_recovery", "finite_gamma_s2"],
            "The baseline positive S2 spectrum cannot be reused as the gap of an unspecified critical branch.",
        ),
        "R10_two_conserved_source_geometries_frozen": _input_requirement(
            False,
            "Two non-equivalent conserved source geometries are frozen before solving the nonlinear map.",
            ["interface"],
            "Locality and geometry-independent normal-form coefficients cannot be tested.",
        ),
    }
    missing_requirements = [
        name for name, requirement in requirements.items() if not requirement["present"]
    ]
    inputs_complete = not missing_requirements

    candidate_spectral_adjudication = {
        "calculation_complete": requirements[
            "R9_candidate_spectrum_symbol_and_free_energy_gap_complete"
        ]["present"],
        "full_linearized_operator_isomorphism": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "exactly_one_physical_critical_collective": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "uniform_positive_gap_on_noncollective_complement": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "exhaustive_uniform_free_energy_gap_to_competitors": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "transition_below_independent_eft_cutoff": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "interpretation": (
            "Completing R9 means performing the candidate calculation; it does "
            "not predetermine an isomorphism, a critical kernel, a complement "
            "gap, a free-energy gap or cutoff separation."
        ),
    }

    functional_analytic_adjudication = {
        "action_and_source_input_bundle_frozen": bool(
            requirements["R1_bulk_action_and_background_frozen"]["present"]
            and requirements["R2_complete_boundary_action_and_jets_frozen"]["present"]
            and requirements["R6_matter_action_localization_and_source_frozen"][
                "present"
            ]
        ),
        "boundary_and_constraint_input_bundle_complete": bool(
            requirements["R3_eh_ghy_boundary_variation_complete"]["present"]
            and requirements["R4_nonlinear_junctions_with_bending_complete"]["present"]
            and requirements["R5_nonlinear_lapse_shift_and_dirac_system_complete"][
                "present"
            ]
        ),
        "maps_analytic_between_fixed_banach_spaces": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "gauge_fixed_boundary_value_problem_complete": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "dirac_rank_constant": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "algebraic_auxiliary_jacobian_invertible_or_absent": {
            "evaluated": False,
            "certified": False,
            "status": "NOT_EVALUATED_INPUT_INCOMPLETE",
        },
        "interpretation": (
            "Frozen actions and completed equations are prerequisites only. "
            "They do not by themselves certify analyticity on chosen function "
            "spaces, Fredholm well-posedness, constant Dirac rank or an "
            "algebraic auxiliary Jacobian."
        ),
    }

    certified_theorem_hypotheses = {
        "maps_analytic_between_fixed_banach_spaces": (
            functional_analytic_adjudication[
                "maps_analytic_between_fixed_banach_spaces"
            ]["certified"]
        ),
        "gauge_fixed_boundary_value_problem_complete": (
            functional_analytic_adjudication[
                "gauge_fixed_boundary_value_problem_complete"
            ]["certified"]
        ),
        "dirac_rank_constant": functional_analytic_adjudication["dirac_rank_constant"][
            "certified"
        ],
        "algebraic_auxiliary_jacobian_invertible_or_absent": (
            functional_analytic_adjudication[
                "algebraic_auxiliary_jacobian_invertible_or_absent"
            ]["certified"]
        ),
        "full_linearized_gauge_fixed_bvp_is_bounded_isomorphism": (
            candidate_spectral_adjudication["full_linearized_operator_isomorphism"][
                "certified"
            ]
        ),
        "exhaustive_uniform_free_energy_gap_to_all_competing_branches": (
            candidate_spectral_adjudication[
                "exhaustive_uniform_free_energy_gap_to_competitors"
            ]["certified"]
        ),
    }
    theorem_application = analytic_branch_theorem(certified_theorem_hypotheses)

    kill_criteria = [
        _kill_criterion(
            "K1_regular_analytic_branch",
            "Apply the analytic branch theorem to the fully reduced source-zero solution.",
            "The full gauge-fixed boundary-value linearization is an isomorphism, an exhaustive uniform free-energy gap selects this branch, and its Dirichlet-to-Neumann map stays regular and analytic instead of developing a protected critical collective.",
        ),
        _kill_criterion(
            "K2_unprotected_codimension",
            "Derive the normal form and count independent relevant coefficients before comparison with the target.",
            "Criticality at zero source requires tuning any unprotected boundary jet, brane scale or Wilson coefficient.",
        ),
        _kill_criterion(
            "K3_negative_mode_or_bad_principal_symbol",
            "Compute the gauge-reduced Hessian, kinetic residues and full principal symbol on the selected branch.",
            "A negative-norm or negative-energy physical mode, ill-posed characteristic, or vanishing tensor Planck coefficient occurs.",
        ),
        _kill_criterion(
            "K4_gauge_or_constraint_artifact",
            "Track the Dirac rank and physical mode count through the candidate transition.",
            "The nonanalyticity is a gauge kernel or unsolved lapse/shift constraint, or the Dirac rank changes anywhere on the candidate branch.",
        ),
        _kill_criterion(
            "K5_background_junction_or_conservation_failure",
            "Vary the same total action and evaluate bulk equations, scalar/Israel junctions and conserved matter Ward identities.",
            "The selected branch fails any background equation, junction condition or source conservation identity.",
        ),
        _kill_criterion(
            "K6_nonlocal_or_geometry_dependent_normal_form",
            "Extract the local Dirichlet-to-Neumann normal form for two frozen conserved source geometries.",
            "The leading relation is nonlocal or its supposedly local coefficient depends on source geometry.",
        ),
        _kill_criterion(
            "K7_required_vertices_absent",
            "Project the complete constrained action through q^2Y and q^6 on the selected canonical mode.",
            "The physical q^2Y vertex or stable g6 coefficient is absent after all inputs are complete.",
        ),
        _kill_criterion(
            "K8_noncollective_gap_or_cutoff_failure",
            "Bound the full non-collective spectrum uniformly and compare every transition scale with the independently derived EFT cutoff.",
            "Any physical mode other than the single selected collective becomes gapless, a tower accumulates at zero, or the transition occurs at or above the EFT cutoff.",
        ),
    ]

    campaign_step_projection = {
        "projection_scope": (
            "Partial step projection only; this artifact is not a standalone "
            "holo.mechanism-campaign.v1 document."
        ),
        "step_id": "C3",
        "family": "geometric_brane_transition",
        "status": "ready",
        "status_semantics": (
            "ready means C2 unlocked the ladder step; it does not override the "
            "INPUT_INCOMPLETE/BLOCKED_C3 diagnostic."
        ),
        "checks": [
            {
                "id": check_id,
                "status": "pending",
                "evidence_refs": [],
            }
            for check_id in C3_CAMPAIGN_CHECK_IDS
        ],
    }

    decision = {
        "input_status": "INPUT_INCOMPLETE" if not inputs_complete else "INPUT_COMPLETE",
        "status": "BLOCKED_C3" if not inputs_complete else "READY_FOR_C3_EVALUATION",
        "kill_triggered": False,
        "candidate_passed": False,
        "missing_requirement_ids": missing_requirements,
        "reason": (
            "The existing certificates close important background, ADM, bending, "
            "BPS and selector precursors, but they do not freeze the complete "
            "boundary/junction, nonlinear constraint and matter-source problem."
        ),
        "next_action": (
            "Freeze and derive the missing inputs in one total action, then solve "
            "all branches and evaluate the predeclared kill criteria without "
            "changing boundary jets or source conventions."
        ),
    }

    source_receipts = _source_receipts()
    source_hashes_are_valid = all(
        len(receipt["sha256"]) == 64
        and all(character in "0123456789abcdef" for character in receipt["sha256"])
        for receipt in source_receipts.values()
    )
    checks = {
        "all_upstream_mathematical_certificates_pass": all(
            precursor_certificates.values()
        ),
        "source_receipts_are_content_addressed": source_hashes_are_valid,
        "required_inputs_are_incomplete": not inputs_complete,
        "missing_boundary_junction_lapse_shift_and_matter_inputs_detected": all(
            requirement in missing_requirements
            for requirement in (
                "R2_complete_boundary_action_and_jets_frozen",
                "R3_eh_ghy_boundary_variation_complete",
                "R4_nonlinear_junctions_with_bending_complete",
                "R5_nonlinear_lapse_shift_and_dirac_system_complete",
                "R6_matter_action_localization_and_source_frozen",
            )
        ),
        "analytic_theorem_not_applied_without_hypotheses": (
            theorem_application["local_status"] == "NOT_APPLICABLE"
            and not theorem_application[
                "local_continuous_nonanalytic_transition_excluded"
            ]
            and not theorem_application["physical_no_go_claimed"]
        ),
        "baseline_s2_gap_not_promoted_to_candidate_branch_gap": not requirements[
            "R9_candidate_spectrum_symbol_and_free_energy_gap_complete"
        ]["present"],
        "kill_criteria_remain_unevaluated": all(
            not criterion["evaluated"]
            and criterion["result"] == "NOT_EVALUATED_INPUT_INCOMPLETE"
            for criterion in kill_criteria
        ),
        "campaign_step_is_ready_with_pending_checks": (
            campaign_step_projection["status"] == "ready"
            and all(
                row["status"] == "pending" and row["evidence_refs"] == []
                for row in campaign_step_projection["checks"]
            )
        ),
        "no_observational_data_read": (
            interface["observational_inputs_read"] == []
            and adm_bps["checks"]["no_observational_tables_read"]
            and adm_s2["checks"]["no_observational_tables_read"]
            and bending["checks"]["no_observational_inputs"]
            and compact["checks"]["no_observational_tables_read"]
            and finite_gamma["checks"]["no_observational_tables_read"]
            and biscalar["checks"]["no_observational_tables_read"]
            and selector["checks"]["no_observational_tables_read"]
        ),
    }
    checks["blocked_verdict_is_not_a_kill"] = (
        decision["status"] == "BLOCKED_C3"
        and not decision["kill_triggered"]
        and not decision["candidate_passed"]
    )
    checks["all"] = all(checks.values())

    return {
        "schema": "holo.c3-geometric-transition-gate.v1",
        "title": "C3 geometric brane-transition input and analytic gate",
        "classification": "input_incomplete;blocked_without_physical_kill",
        "evidence_boundary": (
            "This certificate composes existing theory-only results and proves "
            "that the C3 calculation is not yet well posed. It neither rejects "
            "geometric phase transitions nor claims a force, critical exponent, "
            "lensing response or physical completion."
        ),
        "sources": {
            "artifacts": source_receipts,
            "observational_inputs_read": [],
        },
        "precursor_certificates": precursor_certificates,
        "required_inputs": requirements,
        "input_completeness": {
            "all": inputs_complete,
            "missing_requirement_ids": missing_requirements,
            "present_count": sum(
                requirement["present"] for requirement in requirements.values()
            ),
            "required_count": len(requirements),
        },
        "analytic_branch_theorem": {
            "local_statement": (
                "For an analytic gauge-fixed boundary-value map between fixed "
                "Banach spaces, constant Dirac rank and a boundedly invertible "
                "full linearized operator let the analytic implicit-function "
                "theorem give a unique local analytic stationary branch and "
                "analytic on-shell Dirichlet-to-Neumann map."
            ),
            "global_caveat": (
                "A first-order crossing with a distinct branch is excluded only "
                "after a separate exhaustive uniform free-energy gap to all "
                "competitors is proved."
            ),
            "ways_a_transition_can_remain_open": [
                "a retained physical mode becomes gapless",
                "two stable branches cross in free energy",
                "a healthy threshold independently derives a nonanalytic microscopic functional below its certified cutoff",
            ],
            "certified_hypotheses": certified_theorem_hypotheses,
            "application": theorem_application,
            "scope": (
                "A failed hypothesis opens a calculation; it is not evidence for "
                "a transition and not a no-go against one."
            ),
        },
        "functional_analytic_adjudication": functional_analytic_adjudication,
        "candidate_spectral_adjudication": candidate_spectral_adjudication,
        "kill_criteria": kill_criteria,
        "campaign_step_projection": campaign_step_projection,
        "decision": decision,
        "checks": checks,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    completeness = result["input_completeness"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[C3 inputs] {}/{} present; {} missing".format(
            completeness["present_count"],
            completeness["required_count"],
            len(completeness["missing_requirement_ids"]),
        )
    )
    print(f"[C3 input status] {result['decision']['input_status']}")
    print(f"[C3 verdict] {result['decision']['status']}")
    print(f"[certificate] {'PASS' if result['checks']['all'] else 'FAIL'}")
    return 0 if result["checks"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
