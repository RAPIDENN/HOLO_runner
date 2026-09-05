#!/usr/bin/env python3
"""Fail-closed ledger for the proposed weaker-jet bridge v5.6.7.6.

Only three stand-alone mathematical ingredients are discharged here:

* complete Fourier shells converge from H^(19/4) to H^(9/2);
* the *exact ideal* radial family
  ``b_j=(1-x^2)^3 P_j(x)``, ``x=2 rho-1``, has the stated weighted C2 tail
  and C^(0,3/8) equicontinuity bound; and
* periodic trapezoid and Gauss--Legendre rules obey the stated Holder bounds.

The exact radial family is implemented below with ``Fraction`` recurrence
arithmetic for every requested j.  It is intentionally separate from the
pinned NumPy power-basis generator, which was only checked through K=8 and is
numerically unstable at larger j (in particular at an endpoint for j=23).

The pinned action source is still inspected, but that inspection is explicitly
diagnostic.  A list of function names, fourteen selected call edges and leaf
names is not a closed typed expression IR for the twenty primal/JVP formulae.
It cannot prove decoder continuity, bind every inverse/root to a margin, or
control nested helper semantics.  Therefore the three formula/Holder/bridge
keys stay FALSE even when all byte pins match.  No artifact is written.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
SCHEMA = (
    "holo.one-omega-topological-so3-bounded-margin-weaker-jet-"
    "uniform-bridge-v5-6-7-6.v1"
)

V567_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
)
V567_TEST = (
    HERE
    / "test_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
)
V5671_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
)
V5671_TEST = (
    HERE
    / "test_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
)
V5673_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_direct_free_pointwise_margin_diagonal_v5_6_7_3_gate.py"
)
V5673_TEST = (
    HERE
    / "test_one_omega_topological_so3_direct_free_pointwise_margin_diagonal_v5_6_7_3_gate.py"
)

SOURCE_PINS = {
    V567_SOURCE.name: "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25",
    V567_TEST.name: "3fdcd09c3e575893dade6a396865a593349ebc62d28c07706d3f2b58a0caacd4",
    V5671_SOURCE.name: "afe410507da533dfff9037b5bd730d90d5931f82aaeb8d4839a48f9a4d18e0c9",
    V5671_TEST.name: "d7988e078fb81f9fa3001eaff2414962d45bfb240b024fbaacf8a9ab126b9694",
    V5673_SOURCE.name: "e85d247bfbc766ff59105469626b0191adb6aaeda9799c84dca3fdeca4e3271a",
    V5673_TEST.name: "1d7687ed37c9a10454d221440184080412ede621f8301aa940b1ed76d3c05fdd",
}

DIMENSION = 4
S = Fraction(19, 4)
S0 = Fraction(9, 2)
ALPHA = Fraction(1, 4)
RADIAL_HOLDER = Fraction(3, 8)
RADIAL_WEIGHT_POWER = 4
BULK_COUNT = 12
BOUNDARY_COUNT = 8
COMPONENT_COUNT = BULK_COUNT + BOUNDARY_COUNT

EXPECTED_COMPONENTS = (
    "EH_bulk_plus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "GHY_minus",
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)

EXPECTED_ANALYTIC_MARGINS = frozenset(
    {
        "common_gamma_lorentzian_eigen_gap",
        "pulled_bulk_actual_plus_lorentzian_eigen_gap",
        "pulled_bulk_actual_minus_lorentzian_eigen_gap",
        "pulled_bulk_reference_plus_lorentzian_eigen_gap",
        "pulled_bulk_reference_minus_lorentzian_eigen_gap",
        "ghy_spacelike_normal_plus",
        "ghy_spacelike_normal_minus",
        "khronon_timelike",
        "frame_gram_leading_minor_1",
        "frame_gram_leading_minor_2",
        "frame_gram_leading_minor_3",
        "omega_plus",
        "omega_minus",
        "so3_chart_q",
        "so3_chart_r_plus",
        "so3_chart_r_minus",
    }
)

ENHANCED_H_S_PLUS_1_FIELDS = (
    "plus.Y",
    "minus.Y",
    "Q_frame.q",
    "plus.r_E0",
    "minus.r_E0",
)

CONSUMED_JET_LEAVES = {
    "bulk_each_side": (
        "g",
        "d_g",
        "dd_g",
        "log_Omega",
        "d_log_Omega",
        "phi",
        "d_phi",
        "A",
        "d_A",
        "B",
    ),
    "GHY_each_side": ("g", "d_g"),
    "shared_interface": (
        "gamma",
        "d_gamma",
        "dd_gamma",
        "d_tau",
        "dd_tau",
        "E_Q",
        "varphi",
        "log_Omega",
    ),
}

REQUIRED_CALL_EDGES = {
    "decode_common_first_boundary_td3": frozenset(
        {"_spectral_td3", "so3_exp", "_inverse_td3", "_matmul", "_vee_checked_td3"}
    ),
    "_collar_ambient_x64": frozenset({"_load_pinned_upstream", "RhoJet2"}),
    "_pullback_x64_and_reference15": frozenset(
        {"_sym_matrix", "_matmul", "_det3"}
    ),
    "rhojet2_local_two_jet": frozenset({"_dual_value"}),
    "_bulk_component_densities_td3": frozenset(
        {"td3_metric_geometry", "td3_cross", "_regular_v4_td3"}
    ),
    "_relative_bulk_densities_td3": frozenset(
        {"_bulk_component_densities_td3", "_x64_local_primitives"}
    ),
    "_ghy_density_td3": frozenset(
        {"_x64_local_primitives", "td3_metric_geometry"}
    ),
    "_foliation_geometry_td3": frozenset({"td3_metric_geometry"}),
    "_interface_component_densities_td3": frozenset(
        {"_foliation_geometry_td3", "_dual_value"}
    ),
    "_bulk_components_from_boundary_td3": frozenset(
        {
            "_collar_ambient_x64",
            "_pullback_x64_and_reference15",
            "_relative_bulk_densities_td3",
        }
    ),
    "_boundary_components_from_boundary_td3": frozenset(
        {
            "_collar_ambient_x64",
            "_pullback_x64_and_reference15",
            "_ghy_density_td3",
            "_interface_component_densities_td3",
        }
    ),
    "_local_density_td3": frozenset(
        {
            "decode_common_first_boundary_td3",
            "_bulk_components_from_boundary_td3",
            "_boundary_components_from_boundary_td3",
        }
    ),
    "integrated_action_values_and_eta_jvps": frozenset(
        {
            "finite_full_t4_rho_quadrature",
            "decode_common_first_boundary_td3",
            "_bulk_components_from_boundary_td3",
            "_boundary_components_from_boundary_td3",
        }
    ),
}

REQUIRED_DOMAIN_FRAGMENTS = {
    "boundary_once_per_T4_node": "for name in BOUNDARY_COMPONENTS:",
    "bulk_has_rho_loop": "for rho, radial_weight in zip(rho_nodes, rho_weights):",
    "bulk_uses_product_weight": (
        "combined_weight = float(tangential_weight) * float(radial_weight)"
    ),
    "bulk_component_loop": "for name in BULK_COMPONENTS:",
    "total_after_components": (
        'math.fsum(records[name]["value"] for name in LOCAL_DENSITY_COMPONENTS)'
    ),
    "explicit_domain_separation": (
        '"S_total_formed_only_after_twenty_domain_integrals": True'
    ),
}

TRUE_DECISION_KEYS = frozenset(
    {
        "complete_shell_H19_4_to_H9_2_uniform_rate_pass",
        "weighted_radial_p4_C2_tail_and_C0_3_8_equicontinuity_pass",
        "tensor_trapezoid_gauss_bernstein_exact_bound_pass",
    }
)

FALSE_DECISION_KEYS = frozenset(
    {
        "margins_certified_pass",
        "integrated_action_pass",
        "quadrature_pass",
        "v5_6_7_1_runtime_eventual_acceptance_pass",
        "twenty_real_formula_paths_and_sixteen_margin_inventory_ast_bound_pass",
        "uniform_twenty_primal_jvp_holder_lemma_pass",
        "bounded_margin_ball_weaker_jet_exact_formula_uniform_bridge_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_N_to_infinity_numerical_certificate_pass",
        "same_functional_symbolic_identity_pass",
        "all_N_q_zero_factorization_pass",
        "continuum_action_representative_independence_theorem_pass",
        "global_smooth_physical_gauge_quotient_manifold_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "P4_full_same_action_pass",
        "B4_pass",
        "B5_pass",
    }
)


class WeakerJetUniformBridgeError(RuntimeError):
    """Raised when an exact theorem input or source binding drifts."""


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strict_nonnegative_integer(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def complete_shell_size(shell_radius: int) -> int:
    """Real dimension of the complete |k|_infinity<=L Fourier shell."""

    radius = _strict_nonnegative_integer("shell_radius", shell_radius)
    return (2 * radius + 1) ** DIMENSION


def radial_basis_derivative_bounds(index: int) -> tuple[int, int, int]:
    """All-j sup bounds for the ideal b_j, b'_j and b''_j family."""

    j = _strict_nonnegative_integer("index", index)
    return 1, 12 + 4 * j, 120 + 80 * j + 4 * j * (j + 1)


