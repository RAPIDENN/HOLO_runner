#!/usr/bin/env python3
"""Literal Torch route A for the restricted v5.2 action.

This file is deliberately self-contained.  It does not import the v5.6.4
generator/exporter, a v5.6.2 evaluator, an Eulerian ledger, or any repository
helper.  It accepts only the frozen v5.6.4.2 pointwise primitive bundle,
reconstructs its free coefficient layout and Fourier/radial basis, eliminates
the constrained traces by the common-first equations at every action node,
and evaluates the literal v5.2 action with Torch float64 tensor calculus.

The route exposes an AD/JVP of ``S_v5_2 o common_first_pointwise_decode``.
Agreement with another
route, Green identities, simultaneous refinement, and every C1/N1/B4/B5
promotion remain separate obligations.  In particular, this route is one
implementation, not an independent audit of itself.
"""

from __future__ import annotations

import base64
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import torch


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ARTIFACT = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_literal_torch_action_route_a_v5_6_5_certificate.json"
)
TEST = HERE / "test_one_omega_topological_so3_literal_torch_action_route_a_v5_6_5_certificate.py"
PRIMITIVE_BUNDLE = (
    HERE
    / "artifacts"
    / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitive_bundle.json"
)

BUNDLE_SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-v5-6-4-2-"
    "pointwise-primitive-bundle.v1"
)
SCHEMA = "holo.one-omega-topological-so3-literal-torch-action-route-a-v5-6-5-certificate.v1"
EXPECTED_BUNDLE_TOP_LEVEL = {
    "schema",
    "classification",
    "source_pins",
    "action_contract",
    "geometry_convention",
    "pointwise_decoder_contract",
    "primary_member",
    "identity_control",
    "off_collocation_validation_nodes",
    "toroidal_relative_scope",
    "dependency_graph",
    "payload_sha256",
}

# Filled only after the exporter is frozen.  The bundle also carries and is
# checked against its own canonical payload hash; the byte pin prevents a
# different serialization from silently entering this route.
PRIMITIVE_BUNDLE_FILE_SHA256 = (
    "bcbb0037a2b025d9ece7387b5962a910e31eced7294ccb5324ab764c3bc7cb26"
)
GAUSS_SIGN_CORRIGENDUM_SHA256 = (
    "7c2c3e46ea73b312f753d944e43cd2a2e224d000e5ddd3c3e15ff816e76e441a"
)
V5_2_EXACT_ACTION_SHA256 = (
    "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
)
V5_2_EXACT_ACTION_CANONICAL_BYTES = 1123

DTYPE = torch.float64
DEVICE = torch.device("cpu")
torch.set_default_dtype(DTYPE)
torch.set_num_threads(1)

SIDES = ("plus", "minus")
SIDE_RADIAL_SIGN = {"plus": -1.0, "minus": 1.0}
SIDE_OUTWARD_SIGN = {"plus": 1.0, "minus": -1.0}
SYMMETRIC4 = tuple((i, j) for i in range(4) for j in range(i, 4))
SYMMETRIC5 = tuple((i, j) for i in range(5) for j in range(i, 5))
B_TRIPLES = tuple(
    (i, j, k)
    for i in range(5)
    for j in range(i + 1, 5)
    for k in range(j + 1, 5)
)

EXACT_ACTION = {
    "BF": "S_BF=sum_eps int_Meps <B_eps wedge F[A_eps]>, <X,Y>=-tr_3(XY)/2",
    "GHY": "S_GHY=M5^3*sum_eps int_Sigma sqrt(-gamma)*Theta_eps for outward normals",
    "Robin_intrinsic": "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)",
    "bulk_gauged": "S_bulk_gauged=sum_eps int_Meps sqrt(-g_eps)*[M5^3*R_eps/2-G*(nabla Omega_eps)^2/2-U(Omega_eps)-Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2-Z5*M^2*Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)]",
    "bulk_potential": "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
    "foliation_lower": "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-B4_bar*Rcal^2/(16*k_infinity^2)]",
    "full_V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
    "gauged_conformal_derivative": "P_eps_M=D_(A_eps,M)phi_eps+3*phi_eps*partial_M log(Omega_eps)/2",
    "removed_terms": "S_X=0 and every bulk screen-clock term=0",
    "superpotential": "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]",
    "total": "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF",
    "wall_background": "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2]",
}

COEFFICIENTS = {
    "B4_bar": 0.8,
    "M4_bulk_squared_selected_one_Omega_wall_value": 1.107013790800849,
    "M5_cubed": 1.0,
    "Robin_kappa_hat": 1.0,
    "Robin_kappa_in_Mb_units": 0.5,
    "Robin_y": math.sqrt(3.0),
    "Robin_y_squared": 3.0,
    "brane_Mb_squared": 2.0,
    "brane_beta": 2.0,
    "compensator_metric_G": 1.2,
    "eta": 3.107013790800849,
    "k_BF_trace_equivalent": -0.5,
    "k_infinity": 1.0,
    "kappa_BF_inner_product": 1.0,
    "lambda_K": -0.5535068954004245,
    "material_Z5_per_side": 1.0,
    "material_mass_M": 1.0,
    "xi": 1.0,
}

BULK_ATOMS = (
    "EH",
    "Omega_kinetic",
    "Omega_potential",
    "P_kinetic",
    "full_V4",
    "BF",
)
BRANE_ATOMS = (
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)
COMPONENT_NAMES = tuple(
    name
    for side in SIDES
    for name in tuple(f"{atom}_bulk_{side}" for atom in BULK_ATOMS)
    + (f"GHY_{side}",)
) + BRANE_ATOMS
OUTPUT_NAMES = COMPONENT_NAMES + ("S_total",)


class LiteralTorchRouteError(ValueError):
    """A literal action, bundle, shape, or finite-domain contract drifted."""


@dataclass(frozen=True)
class QuadratureSpec:
    """Finite periodic-box/collar quadrature used by one route-A evaluation."""

    tangential_order_per_axis: int = 1
    radial_order: int = 3

    def validate(self) -> None:
        if (
            isinstance(self.tangential_order_per_axis, bool)
            or not isinstance(self.tangential_order_per_axis, int)
            or self.tangential_order_per_axis <= 0
        ):
            raise LiteralTorchRouteError("tangential quadrature order must be positive")
        if (
            isinstance(self.radial_order, bool)
            or not isinstance(self.radial_order, int)
            or self.radial_order <= 0
        ):
            raise LiteralTorchRouteError("radial quadrature order must be positive")


