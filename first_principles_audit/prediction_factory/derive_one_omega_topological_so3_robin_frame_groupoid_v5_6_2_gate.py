#!/usr/bin/env python3
"""Independent Robin/frame/groupoid corrective gate for the v5.6.2 family.

This module does not import the v5.6.2 primary implementation or any earlier
Ward helper.  It reconstructs the literal v5.2 intrinsic Robin term on the
same selected moving graph family.  The boundary vector is soldered as

    varphi = R phi,             varphi_H^mu = E_Q^mu_a varphi^a,

where ``E_Q`` is a chosen coordinate-adapted local section of the oriented
orthonormal frame bundle of the spatial distribution defined by the induced
metric ``gamma`` and khronon ``T=t``.  It then keeps
the source-P and target-Q Ward identities separate:

    source P: delta phi = hat(lambda) phi, delta R = -R hat(lambda),
    target Q: delta varphi = hat(q) varphi, delta E_Q = -E_Q hat(q).

The selected-family metric/embedding/Omega/matter derivatives are evaluated
by a complex-step JVP and compared with a separately evaluated central finite
difference.  This closes only the Robin solder sub-block.  It is not a
same-action C1/N1 promotion, a red-team replication, or a BV--BFV result.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import platform
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "one_omega_topological_so3_robin_frame_groupoid_v5_6_2_gate.json"
TEST = HERE / "test_one_omega_topological_so3_robin_frame_groupoid_v5_6_2_gate.py"
V52_ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
V52_GENERATOR = HERE / "derive_one_omega_topological_so3_classical_v5_2_gate.py"
V52_TEST = HERE / "test_one_omega_topological_so3_classical_v5_2_gate.py"
V562_ARTIFACT = HERE / "artifacts" / "one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate.json"
V562_GENERATOR = HERE / "derive_one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate.py"
V562_TEST = HERE / "test_one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate.py"
SCHEMA = "holo.one-omega-topological-so3-robin-frame-groupoid-v5-6-2-gate.v1"

V52_PINS = {
    "artifact": "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
    "generator": "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
    "test": "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
}
V562_PINS = {
    "artifact": "48c1a98c2071df36eccc4ce30f2bdf962ad73c425330404f2c6b7cdb5913a590",
    "generator": "b9b0baf2c34620f5300ebf79084f9f8abf3a5f5b6374672c71c6add75222f372",
    "test": "bc0ba559975e5bdd975850e26daa42251c90cc46330d1f9a77941d7249fe3ce7",
}
V562_SCHEMA = "holo.one-omega-topological-so3-full-moving-c1-n1-v5-6-2-gate.v1"
ROBIN_LITERAL = (
    "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*"
    "h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)"
)

KAPPA = 1.0
ROBIN_Y = math.sqrt(3.0)
K_INFINITY = 1.0
WARP_CORE = 0.71
T_POINTS = 18
X_POINTS = 20
THETA = np.asarray([0.29, 0.24, 0.33, 0.41], dtype=float)
PARAMETER_NAMES = (
    "moving_embedding",
    "ambient_metric",
    "Omega",
    "associated_matter",
)
PRIMARY_PARAMETER_ORDER = PARAMETER_NAMES + ("SO3_connection", "BF_three_form")
PRIMARY_THETA = np.asarray([0.29, 0.24, 0.33, 0.41, 0.46, 0.38], dtype=float)
PROFILE_ORDER = (
    "Y", "Y_t", "Y_x", "Y_tt", "Y_xx", "Y_tx",
    "dY", "dY_t", "dY_x", "dY_tt", "dY_xx", "dY_tx",
)
PRIMARY_PROFILE_SAMPLE_SHA256 = "dcde57d89fad5488150ec3a6330bc2675ad75113ae02c5e1ce5567e054177c71"
PRIMARY_PROFILES_AST_SHA256 = "56b0036f22b80493291f1139948d749e0ddf16abb0ad11634a4ef7df2c05ebe2"
PRIMARY_SCOPE = {
    "ordinary_coordinate_dependence": {"q": True, "t": True, "x": True, "y": False, "z": False},
    "all_five_ordinary_coordinate_derivatives_active": False,
    "full_5D_coordinate_family_claimed": False,
}
COMPLEX_STEP = 1.0e-30
CENTRAL_STEP = 2.0e-5
WARD_STEP = 2.0e-5

FAIL_CLOSED_KEYS = (
    "passive_Phase_A_J_disengaged_pass",
    "LOCK_1_contamination_cleared_pass",
    "publication_authorized",
    "unrestricted_large_gauge_sector_pass",
    "C1_ACTION_selected_family_pass",
    "N1_ACTION_selected_family_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "full_variational_principle_pass",
    "two_sided_distinct_R_plus_R_minus_execution_pass",
    "non_Z2_two_sided_interface_pass",
    "two_sided_groupoid_master_integration_pass",
    "complete_same_action_SO3_Ward_pass",
    "same_action_bulk_embedding_interface_Euler_Green_pass",
    "independent_redteam_replication_pass",
    "continuum_convergence_pass",
    "BV_BFV_interface_completion_pass",
    "C1_pass",
    "N1_pass",
    "C1_N1_promotion_pass",
    "B4_pass",
    "B5_pass",
)


class RobinFrameGroupoidError(ValueError):
    """A source pin or a local mathematical invariant failed closed."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_v52_robin_contract() -> dict[str, Any]:
    paths = {
        "artifact": V52_ARTIFACT,
        "generator": V52_GENERATOR,
        "test": V52_TEST,
    }
    actual = {name: _sha256(path) for name, path in paths.items()}
    if actual != V52_PINS:
        raise RobinFrameGroupoidError(f"v5.2 source drift: {actual}")
    payload = json.loads(V52_ARTIFACT.read_text(encoding="utf-8"))
    try:
        charter = payload["exact_classical_charter"]
        literal = charter["exact_action"]["Robin_intrinsic"]
        coefficients = charter["coefficient_policy"]["parameters"]
    except (KeyError, TypeError) as exc:
        raise RobinFrameGroupoidError("v5.2 Robin contract is absent") from exc
    if literal != ROBIN_LITERAL:
        raise RobinFrameGroupoidError("v5.2 Robin action literal drift")
    expected = {
        "Robin_kappa_hat": KAPPA,
        "Robin_y": ROBIN_Y,
        "Robin_y_squared": 3.0,
    }
    if any(float(coefficients[key]) != value for key, value in expected.items()):
        raise RobinFrameGroupoidError("v5.2 Robin coefficient drift")
    return {
        "schema": payload.get("schema"),
        "paths": {name: str(path.relative_to(REPO)) for name, path in paths.items()},
        "sha256": actual,
        "literal": literal,
        "coefficients": expected,
        "decision_boolean_consumed": False,
        "Eulerian_or_residual_consumed": False,
    }


V52_CONTRACT = _load_v52_robin_contract()