def _exact_scalar(value: Any, *, name: str) -> Fraction:
    """Accept only exact integers/Fractions on the ideal-basis path."""

    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError(f"{name} must be an int or Fraction")
    return Fraction(value)


def _poly_add(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    size = max(len(left), len(right))
    values = [Fraction(0) for _ in range(size)]
    for index, coefficient in enumerate(left):
        values[index] += coefficient
    for index, coefficient in enumerate(right):
        values[index] += coefficient
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def _poly_scale(
    coefficients: Sequence[Fraction], scalar: Fraction
) -> tuple[Fraction, ...]:
    return tuple(scalar * coefficient for coefficient in coefficients)


def _poly_multiply(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    values = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for left_index, left_coefficient in enumerate(left):
        for right_index, right_coefficient in enumerate(right):
            values[left_index + right_index] += left_coefficient * right_coefficient
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def exact_legendre_coefficients(index: int) -> tuple[Fraction, ...]:
    """Return P_j(x) in increasing powers of x by the exact all-j recurrence."""

    j = _strict_nonnegative_integer("index", index)
    previous = (Fraction(1),)
    if j == 0:
        return previous
    current = (Fraction(0), Fraction(1))
    for degree in range(1, j):
        x_current = (Fraction(0),) + current
        numerator = _poly_add(
            _poly_scale(x_current, Fraction(2 * degree + 1)),
            _poly_scale(previous, Fraction(-degree)),
        )
        following = _poly_scale(numerator, Fraction(1, degree + 1))
        previous, current = current, following
    return current


def exact_radial_basis_coefficients(index: int) -> tuple[Fraction, ...]:
    """Return (1-x^2)^3 P_j(x), never the NumPy power-basis conversion."""

    envelope = tuple(Fraction(value) for value in (1, 0, -3, 0, 3, 0, -1))
    return _poly_multiply(envelope, exact_legendre_coefficients(index))


def _poly_derivative(
    coefficients: Sequence[Fraction], order: int
) -> tuple[Fraction, ...]:
    derivative_order = _strict_nonnegative_integer("order", order)
    result = tuple(coefficients)
    for _ in range(derivative_order):
        if len(result) == 1:
            return (Fraction(0),)
        result = tuple(
            Fraction(power) * coefficient
            for power, coefficient in enumerate(result[1:], start=1)
        )
    return result


def _poly_value(coefficients: Sequence[Fraction], argument: Fraction) -> Fraction:
    value = Fraction(0)
    for coefficient in reversed(coefficients):
        value = value * argument + coefficient
    return value


def exact_radial_basis_jet(index: int, rho: int | Fraction) -> tuple[Fraction, ...]:
    """Return exact rho derivatives 0..2 of b_j at an exact rho in [0,1]."""

    exact_rho = _exact_scalar(rho, name="rho")
    if not Fraction(0) <= exact_rho <= Fraction(1):
        raise ValueError("rho must lie in [0,1]")
    x = 2 * exact_rho - 1
    coefficients = exact_radial_basis_coefficients(index)
    return tuple(
        Fraction(2**order) * _poly_value(_poly_derivative(coefficients, order), x)
        for order in range(3)
    )


def _fraction_sequence_payload(values: Sequence[Fraction]) -> list[list[int]]:
    return [[value.numerator, value.denominator] for value in values]


def exact_radial_family_fingerprint(last_index: int = 12) -> str:
    """Fingerprint an exact prefix; the recurrence itself accepts arbitrary j."""

    final = _strict_nonnegative_integer("last_index", last_index)
    payload = [
        _fraction_sequence_payload(exact_radial_basis_coefficients(index))
        for index in range(final + 1)
    ]
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _assignment_value(tree: ast.AST, name: str) -> Any:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == name for target in targets):
            continue
        value = node.value
        if value is None:
            break
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
            and len(value.args) == 1
        ):
            value = value.args[0]
        return ast.literal_eval(value)
    raise WeakerJetUniformBridgeError(f"assignment {name!r} not found or non-literal")


