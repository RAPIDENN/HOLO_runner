#!/usr/bin/env python3
"""Inventory the still-unproved BRST algebra for the canonical solid action.

This module consumes exactly one input: the canonical one-Omega action-charter
JSON artifact.  It verifies the artifact bytes, recomputes the canonical action
digest, and then checks the field, symmetry, domain, and fail-closed decision
inventories with exact Python types.

The resulting report is intentionally only an inventory.  Candidate BRST
formula strings are recorded so a later graded-algebra implementation has an
unambiguous target, but this module does not evaluate those strings.  In
particular, it does not establish nonlinear nilpotency, tangency to the moving
interface gluing constraints, a gauge fermion, boundary conditions, or an
elliptic/Lorentzian operator domain.  It writes no artifact.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CHARTER_ARTIFACT = HERE / "artifacts" / "one_omega_action_charter_gate.json"

SCHEMA = "holo.one-omega-solid-c2a-brst-algebra-inventory-gate.v1"
CHARTER_SCHEMA = "holo.one-omega-action-charter-gate.v1"
CHARTER_ARTIFACT_SHA256 = (
    "b718cb68934a665cf0a7b89fafffcf2b9ebb2c0bb94c9386ff64f34d91a2e0ef"
)
CHARTER_ACTION_DIGEST = (
    "93105331d9da311afa7845f9939dbd60617b929ae9ede23286fa26bedaa815c1"
)
CHARTER_ACTION_DIGEST_ALGORITHM = "sha256(canonical-json(action_charter))"
CHARTER_ROUTE = "canonical_one_Omega_backreacted_wall_with_rank_full_solid_v1"

C_ITEM_IDS = [
    "C1_ACTION",
    "C2_BRST",
    "C3_DOMAIN",
    "C4_HESSIAN",
    "C5_JACOBIANS",
    "C6_ZERO_MODES",
    "C7_REGULATOR",
    "C8_CONTOUR",
    "C9_REDUCTION",
    "C10_INDEPENDENCE_UNITARITY",
]
N_ITEM_IDS = [
    "N1_ACTION",
    "N2_CONSTRAINTS",
    "N3_CHARACTERISTICS",
    "N4_JUNCTION_BENDING",
    "N5_COUPLED_BVP",
    "N6_GLOBAL_STABILITY",
    "N7_LINEAR_REDUCTION",
    "N8_MATERIAL_PORT",
]

FAIL_CLOSED_DECISION_KEYS = [
    "C2_BRST_pass",
    "C3_DOMAIN_pass",
    "C4_HESSIAN_pass",
    "C5_JACOBIANS_pass",
    "C6_ZERO_MODES_pass",
    "C7_REGULATOR_pass",
    "C8_CONTOUR_pass",
    "C9_REDUCTION_pass",
    "C10_INDEPENDENCE_UNITARITY_pass",
    "P3_complete_gauge_fixed_unitary_determinant_pass",
    "P4_full_same_action_pass",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
]


class SolidC2AInventoryError(ValueError):
    """The canonical input or the inventory report violated its exact scope."""


def _expected_selection() -> dict[str, Any]:
    return {
        "bifundamental_solder_selected": False,
        "bulk_compensator": "Omega",
        "bulk_compensator_count": 1,
        "canonical_genealogy_selected_for_C1_and_N1": True,
        "fixed_external_triad_selected": False,
        "old_P3_gate_automatically_updated": False,
        "solder_route": "three brane Stueckelberg solid scalars X^a",
    }


def _expected_independent_fields() -> dict[str, Any]:
    return {
        "brane_dynamic": [
            "embedding Y_plus^M(sigma) and Y_minus^M(sigma)",
            "khronon T(sigma)",
            "three solid Stueckelberg scalars X^a(sigma)",
        ],
        "bulk_dynamic": [
            "g_MN on each Z2 side",
            "one positive compensator Omega on each Z2 side",
            "one real SO(3) triplet phi^a on each Z2 side",
        ],
        "classical_FP_or_BRST_fields": [],
        "composites_not_independent_fields": [
            "induced gamma_mu_nu",
            "bulk-side normals n_plus^M and n_minus^M",
            "bulk extrinsic curvatures Theta_plus_mu_nu and Theta_minus_mu_nu",
            "u_mu, h_mu_nu, Kcal_mu_nu, acceleration a_mu and leaf curvature Rcal",
            "B^ab, B^(-1/2), E^a_mu and Acal^a",
        ],
        "continuous_Z2_even_traces": ["Omega_Sigma", "varphi^a"],
        "independent_auxiliary_fields": [],
        "independent_internal_gauge_fields": [],
    }


def _expected_symmetries() -> list[str]:
    return [
        "five-dimensional diffeomorphisms with matched interface action",
        "four-dimensional reparametrizations of the moving brane",
        "Z2 exchange of the two bulk sides",
        "monotone khronon reparametrization T maps to f(T)",
        "time-orientation reversal u_mu maps to minus u_mu",
        "global internal ISO(3): X^a maps to R^a_b X^b+c^a and phi^a maps to R^a_b phi^b",
    ]


def _expected_symmetry_breaking() -> dict[str, Any]:
    return {
        "internal_translations": "global shifts X^a maps to X^a+c^a",
        "relative_SO3": "explicitly broken by the Robin solder",
        "relative_SO3_is_gauged": False,
        "unbroken_on_X_equals_vx_background": "diagonal SO(3)⋉R^3_X",
    }


def _expected_domains() -> dict[str, Any]:
    return {
        "BRST_closed_boundary_domain_selected": False,
        "Omega": "Omega>0",
        "excluded": [
            "khronon caustics",
            "solid defects with det(B)=0",
            "a nondynamical external triad",
        ],
        "gluing_is_a_restricted_domain_not_a_multiplier_equation": True,
        "interface_gluing": {
            "configuration_Omega": "Omega_+(Y_+)=Omega_-(Y_-)=Omega_Sigma",
            "configuration_metric": (
                "gamma^+_{mu nu}[g_+,Y_+]=gamma^-_{mu nu}[g_-,Y_-]="
                "gamma_{mu nu}"
            ),
            "configuration_phi": "phi_+^a(Y_+)=phi_-^a(Y_-)=varphi^a",
            "implementation": (
                "the common induced metric and continuous even traces define the "
                "restricted configuration and variation spaces; no gluing Lagrange "
                "multiplier is required"
            ),
            "variation_Omega": (
                "delta[Omega_+(Y_+)]=delta[Omega_-(Y_-)]=delta Omega_Sigma"
            ),
            "variation_metric": (
                "delta gamma^+_{mu nu}=delta gamma^-_{mu nu}=delta gamma_{mu nu}"
            ),
            "variation_phi": (
                "delta[phi_+^a(Y_+)]=delta[phi_-^a(Y_-)]=delta varphi^a"
            ),
        },
        "khronon": (
            "-gamma^(mu nu)*D_mu T*D_nu T>0 with a global time orientation"
        ),
        "solder_patch": "rank-full orientation-preserving sector with det(B)>0",
        "solid": "B^ab positive definite and det(partial_i X^a)>0",
    }


def _canonical_digest(value: Any) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SolidC2AInventoryError(f"cannot canonicalize action charter: {exc}") from exc
    return hashlib.sha256(encoded).hexdigest()


def _decode_strict_json(raw: bytes) -> dict[str, Any]:
    """Decode one byte sequence, rejecting duplicate keys and non-finite values."""

    if type(raw) is not bytes:
        raise SolidC2AInventoryError("strict JSON input must have exact type bytes")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise SolidC2AInventoryError(f"duplicate JSON key: {key!r}")
            result[key] = value
        return result

    def reject_nonfinite(token: str) -> None:
        raise SolidC2AInventoryError(f"non-finite JSON constant: {token}")

    def parse_finite_float(token: str) -> float:
        value = float(token)
        if not math.isfinite(value):
            raise SolidC2AInventoryError(
                f"JSON float overflows finite range: {token}"
            )
        return value

    try:
        text = raw.decode("utf-8")
        payload = json.loads(
            text,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_nonfinite,
            parse_float=parse_finite_float,
        )
    except SolidC2AInventoryError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SolidC2AInventoryError(f"invalid UTF-8 JSON: {exc}") from exc
    if type(payload) is not dict:
        raise SolidC2AInventoryError("charter JSON must be an object")
    return payload


def _require_exact(observed: Any, expected: Any, path: str) -> None:
    """Require exact values and exact container/scalar types recursively."""

    if type(observed) is not type(expected):
        raise SolidC2AInventoryError(
            f"{path} type mismatch: {type(observed).__name__} != "
            f"{type(expected).__name__}"
        )
    if type(expected) is dict:
        if set(observed) != set(expected):
            raise SolidC2AInventoryError(
                f"{path} key inventory mismatch: {sorted(observed)} != "
                f"{sorted(expected)}"
            )
        for key in expected:
            _require_exact(observed[key], expected[key], f"{path}.{key}")
        return
    if type(expected) is list:
        if len(observed) != len(expected):
            raise SolidC2AInventoryError(
                f"{path} length mismatch: {len(observed)} != {len(expected)}"
            )
        for index, item in enumerate(expected):
            _require_exact(observed[index], item, f"{path}[{index}]")
        return
    if observed != expected:
        raise SolidC2AInventoryError(f"{path} value mismatch")


def _require_boolean(payload: dict[str, Any], key: str, expected: bool, path: str) -> None:
    if key not in payload:
        raise SolidC2AInventoryError(f"{path}.{key} is missing")
    value = payload[key]
    if type(value) is not bool or value is not expected:
        raise SolidC2AInventoryError(f"{path}.{key} must be exact {expected!r}")


def _validate_item_ledger(
    ledger: Any,
    *,
    expected_ids: list[str],
    expected_passes: list[bool],
    expected_pass_ids: list[str],
    path: str,
) -> None:
    if type(ledger) is not dict:
        raise SolidC2AInventoryError(f"{path} must be an object")
    items = ledger.get("items")
    if type(items) is not list or len(items) != len(expected_ids):
        raise SolidC2AInventoryError(f"{path}.items inventory mismatch")
    for index, (item, expected_id, expected_pass) in enumerate(
        zip(items, expected_ids, expected_passes, strict=True)
    ):
        item_path = f"{path}.items[{index}]"
        if type(item) is not dict or set(item) != {
            "current_evidence",
            "id",
            "pass",
            "required",
        }:
            raise SolidC2AInventoryError(f"{item_path} key inventory mismatch")
        _require_exact(item["id"], expected_id, f"{item_path}.id")
        _require_exact(item["pass"], expected_pass, f"{item_path}.pass")
        if type(item["required"]) is not str or not item["required"]:
            raise SolidC2AInventoryError(f"{item_path}.required must be a string")
        if type(item["current_evidence"]) is not str or not item["current_evidence"]:
            raise SolidC2AInventoryError(
                f"{item_path}.current_evidence must be a string"
            )
    _require_exact(ledger.get("pass_ids"), expected_pass_ids, f"{path}.pass_ids")
    _require_exact(ledger.get("all_items_pass"), False, f"{path}.all_items_pass")


def validate_charter(payload: Any) -> None:
    """Validate the bounded charter semantics consumed by this inventory.

    Live trust comes from :func:`load_canonical_charter`, which checks the byte
    pin before calling this function.  Standalone semantic validation is useful
    for mutation tests but is not a universal authenticity check for arbitrary
    charter payloads.
    """

    if type(payload) is not dict:
        raise SolidC2AInventoryError("charter payload must have exact type dict")
    _require_exact(payload.get("schema"), CHARTER_SCHEMA, "schema")

    action = payload.get("action_charter")
    if type(action) is not dict:
        raise SolidC2AInventoryError("action_charter must be an object")
    digest = _canonical_digest(action)
    if digest != CHARTER_ACTION_DIGEST:
        raise SolidC2AInventoryError(
            f"live action digest mismatch: {digest} != {CHARTER_ACTION_DIGEST}"
        )
    _require_exact(
        payload.get("action_charter_digest"),
        {
            "algorithm": CHARTER_ACTION_DIGEST_ALGORITHM,
            "sha256": CHARTER_ACTION_DIGEST,
        },
        "action_charter_digest",
    )

    _require_exact(action.get("route_id"), CHARTER_ROUTE, "action_charter.route_id")
    _require_exact(
        action.get("selection"), _expected_selection(), "action_charter.selection"
    )
    _require_exact(
        action.get("independent_fields"),
        _expected_independent_fields(),
        "action_charter.independent_fields",
    )
    _require_exact(
        action.get("symmetries"), _expected_symmetries(), "action_charter.symmetries"
    )
    _require_exact(
        action.get("symmetry_breaking_pattern"),
        _expected_symmetry_breaking(),
        "action_charter.symmetry_breaking_pattern",
    )
    _require_exact(action.get("domains"), _expected_domains(), "action_charter.domains")

    ledgers = payload.get("certificate_ledger")
    if type(ledgers) is not dict:
        raise SolidC2AInventoryError("certificate_ledger must be an object")
    c_ledger = ledgers.get("C1_through_C10")
    _validate_item_ledger(
        c_ledger,
        expected_ids=C_ITEM_IDS,
        expected_passes=[True] + [False] * 9,
        expected_pass_ids=["C1_ACTION"],
        path="certificate_ledger.C1_through_C10",
    )
    _require_exact(
        c_ledger.get("P3_complete"),
        False,
        "certificate_ledger.C1_through_C10.P3_complete",
    )
    _validate_item_ledger(
        ledgers.get("N1_through_N8"),
        expected_ids=N_ITEM_IDS,
        expected_passes=[True] + [False] * 6 + [True],
        expected_pass_ids=["N1_ACTION", "N8_MATERIAL_PORT"],
        path="certificate_ledger.N1_through_N8",
    )

    decision = payload.get("decision")
    if type(decision) is not dict:
        raise SolidC2AInventoryError("decision must be an object")
    _require_boolean(decision, "C1_ACTION_pass", True, "decision")
    _require_boolean(decision, "N1_ACTION_pass", True, "decision")
    for key in FAIL_CLOSED_DECISION_KEYS:
        _require_boolean(decision, key, False, "decision")


def load_canonical_charter(path: Any = CHARTER_ARTIFACT) -> tuple[dict[str, Any], str]:
    """Read the charter bytes exactly once, then hash, decode, and validate them."""

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SolidC2AInventoryError(f"cannot read canonical charter {path}: {exc}") from exc
    if type(raw) is not bytes:
        raise SolidC2AInventoryError("read_bytes() must return exact bytes")
    observed_sha256 = hashlib.sha256(raw).hexdigest()
    if observed_sha256 != CHARTER_ARTIFACT_SHA256:
        raise SolidC2AInventoryError(
            "canonical charter byte hash mismatch: "
            f"{observed_sha256} != {CHARTER_ARTIFACT_SHA256}"
        )
    payload = _decode_strict_json(raw)
    validate_charter(payload)
    return payload, observed_sha256


def _ghost_classification() -> dict[str, Any]:
    return {
        "status": "INVENTORY_ONLY",
        "candidate_required_if_the_declared_redundancies_are_quotiented": [
            {
                "id": "bulk_five_dimensional_diffeomorphisms",
                "candidate_ghosts": ["c_plus^M(x)", "c_minus^M(x)"],
                "qualification": (
                    "the charter does not choose two independent side ghosts versus "
                    "a Z2-equivariant subalgebra"
                ),
            },
            {
                "id": "moving_brane_reparametrizations",
                "candidate_ghosts": ["eta^mu(sigma)"],
                "qualification": (
                    "one common worldvolume reparametrization acts on both embedding "
                    "representatives"
                ),
            },
            {
                "id": "monotone_khronon_target_relabeling",
                "candidate_ghosts": ["kappa(t) evaluated at t=T(sigma)"],
                "qualification": (
                    "candidate Vect(R_T) ghost only if the relabeling is quotiented; "
                    "it is not an arbitrary local FP scalar on Sigma"
                ),
            },
        ],
        "no_local_FP_ghost_from_charter": [
            {
                "id": "global_internal_ISO3",
                "reason": "rigid global symmetry, not an internal gauge symmetry",
            },
            {
                "id": "relative_SO3",
                "reason": "explicitly broken by the Robin solder and not gauged",
            },
            {
                "id": "Z2_exchange",
                "reason": "discrete symmetry; its quotient status is not a local ghost species",
            },
            {
                "id": "time_orientation_reversal",
                "reason": "discrete symmetry, not a connected BRST generator",
            },
        ],
        "forbidden_local_FP_ghost_ids": ["global_internal_ISO3", "relative_SO3"],
        "bulk_side_ghost_identification_selected": False,
        "nonminimal_antighost_and_auxiliary_inventory_selected": False,
    }


def _candidate_transformations() -> dict[str, Any]:
    return {
        "status": "FORMULA_INVENTORY_ONLY",
        "machine_checked": False,
        "graded_evaluation_terms_required": True,
        "formulas": [
            {"field": "g_epsilon", "candidate": "s g_epsilon=-L_c_epsilon g_epsilon"},
            {"field": "Omega_epsilon", "candidate": "s Omega_epsilon=-L_c_epsilon Omega_epsilon"},
            {"field": "phi_epsilon^a", "candidate": "s phi_epsilon^a=-L_c_epsilon phi_epsilon^a"},
            {"field": "c_epsilon^M", "candidate": "s c_epsilon^M=-c_epsilon^N partial_N c_epsilon^M"},
            {"field": "Y_epsilon^M", "candidate": "s Y_epsilon^M=c_epsilon^M(Y_epsilon)-eta^mu partial_mu Y_epsilon^M"},
            {"field": "X^a", "candidate": "s X^a=-eta^mu partial_mu X^a"},
            {"field": "eta^mu", "candidate": "s eta^mu=-eta^nu partial_nu eta^mu"},
            {"field": "T", "candidate": "s T=-eta^mu partial_mu T+kappa(T)"},
            {"field": "kappa(t)", "candidate": "s kappa(t)=-kappa(t) partial_t kappa(t)"},
        ],
        "interpretation": (
            "These strings are inputs for a later graded evaluation; no algebraic "
            "conclusion follows from listing them."
        ),
    }


def _blockers() -> list[dict[str, str]]:
    return [
        {
            "id": "side_ghost_algebra",
            "missing": "choose and derive two-side versus Z2-equivariant bulk ghost algebra",
        },
        {
            "id": "embedded_deformation_algebra",
            "missing": "derive the ambient and worldvolume embedding algebra with graded evaluation terms",
        },
        {
            "id": "khronon_quotient",
            "missing": "choose whether Vect(R_T) is quotiented and specify its ghost function space",
        },
        {
            "id": "nonlinear_nilpotency",
            "missing": "machine-check nonlinear nilpotency on every selected field and ghost",
        },
        {
            "id": "gluing_tangency",
            "missing": "machine-check tangency to metric, Omega and phi pullback gluing constraints",
        },
        {
            "id": "gauge_fermion",
            "missing": "derive one nonminimal sector and gauge fermion for the same action",
        },
        {
            "id": "boundary_domain",
            "missing": "derive BRST-closed field and ghost interface operators",
        },
        {
            "id": "well_posedness",
            "missing": "prove strong ellipticity or a Lorentzian initial-boundary value estimate",
        },
    ]


def _decision() -> dict[str, Any]:
    decision = {
        "C1_ACTION_input_pass": True,
        "N1_ACTION_input_pass": True,
        "selected_action_symmetry_inventory_matches_charter": True,
        "declared_symmetry_ghost_classification_boundary_recorded": True,
        "C2a_BRST_algebra_proof_pass": False,
        "C2_BRST_pass": False,
        "C3_DOMAIN_pass": False,
        "P3_complete_gauge_fixed_unitary_determinant_pass": False,
        "P4_full_same_action_pass": False,
        "B4_pass": False,
        "B5_pass": False,
        "publication_authorized": False,
    }
    for index in range(4, 11):
        decision[f"C{index}_{C_ITEM_IDS[index - 1].split('_', 1)[1]}_pass"] = False
    return decision


def _expected_report() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "classification": (
            "theory_only;inventory_only;solid_C2a_unproved;"
            "C2_C10_P3_P4_B4_B5_fail_closed"
        ),
        "summary": (
            "The canonical solid action fixes which continuous, rigid and discrete "
            "symmetries must be distinguished before BRST construction. Candidate "
            "formula strings are listed but no algebra, nilpotency, gluing tangency, "
            "gauge fermion or operator domain is established."
        ),
        "canonical_input": {
            "path": str(CHARTER_ARTIFACT.relative_to(REPO)),
            "schema": CHARTER_SCHEMA,
            "artifact_sha256": CHARTER_ARTIFACT_SHA256,
            "route_id": CHARTER_ROUTE,
            "action_digest_algorithm": CHARTER_ACTION_DIGEST_ALGORITHM,
            "action_digest_sha256": CHARTER_ACTION_DIGEST,
            "loader_reads_one_byte_sequence": True,
        },
        "consumed_semantics": {
            "solder_route": "three brane Stueckelberg solid scalars X^a",
            "global_internal_ISO3": True,
            "relative_SO3_explicitly_broken": True,
            "relative_SO3_is_gauged": False,
            "independent_internal_gauge_fields": [],
            "independent_auxiliary_fields": [],
            "classical_FP_or_BRST_fields": [],
            "C1_ACTION_input_pass": True,
            "N1_ACTION_input_pass": True,
            "C2_BRST_input_pass": False,
            "BRST_closed_boundary_domain_selected": False,
        },
        "upstream_wording_conflict": {
            "present": True,
            "conflict": (
                "the upstream C2 requirement mentions a relative-SO3 sector even "
                "though the selected action explicitly breaks and does not gauge it"
            ),
            "resolution_for_this_inventory": (
                "do not introduce relative-SO3 ghosts; classify any global collective "
                "coordinates later under zero modes"
            ),
        },
        "ghost_classification": _ghost_classification(),
        "candidate_transformations": _candidate_transformations(),
        "blockers": _blockers(),
        "proof_boundary": {
            "nonlinear_nilpotency_machine_proved": False,
            "gluing_tangency_machine_proved": False,
            "full_gauge_fermion": False,
            "bulk_covariance_machine_proved": False,
            "khronon_u_invariance_machine_proved": False,
            "embedded_deformation_algebroid_machine_proved": False,
            "BRST_closed_boundary_operators_derived": False,
            "strong_ellipticity_or_Lorentzian_well_posedness_proved": False,
        },
        "decision": _decision(),
        "artifact_written": False,
    }


def validate_report(report: Any) -> None:
    """Fail closed if any inventory classification or false boundary is changed."""

    _require_exact(report, _expected_report(), "report")


def build_report() -> dict[str, Any]:
    payload, observed_sha256 = load_canonical_charter()
    if observed_sha256 != CHARTER_ARTIFACT_SHA256:
        raise SolidC2AInventoryError("unreachable canonical hash divergence")
    if _canonical_digest(payload["action_charter"]) != CHARTER_ACTION_DIGEST:
        raise SolidC2AInventoryError("unreachable action digest divergence")
    report = _expected_report()
    validate_report(report)
    return report


def main() -> int:
    print(json.dumps(build_report(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