def _load_primary_v562_contract() -> dict[str, Any]:
    """Pin identity/scope inputs without consuming a decision or Eulerian."""

    paths = {
        "artifact": V562_ARTIFACT,
        "generator": V562_GENERATOR,
        "test": V562_TEST,
    }
    actual = {name: _sha256(path) for name, path in paths.items()}
    if actual != V562_PINS:
        raise RobinFrameGroupoidError(f"primary v5.6.2 source drift: {actual}")
    payload = json.loads(V562_ARTIFACT.read_text(encoding="utf-8"))
    if payload.get("schema") != V562_SCHEMA:
        raise RobinFrameGroupoidError("primary v5.6.2 schema drift")
    try:
        scientific = payload["scientific"]
        parameter_order = tuple(scientific["parameter_order"])
        theta = np.asarray(scientific["theta"], dtype=float)
        field_activity = scientific["field_activity"]
        scope = {
            "ordinary_coordinate_dependence": field_activity["ordinary_coordinate_dependence"],
            "all_five_ordinary_coordinate_derivatives_active": field_activity[
                "all_five_ordinary_coordinate_derivatives_active"
            ],
            "full_5D_coordinate_family_claimed": field_activity[
                "full_5D_coordinate_family_claimed"
            ],
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise RobinFrameGroupoidError("primary v5.6.2 family contract is absent") from exc
    if parameter_order != PRIMARY_PARAMETER_ORDER:
        raise RobinFrameGroupoidError("primary v5.6.2 parameter order drift")
    if theta.shape != PRIMARY_THETA.shape or not np.array_equal(theta, PRIMARY_THETA):
        raise RobinFrameGroupoidError("primary v5.6.2 theta drift")
    if scope != PRIMARY_SCOPE:
        raise RobinFrameGroupoidError("primary v5.6.2 coordinate scope drift")
    tree = ast.parse(V562_GENERATOR.read_text(encoding="utf-8"))
    profile_nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_profiles"
    ]
    if len(profile_nodes) != 1:
        raise RobinFrameGroupoidError("primary v5.6.2 _profiles definition is not unique")
    profile_ast_sha256 = hashlib.sha256(
        ast.dump(
            profile_nodes[0], annotate_fields=True, include_attributes=False
        ).encode("utf-8")
    ).hexdigest()
    if profile_ast_sha256 != PRIMARY_PROFILES_AST_SHA256:
        raise RobinFrameGroupoidError("primary v5.6.2 _profiles AST drift")
    return {
        "schema": payload["schema"],
        "paths": {name: str(path.relative_to(REPO)) for name, path in paths.items()},
        "sha256": actual,
        "parameter_order": list(parameter_order),
        "theta": theta.tolist(),
        "scope": scope,
        "profiles_AST_sha256": profile_ast_sha256,
        "profiles_AST_executed": False,
        "decision_boolean_consumed": False,
        "Eulerian_or_residual_consumed": False,
        "primary_helper_imported_or_called": False,
    }


PRIMARY_V562_CONTRACT = _load_primary_v562_contract()


def _grid() -> tuple[np.ndarray, np.ndarray]:
    t_axis = np.linspace(0.0, 2.0 * math.pi, T_POINTS, endpoint=False)[:, None]
    x_axis = np.linspace(0.0, 2.0 * math.pi, X_POINTS, endpoint=False)[None, :]
    shape = (T_POINTS, X_POINTS)
    return np.broadcast_to(t_axis, shape), np.broadcast_to(x_axis, shape)


def _profiles(t: np.ndarray, x: np.ndarray) -> dict[str, np.ndarray]:
    """Literal selected graph and tangent used by the v5.6.2 family."""

    u = 2.0 * t - x
    return {
        "Y": 0.16 + 0.055 * np.cos(t) + 0.071 * np.cos(x) + 0.031 * np.sin(t + x),
        "Y_t": -0.055 * np.sin(t) + 0.031 * np.cos(t + x),
        "Y_x": -0.071 * np.sin(x) + 0.031 * np.cos(t + x),
        "Y_tt": -0.055 * np.cos(t) - 0.031 * np.sin(t + x),
        "Y_xx": -0.071 * np.cos(x) - 0.031 * np.sin(t + x),
        "Y_tx": -0.031 * np.sin(t + x),
        "dY": 0.061 * np.sin(t) * np.cos(x) + 0.029 * np.cos(u),
        "dY_t": 0.061 * np.cos(t) * np.cos(x) - 0.058 * np.sin(u),
        "dY_x": -0.061 * np.sin(t) * np.sin(x) + 0.029 * np.sin(u),
        "dY_tt": -0.061 * np.sin(t) * np.cos(x) - 0.116 * np.cos(u),
        "dY_xx": -0.061 * np.sin(t) * np.cos(x) - 0.029 * np.cos(u),
        "dY_tx": -0.061 * np.cos(t) * np.sin(x) + 0.058 * np.cos(u),
    }


def _profile_sample_sha256(t: np.ndarray, x: np.ndarray) -> str:
    """Value-level fingerprint of the pinned selected graph contract."""

    profiles = _profiles(t, x)
    digest = hashlib.sha256()
    for name in PROFILE_ORDER:
        digest.update(name.encode("ascii") + b"\0")
        digest.update(np.ascontiguousarray(profiles[name], dtype="<f8").tobytes())
    return digest.hexdigest()


def _embedding(parameter: complex | float, t: np.ndarray, x: np.ndarray) -> dict[str, np.ndarray]:
    profiles = _profiles(t, x)
    return {
        name: profiles[name] + parameter * profiles[f"d{name}"]
        for name in ("Y", "Y_t", "Y_x", "Y_tt", "Y_xx", "Y_tx")
    }


