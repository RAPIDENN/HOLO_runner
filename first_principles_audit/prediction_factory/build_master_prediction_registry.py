#!/usr/bin/env python3
"""Build the single fail-closed registry for the HOLO prediction factory.

The registry is deliberately a graph, not a list of attractive numbers.  Each
edge records whether the link is derived, conditional, phenomenological, or
blocked, together with the machine-readable artefact that supports that label.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

if __package__:
    from . import validate_mechanism_campaign as mechanism_contract
else:
    import validate_mechanism_campaign as mechanism_contract


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT_JSON = HERE / "MASTER_PREDICTION_REGISTRY.json"
OUT_MD = HERE / "MASTER_PREDICTION_REGISTRY.md"


def _read_json(relative: str) -> dict[str, Any]:
    return json.loads((REPO / relative).read_text(encoding="utf-8"))


def _sha256(relative: str) -> str:
    return hashlib.sha256((REPO / relative).read_bytes()).hexdigest()


def _evidence(relative: str) -> dict[str, str]:
    return {"path": relative, "sha256": _sha256(relative)}


def build_registry() -> dict[str, Any]:
    boundary_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "boundary_branch_catalogue.json"
    )
    shooting_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "nd_ultralight_shooting.json"
    )
    material_path = (
        "first_principles_audit/prediction_factory/material_predictions.json"
    )
    wilson_path = (
        "first_principles_audit/prediction_factory/wilson_data_manifest.json"
    )
    sparc_legacy_path = (
        "first_principles_audit/prediction_factory/sparc_crossval_report.json"
    )
    sparc_path = (
        "first_principles_audit/prediction_factory/sparc_physical_audit.json"
    )
    desi_path = (
        "first_principles_audit/prediction_factory/desi_dr1_growth_diagnostic.json"
    )
    em_path = (
        "first_principles_audit/prediction_factory/em_kernel_completion.json"
    )
    em_fingerprint_path = (
        "first_principles_audit/prediction_factory/em_spectral_fingerprint.json"
    )
    robin_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "robin_boundary_family.json"
    )
    breathing_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "breathing_response.json"
    )
    microscopic_boundary_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "superpotential_boundary_completion.json"
    )
    microscopic_shooting_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "superpotential_boundary_shooting.json"
    )
    stiff_force_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "stiff_boundary_force.json"
    )
    finite_disk_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "sparc_finite_disk_yukawa.json"
    )
    residual_bridge_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "force_residual_bridge.json"
    )
    collector_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "universal_residual_collector.json"
    )
    collector_action_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "nonlinear_collector_action.json"
    )
    collector_embedding_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "holo_collector_embedding_gate.json"
    )
    axisymmetric_collector_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "derive_axisymmetric_collector_certificate.json"
    )
    axisymmetric_solver_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "derive_axisymmetric_collector_solver.json"
    )
    jordan_selector_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "jordan_selector_embedding.json"
    )
    jordan_deep_gate_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "jordan_deep_limit_gate.json"
    )
    tricritical_bridge_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "tricritical_constitutive_bridge.json"
    )
    spectral_bridge_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "collective_spectral_bridge.json"
    )
    bulk_decision_gate_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "bulk_constitutive_decision_gate.json"
    )
    bulk_cubic_inventory_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "bulk_cubic_vertex_inventory.json"
    )
    gauge_invariant_cubic_route_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "gauge_invariant_cubic_route.json"
    )
    cubic_boundary_identifiability_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "cubic_boundary_identifiability.json"
    )
    radial_adm_quartic_seed_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "radial_adm_quartic_seed.json"
    )
    adm_quadratic_recovery_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "adm_quadratic_recovery.json"
    )
    adm_bmp_bps_flatness_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "adm_bmp_tricritical_necessity.json"
    )
    bps_radion_matter_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "bps_radion_matter_coupling.json"
    )
    bps_biscalar_matter_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "bps_biscalar_matter_geometry.json"
    )
    bps_volume_constraint_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "bps_volume_constraint_selector.json"
    )
    nonlinear_swarm_adjudication_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "nonlinear_swarm_adjudication.json"
    )
    nonlinear_route_matrix_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "holo_nonlinear_route_matrix.json"
    )
    minimal_mechanism_campaign_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "minimal_mechanism_campaign.json"
    )
    c2_band_edge_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "c2_band_edge_continuum.json"
    )
    dirac_bath_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "dirac_critical_bath_gate.json"
    )
    dirac_red_team_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "dirac_bath_red_team_map.json"
    )
    covariant_5d_origin_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "covariant_5d_pseudogap_gate.json"
    )
    khronon_stability_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "khronon_constraint_stability_gate.json"
    )
    scale_consistency_path = (
        "first_principles_audit/prediction_factory/artifacts/"
        "scale_consistency.json"
    )
    observation_path = (
        "first_principles_audit/prediction_factory/prediction_manifest.json"
    )

    boundary = _read_json(boundary_path)
    shooting = _read_json(shooting_path)
    material = _read_json(material_path)["payload"]
    wilson = _read_json(wilson_path)
    sparc = _read_json(sparc_path)
    desi = _read_json(desi_path)
    em = _read_json(em_path)
    em_fingerprint = _read_json(em_fingerprint_path)
    robin = _read_json(robin_path)
    breathing = _read_json(breathing_path)
    microscopic_boundary = _read_json(microscopic_boundary_path)
    microscopic_shooting = _read_json(microscopic_shooting_path)
    stiff_force = _read_json(stiff_force_path)
    finite_disk = _read_json(finite_disk_path)
    residual_bridge = _read_json(residual_bridge_path)
    collector = _read_json(collector_path)
    collector_action = _read_json(collector_action_path)
    collector_embedding = _read_json(collector_embedding_path)
    axisymmetric_collector = _read_json(axisymmetric_collector_path)
    axisymmetric_solver = _read_json(axisymmetric_solver_path)
    jordan_selector = _read_json(jordan_selector_path)
    jordan_deep_gate = _read_json(jordan_deep_gate_path)
    tricritical_bridge = _read_json(tricritical_bridge_path)
    spectral_bridge = _read_json(spectral_bridge_path)
    bulk_decision_gate = _read_json(bulk_decision_gate_path)
    bulk_cubic_inventory = _read_json(bulk_cubic_inventory_path)
    gauge_invariant_cubic_route = _read_json(gauge_invariant_cubic_route_path)
    cubic_boundary_identifiability = _read_json(
        cubic_boundary_identifiability_path
    )
    radial_adm_quartic_seed = _read_json(radial_adm_quartic_seed_path)
    adm_quadratic_recovery = _read_json(adm_quadratic_recovery_path)
    adm_bmp_bps_flatness = _read_json(adm_bmp_bps_flatness_path)
    bps_radion_matter = _read_json(bps_radion_matter_path)
    bps_biscalar_matter = _read_json(bps_biscalar_matter_path)
    bps_volume_constraint = _read_json(bps_volume_constraint_path)
    nonlinear_swarm_adjudication = _read_json(
        nonlinear_swarm_adjudication_path
    )
    nonlinear_route_matrix = _read_json(nonlinear_route_matrix_path)
    minimal_mechanism_campaign = mechanism_contract.load_and_validate(
        REPO / minimal_mechanism_campaign_path,
        repository_root=REPO,
    )
    if minimal_mechanism_campaign["campaign_id"] != "minimal-mechanism-ladder-20260831":
        raise ValueError("unexpected mechanism campaign identity")
    c2_band_edge = _read_json(c2_band_edge_path)
    dirac_bath = _read_json(dirac_bath_path)
    dirac_red_team = _read_json(dirac_red_team_path)
    covariant_5d_origin = _read_json(covariant_5d_origin_path)
    khronon_stability = _read_json(khronon_stability_path)
    if c2_band_edge.get("decision", {}).get("verdict") != (
        "KILL_C2_BAND_EDGE_WRONG_VARIATIONAL_SIGN"
    ):
        raise ValueError("band-edge negative control is not frozen")
    if dirac_bath.get("decision", {}).get("verdict") != (
        "SURVIVES_STATIC_SPECTRAL_GATE_BLOCKED_MICROSCOPIC_"
        "LOCAL_QFT_AND_HOLO"
    ):
        raise ValueError("unexpected Dirac bath gate verdict")
    if dirac_red_team.get("decision", {}).get("verdict") != (
        "SURVIVES_STATIC_SPECTRAL_RED_TEAM_BLOCKED_LOCAL_QFT_"
        "DYNAMICS_AND_HOLO"
    ):
        raise ValueError("unexpected Dirac bath red-team verdict")
    if covariant_5d_origin.get("decision", {}).get("verdict") != (
        "COVARIANT_5D_LIFSHITZ_SCALING_ROUTE_SURVIVES_"
        "DETERMINANT_MATCHING_AND_DYNAMICS_BLOCKED"
    ):
        raise ValueError("unexpected covariant 5D pseudogap-origin verdict")
    if khronon_stability.get("decision", {}).get("verdict") != (
        "GEOMETRIC_KHRONON_MATCHING_PRESERVES_LOCAL_CONSTRAINT_RANK_"
        "FULL_RETARDED_AND_WARPED_COMPLETION_BLOCKED"
    ):
        raise ValueError("unexpected khronon constraint/stability verdict")
    if not all(
        artifact.get("checks", {}).get("all") is True
        for artifact in (
            c2_band_edge,
            dirac_bath,
            dirac_red_team,
            covariant_5d_origin,
            khronon_stability,
        )
    ):
        raise ValueError("post-campaign microscopic gate checks are incomplete")
    scale_consistency = _read_json(scale_consistency_path)
    observations = _read_json(observation_path)

    branches: dict[str, Any] = {}
    for name, row in boundary["branches"].items():
        branches[name] = {
            "left_boundary": row["left_boundary"],
            "right_boundary": row["right_boundary"],
            "has_exact_massless_mode": row["has_exact_massless_mode"],
            "uv_point_probe_decouples": row["uv_point_probe_decouples"],
            "masses_mu": row["masses_mu"],
            "uv_probe_couplings_beta_n": row["uv_probe_couplings_beta_n"],
            "adjudication": row["adjudication"],
        }

    test = sparc["results"]["test"]
    rar_p5 = test["comparisons"]["rar_vs_legacy_p5_refit"]
    positive = material["positive_modes"]

    artefacts = {
        "boundary_branches": _evidence(boundary_path),
        "nd_shooting": _evidence(shooting_path),
        "material_fingerprint": _evidence(material_path),
        "wilson_input_audit": _evidence(wilson_path),
        "sparc_legacy_retrospective_cv": _evidence(sparc_legacy_path),
        "sparc_physical_input_audit": _evidence(sparc_path),
        "desi_dr1_diagonal_diagnostic": _evidence(desi_path),
        "em_kernel_completion": _evidence(em_path),
        "em_spectral_fingerprint": _evidence(em_fingerprint_path),
        "robin_boundary_family": _evidence(robin_path),
        "breathing_response": _evidence(breathing_path),
        "microscopic_boundary_completion": _evidence(microscopic_boundary_path),
        "microscopic_boundary_shooting": _evidence(microscopic_shooting_path),
        "stiff_boundary_force": _evidence(stiff_force_path),
        "sparc_finite_disk_yukawa": _evidence(finite_disk_path),
        "force_residual_bridge": _evidence(residual_bridge_path),
        "universal_residual_collector": _evidence(collector_path),
        "nonlinear_collector_action": _evidence(collector_action_path),
        "holo_collector_embedding_gate": _evidence(collector_embedding_path),
        "axisymmetric_collector_prototype": _evidence(axisymmetric_collector_path),
        "axisymmetric_collector_solver": _evidence(axisymmetric_solver_path),
        "jordan_selector_embedding": _evidence(jordan_selector_path),
        "jordan_deep_limit_gate": _evidence(jordan_deep_gate_path),
        "tricritical_constitutive_bridge": _evidence(tricritical_bridge_path),
        "collective_spectral_bridge": _evidence(spectral_bridge_path),
        "bulk_constitutive_decision_gate": _evidence(bulk_decision_gate_path),
        "bulk_cubic_vertex_inventory": _evidence(bulk_cubic_inventory_path),
        "gauge_invariant_cubic_route": _evidence(
            gauge_invariant_cubic_route_path
        ),
        "cubic_boundary_identifiability": _evidence(
            cubic_boundary_identifiability_path
        ),
        "radial_adm_quartic_seed": _evidence(radial_adm_quartic_seed_path),
        "adm_quadratic_recovery": _evidence(adm_quadratic_recovery_path),
        "adm_bmp_bps_radion_flatness": _evidence(adm_bmp_bps_flatness_path),
        "bps_radion_matter_metric": _evidence(bps_radion_matter_path),
        "bps_biscalar_matter_geometry": _evidence(bps_biscalar_matter_path),
        "bps_volume_constraint_selector": _evidence(
            bps_volume_constraint_path
        ),
        "nonlinear_swarm_adjudication": _evidence(
            nonlinear_swarm_adjudication_path
        ),
        "holo_nonlinear_route_matrix": _evidence(nonlinear_route_matrix_path),
        "minimal_mechanism_campaign": _evidence(minimal_mechanism_campaign_path),
        "c2_band_edge_continuum": _evidence(c2_band_edge_path),
        "dirac_critical_bath_gate": _evidence(dirac_bath_path),
        "dirac_bath_red_team_map": _evidence(dirac_red_team_path),
        "covariant_5d_pseudogap_gate": _evidence(covariant_5d_origin_path),
        "khronon_constraint_stability_gate": _evidence(khronon_stability_path),
        "scale_consistency": _evidence(scale_consistency_path),
        "observational_protocol": _evidence(observation_path),
    }

    return {
        "schema": "holo.master-prediction-registry.v1",
        "freeze_date_utc": "2026-08-31",
        "global_classification": (
            "executable prediction programme; no new physical detection and no "
            "clean confirmatory holdout in this checkout"
        ),
        "nodes": {
            "frozen_trace": "verified numerical input",
            "effective_action": "geometry-preserving inverse completion",
            "scalar_carrier": "derived local fluctuation degree of freedom",
            "boundary_action": (
                "minimal superpotential matching derived and rejected; stabilized "
                "curvatures remain unselected"
            ),
            "robin_phase_map": "derived positive endpoint-action family",
            "matter_probe": "canonically normalized UV matter vertex in stiff limit",
            "material_force": "current seven-mode stiff Yukawa candidate",
            "breathing_response": "conditional retarded scalar response",
            "laboratory_signal": "requires dimensional source and detector",
            "photon_localization": "bulk or brane branch not yet selected",
            "em_overlap_kernel": "action-derived family containing Eq. 39",
            "em_double_comb": "conditional scalar and photon spectral fingerprint",
            "photon_kk_tower": "bulk-Maxwell compact-interval eigenmodes",
            "galaxy_readout": (
                "action-derived stiff force tested; empirically insufficient and "
                "unique source convolution unavailable"
            ),
            "galaxy_residual_target": (
                "train-frozen universal signed response; empirical, not action-derived"
            ),
            "nonlinear_collector_action": (
                "locally elliptic but degenerate nonrelativistic action target; not HOLO-derived"
            ),
            "collector_embedding_gate": (
                "conditional no-go for the current regular linearized HOLO sector"
            ),
            "nonlinear_route_matrix": (
                "theory-only route generation with explicit killed branches"
            ),
            "minimal_mechanism_campaign": (
                "content-addressed sequential mechanism record; C1 and the current "
                "compact C2 are killed, while C3 is input-incomplete"
            ),
            "c2_band_edge_negative_control": (
                "post-campaign continuum test; exact exponent but wrong stable-bath sign"
            ),
            "dirac_static_spectral_candidate": (
                "explicit uniform-static Clifford bath; finite local QFT not exhibited"
            ),
            "dirac_bath_red_team": (
                "17-attack map; L1 passes while local QFT, dynamics and HOLO are blocked"
            ),
            "covariant_5d_pseudogap_origin_gate": (
                "local z=3/2 Lifshitz scaling background; exact same-action bath blocked"
            ),
            "khronon_geometric_matching_gate": (
                "convex covariant EFT and local flat constraints; full retarded and "
                "warped completion blocked"
            ),
            "derivative_constitutive_scalar": (
                "surviving architecture; microscopic derivative operator not derived"
            ),
            "critical_constitutive_bridge": (
                "exact three-halves mechanism; critical bulk realization not derived"
            ),
            "bps_moduli_matter_metric": (
                "minimal induced metrics derived on a separation slice; "
                "two-modulus canonical projection remains unselected"
            ),
            "axisymmetric_collector": (
                "four converged defined-source solves; two pass source closure, "
                "global a0 remains observation-trained"
            ),
            "growth_readout": "phenomenological cosmological dictionary",
            "wilson_observable": "analyser ready; gauge links absent",
            "qcd_scale": "requires Wilson ensembles and continuum scale setting",
        },
        "links": [
            {
                "id": "trace_to_effective_action",
                "from": "frozen_trace",
                "to": "effective_action",
                "status": "derived_inverse",
                "gate": "passed",
                "meaning": "The achieved profiles admit a positive-kinetic Einstein-scalar completion on the certified interval.",
            },
            {
                "id": "effective_action_to_scalar_carrier",
                "from": "effective_action",
                "to": "scalar_carrier",
                "status": "derived_local",
                "gate": "passed",
                "meaning": "The healthy gauge-invariant trace carrier follows locally from the completed action.",
            },
            {
                "id": "boundary_selects_spectrum",
                "from": "boundary_action",
                "to": "scalar_carrier",
                "status": "derived_microscopic_family_unselected",
                "gate": "blocked_finite_boundary_curvatures_not_derived",
                "meaning": (
                    "Minimal superpotential matching forces a massless scalar and is "
                    "rejected for a finite-range force. Positive endpoint curvatures "
                    "stabilize it, but the bulk does not select their values; the "
                    "stiff limit is a declared candidate, not a detection."
                ),
                "evidence": artefacts["microscopic_boundary_completion"],
            },
            {
                "id": "positive_robin_action_to_phase_map",
                "from": "boundary_action",
                "to": "robin_phase_map",
                "status": "derived_family_unselected",
                "gate": "passed_family_scan_missing_microscopic_boundary_coefficients",
                "meaning": (
                    "Positive quadratic endpoint terms map poles and UV residues; "
                    "IR stiffness alone cannot lift the light mode, while UV stiffness "
                    "causes a residue exchange through an avoided crossing."
                ),
                "evidence": artefacts["robin_boundary_family"],
            },
            {
                "id": "carrier_to_matter_coupling",
                "from": "scalar_carrier",
                "to": "matter_probe",
                "status": "derived_canonical_stiff_limit",
                "gate": "passed_for_declared_stiff_candidate",
                "meaning": (
                    "The quadratic gauge-invariant scalar action and UV matter "
                    "vertex fix seven positive residues without reusing NN trace "
                    "couplings."
                ),
                "evidence": artefacts["stiff_boundary_force"],
            },
            {
                "id": "matter_to_dimensionless_force",
                "from": "matter_probe",
                "to": "material_force",
                "status": "derived_for_stiff_boundary_candidate",
                "gate": "passed_dimensionless_force_scale_unfixed",
                "meaning": (
                    "The stiff candidate predicts a frozen seven-mode Yukawa comb "
                    "with sum(alpha)=0.106765; ell remains independent."
                ),
                "evidence": artefacts["stiff_boundary_force"],
            },
            {
                "id": "material_force_to_breathing_response",
                "from": "material_force",
                "to": "breathing_response",
                "status": "derived_linear_space_time_transfer",
                "gate": "passed_for_unselected_stiff_candidate",
                "meaning": (
                    "The stiff force is the zero-frequency slice. A harmonic source is "
                    "evanescent below each threshold and launches an outgoing "
                    "massive wave above it; all threshold ratios are correlated."
                ),
                "evidence": artefacts["breathing_response"],
            },
            {
                "id": "breathing_response_to_lab_signal",
                "from": "breathing_response",
                "to": "laboratory_signal",
                "status": "blocked_dimensional_and_source_readout",
                "gate": "missing_selected_boundary_independent_clock_source_coherence_and_detector",
                "meaning": (
                    "A measured mode frequency could fix ell, but an interaction "
                    "still requires an independent source or ambient occupation, "
                    "causal propagation, coherence, and a calibrated detector."
                ),
                "evidence": artefacts["breathing_response"],
            },
            {
                "id": "dimensionless_force_to_lab_signal",
                "from": "material_force",
                "to": "laboratory_signal",
                "status": "blocked",
                "gate": "missing_ell_source_detector_and_noise_model",
                "meaning": "No metres, newtons, displacement or significance can be predicted until these independent inputs are frozen.",
            },
            {
                "id": "photon_action_to_em_kernel",
                "from": "photon_localization",
                "to": "em_overlap_kernel",
                "status": "derived_family_conditional_on_bulk_photon",
                "gate": "bulk_or_brane_photon_branch_unselected",
                "meaning": (
                    "Eq. 39 is the conformal-coordinate form of the minimal bulk-Maxwell "
                    "measure. The historical numerical kernel mixed conformal and "
                    "domain-wall coordinates and is rejected."
                ),
                "evidence": artefacts["em_kernel_completion"],
            },
            {
                "id": "em_kernel_to_double_comb",
                "from": "em_overlap_kernel",
                "to": "em_double_comb",
                "status": "derived_given_bulk_photon_and_comoving_boundaries",
                "gate": "passed_as_conditional_dimensionless_template",
                "meaning": (
                    "The scalar lapse constraint fixes d_gamma,n and the same interval "
                    "fixes a photon KK tower; no free c_gamma is fitted at the Z=1 point."
                ),
                "evidence": artefacts["em_spectral_fingerprint"],
            },
            {
                "id": "bulk_photon_to_photon_kk_tower",
                "from": "photon_localization",
                "to": "photon_kk_tower",
                "status": "derived_given_bulk_photon",
                "gate": "passed_as_conditional_dimensionless_template",
                "meaning": (
                    "Neumann bulk Maxwell data give a flat massless photon plus a "
                    "correlated massive vector comb with UV charge residues."
                ),
                "evidence": artefacts["em_spectral_fingerprint"],
            },
            {
                "id": "em_double_comb_to_clock_signal",
                "from": "em_double_comb",
                "to": "laboratory_signal",
                "status": "blocked_dimensional_readout",
                "gate": "missing_ell_source_atomic_coefficients_and_physical_branch_selection",
                "meaning": (
                    "The normalized source-to-alpha transfer is derived, but hertz and "
                    "significance still require a physical branch, ell, a source and "
                    "atomic differential sensitivities."
                ),
                "evidence": artefacts["em_spectral_fingerprint"],
            },
            {
                "id": "trace_to_galaxy_readout",
                "from": "frozen_trace",
                "to": "galaxy_readout",
                "status": "action_derived_candidate_tested_negative",
                "gate": "missing_state_dependent_sector_and_unique_source_density",
                "meaning": (
                    "After repairing signed gas and stellar mass-to-light factors, "
                    "the stiff force improves on baryons but remains far worse than "
                    "the empirical RAR target. The effective-disk finite-range scan "
                    "runs to the long-range boundary; disk cancellation does not "
                    "rescue it. Public tables do not identify the unique 3D source."
                ),
                "evidence": artefacts["sparc_finite_disk_yukawa"],
            },
            {
                "id": "galaxy_residual_to_universal_collector",
                "from": "galaxy_readout",
                "to": "galaxy_residual_target",
                "status": "retrospective_universal_target_derived_from_train_data",
                "gate": "missing_action_derived_nonlinear_or_ultralight_sector",
                "meaning": (
                    "One train-fitted acceleration scale maps the signed residual "
                    "without per-galaxy parameters. It beats the rigid force on the "
                    "frozen test split, but remains an empirical target rather than "
                    "a HOLO prediction."
                ),
                "evidence": artefacts["universal_residual_collector"],
            },
            {
                "id": "universal_collector_to_nonlinear_action",
                "from": "galaxy_residual_target",
                "to": "nonlinear_collector_action",
                "status": "phenomenological_nonrelativistic_action_reconstruction",
                "gate": "missing_microscopic_holo_and_relativistic_completion",
                "meaning": (
                    "The collector defines a single-valued, locally elliptic scalar "
                    "action with the correct deep and Newtonian limits, but the "
                    "operator degenerates as the field tends to zero. Its transition is "
                    "set by acceleration, so the corresponding radius depends on "
                    "source mass; this action is reconstructed from the empirical "
                    "target rather than derived from the current HOLO bulk."
                ),
                "evidence": artefacts["nonlinear_collector_action"],
            },
            {
                "id": "current_holo_to_nonlinear_collector",
                "from": "scalar_carrier",
                "to": "nonlinear_collector_action",
                "status": "conditional_no_go_current_linearized_regular_sector",
                "gate": "failed_source_scaling_and_operator_class",
                "meaning": (
                    "The current positive canonical carrier and its source-independent "
                    "Yukawa tower scale as M and have F proportional to X near vacuum. "
                    "The collector requires sqrt(M) and F proportional to X^(3/2). "
                    "Regular boundary potentials or field redefinitions cannot bridge "
                    "that mismatch; nonperturbative or new derivative sectors remain open."
                ),
                "evidence": artefacts["holo_collector_embedding_gate"],
            },
            {
                "id": "collector_target_to_nonlinear_route_matrix",
                "from": "nonlinear_collector_action",
                "to": "nonlinear_route_matrix",
                "status": "theory_only_route_generation_with_falsifiers",
                "gate": "no_route_is_yet_a_microscopic_force_prediction",
                "meaning": (
                    "The exact Legendre envelope and shell residual generate "
                    "candidate mechanisms. Fixed Yukawa poles, gapped tree "
                    "elimination and the direct full-Planck Jordan selector are "
                    "negative controls rather than promoted explanations."
                ),
                "evidence": artefacts["holo_nonlinear_route_matrix"],
            },
            {
                "id": "nonlinear_route_matrix_to_minimal_mechanism_campaign",
                "from": "nonlinear_route_matrix",
                "to": "minimal_mechanism_campaign",
                "status": "recorded_sequential_adjudication_blocked",
                "gate": "c3_input_contract_incomplete",
                "meaning": (
                    "The fail-closed ladder rejects the disclosed C1 candidate and "
                    "the current frozen compact C2 spectrum. C3 is not falsified: "
                    "nine microscopic action, constraint, source and branch-selection "
                    "inputs remain absent. Three Skai review attempts returned provider "
                    "errors and therefore contribute no physics evidence."
                ),
                "evidence": artefacts["minimal_mechanism_campaign"],
            },
            {
                "id": "minimal_campaign_to_band_edge_negative_control",
                "from": "minimal_mechanism_campaign",
                "to": "c2_band_edge_negative_control",
                "status": "post_campaign_outside_scope_continuum_falsified",
                "gate": "killed_wrong_AQUAL_variational_sign",
                "meaning": (
                    "A z=2 gapless band edge realizes the exact three-halves "
                    "pressure law left outside the compact C2 no-go, but stable "
                    "equilibrium occupation induces the opposite variational sign."
                ),
                "evidence": artefacts["c2_band_edge_continuum"],
            },
            {
                "id": "band_edge_to_dirac_static_spectral_candidate",
                "from": "c2_band_edge_negative_control",
                "to": "dirac_static_spectral_candidate",
                "status": "uniform_static_spectral_construction_survives",
                "gate": "finite_local_QFT_radiative_and_dynamic_completion_missing",
                "meaning": (
                    "Replacing the chemical-shift bath by a filled Clifford sea "
                    "fixes the deep variational sign and derives a0=Lambda/y. The "
                    "result is pointwise and static, not a finite local QFT or force."
                ),
                "evidence": artefacts["dirac_critical_bath_gate"],
            },
            {
                "id": "dirac_static_candidate_to_red_team_map",
                "from": "dirac_static_spectral_candidate",
                "to": "dirac_bath_red_team",
                "status": "adversarial_static_gate_pass_with_blockers",
                "gate": "first_blocked_level_L2_finite_local_QFT",
                "meaning": (
                    "The attack map closes static algebra and convexity at L0-L1, "
                    "then blocks promotion at finite regulation, temporal response, "
                    "radiative protection, current-HOLO origin and matter/lensing."
                ),
                "evidence": artefacts["dirac_bath_red_team_map"],
            },
            {
                "id": "dirac_red_team_to_covariant_5d_origin_gate",
                "from": "dirac_bath_red_team",
                "to": "covariant_5d_pseudogap_origin_gate",
                "status": "covariant_scaling_background_survives_exact_bath_blocked",
                "gate": "L2_scaling_pass_L3_same_action_determinant_blocked",
                "meaning": (
                    "A local 4+1 Einstein-Proca background with z=3/2 supplies the "
                    "required effective thermodynamic scaling exponent, but not a "
                    "literal single-particle DOS. Neither that scaling nor the free "
                    "fractional Clifford witness derives the required "
                    "determinant from the same local bulk action."
                ),
                "evidence": artefacts["covariant_5d_pseudogap_gate"],
            },
            {
                "id": "covariant_5d_origin_to_khronon_geometric_matching",
                "from": "covariant_5d_pseudogap_origin_gate",
                "to": "khronon_geometric_matching_gate",
                "status": "local_flat_geometric_reorganization_survives",
                "gate": "K2_local_rank_pass_K4_retarded_and_K5_warped_blocked",
                "meaning": (
                    "The covariant khronon EFT retains the positive bath quadratic "
                    "inside a convex F_eff and obtains the static cancellation only "
                    "after the metric/lapse Schur reduction. The exact mu and local "
                    "flat constraint count close; the same-action microscopic bath, "
                    "full retarded kernel and warped junction system do not."
                ),
                "evidence": artefacts["khronon_constraint_stability_gate"],
            },
            {
                "id": "matter_interface_to_derivative_constitutive_scalar",
                "from": "scalar_carrier",
                "to": "derivative_constitutive_scalar",
                "status": "surviving_architecture_operator_not_derived",
                "gate": "missing_bulk_derived_PY_a0_causality_slip_and_lensing",
                "meaning": (
                    "The exact matter-frame transformation diagnoses why early "
                    "linearization returns a mass-linear Yukawa response. Directly "
                    "using s as the full Jordan Planck coefficient is singular as "
                    "s tends to zero. The surviving route keeps the tensor "
                    "Einstein-Hilbert term nondegenerate and places s in a separate "
                    "collective scalar-gradient sector."
                ),
                "evidence": artefacts["jordan_deep_limit_gate"],
            },
            {
                "id": "quadratic_carrier_to_critical_constitutive_bridge",
                "from": "scalar_carrier",
                "to": "critical_constitutive_bridge",
                "status": "exact_exponent_mechanism_bulk_vertex_not_derived",
                "gate": "missing_q2Y_vertex_critical_selection_and_controlled_gradients",
                "meaning": (
                    "A tricritical collective amplitude gives exactly P(Y)=2Y^(3/2)/3 "
                    "and changes the deep source exponent from one to one half. The "
                    "current certified action reaches only the positive quadratic "
                    "carrier and does not yet select the required q^2Y vertex or "
                    "vanishing quadratic and quartic relevant couplings."
                ),
                "evidence": artefacts["tricritical_constitutive_bridge"],
            },
            {
                "id": "bps_moduli_to_even_matter_selector",
                "from": "scalar_carrier",
                "to": "bps_moduli_matter_metric",
                "status": "covariant_biscalar_jets_derived_physical_selector_open",
                "gate": "silent_tangent_exists_but_is_not_selected",
                "meaning": (
                    "The Einstein-frame induced metrics on the real functional-BPS "
                    "background are not stationary along the declared relative-"
                    "separation slice. The full finite-endpoint reduction resolves "
                    "two physical moduli with a positive kinetic metric. Each "
                    "single-brane selector has a covariant stationary direction "
                    "with a nonzero even jet, but no common direction exists and "
                    "the BPS, positive local quadratic, and positive local sextic "
                    "completions select none. The inverse-selector matter expansion "
                    "has the required negative candidate sign after its standard "
                    "term is separated, but its Y operator and normalization are "
                    "unidentified. The physical q^2Y vertex remains unproved."
                ),
                "evidence": artefacts["bps_biscalar_matter_geometry"],
            },
            {
                "id": "bps_volume_constraint_to_selected_even_mode",
                "from": "bps_moduli_matter_metric",
                "to": "critical_constitutive_bridge",
                "status": "near_alignment_found_minimal_completion_rejected",
                "gate": "constraint_absent_exact_alignment_absent_and_level_set_sign_wrong",
                "meaning": (
                    "A fixed warped-volume tangent is only 0.0686 degrees from "
                    "the lower-brane silent direction, but its residual is nonzero. "
                    "Exact alignment would require A'_-=0 outside the certified "
                    "interval. On the actual F-level curve, minimal -Y/C then has "
                    "the opposite q^2Y sign; obtaining the target requires an "
                    "additional shifted nonminimal operator. No global-F constraint "
                    "is present in the current action."
                ),
                "evidence": artefacts["bps_volume_constraint_selector"],
            },
            {
                "id": "critical_constitutive_bridge_to_physical_force",
                "from": "critical_constitutive_bridge",
                "to": "derivative_constitutive_scalar",
                "status": "prospective_bulk_test_defined_not_runnable",
                "gate": "unfrozen_boundary_scale_matter_causality_and_lensing_inputs",
                "meaning": (
                    "The fixed seven-mode spectrum mimics the three-halves slope for "
                    "only 0.210 dex. An exact spectral identity needs a gapless "
                    "constant density and still lacks a healthy local-generation sign. "
                    "A blind Dirichlet-to-Neumann amplitude scan is pre-registered, "
                    "but the microscopic inputs required to run it remain unfixed."
                ),
                "evidence": artefacts["bulk_constitutive_decision_gate"],
            },
            {
                "id": "nonlinear_action_to_axisymmetric_galaxies",
                "from": "nonlinear_collector_action",
                "to": "axisymmetric_collector",
                "status": "defined_source_solves_converged_mixed_source_gates",
                "gate": "two_of_four_source_closures_fail_and_global_a0_uses_vobs",
                "meaning": (
                    "A bounded reconstruction from archived density and metadata "
                    "profiles gives four converged AQUAL solves. NGC 2403 and "
                    "NGC 3198 pass the prospective Newtonian component closure; "
                    "DDO 154 and NGC 2841 fail through gas inversion. The operator "
                    "still inherits a0 from a Vobs-trained fit."
                ),
                "evidence": artefacts["axisymmetric_collector_solver"],
            },
            {
                "id": "trace_to_growth_readout",
                "from": "frozen_trace",
                "to": "growth_readout",
                "status": "phenomenological_dictionary",
                "gate": "external_diagnostic_not_full_likelihood",
                "meaning": "The frozen curve can be scored, but a 4D cosmological interface has not been derived.",
                "evidence": artefacts["desi_dr1_diagonal_diagnostic"],
            },
            {
                "id": "gauge_links_to_wilson_observable",
                "from": "wilson_observable",
                "to": "qcd_scale",
                "status": "blocked",
                "gate": "missing_su3_link_configurations",
                "meaning": "Rectangular loops, Creutz ratios and a continuum scale cannot be recovered from plaquette summaries or an ED endpoint proxy.",
                "evidence": artefacts["wilson_input_audit"],
            },
            {
                "id": "qcd_scale_to_compactification_length",
                "from": "qcd_scale",
                "to": "material_force",
                "status": "conditional_single_scale_no_go",
                "gate": "missing_uv_matching_or_separate_ultralight_sector",
                "meaning": (
                    "Forcing the same ell to realize the legacy 1.600 GeV proxy "
                    "and the SPARC long-range boundary creates a 40.94-order scale "
                    "mismatch. A UV relation or separate sector is required."
                ),
                "evidence": artefacts["scale_consistency"],
            },
        ],
        "current_predictions": {
            "boundary_branches": {
                "classification": "conditional numerical alternatives",
                "branches": branches,
                "nd_independent_shooting": {
                    "mu_lightest": shooting["mass_mu"],
                    "beta_uv": shooting["uv_coupling_beta"],
                    "certificate": shooting["passes"],
                },
                "result": (
                    "NN contains the excluded universal unscreened massless mode; "
                    "ND leaves an ultralight UV-coupled mode; DN and DD decouple "
                    "an exact UV point probe."
                ),
            },
            "robin_boundary_family": {
                "classification": robin["classification"],
                "C_p": robin["dimensionless_parameterization"][
                    "C_p_inverse_R_p"
                ],
                "ir_only_lightest_mass_ceiling": robin["ir_only_no_go"][
                    "hard_nd_mu_ceiling"
                ],
                "uv_residue_exchange_rho_brackets": robin[
                    "uv_avoided_crossing"
                ]["residue_exchange_brackets"],
                "minimum_avoided_crossing_gap": robin[
                    "uv_avoided_crossing"
                ]["minimum_first_pair_mass_gap"],
                "hellmann_feynman_identity": robin["hellmann_feynman"][
                    "identity"
                ],
                "physical_boundary_coefficients_selected": False,
            },
            "material_fingerprint": {
                "classification": material["classification"],
                "positive_mode_count": len(positive),
                "sum_alpha": material["short_distance_limits"]["sum_alpha_n"],
                "mass_ratios": [row["mu_n"] / positive[0]["mu_n"] for row in positive],
                "anchor_responses": material["distance_ratios"]["response_at_anchors"],
                "physical_units_available": False,
                "status": "legacy NN trace benchmark, superseded as physical candidate",
            },
            "stiff_boundary_force": {
                "classification": stiff_force["classification"],
                "mode_count": len(stiff_force["spectrum_and_force"]["masses_mu"]),
                "masses_mu": stiff_force["spectrum_and_force"]["masses_mu"],
                "strengths_alpha": stiff_force["spectrum_and_force"]
                ["alpha_uv_2_beta_squared"],
                "sum_alpha": stiff_force["spectrum_and_force"]
                ["sum_alpha_short_distance"],
                "maximum_circular_speed_multiplier": stiff_force[
                    "spectrum_and_force"
                ]["maximum_circular_speed_multiplier"],
                "ell_fixed": False,
                "physical_boundary_selected": False,
            },
            "breathing_response": {
                "classification": breathing["classification"],
                "stiff_static_slice_recovered": breathing["passes"][
                    "stiff_static_force_recovered"
                ],
                "threshold_frequency_ratios": [
                    row["threshold_frequency_over_f1"]
                    for row in breathing["correlated_mode_clock"]["modes"]
                ],
                "minimum_first_zero_duration_over_T1": breathing[
                    "correlated_mode_clock"
                ]["adjacent_resolution"]["minimum_first_zero_duration_over_T1"],
                "ell_fixed": False,
                "source_occupation_fixed": False,
                "physical_boundary_selected": False,
                "absolute_force_residues_available": breathing[
                    "microscopic_boundary_update"
                ]["stiff_stabilized_candidate"]["absolute_force_residues_available"],
            },
            "sparc": {
                "classification": sparc["classification"],
                "split_galaxies": sparc["protocol"]["split_counts"],
                "baryonic_contract": sparc["baryonic_contract"],
                "p5_optimizer_success": sparc["frozen_train_fits"]
                ["legacy_p5_on_repaired_inputs"]["optimizer"]["success"],
                "p5_parameters_at_bounds": sparc["frozen_train_fits"]
                ["legacy_p5_on_repaired_inputs"]["parameters_at_bounds"],
                "test_chi2_per_point": {
                    name: test["models"][name]["chi2_per_point"]
                    for name in (
                        "p6_corrected_long_range_envelope",
                        "stiff_boundary_long_range_envelope",
                        "legacy_p5_refit",
                        "newton",
                        "rar",
                    )
                },
                "test_rar_vs_p5_galaxy_win_fraction": rar_p5["left_win_fraction"],
                "rar_g_dagger_m_s2": sparc["frozen_train_fits"]["rar"]
                ["g_dagger_m_s2"],
                "rar_median_absolute_fractional_velocity_error": test["models"]
                ["rar"]["median_absolute_fractional_velocity_error"],
                "legacy_p5_accepted": sparc["adjudication"]["legacy_p5_accepted"],
                "p6_current_curve_replaces_legacy_p5": sparc["adjudication"][
                    "p6_current_curve_replaces_legacy_p5"
                ],
                "p6_corrected_benchmark_status": sparc["adjudication"][
                    "p6_corrected_benchmark_status"
                ],
                "p6_maximum_fractional_velocity_boost": sparc["frozen_train_fits"]
                ["p6_corrected_long_range_convolution_envelope"]
                ["maximum_fractional_velocity_boost"],
                "holo_acceleration_law_status": sparc["adjudication"]
                ["holo_acceleration_law_status"],
                "finite_disk_best_global_ell_kpc": finite_disk[
                    "baseline_scan"
                ]["best_ell_kpc"],
                "finite_disk_best_at_upper_boundary": finite_disk[
                    "baseline_scan"
                ]["best_at_upper_boundary"],
                "finite_disk_test_chi2_per_point": finite_disk["metrics"]
                ["finite_disk_at_train_selected_scale"]["test"]["chi2_per_point"],
                "finite_scale_identified": finite_disk["adjudication"]
                ["finite_scale_identified"],
                "disk_cancellation_rescues_stiff_candidate": finite_disk[
                    "adjudication"
                ]["disk_cancellation_rescues_stiff_candidate"],
                "zero_residual_crossing_gbar_m_s2": residual_bridge[
                    "parameters"
                ]["zero_differential_crossing_gbar_m_s2"],
                "collector_classification": collector["classification"],
                "collector_test_chi2_per_point": collector["metrics"]
                ["collector"]["test"]["chi2_per_point"],
                "collector_rigid_nu_ceiling": collector["frozen_inputs"]
                ["rigid_long_range_nu_ceiling"],
                "collector_required_nu_max": collector["acceleration_domain"]
                ["all_catalogue"]["collector_nu_max"],
                "collector_fraction_above_rigid_ceiling": collector[
                    "acceleration_domain"
                ]["all_catalogue"]["fraction_requiring_more_than_rigid_ceiling"],
                "radius_0p6_kpc_stiff_chi2_per_point": collector[
                    "six_hundred_disambiguation"
                ]["observed_radius_thresholds_test"][1]["stiff_long_range"]
                ["chi2_per_point"],
                "ell_600_kpc_stiff_chi2_per_point": collector[
                    "six_hundred_disambiguation"
                ]["global_yukawa_range_test"]["test"][1]["chi2_per_point"],
                "result": (
                    "The physical SPARC input contract is repaired. The action-derived "
                    "stiff force improves on baryons, but the geometry-matched scale "
                    "scan runs to the long-range boundary and remains far from RAR. "
                    "P6 and P5 are numerical genealogy only; the empirical residual "
                    "is a target for new microscopic physics, not a fitted force."
                ),
            },
            "nonlinear_collector_action": {
                "classification": collector_action["classification"],
                "a0_m_s2": collector_action["source"]["a0_m_s2"],
                "per_galaxy_parameters": collector_action["source"]
                ["per_galaxy_parameters"],
                "constitutive_inversion_closure_max_relative_error": collector_action[
                    "numerical_consistency_checks"
                ]["constitutive_inversion_closure_max_relative_error"],
                "plummer_pde_max_relative_residual": collector_action[
                    "numerical_consistency_checks"
                ]["spherical_plummer_pde"]
                ["maximum_finite_difference_pde_relative_residual"],
                "minimum_transverse_elliptic_eigenvalue": collector_action[
                    "action_reconstruction"
                ]["diagnostics"]["minimum_mu"],
                "minimum_longitudinal_elliptic_eigenvalue": collector_action[
                    "action_reconstruction"
                ]["diagnostics"]["minimum_longitudinal_elliptic_eigenvalue"],
                "uniformly_elliptic": collector_action["action_reconstruction"]
                ["diagnostics"]["uniformly_elliptic_on_x_greater_than_zero"],
                "degenerately_elliptic_at_zero": collector_action[
                    "action_reconstruction"
                ]["diagnostics"]["degenerately_elliptic_as_x_tends_to_zero"],
                "transition_mass_at_0p6_kpc_msun": collector_action["scale_map"]
                ["mass_implied_by_candidate_radius"]["0.6_kpc"]
                ["source_mass_for_gN_equal_a0_msun"],
                "transition_mass_at_600_kpc_msun": collector_action["scale_map"]
                ["mass_implied_by_candidate_radius"]["600_kpc"]
                ["source_mass_for_gN_equal_a0_msun"],
                "sun_transition_radius_au": collector_action["scale_map"]
                ["transition_radii_by_source_mass"]["Sun"]["radius_au"],
                "milky_way_transition_radius_kpc": collector_action["scale_map"]
                ["transition_radii_by_source_mass"]
                ["Milky_Way_baryons_6e10_Msun"]["radius_kpc"],
                "passes": collector_action["passes"]["all"],
            },
            "holo_collector_embedding_gate": {
                "classification": collector_embedding["classification"],
                "current_mass_exponent": collector_embedding[
                    "source_scaling_certificate"
                ]["current_fixed_radius_mass_exponent"],
                "collector_deep_mass_exponent_range": collector_embedding[
                    "source_scaling_certificate"
                ]["collector_deep_exponent_range"],
                "current_dlog_F_dlog_X": collector_embedding[
                    "operator_certificate"
                ]["current_dlog_F_dlog_X"],
                "collector_deep_dlog_F_dlog_X": collector_embedding[
                    "operator_certificate"
                ]["collector_deep_dlog_F_dlog_X"],
                "current_linearized_sector_can_embed": collector_embedding[
                    "passes"
                ]["linearized_current_sector_can_embed_collector"],
                "full_nonlinear_completion_resolved": False,
            },
            "nonlinear_route_matrix": {
                "classification": nonlinear_route_matrix["classification"],
                "leading_research_hypotheses": nonlinear_route_matrix[
                    "prototype_selection"
                ]["leading_research_hypotheses"],
                "direct_jordan_selector_status": next(
                    route["status"]
                    for route in nonlinear_route_matrix["routes"]
                    if route["id"] == "jordan_frame_gravitational_selector"
                ),
                "surviving_architecture_status": next(
                    route["status"]
                    for route in nonlinear_route_matrix["routes"]
                    if route["id"] == "derivative_constitutive_scalar"
                ),
                "selector_definition": jordan_selector["frame_derivation"]
                ["selector_definition"],
                "selector_power_in_t": jordan_deep_gate["diagnostics"]
                ["selector_power_in_t"],
                "conformal_power_in_t": jordan_deep_gate["diagnostics"]
                ["conformal_power_in_t"],
                "direct_full_planck_selector_completion": jordan_deep_gate[
                    "physical_gates"
                ]["direct_s_as_full_planck_coefficient_completion"],
                "physical_completion": False,
                "passes": nonlinear_route_matrix["passes"]["all"],
            },
            "minimal_mechanism_campaign": {
                "classification": "theory_only_sequential_campaign_blocked",
                "record_time_authentication": "not_timestamp_authenticated",
                "provenance_scope": minimal_mechanism_campaign["data_policy"]
                ["provenance_audit_scope"],
                "campaign_id": minimal_mechanism_campaign["campaign_id"],
                "target_blind": minimal_mechanism_campaign["objective"][
                    "target_blind"
                ],
                "step_statuses": {
                    step["id"]: step["status"]
                    for step in minimal_mechanism_campaign["steps"]
                },
                "step_reason_codes": {
                    step["id"]: step["reason_codes"]
                    for step in minimal_mechanism_campaign["steps"]
                },
                "skai_review_attempt_statuses": {
                    step["id"]: step["evidence"]["review_attempts"][0]["status"]
                    for step in minimal_mechanism_campaign["steps"]
                },
                "mechanism_candidate": minimal_mechanism_campaign["claim_gate"]
                ["mechanism_candidate"],
                "physical_completion": minimal_mechanism_campaign["claim_gate"]
                ["physical_completion"],
                "new_force_derived": minimal_mechanism_campaign["claim_gate"]
                ["new_force_derived"],
                "lensing_derived": minimal_mechanism_campaign["claim_gate"]
                ["lensing_derived"],
                "publication_authorized": minimal_mechanism_campaign["claim_gate"]
                ["publication_authorized"],
                "verdict": minimal_mechanism_campaign["verdict"],
            },
            "c2_band_edge_continuum": {
                "classification": c2_band_edge["classification"],
                "verdict": c2_band_edge["decision"]["verdict"],
                "pressure_log_slope": c2_band_edge["diagnostics"]
                ["pressure_log_slope"],
                "exact_exponent_derived": c2_band_edge["decision"]
                ["exact_exponent_and_positive_pressure_derived"],
                "required_variational_sign_derived": c2_band_edge["decision"]
                ["required_AQUAL_variational_sign_derived"],
                "candidate_survives": c2_band_edge["decision"]
                ["candidate_survives"],
                "raw_observational_tables_read_directly": c2_band_edge["sources"]
                ["raw_observational_tables_read_directly"],
                "inherited_target_origin": c2_band_edge["sources"]
                ["inherited_exposed_target_origin"],
                "physical_completion": c2_band_edge["decision"]
                ["physical_completion"],
            },
            "dirac_critical_bath_gate": {
                "classification": dirac_bath["classification"],
                "verdict": dirac_bath["decision"]["verdict"],
                "constitutive_function": dirac_bath["uniform_static_derivation"]
                ["constitutive_function"],
                "acceleration_scale": dirac_bath["uniform_static_derivation"]
                ["acceleration_scale"],
                "uniform_static_spectral_candidate": dirac_bath["decision"]
                ["uniform_static_spectral_candidate"],
                "finite_local_qft_realization_exhibited": dirac_bath["decision"]
                ["finite_local_qft_realization_exhibited"],
                "exact_exposed_collector_interpolation_reproduced": dirac_bath[
                    "decision"
                ]["exact_exposed_collector_interpolation_reproduced"],
                "maximum_absolute_mu_difference_from_exposed_target": dirac_bath[
                    "diagnostics"
                ]["maximum_absolute_mu_difference_from_exposed_target"],
                "inherited_target_origin": dirac_bath["sources"]
                ["inherited_exposed_target_origin"],
                "physical_completion": dirac_bath["decision"]
                ["physical_completion"],
                "publication_authorized": dirac_bath["decision"]
                ["publication_authorized"],
            },
            "dirac_bath_red_team": {
                "classification": dirac_red_team["classification"],
                "verdict": dirac_red_team["decision"]["verdict"],
                **dirac_red_team["summary"],
                "static_spectral_construction_survives": dirac_red_team[
                    "decision"
                ]["static_spectral_construction_survives"],
                "finite_local_qft_survives": dirac_red_team["decision"]
                ["finite_local_qft_survives"],
                "causal_covariant_completion_survives": dirac_red_team[
                    "decision"
                ]["causal_covariant_completion_survives"],
                "current_holo_mechanism": dirac_red_team["decision"]
                ["current_holo_mechanism"],
                "physical_completion": dirac_red_team["decision"]
                ["physical_completion"],
                "publication_authorized": dirac_red_team["decision"]
                ["publication_authorized"],
            },
            "covariant_5d_pseudogap_gate": {
                "classification": covariant_5d_origin["classification"],
                "verdict": covariant_5d_origin["decision"]["verdict"],
                "current_regular_compact_origin_survives": covariant_5d_origin[
                    "decision"
                ]["current_regular_compact_Einstein_dilaton_origin_survives"],
                "covariant_lifshitz_scaling_background_exhibited": (
                    covariant_5d_origin["decision"]
                    ["covariant_local_5D_Lifshitz_scaling_background_exhibited"]
                ),
                "effective_linear_state_counting_exponent_derived": (
                    covariant_5d_origin["decision"]
                    ["effective_linear_state_counting_exponent_from_5D_scaling"]
                ),
                "literal_boundary_single_particle_DOS_derived": covariant_5d_origin[
                    "decision"
                ]["literal_boundary_single_particle_DOS_derived"],
                "same_action_exact_Clifford_determinant_derived": (
                    covariant_5d_origin["decision"]
                    ["exact_Clifford_determinant_derived_from_same_local_5D_action"]
                ),
                "quadratic_matching_Ward_protected": covariant_5d_origin[
                    "decision"
                ]["quadratic_matching_is_Ward_protected"],
                "complete_constraint_and_time_stability": covariant_5d_origin[
                    "decision"
                ]["complete_constraint_rank_and_time_stability_derived"],
                "inherited_target_origin": covariant_5d_origin["sources"]
                ["inherited_target_origin"],
                "current_holo_mechanism": covariant_5d_origin["decision"]
                ["current_holo_mechanism"],
                "physical_completion": covariant_5d_origin["decision"]
                ["physical_completion"],
                "publication_authorized": covariant_5d_origin["decision"]
                ["publication_authorized"],
            },
            "khronon_constraint_stability_gate": {
                "classification": khronon_stability["classification"],
                "verdict": khronon_stability["decision"]["verdict"],
                "constitutive_function": khronon_stability["static_reduction"]
                ["constitutive_function"],
                "eta_critical": khronon_stability["diagnostics"]["eta_critical"],
                "eta_infinity": khronon_stability["diagnostics"]["eta_infinity"],
                "bath_delta_eta": khronon_stability["diagnostics"]
                ["bath_delta_eta"],
                "maximum_Schur_mu_error": khronon_stability["diagnostics"]
                ["maximum_Schur_mu_error"],
                "minimum_lapse_symbol": khronon_stability["diagnostics"]
                ["minimum_lapse_symbol"],
                "old_internal_quadratic_cancellation_required": khronon_stability[
                    "decision"
                ]["old_internal_bare_minus_bath_quadratic_cancellation_required"],
                "geometric_critical_matching_rule_derived": khronon_stability[
                    "decision"
                ]["geometric_critical_matching_rule_derived"],
                "exact_static_mu_from_Schur": khronon_stability["decision"]
                ["exact_static_mu_derived_from_action_Schur_complement"],
                "same_action_local_5D_microscopic_bath_derived": khronon_stability[
                    "decision"
                ]["same_action_local_5D_microscopic_bath_derived"],
                "fine_tuning_eliminated": khronon_stability["decision"]
                ["fine_tuning_eliminated"],
                "same_5D_action_and_background_closed": khronon_stability[
                    "decision"
                ]["same_5D_action_and_background_closed"],
                "static_effective_function_convex": khronon_stability["decision"]
                ["static_effective_acceleration_function_is_convex"],
                "local_lapse_constraint_rank_preserved": khronon_stability[
                    "decision"
                ]["local_flat_background_lapse_constraint_rank_preserved"],
                "khronometric_gravitational_DOF": khronon_stability[
                    "hessian_and_constraint_rank"
                ]["inventory"]["khronometric_gravitational_dof"],
                "truncated_z2_kernel_has_no_upper_half_plane_poles": (
                    khronon_stability["decision"]
                    ["truncated_z2_kernel_has_no_upper_half_plane_poles"]
                ),
                "full_microscopic_retarded_kernel_derived": khronon_stability[
                    "decision"
                ]["full_microscopic_retarded_kernel_derived"],
                "full_warped_brane_constraints_derived": khronon_stability[
                    "decision"
                ]["full_warped_brane_boundary_constraint_system_derived"],
                "complete_time_dependent_stability": khronon_stability[
                    "decision"
                ]["complete_time_dependent_stability"],
                "current_holo_mechanism": khronon_stability["decision"]
                ["current_holo_mechanism"],
                "physical_completion": khronon_stability["decision"]
                ["physical_completion"],
                "publication_authorized": khronon_stability["decision"]
                ["publication_authorized"],
            },
            "bulk_constitutive_decision_gate": {
                "classification": bulk_decision_gate["classification"],
                "old_source_mass_exponent": bulk_decision_gate["old_vs_this"]
                ["old_fixed_poles"]["source_mass_exponent"],
                "new_source_mass_exponent": bulk_decision_gate["old_vs_this"]
                ["this_critical_constitutive_response"]["source_mass_exponent"],
                "old_three_halves_crossover_width_dex": spectral_bridge[
                    "current_seven_mode_test"
                ]["within_0p05_log10_width_dex"],
                "tricritical_selector": tricritical_bridge["exact_mechanism"]
                ["tricritical_solution"],
                "minimal_radial_characteristic_ratio": bulk_decision_gate[
                    "principal_symbol_audit"
                ]["radial_over_transverse_characteristic_ratio"],
                "prospective_test_can_run": bulk_decision_gate[
                    "prospective_bulk_test"
                ]["can_run_with_current_frozen_inputs"],
                "physical_completion": bulk_decision_gate["physical_gates"]
                ["physical_completion"],
                "raw_metric_scalar_vertex_derived": bulk_cubic_inventory[
                    "checks"
                ]["densitized_inverse_first_variation_verified"],
                "fixed_metric_scalar_derivative_cubic_zero": (
                    bulk_cubic_inventory["checks"]
                    ["fixed_metric_scalar_derivative_cubic_is_zero"]
                ),
                "physical_overlap_coefficients_computed": bulk_cubic_inventory[
                    "physical_gates"
                ]["physical_overlap_coefficients_c_a_computed"],
                "gauge_invariant_S2_operator_match": gauge_invariant_cubic_route[
                    "physical_gates"
                ]["same_local_S2_operator_identified"],
                "stiff_to_gauge_invariant_mode_map": gauge_invariant_cubic_route[
                    "physical_gates"
                ]["linear_stiff_to_gauge_invariant_mode_map_identified"],
                "bmp_holographic_three_point_kernel_identified": gauge_invariant_cubic_route[
                    "physical_gates"
                ]["bmp_holographic_three_point_kernel_identified"],
                "compact_bulk_S3_action_derived": gauge_invariant_cubic_route[
                    "physical_gates"
                ]["compact_bulk_S3_action_derived"],
                "compact_S3_endpoint_terms_derived": gauge_invariant_cubic_route[
                    "physical_gates"
                ]["compact_endpoint_terms_derived"],
                "cubic_boundary_jet_nonidentifiability_proved": (
                    cubic_boundary_identifiability["physical_gates"]
                    ["boundary_jet_nonidentifiability_proved"]
                ),
                "natural_fixed_jet_stiff_path_defined": (
                    cubic_boundary_identifiability["physical_gates"]
                    ["natural_fixed_higher_jet_stiff_limit_defined"]
                ),
                "full_second_order_junction_source_derived": (
                    cubic_boundary_identifiability["physical_gates"]
                    ["full_second_order_junction_source_derived"]
                ),
                "formal_fixed_brane_GHY_and_potential_jet_convolution_verified": (
                    cubic_boundary_identifiability["physical_gates"]
                    ["formal_fixed_brane_GHY_prefactor_and_potential_jet_convolution_verified"]
                ),
                "quartic_stiff_eta_squared_uniformity_rule": (
                    cubic_boundary_identifiability["stiff_limit_paths"]
                    ["junction_scaling"]["quartic_eta_squared_response"]
                ),
                "exact_radial_ADM_bulk_density_derived": radial_adm_quartic_seed[
                    "physical_gates"
                ]["exact_bulk_ADM_scalar_density_identified"],
                "ADM_quartic_jet_generator_implemented": radial_adm_quartic_seed[
                    "physical_gates"
                ]["quartic_local_jet_generator_implemented"],
                "bulk_ADM_S2_compact_support_recovered": adm_quadratic_recovery[
                    "physical_gates"
                ]["same_variable_bulk_ADM_S2_action_recovered_on_compact_support"],
                "compact_master_ADM_S2_including_endpoints_recovered": (
                    adm_quadratic_recovery["physical_gates"]
                    ["compact_master_ADM_S2_including_endpoints_recovered"]
                ),
                "ADM_S2_backward_max_relative": adm_quadratic_recovery[
                    "verification"
                ]["periodic_compact_support_backward_test"][
                    "maximum_relative_error"
                ],
                "nonlinear_swarm_winner": nonlinear_swarm_adjudication[
                    "selection"
                ]["winner"],
                "nonlinear_swarm_current_score": nonlinear_swarm_adjudication[
                    "selection"
                ]["current_score"],
                "nonlinear_swarm_physical_c000": nonlinear_swarm_adjudication[
                    "hard_gates"
                ]["physical_c000_computed"],
                "physical_compact_S3_complete": gauge_invariant_cubic_route[
                    "physical_gates"
                ]["physical_S3_complete"],
                "direct_quartic_contact_computed": gauge_invariant_cubic_route[
                    "physical_gates"
                ]["direct_S4_contact_derived"],
                "conditional_functional_BPS_m2_zero": adm_bmp_bps_flatness[
                    "tricritical_gate"
                ]["m2_zero"],
                "conditional_functional_BPS_u4_zero": adm_bmp_bps_flatness[
                    "tricritical_gate"
                ]["u4_zero"],
                "conditional_functional_BPS_positive_q6": adm_bmp_bps_flatness[
                    "tricritical_gate"
                ]["positive_q6"],
                "conditional_positive_q6_from_sixth_order_brane_detuning": (
                    adm_bmp_bps_flatness["tricritical_gate"]
                    ["conditional_positive_q6_from_sixth_order_brane_detuning"]
                ),
                "sixth_order_brane_detuning_selected_by_bulk": (
                    adm_bmp_bps_flatness["localized_non_BPS_sextic_candidate"]
                    ["rho_i_selected_by_bulk"]
                ),
                "conditional_functional_BPS_q2Y_derived": adm_bmp_bps_flatness[
                    "tricritical_gate"
                ]["q2Y_derived"],
                "BPS_candidate_bulk_zero_mode_count": adm_bmp_bps_flatness[
                    "massless_kernel"
                ]["candidate_bulk_zero_mode_count"],
                "BPS_unique_canonical_q_selected": bps_radion_matter[
                    "full_moduli_space_gate"
                ]["unique_canonical_q_selected"],
                "BPS_separation_slice_lower_selector_c1": bps_radion_matter[
                    "endpoint_expansions_in_delta_R"
                ]["lower"]["c1"],
                "BPS_separation_slice_upper_selector_c1": bps_radion_matter[
                    "endpoint_expansions_in_delta_R"
                ]["upper"]["c1"],
                "BPS_minimal_separation_slice_pure_q2Y": bps_radion_matter[
                    "q2Y_gate"
                ]["pure_leading_q2Y_from_minimal_endpoint_matter"],
                "BPS_unselected_one_brane_orthogonal_tangent_exists": (
                    bps_radion_matter["q2Y_gate"]
                    ["some_unselected_two_modulus_tangent_can_kill_one_first_jet"]
                ),
                "BPS_same_tangent_stationary_for_both_matter_brane_metrics": (
                    bps_radion_matter["q2Y_gate"]
                    ["same_nonzero_tangent_can_kill_both_endpoint_first_jets"]
                ),
                "BPS_finite_endpoint_physical_moduli_count": (
                    bps_biscalar_matter["physical_gates"]
                    ["physical_moduli_count"]
                ),
                "BPS_Planck_normalized_kinetic_metric_eigenvalues": (
                    bps_biscalar_matter["moduli_metric"]["Khat_eigenvalues"]
                ),
                "BPS_lower_silent_covariant_selector_curvature": (
                    bps_biscalar_matter["selectors"]["lower"]
                    ["invariants_in_Khat_equals_6I_over_F_units"]
                    ["covariant_projected_curvature"]
                ),
                "BPS_upper_silent_covariant_selector_curvature": (
                    bps_biscalar_matter["selectors"]["upper"]
                    ["invariants_in_Khat_equals_6I_over_F_units"]
                    ["covariant_projected_curvature"]
                ),
                "BPS_lower_conditional_q2Y_coefficient": (
                    bps_biscalar_matter["selectors"]["lower"]
                    ["conditional_geodesic_mixed_jets"]
                    ["target_auxiliary_s_equals_one_minus_C"]
                    ["qbar_squared_Y_candidate_coefficient"]
                ),
                "BPS_upper_conditional_q2Y_coefficient": (
                    bps_biscalar_matter["selectors"]["upper"]
                    ["conditional_geodesic_mixed_jets"]
                    ["target_auxiliary_s_equals_one_minus_C"]
                    ["qbar_squared_Y_candidate_coefficient"]
                ),
                "BPS_positive_local_p2_or_p6_selects_silent_tangent": (
                    bps_biscalar_matter["physical_gates"]
                    ["existing_positive_diagonal_p2_or_p6_completion_selects_silent_tangent"]
                ),
                "BPS_matter_Y_operator_identified": bps_biscalar_matter[
                    "physical_gates"
                ]["matter_Y_convention_fixed"],
                "BPS_physical_q2Y_selector_derived": bps_biscalar_matter[
                    "physical_gates"
                ]["physical_q2Y_selector_derived"],
                "BPS_volume_constraint_lower_kernel_angle_degrees": (
                    bps_volume_constraint["selector_kernel_comparison"]["lower"]
                    ["covariant_kernel_angle_degrees"]
                ),
                "BPS_volume_constraint_lower_selector_residual": (
                    bps_volume_constraint["selector_kernel_comparison"]["lower"]
                    ["directional_residual_C_a_vF_a"]
                ),
                "BPS_volume_constraint_exact_alignment_on_background": (
                    bps_volume_constraint["physical_gates"]
                    ["lower_alignment_exact_on_certified_background"]
                ),
                "BPS_volume_constraint_F_level_q2Y_coefficient": (
                    bps_volume_constraint[
                        "lower_exact_alignment_fixed_jet_diagnostic"
                    ]["F_level_set_curve"]["expansions"]["minus_Y_over_C"]
                    ["qbar_squared_Y_coefficient"]
                ),
                "BPS_volume_constraint_present_in_action": (
                    bps_volume_constraint["physical_gates"]
                    ["global_F_constraint_present_in_current_repository_action"]
                ),
                "BPS_volume_constraint_physical_q2Y_derived": (
                    bps_volume_constraint["physical_gates"]
                    ["physical_q2Y_vertex_derived"]
                ),
                "functional_BPS_branch_selected_by_bulk": adm_bmp_bps_flatness[
                    "scope_boundary"
                ]["functional_BPS_branch_selected_by_bulk"],
                "m2_u4_zero_from_bulk_alone": adm_bmp_bps_flatness[
                    "scope_boundary"
                ]["m2_u4_zero_from_bulk_alone"],
                "BPS_raw_action_max_relative": adm_bmp_bps_flatness[
                    "raw_actual_interval_action"
                ]["maximum_relative_cancellation"],
                "synthetic_fixture_used_as_BPS_physical_evidence": not (
                    adm_bmp_bps_flatness["checks"]
                    ["synthetic_bent_geometry_not_imported"]
                ),
                "stiff_mode_map_max_rms_relative": gauge_invariant_cubic_route[
                    "linear_mode_map"
                ]["stiff_branch"]["strong_equation_check"]
                ["maximum_rms_relative"],
                "gapped_exchange_contribution_to_P": bulk_cubic_inventory[
                    "modal_reduction"
                ]["low_energy_result_if_c_a_were_known"],
                "total_Y2_coefficient": bulk_cubic_inventory[
                    "modal_reduction"
                ]["total_quartic_coefficient"],
                "passes": bulk_decision_gate["algebra_checks"]["all"],
            },
            "axisymmetric_collector": {
                "classification": axisymmetric_collector["classification"],
                "fine_plummer_l2_residual": axisymmetric_collector[
                    "analytic_and_numerical_controls"
                ]["spherical_plummer_cylindrical_finite_volume"]["fine"]
                ["weighted_relative_l2_residual"],
                "coarse_to_fine_l2_ratio": axisymmetric_collector[
                    "analytic_and_numerical_controls"
                ]["spherical_plummer_cylindrical_finite_volume"]
                ["coarse_to_fine_l2_ratio"],
                "flattened_normalized_curl": axisymmetric_collector[
                    "analytic_and_numerical_controls"
                ]["algebraic_field_integrability"]["flattened_miyamoto_nagai"]
                ["normalized_weighted_rms_curl"],
                "sparc_source_status": axisymmetric_collector[
                    "sparc_source_identifiability"
                ]["status"],
                "physical_sparc_pde_identifiable": axisymmetric_collector[
                    "sparc_source_identifiability"
                ]["physical_axisymmetric_pde_identifiable"],
                "effective_non_pde_test_chi2_per_point": axisymmetric_collector[
                    "effective_midplane_diagnostic"
                ]["frozen_test_score"]["chi2_per_point"],
                "resource_peak_array_mib": axisymmetric_collector["resource_bound"]
                ["conservative_peak_array_mib"],
                "passes": axisymmetric_collector["passes"]["all"],
                "defined_source_classification": axisymmetric_solver[
                    "classification"
                ],
                "defined_source_eligible_galaxies": axisymmetric_solver[
                    "newtonian_source_gate"
                ]["eligible_galaxies"],
                "defined_source_failed_galaxies": axisymmetric_solver[
                    "newtonian_source_gate"
                ]["failed_galaxies"],
                "ngc2403_chi2_per_point": axisymmetric_solver["galaxies"]
                ["NGC2403"]["score_after_prediction_only"]["chi2_per_point"],
                "ngc3198_chi2_per_point": axisymmetric_solver["galaxies"]
                ["NGC3198"]["score_after_prediction_only"]["chi2_per_point"],
                "all_defined_source_solves_converged": axisymmetric_solver[
                    "passes"
                ]["all_galaxy_solves_converged"],
                "defined_source_physical_completion": axisymmetric_solver[
                    "passes"
                ]["all"],
            },
            "scale_consistency": {
                "classification": scale_consistency["classification"],
                "ell_galaxy_over_ell_qcd": scale_consistency["comparison"]
                ["ell_galaxy_over_ell_qcd"],
                "orders_of_magnitude_in_ell": scale_consistency["comparison"]
                ["orders_of_magnitude_in_ell"],
                "galaxy_boundary_frequency_hz": scale_consistency[
                    "conditional_galaxy_boundary_reading"
                ]["cyclic_frequency_hz"],
                "galaxy_boundary_period_year": scale_consistency[
                    "conditional_galaxy_boundary_reading"
                ]["period_julian_year"],
                "single_scale_viable": scale_consistency["comparison"]
                ["single_ell_can_realize_both_identifications"],
            },
            "desi_dr1_growth": {
                "classification": desi["classification"],
                **desi["summary"],
            },
            "em_kernel": {
                "classification": em["classification"],
                "eq39_coordinate_certificate": em["bulk_maxwell_branch"][
                    "eq39_special_case"
                ]["coordinate_certificate"]["passes"],
                "coordinate_measure_max_abs_error": em["bulk_maxwell_branch"][
                    "eq39_special_case"
                ]["coordinate_certificate"][
                    "cumulative_measure_max_abs_difference"
                ],
                "legacy_max_abs_error_from_correct_u_kernel": em[
                    "historical_artifact_audit"
                ]["max_abs_difference_from_uniform_domain_wall_kernel"],
                "result": em["adjudication"],
            },
            "em_spectral_fingerprint": {
                "classification": em_fingerprint["classification"],
                "photon_positive_masses_mu": [
                    row["mu_gamma"]
                    for row in em_fingerprint["bulk_photon_tower"]["modes"][1:]
                ],
                "photon_uv_residues_relative_to_zero": [
                    row["uv_charge_coupling_squared_relative_to_zero_mode"]
                    for row in em_fingerprint["bulk_photon_tower"]["modes"][1:]
                ],
                "nn_positive_d_gamma_at_c0": [
                    row["d_gamma_at_c0"]
                    for row in em_fingerprint["scalar_boundary_branches"]["NN"][
                        "modes"
                    ][1:]
                ],
                "nd_d_gamma_at_c0": [
                    row["d_gamma_at_c0"]
                    for row in em_fingerprint["scalar_boundary_branches"]["ND"][
                        "modes"
                    ]
                ],
                "ell_fixed": False,
                "physical_branch_selected": False,
            },
            "wilson_loops": {
                "classification": wilson["status"],
                "fail_closed": wilson["fail_closed"],
                "sigma_a2": wilson["sigma_a2"],
                "result": "analyser tested; no usable gauge-link ensemble found",
            },
            "historical_boss_and_clock": observations["historical_audit_receipts"],
        },
        "next_falsifiable_runs": [
            {
                "priority": 1,
                "id": "blind_bulk_constitutive_amplitude_scan",
                "freeze_before_data": (
                    "S5, boundary actions, kappa5, ell, A_m, Standard-Model "
                    "localization and two conserved source geometries"
                ),
                "output": (
                    "Dirichlet-to-Neumann Pi(g), deep and high-field exponents, "
                    "fluctuation spectrum, characteristic cone, slip and lensing"
                ),
            },
            {
                "priority": 2,
                "id": "physical_boundary_selection",
                "freeze_before_data": "boundary/junction action and matter slice",
                "output": "one selected spectrum or an explicit proof that this compactification fails",
            },
            {
                "priority": 3,
                "id": "breathing_mode_drive_test",
                "freeze_before_data": (
                    "boundary action, independent clock anchor, source waveform, "
                    "separation, coherence, detector transfer and noise covariance"
                ),
                "output": (
                    "phase-resolved threshold scan with the complete correlated "
                    "frequency comb and causal delay"
                ),
            },
            {
                "priority": 4,
                "id": "bulk_photon_double_comb_test",
                "freeze_before_data": (
                    "bulk photon localization, ell, electrostatic source geometry, "
                    "clock species and distance bins"
                ),
                "output": (
                    "joint Coulomb, scalar-force and differential-clock template with "
                    "shared mass ratios"
                ),
            },
            {
                "priority": 5,
                "id": "dimensional_material_scan",
                "freeze_before_data": "ell, source geometry, detector transfer and distance bins",
                "output": "absolute force/displacement curve and null arms",
            },
            {
                "priority": 6,
                "id": "wilson_ensemble_export",
                "freeze_before_data": "thermalized SU(3) links, action, beta values and blocking plan",
                "output": "W(R,T), V_eff, Creutz plateaux and continuum sigma",
            },
            {
                "priority": 7,
                "id": "prospective_external_observation",
                "freeze_before_data": "model, likelihood, masks and nuisance policy",
                "output": "a preserved external holdout result, including a null or failure",
            },
        ],
        "artefacts": artefacts,
        "hard_rules": [
            "No boundary condition is selected from observational performance.",
            "No QCD scale is identified with ell without a separately derived UV matching relation.",
            "No retrospective split is called a blind confirmation.",
            "A weak or failed comparator result is preserved rather than recalibrated after unblinding.",
        ],
    }


def _fmt(value: float) -> str:
    return f"{value:.6g}"


def render_markdown(registry: dict[str, Any]) -> str:
    branch = registry["current_predictions"]["boundary_branches"]
    material = registry["current_predictions"]["material_fingerprint"]
    stiff = registry["current_predictions"]["stiff_boundary_force"]
    sparc = registry["current_predictions"]["sparc"]
    desi = registry["current_predictions"]["desi_dr1_growth"]
    wilson = registry["current_predictions"]["wilson_loops"]
    em = registry["current_predictions"]["em_kernel"]
    em_fingerprint = registry["current_predictions"]["em_spectral_fingerprint"]
    robin = registry["current_predictions"]["robin_boundary_family"]
    breathing = registry["current_predictions"]["breathing_response"]
    scale = registry["current_predictions"]["scale_consistency"]
    collector_action = registry["current_predictions"][
        "nonlinear_collector_action"
    ]
    collector_embedding = registry["current_predictions"][
        "holo_collector_embedding_gate"
    ]
    mechanism_campaign = registry["current_predictions"][
        "minimal_mechanism_campaign"
    ]
    band_edge = registry["current_predictions"]["c2_band_edge_continuum"]
    dirac_bath = registry["current_predictions"]["dirac_critical_bath_gate"]
    dirac_red_team = registry["current_predictions"]["dirac_bath_red_team"]
    covariant_origin = registry["current_predictions"][
        "covariant_5d_pseudogap_gate"
    ]
    khronon_stability = registry["current_predictions"][
        "khronon_constraint_stability_gate"
    ]
    bulk_gate = registry["current_predictions"][
        "bulk_constitutive_decision_gate"
    ]
    axisymmetric = registry["current_predictions"]["axisymmetric_collector"]

    rows = []
    for link in registry["links"]:
        rows.append(
            f"| `{link['id']}` | `{link['status']}` | `{link['gate']}` | "
            f"{link['meaning']} |"
        )

    next_rows = []
    for item in registry["next_falsifiable_runs"]:
        next_rows.append(
            f"{item['priority']}. **{item['id']}** — freeze: "
            f"{item['freeze_before_data']}. Output: {item['output']}."
        )

    return "\n".join(
        [
            "# Master prediction registry",
            "",
            "This is the executable evidence map for the current HOLO prediction programme. "
            "It is intentionally fail-closed: a computational link is not promoted to a "
            "physical link merely because both endpoints exist.",
            "",
            "## Link graph",
            "",
            "```mermaid",
            "flowchart LR",
            "  T[Frozen trace] -->|derived inverse| A[Effective action]",
            "  A -->|derived local carrier| C[Scalar carrier]",
            "  B[Boundary action] -->|positive Robin family| RP[Robin pole map]",
            "  B -.->|missing microscopic selector| C",
            "  C -->|conditional compact interval| M[Matter coupling]",
            "  M -->|derived vs r/ell| F[Material fingerprint]",
            "  F -->|retarded mode equation| BR[Breathing response]",
            "  BR -.->|missing clock + source + detector| L",
            "  F -.->|missing ell + apparatus| L[Laboratory signal]",
            "  P[Photon localization] -->|bulk Maxwell branch| K[EM overlap kernel]",
            "  K -->|scalar lapse constraint| D[Scalar-photon double comb]",
            "  P -->|Neumann bulk photon| V[Photon KK comb]",
            "  D -.->|missing ell + source + atomic response| L",
            "  T -->|phenomenological dictionary| G[Galaxy readout]",
            "  G -->|train-frozen residual| RC[Universal collector target]",
            "  RC -->|nonlinear reconstruction| NA[Nonrelativistic action]",
            "  C -.->|current linear sector: no-go| NA",
            "  NA -->|inverse-design falsifiers| NR[Nonlinear route matrix]",
            "  NR -->|content-addressed C1-C2-C3| MC[Minimal mechanism campaign]",
            "  MC -.->|outside-scope C2: wrong sign| BE[Band-edge negative control]",
            "  BE -->|filled Clifford sea| DB[Dirac static spectral candidate]",
            "  DB -.->|17 adversarial attacks; stops at L2| RT[Dirac red-team map]",
            "  RT -.->|L2 scaling only; determinant blocked| CO[Covariant 5D origin gate]",
            "  CO -.->|convex Schur matching; flat local gate| KG[Khronon matching gate]",
            "  C -.->|missing bulk-derived P(Y)| DS[Derivative constitutive scalar]",
            "  C -.->|missing q2Y + critical selector| CB[Critical constitutive bridge]",
            "  CB -.->|unfrozen matter + causal gates| DS",
            "  NA -.->|mixed source gates + trained a0| AX[Axisymmetric SPARC PDE]",
            "  T -->|phenomenological dictionary| R[Growth readout]",
            "  W[SU3 gauge links] -.->|missing inputs| Q[Wilson scale]",
            "  Q -.->|missing UV matching| F",
            "```",
            "",
            "| Link | Class | Gate | Meaning |",
            "|---|---|---|---|",
            *rows,
            "",
            "## Results already generated",
            "",
            f"- **Boundary audit:** ND has an independently checked ultralight mode "
            f"`mu={_fmt(branch['nd_independent_shooting']['mu_lightest'])}` with "
            f"`beta_UV={_fmt(branch['nd_independent_shooting']['beta_uv'])}`. NN has "
            "the massless mode; DN/DD decouple an exact UV point probe. No branch has "
            "been selected.",
            f"- **Material force:** the current stiff candidate has "
            f"{stiff['mode_count']} positive modes and "
            f"`sum(alpha)={_fmt(stiff['sum_alpha'])}`. The old "
            f"{material['positive_mode_count']}-mode NN/P6 result is retained only "
            "as trace genealogy; `ell` remains unfixed.",
            f"- **P7 breathing response:** the stiff force is recovered exactly at zero drive "
            "frequency. Below each scalar threshold the response is evanescent; "
            "above it the mode propagates with a subluminal group velocity. The "
            "seven threshold ratios are `"
            f"{', '.join(_fmt(value) for value in breathing['threshold_frequency_ratios'])}` "
            "times `f1`. This is a conditional transfer law, not a measured cosmic "
            "frequency or interaction.",
            f"- **Positive Robin family:** IR stiffness alone leaves "
            f"`mu_0<={_fmt(robin['ir_only_lightest_mass_ceiling'])}`. UV stiffness "
            "produces an avoided crossing with residue exchange; its minimum first-pair "
            f"gap is `{_fmt(robin['minimum_avoided_crossing_gap'])}`. The endpoint "
            "coefficients remain unselected theory inputs.",
            f"- **Functional-BPS radion:** the real-background bulk, GHY and brane "
            "action cancels for arbitrary separation to maximum relative residual "
            f"`{_fmt(bulk_gate['BPS_raw_action_max_relative'])}`. Thus the conditional "
            "branch has `m2=u4=0`, but also `q6=0`. A localized sixth-order brane "
            "detuning can supply positive `q6` conditionally; its coefficient is new "
            "brane physics, not selected by the bulk. No synthetic fixture enters "
            "this certificate. The same BPS reduction exposes two positive-norm "
            "zero-mode candidates, so a unique canonical `q` is not yet selected. "
            "Along the explicit lower-fixed separation slice, the normalized "
            f"matter-selector slopes are `{_fmt(bulk_gate['BPS_separation_slice_lower_selector_c1'])}` "
            f"and `{_fmt(bulk_gate['BPS_separation_slice_upper_selector_c1'])}` on "
            "the two branes, not zero. Minimal endpoint matter therefore does not "
            "produce a leading pure `q2Y` on that slice; an orthogonal two-modulus "
            "tangent can be written for one brane but is not selected or stabilized.",
            f"- **SPARC physical-input repair:** all "
            f"{sparc['baryonic_contract']['velocity_points_total']} velocity points "
            "were recomputed with signed gas and the declared stellar mass-to-light "
            "factors. Test chi2 per point is "
            f"`{_fmt(sparc['test_chi2_per_point']['rar'])}` for the empirical RAR, "
            f"`{_fmt(sparc['test_chi2_per_point']['stiff_boundary_long_range_envelope'])}` "
            "for the stiff force, "
            f"`{_fmt(sparc['test_chi2_per_point']['p6_corrected_long_range_envelope'])}` "
            "for the old P6 envelope, "
            f"`{_fmt(sparc['test_chi2_per_point']['legacy_p5_refit'])}` for legacy P5, "
            f"and `{_fmt(sparc['test_chi2_per_point']['newton'])}` for baryons alone. "
            f"The finite-disk scan selects its upper boundary at "
            f"`ell={_fmt(sparc['finite_disk_best_global_ell_kpc'])} kpc`, so no finite "
            "scale is identified. Interpreting 600 as either `R>=0.6 kpc` or "
            f"`ell=600 kpc` leaves the stiff score at "
            f"`{_fmt(sparc['radius_0p6_kpc_stiff_chi2_per_point'])}` and "
            f"`{_fmt(sparc['ell_600_kpc_stiff_chi2_per_point'])}` respectively. "
            f"The train-frozen universal signed collector reaches "
            f"`{_fmt(sparc['collector_test_chi2_per_point'])}`, but it is the empirical "
            "RAR target, not a HOLO prediction.",
            f"- **Nonlinear collector action target:** the reconstructed scalar "
            f"action closes an independent constitutive inversion to relative error "
            f"`{_fmt(collector_action['constitutive_inversion_closure_max_relative_error'])}` "
            "and a spherical Plummer finite-difference PDE control to "
            f"`{_fmt(collector_action['plummer_pde_max_relative_residual'])}`. It is "
            "locally elliptic for nonzero field but degenerates at zero field; no "
            "global existence or uniqueness theorem is claimed. Its transition is "
            "acceleration-controlled: `0.6 kpc` corresponds to "
            f"`{_fmt(collector_action['transition_mass_at_0p6_kpc_msun'])} Msun`, "
            "whereas `600 kpc` corresponds to "
            f"`{_fmt(collector_action['transition_mass_at_600_kpc_msun'])} Msun`. "
            "This is a phenomenological nonrelativistic reconstruction, not a "
            "microscopic or relativistic HOLO derivation.",
            f"- **HOLO embedding gate:** the current canonical weak-field response "
            f"scales with source mass as `M^{_fmt(collector_embedding['current_mass_exponent'])}`, "
            "whereas the collector tends to "
            f"`M^{_fmt(collector_embedding['collector_deep_mass_exponent_range'][0])}`. "
            f"The gradient-action powers are `{_fmt(collector_embedding['current_dlog_F_dlog_X'])}` "
            f"and `{_fmt(collector_embedding['collector_deep_dlog_F_dlog_X'])}`. "
            "Thus the present source-independent Yukawa tower and endpoint potentials "
            "cannot contain the collector through a regular weak-field embedding. This "
            "does not exclude a new derivative or nonperturbative IR sector.",
            f"- **Minimal mechanism ladder:** C1 is "
            f"`{mechanism_campaign['step_statuses']['C1']}`, the current frozen "
            f"compact C2 model is `{mechanism_campaign['step_statuses']['C2']}`, "
            f"and C3 is `{mechanism_campaign['step_statuses']['C3']}` because its "
            "microscopic input contract is incomplete. The campaign is explicitly "
            f"target-blind=`{str(mechanism_campaign['target_blind']).lower()}`: C1 "
            "tests a known candidate, C2 knows its acceptance target, and C3 knows "
            "the required mechanism structure. All three Skai review attempts ended "
            "in provider errors and are retained as inconclusive non-evidence. No "
            "mechanism candidate, physical completion, new force or lensing result is "
            "promoted. The record is content-addressed, but its record time is not "
            "independently authenticated.",
            f"- **Post-campaign microscopic branch:** the z=2 band edge derives "
            f"pressure exponent `{_fmt(band_edge['pressure_log_slope'])}` but is "
            f"`{band_edge['verdict']}` because a stable chemical bath has the wrong "
            "variational sign. A filled Clifford sea instead derives "
            f"`{dirac_bath['constitutive_function']}` and "
            f"`{dirac_bath['acceleration_scale']}` with the required static sign. "
            "That candidate matches only the target asymptotes, not its full "
            f"SPARC-trained curve (maximum absolute mu difference "
            f"`{_fmt(dirac_bath['maximum_absolute_mu_difference_from_exposed_target'])}`). "
            f"The adversarial map contains `{dirac_red_team['threat_count']}` threats: "
            f"its highest passed level is `{dirac_red_team['highest_level_passed']}` "
            f"and its first blocked level is `{dirac_red_team['first_blocked_level']}`. "
            "It is a uniform-static spectral construction, not a finite local QFT, "
            "causal HOLO completion, force, lensing result or publication.",
            f"- **Covariant 5D continuation:** the present regular compact "
            f"Einstein-dilaton origin survives=`"
            f"{str(covariant_origin['current_regular_compact_origin_survives']).lower()}`. "
            "A local isotropic `z=3/2` Einstein-Proca background supplies the required "
            "effective linear thermodynamic state-counting exponent, but not a "
            "literal single-particle DOS; scaling also does not derive "
            "the sharp Clifford determinant, its sign or normalization from that "
            "same action. The quadratic matching also has no Ward protection.",
            f"- **Geometric khronon reorganization:** retaining the positive bath "
            "quadratic inside a convex `F_eff` and eliminating the metric constraint "
            f"reproduces `{khronon_stability['constitutive_function']}` with maximum "
            f"Schur error `{_fmt(khronon_stability['maximum_Schur_mu_error'])}`. The "
            f"local flat 4+1 count is `{khronon_stability['khronometric_gravitational_DOF']}` "
            "gravitational modes and the lapse principal symbol stays positive. This "
            "removes the unstable internal bare-minus-bath cancellation, but not the "
            "codimension-one tuning: it is neither protected nor dynamically selected. "
            "The three-component boundary bath, four-spatial-component bulk khronon, "
            "nonzero radial acceleration of the Lifshitz background, full retarded "
            "kernel and warped brane constraints have not yet been joined into one "
            "action/background calculation.",
            f"- **Old versus critical response:** the old fixed tower has source "
            f"exponent `{_fmt(bulk_gate['old_source_mass_exponent'])}` and only "
            f"crosses the target three-halves slope for "
            f"`{_fmt(bulk_gate['old_three_halves_crossover_width_dex'])}` dex. "
            "The tricritical selector `s=sqrt(Y)` gives source exponent "
            f"`{_fmt(bulk_gate['new_source_mass_exponent'])}` exactly, but its "
            "bulk vertex and critical selection are not derived. The minimal "
            "covariant scalar has radial characteristic ratio "
            f"`{_fmt(bulk_gate['minimal_radial_characteristic_ratio'])}` and "
            "degenerates in vacuum; the prospective physical gate therefore "
            f"remains `{bulk_gate['physical_completion']}`.",
            f"- **Axisymmetric collector gate:** the cylindrical finite-volume control "
            f"has fine-grid relative L2 residual `{_fmt(axisymmetric['fine_plummer_l2_residual'])}` "
            f"and coarse/fine ratio `{_fmt(axisymmetric['coarse_to_fine_l2_ratio'])}`. "
            "For a flattened source the algebraic field has normalized curl "
            f"`{_fmt(axisymmetric['flattened_normalized_curl'])}`, so it is not an AQUAL "
            "solution. The SPARC solve remains "
            f"`{axisymmetric['sparc_source_status']}` because the local tables do not "
            "identify rho(R,z), thicknesses or boundary data; the existing "
            f"`chi2/point={_fmt(axisymmetric['effective_non_pde_test_chi2_per_point'])}` "
            "is retained only as a non-PDE algebraic diagnostic.",
            f"- **One-scale consistency:** identifying the same `ell` with the legacy "
            f"QCD proxy and the galactic long-range boundary disagrees by "
            f"`{_fmt(scale['orders_of_magnitude_in_ell'])}` orders of magnitude. "
            f"At the latter boundary `f0={_fmt(scale['galaxy_boundary_frequency_hz'])}` "
            "Hz, but that is a saturated scan edge, not a measured cosmic clock.",
            f"- **DESI DR1 marginal diagnostic:** diagonal chi2 is "
            f"`{_fmt(desi['diagonal_chi2_holo'])}` for the frozen HOLO dictionary and "
            f"`{_fmt(desi['diagonal_chi2_lcdm'])}` for matched LCDM "
            f"(`delta={_fmt(desi['delta_chi2_holo_minus_lcdm'])}`). This is not the "
            "official full likelihood and gives no preference for HOLO.",
            f"- **Eq. 39 electromagnetic kernel:** the minimal bulk-Maxwell measure "
            "is coordinate covariant to "
            f"`{_fmt(em['coordinate_measure_max_abs_error'])}`. The historical "
            "numerical kernel used domain-wall `u` as conformal `z` and differs from "
            f"the correct `Z=1` `u`-kernel by `{_fmt(em['legacy_max_abs_error_from_correct_u_kernel'])}`; "
            "that old projection is rejected.",
            f"- **Scalar-photon double comb:** the first positive bulk-photon masses "
            f"are `{', '.join(_fmt(value) for value in em_fingerprint['photon_positive_masses_mu'][:3])}`. "
            "The scalar lapse fixes branch-dependent `d_gamma,n`, while all photon and "
            "scalar masses share the same still-free `ell`. This is a conditional "
            "dimensionless fingerprint, not a detected signal.",
            f"- **Wilson route:** `{wilson['classification']}`. The analyser is ready "
            "and tested, but no rectangular-loop result or string tension can be "
            "computed from the available summaries.",
            "",
            "## Next falsifiable runs",
            "",
            *next_rows,
            "",
            "The JSON beside this document contains all exact values, relative paths, "
            "and SHA-256 hashes.",
            "",
        ]
    )


def main() -> None:
    registry = build_registry()
    OUT_JSON.write_text(
        json.dumps(registry, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    OUT_MD.write_text(render_markdown(registry), encoding="utf-8")
    print(f"[registry] {OUT_JSON}")
    print(f"[registry] {OUT_MD}")
    print("[classification] no new detection; links fail closed")


if __name__ == "__main__":
    main()
