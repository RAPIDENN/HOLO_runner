#!/usr/bin/env python3
"""Finite restricted-spectral family certificate (v5.6.4).

This module constructs only the finite, kinematic fibre products C_N for
N=1,2,3.  It deliberately does not evaluate the v5.2 action, an Eulerian,
a Green identity, Robin data, or any C1/N1 closure claim.

The important distinction in this certificate is between the redundant
ambient coordinate q and the common-first retraction i_N.  The public gluing
map G is evaluated on q *before* retraction.  Its runtime Jacobian therefore
has 52 rows per retained real Fourier mode and full row rank; it is not the
zero Jacobian of G o i_N.  Admissible tangents are obtained from the SVD
kernel of that ambient Jacobian by a complete QR after compact-SVD rank audit.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import scipy
from scipy.linalg import expm, expm_frechet


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_certificate.json"
TEST = HERE / "test_one_omega_topological_so3_restricted_spectral_family_v5_6_4_certificate.py"
SCHEMA = "holo.one-omega-topological-so3-restricted-spectral-family-v5-6-4-certificate.v1"
CERTIFICATE_NAME = "restricted_spectral_family_certificate"


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
    "literal_v5_2_action": SourcePin(
        "one_omega_topological_so3_classical_v5_2_gate.json",
        "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
        "holo.one-omega-topological-so3-classical-v5-2-gate.v1",
        "derive_one_omega_topological_so3_classical_v5_2_gate.py",
        "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
        "test_one_omega_topological_so3_classical_v5_2_gate.py",
        "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
    ),
    "level_zero_v5_6_3_fixture": SourcePin(
        "one_omega_topological_so3_two_sided_groupoid_non_z2_v5_6_3_gate.json",
        "0704cb80c0e49e3fd60b3165145a20d3dc489a39ce356eecbb0bdc87ab079bbf",
        "holo.one-omega-topological-so3-two-sided-groupoid-non-z2-v5-6-3-gate.v1",
        "derive_one_omega_topological_so3_two_sided_groupoid_non_z2_v5_6_3_gate.py",
        "7391dd142a5fd45bb8e4cc9d2137a4f326fcfe482c02adfd31075c7920da7fc8",
        "test_one_omega_topological_so3_two_sided_groupoid_non_z2_v5_6_3_gate.py",
        "cfb08fa3609f8c64c6f3ad0020b11aa3c2cffdbb9c18fdf777afa3904b643118",
    ),
}


FAIL_CLOSED_KEYS = (
    "finite_C_N_action_closure_pass",
    "numerical_C_N_action_certificate_pass",
    "total_v5_2_action_reexecuted_pass",
    "AD_JVP_literal_action_pass",
    "high_order_or_high_precision_finite_difference_action_pass",
    "independent_action_route_graph_pass",
    "bulk_compact_support_SO3_Ward_pass",
    "bulk_residual_pass",
    "interface_residual_pass",
    "corner_residual_pass",
    "Robin_residual_pass",
    "Green_identity_pass",
    "action_gluing_residual_pass",
    "derivative_step_convergence_pass",
    "quadrature_convergence_pass",
    "mesh_convergence_pass",
    "spectral_N_convergence_pass",
    "full_physical_gauge_quotient_pass",
    "BF_shift_quotient_pass",
    "bulk_diffeomorphism_quotient_pass",
    "brane_reparametrization_quotient_pass",
    "khronon_reparametrization_quotient_pass",
    "continuous_C1_N1_theorem_pass",
    "density_union_C_N_pass",
    "uniform_stability_pass",
    "N_to_infinity_limit_control_pass",
    "periodic_box_exhaustion_and_tail_control_pass",
    "Sobolev_or_mass_weighted_uniform_singular_bound_pass",
    "mass_weighted_horizontal_pass",
    "H_N_neighborhood_smooth_equivariance_pass",
    "finite_H_N_reachable_chart_pass",
    "local_horizontal_reachability_theorem_pass",
    "analytic_global_signature_preservation_pass",
    "padded_off_grid_regularity_pass",
    "legacy_147_regression_executed_pass",
    "restricted_family_exact_action_identity_pass",
    "C1_ACTION_selected_family_pass",
    "N1_ACTION_selected_family_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "mutant_action_campaign_pass",
    "independent_redteam_replication_pass",
    "clean_process_artifact_regeneration_pass",
    "independent_reserved_seed_protocol_pass",
    "passive_Phase_A_J_disengaged_pass",
    "LOCK_1_contamination_cleared_pass",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
)


TRUNCATIONS = (1, 2, 3)
IDENTITY_CONTROL_SEED = 0
DEVELOPMENT_SEED = 20260902
PRIMARY_SEEDS = (IDENTITY_CONTROL_SEED, DEVELOPMENT_SEED)
RESERVED_SEED_DOMAINS = (
    "restricted-spectral-holdout-1",
    "restricted-spectral-holdout-2",
)
SIDES = ("plus", "minus")
NORMAL_REFLECTION = np.diag((1.0, 1.0, 1.0, 1.0, -1.0))
V5_2_EXACT_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
SYMMETRIC4 = tuple((i, j) for i in range(4) for j in range(i, 4))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))
RADIAL_SAMPLE = np.asarray((0.0, 0.15, 0.37, 0.63, 0.85, 1.0, 1.2), dtype=float)
SOBLEV_TARGET_S = 4.75
SPECTRAL_DECAY_POWER = 8.0


TOLERANCES = {
    "gluing_Linf": 2.0e-10,
    "rank_relative_multiplier": 128.0,
    "kernel_residual_L2": 2.0e-9,
    "orthonormality_Linf": 2.0e-10,
    "retraction_pushforward_residual_L2": 2.0e-7,
    "retraction_rank_relative": 2.0e-8,
    "signature_eigenvalue_margin": 2.0e-2,
    "Omega_min": 5.0e-1,
    "timelike_margin": 2.0e-1,
    "rotation_cut_locus_margin": 1.0,
    "nonidentity_rotation_Linf": 1.0e-3,
    "independent_embedding_L2": 1.0e-3,
    "SO3_horizontal_tangent_activity_L2": 1.0e-7,
    "SO3_horizontal_non_Z2_L2": 1.0e-5,
    "complex_step": 1.0e-30,
    "retraction_step": 2.0e-6,
    "reachable_chart_step": 2.0e-5,
    "reachable_chart_G_Linf": 2.0e-10,
    "reachable_chart_first_order_L2": 2.0e-5,
    "reachable_chart_activity_L2": 1.0e-10,
}


class SpectralCertificateError(ValueError):
    """The finite family, a source pin, or a fail-closed boundary drifted."""


class VectorLayout:
    """Stable named slices for a flat primitive coordinate vector."""

    def __init__(self) -> None:
        self.size = 0
        self.rows: dict[str, tuple[slice, tuple[int, ...]]] = {}

    def add(self, name: str, shape: tuple[int, ...]) -> None:
        width = int(np.prod(shape))
        self.rows[name] = (slice(self.size, self.size + width), shape)
        self.size += width

    def put(self, vector: np.ndarray, name: str, value: np.ndarray) -> None:
        block, shape = self.rows[name]
        array = np.asarray(value)
        if array.shape != shape:
            raise SpectralCertificateError(f"{name} shape {array.shape} != {shape}")
        vector[block] = array.reshape(-1)

    def get(self, vector: np.ndarray, name: str) -> np.ndarray:
        block, shape = self.rows[name]
        return vector[block].reshape(shape)

    def indices(self, name: str) -> np.ndarray:
        block, _ = self.rows[name]
        return np.arange(block.start, block.stop, dtype=int)

    def contract(self) -> dict[str, Any]:
        return {
            name: {
                "start": block.start,
                "stop": block.stop,
                "shape": list(shape),
            }
            for name, (block, shape) in self.rows.items()
        }


def ambient_layout(N: int) -> VectorLayout:
    _validate_N(N)
    K = radial_truncation(N)
    layout = VectorLayout()
    layout.add("common.gamma", (N, 10))
    layout.add("common.T", (N, 1))
    layout.add("common.log_Omega", (N, 1))
    layout.add("common.varphi", (N, 3))
    layout.add("common.A_Sigma", (N, 4, 3))
    layout.add("Q_frame.q", (N, 3))
    for side in SIDES:
        prefix = f"{side}."
        layout.add(prefix + "Y", (N, 1))
        layout.add(prefix + "g_trace", (N, 15))
        layout.add(prefix + "log_Omega_trace", (N, 1))
        layout.add(prefix + "phi_trace", (N, 3))
        layout.add(prefix + "A_trace_full", (N, 5, 3))
        layout.add(prefix + "r", (N, 3))
        layout.add(prefix + "B_trace_full", (N, 10, 3))
        layout.add(prefix + "boundary_jet_J1", (N, 64))
        layout.add(prefix + "interior_bump_C", (N, K, 64))
    if layout.size != (294 + 128 * K) * N:
        raise SpectralCertificateError("ambient dimension contract drift")
    return layout


def free_layout(N: int) -> VectorLayout:
    _validate_N(N)
    K = radial_truncation(N)
    layout = VectorLayout()
    layout.add("common.gamma", (N, 10))
    layout.add("common.T", (N, 1))
    layout.add("common.log_Omega", (N, 1))
    layout.add("common.varphi_E0", (N, 3))
    layout.add("common.A_E0", (N, 4, 3))
    layout.add("Q_frame.q", (N, 3))
    for side in SIDES:
        prefix = f"{side}."
        layout.add(prefix + "Y", (N, 1))
        layout.add(prefix + "metric_free", (N, 5))
        layout.add(prefix + "A_perp", (N, 3))
        layout.add(prefix + "B0_full", (N, 10, 3))
        layout.add(prefix + "r_E0", (N, 3))
        layout.add(prefix + "boundary_jet_J1", (N, 64))
        layout.add(prefix + "interior_bump_C", (N, K, 64))
    if layout.size != (242 + 128 * K) * N:
        raise SpectralCertificateError("free dimension contract drift")
    return layout


def _validate_N(N: int) -> None:
    if not isinstance(N, int) or isinstance(N, bool) or N <= 0:
        raise SpectralCertificateError("N must be a positive integer")


def radial_truncation(N: int) -> int:
    """Diagonal exhaustion K(N)=N for the compact radial bump basis."""

    _validate_N(N)
    return N


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise SpectralCertificateError(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(value), dtype="<f8")
    return hashlib.sha256(array.tobytes()).hexdigest()


def _encode_f64le(value: np.ndarray) -> dict[str, Any]:
    """Portable primitive array encoding that avoids multi-megabyte JSON floats."""

    array = np.ascontiguousarray(np.asarray(value), dtype="<f8")
    raw = array.tobytes()
    return {
        "encoding": "base64",
        "dtype": "<f8",
        "shape": list(array.shape),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "data": base64.b64encode(raw).decode("ascii"),
    }


def _pin_upstreams() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, pin in SOURCE_PINS.items():
        paths = {
            "artifact": HERE / "artifacts" / pin.artifact,
            "generator": HERE / pin.generator,
            "test": HERE / pin.test,
        }
        actual = {kind: _sha256(path) for kind, path in paths.items()}
        expected = {
            "artifact": pin.artifact_sha256,
            "generator": pin.generator_sha256,
            "test": pin.test_sha256,
        }
        if actual != expected:
            raise SpectralCertificateError(f"{name} source drift: {actual}")
        schema = json.loads(paths["artifact"].read_text(encoding="utf-8")).get("schema")
        if schema != pin.schema:
            raise SpectralCertificateError(f"{name} schema drift: {schema}")
        result[name] = {
            "schema": schema,
            "paths": {kind: str(path.relative_to(REPO)) for kind, path in paths.items()},
            "sha256": actual,
            "role": "immutable_literal_action_pin_only" if name == "literal_v5_2_action" else "level_zero_lineage_fixture_only",
            "python_helper_imported_or_called": False,
            "decision_boolean_consumed": False,
            "prediction_consumed": False,
            "ledger_consumed": False,
            "action_value_consumed": False,
        }
        if name == "literal_v5_2_action":
            artifact = json.loads(paths["artifact"].read_text(encoding="utf-8"))
            exact_action = artifact["exact_classical_charter"]["exact_action"]
            exact_action_hash = _canonical_sha256(exact_action)
            if exact_action_hash != V5_2_EXACT_ACTION_SHA256:
                raise SpectralCertificateError("v5.2 exact_action literal drift")
            result[name]["literal_exact_action_pin"] = {
                "json_path": "exact_classical_charter.exact_action",
                "canonicalization": "json.dumps(sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')",
                "canonical_byte_length": len(json.dumps(exact_action, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")),
                "sha256": exact_action_hash,
                "literal_content_exported_to_evaluators": False,
            }
    return result


def real_fourier_basis(N: int) -> dict[str, Any]:
    """First N elements of a declared nested real Fourier basis on T^4."""

    _validate_N(N)
    priority = [(1, 1, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    wavevectors: list[tuple[int, int, int, int]] = []
    for vector in priority:
        if vector not in wavevectors:
            wavevectors.append(vector)
    radius = 1
    while len(wavevectors) < max(1, (N - 1 + 1) // 2):
        candidates: list[tuple[int, int, int, int]] = []
        for a in range(-radius, radius + 1):
            for b in range(-radius, radius + 1):
                for c in range(-radius, radius + 1):
                    for d in range(-radius, radius + 1):
                        vector = (a, b, c, d)
                        if vector == (0, 0, 0, 0) or max(map(abs, vector)) != radius:
                            continue
                        first = next(item for item in vector if item != 0)
                        if first < 0:
                            continue
                        candidates.append(vector)
        for vector in sorted(candidates, key=lambda item: (sum(map(abs, item)), item)):
            if vector not in wavevectors:
                wavevectors.append(vector)
        radius += 1

    irrational = np.sqrt(np.asarray((2.0, 3.0, 5.0, 7.0)))
    points = 2.0 * math.pi * np.mod(
        (np.arange(N, dtype=float)[:, None] + 0.173) * irrational[None, :], 1.0
    )
    labels: list[str] = ["1"]
    columns: list[np.ndarray] = [np.ones(N)]
    derivative_columns: list[list[np.ndarray]] = [[np.zeros(N)] for _ in range(4)]
    mode_wavevectors: list[list[int]] = [[0, 0, 0, 0]]
    for index in range(1, N):
        vector = np.asarray(wavevectors[(index - 1) // 2], dtype=float)
        phase = points @ vector
        cosine_mode = index % 2 == 1
        labels.append(
            ("cos" if cosine_mode else "sin")
            + "("
            + "+".join(f"{int(k)}*x{mu}" for mu, k in enumerate(vector) if k)
            + ")"
        )
        columns.append(np.cos(phase) if cosine_mode else np.sin(phase))
        mode_wavevectors.append(vector.astype(int).tolist())
        for mu in range(4):
            derivative_columns[mu].append(
                -vector[mu] * np.sin(phase)
                if cosine_mode
                else vector[mu] * np.cos(phase)
            )
    values = np.stack(columns, axis=-1)
    derivatives = np.stack(
        tuple(np.stack(columns_mu, axis=-1) for columns_mu in derivative_columns),
        axis=0,
    )
    inverse = np.linalg.inv(values)
    return {
        "labels": tuple(labels),
        "points_T4": points,
        "mode_wavevectors": mode_wavevectors,
        "values": values,
        "derivatives": derivatives,
        "inverse": inverse,
        "condition_number": float(np.linalg.cond(values)),
    }


def _coefficients(seed: int, label: str, shape: tuple[int, ...], scale: float = 1.0) -> np.ndarray:
    result = np.empty(shape, dtype=float)
    for flat in range(result.size):
        digest = hashlib.sha256(f"v5.6.4:{seed}:{label}:{flat}".encode("ascii")).digest()
        unit = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
        result.reshape(-1)[flat] = scale * (2.0 * unit - 1.0)
    return result


def _spectral_coefficients(
    seed: int, label: str, shape: tuple[int, ...], scale: float = 1.0
) -> np.ndarray:
    """N-independent coefficients with declared T^4 Sobolev decay by mode."""

    if not shape:
        raise SpectralCertificateError("spectral coefficient shape must have a mode axis")
    N = shape[0]
    raw = _coefficients(seed, label, shape, scale)
    wavevectors = np.asarray(real_fourier_basis(N)["mode_wavevectors"], dtype=float)
    weights = (1.0 + np.sum(wavevectors * wavevectors, axis=1)) ** (
        -0.5 * SPECTRAL_DECAY_POWER
    )
    return raw * weights.reshape((N,) + (1,) * (len(shape) - 1))


def _spectral_radial_coefficients(
    seed: int, label: str, N: int, channels: int, scale: float = 1.0
) -> np.ndarray:
    """Nested coefficients indexed independently by tangential mode and bump."""

    K = radial_truncation(N)
    wavevectors = np.asarray(real_fourier_basis(N)["mode_wavevectors"], dtype=float)
    weights = (1.0 + np.sum(wavevectors * wavevectors, axis=1)) ** (
        -0.5 * SPECTRAL_DECAY_POWER
    )
    result = np.empty((N, K, channels), dtype=float)
    for mode in range(N):
        for radial in range(K):
            for channel in range(channels):
                digest = hashlib.sha256(
                    f"v5.6.4:{seed}:{label}:m{mode}:k{radial}:c{channel}".encode(
                        "ascii"
                    )
                ).digest()
                unit = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
                radial_weight = (1.0 + radial * radial) ** (
                    -0.5 * SPECTRAL_DECAY_POWER
                )
                result[mode, radial, channel] = (
                    scale * weights[mode] * radial_weight * (2.0 * unit - 1.0)
                )
    return result


def _sym_to_vec(matrix: np.ndarray, pairs: tuple[tuple[int, int], ...]) -> np.ndarray:
    return np.stack(tuple(matrix[..., i, j] for i, j in pairs), axis=-1)


def _vec_to_sym(vector: np.ndarray, size: int, pairs: tuple[tuple[int, int], ...]) -> np.ndarray:
    result = np.zeros(vector.shape[:-1] + (size, size), dtype=vector.dtype)
    for index, (i, j) in enumerate(pairs):
        result[..., i, j] = vector[..., index]
        result[..., j, i] = vector[..., index]
    return result


def _hat(vector: np.ndarray) -> np.ndarray:
    result = np.zeros(vector.shape[:-1] + (3, 3), dtype=vector.dtype)
    result[..., 0, 1], result[..., 0, 2] = -vector[..., 2], vector[..., 1]
    result[..., 1, 0], result[..., 1, 2] = vector[..., 2], -vector[..., 0]
    result[..., 2, 0], result[..., 2, 1] = -vector[..., 1], vector[..., 0]
    return result


def _vee(matrix: np.ndarray) -> np.ndarray:
    return np.stack((matrix[..., 2, 1], matrix[..., 0, 2], matrix[..., 1, 0]), axis=-1)


def _rotation_nodes(r_coeff: np.ndarray, basis: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Return R=exp(hat(r)) and exact d_mu R from Frechet derivatives."""

    values = basis["values"] @ r_coeff
    derivatives_mu = basis["derivatives"] @ r_coeff
    rotations = np.empty((values.shape[0], 3, 3), dtype=values.dtype)
    derivatives = np.empty((values.shape[0], 4, 3, 3), dtype=values.dtype)
    for node in range(values.shape[0]):
        algebra = _hat(values[node])
        rotations[node] = expm(algebra)
        for mu in range(4):
            direction = _hat(derivatives_mu[mu, node])
            derivatives[node, mu] = expm_frechet(algebra, direction, compute_expm=False)
    return rotations, derivatives