def lorentzian_inertia_diagnostics(
    metric: torch.Tensor,
    *,
    label: str,
    zero_tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Check signature ``(-,+,...,+)`` at every supplied action node.

    This is an inertia check, not a determinant-sign proxy.  It intentionally
    reports the raw eigenvalue margin as a route-owned diagnostic so a later
    comparator can audit whether every bulk/interface quadrature node stayed
    inside the same Lorentzian component.
    """

    if metric.ndim < 2 or metric.shape[-1] != metric.shape[-2]:
        raise LiteralTorchRouteError(f"{label}: metric must end in a square matrix")
    if zero_tolerance <= 0.0 or not math.isfinite(zero_tolerance):
        raise LiteralTorchRouteError(f"{label}: invalid inertia zero tolerance")
    symmetry_residual = torch.amax(torch.abs(metric - metric.transpose(-1, -2)))
    eigenvalues = torch.linalg.eigvalsh(metric)
    negative_count = torch.sum(eigenvalues < -zero_tolerance, dim=-1)
    positive_count = torch.sum(eigenvalues > zero_tolerance, dim=-1)
    zero_count = metric.shape[-1] - negative_count - positive_count
    expected_positive = metric.shape[-1] - 1
    node_pass = (
        (negative_count == 1)
        & (positive_count == expected_positive)
        & (zero_count == 0)
    )
    flattened = eigenvalues.reshape(-1, metric.shape[-1])
    return {
        "label": label,
        "matrix_dimension": metric.shape[-1],
        "node_count": flattened.shape[0],
        "all_nodes_lorentzian": bool(torch.all(node_pass).detach()),
        "negative_count_min": int(torch.min(negative_count).detach()),
        "negative_count_max": int(torch.max(negative_count).detach()),
        "positive_count_min": int(torch.min(positive_count).detach()),
        "positive_count_max": int(torch.max(positive_count).detach()),
        "zero_count_max": int(torch.max(zero_count).detach()),
        "minimum_absolute_eigenvalue": float(
            torch.min(torch.abs(flattened)).detach()
        ),
        "minimum_eigenvalue": float(torch.min(flattened).detach()),
        "maximum_eigenvalue": float(torch.max(flattened).detach()),
        "symmetry_residual_Linf": float(symmetry_residual.detach()),
        "zero_tolerance": zero_tolerance,
    }


def require_lorentzian_inertia(report: Mapping[str, Any]) -> None:
    """Fail closed when any action node leaves the declared Lorentzian sector."""

    if report.get("all_nodes_lorentzian") is not True:
        raise LiteralTorchRouteError(
            f"{report.get('label', 'metric')}: Lorentzian inertia failed at an action node"
        )


class VectorLayout:
    """Stable named slices for the flat ambient primitive vector."""

    def __init__(self) -> None:
        self.size = 0
        self.rows: dict[str, tuple[slice, tuple[int, ...]]] = {}

    def add(self, name: str, shape: tuple[int, ...]) -> None:
        if name in self.rows:
            raise LiteralTorchRouteError(f"duplicate layout field: {name}")
        width = math.prod(shape)
        self.rows[name] = (slice(self.size, self.size + width), shape)
        self.size += width

    def get(self, vector: torch.Tensor, name: str) -> torch.Tensor:
        block, shape = self.rows[name]
        return vector[block].reshape(shape)

    def contract(self) -> dict[str, Any]:
        return {
            name: {"start": block.start, "stop": block.stop, "shape": list(shape)}
            for name, (block, shape) in self.rows.items()
        }


def _validate_N_K(N: int, K: int) -> None:
    for label, value in (("N", N), ("K", K)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise LiteralTorchRouteError(f"{label} must be a positive integer")


def ambient_layout(N: int, K: int) -> VectorLayout:
    _validate_N_K(N, K)
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
    expected = (294 + 128 * K) * N
    if layout.size != expected:
        raise LiteralTorchRouteError("ambient dimension formula drift")
    return layout


def free_layout(N: int, K: int) -> VectorLayout:
    """Authoritative common-first coordinates of the v5.6.4.2 bundle.

    Constrained side traces are deliberately absent: they are reconstructed
    pointwise from these blocks, not projected back through an N-node grid.
    """

    _validate_N_K(N, K)
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
    expected = (242 + 128 * K) * N
    if layout.size != expected:
        raise LiteralTorchRouteError("free dimension formula drift")
    return layout


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise LiteralTorchRouteError(f"cannot hash {path}: {exc}") from exc


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _tensor_sha256(value: torch.Tensor) -> str:
    raw = value.detach().to(device="cpu", dtype=DTYPE).contiguous().numpy().astype(
        "<f8", copy=False
    ).tobytes()
    return hashlib.sha256(raw).hexdigest()


def decode_f64le(record: Mapping[str, Any], *, label: str) -> torch.Tensor:
    """Decode one portable primitive array without calling an exporter helper."""

    if record.get("encoding") != "base64" or record.get("dtype") not in {
        "<f8",
        "float64-le",
        "f64le",
    }:
        raise LiteralTorchRouteError(f"{label}: unsupported primitive encoding")
    shape_raw = record.get("shape")
    if not isinstance(shape_raw, list) or any(
        isinstance(item, bool) or not isinstance(item, int) or item < 0
        for item in shape_raw
    ):
        raise LiteralTorchRouteError(f"{label}: invalid shape")
    try:
        raw = base64.b64decode(record["data"], validate=True)
    except (KeyError, ValueError) as exc:
        raise LiteralTorchRouteError(f"{label}: invalid base64") from exc
    digest = hashlib.sha256(raw).hexdigest()
    if digest != record.get("sha256"):
        raise LiteralTorchRouteError(f"{label}: primitive byte hash drift")
    expected_bytes = math.prod(shape_raw) * 8
    if len(raw) != expected_bytes:
        raise LiteralTorchRouteError(f"{label}: primitive byte length drift")
    # bytearray gives Torch a writable owner; clone then severs that storage.
    tensor = torch.frombuffer(bytearray(raw), dtype=DTYPE).clone()
    return tensor.reshape(tuple(shape_raw)).to(device=DEVICE)


def _hat(vector: torch.Tensor) -> torch.Tensor:
    if vector.shape[-1] != 3:
        raise LiteralTorchRouteError("hat expects a final SO(3) vector axis")
    x, y, z = vector.unbind(dim=-1)
    zero = torch.zeros_like(x)
    return torch.stack(
        (
            zero,
            -z,
            y,
            z,
            zero,
            -x,
            -y,
            x,
            zero,
        ),
        dim=-1,
    ).reshape(vector.shape[:-1] + (3, 3))


def _vee(matrix: torch.Tensor) -> torch.Tensor:
    return torch.stack((matrix[..., 2, 1], matrix[..., 0, 2], matrix[..., 1, 0]), dim=-1)


def _vec_to_sym(
    vector: torch.Tensor, size: int, pairs: Sequence[tuple[int, int]]
) -> torch.Tensor:
    if vector.shape[-1] != len(pairs):
        raise LiteralTorchRouteError("symmetric-vector width drift")
    rows: list[torch.Tensor] = []
    lookup = {pair: index for index, pair in enumerate(pairs)}
    for i in range(size):
        rows.append(
            torch.stack(
                tuple(vector[..., lookup[(min(i, j), max(i, j))]] for j in range(size)),
                dim=-1,
            )
        )
    return torch.stack(rows, dim=-2)


def _sym_to_vec(matrix: torch.Tensor, pairs: Sequence[tuple[int, int]]) -> torch.Tensor:
    return torch.stack(tuple(matrix[..., i, j] for i, j in pairs), dim=-1)


def _cross(left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
    return torch.linalg.cross(left, right, dim=-1)


def _permutation_sign(items: Sequence[int]) -> int:
    inversions = sum(
        int(items[i] > items[j])
        for i in range(len(items))
        for j in range(i + 1, len(items))
    )
    return -1 if inversions % 2 else 1


def _mode_wavevectors(N: int) -> tuple[tuple[int, int, int, int], ...]:
    """Reimplement the nested real T^4 basis enumeration from its contract."""

    _validate_N_K(N, 1)
    priority = [(1, 1, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    nonzero: list[tuple[int, int, int, int]] = []
    for vector in priority:
        if vector not in nonzero:
            nonzero.append(vector)
    radius = 1
    target = max(1, (N - 1 + 1) // 2)
    while len(nonzero) < target:
        candidates: list[tuple[int, int, int, int]] = []
        for vector in itertools.product(range(-radius, radius + 1), repeat=4):
            if vector == (0, 0, 0, 0) or max(map(abs, vector)) != radius:
                continue
            first = next(item for item in vector if item != 0)
            if first > 0:
                candidates.append(vector)
        for vector in sorted(candidates, key=lambda item: (sum(map(abs, item)), item)):
            if vector not in nonzero:
                nonzero.append(vector)
        radius += 1
    result: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)]
    for index in range(1, N):
        result.append(nonzero[(index - 1) // 2])
    return tuple(result)


def evaluate_real_fourier_basis(points: torch.Tensor, N: int) -> dict[str, torch.Tensor]:
    """Values plus first/second coordinate derivatives at arbitrary T^4 points."""

    if points.ndim != 2 or points.shape[1] != 4:
        raise LiteralTorchRouteError("Fourier points must have shape (P,4)")
    wavevectors = _mode_wavevectors(N)
    values: list[torch.Tensor] = []
    first: list[torch.Tensor] = []
    second: list[torch.Tensor] = []
    for mode, vector_tuple in enumerate(wavevectors):
        vector = torch.tensor(vector_tuple, dtype=DTYPE, device=points.device)
        if mode == 0:
            value = torch.ones(points.shape[0], dtype=DTYPE, device=points.device)
            derivative = torch.zeros(points.shape[0], 4, dtype=DTYPE, device=points.device)
            hessian = torch.zeros(points.shape[0], 4, 4, dtype=DTYPE, device=points.device)
        else:
            phase = points @ vector
            is_cosine = mode % 2 == 1
            value = torch.cos(phase) if is_cosine else torch.sin(phase)
            scalar_first = -torch.sin(phase) if is_cosine else torch.cos(phase)
            derivative = scalar_first[:, None] * vector[None, :]
            hessian = -value[:, None, None] * vector[None, :, None] * vector[None, None, :]
        values.append(value)
        first.append(derivative)
        second.append(hessian)
    return {
        "values": torch.stack(values, dim=-1),
        "first": torch.stack(first, dim=-1),
        "second": torch.stack(second, dim=-1),
        "wavevectors": torch.tensor(wavevectors, dtype=DTYPE, device=points.device),
    }


def collocation_basis(N: int) -> dict[str, torch.Tensor]:
    irrational = torch.sqrt(torch.tensor((2.0, 3.0, 5.0, 7.0), dtype=DTYPE))
    row = torch.arange(N, dtype=DTYPE)[:, None] + 0.173
    points = 2.0 * math.pi * torch.remainder(row * irrational[None, :], 1.0)
    evaluated = evaluate_real_fourier_basis(points, N)
    values = evaluated["values"]
    return {
        **evaluated,
        "points": points,
        "inverse": torch.linalg.inv(values),
        "condition_number": torch.linalg.cond(values),
    }


def _matrix_exp_frechet(algebra: torch.Tensor, direction: torch.Tensor) -> torch.Tensor:
    """Exact Frechet derivative via the upper block of a matrix exponential."""

    if algebra.shape != direction.shape or algebra.shape[-2:] != (3, 3):
        raise LiteralTorchRouteError("SO(3) Frechet shape drift")
    zeros = torch.zeros_like(algebra)
    top = torch.cat((algebra, direction), dim=-1)
    bottom = torch.cat((zeros, algebra), dim=-1)
    block = torch.cat((top, bottom), dim=-2)
    return torch.matrix_exp(block)[..., :3, 3:]


def rotation_and_tangential_derivatives(
    coefficients: torch.Tensor, basis: Mapping[str, torch.Tensor]
) -> tuple[torch.Tensor, torch.Tensor]:
    values = torch.einsum("pm,ma->pa", basis["values"], coefficients)
    first = torch.einsum("pum,ma->pua", basis["first"], coefficients)
    algebra = _hat(values)
    rotations = torch.matrix_exp(algebra)
    directions = _hat(first)
    repeated = algebra[:, None, :, :].expand_as(directions)
    derivatives = _matrix_exp_frechet(repeated, directions)
    return rotations, derivatives


def _flatten_layout_blocks(
    layout: VectorLayout, blocks: Mapping[str, torch.Tensor]
) -> torch.Tensor:
    if set(blocks) != set(layout.rows):
        missing = sorted(set(layout.rows) - set(blocks))
        extra = sorted(set(blocks) - set(layout.rows))
        raise LiteralTorchRouteError(f"layout block mismatch: missing={missing}, extra={extra}")
    flattened: list[torch.Tensor] = []
    for name, (_, shape) in layout.rows.items():
        value = blocks[name]
        if tuple(value.shape) != shape:
            raise LiteralTorchRouteError(
                f"{name}: retraction shape {tuple(value.shape)} != {shape}"
            )
        flattened.append(value.reshape(-1))
    return torch.cat(flattened)


def retract_ambient_q(q: torch.Tensor, N: int, K: int) -> torch.Tensor:
    """Common-first retraction on redundant ambient coefficients.

    The trial common blocks and every unconstrained side block are retained.
    Only the four constrained lateral traces are re-solved: tangential metric,
    log Omega, associated vector, and pulled-back tangential connection.  This
    is algebraically the same local elimination as introducing an E0 section
    and then cancelling it; avoiding that cancellation here reduces the AD
    graph without changing q on the constraint surface.
    """

    layout = ambient_layout(N, K)
    if q.ndim != 1 or q.numel() != layout.size:
        raise LiteralTorchRouteError(
            f"ambient q has shape {tuple(q.shape)}, expected ({layout.size},)"
        )
    basis = collocation_basis(N)
    F = basis["values"]
    Finv = basis["inverse"]
    blocks: dict[str, torch.Tensor] = {
        name: layout.get(q, name) for name in layout.rows
    }

    gamma_nodes = _vec_to_sym(F @ blocks["common.gamma"], 4, SYMMETRIC4)
    varphi_nodes = F @ blocks["common.varphi"]
    A_common_nodes = (
        F @ blocks["common.A_Sigma"].reshape(N, 12)
    ).reshape(N, 4, 3)

    for side in SIDES:
        Y_coeff = blocks[f"{side}.Y"]
        Y_gradient = torch.einsum(
            "pum,mc->puc", basis["first"], Y_coeff
        )[..., 0]

        g_trial_nodes = _vec_to_sym(
            F @ blocks[f"{side}.g_trace"], 5, SYMMETRIC5
        )
        normal_metric = g_trial_nodes[:, 4, 4]
        adapted_cross = (
            g_trial_nodes[:, :4, 4]
            + normal_metric[:, None] * Y_gradient
        )
        upper = (
            gamma_nodes
            - adapted_cross[:, :, None] * Y_gradient[:, None, :]
            - Y_gradient[:, :, None] * adapted_cross[:, None, :]
            + normal_metric[:, None, None]
            * Y_gradient[:, :, None]
            * Y_gradient[:, None, :]
        )
        ambient_cross = adapted_cross - normal_metric[:, None] * Y_gradient
        row0 = torch.cat((upper, ambient_cross[:, :, None]), dim=-1)
        row1 = torch.cat((ambient_cross, normal_metric[:, None]), dim=-1)[:, None, :]
        solved_metric = torch.cat((row0, row1), dim=-2)
        blocks[f"{side}.g_trace"] = Finv @ _sym_to_vec(solved_metric, SYMMETRIC5)

        blocks[f"{side}.log_Omega_trace"] = blocks["common.log_Omega"]

        R, dR = rotation_and_tangential_derivatives(blocks[f"{side}.r"], basis)
        phi_source = torch.einsum("pji,pj->pi", R, varphi_nodes)
        blocks[f"{side}.phi_trace"] = Finv @ phi_source

        A_source_matrices = (
            torch.einsum(
                "pij,pujk,pkl->puil",
                R.transpose(-1, -2),
                _hat(A_common_nodes),
                R,
            )
            + torch.einsum("pij,pujk->puik", R.transpose(-1, -2), dR)
        )
        A_source_pullback = _vee(A_source_matrices)
        A_trial_nodes = (
            F @ blocks[f"{side}.A_trace_full"].reshape(N, 15)
        ).reshape(N, 5, 3)
        A_normal = A_trial_nodes[:, 4]
        A_full_nodes = torch.cat(
            (
                A_source_pullback
                - Y_gradient[:, :, None] * A_normal[:, None, :],
                A_normal[:, None, :],
            ),
            dim=1,
        )
        blocks[f"{side}.A_trace_full"] = (
            Finv @ A_full_nodes.reshape(N, 15)
        ).reshape(N, 5, 3)

    return _flatten_layout_blocks(layout, blocks)


def gluing_map(q: torch.Tensor, N: int, K: int) -> torch.Tensor:
    """The full 52N projected gluing map on redundant ambient q."""

    layout = ambient_layout(N, K)
    if q.ndim != 1 or q.numel() != layout.size:
        raise LiteralTorchRouteError("gluing-map ambient shape drift")
    basis = collocation_basis(N)
    F, Finv = basis["values"], basis["inverse"]
    gamma = _vec_to_sym(F @ layout.get(q, "common.gamma"), 4, SYMMETRIC4)
    omega = torch.exp((F @ layout.get(q, "common.log_Omega"))[..., 0])
    varphi = F @ layout.get(q, "common.varphi")
    A_common = (
        F @ layout.get(q, "common.A_Sigma").reshape(N, 12)
    ).reshape(N, 4, 3)
    side_blocks: list[torch.Tensor] = []
    for side in SIDES:
        Y_coeff = layout.get(q, f"{side}.Y")
        Y_gradient = torch.einsum(
            "pum,mc->puc", basis["first"], Y_coeff
        )[..., 0]
        tangent = torch.zeros(N, 5, 4, dtype=DTYPE, device=q.device)
        tangent[:, :4, :] = torch.eye(4, dtype=DTYPE, device=q.device)[None, ...]
        tangent[:, 4, :] = Y_gradient
        metric = _vec_to_sym(F @ layout.get(q, f"{side}.g_trace"), 5, SYMMETRIC5)
        induced = torch.einsum("pmi,pmn,pnj->pij", tangent, metric, tangent)
        omega_side = torch.exp((F @ layout.get(q, f"{side}.log_Omega_trace"))[..., 0])
        phi_side = F @ layout.get(q, f"{side}.phi_trace")
        A_full = (
            F @ layout.get(q, f"{side}.A_trace_full").reshape(N, 15)
        ).reshape(N, 5, 3)
        A_pull = A_full[:, :4] + Y_gradient[:, :, None] * A_full[:, 4, None, :]
        R, dR = rotation_and_tangential_derivatives(layout.get(q, f"{side}.r"), basis)
        A_transported_matrix = (
            torch.einsum("pij,pujk,pkl->puil", R, _hat(A_pull), R.transpose(-1, -2))
            - torch.einsum("puij,pjk->puik", dR, R.transpose(-1, -2))
        )
        A_transported = _vee(A_transported_matrix)
        residual = torch.cat(
            (
                _sym_to_vec(induced - gamma, SYMMETRIC4),
                (omega_side - omega)[:, None],
                torch.einsum("pij,pj->pi", R, phi_side) - varphi,
                (A_transported - A_common).reshape(N, 12),
            ),
            dim=-1,
        )
        side_blocks.append(residual)
    nodal = torch.stack(side_blocks, dim=1)
    return torch.einsum("mp,psc->msc", Finv, nodal).reshape(-1)


def pointwise_gluing_residual(
    free: torch.Tensor,
    N: int,
    K: int,
    points: torch.Tensor,
) -> torch.Tensor:
    """Unprojected 52-component common-first gluing residual per T4 node."""

    layout = free_layout(N, K)
    common = pointwise_common_fields(free, N, K, points)
    basis = evaluate_real_fourier_basis(points, N)
    side_residuals: list[torch.Tensor] = []
    for side in SIDES:
        trace = torch.func.vmap(
            lambda point: _common_first_trace_value_at_point(
                free, N, K, side, point
            )
        )(points)
        metric = _vec_to_sym(trace[..., :15], 5, SYMMETRIC5)
        Y_value, Y_first_raw, _ = _spectral_evaluate(
            layout.get(free, f"{side}.Y"), basis
        )
        del Y_value
        Y_first = Y_first_raw[..., 0]
        tangent = torch.zeros(points.shape[0], 5, 4, dtype=DTYPE, device=free.device)
        tangent[:, :4, :] = torch.eye(4, dtype=DTYPE, device=free.device)[None, ...]
        tangent[:, 4, :] = Y_first
        induced = torch.einsum("pmi,pmn,pnj->pij", tangent, metric, tangent)

        R0, dR0 = rotation_and_tangential_derivatives(
            layout.get(free, f"{side}.r_E0"), basis
        )
        R = torch.einsum("pij,pjk->pik", common["S"], R0)
        dR = (
            torch.einsum("puij,pjk->puik", common["dS"], R0)
            + torch.einsum("pij,pujk->puik", common["S"], dR0)
        )
        phi_source = trace[..., 16:19]
        A_full = trace[..., 19:34].reshape(points.shape[0], 5, 3)
        A_pull = A_full[:, :4] + Y_first[:, :, None] * A_full[:, 4, None, :]
        A_transported_matrix = (
            torch.einsum(
                "pij,pujk,pkl->puil", R, _hat(A_pull), R.transpose(-1, -2)
            )
            - torch.einsum("puij,pjk->puik", dR, R.transpose(-1, -2))
        )
        residual = torch.cat(
            (
                _sym_to_vec(induced - common["gamma"], SYMMETRIC4),
                (
                    torch.exp(trace[..., 15]) - common["Omega"][..., 0]
                )[:, None],
                torch.einsum("pij,pj->pi", R, phi_source)
                - common["varphi_Q"],
                (_vee(A_transported_matrix) - common["A_Q"]).reshape(
                    points.shape[0], 12
                ),
            ),
            dim=-1,
        )
        if residual.shape != (points.shape[0], 26):
            raise LiteralTorchRouteError("pointwise side gluing width drift")
        side_residuals.append(residual)
    return torch.cat(side_residuals, dim=-1)


def periodic_t4_quadrature(order: int) -> tuple[torch.Tensor, torch.Tensor]:
    if isinstance(order, bool) or not isinstance(order, int) or order <= 0:
        raise LiteralTorchRouteError("periodic quadrature order must be positive")
    axis = 2.0 * math.pi * torch.arange(order, dtype=DTYPE) / float(order)
    points = torch.cartesian_prod(axis, axis, axis, axis)
    if points.ndim == 1:
        points = points[None, :]
    weights = torch.full(
        (points.shape[0],),
        (2.0 * math.pi / float(order)) ** 4,
        dtype=DTYPE,
    )
    return points, weights


def gauss_legendre_unit_interval(order: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Golub-Welsch Gauss-Legendre nodes/weights on the open interval (0,1)."""

    if isinstance(order, bool) or not isinstance(order, int) or order <= 0:
        raise LiteralTorchRouteError("radial quadrature order must be positive")
    jacobi = torch.zeros(order, order, dtype=DTYPE)
    if order > 1:
        index = torch.arange(1, order, dtype=DTYPE)
        off_diagonal = index / torch.sqrt(4.0 * index * index - 1.0)
        jacobi[torch.arange(order - 1), torch.arange(1, order)] = off_diagonal
        jacobi[torch.arange(1, order), torch.arange(order - 1)] = off_diagonal
    values, vectors = torch.linalg.eigh(jacobi)
    nodes = (values + 1.0) / 2.0
    weights = vectors[0] ** 2
    return nodes, weights


def radial_profile_evaluation(rho: torch.Tensor, K: int) -> dict[str, torch.Tensor]:
    """h0, h1 and compact Legendre-bump modes through second rho derivative."""

    _validate_N_K(1, K)
    if rho.ndim != 1 or bool(torch.any((rho <= 0.0) | (rho >= 1.0))):
        raise LiteralTorchRouteError("bulk radial nodes must lie strictly inside (0,1)")
    one_minus = 1.0 - rho
    exponent = -(rho / one_minus) ** 2
    exponent_first = -2.0 * rho / one_minus**3
    exponent_second = -2.0 * (1.0 + 2.0 * rho) / one_minus**4
    cutoff = torch.exp(exponent)
    cutoff_first = cutoff * exponent_first
    cutoff_second = cutoff * (exponent_first**2 + exponent_second)

    h0 = cutoff
    h0_first = cutoff_first
    h0_second = cutoff_second
    h1 = rho * cutoff
    h1_first = cutoff + rho * cutoff_first
    h1_second = 2.0 * cutoff_first + rho * cutoff_second

    u = rho * one_minus
    bump_exponent = 4.0 - 1.0 / u
    bump_log_first = (1.0 - 2.0 * rho) / u**2
    bump_log_second = -2.0 / u**2 - 2.0 * (1.0 - 2.0 * rho) ** 2 / u**3
    envelope = torch.exp(bump_exponent)
    envelope_first = envelope * bump_log_first
    envelope_second = envelope * (bump_log_first**2 + bump_log_second)
    coordinate = 2.0 * rho - 1.0

    polynomials: list[torch.Tensor] = [torch.ones_like(coordinate)]
    polynomial_first: list[torch.Tensor] = [torch.zeros_like(coordinate)]
    polynomial_second: list[torch.Tensor] = [torch.zeros_like(coordinate)]
    if K > 1:
        polynomials.append(coordinate)
        polynomial_first.append(torch.ones_like(coordinate))
        polynomial_second.append(torch.zeros_like(coordinate))
    for degree in range(2, K):
        scale = float(2 * degree - 1)
        previous = polynomials[-1]
        previous_first = polynomial_first[-1]
        previous_second = polynomial_second[-1]
        polynomials.append(
            (scale * coordinate * previous - float(degree - 1) * polynomials[-2])
            / float(degree)
        )
        polynomial_first.append(
            (
                scale * (previous + coordinate * previous_first)
                - float(degree - 1) * polynomial_first[-2]
            )
            / float(degree)
        )
        polynomial_second.append(
            (
                scale * (2.0 * previous_first + coordinate * previous_second)
                - float(degree - 1) * polynomial_second[-2]
            )
            / float(degree)
        )
    polynomial = torch.stack(polynomials, dim=-1)
    polynomial_rho = 2.0 * torch.stack(polynomial_first, dim=-1)
    polynomial_rhorho = 4.0 * torch.stack(polynomial_second, dim=-1)
    bumps = envelope[:, None] * polynomial
    bumps_first = envelope_first[:, None] * polynomial + envelope[:, None] * polynomial_rho
    bumps_second = (
        envelope_second[:, None] * polynomial
        + 2.0 * envelope_first[:, None] * polynomial_rho
        + envelope[:, None] * polynomial_rhorho
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


def _spectral_evaluate(
    coefficients: torch.Tensor, basis: Mapping[str, torch.Tensor]
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Evaluate arbitrary trailing channels and two exact T^4 derivatives."""

    if coefficients.ndim < 1:
        raise LiteralTorchRouteError("spectral coefficients need a mode axis")
    N = coefficients.shape[0]
    channels = math.prod(coefficients.shape[1:])
    flat = coefficients.reshape(N, channels)
    value = basis["values"] @ flat
    first = torch.einsum("pum,mc->puc", basis["first"], flat)
    second = torch.einsum("puvm,mc->puvc", basis["second"], flat)
    tail = coefficients.shape[1:]
    return (
        value.reshape((value.shape[0],) + tail),
        first.reshape((first.shape[0], 4) + tail),
        second.reshape((second.shape[0], 4, 4) + tail),
    )


def _common_first_trace_value_at_point(
    free: torch.Tensor,
    N: int,
    K: int,
    side: str,
    point: torch.Tensor,
) -> torch.Tensor:
    """Return the 64 eliminated side-trace primitives at one T4 point.

    The derivative of every SO(3) exponential is obtained from the exact
    Frechet block exponential in ``rotation_and_tangential_derivatives``.
    In particular, no ``R @ hat(d r)`` shortcut is used away from r=0.
    """

    if side not in SIDES:
        raise LiteralTorchRouteError(f"unknown side: {side}")
    if point.shape != (4,):
        raise LiteralTorchRouteError("pointwise decoder expects one T4 point")
    layout = free_layout(N, K)
    if free.ndim != 1 or free.numel() != layout.size:
        raise LiteralTorchRouteError("pointwise free-coordinate shape drift")
    basis = evaluate_real_fourier_basis(point[None, :], N)

    gamma_vector, _, _ = _spectral_evaluate(
        layout.get(free, "common.gamma"), basis
    )
    gamma = _vec_to_sym(gamma_vector, 4, SYMMETRIC4)
    log_Omega, _, _ = _spectral_evaluate(
        layout.get(free, "common.log_Omega"), basis
    )
    varphi_E0, _, _ = _spectral_evaluate(
        layout.get(free, "common.varphi_E0"), basis
    )
    A_E0, _, _ = _spectral_evaluate(layout.get(free, "common.A_E0"), basis)
    S, dS = rotation_and_tangential_derivatives(
        layout.get(free, "Q_frame.q"), basis
    )

    Y_value, Y_first_raw, _ = _spectral_evaluate(
        layout.get(free, f"{side}.Y"), basis
    )
    del Y_value
    Y_first = Y_first_raw[..., 0]
    metric_free, _, _ = _spectral_evaluate(
        layout.get(free, f"{side}.metric_free"), basis
    )
    adapted_cross = metric_free[..., :4]
    normal_metric = metric_free[..., 4]
    upper = (
        gamma
        - adapted_cross[:, :, None] * Y_first[:, None, :]
        - Y_first[:, :, None] * adapted_cross[:, None, :]
        + normal_metric[:, None, None]
        * Y_first[:, :, None]
        * Y_first[:, None, :]
    )
    ambient_cross = adapted_cross - normal_metric[:, None] * Y_first
    metric = torch.cat(
        (
            torch.cat((upper, ambient_cross[:, :, None]), dim=-1),
            torch.cat((ambient_cross, normal_metric[:, None]), dim=-1)[:, None, :],
        ),
        dim=-2,
    )

    R0, dR0 = rotation_and_tangential_derivatives(
        layout.get(free, f"{side}.r_E0"), basis
    )
    R = torch.einsum("pij,pjk->pik", S, R0)
    dR = (
        torch.einsum("puij,pjk->puik", dS, R0)
        + torch.einsum("pij,pujk->puik", S, dR0)
    )
    varphi_Q = torch.einsum("pij,pj->pi", S, varphi_E0)
    A_Q_matrix = (
        torch.einsum("pij,pujk,pkl->puil", S, _hat(A_E0), S.transpose(-1, -2))
        - torch.einsum("puij,pjk->puik", dS, S.transpose(-1, -2))
    )
    A_source_matrix = (
        torch.einsum(
            "pij,pujk,pkl->puil", R.transpose(-1, -2), A_Q_matrix, R
        )
        + torch.einsum("pij,pujk->puik", R.transpose(-1, -2), dR)
    )
    A_source = _vee(A_source_matrix)
    phi_source = torch.einsum("pji,pj->pi", R, varphi_Q)
    A_perp, _, _ = _spectral_evaluate(
        layout.get(free, f"{side}.A_perp"), basis
    )
    A_full = torch.cat(
        (
            A_source - Y_first[:, :, None] * A_perp[:, None, :],
            A_perp[:, None, :],
        ),
        dim=1,
    )
    B0, _, _ = _spectral_evaluate(
        layout.get(free, f"{side}.B0_full"), basis
    )
    trace = torch.cat(
        (
            _sym_to_vec(metric, SYMMETRIC5),
            log_Omega,
            phi_source,
            A_full.reshape(1, 15),
            B0.reshape(1, 30),
        ),
        dim=-1,
    )
    if trace.shape != (1, 64):
        raise LiteralTorchRouteError("pointwise eliminated trace width drift")
    return trace[0]


def common_first_trace_jets(
    free: torch.Tensor,
    N: int,
    K: int,
    side: str,
    points: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Eliminated trace values and exact first/second T4 derivatives.

    Differentiation is with respect to the evaluator-owned action nodes.  It
    therefore differentiates the nonlinear common-first formulas themselves,
    rather than differentiating an N-node interpolation of already-eliminated
    traces.  The outer free-coordinate AD/JVP remains active through these
    nested forward-mode derivatives.
    """

    if points.ndim != 2 or points.shape[1] != 4:
        raise LiteralTorchRouteError("pointwise trace points must have shape (P,4)")

    def value_at(point: torch.Tensor) -> torch.Tensor:
        return _common_first_trace_value_at_point(free, N, K, side, point)

    first_at = torch.func.jacfwd(value_at)
    second_at = torch.func.jacfwd(first_at)
    values = torch.func.vmap(value_at)(points)
    first_channels_last = torch.func.vmap(first_at)(points)
    second_channels_first = torch.func.vmap(second_at)(points)
    first = first_channels_last.permute(0, 2, 1)
    second = second_channels_first.permute(0, 2, 3, 1)
    if (
        values.shape != (points.shape[0], 64)
        or first.shape != (points.shape[0], 4, 64)
        or second.shape != (points.shape[0], 4, 4, 64)
    ):
        raise LiteralTorchRouteError("pointwise trace jet shape drift")
    return values, first, second


def pointwise_common_fields(
    free: torch.Tensor,
    N: int,
    K: int,
    points: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """Decode common B_N data and Q-frame transport at arbitrary T4 nodes."""

    layout = free_layout(N, K)
    if free.ndim != 1 or free.numel() != layout.size:
        raise LiteralTorchRouteError("common pointwise free-coordinate shape drift")
    basis = evaluate_real_fourier_basis(points, N)
    gamma_vector, gamma_first_vector, gamma_second_vector = _spectral_evaluate(
        layout.get(free, "common.gamma"), basis
    )
    gamma = _vec_to_sym(gamma_vector, 4, SYMMETRIC4)
    gamma_first = _vec_to_sym(gamma_first_vector, 4, SYMMETRIC4)
    gamma_second = _vec_to_sym(gamma_second_vector, 4, SYMMETRIC4)
    T, T_first, T_second = _spectral_evaluate(
        layout.get(free, "common.T"), basis
    )
    log_Omega, log_Omega_first, log_Omega_second = _spectral_evaluate(
        layout.get(free, "common.log_Omega"), basis
    )
    varphi_E0, _, _ = _spectral_evaluate(
        layout.get(free, "common.varphi_E0"), basis
    )
    A_E0, _, _ = _spectral_evaluate(layout.get(free, "common.A_E0"), basis)
    S, dS = rotation_and_tangential_derivatives(
        layout.get(free, "Q_frame.q"), basis
    )
    varphi_Q = torch.einsum("pij,pj->pi", S, varphi_E0)
    A_Q_matrix = (
        torch.einsum("pij,pujk,pkl->puil", S, _hat(A_E0), S.transpose(-1, -2))
        - torch.einsum("puij,pjk->puik", dS, S.transpose(-1, -2))
    )
    return {
        "basis_values": basis["values"],
        "gamma": gamma,
        "gamma_first": gamma_first,
        "gamma_second": gamma_second,
        "T": T,
        "T_first": T_first,
        "T_second": T_second,
        "log_Omega": log_Omega,
        "log_Omega_first": log_Omega_first,
        "log_Omega_second": log_Omega_second,
        "Omega": torch.exp(log_Omega),
        "varphi_E0": varphi_E0,
        "varphi_Q": varphi_Q,
        "A_E0": A_E0,
        "A_Q": _vee(A_Q_matrix),
        "S": S,
        "dS": dS,
    }


def _radial_expand_flat(
    trace: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    jet: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    interior: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    reference: torch.Tensor,
    profiles: Mapping[str, torch.Tensor],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Tensor-product expansion in adapted (x^mu,rho) coordinates."""

    trace_value, trace_first, trace_second = trace
    jet_value, jet_first, jet_second = jet
    interior_value, interior_first, interior_second = interior
    P, channels = trace_value.shape
    if jet_value.shape != (P, channels):
        raise LiteralTorchRouteError("boundary-jet channel shape drift")
    if interior_value.ndim != 3 or interior_value.shape[0] != P or interior_value.shape[2] != channels:
        raise LiteralTorchRouteError("interior-mode channel shape drift")
    K = interior_value.shape[1]
    if profiles["bumps"].shape[1] != K or reference.shape != (channels,):
        raise LiteralTorchRouteError("radial expansion contract drift")

    h0 = profiles["h0"][:, None, None]
    h1 = profiles["h1"][:, None, None]
    h0p = profiles["h0_first"][:, None, None]
    h1p = profiles["h1_first"][:, None, None]
    h0pp = profiles["h0_second"][:, None, None]
    h1pp = profiles["h1_second"][:, None, None]
    reference_broadcast = reference[None, None, :]
    trace_delta = trace_value - reference[None, :]

    value = (
        reference_broadcast
        + h0 * trace_delta[None, ...]
        + h1 * jet_value[None, ...]
        + torch.einsum("rk,pkc->rpc", profiles["bumps"], interior_value)
    )
    tangent_first = (
        h0[:, :, None, :] * trace_first[None, ...]
        + h1[:, :, None, :] * jet_first[None, ...]
        + torch.einsum("rk,pukc->rpuc", profiles["bumps"], interior_first)
    )
    radial_first = (
        h0p * trace_delta[None, ...]
        + h1p * jet_value[None, ...]
        + torch.einsum("rk,pkc->rpc", profiles["bumps_first"], interior_value)
    )
    first = torch.cat((tangent_first, radial_first[:, :, None, :]), dim=2)

    tangent_second = (
        h0[:, :, None, None, :] * trace_second[None, ...]
        + h1[:, :, None, None, :] * jet_second[None, ...]
        + torch.einsum("rk,puvkc->rpuvc", profiles["bumps"], interior_second)
    )
    mixed = (
        h0p[:, :, None, :] * trace_first[None, ...]
        + h1p[:, :, None, :] * jet_first[None, ...]
        + torch.einsum("rk,pukc->rpuc", profiles["bumps_first"], interior_first)
    )
    radial_second = (
        h0pp * trace_delta[None, ...]
        + h1pp * jet_value[None, ...]
        + torch.einsum("rk,pkc->rpc", profiles["bumps_second"], interior_value)
    )
    top = torch.cat((tangent_second, mixed[:, :, :, None, :]), dim=3)
    bottom = torch.cat((mixed, radial_second[:, :, None, :]), dim=2)[:, :, None, :, :]
    second = torch.cat((top, bottom), dim=2)
    return value, first, second


def _expanded_field(
    trace_coefficients: torch.Tensor,
    jet_coefficients: torch.Tensor,
    interior_coefficients: torch.Tensor,
    reference: torch.Tensor,
    basis: Mapping[str, torch.Tensor],
    profiles: Mapping[str, torch.Tensor],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Preserve field tensor axes around the flat radial-expansion kernel."""

    tail = trace_coefficients.shape[1:]
    channels = math.prod(tail)
    trace_raw = _spectral_evaluate(trace_coefficients.reshape(trace_coefficients.shape[0], channels), basis)
    jet_raw = _spectral_evaluate(jet_coefficients.reshape(jet_coefficients.shape[0], channels), basis)
    interior_raw = _spectral_evaluate(
        interior_coefficients.reshape(
            interior_coefficients.shape[0], interior_coefficients.shape[1], channels
        ),
        basis,
    )
    value, first, second = _radial_expand_flat(
        trace_raw,
        jet_raw,
        interior_raw,
        reference.reshape(channels),
        profiles,
    )
    R, P = value.shape[:2]
    return (
        value.reshape((R, P) + tail),
        first.reshape((R, P, 5) + tail),
        second.reshape((R, P, 5, 5) + tail),
    )


def _adapted_to_ambient_derivatives(
    first: torch.Tensor,
    second: torch.Tensor,
    Y_first: torch.Tensor,
    Y_second: torch.Tensor,
    side: str,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Convert derivatives from (x,rho) to fixed ambient (x,y4)."""

    if side not in SIDES:
        raise LiteralTorchRouteError(f"unknown side: {side}")
    R, P = first.shape[:2]
    tail = first.shape[3:]
    channels = math.prod(tail)
    first_flat = first.reshape(R, P, 5, channels)
    second_flat = second.reshape(R, P, 5, 5, channels)
    sign = SIDE_RADIAL_SIGN[side]
    identity = torch.eye(5, dtype=DTYPE, device=first.device)
    rows: list[torch.Tensor] = []
    for mu in range(4):
        rows.append(
            torch.cat(
                (
                    identity[mu, :4].expand(P, 4),
                    (-sign * Y_first[:, mu])[:, None],
                ),
                dim=-1,
            )
        )
    rows.append(
        torch.cat(
            (
                torch.zeros(P, 4, dtype=DTYPE, device=first.device),
                torch.full((P, 1), sign, dtype=DTYPE, device=first.device),
            ),
            dim=-1,
        )
    )
    transform = torch.stack(rows, dim=1)
    ambient_first = torch.einsum("pma,rpac->rpmc", transform, first_flat)
    ambient_second = torch.einsum(
        "pma,pnb,rpabc->rpmnc", transform, transform, second_flat
    )
    correction = torch.zeros(P, 5, 5, dtype=DTYPE, device=first.device)
    correction[:, :4, :4] = -sign * Y_second
    ambient_second = ambient_second + correction[None, :, :, :, None] * first_flat[:, :, 4, None, None, :]
    return (
        ambient_first.reshape((R, P, 5) + tail),
        ambient_second.reshape((R, P, 5, 5) + tail),
    )


def decode_bulk_primitives(
    q_retracted: torch.Tensor,
    N: int,
    K: int,
    side: str,
    tangential_points: torch.Tensor,
    rho: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """Reconstruct raw fields and ambient derivatives; no upstream samples are read."""

    if side not in SIDES:
        raise LiteralTorchRouteError(f"unknown side: {side}")
    layout = ambient_layout(N, K)
    basis = evaluate_real_fourier_basis(tangential_points, N)
    profiles = radial_profile_evaluation(rho, K)
    Y_coeff = layout.get(q_retracted, f"{side}.Y")
    Y_value, Y_first_raw, Y_second_raw = _spectral_evaluate(Y_coeff, basis)
    Y = Y_value[..., 0]
    Y_first = Y_first_raw[..., 0]
    Y_second = Y_second_raw[..., 0]

    J = layout.get(q_retracted, f"{side}.boundary_jet_J1")
    C = layout.get(q_retracted, f"{side}.interior_bump_C")
    g_trace = _vec_to_sym(layout.get(q_retracted, f"{side}.g_trace"), 5, SYMMETRIC5)
    g_jet = _vec_to_sym(J[:, :15], 5, SYMMETRIC5)
    g_interior = _vec_to_sym(C[:, :, :15], 5, SYMMETRIC5)
    reference_metric = torch.diag(
        torch.tensor((-1.64, 1.17, 1.31, 1.46, 1.17), dtype=DTYPE)
    )

    field_specs = {
        "g": (g_trace, g_jet, g_interior, reference_metric),
        "log_Omega": (
            layout.get(q_retracted, f"{side}.log_Omega_trace"),
            J[:, 15:16],
            C[:, :, 15:16],
            torch.zeros(1, dtype=DTYPE),
        ),
        "phi": (
            layout.get(q_retracted, f"{side}.phi_trace"),
            J[:, 16:19],
            C[:, :, 16:19],
            torch.zeros(3, dtype=DTYPE),
        ),
        "A": (
            layout.get(q_retracted, f"{side}.A_trace_full"),
            J[:, 19:34].reshape(N, 5, 3),
            C[:, :, 19:34].reshape(N, K, 5, 3),
            torch.zeros(5, 3, dtype=DTYPE),
        ),
        "B": (
            layout.get(q_retracted, f"{side}.B_trace_full"),
            J[:, 34:64].reshape(N, 10, 3),
            C[:, :, 34:64].reshape(N, K, 10, 3),
            torch.zeros(10, 3, dtype=DTYPE),
        ),
    }
    result: dict[str, torch.Tensor] = {
        "Y": Y,
        "Y_first": Y_first,
        "Y_second": Y_second,
    }
    for name, (trace, jet, interior, reference) in field_specs.items():
        value, first_adapted, second_adapted = _expanded_field(
            trace, jet, interior, reference, basis, profiles
        )
        first_ambient, second_ambient = _adapted_to_ambient_derivatives(
            first_adapted, second_adapted, Y_first, Y_second, side
        )
        result[name] = value
        result[f"d_{name}"] = first_ambient
        result[f"dd_{name}"] = second_ambient
    result["Omega"] = torch.exp(result["log_Omega"])
    result["d_Omega"] = result["Omega"][..., None, :] * result["d_log_Omega"]
    return result


def decode_free_bulk_primitives(
    free: torch.Tensor,
    N: int,
    K: int,
    side: str,
    tangential_points: torch.Tensor,
    rho: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """Pointwise common-first bulk decoder for authoritative free coordinates."""

    if side not in SIDES:
        raise LiteralTorchRouteError(f"unknown side: {side}")
    layout = free_layout(N, K)
    if free.ndim != 1 or free.numel() != layout.size:
        raise LiteralTorchRouteError("free bulk-coordinate shape drift")
    basis = evaluate_real_fourier_basis(tangential_points, N)
    profiles = radial_profile_evaluation(rho, K)
    trace = common_first_trace_jets(free, N, K, side, tangential_points)
    jet = _spectral_evaluate(
        layout.get(free, f"{side}.boundary_jet_J1"), basis
    )
    interior = _spectral_evaluate(
        layout.get(free, f"{side}.interior_bump_C"), basis
    )
    reference_metric = torch.diag(
        torch.tensor((-1.64, 1.17, 1.31, 1.46, 1.17), dtype=DTYPE)
    )
    reference = torch.cat(
        (
            _sym_to_vec(reference_metric, SYMMETRIC5),
            torch.zeros(49, dtype=DTYPE, device=free.device),
        )
    )
    value, first_adapted, second_adapted = _radial_expand_flat(
        trace, jet, interior, reference, profiles
    )

    Y_value, Y_first_raw, Y_second_raw = _spectral_evaluate(
        layout.get(free, f"{side}.Y"), basis
    )
    Y = Y_value[..., 0]
    Y_first = Y_first_raw[..., 0]
    Y_second = Y_second_raw[..., 0]
    first, second = _adapted_to_ambient_derivatives(
        first_adapted, second_adapted, Y_first, Y_second, side
    )

    result: dict[str, torch.Tensor] = {
        "Y": Y,
        "Y_first": Y_first,
        "Y_second": Y_second,
        "g": _vec_to_sym(value[..., :15], 5, SYMMETRIC5),
        "d_g": _vec_to_sym(first[..., :15], 5, SYMMETRIC5),
        "dd_g": _vec_to_sym(second[..., :15], 5, SYMMETRIC5),
        "log_Omega": value[..., 15:16],
        "d_log_Omega": first[..., 15:16],
        "dd_log_Omega": second[..., 15:16],
        "phi": value[..., 16:19],
        "d_phi": first[..., 16:19],
        "dd_phi": second[..., 16:19],
        "A": value[..., 19:34].reshape(
            value.shape[:2] + (5, 3)
        ),
        "d_A": first[..., 19:34].reshape(
            first.shape[:3] + (5, 3)
        ),
        "dd_A": second[..., 19:34].reshape(
            second.shape[:4] + (5, 3)
        ),
        "B": value[..., 34:64].reshape(
            value.shape[:2] + (10, 3)
        ),
        "d_B": first[..., 34:64].reshape(
            first.shape[:3] + (10, 3)
        ),
        "dd_B": second[..., 34:64].reshape(
            second.shape[:4] + (10, 3)
        ),
    }
    result["Omega"] = torch.exp(result["log_Omega"])
    result["d_Omega"] = result["Omega"][..., None, :] * result["d_log_Omega"]
    result["dd_Omega"] = result["Omega"][..., None, None, :] * (
        result["dd_log_Omega"]
        + result["d_log_Omega"][..., :, None, :]
        * result["d_log_Omega"][..., None, :, :]
    )
    return result


def metric_geometry(
    metric: torch.Tensor,
    first: torch.Tensor,
    second: torch.Tensor | None = None,
    *,
    include_riemann: bool = False,
) -> dict[str, torch.Tensor]:
    """Levi-Civita connection and curvature for arbitrary leading batch axes."""

    dimension = metric.shape[-1]
    if metric.shape[-2:] != (dimension, dimension):
        raise LiteralTorchRouteError("metric must be square")
    if first.shape != metric.shape[:-2] + (dimension, dimension, dimension):
        raise LiteralTorchRouteError("metric first-derivative shape drift")
    inverse = torch.linalg.inv(metric)
    determinant = torch.linalg.det(metric)
    derivative_inverse = -torch.einsum(
        "...ka,...pab,...bl->...pkl", inverse, first, inverse
    )
    christoffel_seed = (
        torch.einsum("...mln->...lmn", first)
        + torch.einsum("...nlm->...lmn", first)
        - first
    )
    christoffel = 0.5 * torch.einsum(
        "...kl,...lmn->...kmn", inverse, christoffel_seed
    )
    result = {
        "inverse": inverse,
        "determinant": determinant,
        "sqrt_abs_determinant": torch.sqrt(torch.abs(determinant)),
        "derivative_inverse": derivative_inverse,
        "christoffel": christoffel,
    }
    if second is None:
        return result
    expected_second = metric.shape[:-2] + (
        dimension,
        dimension,
        dimension,
        dimension,
    )
    if second.shape != expected_second:
        raise LiteralTorchRouteError("metric second-derivative shape drift")
    derivative_seed = (
        torch.einsum("...pmln->...plmn", second)
        + torch.einsum("...pnlm->...plmn", second)
        - second
    )
    derivative_christoffel = 0.5 * (
        torch.einsum(
            "...pkl,...lmn->...pkmn", derivative_inverse, christoffel_seed
        )
        + torch.einsum("...kl,...plmn->...pkmn", inverse, derivative_seed)
    )
    ricci = (
        torch.einsum("...kkmn->...mn", derivative_christoffel)
        - torch.einsum("...nkmk->...mn", derivative_christoffel)
        + torch.einsum("...kkl,...lmn->...mn", christoffel, christoffel)
        - torch.einsum("...knl,...lmk->...mn", christoffel, christoffel)
    )
    scalar = torch.einsum("...mn,...mn->...", inverse, ricci)
    result.update(
        {
            "derivative_christoffel": derivative_christoffel,
            "ricci": ricci,
            "scalar_curvature": scalar,
        }
    )
    if include_riemann:
        riemann_upper = (
            torch.einsum("...mrns->...rsmn", derivative_christoffel)
            - torch.einsum("...nrms->...rsmn", derivative_christoffel)
            + torch.einsum("...rml,...lns->...rsmn", christoffel, christoffel)
            - torch.einsum("...rnl,...lms->...rsmn", christoffel, christoffel)
        )
        riemann_lower = torch.einsum(
            "...ar,...rsmn->...asmn", metric, riemann_upper
        )
        result["riemann_upper"] = riemann_upper
        result["riemann_lower"] = riemann_lower
    return result


def _integrate_bulk(density: torch.Tensor, radial_weights: torch.Tensor, tangential_weights: torch.Tensor) -> torch.Tensor:
    if density.shape != (radial_weights.numel(), tangential_weights.numel()):
        raise LiteralTorchRouteError("bulk density/quadrature shape drift")
    return torch.einsum("r,p,rp->", radial_weights, tangential_weights, density)


def _integrate_brane(density: torch.Tensor, tangential_weights: torch.Tensor) -> torch.Tensor:
    if density.shape != (tangential_weights.numel(),):
        raise LiteralTorchRouteError("brane density/quadrature shape drift")
    return torch.dot(tangential_weights, density)


def bulk_component_densities(
    primitives: Mapping[str, torch.Tensor],
    side: str,
    *,
    connection_cross_sign: float = 1.0,
) -> dict[str, torch.Tensor]:
    """Six literal bulk atoms on one side, before numerical integration."""

    if side not in SIDES:
        raise LiteralTorchRouteError(f"unknown side: {side}")
    if connection_cross_sign not in (-1.0, 1.0):
        raise LiteralTorchRouteError("connection cross sign must be +/-1")
    geometry = metric_geometry(primitives["g"], primitives["d_g"], primitives["dd_g"])
    inverse = geometry["inverse"]
    volume = geometry["sqrt_abs_determinant"]
    scalar_curvature = geometry["scalar_curvature"]
    Omega = primitives["Omega"][..., 0]
    dOmega = primitives["d_Omega"][..., 0]
    dlog = primitives["d_log_Omega"][..., 0]
    phi = primitives["phi"]
    dphi = primitives["d_phi"]
    connection = primitives["A"]
    dconnection = primitives["d_A"]

    Omega_squared_gradient = torch.einsum(
        "...mn,...m,...n->...", inverse, dOmega, dOmega
    )
    covariant_phi = (
        dphi
        + connection_cross_sign * _cross(connection, phi[..., None, :])
        + 1.5 * phi[..., None, :] * dlog[..., :, None]
    )
    P_squared = torch.einsum(
        "...mn,...ma,...na->...", inverse, covariant_phi, covariant_phi
    )

    M5_cubed = COEFFICIENTS["M5_cubed"]
    G = COEFFICIENTS["compensator_metric_G"]
    k_infinity = COEFFICIENTS["k_infinity"]
    Z5 = COEFFICIENTS["material_Z5_per_side"]
    material_mass = COEFFICIENTS["material_mass_M"]
    W = 3.0 * M5_cubed * k_infinity * torch.exp(
        -G * Omega * Omega / (6.0 * M5_cubed)
    )
    W_Omega = -G * Omega * W / (3.0 * M5_cubed)
    U = W_Omega * W_Omega / (2.0 * G) - 2.0 * W * W / (3.0 * M5_cubed)
    phi_norm = torch.linalg.vector_norm(phi, dim=-1)
    radial_matter = Omega**1.5 * phi_norm
    V4 = radial_matter**4 / (2.0 * torch.sqrt(1.0 + radial_matter**4))

    curvature = (
        dconnection - dconnection.transpose(-3, -2)
        + connection_cross_sign
        * _cross(connection[..., :, None, :], connection[..., None, :, :])
    )
    BF_density = torch.zeros_like(Omega)
    all_indices = set(range(5))
    for triple_index, triple in enumerate(B_TRIPLES):
        complement = tuple(sorted(all_indices - set(triple)))
        sign = float(_permutation_sign(triple + complement))
        BF_density = BF_density + sign * torch.sum(
            primitives["B"][..., triple_index, :] * curvature[..., complement[0], complement[1], :],
            dim=-1,
        )

    return {
        "EH": volume * M5_cubed * scalar_curvature / 2.0,
        "Omega_kinetic": -volume * G * Omega_squared_gradient / 2.0,
        "Omega_potential": -volume * U,
        "P_kinetic": -volume * Z5 * P_squared / 2.0,
        "full_V4": -volume * Z5 * material_mass**2 * Omega**-5.0 * V4,
        # B and F above carry ambient indices.  Pulling the top form into the
        # declared positive (x,rho_epsilon) chart contributes det J=s_epsilon.
        "BF": SIDE_RADIAL_SIGN[side] * BF_density,
    }


def interface_ghy_density(
    q_retracted: torch.Tensor,
    N: int,
    K: int,
    side: str,
    tangential_points: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """GHY density from the graph, side trace, radial jet, and outward normal."""

    if side not in SIDES:
        raise LiteralTorchRouteError(f"unknown side: {side}")
    layout = ambient_layout(N, K)
    basis = evaluate_real_fourier_basis(tangential_points, N)
    Y_value, Y_first_raw, Y_second_raw = _spectral_evaluate(
        layout.get(q_retracted, f"{side}.Y"), basis
    )
    Y_first = Y_first_raw[..., 0]
    Y_second = Y_second_raw[..., 0]
    metric_coefficients = _vec_to_sym(
        layout.get(q_retracted, f"{side}.g_trace"), 5, SYMMETRIC5
    )
    metric, metric_tangent_first, _ = _spectral_evaluate(metric_coefficients, basis)
    jet_coefficients = _vec_to_sym(
        layout.get(q_retracted, f"{side}.boundary_jet_J1")[:, :15],
        5,
        SYMMETRIC5,
    )
    metric_radial_first, _, _ = _spectral_evaluate(jet_coefficients, basis)
    first_adapted = torch.cat(
        (metric_tangent_first, metric_radial_first[:, None, :, :]), dim=1
    )[None, ...]
    second_dummy = torch.zeros(
        (1, tangential_points.shape[0], 5, 5, 5, 5),
        dtype=DTYPE,
        device=q_retracted.device,
    )
    metric_ambient_first, _ = _adapted_to_ambient_derivatives(
        first_adapted, second_dummy, Y_first, Y_second, side
    )
    metric_ambient_first = metric_ambient_first[0]
    geometry = metric_geometry(metric, metric_ambient_first)
    inverse = geometry["inverse"]
    christoffel = geometry["christoffel"]

    P = tangential_points.shape[0]
    tangent = torch.zeros(P, 5, 4, dtype=DTYPE, device=q_retracted.device)
    tangent[:, :4, :] = torch.eye(4, dtype=DTYPE, device=q_retracted.device)[None, ...]
    tangent[:, 4, :] = Y_first
    induced = torch.einsum("pmi,pmn,pnj->pij", tangent, metric, tangent)
    induced_inverse = torch.linalg.inv(induced)

    raw_normal = torch.cat((-Y_first, torch.ones(P, 1, dtype=DTYPE)), dim=-1)
    raw_norm_squared = torch.einsum(
        "pm,pmn,pn->p", raw_normal, inverse, raw_normal
    )
    outward_sign = SIDE_OUTWARD_SIGN[side]
    normal_covector = outward_sign * raw_normal / torch.sqrt(raw_norm_squared)[:, None]
    normal_vector = torch.einsum("pmn,pn->pm", inverse, normal_covector)
    orientation_matrix = torch.cat((tangent, normal_vector[:, :, None]), dim=-1)

    raw_normal_derivative = torch.cat(
        (-Y_second, torch.zeros(P, 4, 1, dtype=DTYPE)), dim=-1
    )
    inverse_tangent_derivative = -torch.einsum(
        "pma,puab,pbn->pumn", inverse, metric_tangent_first, inverse
    )
    norm_squared_derivative = (
        2.0
        * torch.einsum(
            "pum,pmn,pn->pu", raw_normal_derivative, inverse, raw_normal
        )
        + torch.einsum(
            "pm,pumn,pn->pu", raw_normal, inverse_tangent_derivative, raw_normal
        )
    )
    normal_tangent_derivative = outward_sign * (
        raw_normal_derivative / torch.sqrt(raw_norm_squared)[:, None, None]
        - raw_normal[:, None, :]
        * norm_squared_derivative[:, :, None]
        / (2.0 * raw_norm_squared[:, None, None] ** 1.5)
    )
    connection_pull = torch.einsum(
        "pmi,pkmn,pk->pin", tangent, christoffel, normal_covector
    )
    covariant_normal = normal_tangent_derivative - connection_pull
    extrinsic = torch.einsum("pin,pnj->pij", covariant_normal, tangent)
    theta = torch.einsum("pij,pij->p", induced_inverse, extrinsic)
    density = (
        COEFFICIENTS["M5_cubed"]
        * torch.sqrt(torch.abs(torch.linalg.det(induced)))
        * theta
    )
    return {
        "density": density,
        "Theta": theta,
        "induced_metric": induced,
        "normal_covector": normal_covector,
        "normal_vector": normal_vector,
        "boundary_orientation_determinant": torch.linalg.det(orientation_matrix),
        "normal_norm_squared": torch.einsum(
            "pm,pmn,pn->p", normal_covector, inverse, normal_covector
        ),
        "Y": Y_value[..., 0],
    }


def interface_free_ghy_density(
    free: torch.Tensor,
    N: int,
    K: int,
    side: str,
    tangential_points: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """Pointwise GHY density from free coordinates and the exact trace lift."""

    if side not in SIDES:
        raise LiteralTorchRouteError(f"unknown side: {side}")
    layout = free_layout(N, K)
    basis = evaluate_real_fourier_basis(tangential_points, N)
    trace_value, trace_first, _ = common_first_trace_jets(
        free, N, K, side, tangential_points
    )
    metric = _vec_to_sym(trace_value[..., :15], 5, SYMMETRIC5)
    metric_tangent_first = _vec_to_sym(
        trace_first[..., :15], 5, SYMMETRIC5
    )
    jet, _, _ = _spectral_evaluate(
        layout.get(free, f"{side}.boundary_jet_J1"), basis
    )
    metric_radial_first = _vec_to_sym(jet[..., :15], 5, SYMMETRIC5)
    Y_value, Y_first_raw, Y_second_raw = _spectral_evaluate(
        layout.get(free, f"{side}.Y"), basis
    )
    Y_first = Y_first_raw[..., 0]
    Y_second = Y_second_raw[..., 0]

    first_adapted = torch.cat(
        (metric_tangent_first, metric_radial_first[:, None, :, :]), dim=1
    )[None, ...]
    second_dummy = torch.zeros(
        (1, tangential_points.shape[0], 5, 5, 5, 5),
        dtype=DTYPE,
        device=free.device,
    )
    metric_ambient_first, _ = _adapted_to_ambient_derivatives(
        first_adapted, second_dummy, Y_first, Y_second, side
    )
    metric_ambient_first = metric_ambient_first[0]
    geometry = metric_geometry(metric, metric_ambient_first)
    inverse = geometry["inverse"]
    christoffel = geometry["christoffel"]

    P = tangential_points.shape[0]
    tangent = torch.zeros(P, 5, 4, dtype=DTYPE, device=free.device)
    tangent[:, :4, :] = torch.eye(4, dtype=DTYPE, device=free.device)[None, ...]
    tangent[:, 4, :] = Y_first
    induced = torch.einsum("pmi,pmn,pnj->pij", tangent, metric, tangent)
    induced_inverse = torch.linalg.inv(induced)

    raw_normal = torch.cat(
        (-Y_first, torch.ones(P, 1, dtype=DTYPE, device=free.device)), dim=-1
    )
    raw_norm_squared = torch.einsum("pm,pmn,pn->p", raw_normal, inverse, raw_normal)
    outward_sign = SIDE_OUTWARD_SIGN[side]
    normal_covector = outward_sign * raw_normal / torch.sqrt(raw_norm_squared)[:, None]
    normal_vector = torch.einsum("pmn,pn->pm", inverse, normal_covector)
    orientation_matrix = torch.cat((tangent, normal_vector[:, :, None]), dim=-1)
    raw_normal_derivative = torch.cat(
        (-Y_second, torch.zeros(P, 4, 1, dtype=DTYPE, device=free.device)), dim=-1
    )
    inverse_tangent_derivative = -torch.einsum(
        "pma,puab,pbn->pumn", inverse, metric_tangent_first, inverse
    )
    norm_squared_derivative = (
        2.0
        * torch.einsum(
            "pum,pmn,pn->pu", raw_normal_derivative, inverse, raw_normal
        )
        + torch.einsum(
            "pm,pumn,pn->pu", raw_normal, inverse_tangent_derivative, raw_normal
        )
    )
    normal_tangent_derivative = outward_sign * (
        raw_normal_derivative / torch.sqrt(raw_norm_squared)[:, None, None]
        - raw_normal[:, None, :]
        * norm_squared_derivative[:, :, None]
        / (2.0 * raw_norm_squared[:, None, None] ** 1.5)
    )
    connection_pull = torch.einsum(
        "pmi,pkmn,pk->pin", tangent, christoffel, normal_covector
    )
    covariant_normal = normal_tangent_derivative - connection_pull
    extrinsic = torch.einsum("pin,pnj->pij", covariant_normal, tangent)
    theta = torch.einsum("pij,pij->p", induced_inverse, extrinsic)
    density = (
        COEFFICIENTS["M5_cubed"]
        * torch.sqrt(torch.abs(torch.linalg.det(induced)))
        * theta
    )
    return {
        "density": density,
        "Theta": theta,
        "induced_metric": induced,
        "normal_covector": normal_covector,
        "normal_vector": normal_vector,
        "boundary_orientation_determinant": torch.linalg.det(orientation_matrix),
        "normal_norm_squared": torch.einsum(
            "pm,pmn,pn->p", normal_covector, inverse, normal_covector
        ),
        "Y": Y_value[..., 0],
    }


def _ordered_spatial_frame(
    gamma: torch.Tensor, u_covector: torch.Tensor, u_vector: torch.Tensor
) -> torch.Tensor:
    """Ordered gamma-Gram-Schmidt frame E0 specified by the primitive contract."""

    P = gamma.shape[0]
    columns: list[torch.Tensor] = []
    for column in range(3):
        seed = torch.zeros(P, 4, dtype=DTYPE, device=gamma.device)
        seed[:, column + 1] = 1.0
        candidate = seed + u_vector * u_covector[:, column + 1, None]
        for previous in columns:
            projection = torch.einsum("pi,pij,pj->p", previous, gamma, candidate)
            candidate = candidate - projection[:, None] * previous
        length = torch.sqrt(torch.einsum("pi,pij,pj->p", candidate, gamma, candidate))
        columns.append(candidate / length[:, None])
    return torch.stack(columns, dim=-1)


def foliation_geometry_from_primitives(
    gamma: torch.Tensor,
    gamma_first: torch.Tensor,
    gamma_second: torch.Tensor,
    tau_gradient: torch.Tensor,
    tau_hessian: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """Derived khronon geometry with the frozen contracted-Gauss convention."""

    geometry = metric_geometry(
        gamma, gamma_first, gamma_second, include_riemann=True
    )
    inverse = geometry["inverse"]
    christoffel = geometry["christoffel"]
    tau_norm_squared = torch.einsum(
        "pij,pi,pj->p", inverse, tau_gradient, tau_gradient
    )
    normalization = torch.sqrt(-tau_norm_squared)
    u_covector = -tau_gradient / normalization[:, None]
    u_vector = torch.einsum("pij,pj->pi", inverse, u_covector)
    derivative_tau_norm_squared = (
        torch.einsum(
            "puij,pi,pj->pu",
            geometry["derivative_inverse"],
            tau_gradient,
            tau_gradient,
        )
        + 2.0
        * torch.einsum("pij,pui,pj->pu", inverse, tau_hessian, tau_gradient)
    )
    derivative_normalization = -derivative_tau_norm_squared / (
        2.0 * normalization[:, None]
    )
    derivative_u_covector = (
        -tau_hessian / normalization[:, None, None]
        + tau_gradient[:, None, :]
        * derivative_normalization[:, :, None]
        / normalization[:, None, None] ** 2
    )
    covariant_u = derivative_u_covector - torch.einsum(
        "pkij,pk->pij", christoffel, u_covector
    )
    projector_covariant = gamma + u_covector[:, :, None] * u_covector[:, None, :]
    projector_contravariant = inverse + u_vector[:, :, None] * u_vector[:, None, :]
    projector_mixed = (
        torch.eye(4, dtype=DTYPE, device=gamma.device)[None, ...]
        + u_covector[:, :, None] * u_vector[:, None, :]
    )
    Kcal = torch.einsum(
        "pma,pnb,pab->pmn", projector_mixed, projector_mixed, covariant_u
    )
    Ktrace = torch.einsum("pmn,pmn->p", projector_contravariant, Kcal)
    K_squared = torch.einsum(
        "pmr,pns,pmn,prs->p",
        projector_contravariant,
        projector_contravariant,
        Kcal,
        Kcal,
    )
    acceleration_covector = torch.einsum("pa,pan->pn", u_vector, covariant_u)
    acceleration_squared = torch.einsum(
        "pmn,pm,pn->p", inverse, acceleration_covector, acceleration_covector
    )
    projected_riemann = torch.einsum(
        "pam,psn,pasmn->p",
        projector_contravariant,
        projector_contravariant,
        geometry["riemann_lower"],
    )
    # Contracted Gauss equation for signature (-,+,+,+),
    # K_ab=h_a^c h_b^d nabla_c u_d and the Riemann convention implemented by
    # metric_geometry.  The opposite sign printed in v5.5.4 is quarantined:
    # it fails the flat-spatial FLRW witness while this convention also gives
    # Rcal=+6/a^2 on a static round S3.
    Rcal = projected_riemann + K_squared - Ktrace * Ktrace
    return {
        **geometry,
        "tau_norm_squared": tau_norm_squared,
        "u_covector": u_covector,
        "u_vector": u_vector,
        "projector_covariant": projector_covariant,
        "projector_contravariant": projector_contravariant,
        "Kcal": Kcal,
        "Ktrace": Ktrace,
        "K_squared": K_squared,
        "acceleration_covector": acceleration_covector,
        "acceleration_squared": acceleration_squared,
        "projected_riemann": projected_riemann,
        "Rcal": Rcal,
    }


def brane_component_densities(
    q_retracted: torch.Tensor,
    N: int,
    K: int,
    tangential_points: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """Six shared-interface atoms from gamma, tau_T, Q-frame, Omega and varphi."""

    layout = ambient_layout(N, K)
    basis = evaluate_real_fourier_basis(tangential_points, N)

    gamma_coefficients = layout.get(q_retracted, "common.gamma")
    gamma_vector, gamma_first_vector, gamma_second_vector = _spectral_evaluate(
        gamma_coefficients, basis
    )
    gamma = _vec_to_sym(gamma_vector, 4, SYMMETRIC4)
    gamma_first = _vec_to_sym(gamma_first_vector, 4, SYMMETRIC4)
    gamma_second = _vec_to_sym(gamma_second_vector, 4, SYMMETRIC4)
    _, T_first_raw, T_second_raw = _spectral_evaluate(
        layout.get(q_retracted, "common.T"), basis
    )
    tau_gradient = T_first_raw[..., 0]
    tau_gradient = tau_gradient + torch.tensor(
        (1.0, 0.0, 0.0, 0.0), dtype=DTYPE, device=q_retracted.device
    )[None, :]
    tau_hessian = T_second_raw[..., 0]
    foliation = foliation_geometry_from_primitives(
        gamma, gamma_first, gamma_second, tau_gradient, tau_hessian
    )
    inverse = foliation["inverse"]
    measure = foliation["sqrt_abs_determinant"]
    tau_norm_squared = foliation["tau_norm_squared"]
    u_covector = foliation["u_covector"]
    u_vector = foliation["u_vector"]
    projector_covariant = foliation["projector_covariant"]
    Ktrace = foliation["Ktrace"]
    K_squared = foliation["K_squared"]
    acceleration_covector = foliation["acceleration_covector"]
    acceleration_squared = foliation["acceleration_squared"]
    Rcal = foliation["Rcal"]

    frame0 = _ordered_spatial_frame(gamma, u_covector, u_vector)
    q_frame, _, _ = _spectral_evaluate(layout.get(q_retracted, "Q_frame.q"), basis)
    Q_rotation = torch.matrix_exp(_hat(q_frame))
    frame = torch.einsum("pma,pba->pmb", frame0, Q_rotation)
    varphi, _, _ = _spectral_evaluate(layout.get(q_retracted, "common.varphi"), basis)
    varphi_vector = torch.einsum("pma,pa->pm", frame, varphi)
    acceleration_vector = torch.einsum("pmn,pn->pm", inverse, acceleration_covector)
    robin_vector = varphi_vector - COEFFICIENTS["Robin_y"] * acceleration_vector
    robin_norm = torch.einsum(
        "pmn,pm,pn->p", projector_covariant, robin_vector, robin_vector
    )

    log_Omega, _, _ = _spectral_evaluate(
        layout.get(q_retracted, "common.log_Omega"), basis
    )
    Omega = torch.exp(log_Omega[..., 0])
    M5_cubed = COEFFICIENTS["M5_cubed"]
    G = COEFFICIENTS["compensator_metric_G"]
    k_infinity = COEFFICIENTS["k_infinity"]
    W = 3.0 * M5_cubed * k_infinity * torch.exp(
        -G * Omega * Omega / (6.0 * M5_cubed)
    )
    Mb_squared = COEFFICIENTS["brane_Mb_squared"]
    return {
        "wall": measure
        * (-2.0 * W - COEFFICIENTS["brane_beta"] * (Omega - 1.0) ** 2 / 2.0),
        "K_foliation": measure
        * Mb_squared
        * (K_squared - COEFFICIENTS["lambda_K"] * Ktrace * Ktrace)
        / 2.0,
        "R": measure * Mb_squared * COEFFICIENTS["xi"] * Rcal / 2.0,
        "R_squared": -measure
        * Mb_squared
        * COEFFICIENTS["B4_bar"]
        * Rcal
        * Rcal
        / (32.0 * k_infinity**2),
        "a_squared": measure
        * Mb_squared
        * COEFFICIENTS["eta"]
        * acceleration_squared
        / 2.0,
        "Robin": -measure * COEFFICIENTS["Robin_kappa_hat"] * robin_norm / 2.0,
        "diagnostic::tau_norm_squared": tau_norm_squared,
        "diagnostic::Rcal": Rcal,
        "diagnostic::Ktrace": Ktrace,
        "diagnostic::K_squared": K_squared,
        "diagnostic::a_squared": acceleration_squared,
        "diagnostic::frame_gram": torch.einsum("pma,pmn,pnb->pab", frame, gamma, frame),
    }


def free_brane_component_densities(
    free: torch.Tensor,
    N: int,
    K: int,
    tangential_points: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """Six interface atoms decoded pointwise from authoritative free data."""

    common = pointwise_common_fields(free, N, K, tangential_points)
    gamma = common["gamma"]
    tau_gradient = common["T_first"][..., 0] + torch.tensor(
        (1.0, 0.0, 0.0, 0.0), dtype=DTYPE, device=free.device
    )[None, :]
    tau_hessian = common["T_second"][..., 0]
    foliation = foliation_geometry_from_primitives(
        gamma,
        common["gamma_first"],
        common["gamma_second"],
        tau_gradient,
        tau_hessian,
    )
    inverse = foliation["inverse"]
    measure = foliation["sqrt_abs_determinant"]
    u_covector = foliation["u_covector"]
    u_vector = foliation["u_vector"]
    projector_covariant = foliation["projector_covariant"]
    Ktrace = foliation["Ktrace"]
    K_squared = foliation["K_squared"]
    acceleration_covector = foliation["acceleration_covector"]
    acceleration_squared = foliation["acceleration_squared"]
    Rcal = foliation["Rcal"]

    frame0 = _ordered_spatial_frame(gamma, u_covector, u_vector)
    frame = torch.einsum(
        "pma,pba->pmb", frame0, common["S"]
    )
    varphi_vector = torch.einsum("pma,pa->pm", frame, common["varphi_Q"])
    acceleration_vector = torch.einsum("pmn,pn->pm", inverse, acceleration_covector)
    robin_vector = varphi_vector - COEFFICIENTS["Robin_y"] * acceleration_vector
    robin_norm = torch.einsum(
        "pmn,pm,pn->p", projector_covariant, robin_vector, robin_vector
    )

    Omega = common["Omega"][..., 0]
    M5_cubed = COEFFICIENTS["M5_cubed"]
    G = COEFFICIENTS["compensator_metric_G"]
    k_infinity = COEFFICIENTS["k_infinity"]
    W = 3.0 * M5_cubed * k_infinity * torch.exp(
        -G * Omega * Omega / (6.0 * M5_cubed)
    )
    Mb_squared = COEFFICIENTS["brane_Mb_squared"]
    return {
        "wall": measure
        * (-2.0 * W - COEFFICIENTS["brane_beta"] * (Omega - 1.0) ** 2 / 2.0),
        "K_foliation": measure
        * Mb_squared
        * (K_squared - COEFFICIENTS["lambda_K"] * Ktrace * Ktrace)
        / 2.0,
        "R": measure * Mb_squared * COEFFICIENTS["xi"] * Rcal / 2.0,
        "R_squared": -measure
        * Mb_squared
        * COEFFICIENTS["B4_bar"]
        * Rcal
        * Rcal
        / (32.0 * k_infinity**2),
        "a_squared": measure
        * Mb_squared
        * COEFFICIENTS["eta"]
        * acceleration_squared
        / 2.0,
        "Robin": -measure * COEFFICIENTS["Robin_kappa_hat"] * robin_norm / 2.0,
        "diagnostic::tau_norm_squared": foliation["tau_norm_squared"],
        "diagnostic::Rcal": Rcal,
        "diagnostic::Ktrace": Ktrace,
        "diagnostic::K_squared": K_squared,
        "diagnostic::a_squared": acceleration_squared,
        "diagnostic::frame_gram": torch.einsum(
            "pma,pmn,pnb->pab", frame, gamma, frame
        ),
    }


def reference_bulk_component_densities(shape: tuple[int, int]) -> dict[str, torch.Tensor]:
    """Per-component L_i[X_infinity] for the compact relative action."""

    reference_metric = torch.diag(
        torch.tensor((-1.64, 1.17, 1.31, 1.46, 1.17), dtype=DTYPE)
    )
    volume = torch.sqrt(torch.abs(torch.linalg.det(reference_metric)))
    M5_cubed = COEFFICIENTS["M5_cubed"]
    G = COEFFICIENTS["compensator_metric_G"]
    k_infinity = COEFFICIENTS["k_infinity"]
    Omega = torch.tensor(1.0, dtype=DTYPE)
    W = 3.0 * M5_cubed * k_infinity * torch.exp(
        -G * Omega * Omega / (6.0 * M5_cubed)
    )
    W_Omega = -G * Omega * W / (3.0 * M5_cubed)
    U = W_Omega * W_Omega / (2.0 * G) - 2.0 * W * W / (3.0 * M5_cubed)
    zero = torch.zeros(shape, dtype=DTYPE)
    return {
        "EH": zero,
        "Omega_kinetic": zero,
        "Omega_potential": torch.ones(shape, dtype=DTYPE) * (-volume * U),
        "P_kinetic": zero,
        "full_V4": zero,
        "BF": zero,
    }


def relative_action_components_on_nodes(
    free: torch.Tensor,
    N: int,
    K: int,
    tangential_points: torch.Tensor,
    tangential_weights: torch.Tensor,
    rho: torch.Tensor,
    radial_weights: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """Evaluate all atoms on an explicit subset of quadrature nodes.

    Every subset keeps its original weights.  Therefore summing disjoint
    subsets is exactly the same linear quadrature functional as evaluating the
    full tensor grid at once, while bounding the AD transform's peak memory.
    """

    layout = free_layout(N, K)
    if free.shape != (layout.size,):
        raise LiteralTorchRouteError("relative action free-coordinate shape drift")
    if tangential_points.ndim != 2 or tangential_points.shape[1] != 4:
        raise LiteralTorchRouteError("explicit tangential nodes must have shape (P,4)")
    if tangential_weights.shape != (tangential_points.shape[0],):
        raise LiteralTorchRouteError("explicit tangential weight shape drift")
    if rho.ndim != 1 or radial_weights.shape != rho.shape:
        raise LiteralTorchRouteError("explicit radial quadrature shape drift")
    reference = reference_bulk_component_densities(
        (radial_weights.numel(), tangential_weights.numel())
    )
    components: dict[str, torch.Tensor] = {}
    for side in SIDES:
        primitives = decode_free_bulk_primitives(
            free, N, K, side, tangential_points, rho
        )
        bulk = bulk_component_densities(primitives, side)
        for atom in BULK_ATOMS:
            density_relative = bulk[atom] - reference[atom]
            components[f"{atom}_bulk_{side}"] = _integrate_bulk(
                density_relative, radial_weights, tangential_weights
            )
        ghy = interface_free_ghy_density(free, N, K, side, tangential_points)
        components[f"GHY_{side}"] = _integrate_brane(
            ghy["density"], tangential_weights
        )
    brane = free_brane_component_densities(free, N, K, tangential_points)
    for atom in BRANE_ATOMS:
        components[atom] = _integrate_brane(brane[atom], tangential_weights)
    if set(components) != set(COMPONENT_NAMES):
        raise LiteralTorchRouteError("twenty-component action decomposition drift")
    components["S_total"] = torch.stack(
        tuple(components[name] for name in COMPONENT_NAMES)
    ).sum()
    return components


def relative_action_components(
    free: torch.Tensor,
    N: int,
    K: int,
    quadrature: QuadratureSpec,
) -> dict[str, torch.Tensor]:
    """Evaluate twenty S_rel atoms after pointwise common-first elimination."""

    quadrature.validate()
    tangential_points, tangential_weights = periodic_t4_quadrature(
        quadrature.tangential_order_per_axis
    )
    rho, radial_weights = gauss_legendre_unit_interval(quadrature.radial_order)
    return relative_action_components_on_nodes(
        free,
        N,
        K,
        tangential_points,
        tangential_weights,
        rho,
        radial_weights,
    )


def relative_action_vector(
    free: torch.Tensor,
    N: int,
    K: int,
    quadrature: QuadratureSpec,
) -> torch.Tensor:
    components = relative_action_components(free, N, K, quadrature)
    return torch.stack(tuple(components[name] for name in OUTPUT_NAMES))


def action_value_and_jvp(
    free: torch.Tensor,
    tangent: torch.Tensor,
    N: int,
    K: int,
    quadrature: QuadratureSpec,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Forward AD for S_rel o pointwise-decode at one free tangent."""

    layout = free_layout(N, K)
    if free.shape != (layout.size,) or tangent.shape != (layout.size,):
        raise LiteralTorchRouteError("action JVP free-coordinate shape drift")

    def functional(trial: torch.Tensor) -> torch.Tensor:
        return relative_action_vector(trial, N, K, quadrature)

    value, directional = torch.func.jvp(functional, (free,), (tangent,))
    return value, directional


def action_value_and_jvp_chunked(
    free: torch.Tensor,
    tangent: torch.Tensor,
    N: int,
    K: int,
    quadrature: QuadratureSpec,
    *,
    tangential_chunk_size: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Forward AD/JVP with bounded memory and exact quadrature additivity."""

    layout = free_layout(N, K)
    if free.shape != (layout.size,) or tangent.shape != (layout.size,):
        raise LiteralTorchRouteError("chunked action JVP free-coordinate shape drift")
    if (
        isinstance(tangential_chunk_size, bool)
        or not isinstance(tangential_chunk_size, int)
        or tangential_chunk_size <= 0
    ):
        raise LiteralTorchRouteError("tangential chunk size must be positive")
    quadrature.validate()
    points, weights = periodic_t4_quadrature(quadrature.tangential_order_per_axis)
    rho, radial_weights = gauss_legendre_unit_interval(quadrature.radial_order)
    value_total = torch.zeros(len(OUTPUT_NAMES), dtype=DTYPE, device=free.device)
    directional_total = torch.zeros_like(value_total)
    for start in range(0, points.shape[0], tangential_chunk_size):
        stop = min(start + tangential_chunk_size, points.shape[0])
        chunk_points = points[start:stop]
        chunk_weights = weights[start:stop]

        def chunk_functional(trial: torch.Tensor) -> torch.Tensor:
            components = relative_action_components_on_nodes(
                trial,
                N,
                K,
                chunk_points,
                chunk_weights,
                rho,
                radial_weights,
            )
            return torch.stack(tuple(components[name] for name in OUTPUT_NAMES))

        value, directional = torch.func.jvp(
            chunk_functional, (free,), (tangent,)
        )
        value_total = value_total + value.detach()
        directional_total = directional_total + directional.detach()
    return value_total, directional_total


def action_sampling_diagnostics(
    free: torch.Tensor,
    N: int,
    K: int,
    quadrature: QuadratureSpec,
) -> dict[str, Any]:
    """Pointwise raw margins at every node used by this action evaluation."""

    quadrature.validate()
    points, _ = periodic_t4_quadrature(quadrature.tangential_order_per_axis)
    rho, _ = gauss_legendre_unit_interval(quadrature.radial_order)
    layout = free_layout(N, K)
    if free.shape != (layout.size,):
        raise LiteralTorchRouteError("sampling diagnostic free-coordinate shape drift")
    basis = evaluate_real_fourier_basis(points, N)
    common = pointwise_common_fields(free, N, K, points)
    common_gamma = common["gamma"]
    inertia_reports: dict[str, dict[str, Any]] = {
        "common_gamma": lorentzian_inertia_diagnostics(
            common_gamma, label="common_gamma_at_action_nodes"
        )
    }
    induced_residuals: dict[str, float] = {}
    bulk_min_minus_det: dict[str, float] = {}
    bulk_min_Omega: dict[str, float] = {}
    normal_residuals: dict[str, float] = {}
    orientation_signed_margins: dict[str, float] = {}
    rotation_chart_margins: dict[str, float] = {}
    q_frame, _, _ = _spectral_evaluate(layout.get(free, "Q_frame.q"), basis)
    rotation_chart_margins["Q_frame"] = float(
        (math.pi - torch.max(torch.linalg.vector_norm(q_frame, dim=-1))).detach()
    )
    for side in SIDES:
        bulk = decode_free_bulk_primitives(free, N, K, side, points, rho)
        inertia_reports[f"bulk_g_{side}"] = lorentzian_inertia_diagnostics(
            bulk["g"], label=f"bulk_g_{side}_at_action_nodes"
        )
        bulk_min_minus_det[side] = float(torch.min(-torch.linalg.det(bulk["g"])).detach())
        bulk_min_Omega[side] = float(torch.min(bulk["Omega"]).detach())
        ghy = interface_free_ghy_density(free, N, K, side, points)
        inertia_reports[f"induced_gamma_{side}"] = lorentzian_inertia_diagnostics(
            ghy["induced_metric"], label=f"induced_gamma_{side}_at_action_nodes"
        )
        induced_residuals[side] = float(
            torch.max(torch.abs(ghy["induced_metric"] - common_gamma)).detach()
        )
        normal_residuals[side] = float(
            torch.max(torch.abs(ghy["normal_norm_squared"] - 1.0)).detach()
        )
        expected_orientation_sign = 1.0 if side == "plus" else -1.0
        orientation_signed_margins[side] = float(
            torch.min(
                expected_orientation_sign
                * ghy["boundary_orientation_determinant"]
            ).detach()
        )
        r_E0, _, _ = _spectral_evaluate(
            layout.get(free, f"{side}.r_E0"), basis
        )
        rotation_chart_margins[side] = float(
            (math.pi - torch.max(torch.linalg.vector_norm(r_E0, dim=-1))).detach()
        )
    brane = free_brane_component_densities(free, N, K, points)
    frame_identity = torch.eye(3, dtype=DTYPE)[None, ...]
    for report in inertia_reports.values():
        require_lorentzian_inertia(report)
    if min(bulk_min_Omega.values()) <= 0.0:
        raise LiteralTorchRouteError("Omega positivity failed at an action node")
    if max(float(torch.max(brane["diagnostic::tau_norm_squared"]).detach()), -math.inf) >= 0.0:
        raise LiteralTorchRouteError("khronon gradient is not timelike at an action node")
    if min(orientation_signed_margins.values()) <= 0.0:
        raise LiteralTorchRouteError("outward boundary orientation failed at an action node")
    if min(rotation_chart_margins.values()) <= 0.0:
        raise LiteralTorchRouteError("SO(3) exponential coordinate reached the cut locus")
    gluing = pointwise_gluing_residual(free, N, K, points)
    return {
        "lorentzian_inertia_at_every_action_node": inertia_reports,
        "bulk_min_minus_det_g": bulk_min_minus_det,
        "bulk_min_Omega": bulk_min_Omega,
        "pointwise_induced_minus_common_gamma_Linf": induced_residuals,
        "pointwise_full_gluing_Linf": float(torch.max(torch.abs(gluing)).detach()),
        "outward_normal_unit_residual_Linf": normal_residuals,
        "outward_orientation_signed_determinant_min": orientation_signed_margins,
        "SO3_cut_locus_margin": rotation_chart_margins,
        "tau_norm_squared_max": float(
            torch.max(brane["diagnostic::tau_norm_squared"]).detach()
        ),
        "frame_gram_Linf": float(
            torch.max(torch.abs(brane["diagnostic::frame_gram"] - frame_identity)).detach()
        ),
        "corner_term_status": "absent: periodic T4 has no boundary and compact radial variations are flat at rho=1",
    }


def _verify_embedded_hash(mapping: Mapping[str, Any], field: str, *, label: str) -> None:
    expected = mapping.get(field)
    if not isinstance(expected, str):
        raise LiteralTorchRouteError(f"{label}: missing {field}")
    material = {key: value for key, value in mapping.items() if key != field}
    if _canonical_sha256(material) != expected:
        raise LiteralTorchRouteError(f"{label}: canonical hash drift")


def load_primitive_bundle() -> dict[str, Any]:
    """Load and validate the sole public route input without upstream imports."""

    if _sha256(PRIMITIVE_BUNDLE) != PRIMITIVE_BUNDLE_FILE_SHA256:
        raise LiteralTorchRouteError("primitive bundle byte pin drift")
    try:
        payload = json.loads(PRIMITIVE_BUNDLE.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LiteralTorchRouteError(f"cannot parse primitive bundle: {exc}") from exc
    if not isinstance(payload, dict) or set(payload) != EXPECTED_BUNDLE_TOP_LEVEL:
        raise LiteralTorchRouteError("primitive bundle top-level allowlist drift")
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise LiteralTorchRouteError("primitive bundle schema drift")
    _verify_embedded_hash(payload, "payload_sha256", label="primitive bundle")

    action = payload.get("action_contract")
    if not isinstance(action, dict):
        raise LiteralTorchRouteError("action contract missing")
    if action.get("exact_action") != EXACT_ACTION:
        raise LiteralTorchRouteError("literal v5.2 action text drift")
    if action.get("exact_action_sha256") != V5_2_EXACT_ACTION_SHA256:
        raise LiteralTorchRouteError("literal v5.2 action hash drift")
    if len(_canonical_bytes(action["exact_action"])) != V5_2_EXACT_ACTION_CANONICAL_BYTES:
        raise LiteralTorchRouteError("literal v5.2 action canonical length drift")
    if action.get("coefficient_parameters") != COEFFICIENTS:
        raise LiteralTorchRouteError("literal v5.2 coefficient drift")
    if action.get("coefficient_parameters_sha256") != _canonical_sha256(COEFFICIENTS):
        raise LiteralTorchRouteError("literal v5.2 coefficient hash drift")
    relative = action.get("compact_relative_action_contract")
    if not isinstance(relative, dict):
        raise LiteralTorchRouteError("compact relative action contract missing")
    if relative.get("object_name") != "S_rel_v5_2_on_finite_C_N_member":
        raise LiteralTorchRouteError("relative action object drift")
    if relative.get("bulk_domain") != {
        "radial": "rho_epsilon in [0,1] on each collar",
        "tangential": "T4=[0,2*pi)^4",
        "tangential_measure": "unnormalized dx0 dx1 dx2 dx3 with total constant-mode weight (2*pi)^4",
    }:
        raise LiteralTorchRouteError("relative action integration domain drift")
    if "DS_rel equals the first variation" not in relative.get("variational_equivalence", ""):
        raise LiteralTorchRouteError("relative/literal first-variation contract drift")

    decoder = payload.get("pointwise_decoder_contract")
    if not isinstance(decoder, dict) or decoder.get("N") != 2 or decoder.get("K") != 2:
        raise LiteralTorchRouteError("pointwise decoder truncation drift")
    tensor_order = decoder.get("tensor_component_order")
    if (
        not isinstance(tensor_order, dict)
        or tensor_order.get("symmetric4_pairs")
        != [list(pair) for pair in SYMMETRIC4]
        or tensor_order.get("symmetric5_pairs")
        != [list(pair) for pair in SYMMETRIC5]
        or tensor_order.get("antisymmetric_B_triples_5D")
        != [list(item) for item in B_TRIPLES]
    ):
        raise LiteralTorchRouteError("tensor component order drift")
    primitive_convention = decoder.get("primitive_component_convention")
    if not isinstance(primitive_convention, dict) or primitive_convention.get(
        "tau_covariant_derivative"
    ) != "D_M phi = partial_M phi + A_M_tau cross phi" or primitive_convention.get(
        "tau_curvature"
    ) != "F_MN_tau=partial_M A_N_tau-partial_N A_M_tau+A_M_tau cross A_N_tau":
        raise LiteralTorchRouteError("tau component convention drift")
    frame_contract = decoder.get("frame_rotation_contract")
    if not isinstance(frame_contract, dict) or frame_contract.get(
        "khronon_coordinate"
    ) != "tau_T(x)=x0+T(x)" or frame_contract.get(
        "Q_frame_decoder"
    ) != "E_Q=E0 exp(-hat(q_Q))":
        raise LiteralTorchRouteError("khronon/frame contract drift")
    embedding = decoder.get("embedding_pullback_orientation_contract")
    if not isinstance(embedding, dict) or embedding.get("collar_maps") != {
        "minus": "y4=Y_minus(x)+rho_minus; s_minus=partial y4/partial rho_minus=+1",
        "plus": "y4=Y_plus(x)-rho_plus; s_plus=partial y4/partial rho_plus=-1",
    } or embedding.get("oriented_interface_BF_flux_signs") != {
        "minus": -1,
        "plus": 1,
    }:
        raise LiteralTorchRouteError("embedding/orientation contract drift")

    published_layout = decoder.get("free_layout")
    if (
        not isinstance(published_layout, dict)
        or published_layout.get("blocks") != free_layout(2, 2).contract()
        or published_layout.get("canonical_sha256")
        != _canonical_sha256(published_layout.get("blocks"))
    ):
        raise LiteralTorchRouteError("authoritative free layout drift")
    published_basis = decoder.get("basis")
    if not isinstance(published_basis, dict):
        raise LiteralTorchRouteError("published N=2 basis missing")
    rebuilt = collocation_basis(2)
    if published_basis.get("mode_wavevectors") != [
        list(item) for item in _mode_wavevectors(2)
    ]:
        raise LiteralTorchRouteError("N=2 mode enumeration drift")
    comparisons = (
        (rebuilt["points"], published_basis.get("collocation_points_T4")),
        (rebuilt["values"], published_basis.get("value_matrix")),
        (
            rebuilt["first"].permute(1, 0, 2),
            published_basis.get("four_partial_derivative_matrices"),
        ),
    )
    for rebuilt_value, published_value in comparisons:
        candidate = torch.tensor(published_value, dtype=DTYPE)
        if candidate.shape != rebuilt_value.shape or float(
            torch.max(torch.abs(candidate - rebuilt_value))
        ) > 8.0e-15:
            raise LiteralTorchRouteError("published N=2 Fourier basis drift")

    geometry = payload.get("geometry_convention")
    if not isinstance(geometry, dict) or geometry.get("Gauss_sign_cross_checks") != [
        "spatially flat FLRW gives Rcal=0",
        "static R x S3 of radius a gives Rcal=+6/a^2",
    ] or "Rcal=h^mu_rho h^nu_sigma R4_(mu nu rho sigma)-Kcal^2+Kcal_mu_nu Kcal^mu_nu" not in geometry.get(
        "foliation", []
    ):
        raise LiteralTorchRouteError("Gauss/Riemann geometry convention drift")

    corrigendum_pin = payload.get("source_pins", {}).get(
        "mandatory_v5_5_4_Gauss_sign_corrigendum"
    )
    if (
        not isinstance(corrigendum_pin, dict)
        or corrigendum_pin.get("artifact_sha256") != GAUSS_SIGN_CORRIGENDUM_SHA256
        or corrigendum_pin.get("required_decision_path")
        != "decision.v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma"
        or corrigendum_pin.get("required_value_literal") != "false"
    ):
        raise LiteralTorchRouteError("mandatory Gauss-sign corrigendum pin drift")

    primary = payload.get("primary_member")
    identity = payload.get("identity_control")
    if not isinstance(primary, dict) or primary.get("member_id") != "N2.K2.seed20260902":
        raise LiteralTorchRouteError("primary N2 development member drift")
    if not isinstance(identity, dict) or identity.get("member_id") != "N2.K2.seed0":
        raise LiteralTorchRouteError("N2 identity control drift")
    for member in (primary, identity):
        if member.get("N") != 2 or member.get("K") != 2:
            raise LiteralTorchRouteError("pointwise member truncation drift")
        free = decode_f64le(
            member.get("authoritative_free_central_f64le", {}),
            label=f"{member.get('member_id')}.free",
        )
        if free.shape != (free_layout(2, 2).size,):
            raise LiteralTorchRouteError("pointwise member free dimension drift")

    curves = primary.get("curves")
    if not isinstance(curves, list) or not curves:
        raise LiteralTorchRouteError("primary free-coordinate curves missing")
    joint = [
        row
        for row in curves
        if row.get("name") == "joint_all_primitive_classes_control_candidate"
    ]
    if len(joint) != 1:
        raise LiteralTorchRouteError("unique joint primary curve missing")
    central = decode_f64le(
        primary["authoritative_free_central_f64le"], label="primary.free"
    )
    tangent = decode_f64le(
        joint[0].get("authoritative_free_tangent_f64le", {}),
        label="primary.joint.free_tangent",
    )
    if tangent.shape != central.shape:
        raise LiteralTorchRouteError("joint free tangent dimension drift")
    families = joint[0].get("step_families")
    if not isinstance(families, list) or [row.get("label") for row in families] != [
        "h",
        "h_over_2",
        "h_over_4",
    ]:
        raise LiteralTorchRouteError("multi-h free endpoint family drift")
    for family in families:
        endpoints = family.get("free_endpoints_f64le")
        if not isinstance(endpoints, dict) or set(endpoints) != {"-2", "-1", "1", "2"}:
            raise LiteralTorchRouteError("multi-h endpoint set drift")
        step = family.get("step")
        if not isinstance(step, (int, float)) or step <= 0.0:
            raise LiteralTorchRouteError("multi-h endpoint step drift")
        for multiplier_text, record in endpoints.items():
            endpoint = decode_f64le(
                record,
                label=f"primary.joint.{family.get('label')}.{multiplier_text}",
            )
            expected = central + float(multiplier_text) * float(step) * tangent
            if float(torch.max(torch.abs(endpoint - expected))) > 3.0e-15:
                raise LiteralTorchRouteError("published endpoint is not on the free affine curve")
    return payload


def _float_record(values: torch.Tensor) -> dict[str, float]:
    flat = values.detach().to(device="cpu", dtype=DTYPE).reshape(-1)
    if flat.numel() != len(OUTPUT_NAMES):
        raise LiteralTorchRouteError("action output width drift")
    return {name: float(flat[index]) for index, name in enumerate(OUTPUT_NAMES)}


def _primitive_direction_records(member: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Select only the byte-pinned joint curve used by the primary comparator."""

    curves = member.get("curves")
    if not isinstance(curves, list):
        raise LiteralTorchRouteError("primary pointwise curves missing")
    selected = [
        row
        for row in curves
        if row.get("name") == "joint_all_primitive_classes_control_candidate"
    ]
    if len(selected) != 1:
        raise LiteralTorchRouteError("unique primary joint free curve missing")
    return selected


def evaluate_member_route_a(
    member: Mapping[str, Any], quadrature: QuadratureSpec
) -> dict[str, Any]:
    """Evaluate the N2 joint free curve by Torch AD and raw multi-h endpoints."""

    N, K = member.get("N"), member.get("K")
    _validate_N_K(N, K)
    free = decode_f64le(
        member.get("authoritative_free_central_f64le", {}),
        label=f"{member.get('member_id')}.free",
    )
    direction_rows = _primitive_direction_records(member)
    source = direction_rows[0]
    direction = decode_f64le(
        source["authoritative_free_tangent_f64le"],
        label=f"{member.get('member_id')}.{source['name']}",
    )

    def functional(trial: torch.Tensor) -> torch.Tensor:
        return relative_action_vector(trial, N, K, quadrature)

    central, directional = torch.func.jvp(functional, (free,), (direction,))
    endpoint_rows: list[dict[str, Any]] = []
    for family in source["step_families"]:
        endpoint_values: dict[str, Any] = {}
        endpoint_hashes: dict[str, str] = {}
        endpoint_domains: dict[str, Any] = {}
        for multiplier, record in family["free_endpoints_f64le"].items():
            endpoint = decode_f64le(
                record,
                label=f"{member.get('member_id')}.{source['name']}.{family['label']}.{multiplier}",
            )
            endpoint_hashes[multiplier] = record["sha256"]
            endpoint_values[multiplier] = _float_record(functional(endpoint))
            endpoint_domains[multiplier] = action_sampling_diagnostics(
                endpoint, N, K, quadrature
            )
        endpoint_rows.append(
            {
                "label": family["label"],
                "step": family["step"],
                "free_endpoint_sha256": endpoint_hashes,
                "raw_S_rel_components": endpoint_values,
                "action_node_domain_diagnostics": endpoint_domains,
            }
        )
    central_record = _float_record(central)
    return {
        "member_id": member["member_id"],
        "N": N,
        "K": K,
        "seed": member["seed"],
        "seed_role": member["role"],
        "authoritative_free_central_sha256": member[
            "authoritative_free_central_f64le"
        ]["sha256"],
        "quadrature": {
            "tangential_rule": "independent tensor periodic trapezoid on [0,2*pi)^4",
            "tangential_order_per_axis": quadrature.tangential_order_per_axis,
            "tangential_node_count": quadrature.tangential_order_per_axis**4,
            "tangential_constant_mode_weight": (2.0 * math.pi) ** 4,
            "radial_rule": "independent Golub-Welsch Gauss-Legendre on [0,1]",
            "radial_order": quadrature.radial_order,
            "collocation_nodes_used_as_quadrature": False,
        },
        "central_S_rel_components": central_record,
        "central_component_scale_Linf": max(abs(value) for value in central_record.values()),
        "component_sum_residual": abs(
            central_record["S_total"]
            - sum(central_record[name] for name in COMPONENT_NAMES)
        ),
        "pointwise_sampling_diagnostics": action_sampling_diagnostics(
            free, N, K, quadrature
        ),
        "AD_JVP_receipt": {
            "name": source["name"],
            "comparison_role": source["comparison_role"],
            "free_tangent_sha256": source[
                "authoritative_free_tangent_f64le"
            ]["sha256"],
            "parent_ambient_tangent_sha256": source[
                "parent_ambient_tangent_sha256"
            ],
            "free_tangent_L2": float(torch.linalg.vector_norm(direction)),
            "AD_JVP_by_component": _float_record(directional),
            "AD_JVP_component_L2": float(torch.linalg.vector_norm(directional[:-1])),
            "AD_JVP_total_abs": float(torch.abs(directional[-1])),
            "AD_JVP_finite": bool(torch.all(torch.isfinite(directional))),
        },
        "raw_multi_h_endpoint_values": endpoint_rows,
        "interpretation": "raw off-shell directional derivatives; no zero-Ward or stationarity expectation is applied here",
    }


def evaluate_identity_control_route_a(
    member: Mapping[str, Any], quadrature: QuadratureSpec
) -> dict[str, Any]:
    """Evaluate the matched N2 seed-0 R=I control without a tangent claim."""

    if member.get("member_id") != "N2.K2.seed0" or member.get("role") != "R_equals_identity_control_only":
        raise LiteralTorchRouteError("identity-control member contract drift")
    free = decode_f64le(
        member.get("authoritative_free_central_f64le", {}),
        label="N2.K2.seed0.free",
    )
    values = relative_action_vector(free, 2, 2, quadrature)
    return {
        "member_id": member["member_id"],
        "N": 2,
        "K": 2,
        "seed": 0,
        "role": member["role"],
        "authoritative_free_central_sha256": member[
            "authoritative_free_central_f64le"
        ]["sha256"],
        "central_S_rel_components": _float_record(values),
        "pointwise_sampling_diagnostics": action_sampling_diagnostics(
            free, 2, 2, quadrature
        ),
        "interpretation": "matched-richness R=I control only; no tangent or closure claim",
    }


def mathematical_contract() -> dict[str, Any]:
    return {
        "object": "S_rel_v5_2_on_finite_C_N_member",
        "literal_action_sha256": V5_2_EXACT_ACTION_SHA256,
        "literal_action_component_count": 20,
        "output_component_count_including_total": 21,
        "ordered_components": list(OUTPUT_NAMES),
        "bulk_relative_action": "integral_[T4 x 0,1] (L_i[X]-L_i[X_infinity]) separately for each of twelve bulk atoms",
        "interface_action": "GHY plus wall,K,R,R_squared,a_squared,Robin are not reference-subtracted",
        "AD_object": "JVP of S_rel o common_first_pointwise_decode with respect to authoritative free coordinates",
        "tensor_calculus": {
            "EH": "Christoffel, dChristoffel, Ricci and scalar curvature reconstructed directly from g,dg,ddg",
            "GHY": "graph tangent, derived outward unit normal and trace of second fundamental form",
            "foliation": "tau_T=x0+T; Rcal=h h R4-Kcal^2+Kcal_mu_nu Kcal^mu_nu in the stated Riemann convention",
            "SO3_tau": "D phi=d phi+A cross phi; F=dA+A cross A",
            "BF": "full pullback top-form coefficient with det(J_collar)=s_epsilon; no factorial in unique-component storage",
            "Robin": "E_Q=E0 exp(-hat(q_Q)); varphi_H^mu=E_Q^mu_a varphi^a",
        },
        "radial_support": "h0/h1 and compact bumps are flat at rho=1; no artificial outer-boundary term enters DS_rel",
        "common_first_pointwise": "gamma,Omega,varphi_Q,A_Q are decoded first; both side traces are eliminated at every action node without N-node interpolation",
        "Gauss_sign_corrigendum": "v5.5.4's opposite intrinsic-curvature sign is quarantined; flat FLRW and static R x S3 witnesses fix this route's sign",
        "corner_term": "zero/absent because partial T4 is empty and the radial compact variation is flat at rho=1; no unlisted corner action is invented",
        "scope": "finite periodic T4 box and compact radial collar only",
    }


def _build_legacy_q3_payload() -> dict[str, Any]:
    bundle = load_primitive_bundle()
    quadrature = QuadratureSpec(tangential_order_per_axis=3, radial_order=4)
    receipt = evaluate_member_route_a(bundle["primary_member"], quadrature)
    identity_receipt = evaluate_identity_control_route_a(
        bundle["identity_control"], quadrature
    )
    central_domain = receipt["pointwise_sampling_diagnostics"]
    endpoint_domains = [
        domain
        for family in receipt["raw_multi_h_endpoint_values"]
        for domain in family["action_node_domain_diagnostics"].values()
    ]
    all_domains = [
        central_domain,
        identity_receipt["pointwise_sampling_diagnostics"],
        *endpoint_domains,
    ]
    checks = {
        "bundle_byte_and_canonical_pins_verified": True,
        "mandatory_Gauss_sign_corrigendum_verified": True,
        "literal_v5_2_action_and_coefficients_verified": True,
        "twenty_components_plus_total_emitted": set(receipt["central_S_rel_components"])
        == set(OUTPUT_NAMES),
        "component_sum_is_self_consistent": receipt["component_sum_residual"] < 2.0e-10,
        "common_first_pointwise_G_at_action_nodes": max(
            row["pointwise_full_gluing_Linf"] for row in all_domains
        ) < 2.0e-10,
        "Lorentzian_inertia_at_every_central_and_endpoint_action_node": all(
            all(
                report["all_nodes_lorentzian"]
                for report in row["lorentzian_inertia_at_every_action_node"].values()
            )
            for row in all_domains
        ),
        "all_route_A_JVP_outputs_are_finite": receipt["AD_JVP_receipt"][
            "AD_JVP_finite"
        ],
        "off_shell_joint_JVP_is_nontrivial": receipt["AD_JVP_receipt"][
            "AD_JVP_component_L2"
        ] > 0.0,
        "multi_h_endpoint_actions_emitted_raw": len(
            receipt["raw_multi_h_endpoint_values"]
        ) == 3,
        "AD_vs_independent_FD5_comparator_pass": False,
        "Euler_Green_independent_route_pass": False,
        "quadrature_mesh_N_simultaneous_convergence_pass": False,
        "independent_clean_process_redteam_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "B4_pass": False,
        "B5_pass": False,
    }
    return {
        "schema": SCHEMA,
        "title": "Literal Torch float64 v5.2 action route A on the finite restricted spectral family",
        "classification": "theory_only;finite_relative_action;literal_torch_AD_JVP;route_A_only;fail_closed",
        "decision": {
            "route_A_literal_action_and_AD_JVP_implemented": all(
                checks[key]
                for key in (
                    "bundle_byte_and_canonical_pins_verified",
                    "mandatory_Gauss_sign_corrigendum_verified",
                    "literal_v5_2_action_and_coefficients_verified",
                    "twenty_components_plus_total_emitted",
                    "component_sum_is_self_consistent",
                    "common_first_pointwise_G_at_action_nodes",
                    "Lorentzian_inertia_at_every_central_and_endpoint_action_node",
                    "all_route_A_JVP_outputs_are_finite",
                    "off_shell_joint_JVP_is_nontrivial",
                    "multi_h_endpoint_actions_emitted_raw",
                )
            ),
            "restricted_spectral_action_closure_claimed": False,
            "continuous_C1_N1_claimed": False,
        },
        "checks": checks,
        "mathematical_contract": mathematical_contract(),
        "literal_action": EXACT_ACTION,
        "coefficient_parameters": COEFFICIENTS,
        "scientific": {
            "primary_member_receipt": receipt,
            "identity_control_receipt": identity_receipt,
            "Green_identity_evaluated": False,
            "Eulerian_imported_or_reconstructed": False,
            "corner_residual_evaluated": False,
            "legacy_147_role": "20 component values plus S_total across seven old paths was a historical baseline only; no 147-vector is defined or evaluated here",
        },
        "dependency_graph": {
            "nodes": [
                "v5_2_literal_action_embedded_in_bundle",
                "v5_5_4_Gauss_sign_corrigendum",
                "v5_6_4_2_pointwise_primitive_bundle",
                "route_A_self_contained_Torch_tensor_calculus",
                "route_A_AD_JVP_receipt",
            ],
            "edges": [
                ["v5_2_literal_action_embedded_in_bundle", "v5_6_4_2_pointwise_primitive_bundle"],
                ["v5_5_4_Gauss_sign_corrigendum", "v5_6_4_2_pointwise_primitive_bundle"],
                ["v5_6_4_2_pointwise_primitive_bundle", "route_A_self_contained_Torch_tensor_calculus"],
                ["route_A_self_contained_Torch_tensor_calculus", "route_A_AD_JVP_receipt"],
            ],
            "no_edge_to_route_B_C_or_D": True,
            "forbidden_imports": [
                "v5.6.4 generator",
                "v5.6.2 generators/evaluators",
                "Eulerian/Green ledgers",
                "repository helpers",
            ],
        },
        "provenance": {
            "primitive_bundle": {
                "path": str(PRIMITIVE_BUNDLE.relative_to(REPO)),
                "sha256": _sha256(PRIMITIVE_BUNDLE),
                "schema": BUNDLE_SCHEMA,
                "payload_sha256": bundle["payload_sha256"],
                "gate_booleans_consumed": False,
                "precomputed_bulk_samples_consumed": False,
                "upstream_tolerances_consumed": False,
            },
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST) if TEST.exists() else None,
            },
            "runtime": {
                "torch_version": torch.__version__,
                "dtype": "torch.float64",
                "device": "cpu",
                "torch_threads": torch.get_num_threads(),
            },
        },
        "evidence_boundary": "This receipt establishes one literal Torch implementation, its forward-mode JVP on the finite N2.K2.seed20260902 joint curve, raw multi-h endpoint values, and a matched N2 seed-0 R=I control. It is not an independent agreement result, a Green identity, a simultaneous refinement table, finite action closure, or a continuous theorem.",
    }


def build_payload() -> dict[str, Any]:
    """Build the memory-bounded Q=5 route-A receipt used by the comparator."""

    bundle = load_primitive_bundle()
    member = bundle["primary_member"]
    identity_member = bundle["identity_control"]
    quadrature = QuadratureSpec(tangential_order_per_axis=5, radial_order=3)
    chunk_size = 64
    free = decode_f64le(
        member["authoritative_free_central_f64le"], label="primary.free"
    )
    curve = _primitive_direction_records(member)[0]
    tangent = decode_f64le(
        curve["authoritative_free_tangent_f64le"], label="primary.joint"
    )
    central, directional = action_value_and_jvp_chunked(
        free,
        tangent,
        2,
        2,
        quadrature,
        tangential_chunk_size=chunk_size,
    )
    central_diagnostics = action_sampling_diagnostics(free, 2, 2, quadrature)

    identity_free = decode_f64le(
        identity_member["authoritative_free_central_f64le"],
        label="identity.free",
    )
    identity_action = relative_action_vector(identity_free, 2, 2, quadrature)
    identity_diagnostics = action_sampling_diagnostics(
        identity_free, 2, 2, quadrature
    )
    layout = free_layout(2, 2)
    identity_r_zero = all(
        int(torch.count_nonzero(layout.get(identity_free, f"{side}.r_E0"))) == 0
        for side in SIDES
    )
    central_record = _float_record(central)
    directional_record = _float_record(directional)
    endpoint_manifest = [
        {
            "label": family["label"],
            "step": family["step"],
            "free_endpoint_sha256": {
                multiplier: record["sha256"]
                for multiplier, record in family["free_endpoints_f64le"].items()
            },
        }
        for family in curve["step_families"]
    ]
    checks = {
        "sole_runtime_input_bundle_byte_pin_verified": True,
        "literal_v5_2_action_hash_verified": True,
        "mandatory_Gauss_quarantine_embedded_in_bundle": True,
        "Q5_central_component_sum_residual_below_2e_10": abs(
            central_record["S_total"]
            - sum(central_record[name] for name in COMPONENT_NAMES)
        )
        < 2.0e-10,
        "Q5_chunked_AD_JVP_finite": bool(torch.all(torch.isfinite(directional))),
        "Q5_off_shell_JVP_nonzero": float(torch.linalg.vector_norm(directional[:-1]))
        > 0.0,
        "primary_pointwise_gluing_below_2e_10": central_diagnostics[
            "pointwise_full_gluing_Linf"
        ]
        < 2.0e-10,
        "identity_pointwise_gluing_below_2e_10": identity_diagnostics[
            "pointwise_full_gluing_Linf"
        ]
        < 2.0e-10,
        "primary_all_action_nodes_Lorentzian": all(
            row["all_nodes_lorentzian"]
            for row in central_diagnostics[
                "lorentzian_inertia_at_every_action_node"
            ].values()
        ),
        "identity_all_action_nodes_Lorentzian": all(
            row["all_nodes_lorentzian"]
            for row in identity_diagnostics[
                "lorentzian_inertia_at_every_action_node"
            ].values()
        ),
        "N2_seed0_R_exactly_identity": identity_r_zero,
        "independent_FD5_agreement_pass": False,
        "Euler_Green_independent_route_pass": False,
        "mutant_campaign_pass": False,
        "clean_process_redteam_pass": False,
        "multi_N_continuum_extension_pass": False,
    }
    route_a_ready = all(
        value
        for key, value in checks.items()
        if key
        not in {
            "independent_FD5_agreement_pass",
            "Euler_Green_independent_route_pass",
            "mutant_campaign_pass",
            "clean_process_redteam_pass",
            "multi_N_continuum_extension_pass",
        }
    )
    return {
        "schema": SCHEMA,
        "title": "Memory-bounded literal Torch route-A Q5 action and AD/JVP receipt",
        "classification": "theory_only;finite_N2;raw_route_A;no_C1_N1_promotion",
        "decision": {
            "route_A_Q5_literal_action_and_AD_JVP_pass": route_a_ready,
            "restricted_spectral_action_closure_claimed": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "checks": checks,
        "mathematical_contract": mathematical_contract(),
        "literal_action": EXACT_ACTION,
        "coefficient_parameters": COEFFICIENTS,
        "scientific": {
            "member_id": member["member_id"],
            "identity_control_member_id": identity_member["member_id"],
            "quadrature": {
                "tangential_points_per_axis": 5,
                "tangential_node_count": 5**4,
                "radial_gauss_order": 3,
            },
            "AD_execution": {
                "method": "torch.func.jvp summed over disjoint weighted tangential chunks",
                "tangential_chunk_size": chunk_size,
                "same_grid_chunk_equivalence_is_a_test_obligation": True,
                "same_grid_chunk_equivalence_test_sha256": _sha256(TEST),
            },
            "authoritative_free_central_sha256": member[
                "authoritative_free_central_f64le"
            ]["sha256"],
            "authoritative_free_tangent_sha256": curve[
                "authoritative_free_tangent_f64le"
            ]["sha256"],
            "parent_ambient_tangent_sha256": curve[
                "parent_ambient_tangent_sha256"
            ],
            "central_S_rel_components": central_record,
            "AD_JVP_by_component": directional_record,
            "primary_action_node_diagnostics": central_diagnostics,
            "published_endpoint_manifest_not_evaluated_by_route_A": endpoint_manifest,
            "R_equals_identity_control": {
                "central_S_rel_components": _float_record(identity_action),
                "action_node_diagnostics": identity_diagnostics,
                "r_E0_exactly_zero_both_sides": identity_r_zero,
            },
        },
        "provenance": {
            "primitive_bundle": {
                "path": str(PRIMITIVE_BUNDLE.relative_to(REPO)),
                "sha256": _sha256(PRIMITIVE_BUNDLE),
                "payload_sha256": bundle["payload_sha256"],
            },
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST),
            },
            "runtime": {
                "torch_version": torch.__version__,
                "dtype": "torch.float64",
                "device": "cpu",
                "torch_threads": torch.get_num_threads(),
            },
        },
        "evidence_boundary": "This raw route-A receipt covers one finite N2 member and its matched R=I control at Q5/r3. It does not compare FD5, derive Euler-Green, execute mutants, prove multi-N convergence, or promote C1/N1.",
    }


def main() -> None:
    payload = build_payload()
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(ARTIFACT)


if __name__ == "__main__":
    main()
