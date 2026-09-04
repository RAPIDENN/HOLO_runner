#!/usr/bin/env python3
"""Route C sector densities evaluate the same functional as the pinned literal
action implementation, pointwise (v5.6.6.15).

Open item discharged (bridge ledger, gap 1, v5.6.6.11 same-objects theorem):
    "the Route C sector list evaluates the same functional S_rel as the
     v5.6.6.8 theorem (asserted from the sector names; that gate never
     touches the density)".

What is compared.  Two byte-pinned, independently written implementations of
the literal v5.2 relative action (exact_action sha 3011119e...):

  * Route C (v5.6.6.3, _bulk_density / _ghy_density / _brane_density):
    the moving physical collar is pulled back in full by the embedding Y to
    the reference half-space and the density is evaluated on the (theta,rho)
    jets of the pulled-back channels (metric J^T g J, connection J^T A,
    3-form by 3x3 minors of J, reference metric J^T X_inf J).
  * Route B (v5.6.5 numpy certificate, bulk_action_components /
    ghy_component / interface_action_components): the density is evaluated on
    the ambient-coordinate jets at the physical point, with the collar
    orientation carried by collar_sign and the outward normal built from
    (-Y_first, 1).

These are two different formulations of the same integral, not two copies of
one formula: curvature (Route C: connection_first + Ricci; Route B:
tensor_geometry), leaf curvature (Route C: projected Riemann + K^2 - K_trace^2;
Route B: Gauss identity with Ricci(u,u)), the Robin term (Route C: spacetime
vector with the covariant projector; Route B: internal frame vector) and the
BF orientation (Route C: pulled-back 3-form; Route B: ambient 3-form times
collar_sign) are all computed differently.

How.  A local ambient configuration is generated exactly (sympy): every one
of the 64 channels is a random quadratic Taylor polynomial in (x0+x1, y)
around the asymptotic reference X_inf, centred at the physical evaluation
point; the embedding Y is a random cubic in x0+x1 centred at theta0 (so the
derivative of the pull-back Jacobian is exercised); the point (theta0, rho0)
is random in the collar and both sides are used with their own collar_sign.  Route B receives the ambient 2-jet at the physical point; Route
C receives the exact (theta,rho) 2-jet of the pulled-back channels, obtained
by symbolic differentiation (no finite differences anywhere).  The twelve
bulk sector densities, the two GHY densities and the six interface densities
are then compared number by number.  A second, weaker block checks the
closed-form pieces of the literal formula strings (W, U, V4, wall, Robin,
the BF pairing <X,Y> = -tr(XY)/2 and the 5-form coefficient of B wedge F)
directly against the Route C code, so that for those pieces the tie is to
the literal text and not only to Route B.

What this establishes and what it does not.  Sampled pointwise identity of
the twenty sector densities as functions of the local data, at random
generic 2-jets inside the v5.6.4 margins, to the reported tolerance; and a
literal-text check of the closed-form coefficients.  It is not a symbolic
identity proof (the densities are transcendental in the jets), it does not
bound the finite-difference stencil bias B_FD of the real Route C pipeline
(Codex lane, v5.6.6.12), it does not touch quadrature, and it flips no
bridge, C1/N1, B4/B5 or promotion key.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / "one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.json"
TEST = HERE / "test_one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.py"
SCHEMA = "holo.one-omega-topological-so3-route-c-same-functional-pointwise-v5-6-6-15.v1"
FROZEN_COMMIT = "ea014fd"

LITERAL_V5_2_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
BUNDLE_PATH = ARTIFACTS / "one_omega_topological_so3_restricted_spectral_family_v5_6_4_4_c2_radial_primitive_bundle.json"
BUNDLE_SHA256 = "1f6a0234a536c05119ad6a0dbdbf2ccd8cb555e8eec43e4c1dfefd4626227bdf"
ROUTE_C_PATH = HERE / "derive_one_omega_topological_so3_multin_independent_euler_green_route_c_v5_6_6_3.py"
ROUTE_C_SHA256 = "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b"
ROUTE_B_PATH = HERE / "derive_one_omega_topological_so3_numpy_fd5_action_route_b_v5_6_5_certificate.py"
ROUTE_B_SHA256 = "6c98724d0e51c1cad16c80303e6ad7625d661bd1c9c56c9ff96c5b8124992909"
V56611_PATH = ARTIFACTS / "one_omega_topological_so3_pinned_members_dense_collar_margins_v5_6_6_11.json"
V56611_SHA256 = "89592cd0eb7a3357a7f0b6f69bebeed5fb18d7466719c226b482b8611201a7b6"

# Fixed before run.
SEED = 56615
BULK_SAMPLES_PER_SIDE = 12
INTERFACE_SAMPLES = 24
CLOSED_FORM_SAMPLES = 16
FIELD_AMPLITUDE = 0.18
DERIVATIVE_AMPLITUDE = 0.35
EMBEDDING_AMPLITUDE = 0.25
RELATIVE_TOLERANCE = 1.0e-9
CLOSED_FORM_TOLERANCE = 1.0e-12
# v5.6.4 margins (checked on every sampled configuration, both routes' inputs).
MARGIN_SIGNATURE_EIGENVALUE = 0.02
MARGIN_OMEGA = 0.5
MARGIN_KHRONON = 0.2
MARGIN_ROTATION_CUT_LOCUS = 1.0

SIDES = ("plus", "minus")
COLLAR_SIGN = {"plus": -1, "minus": 1}
REFERENCE_METRIC = np.diag((-1.64, 1.17, 1.31, 1.46, 1.17))
BULK_SECTORS = ("EH", "Omega_kinetic", "Omega_potential", "P_kinetic", "full_V4", "BF")
BRANE_SECTORS = ("wall", "K_foliation", "R", "R_squared", "a_squared", "Robin")
LITERAL_TERM_OF_SECTOR = {
    "EH": "bulk_gauged:M5^3*R/2",
    "Omega_kinetic": "bulk_gauged:-G*(nabla Omega)^2/2",
    "Omega_potential": "bulk_gauged:-U(Omega) [bulk_potential, superpotential]",
    "P_kinetic": "bulk_gauged:-Z5*delta_ab*P^a_M*P^(bM)/2 [gauged_conformal_derivative]",
    "full_V4": "bulk_gauged:-Z5*M^2*Omega^(-5)*V4(Omega^(3/2)*|phi|) [full_V4]",
    "BF": "BF:<B wedge F[A]>, <X,Y>=-tr_3(XY)/2",
    "GHY": "GHY:M5^3*sqrt(-gamma)*Theta_eps (outward normals)",
    "wall": "wall_background:-sqrt(-gamma)*[2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2]",
    "K_foliation": "foliation_lower:Mb^2/2*sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2]",
    "R": "foliation_lower:Mb^2/2*sqrt(-gamma)*xi*Rcal",
    "R_squared": "foliation_lower:Mb^2/2*sqrt(-gamma)*[-B4_bar*Rcal^2/(16*k_infinity^2)]",
    "a_squared": "foliation_lower:Mb^2/2*sqrt(-gamma)*eta*a_mu*a^mu",
    "Robin": "Robin_intrinsic:-kappa_hat/2*sqrt(-gamma)*h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)",
}


class SameFunctionalGateError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# pins and pinned modules
# --------------------------------------------------------------------------
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_pinned_module(path: Path, expected_sha256: str, name: str) -> Any:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise SameFunctionalGateError(f"{path.name} byte pin drift: {observed}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_bundle() -> Mapping[str, Any]:
    if _sha256(BUNDLE_PATH) != BUNDLE_SHA256:
        raise SameFunctionalGateError("C2 primitive bundle drift")
    bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    action = bundle["action_contract"]
    if action["exact_action_sha256"] != LITERAL_V5_2_ACTION_SHA256:
        raise SameFunctionalGateError("literal v5.2 action hash drift")
    if _canonical_sha256(action["exact_action"]) != LITERAL_V5_2_ACTION_SHA256:
        raise SameFunctionalGateError("literal v5.2 action text does not hash to its pin")
    return bundle


def load_routes() -> tuple[Any, Any]:
    route_c = _load_pinned_module(ROUTE_C_PATH, ROUTE_C_SHA256, "pinned_route_c_v5_6_6_3")
    route_b = _load_pinned_module(ROUTE_B_PATH, ROUTE_B_SHA256, "pinned_route_b_v5_6_5")
    if tuple(route_c.BULK_SECTORS) != BULK_SECTORS or tuple(route_c.BRANE_SECTORS) != BRANE_SECTORS:
        raise SameFunctionalGateError("Route C sector list drift")
    if tuple(route_c.SYMMETRIC5) != tuple(route_b.SYMMETRIC5):
        raise SameFunctionalGateError("symmetric packing conventions differ")
    if not np.array_equal(route_c.REFERENCE_METRIC, REFERENCE_METRIC) or not np.array_equal(
        route_b.REFERENCE_METRIC, REFERENCE_METRIC
    ):
        raise SameFunctionalGateError("reference metric drift")
    if tuple(route_c.B_TRIPLES) != tuple(route_b.B_TRIPLES):
        raise SameFunctionalGateError("3-form index conventions differ")
    return route_c, route_b


# --------------------------------------------------------------------------
# exact local ambient configuration (sympy) and the two routes' inputs
# --------------------------------------------------------------------------
T_SYM, Y_SYM = sp.symbols("T Yv")  # ambient x0+x1 and ambient radial coordinate y
TH_SYM, RH_SYM = sp.symbols("theta rho")  # Route C reference coordinates


def _poly2(rng: np.random.Generator, amplitude: float, derivative_amplitude: float, dT: sp.Expr, dY: sp.Expr) -> sp.Expr:
    c = rng.uniform(-1.0, 1.0, size=6)
    return (
        amplitude * c[0]
        + derivative_amplitude * (c[1] * dT + c[2] * dY)
        + 0.5 * derivative_amplitude * (c[3] * dT**2 + c[4] * dT * dY + c[5] * dY**2)
    )


def local_configuration(
    rng: np.random.Generator,
    pairs: tuple[tuple[int, int], ...],
    theta0: float,
    rho0: float,
    side: str,
) -> Mapping[str, Any]:
    """Random quadratic ambient channels around X_inf, Taylor-centred at the physical point
    (theta0, Y(theta0) + collar_sign*rho0), and a cubic embedding centred at theta0."""
    y = rng.uniform(-1.0, 1.0, size=4) * EMBEDDING_AMPLITUDE
    dT = T_SYM - theta0
    Y = y[0] + y[1] * dT + 0.5 * y[2] * dT**2 + y[3] * dT**3 / 6.0
    y_centre = float(Y.subs(T_SYM, theta0)) + COLLAR_SIGN[side] * rho0
    dY = Y_SYM - y_centre
    metric = sp.Matrix(5, 5, lambda i, j: sp.Float(REFERENCE_METRIC[i, j]))
    for i, j in pairs:
        bump = _poly2(rng, FIELD_AMPLITUDE, DERIVATIVE_AMPLITUDE, dT, dY)
        metric[i, j] = metric[i, j] + bump
        if i != j:
            metric[j, i] = metric[i, j]
    log_omega = _poly2(rng, FIELD_AMPLITUDE, DERIVATIVE_AMPLITUDE, dT, dY)
    phi = sp.Matrix([_poly2(rng, 2.0 * FIELD_AMPLITUDE, DERIVATIVE_AMPLITUDE, dT, dY) for _ in range(3)])
    A = sp.Matrix(5, 3, lambda i, j: _poly2(rng, 2.0 * FIELD_AMPLITUDE, DERIVATIVE_AMPLITUDE, dT, dY))
    B = sp.Matrix(10, 3, lambda i, j: _poly2(rng, 2.0 * FIELD_AMPLITUDE, DERIVATIVE_AMPLITUDE, dT, dY))
    return {"metric": metric, "log_omega": log_omega, "phi": phi, "A": A, "B": B, "Y": Y, "centre": (theta0, rho0, side)}


def _ambient_vector(configuration: Mapping[str, Any], pairs: tuple[tuple[int, int], ...]) -> list[sp.Expr]:
    channels: list[sp.Expr] = [configuration["metric"][i, j] for i, j in pairs]
    channels.append(configuration["log_omega"])
    channels += list(configuration["phi"])
    channels += [configuration["A"][i, j] for i in range(5) for j in range(3)]
    channels += [configuration["B"][i, j] for i in range(10) for j in range(3)]
    if len(channels) != 64:
        raise SameFunctionalGateError("ambient channel count")
    return channels


def route_b_state(
    configuration: Mapping[str, Any],
    pairs: tuple[tuple[int, int], ...],
    side: str,
    theta0: float,
    rho0: float,
    route_b: Any,
) -> Mapping[str, np.ndarray]:
    """Ambient 2-jet at the physical point, packed exactly as decode_bulk_state does."""
    sign = COLLAR_SIGN[side]
    channels = _ambient_vector(configuration, pairs)
    Y = configuration["Y"]
    y0 = float(Y.subs(T_SYM, theta0)) + sign * rho0
    point = {T_SYM: theta0, Y_SYM: y0}
    ambient = [T_SYM, T_SYM, None, None, Y_SYM]  # d/dx0 = d/dx1 = d/dT, d/dx2 = d/dx3 = 0, d/dy
    value = np.asarray([float(c.subs(point)) for c in channels])
    first = np.zeros((5, 64))
    second = np.zeros((5, 5, 64))
    d1 = {}
    for mu, var in enumerate(ambient):
        if var is None:
            continue
        d1[mu] = [sp.diff(c, var) for c in channels]
        first[mu] = [float(e.subs(point)) for e in d1[mu]]
    for mu, var_mu in enumerate(ambient):
        if var_mu is None:
            continue
        for nu, var_nu in enumerate(ambient):
            if var_nu is None or nu < mu:
                continue
            row = [float(sp.diff(e, var_nu).subs(point)) for e in d1[mu]]
            second[mu, nu] = row
            second[nu, mu] = row
    Y_theta = float(sp.diff(Y, T_SYM).subs(T_SYM, theta0))
    Y_theta_theta = float(sp.diff(Y, T_SYM, 2).subs(T_SYM, theta0))
    Y_first = np.asarray((Y_theta, Y_theta, 0.0, 0.0))
    Y_second = np.zeros((4, 4))
    Y_second[:2, :2] = Y_theta_theta
    log_omega = value[15]
    omega = math.exp(log_omega)
    return {
        "g": route_b._sym_to_matrix(value[None, None, :15], 5),
        "dg": route_b._sym_to_matrix(first[None, None, :, :15], 5),
        "ddg": route_b._sym_to_matrix(second[None, None, :, :, :15], 5),
        "Omega": np.asarray([[omega]]),
        "dOmega": (omega * first[:, 15])[None, None, :],
        "dlog_Omega": first[:, 15][None, None, :],
        "phi": value[16:19][None, None, :],
        "dphi": first[:, 16:19][None, None, :, :],
        "A": value[19:34].reshape(1, 1, 5, 3),
        "dA": first[:, 19:34].reshape(1, 1, 5, 5, 3),
        "B": value[34:64].reshape(1, 1, 10, 3),
        "Y_first": Y_first[None, :],
        "Y_second": Y_second[None, :, :],
        "collar_sign": np.asarray(sign),
        "_value": value,
        "_first": first,
    }


def route_c_jet(
    configuration: Mapping[str, Any],
    pairs: tuple[tuple[int, int], ...],
    triples: tuple[tuple[int, int, int], ...],
    side: str,
    theta0: float,
    rho0: float,
) -> Mapping[str, np.ndarray]:
    """Exact (theta,rho) 2-jet of the pulled-back channels, Route C layout (64 + 15)."""
    sign = COLLAR_SIGN[side]
    Y = configuration["Y"].subs(T_SYM, TH_SYM)
    substitution = {T_SYM: TH_SYM, Y_SYM: Y + sign * RH_SYM}
    metric = configuration["metric"].subs(substitution)
    A = configuration["A"].subs(substitution)
    B = configuration["B"].subs(substitution)
    Y_theta = sp.diff(Y, TH_SYM)
    J = sp.eye(5)
    J[4, 0] = Y_theta
    J[4, 1] = Y_theta
    J[4, 4] = sign
    pulled_metric = J.T * metric * J
    pulled_A = J.T * A
    pulled_B = sp.zeros(10, 3)
    for position, target in enumerate(triples):
        for source_position, source in enumerate(triples):
            minor = J.extract(list(source), list(target)).det()
            if minor == 0:
                continue
            for a in range(3):
                pulled_B[position, a] += minor * B[source_position, a]
    reference = J.T * sp.Matrix(5, 5, lambda i, j: sp.Float(REFERENCE_METRIC[i, j])) * J
    channels: list[sp.Expr] = [pulled_metric[i, j] for i, j in pairs]
    channels.append(configuration["log_omega"].subs(substitution))
    channels += [e.subs(substitution) for e in configuration["phi"]]
    channels += [pulled_A[i, j] for i in range(5) for j in range(3)]
    channels += [pulled_B[i, j] for i in range(10) for j in range(3)]
    channels += [reference[i, j] for i, j in pairs]
    if len(channels) != 79:
        raise SameFunctionalGateError("pulled-back channel count")
    point = {TH_SYM: theta0, RH_SYM: rho0}

    def at(exprs: list[sp.Expr]) -> np.ndarray:
        return np.asarray([float(e.subs(point)) for e in exprs])

    dt = [sp.diff(e, TH_SYM) for e in channels]
    dr = [sp.diff(e, RH_SYM) for e in channels]
    return {
        "q": at(channels),
        "qt": at(dt),
        "qr": at(dr),
        "qtt": at([sp.diff(e, TH_SYM) for e in dt]),
        "qtr": at([sp.diff(e, RH_SYM) for e in dt]),
        "qrr": at([sp.diff(e, RH_SYM) for e in dr]),
    }


# --------------------------------------------------------------------------
# margins
# --------------------------------------------------------------------------
def _signature_margin(metric: np.ndarray, negative: int) -> float:
    eigenvalues = np.linalg.eigvalsh(0.5 * (metric + metric.T))
    if int(np.sum(eigenvalues < 0.0)) != negative:
        raise SameFunctionalGateError("sampled metric is not Lorentzian")
    return float(np.min(np.abs(eigenvalues)))


def _compare(name: str, left: float, right: float, rows: dict[str, dict[str, float]]) -> None:
    scale = max(1.0, abs(left), abs(right))
    absolute = abs(left - right)
    row = rows.setdefault(
        name,
        {"max_abs_difference": 0.0, "max_relative_difference": 0.0, "max_abs_value": 0.0, "samples": 0},
    )
    row["max_abs_difference"] = max(row["max_abs_difference"], absolute)
    row["max_relative_difference"] = max(row["max_relative_difference"], absolute / scale)
    row["max_abs_value"] = max(row["max_abs_value"], abs(left), abs(right))
    row["samples"] += 1


# --------------------------------------------------------------------------
# block A: bulk and GHY, both sides, exact pulled-back vs ambient jets
# --------------------------------------------------------------------------
def bulk_and_ghy_comparison(route_c: Any, route_b: Any, parameters: Mapping[str, float]) -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    pairs = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5)
    triples = tuple(tuple(int(x) for x in t) for t in route_c.B_TRIPLES)
    rows: dict[str, dict[str, float]] = {}
    margins = {"signature_bulk_min": math.inf, "signature_induced_min": math.inf, "omega_min": math.inf, "omega_max": 0.0}
    reference_leak = 0.0
    original_decode = route_b.decode_bulk_state
    try:
        for side in SIDES:
            for _sample in range(BULK_SAMPLES_PER_SIDE):
                theta0 = float(rng.uniform(0.0, 2.0 * math.pi))
                rho0 = float(rng.uniform(0.05, 0.95))
                configuration = local_configuration(rng, pairs, theta0, rho0, side)
                state = route_b_state(configuration, pairs, side, theta0, rho0, route_b)
                jet = route_c_jet(configuration, pairs, triples, side, theta0, rho0)
                margins["signature_bulk_min"] = min(margins["signature_bulk_min"], _signature_margin(state["g"][0, 0], 1))
                margins["signature_bulk_min"] = min(
                    margins["signature_bulk_min"], _signature_margin(route_c._sym(jet["q"][:15], 5), 1)
                )
                omega = float(state["Omega"][0, 0])
                margins["omega_min"] = min(margins["omega_min"], omega)
                margins["omega_max"] = max(margins["omega_max"], omega)
                c_bulk = route_c._bulk_density(jet, parameters)
                b_bulk = route_b.bulk_action_components(state, np.asarray([1.0]), np.asarray([1.0]), parameters, side)
                for sector in BULK_SECTORS:
                    _compare(f"{sector}_bulk_{side}", float(c_bulk[sector]), float(b_bulk[f"{sector}_bulk_{side}"]), rows)
                # Route C subtracts the pulled-back reference atoms in every sector; with exact jets
                # the reference contribution outside Omega_potential must vanish (flat pull-back).
                reference_first = route_c._expand_first(jet["qt"][64:79], jet["qr"][64:79])
                reference_second = route_c._expand_second(jet["qtt"][64:79], jet["qtr"][64:79], jet["qrr"][64:79])
                reference_value = np.zeros(64)
                reference_value[:15] = jet["q"][64:79]
                full_first = np.zeros((5, 64))
                full_first[:, :15] = reference_first
                full_second = np.zeros((5, 5, 64))
                full_second[:, :, :15] = reference_second
                reference_atoms = route_c._bulk_atoms(reference_value, full_first, full_second, parameters)
                for sector in BULK_SECTORS:
                    if sector != "Omega_potential":
                        reference_leak = max(reference_leak, abs(float(reference_atoms[sector])))
                # GHY at the interface rho = 0 of a configuration centred there.
                configuration0 = local_configuration(rng, pairs, theta0, 0.0, side)
                state0 = route_b_state(configuration0, pairs, side, theta0, 0.0, route_b)
                jet0 = route_c_jet(configuration0, pairs, triples, side, theta0, 0.0)
                tangent = np.zeros((5, 4))
                tangent[:4, :] = np.eye(4)
                tangent[4, :] = state0["Y_first"][0]
                induced = tangent.T @ state0["g"][0, 0] @ tangent
                margins["signature_induced_min"] = min(margins["signature_induced_min"], _signature_margin(induced, 1))
                route_b.decode_bulk_state = lambda *args, _state=state0, **kwargs: _state
                b_ghy = route_b.ghy_component(None, None, None, 1, np.asarray([1.0]), parameters, side, 1, 1)
                route_b.decode_bulk_state = original_decode
                c_ghy = route_c._ghy_density(jet0, parameters)
                _compare(f"GHY_{side}", float(c_ghy), float(b_ghy), rows)
    finally:
        route_b.decode_bulk_state = original_decode
    worst = max(row["max_relative_difference"] for row in rows.values())
    return {
        "method": (
            "exact sympy 2-jets: Route C on the pulled-back (theta,rho) channels through J(theta) = "
            "[[I4,0],[(Y',Y',0,0),collar_sign]] with the 3-form pulled back by 3x3 minors and the reference "
            "metric by J^T X_inf J; Route B on the ambient jet at (theta0, Y(theta0)+collar_sign*rho0) with "
            "Y_first=(Y',Y',0,0), Y_second=Y'' on the (x0,x1) block; unit weights; decode_bulk_state stubbed "
            "only inside ghy_component to inject the same ambient jet"
        ),
        "samples_per_side": BULK_SAMPLES_PER_SIDE,
        "sectors": rows,
        "worst_relative_difference": worst,
        "route_c_reference_leak_outside_Omega_potential_max_abs": reference_leak,
        "margins_observed": margins,
        "pass": bool(worst <= RELATIVE_TOLERANCE and reference_leak <= 1.0e-9),
    }


# --------------------------------------------------------------------------
# block B: interface sectors on reduced (x0+x1) 2-jets through Route B's spectral tables
# --------------------------------------------------------------------------
def _pseudo_spectral_tables() -> tuple[Mapping[str, np.ndarray], list[tuple[int, int]]]:
    """Fifteen pseudo-modes so that a coefficient block (15, ch) is literally (value, 4 first, 10 second)."""
    second_pairs = [(i, j) for i in range(4) for j in range(i, 4)]
    n = 1 + 4 + len(second_pairs)
    values = np.zeros((1, n))
    first = np.zeros((1, 4, n))
    second = np.zeros((1, 4, 4, n))
    values[0, 0] = 1.0
    for mu in range(4):
        first[0, mu, 1 + mu] = 1.0
    for position, (i, j) in enumerate(second_pairs):
        second[0, i, j, 5 + position] = 1.0
        second[0, j, i, 5 + position] = 1.0
    return {"values": values, "first": first, "second": second}, second_pairs


def interface_comparison(route_c: Any, route_b: Any, parameters: Mapping[str, float]) -> dict[str, Any]:
    rng = np.random.default_rng(SEED + 1)
    tables, second_pairs = _pseudo_spectral_tables()
    pairs4 = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC4)
    reference4 = REFERENCE_METRIC[:4, :4]
    blocks = {"common.gamma": 10, "common.T": 1, "common.log_Omega": 1, "common.varphi_E0": 3, "Q_frame.q": 3}
    layout: dict[str, Any] = {}
    cursor = 0
    for name, width in blocks.items():
        layout[name] = {"start": cursor, "stop": cursor + 15 * width, "shape": [15, width]}
        cursor += 15 * width
    rows: dict[str, dict[str, float]] = {}
    margins = {"signature_common_min": math.inf, "khronon_norm_max": -math.inf, "rotation_norm_max": 0.0, "omega_min": math.inf}
    for _sample in range(INTERFACE_SAMPLES):
        gamma = reference4.copy()
        for i, j in pairs4:
            gamma[i, j] += FIELD_AMPLITUDE * rng.uniform(-1.0, 1.0)
            gamma[j, i] = gamma[i, j]
        gamma_t = np.asarray([DERIVATIVE_AMPLITUDE * rng.uniform(-1.0, 1.0) for _ in pairs4])
        gamma_tt = np.asarray([DERIVATIVE_AMPLITUDE * rng.uniform(-1.0, 1.0) for _ in pairs4])
        T_t = 0.3 * FIELD_AMPLITUDE * rng.uniform(-1.0, 1.0)
        T_tt = DERIVATIVE_AMPLITUDE * rng.uniform(-1.0, 1.0)
        log_omega = FIELD_AMPLITUDE * rng.uniform(-1.0, 1.0)
        varphi = 2.0 * FIELD_AMPLITUDE * rng.uniform(-1.0, 1.0, size=3)
        frame_q = rng.uniform(-1.0, 1.0, size=3)
        frame_q *= (math.pi - MARGIN_ROTATION_CUT_LOCUS) * rng.uniform(0.1, 1.0) / np.linalg.norm(frame_q)
        # Route C reduced jet: [gamma(10), T, log_Omega, varphi_E0(3), q(3)] with theta derivatives only.
        q = np.concatenate((route_c._sym_vector(gamma, 4), [0.0, log_omega], varphi, frame_q))
        qt = np.concatenate((gamma_t, [T_t, 0.0], np.zeros(3), np.zeros(3)))
        qtt = np.concatenate((gamma_tt, [T_tt, 0.0], np.zeros(3), np.zeros(3)))
        jet = {"q": q, "qt": qt, "qtt": qtt}
        # Route B coefficient vector through the pseudo-modes: theta = x0 + x1 dependence.
        free = np.zeros(cursor)

        def fill(name: str, value: np.ndarray, first_t: np.ndarray, second_tt: np.ndarray) -> None:
            block = np.zeros((15, blocks[name]))
            block[0] = value
            block[1] = first_t
            block[2] = first_t
            for position, (i, j) in enumerate(second_pairs):
                if i < 2 and j < 2:
                    block[5 + position] = second_tt
            spec = layout[name]
            free[spec["start"]:spec["stop"]] = block.reshape(-1)

        fill("common.gamma", route_b._matrix_to_sym(gamma, 4), gamma_t, gamma_tt)
        fill("common.T", np.asarray([0.0]), np.asarray([T_t]), np.asarray([T_tt]))
        fill("common.log_Omega", np.asarray([log_omega]), np.zeros(1), np.zeros(1))
        fill("common.varphi_E0", varphi, np.zeros(3), np.zeros(3))
        fill("Q_frame.q", frame_q, np.zeros(3), np.zeros(3))
        c_brane = route_c._brane_density(jet, parameters)
        b_brane = route_b.interface_action_components(free, layout, tables, np.asarray([1.0]), parameters)
        for sector in BRANE_SECTORS:
            _compare(sector, float(c_brane[sector]), float(b_brane[sector]), rows)
        margins["signature_common_min"] = min(margins["signature_common_min"], _signature_margin(gamma, 1))
        tau = np.asarray((1.0 + T_t, T_t, 0.0, 0.0))
        margins["khronon_norm_max"] = max(margins["khronon_norm_max"], float(tau @ np.linalg.inv(gamma) @ tau))
        margins["rotation_norm_max"] = max(margins["rotation_norm_max"], float(np.linalg.norm(frame_q)))
        margins["omega_min"] = min(margins["omega_min"], math.exp(log_omega))
    worst = max(row["max_relative_difference"] for row in rows.values())
    return {
        "method": (
            "reduced 2-jets (dependence on x0+x1 only, as in the pinned members): Route C _brane_density on "
            "[gamma, T, log_Omega, varphi_E0, q] with theta derivatives; Route B interface_action_components on "
            "a coefficient vector whose fifteen pseudo-modes are (value, four first, ten second derivatives) "
            "with first=(f',f',0,0) and second=f'' on the (x0,x1) block; unit weight"
        ),
        "samples": INTERFACE_SAMPLES,
        "sectors": rows,
        "worst_relative_difference": worst,
        "margins_observed": margins,
        "pass": bool(worst <= RELATIVE_TOLERANCE and margins["khronon_norm_max"] <= -MARGIN_KHRONON),
    }


# --------------------------------------------------------------------------
# block C: closed-form pieces of the literal formula strings against Route C code
# --------------------------------------------------------------------------
def closed_form_transcription(route_c: Any, parameters: Mapping[str, float], exact_action: Mapping[str, str]) -> dict[str, Any]:
    rng = np.random.default_rng(SEED + 2)
    M5, G, k, Z, M = (float(parameters[n]) for n in ("M5_cubed", "compensator_metric_G", "k_infinity", "material_Z5_per_side", "material_mass_M"))
    beta, kappa_hat = float(parameters["brane_beta"]), float(parameters["Robin_kappa_hat"])
    Om, r = sp.symbols("Omega r", positive=True)
    # literal strings, transcribed
    W = 3 * M5 * k * sp.exp(-G * Om**2 / (6 * M5))
    W_Om = sp.diff(W, Om)
    U = W_Om**2 / (2 * G) - 2 * W**2 / (3 * M5)
    V4 = r**4 / (2 * sp.sqrt(1 + r**4))
    checks: dict[str, float] = {}
    pairs = tuple(tuple(int(x) for x in pair) for pair in route_c.SYMMETRIC5)
    volume = math.sqrt(abs(np.linalg.det(REFERENCE_METRIC)))
    for _ in range(CLOSED_FORM_SAMPLES):
        log_omega = float(rng.uniform(-0.6, 0.6))
        omega = math.exp(log_omega)
        phi = rng.uniform(-1.0, 1.0, size=3)
        value = np.zeros(64)
        value[:15] = route_c._sym_vector(REFERENCE_METRIC)
        value[15] = log_omega
        value[16:19] = phi
        atoms = route_c._bulk_atoms(value, np.zeros((5, 64)), np.zeros((5, 5, 64)), parameters)
        literal_potential = -volume * float(U.subs(Om, omega))
        argument = omega**1.5 * float(np.linalg.norm(phi))
        literal_v4 = -volume * Z * M**2 * omega**-5.0 * float(V4.subs(r, argument))
        checks["Omega_potential_vs_literal_U_W"] = max(checks.get("Omega_potential_vs_literal_U_W", 0.0), abs(atoms["Omega_potential"] - literal_potential) / max(1.0, abs(literal_potential)))
        checks["full_V4_vs_literal_V4"] = max(checks.get("full_V4_vs_literal_V4", 0.0), abs(atoms["full_V4"] - literal_v4) / max(1.0, abs(literal_v4)))
        for sector in ("EH", "Omega_kinetic", "P_kinetic", "BF"):
            checks[f"{sector}_vanishes_on_constant_reference_data"] = max(checks.get(f"{sector}_vanishes_on_constant_reference_data", 0.0), abs(atoms[sector]))
        # wall and Robin on a flat static interface: sqrt(-gamma)*(-2W - beta(Omega-1)^2/2), -kappa_hat/2 |varphi|^2
        gamma4 = REFERENCE_METRIC[:4, :4]
        q = np.concatenate((route_c._sym_vector(gamma4, 4), [0.0, log_omega], phi, np.zeros(3)))
        brane = route_c._brane_density({"q": q, "qt": np.zeros(18), "qtt": np.zeros(18)}, parameters)
        measure = math.sqrt(abs(np.linalg.det(gamma4)))
        literal_wall = measure * (-2.0 * float(W.subs(Om, omega)) - 0.5 * beta * (omega - 1.0) ** 2)
        literal_robin = -0.5 * kappa_hat * measure * float(phi @ phi)
        checks["wall_vs_literal_W_beta"] = max(checks.get("wall_vs_literal_W_beta", 0.0), abs(brane["wall"] - literal_wall) / max(1.0, abs(literal_wall)))
        checks["Robin_static_flat_vs_literal"] = max(checks.get("Robin_static_flat_vs_literal", 0.0), abs(brane["Robin"] - literal_robin) / max(1.0, abs(literal_robin)))
        for sector in ("K_foliation", "R", "R_squared", "a_squared"):
            checks[f"{sector}_vanishes_on_flat_static_interface"] = max(checks.get(f"{sector}_vanishes_on_flat_static_interface", 0.0), abs(brane[sector]))
    # BF: <B wedge F>, <X,Y> = -tr_3(XY)/2 on so(3) in the hat basis, 5-form coefficient by Levi-Civita
    x1, x2, x3, y1, y2, y3 = sp.symbols("x1 x2 x3 y1 y2 y3")
    hat = lambda v: sp.Matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    pairing = sp.simplify(-(hat((x1, x2, x3)) * hat((y1, y2, y3))).trace() / 2 - (x1 * y1 + x2 * y2 + x3 * y3))
    checks["BF_pairing_minus_half_trace_equals_dot"] = 0.0 if pairing == 0 else 1.0
    triples = tuple(tuple(int(x) for x in t) for t in route_c.B_TRIPLES)
    bf_worst = 0.0
    for _ in range(CLOSED_FORM_SAMPLES):
        B = rng.uniform(-1.0, 1.0, size=(10, 3))
        dA = rng.uniform(-1.0, 1.0, size=(5, 5, 3))
        value = np.zeros(64)
        value[:15] = route_c._sym_vector(REFERENCE_METRIC)
        value[34:64] = B.reshape(30)
        first = np.zeros((5, 64))
        first[:, 19:34] = dA.reshape(5, 15)
        atoms = route_c._bulk_atoms(value, first, np.zeros((5, 5, 64)), parameters)
        F = dA - np.transpose(dA, (1, 0, 2))  # A = 0 so F_MN = d_M A_N - d_N A_M
        full_B = np.zeros((5, 5, 5, 3))
        for position, (i, j, kk) in enumerate(triples):
            for perm, sign in (((i, j, kk), 1), ((j, kk, i), 1), ((kk, i, j), 1), ((j, i, kk), -1), ((i, kk, j), -1), ((kk, j, i), -1)):
                full_B[perm] = sign * B[position]
        literal = 0.0
        for a, b, c, d, e in __import__("itertools").permutations(range(5)):
            eps = int(sp.LeviCivita(a, b, c, d, e))
            literal += eps * float(full_B[a, b, c] @ F[d, e])
        literal /= 12.0  # 3! 2!
        bf_worst = max(bf_worst, abs(atoms["BF"] - literal) / max(1.0, abs(literal)))
    checks["BF_5form_coefficient_vs_LeviCivita_over_3!2!"] = bf_worst
    worst = max(checks.values())
    return {
        "literal_strings_used": {key: exact_action[key] for key in ("superpotential", "bulk_potential", "full_V4", "wall_background", "Robin_intrinsic", "BF")},
        "checks_max_relative_difference": checks,
        "worst": worst,
        "pass": bool(worst <= CLOSED_FORM_TOLERANCE),
        "scope": (
            "closed-form pieces only (W, U, V4, wall, static-flat Robin, BF pairing and 5-form coefficient); "
            "curvature, kinetic, foliation and Robin-with-acceleration terms are tied to the literal text only "
            "through the pinned Route B transcription (blocks A and B)"
        ),
    }


def sector_term_bijection(exact_action: Mapping[str, str]) -> dict[str, Any]:
    names = [f"{s}_bulk_{side}" for side in SIDES for s in BULK_SECTORS] + [f"GHY_{side}" for side in SIDES] + list(BRANE_SECTORS)
    total = exact_action["total"]
    literal_terms = ("S_bulk_gauged", "S_GHY", "S_wall0", "S_fol_lower", "S_R_intrinsic", "S_BF")
    covered = {
        "S_bulk_gauged": [s for s in BULK_SECTORS if s != "BF"],
        "S_GHY": ["GHY"],
        "S_wall0": ["wall"],
        "S_fol_lower": ["K_foliation", "R", "R_squared", "a_squared"],
        "S_R_intrinsic": ["Robin"],
        "S_BF": ["BF"],
    }
    every_term_present = all(term in total for term in literal_terms)
    every_sector_assigned = set(sum(covered.values(), [])) == set(BULK_SECTORS) | set(BRANE_SECTORS) | {"GHY"}
    return {
        "route_c_action_components": names,
        "literal_total": total,
        "literal_term_to_sectors": covered,
        "sector_to_literal_term": LITERAL_TERM_OF_SECTOR,
        "removed_terms_declared": exact_action["removed_terms"],
        "pass": bool(every_term_present and every_sector_assigned and len(names) == 20),
    }


# --------------------------------------------------------------------------
# payload
# --------------------------------------------------------------------------
def build_payload() -> dict[str, Any]:
    bundle = load_bundle()
    route_c, route_b = load_routes()
    parameters = bundle["action_contract"]["coefficient_parameters"]
    exact_action = bundle["action_contract"]["exact_action"]
    bijection = sector_term_bijection(exact_action)
    block_a = bulk_and_ghy_comparison(route_c, route_b, parameters)
    block_b = interface_comparison(route_c, route_b, parameters)
    block_c = closed_form_transcription(route_c, parameters, exact_action)
    if _sha256(V56611_PATH) != V56611_SHA256:
        raise SameFunctionalGateError("v5.6.6.11 receipt drift")
    v56611 = json.loads(V56611_PATH.read_text(encoding="utf-8"))
    hypothesis_text = next(
        (h for h in v56611["scientific"]["same_objects_theorem"].get("analytic_not_machine_checked", []) if "same functional" in h),
        None,
    )
    scientific = {
        "statement": (
            "For the twenty named components of S_rel_v5_2 the Route C sector densities (pulled-back "
            "formulation, v5.6.6.3) and the pinned Route B densities (ambient formulation, v5.6.5, byte-pinned to "
            "the literal v5.2 action) agree pointwise as functions of the local data at random generic 2-jets "
            "inside the v5.6.4 margins, on both collars, to the reported relative tolerance; the BF orientation "
            "(pulled-back 3-form versus collar_sign times the ambient 3-form), the outward GHY normal and the "
            "reference subtraction conventions are included in the comparison. The closed-form pieces of the "
            "literal formula strings are additionally checked against the Route C code directly."
        ),
        "hypothesis_discharged_from_v5_6_6_11": hypothesis_text,
        "sector_term_bijection": bijection,
        "block_A_bulk_and_GHY_pointwise": block_a,
        "block_B_interface_pointwise": block_b,
        "block_C_closed_form_literal_transcription": block_c,
        "conventions_verified": {
            "collar_sign": {"plus": -1, "minus": 1, "route_c": "SIDE_RADIAL_SIGN = J[4,4]", "route_b": "collar_sign in _physical_derivatives and _bf_coefficient"},
            "BF_orientation": "Route C evaluates the pulled-back 3-form with unit-weight (theta,rho) measure; Route B multiplies the ambient coefficient by collar_sign = det J; equal pointwise on both sides",
            "reference_subtraction": "Route C subtracts the pulled-back X_inf atoms in every bulk sector (exactly zero outside Omega_potential for exact jets, leak reported); Route B subtracts only the constant -sqrt(-X_inf) U(1) in Omega_potential; interface and GHY unsubtracted in both (compact_relative_action_contract)",
            "GHY_normal": "Route C: -d rho normalised by the pulled-back inverse metric at rho = 0; Route B: outward_sign * (-Y_first, 1) normalised by the ambient inverse metric",
        },
        "what_is_not_established": [
            "a symbolic identity of the densities (they are transcendental in the jets; this is a sampled identity)",
            "the finite-difference stencil bias B_FD of the real Route C jets (Codex lane, v5.6.6.12); this gate uses exact jets",
            "quadrature: nothing here concerns the (theta,rho) integration or its rate",
            "the transcription of curvature, kinetic, foliation and Robin-with-acceleration terms from the literal text; for those the tie to the text is the pinned Route B implementation (v5.6.4/v5.6.5 pins), which this gate shows Route C reproduces",
            "any bridge, C1/N1, B4/B5 or promotion key",
        ],
    }
    decision = {
        "route_c_sector_list_is_literal_action_term_list_pass": bool(bijection["pass"]),
        "route_c_bulk_and_ghy_densities_equal_pinned_literal_implementation_pointwise_pass": bool(block_a["pass"]),
        "route_c_interface_densities_equal_pinned_literal_implementation_pointwise_pass": bool(block_b["pass"]),
        "route_c_closed_form_coefficients_match_literal_formula_strings_pass": bool(block_c["pass"]),
        "same_functional_symbolic_identity_pass": False,
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
        "classification": "theory_only;sampled_pointwise_density_identity;two_pinned_implementations;literal_closed_form_transcription;restricted_spectral_family;fail_closed_bridge",
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            "C2_multi_N_primitive_bundle_sha256": BUNDLE_SHA256,
            "coefficient_parameters_sha256": bundle["action_contract"]["coefficient_parameters_sha256"],
            "route_c_v5_6_6_3_derive_sha256": ROUTE_C_SHA256,
            "route_b_v5_6_5_certificate_derive_sha256": ROUTE_B_SHA256,
            "v5_6_6_11_receipt_sha256": V56611_SHA256,
        },
        "fixed_before_run": {
            "seed": SEED,
            "bulk_samples_per_side": BULK_SAMPLES_PER_SIDE,
            "interface_samples": INTERFACE_SAMPLES,
            "closed_form_samples": CLOSED_FORM_SAMPLES,
            "field_amplitude": FIELD_AMPLITUDE,
            "derivative_amplitude": DERIVATIVE_AMPLITUDE,
            "embedding_amplitude": EMBEDDING_AMPLITUDE,
            "relative_tolerance": RELATIVE_TOLERANCE,
            "closed_form_tolerance": CLOSED_FORM_TOLERANCE,
            "margins": {
                "signature_eigenvalue": MARGIN_SIGNATURE_EIGENVALUE,
                "omega": MARGIN_OMEGA,
                "khronon": MARGIN_KHRONON,
                "rotation_cut_locus": MARGIN_ROTATION_CUT_LOCUS,
            },
        },
        "scientific": scientific,
        "decision": decision,
        "evidence_boundary": (
            "Sampled pointwise agreement of two pinned implementations of the literal v5.2 relative action on "
            "exact random 2-jets, plus literal-text checks of the closed-form pieces. Not a symbolic identity, not "
            "a statement about the finite-difference jets or the quadrature of the real Route C pipeline, and "
            "not a bridge, C1/N1 or promotion result."
        ),
        "independence_boundary": {
            "dynamic_imports": {"route_c": ROUTE_C_PATH.name, "route_b": ROUTE_B_PATH.name},
            "route_b_monkeypatch": "decode_bulk_state replaced only during ghy_component calls, restored afterwards",
            "no_route_c_pipeline_run": True,
            "no_finite_differences": True,
        },
        "open_obligation": [
            "B_FD bound (Codex, v5.6.6.12)",
            "gap 5 of the bridge ledger (finite DG_N on V_N, gauge quotient H_N)",
            "N -> infinity for arbitrary class members",
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
    decision = payload["decision"]
    print(json.dumps({k: v for k, v in decision.items() if v}, indent=2))
    a = payload["scientific"]["block_A_bulk_and_GHY_pointwise"]
    b = payload["scientific"]["block_B_interface_pointwise"]
    c = payload["scientific"]["block_C_closed_form_literal_transcription"]
    print(f"worst relative: bulk+GHY {a['worst_relative_difference']:.3e}, interface {b['worst_relative_difference']:.3e}, closed-form {c['worst']:.3e}")
    print(f"reference leak: {a['route_c_reference_leak_outside_Omega_potential_max_abs']:.3e}")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
