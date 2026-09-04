#!/usr/bin/env python3
"""Free-data family, lateral-trace invariance, and sampled nullspaces.

This corrected v5.6.6.16 receipt records finite evidence relevant to bridge
ledger gap 5 without calling it a kernel or quotient theorem.

Let U_N be the free-data space of the byte-pinned v5.6.4.2 common-first
decoder and let Phi map it to interface data, common and lateral traces, and
the C2 bulk fields.  Defining F_N := Phi(U_N) avoids a finite collocation
inverse in the selected Route A/Route C calculations.  It does not by itself
prove that a gauge quotient is unnecessary or harmless for the continuum
identity.  The checks here establish only:

  (G0) the pinned decoder's gluing-defect map and four sampled directional
       derivatives are within fixed tolerances at the three pinned members;
  (G1) Q_frame cancels symbolically from the lateral phi/A trace formulas;
  (G2) the same lateral-trace invariance is sampled in both pinned decoders,
       while common-frame outputs are explicitly shown to move;
  (G3) a finite output Jacobian, formed from lateral traces and interface
       consumables at eight random T4 points and omitting the independent J1/C
       radial-profile columns, has the reported sampled nullspace at the three
       pinned members; and
  (G4) six interface densities are invariant within tolerance under Q_frame
       changes on 16 sampled jets in each implementation; and
  (G5) the pinned Route C family is not dense in the declared H^s(T^4)
       target class: every current field depends tangentially only on
       theta=x0+x1, whereas cos(x2) is an exact orthogonal witness.

G3 is not the complete kernel of DPhi and is not a constant-rank theorem.  A
constant-only N=2 input has a nontrivial sampled-output fiber, serving as a
canary against globalizing the pinned-member ranks.  G1/G2 do not make Q_frame a
kernel of full Phi because its common-frame outputs move.  G4 does not prove
that every density, the action, or S_rel is invariant.  Therefore the
quotient/representative-independence part of gap 5 remains open.  G5
definitively refutes the current Route C uniform-N strategy, not the existence
of a different full-T4/arbitrary-N construction.  B_FD, quadrature, C1/N1,
B4, and B5 remain open/false.
"""

from __future__ import annotations

