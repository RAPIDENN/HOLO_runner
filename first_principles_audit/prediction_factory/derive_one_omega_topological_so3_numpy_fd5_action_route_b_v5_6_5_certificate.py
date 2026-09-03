#!/usr/bin/env python3
"""Independent NumPy/FD5 evaluation route for the literal v5.2 action.

The only configuration input is the byte-pinned v5.6.4.2 primitive bundle.  This
file owns its Fourier/radial decoder, tensor calculus, action density, numerical
quadrature, and five-point directional derivative.  It imports no other project
module, consumes no upstream numerical result or tolerance, and validates the
mandatory false v5.5.4 quarantine record embedded in that sole input bundle.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


REPO = Path(__file__).resolve().parents[2]
PREDICTION_FACTORY = Path("first_principles_audit/prediction_factory")
ARTIFACTS = PREDICTION_FACTORY / "artifacts"
BUNDLE = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_2_pointwise_primitive_bundle.json"
)
BUNDLE_SHA256 = "bcbb0037a2b025d9ece7387b5962a910e31eced7294ccb5324ab764c3bc7cb26"
BUNDLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-2-pointwise-primitive-bundle.v1"
)
LITERAL_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
GAUSS_CORRIGENDUM_ARTIFACT_SHA256 = (
    "7c2c3e46ea73b312f753d944e43cd2a2e224d000e5ddd3c3e15ff816e76e441a"
)
SCHEMA = "holo.one-omega-topological-so3-numpy-fd5-action-route-b-v5-6-5.v1"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.json"
TEST = PREDICTION_FACTORY / "test_one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.py"

SIDES = ("plus", "minus")
SYMMETRIC4 = tuple((i, j) for i in range(4) for j in range(i, 4))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))
B_TRIPLES = tuple(
    (i, j, k)
    for i in range(5)
    for j in range(i + 1, 5)
    for k in range(j + 1, 5)
)
REFERENCE_METRIC = np.diag((-1.64, 1.17, 1.31, 1.46, 1.17))
TAU_VOLUME = (2.0 * math.pi) ** 4

ACTION_COMPONENTS = (
    "EH_bulk_plus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "GHY_minus",
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)

PREPARED_MUTANTS = (
    {
        "id": "BF_insert_erroneous_inverse_factorial",
        "target": "BF_bulk_plus and BF_bulk_minus exterior normalization",
        "intervention": "multiply the ordered-basis B wedge F coefficient by 1/(3!*2!)",
    },
    {
        "id": "BF_invert_complement_permutation_sign",
        "target": "BF_bulk_plus and BF_bulk_minus exterior orientation",
        "intervention": "invert every complementary triple/pair permutation sign",
    },
    {
        "id": "BF_invert_collar_jacobian_sign",
        "target": "BF_bulk_plus and BF_bulk_minus collar pullback",
        "intervention": "replace s_epsilon by -s_epsilon",
    },
    {
        "id": "freeze_relative_R",
        "target": "primitive endpoint configurations",
        "intervention": "replace each endpoint side.r_E0 free block by its central value before reevaluation",
    },
    {
        "id": "rotate_phi_only",
        "target": "primitive endpoint configurations",
        "intervention": "apply the selected SO3 rotation to phi but not A or B before reevaluation",
    },
    {
        "id": "break_Robin",
        "target": "Robin interface component",
        "intervention": "remove the acceleration contribution from varphi_H-y*a",
    },
    {
        "id": "break_gluing",
        "target": "one decoded endpoint after common-first reconstruction",
        "intervention": "explicitly bypass the free decoder and perturb one lateral trace without the matching common trace",
    },
    {
        "id": "impose_Z2",
        "target": "independent plus/minus primitive data",
        "intervention": "replace minus data by the reflected plus data before reevaluation",
    },
)

# Fixed before the scientific receipt is emitted.  It spans the truncation
# regime and the float64 roundoff floor; the much smaller endpoint family in
# the primitive bundle is preserved separately as an archived stress case.
FD5_REFINEMENT_STEPS = (4.0e-2, 2.0e-2, 1.0e-2, 5.0e-3, 2.5e-3)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def _contains_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, dict):
        return any(_contains_boolean(key) or _contains_boolean(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_boolean(item) for item in value)
    return False


def load_primitive_bundle() -> Mapping[str, Any]:
    raw = (REPO / BUNDLE).read_bytes()
    observed = _sha256_bytes(raw)
    if observed != BUNDLE_SHA256:
        raise RuntimeError(f"primitive bundle byte pin mismatch: {observed} != {BUNDLE_SHA256}")
    bundle = json.loads(raw)
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise ValueError("unexpected primitive bundle schema")
    if _contains_boolean(bundle):
        raise ValueError("route B rejects primitive bundles containing boolean payloads")
    action = bundle["action_contract"]
    if action["exact_action_sha256"] != LITERAL_ACTION_SHA256:
        raise ValueError("unexpected literal v5.2 action digest")
    if _canonical_sha256(action["exact_action"]) != LITERAL_ACTION_SHA256:
        raise ValueError("literal v5.2 action canonical bytes do not match their digest")
    pointwise = bundle["pointwise_decoder_contract"]
    convention = pointwise["primitive_component_convention"]
    if convention["primitive_storage_basis"] != "tau_I=hat(e_I)":
        raise ValueError("route B requires the published tau-component primitive basis")
    expected_conversion = ["A_tau=-A_T", "B_tau=-B_T", "lambda_tau=-lambda_T"]
    if convention["same_matrix_component_conversion"] != expected_conversion:
        raise ValueError("route B requires the explicit literal-T to primitive-tau conversion")
    if "no additional factorial" not in convention["B_wedge_F_top_coefficient"]:
        raise ValueError("route B requires the published ordered exterior-form normalization")
    geometry = pointwise["embedding_pullback_orientation_contract"]
    if geometry["oriented_interface_BF_flux_signs"] != {"plus": 1, "minus": -1}:
        raise ValueError("route B requires the published two-sided BF orientation")
    relative = bundle["toroidal_relative_scope"]
    if relative["object_name"] != "S_rel_v5_2_on_finite_C_N_member":
        raise ValueError("route B evaluates only the published compact relative action")
    if relative["bulk_domain"]["tangential"] != "T4=[0,2*pi)^4":
        raise ValueError("route B requires the published unnormalized T4 domain")
    order = pointwise["tensor_component_order"]
    if tuple(map(tuple, order["symmetric4_pairs"])) != SYMMETRIC4:
        raise ValueError("route B symmetric4 component order mismatch")
    if tuple(map(tuple, order["symmetric5_pairs"])) != SYMMETRIC5:
        raise ValueError("route B symmetric5 component order mismatch")
    if tuple(map(tuple, order["antisymmetric_B_triples_5D"])) != B_TRIPLES:
        raise ValueError("route B B-triple component order mismatch")
    _validate_gauss_corrigendum(bundle)
    return bundle


def _validate_gauss_corrigendum(bundle: Mapping[str, Any]) -> None:
    pin = bundle["source_pins"]["mandatory_v5_5_4_Gauss_sign_corrigendum"]
    if (
        pin["required_decision_path"]
        != "decision.v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma"
        or pin["required_value_literal"] != "false"
    ):
        raise ValueError("primitive bundle does not embed the mandatory v5.5.4 quarantine")
    if pin["artifact_sha256"] != GAUSS_CORRIGENDUM_ARTIFACT_SHA256:
        raise ValueError("unexpected embedded Gauss corrigendum artifact pin")
    required_formula = (
        "equivalently Rcal=R4+2*Ric4_mu_nu*u^mu*u^nu-Kcal^2+"
        "Kcal_mu_nu*Kcal^mu_nu"
    )
    if required_formula not in bundle["geometry_convention"]["foliation"]:
        raise ValueError("pointwise bundle does not bind the corrected Gauss formula")


def _decode_f64(record: Mapping[str, Any]) -> np.ndarray:
    if record["dtype"] != "<f8" or record["encoding"] != "base64":
        raise ValueError("primitive array is not encoded as base64 little-endian float64")
    raw = base64.b64decode(record["data"], validate=True)
    if _sha256_bytes(raw) != record["sha256"]:
        raise ValueError("primitive array digest mismatch")
    result = np.frombuffer(raw, dtype="<f8").copy()
    shape = tuple(int(item) for item in record["shape"])
    if result.size != math.prod(shape):
        raise ValueError("primitive array shape mismatch")
    return result.reshape(shape)


def _member(bundle: Mapping[str, Any], member_id: str) -> Mapping[str, Any]:
    if bundle["primary_member"]["member_id"] == member_id:
        selected = bundle["primary_member"]
    elif bundle["identity_control"]["member_id"] == member_id:
        selected = bundle["identity_control"]
    else:
        raise ValueError(f"unpublished pointwise member: {member_id}")
    if int(selected["K"]) != int(selected["N"]):
        raise ValueError("route B requires the published diagonal K(N)=N")
    pointwise = bundle["pointwise_decoder_contract"]
    if int(selected["N"]) != int(pointwise["N"]):
        raise ValueError("member N does not match pointwise decoder contract")
    if int(selected["K"]) != int(pointwise["K"]):
        raise ValueError("member K does not match pointwise decoder contract")
    dimension = int(pointwise["free_coordinate_dimension"])
    central = _decode_f64(selected["authoritative_free_central_f64le"])
    if central.shape != (dimension,):
        raise ValueError("member central free-coordinate dimension mismatch")
    blocks = sorted(
        pointwise["free_layout"]["blocks"].values(),
        key=lambda block: int(block["start"]),
    )
    cursor = 0
    for block in blocks:
        start = int(block["start"])
        stop = int(block["stop"])
        if start != cursor or stop - start != math.prod(block["shape"]):
            raise ValueError("free-coordinate layout is not contiguous and exact")
        cursor = stop
    if cursor != dimension:
        raise ValueError("free-coordinate layout does not cover the declared dimension")
    _free_curve_affine_residuals(selected, dimension)
    return selected


def _free_curve_affine_residuals(
    member: Mapping[str, Any],
    dimension: int,
) -> Mapping[str, Mapping[str, Mapping[str, float]]]:
    central = _decode_f64(member["authoritative_free_central_f64le"])
    result: dict[str, dict[str, dict[str, float]]] = {}
    curves = member.get("curves", [])
    if len({curve["name"] for curve in curves}) != len(curves):
        raise ValueError("duplicate free-curve name")
    for curve in curves:
        tangent = _decode_f64(curve["authoritative_free_tangent_f64le"])
        if tangent.shape != (dimension,):
            raise ValueError("free tangent dimension mismatch")
        curve_records: dict[str, dict[str, float]] = {}
        for family in curve["step_families"]:
            step = float(family["step"])
            if step <= 0.0 or family["multipliers"] != [-2, -1, 1, 2]:
                raise ValueError("invalid affine FD5 step family")
            for multiplier in (-2, -1, 1, 2):
                endpoint = _decode_f64(
                    family["free_endpoints_f64le"][str(multiplier)]
                )
                if endpoint.shape != (dimension,):
                    raise ValueError("free endpoint dimension mismatch")
                expected = central + multiplier * step * tangent
                residual = float(np.max(np.abs(endpoint - expected)))
                scale = max(1.0, float(np.max(np.abs(expected))))
                roundoff_bound = 256.0 * np.finfo(float).eps * scale
                if residual > roundoff_bound:
                    raise ValueError(
                        f"endpoint leaves affine free curve: {curve['name']} "
                        f"{family['label']} multiplier={multiplier}"
                    )
                curve_records[f"{family['label']}:{multiplier:+d}"] = {
                    "Linf": residual,
                    "roundoff_bound": roundoff_bound,
                }
        result[curve["name"]] = curve_records
    return result


def _layout_get(q: np.ndarray, layout: Mapping[str, Any], name: str) -> np.ndarray:
    block = layout[name]
    return q[int(block["start"]):int(block["stop"])].reshape(tuple(block["shape"]))


def _permutation_sign(sequence: Sequence[int]) -> int:
    inversions = sum(
        int(sequence[i] > sequence[j])
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _sym_to_matrix(vector: np.ndarray, dimension: int) -> np.ndarray:
    pairs = SYMMETRIC4 if dimension == 4 else SYMMETRIC5
    result = np.zeros(vector.shape[:-1] + (dimension, dimension), dtype=float)
    for position, (i, j) in enumerate(pairs):
        result[..., i, j] = vector[..., position]
        result[..., j, i] = vector[..., position]
    return result


def _matrix_to_sym(matrix: np.ndarray, dimension: int) -> np.ndarray:
    pairs = SYMMETRIC4 if dimension == 4 else SYMMETRIC5
    return np.stack([matrix[..., i, j] for i, j in pairs], axis=-1)


def _lorentzian_inertia(
    metric: np.ndarray,
    expected_negative: int,
    expected_positive: int,
    location: str,
) -> Mapping[str, float | int]:
    """Require a nondegenerate Lorentzian inertia and expose its spectral margin."""

    symmetric = 0.5 * (metric + metric.T)
    eigenvalues = np.linalg.eigvalsh(symmetric)
    scale = max(1.0, float(np.max(np.abs(eigenvalues))))
    zero_threshold = 64.0 * np.finfo(float).eps * scale
    negative = eigenvalues[eigenvalues < -zero_threshold]
    positive = eigenvalues[eigenvalues > zero_threshold]
    zero_count = int(eigenvalues.size - negative.size - positive.size)
    if (
        negative.size != expected_negative
        or positive.size != expected_positive
        or zero_count != 0
    ):
        raise ValueError(
            f"wrong Lorentzian inertia at {location}: "
            f"negative={negative.size}, positive={positive.size}, zero={zero_count}, "
            f"eigenvalues={eigenvalues.tolist()}"
        )
    margin = float(np.min(np.abs(eigenvalues)))
    return {
        "negative_count": int(negative.size),
        "positive_count": int(positive.size),
        "zero_count": zero_count,
        "minimum_negative_magnitude": float(np.min(-negative)),
        "minimum_positive_eigenvalue": float(np.min(positive)),
        "spectral_margin_absolute": margin,
        "spectral_margin_relative": margin / scale,
    }


def _record_lorentzian_inertia(
    records: dict[str, list[Mapping[str, float | int]]] | None,
    sector: str,
    metric: np.ndarray,
    expected_negative: int,
    expected_positive: int,
    location: str,
) -> None:
    result = _lorentzian_inertia(
        metric, expected_negative, expected_positive, location
    )
    if records is not None:
        records.setdefault(sector, []).append(result)


def _summarize_lorentzian_inertia(
    records: Mapping[str, Sequence[Mapping[str, float | int]]],
) -> Mapping[str, Any]:
    return {
        sector: {
            "node_count": len(items),
            "negative_count_at_each_node": int(items[0]["negative_count"]),
            "positive_count_at_each_node": int(items[0]["positive_count"]),
            "zero_count_at_each_node": int(items[0]["zero_count"]),
            "minimum_negative_magnitude": min(
                float(item["minimum_negative_magnitude"]) for item in items
            ),
            "minimum_positive_eigenvalue": min(
                float(item["minimum_positive_eigenvalue"]) for item in items
            ),
            "minimum_spectral_margin_absolute": min(
                float(item["spectral_margin_absolute"]) for item in items
            ),
            "minimum_spectral_margin_relative": min(
                float(item["spectral_margin_relative"]) for item in items
            ),
        }
        for sector, items in records.items()
        if items
    }


def _hat(vector: np.ndarray) -> np.ndarray:
    x, y, z = vector
    return np.array(((0.0, -z, y), (z, 0.0, -x), (-y, x, 0.0)), dtype=float)


def _so3_exp(rotation_vector: np.ndarray) -> np.ndarray:
    angle = float(np.linalg.norm(rotation_vector))
    generator = _hat(rotation_vector)
    if angle < 1.0e-10:
        return np.eye(3) + generator + 0.5 * (generator @ generator)
    return (
        np.eye(3)
        + math.sin(angle) / angle * generator
        + (1.0 - math.cos(angle)) / (angle * angle) * (generator @ generator)
    )


def tangential_quadrature(points_per_axis: int) -> Mapping[str, Any]:
    if points_per_axis < 1:
        raise ValueError("tangential points per axis must be positive")
    axis = 2.0 * math.pi * np.arange(points_per_axis, dtype=float) / points_per_axis
    points = np.asarray(list(itertools.product(axis, repeat=4)), dtype=float)
    weights = np.full(points.shape[0], TAU_VOLUME / points.shape[0], dtype=float)
    return {"points": points, "weights": weights}


def _pseudospectral_role(points_per_axis: int, numerical_role: str) -> str:
    if points_per_axis == 3:
        if numerical_role != "smoke":
            raise ValueError("Q=3 is admitted only as an explicitly aliased smoke")
        return "aliased_smoke_only"
    if points_per_axis < 5 or points_per_axis % 2 == 0:
        raise ValueError(
            "N=2 nonlinear pseudospectral decoding requires an odd periodic grid "
            "with at least five nodes per axis; it remains a Q-refined projection"
        )
    return "odd_Q_refinable_projection"


def radial_quadrature(order: int) -> Mapping[str, Any]:
    if order < 2:
        raise ValueError("radial Gauss order must be at least two")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return {"points": 0.5 * (nodes + 1.0), "weights": 0.5 * weights}


def fourier_tables(basis: Mapping[str, Any], points: np.ndarray) -> Mapping[str, np.ndarray]:
    labels = basis["labels"]
    wavevectors = np.asarray(basis["mode_wavevectors"], dtype=float)
    P = points.shape[0]
    N = len(labels)
    values = np.empty((P, N), dtype=float)
    first = np.empty((P, 4, N), dtype=float)
    second = np.empty((P, 4, 4, N), dtype=float)
    for mode, label in enumerate(labels):
        k = wavevectors[mode]
        phase = points @ k
        if label == "1":
            values[:, mode] = 1.0
            first[:, :, mode] = 0.0
            second[:, :, :, mode] = 0.0
        elif label.startswith("cos("):
            cosine = np.cos(phase)
            sine = np.sin(phase)
            values[:, mode] = cosine
            first[:, :, mode] = -sine[:, None] * k[None, :]
            second[:, :, :, mode] = -cosine[:, None, None] * np.outer(k, k)[None, :, :]
        elif label.startswith("sin("):
            cosine = np.cos(phase)
            sine = np.sin(phase)
            values[:, mode] = sine
            first[:, :, mode] = cosine[:, None] * k[None, :]
            second[:, :, :, mode] = -sine[:, None, None] * np.outer(k, k)[None, :, :]
        else:
            raise ValueError(f"unsupported real Fourier label: {label}")
    return {"values": values, "first": first, "second": second}


def _spectral(coefficients: np.ndarray, tables: Mapping[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    value = np.tensordot(tables["values"], coefficients, axes=([1], [0]))
    first = np.tensordot(tables["first"], coefficients, axes=([2], [0]))
    second = np.tensordot(tables["second"], coefficients, axes=([3], [0]))
    return value, first, second


def _left_jacobian(rotation_vector: np.ndarray) -> np.ndarray:
    angle = float(np.linalg.norm(rotation_vector))
    generator = _hat(rotation_vector)
    if angle < 1.0e-8:
        return np.eye(3) + 0.5 * generator + (generator @ generator) / 6.0
    return (
        np.eye(3)
        + (1.0 - math.cos(angle)) / (angle * angle) * generator
        + (angle - math.sin(angle)) / (angle ** 3) * (generator @ generator)
    )


def _rotation_and_spatial_derivative(
    coefficients: np.ndarray,
    tables: Mapping[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    value, first, _second = _spectral(coefficients, tables)
    rotations = np.empty((value.shape[0], 3, 3), dtype=float)
    spatial_angular_velocity = np.empty((value.shape[0], 4, 3), dtype=float)
    for point in range(value.shape[0]):
        rotations[point] = _so3_exp(value[point])
        jacobian = _left_jacobian(value[point])
        for mu in range(4):
            spatial_angular_velocity[point, mu] = jacobian @ first[point, mu]
    return rotations, spatial_angular_velocity


def decode_pointwise_free_boundary(
    free: np.ndarray,
    bundle: Mapping[str, Any],
    points: np.ndarray,
) -> Mapping[str, Any]:
    """Independent free-coordinate decoder at evaluator-owned T4 nodes."""

    contract = bundle["pointwise_decoder_contract"]
    layout = contract["free_layout"]["blocks"]
    tables = fourier_tables(contract["basis"], points)
    gamma_vector, _gamma_first, _gamma_second = _spectral(
        _layout_get(free, layout, "common.gamma"), tables
    )
    gamma = _sym_to_matrix(gamma_vector, 4)
    log_Omega, _log_first, _log_second = _spectral(
        _layout_get(free, layout, "common.log_Omega"), tables
    )
    varphi_E0, _varphi_first, _varphi_second = _spectral(
        _layout_get(free, layout, "common.varphi_E0"), tables
    )
    A_E0, _A_first, _A_second = _spectral(
        _layout_get(free, layout, "common.A_E0"), tables
    )
    S, omega_S = _rotation_and_spatial_derivative(
        _layout_get(free, layout, "Q_frame.q"), tables
    )
    varphi = np.einsum("pij,pj->pi", S, varphi_E0)
    A_common = np.einsum("pij,pmj->pmi", S, A_E0) - omega_S

    sides: dict[str, Any] = {}
    for side in SIDES:
        _Y, Y_first, _Y_second = _spectral(
            _layout_get(free, layout, f"{side}.Y"), tables
        )
        Y_first = Y_first[..., 0]
        metric_free, _metric_first, _metric_second = _spectral(
            _layout_get(free, layout, f"{side}.metric_free"), tables
        )
        adapted_cross = metric_free[:, :4]
        normal_metric = metric_free[:, 4]
        metric = np.empty((points.shape[0], 5, 5), dtype=float)
        metric[:, :4, :4] = (
            gamma
            - np.einsum("pm,pn->pmn", adapted_cross, Y_first)
            - np.einsum("pm,pn->pmn", Y_first, adapted_cross)
            + np.einsum(
                "p,pm,pn->pmn", normal_metric, Y_first, Y_first
            )
        )
        metric[:, :4, 4] = adapted_cross - normal_metric[:, None] * Y_first
        metric[:, 4, :4] = metric[:, :4, 4]
        metric[:, 4, 4] = normal_metric

        R0, omega_R0 = _rotation_and_spatial_derivative(
            _layout_get(free, layout, f"{side}.r_E0"), tables
        )
        R = np.einsum("pij,pjk->pik", S, R0)
        omega_R = omega_S + np.einsum("pij,pmj->pmi", S, omega_R0)
        phi_source = np.einsum("pji,pj->pi", R, varphi)
        A_source = np.einsum(
            "pji,pmj->pmi", R, A_common + omega_R
        )
        A_perp, _A_perp_first, _A_perp_second = _spectral(
            _layout_get(free, layout, f"{side}.A_perp"), tables
        )
        A_full = np.empty((points.shape[0], 5, 3), dtype=float)
        A_full[:, :4] = A_source - Y_first[:, :, None] * A_perp[:, None, :]
        A_full[:, 4] = A_perp
        B, _B_first, _B_second = _spectral(
            _layout_get(free, layout, f"{side}.B0_full"), tables
        )
        J1, _J_first, _J_second = _spectral(
            _layout_get(free, layout, f"{side}.boundary_jet_J1"), tables
        )
        C, _C_first, _C_second = _spectral(
            _layout_get(free, layout, f"{side}.interior_bump_C"), tables
        )
        sides[side] = {
            "Y_first": Y_first,
            "Y_second": _Y_second[..., 0],
            "g_trace": metric,
            "log_Omega_trace": log_Omega[..., 0],
            "phi_trace": phi_source,
            "A_trace_full": A_full,
            "B_trace_full": B,
            "boundary_jet_J1": J1,
            "interior_bump_C": C,
            "R_source_to_Q": R,
            "omega_R": omega_R,
        }
    return {
        "common": {
            "gamma": gamma,
            "log_Omega": log_Omega[..., 0],
            "varphi": varphi,
            "A_Sigma": A_common,
            "S_Q": S,
        },
        "sides": sides,
    }


def pointwise_gluing_defects(decoded: Mapping[str, Any]) -> Mapping[str, Mapping[str, np.ndarray]]:
    common = decoded["common"]
    result: dict[str, Mapping[str, np.ndarray]] = {}
    for side in SIDES:
        item = decoded["sides"][side]
        count = item["Y_first"].shape[0]
        tangent = np.zeros((count, 5, 4), dtype=float)
        tangent[:, :4] = np.eye(4)[None, :, :]
        tangent[:, 4] = item["Y_first"]
        induced = np.einsum(
            "pMm,pMN,pNn->pmn", tangent, item["g_trace"], tangent
        )
        pulled_A = item["A_trace_full"][:, :4] + (
            item["Y_first"][:, :, None]
            * item["A_trace_full"][:, 4, None, :]
        )
        transported_A = np.einsum(
            "pij,pmj->pmi", item["R_source_to_Q"], pulled_A
        ) - item["omega_R"]
        result[side] = {
            "gamma": induced - common["gamma"],
            "Omega": np.exp(item["log_Omega_trace"])
            - np.exp(common["log_Omega"]),
            "phi": np.einsum(
                "pij,pj->pi", item["R_source_to_Q"], item["phi_trace"]
            )
            - common["varphi"],
            "A": transported_A - common["A_Sigma"],
        }
    return result


def _summarize_pointwise_gluing(
    defects: Mapping[str, Mapping[str, np.ndarray]],
) -> Mapping[str, Mapping[str, Mapping[str, float | int]]]:
    return {
        side: {
            component: {
                "scalar_entry_count": int(values.size),
                "Linf": float(np.max(np.abs(values))),
                "RMS": float(math.sqrt(float(np.mean(values * values)))),
            }
            for component, values in side_defects.items()
        }
        for side, side_defects in defects.items()
    }


def _identity_rotation_residual(
    free: np.ndarray,
    bundle: Mapping[str, Any],
    points: np.ndarray,
) -> Mapping[str, float]:
    decoded = decode_pointwise_free_boundary(free, bundle, points)
    identity = np.eye(3)
    return {
        side: float(
            np.max(
                np.abs(
                    decoded["sides"][side]["R_source_to_Q"]
                    - identity[None, :, :]
                )
            )
        )
        for side in SIDES
    }


def _periodic_derivatives(
    values: np.ndarray,
    points_per_axis: int,
) -> tuple[np.ndarray, np.ndarray]:
    expected = points_per_axis ** 4
    if values.shape[0] != expected:
        raise ValueError("periodic derivative input does not match the tensor mesh")
    grid = values.reshape((points_per_axis,) * 4 + values.shape[1:])
    spectrum = np.fft.fftn(grid, axes=(0, 1, 2, 3))
    frequencies = np.fft.fftfreq(points_per_axis, d=1.0 / points_per_axis)
    trailing = (1,) * (values.ndim - 1)
    first = np.empty((expected, 4) + values.shape[1:], dtype=float)
    second = np.empty((expected, 4, 4) + values.shape[1:], dtype=float)
    for mu in range(4):
        multiplier_mu = frequencies.reshape(
            (1,) * mu + (points_per_axis,) + (1,) * (3 - mu) + trailing
        )
        first_grid = np.fft.ifftn(
            1j * multiplier_mu * spectrum, axes=(0, 1, 2, 3)
        ).real
        first[:, mu] = first_grid.reshape((expected,) + values.shape[1:])
        for nu in range(4):
            multiplier_nu = frequencies.reshape(
                (1,) * nu
                + (points_per_axis,)
                + (1,) * (3 - nu)
                + trailing
            )
            second_grid = np.fft.ifftn(
                -multiplier_mu * multiplier_nu * spectrum,
                axes=(0, 1, 2, 3),
            ).real
            second[:, mu, nu] = second_grid.reshape(
                (expected,) + values.shape[1:]
            )
    return first, second


def radial_profiles(rho: np.ndarray, K: int) -> Mapping[str, np.ndarray]:
    rho = np.asarray(rho, dtype=float)
    h0 = np.zeros_like(rho)
    h0_first = np.zeros_like(rho)
    h0_second = np.zeros_like(rho)
    interior = (rho >= 0.0) & (rho < 1.0)
    r = rho[interior]
    one_minus = 1.0 - r
    log_first = -2.0 * r / (one_minus ** 3)
    log_second = -2.0 * (1.0 + 2.0 * r) / (one_minus ** 4)
    h = np.exp(-((r / one_minus) ** 2))
    h0[interior] = h
    h0_first[interior] = h * log_first
    h0_second[interior] = h * (log_second + log_first ** 2)
    h1 = rho * h0
    h1_first = h0 + rho * h0_first
    h1_second = 2.0 * h0_first + rho * h0_second

    bumps = np.zeros((rho.size, K), dtype=float)
    bumps_first = np.zeros_like(bumps)
    bumps_second = np.zeros_like(bumps)
    bump_domain = (rho > 0.0) & (rho < 1.0)
    rb = rho[bump_domain]
    s = rb * (1.0 - rb)
    envelope = np.exp(4.0 - 1.0 / s)
    envelope_log_first = (1.0 - 2.0 * rb) / (s ** 2)
    envelope_log_second = -2.0 / (s ** 2) - 2.0 * ((1.0 - 2.0 * rb) ** 2) / (s ** 3)
    z = 2.0 * rb - 1.0
    for j in range(K):
        coefficient = np.zeros(j + 1)
        coefficient[j] = 1.0
        first_coefficient = np.polynomial.legendre.legder(coefficient, 1)
        second_coefficient = np.polynomial.legendre.legder(coefficient, 2)
        polynomial = np.polynomial.legendre.legval(z, coefficient)
        polynomial_first = 2.0 * np.polynomial.legendre.legval(z, first_coefficient)
        polynomial_second = 4.0 * np.polynomial.legendre.legval(z, second_coefficient)
        bumps[bump_domain, j] = envelope * polynomial
        bumps_first[bump_domain, j] = envelope * (
            polynomial_first + polynomial * envelope_log_first
        )
        bumps_second[bump_domain, j] = envelope * (
            polynomial_second
            + 2.0 * polynomial_first * envelope_log_first
            + polynomial * (envelope_log_second + envelope_log_first ** 2)
        )
    return {
        "h0": h0,
        "h0_first": h0_first,
        "h0_second": h0_second,
        "h1": h1,
        "h1_first": h1_first,
        "h1_second": h1_second,
        "bumps": bumps,
        "bumps_first": bumps_first,
        "bumps_second": bumps_second,
    }


def _sampled_side_channels(
    decoded: Mapping[str, Any],
    side: str,
    points_per_axis: int,
    K: int,
) -> tuple[np.ndarray, ...]:
    item = decoded["sides"][side]
    point_count = item["g_trace"].shape[0]
    X0 = np.zeros((point_count, 64), dtype=float)
    X0[:, :15] = _matrix_to_sym(item["g_trace"], 5)
    X0[:, 15] = item["log_Omega_trace"]
    X0[:, 16:19] = item["phi_trace"]
    X0[:, 19:34] = item["A_trace_full"].reshape(point_count, 15)
    X0[:, 34:64] = item["B_trace_full"].reshape(point_count, 30)
    J1 = item["boundary_jet_J1"]
    C = item["interior_bump_C"]
    if C.shape != (point_count, K, 64):
        raise ValueError("unexpected sampled compact radial coefficient shape")
    X0_x, X0_xx = _periodic_derivatives(X0, points_per_axis)
    J_x, J_xx = _periodic_derivatives(J1, points_per_axis)
    C_x, C_xx = _periodic_derivatives(C, points_per_axis)
    reference = np.zeros(64, dtype=float)
    reference[:15] = _matrix_to_sym(REFERENCE_METRIC, 5)
    return X0, X0_x, X0_xx, J1, J_x, J_xx, C, C_x, C_xx, reference


def _combine_channels(
    samples: tuple[np.ndarray, ...],
    profiles: Mapping[str, np.ndarray],
) -> Mapping[str, np.ndarray]:
    X0, X0_x, X0_xx, J, J_x, J_xx, C, C_x, C_xx, reference = samples
    h0 = profiles["h0"]
    h1 = profiles["h1"]
    b = profiles["bumps"]
    value = (
        reference[None, None, :]
        + h0[None, :, None] * (X0[:, None, :] - reference[None, None, :])
        + h1[None, :, None] * J[:, None, :]
        + np.einsum("rk,pkc->prc", b, C)
    )
    tangent = (
        h0[None, :, None, None] * X0_x[:, None, :, :]
        + h1[None, :, None, None] * J_x[:, None, :, :]
        + np.einsum("rk,pmkc->prmc", b, C_x)
    )
    tangent_second = (
        h0[None, :, None, None, None] * X0_xx[:, None, :, :, :]
        + h1[None, :, None, None, None] * J_xx[:, None, :, :, :]
        + np.einsum("rk,pabkc->prabc", b, C_xx)
    )
    radial = (
        profiles["h0_first"][None, :, None]
        * (X0[:, None, :] - reference[None, None, :])
        + profiles["h1_first"][None, :, None] * J[:, None, :]
        + np.einsum("rk,pkc->prc", profiles["bumps_first"], C)
    )
    radial_second = (
        profiles["h0_second"][None, :, None]
        * (X0[:, None, :] - reference[None, None, :])
        + profiles["h1_second"][None, :, None] * J[:, None, :]
        + np.einsum("rk,pkc->prc", profiles["bumps_second"], C)
    )
    mixed = (
        profiles["h0_first"][None, :, None, None] * X0_x[:, None, :, :]
        + profiles["h1_first"][None, :, None, None] * J_x[:, None, :, :]
        + np.einsum("rk,pmkc->prmc", profiles["bumps_first"], C_x)
    )
    return {
        "value": value,
        "tangent": tangent,
        "tangent_second": tangent_second,
        "radial": radial,
        "radial_second": radial_second,
        "mixed": mixed,
    }


def _physical_derivatives(
    channel: Mapping[str, np.ndarray],
    Y_first: np.ndarray,
    Y_second: np.ndarray,
    collar_sign: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    value = channel["value"]
    tangent = channel["tangent"]
    radial = channel["radial"]
    tangent_second = channel["tangent_second"]
    mixed = channel["mixed"]
    radial_second = channel["radial_second"]
    P, R, C = value.shape
    first = np.empty((P, R, 5, C), dtype=float)
    second = np.empty((P, R, 5, 5, C), dtype=float)
    first[:, :, :4, :] = tangent - (
        collar_sign * Y_first[:, None, :, None] * radial[:, :, None, :]
    )
    first[:, :, 4, :] = collar_sign * radial
    for mu in range(4):
        for nu in range(4):
            second[:, :, mu, nu, :] = (
                tangent_second[:, :, mu, nu, :]
                - collar_sign
                * (
                    Y_first[:, None, mu, None] * mixed[:, :, nu, :]
                    + Y_first[:, None, nu, None] * mixed[:, :, mu, :]
                    + Y_second[:, None, mu, nu, None] * radial
                )
                + Y_first[:, None, mu, None]
                * Y_first[:, None, nu, None]
                * radial_second
            )
        second[:, :, mu, 4, :] = (
            collar_sign * mixed[:, :, mu, :]
            - Y_first[:, None, mu, None] * radial_second
        )
        second[:, :, 4, mu, :] = second[:, :, mu, 4, :]
    second[:, :, 4, 4, :] = radial_second
    return value, first, second


def decode_bulk_state(
    free: np.ndarray,
    bundle: Mapping[str, Any],
    points: np.ndarray,
    points_per_axis: int,
    rho: np.ndarray,
    side: str,
    N: int,
    K: int,
) -> Mapping[str, np.ndarray]:
    decoded = decode_pointwise_free_boundary(free, bundle, points)
    Y_first = decoded["sides"][side]["Y_first"]
    Y_second = decoded["sides"][side]["Y_second"]
    collar_sign = -1 if side == "plus" else 1
    profiles = radial_profiles(rho, K)
    channels = _combine_channels(
        _sampled_side_channels(decoded, side, points_per_axis, K), profiles
    )
    value, first, second = _physical_derivatives(
        channels, Y_first, Y_second, collar_sign
    )
    log_Omega = value[..., 15]
    dlog_Omega = first[..., 15]
    Omega = np.exp(log_Omega)
    dOmega = Omega[..., None] * dlog_Omega
    return {
        "g": _sym_to_matrix(value[..., :15], 5),
        "dg": _sym_to_matrix(first[..., :15], 5),
        "ddg": _sym_to_matrix(second[..., :15], 5),
        "Omega": Omega,
        "dOmega": dOmega,
        "dlog_Omega": dlog_Omega,
        "phi": value[..., 16:19],
        "dphi": first[..., 16:19],
        "A": value[..., 19:34].reshape(value.shape[:2] + (5, 3)),
        "dA": first[..., 19:34].reshape(first.shape[:3] + (5, 3)),
        "B": value[..., 34:64].reshape(value.shape[:2] + (10, 3)),
        "Y_first": Y_first,
        "Y_second": Y_second,
        "collar_sign": np.asarray(collar_sign),
    }


def _connection(metric: np.ndarray, metric_first: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    dimension = metric.shape[0]
    inverse = np.linalg.inv(metric)
    connection = np.zeros((dimension, dimension, dimension), dtype=float)
    for upper in range(dimension):
        for lower_a in range(dimension):
            for lower_b in range(dimension):
                connection[upper, lower_a, lower_b] = 0.5 * sum(
                    inverse[upper, ell]
                    * (
                        metric_first[lower_a, ell, lower_b]
                        + metric_first[lower_b, ell, lower_a]
                        - metric_first[ell, lower_a, lower_b]
                    )
                    for ell in range(dimension)
                )
    return inverse, connection


def tensor_geometry(
    metric: np.ndarray,
    metric_first: np.ndarray,
    metric_second: np.ndarray,
) -> Mapping[str, np.ndarray | float]:
    dimension = metric.shape[0]
    inverse, connection = _connection(metric, metric_first)
    inverse_first = np.empty((dimension, dimension, dimension), dtype=float)
    for derivative in range(dimension):
        inverse_first[derivative] = -inverse @ metric_first[derivative] @ inverse
    connection_first = np.zeros((dimension, dimension, dimension, dimension), dtype=float)
    for derivative in range(dimension):
        for upper in range(dimension):
            for lower_a in range(dimension):
                for lower_b in range(dimension):
                    total = 0.0
                    for ell in range(dimension):
                        C = (
                            metric_first[lower_a, ell, lower_b]
                            + metric_first[lower_b, ell, lower_a]
                            - metric_first[ell, lower_a, lower_b]
                        )
                        dC = (
                            metric_second[derivative, lower_a, ell, lower_b]
                            + metric_second[derivative, lower_b, ell, lower_a]
                            - metric_second[derivative, ell, lower_a, lower_b]
                        )
                        total += inverse_first[derivative, upper, ell] * C + inverse[upper, ell] * dC
                    connection_first[derivative, upper, lower_a, lower_b] = 0.5 * total
    ricci = np.zeros((dimension, dimension), dtype=float)
    for mu in range(dimension):
        for nu in range(dimension):
            derivative_terms = sum(
                connection_first[k, k, mu, nu] - connection_first[nu, k, mu, k]
                for k in range(dimension)
            )
            quadratic_terms = 0.0
            for k in range(dimension):
                for ell in range(dimension):
                    quadratic_terms += (
                        connection[k, mu, nu] * connection[ell, k, ell]
                        - connection[k, mu, ell] * connection[ell, nu, k]
                    )
            ricci[mu, nu] = derivative_terms + quadratic_terms
    scalar = float(np.einsum("ij,ij->", inverse, ricci))
    return {"inverse": inverse, "connection": connection, "ricci": ricci, "scalar": scalar}


def _curvature_tau(A: np.ndarray, dA: np.ndarray) -> np.ndarray:
    result = np.zeros((5, 5, 3), dtype=float)
    for M in range(5):
        for N in range(M + 1, 5):
            value = dA[M, N] - dA[N, M] + np.cross(A[M], A[N])
            result[M, N] = value
            result[N, M] = -value
    return result


def _bf_coefficient(B: np.ndarray, curvature: np.ndarray, collar_sign: int) -> float:
    total = 0.0
    all_indices = set(range(5))
    for position, triple in enumerate(B_TRIPLES):
        pair = tuple(sorted(all_indices.difference(triple)))
        sign = _permutation_sign(triple + pair)
        total += sign * float(B[position] @ curvature[pair[0], pair[1]])
    return float(collar_sign * total)


def _superpotential(Omega: float, parameters: Mapping[str, float]) -> tuple[float, float]:
    M5 = float(parameters["M5_cubed"])
    G = float(parameters["compensator_metric_G"])
    k = float(parameters["k_infinity"])
    W = 3.0 * M5 * k * math.exp(-G * Omega * Omega / (6.0 * M5))
    W_Omega = -G * Omega * W / (3.0 * M5)
    return W, W_Omega


def bulk_action_components(
    state: Mapping[str, np.ndarray],
    tangential_weights: np.ndarray,
    radial_weights: np.ndarray,
    parameters: Mapping[str, float],
    side: str,
    inertia_records: dict[str, list[Mapping[str, float | int]]] | None = None,
) -> Mapping[str, float]:
    values = {name: 0.0 for name in ACTION_COMPONENTS if name.endswith(f"bulk_{side}")}
    M5 = float(parameters["M5_cubed"])
    G = float(parameters["compensator_metric_G"])
    Z5 = float(parameters["material_Z5_per_side"])
    material_mass = float(parameters["material_mass_M"])
    kappa_BF = float(parameters["kappa_BF_inner_product"])
    reference_volume = math.sqrt(-float(np.linalg.det(REFERENCE_METRIC)))
    _reference_W, reference_W_Omega = _superpotential(1.0, parameters)
    reference_U = (
        reference_W_Omega * reference_W_Omega / (2.0 * G)
        - 2.0 * _reference_W * _reference_W / (3.0 * M5)
    )
    for p in range(state["g"].shape[0]):
        for r in range(state["g"].shape[1]):
            metric = state["g"][p, r]
            _record_lorentzian_inertia(
                inertia_records,
                f"bulk_{side}",
                metric,
                1,
                4,
                f"bulk_{side}[p={p},r={r}]",
            )
            determinant = float(np.linalg.det(metric))
            if determinant >= 0.0:
                raise ValueError(f"non-Lorentzian bulk determinant at {side}, p={p}, r={r}")
            volume = math.sqrt(-determinant)
            geometry = tensor_geometry(metric, state["dg"][p, r], state["ddg"][p, r])
            inverse = geometry["inverse"]
            weight = float(tangential_weights[p] * radial_weights[r])
            Omega = float(state["Omega"][p, r])
            dOmega = state["dOmega"][p, r]
            Omega_norm = float(np.einsum("mn,m,n->", inverse, dOmega, dOmega))
            W, W_Omega = _superpotential(Omega, parameters)
            potential_U = W_Omega * W_Omega / (2.0 * G) - 2.0 * W * W / (3.0 * M5)
            phi = state["phi"][p, r]
            A = state["A"][p, r]
            covariant_phi = np.empty((5, 3), dtype=float)
            for M in range(5):
                covariant_phi[M] = state["dphi"][p, r, M] + np.cross(A[M], phi)
                covariant_phi[M] += 1.5 * phi * state["dlog_Omega"][p, r, M]
            P_norm = float(np.einsum("mn,ma,na->", inverse, covariant_phi, covariant_phi))
            argument = Omega ** 1.5 * float(np.linalg.norm(phi))
            V4 = argument ** 4 / (2.0 * math.sqrt(1.0 + argument ** 4))
            curvature = _curvature_tau(A, state["dA"][p, r])
            bf = _bf_coefficient(
                state["B"][p, r], curvature, int(state["collar_sign"])
            )
            values[f"EH_bulk_{side}"] += weight * volume * M5 * float(geometry["scalar"]) / 2.0
            values[f"Omega_kinetic_bulk_{side}"] += weight * volume * (-G * Omega_norm / 2.0)
            values[f"Omega_potential_bulk_{side}"] += weight * (
                volume * (-potential_U) - reference_volume * (-reference_U)
            )
            values[f"P_kinetic_bulk_{side}"] += weight * volume * (-Z5 * P_norm / 2.0)
            values[f"full_V4_bulk_{side}"] += weight * volume * (
                -Z5 * material_mass ** 2 * Omega ** -5.0 * V4
            )
            values[f"BF_bulk_{side}"] += weight * kappa_BF * bf
    return values


def ghy_component(
    free: np.ndarray,
    bundle: Mapping[str, Any],
    points: np.ndarray,
    points_per_axis: int,
    tangential_weights: np.ndarray,
    parameters: Mapping[str, float],
    side: str,
    N: int,
    K: int,
    inertia_records: dict[str, list[Mapping[str, float | int]]] | None = None,
) -> float:
    state = decode_bulk_state(
        free,
        bundle,
        points,
        points_per_axis,
        np.asarray([0.0]),
        side,
        N,
        K,
    )
    outward_sign = 1.0 if side == "plus" else -1.0
    total = 0.0
    for p in range(state["g"].shape[0]):
        metric = state["g"][p, 0]
        inverse, connection = _connection(metric, state["dg"][p, 0])
        Y_first = state["Y_first"][p]
        Y_second = state["Y_second"][p]
        tangent = np.zeros((5, 4), dtype=float)
        tangent[:4, :] = np.eye(4)
        tangent[4, :] = Y_first
        induced = tangent.T @ metric @ tangent
        _record_lorentzian_inertia(
            inertia_records,
            f"interface_GHY_{side}",
            induced,
            1,
            3,
            f"interface_GHY_{side}[p={p}]",
        )
        determinant = float(np.linalg.det(induced))
        if determinant >= 0.0:
            raise ValueError(f"non-Lorentzian induced determinant at {side}, p={p}")
        raw_covector = np.concatenate((-Y_first, (1.0,)))
        norm_squared = float(raw_covector @ inverse @ raw_covector)
        if norm_squared <= 0.0:
            raise ValueError(f"non-spacelike interface normal at {side}, p={p}")
        normal_covector = outward_sign * raw_covector / math.sqrt(norm_squared)
        second_embedding = np.zeros((5, 4, 4), dtype=float)
        second_embedding[4] = Y_second
        acceleration = second_embedding.copy()
        acceleration += np.einsum("pmn,ma,nb->pab", connection, tangent, tangent)
        extrinsic = -np.einsum("p,pab->ab", normal_covector, acceleration)
        theta = float(np.einsum("ab,ab->", np.linalg.inv(induced), extrinsic))
        total += (
            float(tangential_weights[p])
            * math.sqrt(-determinant)
            * float(parameters["M5_cubed"])
            * theta
        )
    return total


def interface_action_components(
    free: np.ndarray,
    layout: Mapping[str, Any],
    tables: Mapping[str, np.ndarray],
    tangential_weights: np.ndarray,
    parameters: Mapping[str, float],
    inertia_records: dict[str, list[Mapping[str, float | int]]] | None = None,
) -> Mapping[str, float]:
    gamma_coeff = _layout_get(free, layout, "common.gamma")
    gamma_vector, gamma_vector_first, gamma_vector_second = _spectral(gamma_coeff, tables)
    gamma = _sym_to_matrix(gamma_vector, 4)
    gamma_first = _sym_to_matrix(gamma_vector_first, 4)
    gamma_second = _sym_to_matrix(gamma_vector_second, 4)
    T_value, T_first, T_second = _spectral(_layout_get(free, layout, "common.T"), tables)
    del T_value
    log_Omega, _log_first, _log_second = _spectral(
        _layout_get(free, layout, "common.log_Omega"), tables
    )
    varphi_E0, _varphi_first, _varphi_second = _spectral(
        _layout_get(free, layout, "common.varphi_E0"), tables
    )
    frame_q, _frame_first, _frame_second = _spectral(
        _layout_get(free, layout, "Q_frame.q"), tables
    )
    varphi = np.empty_like(varphi_E0)
    for point in range(varphi.shape[0]):
        varphi[point] = _so3_exp(frame_q[point]) @ varphi_E0[point]
    result = {name: 0.0 for name in ACTION_COMPONENTS[14:]}
    Mb2 = float(parameters["brane_Mb_squared"])
    beta = float(parameters["brane_beta"])
    lambda_K = float(parameters["lambda_K"])
    xi = float(parameters["xi"])
    eta = float(parameters["eta"])
    B4_bar = float(parameters["B4_bar"])
    k_infinity = float(parameters["k_infinity"])
    kappa_hat = float(parameters["Robin_kappa_hat"])
    robin_y = float(parameters["Robin_y"])
    for p in range(gamma.shape[0]):
        _record_lorentzian_inertia(
            inertia_records,
            "interface_common",
            gamma[p],
            1,
            3,
            f"interface_common[p={p}]",
        )
        determinant = float(np.linalg.det(gamma[p]))
        if determinant >= 0.0:
            raise ValueError(f"non-Lorentzian common metric determinant at p={p}")
        volume = math.sqrt(-determinant)
        geometry = tensor_geometry(gamma[p], gamma_first[p], gamma_second[p])
        inverse = geometry["inverse"]
        connection = geometry["connection"]
        time_gradient = T_first[p, :, 0].copy()
        time_gradient[0] += 1.0
        time_hessian = T_second[p, :, :, 0]
        clock_norm = -float(time_gradient @ inverse @ time_gradient)
        if clock_norm <= 0.0:
            raise ValueError(f"non-timelike khronon at p={p}")
        normalization = clock_norm ** -0.5
        inverse_first = np.empty((4, 4, 4), dtype=float)
        for derivative in range(4):
            inverse_first[derivative] = -inverse @ gamma_first[p, derivative] @ inverse
        clock_norm_first = np.empty(4, dtype=float)
        for derivative in range(4):
            clock_norm_first[derivative] = -(
                np.einsum(
                    "ab,a,b->", inverse_first[derivative], time_gradient, time_gradient
                )
                + 2.0
                * np.einsum(
                    "ab,a,b->", inverse, time_hessian[derivative], time_gradient
                )
            )
        normalization_first = -0.5 * clock_norm ** -1.5 * clock_norm_first
        u_covector = -normalization * time_gradient
        u_vector = inverse @ u_covector
        u_first = np.empty((4, 4), dtype=float)
        for derivative in range(4):
            u_first[derivative] = (
                -normalization_first[derivative] * time_gradient
                - normalization * time_hessian[derivative]
            )
        covariant_u = u_first - np.einsum("lab,l->ab", connection, u_covector)
        projector = np.eye(4) + np.outer(u_covector, u_vector)
        foliation_K = np.einsum("ma,nb,ab->mn", projector, projector, covariant_u)
        foliation_K = 0.5 * (foliation_K + foliation_K.T)
        K_trace = float(np.einsum("mn,mn->", inverse, foliation_K))
        K_square = float(
            np.einsum("ma,nb,mn,ab->", inverse, inverse, foliation_K, foliation_K)
        )
        acceleration_covector = np.einsum("a,am->m", u_vector, covariant_u)
        acceleration_square = float(
            np.einsum("mn,m,n->", inverse, acceleration_covector, acceleration_covector)
        )

        E0 = np.empty((4, 3), dtype=float)
        for column in range(3):
            candidate = np.zeros(4, dtype=float)
            candidate[column + 1] = 1.0
            candidate += u_vector * u_covector[column + 1]
            for previous in range(column):
                projection = float(E0[:, previous] @ gamma[p] @ candidate)
                candidate -= projection * E0[:, previous]
            norm_squared = float(candidate @ gamma[p] @ candidate)
            if norm_squared <= 0.0:
                raise ValueError(f"degenerate horizontal frame at p={p}, column={column}")
            E0[:, column] = candidate / math.sqrt(norm_squared)
        Q_rotation = _so3_exp(frame_q[p])
        E_Q = E0 @ Q_rotation.T
        acceleration_internal = E_Q.T @ acceleration_covector
        robin_vector = varphi[p] - robin_y * acceleration_internal
        Omega = math.exp(float(log_Omega[p, 0]))
        W, _W_Omega = _superpotential(Omega, parameters)
        weight = float(tangential_weights[p]) * volume
        scalar_R4 = float(geometry["scalar"])
        scalar_Rcal = leaf_scalar_curvature(
            scalar_R4,
            geometry["ricci"],
            u_vector,
            K_trace,
            K_square,
        )
        result["wall"] += weight * (-(2.0 * W + 0.5 * beta * (Omega - 1.0) ** 2))
        result["K_foliation"] += weight * (0.5 * Mb2 * (K_square - lambda_K * K_trace ** 2))
        result["R"] += weight * (0.5 * Mb2 * xi * scalar_Rcal)
        result["R_squared"] += weight * (
            0.5 * Mb2 * (-B4_bar * scalar_Rcal ** 2 / (16.0 * k_infinity ** 2))
        )
        result["a_squared"] += weight * (0.5 * Mb2 * eta * acceleration_square)
        result["Robin"] += weight * (-0.5 * kappa_hat * float(robin_vector @ robin_vector))
    return result


def leaf_scalar_curvature(
    scalar_R4: float,
    ricci_R4: np.ndarray,
    u_vector: np.ndarray,
    K_trace: float,
    K_square: float,
) -> float:
    """Gauss identity for signature -+++ and K=h nabla u."""

    ricci_uu = float(np.einsum("mn,m,n->", ricci_R4, u_vector, u_vector))
    return float(scalar_R4 + 2.0 * ricci_uu - K_trace ** 2 + K_square)


def action_evaluation(
    free: np.ndarray,
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    tangential_points_per_axis: int = 5,
    radial_gauss_order: int = 3,
    numerical_role: str = "refinable",
) -> Mapping[str, Any]:
    N = int(member["N"])
    K = int(member["K"])
    _pseudospectral_role(tangential_points_per_axis, numerical_role)
    pointwise = bundle["pointwise_decoder_contract"]
    layout = pointwise["free_layout"]["blocks"]
    basis = pointwise["basis"]
    tangential = tangential_quadrature(tangential_points_per_axis)
    radial = radial_quadrature(radial_gauss_order)
    tables = fourier_tables(basis, tangential["points"])
    parameters = bundle["action_contract"]["coefficient_parameters"]
    gluing = _summarize_pointwise_gluing(
        pointwise_gluing_defects(
            decode_pointwise_free_boundary(free, bundle, tangential["points"])
        )
    )
    values: dict[str, float] = {}
    inertia_records: dict[str, list[Mapping[str, float | int]]] = {}
    for side in SIDES:
        state = decode_bulk_state(
            free,
            bundle,
            tangential["points"],
            tangential_points_per_axis,
            radial["points"],
            side,
            N,
            K,
        )
        values.update(
            bulk_action_components(
                state,
                tangential["weights"],
                radial["weights"],
                parameters,
                side,
                inertia_records,
            )
        )
        values[f"GHY_{side}"] = ghy_component(
            free,
            bundle,
            tangential["points"],
            tangential_points_per_axis,
            tangential["weights"],
            parameters,
            side,
            N,
            K,
            inertia_records,
        )
    values.update(
        interface_action_components(
            free,
            layout,
            tables,
            tangential["weights"],
            parameters,
            inertia_records,
        )
    )
    if set(values) != set(ACTION_COMPONENTS):
        missing = sorted(set(ACTION_COMPONENTS).difference(values))
        extra = sorted(set(values).difference(ACTION_COMPONENTS))
        raise RuntimeError(f"action component coverage mismatch: missing={missing}, extra={extra}")
    result = {name: float(values[name]) for name in ACTION_COMPONENTS}
    result["S_total"] = float(math.fsum(result.values()))
    return {
        "components": result,
        "lorentzian_inertia": _summarize_lorentzian_inertia(inertia_records),
        "pointwise_gluing": gluing,
    }


def action_components(
    free: np.ndarray,
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    tangential_points_per_axis: int = 5,
    radial_gauss_order: int = 3,
) -> Mapping[str, float]:
    return action_evaluation(
        free,
        bundle,
        member,
        tangential_points_per_axis,
        radial_gauss_order,
        "refinable",
    )["components"]


def fd5_directional_derivative(
    curve: Mapping[str, Any],
    step_family: Mapping[str, Any],
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    tangential_points_per_axis: int,
    radial_gauss_order: int,
    central_evaluation: Mapping[str, Any] | None = None,
    numerical_role: str = "refinable",
) -> Mapping[str, Any]:
    if central_evaluation is None:
        central_evaluation = action_evaluation(
            _decode_f64(member["authoritative_free_central_f64le"]),
            bundle,
            member,
            tangential_points_per_axis,
            radial_gauss_order,
            numerical_role,
        )
    central = central_evaluation["components"]
    if step_family["multipliers"] != [-2, -1, 1, 2]:
        raise ValueError("route B requires the published centered FD5 multipliers")
    endpoints = step_family["free_endpoints_f64le"]
    endpoint_evaluations = {
        key: action_evaluation(
            _decode_f64(endpoints[key]),
            bundle,
            member,
            tangential_points_per_axis,
            radial_gauss_order,
            numerical_role,
        )
        for key in ("-2", "-1", "1", "2")
    }
    evaluated = {
        key: endpoint_evaluations[key]["components"]
        for key in ("-2", "-1", "1", "2")
    }
    step = float(step_family["step"])
    if step <= 0.0:
        raise ValueError("FD5 step must be positive")
    result: dict[str, float] = {}
    scales: dict[str, Mapping[str, float]] = {}
    for component in ACTION_COMPONENTS + ("S_total",):
        centered = {
            key: evaluated[key][component] - central[component]
            for key in ("-2", "-1", "1", "2")
        }
        weighted_terms = (
            centered["-2"],
            -8.0 * centered["-1"],
            8.0 * centered["1"],
            -centered["2"],
        )
        numerator = math.fsum(weighted_terms)
        absolute_term_sum = math.fsum(abs(item) for item in weighted_terms)
        result[component] = float(numerator / (12.0 * step))
        scales[component] = {
            "central_S_rel_abs": abs(float(central[component])),
            "centered_endpoint_max_abs": max(abs(float(item)) for item in centered.values()),
            "FD5_weighted_term_sum_abs": float(absolute_term_sum),
            "FD5_numerator_abs": abs(float(numerator)),
            "cancellation_ratio": (
                abs(float(numerator)) / float(absolute_term_sum)
                if absolute_term_sum > 0.0
                else 0.0
            ),
        }
    return {
        "curve_name": curve["name"],
        "step_family_label": step_family["label"],
        "step": step,
        "FD5_action_directional_derivative": result,
        "FD5_centering_scales": scales,
        "central_lorentzian_inertia": central_evaluation["lorentzian_inertia"],
        "endpoint_lorentzian_inertia": {
            key: endpoint_evaluations[key]["lorentzian_inertia"]
            for key in ("-2", "-1", "1", "2")
        },
        "central_pointwise_gluing": central_evaluation["pointwise_gluing"],
        "endpoint_pointwise_gluing": {
            key: endpoint_evaluations[key]["pointwise_gluing"]
            for key in ("-2", "-1", "1", "2")
        },
    }


def _raw_f64_sha256(value: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(value, dtype="<f8")
    return _sha256_bytes(contiguous.tobytes(order="C"))


def _pointwise_gluing_linf(evaluation: Mapping[str, Any]) -> float:
    return max(
        float(component["Linf"])
        for side in evaluation["pointwise_gluing"].values()
        for component in side.values()
    )


def affine_fd5_step_window(
    free: np.ndarray,
    tangent: np.ndarray,
    steps: Sequence[float],
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    tangential_points_per_axis: int,
    radial_gauss_order: int,
    numerical_role: str = "refinable",
) -> Mapping[str, Any]:
    """Evaluate a nested FD5 window, caching every shared affine endpoint.

    The window does not change the spectral family: every endpoint is formed in
    its authoritative free coordinates and then passed through the same
    common-first pointwise decoder.  Requiring dyadic refinement makes the
    shared endpoints explicit and auditable.
    """

    if free.shape != tangent.shape or free.ndim != 1:
        raise ValueError("FD5 window free/tangent shape mismatch")
    step_values = tuple(float(step) for step in steps)
    if not step_values or any(not math.isfinite(step) or step <= 0.0 for step in step_values):
        raise ValueError("FD5 window steps must be finite and positive")
    if any(
        not math.isclose(finer * 2.0, coarser, rel_tol=0.0, abs_tol=1.0e-18)
        for coarser, finer in zip(step_values, step_values[1:])
    ):
        raise ValueError("FD5 window must be a strictly descending dyadic refinement")

    endpoint_cache: dict[float, Mapping[str, Any]] = {}
    endpoint_records: dict[str, Mapping[str, Any]] = {}
    for step in step_values:
        for multiplier in (-2, -1, 1, 2):
            displacement = float(multiplier * step)
            if displacement in endpoint_cache:
                continue
            endpoint = np.asarray(free + displacement * tangent, dtype=float)
            evaluation = action_evaluation(
                endpoint,
                bundle,
                member,
                tangential_points_per_axis,
                radial_gauss_order,
                numerical_role,
            )
            endpoint_cache[displacement] = evaluation
            key = displacement.hex()
            endpoint_records[key] = {
                "displacement": displacement,
                "authoritative_free_endpoint_sha256": _raw_f64_sha256(endpoint),
                "S_rel_components": evaluation["components"],
                "pointwise_gluing_Linf": _pointwise_gluing_linf(evaluation),
                "lorentzian_inertia": evaluation["lorentzian_inertia"],
            }

    derivatives: list[Mapping[str, Any]] = []
    for step in step_values:
        evaluated = {
            multiplier: endpoint_cache[float(multiplier * step)]["components"]
            for multiplier in (-2, -1, 1, 2)
        }
        derivative = {
            component: float(
                math.fsum(
                    (
                        evaluated[-2][component],
                        -8.0 * evaluated[-1][component],
                        8.0 * evaluated[1][component],
                        -evaluated[2][component],
                    )
                )
                / (12.0 * step)
            )
            for component in ACTION_COMPONENTS + ("S_total",)
        }
        derivatives.append(
            {
                "step": step,
                "endpoint_displacements": [
                    float(multiplier * step) for multiplier in (-2, -1, 1, 2)
                ],
                "FD5_action_directional_derivative": derivative,
            }
        )
    return {
        "steps": list(step_values),
        "dyadic_refinement": True,
        "unique_endpoint_count": len(endpoint_cache),
        "endpoint_records_by_float_hex": endpoint_records,
        "derivatives": derivatives,
    }


def _curve_receipt(
    curve: Mapping[str, Any],
    family_results: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]],
) -> Mapping[str, Any]:
    return {
        "kind": "SO3_horizontal_free_curve",
        "name": curve["name"],
        "comparison_role": curve["comparison_role"],
        "parent_ambient_tangent_sha256": curve["parent_ambient_tangent_sha256"],
        "authoritative_free_tangent_sha256": curve[
            "authoritative_free_tangent_f64le"
        ]["sha256"],
        "step_family_results": [
            {
                "label": family["label"],
                "step": float(family["step"]),
                "free_endpoint_sha256": {
                    key: family["free_endpoints_f64le"][key]["sha256"]
                    for key in ("-2", "-1", "1", "2")
                },
                "FD5_action_directional_derivative": derivative[
                    "FD5_action_directional_derivative"
                ],
                "FD5_centering_scales": derivative["FD5_centering_scales"],
                "endpoint_lorentzian_inertia": derivative[
                    "endpoint_lorentzian_inertia"
                ],
                "endpoint_pointwise_gluing": derivative[
                    "endpoint_pointwise_gluing"
                ],
            }
            for family, derivative in family_results
        ],
    }


def build_route_receipt(
    direction_scope: str = "all",
    tangential_points_per_axis: int = 5,
    radial_gauss_order: int = 3,
) -> Mapping[str, Any]:
    if direction_scope not in {"smoke", "all"}:
        raise ValueError("direction_scope must be 'smoke' or 'all'")
    bundle = load_primitive_bundle()
    member = _member(bundle, "N2.K2.seed20260902")
    identity_member = _member(bundle, "N2.K2.seed0")
    free = _decode_f64(member["authoritative_free_central_f64le"])
    identity_free = _decode_f64(
        identity_member["authoritative_free_central_f64le"]
    )
    tangential_rule = tangential_quadrature(tangential_points_per_axis)
    radial_rule = radial_quadrature(radial_gauss_order)
    numerical_role = "smoke" if direction_scope == "smoke" else "refinable"
    central_evaluation = action_evaluation(
        free,
        bundle,
        member,
        tangential_points_per_axis,
        radial_gauss_order,
        numerical_role,
    )
    central = central_evaluation["components"]
    identity_evaluation = action_evaluation(
        identity_free,
        bundle,
        identity_member,
        tangential_points_per_axis,
        radial_gauss_order,
        numerical_role,
    )
    curves = list(member["curves"])
    if direction_scope == "smoke":
        curves = [
            next(
                curve
                for curve in curves
                if curve["name"] == "joint_all_primitive_classes_control_candidate"
            )
        ]
    derivative_receipts = []
    for curve in curves:
        families = curve["step_families"]
        if direction_scope == "smoke":
            families = families[:1]
        family_results = []
        for family in families:
            derivative = fd5_directional_derivative(
                curve,
                family,
                bundle,
                member,
                tangential_points_per_axis,
                radial_gauss_order,
                central_evaluation,
                numerical_role,
            )
            family_results.append((family, derivative))
        derivative_receipts.append(_curve_receipt(curve, family_results))
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": (
            "independent_route_B;finite_compact_relative_action_evaluation;"
            "raw_FD5_values_only;no_global_C1_N1_promotion"
        ),
        "input_contract": {
            "primitive_bundle": {"path": BUNDLE.as_posix(), "sha256": BUNDLE_SHA256},
            "mandatory_Gauss_corrigendum": {
                "artifact_sha256": GAUSS_CORRIGENDUM_ARTIFACT_SHA256,
                "required_decision": (
                    "decision.v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma=false"
                ),
            },
            "literal_action_sha256": LITERAL_ACTION_SHA256,
            "member_id": member["member_id"],
            "identity_control_member_id": identity_member["member_id"],
            "fields_consumed": [
                "action_contract.exact_action",
                "action_contract.coefficient_parameters",
                "pointwise_decoder_contract basis/free-layout/component/frame/embedding contracts",
                "primary_member authoritative free center/tangents/multi-h endpoints",
            ],
        },
        "implementation_contract": {
            "numeric_stack": "NumPy float64 plus Python standard library",
            "owned_implementations": [
                "real Fourier evaluation and first/second derivatives",
                "pointwise common-first reconstruction of all eliminated glued traces",
                "route-owned periodic FFT differentiation of nonlinear reconstructed traces",
                "compact radial trace lift, normal jet, Legendre bumps and first/second derivatives",
                "ambient-to-collar chain rule and full form-orientation Jacobian sign",
                "Christoffel, Ricci, scalar curvature, GHY and intrinsic foliation tensors",
                "tau-basis SO3 curvature, covariant derivative and BF wedge contraction",
                "literal v5.2 twenty-component action and FD5 directional derivative",
            ],
            "external_project_module_imports": [],
            "runtime_scientific_input_count": 1,
            "runtime_scientific_input": BUNDLE.as_posix(),
            "finite_difference_formula": "(S[-2]-8*S[-1]+8*S[1]-S[2])/(12*h)",
        },
        "quadrature_and_mesh": {
            "tangential_domain": "T4=[0,2*pi)^4",
            "tangential_rule": "uniform periodic trapezoidal tensor product",
            "nonlinear_derivative_rule": (
                "route-owned odd-Q Fourier projection of reconstructed pointwise "
                "traces; not asserted exact at finite Q"
            ),
            "pseudospectral_role": (
                _pseudospectral_role(tangential_points_per_axis, numerical_role)
            ),
            "tangential_points_per_axis": tangential_points_per_axis,
            "tangential_total_points": tangential_points_per_axis ** 4,
            "tangential_nodes": tangential_rule["points"].tolist(),
            "tangential_weights": tangential_rule["weights"].tolist(),
            "tangential_weight_sum": float(np.sum(tangential_rule["weights"])),
            "radial_domain": [0.0, 1.0],
            "radial_rule": "Gauss-Legendre",
            "radial_order": radial_gauss_order,
            "radial_nodes": radial_rule["points"].tolist(),
            "radial_weights": radial_rule["weights"].tolist(),
            "radial_weight_sum": float(np.sum(radial_rule["weights"])),
            "refinement_axes": [
                "increase tangential_points_per_axis",
                "increase radial_gauss_order",
                "select higher N with K=N from a future bundle",
                "compare the published h, h/2 and h/4 FD5 stencils on the same affine free curve",
            ],
        },
        "component_coverage": list(ACTION_COMPONENTS) + ["S_total"],
        "direction_scope": {
            "mode": direction_scope,
            "evaluated_direction_count": len(curves),
            "evaluated_step_family_count": sum(
                len(item["step_family_results"]) for item in derivative_receipts
            ),
            "published_N2_horizontal_curve_count": len(member["curves"]),
            "primary_curve": "joint_all_primitive_classes_control_candidate",
        },
        "relative_action_normalization": {
            "object": "S_rel_v5_2_on_finite_C_N_member",
            "bulk_operation": "subtract L_i[X_infinity] from each bulk component before integration",
            "reference_metric": np.diag(REFERENCE_METRIC).tolist(),
            "reference_Omega": 1.0,
            "reference_phi_A_B": "zero",
            "outer_boundary_operation": "none because every perturbation profile is flat at rho=1",
            "interface_operation": "no reference subtraction",
        },
        "central_relative_action_components": central,
        "central_lorentzian_inertia": central_evaluation["lorentzian_inertia"],
        "central_pointwise_gluing": central_evaluation["pointwise_gluing"],
        "free_curve_affine_residuals": _free_curve_affine_residuals(
            member, int(bundle["pointwise_decoder_contract"]["free_coordinate_dimension"])
        ),
        "R_equals_identity_control": {
            "member_id": identity_member["member_id"],
            "R_minus_identity_Linf_by_side": _identity_rotation_residual(
                identity_free, bundle, tangential_rule["points"]
            ),
            "relative_action_components": identity_evaluation["components"],
            "lorentzian_inertia": identity_evaluation["lorentzian_inertia"],
            "pointwise_gluing": identity_evaluation["pointwise_gluing"],
        },
        "raw_directional_derivatives": derivative_receipts,
        "mutant_campaign_specification": {
            "execution_status": "prepared_not_run",
            "input_mutants": list(PREPARED_MUTANTS),
            "component_omission_mutants": [
                {
                    "id": f"omit_{component}",
                    "target": component,
                    "intervention": "set only this computed component density to zero and reevaluate totals",
                }
                for component in ACTION_COMPONENTS
            ],
            "component_sign_mutants": [
                {
                    "id": f"invert_sign_{component}",
                    "target": component,
                    "intervention": "multiply only this computed component density by -1 and reevaluate totals",
                }
                for component in ACTION_COMPONENTS
            ],
        },
        "evidence_boundary": (
            "These are finite-collar N=2 quadrature values and raw FD5 derivatives. "
            "They are neither an action-closure residual nor a continuous theorem."
        ),
        "dependency_graph": {
            "nodes": [
                {"id": "pointwise_primitive_bundle_bcbb0037", "kind": "only_configuration_input"},
                {"id": "numpy_route_B_owned_action", "kind": "independent_implementation"},
                {"id": "route_B_raw_receipt", "kind": "raw_numeric_output"},
            ],
            "edges": [
                {
                    "from": "pointwise_primitive_bundle_bcbb0037",
                    "to": "numpy_route_B_owned_action",
                    "carries": ["literal_contracts", "authoritative_free_curves", "multi_h_FD5_endpoints"],
                    "embedded_integrity_records": [
                        "Gauss_corrigendum_7c2c3e46_pin",
                        "v5_5_4_intrinsic_Rcal_required_false",
                    ],
                },
                {
                    "from": "numpy_route_B_owned_action",
                    "to": "route_B_raw_receipt",
                    "carries": [
                        "twenty_relative_components",
                        "relative_total",
                        "centered_raw_FD5_derivatives",
                    ],
                },
            ],
        },
    }
    receipt["scientific_payload_sha256"] = _canonical_sha256(receipt)
    receipt["provenance"] = {
        "generator": {
            "path": Path(__file__).resolve().relative_to(REPO).as_posix(),
            "sha256": _sha256_file(Path(__file__).resolve().relative_to(REPO)),
        },
        "test": {"path": TEST.as_posix(), "sha256": _sha256_file(TEST)},
        "numpy": np.__version__,
    }
    return receipt


def render_receipt(receipt: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _inertia_summary_is_lorentzian(summary: Mapping[str, Any]) -> bool:
    return bool(summary) and all(
        int(row["negative_count_at_each_node"]) == 1
        and int(row["zero_count_at_each_node"]) == 0
        and float(row["minimum_spectral_margin_absolute"]) > 0.0
        and float(row["minimum_spectral_margin_relative"]) > 0.0
        for row in summary.values()
    )


def build_refinement_receipt() -> Mapping[str, Any]:
    """Build the Q=5 route-B raw receipt and cached FD5 refinement window."""

    bundle = load_primitive_bundle()
    member = _member(bundle, "N2.K2.seed20260902")
    identity_member = _member(bundle, "N2.K2.seed0")
    free = _decode_f64(member["authoritative_free_central_f64le"])
    identity_free = _decode_f64(
        identity_member["authoritative_free_central_f64le"]
    )
    curve = next(
        row
        for row in member["curves"]
        if row["name"] == "joint_all_primitive_classes_control_candidate"
    )
    tangent = _decode_f64(curve["authoritative_free_tangent_f64le"])
    Q = 5
    radial_order = 3
    central = action_evaluation(free, bundle, member, Q, radial_order, "refinable")
    identity = action_evaluation(
        identity_free, bundle, identity_member, Q, radial_order, "refinable"
    )
    window = affine_fd5_step_window(
        free,
        tangent,
        FD5_REFINEMENT_STEPS,
        bundle,
        member,
        Q,
        radial_order,
        "refinable",
    )
    endpoint_rows = list(window["endpoint_records_by_float_hex"].values())
    identity_points = tangential_quadrature(Q)["points"]
    identity_rotation = _identity_rotation_residual(
        identity_free, bundle, identity_points
    )
    published_endpoint_manifest = [
        {
            "label": family["label"],
            "step": float(family["step"]),
            "free_endpoint_sha256": {
                multiplier: record["sha256"]
                for multiplier, record in family["free_endpoints_f64le"].items()
            },
            "role": "archived_small_h_roundoff_stress_not_used_to_fit_the_h4_window",
        }
        for family in curve["step_families"]
    ]
    checks = {
        "sole_runtime_input_bundle_byte_pin_verified": True,
        "literal_v5_2_action_hash_verified": True,
        "mandatory_Gauss_quarantine_embedded_in_bundle": True,
        "Q5_is_refinable_odd_grid": _pseudospectral_role(Q, "refinable")
        == "odd_Q_refinable_projection",
        "central_pointwise_gluing_below_2e_12": _pointwise_gluing_linf(central)
        < 2.0e-12,
        "identity_pointwise_gluing_below_2e_12": _pointwise_gluing_linf(identity)
        < 2.0e-12,
        "all_endpoint_pointwise_gluing_below_2e_12": max(
            float(row["pointwise_gluing_Linf"]) for row in endpoint_rows
        )
        < 2.0e-12,
        "central_all_action_nodes_Lorentzian": _inertia_summary_is_lorentzian(
            central["lorentzian_inertia"]
        ),
        "identity_all_action_nodes_Lorentzian": _inertia_summary_is_lorentzian(
            identity["lorentzian_inertia"]
        ),
        "all_endpoint_action_nodes_Lorentzian": all(
            _inertia_summary_is_lorentzian(row["lorentzian_inertia"])
            for row in endpoint_rows
        ),
        "N2_seed0_R_exactly_identity": max(identity_rotation.values()) < 2.0e-14,
        "dyadic_FD5_window_and_endpoint_cache_complete": window[
            "dyadic_refinement"
        ]
        and window["unique_endpoint_count"] == 12,
        "independent_AD_agreement_pass": False,
        "Euler_Green_independent_route_pass": False,
        "mutant_campaign_pass": False,
        "clean_process_redteam_pass": False,
        "multi_N_continuum_extension_pass": False,
    }
    excluded = {
        "independent_AD_agreement_pass",
        "Euler_Green_independent_route_pass",
        "mutant_campaign_pass",
        "clean_process_redteam_pass",
        "multi_N_continuum_extension_pass",
    }
    route_b_ready = all(value for key, value in checks.items() if key not in excluded)
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": "theory_only;finite_N2;raw_route_B;no_C1_N1_promotion",
        "decision": {
            "route_B_Q5_literal_action_and_FD5_window_pass": route_b_ready,
            "restricted_spectral_action_closure_claimed": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "checks": checks,
        "input_contract": {
            "primitive_bundle": {
                "path": BUNDLE.as_posix(),
                "sha256": BUNDLE_SHA256,
                "payload_sha256": bundle["payload_sha256"],
            },
            "literal_action_sha256": LITERAL_ACTION_SHA256,
            "member_id": member["member_id"],
            "identity_control_member_id": identity_member["member_id"],
            "authoritative_free_central_sha256": member[
                "authoritative_free_central_f64le"
            ]["sha256"],
            "authoritative_free_tangent_sha256": curve[
                "authoritative_free_tangent_f64le"
            ]["sha256"],
            "parent_ambient_tangent_sha256": curve[
                "parent_ambient_tangent_sha256"
            ],
        },
        "implementation_contract": {
            "numeric_stack": "NumPy float64 plus Python standard library",
            "external_project_module_imports": [],
            "runtime_scientific_input_count": 1,
            "runtime_scientific_input": BUNDLE.as_posix(),
            "finite_difference_formula": "(S[-2]-8*S[-1]+8*S[1]-S[2])/(12*h)",
            "endpoint_rule": "free_endpoint=free_central+displacement*authoritative_free_tangent",
        },
        "scientific": {
            "quadrature": {
                "tangential_points_per_axis": Q,
                "tangential_total_points": Q**4,
                "radial_gauss_order": radial_order,
            },
            "central_S_rel_components": central["components"],
            "central_pointwise_gluing": central["pointwise_gluing"],
            "central_lorentzian_inertia": central["lorentzian_inertia"],
            "FD5_refinement_window": window,
            "published_small_h_endpoint_manifest": published_endpoint_manifest,
            "R_equals_identity_control": {
                "central_S_rel_components": identity["components"],
                "pointwise_gluing": identity["pointwise_gluing"],
                "lorentzian_inertia": identity["lorentzian_inertia"],
                "R_minus_identity_Linf_by_side": identity_rotation,
            },
        },
        "mutant_campaign_specification": {
            "execution_status": "prepared_not_run",
            "input_mutants": list(PREPARED_MUTANTS),
            "component_omission_mutants": [
                f"omit_{component}" for component in ACTION_COMPONENTS
            ],
            "component_sign_mutants": [
                f"invert_sign_{component}" for component in ACTION_COMPONENTS
            ],
        },
        "provenance": {
            "generator": {
                "path": Path(__file__).resolve().relative_to(REPO).as_posix(),
                "sha256": _sha256_file(Path(__file__).resolve().relative_to(REPO)),
            },
            "test": {"path": TEST.as_posix(), "sha256": _sha256_file(TEST)},
            "numpy": np.__version__,
        },
        "evidence_boundary": "This raw route-B receipt covers one finite N2 member, a Q5 FD5 step window, and a matched R=I control. It does not compare AD, derive Euler-Green, execute mutants, prove multi-N convergence, or promote C1/N1.",
    }
    receipt["scientific_payload_sha256"] = _canonical_sha256(receipt["scientific"])
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--emit-refinement", action="store_true")
    parser.add_argument("--tangential-points-per-axis", type=int, default=5)
    parser.add_argument("--radial-gauss-order", type=int, default=3)
    args = parser.parse_args()
    if args.emit_refinement:
        receipt = build_refinement_receipt()
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(render_receipt(receipt))
        print(OUTPUT)
        return
    receipt = build_route_receipt(
        direction_scope="smoke",
        tangential_points_per_axis=args.tangential_points_per_axis,
        radial_gauss_order=args.radial_gauss_order,
    )
    first = receipt["raw_directional_derivatives"][0]
    first_family = first["step_family_results"][0]
    print(
        json.dumps(
            {
                "member_id": receipt["input_contract"]["member_id"],
                "central_relative_action_components": receipt[
                    "central_relative_action_components"
                ],
                "direction_name": first["name"],
                "FD5_action_directional_derivative": first_family[
                    "FD5_action_directional_derivative"
                ],
                "FD5_centering_scales": first_family["FD5_centering_scales"],
            },
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