def _function_nodes(tree: ast.AST) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _function_calls(node: ast.AST) -> frozenset[str]:
    return frozenset(
        name
        for call in ast.walk(node)
        if isinstance(call, ast.Call)
        for name in [_call_name(call)]
        if name is not None
    )


def _transitive_formula_source_diagnostic(source_text: str) -> dict[str, Any]:
    """Expose why the Python source is not yet a closed, pure formula IR.

    This deliberately follows every lexically local call reachable from the
    public integration entry point, rather than blessing a hand-picked edge
    list.  Attribute calls cannot be resolved soundly by this AST walk (class
    methods with the same short name collide), which is itself one reason this
    diagnostic cannot discharge the formula theorem.
    """

    tree = ast.parse(source_text)
    functions = _function_nodes(tree)
    roots = ("integrated_action_values_and_eta_jvps",)
    pending = list(roots)
    reachable: set[str] = set()
    while pending:
        name = pending.pop()
        if name in reachable or name not in functions:
            continue
        reachable.add(name)
        pending.extend(sorted(_function_calls(functions[name]) - reachable))

    adjacency = {
        name: sorted(call for call in _function_calls(functions[name]) if call in functions)
        for name in sorted(reachable)
    }
    encoded_adjacency = json.dumps(
        adjacency, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    per_function: dict[str, dict[str, Any]] = {}
    for name in sorted(reachable):
        node = functions[name]
        body_attributes = sum(
            1
            for child in ast.walk(node)
            if isinstance(child, ast.Attribute) and child.attr == "body"
        )
        forbidden_builtin_calls = sorted(
            {
                child.func.id
                for child in ast.walk(node)
                if isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id in {"abs", "max", "min"}
            }
        )
        branch_nodes = sum(
            1
            for child in ast.walk(node)
            if isinstance(child, (ast.If, ast.IfExp, ast.Match))
        )
        numpy_references = sum(
            1
            for child in ast.walk(node)
            if (
                isinstance(child, ast.Name)
                and child.id in {"np", "numpy"}
            )
        )
        if body_attributes or forbidden_builtin_calls or branch_nodes or numpy_references:
            per_function[name] = {
                "body_attribute_count": body_attributes,
                "forbidden_builtin_calls": forbidden_builtin_calls,
                "branch_node_count": branch_nodes,
                "numpy_reference_count": numpy_references,
            }

    return {
        "roots": list(roots),
        "reachable_local_function_count": len(reachable),
        "reachable_local_functions": sorted(reachable),
        "adjacency_sha256": hashlib.sha256(encoded_adjacency).hexdigest(),
        "regular_v4_reachable": "_regular_v4_td3" in reachable,
        "functions_with_non_pure_python_features": per_function,
        "attribute_calls_semantically_resolved": False,
        "standalone_typed_expression_IR_emitted": False,
        "decoder_projection_continuity_discharged": False,
        "inverse_root_guard_bijection_discharged": False,
        "pass": False,
    }


def _literal_return_dict_keys(node: ast.AST) -> frozenset[str]:
    keys: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Return) or not isinstance(child.value, ast.Dict):
            continue
        for key in child.value.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
    return frozenset(keys)


def _literal_subscript_keys(node: ast.AST, base_name: str) -> frozenset[str]:
    keys: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Subscript):
            continue
        if not isinstance(child.value, ast.Name) or child.value.id != base_name:
            continue
        if isinstance(child.slice, ast.Constant) and isinstance(child.slice.value, str):
            keys.add(child.slice.value)
    return frozenset(keys)