def _so3_log(rotation: np.ndarray) -> np.ndarray:
    cosine = float(np.clip((np.trace(rotation) - 1.0) / 2.0, -1.0, 1.0))
    angle = math.acos(cosine)
    antisymmetric = rotation - rotation.T
    if angle < 1.0e-9:
        return 0.5 * _vee(antisymmetric)
    return angle * _vee(antisymmetric) / (2.0 * math.sin(angle))


def _radial_profile_data(
    rho: np.ndarray = RADIAL_SAMPLE, K: int = 1
) -> dict[str, np.ndarray]:
    """Restricted h0/J1 boundary lifts and K compact bump-polynomial modes."""

    rho = np.asarray(rho, dtype=float)
    cutoff = np.zeros_like(rho)
    cutoff_prime = np.zeros_like(rho)
    half_open = (rho >= 0.0) & (rho < 1.0)
    s = rho[half_open]
    cutoff[half_open] = np.exp(-(s / (1.0 - s)) ** 2)
    cutoff_prime[half_open] = cutoff[half_open] * (-2.0 * s / (1.0 - s) ** 3)
    boundary_lifts = np.column_stack((cutoff, rho * cutoff))
    boundary_lifts_prime = np.column_stack(
        (cutoff_prime, cutoff + rho * cutoff_prime)
    )
    boundary_jet_matrix = np.eye(2)

    bump_envelope = np.zeros_like(rho)
    bump_envelope_prime = np.zeros_like(rho)
    interior = (rho > 0.0) & (rho < 1.0)
    s = rho[interior]
    bump_envelope[interior] = np.exp(4.0 - 1.0 / (s * (1.0 - s)))
    bump_envelope_prime[interior] = bump_envelope[interior] * (
        (1.0 - 2.0 * s) / (s * s * (1.0 - s) ** 2)
    )
    bumps = np.zeros((rho.size, K), dtype=float)
    bumps_prime = np.zeros((rho.size, K), dtype=float)
    coordinate = 2.0 * rho - 1.0
    for radial in range(K):
        polynomial = np.polynomial.legendre.Legendre.basis(radial)
        values = polynomial(coordinate)
        derivatives = 2.0 * polynomial.deriv()(coordinate)
        bumps[:, radial] = bump_envelope * values
        bumps_prime[:, radial] = (
            bump_envelope_prime * values + bump_envelope * derivatives
        )
    return {
        "boundary_lifts": boundary_lifts,
        "boundary_lifts_prime": boundary_lifts_prime,
        "boundary_jet_matrix": boundary_jet_matrix,
        "bumps": bumps,
        "bumps_prime": bumps_prime,
    }


def _radial_profiles(N: int, rho: np.ndarray = RADIAL_SAMPLE) -> np.ndarray:
    profiles = _radial_profile_data(rho, radial_truncation(N))
    return np.column_stack((profiles["boundary_lifts"], profiles["bumps"]))


def bulk_primitives(q: np.ndarray, N: int, rho: np.ndarray = RADIAL_SAMPLE) -> dict[str, Any]:
    """Decode raw v5.2 primitive fields and radial derivatives from ambient q."""

    rho = np.asarray(rho, dtype=float)
    basis = real_fourier_basis(N)
    F = basis["values"]
    layout = ambient_layout(N)
    q = np.asarray(q, dtype=float)
    K = radial_truncation(N)
    profiles = _radial_profile_data(rho, K)
    triples = tuple(
        (i, j, k)
        for i in range(5)
        for j in range(i + 1, 5)
        for k in range(j + 1, 5)
    )
    result: dict[str, Any] = {}
    for side in SIDES:
        g_trace = _vec_to_sym(F @ layout.get(q, f"{side}.g_trace"), 5, SYMMETRIC5)
        log_Omega_trace = (
            F @ layout.get(q, f"{side}.log_Omega_trace")
        )[..., 0]
        phi_trace = F @ layout.get(q, f"{side}.phi_trace")
        A_X0 = (F @ layout.get(q, f"{side}.A_trace_full").reshape(N, 15)).reshape(N, 5, 3)
        B_X0 = (F @ layout.get(q, f"{side}.B_trace_full").reshape(N, 30)).reshape(N, 10, 3)
        J = F @ layout.get(q, f"{side}.boundary_jet_J1")
        C = (
            F @ layout.get(q, f"{side}.interior_bump_C").reshape(N, K * 64)
        ).reshape(N, K, 64)
        g_J = _vec_to_sym(J[:, :15], 5, SYMMETRIC5)
        g_C = _vec_to_sym(C[:, :, :15], 5, SYMMETRIC5)
        Omega_J, Omega_C = J[:, 15], C[:, :, 15]
        phi_J, phi_C = J[:, 16:19], C[:, :, 16:19]
        A_J = J[:, 19:34].reshape(N, 5, 3)
        A_C = C[:, :, 19:34].reshape(N, K, 5, 3)
        B_J = J[:, 34:64].reshape(N, 10, 3)
        B_C = C[:, :, 34:64].reshape(N, K, 10, 3)

        boundary_lifts = profiles["boundary_lifts"]
        boundary_lifts_prime = profiles["boundary_lifts_prime"]
        trace_lift = boundary_lifts[:, 0]
        trace_lift_prime = boundary_lifts_prime[:, 0]
        jet_lift = boundary_lifts[:, 1]
        jet_lift_prime = boundary_lifts_prime[:, 1]
        bumps = profiles["bumps"]
        bumps_prime = profiles["bumps_prime"]
        reference_metric = np.diag((-1.64, 1.17, 1.31, 1.46, 1.17))
        metric = (
            reference_metric[None, None, ...]
            + trace_lift[:, None, None, None]
            * (g_trace[None, ...] - reference_metric[None, None, ...])
            + jet_lift[:, None, None, None] * g_J[None, ...]
            + np.einsum("rk,nkij->rnij", bumps, g_C)
        )
        metric_rho = (
            trace_lift_prime[:, None, None, None]
            * (g_trace[None, ...] - reference_metric[None, None, ...])
            + jet_lift_prime[:, None, None, None] * g_J[None, ...]
            + np.einsum("rk,nkij->rnij", bumps_prime, g_C)
        )
        log_Omega = (
            trace_lift[:, None] * log_Omega_trace[None, :]
            + jet_lift[:, None] * Omega_J[None, :]
            + np.einsum("rk,nk->rn", bumps, Omega_C)
        )
        log_Omega_rho = (
            trace_lift_prime[:, None] * log_Omega_trace[None, :]
            + jet_lift_prime[:, None] * Omega_J[None, :]
            + np.einsum("rk,nk->rn", bumps_prime, Omega_C)
        )
        Omega = np.exp(log_Omega)
        Omega_rho = Omega * log_Omega_rho
        phi = trace_lift[:, None, None] * phi_trace[None, ...] + jet_lift[:, None, None] * phi_J[None, ...] + np.einsum("rk,nka->rna", bumps, phi_C)
        phi_rho = trace_lift_prime[:, None, None] * phi_trace[None, ...] + jet_lift_prime[:, None, None] * phi_J[None, ...] + np.einsum("rk,nka->rna", bumps_prime, phi_C)
        connection = trace_lift[:, None, None, None] * A_X0[None, ...] + jet_lift[:, None, None, None] * A_J[None, ...] + np.einsum("rk,nkma->rnma", bumps, A_C)
        connection_rho = trace_lift_prime[:, None, None, None] * A_X0[None, ...] + jet_lift_prime[:, None, None, None] * A_J[None, ...] + np.einsum("rk,nkma->rnma", bumps_prime, A_C)
        B_field = trace_lift[:, None, None, None] * B_X0[None, ...] + jet_lift[:, None, None, None] * B_J[None, ...] + np.einsum("rk,nkja->rnja", bumps, B_C)
        B_rho = trace_lift_prime[:, None, None, None] * B_X0[None, ...] + jet_lift_prime[:, None, None, None] * B_J[None, ...] + np.einsum("rk,nkja->rnja", bumps_prime, B_C)
        result[side] = {
            "values": {
                "g_MN": metric,
                "Omega": Omega,
                "phi_a": phi,
                "A_Ma": connection,
                "B_MNP_a": B_field,
            },
            "radial_derivatives": {
                "g_MN": metric_rho,
                "Omega": Omega_rho,
                "phi_a": phi_rho,
                "A_Ma": connection_rho,
                "B_MNP_a": B_rho,
            },
            "component_contract": {
                "g_MN": 15,
                "Omega": 1,
                "phi_a": 3,
                "A_Ma": 15,
                "B_MNP_a": 30,
                "X0_channels": 64,
                "free_boundary_jet_orders": [1],
                "channels_per_boundary_jet": 64,
                "C_bump_channels_per_radial_mode": 64,
                "radial_bump_mode_count": K,
                "Omega_coordinate": "log_Omega; physical Omega=exp(log_Omega)",
                "asymptotic_reference": "diag(-1.64,1.17,1.31,1.46,1.17), Omega=1, phi=A=B=0",
                "B_form_index_order": [list(item) for item in triples],
                "B_X0_form_index_order": [list(item) for item in triples],
            },
        }
    return result


def _frame_from_gamma_T(gamma: np.ndarray, T_coeff: np.ndarray, basis: Mapping[str, Any]) -> dict[str, np.ndarray]:
    inverse = np.linalg.inv(gamma)
    T_derivatives = (basis["derivatives"] @ T_coeff)[..., 0]
    gradient = np.swapaxes(T_derivatives, 0, 1)
    gradient[:, 0] += 1.0
    norm2 = np.einsum("nij,ni,nj->n", inverse, gradient, gradient)
    normalization = np.sqrt(-norm2)
    u_cov = -gradient / normalization[:, None]
    u = np.einsum("nij,nj->ni", inverse, u_cov)
    frame = np.empty((gamma.shape[0], 4, 3), dtype=float)
    for node in range(gamma.shape[0]):
        for column in range(3):
            candidate = np.zeros(4)
            candidate[column + 1] = 1.0
            candidate += u[node] * u_cov[node, column + 1]
            for previous in range(column):
                projection = frame[node, :, previous] @ gamma[node] @ candidate
                candidate -= projection * frame[node, :, previous]
            length = math.sqrt(float(candidate @ gamma[node] @ candidate))
            frame[node, :, column] = candidate / length
    return {
        "E0": frame,
        "T_gradient": gradient,
        "T_norm2": norm2,
        "u_cov": u_cov,
        "u": u,
    }