import ast
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
SCHEMA = "holo.one-omega-topological-so3-free-data-family-gauge-kernel-v5-6-6-16.v2"
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
TARGET_CLASS_PATH = HERE / "derive_one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.py"
TARGET_CLASS_SHA256 = "a8b26f130189dacfef14faf9cb9e1d1f19208cb645e267f198fc2f21ede428e4"

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
CONSTRAINT_TOLERANCE = 1.0e-11
CONSTRAINT_DERIVATIVE_TOLERANCE = 1.0e-8
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
# G0: sampled gluing defects and sampled directional derivatives are within tolerance
# --------------------------------------------------------------------------
def constraint_composed_with_free_embedding(decoder: Any, route_c: Any, bundle: Mapping[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    """Sample G o I_N and directional FD estimates of D(G o I_N)."""
    rows: dict[str, Any] = {}
    worst_value = 0.0
    worst_derivative = 0.0
    for member in bundle["primary_members"]:
        N = int(member["N"])
        contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
        free = _member_free(route_c, member)
        points = rng.uniform(0.0, 2.0 * math.pi, size=(POINTS_PER_MEMBER, 4))

        def defects(vector: np.ndarray) -> np.ndarray:
            decoded = decoder.decode_pointwise_boundary(vector, contract, points)
            result = decoder.pointwise_gluing_defects(decoded)
            return np.concatenate([np.asarray(result[side][name]).reshape(-1) for side in SIDES for name in ("gamma", "Omega", "phi", "A")])

        value = float(np.max(np.abs(defects(free))))
        derivative = 0.0
        for _ in range(4):
            direction = rng.normal(size=free.size)
            direction /= np.linalg.norm(direction)
            estimates = []
            for h in (JACOBIAN_STEP, 0.5 * JACOBIAN_STEP):
                estimates.append((defects(free + h * direction) - defects(free - h * direction)) / (2.0 * h))
            derivative = max(derivative, float(np.max(np.abs((4.0 * estimates[1] - estimates[0]) / 3.0))))
        rows[member["member_id"]] = {"N": N, "max_abs_defect": value, "max_abs_defect_derivative": derivative}
        worst_value = max(worst_value, value)
        worst_derivative = max(worst_derivative, derivative)
    return {
        "method": "pointwise_gluing_defects of the byte-pinned decoder (gamma, Omega, phi, A) at random T^4 points on the pinned members; derivative by Richardson central differences along four random unit directions of the whole free vector",
        "members": rows,
        "worst_defect": worst_value,
        "worst_defect_derivative": worst_derivative,
        "value_pass": bool(worst_value <= CONSTRAINT_TOLERANCE),
        "derivative_pass": bool(worst_derivative <= CONSTRAINT_DERIVATIVE_TOLERANCE),
    }

# --------------------------------------------------------------------------
# G1: symbolic Q-frame cancellation in the lateral phi/A traces
# --------------------------------------------------------------------------
def _hat_sym(v: sp.Matrix) -> sp.Matrix:
    return sp.Matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def _cayley(v: sp.Matrix) -> sp.Matrix:
    X = _hat_sym(v)
    return (sp.eye(3) - X).inv() * (sp.eye(3) + X)


def symbolic_q_frame_lateral_trace_cancellation(
    rng: np.random.Generator,
) -> dict[str, Any]:
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
# G2: numeric lateral-trace invariance and decoder agreement
# --------------------------------------------------------------------------
def numeric_q_frame_lateral_trace_invariance(
    decoder: Any,
    route_c: Any,
    bundle: Mapping[str, Any],
    rng: np.random.Generator,
) -> dict[str, Any]:
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
        "lateral_invariance_with_nonvacuous_common_motion_pass": bool(
            worst_kernel <= Q_INDEPENDENCE_TOLERANCE
            and smallest_common_motion > 1.0e-2
        ),
        "agreement_pass": bool(worst_agreement <= DECODER_AGREEMENT_TOLERANCE),
    }


# --------------------------------------------------------------------------
# G3: nullspace of a sampled trace/interface-output Jacobian
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


def sampled_trace_output_jacobian_nullspace(
    decoder: Any,
    route_c: Any,
    bundle: Mapping[str, Any],
    rng: np.random.Generator,
) -> dict[str, Any]:
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
            labels.append(
                f"[exact lateral-trace null direction] Q_frame.q[{index - start}]"
            )
        start, stop, shape = _block_slice(contract, "common.T")
        generators.append(unit(start))  # constant mode is the first row of the (N, 1) block
        labels.append("[decoder zero-mode, not SO(3)] common.T constant mode")
        for side in SIDES:
            start, stop, shape = _block_slice(contract, f"{side}.Y")
            generators.append(unit(start))
            labels.append(f"[decoder zero-mode, not SO(3)] {side}.Y constant mode")
        if N == 1:
            frame = _global_frame_generators(decoder, route_c, contract, free, columns)
            generators.append(frame[:, 0])
            labels.append("[pinned N=1 member stabiliser] constant common-frame rotation about varphi_E0 (stabiliser of the interface scalar)")
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
            "generator_categories": {
                "exact_lateral_trace_null_directions_Q_frame": sum(
                    label.startswith("[exact lateral-trace null direction]")
                    for label in labels
                ),
                "decoder_zero_modes_not_SO3": sum(label.startswith("[decoder zero-mode") for label in labels),
                "pinned_N1_member_stabiliser": sum(
                    label.startswith("[pinned N=1 member stabiliser]")
                    for label in labels
                ),
            },
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
            "to the selected trace-coordinate columns (the independent-profile blocks J1 and C are omitted); SVD; nullspace "
            "= singular values below KERNEL_RELATIVE_THRESHOLD * sigma_max; compared with the explicit generators by "
            "two-sided projection residuals and by J G directly"
        ),
        "members": rows,
        "pass": bool(all_pass),
    }


