#!/usr/bin/env python3
"""Build an adversarial attack map for the Dirac critical-bath candidate.

This is a scientific red-team artefact.  It treats every promoted statement as
an asset, every change of description as a trust boundary, and every missing
derivation as an exploit path.  Passing the uniform-static spectral checks is
not allowed to imply a finite local QFT, a covariant gravitational theory, a
current-HOLO origin, a force prediction or lensing.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DIRAC_GATE = HERE / "artifacts" / "dirac_critical_bath_gate.json"
BAND_EDGE = HERE / "artifacts" / "c2_band_edge_continuum.json"
CAMPAIGN = HERE / "artifacts" / "minimal_mechanism_campaign.json"
OUTPUT = HERE / "artifacts" / "dirac_bath_red_team_map.json"

SCHEMA = "holo.dirac-bath-red-team-map.v1"
PRIORITIES = ("P0", "P1", "P2")
BLOCKING_STATUSES = {"CONFIRMED_BLOCKER", "OPEN_BLOCKER"}


class RedTeamInputError(ValueError):
    """An attack-map input or row is malformed."""


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RedTeamInputError(f"cannot read {path}: {exc}") from exc
    if type(value) is not dict:
        raise RedTeamInputError(f"{path}: expected a JSON object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _threat(
    threat_id: str,
    *,
    priority: str,
    asset: str,
    boundary: str,
    exploit: str,
    result: str,
    status: str,
    kill_criterion: str,
    closure_evidence: str,
    executable_evidence: list[str] | None = None,
) -> dict[str, Any]:
    if priority not in PRIORITIES:
        raise RedTeamInputError(f"invalid priority for {threat_id}")
    if status not in {"CLOSED", "CONFIRMED_LIMITATION", *BLOCKING_STATUSES}:
        raise RedTeamInputError(f"invalid status for {threat_id}")
    return {
        "id": threat_id,
        "priority": priority,
        "asset": asset,
        "trust_boundary": boundary,
        "exploit": exploit,
        "result": result,
        "status": status,
        "blocks_physical_completion": status in BLOCKING_STATUSES,
        "kill_criterion": kill_criterion,
        "closure_evidence": closure_evidence,
        "executable_evidence": executable_evidence or [],
    }


def build() -> dict[str, Any]:
    gate = _read(DIRAC_GATE)
    band = _read(BAND_EDGE)
    campaign = _read(CAMPAIGN)
    if gate.get("schema") != "holo.dirac-critical-bath-gate.v1":
        raise RedTeamInputError("unexpected Dirac gate schema")
    if gate.get("checks", {}).get("all") is not True:
        raise RedTeamInputError("Dirac static checks are not certified")
    if gate.get("decision", {}).get("verdict") != (
        "SURVIVES_STATIC_SPECTRAL_GATE_BLOCKED_MICROSCOPIC_"
        "LOCAL_QFT_AND_HOLO"
    ):
        raise RedTeamInputError("unexpected Dirac gate verdict")
    if band.get("decision", {}).get("verdict") != (
        "KILL_C2_BAND_EDGE_WRONG_VARIATIONAL_SIGN"
    ):
        raise RedTeamInputError("band-edge negative control is not frozen")
    if band.get("checks", {}).get("all") is not True:
        raise RedTeamInputError("band-edge negative control is not certified")
    if band.get("sources", {}).get("inherited_exposed_target_origin") != (
        gate.get("sources", {}).get("inherited_exposed_target_origin")
    ):
        raise RedTeamInputError("band-edge and Dirac target genealogy diverged")
    if campaign.get("verdict", {}).get("status") != "blocked":
        raise RedTeamInputError("minimal mechanism campaign is not blocked")

    diagnostics = gate["diagnostics"]
    physical = gate["physical_gates"]

    trust_boundaries = [
        {
            "id": "TB1_spectrum_to_static_determinant",
            "status": "CLOSED_UNIFORM_STATIC",
            "meaning": "Hermitian Clifford spectrum to filled-sea sign and integral.",
        },
        {
            "id": "TB2_continuous_DOS_to_finite_local_QFT",
            "status": "OPEN",
            "meaning": "An onsite continuum is an infinite internal fiber, not a finite 3+1 QFT.",
        },
        {
            "id": "TB3_static_determinant_to_causal_dynamics",
            "status": "OPEN",
            "meaning": "The zero-gap fermion bubble has a nonanalytic temporal kernel.",
        },
        {
            "id": "TB4_gradient_proxy_to_gravitational_constraints",
            "status": "OPEN",
            "meaning": "Choosing scalar gradient, lapse acceleration or aether changes constraints and DOF.",
        },
        {
            "id": "TB5_new_spectral_sector_to_current_HOLO_5D",
            "status": "OPEN",
            "meaning": "The current compact one-coordinate bulk has a discrete gapped tower.",
        },
        {
            "id": "TB6_quasistatic_scalar_to_matter_and_lensing",
            "status": "OPEN",
            "meaning": "A spherical constitutive equation does not fix two metric potentials or universal matter coupling.",
        },
    ]

    threats = [
        _threat(
            "RT01_determinant_factor_and_sign",
            priority="P0",
            asset="uniform static exponent and attractive sign",
            boundary="TB1_spectrum_to_static_determinant",
            exploit="Recompute the spectrum, filled-sea integral, Legendre sign and degeneracy.",
            result="Factors, sign, K2 and a0=Lambda/y close in the declared per-negative-branch convention.",
            status="CLOSED",
            kill_criterion="Any sign flip, complex energy or factor mismatch.",
            closure_evidence="Independent symbolic derivation and executable Clifford/integral tests.",
            executable_evidence=[
                "checks.clifford_coupling_is_linear_and_isotropic",
                "checks.spectral_integral_matches_closed_form",
                "checks.a0_relation_closes",
            ],
        ),
        _threat(
            "RT02_static_energy_instability",
            priority="P0",
            asset="static stability",
            boundary="TB1_spectrum_to_static_determinant",
            exploit="Search for negative energy, negative slope or a negative Hessian eigenvalue.",
            result="Single matched bath and the 1F+8B witness are positive and convex for nonzero field; both degenerate at zero.",
            status="CLOSED",
            kill_criterion="Negative static energy or transverse/longitudinal curvature.",
            closure_evidence="Global analytic inequalities plus logarithmic executable scans.",
            executable_evidence=[
                "checks.nonzero_background_is_elliptic",
                "checks.mixed_statistics_static_energy_is_positive_and_convex",
            ],
        ),
        _threat(
            "RT03_finite_spectrum_order_of_limits",
            priority="P0",
            asset="exact three-halves infrared asymptote",
            boundary="TB2_continuous_DOS_to_finite_local_QFT",
            exploit="Replace the continuum by a finite regulated spectrum, with and without a zero mode.",
            result="A zero mode gives a linear onset; a positive finite tower gives a quartic critical remainder, never cubic at the origin.",
            status="CONFIRMED_BLOCKER",
            kill_criterion="No regulated window with a bounded cubic approximation at the claimed physical scale.",
            closure_evidence="A canonical regulator, order of limits and a uniform error bound over the physical window.",
            executable_evidence=[
                "diagnostics.finite_positive_tower_critical_power",
                "diagnostics.finite_tower_zero_mode_power",
            ],
        ),
        _threat(
            "RT04_gapless_temporal_kernel",
            priority="P0",
            asset="causal local dynamics",
            boundary="TB3_static_determinant_to_causal_dynamics",
            exploit="Compute the same fermion bubble at nonzero frequency after subtracting K(0).",
            result="The leading kernel is proportional to |omega|; bosonic a^2 seagulls do not cancel it.",
            status="CONFIRMED_BLOCKER",
            kill_criterion="No hyperbolic initial-value problem, unstable pole or negative spectral weight.",
            closure_evidence="Full retarded propagator, constraints, positive residues and strong-coupling cutoff.",
            executable_evidence=["diagnostics.gapless_temporal_kernel_power"],
        ),
        _threat(
            "RT05_unprotected_quadratic_matching",
            priority="P0",
            asset="deep branch with no residual a-squared term",
            boundary="TB3_static_determinant_to_causal_dynamics",
            exploit="Renormalize K2 and perturb the 1:8, y:y/2 mixed-field rule.",
            result="The operator a^2 is symmetry-allowed; neither cancellation is RG protected.",
            status="CONFIRMED_BLOCKER",
            kill_criterion="Radiative drift larger than the accuracy required for the deep branch.",
            closure_evidence="A Ward identity or exact anomaly-free symmetry preserving Str(Q^2)=0 but Str(|Q|^3) nonzero.",
        ),
        _threat(
            "RT06_current_5D_DOS_origin",
            priority="P0",
            asset="current-HOLO microscopic origin",
            boundary="TB5_new_spectral_sector_to_current_HOLO_5D",
            exploit="Apply one-dimensional Weyl/Sturm-Liouville counting to the compact current bulk.",
            result="The regular finite interval supplies a discrete gapped tower with asymptotically constant DOS, not rho(epsilon) proportional to epsilon.",
            status="CONFIRMED_BLOCKER",
            kill_criterion="The current 5D action cannot generate the required continuum and Clifford vertex.",
            closure_evidence="A covariant bulk/brane action, boundary conditions and reduction deriving DOS, sign and normalization.",
        ),
        _threat(
            "RT07_nonzero_physical_hopping",
            priority="P0",
            asset="spatial locality",
            boundary="TB2_continuous_DOS_to_finite_local_QFT",
            exploit="Give the internal fermions physical group velocity and evaluate the inhomogeneous determinant.",
            result="A nonlocal spatial polarization returns; LDA requires v/(y|a|L)<<1 and is not uniform as a tends to zero.",
            status="OPEN_BLOCKER",
            kill_criterion="Nonlocal kernel dominates the local cubic in the intended regime.",
            closure_evidence="A finite local regulator with a quantitative locality bound on two source geometries.",
        ),
        _threat(
            "RT08_gravity_constraint_and_DOF",
            priority="P1",
            asset="healthy gravitational embedding",
            boundary="TB4_gradient_proxy_to_gravitational_constraints",
            exploit="Choose a_i as scalar gradient, lapse acceleration or aether acceleration and run ADM/Dirac analysis.",
            result="No choice and complete constraint algebra have yet been derived; the principal spatial symbol degenerates at a=0.",
            status="OPEN_BLOCKER",
            kill_criterion="Ghost, lost constraint, ill-posed characteristic or unacceptable strong coupling.",
            closure_evidence="Canonical action, complete constraint rank and principal-symbol spectrum on vacuum and sourced backgrounds.",
        ),
        _threat(
            "RT09_matter_and_lensing",
            priority="P1",
            asset="physical force and lensing",
            boundary="TB6_quasistatic_scalar_to_matter_and_lensing",
            exploit="Derive both weak-field metric potentials and couple all conserved matter through one metric.",
            result="Only a spherical constitutive proxy exists; normalization, slip and lensing are open.",
            status="OPEN_BLOCKER",
            kill_criterion="Non-universal force, wrong slip or insufficient lensing.",
            closure_evidence="One matter action and two-source solutions for Phi, Psi, force and lensing without target fitting.",
        ),
        _threat(
            "RT10_anomaly_and_topological_terms",
            priority="P1",
            asset="real anomaly-free determinant",
            boundary="TB2_continuous_DOS_to_finite_local_QFT",
            exploit="Regulate the paired cones with all three mass matrices and inspect parity-odd terms.",
            result="The 4x4 spectrum pairs two cones, but the full regulator and texture-dependent determinant are unspecified.",
            status="OPEN_BLOCKER",
            kill_criterion="Gauge/gravitational anomaly or unwanted topological response.",
            closure_evidence="Explicit lattice or Pauli-Villars regulator and cancellation of the complete parity-odd functional.",
        ),
        _threat(
            "RT11_mixed_bath_high_field",
            priority="P1",
            asset="1F+8B protected-interpolation option",
            boundary="TB1_spectrum_to_static_determinant",
            exploit="Take m much larger than Lambda after the internal quadratic sum rule.",
            result="The mixed energy grows linearly, not quadratically; it is only a deep-static witness, not a complete interpolant.",
            status="CONFIRMED_LIMITATION",
            kill_criterion="Using the mixed sum rule alone as the full Newtonian interpolation.",
            closure_evidence="A protected high-field sector that restores a^2 without reintroducing it on the deep branch.",
        ),
        _threat(
            "RT12_IR_state_and_interactions",
            priority="P1",
            asset="robust spectral exponent",
            boundary="TB2_continuous_DOS_to_finite_local_QFT",
            exploit="Add temperature, chemical potential, a small gap or anomalous dimension.",
            result="A gap explicitly rounds cubic to quartic; the other deformations are unevaluated.",
            status="OPEN_BLOCKER",
            kill_criterion="No domain where y|a| dominates every IR scale and rho remains linear.",
            closure_evidence="RG and phase diagram with a quantified, regulator-independent physical window.",
            executable_evidence=[
                "diagnostics.gapped_critically_subtracted_deep_power"
            ],
        ),
        _threat(
            "RT13_degeneracy_contract",
            priority="P2",
            asset="absolute normalization",
            boundary="TB1_spectrum_to_static_determinant",
            exploit="Count the two negative branches of each 4x4 Clifford multiplet again inside g.",
            result="The code declares g per negative branch, but no real field inventory fixes it.",
            status="OPEN_BLOCKER",
            kill_criterion="Factor-two ambiguity survives the field-content definition.",
            closure_evidence="Canonical field inventory and rho1 normalized per 4x4 multiplet.",
        ),
        _threat(
            "RT14_UV_shape_dependence",
            priority="P2",
            asset="exact interpolation mu(x)",
            boundary="TB1_spectrum_to_static_determinant",
            exploit="Replace the hard linear DOS edge with a local lattice band.",
            result="The cubic coefficient is infrared-universal, but the complete mu curve is UV dependent.",
            status="OPEN_BLOCKER",
            kill_criterion="A reasonable regulator changes the claimed exact curve materially.",
            closure_evidence="Derive the complete band from the microscopic action or claim only universal asymptotics.",
        ),
        _threat(
            "RT15_species_and_backreaction",
            priority="P2",
            asset="controlled effective theory",
            boundary="TB5_new_spectral_sector_to_current_HOLO_5D",
            exploit="Count the onsite continuum's entropy and induced curvature operators.",
            result="The site density/fiber volume is new and its Planck/curvature backreaction is uncomputed.",
            status="OPEN_BLOCKER",
            kill_criterion="Species renormalization or stress invalidates the assumed background.",
            closure_evidence="Finite regulator, stress tensor and gravitational backreaction with bounded corrections.",
        ),
        _threat(
            "RT16_exact_exposed_target_mismatch",
            priority="P1",
            asset="relation to the exposed collector",
            boundary="TB6_quasistatic_scalar_to_matter_and_lensing",
            exploit="Compare mu=1+x-sqrt(1+x^2) with the train-derived parametric mu target.",
            result=(
                "The limits agree, but the maximum absolute mu difference on the "
                "declared theory grid is "
                f"{diagnostics['maximum_absolute_mu_difference_from_exposed_target']:.6g}."
            ),
            status="CONFIRMED_LIMITATION",
            kill_criterion="Claiming reproduction of the exact empirical interpolation.",
            closure_evidence="A blind physical derivation of the full curve followed by external validation.",
            executable_evidence=[
                "decision.exact_exposed_collector_interpolation_reproduced"
            ],
        ),
        _threat(
            "RT17_ordinary_chemical_bath_sign",
            priority="P1",
            asset="alternative material mechanisms",
            boundary="TB1_spectrum_to_static_determinant",
            exploit="Replace the filled sea by stable equilibrium occupation coupled as a chemical shift.",
            result="The susceptibility sign is opposite to the AQUAL energy; that alternative is killed.",
            status="CLOSED",
            kill_criterion="Reusing pressure with a flipped multiplicity or ghost measure.",
            closure_evidence="Frozen C2 band-edge sign certificate.",
            executable_evidence=["c2.decision.required_AQUAL_variational_sign_derived"],
        ),
    ]

    ids = [row["id"] for row in threats]
    p0 = [row for row in threats if row["priority"] == "P0"]
    confirmed_blockers = [
        row for row in threats if row["status"] == "CONFIRMED_BLOCKER"
    ]
    open_blockers = [row for row in threats if row["status"] == "OPEN_BLOCKER"]
    closed = [row for row in threats if row["status"] == "CLOSED"]

    acceptance_ladder = [
        {
            "level": "L0_algebra",
            "status": "PASS",
            "meaning": "Clifford spectrum, determinant, sign and coefficients close.",
        },
        {
            "level": "L1_uniform_static_spectral",
            "status": "PASS",
            "meaning": "Deep exponent, monotone mu and static convexity close.",
        },
        {
            "level": "L2_finite_local_QFT",
            "status": "BLOCKED",
            "meaning": "Finite regulator changes the origin asymptote and the onsite continuum is an infinite fiber.",
        },
        {
            "level": "L3_causal_covariant_dynamics",
            "status": "BLOCKED",
            "meaning": "Temporal nonanalyticity, zero-field degeneracy and constraints remain open.",
        },
        {
            "level": "L4_current_HOLO_origin",
            "status": "BLOCKED",
            "meaning": "The current compact 5D scalar tower does not supply the required DOS or vertex.",
        },
        {
            "level": "L5_physical_force_and_lensing",
            "status": "BLOCKED",
            "meaning": "Matter normalization, two metric potentials and external verification are absent.",
        },
    ]

    checks = {
        "source_static_gate_passes": gate["checks"]["all"],
        "source_has_no_physical_completion": not gate["decision"][
            "physical_completion"
        ],
        "threat_ids_unique": len(ids) == len(set(ids)),
        "all_priorities_present": set(PRIORITIES)
        == {row["priority"] for row in threats},
        "p0_has_confirmed_blockers": any(
            row["status"] == "CONFIRMED_BLOCKER" for row in p0
        ),
        "finite_tower_attack_is_executable": abs(
            diagnostics["finite_positive_tower_critical_power"] - 4.0
        )
        < 1.0e-7
        and abs(diagnostics["finite_tower_zero_mode_power"] - 1.0) < 1.0e-10,
        "temporal_attack_is_executable": abs(
            diagnostics["gapless_temporal_kernel_power"] - 1.0
        )
        < 1.0e-6,
        "finite_local_QFT_gate_is_false": not physical[
            "finite_local_3p1_qft_realization"
        ],
        "current_HOLO_gate_is_false": not physical[
            "current_HOLO_physical_completion"
        ],
        "exact_target_match_is_false": not gate["decision"][
            "exact_exposed_collector_interpolation_reproduced"
        ],
        "no_attack_promotes_publication": not gate["decision"][
            "publication_authorized"
        ],
    }
    checks["all"] = all(checks.values())

    return {
        "schema": SCHEMA,
        "title": "Adversarial attack map for the Dirac critical-bath route",
        "classification": (
            "static_spectral_gate_survives;finite_local_qft_causal_holo_"
            "and_physical_completion_blocked"
        ),
        "review_profile": {
            "style": "defensive scientific red team",
            "model_requested_by_user": "gpt-daybreak-blue-latest",
            "scores_are_priorities_not_probabilities": True,
        },
        "sources": {
            "dirac_gate": {
                "path": str(DIRAC_GATE.relative_to(REPO)),
                "sha256": _sha256(DIRAC_GATE),
            },
            "band_edge_negative_control": {
                "path": str(BAND_EDGE.relative_to(REPO)),
                "sha256": _sha256(BAND_EDGE),
            },
            "minimal_campaign": {
                "path": str(CAMPAIGN.relative_to(REPO)),
                "sha256": _sha256(CAMPAIGN),
            },
            "raw_observational_tables_read_directly": [],
            "inherited_target_origin": gate["sources"][
                "inherited_exposed_target_origin"
            ],
        },
        "assets": [
            "three-halves exponent and attractive static sign",
            "positive convex static energy",
            "constitutive interpolation and a0 relation",
            "finite local field content and regulator",
            "causal covariant dynamics and constraints",
            "current-HOLO origin",
            "universal matter force, slip and lensing",
        ],
        "trust_boundaries": trust_boundaries,
        "threats": threats,
        "summary": {
            "threat_count": len(threats),
            "closed_count": len(closed),
            "confirmed_blocker_count": len(confirmed_blockers),
            "open_blocker_count": len(open_blockers),
            "p0_count": len(p0),
            "highest_level_passed": "L1_uniform_static_spectral",
            "first_blocked_level": "L2_finite_local_QFT",
        },
        "acceptance_ladder": acceptance_ladder,
        "priority_actions": [
            {
                "priority": 1,
                "action": "Construct a finite canonical regulator and bound the cubic window before taking a->0.",
                "closes": ["RT03_finite_spectrum_order_of_limits"],
            },
            {
                "priority": 2,
                "action": "Derive the full retarded kernel and canonical constraint/principal-symbol spectrum.",
                "closes": [
                    "RT04_gapless_temporal_kernel",
                    "RT08_gravity_constraint_and_DOF",
                ],
            },
            {
                "priority": 3,
                "action": "Find an anomaly-free RG-invariant cancellation rule for the a-squared operator.",
                "closes": [
                    "RT05_unprotected_quadratic_matching",
                    "RT10_anomaly_and_topological_terms",
                ],
            },
            {
                "priority": 4,
                "action": "Derive the spectral fiber and Clifford vertex from a covariant extension of the current bulk.",
                "closes": [
                    "RT06_current_5D_DOS_origin",
                    "RT15_species_and_backreaction",
                ],
            },
            {
                "priority": 5,
                "action": "Freeze one matter metric and solve two conserved source geometries for force, slip and lensing.",
                "closes": ["RT09_matter_and_lensing"],
            },
        ],
        "checks": checks,
        "decision": {
            "verdict": (
                "SURVIVES_STATIC_SPECTRAL_RED_TEAM_BLOCKED_LOCAL_QFT_"
                "DYNAMICS_AND_HOLO"
            ),
            "static_spectral_construction_survives": True,
            "finite_local_qft_survives": False,
            "causal_covariant_completion_survives": False,
            "current_holo_mechanism": False,
            "physical_completion": False,
            "publication_authorized": False,
        },
        "evidence_boundary": (
            "The red-team map confirms the uniform-static algebra and records "
            "concrete counterexamples to finite-spectrum, causal and current-HOLO "
            "promotion. The comparison target inherits a SPARC training fit; no "
            "raw observation table is read here. Priorities are attack severity, "
            "not probabilities. No physical force, lensing, discovery or publication "
            "claim is authorized."
        ),
        "software": {"python": platform.python_version()},
    }


def main() -> int:
    result = build()
    if result["checks"]["all"] is not True:
        raise RuntimeError("Dirac bath red-team checks failed")
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(f"[verdict] {result['decision']['verdict']}")
    print(
        "[attack map] "
        f"P0={result['summary']['p0_count']} "
        f"confirmed_blockers={result['summary']['confirmed_blocker_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