def build_free_coordinates(seed: int, N: int) -> np.ndarray:
    """Generate B_N first, then independent side/interior free data."""

    _validate_N(N)
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise SpectralCertificateError("seed must be a nonnegative integer")
    layout = free_layout(N)
    free = np.zeros(layout.size, dtype=float)

    # B_N=(gamma,T,Omega_Sigma,varphi_H,A_Sigma), all generated before sides.
    gamma_coeff = _spectral_coefficients(seed, "base:gamma", (N, 10), 0.004)
    gamma0 = np.diag((-1.64, 1.17, 1.31, 1.46))
    gamma_coeff[0] += _sym_to_vec(gamma0, SYMMETRIC4)
    layout.put(free, "common.gamma", gamma_coeff)
    layout.put(free, "common.T", _spectral_coefficients(seed, "base:T", (N, 1), 0.006))
    log_Omega_coeff = _spectral_coefficients(seed, "base:log_Omega", (N, 1), 0.012)
    log_Omega_coeff[0, 0] += math.log(1.08)
    layout.put(free, "common.log_Omega", log_Omega_coeff)
    layout.put(free, "common.varphi_E0", _spectral_coefficients(seed, "base:varphi", (N, 3), 0.24))
    layout.put(free, "common.A_E0", _spectral_coefficients(seed, "base:A", (N, 4, 3), 0.11))
    q_frame = np.zeros((N, 3)) if seed == IDENTITY_CONTROL_SEED else _spectral_coefficients(seed, "base:Q_frame", (N, 3), 0.055)
    layout.put(free, "Q_frame.q", q_frame)

    # Only after B_N is complete are P_+ and P_- drawn independently.
    for side in SIDES:
        sign = 1.0 if side == "plus" else -1.0
        Y_coeff = _spectral_coefficients(seed, f"{side}:Y", (N, 1), 0.022)
        Y_coeff[0, 0] += sign * 0.19
        layout.put(free, f"{side}.Y", Y_coeff)
        metric_free = _spectral_coefficients(seed, f"{side}:metric_free", (N, 5), 0.007)
        metric_free[0, 4] += 1.17
        layout.put(free, f"{side}.metric_free", metric_free)
        layout.put(free, f"{side}.A_perp", _spectral_coefficients(seed, f"{side}:A_perp", (N, 3), 0.09))
        layout.put(free, f"{side}.B0_full", _spectral_coefficients(seed, f"{side}:B0_full", (N, 10, 3), 0.13))
        r_E0 = np.zeros((N, 3)) if seed == IDENTITY_CONTROL_SEED else _spectral_coefficients(seed, f"{side}:r_E0", (N, 3), 0.14)
        layout.put(free, f"{side}.r_E0", r_E0)
        layout.put(
            free,
            f"{side}.boundary_jet_J1",
            _spectral_coefficients(seed, f"{side}:boundary_jet_J1", (N, 64), 0.045),
        )
        layout.put(
            free,
            f"{side}.interior_bump_C",
            _spectral_radial_coefficients(seed, f"{side}:C", N, 64, 0.12),
        )
    return free


def free_coefficients_are_prefix_nested(seed: int, lower: int, upper: int) -> bool:
    if not (0 < lower < upper):
        raise SpectralCertificateError("nesting comparison requires 0 < lower < upper")
    lower_layout, upper_layout = free_layout(lower), free_layout(upper)
    lower_vector = build_free_coordinates(seed, lower)
    upper_vector = build_free_coordinates(seed, upper)
    if set(lower_layout.rows) != set(upper_layout.rows):
        return False
    for name in lower_layout.rows:
        lower_block = lower_layout.get(lower_vector, name)
        upper_block = upper_layout.get(upper_vector, name)
        if name.endswith("interior_bump_C"):
            candidate = upper_block[:lower, : radial_truncation(lower)]
        else:
            candidate = upper_block[:lower]
        if not np.array_equal(lower_block, candidate):
            return False
    return True


def construct_ambient_point(free: np.ndarray, N: int, *, details: bool = False) -> Any:
    """Common-first retraction i_N from free data into redundant ambient q."""

    basis = real_fourier_basis(N)
    F, D, Finv = basis["values"], basis["derivatives"], basis["inverse"]
    source = free_layout(N)
    target = ambient_layout(N)
    free = np.asarray(free, dtype=float)
    if free.shape != (source.size,):
        raise SpectralCertificateError("free coordinate shape drift")
    q = np.zeros(target.size, dtype=float)

    gamma_coeff = source.get(free, "common.gamma")
    gamma_nodes = _vec_to_sym(F @ gamma_coeff, 4, SYMMETRIC4)
    T_coeff = source.get(free, "common.T")
    log_Omega_coeff = source.get(free, "common.log_Omega")
    varphi0_coeff = source.get(free, "common.varphi_E0")
    A0_coeff = source.get(free, "common.A_E0")
    frame_q_coeff = source.get(free, "Q_frame.q")
    frame0 = _frame_from_gamma_T(gamma_nodes, T_coeff, basis)
    S, dS = _rotation_nodes(frame_q_coeff, basis)
    frame = frame0["E0"] @ np.swapaxes(S, -1, -2)
    varphi0_nodes = F @ varphi0_coeff
    A0_nodes = F @ A0_coeff.reshape(N, 12)
    A0_nodes = A0_nodes.reshape(N, 4, 3)
    varphi_nodes = np.einsum("nij,nj->ni", S, varphi0_nodes)
    A_nodes = np.empty_like(A0_nodes)
    for node in range(N):
        for mu in range(4):
            matrix = S[node] @ _hat(A0_nodes[node, mu]) @ S[node].T - dS[node, mu] @ S[node].T
            A_nodes[node, mu] = _vee(matrix)

    target.put(q, "common.gamma", gamma_coeff)
    target.put(q, "common.T", T_coeff)
    target.put(q, "common.log_Omega", log_Omega_coeff)
    target.put(q, "common.varphi", Finv @ varphi_nodes)
    target.put(q, "common.A_Sigma", (Finv @ A_nodes.reshape(N, 12)).reshape(N, 4, 3))
    target.put(q, "Q_frame.q", frame_q_coeff)

    side_details: dict[str, Any] = {}
    for side in SIDES:
        Y_coeff = source.get(free, f"{side}.Y")
        Y_nodes = (F @ Y_coeff)[..., 0]
        Y_gradient = np.swapaxes((D @ Y_coeff)[..., 0], 0, 1)
        metric_free_coeff = source.get(free, f"{side}.metric_free")
        metric_free_nodes = F @ metric_free_coeff
        cross_adapted = metric_free_nodes[:, :4]
        normal_metric = metric_free_nodes[:, 4]
        g_nodes = np.empty((N, 5, 5), dtype=float)
        for node in range(N):
            y = Y_gradient[node]
            d = cross_adapted[node]
            a = normal_metric[node]
            upper = gamma_nodes[node] - np.outer(d, y) - np.outer(y, d) + a * np.outer(y, y)
            ambient_cross = d - a * y
            g_nodes[node, :4, :4] = upper
            g_nodes[node, :4, 4] = ambient_cross
            g_nodes[node, 4, :4] = ambient_cross
            g_nodes[node, 4, 4] = a

        r0_coeff = source.get(free, f"{side}.r_E0")
        R0, _ = _rotation_nodes(r0_coeff, basis)
        r_nodes = np.empty((N, 3), dtype=float)
        for node in range(N):
            r_nodes[node] = _so3_log(S[node] @ R0[node])
        r_coeff = Finv @ r_nodes
        R, dR = _rotation_nodes(r_coeff, basis)
        phi_source = np.einsum("nji,nj->ni", R, varphi_nodes)
        A_source = np.empty_like(A_nodes)
        for node in range(N):
            for mu in range(4):
                matrix = R[node].T @ _hat(A_nodes[node, mu]) @ R[node] + R[node].T @ dR[node, mu]
                A_source[node, mu] = _vee(matrix)

        target.put(q, f"{side}.Y", Y_coeff)
        target.put(q, f"{side}.g_trace", Finv @ _sym_to_vec(g_nodes, SYMMETRIC5))
        target.put(q, f"{side}.log_Omega_trace", log_Omega_coeff)
        target.put(q, f"{side}.phi_trace", Finv @ phi_source)
        A_perp_coeff = source.get(free, f"{side}.A_perp")
        A_perp_nodes = F @ A_perp_coeff
        A_source_full_nodes = np.zeros((N, 5, 3))
        A_source_full_nodes[:, :4] = A_source - Y_gradient[:, :, None] * A_perp_nodes[:, None, :]
        A_source_full_nodes[:, 4] = A_perp_nodes
        target.put(
            q,
            f"{side}.A_trace_full",
            (Finv @ A_source_full_nodes.reshape(N, 15)).reshape(N, 5, 3),
        )
        target.put(q, f"{side}.r", r_coeff)
        B_nodes = F @ source.get(free, f"{side}.B0_full").reshape(N, 30)
        B_nodes = B_nodes.reshape(N, 10, 3)
        target.put(q, f"{side}.B_trace_full", source.get(free, f"{side}.B0_full"))
        target.put(q, f"{side}.boundary_jet_J1", source.get(free, f"{side}.boundary_jet_J1"))
        target.put(q, f"{side}.interior_bump_C", source.get(free, f"{side}.interior_bump_C"))
        side_details[side] = {
            "Y_nodes": Y_nodes,
            "Y_gradient": Y_gradient,
            "g_nodes": g_nodes,
            "R_nodes": R,
            "dR_nodes": dR,
            "r_nodes": F @ r_coeff,
            "phi_source": phi_source,
            "A_source": A_source,
            "B_nodes": B_nodes,
            "boundary_jet_J1_nodes": F @ source.get(free, f"{side}.boundary_jet_J1"),
            "C_nodes": (
                F
                @ source.get(free, f"{side}.interior_bump_C").reshape(
                    N, radial_truncation(N) * 64
                )
            ).reshape(N, radial_truncation(N), 64),
        }
    if not details:
        return q
    return q, {
        "gamma_nodes": gamma_nodes,
        "T_coeff": T_coeff,
        "log_Omega_nodes": (F @ log_Omega_coeff)[..., 0],
        "Omega_nodes": np.exp((F @ log_Omega_coeff)[..., 0]),
        "varphi_nodes": varphi_nodes,
        "A_nodes": A_nodes,
        "E0": frame0["E0"],
        "E": frame,
        "T_gradient": frame0["T_gradient"],
        "T_norm2": frame0["T_norm2"],
        "Q_rotation": S,
        "Q_drotation": dS,
        "Q_q_nodes": F @ frame_q_coeff,
        "sides": side_details,
    }


def ambient_to_free_coordinates(q: np.ndarray, N: int) -> np.ndarray:
    """Local left inverse used by the exact common-first ambient retraction."""

    basis = real_fourier_basis(N)
    F, D, Finv = basis["values"], basis["derivatives"], basis["inverse"]
    ambient = ambient_layout(N)
    free_layout_N = free_layout(N)
    q = np.asarray(q, dtype=float)
    if q.shape != (ambient.size,):
        raise SpectralCertificateError("ambient coordinate shape drift")
    free = np.zeros(free_layout_N.size, dtype=float)
    for common_name in ("gamma", "T", "log_Omega"):
        free_layout_N.put(
            free,
            f"common.{common_name}",
            ambient.get(q, f"common.{common_name}"),
        )
    q_frame_coeff = ambient.get(q, "Q_frame.q")
    free_layout_N.put(free, "Q_frame.q", q_frame_coeff)
    S, dS = _rotation_nodes(q_frame_coeff, basis)
    varphi = F @ ambient.get(q, "common.varphi")
    varphi0 = np.einsum("nji,nj->ni", S, varphi)
    free_layout_N.put(free, "common.varphi_E0", Finv @ varphi0)
    A_common = (
        F @ ambient.get(q, "common.A_Sigma").reshape(N, 12)
    ).reshape(N, 4, 3)
    A0 = np.empty_like(A_common)
    for node in range(N):
        for mu in range(4):
            matrix = (
                S[node].T @ _hat(A_common[node, mu]) @ S[node]
                + S[node].T @ dS[node, mu]
            )
            A0[node, mu] = _vee(matrix)
    free_layout_N.put(
        free,
        "common.A_E0",
        (Finv @ A0.reshape(N, 12)).reshape(N, 4, 3),
    )

    for side in SIDES:
        Y_coeff = ambient.get(q, f"{side}.Y")
        free_layout_N.put(free, f"{side}.Y", Y_coeff)
        Y_gradient = np.swapaxes((D @ Y_coeff)[..., 0], 0, 1)
        metric = _vec_to_sym(
            F @ ambient.get(q, f"{side}.g_trace"), 5, SYMMETRIC5
        )
        metric_free = np.empty((N, 5), dtype=float)
        metric_free[:, :4] = metric[:, :4, 4] + metric[:, 4, 4, None] * Y_gradient
        metric_free[:, 4] = metric[:, 4, 4]
        free_layout_N.put(free, f"{side}.metric_free", Finv @ metric_free)
        A_full = (
            F @ ambient.get(q, f"{side}.A_trace_full").reshape(N, 15)
        ).reshape(N, 5, 3)
        free_layout_N.put(free, f"{side}.A_perp", Finv @ A_full[:, 4])
        free_layout_N.put(
            free, f"{side}.B0_full", ambient.get(q, f"{side}.B_trace_full")
        )
        R, _ = _rotation_nodes(ambient.get(q, f"{side}.r"), basis)
        R0 = np.swapaxes(S, -1, -2) @ R
        r0_nodes = np.stack(
            tuple(_so3_log(R0[node]) for node in range(N)), axis=0
        )
        free_layout_N.put(free, f"{side}.r_E0", Finv @ r0_nodes)
        for name in ("boundary_jet_J1", "interior_bump_C"):
            free_layout_N.put(free, f"{side}.{name}", ambient.get(q, f"{side}.{name}"))
    return free


def retract_ambient_point(q: np.ndarray, N: int) -> np.ndarray:
    """Exact local retraction onto G=0 through common-first elimination."""

    return construct_ambient_point(ambient_to_free_coordinates(q, N), N)


def gluing_map(q: np.ndarray, N: int) -> np.ndarray:
    """Full redundant G: 10 gamma + 1 Omega + 3 phi + 12 A per side/mode."""

    basis = real_fourier_basis(N)
    F, D = basis["values"], basis["derivatives"]
    layout = ambient_layout(N)
    q = np.asarray(q)
    if q.shape != (layout.size,):
        raise SpectralCertificateError("ambient coordinate shape drift")
    gamma_common = _vec_to_sym(F @ layout.get(q, "common.gamma"), 4, SYMMETRIC4)
    omega_common = np.exp(
        (F @ layout.get(q, "common.log_Omega"))[..., 0]
    )
    varphi_common = F @ layout.get(q, "common.varphi")
    A_common = (F @ layout.get(q, "common.A_Sigma").reshape(N, 12)).reshape(N, 4, 3)
    blocks: list[np.ndarray] = []
    for node in range(N):
        for side in SIDES:
            Y_coeff = layout.get(q, f"{side}.Y")
            Y_gradient = (D @ Y_coeff)[:, node, 0]
            tangent = np.zeros((5, 4), dtype=q.dtype)
            tangent[:4, :] = np.eye(4)
            tangent[4, :] = Y_gradient
            g_nodes = _vec_to_sym(F @ layout.get(q, f"{side}.g_trace"), 5, SYMMETRIC5)
            induced = tangent.T @ g_nodes[node] @ tangent
            omega_side = np.exp(
                (F @ layout.get(q, f"{side}.log_Omega_trace"))[node, 0]
            )
            phi_side = (F @ layout.get(q, f"{side}.phi_trace"))[node]
            A_full_side = (F @ layout.get(q, f"{side}.A_trace_full").reshape(N, 15)).reshape(N, 5, 3)[node]
            A_side = A_full_side[:4] + Y_gradient[:, None] * A_full_side[4]
            r_coeff = layout.get(q, f"{side}.r")
            R, dR = _rotation_nodes(r_coeff, basis)
            transported_A = np.empty((4, 3), dtype=q.dtype)
            for mu in range(4):
                matrix = R[node] @ _hat(A_side[mu]) @ R[node].T - dR[node, mu] @ R[node].T
                transported_A[mu] = _vee(matrix)
            block = np.concatenate(
                (
                    _sym_to_vec(induced - gamma_common[node], SYMMETRIC4),
                    np.asarray((omega_side - omega_common[node],), dtype=q.dtype),
                    R[node] @ phi_side - varphi_common[node],
                    (transported_A - A_common[node]).reshape(-1),
                )
            )
            if block.shape != (26,):
                raise SpectralCertificateError("per-side gluing block is not 26")
            blocks.append(block)
    nodal_blocks = np.stack(blocks, axis=0).reshape(N, 2, 26)
    coefficient_blocks = np.einsum("mn,nsc->msc", basis["inverse"], nodal_blocks)
    result = coefficient_blocks.reshape(-1)
    if result.shape != (52 * N,):
        raise SpectralCertificateError("gluing codomain dimension drift")
    return result


