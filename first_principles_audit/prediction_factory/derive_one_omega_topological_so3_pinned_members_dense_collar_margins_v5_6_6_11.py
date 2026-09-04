#!/usr/bin/env python3
"""Pinned members as class points: dense-collar margins and the same-objects theorem (v5.6.6.11).

Advances two of the five genuine gaps listed by v5.6.6.10 without claiming
their unsampled or continuum parts are closed:

(gap 3) MARGINS ON A DENSE COLLAR GRID.  v5.6.4 checked the class margins (Lorentzian
    signature with eigenvalue margin, Omega >= Omega_min, timelike khronon margin,
    SO(3) cut-locus margin) only at the N Kronecker nodes times 7 radial samples.
    This gate decodes the three byte-pinned members with the byte-pinned v5.6.4.2
    common-first pointwise decoder on a DENSE grid of the collar (256 tangential
    points along the single direction theta = x0 + x1 that carries all modes,
    129 radial points including both endpoints), composes the bulk fields with the
    v5.6.4.4 C2 radial profiles, and measures every margin everywhere.  The pinned
    members' membership in the margin set is thereby established on that finite
    grid.  Membership on the whole collar does not follow from continuity alone:
    it still needs a quantitative derivative/interval bound between grid points.

(gap 1) SAME OBJECTS.  With (a) free data that are degree-<=1 trigonometric
    polynomials in theta and polynomial radial profiles (byte-pinned bundle),
    (b) pointwise gluing to <= 4.4e-16 (v5.6.6.8), and (c) the margins on the
    dense collar (this gate), each pinned member X_N is a point of the restricted
    class of the v5.6.6.8 theorem, hence the exact identity (i) applies to it
    verbatim only after the unsampled collar margins and the common-functional
    identification are certified.  The Route C direct first variation at
    quadrature (Qtheta, Qrho)
    is a trapezoidal x Gauss--Legendre sum of a NODAL integrand that is itself a
    finite-difference approximation (FD5 in the free parameter, 7-point
    coordinate stencils) of the continuum first-variation density; so
    lim_{Q -> inf} Route C(Q) = DS_rel[X_N].dX_N + B_FD, where B_FD is the
    Q-independent stencil bias, and the limit exists for continuous integrands
    with no analyticity hypothesis (analyticity only sets the rate measured in
    v5.6.6.10).  Components (i)-(iii) and (iv) of the ledger therefore refer to
    the same objects up to B_FD, which no ladder can see and which is left as an
    explicit open item.  The theorem is recorded with its hypotheses; the
    quadrature convergence statement is classical and not machine-checked here.

Independence: this gate imports the byte-pinned KINEMATIC decoder module of
v5.6.4.2 (declared below); it imports no action evaluator, no Route C module and
no AD/FD5 helper, and reads no expected value of any receipt.  It does not flip
uniform_N_to_infinity_bridge_pass, C1/N1, B4/B5 or any v5.6.4 fail-closed key.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_pinned_members_dense_collar_margins_v5_6_6_11.json"
TEST = HERE / "test_one_omega_topological_so3_pinned_members_dense_collar_margins_v5_6_6_11.py"
SCHEMA = "holo.one-omega-topological-so3-pinned-members-dense-collar-margins-v5-6-6-11.v1"

FROZEN_COMMIT = "ea014fd1a8ed124c353058eb6f0a1c92b90353bc"
LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
DECODER_PATH = HERE / "export_one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitives.py"
DECODER_SHA256 = "4b7eda150cf2d22e04ef2b1b04391c31dc9e618839d7ead9e74a540371ab3d7f"
V5668_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.json"
V5668_SHA256 = "175dae746dcbf19854d1bdb6e0b6b5541d3eb18acea0050d41fccd444f197091"
V56610_PATH = ARTIFACTS / "one_omega_topological_so3_route_c_quadrature_saturation_bridge_ledger_v5_6_6_10.json"
V56610_SHA256 = "c81d8f62a6ed08619decc0a16f31ce1c99cac0f466c1a1e8e4f5de9f82c33fe6"

# Fixed before run (margins are the v5.6.4 TOLERANCES values, transcribed).
SIGNATURE_EIGENVALUE_MARGIN = 2.0e-2
OMEGA_MIN = 5.0e-1
TIMELIKE_MARGIN = 2.0e-1
ROTATION_CUT_LOCUS_MARGIN = 1.0
THETA_POINTS = 256
RHO_POINTS = 129
REFERENCE_METRIC = np.diag((-1.64, 1.17, 1.31, 1.46, 1.17))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))
SIDES = ("plus", "minus")


class MarginGateError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _load_json(path: Path, expected_sha256: str) -> Any:
    digest = _sha256(path)
    if digest != expected_sha256:
        raise MarginGateError(f"byte pin drift for {path.name}: {digest} != {expected_sha256}")
    return json.loads(path.read_text())


def _decode_f64le(block: dict[str, Any]) -> np.ndarray:
    raw = np.frombuffer(base64.b64decode(block["data"]), dtype=block["dtype"])
    return raw.reshape(block["shape"]) if "shape" in block else raw


def load_pinned_decoder():
    if _sha256(DECODER_PATH) != DECODER_SHA256:
        raise MarginGateError("decoder byte pin drift")
    spec = importlib.util.spec_from_file_location("pinned_v5_6_4_2_decoder", DECODER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# radial profiles (v5.6.4.4 C2 contract; formulas certified symbolically in v5.6.6.8)
# --------------------------------------------------------------------------

def radial_profiles(rho: np.ndarray, K: int) -> dict[str, np.ndarray]:
    r = np.asarray(rho, dtype=float)
    h0 = 1.0 - 10.0 * r**3 + 15.0 * r**4 - 6.0 * r**5
    h1 = r * h0
    envelope = 64.0 * (r * (1.0 - r)) ** 3
    z = 2.0 * r - 1.0
    bumps = np.empty((r.size, K))
    for degree in range(K):
        coefficients = np.zeros(degree + 1)
        coefficients[degree] = 1.0
        bumps[:, degree] = envelope * np.polynomial.legendre.legval(z, coefficients)
    return {"h0": h0, "h1": h1, "bumps": bumps}


def _sym5_from_packed(packed: np.ndarray) -> np.ndarray:
    """packed (..., 15) in symmetric5_pairs order -> (..., 5, 5)."""

    out = np.zeros(packed.shape[:-1] + (5, 5))
    for index, (i, j) in enumerate(SYMMETRIC5):
        out[..., i, j] = packed[..., index]
        out[..., j, i] = packed[..., index]
    return out


# --------------------------------------------------------------------------
# dense-collar margins
# --------------------------------------------------------------------------

def member_margins(decoder, bundle: dict[str, Any], member: dict[str, Any]) -> dict[str, Any]:
    N, K = int(member["N"]), int(member["K"])
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    free = _decode_f64le(member["authoritative_free_central_f64le"])
    if free.shape != (int(contract["free_coordinate_dimension"]),):
        raise MarginGateError("free coordinate dimension drift")
    theta = 2.0 * math.pi * np.arange(THETA_POINTS) / THETA_POINTS
    points = np.zeros((THETA_POINTS, 4))
    points[:, 0] = theta  # all modes are functions of x0 + x1; x1 = x2 = x3 = 0 sweeps the full phase
    decoded = decoder.decode_pointwise_boundary(free, contract, points)
    layout = contract["free_layout"]["blocks"]
    tables = decoder.fourier_tables(contract["basis"], points)

    # boundary: gamma Lorentzian, khronon timelike, Omega
    gamma = decoded["common"]["gamma"]
    gamma_eigs = np.linalg.eigvalsh(gamma)
    gamma_lorentzian = bool(np.all(np.sum(gamma_eigs < 0.0, axis=-1) == 1))
    gamma_min_abs_eig = float(np.min(np.abs(gamma_eigs)))
    T_value, T_first = decoder._spectral(decoder._free_get(free, layout, "common.T"), tables)
    time_gradient = T_first[..., 0].copy()
    time_gradient[:, 0] += 1.0
    T_norm2 = np.einsum("pm,pmn,pn->p", time_gradient, np.linalg.inv(gamma), time_gradient)
    T_norm2_max = float(np.max(T_norm2))
    omega_boundary_min = float(np.min(np.exp(decoded["common"]["log_Omega"])))

    rho = np.linspace(0.0, 1.0, RHO_POINTS)
    profiles = radial_profiles(rho, K)
    sides = {}
    for side in SIDES:
        block = decoded["sides"][side]
        g_trace = block["g_trace"]                       # (P, 5, 5)
        J1 = block["boundary_jet_J1"]                    # (P, 64)
        C = block["interior_bump_C"]                     # (P, K, 64)
        g_J = _sym5_from_packed(J1[:, :15])
        g_C = _sym5_from_packed(C[:, :, :15])
        # bulk metric on the dense collar: (R, P, 5, 5)
        g_bulk = (
            REFERENCE_METRIC[None, None]
            + profiles["h0"][:, None, None, None] * (g_trace - REFERENCE_METRIC)[None]
            + profiles["h1"][:, None, None, None] * g_J[None]
            + np.einsum("rk,pkij->rpij", profiles["bumps"], g_C)
        )
        eigs = np.linalg.eigvalsh(g_bulk)
        lorentzian = bool(np.all(np.sum(eigs < 0.0, axis=-1) == 1))
        min_abs_eig = float(np.min(np.abs(eigs)))
        log_omega_bulk = (
            profiles["h0"][:, None] * block["log_Omega_trace"][None]
            + profiles["h1"][:, None] * J1[None, :, 15]
            + np.einsum("rk,pk->rp", profiles["bumps"], C[:, :, 15])
        )
        omega_bulk = np.exp(log_omega_bulk)
        omega_min_interior = float(np.min(omega_bulk[:-1]))   # rho < 1; the rho = 1 row is the structural reference value 1
        omega_min = float(np.min(omega_bulk))
        # rotation chart clearance from the cut locus
        R = block["R_source_to_Q"]
        cos_angle = np.clip((np.trace(R, axis1=-2, axis2=-1) - 1.0) / 2.0, -1.0, 1.0)
        angle_max = float(np.max(np.arccos(cos_angle)))
        orthogonality = float(np.max(np.abs(np.einsum("pij,pik->pjk", R, R) - np.eye(3))))
        # rho = 1 must be the reference exactly (zero extension)
        reference_residual = float(np.max(np.abs(g_bulk[-1] - REFERENCE_METRIC))) + float(np.max(np.abs(log_omega_bulk[-1])))
        sides[side] = {
            "bulk_metric_lorentzian_everywhere": lorentzian,
            "bulk_metric_min_abs_eigenvalue": min_abs_eig,
            "bulk_Omega_min_including_rho1_reference": omega_min,
            "bulk_Omega_min_interior_rho_below_1": omega_min_interior,
            "bulk_log_Omega_max_interior": float(np.max(log_omega_bulk[:-1])),
            "rotation_angle_max": angle_max,
            "rotation_cut_locus_clearance": math.pi - angle_max,
            "rotation_orthogonality_residual": orthogonality,
            "rho1_reference_residual": reference_residual,
            "pass": bool(
                lorentzian
                and min_abs_eig > SIGNATURE_EIGENVALUE_MARGIN
                and omega_min_interior > OMEGA_MIN
                and math.pi - angle_max > ROTATION_CUT_LOCUS_MARGIN
                and orthogonality < 1.0e-10
                and reference_residual < 1.0e-12
            ),
        }
    boundary_pass = bool(gamma_lorentzian and gamma_min_abs_eig > SIGNATURE_EIGENVALUE_MARGIN and T_norm2_max < -TIMELIKE_MARGIN and omega_boundary_min > OMEGA_MIN)
    return {
        "N": N,
        "K": K,
        "member_id": member["member_id"],
        "authoritative_free_central_sha256": member["authoritative_free_central_f64le"]["sha256"],
        "grid": {"theta_points": THETA_POINTS, "rho_points": RHO_POINTS, "direction": "x0 (all modes depend on x0 + x1)"},
        "boundary": {
            "gamma_lorentzian_everywhere": gamma_lorentzian,
            "gamma_min_abs_eigenvalue": gamma_min_abs_eig,
            "khronon_T_norm2_max": T_norm2_max,
            "Omega_boundary_min": omega_boundary_min,
            "pass": boundary_pass,
        },
        "sides": sides,
        "pass": bool(boundary_pass and all(s["pass"] for s in sides.values())),
    }


def build_payload() -> dict[str, Any]:
    bundle = _load_json(BUNDLE_PATH, BUNDLE_SHA256)
    v5668 = _load_json(V5668_PATH, V5668_SHA256)
    v56610 = _load_json(V56610_PATH, V56610_SHA256)
    if v5668["decision"].get("bundle_members_glued_pointwise_off_collocation_pass") is not True:
        raise MarginGateError("upstream pointwise gluing missing")
    if "margins" not in " ".join(v56610["scientific"]["bridge_component_ledger"]["genuine_gaps_not_audit"]):
        raise MarginGateError("upstream ledger does not list the margins gap")
    decoder = load_pinned_decoder()

    members = [member_margins(decoder, bundle, member) for member in bundle["primary_members"]]
    all_pass = bool(all(m["pass"] for m in members))
    clearance = {
        "min_abs_metric_eigenvalue_over_all": min(min(s["bulk_metric_min_abs_eigenvalue"] for s in m["sides"].values()) for m in members),
        "min_Omega_interior_over_all": min(min(s["bulk_Omega_min_interior_rho_below_1"] for s in m["sides"].values()) for m in members),
        "min_Omega_boundary_over_all": min(m["boundary"]["Omega_boundary_min"] for m in members),
        "Omega_at_rho1_is_structural_reference": 1.0,
        "max_khronon_T_norm2_over_all": max(m["boundary"]["khronon_T_norm2_max"] for m in members),
        "min_cut_locus_clearance_over_all": min(min(s["rotation_cut_locus_clearance"] for s in m["sides"].values()) for m in members),
    }

    scientific = {
        "margins": {
            "signature_eigenvalue_margin": SIGNATURE_EIGENVALUE_MARGIN,
            "Omega_min": OMEGA_MIN,
            "timelike_margin": TIMELIKE_MARGIN,
            "rotation_cut_locus_margin": ROTATION_CUT_LOCUS_MARGIN,
            "source": "v5.6.4 TOLERANCES, transcribed",
        },
        "members": members,
        "clearance_summary": clearance,
        "between_grid_points": (
            "The FREE data are degree-one trigonometric polynomials in theta and polynomials of degree <= 8 in rho; "
            "the COMPOSED fields (g_trace, R = exp(...), khronon normalisation) are smooth with harmonic content above "
            "degree one at the 1e-6 level. The 256 x 129 samples have large clearances, but continuity alone does not "
            "turn a finite grid into an everywhere certificate. No quantitative derivative or interval-arithmetic "
            "bound between grid points is computed here; whole-collar membership therefore remains open."
        ),
        "same_objects_theorem": {
            "hypotheses_machine_checked": [
                "free data of the pinned members are degree-<=1 trigonometric polynomials in the single direction x0 + x1 (bundle labels, v5.6.6.10)",
                "radial profiles are the C2 polynomials of v5.6.4.4 (symbolic jets, v5.6.6.8)",
                "pointwise gluing defects <= 4.4e-16 at off-collocation points (v5.6.6.8)",
                "all class margins hold on the dense collar grid with the clearances recorded here",
            ],
            "statement": (
                "This gate proves that each pinned member X_N (N = 1,2,3) satisfies the class margins on the finite "
                "256 x 129 grid only. Conditional on a certified between-grid margin bound and on the Route C sector "
                "list evaluating the same functional S_rel as the v5.6.6.8 theorem, X_N is a point of that restricted "
                "class and exact identity (i) applies: DS_rel[X_N].dX = int_collar E_weak.dq - int_{T^4} H^rho(0). "
                "The Route C direct first variation at quadrature (Qtheta, Qrho) is the trapezoidal (equispaced theta) x "
                "Gauss--Legendre (interior rho nodes) sum of a nodal integrand that is a finite-difference approximation "
                "of the continuum first-variation density: FD5 in the free parameter (FREE_JVP_STEP = 2e-3, O(h^4)) and "
                "7-point coordinate stencils (h = 5e-3, O(h^8)). Hence lim Route C(Qtheta, Qrho) = DS_rel[X_N].dX + B_FD "
                "as both orders go to infinity, where B_FD is the Q-independent stencil bias; the direct sum converges "
                "for continuous integrands with no analyticity hypothesis (positive weights, Weierstrass), analyticity "
                "only fixing the rate measured in v5.6.6.10. The Euler-plus-Green split of Route C additionally uses "
                "barycentric and FFT differentiation, which needs smoothness (the pinned members are smooth), not just "
                "continuity. Components (i)-(iii) and (iv) of the bridge ledger therefore refer to the same objects up "
                "to B_FD."
            ),
            "analytic_not_machine_checked": [
                "convergence of the trapezoidal and Gauss--Legendre rules for continuous integrands (classical)",
                "continuity of the literal density on the margin set (structure of the v5.2 action)",
                "a quantitative between-grid-points certificate for all class margins",
                "that the Route C sector list evaluates the same functional S_rel as the v5.6.6.8 theorem (asserted from the sector names; this gate never touches the density)",
                "the stencil bias B_FD is not bounded here",
            ],
            "still_open_after_this_gate": [
                "gap 3: certify all class margins between the 256 x 129 samples with a quantitative derivative or interval bound",
                "bound the Q-independent stencil bias B_FD (Richardson in FREE_JVP_STEP and in the coordinate stencil step, or complex-step / AD for the free-parameter derivative)",
                "gap 4: proven (not sampled) Jacobian bound and Sobolev lift for the retraction",
                "gap 5: finite DG_N on V_N and the gauge quotient H_N",
                "the N -> infinity direction for arbitrary class members (density of finite free data + continuity (ii), prose)",
            ],
        },
    }

    decision = {
        "pinned_members_margins_on_dense_collar_pass": all_pass,
        "pinned_members_margins_everywhere_on_collar_pass": False,
        "uniform_N_to_infinity_bridge_pass": False,
        "uniform_stability_pass": False,
        "spectral_N_convergence_pass": False,
        "restricted_family_exact_action_identity_pass": False,
        "periodic_box_exhaustion_and_tail_control_pass": False,
        "density_union_C_N_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
    }

    payload = {
        "schema": SCHEMA,
        "classification": "theory_only;sampled_dense_collar_grid;same_objects_conditional;restricted_spectral_family;fail_closed_bridge",
        "decision": decision,
        "fixed_before_run": {
            "THETA_POINTS": THETA_POINTS,
            "RHO_POINTS": RHO_POINTS,
            "margins": {"signature": SIGNATURE_EIGENVALUE_MARGIN, "Omega_min": OMEGA_MIN, "timelike": TIMELIKE_MARGIN, "cut_locus": ROTATION_CUT_LOCUS_MARGIN},
            "reference_metric_diagonal": [float(x) for x in np.diag(REFERENCE_METRIC)],
        },
        "scientific": scientific,
        "independence_boundary": {
            "imports_pinned_kinematic_decoder": True,
            "pinned_decoder": {"path": DECODER_PATH.name, "sha256": DECODER_SHA256},
            "imports_action_evaluators": False,
            "imports_route_c_or_ad_fd5_modules": False,
            "reads_upstream_expected_values": False,
            "radial_profiles": "re-implemented from the v5.6.4.4 contract, not imported",
        },
        "open_obligation": {
            "gap_4": "prove the Jacobian bound of Phi and its Sobolev lift instead of sampling",
            "gap_5": "finite DG_N on V_N and the gauge quotient H_N",
            "interval_bound": "required: certify the margins between grid points using interval arithmetic or an explicit derivative bound",
            "stencil_bias": "bound B_FD before reading any Route C number as DS_rel itself",
        },
        "evidence_boundary": (
            "Machine-checked: all four class margins hold for the three pinned members on a 256 x 129 dense collar grid "
            "with the recorded clearances, the rho = 1 zero extension is exact, and the rotation charts are orthogonal. "
            "Recorded: a conditional same-objects implication with its unmet hypotheses. Not proven: whole-collar "
            "membership, the unconditional same-objects result, the bridge, C1/N1, B4/B5."
        ),
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "v5_6_4_2_pointwise_decoder_sha256": DECODER_SHA256,
            "v5_6_6_8_receipt_sha256": V5668_SHA256,
            "v5_6_6_10_receipt_sha256": V56610_SHA256,
        },
        "provenance": {
            "generator": {"path": str(Path(__file__).resolve().relative_to(REPO)), "sha256": _sha256(Path(__file__))},
            "test": {"path": str(TEST.relative_to(REPO)), "sha256": _sha256(TEST) if TEST.exists() else None},
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "scientific_payload_sha256": _canonical_sha256(scientific),
    }
    return payload


def main() -> None:
    payload = build_payload()
    if not payload["decision"]["pinned_members_margins_on_dense_collar_pass"]:
        raise MarginGateError("dense-collar margin certificate failed")
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    c = payload["scientific"]["clearance_summary"]
    print(
        f"margins={payload['decision']['pinned_members_margins_on_dense_collar_pass']} "
        f"min|eig|={c['min_abs_metric_eigenvalue_over_all']:.3f} minOmegaInterior={c['min_Omega_interior_over_all']:.6f} minOmegaBoundary={c['min_Omega_boundary_over_all']:.3f} "
        f"maxTnorm2={c['max_khronon_T_norm2_over_all']:.3f} cutlocus={c['min_cut_locus_clearance_over_all']:.3f}"
    )


if __name__ == "__main__":
    main()
