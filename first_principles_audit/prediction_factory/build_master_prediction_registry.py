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
    sparc_path = (
        "first_principles_audit/prediction_factory/sparc_crossval_report.json"
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
    p5_newton = test["comparisons"]["p5_vs_newton"]
    p5_rar = test["comparisons"]["p5_vs_rar"]
    positive = material["positive_modes"]

    artefacts = {
        "boundary_branches": _evidence(boundary_path),
        "nd_shooting": _evidence(shooting_path),
        "material_fingerprint": _evidence(material_path),
        "wilson_input_audit": _evidence(wilson_path),
        "sparc_retrospective_cv": _evidence(sparc_path),
        "desi_dr1_diagonal_diagnostic": _evidence(desi_path),
        "em_kernel_completion": _evidence(em_path),
        "em_spectral_fingerprint": _evidence(em_fingerprint_path),
        "robin_boundary_family": _evidence(robin_path),
        "observational_protocol": _evidence(observation_path),
    }

    return {
        "schema": "holo.master-prediction-registry.v1",
        "freeze_date_utc": "2026-08-29",
        "global_classification": (
            "executable prediction programme; no new physical detection and no "
            "clean confirmatory holdout in this checkout"
        ),
        "nodes": {
            "frozen_trace": "verified numerical input",
            "effective_action": "geometry-preserving inverse completion",
            "scalar_carrier": "derived local fluctuation degree of freedom",
            "boundary_action": "physical selector not yet supplied",
            "robin_phase_map": "derived positive endpoint-action family",
            "matter_probe": "conditional UV-slice compact-interval probe",
            "material_force": "dimensionless six-mode Yukawa fingerprint",
            "laboratory_signal": "requires dimensional source and detector",
            "photon_localization": "bulk or brane branch not yet selected",
            "em_overlap_kernel": "action-derived family containing Eq. 39",
            "em_double_comb": "conditional scalar and photon spectral fingerprint",
            "photon_kk_tower": "bulk-Maxwell compact-interval eigenmodes",
            "galaxy_readout": "phenomenological radial dictionary",
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
                "status": "conditional_unselected",
                "gate": "blocked_missing_boundary_action",
                "meaning": "NN, ND, DN and DD are numerical alternatives; data may not select one after the fact.",
                "evidence": artefacts["boundary_branches"],
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
                "status": "derived_given_compact_interval_and_uv_probe",
                "gate": "conditional",
                "meaning": "beta_n=sqrt(I_g/3) f_n on the declared UV probe slice.",
            },
            {
                "id": "matter_to_dimensionless_force",
                "from": "matter_probe",
                "to": "material_force",
                "status": "derived_for_positive_nn_benchmark_modes",
                "gate": "passed_as_benchmark_not_physical_branch",
                "meaning": "A frozen correlated Yukawa force and gradient fingerprint versus x=r/ell.",
                "evidence": artefacts["material_fingerprint"],
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
                "status": "phenomenological_dictionary",
                "gate": "retrospective_cross_validation_only",
                "meaning": "Five global parameters are fitted on train galaxies; this is not a field-equation derivation.",
                "evidence": artefacts["sparc_retrospective_cv"],
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
                "status": "blocked",
                "gate": "missing_uv_matching_relation_ell_sqrt_sigma",
                "meaning": "Setting ell equal to a lattice spacing or QCD length would be an additional physical hypothesis.",
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
            },
            "sparc": {
                "classification": sparc["classification"],
                "split_galaxies": sparc["protocol"]["split_counts"],
                "p5_optimizer_success": sparc["frozen_fits"]["p5"]["optimizer"]["success"],
                "test_p5_minus_newton_delta_loglike_per_point": p5_newton[
                    "delta_loglike_per_point_left_minus_right"
                ],
                "test_p5_vs_newton_galaxy_win_fraction": p5_newton[
                    "left_win_fraction"
                ],
                "test_p5_minus_rar_delta_loglike_per_point": p5_rar[
                    "delta_loglike_per_point_left_minus_right"
                ],
                "test_p5_vs_rar_galaxy_win_fraction": p5_rar["left_win_fraction"],
                "result": (
                    "The current P5 refit improves on baryons-only Newton on the "
                    "retrospective test split but is decisively worse than the "
                    "one-parameter RAR baseline."
                ),
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
                "id": "physical_boundary_selection",
                "freeze_before_data": "boundary/junction action and matter slice",
                "output": "one selected spectrum or an explicit proof that this compactification fails",
            },
            {
                "priority": 2,
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
                "priority": 3,
                "id": "dimensional_material_scan",
                "freeze_before_data": "ell, source geometry, detector transfer and distance bins",
                "output": "absolute force/displacement curve and null arms",
            },
            {
                "priority": 4,
                "id": "wilson_ensemble_export",
                "freeze_before_data": "thermalized SU(3) links, action, beta values and blocking plan",
                "output": "W(R,T), V_eff, Creutz plateaux and continuum sigma",
            },
            {
                "priority": 5,
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
    sparc = registry["current_predictions"]["sparc"]
    desi = registry["current_predictions"]["desi_dr1_growth"]
    wilson = registry["current_predictions"]["wilson_loops"]
    em = registry["current_predictions"]["em_kernel"]
    em_fingerprint = registry["current_predictions"]["em_spectral_fingerprint"]
    robin = registry["current_predictions"]["robin_boundary_family"]

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
            "  F -.->|missing ell + apparatus| L[Laboratory signal]",
            "  P[Photon localization] -->|bulk Maxwell branch| K[EM overlap kernel]",
            "  K -->|scalar lapse constraint| D[Scalar-photon double comb]",
            "  P -->|Neumann bulk photon| V[Photon KK comb]",
            "  D -.->|missing ell + source + atomic response| L",
            "  T -->|phenomenological dictionary| G[Galaxy readout]",
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
            f"- **Material fingerprint:** {material['positive_mode_count']} positive "
            f"NN benchmark modes predict `sum(alpha)={_fmt(material['sum_alpha'])}` "
            "and a correlated decay versus `r/ell`; no dimensional signal is claimed.",
            f"- **Positive Robin family:** IR stiffness alone leaves "
            f"`mu_0<={_fmt(robin['ir_only_lightest_mass_ceiling'])}`. UV stiffness "
            "produces an avoided crossing with residue exchange; its minimum first-pair "
            f"gap is `{_fmt(robin['minimum_avoided_crossing_gap'])}`. The endpoint "
            "coefficients remain unselected theory inputs.",
            f"- **SPARC retrospective cross-validation:** P5 beats baryons-only Newton "
            f"in `{100*sparc['test_p5_vs_newton_galaxy_win_fraction']:.1f}%` of test "
            f"galaxies but beats RAR in only "
            f"`{100*sparc['test_p5_vs_rar_galaxy_win_fraction']:.1f}%`; its test "
            f"delta log-likelihood per point relative to RAR is "
            f"`{_fmt(sparc['test_p5_minus_rar_delta_loglike_per_point'])}`. This is "
            "development evidence, not blind confirmation.",
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