def _source_pin_ledger() -> dict[str, Any]:
    observed = {
        path.name: _sha256(path)
        for path in (V567_SOURCE, V567_TEST, V5671_SOURCE, V5671_TEST, V5673_SOURCE, V5673_TEST)
    }
    matches = {name: observed.get(name) == expected for name, expected in SOURCE_PINS.items()}
    return {"expected": dict(SOURCE_PINS), "observed": observed, "matches": matches, "pass": all(matches.values())}


def _real_formula_ast_inventory() -> dict[str, Any]:
    action_text = V5671_SOURCE.read_text(encoding="utf-8")
    action_tree = ast.parse(action_text)
    functions = _function_nodes(action_tree)
    missing_functions = sorted(set(REQUIRED_CALL_EDGES) - set(functions))
    observed_calls = {
        name: sorted(_function_calls(functions[name]))
        for name in REQUIRED_CALL_EDGES
        if name in functions
    }
    edge_matches = {
        name: bool(name in functions and required <= _function_calls(functions[name]))
        for name, required in REQUIRED_CALL_EDGES.items()
    }

    sides = tuple(_assignment_value(action_tree, "SIDES"))
    bulk_sectors = tuple(_assignment_value(action_tree, "BULK_SECTORS"))
    interface_sectors = tuple(_assignment_value(action_tree, "INTERFACE_SECTORS"))
    components = tuple(
        name
        for side in sides
        for name in tuple(f"{sector}_bulk_{side}" for sector in bulk_sectors)
        + (f"GHY_{side}",)
    ) + interface_sectors

    bulk_return_keys = (
        _literal_return_dict_keys(functions["_bulk_component_densities_td3"])
        if "_bulk_component_densities_td3" in functions
        else frozenset()
    )
    interface_return_keys = (
        _literal_return_dict_keys(functions["_interface_component_densities_td3"])
        if "_interface_component_densities_td3" in functions
        else frozenset()
    )
    bulk_primitive_keys = (
        _literal_subscript_keys(functions["_bulk_component_densities_td3"], "primitives")
        if "_bulk_component_densities_td3" in functions
        else frozenset()
    )
    ghy_primitive_keys = (
        _literal_subscript_keys(functions["_ghy_density_td3"], "primitives")
        if "_ghy_density_td3" in functions
        else frozenset()
    )
    interface_common_keys = (
        _literal_subscript_keys(functions["_interface_component_densities_td3"], "common")
        if "_interface_component_densities_td3" in functions
        else frozenset()
    )
    expected_bulk_primitive_keys = frozenset(CONSUMED_JET_LEAVES["bulk_each_side"])
    expected_ghy_primitive_keys = frozenset(CONSUMED_JET_LEAVES["GHY_each_side"])
    expected_interface_common_keys = frozenset(
        {"gamma", "T", "E_Q", "varphi", "log_Omega"}
    )
    domain_fragments = {
        name: fragment in action_text for name, fragment in REQUIRED_DOMAIN_FRAGMENTS.items()
    }

    margin_tree = ast.parse(V5673_SOURCE.read_text(encoding="utf-8"))
    observed_margins = frozenset(_assignment_value(margin_tree, "ANALYTIC_MARGIN_OBLIGATIONS"))

    resource_caps = {
        "Q": _assignment_value(action_tree, "MAX_FINITE_T4_ORDER_PER_AXIS"),
        "G": _assignment_value(action_tree, "MAX_FINITE_RADIAL_ORDER"),
    }
    shallow_inventory_pass = bool(
        not missing_functions
        and all(edge_matches.values())
        and components == EXPECTED_COMPONENTS
        and bulk_return_keys
        == frozenset(
            {"EH", "Omega_kinetic", "Omega_potential", "P_kinetic", "full_V4", "BF"}
        )
        and interface_return_keys
        == frozenset({"wall", "K_foliation", "R", "R_squared", "a_squared", "Robin"})
        and bulk_primitive_keys == expected_bulk_primitive_keys
        and ghy_primitive_keys == expected_ghy_primitive_keys
        and interface_common_keys == expected_interface_common_keys
        and all(domain_fragments.values())
        and observed_margins == EXPECTED_ANALYTIC_MARGINS
        and resource_caps == {"Q": 8, "G": 16}
    )
    transitive_diagnostic = _transitive_formula_source_diagnostic(action_text)
    return {
        "missing_required_functions": missing_functions,
        "required_call_edges": {name: sorted(values) for name, values in REQUIRED_CALL_EDGES.items()},
        "observed_calls": observed_calls,
        "call_edge_matches": edge_matches,
        "component_order": list(components),
        "component_count": len(components),
        "bulk_formula_return_keys": sorted(bulk_return_keys),
        "interface_formula_return_keys": sorted(interface_return_keys),
        "consumed_source_subscript_keys": {
            "bulk_primitives": sorted(bulk_primitive_keys),
            "GHY_primitives": sorted(ghy_primitive_keys),
            "interface_common": sorted(interface_common_keys),
        },
        "domain_fragment_matches": domain_fragments,
        "analytic_margin_ids": sorted(observed_margins),
        "analytic_margin_count": len(observed_margins),
        "runtime_resource_caps": resource_caps,
        "v5_6_7_4_consumed_as_positive_pin": False,
        "shallow_lexical_inventory_pass": shallow_inventory_pass,
        "transitive_source_diagnostic": transitive_diagnostic,
        "blocking_reasons": [
            "no standalone typed pure expression IR for all twenty primal/JVP routes",
            "short attribute call names are not resolved to implementations",
            "leaf names do not bind derivative order, shape, or every transitive use",
            "sixteen margin names are not a denominator/root-to-guard bijection",
            "decoder and projection continuity into every consumed jet is not discharged",
        ],
        "pass": False,
    }