def z2_involution(q: np.ndarray, N: int) -> np.ndarray:
    """Declared comparison involution; it is diagnostic and never imposed."""

    layout = ambient_layout(N)
    q = np.asarray(q)
    if q.shape != (layout.size,):
        raise SpectralCertificateError("Z2 input shape drift")
    result = np.zeros_like(q)
    for name in (
        "common.gamma",
        "common.T",
        "common.log_Omega",
        "common.varphi",
        "common.A_Sigma",
        "Q_frame.q",
    ):
        layout.put(result, name, layout.get(q, name))
    g_parity = [NORMAL_REFLECTION[i, i] * NORMAL_REFLECTION[j, j] for i, j in SYMMETRIC5]
    A_parity = [NORMAL_REFLECTION[mu, mu] for mu in range(5) for _ in range(3)]
    B_parity = []
    for i in range(5):
        for j in range(i + 1, 5):
            for k in range(j + 1, 5):
                B_parity.extend((NORMAL_REFLECTION[i, i] * NORMAL_REFLECTION[j, j] * NORMAL_REFLECTION[k, k],) * 3)
    interior_parity = np.asarray(
        (*g_parity, 1.0, 1.0, 1.0, 1.0, *A_parity, *B_parity),
        dtype=q.dtype,
    )
    if interior_parity.shape != (64,):
        raise SpectralCertificateError("interior Z2 parity contract drift")
    for destination, source in (("plus", "minus"), ("minus", "plus")):
        layout.put(result, f"{destination}.Y", -layout.get(q, f"{source}.Y"))
        metric = _vec_to_sym(layout.get(q, f"{source}.g_trace"), 5, SYMMETRIC5)
        reflected = NORMAL_REFLECTION.astype(q.dtype) @ metric @ NORMAL_REFLECTION.astype(q.dtype)
        layout.put(result, f"{destination}.g_trace", _sym_to_vec(reflected, SYMMETRIC5))
        for suffix in ("log_Omega_trace", "phi_trace", "r"):
            layout.put(result, f"{destination}.{suffix}", layout.get(q, f"{source}.{suffix}"))
        A_full = layout.get(q, f"{source}.A_trace_full")
        layout.put(
            result,
            f"{destination}.A_trace_full",
            A_full * np.diag(NORMAL_REFLECTION)[None, :, None],
        )
        B_full = layout.get(q, f"{source}.B_trace_full").reshape(N, 30)
        layout.put(
            result,
            f"{destination}.B_trace_full",
            (B_full * np.asarray(B_parity, dtype=q.dtype)[None, :]).reshape(N, 10, 3),
        )
        boundary_jet = layout.get(q, f"{source}.boundary_jet_J1")
        layout.put(
            result,
            f"{destination}.boundary_jet_J1",
            boundary_jet * interior_parity[None, :],
        )
        interior_modes = layout.get(q, f"{source}.interior_bump_C")
        layout.put(
            result,
            f"{destination}.interior_bump_C",
            interior_modes * interior_parity[None, None, :],
        )
    return result


def z2_gluing_permutation(residual: np.ndarray, N: int) -> np.ndarray:
    residual = np.asarray(residual)
    if residual.shape != (52 * N,):
        raise SpectralCertificateError("Z2 residual shape drift")
    return residual.reshape(N, 2, 26)[:, ::-1, :].reshape(-1)


def gauge_parameter_layout(N: int) -> VectorLayout:
    layout = VectorLayout()
    layout.add("target_Q", (N, 3))
    layout.add("source_plus", (N, 3))
    layout.add("source_minus", (N, 3))
    return layout


def finite_frame_gauge_action(
    q: np.ndarray, N: int, parameter: np.ndarray, epsilon: float
) -> np.ndarray:
    """Finite discrete boundary-trivialization SO(3) orbit on a glued point.

    U_source is rho-independent on the collar.  The inhomogeneous tangential
    term is carried by X0 while J/C adjoint channels rotate homogeneously.
    This is not the later bulk compact-support Ward test.
    """

    basis = real_fourier_basis(N)
    F, Finv = basis["values"], basis["inverse"]
    layout = ambient_layout(N)
    parameters = gauge_parameter_layout(N)
    q = np.asarray(q, dtype=float)
    parameter = np.asarray(parameter, dtype=float)
    if parameter.shape != (parameters.size,):
        raise SpectralCertificateError("gauge parameter shape drift")
    result = q.copy()

    target_coeff = epsilon * parameters.get(parameter, "target_Q")
    U_Q, dU_Q = _rotation_nodes(target_coeff, basis)
    varphi = F @ layout.get(q, "common.varphi")
    A_common = (F @ layout.get(q, "common.A_Sigma").reshape(N, 12)).reshape(N, 4, 3)
    transformed_varphi = np.einsum("nij,nj->ni", U_Q, varphi)
    transformed_A = np.empty_like(A_common)
    for node in range(N):
        for mu in range(4):
            matrix = U_Q[node] @ _hat(A_common[node, mu]) @ U_Q[node].T - dU_Q[node, mu] @ U_Q[node].T
            transformed_A[node, mu] = _vee(matrix)
    layout.put(result, "common.varphi", Finv @ transformed_varphi)
    layout.put(
        result,
        "common.A_Sigma",
        (Finv @ transformed_A.reshape(N, 12)).reshape(N, 4, 3),
    )
    old_Q, _ = _rotation_nodes(layout.get(q, "Q_frame.q"), basis)
    new_Q_log = np.stack(
        tuple(_so3_log(U_Q[node] @ old_Q[node]) for node in range(N)), axis=0
    )
    layout.put(result, "Q_frame.q", Finv @ new_Q_log)

    transformed_rotations: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for side in SIDES:
        source_name = "source_plus" if side == "plus" else "source_minus"
        source_coeff = epsilon * parameters.get(parameter, source_name)
        U_source, _ = _rotation_nodes(source_coeff, basis)
        old_R, _ = _rotation_nodes(layout.get(q, f"{side}.r"), basis)
        new_R_nodes = U_Q @ old_R @ np.swapaxes(U_source, -1, -2)
        new_r_nodes = np.stack(tuple(_so3_log(new_R_nodes[node]) for node in range(N)), axis=0)
        new_r_coeff = Finv @ new_r_nodes
        layout.put(result, f"{side}.r", new_r_coeff)

        A_full_nodes = (F @ layout.get(q, f"{side}.A_trace_full").reshape(N, 15)).reshape(N, 5, 3)
        A_full_nodes[:, 4] = np.einsum(
            "nij,nj->ni", U_source, A_full_nodes[:, 4]
        )
        layout.put(
            result,
            f"{side}.A_trace_full",
            (Finv @ A_full_nodes.reshape(N, 15)).reshape(N, 5, 3),
        )

        B_nodes = (F @ layout.get(q, f"{side}.B_trace_full").reshape(N, 30)).reshape(N, 10, 3)
        B_nodes = np.einsum("nij,nkj->nki", U_source, B_nodes)
        layout.put(
            result,
            f"{side}.B_trace_full",
            (Finv @ B_nodes.reshape(N, 30)).reshape(N, 10, 3),
        )

        for interior_name, radial_width in (
            ("boundary_jet_J1", 1),
            ("interior_bump_C", radial_truncation(N)),
        ):
            interior = (
                F
                @ layout.get(q, f"{side}.{interior_name}").reshape(
                    N, radial_width * 64
                )
            ).reshape(N, radial_width, 64)
            interior[:, :, 16:19] = np.einsum(
                "nij,nwj->nwi", U_source, interior[:, :, 16:19]
            )
            interior[:, :, 19:34] = np.einsum(
                "nij,nwkj->nwki",
                U_source,
                interior[:, :, 19:34].reshape(N, radial_width, 5, 3),
            ).reshape(N, radial_width, 15)
            interior[:, :, 34:64] = np.einsum(
                "nij,nwkj->nwki",
                U_source,
                interior[:, :, 34:64].reshape(N, radial_width, 10, 3),
            ).reshape(N, radial_width, 30)
            transformed_coefficients = (
                Finv @ interior.reshape(N, radial_width * 64)
            ).reshape(N, radial_width, 64)
            if interior_name == "boundary_jet_J1":
                transformed_coefficients = transformed_coefficients[:, 0]
            layout.put(result, f"{side}.{interior_name}", transformed_coefficients)
        transformed_rotations[side] = _rotation_nodes(new_r_coeff, basis)

    # Re-solve only the trace representatives after the finite frame action.
    # This keeps the pseudospectral orbit exactly inside G=0 despite aliasing.
    for side in SIDES:
        R, dR = transformed_rotations[side]
        phi_source = np.einsum("nji,nj->ni", R, transformed_varphi)
        A_source = np.empty_like(transformed_A)
        for node in range(N):
            for mu in range(4):
                matrix = R[node].T @ _hat(transformed_A[node, mu]) @ R[node] + R[node].T @ dR[node, mu]
                A_source[node, mu] = _vee(matrix)
        layout.put(result, f"{side}.phi_trace", Finv @ phi_source)
        A_full_nodes = (
            F @ layout.get(result, f"{side}.A_trace_full").reshape(N, 15)
        ).reshape(N, 5, 3)
        Y_gradient = np.swapaxes(
            (basis["derivatives"] @ layout.get(result, f"{side}.Y"))[..., 0],
            0,
            1,
        )
        A_full_nodes[:, :4] = A_source - Y_gradient[:, :, None] * A_full_nodes[:, 4, None, :]
        layout.put(
            result,
            f"{side}.A_trace_full",
            (Finv @ A_full_nodes.reshape(N, 15)).reshape(N, 5, 3),
        )
    return result


def runtime_SO3_gauge_tangents(q: np.ndarray, N: int) -> np.ndarray:
    parameters = gauge_parameter_layout(N)
    step = TOLERANCES["retraction_step"]
    result = np.empty((ambient_layout(N).size, parameters.size), dtype=float)
    for column in range(parameters.size):
        direction = np.zeros(parameters.size)
        direction[column] = 1.0
        result[:, column] = (
            finite_frame_gauge_action(q, N, direction, step)
            - finite_frame_gauge_action(q, N, direction, -step)
        ) / (2.0 * step)
    return result


def runtime_DG(q: np.ndarray, N: int) -> np.ndarray:
    """Differentiate public G on redundant q by complex step at runtime."""

    q = np.asarray(q, dtype=float)
    step = TOLERANCES["complex_step"]
    jacobian = np.empty((52 * N, q.size), dtype=float)
    for column in range(q.size):
        shifted = q.astype(complex)
        shifted[column] += 1j * step
        jacobian[:, column] = np.imag(gluing_map(shifted, N)) / step
    return jacobian


def runtime_retraction_probes(free: np.ndarray, N: int) -> list[tuple[str, np.ndarray]]:
    """Selected central-difference columns of D i_N; no dense Jacobian."""

    layout = free_layout(N)
    step = TOLERANCES["retraction_step"]
    specifications = (
        ("compact_bulk_SO3_horizontal_candidate", "interior_bump_C", 1.0, -0.41),
        ("free_B_SO3_horizontal_candidate", "B0_full", 0.73, -1.0),
        ("embedding_motion_SO3_horizontal_candidate", "Y", 1.0, 0.37),
    )
    result: list[tuple[str, np.ndarray]] = []
    for label, block_name, plus_weight, minus_weight in specifications:
        parameter = np.zeros(layout.size)
        plus_indices = layout.indices(f"plus.{block_name}")
        minus_indices = layout.indices(f"minus.{block_name}")
        parameter[plus_indices[0]] = plus_weight
        parameter[minus_indices[min(1, minus_indices.size - 1)]] = minus_weight
        plus = np.asarray(free, dtype=float) + step * parameter
        minus = np.asarray(free, dtype=float) - step * parameter
        tangent = (
            construct_ambient_point(plus, N) - construct_ambient_point(minus, N)
        ) / (2.0 * step)
        result.append((label, tangent))
    joint_parameter = np.zeros(layout.size)
    for block_number, name in enumerate(layout.rows):
        indices = layout.indices(name)
        chosen_offset = 5 if name == "common.gamma" else 1
        chosen = indices[min(chosen_offset, indices.size - 1)]
        joint_parameter[chosen] = (0.19 + 0.013 * block_number) * (
            -1.0 if block_number % 2 else 1.0
        )
    plus = np.asarray(free, dtype=float) + step * joint_parameter
    minus = np.asarray(free, dtype=float) - step * joint_parameter
    result.append(
        (
            "joint_all_primitive_classes_control_candidate",
            (construct_ambient_point(plus, N) - construct_ambient_point(minus, N))
            / (2.0 * step),
        )
    )
    return result


def _canonicalize_columns(matrix: np.ndarray) -> np.ndarray:
    result = np.asarray(matrix, dtype=float).copy()
    for column in range(result.shape[1]):
        pivot = int(np.argmax(np.abs(result[:, column])))
        if result[pivot, column] < 0.0:
            result[:, column] *= -1.0
    return result


def _orthonormality_probe_residual(matrix: np.ndarray) -> float:
    """Linear-cost audit of a complete-Q basis produced by LAPACK QR."""

    width = matrix.shape[1]
    sample_count = min(32, width)
    indices = np.unique(np.linspace(0, width - 1, sample_count, dtype=int))
    sampled = matrix[:, indices]
    sampled_residual = float(
        np.max(np.abs(sampled.T @ sampled - np.eye(indices.size)))
    )
    probes = np.sin(
        (np.arange(width, dtype=float)[:, None] + 1.0)
        * (np.arange(8, dtype=float)[None, :] + 1.618033988749895)
    ) / math.sqrt(max(width, 1))
    image = matrix @ probes
    isometry_residual = float(
        np.max(np.abs(image.T @ image - probes.T @ probes))
    )
    column_norm_residual = float(
        np.max(np.abs(np.linalg.norm(matrix, axis=0) - 1.0))
    )
    return max(sampled_residual, isometry_residual, column_norm_residual)


