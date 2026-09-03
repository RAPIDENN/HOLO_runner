#!/usr/bin/env python3
"""Non-additive configuration mutants for the v5.6.5 action comparator.

This is deliberately a mutation harness, not a third nominal evaluator.  It
byte-pins the frozen NumPy implementation, changes primitive configurations or
one literal action ingredient before evaluation, and asks whether the already
independent Torch/NumPy comparison detects a significant change.  No mutant is
allowed to promote C1/N1.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
ROUTE_B_SOURCE = HERE / (
    "derive_one_omega_topological_so3_numpy_fd5_action_route_b_"
    "v5_6_5_certificate.py"
)
ROUTE_A_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_literal_torch_action_route_a_"
    "v5_6_5_certificate.json"
)
ROUTE_B_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_numpy_fd5_action_route_b_"
    "v5_6_5_certificate.json"
)
TEST = HERE / (
    "test_one_omega_topological_so3_special_configuration_mutants_"
    "v5_6_5_4.py"
)
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_special_configuration_mutants_"
    "v5_6_5_4.json"
)

ROUTE_B_SOURCE_SHA256 = "6c98724d0e51c1cad16c80303e6ad7625d661bd1c9c56c9ff96c5b8124992909"
ROUTE_A_ARTIFACT_SHA256 = "ec56360b271cea3d32b41c5d3c19e7a7dc85de4425b4cd3ab4e5fe290f696e2e"
ROUTE_B_ARTIFACT_SHA256 = "7e1044cdc628052750f02f0ab4d134c89ee85f7296d3de027d998177578320db"
SCHEMA = "holo.one-omega-topological-so3-special-configuration-mutants-v5-6-5-4.v1"

TANGENTIAL_Q = 5
RADIAL_Q = 3
COARSE_STEP = 4.0e-2
FINE_STEP = 2.0e-2
ACTION_DELTA_KILL_ABS = 1.0e-7
GLUING_KILL_LINF = 1.0e-7
DERIVATIVE_KILL_REL_L2 = 1.0e-6
T_UI_ACTIVITY_MIN = 1.0e-7
T_UI_FD5_STEP = 2.0e-5
T_UI_ACTION_SHIFT_MAX_ERROR = 2.0e-8


class SpecialMutantError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path, expected: str, label: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected:
        raise SpecialMutantError(f"{label} byte pin drift: {observed} != {expected}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_route_b() -> Any:
    observed = _sha256(ROUTE_B_SOURCE)
    if observed != ROUTE_B_SOURCE_SHA256:
        raise SpecialMutantError(
            f"frozen route B source drift: {observed} != {ROUTE_B_SOURCE_SHA256}"
        )
    module_name = "special_mutants_frozen_numpy_route_b_v565"
    spec = importlib.util.spec_from_file_location(module_name, ROUTE_B_SOURCE)
    if spec is None or spec.loader is None:
        raise SpecialMutantError("cannot import the frozen route B source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_inputs() -> tuple[Any, Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    route_b = load_route_b()
    route_a_receipt = _load_json(
        ROUTE_A_ARTIFACT, ROUTE_A_ARTIFACT_SHA256, "route A artifact"
    )
    route_b_receipt = _load_json(
        ROUTE_B_ARTIFACT, ROUTE_B_ARTIFACT_SHA256, "route B artifact"
    )
    bundle = route_b.load_primitive_bundle()
    return route_b, route_a_receipt, route_b_receipt, bundle


def _block_view(
    vector: np.ndarray, layout: Mapping[str, Any], name: str
) -> np.ndarray:
    item = layout[name]
    return vector[int(item["start"]): int(item["stop"])].reshape(item["shape"])


def freeze_relative_rotation_tangent(
    tangent: np.ndarray, layout: Mapping[str, Any]
) -> np.ndarray:
    mutated = np.array(tangent, dtype=float, copy=True)
    for side in ("plus", "minus"):
        _block_view(mutated, layout, f"{side}.r_E0")[...] = 0.0
    return mutated


def _tensor_component_parities(route_b: Any) -> np.ndarray:
    parity = np.ones(64, dtype=float)
    for position, (i, j) in enumerate(route_b.SYMMETRIC5):
        parity[position] = -1.0 if (i == 4) ^ (j == 4) else 1.0
    parity[15] = 1.0
    parity[16:19] = 1.0
    for M in range(5):
        parity[19 + 3 * M: 19 + 3 * (M + 1)] = -1.0 if M == 4 else 1.0
    for position, triple in enumerate(route_b.B_TRIPLES):
        parity[34 + 3 * position: 34 + 3 * (position + 1)] = (
            -1.0 if 4 in triple else 1.0
        )
    return parity


def impose_reflected_z2_free_data(
    vector: np.ndarray, layout: Mapping[str, Any], route_b: Any
) -> np.ndarray:
    """Reflect plus collar primitives into minus with tensor-index parity."""

    mutated = np.array(vector, dtype=float, copy=True)
    _block_view(mutated, layout, "minus.Y")[...] = -_block_view(
        mutated, layout, "plus.Y"
    )
    plus_metric = _block_view(mutated, layout, "plus.metric_free")
    minus_metric = _block_view(mutated, layout, "minus.metric_free")
    minus_metric[...] = plus_metric
    minus_metric[..., :4] *= -1.0
    _block_view(mutated, layout, "minus.A_perp")[...] = -_block_view(
        mutated, layout, "plus.A_perp"
    )
    plus_B = _block_view(mutated, layout, "plus.B0_full")
    minus_B = _block_view(mutated, layout, "minus.B0_full")
    minus_B[...] = plus_B
    for position, triple in enumerate(route_b.B_TRIPLES):
        if 4 in triple:
            minus_B[:, position, :] *= -1.0
    _block_view(mutated, layout, "minus.r_E0")[...] = _block_view(
        mutated, layout, "plus.r_E0"
    )
    channel_parity = _tensor_component_parities(route_b)
    _block_view(mutated, layout, "minus.boundary_jet_J1")[...] = (
        _block_view(mutated, layout, "plus.boundary_jet_J1") * channel_parity
    )
    _block_view(mutated, layout, "minus.interior_bump_C")[...] = (
        _block_view(mutated, layout, "plus.interior_bump_C")
        * channel_parity[None, None, :]
    )
    return mutated


def z2_free_residual(
    vector: np.ndarray, layout: Mapping[str, Any], route_b: Any
) -> float:
    reflected = impose_reflected_z2_free_data(vector, layout, route_b)
    minus_start = min(int(item["start"]) for name, item in layout.items() if name.startswith("minus."))
    minus_stop = max(int(item["stop"]) for name, item in layout.items() if name.startswith("minus."))
    return float(np.max(np.abs(vector[minus_start:minus_stop] - reflected[minus_start:minus_stop])))


def _copy_tree(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return np.array(value, copy=True)
    if isinstance(value, dict):
        return {key: _copy_tree(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_copy_tree(item) for item in value]
    return copy.deepcopy(value)


@contextmanager
def _patched(module: Any, name: str, replacement: Any) -> Iterator[None]:
    original = getattr(module, name)
    setattr(module, name, replacement)
    try:
        yield
    finally:
        setattr(module, name, original)


def _max_gluing_linf(evaluation: Mapping[str, Any]) -> float:
    return max(
        float(component["Linf"])
        for side in evaluation["pointwise_gluing"].values()
        for component in side.values()
    )


def _central_record(
    identifier: str,
    intervention: str,
    evaluation: Mapping[str, Any],
    nominal: Mapping[str, float],
) -> dict[str, Any]:
    deltas = {
        component: float(evaluation["components"][component] - nominal[component])
        for component in nominal
    }
    component_delta = max(
        abs(value) for name, value in deltas.items() if name != "S_total"
    )
    gluing = _max_gluing_linf(evaluation)
    return {
        "id": identifier,
        "intervention": intervention,
        "mutated_S_rel_components": evaluation["components"],
        "component_deltas_from_nominal": deltas,
        "maximum_action_component_absolute_delta": component_delta,
        "S_total_absolute_delta": abs(deltas["S_total"]),
        "mutated_pointwise_gluing_Linf": gluing,
        "killed_by_action_or_gluing": bool(
            component_delta > ACTION_DELTA_KILL_ABS or gluing > GLUING_KILL_LINF
        ),
    }


def _decoder_mutant_evaluation(
    route_b: Any,
    free: np.ndarray,
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    mutation: str,
) -> Mapping[str, Any]:
    original = route_b.decode_pointwise_free_boundary

    def mutated_decoder(
        local_free: np.ndarray, local_bundle: Mapping[str, Any], points: np.ndarray
    ) -> Mapping[str, Any]:
        decoded = _copy_tree(original(local_free, local_bundle, points))
        if mutation == "rotate_phi_only":
            rotation = route_b._so3_exp(np.asarray((0.19, -0.13, 0.11), dtype=float))
            for side in route_b.SIDES:
                decoded["sides"][side]["phi_trace"] = np.einsum(
                    "ij,pj->pi", rotation, decoded["sides"][side]["phi_trace"]
                )
        elif mutation == "break_induced_pullback":
            defect = 0.031 * (1.0 + 0.2 * np.sin(points[:, 0]))
            metric = decoded["sides"]["plus"]["g_trace"]
            metric[:, 0, 1] += defect
            metric[:, 1, 0] += defect
        elif mutation == "break_gluing":
            defect = 0.043 * (1.0 + 0.2 * np.cos(points[:, 1]))
            decoded["sides"]["plus"]["A_trace_full"][:, 0, 0] += defect
        else:
            raise SpecialMutantError(f"unknown decoder mutation: {mutation}")
        return decoded

    with _patched(route_b, "decode_pointwise_free_boundary", mutated_decoder):
        return route_b.action_evaluation(
            free, bundle, member, TANGENTIAL_Q, RADIAL_Q, "refinable"
        )


def _bulk_mutant_evaluation(
    route_b: Any,
    free: np.ndarray,
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    mutation: str,
) -> Mapping[str, Any]:
    original = route_b.bulk_action_components

    def mutated_bulk(
        state: Mapping[str, np.ndarray],
        tangential_weights: np.ndarray,
        radial_weights: np.ndarray,
        parameters: Mapping[str, float],
        side: str,
        inertia_records: dict[str, list[Mapping[str, float | int]]] | None = None,
    ) -> Mapping[str, float]:
        values = dict(
            original(
                state,
                tangential_weights,
                radial_weights,
                parameters,
                side,
                inertia_records,
            )
        )
        Z5 = float(parameters["material_Z5_per_side"])
        mass = float(parameters["material_mass_M"])
        delta = 0.0
        for p in range(state["g"].shape[0]):
            for r in range(state["g"].shape[1]):
                metric = state["g"][p, r]
                inverse = np.linalg.inv(metric)
                volume = math.sqrt(-float(np.linalg.det(metric)))
                weight = float(tangential_weights[p] * radial_weights[r])
                Omega = float(state["Omega"][p, r])
                phi = state["phi"][p, r]
                if mutation == "V4_anisotropic":
                    argument = Omega ** 1.5 * float(np.linalg.norm(phi))
                    anisotropic_piece = (
                        0.37
                        * (Omega ** 1.5 * float(phi[0])) ** 4
                        / (2.0 * math.sqrt(1.0 + argument ** 4))
                    )
                    delta += weight * volume * (
                        -Z5 * mass ** 2 * Omega ** -5.0 * anisotropic_piece
                    )
                elif mutation == "remove_coordinate_T0i_matter_contractions":
                    A = state["A"][p, r]
                    covariant_phi = np.empty((5, 3), dtype=float)
                    for M in range(5):
                        covariant_phi[M] = (
                            state["dphi"][p, r, M]
                            + np.cross(A[M], phi)
                            + 1.5 * phi * state["dlog_Omega"][p, r, M]
                        )
                    removed = 2.0 * math.fsum(
                        float(inverse[0, i] * (covariant_phi[0] @ covariant_phi[i]))
                        for i in range(1, 4)
                    )
                    delta += weight * volume * (Z5 * removed / 2.0)
                else:
                    raise SpecialMutantError(f"unknown bulk mutation: {mutation}")
        target = (
            f"full_V4_bulk_{side}"
            if mutation == "V4_anisotropic"
            else f"P_kinetic_bulk_{side}"
        )
        values[target] += float(delta)
        return values

    with _patched(route_b, "bulk_action_components", mutated_bulk):
        return route_b.action_evaluation(
            free, bundle, member, TANGENTIAL_Q, RADIAL_Q, "refinable"
        )


def _freeze_r_record(
    route_b: Any,
    free: np.ndarray,
    tangent: np.ndarray,
    layout: Mapping[str, Any],
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
    nominal_ad: Mapping[str, float],
) -> Mapping[str, Any]:
    mutated_tangent = freeze_relative_rotation_tangent(tangent, layout)
    original_r_norm = math.sqrt(
        math.fsum(
            float(value * value)
            for side in route_b.SIDES
            for value in _block_view(tangent, layout, f"{side}.r_E0").ravel()
        )
    )
    window = route_b.affine_fd5_step_window(
        free,
        mutated_tangent,
        (COARSE_STEP, FINE_STEP),
        bundle,
        member,
        TANGENTIAL_Q,
        RADIAL_Q,
        "refinable",
    )
    coarse = window["derivatives"][0]["FD5_action_directional_derivative"]
    fine = window["derivatives"][1]["FD5_action_directional_derivative"]
    richardson = {
        component: float(fine[component] + (fine[component] - coarse[component]) / 15.0)
        for component in route_b.ACTION_COMPONENTS + ("S_total",)
    }
    residual = np.asarray(
        [richardson[name] - float(nominal_ad[name]) for name in route_b.ACTION_COMPONENTS],
        dtype=float,
    )
    reference = np.asarray(
        [float(nominal_ad[name]) for name in route_b.ACTION_COMPONENTS], dtype=float
    )
    relative_l2 = float(np.linalg.norm(residual) / max(np.linalg.norm(reference), 1.0))
    max_gluing = max(
        float(record["pointwise_gluing_Linf"])
        for record in window["endpoint_records_by_float_hex"].values()
    )
    return {
        "id": "freeze_relative_R",
        "intervention": "set both side.r_E0 tangent blocks to zero before endpoint construction",
        "original_relative_R_tangent_L2": original_r_norm,
        "mutated_relative_R_tangent_L2": 0.0,
        "mutated_Richardson_derivative": richardson,
        "nominal_AD_derivative": nominal_ad,
        "AD_minus_mutated_FD5_component_residual_L2": float(np.linalg.norm(residual)),
        "AD_minus_mutated_FD5_relative_L2": relative_l2,
        "maximum_endpoint_pointwise_gluing_Linf": max_gluing,
        "endpoint_count": int(window["unique_endpoint_count"]),
        "killed_by_derivative_comparator": bool(
            original_r_norm > 0.0 and relative_l2 > DERIVATIVE_KILL_REL_L2
        ),
    }


def _matter_t_ui_activity(
    route_b: Any,
    free: np.ndarray,
    bundle: Mapping[str, Any],
    member: Mapping[str, Any],
) -> Mapping[str, Any]:
    tangential = route_b.tangential_quadrature(TANGENTIAL_Q)
    points = tangential["points"]
    weights = tangential["weights"]
    decoded = route_b.decode_pointwise_free_boundary(free, bundle, points)
    layout = bundle["pointwise_decoder_contract"]["free_layout"]["blocks"]
    tables = route_b.fourier_tables(bundle["pointwise_decoder_contract"]["basis"], points)
    _T, T_first, _T_second = route_b._spectral(
        route_b._layout_get(free, layout, "common.T"), tables
    )
    Z5 = float(bundle["action_contract"]["coefficient_parameters"]["material_Z5_per_side"])
    integrated: dict[str, list[float]] = {}
    pointwise_max = 0.0
    action_shift_max_error = 0.0
    action_shift_rows: list[Mapping[str, Any]] = []
    for side in route_b.SIDES:
        state = route_b.decode_bulk_state(
            free,
            bundle,
            points,
            TANGENTIAL_Q,
            np.asarray((0.0,), dtype=float),
            side,
            int(member["N"]),
            int(member["K"]),
        )
        accumulator = np.zeros(3, dtype=float)
        for p in range(points.shape[0]):
            gamma = decoded["common"]["gamma"][p]
            inverse_gamma = np.linalg.inv(gamma)
            time_gradient = T_first[p, :, 0].copy()
            time_gradient[0] += 1.0
            norm = -float(time_gradient @ inverse_gamma @ time_gradient)
            if norm <= 0.0:
                raise SpecialMutantError("non-timelike khronon in T_ui witness")
            u_covector = -time_gradient / math.sqrt(norm)
            u_vector = inverse_gamma @ u_covector
            phi = state["phi"][p, 0]
            covariant_phi = np.empty((5, 3), dtype=float)
            for M in range(5):
                covariant_phi[M] = (
                    state["dphi"][p, 0, M]
                    + np.cross(state["A"][p, 0, M], phi)
                    + 1.5 * phi * state["dlog_Omega"][p, 0, M]
                )
            tangent = np.zeros((5, 4), dtype=float)
            tangent[:4] = np.eye(4)
            tangent[4] = state["Y_first"][p]
            pulled = np.einsum("Mm,Ma->ma", tangent, covariant_phi)
            h = gamma[1:, 1:]
            beta = np.linalg.solve(h, gamma[0, 1:])
            lapse_squared = -float(gamma[0, 0]) + float(beta @ h @ beta)
            if lapse_squared <= 0.0:
                raise SpecialMutantError("non-positive ADM lapse in T_ui witness")
            lapse = math.sqrt(lapse_squared)
            spatial_volume = math.sqrt(float(np.linalg.det(h)))

            def matter_action(local_beta: np.ndarray) -> float:
                local_gamma = np.empty((4, 4), dtype=float)
                local_gamma[1:, 1:] = h
                local_gamma[0, 1:] = h @ local_beta
                local_gamma[1:, 0] = local_gamma[0, 1:]
                local_gamma[0, 0] = -lapse * lapse + float(local_beta @ h @ local_beta)
                local_inverse = np.linalg.inv(local_gamma)
                p_squared = float(
                    np.einsum("mn,ma,na->", local_inverse, pulled, pulled)
                )
                return lapse * spatial_volume * (-0.5 * Z5 * p_squared)

            p_up = inverse_gamma @ pulled
            p_squared = float(np.einsum("mn,ma,na->", inverse_gamma, pulled, pulled))
            lagrangian = -0.5 * Z5 * p_squared
            stress = Z5 * np.einsum("ma,na->mn", p_up, p_up)
            stress += lagrangian * inverse_gamma
            adm_u_covector = np.asarray((-lapse, 0.0, 0.0, 0.0), dtype=float)
            current = np.asarray(adm_u_covector @ stress @ gamma[:, 1:], dtype=float)
            expected_shift = -current / lapse
            numerical_shift = np.empty(3, dtype=float)
            for index in range(3):
                direction = np.eye(3)[index]
                h_fd = T_UI_FD5_STEP
                numerical_shift[index] = math.fsum(
                    (
                        matter_action(beta - 2.0 * h_fd * direction),
                        -8.0 * matter_action(beta - h_fd * direction),
                        8.0 * matter_action(beta + h_fd * direction),
                        -matter_action(beta + 2.0 * h_fd * direction),
                    )
                ) / (12.0 * h_fd * lapse * spatial_volume)
            local_error = float(np.max(np.abs(numerical_shift - expected_shift)))
            action_shift_max_error = max(action_shift_max_error, local_error)
            if p in (0, points.shape[0] // 2, points.shape[0] - 1):
                action_shift_rows.append(
                    {
                        "side": side,
                        "point_index": p,
                        "lapse": lapse,
                        "shift": beta.tolist(),
                        "T_ui": current.tolist(),
                        "minus_T_ui_over_N": expected_shift.tolist(),
                        "independent_local_action_FD5_shift_derivative": numerical_shift.tolist(),
                        "maximum_absolute_error": local_error,
                    }
                )
            pointwise_max = max(pointwise_max, float(np.max(np.abs(current))))
            accumulator += (
                float(weights[p]) * math.sqrt(-float(np.linalg.det(gamma))) * current
            )
        integrated[side] = accumulator.tolist()
    combined = np.sum(np.asarray(list(integrated.values()), dtype=float), axis=0)
    return {
        "definition": "T_ui=Z5*(u^mu P_mu) dot (b_i^nu P_nu); trace and potential terms vanish because u dot b_i=0",
        "integrated_T_ui_by_side": integrated,
        "combined_integrated_T_ui": combined.tolist(),
        "combined_integrated_T_ui_L2": float(np.linalg.norm(combined)),
        "pointwise_T_ui_Linf": pointwise_max,
        "local_action_shift_FD5_step": T_UI_FD5_STEP,
        "local_action_shift_maximum_absolute_error": action_shift_max_error,
        "raw_representative_action_shift_rows": action_shift_rows,
        "omit_T_ui_mutant": [0.0, 0.0, 0.0],
        "omit_T_ui_mutant_witness_L2": float(np.linalg.norm(combined)),
        "nonzero_same_family_current_witness_pass": bool(
            np.linalg.norm(combined) > T_UI_ACTIVITY_MIN
            and pointwise_max > T_UI_ACTIVITY_MIN
        ),
        "independent_action_shift_JVP_match_pass": bool(
            action_shift_max_error < T_UI_ACTION_SHIFT_MAX_ERROR
        ),
        "scope_note": "At every Q5 boundary node and on both sides, the stress projection from the literal covariant matter kinetic term is compared with an independently reconstructed local ADM action and FD5 differentiation at fixed lapse, spatial metric, and covariant matter jet. This closes the local T_ui slot, not the still-open full Euler-Green identity.",
    }


def build_payload() -> dict[str, Any]:
    route_b, route_a_receipt, route_b_receipt, bundle = load_inputs()
    member = bundle["primary_member"]
    layout = bundle["pointwise_decoder_contract"]["free_layout"]["blocks"]
    free = route_b._decode_f64(member["authoritative_free_central_f64le"])
    joint = next(
        curve
        for curve in member["curves"]
        if curve["comparison_role"] == "primary_scientific_comparator"
    )
    tangent = route_b._decode_f64(joint["authoritative_free_tangent_f64le"])
    nominal = {
        key: float(value)
        for key, value in route_b_receipt["scientific"]["central_S_rel_components"].items()
    }
    nominal_ad = {
        key: float(value)
        for key, value in route_a_receipt["scientific"]["AD_JVP_by_component"].items()
    }

    records: list[Mapping[str, Any]] = []
    records.append(
        _freeze_r_record(
            route_b, free, tangent, layout, bundle, member, nominal_ad
        )
    )
    for mutation, intervention in (
        ("rotate_phi_only", "rotate both bulk phi traces without A, B, or common varphi"),
        ("break_induced_pullback", "perturb plus g_01 trace after common-first metric reconstruction"),
        ("break_gluing", "perturb plus tangential A_0^1 without its common trace"),
    ):
        evaluation = _decoder_mutant_evaluation(
            route_b, free, bundle, member, mutation
        )
        records.append(_central_record(mutation, intervention, evaluation, nominal))
    for mutation, intervention in (
        ("V4_anisotropic", "add 0.37*(Omega^(3/2)*phi_1)^4 to the radial V4 numerator"),
        (
            "remove_coordinate_T0i_matter_contractions",
            "delete 2*g^(0i)*P_0 dot P_i, i=1..3, from the bulk matter kinetic contraction",
        ),
    ):
        evaluation = _bulk_mutant_evaluation(route_b, free, bundle, member, mutation)
        records.append(_central_record(mutation, intervention, evaluation, nominal))

    z2_before = z2_free_residual(free, layout, route_b)
    z2_free = impose_reflected_z2_free_data(free, layout, route_b)
    z2_after = z2_free_residual(z2_free, layout, route_b)
    z2_evaluation = route_b.action_evaluation(
        z2_free, bundle, member, TANGENTIAL_Q, RADIAL_Q, "refinable"
    )
    z2_record = _central_record(
        "impose_reflected_Z2",
        "replace independent minus collar primitives by parity-reflected plus primitives",
        z2_evaluation,
        nominal,
    )
    z2_record["non_Z2_distance_before_mutation_Linf"] = z2_before
    z2_record["reflected_Z2_residual_after_mutation_Linf"] = z2_after
    z2_record["killed_by_action_or_gluing"] = bool(
        z2_record["killed_by_action_or_gluing"]
        and z2_before > ACTION_DELTA_KILL_ABS
        and z2_after == 0.0
    )
    records.append(z2_record)

    t_ui = _matter_t_ui_activity(route_b, free, bundle, member)
    executed_killed = all(bool(record["killed_by_action_or_gluing"])
                          if "killed_by_action_or_gluing" in record
                          else bool(record["killed_by_derivative_comparator"])
                          for record in records)
    exact_t_ui = bool(t_ui["independent_action_shift_JVP_match_pass"])
    all_special = bool(executed_killed and exact_t_ui)
    return {
        "schema": SCHEMA,
        "classification": "theory_only;finite_N2;Q5xQ3;non_additive_mutation_harness;fail_closed",
        "decision": {
            "freeze_relative_R_mutant_pass": bool(records[0]["killed_by_derivative_comparator"]),
            "rotate_phi_only_mutant_pass": bool(records[1]["killed_by_action_or_gluing"]),
            "break_induced_pullback_mutant_pass": bool(records[2]["killed_by_action_or_gluing"]),
            "break_gluing_mutant_pass": bool(records[3]["killed_by_action_or_gluing"]),
            "V4_anisotropic_mutant_pass": bool(records[4]["killed_by_action_or_gluing"]),
            "coordinate_T0i_contraction_mutant_pass": bool(records[5]["killed_by_action_or_gluing"]),
            "impose_reflected_Z2_mutant_pass": bool(records[6]["killed_by_action_or_gluing"]),
            "T_ui_matter_nonzero_same_family_witness_pass": bool(
                t_ui["nonzero_same_family_current_witness_pass"]
            ),
            "T_ui_matter_independent_action_shift_JVP_match_pass": exact_t_ui,
            "executed_nonadditive_mutants_killed": executed_killed,
            "special_geometric_action_mutants_pass": all_special,
            "Euler_Green_independent_route_pass": False,
            "independent_clean_process_redteam_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "fixed_before_run": {
            "tangential_points_per_axis": TANGENTIAL_Q,
            "radial_gauss_order": RADIAL_Q,
            "freeze_R_FD5_steps": [COARSE_STEP, FINE_STEP],
            "action_component_delta_kill_abs": ACTION_DELTA_KILL_ABS,
            "pointwise_gluing_kill_Linf": GLUING_KILL_LINF,
            "freeze_R_derivative_kill_relative_L2": DERIVATIVE_KILL_REL_L2,
            "T_ui_activity_min": T_UI_ACTIVITY_MIN,
            "T_ui_local_action_FD5_step": T_UI_FD5_STEP,
            "T_ui_action_shift_maximum_error": T_UI_ACTION_SHIFT_MAX_ERROR,
        },
        "scientific": {
            "records": records,
            "matter_T_ui": t_ui,
        },
        "source_pins": {
            "route_B_source_sha256": ROUTE_B_SOURCE_SHA256,
            "route_A_artifact_sha256": ROUTE_A_ARTIFACT_SHA256,
            "route_B_artifact_sha256": ROUTE_B_ARTIFACT_SHA256,
            "primitive_bundle_sha256": route_b.BUNDLE_SHA256,
            "literal_v5_2_action_sha256": route_b.LITERAL_ACTION_SHA256,
        },
        "open_obligations": [
            "circular Eulerian-route mutant, which belongs to the still-open Euler-Green comparator",
            "clean-process independent reproduction of the special-mutant campaign",
            "multi-N action comparison and continuous-limit theorem",
        ],
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST) if TEST.exists() else None,
            },
        },
        "evidence_boundary": "Seven non-additive interventions are executed on the finite N=2 Q5xQ3 family and detected. The local matter T_ui projection also matches an independently differentiated local ADM matter action at every Q5 boundary node. This does not derive the full Euler-Green identity, provide a clean independent red-team, establish multi-N uniform convergence, or authorize C1/N1.",
    }


def main() -> None:
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
