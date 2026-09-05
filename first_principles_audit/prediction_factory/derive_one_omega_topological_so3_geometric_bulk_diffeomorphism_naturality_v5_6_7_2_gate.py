#!/usr/bin/env python3
"""Exact proof ledger for geometric v5.2 finite bulk-diffeomorphism naturality.

This unit is deliberately independent of the numerical Route-C action units.
It byte-pins the literal geometric ``S_v5.2`` charter and the v5.6.1 open
obligation, binds every literal action term to a typed geometric expression,
and checks finite pullback naturality with a small free-word normalizer.  The
unexpanded local/compact-support chain-rule corollary is then recorded as the
formal derivative of that finite identity on smooth selected-sector fields and
compactly supported generators.

The certificate is exact relative to the finite list of standard
differential-geometric axioms reported by :func:`build_report`.  It is not a
proof-assistant kernel.  It contains no numerical sample, tolerance,
quadrature, decoder, relative-action subtraction, or Sobolev extension.
Material shape motion and the fixed-external-background relative functional
remain explicitly outside the promoted claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"

V52_SOURCE = HERE / "derive_one_omega_topological_so3_classical_v5_2_gate.py"
V52_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_classical_v5_2_gate.json"
V52_TEST = HERE / "test_one_omega_topological_so3_classical_v5_2_gate.py"
V561_SOURCE = HERE / "derive_one_omega_topological_so3_v5_6_1_quarantine_gate.py"
V561_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_v5_6_1_quarantine_gate.json"
V561_TEST = HERE / "test_one_omega_topological_so3_v5_6_1_quarantine_gate.py"

SCHEMA = (
    "holo.one-omega-topological-so3-geometric-bulk-diffeomorphism-"
    "naturality-v5-6-7-2-gate.v1"
)
V52_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
V561_SCHEMA = "holo.one-omega-topological-so3-v5-6-1-quarantine-gate.v2"

EXPECTED_SHA256 = {
    "v5_2_source": "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
    "v5_2_artifact": "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
    "v5_2_test": "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
    "v5_6_1_source": "e31ab6f983ba7cef43a0e6b334d7f294612dd49726d88e5a34ba4d3a57b99bc2",
    "v5_6_1_artifact": "b83c7ae67a7e285ca7feb05afae95b8e9ae685da0f31d84d55a5824007b23e03",
    "v5_6_1_test": "00b06af19d4a9e1db85f1dfd83d42f1924a849167a36e7d70480876ab5b44581",
}

# Keep this separate from the file pins: it binds the canonical sorted JSON
# value of exact_classical_charter.exact_action rather than its presentation.
V52_EXACT_ACTION_SHA256 = (
    "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
)

SIDES = ("plus", "minus")
BULK_SECTORS = (
    "EH",
    "Omega_kinetic",
    "Omega_potential",
    "P_kinetic",
    "full_V4",
    "BF",
)
INTERFACE_SECTORS = (
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
    for name in tuple(f"{sector}_bulk_{side}" for sector in BULK_SECTORS)
    + (f"GHY_{side}",)
) + INTERFACE_SECTORS

TRUE_DECISION_KEYS = frozenset(
    {
        "v5_2_geometric_action_and_v5_6_1_obligation_byte_pinned_pass",
        "finite_complete_domain_pullback_identity_exact_pass",
        "literal_v5_2_twenty_component_naturality_inventory_complete_pass",
        "finite_associated_matter_solder_groupoid_word_covariance_exact_pass",
        "finite_typed_geometric_S_v5_2_action_expression_covariance_exact_pass",
        "formal_local_compact_support_chain_rule_corollary_DS_G_zero_exact_pass",
    }
)
FALSE_DECISION_KEYS = frozenset(
    {
        "finite_full_affine_connection_trace_transport_exact_pass",
        "oriented_BF_incidence_cancellation_exact_pass",
        "literal_bulk_interface_Green_ledger_pass",
        "differentiated_smooth_compact_support_bulk_Ward_identity_exact_pass",
        "full_bulk_diffeomorphism_Ward_pass",
        "fixed_reference_S_rel_diffeomorphism_Ward_pass",
        "complete_moving_embedding_Ward_pass",
        "complete_v5_2_all_field_normal_embedding_pass",
        "full_off_shell_Green_theorem_accepted",
        "global_noncompact_action_finite_pass",
        "continuum_all_configurations_theorem_pass",
        "full_classical_variational_principle_selected_sector_pass",
        "numerical_sample_constitutes_naturality_proof_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "P4_full_same_action_pass",
        "C1_N1_promotion_authorized",
        "B4_pass",
        "B5_pass",
    }
)


class NaturalityCertificateError(RuntimeError):
    """A byte pin, type rule, exact reduction, or quarantine boundary failed."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_json_pin(path: Path, expected_sha256: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise NaturalityCertificateError(
            f"byte pin drift for {path.name}: {observed} != {expected_sha256}"
        )
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise NaturalityCertificateError(f"JSON object required: {path.name}")
    return loaded


@dataclass(frozen=True, order=True)
class GeometricType:
    """A minimal carrier/type tag used by the proof-expression checker."""

    name: str
    dimension: int
    form_degree: int | None = None


METRIC5 = GeometricType("Lorentzian_metric", 5)
INVERSE_METRIC5 = GeometricType("inverse_metric", 5)
SCALAR5 = GeometricType("scalar", 5, 0)
COVECTOR5 = GeometricType("covector", 5, 1)
FORM5 = GeometricType("top_form", 5, 5)
ASSOCIATED0_5 = GeometricType("SO3_associated_form", 5, 0)
ASSOCIATED1_5 = GeometricType("SO3_associated_form", 5, 1)
CONNECTION1_5 = GeometricType("SO3_connection", 5, 1)
ADJOINT2_5 = GeometricType("SO3_adjoint_form", 5, 2)
ADJOINT3_5 = GeometricType("SO3_adjoint_form", 5, 3)

METRIC4 = GeometricType("induced_metric", 4)
INVERSE_METRIC4 = GeometricType("inverse_metric", 4)
SCALAR4 = GeometricType("scalar", 4, 0)
COVECTOR4 = GeometricType("covector", 4, 1)
VECTOR4 = GeometricType("vector", 4)
FORM4 = GeometricType("top_form", 4, 4)


@dataclass(frozen=True)
class Manifold:
    name: str
    dimension: int


@dataclass(frozen=True)
class MapAtom:
    name: str
    source: Manifold
    target: Manifold


@dataclass(frozen=True)
class MapComposition:
    """The map ``outer o inner`` with a checked source/target boundary."""

    outer: MapAtom | MapComposition
    inner: MapAtom | MapComposition

    def __post_init__(self) -> None:
        if _map_target(self.inner) != _map_source(self.outer):
            raise NaturalityCertificateError(
                "ill-typed map composition: inner target differs from outer source"
            )


MapExpression = MapAtom | MapComposition


def _map_source(value: MapExpression) -> Manifold:
    return value.source if isinstance(value, MapAtom) else _map_source(value.inner)


def _map_target(value: MapExpression) -> Manifold:
    return value.target if isinstance(value, MapAtom) else _map_target(value.outer)


def compose(outer: MapExpression, inner: MapExpression) -> MapComposition:
    return MapComposition(outer=outer, inner=inner)


def pullback_word(value: MapExpression) -> tuple[str, ...]:
    """Expand pullback contravariance: ``(g o f)^* = f^* g^*``."""

    if isinstance(value, MapAtom):
        return (value.name,)
    return pullback_word(value.inner) + pullback_word(value.outer)


def _inverse_word(name: str) -> str:
    suffix = "^-1"
    return name[: -len(suffix)] if name.endswith(suffix) else f"{name}{suffix}"


def reduce_free_word(factors: Sequence[str]) -> tuple[tuple[str, ...], tuple[dict[str, Any], ...]]:
    """Cancel adjacent inverse generators and return an inspectable trace."""

    stack: list[str] = []
    steps: list[dict[str, Any]] = []
    for factor in factors:
        if stack and _inverse_word(stack[-1]) == factor:
            left = stack.pop()
            steps.append(
                {
                    "rule": "adjacent_inverse_cancellation",
                    "cancelled": [left, factor],
                    "remaining_prefix": list(stack),
                }
            )
        else:
            stack.append(factor)
    return tuple(stack), tuple(steps)


@dataclass(frozen=True)
class PulledField:
    name: str
    type_tag: GeometricType
    pullback_factors: tuple[str, ...]


@dataclass(frozen=True)
class SolderedMatter:
    """Boundary associated matter with both pullback and frame/groupoid words."""

    name: str
    type_tag: GeometricType
    pullback_factors: tuple[str, ...]
    groupoid_factors: tuple[str, ...]


@dataclass(frozen=True)
class Construction:
    operator: str
    arguments: tuple[Expression, ...]
    type_tag: GeometricType


Expression = PulledField | SolderedMatter | Construction


@dataclass(frozen=True)
class OperatorSpec:
    inputs: tuple[GeometricType, ...]
    output: GeometricType
    naturality_axiom: str