def _rank_tolerance(singulars: np.ndarray, shape: tuple[int, int]) -> float:
    return float(
        TOLERANCES["rank_relative_multiplier"]
        * max(shape)
        * np.finfo(float).eps
        * singulars[0]
    )


def _selected_SO3_horizontal_tangents(
    DG: np.ndarray,
    retraction_probes: list[tuple[str, np.ndarray]],
    horizontal_basis: np.ndarray,
    N: int,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    ambient = ambient_layout(N)
    selected: list[np.ndarray] = []
    receipts: list[dict[str, Any]] = []
    plus_block = slice(ambient.rows["plus.Y"][0].start, ambient.rows["plus.interior_bump_C"][0].stop)
    minus_block = slice(ambient.rows["minus.Y"][0].start, ambient.rows["minus.interior_bump_C"][0].stop)
    for label, probe in retraction_probes:
        vector = horizontal_basis @ (horizontal_basis.T @ probe)
        for previous in selected:
            vector -= previous * float(previous @ vector)
        norm = float(np.linalg.norm(vector))
        if norm < 1.0e-10:
            raise SpectralCertificateError(f"SO3-horizontal probe collapsed: {label}")
        vector /= norm
        selected.append(vector)
        plus = vector[plus_block]
        minus = vector[minus_block]
        z2_image = z2_involution(vector, N)
        z2_even_defect = vector - z2_image
        z2_odd_defect = vector + z2_image
        non_Z2_distance = min(
            float(np.linalg.norm(z2_even_defect)),
            float(np.linalg.norm(z2_odd_defect)),
        )
        activity = {
            name: float(np.linalg.norm(ambient.get(vector, name)))
            for name in ambient.rows
        }
        receipts.append(
            {
                "name": label,
                "ambient_primitive_tangent": vector.tolist(),
                "ambient_primitive_tangent_sha256": _array_sha256(vector),
                "DG_residual_L2": float(np.linalg.norm(DG @ vector)),
                "plus_activity_L2": float(np.linalg.norm(plus)),
                "minus_activity_L2": float(np.linalg.norm(minus)),
                "Z2_even_distance_L2": float(np.linalg.norm(vector - z2_image)),
                "Z2_odd_distance_L2": float(np.linalg.norm(vector + z2_image)),
                "Z2_even_ambient_defect_L2": float(np.linalg.norm(z2_even_defect)),
                "Z2_odd_ambient_defect_L2": float(np.linalg.norm(z2_odd_defect)),
                "non_Z2_no_parity_ambient_distance_L2": non_Z2_distance,
                "gauge_quotient_claimed": False,
                "named_block_activity_L2": activity,
            }
        )
    gram = np.stack(selected, axis=-1).T @ np.stack(selected, axis=-1)
    if np.max(np.abs(gram - np.eye(len(selected)))) > TOLERANCES["orthonormality_Linf"]:
        raise SpectralCertificateError("selected SO3-horizontal tangents lost independence")
    return receipts, np.stack(selected, axis=-1)


def _sampled_endpoint_kinematic_audit(q: np.ndarray, N: int) -> dict[str, Any]:
    """Recompute finite node x radial-sample invariants for a stencil endpoint."""

    free = ambient_to_free_coordinates(q, N)
    rebuilt, detail = construct_ambient_point(free, N, details=True)
    gamma_eigenvalues = np.linalg.eigvalsh(detail["gamma_nodes"])
    ambient_eigenvalues = {
        side: np.linalg.eigvalsh(detail["sides"][side]["g_nodes"])
        for side in SIDES
    }
    bulk = bulk_primitives(rebuilt, N, RADIAL_SAMPLE)
    bulk_eigenvalues = {
        side: np.linalg.eigvalsh(bulk[side]["values"]["g_MN"])
        for side in SIDES
    }
    bulk_Omega_min = min(
        float(np.min(bulk[side]["values"]["Omega"])) for side in SIDES
    )
    rotation_chart_norm = max(
        float(np.max(np.linalg.norm(detail["sides"][side]["r_nodes"], axis=-1)))
        for side in SIDES
    )
    rotation_group_residual = max(
        float(
            np.max(
                np.abs(
                    np.swapaxes(detail["sides"][side]["R_nodes"], -1, -2)
                    @ detail["sides"][side]["R_nodes"]
                    - np.eye(3)
                )
            )
        )
        for side in SIDES
    )
    orientation_signs: dict[str, list[int]] = {}
    normal_residual = 0.0
    for side, inward_sign in (("plus", -1.0), ("minus", 1.0)):
        signs: list[int] = []
        for node in range(N):
            y_gradient = detail["sides"][side]["Y_gradient"][node]
            tangent = np.zeros((5, 4))
            tangent[:4] = np.eye(4)
            tangent[4] = y_gradient
            metric = detail["sides"][side]["g_nodes"][node]
            raw_covector = np.concatenate((-y_gradient, (1.0,)))
            inverse_metric = np.linalg.inv(metric)
            raw_norm2 = float(raw_covector @ inverse_metric @ raw_covector)
            if raw_norm2 <= 0.0:
                normal_residual = math.inf
                signs.append(0)
                continue
            outward_covector = -inward_sign * raw_covector / math.sqrt(raw_norm2)
            outward_vector = inverse_metric @ outward_covector
            normal_residual = max(
                normal_residual,
                abs(float(outward_vector @ metric @ outward_vector) - 1.0),
                float(np.max(np.abs(tangent.T @ metric @ outward_vector))),
            )
            signs.append(
                int(np.sign(np.linalg.det(np.column_stack((tangent, outward_vector)))))
            )
        orientation_signs[side] = signs
    pass_flags = {
        "gamma_Lorentzian": bool(
            np.all(np.sum(gamma_eigenvalues < 0.0, axis=-1) == 1)
            and np.min(np.abs(gamma_eigenvalues))
            > TOLERANCES["signature_eigenvalue_margin"]
        ),
        "ambient_metrics_Lorentzian": all(
            np.all(np.sum(values < 0.0, axis=-1) == 1)
            and np.min(np.abs(values)) > TOLERANCES["signature_eigenvalue_margin"]
            for values in ambient_eigenvalues.values()
        ),
        "sampled_bulk_metrics_Lorentzian": all(
            np.all(np.sum(values < 0.0, axis=-1) == 1)
            and np.min(np.abs(values)) > TOLERANCES["signature_eigenvalue_margin"]
            for values in bulk_eigenvalues.values()
        ),
        "Omega_positive_with_sampled_margin": (
            float(np.min(detail["Omega_nodes"])) > TOLERANCES["Omega_min"]
            and bulk_Omega_min > TOLERANCES["Omega_min"]
        ),
        "T_gradient_timelike": float(np.max(detail["T_norm2"]))
        < -TOLERANCES["timelike_margin"],
        "R_local_SO3_chart": (
            rotation_group_residual < TOLERANCES["orthonormality_Linf"]
            and math.pi - rotation_chart_norm
            > TOLERANCES["rotation_cut_locus_margin"]
        ),
        "normal_and_outward_orientation": (
            normal_residual < TOLERANCES["orthonormality_Linf"]
            and set(orientation_signs["plus"]) == {1}
            and set(orientation_signs["minus"]) == {-1}
        ),
    }
    return {
        "sample_grid": {"tangential_collocation_nodes": N, "rho": RADIAL_SAMPLE.tolist()},
        "retraction_consistency_L2": float(np.linalg.norm(rebuilt - q)),
        "gamma_min_abs_eigenvalue": float(np.min(np.abs(gamma_eigenvalues))),
        "ambient_metric_min_abs_eigenvalue": min(
            float(np.min(np.abs(values))) for values in ambient_eigenvalues.values()
        ),
        "sampled_bulk_metric_min_abs_eigenvalue": min(
            float(np.min(np.abs(values))) for values in bulk_eigenvalues.values()
        ),
        "Omega_min": min(float(np.min(detail["Omega_nodes"])), bulk_Omega_min),
        "T_norm2_max": float(np.max(detail["T_norm2"])),
        "R_cut_locus_margin": math.pi - rotation_chart_norm,
        "normal_residual_Linf": normal_residual,
        "outward_orientation_signs": orientation_signs,
        "checks": pass_flags,
        "all_sampled_checks_pass": all(pass_flags.values()),
    }


def analyze_configuration(seed: int, N: int) -> dict[str, Any]:
    free = build_free_coordinates(seed, N)
    q, detail = construct_ambient_point(free, N, details=True)
    G = gluing_map(q, N)
    DG = runtime_DG(q, N)
    singulars = np.linalg.svd(DG, compute_uv=False, full_matrices=False)
    rank_tolerance = _rank_tolerance(singulars, DG.shape)
    rank = int(np.sum(singulars > rank_tolerance))
    qr_full, _ = np.linalg.qr(DG.T, mode="complete")
    kernel = _canonicalize_columns(qr_full[:, rank:])
    kernel_residuals = np.linalg.norm(DG @ kernel, axis=0)
    kernel_gram_residual = _orthonormality_probe_residual(kernel)

    retraction_probes = runtime_retraction_probes(free, N)
    retraction_probe_residuals = {
        name: float(np.linalg.norm(DG @ vector))
        for name, vector in retraction_probes
    }

    gauge_parameters = gauge_parameter_layout(N)
    gauge_raw = runtime_SO3_gauge_tangents(q, N)
    gauge_singulars = np.linalg.svd(gauge_raw, compute_uv=False)
    gauge_rank_tolerance = float(TOLERANCES["retraction_rank_relative"] * gauge_singulars[0])
    gauge_rank = int(np.sum(gauge_singulars > gauge_rank_tolerance))
    gauge_basis, _ = np.linalg.qr(gauge_raw, mode="reduced")
    gauge_basis = _canonicalize_columns(gauge_basis)
    gauge_in_kernel_coordinates = kernel.T @ gauge_basis
    expected_horizontal_dim = kernel.shape[1] - gauge_basis.shape[1]
    augmented_constraints = np.vstack((DG, gauge_basis.T))
    horizontal_qr, _ = np.linalg.qr(augmented_constraints.T, mode="complete")
    horizontal_basis = _canonicalize_columns(
        horizontal_qr[:, augmented_constraints.shape[0] :]
    )
    horizontal_orthonormality_residual = _orthonormality_probe_residual(
        horizontal_basis
    )
    horizontal_s = np.linalg.svd(gauge_in_kernel_coordinates, compute_uv=False)
    z2_gauge_images = np.stack(
        tuple(z2_involution(gauge_basis[:, column], N) for column in range(gauge_basis.shape[1])),
        axis=-1,
    )
    z2_q = z2_involution(q, N)
    z2_gauge_raw = runtime_SO3_gauge_tangents(z2_q, N)
    z2_gauge_basis, _ = np.linalg.qr(z2_gauge_raw, mode="reduced")
    z2_gauge_basis = _canonicalize_columns(z2_gauge_basis)
    z2_gauge_subspace_residual = float(
        np.max(
            np.linalg.norm(
                z2_gauge_images
                - z2_gauge_basis @ (z2_gauge_basis.T @ z2_gauge_images),
                axis=0,
            )
        )
    )
    selected, selected_vectors = _selected_SO3_horizontal_tangents(
        DG, retraction_probes, horizontal_basis, N
    )

    # H_N is a pointwise Euclidean-coefficient generator.  The following are
    # finite retracted stencils, not a neighborhood flow or reachability proof.
    joint_column = next(
        index
        for index, row in enumerate(selected)
        if row["name"] == "joint_all_primitive_classes_control_candidate"
    )
    chart_step = TOLERANCES["reachable_chart_step"]
    horizontal_endpoint_arrays: dict[str, dict[int, np.ndarray]] = {}
    horizontal_stencils: dict[str, Any] = {}
    for column, row in enumerate(selected):
        tangent = selected_vectors[:, column]
        endpoints = {
            multiplier: retract_ambient_point(
                q + multiplier * chart_step * tangent, N
            )
            for multiplier in (-2, -1, 1, 2)
        }
        five_point = (
            -endpoints[2]
            + 8.0 * endpoints[1]
            - 8.0 * endpoints[-1]
            + endpoints[-2]
        ) / (12.0 * chart_step)
        endpoint_audits = {
            str(multiplier): _sampled_endpoint_kinematic_audit(endpoint, N)
            for multiplier, endpoint in endpoints.items()
        }
        horizontal_endpoint_arrays[row["name"]] = endpoints
        horizontal_stencils[row["name"]] = {
            "ambient_primitive_tangent_reference": f"SO3_gauge_and_horizontal_split.selected_SO3_horizontal_tangents[{column}].ambient_primitive_tangent",
            "ambient_primitive_tangent_sha256": _array_sha256(tangent),
            "stencil_endpoints_ambient_q_f64le": {
                str(multiplier): _encode_f64le(endpoint)
                for multiplier, endpoint in endpoints.items()
            },
            "stencil_endpoint_G_Linf": {
                str(multiplier): float(np.max(np.abs(gluing_map(endpoint, N))))
                for multiplier, endpoint in endpoints.items()
            },
            "stencil_endpoint_sampled_kinematic_audits": endpoint_audits,
            "five_point_tangent_tracking_L2": float(
                np.linalg.norm(five_point - tangent)
            ),
        }
    control_tangent = selected_vectors[:, joint_column]
    reachable_endpoints = horizontal_endpoint_arrays[
        "joint_all_primitive_classes_control_candidate"
    ]

    gauge_representative_stencils: dict[str, Any] = {}
    for parameter_name in ("target_Q", "source_plus", "source_minus"):
        sector_indices = gauge_parameters.indices(parameter_name)
        for mode in range(N):
            for component in range(3):
                direction = np.zeros(gauge_parameters.size)
                parameter_column = int(sector_indices[3 * mode + component])
                direction[parameter_column] = 1.0
                endpoints = {
                    multiplier: finite_frame_gauge_action(
                        q, N, direction, multiplier * chart_step
                    )
                    for multiplier in (-2, -1, 1, 2)
                }
                five_point = (
                    -endpoints[2]
                    + 8.0 * endpoints[1]
                    - 8.0 * endpoints[-1]
                    + endpoints[-2]
                ) / (12.0 * chart_step)
                tangent = gauge_raw[:, parameter_column]
                coefficient = np.zeros((N, 3))
                coefficient[mode, component] = 1.0
                derivative_activity = float(
                    np.linalg.norm(real_fourier_basis(N)["derivatives"] @ coefficient)
                )
                label = f"{parameter_name}.mode_{mode}.component_{component}"
                gauge_representative_stencils[label] = {
                    "sector": parameter_name,
                    "tangential_mode_index": mode,
                    "basis_label": real_fourier_basis(N)["labels"][mode],
                    "wavevector": real_fourier_basis(N)["mode_wavevectors"][mode],
                    "so3_component": component,
                    "gauge_parameter_four_gradient_L2": derivative_activity,
                    "is_local_nonconstant_parameter": derivative_activity > 0.0,
                    "ambient_primitive_tangent_f64le": _encode_f64le(tangent),
                    "stencil_endpoints_ambient_q_f64le": {
                        str(multiplier): _encode_f64le(endpoint)
                        for multiplier, endpoint in endpoints.items()
                    },
                    "stencil_endpoint_G_Linf": {
                        str(multiplier): float(np.max(np.abs(gluing_map(endpoint, N))))
                        for multiplier, endpoint in endpoints.items()
                    },
                    "stencil_endpoint_sampled_kinematic_audits": {
                        str(multiplier): _sampled_endpoint_kinematic_audit(endpoint, N)
                        for multiplier, endpoint in endpoints.items()
                    },
                    "five_point_tangent_tracking_L2": float(
                        np.linalg.norm(five_point - tangent)
                    ),
                }
    reachable_displacement = reachable_endpoints[1] - reachable_endpoints[-1]
    reachable_plus_free = ambient_to_free_coordinates(reachable_endpoints[1], N)
    _, reachable_plus_detail = construct_ambient_point(
        reachable_plus_free, N, details=True
    )
    ambient_N = ambient_layout(N)
    common_log_Omega_motion = float(
        np.linalg.norm(
            np.exp(
                real_fourier_basis(N)["values"]
                @ ambient_N.get(reachable_endpoints[1], "common.log_Omega")
            )
            - detail["Omega_nodes"][:, None]
        )
    )
    reachable_motion_by_class = {
        "embedding_Y": float(
            math.sqrt(
                sum(
                    np.linalg.norm(ambient_N.get(reachable_displacement, f"{side}.Y")) ** 2
                    for side in SIDES
                )
            )
        ),
        "rotation_R": max(
            float(
                np.linalg.norm(
                    reachable_plus_detail["sides"][side]["R_nodes"]
                    - detail["sides"][side]["R_nodes"]
                )
            )
            for side in SIDES
        ),
        "horizontal_frame_E0": float(
            np.linalg.norm(reachable_plus_detail["E0"] - detail["E0"])
        ),
        "metric_g": float(
            math.sqrt(
                sum(
                    np.linalg.norm(ambient_N.get(reachable_displacement, f"{side}.g_trace")) ** 2
                    for side in SIDES
                )
            )
        ),
        "physical_Omega": common_log_Omega_motion,
        "phi": float(np.linalg.norm(ambient_N.get(reachable_displacement, "common.varphi"))),
        "connection_A": float(np.linalg.norm(ambient_N.get(reachable_displacement, "common.A_Sigma"))),
        "three_form_B": float(
            math.sqrt(
                sum(
                    np.linalg.norm(ambient_N.get(reachable_displacement, f"{side}.B_trace_full")) ** 2
                    for side in SIDES
                )
            )
        ),
        "boundary_jet_J1": float(
            math.sqrt(
                sum(
                    np.linalg.norm(ambient_N.get(reachable_displacement, f"{side}.boundary_jet_J1")) ** 2
                    for side in SIDES
                )
            )
        ),
        "compact_radial_modes_C": float(
            math.sqrt(
                sum(
                    np.linalg.norm(ambient_N.get(reachable_displacement, f"{side}.interior_bump_C")) ** 2
                    for side in SIDES
                )
            )
        ),
    }
    reachable_z2 = z2_involution(reachable_displacement, N)
    reachable_z2_even = reachable_displacement - reachable_z2
    reachable_z2_odd = reachable_displacement + reachable_z2
    reachable_non_Z2 = min(
        float(np.linalg.norm(reachable_z2_even)),
        float(np.linalg.norm(reachable_z2_odd)),
    )

    source_gauge_B_activity: dict[str, list[float]] = {}
    source_gauge_adjoint_interior_activity: dict[str, list[float]] = {}
    for side in SIDES:
        source_name = "source_plus" if side == "plus" else "source_minus"
        source_columns = gauge_parameters.indices(source_name)
        source_pushforward = gauge_raw[:, source_columns]
        B_rows = ambient_layout(N).indices(f"{side}.B_trace_full")
        source_gauge_B_activity[side] = np.linalg.norm(
            source_pushforward[B_rows, :], axis=0
        ).tolist()
        adjoint_rows_parts: list[int] = []
        for block_name, radial_width in (
            ("boundary_jet_J1", 1),
            ("interior_bump_C", radial_truncation(N)),
        ):
            interior_block = ambient_layout(N).rows[f"{side}.{block_name}"][0]
            adjoint_rows_parts.extend(
                interior_block.start
                + mode * radial_width * 64
                + radial * 64
                + component
                for mode in range(N)
                for radial in range(radial_width)
                for component in range(16, 64)
            )
        adjoint_rows = np.asarray(adjoint_rows_parts, dtype=int)
        source_gauge_adjoint_interior_activity[side] = np.linalg.norm(
            source_pushforward[adjoint_rows, :], axis=0
        ).tolist()

    gamma = detail["gamma_nodes"]
    gamma_eigenvalues = np.linalg.eigvalsh(gamma)
    ambient_eigenvalues = {
        side: np.linalg.eigvalsh(detail["sides"][side]["g_nodes"]) for side in SIDES
    }
    frame_gram = np.einsum("nma,nmp,npb->nab", detail["E0"], gamma, detail["E0"])
    frame_gram_vertical = np.einsum("nma,nmp,npb->nab", detail["E"], gamma, detail["E"])
    spatiality = np.einsum("nm,nma->na", detail["T_gradient"], detail["E0"])
    rotation_norm_max = max(
        float(np.max(np.linalg.norm(detail["sides"][side]["r_nodes"], axis=-1)))
        for side in SIDES
    )
    R_orthogonality = max(
        float(np.max(np.abs(np.swapaxes(detail["sides"][side]["R_nodes"], -1, -2) @ detail["sides"][side]["R_nodes"] - np.eye(3))))
        for side in SIDES
    )
    R_determinant = max(
        float(np.max(np.abs(np.linalg.det(detail["sides"][side]["R_nodes"]) - 1.0)))
        for side in SIDES
    )
    R_plus_minus = float(np.max(np.abs(detail["sides"]["plus"]["R_nodes"] - detail["sides"]["minus"]["R_nodes"])))
    Y_plus_minus = float(np.linalg.norm(detail["sides"]["plus"]["Y_nodes"] - detail["sides"]["minus"]["Y_nodes"]))
    interior_plus_minus = float(
        math.sqrt(
            np.linalg.norm(detail["sides"]["plus"]["boundary_jet_J1_nodes"] - detail["sides"]["minus"]["boundary_jet_J1_nodes"]) ** 2
            + np.linalg.norm(detail["sides"]["plus"]["C_nodes"] - detail["sides"]["minus"]["C_nodes"]) ** 2
        )
    )
    radial = _radial_profiles(N)
    radial_profile_data = _radial_profile_data(RADIAL_SAMPLE, radial_truncation(N))
    bulk = bulk_primitives(q, N, RADIAL_SAMPLE)
    bulk_metric_eigenvalues = {
        side: np.linalg.eigvalsh(bulk[side]["values"]["g_MN"]) for side in SIDES
    }
    bulk_Omega_min = min(
        float(np.min(bulk[side]["values"]["Omega"])) for side in SIDES
    )
    boundary_normals: dict[str, Any] = {}
    collar_domains = {
        "plus": {
            "interior_domain": "rho_plus=Y_plus(x)-y4>=0",
            "d_rho_sign_against_d(y4-Y)": -1.0,
        },
        "minus": {
            "interior_domain": "rho_minus=y4-Y_minus(x)>=0",
            "d_rho_sign_against_d(y4-Y)": 1.0,
        },
    }
    for side in SIDES:
        inward_sign = collar_domains[side]["d_rho_sign_against_d(y4-Y)"]
        norms: list[float] = []
        orthogonality: list[float] = []
        determinant_signs: list[int] = []
        for node in range(N):
            y_gradient = detail["sides"][side]["Y_gradient"][node]
            tangent = np.zeros((5, 4))
            tangent[:4] = np.eye(4)
            tangent[4] = y_gradient
            metric = detail["sides"][side]["g_nodes"][node]
            raw_covector = np.concatenate((-y_gradient, (1.0,)))
            inverse_metric = np.linalg.inv(metric)
            raw_norm2 = float(raw_covector @ inverse_metric @ raw_covector)
            inward_covector = inward_sign * raw_covector
            normal_covector = -inward_covector / math.sqrt(raw_norm2)
            normal_vector = inverse_metric @ normal_covector
            norms.append(float(normal_vector @ metric @ normal_vector))
            orthogonality.append(float(np.max(np.abs(tangent.T @ metric @ normal_vector))))
            determinant_signs.append(int(np.sign(np.linalg.det(np.column_stack((tangent, normal_vector))))))
        boundary_normals[side] = {
            **collar_domains[side],
            "unit_norm": norms,
            "tangent_orthogonality_Linf": orthogonality,
            "outward_orientation_determinant_sign": determinant_signs,
        }
    off_shell_probe = q + _coefficients(seed + 991 * N, "Z2:off_shell", q.shape, 0.007)
    z2_twice_residual = float(np.max(np.abs(z2_involution(z2_involution(off_shell_probe, N), N) - off_shell_probe)))
    z2_equivariance_residual = float(
        np.max(
            np.abs(
                gluing_map(z2_involution(off_shell_probe, N), N)
                - z2_gluing_permutation(gluing_map(off_shell_probe, N), N)
            )
        )
    )
    B_columns = np.concatenate(
        tuple(ambient_layout(N).indices(f"{side}.B_trace_full") for side in SIDES)
    )
    B_DG_column_norms = np.linalg.norm(DG[:, B_columns], axis=0)

    expected_rank = 52 * N
    expected_kernel = ambient_layout(N).size - expected_rank
    expected_retraction = free_layout(N).size
    if expected_kernel != expected_retraction:
        raise SpectralCertificateError("dimension theorem drift")
    retracted_base_residual = float(
        np.linalg.norm(retract_ambient_point(q, N) - q)
    )
    all_stencil_rows = tuple(horizontal_stencils.values()) + tuple(
        gauge_representative_stencils.values()
    )
    stencil_tracking_residual_max = max(
        row["five_point_tangent_tracking_L2"] for row in all_stencil_rows
    )
    stencil_G_Linf_max = max(
        max(row["stencil_endpoint_G_Linf"].values()) for row in all_stencil_rows
    )
    stencil_sampled_kinematics_pass = all(
        audit["all_sampled_checks_pass"]
        for row in all_stencil_rows
        for audit in row["stencil_endpoint_sampled_kinematic_audits"].values()
    )
    checks = {
        "G_built_on_redundant_ambient_q_not_retracted_coordinates": DG.shape[1] == ambient_layout(N).size,
        "G_has_26_constraints_per_side_and_52_per_retained_coefficient": DG.shape[0] == 52 * N,
        "G_zero_after_common_first_retraction": float(np.max(np.abs(G))) < TOLERANCES["gluing_Linf"],
        "DG_has_expected_full_row_rank": rank == expected_rank,
        "orthonormal_kernel_has_expected_dimension": kernel.shape == (ambient_layout(N).size, expected_kernel),
        "kernel_residuals_pass": float(np.max(kernel_residuals)) < TOLERANCES["kernel_residual_L2"],
        "kernel_orthonormality_pass": kernel_gram_residual < TOLERANCES["orthonormality_Linf"],
        "common_first_elimination_has_expected_local_dimension": expected_retraction == expected_kernel,
        "selected_retraction_pushforwards_lie_in_kernel": max(retraction_probe_residuals.values()) < TOLERANCES["retraction_pushforward_residual_L2"],
        "target_and_source_boundary_trivialization_SO3_orbit_lies_in_kernel": float(np.max(np.linalg.norm(DG @ gauge_basis, axis=0))) < TOLERANCES["kernel_residual_L2"],
        "all_target_and_source_frame_gauge_columns_have_rank_9N": gauge_rank == 9 * N,
        "source_frame_gauge_variations_compensate_B": all(
            min(values) > TOLERANCES["SO3_horizontal_tangent_activity_L2"]
            for values in source_gauge_B_activity.values()
        ),
        "source_frame_gauge_variations_rotate_all_typed_adjoint_interiors": all(
            min(values) > TOLERANCES["SO3_horizontal_tangent_activity_L2"]
            for values in source_gauge_adjoint_interior_activity.values()
        ),
        "SO3_horizontal_complement_dimension_pass": horizontal_basis.shape[1] == expected_horizontal_dim,
        "SO3_horizontal_complement_is_DG_kernel": float(np.max(np.linalg.norm(DG @ horizontal_basis, axis=0))) < TOLERANCES["kernel_residual_L2"],
        "SO3_gauge_horizontal_orthogonality_pass": float(np.max(np.abs(gauge_basis.T @ horizontal_basis))) < TOLERANCES["orthonormality_Linf"],
        "declared_Z2_maps_SO3_gauge_at_q_to_SO3_gauge_at_Jq": z2_gauge_subspace_residual < TOLERANCES["kernel_residual_L2"],
        "H_N_Euclidean_coefficient_control_has_full_horizontal_rank": (
            horizontal_basis.shape[1] == expected_horizontal_dim
            and horizontal_orthonormality_residual
            < TOLERANCES["orthonormality_Linf"]
        ),
        "H_N_image_is_in_ker_DG_and_SO3_orthogonal": (
            float(np.max(np.linalg.norm(DG @ horizontal_basis, axis=0)))
            < TOLERANCES["kernel_residual_L2"]
            and float(np.max(np.abs(gauge_basis.T @ horizontal_basis)))
            < TOLERANCES["orthonormality_Linf"]
        ),
        "common_first_retraction_is_exact_at_base_and_preserves_G_on_all_selected_stencils": (
            retracted_base_residual < TOLERANCES["retraction_pushforward_residual_L2"]
            and stencil_G_Linf_max < TOLERANCES["reachable_chart_G_Linf"]
        ),
        "all_selected_horizontal_and_gauge_stencils_track_their_primitive_tangents": (
            stencil_tracking_residual_max
            < TOLERANCES["reachable_chart_first_order_L2"]
        ),
        "all_selected_stencil_endpoints_preserve_sampled_kinematic_margins": stencil_sampled_kinematics_pass,
        "all_9N_gauge_parameter_columns_are_exported_as_primitive_stencils": (
            len(gauge_representative_stencils) == 9 * N
            and {
                (
                    row["sector"],
                    row["tangential_mode_index"],
                    row["so3_component"],
                )
                for row in gauge_representative_stencils.values()
            }
            == {
                (sector, mode, component)
                for sector in ("target_Q", "source_plus", "source_minus")
                for mode in range(N)
                for component in range(3)
            }
        ),
        "local_nonconstant_Ward_representatives_are_exported_for_each_sector_and_so3_component": (
            N == 1
            or all(
                any(
                    row["sector"] == sector
                    and row["so3_component"] == component
                    and row["is_local_nonconstant_parameter"]
                    and row["gauge_parameter_four_gradient_L2"] > 0.0
                    for row in gauge_representative_stencils.values()
                )
                for sector in ("target_Q", "source_plus", "source_minus")
                for component in range(3)
            )
        ),
        "reachable_joint_control_moves_every_declared_primitive_class": all(
            value > TOLERANCES["reachable_chart_activity_L2"]
            for value in reachable_motion_by_class.values()
        ),
        "retracted_joint_stencil_is_explicitly_non_Z2_in_declared_ambient_identification": (
            reachable_non_Z2 > TOLERANCES["SO3_horizontal_non_Z2_L2"] * chart_step
        ),
        "selected_SO3_horizontal_candidates_are_nonzero_independent_non_Z2": all(
            row["plus_activity_L2"] > TOLERANCES["SO3_horizontal_tangent_activity_L2"]
            and row["minus_activity_L2"] > TOLERANCES["SO3_horizontal_tangent_activity_L2"]
            and row["Z2_even_ambient_defect_L2"] > TOLERANCES["SO3_horizontal_non_Z2_L2"]
            and row["Z2_odd_ambient_defect_L2"] > TOLERANCES["SO3_horizontal_non_Z2_L2"]
            and row["non_Z2_no_parity_ambient_distance_L2"] > TOLERANCES["SO3_horizontal_non_Z2_L2"]
            and row["DG_residual_L2"] < TOLERANCES["kernel_residual_L2"]
            for row in selected
        ),
        "gamma_is_Lorentzian_with_margin": bool(np.all(np.sum(gamma_eigenvalues < 0.0, axis=1) == 1) and np.min(np.abs(gamma_eigenvalues)) > TOLERANCES["signature_eigenvalue_margin"]),
        "ambient_metrics_are_Lorentzian_with_margin": all(
            np.all(np.sum(values < 0.0, axis=1) == 1)
            and np.min(np.abs(values)) > TOLERANCES["signature_eigenvalue_margin"]
            for values in ambient_eigenvalues.values()
        ),
        "Omega_is_strictly_positive": float(np.min(detail["Omega_nodes"])) > TOLERANCES["Omega_min"],
        "bulk_Omega_is_strictly_positive": bulk_Omega_min > TOLERANCES["Omega_min"],
        "bulk_metrics_preserve_Lorentzian_signature": all(
            np.all(np.sum(values < 0.0, axis=-1) == 1)
            and np.min(np.abs(values)) > TOLERANCES["signature_eigenvalue_margin"]
            for values in bulk_metric_eigenvalues.values()
        ),
        "T_gradient_is_uniformly_timelike": float(np.max(detail["T_norm2"])) < -TOLERANCES["timelike_margin"],
        "horizontal_frame_from_gamma_T_is_orthonormal_spatial": float(np.max(np.abs(frame_gram - np.eye(3)))) < TOLERANCES["orthonormality_Linf"] and float(np.max(np.abs(spatiality))) < TOLERANCES["orthonormality_Linf"],
        "vertical_Q_frame_is_orthonormal": float(np.max(np.abs(frame_gram_vertical - np.eye(3)))) < TOLERANCES["orthonormality_Linf"],
        "R_is_SO3_and_local_chart_avoids_cut_locus": R_orthogonality < TOLERANCES["orthonormality_Linf"] and R_determinant < TOLERANCES["orthonormality_Linf"] and math.pi - rotation_norm_max > TOLERANCES["rotation_cut_locus_margin"],
        "embeddings_plus_minus_are_independent": Y_plus_minus > TOLERANCES["independent_embedding_L2"],
        "interiors_plus_minus_are_independent": interior_plus_minus > TOLERANCES["SO3_horizontal_tangent_activity_L2"],
        "B_is_excluded_from_G_and_is_free_kernel_data": float(np.max(B_DG_column_norms)) < TOLERANCES["kernel_residual_L2"],
        "radial_profiles_include_normal_jet_and_interior_bump": bool(
            radial[0, 0] == 1.0
            and np.all(radial[0, 1:] == 0.0)
            and np.all(radial[[5, 6]] == 0.0)
            and np.array_equal(radial_profile_data["boundary_jet_matrix"], np.eye(2))
        ),
        "boundary_normals_are_derived_unit_and_orthogonal": all(
            max(abs(value - 1.0) for value in row["unit_norm"]) < TOLERANCES["orthonormality_Linf"]
            and max(row["tangent_orthogonality_Linf"]) < TOLERANCES["orthonormality_Linf"]
            for row in boundary_normals.values()
        ),
        "outward_orientation_contract_is_verified_from_declared_collar_domains": (
            set(boundary_normals["plus"]["outward_orientation_determinant_sign"]) == {1}
            and set(boundary_normals["minus"]["outward_orientation_determinant_sign"]) == {-1}
        ),
        "declared_Z2_is_an_involution_and_G_equivariant_off_shell": (
            z2_twice_residual < TOLERANCES["orthonormality_Linf"]
            and z2_equivariance_residual < TOLERANCES["gluing_Linf"]
        ),
    }
    if not all(checks.values()):
        failed = [key for key, value in checks.items() if not value]
        raise SpectralCertificateError(f"seed={seed}, N={N} failed: {failed}")

    return {
        "seed": seed,
        "N": N,
        "basis": {
            "labels": list(real_fourier_basis(N)["labels"]),
            "collocation_points_T4": real_fourier_basis(N)["points_T4"].tolist(),
            "mode_wavevectors": real_fourier_basis(N)["mode_wavevectors"],
            "value_matrix": real_fourier_basis(N)["values"].tolist(),
            "four_partial_derivative_matrices": real_fourier_basis(N)["derivatives"].tolist(),
            "matrix_condition_number": real_fourier_basis(N)["condition_number"],
        },
        "dimensions": {
            "ambient_domain": ambient_layout(N).size,
            "gluing_codomain": 52 * N,
            "constraints_per_retained_coefficient": 52,
            "constraints_per_side_per_retained_coefficient": 26,
            "global_coefficient_space_rank_not_block_modal_rank": True,
            "DG_rank_expected": expected_rank,
            "DG_rank_measured": rank,
            "kernel_expected": expected_kernel,
            "kernel_measured": kernel.shape[1],
            "retraction_domain": free_layout(N).size,
            "retraction_domain_dimension": expected_retraction,
            "gauge_dimension": gauge_basis.shape[1],
            "SO3_horizontal_admissible_dimension": horizontal_basis.shape[1],
            "radial_bump_truncation_K": radial_truncation(N),
            "ambient_dimension_formula": "(294+128*K(N))*N",
            "kernel_dimension_formula": "(242+128*K(N))*N",
            "SO3_horizontal_dimension_formula": "(233+128*K(N))*N",
        },
        "primitive_configuration": {
            "ambient_q": q.tolist(),
            "ambient_q_sha256": _array_sha256(q),
            "free_common_first_coordinates_sha256": _array_sha256(free),
            "G_q": G.tolist(),
            "G_q_Linf": float(np.max(np.abs(G))),
        },
        "DG_SVD": {
            "method": "compact_SVD_of_complex_step_DG_for_singulars_and_rank; complete_QR_of_DG_transpose_for_full_kernel_basis",
            "raw_singular_values": singulars.tolist(),
            "rank_tolerance": rank_tolerance,
            "rank": rank,
            "kernel_basis_shape": list(kernel.shape),
            "kernel_basis_sha256": _array_sha256(kernel),
            "raw_kernel_vector_residual_L2": kernel_residuals.tolist(),
            "kernel_residual_max_L2": float(np.max(kernel_residuals)),
            "kernel_orthonormality_probe_Linf": kernel_gram_residual,
            "kernel_orthonormality_construction": "complete Q factor from LAPACK QR; 32 spread columns, all column norms, and eight deterministic isometry probes audited in linear cost",
        },
        "common_first_retraction": {
            "domain_dimension": expected_retraction,
            "structural_rank_argument": "explicit elimination: each free common, Y, metric-free, A_perp, B0, r_E0, J and C coordinate has an identity or locally invertible pivot in q; dimension equals dim ker DG",
            "dense_pushforward_materialized": False,
            "selected_probe_DG_residual_L2": retraction_probe_residuals,
            "selected_probe_DG_residual_max_L2": max(retraction_probe_residuals.values()),
            "retract_base_residual_L2": retracted_base_residual,
        },
        "SO3_gauge_and_horizontal_split": {
            "gauge_definition": "9N discrete_boundary_trivialization_SO3_orbit derivatives (lambda_Q,lambda_plus,lambda_minus), R'=U_Q R U_source^-1; X0 phi/A/B and adjoint J/C channels are compensated with exact exp/log/Frechet transport",
            "rho_scope": "U_source is constant in rho on the collar; the inhomogeneous tangential connection term lives in X0 and J/C rotate homogeneously; no bulk compact-support Ward claim",
            "gauge_basis_shape": list(gauge_basis.shape),
            "gauge_basis_sha256": _array_sha256(gauge_basis),
            "gauge_raw_singular_values": gauge_singulars.tolist(),
            "gauge_rank_tolerance": gauge_rank_tolerance,
            "gauge_rank": gauge_rank,
            "gauge_DG_residual_L2": np.linalg.norm(DG @ gauge_basis, axis=0).tolist(),
            "source_frame_gauge_B_activity_L2": source_gauge_B_activity,
            "source_frame_gauge_adjoint_interior_activity_L2": source_gauge_adjoint_interior_activity,
            "Z2_gauge_covariance_scope": "J_* maps the gauge subspace at q to the separately recomputed gauge subspace at Jq; no same-base-point invariance is claimed",
            "Z2_gauge_covariance_residual_max_L2": z2_gauge_subspace_residual,
            "SO3_horizontal_basis_scope": "orthogonal complement of the 9N SO3 frame orbits inside ker(DG); not a full physical quotient because BF shift, diffeomorphism, brane reparametrization and khronon gauges remain",
            "SO3_horizontal_basis_shape": list(horizontal_basis.shape),
            "SO3_horizontal_basis_sha256": _array_sha256(horizontal_basis),
            "gauge_coordinates_in_kernel_singular_values": horizontal_s.tolist(),
            "SO3_horizontal_DG_residual_max_L2": float(np.max(np.linalg.norm(DG @ horizontal_basis, axis=0))),
            "SO3_gauge_horizontal_overlap_Linf": float(np.max(np.abs(gauge_basis.T @ horizontal_basis))),
            "SO3_horizontal_orthonormality_probe_Linf": horizontal_orthonormality_residual,
            "selected_SO3_horizontal_tangents": selected,
        },
        "H_N_pointwise_generator_and_retracted_stencils": {
            "name": "H_N_Euclidean_coefficient_pointwise_horizontal_generator",
            "not_action_field": True,
            "reachability_or_neighborhood_chart_claimed": False,
            "metric": "identity on the published dimensionless coefficient coordinates; chart dependent and not a Fourier-radial mass/Sobolev metric",
            "operator_basis_shape": list(horizontal_basis.shape),
            "operator_basis_sha256": _array_sha256(horizontal_basis),
            "rank": horizontal_basis.shape[1],
            "image_DG_residual_max_L2": float(np.max(np.linalg.norm(DG @ horizontal_basis, axis=0))),
            "SO3_overlap_Linf": float(np.max(np.abs(gauge_basis.T @ horizontal_basis))),
            "retraction": "ambient_to_free_coordinates followed by construct_ambient_point; preserves trial free blocks and exactly re-solves the four G-constrained lateral traces",
            "stencil_multipliers": [-2, -1, 1, 2],
            "step": chart_step,
            "selected_horizontal_stencils": horizontal_stencils,
            "selected_gauge_representative_stencils": gauge_representative_stencils,
            "all_stencil_endpoint_G_Linf_max": stencil_G_Linf_max,
            "all_stencil_five_point_tangent_tracking_L2_max": stencil_tracking_residual_max,
            "all_stencil_endpoint_sampled_kinematics_pass": stencil_sampled_kinematics_pass,
            "joint_control_tangent_sha256": _array_sha256(control_tangent),
            "joint_control_motion_by_primitive_class_L2": reachable_motion_by_class,
            "joint_control_non_Z2_no_parity_ambient_distance_L2": reachable_non_Z2,
            "pointwise_rank_argument": "H_N is the complete-Q basis of the augmented DG/gauge orthogonality constraints at this q; the selected retracted curves verify only pointwise first-order tracking, not a neighborhood flow, radius or endpoint-map theorem",
            "independent_Newton_retraction_checked": False,
        },
        "kinematic_invariants": {
            "gamma_eigenvalues": gamma_eigenvalues.tolist(),
            "ambient_metric_eigenvalues": {side: values.tolist() for side, values in ambient_eigenvalues.items()},
            "Omega_min": float(np.min(detail["Omega_nodes"])),
            "T_norm2_max": float(np.max(detail["T_norm2"])),
            "horizontal_frame_gram_Linf": float(np.max(np.abs(frame_gram - np.eye(3)))),
            "horizontal_frame_spatiality_Linf": float(np.max(np.abs(spatiality))),
            "vertical_frame_gram_Linf": float(np.max(np.abs(frame_gram_vertical - np.eye(3)))),
            "R_orthogonality_Linf": R_orthogonality,
            "R_determinant_Linf": R_determinant,
            "R_chart_norm_max": rotation_norm_max,
            "R_cut_locus_margin": math.pi - rotation_norm_max,
            "R_plus_minus_Linf": R_plus_minus,
            "dR_Linf": {
                side: float(np.max(np.abs(detail["sides"][side]["dR_nodes"])))
                for side in SIDES
            },
            "Y_plus_minus_L2": Y_plus_minus,
            "interior_plus_minus_L2": interior_plus_minus,
            "B_DG_column_norms": B_DG_column_norms.tolist(),
            "radial_coordinate_samples": RADIAL_SAMPLE.tolist(),
            "radial_profiles_at_samples": radial.tolist(),
            "radial_profile_boundary_jets": {
                "h0_trace_lift": {"value": 1.0, "first": 0.0},
                "h1_free_normal_jet": {"value": 0.0, "first": 1.0},
                "boundary_value_first_derivative_matrix": radial_profile_data["boundary_jet_matrix"].tolist(),
                "interior_C_infinity_bumps": {"count": radial_truncation(N), "value": 0.0, "first": 0.0},
            },
            "bulk_Omega_min": bulk_Omega_min,
            "bulk_metric_eigenvalues": {
                side: values.tolist() for side, values in bulk_metric_eigenvalues.items()
            },
            "boundary_normals": boundary_normals,
            "Z2_involution_twice_Linf": z2_twice_residual,
            "Z2_G_equivariance_Linf": z2_equivariance_residual,
        },
        "bulk_primitive_samples": {
            side: {
                "values": {
                    name: value.tolist()
                    for name, value in bulk[side]["values"].items()
                },
                "radial_derivatives": {
                    name: value.tolist()
                    for name, value in bulk[side]["radial_derivatives"].items()
                },
                "component_contract": bulk[side]["component_contract"],
                "sha256": {
                    **{
                        f"values.{name}": _array_sha256(value)
                        for name, value in bulk[side]["values"].items()
                    },
                    **{
                        f"radial_derivatives.{name}": _array_sha256(value)
                        for name, value in bulk[side]["radial_derivatives"].items()
                    },
                },
            }
            for side in SIDES
        },
        "checks": checks,
    }


def mathematical_contract() -> dict[str, Any]:
    return {
        "family": "C_N=C_{+,N} x_{B_N} C_{-,N}",
        "base": "B_N=(gamma,T,Omega_Sigma,varphi_H,A_Sigma)",
        "spectral_space": "V_N is the span of the first N elements of a declared nested real T^4 enumeration (1,cos(k.x),sin(k.x),...) with k in Z^4 modulo sign; exact four partial derivatives are published and generated coefficient amplitudes carry the N-independent weight (1+|k|^2)^(-4)",
        "radial_truncation": "K(N)=N and b_j(rho)=P_j(2rho-1)*exp(4-1/[rho(1-rho)]) for j=0,...,K(N)-1 on 0<rho<1, extended by zero; this is a growing compact interior basis",
        "radial_profiles": "h0=chi and h1=rho*chi with chi=exp[-(rho/(1-rho))^2] on 0<=rho<1 give h0(0)=1,h0'(0)=0,h1(0)=0,h1'(0)=1; all perturbations vanish for rho>=1 and fields approach a fixed regular reference",
        "bulk_primitive_decoder": "bulk_primitives(q,N,rho) returns X_infinity+h0*(X0-X_infinity)+h1*J1+sum_j b_j*C_j for g_MN(15), logOmega/Omega(1), phi_a(3), A_Ma(15), B_MNP_a(30) and each first radial derivative; X0,J1,C_j are typed 64-channel primitives",
        "Omega_parameterization": "common and lateral scalar coordinates are log_Omega; physical Omega=exp(log_Omega) in G and in the bulk decoder, hence positivity is structural rather than a sampled additive bound",
        "common_first_order": [
            "generate gamma,T,Omega_Sigma,varphi_H,A_Sigma",
            "choose horizontal E0(gamma,T) and vertical Q-frame coordinate q_Q",
            "generate P_+ and P_- embeddings, metric free data, r, full B, J1 and K(N) compact interior modes independently",
            "solve only the lateral trace variables eliminated by G=0",
        ],
        "ambient_coordinate": "q contains redundant common and lateral traces before common-first retraction",
        "G_per_side_per_retained_coefficient": {
            "pullback_gamma_minus_gamma": 10,
            "exp(log_Omega_trace)_minus_exp(log_Omega_Sigma)": 1,
            "R_phi_minus_varphi_H": 3,
            "R_A_Rinv_minus_dR_Rinv_minus_A_Sigma": 12,
            "total": 26,
        },
        "G_total_per_retained_coefficient": 52,
        "rank_note": "G evaluates at N unisolvent T^4 nodes and returns the inverse-collocation spectral projection. Nonlinear R couples coefficient modes, so the certificate claims rank 52N globally, not a block-diagonal modal rank",
        "T_constraint_note": "T is common brane data and is not duplicated as a lateral trace, hence adds no row to G",
        "B_constraint_note": "the full five-dimensional adjoint three-form X0_B (10x3=30 coefficients per retained mode/side) is deliberately outside G and remains free kernel data",
        "rotation": "R_epsilon=exp(hat(r_epsilon)); d_mu R uses scipy.linalg.expm_frechet, never R hat(d_mu r)",
        "metric_retraction": "g_epsilon is solved so Y_epsilon^* g_epsilon=gamma exactly at collocation nodes; gamma is never averaged",
        "frame": "E_Q=E0 exp(-hat(q_Q)); source and target changes of frame act by R'=U_Q R U_source^-1. The relative r_E0 data are not counted a second time as gauge coordinates",
        "SO3_partial_quotient": "the 9N source-plus/source-minus/target-Q orbit is removed; the complement is SO3-horizontal admissible, not a complete physical space",
        "dimension_formula": {"ambient": "(294+128*K(N))*N", "G": "52*N", "kernel_and_retraction": "(242+128*K(N))*N", "SO3_gauge": "9*N", "Euclidean_SO3_horizontal": "(233+128*K(N))*N"},
        "tangent_theorem_finite": "T_q C_N=ker DG(q); compact SVD gives rank/singular diagnostics and complete QR(DG^T) gives the full orthonormal kernel basis. All coefficient-space orthogonality is Euclidean and chart dependent",
        "H_N_pointwise_generator": "H_N(q) is a Euclidean-coefficient orthonormal frame of ker DG(q) intersected with the orthogonal complement of the 9N boundary-trivialization SO(3) orbit. Common-first +/-h,+/-2h stencils are published for every selected horizontal tangent and every one of the 9N target/source gauge columns, including local nonconstant modes when N>=2. They are finite first-order probes, not a flow, reachable neighborhood or endpoint-map theorem. H_N is never a field or term in the v5.2 action",
        "Euclidean_coefficient_metric": {
            "W_N": "identity on dimensionless local coefficient coordinates",
            "generation_amplitude_scales": {"gamma": 0.004, "T": 0.006, "log_Omega": 0.012, "varphi": 0.24, "A_Sigma": 0.11, "Q_frame": 0.055, "Y": 0.022, "metric_free": 0.007, "A_perp": 0.09, "B_full": 0.13, "r_E0": 0.14, "J1": 0.045, "C_modes": 0.12},
            "warning": "orthogonality depends on this coordinate chart; no mass/Sobolev weighting is claimed",
        },
        "Z2_diagnostic_not_constraint": "J exchanges sides, sends Y to -Y, conjugates g by C=diag(1,1,1,1,-1), and gives tensor components parity (-1)^(number of normal indices); J^2=I and G(Jq)=P_J G(q), but Jq=q is not imposed. Gauge covariance compares J_*V_g(q) with V_g(Jq), while no-parity tangent witnesses use the declared ambient identification and make no quotient-distance claim",
        "topology_scope": "local periodic T^4 box/chart only; the executed N<=3 modes cover the first declared multi-directional wavevector but are not directional convergence evidence and do not identify the box with noncompact Sigma=R^(1,3)",
        "regularity_scope": f"tangential coefficient decay power {SPECTRAL_DECAY_POWER} is compatible with the declared s={SOBLEV_TARGET_S}>9/2 target on T^4, but no radial Sobolev norm or uniform bound is certified here",
        "chosen_continuous_promotion_branch": "future exact analytic identity on this declared restricted h0/J1/growing-interior radial class; global density is neither needed for that explicitly restricted theorem nor claimed by this finite certificate",
        "global_density_obstruction": "the restricted h0/J1 boundary-jet ansatz links higher normal jets and therefore is not dense in the full unconstrained H^s bulk space for s>9/2; density_union_C_N_pass remains false",
        "continuous_obligation": "for any global C1/N1 claim, prove constraint-preserving density or separately state and prove an exact restricted-class identity; also require a uniformly bounded right inverse/retraction of DG_N in mass/Sobolev norms, uniform inertia/Omega margins, convergence of S and DS/Green, periodic-box exhaustion and tail control",
        "legacy_147": {
            "role": "R=I legacy regression reference metadata only",
            "legacy_component_count": 147,
            "regression_executed": False,
            "used_to_define_ambient_dimension": False,
            "used_to_define_DG_rank": False,
            "used_to_define_kernel": False,
        },
    }


def build_payload() -> dict[str, Any]:
    upstream = _pin_upstreams()
    contract = mathematical_contract()
    freeze_material = {
        "contract": contract,
        "tolerances": TOLERANCES,
        "truncations": TRUNCATIONS,
        "development_seed": DEVELOPMENT_SEED,
    }
    contract_freeze_sha256 = _canonical_sha256(freeze_material)

    receipts: list[dict[str, Any]] = []
    # Only identity and development are primary.  Holdouts are derived and
    # revealed by a separate clean runner after this generator is frozen.
    for seed in PRIMARY_SEEDS:
        for N in TRUNCATIONS:
            receipts.append(analyze_configuration(seed, N))

    identity_rows = [row for row in receipts if row["seed"] == IDENTITY_CONTROL_SEED]
    nonidentity_rows = [row for row in receipts if row["seed"] != IDENTITY_CONTROL_SEED]
    checks = {
        "all_N_1_2_3_execute": {row["N"] for row in receipts} == set(TRUNCATIONS),
        "declared_real_Fourier_spaces_are_nested": all(
            list(real_fourier_basis(N + 1)["labels"])[:N]
            == list(real_fourier_basis(N)["labels"])
            for N in range(1, 7)
        ),
        "generated_free_coefficients_are_prefix_nested": all(
            free_coefficients_are_prefix_nested(seed, lower, upper)
            for seed in PRIMARY_SEEDS
            for lower, upper in ((1, 2), (2, 3))
        ),
        "all_configurations_and_kernel_audits_pass": all(all(row["checks"].values()) for row in receipts),
        "identity_R_control_pass": all(
            row["kinematic_invariants"]["R_chart_norm_max"] < 2.0e-13 for row in identity_rows
        ),
        "multiple_nontrivial_R_tx_members_pass": all(
            row["kinematic_invariants"]["R_plus_minus_Linf"] > TOLERANCES["nonidentity_rotation_Linf"]
            and row["kinematic_invariants"]["R_chart_norm_max"] > TOLERANCES["nonidentity_rotation_Linf"]
            for row in nonidentity_rows
        ),
        "multiple_nonconstant_R_tx_members_pass": all(
            max(row["kinematic_invariants"]["dR_Linf"].values())
            > TOLERANCES["nonidentity_rotation_Linf"]
            for row in nonidentity_rows
            if row["N"] >= 2
        ),
        "reserved_seed_values_are_not_embedded_or_evaluated_in_primary": True,
        "upstream_bytes_pinned_without_helper_or_decision_consumption": all(
            not row["python_helper_imported_or_called"]
            and not row["decision_boolean_consumed"]
            and not row["prediction_consumed"]
            and not row["ledger_consumed"]
            and not row["action_value_consumed"]
            for row in upstream.values()
        ),
        "legacy_147_is_metadata_only": not contract["legacy_147"]["used_to_define_DG_rank"],
    }
    if not all(checks.values()):
        raise SpectralCertificateError(f"global certificate checks failed: {checks}")

    decision = {
        CERTIFICATE_NAME: True,
        "finite_C_N_kinematics_pass": True,
        "finite_C_N_gluing_and_tangent_kernel_pass": True,
        "finite_retracted_admissible_stencil_pass": True,
        **{key: False for key in FAIL_CLOSED_KEYS},
        "status": "RESTRICTED_SPECTRAL_FAMILY_CERTIFICATE__FINITE_C_N_KINEMATICS_ONLY__ACTION_AND_CONTINUUM_FAIL_CLOSED",
    }
    if any(decision[key] is not False for key in FAIL_CLOSED_KEYS):
        raise SpectralCertificateError("a fail-closed claim was promoted")

    scientific = {
        "certificate_name": CERTIFICATE_NAME,
        "mathematical_contract": contract,
        "primary_contract_freeze_sha256": contract_freeze_sha256,
        "truncations": list(TRUNCATIONS),
        "seeds": {
            "identity_control": IDENTITY_CONTROL_SEED,
            "development": DEVELOPMENT_SEED,
            "primary": list(PRIMARY_SEEDS),
            "reserved_seed_domains": list(RESERVED_SEED_DOMAINS),
            "reserved_seed_values_embedded": False,
            "reserved_seed_values_revealed": False,
            "reserved_seed_receipts_present": False,
            "external_clean_runner_protocol": "after freezing generator bytes, derive each nonnegative seed from SHA256(generator_sha256 + ':' + domain), record generator hash/domain/reveal in a separate artifact, and never feed the result back into formulas, tolerances or primary checks",
            "generator_accepts_external_nonnegative_seed": True,
            "independent_reserved_seed_protocol_pass": False,
        },
        "tolerances": TOLERANCES,
        "ambient_layout_by_N": {str(N): ambient_layout(N).contract() for N in TRUNCATIONS},
        "free_layout_by_N": {str(N): free_layout(N).contract() for N in TRUNCATIONS},
        "configuration_and_tangent_receipts": receipts,
        "spectral_refinement_status": {
            "radial_diagonal": "K(N)=N",
            "executed_pairs": [{"tangential_N": N, "radial_K": radial_truncation(N)} for N in TRUNCATIONS],
            "action_or_residual_convergence_table": [],
            "convergence_rate_claimed": False,
            "reason": "this certificate establishes finite kinematics only; simultaneous action/derivative/quadrature/mesh/N refinement belongs to a later independent evaluator",
        },
        "checks": checks,
        "decision": decision,
    }
    generator_path = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "title": "Restricted spectral family certificate v5.6.4",
        "classification": "theory_only;finite_C_N_kinematics;restricted_spectral_family_certificate;action_not_evaluated;continuous_theorem_open",
        "upstream_byte_pins": upstream,
        "evaluator_input_contract": {
            "primitive_only": True,
            "configuration_field": "scientific.configuration_and_tangent_receipts[*].primitive_configuration.ambient_q",
            "tangent_field": "scientific.configuration_and_tangent_receipts[*].SO3_gauge_and_horizontal_split.selected_SO3_horizontal_tangents[*].ambient_primitive_tangent",
            "gauge_tangent_field": "scientific.configuration_and_tangent_receipts[*].H_N_pointwise_generator_and_retracted_stencils.selected_gauge_representative_stencils[*].ambient_primitive_tangent_f64le",
            "finite_difference_stencil_field": "scientific.configuration_and_tangent_receipts[*].H_N_pointwise_generator_and_retracted_stencils",
            "compact_primitive_array_encoding": "base64 of contiguous little-endian float64 with explicit shape and SHA-256; no generator helper is needed to decode",
            "coordinate_layout": "scientific.ambient_layout_by_N",
            "bulk_primitive_field": "scientific.configuration_and_tangent_receipts[*].bulk_primitive_samples",
            "partial_gauge_warning": "selected tangents are SO3-horizontal only; future evaluators must not label them fully physical before remaining gauge quotients",
            "forbidden_to_future_evaluators": [
                "this generator's helpers",
                "v5.2/v5.6.3 Python helpers",
                "Eulerian objects",
                "ledgers",
                "predictions",
                "primary-gate booleans",
            ],
        },
        "evidence_boundary": "Only finite common-first C_N kinematics, full gluing rank, and admissible tangent geometry are certified. No action residual or continuous C1/N1 theorem is tested.",
        "scientific": scientific,
        "scientific_sha256": _canonical_sha256(scientific),
        "provenance": {
            "generator": {"path": str(generator_path.relative_to(REPO)), "sha256": _sha256(generator_path)},
            "test": {"path": str(TEST.relative_to(REPO)), "sha256": _sha256(TEST)},
            "upstream_helpers_imported": [],
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "thread_contract": "single_process_single_thread_targeted_generation",
            "Skai_or_device_control_touched": False,
        },
        "limits": [
            "The periodic local chart is not noncompact Sigma; box exhaustion and tails are open.",
            "Euclidean singular values are finite diagnostics, not uniform Sobolev or mass-weighted bounds.",
            "The exponential parameterization is a local SO(3) chart with an audited cut-locus margin.",
            "The h0/J1 boundary-jet ansatz is an explicit restricted radial class; it is not dense in unconstrained H^s for s>9/2 because higher continuous normal jets are linked.",
            "With K(N)=N the ambient dimension is quadratic in N and explicit complete kernel/horizontal bases have O(N^4) memory scaling; only N=1,2,3 are certified, not scalable asymptotics or a convergence rate.",
            "H_N uses the identity metric on dimensionless coefficient coordinates; mass/Sobolev-weighted horizontality, neighborhood-smooth frame alignment, and an independent Newton retraction remain open.",
            "Signature, timelikeness, orientation and cut-locus margins are recomputed only on each finite N-node by 7-rho stencil endpoint grid; no padded/off-grid analytic preservation theorem is claimed.",
            "The 147-component object is an R=I legacy reference metadata count only; this certificate does not execute that historical regression.",
            "No action, AD/JVP, finite-difference action route, Eulerian, Green, Robin, bulk, interface, or corner residual is evaluated.",
            "No mutant campaign or clean-process independent red-team is claimed by this artifact.",
            "C1_ACTION, N1_ACTION, B4, B5, publication, and every continuous-limit obligation remain false.",
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
