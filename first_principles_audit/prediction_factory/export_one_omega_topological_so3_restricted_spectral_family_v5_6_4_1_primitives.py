#!/usr/bin/env python3
"""Export the v5.6.4 finite-family primitives through a strict allowlist.

This module deliberately imports no prediction-factory generator or helper.  It
reads two frozen JSON artifacts and uses the v5.6.4 generator/test files only as
byte-pinned integrity inputs.  No gate result, Eulerian object, ledger, residual,
prediction, or decision boolean is copied into the public bundle.
"""

from __future__ import annotations

import base64
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO = Path(__file__).resolve().parents[2]
PREDICTION_FACTORY = Path("first_principles_audit/prediction_factory")
ARTIFACTS = PREDICTION_FACTORY / "artifacts"

V564_GENERATOR = PREDICTION_FACTORY / (
    "derive_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_certificate.py"
)
V564_TEST = PREDICTION_FACTORY / (
    "test_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_certificate.py"
)
V564_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_certificate.json"
)
V52_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_classical_v5_2_gate.json"
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_1_primitive_bundle.json"
)

SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-1-primitive-bundle.v1"
)
V564_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-certificate.v1"
)
V52_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"

PINNED_SHA256 = {
    "v5_6_4_generator": "198808b829a708ca9bc0314bfc5db235317f42eb48aa8f17ced6070cc3c87b7e",
    "v5_6_4_test": "24888a723e29af0d7b6f2df02d9739e676af72694280053b8b17a137eb8f5c82",
    "v5_6_4_artifact": "51d820b4652ca2fbf3039a6471ffbca5cdd29f57dc34f5f3006c2f68a5b4115e",
    "v5_2_artifact": "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
    "v5_2_exact_action": "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a",
}

SOURCE_PATHS = {
    "v5_6_4_generator": V564_GENERATOR,
    "v5_6_4_test": V564_TEST,
    "v5_6_4_artifact": V564_ARTIFACT,
    "v5_2_artifact": V52_ARTIFACT,
}

BASIS_FIELDS = (
    "labels",
    "mode_wavevectors",
    "collocation_points_T4",
    "value_matrix",
    "four_partial_derivative_matrices",
)
BULK_COMPONENT_FIELDS = (
    "g_MN",
    "Omega",
    "phi_a",
    "A_Ma",
    "B_MNP_a",
    "X0_channels",
    "free_boundary_jet_orders",
    "channels_per_boundary_jet",
    "C_bump_channels_per_radial_mode",
    "radial_bump_mode_count",
    "Omega_coordinate",
    "asymptotic_reference",
    "B_form_index_order",
    "B_X0_form_index_order",
)
BULK_FIELDS = ("g_MN", "Omega", "phi_a", "A_Ma", "B_MNP_a")
F64_RECORD_FIELDS = ("data", "dtype", "encoding", "sha256", "shape")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(relative_path: Path) -> str:
    return _sha256_bytes((REPO / relative_path).read_bytes())


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return _sha256_bytes(_canonical_bytes(value))


def _load_pinned_json(relative_path: Path, expected_sha256: str) -> Mapping[str, Any]:
    payload = (REPO / relative_path).read_bytes()
    observed = _sha256_bytes(payload)
    if observed != expected_sha256:
        raise RuntimeError(
            f"byte pin mismatch for {relative_path}: {observed} != {expected_sha256}"
        )
    decoded = json.loads(payload)
    if not isinstance(decoded, dict):
        raise TypeError(f"expected a JSON object in {relative_path}")
    return decoded


def _checked_source_pins() -> Mapping[str, Mapping[str, str]]:
    result: dict[str, Mapping[str, str]] = {}
    for name, relative_path in SOURCE_PATHS.items():
        observed = _sha256_file(relative_path)
        expected = PINNED_SHA256[name]
        if observed != expected:
            raise RuntimeError(
                f"byte pin mismatch for {relative_path}: {observed} != {expected}"
            )
        result[name] = {"path": relative_path.as_posix(), "sha256": observed}
    return result