# --------------------------------------------------------------------------
# Canary: a nontrivial sampled-output fiber blocks globalizing the pinned rank
# --------------------------------------------------------------------------
def constant_only_n2_nontrivial_sampled_output_fiber_canary(
    decoder: Any, route_c: Any, bundle: Mapping[str, Any]
) -> dict[str, Any]:
    from scipy.linalg import expm, logm

    member = bundle["primary_members"][1]
    N = int(member["N"])
    if N != 2:
        raise GaugeKernelGateError("constant-only canary expects the pinned N=2 layout")
    contract = bundle["pointwise_decoder_contract_by_N"][str(N)]
    free = _member_free(route_c, member).copy()
    for spec in contract["free_layout"]["blocks"].values():
        shape = tuple(int(value) for value in spec["shape"])
        if shape and shape[0] == N:
            free[int(spec["start"]):int(spec["stop"])].reshape(shape)[1:] = 0.0

    points = np.random.default_rng(1616).uniform(
        0.0, 2.0 * math.pi, size=(4, 4)
    )
    pairs5 = tuple(tuple(int(value) for value in pair) for pair in route_c.SYMMETRIC5)
    tables = _interface_tables(contract["basis"], points)

    def outputs(vector: np.ndarray) -> np.ndarray:
        decoded = decoder.decode_pointwise_boundary(vector, contract, points)
        return np.concatenate(
            (_side_outputs(decoded, pairs5), _interface_outputs(vector, contract, tables))
        )

    moved = free.copy()
    start, stop, shape = _block_slice(contract, "common.varphi_E0")
    phi = moved[start:stop].reshape(shape)
    axis = phi[0] / np.linalg.norm(phi[0])
    rotation = expm(route_c._hat(0.13 * axis))
    phi[0] = rotation @ phi[0]
    start, stop, shape = _block_slice(contract, "common.A_E0")
    connection = moved[start:stop].reshape(shape)
    connection[0] = connection[0] @ rotation.T
    for side in SIDES:
        start, stop, shape = _block_slice(contract, f"{side}.r_E0")
        coordinate = moved[start:stop].reshape(shape)
        old_rotation = expm(route_c._hat(coordinate[0]))
        coordinate[0] = route_c._vee(np.real(logm(rotation @ old_rotation)))

    parameter_motion = float(np.max(np.abs(moved - free)))
    sampled_output_change = float(np.max(np.abs(outputs(moved) - outputs(free))))
    return {
        "N": N,
        "construction": "zero every nonconstant Fourier coefficient, then apply a finite common-frame rotation about the constant varphi_E0 axis",
        "sampled_T4_point_count": len(points),
        "free_parameter_max_abs_motion": parameter_motion,
        "sampled_trace_interface_output_max_abs_change": sampled_output_change,
        "tolerance": Q_INDEPENDENCE_TOLERANCE,
        "pass": bool(
            parameter_motion > 1.0e-3
            and sampled_output_change <= Q_INDEPENDENCE_TOLERANCE
        ),
        "interpretation": (
            "two distinct U_2 parameter points have the same recorded sampled outputs within tolerance; this is a "
            "nontrivial sampled-output fiber, not a computed tangent or Jacobian null direction, and it blocks "
            "globalizing the pinned N=2 rank from the present evidence"
        ),
    }