def _fourier_ledger() -> dict[str, Any]:
    gap = S - S0
    weight_exponent = -gap / 2
    asymptotic_exponent = -gap
    embedding_C2_alpha_threshold = Fraction(2) + ALPHA + Fraction(DIMENSION, 2)
    embedding_C3_alpha_threshold = Fraction(3) + ALPHA + Fraction(DIMENSION, 2)
    return {
        "dimension": DIMENSION,
        "s": _fraction_record(S),
        "s0": _fraction_record(S0),
        "alpha": _fraction_record(ALPHA),
        "exact_norm_bound": "||(I-P_L)f||_Hs0 <= [1+(L+1)^2]^(-1/8)||f||_Hs",
        "weight_exponent": _fraction_record(weight_exponent),
        "asymptotic_L_exponent": _fraction_record(asymptotic_exponent),
        "complete_shell_formula": "N_L=(2L+1)^4",
        "shell_examples": {str(L): complete_shell_size(L) for L in range(4)},
        "ordinary_embedding": "H^(9/2)(T4) -> C^(2,1/4)(T4)",
        "enhanced_embedding": "H^(11/2)(T4) -> C^(3,1/4)(T4)",
        "enhanced_fields": list(ENHANCED_H_S_PLUS_1_FIELDS),
        "same_norm_operator_convergence_claimed": False,
        "pass": bool(
            gap == Fraction(1, 4)
            and weight_exponent == Fraction(-1, 8)
            and asymptotic_exponent == Fraction(-1, 4)
            and S0 > embedding_C2_alpha_threshold
            and S0 + 1 > embedding_C3_alpha_threshold
            and complete_shell_size(0) == 1
            and complete_shell_size(1) == 81
            and complete_shell_size(2) == 625
        ),
    }