def _inner(metric: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.einsum("...mn,...m,...n->...", metric, left, right)


def _chosen_coordinate_adapted_q_frame(
    gamma_cov: np.ndarray,
    u_cov: np.ndarray,
    u_contra: np.ndarray,
) -> np.ndarray:
    """A local Gram--Schmidt section of Fr^+_SO(H_(gamma,T)), not canonical."""

    shape = gamma_cov.shape[:-2]
    candidates = np.empty(shape + (4, 3), dtype=gamma_cov.dtype)
    for spatial in range(3):
        axis = spatial + 1
        coordinate_vector = np.zeros(4, dtype=gamma_cov.dtype)
        coordinate_vector[axis] = 1.0
        candidates[..., :, spatial] = (
            coordinate_vector + u_contra * u_cov[..., axis, None]
        )
    frame = np.empty_like(candidates)
    for column in range(3):
        vector = candidates[..., :, column].copy()
        for previous in range(column):
            projection = _inner(gamma_cov, frame[..., :, previous], vector)
            vector = vector - frame[..., :, previous] * projection[..., None]
        norm = np.sqrt(_inner(gamma_cov, vector, vector))
        frame[..., :, column] = vector / norm[..., None]
    return frame


def _induced_geometry(theta: np.ndarray) -> dict[str, np.ndarray]:
    """Induced graph metric, T=t foliation, frame, and acceleration."""

    theta = np.asarray(theta)
    if theta.shape != (4,):
        raise RobinFrameGroupoidError("expected four selected-family parameters")
    t, x = _grid()
    graph = _embedding(theta[0], t, x)
    y, yt, yx = graph["Y"], graph["Y_t"], graph["Y_x"]
    ytt, yxx, ytx = graph["Y_tt"], graph["Y_xx"], graph["Y_tx"]
    kappa = K_INFINITY * (1.0 + 0.12 * theta[1])
    radius = np.sqrt(y * y + WARP_CORE**2)
    warp_exponent = -kappa * radius
    warp = np.exp(warp_exponent)
    exponent_q = -kappa * y / radius
    warp_q = exponent_q * warp
    warp_t = warp_q * yt
    warp_x = warp_q * yx

    e_xx = warp * warp + yx * yx
    d = e_xx - yt * yt
    e_t = 2.0 * warp * warp_t + 2.0 * yx * ytx
    e_x = 2.0 * warp * warp_x + 2.0 * yx * yxx
    d_t = e_t - 2.0 * yt * ytt
    d_x = e_x - 2.0 * yt * ytx

    dtype = np.result_type(theta.dtype, np.float64)
    gamma_cov = np.zeros((T_POINTS, X_POINTS, 4, 4), dtype=dtype)
    gamma_cov[..., 0, 0] = -warp * warp + yt * yt
    gamma_cov[..., 0, 1] = yt * yx
    gamma_cov[..., 1, 0] = yt * yx
    gamma_cov[..., 1, 1] = e_xx
    gamma_cov[..., 2, 2] = warp * warp
    gamma_cov[..., 3, 3] = warp * warp
    gamma_inverse = np.linalg.inv(gamma_cov)

    # T=t, N_T=(-gamma^{mu nu} d_mu T d_nu T)^(-1/2).
    lapse = (-gamma_inverse[..., 0, 0]) ** -0.5
    u_cov = np.zeros((T_POINTS, X_POINTS, 4), dtype=dtype)
    u_cov[..., 0] = -lapse
    u_contra = np.einsum("...mn,...n->...m", gamma_inverse, u_cov)
    h_cov = gamma_cov + np.einsum("...m,...n->...mn", u_cov, u_cov)

    # For an adapted khronon foliation a_mu=h_mu^nu d_nu log N_T.
    log_lapse_t = warp_t / warp + 0.5 * d_t / d - 0.5 * e_t / e_xx
    log_lapse_x = warp_x / warp + 0.5 * d_x / d - 0.5 * e_x / e_xx
    gradient_log_lapse = np.zeros_like(u_cov)
    gradient_log_lapse[..., 0] = log_lapse_t
    gradient_log_lapse[..., 1] = log_lapse_x
    u_gradient = np.einsum("...m,...m->...", u_contra, gradient_log_lapse)
    acceleration_cov = gradient_log_lapse + u_cov * u_gradient[..., None]
    acceleration_contra = np.einsum(
        "...mn,...n->...m", gamma_inverse, acceleration_cov
    )
    frame = _chosen_coordinate_adapted_q_frame(gamma_cov, u_cov, u_contra)
    measure = np.sqrt(-np.linalg.det(gamma_cov))
    return {
        "t": t,
        "x": x,
        **graph,
        "warp": warp,
        "gamma_cov": gamma_cov,
        "gamma_inverse": gamma_inverse,
        "lapse": lapse,
        "u_cov": u_cov,
        "u_contra": u_contra,
        "h_cov": h_cov,
        "frame": frame,
        "acceleration_cov": acceleration_cov,
        "acceleration_contra": acceleration_contra,
        "measure": measure,
        "closed_form_measure": warp**3 * np.sqrt(d),
    }


def _rotation_x(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=angle.dtype)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 0, 0] = 1.0
    result[..., 1, 1] = c
    result[..., 1, 2] = -s
    result[..., 2, 1] = s
    result[..., 2, 2] = c
    return result


def _rotation_y(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=angle.dtype)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 0, 0] = c
    result[..., 0, 2] = s
    result[..., 1, 1] = 1.0
    result[..., 2, 0] = -s
    result[..., 2, 2] = c
    return result


def _rotation_z(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=angle.dtype)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 0, 0] = c
    result[..., 0, 1] = -s
    result[..., 1, 0] = s
    result[..., 1, 1] = c
    result[..., 2, 2] = 1.0
    return result


