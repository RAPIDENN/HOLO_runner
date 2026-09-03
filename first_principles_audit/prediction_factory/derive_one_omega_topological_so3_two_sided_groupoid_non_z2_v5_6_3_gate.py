#!/usr/bin/env python3
"""Serializable two-sided groupoid/non-Z2 family engine for master C1/N1.

The engine emits primitive members and admissible tangents only.  It has no
action evaluator, density, P/F construction, Eulerian, Green residual, or
phenomenology.  Each consumer must reconstruct those derived objects.

Three members are exercised: an identity-solder control and two genuinely
two-sided, noncommuting R_+ != R_- members.  All interface gluing is built
from common target data in Q.  B traces remain independent off shell.  The
metric, embedding and khronon formulas are the pinned v5.6.2 formulas, while
side-specific rho*chi(rho) metric and field jets leave their interface traces
unchanged and break the exchange-fixed normal-jet restriction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "one_omega_topological_so3_two_sided_groupoid_non_z2_v5_6_3_gate.json"
TEST = HERE / "test_one_omega_topological_so3_two_sided_groupoid_non_z2_v5_6_3_gate.py"
SCHEMA = "holo.one-omega-topological-so3-two-sided-groupoid-non-z2-v5-6-3-gate.v1"


@dataclass(frozen=True)
class SourcePin:
    artifact: str
    artifact_sha256: str
    schema: str
    generator: str
    generator_sha256: str
    test: str
    test_sha256: str


SOURCE_PINS = {
    "v5_2": SourcePin(
        "one_omega_topological_so3_classical_v5_2_gate.json",
        "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
        "holo.one-omega-topological-so3-classical-v5-2-gate.v1",
        "derive_one_omega_topological_so3_classical_v5_2_gate.py",
        "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
        "test_one_omega_topological_so3_classical_v5_2_gate.py",
        "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
    ),
    "v5_6_2_primary": SourcePin(
        "one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate.json",
        "48c1a98c2071df36eccc4ce30f2bdf962ad73c425330404f2c6b7cdb5913a590",
        "holo.one-omega-topological-so3-full-moving-c1-n1-v5-6-2-gate.v1",
        "derive_one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate.py",
        "b9b0baf2c34620f5300ebf79084f9f8abf3a5f5b6374672c71c6add75222f372",
        "test_one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate.py",
        "bc0ba559975e5bdd975850e26daa42251c90cc46330d1f9a77941d7249fe3ce7",
    ),
    "v5_6_2_robin_groupoid": SourcePin(
        "one_omega_topological_so3_robin_frame_groupoid_v5_6_2_gate.json",
        "56d10b9088d3269bcd57fd3e54eef925ec45c8f8b9c774114ef73fc076350747",
        "holo.one-omega-topological-so3-robin-frame-groupoid-v5-6-2-gate.v1",
        "derive_one_omega_topological_so3_robin_frame_groupoid_v5_6_2_gate.py",
        "7ba65797c2d9b1f7c0bf45ce68a648b202688b673d0f795aeb7b38aaaeacd6c7",
        "test_one_omega_topological_so3_robin_frame_groupoid_v5_6_2_gate.py",
        "71ac02ee2025b768b62a3cf4db5f1a793e9ac0c0e1b0bc9f78993a2b8d414afa",
    ),
}

FAIL_CLOSED_KEYS = (
    "total_v5_2_action_reexecuted_pass",
    "component_action_JVP_pass",
    "same_action_independent_Euler_Green_identity_pass",
    "complete_same_action_SO3_Ward_pass",
    "full_bulk_diffeomorphism_Ward_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_selected_family_pass",
    "N1_ACTION_selected_family_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "continuum_convergence_pass",
    "passive_Phase_A_J_disengaged_pass",
    "LOCK_1_contamination_cleared_pass",
    "BV_BFV_interface_completion_pass",
    "independent_redteam_replication_pass",
    "deterministic_freeze_receipt_issued",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
)


@dataclass(frozen=True)
class FamilySpec:
    """Declarative data only; no derived field equation or action object."""

    version: str = "two-sided-groupoid-non-z2-family.v1"
    seeds: tuple[int, ...] = (0, 17, 29)
    identity_control_seed: int = 0
    sample_t: tuple[float, ...] = (0.37, 1.11, 2.47, 5.31)
    sample_x: tuple[float, ...] = (0.52, 2.03, 4.19, 1.73)
    sample_rho: tuple[float, ...] = (0.0, 0.19, 0.57, 1.25)
    collar_radius: float = 1.25
    warp_core: float = 0.71
    k_infinity: float = 1.0
    base_theta: tuple[float, ...] = (0.29, 0.24, 0.33, 0.41, 0.46, 0.38)
    tangent_step: float = 2.0e-6
    formula_embedding: str = "Y=Y0(t,x)+theta_Y*dY(t,x)"
    formula_metric: str = "g_epsilon=pullback[g0(q_epsilon)]+rho*chi(rho)*H_epsilon"
    formula_collar: str = "q_epsilon=epsilon*rho+chi(rho)*Y; j=rho*chi; j(0)=0; j_prime(0)=1"
    formula_phi_gluing: str = "phi_epsilon=R_epsilon^-1*varphi_H"
    formula_connection_gluing: str = "A_epsilon=R_epsilon^-1*A_Sigma*R_epsilon+R_epsilon^-1*dR_epsilon"
    formula_B_transport: str = "b_epsilon=Ad_R_epsilon(Y_epsilon^*B_epsilon); b_plus and b_minus are independent off shell"
    formula_frame: str = "E_Q=GramSchmidt(gamma,T=t); E_Q is recomputed and never an independent tangent"


@dataclass(frozen=True)
class TangentSpec:
    name: str
    embedding: float
    ambient_metric: float
    common_omega: float
    common_varphi: float
    common_A: float
    R_plus: float
    R_minus: float
    metric_jet_plus: float
    metric_jet_minus: float
    omega_jet_plus: float
    omega_jet_minus: float
    v_jet_plus: float
    v_jet_minus: float
    A_jet_plus: float
    A_jet_minus: float
    B_trace_plus: float
    B_trace_minus: float
    B_jet_plus: float
    B_jet_minus: float


class TwoSidedFamilyError(ValueError):
    """A source pin, primitive invariant, or fail-closed boundary drifted."""


def family_spec() -> FamilySpec:
    return FamilySpec()


def admissible_tangents() -> tuple[TangentSpec, ...]:
    """Coupled directions; every record contains every primitive field slot."""

    return (
        TangentSpec(
            "coupled_alpha", 0.23, -0.19, 0.17, 0.13, -0.11,
            0.29, -0.31, 0.37, -0.27, 0.21, -0.18, 0.16, -0.22,
            0.19, -0.14, 0.12, -0.17, 0.24, -0.20,
        ),
        TangentSpec(
            "coupled_beta", -0.18, 0.24, -0.15, 0.20, 0.16,
            -0.26, 0.33, -0.29, 0.35, -0.23, 0.27, -0.19, 0.25,
            -0.21, 0.18, -0.14, 0.22, -0.28, 0.31,
        ),
        TangentSpec(
            "coupled_gamma", 0.14, 0.11, 0.22, -0.17, 0.19,
            0.34, 0.27, 0.26, -0.32, 0.29, 0.24, -0.27, -0.16,
            0.23, 0.30, 0.18, -0.25, 0.21, -0.29,
        ),
    )


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise TwoSidedFamilyError(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _pin_upstreams() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, pin in SOURCE_PINS.items():
        paths = {
            "artifact": HERE / "artifacts" / pin.artifact,
            "generator": HERE / pin.generator,
            "test": HERE / pin.test,
        }
        pinned = {
            "artifact": pin.artifact_sha256,
            "generator": pin.generator_sha256,
            "test": pin.test_sha256,
        }
        actual = {kind: _sha256(path) for kind, path in paths.items()}
        if actual != pinned:
            raise TwoSidedFamilyError(f"{name} source drift: {actual}")
        artifact = json.loads(paths["artifact"].read_text(encoding="utf-8"))
        if artifact.get("schema") != pin.schema:
            raise TwoSidedFamilyError(f"{name} schema drift")
        result[name] = {
            "schema": pin.schema,
            "paths": {
                kind: str(path.relative_to(REPO)) for kind, path in paths.items()
            },
            "sha256": actual,
            "decision_boolean_consumed": False,
            "action_value_or_density_consumed": False,
            "Eulerian_or_residual_consumed": False,
            "helper_imported_or_called": False,
        }
    return result


def _unit(seed: int, label: str) -> float:
    digest = hashlib.sha256(f"{seed}:{label}".encode("ascii")).digest()
    integer = int.from_bytes(digest[:8], "big")
    return integer / float(2**64 - 1)


def member_coefficients(seed: int) -> dict[str, Any]:
    spec = family_spec()
    if seed not in spec.seeds:
        raise TwoSidedFamilyError(f"seed {seed} is outside the declared family")
    identity = seed == spec.identity_control_seed
    common_phase = 2.0 * math.pi * _unit(seed, "common_phase")
    result: dict[str, Any] = {
        "seed": seed,
        "identity_solder_control": identity,
        "embedding": spec.base_theta[0],
        "ambient_metric": spec.base_theta[1],
        "common_omega": 0.31 + 0.08 * _unit(seed, "common_omega"),
        "common_varphi": 0.88 + 0.17 * _unit(seed, "common_varphi"),
        "common_A": 0.39 + 0.13 * _unit(seed, "common_A"),
        "common_phase": common_phase,
        "sides": {},
    }
    for side in ("plus", "minus"):
        sign = 1.0 if side == "plus" else -1.0
        r_scale = 0.0 if identity else sign * (
            0.63 + 0.24 * _unit(seed, f"R:{side}")
        )
        result["sides"][side] = {
            "R_scale": r_scale,
            "R_phase": 2.0 * math.pi * _unit(seed, f"R_phase:{side}"),
            "metric_jet": sign * (0.027 + 0.013 * _unit(seed, f"metric:{side}")),
            "omega_jet": sign * (0.19 + 0.08 * _unit(seed, f"omega:{side}")),
            "v_jet": sign * (0.17 + 0.07 * _unit(seed, f"v:{side}")),
            "A_jet": sign * (0.14 + 0.06 * _unit(seed, f"A:{side}")),
            "B_trace": 0.73 + sign * 0.12 + 0.08 * _unit(seed, f"Btrace:{side}"),
            "B_jet": sign * (0.18 + 0.07 * _unit(seed, f"Bjet:{side}")),
        }
    return result


def _shifted_coefficients(
    seed: int, tangent: TangentSpec | None, scale: float
) -> dict[str, Any]:
    base = member_coefficients(seed)
    if tangent is None or scale == 0.0:
        return base
    base["embedding"] += scale * tangent.embedding
    base["ambient_metric"] += scale * tangent.ambient_metric
    base["common_omega"] += scale * tangent.common_omega
    base["common_varphi"] += scale * tangent.common_varphi
    base["common_A"] += scale * tangent.common_A
    for side in ("plus", "minus"):
        data = base["sides"][side]
        data["R_scale"] += scale * getattr(tangent, f"R_{side}")
        for key in ("metric_jet", "omega_jet", "v_jet", "A_jet", "B_trace", "B_jet"):
            data[key] += scale * getattr(tangent, f"{key}_{side}")
    return base


def _profiles(t: np.ndarray, x: np.ndarray) -> dict[str, np.ndarray]:
    u = 2.0 * t - x
    return {
        "Y": 0.16 + 0.055 * np.cos(t) + 0.071 * np.cos(x) + 0.031 * np.sin(t + x),
        "Y_t": -0.055 * np.sin(t) + 0.031 * np.cos(t + x),
        "Y_x": -0.071 * np.sin(x) + 0.031 * np.cos(t + x),
        "dY": 0.061 * np.sin(t) * np.cos(x) + 0.029 * np.cos(u),
        "dY_t": 0.061 * np.cos(t) * np.cos(x) - 0.058 * np.sin(u),
        "dY_x": -0.061 * np.sin(t) * np.sin(x) + 0.029 * np.sin(u),
    }


def _embedding(
    parameter: float, t: np.ndarray, x: np.ndarray
) -> dict[str, np.ndarray]:
    profiles = _profiles(t, x)
    return {
        key: profiles[key] + parameter * profiles[f"d{key}"]
        for key in ("Y", "Y_t", "Y_x")
    }


def _chi(rho: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    radius = family_spec().collar_radius
    u = rho / radius
    inside = u < 1.0
    value = np.zeros_like(rho)
    derivative = np.zeros_like(rho)
    ui = u[inside]
    value[inside] = 1.0 - 10.0 * ui**3 + 15.0 * ui**4 - 6.0 * ui**5
    derivative[inside] = (-30.0 * ui**2 + 60.0 * ui**3 - 30.0 * ui**4) / radius
    return value, derivative


def _ambient_metric(
    q: np.ndarray, parameter: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    spec = family_spec()
    kappa = spec.k_infinity * (1.0 + 0.12 * parameter)
    radius = np.sqrt(q * q + spec.warp_core**2)
    exponent_q = -kappa * q / radius
    warp = np.exp(-kappa * radius)
    warp_q = exponent_q * warp
    metric = np.zeros(q.shape + (5, 5), dtype=float)
    metric_q = np.zeros_like(metric)
    for index, sign in enumerate((-1.0, 1.0, 1.0, 1.0)):
        metric[..., index, index] = sign * warp * warp
        metric_q[..., index, index] = sign * 2.0 * warp * warp_q
    metric[..., 4, 4] = 1.0
    return metric, metric_q, warp


def _metric_jet_profile(
    side: str, t: np.ndarray, x: np.ndarray, phase: float
) -> np.ndarray:
    sign = 1.0 if side == "plus" else -1.0
    result = np.zeros(t.shape + (5, 5), dtype=float)
    diagonals = (
        0.17 + 0.03 * np.sin(t + phase),
        0.13 + sign * 0.025 * np.cos(x - phase),
        -0.11 + 0.02 * np.sin(t + x),
        0.09 + sign * 0.018 * np.cos(t - x),
        0.07 + 0.014 * np.sin(x + phase),
    )
    for index, value in enumerate(diagonals):
        result[..., index, index] = value
    result[..., 0, 1] = result[..., 1, 0] = 0.021 * np.sin(t - x + phase)
    result[..., 2, 3] = result[..., 3, 2] = sign * 0.017 * np.cos(t + x)
    return result


def _rotation_x(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=float)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 0, 0] = 1.0
    result[..., 1, 1] = result[..., 2, 2] = c
    result[..., 1, 2], result[..., 2, 1] = -s, s
    return result


def _rotation_x_prime(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=float)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 1, 1] = result[..., 2, 2] = -s
    result[..., 1, 2], result[..., 2, 1] = -c, c
    return result


def _rotation_y(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=float)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 0, 0] = result[..., 2, 2] = c
    result[..., 0, 2], result[..., 2, 0] = s, -s
    result[..., 1, 1] = 1.0
    return result


def _rotation_y_prime(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=float)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 0, 0] = result[..., 2, 2] = -s
    result[..., 0, 2], result[..., 2, 0] = c, -c
    return result


def _rotation_z(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=float)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 0, 0] = result[..., 1, 1] = c
    result[..., 0, 1], result[..., 1, 0] = -s, s
    result[..., 2, 2] = 1.0
    return result


def _rotation_z_prime(angle: np.ndarray) -> np.ndarray:
    result = np.zeros(angle.shape + (3, 3), dtype=float)
    c, s = np.cos(angle), np.sin(angle)
    result[..., 0, 0] = result[..., 1, 1] = -s
    result[..., 0, 1], result[..., 1, 0] = -c, c
    return result


def _rotation_bundle(
    side: str, t: np.ndarray, x: np.ndarray, scale: float, phase: float
) -> dict[str, np.ndarray]:
    sign = 1.0 if side == "plus" else -1.0
    alpha0 = 0.17 + 0.061 * np.sin(t + phase) + sign * 0.029 * np.cos(x)
    beta0 = -0.11 + sign * 0.047 * np.cos(t + x - phase)
    gamma0 = 0.13 + 0.037 * np.sin(t - 2.0 * x + sign * phase)
    alpha, beta, gamma = scale * alpha0, scale * beta0, scale * gamma0
    derivatives = {
        "t": (
            scale * 0.061 * np.cos(t + phase),
            -scale * sign * 0.047 * np.sin(t + x - phase),
            scale * 0.037 * np.cos(t - 2.0 * x + sign * phase),
        ),
        "x": (
            -scale * sign * 0.029 * np.sin(x),
            -scale * sign * 0.047 * np.sin(t + x - phase),
            -scale * 0.074 * np.cos(t - 2.0 * x + sign * phase),
        ),
    }
    rx, ry, rz = _rotation_x(alpha), _rotation_y(beta), _rotation_z(gamma)
    rxp, ryp, rzp = _rotation_x_prime(alpha), _rotation_y_prime(beta), _rotation_z_prime(gamma)
    rotation = rz @ ry @ rx
    d_rotation: dict[str, np.ndarray] = {}
    for axis, (da, db, dg) in derivatives.items():
        d_rotation[axis] = (
            (rzp * dg[..., None, None]) @ ry @ rx
            + rz @ (ryp * db[..., None, None]) @ rx
            + rz @ ry @ (rxp * da[..., None, None])
        )
    zeros = np.zeros_like(rotation)
    return {
        "R": rotation,
        "dR": np.stack((d_rotation["t"], d_rotation["x"], zeros, zeros), axis=-3),
    }


def _hat(vector: np.ndarray) -> np.ndarray:
    result = np.zeros(vector.shape[:-1] + (3, 3), dtype=float)
    result[..., 0, 1], result[..., 0, 2] = -vector[..., 2], vector[..., 1]
    result[..., 1, 0], result[..., 1, 2] = vector[..., 2], -vector[..., 0]
    result[..., 2, 0], result[..., 2, 1] = -vector[..., 1], vector[..., 0]
    return result


def _vee(matrix: np.ndarray) -> np.ndarray:
    return np.stack(
        (matrix[..., 2, 1], matrix[..., 0, 2], matrix[..., 1, 0]), axis=-1
    )


def _common_targets(
    coefficients: Mapping[str, Any], graph: Mapping[str, np.ndarray], t: np.ndarray, x: np.ndarray
) -> dict[str, np.ndarray]:
    phase = float(coefficients["common_phase"])
    omega_profile = (
        0.16 * np.exp(-graph["Y"] ** 2 / 9.0) * np.cos(t)
        + 0.11 * np.sin(x)
        + 0.04 * graph["Y"] * np.sin(t + x)
        + 0.03 * np.cos(2.0 * t - x)
    )
    omega = np.exp(float(coefficients["common_omega"]) * omega_profile)
    varphi = float(coefficients["common_varphi"]) * np.stack(
        (
            0.43 + 0.07 * np.sin(t + phase),
            -0.26 + 0.05 * np.cos(t + x),
            0.31 + 0.04 * np.sin(t - 2.0 * x - phase),
        ),
        axis=-1,
    )
    connection = float(coefficients["common_A"]) * np.stack(
        (
            np.stack((0.12 * np.cos(x), 0.08 * np.sin(t + phase), 0.07 * np.cos(t + x)), axis=-1),
            np.stack((0.09 * np.sin(t), -0.11 * np.cos(x - phase), 0.10 * np.sin(t - x)), axis=-1),
            np.stack((0.05 * np.sin(t + x), 0.06 * np.cos(t), 0.08 * np.sin(x + phase)), axis=-1),
            np.stack((-0.07 * np.cos(x), 0.04 * np.sin(t - phase), 0.06 * np.cos(t + x)), axis=-1),
        ),
        axis=-2,
    )
    return {"Omega": omega, "varphi_H": varphi, "A_Sigma_vector": connection, "A_Sigma_matrix": _hat(connection)}


def _B_target(
    side: str, scale: float, t: np.ndarray, x: np.ndarray
) -> np.ndarray:
    sign = 1.0 if side == "plus" else -1.0
    return scale * np.stack(
        (
            np.stack((0.20 + 0.03 * np.sin(t), -0.17 * np.cos(x), sign * 0.11 * np.sin(t + x)), axis=-1),
            np.stack((sign * 0.07 * np.cos(x), 0.09 * np.sin(t), -0.08 * np.cos(t - x)), axis=-1),
        ),
        axis=-2,
    )


def _inner(metric: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.einsum("...mn,...m,...n->...", metric, left, right)


def _frame_from_gamma(gamma: np.ndarray) -> dict[str, np.ndarray]:
    inverse = np.linalg.inv(gamma)
    lapse = (-inverse[..., 0, 0]) ** -0.5
    u_cov = np.zeros(gamma.shape[:-1], dtype=float)
    u_cov[..., 0] = -lapse
    u_contra = np.einsum("...mn,...n->...m", inverse, u_cov)
    candidates = np.empty(gamma.shape[:-2] + (4, 3), dtype=float)
    for column in range(3):
        coordinate = np.zeros(4)
        coordinate[column + 1] = 1.0
        candidates[..., :, column] = coordinate + u_contra * u_cov[..., column + 1, None]
    frame = np.empty_like(candidates)
    for column in range(3):
        vector = candidates[..., :, column].copy()
        for previous in range(column):
            projection = _inner(gamma, frame[..., :, previous], vector)
            vector -= frame[..., :, previous] * projection[..., None]
        vector /= np.sqrt(_inner(gamma, vector, vector))[..., None]
        frame[..., :, column] = vector
    return {"frame": frame, "u_cov": u_cov, "u_contra": u_contra}


def _pullback_metric(
    metric_trace: np.ndarray, graph: Mapping[str, np.ndarray]
) -> np.ndarray:
    tangent = np.zeros(metric_trace.shape[:-2] + (5, 4), dtype=float)
    tangent[..., 0, 0] = tangent[..., 1, 1] = 1.0
    tangent[..., 2, 2] = tangent[..., 3, 3] = 1.0
    tangent[..., 4, 0] = graph["Y_t"]
    tangent[..., 4, 1] = graph["Y_x"]
    return np.einsum("...Mm,...MN,...Nn->...mn", tangent, metric_trace, tangent)


def _jet_profiles(
    side: str, t: np.ndarray, x: np.ndarray, phase: float
) -> dict[str, np.ndarray]:
    sign = 1.0 if side == "plus" else -1.0
    scalar = 0.13 + sign * 0.021 * np.sin(t + phase) + 0.017 * np.cos(x)
    vector = np.stack(
        (0.08 + sign * 0.02 * np.sin(t), -0.06 + 0.017 * np.cos(x + phase), sign * 0.07 + 0.015 * np.sin(t + x)),
        axis=-1,
    )
    connection = np.stack(
        tuple(
            np.stack(
                (
                    0.012 * (index + 1) + sign * 0.004 * np.sin(t),
                    -0.009 * (index + 1) + 0.003 * np.cos(x + phase),
                    sign * 0.007 * (index + 1) + 0.002 * np.sin(t + x),
                ),
                axis=-1,
            )
            for index in range(5)
        ),
        axis=-2,
    )
    b_form = np.stack(
        tuple(
            np.stack(
                (
                    0.019 * (index + 1) + sign * 0.004 * np.cos(t),
                    sign * 0.016 + 0.003 * np.sin(x + phase),
                    -0.014 * (index + 1) + 0.002 * np.cos(t - x),
                ),
                axis=-1,
            )
            for index in range(2)
        ),
        axis=-2,
    )
    return {"Omega": scalar, "v": vector, "A": connection, "B": b_form}


def _radial_slopes(t: np.ndarray, x: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "Omega": 0.021 + 0.004 * np.sin(t + x),
        "v": np.stack((0.031 + 0.004 * np.cos(t), -0.024 + 0.003 * np.sin(x), 0.027 + 0.002 * np.cos(t - x)), axis=-1),
        "A": np.stack(tuple(np.stack((0.006 * (i + 1) + 0.001 * np.sin(t), -0.005 * (i + 1) + 0.001 * np.cos(x), 0.004 * (i + 1) + 0.001 * np.sin(t + x)), axis=-1) for i in range(5)), axis=-2),
        "B": np.stack(tuple(np.stack((0.008 * (i + 1) + 0.001 * np.cos(t), -0.007 * (i + 1) + 0.001 * np.sin(x), 0.006 * (i + 1) + 0.001 * np.cos(t - x)), axis=-1) for i in range(2)), axis=-2),
    }


def _radial_scale(radial: np.ndarray, value: np.ndarray) -> np.ndarray:
    return radial[(...,) + (None,) * (value.ndim - 1)] * value[None, ...]


def _primitive_hash(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value, dtype="<f8")
    return hashlib.sha256(array.tobytes()).hexdigest()


def build_member(
    seed: int,
    t: np.ndarray | None = None,
    x: np.ndarray | None = None,
    rho: np.ndarray | None = None,
    *,
    tangent: TangentSpec | None = None,
    scale: float = 0.0,
) -> dict[str, Any]:
    """Build raw primitives only; no action-related derived quantities."""

    spec = family_spec()
    if t is None:
        t = np.asarray(spec.sample_t, dtype=float)
    if x is None:
        x = np.asarray(spec.sample_x, dtype=float)
    if rho is None:
        rho = np.asarray(spec.sample_rho, dtype=float)
    t, x, rho = np.asarray(t, dtype=float), np.asarray(x, dtype=float), np.asarray(rho, dtype=float)
    if t.shape != x.shape or t.ndim != 1 or rho.ndim != 1:
        raise TwoSidedFamilyError("t and x must be equal one-dimensional samples; rho must be one-dimensional")
    coefficients = _shifted_coefficients(seed, tangent, scale)
    graph = _embedding(float(coefficients["embedding"]), t, x)
    targets = _common_targets(coefficients, graph, t, x)
    chi, chi_prime = _chi(rho)
    bump, bump_prime = rho * chi, chi + rho * chi_prime
    sides: dict[str, Any] = {}
    gamma_rows: dict[str, np.ndarray] = {}
    for epsilon, side in ((1, "plus"), (-1, "minus")):
        side_coeff = coefficients["sides"][side]
        q = epsilon * rho[:, None] + chi[:, None] * graph["Y"][None, :]
        q_rho = epsilon + chi_prime[:, None] * graph["Y"][None, :]
        q_t_at_rho = chi[:, None] * graph["Y_t"][None, :]
        q_x_at_rho = chi[:, None] * graph["Y_x"][None, :]
        inverse_coordinate_jacobian = {
            "partial_q_from_partial_rho": 1.0 / q_rho,
            "partial_t_at_q_from_partial_rho": -q_t_at_rho / q_rho,
            "partial_x_at_q_from_partial_rho": -q_x_at_rho / q_rho,
        }
        radial_delta = q - graph["Y"][None, :]
        base_metric, base_metric_q, warp = _ambient_metric(q, float(coefficients["ambient_metric"]))
        h_profile = _metric_jet_profile(side, t, x, float(side_coeff["R_phase"]))
        metric = base_metric + float(side_coeff["metric_jet"]) * _radial_scale(bump[:, None], h_profile)
        metric_rho = base_metric_q * q_rho[..., None, None] + float(side_coeff["metric_jet"]) * _radial_scale(bump_prime[:, None], h_profile)
        gamma = _pullback_metric(metric[0], graph)
        gamma_rows[side] = gamma

        rotation_data = _rotation_bundle(
            side, t, x, float(side_coeff["R_scale"]), float(side_coeff["R_phase"])
        )
        rotation, d_rotation = rotation_data["R"], rotation_data["dR"]
        transpose = np.swapaxes(rotation, -1, -2)
        source_phi = np.einsum("...ab,...b->...a", transpose, targets["varphi_H"])
        source_a_matrix = (
            transpose[..., None, :, :] @ targets["A_Sigma_matrix"] @ rotation[..., None, :, :]
            + transpose[..., None, :, :] @ d_rotation
        )
        source_a_vector = _vee(source_a_matrix)
        b_target = _B_target(side, float(side_coeff["B_trace"]), t, x)
        source_b = np.einsum("...ab,...kb->...ka", transpose, b_target)

        jet_target = _jet_profiles(side, t, x, float(side_coeff["R_phase"]))
        jet_source = {
            "Omega": jet_target["Omega"],
            "v": np.einsum("...ab,...b->...a", transpose, jet_target["v"]),
            "A": np.einsum("...ab,...kb->...ka", transpose, jet_target["A"]),
            "B": np.einsum("...ab,...kb->...ka", transpose, jet_target["B"]),
        }
        slopes = _radial_slopes(t, x)
        v_trace = targets["Omega"][..., None] ** 1.5 * source_phi
        a_trace = np.concatenate((source_a_vector, np.zeros(t.shape + (1, 3))), axis=-2)
        traces = {"Omega": targets["Omega"], "v": v_trace, "A": a_trace, "B": source_b}
        jet_coefficients = {
            "Omega": float(side_coeff["omega_jet"]),
            "v": float(side_coeff["v_jet"]),
            "A": float(side_coeff["A_jet"]),
            "B": float(side_coeff["B_jet"]),
        }
        fields: dict[str, np.ndarray] = {}
        field_rho: dict[str, np.ndarray] = {}
        field_q: dict[str, np.ndarray] = {}
        added_jets: dict[str, np.ndarray] = {}
        for name in ("Omega", "v", "A", "B"):
            fields[name] = (
                traces[name][None, ...]
                + _radial_scale(radial_delta, slopes[name])
                + jet_coefficients[name] * _radial_scale(bump[:, None], jet_source[name])
            )
            field_rho[name] = (
                _radial_scale(q_rho, slopes[name])
                + jet_coefficients[name] * _radial_scale(bump_prime[:, None], jet_source[name])
            )
            field_q[name] = field_rho[name] / q_rho[(...,) + (None,) * (fields[name].ndim - 2)]
            added_jets[name] = jet_coefficients[name] * jet_source[name]
        fields["phi"] = fields["Omega"][..., None] ** -1.5 * fields["v"]
        field_rho["phi"] = fields["Omega"][..., None] ** -1.5 * (
            field_rho["v"]
            - 1.5 * fields["v"] * field_rho["Omega"][..., None] / fields["Omega"][..., None]
        )
        field_q["phi"] = field_rho["phi"] / q_rho[..., None]
        target_added_phi_jet = np.einsum(
            "...ab,...b->...a", rotation,
            targets["Omega"][..., None] ** -1.5 * (
                added_jets["v"]
                - 1.5 * v_trace * added_jets["Omega"][..., None] / targets["Omega"][..., None]
            ),
        )
        sides[side] = {
            "epsilon": epsilon,
            "coefficients": side_coeff,
            "q": q,
            "q_rho": q_rho,
            "q_t_at_rho": q_t_at_rho,
            "q_x_at_rho": q_x_at_rho,
            "inverse_coordinate_jacobian": inverse_coordinate_jacobian,
            "metric": metric,
            "metric_rho": metric_rho,
            "metric_added_normal_jet": float(side_coeff["metric_jet"]) * h_profile,
            "gamma": gamma,
            "R": rotation,
            "dR": d_rotation,
            "source_phi_trace": source_phi,
            "source_A_trace_matrix": source_a_matrix,
            "source_A_trace_vector": source_a_vector,
            "source_B_trace": source_b,
            "target_B_trace": b_target,
            "fields": fields,
            "field_rho": field_rho,
            "field_q": field_q,
            "added_normal_jets_source": added_jets,
            "added_normal_phi_jet_target": target_added_phi_jet,
            "added_normal_A_jet_target": jet_coefficients["A"] * jet_target["A"],
            "added_normal_B_jet_target": jet_coefficients["B"] * jet_target["B"],
            "warp": warp,
        }
    common_gamma = 0.5 * (gamma_rows["plus"] + gamma_rows["minus"])
    frame_data = _frame_from_gamma(common_gamma)
    return {
        "seed": seed,
        "coefficients": coefficients,
        "coordinates": {"t": t, "x": x, "rho": rho},
        "graph": graph,
        "targets": targets,
        "common_gamma": common_gamma,
        "frame": frame_data["frame"],
        "u_cov": frame_data["u_cov"],
        "u_contra": frame_data["u_contra"],
        "sides": sides,
    }


def _maximum(value: np.ndarray | float) -> float:
    return float(np.max(np.abs(value)))


def member_kinematic_invariants(member: Mapping[str, Any]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    gamma_plus = member["sides"]["plus"]["gamma"]
    gamma_minus = member["sides"]["minus"]["gamma"]
    for side in ("plus", "minus"):
        data = member["sides"][side]
        rotation, transpose = data["R"], np.swapaxes(data["R"], -1, -2)
        transported_phi = np.einsum("...ab,...b->...a", rotation, data["source_phi_trace"])
        transported_a = (
            rotation[..., None, :, :] @ data["source_A_trace_matrix"] @ transpose[..., None, :, :]
            - data["dR"] @ transpose[..., None, :, :]
        )
        transported_b = np.einsum("...ab,...kb->...ka", rotation, data["source_B_trace"])
        physical_left = np.einsum("...ma,...ab,...b->...m", member["frame"], rotation, data["source_phi_trace"])
        physical_right = np.einsum("...ma,...a->...m", member["frame"], member["targets"]["varphi_H"])
        rows[side] = {
            "gamma_to_common_Linf": _maximum(data["gamma"] - member["common_gamma"]),
            "Omega_to_common_Linf": _maximum(data["fields"]["Omega"][0] - member["targets"]["Omega"]),
            "R_phi_to_common_varphi_Linf": _maximum(transported_phi - member["targets"]["varphi_H"]),
            "E_Q_R_phi_identity_Linf": _maximum(physical_left - physical_right),
            "A_transport_to_common_A_Sigma_Linf": _maximum(transported_a - member["targets"]["A_Sigma_matrix"]),
            "B_adjoint_transport_to_own_b_Linf": _maximum(transported_b - data["target_B_trace"]),
            "R_orthogonality_Linf": _maximum(transpose @ rotation - np.eye(3)),
            "R_determinant_Linf": _maximum(np.linalg.det(rotation) - 1.0),
        }
    frame_gram = np.einsum("...mn,...ma,...nb->...ab", member["common_gamma"], member["frame"], member["frame"])
    frame_spatial = np.einsum("...m,...ma->...a", member["u_cov"], member["frame"])
    commutator = (
        member["sides"]["plus"]["R"] @ member["sides"]["minus"]["R"]
        - member["sides"]["minus"]["R"] @ member["sides"]["plus"]["R"]
    )
    return {
        "per_side_without_cross_side_summation": rows,
        "gamma_plus_minus_Linf": _maximum(gamma_plus - gamma_minus),
        "R_plus_minus_Linf": _maximum(member["sides"]["plus"]["R"] - member["sides"]["minus"]["R"]),
        "R_plus_R_minus_commutator_Linf": _maximum(commutator),
        "frame_orthonormality_Linf": _maximum(frame_gram - np.eye(3)),
        "frame_spatiality_Linf": _maximum(frame_spatial),
        "B_oriented_flux_raw_Linf": _maximum(
            member["sides"]["plus"]["target_B_trace"] - member["sides"]["minus"]["target_B_trace"]
        ),
        "B_oriented_flux_equation_imposed": False,
    }


def _jet_signature(member: Mapping[str, Any], side: str) -> np.ndarray:
    data = member["sides"][side]
    return np.concatenate(
        (
            data["metric_added_normal_jet"].reshape(data["metric_added_normal_jet"].shape[0], -1),
            data["added_normal_jets_source"]["Omega"][..., None],
            data["added_normal_phi_jet_target"],
            data["added_normal_A_jet_target"].reshape(data["added_normal_A_jet_target"].shape[0], -1),
            data["added_normal_B_jet_target"].reshape(data["added_normal_B_jet_target"].shape[0], -1),
        ),
        axis=-1,
    )


def _primitive_arrays(member: Mapping[str, Any]) -> dict[str, np.ndarray]:
    result = {
        "Y": member["graph"]["Y"],
        "gamma": member["common_gamma"],
        "frame": member["frame"],
        "Omega_Sigma": member["targets"]["Omega"],
        "varphi_H": member["targets"]["varphi_H"],
        "A_Sigma": member["targets"]["A_Sigma_vector"],
    }
    for side in ("plus", "minus"):
        data = member["sides"][side]
        result.update(
            {
                f"{side}:R": data["R"],
                f"{side}:g": data["metric"],
                f"{side}:g_rho": data["metric_rho"],
                f"{side}:inverse_coordinate_jacobian_q": data["inverse_coordinate_jacobian"]["partial_q_from_partial_rho"],
                f"{side}:inverse_coordinate_jacobian_t": data["inverse_coordinate_jacobian"]["partial_t_at_q_from_partial_rho"],
                f"{side}:inverse_coordinate_jacobian_x": data["inverse_coordinate_jacobian"]["partial_x_at_q_from_partial_rho"],
                f"{side}:phi": data["fields"]["phi"],
                f"{side}:phi_rho": data["field_rho"]["phi"],
                f"{side}:A": data["fields"]["A"],
                f"{side}:A_rho": data["field_rho"]["A"],
                f"{side}:B": data["fields"]["B"],
                f"{side}:B_rho": data["field_rho"]["B"],
                f"{side}:Omega": data["fields"]["Omega"],
                f"{side}:Omega_rho": data["field_rho"]["Omega"],
                f"{side}:v": data["fields"]["v"],
                f"{side}:v_rho": data["field_rho"]["v"],
            }
        )
    return result


def _sample(value: np.ndarray, count: int = 2) -> list[Any]:
    array = np.asarray(value)
    return array[:count].tolist()


def _member_receipt(member: Mapping[str, Any]) -> dict[str, Any]:
    invariants = member_kinematic_invariants(member)
    primitives = _primitive_arrays(member)
    side_rows: dict[str, Any] = {}
    for side in ("plus", "minus"):
        data = member["sides"][side]
        side_rows[side] = {
            "R_samples": _sample(data["R"]),
            "source_phi_trace_samples": _sample(data["source_phi_trace"]),
            "source_A_trace_vector_samples": _sample(data["source_A_trace_vector"]),
            "source_B_trace_samples": _sample(data["source_B_trace"]),
            "target_B_trace_samples": _sample(data["target_B_trace"]),
            "metric_added_normal_jet_samples": _sample(data["metric_added_normal_jet"]),
            "Omega_added_normal_jet_samples": _sample(data["added_normal_jets_source"]["Omega"]),
            "phi_added_normal_jet_target_samples": _sample(data["added_normal_phi_jet_target"]),
            "A_added_normal_jet_target_samples": _sample(data["added_normal_A_jet_target"]),
            "B_added_normal_jet_target_samples": _sample(data["added_normal_B_jet_target"]),
            "physical_q_derivative_samples": {
                field: _sample(data["field_q"][field][:, :2])
                for field in ("Omega", "v", "phi", "A", "B")
            },
            "inverse_coordinate_jacobian_samples": {
                key: _sample(value)
                for key, value in data["inverse_coordinate_jacobian"].items()
            },
        }
    return {
        "seed": member["seed"],
        "coefficients": member["coefficients"],
        "coordinates": {key: value.tolist() for key, value in member["coordinates"].items()},
        "common_target_samples": {
            "Y": _sample(member["graph"]["Y"]),
            "gamma": _sample(member["common_gamma"]),
            "frame": _sample(member["frame"]),
            "Omega_Sigma": _sample(member["targets"]["Omega"]),
            "varphi_H": _sample(member["targets"]["varphi_H"]),
            "A_Sigma": _sample(member["targets"]["A_Sigma_vector"]),
        },
        "sides": side_rows,
        "kinematic_invariants": invariants,
        "primitive_sha256": {name: _primitive_hash(value) for name, value in sorted(primitives.items())},
        "all_primitives_sha256": _canonical_sha256({name: _primitive_hash(value) for name, value in sorted(primitives.items())}),
    }


def _gluing_vector(member: Mapping[str, Any], side: str) -> np.ndarray:
    data = member["sides"][side]
    rotation, transpose = data["R"], np.swapaxes(data["R"], -1, -2)
    transported_a = (
        rotation[..., None, :, :] @ data["source_A_trace_matrix"] @ transpose[..., None, :, :]
        - data["dR"] @ transpose[..., None, :, :]
    )
    parts = (
        (data["gamma"] - member["common_gamma"]).reshape(data["gamma"].shape[0], -1),
        (data["fields"]["Omega"][0] - member["targets"]["Omega"])[..., None],
        (np.einsum("...ab,...b->...a", rotation, data["source_phi_trace"]) - member["targets"]["varphi_H"]),
        (transported_a - member["targets"]["A_Sigma_matrix"]).reshape(data["R"].shape[0], -1),
        (np.einsum("...ab,...kb->...ka", rotation, data["source_B_trace"]) - data["target_B_trace"]).reshape(data["R"].shape[0], -1),
        (
            np.einsum("...ma,...ab,...b->...m", member["frame"], rotation, data["source_phi_trace"])
            - np.einsum("...ma,...a->...m", member["frame"], member["targets"]["varphi_H"])
        ),
    )
    return np.concatenate(parts, axis=-1)


def _tangent_raw_arrays(
    plus: Mapping[str, Any], minus: Mapping[str, Any], step: float
) -> dict[str, np.ndarray]:
    result = {
        "embedding": (plus["graph"]["Y"] - minus["graph"]["Y"]) / (2.0 * step),
        "frame": (plus["frame"] - minus["frame"]) / (2.0 * step),
        "common_Omega": (plus["targets"]["Omega"] - minus["targets"]["Omega"]) / (2.0 * step),
        "common_varphi": (plus["targets"]["varphi_H"] - minus["targets"]["varphi_H"]) / (2.0 * step),
        "common_A": (plus["targets"]["A_Sigma_vector"] - minus["targets"]["A_Sigma_vector"]) / (2.0 * step),
    }
    for side in ("plus", "minus"):
        p, m = plus["sides"][side], minus["sides"][side]
        result.update(
            {
                f"{side}:g": (p["metric"] - m["metric"]) / (2.0 * step),
                f"{side}:g_normal_jet": (p["metric_rho"][0] - m["metric_rho"][0]) / (2.0 * step),
                f"{side}:Omega": (p["fields"]["Omega"] - m["fields"]["Omega"]) / (2.0 * step),
                f"{side}:Omega_normal_jet": (p["field_rho"]["Omega"][0] - m["field_rho"]["Omega"][0]) / (2.0 * step),
                f"{side}:phi": (p["fields"]["phi"] - m["fields"]["phi"]) / (2.0 * step),
                f"{side}:phi_normal_jet": (p["field_rho"]["phi"][0] - m["field_rho"]["phi"][0]) / (2.0 * step),
                f"{side}:A": (p["fields"]["A"] - m["fields"]["A"]) / (2.0 * step),
                f"{side}:A_normal_jet": (p["field_rho"]["A"][0] - m["field_rho"]["A"][0]) / (2.0 * step),
                f"{side}:B": (p["fields"]["B"] - m["fields"]["B"]) / (2.0 * step),
                f"{side}:B_normal_jet": (p["field_rho"]["B"][0] - m["field_rho"]["B"][0]) / (2.0 * step),
                f"{side}:R": (p["R"] - m["R"]) / (2.0 * step),
            }
        )
    return result


def tangent_receipt(seed: int, tangent: TangentSpec) -> dict[str, Any]:
    step = family_spec().tangent_step
    plus = build_member(seed, tangent=tangent, scale=step)
    minus = build_member(seed, tangent=tangent, scale=-step)
    raw = _tangent_raw_arrays(plus, minus, step)
    gluing: dict[str, Any] = {}
    for side in ("plus", "minus"):
        plus_vector = _gluing_vector(plus, side)
        minus_vector = _gluing_vector(minus, side)
        gluing[side] = {
            "finite_plus_gluing_Linf": _maximum(plus_vector),
            "finite_minus_gluing_Linf": _maximum(minus_vector),
            "linearized_gluing_Linf": _maximum((plus_vector - minus_vector) / (2.0 * step)),
        }
    active = {name: float(np.sqrt(np.mean(value * value))) for name, value in raw.items()}
    return {
        "name": tangent.name,
        "coefficients": asdict(tangent),
        "step": step,
        "per_side_gluing_without_cross_side_summation": gluing,
        "raw_primitive_tangent_L2": active,
        "raw_primitive_tangent_samples": {name: _sample(value) for name, value in raw.items()},
        "raw_primitive_tangent_sha256": {name: _primitive_hash(value) for name, value in sorted(raw.items())},
        "all_tangent_primitives_sha256": _canonical_sha256({name: _primitive_hash(value) for name, value in sorted(raw.items())}),
    }


def _mutant_witnesses(members: Mapping[int, Mapping[str, Any]]) -> dict[str, float]:
    member = members[17]
    plus, minus = member["sides"]["plus"], member["sides"]["minus"]
    identity = np.broadcast_to(np.eye(3), plus["R"].shape)
    freeze_plus_phi = np.einsum("...ab,...b->...a", identity, plus["source_phi_trace"])
    freeze_minus_phi = np.einsum("...ab,...b->...a", identity, minus["source_phi_trace"])
    lambda_vector = np.stack(
        (0.27 + 0.04 * np.sin(member["coordinates"]["t"]), -0.19 + 0.03 * np.cos(member["coordinates"]["x"]), 0.16 + 0.02 * np.sin(member["coordinates"]["t"] - member["coordinates"]["x"])),
        axis=-1,
    )
    rotate_only = np.einsum("...ab,...bc,...c->...a", plus["R"], _hat(lambda_vector), plus["source_phi_trace"])
    wrong_source_a = (
        np.swapaxes(plus["R"], -1, -2)[..., None, :, :] @ member["targets"]["A_Sigma_matrix"] @ plus["R"][..., None, :, :]
        - np.swapaxes(plus["R"], -1, -2)[..., None, :, :] @ plus["dR"]
    )
    wrong_transport = (
        plus["R"][..., None, :, :] @ wrong_source_a @ np.swapaxes(plus["R"], -1, -2)[..., None, :, :]
        - plus["dR"] @ np.swapaxes(plus["R"], -1, -2)[..., None, :, :]
    )
    plus_signature, minus_signature = _jet_signature(member, "plus"), _jet_signature(member, "minus")
    reused_minus_signature = plus_signature.copy()
    q_rho = plus["q_rho"]
    chain_correct = plus["field_rho"]["Omega"] / q_rho
    chain_omitted = plus["field_rho"]["Omega"]
    return {
        "freeze_groupoid_R_plus": _maximum(freeze_plus_phi - member["targets"]["varphi_H"]),
        "freeze_groupoid_R_minus": _maximum(freeze_minus_phi - member["targets"]["varphi_H"]),
        "rotate_only_phi": _maximum(rotate_only),
        "wrong_R_side": _maximum(np.einsum("...ab,...b->...a", plus["R"], minus["source_phi_trace"]) - member["targets"]["varphi_H"]),
        "wrong_R_sign": _maximum(wrong_transport - member["targets"]["A_Sigma_matrix"]),
        "reuse_plus_jet_on_minus": (
            _maximum(plus_signature - minus_signature)
            - _maximum(plus_signature - reused_minus_signature)
        ),
        "break_common_trace": _maximum(
            plus["fields"]["Omega"][0]
            + 0.031 * _chi(np.asarray([0.0]))[0][0]
            - member["targets"]["Omega"]
        ),
        "omit_collar_chain_rule": _maximum(chain_omitted - chain_correct),
    }


def build_payload() -> dict[str, Any]:
    spec = family_spec()
    upstream = _pin_upstreams()
    members = {seed: build_member(seed) for seed in spec.seeds}
    member_receipts = [_member_receipt(members[seed]) for seed in spec.seeds]
    tangent_receipts = {
        str(seed): [tangent_receipt(seed, tangent) for tangent in admissible_tangents()]
        for seed in spec.seeds
    }
    mutants = _mutant_witnesses(members)
    identity_invariants = member_kinematic_invariants(members[spec.identity_control_seed])
    nonidentity_invariants = [member_kinematic_invariants(members[seed]) for seed in spec.seeds if seed != spec.identity_control_seed]
    member_gluing_max = max(
        value
        for receipt in member_receipts
        for row in receipt["kinematic_invariants"]["per_side_without_cross_side_summation"].values()
        for value in row.values()
    )
    tangent_gluing_max = max(
        row["linearized_gluing_Linf"]
        for receipts in tangent_receipts.values()
        for receipt in receipts
        for row in receipt["per_side_gluing_without_cross_side_summation"].values()
    )
    tangent_activity_min = min(
        value
        for receipts in tangent_receipts.values()
        for receipt in receipts
        for value in receipt["raw_primitive_tangent_L2"].values()
    )
    non_z2_jet_min = min(
        _maximum(_jet_signature(members[seed], "plus") - _jet_signature(members[seed], "minus"))
        for seed in spec.seeds
    )
    checks = {
        "three_or_more_members_sampled": len(spec.seeds) >= 3,
        "identity_R_control_executes": (
            identity_invariants["R_plus_minus_Linf"] < 2.0e-14
            and _maximum(members[0]["sides"]["plus"]["R"] - np.eye(3)) < 2.0e-14
        ),
        "two_noncommuting_distinct_R_members_execute": all(
            item["R_plus_minus_Linf"] > 1.0e-3
            and item["R_plus_R_minus_commutator_Linf"] > 1.0e-5
            for item in nonidentity_invariants
        ),
        "member_gluing_is_built_per_side": member_gluing_max < 3.0e-12,
        "linearized_gluing_holds_for_every_member_side_tangent": tangent_gluing_max < 3.0e-9,
        "all_coupled_primitive_tangent_slots_are_active": tangent_activity_min > 1.0e-7,
        "metric_and_nongravitational_normal_jets_are_non_Z2": non_z2_jet_min > 1.0e-3,
        "B_is_transported_but_not_constrained_across_sides": all(
            receipt["kinematic_invariants"]["B_oriented_flux_equation_imposed"] is False
            and receipt["kinematic_invariants"]["B_oriented_flux_raw_Linf"] > 1.0e-3
            for receipt in member_receipts
        ),
        "all_required_mutants_detected": min(mutants.values()) > 1.0e-5,
        "upstreams_are_byte_pinned_without_derived_consumption": all(
            not row["decision_boolean_consumed"]
            and not row["action_value_or_density_consumed"]
            and not row["Eulerian_or_residual_consumed"]
            and not row["helper_imported_or_called"]
            for row in upstream.values()
        ),
    }
    if not all(checks.values()):
        raise TwoSidedFamilyError(f"family control failed: {checks}")
    decision: dict[str, Any] = {
        "two_sided_groupoid_non_Z2_v5_6_3_family_engine_pass": True,
        "serializable_member_builder_pass": True,
        "admissible_coupled_tangent_builder_pass": True,
        "per_member_side_tangent_gluing_pass": True,
        "raw_metric_and_field_normal_jets_published_pass": True,
        "B_oriented_flux_equation_imposed": False,
        **{key: False for key in FAIL_CLOSED_KEYS},
        "status": "TWO_SIDED_GROUPOID_NON_Z2_FAMILY_ENGINE_PASS__ACTION_EULER_C1_N1_FAIL_CLOSED",
    }
    for key in FAIL_CLOSED_KEYS:
        if decision[key] is not False:
            raise TwoSidedFamilyError(f"fail-closed claim promoted: {key}")
    scientific = {
        "family_spec": json.loads(json.dumps(asdict(spec))),
        "admissible_tangents": [asdict(tangent) for tangent in admissible_tangents()],
        "member_receipts": member_receipts,
        "tangent_receipts": tangent_receipts,
        "mutant_witnesses": mutants,
        "checks": checks,
        "decision": decision,
    }
    generator_path = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "title": "Reusable two-sided P+/P- to Q groupoid and non-Z2 primitive family engine v5.6.3",
        "classification": "theory_only;family_engine;primitive_fields_and_tangents;two_sided_groupoid;C1_N1_fail_closed;B4_B5_not_opened",
        "upstream_byte_pins": upstream,
        "consumer_contract": {
            "family_builder": "build_member(seed,t,x,rho,tangent=None,scale=0)",
            "tangent_builder": "admissible_tangents() and tangent_receipt(seed,tangent)",
            "derived_objects_absent": ["action", "densities", "P", "F", "Euler", "Green", "expected_solution"],
            "consumer_obligation": "reconstruct every derived object from the published primitive member and tangent data",
            "name_separation": {
                "freeze_groupoid_R_plus_minus": "mutant of the local solder/groupoid representatives R_epsilon",
                "freeze_spatial_R3": "different curvature mutant; absent and not consumed by this family engine",
            },
        },
        "evidence_boundary": (
            "The engine publishes multiple primitive two-sided members, raw side jets, and coupled admissible tangents. "
            "Gluing is kinematic and built from Q target data. No action or equation-of-motion closure is evaluated."
        ),
        "scientific": scientific,
        "scientific_sha256": _canonical_sha256(scientific),
        "provenance": {
            "generator": {"path": str(generator_path.relative_to(REPO)), "sha256": _sha256(generator_path)},
            "test": {"path": str(TEST.relative_to(REPO)), "sha256": _sha256(TEST)},
            "upstream_helpers_imported": [],
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "limits": [
            "The member engine is finite and sampled; no convergence or continuous-family theorem follows.",
            "Metric normal jets are primitive inputs only; GHY, R5, R3, and their variations are not evaluated here.",
            "B traces are not identified across sides and the oriented BF interface equation remains open.",
            "R_plus and R_minus are local groupoid representatives, not new bifundamental dynamical fields.",
            "Action, JVP, Euler--Green, C1/N1, LOCK-1 Phase-A, BV--BFV, B4, and B5 remain fail-closed.",
        ],
    }


def main() -> None:
    payload = build_payload()
    encoded = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
