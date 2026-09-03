#!/usr/bin/env python3
"""Additive v5.6.2 selected-family C1/N1 fail-closed diagnostics.

This file deliberately does *not* rehabilitate the frozen v5.6 receipt and it
does not compose earlier booleans.  It byte-pins the literal v5.2 action and
the independently audited v5.5.2--v5.5.4 receipts, then evaluates that action
again on one analytic five-dimensional moving-graph family.  A forward dual
route and a separately written NumPy/finite-difference route calculate the
same component action and selected mixed variations without importing any
Eulerian, residual, expected answer, or helper from an upstream gate.

The executable result records only selected-family numerical sanities.  It is
not a primary candidate: the complete same-action SO(3) Ward, the normal and
matter-shift variational route, mutation adequacy, C1/N1, arbitrary off-shell
fields, continuum convergence, BV--BFV/edge modes, large gauges, B4 and B5 all
remain fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import ast
import hashlib
import inspect
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate.json"
TEST = HERE / "test_one_omega_topological_so3_full_moving_c1_n1_v5_6_2_gate.py"
SCHEMA = "holo.one-omega-topological-so3-full-moving-c1-n1-v5-6-2-gate.v1"


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
    "v5_2_action": SourcePin(
        "one_omega_topological_so3_classical_v5_2_gate.json",
        "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
        "holo.one-omega-topological-so3-classical-v5-2-gate.v1",
        "derive_one_omega_topological_so3_classical_v5_2_gate.py",
        "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
        "test_one_omega_topological_so3_classical_v5_2_gate.py",
        "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
    ),
    "v5_5_2_primary": SourcePin(
        "one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.json",
        "4e068475ae316684cebd0f68e10d183fff7c0d90c46b155f2dfc8be4b3b0d6e8",
        "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-gate.v1",
        "derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py",
        "00f8fa443bda37711d2456cb5e55c8a5c349d1c7f814a44c63203e3c02836e1e",
        "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate.py",
        "4547d1e7f361b2c9b931dba3a9a5a5829d2a2563ab4a0c9c54a154f9292f7aca",
    ),
    "v5_5_2_redteam": SourcePin(
        "one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.json",
        "4c94c2abeb24fb3444be4f79c93aa383659feac9e706eea7fe4fe2aac85bc7f6",
        "holo.one-omega-topological-so3-adm-induced-chain-v5-5-2-redteam.v1",
        "derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.py",
        "470d3c8b2bc7429ad77083c39f9112cc1908501b176d72f3b464b2f37f62696d",
        "test_one_omega_topological_so3_adm_induced_chain_v5_5_2_redteam.py",
        "6b373b7cccac70316ca52172fe65cfad991f90d0ad160afa4cdb2994e67e6f4f",
    ),
    "v5_5_3_primary": SourcePin(
        "one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.json",
        "0bae4d93de669a95becb3742e4e2f8ad2f99517e9b6efa7a7cfc518b9c6d832d",
        "holo.one-omega-topological-so3-full-action-gauge-noether-v5-5-3-gate.v1",
        "derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.py",
        "3d9a57482d3a80832427d4d3e9e645e09d78166c3070de49de9f9cb89cbfd692",
        "test_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_gate.py",
        "9d88139a02ca6c708a921a51e27287480db65c81e0c6b008d5717f3775c99e34",
    ),
    "v5_5_3_redteam": SourcePin(
        "one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate.json",
        "21da830fcba7e08708723ba05a77d49be126fc25bea40660eb66c5fd979b1cc7",
        "holo.one-omega-topological-so3-full-action-gauge-noether-v5-5-3-redteam-gate.v1",
        "derive_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate.py",
        "7d4f636c1ef37dc96da13992d75ca96ff737a14a7b301f12997b9536b11aca1a",
        "test_one_omega_topological_so3_full_action_gauge_noether_v5_5_3_redteam_gate.py",
        "eed63000a1b6a0c76466f8732d86a52327cf7d556b675c1881ba1f606053c4e0",
    ),
    "v5_5_4_primary": SourcePin(
        "one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.json",
        "d5e60c535cdfb19aeee7d8007e3c39afcff699e34128ca1a016d4ba4469cd23c",
        "holo.one-omega-topological-so3-interface-diffeomorphism-khronon-v5-5-4-gate.v1",
        "derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.py",
        "299d07965f0a6feb4f9f577664a7c13f09107fefe85ac80ac6efdf5b0e22c024",
        "test_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_gate.py",
        "2c37ccd958c9bee99d8d3a5b28bd345a22b90786d1b36b33cf01c23477c877c6",
    ),
    "v5_5_4_redteam": SourcePin(
        "one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam.json",
        "e1e70a013513ec154f3458891b28bb77a47739bcc264b571935cac1f06d1ade7",
        "holo.one-omega-topological-so3-interface-diffeomorphism-khronon-v5-5-4-redteam.v1",
        "derive_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam.py",
        "ddfbd9fc7bb3d50f09bebea927b6a63c1295aa729fa17e88be7bba7cd0f08bab",
        "test_one_omega_topological_so3_interface_diffeomorphism_khronon_v5_5_4_redteam.py",
        "04a44a3956056ee82da0a87543fd9696b5505e1c7077c35f8a64710a64bc5142",
    ),
    "v5_6_1_freeze": SourcePin(
        "one_omega_topological_so3_v5_6_1_quarantine_gate.json",
        "b83c7ae67a7e285ca7feb05afae95b8e9ae685da0f31d84d55a5824007b23e03",
        "holo.one-omega-topological-so3-v5-6-1-quarantine-gate.v2",
        "derive_one_omega_topological_so3_v5_6_1_quarantine_gate.py",
        "e31ab6f983ba7cef43a0e6b334d7f294612dd49726d88e5a34ba4d3a57b99bc2",
        "test_one_omega_topological_so3_v5_6_1_quarantine_gate.py",
        "00b06af19d4a9e1db85f1dfd83d42f1924a849167a36e7d70480876ab5b44581",
    ),
}


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

EXPECTED_COEFFICIENTS = {
    "M5_cubed": 1.0,
    "M4_bulk_squared_selected_one_Omega_wall_value": 1.107013790800849,
    "brane_Mb_squared": 2.0,
    "k_infinity": 1.0,
    "compensator_metric_G": 1.2,
    "brane_beta": 2.0,
    "xi": 1.0,
    "eta": 3.107013790800849,
    "B4_bar": 0.8,
    "Robin_kappa_hat": 1.0,
    "Robin_kappa_in_Mb_units": 0.5,
    "Robin_y": math.sqrt(3.0),
    "Robin_y_squared": 3.0,
    "lambda_K": -0.5535068954004245,
    "kappa_BF_inner_product": 1.0,
    "k_BF_trace_equivalent": -0.5,
    "material_Z5_per_side": 1.0,
    "material_mass_M": 1.0,
}


class FullMovingV562Error(ValueError):
    """A byte pin, mathematical contract, or fail-closed invariant failed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise FullMovingV562Error(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def _load_and_pin_sources() -> tuple[dict[str, Any], dict[str, Any]]:
    payloads: dict[str, Any] = {}
    receipt: dict[str, Any] = {}
    for label, pin in SOURCE_PINS.items():
        artifact = HERE / "artifacts" / pin.artifact
        generator = HERE / pin.generator
        test = HERE / pin.test
        actual = {
            "artifact": _sha256(artifact),
            "generator": _sha256(generator),
            "test": _sha256(test),
        }
        expected = {
            "artifact": pin.artifact_sha256,
            "generator": pin.generator_sha256,
            "test": pin.test_sha256,
        }
        if actual != expected:
            raise FullMovingV562Error(f"pinned source drift: {label}: {actual}")
        try:
            payload = json.loads(artifact.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise FullMovingV562Error(f"cannot parse {label}: {exc}") from exc
        if type(payload) is not dict or payload.get("schema") != pin.schema:
            raise FullMovingV562Error(f"schema mismatch: {label}")
        payloads[label] = payload
        receipt[label] = {
            "artifact": str(artifact.relative_to(REPO)),
            "artifact_sha256": actual["artifact"],
            "schema": pin.schema,
            "generator": str(generator.relative_to(REPO)),
            "generator_sha256": actual["generator"],
            "test": str(test.relative_to(REPO)),
            "test_sha256": actual["test"],
            "decision_boolean_consumed": False,
            "Eulerian_or_residual_consumed": False,
        }
    charter = payloads["v5_2_action"].get("exact_classical_charter")
    if type(charter) is not dict or charter.get("exact_action") != EXACT_ACTION:
        raise FullMovingV562Error("literal v5.2 action drift")
    try:
        raw = charter["coefficient_policy"]["parameters"]
    except (KeyError, TypeError) as exc:
        raise FullMovingV562Error("v5.2 coefficient ledger missing") from exc
    if set(raw) != set(EXPECTED_COEFFICIENTS):
        raise FullMovingV562Error("v5.2 coefficient keyset drift")
    if any(float(raw[key]) != value for key, value in EXPECTED_COEFFICIENTS.items()):
        raise FullMovingV562Error("v5.2 coefficient value drift")
    return payloads, receipt


SOURCE_PAYLOADS, PIN_RECEIPT = _load_and_pin_sources()
COEF = dict(EXPECTED_COEFFICIENTS)
M5 = COEF["M5_cubed"]
MB2 = COEF["brane_Mb_squared"]
KINF = COEF["k_infinity"]
GCOMP = COEF["compensator_metric_G"]
BETA = COEF["brane_beta"]
XI = COEF["xi"]
ETA = COEF["eta"]
B4BAR = COEF["B4_bar"]
KAPPA = COEF["Robin_kappa_hat"]
ROBIN_Y = COEF["Robin_y"]
LAMBDA_K = COEF["lambda_K"]
Z5 = COEF["material_Z5_per_side"]
MASS = COEF["material_mass_M"]

T_POINTS = 18
X_POINTS = 20
GAUSS_POINTS = 20
RADIAL_CUTOFF = 5.0
COLLAR_RADIUS = 1.25
WARP_CORE = 0.71
FD_STEP = 1.0e-5
MIXED_STEP = 8.0e-4
PARAMETER_NAMES = (
    "moving_embedding", "ambient_metric", "Omega", "associated_matter", "SO3_connection", "BF_three_form",
)
THETA = np.asarray([0.29, 0.24, 0.33, 0.41, 0.46, 0.38], dtype=float)


@dataclass(frozen=True)
class Dual:
    """Scalar/array dual number for a runtime directional JVP."""

    __array_priority__ = 1000
    value: np.ndarray
    dot: np.ndarray

    @classmethod
    def constant(cls, value: Any) -> "Dual":
        array = np.asarray(value, dtype=float)
        return cls(array, np.zeros_like(array))

    @classmethod
    def variable(cls, value: float, dot: float) -> "Dual":
        return cls(np.asarray(value, dtype=float), np.asarray(dot, dtype=float))

    @staticmethod
    def _coerce(value: Any) -> "Dual":
        return value if isinstance(value, Dual) else Dual.constant(value)

    @staticmethod
    def _align(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if left.ndim < right.ndim and left.shape == right.shape[: left.ndim]:
            left = left.reshape(left.shape + (1,) * (right.ndim - left.ndim))
        elif right.ndim < left.ndim and right.shape == left.shape[: right.ndim]:
            right = right.reshape(right.shape + (1,) * (left.ndim - right.ndim))
        return left, right

    def __add__(self, other: Any) -> "Dual":
        rhs = self._coerce(other)
        return Dual(self.value + rhs.value, self.dot + rhs.dot)

    __radd__ = __add__

    def __neg__(self) -> "Dual":
        return Dual(-self.value, -self.dot)

    def __sub__(self, other: Any) -> "Dual":
        return self + (-self._coerce(other))

    def __rsub__(self, other: Any) -> "Dual":
        return self._coerce(other) - self

    def __mul__(self, other: Any) -> "Dual":
        rhs = self._coerce(other)
        left_value, right_value = self._align(self.value, rhs.value)
        left_dot, right_dot = self._align(self.dot, rhs.dot)
        return Dual(left_value * right_value, left_dot * right_value + left_value * right_dot)

    __rmul__ = __mul__

    def __truediv__(self, other: Any) -> "Dual":
        rhs = self._coerce(other)
        return Dual(
            self.value / rhs.value,
            (self.dot * rhs.value - self.value * rhs.dot) / (rhs.value * rhs.value),
        )

    def __rtruediv__(self, other: Any) -> "Dual":
        return self._coerce(other) / self

    def __pow__(self, exponent: float) -> "Dual":
        value = self.value**exponent
        return Dual(value, exponent * self.value ** (exponent - 1.0) * self.dot)


def _dexp(value: Dual) -> Dual:
    out = np.exp(value.value)
    return Dual(out, out * value.dot)


def _dsin(value: Dual) -> Dual:
    return Dual(np.sin(value.value), np.cos(value.value) * value.dot)


def _dcos(value: Dual) -> Dual:
    return Dual(np.cos(value.value), -np.sin(value.value) * value.dot)


def _dstack(values: list[Dual], axis: int = -1) -> Dual:
    broadcast_values = np.broadcast_arrays(*[v.value for v in values])
    shape = broadcast_values[0].shape
    broadcast_dots = [np.broadcast_to(v.dot, shape) for v in values]
    return Dual(np.stack(broadcast_values, axis=axis), np.stack(broadcast_dots, axis=axis))


def _ddot(left: Dual, right: Dual) -> Dual:
    return Dual(
        np.sum(left.value * right.value, axis=-1),
        np.sum(left.dot * right.value + left.value * right.dot, axis=-1),
    )


def _dcross(left: Dual, right: Dual) -> Dual:
    return Dual(
        np.cross(left.value, right.value),
        np.cross(left.dot, right.value) + np.cross(left.value, right.dot),
    )


def _dcomponent(value: Dual, index: int) -> Dual:
    return Dual(value.value[..., index], value.dot[..., index])


def _grid() -> tuple[np.ndarray, np.ndarray]:
    t0 = np.linspace(0.0, 2.0 * math.pi, T_POINTS, endpoint=False)[:, None]
    x0 = np.linspace(0.0, 2.0 * math.pi, X_POINTS, endpoint=False)[None, :]
    shape = (T_POINTS, X_POINTS)
    return np.broadcast_to(t0, shape), np.broadcast_to(x0, shape)


def _profiles(t: np.ndarray, x: np.ndarray) -> dict[str, np.ndarray]:
    u = 2.0 * t - x
    base = 0.16 + 0.055 * np.cos(t) + 0.071 * np.cos(x) + 0.031 * np.sin(t + x)
    delta = 0.061 * np.sin(t) * np.cos(x) + 0.029 * np.cos(u)
    return {
        "Y": base,
        "Y_t": -0.055 * np.sin(t) + 0.031 * np.cos(t + x),
        "Y_x": -0.071 * np.sin(x) + 0.031 * np.cos(t + x),
        "Y_tt": -0.055 * np.cos(t) - 0.031 * np.sin(t + x),
        "Y_xx": -0.071 * np.cos(x) - 0.031 * np.sin(t + x),
        "Y_tx": -0.031 * np.sin(t + x),
        "dY": delta,
        "dY_t": 0.061 * np.cos(t) * np.cos(x) - 0.058 * np.sin(u),
        "dY_x": -0.061 * np.sin(t) * np.sin(x) + 0.029 * np.sin(u),
        "dY_tt": -0.061 * np.sin(t) * np.cos(x) - 0.116 * np.cos(u),
        "dY_xx": -0.061 * np.sin(t) * np.cos(x) - 0.029 * np.cos(u),
        "dY_tx": -0.061 * np.cos(t) * np.sin(x) + 0.058 * np.cos(u),
    }


def _chi(rho: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    u = rho / COLLAR_RADIUS
    inside = u < 1.0
    value = np.zeros_like(rho)
    derivative = np.zeros_like(rho)
    ui = u[inside]
    value[inside] = 1.0 - 10.0 * ui**3 + 15.0 * ui**4 - 6.0 * ui**5
    derivative[inside] = (-30.0 * ui**2 + 60.0 * ui**3 - 30.0 * ui**4) / COLLAR_RADIUS
    return value, derivative


@lru_cache(maxsize=1)
def _quadrature() -> tuple[np.ndarray, np.ndarray]:
    def interval(lo: float, hi: float) -> tuple[np.ndarray, np.ndarray]:
        nodes, weights = np.polynomial.legendre.leggauss(GAUSS_POINTS)
        return (hi - lo) * (nodes + 1.0) / 2.0 + lo, weights * (hi - lo) / 2.0
    inner = interval(0.0, COLLAR_RADIUS)
    outer = interval(COLLAR_RADIUS, RADIAL_CUTOFF)
    return np.concatenate((inner[0], outer[0])), np.concatenate((inner[1], outer[1]))


def _torus_dual(value: Dual) -> Dual:
    scale = (2.0 * math.pi) ** 2
    return Dual(np.asarray(scale * np.mean(value.value)), np.asarray(scale * np.mean(value.dot)))


def _torus_np(value: np.ndarray) -> float:
    return float((2.0 * math.pi) ** 2 * np.mean(value))


def _dual_parameters(theta: np.ndarray, direction: np.ndarray) -> list[Dual]:
    theta = np.asarray(theta, dtype=float)
    direction = np.asarray(direction, dtype=float)
    if theta.shape != (len(PARAMETER_NAMES),) or direction.shape != theta.shape:
        raise FullMovingV562Error("invalid selected-family parameter vector")
    return [Dual.variable(float(value), float(dot)) for value, dot in zip(theta, direction)]


def _dual_embedding(parameter: Dual, t: np.ndarray, x: np.ndarray) -> dict[str, Dual]:
    profiles = _profiles(t, x)
    return {
        name: Dual.constant(profiles[name]) + parameter * profiles[f"d{name}"]
        for name in ("Y", "Y_t", "Y_x", "Y_tt", "Y_xx", "Y_tx")
    }


def _dual_warp(q: Dual, metric_parameter: Dual) -> dict[str, Dual]:
    kappa = KINF * (1.0 + 0.12 * metric_parameter)
    radius = (q * q + WARP_CORE**2) ** 0.5
    A = -kappa * radius
    Aq = -kappa * q / radius
    Aqq = -kappa * WARP_CORE**2 / radius**3
    w = _dexp(A)
    return {"A": A, "Aq": Aq, "Aqq": Aqq, "w": w, "wq": Aq * w, "wqq": (Aqq + Aq * Aq) * w}


def _dual_geometry(parameters: list[Dual], t: np.ndarray, x: np.ndarray, *, freeze_R: bool = False) -> dict[str, Dual]:
    graph = _dual_embedding(parameters[0], t, x)
    warp = _dual_warp(graph["Y"], parameters[1])
    yt, yx = graph["Y_t"], graph["Y_x"]
    yxx, ytx = graph["Y_xx"], graph["Y_tx"]
    w = warp["w"]
    wx = warp["wq"] * yx
    wxx = warp["wqq"] * yx * yx + warp["wq"] * yxx
    E = w * w + yx * yx
    Ex = 2.0 * w * wx + 2.0 * yx * yxx
    D = E - yt * yt
    Dx = Ex - 2.0 * yt * ytx
    lapse = w * (D / E) ** 0.5
    measure = w**3 * D**0.5
    proper_wx = wx / E**0.5
    proper_wxx = wxx / E - wx * Ex / (2.0 * E * E)
    R3 = -4.0 * proper_wxx / w - 2.0 * (proper_wx / w) ** 2
    if freeze_R:
        R3 = Dual.constant(R3.value)
    ax = warp["Aq"] * yx + 0.5 * Dx / D - 0.5 * Ex / E
    a2 = ax * ax / E
    Kxx = yt / lapse * (w * warp["wq"] - yxx + yx * Ex / (2.0 * E))
    Kyy = w**3 * warp["wq"] * yt / (E * lapse)
    kx = Kxx / E
    kp = Kyy / (w * w)
    Ktrace = kx + 2.0 * kp
    Kij2 = kx * kx + 2.0 * kp * kp
    return {
        **graph, **warp, "E": E, "D": D, "N": lapse, "shift_x": yt * yx / E,
        "measure": measure, "R3": R3, "a_x": ax, "a2": a2,
        "Ktrace": Ktrace, "Kij2": Kij2,
    }


def _dual_vector_fields(
    q: Dual,
    t: np.ndarray,
    x: np.ndarray,
    parameters: list[Dual],
    *,
    anisotropic_v4: bool = False,
) -> dict[str, Dual]:
    """Build Omega, phi, A, B, P and F from the literal v5.2 definitions."""

    omega_parameter, matter_parameter, gauge_parameter, b_parameter = parameters[2:]
    envelope = _dexp(-(q * q) / 9.0)
    f = (
        0.16 * envelope * np.cos(t) + 0.11 * np.sin(x)
        + 0.04 * q * np.sin(t + x) + 0.03 * np.cos(2.0 * t - x)
    )
    ft = (
        -0.16 * envelope * np.sin(t) + 0.04 * q * np.cos(t + x)
        - 0.06 * np.sin(2.0 * t - x)
    )
    fx = 0.11 * np.cos(x) + 0.04 * q * np.cos(t + x) + 0.03 * np.sin(2.0 * t - x)
    fq = -0.32 * q * envelope * np.cos(t) / 9.0 + 0.04 * np.sin(t + x)
    omega = _dexp(omega_parameter * f)
    logt, logx, logq = omega_parameter * ft, omega_parameter * fx, omega_parameter * fq

    v = _dstack([
        0.72 + 0.11 * np.sin(t) + 0.045 * q + 0.018 * np.cos(t + x),
        0.28 * np.cos(x) + 0.065 * _dsin(q + t) + 0.025 * np.cos(t - x),
        0.24 * np.sin(t + x) + 0.052 * q * np.cos(x) + 0.021 * np.sin(2.0 * t - x),
    ])
    vt = _dstack([
        Dual.constant(0.11 * np.cos(t) - 0.018 * np.sin(t + x)),
        0.065 * _dcos(q + t) - 0.025 * np.sin(t - x),
        Dual.constant(0.24 * np.cos(t + x) + 0.042 * np.cos(2.0 * t - x)),
    ])
    vx = _dstack([
        Dual.constant(-0.018 * np.sin(t + x)),
        Dual.constant(-0.28 * np.sin(x) + 0.025 * np.sin(t - x)),
        0.24 * np.cos(t + x) - 0.052 * q * np.sin(x) - 0.021 * np.cos(2.0 * t - x),
    ])
    vq = _dstack([
        Dual.constant(np.full_like(q.value, 0.045)),
        0.065 * _dcos(q + t),
        Dual.constant(np.broadcast_to(0.052 * np.cos(x), q.value.shape)),
    ])

    def vec(items: list[Any]) -> Dual:
        return _dstack([item if isinstance(item, Dual) else Dual.constant(np.broadcast_to(item, q.value.shape)) for item in items])

    At0 = vec([0.12 * np.cos(x) + 0.035 * _dsin(q), 0.17 * _dsin(q) + 0.026 * np.cos(t), 0.08 * np.cos(t + x) + 0.031 * q])
    Ax0 = vec([0.09 * np.sin(t) + 0.028 * q, -0.11 * _dcos(q) + 0.022 * np.sin(x), 0.14 * np.sin(t - x)])
    Aq0 = vec([0.13 * np.cos(t) + 0.024 * np.sin(x), 0.07 * np.sin(x) + 0.019 * _dsin(q), -0.10 * np.cos(t + x)])
    Ay0 = vec([0.05 * _dsin(q), 0.06 * np.cos(t), 0.08 * np.sin(x)])
    Az0 = vec([-0.07 * np.cos(x), 0.04 * _dsin(q), 0.06 * np.cos(t)])
    At, Ax, Aq, Ay, Az = [gauge_parameter * item for item in (At0, Ax0, Aq0, Ay0, Az0)]

    At_t = gauge_parameter * vec([0.0, -0.026 * np.sin(t), -0.08 * np.sin(t + x)])
    At_x = gauge_parameter * vec([-0.12 * np.sin(x), 0.0, -0.08 * np.sin(t + x)])
    At_q = gauge_parameter * vec([0.035 * _dcos(q), 0.17 * _dcos(q), 0.031])
    Ax_t = gauge_parameter * vec([0.09 * np.cos(t), 0.0, 0.14 * np.cos(t - x)])
    Ax_x = gauge_parameter * vec([0.0, 0.022 * np.cos(x), -0.14 * np.cos(t - x)])
    Ax_q = gauge_parameter * vec([0.028, 0.11 * _dsin(q), 0.0])
    Aq_t = gauge_parameter * vec([-0.13 * np.sin(t), 0.0, 0.10 * np.sin(t + x)])
    Aq_x = gauge_parameter * vec([0.024 * np.cos(x), 0.07 * np.cos(x), 0.10 * np.sin(t + x)])
    Aq_q = gauge_parameter * vec([0.0, 0.019 * _dcos(q), 0.0])

    scale = matter_parameter * omega**-1.5
    phi = scale * v
    phi_t = scale * (vt - 1.5 * v * logt)
    phi_x = scale * (vx - 1.5 * v * logx)
    phi_q = scale * (vq - 1.5 * v * logq)
    Pt = phi_t + _dcross(At, phi) + 1.5 * phi * logt
    Px = phi_x + _dcross(Ax, phi) + 1.5 * phi * logx
    Pq = phi_q + _dcross(Aq, phi) + 1.5 * phi * logq
    Py = _dcross(Ay, phi)
    Pz = _dcross(Az, phi)

    Ftx = Ax_t - At_x + _dcross(At, Ax)
    Ftq = Aq_t - At_q + _dcross(At, Aq)
    Fxq = Aq_x - Ax_q + _dcross(Ax, Aq)
    Byzq = b_parameter * vec([0.20 + 0.03 * np.sin(t), -0.17 * np.cos(x), 0.11 * _dsin(t + x + q)])
    Bxyz = b_parameter * vec([0.07 * _dcos(q), 0.09 * np.sin(t), -0.08 * np.cos(x)])
    Btyz = b_parameter * vec([-0.06 * _dsin(q), 0.05 * np.cos(t + x), 0.10 * np.sin(x)])
    norm_phi = _ddot(phi, phi) ** 0.5
    radial = omega**1.5 * norm_phi
    V4 = radial**4 / (2.0 * (1.0 + radial**4) ** 0.5)
    if anisotropic_v4:
        V4 = V4 + 0.07 * _dcomponent(phi, 0)
    return {
        "omega": omega, "logt": logt, "logx": logx, "logq": logq,
        "phi": phi, "Pt": Pt, "Px": Px, "Pq": Pq, "Py": Py, "Pz": Pz,
        "At": At, "Ax": Ax, "Aq": Aq, "Ay": Ay, "Az": Az,
        "Ftx": Ftx, "Ftq": Ftq, "Fxq": Fxq,
        "Byzq": Byzq, "Bxyz": Bxyz, "Btyz": Btyz, "V4": V4,
    }


def _dual_bulk_densities(
    q: Dual,
    t: np.ndarray,
    x: np.ndarray,
    parameters: list[Dual],
    *,
    anisotropic_v4: bool = False,
) -> dict[str, Dual]:
    warp = _dual_warp(q, parameters[1])
    fields = _dual_vector_fields(q, t, x, parameters, anisotropic_v4=anisotropic_v4)
    w, omega = warp["w"], fields["omega"]
    R5 = -8.0 * warp["Aqq"] - 20.0 * warp["Aq"] * warp["Aq"]
    omega_t, omega_x, omega_q = omega * fields["logt"], omega * fields["logx"], omega * fields["logq"]
    omega2 = (-omega_t * omega_t + omega_x * omega_x) / (w * w) + omega_q * omega_q
    W = 3.0 * M5 * KINF * _dexp(-GCOMP * omega * omega / (6.0 * M5))
    W_Omega = -GCOMP * omega * W / (3.0 * M5)
    U = W_Omega * W_Omega / (2.0 * GCOMP) - 2.0 * W * W / (3.0 * M5)
    P2 = (
        (-_ddot(fields["Pt"], fields["Pt"]) + _ddot(fields["Px"], fields["Px"])
         + _ddot(fields["Py"], fields["Py"]) + _ddot(fields["Pz"], fields["Pz"])) / (w * w)
        + _ddot(fields["Pq"], fields["Pq"])
    )
    volume = w**4
    bf = (
        _ddot(fields["Byzq"], fields["Ftx"])
        - _ddot(fields["Bxyz"], fields["Ftq"])
        + _ddot(fields["Btyz"], fields["Fxq"])
    )
    return {
        "EH": volume * M5 * R5 / 2.0,
        "Omega_kinetic": -volume * GCOMP * omega2 / 2.0,
        "Omega_potential": -volume * U,
        "P_kinetic": -volume * Z5 * P2 / 2.0,
        "full_V4": -volume * Z5 * MASS**2 * omega**-5.0 * fields["V4"],
        "BF": bf,
    }


def _dual_bulk_side(
    parameters: list[Dual], epsilon: int, mutation: str | None,
) -> tuple[dict[str, Dual], dict[str, Dual]]:
    t, x = _grid()
    graph = _dual_embedding(parameters[0], t, x)
    rho, weights = _quadrature()
    chi, chi_rho = _chi(rho)
    q = epsilon * rho[:, None, None] + chi[:, None, None] * graph["Y"]
    jacobian = 1.0 + epsilon * chi_rho[:, None, None] * graph["Y"]
    if mutation == "broken_pullback_jacobian":
        jacobian = Dual.constant(np.ones_like(q.value))
    densities = _dual_bulk_densities(
        q, t[None, :, :], x[None, :, :], parameters,
        anisotropic_v4=mutation == "anisotropic_V4",
    )
    components: dict[str, Dual] = {}
    torus_densities: dict[str, Dual] = {}
    for name, density in densities.items():
        pulled = jacobian * density
        radial = Dual(
            np.sum(weights[:, None, None] * pulled.value, axis=0),
            np.sum(weights[:, None, None] * pulled.dot, axis=0),
        )
        torus_densities[name] = radial
        components[name] = _torus_dual(radial)
    return components, torus_densities


def _dual_ghy(parameters: list[Dual], epsilon: int, mutation: str | None) -> tuple[Dual, Dual]:
    t, x = _grid()
    geometry = _dual_geometry(parameters, t, x)
    sigma_out = -float(epsilon)
    if mutation == "wrong_GHY_orientation" and epsilon == -1:
        sigma_out = -1.0
    numerator = (
        geometry["wq"]
        * (4.0 * geometry["w"] ** 2 + 5.0 * (geometry["Y_x"] ** 2 - geometry["Y_t"] ** 2))
        + (
            geometry["Y_tt"] * (geometry["w"] ** 2 + geometry["Y_x"] ** 2)
            - geometry["Y_xx"] * (geometry["w"] ** 2 - geometry["Y_t"] ** 2)
            - 2.0 * geometry["Y_t"] * geometry["Y_x"] * geometry["Y_tx"]
        ) / geometry["w"]
    )
    density = M5 * sigma_out * geometry["w"] ** 3 * numerator / geometry["D"]
    return _torus_dual(density), density


def _dual_brane(parameters: list[Dual], mutation: str | None) -> tuple[dict[str, Dual], dict[str, Dual]]:
    t, x = _grid()
    geometry = _dual_geometry(parameters, t, x, freeze_R=mutation == "freeze_R")
    trace = _dual_vector_fields(geometry["Y"], t, x, parameters, anisotropic_v4=False)
    omega, phi = trace["omega"], trace["phi"]
    W = 3.0 * M5 * KINF * _dexp(-GCOMP * omega * omega / (6.0 * M5))
    wall = -2.0 * W - BETA * (omega - 1.0) ** 2 / 2.0
    acceleration_frame = geometry["a_x"] / geometry["E"] ** 0.5
    robin = (
        (_dcomponent(phi, 0) - ROBIN_Y * acceleration_frame) ** 2
        + _dcomponent(phi, 1) ** 2 + _dcomponent(phi, 2) ** 2
    )
    lagrangians = {
        "wall": wall,
        "K_foliation": MB2 * (geometry["Kij2"] - LAMBDA_K * geometry["Ktrace"] ** 2) / 2.0,
        "R": MB2 * XI * geometry["R3"] / 2.0,
        "R_squared": -MB2 * B4BAR * geometry["R3"] ** 2 / (32.0 * KINF**2),
        "a_squared": MB2 * ETA * geometry["a2"] / 2.0,
        "Robin": -KAPPA * robin / 2.0,
    }
    densities = {name: geometry["measure"] * term for name, term in lagrangians.items()}
    return {name: _torus_dual(value) for name, value in densities.items()}, densities


def _apply_component_mutation(name: str, component: Dual, mutation: str | None) -> Dual:
    if mutation == f"omit::{name}":
        return Dual.constant(0.0)
    if mutation == f"flip::{name}":
        return -component
    return component


def _dual_action(
    theta: np.ndarray,
    direction: np.ndarray,
    mutation: str | None = None,
    *,
    include_densities: bool = False,
) -> tuple[dict[str, Dual], dict[str, Dual]]:
    parameters = _dual_parameters(theta, direction)
    components: dict[str, Dual] = {}
    densities: dict[str, Dual] = {}
    for epsilon, side in ((1, "plus"), (-1, "minus")):
        bulk, bulk_density = _dual_bulk_side(parameters, epsilon, mutation)
        for sector, value in bulk.items():
            name = f"{sector}_bulk_{side}"
            components[name] = _apply_component_mutation(name, value, mutation)
            densities[name] = bulk_density[sector]
        ghy, ghy_density = _dual_ghy(parameters, epsilon, mutation)
        name = f"GHY_{side}"
        components[name] = _apply_component_mutation(name, ghy, mutation)
        densities[name] = ghy_density
    brane, brane_density = _dual_brane(parameters, mutation)
    for name, value in brane.items():
        components[name] = _apply_component_mutation(name, value, mutation)
        densities[name] = brane_density[name]
    total = Dual.constant(0.0)
    for value in components.values():
        total = total + value
    components["S_total"] = total
    if include_densities:
        total_density = Dual.constant(np.zeros((T_POINTS, X_POINTS), dtype=float))
        for value in densities.values():
            total_density = total_density + value
        densities["S_total"] = total_density
    return components, densities


# The functions below intentionally duplicate the selected action with plain
# arrays.  They do not call the dual route, so a wrong derivative rule in the
# first implementation cannot manufacture agreement with the FD oracle.
def _np_embedding(parameter: float, t: np.ndarray, x: np.ndarray) -> dict[str, np.ndarray]:
    profiles = _profiles(t, x)
    return {
        name: profiles[name] + parameter * profiles[f"d{name}"]
        for name in ("Y", "Y_t", "Y_x", "Y_tt", "Y_xx", "Y_tx")
    }


def _np_warp(q: np.ndarray, metric_parameter: float) -> dict[str, np.ndarray]:
    kappa = KINF * (1.0 + 0.12 * metric_parameter)
    radius = np.sqrt(q * q + WARP_CORE**2)
    A = -kappa * radius
    Aq = -kappa * q / radius
    Aqq = -kappa * WARP_CORE**2 / radius**3
    w = np.exp(A)
    return {"A": A, "Aq": Aq, "Aqq": Aqq, "w": w, "wq": Aq * w, "wqq": (Aqq + Aq * Aq) * w}


def _np_geometry(theta: np.ndarray, t: np.ndarray, x: np.ndarray, *, freeze_R: bool = False) -> dict[str, np.ndarray]:
    graph = _np_embedding(float(theta[0]), t, x)
    warp = _np_warp(graph["Y"], float(theta[1]))
    yt, yx = graph["Y_t"], graph["Y_x"]
    yxx, ytx = graph["Y_xx"], graph["Y_tx"]
    w = warp["w"]
    wx = warp["wq"] * yx
    wxx = warp["wqq"] * yx * yx + warp["wq"] * yxx
    E = w * w + yx * yx
    Ex = 2.0 * w * wx + 2.0 * yx * yxx
    D = E - yt * yt
    Dx = Ex - 2.0 * yt * ytx
    lapse = w * np.sqrt(D / E)
    measure = w**3 * np.sqrt(D)
    proper_wx = wx / np.sqrt(E)
    proper_wxx = wxx / E - wx * Ex / (2.0 * E * E)
    R3 = -4.0 * proper_wxx / w - 2.0 * (proper_wx / w) ** 2
    if freeze_R:
        reference = _np_geometry(THETA, t, x, freeze_R=False)["R3"] if not np.array_equal(theta, THETA) else R3
        R3 = np.asarray(reference)
    ax = warp["Aq"] * yx + 0.5 * Dx / D - 0.5 * Ex / E
    a2 = ax * ax / E
    Kxx = yt / lapse * (w * warp["wq"] - yxx + yx * Ex / (2.0 * E))
    Kyy = w**3 * warp["wq"] * yt / (E * lapse)
    kx, kp = Kxx / E, Kyy / (w * w)
    return {
        **graph, **warp, "E": E, "D": D, "N": lapse, "shift_x": yt * yx / E,
        "measure": measure, "R3": R3, "a_x": ax, "a2": a2,
        "Ktrace": kx + 2.0 * kp, "Kij2": kx * kx + 2.0 * kp * kp,
    }


def _np_vector_fields(
    q: np.ndarray, t: np.ndarray, x: np.ndarray, theta: np.ndarray, *, anisotropic_v4: bool = False,
) -> dict[str, np.ndarray]:
    po, pm, pa, pb = map(float, theta[2:])
    envelope = np.exp(-q * q / 9.0)
    f = 0.16 * envelope * np.cos(t) + 0.11 * np.sin(x) + 0.04 * q * np.sin(t + x) + 0.03 * np.cos(2.0 * t - x)
    ft = -0.16 * envelope * np.sin(t) + 0.04 * q * np.cos(t + x) - 0.06 * np.sin(2.0 * t - x)
    fx = 0.11 * np.cos(x) + 0.04 * q * np.cos(t + x) + 0.03 * np.sin(2.0 * t - x)
    fq = -0.32 * q * envelope * np.cos(t) / 9.0 + 0.04 * np.sin(t + x)
    omega = np.exp(po * f)
    logt, logx, logq = po * ft, po * fx, po * fq

    v = np.stack((
        0.72 + 0.11 * np.sin(t) + 0.045 * q + 0.018 * np.cos(t + x),
        0.28 * np.cos(x) + 0.065 * np.sin(q + t) + 0.025 * np.cos(t - x),
        0.24 * np.sin(t + x) + 0.052 * q * np.cos(x) + 0.021 * np.sin(2.0 * t - x),
    ), axis=-1)
    vt = np.stack((
        np.broadcast_to(0.11 * np.cos(t) - 0.018 * np.sin(t + x), q.shape),
        0.065 * np.cos(q + t) - 0.025 * np.sin(t - x),
        np.broadcast_to(0.24 * np.cos(t + x) + 0.042 * np.cos(2.0 * t - x), q.shape),
    ), axis=-1)
    vx = np.stack((
        np.broadcast_to(-0.018 * np.sin(t + x), q.shape),
        np.broadcast_to(-0.28 * np.sin(x) + 0.025 * np.sin(t - x), q.shape),
        0.24 * np.cos(t + x) - 0.052 * q * np.sin(x) - 0.021 * np.cos(2.0 * t - x),
    ), axis=-1)
    vq = np.stack((
        np.full(q.shape, 0.045), 0.065 * np.cos(q + t), np.broadcast_to(0.052 * np.cos(x), q.shape),
    ), axis=-1)

    def vec(items: tuple[Any, Any, Any]) -> np.ndarray:
        return np.stack(tuple(np.broadcast_to(item, q.shape) for item in items), axis=-1)

    At = pa * vec((0.12 * np.cos(x) + 0.035 * np.sin(q), 0.17 * np.sin(q) + 0.026 * np.cos(t), 0.08 * np.cos(t + x) + 0.031 * q))
    Ax = pa * vec((0.09 * np.sin(t) + 0.028 * q, -0.11 * np.cos(q) + 0.022 * np.sin(x), 0.14 * np.sin(t - x)))
    Aq = pa * vec((0.13 * np.cos(t) + 0.024 * np.sin(x), 0.07 * np.sin(x) + 0.019 * np.sin(q), -0.10 * np.cos(t + x)))
    Ay = pa * vec((0.05 * np.sin(q), 0.06 * np.cos(t), 0.08 * np.sin(x)))
    Az = pa * vec((-0.07 * np.cos(x), 0.04 * np.sin(q), 0.06 * np.cos(t)))
    At_t = pa * vec((0.0, -0.026 * np.sin(t), -0.08 * np.sin(t + x)))
    At_x = pa * vec((-0.12 * np.sin(x), 0.0, -0.08 * np.sin(t + x)))
    At_q = pa * vec((0.035 * np.cos(q), 0.17 * np.cos(q), 0.031))
    Ax_t = pa * vec((0.09 * np.cos(t), 0.0, 0.14 * np.cos(t - x)))
    Ax_x = pa * vec((0.0, 0.022 * np.cos(x), -0.14 * np.cos(t - x)))
    Ax_q = pa * vec((0.028, 0.11 * np.sin(q), 0.0))
    Aq_t = pa * vec((-0.13 * np.sin(t), 0.0, 0.10 * np.sin(t + x)))
    Aq_x = pa * vec((0.024 * np.cos(x), 0.07 * np.cos(x), 0.10 * np.sin(t + x)))

    scale = pm * omega[..., None] ** -1.5
    phi = scale * v
    phi_t = scale * (vt - 1.5 * v * logt[..., None])
    phi_x = scale * (vx - 1.5 * v * logx[..., None])
    phi_q = scale * (vq - 1.5 * v * logq[..., None])
    Pt = phi_t + np.cross(At, phi) + 1.5 * phi * logt[..., None]
    Px = phi_x + np.cross(Ax, phi) + 1.5 * phi * logx[..., None]
    Pq = phi_q + np.cross(Aq, phi) + 1.5 * phi * logq[..., None]
    Py, Pz = np.cross(Ay, phi), np.cross(Az, phi)
    Ftx = Ax_t - At_x + np.cross(At, Ax)
    Ftq = Aq_t - At_q + np.cross(At, Aq)
    Fxq = Aq_x - Ax_q + np.cross(Ax, Aq)
    Byzq = pb * vec((0.20 + 0.03 * np.sin(t), -0.17 * np.cos(x), 0.11 * np.sin(t + x + q)))
    Bxyz = pb * vec((0.07 * np.cos(q), 0.09 * np.sin(t), -0.08 * np.cos(x)))
    Btyz = pb * vec((-0.06 * np.sin(q), 0.05 * np.cos(t + x), 0.10 * np.sin(x)))
    radial = omega**1.5 * np.linalg.norm(phi, axis=-1)
    V4 = radial**4 / (2.0 * np.sqrt(1.0 + radial**4))
    if anisotropic_v4:
        V4 = V4 + 0.07 * phi[..., 0]
    return {
        "omega": omega, "logt": logt, "logx": logx, "logq": logq,
        "phi": phi, "Pt": Pt, "Px": Px, "Pq": Pq, "Py": Py, "Pz": Pz,
        "At": At, "Ax": Ax, "Aq": Aq, "Ay": Ay, "Az": Az,
        "Ftx": Ftx, "Ftq": Ftq, "Fxq": Fxq,
        "Byzq": Byzq, "Bxyz": Bxyz, "Btyz": Btyz, "V4": V4,
    }


def _np_bulk_densities(q: np.ndarray, t: np.ndarray, x: np.ndarray, theta: np.ndarray, *, anisotropic_v4: bool = False) -> dict[str, np.ndarray]:
    warp = _np_warp(q, float(theta[1]))
    fields = _np_vector_fields(q, t, x, theta, anisotropic_v4=anisotropic_v4)
    w, omega = warp["w"], fields["omega"]
    R5 = -8.0 * warp["Aqq"] - 20.0 * warp["Aq"] ** 2
    ot, ox, oq = omega * fields["logt"], omega * fields["logx"], omega * fields["logq"]
    omega2 = (-ot * ot + ox * ox) / w**2 + oq * oq
    W = 3.0 * M5 * KINF * np.exp(-GCOMP * omega**2 / (6.0 * M5))
    W_Omega = -GCOMP * omega * W / (3.0 * M5)
    U = W_Omega**2 / (2.0 * GCOMP) - 2.0 * W**2 / (3.0 * M5)
    squared = lambda value: np.sum(value * value, axis=-1)
    P2 = (-squared(fields["Pt"]) + squared(fields["Px"]) + squared(fields["Py"]) + squared(fields["Pz"])) / w**2 + squared(fields["Pq"])
    BF = (
        np.sum(fields["Byzq"] * fields["Ftx"], axis=-1)
        - np.sum(fields["Bxyz"] * fields["Ftq"], axis=-1)
        + np.sum(fields["Btyz"] * fields["Fxq"], axis=-1)
    )
    return {
        "EH": w**4 * M5 * R5 / 2.0,
        "Omega_kinetic": -w**4 * GCOMP * omega2 / 2.0,
        "Omega_potential": -w**4 * U,
        "P_kinetic": -w**4 * Z5 * P2 / 2.0,
        "full_V4": -w**4 * Z5 * MASS**2 * omega**-5.0 * fields["V4"],
        "BF": BF,
    }


def _np_action(theta: np.ndarray, mutation: str | None = None, *, include_densities: bool = False) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    theta = np.asarray(theta, dtype=float)
    t, x = _grid()
    graph = _np_embedding(float(theta[0]), t, x)
    rho, weights = _quadrature()
    chi, chi_rho = _chi(rho)
    components: dict[str, float] = {}
    densities: dict[str, np.ndarray] = {}
    for epsilon, side in ((1, "plus"), (-1, "minus")):
        q = epsilon * rho[:, None, None] + chi[:, None, None] * graph["Y"]
        jacobian = 1.0 + epsilon * chi_rho[:, None, None] * graph["Y"]
        if mutation == "broken_pullback_jacobian":
            jacobian = np.ones_like(q)
        bare = _np_bulk_densities(q, t[None, :, :], x[None, :, :], theta, anisotropic_v4=mutation == "anisotropic_V4")
        for sector, value in bare.items():
            radial = np.sum(weights[:, None, None] * jacobian * value, axis=0)
            name = f"{sector}_bulk_{side}"
            result = _torus_np(radial)
            if mutation == f"omit::{name}": result = 0.0
            if mutation == f"flip::{name}": result = -result
            components[name], densities[name] = result, radial

        geometry = _np_geometry(theta, t, x)
        sigma = -float(epsilon)
        if mutation == "wrong_GHY_orientation" and epsilon == -1: sigma = -1.0
        numerator = (
            geometry["wq"] * (4.0 * geometry["w"]**2 + 5.0 * (geometry["Y_x"]**2 - geometry["Y_t"]**2))
            + (geometry["Y_tt"] * (geometry["w"]**2 + geometry["Y_x"]**2)
               - geometry["Y_xx"] * (geometry["w"]**2 - geometry["Y_t"]**2)
               - 2.0 * geometry["Y_t"] * geometry["Y_x"] * geometry["Y_tx"]) / geometry["w"]
        )
        density = M5 * sigma * geometry["w"]**3 * numerator / geometry["D"]
        name = f"GHY_{side}"
        result = _torus_np(density)
        if mutation == f"omit::{name}": result = 0.0
        if mutation == f"flip::{name}": result = -result
        components[name], densities[name] = result, density

    geometry = _np_geometry(theta, t, x, freeze_R=mutation == "freeze_R")
    trace = _np_vector_fields(geometry["Y"], t, x, theta)
    omega, phi = trace["omega"], trace["phi"]
    W = 3.0 * M5 * KINF * np.exp(-GCOMP * omega**2 / (6.0 * M5))
    robin = (phi[..., 0] - ROBIN_Y * geometry["a_x"] / np.sqrt(geometry["E"]))**2 + phi[..., 1]**2 + phi[..., 2]**2
    lagrangians = {
        "wall": -2.0 * W - BETA * (omega - 1.0)**2 / 2.0,
        "K_foliation": MB2 * (geometry["Kij2"] - LAMBDA_K * geometry["Ktrace"]**2) / 2.0,
        "R": MB2 * XI * geometry["R3"] / 2.0,
        "R_squared": -MB2 * B4BAR * geometry["R3"]**2 / (32.0 * KINF**2),
        "a_squared": MB2 * ETA * geometry["a2"] / 2.0,
        "Robin": -KAPPA * robin / 2.0,
    }
    for name, term in lagrangians.items():
        density = geometry["measure"] * term
        result = _torus_np(density)
        if mutation == f"omit::{name}": result = 0.0
        if mutation == f"flip::{name}": result = -result
        components[name], densities[name] = result, density
    components["S_total"] = float(sum(components.values()))
    if include_densities:
        densities["S_total"] = sum(densities.values(), np.zeros((T_POINTS, X_POINTS), dtype=float))
    return components, densities


AUDIT_DIRECTION = np.asarray([0.31, -0.27, 0.23, 0.37, -0.19, 0.29], dtype=float)


@lru_cache(maxsize=1)
def component_jvp_fd_certificate() -> dict[str, Any]:
    directions = {f"basis_{name}": np.eye(len(PARAMETER_NAMES))[i] for i, name in enumerate(PARAMETER_NAMES)}
    directions["coupled_audit"] = AUDIT_DIRECTION
    rows: dict[str, Any] = {}
    maximum_error = 0.0
    minimum_activity = math.inf
    value_route_error = 0.0
    for label, direction in directions.items():
        dual, _ = _dual_action(THETA, direction)
        plus, _ = _np_action(THETA + FD_STEP * direction)
        minus, _ = _np_action(THETA - FD_STEP * direction)
        nominal, _ = _np_action(THETA)
        component_rows: dict[str, Any] = {}
        for name in nominal:
            jvp = float(dual[name].dot)
            finite = float((plus[name] - minus[name]) / (2.0 * FD_STEP))
            error = abs(jvp - finite)
            value_error = abs(float(dual[name].value) - nominal[name])
            component_rows[name] = {
                "dual_action_value": float(dual[name].value),
                "plain_numpy_action_value": nominal[name],
                "runtime_dual_JVP": jvp,
                "independent_central_FD": finite,
                "absolute_JVP_error": error,
                "absolute_value_route_error": value_error,
            }
            maximum_error = max(maximum_error, error)
            value_route_error = max(value_route_error, value_error)
            if label == "coupled_audit" and name != "S_total":
                minimum_activity = min(minimum_activity, abs(jvp))
        rows[label] = {"direction": direction.tolist(), "components": component_rows}
    return {
        "parameter_order": list(PARAMETER_NAMES),
        "theta": THETA.tolist(),
        "central_step": FD_STEP,
        "raw_rows": rows,
        "maximum_component_JVP_error": maximum_error,
        "maximum_component_value_route_error": value_route_error,
        "minimum_absolute_coupled_component_JVP": minimum_activity,
        "routes_share_action_helper": False,
    }


MIXED_PROBES = (
    ("EH_embedding_metric", "EH_bulk_plus", 0, 1),
    ("Omega_kinetic_embedding_Omega", "Omega_kinetic_bulk_plus", 0, 2),
    ("Omega_potential_metric_Omega", "Omega_potential_bulk_minus", 1, 2),
    ("P_Omega_matter", "P_kinetic_bulk_plus", 2, 3),
    ("P_matter_connection", "P_kinetic_bulk_minus", 3, 4),
    ("V4_Omega_matter", "full_V4_bulk_plus", 2, 3),
    ("BF_connection_B", "BF_bulk_plus", 4, 5),
    ("GHY_embedding_metric", "GHY_plus", 0, 1),
    ("wall_embedding_Omega", "wall", 0, 2),
    ("foliation_K_embedding_metric", "K_foliation", 0, 1),
    ("intrinsic_R_embedding_metric", "R", 0, 1),
    ("intrinsic_R2_embedding_metric", "R_squared", 0, 1),
    ("acceleration_embedding_metric", "a_squared", 0, 1),
    ("Robin_embedding_matter", "Robin", 0, 3),
)


@lru_cache(maxsize=1)
def mixed_cross_term_certificate() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    maximum_error = 0.0
    minimum_activity = math.inf
    basis = np.eye(len(PARAMETER_NAMES))
    h = MIXED_STEP
    for label, component, i, j in MIXED_PROBES:
        dual_plus, _ = _dual_action(THETA + h * basis[j], basis[i])
        dual_minus, _ = _dual_action(THETA - h * basis[j], basis[i])
        dual_mixed = float((dual_plus[component].dot - dual_minus[component].dot) / (2.0 * h))
        pp, _ = _np_action(THETA + h * basis[i] + h * basis[j])
        pm, _ = _np_action(THETA + h * basis[i] - h * basis[j])
        mp, _ = _np_action(THETA - h * basis[i] + h * basis[j])
        mm, _ = _np_action(THETA - h * basis[i] - h * basis[j])
        fd_mixed = float((pp[component] - pm[component] - mp[component] + mm[component]) / (4.0 * h * h))
        error = abs(dual_mixed - fd_mixed)
        activity = max(abs(dual_mixed), abs(fd_mixed))
        rows[label] = {
            "action_component": component,
            "first_parameter": PARAMETER_NAMES[i],
            "second_parameter": PARAMETER_NAMES[j],
            "dual_JVP_then_independent_parameter_FD": dual_mixed,
            "plain_action_four_corner_FD": fd_mixed,
            "absolute_error": error,
            "absolute_activity": activity,
        }
        maximum_error = max(maximum_error, error)
        minimum_activity = min(minimum_activity, activity)
    return {
        "mixed_step": h,
        "raw_cross_terms": rows,
        "maximum_cross_route_error": maximum_error,
        "minimum_absolute_cross_term": minimum_activity,
        "scope": "displayed finite six-parameter tangent basis only",
    }


def _spectral_derivative(values: np.ndarray, axis: int) -> np.ndarray:
    points = values.shape[axis]
    frequencies = np.fft.fftfreq(points, d=1.0 / points)
    shape = [1] * values.ndim
    shape[axis] = points
    return np.fft.ifft(1j * frequencies.reshape(shape) * np.fft.fft(values, axis=axis), axis=axis).real


@lru_cache(maxsize=1)
def internal_so3_ward_certificate() -> dict[str, Any]:
    """Bulk P/V4/BF orbit sanity plus the omitted-Robin obstruction."""

    t, x = _grid()
    q = 0.23 + 0.08 * np.sin(t) - 0.05 * np.cos(x)
    fields = _np_vector_fields(q, t, x, THETA)
    warp = _np_warp(q, float(THETA[1]))
    omega, w = fields["omega"], warp["w"]
    brane_geometry = _np_geometry(THETA, t, x)
    brane_fields = _np_vector_fields(brane_geometry["Y"], t, x, THETA)
    brane_acceleration = brane_geometry["a_x"] / np.sqrt(brane_geometry["E"])
    robin_displacement = brane_fields["phi"].copy()
    robin_displacement[..., 0] -= ROBIN_Y * brane_acceleration
    rows: dict[str, Any] = {}
    max_residual = 0.0
    max_robin_obstruction = 0.0
    anisotropic_witness = 0.0
    omitted_bf_witness = 0.0
    for generator in range(3):
        profile = 0.43 + 0.17 * np.sin((generator + 1) * t) + 0.11 * np.cos(x + generator)
        lam = np.zeros(q.shape + (3,), dtype=float)
        lam[..., generator] = profile
        dphi = np.cross(lam, fields["phi"])
        p_variation = (
            (-np.sum(fields["Pt"] * np.cross(lam, fields["Pt"]), axis=-1)
             + np.sum(fields["Px"] * np.cross(lam, fields["Px"]), axis=-1)
             + np.sum(fields["Py"] * np.cross(lam, fields["Py"]), axis=-1)
             + np.sum(fields["Pz"] * np.cross(lam, fields["Pz"]), axis=-1)) / w**2
            + np.sum(fields["Pq"] * np.cross(lam, fields["Pq"]), axis=-1)
        )
        p_term = -Z5 * w**4 * p_variation
        radial_variation = omega**1.5 * np.sum(fields["phi"] * dphi, axis=-1) / np.linalg.norm(fields["phi"], axis=-1)
        v4_term = -Z5 * MASS**2 * w**4 * omega**-5.0 * radial_variation
        bf_B = (
            np.sum(np.cross(lam, fields["Byzq"]) * fields["Ftx"], axis=-1)
            - np.sum(np.cross(lam, fields["Bxyz"]) * fields["Ftq"], axis=-1)
            + np.sum(np.cross(lam, fields["Btyz"]) * fields["Fxq"], axis=-1)
        )
        bf_F = (
            np.sum(fields["Byzq"] * np.cross(lam, fields["Ftx"]), axis=-1)
            - np.sum(fields["Bxyz"] * np.cross(lam, fields["Ftq"]), axis=-1)
            + np.sum(fields["Btyz"] * np.cross(lam, fields["Fxq"]), axis=-1)
        )
        residual = p_term + v4_term + bf_B + bf_F
        anisotropic = -0.07 * Z5 * MASS**2 * w**4 * omega**-5.0 * dphi[..., 0]
        brane_dphi = np.cross(lam, brane_fields["phi"])
        robin_variation = (
            -KAPPA
            * brane_geometry["measure"]
            * np.sum(robin_displacement * brane_dphi, axis=-1)
        )
        robin_integral = _torus_np(robin_variation)
        robin_linf = float(np.max(np.abs(robin_variation)))
        rows[f"T_{generator + 1}"] = {
            "P_material_variation_integral": _torus_np(p_term),
            "radial_V4_variation_integral": _torus_np(v4_term),
            "BF_delta_B_integral": _torus_np(bf_B),
            "BF_delta_F_integral": _torus_np(bf_F),
            "bulk_total_integral_residual": _torus_np(residual),
            "bulk_local_Linf_residual": float(np.max(np.abs(residual))),
            "Robin_orbit_variation_integral": robin_integral,
            "Robin_orbit_variation_Linf": robin_linf,
            "anisotropic_V4_mutant_integral": _torus_np(anisotropic),
            "omit_delta_B_BF_mutant_integral": _torus_np(bf_F),
        }
        max_residual = max(max_residual, float(np.max(np.abs(residual))), abs(_torus_np(residual)))
        max_robin_obstruction = max(max_robin_obstruction, abs(robin_integral), robin_linf)
        anisotropic_witness = max(anisotropic_witness, abs(_torus_np(anisotropic)), float(np.max(np.abs(anisotropic))))
        omitted_bf_witness = max(omitted_bf_witness, abs(_torus_np(bf_F)), float(np.max(np.abs(bf_F))))
    return {
        "convention": "delta_lambda A=-D_A lambda; delta_lambda phi=lambda cross phi; delta_lambda B=lambda cross B",
        "scope": "selected bulk P/V4/BF orbit algebra only; not the complete same-action SO3 Ward",
        "bulk_probe_off_shell": True,
        "Euler_equations_imposed": False,
        "generator_rows": rows,
        "maximum_bulk_nominal_residual": max_residual,
        "maximum_Robin_orbit_obstruction": max_robin_obstruction,
        "complete_same_action_SO3_orbit_claimed": False,
        "complete_same_action_SO3_Ward_claimed": False,
        "anisotropic_V4_mutant_witness": anisotropic_witness,
        "omit_one_BF_orbit_contribution_witness": omitted_bf_witness,
        "Robin_obstruction_interpretation": (
            "With the implemented fixed internal-axis identification of varphi_H, the declared delta_phi orbit "
            "does not leave Robin invariant. A compensating frame/groupoid map is not implemented."
        ),
        "boundary_parameter": "BV-BFV/interface and compensating frame transformations remain open",
    }


@lru_cache(maxsize=1)
def intrinsic_diffeomorphism_ward_certificate() -> dict[str, Any]:
    """Intrinsic torus Ward, kept distinct from the internal SO(3) Ward."""

    _, densities = _np_action(THETA, include_densities=True)
    total = densities["S_total"]
    t, x = _grid()
    probes = (
        (0.19 * np.sin(t) * np.cos(x), 0.13 * np.cos(t) * np.sin(2.0 * x)),
        (0.17 * np.sin(2.0 * t - x), -0.11 * np.cos(t + x)),
    )
    rows = {}
    nominal_max = 0.0
    mutant_min = math.inf
    for index, (xi_t, xi_x) in enumerate(probes):
        divergence = _spectral_derivative(xi_t * total, 0) + _spectral_derivative(xi_x * total, 1)
        advective_mutant = xi_t * _spectral_derivative(total, 0) + xi_x * _spectral_derivative(total, 1)
        nominal = _torus_np(divergence)
        mutant = _torus_np(advective_mutant)
        rows[f"xi_{index}"] = {
            "raw_interior_divergence_integral": nominal,
            "raw_interior_divergence_Linf": float(np.max(np.abs(divergence))),
            "eight_face_balance_consumed_from_upstream": False,
            "omit_density_weight_mutant_integral": mutant,
        }
        nominal_max = max(nominal_max, abs(nominal))
        mutant_min = min(mutant_min, abs(mutant))
    return {
        "Ward": "delta_xi L=d(i_xi L) for the directly recomputed selected-family total density",
        "khronon": "T=t is transported as a scalar in this selected slice; arbitrary moving T remains open",
        "raw_probe_rows": rows,
        "maximum_integrated_interior_residual": nominal_max,
        "minimum_advective_only_mutant_witness": mutant_min,
        "interface_residue": "not forced to zero; the byte-pinned v5.5.4 eight-face lemma remains separate",
        "BV_BFV_interface_obligation_open": True,
    }


@lru_cache(maxsize=1)
def field_activity_certificate() -> dict[str, Any]:
    t, x = _grid()
    q = 0.21 + 0.07 * np.sin(t) - 0.04 * np.cos(x)
    fields = _np_vector_fields(q, t, x, THETA)
    commutator = np.cross(fields["At"], fields["Ax"])
    derivative_only_Ftx = fields["Ftx"] - commutator
    norms = lambda value: float(np.max(np.linalg.norm(value, axis=-1)))
    return {
        "F_tx_max_norm": norms(fields["Ftx"]),
        "F_tq_max_norm": norms(fields["Ftq"]),
        "F_xq_max_norm": norms(fields["Fxq"]),
        "B_yzq_max_norm": norms(fields["Byzq"]),
        "B_xyz_max_norm": norms(fields["Bxyz"]),
        "B_tyz_max_norm": norms(fields["Btyz"]),
        "nonabelian_At_cross_Ax_max_norm": norms(commutator),
        "abelianized_Ftx_mutant_witness": norms(fields["Ftx"] - derivative_only_Ftx),
        "P_t_max_norm": norms(fields["Pt"]),
        "P_x_max_norm": norms(fields["Px"]),
        "P_y_max_norm": norms(fields["Py"]),
        "P_z_max_norm": norms(fields["Pz"]),
        "P_q_max_norm": norms(fields["Pq"]),
        "ordinary_coordinate_dependence": {
            "t": True, "x": True, "y": False, "z": False, "q": True,
        },
        "five_covariant_components_active": True,
        "all_five_ordinary_coordinate_derivatives_active": False,
        "full_5D_coordinate_family_claimed": False,
    }


@lru_cache(maxsize=1)
def normal_flux_and_matter_shift_certificate() -> dict[str, Any]:
    """Visible nonzero normal/interface slots; not a full Green theorem."""

    t, x = _grid()
    geometry = _np_geometry(THETA, t, x)
    fields = _np_vector_fields(geometry["Y"], t, x, THETA)
    w, D = geometry["w"], geometry["D"]
    root_D = np.sqrt(D)
    delta_omega = 0.07 * np.cos(t) + 0.03 * np.sin(x)
    delta_phi = np.stack((0.04 * np.sin(t), 0.05 * np.cos(x), 0.03 * np.sin(t + x)), axis=-1)
    delta_At = np.stack((0.02 * np.cos(x), 0.03 * np.sin(t), 0.025 * np.cos(t + x)), axis=-1)
    delta_Ax = np.stack((0.031 * np.sin(x), -0.027 * np.cos(t), 0.022 * np.sin(t - x)), axis=-1)
    b_tyz = fields["Btyz"] + geometry["Y_t"][..., None] * fields["Byzq"]
    b_xyz = fields["Bxyz"] + geometry["Y_x"][..., None] * fields["Byzq"]
    bf_pair = np.sum(b_tyz * delta_Ax - b_xyz * delta_At, axis=-1)
    sides: dict[str, Any] = {}
    omission_witnesses: dict[str, float] = {}
    for epsilon, side in ((1, "plus"), (-1, "minus")):
        sigma = -float(epsilon)
        nt = sigma * geometry["Y_t"] / (w * root_D)
        nx = -sigma * geometry["Y_x"] / (w * root_D)
        nq = sigma * w / root_D
        nP = nt[..., None] * fields["Pt"] + nx[..., None] * fields["Px"] + nq[..., None] * fields["Pq"]
        nOmega = fields["omega"] * (nt * fields["logt"] + nx * fields["logx"] + nq * fields["logq"])
        pi_omega = GCOMP * nOmega + 3.0 * Z5 * np.sum(fields["phi"] * nP, axis=-1) / (2.0 * fields["omega"])
        pi_phi = Z5 * nP
        omega_pair = _torus_np(geometry["measure"] * pi_omega * delta_omega)
        phi_pair = _torus_np(geometry["measure"] * np.sum(pi_phi * delta_phi, axis=-1))
        bf_oriented_pair = float(epsilon) * _torus_np(bf_pair)
        sides[side] = {
            "Pi_Omega_L2": float(np.sqrt(np.mean(pi_omega**2))),
            "Pi_phi_L2": float(np.sqrt(np.mean(np.sum(pi_phi**2, axis=-1)))),
            "pulled_B_tyz_L2": float(np.sqrt(np.mean(np.sum(b_tyz**2, axis=-1)))),
            "pulled_B_xyz_L2": float(np.sqrt(np.mean(np.sum(b_xyz**2, axis=-1)))),
            "Omega_boundary_pairing": omega_pair,
            "phi_boundary_pairing": phi_pair,
            "BF_boundary_pairing": bf_oriented_pair,
        }
        omission_witnesses[f"omit_Pi_Omega_{side}"] = abs(omega_pair)
        omission_witnesses[f"omit_Pi_phi_{side}"] = abs(phi_pair)
        omission_witnesses[f"omit_BF_pullback_{side}"] = abs(bf_oriented_pair)

    # Local ADM algebra sanity for the visible E_shift^matter=-T_ui/N slot.
    # This is not an independent variation of the complete pulled-back action.
    i, j = 4, 7
    N = float(geometry["N"][i, j])
    beta = np.asarray([geometry["shift_x"][i, j], 0.0, 0.0], dtype=float)
    h = np.diag([geometry["E"][i, j], w[i, j] ** 2, w[i, j] ** 2])
    gamma = np.empty((4, 4), dtype=float)
    gamma[1:, 1:] = h
    gamma[0, 1:] = gamma[1:, 0] = h @ beta
    gamma[0, 0] = -N * N + float(beta @ h @ beta)
    p_cov = np.stack((
        fields["Pt"][i, j] + geometry["Y_t"][i, j] * fields["Pq"][i, j],
        fields["Px"][i, j] + geometry["Y_x"][i, j] * fields["Pq"][i, j],
        fields["Py"][i, j], fields["Pz"][i, j],
    ))
    p_q = fields["Pq"][i, j]
    root_D_sample = math.sqrt(float(geometry["D"][i, j]))
    p_normal = (
        geometry["Y_t"][i, j] * fields["Pt"][i, j] / (w[i, j] * root_D_sample)
        - geometry["Y_x"][i, j] * fields["Px"][i, j] / (w[i, j] * root_D_sample)
        + w[i, j] * p_q / root_D_sample
    )
    inverse = np.linalg.inv(gamma)
    p_up = inverse @ p_cov
    tangential_p2 = float(np.einsum("mn,ma,na->", inverse, p_cov, p_cov))
    p2 = tangential_p2 + float(p_normal @ p_normal)
    ambient_p2 = float(
        (
            -fields["Pt"][i, j] @ fields["Pt"][i, j]
            + fields["Px"][i, j] @ fields["Px"][i, j]
            + fields["Py"][i, j] @ fields["Py"][i, j]
            + fields["Pz"][i, j] @ fields["Pz"][i, j]
        ) / w[i, j] ** 2
        + p_q @ p_q
    )
    legacy_raw_pq_p2 = tangential_p2 + float(p_q @ p_q)
    local_potential = float(Z5 * MASS**2 * fields["omega"][i, j] ** -5.0 * fields["V4"][i, j])
    lagrangian = -0.5 * Z5 * p2 - local_potential
    stress = Z5 * np.einsum("ma,na->mn", p_up, p_up) + lagrangian * inverse
    u_cov = np.asarray([-N, 0.0, 0.0, 0.0])
    T_ui = np.asarray(u_cov @ stress @ gamma[:, 1:], dtype=float)
    predicted = -T_ui / N

    def matter_action(beta_trial: np.ndarray) -> float:
        gamma_trial = np.empty((4, 4), dtype=float)
        gamma_trial[1:, 1:] = h
        gamma_trial[0, 1:] = gamma_trial[1:, 0] = h @ beta_trial
        gamma_trial[0, 0] = -N * N + float(beta_trial @ h @ beta_trial)
        inv = np.linalg.inv(gamma_trial)
        kinetic = float(np.einsum("mn,ma,na->", inv, p_cov, p_cov) + p_normal @ p_normal)
        return N * math.sqrt(float(np.linalg.det(h))) * (-0.5 * Z5 * kinetic - local_potential)

    step = 2.0e-5
    numerical = []
    for axis in range(3):
        e = np.eye(3)[axis]
        derivative = (
            -matter_action(beta + 2.0 * step * e) + 8.0 * matter_action(beta + step * e)
            - 8.0 * matter_action(beta - step * e) + matter_action(beta - 2.0 * step * e)
        ) / (12.0 * step)
        numerical.append(derivative / (N * math.sqrt(float(np.linalg.det(h)))))
    numerical_array = np.asarray(numerical)
    return {
        "normal_slot_rows": sides,
        "normal_slot_omission_mutant_witnesses": omission_witnesses,
        "minimum_normal_slot_omission_witness": min(omission_witnesses.values()),
        "matter_shift": {
            "sample_grid_index": [i, j],
            "normal_component": "n^M P_M",
            "P2_decomposition": {
                "ambient_P2": ambient_p2,
                "orthogonal_ADM_P2": p2,
                "absolute_orthogonal_decomposition_error": abs(p2 - ambient_p2),
                "legacy_raw_Pq_ADM_P2": legacy_raw_pq_p2,
                "legacy_raw_Pq_decomposition_error": abs(legacy_raw_pq_p2 - ambient_p2),
            },
            "T_ui": T_ui.tolist(),
            "T_ui_norm": float(np.linalg.norm(T_ui)),
            "local_covariant_prediction_minus_Tui_over_N": predicted.tolist(),
            "same_local_formula_ADM_shift_FD": numerical_array.tolist(),
            "local_identity_maximum_error": float(np.max(np.abs(predicted - numerical_array))),
            "T_ui_activity_witness": float(np.max(np.abs(numerical_array))),
            "independent_same_action_variational_route_supplied": False,
        },
        "normal_slots_visible_as_accounting_diagnostics": True,
        "complete_normal_and_matter_shift_certificate": False,
        "full_Euler_Green_identity_claimed": False,
        "missing_for_full_Green": [
            "independently derived bulk Euler density for every v5.2 field",
            "one equality between that Euler bulk pairing plus all boundary slots and the total action JVP",
            "arbitrary compactly supported variations and continuum limit",
        ],
    }


@lru_cache(maxsize=1)
def route_separation_certificate() -> dict[str, Any]:
    """Static code-path separation diagnostic; never an independence proof."""

    numpy_functions = (_np_action, _np_bulk_densities, _np_vector_fields, _np_geometry, _np_warp, _np_embedding)
    dual_functions = (_dual_action, _dual_bulk_side, _dual_bulk_densities, _dual_vector_fields, _dual_geometry, _dual_warp, _dual_embedding)
    numpy_source = "\n".join(inspect.getsource(function) for function in numpy_functions)
    dual_source = "\n".join(inspect.getsource(function) for function in dual_functions)
    ast.parse(numpy_source)
    ast.parse(dual_source)
    forbidden_numpy = sorted(name for name in ("_dual_action", "_dual_bulk_side", "Dual") if name in numpy_source)
    forbidden_dual = sorted(name for name in ("_np_action", "_np_bulk_densities") if name in dual_source)
    return {
        "plain_route_forbidden_references": forbidden_numpy,
        "dual_route_forbidden_references": forbidden_dual,
        "symbolically_separate_codepaths": not forbidden_numpy and not forbidden_dual,
        "independent_assemblies": False,
        "independence_claimed": False,
        "shared_infrastructure": ["profiles", "grid", "quadrature", "coefficients", "selected action formulas"],
        "upstream_helpers_imported": [],
        "upstream_decisions_or_residuals_read": False,
        "circular_expected_JVP_mutant_rejected": False,
        "classification": "route-separation diagnostic only; correlated formula errors remain possible",
    }


@lru_cache(maxsize=1)
def mutant_certificate() -> dict[str, Any]:
    nominal, _ = _dual_action(THETA, AUDIT_DIRECTION)
    nominal_total = float(nominal["S_total"].dot)
    component_names = tuple(name for name in nominal if name != "S_total")
    omissions: dict[str, float] = {}
    sign_flips: dict[str, float] = {}
    for name in component_names:
        omitted, _ = _dual_action(THETA, AUDIT_DIRECTION, f"omit::{name}")
        flipped, _ = _dual_action(THETA, AUDIT_DIRECTION, f"flip::{name}")
        omissions[name] = abs(float(omitted["S_total"].dot) - nominal_total)
        sign_flips[name] = abs(float(flipped["S_total"].dot) - nominal_total)
    special: dict[str, float] = {}
    for mutation in ("broken_pullback_jacobian", "wrong_GHY_orientation", "freeze_R", "anisotropic_V4"):
        changed, _ = _dual_action(THETA, AUDIT_DIRECTION, mutation)
        special[mutation] = abs(float(changed["S_total"].dot) - nominal_total)
    frozen_direction = AUDIT_DIRECTION.copy()
    frozen_direction[0] = 0.0
    frozen, _ = _dual_action(THETA, frozen_direction)
    special["frozen_moving_embedding"] = abs(float(frozen["S_total"].dot) - nominal_total)
    fields = field_activity_certificate()
    flux = normal_flux_and_matter_shift_certificate()
    special["abelianize_commutators"] = fields["abelianized_Ftx_mutant_witness"]
    special["remove_T_ui_matter"] = flux["matter_shift"]["T_ui_activity_witness"]
    special["circular_expected_route"] = 0.0
    for name, value in flux["normal_slot_omission_mutant_witnesses"].items():
        special[name] = value
    return {
        "audit_direction": AUDIT_DIRECTION.tolist(),
        "nominal_total_JVP": nominal_total,
        "omit_each_action_contribution_witnesses": omissions,
        "flip_each_action_contribution_witnesses": sign_flips,
        "special_mutant_witnesses": special,
        "minimum_omission_witness": min(omissions.values()),
        "minimum_sign_flip_witness": min(sign_flips.values()),
        "minimum_special_witness": min(special.values()),
        "mutant_expected_route_is_nominal_independent_route": False,
        "independent_mutant_oracle_supplied": False,
        "primary_mutant_suite_complete": False,
        "classification": (
            "component activity/accounting diagnostics only; omit/flip witnesses are algebraic changes "
            "to the nominal assembly and do not establish mutation adequacy"
        ),
    }


FAIL_CLOSED_KEYS = (
    "independent_redteam_replication_complete",
    "internal_SO3_direct_orbit_diagnostic_pass",
    "selected_normal_slots_and_matter_shift_visible_pass",
    "primary_mutant_suite_pass",
    "v5_6_2_selected_family_primary_candidate_pass",
    "all_five_ordinary_coordinate_directions_active_pass",
    "same_action_independent_Euler_Green_identity_pass",
    "same_action_internal_SO3_Euler_Ward_rederived_pass",
    "full_bulk_diffeomorphism_Ward_pass",
    "complete_moving_embedding_Ward_pass",
    "continuum_all_configurations_theorem_pass",
    "full_classical_variational_principle_selected_sector_pass",
    "C1_ACTION_selected_family_pass",
    "N1_ACTION_selected_family_pass",
    "C1_ACTION_pass",
    "N1_ACTION_pass",
    "complete_BV_BFV_boundary_complex_pass",
    "unrestricted_large_gauge_sector_pass",
    "deterministic_freeze_receipt_issued",
    "B4_pass",
    "B5_pass",
    "publication_authorized",
)

ALLOWED_TRUE_PASS_KEYS = frozenset((
    "all_upstream_bytes_and_literal_action_pinned_pass",
    "selected_moving_family_action_JVP_FD_pass",
    "selected_mixed_cross_terms_runtime_pass",
    "selected_nonabelian_BF_activity_pass",
    "selected_bulk_P_V4_BF_orbit_sanity_pass",
    "intrinsic_periodic_density_divergence_diagnostic_pass",
))


def _geometry_summary() -> dict[str, Any]:
    t, x = _grid()
    geometry = _np_geometry(THETA, t, x)
    return {
        "minimum_timelike_D": float(np.min(geometry["D"])),
        "maximum_abs_graph_velocity": float(np.max(np.abs(geometry["Y_t"]))),
        "maximum_abs_graph_slope": float(np.max(np.abs(geometry["Y_x"]))),
        "embedding_parameter_derivative_Linf": float(np.max(np.abs(_profiles(t, x)["dY"]))),
        "intrinsic_R_Linf": float(np.max(np.abs(geometry["R3"]))),
        "foliation_K_Linf": float(np.max(np.abs(geometry["Ktrace"]))),
        "ambient_warp_is_prescribed_not_solved": True,
    }


def build_payload() -> dict[str, Any]:
    # Recheck bytes at build time; importing this module is not a reusable pin.
    _, current_pins = _load_and_pin_sources()
    jvp = component_jvp_fd_certificate()
    cross = mixed_cross_term_certificate()
    gauge = internal_so3_ward_certificate()
    diffeo = intrinsic_diffeomorphism_ward_certificate()
    fields = field_activity_certificate()
    flux = normal_flux_and_matter_shift_certificate()
    routes = route_separation_certificate()
    mutants = mutant_certificate()
    geometry = _geometry_summary()
    checks = {
        "all_upstream_bytes_and_literal_action_pinned": current_pins == PIN_RECEIPT,
        "one_timelike_curved_moving_family": (
            geometry["minimum_timelike_D"] > 0.1
            and geometry["embedding_parameter_derivative_Linf"] > 0.02
            and geometry["intrinsic_R_Linf"] > 1.0e-3
            and geometry["foliation_K_Linf"] > 1.0e-3
        ),
        "plain_and_dual_codepaths_are_symbolically_separate": routes["symbolically_separate_codepaths"],
        "component_action_JVP_matches_separate_plain_FD": (
            jvp["maximum_component_value_route_error"] < 2.0e-12
            and jvp["maximum_component_JVP_error"] < 2.0e-7
            and jvp["minimum_absolute_coupled_component_JVP"] > 1.0e-5
        ),
        "selected_cross_derivatives_match_separate_four_corner_FD": (
            cross["maximum_cross_route_error"] < 2.0e-6
            and cross["minimum_absolute_cross_term"] > 1.0e-6
        ),
        "BF_components_and_nonabelian_commutators_are_active": (
            min(fields["F_tx_max_norm"], fields["F_tq_max_norm"], fields["F_xq_max_norm"]) > 1.0e-3
            and min(fields["B_yzq_max_norm"], fields["B_xyz_max_norm"], fields["B_tyz_max_norm"]) > 1.0e-3
            and fields["nonabelian_At_cross_Ax_max_norm"] > 1.0e-4
            and fields["abelianized_Ftx_mutant_witness"] > 1.0e-4
        ),
        "all_five_covariant_P_slots_active_but_yz_coordinate_reduction_declared": (
            min(fields[f"P_{axis}_max_norm"] for axis in ("t", "x", "y", "z", "q")) > 1.0e-4
            and fields["all_five_ordinary_coordinate_derivatives_active"] is False
            and fields["full_5D_coordinate_family_claimed"] is False
        ),
        "selected_bulk_P_V4_BF_orbit_algebra_sanity": (
            gauge["maximum_bulk_nominal_residual"] < 2.0e-12
            and gauge["anisotropic_V4_mutant_witness"] > 1.0e-5
            and gauge["omit_one_BF_orbit_contribution_witness"] > 1.0e-4
            and gauge["Euler_equations_imposed"] is False
            and gauge["maximum_Robin_orbit_obstruction"] > 1.0e-5
        ),
        "complete_same_action_internal_SO3_orbit": gauge["complete_same_action_SO3_orbit_claimed"],
        "intrinsic_density_divergence_diagnostic_only": (
            diffeo["maximum_integrated_interior_residual"] < 2.0e-12
            and diffeo["minimum_advective_only_mutant_witness"] > 1.0e-4
            and diffeo["BV_BFV_interface_obligation_open"] is True
        ),
        "normal_slot_activity_accounting_is_nonzero": (
            flux["minimum_normal_slot_omission_witness"] > 1.0e-5
            and flux["matter_shift"]["T_ui_norm"] > 1.0e-4
            and flux["matter_shift"]["T_ui_activity_witness"] > 1.0e-4
        ),
        "local_matter_shift_algebra_uses_correct_normal": (
            flux["matter_shift"]["P2_decomposition"]["absolute_orthogonal_decomposition_error"] < 2.0e-12
            and flux["matter_shift"]["P2_decomposition"]["legacy_raw_Pq_decomposition_error"] > 1.0e-5
            and flux["matter_shift"]["local_identity_maximum_error"] < 2.0e-8
        ),
        "complete_normal_and_matter_shift_variational_route": (
            flux["complete_normal_and_matter_shift_certificate"]
            and flux["matter_shift"]["independent_same_action_variational_route_supplied"]
        ),
        "component_mutation_activity_accounting_is_nonzero": (
            mutants["minimum_omission_witness"] > 1.0e-5
            and mutants["minimum_sign_flip_witness"] > 1.0e-5
        ),
        "independent_primary_mutant_suite": mutants["primary_mutant_suite_complete"],
    }
    primary_candidate = all((
        checks["complete_same_action_internal_SO3_orbit"],
        checks["complete_normal_and_matter_shift_variational_route"],
        checks["independent_primary_mutant_suite"],
    ))
    decision = {
        "all_upstream_bytes_and_literal_action_pinned_pass": checks["all_upstream_bytes_and_literal_action_pinned"],
        "selected_moving_family_action_JVP_FD_pass": checks["component_action_JVP_matches_separate_plain_FD"],
        "selected_mixed_cross_terms_runtime_pass": checks["selected_cross_derivatives_match_separate_four_corner_FD"],
        "selected_nonabelian_BF_activity_pass": checks["BF_components_and_nonabelian_commutators_are_active"],
        "selected_bulk_P_V4_BF_orbit_sanity_pass": checks["selected_bulk_P_V4_BF_orbit_algebra_sanity"],
        "internal_SO3_direct_orbit_diagnostic_pass": checks["complete_same_action_internal_SO3_orbit"],
        "intrinsic_periodic_density_divergence_diagnostic_pass": checks["intrinsic_density_divergence_diagnostic_only"],
        "selected_normal_slots_and_matter_shift_visible_pass": checks["complete_normal_and_matter_shift_variational_route"],
        "primary_mutant_suite_pass": checks["independent_primary_mutant_suite"],
        "v5_6_2_selected_family_primary_candidate_pass": primary_candidate,
        "independent_redteam_replication_complete": False,
        "all_five_ordinary_coordinate_directions_active_pass": False,
        "same_action_independent_Euler_Green_identity_pass": False,
        "same_action_internal_SO3_Euler_Ward_rederived_pass": False,
        "full_bulk_diffeomorphism_Ward_pass": False,
        "complete_moving_embedding_Ward_pass": False,
        "continuum_all_configurations_theorem_pass": False,
        "full_classical_variational_principle_selected_sector_pass": False,
        "C1_ACTION_selected_family_pass": False,
        "N1_ACTION_selected_family_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "complete_BV_BFV_boundary_complex_pass": False,
        "unrestricted_large_gauge_sector_pass": False,
        "deterministic_freeze_receipt_issued": False,
        "B4_pass": False,
        "B5_pass": False,
        "publication_authorized": False,
        "status": (
            "V5_6_2_SELECTED_FAMILY_DIAGNOSTICS_ONLY__PRIMARY_CANDIDATE_FAIL_CLOSED__"
            "C1_N1_FAIL_CLOSED_PENDING_SAME_ACTION_WARD_EULER_GREEN_MUTANTS_AND_REDTEAM"
        ),
    }
    for key in FAIL_CLOSED_KEYS:
        if decision[key] is not False:
            raise FullMovingV562Error(f"fail-closed claim promoted: {key}")
    true_passes = {key for key, value in decision.items() if key.endswith("_pass") and value is True}
    if true_passes != ALLOWED_TRUE_PASS_KEYS:
        raise FullMovingV562Error(f"unexpected true pass set: {sorted(true_passes)}")
    scientific = {
        "literal_action": EXACT_ACTION,
        "coefficients": COEF,
        "parameter_order": list(PARAMETER_NAMES),
        "theta": THETA.tolist(),
        "geometry": geometry,
        "component_JVP_FD": jvp,
        "mixed_cross_terms": cross,
        "field_activity": fields,
        "internal_SO3_Ward": gauge,
        "intrinsic_diffeomorphism_diagnostic": diffeo,
        "normal_flux_and_matter_shift": flux,
        "route_separation_diagnostic": routes,
        "mutation_activity_accounting": mutants,
        "checks": checks,
        "decision": decision,
    }
    generator_path = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "title": "One-Omega topological SO(3) full-moving v5.6.2 selected-family fail-closed diagnostics",
        "classification": (
            "theory_only;additive_diagnostics;primary_candidate_rejected;"
            "C1_N1_fail_closed;B4_B5_not_opened"
        ),
        "evidence_boundary": (
            "The v5.2 charter and upstream bytes are pinned. A selected regulated transcription has nonzero "
            "non-Abelian BF, five covariant P components, matching Dual/plain-FD JVPs and selected cross "
            "derivatives. The complete SO3 orbit is obstructed by the implemented Robin identification; normal "
            "and matter-shift results lack an independent same-action variational route; mutation results are "
            "activity/accounting diagnostics only. Primary-candidate, C1/N1 and freeze claims remain false."
        ),
        "open_obligations_enumerated_before_promotion": {
            "convergence": {
                "closed": False,
                "reason": "fixed finite Fourier/Gauss grid only; no h/p refinement or continuum theorem",
            },
            "bulk_complete": {
                "closed": False,
                "reason": "selected sector formulas are present, but ordinary y,z dependence, explicit yz volume, radial-cutoff completion and a full bulk Euler derivation are absent",
            },
            "moving_embedding": {
                "closed": False,
                "reason": "one nontrivial graph tangent and its collar are executed; arbitrary embedding and every normal Green slot are not proved",
            },
            "off_shell_continuous_extension": {
                "closed": False,
                "reason": "off-shell selected probes only; no dense variation class, BV-BFV interface completion, or large gauges",
            },
            "same_action_internal_SO3": {
                "closed": False,
                "reason": "bulk P/V4/BF orbit algebra closes, but the implemented Robin term has a nonzero T2/T3 orbit obstruction and no compensating frame map",
            },
            "normal_and_matter_shift": {
                "closed": False,
                "reason": "normal slots and local ADM algebra are visible, but no independent variation of the same complete action is supplied",
            },
            "mutation_adequacy": {
                "closed": False,
                "reason": "component omit/flip values are activity accounting against the nominal assembly, not kills against an independent oracle",
            },
        },
        "mathematical_contract": {
            "one_action": EXACT_ACTION["total"],
            "pullback": "q_epsilon=rho*epsilon+chi(rho)Y(t,x); scalar densities use |dq/drho|=1+epsilon chi'Y",
            "BF_top_form": "<B_yzq,F_tx>-<B_xyz,F_tq>+<B_tyz,F_xq>; F contains nonzero commutators",
            "GHY_orientation": "outward sign sigma_out=-epsilon",
            "internal_gauge_and_diffeomorphism_Wards_kept_separate": True,
            "route_separation_is_not_independence": True,
            "mutation_activity_is_not_mutation_adequacy": True,
            "Euler_Green_route": "not supplied by Dual/FD; fail-closed",
        },
        "upstream_byte_pins": current_pins,
        "excluded_inputs": {
            "HOLO_TRANSDUCTOR": "not an upstream: different calibrated scalar system without Omega/SO3/BF/GHY/interface/Robin v5.2",
            "legacy_modes_or_CSVs": "not consumed under LOCK-1 theory-only boundary",
            "old_v5_6_receipt": "not imported, modified, or rehabilitated",
        },
        "scientific": scientific,
        "scientific_sha256": _canonical_sha256(scientific),
        "limits": [
            "No ordinary y or z dependence; only covariant P_y/P_z activity is sampled.",
            "No independent runtime derivation of every bulk Eulerian and the complete Green pairing.",
            "The internal SO3 bulk result covers only P/V4/BF algebra; raw Robin T2/T3 variations obstruct a complete same-action orbit.",
            "The intrinsic torus divergence is a diagnostic, not the full bulk/moving/interface diffeomorphism Ward.",
            "The corrected n^M P_M ADM decomposition is a same-formula local sanity, not an independent matter-shift or normal-variation certificate.",
            "Route separation is a static source diagnostic, and component mutation witnesses are activity/accounting only.",
            "No independent red-team generator exists yet for v5.6.2.",
            "No convergence sequence, BV-BFV edge complex, large gauge sector, arbitrary topology, B4 or B5 is opened.",
        ],
        "provenance": {
            "generator": {
                "path": str(generator_path.relative_to(REPO)),
                "sha256": _sha256(generator_path),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST) if TEST.exists() else None,
                "present_at_generation": TEST.exists(),
            },
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    _write(OUTPUT, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