# --------------------------------------------------------------------------
# G5: exact non-density obstruction for the current theta-only Route C family
# --------------------------------------------------------------------------
def route_c_theta_only_t4_density_obstruction(route_c: Any) -> dict[str, Any]:
    if _sha256(TARGET_CLASS_PATH) != TARGET_CLASS_SHA256:
        raise GaugeKernelGateError("v5.6.6.8 target-class source drift")
    target_source = TARGET_CLASS_PATH.read_text(encoding="utf-8")
    target_scope_ok = all(
        token in target_source
        for token in (
            "in H^s(T^4)",
            "Fourier truncations P_N X converge to X in the class norm",
            "j < K, K up to 8",
        )
    )

    route_c_tree = ast.parse(ROUTE_C_PATH.read_text(encoding="utf-8"))
    basis_function = next(
        node for node in route_c_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_basis_values"
    )
    arbitrary_n_rejection_guard = any(
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "N"
        and len(node.test.ops) == 1
        and isinstance(node.test.ops[0], ast.NotIn)
        and len(node.test.comparators) == 1
        and isinstance(node.test.comparators[0], (ast.Tuple, ast.List))
        and [item.value for item in node.test.comparators[0].elts if isinstance(item, ast.Constant)] == [1, 2, 3]
        for node in ast.walk(basis_function)
    )

    supported_N = []
    rejected_N = []
    for N in range(1, 7):
        try:
            route_c._basis_values(N, 0.271)
        except route_c.RouteCMultiNError:
            rejected_N.append(N)
        else:
            supported_N.append(N)

    tangential = np.asarray([2.75])
    radial = np.asarray([-1.25])
    expanded_first = route_c._expand_first(tangential, radial).reshape(5)
    theta_only_derivative_pattern = bool(
        expanded_first[0] == tangential[0]
        and expanded_first[1] == tangential[0]
        and expanded_first[2] == 0.0
        and expanded_first[3] == 0.0
        and expanded_first[4] == radial[0]
    )

    x2 = sp.symbols("x2", real=True)
    mean = sp.integrate(sp.cos(x2), (x2, 0, 2 * sp.pi)) / (2 * sp.pi)
    unit_norm_squared = sp.integrate(sp.cos(x2) ** 2, (x2, 0, 2 * sp.pi)) / (2 * sp.pi)
    epsilon = sp.Rational(1, 4)
    witness_norm_squared = sp.simplify(epsilon**2 * unit_norm_squared)
    omega_minimum = math.exp(-float(epsilon))
    exact_orthogonal_witness = bool(
        mean == 0
        and unit_norm_squared == sp.Rational(1, 2)
        and witness_norm_squared == sp.Rational(1, 32)
        and omega_minimum > 0.5
    )
    current_route_refuted = bool(
        target_scope_ok
        and arbitrary_n_rejection_guard
        and supported_N == [1, 2, 3]
        and rejected_N == [4, 5, 6]
        and theta_only_derivative_pattern
        and exact_orthogonal_witness
    )
    return {
        "target_class_source": TARGET_CLASS_PATH.name,
        "target_class_source_sha256": TARGET_CLASS_SHA256,
        "target_scope_static_audit_pass": target_scope_ok,
        "route_c_basis_arbitrary_N_rejection_guard_ast_pass": arbitrary_n_rejection_guard,
        "route_c_supported_N_probe": supported_N,
        "route_c_rejected_N_probe": rejected_N,
        "route_c_tangential_coordinate": "theta = x0 + x1",
        "route_c_first_derivative_pattern_x0_x1_x2_x3_rho": [float(v) for v in expanded_first],
        "theta_only_derivative_pattern_pass": theta_only_derivative_pattern,
        "orthogonal_target_witness": "(1/4)*cos(x2) in common.log_Omega with all other background data fixed inside the open margins",
        "witness_epsilon": str(epsilon),
        "witness_Omega_lower_bound": omega_minimum,
        "declared_Omega_margin": 0.5,
        "witness_preserves_declared_Omega_margin": bool(omega_minimum > 0.5),
        "normalized_inner_product_factorization": "<cos(x2),g(x0+x1)> = mean_x2(cos(x2))*mean_x0_x1(g) = 0 for every integrable g; x3 factors as 1",
        "normalized_inner_product_with_every_g_x0_plus_x1": str(mean),
        "normalized_unit_amplitude_cos_x2_L2_norm_squared": str(unit_norm_squared),
        "normalized_witness_L2_norm_squared": str(witness_norm_squared),
        "normalized_squared_distance_lower_bound_to_theta_only_family": str(witness_norm_squared),
        "exact_orthogonality_pass": exact_orthogonal_witness,
        "pass": current_route_refuted,
        "scope": (
            "refutes density and the uniform-N bridge strategy of the byte-pinned theta-only Route C implementation; "
            "does not refute a future arbitrary-N full-T4 implementation or the continuum theorem itself"
        ),
    }