OPERATOR_SPECS: Mapping[str, OperatorSpec] = {
    "scalar_curvature": OperatorSpec((METRIC5,), SCALAR5, "curvature_is_natural"),
    "bulk_volume": OperatorSpec((METRIC5,), FORM5, "metric_volume_is_natural"),
    "inverse_metric5": OperatorSpec((METRIC5,), INVERSE_METRIC5, "metric_inverse_is_natural"),
    "exterior_derivative_scalar5": OperatorSpec((SCALAR5,), COVECTOR5, "exterior_derivative_commutes_with_pullback"),
    "d_log_Omega": OperatorSpec((SCALAR5,), COVECTOR5, "smooth_scalar_composition_is_natural"),
    "contract_covectors5": OperatorSpec(
        (INVERSE_METRIC5, COVECTOR5, COVECTOR5),
        SCALAR5,
        "metric_contraction_is_natural",
    ),
    "superpotential": OperatorSpec((SCALAR5,), SCALAR5, "smooth_scalar_composition_is_natural"),
    "superpotential_derivative": OperatorSpec((SCALAR5,), SCALAR5, "smooth_scalar_composition_is_natural"),
    "bulk_potential_from_W": OperatorSpec(
        (SCALAR5, SCALAR5), SCALAR5, "smooth_scalar_composition_is_natural"
    ),
    "covariant_derivative_phi": OperatorSpec(
        (CONNECTION1_5, ASSOCIATED0_5),
        ASSOCIATED1_5,
        "associated_covariant_derivative_is_natural",
    ),
    "conformal_P": OperatorSpec(
        (ASSOCIATED1_5, ASSOCIATED0_5, COVECTOR5),
        ASSOCIATED1_5,
        "tensor_sum_and_product_are_natural",
    ),
    "associated_one_form_norm": OperatorSpec(
        (INVERSE_METRIC5, ASSOCIATED1_5, ASSOCIATED1_5),
        SCALAR5,
        "SO3_pairing_and_metric_contraction_are_natural",
    ),
    "associated_scalar_norm": OperatorSpec(
        (ASSOCIATED0_5,), SCALAR5, "SO3_invariant_pairing_is_natural"
    ),
    "weighted_full_V4": OperatorSpec(
        (SCALAR5, SCALAR5), SCALAR5, "smooth_scalar_composition_is_natural"
    ),
    "multiply_bulk_scalar_density": OperatorSpec(
        (SCALAR5, FORM5), FORM5, "wedge_and_scalar_multiplication_are_natural"
    ),
    "connection_curvature": OperatorSpec(
        (CONNECTION1_5,), ADJOINT2_5, "connection_curvature_is_natural"
    ),
    "invariant_B_wedge_F": OperatorSpec(
        (ADJOINT3_5, ADJOINT2_5),
        FORM5,
        "SO3_invariant_pairing_and_wedge_are_natural",
    ),
    "induced_boundary_metric": OperatorSpec(
        (METRIC5,), METRIC4, "restriction_and_induced_metric_are_natural"
    ),
    "boundary_trace_scalar": OperatorSpec(
        (SCALAR5,), SCALAR4, "restriction_commutes_with_pullback"
    ),
    "boundary_volume": OperatorSpec((METRIC4,), FORM4, "metric_volume_is_natural"),
    "outward_mean_curvature": OperatorSpec(
        (METRIC5,),
        SCALAR4,
        "outward_normal_and_extrinsic_curvature_are_natural",
    ),
    "wall_scalar": OperatorSpec(
        (SCALAR4,), SCALAR4, "smooth_scalar_composition_is_natural"
    ),
    "khronon_K_quadratic": OperatorSpec(
        (METRIC4, SCALAR4),
        SCALAR4,
        "fixed_abstract_khronon_composites_are_natural",
    ),
    "khronon_spatial_curvature": OperatorSpec(
        (METRIC4, SCALAR4),
        SCALAR4,
        "fixed_abstract_khronon_composites_are_natural",
    ),
    "square_boundary_scalar": OperatorSpec(
        (SCALAR4,), SCALAR4, "tensor_sum_and_product_are_natural"
    ),
    "khronon_acceleration": OperatorSpec(
        (METRIC4, SCALAR4),
        COVECTOR4,
        "fixed_abstract_khronon_composites_are_natural",
    ),
    "inverse_metric4": OperatorSpec((METRIC4,), INVERSE_METRIC4, "metric_inverse_is_natural"),
    "contract_covectors4": OperatorSpec(
        (INVERSE_METRIC4, COVECTOR4, COVECTOR4),
        SCALAR4,
        "metric_contraction_is_natural",
    ),
    "Robin_groupoid_quadratic": OperatorSpec(
        (VECTOR4, COVECTOR4, METRIC4),
        SCALAR4,
        "finite_frame_groupoid_soldering_is_natural",
    ),
    "multiply_boundary_scalar_density": OperatorSpec(
        (SCALAR4, FORM4), FORM4, "wedge_and_scalar_multiplication_are_natural"
    ),
}

KERNEL_AXIOMS = tuple(
    sorted({spec.naturality_axiom for spec in OPERATOR_SPECS.values()})
) + (
    "pullback_identity_and_contravariant_functoriality",
    "finite_frame_groupoid_soldering_covariance",
    "flow_pullback_derivative_is_Lie_derivative",
    "inverse_flow_embedding_derivative_has_negative_sign",
    "chain_rule_for_smooth_local_functionals",
    "compact_support_removes_the_exhaustion_boundary_flux",
)
EXPECTED_KERNEL_AXIOMS = frozenset(
    {
        "SO3_invariant_pairing_and_wedge_are_natural",
        "SO3_invariant_pairing_is_natural",
        "SO3_pairing_and_metric_contraction_are_natural",
        "associated_covariant_derivative_is_natural",
        "chain_rule_for_smooth_local_functionals",
        "compact_support_removes_the_exhaustion_boundary_flux",
        "connection_curvature_is_natural",
        "curvature_is_natural",
        "exterior_derivative_commutes_with_pullback",
        "finite_frame_groupoid_soldering_covariance",
        "finite_frame_groupoid_soldering_is_natural",
        "fixed_abstract_khronon_composites_are_natural",
        "flow_pullback_derivative_is_Lie_derivative",
        "inverse_flow_embedding_derivative_has_negative_sign",
        "metric_contraction_is_natural",
        "metric_inverse_is_natural",
        "metric_volume_is_natural",
        "outward_normal_and_extrinsic_curvature_are_natural",
        "pullback_identity_and_contravariant_functoriality",
        "restriction_and_induced_metric_are_natural",
        "restriction_commutes_with_pullback",
        "smooth_scalar_composition_is_natural",
        "tensor_sum_and_product_are_natural",
        "wedge_and_scalar_multiplication_are_natural",
    }
)


def construct(operator: str, *arguments: Expression) -> Construction:
    if operator not in OPERATOR_SPECS:
        raise NaturalityCertificateError(f"unknown natural operator: {operator}")
    spec = OPERATOR_SPECS[operator]
    observed = tuple(argument.type_tag for argument in arguments)
    if observed != spec.inputs:
        raise NaturalityCertificateError(
            f"type mismatch for {operator}: {observed!r} != {spec.inputs!r}"
        )
    return Construction(operator=operator, arguments=tuple(arguments), type_tag=spec.output)


def _side_maps(side: str) -> tuple[MapAtom, MapAtom, MapAtom]:
    if side not in SIDES:
        raise NaturalityCertificateError(f"unknown side: {side}")
    domain = Manifold(f"D_{side}", 5)
    physical = Manifold(f"M_{side}", 5)
    complete_map = MapAtom(f"F_{side}", domain, physical)
    diffeomorphism = MapAtom(f"Phi_{side}", physical, physical)
    inverse = MapAtom(f"Phi_{side}^-1", physical, physical)
    return complete_map, diffeomorphism, inverse


