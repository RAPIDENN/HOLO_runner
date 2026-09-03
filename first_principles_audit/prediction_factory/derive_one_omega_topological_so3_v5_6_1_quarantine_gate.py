#!/usr/bin/env python3
"""Deterministic v5.5.4 freeze and additive v5.6.1 quarantine receipt.

This adjudicator does not derive a Ward identity and is not a promotion gate.
It byte-pins the independently derived v5.5.2--v5.5.4 receipts, compares the
scientific invariants of the primary and independent v5.5.4 routes, freezes
only their common selected-family 4D lemma, and keeps every larger claim red.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "one_omega_topological_so3_v5_6_1_quarantine_gate.json"
TEST = HERE / "test_one_omega_topological_so3_v5_6_1_quarantine_gate.py"
SCHEMA = "holo.one-omega-topological-so3-v5-6-1-quarantine-gate.v2"


def _source(
    artifact: str,
    artifact_sha256: str,
    schema: str,
    generator: str,
    generator_sha256: str,
    test: str,
    test_sha256: str,
) -> dict[str, Any]:
    return {
        "path": HERE / "artifacts" / artifact,
        "sha256": artifact_sha256,
        "schema": schema,
        "generator_path": HERE / generator,
        "generator_sha256": generator_sha256,
        "test_path": HERE / test,
        "test_sha256": test_sha256,
    }


SOURCES = {
    "v5_2_action_charter": _source(
        "one_omega_topological_so3_classical_v5_2_gate.json",
        "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
        "holo.one-omega-topological-so3-classical-v5-2-gate.v1",
        "derive_one_omega_topological_so3_classical_v5_2_gate.py",
        "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
        "test_one_omega_topological_so3_classical_v5_2_gate.py",
        "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
    ),
    "v5_5_2_primary": _source(
        "one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.json",
        "4e068475ae316684cebd0f68e10d183fff7c0d90c46b155f2dfc8be4b3b0d6e8",
        "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-gate.v1",
        "derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py",
        "00f8fa443bda37711d2456cb5e55c8a5c349d1c7f814a44c63203e3c02836e1e",
        "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py",
        "4547d1e7f361b2c9b931dba3a9a5a5829d2a2563ab4a0c9c54a154f9292f7aca",
    ),
    "v5_5_2_redteam": _source(
        "one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.json",
        "4c94c2abeb24fb3444be4f79c93aa383659feac9e706eea7fe4fe2aac85bc7f6",
        "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-redteam.v1",
        "derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.py",
        "470d3c8b2bc7429ad77083c39f9112cc1908501b176d72f3b464b2f37f62696d",
        "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.py",
        "6b373b7cccac70316ca52172fe65cfad991f90d0ad160afa4cdb2994e67e6f4f",
    ),
    "v5_5_3_primary": _source(
        "one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.json",
        "0bae4d93de669a95becb3742e4e2f8ad2f99517e9b6efa7a7cfc518b9c6d832d",
        "holo.one-omega-topological-so3-full-action-gauge-noether-v5-5-3-gate.v1",
        "derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.py",
        "3d9a57482d3a80832427d4d3e9e645e09d78166c3070de49de9f9cb89cbfd692",
        "test_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.py",
        "9d88139a02ca6c708a921a51e27287480db65c81e0c6b008d5717f3775c99e34",
    ),
    "v5_5_3_redteam": _source(
        "one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate.json",
        "21da830fcba7e08708723ba05a77d49be126fc25bea40660eb66c5fd979b1cc7",
        "holo.one-omega-topological-so3-full-action-gauge-noether-v5-5-3-redteam-gate.v1",
        "derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate.py",
        "7d4f636c1ef37dc96da13992d75ca96ff737a14a7b301f12997b9536b11aca1a",
        "test_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate.py",
        "eed63000a1b6a0c76466f8732d86a52327cf7d556b675c1881ba1f606053c4e0",
    ),
    "v5_5_4_primary": _source(
        "one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.json",
        "d5e60c535cdfb19aeee7d8007e3c39afcff699e34128ca1a016d4ba4469cd23c",
        "holo.one-omega-topological-so3-interface-diffeomorphism-khronon-v5-5-4-gate.v1",
        "derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.py",
        "299d07965f0a6feb4f9f577664a7c13f09107fefe85ac80ac6efdf5b0e22c024",
        "test_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.py",
        "2c37ccd958c9bee99d8d3a5b28bd345a22b90786d1b36b33cf01c23477c877c6",
    ),
    "v5_5_4_redteam": _source(
        "one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam.json",
        "e1e70a013513ec154f3458891b28bb77a47739bcc264b571935cac1f06d1ade7",
        "holo.one-omega-topological-so3-interface-diffeomorphism-khronon-v5-5-4-redteam.v1",
        "derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam.py",
        "ddfbd9fc7bb3d50f09bebea927b6a63c1295aa729fa17e88be7bba7cd0f08bab",
        "test_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam.py",
        "04a44a3956056ee82da0a87543fd9696b5505e1c7077c35f8a64710a64bc5142",
    ),
}

PRIMARY_TOLERANCES = {
    "local_density_L2_max": 2.0e-8,
    "local_density_Linf_max": 2.0e-7,
    "action_vs_Euler_max": 2.0e-7,
    "local_route_max": 2.0e-9,
    "Stokes_weak_max": 2.0e-7,
    "mutant_residual_min": 1.0e-6,
}
REDTEAM_TOLERANCES = {
    "R_groupoid_nominal_max": 2.0e-10,
    "component_action_vs_JVP_max": 2.0e-6,
    "component_local_JVP_RMS_min": 1.0e-8,
    "density_route_Linf_max": 2.0e-10,
    "induced_pullback_nominal_max": 2.0e-9,
    "local_density_L2_max": 5.0e-7,
    "local_density_Linf_max": 5.0e-6,
    "matter_shift_nominal_max": 2.0e-8,
    "mutant_residual_min": 1.0e-6,
    "radial_V4_gauge_derivative_max": 2.0e-10,
    "required_mutant_minimum": 1.0e-6,
}
REDTEAM_ADDITIONAL_TOLERANCES = {
    "Stokes_weak_max": 2.0e-5,
    "minimum_coordinate_activity": 1.0e-5,
    "minimum_absolute_slot_pairing": 1.0e-7,
}
COMPONENT_LABELS = [
    "gamma_00", "gamma_01", "gamma_02", "gamma_03", "gamma_11",
    "gamma_12", "gamma_13", "gamma_22", "gamma_23", "gamma_33",
    "T", "Omega", "psi_0", "psi_1", "psi_2", "psi_3",
]
ACTION_KEYS_REPRODUCED = (
    "Robin_intrinsic",
    "bulk_gauged",
    "foliation_lower",
    "full_V4",
    "gauged_conformal_derivative",
    "wall_background",
)
PRIMARY_ACTION_KEYS = frozenset((
    "Robin_intrinsic", "foliation_lower", "wall_background",
))
PRIMARY_COEFFICIENT_KEYS = frozenset((
    "brane_Mb_squared", "lambda_K", "xi", "eta", "B4_bar",
    "k_infinity", "M5_cubed", "compensator_metric_G", "brane_beta",
    "Robin_kappa_hat", "Robin_y",
))
REDTEAM_COEFFICIENT_KEYS = frozenset((*PRIMARY_COEFFICIENT_KEYS,
    "material_Z5_per_side", "material_mass_M",
))
XI_KEYS = frozenset(("xi_variant_0", "xi_variant_1"))

FORCED_FALSE_KEYS = (
    "full_bulk_diffeomorphism_Ward_pass",
    "complete_moving_embedding_Ward_pass",
    "continuum_all_configurations_theorem_pass",
    "complete_v5_2_all_field_normal_embedding_pass",
    "full_off_shell_Green_theorem_accepted",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "N4_JUNCTION_BENDING_pass",
    "P4_full_same_action_pass",
    "v5_6_promotion_authorized",
    "frozen_v5_6_receipt_rehabilitated",
    "B4_pass",
    "B5_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "unrestricted_large_gauge_sector_pass",
    "publication_authorized",
)
ALLOWED_TRUE_PASS_KEYS = frozenset((
    "ADM_induced_selected_local_chain_primary_redteam_pass",
    "internal_SO3_full_5D_primary_redteam_pass",
    "interface_diff_selected_family_primary_redteam_pass",
    "scientific_invariants_coefficients_hashes_residuals_comparison_pass",
    "v5_5_4_selected_4D_family_frozen_lemma_pass",
    "underresolved_Gauss_diagnostic_correctly_red_pass",
    "quarantine_consistency_pass",
))


class V561QuarantineError(ValueError):
    """A source drifted or an illegal promotion escaped quarantine."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise V561QuarantineError(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def _embedded_hash(payload: Mapping[str, Any], name: str) -> str | None:
    provenance = payload.get("provenance", {})
    if not isinstance(provenance, Mapping):
        return None
    flat = provenance.get(f"{name}_sha256")
    if isinstance(flat, str):
        return flat
    nested = provenance.get(name, {})
    if isinstance(nested, Mapping) and isinstance(nested.get("sha256"), str):
        return str(nested["sha256"])
    return None


