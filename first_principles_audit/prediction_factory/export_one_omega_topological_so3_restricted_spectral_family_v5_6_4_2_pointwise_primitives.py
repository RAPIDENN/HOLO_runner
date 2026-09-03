#!/usr/bin/env python3
"""Export authoritative common-first free curves for pointwise gluing.

This additive v5.6.4.2 bundle fixes the interpolation defect of ambient traces:
evaluators receive free common-first coefficients and reconstruct all eliminated
traces at their own nodes.  The frozen v5.6.4 generator is used only here, after
its bytes are verified, to map the already-audited ambient directions into free
coordinate curves.  Evaluators do not import this file or that generator.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.linalg import expm, expm_frechet


REPO = Path(__file__).resolve().parents[2]
PREDICTION_FACTORY = Path("first_principles_audit/prediction_factory")
ARTIFACTS = PREDICTION_FACTORY / "artifacts"
PARENT_BUNDLE = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_1_primitive_bundle.json"
)
PARENT_BUNDLE_SHA256 = "e751d2b542f2246ca7f5aec5632ef0b114819694dd2dc347accb38411d8a0fbc"
UPSTREAM_GENERATOR = PREDICTION_FACTORY / (
    "derive_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_certificate.py"
)
UPSTREAM_GENERATOR_SHA256 = "198808b829a708ca9bc0314bfc5db235317f42eb48aa8f17ced6070cc3c87b7e"
GAUSS_CORRIGENDUM_SOURCE = PREDICTION_FACTORY / (
    "derive_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"
)
GAUSS_CORRIGENDUM_SOURCE_SHA256 = (
    "ac290aebfd981e54e5c5a9bda697fb6e23a4c15c4a17e540aa33700c11f7c717"
)
GAUSS_CORRIGENDUM_TEST = PREDICTION_FACTORY / (
    "test_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"
)
GAUSS_CORRIGENDUM_TEST_SHA256 = (
    "584192eb81e881fdd31fc60dd6c96926a9dfaac6e7d1dc9a7f5dacad15f8db78"
)
GAUSS_CORRIGENDUM_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.json"
)
GAUSS_CORRIGENDUM_ARTIFACT_SHA256 = (
    "7c2c3e46ea73b312f753d944e43cd2a2e224d000e5ddd3c3e15ff816e76e441a"
)
GAUSS_CORRIGENDUM_SCHEMA = (
    "holo.one-omega-topological-so3-v5-5-4-gauss-sign-corrigendum.v1"
)
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_2_pointwise_primitive_bundle.json"
)
TEST = PREDICTION_FACTORY / (
    "test_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_2_pointwise_primitives.py"
)
SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-2-pointwise-primitive-bundle.v1"
)
PARENT_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-1-primitive-bundle.v1"
)
PRIMARY_MEMBER_ID = "N2.K2.seed20260902"
CONTROL_MEMBER_ID = "N2.K2.seed0"
PRIMARY_CURVE = "joint_all_primitive_classes_control_candidate"
STEP_SCALES = (("h", 1.0), ("h_over_2", 0.5), ("h_over_4", 0.25))
MULTIPLIERS = (-2, -1, 1, 2)
SYMMETRIC4 = tuple((i, j) for i in range(4) for j in range(i, 4))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))


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


def _load_parent() -> Mapping[str, Any]:
    raw = (REPO / PARENT_BUNDLE).read_bytes()
    if _sha256_bytes(raw) != PARENT_BUNDLE_SHA256:
        raise RuntimeError("v5.6.4.1 primitive bundle byte pin mismatch")
    parent = json.loads(raw)
    if parent.get("schema") != PARENT_SCHEMA:
        raise ValueError("unexpected v5.6.4.1 primitive bundle schema")
    return parent


def _validate_gauss_corrigendum() -> None:
    pins = (
        (GAUSS_CORRIGENDUM_SOURCE, GAUSS_CORRIGENDUM_SOURCE_SHA256),
        (GAUSS_CORRIGENDUM_TEST, GAUSS_CORRIGENDUM_TEST_SHA256),
        (GAUSS_CORRIGENDUM_ARTIFACT, GAUSS_CORRIGENDUM_ARTIFACT_SHA256),
    )
    for relative_path, expected_sha256 in pins:
        if _sha256_file(relative_path) != expected_sha256:
            raise RuntimeError(f"Gauss corrigendum pin mismatch: {relative_path}")
    corrigendum = json.loads((REPO / GAUSS_CORRIGENDUM_ARTIFACT).read_bytes())
    if corrigendum.get("schema") != GAUSS_CORRIGENDUM_SCHEMA:
        raise ValueError("unexpected Gauss corrigendum schema")
    if corrigendum["decision"][
        "v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma"
    ] is not False:
        raise ValueError("v5.5.4 intrinsic-Rcal quarantine was lifted")


@lru_cache(maxsize=1)
def _upstream_module():
    if _sha256_file(UPSTREAM_GENERATOR) != UPSTREAM_GENERATOR_SHA256:
        raise RuntimeError("v5.6.4 generator byte pin mismatch")
    absolute = REPO / UPSTREAM_GENERATOR
    module_name = "_frozen_restricted_spectral_family_v5_6_4_for_pointwise_export"
    spec = importlib.util.spec_from_file_location(module_name, absolute)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen v5.6.4 generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _decode_f64(record: Mapping[str, Any]) -> np.ndarray:
    if record["dtype"] != "<f8" or record["encoding"] != "base64":
        raise ValueError("expected base64 little-endian float64")
    raw = base64.b64decode(record["data"], validate=True)
    if _sha256_bytes(raw) != record["sha256"]:
        raise ValueError("compact array digest mismatch")
    result = np.frombuffer(raw, dtype="<f8").copy()
    shape = tuple(int(item) for item in record["shape"])
    if result.size != math.prod(shape):
        raise ValueError("compact array shape mismatch")
    return result.reshape(shape)


def _encode_f64(array: np.ndarray) -> Mapping[str, Any]:
    normalized = np.ascontiguousarray(np.asarray(array, dtype="<f8"))
    raw = normalized.tobytes(order="C")
    return {
        "data": base64.b64encode(raw).decode("ascii"),
        "dtype": "<f8",
        "encoding": "base64",
        "sha256": _sha256_bytes(raw),
        "shape": list(normalized.shape),
    }


def _parent_member(parent: Mapping[str, Any], member_id: str) -> Mapping[str, Any]:
    selected = [item for item in parent["primitive_members"] if item["member_id"] == member_id]
    if len(selected) != 1:
        raise ValueError(f"expected one parent member {member_id}")
    return selected[0]


def _free_get(
    free: np.ndarray,
    layout: Mapping[str, Any],
    name: str,
) -> np.ndarray:
    block = layout[name]
    return free[int(block["start"]):int(block["stop"])].reshape(tuple(block["shape"]))


def _hat(vector: np.ndarray) -> np.ndarray:
    x, y, z = vector
    return np.asarray(((0.0, -z, y), (z, 0.0, -x), (-y, x, 0.0)), dtype=float)


def _vee(matrix: np.ndarray) -> np.ndarray:
    return np.asarray((matrix[2, 1], matrix[0, 2], matrix[1, 0]), dtype=float)


def _sym_to_matrix(vector: np.ndarray, dimension: int) -> np.ndarray:
    pairs = SYMMETRIC4 if dimension == 4 else SYMMETRIC5
    result = np.zeros(vector.shape[:-1] + (dimension, dimension), dtype=float)
    for position, (i, j) in enumerate(pairs):
        result[..., i, j] = vector[..., position]
        result[..., j, i] = vector[..., position]
    return result


def fourier_tables(basis: Mapping[str, Any], points: np.ndarray) -> Mapping[str, np.ndarray]:
    labels = basis["labels"]
    wavevectors = np.asarray(basis["mode_wavevectors"], dtype=float)
    values = np.empty((points.shape[0], len(labels)), dtype=float)
    first = np.empty((points.shape[0], 4, len(labels)), dtype=float)
    for mode, label in enumerate(labels):
        k = wavevectors[mode]
        phase = points @ k
        if label == "1":
            values[:, mode] = 1.0
            first[:, :, mode] = 0.0
        elif label.startswith("cos("):
            values[:, mode] = np.cos(phase)
            first[:, :, mode] = -np.sin(phase)[:, None] * k[None, :]
        elif label.startswith("sin("):
            values[:, mode] = np.sin(phase)
            first[:, :, mode] = np.cos(phase)[:, None] * k[None, :]
        else:
            raise ValueError(f"unsupported Fourier label {label}")
    return {"values": values, "first": first}


def _spectral(
    coefficients: np.ndarray,
    tables: Mapping[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    value = np.tensordot(tables["values"], coefficients, axes=([1], [0]))
    first = np.tensordot(tables["first"], coefficients, axes=([2], [0]))
    return value, first


def _rotation_field(
    coefficients: np.ndarray,
    tables: Mapping[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    value, first = _spectral(coefficients, tables)
    rotations = np.empty((value.shape[0], 3, 3), dtype=float)
    derivatives = np.empty((value.shape[0], 4, 3, 3), dtype=float)
    for point in range(value.shape[0]):
        algebra = _hat(value[point])
        rotations[point] = expm(algebra)
        for mu in range(4):
            derivatives[point, mu] = expm_frechet(
                algebra, _hat(first[point, mu]), compute_expm=False
            )
    return rotations, derivatives


def decode_pointwise_boundary(
    free: np.ndarray,
    contract: Mapping[str, Any],
    points: np.ndarray,
) -> Mapping[str, Any]:
    """Reconstruct common and eliminated lateral traces at arbitrary T4 nodes."""

    basis = contract["basis"]
    layout = contract["free_layout"]["blocks"]
    tables = fourier_tables(basis, np.asarray(points, dtype=float))
    gamma_vector, _gamma_first = _spectral(_free_get(free, layout, "common.gamma"), tables)
    gamma = _sym_to_matrix(gamma_vector, 4)
    T_value, T_first = _spectral(_free_get(free, layout, "common.T"), tables)
    del T_value
    S, dS = _rotation_field(_free_get(free, layout, "Q_frame.q"), tables)
    varphi0, _varphi0_first = _spectral(
        _free_get(free, layout, "common.varphi_E0"), tables
    )
    A0, _A0_first = _spectral(_free_get(free, layout, "common.A_E0"), tables)
    varphi = np.einsum("pij,pj->pi", S, varphi0)
    A_common = np.empty_like(A0)
    for point in range(points.shape[0]):
        for mu in range(4):
            A_common[point, mu] = _vee(
                S[point] @ _hat(A0[point, mu]) @ S[point].T
                - dS[point, mu] @ S[point].T
            )

    log_Omega, _log_first = _spectral(
        _free_get(free, layout, "common.log_Omega"), tables
    )
    time_gradient = T_first[..., 0]
    time_gradient[:, 0] += 1.0
    E0 = np.empty((points.shape[0], 4, 3), dtype=float)
    for point in range(points.shape[0]):
        inverse = np.linalg.inv(gamma[point])
        normalization = math.sqrt(-float(time_gradient[point] @ inverse @ time_gradient[point]))
        u_covector = -time_gradient[point] / normalization
        u = inverse @ u_covector
        for column in range(3):
            candidate = np.zeros(4)
            candidate[column + 1] = 1.0
            candidate += u * u_covector[column + 1]
            for previous in range(column):
                candidate -= (
                    E0[point, :, previous] @ gamma[point] @ candidate
                ) * E0[point, :, previous]
            candidate /= math.sqrt(float(candidate @ gamma[point] @ candidate))
            E0[point, :, column] = candidate
    E_Q = np.einsum("pma,pba->pmb", E0, S)

    sides: dict[str, Any] = {}
    for side in ("plus", "minus"):
        Y, Y_first = _spectral(_free_get(free, layout, f"{side}.Y"), tables)
        del Y
        Y_first = Y_first[..., 0]
        metric_free, _metric_free_first = _spectral(
            _free_get(free, layout, f"{side}.metric_free"), tables
        )
        d = metric_free[:, :4]
        a = metric_free[:, 4]
        metric = np.empty((points.shape[0], 5, 5), dtype=float)
        metric[:, :4, :4] = (
            gamma
            - np.einsum("pm,pn->pmn", d, Y_first)
            - np.einsum("pm,pn->pmn", Y_first, d)
            + np.einsum("p,pm,pn->pmn", a, Y_first, Y_first)
        )
        metric[:, :4, 4] = d - a[:, None] * Y_first
        metric[:, 4, :4] = metric[:, :4, 4]
        metric[:, 4, 4] = a

        R0, dR0 = _rotation_field(_free_get(free, layout, f"{side}.r_E0"), tables)
        R = np.einsum("pij,pjk->pik", S, R0)
        dR = np.einsum("pmij,pjk->pmik", dS, R0) + np.einsum(
            "pij,pmjk->pmik", S, dR0
        )
        phi_source = np.einsum("pji,pj->pi", R, varphi)
        A_source = np.empty_like(A_common)
        for point in range(points.shape[0]):
            for mu in range(4):
                A_source[point, mu] = _vee(
                    R[point].T @ _hat(A_common[point, mu]) @ R[point]
                    + R[point].T @ dR[point, mu]
                )
        A_perp, _A_perp_first = _spectral(
            _free_get(free, layout, f"{side}.A_perp"), tables
        )
        A_full = np.empty((points.shape[0], 5, 3), dtype=float)
        A_full[:, :4] = A_source - Y_first[:, :, None] * A_perp[:, None, :]
        A_full[:, 4] = A_perp
        B_full, _B_first = _spectral(
            _free_get(free, layout, f"{side}.B0_full"), tables
        )
        J1, _J1_first = _spectral(
            _free_get(free, layout, f"{side}.boundary_jet_J1"), tables
        )
        C, _C_first = _spectral(
            _free_get(free, layout, f"{side}.interior_bump_C"), tables
        )
        sides[side] = {
            "Y_first": Y_first,
            "g_trace": metric,
            "log_Omega_trace": log_Omega[..., 0],
            "phi_trace": phi_source,
            "A_trace_full": A_full,
            "B_trace_full": B_full,
            "boundary_jet_J1": J1,
            "interior_bump_C": C,
            "R_source_to_Q": R,
            "dR_source_to_Q": dR,
        }
    return {
        "common": {
            "gamma": gamma,
            "log_Omega": log_Omega[..., 0],
            "varphi": varphi,
            "A_Sigma": A_common,
            "E0": E0,
            "E_Q": E_Q,
            "S_Q": S,
        },
        "sides": sides,
    }


def pointwise_gluing_defects(decoded: Mapping[str, Any]) -> Mapping[str, Mapping[str, np.ndarray]]:
    common = decoded["common"]
    result: dict[str, Mapping[str, np.ndarray]] = {}
    for side in ("plus", "minus"):
        item = decoded["sides"][side]
        P = item["Y_first"].shape[0]
        tangent = np.zeros((P, 5, 4), dtype=float)
        tangent[:, :4] = np.eye(4)[None, :, :]
        tangent[:, 4] = item["Y_first"]
        induced = np.einsum("pMm,pMN,pNn->pmn", tangent, item["g_trace"], tangent)
        pulled_A = item["A_trace_full"][:, :4] + (
            item["Y_first"][:, :, None] * item["A_trace_full"][:, 4, None, :]
        )
        transported_A = np.empty_like(pulled_A)
        for point in range(P):
            R = item["R_source_to_Q"][point]
            for mu in range(4):
                transported_A[point, mu] = _vee(
                    R @ _hat(pulled_A[point, mu]) @ R.T
                    - item["dR_source_to_Q"][point, mu] @ R.T
                )
        result[side] = {
            "gamma": induced - common["gamma"],
            "Omega": np.exp(item["log_Omega_trace"]) - np.exp(common["log_Omega"]),
            "phi": np.einsum(
                "pij,pj->pi", item["R_source_to_Q"], item["phi_trace"]
            )
            - common["varphi"],
            "A": transported_A - common["A_Sigma"],
        }
    return result


def _raw_pointwise_diagnostic(
    record_id: str,
    free_record: Mapping[str, Any],
    contract: Mapping[str, Any],
    points: np.ndarray,
) -> Mapping[str, Any]:
    """Materialize raw componentwise gluing defects, without a gate boolean."""

    free = _decode_f64(free_record)
    defects = pointwise_gluing_defects(
        decode_pointwise_boundary(free, contract, points)
    )
    return {
        "record_id": record_id,
        "free_coordinates_sha256": free_record["sha256"],
        "raw_defects_f64le": {
            side: {
                component: _encode_f64(values)
                for component, values in side_defects.items()
            }
            for side, side_defects in defects.items()
        },
    }


def _free_curve(
    ambient_q: np.ndarray,
    ambient_tangent: np.ndarray,
    N: int,
    parameter: float,
) -> np.ndarray:
    upstream = _upstream_module()
    return np.asarray(
        upstream.ambient_to_free_coordinates(
            ambient_q + parameter * ambient_tangent, N
        ),
        dtype=float,
    )


def _codec_free_tangent(
    ambient_q: np.ndarray,
    ambient_tangent: np.ndarray,
    N: int,
    step: float,
) -> np.ndarray:
    values = {
        multiplier: _free_curve(
            ambient_q, ambient_tangent, N, multiplier * step
        )
        for multiplier in MULTIPLIERS
    }
    return (
        values[-2] - 8.0 * values[-1] + 8.0 * values[1] - values[2]
    ) / (12.0 * step)


def _pushforward_free_tangent(
    free_central: np.ndarray,
    free_tangent: np.ndarray,
    N: int,
    step: float,
) -> np.ndarray:
    upstream = _upstream_module()
    values = {
        multiplier: np.asarray(
            upstream.construct_ambient_point(
                free_central + multiplier * step * free_tangent, N
            ),
            dtype=float,
        )
        for multiplier in MULTIPLIERS
    }
    return (
        values[-2] - 8.0 * values[-1] + 8.0 * values[1] - values[2]
    ) / (12.0 * step)


def _curve_payload(
    parent_curve: Mapping[str, Any],
    ambient_q: np.ndarray,
    free_central: np.ndarray,
    N: int,
    base_step: float,
) -> Mapping[str, Any]:
    tangent = _decode_f64(parent_curve["ambient_primitive_tangent_f64le"])
    codec_derivative_step = base_step * 0.25
    free_tangent = _codec_free_tangent(
        ambient_q, tangent, N, codec_derivative_step
    )
    pushed_tangent = _pushforward_free_tangent(
        free_central, free_tangent, N, codec_derivative_step
    )
    pushforward_difference = pushed_tangent - tangent
    step_families = []
    for label, scale in STEP_SCALES:
        step = base_step * scale
        arrays = {
            str(multiplier): free_central + multiplier * step * free_tangent
            for multiplier in MULTIPLIERS
        }
        step_families.append(
            {
                "label": label,
                "step": step,
                "multipliers": list(MULTIPLIERS),
                "free_endpoints_f64le": {
                    str(multiplier): _encode_f64(arrays[str(multiplier)])
                    for multiplier in MULTIPLIERS
                },
            }
        )
    return {
        "name": parent_curve["name"],
        "comparison_role": (
            "primary_scientific_comparator"
            if parent_curve["name"] == PRIMARY_CURVE
            else "sector_isolation_and_mutant_control"
        ),
        "parent_ambient_tangent_f64le": parent_curve[
            "ambient_primitive_tangent_f64le"
        ],
        "parent_ambient_tangent_sha256": parent_curve[
            "ambient_primitive_tangent_f64le"
        ]["sha256"],
        "authoritative_free_tangent_f64le": _encode_f64(free_tangent),
        "curve_definition": (
            "f_v(s)=f0+s*v_free exactly; every published endpoint is evaluated "
            "from this same affine free-coordinate curve, never from a new seed"
        ),
        "free_tangent_codec_definition": (
            "v_free is the centered fourth-order directional derivative of the "
            "byte-pinned ambient_to_free_coordinates codec at q0 along v_parent"
        ),
        "codec_derivative_step": codec_derivative_step,
        "construct_pushforward_residual_L2": float(
            np.linalg.norm(pushforward_difference)
        ),
        "construct_pushforward_residual_Linf": float(
            np.max(np.abs(pushforward_difference))
        ),
        "step_families": step_families,
    }


def _geometry_contract() -> Mapping[str, Any]:
    return {
        "signature": "(-,+,+,+) on gamma and (-,+,+,+,+) in each bulk",
        "Riemann_4D": (
            "R^rho_(sigma mu nu)=partial_mu Gamma^rho_(nu sigma)-partial_nu "
            "Gamma^rho_(mu sigma)+Gamma^rho_(mu lambda)Gamma^lambda_(nu sigma)-"
            "Gamma^rho_(nu lambda)Gamma^lambda_(mu sigma)"
        ),
        "Ricci_4D": "Ric_(sigma nu)=R^rho_(sigma rho nu); R4=gamma^(sigma nu)Ric_(sigma nu)",
        "GHY": [
            "n_out is the normalized outward covector published in the collar contract",
            "Theta_mu_nu=E^M_mu E^N_nu nabla_M n_out_N",
            "Theta=gamma^mu_nu Theta_mu_nu",
        ],
        "khronon": [
            "tau_T=x0+T(x)",
            "u_mu=-N_T partial_mu tau_T with u_mu u^mu=-1",
            "h_mu_nu=gamma_mu_nu+u_mu u_nu",
        ],
        "foliation": [
            "Kcal_mu_nu=h_mu^alpha h_nu^beta D_alpha u_beta",
            "Kcal=gamma^mu_nu Kcal_mu_nu",
            "a_mu=u^nu D_nu u_mu",
            "Rcal=h^mu_rho h^nu_sigma R4_(mu nu rho sigma)-Kcal^2+Kcal_mu_nu Kcal^mu_nu",
            "equivalently Rcal=R4+2*Ric4_mu_nu*u^mu*u^nu-Kcal^2+Kcal_mu_nu*Kcal^mu_nu",
        ],
        "Gauss_sign_cross_checks": [
            "spatially flat FLRW gives Rcal=0",
            "static R x S3 of radius a gives Rcal=+6/a^2",
        ],
        "legacy_v5_5_4_note": (
            "The v5.5.4 scalar Ward lemma may be cited only inside its stated internal "
            "sign convention; its opposite Gauss sign is not the geometric definition "
            "of leaf intrinsic curvature and requires an additive corrigendum"
        ),
        "associated_spatial_vector": [
            "E_Q=E0 exp(-hat(q_Q))",
            "varphi_H^mu=E_Q^mu_a varphi_H^a",
            "h_mu_nu(varphi_H^mu-y*a^mu)(varphi_H^nu-y*a^nu) is the Robin norm",
        ],
    }


def build_bundle() -> Mapping[str, Any]:
    parent = _load_parent()
    _validate_gauss_corrigendum()
    upstream = _upstream_module()
    primary_parent = _parent_member(parent, PRIMARY_MEMBER_ID)
    control_parent = _parent_member(parent, CONTROL_MEMBER_ID)
    N = 2
    if int(primary_parent["N"]) != N or int(primary_parent["seed"]) != 20260902:
        raise ValueError("primary member identity drift")
    free_primary = np.asarray(upstream.build_free_coordinates(20260902, N), dtype=float)
    free_control = np.asarray(upstream.build_free_coordinates(0, N), dtype=float)
    ambient_q = _decode_f64(primary_parent["ambient_q_f64le"])
    inverse_primary = np.asarray(upstream.ambient_to_free_coordinates(ambient_q, N), dtype=float)
    if not np.allclose(free_primary, inverse_primary, rtol=0.0, atol=2.0e-12):
        raise ValueError("generated and inverse-mapped primary free coordinates differ")
    base_step = float(primary_parent["stencil_contract"]["step"])
    curves = [
        _curve_payload(item, ambient_q, free_primary, N, base_step)
        for item in primary_parent["horizontal_primitives"]
    ]
    roundtrip_primary = np.asarray(
        upstream.construct_ambient_point(free_primary, N), dtype=float
    )
    ambient_control = _decode_f64(control_parent["ambient_q_f64le"])
    roundtrip_control = np.asarray(
        upstream.construct_ambient_point(free_control, N), dtype=float
    )
    validation_rng = np.random.default_rng(5642)
    validation_points = validation_rng.uniform(0.0, 2.0 * math.pi, size=(7, 4))
    parent_spectral = parent["spectral_contract"]
    pointwise_contract = {
        "N": N,
        "K": N,
        "basis": parent_spectral["basis_by_N"][str(N)],
        "free_layout": parent_spectral["free_generator_layout_by_N"][str(N)],
        "tensor_component_order": parent_spectral["tensor_component_order"],
        "radial_profiles": parent_spectral["radial_profiles"],
        "radial_basis": parent_spectral["radial_basis"],
        "primitive_component_convention": parent_spectral[
            "primitive_component_convention"
        ],
        "frame_rotation_contract": parent_spectral["frame_rotation_contract"],
        "embedding_pullback_orientation_contract": parent_spectral[
            "embedding_pullback_orientation_contract"
        ],
        "free_coordinate_dimension": int(free_primary.size),
        "decoder": {
            "common": [
                "evaluate gamma,T,log_Omega,varphi_E0,A_E0,q_Q from free Fourier coefficients",
                "S=exp(hat(q_Q)); varphi=S varphi_E0; hat(A_Sigma)=S hat(A_E0) S^T-dS S^T",
                "build E0 from gamma and tau_T=x0+T, then E_Q=E0 S^T",
            ],
            "each_side": [
                "evaluate Y,dY,metric_free=(d_mu,a),A_perp,B0_full,r_E0,J1,C",
                "g_mu_nu=gamma_mu_nu-d_mu Y_nu-Y_mu d_nu+a Y_mu Y_nu",
                "g_mu4=d_mu-a Y_mu; g_44=a, hence Y^*g=gamma pointwise",
                "R0=exp(hat(r_E0)); R=S R0; phi_source=R^T varphi",
                "hat(A_source)=R^T hat(A_Sigma) R+R^T dR",
                "A_full_mu=A_source_mu-Y_mu A_perp; A_full_4=A_perp",
                "B0_full,J1,C remain independent source-frame bulk primitives",
            ],
            "pointwise_scope": (
                "These formulas define eliminated traces at every evaluator node; "
                "ambient spectral projections from v5.6.4 are lineage hashes only"
            ),
        },
    }
    joint_curve = next(item for item in curves if item["name"] == PRIMARY_CURVE)
    diagnostic_inputs: list[tuple[str, Mapping[str, Any]]] = [
        ("central", _encode_f64(free_primary))
    ]
    for family in joint_curve["step_families"]:
        for multiplier in MULTIPLIERS:
            diagnostic_inputs.append(
                (
                    f'{family["label"]}:{multiplier:+d}',
                    family["free_endpoints_f64le"][str(multiplier)],
                )
            )
    pointwise_diagnostics = [
        _raw_pointwise_diagnostic(
            record_id, free_record, pointwise_contract, validation_points
        )
        for record_id, free_record in diagnostic_inputs
    ]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": (
            "primitive_pointwise_family_contract;authoritative_free_curves;"
            "no_action_receipt;no_continuous_promotion"
        ),
        "source_pins": {
            "parent_primitive_bundle": {
                "path": PARENT_BUNDLE.as_posix(),
                "sha256": PARENT_BUNDLE_SHA256,
            },
            "lineage_generator_used_only_for_free_curve_export": {
                "path": UPSTREAM_GENERATOR.as_posix(),
                "sha256": UPSTREAM_GENERATOR_SHA256,
            },
            "mandatory_v5_5_4_Gauss_sign_corrigendum": {
                "source_path": GAUSS_CORRIGENDUM_SOURCE.as_posix(),
                "source_sha256": GAUSS_CORRIGENDUM_SOURCE_SHA256,
                "test_path": GAUSS_CORRIGENDUM_TEST.as_posix(),
                "test_sha256": GAUSS_CORRIGENDUM_TEST_SHA256,
                "artifact_path": GAUSS_CORRIGENDUM_ARTIFACT.as_posix(),
                "artifact_sha256": GAUSS_CORRIGENDUM_ARTIFACT_SHA256,
                "required_decision_path": (
                    "decision.v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma"
                ),
                "required_value_literal": "false",
            },
            "codec_provenance": (
                "Central free coordinates and D(ambient_to_free)_q directions are "
                "produced only by the byte-pinned v5.6.4 codec. The pointwise formulas "
                "in this exporter validate the public decoder contract; they do not "
                "replace the authoritative codec data."
            ),
        },
        "action_contract": parent["action_contract"],
        "geometry_convention": _geometry_contract(),
        "toroidal_relative_scope": parent["action_contract"][
            "compact_relative_action_contract"
        ],
        "pointwise_decoder_contract": pointwise_contract,
        "primary_member": {
            "member_id": PRIMARY_MEMBER_ID,
            "role": "primary_development_comparator",
            "N": N,
            "K": N,
            "seed": 20260902,
            "parent_ambient_q_sha256": primary_parent["ambient_q_f64le"]["sha256"],
            "authoritative_free_central_f64le": _encode_f64(free_primary),
            "codec_roundtrip": {
                "ambient_reconstruction_sha256": _encode_f64(roundtrip_primary)[
                    "sha256"
                ],
                "ambient_reconstruction_Linf": float(
                    np.max(np.abs(roundtrip_primary - ambient_q))
                ),
                "byte_relation": (
                    "byte_identical"
                    if roundtrip_primary.tobytes() == ambient_q.tobytes()
                    else "numeric_roundtrip"
                ),
            },
            "curves": curves,
        },
        "identity_control": {
            "member_id": CONTROL_MEMBER_ID,
            "role": "R_equals_identity_control_only",
            "N": N,
            "K": N,
            "seed": 0,
            "parent_ambient_q_sha256": control_parent["ambient_q_f64le"]["sha256"],
            "authoritative_free_central_f64le": _encode_f64(free_control),
            "codec_roundtrip": {
                "ambient_reconstruction_sha256": _encode_f64(roundtrip_control)[
                    "sha256"
                ],
                "ambient_reconstruction_Linf": float(
                    np.max(np.abs(roundtrip_control - ambient_control))
                ),
                "byte_relation": (
                    "byte_identical"
                    if roundtrip_control.tobytes() == ambient_control.tobytes()
                    else "numeric_roundtrip"
                ),
            },
        },
        "off_collocation_validation_nodes": {
            "role": "reserved_pointwise_decoder_validation",
            "domain": "T4=[0,2*pi)^4",
            "points_f64le": _encode_f64(validation_points),
            "raw_pointwise_gluing_diagnostics": pointwise_diagnostics,
        },
        "dependency_graph": {
            "nodes": [
                {"id": "v5_6_4_1_parent_bundle", "kind": "frozen_lineage_and_action_contract"},
                {"id": "v5_6_4_frozen_generator", "kind": "generation_time_free_coordinate_map"},
                {"id": "v5_5_4_Gauss_corrigendum", "kind": "mandatory_intrinsic_Rcal_quarantine"},
                {"id": "v5_6_4_2_pointwise_bundle", "kind": "only_future_evaluator_input"},
            ],
            "edges": [
                {
                    "from": "v5_6_4_1_parent_bundle",
                    "to": "v5_6_4_2_pointwise_bundle",
                    "carries": ["contracts", "member_and_tangent_lineage", "ambient_curve_seed_data"],
                },
                {
                    "from": "v5_6_4_frozen_generator",
                    "to": "v5_6_4_2_pointwise_bundle",
                    "carries": ["free_coordinate_curve_export_at_generation_time_only"],
                },
                {
                    "from": "v5_5_4_Gauss_corrigendum",
                    "to": "v5_6_4_2_pointwise_bundle",
                    "carries": ["correct_Gauss_sign", "v5_5_4_intrinsic_Rcal_quarantine"],
                },
            ],
        },
    }
    result["payload_sha256"] = _canonical_sha256(result)
    return result


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