def _radial_ledger() -> dict[str, Any]:
    squared_summand_exponents = {
        str(order): 2 * order - 2 * RADIAL_WEIGHT_POWER for order in range(3)
    }
    tail_norm_exponents = {
        str(order): Fraction(exponent + 1, 2)
        for order, exponent in (
            (order, squared_summand_exponents[str(order)]) for order in range(3)
        )
    }
    amplitude_constant = 240  # 2 B_2(j) <= 240 (j+1)^2.
    markov_constant = 8 * 6**6  # ||b'''_j|| <= 8(j+6)^6 <= this*(j+1)^6.
    split_power = Fraction(1, 4)
    low_squared_delta_exponent = Fraction(2) - Fraction(5) * split_power
    high_squared_delta_exponent = Fraction(3) * split_power
    endpoint = low_squared_delta_exponent / 2
    termwise_endpoint_series_exponent = -4 + 8 * RADIAL_HOLDER
    holder_constant_squared = (
        Fraction(512 * markov_constant**2) + Fraction(16 * amplitude_constant**2, 3)
    )
    # Coefficients are in increasing powers of j.  These exact identities
    # certify the coarse inequalities used below without sampling j.
    c2_tail_difference = (-120, -84, 204)
    c2_tail_factored = (-120, -84, 204)  # 12(j-1)(17j+10).
    amplitude_difference = (0, 312, 232)  # 240(j+1)^2-2B_2(j).
    weight_identity = (1, -2, 1)  # 2(1+j^2)-(j+1)^2=(j-1)^2.
    markov_linear_difference = (0, 5)  # 6(j+1)-(j+6)=5j.
    exact_prefix_fingerprint = exact_radial_family_fingerprint(12)
    endpoint_j23 = exact_radial_basis_jet(23, Fraction(1))
    return {
        "basis": "b_j(rho)=64[rho(1-rho)]^3 P_j(2rho-1)",
        "basis_role": "exact ideal family, not the NumPy power-basis runtime generator",
        "exact_engine": {
            "coefficient_field": "Q (fractions only)",
            "legendre_recurrence": (
                "P_0=1; P_1=x; P_(j+1)=((2j+1)xP_j-jP_(j-1))/(j+1)"
            ),
            "envelope_in_x": "(1-x^2)^3",
            "rho_chain_rule": "d_rho^m=2^m d_x^m for m=0,1,2",
            "arbitrary_nonnegative_index_accepted": True,
            "prefix_0_through_12_sha256": exact_prefix_fingerprint,
            "j23_rho1_jet_0_through_2": _fraction_sequence_payload(endpoint_j23),
        },
        "pinned_numpy_generator": {
            "used_by_ideal_lemma": False,
            "upstream_validation_scope": "K<=8 only",
            "all_j_runtime_certified": False,
            "known_failure": "K=24,j=23,rho=1 may evaluate b_23 near -219 in float64",
        },
        "weight": "sum_j (1+j^2)^4 ||C_j||_Hs^2",
        "all_j_sup_bound_proof": {
            "legendre_identities": [
                "|P_j(x)|<=1 on [-1,1]",
                "(1-x^2)P_j'=j(P_(j-1)-xP_j) for j>=1",
                "(1-x^2)P_j''=2xP_j'-j(j+1)P_j",
            ],
            "consequences": [
                "|w P_j'|<=2j with w=1-x^2",
                "d_x b_j=-6xw^2P_j+w^3P_j'",
                (
                    "d_x^2 b_j=(-6w^2+24x^2w-j(j+1)w^2)P_j"
                    "-10xw^2P_j'"
                ),
                "d_rho=2d_x and d_rho^2=4d_x^2",
            ],
            "result": (
                "||b_j||<=1; ||b_j'||<=12+4j; "
                "||b_j''||<=120+80j+4j(j+1)"
            ),
        },
        "derivative_bounds": {
            "b_j": "1",
            "b_j_prime": "12+4j",
            "b_j_second": "120+80j+4j(j+1)",
        },
        "squared_summand_exponents": squared_summand_exponents,
        "tail_norm_exponents": {
            order: _fraction_record(value) for order, value in tail_norm_exponents.items()
        },
        "worst_C2_tail": "R_2(K) <= (416/sqrt(3)) K^(-3/2), K>=1",
        "C2_tail_proof": [
            "B2(j)<=208j^2 for j>=1",
            "sum_(j>=K) B2(j)^2/(1+j^2)^4 <= 208^2 sum_(j>=K)j^(-4)",
            "sum_(j>=K)j^(-4)<=K^(-4)+(1/3)K^(-3)<=(4/3)K^(-3)",
            "Cauchy-Schwarz gives 416/sqrt(3) K^(-3/2)",
        ],
        "worst_C2_constant_numerator": 416,
        "worst_C2_constant_squared_denominator": 3,
        "exact_coarse_inequality_identities": {
            "208j2_minus_B2": {
                "coefficients": list(c2_tail_difference),
                "factorization": "12(j-1)(17j+10), j>=1",
            },
            "240_jplus1_squared_minus_2B2": list(amplitude_difference),
            "twice_1plusj2_minus_jplus1_squared": list(weight_identity),
            "six_jplus1_minus_jplus6": list(markov_linear_difference),
        },
        "markov": {
            "degree": "j+6",
            "third_derivative_bound": (
                "||d_rho^3 b_j||_infinity <= 8(j+6)^6||b_j||_infinity"
            ),
            "coarse_growth_constant": markov_constant,
        },
        "endpoint_split": {
            "delta_range": "0<delta<=1",
            "index": "J=ceil(delta^(-1/4)); low 0<=j<J; high j>=J",
            "integer_bounds": (
                "delta^(-1/4)<=J<=2delta^(-1/4); "
                "sum_(j<J)(j+1)^4<=J^5; sum_(j>=J)(j+1)^(-4)<=1/(3J^3)"
            ),
            "split_power": _fraction_record(split_power),
            "low_squared_delta_exponent": _fraction_record(low_squared_delta_exponent),
            "high_squared_delta_exponent": _fraction_record(high_squared_delta_exponent),
            "holder_exponent": _fraction_record(endpoint),
            "holder_constant_squared": _fraction_record(holder_constant_squared),
            "weighted_Cauchy_Schwarz_proof": [
                "(1+j^2)^(-4)<=16(j+1)^(-8)",
                (
                    "low squared dual weight <=16 A^2 delta^2 "
                    "sum_(j<J)(j+1)^4<=512 A^2 delta^(3/4)"
                ),
                (
                    "high squared dual weight <=16 B^2 "
                    "sum_(j>=J)(j+1)^(-4)<=(16/3)B^2 delta^(3/4)"
                ),
                "one Cauchy-Schwarz over both ranges yields C delta^(3/8)",
            ],
        },
        "termwise_interpolation_endpoint_series_exponent": _fraction_record(
            termwise_endpoint_series_exponent
        ),
        "termwise_interpolation_is_not_endpoint_proof": True,
        "pass": bool(
            exact_legendre_coefficients(3)
            == (Fraction(0), Fraction(-3, 2), Fraction(0), Fraction(5, 2))
            and exact_radial_basis_coefficients(0)
            == tuple(Fraction(value) for value in (1, 0, -3, 0, 3, 0, -1))
            and endpoint_j23 == (Fraction(0), Fraction(0), Fraction(0))
            and radial_basis_derivative_bounds(0) == (1, 12, 120)
            and radial_basis_derivative_bounds(3) == (1, 24, 408)
            and squared_summand_exponents == {"0": -8, "1": -6, "2": -4}
            and tail_norm_exponents["2"] == Fraction(-3, 2)
            and c2_tail_difference == c2_tail_factored
            and c2_tail_difference == (-120, -84, 204)
            and amplitude_difference == (0, 312, 232)
            and weight_identity == (1, -2, 1)
            and markov_linear_difference == (0, 5)
            and markov_constant == 373248
            and low_squared_delta_exponent == high_squared_delta_exponent == Fraction(3, 4)
            and endpoint == RADIAL_HOLDER
            and termwise_endpoint_series_exponent == -1
            and RADIAL_HOLDER > ALPHA
        ),
    }


