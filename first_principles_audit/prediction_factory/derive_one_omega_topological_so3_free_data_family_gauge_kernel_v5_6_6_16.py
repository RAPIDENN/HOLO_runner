#!/usr/bin/env python3
"""The finite family in free data only, and the explicit gauge kernel of the
common-first decoder (v5.6.6.16; bridge ledger gap 5).

Gap 5 of the pointwise-bridge ledger (v5.6.6.10, restated in the roadmap):
    "state the finite family in free data only (so Phi(V_N) need not lie in
     V_N) and treat the 9N gauge orbit explicitly, or prove the quotient is
     harmless for the identity".

Statement adopted here.  Let U_N be the free-data space of the byte-pinned
v5.6.4.2 common-first decoder (blocks common.*, Q_frame.q, side.Y,
side.metric_free, side.A_perp, side.B0_full, side.r_E0, side.boundary_jet_J1,
side.interior_bump_C; real Fourier modes {1, cos(x0+x1), sin(x0+x1)}
truncated at N) and Phi : U_N -> (interface data, lateral traces, bulk
fields) the decoder followed by the C2 radial profiles.  The finite family
is F_N := Phi(U_N), a subset of the v5.6.6.8 continuum class (v5.6.6.9:
Phi is an explicit map with an N-independent Jacobian bound; v5.6.6.13:
the pinned members satisfy the margins on the whole collar).  Route C, the
AD route and the FD5 route all differentiate S_rel o Phi along free-data
curves, so the bridge identity (i) is always evaluated at (Phi(u), DPhi[u]
du); nothing in it needs a finite gluing map, a collocation inverse or a
quotient.  The "9N gauge orbit" of the v5.6.4 contract (Q_frame.q and the
two r_E0 blocks, 3N each) is treated explicitly:

  (G1) symbolic: the decoder composes R = S R0 with S = exp(hat q), so the
       lateral traces phi_source = R^T S varphi_E0 and A_source =
       vee(R^T (S hat(A_E0) S^T - dS S^T) R + R^T dR) reduce identically to
       R0^T varphi_E0 and vee(R0^T hat(A_E0) R0 + R0^T dR0): the 3N Q_frame
       coordinates are an exact kernel of Phi (checked with exact rational
       Cayley rotation families symbolic in theta).
  (G2) numeric: the same on the byte-pinned decoder and on Route C's own
       trace decoder (v5.6.6.3), at the pinned members N = 1, 2, 3, with the
       common-frame outputs shown to move (non-vacuous); and Route C's trace
       decoder agrees with the pinned decoder.
  (G3) numeric: the full kernel of DPhi restricted to the trace coordinates
       (everything except the linear, independent-profile blocks J1 and C)
       at the pinned members, by a Richardson central-difference Jacobian
       and its SVD; the kernel is compared with explicit generators: the 3N
       Q_frame directions, the constant mode of the khronon offset T (only
       its derivatives enter), the constant modes of Y_plus and Y_minus
       (only Y' and Y'' enter the pulled-back densities), and, at N = 1
       only, the constant common-frame rotation about the varphi_E0 axis
       (U varphi_E0 = varphi_E0, Ad_U A_E0, log(U R0_eps)), which stays
       inside U_1 because every block there is a constant.  The other two
       constant rotations are symmetries of the lateral traces but move
       varphi_E0, which the interface Robin term consumes directly with the
       metric-determined frame E0, so only the one-parameter stabiliser of
       varphi_E0 is a redundancy of the whole configuration.  For N >= 2 the
       common-frame rotation is a symmetry of the continuum trace decoder but
       log(U R0(x)) leaves the degree-N space, so it is not a redundancy of
       the finite family: the 6N r_E0 coordinates are physical there.
  (G4) numeric: the six interface densities (Route C _brane_density and the
       pinned Route B interface_action_components) are exactly independent
       of the Q_frame block.

Hence: on F_N no quotient is needed for the identity; the only exact
redundancies of the finite family are listed explicitly with their
generators and Phi (so S_rel o Phi and every density) is constant along
them; the v5.6.4 obligations "DG_N on V_N" and "uniform_stability_pass"
are retired by the change of formulation, not discharged, and their keys
stay False.  Not established: anything about N -> infinity, B_FD,
quadrature, or any bridge/C1/N1/B4/B5 key.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_free_data_family_gauge_kernel_v5_6_6_16.json"
TEST = HERE / "test_one_omega_topological_so3_free_data_family_gauge_kernel_v5_6_6_16.py"
SCHEMA = "holo.one-omega-topological-so3-free-data-family-gauge-kernel-v5-6-6-16.v1"
FROZEN_COMMIT = "ea014fd"

LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
DECODER_PATH = HERE / "export_one_omega_topological_so3_restricted_spectral_family_v5_6_4_2_pointwise_primitives.py"
DECODER_SHA256 = "4b7eda150cf2d22e04ef2b1b04391c31dc9e618839d7ead9e74a540371ab3d7f"
ROUTE_C_PATH = HERE / "derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3.py"
ROUTE_C_SHA256 = "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"
ROUTE_B_PATH = HERE / "derive_one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.py"
ROUTE_B_SHA256 = "6c98724d0e51c1cad16c80303e6ad7625d661bd1c9c56c9ff96c5b8124992909"
V5669_PATH = ARTIFACTS / "one_omega_topological_so3_common_first_explicit_retraction_v5_6_6_9.json"

# Fixed before run.
SEED = 56616
POINTS_PER_MEMBER = 8
Q_PERTURBATION_AMPLITUDE = 0.7
Q_INDEPENDENCE_TOLERANCE = 1.0e-12
DECODER_AGREEMENT_TOLERANCE = 1.0e-9
JACOBIAN_STEP = 1.0e-4
KERNEL_RELATIVE_THRESHOLD = 1.0e-7
KERNEL_GAP_MINIMUM = 1.0e3
KERNEL_SPAN_TOLERANCE = 1.0e-6
SYMBOLIC_INSTANCES = 2
SIDES = ("plus", "minus")
TRACE_COMMON_BLOCKS = ("common.gamma", "common.T", "common.log_Omega", "common.varphi_E0", "common.A_E0", "Q_frame.q")
TRACE_SIDE_BLOCKS = ("Y", "metric_free", "A_perp", "B0_full", "r_E0")
LINEAR_INDEPENDENT_PROFILE_BLOCKS = ("boundary_jet_J1", "interior_bump_C")


class GaugeKernelGateError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_pinned_module(path: Path, expected_sha256: str, name: str) -> Any:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise GaugeKernelGateError(f"{path.name} byte pin drift: {observed}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_bundle() -> Mapping[str, Any]:
    if _sha256(BUNDLE_PATH) != BUNDLE_SHA256:
        raise GaugeKernelGateError("C2 primitive bundle drift")
    bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    if bundle["action_contract"]["exact_action_sha256"] != LITERAL_V5_2_ACTION_SHA256:
        raise GaugeKernelGateError("literal v5.2 action hash drift")
    return bundle


def load_modules() -> tuple[Any, Any, Any]:
    decoder = _load_pinned_module(DECODER_PATH, DECODER_SHA256, "pinned_v5_6_4_2_decoder")
    route_c = _load_pinned_module(ROUTE_C_PATH, ROUTE_C_SHA256, "pinned_route_c_v5_6_6_3")
    route_b = _load_pinned_module(ROUTE_B_PATH, ROUTE_B_SHA256, "pinned_route_b_v5_6_5")
    return decoder, route_c, route_b


# --------------------------------------------------------------------------
# G1: symbolic kernel of the Q frame
# --------------------------------------------------------------------------
def _hat_sym(v: sp.Matrix) -> sp.Matrix:
    return sp.Matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def _cayley(v: sp.Matrix) -> sp.Matrix:
    X = _hat_sym(v)
    return (sp.eye(3) - X).inv() * (sp.eye(3) + X)


def symbolic_q_frame_kernel(rng: np.random.Generator) -> dict[str, Any]:
    theta = sp.symbols("theta", real=True)
    a = sp.Matrix([sp.Function(f"a{i}")(theta) for i in range(3)])
    v = sp.Matrix([sp.Function(f"v{i}")(theta) for i in range(3)])
    instances: list[dict[str, Any]] = []
    for instance in range(SYMBOLIC_INSTANCES):
        s0, s1 = (sp.Matrix([sp.Rational(int(x), 7) for x in rng.integers(-6, 7, size=3)]) for _ in range(2))
        r0, r1 = (sp.Matrix([sp.Rational(int(x), 5) for x in rng.integers(-4, 5, size=3)]) for _ in range(2))
        S = _cayley(s0 + s1 * theta)
        R0 = _cayley(r0 + r1 * theta)
        dS = S.diff(theta)
        dR0 = R0.diff(theta)
        # decoder formulas (byte-pinned v5.6.4.2 decode_pointwise_boundary)
        varphi = S * v
        A_common = S * _hat_sym(a) * S.T - dS * S.T
        R = S * R0
        dR = dS * R0 + S * dR0
        phi_source = R.T * varphi
        A_source = R.T * A_common * R + R.T * dR
        # claimed q-free values
        phi_claim = R0.T * v
        A_claim = R0.T * _hat_sym(a) * R0 + R0.T * dR0
        orthogonal = sp.simplify(S.T * S - sp.eye(3)) == sp.zeros(3, 3) and sp.simplify(R0.T * R0 - sp.eye(3)) == sp.zeros(3, 3)
        phi_zero = sp.simplify(phi_source - phi_claim) == sp.zeros(3, 1)
        A_zero = sp.simplify(A_source - A_claim) == sp.zeros(3, 3)
        A_skew = sp.simplify(A_claim + A_claim.T) == sp.zeros(3, 3)
        instances.append(
            {
                "instance": instance,
                "s_coefficients": [str(x) for x in list(s0) + list(s1)],
                "r_coefficients": [str(x) for x in list(r0) + list(r1)],
                "S_R0_orthogonal": bool(orthogonal),
                "phi_source_equals_R0T_varphi_E0": bool(phi_zero),
                "A_source_equals_R0T_hatA_R0_plus_R0T_dR0": bool(A_zero),
                "A_source_skew_symmetric": bool(A_skew),
            }
        )
    passed = all(all(v for k, v in inst.items() if isinstance(v, bool)) for inst in instances)
    return {
        "method": (
            "exact rational Cayley rotation families S(theta), R0(theta) (linear rotation vectors), symbolic "
            "A_E0(theta), varphi_E0(theta); the decoder composition R = S R0, dR = dS R0 + S dR0, A_common = "
            "S hat(A_E0) S^T - dS S^T, phi_source = R^T S varphi_E0, A_source = R^T A_common R + R^T dR is "
            "simplified against R0^T varphi_E0 and R0^T hat(A_E0) R0 + R0^T dR0; the identity holds for every "
            "orthogonal S, R0 since only S^T S = I is used"
        ),
        "instances": instances,
        "pass": bool(passed),
    }


# --------------------------------------------------------------------------
# helpers for the pinned members
# --------------------------------------------------------------------------
def _member_free(route_c: Any, member: Mapping[str, Any]) -> np.ndarray:
    return route_c._decode_f64(member["authoritative_free_central_f64le"])


def _block_slice(contract: Mapping[str, Any], name: str) -> tuple[int, int, tuple[int, ...]]:
    spec = contract["free_layout"]["blocks"][name]
    return int(spec["start"]), int(spec["stop"]), tuple(int(x) for x in spec["shape"])


def _side_outputs(decoded: Mapping[str, Any], pairs5: tuple[tuple[int, int], ...]) -> np.ndarray:
    pieces: list[np.ndarray] = []
    for side in SIDES:
        item = decoded["sides"][side]
        g = item["g_trace"]
        pieces.append(np.stack([g[:, i, j] for i, j in pairs5], axis=-1).reshape(-1))
        pieces.append(np.asarray(item["log_Omega_trace"]).reshape(-1))
        pieces.append(np.asarray(item["phi_trace"]).reshape(-1))
        pieces.append(np.asarray(item["A_trace_full"]).reshape(-1))
        pieces.append(np.asarray(item["B_trace_full"]).reshape(-1))
        pieces.append(np.asarray(item["Y_first"]).reshape(-1))
    return np.concatenate(pieces)


def _interface_tables(basis: Mapping[str, Any], points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    labels = basis["labels"]
    wavevectors = np.asarray(basis["mode_wavevectors"], dtype=float)
    P, M = points.shape[0], len(labels)
    values = np.zeros((P, M))
    first = np.zeros((P, 4, M))
    second = np.zeros((P, 4, 4, M))
    for mode, label in enumerate(labels):
        k = wavevectors[mode]
        phase = points @ k
        if label == "1":
            values[:, mode] = 1.0
        elif label.startswith("cos("):
            values[:, mode] = np.cos(phase)
            first[:, :, mode] = -np.sin(phase)[:, None] * k[None, :]
            second[:, :, :, mode] = -np.cos(phase)[:, None, None] * np.outer(k, k)[None]
        elif label.startswith("sin("):
            values[:, mode] = np.sin(phase)
            first[:, :, mode] = np.cos(phase)[:, None] * k[None, :]
            second[:, :, :, mode] = -np.sin(phase)[:, None, None] * np.outer(k, k)[None]
        else:
            raise GaugeKernelGateError(f"unsupported label {label}")
    return values, first, second


def _interface_outputs(free: np.ndarray, contract: Mapping[str, Any], tables: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    """What the interface densities consume, linear in the free data: gamma, T', T'', log_Omega, varphi_E0."""
    values, first, second = tables
    pieces: list[np.ndarray] = []
    for name, use in (("common.gamma", "value"), ("common.T", "derivatives"), ("common.log_Omega", "value"), ("common.varphi_E0", "value")):
        start, stop, shape = _block_slice(contract, name)
        coefficients = free[start:stop].reshape(shape)
        if use == "value":
            pieces.append(np.tensordot(values, coefficients, axes=([1], [0])).reshape(-1))
        else:
            pieces.append(np.tensordot(first, coefficients, axes=([2], [0])).reshape(-1))
            pieces.append(np.tensordot(second, coefficients, axes=([3], [0])).reshape(-1))
    return np.concatenate(pieces)