def _load_sources() -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, contract in SOURCES.items():
        artifact_path = Path(contract["path"])
        generator_path = Path(contract["generator_path"])
        test_path = Path(contract["test_path"])
        if _sha256(artifact_path) != contract["sha256"]:
            raise V561QuarantineError(f"source byte hash mismatch: {name}")
        if _sha256(generator_path) != contract["generator_sha256"]:
            raise V561QuarantineError(f"source generator hash mismatch: {name}")
        if _sha256(test_path) != contract["test_sha256"]:
            raise V561QuarantineError(f"source test hash mismatch: {name}")
        try:
            payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise V561QuarantineError(f"cannot parse source {name}: {exc}") from exc
        if type(payload) is not dict or payload.get("schema") != contract["schema"]:
            raise V561QuarantineError(f"source schema mismatch: {name}")
        if _embedded_hash(payload, "generator") != contract["generator_sha256"]:
            raise V561QuarantineError(f"source generator provenance mismatch: {name}")
        if _embedded_hash(payload, "test") != contract["test_sha256"]:
            raise V561QuarantineError(f"source test provenance mismatch: {name}")
        loaded[name] = payload
    return loaded


def _numeric_ast(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _numeric_ast(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "math"
        and node.func.attr == "sqrt"
        and len(node.args) == 1
        and not node.keywords
    ):
        return math.sqrt(_numeric_ast(node.args[0]))
    raise V561QuarantineError("non-numeric coefficient expression in pinned source")


def _extract_numeric_mapping(path: Path, assignment: str) -> dict[str, float]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == assignment for target in node.targets):
            continue
        if not isinstance(node.value, ast.Dict):
            break
        values: dict[str, float] = {}
        for key_node, value_node in zip(node.value.keys, node.value.values, strict=True):
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                raise V561QuarantineError(f"non-string key in {assignment}")
            values[key_node.value] = _numeric_ast(value_node)
        return values
    raise V561QuarantineError(f"missing {assignment} in {path.name}")


