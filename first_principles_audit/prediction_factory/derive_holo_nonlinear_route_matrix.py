#!/usr/bin/env python3
"""Generate a theory-only route matrix for the missing nonlinear HOLO sector.

The matrix combines carriers, selectors, geometries, couplings and observables
that already have concrete representatives in the repository.  It does not
search SPARC or refit the exposed collector.  The collector action is read only
as an immutable target whose microscopic origin is being tested.

Scores are readiness diagnostics, not probabilities.  Each route also carries
a decisive falsifier so that adding possibilities cannot become an exercise in
unfalsifiable model proliferation.
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
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "holo_nonlinear_route_matrix.json"

INPUTS = {
    "effective_action": REPO
    / "first_principles_audit/artifacts/holo_effective_action.json",
    "interface_action": REPO
    / "first_principles_audit/artifacts/interface_action_derivation.json",
    "boundary_completion": ARTIFACTS
    / "superpotential_boundary_completion.json",
    "stiff_force": ARTIFACTS / "stiff_boundary_force.json",
    "breathing_response": ARTIFACTS / "breathing_response.json",
    "scale_consistency": ARTIFACTS / "scale_consistency.json",
    "collector_action_target": ARTIFACTS / "nonlinear_collector_action.json",
    "soft_mode_bridge": ARTIFACTS / "soft_mode_cubic_bridge.json",
    "phase_space_bridge": ARTIFACTS / "phase_space_collector_bridge.json",
    "shell_residual": ARTIFACTS / "collector_shell_residual.json",
    "soft_vertex_scaling": ARTIFACTS / "soft_mode_cubic_scaling.json",
    "jordan_selector": ARTIFACTS / "jordan_selector_embedding.json",
    "jordan_deep_gate": ARTIFACTS / "jordan_deep_limit_gate.json",
    "tricritical_bridge": ARTIFACTS
    / "tricritical_constitutive_bridge.json",
    "spectral_bridge": ARTIFACTS / "collective_spectral_bridge.json",
    "bulk_decision_gate": ARTIFACTS
    / "bulk_constitutive_decision_gate.json",
    "bulk_cubic_inventory": ARTIFACTS / "bulk_cubic_vertex_inventory.json",
}

SCORE_MAX = 4
SCORE_FIELDS = (
    "derivability",
    "stability",
    "sqrt_mass_scaling",
    "lensing",
    "falsifier_strength",
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


def _score(**values: int) -> dict[str, int]:
    if set(values) != set(SCORE_FIELDS):
        raise ValueError("every route must use the complete score rubric")
    if any(
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 <= value <= SCORE_MAX
        for value in values.values()
    ):
        raise ValueError(f"route scores must be integers in [0,{SCORE_MAX}]")
    return {**values, "total_unweighted": sum(values.values())}


def _route(
    route_id: str,
    *,
    carrier: str,
    selector: str,
    geometry: str,
    coupling: str,
    observable: str,
    status: str,
    origin: str,
    equations: list[str],
    new_physics: list[str],
    falsifier: str,
    scores: dict[str, int],
) -> dict[str, Any]:
    return {
        "id": route_id,
        "coordinates": {
            "carrier": carrier,
            "selector": selector,
            "geometry": geometry,
            "coupling": coupling,
            "observable": observable,
        },
        "status": status,
        "origin": origin,
        "minimal_equations": equations,
        "new_physics": new_physics,
        "falsifier": falsifier,
        "scores": scores,
    }


def build() -> dict[str, Any]:
    payloads = {name: _read(path) for name, path in INPUTS.items()}
    effective = payloads["effective_action"]
    interface = payloads["interface_action"]
    boundary = payloads["boundary_completion"]
    stiff = payloads["stiff_force"]
    breathing = payloads["breathing_response"]
    scales = payloads["scale_consistency"]
    target = payloads["collector_action_target"]
    soft_bridge = payloads["soft_mode_bridge"]
    phase_space = payloads["phase_space_bridge"]
    shell_residual = payloads["shell_residual"]
    soft_scaling = payloads["soft_vertex_scaling"]
    jordan = payloads["jordan_selector"]
    jordan_deep = payloads["jordan_deep_gate"]
    tricritical = payloads["tricritical_bridge"]
    spectral = payloads["spectral_bridge"]
    bulk_gate = payloads["bulk_decision_gate"]
    cubic = payloads["bulk_cubic_inventory"]

    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective action input is not certified")
    if interface.get("passes", {}).get("all") is not True:
        raise RuntimeError("interface action input is not certified")
    if boundary.get("passes", {}).get("all") is not True:
        raise RuntimeError("boundary completion input is not certified")
    if stiff.get("passes", {}).get("all") is not True:
        raise RuntimeError("stiff force input is not certified")
    if breathing.get("passes", {}).get("all") is not True:
        raise RuntimeError("breathing response input is not certified")
    if scales.get("passes", {}).get("all") is not True:
        raise RuntimeError("scale consistency input is not certified")
    if target.get("passes", {}).get("all") is not True:
        raise RuntimeError("collector action target is not certified")
    if soft_bridge.get("certificate_checks", {}).get("all") is not True:
        raise RuntimeError("soft-mode exponent bridge is not certified")
    if phase_space.get("algebra_checks", {}).get("all") is not True:
        raise RuntimeError("phase-space bridge algebra is not certified")
    if shell_residual.get("checks", {}).get("all") is not True:
        raise RuntimeError("collector shell residual is not certified")
    if soft_scaling.get("scaling_checks", {}).get("all") is not True:
        raise RuntimeError("soft higher-vertex scaling proxy is not certified")
    if jordan.get("checks", {}).get("all") is not True:
        raise RuntimeError("Jordan selector embedding is not certified")
    if jordan_deep.get("checks", {}).get("all") is not True:
        raise RuntimeError("Jordan deep-limit gate is not certified")
    if tricritical.get("checks", {}).get("all") is not True:
        raise RuntimeError("tricritical constitutive bridge is not certified")
    if spectral.get("checks", {}).get("all") is not True:
        raise RuntimeError("collective spectral bridge is not certified")
    if bulk_gate.get("algebra_checks", {}).get("all") is not True:
        raise RuntimeError("bulk constitutive decision gate is not certified")
    if cubic.get("checks", {}).get("all") is not True:
        raise RuntimeError("bulk cubic vertex inventory is not certified")

    gamma_rows = boundary["stabilized_family"]["equal_gamma_scan"]
    if len(gamma_rows) < 3:
        raise RuntimeError("boundary scan does not resolve the soft limit")
    soft_rows = gamma_rows[:3]
    gamma = np.asarray([row["gamma_minus"] for row in soft_rows], dtype=float)
    soft_mu = np.asarray([row["masses_mu"][0] for row in soft_rows], dtype=float)
    soft_coefficient_rows = np.square(soft_mu) / gamma
    soft_coefficient = float(np.mean(soft_coefficient_rows))
    soft_relative_spread = float(
        np.ptp(soft_coefficient_rows) / soft_coefficient
    )

    spectrum = stiff["spectrum_and_force"]
    masses = np.asarray(spectrum["masses_mu"], dtype=float)
    residues = np.asarray(spectrum["alpha_uv_2_beta_squared"], dtype=float)
    alpha_sum = float(np.sum(residues))
    clock_modes = breathing["correlated_mode_clock"]["modes"]
    clock_ratios = [
        float(row["threshold_frequency_over_f1"]) for row in clock_modes
    ]
    target_slope = float(
        target["action_reconstruction"]["diagnostics"][
            "deep_limit_dlog_F_dlog_X"
        ]
    )

    axes = {
        "carrier": {
            "finite_stiff_tower": "seven positive canonical scalar modes",
            "soft_boundary_mode": "lowest scalar mode as gamma tends to zero",
            "breathing_collective": "positive occupation of the correlated mode comb",
            "boundary_trace_value": "gauge-invariant scalar evaluated on a matter brane",
            "backreacted_metric_scalar": "full metric-dilaton configuration",
            "matter_frame_planck_coefficient": (
                "field-dependent coefficient s=A_m^-2 multiplying R_J"
            ),
            "derivative_constitutive_scalar": (
                "nonlinear scalar-gradient sector beside a nondegenerate tensor term"
            ),
            "tricritical_collective_amplitude": (
                "nonnegative squared amplitude s=q^2 at a sextic critical point"
            ),
            "gapless_spectral_continuum": (
                "continuous scalar measure extending to zero mass"
            ),
        },
        "selector": {
            "fixed_stiff_boundary": "gamma_minus,gamma_plus tend to infinity",
            "finite_mode_elimination": "stationary elimination of massive modes",
            "critical_gamma_limit": "positive gamma continued toward zero",
            "legendre_stationarity": "Q extremizes Q*X-U(Q)",
            "prescribed_boundary_functional": "explicit boundary B(X)",
            "nonlinear_bulk_boundary_value": "bulk equations select a Dirichlet-to-Neumann map",
            "conformal_matter_factor": "nonlinear matter metric selects s=A_m^-2",
            "tricritical_stationarity": "Y=m2+u4*s+s^2 with m2=u4=0",
            "constant_gapless_measure": "rho_m=4/(3*pi) from m=0 to infinity",
        },
        "geometry": {
            "finite_compact_interval": "current compact radial interval",
            "critical_ir_extension": "soft or continuous infrared limit",
            "physical_matter_brane": "localized four-dimensional interface",
            "spherical_quasistatic_bulk": "radial source plus holographic coordinate",
        },
        "coupling": {
            "fixed_linear_trace": "source-independent masses and trace residues",
            "bulk_mode_overlap": "cubic and quartic overlaps derived from S5",
            "collective_susceptibility": "positive response Q coupled to X",
            "boundary_gradient_px": "brane-localized derivative functional",
            "conserved_stress_backreaction": "explicit matter stress in all bulk constraints",
            "nonminimal_curvature": "matter-frame coupling M_Pl^2*s*R_J/2",
            "conformal_scalar_matter": (
                "nonlinear scalar couples through the existing metric A_m^2*g_E"
            ),
        },
        "observable": {
            "bounded_yukawa_multiplier": "g/gN for a fixed pole tower",
            "constitutive_flux": "D=mu(|g|/a0)g",
            "breathing_comb": "correlated thresholds and occupations",
            "metric_force_and_slip": "dynamical potential and lensing combination",
        },
    }

    routes = [
        _route(
            "finite_stiff_yukawa",
            carrier="finite_stiff_tower",
            selector="fixed_stiff_boundary",
            geometry="finite_compact_interval",
            coupling="fixed_linear_trace",
            observable="bounded_yukawa_multiplier",
            status="derived_rejected_as_nonlinear_origin",
            origin="Current stiff P7 static slice; retained as a negative control.",
            equations=[
                "g/gN=1+sum_n alpha_n*(1+mu_n*r/ell)*exp(-mu_n*r/ell)",
                "dlog(g)/dlog(M)=1 at fixed r and ell",
            ],
            new_physics=[],
            falsifier=(
                "Already decisive: a source-independent finite Yukawa tower is "
                "linear in M and bounded by 1+sum(alpha_n)."
            ),
            scores=_score(
                derivability=4,
                stability=4,
                sqrt_mass_scaling=0,
                lensing=1,
                falsifier_strength=4,
            ),
        ),
        _route(
            "finite_mode_tree_elimination",
            carrier="finite_stiff_tower",
            selector="finite_mode_elimination",
            geometry="finite_compact_interval",
            coupling="bulk_mode_overlap",
            observable="constitutive_flux",
            status="analytic_control_rejected_if_spectrum_remains_gapped",
            origin=(
                "Expand the existing Einstein-dilaton action beyond quadratic "
                "order and eliminate the six heavier modes. The universal raw "
                "metric-scalar kinetic vertex is now explicit, but its constrained "
                "gauge-invariant projection is not."
            ),
            equations=[
                "Delta L=(1/2)*sum_n c_n^2*X*(-Box+m_n^2)^(-1)*X",
                "p<<m_n implies Delta L=sum_n c_n^2*X^2/(2*m_n^2)+...",
            ],
            new_physics=["cubic and quartic mode overlaps not yet derived"],
            falsifier=(
                "If all eliminated masses stay positive and finite, the local "
                "series begins with X^2 and cannot have leading X^(3/2)."
            ),
            scores=_score(
                derivability=3,
                stability=3,
                sqrt_mass_scaling=0,
                lensing=2,
                falsifier_strength=4,
            ),
        ),
        _route(
            "critical_ir_soft_mode",
            carrier="soft_boundary_mode",
            selector="critical_gamma_limit",
            geometry="critical_ir_extension",
            coupling="bulk_mode_overlap",
            observable="constitutive_flux",
            status="derived_exponent_precursor_with_failed_current_sign_gate",
            origin=(
                "Use the derived softening mu0^2 proportional to gamma as a "
                "precursor of an IR-critical or continuous scalar sector."
            ),
            equations=[
                f"mu0^2={soft_coefficient:.12g}*gamma+o(gamma)",
                "m_eff^2=m0^2+lambda*a0^2*X",
                "Delta Gamma_static=(1/2) Tr_3 log(-nabla^2+m_eff^2)",
                "Delta Gamma_nonanalytic=-m_eff^3/(12*pi)",
                "m0->0 gives the X^(3/2) power but the current sign is wrong",
            ],
            new_physics=[
                "a microscopic selection rule for the critical endpoint",
                "the nonlinear mass shift lambda",
                "a critical mechanism that removes the analytic Z*X term",
                "an interacting sector that reverses or dominates the determinant sign",
                "a finite physical matter residue as gamma tends to zero",
                "an IR state or extension that justifies the static critical sector",
            ],
            falsifier=(
                "Reject if the renormalized small-X slope is not 3/2, its "
                "coefficient has the wrong sign, the Hessian becomes negative, "
                "the analytic Z*X coefficient remains nonzero, or gamma is "
                "selected using the target."
            ),
            scores=_score(
                derivability=2,
                stability=2,
                sqrt_mass_scaling=2,
                lensing=2,
                falsifier_strength=4,
            ),
        ),
        _route(
            "breathing_legendre_condensate",
            carrier="breathing_collective",
            selector="legendre_stationarity",
            geometry="finite_compact_interval",
            coupling="collective_susceptibility",
            observable="breathing_comb",
            status="generated_gapped_occupation_hypothesis_with_open_ensemble",
            origin=(
                "Fill low-momentum states of a gapped breathing mode and use "
                "its positive rest-energy contribution as a candidate dual."
            ),
            equations=[
                "W(s)=integral_0^s u^2*sqrt(1+u^2)du",
                "s<<1: W=s^3/3+O(s^5)",
                "postulated Legendre pair: F=s*X-W, X=W'(s)",
                "deep: F=2*X^(3/2)/3+O(X^(5/2))",
                "target saturation map: ds/dt=1-s, t=sqrt(g_N/a0)",
                "a0=xi*c*omega0=xi*mu0*c^2/ell",
            ],
            new_physics=[
                "a stationary pumped or interacting bosonic occupation",
                "a derivation that X is conjugate to s rather than particle number",
                "an independently normalized selector and susceptibility coupling",
                "a nonperturbative saturation law yielding ds/dt=1-s",
                "positive damping and a scale-setting rule for xi and ell",
            ],
            falsifier=(
                "Reject if kinetic theory gives zero equilibrium occupation, "
                "s^4/s^5 instead of the gapped rest-energy cubic, couples X to "
                "number rather than s, lacks saturation, or fits a0 to the target."
            ),
            scores=_score(
                derivability=1,
                stability=2,
                sqrt_mass_scaling=3,
                lensing=2,
                falsifier_strength=4,
            ),
        ),
        _route(
            "brane_px_exact_control",
            carrier="boundary_trace_value",
            selector="prescribed_boundary_functional",
            geometry="physical_matter_brane",
            coupling="boundary_gradient_px",
            observable="constitutive_flux",
            status="exact_engineering_control_not_microscopic_derivation",
            origin=(
                "Add a derivative boundary functional to the existing brane "
                "interface and use the exposed collector action as a solver target."
            ),
            equations=[
                "S_B=-a0^2/(8*pi*G4)*integral_B sqrt(-gamma)*B(Y)",
                "Y=h^ab*D_a(Phi)*D_b(Phi)/a0^2",
                "F_eff(X)=Z_bulk*X+C_B*B(s_B*X)",
                "B must cancel Z_bulk*X before reproducing F_target(X)",
            ],
            new_physics=[
                "a brane-localized derivative operator",
                "a microscopic derivation of B, a0 and the matter metric",
            ],
            falsifier=(
                "It fails as a prediction whenever B or a0 is copied from the "
                "target; it fails as a healthy control if the full generalized "
                "mode norm acquires a negative direction."
            ),
            scores=_score(
                derivability=0,
                stability=2,
                sqrt_mass_scaling=4,
                lensing=1,
                falsifier_strength=4,
            ),
        ),
        _route(
            "jordan_frame_gravitational_selector",
            carrier="matter_frame_planck_coefficient",
            selector="conformal_matter_factor",
            geometry="physical_matter_brane",
            coupling="nonminimal_curvature",
            observable="metric_force_and_slip",
            status="exact_frame_identity_rejected_as_direct_full_planck_selector",
            origin=(
                "Transform the existing certified scalar--matter interface "
                "exactly to the metric followed by matter before linearizing."
            ),
            equations=[
                "g_J=A_m(phi)^2*g_E; s=A_m(phi)^(-2)",
                "S_J contains M_Pl^2*s*R_J/2+S_m[g_J,Psi]",
                "U_J(s)=s^2*U_E(phi(s))",
                "desired but unproved: L_static=-M_Pl^2*[s*|grad(Phi)|^2-a0^2*W_J(s)]",
                "only after the full constraints: W_J'(s)=|grad(Phi)|^2/a0^2",
            ],
            new_physics=[
                "the full nonlinear function A_m(phi) from the five-dimensional interface",
                "a healthy branch spanning the required selector range",
                "the lapse, shift, scalar and second-potential constraint reduction",
                "a microscopic W_J(s) with the required convex dual and normalization a0",
            ],
            falsifier=(
                "The direct identification is already blocked in the isolated deep "
                "limit: s tends to zero, so the full Jordan tensor coefficient "
                "vanishes, A_m diverges and the frame map is singular."
            ),
            scores=_score(
                derivability=3,
                stability=1,
                sqrt_mass_scaling=0,
                lensing=2,
                falsifier_strength=4,
            ),
        ),
        _route(
            "derivative_constitutive_scalar",
            carrier="derivative_constitutive_scalar",
            selector="legendre_stationarity",
            geometry="physical_matter_brane",
            coupling="conformal_scalar_matter",
            observable="metric_force_and_slip",
            status="surviving_architecture_operator_not_microscopically_derived",
            origin=(
                "Keep the tensor Einstein-Hilbert term nondegenerate and place "
                "the Legendre selector in a separate collective scalar-gradient "
                "sector coupled through the existing matter metric."
            ),
            equations=[
                "S_E contains M_Pl^2*R_E/2-M_Pl^2*a0^2*F(Y)+S_m[A_m(phi)^2*g_E,Psi]",
                "F(Y)=sup_s[s*Y-W(s)]",
                "selector equation: Y=W'(s)",
                "deep F~2*Y^(3/2)/3 gives a scalar gradient proportional to sqrt(M)",
                "the tensor metric, scalar force, slip and lensing must be combined before comparison",
            ],
            new_physics=[
                "a derivation of the noncanonical derivative operator from the bulk modes",
                "the absolute normalization a0 and the scalar matter coefficient",
                "a healthy causal covariant completion of the quasistatic invariant Y",
                "the two-potential and lensing response including any additional field",
            ],
            falsifier=(
                "Reject if the reduced bulk action retains a nonzero canonical Y "
                "term in the deep branch, has a ghost or ill-posed characteristic, "
                "cannot derive a0 without galaxy data, or fails the independent "
                "lensing and Solar-System limits."
            ),
            scores=_score(
                derivability=2,
                stability=2,
                sqrt_mass_scaling=3,
                lensing=2,
                falsifier_strength=4,
            ),
        ),
        _route(
            "tricritical_collective_amplitude",
            carrier="tricritical_collective_amplitude",
            selector="tricritical_stationarity",
            geometry="critical_ir_extension",
            coupling="collective_susceptibility",
            observable="constitutive_flux",
            status="exact_exponent_mechanism_bulk_realization_not_derived",
            origin=(
                "Represent the constitutive selector by a nonnegative collective "
                "amplitude and ask whether the reduced bulk action selects its "
                "tricritical point prospectively."
            ),
            equations=[
                "s=q^2; L_aux=-s*Y+m2*s+u4*s^2/2+s^3/3",
                "stationarity: Y=m2+u4*s+s^2",
                "m2=u4=0 gives s=sqrt(Y) and P(Y)=2*Y^(3/2)/3",
                "d2L_aux/dq2=8*Y tends to zero in the deep limit",
            ],
            new_physics=[
                "a gauge-invariant q^2*Y vertex from the nonlinear constraints",
                "a symmetry or critical mechanism setting m2=u4=0",
                "positive sextic normalization and controlled q gradients",
                "an independent a0, matter coefficient and lensing response",
            ],
            falsifier=(
                "Reject if the frozen cubic-through-sextic reduction has no q^2*Y "
                "vertex, leaves m2 or u4 nonzero, has an unstable sextic sign, or "
                "requires the exposed target to choose the critical point."
            ),
            scores=_score(
                derivability=1,
                stability=1,
                sqrt_mass_scaling=4,
                lensing=0,
                falsifier_strength=4,
            ),
        ),
        _route(
            "gapless_spectral_continuum",
            carrier="gapless_spectral_continuum",
            selector="constant_gapless_measure",
            geometry="critical_ir_extension",
            coupling="bulk_mode_overlap",
            observable="constitutive_flux",
            status="exact_integral_identity_not_healthy_local_generation",
            origin=(
                "Take the critical or decompactified limit before truncating the "
                "mode tower and test its signed spectral measure."
            ),
            equations=[
                "P(Y)=4/(3*pi)*integral_0^infinity dm*Y^2/(Y+m^2)",
                "constant rho_m gives P(Y)=2*Y^(3/2)/3",
                "finite cutoffs give the power only for eps^2<<Y<<Lambda^2",
                "seven current poles match slope 3/2 for only 0.210 dex",
            ],
            new_physics=[
                "a derived gapless constant positive density per mass",
                "a healthy sign rather than ordinary Gaussian exchange",
                "a reduction from a momentum continuum to a local amplitude operator",
                "independently fixed IR and UV cutoffs",
            ],
            falsifier=(
                "Reject if the spectrum remains gapped, its density is not constant, "
                "the sign follows ordinary stable Gaussian elimination, or the "
                "result is a nonlocal momentum kernel rather than local P(Y)."
            ),
            scores=_score(
                derivability=1,
                stability=1,
                sqrt_mass_scaling=4,
                lensing=0,
                falsifier_strength=4,
            ),
        ),
        _route(
            "collective_bulk_backreaction",
            carrier="backreacted_metric_scalar",
            selector="nonlinear_bulk_boundary_value",
            geometry="spherical_quasistatic_bulk",
            coupling="conserved_stress_backreaction",
            observable="metric_force_and_slip",
            status="secondary_microscopic_route_after_interface_closure",
            origin=(
                "Solve the existing metric and dilaton nonlinearly with an "
                "explicit conserved matter brane instead of summing fixed poles."
            ),
            equations=[
                "Pi_i(g)=delta(S5_on_shell)/delta(D_i(Phi))",
                "D_i Pi_i=4*pi*G4*rho",
                "required deep limit: Pi_i=|g|*g_i/a0",
                "required high limit: Pi_i=g_i",
            ],
            new_physics=[
                "a complete conserved matter/interface action",
                "a nonlinear branch-selection rule",
                "a derived relation between the two metric potentials",
            ],
            falsifier=(
                "Reject the regular branch if its Dirichlet-to-Neumann map keeps "
                "a nonzero linear coefficient as g tends to zero; reject any "
                "critical branch with a negative fluctuation eigenvalue."
            ),
            scores=_score(
                derivability=2,
                stability=2,
                sqrt_mass_scaling=2,
                lensing=3,
                falsifier_strength=3,
            ),
        ),
    ]

    route_ids = [route["id"] for route in routes]
    axis_names = set(axes)
    coordinates_valid = all(
        set(route["coordinates"]) == axis_names
        and all(
            route["coordinates"][axis] in axes[axis]
            for axis in axes
        )
        for route in routes
    )
    scores_valid = all(
        all(
            isinstance(route["scores"][field], int)
            and 0 <= route["scores"][field] <= SCORE_MAX
            for field in SCORE_FIELDS
        )
        and route["scores"]["total_unweighted"]
        == sum(route["scores"][field] for field in SCORE_FIELDS)
        for route in routes
    )

    derived_constraints = {
        "positive_bulk_carrier": {
            "epsilon_min": interface["carrier_metrics"]["epsilon_min"],
            "p_min": interface["carrier_metrics"]["p_min"],
            "w_min": interface["carrier_metrics"]["w_min"],
            "w_integral": interface["carrier_metrics"]["w_integral"],
        },
        "finite_stiff_tower": {
            "masses_mu": masses.tolist(),
            "residues_alpha": residues.tolist(),
            "alpha_sum": alpha_sum,
            "maximum_linear_multiplier": 1.0 + alpha_sum,
            "source_mass_exponent": 1.0,
        },
        "soft_boundary_precursor": {
            "fit_form": "mu0^2=C_gamma*gamma over the first three frozen scan points",
            "C_gamma": soft_coefficient,
            "relative_spread": soft_relative_spread,
            "gamma_values": gamma.tolist(),
            "mu0_values": soft_mu.tolist(),
            "current_nonanalytic_coefficient": soft_bridge[
                "three_dimensional_determinant"
            ]["numerical_coefficient_of_m_cubed"],
            "current_positive_W_sign_gate": soft_bridge["physical_gates"][
                "required_positive_W_sign_generated_by_bosonic_determinant"
            ],
            "analytic_linear_X_term_gate": soft_bridge["physical_gates"][
                "analytic_linear_X_term_absent_or_cancelled"
            ],
            "nonvanishing_matter_residue_gate": soft_bridge["physical_gates"][
                "nonvanishing_physical_matter_residue_derived"
            ],
            "minimal_brane_proxy_power_in_mu0": soft_scaling["scaling_law"][
                "brane_proxy_power_in_mu0"
            ],
            "minimal_brane_quartic_proxy_power_in_mu0": soft_scaling[
                "scaling_law"
            ]["brane_quartic_proxy_power_in_mu0"],
            "higher_brane_jets_microscopically_selected": soft_scaling[
                "physical_gates"
            ]["higher_brane_jets_selected_by_microscopic_boundary_theory"],
        },
        "gapped_occupation_inverse_design": {
            "deep_W_power": phase_space["gapped_dispersion_check"][
                "deep_W_log_slope_vs_s"
            ],
            "deep_F_power": phase_space["gapped_dispersion_check"][
                "deep_F_log_slope_vs_X"
            ],
            "unsaturated_high_X_F_power": phase_space[
                "gapped_dispersion_check"
            ]["high_X_F_log_slope"],
            "stationary_occupation_derived": phase_space["physical_gates"][
                "positive_local_occupation_derived"
            ],
            "normalized_missing_quartic_coefficient": shell_residual[
                "asymptotics"
            ]["measured_deep_Wint_quartic_coefficient"],
            "normalization_warning": shell_residual["asymptotics"][
                "normalization_dependency"
            ],
            "saturation_transport_equation": shell_residual[
                "transport_equivalence"
            ]["equation"],
            "transport_is_holo_derived": shell_residual["physical_gates"][
                "holo_transport_equation_ds_dt_equals_one_minus_s_derived"
            ],
        },
        "breathing_comb": {
            "threshold_frequency_ratios": clock_ratios,
            "absolute_force_residues_available": breathing[
                "microscopic_boundary_update"
            ]["stiff_stabilized_candidate"]["absolute_force_residues_available"],
        },
        "nonlinear_target_for_comparison_only": {
            "deep_dlog_F_dlog_X": target_slope,
            "deep_limit": target["action"]["deep_limit"],
            "newtonian_limit": target["action"]["newtonian_limit"],
        },
        "jordan_selector_embedding": {
            "selector_definition": jordan["frame_derivation"][
                "selector_definition"
            ],
            "curvature_term": jordan["frame_derivation"]["curvature_term"],
            "matter_action": jordan["frame_derivation"]["matter_action"],
            "constraint_reduction_gate": jordan["physical_gates"][
                "weak_field_constraint_reduction_equals_local_s_times_X"
            ],
            "target_potential_gate": jordan["physical_gates"][
                "jordan_potential_equals_required_W_of_s"
            ],
            "physical_completion": jordan["physical_gates"][
                "physical_completion"
            ],
        },
        "jordan_deep_limit_gate": {
            "selector_power_in_t": jordan_deep["diagnostics"][
                "selector_power_in_t"
            ],
            "conformal_power_in_t": jordan_deep["diagnostics"][
                "conformal_power_in_t"
            ],
            "direct_full_planck_selector_gate": jordan_deep["physical_gates"][
                "direct_s_as_full_planck_coefficient_completion"
            ],
            "surviving_architecture": jordan_deep["architecture_implication"][
                "surviving_route"
            ],
        },
        "tricritical_constitutive_bridge": {
            "exact_selector": tricritical["exact_mechanism"][
                "tricritical_solution"
            ],
            "exact_operator": tricritical["exact_mechanism"]["deep_operator"],
            "quartic_contaminated_deep_power": tricritical[
                "relevant_deformation_tests"
            ]["quartic_contaminated_deep_P_power"],
            "correlation_length_power_in_Y": tricritical[
                "locality_obstruction"
            ]["measured_power_in_Y"],
            "bulk_realization_complete": tricritical["physical_gates"][
                "physical_completion"
            ],
        },
        "gapless_spectral_bridge": {
            "required_density_per_mass": spectral["exact_representation"][
                "required_density_per_mass"
            ],
            "current_seven_mode_crossover_width_dex": spectral[
                "current_seven_mode_test"
            ]["within_0p05_log10_width_dex"],
            "current_density_coefficient_of_variation": spectral[
                "current_seven_mode_test"
            ]["coefficient_of_variation_vs_constant_density"],
            "healthy_local_generation_complete": spectral["physical_gates"][
                "physical_completion"
            ],
        },
        "bulk_decision_gate": {
            "old_source_mass_exponent": bulk_gate["old_vs_this"][
                "old_fixed_poles"
            ]["source_mass_exponent"],
            "new_source_mass_exponent": bulk_gate["old_vs_this"][
                "this_critical_constitutive_response"
            ]["source_mass_exponent"],
            "minimal_radial_characteristic_ratio": bulk_gate[
                "principal_symbol_audit"
            ]["radial_over_transverse_characteristic_ratio"],
            "prospective_test_can_run": bulk_gate["prospective_bulk_test"][
                "can_run_with_current_frozen_inputs"
            ],
            "physical_completion": bulk_gate["physical_gates"][
                "physical_completion"
            ],
        },
        "bulk_cubic_vertex_inventory": {
            "raw_derivative_vertex": cubic["exact_first_variation"][
                "raw_derivative_cubic"
            ],
            "fixed_metric_derivative_cubic_zero": cubic["checks"][
                "fixed_metric_scalar_derivative_cubic_is_zero"
            ],
            "unit_overlap_heavy_inverse_mass_squared_moment": cubic[
                "modal_reduction"
            ]["unit_overlap_spectral_moment_sum_mu_inverse_squared"],
            "physical_overlap_coefficients_computed": cubic["physical_gates"][
                "physical_overlap_coefficients_c_a_computed"
            ],
            "direct_quartic_contact_computed": cubic["physical_gates"][
                "direct_quartic_contact_operator_computed"
            ],
            "gapped_exchange_contribution_to_P": cubic["modal_reduction"][
                "low_energy_result_if_c_a_were_known"
            ],
            "total_Y2_coefficient": cubic["modal_reduction"][
                "total_quartic_coefficient"
            ],
            "physical_cubic_vertex_complete": cubic["physical_gates"][
                "physical_cubic_vertex_complete"
            ],
        },
        "scale_boundary": {
            "single_ell_viable_for_qcd_and_galaxy_readings": scales[
                "comparison"
            ]["single_ell_can_realize_both_identifications"],
            "orders_of_magnitude_in_ell": scales["comparison"][
                "orders_of_magnitude_in_ell"
            ],
            "allowed_acceleration_rule": "a0=xi*c^2/ell=xi*c*omega0/mu0",
            "rule": (
                "xi and ell must be predicted independently; neither the "
                "collector a0 nor the saturated galaxy scan may select them"
            ),
        },
    }

    passes = {
        "certified_inputs": True,
        "no_observational_tables_read": True,
        "collector_used_only_as_exposed_target": True,
        "all_five_axes_crossed": coordinates_valid,
        "route_ids_unique": len(route_ids) == len(set(route_ids)),
        "score_rubric_complete": scores_valid,
        "finite_yukawa_rejected_for_sqrt_mass": next(
            route for route in routes if route["id"] == "finite_stiff_yukawa"
        )["scores"]["sqrt_mass_scaling"]
        == 0,
        "critical_softening_resolved": bool(
            soft_coefficient > 0.0 and soft_relative_spread < 0.01
        ),
        "failed_soft_mode_physical_gates_propagated": bool(
            soft_bridge["physical_gates"]["physical_completion"] is False
            and soft_bridge["physical_gates"][
                "required_positive_W_sign_generated_by_bosonic_determinant"
            ]
            is False
            and soft_bridge["physical_gates"][
                "analytic_linear_X_term_absent_or_cancelled"
            ]
            is False
        ),
        "gapped_occupation_hypotheses_propagated": bool(
            phase_space["physical_gates"]["physical_completion"] is False
            and shell_residual["physical_gates"]["physical_completion"] is False
            and soft_scaling["physical_gates"]["physical_completion"] is False
        ),
        "jordan_embedding_gates_propagated": bool(
            jordan["checks"]["all"] is True
            and jordan["physical_gates"]["physical_completion"] is False
            and jordan["physical_gates"][
                "weak_field_constraint_reduction_equals_local_s_times_X"
            ]
            is False
        ),
        "jordan_deep_obstruction_propagated": bool(
            jordan_deep["checks"]["all"] is True
            and jordan_deep["physical_gates"][
                "direct_s_as_full_planck_coefficient_completion"
            ]
            is False
        ),
        "tricritical_exact_algebra_and_open_bulk_gates_propagated": bool(
            tricritical["checks"]["all"] is True
            and tricritical["physical_gates"]["physical_completion"] is False
            and tricritical["physical_gates"][
                "q_squared_times_Y_vertex_derived_from_constraint_action"
            ]
            is False
        ),
        "spectral_identity_and_generation_warning_propagated": bool(
            spectral["checks"]["all"] is True
            and spectral["physical_gates"]["physical_completion"] is False
            and spectral["current_seven_mode_test"][
                "within_0p05_log10_width_dex"
            ]
            < 0.25
        ),
        "bulk_decision_gate_remains_fail_closed": bool(
            bulk_gate["algebra_checks"]["all"] is True
            and bulk_gate["physical_gates"]["physical_completion"] is False
            and bulk_gate["prospective_bulk_test"][
                "can_run_with_current_frozen_inputs"
            ]
            is False
        ),
        "raw_cubic_vertex_and_projection_boundary_propagated": bool(
            cubic["checks"]["all"] is True
            and cubic["checks"][
                "fixed_metric_scalar_derivative_cubic_is_zero"
            ]
            is True
            and cubic["physical_gates"][
                "physical_overlap_coefficients_c_a_computed"
            ]
            is False
            and cubic["physical_gates"][
                "direct_quartic_contact_operator_computed"
            ]
            is False
        ),
        "target_has_three_halves_deep_slope": math.isclose(
            target_slope, 1.5, rel_tol=0.0, abs_tol=2.0e-3
        ),
        "discovery_and_control_routes_separated": bool(
            next(
                route
                for route in routes
                if route["id"] == "brane_px_exact_control"
            )["status"]
            == "exact_engineering_control_not_microscopic_derivation"
        ),
        "single_scale_no_go_preserved": scales["comparison"][
            "single_ell_can_realize_both_identifications"
        ]
        is False,
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.nonlinear-route-matrix.v1",
        "title": "Generative matrix for a microscopic nonlinear HOLO response",
        "classification": (
            "theory_only_route_generation_with_falsifiers_not_a_new_force_claim"
        ),
        "evidence_boundary": (
            "The matrix derives constraints and one soft-mode precursor from "
            "certified HOLO artefacts. The critical, condensate, boundary-P(X) "
            "and collective-backreaction mechanisms are explicit new hypotheses. "
            "The tricritical and spectral bridges prove exact mathematical "
            "routes to the exponent but not their microscopic generation. "
            "No route becomes a prediction until its operator, a0, matter "
            "coupling and lensing response follow from frozen microscopic inputs."
        ),
        "input_contract": {
            "observational_tables_read": [],
            "exposed_empirical_target_for_comparison_only": str(
                INPUTS["collector_action_target"].relative_to(REPO)
            ),
            "inputs": {
                name: {
                    "path": str(path.relative_to(REPO)),
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
        },
        "score_rubric": {
            "range": [0, SCORE_MAX],
            "meaning": {
                "derivability": "0 inserted target; 4 already action-derived",
                "stability": "0 inconsistent; 4 certified positive sector",
                "sqrt_mass_scaling": "0 impossible; 4 exact algebraic mechanism",
                "lensing": "0 absent; 4 derived two-potential prediction",
                "falsifier_strength": "0 vague; 4 immediate decisive test",
            },
            "warning": "totals are readiness summaries, not probabilities or evidence weights",
        },
        "design_axes": axes,
        "routes": routes,
        "derived_constraints": derived_constraints,
        "prototype_selection": {
            "leading_research_hypotheses": [
                "derivative_constitutive_scalar",
                "tricritical_collective_amplitude",
                "gapless_spectral_continuum",
                "critical_ir_soft_mode",
                "breathing_legendre_condensate",
            ],
            "current_failed_realization": (
                "the isolated conventional bosonic soft-mode determinant has "
                "the wrong sign, retains an unremoved analytic X term and has "
                "no derived finite matter residue; the gapped-occupation route "
                "has the desired deep algebra but no derived ensemble, conjugate "
                "coupling, normalization or saturation transport; identifying "
                "the same selector with the full Jordan Planck coefficient makes "
                "that tensor coefficient vanish in the deep limit; the exact "
                "tricritical route still lacks a derived q^2*Y vertex and critical "
                "selection, while the exact spectral identity lacks healthy local "
                "generation"
            ),
            "exact_solver_control": "brane_px_exact_control",
            "negative_controls": [
                "finite_stiff_yukawa",
                "finite_mode_tree_elimination",
                "jordan_frame_gravitational_selector",
            ],
            "deferred_full_geometry_route": "collective_bulk_backreaction",
            "first_low_memory_prototype": (
                "freeze the five-dimensional and boundary inputs; derive the "
                "gauge-invariant cubic-through-sextic collective action and its "
                "Dirichlet-to-Neumann map without the galaxy target; then apply "
                "the pre-registered amplitude, stability, causal and lensing gates"
            ),
        },
        "passes": passes,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    soft = result["derived_constraints"]["soft_boundary_precursor"]
    print(
        "[soft mode] mu0^2/gamma={:.12g}, relative spread={:.3g}".format(
            soft["C_gamma"], soft["relative_spread"]
        )
    )
    print(
        "[research hypotheses] "
        + ", ".join(
            result["prototype_selection"]["leading_research_hypotheses"]
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