# --------------------------------------------------------------------------
# G4: sampled interface-density invariance under Q-frame changes
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
    g0 = constraint_composed_with_free_embedding(decoder, route_c, bundle, rng)
    g1 = symbolic_q_frame_lateral_trace_cancellation(rng)
    g2 = numeric_q_frame_lateral_trace_invariance(decoder, route_c, bundle, rng)
    g3 = sampled_trace_output_jacobian_nullspace(decoder, route_c, bundle, rng)
    output_fiber_canary = constant_only_n2_nontrivial_sampled_output_fiber_canary(
        decoder, route_c, bundle
    )
    g4 = interface_q_independence(route_c, route_b, parameters, rng)
    g5 = route_c_theta_only_t4_density_obstruction(route_c)
    v5669_sha = _sha256(V5669_PATH) if V5669_PATH.exists() else None
    scientific = {
        "statement": (
            "Let Phi_N be the full common-first decoder and Psi_N be its projection to the sampled lateral traces and "
            "interface consumables used in G3. Q_frame cancels algebraically from the lateral phi/A formulas, but it "
            "moves the common-frame arrays, so it is not a kernel direction of the full decoder unless a physical "
            "quotient target is separately defined. The SVD result is the numerical nullspace of D Psi_N evaluated at "
            "eight random T4 points at each of the three pinned members. Its dimensions 7/9/12 and listed spans hold "
            "within the fixed threshold only; they are not a theorem for ker D Phi_N or constant rank. r_E0 is non-null "
            "only at the pinned N=2,3 samples. G4 samples six interface densities only; no constancy of every sector "
            "density, nor along all listed generators, is established. A constant-only U_2 canary finds two distinct "
            "parameter points with the same sampled outputs within tolerance; it is not a tangent calculation. Gap 5 "
            "remains open globally. Independently, the exact cos(x2) orthogonality witness proves that the current "
            "theta=x0+x1, N in {1,2,3} Route C family is not dense in the declared H^s(T4) class, so its present "
            "uniform-N bridge strategy is refuted. This does not rule out a new arbitrary-N full-T4 implementation."
        ),
        "gap_5_restated": {
            "before": "state the finite family in free data only (so Phi(V_N) need not lie in V_N) and treat the 9N gauge orbit explicitly, or prove the quotient is harmless for the identity",
            "after": "F_N := Phi_N(U_N) avoids the finite collocation inverse for the fixed-member computations; Q_frame is invariant only after projection to the recorded lateral traces, and the reported nullspace belongs to a finite sampled D Psi_N. No physical quotient or representative-independence theorem is supplied; gap 5 remains open.",
        },
        "G0_constraint_composed_with_free_embedding": g0,
        "G1_symbolic_Q_frame_lateral_trace_cancellation": g1,
        "G2_numeric_Q_frame_lateral_trace_invariance_and_decoder_agreement": g2,
        "G3_sampled_trace_output_jacobian_nullspace": g3,
        "constant_only_N2_nontrivial_sampled_output_fiber_canary": output_fiber_canary,
        "G4_six_interface_densities_Q_frame_invariance_sampled": g4,
        "G5_current_route_c_theta_only_T4_density_obstruction": g5,
        "linear_blocks_omitted_from_the_sampled_jacobian": {
            "blocks": list(LINEAR_INDEPENDENT_PROFILE_BLOCKS),
            "reason": "omitted by construction; this receipt draws no conclusion about their contribution to the complete D Phi_N kernel",
        },
        "what_is_not_established": [
            "Q_frame as a kernel of full Phi_N, a physical quotient target, or representative-independence of S_rel",
            "the complete kernel of D Phi_N, constant rank, or the pinned N=2,3 r_E0 observation away from those members",
            "all-density or full-action invariance under Q_frame or any other listed sampled-nullspace generator",
            "anything about N -> infinity or density of the union of F_N",
            "a replacement arbitrary-N full-T4 Route C family, including radial K(N), and convergence of its complete decoder",
            "B_FD (Codex lane, v5.6.6.12) and quadrature",
            "any bridge, C1/N1, B4/B5 or promotion key",
        ],
    }
    decision = {
        "pointwise_gluing_defects_of_free_embedding_sampled_within_tolerance_pass": bool(g0["value_pass"]),
        "directional_FD_of_gluing_defects_composed_with_free_embedding_sampled_within_tolerance_pass": bool(g0["derivative_pass"]),
        "Q_frame_cancels_exactly_from_lateral_phi_and_A_trace_formulas_symbolic_pass": bool(g1["pass"]),
        "Q_frame_lateral_trace_invariance_numeric_at_pinned_members_within_tolerance_pass": bool(g2["lateral_invariance_with_nonvacuous_common_motion_pass"]),
        "route_c_and_pinned_lateral_trace_decoders_agree_sampled_within_tolerance_pass": bool(g2["agreement_pass"]),
        "sampled_trace_output_jacobian_nullspace_matches_listed_generators_at_pinned_members_pass": bool(g3["pass"]),
        "constant_only_N2_nontrivial_sampled_output_fiber_canary_pass": bool(
            output_fiber_canary["pass"]
        ),
        "six_interface_density_Q_frame_invariance_sampled_within_tolerance_pass": bool(g4["pass"]),
        "current_route_c_uniform_N_to_infinity_strategy_refuted_by_cos_x2_pass": bool(g5["pass"]),
        "Q_frame_kernel_of_full_free_embedding_Phi_N_pass": False,
        "complete_DPhi_N_kernel_and_constant_rank_theorem_pass": False,
        "pinned_member_sampled_nullspace_dimension_globalizes_over_U_N_pass": False,
        "r_E0_directions_globally_nonnull_for_all_U_N_with_N_ge_2_pass": False,
        "physical_gauge_quotient_and_representative_independence_pass": False,
        "all_sector_densities_and_action_invariant_under_listed_generators_pass": False,
        "gap_5_closed_pass": False,
        "current_route_c_supports_arbitrary_N_full_T4_spectral_projection_pass": False,
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
        "classification": "theory_only;free_data_formulation;sampled_trace_jacobian_kernel_decomposition;pinned_members_N123;current_theta_only_uniform_strategy_refuted;fail_closed_bridge",
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "v5_6_4_2_pointwise_decoder_sha256": DECODER_SHA256,
            "route_c_v5_6_6_3_derive_sha256": ROUTE_C_SHA256,
            "route_b_v5_6_5_certificate_derive_sha256": ROUTE_B_SHA256,
            "v5_6_6_9_receipt_sha256": v5669_sha,
            "v5_6_6_8_target_class_derive_sha256": TARGET_CLASS_SHA256,
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
            "constraint_tolerance": CONSTRAINT_TOLERANCE,
            "constraint_derivative_tolerance": CONSTRAINT_DERIVATIVE_TOLERANCE,
            "trace_common_blocks": list(TRACE_COMMON_BLOCKS),
            "trace_side_blocks": list(TRACE_SIDE_BLOCKS),
        },
        "scientific": scientific,
        "decision": decision,
        "evidence_boundary": (
            "Exact symbolic Q-frame cancellation from the lateral phi/A formulas; lateral-trace invariance and decoder "
            "agreement sampled at the three pinned members; and a Richardson-FD nullspace decomposition for a finite "
            "sampled trace/interface-output Jacobian at those members. The full decoder's common-frame arrays move. "
            "The exact cos(x2) witness refutes density of the byte-pinned theta-only Route C family in the declared T4 "
            "class and therefore its current uniform-N strategy; it does not refute a replacement full-T4 family or the "
            "continuum theorem. Not a full-Phi kernel, constant-rank, quotient, representative-independence, all-density, "
            "B_FD, quadrature, bridge, C1/N1, B4, or B5 theorem."
        ),
        "independence_boundary": {
            "dynamic_imports": {"decoder": DECODER_PATH.name, "route_c": ROUTE_C_PATH.name, "route_b": ROUTE_B_PATH.name},
            "scipy_used_only_for": "expm/logm of the finite common-frame orbit candidates at N=1 and in the constant-only N=2 canary (local imports), plus use inside the pinned decoder",
            "no_route_c_pipeline_run": True,
        },
        "open_obligation": [
            "B_FD bound (Codex, v5.6.6.12)",
            "define and prove any physical quotient target plus representative-independence of the action",
            "complete D Phi_N kernel/constant-rank analysis rather than a finite sampled D Psi_N nullspace",
            "replace the refuted theta-only N={1,2,3} family by an arbitrary-N full-T4 projection with radial K(N), then prove complete-decoder convergence",
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
    g2 = s["G2_numeric_Q_frame_lateral_trace_invariance_and_decoder_agreement"]
    g3 = s["G3_sampled_trace_output_jacobian_nullspace"]
    g4 = s["G4_six_interface_densities_Q_frame_invariance_sampled"]
    print(f"G0 defect {s['G0_constraint_composed_with_free_embedding']['worst_defect']:.2e}, derivative {s['G0_constraint_composed_with_free_embedding']['worst_defect_derivative']:.2e}")
    print(f"G2 worst lateral change {g2['worst_lateral_change']:.2e}, common motion >= {g2['smallest_common_frame_motion']:.2e}, route C vs pinned {g2['worst_route_c_vs_pinned_agreement']:.2e}")
    for mid, row in g3["members"].items():
        print(f"G3 {mid}: sampled nullspace {row['kernel_dimension']} (generators {row['generator_rank']}), gap {row['gap_ratio']:.2e}, sigma_max {row['singular_max']:.3g}, pass {row['pass']}")
    print(f"G4 route C {g4['route_c_max_relative_change_under_q']:.2e}, route B {g4['route_b_max_relative_change_under_q']:.2e}")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