def _groupoid_r(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    alpha = 0.17 + 0.061 * np.sin(t) + 0.029 * np.cos(x)
    beta = -0.11 + 0.047 * np.cos(t + x)
    gamma = 0.13 + 0.037 * np.sin(t - 2.0 * x)
    return np.einsum(
        "...ij,...jk,...kl->...il",
        _rotation_z(gamma),
        _rotation_y(beta),
        _rotation_x(alpha),
    )


def _source_phi(theta: np.ndarray, geometry: Mapping[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    t, x, q = geometry["t"], geometry["x"], geometry["Y"]
    envelope = np.exp(-q * q / 9.0)
    omega_profile = (
        0.16 * envelope * np.cos(t)
        + 0.11 * np.sin(x)
        + 0.04 * q * np.sin(t + x)
        + 0.03 * np.cos(2.0 * t - x)
    )
    omega = np.exp(theta[2] * omega_profile)
    vector = np.stack(
        (
            0.72 + 0.11 * np.sin(t) + 0.045 * q + 0.018 * np.cos(t + x),
            0.28 * np.cos(x) + 0.065 * np.sin(q + t) + 0.025 * np.cos(t - x),
            0.24 * np.sin(t + x) + 0.052 * q * np.cos(x) + 0.021 * np.sin(2.0 * t - x),
        ),
        axis=-1,
    )
    phi = theta[3] * omega[..., None] ** -1.5 * vector
    return omega, phi


def _integral(value: np.ndarray) -> complex | float:
    """Integral over the t,x torus per unit coordinate y,z volume."""

    return (2.0 * math.pi) ** 2 * np.mean(value)


def _robin_from(
    geometry: Mapping[str, np.ndarray],
    frame: np.ndarray,
    varphi: np.ndarray,
) -> dict[str, np.ndarray | complex | float]:
    varphi_h = np.einsum("...ma,...a->...m", frame, varphi)
    residual = varphi_h - ROBIN_Y * geometry["acceleration_contra"]
    norm = np.einsum(
        "...mn,...m,...n->...", geometry["h_cov"], residual, residual
    )
    density = -0.5 * KAPPA * geometry["measure"] * norm
    return {
        "spacetime_varphi": varphi_h,
        "residual": residual,
        "norm": norm,
        "density": density,
        "action": _integral(density),
    }


def selected_state(theta: np.ndarray) -> dict[str, Any]:
    geometry = _induced_geometry(theta)
    omega, phi = _source_phi(np.asarray(theta), geometry)
    r_matrix = _groupoid_r(geometry["t"], geometry["x"])
    varphi = np.einsum("...ab,...b->...a", r_matrix, phi)
    robin = _robin_from(geometry, geometry["frame"], varphi)
    return {
        **geometry,
        "Omega": omega,
        "phi": phi,
        "R": r_matrix,
        "varphi": varphi,
        **robin,
    }


def _hat(vector: np.ndarray) -> np.ndarray:
    result = np.zeros(vector.shape[:-1] + (3, 3), dtype=vector.dtype)
    result[..., 0, 1] = -vector[..., 2]
    result[..., 0, 2] = vector[..., 1]
    result[..., 1, 0] = vector[..., 2]
    result[..., 1, 2] = -vector[..., 0]
    result[..., 2, 0] = -vector[..., 1]
    result[..., 2, 1] = vector[..., 0]
    return result


def _so3_exp(vector: np.ndarray, scale: float) -> np.ndarray:
    generator = _hat(vector)
    norm = np.sqrt(np.sum(vector * vector, axis=-1))
    if float(np.min(norm)) <= 1.0e-12:
        raise RobinFrameGroupoidError("gauge profile must be nonzero for Rodrigues")
    first = np.sin(scale * norm) / norm
    second = (1.0 - np.cos(scale * norm)) / (norm * norm)
    square = np.einsum("...ij,...jk->...ik", generator, generator)
    identity = np.broadcast_to(np.eye(3), generator.shape)
    return identity + first[..., None, None] * generator + second[..., None, None] * square


def _frame_invariants(state: Mapping[str, Any]) -> dict[str, float]:
    frame = state["frame"]
    gram = np.einsum(
        "...mn,...ma,...nb->...ab", state["gamma_cov"], frame, frame
    )
    spatial = np.einsum("...m,...ma->...a", state["u_cov"], frame)
    u_norm = np.einsum("...m,...m->...", state["u_cov"], state["u_contra"])
    a_spatial = np.einsum(
        "...m,...m->...", state["u_contra"], state["acceleration_cov"]
    )
    r_matrix = state["R"]
    r_gram = np.einsum("...ji,...jk->...ik", r_matrix, r_matrix)
    tetrad = np.concatenate((state["u_contra"][..., None], frame), axis=-1)
    oriented_volume = state["measure"] * np.linalg.det(tetrad)
    return {
        "frame_orthonormality_Linf": float(np.max(np.abs(gram - np.eye(3)))),
        "frame_spatiality_Linf": float(np.max(np.abs(spatial))),
        "khronon_unit_norm_Linf": float(np.max(np.abs(u_norm + 1.0))),
        "acceleration_spatiality_Linf": float(np.max(np.abs(a_spatial))),
        "measure_closed_form_Linf": float(
            np.max(np.abs(state["measure"] - state["closed_form_measure"]))
        ),
        "R_orthogonality_Linf": float(np.max(np.abs(r_gram - np.eye(3)))),
        "R_determinant_Linf": float(
            np.max(np.abs(np.linalg.det(r_matrix) - 1.0))
        ),
        "sqrt_minus_gamma_det_u_E_minus_one_Linf": float(
            np.max(np.abs(oriented_volume - 1.0))
        ),
    }


def _maximum_absolute(value: np.ndarray | complex | float) -> float:
    return float(np.max(np.abs(value)))


@lru_cache(maxsize=1)
def selected_family_jvp_fd_certificate() -> dict[str, Any]:
    basis = np.eye(4)
    directions = {
        name: basis[index] for index, name in enumerate(PARAMETER_NAMES)
    }
    directions["coupled"] = np.asarray([0.31, -0.27, 0.23, 0.37])
    compared = (
        "action",
        "measure",
        "frame",
        "acceleration_contra",
        "phi",
        "varphi",
        "residual",
        "density",
    )
    rows: dict[str, Any] = {}
    maximum_error = 0.0
    minimum_action_activity = math.inf
    for label, direction in directions.items():
        complex_theta = THETA.astype(complex) + 1j * COMPLEX_STEP * direction
        complex_state = selected_state(complex_theta)
        plus = selected_state(THETA + CENTRAL_STEP * direction)
        minus = selected_state(THETA - CENTRAL_STEP * direction)
        values: dict[str, Any] = {}
        for key in compared:
            complex_jvp = np.imag(complex_state[key]) / COMPLEX_STEP
            central_fd = (plus[key] - minus[key]) / (2.0 * CENTRAL_STEP)
            error = _maximum_absolute(complex_jvp - central_fd)
            maximum_error = max(maximum_error, error)
            values[key] = {
                "complex_step_JVP_Linf": _maximum_absolute(complex_jvp),
                "central_FD_Linf": _maximum_absolute(central_fd),
                "JVP_minus_FD_Linf": error,
            }
            if key == "action":
                values[key]["complex_step_JVP"] = float(complex_jvp)
                values[key]["central_FD"] = float(central_fd)
                minimum_action_activity = min(
                    minimum_action_activity, abs(float(complex_jvp))
                )
        rows[label] = {"direction": direction.tolist(), "raw": values}
    return {
        "parameter_order": list(PARAMETER_NAMES),
        "theta": THETA.tolist(),
        "complex_step": COMPLEX_STEP,
        "central_step": CENTRAL_STEP,
        "raw_rows": rows,
        "maximum_raw_JVP_FD_error": maximum_error,
        "minimum_absolute_action_JVP": minimum_action_activity,
        "scope": "Robin term only; selected analytic t,x-dependent family per unit y,z volume",
        "routes_share_same_literal_action_evaluator": True,
        "independent_action_reconstruction_claimed": False,
        "interpretation": (
            "Complex-step and central FD independently probe differentiation, but both evaluate the same local "
            "Robin implementation; their agreement is not an independent rederivation of the action."
        ),
    }


def _primary_fixed_axis_robin_action(theta: np.ndarray) -> complex | float:
    """Reconstruct the primary R=I component expression."""

    state = selected_state(theta)
    acceleration_components = np.einsum(
        "...ma,...m->...a", state["frame"], state["acceleration_cov"]
    )
    fixed_axis_residual = state["phi"] - ROBIN_Y * acceleration_components
    fixed_axis_norm = np.sum(fixed_axis_residual * fixed_axis_residual, axis=-1)
    return _integral(-0.5 * KAPPA * state["measure"] * fixed_axis_norm)


def _identity_solder_robin_action(theta: np.ndarray) -> complex | float:
    """Evaluate the covariant E_Q R phi expression in the aligned R=I section."""

    state = selected_state(theta)
    return _robin_from(state, state["frame"], state["phi"])["action"]


@lru_cache(maxsize=1)
def primary_robin_alignment_certificate() -> dict[str, Any]:
    """Separate R=I action agreement from the primary's missing orbit variation."""

    state = selected_state(THETA)
    nontrivial_r_action = float(state["action"])
    identity_solder_action = float(_identity_solder_robin_action(THETA))
    fixed_axis_action = float(_primary_fixed_axis_robin_action(THETA))
    directions = {
        name: np.eye(4)[index] for index, name in enumerate(PARAMETER_NAMES)
    }
    directions["coupled"] = np.asarray([0.31, -0.27, 0.23, 0.37])
    rows: dict[str, Any] = {}
    maximum_aligned_jvp_difference = 0.0
    maximum_nontrivial_configuration_jvp_difference = 0.0
    for name, direction in directions.items():
        complex_theta = THETA.astype(complex) + 1j * COMPLEX_STEP * direction
        nontrivial_r_jvp = float(
            np.imag(selected_state(complex_theta)["action"]) / COMPLEX_STEP
        )
        identity_solder_jvp = float(
            np.imag(_identity_solder_robin_action(complex_theta)) / COMPLEX_STEP
        )
        fixed_axis_jvp = float(
            np.imag(_primary_fixed_axis_robin_action(complex_theta)) / COMPLEX_STEP
        )
        aligned_difference = identity_solder_jvp - fixed_axis_jvp
        configuration_difference = nontrivial_r_jvp - fixed_axis_jvp
        rows[name] = {
            "nontrivial_R_groupoid_JVP": nontrivial_r_jvp,
            "aligned_R_identity_groupoid_JVP": identity_solder_jvp,
            "primary_fixed_axis_JVP": fixed_axis_jvp,
            "aligned_R_identity_minus_primary": aligned_difference,
            "nontrivial_R_minus_primary_configuration_difference": configuration_difference,
        }
        maximum_aligned_jvp_difference = max(
            maximum_aligned_jvp_difference, abs(aligned_difference)
        )
        maximum_nontrivial_configuration_jvp_difference = max(
            maximum_nontrivial_configuration_jvp_difference,
            abs(configuration_difference),
        )
    return {
        "aligned_R_identity_action_compatible": True,
        "primary_section": "R=I with the chosen coordinate-adapted Q-frame",
        "aligned_R_identity_action": identity_solder_action,
        "primary_fixed_axis_action": fixed_axis_action,
        "aligned_R_identity_minus_primary_action": identity_solder_action - fixed_axis_action,
        "nontrivial_R_action": nontrivial_r_action,
        "nontrivial_R_minus_primary_configuration_difference": nontrivial_r_action - fixed_axis_action,
        "raw_directional_JVPs": rows,
        "maximum_absolute_aligned_R_identity_JVP_difference": maximum_aligned_jvp_difference,
        "maximum_absolute_nontrivial_R_configuration_JVP_difference": (
            maximum_nontrivial_configuration_jvp_difference
        ),
        "consequence": (
            "The primary value/JVP is the aligned R=I section of the same Robin action. Its failure was orbital: "
            "varying phi while freezing R/frame is the omit-delta-R mutant. The full same-action Ward and affected "
            "variations still require reassembly and rederivation rather than Boolean composition."
        ),
    }


def _source_lambda(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.stack(
        (
            0.37 + 0.09 * np.sin(t) + 0.04 * np.cos(x),
            -0.23 + 0.07 * np.cos(t + x),
            0.19 + 0.05 * np.sin(t - 2.0 * x),
        ),
        axis=-1,
    )


def _target_q(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.stack(
        (
            -0.29 + 0.06 * np.cos(t),
            0.31 + 0.08 * np.sin(x),
            0.17 + 0.05 * np.cos(t - x),
        ),
        axis=-1,
    )


def _fixed_geometry_robin_action(
    state: Mapping[str, Any], frame: np.ndarray, varphi: np.ndarray
) -> float:
    return float(np.real(_robin_from(state, frame, varphi)["action"]))


@lru_cache(maxsize=1)
def source_p_groupoid_ward_certificate() -> dict[str, Any]:
    state = selected_state(THETA)
    lam = _source_lambda(state["t"], state["x"])
    generator = _hat(lam)
    delta_phi = np.einsum("...ab,...b->...a", generator, state["phi"])
    delta_r = -np.einsum("...ab,...bc->...ac", state["R"], generator)
    delta_varphi = (
        np.einsum("...ab,...b->...a", delta_r, state["phi"])
        + np.einsum("...ab,...b->...a", state["R"], delta_phi)
    )
    omit_delta_r_direction = np.einsum(
        "...ab,...b->...a", state["R"], delta_phi
    )
    left_delta_r = -np.einsum("...ab,...bc->...ac", generator, state["R"])
    left_direction = (
        np.einsum("...ab,...b->...a", left_delta_r, state["phi"])
        + np.einsum("...ab,...b->...a", state["R"], delta_phi)
    )
    wrong_sign_delta_r = np.einsum(
        "...ab,...bc->...ac", state["R"], generator
    )
    wrong_sign_direction = (
        np.einsum("...ab,...b->...a", wrong_sign_delta_r, state["phi"])
        + np.einsum("...ab,...b->...a", state["R"], delta_phi)
    )
    residual_cov = np.einsum(
        "...mn,...n->...m", state["h_cov"], state["residual"]
    )

    def pairing(direction: np.ndarray) -> float:
        delta_spacetime = np.einsum(
            "...ma,...a->...m", state["frame"], direction
        )
        density = -KAPPA * state["measure"] * np.einsum(
            "...m,...m->...", residual_cov, delta_spacetime
        )
        return float(np.real(_integral(density)))

    def transformed_action(scale: float, mode: str) -> tuple[float, np.ndarray]:
        gauge = _so3_exp(lam, scale)
        moved_phi = np.einsum("...ab,...b->...a", gauge, state["phi"])
        if mode == "correct_right_inverse":
            moved_r = np.einsum("...ab,...cb->...ac", state["R"], gauge)
        elif mode == "omit_delta_R":
            moved_r = state["R"]
        elif mode == "wrong_left_inverse":
            moved_r = np.einsum("...ba,...bc->...ac", gauge, state["R"])
        elif mode == "wrong_sign_right":
            moved_r = np.einsum("...ab,...bc->...ac", state["R"], gauge)
        else:
            raise RobinFrameGroupoidError(f"unknown source Ward mode: {mode}")
        moved_varphi = np.einsum("...ab,...b->...a", moved_r, moved_phi)
        return (
            _fixed_geometry_robin_action(state, state["frame"], moved_varphi),
            moved_varphi,
        )

    plus, plus_varphi = transformed_action(WARD_STEP, "correct_right_inverse")
    minus, minus_varphi = transformed_action(-WARD_STEP, "correct_right_inverse")
    direct = (plus - minus) / (2.0 * WARD_STEP)
    euler = pairing(delta_varphi)
    mutant_rows: dict[str, Any] = {}
    mutant_directions = {
        "omit_delta_R": omit_delta_r_direction,
        "wrong_left_compensation": left_direction,
        "wrong_source_sign": wrong_sign_direction,
    }
    for name, direction in mutant_directions.items():
        mutant_plus, _ = transformed_action(WARD_STEP, name if name == "omit_delta_R" else (
            "wrong_left_inverse" if name == "wrong_left_compensation" else "wrong_sign_right"
        ))
        mutant_minus, _ = transformed_action(-WARD_STEP, name if name == "omit_delta_R" else (
            "wrong_left_inverse" if name == "wrong_left_compensation" else "wrong_sign_right"
        ))
        mutant_direct = (mutant_plus - mutant_minus) / (2.0 * WARD_STEP)
        mutant_euler = pairing(direction)
        mutant_rows[name] = {
            "central_direct_derivative": mutant_direct,
            "Euler_pairing": mutant_euler,
            "direct_minus_Euler": mutant_direct - mutant_euler,
            "delta_varphi_Linf": _maximum_absolute(direction),
        }
    finite_scale_action, finite_scale_varphi = transformed_action(
        0.23, "correct_right_inverse"
    )
    nominal_action = float(state["action"])
    return {
        "convention": {
            "hat_lambda_v": "lambda cross v",
            "delta_phi": "hat(lambda) phi",
            "delta_R": "-R hat(lambda)",
            "varphi": "R phi",
            "delta_varphi": "delta_R phi + R delta_phi = 0",
            "Q_frame_held_fixed": True,
        },
        "raw": {
            "delta_varphi_Linf": _maximum_absolute(delta_varphi),
            "central_direct_Robin_derivative": direct,
            "Euler_pairing": euler,
            "direct_minus_Euler": direct - euler,
            "finite_source_gauge_action_difference_at_scale_0_23": finite_scale_action - nominal_action,
            "finite_source_gauge_varphi_Linf": _maximum_absolute(finite_scale_varphi - state["varphi"]),
            "central_varphi_plus_minus_Linf": _maximum_absolute(plus_varphi - minus_varphi),
            "mutants": mutant_rows,
        },
    }


@lru_cache(maxsize=1)
def target_q_frame_ward_certificate() -> dict[str, Any]:
    state = selected_state(THETA)
    q_parameter = _target_q(state["t"], state["x"])
    generator = _hat(q_parameter)
    delta_r = np.einsum("...ab,...bc->...ac", generator, state["R"])
    delta_varphi = np.einsum("...ab,...b->...a", delta_r, state["phi"])
    expected_delta_varphi = np.einsum(
        "...ab,...b->...a", generator, state["varphi"]
    )
    delta_frame = -np.einsum(
        "...ma,...ab->...mb", state["frame"], generator
    )
    delta_spacetime = (
        np.einsum("...ma,...a->...m", delta_frame, state["varphi"])
        + np.einsum("...ma,...a->...m", state["frame"], delta_varphi)
    )
    fixed_frame_delta_spacetime = np.einsum(
        "...ma,...a->...m", state["frame"], delta_varphi
    )
    wrong_sign_delta_frame = np.einsum(
        "...ma,...ab->...mb", state["frame"], generator
    )
    wrong_sign_delta_spacetime = (
        np.einsum(
            "...ma,...a->...m", wrong_sign_delta_frame, state["varphi"]
        )
        + fixed_frame_delta_spacetime
    )
    residual_cov = np.einsum(
        "...mn,...n->...m", state["h_cov"], state["residual"]
    )

    def pairing(direction: np.ndarray) -> float:
        density = -KAPPA * state["measure"] * np.einsum(
            "...m,...m->...", residual_cov, direction
        )
        return float(np.real(_integral(density)))

    def transformed_action(
        scale: float, frame_mode: str
    ) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
        gauge = _so3_exp(q_parameter, scale)
        moved_r = np.einsum("...ab,...bc->...ac", gauge, state["R"])
        moved_varphi = np.einsum("...ab,...b->...a", moved_r, state["phi"])
        if frame_mode == "correct_inverse":
            moved_frame = np.einsum(
                "...ma,...ba->...mb", state["frame"], gauge
            )
        elif frame_mode == "fixed_frame":
            moved_frame = state["frame"]
        elif frame_mode == "wrong_frame_sign":
            moved_frame = np.einsum(
                "...ma,...ab->...mb", state["frame"], gauge
            )
        else:
            raise RobinFrameGroupoidError(f"unknown target Ward mode: {frame_mode}")
        return (
            _fixed_geometry_robin_action(state, moved_frame, moved_varphi),
            moved_frame,
            moved_varphi,
            moved_r,
        )

    plus, _, _, _ = transformed_action(WARD_STEP, "correct_inverse")
    minus, _, _, _ = transformed_action(-WARD_STEP, "correct_inverse")
    direct = (plus - minus) / (2.0 * WARD_STEP)
    euler = pairing(delta_spacetime)
    mutant_rows: dict[str, Any] = {}
    for name, frame_mode, direction in (
        ("fixed_frame", "fixed_frame", fixed_frame_delta_spacetime),
        ("wrong_target_frame_sign", "wrong_frame_sign", wrong_sign_delta_spacetime),
    ):
        mutant_plus, _, _, _ = transformed_action(WARD_STEP, frame_mode)
        mutant_minus, _, _, _ = transformed_action(-WARD_STEP, frame_mode)
        mutant_direct = (mutant_plus - mutant_minus) / (2.0 * WARD_STEP)
        mutant_euler = pairing(direction)
        mutant_rows[name] = {
            "central_direct_derivative": mutant_direct,
            "Euler_pairing": mutant_euler,
            "direct_minus_Euler": mutant_direct - mutant_euler,
            "delta_spacetime_varphi_Linf": _maximum_absolute(direction),
        }
    finite_action, finite_frame, finite_varphi, finite_r = transformed_action(
        0.19, "correct_inverse"
    )
    finite_gram = np.einsum(
        "...mn,...ma,...nb->...ab",
        state["gamma_cov"],
        finite_frame,
        finite_frame,
    )
    finite_spacetime = np.einsum(
        "...ma,...a->...m", finite_frame, finite_varphi
    )
    return {
        "convention": {
            "R_target_action": "R -> g_Q R",
            "derived_varphi": "varphi'=(g_Q R)phi=g_Q varphi",
            "delta_varphi": "hat(q) varphi",
            "delta_E_Q": "-E_Q hat(q)",
            "derived_delta_varphi_H": "delta_E_Q varphi + E_Q delta_varphi = 0",
            "gamma_and_T_held_fixed": True,
            "interpretation": "vertical Aut(Q) change of the representative of Fr^+_SO(H_(gamma,T))",
        },
        "raw": {
            "delta_R_phi_minus_hat_q_varphi_Linf": _maximum_absolute(
                delta_varphi - expected_delta_varphi
            ),
            "delta_spacetime_varphi_Linf": _maximum_absolute(delta_spacetime),
            "central_direct_Robin_derivative": direct,
            "Euler_pairing": euler,
            "direct_minus_Euler": direct - euler,
            "finite_target_gauge_action_difference_at_scale_0_19": finite_action - float(state["action"]),
            "finite_target_gauge_spacetime_varphi_Linf": _maximum_absolute(finite_spacetime - state["spacetime_varphi"]),
            "finite_target_gauge_frame_orthonormality_Linf": _maximum_absolute(finite_gram - np.eye(3)),
            "finite_R_minus_gQ_R_Linf": _maximum_absolute(
                finite_r
                - np.einsum(
                    "...ab,...bc->...ac",
                    _so3_exp(q_parameter, 0.19),
                    state["R"],
                )
            ),
            "mutants": mutant_rows,
        },
    }


@lru_cache(maxsize=1)
def combined_p_q_groupoid_ward_certificate() -> dict[str, Any]:
    """Simultaneous finite and infinitesimal P x Q action on E R phi."""

    state = selected_state(THETA)
    lam = _source_lambda(state["t"], state["x"])
    q_parameter = _target_q(state["t"], state["x"])
    source_generator = _hat(lam)
    target_generator = _hat(q_parameter)
    delta_phi = np.einsum(
        "...ab,...b->...a", source_generator, state["phi"]
    )
    delta_r = (
        np.einsum("...ab,...bc->...ac", target_generator, state["R"])
        - np.einsum("...ab,...bc->...ac", state["R"], source_generator)
    )
    delta_frame = -np.einsum(
        "...ma,...ab->...mb", state["frame"], target_generator
    )
    delta_spacetime = (
        np.einsum(
            "...ma,...ab,...b->...m",
            delta_frame,
            state["R"],
            state["phi"],
        )
        + np.einsum(
            "...ma,...ab,...b->...m",
            state["frame"],
            delta_r,
            state["phi"],
        )
        + np.einsum(
            "...ma,...ab,...b->...m",
            state["frame"],
            state["R"],
            delta_phi,
        )
    )
    wrong_inverse_delta_r = (
        -np.einsum("...ab,...bc->...ac", target_generator, state["R"])
        - np.einsum("...ab,...bc->...ac", state["R"], source_generator)
    )
    wrong_inverse_delta_spacetime = (
        np.einsum(
            "...ma,...ab,...b->...m",
            delta_frame,
            state["R"],
            state["phi"],
        )
        + np.einsum(
            "...ma,...ab,...b->...m",
            state["frame"],
            wrong_inverse_delta_r,
            state["phi"],
        )
        + np.einsum(
            "...ma,...ab,...b->...m",
            state["frame"],
            state["R"],
            delta_phi,
        )
    )
    residual_cov = np.einsum(
        "...mn,...n->...m", state["h_cov"], state["residual"]
    )

    def pairing(direction: np.ndarray) -> float:
        density = -KAPPA * state["measure"] * np.einsum(
            "...m,...m->...", residual_cov, direction
        )
        return float(np.real(_integral(density)))

    def transformed_action(
        scale: float, *, inverse_target_on_r: bool
    ) -> tuple[float, np.ndarray]:
        source_gauge = _so3_exp(lam, scale)
        target_gauge = _so3_exp(q_parameter, scale)
        moved_phi = np.einsum(
            "...ab,...b->...a", source_gauge, state["phi"]
        )
        target_factor = (
            np.swapaxes(target_gauge, -1, -2)
            if inverse_target_on_r
            else target_gauge
        )
        moved_r = np.einsum(
            "...ab,...bc,...dc->...ad",
            target_factor,
            state["R"],
            source_gauge,
        )
        moved_frame = np.einsum(
            "...ma,...ba->...mb", state["frame"], target_gauge
        )
        moved_varphi = np.einsum("...ab,...b->...a", moved_r, moved_phi)
        moved_spacetime = np.einsum(
            "...ma,...a->...m", moved_frame, moved_varphi
        )
        return (
            _fixed_geometry_robin_action(state, moved_frame, moved_varphi),
            moved_spacetime,
        )

    plus, _ = transformed_action(WARD_STEP, inverse_target_on_r=False)
    minus, _ = transformed_action(-WARD_STEP, inverse_target_on_r=False)
    direct = (plus - minus) / (2.0 * WARD_STEP)
    euler = pairing(delta_spacetime)
    mutant_plus, _ = transformed_action(WARD_STEP, inverse_target_on_r=True)
    mutant_minus, _ = transformed_action(-WARD_STEP, inverse_target_on_r=True)
    mutant_direct = (mutant_plus - mutant_minus) / (2.0 * WARD_STEP)
    mutant_euler = pairing(wrong_inverse_delta_spacetime)
    finite_action, finite_spacetime = transformed_action(
        0.17, inverse_target_on_r=False
    )
    return {
        "convention": {
            "finite": "phi'=g_P phi; R'=g_Q R g_P^-1; E'=E g_Q^-1",
            "infinitesimal": (
                "delta phi=hat(lambda)phi; delta R=hat(q)R-Rhat(lambda); "
                "delta E=-Ehat(q)"
            ),
            "derived_identity": "delta(E R phi)=0",
        },
        "raw": {
            "delta_E_R_phi_Linf": _maximum_absolute(delta_spacetime),
            "central_direct_Robin_derivative": direct,
            "Euler_pairing": euler,
            "direct_minus_Euler": direct - euler,
            "finite_combined_action_difference_at_scale_0_17": finite_action - float(state["action"]),
            "finite_combined_spacetime_varphi_Linf": _maximum_absolute(
                finite_spacetime - state["spacetime_varphi"]
            ),
            "target_inverse_R_mutant": {
                "finite_rule": "R'=g_Q^-1 R g_P^-1",
                "central_direct_derivative": mutant_direct,
                "Euler_pairing": mutant_euler,
                "direct_minus_Euler": mutant_direct - mutant_euler,
                "delta_E_R_phi_Linf": _maximum_absolute(
                    wrong_inverse_delta_spacetime
                ),
            },
        },
    }


def build_payload() -> dict[str, Any]:
    state = selected_state(THETA)
    frame = _frame_invariants(state)
    jvp = selected_family_jvp_fd_certificate()
    alignment = primary_robin_alignment_certificate()
    source = source_p_groupoid_ward_certificate()
    target = target_q_frame_ward_certificate()
    combined = combined_p_q_groupoid_ward_certificate()
    source_raw = source["raw"]
    target_raw = target["raw"]
    combined_raw = combined["raw"]
    profile_hash = _profile_sample_sha256(state["t"], state["x"])
    source_mutants = source_raw["mutants"]
    target_mutants = target_raw["mutants"]

    def mutant_closes(row: Mapping[str, Any]) -> bool:
        return (
            abs(row["central_direct_derivative"]) > 1.0e-5
            and abs(row["central_direct_derivative"] - row["Euler_pairing"])
            < 2.0e-8
        )

    checks = {
        "v5_2_Robin_literal_and_coefficients_pinned_pass": True,
        "primary_v5_6_2_bytes_theta_profiles_scope_pinned_pass": (
            PRIMARY_V562_CONTRACT["decision_boolean_consumed"] is False
            and PRIMARY_V562_CONTRACT["Eulerian_or_residual_consumed"] is False
            and PRIMARY_V562_CONTRACT["primary_helper_imported_or_called"] is False
            and PRIMARY_V562_CONTRACT["profiles_AST_executed"] is False
            and PRIMARY_V562_CONTRACT["profiles_AST_sha256"]
            == PRIMARY_PROFILES_AST_SHA256
            and tuple(PRIMARY_V562_CONTRACT["parameter_order"])
            == PRIMARY_PARAMETER_ORDER
            and np.array_equal(
                np.asarray(PRIMARY_V562_CONTRACT["theta"]), PRIMARY_THETA
            )
            and np.array_equal(THETA, PRIMARY_THETA[:4])
            and PRIMARY_V562_CONTRACT["scope"] == PRIMARY_SCOPE
            and profile_hash == PRIMARY_PROFILE_SAMPLE_SHA256
        ),
        "primary_R_identity_Robin_value_and_JVP_alignment_pass": (
            alignment["aligned_R_identity_action_compatible"] is True
            and abs(alignment["aligned_R_identity_minus_primary_action"])
            < 2.0e-12
            and alignment["maximum_absolute_aligned_R_identity_JVP_difference"]
            < 2.0e-10
            and abs(
                alignment[
                    "nontrivial_R_minus_primary_configuration_difference"
                ]
            )
            > 1.0e-5
        ),
        "chosen_coordinate_adapted_Q_frame_from_induced_gamma_T_pass": (
            max(frame.values()) < 2.0e-12
        ),
        "selected_Robin_metric_embedding_Omega_matter_JVP_FD_pass": (
            jvp["maximum_raw_JVP_FD_error"] < 2.0e-7
            and jvp["minimum_absolute_action_JVP"] > 1.0e-5
        ),
        "source_P_groupoid_Robin_Ward_pass": (
            source_raw["delta_varphi_Linf"] < 2.0e-13
            and abs(source_raw["central_direct_Robin_derivative"]) < 2.0e-9
            and abs(source_raw["Euler_pairing"]) < 2.0e-12
            and abs(source_raw["finite_source_gauge_action_difference_at_scale_0_23"]) < 2.0e-12
            and all(mutant_closes(row) for row in source_mutants.values())
        ),
        "target_Q_frame_Robin_Ward_pass": (
            target_raw["delta_R_phi_minus_hat_q_varphi_Linf"] < 2.0e-13
            and target_raw["delta_spacetime_varphi_Linf"] < 2.0e-13
            and abs(target_raw["central_direct_Robin_derivative"]) < 2.0e-9
            and abs(target_raw["Euler_pairing"]) < 2.0e-12
            and abs(target_raw["finite_target_gauge_action_difference_at_scale_0_19"]) < 2.0e-12
            and target_raw["finite_R_minus_gQ_R_Linf"] < 2.0e-13
            and all(mutant_closes(row) for row in target_mutants.values())
        ),
        "combined_P_Q_groupoid_Robin_Ward_pass": (
            combined_raw["delta_E_R_phi_Linf"] < 2.0e-13
            and abs(combined_raw["central_direct_Robin_derivative"]) < 2.0e-9
            and abs(combined_raw["Euler_pairing"]) < 2.0e-12
            and abs(combined_raw["finite_combined_action_difference_at_scale_0_17"])
            < 2.0e-12
            and combined_raw["finite_combined_spacetime_varphi_Linf"] < 2.0e-13
            and mutant_closes(combined_raw["target_inverse_R_mutant"])
        ),
        "required_Robin_groupoid_mutants_rejected_pass": (
            all(mutant_closes(row) for row in source_mutants.values())
            and all(mutant_closes(row) for row in target_mutants.values())
            and mutant_closes(combined_raw["target_inverse_R_mutant"])
        ),
    }
    for key in FAIL_CLOSED_KEYS:
        checks[key] = False
    if not all(value is True for key, value in checks.items() if key not in FAIL_CLOSED_KEYS):
        raise RobinFrameGroupoidError("one or more local Robin corrective checks failed")
    if any(checks[key] for key in FAIL_CLOSED_KEYS):
        raise RobinFrameGroupoidError("a promotion/global key escaped fail-closed status")
    generator_hash = _sha256(Path(__file__).resolve())
    test_hash = _sha256(TEST) if TEST.exists() else None
    return {
        "schema": SCHEMA,
        "classification": "LOCAL_ROBIN_FRAME_GROUPOID_SUBLEMMA_PASS__PRIMARY_R_IDENTITY_ALIGNED__PRIMARY_ORBIT_INCOMPLETE__C1_N1_FAIL_CLOSED",
        "claim": (
            "On one chosen coordinate-adapted local Q-frame section, the corrected literal v5.2 intrinsic Robin "
            "term closes pointwise under separate and combined finite/infinitesimal P x Q groupoid actions."
        ),
        "claim_limit": (
            "This is only a local Robin corrective sublemma on the selected family per unit homogeneous y,z volume. "
            "The pinned primary v5.6.2 value/JVP is the aligned R=I section, but its orbit froze R/frame. "
            "JVP/FD shares one action evaluator. "
            "Neither result is a full variational principle, same-action Ward, C1/N1 promotion, or B4/B5 result."
        ),
        "literal_input": {
            "v5_2_Robin_contract": V52_CONTRACT,
            "primary_v5_6_2_identity_and_scope_pin_only": PRIMARY_V562_CONTRACT,
            "primary_consumption_boundary": (
                "The primary bytes are consumed only to bind identity, theta and declared coordinate scope. "
                "No decision, Eulerian, residual or helper is consumed. The R=I value/JVP alignment is checked "
                "separately from the primary's incomplete orbit."
            ),
        },
        "primary_v5_6_2_family_contract": {
            "profile_order": list(PROFILE_ORDER),
            "profile_sample_sha256": profile_hash,
            "expected_profile_sample_sha256": PRIMARY_PROFILE_SAMPLE_SHA256,
            "primary_profiles_AST_sha256": PRIMARY_V562_CONTRACT[
                "profiles_AST_sha256"
            ],
            "primary_parameter_order": list(PRIMARY_PARAMETER_ORDER),
            "primary_theta": PRIMARY_THETA.tolist(),
            "sublemma_parameter_prefix": list(PARAMETER_NAMES),
            "sublemma_theta_prefix": THETA.tolist(),
            "scope": PRIMARY_SCOPE,
            "scope_relation": (
                "Same t,x,q-dependent trace family and homogeneous y,z sector; this sublemma explicitly reports "
                "per-unit y,z volume and does not claim a full 5D coordinate family."
            ),
        },
        "primary_R_identity_alignment_and_orbit_gap": alignment,
        "two_sided_master_contract_not_executed": {
            "bundles": "P_+|Sigma and P_-|Sigma map independently to Q=Fr^+_SO(H_(gamma,T))",
            "solders": "varphi_+=R_+ phi_+ and varphi_-=R_- phi_-",
            "finite_action": (
                "phi_+'=g_+ phi_+; phi_-'=g_- phi_-; "
                "R_+'=g_Q R_+ g_+^-1; R_-'=g_Q R_- g_-^-1; E'=E g_Q^-1"
            ),
            "gluing_equation_if_imposed": "R_+ phi_+=R_- phi_-=varphi_H in Q components",
            "executed_here": False,
            "current_control": (
                "One local source bundle and one R are executed. It can baseline either side but does not "
                "constitute a two-sided interface theorem."
            ),
            "future_master_obligations": [
                "execute distinct non-commuting R_+ and R_-",
                "execute independent g_+, g_- and common g_Q",
                "use non-Z2 bulk/embedding/interface data",
                "rederive both side traces and cross terms from the same action",
                "reject mutations that identify R_+=R_- or restore Z2 by construction",
            ],
        },
        "selected_family": {
            "ambient_metric": "ds^2=e^(2A(q))(-dt^2+dx^2+dy^2+dz^2)+dq^2",
            "embedding": "X^M=(t,x,y,z,Y(t,x)); exact displayed v5.6.2 graph profiles",
            "khronon": "T=t; u_mu=-N_T partial_mu T",
            "Q": (
                "gamma,T define Fr^+_SO(H_(gamma,T)); coordinate-projected Gram-Schmidt chooses one local "
                "oriented section, not a canonical frame"
            ),
            "groupoid_solder": "varphi=R(t,x) phi; varphi_H^mu=E_Q^mu_a varphi^a",
            "integration": "t,x in [0,2pi)^2; per unit coordinate y,z volume",
            "parameter_order": list(PARAMETER_NAMES),
            "theta": THETA.tolist(),
        },
        "derivation_contract": {
            "Robin": ROBIN_LITERAL,
            "source_P_Ward": "delta phi=hat(lambda)phi; delta R=-Rhat(lambda); delta(Rphi)=0",
            "target_Q_Ward": "delta varphi=hat(q)varphi; delta E_Q=-E_Qhat(q); delta(E_Q varphi)=0",
            "combined_P_Q_Ward": (
                "phi'=g_P phi; R'=g_Q R g_P^-1; E'=E g_Q^-1; "
                "delta R=hat(q)R-Rhat(lambda); delta(E R phi)=0"
            ),
            "metric_khronon_frame": (
                "N_T=(-gamma^munu T_mu T_nu)^(-1/2); u_mu=-N_T T_mu; "
                "H=ker(u); gamma,T define the oriented frame bundle and projected-coordinate Gram-Schmidt "
                "chooses one local section"
            ),
            "acceleration": "a_mu=(delta_mu^nu+u_mu u^nu) partial_nu log(N_T)",
            "JVP_route": "complex-step through the corrective local Robin action",
            "comparison_route": (
                "central finite difference through the same action evaluator; derivative-route check only, "
                "not an independent action reconstruction"
            ),
        },
        "frame_and_groupoid_invariants": frame,
        "selected_family_JVP_FD": jvp,
        "source_P_groupoid_Ward": source,
        "target_Q_frame_Ward": target,
        "combined_P_Q_groupoid_Ward": combined,
        "checks": checks,
        "open_obligations": {
            "complete_same_action_SO3_Ward": True,
            "same_action_bulk_embedding_interface_Euler_Green": True,
            "independent_redteam": True,
            "continuum_and_unrestricted_off_shell_extension": True,
            "BV_BFV_and_large_gauges": True,
            "C1_N1": True,
            "B4_B5": True,
            "passive_Phase_A_LOCK_1_clearance": True,
            "publication": True,
            "two_sided_distinct_R_plus_R_minus_and_non_Z2_master": True,
        },
        "provenance": {
            "generator": str(Path(__file__).resolve().relative_to(REPO)),
            "generator_sha256": generator_hash,
            "test": str(TEST.relative_to(REPO)),
            "test_sha256": test_hash,
            "test_present": TEST.exists(),
            "primary_v5_6_2_helpers_imported": [],
            "upstream_expected_Eulerian_residual_or_boolean_imported": [],
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> int:
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
