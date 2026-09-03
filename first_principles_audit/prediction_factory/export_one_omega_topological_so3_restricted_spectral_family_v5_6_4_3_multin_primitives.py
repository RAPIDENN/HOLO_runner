#!/usr/bin/env python3
"""Export the common-first pointwise primitive family for N=1,2,3.

The frozen v5.6.4.2 exporter established the decoder contract at N=2.  This
additive exporter applies that same byte-pinned codec and pointwise decoder to
all three nested members already present in the frozen v5.6.4.1 bundle.  It
exports primitive configurations and tangents only: no action value, Eulerian,
decision boolean, or convergence conclusion is embedded.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
FROZEN_EXPORTER = HERE / (
    "export_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_2_pointwise_primitives.py"
)
FROZEN_EXPORTER_SHA256 = "4b7eda150cf2d22e04ef2b1b04391c31dc9e618839d7ead9e74a540371ab3d7f"
PARENT_BUNDLE_SHA256 = "e751d2b542f2246ca7f5aec5632ef0b114819694dd2dc347accb38411d8a0fbc"
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_3_multin_primitive_bundle.json"
)
TEST = HERE / (
    "test_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_3_multin_primitives.py"
)
SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-3-multin-primitive-bundle.v1"
)
N_VALUES = (1, 2, 3)
DEVELOPMENT_SEED = 20260902
CONTROL_SEED = 0


class MultiNPrimitiveError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()


def _contains_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, dict):
        return any(_contains_boolean(key) or _contains_boolean(item)
                   for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_boolean(item) for item in value)
    return False


def load_frozen_exporter() -> Any:
    observed = _sha256(FROZEN_EXPORTER)
    if observed != FROZEN_EXPORTER_SHA256:
        raise MultiNPrimitiveError(
            f"v5.6.4.2 exporter drift: {observed} != {FROZEN_EXPORTER_SHA256}"
        )
    name = "frozen_pointwise_exporter_v5642_for_multin"
    spec = importlib.util.spec_from_file_location(name, FROZEN_EXPORTER)
    if spec is None or spec.loader is None:
        raise MultiNPrimitiveError("cannot import frozen v5.6.4.2 exporter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _member_id(N: int, seed: int) -> str:
    return f"N{N}.K{N}.seed{seed}"


def _pointwise_contract(
    frozen: Any, parent: Mapping[str, Any], N: int, free_dimension: int
) -> Mapping[str, Any]:
    spectral = parent["spectral_contract"]
    return {
        "N": N,
        "K": N,
        "basis": spectral["basis_by_N"][str(N)],
        "free_layout": spectral["free_generator_layout_by_N"][str(N)],
        "tensor_component_order": spectral["tensor_component_order"],
        "radial_profiles": spectral["radial_profiles"],
        "radial_basis": spectral["radial_basis"],
        "primitive_component_convention": spectral["primitive_component_convention"],
        "frame_rotation_contract": spectral["frame_rotation_contract"],
        "embedding_pullback_orientation_contract": spectral[
            "embedding_pullback_orientation_contract"
        ],
        "free_coordinate_dimension": free_dimension,
        "decoder": {
            "formula_source": (
                "byte-pinned v5.6.4.2 common-first pointwise decoder; all eliminated "
                "lateral traces are reconstructed at evaluator-owned nodes"
            ),
            "gluing_map": (
                "Y* g=gamma; exp(logOmega)=OmegaSigma; R phi=varphi; "
                "R(Y*A)R^-1-dR R^-1=A_Sigma"
            ),
        },
        "geometry_convention": frozen._geometry_contract(),
    }


def _export_member(
    frozen: Any,
    parent: Mapping[str, Any],
    upstream: Any,
    N: int,
    seed: int,
    include_curves: bool,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    member_id = _member_id(N, seed)
    parent_member = frozen._parent_member(parent, member_id)
    free = np.asarray(upstream.build_free_coordinates(seed, N), dtype=float)
    ambient = frozen._decode_f64(parent_member["ambient_q_f64le"])
    inverse = np.asarray(upstream.ambient_to_free_coordinates(ambient, N), dtype=float)
    if not np.allclose(free, inverse, rtol=0.0, atol=2.0e-12):
        raise MultiNPrimitiveError(f"free inverse mismatch for {member_id}")
    reconstructed = np.asarray(upstream.construct_ambient_point(free, N), dtype=float)
    contract = _pointwise_contract(frozen, parent, N, int(free.size))
    record: dict[str, Any] = {
        "member_id": member_id,
        "role": (
            "development_multin_action_member"
            if seed == DEVELOPMENT_SEED
            else "R_equals_identity_control_only"
        ),
        "N": N,
        "K": N,
        "seed": seed,
        "parent_ambient_q_sha256": parent_member["ambient_q_f64le"]["sha256"],
        "authoritative_free_central_f64le": frozen._encode_f64(free),
        "codec_roundtrip": {
            "ambient_reconstruction_sha256": frozen._encode_f64(reconstructed)["sha256"],
            "ambient_reconstruction_Linf": float(np.max(np.abs(reconstructed - ambient))),
            "byte_relation": (
                "byte_identical"
                if reconstructed.tobytes() == ambient.tobytes()
                else "numeric_roundtrip"
            ),
        },
    }
    if include_curves:
        base_step = float(parent_member["stencil_contract"]["step"])
        record["curves"] = [
            frozen._curve_payload(item, ambient, free, N, base_step)
            for item in parent_member["horizontal_primitives"]
        ]
    return record, contract


def build_bundle() -> Mapping[str, Any]:
    frozen = load_frozen_exporter()
    parent = frozen._load_parent()
    if _sha256(REPO / frozen.PARENT_BUNDLE) != PARENT_BUNDLE_SHA256:
        raise MultiNPrimitiveError("parent v5.6.4.1 bundle drift")
    frozen._validate_gauss_corrigendum()
    upstream = frozen._upstream_module()

    primary_members: list[Mapping[str, Any]] = []
    controls: list[Mapping[str, Any]] = []
    contracts: dict[str, Mapping[str, Any]] = {}
    diagnostics: dict[str, Any] = {}
    for N in N_VALUES:
        primary, contract = _export_member(
            frozen, parent, upstream, N, DEVELOPMENT_SEED, True
        )
        control, control_contract = _export_member(
            frozen, parent, upstream, N, CONTROL_SEED, False
        )
        if contract != control_contract:
            raise MultiNPrimitiveError(f"seed-dependent pointwise contract at N={N}")
        primary_members.append(primary)
        controls.append(control)
        contracts[str(N)] = contract

        validation_rng = np.random.default_rng(564300 + N)
        validation_points = validation_rng.uniform(
            0.0, 2.0 * np.pi, size=(7, 4)
        )
        joint = next(
            curve
            for curve in primary["curves"]
            if curve["name"] == frozen.PRIMARY_CURVE
        )
        raw_inputs: list[tuple[str, Mapping[str, Any]]] = [
            ("central", primary["authoritative_free_central_f64le"])
        ]
        for family in joint["step_families"]:
            for multiplier in frozen.MULTIPLIERS:
                raw_inputs.append(
                    (
                        f'{family["label"]}:{multiplier:+d}',
                        family["free_endpoints_f64le"][str(multiplier)],
                    )
                )
        diagnostics[str(N)] = {
            "role": "reserved_off_collocation_pointwise_decoder_validation",
            "points_f64le": frozen._encode_f64(validation_points),
            "raw_pointwise_gluing_diagnostics": [
                frozen._raw_pointwise_diagnostic(
                    record_id, free_record, contract, validation_points
                )
                for record_id, free_record in raw_inputs
            ],
        }

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": (
            "primitive_pointwise_multin_family;N1_N2_N3;authoritative_free_curves;"
            "no_action_receipt;no_decision_booleans;no_continuous_promotion"
        ),
        "source_pins": {
            "frozen_v5_6_4_2_exporter": {
                "path": str(FROZEN_EXPORTER.relative_to(REPO)),
                "sha256": FROZEN_EXPORTER_SHA256,
            },
            "parent_v5_6_4_1_bundle": {
                "path": str(frozen.PARENT_BUNDLE),
                "sha256": PARENT_BUNDLE_SHA256,
            },
            "frozen_v5_6_4_generator": {
                "path": str(frozen.UPSTREAM_GENERATOR),
                "sha256": frozen.UPSTREAM_GENERATOR_SHA256,
            },
        },
        "action_contract": parent["action_contract"],
        "nested_truncations": {
            "N_values": list(N_VALUES),
            "K_of_N": "K=N",
            "basis_labels_by_N": {
                str(N): contracts[str(N)]["basis"]["labels"] for N in N_VALUES
            },
            "inclusion": "C_1 subset C_2 subset C_3 for the published constant/cosine/sine basis ordering",
        },
        "pointwise_decoder_contract_by_N": contracts,
        "primary_members": primary_members,
        "identity_controls": controls,
        "off_collocation_validation_by_N": diagnostics,
        "dependency_graph": {
            "nodes": [
                {"id": "v5_6_4_1", "kind": "frozen six-member primitive lineage"},
                {"id": "v5_6_4_2", "kind": "frozen common-first decoder implementation"},
                {"id": "v5_6_4_3", "kind": "primitive-only N1/N2/N3 export"},
            ],
            "edges": [
                {"from": "v5_6_4_1", "to": "v5_6_4_3", "carries": ["members", "tangents", "action_contract"]},
                {"from": "v5_6_4_2", "to": "v5_6_4_3", "carries": ["pointwise_decoder", "Gauss_corrigendum_pin"]},
            ],
        },
    }
    if _contains_boolean(result):
        raise MultiNPrimitiveError("primitive bundle must not contain decision booleans")
    result["payload_sha256"] = _canonical_sha256(result)
    return result


def render_bundle(bundle: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render_bundle(build_bundle()))
    print(OUTPUT)
    print(_sha256(OUTPUT))


if __name__ == "__main__":
    main()