def _product(shape: Sequence[int]) -> int:
    result = 1
    for item in shape:
        result *= int(item)
    return result


def _copy_f64_record(record: Mapping[str, Any]) -> Mapping[str, Any]:
    selected = {name: record[name] for name in F64_RECORD_FIELDS}
    if selected["dtype"] != "<f8" or selected["encoding"] != "base64":
        raise ValueError("compact primitive arrays must be base64 little-endian float64")
    raw = base64.b64decode(selected["data"], validate=True)
    if len(raw) != 8 * _product(selected["shape"]):
        raise ValueError("compact primitive array byte length does not match shape")
    if _sha256_bytes(raw) != selected["sha256"]:
        raise ValueError("compact primitive array SHA-256 mismatch")
    return selected


def _encode_f64_vector(values: Sequence[float], expected_sha256: str) -> Mapping[str, Any]:
    raw = struct.pack(f"<{len(values)}d", *(float(item) for item in values))
    observed = _sha256_bytes(raw)
    if observed != expected_sha256:
        raise ValueError(f"primitive vector SHA-256 mismatch: {observed} != {expected_sha256}")
    return {
        "data": base64.b64encode(raw).decode("ascii"),
        "dtype": "<f8",
        "encoding": "base64",
        "sha256": observed,
        "shape": [len(values)],
    }


def _copy_endpoint_map(endpoint_map: Mapping[str, Any]) -> Mapping[str, Any]:
    expected = {"-2", "-1", "1", "2"}
    if set(endpoint_map) != expected:
        raise ValueError("a five-point derivative stencil must expose endpoints -2,-1,1,2")
    return {key: _copy_f64_record(endpoint_map[key]) for key in ("-2", "-1", "1", "2")}


def _basis_contract(receipt: Mapping[str, Any]) -> Mapping[str, Any]:
    source = receipt["basis"]
    contract = {field: source[field] for field in BASIS_FIELDS}
    contract["canonical_sha256"] = _canonical_sha256(contract)
    return contract


def _layout_contract(source: Mapping[str, Any]) -> Mapping[str, Any]:
    contract = {
        name: {
            "shape": item["shape"],
            "start": item["start"],
            "stop": item["stop"],
        }
        for name, item in sorted(source.items())
    }
    return {"blocks": contract, "canonical_sha256": _canonical_sha256(contract)}


def _bulk_samples(receipt: Mapping[str, Any], radial_coordinates: Sequence[float]) -> Mapping[str, Any]:
    source = receipt["bulk_primitive_samples"]
    result: dict[str, Any] = {"radial_coordinates": list(radial_coordinates)}
    for side in ("plus", "minus"):
        item = source[side]
        component_contract = {
            field: item["component_contract"][field] for field in BULK_COMPONENT_FIELDS
        }
        values = {field: item["values"][field] for field in BULK_FIELDS}
        derivatives = {
            field: item["radial_derivatives"][field] for field in BULK_FIELDS
        }
        source_hashes = {
            f"values.{field}": item["sha256"][f"values.{field}"]
            for field in BULK_FIELDS
        }
        source_hashes.update(
            {
                f"radial_derivatives.{field}": item["sha256"][
                    f"radial_derivatives.{field}"
                ]
                for field in BULK_FIELDS
            }
        )
        side_payload = {
            "component_contract": component_contract,
            "values": values,
            "radial_derivatives": derivatives,
            "array_sha256": source_hashes,
        }
        side_payload["canonical_sha256"] = _canonical_sha256(side_payload)
        result[side] = side_payload
    result["canonical_sha256"] = _canonical_sha256(result)
    return result