def _transformation_words(
    side: str,
    mode: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return separate complete-map and physical-field pullback words."""

    complete_map, diffeomorphism, inverse = _side_maps(side)
    if mode == "baseline":
        return pullback_word(complete_map), ()
    if mode == "finite":
        transformed_complete_map = compose(inverse, complete_map)
        return (
            pullback_word(transformed_complete_map),
            pullback_word(diffeomorphism),
        )
    if mode == "frozen_complete_map":
        return pullback_word(complete_map), pullback_word(diffeomorphism)
    if mode == "wrong_inverse_complete_map":
        transformed_complete_map = compose(diffeomorphism, complete_map)
        return (
            pullback_word(transformed_complete_map),
            pullback_word(diffeomorphism),
        )
    if mode == "omitted_field_pullback":
        transformed_complete_map = compose(inverse, complete_map)
        return pullback_word(transformed_complete_map), ()
    raise NaturalityCertificateError(f"unknown field transformation mode: {mode}")


def _bulk_field(
    side: str,
    name: str,
    type_tag: GeometricType,
    mode: str,
) -> PulledField:
    complete_word, field_word = _transformation_words(side, mode)
    factors = complete_word + field_word
    return PulledField(
        name=f"{name}_{side}",
        type_tag=type_tag,
        pullback_factors=factors,
    )


def _fixed_khronon(transform_mutant: bool) -> PulledField:
    return PulledField(
        name="T_on_abstract_Sigma",
        type_tag=SCALAR4,
        pullback_factors=("Psi_Sigma",) if transform_mutant else (),
    )


def _soldered_matter(
    mode: str,
    groupoid_mode: str,
) -> SolderedMatter:
    phi = _bulk_field("plus", "phi", ASSOCIATED0_5, mode)
    if groupoid_mode == "baseline":
        groupoid = ("E", "R", "phi")
    elif groupoid_mode == "finite":
        groupoid = (
            "E",
            "gQ^-1",
            "gQ",
            "R",
            "gP^-1",
            "gP",
            "phi",
        )
    elif groupoid_mode == "frozen_frame":
        groupoid = ("E", "gQ", "R", "gP^-1", "gP", "phi")
    elif groupoid_mode == "missing_source_inverse":
        groupoid = ("E", "gQ^-1", "gQ", "R", "gP", "phi")
    else:
        raise NaturalityCertificateError(f"unknown groupoid mode: {groupoid_mode}")
    return SolderedMatter(
        name="varphi_H",
        type_tag=VECTOR4,
        pullback_factors=phi.pullback_factors,
        groupoid_factors=groupoid,
    )


def _side_components(side: str, mode: str) -> dict[str, Expression]:
    metric = _bulk_field(side, "g", METRIC5, mode)
    omega = _bulk_field(side, "Omega", SCALAR5, mode)
    phi = _bulk_field(side, "phi", ASSOCIATED0_5, mode)
    connection = _bulk_field(side, "A", CONNECTION1_5, mode)
    b_form = _bulk_field(side, "B", ADJOINT3_5, mode)

    inverse_metric = construct("inverse_metric5", metric)
    volume = construct("bulk_volume", metric)
    omega_gradient = construct("exterior_derivative_scalar5", omega)
    omega_norm = construct(
        "contract_covectors5", inverse_metric, omega_gradient, omega_gradient
    )
    superpotential = construct("superpotential", omega)
    superpotential_derivative = construct("superpotential_derivative", omega)
    potential = construct(
        "bulk_potential_from_W", superpotential_derivative, superpotential
    )
    d_phi = construct("covariant_derivative_phi", connection, phi)
    d_log_omega = construct("d_log_Omega", omega)
    conformal_p = construct("conformal_P", d_phi, phi, d_log_omega)
    p_norm = construct(
        "associated_one_form_norm", inverse_metric, conformal_p, conformal_p
    )
    phi_norm = construct("associated_scalar_norm", phi)
    v4 = construct("weighted_full_V4", omega, phi_norm)
    curvature = construct("connection_curvature", connection)
    boundary_metric = construct("induced_boundary_metric", metric)

    return {
        f"EH_bulk_{side}": construct(
            "multiply_bulk_scalar_density",
            construct("scalar_curvature", metric),
            volume,
        ),
        f"Omega_kinetic_bulk_{side}": construct(
            "multiply_bulk_scalar_density", omega_norm, volume
        ),
        f"Omega_potential_bulk_{side}": construct(
            "multiply_bulk_scalar_density", potential, volume
        ),
        f"P_kinetic_bulk_{side}": construct(
            "multiply_bulk_scalar_density", p_norm, volume
        ),
        f"full_V4_bulk_{side}": construct(
            "multiply_bulk_scalar_density", v4, volume
        ),
        f"BF_bulk_{side}": construct("invariant_B_wedge_F", b_form, curvature),
        f"GHY_{side}": construct(
            "multiply_boundary_scalar_density",
            construct("outward_mean_curvature", metric),
            construct("boundary_volume", boundary_metric),
        ),
    }


def build_component_expressions(
    mode: str,
    *,
    groupoid_mode: str | None = None,
    transform_khronon_mutant: bool = False,
) -> dict[str, Expression]:
    components: dict[str, Expression] = {}
    for side in SIDES:
        components.update(_side_components(side, mode))

    metric = _bulk_field("plus", "g", METRIC5, mode)
    omega = _bulk_field("plus", "Omega", SCALAR5, mode)
    gamma = construct("induced_boundary_metric", metric)
    gamma_inverse = construct("inverse_metric4", gamma)
    volume = construct("boundary_volume", gamma)
    omega_boundary = construct("boundary_trace_scalar", omega)
    khronon = _fixed_khronon(transform_khronon_mutant)
    spatial_curvature = construct("khronon_spatial_curvature", gamma, khronon)
    acceleration = construct("khronon_acceleration", gamma, khronon)
    acceleration_norm = construct(
        "contract_covectors4", gamma_inverse, acceleration, acceleration
    )
    selected_groupoid_mode = groupoid_mode or (
        "baseline" if mode == "baseline" else "finite"
    )
    soldered = _soldered_matter(mode, selected_groupoid_mode)

    components.update(
        {
            "wall": construct(
                "multiply_boundary_scalar_density",
                construct("wall_scalar", omega_boundary),
                volume,
            ),
            "K_foliation": construct(
                "multiply_boundary_scalar_density",
                construct("khronon_K_quadratic", gamma, khronon),
                volume,
            ),
            "R": construct(
                "multiply_boundary_scalar_density", spatial_curvature, volume
            ),
            "R_squared": construct(
                "multiply_boundary_scalar_density",
                construct("square_boundary_scalar", spatial_curvature),
                volume,
            ),
            "a_squared": construct(
                "multiply_boundary_scalar_density", acceleration_norm, volume
            ),
            "Robin": construct(
                "multiply_boundary_scalar_density",
                construct("Robin_groupoid_quadratic", soldered, acceleration, gamma),
                volume,
            ),
        }
    )
    if tuple(components) != COMPONENT_NAMES:
        raise NaturalityCertificateError("twenty-component expression order drift")
    return components


def _render_expression(value: Expression) -> str:
    if isinstance(value, PulledField):
        prefix = " ".join(value.pullback_factors) or "Id"
        return f"PB[{prefix}]({value.name})"
    if isinstance(value, SolderedMatter):
        pullback = " ".join(value.pullback_factors) or "Id"
        groupoid = " ".join(value.groupoid_factors)
        return f"SOLDER[PB={pullback};G={groupoid}]({value.name})"
    arguments = ",".join(_render_expression(argument) for argument in value.arguments)
    return f"{value.operator}({arguments})"


def _normalize_expression(
    value: Expression,
    trace: list[dict[str, Any]],
) -> Expression:
    if isinstance(value, PulledField):
        reduced, steps = reduce_free_word(value.pullback_factors)
        trace.append(
            {
                "kind": "pullback_word",
                "field": value.name,
                "before": list(value.pullback_factors),
                "after": list(reduced),
                "steps": list(steps),
            }
        )
        return PulledField(value.name, value.type_tag, reduced)
    if isinstance(value, SolderedMatter):
        reduced_pullback, pullback_steps = reduce_free_word(value.pullback_factors)
        reduced_groupoid, groupoid_steps = reduce_free_word(value.groupoid_factors)
        trace.append(
            {
                "kind": "soldered_pullback_and_groupoid_words",
                "field": value.name,
                "pullback_before": list(value.pullback_factors),
                "pullback_after": list(reduced_pullback),
                "pullback_steps": list(pullback_steps),
                "groupoid_before": list(value.groupoid_factors),
                "groupoid_after": list(reduced_groupoid),
                "groupoid_steps": list(groupoid_steps),
            }
        )
        return SolderedMatter(
            value.name,
            value.type_tag,
            reduced_pullback,
            reduced_groupoid,
        )
    return Construction(
        value.operator,
        tuple(_normalize_expression(argument, trace) for argument in value.arguments),
        value.type_tag,
    )


def normalize_expression(value: Expression) -> tuple[Expression, tuple[dict[str, Any], ...]]:
    trace: list[dict[str, Any]] = []
    normalized = _normalize_expression(value, trace)
    return normalized, tuple(trace)


def _axioms_used(value: Expression) -> frozenset[str]:
    if isinstance(value, PulledField):
        return frozenset({"pullback_identity_and_contravariant_functoriality"})
    if isinstance(value, SolderedMatter):
        return frozenset(
            {
                "pullback_identity_and_contravariant_functoriality",
                "finite_frame_groupoid_soldering_covariance",
            }
        )
    return frozenset({OPERATOR_SPECS[value.operator].naturality_axiom}).union(
        *(_axioms_used(argument) for argument in value.arguments)
    )


def _type_signature(type_tag: GeometricType) -> tuple[str, int, int | None]:
    return type_tag.name, type_tag.dimension, type_tag.form_degree


def _field_role(name: str) -> str:
    if name == "T_on_abstract_Sigma":
        return "T"
    for side in SIDES:
        suffix = f"_{side}"
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return f"unrecognized:{name}"


def _expression_signature(value: Expression) -> tuple[Any, ...]:
    if isinstance(value, PulledField):
        return "field", _field_role(value.name), _type_signature(value.type_tag)
    if isinstance(value, SolderedMatter):
        return "soldered_matter", value.name, _type_signature(value.type_tag)
    return (
        "operator",
        value.operator,
        tuple(_expression_signature(argument) for argument in value.arguments),
    )


def _signature(operator: str, *arguments: tuple[Any, ...]) -> tuple[Any, ...]:
    return "operator", operator, tuple(arguments)


_G5 = ("field", "g", _type_signature(METRIC5))
_O5 = ("field", "Omega", _type_signature(SCALAR5))
_PHI5 = ("field", "phi", _type_signature(ASSOCIATED0_5))
_A5 = ("field", "A", _type_signature(CONNECTION1_5))
_B5 = ("field", "B", _type_signature(ADJOINT3_5))
_T4 = ("field", "T", _type_signature(SCALAR4))
_SOLDER = ("soldered_matter", "varphi_H", _type_signature(VECTOR4))

_INV5 = _signature("inverse_metric5", _G5)
_VOL5 = _signature("bulk_volume", _G5)
_D_OMEGA = _signature("exterior_derivative_scalar5", _O5)
_D_PHI = _signature("covariant_derivative_phi", _A5, _PHI5)
_D_LOG_OMEGA = _signature("d_log_Omega", _O5)
_P = _signature("conformal_P", _D_PHI, _PHI5, _D_LOG_OMEGA)
_GAMMA = _signature("induced_boundary_metric", _G5)
_VOL4 = _signature("boundary_volume", _GAMMA)
_ACCELERATION = _signature("khronon_acceleration", _GAMMA, _T4)
_SPATIAL_R = _signature("khronon_spatial_curvature", _GAMMA, _T4)

# This table is authored independently from build_component_expressions.  It
# prevents a same-output-type component swap from masquerading as a successful
# literal binding merely because both expressions are natural top forms.
EXPECTED_SEMANTIC_SIGNATURES: Mapping[str, tuple[Any, ...]] = {
    "EH": _signature(
        "multiply_bulk_scalar_density",
        _signature("scalar_curvature", _G5),
        _VOL5,
    ),
    "Omega_kinetic": _signature(
        "multiply_bulk_scalar_density",
        _signature("contract_covectors5", _INV5, _D_OMEGA, _D_OMEGA),
        _VOL5,
    ),
    "Omega_potential": _signature(
        "multiply_bulk_scalar_density",
        _signature(
            "bulk_potential_from_W",
            _signature("superpotential_derivative", _O5),
            _signature("superpotential", _O5),
        ),
        _VOL5,
    ),
    "P_kinetic": _signature(
        "multiply_bulk_scalar_density",
        _signature("associated_one_form_norm", _INV5, _P, _P),
        _VOL5,
    ),
    "full_V4": _signature(
        "multiply_bulk_scalar_density",
        _signature(
            "weighted_full_V4",
            _O5,
            _signature("associated_scalar_norm", _PHI5),
        ),
        _VOL5,
    ),
    "BF": _signature(
        "invariant_B_wedge_F",
        _B5,
        _signature("connection_curvature", _A5),
    ),
    "GHY": _signature(
        "multiply_boundary_scalar_density",
        _signature("outward_mean_curvature", _G5),
        _VOL4,
    ),
    "wall": _signature(
        "multiply_boundary_scalar_density",
        _signature("wall_scalar", _signature("boundary_trace_scalar", _O5)),
        _VOL4,
    ),
    "K_foliation": _signature(
        "multiply_boundary_scalar_density",
        _signature("khronon_K_quadratic", _GAMMA, _T4),
        _VOL4,
    ),
    "R": _signature(
        "multiply_boundary_scalar_density",
        _SPATIAL_R,
        _VOL4,
    ),
    "R_squared": _signature(
        "multiply_boundary_scalar_density",
        _signature("square_boundary_scalar", _SPATIAL_R),
        _VOL4,
    ),
    "a_squared": _signature(
        "multiply_boundary_scalar_density",
        _signature(
            "contract_covectors4",
            _signature("inverse_metric4", _GAMMA),
            _ACCELERATION,
            _ACCELERATION,
        ),
        _VOL4,
    ),
    "Robin": _signature(
        "multiply_boundary_scalar_density",
        _signature("Robin_groupoid_quadratic", _SOLDER, _ACCELERATION, _GAMMA),
        _VOL4,
    ),
}


def _component_family(name: str) -> str:
    for side in SIDES:
        bulk_suffix = f"_bulk_{side}"
        if name.endswith(bulk_suffix):
            return name[: -len(bulk_suffix)]
        if name == f"GHY_{side}":
            return "GHY"
    if name in INTERFACE_SECTORS:
        return name
    raise NaturalityCertificateError(f"unknown component family: {name}")


@dataclass(frozen=True)
class ComponentBinding:
    name: str
    source_keys: tuple[str, ...]
    required_fragments: tuple[tuple[str, str], ...]


def literal_component_bindings() -> tuple[ComponentBinding, ...]:
    rows: list[ComponentBinding] = []
    for side in SIDES:
        rows.extend(
            (
                ComponentBinding(
                    f"EH_bulk_{side}",
                    ("bulk_gauged",),
                    (("bulk_gauged", "M5^3*R_eps/2"),),
                ),
                ComponentBinding(
                    f"Omega_kinetic_bulk_{side}",
                    ("bulk_gauged",),
                    (("bulk_gauged", "G*(nabla Omega_eps)^2/2"),),
                ),
                ComponentBinding(
                    f"Omega_potential_bulk_{side}",
                    ("bulk_gauged", "bulk_potential", "superpotential"),
                    (
                        ("bulk_gauged", "-U(Omega_eps)"),
                        ("bulk_potential", "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)"),
                        ("superpotential", "W(Omega)=3*M5^3*k_infinity"),
                    ),
                ),
                ComponentBinding(
                    f"P_kinetic_bulk_{side}",
                    ("bulk_gauged", "gauged_conformal_derivative"),
                    (
                        ("bulk_gauged", "Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2"),
                        ("gauged_conformal_derivative", "P_eps_M=D_(A_eps,M)phi_eps"),
                    ),
                ),
                ComponentBinding(
                    f"full_V4_bulk_{side}",
                    ("bulk_gauged", "full_V4"),
                    (
                        ("bulk_gauged", "Z5*M^2*Omega_eps^(-5)*V4"),
                        ("full_V4", "V4(r)=r^4/(2*sqrt(1+r^4))"),
                    ),
                ),
                ComponentBinding(
                    f"BF_bulk_{side}",
                    ("BF",),
                    (("BF", "<B_eps wedge F[A_eps]>"),),
                ),
                ComponentBinding(
                    f"GHY_{side}",
                    ("GHY",),
                    (("GHY", "Theta_eps for outward normals"),),
                ),
            )
        )
    rows.extend(
        (
            ComponentBinding(
                "wall",
                ("wall_background", "superpotential"),
                (
                    ("wall_background", "2*W(Omega_Sigma)+beta*(Omega_Sigma-1)^2/2"),
                    ("superpotential", "W(Omega)=3*M5^3*k_infinity"),
                ),
            ),
            ComponentBinding(
                "K_foliation",
                ("foliation_lower",),
                (
                    ("foliation_lower", "Kcal_mu_nu*Kcal^mu_nu"),
                    ("foliation_lower", "lambda_K*Kcal^2"),
                ),
            ),
            ComponentBinding(
                "R",
                ("foliation_lower",),
                (("foliation_lower", "+xi*Rcal"),),
            ),
            ComponentBinding(
                "R_squared",
                ("foliation_lower",),
                (("foliation_lower", "-B4_bar*Rcal^2/(16*k_infinity^2)"),),
            ),
            ComponentBinding(
                "a_squared",
                ("foliation_lower",),
                (("foliation_lower", "+eta*a_mu*a^mu"),),
            ),
            ComponentBinding(
                "Robin",
                ("Robin_intrinsic",),
                (
                    ("Robin_intrinsic", "h_mu_nu*(varphi_H^mu-y*a^mu)"),
                    ("Robin_intrinsic", "(varphi_H^nu-y*a^nu)"),
                ),
            ),
        )
    )
    return tuple(rows)


EXPECTED_EXACT_ACTION_KEYS = frozenset(
    {
        "BF",
        "GHY",
        "Robin_intrinsic",
        "bulk_gauged",
        "bulk_potential",
        "foliation_lower",
        "full_V4",
        "gauged_conformal_derivative",
        "removed_terms",
        "superpotential",
        "total",
        "wall_background",
    }
)
EXPECTED_TOTAL_ACTION = (
    "S_v5_2=S_bulk_gauged+S_GHY+S_wall0+S_fol_lower+S_R_intrinsic+S_BF"
)
EXPECTED_REMOVED_TERMS = "S_X=0 and every bulk screen-clock term=0"
EXPECTED_INTERFACE_CONFIGURATION = (
    "Y_plus^*g_plus=Y_minus^*g_minus=gamma",
    "Y_plus^*Omega_plus=Y_minus^*Omega_minus=Omega_Sigma",
    "j_plus(Y_plus^*phi_plus)=j_minus(Y_minus^*phi_minus)=varphi_H",
    "Trans_iota_plus(Y_plus^*A_plus)=Trans_iota_minus(Y_minus^*A_minus)=A_Sigma",
)
EXPECTED_BF_INCIDENCE = "sum_eps s_eps*b_eps=0 with s_plus=1 and s_minus=-1"


def _validate_literal_inventory(
    exact_action: Mapping[str, Any],
    bindings: Sequence[ComponentBinding],
    expressions: Mapping[str, Expression],
) -> dict[str, Any]:
    if frozenset(exact_action) != EXPECTED_EXACT_ACTION_KEYS:
        raise NaturalityCertificateError("literal v5.2 exact_action key drift")
    if exact_action.get("total") != EXPECTED_TOTAL_ACTION:
        raise NaturalityCertificateError("literal v5.2 total action drift")
    if exact_action.get("removed_terms") != EXPECTED_REMOVED_TERMS:
        raise NaturalityCertificateError("literal removed-term declaration drift")
    names = tuple(binding.name for binding in bindings)
    if names != COMPONENT_NAMES or len(set(names)) != len(names):
        raise NaturalityCertificateError("literal component inventory missing, duplicated, or reordered")
    if tuple(expressions) != COMPONENT_NAMES:
        raise NaturalityCertificateError("typed component inventory mismatch")

    expected_types = {
        name: FORM5 if "_bulk_" in name else FORM4 for name in COMPONENT_NAMES
    }
    consumed_keys = {"total", "removed_terms"}
    rows: list[dict[str, Any]] = []
    for binding in bindings:
        expression = expressions[binding.name]
        if expression.type_tag != expected_types[binding.name]:
            raise NaturalityCertificateError(
                f"wrong top-form type for {binding.name}: {expression.type_tag!r}"
            )
        family = _component_family(binding.name)
        semantic_signature = _expression_signature(expression)
        expected_signature = EXPECTED_SEMANTIC_SIGNATURES[family]
        if semantic_signature != expected_signature:
            raise NaturalityCertificateError(
                f"semantic operator signature drift for {binding.name}"
            )
        for key in binding.source_keys:
            if key not in exact_action:
                raise NaturalityCertificateError(
                    f"unknown literal source key for {binding.name}: {key}"
                )
            consumed_keys.add(key)
        for key, fragment in binding.required_fragments:
            if fragment not in exact_action[key]:
                raise NaturalityCertificateError(
                    f"literal fragment missing for {binding.name}: {key}:{fragment}"
                )
        rows.append(
            {
                "component": binding.name,
                "source_keys": list(binding.source_keys),
                "required_fragments": [list(row) for row in binding.required_fragments],
                "root_type": asdict(expression.type_tag),
                "typed_expression": _render_expression(expression),
                "semantic_operator_signature": semantic_signature,
                "naturality_axioms_used": sorted(_axioms_used(expression)),
            }
        )
    if consumed_keys != set(exact_action):
        raise NaturalityCertificateError(
            f"literal action keys not completely consumed: {set(exact_action) - consumed_keys}"
        )
    return {
        "component_count": len(rows),
        "component_order": list(names),
        "all_exact_action_keys_consumed": True,
        "coherent_coefficients_and_signs_bound_by_byte_pin_not_by_naturality": True,
        "rows": rows,
        "pass": True,
    }


def _load_pinned_contracts() -> tuple[dict[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    paths = {
        "v5_2_source": V52_SOURCE,
        "v5_2_artifact": V52_ARTIFACT,
        "v5_2_test": V52_TEST,
        "v5_6_1_source": V561_SOURCE,
        "v5_6_1_artifact": V561_ARTIFACT,
        "v5_6_1_test": V561_TEST,
    }
    observed: dict[str, Any] = {}
    for name, path in paths.items():
        digest = _sha256(path)
        expected = EXPECTED_SHA256[name]
        if digest != expected:
            raise NaturalityCertificateError(
                f"byte pin drift for {name}: {digest} != {expected}"
            )
        observed[name] = {"path": path.name, "sha256": digest}

    v52 = _load_json_pin(V52_ARTIFACT, EXPECTED_SHA256["v5_2_artifact"])
    v561 = _load_json_pin(V561_ARTIFACT, EXPECTED_SHA256["v5_6_1_artifact"])
    if v52.get("schema") != V52_SCHEMA:
        raise NaturalityCertificateError("v5.2 schema drift")
    if v561.get("schema") != V561_SCHEMA:
        raise NaturalityCertificateError("v5.6.1 schema drift")
    exact_action = v52.get("exact_classical_charter", {}).get("exact_action")
    if not isinstance(exact_action, dict):
        raise NaturalityCertificateError("v5.2 exact action missing")
    action_digest = _canonical_sha256(exact_action)
    if action_digest != V52_EXACT_ACTION_SHA256:
        raise NaturalityCertificateError("v5.2 canonical exact_action hash drift")
    interface_configuration = tuple(
        v52.get("exact_classical_charter", {})
        .get("interface_domain", {})
        .get("configuration", ())
    )
    if interface_configuration != EXPECTED_INTERFACE_CONFIGURATION:
        raise NaturalityCertificateError("v5.2 interface matching contract drift")
    bf_incidence = (
        v52.get("exact_classical_charter", {})
        .get("interface_domain", {})
        .get("natural_B_flux_equation")
    )
    if bf_incidence != EXPECTED_BF_INCIDENCE:
        raise NaturalityCertificateError("v5.2 BF incidence contract drift")

    v561_decision = v561.get("decision", {})
    if v561_decision.get("full_bulk_diffeomorphism_Ward_pass") is not False:
        raise NaturalityCertificateError("v5.6.1 historical full-bulk quarantine drift")
    obligation = v561.get("open_obligations_before_C1_N1_gate", {}).get("full_bulk", "")
    required_phrases = (
        "complete 5D metric, scalar, BF and matter bulk diffeomorphism variation",
        "interface identity",
    )
    if not all(phrase in obligation for phrase in required_phrases):
        raise NaturalityCertificateError("v5.6.1 full-bulk obligation text drift")

    observed["v5_2_artifact"]["schema"] = V52_SCHEMA
    observed["v5_2_artifact"]["canonical_exact_action_sha256"] = action_digest
    observed["v5_2_artifact"]["interface_configuration"] = list(
        interface_configuration
    )
    observed["v5_2_artifact"]["pinned_BF_incidence_not_yet_consumed"] = (
        bf_incidence
    )
    observed["v5_6_1_artifact"]["schema"] = V561_SCHEMA
    observed["v5_6_1_historical_target_false"] = True
    observed["v5_6_1_literal_open_obligation"] = obligation
    return observed, v52, v561


def _complete_domain_ledger() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for side in SIDES:
        complete_map, diffeomorphism, inverse = _side_maps(side)
        transformed_complete_map = compose(inverse, complete_map)
        expanded = pullback_word(transformed_complete_map) + pullback_word(diffeomorphism)
        reduced, steps = reduce_free_word(expanded)
        baseline = pullback_word(complete_map)
        rows.append(
            {
                "side": side,
                "map_types": {
                    "F": f"{complete_map.source.name}->{complete_map.target.name}",
                    "Phi": f"{diffeomorphism.source.name}->{diffeomorphism.target.name}",
                    "F_prime": (
                        f"{_map_source(transformed_complete_map).name}->"
                        f"{_map_target(transformed_complete_map).name}"
                    ),
                },
                "identity": "(Phi^-1 o F)^*(Phi^* X)=F^* X",
                "expanded_pullback_word": list(expanded),
                "reduced_pullback_word": list(reduced),
                "baseline_pullback_word": list(baseline),
                "reduction_steps": list(steps),
                "exact_match": reduced == baseline,
            }
        )
    return {
        "complete_maps_are_auxiliary_domain_identifications_not_new_dynamical_fields": True,
        "boundary_compatibility": "F_e o j_e=Y_e on one fixed abstract Sigma",
        "rows": rows,
        "pass": all(row["exact_match"] for row in rows),
    }


def _finite_naturality_ledger() -> dict[str, Any]:
    baseline = build_component_expressions("baseline")
    transformed = build_component_expressions("finite")
    rows: list[dict[str, Any]] = []
    for name in COMPONENT_NAMES:
        baseline_normalized, baseline_trace = normalize_expression(baseline[name])
        transformed_normalized, transformed_trace = normalize_expression(transformed[name])
        rows.append(
            {
                "component": name,
                "transformed_expression": _render_expression(transformed[name]),
                "normalized_transformed_expression": _render_expression(
                    transformed_normalized
                ),
                "baseline_expression": _render_expression(baseline_normalized),
                "exact_match": transformed_normalized == baseline_normalized,
                "transformed_reduction_trace": list(transformed_trace),
                "baseline_reduction_trace": list(baseline_trace),
                "naturality_axioms_used": sorted(_axioms_used(transformed[name])),
            }
        )
    return {
        "identity": "S_v5.2[Phi^*X,Phi^-1 o F,transported iota,T]=S_v5.2[X,F,iota,T]",
        "term_count": len(rows),
        "rows": rows,
        "no_absolute_noncompact_action_value_asserted": True,
        "local_version": (
            "compactly supported diffeomorphism, or an exhaustion boundary outside its support"
        ),
        "pass": len(rows) == len(COMPONENT_NAMES)
        and all(row["exact_match"] for row in rows),
    }


def _interface_raw_pullback_ledger() -> dict[str, Any]:
    field_types = {
        "g": METRIC5,
        "Omega": SCALAR5,
        "phi": ASSOCIATED0_5,
        "A": CONNECTION1_5,
    }
    rows: list[dict[str, Any]] = []
    for statement, (name, type_tag) in zip(
        EXPECTED_INTERFACE_CONFIGURATION, field_types.items()
    ):
        side_rows: list[dict[str, Any]] = []
        for side in SIDES:
            baseline, _ = normalize_expression(
                _bulk_field(side, name, type_tag, "baseline")
            )
            transformed, trace = normalize_expression(
                _bulk_field(side, name, type_tag, "finite")
            )
            side_rows.append(
                {
                    "side": side,
                    "transformed_trace": list(trace),
                    "transformed_reduces_to_baseline": transformed == baseline,
                }
            )
        rows.append(
            {
                "field": name,
                "pinned_matching_premise": statement,
                "transported_groupoid_data_required": name in {"phi", "A"},
                "affine_connection_trace_transport_status": (
                    "open" if name == "A" else "not_applicable"
                ),
                "sides": side_rows,
                "raw_side_pullback_words_reduce_exactly": all(
                    row["transformed_reduces_to_baseline"] for row in side_rows
                ),
            }
        )
    return {
        "rows": rows,
        "logical_form": (
            "raw tensor/form pullbacks preserve a baseline equality; the affine "
            "connection trace lift is a separate open obligation"
        ),
        "scope": "raw spacetime pullback words only",
        "full_v5_2_groupoid_configuration_domain_transport_proved": False,
        "pass": all(
            row["raw_side_pullback_words_reduce_exactly"] for row in rows
        ),
    }


def _soldered_matter_nodes(value: Expression) -> tuple[SolderedMatter, ...]:
    if isinstance(value, SolderedMatter):
        return (value,)
    if isinstance(value, PulledField):
        return ()
    return tuple(
        node
        for argument in value.arguments
        for node in _soldered_matter_nodes(argument)
    )


def _unique_soldered_matter(value: Expression) -> SolderedMatter:
    nodes = _soldered_matter_nodes(value)
    if len(nodes) != 1:
        raise NaturalityCertificateError(
            f"expected one soldered-matter node, observed {len(nodes)}"
        )
    return nodes[0]


def _groupoid_ledger(groupoid_mode: str = "finite") -> dict[str, Any]:
    expected_baseline = ("E", "R", "phi")
    expected_transformed = (
        "E",
        "gQ^-1",
        "gQ",
        "R",
        "gP^-1",
        "gP",
        "phi",
    )
    baseline_node = _unique_soldered_matter(
        build_component_expressions("baseline")["Robin"]
    )
    transformed_node = _unique_soldered_matter(
        build_component_expressions(
            "finite", groupoid_mode=groupoid_mode
        )["Robin"]
    )
    baseline = baseline_node.groupoid_factors
    transformed = transformed_node.groupoid_factors
    reduced, steps = reduce_free_word(transformed)
    expected_baseline_pullback = _bulk_field(
        "plus", "phi", ASSOCIATED0_5, "baseline"
    ).pullback_factors
    expected_transformed_pullback = _bulk_field(
        "plus", "phi", ASSOCIATED0_5, "finite"
    ).pullback_factors
    source_node_binding_exact = (
        baseline_node.name == "varphi_H"
        and transformed_node.name == "varphi_H"
        and baseline_node.type_tag == VECTOR4
        and transformed_node.type_tag == VECTOR4
        and baseline_node.pullback_factors == expected_baseline_pullback
        and transformed_node.pullback_factors == expected_transformed_pullback
        and baseline == expected_baseline
        and transformed == expected_transformed
    )
    return {
        "scope": "associated matter solder E R phi only",
        "affine_connection_trace_transport_claimed": False,
        "source_component": "Robin",
        "source_node_kind": "SolderedMatter",
        "source_node_binding_exact": source_node_binding_exact,
        "finite_rules": {
            "phi_prime": "gP phi",
            "R_prime": "gQ R gP^-1",
            "E_prime": "E gQ^-1",
        },
        "expected_transformed_word": list(expected_transformed),
        "transformed_word": list(transformed),
        "reduction_steps": list(steps),
        "reduced_word": list(reduced),
        "expected_baseline_word": list(expected_baseline),
        "baseline_word": list(baseline),
        "identity": "E' R' phi'=E gQ^-1 gQ R gP^-1 gP phi=E R phi",
        "pass": source_node_binding_exact and reduced == expected_baseline,
    }


@dataclass(frozen=True)
class LinearCombination:
    """An exact integer linear combination for Cartan sign bookkeeping."""

    terms: tuple[tuple[str, int], ...]

    @classmethod
    def from_mapping(cls, values: Mapping[str, int]) -> LinearCombination:
        return cls(tuple(sorted((name, coefficient) for name, coefficient in values.items() if coefficient)))

    def add(self, other: LinearCombination) -> LinearCombination:
        values = dict(self.terms)
        for name, coefficient in other.terms:
            values[name] = values.get(name, 0) + coefficient
        return LinearCombination.from_mapping(values)

    def scale(self, coefficient: int) -> LinearCombination:
        return LinearCombination.from_mapping(
            {name: coefficient * value for name, value in self.terms}
        )

    def substitute(
        self,
        replacements: Mapping[str, LinearCombination],
    ) -> LinearCombination:
        result = LinearCombination(())
        for name, coefficient in self.terms:
            replacement = replacements.get(
                name, LinearCombination.from_mapping({name: 1})
            )
            result = result.add(replacement.scale(coefficient))
        return result

    @property
    def is_zero(self) -> bool:
        return not self.terms


def _linear(**terms: int) -> LinearCombination:
    return LinearCombination.from_mapping(terms)


def _cartan_ledger(mutant: str | None = None) -> dict[str, Any]:
    replacements = {
        "Lie_A": _linear(i_F=1, D_iA=1),
        "Lie_phi": _linear(i_Dphi=1, bracket_iA_phi=-1),
        "Lie_B": _linear(i_DB=1, D_iB=1, bracket_iA_B=-1),
    }
    connection = _linear(Lie_A=1, D_iA=-1, i_F=-1)
    matter = _linear(Lie_phi=1, bracket_iA_phi=1, i_Dphi=-1)
    b_form = _linear(Lie_B=1, bracket_iA_B=1, i_DB=-1, D_iB=-1)
    if mutant == "connection_sign":
        connection = _linear(Lie_A=1, D_iA=1, i_F=-1)
    elif mutant == "matter_sign":
        matter = _linear(Lie_phi=1, bracket_iA_phi=-1, i_Dphi=-1)
    elif mutant == "omit_D_iB":
        b_form = _linear(Lie_B=1, bracket_iA_B=1, i_DB=-1)
    elif mutant is not None:
        raise NaturalityCertificateError(f"unknown Cartan mutant: {mutant}")
    rows = {
        "connection": connection.substitute(replacements),
        "associated_scalar": matter.substitute(replacements),
        "adjoint_three_form": b_form.substitute(replacements),
    }
    formulas = {
        "connection": "L_zeta A-D_A(i_zeta A)=i_zeta F",
        "associated_scalar": "L_zeta phi+(i_zeta A)xphi=i_zeta D_A phi",
        "adjoint_three_form": (
            "L_zeta B+(i_zeta A)xB=i_zeta D_A B+D_A(i_zeta B)"
        ),
    }
    return {
        "repository_gauge_convention": "delta_lambda A=-D_A lambda",
        "formulas": formulas,
        "residuals": {name: list(value.terms) for name, value in rows.items()},
        "pass": all(value.is_zero for value in rows.values()),
    }


FORMAL_LOCAL_PREREQUISITES = frozenset(
    {
        "byte_pins_and_canonical_v5_2_action",
        "literal_twenty_component_inventory",
        "complete_domain_pullback",
        "two_side_raw_spacetime_pullback_words_reduce_exactly",
        "twenty_component_finite_naturality",
        "finite_associated_matter_solder_covariance",
    }
)
FORMAL_LOCAL_REQUIRED_AXIOMS = frozenset(
    {
        "flow_pullback_derivative_is_Lie_derivative",
        "inverse_flow_embedding_derivative_has_negative_sign",
        "chain_rule_for_smooth_local_functionals",
        "compact_support_removes_the_exhaustion_boundary_flux",
    }
)


def _consumed_kernel_axioms(
    expressions: Mapping[str, Expression],
) -> frozenset[str]:
    consumed = set(FORMAL_LOCAL_REQUIRED_AXIOMS)
    for name in COMPONENT_NAMES:
        consumed.update(_axioms_used(expressions[name]))
    return frozenset(consumed)


def _flow_factor_coefficient(factor: str, side: str) -> int:
    if factor == f"Phi_{side}":
        return 1
    if factor == f"Phi_{side}^-1":
        return -1
    if factor == f"F_{side}":
        return 0
    raise NaturalityCertificateError(f"unexpected flow word factor: {factor}")


def _flow_generator_ledger(mode: str = "finite") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for side in SIDES:
        complete_word, field_word = _transformation_words(side, mode)
        complete_map_coefficient = sum(
            _flow_factor_coefficient(factor, side) for factor in complete_word
        )
        field_coefficient = sum(
            _flow_factor_coefficient(factor, side) for factor in field_word
        )
        total = complete_map_coefficient + field_coefficient
        rows.append(
            {
                "side": side,
                "complete_map_pullback_word": list(complete_word),
                "physical_field_pullback_word": list(field_word),
                "complete_map_generator_coefficient": complete_map_coefficient,
                "physical_field_Lie_generator_coefficient": field_coefficient,
                "pulled_field_total_generator_coefficient": total,
                "derived_field_variation": (
                    f"{field_coefficient:+d} L_zeta X_{side}"
                ),
                "derived_embedding_variation": (
                    f"{complete_map_coefficient:+d} zeta_{side} o Y_{side}"
                ),
                "exact_cancellation": total == 0,
            }
        )
    return {
        "mode": mode,
        "inverse_flow_derivative_rule": "d(Phi_t^-1)/dt at zero = -zeta",
        "rows": rows,
        "pass": all(
            row["complete_map_generator_coefficient"] == -1
            and row["physical_field_Lie_generator_coefficient"] == 1
            and row["exact_cancellation"]
            for row in rows
        ),
    }


def _formal_local_chain_rule_ledger(
    prerequisites: Mapping[str, bool],
    *,
    flow_mode: str = "finite",
    available_axioms: Sequence[str] = KERNEL_AXIOMS,
    consumed_axioms: Sequence[str] | None = None,
) -> dict[str, Any]:
    flow = _flow_generator_ledger(flow_mode)
    cartan = _cartan_ledger()
    prerequisite_names_match = frozenset(prerequisites) == FORMAL_LOCAL_PREREQUISITES
    available_axiom_set = frozenset(available_axioms)
    consumed_axiom_set = (
        _consumed_kernel_axioms(build_component_expressions("finite"))
        if consumed_axioms is None
        else frozenset(consumed_axioms)
    )
    missing_axioms = FORMAL_LOCAL_REQUIRED_AXIOMS - available_axiom_set
    unexpected_axioms = available_axiom_set - EXPECTED_KERNEL_AXIOMS
    kernel_axiom_set_matches = available_axiom_set == EXPECTED_KERNEL_AXIOMS
    unused_allowed_axioms = EXPECTED_KERNEL_AXIOMS - consumed_axiom_set
    consumed_unexpected_axioms = consumed_axiom_set - EXPECTED_KERNEL_AXIOMS
    kernel_axioms_consumed_exactly = consumed_axiom_set == EXPECTED_KERNEL_AXIOMS
    return {
        "finite_family": "Phi_e(t)=exp(t zeta_e), Phi_e(0)=Id",
        "prerequisites": dict(prerequisites),
        "required_prerequisite_names": sorted(FORMAL_LOCAL_PREREQUISITES),
        "prerequisite_names_match": prerequisite_names_match,
        "required_chain_rule_axioms": sorted(FORMAL_LOCAL_REQUIRED_AXIOMS),
        "missing_required_chain_rule_axioms": sorted(missing_axioms),
        "unexpected_kernel_axioms": sorted(unexpected_axioms),
        "exact_allowed_kernel_axiom_set_match": kernel_axiom_set_matches,
        "consumed_kernel_axioms": sorted(consumed_axiom_set),
        "unused_allowed_kernel_axioms": sorted(unused_allowed_axioms),
        "consumed_unexpected_kernel_axioms": sorted(
            consumed_unexpected_axioms
        ),
        "every_allowed_kernel_axiom_consumed_exactly": (
            kernel_axioms_consumed_exactly
        ),
        "flow_generators_derived_from_finite_map_words": flow,
        "formal_chain_rule_identity": (
            "D_local S_v5.2[X,Y,iota,T](L_zeta X,-zeta o Y,delta_zeta iota,0)=0"
        ),
        "abstract_khronon_variation": "delta T=0",
        "Cartan_bulk_sign_ledger": cartan,
        "local_Green_or_stratified_Ward_identity_claimed": False,
        "Euler_equations_imposed": False,
        "pass": prerequisite_names_match
        and all(prerequisites.values())
        and not missing_axioms
        and kernel_axiom_set_matches
        and kernel_axioms_consumed_exactly
        and flow["pass"]
        and cartan["pass"],
    }


def _expressions_match(
    candidate: Mapping[str, Expression],
    baseline: Mapping[str, Expression],
) -> tuple[bool, tuple[str, ...]]:
    mismatches: list[str] = []
    for name in COMPONENT_NAMES:
        normalized_candidate, _ = normalize_expression(candidate[name])
        normalized_baseline, _ = normalize_expression(baseline[name])
        if normalized_candidate != normalized_baseline:
            mismatches.append(name)
    return not mismatches, tuple(mismatches)


def _replace_semantic_leaf_role(
    value: Expression,
    target_role: str,
    replacement_role: str,
) -> Expression:
    if isinstance(value, PulledField):
        if _field_role(value.name) != target_role:
            return value
        side_suffix = next(
            (f"_{side}" for side in SIDES if value.name.endswith(f"_{side}")),
            "",
        )
        return PulledField(
            f"{replacement_role}{side_suffix}",
            value.type_tag,
            value.pullback_factors,
        )
    if isinstance(value, SolderedMatter):
        if value.name != target_role:
            return value
        return SolderedMatter(
            replacement_role,
            value.type_tag,
            value.pullback_factors,
            value.groupoid_factors,
        )
    return Construction(
        value.operator,
        tuple(
            _replace_semantic_leaf_role(argument, target_role, replacement_role)
            for argument in value.arguments
        ),
        value.type_tag,
    )


def _mutant_campaign(exact_action: Mapping[str, Any]) -> dict[str, Any]:
    baseline = build_component_expressions("baseline")
    rows: dict[str, Any] = {}
    for mode in (
        "frozen_complete_map",
        "wrong_inverse_complete_map",
        "omitted_field_pullback",
    ):
        matches, mismatches = _expressions_match(
            build_component_expressions(mode, groupoid_mode="baseline"), baseline
        )
        rows[mode] = {
            "killed": not matches,
            "mismatched_components": list(mismatches),
        }

    for groupoid_mode in ("frozen_frame", "missing_source_inverse"):
        matches, mismatches = _expressions_match(
            build_component_expressions("finite", groupoid_mode=groupoid_mode),
            baseline,
        )
        rows[groupoid_mode] = {
            "killed": not matches and "Robin" in mismatches,
            "mismatched_components": list(mismatches),
        }

    omitted_groupoid_transport = _groupoid_ledger("baseline")
    rows["finite_groupoid_transport_omitted"] = {
        "killed": not omitted_groupoid_transport["pass"],
        "observed_transformed_word": omitted_groupoid_transport[
            "transformed_word"
        ],
    }

    matches, mismatches = _expressions_match(
        build_component_expressions(
            "finite", transform_khronon_mutant=True
        ),
        baseline,
    )
    rows["transformed_abstract_khronon"] = {
        "killed": not matches and any(name in INTERFACE_SECTORS for name in mismatches),
        "mismatched_components": list(mismatches),
    }

    bindings = literal_component_bindings()
    for name, mutated in (
        ("omitted_literal_component", bindings[:-1]),
        ("duplicated_literal_component", bindings + (bindings[-1],)),
    ):
        try:
            _validate_literal_inventory(exact_action, mutated, baseline)
        except NaturalityCertificateError:
            killed = True
        else:
            killed = False
        rows[name] = {"killed": killed}

    try:
        construct(
            "invariant_B_wedge_F",
            PulledField("B_wrong_degree", ADJOINT2_5, ("F_plus",)),
            PulledField("F_A", ADJOINT2_5, ("F_plus",)),
        )
    except NaturalityCertificateError:
        bf_degree_killed = True
    else:
        bf_degree_killed = False
    rows["BF_wrong_form_degree"] = {"killed": bf_degree_killed}

    finite_components = build_component_expressions("finite")
    frozen_b_candidate = dict(finite_components)
    transformed_connection = _bulk_field(
        "plus", "A", CONNECTION1_5, "finite"
    )
    frozen_b_candidate["BF_bulk_plus"] = construct(
        "invariant_B_wedge_F",
        PulledField("B_plus", ADJOINT3_5, ()),
        construct("connection_curvature", transformed_connection),
    )
    matches, mismatches = _expressions_match(frozen_b_candidate, baseline)
    rows["BF_field_pullback_omitted"] = {
        "killed": not matches and "BF_bulk_plus" in mismatches,
        "mismatched_components": list(mismatches),
    }

    frozen_normal_candidate = dict(finite_components)
    for side in SIDES:
        transformed_metric = _bulk_field(side, "g", METRIC5, "finite")
        transformed_gamma = construct("induced_boundary_metric", transformed_metric)
        frozen_normal_candidate[f"GHY_{side}"] = construct(
            "multiply_boundary_scalar_density",
            PulledField(f"Theta_frozen_{side}", SCALAR4, ()),
            construct("boundary_volume", transformed_gamma),
        )
    matches, mismatches = _expressions_match(frozen_normal_candidate, baseline)
    rows["GHY_outward_normal_frozen"] = {
        "killed": not matches
        and all(f"GHY_{side}" in mismatches for side in SIDES),
        "mismatched_components": list(mismatches),
    }

    for left, right in (
        ("EH_bulk_plus", "Omega_kinetic_bulk_plus"),
        ("wall", "R_squared"),
        ("Robin", "K_foliation"),
    ):
        swapped = dict(baseline)
        swapped[left], swapped[right] = swapped[right], swapped[left]
        try:
            _validate_literal_inventory(exact_action, bindings, swapped)
        except NaturalityCertificateError:
            swap_killed = True
        else:
            swap_killed = False
        rows[f"semantic_operator_swap_{left}_with_{right}"] = {
            "killed": swap_killed
        }

    for component, target, replacement in (
        ("Omega_kinetic_bulk_plus", "Omega", "unrelated_scalar"),
        ("Robin", "varphi_H", "unrelated_vector"),
    ):
        renamed = dict(baseline)
        renamed[component] = _replace_semantic_leaf_role(
            renamed[component], target, replacement
        )
        try:
            _validate_literal_inventory(exact_action, bindings, renamed)
        except NaturalityCertificateError:
            rename_killed = True
        else:
            rename_killed = False
        rows[f"semantic_leaf_{target}_to_{replacement}"] = {
            "killed": rename_killed
        }

    wrong_sign = _formal_local_chain_rule_ledger(
        {name: True for name in FORMAL_LOCAL_PREREQUISITES},
        flow_mode="wrong_inverse_complete_map",
    )
    rows["same_sign_field_and_embedding"] = {"killed": not wrong_sign["pass"]}
    missing_chain_rule = _formal_local_chain_rule_ledger(
        {name: True for name in FORMAL_LOCAL_PREREQUISITES},
        available_axioms=tuple(
            axiom
            for axiom in KERNEL_AXIOMS
            if axiom != "chain_rule_for_smooth_local_functionals"
        ),
    )
    rows["missing_chain_rule_axiom"] = {
        "killed": not missing_chain_rule["pass"]
    }
    unconsumed_allowed_axiom = _formal_local_chain_rule_ledger(
        {name: True for name in FORMAL_LOCAL_PREREQUISITES},
        consumed_axioms=tuple(
            axiom
            for axiom in EXPECTED_KERNEL_AXIOMS
            if axiom != "curvature_is_natural"
        ),
    )
    rows["unconsumed_allowed_kernel_axiom"] = {
        "killed": not unconsumed_allowed_axiom["pass"]
    }
    unexpected_consumed_axiom = _formal_local_chain_rule_ledger(
        {name: True for name in FORMAL_LOCAL_PREREQUISITES},
        consumed_axioms=tuple(EXPECTED_KERNEL_AXIOMS) + ("magic_axiom",),
    )
    rows["unexpected_consumed_kernel_axiom"] = {
        "killed": not unexpected_consumed_axiom["pass"]
    }
    for mutant in ("connection_sign", "matter_sign", "omit_D_iB"):
        rows[f"Cartan_{mutant}"] = {"killed": not _cartan_ledger(mutant)["pass"]}

    killed = all(row["killed"] for row in rows.values())
    return {"rows": rows, "mutant_count": len(rows), "pass": killed}


def _fixed_background_exclusion() -> dict[str, Any]:
    complete_map, diffeomorphism, inverse = _side_maps("plus")
    transformed_complete_map = compose(inverse, complete_map)
    baseline = pullback_word(complete_map)
    pair_word = pullback_word(transformed_complete_map) + pullback_word(diffeomorphism)
    fixed_word = pullback_word(transformed_complete_map)
    reduced_pair, pair_steps = reduce_free_word(pair_word)
    reduced_fixed, fixed_steps = reduce_free_word(fixed_word)
    nonzero_assumptions = {
        "c": "nonzero",
        "f(0)": "nonzero",
        "Vol(Sigma)": "nonzero",
    }
    flux_factors = ("c", "f(0)", "Vol(Sigma)")
    flux_forced_nonzero = all(
        nonzero_assumptions.get(factor) == "nonzero" for factor in flux_factors
    )
    return {
        "transformed_pair": {
            "identity": "X_infinity' = Phi^* X_infinity",
            "expanded_word": list(pair_word),
            "reduced_word": list(reduced_pair),
            "baseline_word": list(baseline),
            "reduction_steps": list(pair_steps),
            "pair_covariance_exact": reduced_pair == baseline,
        },
        "frozen_external_background": {
            "expanded_word": list(fixed_word),
            "reduced_word": list(reduced_fixed),
            "baseline_word": list(baseline),
            "reduction_steps": list(fixed_steps),
            "full_gauge_identity": reduced_fixed == baseline,
        },
        "normal_interface_flux_counterexample": {
            "manifold": "[0,infinity) x Sigma",
            "background_top_form": "c d_rho wedge vol_Sigma",
            "compact_collar_generator": "zeta=f(rho) partial_rho with f(0) nonzero",
            "uncancelled_flux": "c f(0) Vol(Sigma)",
            "conditional_nonzero_assumptions": [
                "c != 0",
                "f(0) != 0",
                "Vol(Sigma) != 0",
            ],
            "nonzero_under_the_stated_assumptions": flux_forced_nonzero,
            "unconditional_nonzero_claimed": False,
        },
        "conclusion": (
            "covariance of the transformed pair does not establish gauge symmetry with the external background frozen"
        ),
    }


def build_report() -> dict[str, Any]:
    source_pins, v52, _v561 = _load_pinned_contracts()
    exact_action = v52["exact_classical_charter"]["exact_action"]
    baseline = build_component_expressions("baseline")
    inventory = _validate_literal_inventory(
        exact_action, literal_component_bindings(), baseline
    )
    complete_domains = _complete_domain_ledger()
    finite = _finite_naturality_ledger()
    interface_raw_pullback = _interface_raw_pullback_ledger()
    groupoid = _groupoid_ledger()
    pin_pass = (
        source_pins["v5_2_artifact"]["canonical_exact_action_sha256"]
        == V52_EXACT_ACTION_SHA256
        and source_pins["v5_6_1_historical_target_false"] is True
    )
    formal_local_prerequisites = {
        "byte_pins_and_canonical_v5_2_action": pin_pass,
        "literal_twenty_component_inventory": bool(inventory["pass"]),
        "complete_domain_pullback": bool(complete_domains["pass"]),
        "two_side_raw_spacetime_pullback_words_reduce_exactly": bool(
            interface_raw_pullback["pass"]
        ),
        "twenty_component_finite_naturality": bool(finite["pass"]),
        "finite_associated_matter_solder_covariance": bool(groupoid["pass"]),
    }
    formal_local = _formal_local_chain_rule_ledger(
        formal_local_prerequisites
    )
    mutants = _mutant_campaign(exact_action)
    fixed_background = _fixed_background_exclusion()
    kernel_axiom_set_matches = frozenset(KERNEL_AXIOMS) == EXPECTED_KERNEL_AXIOMS
    consumed_kernel_axioms = _consumed_kernel_axioms(
        build_component_expressions("finite")
    )
    kernel_axioms_consumed_exactly = (
        consumed_kernel_axioms == EXPECTED_KERNEL_AXIOMS
    )
    finite_geometric_covariance = (
        all(formal_local_prerequisites.values())
        and kernel_axiom_set_matches
        and kernel_axioms_consumed_exactly
        and mutants["pass"]
    )
    core = {
        "v5_2_geometric_action_and_v5_6_1_obligation_byte_pinned_pass": pin_pass,
        "finite_complete_domain_pullback_identity_exact_pass": bool(
            complete_domains["pass"]
            and finite["pass"]
            and interface_raw_pullback["pass"]
        ),
        "literal_v5_2_twenty_component_naturality_inventory_complete_pass": bool(
            inventory["pass"] and inventory["component_count"] == len(COMPONENT_NAMES)
        ),
        "finite_associated_matter_solder_groupoid_word_covariance_exact_pass": bool(
            groupoid["pass"]
        ),
        "finite_typed_geometric_S_v5_2_action_expression_covariance_exact_pass": (
            finite_geometric_covariance
        ),
        "formal_local_compact_support_chain_rule_corollary_DS_G_zero_exact_pass": bool(
            formal_local["pass"]
        ),
    }
    decision: dict[str, bool] = {
        **core,
        "finite_full_affine_connection_trace_transport_exact_pass": False,
        "oriented_BF_incidence_cancellation_exact_pass": False,
        "literal_bulk_interface_Green_ledger_pass": False,
        "differentiated_smooth_compact_support_bulk_Ward_identity_exact_pass": False,
        "full_bulk_diffeomorphism_Ward_pass": False,
        "fixed_reference_S_rel_diffeomorphism_Ward_pass": False,
        "complete_moving_embedding_Ward_pass": False,
        "complete_v5_2_all_field_normal_embedding_pass": False,
        "full_off_shell_Green_theorem_accepted": False,
        "global_noncompact_action_finite_pass": False,
        "continuum_all_configurations_theorem_pass": False,
        "full_classical_variational_principle_selected_sector_pass": False,
        "numerical_sample_constitutes_naturality_proof_pass": False,
        "C1_ACTION_pass": False,
        "N1_ACTION_pass": False,
        "P4_full_same_action_pass": False,
        "C1_N1_promotion_authorized": False,
        "B4_pass": False,
        "B5_pass": False,
    }
    true_keys = frozenset(key for key, value in decision.items() if value)
    false_keys = frozenset(key for key, value in decision.items() if not value)
    if true_keys != TRUE_DECISION_KEYS or false_keys != FALSE_DECISION_KEYS:
        raise NaturalityCertificateError("decision allowlist or quarantine drift")

    return {
        "schema": SCHEMA,
        "claim": (
            "Exact finite covariance of the typed geometric S_v5.2 action "
            "expression and its formal local compact-support chain-rule "
            "corollary only"
        ),
        "source_pins": source_pins,
        "theorem_domain": {
            "bulk_fields": [
                "Lorentzian g",
                "positive scalar Omega",
                "associated SO3 scalar phi",
                "SO3 connection A",
                "adjoint-valued real three-form B",
            ],
            "bulk_geometry": (
                "two smooth oriented and time-oriented five-dimensional halves"
            ),
            "diffeomorphisms": (
                "orientation- and time-orientation-preserving, connected to "
                "identity, compactly supported, with compatible base-map/raw "
                "pullback traces; affine connection trace transport remains open"
            ),
            "bundle_sector": "trivial SO3 bundles and null-homotopic extendible gauges",
            "abstract_interface_and_T_fixed_in_this_bulk_gauge_bookkeeping": True,
            "interface_matching": list(EXPECTED_INTERFACE_CONFIGURATION),
            "full_affine_connection_trace_transport_in_this_certificate": False,
            "functional_meaning": (
                "finite covariance and its unexpanded local compact-support "
                "chain-rule derivative; no local Green decomposition"
            ),
        },
        "proof_kernel": {
            "status": "exact relative to the enumerated differential-geometric axioms",
            "axioms": list(KERNEL_AXIOMS),
            "expected_allowed_axioms": sorted(EXPECTED_KERNEL_AXIOMS),
            "exact_allowed_axiom_set_match": kernel_axiom_set_matches,
            "consumed_axioms": sorted(consumed_kernel_axioms),
            "unused_allowed_axioms": sorted(
                EXPECTED_KERNEL_AXIOMS - consumed_kernel_axioms
            ),
            "consumed_unexpected_axioms": sorted(
                consumed_kernel_axioms - EXPECTED_KERNEL_AXIOMS
            ),
            "every_allowed_axiom_consumed_exactly": (
                kernel_axioms_consumed_exactly
            ),
            "operator_count": len(OPERATOR_SPECS),
            "operators": {
                name: {
                    "inputs": [asdict(value) for value in spec.inputs],
                    "output": asdict(spec.output),
                    "naturality_axiom": spec.naturality_axiom,
                }
                for name, spec in OPERATOR_SPECS.items()
            },
        },
        "literal_action_inventory": inventory,
        "complete_domain_pullback": complete_domains,
        "finite_naturality": finite,
        "two_side_raw_spacetime_pullback_words": interface_raw_pullback,
        "finite_associated_matter_solder_groupoid": groupoid,
        "formal_local_compact_support_chain_rule_corollary": formal_local,
        "effective_mutants": mutants,
        "excluded_fixed_background_relative_contract": fixed_background,
        "open_local_Ward_obligations": {
            "affine_connection_trace_transport": (
                "OPEN: prove Trans_iota(A)=r(Y^*A)r^-1-(d r)r^-1 under the finite transported bundle/frame data"
            ),
            "oriented_BF_incidence": (
                "OPEN: consume the literal two-side boundary Green form with s_plus=+1 and s_minus=-1"
            ),
            "literal_bulk_interface_Green_ledger": (
                "OPEN: type and normalize the bulk Euler pairings, d_5 current, "
                "embedding Euler term, constrained iota term and d_4 interface "
                "current"
            ),
            "Noether_current_definition": (
                "OPEN for the local ledger: J_e=theta_e(X_e,L_zeta X_e)-i_zeta L_e"
            ),
        },
        "explicit_exclusions": {
            "material_shape": (
                "delta Y=+xi with Eulerian delta fields=0 requires the separate "
                "literal boundary Green/shape derivation"
            ),
            "off_shell_Sobolev": (
                "no product spaces, norm estimates, density theorem, weighted "
                "tails, or noncompact flux limit are claimed"
            ),
            "relative_functional": (
                "simultaneous covariance of (X,X_infinity) is not frozen-background gauge invariance"
            ),
            "promotion": (
                "this does not close the v5.6.1 full-bulk Ward key; C1, N1, P4, B4 and B5 remain false"
            ),
        },
        "decision": decision,
        "evidence_boundary": (
            "This is an exact typed/free-word certificate relative to explicitly "
            "listed standard geometric axioms. It is neither a numerical check "
            "nor a proof-assistant derivation. The local compact-support DS "
            "statement is only the formal chain-rule derivative of the finite "
            "covariance ledger for the action expression; it is not a consumed "
            "local Green/interface Ward identity and does not promote the v5.6.1 "
            "full-bulk key."
        ),
    }


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