def _extract_string_mapping(path: Path, assignment: str) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == assignment for target in node.targets):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError) as exc:
            raise V561QuarantineError(f"non-literal {assignment} in {path.name}") from exc
        if not isinstance(value, dict) or not all(
            isinstance(key, str) and isinstance(item, str) for key, item in value.items()
        ):
            raise V561QuarantineError(f"malformed {assignment} in {path.name}")
        return value
    raise V561QuarantineError(f"missing {assignment} in {path.name}")


def _scope_evidence(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    d52p = sources["v5_5_2_primary"]["decision"]
    d52r = sources["v5_5_2_redteam"]["decision"]
    d53p = sources["v5_5_3_primary"]["decision"]
    d53r = sources["v5_5_3_redteam"]["decision"]
    d54p = sources["v5_5_4_primary"]["decision"]
    d54r = sources["v5_5_4_redteam"]["decision"]
    return {
        "ADM_induced_selected_local_chain_primary_redteam": bool(
            d52p.get("candidate_checks_pass") is True
            and d52p.get("induced_ADM_bidirectional_Jacobian_pass") is True
            and d52r.get("independent_redteam_checks_pass") is True
            and d52r.get("bidirectional_ADM_Jacobian_rank10_pass") is True
        ),
        "internal_SO3_full_5D_primary_redteam": bool(
            d53p.get("bulk_full_v5_2_internal_SO3_Ward_pass") is True
            and d53p.get("internal_SO3_full_action_selected_trivial_sector_Ward_pass") is True
            and d53r.get("full_5D_internal_SO3_gauge_Noether_independent_pass") is True
        ),
        "interface_diff_selected_family_primary_redteam": bool(
            d54p.get("interface_diffeomorphism_khronon_Ward_selected_family_pass") is True
            and d54p.get("compact_xi_weak_Ward_zero_by_local_Stokes_pass") is True
            and d54r.get("independent_interface_diffeomorphism_khronon_redteam_pass") is True
            and d54r.get("compact_xi_weak_Ward_zero_by_local_Stokes_redteam_pass") is True
        ),
        "underresolved_Gauss_diagnostic_is_red_in_both": bool(
            d54p.get("underresolved_Gauss_volume_Ward_diagnostic_pass") is False
            and d54p.get("compact_divergence_quadrature_convergence_pass") is False
            and d54r.get("underresolved_Gauss_volume_Ward_diagnostic_pass") is False
            and d54r.get("compact_divergence_quadrature_convergence_pass") is False
        ),
        "full_bulk_diff_is_red": d54r.get("full_bulk_diffeomorphism_Ward_pass") is False,
        "moving_embedding_is_red": d54r.get("complete_moving_embedding_Ward_pass") is False,
        "continuum_theorem_is_red_in_both": bool(
            d54p.get("continuum_all_configurations_theorem_pass") is False
            and d54r.get("continuum_all_configurations_theorem_pass") is False
        ),
        "all_field_normal_embedding_is_red": bool(
            d52p.get("complete_v5_2_all_field_normal_embedding_pass") is False
            and d52r.get("complete_v5_2_all_field_normal_embedding_pass") is False
            and d54p.get("complete_v5_2_all_field_normal_embedding_pass") is False
            and d54r.get("complete_v5_2_all_field_normal_embedding_pass") is False
        ),
        "BV_BFV_is_red": bool(
            d53p.get("complete_BV_BFV_boundary_complex_pass") is False
            and d53r.get("complete_BV_BFV_boundary_complex_pass") is False
            and d54r.get("complete_BV_BFV_boundary_complex_pass") is False
        ),
        "large_gauge_is_red": bool(
            d53p.get("unrestricted_large_gauge_sector_pass") is False
            and d53r.get("regulated_interface_charge_completion_pass") is False
        ),
    }


def _scientific_comparison(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    v52 = sources["v5_2_action_charter"]
    primary = sources["v5_5_4_primary"]
    redteam = sources["v5_5_4_redteam"]
    charter = v52["exact_classical_charter"]
    v52_actions = charter["exact_action"]
    v52_coefficients = charter["coefficient_policy"]["parameters"]
    primary_spec = SOURCES["v5_5_4_primary"]
    redteam_spec = SOURCES["v5_5_4_redteam"]
    primary_coefficients = _extract_numeric_mapping(
        Path(primary_spec["generator_path"]), "EXPECTED_COEFFICIENTS"
    )
    redteam_coefficients = _extract_numeric_mapping(
        Path(redteam_spec["generator_path"]), "EXPECTED_COEFFICIENTS"
    )
    primary_actions = _extract_string_mapping(
        Path(primary_spec["generator_path"]), "EXPECTED_ACTIONS"
    )
    redteam_actions = redteam["formula_ledger"]["literal_action"]

    coefficient_checks = {
        "primary_coefficient_keyset_exact": (
            frozenset(primary_coefficients) == PRIMARY_COEFFICIENT_KEYS
        ),
        "redteam_coefficient_keyset_exact": (
            frozenset(redteam_coefficients) == REDTEAM_COEFFICIENT_KEYS
        ),
        "primary_declared_matches_v5_2": bool(
            frozenset(primary_coefficients) == PRIMARY_COEFFICIENT_KEYS
            and all(
            key in v52_coefficients and float(v52_coefficients[key]) == value
            for key, value in primary_coefficients.items()
            )
        ),
        "redteam_declared_matches_v5_2": bool(
            frozenset(redteam_coefficients) == REDTEAM_COEFFICIENT_KEYS
            and all(
            key in v52_coefficients and float(v52_coefficients[key]) == value
            for key, value in redteam_coefficients.items()
            )
        ),
        "shared_coefficients_identical": bool(
            frozenset(primary_coefficients) == PRIMARY_COEFFICIENT_KEYS
            and frozenset(redteam_coefficients) == REDTEAM_COEFFICIENT_KEYS
            and all(
            redteam_coefficients.get(key) == value
            for key, value in primary_coefficients.items()
            )
        ),
    }
    action_checks = {
        "primary_action_keyset_exact": frozenset(primary_actions) == PRIMARY_ACTION_KEYS,
        "redteam_action_keyset_exact": (
            frozenset(redteam_actions) == frozenset(ACTION_KEYS_REPRODUCED)
        ),
        "primary_interface_literals_match_v5_2": bool(
            frozenset(primary_actions) == PRIMARY_ACTION_KEYS
            and all(
            v52_actions.get(key) == value for key, value in primary_actions.items()
            )
        ),
        "redteam_six_literals_match_v5_2": bool(
            frozenset(redteam_actions) == frozenset(ACTION_KEYS_REPRODUCED)
            and all(
            redteam_actions.get(key) == v52_actions.get(key)
            for key in ACTION_KEYS_REPRODUCED
            )
        ),
        "v5_2_total_action_is_complete": v52_actions.get("total") == (
            "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF"
        ),
    }

    primary_runtime = primary["runtime"]
    redteam_runtime = redteam["runtime"]
    primary_probes = primary_runtime["compact_arbitrary_xi_probes"]
    redteam_probes = redteam_runtime["compact_xi_probes"]
    primary_residuals = {
        "local_density_L2": [row["local_density_covariance_L2"] for row in primary_probes],
        "local_density_Linf": [row["local_density_covariance_Linf"] for row in primary_probes],
        "action_vs_Euler": [
            row["finite_difference_vs_automatic_sum_error"] for row in primary_probes
        ],
        "local_route": [
            row["reverse_vs_forward_local_slot_max_error"] for row in primary_probes
        ],
        "Stokes_weak": primary_runtime["selected_family_Stokes_weak_residual_bounds"],
        "minimum_mutant_witness": primary_runtime["minimum_mutant_witness"],
    }
    redteam_residuals = {
        "local_density_L2": [row["local_density_covariance_L2"] for row in redteam_probes],
        "local_density_Linf": [row["local_density_covariance_Linf"] for row in redteam_probes],
        "component_action_vs_JVP": [
            row["maximum_component_action_vs_JVP_error"] for row in redteam_probes
        ],
        "pointwise_16_component_additivity": [
            row["component_JVP_additivity"]["pointwise_Linf_error"]
            for row in redteam_probes
        ],
        "density_route_Linf": [
            max(row["independent_density_route_comparison"]["action_vs_JVP_Linf"],
                row["independent_density_route_comparison"]["action_vs_Stokes_Linf"])
            for row in redteam_probes
        ],
        "Stokes_weak": redteam_runtime["selected_family_Stokes_weak_residual_bounds"],
        "minimum_component_local_JVP_RMS": [
            row["minimum_component_local_JVP_RMS"] for row in redteam_probes
        ],
        "minimum_absolute_slot_pairing": [
            row["minimum_absolute_slot_pairing"] for row in redteam_probes
        ],
        "minimum_coordinate_activity": redteam_runtime["activity"][
            "minimum_coordinate_activity"
        ],
        "maximum_nominal_closure_error": redteam_runtime["maximum_nominal_closure_error"],
        "minimum_mutant_witness": redteam_runtime["minimum_mutant_witness"],
        "required_control_mutants": redteam_runtime["required_independent_control_mutants"],
    }

    primary_within_tolerance = bool(
        max(primary_residuals["local_density_L2"]) < PRIMARY_TOLERANCES["local_density_L2_max"]
        and max(primary_residuals["local_density_Linf"]) < PRIMARY_TOLERANCES["local_density_Linf_max"]
        and max(primary_residuals["action_vs_Euler"]) < PRIMARY_TOLERANCES["action_vs_Euler_max"]
        and max(primary_residuals["local_route"]) < PRIMARY_TOLERANCES["local_route_max"]
        and max(primary_residuals["Stokes_weak"].values()) < PRIMARY_TOLERANCES["Stokes_weak_max"]
        and primary_residuals["minimum_mutant_witness"]
        > PRIMARY_TOLERANCES["mutant_residual_min"]
    )
    rt_tol = redteam_runtime["published_tolerances"]
    tolerance_manifest_exact = rt_tol == REDTEAM_TOLERANCES
    controls = redteam_runtime["independent_control_reconstructions"]
    redteam_within_tolerance = bool(
        max(redteam_residuals["local_density_L2"]) < REDTEAM_TOLERANCES["local_density_L2_max"]
        and max(redteam_residuals["local_density_Linf"]) < REDTEAM_TOLERANCES["local_density_Linf_max"]
        and max(redteam_residuals["component_action_vs_JVP"]) < REDTEAM_TOLERANCES["component_action_vs_JVP_max"]
        and max(redteam_residuals["pointwise_16_component_additivity"]) < REDTEAM_TOLERANCES["density_route_Linf_max"]
        and max(redteam_residuals["density_route_Linf"]) < REDTEAM_TOLERANCES["density_route_Linf_max"]
        and frozenset(redteam_residuals["Stokes_weak"]) == XI_KEYS
        and max(redteam_residuals["Stokes_weak"].values())
        < REDTEAM_ADDITIONAL_TOLERANCES["Stokes_weak_max"]
        and min(redteam_residuals["minimum_component_local_JVP_RMS"])
        > REDTEAM_TOLERANCES["component_local_JVP_RMS_min"]
        and min(redteam_residuals["minimum_absolute_slot_pairing"])
        > REDTEAM_ADDITIONAL_TOLERANCES["minimum_absolute_slot_pairing"]
        and redteam_residuals["minimum_coordinate_activity"]
        > REDTEAM_ADDITIONAL_TOLERANCES["minimum_coordinate_activity"]
        and redteam_residuals["minimum_mutant_witness"]
        > REDTEAM_TOLERANCES["mutant_residual_min"]
        and min(redteam_residuals["minimum_mutant_witness"], *redteam_residuals["required_control_mutants"].values())
        > REDTEAM_TOLERANCES["required_mutant_minimum"]
        and controls["R_groupoid_frozen"]["nominal_invariance_error"] < REDTEAM_TOLERANCES["R_groupoid_nominal_max"]
        and controls["induced_pullback_broken"]["nominal_pullback_max_error"] < REDTEAM_TOLERANCES["induced_pullback_nominal_max"]
        and controls["matter_T_ui_omitted"]["nominal_shift_max_error"] < REDTEAM_TOLERANCES["matter_shift_nominal_max"]
        and abs(controls["full_V4_anisotropic"]["signed_radial_gauge_derivative"])
        < REDTEAM_TOLERANCES["radial_V4_gauge_derivative_max"]
    )

    redteam_component_labels = [
        [row["component"] for row in probe["signed_component_action_and_local_JVP"]]
        for probe in redteam_probes
    ]
    redteam_stokes = redteam_runtime["compact_Stokes_boundary_flux"]
    primary_stokes = primary_runtime["compact_Stokes_boundary_flux"]
    geometric_contract = bool(
        primary_runtime["spacetime_dimension"] == 4
        and len(primary_probes) == len(redteam_probes) == 2
        and {row["xi_variant"] for row in primary_probes} == {0, 1}
        and {row["xi_variant"] for row in redteam_probes} == {0, 1}
        and all(row["point_count"] == 81 for row in primary_probes + redteam_probes)
        and all(labels == COMPONENT_LABELS for labels in redteam_component_labels)
        and all(len(row["signed_component_action_and_local_JVP"]) == 16 for row in redteam_probes)
        and frozenset(primary_stokes) == XI_KEYS
        and frozenset(redteam_stokes) == XI_KEYS
        and all(row["face_count"] == len(row["faces"]) == 8 for row in primary_stokes.values())
        and all(row["face_count"] == len(row["faces"]) == 8 for row in redteam_stokes.values())
        and redteam_runtime["activity"]["all_four_coordinates_active"] is True
        and controls["induced_pullback_broken"]["ambient_dimension"] == 5
        and controls["induced_pullback_broken"]["interface_dimension"] == 4
    )
    lineages_match = bool(
        primary["lineage"]["v5_2_artifact_sha256"] == SOURCES["v5_2_action_charter"]["sha256"]
        and redteam["lineage"]["v5_2_artifact_sha256"] == SOURCES["v5_2_action_charter"]["sha256"]
        and redteam["lineage"]["primary_v5_5_4"]["artifact_sha256"] == SOURCES["v5_5_4_primary"]["sha256"]
        and redteam["lineage"]["primary_v5_5_4"]["generator_sha256"] == SOURCES["v5_5_4_primary"]["generator_sha256"]
        and redteam["lineage"]["primary_v5_5_4"]["test_sha256"] == SOURCES["v5_5_4_primary"]["test_sha256"]
    )
    underresolved_gauss_red = bool(
        frozenset(primary_runtime["compact_weak_quadrature_convergence"]) == XI_KEYS
        and frozenset(redteam_runtime["underresolved_Gauss_volume_diagnostics"]) == XI_KEYS
        and
        all(row["certified"] is False for row in primary_runtime["compact_weak_quadrature_convergence"].values())
        and all(
            row["certified"] is False
            and row["convergence_to_zero_tested"] is False
            and row["used_by_selected_family_decision"] is False
            for row in redteam_runtime["underresolved_Gauss_volume_diagnostics"].values()
        )
    )

    checks = {
        **coefficient_checks,
        **action_checks,
        "input_lineages_match": lineages_match,
        "selected_family_geometric_contract_matches": geometric_contract,
        "primary_residuals_within_fixed_tolerances": primary_within_tolerance,
        "redteam_residuals_within_fixed_tolerances": redteam_within_tolerance,
        "redteam_tolerance_manifest_exact": tolerance_manifest_exact,
        "underresolved_Gauss_preserved_red": underresolved_gauss_red,
    }
    return {
        "checks": checks,
        "all_checks_pass": all(value is True for value in checks.values()),
        "action_charter": {
            "route_id": charter["route_id"],
            "exact_action_sha256": _canonical_sha256(v52_actions),
            "coefficient_policy_sha256": _canonical_sha256(charter["coefficient_policy"]),
            "exact_total_action": v52_actions["total"],
            "reproduced_literal_keys": list(ACTION_KEYS_REPRODUCED),
        },
        "coefficient_comparison": {
            "v5_2_parameters": v52_coefficients,
            "primary_declared": primary_coefficients,
            "redteam_declared": redteam_coefficients,
        },
        "fixed_tolerances": {
            "primary": PRIMARY_TOLERANCES,
            "redteam": REDTEAM_TOLERANCES,
            "redteam_additional": REDTEAM_ADDITIONAL_TOLERANCES,
        },
        "scientific_invariants": {
            "interface_dimension": 4,
            "ambient_pullback_control_dimension": 5,
            "compact_xi_probe_count": 2,
            "quadrature_point_count_per_probe": 81,
            "oriented_face_count_per_probe": 8,
            "signed_Euler_JVP_component_count": 16,
            "signed_component_labels": COMPONENT_LABELS,
            "primary_action_scope": primary_runtime["action_scope"],
            "redteam_action_scope": redteam_runtime["action_scope"],
        },
        "raw_residual_comparison": {
            "note": "Independent analytic families are checked against fixed contracts; numerical equality is neither expected nor required.",
            "primary": primary_residuals,
            "redteam": redteam_residuals,
        },
        "archived_red_Gauss_diagnostics": {
            "primary": primary_runtime["compact_weak_quadrature_convergence"],
            "redteam": redteam_runtime["underresolved_Gauss_volume_diagnostics"],
        },
    }


def _adjudicate(
    evidence: Mapping[str, bool], scientific_checks: Mapping[str, bool]
) -> dict[str, Any]:
    required_evidence = (
        "ADM_induced_selected_local_chain_primary_redteam",
        "internal_SO3_full_5D_primary_redteam",
        "interface_diff_selected_family_primary_redteam",
        "underresolved_Gauss_diagnostic_is_red_in_both",
        "full_bulk_diff_is_red",
        "moving_embedding_is_red",
        "continuum_theorem_is_red_in_both",
        "all_field_normal_embedding_is_red",
        "BV_BFV_is_red",
        "large_gauge_is_red",
    )
    scope_ok = all(evidence.get(key) is True for key in required_evidence)
    scientific_ok = bool(scientific_checks) and all(
        value is True for value in scientific_checks.values()
    )
    freeze_ok = bool(
        scope_ok
        and scientific_ok
        and evidence.get("interface_diff_selected_family_primary_redteam") is True
    )
    decision: dict[str, Any] = {
        "ADM_induced_selected_local_chain_primary_redteam_pass": evidence.get(
            "ADM_induced_selected_local_chain_primary_redteam", False
        ),
        "internal_SO3_full_5D_primary_redteam_pass": evidence.get(
            "internal_SO3_full_5D_primary_redteam", False
        ),
        "interface_diff_selected_family_primary_redteam_pass": evidence.get(
            "interface_diff_selected_family_primary_redteam", False
        ),
        "scientific_invariants_coefficients_hashes_residuals_comparison_pass": scientific_ok,
        "v5_5_4_selected_4D_family_frozen_lemma_pass": freeze_ok,
        "underresolved_Gauss_diagnostic_correctly_red_pass": evidence.get(
            "underresolved_Gauss_diagnostic_is_red_in_both", False
        ),
        "quarantine_consistency_pass": scope_ok and scientific_ok,
        "quarantine_active": True,
        "status": (
            "V5_5_4_SELECTED_4D_FAMILY_LEMMA_FROZEN__"
            "FULL_BULK_MOVING_CONTINUUM_C1_N1_V56_B4_B5_BV_LARGE_GAUGE_PUBLICATION_QUARANTINED"
        ),
    }
    for key in FORCED_FALSE_KEYS:
        decision[key] = False
    _enforce_quarantine(decision)
    return decision


def _enforce_quarantine(decision: Mapping[str, Any]) -> None:
    if decision.get("quarantine_active") is not True:
        raise V561QuarantineError("quarantine must remain active")
    if any(decision.get(key) is not False for key in FORCED_FALSE_KEYS):
        raise V561QuarantineError("illegal downstream promotion escaped quarantine")
    unexpected_true_passes = {
        key
        for key, value in decision.items()
        if key.endswith("_pass") and value is True and key not in ALLOWED_TRUE_PASS_KEYS
    }
    if unexpected_true_passes:
        raise V561QuarantineError(
            f"unexpected green pass keys escaped quarantine: {sorted(unexpected_true_passes)}"
        )
    unexpected_frozen = {
        key
        for key, value in decision.items()
        if "frozen" in key and value is True
        and key != "v5_5_4_selected_4D_family_frozen_lemma_pass"
    }
    if unexpected_frozen:
        raise V561QuarantineError(
            f"unexpected frozen scope escaped quarantine: {sorted(unexpected_frozen)}"
        )


def build_payload() -> dict[str, Any]:
    sources = _load_sources()
    evidence = _scope_evidence(sources)
    comparison = _scientific_comparison(sources)
    decision = _adjudicate(evidence, comparison["checks"])
    if decision["quarantine_consistency_pass"] is not True:
        raise V561QuarantineError("source scopes or scientific comparison failed")
    true_passes = {
        key for key, value in decision.items() if key.endswith("_pass") and value is True
    }
    if true_passes != ALLOWED_TRUE_PASS_KEYS:
        raise V561QuarantineError("final green pass-key allowlist mismatch")
    return {
        "schema": SCHEMA,
        "claim": (
            "Deterministic freeze of v5.5.4 only as an independently reproduced selected-family "
            "4D interface Ward lemma; no C1/N1/v5.6/B4/B5 promotion is authorized."
        ),
        "earlier_gate_helpers_imported": [],
        "source_hashes": {
            name: {
                key: contract[key]
                for key in (
                    "sha256", "schema", "generator_sha256", "test_sha256"
                )
            }
            for name, contract in SOURCES.items()
        },
        "scope_evidence": evidence,
        "scientific_comparison": comparison,
        "open_obligations_before_C1_N1_gate": {
            "convergence": (
                "OPEN: local automatic/Stokes closure is green, while under-resolved Gauss "
                "volume quadrature remains an archived red diagnostic and no continuum theorem follows."
            ),
            "full_bulk": (
                "OPEN: the complete 5D metric, scalar, BF and matter bulk diffeomorphism variation "
                "has not yet been combined with the interface identity."
            ),
            "moving_embedding": (
                "OPEN: the 4D-to-5D pullback control is nontrivial, but all cross terms of one "
                "fully coupled moving embedding have not yet been derived together."
            ),
            "off_shell_continuous_extension": (
                "OPEN: certificates cover declared analytic families and probes, not every smooth "
                "off-shell field/variation or noncompact boundary parameter."
            ),
        },
        "decision": decision,
        "consumption_policy": {
            "allowed": (
                "selected local induced-ADM chain; full 5D internal SO(3) Ward in its declared "
                "trivial/null-homotopic sector; v5.5.4 interface Ward only on the audited selected 4D family"
            ),
            "forbidden": (
                "promotion of C1, N1, frozen v5.6, B4, B5, BV-BFV, unrestricted large gauge, "
                "full bulk diffeomorphisms, complete moving embedding, continuum theorem, or publication"
            ),
            "frozen_v5_6_modified": False,
            "authorization_statement": (
                "This deterministic freeze/quarantine receipt is evidence separation, not promotion authority."
            ),
        },
        "provenance": {
            "generator": str(Path(__file__).resolve().relative_to(HERE.parents[1])),
            "generator_sha256": _sha256(Path(__file__).resolve()),
            "test": str(TEST.resolve().relative_to(HERE.parents[1])),
            "test_sha256": _sha256(TEST),
        },
    }


def main() -> int:
    payload = build_payload()
    _write(OUTPUT, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
