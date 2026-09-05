#!/usr/bin/env python3
"""Exact proof ledger for geometric v5.2 finite bulk-diffeomorphism naturality.

This unit is deliberately independent of the numerical Route-C action units.
It byte-pins the literal geometric ``S_v5.2`` charter and the v5.6.1 open
obligation, binds every literal action term to a typed geometric expression,
and checks finite pullback naturality with a small free-word normalizer.  A
separate integer noncommutative word kernel proves the finite affine connection
trace transport on both sides.  A separate exact sign ledger binds the two real
BF routes to the oriented off-shell incidence ``b_plus-b_minus`` and factors the
common ``Delta A_Sigma`` without claiming cancellation before the natural
interface equation is imposed.  An exact symbolic Green ledger then consumes
the twenty literal action components in eighteen variation rows.  It derives
the scalar and material normal currents with a product-rule/integration-by-parts
normalizer, while recording EH+GHY and the six intrinsic interface variations
only as the explicitly named geometric axioms.  The unexpanded
local/compact-support chain-rule corollary is also recorded as the formal
derivative of the finite action identity on smooth selected-sector fields and
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
        "finite_full_affine_connection_trace_transport_exact_pass",
        "oriented_BF_incidence_aggregation_exact_pass",
        "literal_bulk_interface_Green_ledger_pass",
        "finite_typed_geometric_S_v5_2_action_expression_covariance_exact_pass",
        "formal_local_compact_support_chain_rule_corollary_DS_G_zero_exact_pass",
    }
)
FALSE_DECISION_KEYS = frozenset(
    {
        "oriented_BF_incidence_cancellation_exact_pass",
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
EXPECTED_CONNECTION_TRACE_DEFINITION = (
    "Trans_iota(A)=r*(Y^*A)*r^(-1)-(d r)*r^(-1)=A_Sigma"
)
EXPECTED_BF_INCIDENCE = "sum_eps s_eps*b_eps=0 with s_plus=1 and s_minus=-1"
EXPECTED_BF_ACTION_LITERAL = (
    "S_BF=sum_eps int_Meps <B_eps wedge F[A_eps]>, "
    "<X,Y>=-tr_3(XY)/2"
)
EXPECTED_ADJOINT_FORM_TRACE_DEFINITION = (
    "Trans_iota(B)=Ad_r(Y^*B)=b_eps"
)
EXPECTED_BF_GREEN_FORM = (
    "Theta_Sigma=-M5^3/2*sum_eps int sqrt(-gamma)*pi_eps^(mu nu)"
    "Delta gamma_mu_nu-int sqrt(-gamma)*[sum_eps Pi_Omega,eps Delta Omega+"
    "<sum_eps Pi_phi,eps,Delta varphi_H>]-int <sum_eps s_eps b_eps wedge "
    "Delta A_Sigma>+delta(S_wall0+S_fol+S_R)"
)
EXPECTED_BF_NATURAL_INTERFACE_EQUATION = "sum_eps s_eps*b_eps=0"
EXPECTED_COMMON_INTERFACE_VARIATIONS = (
    "Delta gamma, Delta Omega_Sigma, Delta varphi_H and Delta A_Sigma are common"
)
EXPECTED_EH_GHY_FIRST_VARIATION = (
    "delta(S_EH+S_GHY)=M5^3/2*int_M sqrt(-g)*G_MN*Delta g^(MN)-"
    "M5^3/2*int_Sigma sqrt(-gamma)*(Theta^(mu nu)-Theta*gamma^(mu nu))*"
    "Delta gamma_mu_nu; no normal derivative of Delta gamma remains"
)
EXPECTED_GREEN_MOMENTA = {
    "pi_eps": "Theta_eps^(mu nu)-Theta_eps*gamma^(mu nu)",
    "Pi_Omega_eps": "G*n_eps.nabla Omega+3*Z*<phi,n_eps.P>/(2*Omega)",
    "Pi_phi_eps": "Z*j_eps(n_eps.P_eps)",
}
EXPECTED_BF_BULK_EQUATION_A = (
    "D_A B+J_4=0 with J_4 proportional to Z*star(phi^[a P^(b])"
)
# This is an immutable, independently authored target.  Candidate rows are
# derived below from the real AST classifications; this table never builds them.
EXPECTED_GREEN_ROW_LAYOUT = (
    ("EH_GHY_plus", ("EH_bulk_plus", "GHY_plus")),
    ("Omega_kinetic_plus", ("Omega_kinetic_bulk_plus",)),
    ("Omega_potential_plus", ("Omega_potential_bulk_plus",)),
    ("P_kinetic_plus", ("P_kinetic_bulk_plus",)),
    ("full_V4_plus", ("full_V4_bulk_plus",)),
    ("BF_plus", ("BF_bulk_plus",)),
    ("EH_GHY_minus", ("EH_bulk_minus", "GHY_minus")),
    ("Omega_kinetic_minus", ("Omega_kinetic_bulk_minus",)),
    ("Omega_potential_minus", ("Omega_potential_bulk_minus",)),
    ("P_kinetic_minus", ("P_kinetic_bulk_minus",)),
    ("full_V4_minus", ("full_V4_bulk_minus",)),
    ("BF_minus", ("BF_bulk_minus",)),
    ("wall", ("wall",)),
    ("K_foliation", ("K_foliation",)),
    ("R", ("R",)),
    ("R_squared", ("R_squared",)),
    ("a_squared", ("a_squared",)),
    ("Robin", ("Robin",)),
)
EXPECTED_GREEN_ROW_FAMILY_SIDE = {
    "EH_GHY_plus": ("EH_GHY", "plus"),
    "Omega_kinetic_plus": ("Omega_kinetic", "plus"),
    "Omega_potential_plus": ("Omega_potential", "plus"),
    "P_kinetic_plus": ("P_kinetic", "plus"),
    "full_V4_plus": ("full_V4", "plus"),
    "BF_plus": ("BF", "plus"),
    "EH_GHY_minus": ("EH_GHY", "minus"),
    "Omega_kinetic_minus": ("Omega_kinetic", "minus"),
    "Omega_potential_minus": ("Omega_potential", "minus"),
    "P_kinetic_minus": ("P_kinetic", "minus"),
    "full_V4_minus": ("full_V4", "minus"),
    "BF_minus": ("BF", "minus"),
    "wall": ("wall", "interface"),
    "K_foliation": ("K_foliation", "interface"),
    "R": ("R", "interface"),
    "R_squared": ("R_squared", "interface"),
    "a_squared": ("a_squared", "interface"),
    "Robin": ("Robin", "interface"),
}
EXPECTED_INTRINSIC_DELTAS = {
    "wall": "delta(S_wall0)",
    "K_foliation": "delta(S_K_foliation)",
    "R": "delta(S_R)",
    "R_squared": "delta(S_R_squared)",
    "a_squared": "delta(S_a_squared)",
    "Robin": "delta(S_R_intrinsic)",
}
# SHA256 of a canonical full AST fingerprint containing every operator, type,
# field name, pullback word and groupoid word.  These values were authored from
# the reviewed v5.2 expression contract and are not rebuilt by the candidate
# expression constructor.
EXPECTED_GREEN_EXPRESSION_FINGERPRINTS = {
    "EH_bulk_plus": "499c20e77a409a611aa9f34b7f0c9729f1def776e20026f7d4c26098c53e9cd4",
    "Omega_kinetic_bulk_plus": "540fa08579cada74abf15f9a0685227150da8872c961d3c2b2f5bafc2cfcd73b",
    "Omega_potential_bulk_plus": "9860dcbc4d5a57c19f8be7dcb2bb7ece66fea537f2d4a8112b8c808ccd3a01f4",
    "P_kinetic_bulk_plus": "36b910115334ca8335d23c571bb6db69b5e3b3d4893af7f60c01e8f3ab903b97",
    "full_V4_bulk_plus": "50b9f0630d81fa1eb0ab3955ba4342b8075624868220cee67b8ad57a605dce5c",
    "BF_bulk_plus": "5bdb2538a34efa1db97891b4ad9fea1317108a3c823b32f0dc4aff8b5f057a36",
    "GHY_plus": "eee3371dda469c6e0db1d67f63634c1ec39ac96d70ae365a4bcffa38be30fb98",
    "EH_bulk_minus": "ba9ab52c25ae3e1c100a8ace1c6d1a9c71b91a53a5f1b7bb53a27be9d710a729",
    "Omega_kinetic_bulk_minus": "719617262cc2c0ef81bf9882846cd73c4fde469ec6c19f1960ab99db155a2b8c",
    "Omega_potential_bulk_minus": "0c3ccce1b073f2b56de33873fb9ce2f42e4c60927bd3e73ff5e304cf7f96fdd7",
    "P_kinetic_bulk_minus": "21743642fc533d7f7e08ed90c470cb561f4ff7a729525cd2e7ac385c7058d9b0",
    "full_V4_bulk_minus": "88feb4ee3abd3109fcb5edb3de7cc549e98725496f8458c38645690502b55d60",
    "BF_bulk_minus": "7333a1254eadb5f55974b39fe0beb02e178e25655cc216c61daa8acbd168d95e",
    "GHY_minus": "fb52af4895795e5c6309b816375409a4e99828162201cb9e7a53506a177fcaa7",
    "wall": "e6fcdace94e5e6326431f287f4ffaa19a193dac897a7c4d386cad63f4e78563a",
    "K_foliation": "db8708d0e128e7fc2726e294a0e0c83118f2b0a7eb4f3f6619a5003c6065c873",
    "R": "6d857f4ac286fb537b4b9d96e4cea434bcf7388bae8affc4d9542c3040ee9dcb",
    "R_squared": "2a3cad8a39bb2ab85daba4aac10dd50c9ae34c109f4bdc80db31f6e1dbe53369",
    "a_squared": "6fe51cc6a5c2841f34d49a1f0e92343525c93b73fee90d70025f2871408751a1",
    "Robin": "1bbb2c77425994083097a705c563c48227a98ed6a849ade16c37bd9f4f561b29",
}
EXPECTED_DELTA_P_TERM_SIGNATURES = (
    (
        "covariant_Delta_phi",
        "covariant_derivative",
        ("Delta_phi",),
        "Delta_phi",
        True,
        (1, 1, ()),
        "phi_normal_current",
    ),
    (
        "conformal_Delta_phi_dOmega",
        "product",
        ("Delta_phi", "dOmega"),
        "Delta_phi",
        False,
        (3, 2, (("Omega", -1),)),
        None,
    ),
    (
        "conformal_phi_dDeltaOmega",
        "product",
        ("phi", "d_Delta_Omega"),
        "Delta_Omega",
        True,
        (3, 2, (("Omega", -1),)),
        "Omega_normal_current",
    ),
    (
        "conformal_log_variation",
        "product",
        ("phi", "dOmega", "Delta_Omega"),
        "Delta_Omega",
        False,
        (-3, 2, (("Omega", -2),)),
        None,
    ),
    (
        "connection_representation",
        "representation",
        ("Delta_A", "phi"),
        "Delta_A",
        False,
        (1, 1, ()),
        None,
    ),
)
EXPECTED_GREEN_LEAF_MULTISETS: Mapping[str, tuple[tuple[str, int], ...]] = {
    "EH": (("g", 2),),
    "GHY": (("g", 2),),
    "Omega_kinetic": (("Omega", 2), ("g", 2)),
    "Omega_potential": (("Omega", 2), ("g", 1)),
    "P_kinetic": (("A", 2), ("Omega", 2), ("g", 2), ("phi", 4)),
    "full_V4": (("Omega", 1), ("g", 1), ("phi", 1)),
    "BF": (("A", 1), ("B", 1)),
    "wall": (("Omega", 1), ("g", 1)),
    "K_foliation": (("T", 1), ("g", 2)),
    "R": (("T", 1), ("g", 2)),
    "R_squared": (("T", 1), ("g", 2)),
    "a_squared": (("T", 2), ("g", 4)),
    "Robin": (("T", 1), ("g", 3), ("varphi_H", 1)),
}
BF_ORIENTATION_SIGNS = {"plus": 1, "minus": -1}
BF_TRACE_BINDING_MUTATIONS = frozenset(
    {"exact", "detached_b_trace", "detached_affine_target"}
)


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
    connection_trace_definition = (
        v52.get("exact_classical_charter", {})
        .get("definitions", {})
        .get("connection_trace")
    )
    if connection_trace_definition != EXPECTED_CONNECTION_TRACE_DEFINITION:
        raise NaturalityCertificateError(
            "v5.2 affine connection trace definition drift"
        )
    adjoint_form_trace_definition = (
        v52.get("exact_classical_charter", {})
        .get("definitions", {})
        .get("adjoint_form_trace")
    )
    if adjoint_form_trace_definition != EXPECTED_ADJOINT_FORM_TRACE_DEFINITION:
        raise NaturalityCertificateError("v5.2 adjoint-form trace definition drift")
    bf_action_literal = exact_action.get("BF")
    if bf_action_literal != EXPECTED_BF_ACTION_LITERAL:
        raise NaturalityCertificateError("v5.2 BF action literal drift")
    bf_incidence = (
        v52.get("exact_classical_charter", {})
        .get("interface_domain", {})
        .get("natural_B_flux_equation")
    )
    if bf_incidence != EXPECTED_BF_INCIDENCE:
        raise NaturalityCertificateError("v5.2 BF incidence contract drift")
    interface_variations = tuple(
        v52.get("exact_classical_charter", {})
        .get("interface_domain", {})
        .get("variations", ())
    )
    if (
        not interface_variations
        or interface_variations[0] != EXPECTED_COMMON_INTERFACE_VARIATIONS
    ):
        raise NaturalityCertificateError("v5.2 common interface variation drift")
    green_certificate = v52.get("Green_form_certificate", {})
    bf_green_form = green_certificate.get("Green_form")
    if bf_green_form != EXPECTED_BF_GREEN_FORM:
        raise NaturalityCertificateError("v5.2 BF Green-form incidence drift")
    bf_natural_equation = (
        green_certificate.get("natural_interface_equations", {}).get("BF_flux")
    )
    if bf_natural_equation != EXPECTED_BF_NATURAL_INTERFACE_EQUATION:
        raise NaturalityCertificateError("v5.2 BF natural interface equation drift")
    bf_bulk_equation_a = green_certificate.get("bulk_equations_new_sector", {}).get(
        "A"
    )
    if bf_bulk_equation_a != EXPECTED_BF_BULK_EQUATION_A:
        raise NaturalityCertificateError("v5.2 BF bulk A equation drift")

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
    observed["v5_2_artifact"]["connection_trace_definition"] = (
        connection_trace_definition
    )
    observed["v5_2_artifact"]["adjoint_form_trace_definition"] = (
        adjoint_form_trace_definition
    )
    observed["v5_2_artifact"]["BF_action_literal"] = bf_action_literal
    observed["v5_2_artifact"]["pinned_BF_incidence_contract"] = bf_incidence
    observed["v5_2_artifact"]["common_interface_variations"] = list(
        interface_variations
    )
    observed["v5_2_artifact"]["BF_Green_form"] = bf_green_form
    observed["v5_2_artifact"]["BF_natural_interface_equation"] = (
        bf_natural_equation
    )
    observed["v5_2_artifact"]["BF_bulk_equation_A"] = bf_bulk_equation_a
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
                    "checked_by_separate_exact_affine_ledger"
                    if name == "A"
                    else "not_applicable"
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
            "connection trace lift is checked by a separate exact ledger"
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


AFFINE_GROUP_GENERATORS = frozenset(
    {
        "q",
        "q_plus",
        "q_minus",
        "p_plus",
        "p_minus",
        "r_plus",
        "r_minus",
    }
)
EXPECTED_AFFINE_KERNEL_RULES = frozenset(
    {
        "integer_noncommutative_linear_collection",
        "noncommutative_distributive_word_product",
        "full_Leibniz_rule_for_group_words",
        "group_inverse_derivative_rule",
        "adjacent_group_inverse_cancellation",
    }
)
AFFINE_SIDE_MUTATIONS = frozenset(
    {
        "exact",
        "missing_source_affine_term",
        "wrong_source_affine_sign",
        "missing_target_affine_term",
        "wrong_target_affine_sign",
        "wrong_inverse_derivative_sign",
        "wrong_inverse_derivative_order",
        "omit_p_Leibniz_term",
        "omit_r_Leibniz_term",
        "omit_q_Leibniz_term",
        "wrong_r_prime_inverse_order",
        "frozen_r_transport",
        "r_factor_omitted_from_transport",
        "source_inverse_omitted_from_r_transport",
    }
)


def _affine_group_base(atom: str) -> str | None:
    base = atom[:-3] if atom.endswith("^-1") else atom
    return base if base in AFFINE_GROUP_GENERATORS else None


def _inverse_affine_group_atom(atom: str) -> str:
    base = _affine_group_base(atom)
    if base is None:
        raise NaturalityCertificateError(f"not an affine group atom: {atom}")
    return base if atom.endswith("^-1") else f"{base}^-1"


def _inverse_affine_group_word(word: Sequence[str]) -> tuple[str, ...]:
    return tuple(_inverse_affine_group_atom(atom) for atom in reversed(word))


def _reduce_affine_word(
    word: Sequence[str],
) -> tuple[tuple[str, ...], tuple[dict[str, Any], ...]]:
    stack: list[str] = []
    steps: list[dict[str, Any]] = []
    for atom in word:
        if (
            stack
            and _affine_group_base(stack[-1]) is not None
            and _affine_group_base(atom) is not None
            and _inverse_affine_group_atom(stack[-1]) == atom
        ):
            cancelled = stack.pop()
            steps.append(
                {
                    "rule": "adjacent_group_inverse_cancellation",
                    "cancelled": [cancelled, atom],
                    "remaining_prefix": list(stack),
                }
            )
        else:
            stack.append(atom)
    return tuple(stack), tuple(steps)


@dataclass(frozen=True)
class NoncommutativePolynomial:
    """Canonical integer polynomial in noncommuting connection/group atoms."""

    terms: tuple[tuple[tuple[str, ...], int], ...]

    @classmethod
    def from_terms(
        cls,
        terms: Sequence[tuple[int, Sequence[str]]],
    ) -> NoncommutativePolynomial:
        collected: dict[tuple[str, ...], int] = {}
        for coefficient, word in terms:
            if not isinstance(coefficient, int):
                raise NaturalityCertificateError(
                    "affine polynomial coefficients must be exact integers"
                )
            reduced, _steps = _reduce_affine_word(word)
            collected[reduced] = collected.get(reduced, 0) + coefficient
        canonical = tuple(
            sorted(
                (word, coefficient)
                for word, coefficient in collected.items()
                if coefficient
            )
        )
        return cls(canonical)

    @classmethod
    def zero(cls) -> NoncommutativePolynomial:
        return cls(())

    @classmethod
    def word(cls, *atoms: str) -> NoncommutativePolynomial:
        return cls.from_terms(((1, atoms),))

    def add(
        self,
        other: NoncommutativePolynomial,
    ) -> NoncommutativePolynomial:
        return NoncommutativePolynomial.from_terms(
            tuple((coefficient, word) for word, coefficient in self.terms)
            + tuple((coefficient, word) for word, coefficient in other.terms)
        )

    def scale(self, coefficient: int) -> NoncommutativePolynomial:
        return NoncommutativePolynomial.from_terms(
            tuple(
                (coefficient * value, word)
                for word, value in self.terms
            )
        )

    def subtract(
        self,
        other: NoncommutativePolynomial,
    ) -> NoncommutativePolynomial:
        return self.add(other.scale(-1))

    def multiply(
        self,
        other: NoncommutativePolynomial,
    ) -> NoncommutativePolynomial:
        return NoncommutativePolynomial.from_terms(
            tuple(
                (left_coefficient * right_coefficient, left_word + right_word)
                for left_word, left_coefficient in self.terms
                for right_word, right_coefficient in other.terms
            )
        )

    def containing(self, atom: str) -> NoncommutativePolynomial:
        return NoncommutativePolynomial.from_terms(
            tuple(
                (coefficient, word)
                for word, coefficient in self.terms
                if atom in word
            )
        )


def _nc_terms(value: NoncommutativePolynomial) -> list[dict[str, Any]]:
    return [
        {"coefficient": coefficient, "word": list(word)}
        for word, coefficient in value.terms
    ]


def _differentiate_affine_group_atom(
    atom: str,
    *,
    inverse_rule: str,
    omitted_generators: frozenset[str],
) -> tuple[NoncommutativePolynomial, str]:
    base = _affine_group_base(atom)
    if base is None:
        raise NaturalityCertificateError(
            f"cannot differentiate non-group atom: {atom}"
        )
    if base in omitted_generators:
        return NoncommutativePolynomial.zero(), "omitted_mutant"
    differential = f"d_{base}"
    if not atom.endswith("^-1"):
        return NoncommutativePolynomial.word(differential), "direct_generator"
    inverse = f"{base}^-1"
    if inverse_rule == "exact":
        return (
            NoncommutativePolynomial.from_terms(
                ((-1, (inverse, differential, inverse)),)
            ),
            "d(g^-1)=-g^-1*(d g)*g^-1",
        )
    if inverse_rule == "wrong_sign":
        return (
            NoncommutativePolynomial.word(inverse, differential, inverse),
            "mutant_wrong_positive_sign",
        )
    if inverse_rule == "wrong_order":
        return (
            NoncommutativePolynomial.from_terms(
                ((-1, (differential, inverse, inverse)),)
            ),
            "mutant_wrong_factor_order",
        )
    raise NaturalityCertificateError(
        f"unknown inverse derivative rule: {inverse_rule}"
    )


def _differentiate_affine_group_word(
    word: Sequence[str],
    *,
    inverse_rule: str = "exact",
    omitted_generators: frozenset[str] = frozenset(),
) -> tuple[NoncommutativePolynomial, tuple[dict[str, Any], ...]]:
    total = NoncommutativePolynomial.zero()
    trace: list[dict[str, Any]] = []
    for index, atom in enumerate(word):
        atom_derivative, rule = _differentiate_affine_group_atom(
            atom,
            inverse_rule=inverse_rule,
            omitted_generators=omitted_generators,
        )
        contribution = (
            NoncommutativePolynomial.word(*word[:index])
            .multiply(atom_derivative)
            .multiply(NoncommutativePolynomial.word(*word[index + 1 :]))
        )
        total = total.add(contribution)
        trace.append(
            {
                "Leibniz_slot": index,
                "group_atom": atom,
                "atom_rule": rule,
                "atom_derivative_terms": _nc_terms(atom_derivative),
                "contribution_terms": _nc_terms(contribution),
            }
        )
    return total, tuple(trace)


def _conjugate_affine_polynomial(
    group_word: Sequence[str],
    value: NoncommutativePolynomial,
    *,
    inverse_word: Sequence[str] | None = None,
) -> NoncommutativePolynomial:
    inverse = (
        _inverse_affine_group_word(group_word)
        if inverse_word is None
        else tuple(inverse_word)
    )
    return (
        NoncommutativePolynomial.word(*group_word)
        .multiply(value)
        .multiply(NoncommutativePolynomial.word(*inverse))
    )


def _pulled_field_nodes(value: Expression) -> tuple[PulledField, ...]:
    if isinstance(value, PulledField):
        return (value,)
    if isinstance(value, SolderedMatter):
        return ()
    return tuple(
        node
        for argument in value.arguments
        for node in _pulled_field_nodes(argument)
    )


def _connection_trace_binding_rows(
    v52: Mapping[str, Any],
    interface_raw_pullback: Mapping[str, Any],
    components: Mapping[str, Expression],
    target_gauges: Mapping[str, str],
) -> tuple[dict[str, Any], ...]:
    charter = v52.get("exact_classical_charter", {})
    definition = charter.get("definitions", {}).get("connection_trace")
    configuration = tuple(
        charter.get("interface_domain", {}).get("configuration", ())
    )
    connection_statement = EXPECTED_INTERFACE_CONFIGURATION[3]
    raw_rows = [
        row
        for row in interface_raw_pullback.get("rows", ())
        if row.get("field") == "A"
    ]
    raw_row = raw_rows[0] if len(raw_rows) == 1 else {}
    rows: list[dict[str, Any]] = []
    for side in SIDES:
        expected_node = _bulk_field(
            side, "A", CONNECTION1_5, "finite"
        )
        component_names = (
            f"P_kinetic_bulk_{side}",
            f"BF_bulk_{side}",
        )
        expected_occurrence_counts = {
            f"P_kinetic_bulk_{side}": 2,
            f"BF_bulk_{side}": 1,
        }
        route_rows: list[dict[str, Any]] = []
        route_connection_nodes: list[PulledField] = []
        for component_name in component_names:
            connection_nodes = tuple(
                node
                for node in _pulled_field_nodes(components[component_name])
                if node.type_tag == CONNECTION1_5
            )
            structural_nodes = frozenset(connection_nodes)
            route_connection_nodes.extend(connection_nodes)
            route_rows.append(
                {
                    "component": component_name,
                    "raw_AST_connection_occurrence_count": len(connection_nodes),
                    "expected_raw_AST_connection_occurrence_count": (
                        expected_occurrence_counts[component_name]
                    ),
                    "distinct_structural_connection_node_count": len(
                        structural_nodes
                    ),
                    "connection_symbols": [node.name for node in connection_nodes],
                    "pullback_words": [
                        list(node.pullback_factors) for node in connection_nodes
                    ],
                    "all_occurrences_are_the_same_expected_A_e": bool(
                        connection_nodes
                        and all(node == expected_node for node in connection_nodes)
                    ),
                    "one_structural_A_e_symbol_type_pullback_on_this_route": (
                        len(structural_nodes) == 1
                    ),
                    "structural_multiplicity_is_exact": (
                        len(connection_nodes)
                        == expected_occurrence_counts[component_name]
                    ),
                }
            )
        raw_side_rows = [
            row for row in raw_row.get("sides", ()) if row.get("side") == side
        ]
        exact = (
            definition == EXPECTED_CONNECTION_TRACE_DEFINITION
            and configuration == EXPECTED_INTERFACE_CONFIGURATION
            and raw_row.get("pinned_matching_premise") == connection_statement
            and len(raw_side_rows) == 1
            and raw_side_rows[0].get("transformed_reduces_to_baseline") is True
            and len(route_rows) == 2
            and all(
                row["all_occurrences_are_the_same_expected_A_e"]
                and row[
                    "one_structural_A_e_symbol_type_pullback_on_this_route"
                ]
                and row["structural_multiplicity_is_exact"]
                for row in route_rows
            )
            and frozenset(route_connection_nodes) == frozenset({expected_node})
        )
        rows.append(
            {
                "side": side,
                "pinned_connection_trace_definition": definition,
                "pinned_common_interface_configuration": connection_statement,
                "connection_atom": expected_node.name,
                "source_gauge_atom": f"p_{side}",
                "transition_atom": f"r_{side}",
                "target_gauge_atom": target_gauges[side],
                "actual_action_component_routes": route_rows,
                "exactly_two_action_component_routes": len(route_rows) == 2,
                "two_semantic_routes_not_two_AST_visits": True,
                "same_structural_A_e_symbol_type_pullback_on_both_routes": (
                    frozenset(route_connection_nodes)
                    == frozenset({expected_node})
                ),
                "raw_pullback_row_bound": len(raw_side_rows) == 1,
                "pass": exact,
            }
        )
    return tuple(rows)


def _affine_side_identity(
    binding: Mapping[str, Any],
    mutation: str = "exact",
) -> dict[str, Any]:
    if mutation not in AFFINE_SIDE_MUTATIONS:
        raise NaturalityCertificateError(
            f"unknown affine side mutation: {mutation}"
        )
    side = str(binding["side"])
    connection_atom = str(binding["connection_atom"])
    p_atom = str(binding["source_gauge_atom"])
    r_atom = str(binding["transition_atom"])
    q_atom = str(binding["target_gauge_atom"])
    p_inverse = _inverse_affine_group_atom(p_atom)
    r_inverse = _inverse_affine_group_atom(r_atom)
    q_inverse = _inverse_affine_group_atom(q_atom)
    connection = NoncommutativePolynomial.word(connection_atom)

    d_p, _d_p_trace = _differentiate_affine_group_word((p_atom,))
    source_affine_coefficient = -1
    if mutation == "missing_source_affine_term":
        source_affine_coefficient = 0
    elif mutation == "wrong_source_affine_sign":
        source_affine_coefficient = 1
    source_homogeneous = _conjugate_affine_polynomial((p_atom,), connection)
    source_inhomogeneous = d_p.multiply(
        NoncommutativePolynomial.word(p_inverse)
    ).scale(source_affine_coefficient)
    transformed_source_connection = source_homogeneous.add(source_inhomogeneous)

    if mutation == "frozen_r_transport":
        r_prime = (r_atom,)
    elif mutation == "r_factor_omitted_from_transport":
        r_prime = (q_atom, p_inverse)
    elif mutation == "source_inverse_omitted_from_r_transport":
        r_prime = (q_atom, r_atom)
    else:
        r_prime = (q_atom, r_atom, p_inverse)
    expected_r_prime_inverse = _inverse_affine_group_word(r_prime)
    r_prime_inverse = expected_r_prime_inverse
    if mutation == "wrong_r_prime_inverse_order":
        r_prime_inverse = (q_inverse, r_inverse, p_atom)

    inverse_rule = "exact"
    if mutation == "wrong_inverse_derivative_sign":
        inverse_rule = "wrong_sign"
    elif mutation == "wrong_inverse_derivative_order":
        inverse_rule = "wrong_order"
    omitted_generators = frozenset()
    if mutation == "omit_p_Leibniz_term":
        omitted_generators = frozenset({p_atom})
    elif mutation == "omit_r_Leibniz_term":
        omitted_generators = frozenset({r_atom})
    elif mutation == "omit_q_Leibniz_term":
        omitted_generators = frozenset({q_atom})
    d_r_prime, d_r_prime_trace = _differentiate_affine_group_word(
        r_prime,
        inverse_rule=inverse_rule,
        omitted_generators=omitted_generators,
    )
    lhs_homogeneous = _conjugate_affine_polynomial(
        r_prime,
        transformed_source_connection,
        inverse_word=r_prime_inverse,
    )
    lhs_homogeneous_distributed = _conjugate_affine_polynomial(
        r_prime,
        source_homogeneous,
        inverse_word=r_prime_inverse,
    ).add(
        _conjugate_affine_polynomial(
            r_prime,
            source_inhomogeneous,
            inverse_word=r_prime_inverse,
        )
    )
    lhs_inhomogeneous = d_r_prime.multiply(
        NoncommutativePolynomial.word(*r_prime_inverse)
    ).scale(-1)
    lhs = lhs_homogeneous.add(lhs_inhomogeneous)

    d_r, _d_r_trace = _differentiate_affine_group_word((r_atom,))
    source_trace_homogeneous = _conjugate_affine_polynomial(
        (r_atom,), connection
    )
    source_trace_inhomogeneous = d_r.multiply(
        NoncommutativePolynomial.word(r_inverse)
    ).scale(-1)
    source_trace = source_trace_homogeneous.add(source_trace_inhomogeneous)
    source_trace_expected = NoncommutativePolynomial.from_terms(
        (
            (1, (r_atom, connection_atom, r_inverse)),
            (-1, (f"d_{r_atom}", r_inverse)),
        )
    )
    rhs_homogeneous = _conjugate_affine_polynomial((q_atom,), source_trace)
    rhs_homogeneous_distributed = _conjugate_affine_polynomial(
        (q_atom,), source_trace_homogeneous
    ).add(
        _conjugate_affine_polynomial(
            (q_atom,), source_trace_inhomogeneous
        )
    )
    d_q, _d_q_trace = _differentiate_affine_group_word((q_atom,))
    target_affine_coefficient = -1
    if mutation == "missing_target_affine_term":
        target_affine_coefficient = 0
    elif mutation == "wrong_target_affine_sign":
        target_affine_coefficient = 1
    rhs_inhomogeneous = d_q.multiply(
        NoncommutativePolynomial.word(q_inverse)
    ).scale(target_affine_coefficient)
    rhs = rhs_homogeneous.add(rhs_inhomogeneous)

    expected_normal_form = NoncommutativePolynomial.from_terms(
        (
            (
                1,
                (
                    q_atom,
                    r_atom,
                    connection_atom,
                    r_inverse,
                    q_inverse,
                ),
            ),
            (-1, (q_atom, f"d_{r_atom}", r_inverse, q_inverse)),
            (-1, (f"d_{q_atom}", q_inverse)),
        )
    )
    residual = lhs.subtract(rhs)
    lhs_source_dp_homogeneous = lhs_homogeneous.containing(f"d_{p_atom}")
    lhs_source_dp_inhomogeneous = lhs_inhomogeneous.containing(f"d_{p_atom}")
    source_dp_sum = lhs_source_dp_homogeneous.add(
        lhs_source_dp_inhomogeneous
    )
    inverse_slot_rows = [
        row for row in d_r_prime_trace if row["group_atom"] == p_inverse
    ]
    expected_inverse_derivative = NoncommutativePolynomial.from_terms(
        ((-1, (p_inverse, f"d_{p_atom}", p_inverse)),)
    )
    inverse_derivative_exact = (
        len(inverse_slot_rows) == 1
        and inverse_slot_rows[0]["atom_derivative_terms"]
        == _nc_terms(expected_inverse_derivative)
    )
    reduced_identity, inverse_cancellation_steps = _reduce_affine_word(
        r_prime + tuple(r_prime_inverse)
    )
    kernel_checks = {
        "integer_noncommutative_linear_collection": all(
            isinstance(coefficient, int)
            for polynomial in (lhs, rhs, expected_normal_form, residual)
            for _word, coefficient in polynomial.terms
        ),
        "noncommutative_distributive_word_product": (
            bool(source_homogeneous.terms)
            and bool(source_inhomogeneous.terms)
            and bool(source_trace_homogeneous.terms)
            and bool(source_trace_inhomogeneous.terms)
            and lhs_homogeneous == lhs_homogeneous_distributed
            and rhs_homogeneous == rhs_homogeneous_distributed
        ),
        "full_Leibniz_rule_for_group_words": (
            len(d_r_prime_trace) == len(r_prime)
            and tuple(row["Leibniz_slot"] for row in d_r_prime_trace)
            == tuple(range(len(r_prime)))
            and all(
                row["atom_rule"] != "omitted_mutant"
                for row in d_r_prime_trace
            )
        ),
        "group_inverse_derivative_rule": inverse_derivative_exact,
        "adjacent_group_inverse_cancellation": (
            not reduced_identity and bool(inverse_cancellation_steps)
        ),
    }
    source_dp_cancels = (
        bool(lhs_source_dp_homogeneous.terms)
        and bool(lhs_source_dp_inhomogeneous.terms)
        and not source_dp_sum.terms
    )
    identity_pass = (
        binding.get("pass") is True
        and all(kernel_checks.values())
        and source_dp_cancels
        and tuple(r_prime_inverse) == expected_r_prime_inverse
        and lhs == rhs == expected_normal_form
        and not residual.terms
    )
    source_trace_bound_to_common_interface = (
        binding.get("pass") is True
        and binding.get("pinned_connection_trace_definition")
        == EXPECTED_CONNECTION_TRACE_DEFINITION
        and binding.get("pinned_common_interface_configuration")
        == EXPECTED_INTERFACE_CONFIGURATION[3]
        and source_trace == source_trace_expected
    )
    substituted_source_trace = (
        NoncommutativePolynomial.word("A_Sigma")
        if source_trace_bound_to_common_interface
        else NoncommutativePolynomial.zero()
    )
    common_interface_target = _conjugate_affine_polynomial(
        (q_atom,), substituted_source_trace
    ).add(rhs_inhomogeneous)
    return {
        "side": side,
        "mutation": mutation,
        "source_connection_atom_from_actual_action_tree": connection_atom,
        "source_gauge_atom": p_atom,
        "transition_atom": r_atom,
        "shared_target_gauge_atom": q_atom,
        "A_prime_identity": "A'=p A p^-1-(d p)p^-1",
        "r_prime_identity": "r'=q r p^-1",
        "r_prime_word": list(r_prime),
        "r_prime_inverse_word": list(r_prime_inverse),
        "expected_r_prime_inverse_word": list(expected_r_prime_inverse),
        "d_r_prime_Leibniz_trace": list(d_r_prime_trace),
        "source_trace_before_common_interface_substitution_terms": _nc_terms(
            source_trace
        ),
        "expected_Trans_r_A_terms": _nc_terms(source_trace_expected),
        "source_trace_matches_bound_Trans_r_A": (
            source_trace_bound_to_common_interface
        ),
        "common_interface_substitution": "Trans_r_e(A_e)->A_Sigma",
        "common_interface_substitution_applied": (
            source_trace_bound_to_common_interface
        ),
        "lhs_terms": _nc_terms(lhs),
        "rhs_terms": _nc_terms(rhs),
        "expected_normal_form_terms": _nc_terms(expected_normal_form),
        "residual_terms": _nc_terms(residual),
        "source_dp_terms_from_r_prime_A_prime_r_prime_inverse": _nc_terms(
            lhs_source_dp_homogeneous
        ),
        "source_dp_terms_from_minus_d_r_prime_r_prime_inverse": _nc_terms(
            lhs_source_dp_inhomogeneous
        ),
        "source_dp_cancellation_terms": _nc_terms(source_dp_sum),
        "source_dp_cancels_exactly": source_dp_cancels,
        "distributive_expansion_witness": {
            "lhs_conjugation_of_sum_terms": _nc_terms(lhs_homogeneous),
            "lhs_sum_of_conjugated_terms": _nc_terms(
                lhs_homogeneous_distributed
            ),
            "rhs_conjugation_of_sum_terms": _nc_terms(rhs_homogeneous),
            "rhs_sum_of_conjugated_terms": _nc_terms(
                rhs_homogeneous_distributed
            ),
        },
        "kernel_rule_checks": kernel_checks,
        "common_interface_target_terms": _nc_terms(common_interface_target),
        "polynomial_identity_exact": lhs == rhs == expected_normal_form,
        "pass": identity_pass,
    }


def _affine_connection_trace_ledger(
    v52: Mapping[str, Any],
    interface_raw_pullback: Mapping[str, Any],
    *,
    components: Mapping[str, Expression] | None = None,
    side_mutations: Mapping[str, str] | None = None,
    target_gauges: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    actual_components = (
        build_component_expressions("finite")
        if components is None
        else components
    )
    mutations = {side: "exact" for side in SIDES}
    if side_mutations is not None:
        if not set(side_mutations).issubset(SIDES):
            raise NaturalityCertificateError(
                "unknown side in affine mutation map"
            )
        mutations.update(side_mutations)
    gauges = {side: "q" for side in SIDES}
    if target_gauges is not None:
        if not set(target_gauges).issubset(SIDES):
            raise NaturalityCertificateError(
                "unknown side in affine target-gauge map"
            )
        gauges.update(target_gauges)
    bindings = _connection_trace_binding_rows(
        v52,
        interface_raw_pullback,
        actual_components,
        gauges,
    )
    side_rows = tuple(
        _affine_side_identity(binding, mutations[str(binding["side"])])
        for binding in bindings
    )
    common_target_terms = tuple(
        tuple(
            (tuple(term["word"]), int(term["coefficient"]))
            for term in row["common_interface_target_terms"]
        )
        for row in side_rows
    )
    common_q = (
        tuple(row["shared_target_gauge_atom"] for row in side_rows)
        == ("q", "q")
    )
    common_target_exact = (
        len(common_target_terms) == 2
        and common_target_terms[0] == common_target_terms[1]
    )
    transported_trace_equality_exact = (
        common_q
        and common_target_exact
        and all(binding["pass"] for binding in bindings)
        and all(
            row["pass"]
            and row["polynomial_identity_exact"]
            and row["common_interface_substitution_applied"]
            for row in side_rows
        )
    )
    consumed_rules = frozenset(
        name
        for row in side_rows
        for name, value in row["kernel_rule_checks"].items()
        if value
    )
    literal_definition = (
        v52.get("exact_classical_charter", {})
        .get("definitions", {})
        .get("connection_trace")
    )
    literal_configuration = tuple(
        v52.get("exact_classical_charter", {})
        .get("interface_domain", {})
        .get("configuration", ())
    )
    pass_exact = (
        literal_definition == EXPECTED_CONNECTION_TRACE_DEFINITION
        and literal_configuration == EXPECTED_INTERFACE_CONFIGURATION
        and len(bindings) == len(SIDES)
        and all(binding["pass"] for binding in bindings)
        and all(row["pass"] for row in side_rows)
        and transported_trace_equality_exact
        and consumed_rules == EXPECTED_AFFINE_KERNEL_RULES
    )
    return {
        "scope": "finite affine SO3 connection trace transport only",
        "formal_domain": {
            "connections": "Lie(SO3)-valued one-forms A_plus and A_minus",
            "group_maps": (
                "smooth SO3-valued zero-forms p_plus, p_minus, r_plus, "
                "r_minus and one shared q"
            ),
            "differential_degree": (
                "group maps have degree zero; d_p, d_r and d_q have degree one"
            ),
            "coefficient_ring": "exact integers",
            "word_product": "associative and noncommutative",
        },
        "pinned_connection_trace_definition": literal_definition,
        "pinned_common_interface_configuration": literal_configuration[3],
        "finite_transformation_rules": {
            "bulk_connection": "A'=p A p^-1-(d p)p^-1",
            "interface_transition": "r'=q r p^-1",
            "transition_inverse": "(r')^-1=p r^-1 q^-1",
            "inverse_derivative": "d(p^-1)=-p^-1(d p)p^-1",
            "target_connection": (
                "A_Sigma'=q A_Sigma q^-1-(d q)q^-1"
            ),
        },
        "binding_rows": list(bindings),
        "side_polynomial_identities": list(side_rows),
        "target_gauge_atoms_by_side": [
            row["shared_target_gauge_atom"] for row in side_rows
        ],
        "same_literal_q_and_dq_used_on_both_sides": common_q,
        "common_transformed_A_Sigma_terms": (
            list(side_rows[0]["common_interface_target_terms"])
            if transported_trace_equality_exact
            else []
        ),
        "two_transformed_interface_traces_remain_equal": (
            transported_trace_equality_exact
        ),
        "expected_kernel_rules": sorted(EXPECTED_AFFINE_KERNEL_RULES),
        "consumed_kernel_rules": sorted(consumed_rules),
        "every_affine_kernel_rule_consumed_exactly": (
            consumed_rules == EXPECTED_AFFINE_KERNEL_RULES
        ),
        "BF_incidence_or_Green_identity_claimed": False,
        "pass": pass_exact,
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


def _exact_bf_side_mapping(
    name: str,
    values: Mapping[str, Any],
) -> dict[str, Any]:
    if set(values) != set(SIDES):
        raise NaturalityCertificateError(
            f"{name} must contain exactly the plus and minus sides"
        )
    return {side: values[side] for side in SIDES}


def _bf_action_route_binding_rows(
    components: Mapping[str, Expression],
) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    expected_signature = EXPECTED_SEMANTIC_SIGNATURES["BF"]
    for side in SIDES:
        component_name = f"BF_bulk_{side}"
        expression = components.get(component_name)
        expression_is_typed = isinstance(
            expression, (PulledField, SolderedMatter, Construction)
        )
        b_nodes = (
            tuple(
                node
                for node in _pulled_field_nodes(expression)
                if node.type_tag == ADJOINT3_5
            )
            if expression_is_typed
            else ()
        )
        a_nodes = (
            tuple(
                node
                for node in _pulled_field_nodes(expression)
                if node.type_tag == CONNECTION1_5
            )
            if expression_is_typed
            else ()
        )
        expected_b = _bulk_field(side, "B", ADJOINT3_5, "finite")
        expected_a = _bulk_field(side, "A", CONNECTION1_5, "finite")
        signature = (
            _expression_signature(expression) if expression_is_typed else None
        )
        exact = bool(
            isinstance(expression, Construction)
            and expression.operator == "invariant_B_wedge_F"
            and expression.type_tag == FORM5
            and signature == expected_signature
            and b_nodes == (expected_b,)
            and a_nodes == (expected_a,)
        )
        rows.append(
            {
                "side": side,
                "component": component_name,
                "root_operator": (
                    expression.operator
                    if isinstance(expression, Construction)
                    else None
                ),
                "semantic_operator_signature": signature,
                "B_occurrence_count": len(b_nodes),
                "A_occurrence_count": len(a_nodes),
                "B_symbols": [node.name for node in b_nodes],
                "A_symbols": [node.name for node in a_nodes],
                "B_pullback_words": [
                    list(node.pullback_factors) for node in b_nodes
                ],
                "A_pullback_words": [
                    list(node.pullback_factors) for node in a_nodes
                ],
                "expected_B_symbol_type_pullback": {
                    "symbol": expected_b.name,
                    "type": asdict(expected_b.type_tag),
                    "pullback_word": list(expected_b.pullback_factors),
                },
                "expected_A_symbol_type_pullback": {
                    "symbol": expected_a.name,
                    "type": asdict(expected_a.type_tag),
                    "pullback_word": list(expected_a.pullback_factors),
                },
                "pass": exact,
            }
        )
    return tuple(rows)


def _serialize_pulled_field(node: PulledField | None) -> dict[str, Any] | None:
    if node is None:
        return None
    return {
        "symbol": node.name,
        "type": asdict(node.type_tag),
        "pullback_word": list(node.pullback_factors),
    }


def _bf_trace_binding_rows(
    v52: Mapping[str, Any],
    components: Mapping[str, Expression],
    affine_connection_trace: Mapping[str, Any],
    *,
    trace_binding_mutations: Mapping[str, str] | None = None,
) -> tuple[dict[str, Any], ...]:
    mutations = {side: "exact" for side in SIDES}
    if trace_binding_mutations is not None:
        if not set(trace_binding_mutations).issubset(SIDES):
            raise NaturalityCertificateError(
                "unknown side in BF trace-binding mutation map"
            )
        mutations.update(trace_binding_mutations)
    if any(value not in BF_TRACE_BINDING_MUTATIONS for value in mutations.values()):
        raise NaturalityCertificateError("unknown BF trace-binding mutation")

    charter = v52.get("exact_classical_charter", {})
    definition = charter.get("definitions", {}).get("adjoint_form_trace")
    configuration = tuple(
        charter.get("interface_domain", {}).get("configuration", ())
    )
    affine_bindings = tuple(affine_connection_trace.get("binding_rows", ()))
    affine_identities = tuple(
        affine_connection_trace.get("side_polynomial_identities", ())
    )
    common_target_terms = tuple(
        (
            tuple(term.get("word", ())),
            int(term.get("coefficient", 0)),
        )
        for term in affine_connection_trace.get(
            "common_transformed_A_Sigma_terms", ()
        )
    )
    rows: list[dict[str, Any]] = []
    for side in SIDES:
        expression = components.get(f"BF_bulk_{side}")
        expression_is_typed = isinstance(
            expression, (PulledField, SolderedMatter, Construction)
        )
        b_nodes = (
            tuple(
                node
                for node in _pulled_field_nodes(expression)
                if node.type_tag == ADJOINT3_5
            )
            if expression_is_typed
            else ()
        )
        a_nodes = (
            tuple(
                node
                for node in _pulled_field_nodes(expression)
                if node.type_tag == CONNECTION1_5
            )
            if expression_is_typed
            else ()
        )
        source_b = b_nodes[0] if len(b_nodes) == 1 else None
        source_a = a_nodes[0] if len(a_nodes) == 1 else None
        expected_b = _bulk_field(side, "B", ADJOINT3_5, "finite")
        expected_a = _bulk_field(side, "A", CONNECTION1_5, "finite")

        side_affine_bindings = tuple(
            row for row in affine_bindings if row.get("side") == side
        )
        side_affine_identities = tuple(
            row for row in affine_identities if row.get("side") == side
        )
        affine_binding = (
            side_affine_bindings[0] if len(side_affine_bindings) == 1 else {}
        )
        affine_identity = (
            side_affine_identities[0]
            if len(side_affine_identities) == 1
            else {}
        )
        transition_atom = affine_binding.get("transition_atom")

        mutation = mutations[side]
        trace_source_b = source_b
        if mutation == "detached_b_trace" and source_b is not None:
            trace_source_b = PulledField(
                name=f"detached_{source_b.name}",
                type_tag=source_b.type_tag,
                pullback_factors=source_b.pullback_factors,
            )
        adjoint_trace_output = f"b_{side}"
        source_b_bound = bool(
            definition == EXPECTED_ADJOINT_FORM_TRACE_DEFINITION
            and source_b == expected_b
            and trace_source_b == source_b
            and transition_atom == f"r_{side}"
            and adjoint_trace_output == f"b_{side}"
        )

        affine_target_atom = "A_Sigma"
        if mutation == "detached_affine_target":
            affine_target_atom = "detached_A_Sigma"
        boundary_variation_atom = f"Delta_{affine_target_atom}"
        affine_source_bound = bool(
            source_a == expected_a
            and affine_binding.get("pass") is True
            and affine_binding.get("connection_atom") == source_a.name
            and affine_identity.get("pass") is True
            and affine_identity.get(
                "source_connection_atom_from_actual_action_tree"
            )
            == source_a.name
            and affine_identity.get("source_trace_matches_bound_Trans_r_A")
            is True
            and affine_identity.get("common_interface_substitution")
            == "Trans_r_e(A_e)->A_Sigma"
            and affine_identity.get("common_interface_substitution_applied")
            is True
            and configuration == EXPECTED_INTERFACE_CONFIGURATION
            and affine_target_atom == "A_Sigma"
            and boundary_variation_atom == "Delta_A_Sigma"
            and common_target_terms
            and tuple(
                (
                    tuple(term.get("word", ())),
                    int(term.get("coefficient", 0)),
                )
                for term in affine_identity.get(
                    "common_interface_target_terms", ()
                )
            )
            == common_target_terms
        )
        rows.append(
            {
                "side": side,
                "mutation": mutation,
                "source_B_node_from_actual_BF_action": _serialize_pulled_field(
                    source_b
                ),
                "adjoint_trace_input_node": _serialize_pulled_field(
                    trace_source_b
                ),
                "adjoint_trace_transition_atom_from_affine_binding": (
                    transition_atom
                ),
                "adjoint_trace_output_atom": adjoint_trace_output,
                "adjoint_trace_equation": (
                    f"Ad_{transition_atom}(Y_{side}^*{trace_source_b.name})="
                    f"{adjoint_trace_output}"
                    if trace_source_b is not None and transition_atom
                    else None
                ),
                "source_B_node_bound_to_adjoint_trace": source_b_bound,
                "source_A_node_from_actual_BF_action": _serialize_pulled_field(
                    source_a
                ),
                "affine_source_connection_atom": affine_binding.get(
                    "connection_atom"
                ),
                "affine_common_target_atom": affine_target_atom,
                "boundary_variation_atom_derived_from_affine_target": (
                    boundary_variation_atom
                ),
                "source_A_node_bound_through_affine_trace_to_variation": (
                    affine_source_bound
                ),
                "affine_common_target_terms": [
                    {"word": list(word), "coefficient": coefficient}
                    for word, coefficient in common_target_terms
                ],
                "pass": bool(source_b_bound and affine_source_bound),
            }
        )
    return tuple(rows)


def _bf_incidence_aggregation_ledger(
    v52: Mapping[str, Any],
    *,
    components: Mapping[str, Expression] | None = None,
    affine_connection_trace: Mapping[str, Any] | None = None,
    orientation_signs: Mapping[str, int] | None = None,
    variation_atoms: Mapping[str, str] | None = None,
    trace_binding_mutations: Mapping[str, str] | None = None,
    boundary_prefactor: int = -1,
) -> dict[str, Any]:
    actual_components = (
        build_component_expressions("finite")
        if components is None
        else components
    )
    signs = _exact_bf_side_mapping(
        "BF orientation signs",
        BF_ORIENTATION_SIGNS if orientation_signs is None else orientation_signs,
    )
    if any(isinstance(value, bool) or not isinstance(value, int) for value in signs.values()):
        raise NaturalityCertificateError("BF orientation signs must be exact integers")
    if isinstance(boundary_prefactor, bool) or not isinstance(boundary_prefactor, int):
        raise NaturalityCertificateError("BF boundary prefactor must be an exact integer")

    charter = v52.get("exact_classical_charter", {})
    exact_action = charter.get("exact_action", {})
    interface_domain = charter.get("interface_domain", {})
    definitions = charter.get("definitions", {})
    green_certificate = v52.get("Green_form_certificate", {})
    interface_variation_rows = tuple(interface_domain.get("variations", ()))
    literal_bf_bindings = tuple(
        binding
        for binding in literal_component_bindings()
        if binding.name.startswith("BF_bulk_")
    )
    literal_binding_exact = bool(
        tuple(binding.name for binding in literal_bf_bindings)
        == ("BF_bulk_plus", "BF_bulk_minus")
        and all(binding.source_keys == ("BF",) for binding in literal_bf_bindings)
        and all(
            binding.required_fragments == (("BF", "<B_eps wedge F[A_eps]>"),)
            for binding in literal_bf_bindings
        )
    )
    pinned_literals = {
        "BF_action": exact_action.get("BF"),
        "adjoint_form_trace": definitions.get("adjoint_form_trace"),
        "common_interface_variations": (
            interface_variation_rows[0] if interface_variation_rows else None
        ),
        "Green_form": green_certificate.get("Green_form"),
        "natural_B_flux_equation": interface_domain.get(
            "natural_B_flux_equation"
        ),
        "natural_interface_BF_flux": green_certificate.get(
            "natural_interface_equations", {}
        ).get("BF_flux"),
    }
    pinned_literals_exact = pinned_literals == {
        "BF_action": EXPECTED_BF_ACTION_LITERAL,
        "adjoint_form_trace": EXPECTED_ADJOINT_FORM_TRACE_DEFINITION,
        "common_interface_variations": EXPECTED_COMMON_INTERFACE_VARIATIONS,
        "Green_form": EXPECTED_BF_GREEN_FORM,
        "natural_B_flux_equation": EXPECTED_BF_INCIDENCE,
        "natural_interface_BF_flux": EXPECTED_BF_NATURAL_INTERFACE_EQUATION,
    }

    route_rows = _bf_action_route_binding_rows(actual_components)
    actual_affine_connection_trace = (
        _affine_connection_trace_ledger(
            v52,
            _interface_raw_pullback_ledger(),
            components=actual_components,
        )
        if affine_connection_trace is None
        else affine_connection_trace
    )
    trace_binding_rows = _bf_trace_binding_rows(
        v52,
        actual_components,
        actual_affine_connection_trace,
        trace_binding_mutations=trace_binding_mutations,
    )
    trace_rows_by_side = {row["side"]: row for row in trace_binding_rows}
    derived_variations = {
        side: trace_rows_by_side[side][
            "boundary_variation_atom_derived_from_affine_target"
        ]
        for side in SIDES
    }
    variations = _exact_bf_side_mapping(
        "BF variation atoms",
        derived_variations if variation_atoms is None else variation_atoms,
    )
    if any(not isinstance(value, str) or not value for value in variations.values()):
        raise NaturalityCertificateError("BF variation atoms must be nonempty strings")
    oriented_flux = LinearCombination.from_mapping(
        {
            trace_rows_by_side[side]["adjoint_trace_output_atom"]: signs[side]
            for side in SIDES
        }
    )
    expected_flux = _linear(b_plus=1, b_minus=-1)
    common_variation = (
        len(set(variations.values())) == 1
        and tuple(variations.values()) == ("Delta_A_Sigma", "Delta_A_Sigma")
        and variations == derived_variations
    )
    boundary_integrand = LinearCombination.from_mapping(
        {
            (
                f"{trace_rows_by_side[side]['adjoint_trace_output_atom']}"
                f"_wedge_{variations[side]}"
            ): (
                boundary_prefactor * signs[side]
            )
            for side in SIDES
        }
    )
    expected_boundary_integrand = _linear(
        b_plus_wedge_Delta_A_Sigma=-1,
        b_minus_wedge_Delta_A_Sigma=1,
    )
    quotient_rule_consumed = bool(
        pinned_literals_exact
        and all(row["pass"] for row in trace_binding_rows)
        and oriented_flux == expected_flux
    )
    flux_mod_natural_interface_equation = (
        LinearCombination(()) if quotient_rule_consumed else oriented_flux
    )
    off_shell_flux_is_nonzero = not oriented_flux.is_zero
    pass_exact = bool(
        literal_binding_exact
        and pinned_literals_exact
        and all(row["pass"] for row in route_rows)
        and actual_affine_connection_trace.get("pass") is True
        and len(trace_binding_rows) == len(SIDES)
        and all(row["pass"] for row in trace_binding_rows)
        and signs == BF_ORIENTATION_SIGNS
        and common_variation
        and boundary_prefactor == -1
        and oriented_flux == expected_flux
        and boundary_integrand == expected_boundary_integrand
        and off_shell_flux_is_nonzero
        and quotient_rule_consumed
        and flux_mod_natural_interface_equation.is_zero
    )
    return {
        "scope": (
            "literal oriented BF boundary-incidence aggregation; not an "
            "off-shell cancellation and not the complete Green ledger"
        ),
        "pinned_literals": pinned_literals,
        "literal_BF_component_bindings_exact": literal_binding_exact,
        "actual_BF_action_route_bindings": list(route_rows),
        "typed_B_and_affine_target_trace_binding_rows": list(
            trace_binding_rows
        ),
        "all_BF_boundary_atoms_derived_from_typed_trace_rows": bool(
            len(trace_binding_rows) == len(SIDES)
            and all(row["pass"] for row in trace_binding_rows)
        ),
        "orientation_sign_rows": [
            {
                "side": side,
                "s_epsilon": signs[side],
                "boundary_variation_atom": variations[side],
            }
            for side in SIDES
        ],
        "boundary_prefactor": boundary_prefactor,
        "oriented_flux_terms": list(oriented_flux.terms),
        "expected_b_plus_minus_b_minus_terms": list(expected_flux.terms),
        "common_Delta_A_Sigma_factored": common_variation,
        "oriented_boundary_integrand_terms": list(boundary_integrand.terms),
        "expected_boundary_integrand_terms": list(
            expected_boundary_integrand.terms
        ),
        "off_shell_oriented_flux_is_nonzero": off_shell_flux_is_nonzero,
        "off_shell_cancellation_claimed": False,
        "natural_interface_equation_imposed_for_quotient": (
            EXPECTED_BF_NATURAL_INTERFACE_EQUATION
        ),
        "natural_interface_equation_quotient_rule_consumed": (
            quotient_rule_consumed
        ),
        "flux_terms_mod_natural_interface_equation": list(
            flux_mod_natural_interface_equation.terms
        ),
        "on_shell_cancellation_only": bool(
            quotient_rule_consumed
            and flux_mod_natural_interface_equation.is_zero
        ),
        "full_Green_or_Ward_identity_claimed": False,
        "decision_also_requires_separate_affine_connection_trace_pass": True,
        "pass": pass_exact,
    }


def _bf_incidence_mutant_campaign(
    v52: Mapping[str, Any],
    *,
    affine_connection_trace: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    cases = {
        "same_orientation_sign": {"plus": 1, "minus": 1},
        "reversed_orientation_signs": {"plus": -1, "minus": 1},
        "minus_side_omitted": {"plus": 1, "minus": 0},
    }
    for name, signs in cases.items():
        ledger = _bf_incidence_aggregation_ledger(
            v52,
            affine_connection_trace=affine_connection_trace,
            orientation_signs=signs,
        )
        rows[name] = {
            "killed": (
                not ledger["pass"]
                and ledger["oriented_flux_terms"]
                != ledger["expected_b_plus_minus_b_minus_terms"]
            ),
            "oriented_flux_terms": ledger["oriented_flux_terms"],
        }

    split_variation = _bf_incidence_aggregation_ledger(
        v52,
        affine_connection_trace=affine_connection_trace,
        variation_atoms={"plus": "Delta_A_plus", "minus": "Delta_A_minus"},
    )
    rows["split_Delta_A_between_sides"] = {
        "killed": (
            not split_variation["pass"]
            and not split_variation["common_Delta_A_Sigma_factored"]
        ),
        "boundary_integrand_terms": split_variation[
            "oriented_boundary_integrand_terms"
        ],
    }

    wrong_prefactor = _bf_incidence_aggregation_ledger(
        v52,
        affine_connection_trace=affine_connection_trace,
        boundary_prefactor=1,
    )
    rows["wrong_global_boundary_sign"] = {
        "killed": (
            not wrong_prefactor["pass"]
            and wrong_prefactor["oriented_boundary_integrand_terms"]
            != wrong_prefactor["expected_boundary_integrand_terms"]
        ),
        "boundary_integrand_terms": wrong_prefactor[
            "oriented_boundary_integrand_terms"
        ],
    }

    for role in ("B", "A"):
        detached_components = build_component_expressions("finite")
        detached_components["BF_bulk_plus"] = _replace_semantic_leaf_role(
            detached_components["BF_bulk_plus"],
            role,
            f"detached_{role}",
        )
        detached = _bf_incidence_aggregation_ledger(
            v52,
            components=detached_components,
        )
        plus_route = next(
            row
            for row in detached["actual_BF_action_route_bindings"]
            if row["side"] == "plus"
        )
        rows[f"detached_{role}_from_actual_BF_route"] = {
            "killed": (
                not detached["pass"]
                and not plus_route["pass"]
                and all(
                    row["pass"]
                    for row in detached["actual_BF_action_route_bindings"]
                    if row["side"] == "minus"
                )
            ),
            "plus_route": plus_route,
        }
    for mutation in ("detached_b_trace", "detached_affine_target"):
        detached_trace = _bf_incidence_aggregation_ledger(
            v52,
            affine_connection_trace=affine_connection_trace,
            trace_binding_mutations={"plus": mutation},
        )
        plus_trace = next(
            row
            for row in detached_trace[
                "typed_B_and_affine_target_trace_binding_rows"
            ]
            if row["side"] == "plus"
        )
        minus_trace = next(
            row
            for row in detached_trace[
                "typed_B_and_affine_target_trace_binding_rows"
            ]
            if row["side"] == "minus"
        )
        rows[mutation] = {
            "killed": bool(
                not detached_trace["pass"]
                and not plus_trace["pass"]
                and minus_trace["pass"]
            ),
            "plus_trace_binding": plus_trace,
        }
    return {
        "rows": rows,
        "mutant_count": len(rows),
        "pass": bool(rows) and all(row["killed"] for row in rows.values()),
    }


def _integer_gcd(left: int, right: int) -> int:
    left = abs(left)
    right = abs(right)
    while right:
        left, right = right, left % right
    return left or 1


@dataclass(frozen=True, order=True)
class ExactCoefficient:
    """A reduced rational monomial over named, commuting parameters."""

    numerator: int
    denominator: int
    powers: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.numerator, bool)
            or not isinstance(self.numerator, int)
            or isinstance(self.denominator, bool)
            or not isinstance(self.denominator, int)
            or self.denominator <= 0
            or _integer_gcd(self.numerator, self.denominator) != 1
            or tuple(sorted(self.powers)) != self.powers
            or len({name for name, _power in self.powers}) != len(self.powers)
            or any(
                not isinstance(name, str)
                or not name
                or isinstance(power, bool)
                or not isinstance(power, int)
                or power == 0
                for name, power in self.powers
            )
            or (self.numerator == 0 and (self.denominator != 1 or self.powers))
        ):
            raise NaturalityCertificateError(
                "Green coefficient is not a canonical exact rational monomial"
            )

    @classmethod
    def from_parts(
        cls,
        numerator: int,
        denominator: int = 1,
        powers: Sequence[tuple[str, int]] = (),
    ) -> ExactCoefficient:
        if (
            isinstance(numerator, bool)
            or not isinstance(numerator, int)
            or isinstance(denominator, bool)
            or not isinstance(denominator, int)
            or denominator == 0
        ):
            raise NaturalityCertificateError(
                "exact Green coefficients require integer numerator and nonzero denominator"
            )
        collected: dict[str, int] = {}
        for name, power in powers:
            if (
                not isinstance(name, str)
                or not name
                or isinstance(power, bool)
                or not isinstance(power, int)
            ):
                raise NaturalityCertificateError(
                    "exact Green monomial powers require named integer exponents"
                )
            collected[name] = collected.get(name, 0) + power
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator
        divisor = _integer_gcd(numerator, denominator)
        numerator //= divisor
        denominator //= divisor
        canonical_powers = tuple(
            sorted((name, power) for name, power in collected.items() if power)
        )
        if numerator == 0:
            canonical_powers = ()
            denominator = 1
        return cls(numerator, denominator, canonical_powers)

    def multiply(self, other: ExactCoefficient) -> ExactCoefficient:
        return ExactCoefficient.from_parts(
            self.numerator * other.numerator,
            self.denominator * other.denominator,
            self.powers + other.powers,
        )

    def add(self, other: ExactCoefficient) -> ExactCoefficient:
        if self.powers != other.powers:
            raise NaturalityCertificateError(
                "cannot add exact Green coefficients with different monomials"
            )
        return ExactCoefficient.from_parts(
            self.numerator * other.denominator
            + other.numerator * self.denominator,
            self.denominator * other.denominator,
            self.powers,
        )

    def negate(self) -> ExactCoefficient:
        return ExactCoefficient.from_parts(
            -self.numerator, self.denominator, self.powers
        )

    @property
    def is_zero(self) -> bool:
        return self.numerator == 0


def _coefficient(
    numerator: int,
    denominator: int = 1,
    **powers: int,
) -> ExactCoefficient:
    return ExactCoefficient.from_parts(
        numerator, denominator, tuple(powers.items())
    )


@dataclass(frozen=True, order=True)
class ExactGreenTerm:
    """One exact integrated boundary term, with its common variation atom."""

    factor: str
    variation: str
    coefficient: ExactCoefficient


@dataclass(frozen=True, order=True)
class DeltaPVariationTerm:
    """One typed summand in the exact product-rule expansion of Delta P."""

    term_id: str
    operator: str
    factors: tuple[str, ...]
    variation: str
    differentiated_variation: bool
    coefficient: ExactCoefficient
    boundary_channel: str | None


def _delta_p_term_signature(term: DeltaPVariationTerm) -> tuple[Any, ...]:
    return (
        term.term_id,
        term.operator,
        term.factors,
        term.variation,
        term.differentiated_variation,
        (
            term.coefficient.numerator,
            term.coefficient.denominator,
            term.coefficient.powers,
        ),
        term.boundary_channel,
    )


def _serialize_delta_p_terms(
    terms: Sequence[DeltaPVariationTerm],
) -> list[dict[str, Any]]:
    return [
        {
            "term_id": term.term_id,
            "operator": term.operator,
            "factors": list(term.factors),
            "variation": term.variation,
            "differentiated_variation": term.differentiated_variation,
            "coefficient": _serialize_coefficient(term.coefficient),
            "boundary_channel": term.boundary_channel,
        }
        for term in terms
    ]


def _collect_green_terms(
    terms: Sequence[ExactGreenTerm],
) -> tuple[ExactGreenTerm, ...]:
    collected: dict[
        tuple[str, str, tuple[tuple[str, int], ...]], ExactCoefficient
    ] = {}
    for term in terms:
        key = (term.factor, term.variation, term.coefficient.powers)
        previous = collected.get(key)
        collected[key] = (
            term.coefficient if previous is None else previous.add(term.coefficient)
        )
    return tuple(
        sorted(
            (
                ExactGreenTerm(factor, variation, coefficient)
                for (factor, variation, _powers), coefficient in collected.items()
                if not coefficient.is_zero
            ),
            key=lambda item: (
                item.factor,
                item.variation,
                item.coefficient.powers,
                item.coefficient.numerator,
                item.coefficient.denominator,
            ),
        )
    )


def _serialize_coefficient(value: ExactCoefficient) -> dict[str, Any]:
    numerator_parameters = [
        name if power == 1 else f"{name}^{power}"
        for name, power in value.powers
        if power > 0
    ]
    denominator_parameters = [
        name if power == -1 else f"{name}^{-power}"
        for name, power in value.powers
        if power < 0
    ]
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "powers": [list(item) for item in value.powers],
        "numerator_parameters": numerator_parameters,
        "denominator_parameters": denominator_parameters,
        "uses_floating_point": False,
    }


def _serialize_green_terms(
    terms: Sequence[ExactGreenTerm],
) -> list[dict[str, Any]]:
    return [
        {
            "factor": term.factor,
            "variation": term.variation,
            "coefficient": _serialize_coefficient(term.coefficient),
        }
        for term in terms
    ]


@dataclass(frozen=True)
class VariationRow:
    """One source-bound row of the integrated, reference-fixed Green ledger."""

    name: str
    components: tuple[str, ...]
    component_expressions: tuple[tuple[str, Expression], ...]
    component_weights: tuple[tuple[str, ExactCoefficient], ...]
    source_literal_keys: tuple[str, ...]
    derivation_kind: str
    bulk_euler_pairing: str
    bulk_euler_terms: tuple[ExactGreenTerm, ...]
    local_divergence: str | None
    integrated_boundary_terms: tuple[ExactGreenTerm, ...]
    intrinsic_delta: str | None


GREEN_LEDGER_MUTATIONS = frozenset(
    {
        "component_omitted",
        "component_duplicated",
        "component_swapped",
        "component_detached",
        "shared_layout_swap",
        "extra_component",
        "AST_GHOST_pullback",
        "GHY_omitted",
        "GHY_wrong_sign",
        "GHY_inward_normal",
        "Pi_Omega_kinetic_wrong_sign",
        "Pi_Omega_P_wrong_sign",
        "Pi_phi_wrong_sign",
        "P_three_halves_omitted",
        "P_three_halves_wrong",
        "DeltaP_omit_Delta_phi_dOmega",
        "DeltaP_corrupt_Delta_phi_dOmega",
        "DeltaP_omit_Omega_minus2",
        "DeltaP_corrupt_Omega_minus2",
        "DeltaP_omit_representation_DeltaA_phi",
        "DeltaP_corrupt_representation_DeltaA_phi",
        "split_common_variations",
        "Pi_phi_detached",
        "Pi_phi_unsoldered",
        "spurious_Omega_potential_current",
        "spurious_V4_current",
        "R_squared_denominator_16",
        "local_divergence_omitted",
        "BF_offshell_cancelled",
        "BF_wrong_bulk_DAB_sign",
        "BF_omit_DAB",
        "BF_internal_boundary_minus_to_plus",
        "intrinsic_producer_corruption",
    }
    | {f"intrinsic_wrong_sign_{name}" for name in INTERFACE_SECTORS}
    | {f"intrinsic_omitted_{name}" for name in INTERFACE_SECTORS}
)


def _green_component_weight(
    component: str,
    mutation: str | None = None,
) -> ExactCoefficient:
    family = _component_family(component)
    if family == "EH":
        value = _coefficient(1, 2, M5=3)
    elif family == "GHY":
        value = _coefficient(1, 1, M5=3)
    elif family == "Omega_kinetic":
        value = _coefficient(-1, 2, G=1)
    elif family == "Omega_potential":
        value = _coefficient(-1)
    elif family == "P_kinetic":
        value = _coefficient(-1, 2, Z=1)
    elif family == "full_V4":
        value = _coefficient(-1, 1, Z=1, M=2)
    elif family == "BF":
        value = _coefficient(1)
    elif family == "wall":
        value = _coefficient(-1)
    elif family == "K_foliation":
        value = _coefficient(1, 2, Mb=2)
    elif family == "R":
        value = _coefficient(1, 2, Mb=2, xi=1)
    elif family == "R_squared":
        denominator = 16 if mutation == "R_squared_denominator_16" else 32
        value = _coefficient(-1, denominator, Mb=2, B4_bar=1, k_infinity=-2)
    elif family == "a_squared":
        value = _coefficient(1, 2, Mb=2, eta=1)
    elif family == "Robin":
        value = _coefficient(-1, 2, kappa_hat=1)
    else:  # pragma: no cover - _component_family is exhaustive
        raise NaturalityCertificateError(f"unknown Green component: {component}")
    if mutation == "GHY_wrong_sign" and family == "GHY":
        value = value.negate()
    if mutation == f"intrinsic_wrong_sign_{family}" and family in INTERFACE_SECTORS:
        value = value.negate()
    return value


def _expected_green_component_weight(component: str) -> ExactCoefficient:
    """Independent target table for the exact v5.2 action coefficients."""

    family = _component_family(component)
    target = {
        "EH": (1, 2, (("M5", 3),)),
        "GHY": (1, 1, (("M5", 3),)),
        "Omega_kinetic": (-1, 2, (("G", 1),)),
        "Omega_potential": (-1, 1, ()),
        "P_kinetic": (-1, 2, (("Z", 1),)),
        "full_V4": (-1, 1, (("M", 2), ("Z", 1))),
        "BF": (1, 1, ()),
        "wall": (-1, 1, ()),
        "K_foliation": (1, 2, (("Mb", 2),)),
        "R": (1, 2, (("Mb", 2), ("xi", 1))),
        "R_squared": (
            -1,
            32,
            (("B4_bar", 1), ("Mb", 2), ("k_infinity", -2)),
        ),
        "a_squared": (1, 2, (("Mb", 2), ("eta", 1))),
        "Robin": (-1, 2, (("kappa_hat", 1),)),
    }[family]
    return ExactCoefficient.from_parts(*target)


def _green_leaf_multiset(value: Expression) -> tuple[tuple[str, int], ...]:
    counts: dict[str, int] = {}

    def visit(node: Expression) -> None:
        if isinstance(node, PulledField):
            role = _field_role(node.name)
            counts[role] = counts.get(role, 0) + 1
            return
        if isinstance(node, SolderedMatter):
            counts[node.name] = counts.get(node.name, 0) + 1
            return
        for argument in node.arguments:
            visit(argument)

    visit(value)
    return tuple(sorted(counts.items()))


def _full_expression_fingerprint_payload(value: Expression) -> tuple[Any, ...]:
    type_payload = _type_signature(value.type_tag)
    if isinstance(value, PulledField):
        return (
            "PulledField",
            value.name,
            type_payload,
            value.pullback_factors,
        )
    if isinstance(value, SolderedMatter):
        return (
            "SolderedMatter",
            value.name,
            type_payload,
            value.pullback_factors,
            value.groupoid_factors,
        )
    return (
        "Construction",
        value.operator,
        type_payload,
        tuple(
            _full_expression_fingerprint_payload(argument)
            for argument in value.arguments
        ),
    )


def _full_expression_fingerprint(value: Expression) -> str:
    return _canonical_sha256(_full_expression_fingerprint_payload(value))


def _infer_green_component_family(value: Expression) -> str | None:
    signature = _expression_signature(value)
    matches = tuple(
        family
        for family, expected in EXPECTED_SEMANTIC_SIGNATURES.items()
        if signature == expected
    )
    return matches[0] if len(matches) == 1 else None


def _infer_green_component_side(
    value: Expression,
    family: str,
) -> str | None:
    if family in INTERFACE_SECTORS:
        return "interface"
    sides: set[str] = set()

    def visit(node: Expression) -> None:
        if isinstance(node, PulledField):
            for side in SIDES:
                if node.name.endswith(f"_{side}"):
                    sides.add(side)
            return
        if isinstance(node, SolderedMatter):
            return
        for argument in node.arguments:
            visit(argument)

    visit(value)
    return next(iter(sides)) if len(sides) == 1 else None


def _green_row_name_from_AST_classification(family: str, side: str) -> str | None:
    if family in {"EH", "GHY"} and side in SIDES:
        return f"EH_GHY_{side}"
    if family in BULK_SECTORS and side in SIDES:
        return f"{family}_{side}"
    if family in INTERFACE_SECTORS and side == "interface":
        return family
    return None


def _derive_green_candidate_layout_from_AST(
    components: Mapping[str, Expression],
    *,
    mutation: str | None = None,
) -> tuple[
    tuple[tuple[str, tuple[str, ...]], ...],
    tuple[dict[str, Any], ...],
    tuple[str, ...],
]:
    grouped: dict[str, list[str]] = {}
    classifications: list[dict[str, Any]] = []
    issues: list[str] = []
    for component, expression in components.items():
        family = _infer_green_component_family(expression)
        side = (
            _infer_green_component_side(expression, family)
            if family is not None
            else None
        )
        row_name = (
            _green_row_name_from_AST_classification(family, side)
            if family is not None and side is not None
            else None
        )
        classifications.append(
            {
                "component": component,
                "inferred_family": family,
                "inferred_side": side,
                "inferred_row": row_name,
            }
        )
        if row_name is None:
            issues.append(f"unclassified:{component}")
            continue
        grouped.setdefault(row_name, []).append(component)
    if mutation == "component_duplicated" and "Robin" in grouped:
        grouped["Robin"].append("Robin")
    if mutation == "shared_layout_swap":
        left = "Omega_kinetic_plus"
        right = "Omega_potential_plus"
        grouped[left], grouped[right] = grouped.get(right, []), grouped.get(left, [])
    return (
        tuple((name, tuple(component_names)) for name, component_names in grouped.items()),
        tuple(classifications),
        tuple(issues),
    )


def _append_AST_ghost_to_first_pullback(value: Expression) -> Expression:
    changed = False

    def mutate(node: Expression) -> Expression:
        nonlocal changed
        if isinstance(node, PulledField):
            if changed:
                return node
            changed = True
            return PulledField(
                node.name,
                node.type_tag,
                node.pullback_factors + ("AST_GHOST",),
            )
        if isinstance(node, SolderedMatter):
            if changed:
                return node
            changed = True
            return SolderedMatter(
                node.name,
                node.type_tag,
                node.pullback_factors + ("AST_GHOST",),
                node.groupoid_factors,
            )
        return Construction(
            node.operator,
            tuple(mutate(argument) for argument in node.arguments),
            node.type_tag,
        )

    return mutate(value)


def _bulk_euler_pairing(row_name: str) -> str:
    family = row_name.rsplit("_", 1)[0]
    if family == "EH_GHY":
        return "M5^3/2*sqrt(-g)*G_MN*Delta_g^(MN) [geometric axiom]"
    if family == "Omega_kinetic":
        return "sqrt(-g)*G*box(Omega)*Delta_Omega + algebraic metric Euler pairing"
    if family == "Omega_potential":
        return "-sqrt(-g)*U'(Omega)*Delta_Omega + algebraic metric Euler pairing"
    if family == "P_kinetic":
        return "formal Euler pairings E_g,E_A,E_phi,E_Omega after exact product rule and IBP"
    if family == "full_V4":
        return "formal algebraic Euler pairings E_g,E_phi,E_Omega; no derivative variation"
    if family == "BF":
        return "<Delta_B wedge F[A]>+<D_A B wedge Delta_A>"
    return "intrinsic four-dimensional variation retained as exact unexpanded delta"


def _independent_green_row_metadata_target(
    row_name: str,
) -> tuple[str, str, str | None, str | None]:
    side = row_name.rsplit("_", 1)[-1]
    family = row_name.rsplit("_", 1)[0]
    if row_name.startswith("EH_GHY_"):
        return (
            "explicit_geometric_EH_plus_GHY_axiom",
            "M5^3/2*sqrt(-g)*G_MN*Delta_g^(MN) [geometric axiom]",
            f"d_5(theta_EH_GHY_{side})",
            None,
        )
    if family == "Omega_kinetic":
        return (
            "exact_symbolic_product_rule_and_IBP",
            "sqrt(-g)*G*box(Omega)*Delta_Omega + algebraic metric Euler pairing",
            f"d_5(theta_Omega_kinetic_{side})",
            None,
        )
    if family == "Omega_potential":
        return (
            "algebraic_density_no_boundary_current",
            "-sqrt(-g)*U'(Omega)*Delta_Omega + algebraic metric Euler pairing",
            f"d_5(theta_Omega_potential_{side}=0)",
            None,
        )
    if family == "P_kinetic":
        return (
            "exact_symbolic_product_rule_and_IBP",
            "formal Euler pairings E_g,E_A,E_phi,E_Omega after exact product rule and IBP",
            f"d_5(theta_P_kinetic_{side})",
            None,
        )
    if family == "full_V4":
        return (
            "algebraic_density_no_boundary_current",
            "formal algebraic Euler pairings E_g,E_phi,E_Omega; no derivative variation",
            f"d_5(theta_full_V4_{side}=0)",
            None,
        )
    if family == "BF":
        return (
            "reused_oriented_BF_incidence_prerequisite",
            "<Delta_B wedge F[A]>+<D_A B wedge Delta_A>",
            f"-d_5(<B_{side} wedge Delta_A_{side}>)",
            None,
        )
    if row_name in INTERFACE_SECTORS:
        return (
            "exact_unexpanded_intrinsic_delta_axiom",
            "intrinsic four-dimensional variation retained as exact unexpanded delta",
            None,
            EXPECTED_INTRINSIC_DELTAS[row_name],
        )
    return ("invalid_row", "invalid_row", "invalid_row", "invalid_row")


def _delta_p_product_rule_program(
    mutation: str | None = None,
) -> tuple[DeltaPVariationTerm, ...]:
    terms = [
        DeltaPVariationTerm(
            "covariant_Delta_phi",
            "covariant_derivative",
            ("Delta_phi",),
            "Delta_phi",
            True,
            _coefficient(1),
            "phi_normal_current",
        ),
        DeltaPVariationTerm(
            "conformal_Delta_phi_dOmega",
            "product",
            ("Delta_phi", "dOmega"),
            "Delta_phi",
            False,
            _coefficient(3, 2, Omega=-1),
            None,
        ),
        DeltaPVariationTerm(
            "conformal_phi_dDeltaOmega",
            "product",
            ("phi", "d_Delta_Omega"),
            "Delta_Omega",
            True,
            _coefficient(3, 2, Omega=-1),
            "Omega_normal_current",
        ),
        DeltaPVariationTerm(
            "conformal_log_variation",
            "product",
            ("phi", "dOmega", "Delta_Omega"),
            "Delta_Omega",
            False,
            _coefficient(-3, 2, Omega=-2),
            None,
        ),
        DeltaPVariationTerm(
            "connection_representation",
            "representation",
            ("Delta_A", "phi"),
            "Delta_A",
            False,
            _coefficient(1),
            None,
        ),
    ]
    by_id = {term.term_id: index for index, term in enumerate(terms)}

    def replace_term(term_id: str, **changes: Any) -> None:
        index = by_id[term_id]
        old = terms[index]
        values = {
            "term_id": old.term_id,
            "operator": old.operator,
            "factors": old.factors,
            "variation": old.variation,
            "differentiated_variation": old.differentiated_variation,
            "coefficient": old.coefficient,
            "boundary_channel": old.boundary_channel,
        }
        values.update(changes)
        terms[index] = DeltaPVariationTerm(**values)

    if mutation == "P_three_halves_omitted":
        replace_term("conformal_phi_dDeltaOmega", coefficient=_coefficient(0))
    elif mutation == "P_three_halves_wrong":
        replace_term(
            "conformal_phi_dDeltaOmega",
            coefficient=_coefficient(1, 1, Omega=-1),
        )
    elif mutation == "DeltaP_omit_Delta_phi_dOmega":
        terms.pop(by_id["conformal_Delta_phi_dOmega"])
    elif mutation == "DeltaP_corrupt_Delta_phi_dOmega":
        replace_term(
            "conformal_Delta_phi_dOmega",
            coefficient=_coefficient(1, 2, Omega=-1),
        )
    elif mutation == "DeltaP_omit_Omega_minus2":
        terms.pop(by_id["conformal_log_variation"])
    elif mutation == "DeltaP_corrupt_Omega_minus2":
        replace_term(
            "conformal_log_variation",
            coefficient=_coefficient(-3, 2, Omega=-1),
        )
    elif mutation == "DeltaP_omit_representation_DeltaA_phi":
        terms.pop(by_id["connection_representation"])
    elif mutation == "DeltaP_corrupt_representation_DeltaA_phi":
        replace_term(
            "connection_representation",
            operator="detached_representation",
        )
    return tuple(terms)


def _rename_coefficient_power(
    value: ExactCoefficient,
    source: str,
    target: str,
) -> ExactCoefficient:
    return ExactCoefficient.from_parts(
        value.numerator,
        value.denominator,
        tuple((target if name == source else name, power) for name, power in value.powers),
    )


def _bf_bulk_variation_normalizer(
    side: str,
    mutation: str | None = None,
) -> dict[str, Any]:
    if side not in SIDES:
        raise NaturalityCertificateError(f"unknown BF Green side: {side}")
    d_ab_coefficient = _coefficient(1)
    if mutation == "BF_wrong_bulk_DAB_sign":
        d_ab_coefficient = _coefficient(-1)
    elif mutation == "BF_omit_DAB":
        d_ab_coefficient = _coefficient(0)
    local_boundary_coefficient = _coefficient(-1)
    if mutation == "BF_internal_boundary_minus_to_plus":
        local_boundary_coefficient = _coefficient(1)
    bulk_terms = _collect_green_terms(
        (
            ExactGreenTerm(
                f"F[A_{side}]", f"Delta_B_{side}", _coefficient(1)
            ),
            ExactGreenTerm(
                f"D_A_{side} B_{side}",
                f"Delta_A_{side}",
                d_ab_coefficient,
            ),
        )
    )
    expected_bulk_terms = _independent_expected_BF_bulk_terms(side)
    expected_local_boundary = ExactGreenTerm(
        f"<B_{side} wedge Delta_A_{side}>",
        "d_5",
        _coefficient(-1),
    )
    local_boundary = ExactGreenTerm(
        expected_local_boundary.factor,
        expected_local_boundary.variation,
        local_boundary_coefficient,
    )
    return {
        "side": side,
        "graded_product_rule": (
            "delta<B wedge F[A]>=<Delta_B wedge F[A]>+"
            "<D_A B wedge Delta_A>-d<B wedge Delta_A> for deg(B)=3"
        ),
        "B_form_degree": 3,
        "derived_bulk_euler_terms": _serialize_green_terms(bulk_terms),
        "independent_expected_bulk_euler_terms": _serialize_green_terms(
            expected_bulk_terms
        ),
        "derived_local_boundary_divergence_term": _serialize_green_terms(
            (local_boundary,)
        ),
        "independent_expected_local_boundary_divergence_term": (
            _serialize_green_terms((expected_local_boundary,))
        ),
        "pass": bool(
            bulk_terms == expected_bulk_terms
            and local_boundary == expected_local_boundary
        ),
        "_bulk_terms": bulk_terms,
        "_local_boundary_coefficient": local_boundary_coefficient,
    }


def _kinetic_boundary_current_normalizer(
    side: str,
    mutation: str | None = None,
) -> dict[str, Any]:
    if side not in SIDES:
        raise NaturalityCertificateError(f"unknown Green normalizer side: {side}")
    omega_action_weight = _green_component_weight(
        f"Omega_kinetic_bulk_{side}"
    )
    p_action_weight = _green_component_weight(f"P_kinetic_bulk_{side}")
    quadratic_first_variation = _coefficient(2)
    omega_gradient_coefficient = omega_action_weight.multiply(
        quadratic_first_variation
    )
    p_pairing_coefficient = p_action_weight.multiply(quadratic_first_variation)
    delta_p_program = _delta_p_product_rule_program(mutation)
    observed_program_signatures = tuple(
        _delta_p_term_signature(term) for term in delta_p_program
    )
    program_exact = observed_program_signatures == EXPECTED_DELTA_P_TERM_SIGNATURES

    omega_variation = "Delta_Omega_Sigma"
    phi_variation = "Delta_varphi_H"
    if mutation == "split_common_variations":
        omega_variation = f"Delta_Omega_{side}"
        phi_variation = f"Delta_varphi_{side}"

    omega_from_kinetic = ExactGreenTerm(
        f"sqrt(-gamma)*n_{side}.nabla_Omega_{side}",
        omega_variation,
        omega_gradient_coefficient,
    )
    phi_factor = f"sqrt(-gamma)*j_{side}(n_{side}.P_{side})"
    if mutation == "Pi_phi_detached":
        phi_factor = f"sqrt(-gamma)*j_detached(n_{side}.P_{side})"
    elif mutation == "Pi_phi_unsoldered":
        phi_factor = f"sqrt(-gamma)*n_{side}.P_{side}"
        phi_variation = f"Delta_phi_trace_{side}"
    p_boundary_terms: list[ExactGreenTerm] = []
    p_bulk_remainder_terms: list[ExactGreenTerm] = []
    consumed_term_ids: list[str] = []
    for term in delta_p_program:
        consumed_term_ids.append(term.term_id)
        if term.boundary_channel == "phi_normal_current":
            p_boundary_terms.append(
                ExactGreenTerm(
                    phi_factor,
                    phi_variation,
                    p_pairing_coefficient.multiply(term.coefficient),
                )
            )
        elif term.boundary_channel == "Omega_normal_current":
            boundary_coefficient = _rename_coefficient_power(
                term.coefficient, "Omega", "Omega_Sigma"
            )
            p_boundary_terms.append(
                ExactGreenTerm(
                    f"sqrt(-gamma)*<phi_{side},n_{side}.P_{side}>",
                    omega_variation,
                    p_pairing_coefficient.multiply(boundary_coefficient),
                )
            )
        else:
            p_bulk_remainder_terms.append(
                ExactGreenTerm(
                    f"{term.operator}({','.join(term.factors)})",
                    term.variation,
                    p_pairing_coefficient.multiply(term.coefficient),
                )
            )
    p_boundary_terms = list(_collect_green_terms(p_boundary_terms))
    omega_from_p = next(
        (
            term
            for term in p_boundary_terms
            if "<phi_" in term.factor
        ),
        ExactGreenTerm(
            f"sqrt(-gamma)*<phi_{side},n_{side}.P_{side}>",
            omega_variation,
            _coefficient(0),
        ),
    )
    phi_from_p = next(
        (
            term
            for term in p_boundary_terms
            if term is not omega_from_p
        ),
        ExactGreenTerm(phi_factor, phi_variation, _coefficient(0)),
    )
    if mutation == "Pi_Omega_kinetic_wrong_sign":
        omega_from_kinetic = ExactGreenTerm(
            omega_from_kinetic.factor,
            omega_from_kinetic.variation,
            omega_from_kinetic.coefficient.negate(),
        )
    elif mutation == "Pi_Omega_P_wrong_sign":
        omega_from_p = ExactGreenTerm(
            omega_from_p.factor,
            omega_from_p.variation,
            omega_from_p.coefficient.negate(),
        )
    elif mutation == "Pi_phi_wrong_sign":
        phi_from_p = ExactGreenTerm(
            phi_from_p.factor,
            phi_from_p.variation,
            phi_from_p.coefficient.negate(),
        )

    boundary_terms = _collect_green_terms(
        (omega_from_kinetic, omega_from_p, phi_from_p)
    )
    expected_side_terms = _collect_green_terms(
        (
            ExactGreenTerm(
                f"sqrt(-gamma)*n_{side}.nabla_Omega_{side}",
                "Delta_Omega_Sigma",
                _coefficient(-1, 1, G=1),
            ),
            ExactGreenTerm(
                f"sqrt(-gamma)*<phi_{side},n_{side}.P_{side}>",
                "Delta_Omega_Sigma",
                _coefficient(-3, 2, Z=1, Omega_Sigma=-1),
            ),
            ExactGreenTerm(
                f"sqrt(-gamma)*j_{side}(n_{side}.P_{side})",
                "Delta_varphi_H",
                _coefficient(-1, 1, Z=1),
            ),
        )
    )
    positive_momenta = _collect_green_terms(
        tuple(
            ExactGreenTerm(term.factor, term.variation, term.coefficient.negate())
            for term in boundary_terms
        )
    )
    expected_program_ids = tuple(row[0] for row in EXPECTED_DELTA_P_TERM_SIGNATURES)
    all_program_terms_consumed_once = bool(
        tuple(consumed_term_ids) == tuple(term.term_id for term in delta_p_program)
        and len(consumed_term_ids) == len(set(consumed_term_ids))
        and tuple(consumed_term_ids) == expected_program_ids
    )
    conformal_current_term = next(
        (
            term
            for term in delta_p_program
            if term.term_id == "conformal_phi_dDeltaOmega"
        ),
        None,
    )
    conformal_product_coefficient = (
        _rename_coefficient_power(
            conformal_current_term.coefficient, "Omega", "Omega_Sigma"
        )
        if conformal_current_term is not None
        else _coefficient(0)
    )
    exact = bool(
        boundary_terms == expected_side_terms
        and program_exact
        and all_program_terms_consumed_once
    )
    return {
        "side": side,
        "source_action_weights": {
            "Omega_kinetic": _serialize_coefficient(omega_action_weight),
            "P_kinetic": _serialize_coefficient(p_action_weight),
        },
        "quadratic_first_variation_multiplicity": 2,
        "Delta_P_product_rule": _serialize_delta_p_terms(delta_p_program),
        "observed_Delta_P_term_signatures": observed_program_signatures,
        "independent_expected_Delta_P_term_signatures": (
            EXPECTED_DELTA_P_TERM_SIGNATURES
        ),
        "Delta_P_program_matches_independent_target": program_exact,
        "Delta_P_consumed_term_ids": consumed_term_ids,
        "Delta_P_all_five_terms_consumed_once": all_program_terms_consumed_once,
        "Delta_P_bulk_remainder_terms_after_current_extraction": (
            _serialize_green_terms(_collect_green_terms(p_bulk_remainder_terms))
        ),
        "independent_normalization_steps": [
            "differentiate the two quadratic kinetic densities",
            "expand Delta_P by the displayed product rule",
            "integrate only d(Delta_Omega) and D_A(Delta_phi) by parts",
            "restrict normal currents to the fixed reference interface",
            "apply the common scalar trace and j_epsilon matter trace",
        ],
        "raw_Omega_gradient_coefficient": _serialize_coefficient(
            omega_gradient_coefficient
        ),
        "raw_P_pairing_coefficient": _serialize_coefficient(
            p_pairing_coefficient
        ),
        "conformal_product_coefficient": _serialize_coefficient(
            conformal_product_coefficient
        ),
        "derived_integrated_boundary_terms": _serialize_green_terms(boundary_terms),
        "independent_expected_boundary_terms": _serialize_green_terms(
            expected_side_terms
        ),
        "derived_positive_momenta": _serialize_green_terms(positive_momenta),
        "Pi_Omega_formula": (
            f"G*n_{side}.nabla_Omega_{side}+3*Z*<phi_{side},n_{side}.P_{side}>/"
            "(2*Omega_Sigma)"
        ),
        "Pi_phi_formula": f"Z*j_{side}(n_{side}.P_{side})",
        "pass": exact,
        "_terms": boundary_terms,
    }


def _expected_green_boundary_terms() -> tuple[ExactGreenTerm, ...]:
    terms: list[ExactGreenTerm] = []
    for side in SIDES:
        terms.extend(
            (
                ExactGreenTerm(
                    f"sqrt(-gamma)*pi_{side}^(mu nu)",
                    "Delta_gamma_mu_nu",
                    _coefficient(-1, 2, M5=3),
                ),
                ExactGreenTerm(
                    f"sqrt(-gamma)*n_{side}.nabla_Omega_{side}",
                    "Delta_Omega_Sigma",
                    _coefficient(-1, 1, G=1),
                ),
                ExactGreenTerm(
                    f"sqrt(-gamma)*<phi_{side},n_{side}.P_{side}>",
                    "Delta_Omega_Sigma",
                    _coefficient(-3, 2, Z=1, Omega_Sigma=-1),
                ),
                ExactGreenTerm(
                    f"sqrt(-gamma)*j_{side}(n_{side}.P_{side})",
                    "Delta_varphi_H",
                    _coefficient(-1, 1, Z=1),
                ),
            )
        )
    terms.extend(
        (
            ExactGreenTerm(
                "b_plus_wedge", "Delta_A_Sigma", _coefficient(-1)
            ),
            ExactGreenTerm(
                "b_minus_wedge", "Delta_A_Sigma", _coefficient(1)
            ),
        )
    )
    return _collect_green_terms(terms)


def _green_literal_contract(v52: Mapping[str, Any]) -> dict[str, Any]:
    charter = v52.get("exact_classical_charter", {})
    action = charter.get("exact_action", {})
    interface = charter.get("interface_domain", {})
    green = v52.get("Green_form_certificate", {})
    observed = {
        "total": action.get("total"),
        "superpotential": action.get("superpotential"),
        "bulk_potential": action.get("bulk_potential"),
        "full_V4": action.get("full_V4"),
        "bulk_gauged": action.get("bulk_gauged"),
        "gauged_conformal_derivative": action.get("gauged_conformal_derivative"),
        "GHY": action.get("GHY"),
        "wall_background": action.get("wall_background"),
        "foliation_lower": action.get("foliation_lower"),
        "Robin_intrinsic": action.get("Robin_intrinsic"),
        "BF": action.get("BF"),
        "removed_terms": action.get("removed_terms"),
        "common_interface_variations": (
            tuple(interface.get("variations", ()))[0]
            if interface.get("variations")
            else None
        ),
        "Green_form": green.get("Green_form"),
        "EH_plus_GHY_first_variation": green.get(
            "EH_plus_GHY_first_variation"
        ),
        "momenta": green.get("momenta"),
        "BF_bulk_equation_A": green.get("bulk_equations_new_sector", {}).get(
            "A"
        ),
        "compact_support_at_bulk_infinity": green.get(
            "compact_support_at_bulk_infinity"
        ),
        "Sigma_has_no_boundary": green.get("Sigma_has_no_boundary"),
        "GHY_removes_normal_metric_variation": green.get(
            "GHY_removes_normal_metric_variation"
        ),
        "intrinsic_Sigma_integrations_have_no_corner_terms": green.get(
            "intrinsic_Sigma_integrations_have_no_corner_terms"
        ),
    }
    expected = {
        "total": EXPECTED_TOTAL_ACTION,
        "superpotential": (
            "W(Omega)=3*M5^3*k_infinity*exp[-G*Omega^2/(6*M5^3)]"
        ),
        "bulk_potential": "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
        "full_V4": "V4(r)=r^4/(2*sqrt(1+r^4))",
        "bulk_gauged": (
            "S_bulk_gauged=sum_eps int_Meps sqrt(-g_eps)*[M5^3*R_eps/2-"
            "G*(nabla Omega_eps)^2/2-U(Omega_eps)-"
            "Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2-"
            "Z5*M^2*Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)]"
        ),
        "gauged_conformal_derivative": (
            "P_eps_M=D_(A_eps,M)phi_eps+3*phi_eps*partial_M log(Omega_eps)/2"
        ),
        "GHY": (
            "S_GHY=M5^3*sum_eps int_Sigma sqrt(-gamma)*Theta_eps for outward normals"
        ),
        "wall_background": (
            "S_wall0=-int_Sigma sqrt(-gamma)*[2*W(Omega_Sigma)+"
            "beta*(Omega_Sigma-1)^2/2]"
        ),
        "foliation_lower": (
            "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-"
            "lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
            "B4_bar*Rcal^2/(16*k_infinity^2)]"
        ),
        "Robin_intrinsic": (
            "S_R_intrinsic=-kappa_hat/2*int_Sigma sqrt(-gamma)*"
            "h_mu_nu*(varphi_H^mu-y*a^mu)*(varphi_H^nu-y*a^nu)"
        ),
        "BF": EXPECTED_BF_ACTION_LITERAL,
        "removed_terms": EXPECTED_REMOVED_TERMS,
        "common_interface_variations": EXPECTED_COMMON_INTERFACE_VARIATIONS,
        "Green_form": EXPECTED_BF_GREEN_FORM,
        "EH_plus_GHY_first_variation": EXPECTED_EH_GHY_FIRST_VARIATION,
        "momenta": EXPECTED_GREEN_MOMENTA,
        "BF_bulk_equation_A": EXPECTED_BF_BULK_EQUATION_A,
        "compact_support_at_bulk_infinity": True,
        "Sigma_has_no_boundary": True,
        "GHY_removes_normal_metric_variation": True,
        "intrinsic_Sigma_integrations_have_no_corner_terms": True,
    }
    return {
        "observed": observed,
        "expected": expected,
        "all_literal_and_geometric_axiom_pins_exact": observed == expected,
        "Green_form_text_used_as_proof_target": False,
    }


def _intrinsic_delta_name(component: str) -> str:
    return {
        "wall": "delta(S_wall0)",
        "K_foliation": "delta(S_K_foliation)",
        "R": "delta(S_R)",
        "R_squared": "delta(S_R_squared)",
        "a_squared": "delta(S_a_squared)",
        "Robin": "delta(S_R_intrinsic)",
    }[component]


def _independent_expected_component_classification(
    component: str,
) -> tuple[str, str] | None:
    containing_rows = tuple(
        row_name
        for row_name, components in EXPECTED_GREEN_ROW_LAYOUT
        if component in components
    )
    if len(containing_rows) != 1 or component not in COMPONENT_NAMES:
        return None
    row_name = containing_rows[0]
    _row_family, row_side = EXPECTED_GREEN_ROW_FAMILY_SIDE[row_name]
    return _component_family(component), row_side


def _independent_expected_BF_bulk_terms(
    side: str,
) -> tuple[ExactGreenTerm, ...]:
    if side not in SIDES:
        raise NaturalityCertificateError(f"unknown expected BF side: {side}")
    return _collect_green_terms(
        (
            ExactGreenTerm(
                f"F[A_{side}]", f"Delta_B_{side}", _coefficient(1)
            ),
            ExactGreenTerm(
                f"D_A_{side} B_{side}",
                f"Delta_A_{side}",
                _coefficient(1),
            ),
        )
    )


def _literal_green_ledger(
    v52: Mapping[str, Any],
    *,
    components: Mapping[str, Expression] | None = None,
    bf_incidence_aggregation: Mapping[str, Any] | None = None,
    mutation: str | None = None,
) -> dict[str, Any]:
    if mutation is not None and mutation not in GREEN_LEDGER_MUTATIONS:
        raise NaturalityCertificateError(f"unknown Green-ledger mutation: {mutation}")
    actual_components = dict(
        build_component_expressions("baseline")
        if components is None
        else components
    )
    if mutation == "component_swapped":
        left = "Omega_kinetic_bulk_plus"
        right = "Omega_potential_bulk_plus"
        actual_components[left], actual_components[right] = (
            actual_components[right],
            actual_components[left],
        )
    elif mutation == "component_detached":
        name = "P_kinetic_bulk_plus"
        actual_components[name] = _replace_semantic_leaf_role(
            actual_components[name], "phi", "detached_phi"
        )
    elif mutation == "component_omitted":
        actual_components.pop("Robin", None)
    elif mutation == "GHY_omitted":
        actual_components.pop("GHY_plus", None)
    elif mutation == "extra_component":
        actual_components["EXTRA_COMPONENT"] = actual_components["wall"]
    elif mutation == "AST_GHOST_pullback":
        name = "EH_bulk_plus"
        actual_components[name] = _append_AST_ghost_to_first_pullback(
            actual_components[name]
        )
    for intrinsic in INTERFACE_SECTORS:
        if mutation == f"intrinsic_omitted_{intrinsic}":
            actual_components.pop(intrinsic, None)

    actual_bf = (
        _bf_incidence_aggregation_ledger(v52, components=actual_components)
        if bf_incidence_aggregation is None
        else bf_incidence_aggregation
    )
    normalizers = {
        side: _kinetic_boundary_current_normalizer(side, mutation) for side in SIDES
    }
    bf_normalizers = {
        side: _bf_bulk_variation_normalizer(side, mutation) for side in SIDES
    }
    layout, AST_classifications, AST_classification_issues = (
        _derive_green_candidate_layout_from_AST(
            actual_components,
            mutation=mutation,
        )
    )

    bindings_by_component = {
        binding.name: binding for binding in literal_component_bindings()
    }
    rows: list[VariationRow] = []
    for row_name, component_names in layout:
        expressions = tuple(
            (name, actual_components[name])
            for name in component_names
            if name in actual_components
        )
        weights = tuple(
            (
                name,
                _green_component_weight(name, mutation)
                if name in COMPONENT_NAMES
                else _coefficient(0),
            )
            for name in component_names
        )
        source_keys = tuple(
            sorted(
                {
                    key
                    for name in component_names
                    for key in (
                        bindings_by_component[name].source_keys
                        if name in bindings_by_component
                        else ()
                    )
                }
            )
        )
        family, side = EXPECTED_GREEN_ROW_FAMILY_SIDE.get(
            row_name, ("invalid", "invalid")
        )
        boundary_terms: tuple[ExactGreenTerm, ...] = ()
        bulk_euler_terms: tuple[ExactGreenTerm, ...] = ()
        intrinsic_delta: str | None = None
        local_divergence: str | None = None
        if row_name.startswith("EH_GHY_"):
            derivation_kind = "explicit_geometric_EH_plus_GHY_axiom"
            factor = f"sqrt(-gamma)*pi_{side}^(mu nu)"
            if mutation == "GHY_inward_normal" and side == "plus":
                factor = f"sqrt(-gamma)*pi_inward_{side}^(mu nu)"
            boundary_terms = (
                ExactGreenTerm(
                    factor,
                    "Delta_gamma_mu_nu",
                    _coefficient(-1, 2, M5=3),
                ),
            )
            local_divergence = f"d_5(theta_EH_GHY_{side})"
        elif family in {"Omega_kinetic", "P_kinetic"}:
            derivation_kind = "exact_symbolic_product_rule_and_IBP"
            normalized_terms = normalizers[side]["_terms"]
            if family == "Omega_kinetic":
                boundary_terms = tuple(
                    term
                    for term in normalized_terms
                    if "nabla_Omega" in term.factor
                )
            else:
                boundary_terms = tuple(
                    term
                    for term in normalized_terms
                    if "nabla_Omega" not in term.factor
                )
            local_divergence = f"d_5(theta_{family}_{side})"
        elif family in {"Omega_potential", "full_V4"}:
            derivation_kind = "algebraic_density_no_boundary_current"
            if (
                mutation == "spurious_Omega_potential_current"
                and family == "Omega_potential"
                and side == "plus"
            ) or (
                mutation == "spurious_V4_current"
                and family == "full_V4"
                and side == "plus"
            ):
                boundary_terms = (
                    ExactGreenTerm(
                        f"spurious_{family}_normal_current",
                        "Delta_Omega_Sigma",
                        _coefficient(1),
                    ),
                )
            local_divergence = f"d_5(theta_{family}_{side}=0)"
        elif family == "BF":
            derivation_kind = "reused_oriented_BF_incidence_prerequisite"
            bf_normalizer = bf_normalizers[side]
            bulk_euler_terms = bf_normalizer["_bulk_terms"]
            orientation = _coefficient(BF_ORIENTATION_SIGNS[side])
            coefficient = bf_normalizer["_local_boundary_coefficient"].multiply(
                orientation
            )
            if mutation == "BF_offshell_cancelled":
                coefficient = _coefficient(0)
            boundary_terms = _collect_green_terms(
                (
                    ExactGreenTerm(
                        f"b_{side}_wedge", "Delta_A_Sigma", coefficient
                    ),
                )
            )
            local_sign = bf_normalizer["_local_boundary_coefficient"].numerator
            local_divergence = (
                f"-d_5(<B_{side} wedge Delta_A_{side}>)"
                if local_sign == -1
                else f"+d_5(<B_{side} wedge Delta_A_{side}>)"
            )
        else:
            derivation_kind = "exact_unexpanded_intrinsic_delta_axiom"
            intrinsic_delta = _intrinsic_delta_name(row_name)
            if mutation == "intrinsic_producer_corruption" and row_name == "R":
                intrinsic_delta = "delta(S_WRONG_R)"

        if mutation == "local_divergence_omitted" and row_name == "P_kinetic_plus":
            local_divergence = None
        rows.append(
            VariationRow(
                name=row_name,
                components=tuple(component_names),
                component_expressions=expressions,
                component_weights=weights,
                source_literal_keys=source_keys,
                derivation_kind=derivation_kind,
                bulk_euler_pairing=_bulk_euler_pairing(row_name),
                bulk_euler_terms=bulk_euler_terms,
                local_divergence=local_divergence,
                integrated_boundary_terms=_collect_green_terms(boundary_terms),
                intrinsic_delta=intrinsic_delta,
            )
        )
    expected_layout = EXPECTED_GREEN_ROW_LAYOUT
    observed_layout = tuple((row.name, row.components) for row in rows)
    actual_component_keys = tuple(actual_components)
    exact_component_key_set = bool(
        len(actual_component_keys) == len(COMPONENT_NAMES)
        and set(actual_component_keys) == set(COMPONENT_NAMES)
    )
    classification_by_component = {
        row["component"]: row for row in AST_classifications
    }
    component_counts: dict[str, int] = {}
    for row in rows:
        for component in row.components:
            component_counts[component] = component_counts.get(component, 0) + 1
    exact_component_multiset = component_counts == {
        component: 1 for component in COMPONENT_NAMES
    }
    literal_contract = _green_literal_contract(v52)
    row_reports: list[dict[str, Any]] = []
    for row in rows:
        component_reports: list[dict[str, Any]] = []
        for component, expression in row.component_expressions:
            expected_classification = _independent_expected_component_classification(
                component
            )
            expected_family = (
                expected_classification[0]
                if expected_classification is not None
                else None
            )
            expected_side = (
                expected_classification[1]
                if expected_classification is not None
                else None
            )
            observed_classification = classification_by_component.get(component, {})
            inferred_family = observed_classification.get("inferred_family")
            inferred_side = observed_classification.get("inferred_side")
            observed_fingerprint = _full_expression_fingerprint(expression)
            expected_fingerprint = EXPECTED_GREEN_EXPRESSION_FINGERPRINTS.get(
                component
            )
            full_fingerprint_match = observed_fingerprint == expected_fingerprint
            semantic_match = (
                expected_family is not None
                and _expression_signature(expression)
                == EXPECTED_SEMANTIC_SIGNATURES[expected_family]
            )
            leaf_multiset = _green_leaf_multiset(expression)
            expected_leaf_multiset = (
                EXPECTED_GREEN_LEAF_MULTISETS[expected_family]
                if expected_family is not None
                else ()
            )
            weight = dict(row.component_weights).get(component)
            expected_weight = (
                _expected_green_component_weight(component)
                if expected_classification is not None
                else None
            )
            family_and_side_match = bool(
                expected_classification is not None
                and inferred_family == expected_family
                and inferred_side == expected_side
            )
            component_reports.append(
                {
                    "component": component,
                    "typed_expression": _render_expression(expression),
                    "full_AST_fingerprint_payload": (
                        _full_expression_fingerprint_payload(expression)
                    ),
                    "observed_full_AST_fingerprint_sha256": observed_fingerprint,
                    "independent_expected_full_AST_fingerprint_sha256": (
                        expected_fingerprint
                    ),
                    "full_AST_fingerprint_exact": full_fingerprint_match,
                    "structurally_equal_to_real_component_expression": (
                        full_fingerprint_match
                    ),
                    "inferred_family_from_AST": inferred_family,
                    "independent_expected_family": expected_family,
                    "inferred_side_from_AST": inferred_side,
                    "independent_expected_side": expected_side,
                    "AST_family_and_side_match_independent_component_target": (
                        family_and_side_match
                    ),
                    "semantic_signature_exact": semantic_match,
                    "observed_leaf_multiset": [list(item) for item in leaf_multiset],
                    "expected_leaf_multiset": [
                        list(item) for item in expected_leaf_multiset
                    ],
                    "leaf_multiset_exact": leaf_multiset == expected_leaf_multiset,
                    "observed_weight": (
                        _serialize_coefficient(weight) if weight is not None else None
                    ),
                    "expected_weight": (
                        _serialize_coefficient(expected_weight)
                        if expected_weight is not None
                        else None
                    ),
                    "exact_symbolic_weight": weight == expected_weight,
                }
            )
        expected_row = dict(expected_layout).get(row.name)
        row_layout_exact = expected_row == row.components
        component_names_match_expressions = row.components == tuple(
            component for component, _expression in row.component_expressions
        )
        (
            expected_derivation_kind,
            expected_bulk_euler_pairing,
            expected_local_divergence,
            expected_intrinsic_delta,
        ) = _independent_green_row_metadata_target(row.name)
        local_divergence_exact = row.local_divergence == expected_local_divergence
        intrinsic_exact = row.intrinsic_delta == expected_intrinsic_delta
        derivation_kind_exact = row.derivation_kind == expected_derivation_kind
        bulk_euler_pairing_exact = (
            row.bulk_euler_pairing == expected_bulk_euler_pairing
        )
        expected_row_family, expected_row_side = EXPECTED_GREEN_ROW_FAMILY_SIDE.get(
            row.name, (None, None)
        )
        row_family_side_exact = bool(
            expected_row is not None
            and all(
                (
                    component["inferred_side_from_AST"] == expected_row_side
                    and (
                        component["inferred_family_from_AST"]
                        in ({"EH", "GHY"} if expected_row_family == "EH_GHY" else {expected_row_family})
                    )
                )
                for component in component_reports
            )
        )
        expected_bulk_euler_terms = (
            _independent_expected_BF_bulk_terms(expected_row_side)
            if expected_row_family == "BF" and expected_row_side in SIDES
            else ()
        )
        bulk_euler_terms_exact = row.bulk_euler_terms == expected_bulk_euler_terms
        row_pass = bool(
            row_layout_exact
            and component_names_match_expressions
            and row_family_side_exact
            and component_reports
            and all(
                component["structurally_equal_to_real_component_expression"]
                and component[
                    "AST_family_and_side_match_independent_component_target"
                ]
                and component["semantic_signature_exact"]
                and component["leaf_multiset_exact"]
                and component["exact_symbolic_weight"]
                for component in component_reports
            )
            and row.source_literal_keys
            and bulk_euler_pairing_exact
            and bulk_euler_terms_exact
            and local_divergence_exact
            and intrinsic_exact
            and derivation_kind_exact
        )
        row_reports.append(
            {
                "name": row.name,
                "components": list(row.components),
                "source_literal_keys": list(row.source_literal_keys),
                "derivation_kind": row.derivation_kind,
                "bulk_euler_pairing": row.bulk_euler_pairing,
                "independent_expected_bulk_euler_pairing": (
                    expected_bulk_euler_pairing
                ),
                "bulk_euler_pairing_exact": bulk_euler_pairing_exact,
                "bulk_euler_terms": _serialize_green_terms(row.bulk_euler_terms),
                "independent_expected_bulk_euler_terms": _serialize_green_terms(
                    expected_bulk_euler_terms
                ),
                "bulk_euler_terms_exact": bulk_euler_terms_exact,
                "local_divergence": row.local_divergence,
                "integrated_boundary_terms": _serialize_green_terms(
                    row.integrated_boundary_terms
                ),
                "intrinsic_delta": row.intrinsic_delta,
                "component_bindings": component_reports,
                "row_layout_exact": row_layout_exact,
                "component_names_match_expression_bindings": (
                    component_names_match_expressions
                ),
                "row_family_and_side_match_AST_classifications": (
                    row_family_side_exact
                ),
                "local_d5_divergence_recorded_exactly_for_bulk_row": (
                    local_divergence_exact
                ),
                "intrinsic_delta_exact_and_unexpanded": intrinsic_exact,
                "derivation_kind_matches_independent_target": derivation_kind_exact,
                "pass": row_pass,
            }
        )

    derived_boundary = _collect_green_terms(
        tuple(term for row in rows for term in row.integrated_boundary_terms)
    )
    expected_boundary = _expected_green_boundary_terms()
    intrinsic_rows = [row for row in rows if row.name in INTERFACE_SECTORS]
    intrinsic_exact = bool(
        len(intrinsic_rows) == len(INTERFACE_SECTORS)
        and tuple(row.name for row in intrinsic_rows) == INTERFACE_SECTORS
        and all(
            row.intrinsic_delta == EXPECTED_INTRINSIC_DELTAS[row.name]
            and dict(row.component_weights).get(row.name)
            == _expected_green_component_weight(row.name)
            for row in intrinsic_rows
        )
    )
    normalizer_pass = all(normalizers[side]["pass"] for side in SIDES)
    bf_bulk_normalizer_pass = all(
        bf_normalizers[side]["pass"] for side in SIDES
    )
    bf_reused_exactly = bool(
        actual_bf.get("pass") is True
        and actual_bf.get("off_shell_oriented_flux_is_nonzero") is True
        and actual_bf.get("off_shell_cancellation_claimed") is False
        and actual_bf.get("oriented_boundary_integrand_terms")
        == [
            ("b_minus_wedge_Delta_A_Sigma", 1),
            ("b_plus_wedge_Delta_A_Sigma", -1),
        ]
        and mutation != "BF_offshell_cancelled"
    )
    pass_exact = bool(
        literal_contract["all_literal_and_geometric_axiom_pins_exact"]
        and exact_component_key_set
        and not AST_classification_issues
        and observed_layout == expected_layout
        and len(rows) == 18
        and exact_component_multiset
        and all(row["pass"] for row in row_reports)
        and normalizer_pass
        and bf_bulk_normalizer_pass
        and derived_boundary == expected_boundary
        and intrinsic_exact
        and bf_reused_exactly
    )
    serialized_normalizers = {
        side: {key: value for key, value in normalizers[side].items() if key != "_terms"}
        for side in SIDES
    }
    return {
        "scope": (
            "literal integrated Green ledger on fixed reference bulk halves and "
            "fixed interface embedding; exact relative to the pinned EH+GHY first-"
            "variation axiom, exact product-rule/IBP normalization, the already "
            "proved oriented BF incidence ledger, and six unexpanded intrinsic deltas"
        ),
        "row_count": len(rows),
        "expected_row_count": 18,
        "component_count_with_multiplicity": sum(component_counts.values()),
        "expected_component_count": len(COMPONENT_NAMES),
        "actual_component_keys": list(actual_component_keys),
        "expected_component_keys": list(COMPONENT_NAMES),
        "actual_component_keys_are_exactly_COMPONENT_NAMES": (
            exact_component_key_set
        ),
        "component_multiplicities": component_counts,
        "exact_twenty_component_multiset": exact_component_multiset,
        "observed_row_layout": [
            [name, list(components)] for name, components in observed_layout
        ],
        "expected_row_layout": [
            [name, list(components)] for name, components in expected_layout
        ],
        "literal_and_geometric_axiom_contract": literal_contract,
        "AST_derived_component_classifications": list(AST_classifications),
        "AST_classification_issues": list(AST_classification_issues),
        "candidate_rows_derived_from_AST_not_expected_layout": True,
        "rows": row_reports,
        "kinetic_product_rule_IBP_normalizer": serialized_normalizers,
        "BF_graded_bulk_variation_normalizer": {
            side: {
                key: value
                for key, value in bf_normalizers[side].items()
                if not key.startswith("_")
            }
            for side in SIDES
        },
        "derived_integrated_boundary_terms": _serialize_green_terms(
            derived_boundary
        ),
        "independent_expected_integrated_boundary_terms": _serialize_green_terms(
            expected_boundary
        ),
        "derived_boundary_equals_independent_target": (
            derived_boundary == expected_boundary
        ),
        "Omega_and_matter_momenta_derived_not_copied_from_Green_string": (
            normalizer_pass
            and literal_contract["Green_form_text_used_as_proof_target"] is False
        ),
        "potential_and_full_V4_have_no_boundary_current": all(
            not row.integrated_boundary_terms
            for row in rows
            if row.name.startswith("Omega_potential_")
            or row.name.startswith("full_V4_")
        ),
        "BF_prerequisite_reused_exactly": bf_reused_exactly,
        "BF_off_shell_oriented_flux_nonzero": actual_bf.get(
            "off_shell_oriented_flux_is_nonzero"
        ),
        "BF_off_shell_cancellation_claimed": False,
        "six_intrinsic_variations_exact_and_unexpanded": intrinsic_exact,
        "intrinsic_trace_leaf_map": {
            "g_plus": "gamma",
            "Omega_plus": "Omega_Sigma",
            "varphi_H_soldered_leaf": "varphi_H",
            "T_on_abstract_Sigma": "T_Sigma",
        },
        "EH_plus_GHY_status": "explicit geometric first-variation axiom only",
        "fixed_reference_interface_embedding": True,
        "moving_embedding_terms_included": False,
        "local_d4_intrinsic_expansion_performed": False,
        "differentiated_Ward_identity_claimed": False,
        "full_off_shell_Green_theorem_accepted": False,
        "pass": pass_exact,
    }


def _green_ledger_mutant_campaign(
    v52: Mapping[str, Any],
    *,
    bf_incidence_aggregation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for mutation in sorted(GREEN_LEDGER_MUTATIONS):
        mutated = _literal_green_ledger(
            v52,
            bf_incidence_aggregation=bf_incidence_aggregation,
            mutation=mutation,
        )
        rows[mutation] = {
            "killed": not mutated["pass"],
            "row_count": mutated["row_count"],
            "component_multiplicities": mutated["component_multiplicities"],
            "boundary_target_match": mutated[
                "derived_boundary_equals_independent_target"
            ],
        }

    literal_mutations = {
        "drift_bulk_action_literal": (
            "exact_classical_charter",
            "exact_action",
            "bulk_gauged",
        ),
        "drift_EH_GHY_axiom_literal": (
            "Green_form_certificate",
            "EH_plus_GHY_first_variation",
        ),
        "drift_momentum_literal": (
            "Green_form_certificate",
            "momenta",
            "Pi_Omega_eps",
        ),
        "drift_common_variation_literal": (
            "exact_classical_charter",
            "interface_domain",
            "variations",
            0,
        ),
        "drift_BF_bulk_equation_A_literal": (
            "Green_form_certificate",
            "bulk_equations_new_sector",
            "A",
        ),
    }
    for name, path in literal_mutations.items():
        mutated_v52 = json.loads(json.dumps(v52))
        target: Any = mutated_v52
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = "mutated"
        mutated = _literal_green_ledger(
            mutated_v52,
            bf_incidence_aggregation=bf_incidence_aggregation,
        )
        rows[name] = {
            "killed": not mutated["pass"],
            "literal_contract_exact": mutated[
                "literal_and_geometric_axiom_contract"
            ]["all_literal_and_geometric_axiom_pins_exact"],
        }
    return {
        "rows": rows,
        "mutant_count": len(rows),
        "pass": bool(rows) and all(row["killed"] for row in rows.values()),
    }


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


def _affine_connection_trace_mutant_campaign(
    v52: Mapping[str, Any],
    interface_raw_pullback: Mapping[str, Any],
) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    algebra_mutations = (
        "missing_source_affine_term",
        "wrong_source_affine_sign",
        "missing_target_affine_term",
        "wrong_target_affine_sign",
        "wrong_inverse_derivative_sign",
        "wrong_inverse_derivative_order",
        "omit_p_Leibniz_term",
        "omit_r_Leibniz_term",
        "omit_q_Leibniz_term",
        "wrong_r_prime_inverse_order",
        "frozen_r_transport",
        "r_factor_omitted_from_transport",
        "source_inverse_omitted_from_r_transport",
    )
    for mutation in algebra_mutations:
        ledger = _affine_connection_trace_ledger(
            v52,
            interface_raw_pullback,
            side_mutations={"plus": mutation},
        )
        plus_row = next(
            row
            for row in ledger["side_polynomial_identities"]
            if row["side"] == "plus"
        )
        rows[mutation] = {
            "killed": not ledger["pass"] and not plus_row["pass"],
            "residual_terms": plus_row["residual_terms"],
            "source_dp_cancels_exactly": plus_row[
                "source_dp_cancels_exactly"
            ],
        }

    split_target = _affine_connection_trace_ledger(
        v52,
        interface_raw_pullback,
        target_gauges={"plus": "q_plus", "minus": "q_minus"},
    )
    rows["split_target_q_between_sides"] = {
        "killed": (
            not split_target["pass"]
            and all(
                row["polynomial_identity_exact"]
                for row in split_target["side_polynomial_identities"]
            )
            and not split_target["same_literal_q_and_dq_used_on_both_sides"]
            and not split_target[
                "two_transformed_interface_traces_remain_equal"
            ]
        ),
        "target_gauge_atoms": split_target["target_gauge_atoms_by_side"],
    }

    detached_components = build_component_expressions("finite")
    detached_components["BF_bulk_plus"] = _replace_semantic_leaf_role(
        detached_components["BF_bulk_plus"],
        "A",
        "detached_connection",
    )
    detached = _affine_connection_trace_ledger(
        v52,
        interface_raw_pullback,
        components=detached_components,
    )
    plus_binding = next(
        row for row in detached["binding_rows"] if row["side"] == "plus"
    )
    bf_route = next(
        row
        for row in plus_binding["actual_action_component_routes"]
        if row["component"] == "BF_bulk_plus"
    )
    rows["detached_hard_coded_ledger_from_BF_connection_route"] = {
        "killed": (
            not detached["pass"]
            and not plus_binding["pass"]
            and not bf_route["all_occurrences_are_the_same_expected_A_e"]
            and not detached[
                "two_transformed_interface_traces_remain_equal"
            ]
            and all(
                row["polynomial_identity_exact"]
                for row in detached["side_polynomial_identities"]
            )
        ),
        "detached_route": bf_route,
    }

    duplicated_components = build_component_expressions("finite")
    original_p_route = duplicated_components["P_kinetic_bulk_plus"]
    if not isinstance(original_p_route, Construction):
        raise NaturalityCertificateError(
            "P kinetic route root is not a typed construction"
        )
    duplicated_components["P_kinetic_bulk_plus"] = Construction(
        operator=original_p_route.operator,
        arguments=original_p_route.arguments
        + (_bulk_field("plus", "A", CONNECTION1_5, "finite"),),
        type_tag=original_p_route.type_tag,
    )
    duplicated = _affine_connection_trace_ledger(
        v52,
        interface_raw_pullback,
        components=duplicated_components,
    )
    duplicated_plus_binding = next(
        row for row in duplicated["binding_rows"] if row["side"] == "plus"
    )
    duplicated_p_route = next(
        row
        for row in duplicated_plus_binding["actual_action_component_routes"]
        if row["component"] == "P_kinetic_bulk_plus"
    )
    rows["duplicated_A_occurrence_on_P_kinetic_route"] = {
        "killed": (
            not duplicated["pass"]
            and not duplicated_plus_binding["pass"]
            and not duplicated[
                "two_transformed_interface_traces_remain_equal"
            ]
            and not duplicated_p_route["structural_multiplicity_is_exact"]
            and duplicated_p_route[
                "all_occurrences_are_the_same_expected_A_e"
            ]
            and duplicated_p_route[
                "one_structural_A_e_symbol_type_pullback_on_this_route"
            ]
        ),
        "duplicated_route": duplicated_p_route,
    }
    return {
        "rows": rows,
        "mutant_count": len(rows),
        "pass": bool(rows) and all(row["killed"] for row in rows.values()),
    }


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
    affine_connection_trace = _affine_connection_trace_ledger(
        v52,
        interface_raw_pullback,
    )
    affine_connection_trace_mutants = (
        _affine_connection_trace_mutant_campaign(
            v52,
            interface_raw_pullback,
        )
    )
    bf_incidence_aggregation = _bf_incidence_aggregation_ledger(
        v52,
        affine_connection_trace=affine_connection_trace,
    )
    bf_incidence_mutants = _bf_incidence_mutant_campaign(
        v52,
        affine_connection_trace=affine_connection_trace,
    )
    green_ledger = _literal_green_ledger(
        v52,
        bf_incidence_aggregation=bf_incidence_aggregation,
    )
    green_ledger_mutants = _green_ledger_mutant_campaign(
        v52,
        bf_incidence_aggregation=bf_incidence_aggregation,
    )
    pin_pass = (
        source_pins["v5_2_artifact"]["canonical_exact_action_sha256"]
        == V52_EXACT_ACTION_SHA256
        and source_pins["v5_2_artifact"]["connection_trace_definition"]
        == EXPECTED_CONNECTION_TRACE_DEFINITION
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
    finite_affine_connection_trace = bool(
        pin_pass
        and affine_connection_trace["pass"]
        and affine_connection_trace_mutants["pass"]
    )
    finite_bf_incidence_aggregation = bool(
        pin_pass
        and finite_affine_connection_trace
        and bf_incidence_aggregation["pass"]
        and bf_incidence_mutants["pass"]
    )
    finite_literal_green_ledger = bool(
        pin_pass
        and finite_bf_incidence_aggregation
        and green_ledger["pass"]
        and green_ledger_mutants["pass"]
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
        "finite_full_affine_connection_trace_transport_exact_pass": (
            finite_affine_connection_trace
        ),
        "oriented_BF_incidence_aggregation_exact_pass": (
            finite_bf_incidence_aggregation
        ),
        "literal_bulk_interface_Green_ledger_pass": finite_literal_green_ledger,
        "finite_typed_geometric_S_v5_2_action_expression_covariance_exact_pass": (
            finite_geometric_covariance
        ),
        "formal_local_compact_support_chain_rule_corollary_DS_G_zero_exact_pass": bool(
            formal_local["pass"]
        ),
    }
    decision: dict[str, bool] = {
        **core,
        "oriented_BF_incidence_cancellation_exact_pass": False,
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
            "expression, exact finite affine connection-trace transport, exact "
            "off-shell oriented BF incidence aggregation, an exact symbolic "
            "fixed-reference integrated Green ledger in its stated axiom scope, "
            "and the formal local compact-support chain-rule corollary only"
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
                "pullback traces and exact finite affine connection-trace "
                "transport"
            ),
            "bundle_sector": "trivial SO3 bundles and null-homotopic extendible gauges",
            "abstract_interface_and_T_fixed_in_this_bulk_gauge_bookkeeping": True,
            "interface_matching": list(EXPECTED_INTERFACE_CONFIGURATION),
            "full_affine_connection_trace_transport_in_this_certificate": True,
            "functional_meaning": (
                "finite covariance and its unexpanded local compact-support "
                "chain-rule derivative, plus the scoped fixed-reference integrated "
                "Green ledger; no differentiated Ward identity"
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
        "finite_affine_connection_trace_transport": affine_connection_trace,
        "affine_connection_trace_effective_mutants": (
            affine_connection_trace_mutants
        ),
        "oriented_BF_incidence_aggregation": bf_incidence_aggregation,
        "oriented_BF_incidence_effective_mutants": bf_incidence_mutants,
        "literal_bulk_interface_Green_ledger": green_ledger,
        "literal_bulk_interface_Green_effective_mutants": green_ledger_mutants,
        "formal_local_compact_support_chain_rule_corollary": formal_local,
        "effective_mutants": mutants,
        "excluded_fixed_background_relative_contract": fixed_background,
        "open_local_Ward_obligations": {
            "differentiated_local_Ward_identity": (
                "OPEN: differentiate the scoped Green ledger with the complete "
                "geometric Lie variations and consume the resulting local bulk "
                "and interface divergence identities"
            ),
            "Noether_current_definition": (
                "OPEN for the local ledger: J_e=theta_e(X_e,L_zeta X_e)-i_zeta L_e"
            ),
            "moving_embedding_and_intrinsic_d4_expansion": (
                "OPEN: embedding Euler term, constrained iota/j variation, and "
                "the expanded intrinsic d_4 current remain outside this ledger"
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
            "BF_off_shell": (
                "the oriented coefficient b_plus-b_minus is not zero off shell; "
                "its cancellation uses the separately displayed natural "
                "interface equation"
            ),
            "Green_scope": (
                "EH+GHY is consumed only as the pinned geometric first-variation "
                "axiom; the six intrinsic terms remain exact unexpanded deltas, "
                "and no moving-embedding or differentiated Ward claim is made"
            ),
            "promotion": (
                "this does not close the v5.6.1 full-bulk Ward key; C1, N1, P4, B4 and B5 remain false"
            ),
        },
        "decision": decision,
        "evidence_boundary": (
            "This is an exact typed/free-word certificate relative to explicitly "
            "listed standard geometric axioms, plus an exact integer "
            "noncommutative polynomial certificate for the finite affine "
            "connection trace. It is neither a numerical check nor a "
            "proof-assistant derivation. The local compact-support DS statement "
            "is only the formal chain-rule derivative of the finite covariance "
            "ledger for the action expression. The Green result is an integrated, "
            "fixed-reference symbolic ledger in the explicitly stated EH+GHY, "
            "BF-boundary and unexpanded-intrinsic axiom scope; it is not the "
            "differentiated local Ward identity and does not promote the v5.6.1 "
            "full-bulk key."
        ),
    }


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