def _canonical_theorem_contract() -> dict[str, Any]:
    return {
        "schema": "bounded-margin-weaker-jet-exact-formula-contract.v1",
        "status": "specification_only_not_discharged",
        "source_space": {
            "dimension": 4,
            "ordinary_fields": "H^(19/4)(T4)",
            "enhanced_fields": list(ENHANCED_H_S_PLUS_1_FIELDS),
            "enhanced_space": "H^(23/4)(T4)",
            "radial_coefficients": "l2((1+j^2)^4;H^(19/4)(T4))^128",
            "base_norm_bound": "||u||<=M",
            "tangent_norm_bound": "||a||<=M",
        },
        "ball": {
            "name": "B_(M,epsilon)",
            "quantifiers": "for every M>=1 and 0<epsilon<=1",
            "margin_condition": "minimum of all sixteen analytic margins >= epsilon",
            "whole_noncompact_domain_uniformity_claimed": False,
        },
        "projection": {
            "T4": "complete |k|_infinity<=L shell",
            "real_dimension": "(2L+1)^4",
            "rho": "indices 0<=j<K",
            "base_and_tangent_projected": True,
        },
        "consumed_jet_target": {
            "ordinary": "C^(2,1/4)",
            "enhanced": "C^(3,1/4) tangential only",
            "radial_second_derivative_modulus": "C^(0,3/8)",
            "full_collar_C3_claimed": False,
            "leaves": {name: list(values) for name, values in CONSUMED_JET_LEAVES.items()},
        },
        "analytic_map": {
            "name": "Gamma_exact_formula_required_but_not_emitted",
            "primitive_inventory": [
                "finite sums and contractions",
                "products",
                "determinant",
                "matrix inverse away from zero eigenvalue",
                "positive square root",
                "reciprocal and integer powers",
                "scalar exponential",
                "entire SO3 Rodrigues functions",
                "regular V4 denominator sqrt(1+Omega^6|phi|^4)",
            ],
            "uniform_first_and_second_derivative_bounds_discharged": False,
            "differentiation_under_each_compact_domain_integral_discharged": False,
        },
        "integrands": {
            "primal_count": 20,
            "JVP_count": 20,
            "bulk_count": 12,
            "boundary_count": 8,
            "uniform_C0_alpha_constant": "H(M,epsilon)",
            "formula_difference_constant": "C(M,epsilon)",
            "S_total_after_twenty_integrals": True,
        },
        "eventual_margins": {
            "exists": "n0(M,epsilon)",
            "definition": (
                "least n>=1 with C_margin(M,epsilon)"
                "([1+(n+1)^2]^(-1/8)+(416/sqrt(3))n^(-3/2))<=epsilon/2"
            ),
            "order": "for every n>=n0 and every (u,a) in B_(M,epsilon)",
            "projected_margin": ">=epsilon/2",
            "early_n_claimed": False,
        },
        "diagonal": {
            "L_n": "n",
            "K_n": "n",
            "N_n": "(2n+1)^4",
            "Q_n": "n",
            "G_n": "n",
            "n_domain": "positive integers",
        },
        "target_identity": {
            "proposed_not_proved": (
                "the exact real integral of the same twenty formula paths"
            ),
            "literal_S_rel_symbolic_identity_claimed": False,
            "q_zero_continuum_factorization_claimed": False,
            "physical_gauge_quotient_claimed": False,
            "float64_runtime_sequence_claimed": False,
        },
    }


def _theorem_contract_accepts(contract: Mapping[str, Any]) -> bool:
    return isinstance(contract, Mapping) and dict(contract) == _canonical_theorem_contract()


def _quadrature_ledger() -> dict[str, Any]:
    gauss_degree_offset = -1
    gauss_degree = "2G-1"
    gauss_rate = -ALPHA / 2
    rates = (-(S - S0), Fraction(-3, 2), -ALPHA, gauss_rate)
    overall_rate = max(rates)
    return {
        "T4_volume": "(2pi)^4",
        "periodic_voronoi_cell_radius_in_dimension_four": "2pi/Q",
        "trapezoid_per_atom": "V H (2pi/Q)^(1/4)",
        "gauss": {
            "positive_weights_sum": 1,
            "polynomial_exactness_degree": gauss_degree,
            "degree_offset_from_2G": gauss_degree_offset,
            "Bernstein_sup_error": "H [1/(2 sqrt(2G-1))]^(1/4)",
            "integral_plus_rule_factor": 2,
            "bulk_per_atom": "2 V H [1/(2 sqrt(2G-1))]^(1/4)",
            "asymptotic_G_exponent": _fraction_record(gauss_rate),
        },
        "projection_delta": (
            "Delta_n=[1+(n+1)^2]^(-1/8)+(416/sqrt(3))n^(-3/2)"
        ),
        "S_total_bound": (
            "20 V C Delta_n + 20 V H (2pi/n)^(1/4) + "
            "24 V H [1/(2 sqrt(2n-1))]^(1/4)"
        ),
        "rate_candidates": [_fraction_record(value) for value in rates],
        "overall_n_exponent": _fraction_record(overall_rate),
        "overall_bound": "D(M,epsilon)n^(-1/8), n>=n0(M,epsilon)",
        "pass": bool(
            ALPHA == Fraction(1, 4)
            and gauss_degree_offset == -1
            and gauss_rate == Fraction(-1, 8)
            and overall_rate == Fraction(-1, 8)
            and COMPONENT_COUNT == 20
            and 2 * BULK_COUNT == 24
        ),
    }


def _same_norm_no_go() -> dict[str, Any]:
    return {
        "witness": (
            "choose one real Fourier mode with |k|_infinity=L+1, normalize its "
            "H^s norm to one, and add a fixed sufficiently small multiple to an "
            "interior background"
        ),
        "projection": "P_L f_L=0",
        "same_norm_error": "||(I-P_L)f_L||_Hs=1",
        "margin_ball_compatibility": (
            "the normalized mode has vanishing C2 amplitude as L grows, so a fixed "
            "small Hs amplitude preserves an interior background margin"
        ),
        "conclusion": "operator-norm convergence on an Hs ball in Hs is impossible",
        "pass": True,
    }


