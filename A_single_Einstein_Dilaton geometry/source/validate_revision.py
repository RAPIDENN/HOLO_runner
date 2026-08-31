#!/usr/bin/env python3
"""Fail-closed validation for the rebuilt Einstein--dilaton paper."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


SOURCE = Path(__file__).resolve().parent
PAPER_ROOT = SOURCE.parent
REPO_ROOT = PAPER_ROOT.parent
PDF = PAPER_ROOT / "build" / "A_single_Einstein-Dilaton_geometry.pdf"
LOG = PAPER_ROOT / "build" / "main.log"
TEXT = PAPER_ROOT / "build" / "main.txt"
PRIMARY = PAPER_ROOT / "A_single_Einstein-Dilaton_geometry.pdf"
FROZEN_V1 = PAPER_ROOT / "A_single_Einstein-Dilaton_geometry_v1_frozen.pdf"
ORIGINAL = FROZEN_V1 if FROZEN_V1.is_file() else PRIMARY
SUMMARY = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "holo_effective_action_summary.json"
)
MINIMAL = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "minimal_probe_completion.json"
)
SHOOTING = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "minimal_probe_completion_shooting_verification.json"
)
RICCI_WILSON = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "ricci_wilson_interface_audit.json"
)
MATERIAL = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "material_transducer.json"
)
FACTORY_ROOT = REPO_ROOT / "first_principles_audit" / "prediction_factory"
BOUNDARY_BRANCHES = FACTORY_ROOT / "artifacts" / "boundary_branch_catalogue.json"
ND_SHOOTING = FACTORY_ROOT / "artifacts" / "nd_ultralight_shooting.json"
EM_KERNEL = FACTORY_ROOT / "em_kernel_completion.json"
EM_FINGERPRINT = FACTORY_ROOT / "em_spectral_fingerprint.json"
ROBIN_FAMILY = FACTORY_ROOT / "artifacts" / "robin_boundary_family.json"
BREATHING_RESPONSE = FACTORY_ROOT / "artifacts" / "breathing_response.json"
DESI_DIAGNOSTIC = FACTORY_ROOT / "desi_dr1_growth_diagnostic.json"
SPARC_CROSSVAL = FACTORY_ROOT / "sparc_crossval_report.json"
SPARC_PHYSICAL = FACTORY_ROOT / "sparc_physical_audit.json"
UNIVERSAL_COLLECTOR = (
    FACTORY_ROOT / "artifacts" / "universal_residual_collector.json"
)
NONLINEAR_COLLECTOR_ACTION = (
    FACTORY_ROOT / "artifacts" / "nonlinear_collector_action.json"
)
HOLO_COLLECTOR_EMBEDDING = (
    FACTORY_ROOT / "artifacts" / "holo_collector_embedding_gate.json"
)
AXISYMMETRIC_COLLECTOR = (
    FACTORY_ROOT / "artifacts" / "derive_axisymmetric_collector_certificate.json"
)
AXISYMMETRIC_SOLVER = (
    FACTORY_ROOT / "artifacts" / "derive_axisymmetric_collector_solver.json"
)
JORDAN_SELECTOR = FACTORY_ROOT / "artifacts" / "jordan_selector_embedding.json"
JORDAN_DEEP_GATE = FACTORY_ROOT / "artifacts" / "jordan_deep_limit_gate.json"
BPS_RADION_MATTER = (
    FACTORY_ROOT / "artifacts" / "bps_radion_matter_coupling.json"
)
BPS_BISCALAR_MATTER = (
    FACTORY_ROOT / "artifacts" / "bps_biscalar_matter_geometry.json"
)
BPS_VOLUME_CONSTRAINT = (
    FACTORY_ROOT / "artifacts" / "bps_volume_constraint_selector.json"
)
NONLINEAR_ROUTE_MATRIX = (
    FACTORY_ROOT / "artifacts" / "holo_nonlinear_route_matrix.json"
)
MECHANISM_CAMPAIGN = (
    FACTORY_ROOT / "artifacts" / "minimal_mechanism_campaign.json"
)
MASTER_REGISTRY = FACTORY_ROOT / "MASTER_PREDICTION_REGISTRY.json"
COMPARISON = PAPER_ROOT / "build" / "original_revision_comparison.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(checks: list[dict[str, Any]], name: str, passed: bool, detail: Any) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def main() -> int:
    checks: list[dict[str, Any]] = []
    for path in (
        PDF,
        LOG,
        ORIGINAL,
        SUMMARY,
        MINIMAL,
        SHOOTING,
        RICCI_WILSON,
        MATERIAL,
        BOUNDARY_BRANCHES,
        ND_SHOOTING,
        EM_KERNEL,
        EM_FINGERPRINT,
        ROBIN_FAMILY,
        BREATHING_RESPONSE,
        DESI_DIAGNOSTIC,
        SPARC_CROSSVAL,
        SPARC_PHYSICAL,
        UNIVERSAL_COLLECTOR,
        NONLINEAR_COLLECTOR_ACTION,
        HOLO_COLLECTOR_EMBEDDING,
        AXISYMMETRIC_COLLECTOR,
        AXISYMMETRIC_SOLVER,
        JORDAN_SELECTOR,
        JORDAN_DEEP_GATE,
        BPS_RADION_MATTER,
        BPS_BISCALAR_MATTER,
        BPS_VOLUME_CONSTRAINT,
        NONLINEAR_ROUTE_MATRIX,
        MECHANISM_CAMPAIGN,
        MASTER_REGISTRY,
        COMPARISON,
        SOURCE / "main.tex",
    ):
        record(checks, f"exists:{path.name}", path.is_file(), str(path))
    if not all(item["passed"] for item in checks):
        raise SystemExit("Required revision input is missing")

    subprocess.run(
        ["pdftotext", "-layout", str(PDF), str(TEXT)], check=True
    )
    info = subprocess.run(
        ["pdfinfo", str(PDF)], check=True, capture_output=True, text=True
    ).stdout
    text = TEXT.read_text(encoding="utf-8")
    text_lower = text.lower()
    text_normalized = re.sub(r"\s+", " ", text_lower)
    log = LOG.read_text(encoding="utf-8", errors="replace")
    tex = (SOURCE / "main.tex").read_text(encoding="utf-8")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    minimal = json.loads(MINIMAL.read_text(encoding="utf-8"))
    shooting = json.loads(SHOOTING.read_text(encoding="utf-8"))
    ricci_wilson = json.loads(RICCI_WILSON.read_text(encoding="utf-8"))
    material = json.loads(MATERIAL.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY_BRANCHES.read_text(encoding="utf-8"))
    nd_shooting = json.loads(ND_SHOOTING.read_text(encoding="utf-8"))
    em_kernel = json.loads(EM_KERNEL.read_text(encoding="utf-8"))
    em_fingerprint = json.loads(EM_FINGERPRINT.read_text(encoding="utf-8"))
    robin_family = json.loads(ROBIN_FAMILY.read_text(encoding="utf-8"))
    breathing_response = json.loads(BREATHING_RESPONSE.read_text(encoding="utf-8"))
    desi = json.loads(DESI_DIAGNOSTIC.read_text(encoding="utf-8"))
    sparc_crossval = json.loads(SPARC_CROSSVAL.read_text(encoding="utf-8"))
    sparc_physical = json.loads(SPARC_PHYSICAL.read_text(encoding="utf-8"))
    universal_collector = json.loads(
        UNIVERSAL_COLLECTOR.read_text(encoding="utf-8")
    )
    nonlinear_collector_action = json.loads(
        NONLINEAR_COLLECTOR_ACTION.read_text(encoding="utf-8")
    )
    holo_collector_embedding = json.loads(
        HOLO_COLLECTOR_EMBEDDING.read_text(encoding="utf-8")
    )
    axisymmetric_collector = json.loads(
        AXISYMMETRIC_COLLECTOR.read_text(encoding="utf-8")
    )
    axisymmetric_solver = json.loads(AXISYMMETRIC_SOLVER.read_text(encoding="utf-8"))
    jordan_selector = json.loads(JORDAN_SELECTOR.read_text(encoding="utf-8"))
    jordan_deep_gate = json.loads(JORDAN_DEEP_GATE.read_text(encoding="utf-8"))
    bps_radion_matter = json.loads(
        BPS_RADION_MATTER.read_text(encoding="utf-8")
    )
    bps_biscalar_matter = json.loads(
        BPS_BISCALAR_MATTER.read_text(encoding="utf-8")
    )
    bps_volume_constraint = json.loads(
        BPS_VOLUME_CONSTRAINT.read_text(encoding="utf-8")
    )
    nonlinear_route_matrix = json.loads(
        NONLINEAR_ROUTE_MATRIX.read_text(encoding="utf-8")
    )
    mechanism_campaign = json.loads(MECHANISM_CAMPAIGN.read_text(encoding="utf-8"))
    master_registry = json.loads(MASTER_REGISTRY.read_text(encoding="utf-8"))
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))

    pages_match = re.search(r"^Pages:\s+(\d+)$", info, flags=re.MULTILINE)
    pages = int(pages_match.group(1)) if pages_match else 0
    record(checks, "page_count", 6 <= pages <= 20, pages)
    record(checks, "metadata_title", "A single Einstein" in info, info.splitlines()[0])
    record(checks, "metadata_author", "Author:          Adrian Bohoyo" in info, "Adrian Bohoyo")

    required_text = {
        "effective_action": "geometry-preserving effective completion",
        "positive_kinetic": "strictly positive",
        "delta_correlation": "0.999999905",
        "spectrum_value": "1.5455",
        "ir_proxy": "0.203",
        "planck_omega": "0.315",
        "planck_hubble": "67.4",
        "planck_sigma8": "0.811",
        "boss_ed": "2.266",
        "boss_lcdm": "2.443",
        "boss_delta": "0.177",
        "nist_null": "22.59",
        "doi": "10.5281/zenodo.18224589",
        "forward_boundary": "forward predictive model",
        "comparison_scope": "not a benchmark",
        "conditional_interface": "compact-interval matter",
        "derived_beta_zero": "0.0542901",
        "derived_force_fraction": "5.89483",
        "first_positive_trace_mass": "0.913899",
        "blind_derivation": "No observational input enters",
        "independent_shooting": "separate shooting solve",
        "legacy_clock_boundary": "does not constitute a clock detection",
        "same_scalar_dof": "not an additional scalar tower",
        "cassini_exclusion": "massless unscreened Neumann branch is therefore",
        "positive_tower_strength": "7.20230",
        "corrected_ricci": "corrected value spans",
        "ricci_rms": "26.91",
        "wilson_boundary": "loop feeds the geometry",
        "material_transfer": "transfer law, not a predicted signal",
        "modern_lattice_ratio": "1.7195",
        "nd_ultralight_mass": "0.00274476",
        "nd_ultralight_beta": "0.0542910",
        "em_coordinate_span": "4.90458",
        "em_coordinate_error": "0.395739",
        "em_measure_invariance": "6.27",
        "photon_first_mass": "0.652597",
        "photon_second_mass": "1.301427",
        "scalar_photon_vertex": "3.94563",
        "double_comb": "double-comb",
        "robin_ir_no_go": "0.002744976",
        "robin_avoided_gap": "0.0119229",
        "robin_identity": "Hellmann",
        "sparc_crossval_split": "122/26/27",
        "sparc_repaired_rar_acceleration": "1.14414",
        "sparc_repaired_rar_score": "36.75",
        "sparc_repaired_p5_score": "290.98",
        "sparc_p6_corrected_score": "414.20",
        "sparc_stiff_score": "371.58",
        "sparc_repaired_newton_score": "414.23",
        "sparc_repaired_rar_velocity_error": "14.5",
        "sparc_holo_force_gate": "not relabelled as a HOLO force law",
        "sparc_stiff_is_current": "current physical curve",
        "sparc_finite_disk": "geometry-matched finite-range scan",
        "sparc_residual_crossing": "6.25719",
        "sparc_600_radius_audit": "390.85",
        "sparc_600_range_audit": "371.72",
        "sparc_collector_ceiling": "23.9192",
        "sparc_collector_scope": "one law works at all physical length scales",
        "collector_action_inversion": "3.46",
        "collector_action_degeneracy": "degenerately",
        "collector_embedding_scaling": "regular weak-field branch obeys",
        "axisymmetric_curl": "2.11",
        "collector_mass_small": "2.955",
        "collector_mass_large": "2.955",
        "collector_milky_way_radius": "8.55",
        "collector_action_boundary": "not a result of the existing bulk",
        "axisymmetric_defined_source_gate": "NGC 2403 and NGC 3198 pass",
        "axisymmetric_solver_score": "237.10",
        "selector_frame_identity": "gives the exact Jordan-frame terms",
        "selector_direct_obstruction": "frame map becomes singular",
        "selector_surviving_architecture": (
            "tensor term nondegenerate"
        ),
        "selector_early_linearization": "concrete reason the nonlinear branch",
        "desi_holo_diagonal": "2.6917",
        "desi_lcdm_diagonal": "2.4189",
        "wilson_fail_closed": "fails closed",
        "p7_static_recovery": "stiff force in Eq.",
        "p7_dynamic_kernel": "radial Green function",
        "p7_frequency_comb": "4.214303",
        "p7_causal_timing": "signal front cannot arrive before",
        "nist_shared_reference": "engineering observable with a shared reference",
    }
    for name, needle in required_text.items():
        record(checks, f"text:{name}", needle.lower() in text_normalized, needle)

    for number in range(1, 16):
        marker = f"Figure {number}:"
        record(checks, f"figure_caption:{number}", marker in text, marker)

    original_assets = [
        "glueball_ratio.png",
        "fig_spectroscopy.pdf",
        "multiarm_svd_diagnostic.png",
        "fig_single_arm_modal_responses.pdf",
        "bulk_clock_5d.png",
        "nist_baseline_vs_uv.png",
    ]
    for asset in original_assets:
        record(checks, f"original_figure:{asset}", asset in tex, asset)
    record(
        checks,
        "new_sparc_physical_figure",
        "fig_sparc_physical_audit.png" in tex,
        "fig_sparc_physical_audit.png",
    )
    record(
        checks,
        "new_nonlinear_collector_action_figure",
        "fig_nonlinear_collector_action.png" in tex,
        "fig_nonlinear_collector_action.png",
    )
    record(
        checks,
        "new_nonlinear_route_map_figure",
        "fig_nonlinear_route_map.png" in tex,
        "fig_nonlinear_route_map.png",
    )
    record(
        checks,
        "new_effective_figure",
        "fig_effective_reconstruction.png" in tex,
        "fig_effective_reconstruction.png",
    )
    record(
        checks,
        "new_probe_figure",
        "fig_minimal_probe_completion.png" in tex,
        "fig_minimal_probe_completion.png",
    )
    record(
        checks,
        "new_ricci_material_figure",
        "fig_ricci_material_audit.png" in tex,
        "fig_ricci_material_audit.png",
    )
    record(
        checks,
        "new_prediction_factory_figure",
        "fig_prediction_factory.png" in tex,
        "fig_prediction_factory.png",
    )
    record(
        checks,
        "new_em_double_comb_figure",
        "fig_em_double_comb.png" in tex,
        "fig_em_double_comb.png",
    )
    record(
        checks,
        "new_breathing_response_figure",
        "fig_breathing_response.png" in tex,
        "fig_breathing_response.png",
    )

    forbidden_text = [
        "??",
        "qquad",
        "We present",
        "MNRAS 000",
        "Preprint 29 August",
        "Compiled using MNRAS",
        "sub-percent accuracy",
        "closes the X = 1 gap",
        "why NIST clocks see no signal",
        "nine global parameters",
    ]
    for needle in forbidden_text:
        record(checks, f"forbidden:{needle}", needle not in text, needle)

    fatal_log_patterns = [
        "Undefined control sequence",
        "Reference `",
        "Citation `",
        "Overfull \\hbox",
        "Fatal error",
        "Emergency stop",
    ]
    for pattern in fatal_log_patterns:
        record(checks, f"log_clean:{pattern}", pattern not in log, pattern)

    record(checks, "effective_certificate", summary["passes"]["all"], summary["passes"])
    record(checks, "minimal_probe_certificate", minimal["passes"]["all"], minimal["passes"])
    record(checks, "shooting_certificate", shooting["passes"]["all"], shooting["passes"])
    record(
        checks,
        "ricci_wilson_certificate",
        ricci_wilson["passes"]["all"],
        ricci_wilson["passes"],
    )
    record(
        checks,
        "material_transducer_certificate",
        material["passes"]["all"],
        material["passes"],
    )
    record(
        checks,
        "boundary_branch_certificate",
        boundary["passes"]["all"],
        boundary["passes"],
    )
    record(
        checks,
        "nd_ultralight_certificate",
        nd_shooting["passes"]["all"],
        nd_shooting["passes"],
    )
    record(
        checks,
        "em_kernel_certificate",
        all(em_kernel["passes"].values()),
        em_kernel["passes"],
    )
    record(
        checks,
        "em_fingerprint_certificate",
        em_fingerprint["passes"]["all"],
        em_fingerprint["passes"],
    )
    record(
        checks,
        "robin_family_certificate",
        robin_family["passes"]["all"],
        robin_family["passes"],
    )
    record(
        checks,
        "breathing_response_certificate",
        breathing_response["passes"]["all"]
        and breathing_response["passes"]["static_p6_recovered"]
        and breathing_response["observational_inputs_read"] == []
        and breathing_response["historical_frequency_values_read"] == [],
        breathing_response["passes"],
    )
    record(
        checks,
        "desi_diagnostic_certificate",
        desi["passes"]["all"],
        desi["passes"],
    )
    record(
        checks,
        "sparc_crossval_evidence_label",
        sparc_crossval["classification"]
        == "retrospective_cross_validation_not_blind_confirmation",
        sparc_crossval["classification"],
    )
    record(
        checks,
        "sparc_physical_audit_certificate",
        sparc_physical["passes"]["all"]
        and not sparc_physical["adjudication"]["legacy_p5_accepted"]
        and not sparc_physical["adjudication"][
            "legacy_p5_represents_corrected_completion"
        ]
        and sparc_physical["adjudication"]["p6_current_curve_replaces_legacy_p5"]
        and sparc_physical["adjudication"]["p6_corrected_benchmark_status"]
        == "evaluated_exact_long_range_convolution_envelope"
        and sparc_physical["adjudication"]["corrected_completion_test_status"]
        == "stiff_force_and_effective_disk_scan_complete_no_finite_scale"
        and sparc_physical["adjudication"]["holo_acceleration_law_status"]
        == "action_derived_stiff_force_available_but_empirically_insufficient",
        sparc_physical["adjudication"],
    )
    record(
        checks,
        "master_registry_evidence_label",
        "no new physical detection" in master_registry["global_classification"],
        master_registry["global_classification"],
    )
    record(
        checks,
        "universal_collector_certificate",
        universal_collector["passes"]["all"]
        and "not_action_derivation" in universal_collector["classification"]
        and universal_collector["train_fit"]["per_galaxy_parameters"] == 0
        and universal_collector["six_hundred_disambiguation"]
        ["observed_radius_thresholds_test"][1]["stiff_long_range"]
        ["chi2_per_point"]
        > 100.0
        and universal_collector["six_hundred_disambiguation"]
        ["global_yukawa_range_test"]["test"][1]["chi2_per_point"]
        > 100.0,
        universal_collector["passes"],
    )
    record(
        checks,
        "nonlinear_collector_action_certificate",
        nonlinear_collector_action["passes"]["all"]
        and "not_derived_from_current_holo_bulk"
        in nonlinear_collector_action["classification"]
        and nonlinear_collector_action["source"]["per_galaxy_parameters"] == 0
        and nonlinear_collector_action["action_reconstruction"]["diagnostics"]
        ["minimum_mu"]
        > 0.0
        and nonlinear_collector_action["action_reconstruction"]["diagnostics"]
        ["minimum_longitudinal_elliptic_eigenvalue"]
        > 0.0
        and nonlinear_collector_action["action_reconstruction"]["diagnostics"]
        ["degenerately_elliptic_as_x_tends_to_zero"]
        and not nonlinear_collector_action["action_reconstruction"]["diagnostics"]
        ["uniformly_elliptic_on_x_greater_than_zero"]
        and nonlinear_collector_action["numerical_consistency_checks"]
        ["constitutive_inversion_closure_max_relative_error"]
        < 1.0e-8,
        nonlinear_collector_action["passes"],
    )
    record(
        checks,
        "holo_collector_embedding_gate",
        holo_collector_embedding["passes"]["audit_complete"]
        and not holo_collector_embedding["passes"]
        ["linearized_current_sector_can_embed_collector"]
        and "full_nonlinear_holo_completion_unresolved"
        in holo_collector_embedding["classification"]
        and holo_collector_embedding["scope"]
        ["observational_inputs_read_by_this_gate"]
        == [],
        holo_collector_embedding["passes"],
    )
    record(
        checks,
        "axisymmetric_collector_source_gate",
        axisymmetric_collector["passes"]["all"]
        and not axisymmetric_collector["sparc_source_identifiability"]
        ["physical_axisymmetric_pde_identifiable"]
        and axisymmetric_collector["sparc_source_identifiability"]["status"]
        == "FAIL_CLOSED_MISSING_UNIQUE_3D_BARYON_SOURCE"
        and axisymmetric_collector["analytic_and_numerical_controls"]
        ["spherical_plummer_cylindrical_finite_volume"]
        ["coarse_to_fine_l2_ratio"]
        > 3.5,
        axisymmetric_collector["passes"],
    )
    eligible = axisymmetric_solver["newtonian_source_gate"]["by_galaxy"]
    record(
        checks,
        "axisymmetric_defined_source_solver_certificate",
        not axisymmetric_solver["passes"]["all"]
        and axisymmetric_solver["audit_checks"]["all"]
        and axisymmetric_solver["passes"]["all_galaxy_solves_converged"]
        and eligible["NGC2403"]
        and eligible["NGC3198"]
        and not eligible["DDO154"]
        and not eligible["NGC2841"]
        and not axisymmetric_solver["passes"]
        ["operator_is_independent_of_vobs_genealogy"],
        axisymmetric_solver["passes"],
    )
    record(
        checks,
        "jordan_selector_identity_certificate",
        jordan_selector["checks"]["all"]
        and not jordan_selector["physical_gates"]["physical_completion"]
        and not jordan_selector["physical_gates"]
        ["weak_field_constraint_reduction_equals_local_s_times_X"],
        jordan_selector["physical_gates"],
    )
    record(
        checks,
        "jordan_deep_obstruction_certificate",
        jordan_deep_gate["checks"]["all"]
        and not jordan_deep_gate["physical_gates"]
        ["direct_s_as_full_planck_coefficient_completion"]
        and abs(jordan_deep_gate["diagnostics"]["selector_power_in_t"] - 1.0)
        < 2.0e-5
        and abs(jordan_deep_gate["diagnostics"]["conformal_power_in_t"] + 0.5)
        < 2.0e-5,
        jordan_deep_gate["physical_gates"],
    )
    record(
        checks,
        "bps_radion_matter_metric_certificate",
        bps_radion_matter["checks"]["all"]
        and not bps_radion_matter["q2Y_gate"]["q2Y_derived"]
        and not bps_radion_matter["q2Y_gate"]
        ["declared_separation_slice_minimal_lower_brane_passes"]
        and not bps_radion_matter["q2Y_gate"]
        ["declared_separation_slice_minimal_upper_brane_passes"]
        and not bps_radion_matter["full_moduli_space_gate"]
        ["unique_canonical_q_selected"],
        bps_radion_matter["q2Y_gate"],
    )
    record(
        checks,
        "bps_biscalar_matter_geometry_certificate",
        bps_biscalar_matter["checks"]["all"]
        and bps_biscalar_matter["physical_gates"]["physical_moduli_count"] == 2
        and bps_biscalar_matter["physical_gates"]
        ["finite_endpoint_physical_mode_count_resolved_here"]
        and not bps_biscalar_matter["physical_gates"]
        ["unique_tangent_selected_by_BPS_geometry"]
        and not bps_biscalar_matter["physical_gates"]
        ["existing_positive_diagonal_p2_or_p6_completion_selects_silent_tangent"]
        and not bps_biscalar_matter["physical_gates"]
        ["matter_Y_convention_fixed"]
        and not bps_biscalar_matter["physical_gates"]
        ["physical_q2Y_selector_derived"]
        and min(
            bps_biscalar_matter["moduli_metric"]["Khat_eigenvalues"]
        )
        > 0.0,
        bps_biscalar_matter["physical_gates"],
    )
    record(
        checks,
        "bps_volume_constraint_candidate_certificate",
        bps_volume_constraint["checks"]["all"]
        and bps_volume_constraint["selector_kernel_comparison"]["lower"]
        ["covariant_kernel_angle_degrees"]
        < 0.1
        and bps_volume_constraint["selector_kernel_comparison"]["upper"]
        ["covariant_kernel_angle_degrees"]
        > 80.0
        and bps_volume_constraint["lower_exact_alignment_fixed_jet_diagnostic"]
        ["F_level_set_curve"]["selector_second_derivative"]
        > 0.0
        and not bps_volume_constraint["physical_gates"]
        ["global_F_constraint_present_in_current_repository_action"]
        and not bps_volume_constraint["physical_gates"]
        ["minimal_minus_Y_over_C_has_requested_negative_q2Y_sign"]
        and not bps_volume_constraint["physical_gates"]
        ["shifted_s_equals_C_minus_1_operator_selected_by_current_action"]
        and not bps_volume_constraint["physical_gates"]
        ["physical_q2Y_vertex_derived"],
        bps_volume_constraint["physical_gates"],
    )
    record(
        checks,
        "nonlinear_route_matrix_certificate",
        nonlinear_route_matrix["passes"]["all"]
        and nonlinear_route_matrix["prototype_selection"]
        ["leading_research_hypotheses"][0]
        == "derivative_constitutive_scalar",
        nonlinear_route_matrix["prototype_selection"],
    )
    campaign_validation = subprocess.run(
        [
            "python3",
            str(FACTORY_ROOT / "validate_mechanism_campaign.py"),
            str(MECHANISM_CAMPAIGN),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    record(
        checks,
        "minimal_mechanism_campaign_contract",
        campaign_validation.returncode == 0,
        campaign_validation.stdout.strip() or campaign_validation.stderr.strip(),
    )
    receipt_mismatches: list[str] = []
    if campaign_validation.returncode == 0:
        campaign_receipts = list(mechanism_campaign["inputs"])
        for step in mechanism_campaign["steps"]:
            campaign_receipts.extend(step["evidence"]["artifact_receipts"])
        receipt_mismatches = [
            receipt["path"]
            for receipt in campaign_receipts
            if sha256(REPO_ROOT / receipt["path"]) != receipt["sha256"]
        ]
    else:
        receipt_mismatches = ["contract_invalid_receipts_not_opened"]
    record(
        checks,
        "minimal_mechanism_campaign_receipts",
        not receipt_mismatches,
        receipt_mismatches,
    )
    record(
        checks,
        "minimal_mechanism_campaign_claim_boundary",
        [step["status"] for step in mechanism_campaign["steps"]]
        == ["failed", "failed", "blocked"]
        and mechanism_campaign["verdict"]["status"] == "blocked"
        and not mechanism_campaign["claim_gate"]["mechanism_candidate"]
        and not mechanism_campaign["claim_gate"]["physical_completion"]
        and not mechanism_campaign["claim_gate"]["new_force_derived"]
        and not mechanism_campaign["claim_gate"]["lensing_derived"]
        and not mechanism_campaign["claim_gate"]["publication_authorized"],
        {
            "steps": [step["status"] for step in mechanism_campaign["steps"]],
            "verdict": mechanism_campaign["verdict"],
            "claim_gate": mechanism_campaign["claim_gate"],
        },
    )
    registered_campaign = master_registry["current_predictions"][
        "minimal_mechanism_campaign"
    ]
    registered_campaign_evidence = master_registry["artefacts"][
        "minimal_mechanism_campaign"
    ]
    registered_campaign_claim_gate = {
        key: registered_campaign.get(key)
        for key in mechanism_campaign["claim_gate"]
    }
    record(
        checks,
        "minimal_mechanism_campaign_registry_binding",
        registered_campaign_evidence["path"]
        == str(MECHANISM_CAMPAIGN.relative_to(REPO_ROOT))
        and registered_campaign_evidence["sha256"] == sha256(MECHANISM_CAMPAIGN)
        and registered_campaign["campaign_id"] == mechanism_campaign["campaign_id"]
        and registered_campaign["step_statuses"]
        == {
            step["id"]: step["status"]
            for step in mechanism_campaign["steps"]
        }
        and registered_campaign["target_blind"]
        == mechanism_campaign["objective"]["target_blind"]
        and registered_campaign_claim_gate == mechanism_campaign["claim_gate"]
        and registered_campaign["verdict"] == mechanism_campaign["verdict"],
        {
            "evidence": registered_campaign_evidence,
            "summary": registered_campaign,
            "expected_target_blind": mechanism_campaign["objective"][
                "target_blind"
            ],
            "expected_claim_gate": mechanism_campaign["claim_gate"],
            "expected_verdict": mechanism_campaign["verdict"],
        },
    )
    record(
        checks,
        "minimal_probe_observational_blinding",
        minimal["observational_inputs_read"] == [],
        minimal["observational_inputs_read"],
    )
    record(
        checks,
        "shooting_observational_blinding",
        shooting["observational_inputs_read"] == [],
        shooting["observational_inputs_read"],
    )
    beta_zero = minimal["zero_mode_prediction"]["beta_0"]
    force_fraction = minimal["zero_mode_prediction"][
        "relative_force_strength_2_beta_squared"
    ]
    record(
        checks,
        "minimal_probe_beta_zero",
        abs(beta_zero - 0.05429009535288237) < 1e-14,
        beta_zero,
    )
    record(
        checks,
        "minimal_probe_force_fraction",
        abs(force_fraction - 0.0058948289068501206) < 1e-14,
        force_fraction,
    )
    record(
        checks,
        "shooting_independent_method",
        not shooting["method"]["primary_solver_reused"]
        and not shooting["method"]["fem_matrix_reused"],
        shooting["method"],
    )
    record(
        checks,
        "original_revision_comparison",
        comparison["passed"],
        comparison["interpretation_checks"],
    )
    metrics = summary["preservation_metrics"]
    record(
        checks,
        "delta_metric_consistent",
        abs(metrics["delta_correlation"] - 0.9999999047611539) < 1e-12,
        metrics["delta_correlation"],
    )
    record(
        checks,
        "source_has_no_placeholders",
        not re.search(r"\(\?\?\)|\(\?\)|TODO|FIXME|TBD", tex),
        "no unresolved citation placeholders",
    )

    passed = all(item["passed"] for item in checks)
    manifest = {
        "schema": "holo-paper-revision-validation.v1",
        "passed": passed,
        "paper": {
            "source": str(SOURCE / "main.tex"),
            "pdf": str(PDF),
            "pdf_sha256": sha256(PDF),
            "pages": pages,
        },
        "original": {
            "path": str(ORIGINAL),
            "sha256": sha256(ORIGINAL),
        },
        "effective_action_summary_sha256": sha256(SUMMARY),
        "minimal_probe_completion_sha256": sha256(MINIMAL),
        "shooting_verification_sha256": sha256(SHOOTING),
        "ricci_wilson_interface_sha256": sha256(RICCI_WILSON),
        "material_transducer_sha256": sha256(MATERIAL),
        "boundary_branch_catalogue_sha256": sha256(BOUNDARY_BRANCHES),
        "nd_ultralight_shooting_sha256": sha256(ND_SHOOTING),
        "em_kernel_completion_sha256": sha256(EM_KERNEL),
        "em_spectral_fingerprint_sha256": sha256(EM_FINGERPRINT),
        "robin_boundary_family_sha256": sha256(ROBIN_FAMILY),
        "breathing_response_sha256": sha256(BREATHING_RESPONSE),
        "desi_diagnostic_sha256": sha256(DESI_DIAGNOSTIC),
        "sparc_crossval_sha256": sha256(SPARC_CROSSVAL),
        "sparc_physical_audit_sha256": sha256(SPARC_PHYSICAL),
        "axisymmetric_solver_sha256": sha256(AXISYMMETRIC_SOLVER),
        "jordan_selector_sha256": sha256(JORDAN_SELECTOR),
        "jordan_deep_gate_sha256": sha256(JORDAN_DEEP_GATE),
        "bps_biscalar_matter_geometry_sha256": sha256(BPS_BISCALAR_MATTER),
        "bps_volume_constraint_selector_sha256": sha256(
            BPS_VOLUME_CONSTRAINT
        ),
        "nonlinear_route_matrix_sha256": sha256(NONLINEAR_ROUTE_MATRIX),
        "minimal_mechanism_campaign_sha256": sha256(MECHANISM_CAMPAIGN),
        "master_prediction_registry_sha256": sha256(MASTER_REGISTRY),
        "original_revision_comparison_sha256": sha256(COMPARISON),
        "checks": checks,
    }
    manifest_path = PAPER_ROOT / "build" / "revision_validation.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    failed = [item["name"] for item in checks if not item["passed"]]
    print(f"validation_passed={passed}")
    print(f"checks={len(checks)} failed={len(failed)}")
    if failed:
        print("failed_checks=" + ",".join(failed))
    print(manifest_path)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