def _horizontal_primitives(receipt: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    split = receipt["SO3_gauge_and_horizontal_split"]
    stencils = receipt["H_N_pointwise_generator_and_retracted_stencils"]
    endpoint_sources = stencils["selected_horizontal_stencils"]
    tangent_sources = {
        tangent["name"]: tangent
        for tangent in split["selected_SO3_horizontal_tangents"]
    }
    if set(tangent_sources) != set(endpoint_sources):
        raise ValueError("horizontal tangent and stencil names differ")
    result = []
    for name in sorted(tangent_sources):
        tangent = tangent_sources[name]
        endpoint_source = endpoint_sources[name]
        encoded_tangent = _encode_f64_vector(
            tangent["ambient_primitive_tangent"],
            tangent["ambient_primitive_tangent_sha256"],
        )
        if encoded_tangent["sha256"] != endpoint_source["ambient_primitive_tangent_sha256"]:
            raise ValueError(f"horizontal stencil tangent mismatch for {name}")
        result.append(
            {
                "name": name,
                "ambient_primitive_tangent_f64le": encoded_tangent,
                "stencil_endpoints_ambient_q_f64le": _copy_endpoint_map(
                    endpoint_source["stencil_endpoints_ambient_q_f64le"]
                ),
            }
        )
    return result


def _gauge_primitives(receipt: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    source = receipt["H_N_pointwise_generator_and_retracted_stencils"][
        "selected_gauge_representative_stencils"
    ]
    result = []
    for name, item in sorted(source.items()):
        result.append(
            {
                "name": name,
                "sector": item["sector"],
                "tangential_mode_index": item["tangential_mode_index"],
                "so3_component": item["so3_component"],
                "basis_label": item["basis_label"],
                "wavevector": item["wavevector"],
                "ambient_primitive_tangent_f64le": _copy_f64_record(
                    item["ambient_primitive_tangent_f64le"]
                ),
                "stencil_endpoints_ambient_q_f64le": _copy_endpoint_map(
                    item["stencil_endpoints_ambient_q_f64le"]
                ),
            }
        )
    return result


def _seed_role(seed: int, seeds: Mapping[str, Any]) -> str:
    if seed == seeds["identity_control"]:
        return "identity_control"
    if seed == seeds["development"]:
        return "development"
    raise ValueError(f"unpublished seed role for {seed}")


def _member(receipt: Mapping[str, Any], seeds: Mapping[str, Any]) -> Mapping[str, Any]:
    N = int(receipt["N"])
    K = N
    seed = int(receipt["seed"])
    source_stencils = receipt["H_N_pointwise_generator_and_retracted_stencils"]
    primitive = receipt["primitive_configuration"]
    radial_coordinates = receipt["kinematic_invariants"]["radial_coordinate_samples"]
    payload: dict[str, Any] = {
        "member_id": f"N{N}.K{K}.seed{seed}",
        "N": N,
        "K": K,
        "seed": seed,
        "seed_role": _seed_role(seed, seeds),
        "seed_sha256": _canonical_sha256(seed),
        "ambient_q_f64le": _encode_f64_vector(
            primitive["ambient_q"], primitive["ambient_q_sha256"]
        ),
        "bulk_primitive_samples": _bulk_samples(receipt, radial_coordinates),
        "stencil_contract": {
            "step": source_stencils["step"],
            "multipliers": source_stencils["stencil_multipliers"],
            "derivative_formula": "(q[-2]-8*q[-1]+8*q[1]-q[2])/(12*step)",
        },
        "horizontal_primitives": _horizontal_primitives(receipt),
        "gauge_primitives": _gauge_primitives(receipt),
    }
    for side in ("plus", "minus"):
        bump_count = payload["bulk_primitive_samples"][side]["component_contract"][
            "radial_bump_mode_count"
        ]
        if bump_count != K:
            raise ValueError(f"radial K mismatch for {payload['member_id']} {side}")
    payload["member_payload_sha256"] = _canonical_sha256(payload)
    return payload


def _dependency_graph() -> Mapping[str, Any]:
    routes = (
        ("route_A_literal_AD_JVP", "literal_action_autodiff"),
        ("route_B_independent_FD5", "separate_literal_action_high_order_finite_difference"),
        ("route_C_independent_Euler_Green", "independent_variation_and_green_reconstruction"),
        ("route_D_symbolic_local", "independent_symbolic_local_form"),
    )
    nodes = [
        {"id": "v5_2_literal_action_json", "kind": "frozen_JSON_source"},
        {"id": "v5_6_4_finite_family_json", "kind": "frozen_JSON_source"},
        {"id": "v5_6_4_source_byte_pins", "kind": "integrity_source"},
        {"id": "v5_6_4_1_allowlist_exporter", "kind": "stdlib_only_transform"},
        {"id": "v5_6_4_1_primitive_bundle", "kind": "immutable_route_input"},
    ]
    nodes.extend(
        {"id": route, "kind": "future_evaluator", "implementation_boundary": boundary}
        for route, boundary in routes
    )
    edges = [
        {
            "from": "v5_2_literal_action_json",
            "to": "v5_6_4_1_allowlist_exporter",
            "carries": ["exact_action"],
        },
        {
            "from": "v5_6_4_finite_family_json",
            "to": "v5_6_4_1_allowlist_exporter",
            "carries": [
                "basis_and_layout_contracts",
                "ambient_q",
                "bulk_primitive_samples",
                "horizontal_and_gauge_primitives",
                "constraint_preserving_stencil_endpoints",
                "N_K_seed_metadata",
            ],
        },
        {
            "from": "v5_6_4_source_byte_pins",
            "to": "v5_6_4_1_allowlist_exporter",
            "carries": ["generator_test_artifact_SHA256"],
        },
        {
            "from": "v5_6_4_1_allowlist_exporter",
            "to": "v5_6_4_1_primitive_bundle",
            "carries": ["allowlisted_primitive_payload"],
        },
    ]
    for route, _boundary in routes:
        edges.append(
            {
                "from": "v5_6_4_1_primitive_bundle",
                "to": route,
                "carries": ["only_public_input_contract"],
            }
        )
    return {
        "nodes": nodes,
        "edges": edges,
        "route_separation": (
            "No evaluator-to-evaluator edge exists. Each route must parse this bundle "
            "directly and own every action, variation, quadrature, and differentiation formula "
            "that it purports to evaluate."
        ),
        "excluded_payload_categories": [
            "gate decisions and check booleans",
            "Eulerian and Green objects produced upstream",
            "ledgers and predictions",
            "residuals, tolerances, and primary-gate outcomes",
            "Python helpers from any upstream generator",
        ],
    }


def build_bundle() -> Mapping[str, Any]:
    source_pins = _checked_source_pins()
    v564 = _load_pinned_json(V564_ARTIFACT, PINNED_SHA256["v5_6_4_artifact"])
    v52 = _load_pinned_json(V52_ARTIFACT, PINNED_SHA256["v5_2_artifact"])
    if v564.get("schema") != V564_SCHEMA:
        raise ValueError("unexpected v5.6.4 schema")
    if v52.get("schema") != V52_SCHEMA:
        raise ValueError("unexpected v5.2 schema")

    exact_action = v52["exact_classical_charter"]["exact_action"]
    action_sha256 = _canonical_sha256(exact_action)
    if action_sha256 != PINNED_SHA256["v5_2_exact_action"]:
        raise ValueError("literal v5.2 exact_action SHA-256 mismatch")
    charter = v52["exact_classical_charter"]
    coefficient_parameters = charter["coefficient_policy"]["parameters"]
    topology_orientation = {
        "bulk_halves": charter["topology"]["bulk_halves"],
        "interface": charter["topology"]["interface"],
        "reference_domain_formulation": charter["topology"][
            "reference_domain_formulation"
        ],
        "natural_B_flux_equation": charter["interface_domain"][
            "natural_B_flux_equation"
        ],
    }

    scientific = v564["scientific"]
    receipts = scientific["configuration_and_tangent_receipts"]
    truncations = [int(item) for item in scientific["truncations"]]
    receipt_by_N: dict[int, Mapping[str, Any]] = {}
    for receipt in receipts:
        N = int(receipt["N"])
        basis = _basis_contract(receipt)
        previous = receipt_by_N.get(N)
        if previous is None:
            receipt_by_N[N] = basis
        elif previous != basis:
            raise ValueError(f"basis contract depends on seed at N={N}")

    basis_by_N = {str(N): receipt_by_N[N] for N in truncations}
    ambient_layout_by_N = {
        str(N): _layout_contract(scientific["ambient_layout_by_N"][str(N)])
        for N in truncations
    }
    free_layout_by_N = {
        str(N): _layout_contract(scientific["free_layout_by_N"][str(N)])
        for N in truncations
    }
    tensor_order = {
        "symmetric4_pairs": [[i, j] for i in range(4) for j in range(i, 4)],
        "symmetric5_pairs": [[i, j] for i in range(5) for j in range(i, 5)],
        "antisymmetric_B_triples_5D": [
            [i, j, k]
            for i in range(5)
            for j in range(i + 1, 5)
            for k in range(j + 1, 5)
        ],
    }
    math_contract = scientific["mathematical_contract"]
    primitive_component_convention = {
        "epsilon_orientation": "epsilon_123=+1",
        "hat_map": "hat(v) w = v cross w",
        "literal_v5_2_matrix_basis": (
            "(T_I)^J_K=epsilon_IJK, hence T_I=-tau_I when "
            "tau_I=hat(e_I)"
        ),
        "primitive_storage_basis": "tau_I=hat(e_I)",
        "same_matrix_component_conversion": [
            "A_tau=-A_T",
            "B_tau=-B_T",
            "lambda_tau=-lambda_T",
        ],
        "tau_covariant_derivative": "D_M phi = partial_M phi + A_M_tau cross phi",
        "tau_curvature": (
            "F_MN_tau=partial_M A_N_tau-partial_N A_M_tau+"
            "A_M_tau cross A_N_tau"
        ),
        "tau_infinitesimal_gauge_action": [
            "delta_lambda A_tau=-(d lambda_tau+A_tau cross lambda_tau)",
            "delta_lambda phi=lambda_tau cross phi",
        ],
        "tau_finite_gauge_action": [
            "U=exp(hat(lambda_tau))",
            "hat(A_tau)'=U hat(A_tau) U^T-dU U^T",
            "phi'=U phi",
        ],
        "BF_component_pairing": (
            "The simultaneous A_tau/B_tau sign conversion preserves the literal "
            "v5.2 inner product <B,F>=-tr_3(BF)/2"
        ),
        "B_ordered_exterior_basis": (
            "The 10 stored B_MNP components multiply the ordered basis "
            "dy^M wedge dy^N wedge dy^P with M<N<P"
        ),
        "F_ordered_exterior_basis": (
            "F_MN multiplies the ordered basis dy^M wedge dy^N with M<N"
        ),
        "B_wedge_F_top_coefficient": (
            "sum over each stored B triple and its ordered complementary F pair "
            "of permutation_sign(triple,pair)*dot_tau(B_triple,F_pair), with no "
            "additional factorial"
        ),
        "tau_internal_pairing": "dot_tau(X,Y)=-tr_3(XY)/2",
        "required_exterior_normalization_mutants": [
            "insert the erroneous factor 1/(3!*2!)",
            "remove or invert the complementary-pair permutation sign",
        ],
    }
    frame_rotation_contract = {
        "published_frame": math_contract["frame"],
        "published_relative_rotation": math_contract["rotation"],
        "khronon_coordinate": "tau_T(x)=x0+T(x)",
        "horizontal_frame_seed": (
            "E0 is the ordered gamma-Gram-Schmidt orthonormalization of the three "
            "coordinate spatial vectors projected orthogonally to "
            "u_mu=-N_T partial_mu tau_T"
        ),
        "Q_frame_decoder": "E_Q=E0 exp(-hat(q_Q))",
        "relative_source_to_Q_decoder": "R_epsilon=exp(hat(r_epsilon))",
        "boundary_groupoid_action_tau": [
            "phi_Q=R_epsilon phi_source",
            "hat(A_Q)=R_epsilon hat(A_source) R_epsilon^T-dR_epsilon R_epsilon^T",
        ],
    }
    embedding_pullback_orientation_contract = {
        "ambient_coordinates": "y^M=(x0,x1,x2,x3,y4)",
        "interface_embeddings": "Y_epsilon(x)=(x0,x1,x2,x3,Y_epsilon(x))",
        "collar_coordinates": "z^A=(x0,x1,x2,x3,rho_epsilon)",
        "collar_definitions": {
            "plus": "rho_plus=Y_plus(x)-y4>=0",
            "minus": "rho_minus=y4-Y_minus(x)>=0",
        },
        "collar_maps": {
            "plus": "y4=Y_plus(x)-rho_plus; s_plus=partial y4/partial rho_plus=-1",
            "minus": "y4=Y_minus(x)+rho_minus; s_minus=partial y4/partial rho_minus=+1",
        },
        "collar_jacobian": [
            "J^M_mu=delta^M_mu+delta^M_4 partial_mu Y_epsilon",
            "J^M_rho=delta^M_4 s_epsilon",
        ],
        "tensor_pullbacks": [
            "g_bar_AB=J^M_A J^N_B g_MN",
            "A_bar_A=J^M_A A_M",
            "B_bar_ABC=J^M_A J^N_B J^P_C B_MNP",
            "Y_epsilon^*g_mu_nu=g_mu_nu+g_mu4 Y_nu+g_4nu Y_mu+g_44 Y_mu Y_nu",
            "Y_epsilon^*A_mu=A_mu+Y_mu A_4",
        ],
        "outward_normal_covector": {
            "raw": "m_M=(-partial_mu Y_epsilon,+1)",
            "plus": "+m/sqrt(g^MN m_M m_N)",
            "minus": "-m/sqrt(g^MN m_M m_N)",
        },
        "orientation": [
            "Each ordered reference collar chart (x0,x1,x2,x3,rho_epsilon) is positive",
            "All tensor and differential-form integrands are pulled back with the full collar Jacobian",
            "The coefficient of pulled-back B wedge F is integrated in that positive chart orientation",
            "The boundary orientation is the contraction i_(n_out) vol_5",
            "det[tangent_0,...,tangent_3,n_out] has sign +1 on plus and -1 on minus",
        ],
        "oriented_interface_BF_flux_signs": {"plus": 1, "minus": -1},
        "reference_domain_formulation": charter["topology"][
            "reference_domain_formulation"
        ],
    }
    spectral_contract = {
        "truncation_pairs": [{"N": N, "K": N} for N in truncations],
        "K_rule": "K(N)=N",
        "real_tangential_basis": math_contract["spectral_space"],
        "radial_profiles": math_contract["radial_profiles"],
        "radial_basis": math_contract["radial_truncation"],
        "bulk_decoder_contract": math_contract["bulk_primitive_decoder"],
        "tensor_component_order": tensor_order,
        "primitive_component_convention": primitive_component_convention,
        "frame_rotation_contract": frame_rotation_contract,
        "embedding_pullback_orientation_contract": (
            embedding_pullback_orientation_contract
        ),
        "basis_by_N": basis_by_N,
        "ambient_layout_by_N": ambient_layout_by_N,
        "free_generator_layout_by_N": free_layout_by_N,
    }
    spectral_contract["canonical_sha256"] = _canonical_sha256(spectral_contract)

    seeds = scientific["seeds"]
    seed_roles = [
        {
            "role": "identity_control",
            "seed": int(seeds["identity_control"]),
            "seed_sha256": _canonical_sha256(int(seeds["identity_control"])),
        },
        {
            "role": "development",
            "seed": int(seeds["development"]),
            "seed_sha256": _canonical_sha256(int(seeds["development"])),
        },
    ]
    reserved_domains = [
        {
            "role": "reserved_holdout_domain_unrevealed",
            "domain": domain,
            "domain_sha256": _sha256_bytes(domain.encode("utf-8")),
        }
        for domain in seeds["reserved_seed_domains"]
    ]
    seed_contract = {
        "seed_hash_canonicalization": "SHA256(canonical JSON integer)",
        "roles": seed_roles,
        "reserved_domains": reserved_domains,
    }
    seed_contract["canonical_sha256"] = _canonical_sha256(seed_contract)

    members = [_member(receipt, seeds) for receipt in receipts]
    bundle: dict[str, Any] = {
        "schema": SCHEMA,
        "source_pins": source_pins,
        "action_contract": {
            "exact_action": exact_action,
            "exact_action_sha256": action_sha256,
            "exact_action_source_json_path": "exact_classical_charter.exact_action",
            "canonical_byte_length": len(_canonical_bytes(exact_action)),
            "canonicalization": (
                "json.dumps(sort_keys=True,separators=(',',':'),"
                "ensure_ascii=False,allow_nan=False).encode('utf-8')"
            ),
            "coefficient_parameters": coefficient_parameters,
            "coefficient_parameters_sha256": _canonical_sha256(coefficient_parameters),
            "coefficient_parameters_canonical_byte_length": len(
                _canonical_bytes(coefficient_parameters)
            ),
            "coefficient_parameters_source_json_path": (
                "exact_classical_charter.coefficient_policy.parameters"
            ),
            "topology_orientation": topology_orientation,
            "topology_orientation_sha256": _canonical_sha256(topology_orientation),
            "topology_orientation_source_json_paths": [
                "exact_classical_charter.topology.bulk_halves",
                "exact_classical_charter.topology.interface",
                "exact_classical_charter.topology.reference_domain_formulation",
                "exact_classical_charter.interface_domain.natural_B_flux_equation",
            ],
            "compact_relative_action_contract": {
                "object_name": "S_rel_v5_2_on_finite_C_N_member",
                "bulk_domain": {
                    "tangential": "T4=[0,2*pi)^4",
                    "tangential_measure": (
                        "unnormalized dx0 dx1 dx2 dx3 with total constant-mode weight "
                        "(2*pi)^4"
                    ),
                    "radial": "rho_epsilon in [0,1] on each collar",
                },
                "asymptotic_reference": (
                    "X_infinity=diag(-1.64,1.17,1.31,1.46,1.17), Omega=1, "
                    "phi=A=B=0"
                ),
                "compact_support_contract": (
                    "Every generated perturbation equals X_infinity for rho>=1; "
                    "the h0, h1 and b_j profiles are flat at rho=1, so compact "
                    "variations generate no artificial outer-boundary term"
                ),
                "bulk_definition": (
                    "For each of the twelve named bulk components integrate over its "
                    "own oriented collar L_i[X]-L_i[X_infinity] before summing"
                ),
                "interface_definition": (
                    "GHY and the six interface components are not reference-subtracted; "
                    "a route may remove only an explicitly recorded configuration-independent "
                    "constant, which cancels from every directional derivative"
                ),
                "variational_equivalence": (
                    "DS_rel equals the first variation of the literal v5.2 action for "
                    "the published compactly supported variations"
                ),
                "quadrature_independence": [
                    "Evaluate Fourier coefficients from the published wavevectors and labels",
                    "Do not use the N unisolvent collocation points as nonlinear quadrature nodes",
                    "Each independent route owns its tangential and radial quadrature implementation",
                    "Each route records nodes, weights, orders and simultaneous refinement data",
                ],
                "FD5_centering": (
                    "Evaluate S_rel at every retracted endpoint, subtract the central S_rel "
                    "component before forming the FD5 numerator, and record the central scale, "
                    "centered-term scale and cancellation ratio"
                ),
                "excluded_interpretations": [
                    "absolute action on the noncompact half-spaces",
                    "holographic counterterm or unlisted background counterterm",
                    "continuous C1/N1 theorem",
                ],
            },
        },
        "spectral_contract": spectral_contract,
        "seed_contract": seed_contract,
        "primitive_members": members,
        "dependency_graph": _dependency_graph(),
    }
    bundle["payload_sha256"] = _canonical_sha256(bundle)
    return bundle


def render_bundle(bundle: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def main() -> None:
    target = REPO / OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(render_bundle(build_bundle()))
    print(OUTPUT.as_posix())
    print(_sha256_file(OUTPUT))


if __name__ == "__main__":
    main()