def _trace_coordinate_columns(contract: Mapping[str, Any]) -> list[tuple[str, int]]:
    columns: list[tuple[str, int]] = []
    for name in TRACE_COMMON_BLOCKS:
        start, stop, _ = _block_slice(contract, name)
        columns += [(name, index) for index in range(start, stop)]
    for side in SIDES:
        for block in TRACE_SIDE_BLOCKS:
            name = f"{side}.{block}"
            start, stop, _ = _block_slice(contract, name)
            columns += [(name, index) for index in range(start, stop)]
    return columns


# --------------------------------------------------------------------------
# G2: numeric kernel of the Q frame and decoder agreement
# --------------------------------------------------------------------------
def numeric_q_frame_kernel(decoder: Any, route_c: Any, bundle: Mapping[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    pairs5 = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5)
    rows: dict[str, Any] = {}
    worst_kernel = 0.0
    worst_agreement = 0.0
    smallest_common_motion = math.inf
    for member in bundle["primary_members"]:
        N = int(member["N"])
        contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
        free = _member_free(route_c, member)
        start, stop, _ = _block_slice(contract, "Q_frame.q")
        perturbed = free.copy()
        perturbed[start:stop] += Q_PERTURBATION_AMPLITUDE * rng.uniform(-1.0, 1.0, size=stop - start)
        points = rng.uniform(0.0, 2.0 * math.pi, size=(POINTS_PER_MEMBER, 4))
        base = decoder.decode_pointwise_boundary(free, contract, points)
        moved = decoder.decode_pointwise_boundary(perturbed, contract, points)
        kernel_pinned = float(np.max(np.abs(_side_outputs(base, pairs5) - _side_outputs(moved, pairs5))))
        common_motion = max(
            float(np.max(np.abs(base["common"]["varphi"] - moved["common"]["varphi"]))),
            float(np.max(np.abs(base["common"]["A_Sigma"] - moved["common"]["A_Sigma"]))),
            float(np.max(np.abs(base["common"]["E_Q"] - moved["common"]["E_Q"]))),
        )
        thetas = rng.uniform(0.0, 2.0 * math.pi, size=POINTS_PER_MEMBER)
        kernel_route_c = 0.0
        agreement = 0.0
        for side in SIDES:
            for theta in thetas:
                c_base, Y, Y_theta = route_c._trace_ambient_value(free, contract, side, float(theta))
                c_moved, _, _ = route_c._trace_ambient_value(perturbed, contract, side, float(theta))
                kernel_route_c = max(kernel_route_c, float(np.max(np.abs(c_base - c_moved))))
                point = np.asarray([[float(theta), 0.0, 0.0, 0.0]])
                pinned = decoder.decode_pointwise_boundary(free, contract, point)["sides"][side]
                pinned_vector = np.concatenate(
                    (
                        np.asarray([pinned["g_trace"][0, i, j] for i, j in pairs5]),
                        [float(pinned["log_Omega_trace"][0])],
                        pinned["phi_trace"][0],
                        pinned["A_trace_full"][0].reshape(15),
                        pinned["B_trace_full"][0].reshape(30),
                    )
                )
                agreement = max(agreement, float(np.max(np.abs(c_base - pinned_vector))))
                agreement = max(agreement, abs(Y_theta - float(pinned["Y_first"][0, 0])))
        rows[member["member_id"]] = {
            "N": N,
            "q_block_size": stop - start,
            "pinned_decoder_lateral_change_under_q_perturbation": kernel_pinned,
            "route_c_decoder_lateral_change_under_q_perturbation": kernel_route_c,
            "common_frame_outputs_change_under_q_perturbation": common_motion,
            "route_c_vs_pinned_decoder_lateral_traces_max_abs": agreement,
        }
        worst_kernel = max(worst_kernel, kernel_pinned, kernel_route_c)
        worst_agreement = max(worst_agreement, agreement)
        smallest_common_motion = min(smallest_common_motion, common_motion)
    return {
        "members": rows,
        "worst_lateral_change": worst_kernel,
        "smallest_common_frame_motion": smallest_common_motion,
        "worst_route_c_vs_pinned_agreement": worst_agreement,
        "kernel_pass": bool(worst_kernel <= Q_INDEPENDENCE_TOLERANCE and smallest_common_motion > 1.0e-2),
        "agreement_pass": bool(worst_agreement <= DECODER_AGREEMENT_TOLERANCE),
    }


# --------------------------------------------------------------------------
# G3: Jacobian kernel on the trace coordinates
# --------------------------------------------------------------------------
def _richardson_jacobian(function: Callable[[np.ndarray], np.ndarray], free: np.ndarray, columns: list[tuple[str, int]], step: float) -> np.ndarray:
    base = function(free)
    jacobian = np.empty((base.size, len(columns)))
    for column, (_name, index) in enumerate(columns):
        estimates = []
        for h in (step, 0.5 * step):
            up = free.copy()
            down = free.copy()
            up[index] += h
            down[index] -= h
            estimates.append((function(up) - function(down)) / (2.0 * h))
        jacobian[:, column] = (4.0 * estimates[1] - estimates[0]) / 3.0
    return jacobian


def _global_frame_generators(decoder: Any, route_c: Any, contract: Mapping[str, Any], free: np.ndarray, columns: list[tuple[str, int]]) -> np.ndarray:
    """N = 1 only: d/dt of u(t) = (U varphi_E0, Ad_U A_E0, log(U R0_eps)) for U = exp(t hat(axis)) with the
    axis along varphi_E0 (the stabiliser of the interface scalar), constant modes only."""
    from scipy.linalg import expm, logm  # local import: only for the finite orbit at N = 1

    index_of = {index: column for column, (_name, index) in enumerate(columns)}
    generators = []
    s_phi, e_phi, shape_phi = _block_slice(contract, "common.varphi_E0")
    axis = free[s_phi:e_phi].reshape(shape_phi)[0]
    axes = [axis / np.linalg.norm(axis)]
    for epsilon in axes:

        def orbit(t: float) -> np.ndarray:
            U = expm(route_c._hat(t * epsilon))
            moved = free.copy()
            s, e, shape = _block_slice(contract, "common.varphi_E0")
            moved[s:e] = (U @ free[s:e].reshape(shape)[0]).reshape(-1)
            s, e, shape = _block_slice(contract, "common.A_E0")
            A = free[s:e].reshape(shape)[0]  # (4, 3) constant mode
            moved[s:e] = (A @ U.T).reshape(-1)
            for side in SIDES:
                s, e, shape = _block_slice(contract, f"{side}.r_E0")
                R0 = expm(route_c._hat(free[s:e].reshape(shape)[0]))
                moved[s:e] = route_c._vee(np.real(logm(U @ R0))).reshape(-1)
            return moved

        h = 1.0e-5
        direction_full = (orbit(h) - orbit(-h)) / (2.0 * h)
        direction = np.zeros(len(columns))
        for index, value in enumerate(direction_full):
            if index in index_of:
                direction[index_of[index]] = value
        generators.append(direction)
    return np.stack(generators, axis=-1)


def jacobian_kernel(decoder: Any, route_c: Any, bundle: Mapping[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    pairs5 = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5)
    rows: dict[str, Any] = {}
    all_pass = True
    for member in bundle["primary_members"]:
        N = int(member["N"])
        contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
        free = _member_free(route_c, member)
        columns = _trace_coordinate_columns(contract)
        points = rng.uniform(0.0, 2.0 * math.pi, size=(POINTS_PER_MEMBER, 4))
        tables = _interface_tables(contract["basis"], points)

        def outputs(vector: np.ndarray) -> np.ndarray:
            decoded = decoder.decode_pointwise_boundary(vector, contract, points)
            return np.concatenate((_side_outputs(decoded, pairs5), _interface_outputs(vector, contract, tables)))

        jacobian = _richardson_jacobian(outputs, free, columns, JACOBIAN_STEP)
        singular = np.linalg.svd(jacobian, compute_uv=False)
        threshold = KERNEL_RELATIVE_THRESHOLD * float(singular[0])
        kernel_dimension = int(np.sum(singular < threshold))
        nonkernel_min = float(singular[-kernel_dimension - 1]) if kernel_dimension < singular.size else 0.0
        kernel_max = float(singular[-1]) if kernel_dimension == 0 else float(singular[singular.size - kernel_dimension])
        gap = nonkernel_min / max(kernel_max, 1.0e-300)
        # explicit generators
        generators: list[np.ndarray] = []
        labels: list[str] = []
        index_of = {index: column for column, (_name, index) in enumerate(columns)}

        def unit(index: int) -> np.ndarray:
            vector = np.zeros(len(columns))
            vector[index_of[index]] = 1.0
            return vector

        start, stop, _ = _block_slice(contract, "Q_frame.q")
        for index in range(start, stop):
            generators.append(unit(index))
            labels.append(f"Q_frame.q[{index - start}]")
        start, stop, shape = _block_slice(contract, "common.T")
        generators.append(unit(start))  # constant mode is the first row of the (N, 1) block
        labels.append("common.T constant mode")
        for side in SIDES:
            start, stop, shape = _block_slice(contract, f"{side}.Y")
            generators.append(unit(start))
            labels.append(f"{side}.Y constant mode")
        if N == 1:
            frame = _global_frame_generators(decoder, route_c, contract, free, columns)
            generators.append(frame[:, 0])
            labels.append("constant common-frame rotation about varphi_E0 (stabiliser of the interface scalar)")
        G = np.stack(generators, axis=-1)
        # kernel basis from the SVD
        _u, _s, vt = np.linalg.svd(jacobian, full_matrices=True)
        K = vt[jacobian.shape[1] - kernel_dimension:].T if kernel_dimension > 0 else np.zeros((len(columns), 0))
        generator_rank = int(np.linalg.matrix_rank(G, tol=1.0e-8))
        if kernel_dimension > 0:
            residual_G_in_K = float(np.max(np.abs(G - K @ (K.T @ G)))) / float(np.max(np.abs(G)))
            residual_K_in_G = float(np.max(np.abs(K - G @ np.linalg.lstsq(G, K, rcond=None)[0])))
            jacobian_on_generators = float(np.max(np.abs(jacobian @ G))) / float(singular[0])
        else:
            residual_G_in_K = residual_K_in_G = jacobian_on_generators = math.nan
        r_singular = []
        for side in SIDES:
            start, stop, _ = _block_slice(contract, f"{side}.r_E0")
            sub = jacobian[:, [index_of[i] for i in range(start, stop)]]
            r_singular.append(float(np.min(np.linalg.svd(sub, compute_uv=False))) / float(singular[0]))
        member_pass = (
            kernel_dimension == G.shape[1] == generator_rank
            and gap >= KERNEL_GAP_MINIMUM
            and residual_G_in_K <= KERNEL_SPAN_TOLERANCE
            and residual_K_in_G <= KERNEL_SPAN_TOLERANCE
            and jacobian_on_generators <= KERNEL_SPAN_TOLERANCE
            and min(r_singular) > KERNEL_RELATIVE_THRESHOLD * 10.0
        )
        all_pass = all_pass and member_pass
        rows[member["member_id"]] = {
            "N": N,
            "trace_coordinates": len(columns),
            "outputs": int(jacobian.shape[0]),
            "singular_max": float(singular[0]),
            "kernel_dimension": kernel_dimension,
            "kernel_singular_max": kernel_max,
            "nonkernel_singular_min": nonkernel_min,
            "gap_ratio": gap,
            "explicit_generators": labels,
            "generator_rank": generator_rank,
            "generators_inside_kernel_residual": residual_G_in_K,
            "kernel_inside_generators_residual": residual_K_in_G,
            "jacobian_on_generators_relative": jacobian_on_generators,
            "r_E0_blocks_smallest_singular_relative": r_singular,
            "pass": bool(member_pass),
        }
    return {
        "method": (
            "Richardson central-difference Jacobian (steps h, h/2) of the lateral traces (g, log Omega, phi, A, B, Y') "
            "at random T^4 points plus the interface consumables (gamma, T', T'', log Omega, varphi_E0) with respect "
            "to every trace coordinate (all blocks except the linear independent-profile blocks J1 and C); SVD; kernel "
            "= singular values below KERNEL_RELATIVE_THRESHOLD * sigma_max; compared with the explicit generators by "
            "two-sided projection residuals and by J G directly"
        ),
        "members": rows,
        "pass": bool(all_pass),
    }


# --------------------------------------------------------------------------
# G4: interface densities do not see the Q frame
# --------------------------------------------------------------------------
def interface_q_independence(route_c: Any, route_b: Any, parameters: Mapping[str, float], rng: np.random.Generator) -> dict[str, Any]:
    reference4 = np.diag((-1.64, 1.17, 1.31, 1.46))
    pairs4 = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC4)
    worst_c = 0.0
    worst_b = 0.0
    q_norm_max = 0.0
    second_pairs = [(i, j) for i in range(4) for j in range(i, 4)]
    n = 1 + 4 + len(second_pairs)
    values = np.zeros((1, n))
    first = np.zeros((1, 4, n))
    second = np.zeros((1, 4, 4, n))
    values[0, 0] = 1.0
    for mu in range(4):
        first[0, mu, 1 + mu] = 1.0
    for position, (i, j) in enumerate(second_pairs):
        second[0, i, j, 5 + position] = second[0, j, i, 5 + position] = 1.0
    tables = {"values": values, "first": first, "second": second}
    blocks = {"common.gamma": 10, "common.T": 1, "common.log_Omega": 1, "common.varphi_E0": 3, "Q_frame.q": 3}
    layout: dict[str, Any] = {}
    cursor = 0
    for name, width in blocks.items():
        layout[name] = {"start": cursor, "stop": cursor + n * width, "shape": [n, width]}
        cursor += n * width
    for _ in range(16):
        gamma = reference4.copy()
        for i, j in pairs4:
            gamma[i, j] += 0.18 * rng.uniform(-1.0, 1.0)
            gamma[j, i] = gamma[i, j]
        gamma_t = 0.35 * rng.uniform(-1.0, 1.0, size=10)
        gamma_tt = 0.35 * rng.uniform(-1.0, 1.0, size=10)
        T_t, T_tt = 0.05 * rng.uniform(-1.0, 1.0), 0.35 * rng.uniform(-1.0, 1.0)
        log_omega = 0.18 * rng.uniform(-1.0, 1.0)
        varphi = 0.36 * rng.uniform(-1.0, 1.0, size=3)
        q = rng.uniform(-1.0, 1.0, size=3)
        q *= 2.0 * rng.uniform(0.2, 1.0) / np.linalg.norm(q)
        q_norm_max = max(q_norm_max, float(np.linalg.norm(q)))
        results_c = []
        results_b = []
        for frame_q in (np.zeros(3), q):
            jet = {
                "q": np.concatenate((route_c._sym_vector(gamma, 4), [0.0, log_omega], varphi, frame_q)),
                "qt": np.concatenate((gamma_t, [T_t, 0.0], np.zeros(6))),
                "qtt": np.concatenate((gamma_tt, [T_tt, 0.0], np.zeros(6))),
            }
            results_c.append(route_c._brane_density(jet, parameters))
            free = np.zeros(cursor)
            for name, value, first_t, second_tt in (
                ("common.gamma", route_b._matrix_to_sym(gamma, 4), gamma_t, gamma_tt),
                ("common.T", np.zeros(1), np.asarray([T_t]), np.asarray([T_tt])),
                ("common.log_Omega", np.asarray([log_omega]), np.zeros(1), np.zeros(1)),
                ("common.varphi_E0", varphi, np.zeros(3), np.zeros(3)),
                ("Q_frame.q", frame_q, np.zeros(3), np.zeros(3)),
            ):
                block = np.zeros((n, blocks[name]))
                block[0] = value
                block[1] = block[2] = first_t
                for position, (i, j) in enumerate(second_pairs):
                    if i < 2 and j < 2:
                        block[5 + position] = second_tt
                spec = layout[name]
                free[spec["start"]:spec["stop"]] = block.reshape(-1)
            results_b.append(route_b.interface_action_components(free, layout, tables, np.asarray([1.0]), parameters))
        for sector in route_c.BRANE_SECTORS:
            scale = max(1.0, abs(float(results_c[0][sector])))
            worst_c = max(worst_c, abs(float(results_c[0][sector]) - float(results_c[1][sector])) / scale)
            worst_b = max(worst_b, abs(float(results_b[0][sector]) - float(results_b[1][sector])) / scale)
    return {
        "route_c_max_relative_change_under_q": worst_c,
        "route_b_max_relative_change_under_q": worst_b,
        "q_norm_max": q_norm_max,
        "pass": bool(max(worst_c, worst_b) <= Q_INDEPENDENCE_TOLERANCE),
    }


# --------------------------------------------------------------------------
def build_payload() -> dict[str, Any]:
    bundle = load_bundle()
    decoder, route_c, route_b = load_modules()
    parameters = bundle["action_contract"]["coefficient_parameters"]
    rng = np.random.default_rng(SEED)
    g1 = symbolic_q_frame_kernel(rng)
    g2 = numeric_q_frame_kernel(decoder, route_c, bundle, rng)
    g3 = jacobian_kernel(decoder, route_c, bundle, rng)
    g4 = interface_q_independence(route_c, route_b, parameters, rng)
    v5669_sha = _sha256(V5669_PATH) if V5669_PATH.exists() else None
    scientific = {
        "statement": (
            "Finite family in free data only: F_N = Phi(U_N) with Phi the byte-pinned common-first decoder followed "
            "by the C2 radial profiles; every route differentiates S_rel o Phi along free-data curves, so the bridge "
            "identity is evaluated at (Phi(u), DPhi[u] du) and needs neither a finite gluing map nor a quotient. The "
            "9N rotation coordinates of the v5.6.4 contract are treated explicitly: the 3N Q_frame coordinates are an "
            "exact kernel of Phi (symbolic and numeric), the 6N r_E0 coordinates are physical for N >= 2, and the "
            "complete kernel of DPhi on the trace coordinates at the pinned members is spanned by explicit generators "
            "(Q_frame, the constant modes of T, Y_plus, Y_minus, and at N = 1 the constant common-frame rotation about "
            "varphi_E0, the only constant rotation that leaves the interface scalar consumed by the Robin term fixed). "
            "Phi, hence S_rel o Phi and every sector density, is constant along these directions."
        ),
        "gap_5_restated": {
            "before": "state the finite family in free data only (so Phi(V_N) need not lie in V_N) and treat the 9N gauge orbit explicitly, or prove the quotient is harmless for the identity",
            "after": "F_N := Phi(U_N); kernel of DPhi listed with generators; no quotient enters the identity; the v5.6.4 'DG_N on V_N' and 'uniform_stability' obligations are retired by the change of formulation, not discharged (keys stay False)",
        },
        "G1_symbolic_Q_frame_kernel": g1,
        "G2_numeric_Q_frame_kernel_and_decoder_agreement": g2,
        "G3_jacobian_kernel_on_trace_coordinates": g3,
        "G4_interface_densities_independent_of_Q_frame": g4,
        "linear_blocks_not_in_the_jacobian": {
            "blocks": list(LINEAR_INDEPENDENT_PROFILE_BLOCKS),
            "reason": "they enter the bulk fields linearly through h1(rho) and the Legendre bumps b_j(rho), which are linearly independent radial profiles, so they add no kernel and no coupling to the trace coordinates",
        },
        "what_is_not_established": [
            "anything about N -> infinity, density of the union of F_N, or the common-frame redundancy of the continuum decoder inside U_N for N >= 2 (shown numerically to be absent, not proven)",
            "B_FD (Codex lane, v5.6.6.12) and quadrature",
            "the kernel at points other than the three pinned members (constant rank is not proven)",
            "any bridge, C1/N1, B4/B5 or promotion key",
        ],
    }
    decision = {
        "Q_frame_coordinates_are_exact_kernel_of_the_decoder_symbolic_pass": bool(g1["pass"]),
        "Q_frame_coordinates_are_exact_kernel_of_pinned_and_route_c_decoders_numeric_pass": bool(g2["kernel_pass"]),
        "route_c_trace_decoder_matches_pinned_decoder_pass": bool(g2["agreement_pass"]),
        "free_data_family_jacobian_kernel_is_explicit_gauge_generators_pass": bool(g3["pass"]),
        "interface_densities_independent_of_Q_frame_pass": bool(g4["pass"]),
        "uniform_N_to_infinity_bridge_pass": False,
        "uniform_stability_pass": False,
        "spectral_N_convergence_pass": False,
        "restricted_family_exact_action_identity_pass": False,
        "periodic_box_exhaustion_and_tail_control_pass": False,
        "density_union_C_N_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "C1_N1_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
    }
    payload = {
        "schema": SCHEMA,
        "classification": "theory_only;free_data_formulation;explicit_gauge_kernel;pinned_members_N123;restricted_spectral_family;fail_closed_bridge",
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "v5_6_4_2_pointwise_decoder_sha256": DECODER_SHA256,
            "route_c_v5_6_6_3_derive_sha256": ROUTE_C_SHA256,
            "route_b_v5_6_5_certificate_derive_sha256": ROUTE_B_SHA256,
            "v5_6_6_9_receipt_sha256": v5669_sha,
        },
        "fixed_before_run": {
            "seed": SEED,
            "points_per_member": POINTS_PER_MEMBER,
            "q_perturbation_amplitude": Q_PERTURBATION_AMPLITUDE,
            "q_independence_tolerance": Q_INDEPENDENCE_TOLERANCE,
            "decoder_agreement_tolerance": DECODER_AGREEMENT_TOLERANCE,
            "jacobian_step": JACOBIAN_STEP,
            "kernel_relative_threshold": KERNEL_RELATIVE_THRESHOLD,
            "kernel_gap_minimum": KERNEL_GAP_MINIMUM,
            "kernel_span_tolerance": KERNEL_SPAN_TOLERANCE,
            "symbolic_instances": SYMBOLIC_INSTANCES,
            "trace_common_blocks": list(TRACE_COMMON_BLOCKS),
            "trace_side_blocks": list(TRACE_SIDE_BLOCKS),
        },
        "scientific": scientific,
        "decision": decision,
        "evidence_boundary": (
            "Exact symbolic kernel of the Q frame; numeric kernel and decoder agreement at the three pinned members; "
            "Richardson-FD Jacobian kernel with explicit generators at those members. Not a constant-rank theorem, "
            "not a statement about N -> infinity, B_FD, quadrature, or any bridge/C1/N1 key."
        ),
        "independence_boundary": {
            "dynamic_imports": {"decoder": DECODER_PATH.name, "route_c": ROUTE_C_PATH.name, "route_b": ROUTE_B_PATH.name},
            "scipy_used_only_for": "expm/logm of the finite common-frame orbit at N = 1 (local import) and inside the pinned decoder",
            "no_route_c_pipeline_run": True,
        },
        "open_obligation": [
            "B_FD bound (Codex, v5.6.6.12)",
            "N -> infinity for arbitrary class members (density of the union of F_N modulo the continuum common-frame redundancy)",
            "independent audit before uniform_N_to_infinity_bridge_pass",
            "v5.6.1 quarantine obligations for C1/N1",
        ],
        "provenance": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "sympy": sp.__version__,
            "platform": platform.platform(),
            "generator": Path(__file__).name,
            "test": TEST.name,
        },
    }
    payload["scientific_payload_sha256"] = _canonical_sha256(scientific)
    return payload


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in payload["decision"].items() if v}, indent=2))
    s = payload["scientific"]
    g2, g3, g4 = s["G2_numeric_Q_frame_kernel_and_decoder_agreement"], s["G3_jacobian_kernel_on_trace_coordinates"], s["G4_interface_densities_independent_of_Q_frame"]
    print(f"G2 worst lateral change {g2['worst_lateral_change']:.2e}, common motion >= {g2['smallest_common_frame_motion']:.2e}, route C vs pinned {g2['worst_route_c_vs_pinned_agreement']:.2e}")
    for mid, row in g3["members"].items():
        print(f"G3 {mid}: kernel {row['kernel_dimension']} (generators {row['generator_rank']}), gap {row['gap_ratio']:.2e}, sigma_max {row['singular_max']:.3g}, pass {row['pass']}")
    print(f"G4 route C {g4['route_c_max_relative_change_under_q']:.2e}, route B {g4['route_b_max_relative_change_under_q']:.2e}")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