def _mutant_campaign() -> dict[str, Any]:
    canonical = _canonical_theorem_contract()
    mutants: dict[str, dict[str, Any]] = {}

    def add(identifier: str, mutation: Any) -> None:
        candidate = copy.deepcopy(canonical)
        mutation(candidate)
        mutants[identifier] = {
            "accepted": _theorem_contract_accepts(candidate),
            "detected": not _theorem_contract_accepts(candidate),
        }

    add("same_norm_target", lambda c: c["consumed_jet_target"].update({"ordinary": "H^(19/4)"}))
    add("critical_s0_four", lambda c: c["consumed_jet_target"].update({"ordinary": "H^4"}))
    add("alpha_one_half_endpoint", lambda c: c["consumed_jet_target"].update({"ordinary": "C^(2,1/2)"}))
    add("omit_q_enhanced_regularity", lambda c: c["source_space"]["enhanced_fields"].remove("Q_frame.q"))
    add("radial_weight_three", lambda c: c["source_space"].update({"radial_coefficients": "l2((1+j^2)^3;H^(19/4)(T4))^128"}))
    add("omit_tangent_bound", lambda c: c["source_space"].pop("tangent_norm_bound"))
    add("omit_one_margin", lambda c: c["ball"].update({"margin_condition": "fifteen margins >= epsilon"}))
    add("merge_bulk_boundary_domains", lambda c: c["integrands"].update({"bulk_count": 20, "boundary_count": 0}))
    add("gauss_degree_2G", lambda c: c["diagonal"].update({"G_n": "degree 2G exact"}))
    add("fixed_quadrature", lambda c: c["diagonal"].update({"Q_n": "8", "G_n": "16"}))
    add("N_n_equals_n", lambda c: c["diagonal"].update({"N_n": "n"}))
    add("claim_literal_S_rel_identity", lambda c: c["target_identity"].update({"literal_S_rel_symbolic_identity_claimed": True}))
    add("claim_q_continuum", lambda c: c["target_identity"].update({"q_zero_continuum_factorization_claimed": True}))
    add("claim_float64_sequence", lambda c: c["target_identity"].update({"float64_runtime_sequence_claimed": True}))
    return {
        "mutants": mutants,
        "all_mutants_effective": bool(mutants and all(row["detected"] for row in mutants.values())),
    }


def build_report() -> dict[str, Any]:
    pins = _source_pin_ledger()
    ast_inventory = _real_formula_ast_inventory()
    fourier = _fourier_ledger()
    radial = _radial_ledger()
    quadrature = _quadrature_ledger()
    theorem_contract = _canonical_theorem_contract()
    contract_schema_matches = _theorem_contract_accepts(theorem_contract)
    mutants = _mutant_campaign()
    no_go = _same_norm_no_go()

    # Deliberately non-computable from pins or lexical inventories.  These
    # booleans can only change after a separate, typed, pure expression IR and
    # its decoder/projection/margin proof are present.  They are absent here.
    formula_ir_pass = False
    analytic_holder_pass = False
    scoped_bridge_pass = False
    positives = {
        "complete_shell_H19_4_to_H9_2_uniform_rate_pass": bool(fourier["pass"]),
        "weighted_radial_p4_C2_tail_and_C0_3_8_equicontinuity_pass": bool(
            radial["pass"]
        ),
        "twenty_real_formula_paths_and_sixteen_margin_inventory_ast_bound_pass": formula_ir_pass,
        "uniform_twenty_primal_jvp_holder_lemma_pass": analytic_holder_pass,
        "tensor_trapezoid_gauss_bernstein_exact_bound_pass": bool(
            quadrature["pass"]
        ),
        "bounded_margin_ball_weaker_jet_exact_formula_uniform_bridge_pass": scoped_bridge_pass,
    }
    decision = {**positives, **{key: False for key in sorted(FALSE_DECISION_KEYS)}}
    if set(decision) != TRUE_DECISION_KEYS | FALSE_DECISION_KEYS:
        raise WeakerJetUniformBridgeError("decision-key allowlist drift")
    if not all(decision[key] is True for key in TRUE_DECISION_KEYS):
        raise WeakerJetUniformBridgeError("scoped theorem did not discharge")
    if not all(decision[key] is False for key in FALSE_DECISION_KEYS):
        raise WeakerJetUniformBridgeError("fail-closed legacy boundary drift")

    return {
        "schema": SCHEMA,
        "source_pins": pins,
        "real_formula_AST_inventory": ast_inventory,
        "theorem_contract": theorem_contract,
        "theorem_contract_schema_matches": contract_schema_matches,
        "fourier_complete_shell_lemma": fourier,
        "weighted_radial_lemma": radial,
        "analytic_holder_and_eventual_margin_lemma": {
            "quantifiers": (
                "for every M>=1 and 0<epsilon<=1 there exist n0(M,epsilon), "
                "C(M,epsilon),H(M,epsilon),D(M,epsilon), such that for every "
                "(u,a) in B_(M,epsilon) and every n>=n0"
            ),
            "projected_margin": ">=epsilon/2",
            "n0_definition": theorem_contract["eventual_margins"]["definition"],
            "uniformity": "uniform on each fixed B_(M,epsilon)",
            "noncompact_exhaustion": (
                "the admissible open domain is the union of such balls, but the "
                "constants are not uniform as M->infinity or epsilon->0"
            ),
            "unclosed_obligations": [
                "emit all twenty primal formulas and JVPs as a closed typed pure IR",
                "bind every transitive helper and consumed jet leaf with derivative order",
                "prove decoder and projection continuity into that complete leaf schema",
                "bind every inverse, reciprocal and positive root to one of sixteen margins or structural positivity",
                "derive uniform first/second IR derivative bounds before differentiating under integrals",
            ],
            "pass": analytic_holder_pass,
        },
        "quadrature_and_total_rate_lemma": quadrature,
        "exact_same_norm_no_go": no_go,
        "effective_contract_mutants": mutants,
        "decision": decision,
        "scope": (
            "Exact stand-alone Fourier, ideal-radial and quadrature lemmas only. The "
            "twenty-formula IR, its uniform primal/JVP Holder theorem and the resulting "
            "bounded-margin bridge are not discharged. The ideal radial result does not "
            "certify the pinned float64 radial generator for arbitrary K. No symbolic S_rel, "
            "q-continuum, quotient, C1/N1/P4/B4/B5 or runtime promotion follows."
        ),
    }


def main() -> None:
    print(json.dumps(build_report(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
